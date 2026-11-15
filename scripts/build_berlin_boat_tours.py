#!/usr/bin/env python3
"""Build /berlin-boat-tours (EN) and /de/spreefahrt-berlin (DE) from the
private-cruises-paris template, with the Seine page's card features
(rating popover, pill dropdowns, Pick/Skip).

    python3 scripts/build_berlin_boat_tours.py
    python3 scripts/sync_layout.py
    python3 scripts/i18n/port.py sync berlin     # cards + sections from EN via the translation memory

Run in that order: the builder writes both languages, port.py then aligns the DE cards
with the site-wide translation memory. Facts come from the live Tiqets / GetYourGuide listings (checked 2026-11-15).
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
ASSET = "/assets/berlin-boat-tours"
DATE_ISO = "2026-11-15T12:00:00+01:00"
CHECKED = {"en": "Nov 15, 2026", "de": "15. Nov. 2026"}
SLUG = {"en": "berlin-boat-tours", "de": "de/spreefahrt-berlin"}
GYG = "YS414AJ"
TQ = "thecruisedetective.com-176436"


def gyg(path, key, lang):
    cmp = f"article-berlin-boat-tours-{key}" + ("-de" if lang == "de" else "")
    return (f"https://www.getyourguide.com/berlin-l17/{path}/?partner_id={GYG}"
            f"&utm_medium=online_publisher&cmp={cmp}&mkt_cmp=true")


def tiq(path, key, lang):
    camp = f"berlin-boat-tours-{key}" + ("-de" if lang == "de" else "")
    return (f"https://www.tiqets.com/en/berlin-attractions-c65144/{path}/"
            f"?partner={TQ}&tq_campaign={camp}")


# ---------------------------------------------------------------------------
# DATA (prices, ratings, piers from the live listings, 15 Nov 2026)
# ratings: (site, score, count); the booked site is linked in the popover.
# ---------------------------------------------------------------------------
PRODUCTS = [
    {
        "key": "hadynski-glass-roof", "photos": 5, "cats": "hour cancel under20",
        "book": ("gyg", "berlin-bilingual-river-cruise-ende-live-guided-heated-t520045"),
        "operator": "Reederei Hadynski", "hours": 1.0,
        "price": 18.06, "was": 21, "cancel": True,
        "ratings": [("GetYourGuide", 4.72, 7465)],
        "pier": "Anna-Louisa-Karsch-Straße 2, 10178 Berlin",
        "pier_short": {"en": "Opposite Berlin Cathedral", "de": "Gegenüber Berliner Dom"},
        "dur": {"en": "1 Hour", "de": "1 Stunde"},
        "rank": {"en": "🏆 #1 Best Overall", "de": "🏆 #1 Testsieger im Vergleich"},
        "gold": True,
        "short": {"en": "Hadynski: Glass-Roof Boat, Live Guide", "de": "Hadynski: Glasdach-Boot, Live-Guide"},
        "title": {"en": "1-Hour Spree Cruise on a Heated Glass-Roof Boat with a Live Guide",
                  "de": "1 Stunde Spreefahrt im beheizten Glasdach-Boot mit Live-Guide"},
        "pills": [
            ("🎙️", {"en": "Live Guide DE/EN", "de": "Live-Guide DE/EN"},
             {"en": "<strong>A real guide, not a recording.</strong> The commentary is given live in German and English on every departure.",
              "de": "<strong>Ein echter Guide, keine Bandansage.</strong> Die Erklärungen kommen bei jeder Fahrt live auf Deutsch und Englisch."},
             {"en": "No audio guide in other languages. For French, Spanish or Italian, pick #3.",
              "de": "Kein Audioguide in anderen Sprachen. Für Französisch, Spanisch oder Italienisch nimm #3."}),
            ("☔", {"en": "Glass Roof + Heating", "de": "Glasdach + Heizung"},
             {"en": "<strong>Weatherproof.</strong> The glass roof opens on sunny days and closes in rain; the cabin is heated when it is cold. Toilet on board.",
              "de": "<strong>Wetterfest.</strong> Das Glasdach öffnet bei Sonne und schließt bei Regen, die Kabine ist bei Kälte beheizt. Toilette an Bord."},
             {"en": "Sails daily from March to December on MS Carola or MS Franziska.",
              "de": "Fährt täglich von März bis Dezember mit MS Carola oder MS Franziska."}),
            ("🏛️", {"en": "Classic City Loop", "de": "Klassische City-Runde"},
             {"en": "<strong>The 1-hour central loop:</strong> Humboldt Forum, Nikolaiviertel, Museum Island, Tränenpalast, Reichstag, Hauptbahnhof, Chancellery and Haus der Kulturen der Welt, then back.",
              "de": "<strong>Die 1-Stunden-Runde durch die Mitte:</strong> Humboldt Forum, Nikolaiviertel, Museumsinsel, Tränenpalast, Reichstag, Hauptbahnhof, Kanzleramt und Haus der Kulturen der Welt, dann zurück."},
             {"en": "Same route as #3 and #4. The difference is the boat and the guide.",
              "de": "Dieselbe Route wie #3 und #4. Der Unterschied ist das Boot und der Guide."}),
        ],
        "pick": {"en": "for the best 1-hour cruise in any weather: live guide, glass roof, €18.",
                 "de": "für die beste 1-Stunden-Fahrt bei jedem Wetter: Live-Guide, Glasdach, €18."},
        "skip": {"en": "if you need a wheelchair-accessible boat: the listing says it is not suitable.",
                 "de": "wenn du ein rollstuhlgerechtes Boot brauchst: laut Angebot nicht geeignet."},
        "pros": {"en": ["<strong>Highest rating of the 1-hour cruises</strong>: 4.7 from 7,465 reviews.",
                        "<strong>Live bilingual guide</strong> on every trip, while most rivals play a recording.",
                        "<strong>Glass roof and heating</strong>: the best 1-hour pick from November to March."],
                 "de": ["<strong>Beste Bewertung der 1-Stunden-Fahrten</strong>: 4,7 aus 7.465 Bewertungen.",
                        "<strong>Live-Guide auf Deutsch und Englisch</strong> bei jeder Fahrt, die meisten anderen spielen eine Aufnahme ab.",
                        "<strong>Glasdach und Heizung</strong>: die beste 1-Stunden-Wahl von November bis März."]},
        "cons": {"en": ["<strong>Commentary in German and English only</strong>, no other languages.",
                        "<strong>Not suitable for wheelchair users</strong> or guests with limited mobility.",
                        "<strong>Drinks cost extra</strong> at the bar on board."],
                 "de": ["<strong>Erklärungen nur auf Deutsch und Englisch</strong>, keine weiteren Sprachen.",
                        "<strong>Nicht geeignet für Rollstuhlfahrer</strong> oder Gäste mit eingeschränkter Mobilität.",
                        "<strong>Getränke kosten extra</strong> an der Bar an Bord."]},
        "review": {"en": ["If you only have an hour, this is the one. Reederei Hadynski runs two glass panorama boats, <strong>MS Carola and MS Franziska</strong>, and puts a <strong>live guide</strong> on every departure who switches between German and English. That is why it rates <strong>4.7 from 7,465 reviews</strong>, the best score of any 1-hour Spree cruise.",
                          "The route is the classic central loop past Museum Island, the Reichstag and the government quarter. In summer the glass roof is fully open; from November it closes and the heating goes on, so it is also the best rainy-day pick. At <strong>€18.06</strong> it costs the same as the audio-guide boats."],
                   "de": ["Wenn du nur eine Stunde hast, ist es diese Fahrt. Die Reederei Hadynski fährt mit zwei Glas-Panoramabooten, <strong>MS Carola und MS Franziska</strong>, und hat bei jeder Abfahrt einen <strong>Live-Guide</strong> an Bord, der zwischen Deutsch und Englisch wechselt. Deshalb steht sie bei <strong>4,7 aus 7.465 Bewertungen</strong>, der besten Note aller 1-Stunden-Spreefahrten.",
                          "Die Route ist die klassische Runde durch die Mitte, vorbei an Museumsinsel, Reichstag und Regierungsviertel. Im Sommer ist das Glasdach ganz offen, ab November wird es geschlossen und die Heizung läuft, also auch die beste Wahl bei Regen. Mit <strong>€18,06</strong> kostet sie so viel wie die Boote mit Audioguide."]},
        "facts": {"en": [("Duration", "1 hour"), ("Commentary", "Live guide in German and English"),
                         ("Pier", "Reederei Hadynski, Anna-Louisa-Karsch-Straße 2, 10178 Berlin (near S Hackescher Markt)"),
                         ("Included", "Cruise, live guide, heated cabin, toilet"), ("Not included", "Drinks (bar on board), tips"),
                         ("Season", "Daily, March to December"), ("Cancellation", "Free up to 24 hours before")],
                  "de": [("Dauer", "1 Stunde"), ("Erklärungen", "Live-Guide auf Deutsch und Englisch"),
                         ("Anleger", "Reederei Hadynski, Anna-Louisa-Karsch-Straße 2, 10178 Berlin (nahe S Hackescher Markt)"),
                         ("Inklusive", "Fahrt, Live-Guide, beheizte Kabine, Toilette"), ("Nicht inklusive", "Getränke (Bar an Bord), Trinkgeld"),
                         ("Saison", "Täglich, März bis Dezember"), ("Stornierung", "Kostenlos bis 24 Stunden vorher")]},
    },
    {
        "key": "bridges-landwehr-canal", "photos": 5, "cats": "long",
        "book": ("tiq", "tickets-for-3-hour-bridges-tour-p1065876"),
        "operator": "Stern und Kreis", "hours": 3.25,
        "price": 32.90, "was": None, "cancel": False,
        "ratings": [("GetYourGuide", 4.63, 4847), ("Tiqets", 2.5, 4)],
        "pier": "Rolandufer 4, 10179 Berlin",
        "pier_short": {"en": "Rolandufer (Jannowitzbrücke)", "de": "Rolandufer (Jannowitzbrücke)"},
        "dur": {"en": "3.25 Hours", "de": "3,25 Stunden"},
        "rank": {"en": "🌉 #2 Best Full City Tour", "de": "🌉 #2 Beste große Stadtrundfahrt"},
        "short": {"en": "Stern und Kreis: Bridges Tour", "de": "Stern und Kreis: Brückenfahrt"},
        "title": {"en": "3.25-Hour Bridges Tour on the Spree and Landwehr Canal",
                  "de": "3,25 Stunden Brückenfahrt auf Spree und Landwehrkanal"},
        "pills": [
            ("🌉", {"en": "Spree + Landwehr Canal", "de": "Spree + Landwehrkanal"},
             {"en": "<strong>A full circle through Berlin:</strong> under about 40 bridges, along the Spree through the centre and back through the Landwehr Canal past the Technikmuseum and Potsdamer Platz.",
              "de": "<strong>Eine ganze Runde durch Berlin:</strong> unter rund 40 Brücken durch, über die Spree durch die Mitte und durch den Landwehrkanal zurück, vorbei am Technikmuseum und am Potsdamer Platz."},
             {"en": "The only cruise here that shows Kreuzberg and the canal side of the city.",
              "de": "Die einzige Fahrt in diesem Vergleich, die Kreuzberg und die Kanalseite der Stadt zeigt."}),
            ("🎧", {"en": "Audio Guide, 11 Languages", "de": "Audioguide, 11 Sprachen"},
             {"en": "<strong>Audio guide:</strong> English, Chinese, Dutch, French, Hebrew, Italian, Polish, Portuguese, Russian, Spanish, Swedish. Commentary on board in German.",
              "de": "<strong>Audioguide:</strong> Englisch, Chinesisch, Niederländisch, Französisch, Hebräisch, Italienisch, Polnisch, Portugiesisch, Russisch, Spanisch, Schwedisch. Erklärungen an Bord auf Deutsch."},
             None),
            ("💶", {"en": "€10 per Hour", "de": "€10 pro Stunde"},
             {"en": "<strong>€32.90 for 3.25 hours</strong> works out at about €10 per hour, half the hourly price of a 1-hour cruise.",
              "de": "<strong>€32,90 für 3,25 Stunden</strong> sind rund €10 pro Stunde, halb so viel pro Stunde wie eine 1-Stunden-Fahrt."},
             {"en": "Food and drinks can be ordered on board.", "de": "Essen und Getränke kann man an Bord bestellen."}),
        ],
        "pick": {"en": "if you have an afternoon and want to see more than the government quarter.",
                 "de": "wenn du einen Nachmittag Zeit hast und mehr als das Regierungsviertel sehen willst."},
        "skip": {"en": "if your plans may change: this ticket is non-refundable.",
                 "de": "wenn sich deine Pläne ändern könnten: dieses Ticket ist nicht erstattbar."},
        "pros": {"en": ["<strong>The longest route through the city</strong>: Spree plus Landwehr Canal in one trip.",
                        "<strong>4.6 from 4,800+ reviews</strong> across two booking sites.",
                        "<strong>About €10 per hour</strong>, the best value of the city-centre cruises."],
                 "de": ["<strong>Die längste Route durch die Stadt</strong>: Spree und Landwehrkanal in einer Fahrt.",
                        "<strong>4,6 aus über 4.800 Bewertungen</strong> auf zwei Buchungsseiten.",
                        "<strong>Rund €10 pro Stunde</strong>, das beste Preis-Leistungs-Verhältnis der Innenstadt-Fahrten."]},
        "cons": {"en": ["<strong>Non-refundable ticket</strong>, no rescheduling.",
                        "<strong>3.25 hours is long</strong> with small children.",
                        "<strong>Window seats are not guaranteed</strong>, so arrive early."],
                 "de": ["<strong>Nicht erstattbares Ticket</strong>, keine Umbuchung.",
                        "<strong>3,25 Stunden sind lang</strong> mit kleinen Kindern.",
                        "<strong>Fensterplätze sind nicht garantiert</strong>, also früh da sein."]},
        "review": {"en": ["Berlin's 1-hour cruises all turn around at the same two points. The <strong>Brückenfahrt</strong> by Stern und Kreis is the one that keeps going: through the centre on the Spree, then back along the <strong>Landwehr Canal</strong> through Kreuzberg, under about 40 bridges, past the Technikmuseum and Potsdamer Platz.",
                          "It is the most-reviewed long cruise in Berlin, with <strong>4.6 from more than 4,800 reviews</strong>, and at <strong>€32.90 for 3.25 hours</strong> it is the cheapest way to see the city from the water per hour. Bring a jacket for the open deck, and know that the ticket cannot be refunded."],
                   "de": ["Alle 1-Stunden-Fahrten in Berlin drehen an denselben zwei Punkten um. Die <strong>Brückenfahrt</strong> von Stern und Kreis fährt weiter: über die Spree durch die Mitte und dann über den <strong>Landwehrkanal</strong> durch Kreuzberg zurück, unter rund 40 Brücken durch, vorbei am Technikmuseum und am Potsdamer Platz.",
                          "Sie ist die meistbewertete lange Fahrt in Berlin, mit <strong>4,6 aus über 4.800 Bewertungen</strong>, und mit <strong>€32,90 für 3,25 Stunden</strong> pro Stunde die günstigste Art, die Stadt vom Wasser aus zu sehen. Nimm eine Jacke fürs offene Deck mit, und denk daran: das Ticket ist nicht erstattbar."]},
        "facts": {"en": [("Duration", "3 hours 15 minutes"), ("Route", "Spree and Landwehr Canal, about 40 bridges"),
                         ("Commentary", "German on board, audio guide in 11 languages"),
                         ("Pier", "Rolandufer 4, 10179 Berlin (near S+U Jannowitzbrücke)"),
                         ("Not included", "Food and drinks (sold on board)"), ("Cancellation", "Non-refundable")],
                  "de": [("Dauer", "3 Stunden 15 Minuten"), ("Route", "Spree und Landwehrkanal, rund 40 Brücken"),
                         ("Erklärungen", "Deutsch an Bord, Audioguide in 11 Sprachen"),
                         ("Anleger", "Rolandufer 4, 10179 Berlin (nahe S+U Jannowitzbrücke)"),
                         ("Nicht inklusive", "Essen und Getränke (an Bord erhältlich)"), ("Stornierung", "Nicht erstattbar")]},
    },
    {
        "key": "stern-und-kreis-1-hour", "photos": 5, "cats": "hour cancel under20",
        "book": ("gyg", "1-hour-spree-cruise-from-friedrichstrasse-t21231"),
        "operator": "Stern und Kreis", "hours": 1.0,
        "price": 18.00, "was": 23, "cancel": True,
        "ratings": [("GetYourGuide", 4.27, 18072), ("Tiqets", 4.3, 69)],
        "pier": "Reichstagufer, 10117 Berlin",
        "pier_short": {"en": "Friedrichstraße or Nikolaiviertel", "de": "Friedrichstraße oder Nikolaiviertel"},
        "dur": {"en": "1 Hour", "de": "1 Stunde"},
        "rank": {"en": "🎧 #3 Most Languages", "de": "🎧 #3 Die meisten Sprachen"},
        "short": {"en": "Stern und Kreis: 1-Hour City Cruise", "de": "Stern und Kreis: 1-Stunden-Fahrt"},
        "title": {"en": "1-Hour City Cruise with an Audio Guide in 12 Languages",
                  "de": "1 Stunde Stadtrundfahrt mit Audioguide in 12 Sprachen"},
        "pills": [
            ("🎧", {"en": "12-Language Audio", "de": "Audioguide, 12 Sprachen"},
             {"en": "<strong>Audio guide device:</strong> English, French, Spanish, Portuguese, Italian, Dutch, Russian, Polish, Swedish, Chinese, Hebrew, Finnish. German commentary over the speakers.",
              "de": "<strong>Audioguide-Gerät:</strong> Englisch, Französisch, Spanisch, Portugiesisch, Italienisch, Niederländisch, Russisch, Polnisch, Schwedisch, Chinesisch, Hebräisch, Finnisch. Deutsche Ansage über Lautsprecher."},
             {"en": "The pick for families who don't speak German or English.",
              "de": "Die Wahl für Familien, die weder Deutsch noch Englisch sprechen."}),
            ("📍", {"en": "Two Piers", "de": "Zwei Anleger"},
             {"en": "<strong>Board at Friedrichstraße (Reichstagufer) or Nikolaiviertel</strong>, whichever is closer. You pick the pier when you book.",
              "de": "<strong>Einstieg an der Friedrichstraße (Reichstagufer) oder im Nikolaiviertel</strong>, je nachdem, was näher liegt. Den Anleger wählst du bei der Buchung."},
             {"en": "Missed your boat? Staff put you on a later departure.",
              "de": "Boot verpasst? Das Personal setzt dich auf eine spätere Abfahrt."}),
            ("🐕", {"en": "Dogs + Pushchairs OK", "de": "Hunde + Kinderwagen OK"},
             {"en": "<strong>Pushchairs can come on board</strong> and dogs on a lead are welcome.",
              "de": "<strong>Kinderwagen dürfen mit an Bord</strong>, Hunde an der Leine sind willkommen."},
             {"en": "Not wheelchair accessible. Own food and drink are not allowed.",
              "de": "Nicht rollstuhlgerecht. Eigenes Essen und Trinken sind nicht erlaubt."}),
        ],
        "pick": {"en": "for the cheapest classic loop, with audio in your own language.",
                 "de": "für die günstigste klassische Runde, mit Audioguide in deiner Sprache."},
        "skip": {"en": "if you want a live guide: #1 has one for the same price.",
                 "de": "wenn du einen Live-Guide willst: #1 hat einen zum selben Preis."},
        "pros": {"en": ["<strong>The most-booked boat tour in Berlin</strong>: 18,000+ reviews.",
                        "<strong>Audio guide in 12 languages</strong>, the widest choice here.",
                        "<strong>€18 with free cancellation</strong> and two central piers."],
                 "de": ["<strong>Die meistgebuchte Bootstour Berlins</strong>: über 18.000 Bewertungen.",
                        "<strong>Audioguide in 12 Sprachen</strong>, die größte Auswahl in diesem Vergleich.",
                        "<strong>€18 mit kostenloser Stornierung</strong> und zwei zentralen Anlegern."]},
        "cons": {"en": ["<strong>Recorded commentary</strong>, no live guide.",
                        "<strong>Lower rating (4.3)</strong> than the smaller boats.",
                        "<strong>Big boats</strong>: window seats are first come, first served."],
                 "de": ["<strong>Aufgezeichnete Erklärungen</strong>, kein Live-Guide.",
                        "<strong>Niedrigere Bewertung (4,3)</strong> als die kleineren Boote.",
                        "<strong>Große Boote</strong>: Fensterplätze nach dem Motto wer zuerst kommt."]},
        "review": {"en": ["Stern und Kreis is Berlin's biggest boat operator, and this is its bread-and-butter trip: <strong>one hour from Friedrichstraße or the Nikolaiviertel</strong>, out past the Reichstag and the Chancellery to the Haus der Kulturen der Welt, turning at Luther Bridge with a view of Bellevue Palace, then back past Museum Island.",
                          "With <strong>more than 18,000 reviews</strong> it is the most-booked boat tour in the city. The rating (4.3) is lower than the smaller boats above, mostly because the commentary is recorded. What it does better than anyone: the <strong>audio guide in 12 languages</strong>, and it costs <strong>€18</strong> with free cancellation."],
                   "de": ["Stern und Kreis ist Berlins größte Reederei, und das ist ihr Klassiker: <strong>eine Stunde ab Friedrichstraße oder Nikolaiviertel</strong>, vorbei an Reichstag und Kanzleramt bis zum Haus der Kulturen der Welt, Wende an der Lutherbrücke mit Blick auf Schloss Bellevue, dann zurück an der Museumsinsel vorbei.",
                          "Mit <strong>über 18.000 Bewertungen</strong> ist sie die meistgebuchte Bootstour der Stadt. Die Note (4,3) liegt unter den kleineren Booten oben, vor allem, weil die Erklärungen aufgezeichnet sind. Was sie besser kann als alle anderen: den <strong>Audioguide in 12 Sprachen</strong>, und sie kostet <strong>€18</strong> mit kostenloser Stornierung."]},
        "facts": {"en": [("Duration", "1 hour"), ("Commentary", "Audio guide in 12 languages, German over the speakers"),
                         ("Pier", "Friedrichstraße (Reichstagufer, 10117 Berlin) or Nikolaiviertel, chosen when booking"),
                         ("Not included", "Food and drinks (sold on board)"), ("Good to know", "Pushchairs and dogs on a lead allowed; not wheelchair accessible"),
                         ("Cancellation", "Free up to 24 hours before")],
                  "de": [("Dauer", "1 Stunde"), ("Erklärungen", "Audioguide in 12 Sprachen, Deutsch über Lautsprecher"),
                         ("Anleger", "Friedrichstraße (Reichstagufer, 10117 Berlin) oder Nikolaiviertel, Wahl bei der Buchung"),
                         ("Nicht inklusive", "Essen und Getränke (an Bord erhältlich)"), ("Gut zu wissen", "Kinderwagen und Hunde an der Leine erlaubt; nicht rollstuhlgerecht"),
                         ("Stornierung", "Kostenlos bis 24 Stunden vorher")]},
    },
    {
        "key": "hemingway", "photos": 5, "cats": "hour cancel",
        "book": ("gyg", "berlin-1h-boutique-style-cruise-on-the-historic-hemingway-t616531"),
        "operator": "FLAGSHIP.BERLIN", "hours": 1.0,
        "price": 25.00, "was": None, "cancel": True,
        "ratings": [("GetYourGuide", 4.66, 1077)],
        "pier": "Anlegestelle Paul-Löbe-Haus, 10117 Berlin",
        "pier_short": {"en": "By the Reichstag", "de": "Am Reichstag"},
        "dur": {"en": "1 to 1.5 Hours", "de": "1 bis 1,5 Stunden"},
        "rank": {"en": "💑 #4 Best for Couples", "de": "💑 #4 Beste für Paare"},
        "short": {"en": "FLAGSHIP.BERLIN: Hemingway", "de": "FLAGSHIP.BERLIN: Hemingway"},
        "title": {"en": "1-Hour Cruise on the Hemingway, a Restored 1908 Steamship",
                  "de": "1 Stunde auf der Hemingway, einem restaurierten Dampfer von 1908"},
        "pills": [
            ("⚡", {"en": "Silent Electric Boat", "de": "Leises Elektroboot"},
             {"en": "<strong>Built in 1908, now electric.</strong> No engine noise, white tablecloths, fresh flowers and a mahogany salon instead of plastic chairs.",
              "de": "<strong>Gebaut 1908, heute elektrisch.</strong> Kein Motorenlärm, weiße Tischdecken, frische Blumen und ein Mahagoni-Salon statt Plastikstühlen."},
             None),
            ("🎧", {"en": "Commentary + Music", "de": "Erklärungen + Musik"},
             {"en": "<strong>A mix of sightseeing commentary in German and English</strong> and quiet background music.",
              "de": "<strong>Eine Mischung aus Erklärungen auf Deutsch und Englisch</strong> und leiser Hintergrundmusik."},
             {"en": "Drinks are served at your seat and cost extra.", "de": "Getränke werden am Platz serviert und kosten extra."}),
            ("📍", {"en": "Pier by the Reichstag", "de": "Anleger am Reichstag"},
             {"en": "<strong>From the Reichstag walk down to the river and turn left.</strong> After about 150 m you see the yellow FLAGSHIP.BERLIN flags.",
              "de": "<strong>Vom Reichstag runter zum Ufer und links halten.</strong> Nach etwa 150 m siehst du die gelben FLAGSHIP.BERLIN-Fahnen."},
             {"en": "Arrive 20 minutes early to choose your seat.", "de": "20 Minuten früher da sein, um den Platz zu wählen."}),
        ],
        "pick": {"en": "for a date: the quietest, most stylish boat on the 1-hour loop.",
                 "de": "für ein Date: das leiseste, stilvollste Boot auf der 1-Stunden-Runde."},
        "skip": {"en": "if price matters most: #1 and #3 cost €7 less.",
                 "de": "wenn der Preis zählt: #1 und #3 kosten €7 weniger."},
        "pros": {"en": ["<strong>A 1908 steamship</strong> with a silent electric engine.",
                        "<strong>Table service</strong> and a salon instead of rows of plastic chairs.",
                        "<strong>4.7 from 1,077 reviews</strong>, free cancellation."],
                 "de": ["<strong>Ein Dampfer von 1908</strong> mit leisem Elektromotor.",
                        "<strong>Service am Platz</strong> und ein Salon statt Reihen aus Plastikstühlen.",
                        "<strong>4,7 aus 1.077 Bewertungen</strong>, kostenlose Stornierung."]},
        "cons": {"en": ["<strong>€25</strong>, the priciest of the 1-hour cruises.",
                        "<strong>Drinks are not included</strong> in the ticket.",
                        "<strong>Not suitable for wheelchair users.</strong>"],
                 "de": ["<strong>€25</strong>, die teuerste der 1-Stunden-Fahrten.",
                        "<strong>Getränke sind nicht im Ticket</strong> enthalten.",
                        "<strong>Nicht geeignet für Rollstuhlfahrer.</strong>"]},
        "review": {"en": ["The <strong>Hemingway</strong> was built in 1908 and restored by FLAGSHIP.BERLIN with a <strong>silent electric engine</strong>, white tablecloths and a mahogany salon. It sails the same central loop as #1 and #3, past the Reichstag, Museum Island and the Nikolaiviertel, but it feels like a different trip: no engine noise, no crowd, drinks brought to your table.",
                          "Reviewers rate it <strong>4.7 from 1,077 reviews</strong>. At <strong>€25</strong> it costs €7 more than the classic boats, which is the price of a quieter hour. Board at the FLAGSHIP.BERLIN pier just below the Reichstag."],
                   "de": ["Die <strong>Hemingway</strong> wurde 1908 gebaut und von FLAGSHIP.BERLIN mit einem <strong>leisen Elektromotor</strong>, weißen Tischdecken und einem Mahagoni-Salon restauriert. Sie fährt dieselbe Runde durch die Mitte wie #1 und #3, vorbei an Reichstag, Museumsinsel und Nikolaiviertel, fühlt sich aber anders an: kein Motorenlärm, kein Gedränge, Getränke an den Tisch.",
                          "Die Gäste geben <strong>4,7 aus 1.077 Bewertungen</strong>. Mit <strong>€25</strong> kostet sie €7 mehr als die klassischen Boote, das ist der Preis für eine ruhigere Stunde. Einstieg am FLAGSHIP.BERLIN-Anleger direkt unterhalb des Reichstags."]},
        "facts": {"en": [("Duration", "1 to 1.5 hours"), ("Boat", "Hemingway, built 1908, electric"),
                         ("Commentary", "German and English, with background music"),
                         ("Pier", "FLAGSHIP.BERLIN, Anlegestelle Paul-Löbe-Haus, government district (U Bundestag)"),
                         ("Not included", "Drinks (served at your seat)"), ("Cancellation", "Free up to 24 hours before")],
                  "de": [("Dauer", "1 bis 1,5 Stunden"), ("Boot", "Hemingway, Baujahr 1908, elektrisch"),
                         ("Erklärungen", "Deutsch und Englisch, mit Hintergrundmusik"),
                         ("Anleger", "FLAGSHIP.BERLIN, Anlegestelle Paul-Löbe-Haus, Regierungsviertel (U Bundestag)"),
                         ("Nicht inklusive", "Getränke (am Platz serviert)"), ("Stornierung", "Kostenlos bis 24 Stunden vorher")]},
    },
    {
        "key": "evening-yacht-aperitif", "photos": 5, "cats": "evening cancel",
        "book": ("gyg", "berlin-evening-yacht-cruise-with-aperitif-t480108"),
        "operator": "FLAGSHIP.BERLIN", "hours": 1.4,
        "price": 39.00, "was": None, "cancel": True,
        "ratings": [("GetYourGuide", 4.55, 625)],
        "pier": "Anlegestelle Paul-Löbe-Haus, 10117 Berlin",
        "pier_short": {"en": "By the Reichstag", "de": "Am Reichstag"},
        "dur": {"en": "75 to 90 Min", "de": "75 bis 90 Min."},
        "rank": {"en": "🌙 #5 Best Evening Cruise", "de": "🌙 #5 Beste Abendfahrt"},
        "short": {"en": "FLAGSHIP.BERLIN: Evening Yacht", "de": "FLAGSHIP.BERLIN: Abend-Yacht"},
        "title": {"en": "Evening Yacht Cruise with a Glass of Crémant",
                  "de": "Abendfahrt mit der Yacht und einem Glas Crémant"},
        "pills": [
            ("🥂", {"en": "Crémant Included", "de": "Crémant inklusive"},
             {"en": "<strong>One glass of Crémant or alcohol-free sparkling wine</strong> on boarding. Long drinks and more wine from the bar cost extra.",
              "de": "<strong>Ein Glas Crémant oder alkoholfreier Sekt</strong> zur Begrüßung. Longdrinks und weiterer Wein von der Bar kosten extra."},
             None),
            ("🌆", {"en": "Sunset, No Lecture", "de": "Sonnenuntergang, kein Vortrag"},
             {"en": "<strong>Not a guided tour.</strong> Music, lounge furniture on the sundeck and the city lighting up as it gets dark.",
              "de": "<strong>Keine Führung.</strong> Musik, Lounge-Möbel auf dem Sonnendeck und die Stadt, die sich im Dunkeln beleuchtet."},
             {"en": "The salon has room for everyone if it rains.", "de": "Bei Regen hat der Salon Platz für alle."}),
            ("🍽️", {"en": "Dinner Add-On", "de": "Dinner-Option"},
             {"en": "<strong>On some dates you can add a 3-course dinner:</strong> the yacht drops you one way at the Patio restaurant ship, where the evening ends.",
              "de": "<strong>An manchen Terminen kannst du ein 3-Gänge-Menü dazubuchen:</strong> die Yacht bringt dich dann einfach zum Restaurantschiff Patio, wo der Abend endet."},
             {"en": "Check the options for your date.", "de": "Die Optionen für dein Datum prüfen."}),
        ],
        "pick": {"en": "for a relaxed start to the evening, drink in hand.",
                 "de": "für einen entspannten Start in den Abend, Glas in der Hand."},
        "skip": {"en": "if you want to learn about the sights: there is no commentary.",
                 "de": "wenn du etwas über die Sehenswürdigkeiten erfahren willst: es gibt keine Erklärungen."},
        "pros": {"en": ["<strong>A glass of Crémant included</strong>, music, lounge seating.",
                        "<strong>Evening departures</strong> as the city lights come on.",
                        "<strong>4.6 from 625 reviews</strong>, free cancellation."],
                 "de": ["<strong>Ein Glas Crémant inklusive</strong>, Musik, Lounge-Plätze.",
                        "<strong>Abendliche Abfahrten</strong>, wenn die Stadt zu leuchten beginnt.",
                        "<strong>4,6 aus 625 Bewertungen</strong>, kostenlose Stornierung."]},
        "cons": {"en": ["<strong>No sightseeing commentary.</strong>",
                        "<strong>€39 for about 75 to 90 minutes</strong>, the second-priciest per hour.",
                        "<strong>Dogs are allowed but lose seat choice.</strong>"],
                 "de": ["<strong>Keine Erklärungen zu den Sehenswürdigkeiten.</strong>",
                        "<strong>€39 für etwa 75 bis 90 Minuten</strong>, pro Stunde die zweitteuerste Fahrt.",
                        "<strong>Hunde erlaubt, aber ohne freie Platzwahl.</strong>"]},
        "review": {"en": ["This is the cruise for people who don't want a cruise lecture. A uniformed crew welcomes you at the <strong>FLAGSHIP.BERLIN pier below the Reichstag</strong> with a <strong>glass of Crémant</strong> (or alcohol-free sparkling wine), and for the next 75 to 90 minutes there is music, lounge furniture on the sundeck and the Spree turning gold and then dark.",
                          "The route is the central loop past Museum Island and the Berlin Cathedral. On some dates you can add a <strong>3-course dinner</strong>: the yacht then takes you one way to the Patio restaurant ship. At <strong>€39</strong> it rates <strong>4.6 from 625 reviews</strong> and can be cancelled free up to 24 hours before."],
                   "de": ["Das ist die Fahrt für alle, die keinen Vortrag wollen. Eine Crew in Uniform empfängt dich am <strong>FLAGSHIP.BERLIN-Anleger unterhalb des Reichstags</strong> mit einem <strong>Glas Crémant</strong> (oder alkoholfreiem Sekt), und die nächsten 75 bis 90 Minuten gibt es Musik, Lounge-Möbel auf dem Sonnendeck und eine Spree, die erst golden und dann dunkel wird.",
                          "Die Route ist die Runde durch die Mitte, vorbei an Museumsinsel und Berliner Dom. An manchen Terminen kannst du ein <strong>3-Gänge-Menü</strong> dazubuchen: die Yacht bringt dich dann zum Restaurantschiff Patio. Mit <strong>€39</strong> kommt sie auf <strong>4,6 aus 625 Bewertungen</strong> und ist bis 24 Stunden vorher kostenlos stornierbar."]},
        "facts": {"en": [("Duration", "75 to 90 minutes"), ("Included", "One glass of Crémant or alcohol-free sparkling wine"),
                         ("Commentary", "None (music and views)"),
                         ("Pier", "FLAGSHIP.BERLIN, Anlegestelle Paul-Löbe-Haus, government district (U Bundestag)"),
                         ("Not included", "Extra drinks; optional 3-course dinner on some dates"), ("Cancellation", "Free up to 24 hours before")],
                  "de": [("Dauer", "75 bis 90 Minuten"), ("Inklusive", "Ein Glas Crémant oder alkoholfreier Sekt"),
                         ("Erklärungen", "Keine (Musik und Aussicht)"),
                         ("Anleger", "FLAGSHIP.BERLIN, Anlegestelle Paul-Löbe-Haus, Regierungsviertel (U Bundestag)"),
                         ("Nicht inklusive", "Weitere Getränke; 3-Gänge-Menü an manchen Terminen zubuchbar"), ("Stornierung", "Kostenlos bis 24 Stunden vorher")]},
    },
    {
        "key": "seven-lakes-wannsee", "photos": 6, "cats": "lakes under20",
        "book": ("tiq", "tickets-for-wannsee-havel-2-hour-7-lake-cruise-p1068753"),
        "operator": "Stern und Kreis", "hours": 1.75,
        "price": 18.90, "was": None, "cancel": False,
        "ratings": [("GetYourGuide", 4.60, 2651), ("Tiqets", 4.3, 139)],
        "pier": "Kronprinzessinnenweg 5, 14109 Berlin",
        "pier_short": {"en": "Wannsee pier (S Wannsee)", "de": "Anleger Wannsee (S Wannsee)"},
        "dur": {"en": "About 1h 45", "de": "Ca. 1:45 Std."},
        "rank": {"en": "🌳 #6 Best Lake Cruise", "de": "🌳 #6 Beste Seenfahrt"},
        "short": {"en": "Stern und Kreis: Seven Lakes", "de": "Stern und Kreis: 7-Seen-Rundfahrt"},
        "title": {"en": "Seven Lakes Cruise from Wannsee", "de": "7-Seen-Rundfahrt ab Wannsee"},
        "pills": [
            ("🌳", {"en": "7 Lakes, No City", "de": "7 Seen statt Stadt"},
             {"en": "<strong>A loop through the south-western Havel lakes:</strong> Kleiner Wannsee, Pohlesee, Stölpchensee, Griebnitzsee, Glienicker See and Jungfernsee, back to Wannsee.",
              "de": "<strong>Eine Runde durch die Havelseen im Südwesten:</strong> Kleiner Wannsee, Pohlesee, Stölpchensee, Griebnitzsee, Glienicker See und Jungfernsee, zurück zum Wannsee."},
             {"en": "Villas, Babelsberg Palace and the Heilandskirche in Sacrow along the way.",
              "de": "Villen, Schloss Babelsberg und die Heilandskirche Sacrow am Ufer."}),
            ("🚆", {"en": "5 Min from S Wannsee", "de": "5 Min. ab S Wannsee"},
             {"en": "<strong>The pier is a 5-minute walk from Wannsee station</strong> (S1, S7 and regional trains), about 25 minutes from the centre.",
              "de": "<strong>Der Anleger liegt 5 Gehminuten vom Bahnhof Wannsee</strong> (S1, S7 und Regionalzüge), etwa 25 Minuten aus der Mitte."},
             {"en": "Combine it with a walk on Peacock Island or in the Grunewald.",
              "de": "Gut kombinierbar mit einem Spaziergang auf der Pfaueninsel oder im Grunewald."}),
            ("💶", {"en": "€10.80 per Hour", "de": "€10,80 pro Stunde"},
             {"en": "<strong>€18.90 for about 1 hour 45 minutes.</strong> Food and drinks are sold on board.",
              "de": "<strong>€18,90 für rund 1 Stunde 45 Minuten.</strong> Essen und Getränke gibt es an Bord."},
             None),
        ],
        "pick": {"en": "for a calm, green half-day out of the city for under €20.",
                 "de": "für einen ruhigen, grünen halben Tag raus aus der Stadt für unter €20."},
        "skip": {"en": "if it is your first day in Berlin: you won't see a single landmark of the centre.",
                 "de": "wenn es dein erster Tag in Berlin ist: du siehst keine einzige Sehenswürdigkeit der Mitte."},
        "pros": {"en": ["<strong>Lakes, villas and palaces</strong> instead of government buildings.",
                        "<strong>4.6 from 2,700+ reviews</strong> across two booking sites.",
                        "<strong>€18.90</strong>, one of the cheapest cruises here."],
                 "de": ["<strong>Seen, Villen und Schlösser</strong> statt Regierungsgebäuden.",
                        "<strong>4,6 aus über 2.700 Bewertungen</strong> auf zwei Buchungsseiten.",
                        "<strong>€18,90</strong>, eine der günstigsten Fahrten in diesem Vergleich."]},
        "cons": {"en": ["<strong>25 minutes by S-Bahn</strong> from the centre each way.",
                        "<strong>Non-refundable ticket.</strong>",
                        "<strong>Best in summer</strong>: in winter the lakes are grey and quiet."],
                 "de": ["<strong>25 Minuten S-Bahn</strong> pro Richtung aus der Mitte.",
                        "<strong>Nicht erstattbares Ticket.</strong>",
                        "<strong>Am schönsten im Sommer</strong>: im Winter sind die Seen grau und still."]},
        "review": {"en": ["Berliners don't take their visitors on the Spree, they take them to the lakes. The <strong>7-Seen-Rundfahrt</strong> leaves from the Wannsee pier, 5 minutes on foot from the S-Bahn, and loops through six smaller Havel lakes past lakeside villas, <strong>Babelsberg Palace</strong> and the Heilandskirche in Sacrow before returning.",
                          "It rates <strong>4.6 from more than 2,700 reviews</strong> and costs <strong>€18.90</strong>. Pair it with Peacock Island or a walk in the Grunewald for a full day. The trade-off: it takes about 25 minutes on the S-Bahn to get there, and the ticket is non-refundable."],
                   "de": ["Berliner fahren mit ihrem Besuch nicht auf der Spree, sondern an die Seen. Die <strong>7-Seen-Rundfahrt</strong> startet am Anleger Wannsee, 5 Minuten zu Fuß von der S-Bahn, und dreht eine Runde durch sechs kleinere Havelseen, vorbei an Villen am Ufer, <strong>Schloss Babelsberg</strong> und der Heilandskirche Sacrow.",
                          "Sie kommt auf <strong>4,6 aus über 2.700 Bewertungen</strong> und kostet <strong>€18,90</strong>. Mit der Pfaueninsel oder einem Spaziergang im Grunewald wird ein ganzer Tag daraus. Der Haken: rund 25 Minuten S-Bahn bis dorthin, und das Ticket ist nicht erstattbar."]},
        "facts": {"en": [("Duration", "About 1 hour 45 minutes"), ("Route", "Wannsee, Pohlesee, Stölpchensee, Griebnitzsee, Glienicker See, Jungfernsee"),
                         ("Pier", "Wannsee pier, Kronprinzessinnenweg 5, 14109 Berlin (5 min walk from S Wannsee)"),
                         ("Not included", "Food and drinks (sold on board)"), ("Cancellation", "Non-refundable")],
                  "de": [("Dauer", "Rund 1 Stunde 45 Minuten"), ("Route", "Wannsee, Pohlesee, Stölpchensee, Griebnitzsee, Glienicker See, Jungfernsee"),
                         ("Anleger", "Anleger Wannsee, Kronprinzessinnenweg 5, 14109 Berlin (5 Min. zu Fuß ab S Wannsee)"),
                         ("Nicht inklusive", "Essen und Getränke (an Bord erhältlich)"), ("Stornierung", "Nicht erstattbar")]},
    },
    {
        "key": "east-side-gallery", "photos": 6, "cats": "long",
        "book": ("tiq", "tickets-for-berlin-east-side-tour-on-cruise-p1068188"),
        "operator": "BWSG", "hours": 2.5,
        "price": 30.00, "was": None, "cancel": False,
        "ratings": [("Tiqets", 4.5, 36)],
        "pier": "Burgstraße 27, 10178 Berlin",
        "pier_short": {"en": "Alte Börse (Hackescher Markt)", "de": "Alte Börse (Hackescher Markt)"},
        "dur": {"en": "2.5 Hours", "de": "2,5 Stunden"},
        "rank": {"en": "🎨 #7 Best for East Berlin", "de": "🎨 #7 Beste für den Osten"},
        "short": {"en": "BWSG: East Side Cruise", "de": "BWSG: East-Side-Tour"},
        "title": {"en": "2.5-Hour East Side Cruise past the Oberbaumbrücke",
                  "de": "2,5 Stunden East-Side-Tour unter der Oberbaumbrücke durch"},
        "pills": [
            ("🎨", {"en": "East Side Gallery", "de": "East Side Gallery"},
             {"en": "<strong>The only cruise here that goes east:</strong> under the Oberbaumbrücke into the Osthafen, past the East Side Gallery, the Molecule Man and the arena.",
              "de": "<strong>Die einzige Fahrt in diesem Vergleich, die nach Osten fährt:</strong> unter der Oberbaumbrücke durch in den Osthafen, vorbei an East Side Gallery, Molecule Man und Arena."},
             {"en": "It also covers the centre: Berliner Dom, Humboldt Forum, Reichstag and Hauptbahnhof.",
              "de": "Die Mitte ist auch dabei: Berliner Dom, Humboldt Forum, Reichstag und Hauptbahnhof."}),
            ("🎧", {"en": "DE/EN + 6 Audio", "de": "DE/EN + 6 Audio"},
             {"en": "<strong>German and English over the speakers</strong>, plus an audio guide in Spanish, French, Italian, Russian, Polish and Hebrew.",
              "de": "<strong>Deutsch und Englisch über Lautsprecher</strong>, dazu Audioguide auf Spanisch, Französisch, Italienisch, Russisch, Polnisch und Hebräisch."},
             None),
            ("📍", {"en": "Pier at Hackescher Markt", "de": "Anleger am Hackeschen Markt"},
             {"en": "<strong>Board at the Alte Börse pier</strong> opposite Burgstraße 27, next to Friedrichsbrücke and Museum Island, a few minutes from S Hackescher Markt.",
              "de": "<strong>Einstieg am Anleger Alte Börse</strong> gegenüber Burgstraße 27, neben Friedrichsbrücke und Museumsinsel, wenige Minuten von S Hackescher Markt."},
             {"en": "Arrive 15 minutes early to swap your ticket for a boarding pass.",
              "de": "15 Minuten früher da sein, um das Ticket gegen eine Bordkarte zu tauschen."}),
        ],
        "pick": {"en": "to see the East Side Gallery and Oberbaumbrücke from the water.",
                 "de": "um East Side Gallery und Oberbaumbrücke vom Wasser aus zu sehen."},
        "skip": {"en": "if you want flexibility: non-refundable, and only 36 reviews so far.",
                 "de": "wenn du flexibel bleiben willst: nicht erstattbar, und bisher nur 36 Bewertungen."},
        "pros": {"en": ["<strong>Centre plus the East Side</strong>: Oberbaumbrücke, East Side Gallery, Molecule Man.",
                        "<strong>Commentary in 8 languages</strong> (2 live over speakers, 6 by audio guide).",
                        "<strong>4.5/5</strong> on the booking listing."],
                 "de": ["<strong>Mitte plus East Side</strong>: Oberbaumbrücke, East Side Gallery, Molecule Man.",
                        "<strong>Erklärungen in 8 Sprachen</strong> (2 über Lautsprecher, 6 per Audioguide).",
                        "<strong>4,5/5</strong> im Buchungsangebot."]},
        "cons": {"en": ["<strong>Non-refundable ticket.</strong>",
                        "<strong>Only 36 reviews</strong>, fewer than the big operators.",
                        "<strong>Recorded commentary</strong>, no live guide."],
                 "de": ["<strong>Nicht erstattbares Ticket.</strong>",
                        "<strong>Nur 36 Bewertungen</strong>, weniger als bei den großen Reedereien.",
                        "<strong>Aufgezeichnete Erklärungen</strong>, kein Live-Guide."]},
        "review": {"en": ["Every other cruise in the centre turns around at the Mühlendamm lock. This one from BWSG keeps going east: <strong>under the Oberbaumbrücke</strong>, along the <strong>East Side Gallery</strong>, into the Osthafen past the Molecule Man sculpture and the arena, and then all the way back west to the Reichstag and the Hauptbahnhof.",
                          "It leaves from the <strong>Alte Börse pier at Hackescher Markt</strong>, costs <strong>€30 for 2.5 hours</strong> and has commentary in German and English plus an audio guide in six more languages. It rates <strong>4.5</strong>, but from only 36 reviews, and the ticket is non-refundable."],
                   "de": ["Jede andere Fahrt in der Mitte dreht an der Mühlendammschleuse um. Diese von der BWSG fährt weiter nach Osten: <strong>unter der Oberbaumbrücke durch</strong>, an der <strong>East Side Gallery</strong> entlang, in den Osthafen vorbei am Molecule Man und der Arena, und dann ganz zurück nach Westen bis Reichstag und Hauptbahnhof.",
                          "Sie startet am <strong>Anleger Alte Börse am Hackeschen Markt</strong>, kostet <strong>€30 für 2,5 Stunden</strong> und hat Erklärungen auf Deutsch und Englisch plus Audioguide in sechs weiteren Sprachen. Sie kommt auf <strong>4,5</strong>, allerdings aus nur 36 Bewertungen, und das Ticket ist nicht erstattbar."]},
        "facts": {"en": [("Duration", "2.5 hours"), ("Route", "Museum Island, Oberbaumbrücke, East Side Gallery, Osthafen, Reichstag, Hauptbahnhof"),
                         ("Commentary", "German and English on board; audio guide in Spanish, French, Italian, Russian, Polish, Hebrew"),
                         ("Pier", "Alte Börse, opposite Burgstraße 27, 10178 Berlin (S Hackescher Markt)"),
                         ("Cancellation", "Non-refundable")],
                  "de": [("Dauer", "2,5 Stunden"), ("Route", "Museumsinsel, Oberbaumbrücke, East Side Gallery, Osthafen, Reichstag, Hauptbahnhof"),
                         ("Erklärungen", "Deutsch und Englisch an Bord; Audioguide auf Spanisch, Französisch, Italienisch, Russisch, Polnisch, Hebräisch"),
                         ("Anleger", "Alte Börse, gegenüber Burgstraße 27, 10178 Berlin (S Hackescher Markt)"),
                         ("Stornierung", "Nicht erstattbar")]},
    },
    {
        "key": "potsdam-world-heritage", "photos": 5, "cats": "lakes long cancel",
        "book": ("gyg", "berlin-world-heritage-cruise-to-potsdam-3-hours-t28802"),
        "operator": "Stern und Kreis", "hours": 3.0,
        "price": 21.90, "was": None, "cancel": True,
        "ratings": [("GetYourGuide", 4.55, 1906)],
        "pier": "Kronprinzessinnenweg 5, 14109 Berlin",
        "pier_short": {"en": "Wannsee pier (S Wannsee)", "de": "Anleger Wannsee (S Wannsee)"},
        "dur": {"en": "3 Hours", "de": "3 Stunden"},
        "rank": {"en": "🏰 #8 Best for Palaces", "de": "🏰 #8 Beste für Schlösser"},
        "short": {"en": "Stern und Kreis: Potsdam", "de": "Stern und Kreis: Potsdam"},
        "title": {"en": "3-Hour World Heritage Cruise to Potsdam", "de": "3 Stunden Welterbe-Fahrt nach Potsdam"},
        "pills": [
            ("🏰", {"en": "UNESCO Palaces", "de": "UNESCO-Schlösser"},
             {"en": "<strong>Wannsee to Potsdam and back:</strong> Peacock Island, Nikolskoe, Cecilienhof Palace, Glienicke Bridge, Babelsberg Palace and Potsdam's Lange Brücke.",
              "de": "<strong>Vom Wannsee nach Potsdam und zurück:</strong> Pfaueninsel, Nikolskoe, Schloss Cecilienhof, Glienicker Brücke, Schloss Babelsberg und die Lange Brücke in Potsdam."},
             {"en": "Glienicke Bridge is the Cold War 'bridge of spies'.",
              "de": "Die Glienicker Brücke ist die Agentenbrücke aus dem Kalten Krieg."}),
            ("🎙️", {"en": "Info DE/EN", "de": "Infos DE/EN"},
             {"en": "<strong>Commentary in German and English</strong> over the onboard system.",
              "de": "<strong>Erklärungen auf Deutsch und Englisch</strong> über die Bordanlage."},
             {"en": "Food and drinks are sold on board.", "de": "Essen und Getränke gibt es an Bord."}),
            ("💶", {"en": "€7.30 per Hour", "de": "€7,30 pro Stunde"},
             {"en": "<strong>€21.90 for 3 hours</strong>, with free cancellation up to 24 hours before.",
              "de": "<strong>€21,90 für 3 Stunden</strong>, kostenlos stornierbar bis 24 Stunden vorher."},
             None),
        ],
        "pick": {"en": "to see Potsdam's palaces without a day trip by train and bus.",
                 "de": "um Potsdams Schlösser ohne Tagesausflug mit Bahn und Bus zu sehen."},
        "skip": {"en": "if you want to visit the palaces: the boat passes them, it doesn't stop.",
                 "de": "wenn du die Schlösser besichtigen willst: das Schiff fährt vorbei, es hält nicht."},
        "pros": {"en": ["<strong>Palaces and parks of a UNESCO World Heritage site</strong> from the water.",
                        "<strong>Glienicke Bridge</strong> and Peacock Island on one trip.",
                        "<strong>€7.30 per hour</strong> with free cancellation."],
                 "de": ["<strong>Schlösser und Parks eines UNESCO-Welterbes</strong> vom Wasser aus.",
                        "<strong>Glienicker Brücke</strong> und Pfaueninsel auf einer Fahrt.",
                        "<strong>€7,30 pro Stunde</strong> mit kostenloser Stornierung."]},
        "cons": {"en": ["<strong>Starts in Wannsee</strong>, 25 minutes by S-Bahn from the centre.",
                        "<strong>No stops</strong>: you see Potsdam, you don't visit it.",
                        "<strong>Window seats not guaranteed.</strong>"],
                 "de": ["<strong>Start am Wannsee</strong>, 25 Minuten S-Bahn aus der Mitte.",
                        "<strong>Keine Stopps</strong>: du siehst Potsdam, du besichtigst es nicht.",
                        "<strong>Fensterplätze nicht garantiert.</strong>"]},
        "review": {"en": ["From the same Wannsee pier as #6, this longer Stern und Kreis trip heads down the Havel to <strong>Potsdam and back in 3 hours</strong>. On the way: Peacock Island, the church at Nikolskoe, <strong>Cecilienhof Palace</strong>, the <strong>Glienicke Bridge</strong> of Cold War spy swaps, Babelsberg Palace and the Lange Brücke in Potsdam.",
                          "It rates <strong>4.5 from 1,906 reviews</strong> and costs <strong>€21.90</strong>, about €7 per hour, with commentary in German and English and free cancellation. If you would rather walk around Sanssouci, take the train instead; this is the way to see the whole World Heritage landscape in one afternoon."],
                   "de": ["Vom selben Anleger am Wannsee wie #6 fährt diese längere Tour von Stern und Kreis die Havel hinunter <strong>nach Potsdam und in 3 Stunden zurück</strong>. Unterwegs: Pfaueninsel, die Kirche in Nikolskoe, <strong>Schloss Cecilienhof</strong>, die <strong>Glienicker Brücke</strong> der Agentenaustausche, Schloss Babelsberg und die Lange Brücke in Potsdam.",
                          "Sie kommt auf <strong>4,5 aus 1.906 Bewertungen</strong> und kostet <strong>€21,90</strong>, rund €7 pro Stunde, mit Erklärungen auf Deutsch und Englisch und kostenloser Stornierung. Wer lieber durch Sanssouci laufen will, nimmt den Zug; das hier ist der Weg, die ganze Welterbe-Landschaft an einem Nachmittag zu sehen."]},
        "facts": {"en": [("Duration", "3 hours"), ("Route", "Wannsee, Peacock Island, Cecilienhof, Glienicke Bridge, Babelsberg, Potsdam Lange Brücke, back"),
                         ("Commentary", "German and English over the onboard system"),
                         ("Pier", "Wannsee pier, Kronprinzessinnenweg 5, 14109 Berlin (S Wannsee)"),
                         ("Not included", "Food and drinks (sold on board)"), ("Cancellation", "Free up to 24 hours before")],
                  "de": [("Dauer", "3 Stunden"), ("Route", "Wannsee, Pfaueninsel, Cecilienhof, Glienicker Brücke, Babelsberg, Lange Brücke Potsdam, zurück"),
                         ("Erklärungen", "Deutsch und Englisch über die Bordanlage"),
                         ("Anleger", "Anleger Wannsee, Kronprinzessinnenweg 5, 14109 Berlin (S Wannsee)"),
                         ("Nicht inklusive", "Essen und Getränke (an Bord erhältlich)"), ("Stornierung", "Kostenlos bis 24 Stunden vorher")]},
    },
    {
        "key": "muggelsee", "photos": 6, "cats": "lakes long cancel",
        "book": ("tiq", "tickets-for-berlin-boat-trip-to-muggelsee-p1124582"),
        "operator": "Stern und Kreis", "hours": 3.5,
        "price": 21.90, "was": None, "cancel": True,
        "ratings": [("GetYourGuide", 4.58, 2436), ("Tiqets", 4.7, 12)],
        "pier": "Puschkinallee 15, 12435 Berlin",
        "pier_short": {"en": "Treptow (S Treptower Park)", "de": "Treptow (S Treptower Park)"},
        "dur": {"en": "3.5 Hours", "de": "3,5 Stunden"},
        "rank": {"en": "💶 #9 Most Hours per Euro", "de": "💶 #9 Meiste Stunden pro Euro"},
        "short": {"en": "Stern und Kreis: Müggelsee", "de": "Stern und Kreis: Müggelsee"},
        "title": {"en": "3.5-Hour Spree Cruise to Müggelsee", "de": "3,5 Stunden Spreefahrt zum Müggelsee"},
        "pills": [
            ("🌲", {"en": "Köpenick + Müggelsee", "de": "Köpenick + Müggelsee"},
             {"en": "<strong>Up the Spree to Berlin's largest lake:</strong> Treptower Park, the old factories of Oberschöneweide, Köpenick Palace and old town, Friedrichshagen, then Müggelsee with a view of the Müggelturm.",
              "de": "<strong>Die Spree hinauf zum größten See Berlins:</strong> Treptower Park, die alten Fabriken von Oberschöneweide, Schloss und Altstadt Köpenick, Friedrichshagen, dann der Müggelsee mit Blick auf den Müggelturm."},
             None),
            ("💶", {"en": "€6.30 per Hour", "de": "€6,30 pro Stunde"},
             {"en": "<strong>€21.90 for 3.5 hours</strong>, the lowest price per hour of all 10 cruises.",
              "de": "<strong>€21,90 für 3,5 Stunden</strong>, der niedrigste Preis pro Stunde aller 10 Fahrten."},
             {"en": "Food is sold on board.", "de": "Essen gibt es an Bord zu kaufen."}),
            ("✅", {"en": "Free Cancellation", "de": "Kostenlos stornierbar"},
             {"en": "<strong>Cancel for free or reschedule up to 24 hours before</strong> your date.",
              "de": "<strong>Kostenlos stornieren oder umbuchen</strong> bis 24 Stunden vor deinem Termin."},
             None),
        ],
        "pick": {"en": "for a long, cheap, green day on the water in the east of the city.",
                 "de": "für einen langen, günstigen, grünen Tag auf dem Wasser im Osten der Stadt."},
        "skip": {"en": "if you only have a few hours in Berlin: it skips the centre entirely.",
                 "de": "wenn du nur ein paar Stunden in Berlin hast: die Mitte ist gar nicht dabei."},
        "pros": {"en": ["<strong>€6.30 per hour</strong>, the cheapest hour on the water in Berlin.",
                        "<strong>4.6 from 2,400+ reviews</strong> across two booking sites.",
                        "<strong>Free cancellation</strong> and rescheduling up to 24 hours before."],
                 "de": ["<strong>€6,30 pro Stunde</strong>, die günstigste Stunde auf dem Wasser in Berlin.",
                        "<strong>4,6 aus über 2.400 Bewertungen</strong> auf zwei Buchungsseiten.",
                        "<strong>Kostenlose Stornierung</strong> und Umbuchung bis 24 Stunden vorher."]},
        "cons": {"en": ["<strong>No city-centre sights.</strong>",
                        "<strong>3.5 hours</strong> is a big chunk of a short trip.",
                        "<strong>Starts in Treptow</strong>, not in Mitte."],
                 "de": ["<strong>Keine Sehenswürdigkeiten der Mitte.</strong>",
                        "<strong>3,5 Stunden</strong> sind viel Zeit bei einem kurzen Besuch.",
                        "<strong>Start in Treptow</strong>, nicht in Mitte."]},
        "review": {"en": ["The other way out of the city. This Stern und Kreis trip leaves <strong>Treptow harbour</strong> by Treptower Park and follows the Spree south-east past the old factory district of Oberschöneweide and <strong>Köpenick Palace</strong> to <strong>Müggelsee</strong>, Berlin's largest lake.",
                          "At <strong>€21.90 for 3.5 hours</strong> it is the cheapest hour on the water in this list, it rates <strong>4.6 from more than 2,400 reviews</strong>, and it is one of the few Tiqets tickets here you can cancel or reschedule for free up to 24 hours before."],
                   "de": ["Der andere Weg raus aus der Stadt. Diese Fahrt von Stern und Kreis startet im <strong>Hafen Treptow</strong> am Treptower Park und folgt der Spree nach Südosten, vorbei am alten Industrieviertel Oberschöneweide und <strong>Schloss Köpenick</strong> bis zum <strong>Müggelsee</strong>, dem größten See Berlins.",
                          "Mit <strong>€21,90 für 3,5 Stunden</strong> ist sie die günstigste Stunde auf dem Wasser in dieser Liste, sie kommt auf <strong>4,6 aus über 2.400 Bewertungen</strong>, und sie ist eines der wenigen Tiqets-Tickets hier, das du bis 24 Stunden vorher kostenlos stornieren oder umbuchen kannst."]},
        "facts": {"en": [("Duration", "3.5 hours"), ("Route", "Treptower Park, Oberschöneweide, Köpenick Palace, Friedrichshagen, Müggelsee"),
                         ("Pier", "Treptow harbour, Puschkinallee 15, 12435 Berlin (S Treptower Park)"),
                         ("Not included", "Food and drinks (sold on board)"), ("Cancellation", "Free up to 24 hours before, rescheduling possible")],
                  "de": [("Dauer", "3,5 Stunden"), ("Route", "Treptower Park, Oberschöneweide, Schloss Köpenick, Friedrichshagen, Müggelsee"),
                         ("Anleger", "Hafen Treptow, Puschkinallee 15, 12435 Berlin (S Treptower Park)"),
                         ("Nicht inklusive", "Essen und Getränke (an Bord erhältlich)"), ("Stornierung", "Kostenlos bis 24 Stunden vorher, Umbuchung möglich")]},
    },
    {
        "key": "dinner-cruise", "photos": 6, "cats": "evening long",
        "book": ("tiq", "tickets-for-berlin-dinner-cruise-p978867"),
        "operator": "Reederei Becker", "hours": 2.5,
        "price": 79.90, "was": None, "cancel": False,
        "ratings": [("GetYourGuide", 4.50, 371), ("Tiqets", 4.2, 11)],
        "pier": "Wintersteinstraße 24, 10587 Berlin",
        "pier_short": {"en": "Charlottenburg (U Richard-Wagner-Platz)", "de": "Charlottenburg (U Richard-Wagner-Platz)"},
        "dur": {"en": "2.5 Hours", "de": "2,5 Stunden"},
        "rank": {"en": "🍽️ #10 Best Dinner Cruise", "de": "🍽️ #10 Beste Dinnerfahrt"},
        "short": {"en": "Reederei Becker: Dinner Cruise", "de": "Reederei Becker: Dinnerfahrt"},
        "title": {"en": "2.5-Hour Dinner Cruise on the MS Der Fliegende Holländer",
                  "de": "2,5 Stunden Dinnerfahrt auf der MS Der Fliegende Holländer"},
        "pills": [
            ("🍽️", {"en": "3 or 4 Courses", "de": "3 oder 4 Gänge"},
             {"en": "<strong>Berlin Dinner:</strong> welcome Prosecco, 3-course menu and one drink with dinner. <strong>Capital Dinner:</strong> 4 courses, all drinks included (beer, wine, Prosecco, soft drinks) and a guaranteed window seat.",
              "de": "<strong>Berlin Dinner:</strong> Prosecco zur Begrüßung, 3-Gänge-Menü und ein Getränk zum Essen. <strong>Capital Dinner:</strong> 4 Gänge, alle Getränke inklusive (Bier, Wein, Prosecco, Softdrinks) und garantierter Fensterplatz."},
             {"en": "Meat and vegetarian options; the 3-course menu has no fish.",
              "de": "Fleisch und vegetarisch; im 3-Gänge-Menü gibt es keinen Fisch."}),
            ("🕡", {"en": "18:30 Departure", "de": "Abfahrt 18:30"},
             {"en": "<strong>One departure, 18:30.</strong> Arrive 15 minutes early and show your phone ticket at the pier.",
              "de": "<strong>Eine Abfahrt, 18:30 Uhr.</strong> 15 Minuten früher da sein und das Handy-Ticket am Anleger zeigen."},
             {"en": "Audio guide in English and German during the cruise.",
              "de": "Audioguide auf Englisch und Deutsch während der Fahrt."}),
            ("📍", {"en": "Pier in Charlottenburg", "de": "Anleger in Charlottenburg"},
             {"en": "<strong>The pier has no street address</strong>; it is by Wintersteinstraße 24 in Charlottenburg. Nearest U-Bahn: Richard-Wagner-Platz (U7).",
              "de": "<strong>Der Anleger hat keine eigene Adresse</strong>; er liegt bei der Wintersteinstraße 24 in Charlottenburg. Nächste U-Bahn: Richard-Wagner-Platz (U7)."},
             {"en": "Card payments: the bar on board takes cash only.",
              "de": "Bezahlen: die Bar an Bord nimmt nur Bargeld."}),
        ],
        "pick": {"en": "for a sit-down dinner with the Reichstag and Museum Island going by.",
                 "de": "für ein richtiges Abendessen, während Reichstag und Museumsinsel vorbeiziehen."},
        "skip": {"en": "if you want flexibility: non-refundable, and the pier is out in Charlottenburg.",
                 "de": "wenn du flexibel bleiben willst: nicht erstattbar, und der Anleger liegt draußen in Charlottenburg."},
        "pros": {"en": ["<strong>A real 3 or 4-course dinner</strong>, not a snack box.",
                        "<strong>All drinks included</strong> on the Capital Dinner option, plus a window seat.",
                        "<strong>4.5 from 380+ reviews</strong> across two booking sites."],
                 "de": ["<strong>Ein echtes 3- oder 4-Gänge-Menü</strong>, keine Snackbox.",
                        "<strong>Alle Getränke inklusive</strong> beim Capital Dinner, dazu ein Fensterplatz.",
                        "<strong>4,5 aus über 380 Bewertungen</strong> auf zwei Buchungsseiten."]},
        "cons": {"en": ["<strong>Non-refundable ticket</strong>, no rescheduling.",
                        "<strong>Pier in Charlottenburg</strong>, west of the centre.",
                        "<strong>Cash only</strong> at the bar on board."],
                 "de": ["<strong>Nicht erstattbares Ticket</strong>, keine Umbuchung.",
                        "<strong>Anleger in Charlottenburg</strong>, westlich der Mitte.",
                        "<strong>Nur Bargeld</strong> an der Bar an Bord."]},
        "review": {"en": ["Berlin's dinner cruise: the <strong>MS Der Fliegende Holländer</strong> of Reederei Becker leaves at <strong>18:30</strong> from Charlottenburg and spends 2.5 hours sailing past Bellevue Palace, the Reichstag, Museum Island and Alexanderplatz while you eat at your own table.",
                          "There are two menus. The <strong>Berlin Dinner</strong> (from <strong>€79.90</strong>) is a welcome Prosecco, three courses and one drink. The <strong>Capital Dinner</strong> adds a fourth course, <strong>all drinks included</strong> and a guaranteed window seat. It rates <strong>4.5 from more than 380 reviews</strong>. The ticket is non-refundable and the bar takes cash only."],
                   "de": ["Berlins Dinnerfahrt: die <strong>MS Der Fliegende Holländer</strong> der Reederei Becker legt um <strong>18:30 Uhr</strong> in Charlottenburg ab und fährt 2,5 Stunden an Schloss Bellevue, Reichstag, Museumsinsel und Alexanderplatz vorbei, während du am eigenen Tisch isst.",
                          "Es gibt zwei Menüs. Das <strong>Berlin Dinner</strong> (ab <strong>€79,90</strong>) bringt Prosecco zur Begrüßung, drei Gänge und ein Getränk. Das <strong>Capital Dinner</strong> legt einen vierten Gang, <strong>alle Getränke inklusive</strong> und einen garantierten Fensterplatz drauf. Bewertung: <strong>4,5 aus über 380 Bewertungen</strong>. Das Ticket ist nicht erstattbar und die Bar nimmt nur Bargeld."]},
        "facts": {"en": [("Duration", "2.5 hours, departs 18:30"), ("Menus", "Berlin Dinner: Prosecco, 3 courses, 1 drink. Capital Dinner: 4 courses, all drinks, window seat"),
                         ("Pier", "By Wintersteinstraße 24, 10587 Berlin (U Richard-Wagner-Platz)"),
                         ("Commentary", "Audio guide in English and German"),
                         ("Good to know", "Cash only at the bar"), ("Cancellation", "Non-refundable")],
                  "de": [("Dauer", "2,5 Stunden, Abfahrt 18:30 Uhr"), ("Menüs", "Berlin Dinner: Prosecco, 3 Gänge, 1 Getränk. Capital Dinner: 4 Gänge, alle Getränke, Fensterplatz"),
                         ("Anleger", "Bei Wintersteinstraße 24, 10587 Berlin (U Richard-Wagner-Platz)"),
                         ("Erklärungen", "Audioguide auf Englisch und Deutsch"),
                         ("Gut zu wissen", "Nur Bargeld an der Bar"), ("Stornierung", "Nicht erstattbar")]},
    },
]

# ---------------------------------------------------------------------------
# PAGE COPY
# ---------------------------------------------------------------------------
T = {
    "en": {
        "title": "10 Best Berlin Boat Tours (2026): Spree Cruises Compared",
        "h1": "The 10 Best Berlin Boat Tours", "kicker": "2026 Spree Cruise Comparison",
        "desc": "Berlin boat tours compared: 10 Spree, canal and lake cruises from €18, with piers, price per hour, live or audio guide and which ones cancel for free.",
        "home": "Home", "home_href": "/", "updated": "Last updated", "author_role": "Owner &amp; Head Cruise Detective",
        "author_sub": "Compared side by side on live listings • Independent comparison",
        "lead": "Nearly every 1-hour Spree cruise runs the same loop past the Reichstag and Museum Island for €17 to €25, so the real choice is the boat, the guide and the pier: here are the 10 worth booking, from a <strong>€6-per-hour lake trip</strong> to a <strong>4-course dinner cruise</strong>.",
        "qp_title": "Quick picks",
        "qp": [("Best overall", 1, "glass-roof boat with a live guide, €18"),
               ("Best long tour", 2, "Spree + Landwehr Canal in 3.25 hours"),
               ("Best evening", 5, "yacht with a glass of Crémant"),
               ("Best value", 9, "3.5 hours to Müggelsee, €6.30 an hour")],
        "filters": "Filters:", "all": "All",
        "flt": [("hour", "⏱️ 1-hour city loop"), ("lakes", "🌳 Lakes &amp; palaces"), ("evening", "🌙 Evening &amp; dinner"),
                ("cancel", "✅ Free cancellation"), ("under20", "💶 Under €20")],
        "per_adult": "per adult", "check": "Check Availability →", "via": "Booked securely via {}",
        "free_cancel": "✓ Free cancellation up to 24h before", "nonref": "Non-refundable ticket", "mobile": "✓ Instant mobile ticket",
        "read": "Read review ↓", "pick": "✓ Pick it", "skip": "✕ Skip it",
        "rate_head": "Average of {} booking sites, weighted by number of reviews", "rate_head1": "Rating on the booking site",
        "reviews": "reviews", "sites": "sites",
        "breakdown": "Detailed Breakdown: 10 Berlin Boat Tours",
        "breakdown_sub": "Route, pier, price per hour and what is included, boat by boat",
        "expand": "Expand All", "collapse": "Collapse All", "pros": "Pros:", "cons": "Cons:",
        "photos": "📸 Photos", "swipe": "Swipe {} Photos →", "summary": "Summary &amp; Review", "overview": "Overview",
        "qf": "Quick Facts", "photo_cap": "Photo: {} via {}", "cta_from": "Check Availability: €{} →",
        "toc": "Table of Contents", "toc_deck": "Top 10 Berlin Boat Tours", "toc_breakdown": "Detailed Breakdown (10 Boat Tours)",
        "sticky_all": "All 10 Boat Tours", "sheet": "Jump to a Berlin Boat Tour", "top": "Top", "pick_badge": "#1 PICK",
        "free": "Free Cancellation", "jump": "Jump to Cruise Review",
        "breadcrumb_name": "The 10 Best Berlin Boat Tours (2026)",
    },
    "de": {
        "title": "Spreefahrt Berlin 2026: Die 10 besten Bootstouren im Vergleich",
        "h1": "Spreefahrt Berlin: Die 10 besten Bootstouren", "kicker": "Spreefahrten-Vergleich 2026",
        "desc": "Spreefahrt Berlin: 10 Bootstouren auf Spree, Kanal und Seen ab €18 im Vergleich, mit Anleger, Preis pro Stunde, Guide und kostenloser Stornierung.",
        "home": "Startseite", "home_href": "/de", "updated": "Zuletzt aktualisiert", "author_role": "Inhaber &amp; Chef-Cruise-Detektiv",
        "author_sub": "Live-Angebote nebeneinander verglichen • Unabhängiger Vergleich",
        "lead": "Fast jede 1-Stunden-Spreefahrt fährt dieselbe Runde an Reichstag und Museumsinsel vorbei, für €17 bis €25, also entscheiden Boot, Guide und Anleger: hier sind die 10, die sich lohnen, von der <strong>Seenfahrt für €6 pro Stunde</strong> bis zur <strong>Dinnerfahrt mit 4 Gängen</strong>.",
        "qp_title": "Schnellauswahl",
        "qp": [("Testsieger", 1, "Glasdach-Boot mit Live-Guide, €18"),
               ("Beste lange Tour", 2, "Spree + Landwehrkanal in 3,25 Stunden"),
               ("Bester Abend", 5, "Yacht mit einem Glas Crémant"),
               ("Bester Preis", 9, "3,5 Stunden zum Müggelsee, €6,30 pro Stunde")],
        "filters": "Filter:", "all": "Alle",
        "flt": [("hour", "⏱️ 1-Stunden-Runde"), ("lakes", "🌳 Seen &amp; Schlösser"), ("evening", "🌙 Abend &amp; Dinner"),
                ("cancel", "✅ Kostenlos stornierbar"), ("under20", "💶 Unter €20")],
        "per_adult": "pro Erwachsenem", "check": "Verfügbarkeit prüfen →", "via": "Sicher gebucht über {}",
        "free_cancel": "✓ Kostenlos stornierbar bis 24 Std. vorher", "nonref": "Nicht erstattbares Ticket", "mobile": "✓ Sofort Handy-Ticket",
        "read": "Rezension lesen ↓", "pick": "✓ Buchen", "skip": "✕ Lieber nicht",
        "rate_head": "Durchschnitt von {} Buchungsseiten, gewichtet nach Anzahl der Bewertungen", "rate_head1": "Bewertung auf der Buchungsseite",
        "reviews": "Bewertungen", "sites": "Seiten",
        "breakdown": "Detailvergleich: 10 Bootstouren in Berlin",
        "breakdown_sub": "Route, Anleger, Preis pro Stunde und was inklusive ist, Boot für Boot",
        "expand": "Alle aufklappen", "collapse": "Alle zuklappen", "pros": "Vorteile:", "cons": "Nachteile:",
        "photos": "📸 Fotos", "swipe": "{} Fotos wischen →", "summary": "Zusammenfassung &amp; Rezension", "overview": "Überblick",
        "qf": "Kurzinfos", "photo_cap": "Foto: {} über {}", "cta_from": "Verfügbarkeit prüfen: €{} →",
        "toc": "Inhaltsverzeichnis", "toc_deck": "Top 10 Bootstouren Berlin", "toc_breakdown": "Detailvergleich (10 Bootstouren)",
        "sticky_all": "Alle 10 Bootstouren", "sheet": "Direkt zur Bootstour springen", "top": "Nach oben", "pick_badge": "#1 TIPP",
        "free": "Kostenlos stornierbar", "jump": "Zur Rezension springen",
        "breadcrumb_name": "Spreefahrt Berlin: Die 10 besten Bootstouren (2026)",
    },
}


def money(v, lang):
    # card prices use a dot in every language (site convention; port.py sync rewrites cards from EN)
    return f"{int(v)}" if float(v).is_integer() else f"{v:.2f}"


def num(n, lang):
    s = f"{n:,}"
    return s.replace(",", ".") if lang == "de" else s


def short_count(n, lang):
    if n >= 1000:
        k = n // 100 / 10
        return (f"{k:.1f}".rstrip("0").rstrip(".")) + "k+"
    return num(n, lang)


def weighted(ratings):
    tot = sum(c for _, _, c in ratings)
    return sum(s * c for _, s, c in ratings) / tot, tot


def score(v, lang):
    # site convention: rating scores use a dot in every language (cards.py drift compares them)
    return f"{v:.1f}"


def esc(s):
    return html.escape(s, quote=True)


def book_url(p, lang):
    kind, path = p["book"]
    return gyg(path, p["key"], lang) if kind == "gyg" else tiq(path, p["key"], lang)


def book_site(p):
    return "GetYourGuide" if p["book"][0] == "gyg" else "Tiqets"


AFF = 'rel="nofollow sponsored noopener" target="_blank"'


def stars_svg():
    one = ('<svg aria-hidden="true" viewbox="0 0 24 24"><path d="M11.9999 18.26L4.94691 22.208L6.52191 14.28L0.586914 '
           '8.792L8.61391 7.84L11.9999 0.5L15.3859 7.84L23.4129 8.792L17.4779 14.28L19.0529 22.208L11.9999 18.26Z"></path></svg>')
    return one * 5


def maps(q):
    from urllib.parse import quote_plus
    return "https://www.google.com/maps/search/?api=1&amp;query=" + quote_plus(q)


def pill(emoji, label, lead, note, lang):
    n = f'<span class="bpa-lang-note">{note[lang]}</span>' if note else ""
    return (f'<details class="bpa-lang"><summary class="bpa-sp">{emoji} <span class="bpa-lang-label">{label[lang]}</span>'
            f'<span class="bpa-lang-chev" aria-hidden="true">▾</span></summary><div class="bpa-lang-pop">{lead[lang]}{n}</div></details>')


def rating_block(p, lang, icons):
    t = T[lang]
    r, tot = weighted(p["ratings"])
    nsites = len(p["ratings"])
    meta = (f"{short_count(tot, lang)} {t['reviews']} · {nsites} {t['sites']}" if nsites > 1
            else f"{num(tot, lang)} {t['reviews']}")
    head = t["rate_head"].format(nsites) if nsites > 1 else t["rate_head1"]
    badges = []
    for site, s, c in sorted(p["ratings"], key=lambda x: -x[2]):
        inner = (f'<img alt="{site}" class="bpa-rev-icon" loading="lazy" src="{icons[site]}"/><span class="bpa-rev-site">{site}</span>'
                 f'<span class="bpa-rev-score">{score(s, lang)}</span><span class="bpa-rev-stars">{stars_svg()}</span>'
                 f'<span class="bpa-rev-count">({short_count(c, lang)})</span>')
        if site == book_site(p):
            badges.append(f'<a class="bpa-rev-badge is-link" href="{esc(book_url(p, lang))}" {AFF}>{inner}'
                          f'<span class="bpa-rev-go" aria-hidden="true">→</span></a>')
        else:
            badges.append(f'<span class="bpa-rev-badge is-static">{inner}</span>')
    return (f'<div class="bpa-reviews-line"><div class="bpa-summary-reviews bpa-rate"><details class="bpa-lang bpa-rate-more">'
            f'<summary class="bpa-rate-sum"><span class="bpa-stars" style="--r:{r:.2f}" aria-hidden="true"></span>'
            f'<b class="bpa-rate-score">{score(r, lang)}</b><span class="bpa-rate-meta">{meta}</span>'
            f'<span class="bpa-lang-chev" aria-hidden="true">▾</span></summary><div class="bpa-lang-pop"><strong>{head}</strong>'
            f'<span class="bpa-rate-list">{"".join(badges)}</span></div></details></div></div>')


def photo(p, i):
    return f"{ASSET}/berlin-boat-tour-{p['key']}-{i:02d}.avif"


def card(n, p, lang, icons):
    t = T[lang]
    url = esc(book_url(p, lang))
    imgs = []
    for i in range(1, p["photos"] + 1):
        lazy = 'loading="eager" fetchpriority="high"' if (n == 1 and i == 1) else 'loading="lazy"'
        imgs.append(f'<img alt="{esc(p["title"][lang])}, photo {i}" height="534" width="800" {lazy} src="{photo(p, i)}"/>')
    gold = " bpa-gold" if p.get("gold") else ""
    was = ""
    if p["was"]:
        pct = round((1 - p["price"] / p["was"]) * 100)
        was = f'<div class="bpa-was"><s>€{money(p["was"], lang)}</s> <span>−{pct}%</span></div>'
    trust = (f'<span>{t["free_cancel"]}</span>' if p["cancel"]
             else f'<span class="bt-nonref">{t["nonref"]}</span>')
    return f'''<div class="bpa-card" data-cat="{p['cats']}" id="card-{n}">
<div class="bpa-main">
<div class="bpa-media">
<button aria-label="Previous photo" class="bpa-arrow prev" onclick="bpaSlide(this,-1)" type="button">‹</button><button aria-label="Next photo" class="bpa-arrow next" onclick="bpaSlide(this,1)" type="button">›</button><span class="bpa-pill">1 / {p['photos']}</span><span class="bpa-rank-tag{gold}">{p['rank'][lang]}</span>
<div class="bpa-slider" onscroll="bpaCount(this)">{''.join(imgs)}</div>
</div>
<div class="bpa-info">
<div class="bpa-kicker">{p['operator']} • ⏱️ {p['dur'][lang]} • <a class="bpa-kicker-map-link" href="{maps(p['pier'])}" onclick="event.stopPropagation()" rel="noopener noreferrer" target="_blank">📍 {p['pier_short'][lang]}</a></div>
<a class="bpa-title" href="{url}" {AFF}>{p['title'][lang]}</a>
{rating_block(p, lang, icons)}
<div class="bpa-specs-row">
{''.join(pill(e, l, ld, nt, lang) for e, l, ld, nt in p['pills'])}
</div>
<div class="bpa-best-for bpa-pickskip"><span class="bpa-pick">{t['pick']}</span> {p['pick'][lang]} <span class="bpa-skip">{t['skip']}</span> {p['skip'][lang]}</div>
</div>
<div class="bpa-cta-cell">
<div>
{was}<div class="bpa-price">€{money(p['price'], lang)}</div>
<div class="bpa-psub">{t['per_adult']}</div>
</div>
<a class="bpa-btn" href="{url}" {AFF}>{t['check']}</a>
<div class="bpa-via">{t['via'].format(book_site(p))}</div>
<div class="bpa-trust2">{trust}<span>{t['mobile']}</span></div>
<a class="bpa-sublink" href="#bt-{p['key']}">{t['read']}</a>
</div>
</div>
</div>'''


def details(n, p, lang):
    t = T[lang]
    url = esc(book_url(p, lang))
    r, tot = weighted(p["ratings"])
    gold = " bpa-gold" if p.get("gold") else ""
    pros = "".join(f"<li>{x}</li>" for x in p["pros"][lang])
    cons = "".join(f"<li>{x}</li>" for x in p["cons"][lang])
    src = PHOTO_SRC.get(p["key"], ["GetYourGuide"] * p["photos"])
    slides = "".join(
        f'<div class="ltt-strip-slide"><img alt="{esc(p["operator"])}: {esc(p["title"][lang])}, photo {i}" loading="lazy" src="{photo(p, i)}"/>'
        f'<div class="ltt-strip-cap"><span class="ltt-strip-num">{i} / {p["photos"]}</span> <span>{t["photo_cap"].format(esc(p["operator"]), src[i - 1])}</span></div></div>'
        for i in range(1, p["photos"] + 1))
    review = "".join(f"<p>{x}</p>" for x in p["review"][lang])
    facts = "".join(f'<div class="qf1-row"><div class="qf1-label">{a}</div><div class="qf1-val">{b}</div></div>' for a, b in p["facts"][lang])
    meta = f"{num(tot, lang)} {t['reviews']}"
    return f'''<details class="bpa-details-card" data-cat="{p['cats']}" id="bt-{p['key']}" open="">
<summary class="bpa-details-summary">
<div class="bpa-details-summary-content">
<div class="bpa-details-top-row">
<span class="bpa-rank-tag{gold}">{p['rank'][lang]}</span>
<div class="bpa-kicker">{p['operator']} • ⏱️ {p['dur'][lang]} • <a class="bpa-kicker-map-link" href="{maps(p['pier'])}" onclick="event.stopPropagation()" rel="noopener noreferrer" target="_blank">{p['pier_short'][lang]}</a></div>
</div>
<h3 class="bpa-details-title">{p['title'][lang]}</h3>
<div class="bpa-reviews-line"><span class="bpa-stars" style="--r:{r:.2f}" aria-hidden="true"></span> <b class="bpa-rate-score">{score(r, lang)}</b> <span class="bpa-rate-meta">({meta})</span></div>
</div>
<div class="bpa-details-right">
<span class="bpa-details-price">€{money(p['price'], lang)}</span>
<div class="bpa-details-toggle">
<span class="bpa-details-state-text"></span>
<span class="bpa-details-chevron">▾</span>
</div>
</div>
</summary>
<div class="bpa-details-body">
<div class="pro-con-box-wrapper"><div class="w-layout-grid grid-15"><div class="pro-con-box-pro-cell" data-wf-pbl="layout-grid-1x2-vertical"><div class="pro-con-box-pro-cell-rich-text-block w-richtext"><h3><strong>{t['pros']}</strong></h3><ul>{pros}</ul></div></div><div class="pro-con-box-con-cell" data-wf-pbl="layout-grid-1x2-vertical"><div class="pro-con-box-con-cell-rich-text-block w-richtext"><h3><strong>{t['cons']}</strong></h3><ul>{cons}</ul></div></div></div></div><details class="ltt-bento-group" open=""><summary class="ltt-bento-group-head"><span class="ltt-bento-group-title">{t['photos']}</span><span class="ltt-bento-right"><span class="ltt-mini-pill">{t['swipe'].format(p['photos'])}</span><span class="ltt-bento-chev">▾</span></span></summary><div class="ltt-bento-group-body" style="padding: 12px 14px !important;"><div class="ltt-filmstrip-wrap"><button aria-label="Previous photo" class="ltt-film-btn ltt-film-prev is-disabled" onclick="window.lttFilmSlide(this, -1)" type="button">‹</button><button aria-label="Next photo" class="ltt-film-btn ltt-film-next" onclick="window.lttFilmSlide(this, 1)" type="button">›</button><div class="ltt-filmstrip" onscroll="window.lttFilmSync(this)">{slides}</div></div></div></details><details class="ltt-bento-group" open="">
<summary class="ltt-bento-group-head">
<span class="ltt-bento-group-title">{t['summary']}</span>
<span class="ltt-bento-right">
<span class="ltt-mini-pill">{t['overview']}</span>
<span class="ltt-bento-chev">▾</span>
</span>
</summary>
<div class="ltt-bento-group-body">
<div class="w-richtext">{review}</div>
</div>
</details>
<div class="qf1-wrap"><div class="qf1-title-row"><h4 class="qf1-title">{t['qf']}</h4><span class="qf1-badge">{p['pier_short'][lang]}</span></div><div class="qf1-table">{facts}</div></div>
<a class="bpa-btn" href="{url}" {AFF} style="margin-top:14px;display:block;text-align:center">{t['cta_from'].format(money(p['price'], lang))}</a></div>
</details>'''


PHOTO_SRC = {
    "dinner-cruise": ["Tiqets"] * 6,
    "east-side-gallery": ["Tiqets"] * 6,
    "seven-lakes-wannsee": ["Tiqets"] * 3 + ["GetYourGuide"] * 3,
    "muggelsee": ["GetYourGuide"] * 5 + ["Tiqets"],
}


def per_hour(p):
    return p["price"] / p["hours"]


# ---------------------------------------------------------------------------
# Buyer's guide sections
# ---------------------------------------------------------------------------
def logistics_table(lang):
    hd = {"en": ["#", "Cruise", "Time", "Price", "€ per hour", "Pier (nearest station)", "Commentary", "Free cancel"],
          "de": ["#", "Fahrt", "Dauer", "Preis", "€ pro Stunde", "Anleger (nächster Bahnhof)", "Erklärungen", "Gratis storno"]}[lang]
    comm = {
        "hadynski-glass-roof": {"en": "Live DE/EN", "de": "Live DE/EN"},
        "bridges-landwehr-canal": {"en": "DE + audio 11 lang.", "de": "DE + Audio 11 Spr."},
        "stern-und-kreis-1-hour": {"en": "Audio 12 lang.", "de": "Audio 12 Spr."},
        "hemingway": {"en": "DE/EN + music", "de": "DE/EN + Musik"},
        "evening-yacht-aperitif": {"en": "None, music", "de": "Keine, Musik"},
        "seven-lakes-wannsee": {"en": "Not stated", "de": "Nicht angegeben"},
        "east-side-gallery": {"en": "DE/EN + audio 6", "de": "DE/EN + Audio 6"},
        "potsdam-world-heritage": {"en": "DE/EN", "de": "DE/EN"},
        "muggelsee": {"en": "Not stated", "de": "Nicht angegeben"},
        "dinner-cruise": {"en": "Audio EN/DE", "de": "Audio EN/DE"},
    }
    station = {
        "hadynski-glass-roof": "S Hackescher Markt", "bridges-landwehr-canal": "S+U Jannowitzbrücke",
        "stern-und-kreis-1-hour": "S+U Friedrichstraße", "hemingway": "U Bundestag",
        "evening-yacht-aperitif": "U Bundestag", "seven-lakes-wannsee": "S Wannsee",
        "east-side-gallery": "S Hackescher Markt", "potsdam-world-heritage": "S Wannsee",
        "muggelsee": "S Treptower Park", "dinner-cruise": "U Richard-Wagner-Platz",
    }
    yes, no = ("Yes", "No") if lang == "en" else ("Ja", "Nein")
    rows = []
    for n, p in enumerate(PRODUCTS, 1):
        rows.append(f'<tr><td>{n}</td><td><a href="#card-{n}">{p["short"][lang]}</a></td><td>{p["dur"][lang]}</td>'
                    f'<td>€{money(p["price"], lang)}</td><td>€{money(round(per_hour(p), 2), lang)}</td>'
                    f'<td>{p["pier_short"][lang].split(" (")[0]} ({station[p["key"]]})</td><td>{comm[p["key"]][lang]}</td>'
                    f'<td>{yes if p["cancel"] else no}</td></tr>')
    th = "".join(f"<th>{h}</th>" for h in hd)
    return f'<div class="bt-table-wrap"><table class="bt-logistics"><thead><tr>{th}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


FAQ = {
    "en": [
        ("How much does a boat tour in Berlin cost?",
         "A 1-hour Spree cruise through the centre costs €17 to €25 per adult. Longer trips cost €19 to €33 for 1.75 to 3.5 hours, an evening yacht with a glass of Crémant is €39, and a dinner cruise starts at €79.90."),
        ("Which Berlin boat tour has a live guide in English?",
         "Reederei Hadynski's 1-hour glass-roof cruise has a live guide in German and English on every departure, and it is the best-rated 1-hour cruise at 4.7 from 7,465 reviews. Most other boats use recorded commentary or an audio guide."),
        ("Where do Berlin boat tours leave from?",
         "The 1-hour cruises leave from piers around Museum Island and Friedrichstraße: Hackescher Markt, the Nikolaiviertel, Reichstagufer and the FLAGSHIP.BERLIN pier below the Reichstag. Lake cruises start at Wannsee (S-Bahn), the Müggelsee trip at Treptower Park, and the dinner cruise in Charlottenburg."),
        ("Do Berlin boat tours run in winter?",
         "Yes. Heated boats like Reederei Hadynski's glass-roof cruise sail daily from March to December, and November and December departures often serve mulled wine at the bar. For the lake trips, check the booking calendar for your date."),
        ("Is a Berlin boat tour worth it?",
         "Yes, if you pick the right length. One hour on the Spree shows Museum Island, the Reichstag and the government quarter without walking, for about €18. With an afternoon free, the 3.25-hour bridges tour adds Kreuzberg and the Landwehr Canal for about €10 per hour."),
        ("Can I cancel a Berlin boat tour for free?",
         "Six of the 10 cruises here can be cancelled for free up to 24 hours before: the Hadynski, Stern und Kreis 1-hour, Hemingway, evening yacht, Potsdam and Müggelsee tickets. The bridges tour, Seven Lakes, East Side and dinner cruise tickets are non-refundable."),
    ],
    "de": [
        ("Was kostet eine Bootstour in Berlin?",
         "Eine 1-Stunden-Spreefahrt durch die Mitte kostet €17 bis €25 pro Erwachsenem. Längere Fahrten kosten €19 bis €33 für 1,75 bis 3,5 Stunden, die Abend-Yacht mit einem Glas Crémant €39, und eine Dinnerfahrt beginnt bei €79,90."),
        ("Welche Spreefahrt hat einen Live-Guide?",
         "Die 1-Stunden-Fahrt der Reederei Hadynski im Glasdach-Boot hat bei jeder Abfahrt einen Live-Guide auf Deutsch und Englisch und ist mit 4,7 aus 7.465 Bewertungen die bestbewertete 1-Stunden-Fahrt. Die meisten anderen Boote nutzen Aufnahmen oder einen Audioguide."),
        ("Wo starten die Bootstouren in Berlin?",
         "Die 1-Stunden-Fahrten starten an Anlegern rund um Museumsinsel und Friedrichstraße: Hackescher Markt, Nikolaiviertel, Reichstagufer und der FLAGSHIP.BERLIN-Anleger unterhalb des Reichstags. Die Seenfahrten starten am Wannsee (S-Bahn), die Müggelsee-Fahrt am Treptower Park und die Dinnerfahrt in Charlottenburg."),
        ("Fahren die Schiffe in Berlin auch im Winter?",
         "Ja. Beheizte Boote wie das Glasdach-Boot der Reederei Hadynski fahren von März bis Dezember täglich, und im November und Dezember gibt es an Bord oft Glühwein. Für die Seenfahrten den Buchungskalender für dein Datum prüfen."),
        ("Lohnt sich eine Spreefahrt in Berlin?",
         "Ja, wenn die Länge passt. Eine Stunde auf der Spree zeigt Museumsinsel, Reichstag und Regierungsviertel ohne Laufen, für rund €18. Mit einem freien Nachmittag zeigt die 3,25-stündige Brückenfahrt zusätzlich Kreuzberg und den Landwehrkanal, für rund €10 pro Stunde."),
        ("Kann ich eine Bootstour in Berlin kostenlos stornieren?",
         "Sechs der 10 Fahrten hier sind bis 24 Stunden vorher kostenlos stornierbar: Hadynski, die 1-Stunden-Fahrt von Stern und Kreis, Hemingway, Abend-Yacht, Potsdam und Müggelsee. Die Tickets für Brückenfahrt, 7-Seen-Rundfahrt, East-Side-Tour und Dinnerfahrt sind nicht erstattbar."),
    ],
}


def sections(lang):
    if lang == "en":
        worth = ('<section data-toc="Is It Worth It?" id="bt-worth-it"><div class="w-richtext"><h2>Is a Berlin Boat Tour Worth It?</h2>'
                 '<p>A Spree cruise covers Museum Island, the Berlin Cathedral, the Reichstag, the Chancellery and the Hauptbahnhof, sights that take half a day on foot, in one hour and for about <strong>€18</strong>. That is the best-value hour in the city for a first visit, especially in the cold months on a heated boat.</p>'
                 '<p>The catch: <strong>almost every 1-hour cruise runs the same loop</strong>: it turns at the Mühlendamm lock in the east and the Haus der Kulturen der Welt in the west. So don\'t choose by route. Choose by <strong>guide</strong> (live on #1, 12 audio languages on #3), by <strong>boat</strong> (the 1908 Hemingway at #4) and by <strong>pier</strong>. If you want more than the government quarter, the longer trips are cheaper per hour: <strong>€10 an hour</strong> on the bridges tour and <strong>€6.30 an hour</strong> to Müggelsee.</p>'
                 '<p>Comparing cities? Here are the best <a href="/seine-river-cruises-paris">Seine river cruises in Paris</a>, <a href="/canal-cruises-amsterdam">Amsterdam canal cruises</a> and <a href="/thames-river-cruises-london">Thames cruises in London</a>.</p></div></section>')
        logi = ('<section data-toc="Side by Side" id="bt-logistics"><div class="w-richtext"><h2>All 10 Berlin Boat Tours Side by Side</h2>'
                '<p>Price per hour, the pier with its nearest station, the type of commentary and whether you can cancel for free: the details that decide the booking, in one table.</p></div>'
                + logistics_table(lang) + '</section>')
        best = ('<section data-toc="Best Time to Go" id="bt-best-time"><div class="w-richtext"><h2>Best Time for a Spree Cruise</h2>'
                '<p><strong>Late afternoon into dusk.</strong> The government quarter and Museum Island look best in low light, and from November to February sunset is around 16:00, so a 15:30 departure catches it. In summer, the evening yacht (#5) and the dinner cruise (#10) are timed for the long light.</p>'
                '<p><strong>In winter, pick a heated boat with a roof.</strong> Reederei Hadynski\'s glass-roof boats sail daily until the end of December. The lake cruises from Wannsee and Treptow are at their best from spring to autumn, when the beaches, gardens and villas are green; check the booking calendar for your date.</p></div></section>')
        meth = ('<section data-toc="How I Compared" id="bt-methodology"><div class="w-richtext"><h2>How I Compared These 10 Berlin Boat Tours</h2>'
                '<p>On 15 November 2026 I compared every Berlin cruise bookable on Tiqets and GetYourGuide, side by side on the details that decide a booking: route and turning points, duration, price per hour, pier and nearest station, live guide or audio guide, what is included and the cancellation terms. Prices and ratings are taken from the live listings on that date; ratings are averaged across booking sites and weighted by number of reviews.</p>'
                '<p>Where the same boat is sold on both sites I list it once and link the better offer, and I left out near-duplicates of the 1-hour city loop with fewer reviews rather than padding the list. Each of the 10 wins at something: best overall, longest route, most languages, quietest boat, evening, lakes, the East Side, Potsdam, value and dinner.</p></div></section>')
    else:
        worth = ('<section data-toc="Lohnt es sich?" id="bt-worth-it"><div class="w-richtext"><h2>Lohnt sich eine Spreefahrt in Berlin?</h2>'
                 '<p>Eine Spreefahrt zeigt Museumsinsel, Berliner Dom, Reichstag, Kanzleramt und Hauptbahnhof, für die du zu Fuß einen halben Tag brauchst, in einer Stunde und für rund <strong>€18</strong>. Für einen ersten Besuch ist das die beste Stunde in der Stadt, besonders in den kalten Monaten auf einem beheizten Boot.</p>'
                 '<p>Der Haken: <strong>fast jede 1-Stunden-Fahrt fährt dieselbe Runde</strong>: sie wendet im Osten an der Mühlendammschleuse und im Westen am Haus der Kulturen der Welt. Wähle also nicht nach Route, sondern nach <strong>Guide</strong> (live bei #1, 12 Audiosprachen bei #3), nach <strong>Boot</strong> (die Hemingway von 1908 bei #4) und nach <strong>Anleger</strong>. Wer mehr als das Regierungsviertel sehen will, fährt mit den längeren Touren pro Stunde günstiger: <strong>€10 pro Stunde</strong> bei der Brückenfahrt und <strong>€6,30 pro Stunde</strong> zum Müggelsee.</p>'
                 '<p>Städte im Vergleich? Hier sind die besten <a href="/de/besten-bootsfahrten-seine-paris">Bootsfahrten auf der Seine in Paris</a>, <a href="/de/besten-grachtenfahrten-amsterdam">Grachtenfahrten in Amsterdam</a> und <a href="/de/themse-kreuzfahrten-london">Themse-Fahrten in London</a>.</p></div></section>')
        logi = ('<section data-toc="Im Überblick" id="bt-logistics"><div class="w-richtext"><h2>Alle 10 Bootstouren in Berlin im Überblick</h2>'
                '<p>Preis pro Stunde, Anleger mit nächstem Bahnhof, Art der Erklärungen und ob du kostenlos stornieren kannst: die Details, die über die Buchung entscheiden, in einer Tabelle.</p></div>'
                + logistics_table(lang) + '</section>')
        best = ('<section data-toc="Beste Zeit" id="bt-best-time"><div class="w-richtext"><h2>Die beste Zeit für eine Spreefahrt</h2>'
                '<p><strong>Später Nachmittag bis Dämmerung.</strong> Regierungsviertel und Museumsinsel sehen im tiefen Licht am besten aus, und von November bis Februar ist der Sonnenuntergang gegen 16:00 Uhr, eine Abfahrt um 15:30 Uhr erwischt ihn also. Im Sommer sind die Abend-Yacht (#5) und die Dinnerfahrt (#10) auf das lange Licht abgestimmt.</p>'
                '<p><strong>Im Winter ein beheiztes Boot mit Dach wählen.</strong> Die Glasdach-Boote der Reederei Hadynski fahren bis Ende Dezember täglich. Die Seenfahrten ab Wannsee und Treptow sind von Frühling bis Herbst am schönsten, wenn Strände, Gärten und Villen im Grünen liegen; den Buchungskalender für dein Datum prüfen.</p></div></section>')
        meth = ('<section data-toc="So habe ich verglichen" id="bt-methodology"><div class="w-richtext"><h2>So habe ich diese 10 Bootstouren verglichen</h2>'
                '<p>Am 15. November 2026 habe ich jede Berliner Schiffstour, die auf Tiqets und GetYourGuide buchbar ist, nebeneinander verglichen, nach den Details, die über eine Buchung entscheiden: Route und Wendepunkte, Dauer, Preis pro Stunde, Anleger und nächster Bahnhof, Live-Guide oder Audioguide, was inklusive ist und die Stornobedingungen. Preise und Bewertungen stammen aus den Live-Angeboten an diesem Tag; Bewertungen sind über die Buchungsseiten gemittelt und nach Anzahl der Bewertungen gewichtet.</p>'
                '<p>Wird dasselbe Boot auf beiden Seiten verkauft, steht es nur einmal hier, verlinkt mit dem besseren Angebot, und fast gleiche 1-Stunden-Runden mit weniger Bewertungen habe ich weggelassen, statt die Liste aufzufüllen. Jede der 10 Fahrten gewinnt in etwas: Testsieger, längste Route, meiste Sprachen, leisestes Boot, Abend, Seen, East Side, Potsdam, Preis und Dinner.</p></div></section>')
    faq_h = {"en": ("FAQ", "Berlin Boat Tours: FAQ"), "de": ("FAQ", "Spreefahrt Berlin: Häufige Fragen")}[lang]
    faq = (f'<section data-toc="{faq_h[0]}" id="bt-faq"><div class="w-richtext"><h2>{faq_h[1]}</h2>'
           + "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in FAQ[lang]) + '</div></section>')
    return worth + "\n" + logi + "\n" + best + "\n" + faq + "\n" + meth


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
.bpa-rev-badge.is-link:hover,.bpa-rev-badge.is-link:hover *{color:inherit}
.bpa-trust2 .bt-nonref{color:#64748b !important}
.bpa-details-card .bpa-reviews-line{display:flex;align-items:center;gap:4px;font-size:12.5px}
</style>"""


