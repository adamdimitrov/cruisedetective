#!/usr/bin/env python3
"""
CONTACT DESK UPGRADE ENGINE — THE CRUISE DETECTIVE
Upgrades all 8 translated contact pages with:
- Luxury form-section-touch styling
- Yellow spam-defense advisory callout
- Form targeting adam.dimitrov.business@gmail.com with honeypot & interactive captcha
- 9999px gold pill submit button
"""

import os
import re
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

CONTACT_PAGES = {
    'fr': 'fr/contact/index.html',
    'de': 'de/kontakt/index.html',
    'es': 'es/contacto/index.html',
    'it': 'it/contatto/index.html',
    'ja': 'ja/接触/index.html',
    'nl': 'nl/contact/index.html',
    'pl': 'pl/kontakt/index.html',
    'ro': 'ro/contact/index.html'
}

CONTACT_I18N = {
    'fr': {
        'eyebrow': 'BUREAU ÉDITORIAL',
        'title': 'Contactez notre Rédaction',
        'badge': '⚠️ À lire avant de nous envoyer un e-mail !',
        'warning': '<strong>Nous ne répondons à aucune sollicitation de services ou de produits non demandés</strong> (SEO, achat de liens, articles sponsorisés, agences marketing, etc.). Tout spam sera supprimé automatiquement sans réponse.',
        'lead': 'Besoin d\'entrer en contact avec notre bureau éditorial ou de partager vos retours d\'expérience sur une croisière ? Remplissez simplement le formulaire ci-dessous et nous vous répondrons dans les plus brefs délais.<br/><br/>Si vous avez vécu une expérience qui ne correspond pas à nos rapports sur le terrain, ou si vous souhaitez nous envoyer des photos ou factures anonymes, nous sommes toujours à votre écoute.',
        'lbl_name': 'Votre Nom *', 'ph_name': 'ex. Julie Martin',
        'lbl_email': 'Votre E-mail *', 'ph_email': 'ex. julie@exemple.fr',
        'lbl_topic': 'Sujet / Fleuve concerné',
        'lbl_msg': 'Votre Message *', 'ph_msg': 'Détails, date de la croisière, nom de la compagnie ou votre question...',
        'captcha_title': 'Contrôle de Sécurité Anti-Spam',
        'captcha_hint': 'Veuillez résoudre :',
        'captcha_err': 'Réponse incorrecte. Veuillez résoudre le calcul pour envoyer.',
        'btn': 'ENVOYER LE MESSAGE →',
        'opt1': 'Paris Promenade sur la Seine', 'opt2': 'Paris Dîners-Croisières sur la Seine',
        'opt3': 'Amsterdam Canaux', 'opt4': 'Londres Tamise',
        'opt5': 'Retour d\'expérience / Photo / Reçu', 'opt6': 'Question éditoriale générale'
    },
    'de': {
        'eyebrow': 'REDAKTIONSBÜRO',
        'title': 'Kontaktieren Sie unsere Redaktion',
        'badge': '⚠️ Bitte vor dem Schreiben lesen!',
        'warning': '<strong>Wir reagieren nicht auf unaufgeforderte Dienstleistungsangebote</strong> (SEO, Linkaufbau, Gastbeiträge, Marketing-Agenturen usw.). Sämtlicher Spam wird automatisch und kommentarlos gelöscht.',
        'lead': 'Möchten Sie mit unserer Redaktion Kontakt aufnehmen oder Feedback zu einer Schifffahrt einreichen? Füllen Sie einfach das folgende Formular aus – wir antworten so schnell wie möglich.<br/><br/>Wenn Sie eine Fahrt erlebt haben, die nicht mit unserem Testbericht übereinstimmt, oder uns Belege und Fotos zusenden möchten, freuen wir uns über Ihren Hinweis.',
        'lbl_name': 'Ihr Name *', 'ph_name': 'z. B. Maximilian Weber',
        'lbl_email': 'Ihre E-Mail *', 'ph_email': 'z. B. maximilian@beispiel.de',
        'lbl_topic': 'Betreff / Flussgebiet',
        'lbl_msg': 'Ihre Nachricht *', 'ph_msg': 'Details, Reisedatum, Schiffsname oder Ihre Frage...',
        'captcha_title': 'Sicherheitsüberprüfung gegen Spam',
        'captcha_hint': 'Bitte lösen:',
        'captcha_err': 'Falsches Ergebnis. Bitte lösen Sie die Rechenaufgabe.',
        'btn': 'NACHRICHT SENDEN →',
        'opt1': 'Paris Seine Sightseeing', 'opt2': 'Paris Seine Dinner-Kreuzfahrten',
        'opt3': 'Amsterdam Grachtenfahrten', 'opt4': 'London Themse-Kreuzfahrten',
        'opt5': 'Erfahrungsbericht / Beleg / Foto einreichen', 'opt6': 'Allgemeine redaktionelle Frage'
    },
    'es': {
        'eyebrow': 'MESA EDITORIAL',
        'title': 'Contacte con Nuestra Redacción',
        'badge': '⚠️ ¡Lea antes de enviar un correo!',
        'warning': '<strong>No consideramos servicios ni productos no solicitados</strong> (SEO, compra de enlaces, agencias de marketing, etc.). El correo no deseado se eliminará automáticamente sin respuesta.',
        'lead': '¿Necesita ponerse en contacto con nuestra mesa editorial o enviar comentarios sobre una experiencia en crucero? Complete el siguiente formulario y le responderemos lo antes posible.<br/><br/>Si experimentó un crucero que no coincidió con nuestro informe de campo, o desea enviar fotos y recibos, siempre estamos abiertos a recibir sus comentarios.',
        'lbl_name': 'Su Nombre *', 'ph_name': 'ej. Carlos García',
        'lbl_email': 'Su Correo Electrónico *', 'ph_email': 'ej. carlos@ejemplo.es',
        'lbl_topic': 'Asunto / Río de interés',
        'lbl_msg': 'Su Mensaje *', 'ph_msg': 'Detalles, fecha del crucero, nombre del operador o su consulta...',
        'captcha_title': 'Verificación de Seguridad Anti-Spam',
        'captcha_hint': 'Por favor resuelva:',
        'captcha_err': 'Respuesta incorrecta. Por favor resuelva el cálculo para enviar.',
        'btn': 'ENVIAR MENSAJE →',
        'opt1': 'París Paseos en el Sena', 'opt2': 'París Cruceros con Cena en el Sena',
        'opt3': 'Ámsterdam Canales', 'opt4': 'Londres Támesis',
        'opt5': 'Comentarios de campo / Fotos / Recibos', 'opt6': 'Consulta editorial general'
    },
    'it': {
        'eyebrow': 'DESK EDITORIALE',
        'title': 'Contatta la Nostra Redazione',
        'badge': '⚠️ Da leggere prima di scrivere!',
        'warning': '<strong>Non prendiamo in considerazione offerte di servizi non richiesti</strong> (SEO, link building, agenzie di marketing, ecc.). Lo spam verrà eliminato automaticamente senza risposta.',
        'lead': 'Hai bisogno di contattare la nostra redazione o condividere un feedback su una crociera? Compila il modulo sottostante e ti risponderemo al più presto.<br/><br/>Se hai vissuto un\'esperienza che non corrisponde al nostro report sul campo o vuoi inviarci foto e scontrini, saremo felici di leggere il tuo messaggio.',
        'lbl_name': 'Il Tuo Nome *', 'ph_name': 'es. Marco Rossi',
        'lbl_email': 'La Tua Email *', 'ph_email': 'es. marco@esempio.it',
        'lbl_topic': 'Oggetto / Fiume di interesse',
        'lbl_msg': 'Il Tuo Messaggio *', 'ph_msg': 'Dettagli, data della crociera, nome della compagnia o la tua domanda...',
        'captcha_title': 'Verifica di Sicurezza Anti-Spam',
        'captcha_hint': 'Risolvi l\'operazione:',
        'captcha_err': 'Risposta errata. Risolvi il calcolo per inviare.',
        'btn': 'INVIA MESSAGGIO →',
        'opt1': 'Parigi Crociere Panoramiche sulla Senna', 'opt2': 'Parigi Crociere con Cena sulla Senna',
        'opt3': 'Amsterdam Canali', 'opt4': 'Londra Tamigi',
        'opt5': 'Feedback dal vivo / Foto / Ricevuta', 'opt6': 'Domanda editoriale generale'
    },
    'ja': {
        'eyebrow': '編集部デスク',
        'title': '編集部へのお問い合わせ',
        'badge': '⚠️ 送信前にお読みください',
        'warning': '<strong>営業メール、SEO・被リンク売買、記事広告仲介等のセールスは一切お断りしております。</strong>送信いただいても返信せず自動削除いたします。',
        'lead': '編集部へのご意見、掲載内容に関するお問い合わせ、乗船体験のフィードバックは以下のフォームよりお送りください。確認次第、担当者よりご連絡いたします。<br/><br/>記事の評価と異なる体験をされた場合や、現地での写真・領収書のご提供も随時歓迎しております。',
        'lbl_name': 'お名前 *', 'ph_name': '例：山田 太郎',
        'lbl_email': 'メールアドレス *', 'ph_email': '例：yamada@example.com',
        'lbl_topic': 'お問い合わせ項目 / 対象都市',
        'lbl_msg': 'メッセージ内容 *', 'ph_msg': '乗船日、船名、具体的なお問い合わせ内容をご記入ください...',
        'captcha_title': 'スパム防止セキュリティ確認',
        'captcha_hint': '計算してください:',
        'captcha_err': '回答が正しくありません。計算を解いてから送信してください。',
        'btn': 'メッセージを送信 →',
        'opt1': 'パリ セーヌ川 観光遊覧クルーズ', 'opt2': 'パリ セーヌ川 ディナークルーズ',
        'opt3': 'アムステルダム 運河クルーズ', 'opt4': 'ロンドン テムズ川クルーズ',
        'opt5': '実地体験のフィードバック・写真提供', 'opt6': '一般的な編集部へのお問い合わせ'
    },
    'nl': {
        'eyebrow': 'REDACTIE',
        'title': 'Contacteer Onze Redactie',
        'badge': '⚠️ Lees dit voor u mailt!',
        'warning': '<strong>Wij reageren niet op ongevraagde commerciële diensten</strong> (SEO, linkbuilding, marketingbureaus etc.). Spam wordt direct en automatisch verwijderd.',
        'lead': 'Wilt u contact opnemen met onze redactie of feedback delen over een riviercruise? Vul het onderstaande formulier in en we reageren zo snel mogelijk.<br/><br/>Als uw ervaring niet overeenkwam met ons verslag, of als u foto\'s en bonnetjes wilt insturen, horen we graag van u.',
        'lbl_name': 'Uw Naam *', 'ph_name': 'bijv. Daan de Jong',
        'lbl_email': 'Uw E-mailadres *', 'ph_email': 'bijv. daan@voorbeeld.nl',
        'lbl_topic': 'Onderwerp / Rivier',
        'lbl_msg': 'Uw Bericht *', 'ph_msg': 'Geef details, cruisedatum, rederij of uw specifieke vraag...',
        'captcha_title': 'Beveiligingscontrole tegen Spam',
        'captcha_hint': 'Los op:',
        'captcha_err': 'Onjuist antwoord. Los de berekening op om te verzenden.',
        'btn': 'BERICHT VERZENDEN →',
        'opt1': 'Parijs Seine Rondvaarten', 'opt2': 'Parijs Seine Dinercruises',
        'opt3': 'Amsterdam Grachtenrondvaarten', 'opt4': 'Londen Theems Rondvaarten',
        'opt5': 'Ervaring insturen / Foto / Bonnetjes', 'opt6': 'Algemene redactionele vraag'
    },
    'pl': {
        'eyebrow': 'BIURO REDAKCJI',
        'title': 'Skontaktuj się z Redakcją',
        'badge': '⚠️ Przeczytaj przed wysłaniem wiadomości!',
        'warning': '<strong>Nie odpowiadamy na niezamówione oferty handlowe</strong> (SEO, pozyskiwanie linków, agencje marketingowe itp.). Wszelki spam jest usuwany bez odpowiedzi.',
        'lead': 'Chcesz skontaktować się z redakcją lub przesłać opinię z rejsu? Wypełnij poniższy formularz, a odpowiemy tak szybko, jak to możliwe.<br/><br/>Jeśli Twoje wrażenia różniły się od naszego raportu lub chcesz przesłać anonimowe zdjęcia lub paragony, chętnie zapoznamy się z Twoją opinią.',
        'lbl_name': 'Twoje Imię *', 'ph_name': 'np. Piotr Kowalski',
        'lbl_email': 'Twój E-mail *', 'ph_email': 'np. piotr@przyklad.pl',
        'lbl_topic': 'Temat / Rzeka',
        'lbl_msg': 'Twoja Wiadomość *', 'ph_msg': 'Szczegóły, data rejsu, nazwa armatora lub Twoje pytanie...',
        'captcha_title': 'Weryfikacja Antyspamowa',
        'captcha_hint': 'Rozwiąż działanie:',
        'captcha_err': 'Nieprawidłowa odpowiedź. Rozwiąż działanie przed wysłaniem.',
        'btn': 'WYŚLIJ WIADOMOŚĆ →',
        'opt1': 'Paryż Rejsy Widokowe po Sekwanie', 'opt2': 'Paryż Rejsy z Kolacją po Sekwanie',
        'opt3': 'Amsterdam Rejsy Kanałami', 'opt4': 'Londyn Rejsy po Tamizie',
        'opt5': 'Opinia z rejsu / Zdjęcia / Paragony', 'opt6': 'Ogólne pytanie do redakcji'
    },
    'ro': {
        'eyebrow': 'BIROUL EDITORIAL',
        'title': 'Contactați Redacția Noastră',
        'badge': '⚠️ Citiți înainte de a trimite mesajul!',
        'warning': '<strong>Nu luăm în considerare oferte nesolicitate de servicii</strong> (SEO, link building, advertoriale, agenții de marketing etc.). Mesajele spam sunt șterse automat fără răspuns.',
        'lead': 'Doriți să luați legătura cu redacția noastră sau să trimiteți un pont despre o croazieră? Completați formularul de mai jos și vă vom răspunde în cel mai scurt timp.<br/><br/>Dacă ați trăit o experiență care nu s-a potrivit cu raportul nostru sau doriți să trimiteți fotografii și chitanțe, suntem mereu deschiși să vă ascultăm.',
        'lbl_name': 'Numele Dumneavoastră *', 'ph_name': 'ex. Andrei Ionescu',
        'lbl_email': 'Adresa de E-mail *', 'ph_email': 'ex. andrei@exemplu.ro',
        'lbl_topic': 'Subiect / Râu',
        'lbl_msg': 'Mesajul Dumneavoastră *', 'ph_msg': 'Detalii, data croazierei, numele operatorului sau întrebarea dvs...',
        'captcha_title': 'Verificare de Securitate Anti-Spam',
        'captcha_hint': 'Vă rugăm calculați:',
        'captcha_err': 'Răspuns incorect. Vă rugăm să rezolvați calculul.',
        'btn': 'TRIMITE MESAJUL →',
        'opt1': 'Paris Croaziere Panoramice pe Sena', 'opt2': 'Paris Croaziere cu Cină pe Sena',
        'opt3': 'Amsterdam Canale', 'opt4': 'Londra Tamisa',
        'opt5': 'Feedback din teren / Foto / Chitanțe', 'opt6': 'Întrebare editorială generală'
    }
}

