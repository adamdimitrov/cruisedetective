"""Listicle cards: page <-> structured JSON (river / dinner cruise card design).

Shared kit script. A "listicle" page is a comparison article whose ranked offers are
`<div class="bpa-card" ... id="card-N">` blocks (the design of best-budapest-river-cruises
and best-dinner-cruises-budapest). This script moves those cards between the page and a
data file so cards can be edited (or generated for a new page) as data:

  extract <page.html>   cards of the page -> data/listicles/<slug>.json
  build   <page.html>   data/listicles/<slug>.json -> the page's card region
                        (everything outside the region is left byte for byte)
  stats   <page.html>   how much of each card is structured vs kept as HTML

The card region runs from the first card's `<div class="bpa-card"` to the end of the last
card. A page with no cards yet can hold the marker `<!-- listicle:cards -->` instead; build
replaces it.

Data file: {"format": 1, "icons": {site name: icon data URI}, "cards": [card, ...]}. A card:
  id, cats[]                      card div id ("card-N") and data-cat words; attrs: any other attrs
  gallery   rank {text, medal}, photos [[[attr, value], ...] per <img>, source order],
            thumbs [{src}]        (thumb buttons, "+N more" and "1 / N" pill are derived)
  kicker    [text | {map, url, rel, target, onclick}]   parts joined by " • "
  title     {text, url, rel, target}
  reviews   ratings {stars, score, meta, heading, sites [{kind link|plain|static, site, score,
            count, url, rel, target}]} (or just {meta} for a text-only line); tested {chip, pop_html}
  pills     [{cls, data {langs: ..}, emoji, label, pop_html}]   (summary_html if the summary is
            not "emoji + label")
  slot      {tt (timetable JSON), dur, every}
  best_for  {pick_html, skip_html}
  faq       {items [{q, a}]}      (summary "❓ N questions travellers ask" is derived)
  extras_after_<field>            unmodelled blocks (dinner food meter, dc-opts) as raw HTML
  price     {main, sub, rows [{label, small, price}], total {label, price}, note}
  cta       {btn {url, rel, target, text}, via, trust [line, ...], sublink {url, text}}
  before    text between the previous card and this one when it is not a blank line
Any part that does not fit its model is stored as {"raw": html} in its place.

JSON conventions:
- text fields (labels, titles, questions, ...) are HTML fragments exactly as they appear in
  the page (`&amp;` stays `&amp;`, inline markup allowed); `*_html` fields are free-form
  fragments (popover bodies, Pick/Skip sentences);
- URLs and other attribute values are plain (unescaped) strings;
- keys starting with `_` only record how the source page happens to be formatted (attribute
  order, a line break, a value that differs from the computed default). New cards leave them
  out and get the house format;
- anything not modelled yet is kept as `raw` / `extras_after_<field>` HTML at its exact
  position, so extract -> build is byte-identical.

Language versions (see "language versions" below for the files):
  build-lang <english-page> <lang>   the language page (its hreflang link on the English page) gets the
                                     English cards with text from data/listicles/i18n/<slug>/<lang>.json
                                     and the kit table runtime/listicle/i18n/<lang>.json; facts, photos
                                     and links come from English. Refuses while strings are missing
                                     (--allow-missing builds them in English); --check only compares;
                                     --page=FILE overrides the target page. Refuses a page still in an
                                     older design than English (port it first); afterwards measures the
                                     page in a browser (checks/check_listicle_layout.py; --no-layout skips).
  missing <english-page> <lang>      untranslated strings, numbers carried over, link/markup differences,
                                     unused entries; --todo=FILE writes the untranslated strings as
                                     {"english": ""}; --prune drops unused entries and sorts the file.
  translate <english-page> <lang>    sends the untranslated strings (--todo=FILE from `missing`, else all
                                     missing ones) to the Claude API (model: env LISTICLE_TRANSLATE_MODEL,
                                     default claude-opus-5-5; key: ANTHROPIC_API_KEY or the site's .env) and
                                     writes each translation that passes validate() (same tags, numbers,
                                     times, currency, URLs, placeholders, emoji) to the language file;
                                     failures are reported, never written (--rejects=FILE lists them).
                                     --dry-run prints the prompt, the batches and the estimated size.
                                     First harvest what the site already has: scripts/listicle_harvest.py.

Usage: python3 scripts/listicle.py extract|build|stats <page.html> [--data FILE] [--check]
       python3 scripts/listicle.py build-lang|missing|translate <english-page.html> <lang> [options]
"""
import html as _html
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checks"))
from sitecfg import ROOT  # noqa: E402

MARKER = "<!-- listicle:cards -->"
VOID = {"img", "br", "input", "meta", "source", "hr", "wbr", "link"}
TOKEN = re.compile(r"<!--.*?-->|<(/?)([a-zA-Z][a-zA-Z0-9-]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>", re.S)
ATTR = re.compile(r' ([^\s="/>]+)="([^"]*)"')


# Fixed strings the card template renders itself (not data). English is the default; a language
# build (build-lang) swaps in the kit table runtime/listicle/i18n/<lang>.json "ui" plus the page's own
# overrides. Placeholders: {n} count / card number, {i} photo number.
UI_EN = {
    "faq_title": "❓ {n} questions travellers ask",
    "price_heading": "All ticket prices",
    "pick": "✓ Pick it",
    "skip": "✕ Skip it",
    "photo_prev": "Previous photo",
    "photo_next": "Next photo",
    "gallery_label": "Photo gallery {n}",
    "thumbs_label": "Photo thumbnails",
    "thumb_label": "Show photo {i} of {n}",
}
UI = dict(UI_EN)


class Unmodelled(Exception):
    """The fragment does not have the shape the model expects: keep it as raw HTML."""


# ------------------------------------------------------------------ lossless HTML tree
class Node:
    __slots__ = ("tag", "start", "end", "ch")

    def __init__(self, tag, start):
        self.tag, self.start, self.end, self.ch = tag, start, "", []

    def outer(self):
        return self.start + self.inner() + self.end

    def inner(self):
        return "".join(c if isinstance(c, str) else c.outer() for c in self.ch)

    def attrs(self):
        """[[name, value], ...] in source order, values unescaped. Unmodelled if the start tag
        is not in canonical form (one space, double quotes, every attribute has a value)."""
        m = re.match(r"<[a-zA-Z0-9-]+", self.start)
        rest, out, pos = self.start[m.end():], [], 0
        for a in ATTR.finditer(rest):
            if a.start() != pos:
                break
            out.append([a.group(1), _html.unescape(a.group(2))])
            pos = a.end()
        if rest[pos:] not in (">", "/>"):
            raise Unmodelled(f"non-canonical tag {self.start[:80]}")
        return out

    def a(self):
        return dict(self.attrs())

    def cls(self):
        return self.a().get("class")

    def elems(self):
        return [c for c in self.ch if isinstance(c, Node)]

    def selfclosed(self):
        return self.start.endswith("/>")


def parse(src):
    root = Node(None, "")
    stack, pos = [root], 0
    for m in TOKEN.finditer(src):
        if m.start() > pos:
            stack[-1].ch.append(src[pos:m.start()])
        pos = m.end()
        tok = m.group(0)
        if tok.startswith("<!--"):
            n = Node("!--", tok)
            stack[-1].ch.append(n)
            continue
        tag = m.group(2).lower()
        if m.group(1):
            if stack[-1].tag != tag:
                raise ValueError(f"unbalanced </{tag}> near {src[max(0, m.start() - 80):m.start()]!r}")
            stack[-1].end = tok
            stack.pop()
        else:
            n = Node(tag, tok)
            stack[-1].ch.append(n)
            if tag not in VOID and not tok.endswith("/>"):
                stack.append(n)
    if pos < len(src):
        stack[-1].ch.append(src[pos:])
    if len(stack) != 1:
        raise ValueError("unclosed element " + stack[-1].start[:80])
    return root


def esc(v):
    return v.replace("&", "&amp;").replace('"', "&quot;")


def tag(name, attrs, selfclose=False):
    """Start tag from [[name, value], ...] (or a dict); None values are left out."""
    items = attrs.items() if isinstance(attrs, dict) else attrs
    s = "".join(f' {k}="{esc(str(v))}"' for k, v in items if v is not None)
    return f"<{name}{s}{'/>' if selfclose else '>'}"


def el(name, attrs, inner=""):
    return tag(name, attrs) + inner + f"</{name}>"


def split_ws(node):
    """Element children of node, plus the whitespace text before each one and at the end.
    Unmodelled if there is non-whitespace text between them."""
    out, ws = [], ""
    for c in node.ch:
        if isinstance(c, str):
            if c.strip():
                raise Unmodelled("text between blocks")
            ws += c
        else:
            out.append((ws, c))
            ws = ""
    return out, ws


def expect(node, name, cls=None):
    if not isinstance(node, Node) or node.tag != name or (cls is not None and node.cls() != cls):
        got = node.start[:60] if isinstance(node, Node) else repr(node)[:60]
        raise Unmodelled(f"expected <{name} class={cls!r}>, got {got}")
    return node


def only(node, name=None, cls=None):
    """The single element child of node (no text around it)."""
    if len(node.ch) != 1:
        raise Unmodelled("expected a single child in " + node.start[:60])
    return expect(node.ch[0], name, cls) if name else node.ch[0]


# ------------------------------------------------------------------ links
LINK_ORDER = ["class", "href", "rel", "target"]


def link_fields(node, cls):
    """{url, rel, target, _order?} of an <a> whose attributes are exactly class/href/rel/target
    (+ onclick)."""
    at = node.attrs()
    names = [k for k, _ in at]
    d = dict(at)
    if d.get("class") != cls or set(names) - {"class", "href", "rel", "target", "onclick"}:
        raise Unmodelled("link attrs " + node.start[:80])
    out = {"url": d["href"]}
    if "rel" in d:
        out["rel"] = d["rel"]
    if "target" in d:
        out["target"] = d["target"]
    if "onclick" in d:
        out["onclick"] = d["onclick"]
    default = [k for k in ["class", "href", "onclick", "rel", "target"] if k in d]
    if names != default:
        out["_order"] = names
    return out


def link_tag(cls, f):
    vals = {"class": cls, "href": f["url"], "rel": f.get("rel"), "target": f.get("target"),
            "onclick": f.get("onclick")}
    order = f.get("_order") or [k for k in ["class", "href", "onclick", "rel", "target"]
                                if vals[k] is not None]
    return tag("a", [[k, vals[k]] for k in order])


# ------------------------------------------------------------------ gallery
def arrow(d):
    """Previous (-1) / next (1) photo button; the aria-label comes from the UI table."""
    label = UI["photo_prev"] if d < 0 else UI["photo_next"]
    return (f'<button aria-label="{esc(label)}" class="bpa-arrow {"prev" if d < 0 else "next"}" '
            f'onclick="bpaSlide(this,{d})" type="button">{"‹" if d < 0 else "›"}</button>')


