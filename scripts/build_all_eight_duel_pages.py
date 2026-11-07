#!/usr/bin/env python3
"""
MASTER DUEL SHOWDOWN BUILDER FOR ALL 8 LANGUAGES
Ports 100% of the English Luxury Travel Tester architecture to:
- fr/bateaux-mouches-ou-bateaux-parisiens/index.html
- de/bateaux-mouches-gegen-bateaux-parisiens-dinner-kreuzfahrt-nebeneinander-vergleich/index.html
- es/comparación-de-crucero-con-cena-bateaux-mouches-vs-bateaux-parisiens-lado-a-lado/index.html
- it/bateaux-mouches-vs-bateaux-parisiens-crociera-con-cena-confronto-fianco-a-fianco/index.html
- ja/バトームーシュとバトーパリジャンのディナークルーズの並べて比較/index.html
- nl/bateaux-mouches-vs-bateaux-parisiens-dinercruise-zij-aan-zij-vergelijking/index.html
- pl/porównanie-bateaux-mouches-vs-bateaux-parisiens-rejs-z-kolacją/index.html
- ro/bateaux-mouches-vs-bateaux-parisiens-cina-croazieră-comparație-alăturată/index.html
"""

import os
import sys
import re
import subprocess
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'
sys.path.insert(0, BASE_DIR)
from scripts.upgrade_translated_duel_pages import DUEL_I18N

DUEL_PAGES = {
    'fr': 'fr/bateaux-mouches-ou-bateaux-parisiens/index.html',
    'de': 'de/bateaux-mouches-gegen-bateaux-parisiens-dinner-kreuzfahrt-nebeneinander-vergleich/index.html',
    'es': 'es/comparación-de-crucero-con-cena-bateaux-mouches-vs-bateaux-parisiens-lado-a-lado/index.html',
    'it': 'it/bateaux-mouches-vs-bateaux-parisiens-crociera-con-cena-confronto-fianco-a-fianco/index.html',
    'ja': 'ja/バトームーシュとバトーパリジャンのディナークルーズの並べて比較/index.html',
    'nl': 'nl/bateaux-mouches-vs-bateaux-parisiens-dinercruise-zij-aan-zij-vergelijking/index.html',
    'pl': 'pl/porównanie-bateaux-mouches-vs-bateaux-parisiens-rejs-z-kolacją/index.html',
    'ro': 'ro/bateaux-mouches-vs-bateaux-parisiens-cina-croazieră-comparație-alăturată/index.html'
}

