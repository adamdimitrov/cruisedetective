#!/usr/bin/env python3
"""The site menu (<header class="ltt-navbar">) as data: data/menu/<lang>.json.

Shared kit script (kit/scripts/menu.py). The menu of each language lives in the
site's data/menu/<lang>.json; this script turns it into the header HTML of that
language's MASTER page (scripts/layout_config.json "masters"), and
scripts/sync_layout.py then copies the header from the master to every page.

    python3 scripts/menu.py extract [--lang xx]   # master page header -> data/menu/<lang>.json
    python3 scripts/menu.py build   [--lang xx]   # data/menu/<lang>.json -> master page header
    python3 scripts/menu.py build --check         # exit 1 when a master is out of date
    python3 scripts/sync_layout.py                # then spread it to every page

To change the menu: edit data/menu/<lang>.json, run build, then sync_layout.py.
Other kit code renders a menu dict with render_header(menu) (no site needed).

The JSON (every key is optional unless marked; leave out what you do not need):

  {
    "lang": "en",
    "brand": {"name": "BUDAPEST ADVENTURES", "href": "/", "aria": "BUDAPEST ADVENTURES Homepage",
              "logo": "/assets/logo.webp"},        # or "logo": {"src", "alt", "width", "height"}
    "nav_label": "Primary Navigation",
    "nav": [                                         # the desktop menu, left to right
      {"type": "dropdown", "label": "Cruises", "narrow": false, "right": false,
       "columns": [
         {"groups": [
           {"head": "River Cruises", "items": [
             {"href": "/best-budapest-river-cruises", "title": "Top 13 River Cruises",
              "desc": "Personally tested day & night boats",
              "thumb": "/assets/nav-thumbs/best-budapest-river-cruises.webp"},  # or "icon": "emoji"
           ]},
           {"head": "Experiences", "subitems": [{"href": "/x", "label": "Water Parks"}]}
         ]}
       ]},
      {"type": "link", "label": "About", "href": "/about"}
    ],
    "search": {"label": "Search"},                   # true = defaults, false = no search button
    "languages": [{"lang": "en", "name": "English", "href": "/", "current": true}, ...],
    "lang_switcher": {"heading": "Select Language", "count": "● 22 AVAILABLE", ...},
    "hamburger": {"label": "Toggle Menu"},
    "drawer": [                                      # the mobile menu; left out = made from "nav"
      {"type": "accordion", "label": "Cruises", "groups": [
         {"head": "River Cruises", "items": [{"href": "...", "title": "...", "thumb": "...", "tag": "TOP PICK"}]}]},
      {"type": "section", "groups": [{"head": "Editorial", "items": [{"href": "/about", "title": "About"}]}]},
      {"type": "languages", "label": "Language"}     # chips made from "languages"
    ],
    "after": [{"raw": "<style>...</style>"}]          # anything else inside <header>, kept as is
  }

Any entry may also be {"raw": "<html>"} (kept verbatim), and any component may carry
"attrs" (extra attributes), "classes" (extra classes) and "active": true (current page).
Text values are plain text (escaped on output); {"html": "..."} keeps markup as is.

"_fmt" keys are formatting hints written by extract so that build reproduces the master
byte for byte (whitespace and HTML comments between tags, attribute order, `inert` vs
`inert=""`, `<img>` vs `<img/>`). They are optional: a hand-written menu has none and gets
the standard layout. "icons" overrides the standard SVG icons (chevron, search, globe).
"""
import argparse
import html as _html
import json
import os
import re
import sys
from collections import Counter

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
RAWTEXT = {"script", "style"}
PAT_HEADER = re.compile(r'<header[^>]*class="[^"]*\bltt-navbar\b[^"]*".*?</header>', re.S)

DEFAULT_ICONS = {
    "chevron": '<svg class="ltt-chevron" fill="none" height="12" stroke="currentColor" stroke-linecap="round" '
               'stroke-linejoin="round" stroke-width="2.5" viewbox="0 0 24 24" width="12">'
               '<polyline points="6 9 12 15 18 9"></polyline></svg>',
    "search": '<svg aria-hidden="true" fill="none" height="17" stroke="currentColor" stroke-linecap="round" '
              'stroke-linejoin="round" stroke-width="2.2" viewBox="0 0 24 24" width="17">'
              '<circle cx="11" cy="11" r="7"></circle><line x1="21" x2="16.65" y1="21" y2="16.65"></line></svg>',
    "globe": '<svg class="ltt-lang-globe" fill="none" height="13" stroke="currentColor" stroke-linecap="round" '
             'stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="13">\n'
             '<circle cx="12" cy="12" r="10"></circle>\n<line x1="2" x2="22" y1="12" y2="12"></line>\n'
             '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 '
             '4-10z"></path>\n</svg>',
    "lang_chevron": '<svg class="ltt-lang-chevron" fill="none" height="10" stroke="currentColor" '
                    'stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" viewbox="0 0 24 24" '
                    'width="10">\n<polyline points="6 9 12 15 18 9"></polyline>\n</svg>',
    "mobile_globe": '<svg fill="none" height="12" stroke="currentColor" stroke-linecap="round" '
                    'stroke-linejoin="round" stroke-width="2" viewbox="0 0 24 24" width="12">'
                    '<circle cx="12" cy="12" r="10"></circle><line x1="2" x2="22" y1="12" y2="12"></line>'
                    '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 '
                    '4-10z"></path></svg>',
}
COUNT_STYLE = "font-size:9px; color:#10b981; font-weight:800;"


class Miss(Exception):
    """The HTML does not have the shape a component expects (extract keeps it raw)."""


# ===================================================================== HTML parsing
# A small lossless parser: every element keeps its exact source, so extract can check
# that the structured data renders back to the same bytes.
TOKEN = re.compile(
    r"<!--.*?-->"
    r"|<([a-zA-Z][\w:-]*)((?:\s+[^\s\"'=<>/]+(?:\s*=\s*(?:\"[^\"]*\"|'[^']*'|[^\s\"'=<>`]+))?)*)\s*/?>"
    r"|</([a-zA-Z][\w:-]*)\s*>", re.S)
