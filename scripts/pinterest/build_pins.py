#!/usr/bin/env python3
"""Pinterest pin generator for the cruise money pages (TCD + BPA).

Renders 1000x1500 pins from an HTML template with Playwright and writes a
Pinterest bulk-upload CSV next to them.

  python3 scripts/pinterest/build_pins.py [--out DIR] [--only SLUG]

Photos: only first-party photos hosted under /assets on our own sites (lead
photo of the tested cards), never OTA CDN images. Pages without usable photos
get a typographic pin.
Copy: no em dashes, claim "tested" only where the page title claims it.
"""
import argparse
import base64
import csv
import html
import mimetypes
import re
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[2]
BPA_ROOT = Path.home() / "Development" / "budapest-adventures"
UTM = "utm_source=pinterest&utm_medium=social&utm_campaign=pin_test_2026"

SITES = {
    "tcd": {"root": ROOT, "domain": "thecruisedetective.com", "brand": "The Cruise Detective",
            "bg": "#0f2238", "accent": "#dfa732"},
    "bpa": {"root": BPA_ROOT, "domain": "budapestadventures.com", "brand": "Budapest Adventures",
            "bg": "#13283d", "accent": "#e8b04b"},
}

# (page file, pin index) -> (bullets or None, photo). photo: filename substring
# of an /assets/cdn image on that page, "none" for a typographic pin, None = auto.
# Photos are hand-picked: /assets/cdn also holds some operator promo shots
# (yacht models, aerials, logos) that must never be pinned.
OVERRIDES = {
    ("seine-river-cruises-paris/index.html", 0): (["Bateaux Parisiens: best overall", "Bateaux Mouches: runner-up", "Vedettes de Paris: best music and vibe"], None),
    ("seine-river-cruises-paris/index.html", 2): (["Batobus: best hop-on hop-off", "Canal Saint-Martin: best locks cruise", "Private yacht with champagne"], None),
    ("dinner-cruises-paris/index.html", 0): (["Bateaux Mouches: best overall", "Bateaux Parisiens: runner-up", "La Marina: top value"], None),
    ("dinner-cruises-paris/index.html", 2): (["La Marina: top value", "Paris en Scène: best budget", "Le Diamant Bleu: best party"], None),
    ("private-cruises-paris/index.html", 0): (["Small boat with champagne", "Rosé and macarons for couples", "2 hours with a skipper-guide"], "none"),
    ("private-cruises-paris/index.html", 1): (None, "none"),
    ("private-cruises-paris/index.html", 2): (["Electric pontoon for 6", "Live guide on board", "Limousine boat for up to 12"], "none"),
    ("canal-cruises-amsterdam/index.html", 0): (["Captain Jack: best overall", "Lover's: best sightseeing value", "Flagship: best open boat"], None),
    ("canal-cruises-amsterdam/index.html", 2): (["Blue Boat: best heated classic", "Friendship: best luxury salon", "Best Light Festival cruise"], None),
    ("thames-river-cruises-london/index.html", 0): (["Westminster to Greenwich", "London Eye 45-minute loop", "24-hour hop-on hop-off"], None),
    ("thames-river-cruises-london/index.html", 2): (["Thames Rockets speedboat", "Speedboat to the Thames Barrier", "2-course lunch from Tower Bridge"], None),
    ("best-budapest-river-cruises.html", 0): (["Legenda: best overall", "Best unlimited drinks cruise", "Best historic paddle steamer"], "legenda-sightseeing-cruise-00025"),
    ("best-budapest-river-cruises.html", 1): (None, "portum-14"),
    ("best-budapest-river-cruises.html", 2): (["Unlimited drinks on the Danube", "Historic paddle steamer", "Best budget value"], "paddle steam cruise (15)"),
    ("best-night-cruises-budapest.html", 0): (None, "legenda-17"),
    ("best-night-cruises-budapest.html", 1): (None, "portum-21"),
    ("best-night-cruises-budapest.html", 2): (None, "portum-14"),
    ("best-private-boat-tours-budapest.html", 0): (None, "1-private-boat-cruise-1-hour"),
    ("best-private-boat-tours-budapest.html", 1): (None, "none"),
    ("best-private-boat-tours-budapest.html", 2): (None, "none"),
    ("unlimited-prosecco-cruises-budapest.html", 0): (["Best overall value", "Sunset and photo cruise", "Budget food and drinks"], "best-unlimited-prosecco-cruises-hero"),
    ("unlimited-prosecco-cruises-budapest.html", 1): (None, "portum-16"),
    ("unlimited-prosecco-cruises-budapest.html", 2): (["Pizza and drinks on a budget", "Late-night DJ party", "Daytime gourmet brunch"], "cocktail-pizza-drinks-cruise-6"),
}

