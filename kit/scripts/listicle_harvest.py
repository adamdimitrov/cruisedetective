"""Harvest translations a listicle's language page already has, into its card text file.

Shared kit script. Before anything is sent to a translator, every string the site already has a
translation for is reused. For an English listicle page and a language it builds English ->
translation pairs from what is on the site and git:

  1. the old translated page (the page the English page's hreflang link names), aligned with the
     ENGLISH version it was translated from: that version is looked up in the English page's git
     history (the commit whose cards match the translated page best on language-independent things:
     card ids, photo files, link targets, element structure, the numbers in the text); then cards
     are paired (by photos, else by id), and inside a card element by element (same tag and class
     path, same position), text nodes by position (kicker parts split on " • "), photo alt texts
     by photo file; other blocks with the same id on both pages (review sections) the same way;
  2. memories that already exist for the language: other listicles' card files
     (data/listicles/i18n/*/<lang>.json), the kit phrase table, and the page port memories
     (data/i18n/port/*/<lang>.json, keyed by a hash of the English segment).

A pair is kept only when its English side (the OLD English string, never the current page's string
at the same position: that one may have changed since the translation was made) is, word for word,
a string the CURRENT English card data uses (key = the
current fragment, so `build-lang` picks it up as is) and it passes the quality guard:
  - the same numbers (digit runs; covers prices, times, counts, dock numbers), the same currency
    signs and the same links as English: a pair that differs belongs to an older fact and is skipped;
  - the same markup as English (tag sequence, as build-lang checks it);
  - it does not look untranslated: identical to English is accepted only for names (brand, boat and
    place names: capitalised words, no English function words); otherwise skipped, as is a string
    with plain English sentences in it, or one without the language's own script (bg el he ja ko
    ru sr uk);
  - it is a translation of the same text: no colon added or dropped (old pages put rank labels into
    titles), no brackets dropped (dock names), not much shorter or longer, not another name for a
    name (an old operator), and not one translation used for several different English strings
    (old pages repeated the title as every photo's alt text).
New entries are added to data/listicles/i18n/<slug>/<lang>.json "text" (never overwriting an
entry), localized booking links found on the old page to its "urls" (same host only), and where
every entry came from goes to data/listicles/i18n/<slug>/<lang>.harvest.json (plus what was skipped
and why), for the reviewer.

Usage: python3 scripts/listicle_harvest.py <english-page> <lang|all> [--dry-run] [--quiet] [--json]
       (all = every language with an hreflang link on the English page, except English, hu and
       the languages in --skip=hu,xx)
Then: python3 scripts/listicle.py missing <english-page> <lang> --todo=FILE, translate the rest
(listicle.py translate), review, build-lang.
"""
import collections
import difflib
import hashlib
import html as _html
import json
import os
import re
import subprocess
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import listicle as L  # noqa: E402

ROOT = L.ROOT
NONLATIN = {"bg": "CYRILLIC", "ru": "CYRILLIC", "sr": "CYRILLIC", "uk": "CYRILLIC", "el": "GREEK",
            "he": "HEBREW", "ja": "CJK|HIRAGANA|KATAKANA", "ko": "HANGUL"}
# words that are (almost) never words of the other site languages
EN_STOP = {"the", "and", "with", "your", "you", "for", "of", "are", "this", "from", "at", "it", "be",
           "can", "will", "who", "what", "which", "that", "when", "have", "has", "only", "if", "than",
           "they", "their", "there", "but", "not", "or", "on", "by", "about", "after", "before", "per",
           "into", "more", "most", "just", "also", "every", "each", "free", "book", "booking", "ride"}
CURRENCY = re.compile(r"€|\$|£|Ft\b|HUF|EUR|USD")
ATTR_RE = re.compile(r'([^\s="/>]+)="([^"]*)"')
SKEL_SKIP = {"img", "svg", "path", "source", "br", "!--"}


# ------------------------------------------------------------------ small helpers
def nfc(s):
    return unicodedata.normalize("NFC", s)


def norm(s):
    """Comparison form of a fragment: entities decoded, whitespace collapsed."""
    s = _html.unescape(re.sub(r"&#x27;|&#39;", "'", s))
    return nfc(re.sub(r"\s+", " ", s).strip())


