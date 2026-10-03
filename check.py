"""Re-verify what the page claims against the live web.

1. Every US charity's IRS record and Charity Navigator rating must still match data/.
2. Every link on the page, and every listed business's website, must still load.

Prints a report and exits 1 if anything changed or broke, so a scheduled run fails loudly.

A site that answers 403 or 429 has turned the checker away, which says nothing about whether
the page exists. Which sites do that depends on the network the check runs from, so those links
are reported as refused instead of failing the run."""
import html, json, pathlib, re, sys, time

import build, give
from records import RequestException, charity_navigator_record, get, irs_record

DATA = pathlib.Path(__file__).parent / 'data'
REFUSED = ('403', '429')  # the site turned the checker away

def record_problems():
    problems = []
    for name, pull in (('irs.json', irs_record), ('charity_navigator.json', charity_navigator_record)):
        stored = json.loads((DATA / name).read_text(encoding='utf-8'))
        for ein in give.EINS:
            try:
                live = pull(ein)
            except RequestException as error:
                problems.append(f'{name}: could not pull the record for EIN {ein} ({error})')
                continue
            for field, old in stored[ein].items():
                if live[field] != old:
                    problems.append(f'{name}: EIN {ein} ({give.IRS[ein]["name"]}) {field} changed from {old!r} to {live[field]!r}')
    return problems

def link_status(url):
    try:
        return str(get(url).status_code)
    except RequestException as error:
        return type(error).__name__

def link_report():
    """Returns (broken, refused, total): links that failed, links whose site refused the check, and the count."""
    page = build.build()
    urls = {html.unescape(u) for u in re.findall(r'(?:href|src)="(https?://[^"]+)"', page)}
    urls |= {p['web'] for p in json.loads((DATA / 'places.json').read_text(encoding='utf-8')) if p['web']}
    broken, refused = [], []
    for url in sorted(urls):
        status = link_status(url)
        if status not in ('200', *REFUSED):  # slow sites time out now and then, so a failure gets one more try
            time.sleep(5)
            status = link_status(url)
        if status in REFUSED:
            refused.append(url)
        elif status != '200':
            broken.append(f'link returned {status}: {url}')
    return broken, refused, len(urls)

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    problems = record_problems()
    broken, refused, total = link_report()
    problems += broken
    print(f'{total} links, {len(give.EINS)} charity records checked.')
    print(f'Refused the automated check, so open these by hand ({len(refused)}):')
    for url in refused:
        print(f'  {url}')
    if problems:
        print(f'\n{len(problems)} PROBLEMS:')
        for problem in problems:
            print(f'  {problem}')
        sys.exit(1)
    print('\nAll checks passed.')