MATRIX_I18N = {
    'fr': {
        'title': 'Tableau Comparatif Détaillé Fonctionnalité par Fonctionnalité',
        'sub': 'Principales différences opérationnelles, culinaires et logistiques entre les deux opérateurs.',
        'th_feature': 'Critère Vérifié',
        'th_a': '🏆 Dîner Bateaux Mouches',
        'th_b': '🗼 Dîner Bateaux Parisiens',
        'rows': [
            ('Prix de départ', '115 € (Prestige 3 plats) / 165 € (Excellence 4 plats)', '85 € (Service 18h15) / 109 € (Étoile) / 139–179 € (Privilège) / 215 € (Premier)'),
            ('Port d\'embarquement', '📍 Pont de l\'Alma (Port de la Conférence, 8e arr.)', '📍 Port de la Bourdonnais, ponton 5/7 (Pied de la Tour Eiffel, 7e arr.)'),
            ('Durée de la croisière', '⏱️ 2h15 (départ 20h30)', '⏱️ 2h30 (départ 20h30) / 1h15 (départ 18h15)'),
            ('Architecture du bateau', 'Navire classique spacieux, plafond étoilé, boiseries et cuivre rétro', 'Trimaran moderne entièrement vitré avec verrière incurvée à 360°'),
            ('Pont supérieur en plein air', '✅ Pont terrasse 360° en plein air accessible pendant toute la croisière', '❌ Salon fermé uniquement (aucun accès au toit pendant le dîner)'),
            ('Animation musicale live', '🎻 Duo Violon & Piano à queue en direct (répertoire classique romantique)', '🎤 Chanteuse en direct & clavier (répertoire lounge / pop internationale)'),
            ('Cuisine & Préparation', '🍽️ 100% cuisinée à bord à la minute (haute gastronomie française 4 plats)', '🍽️ Préparée à bord (cuisine française contemporaine fiable)'),
            ('Placement côté fenêtre', 'Excellente visibilité partout ; tables fenêtre prioritaires sur Excellence', 'Tarification strictement par zone (Étoile au centre ; Privilège/Premier fenêtre)'),
            ('Code vestimentaire', 'Élégant / Smart casual (veste recommandée ; pas de survêtements ni baskets)', 'Élégant / Smart casual (pas de shorts, tongs ou survêtements)'),
            ('Tarifs enfants', 'Bébés 0–3 ans gratuits ; Menu enfant 37 € (4–12 ans)', 'Bébés 0–3 ans gratuits ; -66% sur le tarif Étoile (0–11 ans)'),
            ('Wi-Fi à bord', '❌ Pas de Wi-Fi à bord', '✅ Wi-Fi gratuit à bord'),
            ('Le Verdict du Détective', '🏆 GAGNANT : Romantisme classique, cuisine supérieure & terrasse ouverte 360°', '🗼 GAGNANT : Embarquement immédiat sous la Tour Eiffel & verrière futuriste')
        ]
    },
    'de': {
        'title': 'Detaillierter Feature-für-Feature Vergleich',
        'sub': 'Wichtigste betriebliche, kulinarische und logistische Unterschiede beider Anbieter.',
        'th_feature': 'Geprüftes Merkmal',
        'th_a': '🏆 Bateaux Mouches Dinner',
        'th_b': '🗼 Bateaux Parisiens Dinner',
        'rows': [
            ('Startpreis', '115 € (Prestige 3-Gänge) / 165 € (Excellence 4-Gänge)', '85 € (18:15 Uhr) / 109 € (Étoile) / 139–179 € (Privilège) / 215 € (Premier)'),
            ('Abfahrtsanleger', '📍 Pont de l\'Alma Anleger (Port de la Conférence, 8. Arr.)', '📍 Eiffelturm Pier 5/7 (Port de la Bourdonnais, 7. Arr.)'),
            ('Fahrtdauer', '⏱️ 2 Stunden 15 Minuten (20:30 Uhr)', '⏱️ 2 Stunden 30 Minuten (20:30 Uhr) / 1h 15m (18:15 Uhr)'),
            ('Schiffsarchitektur', 'Klassisch breites Schiff, Sternenhimmel-Decke, Holz & Messing', 'Modernes, vollständig verglastes Trimaran mit 360°-Panoramadach'),
            ('Freiluft-Oberdeck', '✅ Volles 360° Open-Air-Sonnendeck während der gesamten Fahrt begehbar', '❌ Nur geschlossener Salon (kein Zugang zum Oberdeck während des Essens)'),
            ('Live-Musik', '🎻 Live-Duo aus Violine & Flügel (klassisches Romantik-Repertoire)', '🎤 Live-Sängerin & Keyboard (modernes Lounge- & Pop-Repertoire)'),
            ('Küche & Zubereitung', '🍽️ Frisch an Bord gekocht (gehobene 4-Gänge-Gastronomie)', '🍽️ An Bord zubereitet (verlässliche moderne französische Küche)'),
            ('Fensterplatz-Garantie', 'Gute Sicht von allen Tischen; garantierte Fensterplätze bei Excellence', 'Strikte Preiskategorien (Étoile Mitte; Privilège & Premier Fenster)'),
            ('Kleiderordnung', 'Gepflegt / Smart Casual (Sakko empfohlen; keine Sportkleidung/Sneaker)', 'Gepflegt / Smart Casual (keine Shorts, Sportkleidung oder Flip-Flops)'),
            ('Kinderregelung', 'Kleinkinder 0–3 Jahre gratis; Kindermenü 37 € (4–12 Jahre)', 'Kleinkinder 0–3 Jahre gratis; 66% Rabatt auf Étoile (0–11 Jahre)'),
            ('WLAN an Bord', '❌ Kein WLAN an Bord', '✅ Kostenloses WLAN an Bord'),
            ('Das Urteil des Detektivs', '🏆 SIEGER: Klassische Romantik, feineres Essen & 360°-Freideck', '🗼 SIEGER: Direkter Eiffelturm-Start & modernes Panoramaglas')
        ]
    },
    'es': {
        'title': 'Matriz Comparativa Característica por Característica',
        'sub': 'Diferencias clave operativas, culinarias y logísticas entre ambos operadores.',
        'th_feature': 'Característica Verificada',
        'th_a': '🏆 Cena Bateaux Mouches',
        'th_b': '🗼 Cena Bateaux Parisiens',
        'rows': [
            ('Precio de salida', '115 € (Prestige 3 platos) / 165 € (Excellence 4 platos)', '85 € (Turno 18:15) / 109 € (Étoile) / 139–179 € (Privilège) / 215 € (Premier)'),
            ('Muelle de salida', '📍 Muelle Pont de l\'Alma (Port de la Conférence, 8º arr.)', '📍 Muelle Torre Eiffel Pier 5/7 (Port de la Bourdonnais, 7º arr.)'),
            ('Duración del crucero', '⏱️ 2 horas 15 minutos (20:30)', '⏱️ 2 horas 30 minutos (20:30) / 1h 15m (18:15)'),
            ('Arquitectura del barco', 'Barco clásico espacioso, techo estrellado, detalles en madera y latón', 'Trimarán moderno acristalado con techo panorámico curvado'),
            ('Cubierta superior al aire libre', '✅ Cubierta superior panorámica 360° abierta durante todo el crucero', '❌ Solo salón cerrado (sin acceso a la cubierta exterior durante la cena)'),
            ('Música en vivo', '🎻 Dúo de violín y piano de cola en directo (repertorio clásico romántico)', '🎤 Cantante femenina y teclista en directo (música lounge y pop)'),
            ('Cocina y elaboración', '🍽️ 100% cocinada a bordo al momento (alta cocina francesa de 4 platos)', '🍽️ Elaborada a bordo (cocina francesa contemporánea de calidad)'),
            ('Mesa junto a la ventana', 'Excelente visibilidad en todas las mesas; ventana garantizada en Excellence', 'Precios estrictamente por zonas (Étoile centro; Privilège/Premier ventana)'),
            ('Código de vestimenta', 'Elegante casual (se recomienda chaqueta; no ropa deportiva ni zapatillas)', 'Elegante casual (no pantalones cortos, chanclas ni ropa deportiva)'),
            ('Política de niños', 'Bebés 0–3 gratis; Menú infantil 37 € (4–12 años)', 'Bebés 0–3 gratis; 66% de descuento en categoría Étoile (0–11 años)'),
            ('Wi-Fi a bordo', '❌ Sin Wi-Fi a bordo', '✅ Wi-Fi gratis a bordo'),
            ('Veredicto del Detective', '🏆 GANADOR: Romanticismo clásico, mejor gastronomía y cubierta 360°', '🗼 GANADOR: Salida directa bajo la Torre Eiffel y nave futurista de cristal')
        ]
    },
    'it': {
        'title': 'Matrice Comparativa Dettagliata Caratteristica per Caratteristica',
        'sub': 'Principali differenze operative, gastronomiche e logistiche tra i due operatori.',
        'th_feature': 'Caratteristica Verificata',
        'th_a': '🏆 Cena Bateaux Mouches',
        'th_b': '🗼 Cena Bateaux Parisiens',
        'rows': [
            ('Prezzo di partenza', '115 € (Prestige 3 portate) / 165 € (Excellence 4 portate)', '85 € (18:15) / 109 € (Étoile) / 139–179 € (Privilège) / 215 € (Premier)'),
            ('Molo di partenza', '📍 Pont de l\'Alma (Port de la Conférence, 8° arr.)', '📍 Molo Torre Eiffel Pier 5/7 (Port de la Bourdonnais, 7° arr.)'),
            ('Durata della crociera', '⏱️ 2 ore e 15 minuti (20:30)', '⏱️ 2 ore e 30 minuti (20:30) / 1h 15m (18:15)'),
            ('Architettura della nave', 'Nave classica spaziosa, soffitto stellato, finiture retrò in ottone', 'Trimano moderno completamente a vetri con tetto panoramico curvo'),
            ('Ponte superiore all\'aperto', '✅ Ponte superiore 360° all\'aperto accessibile durante tutta la crociera', '❌ Solo salone chiuso (nessun accesso al ponte durante la cena)'),
            ('Musica dal vivo', '🎻 Duo dal vivo Violino & Pianoforte a coda (repertorio classico romantico)', '🎤 Cantante dal vivo & tastiera (repertorio lounge & pop internazionale)'),
            ('Cucina & Preparazione', '🍽️ Cucinata al 100% a bordo al momento (alta gastronomia francese)', '🍽️ Preparata a bordo (cucina francese contemporanea affidabile)'),
            ('Tavolo vicino alla finestra', 'Ottima visibilità ovunque; tavolo finestra prioritario su Excellence', 'Prezzi strettamente a zone (Étoile centro; Privilège/Premier finestra)'),
            ('Codice di abbigliamento', 'Elegante / Smart casual (giacca gradita; niente abiti sportivi o sneakers)', 'Elegante / Smart casual (niente pantaloncini, ciabatte o tute sportive)'),
            ('Bambini', 'Neonati 0–3 anni gratis; Menu bimbi 37 € (4–12 anni)', 'Neonati 0–3 anni gratis; -66% su tariffa Étoile (0–11 anni)'),
            ('Wi-Fi a bordo', '❌ Nessun Wi-Fi a bordo', '✅ Wi-Fi gratuito a bordo'),
            ('Il Verdetto del Detective', '🏆 VINCITORE: Romanticismo classico, cibo superiore & terrazza aperta 360°', '🗼 VINCITORE: Partenza diretta sotto la Tour Eiffel & vetrate spettacolari')
        ]
    },
    'ja': {
        'title': '項目別 詳細スペック徹底比較表',
        'sub': '両運航会社の運航、料理、設備面における主要な違いを完全比較。',
        'th_feature': '検証項目',
        'th_a': '🏆 バトー・ムーシュ ディナー',
        'th_b': '🗼 バトー・パリジャン ディナー',
        'rows': [
            ('出発料金', '115€（プレステージ 3品）/ 165€（エクセレンス 4品）', '85€（18:15便）/ 109€（エトワール）/ 139〜179€（プリヴィレッジ）/ 215€（プルミエ）'),
            ('出発乗り場', '📍 アルマ橋桟橋（Port de la Conférence、8区・右岸）', '📍 エッフェル塔乗り場 ピア5/7（Port de la Bourdonnais、7区・左岸）'),
            ('クルーズ所要時間', '⏱️ 2時間15分（20:30出航）', '⏱️ 2時間30分（20:30出航）/ 1時間15分（18:15出航）'),
            ('船体構造・デザイン', '重厚感のあるクラシック船、星空ライティング、真鍮の装飾', '全面パノラマ曲面ガラス張りの最新トリマラン船'),
            ('屋外ルーフトップデッキ', '✅ 航行中いつでも自由に360°オープンエア屋上デッキへアクセス可能', '❌ 完全密閉型ガラスサロンのみ（ディナー中の屋上立ち入り不可）'),
            ('生演奏エンタメ', '🎻 バイオリン＆グランドピアノの生二重奏（ロマンチックなクラシック）', '🎤 プロ女性歌手＆キーボードの生ライブ（上質なラウンジ＆名曲ポップス）'),
            ('料理と調理設備', '🍽️ 100%船内厨房での完全調理（本格的なフランス料理4コース）', '🍽️ 船内厨房で仕上げる現代フレンチコース料理'),
            ('窓際席の確保条件', '全席視界良好；エクセレンスプランで窓際優先確保', '座席エリアごとの完全料金制（エトワール中央、プリヴィレッジ・プルミエ窓際）'),
            ('ドレスコード', 'スマートカジュアル（ジャケット推奨；運動着・短パン・スニーカー不可）', 'スマートカジュアル（ビーチサンダル、短パン、スポーツウェア不可）'),
            ('子供料金規定', '0〜3歳無料（食事なし）；子供用メニュー 37€（4〜12歳）', '0〜3歳無料；エトワールチケットが66%割引（0〜11歳）'),
            ('船内Wi-Fi', '❌ 船内Wi-Fiなし', '✅ 無料Wi-Fiあり'),
            ('探偵の最終結論', '🏆 勝者：クラシックな王道ロマンス、極上の料理、自由に出られる360°展望デッキ', '🗼 勝者：エッフェル塔真下からのドラマチックな出航と未来的な全面ガラス張り')
        ]
    },
    'nl': {
        'title': 'Gedetailleerde Vergelijkingstabel per Onderdeel',
        'sub': 'De belangrijkste operationele, culinaire en logistieke verschillen tussen beide rederijen.',
        'th_feature': 'Geverifieerd Kenmerk',
        'th_a': '🏆 Bateaux Mouches Diner',
        'th_b': '🗼 Bateaux Parisiens Diner',
        'rows': [
            ('Vanafprijs', '€115 (Prestige 3-gangen) / €165 (Excellence 4-gangen)', '€85 (18:15 uur) / €109 (Étoile) / €139–€179 (Privilège) / €215 (Premier)'),
            ('Vertreksteiger', '📍 Pont de l\'Alma Pier (Port de la Conférence, 8e arr.)', '📍 Eiffeltoren Pier 5/7 (Port de la Bourdonnais, 7e arr.)'),
            ('Vaarduur', '⏱️ 2 uur en 15 minuten (20:30 uur)', '⏱️ 2 uur en 30 minuten (20:30 uur) / 1u 15m (18:15 uur)'),
            ('Scheepsarchitectuur', 'Klassiek ruim schip, sterrenhemel plafond, messing details', 'Modern volledig glazen trimaran met panoramisch gebogen dak'),
            ('Bovendek in de open lucht', '✅ Volledig 360° openlucht panoramadek toegankelijk tijdens hele vaart', '❌ Alleen gesloten salon (geen toegang tot het buitendek tijdens diner)'),
            ('Live entertainment', '🎻 Live viool- en vleugelpianoduo (romantisch klassiek repertoire)', '🎤 Live zangeres & keyboard (moderne lounge en internationale pop)'),
            ('Keuken & Bereiding', '🍽️ 100% vers bereid in eigen scheepskeuken (hoogwaardig 4-gangen diner)', '🍽️ Aan boord bereid (betrouwbare eigentijdse Franse gastronomie)'),
            ('Raamplaatsgarantie', 'Uitstekend zicht vanaf alle tafels; voorrang raamplaats bij Excellence', 'Strikte zoneprijzen (Étoile midden; Privilège & Premier aan raam)'),
            ('Kledingvoorschrift', 'Smart casual (jasje aanbevolen; geen sportkleding of sneakers)', 'Smart casual (geen korte broeken, slippers of sportkleding)'),
            ('Kinderbeleid', 'Baby\'s 0–3 jaar gratis; Kindermenu €37 (4–12 jaar)', 'Baby\'s 0–3 jaar gratis; 66% korting op Étoile-ticket (0–11 jaar)'),
            ('Wi-Fi aan boord', '❌ Geen Wi-Fi aan boord', '✅ Gratis Wi-Fi aan boord'),
            ('Het Oordeel van de Detective', '🏆 WINNAAR: Klassieke romantiek, superieur eten & 360° openluchtdak', '🗼 WINNAAR: Vertrek direct onder de Eiffeltoren & spectaculaire glazen koepel')
        ]
    },
    'pl': {
        'title': 'Szczegółowa Tabela Porównawcza Punkt po Punkcie',
        'sub': 'Kluczowe różnice operacyjne, kulinarne i logistyczne pomiędzy obydwoma armatorami.',
        'th_feature': 'Zweryfikowana Cecha',
        'th_a': '🏆 Bateaux Mouches Kolacja',
        'th_b': '🗼 Bateaux Parisiens Kolacja',
        'rows': [
            ('Cena wyjściowa', '115 € (Prestige 3 dania) / 165 € (Excellence 4 dania)', '85 € (18:15) / 109 € (Étoile) / 139–179 € (Privilège) / 215 € (Premier)'),
            ('Przystań początkowa', '📍 Przystań Pont de l\'Alma (Port de la Conférence, 8. dzielnica)', '📍 Przystań pod Wieżą Eiffla Pier 5/7 (Port de la Bourdonnais, 7. dzielnica)'),
            ('Czas trwania rejsu', '⏱️ 2 godziny 15 minut (20:30)', '⏱️ 2 godziny 30 minut (20:30) / 1h 15m (18:15)'),
            ('Architektura statku', 'Klasyczny przestronny statek, sufit ze światełkami gwiazd, mosiądz i drewno', 'Nowoczesny w 100% przeszklony trimaran z panoramicznym dachem'),
            ('Otwarte górne pokłady', '✅ Pełny otwarty taras widokowy 360° dostępny przez cały czas trwania rejsu', '❌ Tylko zamknięty salon (brak wyjścia na górny pokład w trakcie kolacji)'),
            ('Muzyka na żywo', '🎻 Duet skrzypce i fortepian na żywo (romantyczny repertuar klasyczny)', '🎤 Wokalistka i instrumenty klawiszowe na żywo (elegancki pop i lounge)'),
            ('Kuchnia i przygotowanie', '🍽️ 100% gotowane na bieżąco w kuchni pokładowej (wykwintna kuchnia 4 dania)', '🍽️ Przygotowywane na pokładzie (smaczna współczesna kuchnia francuska)'),
            ('Gwarancja stolika przy oknie', 'Świetna widoczność z każdego stolika; priorytet okna w pakiecie Excellence', 'Sztywny podział cenowy na strefy (Étoile środek; Privilège/Premier okno)'),
            ('Dress code', 'Smart casual (zalecana marynarka; zakaz strojów sportowych i sneakersów)', 'Smart casual (zakaz krótkich spodenek, klapek i dresów)'),
            ('Zasady dla dzieci', 'Dzieci 0–3 lat bezpłatnie; Menu dziecięce 37 € (4–12 lat)', 'Dzieci 0–3 lat bezpłatnie; 66% zniżki na bilet Étoile (0–11 lat)'),
            ('Wi-Fi na statku', '❌ Brak Wi-Fi na pokładzie', '✅ Bezpłatne Wi-Fi na pokładzie'),
            ('Werdykt Detektywa', '🏆 ZWYCIĘZCA: Klasyczny romantyzm, wybitna kuchnia i taras 360° na dachu', '🗼 ZWYCIĘZCA: Wypłynięcie spod samej Wieży Eiffla i nowoczesna szklana kopuła')
        ]
    },
    'ro': {
        'title': 'Tabel Comparativ Detaliat Caracteristică cu Caracteristică',
        'sub': 'Principalele diferențe operaționale, culinare și logistice între cele două companii.',
        'th_feature': 'Caracteristică Verificată',
        'th_a': '🏆 Cină Bateaux Mouches',
        'th_b': '🗼 Cină Bateaux Parisiens',
        'rows': [
            ('Preț de pornire', '115 € (Prestige 3 feluri) / 165 € (Excellence 4 feluri)', '85 € (ora 18:15) / 109 € (Étoile) / 139–179 € (Privilège) / 215 € (Premier)'),
            ('Ponton de îmbarcare', '📍 Pontonul Pont de l\'Alma (Port de la Conférence, arondismentul 8)', '📍 Pontonul Turnul Eiffel Pier 5/7 (Port de la Bourdonnais, arond. 7)'),
            ('Durata croazierei', '⏱️ 2 ore și 15 minute (plecare 20:30)', '⏱️ 2 ore și 30 minute (plecare 20:30) / 1h 15m (18:15)'),
            ('Arhitectura vasului', 'Vas clasic spațios, tavan cu luminițe stelare, lambriuri din lemn și alamă', 'Trimaran modern complet vitrat cu acoperiș panoramic curbat'),
            ('Punte superioară în aer liber', '✅ Punte exterioară 360° complet deschisă și accesibilă pe tot parcursul cinei', '❌ Doar salon interior închis (fără acces pe terasă în timpul cinei)'),
            ('Muzică live', '🎻 Duet live Vioară & Pian cu coadă (repertoriu clasic romantic)', '🎤 Cântăreață live & orgă (repertoriu modern de muzică internațională)'),
            ('Bucătărie & Preparare', '🍽️ 100% gătit proaspăt la bord în bucătărie proprie (gastronomie rafinată)', '🍽️ Pregătit la bord (gastronomie franceză contemporană de încredere)'),
            ('Masă la fereastră', 'Vizibilitate excelentă de la orice masă; prioritate la geam la pachetul Excellence', 'Tarifare strictă pe zone (Étoile în centru; Privilège/Premier la fereastră)'),
            ('Cod vestimentar', 'Smart casual (sacou recomandat; fără haine sport sau adidași)', 'Smart casual (fără pantaloni scurți, șlapi sau treninguri)'),
            ('Politica pentru copii', 'Copii 0–3 ani gratuit; Meniu copii 37 € (4–12 ani)', 'Copii 0–3 ani gratuit; 66% reducere la biletul Étoile (0–11 ani)'),
            ('Wi-Fi la bord', '❌ Fără Wi-Fi la bord', '✅ Wi-Fi gratuit la bord'),
            ('Verdictul Detectivului', '🏆 CÂȘTIGĂTOR: Romantism clasic parizian, mâncare superioară & punte deschisă 360°', '🗼 CÂȘTIGĂTOR: Plecare direct de sub Turnul Eiffel & cupolă futuristă din sticlă')
        ]
    }
}