ATTR = re.compile(r"\s+([^\s\"'=<>/]+)(?:\s*=\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s\"'=<>`]+)))?")


class OEl:
    def __init__(self, tag, attrs, open_tag, start):
        self.tag, self.attrs, self.open, self.start = tag, attrs, open_tag, start
        self.kids, self.src = [], ""


class OText:
    def __init__(self, raw):
        self.raw = raw


class OComment:
    def __init__(self, raw):
        self.raw = raw


def parse(s):
    root = OEl("#root", [], "", 0)
    stack, pos = [root], 0

    def text(upto):
        if upto > pos:
            stack[-1].kids.append(OText(s[pos:upto]))

    while True:
        m = TOKEN.search(s, pos)
        if not m:
            text(len(s))
            break
        text(m.start())
        tok = m.group()
        if tok.startswith("<!--"):
            stack[-1].kids.append(OComment(tok))
            pos = m.end()
        elif m.group(1):
            tag = m.group(1).lower()
            attrs = []
            for a in ATTR.finditer(m.group(2) or ""):
                val = next((v for v in a.groups()[1:] if v is not None), None)
                attrs.append((a.group(1), None if val is None else _html.unescape(val)))
            el = OEl(tag, attrs, tok, m.start())
            stack[-1].kids.append(el)
            pos = m.end()
            if tag in VOID:
                el.src = tok
            elif tag in RAWTEXT:
                end = re.compile(rf"</{tag}\s*>", re.I).search(s, pos)
                if not end:
                    raise Miss(f"unclosed <{tag}>")
                if end.start() > pos:
                    el.kids.append(OText(s[pos:end.start()]))
                el.src = s[el.start:end.end()]
                pos = end.end()
            else:
                stack.append(el)
        else:
            tag = m.group(3).lower()
            pos = m.end()
            if not any(e.tag == tag for e in stack[1:]):
                continue  # stray close tag: ignore
            while stack[-1].tag != tag:
                e = stack.pop()
                e.src = s[e.start:m.start()]
            e = stack.pop()
            e.src = s[e.start:m.end()]
    while len(stack) > 1:
        e = stack.pop()
        e.src = s[e.start:]
    return root.kids


def split_content(o):
    """An element's content as (gaps, nodes): gaps[i] is the whitespace/comment text before
    nodes[i], gaps[-1] the text before the closing tag. Nodes are elements and the
    non-blank texts (stripped)."""
    gaps, nodes, cur = [], [], ""
    for k in o.kids:
        if isinstance(k, OComment):
            cur += k.raw
        elif isinstance(k, OText):
            if not k.raw.strip():
                cur += k.raw
            else:
                core = k.raw.strip()
                lead = k.raw[:len(k.raw) - len(k.raw.lstrip())]
                trail = k.raw[len(k.raw.rstrip()):]
                gaps.append(cur + lead)
                nodes.append(OText(core))
                cur = trail
        else:
            gaps.append(cur)
            nodes.append(k)
            cur = ""
    gaps.append(cur)
    return gaps, nodes


def esc_text(v):
    return v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def esc_attr(v):
    return v.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def text_field(raw):
    v = _html.unescape(raw)
    return v if esc_text(v) == raw else {"html": raw}


# ===================================================================== render tree
class E:
    """An element to render. style 'b' = children on their own lines, 'i' = inline."""
    def __init__(self, tag, attrs, kids=(), style="b", kind=None):
        self.tag, self.kind = tag, kind
        self.attrs = [(k, str(v)) for k, v in attrs.items() if v is not None and v is not False]
        self.kids = [k for k in kids if k is not None]
        self.style, self.owner, self.path = style, None, None


class T:
    def __init__(self, value):
        self.raw = value["html"] if isinstance(value, dict) else esc_text(str(value))
        self.owner = self.path = None


class R:
    def __init__(self, raw):
        self.raw = raw
        self.owner = self.path = None


def hints(node):
    d, key = node.owner
    return d.get(key, {}).get(node.path, {})


def set_hint(node, k, v):
    d, key = node.owner
    d.setdefault(key, {}).setdefault(node.path, {})[k] = v


def own(d, nodes, key="_fmt"):
    """Mark the nodes of component d (not those of nested components) with their path."""
    def visit(n, path):
        if n.owner is not None:
            return
        n.owner, n.path = (d, key), path
        for j, k in enumerate(getattr(n, "kids", [])):
            visit(k, f"{path}.{j}")
    for i, n in enumerate(nodes):
        visit(n, str(i))
    return nodes


def attr_order(node):
    names = [k for k, _ in node.attrs]
    order = hints(node).get("o")
    if not order:
        return sorted(names)
    return [n for n in order if n in names] + sorted(n for n in names if n not in order)


def open_tag(node):
    vals = dict(node.attrs)
    bare = hints(node).get("b", [])
    out = "<" + node.tag
    for n in attr_order(node):
        v = vals[n]
        out += f" {n}" if (n in bare and v == "") else f' {n}="{esc_attr(v)}"'
    if node.tag in VOID:
        return out + hints(node).get("v", "/>")
    return out + ">"


def default_pre(container):
    return "\n" if container.style == "b" else ""


def default_end(container):
    return "\n" if container.style == "b" and container.kids else ""


def serialize(node):
    if isinstance(node, (T, R)):
        return node.raw
    out = open_tag(node)
    if node.tag in VOID:
        return out
    for k in node.kids:
        out += hints(k).get("p", default_pre(node)) + serialize(k)
    return out + hints(node).get("e", default_end(node)) + f"</{node.tag}>"


