"""Re-verify what the page claims against the live web.

1. Every US charity's IRS record and Charity Navigator rating must still match data/.
2. Every link on the page must still load.
3. Every recorded phrase must still be on its page: the evidence each business is listed on, the EIN on
   a charity's own site, the person a story is about on the report it comes from. A page that loads
   without its phrase has changed: the business rebranded or closed, the story was taken down, or the
   site was redesigned and the phrase needs updating.
4. The scripts loaded from the CDN must still match their integrity hashes, or browsers will refuse them.
5. Nothing the page dates may be too old: the entries about the war today, and the reviews by hand
   of the places and of the Give list.
6. The Census figures must be the latest year the Census Bureau has published.

Prints a report and exits 1 if anything changed, broke or went stale, so a scheduled run fails loudly.

A site that answers 403 or 429 has turned the checker away, which says nothing about whether the page
exists. Which sites do that depends on the network the check runs from. A site that leaves out part of
its certificate chain (ukrainer.net does) works in browsers, which fetch the missing certificate
themselves, but cannot be verified by a script. Those links, with the phrases that could not be
confirmed on them, are listed for a look by hand instead of failing the run. Any other certificate
error fails it, because browsers would show a warning too."""
import base64, datetime, hashlib, html, json, pathlib, re, sys, time
from concurrent.futures import ThreadPoolExecutor

import build, census, culture, diaspora, give, history, places, stories
from records import RequestException, charity_navigator_record, get, irs_record

DATA = pathlib.Path(__file__).parent / 'data'
INCOMPLETE_CHAIN = 'incomplete certificate chain'
REFUSED = ('403', '429', '202', INCOMPLETE_CHAIN)  # links the checker cannot judge, listed for a look by hand; 202 is a bot challenge
# Sites that show automated readers a stand-in page: 403 from a home connection, and from GitHub's servers a page that
# answers 200 without the article. Their links are refused whatever they answer, and listed for a look by hand.
WALLED = ('https://www.13newsnow.com/', 'https://www.abc10.com/', 'https://www.king5.com/')
NOT_SOURCES = ('https://www.google.com/maps/search/',)  # searches the page builds for each place
MAX_AGE = {  # what, (date, days)
    'the entries about the war today (AS_OF in history.py)': (history.AS_OF, 120),
    'the review of the places ("reviewed" in data/places_review.json)': (places.REVIEW['reviewed'], 365),
    'the review of the Give list (REVIEWED in give.py)': (give.REVIEWED, 180),
    "the review of the Culture tab's events and resources (REVIEWED in culture.py)": (culture.REVIEWED, 365),
}

def record_problems():
    problems = []
    for name, pull in (('irs.json', irs_record), ('charity_navigator.json', charity_navigator_record)):
        stored = json.loads((DATA / name).read_text(encoding='utf-8'))
        for ein in give.EINS:
            try:
                live = pull(ein)
            except (RequestException, ValueError) as error:
                problems.append(f'{name}: could not pull the record for EIN {ein} ({error})')
                continue
            for field, old in stored[ein].items():
                if live[field] != old:
                    problems.append(f'{name}: EIN {ein} ({give.IRS[ein]["name"]}) {field} changed from {old!r} to {live[field]!r}')
    return problems

def stale():
    today = datetime.date.today()
    return [f'{what} is dated {date}, more than {days} days ago: review it, then update the date'
            for what, (date, days) in MAX_AGE.items() if (today - datetime.date.fromisoformat(date)).days > days]

def fetch(url):
    """(status, response). A failure other than a refusal gets one more try: slow sites time out now and then."""
    for attempt in range(2):
        try:
            response = get(url)
            status = str(response.status_code)
        except RequestException as error:
            response = None
            status = INCOMPLETE_CHAIN if 'unable to get local issuer certificate' in str(error) else type(error).__name__
        if url.startswith(WALLED) and status == '200': status = '403'
        if status in ('200', *REFUSED) or attempt:
            return status, response
        time.sleep(5)

def normalize(text):
    return ' '.join(text.replace('’', "'").replace('‘', "'").split()).casefold()

def page_text(response):
    """The page's text with the tags removed. Script contents stay, because some sites carry their text in page data."""
    return normalize(html.unescape(re.sub(r'<[^>]+>', ' ', response.text)))

def census_problems():
    """A newer year of the Census figures than data/census.json holds."""
    year = diaspora.YEAR + 1
    try:
        if not census.published(year): return []
    except (RequestException, ValueError) as error:
        return [f'could not check for {year} Census figures ({error})']
    return [f'the Census Bureau has published its {year} figures: run census.py, review the diff and commit']

def web_report():
    """Returns (problems, refused, link count, phrase count). refused lists each refused url with the phrases it should carry."""
    page = build.build()
    claims = places.claims() + give.claims() + stories.claims() + culture.claims() + history.claims()
    links = re.sub(r'<link rel="preconnect"[^>]*>', '', page)  # a preconnect hint names a host, not a page
    urls = {html.unescape(u) for u in re.findall(r'(?:href|src)="(https?://[^"]+)"', links) if not u.startswith(NOT_SOURCES)}
    urls |= {url for url, _, _ in claims}
    integrity = dict(re.findall(r'<script src="([^"]+)" integrity="([^"]+)"', page))
    with ThreadPoolExecutor(max_workers=8) as pool:  # one at a time took 7 minutes, and the page keeps growing
        results = dict(zip(sorted(urls), pool.map(fetch, sorted(urls))))
    problems, refused = [], {}
    for url, (status, _) in results.items():
        if status in REFUSED: refused[url] = (status, [])
        elif status != '200': problems.append(f'link returned {status}: {url}')
    texts = {url: page_text(response) for url, (status, response) in results.items() if status == '200'}
    for url, phrase, what in claims:
        if url in refused: refused[url][1].append(phrase)
        elif url in texts and normalize(phrase) not in texts[url]:
            problems.append(f'{what}: "{phrase}" is no longer on {url}')
    for url, expected in integrity.items():
        status, response = results[url]
        actual = 'sha384-' + base64.b64encode(hashlib.sha384(response.content).digest()).decode() if status == '200' else None
        if actual and actual != expected:
            problems.append(f'{url} no longer matches its integrity hash, so browsers will refuse it: pin a version whose hash is {actual}')
    return problems, refused, len(urls), len(claims)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    problems = record_problems() + stale() + census_problems()
    web_problems, refused, links, phrases = web_report()
    problems += web_problems
    print(f'{links} links, {phrases} phrases on them, {len(give.EINS)} charity records checked.')
    print(f'Could not be checked automatically, so open these by hand ({len(refused)}):')
    for url, (status, expected) in refused.items():
        print(f'  {url} ({status})' + ''.join(f'\n      should say: "{phrase}"' for phrase in expected))
    if problems:
        print(f'\n{len(problems)} PROBLEMS:')
        for problem in problems:
            print(f'  {problem}')
        sys.exit(1)
    print('\nAll checks passed.')
