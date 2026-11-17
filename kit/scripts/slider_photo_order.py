"""Order card slider photos so each sequence sells the card's promise.

Shared kit script. The orders themselves are site data: scripts/slider_photo_order_data.py
in each site defines PHOTO_ORDER (page -> card number (1-based slider index on the page) ->
photos in the wanted order, as 1-based indexes into the card's current photo list or as
photo ids). Photos not listed are dropped. The same order is applied to every language
version of the page (found through its hreflang links); image files are shared, only alt
text differs.

First photo = the single strongest shot for the card's promise, then the story
(venue/boat, food/drinks, views, details). Off-topic shots (menus, payment graphics, text
boards, near-duplicates) are dropped. Orders are picked by looking at contact sheets of
every card, not by filename.

site.json "photo_order": {"slot": "rebuild"} switches to the rebuild slot convention
(see fill_slot below); the default keeps each slot's tag and swaps the photo.

Usage: python3 scripts/slider_photo_order.py [--check]
"""
import html
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import quote, unquote

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checks"))
from sitecfg import ROOT as _ROOT, SITE  # noqa: E402

ROOT = Path(_ROOT)
DOMAIN = SITE.get("domain", "").rstrip("/")


def load_orders():
    p = ROOT / "scripts" / "slider_photo_order_data.py"
    if not p.exists():
        return {}
    ns = {}
    exec(compile(p.read_text(encoding="utf-8"), str(p), "exec"), ns)
    return ns.get("PHOTO_ORDER", {})


PHOTO_ORDER = load_orders()


SLIDER_RE = re.compile(r'<div[^>]*class="bpa-slider"')
IMG_RE = re.compile(r"<img [^>]*>")
LD_LOG = []
PILL_RE = re.compile(r'(<span class="bpa-pill">1 / )(\d+)(</span>)')


def balanced_end(h, start):
    depth = 0
    for m in re.finditer(r"<(/?)div\b[^>]*>", h[start:]):
        depth += -1 if m.group(1) else 1
        if depth == 0:
            return start + m.end()
    raise ValueError("unbalanced div")


def img_url(im):
    m = re.search(r'data-src="([^"]+)"', im) or re.search(r' src="([^"]+)"', im)
    return m.group(1)


def attr(im, name):
    m = re.search(r'\s%s="[^"]*"' % name, im)
    return m.group(0) if m else None


def fill_slot_in_place(template, im):
    """Put photo `im` into the slot `template` (keeps the slot's loading attrs)."""
    out = template
    out = re.sub(r'\salt="[^"]*"', lambda _: attr(im, "alt") or ' alt=""', out, count=1)
    u = img_url(im)
    if 'data-src="' in out:
        out = re.sub(r'data-src="[^"]*"', lambda _: 'data-src="%s"' % u, out, count=1)
    else:
        out = re.sub(r' src="[^"]*"', lambda _: ' src="%s"' % u, out, count=1)
    # responsive variants travel with the photo
    ss = re.search(r'\s(?:data-)?srcset="([^"]*)"', im)
    if ss:
        out = re.sub(r'(\s(?:data-)?srcset=")[^"]*"', lambda m: m.group(1) + ss.group(1) + '"', out, count=1)
    else:
        out = re.sub(r'\s(?:data-)?srcset="[^"]*"', "", out, count=1)
    oe_t, oe_i = attr(out, "onerror"), attr(im, "onerror")
    if oe_t and oe_i:
        out = out.replace(oe_t, oe_i, 1)
    return out


def fill_slot_rebuild(template, im):
    """Put photo `im` into the slot `template`.

    Everything that describes the photo (alt, data-cap, srcset, sizes, size)
    stays with the photo. Only the loading mode comes from the slot: the
    first slot loads eagerly with src/srcset, the others lazily with
    data-src/data-srcset behind the slot's placeholder.
    """
    url = img_url(im)
    ss = re.search(r'\s(?:data-)?srcset="([^"]*)"', im)
    ss = ss.group(1) if ss else None
    body = im[len("<img"):].rstrip("/>").rstrip()
    for name in ("src", "data-src", "srcset", "data-srcset", "loading", "fetchpriority", "decoding"):
        body = re.sub(r'\s%s="[^"]*"' % name, "", body)
    slot = "".join(attr(template, n) or "" for n in ("loading", "fetchpriority", "decoding"))
    if 'data-src="' in template:
        ph = re.search(r' src="([^"]*)"', template).group(1)
        media = ' data-src="%s"' % url + (' data-srcset="%s"' % ss if ss else "") + ' src="%s"' % ph
    else:
        media = ' src="%s"' % url + (' srcset="%s"' % ss if ss else "")
    return "<img" + body + slot + media + "/>"