# whitespace before rank tag, prev, next, pill, slider and before </div> of bpa-media
MEDIA_WS = ["\n", "\n", "", "", "", "\n"]
THUMB_IMG = ' alt="" loading="lazy" decoding="async" width="80" height="60">'


def ex_gallery(gal, num):
    expect(gal, "div", "cd-gal")
    kids = gal.elems()
    if len(kids) != 2 or "".join(c for c in gal.ch if isinstance(c, str)):
        raise Unmodelled("cd-gal shape")
    media, thumbs = kids
    expect(media, "div", "bpa-media")
    items, tail = split_ws(media)
    ws = [w for w, _ in items] + [tail]
    if len(items) != 5:
        raise Unmodelled("bpa-media layout")
    rank, prev, nxt, pill, slider = [n for _, n in items]
    if prev.outer() != arrow(-1) or nxt.outer() != arrow(1):
        raise Unmodelled("arrows")
    rcls = expect(rank, "span").cls() or ""
    if not rcls.startswith("bpa-rank-tag ") or len(rank.attrs()) != 1:
        raise Unmodelled("rank tag")
    out = {"rank": {"text": rank.inner(), "medal": rcls[len("bpa-rank-tag "):]}}
    if ws != MEDIA_WS:
        out["_media_ws"] = ws
    expect(slider, "div", "bpa-slider")
    photos, sep = [], None
    for c in slider.ch:
        if isinstance(c, str):
            if c.strip():
                raise Unmodelled("text in slider")
            if sep is None:
                sep = c
            elif c != sep:
                raise Unmodelled("mixed slider separators")
            continue
        expect(c, "img")
        if not c.selfclosed():
            raise Unmodelled("slider img not self-closed")
        photos.append(c.attrs())
    # separators: either none, or the same text before every img and before </div>
    nimg = len(photos)
    texts = [c for c in slider.ch if isinstance(c, str)]
    if texts and len(texts) != nimg + 1:
        if not (len(texts) == nimg and isinstance(slider.ch[-1], Node)):
            raise Unmodelled("slider separator pattern")
    out["photos"] = photos
    if sep:
        out["_photo_sep"] = sep
        if isinstance(slider.ch[-1], Node):
            out["_photo_sep_end"] = False
    sa = slider.attrs()
    want = [["aria-label", UI["gallery_label"].format(n=num)], ["class", "bpa-slider"],
            ["onscroll", "bpaCount(this)"], ["tabindex", "0"]]
    if sa != want:
        if [k for k, _ in sa] != [k for k, _ in want] or sa[1:] != want[1:]:
            raise Unmodelled("slider attrs")
        out["_gallery_label"] = sa[0][1]
    pt = pill.outer()
    if pt != f'<span class="bpa-pill">1 / {nimg}</span>':
        m = re.fullmatch(r'<span class="bpa-pill">(.*)</span>', pt)
        if not m:
            raise Unmodelled("pill")
        out["_pill"] = m.group(1)
    # thumbnails
    if thumbs.start != thumbs_tag():
        raise Unmodelled("thumbs tag")
    tl = []
    nt = len(thumbs.ch)
    for i, b in enumerate(thumbs.ch):
        expect(b, "button")
        img = only(b, "img")
        m = re.fullmatch(r'<img src="([^"]*)"' + re.escape(THUMB_IMG), img.start)
        if not m:
            raise Unmodelled("thumb img")
        t = {"src": _html.unescape(m.group(1))}
        if b.start != thumb_tag(i, nt, nimg):
            t["_tag"] = b.start
        tl.append(t)
    out["thumbs"] = tl
    return out


def thumb_tag(i, nt, nimg):
    c = "cd-thumb is-on" if i == 0 else ("cd-thumb is-hid" if i >= 5 else "cd-thumb")
    more = f' data-more="+{nt - 4}"' if (i == 4 and nt > 5) else ""
    return (f'<button type="button" class="{c}" data-i="{i}"{more} '
            f'aria-label="{esc(UI["thumb_label"].format(i=i + 1, n=nt))}">')


def thumbs_tag():
    return f'<div class="cd-thumbs" aria-label="{esc(UI["thumbs_label"])}">'


def render_gallery(g, num):
    photos = g["photos"]
    sep = g.get("_photo_sep", "")
    imgs = "".join(sep + tag("img", p, True) for p in photos)
    if sep and g.get("_photo_sep_end", True):
        imgs += sep
    pill = g.get("_pill", f"1 / {len(photos)}")
    label = g.get("_gallery_label", UI["gallery_label"].format(n=num))
    nt = len(g["thumbs"])
    thumbs = "".join(
        (t.get("_tag") or thumb_tag(i, nt, len(photos)))
        + f'<img src="{esc(t["src"])}"{THUMB_IMG}</button>'
        for i, t in enumerate(g["thumbs"]))
    w = g.get("_media_ws", MEDIA_WS)
    return ('<div class="cd-gal"><div class="bpa-media">' + w[0]
            + el("span", {"class": "bpa-rank-tag " + g["rank"]["medal"]}, g["rank"]["text"]) + w[1]
            + arrow(-1) + w[2] + arrow(1) + w[3] + f'<span class="bpa-pill">{pill}</span>' + w[4]
            + tag("div", [["aria-label", label], ["class", "bpa-slider"],
                          ["onscroll", "bpaCount(this)"], ["tabindex", "0"]])
            + imgs + "</div>" + w[5] + "</div>"
            + thumbs_tag() + thumbs + "</div></div>")


# ------------------------------------------------------------------ kicker / title
KICK_SEP = " • "


def ex_kicker(n):
    """Kicker parts joined by " • ": plain text, or a map link {map, url, ...}."""
    if n.start != '<div class="bpa-kicker">':
        raise Unmodelled("kicker tag")
    flat, links = "", []
    for c in n.ch:
        if isinstance(c, str):
            if "\x00" in c:
                raise Unmodelled("kicker text")
            flat += c
        elif c.tag == "a" and c.cls() == "bpa-kicker-map-link":
            f = link_fields(c, "bpa-kicker-map-link")
            f["map"] = c.inner()
            flat += f"\x00{len(links)}\x00"
            links.append(f)
        else:
            raise Unmodelled("kicker child " + c.start[:40])
    parts = []
    for p in flat.split(KICK_SEP):
        m = re.fullmatch(r"\x00(\d+)\x00", p)
        if m:
            parts.append(links[int(m.group(1))])
        elif "\x00" in p:
            raise Unmodelled("map link not between separators")
        else:
            parts.append(p)
    return parts


def render_kicker(parts):
    out = []
    for p in parts:
        if isinstance(p, str):
            out.append(p)
        else:
            out.append(link_tag("bpa-kicker-map-link", p) + p["map"] + "</a>")
    return '<div class="bpa-kicker">' + KICK_SEP.join(out) + "</div>"


def ex_title(n):
    f = link_fields(expect(n, "a", "bpa-title"), "bpa-title")
    f["text"] = n.inner()
    return f


def render_title(t):
    return link_tag("bpa-title", t) + t["text"] + "</a>"


# ------------------------------------------------------------------ ratings + tested chip
CHEV = '<span class="bpa-lang-chev" aria-hidden="true">▾</span>'
CHEV_PLAIN = ' <span class="bpa-lang-chev">▾</span>'


def ex_badge(b, icons):
    c = b.cls()
    kind = {"bpa-rev-badge is-link": "link", "bpa-rev-badge": "plain",
            "bpa-rev-badge is-static": "static"}.get(c)
    if not kind or (b.tag == "a") != (kind == "link"):
        raise Unmodelled("badge class")
    out = {}
    if kind == "link":
        out.update(link_fields(b, "bpa-rev-badge is-link"))
    elif len(b.attrs()) != 1:
        raise Unmodelled("badge attrs")
    ch = list(b.ch)
    if ch and isinstance(ch[0], str):
        out["_nl"] = ch.pop(0)
    names = ["img", "site", "score", "count"] + (["go"] if kind == "link" else [])
    if len(ch) != len(names) or any(isinstance(x, str) for x in ch):
        raise Unmodelled("badge parts")
    img, site, score, count = ch[:4]
    ia = img.attrs()
    if [k for k, _ in ia] != ["alt", "class", "loading", "src"] or ia[1][1] != "bpa-rev-icon" \
            or ia[2][1] != "lazy" or not img.selfclosed():
        raise Unmodelled("badge icon")
    name = ia[0][1]
    icons.setdefault(name, ia[3][1])
    if icons[name] != ia[3][1]:
        out["icon"] = ia[3][1]
    for node, k in ((site, "bpa-rev-site"), (score, "bpa-rev-score"), (count, "bpa-rev-count")):
        if node.start != f'<span class="{k}">':
            raise Unmodelled("badge span")
    if kind == "link" and ch[4].outer() != '<span class="bpa-rev-go" aria-hidden="true">→</span>':
        raise Unmodelled("badge go")
    out = {"kind": kind, "icon_alt": name, "site": site.inner(), "score": score.inner(),
           "count": count.inner(), **out}
    if out["site"] == name:
        del out["icon_alt"]
    return out


def render_badge(b, icons):
    name = b.get("icon_alt", b["site"])
    icon = b.get("icon", icons.get(name, ""))
    inner = (b.get("_nl", "")
             + tag("img", [["alt", name], ["class", "bpa-rev-icon"], ["loading", "lazy"], ["src", icon]], True)
             + f'<span class="bpa-rev-site">{b["site"]}</span><span class="bpa-rev-score">{b["score"]}</span>'
             f'<span class="bpa-rev-count">{b["count"]}</span>')
    if b["kind"] == "link":
        return (link_tag("bpa-rev-badge is-link", b) + inner
                + '<span class="bpa-rev-go" aria-hidden="true">→</span></a>')
    cls = "bpa-rev-badge" + (" is-static" if b["kind"] == "static" else "")
    return f'<span class="{cls}">' + inner + "</span>"


def ex_rating(n, icons):
    if n.start != '<div class="bpa-summary-reviews bpa-rate">':
        raise Unmodelled("rating tag")
    c = only(n)
    if c.tag == "span":  # no review data: one line of text
        if c.start != '<span class="bpa-rate-meta">':
            raise Unmodelled("rating text")
        return {"meta": c.inner()}
    expect(c, "details", "bpa-lang bpa-rate-more")
    summ, pop = c.ch
    expect(summ, "summary", "bpa-rate-sum")
    stars, score, meta, chev = summ.ch
    m = re.fullmatch(r'<span class="bpa-stars" style="--r:([^"]*)" aria-hidden="true"></span>', stars.outer())
    if not m or score.start != '<b class="bpa-rate-score">' or meta.start != '<span class="bpa-rate-meta">' \
            or chev.outer() != CHEV:
        raise Unmodelled("rating summary")
    expect(pop, "div", "bpa-lang-pop")
    head, lst = pop.ch
    expect(head, "strong")
    expect(lst, "span", "bpa-rate-list")
    if len(pop.attrs()) != 1 or len(lst.attrs()) != 1:
        raise Unmodelled("rating pop")
    sites = []
    for b in lst.ch:
        if isinstance(b, str):
            raise Unmodelled("text in rate list")
        sites.append(ex_badge(b, icons))
    return {"stars": m.group(1), "score": score.inner(), "meta": meta.inner(),
            "heading": head.inner(), "sites": sites}


