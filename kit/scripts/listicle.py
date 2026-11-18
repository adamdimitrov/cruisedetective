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

Usage: python3 scripts/listicle.py extract|build|stats <page.html> [--data FILE] [--check]
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
ARROW_PREV = ('<button aria-label="Previous photo" class="bpa-arrow prev" onclick="bpaSlide(this,-1)" '
              'type="button">‹</button>')
ARROW_NEXT = ('<button aria-label="Next photo" class="bpa-arrow next" onclick="bpaSlide(this,1)" '
              'type="button">›</button>')
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
    if prev.outer() != ARROW_PREV or nxt.outer() != ARROW_NEXT:
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
    want = [["aria-label", f"Photo gallery {num}"], ["class", "bpa-slider"],
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
    if thumbs.start != '<div class="cd-thumbs" aria-label="Photo thumbnails">':
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
            f'aria-label="Show photo {i + 1} of {nt}">')


def render_gallery(g, num):
    photos = g["photos"]
    sep = g.get("_photo_sep", "")
    imgs = "".join(sep + tag("img", p, True) for p in photos)
    if sep and g.get("_photo_sep_end", True):
        imgs += sep
    pill = g.get("_pill", f"1 / {len(photos)}")
    label = g.get("_gallery_label", f"Photo gallery {num}")
    nt = len(g["thumbs"])
    thumbs = "".join(
        (t.get("_tag") or thumb_tag(i, nt, len(photos)))
        + f'<img src="{esc(t["src"])}"{THUMB_IMG}</button>'
        for i, t in enumerate(g["thumbs"]))
    w = g.get("_media_ws", MEDIA_WS)
    return ('<div class="cd-gal"><div class="bpa-media">' + w[0]
            + el("span", {"class": "bpa-rank-tag " + g["rank"]["medal"]}, g["rank"]["text"]) + w[1]
            + ARROW_PREV + w[2] + ARROW_NEXT + w[3] + f'<span class="bpa-pill">{pill}</span>' + w[4]
            + tag("div", [["aria-label", label], ["class", "bpa-slider"],
                          ["onscroll", "bpaCount(this)"], ["tabindex", "0"]])
            + imgs + "</div>" + w[5] + "</div>"
            + '<div class="cd-thumbs" aria-label="Photo thumbnails">' + thumbs + "</div></div>")


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


PICK = '<span class="bpa-pick">✓ Pick it</span> '
SKIP = ' <span class="bpa-skip">✕ Skip it</span> '


def ex_bestfor(n):
    if n.start != '<div class="bpa-best-for bpa-pickskip">':
        raise Unmodelled("best-for tag")
    m = re.fullmatch(r'<span class="bpa-pick">(.*?)</span> (.*) <span class="bpa-skip">(.*?)</span> (.*)',
                     n.inner(), re.S)
    if not m:
        raise Unmodelled("pick/skip shape")
    out = {"pick_html": m.group(2), "skip_html": m.group(4)}
    if m.group(1) != "✓ Pick it":
        out["_pick_label"] = m.group(1)
    if m.group(3) != "✕ Skip it":
        out["_skip_label"] = m.group(3)
    return out


def render_bestfor(b):
    return ('<div class="bpa-best-for bpa-pickskip"><span class="bpa-pick">' + b.get("_pick_label", "✓ Pick it")
            + "</span> " + b["pick_html"] + ' <span class="bpa-skip">' + b.get("_skip_label", "✕ Skip it")
            + "</span> " + b["skip_html"] + "</div>")


FAQ_CHEV = ' <span class="fbm-faq-chev" aria-hidden="true">▾</span>'


def faq_title(n):
    return f"❓ {n} questions travellers ask"


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
PDD_HEAD = "All ticket prices"


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
    if kids[0].inner() != PDD_HEAD:
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
            + f'<div class="cd-pdd-h">{p.get("_heading", PDD_HEAD)}</div>' + rows + total + note
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


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    opts = {a.split("=")[0]: (a.split("=", 1)[1] if "=" in a else True) for a in argv if a.startswith("--")}
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
