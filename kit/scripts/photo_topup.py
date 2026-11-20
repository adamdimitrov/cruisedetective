"""Top up listicle card sliders to 9-10 photos from the exact product's own listing.

Shared kit script. A card slider should hold 9-10 photos. This tool finds the cards that
hold fewer, collects the photos of the exact product the card books (its booking/listing
link), drops the ones the card already has, and writes the photos you pick, in the order
you pick, into the card data (data/listicles/<slug>.json), then rebuilds the page.

Photo rules (RULES.md section 7, memory notes of the owner):
- exact product only: the listing the card's button books, never another tour, never the
  same operator's other product;
- the order sells the card's promise: first photo = the money shot, then the story; drop
  off-topic shots, menus, maps, text boards, logos and near-duplicates (pick from the
  contact sheet, never by filename);
- new files are .avif with new filenames under /assets/ (never overwrite an asset);
- keep our own photos (local files of the card); a listing with too few photos stays short.

Steps:
  scan [--min 9] [--json]                     cards under --min photos on the pages in
                                              site.json listicle.pages (English data files)
  snippet [gyg|generic]                       JavaScript to run on the listing page in the
                                              built-in browser (GetYourGuide blocks curl): gyg
                                              returns "gyg:<photo> <photo> ..." (the product's own
                                              gallery, pass it to stage as is); generic returns
                                              {"url", "photos": [image URLs]}
  stage <page> <card-id> <source> [--out DIR] downloads the candidates and writes a numbered
                                              contact sheet: E1..En = photos on the card now,
                                              C1..Cm = new candidates (near-duplicates of the
                                              card's photos and of each other are dropped)
        <source> = the "gyg:..." string from `snippet gyg`,
                   a JSON file ({"url", "photos": [...]} or a list of URLs),
                   a Hostelworld / TourRadar / Tiqets / operator page URL (read with curl),
                   or image URLs separated by commas
  apply <page> <card-id> --order E1,C4,E2,... [--stage DIR] [--max 10] [--no-build]
        [--alts '{"C4": "alt text"}']
                                              writes the order: picked candidates become new
                                              .avif files next to the card's photos, the
                                              slider and thumbnails follow the order, unlisted
                                              E photos are dropped; then `listicle.py build`
                                              and swaps the new gallery into the language
                                              pages built from the English cards. Alt of a new photo: the
                                              slider's shared alt, else the product name, else
                                              --alts
  skip <page> <card-id> --reason TEXT          record why a card stays under 9 (scan shows it)

<page> is the English page (as in site.json listicle.pages) or its data file.
Staging lives outside the repo (default: $TMPDIR/photo_topup/<slug>/<card-id>).

Usage: python3 scripts/photo_topup.py scan|snippet|stage|apply ...
"""
import hashlib
import html as _html
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.request
from urllib.parse import quote, unquote, urljoin, urlparse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checks"))
from sitecfg import ROOT, SITE  # noqa: E402

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) " \
     "Chrome/130.0 Safari/537.36"
MIN, MAX = 9, 10
SIZE = (1200, 800)          # saved photo size (3:2, the card slider's shape), never upscaled
DUP_BITS = 10               # dHash distance (of 64) at or below which two photos are the same shot
GYG_IMG = "https://cdn.getyourguide.com/image/fit=cover,width=%d,height=%d/tour_img/%s"


# ------------------------------------------------------------------ pages and cards
def page_list():
    return [p for p in SITE.get("listicle", {}).get("pages", [])]


def data_file(page):
    if page.endswith(".json"):
        return page if os.path.isabs(page) else os.path.join(ROOT, page)
    rel = os.path.relpath(os.path.join(ROOT, page), ROOT)
    slug = rel[:-5] if rel.endswith(".html") else rel
    return os.path.join(ROOT, "data", "listicles", slug.replace(os.sep, "--") + ".json")


def page_of(data_path):
    slug = os.path.basename(data_path)[:-5]
    for p in page_list():
        if os.path.basename(data_file(p)) == slug + ".json":
            return p
    rel = slug.replace("--", os.sep)
    return rel + ".html" if not rel.endswith("index") else rel + ".html"


def is_english(page):
    """English pages are the ones whose cards are data (language pages are built from them)."""
    return os.path.exists(data_file(page))


def load(path):
    return json.load(open(path, encoding="utf-8"))


