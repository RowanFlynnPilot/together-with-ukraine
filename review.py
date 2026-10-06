"""The review page (site/review.html): every English text on the page beside its Ukrainian, numbered and
grouped by section, for a native speaker to check (the open item in CLAUDE.md). Each row's button opens
the "Report a mistake" form on GitHub with the row filled in and the Ukrainian ready to edit. Names
spelled in Ukrainian from English-only reports are flagged, since their spelling is a guess.

The page is not linked from the tabs, only from the footer's note on the translation, and asks search
engines not to index it."""
import html, re, pathlib
from urllib.parse import urlencode

import culture, diaspora, give, history, places, places_uk, stories
import history_uk as UK

ROOT = pathlib.Path(__file__).parent
ISSUE = 'https://github.com/RowanFlynnPilot/together-with-ukraine/issues/new?'
# Ukrainian spellings of names taken from English-only reports (CLAUDE.md, Open items), as stems.
GUESSED_NAMES = ['Безпрозван', 'Поканевич', 'Сокор', 'Гапон', 'Бірчард', 'Фертш', 'Градинар', 'Ентін', 'Дзуенко']

def pairs():
    """(section, where, English, Ukrainian) for every text on the page, section by section, in page order."""
    out = []
    add = lambda section, where, pair: out.append((section, where, *pair))
    for match in re.finditer(r'\{\{(.+?)\|\|(.+?)\}\}', (ROOT / 'template.html').read_text(encoding='utf-8'), re.S):
        en, uk = (re.sub(r'__[A-Z_]+__', '…', re.sub(r'\s+', ' ', x)).strip() for x in match.groups())
        add('Page', 'Interface', (en, uk))
    add('Culture', 'Header photo', culture.HERO['alt'])
    for v in culture.GALLERY: add('Culture', 'Gallery', v['photo']['alt'])
    for section_id, title, intro, entries in culture.SECTIONS:
        add('Culture', 'Section title', title)
        if intro: add('Culture', 'Section intro', intro)
        for x in entries:
            where = x['name'][0]
            add('Culture', where, x['name'])
            add('Culture', where, x['about'])
            for field in ('date', 'when', 'where'):
                if field in x: add('Culture', where, x[field])
            if x.get('photo'): add('Culture', f'{where}: picture', x['photo']['alt'])
            if x['key'] in culture.RELABELS:
                for label in culture.RELABELS[x['key']]: add('Culture', f'{where}: label', label)
    for label, _ in culture.RESOURCE_KINDS.values(): add('Culture', 'Resource kind', label)
    for era_id, name, span, events in history.ERAS:
        add('History', name, (name, UK.ERAS[name][0]))
        add('History', name, (span, UK.ERAS[name][1]))
        if era_id in history.ERA_PHOTOS: add('History', f'{name}: picture', history.ERA_PHOTOS[era_id]['alt'])
        for year, title, text, _ in events:
            where = f'{year}: {title}'
            if year in UK.YEARS: add('History', where, (year, UK.YEARS[year]))
            add('History', where, (title, UK.EVENTS[title][0]))
            add('History', where, (text, UK.EVENTS[title][1]))
            if title in history.EVENT_PHOTOS: add('History', f'{where}: picture', history.EVENT_PHOTOS[title]['alt'])
    for theme_id, title, intro, entries in stories.THEMES:
        add('People', 'Theme', title)
        add('People', 'Theme', intro)
        for s in entries:
            where = s['person'][0]
            for field in ('person', 'context', 'title', 'text'): add('People', where, s[field])
            if s['photo']: add('People', f'{where}: picture', s['photo']['alt'])
    for part, en, uk in diaspora.texts():
        if en != uk: add('In the US', part, (en, uk))  # the map legend's ranges read the same in both
    add('Eat and shop', 'Summary', places.summary())
    for tag in places.UKRAINIAN.values(): add('Eat and shop', 'Tag', tag)
    for label, _ in places.GROUPS.values(): add('Eat and shop', 'Kind filter', label)
    for kind, uk in places_uk.KINDS.items(): add('Eat and shop', 'Kind of place', (kind, uk))
    for state, uk in places_uk.STATES.items(): add('Eat and shop', 'State', (state, uk))
    for _, p in places.PHOTOS: add('Eat and shop', 'Picture', p['alt'])
    for title, intro, orgs in give.GROUPS:
        add('Give', 'Group', title)
        if intro: add('Give', 'Group', intro)
        for o in orgs:
            where = o['name'][0]
            for field in ('name', 'kind', 'what', 'action'): add('Give', where, o[field])
            for check in o['checks']: add('Give', f'{where}: checked', check[:2])
    seen, unique = set(), []
    for item in out:  # the same pair shown in several places is reviewed once
        if item[2:] not in seen: seen.add(item[2:]); unique.append(item)
    return unique

SECTIONS = {'Page': 'Загальне', 'Culture': 'Культура', 'History': 'Історія', 'People': 'Люди', 'In the US': 'У США', 'Eat and shop': 'Заклади', 'Give': 'Допомогти'}

def _issue_link(number, section, where, en, uk):
    fields = {'template': 'problem.yml', 'title': f'Ukrainian #{number}: {where}'[:120],
              'what': f'Ukrainian text #{number} on the review page ({section}: {where}).\n\nEnglish:\n{en}\n\nUkrainian now:\n{uk}',
              'source': uk}
    url = ISSUE + urlencode(fields)
    if len(url) > 7500:  # GitHub refuses very long links; the English is on the review page anyway
        fields['what'] = f'Ukrainian text #{number} on the review page ({section}: {where}).'
        url = ISSUE + urlencode(fields)
    return url

