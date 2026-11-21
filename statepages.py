"""A page per state for the Eat and shop list (site/places/<state>/ in English, site/places/<state>/uk/ in Ukrainian),
an index of them (site/places/), and site/sitemap.xml.

The main page keeps every listing behind a tab at one address, so a search for Ukrainian places in one state had
nothing to land on. These pages carry the same listings, from the same data and under the same rule 2, as plain
pages with their own titles, and each links back to the map. They need no script."""
import html, json
from urllib.parse import quote

import diaspora, places, places_uk, stories
from i18n import dates, plural_uk, slug

SITE = 'https://rowanflynnpilot.github.io/together-with-ukraine/'
DC = 'District of Columbia'
KIND_WORDS = {  # the plural of each group of kinds, for a page's title
    'restaurant': ('restaurants', 'ресторани'), 'cafe': ('cafés', 'кафе'), 'bakery': ('bakeries', 'пекарні'), 'market': ('shops', 'крамниці'),
}
# Every fixed text on these pages, (English, Ukrainian), for the pages and for the review page.
TEXT = {
    'site': ('Together with Ukraine', 'Разом з Україною'),
    'tab': ('Eat and shop', 'Заклади'),
    'index_h1': ('Ukrainian places to eat and shop, by state', 'Українські заклади та крамниці за штатами'),
    'index_lede': ('Restaurants, cafés, bakeries, delis, groceries and shops that serve Ukrainian food, sell Ukrainian goods or are owned by Ukrainians, as their own websites or the press say.',
                   'Ресторани, кафе, пекарні, кулінарії, продуктові магазини та крамниці, які пропонують українську їжу, продають українські товари або належать українцям — так зазначено на їхніх власних сайтах чи в пресі.'),
    'rule': ('Each serves Ukrainian food, sells Ukrainian goods or is owned by Ukrainians, as its own website or the press says, and each listing links to where it says so. Check hours before you go.',
             'Кожен пропонує українську їжу, продає українські товари або належить українцям — так зазначено на його власному сайті чи в пресі, і біля кожного є посилання на джерело. Перед візитом перевірте години роботи.'),
    'map': ('See them on the map', 'Подивитися на мапі'),
    'all': ('All states', 'Усі штати'),
    'website': ('Website', 'Сайт'),
    'story': ('Story: ', 'Історія: '),
    'source': ('Source: ', 'Джерело: '),
    'own': ('its own website', 'власний сайт закладу'),
    'other': ('Other states', 'Інші штати'),
    'other_lang': ('Українською', 'In English'),
    'missing': ('Know a place that belongs here?', 'Знаєте заклад, який варто додати?'),
    'suggest': ('Suggest it', 'Запропонуйте його'),
}
TEXT.update({'tag-' + key: pair for key, pair in places.UKRAINIAN.items()})

