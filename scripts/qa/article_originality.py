#!/usr/bin/env python3
"""Originality gate for a new article: the scaled-content checks article_lint.py does not do.

Google's scaled-content and helpful-content systems demote sites that publish
many similar, templated pages with nothing a reader could not get elsewhere.
article_lint.py covers meta, wiring, JSON-LD, images, links and em dashes.
This script covers the rest:

  ✗ blocks the preview     ! a human has to confirm it

- Duplicate / cannibal: title too close to an existing EN page, or body text
  that repeats another article (5-word shingles).
- No first-hand facts: no "Checked <Mon d, yyyy>" line, newest check older
  than 30 days, no methodology section, fewer cards than the title promises.
- Unverifiable claims: "tested", "personally", "price guarantee", "cheapest"
  and similar are flagged so someone confirms each is true for that card.

  python3 scripts/qa/article_originality.py private-cruises-paris
  python3 scripts/qa/article_originality.py lunch-cruises-paris --min-cards 3
  python3 scripts/qa/article_originality.py some-guide --guide     # no product cards

Exit 1 if anything is ✗.
"""
import argparse
import os
import re
import sys
from datetime import datetime, date
from urllib.parse import urlparse, unquote

from bs4 import BeautifulSoup

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
NON_ARTICLES = {"", "about", "contact", "privacy-policy", "terms-of-service", "search", "paris-cruise-quiz"}
RISKY = [r"\btested\b", r"\bpersonally\b", r"\bI (?:tried|took|booked|sailed)\b", r"\bwe (?:tried|took|booked)\b",
         r"price guarantee", r"\bcheapest\b", r"\bguaranteed?\b", r"\bexclusive\b"]
MONTHS = "Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
STOP = {"the", "in", "best", "of", "a", "and", "for", "to", "on", "with"}


def load(slug):
    f = os.path.join(ROOT, slug.strip("/"), "index.html")
    return open(f, encoding="utf-8").read() if os.path.exists(f) else None


def body_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "nav", "header", "footer", "noscript"]):
        t.decompose()
    main = soup.find("main") or soup.body or soup
    return main.get_text(" ", strip=True)


def shingles(text, n=5):
    w = re.findall(r"[a-z0-9€]+", text.lower())
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def title_words(t):
    return set(re.findall(r"[a-z]+", (t or "").lower())) - STOP


def en_articles():
    sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    out = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", sm):
        p = unquote(urlparse(loc).path).strip("/")
        if "/" in p or re.fullmatch(r"[a-z]{2}", p) or p in NON_ARTICLES:
            continue
        out.append(p)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page", help="slug, e.g. private-cruises-paris")
    ap.add_argument("--min-cards", type=int, default=3, help="minimum product cards for a comparison article")
    ap.add_argument("--max-age", type=int, default=30, help="max days since the newest 'Checked' date")
    ap.add_argument("--guide", action="store_true", help="informational guide without product cards")
    a = ap.parse_args()
    slug = a.page.strip("/")
    html = load(slug)
    if html is None:
        print(f"✗ {slug}/index.html not found")
        return 1
    soup = BeautifulSoup(html, "html.parser")
    text = body_text(html)
    title = (soup.title.string or "").strip() if soup.title else ""
    fails, warns, oks = [], [], []

    # first-hand evidence
    checks = re.findall(rf"[Cc]hecked (?:on )?((?:{MONTHS})[a-z]* \d{{1,2}}, \d{{4}})", text)
    if not checks:
        fails.append('no "Checked <Mon d, yyyy>" line: show when the facts were verified')
    else:
        newest = max(datetime.strptime(re.sub(r"^(\w{3})\w*", r"\1", c), "%b %d, %Y").date() for c in checks)
        age = (date.today() - newest).days
        (oks if age <= a.max_age else fails).append(f"facts checked {newest} ({age} days ago)")
    meth = [h for h in soup.find_all("h2")
            if re.search(r"How I (?:Picked|Chose|Ranked|Compared)|How We|Methodology", h.get_text(), re.I)]
    (oks if meth else fails).append("methodology section (How I Picked ...)")

    if not a.guide:
        cards = soup.select("div.bpa-card")
        m = re.search(r"\b(\d{1,2}) Best\b", title)
        promised = int(m.group(1)) if m else None
        if len(cards) < a.min_cards:
            fails.append(f"{len(cards)} product cards, need {a.min_cards}+ (or --guide)")
        elif promised and promised != len(cards):
            fails.append(f"title promises {promised}, page has {len(cards)} cards")
        else:
            oks.append(f"{len(cards)} product cards")

    # claims a human must confirm
    for pat in RISKY:
        m = re.search(pat, text, re.I)
        if m:
            ctx = text[max(0, m.start() - 60): m.end() + 60]
            warns.append(f'claim "{m.group(0)}": ...{ctx}...')

    # uniqueness against every other EN article
    me_t, me_s = title_words(title), shingles(text)
    worst_t, worst_s = (0.0, None), (0.0, None)
    for p in en_articles():
        if p == slug:
            continue
        h = load(p)
        if not h:
            continue
        s2 = BeautifulSoup(h, "html.parser")
        t2 = title_words(s2.title.string if s2.title else "")
        if me_t and t2:
            worst_t = max(worst_t, (len(me_t & t2) / len(me_t | t2), p))
        worst_s = max(worst_s, (len(me_s & shingles(body_text(h))) / max(1, len(me_s)), p))
    (oks if worst_t[0] < 0.6 else fails).append(
        f"title overlap {worst_t[0]:.0%} with /{worst_t[1]} (cannibalization at 60%+)")
    (oks if worst_s[0] < 0.25 else fails).append(
        f"body repeats {worst_s[0]:.0%} of its 5-word phrases from /{worst_s[1]} (max 25%)")

    for m in oks:
        print(f"  ✓ {m}")
    for m in warns:
        print(f"  ! {m}")
    for m in fails:
        print(f"  ✗ {m}")
    print(f"\n{slug}: {len(fails)} ✗, {len(warns)} !")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