def build_contact_main_html(lang):
    d = CONTACT_I18N[lang]

    return f'''
<main>
  <div class="form-section-touch" style="padding: 60px 20px 80px 20px; max-width: 860px; margin: 0 auto;">
    <div class="container-24">
      <div class="form-wrap-2" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 40px; box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);">
        <div class="title-wrap-2" style="margin-bottom: 32px;">
          <div class="ltt-contact-eyebrow" style="font-size: 11px; font-weight: 800; color: #dfa732; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 8px;">{d['eyebrow']}</div>
          <h1 class="heading-40" style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 32px; font-weight: 800; color: #0f172a; margin: 0 0 16px 0;">{d['title']}</h1>
          
          <div class="ltt-yellow-callout" style="background: #fefce8; border-left: 4px solid #eab308; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px;">
            <div class="ltt-yellow-callout-badge" style="font-size: 12px; font-weight: 800; color: #854d0e; margin-bottom: 4px;">{d['badge']}</div>
            <p class="ltt-yellow-callout-text" style="font-size: 13.5px; color: #713f12; line-height: 1.5; margin: 0;">
              {d['warning']}
            </p>
          </div>

          <p class="rich-text-intro" style="font-size: 15px; color: #475569; line-height: 1.65; margin: 0;">
            {d['lead']}
          </p>
        </div>

        <div class="form-block">
          <form action="https://formsubmit.co/adam.dimitrov.business@gmail.com" id="contact-form" method="POST">
            <input autocomplete="off" name="_gotcha" style="position: absolute; left: -9999px; opacity: 0; pointer-events: none; width: 0; height: 0;" tabindex="-1" type="text"/>
            <input name="_subject" type="hidden" value="New Inquiry via The Cruise Detective Contact Desk [{lang.upper()}]"/>
            <input name="_template" type="hidden" value="table"/>
            <input name="_captcha" type="hidden" value="false"/>

            <div class="field-wrap" style="margin-bottom: 18px;">
              <label class="field-label" for="Name-Touch" style="display: block; font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 6px;">{d['lbl_name']}</label>
              <input class="text-field-2" id="Name-Touch" maxlength="256" name="name" placeholder="{d['ph_name']}" required="" type="text" style="width: 100%; padding: 12px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; box-sizing: border-box;"/>
            </div>

            <div class="field-wrap" style="margin-bottom: 18px;">
              <label class="field-label" for="Email-Touch" style="display: block; font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 6px;">{d['lbl_email']}</label>
              <input class="text-field-2" id="Email-Touch" maxlength="256" name="email" placeholder="{d['ph_email']}" required="" type="email" style="width: 100%; padding: 12px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; box-sizing: border-box;"/>
            </div>

            <div class="field-wrap" style="margin-bottom: 18px;">
              <label class="field-label" for="Topic-Touch" style="display: block; font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 6px;">{d['lbl_topic']}</label>
              <select class="select-field" id="Topic-Touch" name="topic" style="width: 100%; padding: 12px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; background: #fff; box-sizing: border-box;">
                <option value="Paris Sightseeing">{d['opt1']}</option>
                <option value="Paris Dinner Cruises">{d['opt2']}</option>
                <option value="Amsterdam Canals">{d['opt3']}</option>
                <option value="London Thames">{d['opt4']}</option>
                <option value="Field Report Feedback">{d['opt5']}</option>
                <option value="General Editorial Question">{d['opt6']}</option>
              </select>
            </div>

            <div class="field-wrap" style="margin-bottom: 22px;">
              <label class="field-label" for="Message-Touch" style="display: block; font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 6px;">{d['lbl_msg']}</label>
              <textarea class="text-field-large" id="Message-Touch" maxlength="5000" name="message" placeholder="{d['ph_msg']}" required="" style="width: 100%; min-height: 130px; padding: 12px 14px; border: 1px solid #cbd5e1; border-radius: 8px; font-size: 14px; box-sizing: border-box;"></textarea>
            </div>

            <div class="ltt-captcha-card" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 16px; margin-bottom: 24px;">
              <div class="ltt-captcha-header" style="display: flex; align-items: center; gap: 8px; font-size: 12.5px; font-weight: 700; color: #0f172a; margin-bottom: 10px;">
                <svg fill="none" height="16" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="16"><rect height="11" rx="2" ry="2" width="18" x="3" y="11"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <span>{d['captcha_title']}</span>
              </div>
              <div class="ltt-captcha-prompt" style="display: flex; align-items: center; gap: 12px; font-size: 13.5px;">
                <span class="ltt-captcha-hint" style="color: #64748b;">{d['captcha_hint']}</span>
                <span class="ltt-captcha-equation" id="captchaEquation" style="font-weight: 800; color: #0f172a; font-size: 16px; background: #e2e8f0; padding: 4px 10px; border-radius: 6px;">7 + 4 = ?</span>
                <input autocomplete="off" class="ltt-captcha-input" id="captchaAnswer" placeholder="?" required="" type="number" style="width: 70px; padding: 6px 10px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 14px; text-align: center;"/>
              </div>
              <div class="ltt-captcha-error" id="captchaError" style="display: none; color: #dc2626; font-size: 12px; font-weight: 600; margin-top: 8px;">{d['captcha_err']}</div>
            </div>

            <div class="button-wrap-right" style="text-align: right;">
              <button class="buy-button-2" id="submitBtn" type="submit" style="padding: 14px 28px; font-size: 14px; cursor: pointer;">{d['btn']}</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</main>

<script>
  (function() {{
    var n1 = Math.floor(Math.random() * 8) + 2;
    var n2 = Math.floor(Math.random() * 7) + 1;
    var expected = n1 + n2;
    var eqEl = document.getElementById('captchaEquation');
    if (eqEl) eqEl.textContent = n1 + ' + ' + n2 + ' = ?';

    var form = document.getElementById('contact-form');
    var input = document.getElementById('captchaAnswer');
    var err = document.getElementById('captchaError');

    if (form) {{
      form.addEventListener('submit', function(e) {{
        if (parseInt(input.value, 10) !== expected) {{
          e.preventDefault();
          if (err) err.style.display = 'block';
          input.focus();
        }} else {{
          if (err) err.style.display = 'none';
        }}
      }});
    }}
  }})();
</script>
'''

def upgrade_contact_page(lang, rel_path):
    abs_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(abs_path):
        return

    with open(abs_path, 'r', encoding='utf-8') as f:
        html = f.read()

    main_html = build_contact_main_html(lang)

    # Replace <main>...</main> or <div class="form-section-touch">...</div>
    pos_main_start = html.find('<main')
    pos_main_end = html.find('</main>')

    if pos_main_start != -1 and pos_main_end != -1:
        html = html[:pos_main_start] + main_html + html[pos_main_end+7:]
    else:
        # Replace between </header> and <div class="footer-section">
        pos_header = html.find('</header>')
        pos_footer = html.find('<div class="footer-section">')
        if pos_header != -1 and pos_footer != -1:
            html = html[:pos_header+len('</header>')] + '\n' + main_html + '\n' + html[pos_footer:]
        else:
            print(f"[{lang.upper()}] Could not locate insertion points for contact page {rel_path}")
            return

    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[{lang.upper()}] Upgraded contact desk in: {rel_path}")

def main():
    for lang, rel_path in CONTACT_PAGES.items():
        upgrade_contact_page(lang, rel_path)

if __name__ == '__main__':
    main()
