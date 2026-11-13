# Verre Alum Partner — redesign (static site)

Rebuilt from the live Wix site (verrealu.com) in the visual language of spectra.ma.
Pure HTML/CSS/JS — no build step needed to host. Upload the folder to any web host.

- Preview locally: `python -m http.server 8123` then open http://localhost:8123
- Regenerate pages after editing content/layout: `python tools/build.py` (needs Python + Pillow)
- `tools/_src` = scraped copy of the original pages (text + raw images); `tools/test.py` = interaction tests.

## Must be recreated / decided before going live
1. **Contact form back-end** — the Wix form service can't be recovered. Set `FORM_ENDPOINT` at the top of `assets/js/main.js`
   (e.g. a Formspree URL). Until then the form opens the visitor's mail client (mailto) to contact@verrealu.ma.
2. **E-mail address mismatch** — original site displays contact@verrealu.ma but its link pointed to contact@batiplus.ma. Confirm the right one.
3. **Hero slideshow photos** — Wix slide backgrounds weren't exposed in the HTML; slides use site images matching the six slide names.
4. **Domain / SEO** — URLs keep the original slugs (ASCII, in folders); add 301 redirects for the accented originals
   (`/copie-de-système-repliable`, `/copie-de-cor-60-ouvrant-caché-rpt`, `/vapaménagement`...). Wix hosting/analytics are not carried over.
5. "Garde corps" tiles had no page on the original; they link to the contact section.