def render_rating(r, icons):
    if "stars" not in r:
        return f'<div class="bpa-summary-reviews bpa-rate"><span class="bpa-rate-meta">{r["meta"]}</span></div>'
    return ('<div class="bpa-summary-reviews bpa-rate"><details class="bpa-lang bpa-rate-more">'
            f'<summary class="bpa-rate-sum"><span class="bpa-stars" style="--r:{r["stars"]}" aria-hidden="true">'
            f'</span><b class="bpa-rate-score">{r["score"]}</b><span class="bpa-rate-meta">{r["meta"]}</span>'
            + CHEV + '</summary><div class="bpa-lang-pop"><strong>' + r["heading"] + "</strong>"
            + '<span class="bpa-rate-list">' + "".join(render_badge(b, icons) for b in r["sites"])
            + "</span></div></details></div>")


def ex_tested(n):
    if n.start != '<div class="bpa-proof">':
        raise Unmodelled("proof tag")
    d = only(n, "details", "bpa-lang bpa-tested")
    summ, pop = d.ch
    if summ.start != '<summary class="bpa-vchip">' or pop.start != '<div class="bpa-lang-pop">':
        raise Unmodelled("tested parts")
    s = summ.inner()
    if not s.endswith(CHEV):
        raise Unmodelled("tested chev")
    return {"chip": s[:-len(CHEV)], "pop_html": pop.inner()}


def render_tested(t):
    return ('<div class="bpa-proof"><details class="bpa-lang bpa-tested"><summary class="bpa-vchip">'
            + t["chip"] + CHEV + '</summary><div class="bpa-lang-pop">' + t["pop_html"]
            + "</div></details></div>")


def ex_reviews(n, icons):
    if n.start != '<div class="bpa-reviews-line">':
        raise Unmodelled("reviews tag")
    items, tail = split_ws(n)
    if tail != "\n" or any(w != "\n" for w, _ in items) or not 1 <= len(items) <= 2:
        raise Unmodelled("reviews layout")
    out = {"ratings": model(ex_rating, render_rating, items[0][1], icons)}
    if len(items) == 2:
        out["tested"] = model(ex_tested, render_tested, items[1][1])
    return out


# ------------------------------------------------------------------ pills
def ex_pill(n):
    expect(n, "details")
    at = n.attrs()
    if not at or at[0][0] != "class" or not at[0][1].startswith("bpa-lang"):
        raise Unmodelled("pill class")
    out = {"cls": at[0][1]}
    data = {}
    for k, v in at[1:]:
        if not k.startswith("data-"):
            raise Unmodelled("pill attr " + k)
        data[k[5:]] = v
    if data:
        out["data"] = data
    if len(n.ch) != 2:
        raise Unmodelled("pill parts")
    summ, pop = n.ch
    if summ.start != '<summary class="bpa-sp">' or pop.start != '<div class="bpa-lang-pop">':
        raise Unmodelled("pill summary/pop")
    s = summ.inner()
    m = re.fullmatch(r'(.*?) <span class="bpa-lang-label">(.*?)</span>(' + re.escape(CHEV) + "|"
                     + re.escape(CHEV_PLAIN) + ")", s, re.S)
    if m and "<" not in m.group(1) and "</span>" not in m.group(2):
        out["emoji"], out["label"] = m.group(1), m.group(2)
        if (m.group(3) == CHEV_PLAIN) != default_plain_chev(out["cls"]):
            out["_chev"] = "plain" if m.group(3) == CHEV_PLAIN else "aria"
    else:
        out["summary_html"] = s
    out["pop_html"] = pop.inner()
    return out


def default_plain_chev(cls):
    """The access pill puts a space and a plain chevron after its label; the others an aria-hidden one."""
    return "cd-access" in cls.split()


def render_pill(p):
    at = [["class", p["cls"]]] + [["data-" + k, v] for k, v in p.get("data", {}).items()]
    if "summary_html" in p:
        s = p["summary_html"]
    else:
        s = (p["emoji"] + ' <span class="bpa-lang-label">' + p["label"] + "</span>"
             + (CHEV_PLAIN if p.get("_chev", "plain" if default_plain_chev(p["cls"]) else "aria") == "plain"
                else CHEV))
    return (tag("details", at) + '<summary class="bpa-sp">' + s + '</summary><div class="bpa-lang-pop">'
            + p["pop_html"] + "</div></details>")


def ex_specs(n):
    if n.start != '<div class="bpa-specs-row">':
        raise Unmodelled("specs tag")
    items, tail = split_ws(n)
    if tail != "\n" or any(w != "\n" for w, _ in items):
        raise Unmodelled("specs layout")
    return [model(ex_pill, render_pill, c) for _, c in items]


def render_specs(pills):
    return '<div class="bpa-specs-row">\n' + "".join(render(render_pill, p) + "\n" for p in pills) + "</div>"


# ------------------------------------------------------------------ slot, pick/skip, faq
def ex_slot(n):
    expect(n, "div", "fbm-slot")
    if n.ch:
        raise Unmodelled("slot content")
    at = n.attrs()
    names = [k for k, _ in at]
    if names[:2] != ["class", "data-tt"] or set(names[2:]) - {"data-dur", "data-every"}:
        raise Unmodelled("slot attrs")
    d = dict(at)
    out = {}
    try:
        tt = json.loads(d["data-tt"])
        if json.dumps(tt, ensure_ascii=False) != d["data-tt"]:
            raise ValueError
        out["tt"] = tt
    except ValueError:
        out["_tt_raw"] = d["data-tt"]
    for k in names[2:]:
        out[k[5:]] = d[k]
    if names[2:] != [k for k in ("data-dur", "data-every") if k in d]:
        out["_order"] = names
    return out


def render_slot(s):
    tt = s["_tt_raw"] if "_tt_raw" in s else json.dumps(s["tt"], ensure_ascii=False)
    vals = {"class": "fbm-slot", "data-tt": tt, "data-dur": s.get("dur"), "data-every": s.get("every")}
    order = s.get("_order") or ["class", "data-tt", "data-dur", "data-every"]
    return tag("div", [[k, vals[k]] for k in order]) + "</div>"


def ex_bestfor(n):
    if n.start != '<div class="bpa-best-for bpa-pickskip">':
        raise Unmodelled("best-for tag")
    m = re.fullmatch(r'<span class="bpa-pick">(.*?)</span> (.*) <span class="bpa-skip">(.*?)</span> (.*)',
                     n.inner(), re.S)
    if not m:
        raise Unmodelled("pick/skip shape")
    out = {"pick_html": m.group(2), "skip_html": m.group(4)}
    if m.group(1) != UI["pick"]:
        out["_pick_label"] = m.group(1)
    if m.group(3) != UI["skip"]:
        out["_skip_label"] = m.group(3)
    return out


def render_bestfor(b):
    return ('<div class="bpa-best-for bpa-pickskip"><span class="bpa-pick">' + b.get("_pick_label", UI["pick"])
            + "</span> " + b["pick_html"] + ' <span class="bpa-skip">' + b.get("_skip_label", UI["skip"])
            + "</span> " + b["skip_html"] + "</div>")


FAQ_CHEV = ' <span class="fbm-faq-chev" aria-hidden="true">▾</span>'


def faq_title(n):
    return UI["faq_title"].format(n=n)


def ex_faq(n):
    expect(n, "details", "fbm-faq")
    summ, body = n.ch
    if summ.start != "<summary>" or body.start != '<div class="fbm-faq-body">':
        raise Unmodelled("faq parts")
    s = summ.inner()
    if not s.endswith(FAQ_CHEV):
        raise Unmodelled("faq chev")
    qa = []
    for item in body.ch:
        expect(item, "div", "fbm-qa")
        if len(item.ch) != 2 or item.ch[0].start != '<div class="fbm-q">' \
                or item.ch[1].start != '<div class="fbm-a">':
            raise Unmodelled("faq item")
        qa.append({"q": item.ch[0].inner(), "a": item.ch[1].inner()})
    out = {"items": qa}
    if s[:-len(FAQ_CHEV)] != faq_title(len(qa)):
        out["_title"] = s[:-len(FAQ_CHEV)]
    return out


def render_faq(f):
    return ('<details class="fbm-faq"><summary>' + f.get("_title", faq_title(len(f["items"]))) + FAQ_CHEV
            + '</summary><div class="fbm-faq-body">'
            + "".join(f'<div class="fbm-qa"><div class="fbm-q">{x["q"]}</div><div class="fbm-a">{x["a"]}</div></div>'
                      for x in f["items"]) + "</div></details>")


# ------------------------------------------------------------------ info column
# field -> (class of the block, extractor, renderer); the house order of the blocks
INFO = [
    ("kicker", "bpa-kicker"),
    ("title", "bpa-title"),
    ("reviews", "bpa-reviews-line"),
    ("pills", "bpa-specs-row"),
    ("slot", "fbm-slot"),
    ("best_for", "bpa-best-for bpa-pickskip"),
    ("faq", "fbm-faq"),
]


def info_ex(field, node, icons):
    if field == "reviews":
        return ex_reviews(node, icons)  # parts fall back on their own
    fn = {"kicker": ex_kicker, "title": ex_title, "pills": ex_specs, "slot": ex_slot,
          "best_for": ex_bestfor, "faq": ex_faq}[field]
    return fn(node)


def info_render(field, val, icons):
    if field == "reviews":
        return ("<div class=\"bpa-reviews-line\">\n" + render(render_rating, val["ratings"], icons) + "\n"
                + (render(render_tested, val["tested"]) + "\n" if "tested" in val else "") + "</div>")
    fn = {"kicker": render_kicker, "title": render_title, "pills": render_specs, "slot": render_slot,
          "best_for": render_bestfor, "faq": render_faq}[field]
    return fn(val)


def ex_info(n, card, icons):
    if n.start != '<div class="bpa-info">':
        raise Unmodelled("info tag")
    items, tail = split_ws(n)
    if tail != "\n" or not items or items[0][0] != "\n":
        raise Unmodelled("info layout")
    pos = 0  # next house slot
    last = None
    for ws, node in items:
        c = node.cls()
        hit = next((i for i in range(pos, len(INFO)) if INFO[i][1] == c), None)
        key = f"extras_after_{last}" if last else "extras_before_kicker"
        if hit is None:
            # extras keep the exact whitespace between them; the block itself starts on a new line
            if key in card:
                card[key] += ws + node.outer()
            elif ws == "\n":
                card[key] = node.outer()
            else:
                raise Unmodelled("info layout")
            continue
        if ws != "\n":
            raise Unmodelled("info layout")
        field = INFO[hit][0]
        card[field] = model(lambda x, f=field: info_ex(f, x, icons), None, node, field=field, icons=icons)
        pos, last = hit + 1, field


