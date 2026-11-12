#!/usr/bin/env python3
"""
Fill in missing alt text on site pages (idempotent).

* Review-platform icons (class "bpa-rev-icon", inline data-URI logos next to a
  score) get the platform name - the icon is the only thing that says which
  platform the score is from.
* Content photos that had alt="" get a localized description (keyed by the
  asset id in the file name).
* Logos / payment badges on the English Amsterdam guide get English alts.
* The Meta pixel <noscript> image gets alt="" (decorative, never shown).

Only <img> tags whose alt is missing or empty are touched.
"""

import hashlib
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGS = ["fr", "de", "es", "it", "nl", "pl", "ro", "ja"]

# md5(src)[:8] of the inline review-platform icons -> platform
ICONS = {"8709a15f": "Tiqets", "9ed8dff8": "GetYourGuide", "bd87e945": "Viator", "bc4cfa6c": "Tripadvisor"}

# English-only logos (asset id -> alt)
LOGOS = {
    "6852917a8b23e16d4296b394": "Tiqets",
    "65325ee2255a64979bc2e8c4": "GetYourGuide",
    "65325f5c5363ff458c1051df": "Viator",
    "65325c2aeebb4df779830d4f": "Tripadvisor",
    "6970f694366890b5b4348a92": "Accepted payment methods",
    "67e914cce5f540f75b5a5b2d": "Accepted payment methods",
}

