"""The In the US tab: where people of Ukrainian ancestry live in the United States, in the Census Bureau's
American Community Survey. census.py pulls the figures into data/census.json; this module checks and renders them.

Every figure is the Bureau's estimate with its margin of error (90 percent confidence). A state where the Bureau
withheld a table shows that it was not published. A claim the page makes about a change, such as the rise since
2021, must clear the margins of error, or the build stops."""
import html, json, math, pathlib

import places, places_uk
from i18n import both, plural_uk

DATA = pathlib.Path(__file__).parent / 'data'
CENSUS = json.loads((DATA / 'census.json').read_text(encoding='utf-8'))
YEAR = CENSUS['year']
NBSP = ' '
# The map's classes: the lowest number of people of Ukrainian ancestry per 1,000 residents in each, with its legend.
BINS = [(0, 'Under 1', 'Менше 1'), (1, '1–2', '1–2'), (2, '2–4', '2–4'), (4, '4–6', '4–6'), (6, '6 or more', '6 і більше')]
SHOWN_ROWS = 15  # the table shows this many states until the reader asks for all of them
# The first city in the name of each metro area the tab may show, in Ukrainian.
CITIES_UK = {
    'New York': 'Нью-Йорк', 'Chicago': 'Чикаго', 'Philadelphia': 'Філадельфія', 'Seattle': 'Сієтл', 'Los Angeles': 'Лос-Анджелес',
    'Sacramento': 'Сакраменто', 'Miami': 'Маямі', 'Portland': 'Портленд', 'Washington': 'Вашингтон', 'Cleveland': 'Клівленд',
    'Detroit': 'Детройт', 'San Francisco': 'Сан-Франциско', 'Boston': 'Бостон', 'Pittsburgh': 'Піттсбург', 'Minneapolis': 'Міннеаполіс',
    'San Jose': 'Сан-Хосе', 'Denver': 'Денвер', 'Phoenix': 'Фінікс', 'Baltimore': 'Балтимор', 'Atlanta': 'Атланта',
}
TABLES = {  # the Census Bureau's tables behind each figure, on data.census.gov
    'ancestry': f'https://data.census.gov/table/ACSDT1Y{YEAR}.B04006',
    'born': f'https://data.census.gov/table/ACSDT1Y{YEAR}.B05006',
}
ABOUT = {
    'ancestry': 'https://www.census.gov/topics/population/ancestry/about.html',
    'foreign born': 'https://www.census.gov/topics/population/foreign-born/about.html',
    'margins': 'https://www.census.gov/content/dam/Census/library/publications/2018/acs/acs_general_handbook_2018_ch07.pdf',
    'withheld': 'https://www.census.gov/programs-surveys/acs/technical-documentation/data-suppression.html',
}

def num(n):
    """A count in both languages: 1,263,837 and 1 263 837."""
    return f'{n:,}', f'{n:,}'.replace(',', NBSP)

def dec(x):
    return f'{x:.1f}', f'{x:.1f}'.replace('.', ',')

def figure(pair):
    """An estimate with its margin of error."""
    (en, uk), (moe_en, moe_uk) = num(pair[0]), num(pair[1])
    return (f'<span class="fig">{both(en, uk)}</span> '
            f'<span class="moe">±{NBSP}{both(moe_en, moe_uk)}</span>')

def per_thousand(state):
    """People of Ukrainian ancestry per 1,000 residents, to the tenth the page shows, so the class matches the number."""
    s = CENSUS['states'][state]
    return round(s['ancestry'][0] / s['population'] * 1000, 1)

def bin_of(rate):
    return max(i for i, (low, _, _) in enumerate(BINS) if rate >= low) + 1

STATES = CENSUS['states']
PUBLISHED = sorted((s for s in STATES if STATES[s]['ancestry']), key=lambda s: -STATES[s]['ancestry'][0])
WITHHELD = sorted(s for s in STATES if not STATES[s]['ancestry'])
NO_BIRTHPLACE = sorted(s for s in STATES if not STATES[s]['born'])
for _state in STATES:
    if _state not in places_uk.STATES: raise ValueError(f'no Ukrainian name for state: {_state}')
