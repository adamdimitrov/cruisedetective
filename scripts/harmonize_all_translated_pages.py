#!/usr/bin/env python3
"""
MASTER TRANSLATION HARMONIZATION ENGINE — THE CRUISE DETECTIVE
Synchronizes all 8 translated editions (FR, DE, ES, IT, JA, NL, PL, RO)
with the English Luxury Editorial Design System:
- Canonical ltt-navbar with localized links and drawer
- Luxury editorial CSS & Open Sans / Plus Jakarta Sans fonts
- Universal 9999px circular pill buttons with signature gold gradient
- Suppression of Webflow badges
- Modern Luxury Homepage, About, Contact, and Duel architectures
- Preserves 100% of authentic localized translations and affiliate tracking
"""

import os
import re
import glob
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

LANGS = ['fr', 'de', 'es', 'it', 'ja', 'nl', 'pl', 'ro']

def classify_path(path):
    p = path.lower()
    parts = p.split('/')
    if len(parts) == 2 and parts[1] == 'index.html':
        return 'home'
    if any(k in p for k in ['mouches', 'parisiens', 'vergleich', 'lado-a-lado', 'confronto', '並べて比較', 'zij-aan-zij', 'kolacj', 'alăturată']):
        return 'duel'
    if any(k in p for k in ['diner', 'dinner', 'cena', 'abendessen', 'ディナー', 'ディナ-クル-ズ', 'obiadem', 'cină']):
        if any(k in p for k in ['seine', 'paris', 'senna', 'paryz', 'セーヌ', 'セ-ヌ', 'senine']):
            return 'paris_dinner'
    if any(k in p for k in ['seine', 'sena', 'senna', 'sekwanie', 'senine', 'セーヌ', 'セ-ヌ']):
        if any(k in p for k in ['deal', 'review', '-1']):
            return 'seine_sub'
        return 'paris_sightseeing'
    if any(k in p for k in ['amsterdam', 'canal', 'grachten', 'kanał', '運河']):
        return 'amsterdam'
    if any(k in p for k in ['london', 'tamise', 'themse', 'tamesis', 'tamigi', 'londres', 'londra', 'londyn', 'テムズ', 'tamisie', 'tamisa']):
        return 'london'
    if any(k in p for k in ['a-propos', 'uber-uns', 'acerca', 'su-di-noi', 'について', 'over-uns', '/o/', 'despre']):
        return 'about'
    if any(k in p for k in ['contact', 'kontakt', 'contacto', 'contatto', '接触']):
        return 'contact'
    if 'privacy' in p:
        return 'privacy'
    if 'terms' in p:
        return 'terms'
    return 'other'

def build_page_mappings():
    mappings = {}
    for lang in LANGS:
        mappings[lang] = {}
        files = glob.glob(os.path.join(BASE_DIR, f'{lang}/**/*.html'), recursive=True)
        for f in files:
            rel = os.path.relpath(f, BASE_DIR)
            c = classify_path(rel)
            if c not in mappings[lang] or c == 'home':
                mappings[lang][c] = '/' + rel.replace('/index.html', '')
                if mappings[lang][c] == f'/{lang}':
                    mappings[lang][c] = f'/{lang}/'
    return mappings

