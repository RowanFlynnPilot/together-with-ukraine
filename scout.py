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

def stem(word):
    """The part of a search that makes it Ukrainian: 'ukrainian deli' and 'ukraine' -> 'ukrain', 'lviv' -> 'lviv'."""
    return 'ukrain' if word.startswith('ukrain') else word

def named():
    """The same, for venues and shops whose names Nominatim matches to a Ukrainian word. At most one request a second.
    Nominatim also matches words in an address, which turned every shop in Chicago's Ukrainian Village into a lead
    (October 2026), so a result counts only when the word is in its name or its cuisine."""
    for word in WORDS:
        query = urllib.parse.urlencode({'q': word, 'countrycodes': 'us', 'format': 'jsonv2', 'limit': 50, 'extratags': 1})
        for r in fetch(NOMINATIM + query):
            said = f"{r['name']} {(r.get('extratags') or {}).get('cuisine', '')}".lower()
            if stem(word) not in said: continue
            if r['category'] == 'shop' or (r['category'] == 'amenity' and r['type'] in VENUE_TYPES):
                yield (r['name'], float(r['lat']), float(r['lon']), r['type'] if r['category'] == 'amenity' else 'shop=' + r['type'],
                       r.get('extratags') or {}, f"https://www.openstreetmap.org/{r['osm_type']}/{r['osm_id']}")
        time.sleep(1.1)

def meters(lat1, lon1, lat2, lon2):
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    return 6371000 * math.hypot(x, math.radians(lat2 - lat1))

def simple(name):
    return re.sub(r'[^a-z0-9]', '', re.sub(r"['’]s\b", '', name.lower()))

STATE_CODES = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT',
    'Delaware': 'DE', 'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL',
    'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
    'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
    'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA',
    'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
}
if set(STATE_CODES) != set(places.STATE_IDS): raise ValueError('STATE_CODES needs exactly the states places.py knows')

def same_business(a, b):
    """Two names for one business: the same, or one the other with words added (Babushka Deli, Babushka Deli & Bakery)."""
    a, b = simple(a), simple(b)
    short, long = sorted((a, b), key=len)
    return a == b or (len(short) >= 6 and long.startswith(short))

def held(name, state):
    """Whether a lead was already looked at and held back. A held entry is 'Name (City, ST)' and matches the same business
    in that state only, so a held Ukrainian Cultural Center in Michigan does not hide a Ukrainian Kitchen in Colorado. An
    entry that names no state (a chain such as Multicook, or an early entry) matches its name anywhere."""
    for key in places.REVIEW['held']:
        located = re.fullmatch(r'(.+?) \((?:.*, )?([A-Z]{2})\)', key)
        held_name, held_state = (located[1], located[2]) if located else (re.sub(r' \(.*\)$', '', key), None)
        if same_business(name, held_name) and held_state in (None, STATE_CODES[state]): return True
    return False

def known(name, lat, lon, state):
    for p in places.PLACES:
        same_name = simple(p['name'])[:6] in simple(name) or simple(name)[:6] in simple(p['name'])
        if (same_name or name == NO_NAME) and meters(lat, lon, p['lat'], p['lon']) < NEAR_METERS: return True
    return name != NO_NAME and held(name, state)

def leads():
    rings = places._rings_by_state()
    seen, out = set(), []
    for name, lat, lon, kind, tags, osm in [*tagged(), *named()]:
        if 'brand' in tags or 'brand:wikidata' in tags: continue  # chains carry their name in many languages, Ukrainian among them
        state = next((s for s, r in rings.items() if places._contains(r, lon, lat)), None)
        if osm in seen or state is None or known(name, lat, lon, state): continue
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