def build(lang):
    src = TEMPLATE.read_text(encoding="utf-8")
    seine = SEINE.read_text(encoding="utf-8")
    t = T[lang]
    url = f"{SITE}/{SLUG[lang]}"
    icons = {}
    for site in ("GetYourGuide", "Tiqets"):
        m = re.search(r'<img alt="%s" class="bpa-rev-icon" loading="lazy" src="(data:[^"]+)"' % site, seine)
        icons[site] = m.group(1)
    lang_css = re.search(r'<style id="bpa-lang-css">.*?</style>', seine, re.S).group(0)
    lang_js = re.search(r'<script id="bpa-lang-js">.*?</script>', seine, re.S).group(0)
    card_css = "<style id=\"bt-card-css\">\n" + (ROOT / "scripts" / "articles" / "seine_card_extra.css").read_text(encoding="utf-8") + "\n</style>"

    h = src
    h = h.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    # --- head meta
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
           f'<link href="{SITE}/{SLUG["en"]}" hreflang="en" rel="alternate"/>\n'
           f'<link href="{SITE}/{SLUG["de"]}" hreflang="de" rel="alternate"/>\n'
           f'<link href="{SITE}/{SLUG["en"]}" hreflang="x-default" rel="alternate"/>\n')
    h = re.sub(r'<link href="[^"]*" rel="canonical"/>\n(?:<link href="[^"]*" hreflang="[^"]*" rel="alternate"/>\n)+', alt, h, count=1)
    h = h.replace('<link href="/dinner-cruises-paris.md" rel="alternate" type="text/markdown"/>\n', "")
    h = re.sub(r'<link as="image" fetchpriority="high" href="[^"]*" rel="preload"/>',
               f'<link as="image" fetchpriority="high" href="{photo(PRODUCTS[0], 1)}" rel="preload"/>', h, count=1)
    h = re.sub(r'<script id="private-cruises-schema-jsonld" type="application/ld\+json">.*?</script>',
               lambda m: f'<script id="berlin-boat-tours-schema-jsonld" type="application/ld+json">{jsonld(lang)}</script>'
               + "\n" + lang_css + "\n" + card_css + EXTRA_CSS, h, count=1, flags=re.S)

    # --- hero
    hero_start = h.index('<div class="ltt-hero-wrap">')
    deck_end = h.index('<div class="blog-section-2">')
    deck_css = re.search(r'<style id="ltt-dubai-safari-styles">.*?</style>', h, re.S).group(0)
    cats = {}
    for p in PRODUCTS:
        for c in p["cats"].split():
            cats[c] = cats.get(c, 0) + 1
    filt = [f'<button class="ltt-tab-btn active" data-cat="all" onclick="lttFilterItems(\'all\', this)" type="button">{t["all"]} ({len(PRODUCTS)})</button>']
    for c, label in t["flt"]:
        filt.append(f'<button class="ltt-tab-btn" data-cat="{c}" onclick="lttFilterItems(\'{c}\', this)" type="button">{label} ({cats.get(c, 0)})</button>')
    qp = "".join(f'<li><strong>{a}:</strong> <a href="#card-{n}">{PRODUCTS[n - 1]["short"][lang]}</a>, {d}</li>' for a, n, d in t["qp"])
    hero = f'''<div class="ltt-hero-wrap">
<div class="ltt-clean-card">
<div class="ltt-top-bar">
<nav aria-label="Breadcrumb" class="ltt-breadcrumbs">
<a href="{t['home_href']}">{t['home']}</a>
<span class="ltt-bc-sep">›</span>
<span class="ltt-bc-current">{t['breadcrumb_name']}</span>
</nav>
<span class="ltt-hero-kicker-badge">{t['kicker']}</span>
</div>
<h1 class="ltt-editorial-h1">{t['h1']} <span class="ltt-h1-muted">(2026)</span></h1>
<div class="ltt-trust-bar">
<div class="ltt-author-cluster">
<div class="ltt-author-avatar-wrap">
<img alt="Adam Dimitrov" class="ltt-author-avatar" src="https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp"/>
</div>
<div class="ltt-author-meta">
<div class="ltt-author-line">
            {'By' if lang == 'en' else 'Von'} <a href="{'/about' if lang == 'en' else '/de/uber-uns'}" target="_blank">Adam Dimitrov</a>, {t['author_role']}
          </div>
<div class="ltt-author-role">{t['author_sub']}</div>
</div>
</div>
<div class="ltt-trust-pills">
<span class="ltt-trust-pill paragraph-26"><strong>{t['updated']}</strong>: {CHECKED[lang]}</span>
</div>
</div>
<div class="ltt-lead-copy">
<p>{t['lead']}</p>
<div class="bt-qp"><p class="bt-qp-title">{t['qp_title']}</p><ul>{qp}</ul></div>
</div>
<div class="ltt-integrated-filter-bar">
<span class="ltt-filter-label">{t['filters']}</span>
<div class="ltt-integrated-pills">{chr(10).join(filt)}</div>
</div>
</div>
</div><div class="comparison-table"><div class="container-27">
{deck_css}
<div class="ltt-deck-container" id="berlin-boat-tour-deck">
<div class="bpa-deck-wrap" id="ltt-cards-deck">{chr(10).join(card(n, p, lang, icons) for n, p in enumerate(PRODUCTS, 1))}
</div></div></div></div>'''
    h = h[:hero_start] + hero + h[deck_end:]

    # --- breakdown + sections
    bstart = h.index('<div class="bpa-breakdown-top-bar" id="breakdown-header">')
    first_det = h.index('<details class="bpa-details-card"', bstart)
    head = h[bstart:first_det]
    head = re.sub(r'<h2 class="bpa-breakdown-heading" id="[^"]*">.*?</h2>',
                  f'<h2 class="bpa-breakdown-heading" id="berlin-boat-tours-breakdown">{t["breakdown"]}</h2>', head, flags=re.S)
    head = re.sub(r'<p class="bpa-breakdown-sub">.*?</p>', f'<p class="bpa-breakdown-sub">{t["breakdown_sub"]}</p>', head, flags=re.S)
    head = head.replace(">Expand All<", f">{t['expand']}<").replace(">Collapse All<", f">{t['collapse']}<")
    sec_start = h.index("<section", first_det)
    between = h[first_det:sec_start]
    last_det_end = between.rindex("</details>") + len("</details>")
    tail_between = between[last_det_end:]
    sec_end = h.rindex("</section>") + len("</section>")
    body = (head + "\n".join(details(n, p, lang) for n, p in enumerate(PRODUCTS, 1)) + tail_between + sections(lang))
    h = h[:bstart] + body + h[sec_end:]
    h = h.replace('<div class="title-small-3">Table of Contents</div>', f'<div class="title-small-3">{t["toc"]}</div>')

    # --- page config + sticky bar
    cfg = {"deckId": "berlin-boat-tour-deck", "tocDeckLabel": t["toc_deck"], "tocBreakdownLabel": t["toc_breakdown"],
           "shortTitles": [p["short"][lang] for p in PRODUCTS]}
    h = re.sub(r"LTT_PAGE_CONFIG = \{.*?\};", lambda m: "LTT_PAGE_CONFIG = " + json.dumps(cfg, ensure_ascii=False) + ";", h, count=1, flags=re.S)
    p1 = PRODUCTS[0]
    h = re.sub(r'<span>All 6 Private Cruises</span>', f'<span>{t["sticky_all"]}</span>', h)
    h = re.sub(r'(<span class="hybrid-active-badge" id="sticky-rank">)[^<]*', r"\g<1>" + t["pick_badge"], h)
    h = re.sub(r'(<span class="hybrid-active-title" id="sticky-name">)[^<]*', lambda m: m.group(1) + p1["short"][lang], h)
    h = re.sub(r'(<span class="hybrid-active-price" id="sticky-price">)[^<]*', lambda m: m.group(1) + "€" + money(p1["price"], lang), h)
    h = re.sub(r'(<span class="hybrid-active-trust">)[^<]*', lambda m: m.group(1) + t["free"], h)
    h = re.sub(r'<a class="hybrid-cta-btn" href="[^"]*"', f'<a class="hybrid-cta-btn" href="{esc(book_url(p1, lang))}"', h, count=1)
    h = re.sub(r'(<a class="hybrid-cta-btn"[^>]*>)\s*Check Availability →\s*</a>', lambda m: m.group(1) + "\n      " + t["check"] + "\n    </a>", h)
    h = h.replace('aria-label="Jump to Paris Private Cruise"', f'aria-label="{t["sheet"]}"')
    h = re.sub(r'<h3 class="hybrid-sheet-title">[^<]*</h3>', f'<h3 class="hybrid-sheet-title">{t["sheet"]}</h3>', h)
    h = h.replace('aria-label="Jump to Cruise Review"', f'aria-label="{t["jump"]}"')
    if lang != "en":
        h = h.replace("<span>Top</span>", f"<span>{t['top']}</span>")
    h = h.replace("</body>", lang_js + "\n</body>", 1)
    return h


