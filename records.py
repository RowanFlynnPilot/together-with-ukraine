"""Pull the public records the Give section relies on: IRS filings (through ProPublica's
Nonprofit Explorer) and Charity Navigator ratings. Used by refresh.py and check.py.

A page that loads but cannot be read stops with an error rather than returning empty values,
so a change in a site's layout is never mistaken for a charity losing its rating."""
import pathlib, re
from urllib.parse import urlsplit

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException  # re-exported for check.py

# A site whose certificate leads to a root the usual stores no longer carry is checked against a file holding the chain
# browsers find for themselves. data/ukrainer-chain.pem says why Ukraїner's needs one.
CHAINS = {'www.ukrainer.net': str(pathlib.Path(__file__).parent / 'data' / 'ukrainer-chain.pem')}

def get(url):
    """Fetch like Chrome does. Several of these sites refuse clients that don't look like a browser."""
    return requests.get(url, impersonate='chrome', timeout=30, verify=CHAINS.get(urlsplit(url).hostname, True))

def irs_record(ein):
    response = get(f'https://projects.propublica.org/nonprofits/api/v2/organizations/{ein}.json')
    response.raise_for_status()
    data = response.json()
    org = data['organization']
    latest = data['filings_with_data'][0] if data['filings_with_data'] else {}
    return {
        'name': org['name'], 'city': org['city'], 'state': org['state'], 'ruling': org['ruling_date'],
        'latest_year': latest.get('tax_prd_yr'), 'revenue': latest.get('totrevenue'),
    }

def charity_navigator_record(ein):
    url = f'https://www.charitynavigator.org/ein/{ein}'
    response = get(url)
    response.raise_for_status()
    stars = re.search(r'"ratingValue":(\d)', response.text)
    if not stars:
        if '<span>Not Rated</span>' not in response.text:
            raise ValueError(f'{url} shows neither a star rating nor "Not Rated"; its layout changed, so update records.py')
        return {'stars': None, 'program_ratio': None, 'program_years': None}
    ratio = re.search(r'Program Expense Ratio\\",\\"value\\":\\"([\d.]+)% of total expenses\\",\\"description\\":\\"[^"]*?\\",\\"dataSource\\":\\"Public data from IRS Form 990\. Fiscal Years? ([\d, ]+)', response.text)
    if not ratio:
        raise ValueError(f'{url} has a star rating but no program expense ratio; its layout changed, so update records.py')
    return {'stars': stars.group(1), 'program_ratio': float(ratio.group(1)), 'program_years': ratio.group(2).strip()}