def align(b, o):
    """Check that render node b matches original node o and record the formatting hints."""
    if isinstance(b, R):
        return isinstance(o, OEl) and o.src == b.raw
    if isinstance(b, T):
        return isinstance(o, OText) and o.raw == b.raw
    if not isinstance(o, OEl) or o.tag != b.tag:
        return False
    oa = {n: (v if v is not None else "") for n, v in o.attrs}
    if len(oa) != len(o.attrs) or oa != dict(b.attrs):
        return False
    names = [n for n, _ in o.attrs]
    if names != sorted(names):
        set_hint(b, "o", names)
    bare = [n for n, v in o.attrs if v is None]
    if bare:
        set_hint(b, "b", bare)
    if b.tag in VOID:
        close = re.search(r"\s*/?>$", o.open).group()
        if close != "/>":
            set_hint(b, "v", close)
    if open_tag(b) != o.open:
        return False
    if b.tag in VOID:
        return True
    gaps, nodes = split_content(o)
    if len(nodes) != len(b.kids):
        return False
    for g, k in zip(gaps, b.kids):
        if g != default_pre(b):
            set_hint(k, "p", g)
    if gaps[-1] != default_end(b):
        set_hint(b, "e", gaps[-1])
    return all(align(k, on) for k, on in zip(b.kids, nodes))


def clear_hints(obj):
    if isinstance(obj, dict):
        for k in [k for k in obj if k.startswith("_fmt")]:
            del obj[k]
        for v in obj.values():
            clear_hints(v)
    elif isinstance(obj, list):
        for v in obj:
            clear_hints(v)


# ===================================================================== builders
def cls(base, d, *flags):
    toks = [base] + [c for c, on in flags if on] + list(d.get("classes", []))
    return " ".join(toks)


def root_attrs(d, attrs):
    attrs = dict(attrs)
    attrs.update(d.get("attrs", {}))
    return attrs


def opt(d, key, default):
    return d[key] if key in d else default


def thumb_img(src, size):
    return E("img", {"alt": "", "class": "ltt-thumb", "data-src": src, "decoding": "async",
                     "height": size, "width": size})


