#!/usr/bin/env python3
"""
MASTER TRANSLATED DESTINATION GUIDE COMPILER — THE CRUISE DETECTIVE
Compiles all 32 translated destination guide pages across 8 languages:
- Paris Dinner Cruises (8 languages)
- Paris Sightseeing Cruises (8 languages)
- Amsterdam Canal Cruises (8 languages)
- London Thames Cruises (8 languages)
+ Secondary alias pages (seine-river-cruises-paris-1)

Enforces 100% architectural, visual, and functional parity with the English Luxury Travel Tester standard:
- Zero legacy Webflow hero wrappers, zero yellow résumé banners, zero green buttons.
- Canonical ltt-navbar with localized links and mobile drawer.
- Canonical ltt-hero-wrap > ltt-clean-card with breadcrumbs, kicker, trust bar, lead copy, and single-row filter bar.
- Canonical ltt-deck-container with 10 bpa-card cards, 3-column desktop layout, photo sliders, and 9999px gold pill buttons.
- Canonical blog-section-2 with sticky Table of Contents and 10 details.bpa-details-card review cards.
- Canonical luxury footer, hybrid sticky bar, and ltt-nav.js controller.
- 100% affiliate tracking link preservation (partner=thecruisedetective.com-176436).
"""

import os
import re
import sys
import glob
import subprocess
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'
sys.path.insert(0, BASE_DIR)

LANGS = ['fr', 'de', 'es', 'it', 'ja', 'nl', 'pl', 'ro']

