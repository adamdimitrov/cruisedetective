#!/usr/bin/env python3
"""Keep the site chrome (menu, mobile drawer, footer) identical on every page.

Every published page (sitemap.xml) gets the header and footer of its language's
MASTER page. To change the menu or footer site-wide, edit it on the master page
for that language, then run:

    python3 scripts/sync_layout.py            # write changes
    python3 scripts/sync_layout.py --check    # report only, exit 1 on drift

What is synced on each page:
  * <header class="ltt-navbar"> (desktop menu, mega menu, language switcher,
    mobile drawer). Per page it keeps: the active menu item, and the language
    switcher links, which point at the page's own hreflang alternates.
  * the footer (<footer class="footer-dark">, or the old Webflow
    <section class="footer-dark"> / ad-style <footer class="main-footer">,
    which are replaced). Pages with no footer get one.
  * the inline <style id="ltt-nav-styles"> / <script id="ltt-nav-script"> blocks
    where a page carries them; pages without any nav styling get them.

It also rebuilds the site search index (search/<lang>.json, see
scripts/search_index.py) that the menu's search button (/js/site-search.js) uses.

--check also fails on:
  * floating bar / table-of-contents links (#anchor) that point at nothing on the page
  * a floating bar CTA whose booking product does not appear anywhere else on the page
  * an index.html that is neither in sitemap.xml, nor an ad landing page
    (AD_LANDINGS), so stale copies cannot quietly stay live
"""
import argparse
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search_index  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.thecruisedetective.com"

MASTERS = {
    "en": "seine-river-cruises-paris/index.html",
    "fr": "fr/meilleures-croisieres-seine-paris/index.html",
    "de": "de/besten-bootsfahrten-seine-paris/index.html",
    "es": "es/mejores-cruceros-sena-paris/index.html",
    "it": "it/migliori-crociere-senna-parigi/index.html",
    "nl": "nl/beste-boottochten-seine-parijs/index.html",
    "pl": "pl/najlepsze-rejsy-po-sekwanie-paryz/index.html",
    "ro": "ro/cele-mai-bune-croaziere-sena-paris/index.html",
    "ja": "ja/パリのベスト-セーヌ川クルーズ/index.html",
}
HOMES = {lg: ("/" if lg == "en" else f"/{lg}") for lg in MASTERS}

# Google Ads landing pages: deliberately minimal chrome, not in the sitemap.
AD_LANDINGS = {
    "amsterdam-comparison", "bateaux-parisiens-landing", "dinner-advertorial",
    "dinner-comparison", "paris-couples-pass", "paris-dinner-cruise",
    "paris-family-compare", "paris-family-cruise", "paris-family-pass",
    "paris-fast-booking", "romantic-quiz", "seine-advertorial",
    "seine-comparison", "seine-deal",
}
SKIP_DIRS = {"node_modules", ".git", ".claude", "test", "reports", "menu-lab", "review-lab"}

PAT_HEADER = re.compile(r'<header[^>]*class="ltt-navbar".*?</header>', re.S)
PAT_NAV_CSS = re.compile(r'<style id="ltt-nav-styles">.*?</style>', re.S)
PAT_NAV_JS = re.compile(r'<script id="ltt-nav-script">.*?</script>', re.S)
PAT_LANG_CSS = re.compile(r'<style id="ltt-language-switcher-styles">.*?</style>', re.S)
PAT_LANG_JS = re.compile(r'<script id="ltt-language-switcher-logic">.*?</script>', re.S)
FOOTER_STARTS = [
    re.compile(r'<footer class="footer-dark"[^>]*>'),
    re.compile(r'<section class="footer-dark"[^>]*>'),
    re.compile(r'<footer class="main-footer"[^>]*>'),
    re.compile(r'<div class="footer-section"[^>]*>'),  # bare Webflow footer (old contact pages)
]


def in_template(s, i):
    return s.rfind("<template", 0, i) > s.rfind("</template>", 0, i)
ACTIVE_CLASSES = ("ltt-mega-item", "ltt-nav-link", "ltt-mobile-link")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def norm_path(p):
    p = urllib.parse.unquote(p.split("#")[0].split("?")[0])
    if p.startswith(SITE):
        p = p[len(SITE):]
    return "/" + p.strip("/") if p.strip("/") else "/"


def file_to_path(f):
    d = os.path.dirname(f)
    return "/" + d if d else "/"


def sitemap_files():
    out = []
    for loc in re.findall(r"<loc>([^<]*)</loc>", read("sitemap.xml")):
        p = norm_path(loc)
        f = "index.html" if p == "/" else p.lstrip("/") + "/index.html"
        if os.path.exists(os.path.join(ROOT, f)) and f not in out:
            out.append(f)
    return out


def page_lang(s):
    m = re.search(r'<html[^>]*\blang="([a-zA-Z-]+)"', s)
    return m.group(1).split("-")[0].lower() if m else None