LEAD_SYM = re.compile(r"^[^\w<&(\[\"'„«¿¡]+(?=\w)")


def lead_sym(s):
    m = LEAD_SYM.match(norm(s))
    return m.group(0) if m else ""


def loose(s):
    """Looser comparison form: letter case and a leading symbol (✓, emoji) ignored."""
    n = norm(s)
    return n[len(lead_sym(s)):].casefold()


def plain(s):
    return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()


def words(s):
    return re.findall(r"[^\W\d_]+", plain(s))


def digits(s):
    """Digit runs of the visible text and links (language independent facts)."""
    t = unicodedata.normalize("NFKC", _html.unescape(re.sub(r"<(?!a\b)[^>]+>", " ", s)))
    t = re.sub(r'<a\b[^>]*href="([^"]*)"[^>]*>', r" \1 ", t)
    return sorted(re.findall(r"\d+", t))


def currency(s):
    return sorted(CURRENCY.findall(_html.unescape(s)))


def attrs(node):
    return dict(ATTR_RE.findall(node.start)) if node.start.startswith("<") else {}


def sig(node):
    return (node.tag, attrs(node).get("class", ""))


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout


def mem_key(s):
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:12]


def colons(s):
    return len(re.findall(r"[:：]", plain(s)))


def same_target(en, t, lang):
    """t is the language version of the booking page en: same host and query, a path in the
    language (/<lang>/...). Other differences (another product, tracking tags) are not."""
    from urllib.parse import urlsplit
    a, b = urlsplit(en), urlsplit(t)
    return (a.netloc == b.netloc and a.query == b.query and a.path != b.path
            and re.match(r"/%s(/|$)" % re.escape(lang), b.path) is not None)


def is_name(s):
    """A brand / boat / place name (kept as is in every language)."""
    w = words(s)
    if not w or len(w) > 6 or any(x.lower() in EN_STOP for x in w):
        return False
    return all(x[0].isupper() or not x.isascii() for x in w)


def has_script(s, lang):
    pat = NONLATIN.get(lang)
    if not pat:
        return True
    rx = re.compile(pat)
    return any(rx.search(unicodedata.name(ch, "")) for ch in plain(s) if ch.isalpha())


def looks_english(s):
    w = [x.lower() for x in words(s) if x.isascii()]
    hits = sum(1 for x in w if x in EN_STOP)
    return len(w) >= 4 and hits >= 2 and hits / max(1, len(words(s))) >= 0.15


def guard(en, tr, lang, plain_target=False):
    """None when the pair may be used, else the reason it is skipped."""
    if not tr or not tr.strip():
        return "empty"
    if digits(en) != digits(tr):
        return "numbers differ (older fact)"
    if currency(en) != currency(tr):
        return "currency differs"
    if not plain_target:
        if L.links_of(en) != L.links_of(tr):
            return "links differ"
        if L.tags_of(en) != L.tags_of(tr):
            return "markup differs"
    if norm(en) == norm(tr):
        return None if is_name(en) else "identical to English"
    if colons(en) != colons(tr):
        return "colon added or dropped (old label?)"
    if plain(en).count("(") != plain(tr).count("("):
        return "brackets added or dropped (part of the text missing?)"
    ratio = len(plain(tr)) / max(1, len(plain(en)))
    if len(plain(en)) > 8 and (ratio < (0.2 if lang in ("ja", "ko") else 0.5) or ratio > 2.5):
        return "much shorter or longer than English (another or older text)"
    if is_name(en) and not digits(en):
        # a brand or operator name replaced by another one (an old operator name, another boat):
        # the translation is itself a name of two or more words sharing no word stem with English
        we = {x.casefold()[:4] for x in words(en)}
        wt = words(tr)
        if (len(wt) >= 2 and all(x.isascii() and x[0].isupper() for x in wt)
                and not we & {x.casefold()[:4] for x in wt}):
            return "another name"
    if lang in NONLATIN and not has_script(tr, lang) and not is_name(en):
        return "not in the language's script"
    if looks_english(tr) and not looks_english_too(en, tr):
        return "reads as English"
    return None


