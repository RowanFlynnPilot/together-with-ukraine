"""Pull fresh IRS and Charity Navigator records for every US charity on the page, write them
to data/, and stamp today's date as the day the page was checked.

Run this after check.py reports a change, read `git diff data/`, and commit if the change is real."""
import datetime, json, pathlib, sys

import give
from records import charity_navigator_record, irs_record

DATA = pathlib.Path(__file__).parent / 'data'

def write(name, obj):
    (DATA / name).write_text(json.dumps(obj, indent=1) + '\n', encoding='utf-8')

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    write('irs.json', {ein: irs_record(ein) for ein in give.EINS})
    write('charity_navigator.json', {ein: charity_navigator_record(ein) for ein in give.EINS})
    write('checked.json', {'date': datetime.date.today().isoformat()})
    print(f'refreshed records for {len(give.EINS)} charities; review with: git diff data/')
