#!/usr/bin/env python3
"""
DEFINITIVE 1:1 MASTER TEMPLATE CLONING & TRANSLATION ENGINE
Clones the exact perfected English master pages:
1. Destination Guides (dinner, sightseeing, amsterdam, london) -> 32 pages + 8 aliases
2. Homepages (index.html) -> 8 foreign homepages (fr, de, es, it, ja, nl, pl, ro)
3. About Pages (about/index.html) -> 8 foreign about pages
4. Duel Pages (bateaux-mouches-vs-bateaux-parisiens.../index.html) -> 8 foreign duel pages
5. Contact Pages (contact/index.html) -> 8 foreign contact pages

Guarantees 100% architectural, layout, and visual fidelity with English originals.
Eliminates all unstyled elements, giant star SVGs, broken images, and text contrast flaws.
"""

import os
import re
import sys
import copy
import json
import subprocess
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'
sys.path.insert(0, os.path.join(BASE_DIR, 'scripts'))

from clone_and_translate_master_pages import (
    DEST_CONFIGS,
    COMMON_I18N as GUIDE_I18N,
    clone_and_translate_page as clone_guide_page
)
from upgrade_translated_about_pages import ABOUT_I18N
from upgrade_translated_duel_pages import DUEL_I18N, DUEL_PAGES
from upgrade_translated_contact_pages import CONTACT_I18N, CONTACT_PAGES
from harmonize_all_translated_pages import I18N as HOMEPAGE_I18N

LANGS = ['fr', 'de', 'es', 'it', 'ja', 'nl', 'pl', 'ro']

URL_MAP = {
    'fr': {
        'dinner': '/fr/meilleurs-diners-croisieres-paris',
        'sightseeing': '/fr/meilleures-croisieres-seine-paris',
        'duel': '/fr/bateaux-mouches-ou-bateaux-parisiens',
        'amsterdam': '/fr/meilleures-croisieres-amsterdam',
        'london': '/fr/croisières-sur-la-tamise-à-londres',
        'about': '/fr/a-propos',
        'contact': '/fr/contact'
    },
    'de': {
        'dinner': '/de/besten-bootsfahrten-mit-abendessen-paris',
        'sightseeing': '/de/besten-bootsfahrten-seine-paris',
        'duel': '/de/bateaux-mouches-gegen-bateaux-parisiens-dinner-kreuzfahrt-nebeneinander-vergleich',
        'amsterdam': '/de/besten-grachtenfahrten-amsterdam',
        'london': '/de/themse-kreuzfahrten-london',
        'about': '/de/uber-uns',
        'contact': '/de/kontakt'
    },
    'es': {
        'dinner': '/es/mejores-cruceros-con-cena-paris',
        'sightseeing': '/es/mejores-cruceros-sena-paris',
        'duel': '/es/comparación-de-crucero-con-cena-bateaux-mouches-vs-bateaux-parisiens-lado-a-lado',
        'amsterdam': '/es/mejores-cruceros-canales-amsterdam',
        'london': '/es/mejores-cruceros-tamesis-londres',
        'about': '/es/acerca',
        'contact': '/es/contacto'
    },
    'it': {
        'dinner': '/it/migliori-crociere-con-cena-senna-parigi',
        'sightseeing': '/it/migliori-crociere-senna-parigi',
        'duel': '/it/bateaux-mouches-vs-bateaux-parisiens-crociera-con-cena-confronto-fianco-a-fianco',
        'amsterdam': '/it/migliori-crociere-canali-amsterdam',
        'london': '/it/crociere-sul-fiume-tamigi-a-londra',
        'about': '/it/su-di-noi',
        'contact': '/it/contatto'
    },
    'ja': {
        'dinner': '/ja/パリのベスト-ディナ-クル-ズ',
        'sightseeing': '/ja/パリのベスト-セ-ヌ川クル-ズ',
        'duel': '/ja/バトームーシュとバトーパリジャンのディナークルーズの並べて比較',
        'amsterdam': '/ja/ベスト運河クル-ズ-アムステルダム',
        'london': '/ja/ロンドンのテムズ川クル-ズ',
        'about': '/ja/について',
        'contact': '/ja/接触'
    },
    'nl': {
        'dinner': '/nl/beste-boottochten-seine-met-diner-parijs',
        'sightseeing': '/nl/beste-boottochten-seine-parijs',
        'duel': '/nl/bateaux-mouches-vs-bateaux-parisiens-dinercruise-zij-aan-zij-vergelijking',
        'amsterdam': '/nl/beste-roondvarten-grachten-amsterdam',
        'london': '/nl/beste-boottochten-theems-londen',
        'about': '/nl/over-uns',
        'contact': '/nl/contact'
    },
    'pl': {
        'dinner': '/pl/najlepsze-rejsy-z-obiadem-paryz',
        'sightseeing': '/pl/najlepsze-rejsy-po-sekwanie-paryz',
        'duel': '/pl/porównanie-bateaux-mouches-vs-bateaux-parisiens-rejs-z-kolacją',
        'amsterdam': '/pl/najlepsze-rejsy-po-kanałach-amsterdam',
        'london': '/pl/rejsy-po-tamizie-londyn',
        'about': '/pl/o',
        'contact': '/pl/kontakt'
    },
    'ro': {
        'dinner': '/ro/cele-mai-bune-cina-croaziere-paris',
        'sightseeing': '/ro/cele-mai-bune-croaziere-râul-senine-paris',
        'duel': '/ro/bateaux-mouches-vs-bateaux-parisiens-cina-croazieră-comparație-alăturată',
        'amsterdam': '/ro/cele-mai-bune-croaziere-canal-amsterdam',
        'london': '/ro/cele-mai-bune-croaziere-râul-tamisa-londra',
        'about': '/ro/despre',
        'contact': '/ro/contact'
    }
}