CSS = '''
:root { color-scheme: light dark; --sky: #0057B7; --wheat: #FFD700; --paper: #FFFFFF; --wash: #EEF3FA; --ink: #0B1F3A; --muted: #4A5B74; --line: #C3D2E6; --link: #0057B7; --card: #FFFFFF; box-sizing: border-box; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { color-scheme: dark; --paper: #0A1626; --wash: #12233A; --ink: #EAF0F8; --muted: #A8B8CE; --line: #2A4263; --link: #8DBEFF; --card: #12233A; } }
:root[data-theme="light"] { color-scheme: light; }
:root[data-theme="dark"] { color-scheme: dark; --paper: #0A1626; --wash: #12233A; --ink: #EAF0F8; --muted: #A8B8CE; --line: #2A4263; --link: #8DBEFF; --card: #12233A; }
*, *::before, *::after { box-sizing: inherit; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: "Arsenal", "Segoe UI", system-ui, sans-serif; font-size: 1.125rem; line-height: 1.55; }
a { color: var(--link); }
:focus-visible { outline: 3px solid var(--wheat); outline-offset: 2px; box-shadow: 0 0 0 5px #0B1F3A; }
.wrap { max-width: 56rem; margin: 0 auto; padding: 0 1.25rem; }
.top { background: var(--sky); color: #FFFFFF; border-bottom: 6px solid var(--wheat); padding: 1.1rem 0 1.6rem; }
.top a { color: #FFFFFF; }
.top a:focus-visible { outline-color: #FFFFFF; }
.crumbs { display: flex; flex-wrap: wrap; align-items: center; gap: 0.3rem 0.6rem; margin: 0; font-size: 0.9375rem; }
.crumbs .flag { width: 1.8rem; height: 1.2rem; box-shadow: 0 0 0 2px #FFFFFF; margin-right: 0.3rem; }
.crumbs .lang { margin-left: auto; font-weight: 700; }
h1 { margin: 1.3rem 0 0; font-size: clamp(1.8rem, 5vw, 2.75rem); line-height: 1.1; }
main.wrap { padding-top: 2rem; padding-bottom: 3rem; }
.lede { margin: 0 0 0.6rem; max-width: 42rem; }
.census { margin: 0 0 1.5rem; max-width: 42rem; color: var(--muted); font-size: 1rem; }
.btn { display: inline-block; padding: 0.4rem 0.9rem; border: 2px solid var(--link); color: var(--link); font-weight: 700; text-decoration: none; }
.btn:hover { background: var(--link); color: var(--paper); }
h2.city { display: flex; align-items: center; gap: 0.75rem; margin: 2.2rem 0 0.85rem; font-size: 1.3rem; }
h2.city::after { content: ""; flex: 1; height: 1px; background: var(--line); }
.cards { display: grid; gap: 0.9rem; }
.place { background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--sky); padding: 0.95rem 1.15rem 1rem; }
.place p { margin: 0; }
.kind { color: var(--muted); font-size: 0.9375rem; }
.place h3 { margin: 0.2rem 0 0.1rem; font-size: 1.35rem; line-height: 1.2; }
.addr { color: var(--muted); }
.place .tags { margin-top: 0.55rem; display: flex; flex-wrap: wrap; gap: 0.35rem; }
.tag { font-size: 0.8125rem; font-weight: 700; padding: 0.1rem 0.5rem; background: rgba(0, 87, 183, 0.12); border: 1px solid rgba(0, 87, 183, 0.35); }
.place .links { margin-top: 0.8rem; display: flex; flex-wrap: wrap; gap: 0.5rem; }
.place .links .btn { font-size: 0.9375rem; padding: 0.3rem 0.8rem; }
.place .story { margin-top: 0.6rem; font-weight: 700; }
.place .why { margin-top: 0.8rem; padding-top: 0.6rem; border-top: 1px dashed var(--line); font-size: 0.875rem; color: var(--muted); }
.states { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fill, minmax(13rem, 1fr)); gap: 0.4rem 1.25rem; }
.states span { color: var(--muted); font-size: 0.9375rem; }
.more { margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid var(--line); }
.more h2 { margin: 0 0 0.8rem; font-size: 1.2rem; }
.note { margin: 2rem 0 0; padding: 1rem 1.25rem; background: var(--wash); font-size: 1rem; }
'''

def state_name(state):
    """A state as these pages name it: (English, Ukrainian, how the English reads after 'in')."""
    if state == DC: return 'Washington, DC', 'Вашингтон, округ Колумбія', 'Washington, DC'
    # Washington alone would read as the capital, which has a page of its own.
    return state, 'штат ' + places_uk.STATES[state], 'Washington state' if state == 'Washington' else state

def path(state, lang):
    return f'places/{slug(state)}/' + ('uk/' if lang else '')

def _listed():
    by_state = {}
    for p in places.PLACES: by_state.setdefault(p['state'], []).append(p)
    return {state: sorted(found, key=lambda p: (p['city'], p['name'])) for state, found in sorted(by_state.items())}

def _stories():
    """(place name, city) -> [(story id, person in English, in Ukrainian)]."""
    out = {}
    for story_id, en, uk, kind, key in stories.related():
        if kind == 'place': out.setdefault(key, []).append((story_id, en, uk))
    return out