PAGE_TEXT_I18N = {
    'fr': {
        'bc_home': 'Accueil',
        'bc_parent': 'Croisières Dîner Paris',
        'kicker': '✓ 2026 Testé sur le terrain',
        'author_line': 'Par <a href="/fr/a-propos" target="_blank">Adam Dimitrov</a> — Fondateur & Enquêteur en chef',
        'author_role': 'Tests indépendants sur le terrain • Photos & Vidéos originales • Avis impartiaux',
        'updated': 'Dernière mise à jour : 1 nov. 2026',
        'toc_title': 'Table des matières',
        'breakdown_title': 'Comparatif Direct & Audits Détaillés sur le Terrain',
        'breakdown_sub': 'Évaluation indépendante sous couverture de la gastronomie, des places, de la musique live et des tarifs.',
        'btn_expand': 'Tout afficher',
        'btn_collapse': 'Tout masquer',
        'pros': 'Avantages :',
        'cons': 'Inconvénients :',
        'read_review': 'Lire l\'avis complet ↓'
    },
    'de': {
        'bc_home': 'Startseite',
        'bc_parent': 'Seine Dinner-Kreuzfahrten',
        'kicker': '✓ 2026 Im Feld getesteter Vergleich',
        'author_line': 'Von <a href="/de/uber-uns" target="_blank">Adam Dimitrov</a> — Gründer & Chefermittler',
        'author_role': 'Unabhängige Tests vor Ort • Eigene Fotos & Videos • Ehrliche Urteile',
        'updated': 'Zuletzt aktualisiert: 1. Nov. 2026',
        'toc_title': 'Inhaltsverzeichnis',
        'breakdown_title': 'Direkter Schiffsvergleich & Detaillierte Vor-Ort-Audits',
        'breakdown_sub': 'Unabhängige Prüfung von Menüqualität, Fensterplätzen, Live-Musik und Preis-Leistung.',
        'btn_expand': 'Alle ausklappen',
        'btn_collapse': 'Alle einklappen',
        'pros': 'Vorteile:',
        'cons': 'Nachteile:',
        'read_review': 'Ganze Rezension lesen ↓'
    },
    'es': {
        'bc_home': 'Inicio',
        'bc_parent': 'Cruceros con Cena en París',
        'kicker': '✓ 2026 Comparación probada en campo',
        'author_line': 'Por <a href="/es/acerca" target="_blank">Adam Dimitrov</a> — Fundador e Investigador Principal',
        'author_role': 'Evaluación en persona • Fotos y vídeos originales • Opiniones imparciales',
        'updated': 'Última actualización: 1 de nov. de 2026',
        'toc_title': 'Tabla de contenidos',
        'breakdown_title': 'Comparación Directa y Auditoría Detallada en el Terreno',
        'breakdown_sub': 'Evaluación independiente y anónima de la gastronomía, las vistas, la música en vivo y las tarifas.',
        'btn_expand': 'Expandir todo',
        'btn_collapse': 'Contraer todo',
        'pros': 'Ventajas:',
        'cons': 'Inconvenientes:',
        'read_review': 'Leer reseña completa ↓'
    },
    'it': {
        'bc_home': 'Home',
        'bc_parent': 'Crociere con Cena a Parigi',
        'kicker': '✓ 2026 Confronto testato sul campo',
        'author_line': 'Di <a href="/it/su-di-noi" target="_blank">Adam Dimitrov</a> — Fondatore e Investigatore Principale',
        'author_role': 'Testato sul campo • Foto e video originali • Recensioni indipendenti',
        'updated': 'Ultimo aggiornamento: 1 nov 2026',
        'toc_title': 'Indice dei contenuti',
        'breakdown_title': 'Confronto Diretto & Verifiche Approfondite sul Campo',
        'breakdown_sub': 'Valutazione indipendente di qualità del cibo, posti a sedere, musica dal vivo e rapporto qualità/prezzo.',
        'btn_expand': 'Espandi tutto',
        'btn_collapse': 'Comprimi tutto',
        'pros': 'Vantaggi:',
        'cons': 'Svantaggi:',
        'read_review': 'Leggi recensione completa ↓'
    },
    'ja': {
        'bc_home': 'ホーム',
        'bc_parent': 'パリのディナークルーズ',
        'kicker': '✓ 2026 現地実地検証済み比較',
        'author_line': '著者：<a href="/ja/について" target="_blank">Adam Dimitrov</a> — 創設者 兼 主席調査員',
        'author_role': '自費実地テスト実施 • オリジナル写真・動画収録 • 中立な徹底検証',
        'updated': '最終更新日：2026年11月1日',
        'toc_title': '目次',
        'breakdown_title': '徹底直接対決＆現地実地検証レポート',
        'breakdown_sub': '料理の味、座席の眺望、生演奏、料金設定を自費で潜入調査した客観的レポート。',
        'btn_expand': 'すべて展開',
        'btn_collapse': 'すべて折りたたむ',
        'pros': 'メリット（長所）：',
        'cons': 'デメリット（注意点）：',
        'read_review': '詳細レビューを読む ↓'
    },
    'nl': {
        'bc_home': 'Home',
        'bc_parent': 'Seine Dinercruises Parijs',
        'kicker': '✓ 2026 Getest in de praktijk',
        'author_line': 'Door <a href="/nl/over-uns" target="_blank">Adam Dimitrov</a> — Oprichter & Hoofdonderzoeker',
        'author_role': 'Zelf getest in het veld • Originele foto\'s en video\'s • Onafhankelijke reviews',
        'updated': 'Laatst bijgewerkt: 1 nov. 2026',
        'toc_title': 'Inhoudsopgave',
        'breakdown_title': 'Directe Vergelijking & Diepgaande Veldinspecties',
        'breakdown_sub': 'Onafhankelijke evaluatie van voedselkwaliteit, uitzicht, live muziek en ticketprijzen.',
        'btn_expand': 'Alles uitvouwen',
        'btn_collapse': 'Alles inklappen',
        'pros': 'Voordelen:',
        'cons': 'Nadelen:',
        'read_review': 'Volledige review lezen ↓'
    },
    'pl': {
        'bc_home': 'Strona główna',
        'bc_parent': 'Rejsy z kolacją Paryż',
        'kicker': '✓ 2026 Porównanie przetestowane w terenie',
        'author_line': 'Autor: <a href="/pl/o" target="_blank">Adam Dimitrov</a> — Założyciel i Główny Detektyw',
        'author_role': 'Osobiste testy w terenie • Oryginalne zdjęcia i filmy • Niezależne recenzje',
        'updated': 'Ostatnia aktualizacja: 1 listopada 2026',
        'toc_title': 'Spis treści',
        'breakdown_title': 'Bezpośrednie Porównanie & Szczegółowe Audyty Pokładowe',
        'breakdown_sub': 'Niezależna ocena jakości posiłków, widoków z okien, muzyki na żywo oraz opłacalności biletów.',
        'btn_expand': 'Rozwiń wszystko',
        'btn_collapse': 'Zwiń wszystko',
        'pros': 'Zalety:',
        'cons': 'Wady:',
        'read_review': 'Przeczytaj całą recenzję ↓'
    },
    'ro': {
        'bc_home': 'Acasă',
        'bc_parent': 'Croaziere cu Cină Paris',
        'kicker': '✓ 2026 Comparație testată pe teren',
        'author_line': 'De <a href="/ro/despre" target="_blank">Adam Dimitrov</a> — Fondator și Investigator Șef',
        'author_role': 'Testare personală pe teren • Fotografii și clipuri originale • Recenzii independente',
        'updated': 'Ultima actualizare: 1 nov. 2026',
        'toc_title': 'Cuprins',
        'breakdown_title': 'Comparație Directă & Audituri Detaliate pe Teren',
        'breakdown_sub': 'Evaluare independentă sub acoperire a preparatelor culinare, poziționării meselor, muzicii live și tarifelor.',
        'btn_expand': 'Extinde tot',
        'btn_collapse': 'Restrânge tot',
        'pros': 'Avantaje:',
        'cons': 'Dezavantaje:',
        'read_review': 'Citește recenzia completă ↓'
    }
}

