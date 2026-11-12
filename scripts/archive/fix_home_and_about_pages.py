import os
import re
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

HOMEPAGES = [
    'de/index.html',
    'es/index.html',
    'fr/index.html',
    'it/index.html',
    'ja/index.html',
    'nl/index.html',
    'pl/index.html',
    'ro/index.html'
]

ABOUT_PAGES = {
    'fr': 'fr/a-propos/index.html',
    'de': 'de/uber-uns/index.html',
    'es': 'es/acerca/index.html',
    'it': 'it/su-di-noi/index.html',
    'ja': 'ja/について/index.html',
    'nl': 'nl/over-uns/index.html',
    'pl': 'pl/o/index.html',
    'ro': 'ro/despre/index.html'
}

ETHICS_I18N = {
    'fr': {
        'eyebrow': 'CHARTE ÉTHIQUE & TRANSPARENCE',
        'title': 'Nos 5 Engagements Éditoriaux',
        'subtitle': 'Des normes strictes pour préserver une indépendance totale et la confiance de nos lecteurs.',
        'cards': [
            ('01', '100% Billets Auto-Financés', 'Aucun billet gratuit, repas offert ou surclassement de presse. Nous payons nos places au tarif public.'),
            ('02', 'Anonymat Total à Bord', 'Les équipages ignorent notre présence pour garantir un service standard et authentique.'),
            ('03', 'Transparence d\'Affiliation', 'Nous recommandons le meilleur bateau même quand les commissions sont plus faibles.'),
            ('04', 'Ré-audits Périodiques', 'Nous réévaluons régulièrement les menus et changements de navires à chaque nouvelle saison.'),
            ('05', 'Droit de Réponse & Rectification', 'Si un opérateur améliore sa cuisine ou ses installations, nous le revérifions sur le terrain.')
        ]
    },
    'de': {
        'eyebrow': 'ETHIK-CHARTA & TRANSPARENZ',
        'title': 'Unsere 5 Redaktionellen Grundsätze',
        'subtitle': 'Strenge Standards zur Wahrung vollständiger Unabhängigkeit und des Vertrauens unserer Leser.',
        'cards': [
            ('01', '100% Selbstfinanzierte Tickets', 'Keine Freikarten, gesponserten Mahlzeiten oder Presse-Upgrades. Wir zahlen reguläre Tarife.'),
            ('02', 'Vollständige Anonymität an Bord', 'Die Crews wissen nichts von unserer Anwesenheit, um einen realen Standardservice zu garantieren.'),
            ('03', 'Transparente Partnerschaften', 'Wir empfehlen das beste Schiff, selbst wenn alternative Partner höhere Provisionen bieten.'),
            ('04', 'Regelmäßige Nachprüfungen', 'Wir überprüfen Menüs, Service und Schiffsflotten kontinuierlich bei jeder neuen Saison.'),
            ('05', 'Recht auf Richtigstellung', 'Wenn ein Betreiber Küche oder Ausstattung verbessert, testen wir vor Ort erneut.')
        ]
    },
    'es': {
        'eyebrow': 'CÓDIGO ÉTICO Y TRANSPARENCIA',
        'title': 'Nuestros 5 Compromisos Editoriales',
        'subtitle': 'Normas estrictas para preservar la independencia total y la confianza de nuestros lectores.',
        'cards': [
            ('01', '100% Billetes Autofinanciados', 'Ni entradas gratis, ni comidas patrocinadas ni trato de prensa. Pagamos como cualquier viajero.'),
            ('02', 'Anonimato Total a Bordo', 'Las tripulaciones desconocen nuestra presencia para evaluar el servicio cotidiano real.'),
            ('03', 'Transparencia de Afiliación', 'Recomendamos el mejor barco incluso cuando las comisiones son más bajas.'),
            ('04', 'Reauditorías Periódicas', 'Reevaluamos menús y cambios de embarcación de forma continua cada temporada.'),
            ('05', 'Derecho de Réplica', 'Si un operador renueva su gastronomía o barcos, volvemos a probarlo en persona.')
        ]
    },
    'it': {
        'eyebrow': 'CODICE ETICO E TRASPARENZA',
        'title': 'I Nostri 5 Impegni Editoriali',
        'subtitle': 'Standard rigorosi per garantire totale indipendenza e massima fiducia dei lettori.',
        'cards': [
            ('01', '100% Biglietti Autofinanziati', 'Nessun biglietto omaggio, pasto offerto o invito stampa. Paghiamo di tasca nostra.'),
            ('02', 'Anonimato Totale a Bordo', 'Gli equipaggi ignorano la nostra presenza per verificare il servizio standard autentico.'),
            ('03', 'Trasparenza nelle Affiliazioni', 'Consigliamo l\'imbarcazione migliore anche quando riconosce commissioni inferiori.'),
            ('04', 'Audit Periodici di Controllo', 'Testiamo nuovamente menu e imbarcazioni ad ogni cambio di stagione.'),
            ('05', 'Diritto di Rettifica', 'Se una compagnia migliora la cucina o le navi, torniamo a verificarlo sul campo.')
        ]
    },
    'ja': {
        'eyebrow': '倫理基準と透明性',
        'title': '編集部が約束する5つの原則',
        'subtitle': '完全な独立性と読者からの信頼を守るための厳格な行動規範。',
        'cards': [
            ('01', '100% 自費購入チケット', '招待券、無料試食、プレスの特別扱いは一切辞退し、一般料金を自費で支払います。'),
            ('02', '完全覆面調査', '日常通りの一般サービスを検証するため、取材であることを一切明かさずに乗船します。'),
            ('03', '公正なアフィリエイト情報開示', '手数料の多寡に関わらず、旅行者にとって客観的に最良のクルーズを推奨します。'),
            ('04', '定期的な再調査', 'メニュー改定や運航船の変更に合わせ、シーズンごとに現地調査を更新します。'),
            ('05', '客観的な訂正と再検証', '運航会社が料理や設備を改善した場合、現地で再度覆面調査を実施します。')
        ]
    },
    'nl': {
        'eyebrow': 'ETHIEK & TRANSPARANTIE',
        'title': 'Onze 5 Redactionele Beloften',
        'subtitle': 'Strikte normen om volledige onafhankelijkheid en het vertrouwen van lezers te waarborgen.',
        'cards': [
            ('01', '100% Zelfbetaalde Tickets', 'Geen gratis perskaarten of gesponsorde maaltijden. Wij betalen reguliere tarieven.'),
            ('02', 'Volledige Anonieme Aanwezigheid', 'De bemanning weet niet van onze aanwezigheid om de standaardervaring te toetsen.'),
            ('03', 'Transparante Aanbevelingen', 'Wij bevelen de beste boot aan, ongeacht lagere commissiepercentages.'),
            ('04', 'Periodieke Herbeoordelingen', 'Wij testen menu\'s en scheepswijzigingen regelmatig opnieuw elk seizoen.'),
            ('05', 'Recht op Rectificatie', 'Wanneer een rederij haar keuken of schepen verbetert, controleren wij dat opnieuw.')
        ]
    },
    'pl': {
        'eyebrow': 'KODEKS ETYCZNY I TRANSPARENTNOŚĆ',
        'title': 'Nasze 5 Zasad Redakcyjnych',
        'subtitle': 'Rygorystyczne zasady gwarantujące pełną niezależność i zaufanie czytelników.',
        'cards': [
            ('01', '100% Samodzielnie Opłacone Bilety', 'Zero darmowych wejściówek, posiłków prasowych czy specjalnego traktowania.'),
            ('02', 'Pełna Anonimowość na Pokładzie', 'Załoga nie wie o naszej obecności, dzięki czemu testujemy standardową obsługę.'),
            ('03', 'Uczciwe Linki Partnerskie', 'Rekomendujemy najlepsze rejsy, nawet gdy prowizja partnerska jest niższa.'),
            ('04', 'Regularne Re-Audyty', 'Sezonowo sprawdzamy zmiany w menu, flotę i standardy gastronomiczne.'),
            ('05', 'Prawo do Sprawdzenia Poprawek', 'Gdy armator ulepsza jakość dań lub łodzi, weryfikujemy to osobiście na miejscu.')
        ]
    },
    'ro': {
        'eyebrow': 'COD ETIC ȘI TRANSPARENȚĂ',
        'title': 'Cele 5 Angajamente Editoriale',
        'subtitle': 'Standarde stricte pentru a asigura independența deplină și încrederea cititorilor.',
        'cards': [
            ('01', '100% Bilete Autofinanțate', 'Fără invitații de presă, mese gratuite sau tratament preferențial. Plătim prețul întreg.'),
            ('02', 'Anonimat Total la Bord', 'Echipajul nu știe de prezența noastră, evaluând serviciul oferit oricărui călător.'),
            ('03', 'Transparență în Recomandări', 'Recomandăm cel mai bun vas chiar dacă generează comisioane mai reduse.'),
            ('04', 'Reauditări Periodice', 'Testăm repetat meniurile și renovările de flotă la fiecare sezon.'),
            ('05', 'Verificarea Îmbunătățirilor', 'Dacă o companie își îmbunătățește bucătăria sau navele, reverificăm pe teren.')
        ]
    }
}

