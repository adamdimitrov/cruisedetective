#!/usr/bin/env python3
"""Internal link graph for a static site (works for TCD and BPA).

Counts in-body internal links: <a> inside <main> (or <article>) prose, i.e.
inside a <p>, <li>, <td> or <blockquote>, and not inside the menu, footer,
breadcrumbs, table of contents, comparison deck cards or CTA buttons.

    python3 scripts/qa/internal_links.py                 # this repo
    python3 scripts/qa/internal_links.py --root DIR --site https://www.example.com
    python3 scripts/qa/internal_links.py --lang en --json out.json
    python3 scripts/qa/internal_links.py --pairs        # translations vs EN (needs hreflang)

Reports per page: inbound in-body links from same-language pages, outbound
count, and problems: broken targets, links to redirects / noindex pages,
cross-language links, self links.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
from collections import defaultdict

from bs4 import BeautifulSoup

# Matched against each class token / id of an ancestor. The comparison deck is div.bpa-card
# (and its bpa-card-* parts); editorial wrappers such as ltt-clean-card (intro),
# bpa-details-card (detailed reviews) and cf-faq-plus-card (FAQ) are prose and DO count.
SKIP_CLASS = re.compile(
    r"^(bpa-card(-.*)?|.*deck.*|.*toc.*|.*breadcrumb.*|.*navbar.*|.*nav-links.*|.*footer.*|"
    r".*floating.*|.*sticky.*|.*btn.*|.*button.*|.*cta.*|.*mega.*|.*drawer.*|.*switcher.*|"
    r"related-guides|author.*|.*byline.*|.*share.*|hp-guide.*|ltt-guide.*)$", re.I)
PROSE = {"p", "li", "td", "blockquote", "dd"}


def load(root, rel):
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


class Site:
    def __init__(self, root, site):
        self.root, self.site = root, site.rstrip("/")
        try:
            cfg = json.loads(load(root, "vercel.json"))
        except (OSError, ValueError):
            cfg = {}
        self.rw = {r["source"]: r["destination"] for r in cfg.get("rewrites", []) if ":" not in r["source"]}
        self.redirects = {r["source"].rstrip("/") or "/": r["destination"]
                          for r in cfg.get("redirects", [])
                          if ":" not in r["source"] and "(" not in r["source"] and not r.get("has")}
        self.redirect_pats = [r["source"] for r in cfg.get("redirects", []) if ":" in r["source"] or "(" in r["source"]]
        self.pages = {}  # path -> file
        for loc in re.findall(r"<loc>([^<]*)</loc>", load(root, "sitemap.xml")):
            p = self.norm(loc.strip())
            f = self.url_to_file(p)
            if f:
                self.pages[p] = f

    def norm(self, href):
        p = href.split("#")[0].split("?")[0]
        if p.startswith(self.site):
            p = p[len(self.site):]
        elif re.match(r"https?://", p):
            return None
        p = urllib.parse.unquote(p).strip("/")
        p = re.sub(r"(/index)?\.html$", "", p)
        return "/" + p if p and p != "index" else "/"

    def url_to_file(self, path):
        for p in (path, self.rw.get(path)):
            if not p:
                continue
            p = urllib.parse.unquote(p).rstrip("/") or "/"
            cands = ["index.html"] if p == "/" else [p.lstrip("/") + ".html", p.lstrip("/") + "/index.html"]
            for c in cands:
                if os.path.isfile(os.path.join(self.root, c)):
                    return c
        return None


def page_lang(soup):
    h = soup.find("html")
    lang = (h.get("lang") or "") if h else ""
    return lang.split("-")[0].lower() or "?"


def skipped(a, body):
    for par in a.parents:
        if par is body:
            return False
        if par.name in ("nav", "header", "footer", "aside", "button", "template"):
            return True
        tokens = list(par.get("class") or []) + ([par["id"]] if par.get("id") else [])
        if any(SKIP_CLASS.match(t) for t in tokens):
            return True
    return False


def in_prose(a, body):
    for par in a.parents:
        if par is body:
            return False
        if par.name in PROSE:
            return True
    return False


def body_of(soup):
    return soup.find("main") or soup.find("article") or soup.body


def analyse(site):
    meta, out_links, problems = {}, defaultdict(list), []
    for path, f in site.pages.items():
        soup = BeautifulSoup(load(site.root, f), "html.parser")
        robots = soup.find("meta", attrs={"name": "robots"})
        noindex = bool(robots and "noindex" in (robots.get("content") or "").lower())
        alts = {l.get("hreflang"): site.norm(l.get("href") or "")
                for l in soup.find_all("link", rel="alternate") if l.get("hreflang")}
        meta[path] = {"file": f, "lang": page_lang(soup), "noindex": noindex, "alts": alts}
        body = body_of(soup)
        if not body:
            continue
        for a in body.find_all("a", href=True):
            href = a["href"].strip()
            if href.startswith(("#", "mailto:", "tel:", "javascript:")):
                continue
            tgt = site.norm(href)
            if tgt is None:
                continue  # external
            if skipped(a, body) or not in_prose(a, body):
                continue
            out_links[path].append((tgt, a.get_text(" ", strip=True)))
    inbound = defaultdict(list)
    for src, links in out_links.items():
        for tgt, anchor in links:
            if tgt == src:
                problems.append(("self-link", src, tgt, anchor))
                continue
            if tgt in site.redirects:
                problems.append(("redirect-target", src, tgt, anchor))
                continue
            if tgt not in site.pages:
                kind = "not-in-sitemap" if site.url_to_file(tgt) else "broken"
                problems.append((kind, src, tgt, anchor))
                continue
            if meta[tgt]["noindex"]:
                problems.append(("noindex-target", src, tgt, anchor))
            if meta[tgt]["lang"] != meta[src]["lang"]:
                problems.append(("cross-language", src, tgt, anchor))
                continue
            inbound[tgt].append(src)
    return meta, out_links, inbound, problems


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--root", default=here)
    ap.add_argument("--site", default="https://www.thecruisedetective.com")
    ap.add_argument("--lang", help="only report pages in this language")
    ap.add_argument("--json", help="write full graph to this file")
    ap.add_argument("--min", type=int, default=3, help="minimum inbound in-body links")
    ap.add_argument("--money", default="", help="comma-separated EN money page paths")
    ap.add_argument("--pairs", action="store_true", help="compare each translation's outbound links with its EN page")
    a = ap.parse_args()

    site = Site(a.root, a.site)
    meta, out_links, inbound, problems = analyse(site)
    rows = []
    for p, m in meta.items():
        if a.lang and m["lang"] != a.lang:
            continue
        if m["noindex"]:
            continue
        rows.append((len(set(inbound.get(p, []))), len(out_links.get(p, [])), m["lang"], p))
    rows.sort()
    langs = sorted({r[2] for r in rows})
    for lg in langs:
        lr = [r for r in rows if r[2] == lg]
        under = [r for r in lr if r[0] < a.min]
        orphans = [r for r in lr if r[0] == 0]
        print(f"[{lg}] pages={len(lr)} orphans={len(orphans)} under{a.min}={len(under)} "
              f"links_out={sum(r[1] for r in lr)}")
    print()
    for r in rows:
        print(f"{r[0]:3d} in  {r[1]:3d} out  {r[2]:3s} {r[3]}")
    if problems:
        print("\nPROBLEMS")
        for pr in problems:
            if a.lang and meta.get(pr[1], {}).get("lang") != a.lang:
                continue
            print("  %-15s %s -> %s  [%s]" % pr)

    rc = 0
    if a.money:
        money = [m.strip() for m in a.money.split(",") if m.strip()]
        for lg in langs:
            lr = {r[3]: r[0] for r in rows if r[2] == lg}
            mset = [p for p in lr if p in money or meta[p]["alts"].get("en") in money]
            others = [v for p, v in lr.items() if p not in mset]
            if mset and others:
                low = min(lr[p] for p in mset)
                if low <= max(others):
                    print(f"\n[{lg}] money page with fewest inbound ({low}) is not above the top non-money page ({max(others)})")

    if a.pairs:
        en_by_path = {p: m for p, m in meta.items() if m["lang"] == "en"}
        miss = []
        for p, m in meta.items():
            if m["lang"] == "en" or m["noindex"]:
                continue
            en = m["alts"].get("en") or m["alts"].get("x-default")
            if en not in en_by_path:
                continue
            mine = {meta[t]["alts"].get("en") for t, _ in out_links.get(p, []) if t in meta}
            for t, _ in out_links.get(en, []):
                if t == en or t not in meta:
                    continue
                if t in mine:
                    continue
                has_tr = any(v == t for v in []) or meta[t]["alts"].get(m["lang"])
                miss.append((m["lang"], p, t, "missing" if has_tr else "no-translated-target"))
        print("\nTRANSLATION PARITY (EN links not present on the translation)")
        for x in miss:
            print("  %-3s %s  ->  %s  (%s)" % x)

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump({"inbound": {k: sorted(set(v)) for k, v in inbound.items()},
                       "outbound": out_links, "meta": meta, "problems": problems}, fh, ensure_ascii=False, indent=1)
    return rc


if __name__ == "__main__":
    sys.exit(main())