# Two slot conventions exist. "in_place" (default): keep the slot's tag and swap the photo
# (alt, src or data-src, srcset, onerror). "rebuild": rebuild the tag from the photo, keeping
# only the slot's loading mode (site.json "photo_order": {"slot": "rebuild"}, Cruise Detective).
fill_slot = fill_slot_rebuild if SITE.get("photo_order", {}).get("slot") == "rebuild" else fill_slot_in_place

def norm(u):
    """Compare slider URLs (&amp;, spaces) with JSON-LD URLs (%26, %20)."""
    return unquote(html.unescape(u)).lstrip("/")


def ld_url(u, like):
    return ("/" if like.startswith("/") else "") + quote(norm(u), safe="/:()")


def page_file(path):
    for c in (path + ".html", path + "/index.html",
              unicodedata.normalize("NFD", path) + ".html",
              unicodedata.normalize("NFD", path) + "/index.html"):
        if (ROOT / c).exists():
            return ROOT / c
    return None


def cluster_files(page):
    """[(lang, file)] for the page and every language version its hreflang links name."""
    main = page_file(page)
    if not main:
        return []
    h = main.read_text()
    files = []
    if DOMAIN:
        for path, lang in re.findall(
                r'<link href="%s/([^"]*)" hreflang="([^"]+)" rel="alternate"' % re.escape(DOMAIN), h):
            if lang == "x-default":
                continue
            f = page_file(unquote(path))
            if f and (lang, f) not in files:
                files.append((lang, f))
    return files or [("en", main)]


def photo_key(u):
    """Webflow asset hash when there is one, else the file name."""
    b = norm(u).split("/")[-1]
    m = re.match(r"([0-9a-f]{24})_", b)
    return m.group(1) if m else b


class MissingPhoto(Exception):
    pass