# Comprehensive Language Dictionary
I18N = {
    'fr': {
        'brand': 'THE CRUISE DETECTIVE',
        'destinations': 'Destinations',
        'seine_heading': 'SEINE À PARIS',
        'paris_dinner': 'Croisières Dîner Paris',
        'paris_dinner_sub': '10 bateaux testés et avis dégustation',
        'paris_sightseeing': 'Croisières Promenade Paris',
        'paris_sightseeing_sub': 'Visites de jour et illuminations nocturnes',
        'duel': 'Mouches vs. Parisiens',
        'duel_sub': 'Comparatif face-à-face des dîners-croisières',
        'waterways_heading': 'VOIES NAVIGABLES EUROPÉENNES',
        'amsterdam': 'Croisières Canaux Amsterdam',
        'amsterdam_sub': 'Barques ouvertes et bateaux salon classiques',
        'london': 'Croisières Tamise Londres',
        'london_sub': 'Visites guidées, dîners et bateaux rapides',
        'top_dinner': 'Croisières Dîner',
        'top_sightseeing': 'Croisières Promenade',
        'about': 'À Propos',
        'contact': 'Contact',
        'drawer_destinations': 'Destinations & Guides',
        'drawer_editorial': 'Éditorial & Contact',
        'top_pick': 'CHOIX #1',
        # Home
        'home_eyebrow': '🕵️ AUDIT INCOGNITO DE CROISIÈRES FLUVIALES • ÉDITION ÉDITORIALE 2026',
        'home_title': 'Avis indépendants et testés sur le terrain sur les croisières fluviales pour',
        'home_title_gold': 'voyageurs exigeants.',
        'home_subtitle': 'Nous payons nos propres billets, réservons nos tables incognito, goûtons chaque plat et évaluons les angles de vue aux heures de départ en soirée. Zéro billet sponsorisé, zéro blabla promotionnel : uniquement des faits vérifiés, des photos originales et une critique authentique.',
        'stat_1_num': '100%', 'stat_1_label': 'Réservations Anonymes', 'stat_1_sub': 'Payées de notre poche',
        'stat_2_num': '40+', 'stat_2_label': 'Croisières Évaluées', 'stat_2_sub': 'Paris • Amsterdam • Londres',
        'stat_3_num': 'Zéro', 'stat_3_label': 'Cadeaux Sponsorisés', 'stat_3_sub': '100% Sans compromis',
        'stat_4_num': '4', 'stat_4_label': 'Capitales Fluviales', 'stat_4_sub': 'Eaux d\'Europe de l\'Ouest',
        'flagship_eyebrow': 'GUIDES DE RÉFÉRENCE',
        'flagship_title': 'Nos Guides Testés sur l\'Eau',
        'flagship_sub': 'Chaque guide est mis à jour chaque mois avec les prix réels, les plans d\'embarquement et nos photos de table.',
        'btn_read_guide': 'Lire le guide complet →',
        'btn_compare': 'Comparer le duel →',
        'manifesto_eyebrow': 'NOTRE MÉTHODOLOGIE SOUS COUVERTURE',
        'manifesto_title': 'Pourquoi Faire Confiance au Cruise Detective ?',
        'manifesto_sub': 'La plupart des guides de voyage recopient les brochures d\'agences. Nous montons à bord incognito.',
        'man_1_title': '100% Auto-Financé & Incognito',
        'man_1_text': 'Nous ne demandons ni n\'acceptons jamais de billets de presse, de repas offerts ou de traitement de faveur. Nous faisons la queue avec les voyageurs réguliers et payons plein tarif.',
        'man_2_title': 'Zéro Biais Publicitaire',
        'man_2_text': 'Nos classements ne sont pas à vendre. Si une compagnie sert des plats surgelés ou entasse les passagers, nous l\'écrivons sans filtre.',
        'man_3_title': 'Logistique Terrain Vérifiée',
        'man_3_text': 'Coordonnées GPS précises des quais d\'embarquement, stations de métro les plus proches, politiques de placement côté fenêtre et astuces coupe-file.',
        'author_eyebrow': 'DÉTECTIVE EN CHEF & FONDATEUR',
        'author_name': 'Adam Dimitrov',
        'author_role': 'Fondateur & Rédacteur en Chef',
        'author_bio': 'Adam Dimitrov a fondé The Cruise Detective après des années passées à voyager sur les fleuves d\'Europe. Fatigué des avis génériques et des pièges à touristes en ligne, il a créé cette publication pour offrir aux voyageurs une transparence totale sur l\'expérience réelle à bord.',
        'author_link': 'En savoir plus sur notre méthodologie →',
        # Footer
        'footer_desc': 'TheCruiseDetective.com est votre guide indépendant et testé sur le terrain pour choisir les meilleures croisières fluviales et dîners-croisières en Europe.',
        'footer_guides_head': 'Guides de Référence',
        'footer_company_head': 'Société & Confiance',
        'footer_privacy': 'Politique de confidentialité',
        'footer_terms': 'Conditions d\'utilisation',
    },
    'de': {
        'brand': 'THE CRUISE DETECTIVE',
        'destinations': 'Reiseziele',
        'seine_heading': 'SEINE IN PARIS',
        'paris_dinner': 'Dinner-Kreuzfahrten Paris',
        'paris_dinner_sub': '10 getestete Schiffe & Menü-Bewertungen',
        'paris_sightseeing': 'Sightseeing-Bootsfahrten Paris',
        'paris_sightseeing_sub': 'Tagesfahrten & Lichtertouren am Abend',
        'duel': 'Mouches vs. Parisiens',
        'duel_sub': 'Direkter Dinner-Kreuzfahrt-Vergleich',
        'waterways_heading': 'EUROPÄISCHE WASSERWEGE',
        'amsterdam': 'Grachtenfahrten Amsterdam',
        'amsterdam_sub': 'Offene Schaluppen & Salonboote',
        'london': 'Themse-Kreuzfahrten London',
        'london_sub': 'Sightseeing, Dinner & Speedboote',
        'top_dinner': 'Dinner-Kreuzfahrten',
        'top_sightseeing': 'Sightseeing-Fahrten',
        'about': 'Über Uns',
        'contact': 'Kontakt',
        'drawer_destinations': 'Reiseziele & Guides',
        'drawer_editorial': 'Redaktion & Kontakt',
        'top_pick': 'TOP-TIPP',
        # Home
        'home_eyebrow': '🕵️ VERDECKTE FLUSSKREUZFAHRT-PRÜFUNGEN • REDAKTIONSAUSGABE 2026',
        'home_title': 'Unabhängige, praxisgetestete Flusskreuzfahrt-Bewertungen für',
        'home_title_gold': 'anspruchsvolle Reisende.',
        'home_subtitle': 'Wir zahlen unsere Tickets selbst, reservieren Tische anonym, testen jedes Menü und prüfen die Aussicht bei Abfahrt am Abend. Keine gesponserten Freikarten, kein Werbegeplänkel – nur verifizierte Fakten, echte Fotos und ehrliche Kritik.',
        'stat_1_num': '100%', 'stat_1_label': 'Anonyme Buchungen', 'stat_1_sub': 'Aus eigener Tasche bezahlt',
        'stat_2_num': '40+', 'stat_2_label': 'Getestete Fahrten', 'stat_2_sub': 'Paris • Amsterdam • London',
        'stat_3_num': 'Null', 'stat_3_label': 'Sponsoring-Geschenke', 'stat_3_sub': '100% Unbestechlich',
        'stat_4_num': '4', 'stat_4_label': 'Flussmetropolen', 'stat_4_sub': 'Westeuropäische Gewässer',
        'flagship_eyebrow': 'FLAGGSCHIFF-GUIDES',
        'flagship_title': 'Unsere Praxiserprobten Guides',
        'flagship_sub': 'Jeder Guide wird monatlich mit aktuellen Ticketpreisen, Anlegestellen und eigenen Fotos aktualisiert.',
        'btn_read_guide': 'Vollständigen Guide lesen →',
        'btn_compare': 'Zum Schiffsvergleich →',
        'manifesto_eyebrow': 'UNSERE TEST-METHODIK',
        'manifesto_title': 'Warum Sie The Cruise Detective vertrauen können',
        'manifesto_sub': 'Andere Seiten kopieren Werbeprospekte. Wir gehen verdeckt an Bord und dokumentieren die Realität.',
        'man_1_title': '100% Selbst Finanziert & Anonym',
        'man_1_text': 'Wir akzeptieren niemals Freitickets, Pressereisen oder Sonderbehandlungen. Wir stehen wie alle Gäste in der Schlange und zahlen reguläre Preise.',
        'man_2_title': 'Kein Werbeeinfluss',
        'man_2_text': 'Unsere Bewertungen sind nicht käuflich. Wenn ein Schiff Tiefkühlkost serviert oder Tische überfüllt, benennen wir das ungeschminkt.',
        'man_3_title': 'Geprüfte Praxis-Logistik',
        'man_3_text': 'Genaue GPS-Daten der Schiffsanleger, nahegelegene U-Bahn-Stationen, Fensterplatz-Garantien und Zeitspar-Tipps.',
        'author_eyebrow': 'CHEF-ERMITTLER & GRÜNDER',
        'author_name': 'Adam Dimitrov',
        'author_role': 'Gründer & Chefredakteur',
        'author_bio': 'Adam Dimitrov gründete The Cruise Detective, um Reisenden schonungslose Transparenz bei europäischen Schifffahrten zu bieten. Nach zahllosen Fahrten deckt er die besten Plätze und Fallen verlässlich auf.',
        'author_link': 'Mehr über unsere Testkriterien erfahren →',
        # Footer
        'footer_desc': 'TheCruiseDetective.com ist Ihr unabhängiger, praxisgetesteter Ratgeber für die besten Fluss-, Grachten- und Dinner-Kreuzfahrten in Europa.',
        'footer_guides_head': 'Beliebte Guides',
        'footer_company_head': 'Unternehmen & Vertrauen',
        'footer_privacy': 'Datenschutzrichtlinie',
        'footer_terms': 'Nutzungsbedingungen',
    },
    'es': {
        'brand': 'THE CRUISE DETECTIVE',
        'destinations': 'Destinos',
        'seine_heading': 'RÍO SENA EN PARÍS',
        'paris_dinner': 'Cruceros con Cena en París',
        'paris_dinner_sub': '10 barcos probados y notas de cata',
        'paris_sightseeing': 'Cruceros Paseo en París',
        'paris_sightseeing_sub': 'Paseos de día e iluminaciones nocturnas',
        'duel': 'Mouches vs. Parisiens',
        'duel_sub': 'Comparativa cara a cara con cena',
        'waterways_heading': 'RUTAS FLUVIALES EUROPEAS',
        'amsterdam': 'Cruceros Canales Ámsterdam',
        'amsterdam_sub': 'Lanchas abiertas y barcos clásicos',
        'london': 'Cruceros Támesis Londres',
        'london_sub': 'Vistas panorámicas, cenas y lanchas rápidas',
        'top_dinner': 'Cruceros con Cena',
        'top_sightseeing': 'Paseos en Barco',
        'about': 'Acerca de',
        'contact': 'Contacto',
        'drawer_destinations': 'Destinos y Guías',
        'drawer_editorial': 'Editorial y Contacto',
        'top_pick': 'ELECCIÓN #1',
        # Home
        'home_eyebrow': '🕵️ AUDITORÍA ENCUBIERTA DE CRUCEROS FLUVIALES • EDICIÓN EDITORIAL 2026',
        'home_title': 'Reseñas independientes y probadas sobre el terreno para',
        'home_title_gold': 'viajeros exigentes.',
        'home_subtitle': 'Pagamos nuestros propios billetes, reservamos mesas de incógnito, probamos cada plato y evaluamos las vistas según los horarios nocturnos. Cero billetes patrocinados, cero adornos promocionales: solo datos verificados, fotos originales y crítica honesta.',
        'stat_1_num': '100%', 'stat_1_label': 'Reservas Anónimas', 'stat_1_sub': 'Pagadas de nuestro bolsillo',
        'stat_2_num': '40+', 'stat_2_label': 'Cruceros Auditados', 'stat_2_sub': 'París • Ámsterdam • Londres',
        'stat_3_num': 'Cero', 'stat_3_label': 'Viajes Patrocinados', 'stat_3_sub': '100% Sin compromisos',
        'stat_4_num': '4', 'stat_4_label': 'Capitales Fluviales', 'stat_4_sub': 'Aguas de Europa Occidental',
        'flagship_eyebrow': 'GUÍAS PRINCIPALES',
        'flagship_title': 'Nuestras Guías Probadas en el Agua',
        'flagship_sub': 'Cada guía se actualiza mensualmente con precios reales, muelles de embarque y fotos propias.',
        'btn_read_guide': 'Leer guía completa →',
        'btn_compare': 'Ver comparativa →',
        'manifesto_eyebrow': 'NUESTRA METODOLOGÍA ENCUBIERTA',
        'manifesto_title': '¿Por Qué Confiar en The Cruise Detective?',
        'manifesto_sub': 'La mayoría de los sitios copian folletos de agencias. Nosotros subimos a bordo de incógnito.',
        'man_1_title': '100% Autofinanciado y de Incógnito',
        'man_1_text': 'Nunca aceptamos billetes de prensa, comidas gratis ni favores. Hacemos cola como cualquier viajero y pagamos tarifa completa.',
        'man_2_title': 'Sin Sesgo Publicitario',
        'man_2_text': 'Nuestras recomendaciones no se venden. Si un barco sirve comida congelada o hacina las mesas, lo decimos claramente.',
        'man_3_title': 'Logística Verificada',
        'man_3_text': 'Ubicación exacta de los muelles, estaciones de metro cercanas, políticas de mesas junto a la ventana y consejos prácticos.',
        'author_eyebrow': 'DETECTIVE JEFE Y FUNDADOR',
        'author_name': 'Adam Dimitrov',
        'author_role': 'Fundador y Editor Jefe',
        'author_bio': 'Adam Dimitrov fundó The Cruise Detective para brindar total transparencia a los cruceros fluviales europeos tras experimentar incontables trampas turísticas.',
        'author_link': 'Conoce más sobre nuestra metodología →',
        # Footer
        'footer_desc': 'TheCruiseDetective.com es su guía independiente y probada sobre el terreno para elegir los mejores cruceros fluviales, por canales y con cena en Europa.',
        'footer_guides_head': 'Guías Populares',
        'footer_company_head': 'Compañía y Confianza',
        'footer_privacy': 'Política de Privacidad',
        'footer_terms': 'Términos de Servicio',
    },
    'it': {
        'brand': 'THE CRUISE DETECTIVE',
        'destinations': 'Destinazioni',
        'seine_heading': 'FIUME SENNA A PARIGI',
        'paris_dinner': 'Crociere con Cena a Parigi',
        'paris_dinner_sub': '10 battelli provati e note di degustazione',
        'paris_sightseeing': 'Crociere Panoramiche a Parigi',
        'paris_sightseeing_sub': 'Tour diurni e illuminazioni serali',
        'duel': 'Mouches vs. Parisiens',
        'duel_sub': 'Confronto diretto cene in battello',
        'waterways_heading': 'VIE D\'ACQUA EUROPEE',
        'amsterdam': 'Crociere Canali Amsterdam',
        'amsterdam_sub': 'Barche aperte e battelli d\'epoca',
        'london': 'Crociere Tamigi Londra',
        'london_sub': 'Giri turistici, cene e motoscafi',
        'top_dinner': 'Crociere con Cena',
        'top_sightseeing': 'Crociere Panoramiche',
        'about': 'Su di noi',
        'contact': 'Contatto',
        'drawer_destinations': 'Destinazioni e Guide',
        'drawer_editorial': 'Editoriale e Contatto',
        'top_pick': 'SCELTA #1',
        # Home
        'home_eyebrow': '🕵️ AUDIT INCOGNITO DELLE CROCIERE FLUVIALI • EDIZIONE EDITORIALE 2026',
        'home_title': 'Recensioni indipendenti e testate sul campo per',
        'home_title_gold': 'viaggiatori esigenti.',
        'home_subtitle': 'Paghiamo noi stessi i biglietti, prenotiamo i tavoli in incognito, assaggiamo ogni portata e valutiamo la visuale agli orari serali di partenza. Zero biglietti sponsorizzati, zero chiacchiere promozionali: solo fatti verificati, foto originali e critiche sincere.',
        'stat_1_num': '100%', 'stat_1_label': 'Prenotazioni Anonime', 'stat_1_sub': 'Pagate di tasca nostra',
        'stat_2_num': '40+', 'stat_2_label': 'Crociere Esaminate', 'stat_2_sub': 'Parigi • Amsterdam • Londra',
        'stat_3_num': 'Zero', 'stat_3_label': 'Regali Sponsorizzati', 'stat_3_sub': '100% Incorruttibili',
        'stat_4_num': '4', 'stat_4_label': 'Capitali Fluviali', 'stat_4_sub': 'Acque dell\'Europa Occidentale',
        'flagship_eyebrow': 'GUIDE PRINCIPALI',
        'flagship_title': 'Le Nostre Guide Provate sull\'Acqua',
        'flagship_sub': 'Ogni guida viene aggiornata mensilmente con tariffe reali, moli d\'imbarco e foto scattate a bordo.',
        'btn_read_guide': 'Leggi la guida completa →',
        'btn_compare': 'Confronta i battelli →',
        'manifesto_eyebrow': 'IL NOSTRO METODO INCOGNITO',
        'manifesto_title': 'Perché Fidarsi di The Cruise Detective?',
        'manifesto_sub': 'Gli altri siti copiano i dépliant promozionali. Noi saliamo a bordo in incognito.',
        'man_1_title': '100% Autofinanziato e Anonimo',
        'man_1_text': 'Non accettiamo mai biglietti omaggio per la stampa o trattamenti speciali. Facciamo la fila come tutti i viaggiatori e paghiamo la tariffa intera.',
        'man_2_title': 'Zero Condizionamento',
        'man_2_text': 'I nostri giudizi non sono in vendita. Se una compagnia serve cibo surgelato o ammassa i tavoli, lo scriviamo apertamente.',
        'man_3_title': 'Logistica Verificata',
        'man_3_text': 'Coordinate GPS precise dei moli, stazioni metro più comode, regole sui tavoli vicino al finestrino e consigli operativi.',
        'author_eyebrow': 'INVESTIGATORE CAPO & FONDATORE',
        'author_name': 'Adam Dimitrov',
        'author_role': 'Fondatore e Direttore Editoriale',
        'author_bio': 'Adam Dimitrov ha fondato The Cruise Detective per offrire ai viaggiatori una trasparenza assoluta sulle crociere fluviali europee, senza filtri commerciali.',
        'author_link': 'Scopri i nostri criteri di valutazione →',
        # Footer
        'footer_desc': 'TheCruiseDetective.com è la tua guida indipendente e testata sul campo per scegliere le migliori crociere fluviali, sui canali e con cena in Europa.',
        'footer_guides_head': 'Guide Popolari',
        'footer_company_head': 'Azienda e Fiducia',
        'footer_privacy': 'Informativa sulla Privacy',
        'footer_terms': 'Termini di Servizio',
    },
    'ja': {
        'brand': 'THE CRUISE DETECTIVE',
        'destinations': '就航都市',
        'seine_heading': 'パリ・セーヌ川',
        'paris_dinner': 'パリ ディナークルーズ',
        'paris_dinner_sub': '実地検証済みの厳選船＆ディナー',
        'paris_sightseeing': 'パリ 観光クルーズ',
        'paris_sightseeing_sub': '昼夜の遊覧船・夜景イルミネーション',
        'duel': 'ムーシュ vs パリジャン',
        'duel_sub': '定番2大ディナークルーズ徹底比較',
        'waterways_heading': 'ヨーロッパの主要水路',
        'amsterdam': 'アムステルダム運河クルーズ',
        'amsterdam_sub': 'オープンボート＆クラシックサロン船',
        'london': 'ロンドン テムズ川クルーズ',
        'london_sub': '観光遊覧、ディナー＆スピードボート',
        'top_dinner': 'ディナークルーズ',
        'top_sightseeing': '観光クルーズ',
        'about': '当サイトについて',
        'contact': 'お問い合わせ',
        'drawer_destinations': '目的地とガイド',
        'drawer_editorial': '編集部・お問い合わせ',
        'top_pick': 'おすすめ #1',
        # Home
        'home_eyebrow': '🕵️ 現地覆面調査によるリバークルーズ検証 • 2026年 編集部決定版',
        'home_title': '妥協のない旅人のための、',
        'home_title_gold': '実地検証済み独立系リバークルーズガイド。',
        'home_subtitle': '私たちは自費で乗船チケットを購入し、覆面で窓際や中央席を予約して全コースを試食。夜間出航時の夜景の見え方を徹底検証しています。企業案件・PR案件は一切なし。検証済みの事実、オリジナル写真、本音の批評のみをお届けします。',
        'stat_1_num': '100%', 'stat_1_label': '完全覆面調査', 'stat_1_sub': '自費購入チケット',
        'stat_2_num': '40+', 'stat_2_label': '検証済みクルーズ', 'stat_2_sub': 'パリ • アムステルダム • ロンドン',
        'stat_3_num': 'ゼロ', 'stat_3_label': '企業PR・提供案件', 'stat_3_sub': '妥協なき中立性',
        'stat_4_num': '4', 'stat_4_label': '主要都市水路', 'stat_4_sub': '西ヨーロッパ主要河川',
        'flagship_eyebrow': '主力ガイド',
        'flagship_title': '水上で実地検証した厳選ガイド',
        'flagship_sub': '毎月最新の運賃、乗り場案内、実際の乗船写真で更新されています。',
        'btn_read_guide': 'ガイドを読む →',
        'btn_compare': '比較を見る →',
        'manifesto_eyebrow': '覆面調査の原則',
        'manifesto_title': 'なぜ The Cruise Detective が選ばれるのか？',
        'manifesto_sub': 'パンフレットを転記する一般的な旅行サイトとは異なり、私たちは現地で直接検証します。',
        'man_1_title': '100% 自費での覆面調査',
        'man_1_text': 'プレス用招待券や食事の無償提供は一切受け取りません。一般の乗客と同じ列に並び、通常料金を支払って乗船します。',
        'man_2_title': '広告に左右されない評価',
        'man_2_text': '評価の売買は行いません。冷凍食品が提供されていたり、座席が過密である場合は、率直にありのままをレポートします。',
        'man_3_title': '検証済みの現地アクセス',
        'man_3_text': '正確な乗り場GPS、最寄り駅、窓際席の確約条件など、失敗しないための実用的な情報を提供します。',
        'author_eyebrow': '創設者 兼 主任調査員',
        'author_name': 'Adam Dimitrov',
        'author_role': '創設者 兼 編集長',
        'author_bio': 'ヨーロッパ各国のリバークルーズにおける観光客向け誇大広告に問題意識を持ち、旅行者が後悔しないための完全中立な検証メディアとして The Cruise Detective を立ち上げました。',
        'author_link': '検証ポリシーの詳細を見る →',
        # Footer
        'footer_desc': 'TheCruiseDetective.com は、ヨーロッパ各地のリバークルーズ、運河クルーズ、ディナークルーズを現地で実地検証した独立系ガイドです。',
        'footer_guides_head': '人気ガイド',
        'footer_company_head': '運営情報と信頼性',
        'footer_privacy': 'プライバシーポリシー',
        'footer_terms': '利用規約',
    },
    'nl': {
        'brand': 'THE CRUISE DETECTIVE',
        'destinations': 'Bestemmingen',
        'seine_heading': 'SEINE IN PARIJS',
        'paris_dinner': 'Dinercruises Parijs',
        'paris_dinner_sub': '10 geteste schepen & proeverijnotities',
        'paris_sightseeing': 'Rondvaarten Parijs',
        'paris_sightseeing_sub': 'Dagtochten & avondverlichting',
        'duel': 'Mouches vs. Parisiens',
        'duel_sub': 'Directe vergelijking van dinercruises',
        'waterways_heading': 'EUROPESE WATERWEGEN',
        'amsterdam': 'Grachtenrondvaarten Amsterdam',
        'amsterdam_sub': 'Open sloepen & klassieke salonboten',
        'london': 'Theems Rondvaarten Londen',
        'london_sub': 'Sightseeing, dineren & speedboten',
        'top_dinner': 'Dinercruises',
        'top_sightseeing': 'Rondvaarten',
        'about': 'Over Ons',
        'contact': 'Contact',
        'drawer_destinations': 'Bestemmingen & Gidsen',
        'drawer_editorial': 'Redactie & Contact',
        'top_pick': 'TOP KEUZE',
        # Home
        'home_eyebrow': '🕵️ ONDERDEKKEN RIVIERCRUISE AUDITS • REDACTIONELE EDITIE 2026',
        'home_title': 'Onafhankelijke, in de praktijk geteste riviercruisereviews voor',
        'home_title_gold': 'kritische reizigers.',
        'home_subtitle': 'We betalen onze eigen tickets, reserveren anoniem, proeven elk gerecht en beoordelen het uitzicht bij vertrek in de avond. Geen gesponsorde tickets, geen marketingpraatjes – alleen geverifieerde feiten, echte foto\'s en eerlijke kritiek.',
        'stat_1_num': '100%', 'stat_1_label': 'Anonieme Boekingen', 'stat_1_sub': 'Zelf betaald',
        'stat_2_num': '40+', 'stat_2_label': 'Gecontroleerde Cruises', 'stat_2_sub': 'Parijs • Amsterdam • Londen',
        'stat_3_num': 'Geen', 'stat_3_label': 'Gesponsorde Trips', 'stat_3_sub': '100% Onafhankelijk',
        'stat_4_num': '4', 'stat_4_label': 'Waterhoofdsteden', 'stat_4_sub': 'West-Europese wateren',
        'flagship_eyebrow': 'BELANGRIJKSTE GIDSEN',
        'flagship_title': 'Onze Gidsen, Getest op het Water',
        'flagship_sub': 'Elke gids wordt maandelijks bijgewerkt met actuele ticketprijzen, opstapplaatsen en eigen foto\'s.',
        'btn_read_guide': 'Lees volledige gids →',
        'btn_compare': 'Vergelijk cruises →',
        'manifesto_eyebrow': 'ONZE ONAFHANKELIJKE METHODE',
        'manifesto_title': 'Waarom The Cruise Detective Vertrouwen?',
        'manifesto_sub': 'Andere platforms kopiëren brochures van touroperators. Wij stappen anoniem aan boord.',
        'man_1_title': '100% Zelfbekostigd & Anoniem',
        'man_1_text': 'We accepteren nooit gratis tickets, persreizen of voorkeursbehandelingen. We staan gewoon in de rij en betalen het reguliere tarief.',
        'man_2_title': 'Geen Advertentiebeïnvloeding',
        'man_2_text': 'Onze beoordelingen zijn niet te koop. Als een rederij diepvriesmaaltijden serveert of tafels op elkaar propt, schrijven we dat duidelijk op.',
        'man_3_title': 'Geverifieerde Logistiek',
        'man_3_text': 'Exacte GPS-locaties van pieren, dichtstbijzijnde metrostations, raamplaatsgaranties en praktische tips.',
        'author_eyebrow': 'HOOFDDETECTIVE & OPRICHTER',
        'author_name': 'Adam Dimitrov',
        'author_role': 'Oprichter & Hoofdredacteur',
        'author_bio': 'Adam Dimitrov richtte The Cruise Detective op om reizigers te voorzien van eerlijke transparantie op Europese rivieren, zonder commerciële opsmuk.',
        'author_link': 'Lees meer over onze werkwijze →',
        # Footer
        'footer_desc': 'TheCruiseDetective.com is uw onafhankelijke, in de praktijk geteste gids voor de beste rivier-, grachten- en dinercruises in Europa.',
        'footer_guides_head': 'Populaire Gidsen',
        'footer_company_head': 'Bedrijf & Vertrouwen',
        'footer_privacy': 'Privacybeleid',
        'footer_terms': 'Algemene Voorwaarden',
    },
    'pl': {
        'brand': 'THE CRUISE DETECTIVE',
        'destinations': 'Kierunki',
        'seine_heading': 'SEKWANA W PARYŻU',
        'paris_dinner': 'Rejsy z kolacją w Paryżu',
        'paris_dinner_sub': '10 przetestowanych statków i opinie o menu',
        'paris_sightseeing': 'Rejsy widokowe po Sekwanie',
        'paris_sightseeing_sub': 'Rejsy dzienne i iluminacje nocne',
        'duel': 'Mouches vs. Parisiens',
        'duel_sub': 'Bezpośrednie porównanie rejsów z kolacją',
        'waterways_heading': 'EUROPEJSKIE SZLAKI WODNE',
        'amsterdam': 'Rejsy kanałami Amsterdamu',
        'amsterdam_sub': 'Otwarte łodzie i klasyczne salony',
        'london': 'Rejsy po Tamizie w Londynie',
        'london_sub': 'Rejsy turystyczne, kolacje i motorówki',
        'top_dinner': 'Rejsy z kolacją',
        'top_sightseeing': 'Rejsy widokowe',
        'about': 'O nas',
        'contact': 'Kontakt',
        'drawer_destinations': 'Kierunki i przewodniki',
        'drawer_editorial': 'Redakcja i kontakt',
        'top_pick': 'WYBÓR #1',
        # Home
        'home_eyebrow': '🕵️ NIEZALEŻNY AUDYT REJSÓW RZECZNYCH • WYDANIE REDAKCYJNE 2026',
        'home_title': 'Niezależne, sprawdzone w terenie recenzje rejsów rzecznych dla',
        'home_title_gold': 'wymagających podróżników.',
        'home_subtitle': 'Płacimy za własne bilety, rezerwujemy stoliki incognito, próbujemy każdego dania i oceniamy widoki o wieczornych porach rejsu. Zero sponsorowanych wejściówek, zero marketingowych sloganów — tylko sprawdzone fakty, autorskie zdjęcia i szczere oceny.',
        'stat_1_num': '100%', 'stat_1_label': 'Anonimowe Rezerwacje', 'stat_1_sub': 'Płacone z własnej kieszeni',
        'stat_2_num': '40+', 'stat_2_label': 'Przetestowanych Rejsów', 'stat_2_sub': 'Paryż • Amsterdam • Londyn',
        'stat_3_num': 'Zero', 'stat_3_label': 'Sponsorowanych Wycieczek', 'stat_3_sub': '100% Niezależności',
        'stat_4_num': '4', 'stat_4_label': 'Rzeczne Stolice', 'stat_4_sub': 'Wody Europy Zachodniej',
        'flagship_eyebrow': 'GŁÓWNE PRZEWODNIKI',
        'flagship_title': 'Nasze Przewodniki Przetestowane na Wodzie',
        'flagship_sub': 'Każdy przewodnik aktualizujemy co miesiąc o aktualne ceny, przystanie i autorskie zdjęcia.',
        'btn_read_guide': 'Czytaj cały przewodnik →',
        'btn_compare': 'Zobacz porównanie →',
        'manifesto_eyebrow': 'NASZA METODOLOGIA AUDYTU',
        'manifesto_title': 'Dlaczego Warto Ufać The Cruise Detective?',
        'manifesto_sub': 'Inne strony kopiują broszury agencji turystycznych. My wchodzimy na pokład incognito.',
        'man_1_title': '100% Własne Finansowanie i Anonimowość',
        'man_1_text': 'Nigdy nie przyjmujemy darmowych wejściówek dla prasy ani specjalnego traktowania. Czekamy w kolejce z innymi pasażerami i płacimy pełną stawkę.',
        'man_2_title': 'Zero Wpływu Reklamodawców',
        'man_2_text': 'Nasze oceny nie są na sprzedaż. Jeśli armator serwuje mrożonki lub upycha stoliki, piszemy o tym wprost.',
        'man_3_title': 'Sprawdzona Logistyka',
        'man_3_text': 'Dokładne współrzędne przystani, najbliższe stacje metra, zasady przydziału stolików przy oknie i praktyczne wskazówki.',
        'author_eyebrow': 'GŁÓWNY DETEKTYW I ZAŁOŻYCIEL',
        'author_name': 'Adam Dimitrov',
        'author_role': 'Założyciel i Redaktor Naczelny',
        'author_bio': 'Adam Dimitrov założył The Cruise Detective, aby zapewnić podróżnym pełną przejrzystość na temat europejskich rejsów po latach demaskowania pułapek turystycznych.',
        'author_link': 'Poznaj naszą metodologię testów →',
        # Footer
        'footer_desc': 'TheCruiseDetective.com to Twój niezależny, sprawdzony w terenie przewodnik po najlepszych rejsach rzecznych, kanałowych i rejsach z kolacją w Europie.',
        'footer_guides_head': 'Popularne Przewodniki',
        'footer_company_head': 'Firma i Zaufanie',
        'footer_privacy': 'Polityka prywatności',
        'footer_terms': 'Regulamin',
    },
    'ro': {
        'brand': 'THE CRUISE DETECTIVE',
        'destinations': 'Destinații',
        'seine_heading': 'RÂUL SENA ÎN PARIS',
        'paris_dinner': 'Croaziere cu cină în Paris',
        'paris_dinner_sub': '10 nave testate și evaluări de meniu',
        'paris_sightseeing': 'Croaziere turistice pe Sena',
        'paris_sightseeing_sub': 'Tururi de zi și iluminat de seară',
        'duel': 'Mouches vs. Parisiens',
        'duel_sub': 'Comparație directă croaziere cu cină',
        'waterways_heading': 'CĂI NAVIGABILE EUROPENE',
        'amsterdam': 'Croaziere canale Amsterdam',
        'amsterdam_sub': 'Șalupe deschise și ambarcațiuni salon',
        'london': 'Croaziere pe Tamisa la Londra',
        'london_sub': 'Tururi de vizitare, cine și bărci rapide',
        'top_dinner': 'Croaziere cu cină',
        'top_sightseeing': 'Croaziere panoramice',
        'about': 'Despre noi',
        'contact': 'Contact',
        'drawer_destinations': 'Destinații și Ghiduri',
        'drawer_editorial': 'Redacție și Contact',
        'top_pick': 'RECOMANDARE #1',
        # Home
        'home_eyebrow': '🕵️ AUDIT SUB ACOPERIRE AL CROAZIERELOR FLUVIALE • EDIȚIA EDITORIALĂ 2026',
        'home_title': 'Recenzii independente și testate pe teren ale croazierelor fluviale pentru',
        'home_title_gold': 'călători exigenți.',
        'home_subtitle': 'Ne plătim propriile bilete, rezervăm mese sub acoperire, gustăm fiecare fel de mâncare și evaluăm unghiurile de vizualizare la orele de plecare de seară. Zero bilete sponsorizate, zero laude promoționale — doar fapte verificate, fotografii originale și critici sincere.',
        'stat_1_num': '100%', 'stat_1_label': 'Rezervări Anonime', 'stat_1_sub': 'Plătite din buzunarul propriu',
        'stat_2_num': '40+', 'stat_2_label': 'Croaziere Evaluate', 'stat_2_sub': 'Paris • Amsterdam • Londra',
        'stat_3_num': 'Zero', 'stat_3_label': 'Călătorii Sponsorizate', 'stat_3_sub': '100% Fără compromisuri',
        'stat_4_num': '4', 'stat_4_label': 'Capitale Fluviale', 'stat_4_sub': 'Apele Europei de Vest',
        'flagship_eyebrow': 'GHIDURI PRINCIPALE',
        'flagship_title': 'Ghidurile Noastre Testate pe Apă',
        'flagship_sub': 'Fiecare ghid este actualizat lunar cu prețuri reale, pontoane de îmbarcare și fotografii originale.',
        'btn_read_guide': 'Citește ghidul complet →',
        'btn_compare': 'Vezi comparația →',
        'manifesto_eyebrow': 'METODOLOGIA NOASTRĂ SUB ACOPERIRE',
        'manifesto_title': 'De Ce Să Ai Încredere în The Cruise Detective?',
        'manifesto_sub': 'Alte platforme copiază pliantele agențiilor. Noi urcăm la bord sub acoperire.',
        'man_1_title': '100% Autofinanțat și Sub Acoperire',
        'man_1_text': 'Nu acceptăm niciodată bilete de presă sau tratament preferențial. Stăm la coadă alături de ceilalți călători și plătim tariful standard.',
        'man_2_title': 'Zero Influență Publicitară',
        'man_2_text': 'Evaluările noastre nu sunt de vânzare. Dacă un vas servește mâncare congelată sau înghesuie mesele, scriem asta deschis.',
        'man_3_title': 'Logistică Verificată pe Teren',
        'man_3_text': 'Coordonate GPS exacte ale pontoanelor, stații de metrou apropiate, politici privind mesele la fereastră și sfaturi utile.',
        'author_eyebrow': 'DETECTIV ȘEF ȘI FONDATOR',
        'author_name': 'Adam Dimitrov',
        'author_role': 'Fondator și Redactor-Șef',
        'author_bio': 'Adam Dimitrov a fondat The Cruise Detective pentru a aduce transparență totală în domeniul croazierelor fluviale europene, după ce a testat direct zeci de ambarcațiuni.',
        'author_link': 'Află mai multe despre metodologia noastră →',
        # Footer
        'footer_desc': 'TheCruiseDetective.com este ghidul dumneavoastră independent și testat pe teren pentru alegerea celor mai bune croaziere fluviale, pe canale și cu cină din Europa.',
        'footer_guides_head': 'Ghiduri Populare',
        'footer_company_head': 'Companie și Încredere',
        'footer_privacy': 'Politica de confidențialitate',
        'footer_terms': 'Termeni și condiții',
    }
}