def save(path, data):
    """Write the card data in the file's own style (listicle.dumps, or plain indent=1 JSON)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import listicle
    style = "dumps"
    try:
        old = open(path, encoding="utf-8").read()
        if old == json.dumps(json.loads(old), indent=1, ensure_ascii=False) + "\n":
            style = "indent1"
    except (OSError, ValueError):
        pass
    text = json.dumps(data, indent=1, ensure_ascii=False) if style == "indent1" else listicle.dumps(data)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text + "\n")


def card_by_id(data, cid):
    for c in data.get("cards", []):
        if c.get("id") == cid:
            return c
    raise SystemExit(f"no card {cid}")


def booking_url(card):
    for get in (lambda c: c["cta"]["btn"]["url"], lambda c: c["title"]["url"]):
        try:
            u = get(card)
            if u and u.startswith("http"):
                return u
        except (KeyError, TypeError):
            pass
    return ""


def product_url(u):
    """The listing behind an affiliate link (tracking redirects and partner parameters dropped)."""
    p = urlparse(u)
    if p.netloc.endswith("tp.st"):          # Travelpayouts short link -> its redirect target
        try:
            loc = subprocess.run(["curl", "-s", "-o", "/dev/null", "-w", "%{redirect_url}", u],
                                 capture_output=True, text=True, timeout=30).stdout.strip()
            if loc:
                return product_url(loc)
        except Exception:  # noqa: BLE001
            pass
    if "destination:" in u:                 # partnerize (prf.hn) deep link
        return product_url(unquote(u.split("destination:", 1)[1]).split("?")[0])
    if "redirect" in p.path:
        q = dict(x.split("=", 1) for x in p.query.split("&") if "=" in x)
        for k in ("u", "url", "murl", "dest"):
            if k in q:
                return product_url(unquote(q[k]))
    if "getyourguide." in p.netloc:
        return f"https://www.getyourguide.com{p.path}"
    if "tourradar." in p.netloc or "tiqets." in p.netloc or "guruwalk." in p.netloc:
        return f"https://{p.netloc}{p.path}"
    return u


def kv(attrs):
    return {k: v for k, v in attrs}


def photo_url(attrs):
    a = kv(attrs)
    return a.get("data-src") or a.get("src")


def photos_of(card):
    return card.get("gallery", {}).get("photos", [])


# ------------------------------------------------------------------ scan
def scan(minimum=MIN, as_json=False):
    rows = []
    for page in page_list():
        df = data_file(page)
        if not os.path.exists(df):
            continue
        for c in load(df).get("cards", []):
            g = c.get("gallery")
            if not isinstance(g, dict) or "photos" not in g:
                raw = (g or {}).get("raw", "") if isinstance(g, dict) else ""
                n = len(re.findall(r"<img\b", raw.split('class="cd-thumbs"')[0]))
                if n < minimum:
                    one = "single-photo layout (cd-gal-one), " if "cd-gal-one" in raw else ""
                    rows.append({"page": page, "card": c.get("id"), "photos": n, "url": booking_url(c),
                                 "note": one + "gallery kept as raw HTML: convert the card first",
                                 "skip": c.get("_photo_topup", {}).get("skip")})
                continue
            n = len(g["photos"])
            if n < minimum:
                rows.append({"page": page, "card": c["id"], "photos": n, "url": booking_url(c),
                             "skip": c.get("_photo_topup", {}).get("skip")})
    if as_json:
        print(json.dumps(rows, indent=1, ensure_ascii=False))
    else:
        for r in rows:
            host = urlparse(r["url"]).netloc or "-"
            note = r.get("note") or (f"skip: {r['skip']}" if r.get("skip") else "")
            print(f"{r['photos']:>2}  {r['page']}  {r['card']:<8} {host}  {note}")
        todo = [r for r in rows if not r.get("skip")]
        print(f"{len(rows)} card(s) under {minimum} photos, {len(todo)} to top up")
    return rows


# ------------------------------------------------------------------ browser snippets
SNIPPETS = {
    # GetYourGuide: the product's own gallery block ("main-media-gallery"), not the related tours
    # or traveller review photos further down the page.
    "gyg": r"""(()=>{const t=[...document.scripts].map(s=>s.textContent).find(x=>x.includes('main-media-gallery'))||'';
const k=t.indexOf('mediaGalleryCarousel',t.indexOf('"id":"main-media-gallery"'));let s=t.indexOf('[',k),d=0,e=s;
for(;k>0&&e<t.length;e++){const c=t[e];if(c==='[')d++;else if(c===']'){d--;if(!d)break}}
const g=k>0?t.slice(s,e+1):'';const hs=[...g.matchAll(/tour_img.{1,8}?([a-f0-9]{10,64}\.(?:jpe?g|png|webp))/g)].map(m=>m[1]);
return 'gyg:'+[...new Set(hs)].join(' ')})()""",
    # anything else: JSON-LD images, og:image and large <img> elements, page order
    "generic": r"""(()=>{const out=[];const add=u=>{if(u&&!out.includes(u))out.push(u)};
document.querySelectorAll('script[type="application/ld+json"]').forEach(s=>{try{const f=o=>{if(o&&typeof o==='object'){
let im=o.image;if(im){(Array.isArray(im)?im:[im]).forEach(x=>add(typeof x==='string'?x:x.url||x.contentUrl))}Object.values(o).forEach(f)}};
f(JSON.parse(s.textContent))}catch(e){}});const og=document.querySelector('meta[property="og:image"]');if(og)add(og.content);
document.querySelectorAll('img').forEach(i=>{if((i.naturalWidth||0)>=600)add(i.currentSrc||i.src)});
return JSON.stringify({url:location.href.split('?')[0],photos:out})})()""",
}


# ------------------------------------------------------------------ candidate sources (curl)
def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en"})
    with urllib.request.urlopen(req, timeout=40) as r:
        b = r.read()
    return b if binary else b.decode("utf-8", "replace")


def fetch_page(url):
    """A listing page's HTML (curl: follows every redirect kind, 308 included)."""
    r = subprocess.run(["curl", "-sL", "--max-time", "40", "-A", UA, "-H", "Accept-Language: en", url],
                       capture_output=True, timeout=60)
    return r.stdout.decode("utf-8", "replace")