def render():
    e = html.escape
    rows, counts = [], {}
    for number, (section, where, en, uk) in enumerate(pairs(), 1):
        counts[section] = counts.get(section, 0) + 1
        guessed = any(stem in uk for stem in GUESSED_NAMES)
        flag = '<p class="flag">Ім’я з англомовного джерела: перевірте написання · A name from an English-only report: check the spelling</p>' if guessed else ''
        anchor = f' id="{section_id(section)}"' if counts[section] == 1 else ''
        rows.append(f'''  <tr{anchor}{' class="guessed"' if guessed else ''}>
    <td class="num">{number}</td>
    <td class="where"><span class="section">{e(SECTIONS[section])} · {e(section)}</span>{e(where)}</td>
    <td lang="en">{e(en)}</td>
    <td lang="uk">{e(uk)}{flag}</td>
    <td class="act"><a href="{e(_issue_link(number, section, where, en, uk))}" target="_blank" rel="noopener">Запропонувати виправлення<span class="en">Suggest a fix</span></a></td>
  </tr>''')
    nav = ' '.join(f'<a href="#{section_id(s)}">{e(SECTIONS[s])} <span>{n}</span></a>' for s, n in counts.items())
    guessed_total = sum(1 for _, _, _, uk in pairs() if any(stem in uk for stem in GUESSED_NAMES))
    return TEMPLATE.replace('__COUNT__', str(sum(counts.values()))).replace('__GUESSED__', str(guessed_total)).replace('__NAV__', nav).replace('__ROWS__', '\n'.join(rows))

def section_id(section):
    return 'section-' + re.sub(r'[^a-z]+', '-', section.lower()).strip('-')

TEMPLATE = '''<!doctype html>
<html lang="uk">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Перевірка українського тексту · Checking the Ukrainian</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 3 2'%3E%3Crect width='3' height='1' fill='%230057B7'/%3E%3Crect y='1' width='3' height='1' fill='%23FFD700'/%3E%3C/svg%3E">
<style>
:root { color-scheme: light dark; --paper: #FFFFFF; --ink: #0B1F3A; --muted: #4A5B74; --line: #C3D2E6; --wash: #EEF3FA; --link: #0057B7; --flag: #FFF3B0; }
@media (prefers-color-scheme: dark) { :root { --paper: #0A1626; --ink: #EAF0F8; --muted: #A8B8CE; --line: #2A4263; --wash: #12233A; --link: #8DBEFF; --flag: #4A3F00; } }
* { box-sizing: border-box; }
body { margin: 0; background: var(--paper); color: var(--ink); font: 1rem/1.5 "Segoe UI", system-ui, sans-serif; }
header { background: #0057B7; color: #FFFFFF; border-bottom: 8px solid #FFD700; padding: 1.5rem 1.25rem; }
header h1 { margin: 0 0 0.5rem; font-size: 1.6rem; line-height: 1.2; }
header p { margin: 0.35rem 0 0; max-width: 52rem; }
header a { color: #FFFFFF; }
nav { position: sticky; top: 0; z-index: 1; display: flex; flex-wrap: wrap; gap: 0.4rem; padding: 0.6rem 1.25rem; background: var(--wash); border-bottom: 1px solid var(--line); }
nav a { padding: 0.25rem 0.7rem; border: 1px solid var(--line); background: var(--paper); color: var(--ink); text-decoration: none; font-weight: 600; }
nav a span { color: var(--muted); font-weight: 400; }
main { padding: 0 1.25rem 3rem; }
table { width: 100%; border-collapse: collapse; }
td { padding: 0.65rem 0.6rem; border-bottom: 1px solid var(--line); vertical-align: top; }
tr { scroll-margin-top: 3.5rem; }
.num { color: var(--muted); font-variant-numeric: tabular-nums; width: 3rem; }
.where { width: 13rem; color: var(--muted); font-size: 0.875rem; }
.section { display: block; color: var(--link); font-weight: 700; }
td[lang="en"] { width: 32%; color: var(--muted); }
td[lang="uk"] { width: 36%; }
.guessed td[lang="uk"] { background: var(--flag); }
.flag { margin: 0.4rem 0 0; font-size: 0.8125rem; font-weight: 600; }
.act a { display: inline-block; padding: 0.35rem 0.7rem; background: #0057B7; color: #FFFFFF; text-decoration: none; font-size: 0.875rem; font-weight: 600; }
.act a .en { display: block; font-weight: 400; opacity: 0.85; }
@media (max-width: 52rem) {
  table, tbody, tr, td { display: block; width: 100% !important; }
  tr { padding: 0.75rem 0; border-bottom: 2px solid var(--line); }
  td { border: 0; padding: 0.25rem 0; }
}
</style>
</head>
<body>
<header>
  <h1>Перевірка українського тексту · Checking the Ukrainian</h1>
  <p>Український текст сайту «Разом з Україною» перекладено автоматично. Тут кожен текст подано поруч з англійським оригіналом. Якщо український варіант неправильний або звучить неприродно, натисніть «Запропонувати виправлення»: GitHub відкриє форму, де текст уже вписано, — виправте його й надішліть. Потрібен безкоштовний обліковий запис GitHub.</p>
  <p lang="en">The Ukrainian on Together with Ukraine was machine-translated. Each text appears here beside its English. If the Ukrainian is wrong or unnatural, press the button: GitHub opens a form with the text already filled in; correct it and submit. A free GitHub account is needed.</p>
  <p>Текстів: __COUNT__. Імен, написання яких треба підтвердити: __GUESSED__ (виділено). · <a href="./">До сайту · Back to the site</a></p>
</header>
<nav aria-label="Розділи">__NAV__</nav>
<main>
<table>
__ROWS__
</table>
</main>
</body>
</html>
'''