def build_navbar(lang, mapping):
    d = I18N[lang]
    home_url = mapping.get('home', f'/{lang}/')
    dinner_url = mapping.get('paris_dinner', f'/{lang}/dinner-cruises')
    sightseeing_url = mapping.get('paris_sightseeing', f'/{lang}/seine-cruises')
    duel_url = mapping.get('duel', f'/{lang}/duel')
    amsterdam_url = mapping.get('amsterdam', f'/{lang}/amsterdam')
    london_url = mapping.get('london', f'/{lang}/london')
    about_url = mapping.get('about', f'/{lang}/about')
    contact_url = mapping.get('contact', f'/{lang}/contact')

    return f'''<header class="ltt-navbar" role="banner">
    <div class="ltt-nav-inner">
      <a aria-label="{d['brand']} Homepage" class="ltt-brand" href="{home_url}">
        <img alt="{d['brand']} Logo" class="ltt-brand-logo" height="36" src="/assets/cdn/652d0405192ba076b04f74a3/6570a89c8c97ba4e084ac5d5_webclip-cruise-detective.png" width="36"/>
        <span class="ltt-brand-text">{d['brand']}</span>
      </a>

      <nav aria-label="Primary Navigation" class="ltt-nav-links">
        <div class="ltt-nav-dropdown" id="lttExploreDropdown">
          <button aria-expanded="false" aria-haspopup="true" class="ltt-nav-link ltt-dropdown-btn" type="button">
            <span>{d['destinations']}</span>
            <svg class="ltt-chevron" fill="none" height="12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" viewBox="0 0 24 24" width="12">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          <div class="ltt-mega-menu" role="menu">
            <div class="ltt-mega-col">
              <div class="ltt-mega-head">{d['seine_heading']}</div>
              <a class="ltt-mega-item" href="{dinner_url}">
                <span class="ltt-mega-icon">🍷</span>
                <div>
                  <strong>{d['paris_dinner']}</strong>
                  <p>{d['paris_dinner_sub']}</p>
                </div>
              </a>
              <a class="ltt-mega-item" href="{sightseeing_url}">
                <span class="ltt-mega-icon">🗼</span>
                <div>
                  <strong>{d['paris_sightseeing']}</strong>
                  <p>{d['paris_sightseeing_sub']}</p>
                </div>
              </a>
              <a class="ltt-mega-item" href="{duel_url}">
                <span class="ltt-mega-icon">⚖️</span>
                <div>
                  <strong>{d['duel']}</strong>
                  <p>{d['duel_sub']}</p>
                </div>
              </a>
            </div>
            <div class="ltt-mega-col">
              <div class="ltt-mega-head">{d['waterways_heading']}</div>
              <a class="ltt-mega-item" href="{amsterdam_url}">
                <span class="ltt-mega-icon">🌷</span>
                <div>
                  <strong>{d['amsterdam']}</strong>
                  <p>{d['amsterdam_sub']}</p>
                </div>
              </a>
              <a class="ltt-mega-item" href="{london_url}">
                <span class="ltt-mega-icon">🇬🇧</span>
                <div>
                  <strong>{d['london']}</strong>
                  <p>{d['london_sub']}</p>
                </div>
              </a>
            </div>
          </div>
        </div>

        <a class="ltt-nav-link" href="{dinner_url}">{d['top_dinner']}</a>
        <a class="ltt-nav-link" href="{sightseeing_url}">{d['top_sightseeing']}</a>
        <a class="ltt-nav-link" href="{about_url}">{d['about']}</a>
        <a class="ltt-nav-link" href="{contact_url}">{d['contact']}</a>
      </nav>

      <div class="ltt-nav-right">
        <button aria-controls="lttMobileDrawer" aria-expanded="false" aria-label="Toggle Menu" class="ltt-hamburger" id="lttNavToggle" type="button">
          <span class="ltt-hamburger-bar"></span>
          <span class="ltt-hamburger-bar"></span>
          <span class="ltt-hamburger-bar"></span>
        </button>
      </div>
    </div>

    <!-- Mobile Drawer -->
    <div aria-hidden="true" class="ltt-mobile-drawer" id="lttMobileDrawer">
      <div class="ltt-drawer-content">
        <div class="ltt-mobile-section">
          <div class="ltt-mobile-label">{d['drawer_destinations']}</div>
          <a class="ltt-mobile-link" href="{dinner_url}">
            <span>🍷 {d['paris_dinner']}</span>
            <span style="font-size:10px; font-weight:800; background:#dfa732; color:#fff; padding:2px 7px; border-radius:9999px;">{d['top_pick']}</span>
          </a>
          <a class="ltt-mobile-link" href="{sightseeing_url}">
            <span>🗼 {d['paris_sightseeing']}</span>
          </a>
          <a class="ltt-mobile-link" href="{duel_url}">
            <span>⚖️ {d['duel']}</span>
          </a>
          <a class="ltt-mobile-link" href="{amsterdam_url}">
            <span>🌷 {d['amsterdam']}</span>
          </a>
          <a class="ltt-mobile-link" href="{london_url}">
            <span>🇬🇧 {d['london']}</span>
          </a>
        </div>
        <div class="ltt-mobile-section">
          <div class="ltt-mobile-label">{d['drawer_editorial']}</div>
          <a class="ltt-mobile-link" href="{about_url}">
            <span>📖 {d['about']}</span>
          </a>
          <a class="ltt-mobile-link" href="{contact_url}">
            <span>✉️ {d['contact']}</span>
          </a>
        </div>
      </div>
    </div>
  </header>'''

