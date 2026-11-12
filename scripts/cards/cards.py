#!/usr/bin/env python3
"""Money-page card toolkit: one data layer for the bpa-card comparison cards.

Subcommands
  extract PAGE [-o OUT.json]   Card facts of one page as JSON (the data layer).
  drift   EN_PAGE              Compare the EN page with every hreflang translation:
                               product, price, rating, photo count and card features.
  links   [PAGE ...]           Affiliate-link rules on cards (default: every page with cards).
  all                          drift for every EN money page + links everywhere. Exit 1 on errors.

PAGE is a folder (seine-river-cruises-paris) or a path to index.html.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://www.thecruisedetective.com"
TIQETS_PARTNER = "thecruisedetective.com-176436"
GYG_PARTNER = "YS414AJ"
FAREHARBOR_ASN = "cruisedetective-asn"  # FareHarbor affiliate (ASN) ref, e.g. Captain Jack Amsterdam
BOOKING_HOSTS = ("tiqets.com", "getyourguide.com", "fareharbor.com")
# Card features shipped on the EN Seine page on 2026-11-11. Drift reports which
# translations are still missing them.
FEATURES = {
    "rate_popover": ".bpa-rate-more",
    "tested_popover": ".bpa-tested",
    "time_pill": ".bpa-time",
    "lang_popover": ".bpa-lang-names",
    "route_popover": ".bpa-route",
    "pick_skip": ".bpa-pick",
    "kids_price": ".bpa-kids",
    "photo_captions": "img[data-cap]",
    "menu_pill": ".bpa-menu",
}


def page_path(p):
    p = Path(p)
    if not p.is_absolute():
        p = ROOT / p
    if p.is_dir():
        p = p / "index.html"
    return p


def text(el):
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip() if el else None


def product_id(href):
    if not href:
        return None
    m = re.search(r"-(p\d{5,})/", href) or re.search(r"-(t\d{3,})/?", href)
    return m.group(1) if m else urlparse(href).netloc or href


def money(s):
    if not s:
        return None
    m = re.search(r"(\d+(?:[.,]\d+)?)", s.replace("\u202f", "").replace(" ", ""))
    return float(m.group(1).replace(",", ".")) if m else None


def extract(path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    cards = []
    for c in soup.select("div.bpa-card"):
        title = c.select_one(".bpa-title")
        btn = c.select_one(".bpa-btn")
        stars = c.select_one(".bpa-stars")
        r = re.search(r"--r:\s*([\d.]+)", stars.get("style", "")) if stars else None
        badges = []
        for b in c.select(".bpa-rev-badge"):
            badges.append({
                "site": text(b.select_one(".bpa-rev-site")),
                "score": text(b.select_one(".bpa-rev-score")),
                "count": text(b.select_one(".bpa-rev-count")),
                "href": b.get("href"),
            })
        cards.append({
            "id": c.get("id"),
            "cat": c.get("data-cat"),
            "rank": text(c.select_one(".bpa-rank-tag")),
            "kicker": text(c.select_one(".bpa-kicker")),
            "title": text(title),
            "title_href": title.get("href") if title else None,
            "product": product_id(title.get("href") if title else None),
            "rating": text(c.select_one(".bpa-rate-score")),
            "rating_weighted": float(r.group(1)) if r else None,
            "rating_meta": text(c.select_one(".bpa-rate-meta")),
            "badges": badges,
            "pills": [text(s) for s in c.select(".bpa-specs-row .bpa-sp")],
            "was": text(c.select_one(".bpa-was")),
            "price": text(c.select_one(".bpa-price")),
            "price_value": money(text(c.select_one(".bpa-price"))),
            "kids": text(c.select_one(".bpa-kids")),
            "pick_skip": text(c.select_one(".bpa-pickskip")) or text(c.select_one(".bpa-best-for")),
            "cta": text(btn),
            "cta_href": btn.get("href") if btn else None,
            "photos": len(c.select(".bpa-slider img")),
            "captions": len(c.select(".bpa-slider img[data-cap]")),
            "features": sorted(k for k, sel in FEATURES.items() if c.select_one(sel)),
            "links": [a.get("href") for a in c.select("a[href]")],
        })
    alts = {l.get("hreflang"): l.get("href") for l in soup.select('link[rel="alternate"][hreflang]')}
    return {"page": str(path.relative_to(ROOT)), "alternates": alts, "cards": cards}


def url_to_path(url):
    rel = unquote(urlparse(url).path).strip("/")
    return ROOT / rel / "index.html" if rel else ROOT / "index.html"


def drift(en_page):
    en = extract(page_path(en_page))
    out = {"page": en["page"], "langs": {}}
    errors = 0
    for lang, url in sorted(en["alternates"].items()):
        if lang in ("en", "x-default"):
            continue
        p = url_to_path(url)
        if not p.exists():
            out["langs"][lang] = {"error": f"missing file {p.relative_to(ROOT)}"}
            errors += 1
            continue
        tr = extract(p)
        issues, missing_feat = [], set()
        if len(tr["cards"]) != len(en["cards"]):
            issues.append(f"card count {len(tr['cards'])} vs EN {len(en['cards'])}")
        for i, (a, b) in enumerate(zip(en["cards"], tr["cards"]), 1):
            if a["product"] != b["product"]:
                issues.append(f"#{i} product {b['product']} vs EN {a['product']}")
            if a["price_value"] != b["price_value"]:
                issues.append(f"#{i} price {b['price']} vs EN {a['price']}")
            if a["rating"] and b["rating"] and a["rating"] != b["rating"]:
                issues.append(f"#{i} rating {b['rating']} vs EN {a['rating']}")
            if b["photos"] < a["photos"]:
                issues.append(f"#{i} photos {b['photos']} vs EN {a['photos']}")
            missing_feat |= set(a["features"]) - set(b["features"])
        errors += len(issues)
        out["langs"][lang] = {
            "page": tr["page"],
            "issues": issues,
            "missing_features": sorted(missing_feat),
        }
    return out, errors


def link_problems(path):
    data = extract(path)
    probs = []
    for i, c in enumerate(data["cards"], 1):
        badge_hrefs = {b["href"] for b in c["badges"] if b["href"]}
        for href in c["links"]:
            if not href or href.startswith("#") or href.startswith("/"):
                continue
            host = urlparse(href).netloc.lower()
            if ("maps.google" in host or "goo.gl" in host or "thecruisedetective.com" in host
                    or (host.endswith("google.com") and "/maps" in href)):
                continue
            if host in ("tp.media", "tripadvisor.tp.st"):  # Travelpayouts affiliate redirects
                continue
            if "viator.com" in host and href in badge_hrefs:
                continue  # Viator is allowed as a review badge
            q = parse_qs(urlparse(href).query)
            if "tiqets.com" in host:
                if q.get("partner", [None])[0] != TIQETS_PARTNER:
                    probs.append(f"#{i} Tiqets link without partner={TIQETS_PARTNER}: {href[:90]}")
                if not q.get("tq_campaign"):
                    probs.append(f"#{i} Tiqets link without tq_campaign: {href[:90]}")
            elif "getyourguide.com" in host:
                if q.get("partner_id", [None])[0] != GYG_PARTNER:
                    probs.append(f"#{i} GYG link without partner_id={GYG_PARTNER}: {href[:90]}")
            elif "fareharbor.com" in host:
                if q.get("ref", [None])[0] != FAREHARBOR_ASN:
                    probs.append(f"#{i} FareHarbor link without ref={FAREHARBOR_ASN}: {href[:90]}")
            elif "viator.com" in host:
                probs.append(f"#{i} Viator link on a card (Viator is badge-only, no link): {href[:90]}")
            else:
                probs.append(f"#{i} non-affiliate outbound link: {href[:90]}")
        for key in ("title_href", "cta_href"):
            h = c[key]
            if h and not any(x in urlparse(h).netloc for x in BOOKING_HOSTS):
                probs.append(f"#{i} {key} is not Tiqets/GYG: {h[:90]}")
        if c["title_href"] and c["cta_href"] and product_id(c["title_href"]) != product_id(c["cta_href"]):
            probs.append(f"#{i} title and button point to different products")
    return data["page"], probs


def card_pages():
    for p in sorted(ROOT.rglob("index.html")):
        if any(x in p.relative_to(ROOT).parts for x in ("node_modules", ".claude", ".git")):
            continue
        try:
            if 'class="bpa-card"' in p.read_text(encoding="utf-8"):
                yield p
        except UnicodeDecodeError:
            continue


EN_MONEY_PAGES = [
    "seine-river-cruises-paris",
    "dinner-cruises-paris",
    "thames-river-cruises-london",
    "canal-cruises-amsterdam",
]


def print_drift(rep):
    print(f"\n== {rep['page']}")
    for lang, r in rep["langs"].items():
        if "error" in r:
            print(f"  {lang}: ERROR {r['error']}")
            continue
        status = "OK" if not r["issues"] else f"{len(r['issues'])} issue(s)"
        print(f"  {lang}: {status}  ({r['page']})")
        for s in r["issues"]:
            print(f"      - {s}")
        if r["missing_features"]:
            print(f"      behind EN: {', '.join(r['missing_features'])}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("extract"); e.add_argument("page"); e.add_argument("-o")
    d = sub.add_parser("drift"); d.add_argument("page"); d.add_argument("--json", action="store_true")
    l = sub.add_parser("links"); l.add_argument("pages", nargs="*")
    sub.add_parser("all")
    a = ap.parse_args()

    if a.cmd == "extract":
        data = extract(page_path(a.page))
        for c in data["cards"]:
            c.pop("links")
        js = json.dumps(data, ensure_ascii=False, indent=2)
        Path(a.o).write_text(js + "\n", encoding="utf-8") if a.o else print(js)
        return 0
    if a.cmd == "drift":
        rep, errs = drift(a.page)
        print(json.dumps(rep, ensure_ascii=False, indent=2)) if a.json else print_drift(rep)
        return 1 if errs else 0
    if a.cmd == "links":
        pages = [page_path(p) for p in a.pages] or list(card_pages())
        total = 0
        for p in pages:
            name, probs = link_problems(p)
            total += len(probs)
            if probs:
                print(f"\n== {name}")
                for s in probs:
                    print(f"  - {s}")
        print(f"\n{total} link problem(s) across {len(pages)} page(s)")
        return 1 if total else 0
    if a.cmd == "all":
        errs = 0
        for p in EN_MONEY_PAGES:
            rep, n = drift(p)
            print_drift(rep)
            errs += n
        pages = list(card_pages())
        lp = 0
        for p in pages:
            name, probs = link_problems(p)
            lp += len(probs)
            if probs:
                print(f"\n== links {name}")
                for s in probs:
                    print(f"  - {s}")
        print(f"\nSummary: {errs} cross-language fact issue(s), {lp} link problem(s), {len(pages)} card pages")
        return 1 if errs or lp else 0


if __name__ == "__main__":
    sys.exit(main())