def _title(state, found, lang):
    kinds = [KIND_WORDS[g][lang] for g in places.GROUPS if any(p['group'] == g for p in found)]
    listed = kinds[0] if len(kinds) == 1 else ', '.join(kinds[:-1]) + (' and ' if not lang else ' та ') + kinds[-1]
    en, uk, after_in = state_name(state)
    return f'Ukrainian {listed} in {after_in}' if not lang else f'Українські {listed}: {uk}'

def _census(state, lang):
    """One sentence from the In the US tab's figures, where the Census Bureau published the state's (rule 9)."""
    s = diaspora.STATES[state]
    if not s['ancestry']: return ''
    (n_en, n_uk), (m_en, m_uk) = diaspora.num(s['ancestry'][0]), diaspora.num(s['ancestry'][1])
    text = (f'{n_en} people here (± {m_en}) reported Ukrainian ancestry in the Census Bureau’s American Community Survey for {diaspora.YEAR}.' if not lang else
            f'За даними Американського опитування громад Бюро перепису населення США за {diaspora.YEAR} рік, українське походження тут вказали {n_uk} (± {m_uk}) людей.')
    more = ('More figures', 'Більше даних')[lang]
    return f'<p class="census">{html.escape(text)} <a href="{_home(lang)}#in-the-us">{more}</a></p>'

def _home(lang, depth=2):
    return '../' * (depth + lang) + ('?lang=uk' if lang else '')

def _head(title, description, here, lang, alternates):
    e = html.escape
    return f'''<!doctype html>
<html lang="{('en', 'uk')[lang]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)} | {TEXT['site'][lang]}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{SITE}{here}">
<link rel="alternate" hreflang="en" href="{SITE}{alternates[0]}">
<link rel="alternate" hreflang="uk" href="{SITE}{alternates[1]}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Together with Ukraine · Разом з Україною">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{SITE}{here}">
<meta property="og:image" content="{SITE}images/share.jpg">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0057B7">
<script>try {{ const theme = localStorage.getItem('theme'); if (theme === 'light' || theme === 'dark') document.documentElement.dataset.theme = theme; }} catch (error) {{ /* storage unavailable: the system theme applies */ }}</script>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 3 2'%3E%3Crect width='3' height='1' fill='%230057B7'/%3E%3Crect y='1' width='3' height='1' fill='%23FFD700'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Arsenal:ital,wght@0,400;0,700;1,400&display=swap">
<style>{CSS}</style>
'''

FLAG = '<svg class="flag" viewBox="0 0 3 2" aria-hidden="true" focusable="false"><rect width="3" height="1" fill="#0057B7"/><rect y="1" width="3" height="1" fill="#FFD700"/></svg>'

def _top(crumbs, h1, other, lang):
    """The blue band: where the page sits, the link to the other language, and the heading."""
    trail = ' › '.join(f'<a href="{href}">{html.escape(label)}</a>' if href else f'<span>{html.escape(label)}</span>' for label, href in crumbs)
    other_lang = ('uk', 'en')[lang]
    return f'''<header class="top"><div class="wrap">
  <p class="crumbs">{FLAG}{trail}<a class="lang" href="{other}" lang="{other_lang}" hreflang="{other_lang}">{TEXT['other_lang'][lang]}</a></p>
  <h1>{html.escape(h1)}</h1>
</div></header>
'''