def looks_english_too(en, tr):
    """English words in the translation that are just copied names from English (Legenda City
    Cruises ...) do not count: compare with the English words that are capitalised."""
    names = {x.lower() for x in words(en) if x[0].isupper()}
    w = [x.lower() for x in words(tr) if x.isascii() and x.lower() in EN_STOP and x.lower() not in names]
    return len(w) < 2


def fit(cur, tr, src_plain, plain_target):
    """The translation in the form of the current English string: same outer whitespace, plain
    text for attribute values (photo alt), HTML for fragments."""
    if src_plain and not plain_target:
        tr = tr.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    elif plain_target and not src_plain:
        if "<" in tr:
            return None
        tr = _html.unescape(tr)
    if not re.match(r"\s*[,;:]", cur):
        tr = re.sub(r"^\s*[,;:]\s*", "", tr)
    lead = cur[:len(cur) - len(cur.lstrip())]
    trail = cur[len(cur.rstrip()):]
    return lead + tr.strip() + trail


# ------------------------------------------------------------------ page structure
def tree_of(chunk):
    try:
        return L.parse(chunk)
    except ValueError:
        return None


def cards_of(src):
    out = []
    try:
        spans = L.card_spans(src)
    except SystemExit:
        return out
    for s, e in spans:
        t = tree_of(src[s:e])
        if t and t.elems():
            out.append(t.elems()[0])
    return out


def walk(node):
    yield node
    for c in node.ch:
        if not isinstance(c, str):
            yield from walk(c)


def photos(node):
    out = []
    for n in walk(node):
        if n.tag == "img":
            a = attrs(n)
            for k in ("data-src", "src"):
                v = a.get(k, "")
                if v and not v.startswith("data:"):
                    out.append((_html.unescape(v).rsplit("/", 1)[-1], _html.unescape(a.get("alt", ""))))
                    break
    return out


def skeleton(node):
    return tuple("%s.%s" % sig(n) for n in walk(node) if n.tag not in SKEL_SKIP and n.tag)


def card_features(card):
    ph = photos(card)
    return {"id": attrs(card).get("id"), "photos": {p for p, _ in ph}, "skel": skeleton(card),
            "digits": collections.Counter(digits(card.inner()))}


def card_score(e, t):
    ph = len(e["photos"] & t["photos"]) / max(1, len(e["photos"] | t["photos"]))
    sm = difflib.SequenceMatcher(None, e["skel"], t["skel"], autojunk=False)
    sk = sm.quick_ratio()
    if sk > 0.5:
        sk = sm.ratio()
    dg = sum((e["digits"] & t["digits"]).values()) / max(1, sum((e["digits"] | t["digits"]).values()))
    return ph + sk + dg


def pair_cards(ecards, tcards):
    """[(english card, translated card)] matched by photos, else by id."""
    out, used = [], set()
    ef = [card_features(c) for c in ecards]
    for tc in tcards:
        tf = card_features(tc)
        best, bi = 0, None
        for i, f in enumerate(ef):
            if i in used:
                continue
            ov = len(f["photos"] & tf["photos"]) / max(1, len(f["photos"] | tf["photos"]))
            if ov > best:
                best, bi = ov, i
        if bi is None or best < 0.3:
            # by id only when neither card has photos (a changed lineup reuses ids for other cruises)
            bi = next((i for i, f in enumerate(ef) if i not in used and f["id"] and f["id"] == tf["id"]
                       and not f["photos"] and not tf["photos"]), None)
        if bi is not None:
            used.add(bi)
            out.append((ecards[bi], tc))
    return out


def page_score(ecards, tcards):
    pairs = pair_cards(ecards, tcards)
    if not pairs:
        return 0.0
    s = sum(card_score(card_features(e), card_features(t)) for e, t in pairs)
    return s / max(len(ecards), len(tcards))


# ------------------------------------------------------------------ alignment
def split_kicker(s):
    return [x for x in re.split(r"\s*•\s*", s)]


