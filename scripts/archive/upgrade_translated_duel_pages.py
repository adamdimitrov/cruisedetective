#!/usr/bin/env python3
"""
DUEL SHOWDOWN UPGRADE ENGINE (V2 PERFECTED) — THE CRUISE DETECTIVE
Injects the perfected luxury 2-column head-to-head showdown card deck (.ltt-duel-grid),
photo media, verified spec pills (.ltt-duel-spec-pill), best-for highlights (.ltt-duel-bestfor),
score badges, central VS badge, and 9999px gold pill buttons into all 8 translated duel pages.
"""

import os
import re

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

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

DUEL_I18N = {
    'fr': {
        'deck_header': 'Face-à-Face en Direct : Mouches vs. Parisiens',
        'deck_subtitle': 'Les deux croisières les plus emblématiques de Paris comparées sur la nourriture, le placement et l\'ambiance.',
        'c1_tag': 'CANDIDAT A • 🏆 #1 MEILLEURE CUISINE & ROMANTISME',
        'c1_title': '1. Dîner-croisière Bateaux Mouches',
        'c1_kicker': 'Compagnie des Bateaux Mouches • ⏱️ 2h15 • 📍 Pont de l\'Alma',
        'c1_dep': '20h30 (Embarquement 19h45)',
        'c1_dur': '2h15 sur la Seine',
        'c1_price': 'À partir de 115 €',
        'c1_music': 'Duo Violon & Piano',
        'c1_seat': 'Table fenêtre ou centre',
        'c1_best': 'Couples recherchant une gastronomie raffinée et une ambiance romantique au violon.',
        'c1_btn': 'Réserver sur Tiqets (115 €) →',
        'c1_guar': '⚡ QR code instantané • 🛡️ Annulation gratuite 24h',
        'c2_tag': 'CANDIDAT B • 🗼 #2 MEILLEUR BATEAU ENTIÈREMENT VITRÉ',
        'c2_title': '2. Dîner-croisière Bateaux Parisiens',
        'c2_kicker': 'Bateaux Parisiens • ⏱️ 2h30 • 📍 Port de la Bourdonnais (Tour Eiffel)',
        'c2_dep': '20h30 (Embarquement 19h45)',
        'c2_dur': '2h30 sur la Seine',
        'c2_price': 'À partir de 115 €',
        'c2_music': 'Chanteuse & Orchestre',
        'c2_seat': 'Verrière panoramique 360°',
        'c2_best': 'Vue directe sur la tour Eiffel scintillante et ambiance festive avec chanteuse live.',
        'c2_btn': 'Réserver sur Tiqets (115 €) →',
        'c2_guar': '⚡ QR code instantané • 🛡️ Annulation gratuite 24h',
        'lbl_best': 'Idéal pour'
    },
    'de': {
        'deck_header': 'Direkter Schiffsvergleich: Mouches vs. Parisiens',
        'deck_subtitle': 'Die beiden bekanntesten Schiffe im direkten Vergleich bei Menüqualität, Tischen und Aussicht.',
        'c1_tag': 'KANDIDAT A • 🏆 #1 BESTES ESSEN & ROMANTIK',
        'c1_title': '1. Bateaux Mouches Dinner-Kreuzfahrt',
        'c1_kicker': 'Compagnie des Bateaux Mouches • ⏱️ 2h15m • 📍 Pont de l\'Alma Anleger',
        'c1_dep': '20:30 Uhr (Boarding 19:45)',
        'c1_dur': '2h 15m Fahrzeit',
        'c1_price': 'Ab 115 €',
        'c1_music': 'Violine & Klavier Live',
        'c1_seat': 'Fenster- oder Mitteltisch',
        'c1_best': 'Paare, die klassische Pariser Romantik und gehobene französische Küche schätzen.',
        'c1_btn': 'Auf Tiqets buchen (115 €) →',
        'c1_guar': '⚡ Sofortiges Smartphone-Ticket • 🛡️ Kostenlose Stornierung bis 24h',
        'c2_tag': 'KANDIDAT B • 🗼 #2 BESTES MODERNES GLAS-SCHIFF',
        'c2_title': '2. Bateaux Parisiens Dinner-Kreuzfahrt',
        'c2_kicker': 'Bateaux Parisiens • ⏱️ 2h30m • 📍 Eiffelturm Pier 5/7',
        'c2_dep': '20:30 Uhr (Boarding 19:45)',
        'c2_dur': '2h 30m Fahrzeit',
        'c2_price': 'Ab 115 €',
        'c2_music': 'Live-Sängerin & Band',
        'c2_seat': '360° Panoramaglas-Salon',
        'c2_best': 'Perfekter Blick auf den glitzernden Eiffelturm und lebendige Live-Musik.',
        'c2_btn': 'Auf Tiqets buchen (115 €) →',
        'c2_guar': '⚡ Sofortiges Smartphone-Ticket • 🛡️ Kostenlose Stornierung bis 24h',
        'lbl_best': 'Ideal für'
    },
    'es': {
        'deck_header': 'Cara a Cara: Mouches vs. Parisiens',
        'deck_subtitle': 'Los dos cruceros con cena más famosos de París comparados en menú, ubicación y vistas.',
        'c1_tag': 'CANDIDATO A • 🏆 #1 MEJOR GASTRONOMÍA Y ROMANCE',
        'c1_title': '1. Crucero con Cena Bateaux Mouches',
        'c1_kicker': 'Compagnie des Bateaux Mouches • ⏱️ 2h15m • 📍 Muelle Pont de l\'Alma',
        'c1_dep': '20:30 (Embarque 19:45)',
        'c1_dur': '2h 15m de recorrido',
        'c1_price': 'Desde 115 €',
        'c1_music': 'Dúo Violín y Piano',
        'c1_seat': 'Mesa ventana o centro',
        'c1_best': 'Parejas que buscan romanticismo clásico parisino y excelente gastronomía francesa.',
        'c1_btn': 'Reservar en Tiqets (115 €) →',
        'c1_guar': '⚡ Código QR al instante • 🛡️ Cancelación gratuita 24h',
        'c2_tag': 'CANDIDATO B • 🗼 #2 MEJOR BARCO DE CRISTAL PANORÁMICO',
        'c2_title': '2. Crucero con Cena Bateaux Parisiens',
        'c2_kicker': 'Bateaux Parisiens • ⏱️ 2h30m • 📍 Muelle Torre Eiffel Pier 5/7',
        'c2_dep': '20:30 (Embarque 19:45)',
        'c2_dur': '2h 30m de recorrido',
        'c2_price': 'Desde 115 €',
        'c2_music': 'Cantante y Banda en vivo',
        'c2_seat': 'Salón de cristal 360°',
        'c2_best': 'Vistas espectaculares de la Torre Eiffel iluminada y ambiente contemporáneo.',
        'c2_btn': 'Reservar en Tiqets (115 €) →',
        'c2_guar': '⚡ Código QR al instante • 🛡️ Cancelación gratuita 24h',
        'lbl_best': 'Ideal para'
    },
    'it': {
        'deck_header': 'Confronto Diretto: Mouches vs. Parisiens',
        'deck_subtitle': 'Le due crociere con cena più celebri di Parigi esaminate su cucina, tavoli e vista panoramica.',
        'c1_tag': 'CANDIDATO A • 🏆 #1 MIGLIOR CUCINA E ROMANTICISMO',
        'c1_title': '1. Crociera con Cena Bateaux Mouches',
        'c1_kicker': 'Compagnie des Bateaux Mouches • ⏱️ 2h15m • 📍 Molo Pont de l\'Alma',
        'c1_dep': '20:30 (Imbarco 19:45)',
        'c1_dur': '2h 15m di navigazione',
        'c1_price': 'Da 115 €',
        'c1_music': 'Violino e Pianoforte live',
        'c1_seat': 'Tavolo a vetrata o centro',
        'c1_best': 'Coppie in cerca di un\'atmosfera intima, cucina francese curata e violino dal vivo.',
        'c1_btn': 'Prenota su Tiqets (115 €) →',
        'c1_guar': '⚡ Biglietto QR immediato • 🛡️ Cancellazione gratuita 24h',
        'c2_tag': 'CANDIDATO B • 🗼 #2 MIGLIOR BATTELLO PANORAMICO IN VETRO',
        'c2_title': '2. Crociera con Cena Bateaux Parisiens',
        'c2_kicker': 'Bateaux Parisiens • ⏱️ 2h30m • 📍 Molo Torre Eiffel Pier 5/7',
        'c2_dep': '20:30 (Imbarco 19:45)',
        'c2_dur': '2h 30m di navigazione',
        'c2_price': 'Da 115 €',
        'c2_music': 'Cantante live ed Orchestra',
        'c2_seat': 'Vetrata panoramica 360°',
        'c2_best': 'Visuale perfetta sulla Torre Eiffel illuminata e serata con musica coinvolgente.',
        'c2_btn': 'Prenota su Tiqets (115 €) →',
        'c2_guar': '⚡ Biglietto QR immediato • 🛡️ Cancellazione gratuita 24h',
        'lbl_best': 'Ideale per'
    },
    'ja': {
        'deck_header': '2大人気船の徹底対決：バトー・ムーシュ vs バトー・パリジャン',
        'deck_subtitle': 'パリで最も知名度の高い2大ディナークルーズを、料理の質、座席配置、夜景の見え方で直接比較。',
        'c1_tag': '候補 A • 🏆 #1 最高峰の料理とロマンチックな雰囲気',
        'c1_title': '1. バトー・ムーシュ ディナークルーズ',
        'c1_kicker': 'Compagnie des Bateaux Mouches • ⏱️ 2時間15分 • 📍 アルマ橋乗り場',
        'c1_dep': '20:30出航（乗船 19:45〜）',
        'c1_dur': '2時間15分の運航',
        'c1_price': '115 €〜',
        'c1_music': 'バイオリン＆ピアノ生演奏',
        'c1_seat': '窓際・中央席プランあり',
        'c1_best': '本格的なフランス料理コースと、バイオリンの調べに包まれる王道のロマンチックディナー。',
        'c1_btn': 'Tiqetsで予約（115 €）→',
        'c1_guar': '⚡ 即時QRチケット発行 • 🛡️ 24時間前までキャンセル無料',
        'c2_tag': '候補 B • 🗼 #2 360度全面ガラス張りのモダン大型船',
        'c2_title': '2. バトー・パリジャン ディナークルーズ',
        'c2_kicker': 'Bateaux Parisiens • ⏱️ 2時間30分 • 📍 エッフェル塔乗り場 Pier 5/7',
        'c2_dep': '20:30出航（乗船 19:45〜）',
        'c2_dur': '2時間30分の運航',
        'c2_price': '115 €〜',
        'c2_music': '生バンド＆ボーカル',
        'c2_seat': '360°全面ガラス張り',
        'c2_best': '輝くエッフェル塔を間近に臨む大パノラマと、活気あふれる華やかなディナー。',
        'c2_btn': 'Tiqetsで予約（115 €）→',
        'c2_guar': '⚡ 即時QRチケット発行 • 🛡️ 24時間前までキャンセル無料',
        'lbl_best': 'おすすめ'
    },
    'nl': {
        'deck_header': 'Zij-aan-Zij Vergelijking: Mouches vs. Parisiens',
        'deck_subtitle': 'De twee meest geboekte dinercruises van Parijs vergeleken op eten, tafelkeuze en uitzicht.',
        'c1_tag': 'KANDIDAAT A • 🏆 #1 BESTE DINER & ROMANTIEK',
        'c1_title': '1. Bateaux Mouches Dinercruise',
        'c1_kicker': 'Compagnie des Bateaux Mouches • ⏱️ 2u15m • 📍 Pont de l\'Alma Pier',
        'c1_dep': '20:30 (Inschepen 19:45)',
        'c1_dur': '2u 15m vaartijd',
        'c1_price': 'Vanaf €115',
        'c1_music': 'Viool & Piano live',
        'c1_seat': 'Raam- of middentafel',
        'c1_best': 'Stellen die houden van traditionele Parijse romantiek en verfijnde Franse gastronomie.',
        'c1_btn': 'Boek op Tiqets (€115) →',
        'c1_guar': '⚡ Direct smartphone-ticket • 🛡️ Gratis annuleren tot 24u',
        'c2_tag': 'KANDIDAAT B • 🗼 #2 BESTE MODERNE GLAZEN BOOT',
        'c2_title': '2. Bateaux Parisiens Dinercruise',
        'c2_kicker': 'Bateaux Parisiens • ⏱️ 2u30m • 📍 Eiffeltoren Pier 5/7',
        'c2_dep': '20:30 (Inschepen 19:45)',
        'c2_dur': '2u 30m vaartijd',
        'c2_price': 'Vanaf €115',
        'c2_music': 'Zangeres & Live Band',
        'c2_seat': '360° Panoramaglas',
        'c2_best': 'Adembenemend zicht op de Eiffeltoren en een feestelijke eigentijdse ambiance.',
        'c2_btn': 'Boek op Tiqets (€115) →',
        'c2_guar': '⚡ Direct smartphone-ticket • 🛡️ Gratis annuleren tot 24u',
        'lbl_best': 'Ideaal voor'
    },
    'pl': {
        'deck_header': 'Bezpośrednie Porównanie: Mouches vs. Parisiens',
        'deck_subtitle': 'Dwa najpopularniejsze rejsy z kolacją w Paryżu ocenione pod kątem kuchni, stolików i widoków.',
        'c1_tag': 'KANDYDAT A • 🏆 #1 NAJLEPSZA KUCHNIA I ROMANTYZM',
        'c1_title': '1. Rejs z kolacją Bateaux Mouches',
        'c1_kicker': 'Compagnie des Bateaux Mouches • ⏱️ 2h15m • 📍 Przystań Pont de l\'Alma',
        'c1_dep': '20:30 (Wejście na pokład 19:45)',
        'c1_dur': '2h 15m rejsu',
        'c1_price': 'Od 115 €',
        'c1_music': 'Skrzypce i Fortepian',
        'c1_seat': 'Stolik przy oknie lub na środku',
        'c1_best': 'Pary szukające klasycznego paryskiego romantyzmu i wykwintnej kuchni francuskiej.',
        'c1_btn': 'Zarezerwuj na Tiqets (115 €) →',
        'c1_guar': '⚡ Natychmiastowy kod QR • 🛡️ Bezpłatne odwołanie do 24h',
        'c2_tag': 'KANDYDAT B • 🗼 #2 NAJLEPSZY PRZESZKLONY STATEK',
        'c2_title': '2. Rejs z kolacją Bateaux Parisiens',
        'c2_kicker': 'Bateaux Parisiens • ⏱️ 2h30m • 📍 Przystań pod Wieżą Eiffla Pier 5/7',
        'c2_dep': '20:30 (Wejście na pokład 19:45)',
        'c2_dur': '2h 30m rejsu',
        'c2_price': 'Od 115 €',
        'c2_music': 'Wokalistka i Zespół live',
        'c2_seat': 'Szklana kopuła 360°',
        'c2_best': 'Widok z bliska na mieniącą się Wieżę Eiffla i nowoczesna atmosfera z muzyką.',
        'c2_btn': 'Zarezerwuj na Tiqets (115 €) →',
        'c2_guar': '⚡ Natychmiastowy kod QR • 🛡️ Bezpłatne odwołanie do 24h',
        'lbl_best': 'Idealne dla'
    },
    'ro': {
        'deck_header': 'Comparație Directă: Mouches vs. Parisiens',
        'deck_subtitle': 'Cele mai renumite două vase din Paris evaluate pe mâncare, poziționare și atmosferă.',
        'c1_tag': 'CANDIDAT A • 🏆 #1 CEA MAI BUNĂ MÂNCARE & ROMANTISM',
        'c1_title': '1. Croazieră cu cină Bateaux Mouches',
        'c1_kicker': 'Compagnie des Bateaux Mouches • ⏱️ 2h15m • 📍 Pontonul Pont de l\'Alma',
        'c1_dep': '20:30 (Îmbarcare 19:45)',
        'c1_dur': '2h 15m croazieră',
        'c1_price': 'De la 115 €',
        'c1_music': 'Vioară și Pian live',
        'c1_seat': 'Masă la fereastră sau centrală',
        'c1_best': 'Cupluri care caută romantism clasic parizian și preparate culinare franțuzești de top.',
        'c1_btn': 'Rezervă pe Tiqets (115 €) →',
        'c1_guar': '⚡ Bilet QR instant pe telefon • 🛡️ Anulare gratuită cu 24h înainte',
        'c2_tag': 'CANDIDAT B • 🗼 #2 CEL MAI BUN VAS MODERN PANORAMIC',
        'c2_title': '2. Croazieră cu cină Bateaux Parisiens',
        'c2_kicker': 'Bateaux Parisiens • ⏱️ 2h30m • 📍 Pontonul Turnul Eiffel Pier 5/7',
        'c2_dep': '20:30 (Îmbarcare 19:45)',
        'c2_dur': '2h 30m croazieră',
        'c2_price': 'De la 115 €',
        'c2_music': 'Cântăreață și Trupă live',
        'c2_seat': 'Pereți din sticlă 360°',
        'c2_best': 'Priveliști panoramice uluitoare asupra Turnului Eiffel și o atmosferă dinamică.',
        'c2_btn': 'Rezervă pe Tiqets (115 €) →',
        'c2_guar': '⚡ Bilet QR instant pe telefon • 🛡️ Anulare gratuită cu 24h înainte',
        'lbl_best': 'Ideal pentru'
    }
}

