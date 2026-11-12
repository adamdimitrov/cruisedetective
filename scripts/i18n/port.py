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
    ap.add_argument('cmd', choices=['missing', 'learn', 'harvest', 'cards', 'sections', 'menus', 'sync'])
    ap.add_argument('preset', nargs='?')
    ap.add_argument('--langs')
    for x in ('--lang', '--en', '--tr', '--what', '--ids', '--place', '--out', '--todo', '--done'):
        ap.add_argument(x)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--force', action='store_true', help='apply even with untranslated strings (they stay English)')
    a = ap.parse_args()
    return {'missing': do_missing, 'learn': do_learn, 'harvest': do_harvest,
            'cards': do_cards, 'sections': do_sections, 'menus': do_menus, 'sync': do_sync}[a.cmd](a) or 0


if __name__ == '__main__':
    sys.exit(main())
