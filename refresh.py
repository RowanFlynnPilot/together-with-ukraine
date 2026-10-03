"""Pull fresh IRS and Charity Navigator records for every US charity on the page, write them
to data/, and stamp today's date as the day the records were pulled.

Run this after check.py reports a change, read `git diff data/`, and commit if the change is real.
It does not touch the review dates of the places or the Give list: those mean a person looked."""
import datetime, json, pathlib, sys

import give
from records import charity_navigator_record, irs_record

DATA = pathlib.Path(__file__).parent / 'data'

def write(name, obj):
    (DATA / name).write_text(json.dumps(obj, indent=1) + '\n', encoding='utf-8')

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    irs = {ein: irs_record(ein) for ein in give.EINS}
    cn = {ein: charity_navigator_record(ein) for ein in give.EINS}
    write('irs.json', irs)
    write('charity_navigator.json', cn)
    write('checked.json', {'records': datetime.date.today().isoformat()})
    print(f'refreshed records for {len(give.EINS)} charities; review with: git diff data/')
