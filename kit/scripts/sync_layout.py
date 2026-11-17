#!/usr/bin/env python3
"""Keep the site chrome (menu, mobile drawer, footer) identical on every page.

Shared kit script (kit/scripts/sync_layout.py); settings live in each site's
scripts/layout_config.json. Every published page (sitemap.xml)
gets the header and footer of its language's MASTER page. To change the menu or
footer site-wide, edit it on the master page of that language, then run:

    python3 scripts/sync_layout.py            # write changes
    python3 scripts/sync_layout.py --check    # report only, exit 1 on drift

What is synced on each page:
  * <header class="ltt-navbar"> (desktop menu, mega menu, language switcher,
    search button, mobile drawer). Per page it keeps the active menu item, and
    points the language switcher at the page's own hreflang alternates.
  * the footer (any of the old footer variants listed in the config is
    replaced; pages without a footer get one).
  * the style/script blocks listed under "sync_blocks" (nav CSS/JS, language
    switcher, footer CSS): replaced where present, added where missing.
It also rebuilds the site search index (search/<lang>.json, see
scripts/search_index.py) that the menu's search button (/js/site-search.js) uses.

--check also fails on:
  * floating bar / table-of-contents links (#anchor) that point at nothing on the page
  * a floating bar CTA whose booking product does not appear anywhere else on the page
  * more than one menu or footer on a page
  * an .html file that is neither published (sitemap.xml) nor listed in
    "unlisted_ok", so stale copies cannot quietly stay live
"""
import argparse
import fnmatch
import json
import os
import re
import sys
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checks"))
import search_index  # noqa: E402
import fix_affiliate_rel  # noqa: E402
from sitecfg import ROOT  # noqa: E402

with open(os.path.join(ROOT, "scripts", "layout_config.json"), encoding="utf-8") as _fh:
    CFG = json.load(_fh)

SITE = CFG["site"].rstrip("/")
DEFAULT_LANG = CFG.get("default_lang", "en")
MASTERS = CFG["masters"]
HOMES = {lg: ("/" if lg == DEFAULT_LANG else f"/{lg}") for lg in MASTERS}
UNLISTED_OK = CFG.get("unlisted_ok", [])
SKIP_DIRS = set(CFG.get("skip_dirs", [])) | {"node_modules", ".git", ".claude", ".github", "scripts", "search"}

PAT_HEADER = re.compile(r'<header[^>]*class="[^"]*\bltt-navbar\b[^"]*".*?</header>', re.S)
FOOTER_STARTS = [re.compile(p) for p in CFG["footer_starts"]]
FOOTER_MARKER = CFG["footer_marker"]
ACTIVE_CLASSES = ("ltt-mega-item", "ltt-mega-subitem", "ltt-nav-link", "ltt-mobile-link")
FOOTER_LINK_CLASS = CFG.get("footer_link_class", "footer-link-3")


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def norm_path(p):
    p = p.split("#")[0].split("?")[0]
    if p.startswith(SITE):
        p = p[len(SITE):]
    elif re.match(r"https?://", p):
        p = re.sub(r"^https?://[^/]+", "", p)
    p = urllib.parse.unquote(p).strip("/")
    p = re.sub(r"(/index)?\.html$", "", p)
    return "/" + p if p and p != "index" else "/"


def rewrites():
    try:
        cfg = json.loads(read("vercel.json"))
    except (OSError, ValueError):
        return {}
    return {r["source"]: r["destination"] for r in cfg.get("rewrites", []) if ":" not in r["source"]}


def url_to_file(path, rw):
    for p in (path, rw.get(path)):
        if not p:
            continue
        p = urllib.parse.unquote(p).rstrip("/") or "/"
        cands = ["index.html"] if p == "/" else [p.lstrip("/") + ".html", p.lstrip("/") + "/index.html", p.lstrip("/")]
        for c in cands:
            if c.endswith(".html") and os.path.isfile(os.path.join(ROOT, c)):
                return c
    return None


def published_pages():
    """[(path, file)] for every sitemap URL that maps to a file, in sitemap order."""
    rw, out, seen = rewrites(), [], set()
    for loc in re.findall(r"<loc>([^<]*)</loc>", read("sitemap.xml")):
        path = norm_path(loc.strip())
        f = url_to_file(path, rw)
        if f and f not in seen:
            seen.add(f)
            out.append((path, f))
    return out


def page_lang(s):
    m = re.search(r'<html[^>]*\blang="([a-zA-Z-]+)"', s)
    return m.group(1).split("-")[0].lower() if m else None


def element_end(s, start, tag):
    depth = 0
    pat = re.compile(rf"<(/?){tag}\b[^>]*>", re.I)
    for m in pat.finditer(s, start):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return m.end()
    raise ValueError(f"unclosed <{tag}>")


