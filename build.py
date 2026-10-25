"""Builds the static pages: src/pages/*.html + partials -> ./*.html
Also builds one case study page per file in content/case-studies/*.json
(case-study-<slug>.html) and the project grid on the Work page ({{work_grid}}).
The case study files are edited from /admin (Decap CMS); Netlify runs this
script on every save, so nobody has to run it by hand.

Each page starts with a meta comment:
<!-- title: Page title | active: services | description: ... | cta: Heading for the form band -->
and uses {{header}}, {{cta}} and {{footer}} where the shared parts go.
"""
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / 'src'
PARTS = {p.stem: p.read_text() for p in (SRC / 'partials').glob('*.html')}
HEAD = """<!doctype html>
<html lang="en-IN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600&family=DM+Sans:opsz,wght@9..40,400;9..40,500&family=DM+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="assets/css/styles.css">
<link rel="icon" href="assets/img/mark.png">
</head>
<body>
"""


ARW = '<svg width="{0}" height="{0}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17L17 7M9 7h8v8"/></svg>'


def esc(v):
    return html.escape(str(v or ''), quote=True)


def load_cases():
    cases = []
    for f in (ROOT / 'content' / 'case-studies').glob('*.json'):
        c = json.loads(f.read_text())
        c['slug'] = re.sub(r'[^a-z0-9-]+', '-', (c.get('slug') or f.stem).lower()).strip('-')
        cases.append(c)
    return sorted(cases, key=lambda c: (float(c.get('order') or 999), c['slug']))


def img_src(v):
    v = (v or '').strip()
    return v.lstrip('/') if v and not v.startswith('http') else v


def work_grid(cases):
    out = []
    for i, c in enumerate([c for c in cases if c.get('show_on_work', True)]):
        out.append(f'''      <a class="wcard" href="case-study-{c['slug']}.html" data-type="{esc(c.get('filter'))}">
        <img src="{esc(img_src(c.get('card_image')))}" alt="{esc(c.get('name'))}, {esc(c.get('type_label', '')).lower()} by Novera Labs" width="604" height="415" loading="{'eager' if i < 2 else 'lazy'}">
        <span class="info"><span class="txt"><small>{esc(c.get('number'))} · {esc(c.get('type_label'))}</small><b>{esc(c.get('name'))}</b><p>{esc(c.get('card_line'))}</p></span><span class="circ">{ARW.format(18)}</span></span>
      </a>''')
    return '\n'.join(out)


def load_more():
    rows = [json.loads(f.read_text()) for f in (ROOT / 'content' / 'more-work').glob('*.json')]
    return sorted(rows, key=lambda r: (float(r.get('order') or 999), r.get('title', '')))


def more_rows(rows):
    out = []
    for i, r in enumerate(rows, 1):
        inner = f'<span class="n">{i:02d}</span><span class="body"><span class="t">{esc(r.get("title"))}</span><span class="d">{esc(r.get("line"))}</span></span><span class="tag">{esc(r.get("tag"))}</span>'
        pdf = img_src(r.get('pdf'))
        if pdf:
            out.append(f'      <a class="more-row has-pdf" href="{esc(pdf)}" target="_blank" rel="noopener">{inner}<span class="pdf">View PDF ↗</span></a>')
        else:
            out.append(f'      <div class="more-row">{inner}</div>')
    return '\n'.join(out)