def jsonld(lang):
    t = T[lang]
    url = f"{SITE}/{SLUG[lang]}"
    items = []
    for n, p in enumerate(PRODUCTS, 1):
        items.append({"@type": "ListItem", "position": n, "item": {
            "@type": "TouristTrip", "name": p["title"][lang],
            "description": (p["pick"][lang][0].upper() + p["pick"][lang][1:]).rstrip("."),
            "image": [f"{SITE}{photo(p, i)}" for i in range(1, min(p["photos"], 3) + 1)],
            "provider": {"@type": "Organization", "name": p["operator"]},
            "offers": {"@type": "Offer", "price": f"{p['price']:.2f}", "priceCurrency": "EUR", "url": book_url(p, lang)}}})
    graph = [
        {"@type": "Article", "@id": f"{url}#article", "headline": t["breadcrumb_name"], "description": t["desc"],
         "image": [f"{SITE}{photo(p, 1)}" for p in PRODUCTS[:6]],
         "datePublished": DATE_ISO, "dateModified": DATE_ISO, "inLanguage": lang,
         "mainEntityOfPage": {"@type": "WebPage", "@id": url},
         "author": {"@type": "Person", "name": "Adam Dimitrov", "jobTitle": "Owner & Head Cruise Detective", "url": f"{SITE}/about"},
         "publisher": {"@type": "Organization", "name": "The Cruise Detective", "url": SITE,
                       "logo": {"@type": "ImageObject", "url": "https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/6570a89c8c97ba4e084ac5d5_webclip-cruise-detective.png"}},
         "mainEntity": {"@id": f"{url}#list"}},
        {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": t["home"], "item": f"{SITE}{'/' if lang == 'en' else '/de'}"},
            {"@type": "ListItem", "position": 2, "name": t["breadcrumb_name"], "item": url}]},
        {"@type": "ItemList", "@id": f"{url}#list", "name": t["breadcrumb_name"], "numberOfItems": len(PRODUCTS), "itemListElement": items},
        {"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ[lang]]},
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def main():
    for lang in ("en", "de"):
        out = ROOT / SLUG[lang] / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build(lang), encoding="utf-8")
        print("wrote", out.relative_to(ROOT))


if __name__ == "__main__":
    main()
