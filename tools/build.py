"""Static site generator for the Verre Alum Partner redesign.

Text content is read from the scraped copies of the original pages (tools/_src/txt_*.txt)
so nothing is retyped. Run:  python tools/build.py
"""
import os, re, json, html, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
SRC = os.path.join(HERE, '_src')
E = html.escape

# --------------------------------------------------------------------------- content helpers
def norm(s): return ' '.join(s.replace('​', ' ').split())

def lines(orig):
    """Content lines of an original page, cut before the site navigation."""
    p = os.path.join(SRC, f'txt_{orig}.txt')
    L = [norm(l) for l in open(p, encoding='utf8').read().split('\n')]
    L = [l for l in L if l]
    if L and L[0] == 'top of page': L = L[1:]
    for i, l in enumerate(L):
        if l == 'Accueil':
            L = L[:i]; break
    return L

def pick(L, prefix, default=''):
    for l in L:
        if l.startswith(prefix): return l
    if default == '': raise KeyError(prefix)
    return default

def img(key, ext=None):
    for e in ([ext] if ext else ['jpg', 'png', 'gif']):
        if os.path.exists(os.path.join(ROOT, 'assets', 'img', f'{key}.{e}')): return f'assets/img/{key}.{e}'
    raise FileNotFoundError(key)

# --------------------------------------------------------------------------- site data
PHONE = '00 212 662 16 16 17'
PHONE_TEL = '+212662161617'
MAIL = 'contact@verrealu.ma'
ADDR = ['Res. Le Jardin Abdelmoumen G12', 'Bureau 4 - 20340 Casablanca', '- Maroc']
SOCIAL = [
    ('Instagram', 'https://instagram.com/verrealu.ma?igshid=OGQ5ZDc2ODk2ZA==',
     'M7 2h10a5 5 0 015 5v10a5 5 0 01-5 5H7a5 5 0 01-5-5V7a5 5 0 015-5zm0 2a3 3 0 00-3 3v10a3 3 0 003 3h10a3 3 0 003-3V7a3 3 0 00-3-3H7zm5 3.5a4.5 4.5 0 110 9 4.5 4.5 0 010-9zm0 2a2.5 2.5 0 100 5 2.5 2.5 0 000-5zM17.5 6a1 1 0 110 2 1 1 0 010-2z'),
    ('Facebook', 'https://www.facebook.com/verrealucasa',
     'M13.5 22v-8h2.7l.5-3.3h-3.2V8.6c0-.9.4-1.7 1.8-1.7h1.5V4.1S15.1 3.9 14 3.9c-2.6 0-4.2 1.6-4.2 4.3v2.5H7v3.3h2.8v8h3.7z'),
    ('LinkedIn', 'https://www.linkedin.com/company/verre-alum/',
     'M4.98 3.5a2.5 2.5 0 110 5 2.5 2.5 0 010-5zM3 9.75h4V21H3zM9.75 9.75h3.8v1.6h.05c.55-1 1.9-1.95 3.8-1.95 4 0 4.7 2.6 4.7 6V21h-4v-5c0-1.2 0-2.7-1.7-2.7s-1.9 1.3-1.9 2.6V21h-4z'),
]
DOCS = [('Cortizo Aluminium.pdf', 'assets/docs/cortizo-aluminium.pdf'), ('Cortizo Facade.pdf', 'assets/docs/cortizo-facade.pdf')]
GROUP_URL = 'http://www.c3amaroc.com'

# (slug, nav label, original source key, short category)
PRODUCTS = [
    ('corvisionplus', 'CorVisionPlus', 'corvisionplus'),
]
SERVICES = [
    # slug, nav label, card title, image key, tag
    ('menuiseriealuminium', 'Menuiserie Aluminium', 'MENUISERIE ALUMINIUM', 'ca3c68cf', 'Sur mesure'),
    ('cloisons-amovibles-abcd', 'Cloisons amovibles', 'CLOISONS AMOVIBLES', '36fcfba2', 'Bureaux'),
    ('mursrideaux', 'Murs Rideaux', 'MUR RIDEAUX & HABILLAGE DES FACADES', '37f2dad8', 'Façades'),
    (None, None, 'GARDE CORPS VITRES', '8d32795c', 'Sur demande'),
    ('pergolasbioclimatiques', 'Pergolas & Verandas', 'PERGOLAS BIOCLIMATIQUES & VERANDAS', 'dec6f397', 'Outdoor'),
    ('paroisetcabinesdouches', 'Parois de douches', 'PAROIS DE DOUCHES', 'b22db060', 'Verre trempé'),
    (None, None, 'GARDE CORPS', '71efb4bf', 'Sur demande'),
]
SERVICE_NAV = [s for s in SERVICES if s[0]]

IMG_INFO = json.load(open(os.path.join(SRC, 'imgs.json'), encoding='utf8'))
COMMON = {'2647386e', '8ae91ced', 'fdcfaba1', 'ce6ec7c1', '8efda639'}

def page_images(orig_html):
    out = []
    for i in IMG_INFO.get(orig_html, []):
        k = i[7:15] if i.startswith(('c56115_', 'cb8581_')) else i[:8]
        if k not in COMMON and k not in out: out.append(k)
    return out

def size_of(key):
    from PIL import Image
    return Image.open(os.path.join(ROOT, img(key))).size

# --------------------------------------------------------------------------- layout pieces
def rel(depth): return '../' * depth