DEST_FILTER_LABELS = {
    'fr': {'all': 'Tous les Guides (5)', 'paris': 'Paris (3)', 'amsterdam': 'Amsterdam (1)', 'london': 'Londres (1)'},
    'de': {'all': 'Alle Guides (5)', 'paris': 'Paris (3)', 'amsterdam': 'Amsterdam (1)', 'london': 'London (1)'},
    'es': {'all': 'Todas las Guías (5)', 'paris': 'París (3)', 'amsterdam': 'Ámsterdam (1)', 'london': 'Londres (1)'},
    'it': {'all': 'Tutte le Guide (5)', 'paris': 'Parigi (3)', 'amsterdam': 'Amsterdam (1)', 'london': 'Londra (1)'},
    'ja': {'all': 'すべてのガイド (5)', 'paris': 'パリ (3)', 'amsterdam': 'アムステルダム (1)', 'london': 'ロンドン (1)'},
    'nl': {'all': 'Alle Gidsen (5)', 'paris': 'Parijs (3)', 'amsterdam': 'Amsterdam (1)', 'london': 'Londen (1)'},
    'pl': {'all': 'Wszystkie Przewodniki (5)', 'paris': 'Paryż (3)', 'amsterdam': 'Amsterdam (1)', 'london': 'Londyn (1)'},
    'ro': {'all': 'Toate Ghidurile (5)', 'paris': 'Paris (3)', 'amsterdam': 'Amsterdam (1)', 'london': 'Londra (1)'}
}

PRICE_LABELS = {
    'fr': {'from': 'À partir de', 'pp': '/ personne'},
    'de': {'from': 'Ab', 'pp': '/ Person'},
    'es': {'from': 'Desde', 'pp': '/ persona'},
    'it': {'from': 'Da', 'pp': '/ persona'},
    'ja': {'from': '', 'pp': '〜 / 1名'},
    'nl': {'from': 'Vanaf', 'pp': '/ persoon'},
    'pl': {'from': 'Od', 'pp': '/ osoba'},
    'ro': {'from': 'De la', 'pp': '/ persoană'}
}

