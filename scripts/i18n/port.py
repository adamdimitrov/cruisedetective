#!/usr/bin/env python3
"""i18n port tool: bring translated pages in line with the EN page using a translation memory.

Translation memory: i18n/memory/<lang>.json  (EN string -> translated string). Every string
translated once is reused on every page and every later run, so only new strings cost tokens.

Commands
  missing  --lang L --en EN_PAGE --what cards|sections|menus [--ids a,b] [--out FILE]
           List EN strings with no translation yet -> i18n/todo/<page>.<what>.<lang>.txt ("n|EN").
  learn    --lang L --todo FILE --done FILE
           Merge a translated todo ("n|translation", same numbering) into the memory.
  harvest  --lang L --en EN_PAGE --tr TR_PAGE --what cards|sections [--ids a,b]
           Learn from a page that is already fully translated (same HTML structure as EN).
  cards    --lang L --en EN_PAGE --tr TR_PAGE [--check]
           Rebuild the comparison cards (div.bpa-card) from EN, keep the page's own titles/rank tags.
  sections --lang L --en EN_PAGE --tr TR_PAGE --ids a,b --place before-id:ID|before-closing-of:ID|before:TEXT [--check]
           Insert (or replace) a contiguous run of EN sections, translated.
  menus    --lang L --en EN_PAGE --tr TR_PAGE [--check]
           Printed-menu modal + templates + scripts (dinner pages).
  page     --lang L --en EN_PAGE --tr NEW_PAGE --chrome-from TR_PAGE_SAME_LANG [--check]
           Whole-page translation for a page that has no translation yet: header/footer from an existing
           page in that language, body text, title/meta/og, JSON-LD strings, page config labels, html lang,
           canonical/og:url. hreflang: EN page and new page are linked to each other (others removed).
           Strings: --what page with missing/learn.
  sync     PRESET [--langs de,fr] [--check]
           Everything in scripts/i18n/presets.json for that page group (cards, menus, sections),
           for every language. With --check: report what is missing per language, change nothing.
           Typical loop after an EN change:  sync seine --check  ->  missing/learn  ->  sync seine
EN_PAGE / TR_PAGE are folders (seine-river-cruises-paris, fr/meilleures-croisieres-seine-paris).
After applying: scripts/cards/cards.py drift, scripts/qa/mobile_overflow.py, scripts/ship/preflight.py --fix.
"""
import argparse, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
from seg import cards, segments  # noqa: E402

MEM_DIR = os.path.join(ROOT, 'i18n', 'memory')
TODO_DIR = os.path.join(ROOT, 'i18n', 'todo')
LANGS = json.load(open(os.path.join(HERE, 'langs.json'), encoding='utf-8'))
KEEP = re.compile(r'^(GetYourGuide|Tiqets|Viator|Tripadvisor|\(\d[\d.,]*k?\+?\)|[\d.]+|€\d+|\d+ / \d+)$')
ALT = re.compile(r'^(.+?) dinner cruise: (.+)$')
STYLE_IDS = ['bpa-lang-css', 'dc-menu-css', 'dc-food-css', 'ltt-dubai-safari-styles']