def nav_html(p, current):
    def a(href, label, cls='nl'):
        on = ' on' if current == href else ''
        return f'<a class="{cls}{on}" href="{p}{href}">{E(label)}</a>'
    prod = ''.join(f'<a href="{p}{s}/index.html">{E(l)}</a>' for s, l, _ in PRODUCTS)
    serv = ''.join(f'<a href="{p}{s}/index.html">{E(l)}</a>' for s, l, *_ in SERVICE_NAV)
    return f'''<header class="nav" data-over>
  <a class="nav-logo" href="{p}index.html" aria-label="Verre Alum Partner — Accueil"><img class="lg-w" src="{p}assets/img/logo-white.png" alt="Verre Alum Partner" width="900" height="244"><img class="lg-c" src="{p}assets/img/logo-color.png" alt="" aria-hidden="true" width="900" height="244"></a>
  <ul class="nav-links">
    <li>{a('index.html', 'Accueil')}</li>
    <li>{a('qui-sommes-nous/index.html', 'Qui sommes-nous ?')}</li>
    <li class="has-sub">{a('cortizoaluminiummaroc/index.html', 'Cortizo Aluminium Maroc')}<div class="sub">{prod}</div></li>
    <li class="has-sub">{a('vapamenagement/index.html', 'C3A Maroc')}<div class="sub"><a href="{p}vapamenagement/index.html">C3A Maroc</a><a href="{p}albertgeanucasablancamaroc/index.html">Albert Genau</a><hr><a href="{GROUP_URL}" target="_blank" rel="noopener">Groupe C3A — c3amaroc.com ↗</a></div></li>
    <li class="has-sub"><button class="nl" type="button" aria-haspopup="true">Nos services</button><div class="sub"><div class="sub-h">Nos services</div>{serv}</div></li>
    <li><a class="nl" href="#brochures" data-open-brochures>Nos brochures</a></li>
  </ul>
  <a class="nav-cta" href="#contact">Contactez-nous</a>
  <button class="nav-burger" type="button" aria-label="Menu" aria-expanded="false"><span></span><span></span></button>
</header>
<nav class="mob" aria-label="Menu mobile">
  <ul>
    <li><a class="m" href="{p}index.html">Accueil</a></li>
    <li><a class="m" href="{p}qui-sommes-nous/index.html">Qui sommes-nous ?</a></li>
    <li><details><summary>Cortizo Aluminium Maroc</summary><div class="msub"><a href="{p}cortizoaluminiummaroc/index.html">Cortizo Aluminium Maroc</a>{prod.replace('<a href="', '<a href="')}</div></details></li>
    <li><details><summary>C3A Maroc</summary><div class="msub"><a href="{p}vapamenagement/index.html">C3A Maroc</a><a href="{p}albertgeanucasablancamaroc/index.html">Albert Genau</a><a href="{GROUP_URL}" target="_blank" rel="noopener">c3amaroc.com ↗</a></div></details></li>
    <li><details><summary>Nos services</summary><div class="msub">{serv}</div></details></li>
    <li><a class="m" href="#brochures" data-open-brochures>Nos brochures</a></li>
    <li><a class="m" href="#contact">Contactez-nous</a></li>
  </ul>
  <div class="mob-foot">{PHONE}<br><a href="mailto:{MAIL}">{MAIL}</a></div>
</nav>'''

def social_html():
    return '<div class="social">' + ''.join(
        f'<a href="{u}" target="_blank" rel="noopener" aria-label="{n}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="{d}"/></svg></a>' for n, u, d in SOCIAL) + '</div>'

def contact_html():
    maps = 'https://www.google.com/maps/search/?api=1&query=' + 'Res.+Le+Jardin+Abdelmoumen+G12+Bureau+4+20340+Casablanca+Maroc'
    return f'''<section class="sec" id="contact" aria-labelledby="ct-h">
  <div class="contact-g">
    <div class="rv">
      <div class="sl">Contact</div>
      <h2 class="h2" id="ct-h">Contactez-<em>nous</em></h2>
      <dl class="ct-info">
        <div><dt>Groupe C3A MAROC</dt><dd><a href="{GROUP_URL}" target="_blank" rel="noopener">www.c3amaroc.com</a></dd></div>
        <div><dt>Adresse</dt><dd>{'<br>'.join(E(x) for x in ADDR)}</dd></div>
        <div><dt>E-mail</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd></div>
        <div><dt>Tel</dt><dd><a href="tel:{PHONE_TEL}">{PHONE}</a></dd></div>
        <div><dt>Suivez-nous</dt><dd>{social_html()}</dd></div>
      </dl>
      <p class="map-link"><a class="link-arrow" href="{maps}" target="_blank" rel="noopener">Ouvrir dans Google Maps</a></p>
    </div>
    <form class="form rv" id="contact-form" novalidate style="--d:120ms">
      <div class="field"><label for="f-nom">Nom *</label><input id="f-nom" name="nom" type="text" required maxlength="100" autocomplete="name"><span class="ferr">Champ requis</span></div>
      <div class="field"><label for="f-email">Email *</label><input id="f-email" name="email" type="email" required maxlength="250" autocomplete="email"><span class="ferr">Format email invalide</span></div>
      <div class="field"><label for="f-phone">Telephone</label><input id="f-phone" name="phone" type="tel" maxlength="50" autocomplete="tel"></div>
      <div class="field"><label for="f-sujet">Sujet</label><input id="f-sujet" name="sujet" type="text"></div>
      <div class="field"><label for="f-msg">Message</label><textarea id="f-msg" name="message"></textarea></div>
      <div class="form-status" role="status" aria-live="polite"></div>
      <div><button class="btn btn-liquid" type="submit"><span>Envoyer</span></button></div>
    </form>
  </div>
</section>'''

def footer_html(p):
    prod = ''.join(f'<li><a href="{p}{s}/index.html">{E(l)}</a></li>' for s, l, _ in PRODUCTS)
    serv = ''.join(f'<li><a href="{p}{s}/index.html">{E(l)}</a></li>' for s, l, *_ in SERVICE_NAV)
    return f'''<footer class="foot">
  <div class="foot-g">
    <div class="foot-brand"><img class="foot-logo" src="{p}assets/img/logo-white.png" alt="Verre Alum Partner" width="900" height="244" loading="lazy">
      <p>Conception, fabrication et installation de menuiseries en aluminium pour les bâtiments commerciaux et résidentiels. Représentant des marques Cortizo aluminium et Albert Genau Maroc.</p>
    </div>
    <div><h5>Accueil</h5><ul><li><a href="{p}index.html">Accueil</a></li><li><a href="{p}qui-sommes-nous/index.html">Qui sommes-nous ?</a></li><li><a href="{p}albertgeanucasablancamaroc/index.html">C3A MAROC</a></li><li><a href="{p}vapamenagement/index.html">C3A Maroc</a></li><li><a href="#brochures" data-open-brochures>Nos brochures</a></li></ul>
      <h5 style="margin-top:28px">Nos services</h5><ul>{serv}</ul></div>
    <div><h5>Cortizo Aluminium Maroc</h5><ul><li><a href="{p}cortizoaluminiummaroc/index.html">Cortizo Aluminium Maroc</a></li>{prod}</ul></div>
    <div><h5>Groupe C3A MAROC</h5>
      <address>{'<br>'.join(E(x) for x in ADDR)}<br><br>E-mail: <a href="mailto:{MAIL}">{MAIL}</a><br>Tel: <a href="tel:{PHONE_TEL}">{PHONE}</a></address>
      <div style="margin-top:22px">{social_html()}</div></div>
  </div>
  <div class="foot-bot"><span>© Verre Alum Partner — Casablanca, Maroc</span><span>Menuiserie aluminium · Cortizo · Albert Genau</span></div>
</footer>'''