def build_matrix_html(lang):
    m = MATRIX_I18N[lang]
    rows_html = []
    for feat, val_a, val_b in m['rows']:
        rows_html.append(f'''
    <tr>
      <td class="ltt-duel-td-feature">{feat}</td>
      <td class="ltt-duel-td-a">{val_a}</td>
      <td class="ltt-duel-td-b">{val_b}</td>
    </tr>''')

    return f'''
<div class="ltt-duel-matrix-wrap" id="duel-matrix" style="margin-top: 36px;">
  <div class="ltt-duel-matrix-header" style="text-align: center; margin-bottom: 20px;">
    <span class="ltt-matrix-kicker" style="color: #dfa732; font-weight: 800; font-size: 11px; letter-spacing: 0.1em; text-transform: uppercase;">⚖️ {m['th_feature'].upper()}</span>
    <h3 class="ltt-duel-matrix-title" style="font-size: 24px; font-weight: 800; color: #0f172a; margin: 8px 0 6px 0;">{m['title']}</h3>
    <p class="ltt-duel-matrix-sub" style="font-size: 14px; color: #64748b; margin: 0 auto; max-width: 600px;">{m['sub']}</p>
  </div>
  <div class="ltt-duel-table-responsive" style="overflow-x: auto; background: #fff; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.05);">
    <table class="ltt-duel-table" style="width: 100%; border-collapse: collapse; text-align: left; font-size: 14px;">
      <thead>
        <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0;">
          <th class="ltt-duel-th-feature" style="padding: 16px; font-weight: 700; color: #475569; width: 25%;">{m['th_feature']}</th>
          <th class="ltt-duel-th-a" style="padding: 16px; font-weight: 800; color: #0f172a; width: 37.5%; border-left: 1px solid #e2e8f0;">{m['th_a']}</th>
          <th class="ltt-duel-th-b" style="padding: 16px; font-weight: 800; color: #0f172a; width: 37.5%; border-left: 1px solid #e2e8f0;">{m['th_b']}</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows_html)}
      </tbody>
    </table>
  </div>
</div>'''

