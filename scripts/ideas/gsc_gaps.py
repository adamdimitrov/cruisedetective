#!/usr/bin/env python3
"""Find new-article ideas in Search Console data.

Google already shows thecruisedetective.com for queries that no page really
answers (it ranks the Seine listicle at position 25 for "lunch cruise paris").
Those queries are demand we can prove, with no keyword tool needed.

For every query the script finds the best page that ranks for it, then looks at
the words in the query that the page's title, H1 and URL do not cover. Queries
that share such a missing word ("lunch", "eiffel", "batobus") are grouped into
one topic. A topic with many impressions at a poor position is a gap: an
article idea. Queries the page already covers but ranks 8-20 for are listed
separately as refresh work on the existing page, not new articles.

  python3 scripts/ideas/gsc_gaps.py                 # EN, last 90 days
  python3 scripts/ideas/gsc_gaps.py --days 180 --min-impr 50
  python3 scripts/ideas/gsc_gaps.py --lang all --json /tmp/gaps.json

Read-only. Needs credentials/gsc_service_account.json.
"""
import argparse
import json
import os
import re
import sys
import warnings
from collections import defaultdict
from datetime import date, timedelta
from urllib.parse import urlparse, unquote

warnings.filterwarnings("ignore")
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CREDS = os.path.join(ROOT, "credentials", "gsc_service_account.json")
if not os.path.exists(CREDS):  # worktrees have no credentials folder
    CREDS = os.path.join(ROOT.split("/.claude/worktrees/")[0], "credentials", "gsc_service_account.json")
SITE = "sc-domain:thecruisedetective.com"
CITIES = {"paris": "paris", "seine": "paris", "eiffel": "paris", "amsterdam": "amsterdam",
          "london": "london", "thames": "london"}

# Words that never make a topic on their own: they are in almost every query.
GENERIC = set("""
a an the and or of in on at to for with from by is are vs best top good which what
how much price prices cost ticket tickets book booking review reviews 2025 2026 2027
cruise cruises boat boats tour tours trip river riverboat ride rides cruising
paris seine amsterdam canal canals london thames city near me my do does can i
france french uk england netherlands holland de la le les en sur bateaux parisien parisiens
""".split())


def norm(word):
    word = word.lower()
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def words(text):
    return {norm(w) for w in re.findall(r"[a-zA-ZÀ-ÿ]+", text or "") if len(w) > 1}


def page_lang(url):
    seg = urlparse(url).path.strip("/").split("/")[0]
    return seg if re.fullmatch(r"[a-z]{2}", seg) else "en"


def city_of(query, url):
    for w in re.findall(r"[a-z]+", query.lower()):
        if w in CITIES:
            return CITIES[w]
    for w, c in CITIES.items():
        if w in url.lower():
            return c
    return "?"


def clean_url(url):
    return url.split("#")[0].split("?")[0].rstrip("/") or url


def page_file(url):
    path = unquote(urlparse(url).path).strip("/")
    for cand in (os.path.join(ROOT, path, "index.html"), os.path.join(ROOT, path + ".html"),
                 os.path.join(ROOT, "index.html") if not path else ""):
        if cand and os.path.exists(cand):
            return cand
    return None


_page_cache = {}


def page_words(url):
    if url in _page_cache:
        return _page_cache[url]
    text = urlparse(url).path.replace("-", " ").replace("/", " ")
    f = page_file(url)
    if f:
        html = open(f, encoding="utf-8", errors="ignore").read()
        for pat in (r"<title[^>]*>(.*?)</title>", r"<h1[^>]*>(.*?)</h1>"):
            m = re.search(pat, html, re.S | re.I)
            if m:
                text += " " + re.sub(r"<[^>]+>", " ", m.group(1))
    _page_cache[url] = words(text)
    return _page_cache[url]