def modals_html(p):
    docs = ''.join(f'<a class="doc" href="{p}{u}" target="_blank" rel="noopener"><em>PDF</em><span>{E(n)}</span><i>↓</i></a>' for n, u in DOCS)
    return f'''<div class="modal" id="brochures" role="dialog" aria-modal="true" aria-labelledby="br-h">
  <div class="modal-box"><button class="x-btn" type="button" aria-label="Fermer">✕</button>
    <div class="sl" style="color:rgba(242,241,238,.55)">Brochures</div><h3 id="br-h">Télécharger brochures</h3>
    <p class="sub2">Documents disponibles</p><div class="docs">{docs}</div></div>
</div>
<div class="lb" id="lb" role="dialog" aria-modal="true" aria-label="Galerie">
  <div class="lb-in"><button class="x-btn lb-close" type="button" aria-label="Fermer">✕</button>
    <img class="lb-img" alt="">
    <div class="lb-bar"><span class="lb-cap"></span><div class="lb-nav"><button class="lb-btn lb-prev" type="button" aria-label="Précédent">←</button><span class="lb-count"></span><button class="lb-btn lb-next" type="button" aria-label="Suivant">→</button></div></div>
  </div>
</div>'''

def head_html(title, desc, p, image=None):
    return f'''<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:type" content="website">
<link rel="icon" type="image/png" href="{p}{img('c424f6bd')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@200;300;400;500;600;700&family=Playfair+Display:ital,wght@0,400;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p}assets/css/style.css">
</head>'''

def page(path, title, desc, hero, main, current='', depth=1, extra_before_contact=''):
    p = rel(depth)
    out = f'''{head_html(title, desc, p)}
<body>
<a class="skip" href="#main">Aller au contenu</a>
{nav_html(p, current)}
{hero}
<main id="main">
{main}
{extra_before_contact}
</main>
{contact_html()}
{footer_html(p)}
{modals_html(p)}
<script src="{p}assets/js/main.js" defer></script>
</body>
</html>'''
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf8', newline='\n').write(out)

def phero(p, crumbs, h1, sub='', bg=None, tag=''):
    cr = ''.join(f'<span>/</span><a href="{p}{u}">{E(t)}</a>' if i else f'<a href="{p}{u}">{E(t)}</a>' for i, (t, u) in enumerate(crumbs))
    style = f' style="background-image:url({p}{bg})"' if bg else ''
    cls = 'phero' if bg else 'phero plain'
    return f'''<section class="{cls}"{style}><div class="phero-in">
  <div class="crumb">{cr}</div>{f'<span class="tag">{E(tag)}</span>' if tag else ''}
  <h1>{h1}</h1>{f'<p>{E(sub)}</p>' if sub else ''}</div></section>'''

def cta_band(p, text='Un projet ? <em>Parlons-en.</em>'):
    return f'''<section class="cta-band"><h3 class="rv">{text}</h3>
  <div class="rv" style="display:flex;gap:14px;flex-wrap:wrap"><a class="btn btn-primary" href="#contact">Contactez-nous</a><a class="btn btn-ghost" href="#brochures" data-open-brochures>Nos brochures</a></div></section>'''

def gal_btn(p, key, alt, cls=''):
    return f'<button class="g {cls}" type="button" data-lb="{p}{img(key)}"><img src="{p}{img(key)}" alt="{E(alt)}" loading="lazy"><span class="zoom">+</span></button>'