def page_photos(url):
    """Photo URLs of the exact product's own gallery on a listing page that can be read with curl.
    GetYourGuide refuses curl: use `snippet gyg` in the browser instead."""
    url = product_url(url)
    host = urlparse(url).netloc
    if "getyourguide." in host:
        raise SystemExit("GetYourGuide blocks curl: open the listing in the built-in browser, run "
                         "`photo_topup.py snippet gyg` there and pass its output to stage")
    src = fetch_page(url)
    found = []

    def add(u):
        u = _html.unescape(u).replace("\\/", "/")
        if u.startswith("//"):
            u = "https:" + u
        if u not in found:
            found.append(u)

    if "hostelworld" in host:               # property photos of this property id only
        pid = re.search(r"/(\d{3,})(?:/|$)", urlparse(url).path)
        pid = pid.group(1) if pid else r"\d+"
        for m in re.finditer(r"a\.hwstatic\.com/image/upload/[^\"'\s)]*?/propertyimages/\d+/%s/[A-Za-z0-9_-]+\.(?:jpe?g|png|webp)" % pid, src):
            add("https://a.hwstatic.com/image/upload/q_auto,w_1600/propertyimages/" + m.group(0).split("/propertyimages/", 1)[1])
    elif "tourradar" in host:               # tour photos of this tour id (not maps, operator logos, travellers)
        tid = re.search(r"/t/(\d+)", url)
        tid = tid.group(1) if tid else r"\d+"
        for m in re.finditer(r"cdn\.tourradar\.com/s3/tour/\d+x\d+/(%s_[A-Za-z0-9]+\.(?:jpe?g|png|webp))" % tid, src):
            add("https://cdn.tourradar.com/s3/tour/1500x800/" + m.group(1))
    elif "tiqets" in host:                  # the product gallery's lightbox links
        for m in re.finditer(r'<a\s+href="(https://aws-tiqets-cdn\.imgix\.net/images/content/[a-f0-9]+\.\w+)', src):
            add(m.group(1) + "?w=1600&h=1067&fit=crop")
    elif "guruwalk" in host:                # the walk's own gallery
        for m in re.finditer(r'alt="Tour image \d+"[^>]*src="(https://media\.guruwalk\.com/[a-z0-9]+)"', src):
            add(m.group(1))
    elif "data-large_image=" in src:        # WooCommerce product gallery (operator shops)
        for m in re.finditer(r'data-large_image="([^"]+)"', src):
            add(m.group(1))
    if not found:                           # generic: JSON-LD / og:image of the page
        for m in re.finditer(r'"image"\s*:\s*(\[[^\]]*\]|"[^"]+")', src):
            for u in re.findall(r'"(https?:[^"]+)"', m.group(1)):
                add(u)
        m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', src)
        if m:
            add(m.group(1))
    return found