class Builder:
    def __init__(self, menu):
        self.menu = menu
        self.icons = dict(DEFAULT_ICONS)
        self.icons.update(menu.get("icons", {}))

    def icon(self, d, key, kind):
        return R(d[key] if d.get(key) else self.icons[kind])

    def raw(self, d):
        return own(d, [R(d["raw"])])

    # ------------------------------------------------------------- desktop
    def brand(self, d):
        if "raw" in d:
            return self.raw(d)
        name = d.get("name", "")
        kids = []
        logo = d.get("logo")
        if d.get("emblem"):
            kids.append(R(d["emblem"]))
        elif logo:
            lg = logo if isinstance(logo, dict) else {"src": logo}
            kids.append(E("img", {"alt": lg.get("alt", f"{name} Logo"), "class": "ltt-brand-logo",
                                  "height": lg.get("height", "36"), "src": lg["src"],
                                  "width": lg.get("width", "36")}))
        kids.append(E("span", {"class": "ltt-brand-text"}, [T(name)], "i"))
        return own(d, [E("a", root_attrs(d, {"aria-label": opt(d, "aria", f"{name} Homepage"),
                                             "class": cls("ltt-brand", d), "href": d.get("href", "/")}), kids)])

    def nav_entry(self, d, i):
        if "raw" in d:
            return self.raw(d)
        if d.get("type", "dropdown" if "columns" in d else "link") == "link":
            act = d.get("active")
            return own(d, [E("a", root_attrs(d, {"aria-current": "page" if act else None,
                                                 "class": cls("ltt-nav-link", d, ("active", act)),
                                                 "href": d["href"]}), [T(d["label"])], "i")])
        return self.dropdown(d, i)

    def dropdown(self, d, i):
        act = d.get("active")
        btn = E("button", {"aria-current": "true" if act else None, "aria-expanded": "false",
                           "aria-haspopup": "true", "class": "ltt-nav-link ltt-dropdown-btn" + (" active" if act else ""),
                           "type": "button"},
                [E("span", {}, [T(d["label"])], "i"), self.icon(d, "chevron", "chevron")], "i", "nav_button")
        cols = [n for c in d.get("columns", []) for n in self.column(c)]
        mega = E("div", {"class": "ltt-mega-menu" + (" is-narrow" if d.get("narrow") else "")
                         + (" is-right" if d.get("right") else ""), "role": "menu"}, cols)
        did = opt(d, "id", "lttExploreDropdown" if i == 0 else f"lttNavDrop{i}")
        return own(d, [E("div", root_attrs(d, {"class": cls("ltt-nav-dropdown", d), "id": did}), [btn, mega])])

    def column(self, d):
        if "raw" in d:
            return self.raw(d)
        kids = [n for g in d.get("groups", []) for n in self.group(g, self.mega_item, "ltt-mega-head")]
        return own(d, [E("div", root_attrs(d, {"class": cls("ltt-mega-col", d)}), kids)])

    def group(self, g, item_fn, head_cls):
        if "raw" in g:
            return self.raw(g)
        nodes = []
        if g.get("head") is not None:
            nodes.append(E("div", {"class": head_cls}, [T(g["head"])], "i"))
        for it in g.get("items", []):
            nodes += item_fn(it)
        if "subitems" in g:
            nodes.append(E("div", g.get("subitems_attrs", {}), [n for s in g["subitems"] for n in self.subitem(s)]))
        return own(g, nodes)

    def mega_item(self, d):
        if "raw" in d:
            return self.raw(d)
        act = d.get("active")
        lead = None
        if d.get("thumb"):
            lead = thumb_img(d["thumb"], d.get("thumb_size", "48"))
        elif d.get("icon"):
            lead = E("span", {"class": "ltt-mega-icon"}, [T(d["icon"])], "i")
        text = [E("strong", {}, [T(d["title"])], "i")]
        if d.get("desc") is not None:
            text.append(E("p", {}, [T(d["desc"])], "i"))
        return own(d, [E("a", root_attrs(d, {"aria-current": "page" if act else None,
                                             "class": cls("ltt-mega-item", d, ("active", act)), "href": d["href"]}),
                         [lead, E("div", {}, text, "i", "mega_item_body")], "i", "mega_item")])

    def subitem(self, d):
        if "raw" in d:
            return self.raw(d)
        act = d.get("active")
        return own(d, [E("a", root_attrs(d, {"aria-current": "page" if act else None,
                                             "class": cls("ltt-mega-subitem", d, ("active", act)), "href": d["href"]}),
                         [T(d["label"])], "i")])

    def search(self, d):
        if d is True:
            d = {}
        if "raw" in d:
            return self.raw(d)
        label = d.get("label", "Search")
        return own(d, [E("button", root_attrs(d, {"aria-label": label, "class": cls("ltt-search-btn", d),
                                                  "data-ltt-search": "", "data-placeholder": d.get("placeholder"),
                                                  "title": opt(d, "title", label), "type": "button"}),
                         [self.icon(d, "icon", "search")], "i")])

    def lang_switcher(self, d, langs):
        if "raw" in d:
            return self.raw(d)
        cur = next((x for x in langs if x.get("current")), None)
        code = opt(d, "code", (cur or {}).get("code") or (cur or {}).get("lang", self.menu.get("lang", "en")).upper())
        btn = E("button", {"aria-expanded": "false", "aria-haspopup": "true",
                           "aria-label": opt(d, "button_label", "Select Language"), "class": "ltt-lang-btn",
                           "id": "lttLangBtn", "onclick": "window.lttToggleLangDropdown()", "type": "button"},
                [self.icon(d, "globe", "globe"),
                 E("span", {"class": "ltt-lang-code", "id": "lttActiveLangLabel"}, [T(code)], "i"),
                 self.icon(d, "chevron", "lang_chevron")])
        head = E("div", {"class": "ltt-lang-dropdown-header"}, [
            E("span", {}, [T(d.get("heading", "Select Language"))], "i"),
            E("span", {"style": opt(d, "count_style", COUNT_STYLE)},
              [T(d.get("count", f"● {len(langs)} AVAILABLE"))], "i")])
        grid = E("div", {"class": "ltt-lang-grid-menu"}, [n for x in langs for n in self.lang_item(x)])
        dd = E("div", {"aria-label": opt(d, "menu_label", "Select Language"), "class": "ltt-lang-dropdown",
                       "id": "lttLangDropdown", "role": "menu"}, [head, grid])
        return own(d, [E("div", root_attrs(d, {"class": cls("ltt-lang-trigger", d), "id": "lttLangTrigger"}),
                         [btn, dd])])

    def lang_item(self, d):
        if "raw" in d:
            return self.raw(d)
        return own(d, [E("a", root_attrs(d, {"class": cls("ltt-lang-item", d, ("current", d.get("current"))),
                                             "data-lang": d["lang"], "href": d["href"], "role": "menuitem"}),
                         [E("span", {"class": "lang-native"}, [T(d["name"])], "i"),
                          E("span", {"class": "lang-code-tag"}, [T(d.get("code", d["lang"].upper()))], "i")])])

    def hamburger(self, d):
        if "raw" in d:
            return self.raw(d)
        bars = [E("span", {"class": "ltt-hamburger-bar"}, [], "i") for _ in range(3)]
        return own(d, [E("button", root_attrs(d, {"aria-controls": "lttMobileDrawer", "aria-expanded": "false",
                                                  "aria-label": d.get("label", "Toggle Menu"),
                                                  "class": cls("ltt-hamburger", d), "id": "lttNavToggle",
                                                  "type": "button"}), bars)])

    # ------------------------------------------------------------- mobile
    def drawer_section(self, d, langs):
        if "raw" in d:
            return self.raw(d)
        t = d.get("type", "section")
        if t == "languages":
            return self.lang_box(d, langs)
        kids = [n for g in d.get("groups", []) for n in self.group(g, self.mobile_link, "ltt-mobile-label")]
        if t == "accordion":
            summ = E("summary", {"class": "ltt-mobile-acc-sum"},
                     [E("span", {}, [T(d["label"])], "i"), self.icon(d, "chevron", "chevron")], "i", "summary")
            body = E("div", {"class": "ltt-mobile-acc-body"}, kids)
            return own(d, [E("details", root_attrs(d, {"class": cls("ltt-mobile-acc", d)}), [summ, body])])
        return own(d, [E("div", root_attrs(d, {"class": cls("ltt-mobile-section", d)}), kids)])

    def mobile_link(self, d):
        if "raw" in d:
            return self.raw(d)
        act = d.get("active")
        attrs = root_attrs(d, {"aria-current": "page" if act else None,
                               "class": cls("ltt-mobile-link", d, ("active", act)), "href": d["href"]})
        tag = None
        if d.get("tag") is not None:
            tag = E("span", d.get("tag_attrs", {"class": "ltt-mobile-tag"}), [T(d["tag"])], "i")
        if d.get("thumb"):
            main = E("span", {"class": "ltt-mobile-link-main"},
                     [thumb_img(d["thumb"], d.get("thumb_size", "36")), E("span", {}, [T(d["title"])], "i")], "i")
            return own(d, [E("a", attrs, [main, tag], "i", "mobile_link_thumb")])
        return own(d, [E("a", attrs, [E("span", {}, [T(d["title"])], "i"), tag], "b", "mobile_link")])

    def lang_box(self, d, langs):
        title = E("div", {"class": "ltt-mobile-lang-title"},
                  [self.icon(d, "globe", "mobile_globe"), E("span", {}, [T(d.get("label", "Language"))], "i")])
        if "chips" in d:
            chips = [n for c in d["chips"] for n in self.chip(c, c)]
        else:
            chips = [n for x in langs for n in self.chip(x, x, "_fmt_chip")]
        box = E("div", root_attrs(d, {"class": cls("ltt-mobile-lang-box", d)}),
                [title, E("div", {"class": "ltt-mobile-lang-chips"}, chips)])
        return own(d, [box])

    def chip(self, d, owner, key="_fmt"):
        if "raw" in d:
            return own(owner, [R(d["raw"])], key)
        return own(owner, [E("a", {"class": "ltt-mobile-lang-chip" + (" current" if d.get("current") else ""),
                                   "data-m-lang": d["lang"], "href": d["href"]},
                             [E("span", {"class": "chip-code"}, [T(d.get("code", d["lang"].upper()))], "i"),
                              E("span", {"class": "chip-name"}, [T(d["name"])], "i")])], key)

    # ------------------------------------------------------------- header
    def header(self):
        m = self.menu
        langs = m.get("languages", [])
        brand = self.brand(m.get("brand", {}))
        nav = E("nav", {"aria-label": m.get("nav_label", "Primary Navigation"), "class": "ltt-nav-links"},
                [n for i, x in enumerate(m.get("nav", [])) for n in self.nav_entry(x, i)])
        right = []
        if m.get("search", True):
            right += self.search(m.get("search", True))
        if langs and m.get("lang_switcher", {}) is not False:
            right += self.lang_switcher(m.get("lang_switcher", {}), langs)
        right += self.hamburger(m.get("hamburger", {}))
        inner = E("div", {"class": "ltt-nav-inner"}, brand + [E("div", {"class": "ltt-nav-right"}, right)])
        inner.kids.insert(1, nav)
        drawer_data = m["drawer"] if "drawer" in m else derive_drawer(m)
        sections = [n for x in drawer_data for n in self.drawer_section(x, langs)]
        drawer = E("div", {"aria-hidden": "true", "class": "ltt-mobile-drawer", "id": "lttMobileDrawer", "inert": ""},
                   [E("div", {"class": "ltt-drawer-content"}, sections)])
        after = [n for x in m.get("after", []) for n in self.raw(x)]
        hdr = E("header", root_attrs(m, {"class": cls("ltt-navbar", m), "role": "banner"}), [inner, drawer] + after)
        own(m, [hdr])
        layout = m.get("layout", {})
        if layout:
            for n in walk(hdr):
                if getattr(n, "kind", None) in layout:
                    n.style = layout[n.kind]
        return hdr


