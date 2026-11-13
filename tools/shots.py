"""Screenshot + smoke-test every page at desktop / tablet / mobile. Usage: python tools/shots.py [outdir]"""
import sys, os, glob
from playwright.sync_api import sync_playwright

OUT = sys.argv[1] if len(sys.argv) > 1 else 'shots'
os.makedirs(OUT, exist_ok=True)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
pages = ['index.html'] + sorted(os.path.relpath(p, ROOT).replace('\\', '/') for p in glob.glob(ROOT + '/*/index.html') if '/tools/' not in p.replace('\\', '/') and 'node_modules' not in p)
sizes = {'d': (1440, 900), 't': (820, 1100), 'm': (390, 844)}
only = sys.argv[2].split(',') if len(sys.argv) > 2 else list(sizes)
problems = []
with sync_playwright() as pw:
    b = pw.chromium.launch(channel='chrome')
    for tag in only:
        w, h = sizes[tag]
        ctx = b.new_context(viewport={'width': w, 'height': h})
        for pg in pages:
            page = ctx.new_page()
            errs = []
            page.on('pageerror', lambda e: errs.append(str(e)))
            page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            page.on('requestfailed', lambda r: errs.append('FAILED ' + r.url) if 'fonts.g' not in r.url else None)
            page.on('response', lambda r: errs.append(f'{r.status} {r.url}') if r.status >= 400 else None)
            page.goto('http://localhost:8123/' + pg, wait_until='networkidle')
            page.wait_for_timeout(1500)
            # force reveal + lazy images
            page.evaluate("document.querySelectorAll('.rv').forEach(e=>e.classList.add('in'));window.scrollTo(0,document.body.scrollHeight)")
            page.wait_for_timeout(700)
            page.evaluate('window.scrollTo(0,0)')
            page.wait_for_timeout(500)
            ow = page.evaluate('document.documentElement.scrollWidth - document.documentElement.clientWidth')
            if ow > 0: errs.append(f'HORIZONTAL OVERFLOW {ow}px')
            name = pg.replace('/index.html', '').replace('index.html', 'home')
            page.screenshot(path=f'{OUT}/{tag}-{name}.png', full_page=True)
            if errs: problems.append((tag, pg, errs[:6]))
            page.close()
        ctx.close()
    b.close()
for p in problems: print(p)
print('done', len(pages), 'pages;', len(problems), 'with problems')
