"""Build site/index.html from the content modules, the data folder and template.html.

Uses no network. A missing translation, an unknown state or kind of place, or a US charity
without a pulled record stops the build."""
import json, pathlib, sys

import give, history, places_uk
from i18n import both, fill_markers

ROOT = pathlib.Path(__file__).parent
MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MONTHS_UK = ['січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня']

def read_json(name):
    return json.loads((ROOT / 'data' / name).read_text(encoding='utf-8'))

def embed(obj):
    """JSON that is safe inside a <script> element."""
    return json.dumps(obj, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')

def build():
    places = read_json('places.json')
    states = read_json('states-10m.json')
    state_names = {g['properties']['name'] for g in states['objects']['states']['geometries'] if int(g['id']) < 60}
    if missing := state_names - set(places_uk.STATES):
        raise ValueError(f'no Ukrainian name for states: {missing}')
    if missing := {p['kind'] for p in places} - set(places_uk.KINDS):
        raise ValueError(f'no Ukrainian name for kinds of place: {missing}')
    for p in places:
        if p['web'] and not p['web'].startswith(('https://', 'http://')):
            raise ValueError(f"bad website for {p['name']}: {p['web']}")

    year, month, day = (int(x) for x in read_json('checked.json')['date'].split('-'))
    checked_en = f'{MONTHS_EN[month - 1]} {day}, {year}'
    checked_uk = f'{day} {MONTHS_UK[month - 1]} {year} року'

    timeline, _, eras = history.render()
    give_html, _ = give.render()
    era_nav = '\n'.join(f'      <button data-era="{i}">{both(en, uk)}</button>' for i, en, uk in eras)

    template = (ROOT / 'template.html').read_text(encoding='utf-8')
    page = (fill_markers(template)
            .replace('__ERA_NAV__', era_nav).replace('__HISTORY__', timeline).replace('__GIVE__', give_html)
            .replace('__PULLED_EN__', checked_en).replace('__PULLED_UK__', checked_uk)
            .replace('__PLACES__', embed(places)).replace('__STATES__', embed(states))
            .replace('__PLACES_UK__', embed({'states': places_uk.STATES, 'kinds': places_uk.KINDS})))
    markup = page.split('<script type="application/json"')[0]
    if '__' in markup or '{{' in markup:
        raise ValueError('unfilled placeholder in template.html')
    return page

if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    out = ROOT / 'site' / 'index.html'
    out.parent.mkdir(exist_ok=True)
    out.write_text(build(), encoding='utf-8')
    print(f'built {out.relative_to(ROOT)} ({out.stat().st_size:,} bytes)')