def walk(node):
    yield node
    for k in getattr(node, "kids", []):
        yield from walk(k)


LAYOUT_KINDS = ("nav_button", "mega_item", "mega_item_body", "summary", "mobile_link", "mobile_link_thumb")


def derive_drawer(menu):
    """The standard mobile drawer for a menu without one: an accordion per dropdown, the
    plain links in one section, then the language chips."""
    out, links = [], []
    for x in menu.get("nav", []):
        if "raw" in x:
            continue
        if x.get("type", "dropdown" if "columns" in x else "link") == "link":
            links.append({"href": x["href"], "title": x["label"]})
            continue
        groups = []
        for c in x.get("columns", []):
            for g in c.get("groups", []):
                items = [{"href": it["href"], "title": it["title"], **({"thumb": it["thumb"]} if it.get("thumb") else {})}
                         for it in g.get("items", []) if "raw" not in it]
                items += [{"href": s["href"], "title": s["label"]} for s in g.get("subitems", []) if "raw" not in s]
                groups.append({"head": g.get("head"), "items": items})
        out.append({"type": "accordion", "label": x["label"], "groups": groups})
    if links:
        out.append({"type": "section", "groups": [{"items": links}]})
    if menu.get("languages"):
        out.append({"type": "languages"})
    return out


def render_header(menu):
    """The <header class="ltt-navbar">...</header> HTML for a menu dict (see the module doc)."""
    return serialize(Builder(menu).header())


# ===================================================================== extract
def els(o):
    return split_content(o)[1]


def classes(o):
    return (dict(o.attrs).get("class") or "").split()


def has_class(o, c):
    return isinstance(o, OEl) and c in classes(o)


def text_of(o):
    nodes = els(o)
    if not nodes:
        return ""
    if len(nodes) != 1 or not isinstance(nodes[0], OText):
        raise Miss(f"<{o.tag}> holds markup")
    return text_field(nodes[0].raw)


class Root:
    """Reads a component's root element: known attributes and classes are taken, the rest
    is kept in "attrs"/"classes"."""
    def __init__(self, o, tag, base):
        if not isinstance(o, OEl) or o.tag != tag or base not in classes(o):
            raise Miss(f"expected <{tag} class={base}>")
        self.o, self.attrs = o, dict((n, v if v is not None else "") for n, v in o.attrs)
        self.cls = classes(o)
        self.cls.remove(base)
        self.attrs.pop("class", None)

    def get(self, name, default=None):
        return self.attrs.pop(name, default)

    def flag(self, c):
        if c in self.cls:
            self.cls.remove(c)
            return True
        return False

    def active(self, d, current="page"):
        if self.flag("active"):
            d["active"] = True
            if self.attrs.get("aria-current") == current:
                del self.attrs["aria-current"]
            elif "aria-current" not in self.attrs:
                self.attrs["aria-current"] = None  # active without aria-current

    def expect(self, **fixed):
        """Take attributes that always have these values (they are not stored)."""
        for k, v in fixed.items():
            k = k.replace("_", "-")
            if self.attrs.get(k) == v:
                del self.attrs[k]

    def finish(self, d):
        if self.cls:
            d["classes"] = self.cls
        if self.attrs:
            d["attrs"] = self.attrs
        return d