def resolve(u):
    if u.startswith("gyg:"):
        return GYG_IMG % (SIZE[0], SIZE[1], u[4:])
    return u


def candidates_from(source):
    if source.startswith("gyg:"):   # output of `snippet gyg`: gyg:<hash.jpg> <hash.jpg> ...
        return ["gyg:" + h for h in source[4:].split()]
    if os.path.exists(source):
        d = load(source)
        return d["photos"] if isinstance(d, dict) else d
    if "," in source or re.search(r"\.(jpe?g|png|webp|avif)(\?|$)", source, re.I):
        return [s for s in source.split(",") if s]
    return page_photos(source)


# ------------------------------------------------------------------ images
def pil():
    from PIL import Image  # noqa: F401  (Pillow with AVIF support)
    from PIL import features
    if not features.check("avif"):
        raise SystemExit("Pillow without AVIF support: pip3 install -U pillow")
    return Image


def dhash(im, crop=1.0):
    im = im.convert("L")
    if crop < 1:
        w, h = im.size
        cw, ch = w * crop, h * crop
        im = im.crop((int((w - cw) / 2), int((h - ch) / 2), int((w + cw) / 2), int((h + ch) / 2)))
    g = im.resize((9, 8))
    px = list(g.getdata())
    bits = 0
    for r in range(8):
        for c in range(8):
            bits = (bits << 1) | (px[r * 9 + c] > px[r * 9 + c + 1])
    return bits


def crops(im, aspect):
    """Windows of `im` with the given aspect: 3 scales x 3x3 positions (the same shot saved with
    another crop or shape is one of them)."""
    w, h = im.size
    if w / h > aspect:
        bw, bh = h * aspect, h
    else:
        bw, bh = w, w / aspect
    for sc in (1.0, 0.9, 0.8):
        cw, ch = bw * sc, bh * sc
        for fx in (0, 0.5, 1):
            for fy in (0, 0.5, 1):
                x, y = (w - cw) * fx, (h - ch) * fy
                yield im.crop((int(x), int(y), int(x + cw), int(y + ch)))


def sig(im):
    """A small greyscale copy (hashes are taken per comparison, at the other photo's shape)."""
    g = im.convert("L")
    g.thumbnail((240, 240))
    return g


def dist(a, b):
    """Smallest dHash distance between one photo and any crop of the other, both ways."""
    best = 64
    for x, y in ((a, b), (b, a)):
        hx = dhash(x)
        asp = x.size[0] / x.size[1]
        for c in crops(y, asp):
            d = bin(hx ^ dhash(c)).count("1")
            if d < best:
                best = d
    return best


def local_file(url):
    """The repo file of a site URL (/assets/...), or None."""
    if not url or not url.startswith("/") or url.startswith("//"):
        return None
    p = os.path.join(ROOT, unquote(url.split("?")[0]).lstrip("/"))
    return p if os.path.isfile(p) else None


def open_url_image(url):
    Image = pil()
    lf = local_file(url)
    if lf:
        return Image.open(lf)
    return Image.open(io.BytesIO(fetch(url, binary=True)))


def fit(im, size=SIZE):
    """Cover-crop to the slider shape, never upscaled."""
    im = im.convert("RGB")
    w, h = im.size
    tw, th = size
    r = max(tw / w, th / h)
    if r > 1:   # smaller than the target: crop to shape at native size
        r = 1
        tw, th = (w, round(w * size[1] / size[0])) if w / h < size[0] / size[1] else (round(h * size[0] / size[1]), h)
    nw, nh = max(tw, round(w * r)), max(th, round(h * r))
    im = im.resize((nw, nh), pil().LANCZOS)
    x, y = (nw - tw) // 2, (nh - th) // 2
    return im.crop((x, y, x + tw, y + th))