# --------------------------------------------------------------------------- HOME
def build_home():
    p = ''
    slides = [
        ('MENUISERIE ALUMINIUM', 'ca3c68cf')]  # hero = video only (poster shown until it loads)
    sl = ''.join(
        (f'<div class="hslide has-video" data-cap="{E(c)}" style="background-image:url({img(k)})"><video muted loop autoplay playsinline preload="auto" poster="{img(k)}" aria-hidden="true"><source src="assets/video/hero.mp4" type="video/mp4"></video></div>' if n == 0
         else f'<div class="hslide" data-cap="{E(c)}" style="background-image:url({img(k)})"></div>')
        for n, (c, k) in enumerate(slides))
    dots = ''.join(f'<button class="hdot" type="button" aria-label="{E(c)}"></button>' for c, _ in slides)
    hero = f'''<section class="hero" aria-label="Accueil">
  <div class="hero-bg">{sl}</div><div class="hero-ov"></div>
  <div class="hc tl">Casablanca · Maroc</div><div class="hc tr">Cortizo · Albert Genau · C3A</div>
  <div class="hero-cnt">
    <div class="hero-ey">Verre Alum Partner</div>
    <h1 class="ht"><span class="sv"><span class="hw-mask"><span class="hw" style="--d:150ms">Tous</span></span> <span class="hw-mask"><span class="hw" style="--d:230ms">type</span></span> <span class="hw-mask"><span class="hw" style="--d:310ms">de</span></span></span><span class="linv"><span class="hw-mask"><span class="hw" style="--d:420ms">MENUISERIE</span></span> <span class="hw-mask"><span class="hw" style="--d:520ms">ALUMINIUM</span></span></span></h1>
    <div class="hero-rule"></div>
    <p class="hero-sub">L’installation de vos menuiseries Aluminium est prise en charge par votre professionnel Verre Alum Partner proche de chez vous.</p>
    <div class="hero-ctas"><a class="btn btn-inv" href="#services">Tous nos services</a><a class="btn btn-ghost" href="#contact">Contactez-nous</a></div>
  </div>
  <div class="hero-scroll"><span>Scroll</span><div class="sline"></div></div>
</section>'''
    A = lines('qui-sommes-nous')
    paras = [l for l in A[1:] ]
    marq = ['Menuiserie aluminium', 'Cloisons amovibles', 'Murs rideaux', 'Garde-corps', 'Pergolas bioclimatiques', 'Vérandas', 'Parois de douches', 'Cortizo', 'Albert Genau', 'Schüco']
    mq = ''.join(f'<span class="mi">{E(m)}</span><span class="mi mdot">·</span>' for m in marq)
    cards = ''
    descs = {
        'menuiseriealuminium': 'Sur-mesure et haut de gamme, nos créations sont fabriquées dans notre atelier en région Casablancaise.',
        'cloisons-amovibles-abcd': 'Leader l’aménagement des espaces de travail.',
        'mursrideaux': 'Des solutions de façade modernes, légères et performantes.',
        'pergolasbioclimatiques': 'La pergola bioclimatique est la nouvelle tendance extérieure.',
        'paroisetcabinesdouches': 'Confiez-nous vos projets de pare douche en verre.',
        None: 'Contactez-nous pour votre projet.',
    }
    for i, (slug, _, title, k, tag) in enumerate(SERVICES, 1):
        href = f'{slug}/index.html' if slug else '#contact'
        cards += f'''<a class="exp-card rv" style="--d:{(i % 3) * 90}ms" href="{href}"><div class="bgi" style="background-image:url({img(k)})"></div>
  <div><div class="exp-num">{i:02d}</div><h3 class="exp-name">{E(title)}</h3><p class="exp-desc">{E(descs[slug])}</p></div>
  <div class="exp-bot"><span class="exp-tag">{E(tag)}</span><span class="exp-arr">→</span></div></a>'''
    alb = lines('albertgeanucasablancamaroc')
    cort = lines('cortizoaluminiummaroc')
    part = f'''<section class="sec" aria-labelledby="pt-h"><div class="exp-hdr"><div class="rv"><div class="sl">Nos marques</div><h2 class="h2" id="pt-h">Des marques <em>de référence</em></h2></div>
  <p class="exp-hdr-r rv">Représentant des marques Cortizo aluminium et Albert Genau Maroc.</p></div>
  <div class="part-g">
   <a class="part rv" href="cortizoaluminiummaroc/index.html"><div class="logo"><img src="{img('ad15ca33')}" alt="Cortizo" loading="lazy"></div><h3>Cortizo Aluminium Maroc</h3><p>{E(pick(cort, 'Des systèmes à hautes'))}</p><span class="link-arrow">Découvrir</span></a>
   <a class="part rv" style="--d:90ms" href="albertgeanucasablancamaroc/index.html"><div class="logo"><img src="{img('8ae91ced')}" alt="C3A Maroc" loading="lazy"></div><h3>C3A Maroc — Albert Genau</h3><p>{E(pick(alb, 'Les systèmes Albert Genau'))}</p><span class="link-arrow">Découvrir</span></a>
   <a class="part rv" style="--d:180ms" href="menuiseriealuminium/index.html"><div class="logo"><img src="{img('a58f45ae')}" alt="Schüco" loading="lazy"></div><h3>Schüco · Sepalumic · Aluminium du Maroc</h3><p>Verre alum Partner collabore en partenariat avec trois grandes marques : Schuco, Sepalumic et Aluminium du Maroc.</p><span class="link-arrow">Découvrir</span></a>
  </div></section>'''
    stats = '''<div class="stats">
  <div class="st rv"><div class="st-val" data-count="15" data-suffix="+">15+</div><div class="st-lbl">Ans d’expérience</div></div>
  <div class="st rv" style="--d:80ms"><div class="st-val" data-count="37">37</div><div class="st-lbl">Ans d’expertise Albert Genau</div></div>
  <div class="st rv" style="--d:160ms"><div class="st-val" data-count="52">52</div><div class="st-lbl">Pays — réseau Albert Genau</div></div>
  <div class="st rv" style="--d:240ms"><div class="st-val" data-count="185">185</div><div class="st-lbl">km/h — résistance au vent des pergolas</div></div></div>'''
    refs = [('marita', 'Marita Group'), ('maroc-bureau', 'Maroc Bureau'), ('ministere', 'Royaume du Maroc — Ministère des Affaires Étrangères, de la Coopération Africaine et des Marocains Résidant à l’Étranger'), ('ventec', 'Ventec'), ('magneti-marelli', 'Magneti Marelli')]
    refs_count = len(refs)
    def ref_set(hidden):
        return ''.join(f'<div class="ref" {"aria-hidden=true" if hidden else "role=listitem"}><img src="assets/img/refs/{k}.png" alt="{"" if hidden else E(n)}" loading="lazy"></div>' for k, n in refs)
    refs_track = '<div class="refs-track">' + ref_set(False) + ref_set(True) + ref_set(True) + ref_set(True) + '</div>'
    docs = ''.join(f'<a class="doc" href="{u}" target="_blank" rel="noopener"><em>PDF</em><span>{E(n)}</span><i>↓</i></a>' for n, u in DOCS)
    main = f'''
<div class="marquee" aria-hidden="true"><div class="mtrack">{mq}{mq}</div></div>
<section class="sec" aria-labelledby="ab-h"><div class="about-g">
  <div class="rv"><div class="sl">Qui sommes-nous ?</div><h2 class="h2" id="ab-h">Verre Alum Partner, <em>menuiserie aluminium haut de gamme</em></h2>
    <div class="about-ctas"><a class="btn btn-primary" href="qui-sommes-nous/index.html">Qui sommes-nous ?</a><a class="btn btn-ghost" href="#contact">Devis gratuit</a></div></div>
  <div class="body rv" style="--d:100ms">{''.join(f'<p>{E(x)}</p>' for x in paras[:2])}</div></div></section>
<section class="sec" id="services" style="padding-top:0" aria-labelledby="sv-h"><div class="exp-hdr"><div class="rv"><div class="sl">Nos services</div><h2 class="h2" id="sv-h">TOUS NOS <em>services</em></h2></div>
  <p class="exp-hdr-r rv">Tous type de menuiserie aluminium — du sur-mesure résidentiel aux façades tertiaires.</p></div>
  <div class="exp-grid">{cards}</div></section>
{part}
{stats}
<section class="sec refs" aria-labelledby="rf-h"><div class="exp-hdr"><div class="rv"><div class="sl">Références</div><h2 class="h2" id="rf-h">Nos <em>References</em></h2></div>
  <p class="exp-hdr-r rv">{refs_count} références qui nous font confiance.</p></div>
  <div class="refs-band rv" role="list" aria-label="Nos références">{refs_track}</div></section>
<section class="sec dark"><div class="pro-g">
  <div class="rv"><div class="sl">Documentation</div><h2 class="h2">Télécharger <em>brochures</em></h2><p class="lead" style="margin-top:20px">Retrouvez les brochures Cortizo : aluminium et façades.</p></div>
  <div class="docs rv" style="--d:100ms">{docs}</div></div></section>'''
    page('index.html', 'Verre alum Partner | Menuiserie aluminium',
         "Verre Alum partner est une entreprise spécialisée dans la conception, la fabrication et l'installation de menuiseries en aluminium pour les bâtiments commerciaux et résidentiels. (Representant des marques Cortizo aluminium et Albert Genau Maroc)",
         hero, main, current='index.html', depth=0)