def find_footer(s):
    for pat in FOOTER_STARTS:
        m = pat.search(s)
        if m:
            tag = re.match(r"<(\w+)", m.group()).group(1)
            return m.start(), element_end(s, m.start(), tag)
    return None


def in_template(s, i):
    return s.rfind("<template", 0, i) > s.rfind("</template>", 0, i)


# ---------------------------------------------------------------- per-page data
def deactivate(html):
    html = re.sub(r'\s+aria-current="(?:page|true)"', "", html)

    def fix_cls(m):
        toks = [t for t in m.group(1).split() if t not in ("active", "w--current", "current")]
        return f'class="{" ".join(toks)}"'
    return re.sub(r'class="([^"]*\b(?:ltt-mega-item|ltt-mega-subitem|ltt-nav-link|ltt-mobile-link|ltt-dropdown-btn|'
                  + re.escape(FOOTER_LINK_CLASS) + r'|ltt-lang-item|ltt-mobile-lang-chip)\b[^"]*)"', fix_cls, html)


def activate(html, path, lang, footer=False):
    def on(m):
        tag = m.group(0)
        href = re.search(r'href="([^"]*)"', tag)
        cls = re.search(r'class="([^"]*)"', tag)
        if not href or not cls or href.group(1).startswith("#") or norm_path(href.group(1)) != path:
            return tag
        toks = cls.group(1).split()
        if footer and FOOTER_LINK_CLASS in toks:
            toks.append("w--current")
        elif not footer and any(c in toks for c in ACTIVE_CLASSES):
            toks.append("active")
        else:
            return tag
        tag = tag.replace(cls.group(0), f'class="{" ".join(toks)}"', 1)
        return tag.replace("<a ", '<a aria-current="page" ', 1)
    html = re.sub(r"<a [^>]*>", on, html)
    if not footer:
        # mark the top-level dropdown button whose mega menu holds the current page
        def mark_drop(m):
            block = m.group(0)
            if re.search(r'class="ltt-mega-(?:sub)?item active"', block):
                block = re.sub(r'<button ([^>]*)class="ltt-nav-link ltt-dropdown-btn"',
                               r'<button aria-current="true" \1class="ltt-nav-link ltt-dropdown-btn active"', block, count=1)
            return block
        html = re.sub(r'<div class="ltt-nav-dropdown".*?(?=<div class="ltt-nav-dropdown"|</nav>)', mark_drop, html, flags=re.S)
        # current language in the switcher
        html = re.sub(rf'(<a [^>]*class="(?:ltt-lang-item|ltt-mobile-lang-chip))("[^>]*data-(?:m-)?lang="{lang}")',
                      r"\1 current\2", html)
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
        target = alt.get(lg, HOMES.get(lg, f"/{lg}"))
        return re.sub(r'href="[^"]*"', f'href="{target}"', tag, count=1)
    return re.sub(r'<a [^>]*data-(m-)?lang="([a-z]+)"[^>]*>', fix, header)


def build_header(master_header, page, path, lang):
    return point_switcher(activate(deactivate(master_header), path, lang), alternates(page))


def build_footer(master_footer, path, lang):
    return activate(deactivate(master_footer), path, lang, footer=True)


# ---------------------------------------------------------------------- sync
def block_pattern(b):
    close = "</style>" if b["open"].startswith("<style") else "</script>"
    return re.compile(re.escape(b["open"]) + r".*?" + re.escape(close), re.S)


def sync_page(s, master, path, lang):
    changed = []

    m_hdr = PAT_HEADER.search(master).group()
    new_hdr = build_header(m_hdr, s, path, lang)
    m = PAT_HEADER.search(s)
    if m:
        s2 = s[:m.start()] + new_hdr + s[m.end():]
    else:
        body = re.search(r"<body\b[^>]*>", s)
        if not body:
            raise ValueError("no <body>")
        s2 = s[:body.end()] + "\n" + new_hdr + s[body.end():]
    if s2 != s:
        changed.append("header")
    s = s2

    ms, me = find_footer(master)
    new_footer = build_footer(master[ms:me], path, lang)
    span = find_footer(s)
    if span and in_template(s, span[0]):
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

    for b in CFG.get("sync_blocks", []):
        pat = block_pattern(b)
        mb = pat.search(master)
        if not mb:
            continue
        block = mb.group()
        if pat.search(s):
            s2 = pat.sub(lambda _m: block, s, count=1)
        elif any(re.search(x, s) for x in b.get("skip_if", [])):
            s2 = s
        elif b["insert"] == "head":
            s2 = s.replace("</head>", block + "\n</head>", 1)
        elif b["insert"] == "after-header":
            s2 = s.replace("</header>", "</header>\n" + block, 1)
        else:
            s2 = s.replace("</body>", block + "\n</body>", 1)
        if s2 != s:
            changed.append(b["name"])
        s = s2
    return s, changed


