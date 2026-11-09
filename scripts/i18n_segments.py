#!/usr/bin/env python3
"""
Find and replace leftover English text on localized pages.

  python3 scripts/i18n_segments.py extract <lang>   -> i18n/<lang>.todo.json
  python3 scripts/i18n_segments.py apply <lang>     <- i18n/<lang>.json

A "segment" is the raw inner HTML of the outermost text element (li, p, h1-h4,
span, td, ...) whose visible text is English and which contains no block-level
children. Inline markup (<strong>, <a>, <br>...) is kept inside the segment, so
translations must preserve it.

Covered sources per page:
  * body HTML (outside <script>/<style>)
  * the article injected via `content.innerHTML = "..."` on the
    seine-river-cruise-review pages (JSON-decoded, translated, re-encoded)
  * <title>, meta description / og:* / twitter:* content attributes

`apply` replaces exact raw segments only, so it is idempotent and never touches
anything that was not extracted.
"""

import glob
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "i18n")

EN = set("""the and of to is are was were with for this that you your our we it on in at be by from have has
not but or as an they their which when what will can more than all just only about if so there been
it's you'll you're don't i my me also into very most some any while during each per""".split())
STOP = {
    "pl": set("i w z na do po nie jest się że jak od dla przez oraz jego ich być może bardzo tylko czy już a o".split()),
    "ja": set(),
}

TAGS = "li|p|h1|h2|h3|h4|h5|span|td|th|figcaption|blockquote|label|button|summary|strong|em|b|a|div|small"
BLOCK = re.compile(r"<(?:li|p|div|h[1-6]|ul|ol|table|tr|section|article|header|footer|img|figure|iframe|script|style)\b", re.I)
# one regex per tag: a single alternation would consume outer elements and hide inner ones
ELEMS = [re.compile(r"<(%s)\b[^>]*>((?:(?!<\1\b|</\1>).)*?)</\1>" % t, re.S | re.I) for t in TAGS.split("|")]
SKIP_REGION = re.compile(r"<(script|style)\b.*?</\1>", re.S | re.I)
INJECT = re.compile(r'(content\.innerHTML = )("(?:[^"\\]|\\.)*")')
META = re.compile(r'(<title>)([^<]+)(</title>)|(<meta content=")([^"]+)("\s+(?:name|property)="(?:description|og:title|og:description|twitter:title|twitter:description)")')

DATE_LOCALE = {"pl": "pl-PL", "ja": "ja-JP", "de": "de-DE", "fr": "fr-FR", "es": "es-ES",
               "it": "it-IT", "nl": "nl-NL", "ro": "ro-RO"}
CJK = re.compile(r"[぀-ヿ一-鿿]")