def render_info(card, icons):
    parts = []
    if "extras_before_kicker" in card:
        parts.append(card["extras_before_kicker"])
    for field, _ in INFO:
        if field in card:
            v = card[field]
            parts.append(v["raw"] if isinstance(v, dict) and set(v) == {"raw"} else info_render(field, v, icons))
        if f"extras_after_{field}" in card:
            parts.append(card[f"extras_after_{field}"])
    return '<div class="bpa-info">\n' + "".join(p + "\n" for p in parts) + "</div>"


# ------------------------------------------------------------------ price + CTA
def ex_price(n):
    if n.start != "<div>":
        raise Unmodelled("price wrapper")
    items, tail = split_ws(n)
    if len(items) != 1 or items[0][0] != "\n" or tail != "\n":
        raise Unmodelled("price wrapper layout")
    d = expect(items[0][1], "details", "cd-pdd")
    summ, pop = d.ch
    m = re.fullmatch(r'<span class="cd-pdd-main">(.*?)</span><span class="cd-pdd-sub">(.*?) '
                     r'<span class="cd-pdd-chev" aria-hidden="true">▾</span></span>', summ.inner(), re.S)
    if summ.start != "<summary>" or not m or pop.start != '<div class="cd-pdd-pop">':
        raise Unmodelled("price summary")
    out = {"main": m.group(1), "sub": m.group(2)}
    kids = pop.ch
    if any(isinstance(k, str) for k in kids):
        raise Unmodelled("price pop text")
    if kids[0].start != '<div class="cd-pdd-h">':
        raise Unmodelled("price head")
    if kids[0].inner() != UI["price_heading"]:
        out["_heading"] = kids[0].inner()
    rest = kids[1:]
    if rest and rest[0].tag == "table":
        if rest[0].start != "<table>":
            raise Unmodelled("table tag")
        rows = []
        for tr in rest[0].ch:
            expect(tr, "tr")
            if tr.start != "<tr>" or len(tr.ch) != 2 or any(isinstance(t, str) or t.start != "<td>" for t in tr.ch):
                raise Unmodelled("price row")
            lab, val = tr.ch[0].inner(), tr.ch[1].inner()
            row = {"label": lab, "price": val}
            mm = re.fullmatch(r"(.*?)<small>(.*)</small>", lab, re.S)
            if mm and "<" not in mm.group(1) and "<" not in mm.group(2):
                row = {"label": mm.group(1), "small": mm.group(2), "price": val}
            rows.append(row)
        out["rows"] = rows
        rest = rest[1:]
    if rest and rest[0].start == '<div class="cd-pdd-total">':
        t = rest[0].ch
        if len(t) != 2 or any(isinstance(x, str) or x.start != "<span>" for x in t):
            raise Unmodelled("price total")
        out["total"] = {"label": t[0].inner(), "price": t[1].inner()}
        rest = rest[1:]
    if rest and rest[0].start == '<div class="cd-pdd-note">':
        out["note"] = rest[0].inner()
        rest = rest[1:]
    if rest:
        raise Unmodelled("price extra")
    return out


def render_price(p):
    rows = ""
    if "rows" in p:
        rows = "<table>" + "".join(
            "<tr><td>" + r["label"] + (f"<small>{r['small']}</small>" if "small" in r else "")
            + "</td><td>" + r["price"] + "</td></tr>" for r in p["rows"]) + "</table>"
    total = (f'<div class="cd-pdd-total"><span>{p["total"]["label"]}</span><span>{p["total"]["price"]}</span></div>'
             if "total" in p else "")
    note = f'<div class="cd-pdd-note">{p["note"]}</div>' if "note" in p else ""
    return ('<div>\n<details class="cd-pdd"><summary><span class="cd-pdd-main">' + p["main"]
            + '</span><span class="cd-pdd-sub">' + p["sub"]
            + ' <span class="cd-pdd-chev" aria-hidden="true">▾</span></span></summary><div class="cd-pdd-pop">'
            + f'<div class="cd-pdd-h">{p.get("_heading", UI["price_heading"])}</div>' + rows + total + note
            + "</div></details>\n</div>")


def ex_cta(n, card):
    if n.start != '<div class="bpa-cta-cell">':
        raise Unmodelled("cta tag")
    items, tail = split_ws(n)
    if tail != "\n" or any(w != "\n" for w, _ in items):
        raise Unmodelled("cta layout")
    nodes = [x for _, x in items]
    if not nodes or nodes[0].start != "<div>":
        raise Unmodelled("cta: no price")
    card["price"] = model(ex_price, render_price, nodes[0])
    cta = {}
    for x in nodes[1:]:
        c = x.cls()
        if x.tag == "a" and c == "bpa-btn" and "btn" not in cta:
            cta["btn"] = link_fields(x, "bpa-btn")
            cta["btn"]["text"] = x.inner()
        elif x.tag == "div" and c == "bpa-via" and "via" not in cta and len(x.attrs()) == 1:
            cta["via"] = x.inner()
        elif x.tag == "div" and c == "bpa-trust2" and "trust" not in cta and len(x.attrs()) == 1:
            if any(isinstance(s, str) or s.start != "<span>" for s in x.ch):
                raise Unmodelled("trust lines")
            cta["trust"] = [s.inner() for s in x.ch]
        elif x.tag == "a" and c == "bpa-sublink" and "sublink" not in cta and len(x.attrs()) == 2:
            cta["sublink"] = {"url": x.a()["href"], "text": x.inner()}
        else:
            raise Unmodelled("cta child " + x.start[:60])
    keys = list(cta)
    want = [k for k in ("btn", "via", "trust", "sublink") if k in cta]
    if keys != want:
        raise Unmodelled("cta order")
    card["cta"] = cta


def render_cta(card):
    parts = [render(render_price, card["price"])]
    c = card["cta"]
    if "btn" in c:
        parts.append(link_tag("bpa-btn", c["btn"]) + c["btn"]["text"] + "</a>")
    if "via" in c:
        parts.append(f'<div class="bpa-via">{c["via"]}</div>')
    if "trust" in c:
        parts.append('<div class="bpa-trust2">' + "".join(f"<span>{t}</span>" for t in c["trust"]) + "</div>")
    if "sublink" in c:
        parts.append(f'<a class="bpa-sublink" href="{esc(c["sublink"]["url"])}">{c["sublink"]["text"]}</a>')
    return '<div class="bpa-cta-cell">\n' + "".join(p + "\n" for p in parts) + "</div>"


# ------------------------------------------------------------------ the card
CARD_ATTRS = ["class", "data-cat", "id"]


def ex_card(node, icons):
    at = node.attrs()
    d = dict(at)
    m = re.fullmatch(r"card-(\d+)", d.get("id", ""))
    if [k for k, _ in at][:1] != ["class"] or d["class"] != "bpa-card" or not m:
        raise Unmodelled("card tag")
    card = {"id": d["id"]}
    if "data-cat" in d:
        card["cats"] = d["data-cat"].split(" ") if d["data-cat"] else []
        if " ".join(card["cats"]) != d["data-cat"]:
            raise Unmodelled("data-cat spacing")
    other = [[k, v] for k, v in at if k not in CARD_ATTRS]
    if other:
        card["attrs"] = other
    if [k for k, _ in at if k in CARD_ATTRS] != [k for k in CARD_ATTRS if k in d] or \
            [k for k, _ in at][:len(at) - len(other)] != [k for k in CARD_ATTRS if k in d]:
        raise Unmodelled("card attr order")
    num = int(m.group(1))
    items, tail = split_ws(node)
    if len(items) != 1 or items[0][0] != "\n" or tail != "\n":
        raise Unmodelled("card layout")
    main = items[0][1]
    if main.start != '<div class="bpa-main">':
        raise Unmodelled("bpa-main")
    items, tail = split_ws(main)
    if [w for w, _ in items] != ["\n", "\n", "\n"] or tail != "\n":
        raise Unmodelled("bpa-main layout")
    gal, info, cta = [x for _, x in items]
    card["gallery"] = model(lambda x: ex_gallery(x, num), lambda g: render_gallery(g, num), gal, field="gallery")
    ex_info(info, card, icons)
    ex_cta(cta, card)
    return card


def render_card(card, icons):
    if set(card) == {"raw"} or (set(card) <= {"raw", "before"} and "raw" in card):
        return card["raw"]
    num = int(card["id"].split("-")[1])
    at = [["class", "bpa-card"]]
    if "cats" in card:
        at.append(["data-cat", " ".join(card["cats"])])
    at.append(["id", card["id"]])
    at += card.get("attrs", [])
    return (tag("div", at) + '\n<div class="bpa-main">\n'
            + render(lambda g: render_gallery(g, num), card["gallery"]) + "\n"
            + render_info(card, icons) + "\n" + render_cta(card) + "\n</div>\n</div>")


# ------------------------------------------------------------------ model / render with fallback
def model(ex, rn, node, *args, field=None, icons=None):
    """Structured form of node, or {"raw": html} when it does not fit the model or does
    not render back to the same bytes."""
    src = node.outer()
    try:
        val = ex(node, *args)
        if rn is not None:
            back = rn(val, *args)
        elif field:
            back = info_render(field, val, icons)
        else:
            back = src
        if back == src:
            return val
        MISSES.append((field or getattr(ex, "__name__", "?"), "render differs"))
    except Unmodelled as e:
        MISSES.append((field or getattr(ex, "__name__", "?"), str(e)))
    return {"raw": src}


def render(rn, val, *args):
    if isinstance(val, dict) and set(val) == {"raw"}:
        return val["raw"]
    return rn(val, *args)


MISSES = []


# ------------------------------------------------------------------ page level
CARD_START = re.compile(r'<div class="bpa-card"[ >]')


def card_spans(src):
    """[(start, end)] of every card div, in page order."""
    spans = []
    for m in CARD_START.finditer(src):
        if spans and m.start() < spans[-1][1]:
            continue
        depth = 0
        for t in re.finditer(r"<(/?)div\b[^>]*>", src[m.start():]):
            depth += -1 if t.group(1) else 1
            if depth == 0:
                spans.append((m.start(), m.start() + t.end()))
                break
        else:
            raise SystemExit("unbalanced card div")
    return spans


def region(src):
    spans = card_spans(src)
    if spans:
        return spans[0][0], spans[-1][1], spans
    i = src.find(MARKER)
    if i < 0:
        raise SystemExit("no cards and no " + MARKER + " marker in the page")
    return i, i + len(MARKER), []