def build_duel_page(lang, rel_path):
    abs_path = os.path.join(BASE_DIR, rel_path)
    print(f"\nBuilding perfected Duel page for [{lang.upper()}]: {rel_path} ...")
    
    # 1. Fetch original content before 0e6ce9a
    raw_orig = subprocess.check_output(['git', 'show', f'0e6ce9a~1:{rel_path}'], text=True)
    orig_soup = BeautifulSoup(raw_orig, 'html.parser')
    
    # Extract head metadata
    head = orig_soup.find('head')
    title = head.find('title').get_text(strip=True) if head.find('title') else "Bateaux Mouches vs. Bateaux Parisiens"
    meta_desc_tag = head.find('meta', {'name': 'description'})
    meta_desc = meta_desc_tag.get('content', '') if meta_desc_tag else ""
    canonical_tag = head.find('link', rel='canonical')
    canonical_href = canonical_tag.get('href') if canonical_tag else f"https://www.thecruisedetective.com/{rel_path.replace('/index.html', '')}"

    # Extract H1 and lead copy
    h1_tag = orig_soup.find('h1')
    h1_text = h1_tag.get_text(strip=True) if h1_tag else "Bateaux Mouches vs. Bateaux Parisiens"
    
    containers = orig_soup.find_all(class_='container')
    lead_copy_html = ""
    if containers and len(containers) > 0:
        lead_copy_html = ''.join(str(p) for p in containers[0].find_all('p'))
    if not lead_copy_html:
        lead_copy_html = "<p>Compare Paris's two most famous Seine dinner cruises side-by-side to choose the perfect boat for your evening.</p>"

    # Extract article breakdown sections from containers[1]
    article_html = ""
    if len(containers) > 1:
        # Wrap each h2 and its following siblings until next h2
        c1 = containers[1]
        article_html = str(c1)

    # 2. Get current live navbar and footer for this language
    with open(abs_path, 'r', encoding='utf-8') as f:
        cur_soup = BeautifulSoup(f.read(), 'html.parser')
    
    navbar = cur_soup.find('header', class_='ltt-navbar')
    navbar_html = str(navbar) if navbar else ""
    
    footer = cur_soup.find('section', class_='footer-dark')
    footer_html = str(footer) if footer else ""

    t = PAGE_TEXT_I18N[lang]
    d = DUEL_I18N[lang]

    # Contender 1 & 2 URLs
    tiqets_mouches = "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-on-the-seine-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=vs-deck-mouches"
    tiqets_parisiens = "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-on-the-seine-river-bateaux-parisiens-p974358/?partner=thecruisedetective.com-176436&tq_campaign=vs-deck-parisiens"

    # Duel Grid HTML
    duel_grid_html = f'''
  <div class="ltt-duel-grid" id="ltt-cards-deck">
    <!-- CONTENDER 1: MOUCHES -->
    <div class="bpa-card ltt-duel-card" data-cat="mouches" id="duel-card-1">
      <div class="ltt-duel-card-header">
        <span class="bpa-rank-tag bpa-gold" style="font-size: 11.5px; padding: 5px 12px; font-weight: 800; border-radius: 9999px;">{d['c1_tag']}</span>
      </div>
      <div class="bpa-media" style="margin-top: 10px; border-radius: 12px; overflow: hidden; position: relative;">
        <button aria-label="Previous photo" class="bpa-arrow prev" onclick="bpaSlide(this,-1)" type="button">‹</button>
        <button aria-label="Next photo" class="bpa-arrow next" onclick="bpaSlide(this,1)" type="button">›</button>
        <span class="bpa-pill">1 / 4</span>
        <div class="bpa-slider" onscroll="bpaCount(this)">
          <img alt="Bateaux Mouches Dinner Cruise" class="bpa-slide" loading="eager" src="/assets/cdn/652d0405192ba076b04f74a3/6557d7488c95f4ddb81c828e_Bateaux-mouches-dinner-cruise%20(15).webp"/>
          <img alt="Bateaux Mouches Table Setting" class="bpa-slide" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/6557d4919c0214cc0fedf303_Bateaux-mouches-dinner-cruise%20(11).webp"/>
          <img alt="Bateaux Mouches Gastronomy Menu" class="bpa-slide" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/6557d4b0f32b0baf412f95f5_Bateaux-mouches-dinner-cruise%20(7).webp"/>
          <img alt="Bateaux Mouches Open Top Deck" class="bpa-slide" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/6557d53788f84266f7d4d3fd_Bateaux-mouches-dinner-cruise%20(9).webp"/>
        </div>
      </div>
      <div class="bpa-info" style="padding: 16px 0 0 0;">
        <div class="bpa-kicker" style="font-size: 12px; font-weight: 700; color: #64748b; margin-bottom: 6px;">{d['c1_kicker']}</div>
        <h3 class="bpa-title" style="font-size: 20px; font-weight: 800; color: #0f172a; margin: 0 0 10px 0; line-height: 1.3;">{d['c1_title']}</h3>
        <div class="bpa-proof" style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
          <span style="color: #dfa732; font-size: 15px; letter-spacing: 2px;">★★★★★</span>
          <span style="font-weight: 800; font-size: 14px; color: #0f172a;">4.8 / 5.0</span>
          <span style="color: #64748b; font-size: 12px;">(14,200+ Reviews)</span>
          <span class="bpa-vchip" style="font-size: 11px; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 9999px; font-weight: 700;">✓ Verified</span>
        </div>
        <div class="ltt-duel-specs-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 14px;">
          <span class="ltt-duel-spec-pill" style="font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 10px; border-radius: 8px; color: #334155;">🕒 {d['c1_dep']}</span>
          <span class="ltt-duel-spec-pill" style="font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 10px; border-radius: 8px; color: #334155;">⏱️ {d['c1_dur']}</span>
          <span class="ltt-duel-spec-pill" style="font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 10px; border-radius: 8px; color: #334155;">🎻 {d['c1_music']}</span>
          <span class="ltt-duel-spec-pill" style="font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 10px; border-radius: 8px; color: #334155;">🪟 {d['c1_seat']}</span>
        </div>
        <div class="ltt-duel-bestfor" style="font-size: 13px; line-height: 1.5; color: #475569; background: #f8fafc; border-left: 3px solid #dfa732; padding: 10px 14px; border-radius: 0 8px 8px 0; margin-bottom: 16px;">
          🎯 <strong>{d['lbl_best']}:</strong> {d['c1_best']}
        </div>
      </div>
      <div class="bpa-cta-cell" style="padding-top: 14px; border-top: 1px solid #e2e8f0;">
        <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 10px;">
          <div class="bpa-price" style="font-size: 24px; font-weight: 800; color: #0f172a;">{d['c1_price']}</div>
          <div class="bpa-psub" style="font-size: 12px; color: #64748b;">Prestige €130 • Excellence €155</div>
        </div>
        <a class="bpa-btn" href="{tiqets_mouches}" rel="noopener nofollow sponsored" target="_blank" style="display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #dfa732 0%, #b88214 100%) !important; color: #fff !important; font-weight: 800; padding: 13px 20px; border-radius: 9999px !important; text-decoration: none; box-shadow: 0 4px 14px rgba(223, 167, 50, 0.35); transition: transform 0.15s ease;">
          {d['c1_btn']}
        </a>
        <div class="bpa-trust-micro" style="font-size: 11.5px; color: #64748b; margin-top: 8px; text-align: center;">{d['c1_guar']}</div>
        <a class="bpa-sublink" href="#1-bateaux-mouches" style="display: block; text-align: center; margin-top: 8px; font-size: 12px; font-weight: 700; color: #0f172a; text-decoration: underline;">{t['read_review']}</a>
      </div>
    </div>

    <!-- CONTENDER 2: PARISIENS -->
    <div class="bpa-card ltt-duel-card" data-cat="parisiens" id="duel-card-2">
      <div class="ltt-duel-card-header">
        <span class="bpa-rank-tag bpa-gold" style="font-size: 11.5px; padding: 5px 12px; font-weight: 800; border-radius: 9999px;">{d['c2_tag']}</span>
      </div>
      <div class="bpa-media" style="margin-top: 10px; border-radius: 12px; overflow: hidden; position: relative;">
        <button aria-label="Previous photo" class="bpa-arrow prev" onclick="bpaSlide(this,-1)" type="button">‹</button>
        <button aria-label="Next photo" class="bpa-arrow next" onclick="bpaSlide(this,1)" type="button">›</button>
        <span class="bpa-pill">1 / 4</span>
        <div class="bpa-slider" onscroll="bpaCount(this)">
          <img alt="Bateaux Parisiens Curvilinear Glass Vessel" class="bpa-slide" loading="eager" src="/assets/cdn/652d0405192ba076b04f74a3/6557453e8a6348c194b21d69_DSC03716.webp"/>
          <img alt="Bateaux Parisiens Table Sightlines" class="bpa-slide" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/6557452eedc0759fd61fd2eb_DSC03746.webp"/>
          <img alt="Bateaux Parisiens Live Vocalist" class="bpa-slide" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/653e67da33c8ccff6d081df9_bateaux-parisiens-dinner-cruise%20(12).webp"/>
          <img alt="Bateaux Parisiens Eiffel Tower Boarding" class="bpa-slide" loading="lazy" src="/assets/cdn/652d0405192ba076b04f74a3/653e6827827717b4f627f685_bateaux-parisiens-dinner-cruise%20(3).webp"/>
        </div>
      </div>
      <div class="bpa-info" style="padding: 16px 0 0 0;">
        <div class="bpa-kicker" style="font-size: 12px; font-weight: 700; color: #64748b; margin-bottom: 6px;">{d['c2_kicker']}</div>
        <h3 class="bpa-title" style="font-size: 20px; font-weight: 800; color: #0f172a; margin: 0 0 10px 0; line-height: 1.3;">{d['c2_title']}</h3>
        <div class="bpa-proof" style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
          <span style="color: #dfa732; font-size: 15px; letter-spacing: 2px;">★★★★☆</span>
          <span style="font-weight: 800; font-size: 14px; color: #0f172a;">4.6 / 5.0</span>
          <span style="color: #64748b; font-size: 12px;">(22,400+ Reviews)</span>
          <span class="bpa-vchip" style="font-size: 11px; background: #e0f2fe; color: #0369a1; padding: 2px 8px; border-radius: 9999px; font-weight: 700;">✓ Verified</span>
        </div>
        <div class="ltt-duel-specs-grid" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 6px; margin-bottom: 14px;">
          <span class="ltt-duel-spec-pill" style="font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 10px; border-radius: 8px; color: #334155;">🕒 {d['c2_dep']}</span>
          <span class="ltt-duel-spec-pill" style="font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 10px; border-radius: 8px; color: #334155;">⏱️ {d['c2_dur']}</span>
          <span class="ltt-duel-spec-pill" style="font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 10px; border-radius: 8px; color: #334155;">🎤 {d['c2_music']}</span>
          <span class="ltt-duel-spec-pill" style="font-size: 12px; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6px 10px; border-radius: 8px; color: #334155;">🪟 {d['c2_seat']}</span>
        </div>
        <div class="ltt-duel-bestfor" style="font-size: 13px; line-height: 1.5; color: #475569; background: #f8fafc; border-left: 3px solid #dfa732; padding: 10px 14px; border-radius: 0 8px 8px 0; margin-bottom: 16px;">
          🎯 <strong>{d['lbl_best']}:</strong> {d['c2_best']}
        </div>
      </div>
      <div class="bpa-cta-cell" style="padding-top: 14px; border-top: 1px solid #e2e8f0;">
        <div style="display: flex; align-items: baseline; gap: 8px; margin-bottom: 10px;">
          <div class="bpa-price" style="font-size: 24px; font-weight: 800; color: #0f172a;">{d['c2_price']}</div>
          <div class="bpa-psub" style="font-size: 12px; color: #64748b;">Étoile €109 • Privilège €139–€179 • Premier €215</div>
        </div>
        <a class="bpa-btn" href="{tiqets_parisiens}" rel="noopener nofollow sponsored" target="_blank" style="display: block; width: 100%; text-align: center; background: linear-gradient(135deg, #dfa732 0%, #b88214 100%) !important; color: #fff !important; font-weight: 800; padding: 13px 20px; border-radius: 9999px !important; text-decoration: none; box-shadow: 0 4px 14px rgba(223, 167, 50, 0.35); transition: transform 0.15s ease;">
          {d['c2_btn']}
        </a>
        <div class="bpa-trust-micro" style="font-size: 11.5px; color: #64748b; margin-top: 8px; text-align: center;">{d['c2_guar']}</div>
        <a class="bpa-sublink" href="#2-bateaux-parisiens" style="display: block; text-align: center; margin-top: 8px; font-size: 12px; font-weight: 700; color: #0f172a; text-decoration: underline;">{t['read_review']}</a>
      </div>
    </div>
  </div>'''

    matrix_html = build_matrix_html(lang)

    # 3. Assemble Complete Clean Page HTML
    page_html = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
  <style id="cd-kill-webflow-badge">
  .w-webflow-badge, a.w-webflow-badge, [class*="w-webflow-badge"], a[href*="webflow.com?utm_campaign=brandjs"], a[href*="webflow.com/?utm_campaign=brandjs"] {{
    display: none !important; opacity: 0 !important; visibility: hidden !important; pointer-events: none !important;
    position: absolute !important; top: -99999px !important; left: -99999px !important; width: 0 !important; height: 0 !important; z-index: -99999 !important;
  }}
  </style>
  <style id="cd-universal-pill-buttons">
  .ltt-btn-gold, .bpa-btn, .ltt-buy-btn, .ltt-sticky-cta, a[href*="tiqets.com"][class*="btn"], a[href*="getyourguide.com"][class*="btn"] {{
    border-radius: 9999px !important;
    background: linear-gradient(135deg, #dfa732 0%, #b88214 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(223, 167, 50, 0.35) !important;
    transition: transform 0.15s ease, box-shadow 0.15s ease !important;
  }}
  .ltt-btn-gold:hover, .bpa-btn:hover, .ltt-buy-btn:hover, .ltt-sticky-cta:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(223, 167, 50, 0.45) !important;
  }}
  </style>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <meta content="{meta_desc}" name="description"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link rel="canonical" href="{canonical_href}"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Open+Sans:ital,wght@0,400;0,600;0,700;0,800;1,400;1,600;1,700&display=swap" rel="stylesheet"/>
  <link href="/css/editorial-luxury.css" rel="stylesheet"/>
  <link href="/assets/cdn/652d0405192ba076b04f74a3/6570a893c546e01463861a82_favicon-cruise-detective.png" rel="shortcut icon" type="image/x-icon"/>
  <link href="/assets/cdn/652d0405192ba076b04f74a3/6570a89c8c97ba4e084ac5d5_webclip-cruise-detective.png" rel="apple-touch-icon"/>
  <script>(function(w,i,g){{w[g]=w[g]||[];if(typeof w[g].push=='function')w[g].push.apply(w[g],Array.isArray(i)?i:[i]);}})(window,['G-RN34XFKPQ6'],'google_tags_first_party');</script>
  <script async="" src="https://www.googletagmanager.com/gtag/js?id=G-RN34XFKPQ6"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-RN34XFKPQ6');
  </script>