PLACES_IN = {state: sum(p['state'] == state for p in places.PLACES) for state in STATES}

def change():
    """How many more people born in Ukraine lived in the US in the latest year than in the first, and whether that clears the margins."""
    years = CENSUS['born_by_year']
    (first, (a, moe_a)), (last, (b, moe_b)) = min(years.items()), max(years.items())
    # The Census Bureau's test for a difference between two estimates: larger than the margin of error of the difference.
    if abs(b - a) <= math.hypot(moe_a, moe_b):
        raise ValueError(f'born in Ukraine, {first} to {last}: the change is within the margins of error; reword the trend note')
    return first, last, round((b - a) / a * 100)

def tiles():
    us = CENSUS['us']
    first, last, pct = change()
    years = CENSUS['born_by_year']
    top = max(e + m for e, m in years.values())
    columns = []
    for year, (e, m) in years.items():
        en, uk = num(e)
        columns.append(f'''        <li class="col">
          <span class="col-plot"><span class="col-bar" style="height:{e / top * 100:.1f}%"></span><span class="col-moe" style="bottom:{(e - m) / top * 100:.1f}%;height:{2 * m / top * 100:.1f}%"></span><span class="col-value" style="bottom:{(e + m) / top * 100:.1f}%">{both(en, uk)}</span></span>
          <span class="col-year">{year}</span>
        </li>''')
    return f'''    <div class="us-stats">
      <div class="stat">
        <p class="stat-num">{both(*num(us['ancestry'][0]))}</p>
        <p class="stat-moe">±{NBSP}{both(*num(us['ancestry'][1]))}</p>
        <p class="stat-label">{both('people in the US gave Ukrainian as their ancestry, alone or with another', 'мешканців США вказали українське походження — єдине або разом з іншим')}</p>
      </div>
      <div class="stat">
        <p class="stat-num">{both(*num(us['born'][0]))}</p>
        <p class="stat-moe">±{NBSP}{both(*num(us['born'][1]))}</p>
        <p class="stat-label">{both('people in the US were born in Ukraine', 'мешканців США народилися в Україні')}</p>
      </div>
      <figure class="stat trend">
        <figcaption class="trend-title">{both('Born in Ukraine, by year', 'Народжені в Україні, за роками')}</figcaption>
        <ol class="cols">
{chr(10).join(columns)}
        </ol>
        <p class="trend-note">{both(f'{pct}% more in {last} than in {first}, the last year before the full-scale invasion.',
                                    f'У {last} році — на {pct}{NBSP}% більше, ніж у {first}-му, останньому році перед повномасштабним вторгненням.')}</p>
      </figure>
    </div>'''

def legend():
    items = [f'<li><span class="swatch bin-{i + 1}"></span>{both(en, uk)}</li>' for i, (_, en, uk) in enumerate(BINS)]
    items.append(f'<li><span class="swatch bin-0"></span>{both("Not published", "Не опубліковано")}</li>')
    return f'<ul class="us-legend">{"".join(items)}</ul>'

def map_section():
    return f'''    <section class="us-block" aria-labelledby="us-map-title">
      <h3 id="us-map-title">{both('Where they live', 'Де вони живуть')}</h3>
      <p class="us-sub">{both(f'People of Ukrainian ancestry per 1,000 residents, by state, {YEAR}', f'Люди українського походження на 1000 мешканців, за штатами, {YEAR}')}</p>
      {legend()}
      <div class="us-map-frame">
        <svg id="us-map" viewBox="0 0 975 610" role="img" aria-labelledby="us-map-label"></svg>
        <span class="visually-hidden" id="us-map-label">{both('Map of the United States, each state shaded by its number of people of Ukrainian ancestry per 1,000 residents. The table below gives every state’s figures.',
                                                              'Мапа Сполучених Штатів, де кожен штат зафарбовано відповідно до кількості людей українського походження на 1000 мешканців. Дані для кожного штату — у таблиці нижче.')}</span>
        <div class="map-tip" hidden></div>
      </div>
      <p class="map-hint">{both('Point at or tap a state for its figures.', 'Наведіть на штат або торкніться його, щоб побачити дані.')}</p>
    </section>'''