def extract_page(src):
    start, end, spans = region(src)
    if not spans:
        raise SystemExit("no cards in the page")
    icons, cards, prev = {}, [], None
    for s, e in spans:
        chunk = src[s:e]
        tree = parse(chunk)
        if tree.inner() != chunk:
            raise SystemExit("parser is not lossless here")
        node = only(tree)
        try:
            card = ex_card(node, icons)
            if render_card(card, icons) != chunk:
                MISSES.append(("card", f"{card.get('id')}: render differs"))
                card = {"raw": chunk}
        except Unmodelled as why:
            MISSES.append(("card", str(why)))
            card = {"raw": chunk}
        if prev is not None:
            gap = src[prev:s]
            if gap != "\n\n":
                card = {"before": gap, **card}
        cards.append(card)
        prev = e
    return {"format": 1, "icons": icons, "cards": cards}


def render_cards(data):
    out = []
    for i, c in enumerate(data["cards"]):
        if i:
            out.append(c.get("before", "\n\n"))
        out.append(render_card({k: v for k, v in c.items() if k != "before"}, data.get("icons", {})))
    return "".join(out)


def build_page(src, data):
    start, end, _ = region(src)
    return src[:start] + render_cards(data) + src[end:]


def data_path(page):
    rel = os.path.relpath(os.path.abspath(page), ROOT)
    slug = rel[:-5] if rel.endswith(".html") else rel
    return os.path.join(ROOT, "data", "listicles", slug.replace(os.sep, "--") + ".json")


# ------------------------------------------------------------------ coverage
def coverage(card, page_bytes):
    """(raw bytes, free-form html bytes) in a card's data, by key name."""
    raw = frag = 0

    def walk(v, key=""):
        nonlocal raw, frag
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, k)
        elif isinstance(v, list):
            for x in v:
                walk(x, key)
        elif isinstance(v, str):
            n = len(v.encode("utf-8"))
            if key == "raw" or key.startswith("extras_") or key == "before":
                raw += n
            elif key.endswith("_html"):
                frag += n
    walk(card)
    return raw, frag


def stats(src, data):
    _, _, spans = region(src)
    lines, tot = [], [0, 0, 0, 0]
    for (s, e), c in zip(spans, data["cards"]):
        b = len(src[s:e].encode("utf-8"))
        raw, frag = coverage({k: v for k, v in c.items() if k != "before"}, b)
        icon = sum(len(m.group(0)) for m in re.finditer(r'src="data:image/png;base64,[^"]*"', src[s:e]))
        tot[3] += icon
        tot[0] += b
        tot[1] += raw
        tot[2] += frag
        lines.append(f"  {c.get('id', '?'):8} {b:7} B  raw {raw:6} B ({raw / b:5.1%})  "
                     f"html fragments {frag:6} B ({frag / b:5.1%})  structured {1 - (raw + frag) / b:5.1%}"
                     f"  (without review-site icons {1 - (raw + frag) / (b - icon):5.1%})")
    b, raw, frag, icon = tot
    lines.append(f"  {'total':8} {b:7} B  raw {raw:6} B ({raw / b:5.1%})  "
                 f"html fragments {frag:6} B ({frag / b:5.1%})  structured {1 - (raw + frag) / b:5.1%}"
                 f"  (without review-site icons {1 - (raw + frag) / (b - icon):5.1%})")
    return "\n".join(lines)


def dumps(v, ind=0):
    """JSON with one key per line, but lists of plain values (attribute pairs, times,
    categories) on one line."""
    pad, sub = " " * ind, " " * (ind + 1)
    if isinstance(v, dict):
        if not v:
            return "{}"
        return "{\n" + ",\n".join(f"{sub}{json.dumps(k, ensure_ascii=False)}: {dumps(x, ind + 1)}"
                                   for k, x in v.items()) + "\n" + pad + "}"
    if isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v) or \
                all(isinstance(x, list) and all(not isinstance(y, (dict, list)) for y in x) and len(x) == 2
                    for x in v) and len(json.dumps(v, ensure_ascii=False)) < 100:
            return json.dumps(v, ensure_ascii=False)
        if not v:
            return "[]"
        return "[\n" + ",\n".join(sub + dumps(x, ind + 1) for x in v) + "\n" + pad + "]"
    return json.dumps(v, ensure_ascii=False)


# ------------------------------------------------------------------ language versions (i18n)
# A language version of a listicle page is built from the ENGLISH card data plus translations, so
# facts (prices, times, ratings, photos, booking links, filter categories) always come from English:
#
#   kit table   runtime/listicle/i18n/<lang>.json   {"ui": {...}, "js": {...}, "text": {en: tr}}
#               shared by every page and site: the template's fixed strings (UI_EN keys), the
#               strings of the shared JS (JS_UI_EN keys) and phrases many cards repeat
#               ("Check Availability →", "per adult", "Personally tested", ...)
#   page file   data/listicles/i18n/<slug>/<lang>.json
#               {"format": 1, "lang", "ui"?, "js"?, "urls": {en url: lang url},
#                "text": {English fragment: translation}}
#               ("js" may also hold strings for the page's own inline scripts, which read the same
#               #listicle-ui block with English defaults, e.g. the river page's guest-video tiles)
#
# "text" is keyed by the English fragment itself, so a translation belongs to one exact English
# wording. When English changes, its new wording has no translation and `missing` lists it; a change
# that only touches numbers (a price, a time, a count) is carried into the old translation
# automatically when every changed number appears in it once ("numbers updated", listed for review).
# Strings with no words (prices, "4.5", "(10.9k+)", "1 / 9") are facts and pass through as they are.
# "urls" maps English link targets to the language's (a booking page in that language, an internal
# page's translated URL); it applies to data URLs and to href="..." inside translated text. Every
# other URL stays exactly as in English.
I18N_KIT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runtime", "listicle", "i18n")
UI_ELEMENT = "listicle-ui"
# Strings of the shared JS (runtime/listicle/*.js), English defaults. A language page gets its
# translations as <script type="application/json" id="listicle-ui"> (written by build-lang).
JS_UI_EN = {
    "locale": "en-GB",
    "more_filters": "More filters",
    "fewer_filters": "Fewer filters",
    "remove_filter": "Remove filter {label}",
    "showing": "Showing <b>{shown}</b> of {total} cruises",
    "mini_count": "<b>{shown}</b> of {total} cruises",
    "breakdown_filtered": "Showing {shown} of {total} cruises matching your filters",
    "other_date": "Other date",
    "sun_note": "🌇 Sunset {sun}: board about 20 min before ({board}) to catch it  ·  🌃 City lit up {dark} to 22:00 ({date})",
    "slot_closed": "📅 <b>{date}:</b> this date is not open for booking yet, so its sailing times are not out. "
                   "It is fully dark from {dark}: pick a sailing after that when you book.",
    "dur_h": "{h} h",
    "dur_hm": "{h} h {m} min",
    "dur_m": "{m} min",
    "dinner_lit": "🌙 <b>{date}:</b> dark from {dark}, so the last {left} of dinner ({start} to {end}) is under the lights.",
    "dinner_sunset": "🌇 <b>{date}:</b> sunset ({sun}) happens during dinner; it is fully dark only after you dock ({dark}).",
    "dinner_day": "☀️ <b>{date}:</b> the cruise ends before sunset ({sun}).",
    "slot_day": "☀️ <b>{date}:</b> the last sailing ({last}) ends before full dark ({dark}).",
    "lit_head": "🌃 <b>City lit up on {date}: {dark} to 22:00</b>",
    "lit_why": "Lights are on from dusk, about 30 minutes after sunset, until the Parliament switches its "
               "floodlights off at 22:00.",
    "lit_board": "Board for the lights:",
    "lit_every": "{first} then every {step} min to {last}",
    "lit_late": "(later sailings: city lit, Parliament dark)",
    "lit_after22": "Its sailings start after 22:00: the city is lit, the Parliament is dark.",
    "lit_none": "No sailing starts after dark on this date.",
    # a page that names its own landmark / end time (.fbm-mrow data-lit-what, data-lit-end)
    "sun_note_end": "🌇 Sunset {sun}: board about 20 min before ({board}) to catch it  ·  🌃 City lit up {dark} to {end} ({date})",
    "sun_note_open": "🌇 Sunset {sun}: board about 20 min before ({board}) to catch it  ·  🌃 City lit up from {dark} ({date})",
    "lit_head_end": "🌃 <b>City lit up on {date}: {dark} to {end}</b>",
    "lit_head_open": "🌃 <b>City lit up on {date}: from {dark}</b>",
    "lit_why_end": "Lights are on from dusk, about 30 minutes after sunset, until {what} goes dark at {end}.",
    "lit_why_open": "Lights are on from dusk, about 30 minutes after sunset, when the city and {what} light up.",
    "lit_late_end": "(later sailings: city lit, {what} dark)",
    "lit_after_end": "Its sailings start after {end}: the city is lit, {what} is dark.",
    "audio_in": "Audio in {lang} ✓",
    "lang_names": {},
}
# card keys whose strings are never translated (facts, formatting, brand names)
FACT_KEYS = {"id", "cats", "attrs", "url", "rel", "target", "onclick", "medal", "stars", "score", "tt",
             "_tt_raw", "dur", "kind", "icon", "icon_alt", "site", "cls", "data", "emoji", "thumbs", "_order",
             "_media_ws", "_photo_sep", "_photo_sep_end", "_tag", "_chev", "_nl"}
PHOTO_TEXT_ATTRS = {"alt", "title"}
NUM = re.compile(r"\d+(?:[.,:]\d+)*")


def translatable(s):
    """Has words (two letters in a row outside tags): prices, scores and counts do not."""
    return bool(re.search(r"[^\W\d_]{2}", re.sub(r"<[^>]+>|&[#\w]+;", " ", s)))


def text_leaves(data):
    """(where, getter-path) of every translatable string in the card data, in page order."""
    out = []

    def walk(v, path, key):
        if isinstance(v, dict):
            for k, x in v.items():
                if k not in FACT_KEYS:
                    walk(x, path + [k], k)
        elif isinstance(v, list):
            if key == "photos":
                for i, attrs in enumerate(v):
                    for j, (name, val) in enumerate(attrs):
                        if name in PHOTO_TEXT_ATTRS and translatable(val):
                            out.append(path + [i, j, 1])
                return
            for i, x in enumerate(v):
                walk(x, path + [i], key)
        elif isinstance(v, str) and translatable(v):
            out.append(path)
    for n, card in enumerate(data["cards"]):
        walk(card, ["cards", n], "")
    return out


def get_in(d, path):
    for k in path:
        d = d[k]
    return d


def set_in(d, path, v):
    for k in path[:-1]:
        d = d[k]
    d[path[-1]] = v


def where(data, path):
    card = data["cards"][path[1]]
    rest = "".join(f"[{k}]" if isinstance(k, int) else f".{k}" for k in path[2:]).lstrip(".")
    return f"{card.get('id', '#%d' % (path[1] + 1))} {rest}"