</head>
<body>
{navbar_html}

<script id="ltt-nav-script">
(function() {{
  function initNav() {{
    var toggle = document.getElementById('lttNavToggle');
    var drawer = document.getElementById('lttMobileDrawer');
    var dropdown = document.getElementById('lttExploreDropdown') || document.getElementById('lttDestinationsDropdown');
    var dropBtn = dropdown ? dropdown.querySelector('.ltt-dropdown-btn') : null;

    if (toggle && drawer) {{
      toggle.addEventListener('click', function(e) {{
        e.stopPropagation();
        var isOpen = drawer.classList.contains('is-open');
        drawer.classList.toggle('is-open', !isOpen);
        toggle.classList.toggle('is-active', !isOpen);
        toggle.setAttribute('aria-expanded', !isOpen ? 'true' : 'false');
        drawer.setAttribute('aria-hidden', !isOpen ? 'false' : 'true');
      }});
      drawer.querySelectorAll('a').forEach(function(link) {{
        link.addEventListener('click', function() {{
          drawer.classList.remove('is-open');
          toggle.classList.remove('is-active');
          toggle.setAttribute('aria-expanded', 'false');
          drawer.setAttribute('aria-hidden', 'true');
        }});
      }});
    }}
    if (dropBtn && dropdown) {{
      dropBtn.addEventListener('click', function(e) {{
        e.stopPropagation();
        var open = dropdown.classList.toggle('is-open');
        dropBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      }});
    }}
    document.addEventListener('click', function(e) {{
      if (drawer && drawer.classList.contains('is-open') && !drawer.contains(e.target) && (!toggle || !toggle.contains(e.target))) {{
        drawer.classList.remove('is-open');
        if (toggle) {{
          toggle.classList.remove('is-active');
          toggle.setAttribute('aria-expanded', 'false');
        }}
        drawer.setAttribute('aria-hidden', 'true');
      }}
      if (dropdown && dropdown.classList.contains('is-open') && !dropdown.contains(e.target)) {{
        dropdown.classList.remove('is-open');
        if (dropBtn) dropBtn.setAttribute('aria-expanded', 'false');
      }}
    }});
  }}
  if (document.readyState === 'loading') {{
    document.addEventListener('DOMContentLoaded', initNav);
  }} else {{
    initNav();
  }}
}})();
</script>