VALID_AMSTERDAM_IMG = '/assets/cdn/652d0405192ba076b04f74a3/656b5237222689efacce475b_best-amsterdam-canal-cruises-featured-image.webp'

def fix_homepages():
    for rel_path in HOMEPAGES:
        abs_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(abs_path):
            continue
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Fix broken Amsterdam image
        content = re.sub(
            r'/assets/cdn/652d0405192ba076b04f74a3/655b4f84c8be1a48c66e28d8[^\s"\'>]+',
            VALID_AMSTERDAM_IMG,
            content
        )

        # 2. Ensure webflow shared stylesheet is linked
        if '/css/thecruisedetective-com.webflow.shared.5dcd01391.min.css' not in content:
            content = content.replace(
                '<link rel="stylesheet" href="/css/editorial-luxury.css"/>',
                '<link href="/css/thecruisedetective-com.webflow.shared.5dcd01391.min.css" rel="stylesheet" type="text/css"/>\n  <link rel="stylesheet" href="/css/editorial-luxury.css"/>'
            )

        # 3. Ensure footer is wrapped in footer.footer-dark
        if '<footer class="footer-dark"' not in content and '<div class="footer-section">' in content:
            content = content.replace(
                '<div class="footer-section">',
                '<footer class="footer-dark" role="contentinfo">\n    <div class="footer-section">'
            )
            # Find the closing of footer
            content = re.sub(
                r'(</div>\s*</div>\s*</div>\s*)(<script|\s*</body>)',
                r'\1</footer>\n\2',
                content
            )

        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[HOMEPAGE FIXED] {rel_path}")