def links_of(h):
    return sorted(_html.unescape(x) for x in re.findall(r'<a\b[^>]*\bhref="([^"]*)"', h))


def tags_of(h):
    norm = re.sub(r'\b(title|alt|aria-label)="[^"]*"', r'\1=""', h)
    return sorted(re.findall(r"<[^>]+>", norm))


def map_hrefs(h, urls):
    if not urls:
        return h
    return re.sub(r'(\bhref=")([^"]*)(")',
                  lambda m: m.group(1) + esc(urls.get(_html.unescape(m.group(2)), _html.unescape(m.group(2))))
                  + m.group(3) if _html.unescape(m.group(2)) in urls else m.group(0), h)


class Lang:
    """Translations for one page and language: page file over the kit table."""

    def __init__(self, en_page, lang):
        self.lang = lang
        self.path = i18n_path(en_page, lang)
        kit = os.path.join(I18N_KIT, lang + ".json")
        self.kit = json.load(open(kit, encoding="utf-8")) if os.path.exists(kit) else {}
        self.page = json.load(open(self.path, encoding="utf-8")) if os.path.exists(self.path) else {}
        self.urls = dict(self.page.get("urls", {}))
        self.text = dict(self.kit.get("text", {}))
        self.text.update(self.page.get("text", {}))
        self.ui = {**UI_EN, **self.kit.get("ui", {}), **self.page.get("ui", {})}
        self.js = {**self.kit.get("js", {}), **self.page.get("js", {})}
        if "lang_names" in self.kit.get("js", {}) and "lang_names" in self.page.get("js", {}):
            self.js["lang_names"] = {**self.kit["js"]["lang_names"], **self.page["js"]["lang_names"]}
        self.by_shape = {}
        for en, t in self.text.items():
            self.by_shape.setdefault(NUM.sub("#", en), []).append((en, t))
        self.used, self.missing, self.renumbered, self.bad_links, self.bad_tags = set(), [], [], [], []
        self.too_long = []   # (where, english, translation): one-line labels over FIT_BUDGET

    def renumber(self, s):
        """Translation of s via an entry that differs from s only in numbers, or None."""
        new = NUM.findall(s)
        for en, t in self.by_shape.get(NUM.sub("#", s), []):
            old = NUM.findall(en)
            pairs = {}
            if len(old) != len(new) or any(pairs.setdefault(a, b) != b for a, b in zip(old, new)):
                continue
            changed = {a: b for a, b in pairs.items() if a != b}
            toks = NUM.findall(t)
            if any(toks.count(a) != 1 for a in changed):
                continue
            return en, NUM.sub(lambda m: changed.get(m.group(0), m.group(0)), t)
        return None

    def get(self, s, at):
        if s in self.text:
            self.used.add(s)
            t = self.text[s]
        else:
            hit = self.renumber(s)
            if not hit:
                self.missing.append((at, s))
                return None
            self.used.add(hit[0])
            self.renumbered.append((at, hit[0], s))
            t = hit[1]
        t = map_hrefs(t, self.urls)
        if too_long(s, t, at):
            self.too_long.append((at, s, t))
        if links_of(t) != links_of(map_hrefs(s, self.urls)):
            self.bad_links.append((at, s, t))
        elif tags_of(t) != tags_of(map_hrefs(s, self.urls)):
            self.bad_tags.append((at, s, t))
        return t

    def translate(self, data):
        out = json.loads(json.dumps(data))
        for path in text_leaves(data):
            s = get_in(data, path)
            t = self.get(s, where(data, path))
            set_in(out, path, map_hrefs(s, self.urls) if t is None else t)

        def urlmap(v):
            if isinstance(v, dict):
                for k, x in v.items():
                    if k == "url" and isinstance(x, str):
                        v[k] = self.urls.get(x, x)
                    else:
                        urlmap(x)
            elif isinstance(v, list):
                for x in v:
                    urlmap(x)
        urlmap(out["cards"])
        return out

    def ui_json(self):
        # kit keys are the shared JS strings; a page file may add keys for the page's own scripts
        js = {k: v for k, v in self.js.items() if k in JS_UI_EN or k in self.page.get("js", {})}
        return json.dumps(js, ensure_ascii=False, sort_keys=True).replace("</", "<\\/") if js else ""


def slug_of(page):
    rel = os.path.relpath(os.path.abspath(page), ROOT)
    return (rel[:-5] if rel.endswith(".html") else rel).replace(os.sep, "--")


def i18n_path(en_page, lang):
    return os.path.join(ROOT, "data", "listicles", "i18n", slug_of(en_page), lang + ".json")


def lang_page(en_page, lang):
    """The language version's file, from the English page's hreflang link."""
    src = open(en_page, encoding="utf-8").read()
    m = re.search(r'<link\b(?=[^>]*\bhreflang="%s")[^>]*\bhref="([^"]+)"' % re.escape(lang), src)
    if not m:
        raise SystemExit(f"{os.path.relpath(en_page, ROOT)} has no hreflang=\"{lang}\" link")
    path = _html.unescape(re.sub(r"^https?://[^/]+", "", m.group(1))).strip("/")
    for c in (path + ".html", os.path.join(path, "index.html"), path):
        if c and os.path.isfile(os.path.join(ROOT, c)):
            return os.path.join(ROOT, c)
    raise SystemExit(f"no file for the {lang} page {m.group(1)}")


UI_BLOCK = re.compile(r'<script type="application/json" id="%s">\{.*?\}</script>' % UI_ELEMENT, re.S)


def build_lang_page(src, data, tr):
    """The language page with its card region rendered from data (already translated) and the
    JS strings block refreshed (inserted just before the cards when the page has none)."""
    global UI
    saved, UI = UI, tr.ui
    try:
        cards = render_cards(data)
    finally:
        UI = saved
    start, end, _ = region(src)
    out = src[:start] + cards + src[end:]
    block = f'<script type="application/json" id="{UI_ELEMENT}">{tr.ui_json()}</script>' if tr.ui_json() else ""
    m = UI_BLOCK.search(out)
    if m:
        out = out[:m.start()] + block + out[m.end():]
    elif block:
        out = out[:start] + block + "\n" + out[start:]
    return out


def report(tr, data, verbose=True):
    """Lines describing what a language build lacks or should be reviewed."""
    lines = []
    seen = set()
    miss = [(a, s) for a, s in tr.missing if not (s in seen or seen.add(s))]
    if miss:
        lines.append(f"{len(miss)} untranslated string(s) (built in English until translated):")
        lines += [f"  {a}: {s[:160]}" for a, s in miss] if verbose else []
    if tr.renumbered:
        lines.append(f"{len(tr.renumbered)} translation(s) with numbers carried over from English (review):")
        lines += [f"  {a}: {old[:70]!r} -> {new[:70]!r}" for a, old, new in tr.renumbered] if verbose else []
    if tr.bad_links:
        lines.append(f"{len(tr.bad_links)} translation(s) whose links differ from English (fix or add to \"urls\"):")
        lines += [f"  {a}: {links_of(s)} vs {links_of(t)}" for a, s, t in tr.bad_links]
    if tr.too_long:
        lines.append(f"{len(tr.too_long)} label(s) too long for one line (shorten; `translate` redoes them):")
        lines += [f"  {a}: {_html.unescape(t)[:90]!r} ({too_long(s, t, a).split(': ', 1)[1].split(' (')[0]})"
                  for a, s, t in tr.too_long]
    if tr.bad_tags and verbose:
        lines.append(f"{len(tr.bad_tags)} translation(s) with other markup than English (check):")
        lines += [f"  {a}: {s[:90]}" for a, s, t in tr.bad_tags]
    js_missing = [k for k in JS_UI_EN if k not in tr.js and k != "lang_names"]
    ui_missing = [k for k in UI_EN if k not in tr.kit.get("ui", {}) and k not in tr.page.get("ui", {})]
    if ui_missing:
        lines.append(f"template strings without a {tr.lang} translation: {', '.join(ui_missing)}")
    if js_missing:
        lines.append(f"JS strings without a {tr.lang} translation: {', '.join(js_missing)}")
    unused = [k for k in tr.page.get("text", {}) if k not in tr.used]
    if unused:
        lines.append(f"{len(unused)} page translation(s) no longer used by the English cards (prune with --prune)")
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
    stale = [u for u in tr.urls if u not in en_urls]
    if stale:
        lines.append(f"{len(stale)} \"urls\" entr(ies) not used by the English cards: " + ", ".join(stale[:5]))
    internal = sorted(u for u in en_urls if u.startswith("/") and not u.startswith("//") and u not in tr.urls)
    if internal:
        lines.append("internal links kept as in English (add a \"urls\" entry if the page has a translation): "
                     + ", ".join(internal))
    return lines


def filter_cats(html):
    """The filter pill categories of a page (data-cat of .ltt-tab-btn, without "all")."""
    cats = set()
    for t in re.findall(r"<button\b[^>]*>", html):
        if re.search(r'class="[^"]*\bltt-tab-btn\b', t):
            m = re.search(r'data-cat="([^"]*)"', t)
            if m and m.group(1) != "all":
                cats.add(m.group(1))
    return cats


def lang_main(cmd, en_page, lang, opts):
    data = json.load(open(opts.get("--data") or data_path(en_page), encoding="utf-8"))
    tr = Lang(en_page, lang)
    out_data = tr.translate(data)
    rel = os.path.relpath(tr.path, ROOT)
    if cmd == "missing":
        lines = report(tr, data)
        print(f"{os.path.relpath(en_page, ROOT)} -> {lang} ({rel}):")
        print("\n".join("  " + x for x in lines) if lines else "  every card string is translated")
        if opts.get("--todo"):
            todo = {s: "" for _, s in tr.missing + [(a, s) for a, s, _ in tr.too_long]}
            with open(opts["--todo"], "w", encoding="utf-8") as fh:
                fh.write(dumps(todo) + "\n")
            print(f"  {len(todo)} untranslated string(s) written to {opts['--todo']}")
        if opts.get("--prune") and os.path.exists(tr.path):
            page = json.load(open(tr.path, encoding="utf-8"))
            order = [get_in(data, p) for p in text_leaves(data)]
            keep = {k: page["text"][k] for k in dict.fromkeys(order + sorted(tr.used)) if k in page.get("text", {})}
            dropped = len(page.get("text", {})) - len(keep)
            page["text"] = keep
            with open(tr.path, "w", encoding="utf-8") as fh:
                fh.write(dumps(page) + "\n")
            print(f"  pruned {dropped} unused translation(s), the rest in English card order")
        return 1 if (tr.missing or tr.bad_links or tr.too_long) else 0
    page = opts.get("--page") or lang_page(en_page, lang)
    if not os.path.isabs(page):
        page = os.path.join(ROOT, page)
    src = open(page, encoding="utf-8").read()
    prel = os.path.relpath(page, ROOT)
    # build-lang only swaps the cards: on a page still in an older design the new cards would meet an
    # old filter bar, sticky bar and intro (filters that match no card, outdated facts)
    en_cats, lang_cats = filter_cats(open(en_page, encoding="utf-8").read()), filter_cats(src)
    if en_cats != lang_cats and not opts.get("--check"):
        print(f"{prel}: not built, its page design is older than the English page "
              f"(filters {sorted(lang_cats) or 'none'} vs English {sorted(en_cats)}).")
        print(f"  Port the page first: python3 scripts/port_page_i18n.py {os.path.relpath(en_page, ROOT)} "
              f"--langs {lang} --cache-only --listicle-cards (--dump-todo DIR lists what needs translating), "
              "then run build-lang again.")
        return 1
    out = build_lang_page(src, out_data, tr)
    problems = report(tr, data, verbose=False)
    if (tr.missing or tr.bad_links) and not opts.get("--allow-missing"):
        print(f"{prel}: not built, translations missing or links differ:")
        print("\n".join("  " + x for x in report(tr, data)))
        print(f"  (python3 scripts/listicle.py missing {os.path.relpath(en_page, ROOT)} {lang} lists them; "
              "--allow-missing builds with English in their place)")
        return 1
    if opts.get("--check"):
        if out != src:
            print(f"{prel}: cards differ from the English data + {rel}")
            return 1
        print(f"{prel}: cards match the English data + {rel}")
        return 0
    if out != src:
        with open(page, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"{prel}: {len(data['cards'])} cards built in {lang}")
    else:
        print(f"{prel}: unchanged")
    for x in problems:
        print("  " + x)
    if opts.get("--no-layout"):
        return 0
    # longer languages break one-line labels: measure the built page in a browser (skipped without one)
    import check_listicle_layout
    return check_listicle_layout.check([prel])