<style id="ltt-hero-card-styles">
.ltt-hero-wrap {{
  width: 100% !important;
  max-width: 1240px !important;
  margin: 22px auto 0 !important;
  padding: 0 16px !important;
  box-sizing: border-box !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
  color: #0f172a !important;
}}
.ltt-clean-card {{
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  padding: 26px 32px 24px 32px;
  box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.05), 0 1px 3px rgba(15, 23, 42, 0.02);
  box-sizing: border-box;
}}
.ltt-top-bar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}}
.ltt-breadcrumbs {{
  display: inline-flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12.5px;
  font-weight: 600;
  color: #64748b;
  margin: 0;
}}
.ltt-breadcrumbs a {{
  color: #475569 !important;
  text-decoration: none !important;
  transition: color 0.15s ease;
}}
.ltt-breadcrumbs a:hover {{
  color: #dfa732 !important;
  text-decoration: underline !important;
}}
.ltt-breadcrumbs .ltt-bc-sep {{
  color: #cbd5e1;
  font-size: 11px;
}}
.ltt-breadcrumbs .ltt-bc-current {{
  color: #0f172a;
  font-weight: 700;
}}
.ltt-hero-kicker-badge {{
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #785208;
  background: #fdfaf2;
  border: 1px solid #f2e0b6;
  padding: 4px 10px;
  border-radius: 999px;
}}
.ltt-editorial-h1 {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
  font-size: clamp(26px, 3vw, 36px) !important;
  font-weight: 800 !important;
  line-height: 1.18 !important;
  letter-spacing: -0.025em !important;
  color: #0f172a !important;
  margin: 0 0 14px 0 !important;
  text-align: left !important;
}}
.ltt-trust-bar {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  margin-bottom: 14px;
}}
.ltt-author-cluster {{
  display: flex;
  align-items: center;
  gap: 12px;
}}
.ltt-author-avatar-wrap {{
  position: relative;
  width: 42px;
  height: 42px;
  flex-shrink: 0;
}}
.ltt-author-avatar {{
  width: 42px !important;
  height: 42px !important;
  max-width: none !important;
  border-radius: 50% !important;
  object-fit: cover !important;
  border: 2px solid #dfa732 !important;
  display: block !important;
  margin: 0 !important;
}}
.ltt-author-meta {{
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: left;
}}
.ltt-author-line {{
  font-size: 13.5px;
  color: #0f172a;
  font-weight: 700;
  line-height: 1.25;
}}
.ltt-author-role {{
  font-size: 12px;
  color: #64748b;
  line-height: 1.25;
}}
.ltt-lead-copy {{
  font-size: 15.5px;
  line-height: 1.65;
  color: #334155;
  margin-bottom: 16px;
}}
.ltt-lead-copy p {{
  margin: 0 0 10px 0;
}}
@media (max-width: 640px) {{
  .ltt-hero-wrap {{
    margin-top: 14px !important;
    padding: 0 12px !important;
  }}
  .ltt-clean-card {{
    padding: 20px 18px;
  }}
  .ltt-trust-bar {{
    padding: 10px 12px;
  }}
}}
</style>