def sheet(items, out):
    """Numbered contact sheet: [(label, PIL image)] -> out (jpg)."""
    Image = pil()
    from PIL import ImageDraw
    cw, ch, cols = 360, 240, 4
    rows = (len(items) + cols - 1) // cols
    s = Image.new("RGB", (cols * cw, rows * (ch + 28)), "white")
    d = ImageDraw.Draw(s)
    for i, (label, im) in enumerate(items):
        x, y = (i % cols) * cw, (i // cols) * (ch + 28)
        t = im.convert("RGB").copy()
        t.thumbnail((cw - 8, ch - 8))
        s.paste(t, (x + 4, y + 4))
        d.rectangle((x + 4, y + ch, x + 120, y + ch + 24), fill="black")
        d.text((x + 10, y + ch + 5), label, fill="white")
    s.save(out, quality=82)


# ------------------------------------------------------------------ stage
def stage_dir(df, cid, out=None):
    d = out or os.path.join(tempfile.gettempdir(), "photo_topup", os.path.basename(df)[:-5], cid)
    os.makedirs(d, exist_ok=True)
    return d


def stage(page, cid, source, out=None):
    df = data_file(page)
    card = card_by_id(load(df), cid)
    d = stage_dir(df, cid, out)
    existing = []
    for i, p in enumerate(photos_of(card), 1):
        u = photo_url(p)
        try:
            existing.append((f"E{i}", open_url_image(u), u))
        except Exception as e:  # noqa: BLE001
            print(f"  E{i}: cannot open {u}: {e}")
    hashes = [sig(im) for _, im, _ in existing]
    # photos of the page's other cards: a photo never appears on two cards of one page
    others = []
    for oc in load(df).get("cards", []):
        if oc.get("id") == cid:
            continue
        for p in photos_of(oc):
            lf = local_file(photo_url(p))
            if lf:
                try:
                    others.append((oc["id"], sig(pil().open(lf))))
                except Exception:  # noqa: BLE001
                    pass
    cands, skipped = [], []
    urls = candidates_from(source)
    for u in urls:
        full = resolve(u)
        try:
            raw = fetch(full, binary=True)
            im = pil().open(io.BytesIO(raw))
            im.load()
        except Exception as e:  # noqa: BLE001
            skipped.append((u, f"download failed: {e}"))
            continue
        if min(im.size) < 400:
            skipped.append((u, f"too small {im.size}"))
            continue
        h = sig(im)
        near = [i for i, x in enumerate(hashes) if dist(h, x) <= DUP_BITS]
        if near:
            lab = existing[near[0]][0] if near[0] < len(existing) else cands[near[0] - len(existing)][0]
            skipped.append((u, f"same shot as {lab}"))
            continue
        twin = next((ocid for ocid, oh in others if dist(h, oh) <= DUP_BITS), None)
        if twin:
            skipped.append((u, f"already on {twin}"))
            continue
        hashes.append(h)
        n = len(cands) + 1
        path = os.path.join(d, f"C{n}.jpg")
        fit(im).save(path, quality=92)
        cands.append((f"C{n}", im, full))
    listing = source if source.startswith("http") else booking_url(card)
    if os.path.exists(source):
        src_data = load(source)
        listing = src_data.get("url", listing) if isinstance(src_data, dict) else listing
    manifest = {"data": os.path.relpath(df, ROOT), "card": cid, "listing": listing,
                "existing": [[lab, u] for lab, _, u in existing],
                "candidates": [[lab, u, os.path.join(d, lab + ".jpg")] for lab, _, u in cands],
                "skipped": skipped}
    with open(os.path.join(d, "stage.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
    sheet([(lab, im) for lab, im, _ in existing] + [(lab, im) for lab, im, _ in cands],
          os.path.join(d, "contact.jpg"))
    print(f"{os.path.relpath(df, ROOT)} {cid}: {len(existing)} on the card, {len(cands)} new candidate(s), "
          f"{len(skipped)} dropped")
    for u, why in skipped:
        print(f"  dropped {u[:90]}: {why}")
    print(f"  contact sheet: {os.path.join(d, 'contact.jpg')}")
    return d


# ------------------------------------------------------------------ apply
URL_ATTRS = ("src", "data-src", "srcset", "data-srcset")


def variants(attrs):
    """{width: url} of a photo's srcset (main url under 0), so new photos get the same set."""
    a = kv(attrs)
    out = {0: photo_url(attrs)}
    for k in ("srcset", "data-srcset"):
        for part in (a.get(k) or "").split(","):
            bits = part.split()
            if len(bits) == 2 and bits[1].endswith("w"):
                out[int(bits[1][:-1])] = bits[0]
    return out


def suffix_rule(main, other):
    """How a variant's name derives from the main photo's: (suffix before the extension) or None."""
    mb, me = os.path.splitext(unquote(main))
    ob, oe = os.path.splitext(unquote(other))
    if ob.startswith(mb):
        return ob[len(mb):], oe
    # renamed files (Webflow exports): the variant still ends in a size suffix such as -p-500 / -t240
    m = re.search(r"(-p-\d+|-t\d*)$", ob)
    if m:
        return m.group(1), oe
    return None


LOAD_ATTRS = {"src", "data-src", "srcset", "data-srcset", "loading", "fetchpriority", "decoding",
              "width", "height", "sizes"}


def render_photo(template, urls, own):
    """New attrs for a photo in a slot: the slot template's loading attrs (eager first slide or a
    lazy one) with the photo's URLs, plus the photo's own attrs (alt, data-cap, title...)."""
    tv = variants(template)
    out = []
    for k, v in template:
        if k in ("src", "data-src") and not v.startswith("data:"):
            out.append([k, urls[0]])
        elif k in ("srcset", "data-srcset"):
            parts = []
            for part in v.split(","):
                bits = part.split()
                w = int(bits[1][:-1]) if len(bits) == 2 and bits[1].endswith("w") else None
                if w is None:
                    continue
                main_w = [x for x, u in tv.items() if x and u == tv[0]]
                u = urls[0] if (main_w and w == main_w[0]) or bits[0] == tv[0] else urls.get(w)
                if u:
                    parts.append(f"{u} {w}w")
            out.append([k, ", ".join(parts)])
        elif k in LOAD_ATTRS:
            out.append([k, v])
        elif k in own:
            out.append([k, own[k]])
    have = {k for k, _ in out}
    out += [[k, v] for k, v in own.items() if k not in have and k not in LOAD_ATTRS]
    return out


def numbered_alt(alt, i, n):
    m = re.fullmatch(r"(.*) \((\d+)/(\d+)\)", alt)
    return f"{m.group(1)} ({i}/{n})" if m else alt


def new_name(card, folder, used, suffixes=()):
    """Next free <stem>-NN.avif in the card's photo folder (stem from the card's own photo names)."""
    stems = []
    for p in photos_of(card):
        b = os.path.splitext(os.path.basename(unquote(photo_url(p))))[0]
        m = re.fullmatch(r"(.*?)[-_ ]?\(?(\d{1,3})\)?", b)
        if m and not re.fullmatch(r"[0-9a-f]{24}_.*", b):
            stems.append(m.group(1))
    stem = max(set(stems), key=stems.count) if stems else None
    if not stem:
        t = re.sub(r"<[^>]+>", "", (card.get("title") or {}).get("text", "") or card.get("id", "photo"))
        stem = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", _html.unescape(t)).encode("ascii", "ignore")
                      .decode().lower()).strip("-")
        if len(stem) > 48:                  # cut at a word boundary
            stem = stem[:48].rsplit("-", 1)[0]
        stem = stem or card["id"]
    n = 1
    while True:
        name = f"{stem}-{n:02d}.avif"
        names = [name] + [f"{stem}-{n:02d}{suf}.avif" for suf in suffixes]
        if name not in used and not any(os.path.exists(os.path.join(ROOT, folder.lstrip("/"), x)) for x in names):
            used.add(name)
            return f"{folder}/{name}"
        n += 1


def card_folder(card, df):
    """The /assets/ folder of the card's local photos (most used), else /assets/<page slug>."""
    fs = []
    for p in photos_of(card):
        u = photo_url(p)
        if u and u.startswith("/assets/") and not u.startswith("/assets/cdn/"):
            fs.append(os.path.dirname(u))
    if fs:
        return max(set(fs), key=fs.count)
    return "/assets/" + os.path.basename(df)[:-5].split("--")[0]


def write_avif(src_path, url, width=None):
    Image = pil()
    im = Image.open(src_path).convert("RGB")
    if width and im.size[0] > width:
        im = im.resize((width, round(im.size[1] * width / im.size[0])), Image.LANCZOS)
    dest = os.path.join(ROOT, unquote(url).lstrip("/"))
    if os.path.exists(dest):
        raise SystemExit(f"{url} exists: never overwrite an asset")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    im.save(dest, "AVIF", quality=60)


def apply(page, cid, order, stage_path=None, maximum=MAX, build=True, alt_over=None):
    df = data_file(page)
    data = load(df)
    card = card_by_id(data, cid)
    d = stage_dir(df, cid, stage_path)
    man = load(os.path.join(d, "stage.json"))
    g = card["gallery"]
    old = photos_of(card)
    picks = [x.strip().upper() for x in order.split(",") if x.strip()]
    if len(picks) > maximum:
        raise SystemExit(f"{len(picks)} photos picked, at most {maximum}")
    if len(set(picks)) != len(picks):
        raise SystemExit("a photo is picked twice")
    eager = old[0]
    lazy = next((p for p in old[1:] if "data-src" in kv(p)), None)
    if lazy is None:
        raise SystemExit("the card has no lazy slide to copy the slot format from")
    # thumbs: same file as the photo, or a derived variant (suffix + width of the existing thumb)
    old_thumbs = g.get("thumbs", [])
    trule = None
    if old_thumbs and old_thumbs[0]["src"] != photo_url(old[0]):
        trule = suffix_rule(photo_url(old[0]), old_thumbs[0]["src"])
        if trule is None:
            raise SystemExit("thumbnail names do not derive from the photo names: extend photo_topup.py")
    trule_w = None
    if trule:
        tf = local_file(old_thumbs[0]["src"])
        trule_w = pil().open(tf).size[0] if tf else 240
    # srcset variants of the lazy template (e.g. -p-500 at 500w)
    vrules = {}
    for w, u in variants(lazy).items():
        if w and u != variants(lazy)[0]:
            r = suffix_rule(variants(lazy)[0], u)
            if r is None:
                raise SystemExit("srcset variant names do not derive from the photo names: extend photo_topup.py")
            vrules[w] = r
    folder = card_folder(card, df)
    used = set()
    ex = {lab: old[int(lab[1:]) - 1] for lab in (f"E{i}" for i in range(1, len(old) + 1))}
    cand = {lab: path for lab, _, path in man["candidates"]}
    alts = {re.sub(r" \(\d+/\d+\)$", "", kv(p).get("alt", "")) for p in old}
    if len(alts) == 1:     # one alt for the whole slider (usually the product name)
        base_alt = alts.pop()
    else:                  # each photo described: a new photo gets the product name unless --alt says more
        t = (card.get("title") or {}).get("text", "") if isinstance(card.get("title"), dict) else ""
        base_alt = _html.unescape(re.sub(r"<[^>]+>", "", t)).strip() or kv(old[0]).get("alt", "")
    entries = []   # (urls {0: main, w: variant}, alt, thumb url)
    for i, lab in enumerate(picks):
        if lab in ex:
            p = ex[lab]
            urls = variants(p)
            own = {k: v for k, v in p if k not in LOAD_ATTRS}
            alt = own.get("alt", base_alt)
            th = old_thumbs[int(lab[1:]) - 1]["src"] if len(old_thumbs) == len(old) else photo_url(p)
        elif lab in cand:
            main = new_name(card, folder, used, [suf for suf, _ in vrules.values()] + ([trule[0]] if trule else []))
            write_avif(cand[lab], main)
            urls = {0: main}
            stem, ext = os.path.splitext(main)
            for w, (suf, _) in vrules.items():
                urls[w] = stem + suf + ".avif"
                write_avif(cand[lab], urls[w], width=w)
            alt = (alt_over or {}).get(lab, base_alt)
            own = {"alt": alt}
            th = main
            if trule:
                th = stem + trule[0] + ".avif"
                if th not in urls.values():     # the thumbnail may be one of the srcset files
                    write_avif(cand[lab], th, width=trule_w)
        else:
            raise SystemExit(f"unknown photo {lab} (E1..E{len(old)}, {', '.join(cand) or 'no candidates'})")
        own["alt"] = alt
        entries.append((urls, own, th))
    n = len(entries)
    photos, thumbs = [], []
    for i, (urls, own, th) in enumerate(entries):
        own = dict(own, alt=numbered_alt(own["alt"], i + 1, n))
        photos.append(render_photo(eager if i == 0 else lazy, urls, own))
        thumbs.append({"src": th})
    g["photos"] = photos
    g["thumbs"] = thumbs
    g.pop("_pill", None)
    meta = card.setdefault("_photo_topup", {})
    meta["listing"] = man.get("listing")
    if n >= MIN:
        meta.pop("skip", None)
    save(df, data)
    print(f"{os.path.relpath(df, ROOT)} {cid}: {len(old)} -> {n} photos "
          f"({sum(1 for x in picks if x.startswith('C'))} new)")
    if build:
        rebuild(df, [cid])


def mark_skip(page, cid, reason):
    """Record why a card stays under 9 photos (scan lists it as skipped)."""
    df = data_file(page)
    data = load(df)
    card_by_id(data, cid).setdefault("_photo_topup", {})["skip"] = reason
    save(df, data)
    print(f"{os.path.relpath(df, ROOT)} {cid}: skip ({reason})")


def listicle_mod():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import listicle
    return listicle


def lang_pages(en_page):
    """(lang, file) of the language versions built from these English cards (hreflang links that
    point at pages listed in site.json listicle.pages)."""
    en = open(os.path.join(ROOT, en_page), encoding="utf-8").read()
    out = []
    for tag_ in re.findall(r"<link\b[^>]*>", en):
        lm = re.search(r'hreflang="([^"]+)"', tag_)
        hm = re.search(r'href="([^"]+)"', tag_)
        if not lm or not hm or lm.group(1) in ("en", "x-default"):
            continue
        path = _html.unescape(re.sub(r"^https?://[^/]+", "", hm.group(1))).strip("/")
        for c in (path + ".html", path + "/index.html"):
            if c in page_list() and not is_english(c):
                out.append((lm.group(1), c))
    return out


def gallery_span(src, cid):
    """(start, end) of the card's <div class="cd-gal"> block in a page."""
    m = re.search(r'<div class="bpa-card"[^>]*\bid="%s"' % re.escape(cid), src)
    if not m:
        return None
    g = src.find('<div class="cd-gal">', m.end())
    if g < 0:
        return None
    depth = 0
    for t in re.finditer(r"<(/?)div\b[^>]*>", src[g:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return g, g + t.end()
    return None


def sync_lang_galleries(en_page, cids):
    """Language pages share the English photos: swap in the new gallery of each changed card (only
    that block; the rest of the language page is left byte for byte, even when other strings of
    the page still wait for translation)."""
    L = listicle_mod()
    data = load(data_file(en_page))
    for lang, page in lang_pages(en_page):
        tr = L.Lang(os.path.join(ROOT, en_page), lang)
        tdata = tr.translate(data)
        path = os.path.join(ROOT, page)
        src = open(path, encoding="utf-8").read()
        out = src
        for cid in cids:
            card = card_by_id(tdata, cid)
            span = gallery_span(out, cid)
            if not span:
                print(f"  {page}: no gallery for {cid}, left as is")
                continue
            saved, L.UI = L.UI, tr.ui
            try:
                gal = L.render_gallery(card["gallery"], int(cid.split("-")[1]))
            finally:
                L.UI = saved
            out = out[:span[0]] + gal + out[span[1]:]
        if out != src:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(out)
            print(f"  {page}: gallery of {', '.join(cids)} updated")


def rebuild(df, cids=()):
    page = page_of(df)
    here = os.path.join(ROOT, "scripts", "listicle.py")
    script = here if os.path.exists(here) else os.path.join(os.path.dirname(os.path.abspath(__file__)), "listicle.py")
    subprocess.run([sys.executable, script, "build", os.path.join(ROOT, page)], check=True, cwd=ROOT)
    if cids:
        sync_lang_galleries(page, list(cids))


# ------------------------------------------------------------------ main
def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    opts = {}
    pos = []
    i = 0
    while i < len(rest):
        a = rest[i]
        if a.startswith("--"):
            k, _, v = a.partition("=")
            if not v and k in ("--min", "--out", "--order", "--stage", "--max", "--reason", "--alts") and i + 1 < len(rest):
                v = rest[i + 1]
                i += 1
            opts[k] = v or True
        else:
            pos.append(a)
        i += 1
    if cmd == "scan":
        scan(int(opts.get("--min", MIN)), bool(opts.get("--json")))
    elif cmd == "snippet":
        print(SNIPPETS[pos[0] if pos else "gyg"])
    elif cmd == "stage":
        stage(pos[0], pos[1], pos[2], opts.get("--out"))
    elif cmd == "apply":
        alt_over = json.loads(opts["--alts"]) if opts.get("--alts") else None
        apply(pos[0], pos[1], opts["--order"], opts.get("--stage"), int(opts.get("--max", MAX)),
              not opts.get("--no-build"), alt_over)
    elif cmd == "skip":
        mark_skip(pos[0], pos[1], opts.get("--reason") or " ".join(pos[2:]) or "listing has no more photos")
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