# --------------------------------------------------------------------------- ABOUT
def build_about():
    p = '../'
    L = lines('qui-sommes-nous')
    rest = ''.join(f'<div class="ab-row rv" style="--d:{i*60}ms"><span class="ab-n">0{i}</span><p>{E(x)}</p></div>' for i, x in enumerate(L[2:], 1))
    hero = phero(p, [('Accueil', 'index.html'), ('Qui sommes-nous ?', 'qui-sommes-nous/index.html')], 'Qui <em>sommes-nous</em> ?',
                 bg=img('daa8147c'))
    main = f'''<section class="sec"><div class="ab2"><aside class="ab-side rv"><div class="sl">Verre Alum Partner</div><h2 class="h2">Menuiserie aluminium <em>haut de gamme</em></h2>
  <div class="ab-ph"><img src="../{img('daa8147c')}" alt="Verre Alum Partner" loading="lazy"></div>
  <a class="btn btn-primary" href="#contact">Devis personnalisé gratuit</a></aside>
  <div class="ab-main"><p class="ab-lead rv">{E(L[1])}</p>{rest}</div></div></section>'''
    page('qui-sommes-nous/index.html', 'Qui sommes-nous ? | Verre alum Partner', L[1], hero, main + cta_band(p), 'qui-sommes-nous/index.html')

# --------------------------------------------------------------------------- PRODUCT PAGES
def kv_groups(L):
    """Group '» Label' lines with their value lines -> [(label, [values])]"""
    out = []
    for l in L:
        if l.startswith('»'):
            out.append([l.lstrip('» ').strip(), []])
        elif out:
            out[-1][1].append(l)
        else:
            out.append(['', [l]])
    return out

def spec_html(groups):
    rows = ''
    for k, v in groups:
        vals = ''.join(f'<span>{E(x)}</span>' for x in v)
        rows += f'<div class="spec-row"><dt>{E(k.rstrip(":"))}</dt><dd>{vals}</dd></div>'
    return f'<dl class="spec">{rows}</dl>'

def build_product(slug, label, src):
    p = '../'
    L = lines(src)
    i = L.index('La description')
    title, cat = L[i - 2], L[i - 1]
    body = L[i + 3:]
    # split: description / technical data / tests
    t_i = next(j for j, l in enumerate(body) if l.startswith('» Prise de vitrage'))
    e_i = next((j for j, l in enumerate(body) if l.startswith('» Perméabilité')), len(body))
    desc, tech, ess = body[:t_i], body[t_i:e_i], body[e_i:]
    dh = ''
    for l in desc:
        dh += f'<p class="pt">{E(l.lstrip("» ").strip())}</p>' if l.startswith('»') else f'<p>{E(l)}</p>'
    # tech groups: separate trailing note lines ("Consultez ...", "Essai de référence ...") kept inside value lists
    th = spec_html(kv_groups(tech))
    eh = spec_html(kv_groups(ess)) if ess else '<p class="note">Voir données techniques.</p>'
    keys = page_images(src + '.html') if src + '.html' in IMG_INFO else page_images(src.replace('é', 'e') + '.html')
    photos, tech_imgs = [], []
    for k in keys:
        w = size_of(k)[0]
        (tech_imgs if (w <= 370 or k in ('81bf3570', '0da0a1c4')) else photos).append(k)
    hero_bg = next((k for k in photos if size_of(k)[0] >= 1000 and size_of(k)[0] / size_of(k)[1] > 1.3), None)
    g = ''
    if photos:
        g += '<div class="gal-title">Réalisations</div><div class="gal">' + ''.join(gal_btn(p, k, f'{title} — {n}', 'big' if n == 1 else '') for n, k in enumerate(photos, 1)) + '</div>'
    if tech_imgs:
        thumbs = ''.join(f'<button class="th{" on" if n == 1 else ""}" type="button" data-src="{p}{img(k)}" aria-label="Profilé {n}"><img src="{p}{img(k)}" alt="" loading="lazy"><i>0{n}</i></button>' for n, k in enumerate(tech_imgs, 1))
        g += f'<div class="gal-title">Profilés &amp; schémas</div><div class="spot" data-spot><button class="spot-main" type="button" data-lb="{p}{img(tech_imgs[0])}"><img src="{p}{img(tech_imgs[0])}" alt="{E(title)} — profilé"><span class="zoom">+ Agrandir</span></button><div class="spot-th">{thumbs}</div></div>'
    # prev / next
    idx = [s for s, _, _ in PRODUCTS].index(slug)
    pv, nx = PRODUCTS[idx - 1], PRODUCTS[(idx + 1) % len(PRODUCTS)]
    pn_nav = '' if len(PRODUCTS) < 2 else f'<nav class="pn" aria-label="Produits"><a href="../{pv[0]}/index.html"><small>← Précédent</small><b>{E(pv[1])}</b></a><a href="../{nx[0]}/index.html"><small>Suivant →</small><b>{E(nx[1])}</b></a></nav>'
    hero = phero(p, [('Accueil', 'index.html'), ('Cortizo Aluminium Maroc', 'cortizoaluminiummaroc/index.html'), (label, f'{slug}/index.html')],
                 E(title), bg='assets/img/hero-corvision.jpg', tag=cat)
    main = f'''<section class="sec"><div class="pg-g">
  <div data-tabs class="rv"><div class="tabs" role="tablist"><button class="tab" role="tab" type="button">La description</button><button class="tab" role="tab" type="button">Données téchniques</button><button class="tab" role="tab" type="button">Essais</button></div>
    <div class="panel desc" role="tabpanel">{dh}</div><div class="panel" role="tabpanel" hidden>{th}</div><div class="panel" role="tabpanel" hidden>{eh}</div></div>
  <div class="sticky rv" style="--d:100ms">{g}</div></div></section>
{pn_nav}'''
    page(f'{slug}/index.html', f'{title} | Cortizo Aluminium Maroc | Verre alum Partner', f'{title} — {cat}. ' + (desc[0].lstrip('» ')[:150] if desc else ''),
         hero, main + cta_band(p), f'{slug}/index.html')