def build_footer(lang, mapping):
    d = I18N[lang]
    home_url = mapping.get('home', f'/{lang}/')
    dinner_url = mapping.get('paris_dinner', f'/{lang}/dinner-cruises')
    sightseeing_url = mapping.get('paris_sightseeing', f'/{lang}/seine-cruises')
    duel_url = mapping.get('duel', f'/{lang}/duel')
    amsterdam_url = mapping.get('amsterdam', f'/{lang}/amsterdam')
    london_url = mapping.get('london', f'/{lang}/london')
    about_url = mapping.get('about', f'/{lang}/about')
    contact_url = mapping.get('contact', f'/{lang}/contact')
    privacy_url = mapping.get('privacy', f'/{lang}/privacy-policy')
    terms_url = mapping.get('terms', f'/{lang}/terms-of-service')

    return f'''<div class="footer-section">
      <div class="container-21">
        <div class="w-layout-grid footer-grid-2">
          <div class="logo-wrap">
            <p class="footer-logo-paragraph paragraph-17 paragraph-18">
              <a class="footer-logo-text-link" href="{home_url}" style="display: inline-flex; align-items: center; gap: 10px;">
                <img alt="{d['brand']} Logo" height="28" src="/assets/cruise_detective_logo.png" style="border-radius: 50%; display: inline-block; flex-shrink: 0;" width="28"/>
                <span>{d['brand']}</span>
              </a>
            </p>
            <p class="footer-paragraph">{d['footer_desc']}</p>
          </div>
          <div class="w-layout-grid footer-links-grid">
            <div class="footer-link-column">
              <div class="footer-link-title">{d['footer_guides_head']}</div>
              <a class="footer-link-3" href="{sightseeing_url}">{d['paris_sightseeing']}</a>
              <a class="footer-link-3" href="{dinner_url}">{d['paris_dinner']}</a>
              <a class="footer-link-3" href="{duel_url}">{d['duel']}</a>
              <a class="footer-link-3" href="{amsterdam_url}">{d['amsterdam']}</a>
              <a class="footer-link-3" href="{london_url}">{d['london']}</a>
            </div>
            <div class="footer-link-column">
              <div class="footer-link-title">{d['footer_company_head']}</div>
              <a class="footer-link-3" href="{about_url}">{d['about']}</a>
              <a class="footer-link-3" href="{about_url}#methodology">{d['manifesto_title']}</a>
              <a class="footer-link-3" href="{contact_url}">{d['contact']}</a>
            </div>
          </div>
        </div>
        <div class="footer-social-wrap">
          <div class="legal-wrap">
            <p class="legal-paragraph">© 2026 {d['brand']}. All rights reserved.</p>
            <div class="legal-links-wrap">
              <a class="legal-link" href="{privacy_url}">{d['footer_privacy']}</a>
              <span class="legal-divider">•</span>
              <a class="legal-link" href="{terms_url}">{d['footer_terms']}</a>
            </div>
          </div>
        </div>
      </div>
    </div>'''