<div class="ltt-hero-wrap">
  <div class="ltt-clean-card">
    <div class="ltt-top-bar">
      <nav aria-label="Breadcrumb" class="ltt-breadcrumbs">
        <a href="/{lang}/">{t['bc_home']}</a>
        <span class="ltt-bc-sep">›</span>
        <span class="ltt-bc-current">{t['bc_parent']}</span>
        <span class="ltt-bc-sep">›</span>
        <span class="ltt-bc-current">{h1_text}</span>
      </nav>
      <span class="ltt-hero-kicker-badge">{t['kicker']}</span>
    </div>
    <h1 class="ltt-editorial-h1">{h1_text}</h1>
    <div class="ltt-trust-bar">
      <div class="ltt-author-cluster">
        <div class="ltt-author-avatar-wrap">
          <img alt="Adam Dimitrov" class="ltt-author-avatar" src="/assets/adam-dimitrov.webp"/>
        </div>
        <div class="ltt-author-meta">
          <div class="ltt-author-line">{t['author_line']}</div>
          <div class="ltt-author-role">{t['author_role']}</div>
        </div>
      </div>
      <div class="ltt-trust-pills">
        <span class="ltt-trust-pill" style="font-size: 12px; font-weight: 700; color: #475569;">{t['updated']}</span>
      </div>
    </div>
    <div class="ltt-lead-copy">
      {lead_copy_html}
    </div>
  </div>
</div>

<div class="comparison-table">
  <div class="container-27">
    <style id="ltt-dubai-safari-styles">
    .comparison-table, .comparison-table .container-27 {{
      width: 100% !important;
      max-width: 1240px !important;
      margin: 0 auto !important;
      padding: 0 !important;
      box-sizing: border-box !important;
    }}
    .ltt-deck-container {{
      width: 100% !important;
      max-width: 1240px !important;
      margin: 18px auto 32px auto !important;
      padding: 0 16px !important;
      box-sizing: border-box !important;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      color: #1e293b;
    }}
    .ltt-duel-grid {{
      display: grid !important;
      grid-template-columns: repeat(2, 1fr) !important;
      gap: 24px !important;
      margin-top: 20px !important;
    }}
    .ltt-duel-card {{
      background: #ffffff !important;
      border: 1px solid #e2e8f0 !important;
      border-radius: 16px !important;
      padding: 24px !important;
      box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.05) !important;
      display: flex !important;
      flex-direction: column !important;
      justify-content: space-between !important;
    }}
    @media (max-width: 900px) {{
      .ltt-duel-grid {{
        grid-template-columns: 1fr !important;
      }}
    }}
    </style>
    <div class="ltt-deck-container" id="bm-vs-bp-comparison-deck">
      <div class="ltt-header-box" style="margin-bottom: 24px; text-align: center;">
        <span class="ltt-kicker-tag" style="color: #dfa732; font-weight: 800; letter-spacing: 0.1em; font-size: 12px; text-transform: uppercase;">HEAD-TO-HEAD SHOWDOWN</span>
        <h2 class="ltt-header-title" style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 28px; font-weight: 800; color: #0f172a; margin: 8px 0 10px 0;">{d['deck_header']}</h2>
        <p style="font-size: 15px; color: #64748b; margin: 0 auto; max-width: 680px;">{d['deck_subtitle']}</p>
      </div>
      {duel_grid_html}
      {matrix_html}
    </div>
  </div>
</div>

<div class="blog-section-2">
  <div class="container-31">
    <div class="blog-grid-2">
      <div class="content-left">
        <div class="stick-wrapper">
          <div class="title-small-6" style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em; color:var(--slate-900); margin-bottom:12px;">{t['toc_title']}</div>
          <div class="toc" id="toc"></div>
        </div>
      </div>
      <div class="content-right_blog" id="content">
        <div class="container-33 w-container">
          <div class="bpa-breakdown-top-bar" id="breakdown-header" style="margin-bottom: 24px;">
            <div>
              <h2 class="bpa-breakdown-heading" style="font-size: 26px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0;">{t['breakdown_title']}</h2>
              <p class="bpa-breakdown-sub" style="font-size: 14.5px; color: #64748b; margin: 0;">{t['breakdown_sub']}</p>
            </div>
          </div>
          
          <!-- Contender 1 Deep Dive -->
          <details class="bpa-details-card" id="1-bateaux-mouches" open="" style="background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; margin-bottom: 24px; padding: 20px; box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.05); position: relative;">
            <summary class="bpa-details-summary" style="cursor: pointer; list-style: none;">
              <div class="bpa-details-top-row" style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="bpa-rank-tag bpa-gold" style="position: static !important; font-size: 11px; padding: 4px 10px; font-weight: 800; border-radius: 9999px;">{d['c1_tag']}</span>
                <div class="bpa-kicker" style="font-size: 13px; color: #64748b;">{d['c1_kicker']}</div>
              </div>
              <h3 class="bpa-details-title" style="font-size: 22px; font-weight: 800; color: #0f172a; margin: 4px 0 6px 0;">{d['c1_title']}</h3>
            </summary>
            <div class="bpa-details-body" style="margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
              <div class="ltt-duel-bestfor" style="font-size: 14px; line-height: 1.6; color: #334155; margin-bottom: 16px;">
                🎯 <strong>{d['lbl_best']}:</strong> {d['c1_best']}
              </div>
              <a class="bpa-btn" href="{tiqets_mouches}" rel="noopener nofollow sponsored" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #dfa732 0%, #b88214 100%) !important; color: #fff !important; font-weight: 800; padding: 12px 24px; border-radius: 9999px !important; text-decoration: none; margin-top: 10px;">
                {d['c1_btn']}
              </a>
            </div>
          </details>

          <!-- Contender 2 Deep Dive -->
          <details class="bpa-details-card" id="2-bateaux-parisiens" open="" style="background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; margin-bottom: 32px; padding: 20px; box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.05); position: relative;">
            <summary class="bpa-details-summary" style="cursor: pointer; list-style: none;">
              <div class="bpa-details-top-row" style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="bpa-rank-tag bpa-gold" style="position: static !important; font-size: 11px; padding: 4px 10px; font-weight: 800; border-radius: 9999px;">{d['c2_tag']}</span>
                <div class="bpa-kicker" style="font-size: 13px; color: #64748b;">{d['c2_kicker']}</div>
              </div>
              <h3 class="bpa-details-title" style="font-size: 22px; font-weight: 800; color: #0f172a; margin: 4px 0 6px 0;">{d['c2_title']}</h3>
            </summary>
            <div class="bpa-details-body" style="margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
              <div class="ltt-duel-bestfor" style="font-size: 14px; line-height: 1.6; color: #334155; margin-bottom: 16px;">
                🎯 <strong>{d['lbl_best']}:</strong> {d['c2_best']}
              </div>
              <a class="bpa-btn" href="{tiqets_parisiens}" rel="noopener nofollow sponsored" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #dfa732 0%, #b88214 100%) !important; color: #fff !important; font-weight: 800; padding: 12px 24px; border-radius: 9999px !important; text-decoration: none; margin-top: 10px;">
                {d['c2_btn']}
              </a>
            </div>
          </details>

          <!-- Full Editorial Content -->
          <div class="ltt-editorial-wrapper" style="font-size: 16px; line-height: 1.7; color: #334155;">
            {article_html}
          </div>
        </div>
      </div>
    </div>
  </div>
</div>

{footer_html}

<aside class="hybrid-sticky-bar" id="sticky-bar">
  <div class="hybrid-sticky-inner">
    <div class="hybrid-sticky-info">
      <span class="hybrid-sticky-top-badge">🏆 TOP PICK</span>
      <span class="hybrid-sticky-title">Bateaux Mouches 20:30 Prestige</span>
      <span class="hybrid-sticky-price">{d['c1_price']}</span>
    </div>
    <div class="hybrid-sticky-actions">
      <a class="hybrid-sticky-btn ltt-sticky-cta" href="{tiqets_mouches}" rel="noopener nofollow sponsored" target="_blank">
        {d['c1_btn']}
      </a>
    </div>
  </div>
</aside>
<div class="hybrid-sheet-backdrop" id="hybridBackdrop"></div>

<script src="/js/ltt-nav.js"></script>
<script src="/webflow-sync.js"></script>
<script>
window.LTT_PAGE_CONFIG = {{
  "deckId": "bm-vs-bp-comparison-deck",
  "tocDeckLabel": "{d['deck_header']}",
  "tocBreakdownLabel": "{t['breakdown_title']}",
  "shortTitles": [
    "{d['c1_title']}",
    "{d['c2_title']}"
  ]
}};
</script>
</body>
</html>
'''

    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"[{lang.upper()}] Successfully built perfected Duel page ({len(page_html)} bytes).")

def main():
    for lang, rel_path in DUEL_PAGES.items():
        build_duel_page(lang, rel_path)

if __name__ == '__main__':
    main()
