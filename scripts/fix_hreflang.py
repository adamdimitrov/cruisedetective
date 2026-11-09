#!/usr/bin/env python3
"""
Rebuild hreflang annotations for every live page and the sitemap.

Source of truth: the translation groups in sitemap.xml (one <url> block per
page, with its xhtml:link alternates). For each group:
  * every member page gets exactly the same hreflang set: the 9 live languages
    that actually exist for that page + x-default (-> English),
  * all stale alternates (the 24 retired languages that 308 to the homepage)
    are removed,
  * hreflang/canonical URLs use the final, non-redirecting form
    (root keeps "/", everything else has no trailing slash).

Pages whose canonical points elsewhere (e.g. /seine-river-cruises-paris-1,
/seine-river-cruises-paris-ltt) get no hreflang and are dropped from the
sitemap, since hreflang on non-canonical URLs is ignored/conflicting.

Idempotent: safe to re-run.
"""

import os
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = "https://www.thecruisedetective.com"
LANGS = ["en", "fr", "de", "es", "it", "nl", "pl", "ro", "ja"]
SITEMAP = os.path.join(ROOT, "sitemap.xml")

HREFLANG_TAG = re.compile(r'(?:^[ \t]*)?<link\b[^>]*\bhreflang="[^"]*"[^>]*>[ \t]*\n?', re.M)
# whitespace-only lines directly after the canonical tag (left over from removed tags)
BLANK_AFTER = re.compile(r'\A(?:\n[ \t]*(?=\n))+')
CANONICAL_TAG = re.compile(r'<link\b[^>]*\brel="canonical"[^>]*>')


def norm(url):
    path = unquote(urlparse(url).path).strip("/")
    return f"{BASE}/{path}" if path else f"{BASE}/"


def file_for(url):
    path = unquote(urlparse(url).path).strip("/")
    return os.path.join(ROOT, path, "index.html") if path else os.path.join(ROOT, "index.html")


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def canonical_of(html):
    m = CANONICAL_TAG.search(html)
    if not m:
        return None
    h = re.search(r'href="([^"]+)"', m.group(0))
    return h.group(1) if h else None


def fix_canonical(html, url):
    """Point a self-referencing canonical at the non-redirecting URL form."""
    def repl(m):
        tag = m.group(0)
        href = re.search(r'href="([^"]+)"', tag).group(1)
        if norm(href) == url and href != url:
            tag = tag.replace(f'href="{href}"', f'href="{url}"')
        return tag
    return CANONICAL_TAG.sub(repl, html, count=1)


def hreflang_block(group, indent):
    lines = [f'<link href="{group[l]}" hreflang="{l}" rel="alternate"/>' for l in LANGS if l in group]
    lines.append(f'<link href="{group["en"]}" hreflang="x-default" rel="alternate"/>')
    return ("\n" + indent).join(lines)


def load_groups():
    sm = read(SITEMAP)
    groups, lastmod = {}, {}
    for blk in re.findall(r"<url>(.*?)</url>", sm, re.S):
        alts = re.findall(r'hreflang="([^"]+)" href="([^"]+)"', blk)
        g = {}
        for lang, href in alts:
            lang = "en" if lang.lower() in ("en", "en-us") else lang.lower()
            if lang in LANGS:
                g[lang] = norm(href)
        loc = norm(re.search(r"<loc>([^<]+)", blk).group(1))
        if not g:
            g = {"en": loc}
        lm = re.search(r"<lastmod>([^<]+)", blk)
        if lm:
            lastmod[loc] = lm.group(1)
        groups[tuple(sorted(g.items()))] = g
    return list(groups.values()), lastmod


def main():
    groups, lastmod = load_groups()
    live_groups, changed = [], []

    for g in groups:
        members = {}
        for lang, url in g.items():
            p = file_for(url)
            if not os.path.exists(p):
                sys.exit(f"missing file for {url}: {p}")
            members[lang] = (url, p)
        # A group is canonical only if every member's canonical is itself
        canon_ok = all(norm(canonical_of(read(p)) or "") == url for url, p in members.values())
        if canon_ok:
            live_groups.append(g)
        for lang, (url, p) in members.items():
            html = read(p)
            new = HREFLANG_TAG.sub("", html)
            if canon_ok:
                new = fix_canonical(new, url)
                m = CANONICAL_TAG.search(new)
                line_start = new.rfind("\n", 0, m.start()) + 1
                indent = re.match(r"[ \t]*", new[line_start:]).group(0)
                own_line = new[line_start:m.start()].strip() == ""
                block = hreflang_block(g, indent if own_line else "")
                sep = ("\n" + indent) if own_line else "\n"
                new = new[:m.end()] + sep + block + BLANK_AFTER.sub("", new[m.end():])
            if new != html:
                write(p, new)
                changed.append(os.path.relpath(p, ROOT))

    # Other pages that canonicalise elsewhere but still carry hreflang
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if not d.startswith((".", "node_modules", "test", "scripts", "reports"))]
        if "index.html" not in files:
            continue
        p = os.path.join(dirpath, "index.html")
        rel = os.path.relpath(p, ROOT)
        url = norm(BASE + "/" + os.path.relpath(dirpath, ROOT).replace(os.sep, "/").lstrip("."))
        html = read(p)
        c = canonical_of(html)
        if 'hreflang="' in html and c and norm(c) != url:
            write(p, HREFLANG_TAG.sub("", html))
            changed.append(rel)

    # Rebuild sitemap from the canonical groups only
    out = ["<?xml version='1.0' encoding='utf-8'?>",
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for lang in LANGS:
        for g in live_groups:
            if lang not in g:
                continue
            url = g[lang]
            out.append("  <url>")
            out.append(f"    <loc>{url}</loc>")
            lm = lastmod.get(url) or lastmod.get(url.rstrip("/"))
            if lm:
                out.append(f"    <lastmod>{lm}</lastmod>")
            for l in LANGS:
                if l in g:
                    out.append(f'    <xhtml:link rel="alternate" hreflang="{l}" href="{g[l]}" />')
            out.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{g["en"]}" />')
            out.append("  </url>")
    out.append("</urlset>")
    write(SITEMAP, "\n".join(out) + "\n")

    print(f"{len(live_groups)} canonical groups, {sum(len(g) for g in live_groups)} sitemap URLs")
    print(f"{len(changed)} HTML files updated")


if __name__ == "__main__":
    main()