class Extractor:
    def __init__(self):
        self.icon_slots = []  # (dict, key, kind)

    def checked(self, fn, o, *args):
        """fn(o) -> dict; keep it only if it renders back to exactly o, else {"raw": html}."""
        try:
            d = fn(o, *args)
            b = Builder({})
            nodes = self.render_one(b, fn, d, args)
            if len(nodes) == 1 and align(nodes[0], o):
                return d
        except Miss:
            pass
        return {"raw": o.src}

    def render_one(self, b, fn, d, args):
        name = fn.__name__
        if name == "dropdown":
            return b.dropdown(d, args[0])
        if name == "nav_link":
            return b.nav_entry(d, 0)
        if name == "drawer_section":
            return b.drawer_section(d, args[0])
        if name == "chip":
            return b.chip(d, d)
        return getattr(b, name)(d)

    def icon(self, d, key, kind, o):
        if not isinstance(o, OEl) or o.tag != "svg":
            raise Miss("expected <svg>")
        d[key] = o.src
        self.icon_slots.append((d, key, kind))

    # ------------------------------------------------------------- desktop
    def brand(self, o):
        r = Root(o, "a", "ltt-brand")
        nodes = els(o)
        if not nodes or not has_class(nodes[-1], "ltt-brand-text"):
            raise Miss("brand text")
        d = {"name": text_of(nodes[-1]), "href": r.get("href", "/")}
        name = d["name"] if isinstance(d["name"], str) else ""
        aria = r.get("aria-label")
        if aria != f"{name} Homepage":
            d["aria"] = aria
        for n in nodes[:-1]:
            if has_class(n, "ltt-brand-logo") and n.tag == "img":
                a = dict(n.attrs)
                lg = {"src": a.get("src"), "alt": a.get("alt"), "width": a.get("width"), "height": a.get("height")}
                d["logo"] = lg["src"] if (lg["alt"] == f"{name} Logo" and lg["width"] == lg["height"] == "36") else lg
            elif has_class(n, "ltt-brand-emblem"):
                d["emblem"] = n.src
            else:
                raise Miss("brand content")
        if len(nodes) > 2:
            raise Miss("brand content")
        return r.finish(d)

    def nav_link(self, o):
        r = Root(o, "a", "ltt-nav-link")
        d = {"type": "link", "label": text_of(o), "href": r.get("href")}
        r.active(d)
        return r.finish(d)

    def dropdown(self, o, i):
        r = Root(o, "div", "ltt-nav-dropdown")
        nodes = els(o)
        if len(nodes) != 2:
            raise Miss("dropdown")
        btn, mega = nodes
        bn = els(btn)
        if not has_class(btn, "ltt-dropdown-btn") or len(bn) != 2 or bn[0].tag != "span":
            raise Miss("dropdown button")
        d = {"type": "dropdown", "label": text_of(bn[0])}
        did = r.get("id")
        if did != ("lttExploreDropdown" if i == 0 else f"lttNavDrop{i}"):
            d["id"] = did
        if "active" in classes(btn):
            d["active"] = True
        self.icon(d, "chevron", "chevron", bn[1])
        mc = classes(mega)
        if not has_class(mega, "ltt-mega-menu"):
            raise Miss("mega menu")
        if "is-narrow" in mc:
            d["narrow"] = True
        if "is-right" in mc:
            d["right"] = True
        d["columns"] = [self.checked(self.column, c) for c in els(mega)]
        return r.finish(d)

    def groups(self, nodes, head_cls, item_fn):
        groups, g = [], None
        for n in nodes:
            if has_class(n, head_cls) and n.tag == "div":
                g = {"head": text_of(n), "items": []}
                groups.append(g)
                continue
            if g is None:
                g = {"items": []}
                groups.append(g)
            if isinstance(n, OEl) and n.tag == "div" and not n.attrs and els(n) and \
                    all(has_class(k, "ltt-mega-subitem") for k in els(n)):
                g["subitems"] = [self.checked(self.subitem, k) for k in els(n)]
                g = None  # a subitem block ends the group
                continue
            g["items"].append(self.checked(item_fn, n))
        for g in groups:
            if not g["items"] and "subitems" in g:
                del g["items"]
        return groups

    def column(self, o):
        r = Root(o, "div", "ltt-mega-col")
        return r.finish({"groups": self.groups(els(o), "ltt-mega-head", self.mega_item)})

    def mega_item(self, o):
        r = Root(o, "a", "ltt-mega-item")
        d = {"href": r.get("href")}
        r.active(d)
        nodes = els(o)
        if len(nodes) == 2:
            lead = nodes.pop(0)
            if lead.tag == "img" and has_class(lead, "ltt-thumb"):
                a = dict(lead.attrs)
                d["thumb"] = a.get("data-src")
                if a.get("width") != "48":
                    d["thumb_size"] = a.get("width")
            elif lead.tag == "span" and has_class(lead, "ltt-mega-icon"):
                d["icon"] = text_of(lead)
            else:
                raise Miss("item lead")
        if len(nodes) != 1 or nodes[0].tag != "div":
            raise Miss("item body")
        body = els(nodes[0])
        if not body or body[0].tag != "strong":
            raise Miss("item title")
        d["title"] = text_of(body[0])
        if len(body) == 2 and body[1].tag == "p":
            d["desc"] = text_of(body[1])
        elif len(body) != 1:
            raise Miss("item body")
        return r.finish(d)

    def subitem(self, o):
        r = Root(o, "a", "ltt-mega-subitem")
        d = {"href": r.get("href"), "label": text_of(o)}
        r.active(d)
        return r.finish(d)

    def search(self, o):
        r = Root(o, "button", "ltt-search-btn")
        d = {"label": r.get("aria-label")}
        t = r.get("title")
        if t != d["label"]:
            d["title"] = t
        r.expect(data_ltt_search="", type="button")
        ph = r.get("data-placeholder")
        if ph is not None:
            d["placeholder"] = ph
        nodes = els(o)
        if len(nodes) != 1:
            raise Miss("search icon")
        self.icon(d, "icon", "search", nodes[0])
        return r.finish(d)

    def lang_switcher(self, o, menu):
        r = Root(o, "div", "ltt-lang-trigger")
        r.expect(id="lttLangTrigger")
        nodes = els(o)
        if len(nodes) != 2:
            raise Miss("lang switcher")
        btn, dd = nodes
        bn = els(btn)
        if len(bn) != 3:
            raise Miss("lang button")
        d = {}
        ba = dict(btn.attrs)
        d["button_label"] = ba.get("aria-label")
        self.icon(d, "globe", "globe", bn[0])
        self.icon(d, "chevron", "lang_chevron", bn[2])
        d["code"] = text_of(bn[1])
        da = dict(dd.attrs)
        d["menu_label"] = da.get("aria-label")
        dn = els(dd)
        if len(dn) != 2:
            raise Miss("lang dropdown")
        hn = els(dn[0])
        if len(hn) != 2:
            raise Miss("lang heading")
        d["heading"] = text_of(hn[0])
        d["count"] = text_of(hn[1])
        st = dict(hn[1].attrs).get("style")
        if st != COUNT_STYLE:
            d["count_style"] = st
        menu["languages"] = [self.checked(self.lang_item, x) for x in els(dn[1])]
        cur = next((x for x in menu["languages"] if x.get("current")), None)
        if cur and d["code"] == cur.get("code", cur["lang"].upper()):
            del d["code"]
        return r.finish(d)

    def lang_item(self, o):
        r = Root(o, "a", "ltt-lang-item")
        d = {"lang": r.get("data-lang"), "href": r.get("href")}
        if r.flag("current"):
            d["current"] = True
        r.expect(role="menuitem")
        nodes = els(o)
        if len(nodes) != 2:
            raise Miss("lang item")
        d["name"] = text_of(nodes[0])
        code = text_of(nodes[1])
        if code != (d["lang"] or "").upper():
            d["code"] = code
        return r.finish(d)

    def hamburger(self, o):
        r = Root(o, "button", "ltt-hamburger")
        r.expect(aria_controls="lttMobileDrawer", aria_expanded="false", id="lttNavToggle", type="button")
        return r.finish({"label": r.get("aria-label")})

    # ------------------------------------------------------------- mobile
    def drawer_section(self, o, langs):
        if has_class(o, "ltt-mobile-acc"):
            r = Root(o, "details", "ltt-mobile-acc")
            nodes = els(o)
            if len(nodes) != 2 or nodes[0].tag != "summary" or not has_class(nodes[1], "ltt-mobile-acc-body"):
                raise Miss("accordion")
            sn = els(nodes[0])
            if len(sn) != 2 or sn[0].tag != "span":
                raise Miss("accordion summary")
            d = {"type": "accordion", "label": text_of(sn[0])}
            self.icon(d, "chevron", "chevron", sn[1])
            d["groups"] = self.groups(els(nodes[1]), "ltt-mobile-label", self.mobile_link)
            return r.finish(d)
        if has_class(o, "ltt-mobile-lang-box"):
            r = Root(o, "div", "ltt-mobile-lang-box")
            nodes = els(o)
            if len(nodes) != 2:
                raise Miss("lang box")
            tn = els(nodes[0])
            if len(tn) != 2:
                raise Miss("lang box title")
            d = {"type": "languages", "label": text_of(tn[1])}
            self.icon(d, "globe", "mobile_globe", tn[0])
            chips = [self.checked(self.chip, c) for c in els(nodes[1])]
            derived = [{k: x[k] for k in ("lang", "href", "name", "code", "current") if k in x}
                       for x in langs if "raw" not in x]
            if chips != derived:
                d["chips"] = chips
            return r.finish(d)
        r = Root(o, "div", "ltt-mobile-section")
        return r.finish({"type": "section", "groups": self.groups(els(o), "ltt-mobile-label", self.mobile_link)})

    def mobile_link(self, o):
        r = Root(o, "a", "ltt-mobile-link")
        d = {"href": r.get("href")}
        r.active(d)
        nodes = els(o)
        if not nodes or len(nodes) > 2:
            raise Miss("mobile link")
        main = nodes[0]
        if has_class(main, "ltt-mobile-link-main"):
            mn = els(main)
            if len(mn) != 2 or mn[0].tag != "img" or mn[1].tag != "span":
                raise Miss("mobile link main")
            a = dict(mn[0].attrs)
            d["thumb"] = a.get("data-src")
            if a.get("width") != "36":
                d["thumb_size"] = a.get("width")
            d["title"] = text_of(mn[1])
        elif isinstance(main, OEl) and main.tag == "span" and not main.attrs:
            d["title"] = text_of(main)
        else:
            raise Miss("mobile link content")
        if len(nodes) == 2:
            tag = nodes[1]
            if not isinstance(tag, OEl) or tag.tag != "span":
                raise Miss("mobile tag")
            d["tag"] = text_of(tag)
            ta = dict((n, v if v is not None else "") for n, v in tag.attrs)
            if ta != {"class": "ltt-mobile-tag"}:
                d["tag_attrs"] = ta
        return r.finish(d)

    def chip(self, o):
        r = Root(o, "a", "ltt-mobile-lang-chip")
        d = {"lang": r.get("data-m-lang"), "href": r.get("href")}
        nodes = els(o)
        if len(nodes) != 2:
            raise Miss("chip")
        code, name = text_of(nodes[0]), text_of(nodes[1])
        d["name"] = name
        if code != (d["lang"] or "").upper():
            d["code"] = code
        if r.flag("current"):
            d["current"] = True
        return r.finish(d)

    # ------------------------------------------------------------- header
    def header(self, src):
        top = [n for n in parse(src) if isinstance(n, OEl)]
        if len(top) != 1:
            raise Miss("expected one <header>")
        o = top[0]
        r = Root(o, "header", "ltt-navbar")
        r.expect(role="banner")
        m = {}
        nodes = els(o)
        if not nodes or not has_class(nodes[0], "ltt-nav-inner"):
            raise Miss("nav inner")
        inner = els(nodes[0])
        if len(inner) != 3 or inner[1].tag != "nav" or not has_class(inner[2], "ltt-nav-right"):
            raise Miss("nav inner content")
        m["brand"] = self.checked(self.brand, inner[0])
        m["nav_label"] = dict(inner[1].attrs).get("aria-label")
        nav = []
        for i, n in enumerate(els(inner[1])):
            if has_class(n, "ltt-nav-dropdown"):
                nav.append(self.checked(self.dropdown, n, i))
            elif has_class(n, "ltt-nav-link"):
                nav.append(self.checked(self.nav_link, n))
            else:
                nav.append({"raw": n.src})
        m["nav"] = nav
        right = els(inner[2])
        m["search"] = False
        if right and has_class(right[0], "ltt-search-btn"):
            m["search"] = self.checked(self.search, right.pop(0))
        if right and has_class(right[0], "ltt-lang-trigger"):
            m["lang_switcher"] = self.lang_switcher(right.pop(0), m)
        if len(right) != 1 or not has_class(right[0], "ltt-hamburger"):
            raise Miss("hamburger")
        m["hamburger"] = self.checked(self.hamburger, right[0])
        rest = nodes[1:]
        if rest and has_class(rest[0], "ltt-mobile-drawer"):
            dn = els(rest.pop(0))
            if len(dn) != 1 or not has_class(dn[0], "ltt-drawer-content"):
                raise Miss("drawer content")
            langs = m.get("languages", [])
            m["drawer"] = [self.checked(self.drawer_section, s, langs) for s in els(dn[0])]
        else:
            m["drawer"] = []
        m["after"] = [{"raw": n.src} for n in rest]
        if not m["after"]:
            del m["after"]
        r.finish(m)
        self.settle_icons(m)
        return m, o

    def settle_icons(self, m):
        """Icons equal to the standard (or to the menu's own "icons") are left out."""
        by_kind = {}
        for d, key, kind in self.icon_slots:
            if key in d:
                by_kind.setdefault(kind, []).append(d[key])
        icons = {}
        for kind, vals in by_kind.items():
            common = Counter(vals).most_common(1)[0][0]
            if common != DEFAULT_ICONS[kind]:
                icons[kind] = common
        if icons:
            m["icons"] = icons
        eff = dict(DEFAULT_ICONS, **icons)
        for d, key, kind in self.icon_slots:
            if d.get(key) == eff[kind]:
                del d[key]


