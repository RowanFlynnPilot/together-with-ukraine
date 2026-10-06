"""Pull the Census Bureau's figures for the In the US tab into data/census.json.

The figures are the American Community Survey's 1-year estimates, which usually come out each September.
check.py fails once a newer year is published: run this, read `git diff data/census.json`, and commit.

Reads the Bureau's summary files, which need no key (its data API now does), and finds each figure's line
in its table through the API's descriptions of the tables, which need none either, so a renumbered table
is followed rather than misread."""
import datetime, json, pathlib, re, sys

from records import get

DATA = pathlib.Path(__file__).parent / 'data'
FILES = 'https://www2.census.gov/programs-surveys/acs/summary_file/{year}/table-based-SF'
FIRST_YEAR = 2021  # the first year published as table files, and the last before the full-scale invasion
FIGURES = {  # name: (table, the end of the label on its line)
    'population': ('B04006', 'Estimate!!Total:'),  # this table counts everyone, so its total is the population
    'ancestry': ('B04006', '!!Ukrainian'),
    'born': ('B05006', '!!Eastern Europe:!!Ukraine'),
}
US = '0100000US'
CONTROLLED = -555555555
METROS = 10  # how many metro areas the tab shows

def table_url(year, table):
    return f'{FILES.format(year=year)}/data/1YRData/acsdt1y{year}-{table.lower()}.dat'

def published(year):
    """Whether a year's tables are out. Before release the files are already there, but locked."""
    status = get(table_url(year, 'B04006')).status_code
    if status not in (200, 401, 403, 404): raise ValueError(f'{table_url(year, "B04006")} answered {status}')
    return status == 200

def read(url):
    response = get(url)
    response.raise_for_status()
    head, *body = response.text.splitlines()
    head = head.split('|')
    return [dict(zip(head, l.split('|'))) for l in body]

class Year:
    """One year's tables: each figure for any place, or None where the Bureau withheld the table there."""
    def __init__(self, year, names):
        self.year = year
        self.tables = {t: {r['GEO_ID']: r for r in read(table_url(year, t))} for t in {FIGURES[n][0] for n in names}}
        self.lines = {n: self._line(*FIGURES[n]) for n in names}

    def _line(self, table, label_end):
        response = get(f'https://api.census.gov/data/{self.year}/acs/acs1/groups/{table}.json')
        response.raise_for_status()
        found = [v for v, about in response.json()['variables'].items() if v.endswith('E') and about['label'].endswith(label_end)]
        if len(found) != 1: raise ValueError(f'{self.year} {table}: {len(found)} lines end with {label_end!r}: {found}')
        return found[0][:-1].replace('_', '_{}')  # B04006_092E -> B04006_{}092, for the estimate (E) and margin (M) columns

    def __call__(self, name, geo):
        row = self.tables[FIGURES[name][0]].get(geo)
        if row is None: return None
        column = self.lines[name]
        estimate, moe = int(row[column.format('E')]), int(row[column.format('M')])
        # The Bureau writes notes in place of numbers, as large negative ones. Population totals carry one meaning they
        # are fixed to its population estimates and have no margin of error; anything else is unexpected.
        if name == 'population' and moe == CONTROLLED: return estimate
        if estimate < 0 or moe < 0: raise ValueError(f'{self.year} {column.format("")} for {geo} carries the note {estimate}, {moe}')
        return [estimate, moe]

def pull():
    year = datetime.date.today().year
    while not published(year): year -= 1
    now = Year(year, FIGURES)
    where = {r['GEO_ID']: r['NAME'] for r in read(f'{FILES.format(year=year)}/documentation/Geos{year}1YR.txt')}
    states = {}
    for geo in sorted(g for g in where if re.fullmatch(r'0400000US\d\d', g) and g != '0400000US72'):  # not Puerto Rico
        states[where[geo]] = {'fips': geo[-2:], 'population': now('population', geo),
                              'ancestry': now('ancestry', geo), 'born': now('born', geo)}
    if len(states) != 51: raise ValueError(f'expected 50 states and DC, found {len(states)}')
    metros = sorted((g for g in now.tables['B04006'] if g.startswith('310M700US')), key=lambda g: -now('ancestry', g)[0])
    return {
        'year': year,
        'pulled': datetime.date.today().isoformat(),
        'us': {'population': now('population', US), 'ancestry': now('ancestry', US), 'born': now('born', US)},
        'born_by_year': {str(y): (now if y == year else Year(y, ['born']))('born', US) for y in range(FIRST_YEAR, year + 1)},
        'states': states,
        'metros': [{'name': where[g], 'population': now('population', g), 'ancestry': now('ancestry', g), 'born': now('born', g)}
                   for g in metros[:METROS]],
    }

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    census = pull()
    (DATA / 'census.json').write_text(json.dumps(census, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"wrote data/census.json: {census['year']} figures for {len(census['states'])} states and {len(census['metros'])} metro areas;"
          ' review with: git diff data/census.json')