def _card(p, story_links, lang):
    e = html.escape
    name = e(places.shown(p['name']))
    kind = (p['kind'], places_uk.KINDS[p['kind']])[lang]
    address = ', '.join(e(x) for x in (p['street'], p['city']) if x)
    tags = ''.join(f'<span class="tag">{e(places.UKRAINIAN[t][lang])}</span>' for t in p['ukrainian'])
    links = []
    if p['web']: links.append(f'<a class="btn" href="{e(p["web"])}" rel="noopener">{TEXT["website"][lang]}<span class="vh">: {name}</span></a>')
    query = quote(', '.join((p['name'], p['street'], p['city'], p['state'])))
    links.append(f'<a class="btn" href="https://www.google.com/maps/search/?api=1&amp;query={query}" rel="noopener">Google Maps<span class="vh">: {name}</span></a>')
    story = ''.join(f'\n    <p class="story"><a href="{_home(lang)}#{story_id}">{TEXT["story"][lang]}{e((en, uk)[lang])}</a></p>'
                    for story_id, en, uk in story_links.get((p['name'], p['city']), []))
    quotes = ('“{}”', '«{}»')[lang]
    sources = '; '.join(f'{quotes.format(e(b["says"]))} — <a href="{e(b["url"])}" rel="noopener">{e(TEXT["own"][lang] if b["by"] == places.OWN_SITE else b["by"])}</a>' for b in p['basis'])
    return f'''  <article class="place" id="{p['id']}">
    <p class="kind">{e(kind)}</p>
    <h3>{name}</h3>
    <p class="addr">{address}</p>
    <p class="tags">{tags}</p>{story}
    <p class="links">{''.join(links)}</p>
    <p class="why">{TEXT['source'][lang]}{sources}</p>
  </article>'''

def _schema(state, found, lang):
    """The listings as structured data, so a search engine can read them as places with addresses."""
    kinds = {'restaurant': 'Restaurant', 'cafe': 'CafeOrCoffeeShop', 'bakery': 'Bakery', 'market': 'Store'}
    items = []
    for i, p in enumerate(found, 1):
        place = {'@type': kinds[p['group']], 'name': places.shown(p['name']),
                 'address': {'@type': 'PostalAddress', 'addressLocality': p['city'], 'addressRegion': state, 'addressCountry': 'US'},
                 'geo': {'@type': 'GeoCoordinates', 'latitude': p['lat'], 'longitude': p['lon']}}
        if p['street']: place['address']['streetAddress'] = p['street']
        if p['web']: place['url'] = p['web']
        items.append({'@type': 'ListItem', 'position': i, 'item': place})
    data = {'@context': 'https://schema.org', '@type': 'ItemList', 'name': _title(state, found, lang), 'numberOfItems': len(found), 'itemListElement': items}
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'

def _state_links(listed, lang, prefix, skip=None):
    items = []
    for state, found in listed.items():
        if state == skip: continue
        n = len(found)
        count = f'{n} {"place" if n == 1 else "places"}' if not lang else f'{n} {plural_uk(n, "заклад", "заклади", "закладів")}'
        items.append(f'<li><a href="{prefix}{slug(state)}/{"uk/" if lang else ""}">{html.escape(state_name(state)[lang])}</a> <span>{count}</span></li>')
    return '<ul class="states">' + ''.join(items) + '</ul>'

VH = '.vh { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; border: 0; }'

def _foot(lang):
    reviewed = dates(places.REVIEW['reviewed'])[lang]
    checked = (f'Each place was checked against its own website or local press on {reviewed}, and the evidence is re-read every week.',
               f'Кожен заклад перевірено за його власним сайтом або місцевою пресою {reviewed}, а джерела щотижня перечитуються.')[lang]
    return f'''  <p class="note">{html.escape(checked)} {TEXT['missing'][lang]} <a href="https://github.com/RowanFlynnPilot/together-with-ukraine/issues/new/choose" rel="noopener">{TEXT['suggest'][lang]}</a>.</p>
</main>
</body>
</html>
'''