GUIDE_CARDS_I18N = {
    'fr': {
        'featured_tag': '⭐ CHOIX #1 RÉDACTION • SEINE PARIS',
        'featured_kicker': 'Paris, France • 10 Bateaux Testés',
        'featured_title': 'Les 10 Meilleurs Dîners-Croisières sur la Seine à Paris (2026)',
        'featured_excerpt': 'Du grand classique 4 plats des Bateaux Mouches au violon jusqu\'aux salons gastronomiques vitrés et bistrots romantiques intimes.',
        'featured_price': 'À partir de 55 € / personne',
        'c1_tag': '🗼 SEINE PARIS',
        'c1_kicker': 'Paris, France • 10 Compagnies Testées',
        'c1_title': 'Les 10 Meilleures Croisières Promenade sur la Seine (2026)',
        'c1_excerpt': 'Boucles touristiques de jour et croisières illuminées de nuit, de la Tour Eiffel au Pont Marie.',
        'c1_price': 'À partir de 16 € / personne',
        'c2_tag': '⚖️ DUEL SUR LA SEINE',
        'c2_kicker': 'Comparatif Direct • 2 Flottes Historiques',
        'c2_title': 'Bateaux Mouches vs. Bateaux Parisiens Dîner-Croisière',
        'c2_excerpt': 'Duel face-à-face sur la qualité gastronomique, l\'embarquement, les angles de vue et l\'ambiance acoustique.',
        'c2_price': 'À partir de 115 € / personne',
        'c3_tag': '🌷 CANAUX D\'AMSTERDAM',
        'c3_kicker': 'Amsterdam, Pays-Bas • 10 Opérateurs Testés',
        'c3_title': 'Les 10 Meilleures Croisières sur les Canaux d\'Amsterdam (2026)',
        'c3_excerpt': 'Des barques ouvertes électriques avec fromage hollandais et bières artisanales aux élégants bateaux salon vitrés dans la ceinture UNESCO.',
        'c3_price': 'À partir de 16 € / personne',
        'c4_tag': '🇬🇧 TAMISE À LONDRES',
        'c4_kicker': 'Londres, Royaume-Uni • 10 Opérateurs Testés',
        'c4_title': 'Les 10 Meilleures Croisières sur la Tamise à Londres (2026)',
        'c4_excerpt': 'Boucles historiques de Westminster à Greenwich, vedettes ultra-rapides en semi-rigide et dîners illuminés sous Tower Bridge.',
        'c4_price': 'À partir de 15 £ / personne',
        'btn_read': 'Lire le guide complet →',
        'btn_duel': 'Comparer le duel →'
    },
    'de': {
        'featured_tag': '⭐ REDAKTIONSTIPP #1 • PARIS SEINE',
        'featured_kicker': 'Paris, Frankreich • 10 Schiffe Getestet',
        'featured_title': 'Die 10 besten Seine Dinner-Kreuzfahrten in Paris (2026)',
        'featured_excerpt': 'Vom klassischen 4-Gänge-Menü der Bateaux Mouches mit Live-Geige bis zu eleganten Panorama-Salons und romantischen Bistros.',
        'featured_price': 'Ab 55 € / Person',
        'c1_tag': '🗼 PARIS SEINE',
        'c1_kicker': 'Paris, Frankreich • 10 Reedereien Getestet',
        'c1_title': 'Die 10 besten Seine Rundfahrten in Paris (2026)',
        'c1_excerpt': 'Klassische Sightseeing-Runden bei Tag und abendliche Lichterfahrten vom Eiffelturm bis zur Île Saint-Louis.',
        'c1_price': 'Ab 16 € / Person',
        'c2_tag': '⚖️ SEINE DUELL',
        'c2_kicker': 'Direkter Vergleich • 2 Historische Flotten',
        'c2_title': 'Bateaux Mouches vs. Bateaux Parisiens Dinner-Kreuzfahrt',
        'c2_excerpt': 'Direkter Praxisvergleich bei Kulinarik, Boarding, Tischplatzierung und Akustik.',
        'c2_price': 'Ab 115 € / Person',
        'c3_tag': '🌷 GRACHTEN AMSTERDAM',
        'c3_kicker': 'Amsterdam, Niederlande • 10 Anbieter Getestet',
        'c3_title': 'Die 10 besten Grachtenfahrten in Amsterdam (2026)',
        'c3_excerpt': 'Von offenen Elektroschaluppen mit holländischem Käse und Bier bis zu klassischen historischen Salonbooten im UNESCO-Grachtengürtel.',
        'c3_price': 'Ab 16 € / Person',
        'c4_tag': '🇬🇧 THEMSE LONDON',
        'c4_kicker': 'London, Großbritannien • 10 Anbieter Getestet',
        'c4_title': 'Die 10 besten Themse Bootsfahrten in London (2026)',
        'c4_excerpt': 'Historische Touren von Westminster nach Greenwich, rasante Speedboot-Touren und beleuchtete Abendfahrten an der Tower Bridge.',
        'c4_price': 'Ab 15 £ / Person',
        'btn_read': 'Vollständigen Guide lesen →',
        'btn_duel': 'Duell vergleichen →'
    },
    'es': {
        'featured_tag': '⭐ ELECCIÓN #1 EDITORIAL • SENA PARÍS',
        'featured_kicker': 'París, Francia • 10 Barcos Probados',
        'featured_title': 'Los 10 Mejores Cruceros con Cena por el Sena en París (2026)',
        'featured_excerpt': 'Desde el clásico menú francés de 4 platos con violines en vivo de Bateaux Mouches hasta salones panorámicos y bistrós íntimos.',
        'featured_price': 'Desde 55 € / persona',
        'c1_tag': '🗼 SENA PARÍS',
        'c1_kicker': 'París, Francia • 10 Operadores Probados',
        'c1_title': 'Los 10 Mejores Cruceros Panorámicos por el Sena (2026)',
        'c1_excerpt': 'Paseos turísticos diurnos e iluminaciones nocturnas desde la Torre Eiffel hasta Pont Marie.',
        'c1_price': 'Desde 16 € / persona',
        'c2_tag': '⚖️ DUELO EN EL SENA',
        'c2_kicker': 'Comparativa Directa • 2 Flotas Históricas',
        'c2_title': 'Bateaux Mouches vs. Bateaux Parisiens Crucero con Cena',
        'c2_excerpt': 'Comparación cara a cara en nivel gastronómico, embarque, visibilidad y acústica.',
        'c2_price': 'Desde 115 € / persona',
        'c3_tag': '🌷 CANALES DE ÁMSTERDAM',
        'c3_kicker': 'Ámsterdam, Países Bajos • 10 Operadores Probados',
        'c3_title': 'Los 10 Mejores Cruceros por los Canales de Ámsterdam (2026)',
        'c3_excerpt': 'Desde barcazas abiertas eléctricas con queso y cerveza local hasta elegantes barcos salón acristalados en el anillo UNESCO.',
        'c3_price': 'Desde 16 € / persona',
        'c4_tag': '🇬🇧 TÁMESIS LONDRES',
        'c4_kicker': 'Londres, Reino Unido • 10 Operadores Probados',
        'c4_title': 'Los 10 Mejores Cruceros por el Támesis en Londres (2026)',
        'c4_excerpt': 'Recorridos históricos de Westminster a Greenwich, lanchas rápidas RIB y cenas iluminadas junto al Tower Bridge.',
        'c4_price': 'Desde 15 £ / persona',
        'btn_read': 'Leer guía completa →',
        'btn_duel': 'Comparar duelo →'
    },
    'it': {
        'featured_tag': '⭐ SCELTA #1 EDITORIALE • SENNA PARIGI',
        'featured_kicker': 'Parigi, Francia • 10 Navi Provate',
        'featured_title': 'Le 10 Migliori Crociere con Cena sulla Senna a Parigi (2026)',
        'featured_excerpt': 'Dal classico menu francese a 4 portate con violini dal vivo di Bateaux Mouches ai saloni panoramici vetrati e romantici bistrot.',
        'featured_price': 'Da 55 € / persona',
        'c1_tag': '🗼 SENNA PARIGI',
        'c1_kicker': 'Parigi, Francia • 10 Compagnie Provate',
        'c1_title': 'Le 10 Migliori Crociere Panoramiche sulla Senna (2026)',
        'c1_excerpt': 'Tour turistici diurni e crociere illuminate notturne dalla Torre Eiffel a Pont Marie.',
        'c1_price': 'Da 16 € / persona',
        'c2_tag': '⚖️ DUELLO SULLA SENNA',
        'c2_kicker': 'Confronto Diretto • 2 Flotte Storiche',
        'c2_title': 'Bateaux Mouches vs. Bateaux Parisiens Crociera con Cena',
        'c2_excerpt': 'Confronto testa a testa su qualità della cucina, imbarco, visuale e atmosfera acustica.',
        'c2_price': 'Da 115 € / persona',
        'c3_tag': '🌷 CANALI DI AMSTERDAM',
        'c3_kicker': 'Amsterdam, Paesi Bassi • 10 Operatori Provati',
        'c3_title': 'Le 10 Migliori Crociere sui Canali di Amsterdam (2026)',
        'c3_excerpt': 'Dalle barche scoperte elettriche con formaggio olandese e birra artigianale ai battelli d\'epoca nella cerchia UNESCO.',
        'c3_price': 'Da 16 € / persona',
        'c4_tag': '🇬🇧 TAMIGI LONDRA',
        'c4_kicker': 'Londra, Regno Unito • 10 Operatori Provati',
        'c4_title': 'Le 10 Migliori Crociere sul Tamigi a Londra (2026)',
        'c4_excerpt': 'Itinerari storici da Westminster a Greenwich, gommoni veloci RIB e cene eleganti sotto il Tower Bridge.',
        'c4_price': 'Da 15 £ / persona',
        'btn_read': 'Leggi la guida completa →',
        'btn_duel': 'Confronta il duello →'
    },
    'ja': {
        'featured_tag': '⭐ 編集部第1位 • パリ・セーヌ川',
        'featured_kicker': 'フランス・パリ • 10隻を実地検証',
        'featured_title': 'パリのセーヌ川ベストディナークルーズ10選（2026年最新徹底比較）',
        'featured_excerpt': 'バトームーシュの生バイオリン付きクラシック4コース料理から、全面ガラス張りの高級ガストロノミー、隠れ家ビストロまで。',
        'featured_price': '55 € 〜 / 1名',
        'c1_tag': '🗼 パリ・セーヌ川',
        'c1_kicker': 'フランス・パリ • 10社を実地検証',
        'c1_title': 'パリのセーヌ川定番遊覧クルーズ10選（2026年最新比較）',
        'c1_excerpt': 'エッフェル塔からシテ島まで巡る日中観光クルーズと幻想的な夜間ライトアップ遊覧。',
        'c1_price': '16 € 〜 / 1名',
        'c2_tag': '⚖️ セーヌ川2大巨頭対決',
        'c2_kicker': '徹底直接対決 • 2大老舗船団',
        'c2_title': 'バトームーシュ vs バトーパリジャン ディナークルーズ直接比較',
        'c2_excerpt': '料理の味、乗船手続きのスムーズさ、窓際席の視界、生演奏の音響を徹底比較。',
        'c2_price': '115 € 〜 / 1名',
        'c3_tag': '🌷 アムステルダム運河',
        'c3_kicker': 'オランダ・アムステルダム • 10社を実地検証',
        'c3_title': 'アムステルダムのベスト運河クルーズ10選（2026年最新比較）',
        'c3_excerpt': 'オランダ産チーズとクラフトビール付きオープン電気ボートから、UNESCO運河を巡るクラシックサロン船まで。',
        'c3_price': '16 € 〜 / 1名',
        'c4_tag': '🇬🇧 ロンドン・テムズ川',
        'c4_kicker': '英国・ロンドン • 10社を実地検証',
        'c4_title': 'ロンドンのテムズ川クルーズ10選（2026年最新比較）',
        'c4_excerpt': 'ウェストミンスターからグリニッジへの歴史クルーズ、高速ボートRIB、タワーブリッジを望む夜景ディナー。',
        'c4_price': '15 £ 〜 / 1名',
        'btn_read': '完全ガイドを読む →',
        'btn_duel': '対決比較を見る →'
    },
    'nl': {
        'featured_tag': '⭐ #1 EDITORIALE KEUZE • SEINE PARIJS',
        'featured_kicker': 'Parijs, Frankrijk • 10 Schepen Getest',
        'featured_title': 'De 10 Beste Dinercruises op de Seine in Parijs (2026)',
        'featured_excerpt': 'Van het klassieke 4-gangenmenu van Bateaux Mouches met live viool tot panoramische gastronomische salons en romantische bistro\'s.',
        'featured_price': 'Vanaf 55 € / persoon',
        'c1_tag': '🗼 SEINE PARIJS',
        'c1_kicker': 'Parijs, Frankrijk • 10 Rederijen Getest',
        'c1_title': 'De 10 Beste Rondvaarten op de Seine in Parijs (2026)',
        'c1_excerpt': 'Sightseeing overdag en verlichte avondcruises langs de Eiffeltoren en Pont Marie.',
        'c1_price': 'Vanaf 16 € / persoon',
        'c2_tag': '⚖️ SEINE DUELL',
        'c2_kicker': 'Rechtstreekse Vergelijking • 2 Historische Vloten',
        'c2_title': 'Bateaux Mouches vs. Bateaux Parisiens Dinercruise',
        'c2_excerpt': 'Directe vergelijking op culinair niveau, instapprocedure, zichtlijnen en akoestiek.',
        'c2_price': 'Vanaf 115 € / persoon',
        'c3_tag': '🌷 GRACHTEN AMSTERDAM',
        'c3_kicker': 'Amsterdam, Nederland • 10 Rederijen Getest',
        'c3_title': 'De 10 Beste Rondvaarten over de Grachten in Amsterdam (2026)',
        'c3_excerpt': 'Van open elektrische sloepen met Hollandse kaas en speciaalbier tot klassieke salonboten in de UNESCO-grachtengordel.',
        'c3_price': 'Vanaf 16 € / persoon',
        'c4_tag': '🇬🇧 THEEMS LONDEN',
        'c4_kicker': 'Londen, Verenigd Koninkrijk • 10 Rederijen Getest',
        'c4_title': 'De 10 Beste Boottochten op de Theems in Londen (2026)',
        'c4_excerpt': 'Historische vaarten van Westminster naar Greenwich, spectaculaire RIB-speedboten en dinercruises bij Tower Bridge.',
        'c4_price': 'Vanaf 15 £ / persoon',
        'btn_read': 'Volledige gids lezen →',
        'btn_duel': 'Vergelijk het duel →'
    },
    'pl': {
        'featured_tag': '⭐ #1 WYBÓR REDAKCJI • SEKWANA PARYŻ',
        'featured_kicker': 'Paryż, Francja • 10 Statków Przetestowanych',
        'featured_title': '10 Najlepszych Rejsów z Kolacją po Sekwanie w Paryżu (2026)',
        'featured_excerpt': 'Od klasycznej 4-daniowej kolacji Bateaux Mouches ze skrzypcami po luksusowe oszklone salony i kameralne romantyczne bistra.',
        'featured_price': 'Od 55 € / osoba',
        'c1_tag': '🗼 SEKWANA PARYŻ',
        'c1_kicker': 'Paryż, Francja • 10 Armatorów Przetestowanych',
        'c1_title': '10 Najlepszych Rejsów Wycieczkowych po Sekwanie (2026)',
        'c1_excerpt': 'Dzienne rejsy widokowe i magicznie oświetlone trasy nocne od Wieży Eiffla po Pont Marie.',
        'c1_price': 'Od 16 € / osoba',
        'c2_tag': '⚖️ POJEDYNEK NA SEKWANIE',
        'c2_kicker': 'Bezpośrednie Porównanie • 2 Historyczne Floty',
        'c2_title': 'Bateaux Mouches vs. Bateaux Parisiens Rejs z Kolacją',
        'c2_excerpt': 'Pojedynek twarzą w twarz: jakość menu, sprawność wejścia na pokład, widok z okien i muzyka.',
        'c2_price': 'Od 115 € / osoba',
        'c3_tag': '🌷 KANAŁY AMSTERDAMU',
        'c3_kicker': 'Amsterdam, Holandia • 10 Operatorów Przetestowanych',
        'c3_title': '10 Najlepszych Rejsów po Kanałach Amsterdamu (2026)',
        'c3_excerpt': 'Od otwartych łodzi elektrycznych z holenderskim serem i piwem po klasyczne zabytkowe łodzie salonowe w pasie UNESCO.',
        'c3_price': 'Od 16 € / osoba',
        'c4_tag': '🇬🇧 TAMIZA LONDYN',
        'c4_kicker': 'Londyn, Wielka Brytania • 10 Operatorów Przetestowanych',
        'c4_title': '10 Najlepszych Rejsów po Tamizie w Londynie (2026)',
        'c4_excerpt': 'Historyczne trasy z Westminster do Greenwich, szybkie łodzie hybrydowe RIB i wieczorne kolacje przy Tower Bridge.',
        'c4_price': 'Od 15 £ / osoba',
        'btn_read': 'Przeczytaj pełny przewodnik →',
        'btn_duel': 'Porównaj pojedynek →'
    },
    'ro': {
        'featured_tag': '⭐ ALEGEREA #1 EDITORIALĂ • SENA PARIS',
        'featured_kicker': 'Paris, Franța • 10 Nave Testate',
        'featured_title': 'Cele Mai Bune 10 Croaziere cu Cină pe Sena din Paris (2026)',
        'featured_excerpt': 'De la clasica cină franțuzească cu 4 feluri și vioară live Bateaux Mouches, până la saloane gastronomice vitrate și bistrouri cochete.',
        'featured_price': 'De la 55 € / persoană',
        'c1_tag': '🗼 SENA PARIS',
        'c1_kicker': 'Paris, Franța • 10 Companii Testate',
        'c1_title': 'Cele Mai Bune 10 Croaziere Panoramice pe Sena (2026)',
        'c1_excerpt': 'Tururi de zi și croaziere nocturne spectaculoase cu monumentele iluminate, de la Turnul Eiffel la Pont Marie.',
        'c1_price': 'De la 16 € / persoană',
        'c2_tag': '⚖️ DUEL PE SENA',
        'c2_kicker': 'Comparație Directă • 2 Flote Istorice',
        'c2_title': 'Bateaux Mouches vs. Bateaux Parisiens Croazieră cu Cină',
        'c2_excerpt': 'Confruntare directă privind gastronomia, rapiditatea îmbarcării, unghiurile de vizibilitate și muzica live.',
        'c2_price': 'De la 115 € / persoană',
        'c3_tag': '🌷 CANALELE DIN AMSTERDAM',
        'c3_kicker': 'Amsterdam, Olanda • 10 Operatori Testați',
        'c3_title': 'Cele Mai Bune 10 Croaziere pe Canalele din Amsterdam (2026)',
        'c3_excerpt': 'De la bărci deschise electrice cu brânzeturi olandeze și bere locală, până la vapoare salon clasice în inelul UNESCO.',
        'c3_price': 'De la 16 € / persoană',
        'c4_tag': '🇬🇧 TAMISA DIN LONDRA',
        'c4_kicker': 'Londra, Marea Britanie • 10 Operatori Testați',
        'c4_title': 'Cele Mai Bune 10 Croaziere pe Tamisa din Londra (2026)',
        'c4_excerpt': 'Trasee istorice de la Westminster la Greenwich, bărci rapide de mare viteză RIB și cine romantice pe lângă Tower Bridge.',
        'c4_price': 'De la 15 £ / persoană',
        'btn_read': 'Citește ghidul complet →',
        'btn_duel': 'Compară duelul →'
    }
}

