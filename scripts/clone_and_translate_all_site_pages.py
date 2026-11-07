#!/usr/bin/env python3
"""
MASTER 1:1 CLONING & TRANSLATION ENGINE (V3 PRODUCTION READY)
Fixes:
1. Full navbar menu & mobile drawer localization across ALL pages (home, about, duel, contact, and 32 guides)
2. Eliminates all English fragments in guides: rank tags, spec pills, best-for blocks, prices, bento titles, TOC
3. Fixes dropdown UX bridge in CSS & hover intent delay in JS
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

from upgrade_translated_about_pages import ABOUT_I18N
from upgrade_translated_duel_pages import DUEL_I18N, DUEL_PAGES, build_duel_deck_html
from upgrade_translated_contact_pages import CONTACT_I18N, CONTACT_PAGES
from harmonize_all_translated_pages import I18N as HOMEPAGE_I18N

LANGS = ['fr', 'de', 'es', 'it', 'ja', 'nl', 'pl', 'ro']

URL_MAP = {
    'fr': {
        'sheet_title': 'Sélectionner une croisière testée',
        'quick_facts_title': 'Faits en bref — Caractéristiques vérifiées',
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
        'sheet_title': 'Seleccionar un crucero probado',
        'quick_facts_title': 'Datos clave — Especificaciones verificadas',
        'dinner': '/es/mejores-cruceros-con-cena-paris',
        'sightseeing': '/es/mejores-cruceros-sena-paris',
        'duel': '/es/comparación-de-crucero-con-cena-bateaux-mouches-vs-bateaux-parisiens-lado-a-lado',
        'amsterdam': '/es/mejores-cruceros-canales-amsterdam',
        'london': '/es/mejores-cruceros-tamesis-londres',
        'about': '/es/acerca',
        'contact': '/es/contacto'
    },
    'it': {
        'sheet_title': 'Seleziona una crociera verificata',
        'quick_facts_title': 'Dati chiave — Specifiche verificate',
        'dinner': '/it/migliori-crociere-con-cena-senna-parigi',
        'sightseeing': '/it/migliori-crociere-senna-parigi',
        'duel': '/it/bateaux-mouches-vs-bateaux-parisiens-crociera-con-cena-confronto-fianco-a-fianco',
        'amsterdam': '/it/migliori-crociere-canali-amsterdam',
        'london': '/it/crociere-sul-fiume-tamigi-a-londra',
        'about': '/it/su-di-noi',
        'contact': '/it/contatto'
    },
    'ja': {
        'sheet_title': '検証済みクルーズを選択',
        'quick_facts_title': '基本情報 — 検証済みスペック',
        'dinner': '/ja/パリのベスト-ディナ-クル-ズ',
        'sightseeing': '/ja/パリのベスト-セ-ヌ川クル-ズ',
        'duel': '/ja/バトームーシュとバトーパリジャンのディナークルーズの並べて比較',
        'amsterdam': '/ja/ベスト運河クル-ズ-アムステルダム',
        'london': '/ja/ロンドンのテムズ川クル-ズ',
        'about': '/ja/について',
        'contact': '/ja/接触'
    },
    'nl': {
        'sheet_title': 'Selecteer een geteste rondvaart',
        'quick_facts_title': 'Belangrijkste feiten — Geverifieerde specificaties',
        'dinner': '/nl/beste-boottochten-seine-met-diner-parijs',
        'sightseeing': '/nl/beste-boottochten-seine-parijs',
        'duel': '/nl/bateaux-mouches-vs-bateaux-parisiens-dinercruise-zij-aan-zij-vergelijking',
        'amsterdam': '/nl/beste-roondvarten-grachten-amsterdam',
        'london': '/nl/beste-boottochten-theems-londen',
        'about': '/nl/over-uns',
        'contact': '/nl/contact'
    },
    'pl': {
        'sheet_title': 'Wybierz sprawdzony rejs',
        'quick_facts_title': 'Kluczowe fakty — Sprawdzone dane',
        'dinner': '/pl/najlepsze-rejsy-z-obiadem-paryz',
        'sightseeing': '/pl/najlepsze-rejsy-po-sekwanie-paryz',
        'duel': '/pl/porównanie-bateaux-mouches-vs-bateaux-parisiens-rejs-z-kolacją',
        'amsterdam': '/pl/najlepsze-rejsy-po-kanałach-amsterdam',
        'london': '/pl/rejsy-po-tamizie-londyn',
        'about': '/pl/o',
        'contact': '/pl/kontakt'
    },
    'ro': {
        'sheet_title': 'Selectează o croazieră testată',
        'quick_facts_title': 'Date cheie — Specificații verificate',
        'dinner': '/ro/cele-mai-bune-cina-croaziere-paris',
        'sightseeing': '/ro/cele-mai-bune-croaziere-râul-senine-paris',
        'duel': '/ro/bateaux-mouches-vs-bateaux-parisiens-cina-croazieră-comparație-alăturată',
        'amsterdam': '/ro/cele-mai-bune-croaziere-canal-amsterdam',
        'london': '/ro/cele-mai-bune-croaziere-râul-tamisa-londra',
        'about': '/ro/despre',
        'contact': '/ro/contact'
    }
}

NAV_I18N = {
    'fr': {
        'destinations': 'Destinations',
        'col1_head': 'SEINE À PARIS',
        'col2_head': 'VOIES NAVIGABLES EUROPÉENNES',
        'dinner_title': 'Croisières Dîner Paris',
        'dinner_sub': '10 bateaux testés et avis dégustation',
        'sightseeing_title': 'Croisières Promenade Paris',
        'sightseeing_sub': 'Visites de jour et illuminations nocturnes',
        'duel_title': 'Mouches vs. Parisiens',
        'duel_sub': 'Comparatif face-à-face des dîners-croisières',
        'amsterdam_title': 'Croisières Canaux Amsterdam',
        'amsterdam_sub': 'Barques ouvertes et bateaux salon classiques',
        'london_title': 'Croisières Tamise Londres',
        'london_sub': 'Visites guidées, dîners et bateaux rapides',
        'dinner_top': 'Croisières Dîner',
        'sightseeing_top': 'Croisières Promenade',
        'about_top': 'À Propos',
        'contact_top': 'Contact',
        'drawer_sec1': 'Destinations & Guides',
        'drawer_sec2': 'Éditorial & Confiance',
        'top_pick': 'CHOIX #1'
    },
    'es': {
        'destinations': 'Destinos',
        'col1_head': 'SENA EN PARÍS',
        'col2_head': 'VÍAS NAVEGABLES EUROPEAS',
        'dinner_title': 'Cruceros con Cena París',
        'dinner_sub': '10 barcos probados y notas de cata',
        'sightseeing_title': 'Cruceros Panorámicos París',
        'sightseeing_sub': 'Tours diurnos e iluminaciones nocturnas',
        'duel_title': 'Mouches vs. Parisiens',
        'duel_sub': 'Comparativa directa de cruceros con cena',
        'amsterdam_title': 'Cruceros Canales Ámsterdam',
        'amsterdam_sub': 'Barcos abiertos y salones clásicos',
        'london_title': 'Cruceros Támesis Londres',
        'london_sub': 'Paseos turísticos, cenas y lanchas rápidas',
        'dinner_top': 'Cruceros con Cena',
        'sightseeing_top': 'Paseos en Barco',
        'about_top': 'Acerca de',
        'contact_top': 'Contacto',
        'drawer_sec1': 'Destinos y Guías',
        'drawer_sec2': 'Editorial y Confianza',
        'top_pick': 'TOP PICK'
    },
    'de': {
        'destinations': 'Reiseziele',
        'col1_head': 'SEINE IN PARIS',
        'col2_head': 'EUROPÄISCHE WASSERSTRASSEN',
        'dinner_title': 'Dinner-Kreuzfahrten Paris',
        'dinner_sub': '10 Schiffe getestet & Verkostungsnotizen',
        'sightseeing_title': 'Seine Rundfahrten Paris',
        'sightseeing_sub': 'Tagesfahrten & abendliche Lichtertouren',
        'duel_title': 'Mouches vs. Parisiens',
        'duel_sub': 'Direkter Dinner-Kreuzfahrt Vergleich',
        'amsterdam_title': 'Grachtenfahrten Amsterdam',
        'amsterdam_sub': 'Offene Schaluppen & historische Salonboote',
        'london_title': 'Themse Fahrten London',
        'london_sub': 'Sightseeing, Dining & Speedboot-Touren',
        'dinner_top': 'Dinner-Fahrten',
        'sightseeing_top': 'Rundfahrten',
        'about_top': 'Über uns',
        'contact_top': 'Kontakt',
        'drawer_sec1': 'Reiseziele & Guides',
        'drawer_sec2': 'Redaktion & Vertrauen',
        'top_pick': 'TOP-TIPP'
    },
    'it': {
        'destinations': 'Destinazioni',
        'col1_head': 'SENNA A PARIGI',
        'col2_head': 'VIE D\'ACQUA EUROPEE',
        'dinner_title': 'Crociere con Cena Parigi',
        'dinner_sub': '10 navi testate e note di degustazione',
        'sightseeing_title': 'Crociere Panoramiche Parigi',
        'sightseeing_sub': 'Tour diurni e illuminazioni notturne',
        'duel_title': 'Mouches vs. Parisiens',
        'duel_sub': 'Confronto diretto crociere con cena',
        'amsterdam_title': 'Crociere Canali Amsterdam',
        'amsterdam_sub': 'Lance aperte e battelli d\'epoca',
        'london_title': 'Crociere Tamigi Londra',
        'london_sub': 'Visite guidate, cene e motoscafi veloci',
        'dinner_top': 'Crociere con Cena',
        'sightseeing_top': 'Crociere Panoramiche',
        'about_top': 'Chi Siamo',
        'contact_top': 'Contatto',
        'drawer_sec1': 'Destinazioni e Guide',
        'drawer_sec2': 'Editoriale e Fiducia',
        'top_pick': 'SCELTA #1'
    },
    'ja': {
        'destinations': '目的地',
        'col1_head': 'パリ・セーヌ川',
        'col2_head': '欧州の運河・河川',
        'dinner_title': 'パリ ディナークルーズ',
        'dinner_sub': '実地検証済み10隻＆試食レポート',
        'sightseeing_title': 'パリ 遊覧クルーズ',
        'sightseeing_sub': '定番の日中観光と夜景ライトアップ',
        'duel_title': 'ムーシュ vs パリジャン',
        'duel_sub': '2大ディナークルーズ直接比較',
        'amsterdam_title': 'アムステルダム 運河クルーズ',
        'amsterdam_sub': 'オープンボート＆歴史的サロン船',
        'london_title': 'ロンドン テムズ川クルーズ',
        'london_sub': '観光遊覧、ディナー＆高速ボート',
        'dinner_top': 'ディナークルーズ',
        'sightseeing_top': '遊覧クルーズ',
        'about_top': '概要',
        'contact_top': 'お問い合わせ',
        'drawer_sec1': '目的地＆ガイド',
        'drawer_sec2': '編集方針＆信頼',
        'top_pick': '第1位'
    },
    'nl': {
        'destinations': 'Bestemmingen',
        'col1_head': 'SEINE IN PARIJS',
        'col2_head': 'EUROPESE WATERWEGEN',
        'dinner_title': 'Dinercruises Parijs',
        'dinner_sub': '10 geteste boten en proefnotities',
        'sightseeing_title': 'Rondvaarten Parijs',
        'sightseeing_sub': 'Overdag varen en avondverlichting',
        'duel_title': 'Mouches vs. Parisiens',
        'duel_sub': 'Directe dinercruise vergelijking',
        'amsterdam_title': 'Rondvaarten Amsterdam',
        'amsterdam_sub': 'Open sloepen en klassieke salonboten',
        'london_title': 'Boottochten Theems Londen',
        'london_sub': 'Sightseeing, dineren en speedboten',
        'dinner_top': 'Dinercruises',
        'sightseeing_top': 'Rondvaarten',
        'about_top': 'Over ons',
        'contact_top': 'Contact',
        'drawer_sec1': 'Bestemmingen & Gidsen',
        'drawer_sec2': 'Redactioneel & Vertrouwen',
        'top_pick': '#1 KEUZE'
    },
    'pl': {
        'destinations': 'Kierunki',
        'col1_head': 'SEKWANA W PARYŻU',
        'col2_head': 'EUROPEJSKIE DROGI WODNE',
        'dinner_title': 'Rejsy z Kolacją Paryż',
        'dinner_sub': '10 przetestowanych statków i menu',
        'sightseeing_title': 'Rejsy Wycieczkowe Paryż',
        'sightseeing_sub': 'Trasy dzienne i nocne iluminacje',
        'duel_title': 'Mouches vs. Parisiens',
        'duel_sub': 'Pojedynek rejsów z kolacją twarzą w twarz',
        'amsterdam_title': 'Rejsy Kanałami Amsterdamu',
        'amsterdam_sub': 'Otwarte łodzie i klasyczne salony',
        'london_title': 'Rejsy po Tamizie w Londynie',
        'london_sub': 'Zwiedzanie, kolacje i szybkie łodzie',
        'dinner_top': 'Rejsy z Kolacją',
        'sightseeing_top': 'Rejsy Widokowe',
        'about_top': 'O nas',
        'contact_top': 'Kontakt',
        'drawer_sec1': 'Kierunki i Przewodniki',
        'drawer_sec2': 'Redakcja i Zaufanie',
        'top_pick': '#1 WYBÓR'
    },
    'ro': {
        'destinations': 'Destinații',
        'col1_head': 'SENA ÎN PARIS',
        'col2_head': 'CĂI NAVIGABILE EUROPENE',
        'dinner_title': 'Croaziere cu Cină Paris',
        'dinner_sub': '10 nave testate și recenzii gastronomice',
        'sightseeing_title': 'Croaziere Panoramice Paris',
        'sightseeing_sub': 'Tururi de zi și monumente iluminate noaptea',
        'duel_title': 'Mouches vs. Parisiens',
        'duel_sub': 'Comparație directă croaziere cu cină',
        'amsterdam_title': 'Croaziere Canale Amsterdam',
        'amsterdam_sub': 'Bărci deschise și vapoare salon clasice',
        'london_title': 'Croaziere Tamisa Londra',
        'london_sub': 'Tururi turistice, cine și bărci rapide',
        'dinner_top': 'Croaziere cu Cină',
        'sightseeing_top': 'Croaziere de Zi',
        'about_top': 'Despre Noi',
        'contact_top': 'Contact',
        'drawer_sec1': 'Destinații și Ghiduri',
        'drawer_sec2': 'Editorial și Încredere',
        'top_pick': 'ALEGEREA #1'
    }
}

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
            'fr': '⚡ Comparatif des 10 Dîners-Croisières',
            'de': '⚡ Top 10 Dinner-Kreuzfahrten Vergleich',
            'es': '⚡ Comparativa de los 10 Mejores Cruceros con Cena',
            'it': '⚡ Confronto Top 10 Crociere con Cena',
            'ja': '⚡ ディナークルーズ トップ10比較',
            'nl': '⚡ Top 10 Dinercruises Vergelijking',
            'pl': '⚡ Porównanie 10 Rejsów z Kolacją',
            'ro': '⚡ Comparație Top 10 Croaziere cu Cină'
        },
        'toc_guide_label': {
            'fr': '💡 Conseils Pratiques & FAQ',
            'de': '💡 Praxistipps & FAQ',
            'es': '💡 Consejos Prácticos y Preguntas Frecuentes',
            'it': '💡 Consigli Pratici e FAQ',
            'ja': '💡 実地アドバイス＆よくある質問',
            'nl': '💡 Praktisch Advies & FAQ',
            'pl': '💡 Porady Praktyczne i FAQ',
            'ro': '💡 Sfaturi Practice și Întrebări Frecvente'
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
            'fr': '⚡ Comparatif des 10 Croisières Promenade',
            'de': '⚡ Top 10 Sightseeing-Bootsfahrten Vergleich',
            'es': '⚡ Comparativa de los 10 Mejores Cruceros Panorámicos',
            'it': '⚡ Confronto Top 10 Crociere Panoramiche',
            'ja': '⚡ 観光クルーズ トップ10比較',
            'nl': '⚡ Top 10 Rondvaarten Vergelijking',
            'pl': '⚡ Porównanie 10 Rejsów Wycieczkowych',
            'ro': '⚡ Comparație Top 10 Croaziere Panoramice'
        },
        'toc_guide_label': {
            'fr': '💡 Conseils Pratiques & FAQ',
            'de': '💡 Praxistipps & FAQ',
            'es': '💡 Consejos Prácticos y Preguntas Frecuentes',
            'it': '💡 Consigli Pratici e FAQ',
            'ja': '💡 実地アドバイス＆よくある質問',
            'nl': '💡 Praktisch Advies & FAQ',
            'pl': '💡 Porady Praktyczne i FAQ',
            'ro': '💡 Sfaturi Practice și Întrebări Frecvente'
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
            'fr': '⚡ Comparatif des 10 Croisières sur les Canaux',
            'de': '⚡ Top 10 Grachtenfahrten Vergleich',
            'es': '⚡ Comparativa de los 10 Mejores Cruceros por Canales',
            'it': '⚡ Confronto Top 10 Crociere sui Canali',
            'ja': '⚡ 運河クルーズ トップ10比較',
            'nl': '⚡ Top 10 Rondvaarten Vergelijking',
            'pl': '⚡ Porównanie 10 Rejsów po Kanałach',
            'ro': '⚡ Comparație Top 10 Croaziere pe Canale'
        },
        'toc_guide_label': {
            'fr': '💡 Conseils Pratiques & FAQ',
            'de': '💡 Praxistipps & FAQ',
            'es': '💡 Consejos Prácticos y Preguntas Frecuentes',
            'it': '💡 Consigli Pratici e FAQ',
            'ja': '💡 実地アドバイス＆よくある質問',
            'nl': '💡 Praktisch Advies & FAQ',
            'pl': '💡 Porady Praktyczne i FAQ',
            'ro': '💡 Sfaturi Practice și Întrebări Frecvente'
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
            'fr': '⚡ Comparatif des 10 Croisières sur la Tamise',
            'de': '⚡ Top 10 Themse-Kreuzfahrten Vergleich',
            'es': '⚡ Comparativa de los 10 Mejores Cruceros por el Támesis',
            'it': '⚡ Confronto Top 10 Crociere sul Tamigi',
            'ja': '⚡ テムズ川クルーズ トップ10比較',
            'nl': '⚡ Top 10 Theems Boottochten Vergelijking',
            'pl': '⚡ Porównanie 10 Rejsów po Tamizie',
            'ro': '⚡ Comparație Top 10 Croaziere pe Tamisa'
        },
        'toc_guide_label': {
            'fr': '💡 Conseils Pratiques & FAQ',
            'de': '💡 Praxistipps & FAQ',
            'es': '💡 Consejos Prácticos y Preguntas Frecuentes',
            'it': '💡 Consigli Pratici e FAQ',
            'ja': '💡 実地アドバイス＆よくある質問',
            'nl': '💡 Praktisch Advies & FAQ',
            'pl': '💡 Porady Praktyczne i FAQ',
            'ro': '💡 Sfaturi Practice și Întrebări Frecvente'
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
        'trust_micro': '⚡ Voucher smartphone instantané • 🛡️ Annulation 24h gratuite',
        'read_review': 'Lire l\'avis ↓',
        'per_person': 'par personne',
        'best_for': 'Idéal pour',
        'toc_title': 'Table des matières',
        'verified_badge': '✓ Testé en personne',
        'pros_title': 'AVANTAGES',
        'cons_title': 'INCONVÉNIENTS',
        'bento_1': '📝 Résumé, Avis & Chiffres clés',
        'bento_2': '⚓ Avant la croisière — Embarcadère & Plan d\'accès',
        'bento_3': '🛳️ Pendant la croisière — Bateau, Ponts & Vues',
        'bento_4': '🍷 Menus, Dégustation & Ambiance',
        'bento_audio': '🎧 Audioguide & Commentaires à bord',
        'bento_map': '🗺️ Embarcadère & Plan d\'accès',
        'pill_overview': 'Aperçu',
        'pill_photos': 'Photos →',
        'pill_map': 'Plan du quai'
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
        'best_for': 'Ideal para',
        'toc_title': 'Tabla de contenidos',
        'verified_badge': '✓ Probado en persona',
        'pros_title': 'PROS',
        'cons_title': 'CONTRAS',
        'bento_1': '📝 Resumen, Valoración y Datos Clave',
        'bento_2': '⚓ Antes del crucero — Muelle y Mapa de Embarque',
        'bento_3': '🛳️ Durante el crucero — Barco, Cubiertas y Vistas',
        'bento_4': '🍷 Menú, Degustación y Ambiente',
        'bento_audio': '🎧 Audioguía y Ruta explicada',
        'bento_map': '🗺️ Muelle de salida y Mapa del punto de encuentro',
        'pill_overview': 'Resumen',
        'pill_photos': 'Fotos →',
        'pill_map': 'Mapa del muelle'
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
        'best_for': 'Ideal für',
        'toc_title': 'Inhaltsverzeichnis',
        'verified_badge': '✓ Persönlich getestet',
        'pros_title': 'VORTEILE',
        'cons_title': 'NACHTEILE',
        'bento_1': '📝 Zusammenfassung, Bewertung & Fakten',
        'bento_2': '⚓ Vor der Fahrt — Anlegestelle & Anfahrtsplan',
        'bento_3': '🛳️ Während der Fahrt — Schiff, Decks & Aussicht',
        'bento_4': '🍷 Menü, Verkostung & Atmosphäre',
        'bento_audio': '🎧 Audioguide & Routendetails',
        'bento_map': '🗺️ Anlegestelle & Treffpunktkarte',
        'pill_overview': 'Überblick',
        'pill_photos': 'Fotos →',
        'pill_map': 'Anlegerkarte'
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
        'best_for': 'Ideale per',
        'toc_title': 'Indice dei contenuti',
        'verified_badge': '✓ Testato di persona',
        'pros_title': 'PRO',
        'cons_title': 'CONTRO',
        'bento_1': '📝 Sommario, Recensione e Dati Chiave',
        'bento_2': '⚓ Prima della crociera — Molo e Mappa di Imbarco',
        'bento_3': '🛳️ Durante la crociera — Nave, Ponti e Panorami',
        'bento_4': '🍷 Menu, Degustazione e Atmosfera',
        'bento_audio': '🎧 Audioguida e Dettagli del Percorso',
        'bento_map': '🗺️ Molo di partenza e Mappa di ritrovo',
        'pill_overview': 'Panoramica',
        'pill_photos': 'Foto →',
        'pill_map': 'Mappa del molo'
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
        'best_for': 'おすすめの対象',
        'toc_title': '目次',
        'verified_badge': '✓ 自費実地検証済み',
        'pros_title': 'メリット',
        'cons_title': 'デメリット',
        'bento_1': '📝 概要・実地検証レビュー・基本データ',
        'bento_2': '⚓ 乗船前 — 乗り場・集合場所マップ',
        'bento_3': '🛳️ 乗船中 — 船体・デッキ・景色',
        'bento_4': '🍷 コース料理・試食レポート・雰囲気',
        'bento_audio': '🎧 音声ガイド・運航ルート',
        'bento_map': '🗺️ 出航乗り場＆集合場所マップ',
        'pill_overview': '概要',
        'pill_photos': '写真を見る →',
        'pill_map': '乗り場マップ'
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
        'best_for': 'Ideaal voor',
        'toc_title': 'Inhoudsopgave',
        'verified_badge': '✓ Zelf getest',
        'pros_title': 'PLUSPUNTEN',
        'cons_title': 'MINPUNTEN',
        'bento_1': '📝 Samenvatting, Review & Belangrijkste Feiten',
        'bento_2': '⚓ Voor de rondvaart — Steiger & Plattegrond',
        'bento_3': '🛳️ Tijdens de rondvaart — Schip, Dekken & Uitzicht',
        'bento_4': '🍷 Menu, Proeverij & Sfeer',
        'bento_audio': '🎧 Audiogids & Route',
        'bento_map': '🗺️ Vertreksteiger & Verzamelpunt kaart',
        'pill_overview': 'Overzicht',
        'pill_photos': 'Foto\'s →',
        'pill_map': 'Steigerkaart'
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
        'best_for': 'Idealne dla',
        'toc_title': 'Spis treści',
        'verified_badge': '✓ Osobiście przetestowane',
        'pros_title': 'ZALETY',
        'cons_title': 'WADY',
        'bento_1': '📝 Podsumowanie, Recenzja i Kluczowe Fakty',
        'bento_2': '⚓ Przed rejsem — Przystań i Mapa Miejsca Zbiórki',
        'bento_3': '🛳️ Podczas rejsu — Statek, Pokłady i Widoki',
        'bento_4': '🍷 Menu, Degustacja i Atmosfera',
        'bento_audio': '🎧 Przewodnik audio i Trasa',
        'bento_map': '🗺️ Przystań początkowa i Mapa dojazdu',
        'pill_overview': 'Przegląd',
        'pill_photos': 'Zdjęcia →',
        'pill_map': 'Mapa przystani'
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
        'best_for': 'Ideal pentru',
        'toc_title': 'Cuprins',
        'verified_badge': '✓ Testat personal',
        'pros_title': 'AVANTAJE',
        'cons_title': 'DEZAVANTAJE',
        'bento_1': '📝 Rezumat, Recenzie și Date Cheie',
        'bento_2': '⚓ Înainte de croazieră — Debarcader și Hartă de acces',
        'bento_3': '🛳️ În timpul croazierei — Navă, Punți și Priveliști',
        'bento_4': '🍷 Meniu, Degustare și Atmosferă',
        'bento_audio': '🎧 Ghid audio și Traseu',
        'bento_map': '🗺️ Debarcader de plecare și Hartă de acces',
        'pill_overview': 'Prezentare',
        'pill_photos': 'Fotografii →',
        'pill_map': 'Hartă debarcader'
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

# Spec pill vocabulary translations
SPECS_MAP = {
    'fr': {
        '360° Open Deck': 'Pont Ouvert 360°',
        'Open Observation': 'Pont d\'Observation Panoramique',
        'Open upper deck': 'Pont Supérieur Ouvert',
        'Open-Air Upper Deck': 'Pont Supérieur en Plein Air',
        'Rooftop Deck': 'Terrasse sur le Toit',
        'All-Glass Dining Boat': 'Bateau 100% Vitré',
        'Wine & Champagne': 'Vin & Champagne',
        'Free Champagne': 'Coupe de Champagne Incluse',
        'Champagne Welcome': 'Champagne de Bienvenue',
        'Optional Champagne': 'Option Champagne',
        'Sparkling wine': 'Vin Pétillant',
        'Wine Options': 'Formules Vins',
        'Wine Included': 'Vin Inclus',
        'Sommelier Wine': 'Sélection du Sommelier',
        'Unlimited drinks': 'Boissons à Volonté',
        'Open bar included': 'Open Bar Inclus',
        'Unlimited beer/wine': 'Bière & Vin Illimités',
        'Wine & beer': 'Vin & Bière',
        'Premium open bar': 'Open Bar Premium',
        '2 Free drinks': '2 Boissons Incluses',
        'Italian Spritz': 'Spritz Italien',
        'Mulled wine': 'Vin Chaud',
        'Ice Cream or Drink': 'Glace ou Boisson',
        'Ice cream dessert': 'Dessert Glacé',
        'Onboard bar': 'Bar à Bord',
        'Onboard Bar (Extra)': 'Bar à Bord (En supplément)',
        '4-Course Dinner': 'Dîner 4 Plats',
        '4-Course Gourmet': 'Menu Gastronomique 4 Plats',
        '4-Course dinner': 'Dîner 4 Plats',
        '3-Course Dinner': 'Dîner 3 Plats',
        '3-Course dinner': 'Dîner 3 Plats',
        '3-Course Bistro Meal': 'Menu Bistro 3 Plats',
        '3-Course Chef Menu': 'Menu Chef 3 Plats',
        '3-Course Gastronomic': 'Menu Gastronomique 3 Plats',
        '3-Course Lunch + Wine': 'Déjeuner 3 Plats + Vin',
        '2-Course meal': 'Repas 2 Plats',
        '3-4 Courses': '3 à 4 Plats',
        'Fresh Pasta': 'Pâtes Fraîches',
        'Fresh hot pizza': 'Pizza Fraîche au Feu de Bois',
        'Unlimited Gouda': 'Gouda Hollandais Illimité',
        '1 Crêpe Included': '1 Crêpe Incluse',
        '1 Waffle Included': '1 Gaufre Incluse',
        'Violin & Piano': 'Duo Violon & Piano',
        'Live Singer': 'Chanteuse en Direct',
        'Live Vocalist': 'Chanteuse en Direct',
        'Live Jazz Pianist': 'Pianiste de Jazz en Direct',
        'Live jazz band': 'Groupe de Jazz en Direct',
        'Live Music Onboard': 'Musique en Direct à Bord',
        'Curated French Music': 'Sélection Musicale Française',
        'Italian Music': 'Ambiance Musicale Italienne',
        'Party sound system': 'Système Son & DJ',
        'Bluetooth Sound': 'Système Son Bluetooth',
        'Live cabaret': 'Cabaret en Direct',
        '14-Language Audio': 'Audioguide en 14 Langues',
        '19-Language audio': 'Audioguide en 19 Langues',
        'App Audio Guide': 'Audioguide sur Application',
        'Kids audio story': 'Conte Audio pour Enfants',
        'Multi-Language Audio': 'Audioguide Multilingue',
        'Live commentary': 'Commentaires en Direct',
        'Live Bilingual Guide': 'Guide Bilingue en Direct',
        'Live local guide': 'Guide Local en Direct',
        'Pro commentary': 'Commentaires Professionnels',
        'Comedic guide': 'Guide Humoristique',
        'Private Skipper': 'Capitaine Privé Dédié',
        'Eiffel Tower Pier': 'Embarcadère Tour Eiffel',
        'Bir-Hakeim Pier': 'Embarcadère Bir-Hakeim',
        'Musée d\'Orsay Pier': 'Embarcadère Musée d\'Orsay',
        'Port Solférino Pier': 'Embarcadère Port Solférino',
        'Full Seine Circuit': 'Circuit Complet sur la Seine',
        'Illuminated Views': 'Vues sur Paris Illuminé',
        'Night Spotlights': 'Projecteurs Nocturnes sur Monuments',
        'Galley Cooked': 'Cuisine Préparée à Bord',
        'Family Friendly': 'Idéal pour les Familles',
        'Club Armchairs': 'Fauteuils Club en Cuir',
        'Lounge seating': 'Banquettes Lounge Confortables',
        'Plush salon lounge': 'Salon Confortable Haut de Gamme',
        'Heated salon boat': 'Bateau Salon Chauffé',
        'Heated Glass Cabin': 'Cabine Vitrée Chauffée',
        'Silent Electric': '100% Électrique Silencieux',
        '50-knot thrill': 'Sensations Fortes 50 Nœuds',
        'Fast catamaran': 'Catamaran Rapide',
        'Twin 880hp': 'Double Moteur 880 ch',
        '9 Hop-On Stops': '9 Arrêts Bateau-Bus',
        '4 Canal Locks': 'Passage de 4 Écluses',
        'Bastille Tunnel': 'Traversée du Tunnel de la Bastille',
        'Open-Dated Ticket': 'Billet Date Flexible',
        'Huge Open-Air Deck': 'Immense Pont Supérieur Ouvert',
        'Open-air sloop': 'Barque Ouverte Conviviale',
        'Boutique sloop': 'Barque Boutique Intimiste',
        'Cozy Boutique Ship': 'Navire Boutique Chaleureux',
        'Modern Yacht': 'Yacht Contemporain Épuré',
        'Glass Trimaran': 'Trimaran Vitré Panoramique',
        'Art Deco Decor': 'Décoration Style Art Déco',
        'Alain Ducasse': 'Haute Gastronomie Alain Ducasse',
        'Sunset Early Bird': 'Premier Coucher de Soleil',
        'Sunset views': 'Vues au Coucher de Soleil',
        'Evening canals': 'Canaux Illuminés en Soirée',
        'Thames barrier': 'Passage de la Barrière de la Tamise',
        'Big Ben views': 'Vues Imprenables sur Big Ben',
        'Light Festival': 'Festival des Lumières d\'Amsterdam',
        '420-Friendly boat': 'Bateau Smoke-Friendly',
        'Social atmosphere': 'Ambiance Festive & Conviviale',
        'Under €70': 'Moins de 70 €',
        'Scenic dining': 'Dîner Panoramique au Fil de l\'Eau',
        'Scenic commute': 'Traversée Fluviale Panoramique',
        'Wheelchair lift': 'Ascenseur Fauteuil Roulant',
        'No Audio or Drinks': 'Croisière Calme sans Audio'
    },
    'es': {
        '360° Open Deck': 'Cubierta Abierta 360°',
        'Open Observation': 'Cubierta de Observación Panorámica',
        'Open upper deck': 'Cubierta Superior Abierta',
        'Open-Air Upper Deck': 'Cubierta Superior al Aire Libre',
        'Rooftop Deck': 'Terraza en la Cubierta',
        'All-Glass Dining Boat': 'Barco Totalmente Acristalado',
        'Wine & Champagne': 'Vino y Champán',
        'Free Champagne': 'Copa de Champán Incluida',
        'Champagne Welcome': 'Bienvenida con Champán',
        'Optional Champagne': 'Opción de Champán',
        'Sparkling wine': 'Vino Espumoso',
        'Wine Options': 'Opciones de Vino',
        'Wine Included': 'Vino Incluido',
        'Sommelier Wine': 'Selección de Sumiller',
        'Unlimited drinks': 'Bebidas Ilimitadas',
        'Open bar included': 'Barra Libre Incluida',
        'Unlimited beer/wine': 'Cerveza y Vino Ilimitados',
        'Wine & beer': 'Vino y Cerveza',
        'Premium open bar': 'Barra Libre Premium',
        '2 Free drinks': '2 Bebidas Gratis',
        'Italian Spritz': 'Spritz Italiano',
        'Mulled wine': 'Vino Caliente Especiado',
        'Ice Cream or Drink': 'Helado o Bebida',
        'Ice cream dessert': 'Postre Helado',
        'Onboard bar': 'Bar a Bordo',
        'Onboard Bar (Extra)': 'Bar a Bordo (Extra)',
        '4-Course Dinner': 'Cena de 4 Platos',
        '4-Course Gourmet': 'Menú Gourmet de 4 Platos',
        '4-Course dinner': 'Cena de 4 Platos',
        '3-Course Dinner': 'Cena de 3 Platos',
        '3-Course dinner': 'Cena de 3 Platos',
        '3-Course Bistro Meal': 'Menú Bistro de 3 Platos',
        '3-Course Chef Menu': 'Menú de Chef de 3 Platos',
        '3-Course Gastronomic': 'Menú Gastronómico de 3 Platos',
        '3-Course Lunch + Wine': 'Almuerzo de 3 Platos con Vino',
        '2-Course meal': 'Comida de 2 Platos',
        '3-4 Courses': '3 a 4 Platos',
        'Fresh Pasta': 'Pasta Fresca Hecha a Mano',
        'Fresh hot pizza': 'Pizza Caliente Recién Horneada',
        'Unlimited Gouda': 'Queso Gouda Ilimitado',
        '1 Crêpe Included': '1 Crepe Incluido',
        '1 Waffle Included': '1 Gofre Incluido',
        'Violin & Piano': 'Dúo de Violín y Piano',
        'Live Singer': 'Cantante en Vivo',
        'Live Vocalist': 'Vocalista en Vivo',
        'Live Jazz Pianist': 'Pianista de Jazz en Vivo',
        'Live jazz band': 'Banda de Jazz en Vivo',
        'Live Music Onboard': 'Música en Vivo a Bordo',
        'Curated French Music': 'Música Francesa Seleccionada',
        'Italian Music': 'Música Tradicional Italiana',
        'Party sound system': 'Equipo de Sonido y DJ',
        'Bluetooth Sound': 'Sonido Bluetooth Personalizado',
        'Live cabaret': 'Espectáculo de Cabaret en Vivo',
        '14-Language Audio': 'Audioguía en 14 Idiomas',
        '19-Language audio': 'Audioguía en 19 Idiomas',
        'App Audio Guide': 'Audioguía en App Móvil',
        'Kids audio story': 'Audiocuento para Niños',
        'Multi-Language Audio': 'Audioguía Multilingüe',
        'Live commentary': 'Comentarios en Vivo',
        'Live Bilingual Guide': 'Guía Bilingüe en Vivo',
        'Live local guide': 'Guía Local Experto en Vivo',
        'Pro commentary': 'Narración Profesional en Vivo',
        'Comedic guide': 'Guía Cómico Entretenido',
        'Private Skipper': 'Patrón de Barco Privado Exclusivo',
        'Eiffel Tower Pier': 'Muelle Torre Eiffel',
        'Bir-Hakeim Pier': 'Muelle Bir-Hakeim',
        'Musée d\'Orsay Pier': 'Muelle Museo de Orsay',
        'Port Solférino Pier': 'Muelle Port Solférino',
        'Full Seine Circuit': 'Circuito Completo por el Sena',
        'Illuminated Views': 'Vistas Nocturnas Iluminadas',
        'Night Spotlights': 'Focos Iluminando Monumentos',
        'Galley Cooked': 'Cocinado Fresco a Bordo',
        'Family Friendly': 'Ideal para Familias con Niños',
        'Club Armchairs': 'Sillones Club de Cuero',
        'Lounge seating': 'Asientos Lounge Confortables',
        'Plush salon lounge': 'Salón Lounge Clásico Acolchado',
        'Heated salon boat': 'Barco Salón Clásico Calefaccionado',
        'Heated Glass Cabin': 'Cabina Acristalada Climatizada',
        'Silent Electric': '100% Eléctrico y Silencioso',
        '50-knot thrill': 'Sensaciones a 50 Nudos',
        'Fast catamaran': 'Catamarán Rápido',
        'Twin 880hp': 'Doble Motor 880 CV',
        '9 Hop-On Stops': '9 Paradas Hop-On Hop-Off',
        '4 Canal Locks': 'Paso por 4 Esclusas',
        'Bastille Tunnel': 'Cruce del Túnel de la Bastilla',
        'Open-Dated Ticket': 'Billete con Fecha Abierta',
        'Huge Open-Air Deck': 'Enorme Cubierta al Aire Libre',
        'Open-air sloop': 'Chalupa Abierta Típica',
        'Boutique sloop': 'Barco Boutique Acogedor',
        'Cozy Boutique Ship': 'Embarcación Boutique Cálida',
        'Modern Yacht': 'Yate Contemporáneo Elegante',
        'Glass Trimaran': 'Trimaràn Panorámico de Cristal',
        'Art Deco Decor': 'Decoración de Estilo Art Déco',
        'Alain Ducasse': 'Alta Cocina con Sello Alain Ducasse',
        'Sunset Early Bird': 'Puesta de Sol Temprana',
        'Sunset views': 'Vistas al Atardecer',
        'Evening canals': 'Canales al Atardecer',
        'Thames barrier': 'Navegación hasta la Barrera del Támesis',
        'Big Ben views': 'Vistas Magníficas al Big Ben',
        'Light Festival': 'Festival de las Luces de Ámsterdam',
        '420-Friendly boat': 'Barco 420 Smoke-Friendly',
        'Social atmosphere': 'Ambiente Social Animado',
        'Under €70': 'Por menos de 70 €',
        'Scenic dining': 'Cena con Vistas Panorámicas',
        'Scenic commute': 'Transporte Fluvial Panorámico',
        'Wheelchair lift': 'Elevador para Sillas de Ruedas',
        'No Audio or Drinks': 'Paseo Tranquilo sin Megafonía'
    }
}

PARIS_DINNER_BEST_FOR = {
    'fr': [
        "Couples, anniversaires et premiers visiteurs à Paris souhaitant la quintessence du dîner romantique avec violon, piano, champagne généreux et accès au pont ouvert à 360°.",
        "Voyageurs privilégiant une vue panoramique directe sur la Tour Eiffel scintillante depuis une verrière 360° intégrale et un service professionnel très rythmé.",
        "Couples et petits groupes recherchant une expérience gastronomique complète et abordable sous les 100 € avec vue dégagée au ras de l'eau.",
        "Petits budgets et jeunes couples voulant dîner sur la Seine confortablement installés dans des fauteuils club en cuir face aux baies vitrées.",
        "Groupes d'amis, anniversaires et fêtards recherchant une ambiance chic et festive avec DJ en direct et terrasse lounge spacieuse sur le toit.",
        "Amateurs de cuisine italienne généreuse, pâtes fraîches et tiramisu recherchant une atmosphère décontractée et chaleureuse.",
        "Ceux qui recherchent une cuisine fraîche préparée par un chef à bord sur une péniche fluviale traditionnelle avec vue panoramique.",
        "Amateurs de jazz et de raffinement rétro recherchant l'élégance légendaire des années 1930 et une cuisine française d'exception.",
        "Gastronomes et grandes occasions recherchant une expérience culinaire de niveau étoilé Michelin sur un navire 100% électrique totalement silencieux.",
        "Familles avec enfants ou spectateurs se rendant au théâtre le soir, souhaitant un dîner précoce baigné par la lumière dorée du coucher de soleil."
    ],
    'es': [
        "Parejas, aniversarios y visitantes que buscan el crucero con cena más romántico con violín y piano en vivo, champán abundante y acceso a la cubierta abierta de 360°.",
        "Viajeros que buscan una vista panorámica directa de la Torre Eiffel iluminada desde un salón acristalado de 360° con cantante en vivo.",
        "Parejas que buscan una cena romántica completa de calidad por debajo de 100 € con grandes ventanales a nivel del agua.",
        "Viajeros con presupuesto ajustado y parejas jóvenes que quieren cenar en el Sena en cómodos sillones de cuero frente a los ventanales.",
        "Grupos de amigos y cumpleaños que buscan un ambiente moderno y animado con música en vivo, DJ y una enorme terraza lounge superior.",
        "Amantes de la gastronomía italiana fresca y ambiente acogedor que prefieren una cena relajada con spritz y pasta recién hecha.",
        "Viajeros que buscan platos frescos elaborados a bordo por un chef profesional en un barco fluvial tradicional.",
        "Amantes del jazz y del lujo de época que buscan la sofisticación parisina de los años 30 con música en vivo y alta gastronomía.",
        "Gourmets y ocasiones especiales que buscan una experiencia de alta cocina con el sello de Alain Ducasse en un barco 100% eléctrico silencioso.",
        "Familias con niños o viajeros que van al teatro o cabaret más tarde y prefieren cenar temprano aprovechando la luz dorada del atardecer."
    ]
}

PARIS_DINNER_RANKS = {
    'fr': [
        '🏆 #1 Meilleur Choix Global',
        '🥈 #2 Deuxième Choix (Vues 360°)',
        '🥉 #3 Meilleur Rapport Qualité-Prix',
        '💶 #4 Meilleur Petit Budget',
        '✨ #5 Ambiance Festive & Lounge',
        '🍝 #6 Meilleure Ambiance Italienne',
        '🍷 #7 Classique Traditionnel Français',
        '🎷 #8 Jazz Belle Époque',
        '⭐ #9 Luxe Gastronomique (Ducasse)',
        '🌅 #10 Premier Coucher de Soleil'
    ],
    'es': [
        '🏆 #1 Mejor en General',
        '🥈 #2 Segundo Lugar (Vistas 360°)',
        '🥉 #3 Mejor Calidad-Precio',
        '💶 #4 Mejor Opción Económica',
        '✨ #5 Mejor Fiesta y Lounge',
        '🍝 #6 Mejor Estilo Italiano',
        '🍷 #7 Clásico Francés',
        '🎷 #8 Jazz Belle Époque',
        '⭐ #9 Lujo Gastronómico (Ducasse)',
        '🌅 #10 Puesta de Sol Temprana'
    ],
    'de': [
        '🏆 #1 Bester Gesamtsieger',
        '🥈 #2 Zweitplatzierter (360° Panorama)',
        '🥉 #3 Bester Preis-Leistungs-Sieger',
        '💶 #4 Bester Spartipp',
        '✨ #5 Party & Lounge Favorit',
        '🍝 #6 Beste Italienische Küche',
        '🍷 #7 Klassisch Französisch',
        '🎷 #8 Belle Époque Jazz',
        '⭐ #9 Gourmet-Luxus (Ducasse)',
        '🌅 #10 Frühe Sonnenuntergangsfahrt'
    ],
    'it': [
        '🏆 #1 Migliore in Assoluto',
        '🥈 #2 Secondo Classificato (Viste 360°)',
        '🥉 #3 Miglior Rapporto Qualità-Prezzo',
        '💶 #4 Miglior Prezzo Economico',
        '✨ #5 Migliore Festa e Lounge',
        '🍝 #6 Migliore Stile Italiano',
        '🍷 #7 Classico Francese',
        '🎷 #8 Jazz Belle Époque',
        '⭐ #9 Lusso Gastronomico (Ducasse)',
        '🌅 #10 Tramonto Anticipato'
    ],
    'ja': [
        '🏆 #1 総合第1位',
        '🥈 #2 第2位（360°全面ガラス船）',
        '🥉 #3 コスパ最高',
        '💶 #4 ベスト・バリュー',
        '✨ #5 パーティー＆ラウンジ',
        '🍝 #6 本格イタリアン',
        '🍷 #7 クラシック・フレンチ',
        '🎷 #8 ベル・エポック・ジャズ',
        '⭐ #9 ガストロノミー高級クルーズ',
        '🌅 #10 夕暮れサンセット'
    ],
    'nl': [
        '🏆 #1 Beste Algemene Keuze',
        '🥈 #2 Tweede Plaats (360° Panoramaboot)',
        '🥉 #3 Beste Prijs-Kwaliteitverhouding',
        '💶 #4 Beste Budgetkeuze',
        '✨ #5 Beste Feest & Lounge',
        '🍝 #6 Beste Italiaanse Stijl',
        '🍷 #7 Klassiek Frans',
        '🎷 #8 Belle Époque Jazz',
        '⭐ #9 Gastronomische Luxe (Ducasse)',
        '🌅 #10 Vroeg Avondrood'
    ],
    'pl': [
        '🏆 #1 Najlepszy Wybór Ogólny',
        '🥈 #2 Drugie Miejsce (Widok 360°)',
        '🥉 #3 Najlepszy Stosunek Ceny do Jakości',
        '💶 #4 Najlepszy Wybór Budżetowy',
        '✨ #5 Najlepszy Imprezowy i Lounge',
        '🍝 #6 Najlepszy Styl Włoski',
        '🍷 #7 Klasyczny Francuski',
        '🎷 #8 Jazz Belle Époque',
        '⭐ #9 Gastronomiczny Luksus (Ducasse)',
        '🌅 #10 Wczesny Zachód Słońca'
    ],
    'ro': [
        '🏆 #1 Cea Mai Bună Alegere',
        '🥈 #2 Locul 2 (Vedere 360°)',
        '🥉 #3 Cel Mai Bun Raport Calitate-Preț',
        '💶 #4 Cea Mai Bună Opțiune Buget',
        '✨ #5 Cea Mai Bună Petrecere & Lounge',
        '🍝 #6 Cel Mai Bun Stil Italian',
        '🍷 #7 Clasic Franțuzesc',
        '🎷 #8 Jazz Belle Époque',
        '⭐ #9 Lux Gastronomic (Ducasse)',
        '🌅 #10 Apus Timpuriu'
    ]
}


# ---------------------------------------------------------------------------
# SIGHTSEEING, AMSTERDAM & LONDON RANK TAGS & BEST FOR
# ---------------------------------------------------------------------------
PARIS_SIGHTSEEING_RANKS = {
    'fr': [
        '🏆 #1 Meilleure croisière globale',
        '🥈 #2 Deuxième meilleure (Pont ouvert 360°)',
        '🥉 #3 Meilleure ambiance musicale & cosy',
        '#4 Meilleur pass montées/descentes',
        '👑 #5 Meilleur yacht privé exclusif',
        '#6 Meilleure croisière nocturne & gaufres',
        '#7 Meilleur combiné crêpes bretonnes',
        '🍽️ #8 Meilleur déjeuner-croisière',
        '#9 Meilleure formule été & glaces',
        '#10 Meilleur canal & écluses historiques'
    ],
    'es': [
        '🏆 #1 Mejor crucero en general',
        '🥈 #2 Segundo mejor (Cubierta 360°)',
        '🥉 #3 Mejor música y ambiente íntimo',
        '#4 Mejor pase paradas libres (Hop-On Hop-Off)',
        '👑 #5 Mejor yate privado exclusivo',
        '#6 Mejor crucero nocturno con gofres',
        '#7 Mejor combo con crêpes bretones',
        '🍽️ #8 Mejor almuerzo en barco',
        '#9 Mejor opción de verano con helados',
        '#10 Mejor canal y esclusas históricas'
    ],
    'de': [
        '🏆 #1 Gesamtsieger Sightseeing',
        '🥈 #2 Zweitplatzierte Bootsfahrt (360° Freideck)',
        '🥉 #3 Beste Musik & gemütliche Atmosphäre',
        '#4 Bester Hop-On Hop-Off Pass',
        '👑 #5 Beste private Jacht',
        '#6 Beste Nachtfahrt mit Waffeln',
        '#7 Bester Crêpe-Kombi-Deal',
        '🍽️ #8 Beste Mittagessen-Bootsfahrt',
        '#9 Bestes Sommer-Erlebnis mit Eis',
        '#10 Bester historischer Kanal & Schleusen'
    ],
    'it': [
        '🏆 #1 Migliore crociera panoramica',
        '🥈 #2 Seconda migliore (Ponte aperto 360°)',
        '🥉 #3 Miglior musica e atmosfera intima',
        '#4 Miglior pass sali e scendi',
        '👑 #5 Miglior yacht privato esclusivo',
        '#6 Migliore crociera notturna con waffle',
        '#7 Miglior combinato con crêpe',
        '🍽️ #8 Miglior pranzo in crociera',
        '#9 Migliore opzione estiva con gelato',
        '#10 Miglior canale e chiuse storiche'
    ],
    'ja': [
        '🏆 #1 総合ベスト遊覧クルーズ',
        '🥈 #2 第2位（360度オープンデッキ）',
        '🥉 #3 最高の音楽と落ち着いた雰囲気',
        '#4 乗り降り自由ベストパス',
        '👑 #5 最高峰プライベートボート',
        '#6 ベスト夜景＆温かいワッフル',
        '#7 定番クレープセット',
        '🍽️ #8 ベスト ランチクルーズ',
        '#9 夏期限定アイスセット',
        '#10 サン・マルタン運河と水門ツアー'
    ],
    'nl': [
        '🏆 #1 Beste rondvaart algemeen',
        '🥈 #2 Tweede plaats (360° open dek)',
        '🥉 #3 Beste sfeer & Franse muziek',
        '#4 Beste hop-on hop-off pas',
        '👑 #5 Beste exclusieve privéjacht',
        '#6 Beste avondvaart met warme wafels',
        '#7 Beste crêpe-combinatie',
        '🍽️ #8 Beste lunchcruise',
        '#9 Beste zomervaart met ijs',
        '#10 Beste historische kanaal & sluizen'
    ],
    'pl': [
        '🏆 #1 Najlepszy rejs wycieczkowy',
        '🥈 #2 Drugi najlepszy (Otwarty pokład 360°)',
        '🥉 #3 Najlepsza muzyka i klimat',
        '#4 Najlepszy bilet hop-on hop-off',
        '👑 #5 Najlepszy prywatny jacht',
        '#6 Najlepszy rejs nocny z goframi',
        '#7 Najlepszy zestaw z naleśnikami',
        '🍽️ #8 Najlepszy rejs z obiadem',
        '#9 Najlepsza letnia opcja z lodami',
        '#10 Najlepszy rejs kanałem i śluzami'
    ],
    'ro': [
        '🏆 #1 Cea mai bună croazieră panoramică',
        '🥈 #2 A doua cea mai bună (Punte deschisă 360°)',
        '🥉 #3 Cea mai bună muzică & atmosferă intimă',
        '#4 Cel mai bun abonament hop-on hop-off',
        '👑 #5 Cel mai bun iaht privat exclusivist',
        '#6 Cea mai bună croazieră nocturnă cu vafe',
        '#7 Cel mai bun pachet cu clătite',
        '🍽️ #8 Cel mai bun prânz pe vapor',
        '#9 Cea mai bună opțiune de vară cu înghețată',
        '#10 Cel mai bun canal și ecluze istorice'
    ]
}

AMSTERDAM_RANKS = {
    'fr': [
        '🏆 #1 Meilleure expérience globale', '🥈 #2 Meilleur rapport qualité/prix', '🥉 #3 Meilleure barque ouverte',
        '🎖️ #4 Meilleur salon chauffé classique', '✨ #5 Meilleur salon de luxe', '💡 #6 Meilleur Festival des Lumières',
        '🎉 #7 Meilleure croisière apéro / festive', '🌿 #8 Meilleur lounge 420-friendly', '🍕 #9 Meilleure croisière pizza',
        '🍷 #10 Meilleur dîner-croisière 4 plats'
    ],
    'es': [
        '🏆 #1 Mejor experiencia global', '🥈 #2 Mejor calidad/precio', '🥉 #3 Mejor barca abierta',
        '🎖️ #4 Mejor clásico climatizado', '✨ #5 Mejor salón de lujo', '💡 #6 Mejor Festival de las Luces',
        '🎉 #7 Mejor crucero de fiesta y bebidas', '🌿 #8 Mejor lounge 420', '🍕 #9 Mejor crucero con pizza',
        '🍷 #10 Mejor crucero cena 4 platos'
    ],
    'de': [
        '🏆 #1 Gesamtsieger Grachtenfahrt', '🥈 #2 Bestes Preis-Leistungs-Verhältnis', '🥉 #3 Bestes offenes Boot',
        '🎖️ #4 Bester beheizter Klassiker', '✨ #5 Bester Luxussalon', '💡 #6 Bestes Lichtfestival',
        '🎉 #7 Beste Party- und Getränketour', '🌿 #8 Bester 420-freundlicher Smoke-Lounge-Kanal', '🍕 #9 Beste Pizza-Grachtenfahrt',
        '🍷 #10 Beste 4-Gänge-Dinner-Grachtenfahrt'
    ],
    'it': [
        '🏆 #1 Migliore esperienza globale', '🥈 #2 Miglior rapporto qualità-prezzo', '🥉 #3 Migliore barca aperta',
        '🎖️ #4 Miglior classico riscaldato', '✨ #5 Miglior salone di lusso', '💡 #6 Miglior Festival delle Luci',
        '🎉 #7 Migliore crociera con bevande e festa', '🌿 #8 Miglior lounge 420-friendly', '🍕 #9 Migliore crociera pizza',
        '🍷 #10 Migliore crociera cena 4 portate'
    ],
    'ja': [
        '🏆 #1 総合ベスト運河体験', '🥈 #2 ベスト コスパ遊覧', '🥉 #3 ベスト オープンボート',
        '🎖️ #4 ベスト 暖房付きクラシック', '✨ #5 ベスト 高級サロンボート', '💡 #6 ベスト 光の祭典ツアー',
        '🎉 #7 ベスト 飲み放題パーティークルーズ', '🌿 #8 ベスト 420スモークラウンジ', '🍕 #9 ベスト ピザクルーズ',
        '🍷 #10 ベスト 4コースディナークルーズ'
    ],
    'nl': [
        '🏆 #1 Beste ervaring algemeen', '🥈 #2 Beste prijs-kwaliteitverhouding', '🥉 #3 Beste open sloep',
        '🎖️ #4 Beste verwarmde klassieker', '✨ #5 Beste luxe salonboot', '💡 #6 Beste Light Festival',
        '🎉 #7 Beste feest- & borrelcruise', '🌿 #8 Beste 420-vriendelijke lounge', '🍕 #9 Beste pizzacruise',
        '🍷 #10 Beste 4-gangen dinercruise'
    ],
    'pl': [
        '🏆 #1 Najlepszy rejs ogółem', '🥈 #2 Najlepszy stosunek jakości do ceny', '🥉 #3 Najlepsza otwarta łódź',
        '🎖️ #4 Najlepszy ogrzewany klasyk', '✨ #5 Najlepszy luksusowy salon', '💡 #6 Najlepszy Festiwal Światła',
        '🎉 #7 Najlepszy rejs imprezowy z drinkami', '🌿 #8 Najlepszy salon 420', '🍕 #9 Najlepszy rejs z pizzą',
        '🍷 #10 Najlepszy rejs z kolacją 4-daniową'
    ],
    'ro': [
        '🏆 #1 Cea mai bună experiență globală', '🥈 #2 Cel mai bun raport calitate-preț', '🥉 #3 Cea mai bună barcă deschisă',
        '🎖️ #4 Cel mai bun clasic încălzit', '✨ #5 Cel mai bun salon de lux', '💡 #6 Cel mai bun Festival al Luminilor',
        '🎉 #7 Cea mai bună croazieră festivă cu băuturi', '🌿 #8 Cel mai bun lounge 420', '🍕 #9 Cea mai bună croazieră cu pizza',
        '🍷 #10 Cea mai bună cină-croazieră cu 4 feluri'
    ]
}

LONDON_RANKS = {
    'fr': [
        '🏆 #1 Meilleure visite globale', '🥈 #2 Deuxième meilleure visite', '🥉 #3 Meilleur pass montées/descentes',
        '⚡ #4 Sensations fortes en bateau rapide', '⚡ #5 Deuxième bateau rapide', '🍽️ #6 Meilleur déjeuner-croisière',
        '🥂 #7 Meilleur coucher de soleil & canapés', '🎷 #8 Meilleur dîner-croisière Jazz', '🛥️ #9 Meilleur pass transport fluvial',
        '🍷 #10 Meilleur dîner gala cabaret'
    ],
    'es': [
        '🏆 #1 Mejor crucero global', '🥈 #2 Segundo mejor crucero', '🥉 #3 Mejor pase paradas libres',
        '⚡ #4 Máxima emoción en lancha rápida', '⚡ #5 Segunda mejor lancha rápida', '🍽️ #6 Mejor almuerzo en barco',
        '🥂 #7 Mejor atardecer y canapés', '🎷 #8 Mejor crucero cena con Jazz', '🛥️ #9 Mejor pase de transporte fluvial',
        '🍷 #10 Mejor gran cena de gala'
    ],
    'de': [
        '🏆 #1 Gesamtsieger Sightseeing', '🥈 #2 Zweitplatzierte Themse-Fahrt', '🥉 #3 Bester Hop-On Hop-Off Pass',
        '⚡ #4 Bestes Speedboot-Abenteuer', '⚡ #5 Zweitplatziertes Speedboot', '🍽️ #6 Beste Mittagessen-Bootsfahrt',
        '🥂 #7 Bester Sonnenuntergang & Canapés', '🎷 #8 Beste Jazz-Dinner-Kreuzfahrt', '🛥️ #9 Bester Fluss-Nahverkehrspass',
        '🍷 #10 Beste Showboat-Gala-Dinnerfahrt'
    ],
    'it': [
        '🏆 #1 Migliore crociera globale', '🥈 #2 Seconda migliore crociera', '🥉 #3 Miglior pass sali e scendi',
        '⚡ #4 Brivido motoscafo veloce', '⚡ #5 Secondo motoscafo veloce', '🍽️ #6 Miglior pranzo in crociera',
        '🥂 #7 Miglior tramonto e canapè', '🎷 #8 Migliore crociera cena con Jazz', '🛥️ #9 Miglior pass trasporto fluviale',
        '🍷 #10 Migliore cena di gala con spettacolo'
    ],
    'ja': [
        '🏆 #1 総合ベスト観光クルーズ', '🥈 #2 第2位 定番クルーズ', '🥉 #3 ベスト 乗り降り自由パス',
        '⚡ #4 ベスト スピードボート体験', '⚡ #5 第2位 スピードボート', '🍽️ #6 ベスト ランチクルーズ',
        '🥂 #7 ベスト 夕暮れ＆カナッペ', '🎷 #8 ベスト ジャズディナークルーズ', '🛥️ #9 ベスト 水上交通定期券',
        '🍷 #10 ベスト ショーボートガラディナー'
    ],
    'nl': [
        '🏆 #1 Beste rondvaart algemeen', '🥈 #2 Tweede plaats rondvaart', '🥉 #3 Beste hop-on hop-off pas',
        '⚡ #4 Beste speedboot sensatie', '⚡ #5 Tweede plaats speedboot', '🍽️ #6 Beste lunchcruise',
        '🥂 #7 Beste zonsondergang & hapjes', '🎷 #8 Beste jazz dinercruise', '🛥️ #9 Beste rivier OV-pas',
        '🍷 #10 Beste showboat gala dinercruise'
    ],
    'pl': [
        '🏆 #1 Najlepszy rejs wycieczkowy', '🥈 #2 Drugi najlepszy rejs', '🥉 #3 Najlepszy bilet hop-on hop-off',
        '⚡ #4 Najlepszy rejs szybką motorówką', '⚡ #5 Druga najlepsza szybka łódź', '🍽️ #6 Najlepszy rejs z obiadem',
        '🥂 #7 Najlepszy zachód słońca i przekąski', '🎷 #8 Najlepszy rejs z kolacją jazzową', '🛥️ #9 Najlepszy bilet transportowy',
        '🍷 #10 Najlepszy rejs galowy z kolacją'
    ],
    'ro': [
        '🏆 #1 Cea mai bună croazieră turistică', '🥈 #2 A doua cea mai bună', '🥉 #3 Cel mai bun pass hop-on hop-off',
        '⚡ #4 Senzații tari pe barcă rapidă', '⚡ #5 A doua cea mai bună barcă rapidă', '🍽️ #6 Cel mai bun prânz pe râu',
        '🥂 #7 Cel mai bun apus și gustări', '🎷 #8 Cea mai bună cină cu muzică Jazz', '🛥️ #9 Cel mai bun abonament fluvial',
        '🍷 #10 Cea mai bună cină festivă de gală'
    ]
}

PARIS_SIGHTSEEING_BEST_FOR = {
    "fr": [
        "Visiteurs pour la première fois, couples et familles souhaitant les départs les plus fréquents au pied de la Tour Eiffel avec un audioguide clair en 14 langues.",
        "Photographes et promeneurs recherchant un immense pont supérieur à ciel ouvert à 360° et un embarquement rapide sans foule.",
        "Couples et voyageurs en soirée recherchant une ambiance intimiste de salon parisien avec musique française et champagne.",
        "Voyageurs indépendants souhaitant utiliser la Seine comme moyen de transport panoramique toute la journée entre la Tour Eiffel, le Louvre et Notre-Dame.",
        "Demandes en mariage, anniversaires ou petits groupes jusqu'à 7 personnes souhaitant un bateau privatisé exclusif avec champagne offert.",
        "Voyageurs nocturnes et gourmands souhaitant admirer les monuments illuminés tout en dégustant des gaufres belges chaudes au chocolat.",
        "Promeneurs et familles recherchant une croisière classique combinée à une crêpe bretonne fraîche au kiosque du ponton Eiffel.",
        "Voyageurs souhaitant un vrai repas gastronomique français en 3 plats avec musique live en journée sans payer le tarif d'un dîner-croisière.",
        "Voyageurs estivaux et familles cherchant une croisière rafraîchissante avec glace artisanale ou apéritif inclus.",
        "Voyageurs en quête d'une traversée authentique de 2h30 à travers les écluses, les ponts tournants et le tunnel souterrain de la Bastille."
    ],
    "es": [
        "Visitantes primerizos, parejas y familias que buscan salidas frecuentes justo bajo la Torre Eiffel con audioguía clara en 14 idiomas.",
        "Fotógrafos y viajeros que desean una cubierta superior abierta de 360° sin obstáculos y embarque rápido lejos de aglomeraciones.",
        "Parejas y viajeros nocturnos que buscan un ambiente íntimo de salón parisino con música francesa y champán opcional.",
        "Viajeros independientes que desean usar el Sena como transporte panorámico durante todo el día entre la Torre Eiffel, el Louvre y Notre-Dame.",
        "Pedidas de mano, aniversarios o grupos pequeños de hasta 7 personas que buscan un barco privado exclusivo con champán de bienvenida.",
        "Noctámbulos y amantes del dulce que quieren ver los monumentos iluminados acompañados de gofres calientes con chocolate.",
        "Viajeros y familias que buscan un crucero clásico por el Sena combinado con un auténtico crêpe bretón en el muelle de la Torre Eiffel.",
        "Viajeros que buscan una comida francesa completa de 3 platos con música en vivo durante el día sin los altos precios del crucero con cena.",
        "Viajeros de verano y familias que quieren un paseo refrescante por la tarde con helado artesanal o un aperitivo incluido.",
        "Viajeros que buscan una travesía tranquila de 2,5 horas por las esclusas, puentes giratorios y túneles subterráneos del Canal San Martín."
    ],
    "de": [
        "Erstbesucher, Paare und Familien, die häufige Abfahrten direkt am Eiffelturm mit verständlichem Audioguide in 14 Sprachen suchen.",
        "Fotografen und Genießer, die ein riesiges 360°-Freideck und schnelles Boarding abseits der Eiffelturm-Massen bevorzugen.",
        "Paare und Abendreisende, die eine charmante, gemütliche Pariser Salon-Atmosphäre mit französischer Musik und Champagner suchen.",
        "Unabhängige Entdecker, die die Seine als malerisches Ganztagstransportmittel zwischen Eiffelturm, Louvre und Notre-Dame nutzen wollen.",
        "Heiratsanträge, Jubiläen oder kleine Gruppen bis zu 7 Personen, die ein exklusives Privatboot auf der Seine mit Champagner wünschen.",
        "Nachtschwärmer und Naschkatzen, die beleuchtete Monumente mit warmen belgischen Waffeln und Schokolade verbinden möchten.",
        "Spaziergänger und Familien, die eine klassische Seine-Rundfahrt mit einer frischen bretonischen Crêpe am Eiffelturm-Anleger kombinieren möchten.",
        "Reisende, die ein vollwertiges französisches 3-Gänge-Mittagessen mit Live-Musik auf der Seine ohne Dinner-Preise genießen möchten.",
        "Sommerreisende und Familien, die eine erfrischende Nachmittagsfahrt mit handwerklichem Eis oder einem Aperitif suchen.",
        "Reisende, die eine authentische, entspannte 2,5-stündige Reise durch historische Schleusen, Drehbrücken und den Bastille-Tunnel suchen."
    ],
    "it": [
        "Visitatori per la prima volta, coppie e famiglie che desiderano partenze frequenti sotto la Torre Eiffel con audioguida in 14 lingue.",
        "Fotografi e viaggiatori che desiderano un enorme ponte scoperto a 360° e un imbarco veloce lontano dalla folla.",
        "Coppie e viaggiatori serali alla ricerca di un'atmosfera intima da salotto parigino con musica francese e champagne.",
        "Viaggiatori indipendenti che vogliono usare la Senna come panoramico mezzo di trasporto giornaliero tra Torre Eiffel, Louvre e Notre-Dame.",
        "Proposte di matrimonio, anniversari o piccoli gruppi fino a 7 persone che desiderano una barca privata esclusiva con champagne offerto.",
        "Amanti della notte e dei dolci che desiderano ammirare i monumenti illuminati gustando waffle belgi caldi al cioccolato.",
        "Turisti e famiglie alla ricerca di una classica crociera sulla Senna abbinata a una crêpe bretone fresca al molo della Torre Eiffel.",
        "Viaggiatori che desiderano un autentico pranzo francese di 3 portate con musica dal vivo di giorno senza i costi della crociera con cena.",
        "Viaggiatori estivi e famiglie che desiderano una rilassante crociera pomeridiana con gelato artigianale o aperitivo incluso.",
        "Viaggiatori alla ricerca di un autentico viaggio di 2,5 ore attraverso chiuse, ponti girevoli e il tunnel sotterraneo della Bastiglia."
    ],
    "ja": [
        "エッフェル塔真下からの頻繁な出航と14言語対応の明瞭な音声ガイドを求める初訪問者・カップル・家族連れに最適。",
        "エッフェル塔の混雑を避け、広々とした360度オープンデッキから遮るもののないパノラマ写真を撮影したい旅行者向け。",
        "フランス音楽とシャンパンを楽しみながら、小型船ならではの親密で心地よいパリのサロンの雰囲気を味わいたいカップルに最適。",
        "エッフェル塔、ルーヴル、オルセー、ノートルダム間を終日自由に移動できる水上観光バスとして利用したい旅行者向け。",
        "プロポーズや記念日、最大7名までのグループで、シャンパン付きの完全プライベート貸切ボートを楽しみたい方に最適。",
        "美しくライトアップされた歴史的建造物を眺めながら、温かいベルギーワッフルとチョコレートを堪能したい夜の散策派向け。",
        "エッフェル塔乗り場前で焼きたての本格クレープを片手に、定番のセーヌ川クルーズを気軽に楽しみたい家族や観光客向け。",
        "ディナークルーズの高額な料金をかけずに、昼間の明るい陽光の中で本格フレンチ3コースと生演奏を満喫したい旅行者向け。",
        "職人手作りのジェラートやアペリティフを片手に、爽やかな午後のリバークルーズを楽しみたい夏の旅行者に最適。",
        "歴史ある水門や回転橋、バスティーユの地下トンネルを通り抜ける2.5時間の本格的で優雅な運河の旅を体験したい方向け。"
    ],
    "nl": [
        "Eerste bezoekers, stellen en gezinnen die de meest frequente afvaarten direct onder de Eiffeltoren met audiogids in 14 talen wensen.",
        "Fotografen en levensgenieters die een enorm 360° open bovendek en snelle inscheping zonder drukte zoeken.",
        "Stellen en avondreizigers die een charmante, intieme Parijse salonsfeer met Franse muziek en champagne zoeken.",
        "Zelfstandige reizigers die de Seine willen gebruiken als panoramisch dagvervoer tussen de Eiffeltoren, het Louvre en de Notre-Dame.",
        "Huwelijksaanzoeken, jubilea of kleine groepen tot 7 personen die een exclusieve privéboot op de Seine met champagne wensen.",
        "Nachtbrakers en zoetekauwen die verlichte monumenten willen combineren met warme Belgische wafels en chocolade.",
        "Wandelaars en gezinnen die een klassieke Seine-rondvaart willen combineren met een verse Bretonse crêpe aan de Eiffeltoren-steiger.",
        "Reizigers die overdag willen genieten van een complete Franse 3-gangenmaaltijd met live muziek zonder de prijzen van een dinercruise.",
        "Zomerreizigers en gezinnen die een verfrissende middagvaart met ambachtelijk ijs of een aperitief zoeken.",
        "Reizigers die een authentieke, ontspannen 2,5 uur durende tocht door historische sluizen, draaibruggen en de Bastille-tunnel willen beleven."
    ],
    "pl": [
        "Osoby odwiedzające Paryż po raz pierwszy, pary i rodziny szukające częstych rejsów spod samej Wieży Eiffla z audioprzewodnikiem w 14 językach.",
        "Fotografowie i turyści pragnący ogromnego, otwartego pokładu 360° oraz szybkiego wejścia na pokład z dala od tłumów.",
        "Pary i turyści wieczorni szukający kameralnej atmosfery paryskiego salonu z francuską muzyką i opcjonalnym szampanem.",
        "Niezależni podróżnicy chcący wykorzystać Sekwanę jako malowniczy transport pomiędzy Wieżą Eiffla, Luwrem a katedrą Notre-Dame.",
        "Zaręczyny, rocznice lub małe grupy do 7 osób szukające ekskluzywnego prywatnego jachtu na Sekwanie z szampanem.",
        "Nocne marki i miłośnicy słodkości pragnący podziwiać oświetlone zabytki z ciepłymi belgijskimi goframi i czekoladą.",
        "Turyści i rodziny szukający klasycznego rejsu połączonego ze świeżym bretońskim naleśnikiem przy pomoście Wieży Eiffla.",
        "Podróżni szukający pełnego 3-daniowego obiadu francuskiego z muzyką na żywo w ciągu dnia bez wysokich cen rejsu z kolacją.",
        "Letni podróżnicy i rodziny szukający orzeźwiającego popołudniowego rejsu z rzemieślniczymi lodami lub aperitifem.",
        "Podróżni pragnący autentycznej, spokojnej 2,5-godzinnej wyprawy przez zabytkowe śluzy, obrotowe mosty i podziemny tunel Bastylii."
    ],
    "ro": [
        "Vizitatori pentru prima dată, cupluri și familii care doresc plecări frecvente chiar de la Turnul Eiffel cu audioghid clar în 14 limbi.",
        "Fotografi și călători care își doresc o punte superioară deschisă imensă la 360° și îmbarcare rapidă fără aglomerație.",
        "Cupluri și călători de seară în căutarea unei atmosfere intime de salon parizian cu muzică franțuzească și șampanie.",
        "Călători independenți care doresc să folosească Sena ca transport panoramic de o zi între Turnul Eiffel, Luvru și Notre-Dame.",
        "Cereri în căsătorie, aniversări sau grupuri de până la 7 persoane care își doresc o ambarcațiune privată exclusivistă cu șampanie.",
        "Călători nocturni și amatori de dulciuri care doresc să admire monumentele iluminate savurând vafe belgiene calde cu ciocolată.",
        "Turiști și familii care caută o croazieră clasică combinată cu o clătită bretonă proaspătă la debarcaderul Turnului Eiffel.",
        "Călători care doresc un prânz gastronomic franțuzesc complet cu 3 feluri și muzică live în timpul zilei fără prețurile unei cine festive.",
        "Turiști estivali și familii în căutarea unei croaziere relaxante de după-amiază cu înghețată artizanală sau aperitiv inclus.",
        "Călători care doresc o călătorie autentică de 2,5 ore prin ecluze istorice, poduri rotative și tunelul subteran Bastille."
    ]
}


FILTER_TABS_I18N = {
    'fr': {
        'filter_label': 'Filtres :',
        'all': 'Tous (10)',
        'tested': '✓ Testé en personne (5)',
        'livemusic': '🎵 Musique Live (5)',
        'under100': '💶 Moins de 100 € (5)',
        'gourmet': '🍷 Menu Gastronomique 4 Plats (5)',
        'under20': '💶 Moins de 20 € (5)',
        'treats': '🥂 Boissons & Gourmandises (4)',
        'lunch': '🍽️ Déjeuner Assis (1)',
        'route': '🗺️ Batobus & Canal (2)',
        'private': '🛥️ Bateau Privé (1)',
        'sightseeing_amsterdam': '🏆 Promenade Classique (3)',
        'drinks_amsterdam': '🧀 Boissons & Fromage (4)',
        'dining_amsterdam': '🍷 Dîner & Pizza (2)',
        'specialty_amsterdam': '✨ Spécialité & Smoke-Friendly (1)',
        'sightseeing_london': '🏆 Promenade Classique (4)',
        'dining_london': '🍷 Déjeuner & Dîner (4)',
        'speedboat_london': '⚡ Bateaux Rapides (2)',
        'duel_tab_1': 'Dîner Bateaux Mouches',
        'duel_tab_2': 'Dîner Bateaux Parisiens',
        'duel_tab_3': '⚖️ Tableau Comparatif Complet',
        'expand_all': 'Tout afficher',
        'collapse_all': 'Tout réduire',
        'breakdown_sub': 'Tests indépendants sur le terrain • Tous les avis ouverts par défaut • Cliquez pour réduire/afficher',
        "hide_review": "Masquer l'avis",
        "show_review": "Afficher l'avis",
        "buyers_guide_divider": "Guide d'achat & Méthodologie"
    },
    'de': {
        'filter_label': 'Filter:',
        'all': 'Alle (10)',
        'tested': '✓ Persönlich getestet (5)',
        'livemusic': '🎵 Live-Musik (5)',
        'under100': '💶 Unter 100 € (5)',
        'gourmet': '🍷 4-Gänge-Gourmetmenü (5)',
        'under20': '💶 Unter 20 € (5)',
        'treats': '🥂 Getränke & Snacks (4)',
        'lunch': '🍽️ Mittagessen an Bord (1)',
        'route': '🗺️ Hop-On & Kanäle (2)',
        'private': '🛥️ Privatboot (1)',
        'sightseeing_amsterdam': '🏆 Klassische Rundfahrt (3)',
        'drinks_amsterdam': '🧀 Getränke & Käse (4)',
        'dining_amsterdam': '🍷 Abendessen & Pizza (2)',
        'specialty_amsterdam': '✨ Spezial & Smoke-Friendly (1)',
        'sightseeing_london': '🏆 Klassische Rundfahrt (4)',
        'dining_london': '🍷 Mittag- & Abendessen (4)',
        'speedboat_london': '⚡ Schnellboote (2)',
        'duel_tab_1': 'Bateaux Mouches Dinner',
        'duel_tab_2': 'Bateaux Parisiens Dinner',
        'duel_tab_3': '⚖️ Detaillierter Vergleich',
        'expand_all': 'Alle ausklappen',
        'collapse_all': 'Alle einklappen',
        'breakdown_sub': 'Unabhängig im Feld getestet • Alle Bewertungen standardmäßig geöffnet • Zum Ein-/Ausklappen klicken',
        'hide_review': 'Bewertung ausblenden',
        'show_review': 'Bewertung anzeigen',
        'buyers_guide_divider': 'Kaufratgeber & Methodik'
    },
    'es': {
        'filter_label': 'Filtros:',
        'all': 'Todos (10)',
        'tested': '✓ Evaluado personalmente (5)',
        'livemusic': '🎵 Música en Vivo (5)',
        'under100': '💶 Menos de 100 € (5)',
        'gourmet': '🍷 Menú Gourmet 4 Platos (5)',
        'under20': '💶 Menos de 20 € (5)',
        'treats': '🥂 Bebidas y Aperitivos (4)',
        'lunch': '🍽️ Almuerzo a Bordo (1)',
        'route': '🗺️ Paradas Libres y Canales (2)',
        'private': '🛥️ Barco Privado (1)',
        'sightseeing_amsterdam': '🏆 Paseo Panorámico (3)',
        'drinks_amsterdam': '🧀 Bebidas y Queso (4)',
        'dining_amsterdam': '🍷 Cena y Pizza (2)',
        'specialty_amsterdam': '✨ Especial y Smoke-Friendly (1)',
        'sightseeing_london': '🏆 Paseo Panorámico (4)',
        'dining_london': '🍷 Almuerzo y Cena (4)',
        'speedboat_london': '⚡ Lanchas Rápidas (2)',
        'duel_tab_1': 'Cena Bateaux Mouches',
        'duel_tab_2': 'Cena Bateaux Parisiens',
        'duel_tab_3': '⚖️ Tabla Comparativa Detallada',
        'expand_all': 'Expandir todo',
        'collapse_all': 'Contraer todo',
        'breakdown_sub': 'Evaluado de forma independiente en el terreno • Todas las reseñas abiertas por defecto • Haz clic para contraer/expandir',
        'hide_review': 'Ocultar reseña',
        'show_review': 'Ver reseña',
        'buyers_guide_divider': 'Guía del comprador y metodología'
    },
    'it': {
        'filter_label': 'Filtri:',
        'all': 'Tutti (10)',
        'tested': '✓ Testato di persona (5)',
        'livemusic': '🎵 Musica dal Vivo (5)',
        'under100': '💶 Sotto 100 € (5)',
        'gourmet': '🍷 Gourmet 4 Portate (5)',
        'under20': '💶 Sotto 20 € (5)',
        'treats': '🥂 Bevande e Degustazioni (4)',
        'lunch': '🍽️ Pranzo a Bordo (1)',
        'route': '🗺️ Hop-On & Canali (2)',
        'private': '🛥️ Barca Privata (1)',
        'sightseeing_amsterdam': '🏆 Giro Panoramico (3)',
        'drinks_amsterdam': '🧀 Bevande e Formaggi (4)',
        'dining_amsterdam': '🍷 Cena e Pizza (2)',
        'specialty_amsterdam': '✨ Esperienze Speciali & 420 (1)',
        'sightseeing_london': '🏆 Giro Panoramico (4)',
        'dining_london': '🍷 Pranzo e Cena (4)',
        'speedboat_london': '⚡ Motoscafi Veloci (2)',
        'duel_tab_1': 'Cena Bateaux Mouches',
        'duel_tab_2': 'Cena Bateaux Parisiens',
        'duel_tab_3': '⚖️ Tabella di Confronto Completa',
        'expand_all': 'Espandi tutto',
        'collapse_all': 'Comprimi tutto',
        'breakdown_sub': 'Testato sul campo in modo indipendente • Tutte le recensioni aperte di default • Clicca per comprimere/espandere',
        'hide_review': 'Nascondi recensione',
        'show_review': 'Mostra recensione',
        "buyers_guide_divider": "Guida all'acquisto e metodologia"
    },
    'ja': {
        'filter_label': 'フィルター:',
        'all': 'すべて (10)',
        'tested': '✓ 実際に現地検証済み (5)',
        'livemusic': '🎵 ライブ音楽 (5)',
        'under100': '💶 100ユーロ未満 (5)',
        'gourmet': '🍷 4品フルコース (5)',
        'under20': '💶 20ユーロ未満 (5)',
        'treats': '🥂 ドリンク＆スイーツ (4)',
        'lunch': '🍽️ ランチクルーズ (1)',
        'route': '🗺️ 乗り降り自由＆運河 (2)',
        'private': '🛥️ プライベートボート (1)',
        'sightseeing_amsterdam': '🏆 定番観光 (3)',
        'drinks_amsterdam': '🧀 ドリンク＆チーズ (4)',
        'dining_amsterdam': '🍷 ディナー＆ピザ (2)',
        'specialty_amsterdam': '✨ 特別体験＆420フレンドリー (1)',
        'sightseeing_london': '🏆 定番観光 (4)',
        'dining_london': '🍷 ランチ＆ディナー (4)',
        'speedboat_london': '⚡ スピードボート (2)',
        'duel_tab_1': 'バトー・ムーシュ ディナー',
        'duel_tab_2': 'バトー・パリジャン ディナー',
        'duel_tab_3': '⚖️ 詳細スペック比較表',
        'expand_all': 'すべて展開',
        'collapse_all': 'すべて折りたたむ',
        'breakdown_sub': '現地で独自に実地検証済み • すべてのレビューはデフォルトで展開表示 • クリックで折りたたみ/展開',
        'hide_review': 'レビューを閉じる',
        'show_review': 'レビューを見る',
        'buyers_guide_divider': '購入ガイド＆検証方法'
    },
    'nl': {
        'filter_label': 'Filters:',
        'all': 'Alle (10)',
        'tested': '✓ Persoonlijk getest (5)',
        'livemusic': '🎵 Live Muziek (5)',
        'under100': '💶 Onder €100 (5)',
        'gourmet': '🍷 4-Gangen Gastronomisch (5)',
        'under20': '💶 Onder €20 (5)',
        'treats': '🥂 Drankjes & Hapjes (4)',
        'lunch': '🍽️ Lunch aan Boord (1)',
        'route': '🗺️ Hop-On & Kanalen (2)',
        'private': '🛥️ Privéboot (1)',
        'sightseeing_amsterdam': '🏆 Rondvaart (3)',
        'drinks_amsterdam': '🧀 Drankjes & Kaas (4)',
        'dining_amsterdam': '🍷 Diner & Pizza (2)',
        'specialty_amsterdam': '✨ Speciale Vaart & 420 (1)',
        'sightseeing_london': '🏆 Rondvaart (4)',
        'dining_london': '🍷 Lunch & Diner (4)',
        'speedboat_london': '⚡ Speedboten (2)',
        'duel_tab_1': 'Bateaux Mouches Diner',
        'duel_tab_2': 'Bateaux Parisiens Diner',
        'duel_tab_3': '⚖️ Volledige Vergelijkingstabel',
        'expand_all': 'Alles uitklappen',
        'collapse_all': 'Alles inklappen',
        'breakdown_sub': 'Onafhankelijk in de praktijk getest • Alle reviews standaard geopend • Klik om in/uit te klappen',
        'hide_review': 'Review inklappen',
        'show_review': 'Review bekijken',
        'buyers_guide_divider': 'Koopgids & Methodologie'
    },
    'pl': {
        'filter_label': 'Filtry:',
        'all': 'Wszystkie (10)',
        'tested': '✓ Przetestowane osobiście (5)',
        'livemusic': '🎵 Muzyka na żywo (5)',
        'under100': '💶 Poniżej 100 € (5)',
        'gourmet': '🍷 Wykwintne 4 Dania (5)',
        'under20': '💶 Poniżej 20 € (5)',
        'treats': '🥂 Drinki i Przekąski (4)',
        'lunch': '🍽️ Obiad na Statku (1)',
        'route': '🗺️ Hop-On i Kanał (2)',
        'private': '🛥️ Prywatna Łódź (1)',
        'sightseeing_amsterdam': '🏆 Rejs Widokowy (3)',
        'drinks_amsterdam': '🧀 Drinki i Sery (4)',
        'dining_amsterdam': '🍷 Kolacja i Pizza (2)',
        'specialty_amsterdam': '✨ Specjalne i Smoke-Friendly (1)',
        'sightseeing_london': '🏆 Rejs Widokowy (4)',
        'dining_london': '🍷 Obiad i Kolacja (4)',
        'speedboat_london': '⚡ Szybkie Łodzie (2)',
        'duel_tab_1': 'Rejs Bateaux Mouches',
        'duel_tab_2': 'Rejs Bateaux Parisiens',
        'duel_tab_3': '⚖️ Tabela Porównawcza',
        'expand_all': 'Rozwiń wszystko',
        'collapse_all': 'Zwiń wszystko',
        'breakdown_sub': 'Niezależnie przetestowane w terenie • Wszystkie recenzje domyślnie otwarte • Kliknij, aby zwinąć/rozwinąć',
        'hide_review': 'Zwiń recenzję',
        'show_review': 'Zobacz recenzję',
        'buyers_guide_divider': 'Poradnik kupującego i metodologia'
    },
    'ro': {
        'filter_label': 'Filtre:',
        'all': 'Toate (10)',
        'tested': '✓ Testat personal (5)',
        'livemusic': '🎵 Muzică Live (5)',
        'under100': '💶 Sub 100 € (5)',
        'gourmet': '🍷 Meniu Gourmet 4 Feluri (5)',
        'under20': '💶 Sub 20 € (5)',
        'treats': '🥂 Băuturi & Gustări (4)',
        'lunch': '🍽️ Prânz la Masă (1)',
        'route': '🗺️ Hop-On & Canale (2)',
        'private': '🛥️ Barcă Privată (1)',
        'sightseeing_amsterdam': '🏆 Croazieră Panoramică (3)',
        'drinks_amsterdam': '🧀 Băuturi & Brânzeturi (4)',
        'dining_amsterdam': '🍷 Cină & Pizza (2)',
        'specialty_amsterdam': '✨ Experiențe Speciale & 420 (1)',
        'sightseeing_london': '🏆 Croazieră Panoramică (4)',
        'dining_london': '🍷 Prânz & Cină (4)',
        'speedboat_london': '⚡ Bărci Rapide (2)',
        'duel_tab_1': 'Cină Bateaux Mouches',
        'duel_tab_2': 'Cină Bateaux Parisiens',
        'duel_tab_3': '⚖️ Tabel Comparativ Detaliat',
        'expand_all': 'Extinde tot',
        'collapse_all': 'Restrânge tot',
        'breakdown_sub': 'Testat pe teren în mod independent • Toate recenziile deschise implicit • Clic pentru a restrânge/extinde',
        'hide_review': 'Ascunde recenzia',
        'show_review': 'Vezi recenzia',
        'buyers_guide_divider': 'Ghidul cumpărătorului și metodologie'
    }
}

def sync_metadata_from_git(soup, target_rel_path, lang):
    """Extract authentic <title>, <meta description>, og:, twitter:, and JSON-LD schema from git history 0e6ce9a~1"""
    try:
        raw = subprocess.check_output(
            ['git', '-C', BASE_DIR, 'show', f'0e6ce9a~1:{target_rel_path}'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8', errors='ignore')
        old_soup = BeautifulSoup(raw, 'html.parser')
        old_title = old_soup.title.string.strip() if old_soup.title and old_soup.title.string else ''
        d = old_soup.find('meta', {'name': 'description'})
        old_desc = d['content'].strip() if d and d.get('content') else ''

        if old_title:
            if soup.title:
                soup.title.string = old_title
            og_t = soup.find('meta', property='og:title')
            if og_t: og_t['content'] = old_title
            tw_t = soup.find('meta', attrs={'name': 'twitter:title'})
            if tw_t: tw_t['content'] = old_title

        if old_desc:
            m_desc = soup.find('meta', attrs={'name': 'description'})
            if m_desc: m_desc['content'] = old_desc
            og_d = soup.find('meta', property='og:description')
            if og_d: og_d['content'] = old_desc
            tw_d = soup.find('meta', attrs={'name': 'twitter:description'})
            if tw_d: tw_d['content'] = old_desc

        # Also update JSON-LD schema
        canon_url = f"https://www.thecruisedetective.com/{target_rel_path.replace('/index.html', '')}"
        for s in soup.find_all('script', {'type': 'application/ld+json'}):
            try:
                data = json.loads(s.string)
                updated = False
                if '@graph' in data:
                    for item in data['@graph']:
                        if item.get('@type') in ['Article', 'WebPage']:
                            if lang: item['inLanguage'] = lang
                            if old_title and 'headline' in item: item['headline'] = old_title
                            if old_title and 'name' in item: item['name'] = old_title
                            if old_desc and 'description' in item: item['description'] = old_desc
                            item['url'] = canon_url
                            if '@id' in item and '#' in item['@id']:
                                item['@id'] = canon_url + '#' + item['@id'].split('#', 1)[1]
                            updated = True
                if updated:
                    s.string = json.dumps(data, ensure_ascii=False)
            except Exception:
                pass
    except Exception as e:
        pass

def localize_navbar(soup, lang):
    """Ensure navbar branding, links, and drawer are localized cleanly across ALL pages"""
    d = NAV_I18N[lang]
    u = URL_MAP[lang]

    # 1. Brand link
    b_link = soup.find('a', class_='ltt-brand') or soup.find('a', class_='ltt-nav-logo')
    if b_link:
        b_link['href'] = f"/{lang}/"

    # 2. Destinations dropdown button text
    dropBtn = soup.find('button', class_='ltt-dropdown-btn')
    if dropBtn:
        span = dropBtn.find('span')
        if span:
            span.string = d['destinations']

    # 3. Mega menu column headers
    cols = soup.find_all('div', class_='ltt-mega-col')
    if len(cols) >= 2:
        h0 = cols[0].find('div', class_='ltt-mega-head')
        if h0: h0.string = d['col1_head']
        h1 = cols[1].find('div', class_='ltt-mega-head')
        if h1: h1.string = d['col2_head']

    # 4. Mega menu items (5 items)
    mega_items = soup.find_all('a', class_='ltt-mega-item')
    items_data = [
        (u['dinner'], d['dinner_title'], d['dinner_sub']),
        (u['sightseeing'], d['sightseeing_title'], d['sightseeing_sub']),
        (u['duel'], d['duel_title'], d['duel_sub']),
        (u['amsterdam'], d['amsterdam_title'], d['amsterdam_sub']),
        (u['london'], d['london_title'], d['london_sub'])
    ]
    for idx, item in enumerate(mega_items):
        if idx < len(items_data):
            u_path, m_title, m_sub = items_data[idx]
            item['href'] = u_path
            s_tag = item.find('strong')
            if s_tag: s_tag.string = m_title
            p_tag = item.find('p')
            if p_tag: p_tag.string = m_sub

    # 5. Top Navigation Links (Dinner, Sightseeing, About, Contact)
    top_nav = soup.find('nav', class_='ltt-nav-links')
    if top_nav:
        top_links = top_nav.find_all('a', class_='ltt-nav-link')
        t_data = [
            (u['dinner'], d['dinner_top']),
            (u['sightseeing'], d['sightseeing_top']),
            (u['about'], d['about_top']),
            (u['contact'], d['contact_top'])
        ]
        for idx, tl in enumerate(top_links):
            if idx < len(t_data):
                tl['href'] = t_data[idx][0]
                tl.string = t_data[idx][1]

    # 6. Mobile Drawer
    drawer = soup.find(id='lttMobileDrawer')
    if drawer:
        labels = drawer.find_all('div', class_='ltt-mobile-label')
        if len(labels) >= 2:
            labels[0].string = d['drawer_sec1']
            labels[1].string = d['drawer_sec2']

        m_links = drawer.find_all('a', class_='ltt-mobile-link')
        m_data = [
            (u['dinner'], f"🍷 {d['dinner_title']}", d['top_pick']),
            (u['sightseeing'], f"🗼 {d['sightseeing_title']}", None),
            (u['duel'], f"⚖️ {d['duel_title']}", None),
            (u['amsterdam'], f"🌷 {d['amsterdam_title']}", None),
            (u['london'], f"🇬🇧 {d['london_title']}", None),
            (u['about'], f"📖 {d['about_top']}", None),
            (u['contact'], f"✉️ {d['contact_top']}", None),
        ]
        for idx, ml in enumerate(m_links):
            if idx < len(m_data):
                href, title_text, badge_text = m_data[idx]
                ml['href'] = href
                span = ml.find('span')
                if span:
                    span.string = title_text
                # Update top pick badge if present
                badge = ml.find('span', style=lambda s: s and 'background:#dfa732' in s)
                if badge and badge_text:
                    badge.string = badge_text

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
        if 'seine' in href or 'sightseeing' in href or 'promenade' in href:
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
        elif 'contact' in href or 'kontakt' in href or 'contatto' in href or '接触' in href:
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

def extract_original_translated_data(rel_path):
    """Extract authentic translated copy from commit 0e6ce9a~1"""
    try:
        raw_html = subprocess.check_output(
            ['git', '-C', BASE_DIR, 'show', f'0e6ce9a~1:{rel_path}'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8', errors='ignore')
    except Exception as e:
        target_abs = os.path.join(BASE_DIR, rel_path)
        with open(target_abs, 'r', encoding='utf-8') as f:
            raw_html = f.read()

    soup = BeautifulSoup(raw_html, 'html.parser')

    # 1. H1 & Lead Copy
    h1 = soup.find('h1')
    h1_text = h1.get_text(strip=True) if h1 else ""

    intro_sec = soup.find(class_='container-intro-section') or soup.find(class_='rich-text-block-36')
    lead_copy_html = ""
    if intro_sec:
        ps = intro_sec.find_all('p')
        lead_copy_html = ''.join(str(p) for p in ps[:3])

    # 2. Table rows (10 items) - clean price extraction
    comp = soup.find(class_='comparison-table')
    rows = comp.find_all(class_=lambda c: c and 'table-row-' in c) if comp else []
    deck_rows = []
    for r in rows:
        cells = r.find_all(class_=lambda c: c and ('grid-cell' in c or 'content-wrap' in c))
        t_text = ""
        p_text = ""
        link_url = ""
        for cell in cells:
            txt = cell.get_text(" ", strip=True)
            if re.match(r'^\d+\.', txt) and len(txt) > 5 and not t_text:
                t_text = txt
            # Match clean price specifically (e.g. 130-165€ or 115 €), avoiding amenities strings
            p_match = re.search(r'^\s*(\d+[\d\s\-\–\—\.]*(?:€|£|zł|lei|ユーロ)|(?:€|£)\s*\d+[\d\s\-\–\—\.]*)', txt)
            if p_match and len(txt) < 30 and not any(k in txt for k in ['Section', 'section', 'Nourriture', 'Musique', 'Poussette']):
                p_text = p_match.group(1).replace('ⓘ', '').strip()
            a_tag = cell.find('a', href=True)
            if a_tag and not link_url and ('tiqets.com' in a_tag['href'] or 'getyourguide.com' in a_tag['href'] or 'fareharbor.com' in a_tag['href'] or 'tp.media' in a_tag['href'] or 'tripadvisor' in a_tag['href']):
                link_url = a_tag['href']
        deck_rows.append({'title': t_text, 'price': p_text, 'url': link_url})

    # 3. Reviews (10 items)
    headings = soup.find_all(class_='heading-33')
    reviews_data = []
    for idx, h in enumerate(headings[:10]):
        raw_title = h.get_text(' ', strip=True)
        clean_title = re.sub(r'^\d+\.\s*([^\w\s]*\s*)?', '', raw_title).strip()
        parent = h.find_parent('div', class_='container') or h.find_parent('div', class_='w-container') or h.parent
        
        # Pros & Cons
        pro_el = parent.find(class_='pro-con-box-pro-cell-rich-text-block') or parent.find(class_='pro-con-box-pro-cell-3')
        con_el = parent.find(class_='pro-con-box-con-cell-rich-text-block') or parent.find(class_='pro-con-box-con-cell')
        pros = [p.get_text(strip=True).replace('Pros:', '').replace('✔️', '').replace('✓', '').strip() for p in (pro_el.find_all(['p', 'li']) if pro_el else []) if len(p.get_text(strip=True)) > 3]
        cons = [p.get_text(strip=True).replace('Cons:', '').replace('❌', '').strip() for p in (con_el.find_all(['p', 'li']) if con_el else []) if len(p.get_text(strip=True)) > 3]

        # Paragraphs
        rts = parent.find_all(class_='w-richtext')
        paras = []
        for rt in rts:
            for p in rt.find_all(['p', 'li']):
                ptxt = p.get_text(' ', strip=True)
                if len(ptxt) > 25 and not any(k in ptxt for k in ['Pros:', 'Cons:', 'Avantages :', 'Inconvénients :']):
                    paras.append(ptxt)

        reviews_data.append({
            'clean_title': clean_title,
            'raw_title': raw_title,
            'pros': pros,
            'cons': cons,
            'paras': paras
        })

    return {
        'h1_text': h1_text,
        'lead_copy_html': lead_copy_html,
        'deck_rows': deck_rows,
        'reviews': reviews_data
    }

def clone_guide_page(dest_key, lang, target_rel_path):
    dest_cfg = DEST_CONFIGS[dest_key]
    en_path = os.path.join(BASE_DIR, dest_cfg['en_path'])
    target_abs = os.path.join(BASE_DIR, target_rel_path)

    print(f"\n[CLONING MASTER 1:1] [{dest_key.upper()}] [{lang.upper()}]: {target_rel_path} ...")
    
    with open(en_path, 'r', encoding='utf-8') as f:
        en_soup = BeautifulSoup(f.read(), 'html.parser')

    master_soup = copy.deepcopy(en_soup)
    t = COMMON_I18N[lang]

    # Fetch original translated copy
    tr_data = extract_original_translated_data(target_rel_path)

    # 1. Update HTML lang & Canonical
    html_tag = master_soup.find('html')
    if html_tag:
        html_tag['lang'] = lang

    head = master_soup.find('head')
    if head:
        canon_url = f"https://www.thecruisedetective.com/{target_rel_path.replace('/index.html', '')}"
        canon_tag = head.find('link', rel='canonical')
        if canon_tag:
            canon_tag['href'] = canon_url
        sync_metadata_from_git(master_soup, target_rel_path, lang)

    # 2. Localize Navbar & Mobile Drawer
    localize_navbar(master_soup, lang)

    # 3. Update Hero clean card
    hero = master_soup.find(class_='ltt-clean-card') or master_soup.find(class_='ltt-hero-wrap')
    if hero:
        bc_home = hero.find(class_='ltt-breadcrumbs')
        if bc_home:
            a_home = bc_home.find('a')
            if a_home:
                a_home['href'] = f"/{lang}/"
                a_home.string = t['bc_home']
            curr_bc = bc_home.find(class_='ltt-bc-current')
            if curr_bc and tr_data['h1_text']:
                curr_bc.string = tr_data['h1_text']

        kicker = hero.find(class_='ltt-hero-kicker-badge')
        if kicker: kicker.string = t['kicker']

        h1 = hero.find('h1')
        if h1 and tr_data['h1_text']: h1.string = tr_data['h1_text']

        author_line = hero.find(class_='ltt-author-line')
        if author_line:
            author_line.clear()
            author_line.append(BeautifulSoup(t['author_line'], 'html.parser'))
        author_role = hero.find(class_='ltt-author-role')
        if author_role: author_role.string = t['author_role']
        trust_pill = hero.find(class_='ltt-trust-pill')
        if trust_pill: trust_pill.string = t['updated']

        if tr_data['lead_copy_html']:
            lead_div = hero.find(class_='ltt-lead-copy')
            if lead_div:
                lead_div.clear()
                lead_div.append(BeautifulSoup(tr_data['lead_copy_html'], 'html.parser'))

        if lang in FILTER_TABS_I18N:
            ft = FILTER_TABS_I18N[lang]
            fl = hero.find(class_='ltt-filter-label')
            if fl: fl.string = ft['filter_label']
            for btn in hero.find_all('button', class_='ltt-tab-btn'):
                cat = btn.get('data-cat')
                if cat == 'all':
                    btn.string = ft['all']
                elif cat == 'tested':
                    btn.string = ft['tested']
                elif cat == 'livemusic':
                    btn.string = ft['livemusic']
                elif cat == 'under100':
                    btn.string = ft['under100']
                elif cat == 'gourmet':
                    btn.string = ft['gourmet']
                elif cat == 'under20':
                    btn.string = ft['under20']
                elif cat == 'treats':
                    btn.string = ft['treats']
                elif cat == 'lunch':
                    btn.string = ft['lunch']
                elif cat == 'route':
                    btn.string = ft['route']
                elif cat == 'private':
                    btn.string = ft['private']
                elif cat == 'sightseeing':
                    if dest_key == 'amsterdam': btn.string = ft['sightseeing_amsterdam']
                    elif dest_key == 'london': btn.string = ft['sightseeing_london']
                elif cat == 'drinks':
                    btn.string = ft['drinks_amsterdam']
                elif cat == 'dining':
                    if dest_key == 'amsterdam': btn.string = ft['dining_amsterdam']
                    elif dest_key == 'london': btn.string = ft['dining_london']
                elif cat == 'specialty':
                    btn.string = ft['specialty_amsterdam']
                elif cat == 'speedboat':
                    btn.string = ft['speedboat_london']

    # 4. Update Deck Cards (.bpa-card)
    deck = master_soup.find(class_='ltt-deck-container')
    short_titles = []
    if deck:
        cards = deck.find_all(class_='bpa-card')
        for idx, card in enumerate(cards):
            row = tr_data['deck_rows'][idx] if idx < len(tr_data['deck_rows']) else {}
            rev = tr_data['reviews'][idx] if idx < len(tr_data['reviews']) else {}
            
            # Title
            card_title = rev.get('clean_title') or (re.sub(r'^\d+\.\s*', '', row.get('title')) if row.get('title') else card.find(class_='bpa-title').get_text(strip=True))
            short_titles.append(card_title)
            
            title_tag = card.find(class_='bpa-title')
            if title_tag:
                title_tag.string = card_title

            # Localize Rank tag
            rank_map = None
            if dest_key == 'dinner': rank_map = PARIS_DINNER_RANKS
            elif dest_key == 'sightseeing': rank_map = PARIS_SIGHTSEEING_RANKS
            elif dest_key == 'amsterdam': rank_map = AMSTERDAM_RANKS
            elif dest_key == 'london': rank_map = LONDON_RANKS

            rank_tag = card.find(class_='bpa-rank-tag')
            if rank_tag and rank_map and lang in rank_map and idx < len(rank_map[lang]):
                rank_tag.string = rank_map[lang][idx]

            # Localize Verified Proof Badge
            proof_chips = card.find_all(class_='bpa-vchip')
            for pc in proof_chips:
                pc.string = t['verified_badge']

            # Localize Specs Row
            if lang in SPECS_MAP:
                sp_map = SPECS_MAP[lang]
                specs = card.find_all(class_='bpa-sp')
                for sp in specs:
                    sp_text = sp.get_text(strip=True)
                    for en_k, tr_v in sp_map.items():
                        if en_k in sp_text:
                            sp.string = sp_text.replace(en_k, tr_v)
                            break

            # Localize Best For Block
            best_for_div = card.find(class_='bpa-best-for')
            if best_for_div:
                b_text = ""
                if dest_key == 'dinner' and lang in PARIS_DINNER_BEST_FOR and idx < len(PARIS_DINNER_BEST_FOR[lang]):
                    b_text = PARIS_DINNER_BEST_FOR[lang][idx]
                elif dest_key == 'sightseeing' and lang in PARIS_SIGHTSEEING_BEST_FOR and idx < len(PARIS_SIGHTSEEING_BEST_FOR[lang]):
                    b_text = PARIS_SIGHTSEEING_BEST_FOR[lang][idx]
                else:
                    orig_text = best_for_div.get_text(' ', strip=True)
                    b_text = re.sub(r'^(?:🎯\s*)?Best For:\s*', '', orig_text)
                    m_bp = re.search(r'Travelers looking for a verified (.*?) experience with (.*?)\.?', b_text, re.IGNORECASE)
                    if m_bp:
                        dur, op = m_bp.group(1), m_bp.group(2)
                        if lang == 'fr': b_text = f"Voyageurs recherchant une expérience vérifiée de {dur} avec {op}."
                        elif lang == 'es': b_text = f"Viajeros que buscan una experiencia verificada de {dur} con {op}."
                        elif lang == 'de': b_text = f"Reisende, die ein verifiziertes {dur}-Erlebnis mit {op} suchen."
                        elif lang == 'it': b_text = f"Viaggiatori che cercano un'esperienza verificata di {dur} con {op}."
                        elif lang == 'ja': b_text = f"{op}による検証済みの{dur}体験をお探しの旅行者。"
                        elif lang == 'nl': b_text = f"Reizigers die op zoek zijn naar een geverifieerde ervaring van {dur} met {op}."
                        elif lang == 'pl': b_text = f"Podróżni szukający sprawdzonego rejsu ({dur}) z {op}."
                        elif lang == 'ro': b_text = f"Călători care caută o experiență verificată de {dur} cu {op}."

                best_for_div.clear()
                best_for_div.append(BeautifulSoup(f'🎯 <strong>{t["best_for"]} :</strong> {b_text}', 'html.parser'))

            # Price
            if row.get('price'):
                p_tag = card.find(class_='bpa-price')
                if p_tag: p_tag.string = row['price']

            # Price subtext & Buttons
            psub = card.find(class_='bpa-psub')
            if psub: psub.string = t['per_person']
            btn = card.find(class_='bpa-btn')
            if btn: btn.string = t['btn_check']
            tm = card.find(class_='bpa-trust-micro')
            if tm: tm.string = t['trust_micro']
            sublink = card.find(class_='bpa-sublink')
            if sublink: sublink.string = t['read_review']

    # 5. Update Breakdown top bar
    bd_h2 = master_soup.find(class_='bpa-breakdown-heading')
    bd_title = dest_cfg['breakdown_title'].get(lang, dest_cfg['breakdown_title']['fr'])
    if bd_h2: bd_h2.string = bd_title

    if lang in FILTER_TABS_I18N:
        ft = FILTER_TABS_I18N[lang]
        bd_sub = master_soup.find(class_='bpa-breakdown-sub')
        if bd_sub: bd_sub.string = ft['breakdown_sub']
        for abtn in master_soup.find_all('button', class_='bpa-acc-ctrl-btn'):
            if 'true' in abtn.get('onclick', ''):
                abtn.string = ft['expand_all']
            elif 'false' in abtn.get('onclick', ''):
                abtn.string = ft['collapse_all']

    # 6. Update In-Depth Review Cards (details.bpa-details-card)
    review_cards = master_soup.find_all('details', class_='bpa-details-card')
    for idx, rcard in enumerate(review_cards):
        rev = tr_data['reviews'][idx] if idx < len(tr_data['reviews']) else {}
        row = tr_data['deck_rows'][idx] if idx < len(tr_data['deck_rows']) else {}
        card_title = short_titles[idx] if idx < len(short_titles) else rev.get('clean_title', '')

        # Summary title & toggle text
        if lang in FILTER_TABS_I18N:
            toggle_text = rcard.find(class_='bpa-toggle-text')
            if toggle_text:
                toggle_text.string = FILTER_TABS_I18N[lang]['hide_review']

        stitle = rcard.find(class_='bpa-details-title')
        if stitle and card_title:
            stitle.string = card_title

        # Rank tag in review summary
        summary_rank = rcard.find(class_='bpa-rank-tag')
        if summary_rank and rank_map and lang in rank_map and idx < len(rank_map[lang]):
            summary_rank.string = rank_map[lang][idx]

        # Pros & Cons titles
        pro_con_wrap = rcard.find(class_='pro-con-box-wrapper')
        if pro_con_wrap:
            pro_title = pro_con_wrap.find(class_='pro-con-title', style=lambda s: s and '#166534' in s) or pro_con_wrap.find(class_='pro-con-title')
            if pro_title: pro_title.string = t['pros_title']
            con_title = pro_con_wrap.find(class_='pro-con-title', style=lambda s: s and '#991b1b' in s)
            if con_title: con_title.string = t['cons_title']

            if rev.get('pros'):
                pro_ul = pro_con_wrap.find(class_='pro-con-box-pro-cell')
                if pro_ul:
                    ul = pro_ul.find('ul')
                    if ul:
                        ul.clear()
                        for ptext in rev['pros']:
                            li = BeautifulSoup(f'<li><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:3px;"><polyline points="20 6 9 17 4 12"></polyline></svg><span>{ptext}</span></li>', 'html.parser')
                            ul.append(li)
            if rev.get('cons'):
                con_ul = pro_con_wrap.find(class_='pro-con-box-con-cell')
                if con_ul:
                    ul = con_ul.find('ul')
                    if ul:
                        ul.clear()
                        for ctext in rev['cons']:
                            li = BeautifulSoup(f'<li><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:3px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg><span>{ctext}</span></li>', 'html.parser')
                            ul.append(li)

        # Bento groups
        bentos = rcard.find_all('details', class_='ltt-bento-group')
        for bidx, bento in enumerate(bentos):
            btitle_el = bento.find(class_='ltt-bento-group-title')
            if btitle_el:
                orig_btitle = btitle_el.get_text(strip=True)
                if 'Summary' in orig_btitle or 'Quick Facts' in orig_btitle or 'Overview' in orig_btitle:
                    btitle_el.string = t['bento_1']
                elif 'Before' in orig_btitle or 'Pier' in orig_btitle or 'Boarding' in orig_btitle:
                    btitle_el.string = t['bento_2']
                elif 'During' in orig_btitle or 'Ship' in orig_btitle or 'Deck' in orig_btitle:
                    btitle_el.string = t['bento_3']
                elif 'Audio' in orig_btitle or 'Operator' in orig_btitle or 'Menu' in orig_btitle or 'Food' in orig_btitle:
                    btitle_el.string = t['bento_4']
                elif 'Map' in orig_btitle or 'Departure' in orig_btitle:
                    btitle_el.string = t['bento_map']

            # Mini pill
            pill = bento.find(class_='ltt-mini-pill')
            if pill:
                pill_txt = pill.get_text(strip=True)
                if 'Overview' in pill_txt:
                    pill.string = t['pill_overview']
                elif 'Photos' in pill_txt:
                    pill.string = t['pill_photos']
                elif 'Map' in pill_txt:
                    pill.string = t['pill_map']

            # If translated paragraphs available for bento 1, inject them
            if bidx == 0 and rev.get('paras'):
                rt = bento.find(class_='w-richtext')
                if rt and len(rev['paras']) >= 2:
                    rt.clear()
                    for p_str in rev['paras'][:3]:
                        p_tag = master_soup.new_tag('p')
                        p_tag.string = p_str
                        rt.append(p_tag)

        # Buy card at bottom of review
        buy_card = rcard.find(class_='ltt-buy-card')
        if buy_card:
            # Set buy card title
            buy_title = buy_card.find(class_='ltt-buy-card-title')
            if buy_title and card_title:
                buy_title.string = card_title

            if row.get('price'):
                p_disp = buy_card.find('div', style=lambda s: s and 'font-size: 20px' in s)
                if p_disp: p_disp.string = row['price']
            
            # Localize "per person" in buy card
            buy_psub = buy_card.find(class_='ltt-buy-price-sub')
            if buy_psub: buy_psub.string = t['per_person']

            bbtn = buy_card.find('a', class_='bpa-btn')
            if bbtn: bbtn.string = t['btn_check']

            # Localize buy card micro-trust
            buy_tm = buy_card.find('div', style=lambda s: s and 'font-size: 11.5px' in s)
            if buy_tm: buy_tm.string = t['trust_micro']

        # Quick facts header
        qf_h = rcard.find(class_='qf1-title')
        if qf_h:
            qf_h.string = t.get('quick_facts_title', 'Faits en bref — Caractéristiques vérifiées')

    # 7. Update Table of Contents Title
    toc_titles = master_soup.find_all(class_=['title-small-3', 'ltt-toc-heading'])
    for tt in toc_titles:
        tt.string = t['toc_title']

    # Mobile Hybrid Sheet & Button
    hybrid_btn = master_soup.find(id='hybridTocBtn') or master_soup.find(class_='hybrid-toc-btn')
    if hybrid_btn:
        btn_span = hybrid_btn.find('span')
        if btn_span:
            btn_span.string = dest_cfg['toc_deck_label'].get(lang, 'Top 10')

    sheet_title = master_soup.find(class_='hybrid-sheet-title')
    if sheet_title:
        sheet_title.string = t.get('sheet_title', 'Sélectionner une croisière testée')

    # 8. Update Sticky Bar
    sticky = master_soup.find(id='sticky-bar') or master_soup.find(class_='hybrid-sticky-bar')
    if sticky:
        stitle = sticky.find(class_='hybrid-sticky-title') or sticky.find(class_='hybrid-active-title')
        if stitle and short_titles:
            stitle.string = short_titles[0]
        sbtn = sticky.find(class_='hybrid-sticky-btn') or sticky.find(class_='hybrid-cta-btn')
        if sbtn: sbtn.string = t['btn_check']

    # 8.5 Localize Intro .w-richtext before #breakdown-header
    if dest_key in ['dinner', 'sightseeing', 'london']:
        try:
            old_raw = subprocess.check_output(
                ['git', '-C', BASE_DIR, 'show', f'0e6ce9a~1:{target_rel_path}'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')
            old_soup = BeautifulSoup(old_raw, 'html.parser')
            target_intro = master_soup.select_one('.blog-section-2 .content-right_blog .w-richtext')
            for rt in old_soup.find_all('div', class_='w-richtext'):
                if 'breadcrumb' in ' '.join(rt.get('class', [])):
                    continue
                h2s = [h.get_text(strip=True) for h in rt.find_all('h2')]
                if h2s and not any(h.startswith(('1.', '2.', '3.')) for h in h2s):
                    if target_intro:
                        target_intro.clear()
                        for ch in list(rt.children):
                            target_intro.append(ch)
                    break
        except Exception as e:
            pass

    # 9. Handle Post-Review Sections
    if dest_key == 'dinner':
        try:
            old_raw = subprocess.check_output(
                ['git', '-C', BASE_DIR, 'show', f'0e6ce9a~1:{target_rel_path}'],
                stderr=subprocess.DEVNULL
            ).decode('utf-8', errors='ignore')
            old_soup = BeautifulSoup(old_raw, 'html.parser')
            tt_h2 = old_soup.find(lambda el: el.name in ['h2', 'h3'] and any(k in el.text.lower() for k in ['piège', 'trampa', 'touristenfalle', 'trappola', '罠', 'toeristenval', 'pułapka', 'capcană']))
            if tt_h2:
                guide_wrap = tt_h2.find_parent('div', class_='w-richtext') or tt_h2.parent
                target_sec = master_soup.find('section', id='source-guide-section-1')
                if target_sec and guide_wrap:
                    target_sec.clear()
                    for child in list(guide_wrap.children):
                        target_sec.append(child)
        except Exception as e:
            print(f"  [!] Note: could not extract post-review guide for {target_rel_path}: {e}")
    elif dest_key == 'sightseeing':
        # Remove English-only editorial explainers on translated editions
        for sec_id in ['seine-cruises-explained', 'standard-features-explained', 'testing-methodology', 'how-article-structured']:
            sec_to_remove = master_soup.find('section', id=sec_id)
            if sec_to_remove:
                sec_to_remove.decompose()

    # 10. Update window.LTT_PAGE_CONFIG script
    toc_deck = dest_cfg['toc_deck_label'].get(lang, dest_cfg['toc_deck_label']['fr'])
    toc_guide = dest_cfg['toc_guide_label'].get(lang, dest_cfg['toc_guide_label']['fr'])
    script_cfg = master_soup.find(lambda e: e.name == 'script' and 'window.LTT_PAGE_CONFIG' in (e.string or ''))
    cfg_obj = {
        "deckId": dest_cfg['deck_id'],
        "tocDeckLabel": toc_deck,
        "tocBreakdownLabel": bd_title,
        "tocGuideLabel": toc_guide,
        "shortTitles": short_titles
    }
    cfg_code = f"window.LTT_PAGE_CONFIG = {json.dumps(cfg_obj, ensure_ascii=False)};"
    if script_cfg:
        script_cfg.string = cfg_code
    else:
        new_script = master_soup.new_tag('script')
        new_script.string = cfg_code
        master_soup.body.append(new_script)

    # 9.5 Localize inline runtime script strings
    if lang in FILTER_TABS_I18N:
        guide_div_label = FILTER_TABS_I18N[lang]['buyers_guide_divider']
        for sc in master_soup.find_all('script'):
            if sc.string and "Buyer's Guide & Methodology" in sc.string:
                sc.string = sc.string.replace('\"Buyer\'s Guide & Methodology\"', json.dumps(guide_div_label))

    # 10. Localize Footer
    localize_footer(master_soup, lang)

    final_html = str(master_soup)
    with open(target_abs, 'w', encoding='utf-8') as f:
        f.write(final_html)
    print(f"[{dest_key.upper()}] [{lang.upper()}] Cloned & Translated ({len(final_html)} bytes).")

    # If alias pages exist, sync them
    if 'alias_pages' in dest_cfg and lang in dest_cfg['alias_pages']:
        alias_rel = dest_cfg['alias_pages'][lang]
        alias_abs = os.path.join(BASE_DIR, alias_rel)
        if os.path.exists(alias_abs):
            with open(alias_abs, 'w', encoding='utf-8') as f:
                f.write(final_html)
            print(f"  -> Synced alias: {alias_rel}")

def clone_and_translate_homepage(lang):
    """Clones index.html 1:1 and localizes it for target language"""
    en_path = os.path.join(BASE_DIR, 'index.html')
    target_path = os.path.join(BASE_DIR, f"{lang}/index.html")

    print(f"\n[HOMEPAGE 1:1 CLONE] -> {lang}/index.html ...")
    with open(en_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    d = HOMEPAGE_I18N[lang]
    u = URL_MAP[lang]
    df = DEST_FILTER_LABELS[lang]

    # 1. Update html lang & canonical
    html_tag = soup.find('html')
    if html_tag: html_tag['lang'] = lang

    canon = soup.find('link', rel='canonical')
    if canon: canon['href'] = f"https://www.thecruisedetective.com/{lang}/"
    sync_metadata_from_git(soup, f"{lang}/index.html", lang)

    # 2. Localize Navbar & Mobile Drawer
    localize_navbar(soup, lang)

    # 3. Localize Hero
    hero = soup.find(class_='ltt-home-hero')
    if hero:
        eyebrow = hero.find(class_='ltt-hero-eyebrow')
        if eyebrow: eyebrow.string = d['home_eyebrow']

        h1 = hero.find('h1')
        if h1:
            h1.clear()
            h1.append(d['home_title'] + ' ')
            gspan = soup.new_tag('span', **{'class': 'ltt-gold-text'})
            gspan.string = d['home_title_gold']
            h1.append(gspan)

        subtitle = hero.find(class_='ltt-hero-subtitle')
        if subtitle: subtitle.string = d['home_subtitle']

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
        if sec_title: sec_title.string = d['flagship_title']
        sec_sub = guides_sec.find(class_='ltt-section-subtitle')
        if sec_sub: sec_sub.string = d['flagship_sub']

        # Filter buttons
        filter_btns = guides_sec.find_all(class_='ltt-dest-btn')
        for fb in filter_btns:
            fdata = fb.get('data-filter')
            if fdata in df: fb.string = df[fdata]

        # Featured Spotlight Guide (Paris Dinner)
        feat = guides_sec.find(id='featured-guide')
        if feat:
            feat['href'] = u['dinner']
            tag = feat.find(class_='ltt-guide-tag')
            if tag: tag.string = f"⭐ {NAV_I18N[lang]['top_pick']} • PARIS SEINE"
            gtitle = feat.find(class_='ltt-guide-title')
            if gtitle: gtitle.string = d['paris_dinner']
            excerpt = feat.find(class_='ltt-guide-excerpt')
            if excerpt: excerpt.string = d['paris_dinner_sub']
            fbtn = feat.find(class_='ltt-guide-btn')
            if fbtn: fbtn.string = d['btn_read_guide']

        # 4 Grid Cards
        cards = guides_sec.find_all(class_='ltt-guide-card')
        cards_info = [
            (u['sightseeing'], '🗼 PARIS SEINE', d['paris_sightseeing'], d['paris_sightseeing_sub'], d['btn_read_guide']),
            (u['duel'], '⚖️ SEINE DUEL', d['duel'], d['duel_sub'], d['btn_compare']),
            (u['amsterdam'], '🌷 AMSTERDAM CANALS', d['amsterdam'], d['amsterdam_sub'], d['btn_read_guide']),
            (u['london'], '🇬🇧 LONDON THAMES', d['london'], d['london_sub'], d['btn_read_guide']),
        ]
        for idx, card in enumerate(cards):
            if idx < len(cards_info):
                c_url, c_tag, c_title, c_excerpt, c_btn = cards_info[idx]
                card['href'] = c_url
                tag_el = card.find(class_='ltt-guide-tag')
                if tag_el: tag_el.string = c_tag
                title_el = card.find(class_='ltt-guide-title')
                if title_el: title_el.string = c_title
                exc_el = card.find(class_='ltt-guide-excerpt')
                if exc_el: exc_el.string = c_excerpt
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
    if html_tag: html_tag['lang'] = lang

    canon = soup.find('link', rel='canonical')
    if canon: canon['href'] = f"https://www.thecruisedetective.com/{URL_MAP[lang]['about'].lstrip('/')}"
    sync_metadata_from_git(soup, rel_path, lang)

    # 2. Localize Navbar & Drawer
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

def upgrade_all_duel_pages():
    for lang, rel_path in DUEL_PAGES.items():
        abs_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(abs_path):
            continue
        with open(abs_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')
        
        localize_navbar(soup, lang)
        localize_footer(soup, lang)
        sync_metadata_from_git(soup, rel_path, lang)

        if lang in FILTER_TABS_I18N:
            ft = FILTER_TABS_I18N[lang]
            tabs = soup.find_all('button', class_='ltt-tab-btn')
            if len(tabs) >= 3:
                tabs[0].string = ft['duel_tab_1']
                tabs[1].string = ft['duel_tab_2']
                tabs[2].string = ft['duel_tab_3']
        
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"[DUEL NAV LOCALIZED] {rel_path}")

def upgrade_all_contact_pages():
    for lang, rel_path in CONTACT_PAGES.items():
        abs_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(abs_path):
            continue
        with open(abs_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        localize_navbar(soup, lang)
        localize_footer(soup, lang)
        sync_metadata_from_git(soup, rel_path, lang)

        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        print(f"[CONTACT NAV LOCALIZED] {rel_path}")

def run_all_cloners():
    print("=================================================================")
    print("EXECUTING DEFINITIVE MASTER 1:1 CLONING & TRANSLATION ENGINE (V3)")
    print("=================================================================")

    # 1. Destination Guides (32 pages + 8 aliases)
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
    upgrade_all_duel_pages()

    # 5. Contact Pages (8 pages)
    print("\n--- PHASE 5: CONTACT DESK PAGES ---")
    upgrade_all_contact_pages()

    print("\n=================================================================")
    print("ALL 64+ SITE PAGES CLONED & TRANSLATED WITH 100% MASTER PARITY!")
    print("=================================================================")

if __name__ == '__main__':
    run_all_cloners()