# ------------------------------------------------------------------ automatic translation (translate)
# `translate <english-page> <lang> [--todo=FILE] [--dry-run]` sends the untranslated card strings
# (the `missing --todo` list, or what `missing` would list) to the Claude API in batches and writes
# every translation that passes validate() into data/listicles/i18n/<slug>/<lang>.json. A string that
# fails is reported and never written. Order of work for a language version: harvest what the site
# already has (listicle_harvest.py), translate the rest, review, then build-lang.
TRANSLATE_MODEL = "claude-opus-5-5"
FALLBACK_MODELS = ("claude-opus-5-5", "claude-opus-5", "claude-fable-5", "claude-sonnet-5-5")
LANG_NAMES = {
    "hu": "Hungarian", "de": "German", "fr": "French", "it": "Italian", "es": "Spanish", "ro": "Romanian",
    "pl": "Polish", "nl": "Dutch", "cs": "Czech", "sk": "Slovak", "pt": "Portuguese", "ru": "Russian",
    "hr": "Croatian", "sr": "Serbian (Cyrillic script)", "bg": "Bulgarian", "el": "Greek", "tr": "Turkish",
    "uk": "Ukrainian", "he": "Hebrew", "ja": "Japanese", "ko": "Korean", "zh": "Chinese (Simplified)",
}
# How the existing pages address the reader (counted on the sites' translations); the prompt also
# shows existing translations of the page so the model follows their wording.
REGISTER = {
    "de": "formal 'Sie'", "fr": "formal 'vous'", "it": "informal 'tu' (vuoi, puoi)",
    "es": "informal 'tú' (quieres, puedes)", "pt": "'você'", "nl": "informal 'je'",
    "pl": "informal 'ty' (chcesz, możesz)", "ro": "'tu' (vrei, poți)", "cs": "formal 'vy' (chcete)",
    "sk": "formal 'vy' (chcete)", "hr": "formal/plural 'vi' (želite)", "sr": "formal/plural 'ви' (желите)",
    "bg": "formal/plural 'вие' (искате)", "uk": "formal 'ви' (хочете)", "ru": "formal 'вы' (хотите)",
    "el": "formal/plural (θέλετε)", "tr": "polite 'siz' (isterseniz)", "he": "plural 'אתם'",
    "ja": "polite です/ます style", "ko": "polite 합니다/해요 style",
}
TRANSLATE_SYSTEM = """You translate the comparison cards of a travel site's listicle page (Danube cruises in Budapest) from English into {lang}.

Each item is an HTML fragment from one card ("where" says which part: title, pill label, popover, question, answer, Pick/Skip sentence, price label, photo alt text). Translate it for travellers reading {lang}: natural, concise, same meaning and tone, about the same length (labels must stay short).

Hard rules (a translation that breaks one is rejected automatically):
- Keep every HTML tag, in the same order, with the same attributes and values. Translate only the text between tags (and title/alt/aria-label values).
- Keep every number exactly as in English: prices, currencies (€, Ft), times (write 24-hour times like 21:00 exactly as given), durations, counts, ratings, dock numbers. Do not write numbers as words or words as numbers.
- Keep URLs and placeholders such as {{n}} exactly.
- Keep emoji (🏆 🥂 ⏱️ 📍 ✓ ...) where they are.
- Never translate names of boats, operators, companies, docks, streets, places or sites: {names}, Vigadó tér, Jane Haining rakpart, Akadémia, GetYourGuide, Viator, Tripadvisor, Budapest Adventures. Bridges and landmarks (Elizabeth Bridge, Chain Bridge, Parliament) take the form the existing translations use.
- Address the reader with {register}, as the existing translations below do.
- No em dashes (—): use a comma, colon or an en dash with spaces.
- Do not add claims (independent, unsponsored, paid our own tickets, ...) that the English does not make.
- A fragment that is only a name stays as it is.
- The rank tag on the photo (where ends in "gallery.rank.text") must fit on one line: at most {fit_rank} characters (or the English length if longer). Shorten it rather than translate word for word; keep the emoji and the "#N".

Existing translations on this site (follow their wording for the same terms):
{glossary}

Return every id you were given exactly once, with its translation in "html"."""
TRANSLATE_SCHEMA = {
    "type": "object",
    "properties": {"items": {"type": "array", "items": {
        "type": "object", "properties": {"id": {"type": "string"}, "html": {"type": "string"}},
        "required": ["id", "html"], "additionalProperties": False}}},
    "required": ["items"], "additionalProperties": False,
}
TIME = re.compile(r"(?<![\d:])\d{1,2}:\d{2}(?![\d:])")
PLACEHOLDER = re.compile(r"\{[a-z_]+\}")
CURRENCY_RE = re.compile(r"€|\$|£|\bFt\b|\bHUF\b|\bEUR\b|\bUSD\b")
URL_RE = re.compile(r"https?://[^\s\"'<>]+")
TR_ATTRS = r"title|alt|aria-label|placeholder"


def tag_sequence(h):
    """The tags of a fragment in order, translatable attribute values blanked."""
    return [re.sub(r'\b(%s)="[^"]*"' % TR_ATTRS, r'\1=""', t) for t in re.findall(r"<[^>]+>", h)]


def visible(h):
    """Text a reader sees (tags out, entities decoded), plus translatable attribute values."""
    attrs = " ".join(_html.unescape(v) for v in re.findall(r'\b(?:%s)="([^"]*)"' % TR_ATTRS, h))
    import unicodedata
    return unicodedata.normalize("NFKC", _html.unescape(re.sub(r"<[^>]+>", " ", h)) + " " + attrs)


def emoji_of(s):
    """Emoji and pictographs (✓ ✕ 🏆 ⏱️ ...), not arrows or letters."""
    return sorted(ch for ch in s if ord(ch) >= 0x1F000 or 0x2600 <= ord(ch) <= 0x27BF or 0x2B00 <= ord(ch) <= 0x2BFF)


# Short labels that sit on a photo or a button and must stay on one line (listicle-cards.js shrinks
# them a little, check_listicle_layout.py measures the result). A translation may be as long as the
# English or this many visible characters, whichever is more.
FIT_BUDGET = {"gallery.rank.text": 42}


def fit_budget(at):
    """The one-line character budget for the card part `at` ("card-1 gallery.rank.text"), or None."""
    part = (at or "").split(" ", 1)[-1]
    return FIT_BUDGET.get(part)


def too_long(en, tr, at):
    """'too long for one line ...' when a one-line label is over its budget, else None."""
    budget = fit_budget(at)
    if budget is None:
        return None
    n, limit = len(visible(tr).strip()), max(budget, len(visible(en).strip()))
    if n > limit:
        return f"too long for one line: {n} characters, max {limit} (shorten it, keep the meaning)"
    return None


def validate(en, tr, lang=None, where=None):
    """Problems of a translated fragment against its English source; [] when it may be written.
    Pure function: same tag sequence, numbers (digit runs; 2.5 -> 2,5 is fine), times, currency
    signs, URLs, placeholders and emoji; not empty, not plain English, no em dash; one-line labels
    (FIT_BUDGET, by `where`) within their length."""
    probs = []
    if not isinstance(tr, str) or not tr.strip():
        return ["empty"]
    if tag_sequence(en) != tag_sequence(tr):
        probs.append("HTML tags differ")
    ve, vt = visible(en), visible(tr)
    if sorted(re.findall(r"\d+", ve)) != sorted(re.findall(r"\d+", vt)):
        probs.append("numbers differ: %s vs %s" % (re.findall(r"\d+(?:[.,:]\d+)*", ve),
                                                    re.findall(r"\d+(?:[.,:]\d+)*", vt)))
    if sorted(TIME.findall(ve)) != sorted(TIME.findall(vt)):
        probs.append("times differ")
    if sorted(CURRENCY_RE.findall(ve)) != sorted(CURRENCY_RE.findall(vt)):
        probs.append("currency differs")
    if links_of(en) != links_of(tr) or sorted(URL_RE.findall(_html.unescape(en))) != sorted(URL_RE.findall(_html.unescape(tr))):
        probs.append("URLs differ")
    if sorted(PLACEHOLDER.findall(en)) != sorted(PLACEHOLDER.findall(tr)):
        probs.append("placeholders differ")
    if emoji_of(en) != emoji_of(tr):
        probs.append("emoji differ")
    if "—" in tr and "—" not in en:
        probs.append("em dash")
    long_ = too_long(en, tr, where)
    if long_:
        probs.append(long_)
    words_en = re.findall(r"[^\W\d_]+", ve)
    if tr.strip() == en.strip() and len(words_en) >= 3 and not all(w[0].isupper() for w in words_en):
        probs.append("returned unchanged (English)")
    return probs


