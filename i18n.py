"""Two-language output. Every visible string is rendered once per language;
CSS shows the one matching <html data-lang>. A missing translation stops the build."""
import html, re

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
