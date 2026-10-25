# Novera Labs website

Static site: plain HTML, one stylesheet (`assets/css/styles.css`) and one small script (`assets/js/main.js`). No framework, no build step needed to host it. Upload the folder to any static host (Netlify, Vercel, Hostinger, S3) and it works.

## Pages
- `index.html` Home
- `services.html` Services, plus one page per service: `service-websites.html`, `service-web-apps.html`, `service-mobile-apps.html`, `service-crms.html`, `service-ecommerce.html`, `service-ai-automation.html`
- `work.html` Work (grid built from the case studies, filters by type)
- `case-study-<name>.html` One page per case study, built from `content/case-studies/<name>.json`
- `how-we-work.html` How we work (`#pricing`, `#faq`)
- `contact.html` Contact

## Case studies: add, edit and delete without code
Case studies live in `content/case-studies/`, one JSON file each. Edit them from the site's editor at `/admin`:

1. Put this folder in a GitHub repo and connect the repo to Netlify (build settings come from `netlify.toml`).
2. In Netlify: Site configuration → Access & security → OAuth → install the GitHub provider (needs a GitHub OAuth app whose callback URL is `https://api.netlify.com/auth/done`).
3. In `admin/config.yml`, check `repo:` (set to `manav-jain3012/novera-site`) and set `site_url:` to the live domain.
4. Open `https://<your-domain>/admin`, sign in with GitHub. Add, edit or delete case studies and upload images there.

Each save commits to GitHub, Netlify runs `build.py`, and the new or changed page is live in about a minute. Deleted case studies disappear from the Work page and their page is removed.

## Editing
The shared header, quote form band and footer live once in `src/partials/`. Page bodies live in `src/pages/`. After editing anything in `src/`, run:

    python3 build.py

That rewrites the seven `.html` files in this folder. Small text fixes can also be made straight in the built `.html` files, but they will be overwritten the next time `build.py` runs.

## "More we've built" rows and PDFs
The rows in "More we've built" on the Work page live in `content/more-work/`, one file each, and are edited from `/admin` under **More we've built**. Upload a PDF on a row and that row opens the PDF in a new tab. Rows without a PDF are not clickable.

## Still to fill in before launch
- Quote form: `assets/js/main.js` validates and shows a thank-you state but does not send anywhere yet. Connect it to email, a CRM or the WhatsApp API (search for `TODO`).
- Footer: `[email@novera]` and `[City], India` in `src/partials/footer.html`.
- Testimonials on Home and the case study quote: placeholder cards until real, approved quotes come in.
- Home "What founders say" phones: placeholders for screen recordings.
- Case studies: every `[...]` placeholder (cities, delivery times, stacks, quotes, screenshots). Easiest from `/admin`.
- Mobile apps page: the two `[App screens]` panels and the Flavours of Gwalior line.