PILL_BUTTON_STYLE = '''<style id="cd-universal-pill-buttons">
/* The Cruise Detective - Universal Circular Pill Buttons Standard */
.buy-button-2, .buy-button-3, .bpa-btn, .btn, .global-sticky-cta-btn, .ltt-pill-btn, .ltt-duel-btn, .card-button, a.button, .button-primary, .button-gold, .tcd-btn, .load-more {
  border-radius: 9999px !important;
  background: linear-gradient(135deg, #dfa732 0%, #b88214 100%) !important;
  color: #ffffff !important;
  font-weight: 800 !important;
  box-shadow: 0 4px 14px rgba(223, 167, 50, 0.35) !important;
  transition: all 0.2s ease !important;
  text-decoration: none !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  border: none !important;
}
.buy-button-2:hover, .buy-button-3:hover, .bpa-btn:hover, .btn:hover, .global-sticky-cta-btn:hover, .ltt-pill-btn:hover, .ltt-duel-btn:hover, .card-button:hover, .tcd-btn:hover, .load-more:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(223, 167, 50, 0.45) !important;
  background: linear-gradient(135deg, #e5b342 0%, #c48e1a 100%) !important;
  color: #ffffff !important;
}
</style>'''

KILL_BADGE_STYLE = '''<style id="cd-kill-webflow-badge">
.w-webflow-badge, a.w-webflow-badge, [class*="w-webflow-badge"], a[href*="webflow.com?utm_campaign=brandjs"], a[href*="webflow.com/?utm_campaign=brandjs"] {
  display: none !important; opacity: 0 !important; visibility: hidden !important; pointer-events: none !important;
  position: absolute !important; top: -99999px !important; left: -99999px !important; width: 0 !important; height: 0 !important; z-index: -99999 !important;
}
</style>'''