def fix_about_pages():
    for lang, rel_path in ABOUT_PAGES.items():
        abs_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(abs_path):
            continue
        with open(abs_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Ensure webflow shared stylesheet is linked
        if '/css/thecruisedetective-com.webflow.shared.5dcd01391.min.css' not in content:
            content = content.replace(
                '<link href="/css/editorial-luxury.css" rel="stylesheet"/>',
                '<link href="/css/thecruisedetective-com.webflow.shared.5dcd01391.min.css" rel="stylesheet" type="text/css"/>\n<link href="/css/editorial-luxury.css" rel="stylesheet"/>'
            )

        # 2. Replace ethics section with canonical dark luxury grid
        info = ETHICS_I18N[lang]
        cards_html = []
        for num, title, desc in info['cards']:
            cards_html.append(f'''
        <div class="ltt-ethics-card">
          <div class="ltt-ethics-num">{num}</div>
          <h3 style="color:#ffffff !important; font-size:18px; font-weight:800; margin:0 0 8px 0;">{title}</h3>
          <p style="color:#cbd5e1; font-size:13.5px; line-height:1.6; margin:0;">{desc}</p>
        </div>''')

        new_ethics_section = f'''  <!-- SECTION 3: ETHICS POLICY -->
  <section class="ltt-section ltt-ethics-section" id="methodology" style="background: #0f172a !important; color: #ffffff !important; padding: 72px 20px;">
    <div style="max-width: 1180px; margin: 0 auto;">
      <div class="ltt-section-header" style="text-align: center; max-width: 760px; margin: 0 auto 48px auto;">
        <div class="ltt-section-eyebrow" style="background: rgba(217, 119, 6, 0.2); color: #dfa732; padding: 6px 14px; border-radius: 9999px; font-weight: 800; letter-spacing: 0.1em; display: inline-block; margin-bottom: 12px;">{info['eyebrow']}</div>
        <h2 class="ltt-section-title" style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 32px; font-weight: 800; color: #ffffff !important; margin: 0 0 12px 0;">{info['title']}</h2>
        <p class="ltt-section-subtitle" style="font-size: 16px; color: #cbd5e1 !important; line-height: 1.6; margin: 0;">{info['subtitle']}</p>
      </div>

      <div class="ltt-ethics-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px;">
        {''.join(cards_html)}
      </div>
    </div>
  </section>'''

        content = re.sub(
            r'<!-- SECTION 3: ETHICS POLICY -->\s*<section class="ltt-section ltt-ethics-section".*?</section>',
            new_ethics_section,
            content,
            flags=re.DOTALL
        )

        # 3. Ensure footer is wrapped in footer.footer-dark
        if '<footer class="footer-dark"' not in content and '<div class="footer-section">' in content:
            content = content.replace(
                '<div class="footer-section">',
                '<footer class="footer-dark" role="contentinfo">\n<div class="footer-section">'
            )
            content = re.sub(
                r'(</div>\s*</div>\s*</div>\s*)(<script|\s*</body>)',
                r'\1</footer>\n\2',
                content
            )

        with open(abs_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"[ABOUT PAGE FIXED] {rel_path}")

if __name__ == '__main__':
    fix_homepages()
    fix_about_pages()
