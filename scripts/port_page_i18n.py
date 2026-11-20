#!/usr/bin/env python3
"""Port an English page to its translated URLs using the EN page as the template.

The English page is the single source of truth for structure and content. For each
language that already has a translated URL (hreflang alternate on the EN page), this
script translates the EN page's text with Claude and writes the result to that
translated file, so translations get the same layout as English.

    python3 scripts/port_page_i18n.py dinner-cruises-paris/index.html --langs de,hu
    python3 scripts/port_page_i18n.py dinner-cruises-paris/index.html            # all 21
    python3 scripts/port_page_i18n.py dinner-cruises-paris/index.html --dry-run  # no API, keeps EN text
    python3 scripts/port_page_i18n.py seine-river-cruises-paris/index.html --langs de --cache-only --listicle-cards

--listicle-cards: for pages whose cards are data (data/listicles/<page>.json). The cards are left
out of the translation and replaced by the <!-- listicle:cards --> marker; then
`python3 scripts/listicle.py build-lang <en-page> <lang>` renders them from the English card data
plus data/listicles/i18n/<page>/<lang>.json. The English-only AI cruise finder is dropped.

Needs ANTHROPIC_API_KEY (environment or the repo .env) and `pip install anthropic bs4`.
Translations are cached in data/i18n/port/<page>/<lang>.json, so re-runs only send
new or changed segments. After porting, run scripts/sync_layout.py for the menu/footer.

Rules sent to the model: keep brand, company, boat, place and street names as written
(Legenda, Silverline, Vigadó tér, ...), keep every HTML tag and attribute, numbers,
prices, times and URLs unchanged, no em dashes, and no "independent / unsponsored /
undercover / paid our own tickets" style claims.
"""
import argparse
import copy
import hashlib
import json
import os
import re
import sys
import urllib.parse

from bs4 import BeautifulSoup, NavigableString, Comment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.thecruisedetective.com"
MODEL = os.environ.get("PORT_I18N_MODEL", "claude-opus-5-5")
LANG_NAMES = {
    "hu": "Hungarian", "de": "German", "fr": "French", "it": "Italian", "es": "Spanish",
    "ro": "Romanian", "pl": "Polish", "nl": "Dutch", "cs": "Czech", "sk": "Slovak",
    "pt": "Portuguese", "ru": "Russian", "hr": "Croatian", "sr": "Serbian (Cyrillic script)",
    "bg": "Bulgarian", "el": "Greek", "tr": "Turkish", "uk": "Ukrainian", "he": "Hebrew",
    "ja": "Japanese", "ko": "Korean",
}
LANG_NAMES["pt"] = "Portuguese (European)"
INLINE = {"a", "strong", "b", "em", "i", "span", "br", "small", "sup", "sub", "u", "mark", "abbr", "code", "s"}
SKIP = {"script", "style", "svg", "noscript", "template", "iframe", "code"}
ATTRS = ("alt", "title", "aria-label", "placeholder", "data-tooltip", "data-label", "data-lit-what")
JSONLD_KEYS = {"name", "description", "headline", "text", "alternateName", "caption", "about", "reviewBody"}

SYSTEM = """You translate pages of The Cruise Detective, a guide to river, canal and dinner cruises in Paris, London, Amsterdam, Prague, Porto, Berlin and Warsaw, from English into {lang}.

Rules:
- Translate naturally for travelers reading {lang}; keep the meaning, tone and length close to the English. Use the formal form of address where the language has one.
- Each item is an HTML fragment. Keep every tag, attribute and attribute value exactly as given; translate only the human-readable text between tags. Keep leading/trailing spaces.
- Never translate brand, company, boat, venue, product, place or street names (for example Bateaux Mouches, Bateaux Parisiens, Vedettes de Paris, Le Diamant Bleu, Marina de Paris, Eiffel Croisières, Captain Jack, Thames Clippers, Uber Boat, City Cruises, Stern und Kreis, Prague Boats, GetYourGuide, Tiqets, Viator, Tripadvisor, Port de la Bourdonnais, Pont de l'Alma). Keep the site name "The Cruise Detective" in English. Well-known landmarks take their usual {lang} name.
- Keep numbers, prices, currencies, dates, times, ratings, pier numbers and URLs exactly.
- Do not use em dashes (—); use a comma, colon or en dash with spaces instead.
- Do not add claims about being independent, unbiased, unsponsored, undercover, anonymous or paying for our own tickets, even if the wording would make them sound natural.
- Return every id you were given, once, with its translation."""

