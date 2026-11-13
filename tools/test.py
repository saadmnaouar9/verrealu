import os,re,glob
from playwright.sync_api import sync_playwright
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..'))
res=[]
def ok(n,c): res.append((n,bool(c))); print(('PASS ' if c else 'FAIL ')+n)
# static link check
bad=[]
for f in glob.glob(ROOT+'/**/*.html',recursive=True):
    if '_src' in f: continue
    t=open(f,encoding='utf8').read()
    for h in re.findall(r'(?:href|src|data-lb)="([^"#?:]+)"',t):
        if h.startswith(('http','mailto','tel','//')): continue
        if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(f),h))): bad.append((os.path.relpath(f,ROOT),h))
ok('all internal hrefs/srcs resolve (%d bad)'%len(bad),not bad); print(bad[:5])
with sync_playwright() as pw:
    b=pw.chromium.launch(channel='chrome')
    c=b.new_context(viewport={'width':1440,'height':900}); p=c.new_page()
    p.goto('http://localhost:8123/corvisionplus/index.html',wait_until='networkidle')
    p.click('.tab:nth-child(2)'); ok('tab switch shows specs',p.is_visible('.spec-row'))
    p.click('.tab:nth-child(3)'); ok('essais tab',p.locator('[role=tabpanel]:visible').count()==1)
    p.locator('[data-lb]').first.click(); p.wait_for_timeout(500); ok('lightbox opens',p.locator('#lb.on').count()==1)
    p.keyboard.press('ArrowRight'); p.keyboard.press('Escape'); p.wait_for_timeout(500); ok('lightbox closes',p.locator('#lb.on').count()==0)
    p.click('.nav-links [data-open-brochures]'); p.wait_for_timeout(500); ok('brochure modal opens',p.locator('#brochures.on').count()==1)
    ok('brochure pdf links',p.locator('#brochures a[href$=".pdf"]').count()==2)
    p.keyboard.press('Escape')
    p.goto('http://localhost:8123/index.html',wait_until='networkidle'); p.wait_for_timeout(800)
    ok('hero is a playing video',p.evaluate("(()=>{const v=document.querySelector('.hero video');return v&&!v.paused&&!v.error})()"))
    p.hover('.has-sub:nth-child(3)'); p.wait_for_timeout(500); ok('desktop dropdown visible',p.locator('.has-sub:nth-child(3) .sub a').first.is_visible())
    p.click('#contact-form button[type=submit]'); ok('form blocks empty submit',p.locator('.ferr.on').count()>=1)
    p.fill('#f-nom','Test'); p.fill('#f-email','bad'); p.click('#contact-form button[type=submit]'); ok('invalid email rejected',p.locator('#f-email.invalid').count()==1)
    p.click('.exp-card >> nth=0'); p.wait_for_timeout(800); ok('service card navigates',p.url.endswith('menuiseriealuminium/index.html'))
    m=b.new_context(viewport={'width':390,'height':844}); q=m.new_page()
    q.goto('http://localhost:8123/index.html',wait_until='networkidle')
    q.click('.nav-burger'); q.wait_for_timeout(900); ok('mobile menu opens',q.locator('.mob.on').count()==1)
    q.click('.mob summary >> nth=0'); ok('mobile submenu expands',q.locator('.mob details[open] .msub a').first.is_visible())
    q.click('.mob a.m >> nth=1'); q.wait_for_timeout(800); ok('mobile nav link works','qui-sommes-nous' in q.url)
    b.close()
print(sum(1 for _,c in res if not c),'failures')