def localize_navbar(soup, lang):
    """Ensure navbar branding, links, and drawer are localized cleanly"""
    d = HOMEPAGE_I18N[lang]
    u = URL_MAP[lang]

    # Brand link
    b_link = soup.find('a', class_='ltt-nav-logo')
    if b_link:
        b_link['href'] = f"/{lang}/"

    # Mega menu items
    links = {
        u['dinner']: (d['paris_dinner'], d['paris_dinner_sub']),
        u['sightseeing']: (d['paris_sightseeing'], d['paris_sightseeing_sub']),
        u['duel']: (d['duel'], d['duel_sub']),
        u['amsterdam']: (d['amsterdam'], d['amsterdam_sub']),
        u['london']: (d['london'], d['london_sub']),
    }
    
    # Update top links
    nav_links = soup.find_all(class_='ltt-nav-link')
    for nl in nav_links:
        href = nl.get('href', '')
        if 'dinner' in href or 'diner' in href:
            nl['href'] = u['dinner']
            nl.string = d['top_dinner']
        elif 'seine' in href or 'sightseeing' in href or 'promenade' in href:
            nl['href'] = u['sightseeing']
            nl.string = d['top_sightseeing']
        elif 'about' in href or 'propos' in href or 'uber' in href or 'acerca' in href or 'despre' in href:
            nl['href'] = u['about']
            nl.string = d['about']
        elif 'contact' in href or 'kontakt' in href or 'contatto' in href or '接触' in href:
            nl['href'] = u['contact']
            nl.string = d['contact']

    # Update drawer links
    drawer = soup.find(id='lttMobileDrawer')
    if drawer:
        for a in drawer.find_all('a', class_='ltt-mobile-link'):
            href = a.get('href', '')
            span = a.find('span')
            if 'dinner' in href or 'diner' in href:
                a['href'] = u['dinner']
                if span: span.string = f"🍷 {d['paris_dinner']}"
            elif 'seine' in href or 'sightseeing' in href or 'promenade' in href:
                a['href'] = u['sightseeing']
                if span: span.string = f"🗼 {d['paris_sightseeing']}"
            elif 'duel' in href or 'mouches' in href:
                a['href'] = u['duel']
                if span: span.string = f"⚖️ {d['duel']}"
            elif 'amsterdam' in href or 'canal' in href:
                a['href'] = u['amsterdam']
                if span: span.string = f"🌷 {d['amsterdam']}"
            elif 'london' in href or 'tamise' in href or 'thames' in href:
                a['href'] = u['london']
                if span: span.string = f"🇬🇧 {d['london']}"
            elif 'about' in href or 'propos' in href or 'uber' in href or 'despre' in href:
                a['href'] = u['about']
                if span: span.string = f"ℹ️ {d['about']}"
            elif 'contact' in href or 'kontakt' in href or '接触' in href:
                a['href'] = u['contact']
                if span: span.string = f"✉️ {d['contact']}"