def bar(pair, top):
    e, m = pair
    low, high = max(e - m, 0), min(e + m, top)
    return (f'<span class="bar"><span class="bar-fill" style="width:{e / top * 100:.2f}%"></span>'
            f'<span class="bar-moe" style="left:{low / top * 100:.2f}%;width:{(high - low) / top * 100:.2f}%"></span></span>')

def not_published():
    return f'<span class="na">{both("not published", "не опубліковано")}</span>'

def table():
    top = max(sum(STATES[s]['ancestry']) for s in PUBLISHED)
    rows = []
    for i, state in enumerate(PUBLISHED + WITHHELD):
        s, uk = STATES[state], places_uk.STATES[state]
        n = PLACES_IN[state]
        where = f'<span class="visually-hidden">{both(f" {'place' if n == 1 else 'places'} listed in {state}", f" {plural_uk(n, 'заклад', 'заклади', 'закладів')} у списку: {uk}")}</span>'
        listed = f'<a href="#{places.group_id(state)}">{n}{where}</a>' if n else '<span class="na">—</span>'
        if s['ancestry']:
            ancestry = f'{figure(s["ancestry"])}{bar(s["ancestry"], top)}'
            rate = both(*dec(per_thousand(state)))
        else:
            ancestry, rate = not_published(), '<span class="na">—</span>'
        born = figure(s['born']) if s['born'] else not_published()
        more = ' class="more"' if i >= SHOWN_ROWS else ''
        rows.append(f'          <tr{more}><th scope="row">{both(state, uk)}</th><td>{ancestry}</td><td class="num">{rate}</td><td>{born}</td><td class="num">{listed}</td></tr>')
    total = len(STATES)
    return f'''    <section class="us-block" aria-labelledby="us-table-title">
      <h3 id="us-table-title">{both('State by state', 'Штат за штатом')}</h3>
      <div class="table-scroll">
        <table class="us-table" id="us-table">
          <caption class="visually-hidden">{both(f'People of Ukrainian ancestry and people born in Ukraine in each state, {YEAR}, with margins of error, and the number of places listed in the Eat and shop tab',
                                                  f'Люди українського походження та народжені в Україні в кожному штаті, {YEAR}, із похибками, і кількість закладів у розділі «Заклади»')}</caption>
          <thead><tr><th scope="col">{both('State', 'Штат')}</th><th scope="col">{both('Ukrainian ancestry', 'Українське походження')}</th><th scope="col" class="num">{both('Per 1,000 residents', 'На 1000 мешканців')}</th><th scope="col">{both('Born in Ukraine', 'Народжені в Україні')}</th><th scope="col" class="num">{both('Places listed', 'Заклади')}</th></tr></thead>
          <tbody>
{chr(10).join(rows)}
          </tbody>
        </table>
      </div>
      <button type="button" class="more-btn" id="us-more" aria-controls="us-table" aria-expanded="false" hidden><span class="when-closed">{both(f'Show all {total}', f'Показати всі {total}')}</span><span class="when-open">{both('Show fewer', 'Згорнути')}</span></button>
    </section>'''

def metro_name(census_name):
    """'Portland-Vancouver-Hillsboro, OR-WA Metro Area' -> ('Portland', 'Портленд', 'OR–WA')."""
    cities, states = census_name.removesuffix(' Metro Area').rsplit(', ', 1)
    city = cities.split('-')[0]
    if city not in CITIES_UK: raise ValueError(f'no Ukrainian name for the metro area of {city} ({census_name}): add it to CITIES_UK')
    return city, CITIES_UK[city], states.replace('-', '–')