# --------------------------------------------------------------------------- CORTIZO
def nice(t):
    if not t.isupper(): return t
    t = t[0] + t[1:].lower()
    return t.replace('cortizo', 'Cortizo')

def build_cortizo():
    p = '../'
    L = lines('cortizoaluminiummaroc')
    why_h = pick(L, 'Pourquoi choisir'); why_p = pick(L, 'Des systèmes à hautes')
    blocks = [('GAMME DE COULEURS ILLIMITÉES', 'GAMME', '809ef0a8'), ('CORTIZO ECOEFFICIENT', 'CORTIZO ECO', '491a1a01'),
              ("STYLE D'AVANT-GARDE", 'STYLE', 'd2e14e8e'), ('QUALITÉ', 'QUALITÉ', 'a743b24a')]
    bl = ''
    for t, _, ic in blocks:
        j = L.index(t)
        bl += f'<div class="rv"><img src="../{img(ic)}" alt="" width="40" height="40" style="width:40px;height:auto;margin-bottom:20px;mix-blend-mode:multiply;opacity:.8"><h4>{E(nice(t))}</h4><p>{E(L[j + 1])}</p></div>'
    # the why-paragraph continues in the original after 'et dans des laboratoires...' ; join continuation lines
    why = why_p
    j = L.index(why_p)
    k = j + 1
    while k < len(L) and L[k] not in [b[0] for b in blocks]:
        why += ' ' + L[k]; k += 1
    def grp(cat_match):
        out = ''
        for s, l, src in PRODUCTS:
            LL = lines(src); i = LL.index('La description')
            if LL[i - 1] in cat_match:
                k = [x for x in page_images(src + '.html')]
                ph = next((x for x in k if size_of(x)[0] > 370 and x not in ('81bf3570', '0da0a1c4')), None)
                th = next((x for x in k if size_of(x)[0] <= 370), None)
                im = img(ph or th) if (ph or th) else ''
                cls = '' if th and not ph else ' ph'
                im_src = img(th) if th else img(ph)
                out += f'<a class="pcard rv" href="../{s}/index.html"><div class="im"><img src="../{im_src}" alt="{E(l)}" loading="lazy"></div><div class="tx"><div><small>{E(LL[i-1])}</small><h3>{E(l)}</h3></div><span class="arr">→</span></div></a>'
        return out
    cats = [(L[0], ['Baies Coulissantes'], '492e5256'), (L[1], ['Portes-Fenêtres et Portes Battantes', 'Portes'], '330647c1')]
    pc = ''.join(grp(m) for _, m, _ in cats)
    pc += f'<a class="pcard rv" href="../assets/docs/cortizo-facade.pdf" target="_blank" rel="noopener"><div class="im"><img class="ph" src="../{img('41f2dd14')}" alt="{E(L[2])}" loading="lazy"></div><div class="tx"><div><small>{E(L[2])} · PDF</small><h3>Cortizo Facade.pdf</h3></div><span class="arr">↓</span></div></a>'
    sections = f'<div class="cards one">{pc}</div>'
    facade = ''
    hero = phero(p, [('Accueil', 'index.html'), ('Cortizo Aluminium Maroc', 'cortizoaluminiummaroc/index.html')], 'Cortizo <em>Aluminium Maroc</em>', bg='assets/img/hero-cortizo.jpg')
    main = f'''<section class="sec"><div class="about-g"><div class="rv"><div class="sl">Cortizo</div><h2 class="h2">{E(why_h)}</h2></div><div class="body rv" style="--d:100ms"><p>{E(why)}</p></div></div>
  <div class="feat f4">{bl}</div>
  <div class="sl" style="margin-top:72px">Gammes</div>{sections}{facade}</section>'''
    page('cortizoaluminiummaroc/index.html', 'Cortizo Aluminium Maroc | Verre alum Partner', why[:155], hero, main + cta_band(p), 'cortizoaluminiummaroc/index.html')