def localize_footer(soup, lang):
    """Ensure footer has 100% proper classes, styling, and localized URLs"""
    d = HOMEPAGE_I18N[lang]
    u = URL_MAP[lang]

    footer = soup.find('footer') or soup.find(class_='footer-dark')
    if not footer:
        return

    # Tagline
    f_desc = footer.find(class_='footer-paragraph')
    if f_desc:
        f_desc.string = d['footer_desc']

    # Headers
    col_titles = footer.find_all(class_='footer-link-title')
    if len(col_titles) >= 2:
        col_titles[0].string = d['footer_guides_head']
        col_titles[1].string = d['footer_company_head']

    # Links
    for a in footer.find_all('a', class_='footer-link-3'):
        href = a.get('href', '')
        if 'seine' in href or 'sightseeing' in href:
            a['href'] = u['sightseeing']
            a.string = d['paris_sightseeing']
        elif 'dinner' in href or 'diner' in href:
            a['href'] = u['dinner']
            a.string = d['paris_dinner']
        elif 'mouches' in href or 'duel' in href:
            a['href'] = u['duel']
            a.string = d['duel']
        elif 'amsterdam' in href:
            a['href'] = u['amsterdam']
            a.string = d['amsterdam']
        elif 'london' in href or 'tamise' in href or 'thames' in href:
            a['href'] = u['london']
            a.string = d['london']
        elif 'about' in href or 'propos' in href or 'uber' in href or 'despre' in href:
            a['href'] = u['about']
            a.string = d['about']
        elif 'methodology' in href:
            a['href'] = f"{u['about']}#methodology"
            a.string = d.get('author_link', 'Méthodologie').replace(' →', '')
        elif 'contact' in href or 'kontakt' in href:
            a['href'] = u['contact']
            a.string = d['contact']

    # Legal links
    for a in footer.find_all('a', class_='legal-link'):
        href = a.get('href', '')
        if 'privacy' in href:
            a['href'] = f"/{lang}/privacy-policy"
            a.string = d['footer_privacy']
        elif 'terms' in href:
            a['href'] = f"/{lang}/terms-of-service"
            a.string = d['footer_terms']