def align(e, t, where, out):
    """Pair e (English) and t (translation) node by node. Appends (english, translation, where,
    is_plain) for every element whose whole subtree lines up, every text node and every alt/title.
    Returns True when the two subtrees are isomorphic."""
    iso = True
    ea, ta = attrs(e), attrs(t)
    for k in ("alt", "title", "aria-label", "placeholder"):
        if k in ea and k in ta:
            out.append((_html.unescape(ea[k]), _html.unescape(ta[k]), f"{where}@{k}", True))
    ek = [c for c in e.ch if not (isinstance(c, str) and not c.strip())]
    tk = [c for c in t.ch if not (isinstance(c, str) and not c.strip())]
    eel = [c for c in ek if not isinstance(c, str)]
    tel = [c for c in tk if not isinstance(c, str)]
    if [sig(c) for c in eel] == [sig(c) for c in tel]:
        for i, (a, b) in enumerate(zip(eel, tel)):
            iso &= align(a, b, f"{where}/{a.tag}[{i}]", out)
    else:
        # the children differ: pair only elements whose tag + class occurs once on each side
        iso = False
        ce = collections.Counter(sig(c) for c in eel)
        ct = collections.Counter(sig(c) for c in tel)
        for i, a in enumerate(eel):
            if ce[sig(a)] == 1 and ct[sig(a)] == 1 and sig(a)[1]:
                b = next(c for c in tel if sig(c) == sig(a))
                align(a, b, f"{where}/{a.tag}~{i}", out)
    etx = [c for c in ek if isinstance(c, str)]
    ttx = [c for c in tk if isinstance(c, str)]
    if len(etx) == len(ttx):
        for i, (a, b) in enumerate(zip(etx, ttx)):
            out.append((a, b, f"{where}/text()[{i}]", False))
            pa, pb = split_kicker(a), split_kicker(b)
            if len(pa) == len(pb) > 1:
                for j, (x, y) in enumerate(zip(pa, pb)):
                    if x.strip():
                        out.append((x, y, f"{where}/text()[{i}]•{j}", False))
    else:
        iso = False
    kinds_e = ["t" if isinstance(c, str) else sig(c) for c in ek]
    kinds_t = ["t" if isinstance(c, str) else sig(c) for c in tk]
    iso &= kinds_e == kinds_t
    if iso and e.tag:
        out.append((e.inner(), t.inner(), where, False))
        out.append((e.outer(), t.outer(), where + " (outer)", False))
        if e.tag == "a":
            href_e, href_t = _html.unescape(ea.get("href", "")), _html.unescape(ta.get("href", ""))
            out.append((href_e, href_t, f"{where}@href", "url"))
    elif e.tag == "a":
        out.append((_html.unescape(ea.get("href", "")), _html.unescape(ta.get("href", "")), f"{where}@href", "url"))
    return iso