# --------------------------------------------------------------------------- ALBERT GENAU / C3A
def build_albert():
    p = '../'
    L = lines('albertgeanucasablancamaroc')
    sysn = ['Systèmes Rideau de Verre', 'Systèmes Coulissante', 'La Cloison Panoramique', 'Systèmes Paravent Automatique']
    chips = ''.join(f'<span class="chip2">{E(s)}</span>' for s in sysn)
    feats = ''
    for h in ['Un Large Réseau', 'Qualité Approuvée', 'Produits Innovants', "37 ans d'expertise"]:
        feats += f'<div class="rv"><h4>{E(h)}</h4><p>{E(L[L.index(h) + 1])}</p></div>'
    diag = ''.join(gal_btn(p, k, f'Système Albert Genau {n}', 'tech') for n, k in enumerate(['c536c6d5', '5dd7f879', '39216f7e', '7b7a8578'], 1))
    ks = ['4818a098', '9afcdf9e', '880922b8']
    sl_ = ''.join(f'<div class="bn-s"><img src="../{img(k)}" alt="Albert Genau — bannière {n}" loading="lazy"></div>' for n, k in enumerate(ks, 1))
    dots = ''.join(f'<button type="button" class="bn-d{" on" if n == 1 else ""}" aria-label="Bannière {n}"></button>' for n in range(1, 4))
    ban = f'<div class="bn rv" data-bn><div class="bn-t">{sl_}</div><div class="bn-bar"><span class="bn-c"><b>01</b> / 03</span><div class="bn-dots">{dots}</div><div class="bn-ar"><button type="button" class="bn-p" aria-label="Précédent">←</button><button type="button" class="bn-n" aria-label="Suivant">→</button></div></div><i class="bn-pr"></i></div>'
    hero = phero(p, [('Accueil', 'index.html'), ('C3A Maroc', 'albertgeanucasablancamaroc/index.html')], 'Albert <em>Genau</em> · C3A Maroc', bg='assets/img/hero-albert.jpg', tag='Systèmes de vitrage')
    main = f'''<section class="sec"><div class="sl">Systèmes</div><h2 class="h2 rv">Albert Genau, <em>systèmes de vitrage</em></h2><div class="chips rv">{chips}</div>
  <div style="margin:36px 0">{ban}</div>
  <div class="feat">{feats}</div>
  <div class="sc-grid">{diag}</div>
  <p style="margin-top:44px"><a class="link-arrow" href="{GROUP_URL}" target="_blank" rel="noopener">Consultez nos Produits</a></p></section>'''
    page('albertgeanucasablancamaroc/index.html', 'Albert Genau Casablanca Maroc | C3A Maroc | Verre alum Partner', L[L.index('Un Large Réseau') + 1][:155], hero, main + cta_band(p), 'vapamenagement/index.html')

def build_c3a():
    p = '../'
    hero = phero(p, [('Accueil', 'index.html'), ('C3A Maroc', 'vapamenagement/index.html')], 'Bien plus que <em>de l’aménagement</em>', bg='assets/img/hero-c3a.jpg')
    main = f'''<section class="sec"><div class="grp rv">
  <img class="grp-bg" src="../{img('826034be')}" alt="C3A Maroc" loading="lazy">
  <div class="grp-in"><div class="grp-k"><span>Groupe</span><b>C3A MAROC</b></div>
  <div class="grp-c"><div class="sl">Notre groupe</div><h2 class="h2">Verre Alum Partner <em>&amp; C3A Maroc</em></h2>
  <p class="lead">Verre Alum Partner fait partie du Groupe C3A MAROC.</p>
  <a class="btn grp-btn" href="{GROUP_URL}" target="_blank" rel="noopener">www.c3amaroc.com <span aria-hidden="true">↗</span></a></div></div></div></section>'''
    page('vapamenagement/index.html', 'C3A Maroc | Verre alum Partner', "Bien plus que de l'aménagement — Groupe C3A MAROC.", hero, main + cta_band(p), 'vapamenagement/index.html')

# --------------------------------------------------------------------------- SERVICE PAGES
def paras(items, heads=()):
    out = ''
    for x in items:
        out += f'<h3>{E(x)}</h3>' if x in heads else f'<p>{E(x)}</p>'
    return out

def side_gal(p, keys, alt):
    return '<div class="gal">' + ''.join(gal_btn(p, k, f'{alt} {n}', 'big' if n == 1 else '') for n, k in enumerate(keys, 1)) + '</div>'

def build_menuiserie():
    p = '../'
    L = lines('menuiseriealuminium')
    heads = {L[3], L[5], L[8]}
    hero = phero(p, [('Accueil', 'index.html'), ('Nos services', 'index.html#services'), ('Menuiserie Aluminium', 'menuiseriealuminium/index.html')], '<b>Menuiserie</b> <em>Aluminium</em>', L[1], bg='assets/img/hero-menuiserie.jpg')
    body = paras(L[2:], heads)
    main = f'''<section class="sec"><div class="pg-g"><div class="prose rv">{body}</div>
  <div class="sticky rv" style="--d:100ms">{side_gal(p, ['62e2c21b', 'bc83e7ad', '2fb6fd2a'], 'Menuiserie aluminium')}
  <div class="gal-title">Partenaires</div><div style="background:#fff;padding:18px;display:flex;gap:24px;align-items:center;flex-wrap:wrap"><img src="../{img('a58f45ae')}" alt="Schüco" style="height:34px;width:auto"><img src="../{img('ad15ca33')}" alt="Cortizo" style="height:34px;width:auto"></div></div></div></section>'''
    page('menuiseriealuminium/index.html', 'Menuiserie Aluminium | Verre alum Partner', L[1], hero, main + cta_band(p), 'menuiseriealuminium/index.html')

def build_cloisons():
    p = '../'
    L = lines('cloisons-amovibles-abcd')
    si = L.index('CLOISON SIMPLE VITRAGE'); di = L.index('CLOISON DOUBLE VITRAGE')
    def block(items):
        out = ''
        for x in items:
            if x == 'Affaiblissement acoustique' or x == 'Affaiblissement acoustique :': out += f'<h4 style="font-size:10px;letter-spacing:.24em;text-transform:uppercase;font-weight:400;color:var(--t5);margin:22px 0 8px">{E(x)}</h4>'
            elif x.startswith('La cloison la plus fine'): out += f'<p class="note"><strong>{E(x)}</strong></p>'
            else: out += f'<p>{E(x)}</p>'
        return out
    hero = phero(p, [('Accueil', 'index.html'), ('Nos services', 'index.html#services'), ('Cloisons amovibles', 'cloisons-amovibles-abcd/index.html')], '<b>Cloisons</b> <em>amovibles</em>', L[1].title().replace("L'Aménagement", "l’aménagement") if False else L[1], bg='assets/img/hero-cloisons.jpg')
    main = f'''<section class="sec"><div class="sl">{E(L[2])}</div>
  <div class="split top"><div class="rv"><h2 class="h2" style="margin-bottom:26px">{E(L[si].title())}</h2><div class="prose">{block(L[si+1:di])}</div></div>
  <div class="rv" style="--d:100ms"><h2 class="h2" style="margin-bottom:26px">{E(L[di].title())}</h2><div class="prose">{block(L[di+1:])}</div></div></div>
  <div class="gal-title" style="margin-top:56px">Réalisations</div><div class="gal" style="grid-template-columns:repeat(3,1fr)">{gal_btn(p,'9481c659','Cloisons amovibles 1')}{gal_btn(p,'bd41c351','Cloisons amovibles 2')}{gal_btn(p,'0d190808','Cloisons amovibles 3')}</div></section>'''
    page('cloisons-amovibles-abcd/index.html', 'Cloisons amovibles | Verre alum Partner', L[1], hero, main + cta_band(p), 'cloisons-amovibles-abcd/index.html')