SCHEMA = {
    "type": "object",
    "properties": {
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "html": {"type": "string"}},
                "required": ["id", "html"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["items"],
    "additionalProperties": False,
}


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


def load_env_key():
    if os.environ.get("ANTHROPIC_API_KEY"):
        return
    import subprocess
    candidates = [os.path.join(ROOT, ".env")]
    try:  # in a git worktree, .env lives in the main checkout
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if common:
            candidates.append(os.path.join(os.path.dirname(os.path.abspath(os.path.join(ROOT, common))), ".env"))
    except OSError:
        pass
    for env in candidates:
        if not os.path.exists(env):
            continue
        for line in open(env, encoding="utf-8"):
            if line.startswith("ANTHROPIC_API_KEY="):
                os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
                return


def url_to_file(url):
    p = urllib.parse.unquote(url.split(SITE, 1)[-1]).strip("/")
    for c in ([p + ".html", p + "/index.html"] if p else ["index.html"]):
        if os.path.isfile(os.path.join(ROOT, c)):
            return c
    rw = {r["source"]: r["destination"] for r in json.loads(read("vercel.json")).get("rewrites", []) if ":" not in r["source"]}
    d = rw.get("/" + p)
    if d:
        for c in [d.strip("/") + ".html", d.strip("/") + "/index.html"]:
            if os.path.isfile(os.path.join(ROOT, c)):
                return c
    return None


def alternates(html):
    return {lg: href for href, lg in re.findall(r'<link href="([^"]+)" hreflang="([a-zA-Z-]+)" rel="alternate"', html)}


def link_map():
    """EN internal path -> {lang: localized path}, from the hreflang tags of every EN page."""
    out = {}
    locs = re.findall(r"<loc>([^<]*)</loc>", read("sitemap.xml"))
    for u in locs:
        path = "/" + u.split(SITE, 1)[-1].strip("/")
        if re.match(r"^/[a-z]{2}(/|$)", path) and path.split("/")[1] in LANG_NAMES:
            continue
        f = url_to_file(u)
        if not f:
            continue
        alts = alternates(read(f))
        out[path.rstrip("/") or "/"] = {lg: "/" + h.split(SITE, 1)[-1].strip("/") for lg, h in alts.items()}
    return out


# ---------------------------------------------------------------- segments
def is_leaf_block(el):
    if el.name in INLINE or el.name in SKIP:
        return False
    has_text = False
    for c in el.children:
        if isinstance(c, Comment):
            continue
        if isinstance(c, NavigableString):
            if c.strip():
                has_text = True
        elif c.name in INLINE:
            if c.get_text(strip=True):
                has_text = True
            if any(d.name and d.name not in INLINE for d in c.find_all(True)):
                return False
        else:
            if c.name not in SKIP and c.get_text(strip=True):
                return False
    return has_text


def translatable(text):
    t = re.sub(r"<[^>]+>", "", text)
    return bool(re.search(r"[A-Za-z]{2}", t))


def _skip(el):
    """Skipped tags; the dinner page's menu-modal templates are translated like page content."""
    return el.name in SKIP and not (el.name == "template" and (el.get("id") or "").startswith("dc-menu-"))


MENU_TPL_ATTRS = ("data-title", "data-price", "data-sub")


def collect(soup):
    """Return list of (kind, ref, source_html). kind: 'inner' | 'text' | 'attr' | 'meta' | 'title' | 'jsonld'."""
    segs = []
    body = soup.body
    hdr = body.find("header", class_="ltt-navbar")
    ftr = body.find(lambda t: t.name in ("footer", "section") and "footer-dark" in (t.get("class") or []))

    def in_chrome(el):
        return (hdr and (el is hdr or hdr in el.parents)) or (ftr and (el is ftr or ftr in el.parents))

    done = set()
    for el in body.find_all(True):
        if in_chrome(el) or _skip(el) or any(_skip(p) for p in el.parents):
            continue
        if any(id(p) in done for p in el.parents):
            continue
        if is_leaf_block(el):
            inner = el.decode_contents()
            if translatable(inner):
                segs.append(("inner", el, inner))
            done.add(id(el))
    # loose text nodes in mixed containers
    for s in body.find_all(string=True):
        if isinstance(s, Comment) or not s.strip() or not translatable(s):
            continue
        el = s.parent
        if in_chrome(el) or _skip(el) or any(_skip(p) for p in el.parents):
            continue
        if id(el) in done or any(id(p) in done for p in el.parents):
            continue
        segs.append(("text", s, str(s)))
    for el in body.find_all(True):
        if in_chrome(el):
            continue
        for a in ATTRS:
            v = el.get(a)
            if isinstance(v, str) and translatable(v):
                segs.append(("attr", (el, a), v))
    for el in body.find_all("template"):
        if not _skip(el):
            for a in MENU_TPL_ATTRS:
                v = el.get(a)
                if isinstance(v, str) and translatable(v):
                    segs.append(("attr", (el, a), v))
    if soup.title and soup.title.string and translatable(soup.title.string):
        segs.append(("title", soup.title, soup.title.string))
    for m in soup.find_all("meta"):
        key = m.get("name") or m.get("property") or ""
        if key in ("description", "og:title", "og:description", "twitter:title", "twitter:description", "og:image:alt") and translatable(m.get("content", "")):
            segs.append(("meta", m, m["content"]))
    for sc in soup.find_all("script"):
        m = re.search(r"window\.LTT_PAGE_CONFIG\s*=\s*(\{.*?\});", sc.string or "", re.S)
        if m:
            try:
                cfg = json.loads(m.group(1))
                cfg.setdefault("pickLabel", "PICK")  # floating bar badge text; JS falls back to English
                segs.append(("pagecfg", sc, cfg))
            except ValueError:
                pass
    for sc in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(sc.string or "")
        except ValueError:
            continue
        segs.append(("jsonld", sc, data))
    return segs


def jsonld_strings(node, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in JSONLD_KEYS and isinstance(v, str) and translatable(v) and not v.startswith("http"):
                acc.append(v)
            else:
                jsonld_strings(v, acc)
    elif isinstance(node, list):
        for v in node:
            jsonld_strings(v, acc)


def jsonld_apply(node, tr):
    if isinstance(node, dict):
        return {k: (tr.get(v, v) if k in JSONLD_KEYS and isinstance(v, str) else jsonld_apply(v, tr)) for k, v in node.items()}
    if isinstance(node, list):
        return [jsonld_apply(v, tr) for v in node]
    return node


def cfg_strings(node, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if k.lower().endswith("id") or k.lower() in ("href", "url", "anchor"):
                continue
            cfg_strings(v, acc)
    elif isinstance(node, list):
        for v in node:
            cfg_strings(v, acc)
    elif isinstance(node, str) and translatable(node) and not node.startswith(("http", "#", "/")):
        acc.append(node)


def cfg_apply(node, tr, k=""):
    if isinstance(node, dict):
        return {kk: (v if kk.lower().endswith("id") or kk.lower() in ("href", "url", "anchor") else cfg_apply(v, tr, kk)) for kk, v in node.items()}
    if isinstance(node, list):
        return [cfg_apply(v, tr, k) for v in node]
    if isinstance(node, str):
        return tr.get(node, node)
    return node


def key(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


# ---------------------------------------------------------------- translation
CACHE_ONLY = False   # --cache-only: build from data/i18n/port only, no API calls
DUMP_TODO = None     # --dump-todo DIR: write untranslated segments as {id: html} and skip the build


class _Todo(Exception):
    pass


def translate(strings, lang, cache_path, dry_run):
    cache = json.load(open(cache_path, encoding="utf-8")) if os.path.exists(cache_path) else {}
    todo = [s for s in dict.fromkeys(strings) if key(s) not in cache]
    if dry_run:
        return {s: cache.get(key(s), s) for s in strings}
    if CACHE_ONLY:
        if DUMP_TODO:
            os.makedirs(DUMP_TODO, exist_ok=True)
            out = os.path.join(DUMP_TODO, f"{lang}.json")
            json.dump({key(s): s for s in todo}, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            print(f"  {lang}: {len(todo)} untranslated segments written to {out}")
            raise SystemExit(0) if not todo else _Todo()
        if todo:
            raise RuntimeError(f"{lang}: {len(todo)} segments missing from the cache (run with --dump-todo)")
    if todo:
        import anthropic
        client = anthropic.Anthropic()
        batch, size = [], 0
        batches = []
        for s in todo:
            if batch and size + len(s) > 12000:
                batches.append(batch); batch, size = [], 0
            batch.append(s); size += len(s)
        if batch:
            batches.append(batch)
        for i, b in enumerate(batches, 1):
            payload = [{"id": key(s), "html": s} for s in b]
            with client.messages.stream(
                model=MODEL,
                max_tokens=64000,
                system=SYSTEM.format(lang=LANG_NAMES[lang]),
                output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
                messages=[{"role": "user", "content": json.dumps({"items": payload}, ensure_ascii=False)}],
            ) as stream:
                msg = stream.get_final_message()
            if msg.stop_reason not in ("end_turn",):
                raise RuntimeError(f"{lang} batch {i}: stop_reason={msg.stop_reason}")
            text = next(bl.text for bl in msg.content if bl.type == "text")
            got = {it["id"]: it["html"] for it in json.loads(text)["items"]}
            missing = [p["id"] for p in payload if p["id"] not in got]
            if missing:
                raise RuntimeError(f"{lang} batch {i}: {len(missing)} ids missing in response")
            cache.update(got)
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)
            json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
            print(f"  {lang}: batch {i}/{len(batches)} ({len(b)} segments)", flush=True)
    return {s: cache[key(s)] for s in strings}


def tags_of(h):
    """Tags with translatable attribute values blanked, so translated tooltips/alt text still match."""
    norm = lambda t: re.sub(r'\b(%s)="[^"]*"' % "|".join(ATTRS), r'\1=""', t)
    return sorted(norm(t) for t in re.findall(r"<[^>]+>", h))


# ---------------------------------------------------------------- build
def strip_listicle(soup):
    """Cards -> one <!-- listicle:cards --> marker (listicle.py build-lang renders them); the
    English-only AI cruise finder (comment, styles, form, script) is removed."""
    cards = [d for d in soup.find_all("div", class_="bpa-card") if not d.find_parent("div", class_="bpa-card")]
    if cards:
        cards[0].insert_before(Comment(" listicle:cards "))
        for prev, c in zip(cards, cards[1:]):
            for sib in list(prev.next_siblings):
                if sib is c:
                    break
                if isinstance(sib, NavigableString) and not sib.strip():
                    sib.extract()
        for c in cards:
            c.extract()
    for com in soup.find_all(string=lambda t: isinstance(t, Comment) and "AI cruise finder" in t):
        node = com
        while node is not None:
            nxt = node.next_sibling
            if getattr(node, "name", None) == "div" and "cd-frow" in (node.get("class") or []):
                break
            node.extract()
            node = nxt


def port(en_file, lang, target_file, links, dry_run, listicle_cards=False):
    en_html = read(en_file)
    soup = BeautifulSoup(en_html, "html.parser")
    if listicle_cards:
        strip_listicle(soup)
    segs = collect(soup)
    strings = []
    for kind, ref, src in segs:
        if kind == "jsonld":
            jsonld_strings(src, strings)
        elif kind == "pagecfg":
            cfg_strings(src, strings)
        else:
            strings.append(src)
    page = os.path.splitext(en_file.replace("/", "__"))[0]
    tr = translate(strings, lang, os.path.join(ROOT, "data", "i18n", "port", page, f"{lang}.json"), dry_run)

    bad = 0
    for kind, ref, src in segs:
        if kind == "inner":
            new = tr[src]
            if tags_of(new) != tags_of(src):
                bad += 1
                new = src if dry_run else new
            ref.clear()
            for node in BeautifulSoup(new, "html.parser").contents:
                ref.append(copy.copy(node))
        elif kind == "text":
            ref.replace_with(tr[src])
        elif kind == "attr":
            el, a = ref
            el[a] = tr[src]
        elif kind == "title":
            ref.string = tr[src]
        elif kind == "meta":
            ref["content"] = tr[src]
        elif kind == "jsonld":
            ref.string = json.dumps(jsonld_apply(src, tr), ensure_ascii=False)
        elif kind == "pagecfg":
            new = json.dumps(cfg_apply(src, tr), ensure_ascii=False)
            ref.string = re.sub(r"(window\.LTT_PAGE_CONFIG\s*=\s*)\{.*?\};", lambda m: m.group(1) + new + ";", ref.string, count=1, flags=re.S)

    target_url = SITE + "/" + target_file.replace("/index.html", "").replace(".html", "")
    html_tag = soup.find("html")
    html_tag["lang"] = lang
    if lang == "he":
        html_tag["dir"] = "rtl"
    elif html_tag.has_attr("dir"):
        del html_tag["dir"]
    can = soup.find("link", rel="canonical")
    if can:
        can["href"] = target_url
    for m in soup.find_all("meta", property="og:url"):
        m["content"] = target_url
    # structured data: the page's own URL and language, not the English page's
    en_url = SITE + "/" + en_file.replace("/index.html", "").replace(".html", "")
    for sc in soup.find_all("script", type="application/ld+json"):
        if sc.string:
            js = re.sub(re.escape(en_url) + r'(?=["#])', target_url, sc.string)
            sc.string = re.sub(r'("inLanguage":\s*")[a-zA-Z-]+(")', lambda m: m.group(1) + lang + m.group(2), js)
    # internal links -> localized equivalents
    for a in soup.find_all("a", href=True):
        h = a["href"]
        if not h.startswith("/") or h.startswith("//"):
            continue
        path, _, frag = h.partition("#")
        path = path.rstrip("/") or "/"
        loc = links.get(path, {}).get(lang)
        if loc:
            a["href"] = loc + (("#" + frag) if frag else "")
    out = keep_chrome(str(soup), target_file)
    with open(os.path.join(ROOT, target_file), "w", encoding="utf-8") as fh:
        fh.write(out)
    return len(strings), bad


def _layout():
    import importlib.util
    spec = importlib.util.spec_from_file_location("tcd_sync_layout", os.path.join(ROOT, "kit", "scripts", "sync_layout.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def keep_chrome(out, target_file):
    """Put back the translated page's own header and footer: the language master supplies the
    menu and footer of every page in that language (sync_layout.py), so they must not be replaced
    by a translation of the English ones."""
    path = os.path.join(ROOT, target_file)
    if not os.path.exists(path):
        return out
    old = read(target_file)
    lay = _layout()
    mo, mn = lay.PAT_HEADER.search(old), lay.PAT_HEADER.search(out)
    if mo and mn:
        out = out[:mn.start()] + mo.group(0) + out[mn.end():]
    fo, fn = lay.find_footer(old), lay.find_footer(out)
    if fo and fn:
        out = out[:fn[0]] + old[fo[0]:fo[1]] + out[fn[1]:]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("en_file")
    ap.add_argument("--langs", default=",".join(LANG_NAMES))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--cache-only", action="store_true",
                    help="no API: build only from cached translations (fill the cache by hand or another tool)")
    ap.add_argument("--listicle-cards", action="store_true",
                    help="leave the cards out (marker for listicle.py build-lang) and drop the EN-only AI finder")
    ap.add_argument("--dump-todo", metavar="DIR",
                    help="with --cache-only: write each language's untranslated segments to DIR/<lang>.json")
    args = ap.parse_args()
    global CACHE_ONLY, DUMP_TODO
    CACHE_ONLY, DUMP_TODO = args.cache_only or bool(args.dump_todo), args.dump_todo
    load_env_key()
    if not args.dry_run and not CACHE_ONLY and not os.environ.get("ANTHROPIC_API_KEY"):
        sys.exit("ANTHROPIC_API_KEY is not set (environment or .env)")
    alts = alternates(read(args.en_file))
    links = link_map()
    for lang in args.langs.split(","):
        href = alts.get(lang)
        target = url_to_file(href) if href else None
        if not target:
            print(f"{lang}: no translated URL for {args.en_file}, skipped")
            continue
        try:
            n, bad = port(args.en_file, lang, target, links, args.dry_run, args.listicle_cards)
        except (_Todo, SystemExit):
            continue
        print(f"{lang}: {target} ({n} strings, {bad} tag mismatches)")


if __name__ == "__main__":
    main()