ORDER = ["lang", "master", "brand", "nav_label", "nav", "search", "languages", "lang_switcher", "hamburger",
         "drawer", "after", "icons", "layout", "attrs", "classes", "_fmt"]


def extract_header(src, lang=None):
    """The menu dict of a header's HTML. Raises Miss when it cannot be reproduced exactly."""
    m, o = Extractor().header(src)

    def fit():
        clear_hints(m)
        hdr = Builder(m).header()
        return align(hdr, o) and serialize(hdr) == src

    if not fit():
        raise Miss("header does not round-trip")
    # a site that writes some parts on several lines (or inline) gets one "layout" switch
    # for that kind of element instead of the same hints on every item
    best = hint_size(m)
    for kind in LAYOUT_KINDS:
        layout = dict(m.get("layout", {}))
        before = layout.get(kind)
        layout[kind] = "i" if (before or DEFAULT_STYLE[kind]) == "b" else "b"
        m["layout"] = layout
        if fit() and hint_size(m) < best:
            best = hint_size(m)
            continue
        if before is None:
            del layout[kind]
        else:
            layout[kind] = before
        if not layout:
            del m["layout"]
    if not fit():
        raise Miss("header does not round-trip")
    if lang:
        m["lang"] = lang
    return {k: m[k] for k in sorted(m, key=lambda k: ORDER.index(k) if k in ORDER else 99)}