def build_murs():
    p = '../'
    L = lines('mursrideaux')
    chips = ''.join(f'<span class="chip2">{E(x)}</span>' for x in L[2:6])
    hero = phero(p, [('Accueil', 'index.html'), ('Nos services', 'index.html#services'), ('Murs Rideaux', 'mursrideaux/index.html')], '<b>Murs</b> <em>rideaux</em>', L[0], bg='assets/img/hero-murs.jpg')
    mk = ['2ac4221c', '2ac3e144', '42b991c6', 'bdc44ab9', '795ea6a3']
    mth = ''.join(f'<button class="th{" on" if n == 1 else ""}" type="button" data-src="{p}{img(k)}" aria-label="Image {n}"><img src="{p}{img(k)}" alt="" loading="lazy"><i>0{n}</i></button>' for n, k in enumerate(mk, 1))
    imgs = f'<div class="spot" data-spot><button class="spot-main" type="button" data-lb="{p}{img(mk[0])}"><img src="{p}{img(mk[0])}" alt="Murs rideaux"><span class="zoom">+ Agrandir</span></button><div class="spot-th">{mth}</div></div>'
    main = f'''<section class="sec"><div class="pg-g"><div class="prose rv"><div class="sl">Façades</div><div class="chips">{chips}</div>{paras(L[6:])}</div>
  <div class="sticky rv" style="--d:100ms">{imgs}</div></div></section>'''
    page('mursrideaux/index.html', 'Murs Rideaux & habillage des façades | Verre alum Partner', L[0], hero, main + cta_band(p), 'mursrideaux/index.html')

def build_parois():
    p = '../'
    L = lines('paroisetcabinesdouches')
    badges1 = ['VILLAS', 'RESIDENCES', 'HOTELS']
    b2 = L[L.index('Sur Mesure'):L.index('Sur Mesure') + 5]
    b3 = L[L.index('Professionnalisme'):L.index('Professionnalisme') + 6]
    pr = [pick(L, 'Nous étudions'), pick(L, 'Nous sélectionnons'), pick(L, 'Nos cloisons de douche')]
    pr[2] = pr[2]
    hero = phero(p, [('Accueil', 'index.html'), ('Nos services', 'index.html#services'), ('Parois de douches', 'paroisetcabinesdouches/index.html')], '<b>Parois</b> <em>de douche</em>', L[1], bg='assets/img/hero-parois.jpg')
    bd = lambda arr: '<div class="badges">' + ''.join(f'<div class="rv">{E(x)}</div>' for x in arr) + '</div>'
    main = f'''<section class="sec"><div class="pg-g"><div class="prose rv"><div class="sl">{E(L[2])}</div>{bd(badges1)}
  <h3>Verre Alum, le spécialiste des cloisons de douche en verre</h3>{''.join(f'<p>{E(x)}</p>' for x in pr)}{bd(b2)}
  <h3>{E(pick(L, 'Paroi de douche sur mesure'))}</h3><p>{E(pick(L, 'Nous installons'))}</p>{bd(b3)}</div>
  <div class="sticky rv" style="--d:100ms">{side_gal(p, ['882bf9fa', 'ae742a19', '3798ee19', 'b22db060'], 'Parois de douche')}</div></div></section>'''
    page('paroisetcabinesdouches/index.html', 'Parois de douche | Verre alum Partner', L[1], hero, main + cta_band(p), 'paroisetcabinesdouches/index.html')

def build_pergolas():
    p = '../'
    L = lines('pergolasbioclimatiques')
    j = lambda a, b: norm(a + ' ' + b)
    hero = phero(p, [('Accueil', 'index.html'), ('Nos services', 'index.html#services'), ('Pergolas & Verandas', 'pergolasbioclimatiques/index.html')], '<b>Pergolas</b> <em>bioclimatiques</em>', 'ET TOITURES COULISSANTES', bg='assets/img/hero-pergolas.jpg')
    items = L[2:]
    out = ''
    k = 0
    while k < len(items):
        x = items[k]
        if x.startswith('Pourquoi faire installer') or x.startswith('Découvrez les atouts') or x.startswith('Spécialistes de la pose'):
            # headings / paragraphs split over several lines in the original markup — rejoin until a line that begins a new block
            parts = [x]; k += 1
            while k < len(items) and (items[k][0].islower() or items[k][0] in ',' or items[k].startswith('et ') or items[k].startswith('pergola')):
                parts.append(items[k]); k += 1
            t = norm(' '.join(parts)).replace(' ,', ',')
            out += f'<p>{E(t)}</p>' if t.startswith('Spécialistes') else f'<h3>{E(t)}</h3>'
            continue
        if x.startswith('Choisissez une pergola'): out += f'<h3>{E(x)}</h3>'
        else: out += f'<p>{E(x)}</p>'
        k += 1
    main = f'''<section class="sec"><div class="pg-g"><div class="prose rv">{out}</div>
  <div class="sticky rv" style="--d:100ms">{side_gal(p, ['8118a7ad', 'dec6f397', '47dda647'], 'Pergola bioclimatique')}</div></div></section>'''
    page('pergolasbioclimatiques/index.html', 'Pergolas bioclimatiques & Verandas | Verre alum Partner', L[2], hero, main + cta_band(p), 'pergolasbioclimatiques/index.html')

# --------------------------------------------------------------------------- run
if __name__ == '__main__':
    build_home(); build_about(); build_cortizo(); build_albert(); build_c3a()
    for s, l, src in PRODUCTS: build_product(s, l, src)
    build_menuiserie(); build_cloisons(); build_murs(); build_parois(); build_pergolas()
    print('built', len(glob.glob(os.path.join(ROOT, '**', 'index.html'), recursive=True)), 'pages')