GOOGLE_FONTS_LINK = '''<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="/css/editorial-luxury.css"/>'''

def enhance_head(html):
    # Ensure badge killer
    if 'id="cd-kill-webflow-badge"' not in html:
        html = re.sub(r'(<head[^>]*>)', r'\1\n' + KILL_BADGE_STYLE, html, count=1, flags=re.IGNORECASE)
    
    # Ensure google fonts and editorial-luxury.css
    if 'editorial-luxury.css' not in html:
        html = re.sub(r'(</head>)', GOOGLE_FONTS_LINK + '\n\\1', html, count=1, flags=re.IGNORECASE)
    
    # Ensure universal pill buttons style
    if 'id="cd-universal-pill-buttons"' not in html:
        html = re.sub(r'(</head>)', PILL_BUTTON_STYLE + '\n\\1', html, count=1, flags=re.IGNORECASE)
    
    return html

def enhance_scripts(html):
    # Ensure webflow-sync.js and ltt-nav.js are before </body>
    if 'ltt-nav.js' not in html:
        html = re.sub(r'(</body>)', '<script src="/js/ltt-nav.js" defer></script>\n\\1', html, count=1, flags=re.IGNORECASE)
    if 'webflow-sync.js' not in html:
        html = re.sub(r'(</body>)', '<script src="/webflow-sync.js"></script>\n\\1', html, count=1, flags=re.IGNORECASE)
    return html

def remove_legacy_navs_and_insert_ltt_nav(html, lang, mapping):
    navbar_html = build_navbar(lang, mapping)
    
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('body')
    if not body:
        return html
    
    # Remove all legacy nav wrappers
    for legacy_cls in ['navigation-mob', 'navigation-4', 't-navigation', 'ltt-navbar']:
        for el in body.find_all('div', class_=lambda c: c and legacy_cls in c):
            el.decompose()
        for el in body.find_all('header', class_=lambda c: c and legacy_cls in c):
            el.decompose()
    
    # Also clean up any loose mobile drawer
    drawer = body.find(id='lttMobileDrawer')
    if drawer:
        drawer.decompose()

    new_nav_soup = BeautifulSoup(navbar_html, 'html.parser')
    body.insert(0, new_nav_soup)
    return str(soup)