def text_of(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def is_english(text, lang):
    words = re.findall(r"[a-zA-Z']+", text.lower())
    if len(words) < 4:
        return False
    if lang == "ja" and len(CJK.findall(text)) >= 3:
        return False
    en = sum(w in EN for w in words)
    loc = sum(w in STOP.get(lang, ()) for w in words)
    if re.search(r"[ąćęłńóśźż]", text.lower()) and lang == "pl":
        loc += 3
    return en >= 2 and en / len(words) >= 0.15 and en > loc


ALT = re.compile(r'alt="([^"]+)"')
NO_TRANSLATE_ALT = {"Adam Dimitrov", "The Cruise Detective Logo", "Bateaux Parisiens Boat"}


def segments(doc, lang, all_text=False):
    """Outermost English leaf-ish elements in an HTML string -> list of raw inner HTML.

    all_text=True (used for the injected review article, which is entirely
    English) takes every text element, not just ones that look like English
    sentences, so headings, buttons and badges are included too."""
    skip = [m.span() for m in SKIP_REGION.finditer(doc)]
    inside_skip = lambda a: any(s <= a < e for s, e in skip)
    found = []
    for m in (m for rx in ELEMS for m in rx.finditer(doc)):
        inner = m.group(2)
        if inside_skip(m.start()) or BLOCK.search(inner) or not inner.strip():
            continue
        txt = text_of(inner)
        if (all_text and re.search(r"[A-Za-z]{2,}", txt) and not CJK.search(txt)
                and not re.search(r"[ąćęłńóśźż]", txt.lower())) or is_english(txt, lang):
            found.append((m.start(2), m.end(2), inner.strip()))
    # ELEM.finditer is non-overlapping per tag type only via alternation order; drop nested ones
    found.sort(key=lambda x: (x[0], -x[1]))
    out, last_end = [], -1
    for a, b, s in found:
        if a >= last_end:
            out.append(s)
            last_end = b
    return out


def pages(lang):
    return sorted(glob.glob(os.path.join(ROOT, lang, "**", "index.html"), recursive=True))


def page_sources(raw):
    """Yield (kind, text) pieces to scan."""
    yield "body", raw
    m = INJECT.search(raw)
    if m:
        yield "inject", json.loads(m.group(2))


def extract(lang):
    todo, where = {}, {}
    for p in pages(lang):
        raw = open(p, encoding="utf-8").read()
        rel = os.path.relpath(p, ROOT)
        for kind, doc in page_sources(raw):
            for s in segments(doc, lang, all_text=(kind == "inject")):
                todo.setdefault(s, "")
                where.setdefault(s, set()).add(rel)
            if kind == "inject":
                for a in ALT.findall(doc):
                    if a not in NO_TRANSLATE_ALT:
                        key = f'alt="{a}"'
                        todo.setdefault(key, "")
                        where.setdefault(key, set()).add(rel + " (alt)")
        for m in META.finditer(raw):
            t = m.group(2) or m.group(5)
            if is_english(html.unescape(t), lang):
                todo.setdefault(t, "")
                where.setdefault(t, set()).add(rel + " (meta)")
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{lang}.todo.json")
    items = [{"en": s, "pages": sorted(where[s]), lang: ""} for s in todo]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=1)
    chars = sum(len(text_of(s)) for s in todo)
    print(f"{lang}: {len(todo)} segments, ~{chars} chars of text -> {os.path.relpath(path, ROOT)}")


def apply(lang):
    path = os.path.join(OUT, f"{lang}.json")
    tr = {k: v for k, v in json.load(open(path, encoding="utf-8")).items() if v and v != k}
    keys = sorted(tr, key=len, reverse=True)
    total = 0
    for p in pages(lang):
        raw = open(p, encoding="utf-8").read()
        new = raw

        def sub_doc(doc, in_attr=False):
            n = 0
            for k in keys:
                if k in doc:
                    v = tr[k]
                    if in_attr:
                        v = v.replace('"', "&quot;")
                    n += doc.count(k)
                    doc = doc.replace(k, v)
            return doc, n

        # injected article (JSON string) first, then the rest of the page
        m = INJECT.search(new)
        if m:
            art, n1 = sub_doc(json.loads(m.group(2)))
            total += n1
            new = new[:m.start(2)] + json.dumps(art, ensure_ascii=False) + new[m.end(2):]
        # body: replace only between tags (">seg<") to stay out of scripts/attrs
        for k in keys:
            pat = re.compile(r"(>\s*)" + re.escape(k) + r"(\s*</)")
            new, n = pat.subn(lambda mm: mm.group(1) + tr[k] + mm.group(2), new)
            total += n

        def meta_repl(mm):
            if mm.group(1):
                t = mm.group(2)
                return mm.group(1) + tr.get(t, t) + mm.group(3)
            t = mm.group(5)
            return mm.group(4) + tr.get(t, t).replace('"', "&quot;") + mm.group(6)
        new = META.sub(meta_repl, new)
        # injected article date: format it in the page's language
        new = new.replace("toLocaleDateString('en-US', options)",
                          f"toLocaleDateString('{DATE_LOCALE.get(lang, lang)}', options)")
        if new != raw:
            with open(p, "w", encoding="utf-8") as f:
                f.write(new)
    print(f"{lang}: {total} replacements")


if __name__ == "__main__":
    {"extract": extract, "apply": apply}[sys.argv[1]](sys.argv[2])