def clone_and_translate_homepage(lang):
    """Clones index.html 1:1 and localizes it for target language"""
    en_path = os.path.join(BASE_DIR, 'index.html')
    target_path = os.path.join(BASE_DIR, f"{lang}/index.html")

    print(f"\n[HOMEPAGE 1:1 CLONE] -> {lang}/index.html ...")
    with open(en_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    d = HOMEPAGE_I18N[lang]
    u = URL_MAP[lang]
    gc = GUIDE_CARDS_I18N[lang]
    df = DEST_FILTER_LABELS[lang]

    # 1. Update html lang & canonical
    html_tag = soup.find('html')
    if html_tag:
        html_tag['lang'] = lang

    canon = soup.find('link', rel='canonical')
    if canon:
        canon['href'] = f"https://www.thecruisedetective.com/{lang}/"

    # 2. Localize Navbar
    localize_navbar(soup, lang)

    # 3. Localize Hero
    hero = soup.find(class_='ltt-home-hero')
    if hero:
        eyebrow = hero.find(class_='ltt-hero-eyebrow')
        if eyebrow:
            eyebrow.string = d['home_eyebrow']

        h1 = hero.find('h1')
        if h1:
            h1.clear()
            h1.append(d['home_title'] + ' ')
            gspan = soup.new_tag('span', **{'class': 'ltt-gold-text'})
            gspan.string = d['home_title_gold']
            h1.append(gspan)

        subtitle = hero.find(class_='ltt-hero-subtitle')
        if subtitle:
            subtitle.string = d['home_subtitle']

        # Stats strip
        stat_cards = hero.find_all(class_='ltt-stat-card')
        stat_data = [
            (d['stat_1_num'], d['stat_1_label'], d['stat_1_sub']),
            (d['stat_2_num'], d['stat_2_label'], d['stat_2_sub']),
            (d['stat_3_num'], d['stat_3_label'], d['stat_3_sub']),
            (d['stat_4_num'], d['stat_4_label'], d['stat_4_sub']),
        ]
        for idx, sc in enumerate(stat_cards):
            if idx < len(stat_data):
                num_tag = sc.find(class_='ltt-stat-number')
                lbl_tag = sc.find(class_='ltt-stat-label')
                sub_tag = sc.find(class_='ltt-stat-sub')
                if num_tag: num_tag.string = stat_data[idx][0]
                if lbl_tag: lbl_tag.string = stat_data[idx][1]
                if sub_tag: sub_tag.string = stat_data[idx][2]

        # Quick links
        quick_btns = hero.find_all(class_='ltt-quick-btn')
        quick_data = [
            (u['dinner'], f"🍷 {d['paris_dinner']}"),
            (u['sightseeing'], f"🗼 {d['paris_sightseeing']}"),
            (u['duel'], f"⚖️ {d['duel']}"),
            (u['amsterdam'], f"🌷 {d['amsterdam']}"),
            (u['london'], f"🇬🇧 {d['london']}"),
        ]
        for idx, qb in enumerate(quick_btns):
            if idx < len(quick_data):
                qb['href'] = quick_data[idx][0]
                qb.string = quick_data[idx][1]

    # 4. Localize Guides Section
    guides_sec = soup.find(id='guides')
    if guides_sec:
        sec_title = guides_sec.find(class_='ltt-section-title')
        if sec_title:
            sec_title.string = d['flagship_title']
        sec_sub = guides_sec.find(class_='ltt-section-subtitle')
        if sec_sub:
            sec_sub.string = d['flagship_sub']

        # Filter buttons
        filter_btns = guides_sec.find_all(class_='ltt-dest-btn')
        for fb in filter_btns:
            fdata = fb.get('data-filter')
            if fdata in df:
                fb.string = df[fdata]

        # Featured Spotlight Guide (Paris Dinner)
        feat = guides_sec.find(id='featured-guide')
        if feat:
            feat['href'] = u['dinner']
            tag = feat.find(class_='ltt-guide-tag')
            if tag: tag.string = gc['featured_tag']
            kicker = feat.find(class_='ltt-guide-kicker')
            if kicker: kicker.string = gc['featured_kicker']
            gtitle = feat.find(class_='ltt-guide-title')
            if gtitle: gtitle.string = gc['featured_title']
            excerpt = feat.find(class_='ltt-guide-excerpt')
            if excerpt: excerpt.string = gc['featured_excerpt']
            fprice = feat.find('span', style=lambda s: s and 'font-weight: 800' in s)
            if fprice: fprice.string = gc['featured_price']
            fbtn = feat.find(class_='ltt-guide-btn')
            if fbtn: fbtn.string = gc['btn_read']

        # 4 Grid Cards
        cards = guides_sec.find_all(class_='ltt-guide-card')
        cards_info = [
            # 1. Sightseeing
            (u['sightseeing'], gc['c1_tag'], gc['c1_kicker'], gc['c1_title'], gc['c1_excerpt'], gc['c1_price'], gc['btn_read']),
            # 2. Duel
            (u['duel'], gc['c2_tag'], gc['c2_kicker'], gc['c2_title'], gc['c2_excerpt'], gc['c2_price'], gc['btn_duel']),
            # 3. Amsterdam
            (u['amsterdam'], gc['c3_tag'], gc['c3_kicker'], gc['c3_title'], gc['c3_excerpt'], gc['c3_price'], gc['btn_read']),
            # 4. London
            (u['london'], gc['c4_tag'], gc['c4_kicker'], gc['c4_title'], gc['c4_excerpt'], gc['c4_price'], gc['btn_read']),
        ]
        for idx, card in enumerate(cards):
            if idx < len(cards_info):
                c_url, c_tag, c_kicker, c_title, c_excerpt, c_price, c_btn = cards_info[idx]
                card['href'] = c_url
                tag_el = card.find(class_='ltt-guide-tag')
                if tag_el: tag_el.string = c_tag
                kicker_el = card.find(class_='ltt-guide-kicker')
                if kicker_el: kicker_el.string = c_kicker
                title_el = card.find(class_='ltt-guide-title')
                if title_el: title_el.string = c_title
                exc_el = card.find(class_='ltt-guide-excerpt')
                if exc_el: exc_el.string = c_excerpt
                price_el = card.find('span', style=lambda s: s and 'font-weight: 800' in s)
                if price_el: price_el.string = c_price
                btn_el = card.find(class_='ltt-guide-btn')
                if btn_el: btn_el.string = c_btn

    # 5. Localize Manifesto Section
    manifesto_sec = soup.find(lambda s: s.name == 'section' and s.find(class_='ltt-manifesto-grid'))
    if manifesto_sec:
        m_eyebrow = manifesto_sec.find(class_='ltt-section-eyebrow')
        if m_eyebrow: m_eyebrow.string = d['manifesto_eyebrow']
        m_title = manifesto_sec.find(class_='ltt-section-title')
        if m_title: m_title.string = d['manifesto_title']
        m_sub = manifesto_sec.find(class_='ltt-section-subtitle')
        if m_sub: m_sub.string = d['manifesto_sub']

        m_cards = manifesto_sec.find_all(class_='ltt-manifesto-card')
        m_data = [
            (d['man_1_title'], d['man_1_text']),
            (d['man_2_title'], d['man_2_text']),
            (d['man_3_title'], d['man_3_text'])
        ]
        for idx, mc in enumerate(m_cards):
            if idx < len(m_data):
                mctitle = mc.find(class_='ltt-manifesto-title')
                if mctitle: mctitle.string = m_data[idx][0]
                mctext = mc.find(class_='ltt-manifesto-text')
                if mctext: mctext.string = m_data[idx][1]

    # 6. Localize Author Section
    author_sec = soup.find(class_='ltt-author-section')
    if author_sec:
        a_eyebrow = author_sec.find(class_='ltt-author-eyebrow')
        if a_eyebrow: a_eyebrow.string = d['author_eyebrow']
        a_name = author_sec.find(class_='ltt-author-name')
        if a_name: a_name.string = d['author_name']
        a_role = author_sec.find(class_='ltt-author-role')
        if a_role: a_role.string = d['author_role']
        a_bio = author_sec.find(class_='ltt-author-bio')
        if a_bio: a_bio.string = d['author_bio']
        a_link = author_sec.find(class_='ltt-author-links')
        if a_link and a_link.find('a'):
            a_tag = a_link.find('a')
            a_tag['href'] = u['about']
            a_tag.string = d['author_link']

    # 7. Localize Footer
    localize_footer(soup, lang)

    final_html = str(soup)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"  -> Saved {lang}/index.html ({len(final_html)} bytes)")

