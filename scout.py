"""Find candidate places for the Eat and shop tab in OpenStreetMap, across the United States.

Two searches: Overpass for every venue or shop tagged with Ukrainian cuisine or a Ukrainian name
(name:uk), and Nominatim for venues and shops whose names contain a Ukrainian word. Leads already
listed in data/places.json or held back in data/places_review.json are dropped. A lead is only a
lead: it still has to pass rule 2 in CLAUDE.md before it is listed. Writes nothing; prints the
leads, grouped by state.

A search of every name in the country for Ukrainian words would find more, but it is too heavy for
the public Overpass servers (it timed out on all of them in October 2026). The research behind the
list was done by reading local press, which finds far more than OpenStreetMap does.

    python scout.py"""
import json, math, re, sys, time, urllib.parse, urllib.request

import places

# Both services turn away clients that pretend to be a browser, and their usage policies ask callers to say who they are.
USER_AGENT = 'together-with-ukraine scout (https://github.com/RowanFlynnPilot/together-with-ukraine)'
OVERPASS = 'https://overpass-api.de/api/interpreter'
NOMINATIM = 'https://nominatim.openstreetmap.org/search?'
VENUE = '["amenity"~"^(restaurant|cafe|fast_food|bar|pub|ice_cream|marketplace)$"]'
TAGGED = f'''[out:json][timeout:180];
area["ISO3166-1"="US"][admin_level=2]->.us;
(nwr["cuisine"~"ukrainian",i](area.us); nwr["name:uk"]{VENUE}(area.us); nwr["name:uk"]["shop"](area.us););
out center tags;'''
WORDS = ['ukrainian restaurant', 'ukrainian cafe', 'ukrainian bakery', 'ukrainian deli', 'ukrainian store', 'ukrainian market',
         'ukrainian kitchen', 'ukrainian gift', 'ukraine', 'kyiv', 'kiev', 'lviv', 'kharkiv', 'odesa', 'varenyky', 'borscht', 'borsch', 'tryzub']
VENUE_TYPES = {'restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'ice_cream', 'marketplace'}
NEAR_METERS = 300  # a lead this close to a listed place with a similar name is that place
NO_NAME = '(no name)'  # a lead with no name this close to a listed place is taken to be that place

def fetch(url, data=None):
    request = urllib.request.Request(url, data=data, headers={'User-Agent': USER_AGENT})
    with urllib.request.urlopen(request, timeout=240) as response:
        return json.load(response)

def tagged():
    """(name, lat, lon, kind, tags, osm url) for everything Overpass finds tagged as Ukrainian."""
    body = fetch(OVERPASS, urllib.parse.urlencode({'data': TAGGED}).encode())
    for el in body['elements']:
        tags = el.get('tags', {})
        lat, lon = (el['lat'], el['lon']) if 'lat' in el else (el['center']['lat'], el['center']['lon'])
        yield (tags.get('name') or tags.get('name:uk') or NO_NAME, lat, lon, tags.get('amenity') or 'shop=' + tags.get('shop', '?'),
               tags, f"https://www.openstreetmap.org/{el['type']}/{el['id']}")

def named():
    """The same, for venues and shops whose names Nominatim matches to a Ukrainian word. At most one request a second."""
    for word in WORDS:
        query = urllib.parse.urlencode({'q': word, 'countrycodes': 'us', 'format': 'jsonv2', 'limit': 50, 'extratags': 1})
        for r in fetch(NOMINATIM + query):
            if r['category'] == 'shop' or (r['category'] == 'amenity' and r['type'] in VENUE_TYPES):
                yield (r['name'], float(r['lat']), float(r['lon']), r['type'] if r['category'] == 'amenity' else 'shop=' + r['type'],
                       r.get('extratags') or {}, f"https://www.openstreetmap.org/{r['osm_type']}/{r['osm_id']}")
        time.sleep(1.1)

def meters(lat1, lon1, lat2, lon2):
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    return 6371000 * math.hypot(x, math.radians(lat2 - lat1))

def simple(name):
    return re.sub(r'[^a-z0-9]', '', re.sub(r"['’]s\b", '', name.lower()))

def known(name, lat, lon):
    for p in places.PLACES:
        same_name = simple(p['name'])[:6] in simple(name) or simple(name)[:6] in simple(p['name'])
        if (same_name or name == NO_NAME) and meters(lat, lon, p['lat'], p['lon']) < NEAR_METERS: return True
    return any(simple(name)[:8] in simple(held) for held in places.REVIEW['held'])

def leads():
    rings = places._rings_by_state()
    seen, out = set(), []
    for name, lat, lon, kind, tags, osm in [*tagged(), *named()]:
        if 'brand' in tags or 'brand:wikidata' in tags: continue  # chains carry their name in many languages, Ukrainian among them
        state = next((s for s, r in rings.items() if places._contains(r, lon, lat)), None)
        if osm in seen or state is None or known(name, lat, lon): continue
        seen.add(osm)
        out.append((state, name, kind + (f" ({tags['cuisine']})" if tags.get('cuisine') else ''),
                    tags.get('website') or tags.get('contact:website') or '', f'{lat:.5f}, {lon:.5f}', osm))
    return sorted(out)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    found = leads()
    print(f'{len(found)} leads in OpenStreetMap that are neither listed nor held back:')
    state = None
    for lead in found:
        if lead[0] != state:
            state = lead[0]
            print(f'\n{state}')
        print('  ' + ' | '.join(x for x in lead[1:] if x))