# Each page: 3 pins.
PAGES = [
    {"site": "tcd", "file": "seine-river-cruises-paris/index.html", "board": "Paris Seine Cruises",
     "pins": [
         {"kicker": "Paris 2026 · Top 5 personally tested", "head": "11 Best Seine River Cruises in Paris",
          "bullets": "ranks:0-3",
          "title": "11 Best Seine River Cruises in Paris (2026, Top 5 Tested)",
          "desc": "Which Seine cruise should you book? We rode the top 5 ourselves and ranked all 11 side by side: route, audio guide, departure pier, wheelchair access and real review scores from 4 booking sites. Bateaux Parisiens, Bateaux Mouches, Vedettes de Paris, Batobus and more. #paris #seine #parisitinerary #paristravel"},
         {"kicker": "Before you book a Seine cruise", "head": "Which Paris river cruise is actually worth it?",
          "bullets": ["11 cruises compared side by side", "Piers, routes and audio guides", "Review scores from 4 sites"],
          "title": "Which Seine River Cruise in Paris Is Worth It? 11 Compared",
          "desc": "One-hour sightseeing loop, hop-on hop-off Batobus, canal and locks, lunch cruise or private yacht? Our comparison shows which Paris cruise fits your trip, where each one leaves from and what reviewers really say. #parisvacation #seinecruise #thingstodoinparis"},
         {"kicker": "Seine cruises by trip style", "head": "The best Paris boat ride for every kind of trip",
          "bullets": "ranks:3-7",
          "title": "Best Paris Boat Ride for Every Trip: Hop-On, Canal, Private, Lunch",
          "desc": "Not every Seine cruise suits every traveler. Find the best hop-on hop-off boat, the best canal and locks cruise, the best live-guide boat and the best private yacht in Paris, ranked in one place. #paris #parisboat #europetravel"},
     ]},
    {"site": "tcd", "file": "dinner-cruises-paris/index.html", "board": "Paris Dinner Cruises",
     "pins": [
         {"kicker": "Paris 2026 · Top 5 personally tested", "head": "10 Best Dinner Cruises in Paris",
          "bullets": "ranks:0-3",
          "title": "10 Best Seine Dinner Cruises in Paris (2026, Top 5 Tested)",
          "desc": "Planning a dinner cruise on the Seine? We dined on the top 5 ourselves and compared all 10: menu, live music, window seats, dress code and real review scores. Bateaux Mouches, Bateaux Parisiens, Le Diamant Bleu and more. #parisdinner #seine #parisromance #paristravel"},
         {"kicker": "Before you book a Seine dinner cruise", "head": "Which Paris dinner cruise is worth the money?",
          "bullets": ["10 dinner cruises compared", "Menus, music and seating", "From budget bistro to gourmet"],
          "title": "Which Paris Dinner Cruise Is Worth the Money? 10 Compared",
          "desc": "Gourmet 4-course menu, budget bistro boat or party lounge with a DJ? See which Seine dinner cruise matches your evening, what is on the menu and which seats get the Eiffel Tower view. #parisdinnercruise #romanticparis #parisnight"},
         {"kicker": "Seine dinner cruises by style", "head": "Romantic, budget or party: pick your Paris dinner cruise",
          "bullets": "ranks:2-6",
          "title": "Best Paris Dinner Cruise for Couples, Budgets and Parties",
          "desc": "Top value, best budget pick, best party and lounge boat, best Italian-style menu: our Paris dinner cruise ranking sorts every boat by the kind of night you want. #parisanniversary #parisdate #seinedinner"},
     ]},
    {"site": "tcd", "file": "private-cruises-paris/index.html", "board": "Paris Seine Cruises",
     "pins": [
         {"kicker": "Paris 2026", "head": "The 6 Best Private Cruises in Paris",
          "bullets": "ranks:0-3",
          "title": "The 6 Best Private Seine Cruises in Paris (2026)",
          "desc": "A whole boat for just your group: champagne, rosé and macarons, a live guide or two hours on the water. We compared 6 private Seine cruises for couples, proposals and groups up to 12. #parisproposal #privatecruise #parishoneymoon"},
         {"kicker": "Planning a proposal in Paris?", "head": "Private Seine cruises for couples and proposals",
          "bullets": ["Small boats, just the two of you", "Champagne or rosé on board", "Sunset and Eiffel Tower timing"],
          "title": "Private Seine Cruise for a Paris Proposal: 6 Best Boats",
          "desc": "Want to propose on the Seine? These private small-boat cruises give you the river to yourselves, with bubbles on board and departures timed for the Eiffel Tower sparkle. #parisproposal #proposalideas #romanticparis"},
         {"kicker": "Private boats by group size", "head": "Private Paris boats for 2 to 12 people",
          "bullets": "ranks:2-6",
          "title": "Private Paris Boat Hire for Groups: 6 Seine Cruises Compared",
          "desc": "Birthday, family or friends trip? Compare private Seine boats by group size, pier, time on the water and what is included, from a 6-person electric pontoon to a limousine boat for 12. #parisbirthday #parisgroup #seine"},
     ]},
    {"site": "tcd", "file": "canal-cruises-amsterdam/index.html", "board": "Amsterdam Canal Cruises",
     "pins": [
         {"kicker": "Amsterdam 2026 · Top 5 personally tested", "head": "10 Best Canal Cruises in Amsterdam",
          "bullets": "ranks:0-3",
          "title": "10 Best Amsterdam Canal Cruises (2026, Top 5 Tested)",
          "desc": "Which Amsterdam canal cruise should you book? We sailed the top 5 ourselves and ranked all 10: open boat or heated salon, unlimited drinks or sightseeing only, and real review scores. #amsterdam #amsterdamcanals #amsterdamtravel"},
         {"kicker": "Before you book a canal cruise", "head": "Which Amsterdam canal cruise is worth it?",
          "bullets": ["10 canal cruises compared", "Open boats vs glass-top salons", "Drinks, cheese and light festival"],
          "title": "Which Amsterdam Canal Cruise Is Worth It? 10 Compared",
          "desc": "Small open sloop with unlimited drinks, classic glass-top boat or a light festival cruise? Our comparison shows which Amsterdam canal cruise fits your trip and what reviewers really say. #amsterdamtrip #canalcruise #netherlands"},
         {"kicker": "Canal cruises by trip style", "head": "The best Amsterdam canal cruise for every trip",
          "bullets": "ranks:3-7",
          "title": "Best Amsterdam Canal Cruise for Every Trip: Heated, Luxury, Party",
          "desc": "Cold day, special occasion or night out with friends? Find the best heated classic boat, the best luxury salon, the Light Festival cruise and the best social drinks cruise in Amsterdam. #amsterdam #amsterdamnightlife #europetravel"},
     ]},
    {"site": "tcd", "file": "thames-river-cruises-london/index.html", "board": "London Thames Cruises",
     "pins": [
         {"kicker": "London 2026 · Personally tested", "head": "10 Best Thames River Cruises in London",
          "bullets": "ranks:0-3",
          "title": "10 Best Thames River Cruises in London (2026, Tested)",
          "desc": "Which Thames cruise should you book? We compared 10 side by side: Westminster to Greenwich, London Eye loop, hop-on hop-off, speedboats and dinner cruises, with real review scores. #london #thames #londontravel #thingstodoinlondon"},
         {"kicker": "Before you book a Thames cruise", "head": "Which London river cruise is actually worth it?",
          "bullets": ["10 Thames cruises compared", "Sightseeing, speedboat or dinner", "Piers and live commentary"],
          "title": "Which Thames River Cruise in London Is Worth It? 10 Compared",
          "desc": "Live-commentary sightseeing boat, 24-hour hop-on hop-off, a speedboat thrill ride or a jazz dinner cruise? See which Thames cruise fits your London trip and where each one leaves from. #londontrip #thamescruise #uktravel"},
         {"kicker": "Thames cruises by trip style", "head": "Speedboats, lunch and dinner cruises on the Thames",
          "bullets": "ranks:3-7",
          "title": "Best Thames Speedboat, Lunch and Evening Cruises in London",
          "desc": "Thames Rockets from the London Eye, a two-course lunch from Tower Bridge or sparkling wine at sunset: the best London river experiences by trip style, ranked. #london #londonbucketlist #thames"},
     ]},
    {"site": "bpa", "file": "best-budapest-river-cruises.html", "board": "Budapest Danube Cruises",
     "pins": [
         {"kicker": "Budapest 2026 · Personally tested", "head": "10 Best River Cruises in Budapest",
          "bullets": "ranks:0-3",
          "title": "10 Best Danube River Cruises in Budapest (2026, Tested)",
          "desc": "Which Danube cruise should you book in Budapest? We compared 10 side by side: sightseeing with audio guide, unlimited prosecco, a historic paddle steamer and budget boats, with real review scores. #budapest #danube #budapesttravel"},
         {"kicker": "Before you book a Danube cruise", "head": "Which Budapest river cruise is actually worth it?",
          "bullets": ["10 Danube cruises compared", "Parliament views by night", "Drinks, steamer or budget boat"],
          "title": "Which Budapest River Cruise Is Worth It? 10 Danube Cruises Compared",
          "desc": "Day or night? Drinks included or sightseeing only? Our Budapest cruise comparison shows which Danube boat fits your trip, where it leaves from and what reviewers really say. #budapestnight #danubecruise #hungary"},
         {"kicker": "Danube cruises by trip style", "head": "The best Budapest cruise for every kind of trip",
          "bullets": "ranks:1-5",
          "title": "Best Budapest Cruise for Every Trip: Drinks, Steamer, Budget",
          "desc": "Unlimited drinks, a historic steamer, the best budget value or a central no-frills boat: find the right Danube cruise for your Budapest trip in one ranking. #budapest #budapestitinerary #europetravel"},
     ]},
    {"site": "bpa", "file": "best-dinner-cruises-budapest.html", "board": "Budapest Danube Cruises",
     "pins": [
         {"kicker": "Budapest 2026 · Personally tested", "head": "6 Best Dinner Cruises in Budapest",
          "bullets": ["6 Danube dinner cruises ranked", "Menus, live music and views", "Top 3 tested in person"],
          "title": "6 Best Danube Dinner Cruises in Budapest (2026, Tested)",
          "desc": "Planning a dinner cruise on the Danube? We compared 6 Budapest dinner cruises: menu, live music, window seats and the lit-up Parliament. The top 3 we tested in person. #budapestdinner #danube #romanticbudapest"},
         {"kicker": "Before you book a Danube dinner", "head": "Which Budapest dinner cruise is worth it?",
          "bullets": ["Candlelit, buffet or concert", "Parliament lit up at night", "From budget to gourmet"],
          "title": "Which Budapest Dinner Cruise Is Worth It? 6 Compared",
          "desc": "Candlelit dinner, buffet with live music or a concert cruise? See which Danube dinner cruise fits your evening in Budapest and what is on the menu. #budapestnight #danubedinner #hungarytravel"},
         {"kicker": "Romantic night in Budapest", "head": "Danube dinner cruises for couples",
          "bullets": ["Candlelit tables by the window", "Live music on board", "Night views of the Parliament"],
          "title": "Romantic Danube Dinner Cruise in Budapest: Best Picks for Couples",
          "desc": "Anniversary, honeymoon or a date night in Budapest? These Danube dinner cruises give you candlelight, live music and the Parliament glowing over the river. #budapestromance #anniversaryideas #budapest"},
     ]},
    {"site": "bpa", "file": "best-night-cruises-budapest.html", "board": "Budapest Danube Cruises",
     "pins": [
         {"kicker": "Budapest · Personally tested", "head": "10 Best Night Cruises in Budapest",
          "bullets": ["Sightseeing by night", "Booze cruise and drinks boats", "Best value evening cruise"],
          "title": "10 Best Evening and Night Cruises in Budapest (Tested)",
          "desc": "Budapest is at its best after dark. We compared 10 evening and night cruises on the Danube: sightseeing boats, booze cruises and best-value picks, with real review scores. #budapestnight #danube #budapest"},
         {"kicker": "Budapest after dark", "head": "Which Budapest night cruise is worth it?",
          "bullets": ["Parliament and bridges lit up", "Drinks included or not", "Departure piers compared"],
          "title": "Which Budapest Night Cruise Is Worth It? 10 Compared",
          "desc": "The lit-up Parliament, Chain Bridge and Buda Castle from the water: see which Danube night cruise fits your trip, whether drinks are included and where it leaves from. #budapestatnight #danubecruise #hungary"},
         {"kicker": "Budapest bucket list", "head": "See Budapest lit up from the Danube",
          "bullets": ["10 night cruises ranked", "Sightseeing, drinks or party", "Real review scores"],
          "title": "See Budapest Lit Up: Best Danube Night Cruises",
          "desc": "The single best view of Budapest is from the river at night. Our ranking of 10 Danube night cruises helps you pick the right boat, from a calm sightseeing loop to a booze cruise. #budapestbucketlist #budapest #europetravel"},
     ]},
    {"site": "bpa", "file": "best-private-boat-tours-budapest.html", "board": "Budapest Danube Cruises",
     "pins": [
         {"kicker": "Budapest 2026", "head": "The 5 Best Private Boat Tours in Budapest",
          "bullets": ["Your own boat on the Danube", "Luxury yachts and water limos", "Drinks packages compared"],
          "title": "The 5 Best Private Boat Tours in Budapest (2026)",
          "desc": "A whole boat for your group on the Danube: luxury yachts, water limousines and unlimited drinks options. We compared 5 private boat tours in Budapest for couples, families and groups. #budapest #privateboat #danube"},
         {"kicker": "Planning a proposal in Budapest?", "head": "Private Danube boats for couples",
          "bullets": ["Just the two of you", "Parliament views at sunset", "Bubbles on board"],
          "title": "Private Danube Boat Tour for a Budapest Proposal",
          "desc": "Want to propose in Budapest? A private boat on the Danube gives you the river to yourselves, the Parliament lit up and a toast on board. Compare 5 private boat tours. #budapestproposal #proposalideas #budapest"},
         {"kicker": "Group trip to Budapest?", "head": "Private Budapest boats for groups and parties",
          "bullets": ["Bachelor and birthday groups", "Unlimited drinks options", "Pickup piers compared"],
          "title": "Private Budapest Boat Party for Groups: 5 Danube Boats Compared",
          "desc": "Birthday, bachelor party or friends trip: compare private Danube boats in Budapest by group size, drinks package and pier, and book the whole boat for your crew. #budapestbachelor #budapestparty #danube"},
     ]},
    {"site": "bpa", "file": "unlimited-prosecco-cruises-budapest.html", "board": "Budapest Danube Cruises",
     "pins": [
         {"kicker": "Budapest 2026", "head": "6 Best Unlimited Prosecco Cruises in Budapest",
          "bullets": "ranks:0-3",
          "title": "6 Best Unlimited Prosecco Cruises in Budapest (2026)",
          "desc": "Unlimited prosecco on the Danube: we compared 6 Budapest drinks cruises side by side, from best overall value to sunset photo boats, budget food and drinks and a late-night DJ party. #budapest #prosecco #danube"},
         {"kicker": "Sunset in Budapest", "head": "Unlimited prosecco at sunset on the Danube",
          "bullets": ["Sunset and photo cruises", "Drinks included, no bar tab", "Parliament views"],
          "title": "Unlimited Prosecco Sunset Cruise in Budapest: Best Picks",
          "desc": "Golden hour on the Danube with a glass that keeps getting refilled. See which Budapest prosecco cruise gives you the best sunset, the best value and the best views of the Parliament. #budapestsunset #budapest #girlstrip"},
         {"kicker": "Prosecco cruises by style", "head": "Brunch, party or sunset: pick your prosecco cruise",
          "bullets": "ranks:2-6",
          "title": "Budapest Prosecco Cruise: Brunch, Party or Sunset?",
          "desc": "A daytime gourmet brunch, a late-night DJ party or dinner with an open bar: Budapest unlimited drinks cruises sorted by the kind of day or night you want. #budapestnightlife #brunch #budapest"},
     ]},
]