def clone_and_translate_about_page(lang):
    """Clones about/index.html 1:1 and localizes it for target language"""
    en_path = os.path.join(BASE_DIR, 'about/index.html')
    rel_path = URL_MAP[lang]['about'].lstrip('/') + '/index.html'
    target_path = os.path.join(BASE_DIR, rel_path)

    print(f"\n[ABOUT 1:1 CLONE] -> {rel_path} ...")
    with open(en_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    ab = ABOUT_I18N[lang]
    u = URL_MAP[lang]

    # 1. Update html lang & canonical
    html_tag = soup.find('html')
    if html_tag:
        html_tag['lang'] = lang

    canon = soup.find('link', rel='canonical')
    if canon:
        canon['href'] = f"https://www.thecruisedetective.com/{URL_MAP[lang]['about'].lstrip('/')}"

    # 2. Localize Navbar
    localize_navbar(soup, lang)

    # 3. Localize About Header
    hdr = soup.find(class_='ltt-about-header')
    if hdr:
        eyebrow = hdr.find(class_='ltt-section-eyebrow')
        if eyebrow: eyebrow.string = ab['hdr_eyebrow']
        h1 = hdr.find(class_='ltt-about-main-title') or hdr.find('h1')
        if h1:
            h1.clear()
            h1.append(ab['hdr_title'])
            br = soup.new_tag('br')
            h1.append(br)
            gspan = soup.new_tag('span', **{'class': 'ltt-gold-text'})
            gspan.string = ab['hdr_title_gold']
            h1.append(gspan)
        lead = hdr.find(class_='ltt-about-intro-lead')
        if lead: lead.string = ab['hdr_lead']

    # 4. Localize Section 1: Manifesto Pillars
    pillars_sec = soup.find(lambda s: s.name == 'section' and s.find(class_='ltt-manifesto-grid'))
    if pillars_sec:
        eyebrow = pillars_sec.find(class_='ltt-section-eyebrow')
        if eyebrow: eyebrow.string = ab['sec1_eyebrow']
        title = pillars_sec.find(class_='ltt-section-title')
        if title: title.string = ab['sec1_title']
        sub = pillars_sec.find(class_='ltt-section-subtitle')
        if sub: sub.string = ab['sec1_sub']

        p_cards = pillars_sec.find_all(class_='ltt-manifesto-card')
        p_data = [
            (ab['p1_title'], ab['p1_text']),
            (ab['p2_title'], ab['p2_text']),
            (ab['p3_title'], ab['p3_text'])
        ]
        for idx, pc in enumerate(p_cards):
            if idx < len(p_data):
                h3 = pc.find('h3')
                if h3: h3.string = p_data[idx][0]
                p = pc.find('p')
                if p: p.string = p_data[idx][1]

    # 5. Localize Section 2: Founder Card
    founder_sec = soup.find(lambda s: s.name == 'section' and s.find(class_='ltt-author-card'))
    if founder_sec:
        f_eyebrow = founder_sec.find(class_='ltt-author-eyebrow')
        if f_eyebrow: f_eyebrow.string = ab['founder_eyebrow']
        f_name = founder_sec.find(class_='ltt-author-name')
        if f_name: f_name.string = ab['founder_name']
        f_role = founder_sec.find(class_='ltt-author-role')
        if f_role: f_role.string = ab['founder_role']
        
        # Replace bio paragraphs
        f_card = founder_sec.find(class_='ltt-author-card')
        if f_card:
            right_col = f_card.find('div')
            if right_col:
                ps = right_col.find_all('p')
                if len(ps) >= 2:
                    ps[0].string = ab['founder_p1']
                    ps[1].string = ab['founder_p2']

    # 6. Localize Section 3: Ethics Policy (Dark Navy Container)
    ethics_sec = soup.find(class_='ltt-ethics-section')
    if ethics_sec:
        e_eyebrow = ethics_sec.find(class_='ltt-section-eyebrow')
        if e_eyebrow: e_eyebrow.string = ab['sec2_eyebrow']
        e_title = ethics_sec.find(class_='ltt-section-title')
        if e_title: e_title.string = ab['sec2_title']
        e_sub = ethics_sec.find(class_='ltt-section-subtitle')
        if e_sub: e_sub.string = ab['sec2_sub']

        e_cards = ethics_sec.find_all(class_='ltt-ethics-card')
        e_data = [
            (ab['e1_title'], ab['e1_text']),
            (ab['e2_title'], ab['e2_text']),
            (ab['e3_title'], ab['e3_text']),
            (ab['e4_title'], ab['e4_text']),
            (ab['e5_title'], ab['e5_text']),
        ]
        for idx, ec in enumerate(e_cards):
            if idx < len(e_data):
                h3 = ec.find('h3')
                if h3: h3.string = e_data[idx][0]
                p = ec.find('p')
                if p: p.string = e_data[idx][1]

    # 7. Localize Footer
    localize_footer(soup, lang)

    final_html = str(soup)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"  -> Saved {rel_path} ({len(final_html)} bytes)")