DEST_CONFIGS = {
    'dinner': {
        'en_path': 'dinner-cruises-paris/index.html',
        'deck_id': 'paris-dinner-cruises-deck',
        'pages': {
            'fr': 'fr/meilleurs-diners-croisieres-paris/index.html',
            'de': 'de/besten-bootsfahrten-mit-abendessen-paris/index.html',
            'es': 'es/mejores-cruceros-con-cena-paris/index.html',
            'it': 'it/migliori-crociere-con-cena-senna-parigi/index.html',
            'ja': 'ja/パリのベスト-ディナ-クル-ズ/index.html',
            'nl': 'nl/beste-boottochten-seine-met-diner-parijs/index.html',
            'pl': 'pl/najlepsze-rejsy-z-obiadem-paryz/index.html',
            'ro': 'ro/cele-mai-bune-cina-croaziere-paris/index.html'
        },
        'filters': {
            'all': {'en': 'All (10)', 'fr': 'Tous (10)', 'de': 'Alle (10)', 'es': 'Todos (10)', 'it': 'Tutti (10)', 'ja': 'すべて (10)', 'nl': 'Alle (10)', 'pl': 'Wszystkie (10)', 'ro': 'Toate (10)'},
            'tested': {'en': '✓ Personally Tested (5)', 'fr': '✓ Testé en personne (5)', 'de': '✓ Persönlich getestet (5)', 'es': '✓ Probado en persona (5)', 'it': '✓ Testato di persona (5)', 'ja': '✓ 自費実地検証済み (5)', 'nl': '✓ Zelf getest (5)', 'pl': '✓ Osobiście przetestowane (5)', 'ro': '✓ Testat personal (5)'},
            'livemusic': {'en': '🎵 Live Music (5)', 'fr': '🎵 Musique live (5)', 'de': '🎵 Live-Musik (5)', 'es': '🎵 Música en vivo (5)', 'it': '🎵 Musica dal vivo (5)', 'ja': '🎵 生演奏あり (5)', 'nl': '🎵 Live muziek (5)', 'pl': '🎵 Muzyka na żywo (5)', 'ro': '🎵 Muzică live (5)'},
            'under100': {'en': '💶 Under €100 (5)', 'fr': '💶 Moins de 100 € (5)', 'de': '💶 Unter 100 € (5)', 'es': '💶 Menos de 100 € (5)', 'it': '💶 Meno di 100 € (5)', 'ja': '💶 100€未満 (5)', 'nl': '💶 Onder €100 (5)', 'pl': '💶 Poniżej 100 € (5)', 'ro': '💶 Sub 100 € (5)'},
            'gourmet': {'en': '🍷 Gourmet 4-Course (5)', 'fr': '🍷 Menu gourmet 4 plats (5)', 'de': '🍷 Gourmet 4-Gänge (5)', 'es': '🍷 Gourmet 4 platos (5)', 'it': '🍷 Gourmet 4 portate (5)', 'ja': '🍷 本格4コース (5)', 'nl': '🍷 Gourmet 4-gangen (5)', 'pl': '🍷 Wykwintne 4 dania (5)', 'ro': '🍷 Gourmet 4 feluri (5)'}
        },
        'breakdown_title': {
            'fr': 'Analyse Détaillée — Les 10 Meilleurs Dîners-Croisières sur la Seine',
            'de': 'Detaillierte Analyse — Die 10 besten Seine Dinner-Kreuzfahrten',
            'es': 'Análisis Detallado — Los 10 Mejores Cruceros con Cena por el Sena',
            'it': 'Analisi Dettagliata — Le 10 Migliori Crociere con Cena sulla Senna',
            'ja': '徹底詳細分析 — パリ・セーヌ川のベストディナークルーズ10選',
            'nl': 'Gedetailleerde Analyse — De 10 Beste Seine Dinercruises',
            'pl': 'Szczegółowa Analiza — 10 Najlepszych Rejsów z Kolacją po Sekwanie',
            'ro': 'Analiză Detaliată — Cele Mai Bune 10 Croaziere cu Cină pe Sena'
        },
        'toc_deck_label': {
            'fr': 'Comparatif des 10 Dîners-Croisières',
            'de': 'Top 10 Dinner-Kreuzfahrten Vergleich',
            'es': 'Comparativa de los 10 Mejores Cruceros con Cena',
            'it': 'Confronto Top 10 Crociere con Cena',
            'ja': 'ディナークルーズ トップ10比較',
            'nl': 'Top 10 Dinercruises Vergelijking',
            'pl': 'Porównanie 10 Rejsów z Kolacją',
            'ro': 'Comparație Top 10 Croaziere cu Cină'
        }
    },
    'sightseeing': {
        'en_path': 'seine-river-cruises-paris/index.html',
        'deck_id': 'seine-cruise-deck',
        'pages': {
            'fr': 'fr/meilleures-croisieres-seine-paris/index.html',
            'de': 'de/besten-bootsfahrten-seine-paris/index.html',
            'es': 'es/mejores-cruceros-sena-paris/index.html',
            'it': 'it/migliori-crociere-senna-parigi/index.html',
            'ja': 'ja/パリのベスト-セ-ヌ川クル-ズ/index.html',
            'nl': 'nl/beste-boottochten-seine-parijs/index.html',
            'pl': 'pl/najlepsze-rejsy-po-sekwanie-paryz/index.html',
            'ro': 'ro/cele-mai-bune-croaziere-râul-senine-paris/index.html'
        },
        'alias_pages': {
            'fr': 'fr/seine-river-cruises-paris-1/index.html',
            'de': 'de/seine-river-cruises-paris-1/index.html',
            'es': 'es/seine-river-cruises-paris-1/index.html',
            'it': 'it/seine-river-cruises-paris-1/index.html',
            'ja': 'ja/seine-river-cruises-paris-1/index.html',
            'nl': 'nl/seine-river-cruises-paris-1/index.html',
            'pl': 'pl/seine-river-cruises-paris-1/index.html',
            'ro': 'ro/seine-river-cruises-paris-1/index.html'
        },
        'filters': {
            'all': {'en': 'All (10)', 'fr': 'Tous (10)', 'de': 'Alle (10)', 'es': 'Todos (10)', 'it': 'Tutti (10)', 'ja': 'すべて (10)', 'nl': 'Alle (10)', 'pl': 'Wszystkie (10)', 'ro': 'Toate (10)'},
            'tested': {'en': '✓ Personally Tested (5)', 'fr': '✓ Testé en personne (5)', 'de': '✓ Persönlich getestet (5)', 'es': '✓ Probado en persona (5)', 'it': '✓ Testato di persona (5)', 'ja': '✓ 自費実地検証済み (5)', 'nl': '✓ Zelf getest (5)', 'pl': '✓ Osobiście przetestowane (5)', 'ro': '✓ Testat personal (5)'},
            'under20': {'en': '💶 Under €20 (5)', 'fr': '💶 Moins de 20 € (5)', 'de': '💶 Unter 20 € (5)', 'es': '💶 Menos de 20 € (5)', 'it': '💶 Meno di 20 € (5)', 'ja': '💶 20€未満 (5)', 'nl': '💶 Onder €20 (5)', 'pl': '💶 Poniżej 20 € (5)', 'ro': '💶 Sub 20 € (5)'},
            'treats': {'en': '🥂 Drinks & Treats (4)', 'fr': '🥂 Boissons & Gourmandises (4)', 'de': '🥂 Getränke & Snacks (4)', 'es': '🥂 Bebidas y Degustación (4)', 'it': '🥂 Bevande & Degustazione (4)', 'ja': '🥂 ドリンク＆スイーツ (4)', 'nl': '🥂 Drankjes & Snacks (4)', 'pl': '🥂 Drinki i Przekąski (4)', 'ro': '🥂 Băuturi & Gustări (4)'},
            'lunch': {'en': '🍽️ Seated Lunch (1)', 'fr': '🍽️ Déjeuner assis (1)', 'de': '🍽️ Mittagessen (1)', 'es': '🍽️ Almuerzo sentado (1)', 'it': '🍽️ Pranzo servito (1)', 'ja': '🍽️ ランチクルーズ (1)', 'nl': '🍽️ Lunchcruise (1)', 'pl': '🍽️ Rejs z obiadem (1)', 'ro': '🍽️ Prânz la masă (1)'},
            'route': {'en': '🗺️ Hop-On & Canal (2)', 'fr': '🗺️ Hop-On & Canal (2)', 'de': '🗺️ Hop-On & Kanal (2)', 'es': '🗺️ Hop-On y Canal (2)', 'it': '🗺️ Hop-On e Canale (2)', 'ja': '🗺️ 乗り降り自由＆運河 (2)', 'nl': '🗺️ Hop-on & Kanaal (2)', 'pl': '🗺️ Hop-On i Kanał (2)', 'ro': '🗺️ Hop-On & Canal (2)'},
            'private': {'en': '🛥️ Private Boat (1)', 'fr': '🛥️ Bateau privé (1)', 'de': '🛥️ Privates Boot (1)', 'es': '🛥️ Barco privado (1)', 'it': '🛥️ Barca privata (1)', 'ja': '🛥️ プライベート貸切 (1)', 'nl': '🛥️ Privéboot (1)', 'pl': '🛥️ Prywatna łódź (1)', 'ro': '🛥️ Barcă privată (1)'}
        },
        'breakdown_title': {
            'fr': 'Analyse Détaillée — Les 10 Meilleures Croisières Promenade sur la Seine',
            'de': 'Detaillierte Analyse — Die 10 besten Seine Sightseeing-Bootsfahrten',
            'es': 'Análisis Detallado — Los 10 Mejores Cruceros Panorámicos por el Sena',
            'it': 'Analisi Dettagliata — Le 10 Migliori Crociere Panoramiche sulla Senna',
            'ja': '徹底詳細分析 — パリ・セーヌ川の定番遊覧クルーズ10選',
            'nl': 'Gedetailleerde Analyse — De 10 Beste Seine Rondvaarten',
            'pl': 'Szczegółowa Analiza — 10 Najlepszych Rejsów Wycieczkowych po Sekwanie',
            'ro': 'Analiză Detaliată — Cele Mai Bune 10 Croaziere Panoramice pe Sena'
        },
        'toc_deck_label': {
            'fr': 'Comparatif des 10 Croisières Promenade',
            'de': 'Top 10 Sightseeing-Bootsfahrten Vergleich',
            'es': 'Comparativa de los 10 Mejores Cruceros Panorámicos',
            'it': 'Confronto Top 10 Crociere Panoramiche',
            'ja': '観光クルーズ トップ10比較',
            'nl': 'Top 10 Rondvaarten Vergelijking',
            'pl': 'Porównanie 10 Rejsów Wycieczkowych',
            'ro': 'Comparație Top 10 Croaziere Panoramice'
        }
    },
    'amsterdam': {
        'en_path': 'canal-cruises-amsterdam/index.html',
        'deck_id': 'cruise-comparison-deck',
        'pages': {
            'fr': 'fr/meilleures-croisieres-amsterdam/index.html',
            'de': 'de/besten-grachtenfahrten-amsterdam/index.html',
            'es': 'es/mejores-cruceros-canales-amsterdam/index.html',
            'it': 'it/migliori-crociere-canali-amsterdam/index.html',
            'ja': 'ja/ベスト運河クル-ズ-アムステルダム/index.html',
            'nl': 'nl/beste-roondvarten-grachten-amsterdam/index.html',
            'pl': 'pl/najlepsze-rejsy-po-kanałach-amsterdam/index.html',
            'ro': 'ro/cele-mai-bune-croaziere-canal-amsterdam/index.html'
        },
        'filters': {
            'all': {'en': 'All (10)', 'fr': 'Tous (10)', 'de': 'Alle (10)', 'es': 'Todos (10)', 'it': 'Tutti (10)', 'ja': 'すべて (10)', 'nl': 'Alle (10)', 'pl': 'Wszystkie (10)', 'ro': 'Toate (10)'},
            'sightseeing': {'en': '🏆 Sightseeing (3)', 'fr': '🏆 Visite classique (3)', 'de': '🏆 Sightseeing (3)', 'es': '🏆 Panorámicos (3)', 'it': '🏆 Panoramica (3)', 'ja': '🏆 定番観光 (3)', 'nl': '🏆 Rondvaart (3)', 'pl': '🏆 Klasyczne (3)', 'ro': '🏆 Panoramice (3)'},
            'drinks': {'en': '🧀 Drinks & Cheese (4)', 'fr': '🧀 Boissons & Fromage (4)', 'de': '🧀 Drinks & Käse (4)', 'es': '🧀 Bebidas y Queso (4)', 'it': '🧀 Bevande & Formaggi (4)', 'ja': '🧀 ドリンク＆チーズ (4)', 'nl': '🧀 Drankjes & Kaas (4)', 'pl': '🧀 Drinki i Sery (4)', 'ro': '🧀 Băuturi & Brânzeturi (4)'},
            'dining': {'en': '🍷 Dinner & Pizza (2)', 'fr': '🍷 Dîner & Pizza (2)', 'de': '🍷 Dinner & Pizza (2)', 'es': '🍷 Cena y Pizza (2)', 'it': '🍷 Cena & Pizza (2)', 'ja': '🍷 ディナー＆ピザ (2)', 'nl': '🍷 Diner & Pizza (2)', 'pl': '🍷 Kolacja i Pizza (2)', 'ro': '🍷 Cină & Pizza (2)'},
            'specialty': {'en': '✨ Specialty & 420 (1)', 'fr': '✨ Spécialité & 420 (1)', 'de': '✨ Spezial & 420 (1)', 'es': '✨ Especial y 420 (1)', 'it': '✨ Speciali & 420 (1)', 'ja': '✨ 特別・420対応 (1)', 'nl': '✨ Speciaal & 420 (1)', 'pl': '✨ Specjalne i 420 (1)', 'ro': '✨ Speciale & 420 (1)'}
        },
        'breakdown_title': {
            'fr': 'Analyse Détaillée — Les 10 Meilleures Croisières sur les Canaux d\'Amsterdam',
            'de': 'Detaillierte Analyse — Die 10 besten Grachtenfahrten in Amsterdam',
            'es': 'Análisis Detallado — Los 10 Mejores Cruceros por los Canales de Ámsterdam',
            'it': 'Analisi Dettagliata — Le 10 Migliori Crociere sui Canali di Amsterdam',
            'ja': '徹底詳細分析 — アムステルダムのベスト運河クルーズ10選',
            'nl': 'Gedetailleerde Analyse — De 10 Beste Rondvaarten in Amsterdam',
            'pl': 'Szczegółowa Analiza — 10 Najlepszych Rejsów po Kanałach Amsterdamu',
            'ro': 'Analiză Detaliată — Cele Mai Bune 10 Croaziere pe Canalele din Amsterdam'
        },
        'toc_deck_label': {
            'fr': 'Comparatif des 10 Croisières sur les Canaux',
            'de': 'Top 10 Grachtenfahrten Vergleich',
            'es': 'Comparativa de los 10 Mejores Cruceros por Canales',
            'it': 'Confronto Top 10 Crociere sui Canali',
            'ja': '運河クルーズ トップ10比較',
            'nl': 'Top 10 Rondvaarten Vergelijking',
            'pl': 'Porównanie 10 Rejsów po Kanałach',
            'ro': 'Comparație Top 10 Croaziere pe Canale'
        }
    },
    'london': {
        'en_path': 'thames-river-cruises-london/index.html',
        'deck_id': 'cruise-comparison-deck',
        'pages': {
            'fr': 'fr/croisières-sur-la-tamise-à-londres/index.html',
            'de': 'de/themse-kreuzfahrten-london/index.html',
            'es': 'es/mejores-cruceros-tamesis-londres/index.html',
            'it': 'it/crociere-sul-fiume-tamigi-a-londra/index.html',
            'ja': 'ja/ロンドンのテムズ川クル-ズ/index.html',
            'nl': 'nl/beste-boottochten-theems-londen/index.html',
            'pl': 'pl/rejsy-po-tamizie-londyn/index.html',
            'ro': 'ro/cele-mai-bune-croaziere-râul-tamisa-londra/index.html'
        },
        'filters': {
            'all': {'en': 'All (10)', 'fr': 'Tous (10)', 'de': 'Alle (10)', 'es': 'Todos (10)', 'it': 'Tutti (10)', 'ja': 'すべて (10)', 'nl': 'Alle (10)', 'pl': 'Wszystkie (10)', 'ro': 'Toate (10)'},
            'sightseeing': {'en': '🏆 Sightseeing (4)', 'fr': '🏆 Visite guidée (4)', 'de': '🏆 Sightseeing (4)', 'es': '🏆 Panorámicos (4)', 'it': '🏆 Panoramica (4)', 'ja': '🏆 定番観光 (4)', 'nl': '🏆 Rondvaart (4)', 'pl': '🏆 Klasyczne (4)', 'ro': '🏆 Panoramice (4)'},
            'dining': {'en': '🍷 Lunch & Dinner (4)', 'fr': '🍷 Déjeuner & Dîner (4)', 'de': '🍷 Lunch & Dinner (4)', 'es': '🍷 Almuerzo y Cena (4)', 'it': '🍷 Pranzo & Cena (4)', 'ja': '🍷 ランチ＆ディナー (4)', 'nl': '🍷 Lunch & Diner (4)', 'pl': '🍷 Obiad i Kolacja (4)', 'ro': '🍷 Prânz & Cină (4)'},
            'speedboat': {'en': '⚡ Speedboats (2)', 'fr': '⚡ Hors-bord (2)', 'de': '⚡ Speedboote (2)', 'es': '⚡ Lanchas rápidas (2)', 'it': '⚡ Motoscafi veloci (2)', 'ja': '⚡ 高速ボート (2)', 'nl': '⚡ Speedboten (2)', 'pl': '⚡ Szybkie łodzie (2)', 'ro': '⚡ Șalupe rapide (2)'}
        },
        'breakdown_title': {
            'fr': 'Analyse Détaillée — Les 10 Meilleures Croisières sur la Tamise à Londres',
            'de': 'Detaillierte Analyse — Die 10 besten Themse-Kreuzfahrten in London',
            'es': 'Análisis Detallado — Los 10 Mejores Cruceros por el Támesis en Londres',
            'it': 'Analisi Dettagliata — Le 10 Migliori Crociere sul Tamigi a Londra',
            'ja': '徹底詳細分析 — ロンドンのベストテムズ川クルーズ10選',
            'nl': 'Gedetailleerde Analyse — De 10 Beste Boottochten op de Theems in Londen',
            'pl': 'Szczegółowa Analiza — 10 Najlepszych Rejsów po Tamizie w Londynie',
            'ro': 'Analiză Detaliată — Cele Mai Bune 10 Croaziere pe Tamisa din Londra'
        },
        'toc_deck_label': {
            'fr': 'Comparatif des 10 Croisières sur la Tamise',
            'de': 'Top 10 Themse-Kreuzfahrten Vergleich',
            'es': 'Comparativa de los 10 Mejores Cruceros por el Támesis',
            'it': 'Confronto Top 10 Crociere sul Tamigi',
            'ja': 'テムズ川クルーズ トップ10比較',
            'nl': 'Top 10 Theems Boottochten Vergelijking',
            'pl': 'Porównanie 10 Rejsów po Tamizie',
            'ro': 'Comparație Top 10 Croaziere pe Tamisa'
        }
    }
}