PHOTOS = {
    # dinner guide FAQ
    "653d3615718cbd5c514210f8": {
        "en": "Printed souvenir photo from the onboard photo service on a dinner table",
        "fr": "Photo souvenir imprimée par le service photo à bord, posée sur la table du dîner",
        "de": "Ausgedrucktes Erinnerungsfoto des Bordfotoservices auf dem Dinnertisch",
        "es": "Foto de recuerdo impresa por el servicio de fotografía a bordo sobre la mesa de la cena",
        "it": "Foto ricordo stampata dal servizio fotografico a bordo sul tavolo della cena",
        "nl": "Afgedrukte souvenirfoto van de fotoservice aan boord op de dinertafel",
        "pl": "Wydrukowane zdjęcie z pokładowego serwisu fotograficznego na stole podczas kolacji",
        "ro": "Fotografie suvenir tipărită de serviciul foto de la bord, pe masa de cină",
        "ja": "船内の写真サービスで撮影・印刷された記念写真（ディナーテーブルの上）",
    },
    "653ba5d9f8b5205c6d7c39a0": {
        "en": "Smartphone photo of a guest at a window table on the Paris en Scène dinner cruise",
        "fr": "Photo prise au smartphone d'un convive à une table près de la fenêtre lors du dîner-croisière Paris en Scène",
        "de": "Smartphone-Foto eines Gastes an einem Fensterplatz bei der Paris-en-Scène-Dinnerfahrt",
        "es": "Foto con smartphone de un comensal en una mesa junto a la ventana en el crucero con cena Paris en Scène",
        "it": "Foto con lo smartphone di un ospite a un tavolo vicino al finestrino durante la crociera con cena Paris en Scène",
        "nl": "Smartphonefoto van een gast aan een tafel bij het raam tijdens de Paris en Scène-dinercruise",
        "pl": "Zdjęcie ze smartfona: gość przy stoliku przy oknie podczas rejsu z kolacją Paris en Scène",
        "ro": "Fotografie cu smartphone-ul a unui oaspete la o masă lângă fereastră, în croaziera cu cină Paris en Scène",
        "ja": "Paris en Scèneのディナークルーズで窓際の席に座るゲストのスマホ写真",
    },
    "655a3ae527bb0b39f6c997b5": {
        "en": "Birthday celebration with a sparkler candle on the Paris en Scène dinner cruise",
        "fr": "Anniversaire fêté avec une bougie scintillante lors du dîner-croisière Paris en Scène",
        "de": "Geburtstagsfeier mit Wunderkerze bei der Paris-en-Scène-Dinnerfahrt",
        "es": "Celebración de cumpleaños con una vela de bengala en el crucero con cena Paris en Scène",
        "it": "Festa di compleanno con una candela scintillante durante la crociera con cena Paris en Scène",
        "nl": "Verjaardagsviering met een sterretjeskaars tijdens de Paris en Scène-dinercruise",
        "pl": "Świętowanie urodzin z zimnym ogniem podczas rejsu z kolacją Paris en Scène",
        "ro": "Aniversare cu o lumânare-artificiu în croaziera cu cină Paris en Scène",
        "ja": "Paris en Scèneのディナークルーズでの花火キャンドル付きの誕生日のお祝い",
    },
    # Bateaux Mouches vs Bateaux Parisiens comparison
    "653d3629ae6bc593448d9b91": {
        "en": "Bateaux Parisiens dinner boat lit up at night near the Eiffel Tower",
        "fr": "Bateau du dîner-croisière Bateaux Parisiens illuminé de nuit près de la tour Eiffel",
        "de": "Dinnerschiff von Bateaux Parisiens nachts beleuchtet nahe dem Eiffelturm",
        "es": "Barco del crucero con cena de Bateaux Parisiens iluminado de noche cerca de la Torre Eiffel",
        "it": "Battello della crociera con cena Bateaux Parisiens illuminato di notte vicino alla Torre Eiffel",
        "nl": "Dinerboot van Bateaux Parisiens 's avonds verlicht bij de Eiffeltoren",
        "pl": "Statek Bateaux Parisiens na rejs z kolacją, oświetlony nocą w pobliżu wieży Eiffla",
        "ro": "Vasul de croazieră cu cină Bateaux Parisiens luminat noaptea, lângă Turnul Eiffel",
        "ja": "エッフェル塔の近くで夜にライトアップされたBateaux Parisiensのディナークルーズ船",
    },
    "67cd881b32f78191cfc0456a": {
        "en": "Welcome appetizers on the Bateaux Mouches dinner cruise",
        "fr": "Amuse-bouches de bienvenue lors du dîner-croisière Bateaux Mouches",
        "de": "Begrüßungshäppchen bei der Bateaux-Mouches-Dinnerfahrt",
        "es": "Aperitivos de bienvenida en el crucero con cena de Bateaux Mouches",
        "it": "Stuzzichini di benvenuto durante la crociera con cena Bateaux Mouches",
        "nl": "Welkomsthapjes tijdens de Bateaux Mouches-dinercruise",
        "pl": "Przekąski powitalne podczas rejsu z kolacją Bateaux Mouches",
        "ro": "Aperitive de bun venit în croaziera cu cină Bateaux Mouches",
        "ja": "Bateaux Mouchesのディナークルーズのウェルカムアミューズ",
    },
    "67cd882cfcd40d9948467d80": {
        "en": "Beef carpaccio starter on the Bateaux Mouches dinner cruise",
        "fr": "Carpaccio de bœuf en entrée lors du dîner-croisière Bateaux Mouches",
        "de": "Rindercarpaccio als Vorspeise bei der Bateaux-Mouches-Dinnerfahrt",
        "es": "Carpaccio de ternera de entrante en el crucero con cena de Bateaux Mouches",
        "it": "Carpaccio di manzo come antipasto durante la crociera con cena Bateaux Mouches",
        "nl": "Rundercarpaccio als voorgerecht tijdens de Bateaux Mouches-dinercruise",
        "pl": "Carpaccio wołowe jako przystawka podczas rejsu z kolacją Bateaux Mouches",
        "ro": "Carpaccio de vită ca antreu în croaziera cu cină Bateaux Mouches",
        "ja": "Bateaux Mouchesのディナークルーズの前菜、牛肉のカルパッチョ",
    },
    "67cd8839027b6113a595e065": {
        "en": "Sea bream main course on the Bateaux Mouches dinner cruise",
        "fr": "Dorade en plat principal lors du dîner-croisière Bateaux Mouches",
        "de": "Dorade als Hauptgang bei der Bateaux-Mouches-Dinnerfahrt",
        "es": "Dorada de plato principal en el crucero con cena de Bateaux Mouches",
        "it": "Orata come secondo durante la crociera con cena Bateaux Mouches",
        "nl": "Zeebrasem als hoofdgerecht tijdens de Bateaux Mouches-dinercruise",
        "pl": "Dorada jako danie główne podczas rejsu z kolacją Bateaux Mouches",
        "ro": "Doradă ca fel principal în croaziera cu cină Bateaux Mouches",
        "ja": "Bateaux Mouchesのディナークルーズのメイン、鯛料理",
    },
    "67cd88417f149b38ec65a082": {
        "en": "Profiterole dessert on the Bateaux Mouches dinner cruise",
        "fr": "Profiterole en dessert lors du dîner-croisière Bateaux Mouches",
        "de": "Profiterole als Dessert bei der Bateaux-Mouches-Dinnerfahrt",
        "es": "Profiterol de postre en el crucero con cena de Bateaux Mouches",
        "it": "Profiterole come dessert durante la crociera con cena Bateaux Mouches",
        "nl": "Profiterole als dessert tijdens de Bateaux Mouches-dinercruise",
        "pl": "Profiterolka na deser podczas rejsu z kolacją Bateaux Mouches",
        "ro": "Profiterol ca desert în croaziera cu cină Bateaux Mouches",
        "ja": "Bateaux Mouchesのディナークルーズのデザート、プロフィトロール",
    },
    "67cd886c08ea1ae1f6e1c1d9": {
        "en": "Bateaux Mouches dining room with waiters and a starry ceiling",
        "fr": "Salle à manger des Bateaux Mouches avec serveurs et plafond étoilé",
        "de": "Speisesaal von Bateaux Mouches mit Kellnern und Sternenhimmel-Decke",
        "es": "Comedor de Bateaux Mouches con camareros y techo estrellado",
        "it": "Sala da pranzo di Bateaux Mouches con camerieri e soffitto stellato",
        "nl": "Eetzaal van Bateaux Mouches met obers en een sterrenplafond",
        "pl": "Sala restauracyjna Bateaux Mouches z kelnerami i gwiaździstym sufitem",
        "ro": "Sala de mese Bateaux Mouches cu ospătari și tavan înstelat",
        "ja": "給仕スタッフと星空のような天井があるBateaux Mouchesのダイニングルーム",
    },
}