# --------------------------------------------------------------------- checks
def product_key(href):
    for pat in (r"(p\d{6,})/", r"(t\d{4,})/", r"flow=(\d+)", r"(p\d{6,})\b"):
        m = re.search(pat, href)
        if m:
            return m.group(1)
    return None


def bar_problems(s):
    problems = []
    ids = set(re.findall(r'\bid="([^"]+)"', s))
    for cls in ("hybrid-sticky-bar", "hybrid-sheet"):
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


def vercel_ignored():
    """Patterns from .vercelignore: those files never reach the live site."""
    try:
        lines = read(".vercelignore").splitlines()
    except OSError:
        return lambda f: False
    pats = [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#") and not ln.startswith("!")]

    def ignored(f):
        for p in pats:
            anchored = p.startswith("/")
            p2 = p.strip("/")
            if anchored and (fnmatch.fnmatch(f, p2) or f.startswith(p2 + "/")):
                return True
            if not anchored and (fnmatch.fnmatch(os.path.basename(f), p2) or fnmatch.fnmatch(f, p2)
                                 or f.startswith(p2 + "/") or ("/" + p2 + "/") in ("/" + f)):
                return True
        return False
    return ignored


def unlisted_files(published_files):
    out = []
    ignored = vercel_ignored()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel = os.path.relpath(dirpath, ROOT)
        top = rel.split(os.sep)[0]
        if rel != "." and (top in SKIP_DIRS or top.startswith(".")):
            dirnames[:] = []
            continue
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            f = fn if rel == "." else f"{rel}/{fn}"
            if f in published_files or ignored(f) or any(f == u or f.startswith(u.rstrip("/") + "/") for u in UNLISTED_OK):
                continue
            out.append(f)
    return sorted(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report drift and problems, write nothing")
    args = ap.parse_args()

    masters = {lg: read(f) for lg, f in MASTERS.items()}
    pages = published_pages()
    drift, errors, problems = 0, [], []

    for path, f in pages:
        s = read(f)
        lg = page_lang(s)
        if lg not in masters:
            errors.append(f"{f}: no master for language '{lg}'")
            continue
        if f != MASTERS[lg]:
            try:
                new, changed = sync_page(s, masters[lg], path, lg)
            except ValueError as e:
                errors.append(f"{f}: {e}")
                continue
            if changed:
                drift += 1
                print(f"{'out of sync' if args.check else 'updated'}: {f} ({', '.join(changed)})")
                if not args.check:
                    with open(os.path.join(ROOT, f), "w", encoding="utf-8") as fh:
                        fh.write(new)
                s = new
        problems += [f"{f}: {p}" for p in bar_problems(s)]
        for what, n in (("menu", len(PAT_HEADER.findall(s))), ("footer", s.count(FOOTER_MARKER))):
            if n > 1:
                problems.append(f"{f}: {n} {what}s on the page, expected 1")

    entries = []
    for path, f in pages:
        s = read(f) if not args.check else None
        if s is None:
            s = read(f)
        lg = page_lang(s)
        if lg in masters:
            entries.append((lg, path, s))
    for lg, text in search_index.build(entries).items():
        rel = f"search/{lg}.json"
        full = os.path.join(ROOT, rel)
        old = open(full, encoding="utf-8").read() if os.path.exists(full) else None
        if old != text:
            drift += 1
            print(f"{'out of date' if args.check else 'rebuilt'}: {rel}")
            if not args.check:
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "w", encoding="utf-8") as fh:
                    fh.write(text)

    for o in unlisted_files({f for _, f in pages}):
        problems.append(f"{o}: page that is not in sitemap.xml (add a redirect in vercel.json and delete it, "
                        f"add it to the sitemap, or list it under unlisted_ok in scripts/layout_config.json)")
    for rel, _, missing in fix_affiliate_rel.run(write=not args.check):
        if not missing:
            continue
        if args.check:
            problems.append(f"{rel}: {missing} affiliate link(s) without rel=\"nofollow sponsored noopener\" "
                            f"(fix with: python3 scripts/fix_affiliate_rel.py)")
        else:
            print(f"affiliate rel fixed: {rel} ({missing})")
    for p in problems:
        print("PROBLEM", p)
    for e in errors:
        print("ERROR", e)
    print(f"{len(pages)} published pages, {drift} {'out of sync' if args.check else 'updated'}, "
          f"{len(problems)} problem(s), {len(errors)} error(s)")
    if errors or problems or (args.check and drift):
        sys.exit(1)


if __name__ == "__main__":
    main()