COMMON_I18N = {
    'fr': {
        'bc_home': 'Accueil',
        'kicker': '✓ 2026 Testé sur le terrain',
        'author_line': 'Par <a href="/fr/a-propos" target="_blank">Adam Dimitrov</a> — Fondateur & Enquêteur en chef',
        'author_role': 'Tests indépendants sur le terrain • Photos & Vidéos originales • Avis impartiaux',
        'updated': 'Dernière mise à jour : 1 nov. 2026',
        'filter_label': 'Filtres :',
        'btn_check': 'Vérifier les disponibilités →',
        'trust_micro': '⚡ QR instantané • 🛡️ Annulation 24h gratuite',
        'read_review': 'Lire l\'avis ↓',
        'per_person': 'par personne',
        'best_for': 'Idéal pour :',
        'toc_title': 'Table des matières',
        'verified_badge': '✓ Testé en personne'
    },
    'de': {
        'bc_home': 'Startseite',
        'kicker': '✓ 2026 Im Feld getesteter Vergleich',
        'author_line': 'Von <a href="/de/uber-uns" target="_blank">Adam Dimitrov</a> — Gründer & Chefermittler',
        'author_role': 'Unabhängige Tests vor Ort • Eigene Fotos & Videos • Ehrliche Urteile',
        'updated': 'Zuletzt aktualisiert: 1. Nov. 2026',
        'filter_label': 'Filter:',
        'btn_check': 'Verfügbarkeit prüfen →',
        'trust_micro': '⚡ Sofortiges Smartphone-Ticket • 🛡️ Kostenlose Stornierung bis 24h',
        'read_review': 'Rezension lesen ↓',
        'per_person': 'pro Person',
        'best_for': 'Ideal für:',
        'toc_title': 'Inhaltsverzeichnis',
        'verified_badge': '✓ Persönlich getestet'
    },
    'es': {
        'bc_home': 'Inicio',
        'kicker': '✓ 2026 Comparación probada en campo',
        'author_line': 'Por <a href="/es/acerca" target="_blank">Adam Dimitrov</a> — Fundador e Investigador Principal',
        'author_role': 'Evaluación en persona • Fotos y vídeos originales • Opiniones imparciales',
        'updated': 'Última actualización: 1 de nov. de 2026',
        'filter_label': 'Filtros:',
        'btn_check': 'Consultar disponibilidad →',
        'trust_micro': '⚡ Entrada móvil instantánea • 🛡️ Cancelación gratuita 24h',
        'read_review': 'Leer reseña ↓',
        'per_person': 'por persona',
        'best_for': 'Ideal para:',
        'toc_title': 'Tabla de contenidos',
        'verified_badge': '✓ Probado en persona'
    },
    'it': {
        'bc_home': 'Home',
        'kicker': '✓ 2026 Confronto testato sul campo',
        'author_line': 'Di <a href="/it/su-di-noi" target="_blank">Adam Dimitrov</a> — Fondatore e Investigatore Principale',
        'author_role': 'Testato sul campo • Foto e video originali • Recensioni indipendenti',
        'updated': 'Ultimo aggiornamento: 1 nov 2026',
        'filter_label': 'Filtri:',
        'btn_check': 'Verifica disponibilità →',
        'trust_micro': '⚡ Biglietto mobile istantaneo • 🛡️ Cancellazione gratuita 24h',
        'read_review': 'Leggi recensione ↓',
        'per_person': 'a persona',
        'best_for': 'Ideale per:',
        'toc_title': 'Indice dei contenuti',
        'verified_badge': '✓ Testato di persona'
    },
    'ja': {
        'bc_home': 'ホーム',
        'kicker': '✓ 2026 現地実地検証済み比較',
        'author_line': '著者：<a href="/ja/について" target="_blank">Adam Dimitrov</a> — 創設者 兼 主席調査員',
        'author_role': '自費実地テスト実施 • オリジナル写真・動画収録 • 中立な徹底検証',
        'updated': '最終更新日：2026年11月1日',
        'filter_label': '絞り込み:',
        'btn_check': '空き状況を確認する →',
        'trust_micro': '⚡ 即時スマホQR入場 • 🛡️ 24時間前まで無料キャンセル',
        'read_review': '詳細レビューを読む ↓',
        'per_person': '1名あたり',
        'best_for': 'おすすめの対象:',
        'toc_title': '目次',
        'verified_badge': '✓ 自費実地検証済み'
    },
    'nl': {
        'bc_home': 'Home',
        'kicker': '✓ 2026 Getest in de praktijk',
        'author_line': 'Door <a href="/nl/over-uns" target="_blank">Adam Dimitrov</a> — Oprichter & Hoofdonderzoeker',
        'author_role': 'Zelf getest in het veld • Originele foto\'s en video\'s • Onafhankelijke reviews',
        'updated': 'Laatst bijgewerkt: 1 nov. 2026',
        'filter_label': 'Filters:',
        'btn_check': 'Beschikbaarheid controleren →',
        'trust_micro': '⚡ Direct mobiel ticket • 🛡️ Gratis annuleren tot 24u',
        'read_review': 'Review lezen ↓',
        'per_person': 'per persoon',
        'best_for': 'Ideaal voor:',
        'toc_title': 'Inhoudsopgave',
        'verified_badge': '✓ Zelf getest'
    },
    'pl': {
        'bc_home': 'Strona główna',
        'kicker': '✓ 2026 Porównanie przetestowane w terenie',
        'author_line': 'Autor: <a href="/pl/o" target="_blank">Adam Dimitrov</a> — Założyciel i Główny Detektyw',
        'author_role': 'Osobiste testy w terenie • Oryginalne zdjęcia i filmy • Niezależne recenzje',
        'updated': 'Ostatnia aktualizacja: 1 listopada 2026',
        'filter_label': 'Filtry:',
        'btn_check': 'Sprawdź dostępność →',
        'trust_micro': '⚡ Natychmiastowy bilet QR • 🛡️ Bezpłatne odwołanie do 24h',
        'read_review': 'Przeczytaj recenzję ↓',
        'per_person': 'za osobę',
        'best_for': 'Idealne dla:',
        'toc_title': 'Spis treści',
        'verified_badge': '✓ Osobiście przetestowane'
    },
    'ro': {
        'bc_home': 'Acasă',
        'kicker': '✓ 2026 Comparație testată pe teren',
        'author_line': 'De <a href="/ro/despre" target="_blank">Adam Dimitrov</a> — Fondator și Investigator Șef',
        'author_role': 'Testare personală pe teren • Fotografii și clipuri originale • Recenzii independente',
        'updated': 'Ultima actualizare: 1 nov. 2026',
        'filter_label': 'Filtre:',
        'btn_check': 'Verifică disponibilitatea →',
        'trust_micro': '⚡ Bilet instant pe telefon • 🛡️ Anulare gratuită cu 24h înainte',
        'read_review': 'Citește recenzia ↓',
        'per_person': 'de persoană',
        'best_for': 'Ideal pentru:',
        'toc_title': 'Cuprins',
        'verified_badge': '✓ Testat personal'
    }
}