def replace_footer(html, lang, mapping):
    footer_html = build_footer(lang, mapping)
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find existing footer
    found = False
    for el in soup.find_all('div', class_='footer-section'):
        el.replace_with(BeautifulSoup(footer_html, 'html.parser'))
        found = True
        break
    if not found:
        for el in soup.find_all('footer'):
            el.replace_with(BeautifulSoup(footer_html, 'html.parser'))
            found = True
            break
    
    return str(soup)

def build_homepage_html(lang, mapping):
    d = I18N[lang]
    home_url = mapping.get('home', f'/{lang}/')
    dinner_url = mapping.get('paris_dinner', f'/{lang}/dinner-cruises')
    sightseeing_url = mapping.get('paris_sightseeing', f'/{lang}/seine-cruises')
    duel_url = mapping.get('duel', f'/{lang}/duel')
    amsterdam_url = mapping.get('amsterdam', f'/{lang}/amsterdam')
    london_url = mapping.get('london', f'/{lang}/london')
    about_url = mapping.get('about', f'/{lang}/about')
    contact_url = mapping.get('contact', f'/{lang}/contact')

    navbar_html = build_navbar(lang, mapping)
    footer_html = build_footer(lang, mapping)

    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
{KILL_BADGE_STYLE}
  <meta charset="utf-8"/>
  <title>{d['brand']} — {d['home_title']} {d['home_title_gold']}</title>
  <meta content="{d['home_subtitle']}" name="description"/>
  <meta content="{d['brand']} — {d['home_title']} {d['home_title_gold']}" property="og:title"/>
  <meta content="{d['home_subtitle']}" property="og:description"/>
  <meta content="https://www.thecruisedetective.com/assets/cruise_detective_logo.png" property="og:image"/>
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link href="https://www.thecruisedetective.com{home_url}" rel="canonical"/>

  <link rel="icon" type="image/x-icon" href="/favicon.ico"/>
  <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico"/>
  <link rel="apple-touch-icon" href="/assets/apple-touch-icon.png"/>

  {GOOGLE_FONTS_LINK}
  {PILL_BUTTON_STYLE}

  <style>
    .ltt-home-hero {{
      background: radial-gradient(circle at 50% 18%, rgba(2, 132, 199, 0.16) 0%, transparent 60%), linear-gradient(180deg, #0a192f 0%, #0f172a 100%) !important;
      color: #ffffff;
      padding: 76px 20px 88px 20px;
      text-align: center;
      position: relative;
    }}
    .ltt-gold-text {{
      background: linear-gradient(135deg, #dfa732 0%, #fef08a 50%, #b88214 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: inline-block;
    }}
    .ltt-hero-container {{
      max-width: 960px;
      margin: 0 auto;
    }}
    .ltt-hero-eyebrow {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 14px;
      background: rgba(223, 167, 50, 0.15);
      border: 1px solid rgba(223, 167, 50, 0.35);
      border-radius: 9999px;
      font-size: 11.5px;
      font-weight: 800;
      color: #fef08a;
      letter-spacing: 0.08em;
      margin-bottom: 24px;
      text-transform: uppercase;
    }}
    .ltt-hero-title {{
      font-family: 'Plus Jakarta Sans', var(--font-sans);
      font-size: 46px;
      line-height: 1.18;
      font-weight: 800;
      letter-spacing: -0.025em;
      margin: 0 0 20px 0;
      color: #ffffff;
    }}
    .ltt-hero-subtitle {{
      font-size: 17.5px;
      line-height: 1.65;
      color: #cbd5e1;
      max-width: 820px;
      margin: 0 auto 36px auto;
      font-weight: 400;
    }}
    .ltt-stats-strip {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      max-width: 880px;
      margin: 0 auto 36px auto;
    }}
    .ltt-stat-card {{
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 16px 12px;
      backdrop-filter: blur(10px);
    }}
    .ltt-stat-number {{
      font-family: 'Plus Jakarta Sans', var(--font-sans);
      font-size: 26px;
      font-weight: 800;
      color: #dfa732;
      line-height: 1.1;
      margin-bottom: 4px;
    }}
    .ltt-stat-label {{
      font-size: 12.5px;
      font-weight: 700;
      color: #f1f5f9;
      line-height: 1.25;
      margin-bottom: 2px;
    }}
    .ltt-stat-sub {{
      font-size: 10.5px;
      color: #94a3b8;
    }}
    .ltt-quick-links {{
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
      gap: 10px;
      margin-top: 24px;
    }}
    .ltt-quick-btn {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.16);
      color: #ffffff;
      padding: 9px 18px;
      border-radius: 9999px;
      font-size: 13.5px;
      font-weight: 600;
      text-decoration: none;
      transition: all 0.2s ease;
    }}
    .ltt-quick-btn:hover {{
      background: rgba(223, 167, 50, 0.25);
      border-color: #dfa732;
      color: #ffffff;
      transform: translateY(-1px);
    }}
    .ltt-section {{
      padding: 72px 20px;
      max-width: 1180px;
      margin: 0 auto;
    }}
    .ltt-section-header {{
      text-align: center;
      max-width: 760px;
      margin: 0 auto 48px auto;
    }}
    .ltt-section-eyebrow {{
      font-size: 11.5px;
      font-weight: 800;
      color: #b88214;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 8px;
    }}
    .ltt-section-title {{
      font-family: 'Plus Jakarta Sans', var(--font-sans);
      font-size: 34px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.22;
      margin: 0 0 14px 0;
    }}
    .ltt-section-subtitle {{
      font-size: 16px;
      color: #64748b;
      line-height: 1.6;
      margin: 0;
    }}
    .ltt-guides-grid-2x2 {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 28px;
    }}
    .ltt-guide-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      overflow: hidden;
      box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
      transition: all 0.25s ease;
      display: flex;
      flex-direction: column;
    }}
    .ltt-guide-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
      border-color: #cbd5e1;
    }}
    .ltt-guide-thumb {{
      position: relative;
      height: 220px;
      overflow: hidden;
      background: #0f172a;
    }}
    .ltt-guide-thumb img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.4s ease;
    }}
    .ltt-guide-card:hover .ltt-guide-thumb img {{
      transform: scale(1.04);
    }}
    .ltt-guide-badge {{
      position: absolute;
      top: 14px;
      left: 14px;
      background: rgba(15, 23, 42, 0.85);
      backdrop-filter: blur(8px);
      color: #ffffff;
      font-size: 11px;
      font-weight: 800;
      padding: 5px 12px;
      border-radius: 9999px;
      letter-spacing: 0.05em;
      border: 1px solid rgba(255, 255, 255, 0.15);
    }}
    .ltt-guide-body {{
      padding: 24px;
      display: flex;
      flex-direction: column;
      flex-grow: 1;
    }}
    .ltt-guide-title {{
      font-family: 'Plus Jakarta Sans', var(--font-sans);
      font-size: 21px;
      font-weight: 800;
      color: #0f172a;
      line-height: 1.3;
      margin: 0 0 10px 0;
    }}
    .ltt-guide-desc {{
      font-size: 14.5px;
      color: #475569;
      line-height: 1.6;
      margin: 0 0 20px 0;
      flex-grow: 1;
    }}
    .ltt-manifesto-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
    }}
    .ltt-manifesto-card {{
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 14px;
      padding: 28px 24px;
    }}
    .ltt-manifesto-icon {{
      font-size: 32px;
      margin-bottom: 16px;
      display: inline-block;
    }}
    .ltt-manifesto-title {{
      font-family: 'Plus Jakarta Sans', var(--font-sans);
      font-size: 18px;
      font-weight: 800;
      color: #0f172a;
      margin: 0 0 10px 0;
    }}
    .ltt-manifesto-text {{
      font-size: 14px;
      color: #64748b;
      line-height: 1.65;
      margin: 0;
    }}
    .ltt-author-section {{
      background: #f8fafc;
      border-top: 1px solid #e2e8f0;
      border-bottom: 1px solid #e2e8f0;
      padding: 64px 20px;
    }}
    .ltt-author-card {{
      max-width: 860px;
      margin: 0 auto;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 16px;
      padding: 36px;
      box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05);
      display: flex;
      gap: 28px;
      align-items: center;
    }}
    .ltt-author-img {{
      width: 100px;
      height: 100px;
      border-radius: 50%;
      object-fit: cover;
      flex-shrink: 0;
      border: 3px solid #dfa732;
    }}
    @media (max-width: 768px) {{
      .ltt-hero-title {{ font-size: 32px; }}
      .ltt-stats-strip {{ grid-template-columns: repeat(2, 1fr); }}
      .ltt-guides-grid-2x2 {{ grid-template-columns: 1fr; }}
      .ltt-manifesto-grid {{ grid-template-columns: 1fr; }}
      .ltt-author-card {{ flex-direction: column; text-align: center; }}
    }}
  </style>
</head>
<body>

{navbar_html}