def metros():
    top = max(sum(m['ancestry']) for m in CENSUS['metros'])
    rows = []
    for m in CENSUS['metros']:
        en, uk, codes = metro_name(m['name'])
        born = (both(f'{num(m["born"][0])[0]} born in Ukraine', f'{num(m["born"][0])[1]} народилися в Україні') if m['born']
                else both('born in Ukraine: not published', 'народжені в Україні: не опубліковано'))
        rows.append(f'''        <li class="metro">
          <p class="metro-name">{both(en, uk)} <span class="metro-states">{codes}</span></p>
          <p class="metro-born">{born}</p>
          {bar(m['ancestry'], top)}
          <p class="metro-fig">{figure(m['ancestry'])}</p>
        </li>''')
    return f'''    <section class="us-block" aria-labelledby="us-metros-title">
      <h3 id="us-metros-title">{both('Metro areas with the most people of Ukrainian ancestry', 'Агломерації, де найбільше людей українського походження')}</h3>
      <p class="us-sub">{both(f'Each area is a city with its suburbs, as the Census Bureau draws them, {YEAR}', f'Кожна агломерація — це місто з передмістями в межах, які визначає Бюро перепису населення, {YEAR}')}</p>
      <ol class="metros">
{chr(10).join(rows)}
      </ol>
    </section>'''

def _and(items_en, items_uk):
    join = lambda items, word: items[0] if len(items) == 1 else ', '.join(items[:-1]) + f' {word} ' + items[-1]
    return join(items_en, 'and'), join(items_uk, 'і')

def notes():
    e = html.escape
    link = lambda key, en, uk: (f'<a href="{e(ABOUT[key])}" target="_blank" rel="noopener">{en}</a>', f'<a href="{e(ABOUT[key])}" target="_blank" rel="noopener">{uk}</a>')
    pair = lambda en, uk: f'<li><span data-l="en">{en}</span><span data-l="uk" lang="uk">{uk}</span></li>'
    us = CENSUS['us']
    if us['born'][0] * 2 >= us['ancestry'][0]: raise ValueError('the note says most people of Ukrainian ancestry were not born in Ukraine; the figures no longer show it')
    a_en, a_uk = link('ancestry', 'Ancestry', 'Походження')
    f_en, f_uk = link('foreign born', 'foreign-born', 'народженими за кордоном')
    m_en, m_uk = link('margins', 'margin of error', 'похибку')
    w_en, w_uk = link('withheld', 'withholds a table', 'не публікує таблицю')
    n = len(NO_BIRTHPLACE)
    births_en, births_uk = f'the birthplace table for {n} {"state" if n == 1 else "states"}', f'таблицю місця народження — для {n} {plural_uk(n, "штату", "штатів", "штатів")}'
    if WITHHELD:
        names_en, names_uk = _and(WITHHELD, [places_uk.STATES[s] for s in WITHHELD])
        withheld_en = f'the ancestry table for {names_en}' + (f', and {births_en}' if n else '')
        withheld_uk = f'таблицю походження для штатів {names_uk}' + (f', а {births_uk}' if n else '')
    else:
        withheld_en, withheld_uk = births_en, births_uk
    src = lambda key, en, uk: (f'<a href="{e(TABLES[key])}" target="_blank" rel="noopener">{en}</a>', f'<a href="{e(TABLES[key])}" target="_blank" rel="noopener">{uk}</a>')
    t1_en, t1_uk = src('ancestry', 'B04006, People Reporting Ancestry', 'B04006 (People Reporting Ancestry, походження)')
    t2_en, t2_uk = src('born', 'B05006, Place of Birth for the Foreign-Born Population', 'B05006 (Place of Birth for the Foreign-Born Population, місце народження)')
    items = [
        pair(f'{a_en} is a person’s ethnic origin, descent, roots or heritage, as reported in the survey. The survey counts up to two ancestries for each person, so the figure includes everyone who gave Ukrainian, alone or with another. Ancestry is not the same as birthplace: most people of Ukrainian ancestry in the US were not born in Ukraine.',
             f'{a_uk} — це етнічне коріння, родовід чи спадщина людини, як їх зазначено в опитуванні. Опитування враховує до двох походжень кожної людини, тож у підсумок входять усі, хто вказав українське — єдине або разом з іншим. Походження — не те саме, що місце народження: більшість людей українського походження у США народилися не в Україні.'),
        pair(f'The birthplace count covers people born in Ukraine who were not US citizens at birth, whom the Census Bureau calls {f_en}.',
             f'Підрахунок за місцем народження охоплює людей, народжених в Україні, які не були громадянами США від народження, — Бюро перепису населення називає їх {f_uk}.'),
        pair(f'The survey asks a sample of households each year, so every figure is an estimate. The ± is the Census Bureau’s {m_en}, at 90 percent confidence. Where two states or areas are closer than their margins, their order may not be real.',
             f'Опитування щороку охоплює вибірку домогосподарств, тож кожне число — це оцінка. Знак ± позначає {m_uk}, яку публікує Бюро перепису населення, з довірчою ймовірністю 90{NBSP}%. Якщо два штати чи агломерації відрізняються менше, ніж на свою похибку, їхній порядок може бути випадковим.'),
        pair(f'The Census Bureau {w_en} for a state when its estimates there are too uncertain. For {YEAR} it withheld {withheld_en}.',
             f'Бюро перепису населення {w_uk} для штату, якщо оцінки там надто неточні. За {YEAR} рік воно не оприлюднило {withheld_uk}.'),
        pair(f'Source: US Census Bureau, American Community Survey, {YEAR} 1-year estimates, tables {t1_en} and {t2_en}; for earlier years, the same table B05006 for each year.',
             f'Джерело: Бюро перепису населення США, American Community Survey, однорічні оцінки за {YEAR} рік, таблиці {t1_uk} і {t2_uk}; за попередні роки — та сама таблиця B05006 за кожен рік.'),
    ]
    return f'''    <div class="note us-notes">
      <h3>{both('About these numbers', 'Про ці дані')}</h3>
      <ul>
{chr(10).join('        ' + i for i in items)}
      </ul>
    </div>'''