EMOJI = re.compile(r"[\U0001F000-\U0001FAFF☀-➿️]")


def clean_rank(text):
    text = EMOJI.sub("", text)
    text = re.sub(r"#\d+\s*", "", text).strip(" ·-")
    text = re.sub(r"\s+", " ", text)
    if text.isupper():
        text = text.title().replace("Bbq", "BBQ")
    return text[:1].upper() + text[1:]


def page_info(site, file):
    path = SITES[site]["root"] / file
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    canon = soup.find("link", rel="canonical")["href"]
    ranks, photos = [], []
    for card in soup.select(".bpa-card"):
        r = card.select_one(".bpa-rank") or card.select_one("[class*=rank]")
        ranks.append(clean_rank(r.get_text(" ", strip=True)) if r else "")
        tested = bool(card.select_one(".bpa-tested")) or "tested" in (card.get("data-cat") or "")
        for img in card.find_all("img"):
            src = img.get("data-src") or img.get("src") or ""
            # /assets/cdn = our own Webflow-era uploads; /assets/<page>/ holds
            # galleries copied from operator listings, never pinned.
            if src.startswith("/assets/cdn/") and "portrait" not in src.lower() \
                    and not src.endswith((".svg", ".png")):
                photos.append((tested, src))
                break
    photos.sort(key=lambda t: not t[0])
    every = sorted({m for m in re.findall(r'/assets/cdn/[^"\s,]+\.(?:webp|avif|jpe?g)', str(soup))
                    if not re.search(r"-p-\d+\.", m)})
    return canon, ranks, [p for _, p in photos], every


