"""The places section: Ukrainian restaurants, bakeries and markets in the United States.

data/places.json is maintained by hand. Each place names its state, and the build confirms its
coordinates fall inside that state, so a mistyped coordinate stops the build instead of moving a
dot. Each place also carries its evidence (rule 2 in CLAUDE.md): a phrase on its own website or in
local press, which check.py confirms is still on that page every week."""
import html, json, math, pathlib
from collections import Counter
from urllib.parse import quote

import photos, places_uk
from i18n import both, slug
from photos import photo

DATA = pathlib.Path(__file__).parent / 'data'
OWN_SITE = 'own website'
DC = 'District of Columbia'
# Why a place counts as Ukrainian (rule 2), shown on each listing. Its evidence must say so.
UKRAINIAN = {'food': ('Ukrainian food', 'Українська їжа'), 'goods': ('Ukrainian goods', 'Українські товари'), 'owner': ('Ukrainian-owned', 'Власники з України')}
# The kinds of place, grouped for the filter buttons and the icon on each listing.
GROUPS = {
    'restaurant': (('Restaurants', 'Ресторани'), {'Restaurant', 'Counter service'}),
    'cafe': (('Cafés', 'Кафе'), {'Café'}),
    'bakery': (('Bakeries', 'Пекарні'), {'Bakery'}),
    'market': (('Markets and shops', 'Крамниці'), {'Deli', 'Grocery', 'Grocery and café', 'Gift shop', 'Bookstore'}),
}
GROUP_OF = {kind: group for group, (_, kinds) in GROUPS.items() for kind in kinds}
if missing := set(places_uk.KINDS) ^ set(GROUP_OF): raise ValueError(f'kinds of place not in exactly one of GROUPS and places_uk.KINDS: {sorted(missing)}')
# Line icons (24 by 24, drawn with the stroke) for each group: a bowl, a cup, an ear of wheat, a basket.
ICONS = {
    'restaurant': 'M3.5 11.5h17a8.5 8.5 0 0 1-17 0ZM8.5 8.5c0-1.2 1-1.3 1-2.5s-1-1.3-1-2.5M12 8.5c0-1.2 1-1.3 1-2.5s-1-1.3-1-2.5M15.5 8.5c0-1.2 1-1.3 1-2.5s-1-1.3-1-2.5',
    'cafe': 'M4 10h12v4.5a4.5 4.5 0 0 1-4.5 4.5h-3A4.5 4.5 0 0 1 4 14.5ZM16 11.5h1.5a2.5 2.5 0 0 1 0 5H16M3 21.5h14M8 3.5c0 1-1 1.5-1 2.5M12 3.5c0 1-1 1.5-1 2.5',
    'bakery': 'M12 22V6M12 10c-2.2 0-3.5-1.4-3.5-3.5 2.2 0 3.5 1.4 3.5 3.5Zm0 0c2.2 0 3.5-1.4 3.5-3.5-2.2 0-3.5 1.4-3.5 3.5ZM12 14.5c-2.2 0-3.5-1.4-3.5-3.5 2.2 0 3.5 1.4 3.5 3.5Zm0 0c2.2 0 3.5-1.4 3.5-3.5-2.2 0-3.5 1.4-3.5 3.5ZM12 19c-2.2 0-3.5-1.4-3.5-3.5 2.2 0 3.5 1.4 3.5 3.5Zm0 0c2.2 0 3.5-1.4 3.5-3.5-2.2 0-3.5 1.4-3.5 3.5ZM12 6c-.9-.9-.9-2.6 0-3.5.9.9.9 2.6 0 3.5Z',
    'market': 'M3.5 10h17l-1.7 8.4a2 2 0 0 1-2 1.6H7.2a2 2 0 0 1-2-1.6ZM8.5 10 11 4.5M15.5 10 13 4.5M9.5 13.5v3M12 13.5v3M14.5 13.5v3',
}
if set(ICONS) != set(GROUPS): raise ValueError('every group needs an icon')

def read(name): return json.loads((DATA / name).read_text(encoding='utf-8'))