IMG = re.compile(r"<img\b[^>]*>")
HAS_ALT = re.compile(r"""\balt=(["'])\s*[^"'\s]""")
EMPTY_ALT = re.compile(r"""\salt=(["'])\s*\1""")
SKIP_DIRS = {".git", "node_modules", "scripts", "reports", "articles", "test", ".agents", "credentials", "assets", "i18n"}


def esc(s):
    return s.replace("&", "&amp;").replace('"', "&quot;")


def alt_for(tag, lang):
    if HAS_ALT.search(tag):
        return None
    src = (re.search(r'src="([^"]*)"', tag) or [None, ""])[1]
    if "facebook.com/tr" in src:
        return "" if " alt=" not in tag else None
    if "bpa-rev-icon" in tag:
        return ICONS.get(hashlib.md5(src.encode()).hexdigest()[:8])
    m = re.search(r"/([0-9a-f]{24})_", src)
    if not m:
        return None
    aid = m.group(1)
    if aid in PHOTOS:
        return PHOTOS[aid].get(lang, PHOTOS[aid]["en"])
    if aid in LOGOS:
        return LOGOS[aid]
    return None


def set_alt(tag, alt):
    if EMPTY_ALT.search(tag):
        return EMPTY_ALT.sub(f' alt="{esc(alt)}"', tag, count=1)
    return tag.replace("<img", f'<img alt="{esc(alt)}"', 1)


def main():
    changed_files = changed_imgs = 0
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        if "index.html" not in files:
            continue
        p = os.path.join(dirpath, "index.html")
        rel = os.path.relpath(p, ROOT)
        lang = rel.split(os.sep)[0] if rel.split(os.sep)[0] in LANGS else "en"
        html = open(p, encoding="utf-8").read()
        n = 0

        def repl(m):
            nonlocal n
            tag = m.group(0)
            alt = alt_for(tag, lang)
            if alt is None:
                return tag
            new = set_alt(tag, alt)
            n += new != tag
            return new
        # never touch <img> markup inside <script> (JS strings use escaped quotes)
        parts = re.split(r"(<script\b.*?</script>)", html, flags=re.S | re.I)
        new = "".join(part if part.lower().startswith("<script") else IMG.sub(repl, part) for part in parts)
        if new != html:
            open(p, "w", encoding="utf-8").write(new)
            changed_files += 1
            changed_imgs += n
    print(f"{changed_imgs} images updated in {changed_files} files")


if __name__ == "__main__":
    main()