def extract_en_deck_cards(en_soup):
    deck = en_soup.find(class_='ltt-deck-container')
    if not deck:
        return []
    cards = deck.find_all(class_='bpa-card')
    card_data = []
    for c in cards:
        cid = c.get('id', '')
        cat = c.get('data-cat', 'all')
        
        # Media slider
        media = c.find(class_='bpa-media')
        slider_html = str(media) if media else ""
        
        # Rank tag
        rank_tag = c.find(class_='bpa-rank-tag')
        rank_text = rank_tag.get_text(strip=True) if rank_tag else ""
        
        # Kicker
        kicker = c.find(class_='bpa-kicker')
        kicker_html = ''.join(str(child) for child in kicker.children) if kicker else ""
        
        # Title
        title_tag = c.find(class_='bpa-title')
        title_text = title_tag.get_text(strip=True) if title_tag else ""
        href_jump = title_tag.get('href', '') if title_tag else ""
        
        # Reviews line
        rev_line = c.find(class_='bpa-reviews-line')
        rev_html = str(rev_line) if rev_line else ""
        
        # Specs pills
        specs = [s.get_text(strip=True) for s in c.find_all(class_='bpa-sp')]
        
        # Best For
        best_for = c.find(class_='bpa-best-for')
        best_for_text = best_for.get_text(strip=True).replace('🎯Best For:', '').replace('🎯 Best For:', '').strip() if best_for else ""
        
        # Price and affiliate CTA
        cta_cell = c.find(class_='bpa-cta-cell')
        price_tag = cta_cell.find(class_='bpa-price') if cta_cell else None
        price_text = price_tag.get_text(strip=True) if price_tag else ""
        
        btn = cta_cell.find(class_='bpa-btn') if cta_cell else None
        aff_url = btn.get('href', '') if btn else ""
        
        card_data.append({
            'id': cid,
            'cat': cat,
            'slider_html': slider_html,
            'rank_text': rank_text,
            'kicker_html': kicker_html,
            'title_text': title_text,
            'href_jump': href_jump,
            'rev_html': rev_html,
            'specs': specs,
            'best_for_text': best_for_text,
            'price_text': price_text,
            'aff_url': aff_url
        })
    return card_data