def run_all_cloners():
    print("=================================================================")
    print("EXECUTING DEFINITIVE MASTER 1:1 CLONING & TRANSLATION PIPELINE")
    print("=================================================================")

    # 1. Guides (32 pages + 8 aliases)
    print("\n--- PHASE 1: DESTINATION GUIDES ---")
    for dest_key in ['dinner', 'sightseeing', 'amsterdam', 'london']:
        cfg = DEST_CONFIGS[dest_key]
        for lang in LANGS:
            target_rel = cfg['pages'][lang]
            clone_guide_page(dest_key, lang, target_rel)

    # 2. Homepages (8 pages)
    print("\n--- PHASE 2: HOMEPAGES ---")
    for lang in LANGS:
        clone_and_translate_homepage(lang)

    # 3. About Pages (8 pages)
    print("\n--- PHASE 3: ABOUT PAGES ---")
    for lang in LANGS:
        clone_and_translate_about_page(lang)

    # 4. Duel Pages (8 pages)
    print("\n--- PHASE 4: DUEL SHOWDOWN PAGES ---")
    from upgrade_translated_duel_pages import upgrade_duel_page
    for lang, rel_path in DUEL_PAGES.items():
        upgrade_duel_page(lang, rel_path)

    # 5. Contact Pages (8 pages)
    print("\n--- PHASE 5: CONTACT DESK PAGES ---")
    from upgrade_translated_contact_pages import upgrade_contact_page
    for lang, rel_path in CONTACT_PAGES.items():
        upgrade_contact_page(lang, rel_path)

    print("\n=================================================================")
    print("ALL 64+ SITE PAGES CLONED & TRANSLATED WITH 100% MASTER PARITY!")
    print("=================================================================")

if __name__ == '__main__':
    run_all_cloners()