# ---------------------------------------------------------------- memory
def mem_load(lang):
    p = os.path.join(MEM_DIR, f'{lang}.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}


def mem_save(lang, d):
    os.makedirs(MEM_DIR, exist_ok=True)
    json.dump(dict(sorted(d.items())), open(os.path.join(MEM_DIR, f'{lang}.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)


def page(p):
    return os.path.join(ROOT, p.strip('/'), 'index.html')


def read(p):
    return open(page(p), encoding='utf-8').read()


def write(p, h):
    open(page(p), 'w', encoding='utf-8').write(h)


def translatable(t):
    t = t.strip()
    return bool(t) and '\x00' not in t and bool(re.search(r'[A-Za-z]', t)) and not KEEP.match(t)


# ---------------------------------------------------------------- html helpers
def block_end(h, start):
    tag = re.match(r'<(\w+)', h[start:]).group(1)
    d = 0
    for m in re.finditer(r'<(/?)%s\b[^>]*>' % tag, h[start:]):
        d += -1 if m.group(1) else 1
        if d == 0:
            return start + m.end()


def section(h, sid):
    s = re.search(r'<(\w+)[^>]*\bid="%s"' % re.escape(sid), h).start()
    return s, block_end(h, s)


def product(href):
    href = href.replace('&amp;', '&')
    m = re.search(r'-(p\d{5,})/', href) or re.search(r'-(t\d{3,})/?', href)
    return m.group(1) if m else href


class T:
    """Translator over memory, with per-call local overrides; records misses."""
    def __init__(self, lang, ns=''):
        self.lang, self.d, self.local, self.missing, self.ns = lang, mem_load(lang), {}, [], ns

    def tr(self, t):
        core = t.strip()
        if not translatable(core):
            return t
        if core in self.local:
            return t.replace(core, self.local[core])
        if self.ns and f'{self.ns}::{core}' in self.d:
            return t.replace(core, self.d[f'{self.ns}::{core}'])
        if core in self.d:
            return t.replace(core, self.d[core])
        m = ALT.match(core)
        if m:
            cap = m.group(2)[0].upper() + m.group(2)[1:]
            if cap in self.d:
                return t.replace(core, LANGS[self.lang]['dinner_alt'].format(brand=m.group(1), text=self.d[cap]))
        self.missing.append(core)
        return t

    def html(self, b, attrs=('alt', 'data-cap', 'aria-label', 'title', 'data-toc')):
        keep = []
        b = re.sub(r'<style\b.*?</style>|<script\b.*?</script>', lambda m: (keep.append(m.group(0)), f'\x01{len(keep)-1}\x01')[1], b, flags=re.S)
        b = re.sub(r'>([^<>]+)<', lambda m: '>' + self.tr(m.group(1)) + '<', b)
        b = re.sub(r'(?<![\w-])(%s)="([^"]*)"' % '|'.join(attrs), lambda m: f'{m.group(1)}="{self.tr(m.group(2))}"', b)
        return re.sub(r'\x01(\d+)\x01', lambda m: keep[int(m.group(1))], b)


def strings_of(b, attrs=('alt', 'data-cap', 'aria-label', 'title', 'data-toc')):
    b = re.sub(r'<style\b.*?</style>|<script\b.*?</script>', '', b, flags=re.S)
    out = [t.strip() for t in re.findall(r'>([^<>]+)<', b)]
    out += [m.group(2).strip() for m in re.finditer(r'(?<![\w-])(%s)="([^"]*)"' % '|'.join(attrs), b)]
    return [t for t in out if translatable(t)]


# ---------------------------------------------------------------- link localisation
_ALTS = {}


def localize_links(b, lang):
    def alts(path):
        if path not in _ALTS:
            f = page(path)
            m = {}
            if os.path.exists(f):
                for l in re.finditer(r'<link[^>]*hreflang="([^"]+)"[^>]*>', open(f, encoding='utf-8').read()):
                    m[l.group(1)] = re.sub(r'^https://www\.thecruisedetective\.com', '', re.search(r'href="([^"]+)"', l.group(0)).group(1))
            _ALTS[path] = m
        return _ALTS[path]

    def repl(m):
        mm = re.match(r'^(?:https://www\.thecruisedetective\.com)?(/[^"#?]*)(#[^"]*)?$', m.group(1))
        if not mm or mm.group(1) in ('/', ''):
            return m.group(0)
        a = alts(mm.group(1).rstrip('/')).get(lang)
        # only follow hreflang when it points to a page of the same topic (guards against bad alternates)
        if not a or a.rstrip('/') == mm.group(1).rstrip('/'):
            return m.group(0)
        return f'href="{a}{mm.group(2) or ""}"'
    return re.sub(r'href="([^"]+)"', repl, b)


# ---------------------------------------------------------------- cards
def drop_dead_anchors(b, pg):
    b = re.sub(r'<span class="bpa-lang-note"><a href="#([^"]+)">[^<]*</a></span>', lambda m: '' if f'id="{m.group(1)}"' not in pg else m.group(0), b)
    return re.sub(r'\s*<a href="#([^"]+)">[^<]*</a>', lambda m: '' if f'id="{m.group(1)}"' not in pg else m.group(0), b)


def strip_menu_modal(b):
    b = re.sub(r'<button[^>]*class="dc-food-btn"[^>]*>[^<]*</button>', '', b)
    b = re.sub(r'<div class="dc-sets">.*?</div>', '', b, flags=re.S)
    return re.sub(r'<button class="dc-c"([^>]*)>(.*?)</button>',
                  lambda m: '<span class="dc-c"' + re.sub(r'\s(type|data-sec)="[^"]*"', '', m.group(1)) + '>' + m.group(2) + '</span>', b, flags=re.S)


def inner(block, cls):
    m = re.search(r'class="%s[^"]*"[^>]*>([^<]+)<' % re.escape(cls), block)
    return m.group(1) if m else None


def do_cards(a):
    en, tr = read(a.en), read(a.tr)
    t = T(a.lang)
    ec = [en[s:e] for s, e in cards(en)]
    spans = cards(tr)
    by = {product(re.search(r'class="bpa-title" href="([^"]+)"', tr[s:e]).group(1)): tr[s:e] for s, e in spans}
    if len(ec) != len(spans):
        sys.exit(f'card count differs: EN {len(ec)} vs {len(spans)}')
    new = []
    for c in ec:
        old = by.get(product(re.search(r'class="bpa-title" href="([^"]+)"', c).group(1)))
        if old is None:
            sys.exit('a product on EN has no card on the translated page: rerank first')
        ro, to_, re_, te = inner(old, 'bpa-rank-tag'), inner(old, 'bpa-title'), inner(c, 'bpa-rank-tag'), inner(c, 'bpa-title')
        t.local = {te: to_}
        b = c.replace(f'>{re_}<', '>\x00R\x00<', 1).replace(f'>{te}<', '>\x00T\x00<', 1)
        b = t.html(b).replace('\x00R\x00', ro).replace('\x00T\x00', to_)
        b = drop_dead_anchors(localize_links(b, a.lang), tr)
        if 'id="dc-modal"' not in tr:
            b = strip_menu_modal(b)
        new.append(b)
    return finish(a, t, lambda: splice_cards(a, en, tr, spans, new))


def splice_cards(a, en, tr, spans, new):
    out, pos = [], 0
    for (s, e), b in zip(spans, new):
        out += [tr[pos:s], b]
        pos = e
    tr = ''.join(out) + tr[pos:]
    es = {m.group(1): m for m in re.finditer(r'<style id="([^"]+)">(.*?)</style>', en, re.S)}
    for sid in STYLE_IDS:
        if sid not in es:
            continue
        cur = {m.group(1): m for m in re.finditer(r'<style id="([^"]+)">(.*?)</style>', tr, re.S)}
        blk = es[sid].group(0).replace('content:"—"', 'content:"";display:inline-block;width:14px;height:1px;background:currentColor;vertical-align:middle')
        if sid in cur:
            tr = tr[:cur[sid].start()] + blk + tr[cur[sid].end():]
        else:
            k = tr.find('<style id="ltt-hero-card-styles">')
            k = k if k > 0 else tr.find('</head>')
            tr = tr[:k] + blk + '\n' + tr[k:]
    js = re.search(r'<script[^>]*>\s*\(function\(\)\{\s*var N=\{en:.*?</script>', en, re.S)
    if js:
        L = LANGS[a.lang]
        nmap = 'var N=' + json.dumps(L['names'], ensure_ascii=True).replace('"', "'").replace("': '", "':'").replace("', '", "','") + ';'
        j = re.sub(r"var N=\{[^}]*\};", lambda _: nmap, js.group(0), count=1)
        j = j.replace("if(!code||code==='en'||!N[code]) return;", "if(!code||!N[code]) return;")
        j = j.replace("label.textContent='Audio in '+N[code]+' \\u2713';", "label.textContent=" + L['audio_label_js'] + ";")
        old = re.search(r'<script[^>]*>\s*\(function\(\)\{\s*var N=\{.*?</script>', tr, re.S)
        tr = tr[:old.start()] + j + tr[old.end():] if old else tr[:tr.rfind('</body>')] + j + '\n' + tr[tr.rfind('</body>'):]
    write(a.tr, tr)


# ---------------------------------------------------------------- sections
def do_sections(a):
    en, tr = read(a.en), read(a.tr)
    t = T(a.lang, 'sections')
    ids = a.ids.split(',')
    s, _ = section(en, ids[0])
    _, e = section(en, ids[-1])
    m = re.match(r'\s*<script>(?:(?!</script>).)*?getElementById\(\'%s\'\).*?</script>' % re.escape(ids[-1]), en[e:], re.S)
    if m:
        e += m.end()
    block = localize_links(t.html(en[s:e]), a.lang)

    def apply():
        nonlocal tr
        for sid in ids:
            if f'id="{sid}"' in tr:
                x, y = section(tr, sid)
                tail = re.match(r'\s*<script>(?:(?!</script>).)*?getElementById\(\'%s\'\).*?</script>' % re.escape(sid), tr[y:], re.S)
                tr = tr[:x] + tr[y + (tail.end() if tail else 0):]
        mode, _, anchor = a.place.partition(':')
        if mode == 'before':
            k = tr.find(anchor)
        elif mode == 'before-id':
            k = re.search(r'<\w+[^>]*\bid="%s"' % re.escape(anchor), tr).start()
        elif mode == 'before-closing-of':
            k = tr.rfind('</div>', 0, re.search(r'<\w+[^>]*\bid="%s"' % re.escape(anchor), tr).start())
        else:
            sys.exit('bad --place')
        if k < 0:
            sys.exit('anchor not found: ' + a.place)
        write(a.tr, tr[:k] + block + '\n' + tr[k:])
    return finish(a, t, apply)


# ---------------------------------------------------------------- menus
MENU_L10N = json.load(open(os.path.join(HERE, 'menu_l10n.json'), encoding='utf-8'))


def do_menus(a):
    en, tr = read(a.en), read(a.tr)
    t = T(a.lang, 'menus')
    titles = {}
    for s, e in cards(tr):
        m = re.search(r'class="bpa-title" href="([^"]+)"[^>]*>([^<]+)<', tr[s:e])
        if m:
            titles[product(m.group(1))] = m.group(2)
    i = en.find('<div class="dc-modal"')
    j = en.find('</template>', en.rfind('<template id="dc-menu-')) + len('</template>')
    block = en[i:j]
    scripts = re.findall(r'<script>.*?</script>', en[j:j + 8000], re.S)[:2]

    def tpl(m):
        tag = m.group(0)
        p = product(re.search(r'data-link="([^"]+)"', tag).group(1))
        if p in titles:
            tag = re.sub(r'data-title="[^"]*"', lambda _: f'data-title="{titles[p]}"', tag)
        return re.sub(r'data-(price|sub)="([^"]*)"', lambda mm: f'data-{mm.group(1)}="{t.tr(mm.group(2))}"', tag)
    block = re.sub(r'<template id="dc-menu-[^"]+"[^>]*>', tpl, block)
    block = t.html(block, attrs=('aria-label', 'alt', 'title'))
    L = MENU_L10N[a.lang]
    s1 = scripts[0]
    s1 = s1.replace("(n+(v==='veg'?' vegetarian':' GF/LF')+' dish'+(n>1?'es':'')+' on this menu')", '(' + L['count'] + ')')
    s1 = s1.replace("'Nothing marked '+(v==='veg'?'vegetarian':'GF/LF')+' — ask the crew'", L['none'])
    s1 = s1.replace("'Hide menu ▴'", repr(L['hide'])).replace("'Open menu ▾'", repr(L['open']))
    out = block + '\n' + s1 + '\n' + scripts[1]

    def apply():
        nonlocal tr
        if 'id="dc-modal"' in tr:
            x = tr.find('<div class="dc-modal"')
            y = tr.rfind('</template>') + len('</template>')
            for _ in range(2):
                sm = re.match(r'\s*<script>.*?</script>', tr[y:], re.S)
                y += sm.end() if sm else 0
            tr = tr[:x] + out + tr[y:]
        else:
            k = tr.find('</script>', tr.find('id="bpa-lang-js"')) + len('</script>')
            tr = tr[:k] + out + tr[k:]
        write(a.tr, tr)
    return finish(a, t, apply)


# ---------------------------------------------------------------- whole page
SITE = 'https://www.thecruisedetective.com'
META = r'(<meta[^>]*(?:name|property)="(?:description|og:title|og:description|twitter:title|twitter:description|og:image:alt)"[^>]*content=")([^"]*)(")|(<meta[^>]*content=")([^"]*)("[^>]*(?:name|property)="(?:description|og:title|og:description|twitter:title|twitter:description|og:image:alt)"[^>]*>)'
LD_KEYS = {'name', 'description', 'headline', 'text', 'alternativeHeadline', 'caption', 'abstract'}


def balanced(h, pat):
    m = re.search(pat, h)
    return (m.start(), block_end(h, m.start())) if m else None


def page_strings(h):
    """All translatable strings of a whole page (body without header/footer, head meta, JSON-LD, config)."""
    out = []
    t = re.search(r'<title>([^<]*)</title>', h)
    if t:
        out.append(t.group(1).strip())
    for m in re.finditer(META, h):
        out.append((m.group(2) if m.group(2) is not None else m.group(5)).strip())
    for m in re.finditer(r'<script[^>]*ld\+json[^>]*>(.*?)</script>', h, re.S):
        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k in LD_KEYS and isinstance(v, str):
                        out.append(v.strip())
                    else:
                        walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        try:
            walk(json.loads(m.group(1)))
        except Exception:
            pass
    c = re.search(r'window\.LTT_PAGE_CONFIG = (\{.*?\});', h)
    if c:
        cfg = json.loads(c.group(1))
        out += [v for k, v in cfg.items() if isinstance(v, str) and k.endswith('Label')]
        out += cfg.get('shortTitles', [])
    b = h[h.find('<body'):]
    for pat in (r'<header class="ltt-navbar"', r'<section class="footer-dark">'):
        r = balanced(b, pat)
        if r:
            b = b[:r[0]] + b[r[1]:]
    out += strings_of(b, ('alt', 'data-cap', 'aria-label', 'title', 'data-toc', 'placeholder'))
    return [x for x in out if translatable(x)]


def do_page(a):
    en = read(a.en)
    chrome = read(a.chrome_from)
    t = T(a.lang, 'page')
    h = en
    # header + footer from an existing page in the target language
    for pat in (r'<header class="ltt-navbar"', r'<section class="footer-dark">'):
        r_en, r_tr = balanced(h, pat), balanced(chrome, pat)
        if r_en and r_tr:
            blk = re.sub(r'\s*aria-current="page"', '', chrome[r_tr[0]:r_tr[1]]).replace('ltt-mega-item active', 'ltt-mega-item')
            h = h[:r_en[0]] + '\x02' + str(len(blk)) + '\x02' + h[r_en[1]:]
            h = h.replace('\x02' + str(len(blk)) + '\x02', blk, 1) if False else h.replace('\x02' + str(len(blk)) + '\x02', '\x03' + pat + '\x03', 1)
            locals().setdefault('_chrome', {})[pat] = blk
    chrome_blocks = locals().get('_chrome', {})
    head_end = h.find('<body')
    head, body = h[:head_end], h[head_end:]
    # body text
    body = t.html(body, ('alt', 'data-cap', 'aria-label', 'title', 'data-toc', 'placeholder'))
    body = localize_links(body, a.lang)
    for pat, blk in chrome_blocks.items():
        body = body.replace('\x03' + pat + '\x03', blk, 1)
    # head
    head = re.sub(r'<title>([^<]*)</title>', lambda m: '<title>' + t.tr(m.group(1)) + '</title>', head)
    head = re.sub(META, lambda m: (m.group(1) + t.tr(m.group(2)) + m.group(3)) if m.group(1) else (m.group(4) + t.tr(m.group(5)) + m.group(6)), head)
    new_url = SITE + '/' + a.tr.strip('/')
    old_url = SITE + '/' + a.en.strip('/')
    head = re.sub(r'(<html\b[^>]*\blang=")[^"]*(")', rf'\g<1>{a.lang}\2', head)
    h_all = head + body
    h_all = re.sub(r'(<html\b[^>]*\blang=")[^"]*(")', rf'\g<1>{a.lang}\2', h_all)
    h_all = re.sub(r'(<link[^>]*rel="canonical"[^>]*href=")[^"]*(")', lambda m: m.group(1) + new_url + m.group(2), h_all)
    h_all = re.sub(r'(<link[^>]*href=")[^"]*("[^>]*rel="canonical")', lambda m: m.group(1) + new_url + m.group(2), h_all)
    h_all = re.sub(r'(<meta[^>]*property="og:url"[^>]*content=")[^"]*(")', lambda m: m.group(1) + new_url + m.group(2), h_all)
    h_all = re.sub(r'(<meta[^>]*content=")[^"]*("[^>]*property="og:url")', lambda m: m.group(1) + new_url + m.group(2), h_all)
    h_all = re.sub(r'(<meta[^>]*property="og:locale"[^>]*content=")[^"]*(")', lambda m: m.group(1) + LANGS[a.lang].get('locale', a.lang) + m.group(2), h_all)
    hl = (f'<link href="{old_url}" hreflang="en" rel="alternate"/>\n<link href="{new_url}" hreflang="{a.lang}" rel="alternate"/>\n'
          f'<link href="{old_url}" hreflang="x-default" rel="alternate"/>')
    h_all = re.sub(r'(?:<link[^>]*hreflang="[^"]*"[^>]*>\s*)+', lambda m: hl + '\n', h_all, count=1)

    # JSON-LD
    def ld(m):
        try:
            data = json.loads(m.group(2))
        except Exception:
            return m.group(0)

        def walk(x):
            if isinstance(x, dict):
                for k, v in list(x.items()):
                    if k in LD_KEYS and isinstance(v, str):
                        x[k] = t.tr(v)
                    elif k in ('url', '@id', 'mainEntityOfPage', 'item') and isinstance(v, str) and v.startswith(old_url) and '#' not in v.replace(old_url, ''):
                        x[k] = v.replace(old_url, new_url)
                    elif k == 'inLanguage':
                        x[k] = a.lang
                    else:
                        walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(data)
        return m.group(1) + json.dumps(data, ensure_ascii=False, indent=2) + m.group(3)
    h_all = re.sub(r'(<script[^>]*ld\+json[^>]*>)(.*?)(</script>)', ld, h_all, flags=re.S)
    # page config
    c = re.search(r'window\.LTT_PAGE_CONFIG = (\{.*?\});', h_all)
    if c:
        cfg = json.loads(c.group(1))
        for k, v in cfg.items():
            if isinstance(v, str) and k.endswith('Label'):
                cfg[k] = t.tr(v)
        cfg['shortTitles'] = [t.tr(x) for x in cfg.get('shortTitles', [])]
        h_all = h_all[:c.start(1)] + json.dumps(cfg, ensure_ascii=False) + h_all[c.end(1):]

    def apply():
        os.makedirs(os.path.dirname(page(a.tr)), exist_ok=True)
        write(a.tr, h_all)
        # link the EN page back to the new page
        e = read(a.en)
        e = re.sub(r'(?:<link[^>]*hreflang="[^"]*"[^>]*>\s*)+', lambda m: hl + '\n', e, count=1)
        write(a.en, e)
    return finish(a, t, apply)


# ---------------------------------------------------------------- missing / learn / harvest
def collect(a, html):
    if a.what == 'cards':
        return [x for s, e in cards(html) for x in strings_of(html[s:e])]
    if a.what == 'sections':
        out = []
        for sid in a.ids.split(','):
            s, e = section(html, sid)
            out += strings_of(html[s:e])
        return out
    if a.what == 'page':
        return page_strings(html)
    if a.what == 'menus':
        i = html.find('<div class="dc-modal"')
        j = html.find('</template>', html.rfind('<template id="dc-menu-')) + len('</template>')
        b = html[i:j]
        return strings_of(b, ('aria-label', 'alt', 'title')) + [x for x in re.findall(r'data-(?:price|sub)="([^"]+)"', b) if translatable(x)]
    sys.exit('bad --what')


def do_missing(a):
    d = mem_load(a.lang)
    todo = [x for x in dict.fromkeys(collect(a, read(a.en))) if x not in d and f'{a.what}::{x}' not in d and not (ALT.match(x) and (ALT.match(x).group(2)[0].upper() + ALT.match(x).group(2)[1:]) in d)]
    os.makedirs(TODO_DIR, exist_ok=True)
    out = a.out or os.path.join(TODO_DIR, f"{a.en.strip('/').replace('/', '_')}.{a.what}.{a.lang}.txt")
    with open(out, 'w', encoding='utf-8') as f:
        for k, x in enumerate(todo):
            f.write(f'{k}|{x}\n')
    print(f'{len(todo)} string(s) to translate -> {out}')


def do_learn(a):
    todo = {int(l.split('|', 1)[0]): l.rstrip('\n').split('|', 1)[1] for l in open(a.todo, encoding='utf-8') if '|' in l}
    d = mem_load(a.lang)
    n = 0
    for l in open(a.done, encoding='utf-8'):
        if '|' in l:
            k, v = l.rstrip('\n').split('|', 1)
            if '—' in v:
                sys.exit(f'em dash in translation {k}: {v}')
            d[todo[int(k)]] = v
            n += 1
    mem_save(a.lang, d)
    print(f'learned {n} string(s) for {a.lang} (memory: {len(d)})')


def do_harvest(a):
    e, t = collect(a, read(a.en)), collect(a, read(a.tr))
    if len(e) != len(t):
        sys.exit(f'structure differs ({len(e)} EN vs {len(t)} translated strings); harvest needs identical markup')
    d = mem_load(a.lang)
    n = 0
    for x, y in zip(e, t):
        if x not in d and x != y:
            d[x] = y
            n += 1
    mem_save(a.lang, d)
    print(f'harvested {n} new string(s) for {a.lang} (memory: {len(d)})')


def do_sync(a):
    import copy
    P = json.load(open(os.path.join(HERE, 'presets.json'), encoding='utf-8'))[a.preset]
    langs = a.langs.split(',') if a.langs else list(P['pages'])
    bad = 0
    for lang in langs:
        tr = P['pages'][lang]
        steps = []
        if P.get('menus'):
            steps.append(('menus', {}))       # menus first: cards keep the menu buttons only when the modal exists
        if P.get('cards'):
            steps.append(('cards', {}))
        for sec in P.get('sections', []):
            steps.append(('sections', sec))
        for kind, extra in steps:
            b = copy.copy(a)
            b.lang, b.en, b.tr, b.ids, b.place = lang, P['en'], tr, extra.get('ids'), extra.get('place')
            rc = {'cards': do_cards, 'menus': do_menus, 'sections': do_sections}[kind](b)
            if rc:
                bad += 1
                print(f'  -> {lang} {kind}: missing strings, run: port.py missing --lang {lang} --en {P["en"]} --what {kind}' + (f' --ids {extra["ids"]}' if extra.get('ids') else ''))
    print('sync done, problems:', bad)
    return 1 if bad else 0


def finish(a, t, apply):
    miss = list(dict.fromkeys(t.missing))
    if miss:
        print(f'[{a.lang}] {len(miss)} untranslated string(s), e.g. {miss[:5]}\n  run: port.py missing ... then learn')
        if a.check or not a.force:
            return 1
    if a.check:
        print('[%s] ok, nothing missing' % a.lang)
        return 0
    apply()
    print('ok', a.tr)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('cmd', choices=['missing', 'learn', 'harvest', 'cards', 'sections', 'menus', 'sync', 'page'])
    ap.add_argument('--chrome-from')
    ap.add_argument('preset', nargs='?')
    ap.add_argument('--langs')
    for x in ('--lang', '--en', '--tr', '--what', '--ids', '--place', '--out', '--todo', '--done'):
        ap.add_argument(x)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--force', action='store_true', help='apply even with untranslated strings (they stay English)')
    a = ap.parse_args()
    return {'missing': do_missing, 'learn': do_learn, 'harvest': do_harvest,
            'cards': do_cards, 'sections': do_sections, 'menus': do_menus, 'sync': do_sync, 'page': do_page}[a.cmd](a) or 0


if __name__ == '__main__':
    sys.exit(main())
