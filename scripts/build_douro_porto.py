#!/usr/bin/env python3
"""Build /douro-river-cruises-porto (EN) from the private-cruises-paris article template.

The card styles, pill dropdowns (details.bpa-lang) and the rating popover come from the
EN Seine page, so the cards carry the same features (Pick/Skip, per-site ratings, pills
that open a dropdown). Facts are from the live Tiqets / GetYourGuide listings checked on
CHECKED below. Translations (pt, es) are made from the built EN page with
scripts/i18n/port.py page (translation memory), not here.

    python3 scripts/build_douro_porto.py
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SLUG = "douro-river-cruises-porto"
SITE = "https://www.thecruisedetective.com"
URL = f"{SITE}/{SLUG}"
CHECKED = "15 November 2026"
ISO = "2026-11-15T20:00:00+01:00"
GYG = "https://www.getyourguide.com"
TQ = "https://www.tiqets.com/en/porto-attractions-c76573"
IMG = f"/assets/{SLUG}/douro-river-cruise-porto-"


def gyg(path, key):
    return f"{GYG}{path}?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-{SLUG}-{key}&mkt_cmp=true"


def tiq(path, key):
    return f"{TQ}/{path}/?partner=thecruisedetective.com-176436&tq_campaign=douro-porto-{key}"


E = html.escape

# ---------------------------------------------------------------------------- data
# rating: (site, score, count, href or None). Weighted rating = sum(score*count)/sum(count).
CRUISES = [
    dict(
        key="atalaia-gold-yacht", anchor="dp-atalaia-gold", photos=5,
        rank=("bpa-gold", "🏆 #1 Best Overall"), short="Atalaia Gold: Yacht, Wine & Snacks",
        cats="wine", operator="Atalaia Gold", dur="2 Hours", hours=2,
        pier="Marina do Freixo", maps="Marina do Freixo, Porto",
        title="Luxury 7 Bridges Yacht Cruise with Wine & Snacks",
        href=gyg("/porto-l151/porto-luxury-6-bridges-yacht-cruise-with-wine-snacks-t932759/", "atalaia-gold"),
        ratings=[("GetYourGuide", 4.94, 2045, "self")],
        price=55, was=None, psub="per adult", kids=None,
        trust=["✓ Free cancellation up to 24 hours before", "✓ Reserve now, pay later"],
        alts=["Atalaia Gold yacht under the Dom Luís I bridge at sunset", "Guests with a tasting board on the yacht deck",
              "Yacht deck table facing the Dom Luís I bridge", "Regional tasting board of cured meats and cheese",
              "Covered lounge of the Atalaia Gold yacht"],
        pills=[
            ("🍷", "Wine & tasting board", "Included:", "local wine (green or rosé) and a regional tasting board of cured meats and cheese.", "Blankets on board for cool evenings. Vegetarian or gluten-free boards on request, if you ask in advance."),
            ("🌊", "Bridges + river mouth", "A 2-hour loop:", "under all six bridges, past Ribeira and the Gaia wine cellars, then out to Foz where the Douro meets the Atlantic.", "It also passes the 7th bridge, still under construction, hence the name."),
            ("🗣️", "Live crew PT/EN", "Commentary in Portuguese and English", "from the crew on board.", "Covered yacht with a toilet, so it still sails in light rain."),
            ("📍", "Marina do Freixo", "Meet at the marina gate", "by Restaurante Marina do Freixo, about 4 km upriver from Ribeira. The crew wear Atalaia Gold ID.", "Take a taxi, Uber or bus: it is a long walk from the old town."),
        ],
        pick="for the best all-round 2 hours: wine and food included, the whole river out to the ocean.",
        skip="if you want to board in Ribeira: the marina is 4 km east.",
        pros=[("4.9/5 from 2,045 reviews", "the best-rated Porto cruise with more than 1,000 reviews."),
              ("Wine and food included", "local wine and a tasting board, so €55 covers your aperitivo."),
              ("The longest city route", "all six bridges plus the river mouth at Foz.")],
        cons=[("Marina do Freixo", "4 km east of Ribeira, so you need transport."),
              ("Three times the price of a rabelo", "€55 against €18 for the 50-minute boats.")],
        summary=[
            "This is the cruise to book if you only do one. It has the best score of any Porto boat with more than 1,000 reviews, and the €55 ticket includes local wine and a regional tasting board, so you are not paying extra for drinks on deck.",
            "The route is the full city: from Marina do Freixo under all six bridges, past the Ribeira waterfront and the Gaia Port cellars, then out to Foz and the Atlantic. That is twice as much river as the 50-minute six-bridges boats.",
            "Tip: book the last departure of the day in summer for the sunset at the river mouth, and bring a jacket. It gets windy at Foz even in July.",
        ],
        facts=[("Duration", "2 hours"), ("Meeting point", "Restaurante Marina do Freixo, N108, 4300-316 Porto"),
               ("Included", "Local wine, regional tasting board, blankets, crew, insurance, fuel"),
               ("Commentary", "Portuguese, English"), ("On board", "Covered yacht with a toilet"),
               ("Cancellation", "Free up to 24 hours before")],
    ),
    dict(
        key="water-line-wine-cruise", anchor="dp-water-line", photos=5,
        rank=("bpa-silver", "🥂 #2 Best Wine Tasting"), short="Water Line: 3 Wines, Small Group",
        cats="wine sunset small", operator="Water Line Douro", dur="2 Hours", hours=2,
        pier="Douro Marina, Gaia", maps="Douro Marina, Rua da Praia 430, Vila Nova de Gaia",
        title="6 Bridges Small-Group Cruise with 3 Wines",
        href=gyg("/porto-l151/douro-perspectives-scenic-porto-cruise-with-local-wine-t1206034/", "water-line"),
        ratings=[("GetYourGuide", 4.89, 127, "self")],
        price=36, was=40, psub="per adult", kids=None,
        trust=["✓ Free cancellation up to 24 hours before", "✓ Reserve now, pay later"],
        alts=["Guests on the Water Line boat on the Douro", "Three wines served on a wooden board",
              "Sunset on the Douro from the small boat", "Ribeira houses seen from the river", "Toasting with wine on the cruise"],
        pills=[
            ("🍷", "3 wines + pairings", "Three Portuguese wines:", "a Vinho Verde with cashews, a rosé with dried figs and a Tawny Port with chocolate.", "Every group gets one instant printed photo to take home."),
            ("🌅", "Morning, day or sunset", "Choose your departure:", "morning, daytime or sunset. Sunset trips head towards the ocean when the sea allows.", "Same 2-hour route under the six bridges in every slot."),
            ("🗣️", "Live guide EN/PT/ES", "A skipper and a local guide", "on every trip, commentary in English, Portuguese and Spanish.", "Listed as wheelchair accessible."),
            ("📍", "Douro Marina, Gaia", "Rua da Praia 430, Vila Nova de Gaia,", "near the river mouth. Drop-off at Douro Marina or Marina da Afurada.", "About 5 km downriver from Ribeira: plan a taxi or Uber."),
        ],
        pick="for a real wine pairing with a guide for under €40.",
        skip="if you get seasick: the listing says it is not suitable.",
        pros=[("Three wines with food pairings", "the most complete tasting at this price."),
              ("Small group with a live guide", "a skipper plus a guide, in English, Portuguese or Spanish."),
              ("Sunset slot that heads to the ocean", "weather permitting.")],
        cons=[("Not for seasick travellers", "the route can reach open water at Foz."),
              ("Outside the centre", "Douro Marina is about 5 km from Ribeira.")],
        summary=[
            "For €36 you get 2 hours on a small boat and a proper tasting: Vinho Verde with cashews, a rosé with dried figs and a Tawny Port with chocolate. A skipper drives, a guide talks, and the group stays small.",
            "It leaves from Douro Marina on the Gaia side, near the river mouth, and runs under all six bridges past Ribeira. Sunset departures carry on towards the Atlantic when the sea is calm enough.",
        ],
        facts=[("Duration", "2 hours"), ("Meeting point", "Douro Marina, Rua da Praia 430, 4400-554 Vila Nova de Gaia"),
               ("Included", "Skipper, guide, 3 wines with pairings, 1 instant photo per group"),
               ("Commentary", "English, Portuguese, Spanish"), ("Departures", "Morning, daytime or sunset"),
               ("Cancellation", "Free up to 24 hours before")],
    ),
    dict(
        key="bbdouro-sunset-port", anchor="dp-bbdouro", photos=5,
        rank=("bpa-bronze", "💶 #3 Best Value Sunset"), short="BBDouro: Sunset with Port",
        cats="wine sunset", operator="BBDouro", dur="2 Hours", hours=2,
        pier="Douro Marina, Gaia", maps="Douro Marina, Rua da Praia, Vila Nova de Gaia",
        title="Daytime or Sunset Douro River Cruise with Port Wine",
        href=gyg("/porto-l151/porto-daytime-or-sunset-douro-river-sightseeing-cruise-t243637/", "bbdouro"),
        ratings=[("GetYourGuide", 4.78, 959, "self")],
        price=31, was=39, psub="per adult", kids=None,
        trust=["✓ Free cancellation up to 24 hours before", "✓ Reserve now, pay later"],
        alts=["Glasses of Port wine on the BBDouro sailboat", "Guests relaxing on the sailboat deck",
              "Crew serving guests on board", "Group photo under the Dom Luís I bridge", "Sailboat in front of the Ribeira waterfront"],
        pills=[
            ("🍷", "Glass of Port", "A glass of Port wine is included.", "Snacks are not, so eat before you board.", "Wi-Fi and music on board."),
            ("🌅", "Day or sunset", "Two departures to choose from:", "a daytime cruise or a sunset cruise, 2 hours either way.", "Sunset is the one that sells out first in summer."),
            ("⏱️", "€15.50 per hour", "The cheapest hour on the river with a drink:", "€31 for 2 hours, against €21.60 an hour on the €18 50-minute boats.", "Only the party boat is cheaper per hour."),
            ("📍", "Douro Marina, Gaia", "Douro Marina, Rua da Praia, Vila Nova de Gaia,", "near the river mouth.", "About 5 km downriver from Ribeira: plan a taxi or Uber."),
        ],
        pick="for a 2-hour sunset with Port at €31, less per hour than a 50-minute rabelo.",
        skip="if anyone in your group has limited mobility: the listing says it is not suitable.",
        pros=[("€31 for 2 hours", "about €15.50 an hour, with a glass of Port."),
              ("959 reviews at 4.8/5", "consistent over a lot of trips."),
              ("Daytime or sunset", "the same price for both.")],
        cons=[("No snacks included", "only the Port."),
              ("Not for limited mobility", "per the listing.")],
        summary=[
            "This is the value pick. Two hours on the river with a glass of Port costs €31, which works out cheaper per hour than the €18 six-bridges boats that last 50 minutes.",
            "It sails from Douro Marina in Gaia, so you get the stretch towards the river mouth that the old-town boats skip, then the six bridges and Ribeira. Book the sunset slot and arrive a little early to find the pontoon.",
        ],
        facts=[("Duration", "2 hours"), ("Meeting point", "Douro Marina, Rua da Praia, 4400-554 Vila Nova de Gaia"),
               ("Included", "Cruise, glass of Port wine, Wi-Fi, music, crew, insurance"),
               ("Not included", "Snacks"), ("Departures", "Daytime or sunset"),
               ("Cancellation", "Free up to 24 hours before")],
    ),
    dict(
        key="lecaodouro-7-bridges", anchor="dp-lecaodouro", photos=10,
        rank=("bpa-silver", "⭐ #4 Highest Rated"), short="Leçaodouro: 7 Bridges with Port",
        cats="sunset small", operator="Leçaodouro", dur="2 Hours", hours=2,
        pier="Douro Marina, Afurada", maps="Douro Marina, Rua da Praia 430, Vila Nova de Gaia",
        title="7 Bridges Small-Group Cruise with Port Wine",
        href=gyg("/porto-l151/porto-6-bridges-cruise-port-wine-with-sunset-option-t477703/", "lecaodouro"),
        ratings=[("GetYourGuide", 4.95, 2185, "self")],
        price=37, was=45, psub="per adult", kids=None,
        trust=["✓ Free cancellation up to 24 hours before", "✓ Reserve now, pay later"],
        alts=["Leçaodouro motor yacht under the Dom Luís I bridge", "Sunset under the Arrábida bridge from the deck",
              "Guests toasting with local wine and snacks", "The yacht cruising along the Gaia riverside",
              "Covered lounge on the yacht's rear deck", "Two glasses of Port over the boat's wake",
              "Couple toasting below the Dom Luís I bridge", "Guests watching the sun set over the Atlantic",
              "Small group on the open deck of the yacht", "Lounge cabin below deck"],
        pills=[
            ("🍷", "Welcome glass of Port", "Included:", "a welcome drink of Port, local wine, a soft drink or water.", "Bathroom on board, blankets on cool evenings."),
            ("👥", "Small group", "A small group on a covered motor yacht", "with a local guide and a certified crew.", "Commentary in English, Portuguese and Spanish."),
            ("📍", "Douro Marina, Afurada", "Rua da Praia 430, Vila Nova de Gaia,", "in the fishing village of Afurada near the river mouth.", "About 5 km downriver from Ribeira: plan a taxi or Uber."),
        ],
        pick="for the best score here from a big crowd: 4.95 out of 5 from 2,185 reviews, and the sunset slot heads out toward the Atlantic.",
        skip="if you want food on board: only the welcome drink is included, while #1 adds a tasting board.",
        pros=[("4.95/5 from 2,185 reviews", "the highest score of any cruise here with more than 1,000 reviews."),
              ("Port on board", "a welcome glass of Port, local wine or a soft drink."),
              ("Small group with a guide", "plus a bathroom and blankets on board.")],
        cons=[("Drink only", "no food included."),
              ("Afurada pier", "about 5 km from Ribeira.")],
        summary=[
            "More than 2,000 guests rate this one almost perfect. It is a 2-hour small-group trip on a covered motor yacht from Afurada, past all 7 bridges and up to the Freixo Palace, with a welcome glass of Port and a local guide on board.",
            "The listing price is €37, down from €45, which works out to €18.50 per hour. Pick the sunset slot and you finish with the sun going down over the Atlantic at the river mouth.",
        ],
        facts=[("Duration", "2 hours"), ("Meeting point", "Douro Marina, Rua da Praia 430, 4400-554 Vila Nova de Gaia"),
               ("Included", "Welcome drink (Port, local wine, soft drink or water), guide, certified crew, insurance, fuel"),
               ("On board", "Bathroom, blankets on cool days"), ("Languages", "English, Portuguese, Spanish"),
               ("Cancellation", "Free up to 24 hours before")],
    ),
    dict(
        key="douro-captain-sunset", anchor="dp-douro-captain", photos=6,
        rank=("bpa-silver", "⛵ #5 Smallest Group Sunset"), short="Douro Captain: Sunset Sail, Max 8",
        cats="sunset small", operator="Douro Captain", dur="2 Hours", hours=2,
        pier="Douro Marina, Gaia", maps="Douro Marina, Rua da Praia 430, Vila Nova de Gaia",
        title="2-Hour Sunset River Cruise (Max 8 Guests)",
        href=tiq("tickets-for-porto-2-hr-sunset-river-cruise-p1108469", "douro-captain"),
        ratings=[("Tiqets", 5.0, 21, "self")],
        price=60, was=None, psub="per adult", kids=None,
        trust=["✓ Free cancellation up to 24 hours before", "✓ Instant mobile ticket"],
        alts=["Douro Captain sailboat heading into the sunset", "Sailboat at sunset near the river mouth",
              "Guests on deck watching the sunset", "Sun setting over the Atlantic from the boat",
              "Guests relaxing under the sail", "Sailboat silhouette at dusk"],
        pills=[
            ("👥", "Max 8 guests", "The smallest shared group here:", "never more than 8 people on board.", "Arrive 15 minutes before departure."),
            ("🌅", "Sunset sail to the sea", "From Pontoon C at Douro Marina", "up to Ribeira and Gaia, then out towards the sea past the Douro estuary.", "Timed for sunset, so the start time moves with the season."),
            ("🥂", "Welcome drink", "Included:", "a welcome drink, music on board, a professional crew and travel insurance.", "Skipper speaks English, Spanish and Portuguese."),
        ],
        pick="for a quiet sunset sail with no more than 8 people.",
        skip="if price matters most: at €60 it is the priciest 2-hour shared trip here.",
        pros=[("5.0/5", "every reviewer so far gave five stars."),
              ("Max 8 guests", "the smallest group in this comparison."),
              ("Sunset towards the sea", "the best light of the day at the river mouth.")],
        cons=[("€60 per person", "the most expensive shared 2-hour cruise here."),
              ("Only a welcome drink", "no food on board.")],
        summary=[
            "If the point of the evening is the sunset, this is the calmest way to see it. The group is capped at 8, the boat is a sailboat, and the route runs from Douro Marina past Ribeira and then out towards the sea.",
            "You pay for the small group: €60 per person with a welcome drink. For the same money the #1 yacht includes wine and food, so book this one for the atmosphere, not the catering.",
        ],
        facts=[("Duration", "2 hours"), ("Meeting point", "Pontoon C, Douro Marina, Rua da Praia 430, 4400-554 Vila Nova de Gaia"),
               ("Group size", "Max 8"), ("Included", "Welcome drink, music, professional crew, travel insurance"),
               ("Skipper speaks", "English, Spanish, Portuguese"), ("Cancellation", "Free up to 24 hours before")],
    ),
    dict(
        key="tomaz-do-douro-ribeira", anchor="dp-tomaz-do-douro", photos=5,
        rank=("bpa-silver", "🌉 #6 Best Six Bridges from Ribeira"), short="Tomaz do Douro: Six Bridges",
        cats="budget oldtown", operator="Tomaz do Douro", dur="50 Min", hours=50 / 60,
        pier="Cais da Ribeira", maps="Praça da Ribeira 5, Porto",
        title="Douro River Six Bridges Cruise from Ribeira",
        href=tiq("tickets-for-boat-cruise-from-porto-six-bridges-p1013362", "tomaz-do-douro"),
        ratings=[("Tiqets", 4.3, 280, "self"),
                 ("GetYourGuide", 4.32, 7004, gyg("/porto-l151/porto-6-bridge-cruise-t183308/", "tomaz-do-douro-reviews"))],
        price=20, was=None, psub="per adult", kids=None,
        trust=["✓ Free cancellation up to 48 hours before", "✓ Instant mobile ticket"],
        alts=["Tomaz do Douro rabelo boat under the Dom Luís I bridge", "Rabelo boats moored at Cais da Ribeira",
              "Rabelo boat passing the Gaia riverfront", "The Douro and the Dom Luís I bridge from the boat", "The Arrábida bridge seen from the river"],
        pills=[
            ("📍", "Ribeira quay", "Board at the jetty", "where Cais da Estiva meets Praça da Ribeira, right in the old town.", "No taxi needed if you are already in Ribeira."),
            ("🌉", "Six bridges, 50 min", "All six of Porto's bridges", "in 50 minutes, including the Dom Luís I iron bridge.", "Same classic route as #7, from the Porto side of the river."),
            ("🕒", "Daytime departures", "Boats run through the day,", "10:30 to 16:30 in autumn.", "Pick a date to see that day's times."),
        ],
        pick="for the classic six-bridges ride straight from Ribeira, no transport needed.",
        skip="if you want a drink or live commentary: it is the boat ride only.",
        pros=[("Boards in Ribeira", "the most central pier in Porto."),
              ("7,284 reviews across two sites", "4.3/5 on average."),
              ("€20 for all six bridges", "")],
        cons=[("Boat ride only", "no drinks, no guide."),
              ("48-hour cancellation", "stricter than most cruises here.")],
        summary=[
            "Tomaz do Douro runs the classic 50-minute six-bridges trip from the Ribeira quay, so you can walk on from the old town. It is the same operator many visitors find on both booking sites, and together they count more than 7,000 reviews at 4.3.",
            "Expect a busy boat and no commentary worth the name. You pay for the view of Porto and Gaia from the water, which is the reason most people book it.",
        ],
        facts=[("Duration", "50 minutes"), ("Meeting point", "Jetty at Cais da Estiva and Praça da Ribeira, Praça da Ribeira 5, 4050-513 Porto"),
               ("Included", "Boat tour"), ("Departures", "Daytime, 10:30 to 16:30 in autumn"),
               ("Cancellation", "Free up to 48 hours before")],
    ),
    dict(
        key="manos-do-douro-rabelo", anchor="dp-manos-do-douro", photos=5,
        rank=("bpa-silver", "🎟️ #7 Cheapest Six Bridges"), short="Manos do Douro: Rabelo from Gaia",
        cats="budget oldtown", operator="Manos do Douro", dur="50 Min", hours=50 / 60,
        pier="Gaia quay (opposite Cálem)", maps="Avenida de Diogo Leite 408, Vila Nova de Gaia",
        title="Six Bridges Cruise on a Rabelo Boat",
        href=gyg("/vila-nova-de-gaia-l91806/douro-cruises-sightseeing-t394820/", "manos-do-douro"),
        ratings=[("GetYourGuide", 4.26, 17641, "self")],
        price=18, was=None, psub="per adult", kids="under 3 free (mention it when booking)",
        trust=["✓ Free cancellation up to 24 hours before", "✓ Reserve now, pay later"],
        alts=["Manos do Douro rabelo boat passing under the Dom Luís I bridge", "Porto's Ribeira waterfront from the rabelo",
              "Rabelo boat passing the Gaia riverfront", "Rabelo boat under the Dom Luís I bridge", "The Infante bridge seen from the river"],
        pills=[
            ("🎧", "Audio guide, 4 languages", "Scan the QR code", "on the boat or at the dock: English, French, Portuguese and Spanish.", "Bring your own earphones, none are handed out."),
            ("📍", "Gaia quay", "Avenida de Diogo Leite 408,", "on the Gaia riverfront opposite Cálem, a short walk across the lower deck of the Dom Luís I bridge from Ribeira.", "Show the QR code of your ticket when boarding."),
            ("⛵", "Traditional rabelo", "A rabelo boat,", "the flat-bottomed boat that once carried Port barrels down the Douro.", "Covered, so light rain is not a problem."),
        ],
        pick="for the cheapest six-bridges ticket, with the most reviews of any Porto cruise.",
        skip="if you want a live guide: the commentary is an audio guide on your phone.",
        pros=[("€18, under 3s free", "the cheapest way to see the six bridges."),
              ("17,641 reviews", "the most-booked cruise in Porto."),
              ("Audio guide in 4 languages", "on your own phone.")],
        cons=[("Short commentary", "a few lines per landmark."),
              ("Busy boat", "it is the most popular cruise in the city.")],
        summary=[
            "This is the Porto cruise most visitors take: a 50-minute rabelo trip under all six bridges from the Gaia quay opposite Cálem, for €18. Children up to 3 ride free if you add them when you book.",
            "The audio guide works through a QR code on your own phone, in English, French, Portuguese or Spanish, so bring earphones. Combine it with a Port cellar visit on the same riverfront.",
        ],
        facts=[("Duration", "50 minutes (ticket valid 1 hour)"), ("Meeting point", "Avenida de Diogo Leite 408, 4430-999 Vila Nova de Gaia"),
               ("Included", "Six bridges cruise, audio guide via QR code"),
               ("Audio languages", "English, French, Portuguese, Spanish"),
               ("Kids", "Under 3 free (mention when booking)"), ("Cancellation", "Free up to 24 hours before")],
    ),
    dict(
        key="rentdouro-francesinha-dinner", anchor="dp-rentdouro", photos=4,
        rank=("bpa-silver", "🍽️ #8 Best Dinner Cruise"), short="Rentdouro: Francesinha Dinner",
        cats="", operator="Rentdouro", dur="2 Hours", hours=2,
        pier="Marina do Freixo", maps="Marina do Freixo, Rua do Freixo, Porto",
        title="Six Bridges Evening Cruise with Francesinha Dinner",
        href=gyg("/porto-l151/porto-six-bridges-cruise-with-francesinha-dinner-t1396035/", "rentdouro"),
        ratings=[("GetYourGuide", 4.67, 26, "self")],
        price=40, was=None, psub="per adult, dinner included", kids="0 to 3: infant rate, no meal",
        trust=["✓ Free cancellation up to 24 hours before", "✓ Reserve now, pay later"],
        alts=["Rentdouro boat lit up at night on the Douro", "Guests at dinner on board",
              "Francesinha served on the cruise", "Evening dinner on the river"],
        pills=[
            ("🍽️", "Francesinha dinner", "Three courses:", "cured meats and cheeses, then a Francesinha, Porto's layered sandwich in beer sauce, then house dessert.", "Ask about meal changes before the day."),
            ("🍷", "1 drink", "One drink of your choice:", "water, wine, beer, soft drink, sangria or coffee.", "Extra drinks are not included."),
            ("🌙", "Evening, 2 hours", "An evening cruise", "under the six bridges between Porto and Gaia.", "Hotel pickup is not included."),
            ("📍", "Marina do Freixo", "Rua do Freixo, Porto,", "about 4 km upriver from Ribeira.", "Plan a taxi, Uber or bus."),
        ],
        pick="for dinner and the six bridges in one evening, €40 all in.",
        skip="if you want free-flowing drinks: one drink is included.",
        pros=[("Dinner included for €40", "cheaper than most Porto restaurants with a view."),
              ("Porto's signature dish", "a Francesinha, not a generic buffet."),
              ("Evening departure", "the city lights from the water.")],
        cons=[("Only 26 reviews", "a newer product."),
              ("One drink", "extra drinks cost more.")],
        summary=[
            "Porto has no big dinner-cruise boats like Paris, so this is the closest thing: a 2-hour evening cruise under the six bridges with a three-course meal served on board, built around the Francesinha.",
            "At €40 with one drink it costs about the same as dinner on the Ribeira waterfront. It sails from Marina do Freixo, east of the centre, so add a taxi to your evening.",
        ],
        facts=[("Duration", "About 2 hours, evening"), ("Meeting point", "Marina do Freixo, Rua do Freixo, 4300-316 Porto"),
               ("Included", "Cured meats and cheeses, Francesinha, house dessert, 1 drink"),
               ("Not included", "Additional food and drinks, hotel pickup"),
               ("Kids", "0 to 3: infant rate, no meal"), ("Cancellation", "Free up to 24 hours before")],
    ),
    dict(
        key="douro-style-party-boat", anchor="dp-douro-style", photos=6,
        rank=("bpa-silver", "🎉 #9 Best Party Boat"), short="Douro Style: Party Boat with DJ",
        cats="budget sunset oldtown", operator="Douro Style", dur="2 Hours", hours=2,
        pier="Gaia riverfront", maps="Avenida de Ramos Pinto 710, Vila Nova de Gaia",
        title="Douro River Party Boat with Sunset Option",
        href=tiq("tickets-for-douro-river-party-boat-with-sunset-option-from-porto-p1070095", "douro-style"),
        ratings=[("Tiqets", 4.4, 39, "self")],
        price=18, was=None, psub="per adult", kids=None,
        trust=["✓ Free cancellation up to 24 hours before", "✓ Instant mobile ticket"],
        alts=["DJ playing on the Douro party boat", "Friends dancing on the party boat",
              "Party on the lower deck with green lights", "Welcome to the party sign on board",
              "The party boat on the Douro", "Guest watching the sunset from the boat"],
        pills=[
            ("🎧", "DJ on board", "A DJ plays", "for the whole six-bridges trip.", "More drinks are sold on board."),
            ("🍺", "1 drink", "One drink per person:", "a white wine, two beers or a soft drink.", "No alcohol for under-18s."),
            ("🌅", "Sunset option", "Choose a sunset departure", "for the same price when it is on the calendar.", "Arrive 15 minutes before the start."),
            ("📍", "Gaia riverfront", "Avenida de Ramos Pinto 710,", "on the Gaia side among the Port cellars.", "A short walk from Ribeira across the Dom Luís I bridge."),
        ],
        pick="for groups and birthdays on a budget: 2 hours with a DJ and a drink for €18.",
        skip="if you want a quiet sightseeing cruise.",
        pros=[("€9 per hour", "the cheapest hour on the river in Porto."),
              ("DJ and a drink included", ""),
              ("Gaia pier", "walkable from the old town.")],
        cons=[("Party atmosphere", "not for a quiet view."),
              ("39 reviews", "fewer than the classic boats.")],
        summary=[
            "Two hours on the Douro with a DJ and a drink for €18 is the best deal on the river per hour. It is a party first and a sightseeing cruise second, so book it with friends, not with grandparents.",
            "It leaves from the Gaia riverfront among the Port cellars, a short walk from Ribeira, and there is a sunset departure on many days.",
        ],
        facts=[("Duration", "2 hours"), ("Meeting point", "Avenida de Ramos Pinto 710, 4400-161 Vila Nova de Gaia"),
               ("Included", "Six bridges cruise, DJ, 1 drink (white wine, two beers or a soft drink)"),
               ("Not included", "Additional drinks (sold on board)"), ("Age", "No alcohol for under-18s"),
               ("Cancellation", "Free up to 24 hours before")],
    ),
    dict(
        key="douro-valley-regua-cruise", anchor="dp-douro-valley", photos=6,
        rank=("bpa-silver", "🍇 #10 Best Douro Valley Day Cruise"), short="Porto to Régua: Full-Day Cruise",
        cats="wine oldtown", operator="Living Tours", dur="11 Hours", hours=11,
        pier="Cais da Estiva, Ribeira", maps="Cais da Estiva, Porto",
        title="Douro Valley: River Cruise + Breakfast & Lunch from Porto",
        href=tiq("tickets-for-porto-regua-porto-douro-valley-upstream-cruise-with-breakfast-and-lunch-p1027807", "douro-valley"),
        ratings=[("Tiqets", 4.1, 43, "self")],
        price=76, was=None, psub="per adult, meals included", kids=None,
        trust=["✓ Free cancellation up to 72 hours before", "✓ Instant mobile ticket"],
        alts=["Cruise boat sailing through the terraced Douro Valley", "Breakfast table on board the Douro Valley cruise",
              "Douro Valley vineyards above the river", "Guests watching the Crestuma-Lever dam lock",
              "Lunch on board with a view of the river", "Vineyards of the Douro Valley at sunset"],
        pills=[
            ("🚢", "Porto to Régua by boat", "Upriver from Porto to Régua,", "through the lock of the Crestuma-Lever dam, then back to Porto by bus.", "11 hours in total."),
            ("🕗", "08:00 from Ribeira", "Meet at 08:00", "at Cais da Estiva in Ribeira, in front of Café do Cais.", "Back in Porto in the evening."),
            ("🍷", "Breakfast, lunch, drinks", "Included:", "breakfast and lunch on board, with drinks.", "Tips are not included."),
            ("📅", "From April", "A seasonal cruise:", "the next departures are in April 2027, on weekdays.", "No winter sailings."),
        ],
        pick="to see the terraced Douro Valley from the water in one day, meals included.",
        skip="if you visit before April: there are no winter departures.",
        pros=[("The real Douro Valley", "vineyards and the dam lock, not just the city."),
              ("Breakfast, lunch and drinks included", ""),
              ("Starts in Ribeira", "no hotel transfer needed.")],
        cons=[("A long day", "11 hours, with the return by bus."),
              ("Seasonal", "no departures in winter.")],
        summary=[
            "This is what many people mean by a Douro river cruise: a full day upriver from Porto to Régua, between the terraced vineyards, with breakfast and lunch on board. You go through the Crestuma-Lever dam lock on the way, and a bus brings you back in the evening.",
            "It is a seasonal trip. The next sailings are on weekdays from April 2027 at €76, so if you are in Porto in winter, book one of the city cruises above instead.",
        ],
        facts=[("Duration", "11 hours (boat upriver, bus back)"), ("Meeting point", "Cais da Estiva, Ribeira, in front of Café do Cais, 08:00"),
               ("Included", "Cruise from Porto to Régua, breakfast, lunch, drinks, bus back to Porto"),
               ("Not included", "Gratuities"), ("Season", "Weekday departures from April 2027"),
               ("Cancellation", "Free up to 72 hours before")],
    ),
]

FILTERS = [("all", "All"), ("sunset", "🌅 Sunset departures"), ("wine", "🍷 Wine or Port included"),
           ("small", "👥 Small groups"), ("budget", "💶 Under €25"), ("oldtown", "📍 Boards in Ribeira or Gaia")]

N = len(CRUISES)
TITLE = f"Douro River Cruises in Porto: {N} Best Boat Tours (2026)"
H1 = f"The {N} Best Douro River Cruises in Porto"
DESC = ("Porto river cruises compared: six-bridges boats from €18, sunset boats with Port, a Francesinha dinner "
        "cruise and a day to Régua, with piers and price per hour.")
LEAD = [
    "The €31 two-hour sunset boat costs less per hour than the €18 six-bridges rabelo, and that is not the only thing most Porto cruise lists get wrong.",
    "I compared Porto's most popular Douro cruises side by side on what decides the booking: how long you are really on the water, what is included, and which pier you have to get to.",
    "Below are the 10 worth booking, from the classic 50-minute rabelo to a yacht with wine that sails out to the Atlantic, plus a full day upriver to the Douro Valley.",
]
QUICK = [
    ("Best overall", 0), ("Best wine tasting", 1), ("Best value sunset", 2), ("Cheapest six bridges", 6), ("Best dinner", 7),
]


# ---------------------------------------------------------------------------- helpers
def fmt_price(p):
    return f"€{p:.2f}" if p != int(p) else f"€{int(p)}"


def weighted(c):
    tot = sum(n for _, _, n, _ in c["ratings"])
    return sum(s * n for _, s, n, _ in c["ratings"]) / tot, tot


def k(n):
    return f"{n:,}"


def maps(q):
    return "https://www.google.com/maps/search/?api=1&query=" + q.replace(" ", "+").replace(",", "%2C")


def photos(c):
    return [f"{IMG}{c['key']}-{i:02d}.avif" for i in range(1, c["photos"] + 1)]


ICONS, STAR = {}, ""


def load_assets(seine):
    global STAR
    for site in ("GetYourGuide", "Tiqets"):
        m = re.search(r'<img alt="%s" class="bpa-rev-icon" loading="lazy" src="(data:[^"]+)"' % site, seine)
        ICONS[site] = m.group(1)
    STAR = re.search(r'<svg aria-hidden="true" viewbox="0 0 24 24">.*?</svg>', seine, re.S).group(0)


def badge(site, score, n, href):
    inner = (f'<img alt="{site}" class="bpa-rev-icon" loading="lazy" src="{ICONS[site]}"/>'
             f'<span class="bpa-rev-site">{site}</span><span class="bpa-rev-score">{score:.1f}</span>'
             f'<span class="bpa-rev-stars">{STAR * 5}</span><span class="bpa-rev-count">({k(n)})</span>')
    if href:
        return (f'<a class="bpa-rev-badge is-link" href="{E(href)}" rel="nofollow sponsored noopener" target="_blank">{inner}'
                f'<span class="bpa-rev-go" aria-hidden="true">→</span></a>')
    return f'<span class="bpa-rev-badge is-static">{inner}</span>'


def rating_block(c):
    r, tot = weighted(c)
    sites = len(c["ratings"])
    meta = f"{k(tot)} reviews" + (f" · {sites} sites" if sites > 1 else "")
    lead = ("Average of 2 booking sites, weighted by number of reviews" if sites > 1 else "Rating on the booking site")
    badges = "".join(badge(s, sc, n, c["href"] if h == "self" else h) for s, sc, n, h in c["ratings"])
    return (f'<div class="bpa-summary-reviews bpa-rate"><details class="bpa-lang bpa-rate-more"><summary class="bpa-rate-sum">'
            f'<span class="bpa-stars" style="--r:{r:.2f}" aria-hidden="true"></span><b class="bpa-rate-score">{r:.1f}</b>'
            f'<span class="bpa-rate-meta">{meta}</span><span class="bpa-lang-chev" aria-hidden="true">▾</span></summary>'
            f'<div class="bpa-lang-pop"><strong>{lead}</strong><span class="bpa-rate-list">{badges}</span></div></details></div>')


def pill(emoji, label, lead, text, note):
    return (f'<details class="bpa-lang"><summary class="bpa-sp">{emoji} <span class="bpa-lang-label">{E(label)}</span>'
            f'<span class="bpa-lang-chev" aria-hidden="true">▾</span></summary><div class="bpa-lang-pop"><strong>{E(lead)}</strong> {E(text)}'
            + (f'<span class="bpa-lang-note">{E(note)}</span>' if note else "") + '</div></details>')


def kicker(c):
    return (f'{E(c["operator"])} • ⏱️ {c["dur"]} • <a class="bpa-kicker-map-link" href="{E(maps(c["maps"]))}" '
            f'onclick="event.stopPropagation()" rel="noopener noreferrer" target="_blank">📍 {E(c["pier"])}</a>')


def card(i, c):
    imgs = "".join(
        f'<img alt="{E(a)}" height="534" width="800" loading="{"eager" if i == 0 and j == 0 else "lazy"}" decoding="async" src="{p}"/>'
        for j, (p, a) in enumerate(zip(photos(c), c["alts"])))
    was = (f'<div class="bpa-was"><s>{fmt_price(c["was"])}</s> <span>−{round(100 - 100 * c["price"] / c["was"])}%</span></div>'
           if c["was"] else "")
    kids = f'<div class="bpa-kids">{E(c["kids"])}</div>' if c["kids"] else ""
    via = "Tiqets" if "tiqets.com" in c["href"] else "GetYourGuide"
    trust = "".join(f"<span>{E(t)}</span>" for t in c["trust"])
    return f'''<div class="bpa-card" data-cat="{c["cats"]}" id="card-{i + 1}">
<div class="bpa-main">
<div class="bpa-media">
<span class="bpa-rank-tag {c["rank"][0]}">{c["rank"][1]}</span>
<button aria-label="Previous photo" class="bpa-arrow prev" onclick="bpaSlide(this,-1)" type="button">‹</button>
<button aria-label="Next photo" class="bpa-arrow next" onclick="bpaSlide(this,1)" type="button">›</button>
<span class="bpa-pill">1 / {c["photos"]}</span>
<div class="bpa-slider" tabindex="0" aria-label="Photo Gallery" onscroll="bpaCount(this)">{imgs}</div>
</div>
<div class="bpa-info">
<div class="bpa-kicker">{kicker(c)}</div>
<a class="bpa-title" href="{E(c["href"])}" rel="nofollow sponsored noopener" target="_blank">{E(c["title"])}</a>
<div class="bpa-reviews-line">
{rating_block(c)}
</div>
<div class="bpa-specs-row">
{"".join(pill(*p) for p in c["pills"])}
</div>
<div class="bpa-best-for bpa-pickskip"><span class="bpa-pick">✓ Pick it</span> {E(c["pick"])} <span class="bpa-skip">✕ Skip it</span> {E(c["skip"])}</div>
</div>
<div class="bpa-cta-cell">
<div>
{was}<div class="bpa-price">{fmt_price(c["price"])}</div>
<div class="bpa-psub">{E(c["psub"])}</div>
{kids}</div>
<a class="bpa-btn" href="{E(c["href"])}" rel="nofollow sponsored noopener" target="_blank">Check Availability →</a>
<div class="bpa-via">Booked securely via {via}</div>
<div class="bpa-trust2">{trust}</div>
<a class="bpa-sublink" href="#{c["anchor"]}">Full review ↓</a>
</div>
</div>
</div>
'''


def details(i, c):
    r, tot = weighted(c)
    pros = "".join(f"<li><strong>{E(a)}</strong>" + (f": {E(b)}" if b else "") + "</li>" for a, b in c["pros"])
    cons = "".join(f"<li><strong>{E(a)}</strong>" + (f": {E(b)}" if b else "") + "</li>" for a, b in c["cons"])
    summ = "".join(f"<p>{E(p)}</p>" for p in c["summary"])
    facts = "".join(f'<div class="qf1-row"><div class="qf1-label">{E(a)}</div><div class="qf1-val">{E(b)}</div></div>' for a, b in c["facts"])
    film = "".join(f'<div class="ltt-strip-slide"><img alt="{E(a)}" height="534" width="800" loading="lazy" decoding="async" src="{p}"/>'
                   f'<div class="ltt-strip-cap"><span class="ltt-strip-num">{j + 1} / {c["photos"]}</span> <span>Photo: {E(c["operator"])}</span></div></div>'
                   for j, (p, a) in enumerate(zip(photos(c), c["alts"])))
    return f'''<details class="bpa-details-card" data-cat="{c["cats"]}" id="{c["anchor"]}" open="">
<summary class="bpa-details-summary">
<div class="bpa-details-summary-content">
<div class="bpa-details-top-row">
<span class="bpa-rank-tag {c["rank"][0]}">{c["rank"][1]}</span>
<div class="bpa-kicker">{kicker(c)}</div>
</div>
<h3 class="bpa-details-title">{E(c["title"])}</h3>
<div class="bpa-reviews-line">{rating_block(c)}</div>
</div>
<div class="bpa-details-right">
<span class="bpa-details-price">{fmt_price(c["price"])}</span>
<div class="bpa-details-toggle">
<span class="bpa-details-state-text"></span>
<span class="bpa-details-chevron">▾</span>
</div>
</div>
</summary>
<div class="bpa-details-body">
<div class="pro-con-box-wrapper"><div class="w-layout-grid grid-15"><div class="pro-con-box-pro-cell"><div class="pro-con-box-pro-cell-rich-text-block w-richtext"><h3><strong>Pros:</strong></h3><ul>{pros}</ul></div></div><div class="pro-con-box-con-cell"><div class="pro-con-box-con-cell-rich-text-block w-richtext"><h3><strong>Cons:</strong></h3><ul>{cons}</ul></div></div></div></div>
<details class="ltt-bento-group" open=""><summary class="ltt-bento-group-head"><span class="ltt-bento-group-title">📸 Photos</span><span class="ltt-bento-right"><span class="ltt-mini-pill">Swipe {c["photos"]} Photos →</span><span class="ltt-bento-chev">▾</span></span></summary><div class="ltt-bento-group-body" style="padding: 12px 14px !important;"><div class="ltt-filmstrip-wrap"><button aria-label="Previous photo" class="ltt-film-btn ltt-film-prev is-disabled" onclick="window.lttFilmSlide(this, -1)" type="button">‹</button><button aria-label="Next photo" class="ltt-film-btn ltt-film-next" onclick="window.lttFilmSlide(this, 1)" type="button">›</button><div class="ltt-filmstrip" onscroll="window.lttFilmSync(this)">{film}</div></div></div></details>
<details class="ltt-bento-group" open="">
<summary class="ltt-bento-group-head">
<span class="ltt-bento-group-title">Summary &amp; Review</span>
<span class="ltt-bento-right">
<span class="ltt-mini-pill">Overview</span>
<span class="ltt-bento-chev">▾</span>
</span>
</summary>
<div class="ltt-bento-group-body">
<div class="w-richtext">{summ}</div>
</div>
</details>
<div class="qf1-wrap"><div class="qf1-title-row"><h4 class="qf1-title">Quick Facts</h4><span class="qf1-badge">{E(c["pier"])}</span></div><div class="qf1-table">{facts}</div></div>
<a class="bpa-btn" href="{E(c["href"])}" rel="nofollow sponsored noopener" style="margin-top:14px;display:block;text-align:center" target="_blank">Check Availability: {fmt_price(c["price"])} →</a></div>
</details>
'''


def per_hour(c):
    v = c["price"] / c["hours"]
    return f"€{v:.2f}".replace(".00", "")


def hero():
    filt = []
    for cat, label in FILTERS:
        n = N if cat == "all" else sum(cat in c["cats"].split() for c in CRUISES)
        active = " active" if cat == "all" else ""
        filt.append(f'<button class="ltt-tab-btn{active}" data-cat="{cat}" onclick="lttFilterItems(\'{cat}\', this)" type="button">{E(label)} ({n})</button>')
    quick = "".join(
        f'<li><span class="dp-qp-label">{E(lbl)}:</span> <a class="dp-qp-link" href="#card-{i + 1}">{E(CRUISES[i]["short"])}</a> <span class="dp-qp-price">{fmt_price(CRUISES[i]["price"])}</span></li>'
        for lbl, i in QUICK)
    return f'''<div class="ltt-hero-wrap">
<div class="ltt-clean-card">
<div class="ltt-top-bar">
<nav aria-label="Breadcrumb" class="ltt-breadcrumbs">
<a href="/">Home</a>
<span class="ltt-bc-sep">›</span>
<span class="ltt-bc-current">Douro River Cruises in Porto</span>
</nav>
<span class="ltt-hero-kicker-badge">2026 Porto Cruise Comparison</span>
</div>
<h1 class="ltt-editorial-h1">{E(H1)} <span class="ltt-h1-muted">(2026)</span></h1>
<div class="ltt-trust-bar">
<div class="ltt-author-cluster">
<div class="ltt-author-avatar-wrap">
<img alt="Adam Dimitrov" class="ltt-author-avatar" src="https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp"/>
</div>
<div class="ltt-author-meta">
<div class="ltt-author-line">
            By <a href="/about" target="_blank">Adam Dimitrov</a>, Owner &amp; Head Cruise Detective
          </div>
<div class="ltt-author-role">Compared side by side on live listings • Independent comparison</div>
</div>
</div>
<div class="ltt-trust-pills">
<span class="ltt-trust-pill paragraph-26"><strong>Last updated</strong>: Nov 15, 2026</span>
</div>
</div>
<div class="ltt-lead-copy">
<p class="dp-callout">{E(LEAD[0])}</p>
<p>{E(LEAD[1])}</p>
<p>{E(LEAD[2])}</p>
<div class="dp-quick"><div class="dp-quick-title">Quick picks</div><ul>{quick}</ul></div>
</div>
<div class="ltt-integrated-filter-bar">
<span class="ltt-filter-label">Filters:</span>
<div class="ltt-integrated-pills">{"".join(filt)}</div>
</div>
</div>
</div>'''


def table():
    head = "<tr><th>Cruise</th><th>Price</th><th>Time on the water</th><th>Per hour</th><th>Pier</th><th>Food and drink included</th></tr>"
    inc = ["Wine, tasting board", "3 wines, pairings", "Glass of Port", "Welcome drink, local plate", "Welcome drink",
           "Nothing", "Audio guide only", "Dinner, 1 drink", "1 drink, DJ", "Breakfast, lunch, drinks"]
    rows = "".join(
        f'<tr><td><a href="#{c["anchor"]}">{E(c["short"])}</a></td><td>{fmt_price(c["price"])}</td><td>{E(c["dur"].replace("Min", "min").replace("Hours", "hours"))}</td>'
        f'<td>{per_hour(c) if c["hours"] < 5 else "Full day"}</td><td>{E(c["pier"])}</td><td>{E(x)}</td></tr>'
        for c, x in zip(CRUISES, inc))
    return f'<div class="dp-table-wrap"><table class="dp-table"><thead>{head}</thead><tbody>{rows}</tbody></table></div>'


FAQ = [
    ("How much does a Douro river cruise in Porto cost?",
     "A 50-minute six-bridges cruise costs €18 to €20. Two-hour small-boat and sunset cruises cost €31 to €60 and usually include a drink, and a full day upriver to Régua with breakfast and lunch costs €76."),
    ("What are the six bridges of Porto?",
     "From the river mouth upstream: Arrábida, Dom Luís I, Infante D. Henrique, Maria Pia, São João and Freixo. Every cruise on this list passes all six; the 2-hour boats also sail towards Foz, where the Douro meets the Atlantic."),
    ("Which Porto cruise is best at sunset?",
     "BBDouro is the best value at €31 with a glass of Port, Douro Captain is the quietest with no more than 8 guests, and Water Line adds three wines with pairings. All three leave from Douro Marina in Gaia, close to the river mouth where the sun sets."),
    ("Can I cruise to the Douro Valley as a day trip from Porto?",
     "Yes. The Porto to Régua cruise leaves Ribeira at 08:00, sails upriver through the Crestuma-Lever dam lock with breakfast and lunch on board, and brings you back by bus, 11 hours in total. It is seasonal: the next departures are in April 2027."),
    ("Is hotel pickup included?",
     "No. You meet each boat at its pier: Ribeira and the Gaia quay are in the old town, while Douro Marina in Gaia and Marina do Freixo are 4 to 5 km away, so plan a taxi or Uber for those."),
    ("Do Porto river cruises run in winter and in the rain?",
     "The city cruises run all year, and most boats are covered or carry blankets, so light rain is fine. Operators cancel for storms and offer a new date or a refund. The full-day Douro Valley cruise does not sail in winter."),
    ("Which cruise is best with kids?",
     "The 50-minute rabelo from the Gaia quay: it is short, covered, children under 3 ride free, and there is an audio guide in 4 languages. Skip the party boat and the 2-hour sails if your children get restless."),
]


def sections():
    faq = "".join(f"<h3>{E(q)}</h3><p>{E(a)}</p>" for q, a in FAQ)
    return f'''<section data-toc="Is It Worth It?" id="dp-worth-it"><div class="w-richtext"><h2>Is a Douro River Cruise in Porto Worth It?</h2><p>Yes, and it is one of the cheapest good things to do in Porto. The city is built on two steep banks, so the river is the only place where you see Ribeira, the Gaia Port cellars and all six bridges at once.</p><p>The real choice is between two kinds of boat. The 50-minute six-bridges cruises cost €18 to €20, leave from the old town and are mostly about the view. The 2-hour boats cost €31 to €60, leave from the marinas, sail out to the river mouth and usually include wine or Port. If you have a spare evening, the 2-hour boat is the better deal per hour.</p><p>Comparing cities? Here is how the <a href="/seine-river-cruises-paris">best Seine cruises in Paris</a>, the <a href="/thames-river-cruises-london">Thames cruises in London</a> and the <a href="/canal-cruises-amsterdam">Amsterdam canal cruises</a> stack up.</p></div></section>
<section data-toc="Side-by-Side Table" id="dp-compare-table"><div class="w-richtext"><h2>Porto River Cruises Side by Side</h2><p>Price per hour is the ticket price divided by the time you actually spend on the water. It is the quickest way to see which boats are good value.</p>{table()}</div></section>
<section data-toc="Which Pier?" id="dp-piers"><div class="w-richtext"><h2>Where Do Porto Cruises Leave From?</h2><p>The pier matters more than the boat, because none of these cruises include hotel pickup:</p><ul><li><strong>Ribeira, Porto side (#6, #10):</strong> Cais da Ribeira and Cais da Estiva, in the old town. Walk down from the Dom Luís I bridge.</li><li><strong>Gaia quay (#7, #9):</strong> Avenida de Diogo Leite and Avenida de Ramos Pinto, among the Port cellars. Cross the lower deck of the Dom Luís I bridge from Ribeira.</li><li><strong>Douro Marina and Afurada, Gaia (#2, #3, #4, #5):</strong> Rua da Praia 430, about 5 km downriver near the river mouth. Take a taxi or Uber.</li><li><strong>Marina do Freixo, Porto (#1, #8):</strong> about 4 km upriver, next to the Freixo bridge. Take a taxi, Uber or bus.</li></ul><p>The marina boats are the ones that reach Foz and the ocean, which is why they are worth the extra trip.</p></div></section>
<section data-toc="Best Time to Go" id="dp-best-time"><div class="w-richtext"><h2>Best Time for a Douro Cruise</h2><p>Book the last departure of the day. Porto faces west down the river, so the sunset over the river mouth is the best light you will get, from around 17:15 in December to around 21:00 in late June.</p><p>From May to September the sunset boats sell out first, so book a few days ahead. In winter the city cruises still run, but take a jacket: the 2-hour boats reach open water at Foz, where it is always windier than in Ribeira. The Douro Valley day cruise only sails from spring to autumn.</p></div></section>
<section data-toc="FAQ" id="dp-faq"><div class="w-richtext"><h2>Douro River Cruises in Porto: FAQ</h2>{faq}</div></section>
<section data-toc="How I Compared" id="dp-methodology"><div class="w-richtext"><h2>How I Picked These {N} Porto Cruises</h2><p>On {CHECKED} I went through every Douro cruise in Porto bookable on Tiqets and GetYourGuide and compared them side by side on price, time on the water, price per hour, pier, what is included, group size and cancellation terms. Prices, ratings and inclusions are taken from the live listings on that date and can change.</p><p>I kept one product per operator and boat. Where the same boat is sold on both sites, I list it once and add the ratings together, weighted by the number of reviews. Resellers of a boat already on the list, tours where the cruise is a small add-on, and private charters were left out.</p></div></section>'''


def jsonld():
    items = []
    for i, c in enumerate(CRUISES, 1):
        r, tot = weighted(c)
        items.append({"@type": "ListItem", "position": i, "item": {
            "@type": "TouristTrip", "name": c["title"], "description": f"Pick it {c['pick']}",
            "image": [SITE + p for p in photos(c)[:3]],
            "provider": {"@type": "Organization", "name": c["operator"]},
            "offers": {"@type": "Offer", "price": f"{c['price']:g}", "priceCurrency": "EUR", "url": c["href"], "availability": "https://schema.org/InStock"}}})
    graph = [
        {"@type": "Article", "@id": URL + "#article", "headline": TITLE, "description": DESC,
         "image": [SITE + photos(c)[0] for c in CRUISES], "datePublished": ISO, "dateModified": ISO, "inLanguage": "en",
         "mainEntityOfPage": {"@type": "WebPage", "@id": URL},
         "author": {"@type": "Person", "name": "Adam Dimitrov", "jobTitle": "Owner & Head Cruise Detective", "url": SITE + "/about"},
         "publisher": {"@type": "Organization", "name": "The Cruise Detective", "url": SITE,
                       "logo": {"@type": "ImageObject", "url": "https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/6570a89c8c97ba4e084ac5d5_webclip-cruise-detective.png"}},
         "mainEntity": {"@id": URL + "#list"}},
        {"@type": "BreadcrumbList", "@id": URL + "#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Douro River Cruises in Porto", "item": URL}]},
        {"@type": "ItemList", "@id": URL + "#list", "name": TITLE, "numberOfItems": N, "itemListElement": items},
        {"@type": "FAQPage", "@id": URL + "#faq", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]},
    ]
    return ('<script id="douro-porto-schema-jsonld" type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False) + "</script>")


EXTRA_CSS = '''<style id="dp-page-css">
.dp-callout{font-size:1.08em;font-weight:600;color:#0f172a;border-left:4px solid #dfa732;padding:6px 0 6px 14px;background:#fffbeb}
.dp-quick{margin:14px 0 4px;padding:12px 14px;border:1px solid #e2e8f0;border-radius:12px;background:#f8fafc}
.dp-quick-title{font-weight:800;font-size:.85em;letter-spacing:.04em;text-transform:uppercase;color:#334155;margin-bottom:6px}
.dp-quick ul{margin:0!important;padding-left:18px!important}.dp-quick li{margin:3px 0!important;font-size:15px!important;line-height:1.5!important}
.dp-quick li *{font-size:15px!important}
.dp-qp-label{font-weight:700;color:#0f172a}.dp-qp-price{color:#9f6e0d;font-weight:700;white-space:nowrap}
a.dp-qp-link,a.dp-qp-link:hover{color:#0369a1;text-decoration:underline}
.dp-table-wrap{overflow-x:auto;-webkit-overflow-scrolling:touch;margin:14px 0;border:1px solid #e2e8f0;border-radius:10px;max-width:100%}
.dp-table{width:100%;border-collapse:collapse;font-size:14px;min-width:640px}
.dp-table th,.dp-table td{padding:8px 10px;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top}
.dp-table th{background:#f8fafc;font-weight:700;color:#0f172a}
.dp-table a,.dp-table a:hover{color:#0369a1}
.ltt-editorial-wrapper a:hover,.bpa-kicker-map-link:hover,.bpa-sublink:hover{color:#0369a1}
</style>'''


# ---------------------------------------------------------------------------- build
def block_end(h, start):
    tag = re.match(r"<(\w+)", h[start:]).group(1)
    d = 0
    for m in re.finditer(r"<(/?)%s\b[^>]*>" % tag, h[start:]):
        d += -1 if m.group(1) else 1
        if d == 0:
            return start + m.end()
    raise ValueError(tag)


def build():
    tpl = (ROOT / "private-cruises-paris/index.html").read_text(encoding="utf-8")
    seine = (ROOT / "seine-river-cruises-paris/index.html").read_text(encoding="utf-8")
    load_assets(seine)
    h = tpl

    # head
    h = re.sub(r"<title>[^<]*</title>", f"<title>{E(TITLE)}</title>", h, count=1)
    for attr in ('name="description"', 'property="og:description"', 'name="twitter:description"'):
        h = re.sub(r'<meta content="[^"]*" %s/>' % re.escape(attr), f'<meta content="{E(DESC)}" {attr}/>', h, count=1)
    for attr in ('property="og:title"', 'name="twitter:title"'):
        h = re.sub(r'<meta content="[^"]*" %s/>' % re.escape(attr), f'<meta content="{E(TITLE)}" {attr}/>', h, count=1)
    hero_img = SITE + photos(CRUISES[0])[0]
    for attr in ('property="og:image"', 'name="twitter:image"'):
        h = re.sub(r'<meta content="[^"]*" %s/>' % re.escape(attr), f'<meta content="{hero_img}" {attr}/>', h, count=1)
    h = re.sub(r'<meta content="[^"]*" property="og:url"/>', f'<meta content="{URL}" property="og:url"/>', h, count=1)
    h = re.sub(r'<link href="[^"]*" rel="canonical"/>', f'<link href="{URL}" rel="canonical"/>', h, count=1)
    h = re.sub(r'(?:<link href="[^"]*" hreflang="[^"]*" rel="alternate"/>\s*)+',
               f'<link href="{URL}" hreflang="en" rel="alternate"/>\n<link href="{URL}" hreflang="x-default" rel="alternate"/>\n', h, count=1)
    h = re.sub(r'<link as="image" fetchpriority="high" href="[^"]*" rel="preload"/>',
               f'<link as="image" fetchpriority="high" href="{photos(CRUISES[0])[0]}" rel="preload"/>', h, count=1)
    h = re.sub(r'<script id="private-cruises-schema-jsonld" type="application/ld\+json">.*?</script>', lambda m: jsonld(), h, count=1, flags=re.S)
    h = re.sub(r"<script>const alternativeLanguagePages = .*?</script>\n?", "", h, count=1, flags=re.S)
    h = re.sub(r"<script>const LINGUANA_LANGUAGE_ROUTES = .*?</script>\n?", "", h, count=1, flags=re.S)

    # card styles + pill dropdown CSS/JS from the Seine page
    seine_css = re.search(r'<style id="ltt-dubai-safari-styles">.*?</style>', seine, re.S).group(0)
    h = re.sub(r'<style id="ltt-dubai-safari-styles">.*?</style>', lambda m: seine_css, h, count=1, flags=re.S)
    lang_css = re.search(r'<style id="bpa-lang-css">.*?</style>', seine, re.S).group(0)
    lang_js = re.search(r'<script id="bpa-lang-js">.*?</script>', seine, re.S).group(0)
    h = h.replace("</head>", lang_css + EXTRA_CSS + "</head>", 1)
    h = h.replace("</body>", lang_js + "</body>", 1)

    # hero
    s = h.index('<div class="ltt-hero-wrap">')
    e = block_end(h, s)
    h = h[:s] + hero() + h[e:]

    # deck
    s = h.index('<div class="ltt-deck-container" id="paris-private-cruise-deck">')
    e = block_end(h, s)
    deck = ('<div class="ltt-deck-container" id="douro-porto-cruise-deck">\n<div class="bpa-deck-wrap" id="ltt-cards-deck">'
            + "".join(card(i, c) for i, c in enumerate(CRUISES)) + "</div>\n</div>")
    h = h[:s] + deck + h[e:]

    # breakdown header + details cards
    s = h.index('<div class="bpa-breakdown-top-bar" id="breakdown-header">')
    last = [m.start() for m in re.finditer(r'<details class="bpa-details-card"', h)][-1]
    e = block_end(h, last)
    top = f'''<div class="bpa-breakdown-top-bar" id="breakdown-header">
<div>
<h2 class="bpa-breakdown-heading" id="douro-cruises-breakdown">Detailed Breakdown: {N} Douro River Cruises in Porto</h2>
<p class="bpa-breakdown-sub">Prices, piers and inclusions compared side by side</p>
</div>
<div class="bpa-acc-controls">
<button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)" type="button">Expand All</button>
<button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)" type="button">Collapse All</button>
</div>
</div>'''
    h = h[:s] + top + "".join(details(i, c) for i, c in enumerate(CRUISES)) + h[e:]

    # guide sections
    s = h.index('<section data-toc="Is It Worth It?"')
    e = block_end(h, h.index('<section data-toc="How I Compared"'))
    h = h[:s] + sections() + h[e:]

    # sticky bar + page config
    c0 = CRUISES[0]
    h = h.replace("<span>All 6 Private Cruises</span>", f"<span>All {N} Porto Cruises</span>", 1)
    h = re.sub(r'(<span class="hybrid-active-title" id="sticky-name">)[^<]*', lambda m: m.group(1) + E(c0["short"]), h, count=1)
    h = re.sub(r'(<span class="hybrid-active-price" id="sticky-price">)[^<]*', lambda m: m.group(1) + fmt_price(c0["price"]), h, count=1)
    h = re.sub(r'(<a class="hybrid-cta-btn" href=")[^"]*(" id="sticky-cta-btn" rel=")[^"]*', lambda m: m.group(1) + E(c0["href"]) + m.group(2) + "nofollow sponsored noopener", h, count=1)
    h = h.replace("Jump to Paris Private Cruise", "Jump to a Porto Cruise")
    cfg = {"deckId": "douro-porto-cruise-deck", "tocDeckLabel": f"Top {N} Porto Cruises",
           "tocBreakdownLabel": f"Detailed Breakdown ({N} Cruises)", "shortTitles": [c["short"] for c in CRUISES]}
    h = re.sub(r"window\.LTT_PAGE_CONFIG = \{.*?\};", lambda m: "window.LTT_PAGE_CONFIG = " + json.dumps(cfg, ensure_ascii=False) + ";", h, count=1, flags=re.S)

    # leftovers from the template that must not survive
    for bad in ("private-cruises-paris\"", "Private Seine", "Visite Paris"):
        pass
    out = ROOT / SLUG / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(h, encoding="utf-8")
    left = [w for w in ("Visite Paris", "Seine cruise", "Private Cruise", "private-cruises-paris") if w in re.sub(r'<header class="ltt-navbar".*?</header>|<footer class="footer-dark".*?</footer>', "", h, flags=re.S)]
    print("wrote", out.relative_to(ROOT), len(h), "bytes; template leftovers:", left or "none")


if __name__ == "__main__":
    build()
