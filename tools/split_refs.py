"""Split the single 'Nos References' strip (5 logos on white) into individual transparent logos."""
import os
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(HERE, '..', 'assets', 'img', 'f885adb8.jpg')
im = Image.open(src).convert('RGB')
W, H = im.size
px = im.load()
def dark(x, y): return min(px[x, y]) < 235
cols = [sum(dark(x, y) for y in range(0, H, 2)) for x in range(W)]
runs, start, gap, end = [], None, 0, 0
for x, c in enumerate(cols):
    if c > 2:
        if start is None: start = x
        gap = 0; end = x
    elif start is not None:
        gap += 1
        if gap > 70: runs.append((start, end)); start = None
if start is not None: runs.append((start, end))
print(W, H, runs)
names = ['marita', 'maroc-bureau', 'ministere', 'ventec', 'magneti-marelli']
out = os.path.join(HERE, '..', 'assets', 'img', 'refs'); os.makedirs(out, exist_ok=True)
for (s, e), n in zip(runs, names):
    ys = [y for y in range(H) if any(dark(x, y) for x in range(s, e + 1, 2))]
    box = (max(0, s - 12), max(0, min(ys) - 12), min(W, e + 13), min(H, max(ys) + 13))
    c = im.crop(box).convert('RGBA')
    # white -> transparent (soft) so logos sit on any card colour
    d = c.load()
    for y in range(c.height):
        for x in range(c.width):
            r, g, b, _ = d[x, y]; m = min(r, g, b)
            d[x, y] = (r, g, b, 0 if m > 245 else (255 if m < 215 else int((245 - m) / 30 * 255)))
    h = 220
    c = c.resize((round(c.width * h / c.height), h), Image.LANCZOS)
    c.save(os.path.join(out, n + '.png'), optimize=True); print(n, c.size)