TOPO = read('states-10m.json')
REVIEW = read('places_review.json')  # the date of the last review by hand, and the places held back
STATE_IDS = {g['properties']['name']: g['id'] for g in TOPO['objects']['states']['geometries'] if int(g['id']) < 60}

def _rings_by_state():
    """Each state's outline as lists of (lon, lat), decoded from the TopoJSON arcs."""
    (sx, sy), (tx, ty) = TOPO['transform']['scale'], TOPO['transform']['translate']
    arcs = []
    for arc in TOPO['arcs']:
        x = y = 0; points = []
        for dx, dy in arc:
            x += dx; y += dy
            points.append((x * sx + tx, y * sy + ty))
        arcs.append(points)
    rings = {}
    for g in TOPO['objects']['states']['geometries']:
        polygons = g['arcs'] if g['type'] == 'MultiPolygon' else [g['arcs']]
        rings[g['properties']['name']] = [[p for i in ring for p in (arcs[i] if i >= 0 else arcs[~i][::-1])] for polygon in polygons for ring in polygon]
    return rings

def _contains(rings, lon, lat):
    """Even-odd ray casting. Holes and multiple polygons need no special handling."""
    inside = False
    for ring in rings:
        for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
            if (y1 > lat) != (y2 > lat) and lon < x1 + (lat - y1) * (x2 - x1) / (y2 - y1):
                inside = not inside
    return inside

# The state outlines are simplified (1:10 million), so a place on a shoreline can fall just outside its
# state and inside none. Within this distance of its own state's outline, that is accepted.
COAST_KM = 2

def _km_to_outline(rings, lon, lat):
    k = math.cos(math.radians(lat))  # degrees of longitude shrink toward the poles
    def segment(x1, y1, x2, y2):
        dx, dy = (x2 - x1) * k, y2 - y1
        t = max(0.0, min(1.0, (((lon - x1) * k) * dx + (lat - y1) * dy) / (dx * dx + dy * dy or 1)))
        return math.hypot((lon - x1) * k - t * dx, lat - y1 - t * dy) * 111.2
    return min(segment(x1, y1, x2, y2) for ring in rings for (x1, y1), (x2, y2) in zip(ring, ring[1:]))

def _load():
    places = read('places.json')
    rings = _rings_by_state()
    ids = set()
    branches = Counter((p['name'], p['city']) for p in places)  # the street tells apart two branches in one city
    for p in places:
        where = f"{p['name']} ({p['city']})"
        if p['state'] not in STATE_IDS: raise ValueError(f"{where}: unknown state {p['state']!r}")
        if p['kind'] not in places_uk.KINDS: raise ValueError(f"{where}: no Ukrainian name for kind of place {p['kind']!r}")
        if p['web'] and not p['web'].startswith(('https://', 'http://')): raise ValueError(f"{where}: bad website {p['web']!r}")
        if not _contains(rings[p['state']], p['lon'], p['lat']):
            found = [name for name, r in rings.items() if _contains(r, p['lon'], p['lat'])]
            if found or _km_to_outline(rings[p['state']], p['lon'], p['lat']) > COAST_KM:
                raise ValueError(f"{where}: coordinates fall in {found or 'no state'}, not {p['state']}")
        if not p['ukrainian'] or set(p['ukrainian']) - set(UKRAINIAN): raise ValueError(f"{where}: 'ukrainian' must list one or more of {sorted(UKRAINIAN)}")
        if not p['basis']: raise ValueError(f'{where}: no evidence that it is Ukrainian (see rule 2 in CLAUDE.md)')
        for b in p['basis']:
            if not (b['by'] and b['url'].startswith('https://') and b['says'].strip()): raise ValueError(f'{where}: incomplete evidence {b}')
        if p['name'] in REVIEW['held']: raise ValueError(f"{where}: both listed and held back in places_review.json")
        p['id'] = 'place-' + slug(f"{p['name']} {p['street'] if branches[p['name'], p['city']] > 1 else ''} {p['city']}")
        if p['id'] in ids: raise ValueError(f'{where}: listed twice')
        ids.add(p['id'])
        p['state_id'] = STATE_IDS[p['state']]
        p['group'] = GROUP_OF[p['kind']]
    return places