def render():
    return '\n'.join([tiles(), map_section(), table(), metros(), notes()])

def map_data():
    """For the map script: each state's class and the lines of its tooltip, in both languages, by state FIPS code."""
    out = {}
    for state, s in STATES.items():
        uk = places_uk.STATES[state]
        if s['ancestry']:
            rate_en, rate_uk = dec(per_thousand(state))
            (a_en, a_uk), (am_en, am_uk) = num(s['ancestry'][0]), num(s['ancestry'][1])
            en = [state, f'{rate_en} per 1,000 residents', f'{a_en} ± {am_en} of Ukrainian ancestry']
            uk_lines = [uk, f'{rate_uk} на 1000 мешканців', f'{a_uk} ± {am_uk} українського походження']
            cls = bin_of(per_thousand(state))
        else:
            en = [state, f'Not published for {YEAR}']
            uk_lines = [uk, f'Дані за {YEAR} рік не опубліковано']
            cls = 0
        if s['ancestry'] and s['born']:
            (b_en, b_uk), (bm_en, bm_uk) = num(s['born'][0]), num(s['born'][1])
            en.append(f'{b_en} ± {bm_en} born in Ukraine')
            uk_lines.append(f'{b_uk} ± {bm_uk} народилися в Україні')
        out[s['fips']] = {'bin': cls, 'en': en, 'uk': uk_lines}
    return out

def overview():
    """The header's count for this tab: (number in English, in Ukrainian, label in English, in Ukrainian)."""
    millions = CENSUS['us']['ancestry'][0] / 1e6
    return (f'{millions:.2f}M', f'{millions:.2f}'.replace('.', ',') + NBSP + 'млн',
            'people of Ukrainian ancestry in the US', 'людей українського походження у США')