def load_api_key():
    """ANTHROPIC_API_KEY from the environment or the site's .env (in a worktree: the main checkout's)."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]
    import subprocess
    cands = [os.path.join(ROOT, ".env")]
    try:
        common = subprocess.run(["git", "rev-parse", "--git-common-dir"], cwd=ROOT, capture_output=True,
                                text=True).stdout.strip()
        if common:
            cands.append(os.path.join(os.path.dirname(os.path.abspath(os.path.join(ROOT, common))), ".env"))
    except OSError:
        pass
    for env in cands:
        if os.path.exists(env):
            for line in open(env, encoding="utf-8"):
                if line.startswith("ANTHROPIC_API_KEY="):
                    key = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if key:
                        os.environ["ANTHROPIC_API_KEY"] = key
                        return key
    return None


def glossary(tr, data, limit=120):
    """Existing translations of this language to show the model: short terms first (labels,
    pills), then a few full sentences for the register."""
    seen, short, long_ = set(), [], []
    texts = list(tr.page.get("text", {}).items()) + list(tr.kit.get("text", {}).items())
    base = os.path.join(ROOT, "data", "listicles", "i18n")
    if os.path.isdir(base):
        for d in sorted(os.listdir(base)):
            f = os.path.join(base, d, tr.lang + ".json")
            if os.path.exists(f) and os.path.abspath(f) != os.path.abspath(tr.path):
                texts += list(json.load(open(f, encoding="utf-8")).get("text", {}).items())
    for en, t in texts:
        if en in seen or not translatable(en) or en == t:
            continue
        seen.add(en)
        n = len(re.findall(r"\w+", re.sub(r"<[^>]+>", " ", en)))
        (short if n <= 5 else long_).append((en, t))
    pick = short[:limit] + [x for x in long_ if len(x[0]) < 300][:12]
    return "\n".join(f"- {json.dumps(e, ensure_ascii=False)} -> {json.dumps(t, ensure_ascii=False)}"
                     for e, t in pick) or "(none yet)"


def name_list(data):
    """Operator / boat names from the cards' kicker (first part), kept untranslated."""
    names = []
    for c in data["cards"]:
        k = c.get("kicker")
        if isinstance(k, list) and k and isinstance(k[0], str):
            names.append(re.sub(r"<[^>]+>", "", _html.unescape(k[0])).strip())
    return ", ".join(dict.fromkeys(n for n in names if n))


def todo_items(en_page, lang, data, opts):
    """[(english, where)] still untranslated: the --todo file's keys (or missing()), minus what the
    language file has gained since."""
    tr = Lang(en_page, lang)
    tr.translate(data)
    where_of = {s: a for a, s in tr.missing + [(a, s) for a, s, _ in tr.too_long]}
    if opts.get("--todo"):
        keys = list(json.load(open(opts["--todo"], encoding="utf-8")))
    else:
        keys = list(where_of)
    keys = [k for k in dict.fromkeys(keys) if k in where_of]
    return [(k, where_of[k]) for k in keys], tr


def batches_of(items, size):
    out, cur, n = [], [], 0
    for it in items:
        if cur and n + len(it[0]) > size:
            out.append(cur)
            cur, n = [], 0
        cur.append(it)
        n += len(it[0])
    if cur:
        out.append(cur)
    return out


def call_model(client, model, system, payload):
    """One batch -> {id: html}. Raises RuntimeError on a refusal or a cut-off answer."""
    kw = dict(model=model, max_tokens=64000, system=system,
              output_config={"effort": os.environ.get("LISTICLE_TRANSLATE_EFFORT", "medium"),
                             "format": {"type": "json_schema", "schema": TRANSLATE_SCHEMA}},
              messages=[{"role": "user", "content": json.dumps({"items": payload}, ensure_ascii=False)}])
    if model in FALLBACK_MODELS:   # a refused batch is retried on the fallback model server-side
        kw.update(betas=["server-side-fallback-2026-07-01"], fallbacks="default")
    with client.beta.messages.stream(**kw) as stream:
        msg = stream.get_final_message()
    if msg.stop_reason != "end_turn":
        raise RuntimeError(f"stop_reason={msg.stop_reason}")
    text = next(b.text for b in msg.content if b.type == "text")
    return {it["id"]: it["html"] for it in json.loads(text)["items"]}, msg.usage


def translate_main(en_page, lang, opts):
    data = json.load(open(opts.get("--data") or data_path(en_page), encoding="utf-8"))
    items, tr = todo_items(en_page, lang, data, opts)
    rel = os.path.relpath(tr.path, ROOT)
    if not items:
        print(f"{os.path.relpath(en_page, ROOT)} -> {lang}: nothing to translate ({rel} is complete)")
        return 0
    model = os.environ.get("LISTICLE_TRANSLATE_MODEL") or TRANSLATE_MODEL
    system = TRANSLATE_SYSTEM.format(lang=LANG_NAMES.get(lang, lang), names=name_list(data) or "-",
                                     fit_rank=FIT_BUDGET["gallery.rank.text"],
                                     register=REGISTER.get(lang, "the polite form usual on travel sites"),
                                     glossary=glossary(tr, data))
    size = int(opts.get("--batch-chars") or 12000)
    bats = batches_of(items, size)
    chars = sum(len(e) for e, _ in items)
    ratio = 1.6 if lang in ("ja", "ko", "he", "el", "bg", "ru", "uk", "sr") else 1.3
    est_in = (len(system) * len(bats) + chars + 60 * len(items)) // 3
    est_out = int(chars * ratio) // 3 + 15 * len(items)
    words = sum(len(re.findall(r"[^\W\d_]+", re.sub(r"<[^>]+>", " ", e))) for e, _ in items)
    print(f"{os.path.relpath(en_page, ROOT)} -> {lang} with {model}: {len(items)} string(s), {words} words, "
          f"{chars} chars in {len(bats)} batch(es); about {est_in} input / {est_out} output tokens")
    if opts.get("--dry-run"):
        print("--- system prompt ---\n" + system)
        for i, b in enumerate(bats, 1):
            payload = [{"id": f"t{j}", "where": w, "html": e} for j, (e, w) in enumerate(b)]
            print(f"--- batch {i}/{len(bats)}: {len(b)} string(s), {sum(len(e) for e, _ in b)} chars ---")
            print(json.dumps({"items": payload}, ensure_ascii=False, indent=1))
        print("(dry run: nothing sent, nothing written)")
        return 0
    if not load_api_key():
        print("ANTHROPIC_API_KEY is not set (environment or the site's .env): nothing was translated or "
              "changed. Set it, or use --dry-run to see what would be sent.")
        return 2
    try:
        import anthropic
    except ImportError:
        print("the anthropic package is not installed (pip install anthropic): nothing changed")
        return 2
    client = anthropic.Anthropic()
    page = json.load(open(tr.path, encoding="utf-8")) if os.path.exists(tr.path) else {"format": 1, "lang": lang}
    page.setdefault("text", {})
    side_path = tr.path[:-5] + ".translated.json"
    side = json.load(open(side_path, encoding="utf-8")) if os.path.exists(side_path) else \
        {"format": 1, "lang": lang, "comment": "Entries of %s written by `listicle.py translate` "
         "(machine translation: review before publishing)." % os.path.basename(tr.path), "entries": {}}
    redo = {s for _, s, _ in tr.too_long}   # over-long labels: the new translation replaces the old one
    ok, bad = 0, []
    for i, b in enumerate(bats, 1):
        payload = [{"id": f"t{j}", "where": w, "html": e} for j, (e, w) in enumerate(b)]
        try:
            got, usage = call_model(client, model, system, payload)
        except (RuntimeError, ValueError, StopIteration, anthropic.APIError) as why:
            print(f"  batch {i}/{len(bats)}: failed ({why}); its {len(b)} string(s) stay untranslated")
            bad += [(e, w, [f"batch failed: {why}"]) for e, w in b]
            continue
        for j, (e, w) in enumerate(b):
            t = got.get(f"t{j}")
            probs = ["no answer for this id"] if t is None else validate(e, t, lang, where=w)
            if probs:
                bad.append((e, w, probs))
            elif e not in page["text"] or e in redo:
                page["text"][e] = t
                side["entries"][e] = {"model": model, "where": w}
                ok += 1
        os.makedirs(os.path.dirname(tr.path), exist_ok=True)
        order = [get_in(data, pth) for pth in text_leaves(data)]
        page["text"] = {**{k: page["text"][k] for k in dict.fromkeys(order) if k in page["text"]}, **page["text"]}
        with open(tr.path, "w", encoding="utf-8") as fh:
            fh.write(dumps(page) + "\n")
        with open(side_path, "w", encoding="utf-8") as fh:
            fh.write(dumps(side) + "\n")
        print(f"  batch {i}/{len(bats)}: {len(b)} sent, usage in/out {usage.input_tokens}/{usage.output_tokens}")
    print(f"  {ok} translation(s) written to {rel}, {len(bad)} rejected")
    for e, w, probs in bad:
        print(f"  REJECTED {w}: {'; '.join(probs)}: {e[:100]}")
    if opts.get("--rejects") and bad:
        with open(opts["--rejects"], "w", encoding="utf-8") as fh:
            fh.write(dumps({e: {"where": w, "problems": p} for e, w, p in bad}) + "\n")
    print(f"  next: review, then python3 scripts/listicle.py missing {os.path.relpath(en_page, ROOT)} {lang}")
    return 1 if bad else 0


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    opts = {a.split("=")[0]: (a.split("=", 1)[1] if "=" in a else True) for a in argv if a.startswith("--")}
    if len(args) == 3 and args[0] in ("build-lang", "missing", "translate"):
        page = args[1] if os.path.isabs(args[1]) or os.path.exists(args[1]) else os.path.join(ROOT, args[1])
        if args[0] == "translate":
            return translate_main(page, args[2], opts)
        return lang_main(args[0], page, args[2], opts)
    if len(args) != 2 or args[0] not in ("extract", "build", "stats"):
        print(__doc__)
        return 2
    cmd, page = args
    if not os.path.isabs(page) and not os.path.exists(page):
        page = os.path.join(ROOT, page)
    src = open(page, encoding="utf-8").read()
    dpath = opts.get("--data") or data_path(page)
    if cmd == "extract":
        data = extract_page(src)
        if build_page(src, data) != src:
            raise SystemExit("internal error: extracted data does not rebuild the page")
        os.makedirs(os.path.dirname(dpath), exist_ok=True)
        with open(dpath, "w", encoding="utf-8") as fh:
            fh.write(dumps(data) + "\n")
        print(f"{os.path.relpath(page, ROOT)}: {len(data['cards'])} cards -> {os.path.relpath(dpath, ROOT)}")
        for where, why in MISSES:
            print(f"  kept as raw: {where}: {why}")
        return 0
    data = json.load(open(dpath, encoding="utf-8"))
    if cmd == "stats":
        print(os.path.relpath(page, ROOT))
        print(stats(src, data))
        return 0
    out = build_page(src, data)
    if opts.get("--check"):
        if out != src:
            print(f"{os.path.relpath(page, ROOT)}: cards differ from {os.path.relpath(dpath, ROOT)}")
            return 1
        print(f"{os.path.relpath(page, ROOT)}: cards match the data")
        return 0
    if out != src:
        with open(page, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"{os.path.relpath(page, ROOT)}: {len(data['cards'])} cards rebuilt")
    else:
        print(f"{os.path.relpath(page, ROOT)}: unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