def build_duel_deck_html(lang):
    d = DUEL_I18N[lang]
    tiqets_mouches = "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-on-the-seine-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=vs-deck-mouches"
    tiqets_parisiens = "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-on-the-seine-river-bateaux-parisiens-p974358/?partner=thecruisedetective.com-176436&tq_campaign=vs-deck-parisiens"

    return f'''
<div class="ltt-deck-container" id="bm-vs-bp-comparison-deck" style="margin: 36px auto !important;">
  <div class="ltt-header-box" style="margin-bottom: 24px; text-align: center;">
    <span class="ltt-kicker-tag" style="color: #dfa732; font-weight: 800; letter-spacing: 0.1em;">HEAD-TO-HEAD SHOWDOWN</span>
    <h2 class="ltt-header-title" style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 28px; font-weight: 800; color: #0f172a; margin: 8px 0 10px 0;">{d['deck_header']}</h2>
    <p style="font-size: 15px; color: #64748b; margin: 0 auto; max-width: 680px;">{d['deck_subtitle']}</p>
  </div>

  <div class="ltt-duel-grid" id="ltt-cards-deck">
    <!-- CONTENDER 1: MOUCHES -->
    <div class="bpa-card ltt-duel-card" data-cat="mouches" id="duel-card-1">
      <div class="ltt-duel-card-header">
        <span class="ltt-duel-contender-tag" style="background:#0a192f; color:#fef08a;">{d['c1_tag']}</span>
        <h3 class="ltt-duel-card-title"><a class="bpa-title" href="{tiqets_mouches}" rel="noopener" target="_blank">{d['c1_title']}</a></h3>
        <div class="ltt-duel-card-kicker">{d['c1_kicker']}</div>
      </div>
      <div class="ltt-duel-media">
        <img alt="{d['c1_title']}" fetchpriority="high" loading="eager" sizes="(max-width: 767px) 420px, 50vw" src="/assets/cdn/652d0405192ba076b04f74a3/6557d7488c95f4ddb81c828e_Bateaux-mouches-dinner-cruise%20(15).webp" style="width:100%; height:100%; object-fit:cover;"/>
      </div>
      <div class="ltt-duel-body">
        <div class="ltt-duel-specs-grid">
          <span class="ltt-duel-spec-pill">⏱️ {d['c1_dur']}</span>
          <span class="ltt-duel-spec-pill">🍽️ {d['c1_seat']}</span>
          <span class="ltt-duel-spec-pill">🎻 {d['c1_music']}</span>
          <span class="ltt-duel-spec-pill">📍 Pont de l'Alma</span>
        </div>
        <div class="ltt-duel-bestfor">
          <strong>🎯 {d['lbl_best']}:</strong> {d['c1_best']}
        </div>
      </div>
      <div class="ltt-duel-footer">
        <div class="ltt-duel-price-wrap">
          <span class="ltt-duel-price">{d['c1_price']}</span>
          <span class="ltt-duel-price-sub">{d['c1_dep']}</span>
        </div>
        <a class="ltt-duel-cta-btn" href="{tiqets_mouches}" rel="noopener sponsored" target="_blank">{d['c1_btn']}</a>
        <div class="ltt-duel-guarantee">{d['c1_guar']}</div>
      </div>
    </div>

    <!-- CENTRAL VS BADGE -->
    <div aria-hidden="true" class="ltt-duel-vs-badge">VS</div>

    <!-- CONTENDER 2: PARISIENS -->
    <div class="bpa-card ltt-duel-card" data-cat="parisiens" id="duel-card-2">
      <div class="ltt-duel-card-header">
        <span class="ltt-duel-contender-tag" style="background:#0a192f; color:#93c5fd;">{d['c2_tag']}</span>
        <h3 class="ltt-duel-card-title"><a class="bpa-title" href="{tiqets_parisiens}" rel="noopener" target="_blank">{d['c2_title']}</a></h3>
        <div class="ltt-duel-card-kicker">{d['c2_kicker']}</div>
      </div>
      <div class="ltt-duel-media">
        <img alt="{d['c2_title']}" fetchpriority="high" loading="eager" sizes="(max-width: 767px) 420px, 50vw" src="/assets/cdn/652d0405192ba076b04f74a3/653e67da33c8ccff6d081df9_bateaux-parisiens-dinner-cruise%20(12).webp" style="width:100%; height:100%; object-fit:cover;"/>
      </div>
      <div class="ltt-duel-body">
        <div class="ltt-duel-specs-grid">
          <span class="ltt-duel-spec-pill">⏱️ {d['c2_dur']}</span>
          <span class="ltt-duel-spec-pill">🍽️ {d['c2_seat']}</span>
          <span class="ltt-duel-spec-pill">🎤 {d['c2_music']}</span>
          <span class="ltt-duel-spec-pill">📍 Tour Eiffel Pier 5/7</span>
        </div>
        <div class="ltt-duel-bestfor">
          <strong>🎯 {d['lbl_best']}:</strong> {d['c2_best']}
        </div>
      </div>
      <div class="ltt-duel-footer">
        <div class="ltt-duel-price-wrap">
          <span class="ltt-duel-price">{d['c2_price']}</span>
          <span class="ltt-duel-price-sub">{d['c2_dep']}</span>
        </div>
        <a class="ltt-duel-cta-btn" href="{tiqets_parisiens}" rel="noopener sponsored" target="_blank">{d['c2_btn']}</a>
        <div class="ltt-duel-guarantee">{d['c2_guar']}</div>
      </div>
    </div>
  </div>
</div>
'''