def fetch(days):
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_file(
        CREDS, scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
    svc = build("searchconsole", "v1", credentials=creds, cache_discovery=False)
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=days)
    rows, offset = [], 0
    while True:
        body = {"startDate": str(start), "endDate": str(end), "dimensions": ["query", "page"],
                "rowLimit": 25000, "startRow": offset}
        batch = svc.searchanalytics().query(siteUrl=SITE, body=body).execute().get("rows", [])
        rows += batch
        if len(batch) < 25000:
            return rows, start, end
        offset += 25000


def analyse(rows, lang, min_impr):
    # Collapse #fragment URLs into the page, keep the best page per query.
    per = defaultdict(lambda: {"impr": 0, "clicks": 0, "pos_w": 0.0})
    for r in rows:
        q, url = r["keys"]
        url = clean_url(url)
        if lang != "all" and page_lang(url) != lang:
            continue
        d = per[(q, url)]
        d["impr"] = max(d["impr"], r["impressions"])  # fragments repeat the same impressions
        d["clicks"] = max(d["clicks"], r["clicks"])
        d["pos_w"] = r["position"] if not d["pos_w"] else min(d["pos_w"], r["position"])
    best = {}
    for (q, url), d in per.items():
        if q not in best or d["impr"] > best[q]["impr"]:
            best[q] = dict(d, url=url, query=q)

    topics = defaultdict(lambda: {"impr": 0, "clicks": 0, "queries": [], "pages": defaultdict(int)})
    refresh = []
    for q, d in best.items():
        missing = words(q) - page_words(d["url"]) - GENERIC
        if not missing:
            if d["impr"] >= min_impr and 8 <= d["pos_w"] <= 20:
                refresh.append(d)
            continue
        city = city_of(q, d["url"])
        for w in missing:
            t = topics[(city, w)]
            t["impr"] += d["impr"]
            t["clicks"] += d["clicks"]
            t["queries"].append(d)
            t["pages"][d["url"]] += d["impr"]

    out = []
    for (city, w), t in topics.items():
        if t["impr"] < min_impr:
            continue
        t["queries"].sort(key=lambda x: -x["impr"])
        pos = sum(x["pos_w"] * x["impr"] for x in t["queries"]) / t["impr"]
        out.append({"topic": f"{city}: {w}", "city": city, "word": w, "impr": t["impr"], "clicks": t["clicks"], "avg_pos": round(pos, 1),
                    "n_queries": len(t["queries"]),
                    "top_queries": [(x["query"], x["impr"], round(x["pos_w"], 1)) for x in t["queries"][:8]],
                    "ranking_pages": sorted(t["pages"], key=lambda u: -t["pages"][u])[:3]})
    out.sort(key=lambda x: -x["impr"])
    refresh.sort(key=lambda x: -x["impr"])
    return out, refresh


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--lang", default="en", help="en, fr, de, ... or all")
    ap.add_argument("--min-impr", type=int, default=30, help="minimum impressions per topic")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--json", help="also write the full result here")
    a = ap.parse_args()

    rows, start, end = fetch(a.days)
    gaps, refresh = analyse(rows, a.lang, a.min_impr)
    print(f"GSC {SITE} {start}..{end}, lang={a.lang}, {len(rows)} rows\n")
    print(f"== Gap topics (query words no ranking page covers), top {a.top} ==")
    for g in gaps[: a.top]:
        pages = ", ".join(urlparse(u).path or "/" for u in g["ranking_pages"])
        print(f"\n[{g['topic']}]  {g['impr']} impr, {g['clicks']} clicks, avg pos {g['avg_pos']}, "
              f"{g['n_queries']} queries  <- now: {pages}")
        for q, i, p in g["top_queries"]:
            print(f"    {i:>6}  pos {p:>5}  {q}")
    print(f"\n== Refresh (page covers the query, ranks 8-20), top 15 ==")
    for d in refresh[:15]:
        print(f"  {d['impr']:>6}  pos {d['pos_w']:>5.1f}  {d['query']}  <- {urlparse(d['url']).path}")
    if a.json:
        with open(a.json, "w") as f:
            json.dump({"range": [str(start), str(end)], "gaps": gaps, "refresh": refresh}, f, indent=1)
        print(f"\nwrote {a.json}")


if __name__ == "__main__":
    sys.exit(main())
