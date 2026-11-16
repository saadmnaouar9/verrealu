/* VERRE ALUM PARTNER — site behaviour (vanilla JS, no dependencies) */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     CONTACT FORM CONFIG
     The original Wix form back-end could not be recovered from the live
     site. Set FORM_ENDPOINT to a form-handling service (e.g. a Formspree
     URL: https://formspree.io/f/xxxxxxx). While it is empty the form falls
     back to opening the visitor's e-mail client (mailto:) — nothing is
     "sent" silently.
  ------------------------------------------------------------------ */
  var FORM_ENDPOINT = '';
  var FORM_TO = 'contact@verrealu.ma';

  var d = document, root = d.documentElement;
  root.classList.add('js');
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var reduce = window.matchMedia && matchMedia('(prefers-reduced-motion:reduce)').matches;

  /* ---------- page-load flag (hero word reveal) ---------- */
  requestAnimationFrame(function () { setTimeout(function () { d.body.classList.add('loaded'); }, 80); });

  /* ---------- nav: transparent over hero, solid after ---------- */
  var nav = $('.nav');
  var hasHero = nav && nav.hasAttribute('data-over');
  function navState() {
    if (!nav) return;
    var open = nav.classList.contains('menu-open');
    var over = hasHero && window.scrollY < 40 && !open;
    nav.classList.toggle('over', over);
  }
  navState();
  window.addEventListener('scroll', navState, { passive: true });

  /* ---------- mobile menu ---------- */
  var burger = $('.nav-burger'), mob = $('.mob');
  function setMenu(on) {
    if (!burger || !mob) return;
    burger.setAttribute('aria-expanded', on);
    mob.classList.toggle('on', on);
    nav.classList.toggle('menu-open', on);
    d.body.classList.toggle('lock', on);
    navState();
  }
  if (burger) burger.addEventListener('click', function () { setMenu(burger.getAttribute('aria-expanded') !== 'true'); });
  $$('.mob a').forEach(function (a) { a.addEventListener('click', function () { setMenu(false); }); });
  window.addEventListener('resize', function () { if (window.innerWidth > 1180) setMenu(false); });

  /* ---------- scroll reveal ---------- */
  var rv = $$('.rv');
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px', threshold: .08 });
    rv.forEach(function (el) { io.observe(el); });
  } else rv.forEach(function (el) { el.classList.add('in'); });

  /* ---------- count-up stats ---------- */
  $$('[data-count]').forEach(function (el) {
    var end = parseFloat(el.getAttribute('data-count')), suffix = el.getAttribute('data-suffix') || '';
    var fmt = function (n) { return Math.round(n).toLocaleString('fr-FR').replace(/ /g, ' ') + suffix; };
    if (reduce || !('IntersectionObserver' in window)) { el.textContent = fmt(end); return; }
    var o = new IntersectionObserver(function (es) {
      if (!es[0].isIntersecting) return; o.disconnect();
      var t0 = performance.now(), dur = 1600;
      (function step(t) {
        var p = Math.min(1, (t - t0) / dur), e = 1 - Math.pow(1 - p, 4);
        el.textContent = fmt(end * e);
        if (p < 1) requestAnimationFrame(step);
      })(t0);
    }, { threshold: .5 });
    o.observe(el);
  });

  /* ---------- hero slideshow ---------- */
  var slides = $$('.hslide');
  if (slides.length) {
    var dots = $$('.hdot'), cap = $('#hcap'), idx = 0, timer;
    var vids = slides.map(function (s) { return $('video', s); });
    var go = function (i) {
      idx = (i + slides.length) % slides.length;
      slides.forEach(function (s, k) { s.classList.toggle('on', k === idx); });
      dots.forEach(function (b, k) { b.classList.toggle('on', k === idx); b.setAttribute('aria-current', k === idx); });
      if (cap) cap.textContent = slides[idx].getAttribute('data-cap');
      vids.forEach(function (v, k) {
        if (!v) return;
        if (k === idx) { v.currentTime = 0; var pr = v.play(); if (pr && pr.catch) pr.catch(function () {}); }
        else v.pause();
      });
      play();
    };
    /* a video slide stays until its video ends; image slides advance after 6 s */
    function play() {
      clearTimeout(timer);
      if (reduce) return;
      var v = vids[idx];
      if (v && !v.error) {
        v.onended = function () { go(idx + 1); };
        timer = setTimeout(function () { go(idx + 1); }, 60000); /* safety net if 'ended' never fires */
      } else timer = setTimeout(function () { go(idx + 1); }, 6000);
    }
    dots.forEach(function (b, k) { b.addEventListener('click', function () { go(k); }); });
    if (slides.length === 1) {
      /* video-only hero: keep it looping; pause when scrolled out of view to save battery/data */
      slides[0].classList.add('on');
      var hv = vids[0];
      if (hv) {
        var pr0 = hv.play(); if (pr0 && pr0.catch) pr0.catch(function () {});
        if ('IntersectionObserver' in window) new IntersectionObserver(function (es) {
          if (es[0].isIntersecting) { var q = hv.play(); if (q && q.catch) q.catch(function () {}); } else hv.pause();
        }, { threshold: .05 }).observe($('.hero'));
      }
    } else go(0);
  }

  /* ---------- tabs ---------- */
  $$('[data-tabs]').forEach(function (wrap) {
    var tabs = $$('[role=tab]', wrap), panels = $$('[role=tabpanel]', wrap);
    function sel(i) {
      tabs.forEach(function (t, k) { t.setAttribute('aria-selected', k === i); t.tabIndex = k === i ? 0 : -1; });
      panels.forEach(function (p, k) { p.hidden = k !== i; });
    }
    tabs.forEach(function (t, i) {
      t.addEventListener('click', function () { sel(i); });
      t.addEventListener('keydown', function (e) {
        var n = e.key === 'ArrowRight' ? i + 1 : e.key === 'ArrowLeft' ? i - 1 : null;
        if (n === null) return; n = (n + tabs.length) % tabs.length; sel(n); tabs[n].focus();
      });
    });
    sel(0);
  });

  /* ---------- lightbox ---------- */
  var lb = $('#lb');
  if (lb) {
    var items = [], cur = 0, lbImg = $('.lb-img', lb), lbCap = $('.lb-cap', lb), lbCnt = $('.lb-count', lb), lastFocus;
    var show = function (i) {
      cur = (i + items.length) % items.length;
      lbImg.src = items[cur].src; lbImg.alt = items[cur].alt;
      lbCap.textContent = items[cur].alt; lbCnt.textContent = (cur + 1) + ' / ' + items.length;
    };
    var openLb = function (i) { lastFocus = d.activeElement; show(i); lb.classList.add('on'); d.body.classList.add('lock'); $('.lb-close', lb).focus(); };
    var closeLb = function () { lb.classList.remove('on'); d.body.classList.remove('lock'); if (lastFocus) lastFocus.focus(); };
    var gs = $$('[data-lb]');
    items = gs.map(function (g) { var im = $('img', g); return { src: g.getAttribute('data-lb') || im.src, alt: im.alt }; });
    gs.forEach(function (g, i) { g.addEventListener('click', function () { openLb(i); }); });
    $('.lb-close', lb).addEventListener('click', closeLb);
    $('.lb-prev', lb).addEventListener('click', function () { show(cur - 1); });
    $('.lb-next', lb).addEventListener('click', function () { show(cur + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) closeLb(); });
    d.addEventListener('keydown', function (e) {
      if (!lb.classList.contains('on')) return;
      if (e.key === 'Escape') closeLb(); if (e.key === 'ArrowRight') show(cur + 1); if (e.key === 'ArrowLeft') show(cur - 1);
    });
  }

  /* ---------- brochure modal ---------- */
  var modal = $('#brochures');
  if (modal) {
    var mLast;
    var openM = function (e) { if (e) e.preventDefault(); mLast = d.activeElement; modal.classList.add('on'); d.body.classList.add('lock'); setMenu(false); d.body.classList.add('lock'); $('.x-btn', modal).focus(); };
    var closeM = function () { modal.classList.remove('on'); d.body.classList.remove('lock'); if (mLast) mLast.focus(); };
    $$('[data-open-brochures]').forEach(function (a) { a.addEventListener('click', openM); });
    $('.x-btn', modal).addEventListener('click', closeM);
    modal.addEventListener('click', function (e) { if (e.target === modal) closeM(); });
    d.addEventListener('keydown', function (e) { if (e.key === 'Escape' && modal.classList.contains('on')) closeM(); });
    if (location.hash === '#brochures') openM();
  }

  /* ---------- contact form ---------- */
  var form = $('#contact-form');
  if (form) {
    var status = $('.form-status', form), btn = $('button[type=submit]', form);
    var rules = {
      nom: function (v) { return v.trim().length > 1; },
      email: function (v) { return /^.+@.+\.[a-zA-Z]{2,63}$/.test(v.trim()); }
    };
    var check = function (inp) {
      var r = rules[inp.name]; if (!r) return true;
      var ok = r(inp.value), err = inp.parentNode.querySelector('.ferr');
      inp.classList.toggle('valid', ok && !!inp.value); inp.classList.toggle('invalid', !ok);
      if (err) err.classList.toggle('on', !ok); return ok;
    };
    $$('input,textarea', form).forEach(function (i) { i.addEventListener('blur', function () { check(i); }); });
    var say = function (cls, msg) { status.className = 'form-status on ' + cls; status.textContent = msg; };
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var ok = $$('input,textarea', form).map(check).every(Boolean);
      if (!ok) { say('err', 'Veuillez renseigner les champs obligatoires (Nom, Email).'); return; }
      var data = {};
      $$('input,textarea', form).forEach(function (i) { data[i.name] = i.value.trim(); });
      if (FORM_ENDPOINT) {
        btn.disabled = true;
        fetch(FORM_ENDPOINT, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
          .then(function (r) { if (!r.ok) throw new Error(r.status); say('ok', 'Votre message a été envoyé avec succès.'); form.reset(); $$('input', form).forEach(function (i) { i.classList.remove('valid'); }); })
          .catch(function () { say('err', 'Échec de l’envoi. Merci de nous écrire à ' + FORM_TO + ' ou de nous appeler au 00 212 662 16 16 17.'); })
          .then(function () { btn.disabled = false; });
      } else {
        var body = 'Nom: ' + data.nom + '\nEmail: ' + data.email + '\nTéléphone: ' + (data.phone || '') + '\n\n' + (data.message || '');
        say('ok', 'Votre application e-mail va s’ouvrir avec le message prêt à envoyer. Si rien ne s’ouvre, écrivez-nous à ' + FORM_TO + '.');
        location.href = 'mailto:' + FORM_TO + '?subject=' + encodeURIComponent(data.sujet || 'Demande de contact — site web') + '&body=' + encodeURIComponent(body);
      }
    });
  }

  /* ---------- custom cursor ---------- */
  if (window.matchMedia && matchMedia('(pointer:fine)').matches && !reduce) {
    var c = d.createElement('div'), r = d.createElement('div');
    c.id = 'cur'; r.id = 'cur-ring'; d.body.appendChild(c); d.body.appendChild(r);
    var x = -100, y = -100, rx = -100, ry = -100;
    window.addEventListener('mousemove', function (e) { x = e.clientX; y = e.clientY; root.classList.add('cur-on'); }, { passive: true });
    (function loop() {
      rx += (x - rx) * .16; ry += (y - ry) * .16;
      c.style.transform = 'translate(' + x + 'px,' + y + 'px) translate(-50%,-50%)';
      r.style.transform = 'translate(' + rx + 'px,' + ry + 'px) translate(-50%,-50%)';
      requestAnimationFrame(loop);
    })();
    d.addEventListener('mouseover', function (e) {
      var h = e.target.closest && e.target.closest('a,button,[data-lb],input,textarea,summary');
      c.classList.toggle('hover', !!h); r.classList.toggle('hover', !!h);
    });
  }
})();

/* Profilés & schémas spotlight */
(function(){document.querySelectorAll('[data-spot]').forEach(function(sp){
  var m=sp.querySelector('.spot-main'),mi=m.querySelector('img');
  sp.querySelectorAll('.th').forEach(function(t){t.addEventListener('click',function(){
    sp.querySelectorAll('.th').forEach(function(x){x.classList.remove('on')});t.classList.add('on');
    mi.style.opacity=0;setTimeout(function(){mi.src=t.dataset.src;m.dataset.lb=t.dataset.src;mi.style.opacity=1},220)})})})})();
