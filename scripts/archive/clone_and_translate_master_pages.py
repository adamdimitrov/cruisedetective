#!/usr/bin/env python3
"""
MASTER 1:1 TEMPLATE CLONING & TRANSLATION PIPELINE
Clones the exact English Luxury Travel Tester master pages:
- dinner-cruises-paris/index.html
- seine-river-cruises-paris/index.html
- canal-cruises-amsterdam/index.html
- thames-river-cruises-london/index.html

Preserves 100% of the DOM architecture, classes, bento accordions, filmstrips, video embeds,
Google Maps embeds, and pill button geometry, while injecting authentic translated copy
across all 8 languages: fr, de, es, it, ja, nl, pl, ro.
"""

import os
import re
import sys
import copy
import json
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
        'best_for': 'おすすめの対象:',
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
        'best_for': 'Ideaal voor:',
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
        'best_for': 'Idealne dla:',
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
        'best_for': 'Ideal pentru:',
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

def extract_original_translated_data(rel_path):
    """Extract authentic translated copy from commit 0e6ce9a~1"""
    try:
        raw_html = subprocess.check_output(
            ['git', '-C', BASE_DIR, 'show', f'0e6ce9a~1:{rel_path}'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Warning: git show failed for {rel_path}: {e}")
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

    # 2. Table rows (10 items)
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
            if any(char.isdigit() for char in txt) and ('€' in txt or '£' in txt or 'ユーロ' in txt or 'zł' in txt or 'lei' in txt) and not p_text:
                p_text = txt.replace('ⓘ', '').strip()
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

        # Paragraphs & Tasting notes
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

    # 4. Intro article (before item 1)
    blog = soup.find(class_='blog-section') or soup.find(class_='blog-section-2')
    intro_article_html = ""
    if blog:
        cr = blog.find(class_='content-right_blog')
        if cr:
            first_block = cr.find(class_='w-layout-blockcontainer') or cr.find(class_='w-richtext')
            if first_block and not first_block.find(class_='heading-33'):
                intro_article_html = str(first_block)

    return {
        'h1_text': h1_text,
        'lead_copy_html': lead_copy_html,
        'deck_rows': deck_rows,
        'reviews': reviews_data,
        'intro_article_html': intro_article_html
    }

def clone_and_translate_page(dest_key, lang, target_rel_path):
    dest_cfg = DEST_CONFIGS[dest_key]
    en_path = os.path.join(BASE_DIR, dest_cfg['en_path'])
    target_abs = os.path.join(BASE_DIR, target_rel_path)

    print(f"\n[CLONING MASTER 1:1] [{dest_key.upper()}] [{lang.upper()}]: {target_rel_path} ...")
    
    with open(en_path, 'r', encoding='utf-8') as f:
        en_soup = BeautifulSoup(f.read(), 'html.parser')

    # Deep copy the exact English soup
    master_soup = copy.deepcopy(en_soup)
    t = COMMON_I18N[lang]

    # Fetch original translated copy
    tr_data = extract_original_translated_data(target_rel_path)

    # 1. Update HTML lang
    html_tag = master_soup.find('html')
    if html_tag:
        html_tag['lang'] = lang

    # 2. Update Head metadata
    head = master_soup.find('head')
    if head:
        canon_url = f"https://www.thecruisedetective.com/{target_rel_path.replace('/index.html', '')}"
        canon_tag = head.find('link', rel='canonical')
        if canon_tag:
            canon_tag['href'] = canon_url

    # 3. Update Hero clean card
    hero = master_soup.find(class_='ltt-clean-card') or master_soup.find(class_='ltt-hero-wrap')
    if hero:
        # Breadcrumbs
        bc_home = hero.find(class_='ltt-breadcrumbs')
        if bc_home:
            a_home = bc_home.find('a')
            if a_home:
                a_home['href'] = f"/{lang}/"
                a_home.string = t['bc_home']
            curr_bc = bc_home.find(class_='ltt-bc-current')
            if curr_bc and tr_data['h1_text']:
                curr_bc.string = tr_data['h1_text']

        # Kicker
        kicker = hero.find(class_='ltt-hero-kicker-badge')
        if kicker:
            kicker.string = t['kicker']

        # H1
        h1 = hero.find('h1')
        if h1 and tr_data['h1_text']:
            h1.string = tr_data['h1_text']

        # Author cluster
        author_line = hero.find(class_='ltt-author-line')
        if author_line:
            author_line.clear()
            author_line.append(BeautifulSoup(t['author_line'], 'html.parser'))
        author_role = hero.find(class_='ltt-author-role')
        if author_role:
            author_role.string = t['author_role']
        trust_pill = hero.find(class_='ltt-trust-pill')
        if trust_pill:
            trust_pill.string = t['updated']

        # Lead copy
        if tr_data['lead_copy_html']:
            lead_div = hero.find(class_='ltt-lead-copy')
            if lead_div:
                lead_div.clear()
                lead_div.append(BeautifulSoup(tr_data['lead_copy_html'], 'html.parser'))

        # Filter label
        fl = hero.find(class_='ltt-filter-label')
        if fl:
            fl.string = t['filter_label']

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

            # Price
            if row.get('price'):
                p_tag = card.find(class_='bpa-price')
                if p_tag:
                    p_tag.string = row['price']

            # Sub text & CTA
            psub = card.find(class_='bpa-psub')
            if psub:
                psub.string = t['per_person']
            btn = card.find(class_='bpa-btn')
            if btn:
                btn.string = t['btn_check']
            tm = card.find(class_='bpa-trust-micro')
            if tm:
                tm.string = t['trust_micro']
            sublink = card.find(class_='bpa-sublink')
            if sublink:
                sublink.string = t['read_review']

    # 5. Update Breakdown top bar
    bd_h2 = master_soup.find(class_='bpa-breakdown-heading')
    bd_title = dest_cfg['breakdown_title'].get(lang, dest_cfg['breakdown_title']['fr'])
    if bd_h2:
        bd_h2.string = bd_title

    # 6. Update In-Depth Review Cards (details.bpa-details-card)
    review_cards = master_soup.find_all('details', class_='bpa-details-card')
    for idx, rcard in enumerate(review_cards):
        rev = tr_data['reviews'][idx] if idx < len(tr_data['reviews']) else {}
        row = tr_data['deck_rows'][idx] if idx < len(tr_data['deck_rows']) else {}
        card_title = short_titles[idx] if idx < len(short_titles) else rev.get('clean_title', '')

        # Summary title
        stitle = rcard.find(class_='bpa-details-title')
        if stitle and card_title:
            stitle.string = card_title

        # Pros & Cons
        pro_con_wrap = rcard.find(class_='pro-con-box-wrapper')
        if pro_con_wrap:
            pro_title = pro_con_wrap.find(class_='pro-con-title', style=lambda s: s and '#166534' in s) or pro_con_wrap.find(class_='pro-con-title')
            if pro_title:
                pro_title.string = t['pros_title']
            con_title = pro_con_wrap.find(class_='pro-con-title', style=lambda s: s and '#991b1b' in s)
            if con_title:
                con_title.string = t['cons_title']

            # If translated pros/cons available, update list items
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

        # Bento groups summaries
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
                elif 'Map' in orig_btitle:
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
            if row.get('price'):
                p_disp = buy_card.find('div', style=lambda s: s and 'font-size: 20px' in s)
                if p_disp:
                    p_disp.string = row['price']
            bbtn = buy_card.find('a', class_='bpa-btn')
            if bbtn:
                bbtn.string = t['btn_check']

    # 7. Update Sticky Bar
    sticky = master_soup.find(id='sticky-bar') or master_soup.find(class_='hybrid-sticky-bar')
    if sticky:
        stitle = sticky.find(class_='hybrid-sticky-title') or sticky.find(class_='hybrid-active-title')
        if stitle and short_titles:
            stitle.string = short_titles[0]
        sbtn = sticky.find(class_='hybrid-sticky-btn') or sticky.find(class_='hybrid-cta-btn')
        if sbtn:
            sbtn.string = t['btn_check']

    # 8. Update window.LTT_PAGE_CONFIG script
    toc_deck = dest_cfg['toc_deck_label'].get(lang, dest_cfg['toc_deck_label']['fr'])
    script_cfg = master_soup.find(lambda e: e.name == 'script' and 'window.LTT_PAGE_CONFIG' in (e.string or ''))
    cfg_obj = {
        "deckId": dest_cfg['deck_id'],
        "tocDeckLabel": toc_deck,
        "tocBreakdownLabel": bd_title,
        "shortTitles": short_titles
    }
    cfg_code = f"window.LTT_PAGE_CONFIG = {json.dumps(cfg_obj, ensure_ascii=False)};"
    if script_cfg:
        script_cfg.string = cfg_code
    else:
        new_script = master_soup.new_tag('script')
        new_script.string = cfg_code
        master_soup.body.append(new_script)

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

def main():
    for dest_key in ['dinner', 'sightseeing', 'amsterdam', 'london']:
        cfg = DEST_CONFIGS[dest_key]
        for lang in LANGS:
            target_rel = cfg['pages'][lang]
            clone_and_translate_page(dest_key, lang, target_rel)

if __name__ == '__main__':
    main()
