"""Build site/index.html, the image shown when the page is shared, and site/images/ (the stories'
photos), from the content modules, the data and images folders, and template.html.

Uses no network. The build stops on a missing translation, an unknown state or kind of place, a place
whose coordinates fall outside its state, a link to an anchor that does not exist, two elements with
the same id, or a US charity without a pulled record."""
import json, pathlib, re, struct, sys, zlib
from collections import Counter

import culture, give, history, places, places_uk, stories
from i18n import both, dates, fill_markers, plural_uk

ROOT = pathlib.Path(__file__).parent

def read_json(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))

def embed(obj):
    """JSON that is safe inside a <script> element."""
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

def cross_links():
    """Where each story links to in other sections, and the links back from those sections to the story."""
    targets = {(kind, key): value for kind, module in (('history', history), ('place', places), ('give', give))
               for key, value in module.targets().items()}
    back = {'history': {}, 'place': {}, 'give': {}}
    for story_id, en, uk, kind, key in stories.related():
        if (kind, key) not in targets: raise ValueError(f'{story_id} links to {kind} {key!r}, which is not on the page')
        back[kind].setdefault(targets[kind, key][0], []).append((story_id, en, uk))
    return targets, back

def nav(items, indent='      '):
    return '\n'.join(f'{indent}<a href="#{i}">{both(en, uk)}</a>' for i, en, uk in items)

def overview():
    """Links to the five tabs with how much each holds, counted from the content so they stay true."""
    counts = [
        ('culture', len(culture.DISHES), ('dish with a recipe', 'dishes with recipes'), ('страва з рецептом', 'страви з рецептами', 'страв із рецептами')),
        ('history', sum(len(events) for _, _, _, events in history.ERAS), ('turning point', 'turning points'), ('поворотний момент', 'поворотні моменти', 'поворотних моментів')),
        ('stories', len(stories.STORIES), ('story', 'stories'), ('історія', 'історії', 'історій')),
        ('places', len(places.PLACES), ('place to eat and shop', 'places to eat and shop'), ('заклад', 'заклади', 'закладів')),
        ('give', sum(len(orgs) for _, _, orgs in give.GROUPS), ('way to help', 'ways to help'), ('спосіб допомогти', 'способи допомогти', 'способів допомогти')),
    ]
    links = []
    for panel, n, en, uk in counts:
        label = both(en[n != 1], plural_uk(n, *uk))
        links.append(f'        <a class="overview-link" href="#{panel}"><span class="overview-num">{n}</span><span class="overview-label">{label}</span></a>')
    return '\n'.join(links)

def build():
    for name in places.STATE_IDS:
        if name not in places_uk.STATES: raise ValueError(f'no Ukrainian name for state: {name}')

    targets, back = cross_links()
    timeline = history.render(back['history'])
    people, themes = stories.render(targets)
    culture_html, culture_nav = culture.render(targets)
    give_html, give_nav = give.render(back['give'])
    records_en, records_uk = dates(read_json('checked.json')['records'])
    give_en, give_uk = dates(give.REVIEWED)
    places_en, places_uk_date = dates(places.REVIEW['reviewed'])
    summary_en, summary_uk = places.summary()
    as_of_en, as_of_uk = dates(history.AS_OF)

    template = (ROOT / 'template.html').read_text(encoding='utf-8')
    page = (fill_markers(template)
            .replace('__ERA_NAV__', history.era_nav()).replace('__HISTORY__', timeline)
            .replace('__THEME_NAV__', nav(themes)).replace('__STORIES__', people)
            .replace('__CULTURE_NAV__', nav(culture_nav)).replace('__CULTURE__', culture_html).replace('__HERO_CREDIT__', culture.hero_credit())
            .replace('__PLACES_SUMMARY__', both(summary_en, summary_uk)).replace('__PLACE_LIST__', places.render(back['place']))
            .replace('__PLACE_PHOTOS__', places.photo_strip()).replace('__KIND_FILTER__', places.kind_filter()).replace('__PLACE_ICONS__', places.icons())
            .replace('__GIVE_NAV__', nav(give_nav)).replace('__GIVE__', give_html)
            .replace('__RECORDS_EN__', records_en).replace('__RECORDS_UK__', records_uk)
            .replace('__GIVE_REVIEWED_EN__', give_en).replace('__GIVE_REVIEWED_UK__', give_uk)
            .replace('__PLACES_REVIEWED_EN__', places_en).replace('__PLACES_REVIEWED_UK__', places_uk_date)
            .replace('__AS_OF_EN__', as_of_en).replace('__AS_OF_UK__', as_of_uk).replace('__OVERVIEW__', overview())
            .replace('__PLACES__', embed(places.map_data())).replace('__STATES__', embed(places.TOPO))
            .replace('__PLACES_UK__', embed({'states': places_uk.STATES})))

    markup = page.split('<script type="application/json"')[0]
    if '__' in markup or '{{' in markup:
        raise ValueError('unfilled placeholder in template.html')
    ids = Counter(re.findall(r'\sid="([^"]+)"', markup))
    if duplicates := sorted(i for i, n in ids.items() if n > 1):
        raise ValueError(f'more than one element has the id: {duplicates}')
    if broken := sorted(set(re.findall(r'href="#([^"]+)"', markup)) - set(ids)):
        raise ValueError(f'links to anchors that do not exist: {broken}')
    return page

def flag_png(width=1200, height=630):
    """The Ukrainian flag as a PNG, for link previews. Two solid bands compress to almost nothing."""
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    blue, yellow = bytes((0x00, 0x57, 0xB7)) * width, bytes((0xFF, 0xD7, 0x00)) * width
    rows = b''.join(b'\x00' + (blue if y < height // 2 else yellow) for y in range(height))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(rows, 9)) + chunk(b'IEND', b''))

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    out = ROOT / 'site' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(build(), encoding='utf-8')
    (out.parent / 'preview.png').write_bytes(flag_png())
    (out.parent / 'images').mkdir(exist_ok=True)
    for photo in stories.photo_files() + culture.photo_files() + places.photo_files() + history.photo_files():
        (out.parent / 'images' / photo.name).write_bytes(photo.read_bytes())
    print(f'built {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)')
