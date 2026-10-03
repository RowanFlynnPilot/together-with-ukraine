"""The places section: Ukrainian restaurants, bakeries and markets in the United States.

data/places.json is maintained by hand. Each place names its state, and the build confirms its
coordinates fall inside that state, so a mistyped coordinate stops the build instead of moving a
dot. Each place also carries its evidence (rule 2 in CLAUDE.md): a phrase on its own website or in
local press, which check.py confirms is still on that page every week."""
import html, json, pathlib
from collections import Counter
from urllib.parse import quote

import places_uk
from i18n import both, slug

DATA = pathlib.Path(__file__).parent / 'data'
OWN_SITE = 'own website'
DC = 'District of Columbia'

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
            raise ValueError(f"{where}: coordinates fall in {found or 'no state'}, not {p['state']}")
        if not p['basis']: raise ValueError(f'{where}: no evidence that it is Ukrainian (see rule 2 in CLAUDE.md)')
        for b in p['basis']:
            if not (b['by'] and b['url'].startswith('https://') and b['says'].strip()): raise ValueError(f'{where}: incomplete evidence {b}')
        if p['name'] in REVIEW['held']: raise ValueError(f"{where}: both listed and held back in places_review.json")
        p['id'] = 'place-' + slug(f"{p['name']} {p['street'] if branches[p['name'], p['city']] > 1 else ''} {p['city']}")
        if p['id'] in ids: raise ValueError(f'{where}: listed twice')
        ids.add(p['id'])
        p['state_id'] = STATE_IDS[p['state']]
    return places

PLACES = _load()
STATES_WITH_PLACES = {p['state'] for p in PLACES}

def targets():
    """(name, city) -> (element id, English label, Ukrainian label), for links from other sections."""
    out = {}
    for p in PLACES:
        out.setdefault((p['name'], p['city']), (p['id'], f"{p['name']}, {p['city']}", f"{p['name']}, {p['city']}"))
    return out

def claims():
    """(url, phrase, what) for check.py: each place's evidence must still be on its page."""
    return [(b['url'], b['says'], f"{p['name']} ({p['city']}): {b['by']}") for p in PLACES for b in p['basis']]

def summary():
    n, k, dc = len(PLACES), len(STATES_WITH_PLACES - {DC}), DC in STATES_WITH_PLACES
    return (f'{n} places in {k} states' + (' and Washington, DC.' if dc else '.'),
            f'Закладів: {n}. Штатів: {k}' + (', а також Вашингтон (округ Колумбія).' if dc else '.'))

def map_data():
    """What the map script needs: where to draw each dot and which state it belongs to."""
    return [{'name': p['name'], 'lon': p['lon'], 'lat': p['lat'], 'state': p['state_id']} for p in PLACES]

def _evidence(b):
    e = html.escape
    by_en, by_uk = ('its website', 'сайт закладу') if b['by'] == OWN_SITE else (b['by'], b['by'])
    link = lambda label: f'<a href="{e(b["url"])}" target="_blank" rel="noopener">{e(label)}</a>'
    return (f'<span data-l="en">{link(by_en)} says “{e(b["says"])}”</span>'
            f'<span data-l="uk" lang="uk">{link(by_uk)}: «{e(b["says"])}»</span>')

def render(story_links):
    """The list, grouped by state in English alphabetical order (the script reorders the groups for Ukrainian).
    story_links maps a place id to [(story id, English label, Ukrainian label)]."""
    e = html.escape; out = []
    target_ids = {key: target[0] for key, target in targets().items()}  # a story about a business shows on all its listings in that city
    for state in sorted(STATES_WITH_PLACES):
        out.append(f'<div class="state-group" data-state="{STATE_IDS[state]}">\n  <p class="group-name">{both(state, places_uk.STATES[state])}</p>')
        for p in sorted((p for p in PLACES if p['state'] == state), key=lambda p: (p['name'], p['city'])):
            meta = ', '.join(e(x) for x in (p['street'], p['city']) if x)
            query = quote(', '.join((p['name'], p['street'], p['city'], p['state'])))
            links = []
            if p['web']: links.append(f'<a href="{e(p["web"])}" target="_blank" rel="noopener">{both("Website", "Сайт")}</a>')
            links.append(f'<a href="https://www.google.com/maps/search/?api=1&amp;query={query}" target="_blank" rel="noopener">Google Maps</a>')
            for story_id, en, uk in story_links.get(target_ids[p['name'], p['city']], []):
                links.append(f'<a href="#{story_id}">{both("Story: " + en, "Історія: " + uk)}</a>')
            out.append(f'''  <div class="place" id="{p['id']}" tabindex="-1">
    <p class="place-name">{e(p['name'])}</p>
    <p class="place-meta">{both(p['kind'], places_uk.KINDS[p['kind']])}, {meta}</p>
    <p class="src">{both('Why it’s listed', 'Чому в списку')}: {'; '.join(_evidence(b) for b in p['basis'])}.</p>
    <p class="place-links">{''.join(links)}</p>
  </div>''')
        out.append('</div>')
    return '\n'.join(out)