def reorder_page(h, orders):
    sliders = []
    for m in SLIDER_RE.finditer(h):
        sliders.append((m.start(), balanced_end(h, m.start())))
    urls = [[img_url(i) for i in IMG_RE.findall(h[a:b])] for a, b in sliders]
    first_swaps = []
    card_lists = {}
    for idx in sorted(orders, reverse=True):
        order = orders[idx]
        a, b = sliders[idx - 1]
        s = h[a:b]
        imgs = IMG_RE.findall(s)
        by_key = {photo_key(img_url(i)): i for i in imgs}
        new = []
        for k in order:
            if k in by_key:
                new.append(by_key[k])
            elif k.startswith("/assets/") and (ROOT / k.lstrip("/")).exists():
                # a photo added to the card: same alt as the card's other photos
                new.append('<img%s src="%s"/>' % (attr(imgs[0], "alt") or ' alt=""', k))
            else:
                raise MissingPhoto((idx, k))
        card_lists[idx] = ([img_url(i) for i in imgs], [img_url(i) for i in new])
        rest_t = imgs[1] if len(imgs) > 1 else imgs[0]
        tags = [fill_slot(imgs[0], new[0])] + [fill_slot(rest_t, im) for im in new[1:]]
        head = s[:s.find("<img ")]
        tail = s[s.rfind(">", 0, s.rfind("</div>")) + 1:]
        # keep the separator used between tags
        sep = "\n" if "\n<img " in s else ""
        new_s = head + sep.join(tags) + tail
        media = [m.start() for m in re.finditer(r'<div class="bpa-media[" ]', h[max(0, a - 3000):a])]
        pre_start = max(0, a - 3000) + media[-1] if media else a
        pre = h[pre_start:a]
        pre_new, n = PILL_RE.subn(lambda m: m.group(1) + str(len(order)) + m.group(3), pre)
        assert n <= 1
        # the visible caption under the counter starts as the first photo's data-cap
        cap = attr(tags[0], "data-cap")
        cap = cap.split('"')[1] if cap else ""
        pre_new = re.sub(r'(<span class="bpa-cap"[^>]*>)[^<]*(</span>)', lambda m: m.group(1) + cap + m.group(2), pre_new, count=1)
        h = h[:pre_start] + pre_new + new_s + h[b:]
        if img_url(imgs[0]) != img_url(new[0]):
            first_swaps.append((idx, img_url(imgs[0]), img_url(new[0])))
    # JSON-LD: each card's ListItem image (and the Article lead image for card 1)
    # follows the card's first photo. Replace as text to keep the formatting, but
    # only when every occurrence of the old URL sits in one of those spots.
    def fix_ld(m):
        block = m.group(0)
        body = block[block.find(">") + 1:block.rfind("<")]
        try:
            data = json.loads(body)
        except ValueError:
            return block
        nodes = []
        def walk(o):
            if isinstance(o, dict):
                nodes.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(data)
        def imgs_of(o):
            im = o.get("image")
            if isinstance(im, str):
                return [im]
            if isinstance(im, list):
                return [x for x in im if isinstance(x, str)]
            return []
        def count(lst, u):
            return sum(1 for x in lst if norm(x).endswith(norm(u)))
        for idx, old, new_u in first_swaps:
            allowed = 0
            for n in nodes:
                if n.get("@type") == "ListItem" and n.get("position") == idx and isinstance(n.get("item"), dict):
                    allowed += count(imgs_of(n["item"]), old)
                if idx == 1 and n.get("@type") in ("Article", "BlogPosting", "WebPage"):
                    allowed += count(imgs_of(n), old)
            total = sum(count(imgs_of(n), old) for n in nodes)
            spellings = {x for x in re.findall(r'"([^"]+)"', block)
                         if "/assets/" in x and norm(x).endswith(norm(old))}
            if allowed and allowed == total and sum(block.count('"%s"' % x) for x in spellings) == allowed:
                for x in spellings:
                    block = block.replace('"%s"' % x, '"%s%s"' % (x[:x.find("/assets/")], ld_url(new_u, "/")))
                LD_LOG.append((idx, "ok"))
            elif total:
                LD_LOG.append((idx, "skip: old url also used elsewhere (%d/%d)" % (allowed, total)))
        # Multi-photo image lists made from one card's slider (hostels): follow
        # the new slider order, drop removed photos, lead with the new first photo.
        def fix_list(lm):
            items = re.findall(r'"([^"]*)"', lm.group(2))
            if len(items) < 2:
                return lm.group(0)
            for idx, (old_list, new_list) in card_lists.items():
                old_n = [norm(u) for u in old_list]
                if not all(norm(u) in old_n for u in items):
                    continue
                new_n = [norm(u) for u in new_list]
                kept = sorted([u for u in items if norm(u) in new_n], key=lambda u: new_n.index(norm(u)))
                if not kept or norm(kept[0]) != new_n[0]:
                    kept = [ld_url(new_list[0], items[0])] + kept
                kept = kept[:len(items)]
                if kept == items:
                    return lm.group(0)
                inner = lm.group(2)
                lead = re.match(r'\s*', inner).group(0)
                trail = re.search(r'\s*$', inner).group(0)
                sep = re.search(r'",(\s*)"', inner)
                sep = "," + (sep.group(1) if sep else " ")
                LD_LOG.append((idx, "list reordered"))
                return lm.group(1) + lead + sep.join('"%s"' % u for u in kept) + trail + "]"
            return lm.group(0)
        block = re.sub(r'("image":\s*\[)([^\]]*)\]', fix_list, block)
        return block
    h = re.sub(r'<script[^>]*type="application/ld\+json"[^>]*>.*?</script>', fix_ld, h, flags=re.S)
    return h, urls, first_swaps


def main():
    check = "--check" in sys.argv
    report = {}
    for page, orders in PHOTO_ORDER.items():
        files = cluster_files(page)
        done, skipped = [], []
        if not files:
            report[page] = {"changed": [], "skipped": ["page not found (moved or deleted? update slider_photo_order_data.py)"]}
            continue
        for lang, f in files:
            h = f.read_text()
            if 'class="bpa-slider"' not in h:
                skipped.append(lang + " (old w-slider template)")
                continue
            try:
                new_h, urls, _ = reorder_page(h, orders)
            except MissingPhoto as e:
                skipped.append("%s (different photo set: %s)" % (lang, e))
                continue
            if new_h != h:
                if not check:
                    f.write_text(new_h)
                done.append(lang)
        report[page] = {"changed": done, "skipped": skipped}
    print(json.dumps(report, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
