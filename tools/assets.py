"""Convert the images scraped from the original Wix site into optimised local assets."""
import os, glob, urllib.request
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, '_src', 'raw')
OUT = os.path.join(HERE, '..', 'assets', 'img')
os.makedirs(OUT, exist_ok=True)

for p in glob.glob(RAW + '/*'):
    f = os.path.basename(p)
    key = f[7:15] if f.startswith(('c56115_', 'cb8581_')) else f[:8]
    ext = f.rsplit('.', 1)[-1].lower()
    if ext == 'avif':  # Pillow can't read AVIF: ask Wix for a jpg rendition instead
        u = 'https://static.wixstatic.com/media/' + f.replace('_mv2', '~mv2') + '/v1/fill/w_800,h_800,q_85/x.jpg'
        data = urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})).read()
        open(f'{OUT}/{key}.jpg', 'wb').write(data)
        continue
    if ext == 'gif':
        open(f'{OUT}/{key}.gif', 'wb').write(open(p, 'rb').read())
        continue
    im = Image.open(p)
    if im.width > 2200:
        im = im.resize((2200, round(im.height * 2200 / im.width)), Image.LANCZOS)
    if ext == 'png' and im.mode in ('RGBA', 'LA', 'P'):
        im.save(f'{OUT}/{key}.png', optimize=True)
    else:
        im.convert('RGB').save(f'{OUT}/{key}.jpg', quality=84, optimize=True)