def state_page(state, found, listed, story_links, lang):
    en, uk, after_in = state_name(state)
    n = len(found)
    title = _title(state, found, lang)
    h1 = (f'Ukrainian places to eat and shop in {after_in}', f'Українські заклади та крамниці: {uk}')[lang]
    count = (f'{n} {"place" if n == 1 else "places"} in {after_in}.', f'Закладів: {n}.')[lang]
    cities = ', '.join(dict.fromkeys(p['city'] for p in found))
    description = (f'{count} {cities}. Each serves Ukrainian food, sells Ukrainian goods or is Ukrainian-owned, with the source that says so.',
                   f'{count} {cities}. Кожен пропонує українську їжу, продає українські товари або належить українцям; до кожного є джерело.')[lang]
    alternates = (path(state, 0), path(state, 1))
    home = _home(lang)
    body = []
    for city in dict.fromkeys(p['city'] for p in found):
        body.append(f'  <h2 class="city">{html.escape(city)}</h2>\n  <div class="cards">')
        body += [_card(p, story_links, lang) for p in found if p['city'] == city]
        body.append('  </div>')
    crumbs = [(TEXT['site'][lang], home), (TEXT['tab'][lang], home + '#places'), (TEXT['all'][lang], '../' * (1 + lang) + ('uk/' if lang else '')), ((en, uk)[lang], None)]
    return (_head(title, description, alternates[lang], lang, alternates) + f'<style>{VH}</style>\n' + _schema(state, found, lang) + '\n</head>\n<body>\n'
            + _top(crumbs, h1, ('uk/', '../')[lang], lang) + f'''<main class="wrap">
  <p class="lede">{html.escape(count)} {html.escape(TEXT['rule'][lang])}</p>
  {_census(state, lang)}
  <p><a class="btn" href="{home}#{places.group_id(state)}">{TEXT['map'][lang]}</a></p>
''' + '\n'.join(body) + f'''
  <nav class="more" aria-labelledby="other-states">
    <h2 id="other-states">{TEXT['other'][lang]}</h2>
    {_state_links(listed, lang, '../' * (1 + lang), skip=state)}
  </nav>
''' + _foot(lang))

def index_page(listed, lang):
    total, states = len(places.PLACES), len(listed)
    title = TEXT['index_h1'][lang]
    description = (f'{total} Ukrainian restaurants, cafés, bakeries and shops in {states} states and Washington, DC, each with the source that says it is Ukrainian.',
                   f'{total} українських ресторанів, кафе, пекарень і крамниць у США за штатами; до кожного є джерело.')[lang]
    alternates = ('places/', 'places/uk/')
    home = _home(lang, depth=1)
    crumbs = [(TEXT['site'][lang], home), (TEXT['tab'][lang], home + '#places'), (TEXT['all'][lang], None)]
    return (_head(title, description, alternates[lang], lang, alternates) + '</head>\n<body>\n' + _top(crumbs, title, ('uk/', '../')[lang], lang) + f'''<main class="wrap">
  <p class="lede">{html.escape(TEXT['index_lede'][lang])}</p>
  <p><a class="btn" href="{home}#places">{TEXT['map'][lang]}</a></p>
  <nav class="more" aria-labelledby="states">
    <h2 id="states">{TEXT['all'][lang]}</h2>
    {_state_links(listed, lang, '../' if lang else '')}
  </nav>
''' + _foot(lang))

def pages():
    """Every page this module writes: path under site/ -> HTML."""
    listed, story_links = _listed(), _stories()
    out = {}
    for lang in (0, 1):
        out['places/' + ('uk/' if lang else '') + 'index.html'] = index_page(listed, lang)
        for state, found in listed.items():
            out[path(state, lang) + 'index.html'] = state_page(state, found, listed, story_links, lang)
    return out

def sitemap(page_paths):
    """site/sitemap.xml: the main page and every page here, for a search engine to be pointed at."""
    urls = [SITE] + [SITE + p.removesuffix('index.html') for p in sorted(page_paths)]
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + ''.join(f'  <url><loc>{html.escape(u)}</loc></url>\n' for u in urls) + '</urlset>\n')

def nav():
    """Links from the main page's Eat and shop tab to each state's page, in both languages."""
    listed = _listed()
    items = ''.join(f'<li><a href="{path(state, 0)}" data-l="en">{html.escape(state_name(state)[0])}</a>'
                    f'<a href="{path(state, 1)}" data-l="uk" lang="uk">{html.escape(state_name(state)[1])}</a></li>' for state in listed)
    return f'<ul class="state-pages">{items}</ul>'
