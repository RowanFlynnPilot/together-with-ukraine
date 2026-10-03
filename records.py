"""Pull the public records the Give section relies on: IRS filings (through ProPublica's
Nonprofit Explorer) and Charity Navigator ratings. Used by refresh.py and check.py."""
import re

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException  # re-exported for check.py

def get(url):
    """Fetch like Chrome does. Several of these sites refuse clients that don't look like a browser."""
    return requests.get(url, impersonate='chrome', timeout=30)

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
    response = get(f'https://www.charitynavigator.org/ein/{ein}')
    response.raise_for_status()
    stars = re.search(r'"ratingValue":(\d)', response.text)
    ratio = re.search(r'Program Expense Ratio\\",\\"value\\":\\"([\d.]+)% of total expenses\\",\\"description\\":\\"[^"]*?\\",\\"dataSource\\":\\"Public data from IRS Form 990\. Fiscal Years? ([\d, ]+)', response.text)
    return {
        'stars': stars.group(1) if stars else None,
        'program_ratio': float(ratio.group(1)) if ratio else None,
        'program_years': ratio.group(2).strip() if ratio else None,
    }