def case_page(c):
    facts = ''.join(f'<div><small>{esc(f.get("label"))}</small><b>{esc(f.get("value"))}</b></div>' for f in c.get('facts') or [])
    hero = img_src(c.get('hero_image'))
    if hero:
        media = f'<div class="box has-img"><img src="{esc(hero)}" alt="{esc(c.get("name"))}"></div>'
    else:
        media = '<div class="box"><div class="win"><div class="browser-bar"><i></i><i></i><i></i></div><div class="ph"><span class="ph-label">[Main dashboard screenshot]</span></div></div></div>'
    feats = '\n'.join(f'        <div class="feat"><span class="n">0{i}</span><b>{esc(f.get("title"))}</b><span>{esc(f.get("text"))}</span></div>' for i, f in enumerate(c.get('features') or [], 1))
    shots = ''
    sc = [s for s in (c.get('screens') or []) if s.get('image') or s.get('label')][:3]
    if sc:
        cells = []
        for i, s in enumerate(sc):
            cls = ' class="phone-shot"' if i == 2 else ''
            inner = f'<img src="{esc(img_src(s.get("image")))}" alt="{esc(s.get("label"))}" loading="lazy">' if s.get('image') else f'<span class="ph-label">[{esc(s.get("label"))}]</span>'
            cells.append(f'<div{cls}>{inner}</div>')
        shots = f'<div class="shots n{len(sc)}">{"".join(cells)}</div>'
    stack = ''.join(f'<span>{esc(x)}</span>' for x in c.get('stack') or [] if str(x).strip())
    stack_sec = f'''  <section class="wrap split-07 case-sec">
    <p class="eb">04 · Stack</p>
    <div class="stack-chips">{stack}</div>
  </section>''' if stack else ''
    q = c.get('quote') or {}
    quote = f'''<figure class="case-quote">
      <blockquote>“{esc(q.get('text'))}”</blockquote>
      <figcaption><span class="av"></span><span><b>{esc(q.get('name'))}</b><small>{esc(q.get('role'))}</small></span></figcaption>
    </figure>''' if (q.get('text') or '').strip() else ''
    muted = f' <span>{esc(c.get("needed_muted"))}</span>' if (c.get('needed_muted') or '').strip() else ''
    body = f'''{{{{header}}}}
<main>
  <section class="wrap case-top">
    <p class="crumb"><a href="work.html">Work</a> / <b>{esc(c.get('crumb'))}</b></p>
    <h1 class="h1 s92">{esc(c.get('title_before'))} <span class="g">{esc(c.get('title_highlight'))}</span> {esc(c.get('title_after'))}</h1>
    <div class="facts">{facts}</div>
  </section>

  <section class="wrap-wide case-media" aria-label="{esc(c.get('name'))}">
    {media}
  </section>

  <section class="wrap split-07 case-sec first">
    <p class="eb">01 · The client</p>
    <p class="story">{esc(c.get('client'))}</p>
  </section>
  <section class="wrap split-07 case-sec s96">
    <p class="eb">02 · What they needed</p>
    <p class="story">{esc(c.get('needed'))}{muted}</p>
  </section>
  <section class="wrap case-sec">
    <div class="split-07">
      <p class="eb">03 · What we built</p>
      <div class="feats">
{feats}
      </div>
    </div>
    {shots}
  </section>
{stack_sec}
  <section class="wrap case-sec">
    {quote}
    <a class="all-projects" href="work.html"><b>View All Projects</b><span>{ARW.format(24)}</span></a>
  </section>
</main>
{{{{cta}}}}
{{{{footer}}}}'''
    meta = {'title': f"Case study: {c.get('name')} | Novera Labs", 'active': 'work',
            'description': c.get('seo_description') or c.get('card_line') or '', 'cta': "Have an idea? Let's put it on screen."}
    return meta, body


def build(page, text=None, out_name=None, extra=None):
    text = page.read_text() if text is None else text
    meta_match = re.match(r'<!--(.*?)-->\s*', text, re.S)
    meta = {}
    if meta_match:
        for part in meta_match.group(1).split('|'):
            if ':' in part:
                k, v = part.split(':', 1)
                meta[k.strip()] = v.strip()
        text = text[meta_match.end():]
    if extra:
        meta.update(extra)
    active = meta.get('active', '')
    header = PARTS['header']
    for key in ('services', 'work', 'process', 'contact'):
        header = header.replace('{{cur:%s}}' % key, ' aria-current="page"' if key == active else '')
    cta = PARTS['cta'].replace('{{heading}}', meta.get('cta', "Have an idea? Let's put it on screen."))
    body = text.replace('{{work_grid}}', work_grid(CASES)).replace('{{more_rows}}', more_rows(load_more())).replace('{{header}}', header).replace('{{cta}}', cta).replace('{{footer}}', PARTS['footer'])
    page_html = HEAD.format(title=esc(meta.get('title', 'Novera Labs')), description=esc(meta.get('description', ''))) + body + '\n</body>\n</html>\n'
    name = out_name or page.name
    (ROOT / name).write_text(page_html)
    print('built', name)


CASES = load_cases()
# Remove pages of case studies that were deleted in the editor
for old in ROOT.glob('case-study-*.html'):
    if old.stem[len('case-study-'):] not in {c['slug'] for c in CASES}:
        old.unlink()
        print('removed', old.name)
for p in sorted((SRC / 'pages').glob('*.html')):
    build(p)
for c in CASES:
    meta, body = case_page(c)
    build(None, text=body, out_name=f"case-study-{c['slug']}.html", extra=meta)
