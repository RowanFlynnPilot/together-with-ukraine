"""Two-language output. Every visible string is rendered once per language;
CSS shows the one matching <html data-lang>. A missing translation stops the build."""
import datetime, html, re

MONTHS_EN = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
MONTHS_UK = ['січня', 'лютого', 'березня', 'квітня', 'травня', 'червня', 'липня', 'серпня', 'вересня', 'жовтня', 'листопада', 'грудня']

def both(en, uk, tag='span', cls=''):
    c = f' class="{cls}"' if cls else ''
    e = html.escape
    return f'<{tag}{c} data-l="en">{e(en)}</{tag}><{tag}{c} data-l="uk" lang="uk">{e(uk)}</{tag}>'

def fill_markers(template):
    """{{English||Українська}} in the template becomes a bilingual pair of spans."""
    def sub(m):
        en, sep, uk = m.group(1).partition('||')
        if not sep or not uk.strip(): raise ValueError(f'no Ukrainian text for: {en[:50]}')
        return both(en, uk)
    return re.sub(r'\{\{(.+?)\}\}', sub, template, flags=re.S)

def dates(iso):
    """'2026-10-03' as ('October 3, 2026', '3 жовтня 2026 року')."""
    d = datetime.date.fromisoformat(iso)
    return f'{MONTHS_EN[d.month - 1]} {d.day}, {d.year}', f'{d.day} {MONTHS_UK[d.month - 1]} {d.year} року'

def plural_uk(n, one, few, many):
    """Ukrainian noun form for a count: 1 зірка, 2 зірки, 5 зірок."""
    if n % 10 == 1 and n % 100 != 11: return one
    if 2 <= n % 10 <= 4 and not 12 <= n % 100 <= 14: return few
    return many

def slug(text):
    return re.sub(r'[^a-z0-9]+', '-', text.lower().replace('’', '')).strip('-')