PLACES = _load()
STATES_WITH_PLACES = {p['state'] for p in PLACES}

def targets():
    """(name, city) -> (element id, English label, Ukrainian label), for links from other sections."""
    out = {}
    for p in PLACES:
        out.setdefault((p['name'], p['city']), (p['id'], f"{p['name']}, {p['city']}", f"{p['name']}, {p['city']}"))
    return out

W = 'https://commons.wikimedia.org/wiki/File:'
# Photos taken at listed places, from Wikimedia Commons (rule 7), shown in a row above the list: the id of
# the listing each one opens, and the photo. People in them are too small and far away to be recognized.
PHOTOS = [
    ('place-veselka-144-2nd-avenue-new-york',
     photo('place-veselka.jpg', ('Veselka on the corner of Second Avenue and Ninth Street, in the East Village', '«Веселка» на розі Другої авеню та Дев’ятої вулиці в Іст-Віллиджі'),
           'BruceSchaff', 'CC BY-SA 3.0', W + 'Veselka_(1).jpg')),
    ('place-veselka-144-2nd-avenue-new-york',
     photo('place-veselka-deruny.jpg', ('Potato pancakes at Veselka', 'Деруни у «Веселці»'),
           'Antanana', 'CC0', W + 'Veselka-Deruny-20250309_191355.jpg')),
    ('place-kramarczuk-s-sausage-company-minneapolis',
     photo('place-kramarczuks.jpg', ('The Kramarczuk’s storefront in Minneapolis', 'Вітрина Kramarczuk’s у Мінеаполісі'),
           'Mx. Granger', 'CC0', W + 'Kramarczuk_Deli.jpg')),
    ('place-veselka-144-2nd-avenue-new-york',
     photo('place-veselka-plate.jpg', ('Varenyky and a meatless stuffed cabbage roll at Veselka', 'Вареники й пісний голубець у «Веселці»'),
           'Antanana', 'CC0', W + 'Veselka-Vegetarian_Combo_Plate-20250309_191410.jpg')),
]
BY_ID = {p['id']: p for p in PLACES}
for _id, _photo in PHOTOS:
    if _id not in BY_ID: raise ValueError(f'photo {_photo["file"]} opens {_id}, which is not listed')
    photos.validate(_photo, _photo['file'])

def photo_files():
    return [photos.IMAGES / p['file'] for _, p in PHOTOS]

def photo_strip():
    """The row of photos, each opening its place's listing."""
    e = html.escape; figures = []
    for place_id, p in PHOTOS:
        place = BY_ID[place_id]
        figures.append(f'''      <figure class="place-photo">
        <a class="shot" href="#{place_id}">{photos.img(p)}<span class="shot-caption">{e(place['name'])}, {e(place['city'])}</span></a>
        <figcaption class="credit">{photos.credit(p)}</figcaption>
      </figure>''')
    return '    <div class="place-photos">\n' + '\n'.join(figures) + '\n    </div>'

def claims():
    """(url, phrase, what) for check.py: each place's evidence must still be on its page, and each photo's license on its Commons page."""
    return ([(b['url'], b['says'], f"{p['name']} ({p['city']}): {b['by']}") for p in PLACES for b in p['basis']]
            + [photos.claim(p, f"photo {p['file']}: license") for _, p in PHOTOS])

def summary():
    n, k, dc = len(PLACES), len(STATES_WITH_PLACES - {DC}), DC in STATES_WITH_PLACES
    return (f'{n} places in {k} states' + (' and Washington, DC.' if dc else '.'),
            f'Закладів: {n}. Штатів: {k}' + (', а також Вашингтон (округ Колумбія).' if dc else '.'))

def map_data():
    """What the map script needs: where to draw each dot, its state and group, and the listing it opens."""
    return [{'id': p['id'], 'name': p['name'], 'city': p['city'], 'group': p['group'], 'lon': p['lon'], 'lat': p['lat'], 'state': p['state_id']} for p in PLACES]