def extract_target_page_data(target_soup):
    # 1. H1 and lead copy
    h1 = target_soup.find('h1')
    h1_text = h1.get_text(strip=True) if h1 else ""
    
    intro_sec = target_soup.find(class_='container-intro-section') or target_soup.find(class_='rich-text-block-36')
    lead_copy_html = ""
    if intro_sec:
        ps = intro_sec.find_all('p')
        lead_copy_html = ''.join(str(p) for p in ps[:3])
    if not lead_copy_html:
        lead_copy_html = "<p>Discover the finest tested cruises with our comprehensive undercover evaluation.</p>"

    # 2. Extract 10 table rows for localized titles, prices, and links
    comp = target_soup.find(class_='comparison-table')
    rows = comp.find_all(class_=lambda c: c and 'table-row-' in c) if comp else []
    
    row_data = []
    for r in rows:
        cells = r.find_all(class_=lambda c: c and ('grid-cell' in c or 'content-wrap' in c))
        # Find title cell
        t_text = ""
        p_text = ""
        link_url = ""
        for cell in cells:
            txt = cell.get_text(" ", strip=True)
            if re.match(r'^\d+\.', txt) and len(txt) > 5 and not t_text:
                t_text = txt
            if any(char.isdigit() for char in txt) and ('€' in txt or '£' in txt or 'ユーロ' in txt) and not p_text:
                p_text = txt.replace('ⓘ', '').strip()
            a_tag = cell.find('a', href=True)
            if a_tag and not link_url and ('tiqets.com' in a_tag['href'] or 'getyourguide.com' in a_tag['href'] or 'fareharbor.com' in a_tag['href'] or 'tp.media' in a_tag['href']):
                link_url = a_tag['href']
        
        row_data.append({
            'title': t_text,
            'price': p_text,
            'url': link_url
        })

    # 3. Extract in-depth review containers from blog section
    blog = target_soup.find(class_='blog-section') or target_soup.find(class_='blog-section-2')
    containers = blog.find_all(class_='container') if blog else []
    
    # Also extract intro articles (before item 1) and buying guide / FAQ (after item 10)
    cr = blog.find(class_='content-right_blog') if blog else None
    intro_article_html = ""
    if cr:
        first_block = cr.find(class_='w-layout-blockcontainer') or cr.find(class_='w-richtext')
        if first_block and first_block != containers[0] if containers else False:
            intro_article_html = str(first_block)

    return {
        'h1_text': h1_text,
        'lead_copy_html': lead_copy_html,
        'rows': row_data,
        'containers': containers,
        'intro_article_html': intro_article_html
    }