def data_uri(site, src):
    f = SITES[site]["root"] / unquote(src.split("?")[0]).lstrip("/")
    if not f.exists():
        return None
    mime = mimetypes.guess_type(f.name)[0] or ("image/avif" if f.suffix == ".avif" else "image/webp")
    return f"data:{mime};base64," + base64.b64encode(f.read_bytes()).decode()


TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@500;600;700&display=block" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1000px;height:1500px;background:{bg};font-family:Inter,sans-serif;color:#fff;overflow:hidden;position:relative}}
.photo{{position:absolute;inset:0 0 auto 0;height:860px;background:{photo} center/cover no-repeat}}
.photo:after{{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.05) 40%,{bg} 100%)}}
.typo{{position:absolute;inset:0 0 auto 0;height:860px;background:radial-gradient(circle at 30% 30%,#1f3d5e,{bg} 70%)}}
.typo:before{{content:"";position:absolute;left:80px;right:80px;top:120px;height:6px;background:{accent}}}
.content{{position:absolute;left:70px;right:70px;bottom:150px}}
.kicker{{display:inline-block;background:{accent};color:{bg};font-weight:700;font-size:30px;padding:12px 24px;border-radius:8px;margin-bottom:30px}}
h1{{font-family:'Playfair Display',serif;font-weight:800;font-size:{hsize}px;line-height:1.08;margin-bottom:38px}}
ul{{list-style:none}}
li{{font-size:36px;font-weight:600;padding:14px 0 14px 56px;position:relative;border-top:1px solid rgba(255,255,255,.18)}}
li:before{{content:"✓";position:absolute;left:0;top:12px;color:{accent};font-weight:700}}
.foot{{position:absolute;left:0;right:0;bottom:0;height:110px;background:rgba(0,0,0,.28);display:flex;align-items:center;justify-content:space-between;padding:0 70px;font-size:30px}}
.foot b{{color:{accent};font-weight:700}}
</style></head><body>
{visual}
<div class="content"><div class="kicker">{kicker}</div><h1>{head}</h1><ul>{bullets}</ul></div>
<div class="foot"><span>{brand}</span><b>{domain} →</b></div>
</body></html>"""


def build(out, only=None):
    from playwright.sync_api import sync_playwright
    out.mkdir(parents=True, exist_ok=True)
    rows, used = [], set()
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1000, "height": 1500})
        for cfg in PAGES:
            slug = Path(cfg["file"]).parent.name if cfg["file"].endswith("index.html") else Path(cfg["file"]).stem
            if only and slug != only:
                continue
            site = SITES[cfg["site"]]
            canon, ranks, photos, every = page_info(cfg["site"], cfg["file"])
            for i, pin in enumerate(cfg["pins"]):
                o_bullets, o_photo = OVERRIDES.get((cfg["file"], i), (None, None))
                bullets = o_bullets or pin["bullets"]
                if isinstance(bullets, str):
                    a, b = map(int, bullets.split(":")[1].split("-"))
                    bullets = [r for r in ranks[a:b] if r]
                if o_photo == "none":
                    photo = None
                elif o_photo:
                    photo = next(p for p in every if o_photo in unquote(p))
                else:
                    photo = next((p for p in photos if p not in used), None)
                uri = data_uri(cfg["site"], photo) if photo else None
                if uri:
                    used.add(photo)
                visual = (f'<div class="photo" style="background-image:url({uri})"></div>' if uri
                          else '<div class="typo"></div><style>.content{top:300px;bottom:auto}'
                               'h1{font-size:104px!important;margin-bottom:70px}'
                               'li{font-size:42px;padding:22px 0 22px 60px}.kicker{font-size:34px}</style>')
                head = pin["head"]
                doc = TEMPLATE.format(
                    bg=site["bg"], accent=site["accent"], photo="none",
                    hsize=84 if len(head) < 40 else 72 if len(head) < 52 else 64,
                    visual=visual, kicker=html.escape(pin["kicker"]), head=html.escape(head),
                    bullets="".join(f"<li>{html.escape(x)}</li>" for x in bullets[:3]),
                    brand=site["brand"], domain=site["domain"])
                for txt in (pin["title"], pin["desc"], pin["kicker"], head, *bullets):
                    assert "—" not in txt, f"em dash in {slug}: {txt}"
                name = f"{cfg['site']}-{slug}-{i + 1}.png"
                page.set_content(doc, wait_until="networkidle")
                page.screenshot(path=str(out / name))
                rows.append({"file": name, "Title": pin["title"][:100], "Description": pin["desc"][:500],
                             "Link": f"{canon}?{UTM}&utm_content={slug}-{i + 1}",
                             "Pinterest board": cfg["board"], "photo": photo if uri else "typographic"})
                print("rendered", name)
        browser.close()
    with open(out / "pins.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} pins -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "reports" / "pinterest")
    ap.add_argument("--only")
    a = ap.parse_args()
    build(a.out, a.only)