def icons():
    """The icons as SVG symbols, drawn once and used by each listing and filter button."""
    symbols = ''.join(f'<symbol id="icon-{g}" viewBox="0 0 24 24"><path d="{d}"/></symbol>' for g, d in ICONS.items())
    return f'<svg class="icon-defs" aria-hidden="true" focusable="false">{symbols}</svg>'

def _icon(group):
    return f'<svg class="icon" aria-hidden="true" focusable="false"><use href="#icon-{group}"/></svg>'

def kind_filter():
    """One button per group of places, plus one for all of them."""
    buttons = [f'<button type="button" class="chip" data-kind="" aria-pressed="true">{both("All", "Усі")}</button>']
    for group, ((en, uk), _) in GROUPS.items():
        buttons.append(f'<button type="button" class="chip" data-kind="{group}" aria-pressed="false">{_icon(group)}{both(en, uk)}</button>')
    return ''.join(buttons)

def _sources(p):
    """Who says the place is Ukrainian, on one line, and their exact words when opened (rule 2)."""
    e = html.escape
    names = lambda own: list(dict.fromkeys(own if b['by'] == OWN_SITE else b['by'] for b in p['basis']))
    en, uk = names('its own website'), names('власний сайт закладу')
    summary = both(('Sources: ' if len(en) > 1 else 'Source: ') + ', '.join(en),
                   ('Джерела: ' if len(uk) > 1 else 'Джерело: ') + ', '.join(uk))
    quotes = []
    for b in p['basis']:
        by_en, by_uk = ('its website', 'сайт закладу') if b['by'] == OWN_SITE else (b['by'], b['by'])
        link = lambda label: f'<a href="{e(b["url"])}" target="_blank" rel="noopener">{e(label)}</a>'
        quotes.append(f'<li><span data-l="en">“{e(b["says"])}” — {link(by_en)}</span>'
                      f'<span data-l="uk" lang="uk">«{e(b["says"])}» — {link(by_uk)}</span></li>')
    return f'<details class="why"><summary>{summary}</summary><ul>{"".join(quotes)}</ul></details>'

def render(story_links):
    """The listings as cards, grouped by state in English alphabetical order (the script reorders the groups for Ukrainian).
    story_links maps a place id to [(story id, English label, Ukrainian label)]."""
    e = html.escape; out = []
    target_ids = {key: target[0] for key, target in targets().items()}  # a story about a business shows on all its listings in that city
    for state in sorted(STATES_WITH_PLACES):
        out.append(f'<div class="state-group" data-state="{STATE_IDS[state]}">\n  <h3 class="group-name">{both(state, places_uk.STATES[state])}</h3>\n  <div class="cards">')
        for p in sorted((p for p in PLACES if p['state'] == state), key=lambda p: (p['name'], p['city'])):
            address = ', '.join(e(x) for x in (p['street'], p['city']) if x)
            query = quote(', '.join((p['name'], p['street'], p['city'], p['state'])))
            links = []
            if p['web']: links.append(f'<a class="place-btn" href="{e(p["web"])}" target="_blank" rel="noopener">{both("Website", "Сайт")}</a>')
            links.append(f'<a class="place-btn" href="https://www.google.com/maps/search/?api=1&amp;query={query}" target="_blank" rel="noopener">{both("Map", "Мапа")}</a>')
            story = ''.join(f'\n    <p class="place-story"><a href="#{story_id}">{both("Story: " + en, "Історія: " + uk)}</a></p>'
                            for story_id, en, uk in story_links.get(target_ids[p['name'], p['city']], []))
            out.append(f"""  <article class="place" id="{p['id']}" tabindex="-1" data-state="{p['state_id']}" data-group="{p['group']}">
    <p class="place-kind">{_icon(p['group'])}{both(p['kind'], places_uk.KINDS[p['kind']])}</p>
    <h4 class="place-name">{e(p['name'])}</h4>
    <p class="place-addr">{address}</p>
    <p class="place-tags">{''.join(both(*UKRAINIAN[t], cls='tag tag-' + t) for t in p['ukrainian'])}</p>{story}
    <p class="place-links">{''.join(links)}</p>
    {_sources(p)}
  </article>""")
        out.append('  </div>\n</div>')
    return '\n'.join(out)