def compile_guide_page(dest_key, lang, target_rel_path):
    dest_cfg = DEST_CONFIGS[dest_key]
    en_path = os.path.join(BASE_DIR, dest_cfg['en_path'])
    target_abs = os.path.join(BASE_DIR, target_rel_path)

    print(f"\nCompiling [{dest_key.upper()}] [{lang.upper()}]: {target_rel_path} ...")
    
    with open(en_path, 'r', encoding='utf-8') as f:
        en_soup = BeautifulSoup(f.read(), 'html.parser')

    with open(target_abs, 'r', encoding='utf-8') as f:
        target_soup = BeautifulSoup(f.read(), 'html.parser')

    # 1. Base head metadata
    head = target_soup.find('head')
    title = head.find('title').get_text(strip=True) if head and head.find('title') else en_soup.find('title').get_text(strip=True)
    meta_desc_tag = head.find('meta', {'name': 'description'}) if head else None
    meta_desc = meta_desc_tag.get('content', '') if meta_desc_tag else ""
    canonical_tag = head.find('link', rel='canonical') if head else None
    canonical_href = canonical_tag.get('href') if canonical_tag else f"https://www.thecruisedetective.com/{target_rel_path.replace('/index.html', '')}"

    # 2. Localized Navbar and Footer
    navbar = target_soup.find('header', class_='ltt-navbar')
    navbar_html = str(navbar) if navbar else str(en_soup.find('header', class_='ltt-navbar'))
    
    footer = target_soup.find('section', class_='footer-dark')
    footer_html = str(footer) if footer else str(en_soup.find('section', class_='footer-dark'))

    t = COMMON_I18N[lang]
    target_data = extract_target_page_data(target_soup)
    en_cards = extract_en_deck_cards(en_soup)

    # 3. Clean Card Hero Component
    h1_display = target_data['h1_text'] if target_data['h1_text'] else en_soup.find('h1').get_text(strip=True)
    
    # Filter buttons
    filter_btns_html = []
    f_dict = dest_cfg['filters']
    for cat_key, labels in f_dict.items():
        is_active = "active" if cat_key == "all" else ""
        btn_label = labels.get(lang, labels['en'])
        filter_btns_html.append(f'<button class="ltt-tab-btn {is_active}" data-cat="{cat_key}" onclick="lttFilterSafaris(\'{cat_key}\', this)" type="button">{btn_label}</button>')

    clean_hero_html = f'''
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
.ltt-integrated-filter-bar {{
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding-top: 14px;
  border-top: 1px solid #e2e8f0;
}}
.ltt-filter-label {{
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #64748b;
}}
.ltt-integrated-pills {{
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}}
.ltt-tab-btn {{
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #334155;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.15s ease;
}}
.ltt-tab-btn:hover, .ltt-tab-btn.active {{
  background: #0f172a;
  color: #ffffff;
  border-color: #0f172a;
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
        <span class="ltt-bc-current">{h1_display}</span>
      </nav>
      <span class="ltt-hero-kicker-badge">{t['kicker']}</span>
    </div>
    <h1 class="ltt-editorial-h1">{h1_display}</h1>
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
      {target_data['lead_copy_html']}
    </div>
    <div class="ltt-integrated-filter-bar">
      <span class="ltt-filter-label">{t['filter_label']}</span>
      <div class="ltt-integrated-pills">
        {''.join(filter_btns_html)}
      </div>
    </div>
  </div>
</div>'''

    # 4. Construct the 10 Deck Cards (.bpa-card)
    deck_cards_html = []
    short_titles = []
    
    for idx, c in enumerate(en_cards):
        # Localized title from target table row if available
        row = target_data['rows'][idx] if idx < len(target_data['rows']) else {}
        card_title = row.get('title') if row.get('title') else c['title_text']
        short_titles.append(card_title)
        
        # Localized price
        card_price = row.get('price') if row.get('price') else c['price_text']
        
        # Affiliate URL (preserve authentic tracking)
        card_url = row.get('url') if row.get('url') else c['aff_url']
        if not card_url:
            card_url = c['aff_url']

        specs_html = ''.join([f'<span class="bpa-sp">{s}</span>' for s in c['specs']])

        deck_cards_html.append(f'''
    <div class="bpa-card" data-cat="{c['cat']}" id="{c['id']}">
      <div class="bpa-main">
        {c['slider_html']}
        <div class="bpa-info">
          <div class="bpa-kicker">{c['kicker_html']}</div>
          <a class="bpa-title" href="{c['href_jump']}">{card_title}</a>
          {c['rev_html']}
          <div class="bpa-specs-row">
            {specs_html}
          </div>
          <div class="bpa-best-for">
            🎯 <strong>{t['best_for']}</strong> {c['best_for_text']}
          </div>
        </div>
        <div class="bpa-cta-cell">
          <div>
            <div class="bpa-price">{card_price}</div>
            <div class="bpa-psub">{t['per_person']}</div>
          </div>
          <a class="bpa-btn" href="{card_url}" rel="noopener nofollow sponsored" target="_blank">
            {t['btn_check']}
          </a>
          <div class="bpa-trust-micro">{t['trust_micro']}</div>
          <a class="bpa-sublink" href="{c['href_jump']}">{t['read_review']}</a>
        </div>
      </div>
    </div>''')

    comparison_section_html = f'''
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
    .bpa-deck-wrap {{
      display: flex !important;
      flex-direction: column !important;
      gap: 16px !important;
      margin-top: 14px !important;
    }}
    .bpa-card {{
      background: #ffffff !important;
      border: 1px solid #e2e8f0 !important;
      border-radius: 16px !important;
      padding: 16px !important;
      box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04) !important;
      box-sizing: border-box !important;
    }}
    .bpa-main {{
      display: grid !important;
      grid-template-columns: 300px minmax(0, 1fr) 185px !important;
      gap: 20px !important;
      align-items: stretch !important;
    }}
    @media (max-width: 991px) {{
      .bpa-main {{
        grid-template-columns: 1fr !important;
        gap: 16px !important;
      }}
    }}
    </style>
    <div class="ltt-deck-container" id="{dest_cfg['deck_id']}">
      <div class="bpa-deck-wrap">
        {''.join(deck_cards_html)}
      </div>
    </div>
  </div>
</div>'''

    # 5. Review Details Cards (.bpa-details-card) for Blog Section
    details_cards_html = []
    containers = target_data['containers']
    
    for idx, c in enumerate(en_cards):
        row = target_data['rows'][idx] if idx < len(target_data['rows']) else {}
        card_title = row.get('title') if row.get('title') else c['title_text']
        card_price = row.get('price') if row.get('price') else c['price_text']
        card_url = row.get('url') if row.get('url') else c['aff_url']
        jump_id = c['href_jump'].replace('#', '')

        # Localized review content from container if exists
        review_body_html = ""
        if idx < len(containers):
            review_body_html = str(containers[idx])
        else:
            review_body_html = f"<p>Detailed undercover audit and tasting notes for {card_title}.</p>"

        details_cards_html.append(f'''
          <details class="bpa-details-card" data-cat="{c['cat']}" id="{jump_id}" open="" style="background: #fff; border: 1px solid #e2e8f0; border-radius: 16px; margin-bottom: 24px; padding: 20px; box-shadow: 0 4px 20px -4px rgba(15, 23, 42, 0.05); position: relative;">
            <summary class="bpa-details-summary" style="cursor: pointer; list-style: none;">
              <div class="bpa-details-top-row" style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                <span class="bpa-rank-tag bpa-gold" style="position: static !important; font-size: 11px; padding: 4px 10px; font-weight: 800; border-radius: 9999px;">{c['rank_text']}</span>
                <div class="bpa-kicker" style="font-size: 13px; color: #64748b;">{c['kicker_html']}</div>
              </div>
              <h3 class="bpa-details-title" style="font-size: 22px; font-weight: 800; color: #0f172a; margin: 4px 0 6px 0;">{card_title}</h3>
            </summary>
            <div class="bpa-details-body" style="margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 16px;">
              <div class="ltt-editorial-review-block">
                {review_body_html}
              </div>
              <div class="ltt-buy-card" style="margin-top: 20px; padding: 18px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                <div>
                  <div style="font-size: 20px; font-weight: 800; color: #0f172a;">{card_price}</div>
                  <div style="font-size: 12px; color: #64748b;">{t['per_person']} • {t['trust_micro']}</div>
                </div>
                <a class="bpa-btn" href="{card_url}" rel="noopener nofollow sponsored" target="_blank" style="background: linear-gradient(135deg, #dfa732 0%, #b88214 100%) !important; color: #fff !important; font-weight: 800; padding: 12px 24px; border-radius: 9999px !important; text-decoration: none;">
                  {t['btn_check']}
                </a>
              </div>
            </div>
          </details>''')

    bd_title = dest_cfg['breakdown_title'].get(lang, dest_cfg['breakdown_title']['fr'])
    toc_deck = dest_cfg['toc_deck_label'].get(lang, dest_cfg['toc_deck_label']['fr'])

    blog_section_html = f'''
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
          {target_data['intro_article_html']}
          
          <div class="bpa-breakdown-top-bar" id="breakdown-header" style="margin: 28px 0 20px 0;">
            <div>
              <h2 class="bpa-breakdown-heading" style="font-size: 26px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0;">{bd_title}</h2>
            </div>
          </div>
          
          <div id="in-depth-reviews">
            {''.join(details_cards_html)}
          </div>
        </div>
      </div>
    </div>
  </div>
</div>'''

    top_pick_card = en_cards[0]
    top_pick_url = target_data['rows'][0].get('url') if target_data['rows'] else top_pick_card['aff_url']
    if not top_pick_url:
        top_pick_url = top_pick_card['aff_url']

    sticky_bar_html = f'''
<aside class="hybrid-sticky-bar" id="sticky-bar">
  <div class="hybrid-sticky-inner">
    <div class="hybrid-sticky-info">
      <span class="hybrid-sticky-top-badge">🏆 TOP PICK</span>
      <span class="hybrid-sticky-title">{short_titles[0]}</span>
      <span class="hybrid-sticky-price">{top_pick_card['price_text']}</span>
    </div>
    <div class="hybrid-sticky-actions">
      <a class="hybrid-sticky-btn ltt-sticky-cta" href="{top_pick_url}" rel="noopener nofollow sponsored" target="_blank">
        {t['btn_check']}
      </a>
    </div>
  </div>
</aside>
<div class="hybrid-sheet-backdrop" id="hybridBackdrop"></div>'''

    # Complete HTML assembly
    full_html = f'''<!DOCTYPE html>
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

{clean_hero_html}
{comparison_section_html}
{blog_section_html}
{footer_html}
{sticky_bar_html}

<script src="/js/ltt-nav.js"></script>
<script src="/webflow-sync.js"></script>
<script>
window.LTT_PAGE_CONFIG = {{
  "deckId": "{dest_cfg['deck_id']}",
  "tocDeckLabel": "{toc_deck}",
  "tocBreakdownLabel": "{bd_title}",
  "shortTitles": {short_titles}
}};
</script>
</body>
</html>
'''

    with open(target_abs, 'w', encoding='utf-8') as f:
        f.write(full_html)
    print(f"[{dest_key.upper()}] [{lang.upper()}] Successfully compiled ({len(full_html)} bytes).")

    # If alias pages exist (e.g. seine-river-cruises-paris-1), synchronize them too
    if 'alias_pages' in dest_cfg and lang in dest_cfg['alias_pages']:
        alias_rel = dest_cfg['alias_pages'][lang]
        alias_abs = os.path.join(BASE_DIR, alias_rel)
        if os.path.exists(alias_abs):
            with open(alias_abs, 'w', encoding='utf-8') as f:
                f.write(full_html)
            print(f"  -> Synchronized alias: {alias_rel}")

def main():
    for dest_key in ['dinner', 'sightseeing', 'amsterdam', 'london']:
        cfg = DEST_CONFIGS[dest_key]
        for lang in LANGS:
            target_rel = cfg['pages'][lang]
            compile_guide_page(dest_key, lang, target_rel)

if __name__ == '__main__':
    main()