DEFAULT_STYLE = {"nav_button": "i", "mega_item": "i", "mega_item_body": "i", "summary": "i",
                 "mobile_link": "b", "mobile_link_thumb": "i"}


def hint_size(obj):
    if isinstance(obj, dict):
        return sum(len(json.dumps(v)) if k.startswith("_fmt") else hint_size(v) for k, v in obj.items())
    if isinstance(obj, list):
        return sum(hint_size(v) for v in obj)
    return 0


def raw_count(obj):
    """How many parts of a menu dict are kept as raw HTML (0 = fully structured)."""
    if isinstance(obj, dict):
        return (1 if "raw" in obj else 0) + sum(raw_count(v) for k, v in obj.items() if k != "after")
    if isinstance(obj, list):
        return sum(raw_count(v) for v in obj)
    return 0


def dump_menu(menu):
    """The menu as JSON text: indented, with each "_fmt" hint block on one line."""
    blocks = []

    def pull(obj):
        if isinstance(obj, dict):
            out = {}
            for k, v in obj.items():
                if k.startswith("_fmt"):
                    blocks.append(json.dumps(v, ensure_ascii=False, sort_keys=True))
                    out[k] = f"\u0000fmt{len(blocks) - 1}\u0000"
                else:
                    out[k] = pull(v)
            return out
        if isinstance(obj, list):
            return [pull(v) for v in obj]
        return obj
    text = json.dumps(pull(menu), ensure_ascii=False, indent=2)
    text = re.sub(r'"\\u0000fmt(\d+)\\u0000"', lambda m: blocks[int(m.group(1))], text)
    return text + "\n"


# ===================================================================== CLI
def site():
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checks"))
    from sitecfg import ROOT  # noqa: E402
    with open(os.path.join(ROOT, "scripts", "layout_config.json"), encoding="utf-8") as fh:
        cfg = json.load(fh)
    return ROOT, cfg["masters"]


def menu_path(root, lang):
    return os.path.join(root, "data", "menu", f"{lang}.json")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["extract", "build"])
    ap.add_argument("--lang", action="append", help="only this language (repeatable)")
    ap.add_argument("--check", action="store_true", help="build: report masters that differ, write nothing")
    a = ap.parse_args()
    root, masters = site()
    langs = a.lang or list(masters)
    bad = 0
    for lg in langs:
        if lg not in masters:
            print(f"ERROR {lg}: no master in scripts/layout_config.json")
            bad += 1
            continue
        page = os.path.join(root, masters[lg])
        with open(page, encoding="utf-8") as fh:
            s = fh.read()
        m = PAT_HEADER.search(s)
        if not m:
            print(f"ERROR {masters[lg]}: no <header class=\"ltt-navbar\">")
            bad += 1
            continue
        if a.cmd == "extract":
            try:
                menu = extract_header(m.group(), lg)
            except Miss as e:
                print(f"ERROR {masters[lg]}: {e}")
                bad += 1
                continue
            menu = {"lang": lg, "master": masters[lg], **{k: v for k, v in menu.items() if k != "lang"}}
            out = menu_path(root, lg)
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8") as fh:
                fh.write(dump_menu(menu))
            n = raw_count(menu)
            print(f"extracted: data/menu/{lg}.json" + (f" ({n} part(s) kept as raw HTML)" if n else ""))
        else:
            try:
                with open(menu_path(root, lg), encoding="utf-8") as fh:
                    menu = json.load(fh)
            except FileNotFoundError:
                print(f"ERROR data/menu/{lg}.json missing (run: python3 scripts/menu.py extract --lang {lg})")
                bad += 1
                continue
            new = s[:m.start()] + render_header(menu) + s[m.end():]
            if new == s:
                continue
            if a.check:
                print(f"out of date: {masters[lg]} (run: python3 scripts/menu.py build --lang {lg})")
                bad += 1
            else:
                with open(page, "w", encoding="utf-8") as fh:
                    fh.write(new)
                print(f"built: {masters[lg]}")
    if bad:
        sys.exit(1)


if __name__ == "__main__":
    main()
