"""Photos on the page: every one openly licensed or in the public domain, from Wikimedia Commons, and
credited as its license requires (rule 7 in CLAUDE.md). This module checks each photo's record, reads
its size for the layout, renders it with its credit, and gives check.py the license to look for on
its Commons page."""
import html, pathlib, struct

IMAGES = pathlib.Path(__file__).parent / 'images'
# License -> (its deed, or None for the public domain; the phrase its Commons file page shows, which check.py looks for)
LICENSES = {
    'CC BY 4.0': ('https://creativecommons.org/licenses/by/4.0/', 'Creative Commons Attribution 4.0 International'),
    'CC BY 3.0': ('https://creativecommons.org/licenses/by/3.0/', 'Creative Commons Attribution 3.0 Unported'),
    'CC BY-SA 4.0': ('https://creativecommons.org/licenses/by-sa/4.0/', 'Creative Commons Attribution-Share Alike 4.0 International'),
    'CC BY-SA 3.0': ('https://creativecommons.org/licenses/by-sa/3.0/', 'Creative Commons Attribution-Share Alike 3.0 Unported'),
    'CC BY-SA 3.0 pl': ('https://creativecommons.org/licenses/by-sa/3.0/pl/deed.en', 'Creative Commons Attribution-Share Alike 3.0 Poland'),
    'CC0': ('https://creativecommons.org/publicdomain/zero/1.0/', 'Creative Commons CC0 1.0 Universal Public Domain Dedication'),
    'Public domain': (None, 'public domain'),
}

def photo(file, alt, author, license, page):
    """A photo in images/: alt text (English, Ukrainian), the author as Commons credits them, the license, and the Commons file page."""
    return dict(file=file, alt=alt, author=author, license=license, page=page)

def image_size(path):
    """(width, height) of a JPEG or PNG, read from its header."""
    data = path.read_bytes()
    if data[:8] == b'\x89PNG\r\n\x1a\n':
        return struct.unpack('>II', data[16:24])
    if data[:2] == b'\xff\xd8':
        i = 2
        while i + 9 < len(data):
            marker, length = data[i + 1], struct.unpack('>H', data[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):  # a start-of-frame segment
                height, width = struct.unpack('>HH', data[i + 5:i + 9])
                return width, height
            i += 2 + length
    raise ValueError(f'{path}: not a JPEG or PNG the build can read')

def validate(p, where):
    """Stops the build on a photo record that is incomplete or under a license the page does not accept."""
    if p['license'] not in LICENSES: raise ValueError(f'{where}: photo license {p["license"]!r} is not one the page accepts')
    if not p['page'].startswith('https://commons.wikimedia.org/wiki/File:'): raise ValueError(f'{where}: photo needs its Commons file page')
    if not (p['author'].strip() and all(x.strip() for x in p['alt'])): raise ValueError(f'{where}: photo needs its author and alt text in both languages')
    p['size'] = image_size(IMAGES / p['file'])

def claim(p, what):
    """(url, phrase, what) for check.py: the photo's Commons page must still show its license."""
    return (p['page'], LICENSES[p['license']][1], what)

def credit(p):
    """The credit line in both languages: author, license, source."""
    e = html.escape
    deed = LICENSES[p['license']][0]
    author = f'<a href="{e(p["page"])}" target="_blank" rel="noopener">{e(p["author"])}</a>'
    license_en = f'<a href="{e(deed)}" target="_blank" rel="noopener">{e(p["license"])}</a>' if deed else 'public domain'
    license_uk = f'<a href="{e(deed)}" target="_blank" rel="noopener">{e(p["license"])}</a>' if deed else 'суспільне надбання'
    return (f'<span data-l="en">Image: {author}, {license_en}, via Wikimedia Commons</span>'
            f'<span data-l="uk" lang="uk">Зображення: {author}, {license_uk}, з Вікісховища</span>')

def img(p, loading='lazy'):
    e = html.escape; width, height = p['size']
    return (f'<img src="images/{e(p["file"])}" width="{width}" height="{height}" loading="{loading}" '
            f'alt="{e(p["alt"][0])}" data-alt-en="{e(p["alt"][0])}" data-alt-uk="{e(p["alt"][1])}">')