def upgrade_duel_page(lang, rel_path):
    abs_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(abs_path):
        return

    with open(abs_path, 'r', encoding='utf-8') as f:
        html = f.read()

    deck_html = build_duel_deck_html(lang)

    # If already injected, replace the old deck
    if 'id="bm-vs-bp-comparison-deck"' in html:
        pos_deck_start = html.find('<div class="ltt-deck-container" id="bm-vs-bp-comparison-deck"')
        # Find the closing </div></div></div></div> of the deck
        pos_cards_deck = html.find('id="ltt-cards-deck"', pos_deck_start)
        pos_deck_end = html.find('<!-- CONTENDER 2: PARISIENS -->', pos_deck_start)
        if pos_deck_end != -1:
            # find the end of deck container
            pos_real_end = html.find('</div>\n</div>\n</div>', pos_deck_end)
            if pos_real_end != -1:
                html = html[:pos_deck_start] + deck_html + html[pos_real_end+18:]
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"[{lang.upper()}] Replaced and perfected duel deck in: {rel_path}")
                return

    # Otherwise insert fresh
    pos = html.find('class="pricing-comparison-wrap"')
    if pos != -1:
        h2_pos = html.rfind('<h2', 0, pos)
        if h2_pos != -1:
            html = html[:h2_pos] + deck_html + '\n' + html[h2_pos:]
        else:
            html = html[:pos] + deck_html + '\n' + html[pos:]
        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[{lang.upper()}] Injected perfected duel deck in: {rel_path}")

def main():
    for lang, rel_path in DUEL_PAGES.items():
        upgrade_duel_page(lang, rel_path)

if __name__ == '__main__':
    main()
