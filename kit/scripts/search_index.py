"""Build the per-language site search index used by /js/site-search.js.

Writes search/<lang>.json: one entry per published page with its title,
meta description and section headings (with anchor ids, so results can jump
straight to a section). Called by scripts/sync_layout.py; --check there fails
when an index is stale.
"""
import html
import json
import re

MAX_HEADINGS = 60

STRIP_BLOCKS = re.compile(
    r"<(script|style|template|header|footer|nav|noscript)\b.*?</\1>", re.S | re.I)
HEADING = re.compile(r"<(h[23])\b([^>]*)>(.*?)</\1>", re.S | re.I)


def clean(text):
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"[​ \s]+", " ", text).strip()
    return text


def page_entry(s, url):
    title = re.search(r"<h1\b[^>]*>(.*?)</h1>", s, re.S | re.I)
    title = clean(title.group(1)) if title else ""
    if not title:
        t = re.search(r"<title>(.*?)</title>", s, re.S | re.I)
        title = clean(t.group(1)) if t else url
    desc = re.search(r'<meta\s+(?:content="([^"]*)"\s+name="description"|name="description"\s+content="([^"]*)")', s)
    desc = clean((desc.group(1) or desc.group(2) or "") if desc else "")
    body = STRIP_BLOCKS.sub(" ", s)
    heads, seen = [], set()
    for m in HEADING.finditer(body):
        text = clean(m.group(3))[:110]
        if not text or text.lower() in seen or (len(text) <= 14 and text.endswith(":")):
            continue
        seen.add(text.lower())
        hid = re.search(r'\bid="([^"]+)"', m.group(2))
        heads.append([text, hid.group(1) if hid else ""])
        if len(heads) >= MAX_HEADINGS:
            break
    return {"u": url, "t": title, "d": desc[:220], "h": heads}


def build(pages):
    """pages: iterable of (lang, url, html). Returns {lang: json_text}."""
    by_lang = {}
    for lang, url, s in pages:
        by_lang.setdefault(lang, []).append(page_entry(s, url))
    return {lg: json.dumps(sorted(v, key=lambda e: e["u"]), ensure_ascii=False, separators=(",", ":")) + "\n"
            for lg, v in by_lang.items()}
