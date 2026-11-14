#!/usr/bin/env python3
"""Article lint: every house rule a new or refreshed article must pass before preview.

  python3 scripts/qa/article_lint.py private-cruises-paris
  python3 scripts/qa/article_lint.py private-cruises-paris --max-age 45
  python3 scripts/qa/article_lint.py --all          # every EN article in sitemap.xml

The /new-article loop runs this after each draft and fixes until it exits 0.
Unlike scripts/ship/preflight.py (which checks the diff), this checks the WHOLE
page, so it also works for monthly refreshes of old articles.

✗ = fail (exit 1). ⚠ = warn (look at it, does not block).

Checks
  meta      one <h1>, <title> <= 65 chars, meta description 110-160 chars,
            canonical = page URL, hreflang en + x-default, no stale year in title/h1
  wiring    sitemap.xml entry, vercel.json rewrite, search/en.json entry,
            at least 2 other pages link to it from body copy (menu/footer don't count)
  copy      no em dashes anywhere in visible text, meta or JSON-LD
  jsonld    every block parses, has Article + BreadcrumbList, dateModified
            not older than --max-age days (default 90)
  images    every <img> has alt text, local src exists, content photos self-hosted
  links     internal links resolve, outbound booking links follow affiliate rules
            (cards.py link_problems for cards, the same rules for in-text links)
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs, unquote

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "cards"))
import cards  # noqa: E402

SITE = cards.SITE
LANG_DIRS = {"fr", "de", "es", "it", "ja", "nl", "pl", "ro"}
# hosts that may appear in body copy without an affiliate tag
NEUTRAL_HOSTS = (
    "thecruisedetective.com", "google.com", "goo.gl", "maps.app.goo.gl", "wikipedia.org",
    "tp.media", "tripadvisor.tp.st", "cdn.prod.website-files.com", "schema.org",
    "instagram.com", "facebook.com", "youtube.com", "x.com", "twitter.com", "linkedin.com",
    "pinterest.com", "tiktok.com",
)
# Webflow CDN images from the old site: allowed for chrome (logo, avatar), not for content photos
NOT_ARTICLES = {"about", "contact", "privacy-policy", "terms-of-service", "search", "paris-cruise-quiz"}
ARTICLE_TYPES ={"Article", "BlogPosting", "NewsArticle", "Review"}
CHROME_IMG = re.compile(r"(logo|avatar|portrait|webclip|icon|badge|flag)", re.I)


class Report:
    def __init__(self):
        self.fails, self.warns = [], []
        self.other_hosts = set()

    def fail(self, area, msg):
        m = f"[{area}] {msg}"
        if m not in self.fails:
            self.fails.append(m)

    def warn(self, area, msg):
        m = f"[{area}] {msg}"
        if m not in self.warns:
            self.warns.append(m)


def load_rewrites():
    vj = json.loads((ROOT / "vercel.json").read_text(encoding="utf-8"))
    return {r["source"]: r["destination"] for r in vj.get("rewrites", [])}, vj


def resolve_internal(href, rewrites):
    """True when a site-relative href points at something that exists."""
    path = unquote(urlparse(href).path)
    if not path or path == "/":
        return True
    if path in rewrites:
        return True
    p = ROOT / path.lstrip("/")
    return p.is_file() or (p / "index.html").is_file() or Path(str(p) + ".html").is_file()


def body_without_chrome(soup):
    s = BeautifulSoup(str(soup), "html.parser")
    for t in s.find_all(["header", "nav", "footer", "script", "style", "noscript", "template"]):
        t.decompose()
    for t in s.select(".ltt-menu, .ltt-footer, .ltt-drawer, .ltt-mega"):
        t.decompose()
    return s


def check_affiliate(href, where, rep):
    host = urlparse(href).netloc.lower()
    q = parse_qs(urlparse(href).query)
    if "tiqets.com" in host:
        if q.get("partner", [None])[0] != cards.TIQETS_PARTNER:
            rep.fail("links", f"{where}: Tiqets link without partner={cards.TIQETS_PARTNER}: {href[:90]}")
        if not q.get("tq_campaign"):
            rep.fail("links", f"{where}: Tiqets link without tq_campaign: {href[:90]}")
    elif "getyourguide." in host:
        if q.get("partner_id", [None])[0] != cards.GYG_PARTNER:
            rep.fail("links", f"{where}: GYG link without partner_id={cards.GYG_PARTNER}: {href[:90]}")
    elif "fareharbor.com" in host:
        if q.get("ref", [None])[0] != cards.FAREHARBOR_ASN:
            rep.fail("links", f"{where}: FareHarbor link without ref={cards.FAREHARBOR_ASN}: {href[:90]}")
    elif "viator.com" in host:
        rep.fail("links", f"{where}: Viator link (Viator is review-badge only): {href[:90]}")
    elif not any(host == h or host.endswith("." + h) for h in NEUTRAL_HOSTS):
        rep.other_hosts.add(host)


def lint(slug, max_age, rewrites, vercel, sitemap, search_en, all_pages):
    rep = Report()
    slug = slug.strip("/").removesuffix("/index.html")
    path = ROOT / slug / "index.html"
    url = f"{SITE}/{slug}"
    if not path.is_file():
        rep.fail("meta", f"{slug}/index.html does not exist")
        return rep
    raw = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(raw, "html.parser")
    year = datetime.now(timezone.utc).year

    # ---- meta
    h1s = soup.find_all("h1")
    if len(h1s) != 1:
        rep.fail("meta", f"{len(h1s)} <h1> tags (need exactly 1)")
    title = soup.title.get_text(strip=True) if soup.title else ""
    if not title:
        rep.fail("meta", "no <title>")
    elif len(title) > 65:
        rep.warn("meta", f"<title> is {len(title)} chars (Google cuts ~60-65): {title}")
    md = soup.find("meta", attrs={"name": "description"})
    desc = (md.get("content") or "").strip() if md else ""
    if not desc:
        rep.fail("meta", "no meta description")
    elif not 110 <= len(desc) <= 160:
        rep.warn("meta", f"meta description is {len(desc)} chars (aim 110-160)")
    can = soup.find("link", rel="canonical")
    if not can or can.get("href") != url:
        rep.fail("meta", f"canonical should be {url}, is {can.get('href') if can else 'missing'}")
    langs = {l.get("hreflang") for l in soup.find_all("link", rel="alternate") if l.get("hreflang")}
    for need in ("en", "x-default"):
        if need not in langs:
            rep.fail("meta", f"hreflang {need} missing")
    for label, txt in (("title", title), ("h1", h1s[0].get_text(" ", strip=True) if h1s else "")):
        old = [y for y in re.findall(r"\b(20\d\d)\b", txt) if int(y) < year]
        if old:
            rep.fail("meta", f"stale year {old[0]} in {label}: {txt[:80]}")

    # ---- wiring
    if not re.search(r"<loc>" + re.escape(url) + r"</loc>", sitemap):
        rep.fail("wiring", "not in sitemap.xml")
    if f"/{slug}\"" not in search_en and url + '"' not in search_en:
        rep.fail("wiring", "not in search/en.json (run python3 scripts/sync_layout.py)")
    inbound = []
    for other in all_pages:
        if other == path:
            continue
        try:
            o = other.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if f"/{slug}" not in o:
            continue
        body = body_without_chrome(BeautifulSoup(o, "html.parser"))
        hit = any(urlparse(a["href"]).path.rstrip("/") in (f"/{slug}",)
                  or a["href"].startswith(url) for a in body.find_all("a", href=True))
        if hit:
            rel = str(other.parent.relative_to(ROOT))
            inbound.append("/" if rel == "." else rel)
    if len(inbound) < 2:
        rep.fail("wiring", f"only {len(inbound)} page(s) link here from body copy "
                           f"({', '.join(inbound) or 'none'}); add contextual links from 2+ related guides")

    # ---- copy (em dashes): visible text, meta, JSON-LD, but not CSS/JS code or comments
    vis = BeautifulSoup(raw, "html.parser")
    for t in vis.find_all(["style", "noscript", "template"]):
        t.decompose()
    for t in vis.find_all("script"):
        if t.get("type") != "application/ld+json":
            t.decompose()
    hits = []
    for s in vis.find_all(string=lambda x: x and "—" in x):
        if type(s).__name__ == "Comment":
            continue
        hits.append(s.strip()[:80])
    for m in vis.find_all("meta", content=True):
        if "—" in m["content"]:
            hits.append(f'meta {m.get("name") or m.get("property")}: {m["content"][:60]}')
    for a in vis.find_all(alt=True):
        if "—" in a["alt"]:
            hits.append(f'alt: {a["alt"][:60]}')
    if hits:
        rep.fail("copy", f"{len(hits)} em dash(es), e.g. “{hits[0]}”")

    # ---- JSON-LD
    types = set()
    modified = None
    for blk in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(blk.string or "")
        except json.JSONDecodeError as e:
            rep.fail("jsonld", f"block does not parse: {e}")
            continue
        stack = [data]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                t = x.get("@type")
                types.update(t if isinstance(t, list) else [t] if t else [])
                if x.get("@type") in ARTICLE_TYPES and x.get("dateModified"):
                    modified = x["dateModified"]
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)
    for need in ("Article", "BreadcrumbList"):
        if need not in types and not (need == "Article" and types & ARTICLE_TYPES):
            rep.fail("jsonld", f"no {need}" + (" (Article, Review or BlogPosting)" if need == "Article" else ""))
    if not modified:
        rep.fail("jsonld", "Article/Review has no dateModified (Google uses it for freshness)")
    else:
        try:
            dm = datetime.fromisoformat(modified.replace("Z", "+00:00"))
            if dm.tzinfo is None:
                dm = dm.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - dm).days
            if age > max_age:
                rep.fail("jsonld", f"dateModified is {age} days old (> {max_age}); facts need a refresh")
        except ValueError:
            rep.fail("jsonld", f"dateModified not ISO 8601: {modified}")

    # ---- images
    for img in soup.find_all("img"):
        if img.find_parent("noscript") or img.get("width") == "1" or "facebook.com/tr" in (img.get("src") or ""):
            continue  # tracking pixel
        src = img.get("src") or ""
        if src.startswith("data:"):  # lazy placeholder or inline icon
            src = img.get("data-src") or ""
            if not src:
                continue
        alt = (img.get("alt") or "").strip()
        if not alt:
            rep.fail("images", f"no alt text: {src[:80]}")
        if src.startswith("/"):
            if not (ROOT / unquote(urlparse(src).path).lstrip("/")).is_file():
                rep.fail("images", f"missing file: {src[:90]}")
        elif src.startswith("http") and not CHROME_IMG.search(src + " " + alt) \
                and "thecruisedetective.com" not in src:
            rep.warn("images", f"content photo not self-hosted (put AVIF in /assets/{slug}/): {src[:80]}")

    # ---- links
    card_links = set()
    if 'class="bpa-card"' in raw:
        _, probs = cards.link_problems(path)
        for p in probs:
            rep.fail("links", f"card {p}")
        for c in soup.select("div.bpa-card"):
            card_links.update(a["href"] for a in c.find_all("a", href=True))
    body = body_without_chrome(soup)
    for a in body.find_all("a", href=True):
        href = a["href"].strip()
        if href in card_links or href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        if href.startswith("/") or href.startswith(SITE):
            rel = href[len(SITE):] if href.startswith(SITE) else href
            if not resolve_internal(rel or "/", rewrites):
                rep.fail("links", f"broken internal link: {href[:90]}")
        elif href.startswith("http"):
            check_affiliate(href, "text", rep)
    if rep.other_hosts:
        rep.warn("links", "non-affiliate outbound hosts (fine for sources, check the rest): "
                 + ", ".join(sorted(rep.other_hosts)))
    return rep


def en_articles(sitemap):
    out = []
    for loc in re.findall(r"<loc>([^<]+)</loc>", sitemap):
        rel = unquote(loc[len(SITE):]).strip("/")
        if not rel or rel.split("/")[0] in LANG_DIRS:
            continue
        if rel in NOT_ARTICLES:
            continue
        if (ROOT / rel / "index.html").is_file():
            out.append(rel)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="*", help="article folder, e.g. private-cruises-paris")
    ap.add_argument("--all", action="store_true", help="every EN article in sitemap.xml")
    ap.add_argument("--max-age", type=int, default=90, help="max days since dateModified (default 90)")
    a = ap.parse_args()

    rewrites, vercel = load_rewrites()
    sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    search_en = (ROOT / "search" / "en.json").read_text(encoding="utf-8")
    pages = en_articles(sitemap) if a.all else a.pages
    if not pages:
        ap.error("give an article folder or --all")
    all_pages = [p for p in ROOT.rglob("index.html")
                 if not any(x in p.relative_to(ROOT).parts for x in ("node_modules", ".claude", ".git", "test", "archive"))]

    bad = 0
    for slug in pages:
        rep = lint(slug, a.max_age, rewrites, vercel, sitemap, search_en, all_pages)
        mark = "✗" if rep.fails else ("⚠" if rep.warns else "✓")
        print(f"\n{mark} /{slug.strip('/')}")
        for f in rep.fails:
            print("  ✗", f)
        for w in rep.warns:
            print("  ⚠", w)
        bad += bool(rep.fails)
    print(f"\n{len(pages) - bad}/{len(pages)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
