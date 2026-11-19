#!/usr/bin/env python3
"""Dish photos in the menu cartes on /dinner-cruises-paris (English page), same design as the
Budapest dinner page (budapest-adventures scripts/dinner_set_menu_photos.py): a photo above each
dish we have a photo of, in both the breakdown cartes and the #dc-menu-* modal templates, plus a
photo button (thumbnails + "N dish photos" + Full menu) in each card's Food box.

Photos are my own test-cruise photos (assets/cdn), cropped to one plate each, and only where the
plate clearly is a dish on the current menu. Placed by brand + carte tier + course + position.
Idempotent: re-running strips and re-adds.
    python3 scripts/dinner_menu_photos.py          # apply
    python3 scripts/dinner_menu_photos.py --check  # exit 1 if photos are missing
"""
import html, re, sys

PAGE = "dinner-cruises-paris/index.html"
A = "/assets/dinner-cruises-paris/menu-photos/"
BM = {"starter": [None, "bm-beef-carpaccio", None], "main": [None, None, "bm-sea-bream"]}
# (brand prefix, data-tier) -> {course: [photo per dish position, None = no photo]}
MAP = {
    # Bateaux Mouches: carpaccio, sea bream, profiterole (dishes on the Harmonie/Prestige menus)
    ("Bateaux Mouches", "harmonie"): {**BM, "dessert": [None, None, "bm-profiterole"]},
    ("Bateaux Mouches", "prestige"): {**BM, "dessert": [None, None, None, "bm-profiterole"]},
    # La Marina romantic menu: foie gras with financier, sea bass with asparagus risotto and squid ink tuile.
    # (The test-cruise dessert was a crème brûlée tart, the current one is a lemon crème brûlée: no photo.)
    ("Paris City Vision", "adult"): {"starter": [None, "lm-foie-gras"], "main": ["lm-sea-bass", None, None]},
    # Paris en Scène: squash velouté with basil oil (same starter on both menus)
    ("Paris en Scène", "bistro"): {"starter": ["pes-squash-veloute"]},
    ("Paris en Scène", "plant"): {"starter": ["pes-squash-veloute"]},
    # Le Diamant Bleu (menu from the test cruise): fish with pomegranate, veal fillet, Chiboust cream
    ("Le Diamant Bleu", "dinner"): {"starter": [None, None, "db-fish-pomegranate"], "main": [None, None, "db-veal-fillet"],
                                    "dessert": [None, "db-chiboust"]},
}
# Food-box photo button: data-dc-menu -> thumbnails (all photos of that menu)
TEASER = {
    "bmouches": ["bm-sea-bream", "bm-beef-carpaccio", "bm-profiterole"],
    "marina": ["lm-sea-bass", "lm-foie-gras"],
    "enscene": ["pes-squash-veloute"],
    "diamant": ["db-veal-fillet", "db-fish-pomegranate", "db-chiboust"],
}
CSS = """<style id="dc-menu-photos-css">
.dc-pms .dish .dc-dish-photo{display:block;width:min(300px,100%);height:auto;aspect-ratio:4/3;object-fit:cover;border-radius:6px;margin:6px auto 6px;border:1px solid #eadfca;background:#fff}
.dc-food-photos{display:block;width:100%;margin-top:10px;padding:8px;border:1px solid #e9d8ae;border-radius:12px;background:#fdf6e3;cursor:pointer;font:inherit;text-align:left;transition:border-color .2s,box-shadow .2s}
.dc-food-photos .th{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px}
.dc-food-photos .th span{position:relative;display:block;border-radius:8px;overflow:hidden;aspect-ratio:1;background:#fff;box-shadow:0 1px 3px rgba(60,40,10,.15)}
.dc-food-photos .th img{display:block;width:100%;height:100%;object-fit:cover;transition:transform .35s}
.dc-food-photos .tx{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;margin-top:7px;padding:0 2px;font-size:13px;font-weight:800;color:#92400e;line-height:1.25}
.dc-food-photos .tx b{font-size:12.5px;font-weight:700;color:#0369a1;text-decoration:underline;white-space:nowrap}
.dc-food-photos:hover{border-color:#d9b867;box-shadow:0 4px 14px rgba(146,64,14,.12)}
.dc-food-photos:hover .th img{transform:scale(1.06)}
.dc-food-photos:hover .tx,.dc-food-photos:hover .tx b{color:#92400e}
@media (min-width:601px){
.dc-food-photos{display:flex;align-items:center;gap:14px}
.dc-food-photos .th{flex:0 0 auto;grid-template-columns:repeat(4,72px)}
.dc-food-photos .th.n1{grid-template-columns:72px}.dc-food-photos .th.n2{grid-template-columns:repeat(2,72px)}.dc-food-photos .th.n3{grid-template-columns:repeat(3,72px)}
.dc-food-photos .tx{flex:1 1 auto;flex-direction:column;align-items:flex-start;gap:3px;margin-top:0;font-size:14px}
}
.dc-food:has(.dc-food-photos) .dc-food-head .dc-food-btn{display:none}
@media (max-width:600px){
.dc-food-head .dc-food-lvl{order:9;flex-basis:100%}
.dc-pms .dish .dc-dish-photo{width:min(260px,100%)}
.dc-food-photos .th.n1{grid-template-columns:72px}.dc-food-photos .th.n2{grid-template-columns:repeat(2,72px)}.dc-food-photos .th.n3{grid-template-columns:repeat(3,72px)}
.dc-food-photos.one{display:flex;align-items:center;gap:12px}.dc-food-photos.one .th{flex:0 0 auto}.dc-food-photos.one .tx{flex-direction:column;align-items:flex-start;gap:3px;margin-top:0}
}
</style>"""

