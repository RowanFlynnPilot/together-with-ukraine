"""Make images/share.jpg, the 1200 x 630 picture a link preview shows: the header photo under the
page's blue wash, the flag, the title in both languages, the six sections, and the photo's credit,
which its CC BY-SA 4.0 license requires wherever the picture travels.

Run it when the tabs change, then update og:image:alt in template.html to match. It needs Pillow
(python -m pip install pillow) and the Segoe UI fonts that come with Windows. The build only copies
the picture it makes."""
import pathlib

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).parent
W, H = 1200, 630
BOLD, REGULAR = 'C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/segoeui.ttf'
SECTIONS = ('Culture · History · People · In the US · Places to eat and shop · Ways to help',
            'Культура · Історія · Люди · У США · Заклади · Допомогти')
CREDIT = 'Photo: KyivMax, CC BY-SA 4.0, via Wikimedia Commons'

photo = Image.open(ROOT / 'images' / 'hero-lavra.jpg').convert('RGB')
scale = max(W / photo.width, H / photo.height)
photo = photo.resize((round(photo.width * scale), round(photo.height * scale)), Image.LANCZOS)
top = round((photo.height - H) * 0.35)  # the page frames it at 35% from the top too
photo = photo.crop(((photo.width - W) // 2, top, (photo.width - W) // 2 + W, top + H))

# The same wash as the page header: deepest on the left, behind the text.
wash = Image.new('RGBA', (W, H))
px = wash.load()
for x in range(W):
    t = x / (W - 1)
    if t < 0.45:
        a = 0.94 + (0.84 - 0.94) * t / 0.45; rgb = (0, round(60 + 12 * t / 0.45), round(135 + 21 * t / 0.45))
    else:
        u = (t - 0.45) / 0.55; a = 0.84 + (0.5 - 0.84) * u; rgb = (0, round(72 + 15 * u), round(156 + 27 * u))
    for y in range(H):
        px[x, y] = (*rgb, round(255 * a))
image = Image.alpha_composite(photo.convert('RGBA'), wash).convert('RGB')
draw = ImageDraw.Draw(image)

# The flag, top left, with a white edge as on the page.
draw.rectangle((70, 62, 166, 126), fill='#FFFFFF')
draw.rectangle((73, 65, 163, 94), fill='#0057B7')
draw.rectangle((73, 94, 163, 123), fill='#FFD700')

draw.text((66, 176), 'Разом з Україною', font=ImageFont.truetype(BOLD, 104), fill='#FFFFFF')
draw.text((70, 316), 'Together with Ukraine', font=ImageFont.truetype(REGULAR, 50), fill='#FFFFFF')
for (text, font_file, color), y in zip(((SECTIONS[0], BOLD, '#FFD700'), (SECTIONS[1], REGULAR, '#FFFFFF')), (404, 446)):
    font = ImageFont.truetype(font_file, 28)
    if 72 + draw.textlength(text, font=font) > W - 72: raise ValueError(f'the sections no longer fit on one line: {text}')
    draw.text((72, y), text, font=font, fill=color)

# The flag's yellow along the bottom, and the photo's credit.
draw.rectangle((0, H - 14, W, H), fill='#FFD700')
font = ImageFont.truetype(REGULAR, 18)
draw.text((W - 28 - draw.textlength(CREDIT, font=font), H - 46), CREDIT, font=font, fill='#FFFFFF')

image.save(ROOT / 'images' / 'share.jpg', 'JPEG', quality=85, optimize=True, progressive=True)
print(f'wrote images/share.jpg ({W} x {H})')