def id_blocks(src, skip_spans):
    """{id: Node} of id'd blocks outside the card region (review sections etc.), outermost only."""
    out, taken = {}, list(skip_spans)
    for m in re.finditer(r'<(section|div|article|details)\b[^>]*\bid="([^"]+)"[^>]*>', src):
        if any(a <= m.start() < b for a, b in taken):
            continue
        tagname, depth = m.group(1), 0
        for t in re.finditer(r"<(/?)%s\b[^>]*>" % tagname, src[m.start():]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                end = m.start() + t.end()
                break
        else:
            continue
        if end - m.start() > 400000:
            continue
        node = tree_of(src[m.start():end])
        if node and node.elems():
            out[m.group(2)] = node.elems()[0]
            taken.append((m.start(), end))
    return out


def align_pages(esrc, tsrc, label):
    out = []
    for e, t in pair_cards(cards_of(esrc), cards_of(tsrc)):
        align(e, t, f"{label} {attrs(e).get('id', '?')}", out)
        # photo alt texts by photo file (galleries can be reordered or trimmed)
        ealt = dict(photos(e))
        for p, alt in photos(t):
            if p in ealt and ealt[p] and alt:
                out.append((ealt[p], alt, f"{label} {attrs(e).get('id', '?')} photo {p}", True))
    try:
        es, ee, _ = L.region(esrc)
        ts, te, _ = L.region(tsrc)
    except SystemExit:
        return out
    eb, tb = id_blocks(esrc, [(es, ee)]), id_blocks(tsrc, [(ts, te)])
    for k in eb:
        if k in tb and sig(eb[k]) == sig(tb[k]):
            align(eb[k], tb[k], f"{label} #{k}", out)
    return out


# ------------------------------------------------------------------ English history
_VERSIONS = {}


def english_versions(en_page):
    """[(commit, date, src, cards)] of every distinct card region of the English page, newest first
    (the working tree first when it differs from HEAD)."""
    rel = os.path.relpath(en_page, ROOT)
    if rel in _VERSIONS:
        return _VERSIONS[rel]
    seen, out = set(), []
    cur = open(en_page, encoding="utf-8").read()
    revs = [("worktree", "", None)] + [tuple(x.split(" ", 1)) + (1,) for x in
                                        git("log", "--format=%h %cs", "--", rel).split("\n") if x]
    for rev in revs:
        src = cur if rev[0] == "worktree" else git("show", f"{rev[0]}:{rel}")
        try:
            s, e, _ = L.region(src)
        except SystemExit:
            continue
        h = hashlib.sha1(src[s:e].encode()).hexdigest()
        if h in seen:
            continue
        seen.add(h)
        out.append((rev[0], rev[1], src, cards_of(src)))
    _VERSIONS[rel] = out
    return out


def best_version(en_page, tsrc):
    tcards = cards_of(tsrc)
    best, pick = -1.0, None
    for v in english_versions(en_page):
        if not v[3]:
            continue
        sc = page_score(v[3], tcards)
        if sc > best + 1e-9:
            best, pick = sc, v
    return pick, best


# ------------------------------------------------------------------ memories
def memories(en_page, lang):
    """[(name, {english: translation} or None, {hash: translation} or None, {en url: url})]."""
    out = []
    slug = L.slug_of(en_page)
    base = os.path.join(ROOT, "data", "listicles", "i18n")
    if os.path.isdir(base):
        for d in sorted(os.listdir(base)):
            p = os.path.join(base, d, lang + ".json")
            if d != slug and os.path.exists(p):
                f = json.load(open(p, encoding="utf-8"))
                out.append((f"listicle file {d}/{lang}.json", f.get("text", {}), None, f.get("urls", {})))
    kit = os.path.join(L.I18N_KIT, lang + ".json")
    if os.path.exists(kit):
        out.append((f"kit table {lang}.json", json.load(open(kit, encoding="utf-8")).get("text", {}), None, {}))
    port = os.path.join(ROOT, "data", "i18n", "port")
    if os.path.isdir(port):
        dirs = sorted(os.listdir(port), key=lambda d: (d != slug, d))
        for d in dirs:
            p = os.path.join(port, d, lang + ".json")
            if os.path.exists(p):
                try:
                    out.append((f"port memory {d}/{lang}.json", None, json.load(open(p, encoding="utf-8")), {}))
                except ValueError:
                    pass
    return out


def variants(s):
    """Forms an English fragment may have been stored under in a port memory (BeautifulSoup output):
    as is, with quotes decoded, and for tagless strings plain or minimally escaped."""
    out = [s]
    q = re.sub(r"&#x27;|&#39;", "'", s).replace("&quot;", '"')
    out.append(q)
    if "<" not in s:
        p = _html.unescape(s)
        out += [p, p.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")]
    st = [x.strip() for x in out]
    return list(dict.fromkeys(out + st))


# ------------------------------------------------------------------ harvest
def needed(en_page, lang, data):
    tr = L.Lang(en_page, lang)
    tr.translate(data)
    miss = list(dict.fromkeys(s for _, s in tr.missing))
    plain_paths = set()
    for path in L.text_leaves(data):
        if "photos" in path:
            plain_paths.add(L.get_in(data, path))
    return miss, plain_paths, tr


def harvest(en_page, lang, dry_run=False, verbose=True):
    data = json.load(open(L.data_path(en_page), encoding="utf-8"))
    miss, plain_set, tr = needed(en_page, lang, data)
    want = {}
    for s in miss:
        want.setdefault(norm(s), []).append(s)
    cands = collections.defaultdict(list)    # current english -> [(translation, source, prio)]
    skipped = []
    url_cands, url_src = {}, {}
    info = {}

    en_urls = set()

    def collect(v):
        if isinstance(v, dict):
            for k, x in v.items():
                if k == "url" and isinstance(x, str):
                    en_urls.add(x)
                else:
                    collect(x)
        elif isinstance(v, list):
            for x in v:
                collect(x)
        elif isinstance(v, str):
            en_urls.update(_html.unescape(u) for u in re.findall(r'\bhref="([^"]*)"', v))
    collect(data["cards"])

    want_loose = {}
    for s in miss:
        want_loose.setdefault(loose(s), []).append(s)

    def offer(en, t, source, prio, src_plain):
        if src_plain == "url":
            if en in en_urls and t and t != en and en not in tr.urls and same_target(en, t, lang):
                url_cands.setdefault(en, collections.Counter())[t] += 1
                url_src.setdefault((en, t), source)
            return
        exact = want.get(norm(en), [])
        # short fragments of running text (review sections) only word for word: out of context
        # they are often inflected ("with unlimited prosecco")
        loose_ok = " #" not in source
        for cur in exact or (want_loose.get(loose(en), []) if loose_ok else []):
            pt = cur in plain_set
            t1 = nfc(t)
            if not exact:
                # matched apart from letter case or a leading symbol (✓, emoji): the translation
                # takes the current English string's leading symbol, never the old one
                if lead_sym(en) and not t1.startswith(lead_sym(en)):
                    continue
                t1 = lead_sym(cur) + t1[len(lead_sym(en)):].lstrip() if lead_sym(en) else lead_sym(cur) + t1
                source, prio = source + " (loose: case/symbol)", prio + 0.5
            t2 = fit(cur, t1, src_plain, pt)
            if t2 is None:
                continue
            why = guard(cur, t2, lang, plain_target=pt)
            if why:
                skipped.append({"en": cur, "tr": t2, "why": why, "source": source})
            else:
                cands[cur].append((t2, source, prio))

    # 1 + 2: the old translated page against the English version it came from (and the current one)
    try:
        tpage = L.lang_page(en_page, lang)
    except SystemExit as e:
        tpage = None
        info["page"] = str(e)
    if tpage:
        tsrc = open(tpage, encoding="utf-8").read()
        ver, score = best_version(en_page, tsrc)
        info["page"] = os.path.relpath(tpage, ROOT)
        if ver:
            info["english_version"] = f"{ver[0]} {ver[1]}".strip()
            info["match_score"] = round(score, 3)
            for en, t, where, p in align_pages(ver[2], tsrc, f"{lang} page vs EN {ver[0]}"):
                offer(en, t, where, 0, p)

    # 3: memories
    for name, by_text, by_hash, by_url in memories(en_page, lang):
        for en, t in by_url.items():
            offer(en, t, name, 2, "url")
        for n, curs in want.items():
            for cur in curs:
                if by_text is not None:
                    if cur in by_text:
                        offer(cur, by_text[cur], name, 2, cur in plain_set)
                    continue
                for v in variants(cur):
                    k = mem_key(v)
                    if k in by_hash and isinstance(by_hash[k], str):
                        t = by_hash[k]
                        src_plain = "<" not in t and not re.search(r"&(?:\w+|#\w+);", t)
                        offer(cur, t, f"{name} [{k}]", 3, src_plain)
                        break

    chosen, prov = {}, {}
    for cur, lst in cands.items():
        best_p = min(p for _, _, p in lst)
        top = [x for x in lst if x[2] == best_p]
        cnt = collections.Counter(t for t, _, _ in top)
        t, n = cnt.most_common(1)[0]
        chosen[cur] = t
        others = sorted({x for x, _, _ in lst if x != t})
        prov[cur] = {"source": next(s for x, s, _ in top if x == t), "seen": n,
                     **({"alternatives": others[:3]} if others else {})}
    by_tr = collections.defaultdict(set)
    for cur, t in chosen.items():
        by_tr[norm(t)].add(loose(cur))
    for cur in list(chosen):
        if len(by_tr[norm(chosen[cur])]) > 1:
            skipped.append({"en": cur, "tr": chosen[cur], "source": prov[cur]["source"],
                            "why": "same translation for different English strings"})
            del chosen[cur], prov[cur]
    urls = {}
    for en, c in url_cands.items():
        urls[en] = c.most_common(1)[0][0]

    # skipped: only those that were not filled from another source
    skipped = [s for s in skipped if s["en"] not in chosen]
    dedup, seen = [], set()
    for s in skipped:
        k = (s["en"], s["tr"])
        if k not in seen:
            seen.add(k)
            dedup.append(s)
    skipped = dedup

    path = tr.path
    page = json.load(open(path, encoding="utf-8")) if os.path.exists(path) else {"format": 1, "lang": lang}
    text = page.setdefault("text", {})
    added = {k: v for k, v in chosen.items() if k not in text}
    order = [L.get_in(data, p) for p in L.text_leaves(data)]
    new_text = dict(text)
    for k in order:
        if k in added and k not in new_text:
            new_text[k] = added[k]
    page["text"] = new_text
    new_urls = {k: v for k, v in urls.items() if k not in page.get("urls", {})}
    if new_urls:
        page["urls"] = {**page.get("urls", {}), **new_urls}

    still = [s for s in miss if s not in added]
    res = {"lang": lang, "page": info.get("page"), "english_version": info.get("english_version"),
           "match_score": info.get("match_score"), "needed": len(miss), "harvested": len(added),
           "urls": len(new_urls), "missing": len(still),
           "missing_words": sum(len(words(s)) for s in still), "skipped": len(skipped),
           "skipped_why": dict(collections.Counter(s["why"] for s in skipped))}
    if not dry_run and (added or new_urls):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(L.dumps(page) + "\n")
        hpath = path[:-5] + ".harvest.json"
        old = json.load(open(hpath, encoding="utf-8")) if os.path.exists(hpath) else {}
        side = {"format": 1, "lang": lang,
                "comment": "Where each harvested entry of %s came from (listicle_harvest.py). Review, then "
                           "delete this file or keep it as a record." % os.path.basename(path),
                "page": info.get("page"), "english_version": info.get("english_version"),
                "match_score": info.get("match_score"),
                "entries": {**old.get("entries", {}), **{k: prov[k] for k in order if k in added}},
                "urls": {**old.get("urls", {}), **{k: {"to": v, "source": url_src.get((k, v), "")}
                                                   for k, v in new_urls.items()}},
                "skipped": skipped}
        with open(hpath, "w", encoding="utf-8") as fh:
            fh.write(L.dumps(side) + "\n")
        # what build-lang still lacks: it also carries numbers over ("17k+ reviews" -> "1.2k+ reviews")
        after = L.Lang(en_page, lang)
        after.translate(data)
        still = list(dict.fromkeys(s for _, s in after.missing))
        res.update(missing=len(still), missing_words=sum(len(words(s)) for s in still),
                   numbers_carried=len(after.renumbered))
    if verbose:
        print(f"{os.path.relpath(en_page, ROOT)} {lang}: needed {res['needed']}, harvested {res['harvested']}"
              f" (+{res['urls']} urls), still missing {res['missing']} (~{res['missing_words']} words); "
              f"EN version {res['english_version']} (score {res['match_score']}); skipped {res['skipped']} "
              f"{res['skipped_why']}")
    return res


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    opts = {a.split("=")[0]: (a.split("=", 1)[1] if "=" in a else True) for a in argv if a.startswith("--")}
    if len(args) != 2:
        print(__doc__)
        return 2
    page = args[0] if os.path.isabs(args[0]) or os.path.exists(args[0]) else os.path.join(ROOT, args[0])
    page = os.path.abspath(page)
    if args[1] == "all":
        src = open(page, encoding="utf-8").read()
        skip = {"en", "x-default"} | set(str(opts.get("--skip", "hu")).split(","))
        langs = [x for x in dict.fromkeys(re.findall(r'hreflang="([^"]+)"', src)) if x not in skip]
    else:
        langs = args[1].split(",")
    results = [harvest(page, lang, dry_run=bool(opts.get("--dry-run")), verbose=not opts.get("--quiet"))
               for lang in langs]
    if opts.get("--json"):
        print(json.dumps(results, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