<main id="main-content">
  <!-- HERO SECTION -->
  <section class="ltt-home-hero">
    <div class="ltt-hero-container">
      <div class="ltt-hero-eyebrow">
        {d['home_eyebrow']}
      </div>
      <h1 class="ltt-hero-title">
        {d['home_title']} <span class="ltt-gold-text">{d['home_title_gold']}</span>
      </h1>
      <p class="ltt-hero-subtitle">
        {d['home_subtitle']}
      </p>

      <div class="ltt-stats-strip">
        <div class="ltt-stat-card">
          <div class="ltt-stat-number">{d['stat_1_num']}</div>
          <div class="ltt-stat-label">{d['stat_1_label']}</div>
          <div class="ltt-stat-sub">{d['stat_1_sub']}</div>
        </div>
        <div class="ltt-stat-card">
          <div class="ltt-stat-number">{d['stat_2_num']}</div>
          <div class="ltt-stat-label">{d['stat_2_label']}</div>
          <div class="ltt-stat-sub">{d['stat_2_sub']}</div>
        </div>
        <div class="ltt-stat-card">
          <div class="ltt-stat-number">{d['stat_3_num']}</div>
          <div class="ltt-stat-label">{d['stat_3_label']}</div>
          <div class="ltt-stat-sub">{d['stat_3_sub']}</div>
        </div>
        <div class="ltt-stat-card">
          <div class="ltt-stat-number">{d['stat_4_num']}</div>
          <div class="ltt-stat-label">{d['stat_4_label']}</div>
          <div class="ltt-stat-sub">{d['stat_4_sub']}</div>
        </div>
      </div>

      <div class="ltt-quick-links">
        <a class="ltt-quick-btn" href="{dinner_url}">🍷 {d['paris_dinner']}</a>
        <a class="ltt-quick-btn" href="{sightseeing_url}">🗼 {d['paris_sightseeing']}</a>
        <a class="ltt-quick-btn" href="{duel_url}">⚖️ {d['duel']}</a>
        <a class="ltt-quick-btn" href="{amsterdam_url}">🌷 {d['amsterdam']}</a>
        <a class="ltt-quick-btn" href="{london_url}">🇬🇧 {d['london']}</a>
      </div>
    </div>
  </section>

  <!-- FLAGSHIP GUIDES -->
  <section class="ltt-section">
    <div class="ltt-section-header">
      <div class="ltt-section-eyebrow">{d['flagship_eyebrow']}</div>
      <h2 class="ltt-section-title">{d['flagship_title']}</h2>
      <p class="ltt-section-subtitle">{d['flagship_sub']}</p>
    </div>

    <div class="ltt-guides-grid-2x2">
      <!-- 1. Paris Dinner -->
      <div class="ltt-guide-card">
        <div class="ltt-guide-thumb">
          <img alt="{d['paris_dinner']}" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/65562265e60663a885093897_paris-dinner-cruises-featured-image.webp"/>
          <span class="ltt-guide-badge">PARIS SEINE • 🏆 {d['top_pick']}</span>
        </div>
        <div class="ltt-guide-body">
          <h3 class="ltt-guide-title">{d['paris_dinner']}</h3>
          <p class="ltt-guide-desc">{d['paris_dinner_sub']}</p>
          <a class="buy-button-2" href="{dinner_url}">{d['btn_read_guide']}</a>
        </div>
      </div>

      <!-- 2. Paris Sightseeing -->
      <div class="ltt-guide-card">
        <div class="ltt-guide-thumb">
          <img alt="{d['paris_sightseeing']}" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/655a5bf3dd14e3169a969cc5_grid-best-river-cruises-paris.webp"/>
          <span class="ltt-guide-badge">PARIS SEINE • 🗼 ESSENTIAL</span>
        </div>
        <div class="ltt-guide-body">
          <h3 class="ltt-guide-title">{d['paris_sightseeing']}</h3>
          <p class="ltt-guide-desc">{d['paris_sightseeing_sub']}</p>
          <a class="buy-button-2" href="{sightseeing_url}">{d['btn_read_guide']}</a>
        </div>
      </div>

      <!-- 3. Mouches vs Parisiens Duel -->
      <div class="ltt-guide-card">
        <div class="ltt-guide-thumb">
          <img alt="{d['duel']}" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/6557d7488c95f4ddb81c828e_Bateaux-mouches-dinner-cruise%20(15).webp"/>
          <span class="ltt-guide-badge">PARIS SEINE • ⚖️ DUEL</span>
        </div>
        <div class="ltt-guide-body">
          <h3 class="ltt-guide-title">{d['duel']}</h3>
          <p class="ltt-guide-desc">{d['duel_sub']}</p>
          <a class="buy-button-2" href="{duel_url}">{d['btn_compare']}</a>
        </div>
      </div>

      <!-- 4. Amsterdam Canals -->
      <div class="ltt-guide-card">
        <div class="ltt-guide-thumb">
          <img alt="{d['amsterdam']}" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/655b4f84c8be1a48c66e28d8_canal-cruise-amsterdam-featured-image.webp"/>
          <span class="ltt-guide-badge">AMSTERDAM • 🌷 CLASSIC</span>
        </div>
        <div class="ltt-guide-body">
          <h3 class="ltt-guide-title">{d['amsterdam']}</h3>
          <p class="ltt-guide-desc">{d['amsterdam_sub']}</p>
          <a class="buy-button-2" href="{amsterdam_url}">{d['btn_read_guide']}</a>
        </div>
      </div>
    </div>
  </section>

  <!-- EDITORIAL MANIFESTO -->
  <section class="ltt-section" style="padding-top: 0;">
    <div class="ltt-section-header">
      <div class="ltt-section-eyebrow">{d['manifesto_eyebrow']}</div>
      <h2 class="ltt-section-title">{d['manifesto_title']}</h2>
      <p class="ltt-section-subtitle">{d['manifesto_sub']}</p>
    </div>

    <div class="ltt-manifesto-grid">
      <div class="ltt-manifesto-card">
        <div class="ltt-manifesto-icon">💶</div>
        <h3 class="ltt-manifesto-title">{d['man_1_title']}</h3>
        <p class="ltt-manifesto-text">{d['man_1_text']}</p>
      </div>
      <div class="ltt-manifesto-card">
        <div class="ltt-manifesto-icon">⚖️</div>
        <h3 class="ltt-manifesto-title">{d['man_2_title']}</h3>
        <p class="ltt-manifesto-text">{d['man_2_text']}</p>
      </div>
      <div class="ltt-manifesto-card">
        <div class="ltt-manifesto-icon">📍</div>
        <h3 class="ltt-manifesto-title">{d['man_3_title']}</h3>
        <p class="ltt-manifesto-text">{d['man_3_text']}</p>
      </div>
    </div>
  </section>

  <!-- FOUNDER BIO -->
  <section class="ltt-author-section">
    <div class="ltt-author-card">
      <img alt="{d['author_name']}" class="ltt-author-img" height="100" src="/assets/cdn/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp" width="100"/>
      <div>
        <div style="font-size: 11px; font-weight: 800; color: #b88214; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 4px;">{d['author_eyebrow']}</div>
        <h3 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 22px; font-weight: 800; color: #0f172a; margin: 0 0 4px 0;">{d['author_name']}</h3>
        <div style="font-size: 13.5px; font-weight: 600; color: #64748b; margin-bottom: 12px;">{d['author_role']}</div>
        <p style="font-size: 14.5px; color: #334155; line-height: 1.65; margin: 0 0 16px 0;">{d['author_bio']}</p>
        <a href="{about_url}" style="font-size: 13.5px; font-weight: 700; color: #b88214; text-decoration: none;">{d['author_link']}</a>
      </div>
    </div>
  </section>
</main>

{footer_html}

<script src="/js/ltt-nav.js" defer></script>
<script src="/webflow-sync.js"></script>
</body>
</html>'''

def harmonize_file(rel_path, page_type, lang, mapping):
    abs_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(abs_path):
        return
    
    # 1. Homepage complete overhaul
    if page_type == 'home':
        new_html = build_homepage_html(lang, mapping)
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        print(f"[{lang.upper()}] Rebuilt luxury homepage: {rel_path}")
        return

    # 2. General page harmonization
    with open(abs_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Head styles & fonts
    html = enhance_head(html)
    
    # Scripts
    html = enhance_scripts(html)

    # Navbar
    html = remove_legacy_navs_and_insert_ltt_nav(html, lang, mapping)

    # Footer
    html = replace_footer(html, lang, mapping)

    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[{lang.upper()}] Harmonized: {rel_path} ({page_type})")

def main():
    mappings = build_page_mappings()
    print(f"Loaded mappings across {len(mappings)} languages.")
    
    for lang in LANGS:
        print(f"\n==========================================")
        print(f"Processing Language: {lang.upper()}")
        print(f"==========================================")
        lang_mapping = mappings[lang]
        
        files = glob.glob(os.path.join(BASE_DIR, f'{lang}/**/*.html'), recursive=True)
        for f in sorted(files):
            rel = os.path.relpath(f, BASE_DIR)
            c = classify_path(rel)
            harmonize_file(rel, c, lang, lang_mapping)

if __name__ == '__main__':
    main()