DISH = re.compile(r'<div class="dish([^"]*)" data-diet="([^"]*)">(.*?)</div>', re.S)
SEC = re.compile(r'(<div class="sec" data-sec="([^"]+)">)(.*?)(?=<div class="sec"|$)', re.S)
CARTE = re.compile(r'<div class="dc-carte(?: dc-pms)?(?: on)?"[^>]*data-tier="([^"]+)"[^>]*>')


def do_carte(blk, plan, brand):
    blk = re.sub(r'<img class="dc-dish-photo"[^>]*>', "", blk)

    def fix_sec(m):
        head, key, body = m.group(1), m.group(2), m.group(3)
        if key not in plan:
            return m.group(0)
        dishes = list(DISH.finditer(body))
        assert len(dishes) == len(plan[key]), (brand, key, len(dishes))
        out, last = [], 0
        for d, photo in zip(dishes, plan[key]):
            out.append(body[last:d.start()])
            img = ""
            if photo:
                name = html.unescape(re.sub(r"<span.*", "", d.group(3), flags=re.S)).strip()
                img = (f'<img class="dc-dish-photo" src="{A}{photo}.webp" alt="{html.escape(brand + ": " + name, quote=True)}" '
                       f'width="600" height="450" loading="lazy" decoding="async">')
            out.append(f'<div class="dish{d.group(1)}" data-diet="{d.group(2)}">{img}{d.group(3)}</div>')
            last = d.end()
        out.append(body[last:])
        return head + "".join(out)

    return SEC.sub(fix_sec, blk)


def teaser(s, menu, keys):
    m = re.search(r'<button aria-haspopup="dialog" class="dc-food-btn" data-dc-menu="%s" type="button">([^<]*)</button>' % menu, s)
    assert m, menu
    label = m.group(1).replace("↗", "").strip()
    end = s.index('<div class="dc-dna">', m.end())
    end = s.index("</div>", end) + 6
    if s.startswith('<div class="dc-sets">', end):
        end = s.index("</div>", end) + 6
    n = len(keys)
    tiles = "".join(f'<span><img src="{A}{k}-sq.webp" alt="" width="240" height="240" loading="lazy" decoding="async"></span>' for k in keys[:4])
    txt = "1 dish photo" if n == 1 else f"{n} dish photos"
    btn = (f'<button class="dc-food-photos{" one" if n == 1 else ""}" data-dc-menu="{menu}" aria-haspopup="dialog" type="button">'
           f'<span class="th n{min(n, 4)}" aria-hidden="true">{tiles}</span><span class="tx"><span>📷 {txt}</span> <b>{label} ↗</b></span></button>')
    return s[:end] + btn + s[end:]


def process(s):
    n = 0
    for m in reversed(list(CARTE.finditer(s))):
        a = m.start(); b = s.index('<div class="foot">', a)
        blk = s[a:b]
        brand = re.search(r'class="brand">([^<·]*)', blk).group(1).strip()
        hit = next(((bp, t) for (bp, t) in MAP if brand.startswith(bp) and t == m.group(1)), None)
        if not hit:
            continue
        plan = MAP[hit]
        tag = m.group(0)
        if "dc-pms" not in tag:
            tag = tag.replace('class="dc-carte', 'class="dc-carte dc-pms', 1)
        s = s[:a] + tag + do_carte(blk[len(m.group(0)):], plan, brand) + s[b:]
        n += sum(1 for v in plan.values() for k in v if k)
    s = re.sub(r'<button class="dc-food-photos[^"]*" data-dc-menu="[^"]*".*?</button>', "", s, flags=re.S)
    for menu, keys in TEASER.items():
        s = teaser(s, menu, keys)
    s = re.sub(r'<style id="dc-menu-photos-css">.*?</style>', "", s, flags=re.S)
    s = s.replace("</head>", CSS + "</head>", 1)
    return s, n


if __name__ == "__main__":
    cur = open(PAGE, encoding="utf-8").read()
    new, n = process(cur)
    got = new.count(f'class="dc-dish-photo" src="{A}')
    # every carte appears twice (breakdown + modal template)
    ok = got == n and n == 2 * sum(1 for v in MAP.values() for c in v.values() for k in c if k)
    if "--check" in sys.argv:
        ok = ok and cur.count(f'class="dc-dish-photo" src="{A}') == n
    elif new != cur:
        open(PAGE, "w", encoding="utf-8").write(new)
    print("dish photos:", got, "planned:", n, "OK" if ok else "PROBLEM")
    sys.exit(0 if ok else 1)