def element_end(s, start, tag):
    """Index just past the tag that closes the element opened at `start`."""
    depth, i = 0, start
    pat = re.compile(rf"<(/?){tag}\b[^>]*>", re.I)
    for m in pat.finditer(s, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.end()
        i = m.end()
    raise ValueError(f"unclosed <{tag}>")


def find_footer(s):
    for pat in FOOTER_STARTS:
        m = pat.search(s)
        if m:
            tag = re.match(r"<(\w+)", m.group()).group(1)
            return m.start(), element_end(s, m.start(), tag)
    return None


# ---------------------------------------------------------------- per-page data
def deactivate(html):
    html = re.sub(r'\s+aria-current="(?:page|true)"', "", html)

    def fix_cls(m):
        toks = [t for t in m.group(1).split() if t not in ("active", "w--current")]
        return f'class="{" ".join(toks)}"'
    return re.sub(r'class="([^"]*\b(?:ltt-mega-item|ltt-nav-link|ltt-mobile-link|ltt-dropdown-btn|footer-link-3)\b[^"]*)"', fix_cls, html)


def activate(html, path, footer=False):
    def on(m):
        tag = m.group(0)
        href = re.search(r'href="([^"]*)"', tag)
        cls = re.search(r'class="([^"]*)"', tag)
        if not href or not cls or norm_path(href.group(1)) != path or href.group(1).startswith("#"):
            return tag
        toks = cls.group(1).split()
        if footer and "footer-link-3" in toks:
            toks.append("w--current")
        elif not footer and any(c in toks for c in ACTIVE_CLASSES):
            toks.append("active")
        else:
            return tag
        tag = tag.replace(cls.group(0), f'class="{" ".join(toks)}"', 1)
        return tag.replace("<a ", '<a aria-current="page" ', 1)
    html = re.sub(r"<a [^>]*>", on, html)
    if not footer and re.search(r'class="ltt-mega-item active"', html):
        html = re.sub(r'<button ([^>]*)class="ltt-nav-link ltt-dropdown-btn"',
                      r'<button aria-current="true" \1class="ltt-nav-link ltt-dropdown-btn active"', html, count=1)
    return html


def alternates(s):
    out = {}
    for tag in re.findall(r"<link [^>]*hreflang=[^>]*>", s):
        lg = re.search(r'hreflang="([^"]+)"', tag).group(1)
        href = re.search(r'href="([^"]+)"', tag)
        if href and lg != "x-default":
            out[lg.split("-")[0].lower()] = norm_path(href.group(1))
    return out


def point_switcher(header, alt):
    def fix(m):
        tag, lg = m.group(0), m.group(2)
        target = alt.get(lg, HOMES.get(lg, "/"))
        return re.sub(r'href="[^"]*"', f'href="{target}"', tag, count=1)
    return re.sub(r'<a [^>]*data-(m-)?lang="([a-z]+)"[^>]*>', fix, header)


def build_header(master_header, page, path):
    return point_switcher(activate(deactivate(master_header), path), alternates(page))


def build_footer(master_footer, path):
    return activate(deactivate(master_footer), path, footer=True)


# ---------------------------------------------------------------------- sync
def replace_block(s, pat, new):
    m = pat.search(s)
    if not m:
        return s
    return s[:m.start()] + new + s[m.end():]


def sync_page(s, master, path):
    changed = []

    m_hdr = PAT_HEADER.search(master).group()
    if not PAT_HEADER.search(s):
        raise ValueError("no <header class=\"ltt-navbar\">")
    s2 = replace_block(s, PAT_HEADER, build_header(m_hdr, s, path))
    if s2 != s:
        changed.append("header")
    s = s2

    ms, me = find_footer(master)
    new_footer = build_footer(master[ms:me], path)
    span = find_footer(s)
    if span and in_template(s, span[0]):
        # Footer sits inside a shadow-DOM <template> (privacy, terms), where the
        # site CSS cannot reach it. Move it out, right after the shadow host.
        s2 = s[:span[0]] + s[span[1]:]
        t_end = s2.index("</template>", span[0])
        host_end = s2.index("</div>", t_end) + len("</div>")
        s2 = s2[:host_end] + "\n" + new_footer + s2[host_end:]
    elif span:
        s2 = s[:span[0]] + new_footer + s[span[1]:]
    elif "</main>" in s:
        i = s.rindex("</main>") + len("</main>")
        s2 = s[:i] + "\n" + new_footer + s[i:]
    else:
        s2 = s.replace("</body>", new_footer + "\n</body>", 1)
    if s2 != s:
        changed.append("footer")
    s = s2

    css = PAT_NAV_CSS.search(master).group()
    js = PAT_NAV_JS.search(master).group()
    if PAT_NAV_CSS.search(s):
        s2 = replace_block(s, PAT_NAV_CSS, css)
    elif "/css/editorial-luxury.css" not in s:
        # No shared stylesheet: the master nav CSS goes last in <head>, so it
        # wins over any page-local nav rules.
        s2 = s.replace("</head>", css + "\n</head>", 1)
    else:
        s2 = s
    if s2 != s:
        changed.append("nav-css")
    s = s2
    if PAT_NAV_JS.search(s):
        s2 = replace_block(s, PAT_NAV_JS, js)
    elif "/js/ltt-nav.js" not in s and not re.search(r"getElementById\(['\"]lttNavToggle['\"]\)", s):
        s2 = s.replace("</header>", "</header>\n" + js, 1)
    else:
        s2 = s
    if s2 != s:
        changed.append("nav-js")
    s = s2
    # The language switcher in the header needs its styles and toggle logic.
    for pat in (PAT_LANG_CSS, PAT_LANG_JS):
        if not pat.search(s):
            block = pat.search(master).group()
            s = s.replace("</head>", block + "\n</head>", 1) if pat is PAT_LANG_CSS else s.replace("</body>", block + "\n</body>", 1)
            if "lang-switcher" not in changed:
                changed.append("lang-switcher")
    return s, changed


# --------------------------------------------------------------------- checks
def bar_problems(s):
    problems = []
    ids = set(re.findall(r'\bid="([^"]+)"', s))
    for cls in ("hybrid-sticky-bar", "hybrid-sheet", "sticky-bar"):
        m = re.search(rf'<(div|aside|nav|section)[^>]*class="(?:[^"]*\s)?{cls}(?:\s[^"]*)?"', s)
        if not m:
            continue
        end = element_end(s, m.start(), m.group(1))
        block = s[m.start():end]
        for a in re.findall(r'href="#([^"]+)"', block):
            a = urllib.parse.unquote(a)
            if a and a not in ids and a != "top":
                problems.append(f"{cls}: link #{a} points at nothing on the page")
        rest = s[:m.start()] + s[end:]
        for href in re.findall(r'href="(https://[^"]+)"', block):
            key = product_key(href)
            if key and key not in rest:
                problems.append(f"{cls}: CTA product {key} is not on the page")
    return problems


def product_key(href):
    for pat in (r"(p\d{6,})/", r"(t\d{4,})/", r"flow=(\d+)", r"(p\d{6,})\b"):
        m = re.search(pat, href)
        if m:
            return m.group(1)
    return None


def orphan_pages(published):
    orphans = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)
        top = rel.split(os.sep)[0]
        if rel != "." and (top in SKIP_DIRS or top.startswith(".")):
            dirnames[:] = []
            continue
        if "index.html" not in filenames:
            continue
        f = "index.html" if rel == "." else f"{rel}/index.html"
        if f in published or top in AD_LANDINGS:
            continue
        orphans.append(f)
    return sorted(orphans)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report drift and problems, write nothing")
    args = ap.parse_args()

    masters = {lg: read(f) for lg, f in MASTERS.items()}
    published = sitemap_files()
    drift, errors, problems = 0, [], []

    for f in published:
        s = read(f)
        lg = page_lang(s)
        problems += [f"{f}: {p}" for p in bar_problems(s)]
        for what, n in (("menu", len(PAT_HEADER.findall(s))), ("footer", s.count('class="footer-section"'))):
            if n > 1:
                problems.append(f"{f}: {n} {what}s on the page, expected 1")
        if lg not in masters:
            errors.append(f"{f}: no master for language '{lg}'")
            continue
        if f == MASTERS[lg]:
            continue
        try:
            new, changed = sync_page(s, masters[lg], file_to_path(f))
        except ValueError as e:
            errors.append(f"{f}: {e}")
            continue
        if changed:
            drift += 1
            print(f"{'out of sync' if args.check else 'updated'}: {f} ({', '.join(changed)})")
            if not args.check:
                with open(os.path.join(ROOT, f), "w", encoding="utf-8") as fh:
                    fh.write(new)

    # Site search index (search/<lang>.json), rebuilt from the published pages.
    pages = []
    for f in published:
        s = read(f)
        lg = page_lang(s)
        if lg in masters:
            pages.append((lg, file_to_path(f), s))
    for lg, text in search_index.build(pages).items():
        rel = f"search/{lg}.json"
        path = os.path.join(ROOT, rel)
        old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old != text:
            drift += 1
            print(f"{'out of date' if args.check else 'rebuilt'}: {rel}")
            if not args.check:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(text)

    orphans = orphan_pages(set(published))
    for o in orphans:
        problems.append(f"{o}: page that is not in sitemap.xml (add a redirect in vercel.json and delete it, or add it to the sitemap)")
    for p in problems:
        print("PROBLEM", p)
    for e in errors:
        print("ERROR", e)
    print(f"{len(published)} published pages, {drift} {'out of sync' if args.check else 'updated'}, "
          f"{len(problems)} problem(s), {len(errors)} error(s)")
    if errors or problems or (args.check and drift):
        sys.exit(1)


if __name__ == "__main__":
    main()
