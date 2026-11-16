#!/usr/bin/env python3
"""Build /budapest-amsterdam-river-cruises (EN) from the private-cruises-paris template,
with the Seine page's card features (rating popover, pill dropdowns, Pick/Skip).

    python3 scripts/build_budapest_amsterdam.py
    python3 scripts/sync_layout.py

Multi-day river cruises, booked through the TourRadar affiliate program
(utm_source=partner-traveller-1464745). Facts come from the live TourRadar tour
pages, checked 2026-11-16 (prices per person, 2 adults sharing, cheapest cabin,
in US$). Ratings on TourRadar tour pages are the operator's rating.
Edit the PRODUCTS data below, re-run, then run scripts/sync_layout.py.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.thecruisedetective.com"
TEMPLATE = ROOT / "private-cruises-paris" / "index.html"
SEINE = ROOT / "seine-river-cruises-paris" / "index.html"
SLUG = "budapest-amsterdam-river-cruises"
ASSET = f"/assets/{SLUG}"
DATE_ISO = "2026-11-16T12:00:00+01:00"
CHECKED = "Nov 16, 2026"
TR_PARTNER = "partner-traveller-1464745"


def tr(tour_id, key):
    return (f"https://www.tourradar.com/t/{tour_id}?utm_source={TR_PARTNER}"
            f"&utm_medium=ambassador&utm_campaign=tcd-bud-ams-{key}")


# ---------------------------------------------------------------------------
# DATA (TourRadar tour pages, 16 Nov 2026; US$ per person, cheapest cabin, 2 sharing)
# rating: (score, count or None); count None = operator rating without a count shown
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "key": "emerald-splendours", "tour": 342309, "photos": 7, "cats": "tips under5k",
        "operator": "Emerald Cruises", "days": 15, "price": 3976,
        "rating": (4.1, 40), "dir": "Budapest → Amsterdam",
        "rank": "🏆 #1 Best Value Overall", "gold": True,
        "short": "Emerald: Early Season Splendours",
        "title": "Early Season Splendours of Europe: 15 Days, Budapest to Amsterdam",
        "pills": [
            ("💵", "Tips + Transfers Included",
             "<strong>The fare already covers all tipping and gratuities</strong>, airport transfers to and from the ship, port taxes and an Emerald cruise director.",
             "Most lines at this price leave crew tips to you, so the real gap to #2 is bigger than the fares suggest."),
            ("🍷", "Wine &amp; Beer with Meals",
             "<strong>14 breakfasts, 13 lunches and 14 dinners</strong>, with complimentary wine, beer and soft drinks at lunch and dinner on board.",
             "Bar drinks outside meal times cost extra."),
            ("📅", "Late Feb Is Cheapest",
             "<strong>From $3,976</strong> for the late-February sailings (22 Feb 2027 is $4,129, 18 Feb 2028 is $4,027).",
             "The same itinerary in the other direction (Amsterdam to Budapest) starts at $3,163 on 20 Feb 2027 and climbs past $7,000 in May."),
        ],
        "pick": "for the lowest real price on the full route, with tips, transfers and dinner wine already paid.",
        "skip": "if you want May or June sailings at this price: late winter is what makes it cheap.",
        "pros": ["<strong>Tips, transfers and port taxes included</strong>, so there is little to add at the end.",
                 "<strong>Guided e-bike tours</strong> in Vienna, along the Danube and to Waterland, on top of the city walks.",
                 "<strong>From $3,976 for 15 days</strong>, about $265 per day with 41 meals."],
        "cons": ["<strong>The cheapest dates are February and March</strong>, when the vineyards are bare.",
                 "<strong>Big ship</strong>: up to 182 guests on the Emerald Star-Ships.",
                 "<strong>Drinks only with meals</strong>, not all day like #3 and #4."],
        "review": ["This is the cheapest way to sail the whole Danube, Main and Rhine without paying extra at the end. Emerald's <strong>Early Season Splendours of Europe</strong> leaves Budapest in late February and reaches Amsterdam 15 days later on the <strong>Emerald Sky</strong>, stopping in Bratislava, Vienna, Dürnstein and Melk, Passau, Regensburg, Nuremberg, Bamberg, Würzburg, Miltenberg, Rüdesheim and Cologne.",
                   "The fare includes <strong>all tipping and gratuities</strong>, airport transfers and port taxes, plus wine, beer and soft drinks with lunch and dinner. That is why it beats the slightly cheaper-looking #2: once you add tips there, Emerald is the better deal. Prefer to finish in Budapest? The <a href=\"" + "TR_REVERSE" + "\" rel=\"nofollow sponsored noopener\" target=\"_blank\">same cruise in reverse</a> starts at <strong>$3,163</strong> on 20 Feb 2027."],
        "facts": [("Duration", "15 days, 14 nights on board"),
                  ("Route", "Budapest, Bratislava, Vienna, Dürnstein, Melk, Passau, Regensburg, Nuremberg, Bamberg, Würzburg, Miltenberg, Rüdesheim, Cologne, Amsterdam"),
                  ("Ship", "Emerald Sky (180 guests)"),
                  ("Included", "14 breakfasts, 13 lunches, 14 dinners; wine, beer and soft drinks with lunch and dinner; all tips; airport transfers; port taxes; guided tours and e-bike tours"),
                  ("Not included", "Flights, travel insurance, optional excursions"),
                  ("Minimum age", "12"),
                  ("Prices seen", "22 Feb 2027: $4,129 • 18 Feb 2028: $4,027 • 2 Mar 2028: $4,498")],
    },
    {
        "key": "lueftner-amadeus", "tour": 339822, "photos": 4, "cats": "under5k family",
        "operator": "Lueftner Cruises", "days": 15, "price": 3941,
        "rating": (4.5, 220), "dir": "Amsterdam → Budapest",
        "rank": "☀️ #2 Best Value for Summer",
        "short": "Lueftner: Across Europe (AMADEUS)",
        "title": "Across Europe on the AMADEUS Mira: 15 Days, Amsterdam to Budapest",
        "pills": [
            ("☀️", "Cheapest in August",
             "<strong>From $3,941 on 19 Aug 2027</strong>, the lowest summer fare on the route.",
             "May 2027 departures are $4,637 (8 May) and $5,880 (17 May)."),
            ("🍷", "Wine &amp; Beer with Meals",
             "<strong>Gourmet breakfast, multi-course lunches and dinners</strong>, with quality wine and beer included at lunch and dinner.",
             "Free Wi-Fi, a 24/7 coffee station and bicycles for your own use."),
            ("💵", "Tips Not Included",
             "<strong>Crew and guide tips are not in the fare</strong>; the listing calls them discretionary.",
             "Budget for them on top of the fare when you compare it with #1."),
        ],
        "pick": "for a summer sailing under $4,000 on a new ship, starting in Amsterdam.",
        "skip": "if you want to start in Budapest, or want tips and transfers included like #1.",
        "pros": ["<strong>Best-rated operator here</strong>: 4.5 from 220 reviews.",
                 "<strong>Under $4,000 in August</strong>, when the others cost $5,500 to $9,000.",
                 "<strong>AMADEUS Mira</strong>, the newest ship in the Lüftner fleet, with e-bike tours included."],
        "cons": ["<strong>Tips not included.</strong>",
                 "<strong>Partially guided</strong>: some free time where others run a guided tour.",
                 "<strong>Runs Amsterdam to Budapest</strong> only in this listing."],
        "review": ["Austrian family company Lüftner (sold as Lueftner Cruises) is the value pick if you can only travel in summer. Its <strong>Across Europe</strong> cruise sails from Amsterdam via Utrecht, Cologne, Rüdesheim, Würzburg, Bamberg, Nuremberg, Regensburg, Passau, Dürnstein, Vienna and Bratislava to Budapest on the <strong>AMADEUS Mira</strong>.",
                   "The operator rates <strong>4.5 from 220 reviews</strong>, the best score in this comparison, and the <strong>19 Aug 2027</strong> departure is <strong>$3,941</strong>. Wine and beer come with lunch and dinner, Wi-Fi and bikes are free, and there are e-bike tours along the Danube and to Klosterneuburg Abbey. Tips are extra, so add them before comparing it with #1."],
        "facts": [("Duration", "15 days"),
                  ("Route", "Amsterdam, Utrecht, Cologne, Rüdesheim, Miltenberg, Wertheim, Würzburg, Bamberg, Nuremberg, Regensburg, Passau, Dürnstein, Vienna, Bratislava, Budapest"),
                  ("Ship", "AMADEUS Mira"),
                  ("Included", "Full board; wine and beer with lunch and dinner; Wi-Fi; bicycles; e-bike tours; city tours"),
                  ("Not included", "Tips for crew and guides, flights, insurance"),
                  ("Minimum age", "8"),
                  ("Prices seen", "8 May 2027: $4,637 • 17 May 2027: $5,880 • 19 Aug 2027: $3,941")],
    },
    {
        "key": "scenic-jewels", "tour": 344472, "photos": 7, "cats": "allinc tips",
        "operator": "Scenic", "days": 15, "price": 5244,
        "rating": (4.4, 47), "dir": "Budapest → Amsterdam",
        "rank": "🥂 #3 Best All-Inclusive",
        "short": "Scenic: Jewels of Europe",
        "title": "Jewels of Europe: 15 Days, Budapest to Amsterdam, Everything Included",
        "pills": [
            ("🥂", "Drinks All Day",
             "<strong>Premium drinks all day, every day</strong>, not just with meals, plus 14 breakfasts, 13 lunches and 14 dinners.",
             "Free Wi-Fi and e-bikes for exploring on your own."),
            ("💵", "Tips + Transfers Included",
             "<strong>All tipping and gratuities on board and onshore</strong> and return airport transfers are in the fare.",
             None),
            ("📅", "Only One Cheap Date",
             "<strong>$5,244 is the 22 Feb 2027 departure.</strong> The next ones are $9,933 (9 Mar) and $9,321 (23 Mar).",
             "If February doesn't work, #4 is cheaper than Scenic in spring."),
        ],
        "pick": "if you want every drink, tip and transfer covered and can sail on 22 February 2027.",
        "skip": "if you need a spring date: Scenic jumps to over $9,000 from March.",
        "pros": ["<strong>Truly all-inclusive</strong>: drinks all day, tips, transfers, Wi-Fi.",
                 "<strong>Balcony Suites with butler service</strong> on the upper categories.",
                 "<strong>Adults only</strong> (18+), so a quieter ship."],
        "cons": ["<strong>The $5,244 fare is a single date</strong>; most departures are $9,000+.",
                 "<strong>No children</strong> under 18.",
                 "<strong>Late-winter weather</strong> on the cheapest sailing."],
        "review": ["Scenic sells itself as the all-inclusive line, and on this route it delivers: <strong>premium drinks all day</strong>, all tips on board and ashore, return airport transfers and free Wi-Fi are in the fare, and you get e-bikes to explore on your own. The ships take up to 163 guests and the upper Balcony Suites come with a butler.",
                   "The catch is the price calendar. <strong>$5,244</strong> is the <strong>22 February 2027</strong> sailing; in March it is <strong>$9,321 to $9,933</strong>. If you can take that February date, it is the best-value luxury cruise on the route. If not, compare it with #4, which costs less than Scenic in spring and includes spirits too."],
        "facts": [("Duration", "15 days"),
                  ("Route", "Budapest, Vienna, Krems, Dürnstein, Passau, Regensburg, Nuremberg, Bamberg, Würzburg, Wertheim, Miltenberg, Koblenz, Rhine Gorge, Bonn, Cologne, Amsterdam"),
                  ("Ship", "Scenic Space-Ships, up to 163 guests"),
                  ("Included", "14 breakfasts, 13 lunches, 14 dinners; premium drinks all day; all tips on board and onshore; return airport transfers; Wi-Fi; e-bikes"),
                  ("Not included", "Flights, travel insurance"),
                  ("Minimum age", "18"),
                  ("Prices seen", "22 Feb 2027: $5,244 • 9 Mar 2027: $9,933 • 23 Mar 2027: $9,321")],
    },
    {
        "key": "uniworld-european-jewels", "tour": 326678, "photos": 7, "cats": "allinc tips",
        "operator": "Uniworld", "days": 15, "price": 8711,
        "rating": (4.6, 97), "dir": "Budapest → Amsterdam",
        "rank": "✨ #4 Best Boutique Ship",
        "short": "Uniworld: European Jewels",
        "title": "European Jewels on the S.S. Marlene: 15 Days, Budapest to Amsterdam",
        "pills": [
            ("🍸", "Unlimited Drinks + Spirits",
             "<strong>Unlimited drinks on board</strong>, including fine wine, beer, spirits, specialty coffee and soft drinks.",
             "All meals on board are included."),
            ("💵", "Tips Included",
             "<strong>Gratuities for the ship staff, crew and cruise manager are included</strong>, and Wi-Fi is free.",
             None),
            ("🏰", "Heidelberg + Rothenburg",
             "<strong>The only route here with Heidelberg and Rothenburg</strong>, via a Frankfurt stop, on top of the usual Vienna, Nuremberg and Cologne.",
             None),
        ],
        "pick": "for a boutique ship and the most inclusive fare, with spirits and tips covered.",
        "skip": "if you are watching the budget: it is twice the price of #1.",
        "pros": ["<strong>Highest operator rating with real volume</strong>: 4.6 from 97 reviews.",
                 "<strong>Unlimited drinks including spirits</strong>, plus tips and Wi-Fi.",
                 "<strong>Heidelberg and Rothenburg</strong> on the itinerary."],
        "cons": ["<strong>From $8,365</strong>, the most expensive here.",
                 "<strong>Ages 16+</strong> only.",
                 "<strong>Flights not included</strong>, like everywhere else on this list."],
        "review": ["Uniworld's <strong>European Jewels</strong> is the boutique option: the <strong>S.S. Marlene</strong> has lavishly decorated riverview staterooms and suites, and the fare is the most inclusive on the route, with <strong>unlimited drinks including spirits</strong>, gratuities and Wi-Fi.",
                   "The itinerary is a little different too: alongside Vienna, the Wachau, Passau, Regensburg, Nuremberg, Bamberg and Cologne, it adds <strong>Rothenburg</strong> from Würzburg and <strong>Heidelberg</strong> from Frankfurt. It rates <strong>4.6 from 97 reviews</strong>. 2027 departures run <strong>$8,365 to $9,008</strong>; the 13 June sailing is the cheapest."],
        "facts": [("Duration", "15 days, 14 nights"),
                  ("Route", "Budapest, Vienna, Wachau (Weissenkirchen, Melk), Passau, Regensburg, Nuremberg, Bamberg, Würzburg and Rothenburg, Wertheim, Frankfurt and Heidelberg, Rüdesheim, Cologne, Amsterdam"),
                  ("Ship", "S.S. Marlene"),
                  ("Included", "All meals on board; unlimited drinks incl. spirits; gratuities; Wi-Fi; bicycles; guided excursions"),
                  ("Not included", "Flights, travel insurance"),
                  ("Minimum age", "16"),
                  ("Prices seen", "2 May 2027: $9,008 • 30 May 2027: $9,008 • 13 Jun 2027: $8,365")],
    },
    {
        "key": "avalon-magnificent-rivers", "tour": 363261, "photos": 5, "cats": "family",
        "operator": "Avalon Waterways", "days": 15, "price": 7424,
        "rating": (4.6, None), "dir": "Budapest → Amsterdam",
        "rank": "🪟 #5 Best Cabin Views",
        "short": "Avalon: Magnificent Rivers",
        "title": "Magnificent Rivers of Europe: 15 Days in a Panorama Suite",
        "pills": [
            ("🪟", "Wall-to-Wall Windows",
             "<strong>Panorama Suites with wall-to-wall windows and an open-air balcony</strong>, so the bed faces the river.",
             "Comfort Collection beds with a choice of mattress firmness, L'Occitane bath products."),
            ("🍹", "Happy Hour Every Evening",
             "<strong>Wine, beer or soft drinks with lunch and dinner</strong>, plus an included happy hour every evening with house beer, wine and cocktails.",
             "Free Wi-Fi and a 24-hour coffee station."),
            ("👨‍👩‍👧", "Kids 8+ Welcome",
             "<strong>Minimum age 8</strong>, the youngest on the route with #2.",
             "The fare shows about $504 per person in extra upfront charges at booking."),
        ],
        "pick": "if the cabin matters most: you wake up facing the river through a wall of glass.",
        "skip": "if you want tips included: Avalon doesn't list them in the fare.",
        "pros": ["<strong>Panorama Suites</strong> with wall-to-wall windows and open-air balconies.",
                 "<strong>Daily happy hour</strong> on top of wine with lunch and dinner.",
                 "<strong>Families welcome</strong> from age 8."],
        "cons": ["<strong>About $504 in upfront charges</strong> on top of the fare.",
                 "<strong>Gratuities not listed</strong> as included.",
                 "<strong>Summer fares from $7,424</strong>, no cheap winter date."],
        "review": ["Avalon's selling point is the cabin. Its <strong>Panorama Suites</strong> turn the whole outer wall into a window that opens onto an open-air balcony, and the beds face the river. Four ships run this route: Avalon Expression, Illumination, Impression and Passion.",
                   "On board you get wine, beer or soft drinks with lunch and dinner, an included <strong>happy hour every evening</strong> and free Wi-Fi, and Avalon offers a choice of included excursions in every port. 2027 departures run <strong>$7,424 to $7,721</strong>, with about $504 per person in upfront charges added at booking. It is the most grown-up pick that still takes children from 8."],
        "facts": [("Duration", "15 days"),
                  ("Route", "Budapest, Bratislava, Vienna, Dürnstein, Melk, Wachau Valley, Passau, Regensburg, Roth, Nuremberg, Bamberg, Würzburg, Miltenberg, Rüdesheim, Rhine Gorge, Cologne, Amsterdam"),
                  ("Ships", "Avalon Expression, Illumination, Impression, Passion"),
                  ("Included", "Meals on board; wine, beer or soft drinks with lunch and dinner; daily happy hour; Wi-Fi; included excursions"),
                  ("Not included", "Flights, insurance, about $504 upfront charges"),
                  ("Minimum age", "8"),
                  ("Prices seen", "28 May 2027: $7,721 • 15 Jun 2027: $7,721 • 3 Jul 2027: $7,424")],
    },
    {
        "key": "emerald-christmas-markets", "tour": 279591, "photos": 7, "cats": "tips winter under5k",
        "operator": "Emerald Cruises", "days": 15, "price": 4342,
        "rating": (4.1, 40), "dir": "Budapest → Amsterdam",
        "rank": "🎄 #6 Best Christmas Markets",
        "short": "Emerald: Christmas Markets of Europe",
        "title": "Christmas Markets of Europe: 15 Days, Budapest to Amsterdam",
        "pills": [
            ("🎄", "Late November Departures",
             "<strong>Sails in late November and early December</strong>, when the markets in Vienna, Nuremberg and Cologne are open.",
             "2026 sailings: 24 Nov ($8,207), 25 Nov ($6,786), 2 Dec ($6,984). 22 Nov 2027: $5,745."),
            ("💵", "Tips + Transfers Included",
             "<strong>All tipping and gratuities</strong> and airport transfers to and from the ship are included.",
             None),
            ("🍷", "Wine &amp; Beer with Meals",
             "<strong>14 breakfasts, 13 lunches and 14 dinners</strong>, with complimentary wine, beer and soft drinks at lunch and dinner.",
             None),
        ],
        "pick": "for Christmas markets from Budapest to Cologne, with tips included.",
        "skip": "if you want long days and green vineyards: these are short, cold winter days.",
        "pros": ["<strong>Christmas markets in nearly every port</strong>: Vienna, Nuremberg, Cologne.",
                 "<strong>Tips and transfers included</strong>, like #1.",
                 "<strong>Same Emerald ship and route</strong> as the best-value pick."],
        "cons": ["<strong>Short daylight</strong> in late November.",
                 "<strong>2026 dates cost $6,786+</strong>; 2027 is cheaper.",
                 "<strong>Up to 182 guests</strong> on board."],
        "review": ["If the point of the trip is mulled wine and market stalls, this is the one. Emerald runs its Budapest to Amsterdam route in <strong>late November and early December</strong> on the <strong>Emerald Sun, Luna and Astra</strong>, so you reach Vienna, Nuremberg and Cologne while the markets are open.",
                   "The inclusions match #1: all tips, airport transfers and wine, beer and soft drinks with lunch and dinner. This year's sailings are <strong>$6,786 to $8,207</strong>; the <strong>22 November 2027</strong> departure is <strong>$5,745</strong>, and the lowest advertised fare is <strong>$4,342</strong>."],
        "facts": [("Duration", "15 days, 14 nights on board"),
                  ("Route", "Budapest, Bratislava, Vienna, Dürnstein, Melk, Passau, Regensburg, Kelheim, Nuremberg, Bamberg, Würzburg, Wertheim, Miltenberg, Rüdesheim, Koblenz, Cologne, Amsterdam"),
                  ("Ships", "Emerald Sun, Emerald Luna, Emerald Astra"),
                  ("Included", "14 breakfasts, 13 lunches, 14 dinners; wine, beer and soft drinks with lunch and dinner; all tips; airport transfers"),
                  ("Not included", "Flights, insurance, optional activities"),
                  ("Minimum age", "12"),
                  ("Prices seen", "25 Nov 2026: $6,786 • 2 Dec 2026: $6,984 • 22 Nov 2027: $5,745")],
    },
    {
        "key": "viking-grand-european", "tour": 168856, "photos": 5, "cats": "",
        "operator": "Viking", "days": 15, "price": 6633,
        "rating": (3.9, None), "dir": "Budapest → Amsterdam",
        "rank": "🧭 #7 The Famous One",
        "short": "Viking: Grand European Tour",
        "title": "Grand European Tour: 15 Days, Budapest to Amsterdam on a Viking Longship",
        "pills": [
            ("🍷", "Wine &amp; Beer with Meals",
             "<strong>14 breakfasts, 13 lunches and 14 dinners</strong>, with beer, wine and soft drinks at lunch and dinner.",
             "Free Wi-Fi on board (speed may vary)."),
            ("🧾", "Port Taxes Included",
             "<strong>Port taxes and fees are included.</strong> Ground transfers come only with Viking's own air package.",
             None),
            ("🌍", "Booking Depends on Country",
             "<strong>Online booking is not open in every country.</strong> If your dates show as unavailable, it is the region, not the cruise.",
             None),
        ],
        "pick": "if you specifically want Viking's ships and its included tour in every port.",
        "skip": "if you want the best value: #1 includes tips and transfers for less.",
        "pros": ["<strong>The best-known itinerary</strong> on the route, with a guided tour in every port.",
                 "<strong>Port taxes included</strong> and drinks with lunch and dinner.",
                 "<strong>Adults-focused</strong> (18+)."],
        "cons": ["<strong>Lowest operator rating here</strong>: 3.9.",
                 "<strong>Transfers only with Viking air</strong>; tips not listed.",
                 "<strong>Not bookable online from every country.</strong>"],
        "review": ["Viking's <strong>Grand European Tour</strong> is the cruise most people have heard of: 15 days from Budapest via Vienna, Melk, Passau, Regensburg, Nuremberg, Bamberg, Würzburg, Wertheim, Koblenz and Cologne to Amsterdam on a Viking Longship.",
                   "From <strong>$6,633</strong> you get 14 breakfasts, 13 lunches and 14 dinners with beer, wine and soft drinks, free Wi-Fi and port taxes. Transfers are only included if you book Viking's flights, and the operator rating (<strong>3.9</strong>) is the lowest here. Booking online isn't open in every country, so check your dates before planning around it."],
        "facts": [("Duration", "15 days, 14 nights on board"),
                  ("Route", "Budapest, Vienna, Melk, Passau, Regensburg, Nuremberg, Bamberg, Würzburg, Wertheim, Koblenz, Cologne, Amsterdam"),
                  ("Ship", "Viking Longship"),
                  ("Included", "14 breakfasts, 13 lunches, 14 dinners; beer, wine and soft drinks with lunch and dinner; Wi-Fi; port taxes and fees"),
                  ("Not included", "Flights and transfers (unless booked with Viking Air), insurance"),
                  ("Minimum age", "18"),
                  ("Departures", "Nov 2026, then from March 2027")],
    },
]
REVERSE_EMERALD = 342308  # Splendours of Europe, Amsterdam to Budapest, from $3,163 (20 Feb 2027)

T = {
    "title": "7 Best Budapest to Amsterdam River Cruises (2027 Prices)",
    "h1": "The 7 Best Budapest to Amsterdam River Cruises", "kicker": "2027 River Cruise Comparison",
    "desc": "Budapest to Amsterdam river cruises compared: 7 15-day sailings from $3,941, with prices by month and what each fare includes (drinks, tips, transfers).",
    "lead": "The same 15-day Emerald cruise between Budapest and Amsterdam costs <strong>$3,163 in late February and $7,122 in May</strong>, and every line stops in almost the same towns, so the real choice is <strong>when you sail and what the fare includes</strong>: here are the 7 worth booking, from <strong>$3,941 with wine at dinner</strong> to <strong>$8,365 with every drink and tip covered</strong>.",
    "qp": [("Best value", 1, "tips + transfers included, from $3,976"),
           ("Best summer price", 2, "$3,941 in August"),
           ("Best all-inclusive", 3, "drinks all day, $5,244 in Feb"),
           ("Best boutique", 4, "unlimited drinks incl. spirits")],
    "flt": [("tips", "💵 Tips included"), ("allinc", "🥂 Drinks all day"), ("under5k", "💲 Under $5,000"),
            ("family", "👨‍👩‍👧 Kids 8+ welcome"), ("winter", "🎄 Christmas markets")],
    "breakdown": "Detailed Breakdown: 7 Budapest to Amsterdam River Cruises",
    "breakdown_sub": "Route, ship, prices by departure and what is included, cruise by cruise",
    "toc_deck": "Top 7 Budapest to Amsterdam Cruises", "toc_breakdown": "Detailed Breakdown (7 Cruises)",
    "sticky_all": "All 7 River Cruises", "sheet": "Jump to a River Cruise",
    "breadcrumb_name": "The 7 Best Budapest to Amsterdam River Cruises (2027)",
}

AFF = 'rel="nofollow sponsored noopener" target="_blank"'


def esc(s):
    return html.escape(s, quote=True)


def usd(v):
    return f"${v:,}"


def book_url(p):
    return tr(p["tour"], p["key"])


def photo(p, i):
    return f"{ASSET}/budapest-amsterdam-river-cruise-{p['key']}-{i:02d}.avif"


def maps(q):
    from urllib.parse import quote_plus
    return "https://www.google.com/maps/search/?api=1&amp;query=" + quote_plus(q)


def pill(emoji, label, lead, note):
    n = f'<span class="bpa-lang-note">{note}</span>' if note else ""
    return (f'<details class="bpa-lang"><summary class="bpa-sp">{emoji} <span class="bpa-lang-label">{label}</span>'
            f'<span class="bpa-lang-chev" aria-hidden="true">▾</span></summary><div class="bpa-lang-pop">{lead}{n}</div></details>')


def rating_block(p):
    s, c = p["rating"]
    meta = f"{c} reviews" if c else "operator rating"
    head = (f"<strong>{p['operator']} operator rating on TourRadar</strong>"
            + (f" ({c} reviews)" if c else "")
            + '<span class="bpa-lang-note">Reviews cover all of the operator\'s cruises, not only this route.</span>')
    return (f'<div class="bpa-reviews-line"><div class="bpa-summary-reviews bpa-rate"><details class="bpa-lang bpa-rate-more">'
            f'<summary class="bpa-rate-sum"><span class="bpa-stars" style="--r:{s:.2f}" aria-hidden="true"></span>'
            f'<b class="bpa-rate-score">{s:.1f}</b><span class="bpa-rate-meta">{meta}</span>'
            f'<span class="bpa-lang-chev" aria-hidden="true">▾</span></summary><div class="bpa-lang-pop">{head}</div></details></div></div>')


def card(n, p):
    url = esc(book_url(p))
    imgs = []
    for i in range(1, p["photos"] + 1):
        lazy = 'loading="eager" fetchpriority="high"' if (n == 1 and i == 1) else 'loading="lazy"'
        imgs.append(f'<img alt="{esc(p["title"])}, photo {i}" height="534" width="800" {lazy} src="{photo(p, i)}"/>')
    gold = " bpa-gold" if p.get("gold") else ""
    port = p["dir"].split(" → ")[0]
    return f'''<div class="bpa-card" data-cat="{p['cats']}" id="card-{n}">
<div class="bpa-main">
<div class="bpa-media">
<button aria-label="Previous photo" class="bpa-arrow prev" onclick="bpaSlide(this,-1)" type="button">‹</button><button aria-label="Next photo" class="bpa-arrow next" onclick="bpaSlide(this,1)" type="button">›</button><span class="bpa-pill">1 / {p['photos']}</span><span class="bpa-rank-tag{gold}">{p['rank']}</span>
<div class="bpa-slider" onscroll="bpaCount(this)">{''.join(imgs)}</div>
</div>
<div class="bpa-info">
<div class="bpa-kicker">{p['operator']} • ⏱️ {p['days']} Days • <a class="bpa-kicker-map-link" href="{maps(port + ' river cruise pier')}" onclick="event.stopPropagation()" rel="noopener noreferrer" target="_blank">📍 {p['dir']}</a></div>
<a class="bpa-title" href="{url}" {AFF}>{p['title']}</a>
{rating_block(p)}
<div class="bpa-specs-row">
{''.join(pill(*x) for x in p['pills'])}
</div>
<div class="bpa-best-for bpa-pickskip"><span class="bpa-pick">✓ Pick it</span> {p['pick']} <span class="bpa-skip">✕ Skip it</span> {p['skip']}</div>
</div>
<div class="bpa-cta-cell">
<div>
<div class="bpa-price">From {usd(p['price'])}</div>
<div class="bpa-psub">per person, 15 days</div>
</div>
<a class="bpa-btn" href="{url}" {AFF}>Check Dates &amp; Prices →</a>
<div class="bpa-via">Booked securely via TourRadar</div>
<div class="bpa-trust2"><span>✓ ${round(p['price'] / p['days'])} per day</span><span>✓ Twin cabin, 2 sharing</span></div>
<a class="bpa-sublink" href="#ba-{p['key']}">Read review ↓</a>
</div>
</div>
</div>'''


def details(n, p):
    url = esc(book_url(p))
    s, c = p["rating"]
    gold = " bpa-gold" if p.get("gold") else ""
    pros = "".join(f"<li>{x}</li>" for x in p["pros"])
    cons = "".join(f"<li>{x}</li>" for x in p["cons"])
    slides = "".join(
        f'<div class="ltt-strip-slide"><img alt="{esc(p["operator"])}: {esc(p["title"])}, photo {i}" loading="lazy" src="{photo(p, i)}"/>'
        f'<div class="ltt-strip-cap"><span class="ltt-strip-num">{i} / {p["photos"]}</span> <span>Photo: {esc(p["operator"])} via TourRadar</span></div></div>'
        for i in range(1, p["photos"] + 1))
    review = "".join(f"<p>{x}</p>" for x in p["review"]).replace("TR_REVERSE", esc(tr(REVERSE_EMERALD, "emerald-splendours-reverse")))
    facts = "".join(f'<div class="qf1-row"><div class="qf1-label">{a}</div><div class="qf1-val">{b}</div></div>' for a, b in p["facts"])
    meta = f"{c} reviews" if c else "operator rating"
    return f'''<details class="bpa-details-card" data-cat="{p['cats']}" id="ba-{p['key']}" open="">
<summary class="bpa-details-summary">
<div class="bpa-details-summary-content">
<div class="bpa-details-top-row">
<span class="bpa-rank-tag{gold}">{p['rank']}</span>
<div class="bpa-kicker">{p['operator']} • ⏱️ {p['days']} Days • {p['dir']}</div>
</div>
<h3 class="bpa-details-title">{p['title']}</h3>
<div class="bpa-reviews-line"><span class="bpa-stars" style="--r:{s:.2f}" aria-hidden="true"></span> <b class="bpa-rate-score">{s:.1f}</b> <span class="bpa-rate-meta">({meta})</span></div>
</div>
<div class="bpa-details-right">
<span class="bpa-details-price">From {usd(p['price'])}</span>
<div class="bpa-details-toggle">
<span class="bpa-details-state-text"></span>
<span class="bpa-details-chevron">▾</span>
</div>
</div>
</summary>
<div class="bpa-details-body">
<div class="pro-con-box-wrapper"><div class="w-layout-grid grid-15"><div class="pro-con-box-pro-cell" data-wf-pbl="layout-grid-1x2-vertical"><div class="pro-con-box-pro-cell-rich-text-block w-richtext"><h3><strong>Pros:</strong></h3><ul>{pros}</ul></div></div><div class="pro-con-box-con-cell" data-wf-pbl="layout-grid-1x2-vertical"><div class="pro-con-box-con-cell-rich-text-block w-richtext"><h3><strong>Cons:</strong></h3><ul>{cons}</ul></div></div></div></div><details class="ltt-bento-group" open=""><summary class="ltt-bento-group-head"><span class="ltt-bento-group-title">📸 Photos</span><span class="ltt-bento-right"><span class="ltt-mini-pill">Swipe {p['photos']} Photos →</span><span class="ltt-bento-chev">▾</span></span></summary><div class="ltt-bento-group-body" style="padding: 12px 14px !important;"><div class="ltt-filmstrip-wrap"><button aria-label="Previous photo" class="ltt-film-btn ltt-film-prev is-disabled" onclick="window.lttFilmSlide(this, -1)" type="button">‹</button><button aria-label="Next photo" class="ltt-film-btn ltt-film-next" onclick="window.lttFilmSlide(this, 1)" type="button">›</button><div class="ltt-filmstrip" onscroll="window.lttFilmSync(this)">{slides}</div></div></div></details><details class="ltt-bento-group" open="">
<summary class="ltt-bento-group-head">
<span class="ltt-bento-group-title">Summary &amp; Review</span>
<span class="ltt-bento-right">
<span class="ltt-mini-pill">Overview</span>
<span class="ltt-bento-chev">▾</span>
</span>
</summary>
<div class="ltt-bento-group-body">
<div class="w-richtext">{review}</div>
</div>
</details>
<div class="qf1-wrap"><div class="qf1-title-row"><h4 class="qf1-title">Quick Facts</h4><span class="qf1-badge">{p['dir']}</span></div><div class="qf1-table">{facts}</div></div>
<a class="bpa-btn" href="{url}" {AFF} style="margin-top:14px;display:block;text-align:center">Check Dates &amp; Prices: From {usd(p['price'])} →</a></div>
</details>'''


# ---------------------------------------------------------------------------
# Buyer's guide sections
# ---------------------------------------------------------------------------
INCL = {  # drinks, tips, transfers, min age
    "emerald-splendours": ("With lunch &amp; dinner", "Yes", "Yes", "12+"),
    "lueftner-amadeus": ("With lunch &amp; dinner", "No", "Not listed", "8+"),
    "scenic-jewels": ("All day", "Yes", "Yes", "18+"),
    "uniworld-european-jewels": ("All day, incl. spirits", "Yes", "Not listed", "16+"),
    "avalon-magnificent-rivers": ("Meals + happy hour", "Not listed", "Not listed", "8+"),
    "emerald-christmas-markets": ("With lunch &amp; dinner", "Yes", "Yes", "12+"),
    "viking-grand-european": ("With lunch &amp; dinner", "Not listed", "With Viking Air", "18+"),
}


def logistics_table():
    hd = ["#", "Cruise", "Direction", "From", "Per day", "Drinks", "Tips incl.", "Transfers", "Ages"]
    rows = []
    for n, p in enumerate(PRODUCTS, 1):
        d, tip, xf, age = INCL[p["key"]]
        rows.append(f'<tr><td>{n}</td><td><a href="#card-{n}">{p["short"]}</a></td><td>{p["dir"]}</td>'
                    f'<td>{usd(p["price"])}</td><td>${round(p["price"] / p["days"])}</td><td>{d}</td><td>{tip}</td><td>{xf}</td><td>{age}</td></tr>')
    th = "".join(f"<th>{h}</th>" for h in hd)
    return f'<div class="bt-table-wrap"><table class="bt-logistics"><thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def month_table():
    rows = [
        ("Emerald Splendours (Amsterdam → Budapest)", "$3,163 (20 Feb)", "$5,684 (8 Mar)", "$5,941 (23 Apr)", "$7,122 (8 May)"),
        ("Scenic Jewels of Europe", "$5,244 (22 Feb)", "$9,933 (9 Mar)", "$9,321 (23 Mar)", "n/a"),
        ("Lueftner Across Europe", "n/a", "n/a", "$4,637 (8 May)", "$3,941 (19 Aug)"),
        ("Uniworld European Jewels", "n/a", "n/a", "$9,008 (2 May)", "$8,365 (13 Jun)"),
    ]
    th = "".join(f"<th>{h}</th>" for h in ["Cruise (2027 sailings)", "February", "March", "April / May", "Summer"])
    tb = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<div class="bt-table-wrap"><table class="bt-logistics"><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>'


FAQ = [
    ("How much does a Budapest to Amsterdam river cruise cost?",
     "For 15 days, expect from about $3,200 to $4,000 per person on Emerald or Lueftner on their cheapest dates, $5,200 to $7,500 on Scenic, Viking and Avalon, and $8,400 to $9,000 on Uniworld. The same cruise often costs twice as much in May as in late February, so the date matters more than the line."),
    ("How long is a river cruise from Budapest to Amsterdam?",
     "The standard cruise is 15 days with 14 nights on board, sailing about 1,100 miles along the Danube, the Main-Danube Canal, the Main and the Rhine. Some lines also sell 17 to 22-day versions that add hotel nights in Budapest or Amsterdam or a Belgian extension."),
    ("Which river cruise line is best for Budapest to Amsterdam?",
     "For value, Emerald Cruises: from $3,976 with tips, transfers and wine at dinner included. For everything included, Scenic (drinks all day, tips and transfers) or Uniworld (unlimited drinks including spirits and tips). For the cabin, Avalon's Panorama Suites. Lueftner has the best operator rating at 4.5 from 220 reviews."),
    ("Is it better to sail Budapest to Amsterdam or Amsterdam to Budapest?",
     "The stops are the same either way, so pick the direction by price and by where you want to spend extra days. Prices differ by date, not direction: Emerald's cheapest sailing on this route goes Amsterdam to Budapest on 20 February 2027 for $3,163."),
    ("Are drinks and tips included on a Budapest to Amsterdam river cruise?",
     "It depends on the line. Scenic and Uniworld include drinks all day and tips. Emerald includes tips and wine, beer and soft drinks with lunch and dinner. Lueftner, Avalon and Viking include drinks with meals but not tips, so add those to the fare when comparing."),
    ("When is the best time for a Budapest to Amsterdam river cruise?",
     "April to June and September to October for mild weather and green vineyards; late November and December for the Christmas markets; late February and early March for the lowest prices. In very dry late summers, low water on the Danube or Rhine can force a ship swap or a coach section, so travel insurance is worth having."),
]


def sections():
    worth = ('<section data-toc="Is It Worth It?" id="ba-worth-it"><div class="w-richtext"><h2>Is a Budapest to Amsterdam River Cruise Worth It?</h2>'
             '<p>Fifteen days, four countries and around 14 towns without packing your suitcase once. At <strong>$3,976 for Emerald\'s February sailing</strong> that is about <strong>$265 per person per day</strong> for your cabin, 41 meals, wine and beer at lunch and dinner, guided walks in nearly every port, airport transfers and tips. Booking the same hotels, trains and tours yourself across Hungary, Austria, Germany and the Netherlands would cost about the same and take a lot more planning.</p>'
             '<p>It is less of a deal if you want to explore cities in depth: most stops are a morning or an afternoon. In that case, spend a few extra days at either end. In Amsterdam, a <a href="/canal-cruises-amsterdam">canal cruise</a> on your first evening is the best way to get your bearings (<a href="/best-canal-cruise-amsterdam">this is the one I\'d book</a>).</p></div></section>')
    logi = ('<section data-toc="Side by Side" id="ba-logistics"><div class="w-richtext"><h2>All 7 Cruises Side by Side</h2>'
            '<p>The itineraries are almost the same, so these are the columns that decide the booking: price per day, drinks, whether tips and transfers are in the fare, and the minimum age.</p></div>'
            + logistics_table() + '</section>')
    month = ('<section data-toc="Prices by Month" id="ba-price-by-month"><div class="w-richtext"><h2>Prices by Month: When Is It Cheapest?</h2>'
             '<p><strong>Late February is the cheapest time to sail</strong>, often at half the price of May. On Scenic the gap is extreme: <strong>$5,244 on 22 February 2027 against $9,933 two weeks later</strong>. Lueftner is the exception, with its lowest fare in August.</p></div>'
             + month_table()
             + '<div class="w-richtext"><p>Prices are per person in US dollars, cheapest cabin, two people sharing. They move with demand and sales, so treat them as a guide and check your own dates.</p></div></section>')
    route = ('<section data-toc="The Route" id="ba-route"><div class="w-richtext"><h2>The Route: What You See in 15 Days</h2>'
             '<p>Every cruise here follows the same three rivers. The <strong>Danube</strong> from Budapest through Bratislava and Vienna, the Wachau Valley (Dürnstein and Melk) and Passau to Regensburg; the <strong>Main-Danube Canal</strong> over the European watershed to Nuremberg and Bamberg; the <strong>Main</strong> through Würzburg and Miltenberg; and the <strong>Rhine</strong> through the Rhine Gorge, past Rüdesheim and Koblenz to Cologne and Amsterdam.</p>'
             '<p>The differences are small but real: Uniworld adds <strong>Heidelberg and Rothenburg</strong>, Scenic adds <strong>Bonn</strong>, Lueftner stops in <strong>Utrecht</strong>, and Emerald and Avalon include <strong>Bratislava</strong>. The bigger decision is the direction: start in Amsterdam if you want to finish with a few days in Budapest, or the other way round if you would rather end with the canals. If you plan extra nights in Amsterdam, the <a href="/amsterdam-tourism-statistics">Amsterdam tourism statistics</a> show which months the city is busiest.</p></div></section>')
    meth = ('<section data-toc="How I Compared" id="ba-methodology"><div class="w-richtext"><h2>How I Compared These 7 River Cruises</h2>'
            '<p>On 16 November 2026 I compared every Budapest to Amsterdam and Amsterdam to Budapest river cruise sold on TourRadar, side by side on the details that decide a booking: departure dates and prices, price per day, ship, drinks, tips, transfers, minimum age and the stops that differ. Prices are per person for two adults sharing the cheapest cabin, taken from the live listings on that date; ratings are the operator ratings shown there.</p>'
            '<p>Scenic alone sells around 10 versions of this route, so I kept one per line and style rather than padding the list. I left out sailings with no bookable dates. Each of the 7 wins at something: overall value, summer value, all-inclusive, boutique, cabin views, Christmas markets and the best-known name.</p></div></section>')
    faq = ('<section data-toc="FAQ" id="ba-faq"><div class="w-richtext"><h2>Budapest to Amsterdam River Cruises: FAQ</h2>'
           + "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in FAQ) + '</div></section>')
    return "\n".join([worth, logi, month, route, faq, meth])


EXTRA_CSS = """
<style id="bt-extra-css">
.bt-qp{margin:14px 0 4px;padding:12px 14px;border:1px solid #e2e8f0;border-radius:12px;background:#f8fafc}
.bt-qp-title{font-size:12px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:#64748b;margin:0 0 6px}
.bt-qp ul{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:4px 18px}
.bt-qp li{font-size:14px;line-height:1.45;color:#334155;margin:0}
.bt-qp a,.bt-qp a:visited{color:#0f172a;font-weight:700;text-decoration:underline;text-underline-offset:2px}
.bt-qp a:hover,.bt-qp a:focus{color:#855a00}
@media (max-width:600px){.bt-qp ul{grid-template-columns:1fr}}
.bt-table-wrap{width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch;margin:8px 0 18px;border:1px solid #e2e8f0;border-radius:12px}
.bt-logistics{width:100%;min-width:720px;border-collapse:collapse;font-size:13.5px;line-height:1.4}
.bt-logistics th{background:#0f172a;color:#fff;text-align:left;font-weight:700;padding:8px 10px;white-space:nowrap}
.bt-logistics td{padding:8px 10px;border-top:1px solid #e2e8f0;color:#334155;vertical-align:top}
.bt-logistics tr:nth-child(even) td{background:#f8fafc}
.bt-logistics a,.bt-logistics a:visited{color:#0f172a;font-weight:700;text-decoration:underline}
.bt-logistics a:hover,.bt-logistics a:focus{color:#855a00}
.ltt-editorial-wrapper .w-richtext a:hover,.bpa-details-body .w-richtext a:hover,.bpa-lang-pop a:hover,#bpa-lang-float a:hover{color:#855a00}
.bpa-sublink:hover,.bpa-kicker-map-link:hover,.bpa-title:hover{color:#855a00}
.bpa-details-card .bpa-reviews-line{display:flex;align-items:center;gap:4px;font-size:12.5px}
</style>"""


def jsonld():
    url = f"{SITE}/{SLUG}"
    items = []
    for n, p in enumerate(PRODUCTS, 1):
        items.append({"@type": "ListItem", "position": n, "item": {
            "@type": "TouristTrip", "name": p["title"],
            "description": (p["pick"][0].upper() + p["pick"][1:]).rstrip("."),
            "image": [f"{SITE}{photo(p, i)}" for i in range(1, min(p["photos"], 3) + 1)],
            "provider": {"@type": "Organization", "name": p["operator"]},
            "offers": {"@type": "Offer", "price": str(p["price"]), "priceCurrency": "USD", "url": book_url(p)}}})
    graph = [
        {"@type": "Article", "@id": f"{url}#article", "headline": T["breadcrumb_name"], "description": T["desc"],
         "image": [f"{SITE}{photo(p, 1)}" for p in PRODUCTS[:6]],
         "datePublished": DATE_ISO, "dateModified": DATE_ISO, "inLanguage": "en",
         "mainEntityOfPage": {"@type": "WebPage", "@id": url},
         "author": {"@type": "Person", "name": "Adam Dimitrov", "jobTitle": "Owner & Head Cruise Detective", "url": f"{SITE}/about"},
         "publisher": {"@type": "Organization", "name": "The Cruise Detective", "url": SITE,
                       "logo": {"@type": "ImageObject", "url": "https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/6570a89c8c97ba4e084ac5d5_webclip-cruise-detective.png"}},
         "mainEntity": {"@id": f"{url}#list"}},
        {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": T["breadcrumb_name"], "item": url}]},
        {"@type": "ItemList", "@id": f"{url}#list", "name": T["breadcrumb_name"], "numberOfItems": len(PRODUCTS), "itemListElement": items},
        {"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def build():
    src = TEMPLATE.read_text(encoding="utf-8")
    seine = SEINE.read_text(encoding="utf-8")
    t = T
    url = f"{SITE}/{SLUG}"
    lang_css = re.search(r'<style id="bpa-lang-css">.*?</style>', seine, re.S).group(0)
    lang_js = re.search(r'<script id="bpa-lang-js">.*?</script>', seine, re.S).group(0)
    card_css = "<style id=\"bt-card-css\">\n" + (ROOT / "scripts" / "articles" / "seine_card_extra.css").read_text(encoding="utf-8") + "\n</style>"

    h = src
    h = re.sub(r"<title>.*?</title>", f"<title>{t['title']}</title>", h, count=1)
    for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        h = re.sub(r'<meta content="[^"]*" ' + re.escape(attr) + r'/>', f'<meta content="{esc(t["desc"])}" {attr}/>', h, count=1)
    for attr in ('property="og:title"', 'name="twitter:title"'):
        h = re.sub(r'<meta content="[^"]*" ' + re.escape(attr) + r'/>', f'<meta content="{esc(t["title"])}" {attr}/>', h, count=1)
    img0 = f"{SITE}{photo(PRODUCTS[0], 1)}"
    for attr in ('property="og:image"', 'name="twitter:image"'):
        h = re.sub(r'<meta content="[^"]*" ' + re.escape(attr) + r'/>', f'<meta content="{img0}" {attr}/>', h, count=1)
    h = re.sub(r'<meta content="[^"]*" property="og:url"/>', f'<meta content="{url}" property="og:url"/>', h, count=1)
    alt = (f'<link href="{url}" rel="canonical"/>\n'
           f'<link href="{url}" hreflang="en" rel="alternate"/>\n'
           f'<link href="{url}" hreflang="x-default" rel="alternate"/>\n')
    h = re.sub(r'<link href="[^"]*" rel="canonical"/>\n(?:<link href="[^"]*" hreflang="[^"]*" rel="alternate"/>\n)+', alt, h, count=1)
    h = h.replace('<link href="/dinner-cruises-paris.md" rel="alternate" type="text/markdown"/>\n', "")
    h = re.sub(r'<link as="image" fetchpriority="high" href="[^"]*" rel="preload"/>',
               f'<link as="image" fetchpriority="high" href="{photo(PRODUCTS[0], 1)}" rel="preload"/>', h, count=1)
    h = re.sub(r'<script id="private-cruises-schema-jsonld" type="application/ld\+json">.*?</script>',
               lambda m: f'<script id="{SLUG}-schema-jsonld" type="application/ld+json">{jsonld()}</script>'
               + "\n" + lang_css + "\n" + card_css + EXTRA_CSS, h, count=1, flags=re.S)

    # --- hero + deck
    hero_start = h.index('<div class="ltt-hero-wrap">')
    deck_end = h.index('<div class="blog-section-2">')
    deck_css = re.search(r'<style id="ltt-dubai-safari-styles">.*?</style>', h, re.S).group(0)
    cats = {}
    for p in PRODUCTS:
        for c in p["cats"].split():
            cats[c] = cats.get(c, 0) + 1
    filt = [f'<button class="ltt-tab-btn active" data-cat="all" onclick="lttFilterItems(\'all\', this)" type="button">All ({len(PRODUCTS)})</button>']
    for c, label in t["flt"]:
        filt.append(f'<button class="ltt-tab-btn" data-cat="{c}" onclick="lttFilterItems(\'{c}\', this)" type="button">{label} ({cats.get(c, 0)})</button>')
    qp = "".join(f'<li><strong>{a}:</strong> <a href="#card-{n}">{PRODUCTS[n - 1]["short"]}</a>, {d}</li>' for a, n, d in t["qp"])
    hero = f'''<div class="ltt-hero-wrap">
<div class="ltt-clean-card">
<div class="ltt-top-bar">
<nav aria-label="Breadcrumb" class="ltt-breadcrumbs">
<a href="/">Home</a>
<span class="ltt-bc-sep">›</span>
<span class="ltt-bc-current">{t['breadcrumb_name']}</span>
</nav>
<span class="ltt-hero-kicker-badge">{t['kicker']}</span>
</div>
<h1 class="ltt-editorial-h1">{t['h1']} <span class="ltt-h1-muted">(2027)</span></h1>
<div class="ltt-trust-bar">
<div class="ltt-author-cluster">
<div class="ltt-author-avatar-wrap">
<img alt="Adam Dimitrov" class="ltt-author-avatar" src="https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp"/>
</div>
<div class="ltt-author-meta">
<div class="ltt-author-line">
            By <a href="/about" target="_blank">Adam Dimitrov</a>, Owner &amp; Head Cruise Detective
          </div>
<div class="ltt-author-role">Compared on {CHECKED} using live listings • Independent comparison</div>
</div>
</div>
<div class="ltt-trust-pills">
<span class="ltt-trust-pill paragraph-26"><strong>Last updated</strong>: {CHECKED}</span>
</div>
</div>
<div class="ltt-lead-copy">
<p>{t['lead']}</p>
<div class="bt-qp"><p class="bt-qp-title">Quick picks</p><ul>{qp}</ul></div>
</div>
<div class="ltt-integrated-filter-bar">
<span class="ltt-filter-label">Filters:</span>
<div class="ltt-integrated-pills">{chr(10).join(filt)}</div>
</div>
</div>
</div><div class="comparison-table"><div class="container-27">
{deck_css}
<div class="ltt-deck-container" id="budapest-amsterdam-cruise-deck">
<div class="bpa-deck-wrap" id="ltt-cards-deck">{chr(10).join(card(n, p) for n, p in enumerate(PRODUCTS, 1))}
</div></div></div></div>'''
    h = h[:hero_start] + hero + h[deck_end:]

    # --- breakdown + sections
    bstart = h.index('<div class="bpa-breakdown-top-bar" id="breakdown-header">')
    first_det = h.index('<details class="bpa-details-card"', bstart)
    head = h[bstart:first_det]
    head = re.sub(r'<h2 class="bpa-breakdown-heading" id="[^"]*">.*?</h2>',
                  f'<h2 class="bpa-breakdown-heading" id="budapest-amsterdam-breakdown">{t["breakdown"]}</h2>', head, flags=re.S)
    head = re.sub(r'<p class="bpa-breakdown-sub">.*?</p>', f'<p class="bpa-breakdown-sub">{t["breakdown_sub"]}</p>', head, flags=re.S)
    sec_start = h.index("<section", first_det)
    between = h[first_det:sec_start]
    tail_between = between[between.rindex("</details>") + len("</details>"):]
    sec_end = h.rindex("</section>") + len("</section>")
    body = head + "\n".join(details(n, p) for n, p in enumerate(PRODUCTS, 1)) + tail_between + sections()
    h = h[:bstart] + body + h[sec_end:]

    # --- page config + sticky bar
    cfg = {"deckId": "budapest-amsterdam-cruise-deck", "tocDeckLabel": t["toc_deck"], "tocBreakdownLabel": t["toc_breakdown"],
           "shortTitles": [p["short"] for p in PRODUCTS]}
    h = re.sub(r"LTT_PAGE_CONFIG = \{.*?\};", lambda m: "LTT_PAGE_CONFIG = " + json.dumps(cfg, ensure_ascii=False) + ";", h, count=1, flags=re.S)
    p1 = PRODUCTS[0]
    h = h.replace('<span>All 6 Private Cruises</span>', f'<span>{t["sticky_all"]}</span>')
    h = re.sub(r'(<span class="hybrid-active-badge" id="sticky-rank">)[^<]*', r"\g<1>#1 PICK", h)
    h = re.sub(r'(<span class="hybrid-active-title" id="sticky-name">)[^<]*', lambda m: m.group(1) + p1["short"], h)
    h = re.sub(r'(<span class="hybrid-active-price" id="sticky-price">)[^<]*', lambda m: m.group(1) + usd(p1["price"]), h)
    h = re.sub(r'(<span class="hybrid-active-trust">)[^<]*', lambda m: m.group(1) + "Tips included", h)
    h = re.sub(r'<a class="hybrid-cta-btn" href="[^"]*"', f'<a class="hybrid-cta-btn" href="{esc(book_url(p1))}"', h, count=1)
    h = re.sub(r'(<a class="hybrid-cta-btn"[^>]*>)\s*Check Availability →\s*</a>', lambda m: m.group(1) + "\n      Check Dates &amp; Prices →\n    </a>", h)
    h = h.replace('aria-label="Jump to Paris Private Cruise"', f'aria-label="{t["sheet"]}"')
    h = re.sub(r'<h3 class="hybrid-sheet-title">[^<]*</h3>', f'<h3 class="hybrid-sheet-title">{t["sheet"]}</h3>', h)
    h = h.replace("</body>", lang_js + "\n</body>", 1)
    return h


def main():
    out = ROOT / SLUG / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(), encoding="utf-8")
    print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
