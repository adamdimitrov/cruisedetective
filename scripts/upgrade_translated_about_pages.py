#!/usr/bin/env python3
"""
ABOUT MANIFESTO UPGRADE ENGINE — THE CRUISE DETECTIVE
Upgrades all 8 translated about pages with:
- Luxury editorial header
- 3 Travel Reality Manifesto cards
- Adam Dimitrov Founder & Lead Detective Card
- 5 Ethics & Disclosure Policy cards
- Modern luxury typography and cards
"""

import os
import re

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

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

ABOUT_I18N = {
    'fr': {
        'hdr_eyebrow': 'MANIFESTE ÉDITORIAL & STANDARDS',
        'hdr_title': 'Audit de Croisières Fluviales Sous Couverture.',
        'hdr_title_gold': 'Zéro Complaisance Sponsorisée.',
        'hdr_lead': 'Nous avons fondé The Cruise Detective pour remplacer les brochures promotionnelles par la réalité vérifiée du consommateur. Lorsque vous réservez une croisière de vacances à Paris, Amsterdam ou Londres, il n\'y a pas de droit de retour. Nous payons nos billets plein tarif, testons les bateaux incognito, inspectons les cuisines et rapportons ce que les agences dissimulent.',
        'sec1_eyebrow': 'LA RÉALITÉ DU VOYAGE',
        'sec1_title': 'Les Vacances N\'ont Pas de Politique de Retour',
        'sec1_sub': 'Pourquoi les blogs de voyage génériques et les avis d\'agences échouent lorsque votre argent et vos soirées romantiques sont en jeu.',
        'p1_title': 'Les avis TripAdvisor sont souvent biaisés',
        'p1_text': 'Entre faux avis rémunérés et touristes occasionnels ne comparant aucun autre bateau, les notes moyennes ne reflètent pas la réalité du service ni de la vue.',
        'p2_title': 'Les agences sont rémunérées par les bateaux',
        'p2_text': 'Les conciergeries et revendeurs recommandent les croisières offrant les commissions les plus élevées, pas nécessairement les meilleures tables.',
        'p3_title': 'On ne rejoue pas une soirée à Paris',
        'p3_text': 'Un dîner décevant avec vue masquée gâche toute une soirée de vacances. Notre mission est de vous garantir l\'excellence dès la première réservation.',
        'founder_eyebrow': 'FONDATEUR & ENQUÊTEUR TERRAIN',
        'founder_name': 'Adam Dimitrov',
        'founder_role': 'Fondateur & Détective en Chef',
        'founder_p1': 'Hé, je m\'appelle Adam. Je suis un entrepreneur européen basé à Budapest et voyageant constamment entre Paris, Amsterdam et Londres. J\'ai fondé The Cruise Detective après avoir vécu moi-même des dîners-croisières survendus aux tarifs exorbitants.',
        'founder_p2': 'Mon objectif est simple : rendre le choix de vos croisières limpide et fiable. Je réserve moi-même en tant que simple touriste, teste les menus complets et documente tout avec rigueur.',
        'sec2_eyebrow': 'CHARTE ÉTHIQUE & TRANSPARENCE',
        'sec2_title': 'Nos 5 Engagements Éditoriaux',
        'sec2_sub': 'Des normes strictes pour préserver une indépendance totale et la confiance de nos lecteurs.',
        'e1_title': '100% Billets Auto-Financés', 'e1_text': 'Aucun billet gratuit, repas offert ou surclassement de presse.',
        'e2_title': 'Anonymat Total à Bord', 'e2_text': 'Les équipages ignorent notre présence pour garantir un service standard.',
        'e3_title': 'Transparence d\'Affiliation', 'e3_text': 'Nous recommandons le meilleur bateau même quand les commissions sont plus faibles.',
        'e4_title': 'Ré-audits Périodiques', 'e4_text': 'Nous réévaluons régulièrement les menus et changements de navires.',
        'e5_title': 'Droit de Réponse & Rectification', 'e5_text': 'Si un opérateur améliore sa cuisine ou ses installations, nous le vérifions.'
    },
    'de': {
        'hdr_eyebrow': 'REDAKTIONELLES MANIFEST & STANDARDS',
        'hdr_title': 'Verdeckte Flusskreuzfahrt-Prüfungen.',
        'hdr_title_gold': 'Ohne Gesponsertes Schönreden.',
        'hdr_lead': 'Wir haben The Cruise Detective gegründet, um Werbeprospekte durch geprüfte Verbraucherrealität zu ersetzen. Bei einer Urlaubskreuzfahrt in Paris, Amsterdam oder London gibt es kein Rückgaberecht. Wir zahlen volle Preise aus eigener Tasche, testen Schiffe anonym und berichten ungeschönt.',
        'sec1_eyebrow': 'DIE REALE SITUATION',
        'sec1_title': 'Urlaubstage Kann Man Nicht Umtauschen',
        'sec1_sub': 'Warum Standard-Reiseblogs und Verkaufsportale versagen, wenn echtes Geld und romantische Abende auf dem Spiel stehen.',
        'p1_title': 'TripAdvisor-Noten sind oft verzerrt',
        'p1_text': 'Gefälschte Bewertungen und Gelegenheitsurlauber ohne Vergleichsmöglichkeiten spiegeln selten die wahre Speisenqualität oder Sicht wider.',
        'p2_title': 'Reisebüros verdienen an den Provisionen',
        'p2_text': 'Concierges und Agenturen empfehlen oft jene Schiffe mit den höchsten Vermittlungsgebühren, nicht die besten Gourmet-Menüs.',
        'p3_title': 'Ein Pariser Abend lässt sich nicht wiederholen',
        'p3_text': 'Ein schlechtes Menü oder ein blockierter Blick verdirbt den gesamten Urlaubstag. Unser Ziel ist es, dass Ihre Buchung auf Anhieb gelingt.',
        'founder_eyebrow': 'GRÜNDER & CHEF-ERMITTLER',
        'founder_name': 'Adam Dimitrov',
        'founder_role': 'Gründer & Chefredakteur',
        'founder_p1': 'Hey, ich bin Adam. Ich bin ein europäischer Unternehmer mit Sitz in Budapest und reise regelmäßig zwischen Paris, Amsterdam und London. Ich habe The Cruise Detective gegründet, nachdem ich selbst überteuerte und enttäuschende Fahrten erlebt hatte.',
        'founder_p2': 'Mein Ansatz: Ich buche als ganz normaler Tourist, teste die Schiffe inkognito und erstelle extrem detaillierte Guides für verlässliche Entscheidungen.',
        'sec2_eyebrow': 'ETHIK-RICHTLINIEN & TRANSPARENZ',
        'sec2_title': 'Unsere 5 Redaktionellen Grundsätze',
        'sec2_sub': 'Strenge Vorgaben zur Wahrung unserer Unabhängigkeit und des Vertrauens unserer Leser.',
        'e1_title': '100% Selbstbezahlte Tickets', 'e1_text': 'Keine Freikarten, Presseeinladungen oder Sonderbehandlungen.',
        'e2_title': 'Vollständige Anonymität an Bord', 'e2_text': 'Die Schiffsbesatzungen wissen nicht, dass wir bewerten.',
        'e3_title': 'Transparente Partnerschaften', 'e3_text': 'Wir empfehlen das beste Schiff unabhängig von Provisionssätzen.',
        'e4_title': 'Regelmäßige Nachprüfungen', 'e4_text': 'Wir aktualisieren Fahrten und Menüs kontinuierlich vor Ort.',
        'e5_title': 'Korrekturrichtlinie', 'e5_text': 'Wenn ein Anbieter seine Küche oder Schiffe verbessert, prüfen wir das nach.'
    },
    'es': {
        'hdr_eyebrow': 'MANIFIESTO EDITORIAL Y ESTÁNDARES',
        'hdr_title': 'Auditoría Encubierta de Cruceros Fluviales.',
        'hdr_title_gold': 'Cero Adornos Patrocinados.',
        'hdr_lead': 'Fundamos The Cruise Detective para sustituir los folletos comerciales por la realidad verificada del consumidor. Cuando reserva un crucero de vacaciones en París, Ámsterdam o Londres, no hay devoluciones. Pagamos nuestros propios billetes, evaluamos barcos de incógnito e informamos sin filtros.',
        'sec1_eyebrow': 'LA REALIDAD DE VIAJAR',
        'sec1_title': 'Las Vacaciones No Tienen Política de Devolución',
        'sec1_sub': 'Por qué los blogs genéricos y las agencias fallan cuando hay dinero real y momentos especiales en juego.',
        'p1_title': 'Las opiniones en TripAdvisor suelen estar sesgadas',
        'p1_text': 'Entre reseñas sospechosas y turistas que no tienen punto de comparación, las puntuaciones rara vez reflejan la calidad real.',
        'p2_title': 'Las agencias cobran comisiones de los barcos',
        'p2_text': 'Muchos conserjes recomiendan los barcos que más pagan, no necesariamente los que ofrecen la mejor cena.',
        'p3_title': 'Una noche en París no se puede repetir',
        'p3_text': 'Una mala mesa o una comida fría pueden arruinar una velada inolvidable. Nos aseguramos de que acierte a la primera.',
        'founder_eyebrow': 'FUNDADOR E INVESTIGADOR PRINCIPAL',
        'founder_name': 'Adam Dimitrov',
        'founder_role': 'Fundador y Editor Jefe',
        'founder_p1': 'Hola, soy Adam. Soy un emprendedor europeo con base en Budapest y viajo continuamente entre París, Ámsterdam y Londres. Creé The Cruise Detective tras sufrir decepciones personales en cruceros sobrevalorados.',
        'founder_p2': 'Mi compromiso: viajo como un turista común, pago la tarifa completa y elaboro guías exhaustivas y honestas para proteger su experiencia.',
        'sec2_eyebrow': 'CÓDIGO ÉTICO Y TRANSPARENCIA',
        'sec2_title': 'Nuestros 5 Compromisos Editoriales',
        'sec2_sub': 'Normas rigurosas para salvaguardar la total independencia y la confianza del lector.',
        'e1_title': '100% Billetes Autofinanciados', 'e1_text': 'Sin billetes de cortesía ni invitaciones comerciales.',
        'e2_title': 'Anonimato a Bordo', 'e2_text': 'La tripulación nunca sabe que estamos evaluando el servicio.',
        'e3_title': 'Divulgación Transparente', 'e3_text': 'Recomendamos el mejor barco sin importar la comisión.',
        'e4_title': 'Reauditorías Periódicas', 'e4_text': 'Verificamos periódicamente cambios de carta y nuevos barcos.',
        'e5_title': 'Política de Rectificación', 'e5_text': 'Si un operador renueva su propuesta culinaria, lo comprobamos.'
    },
    'it': {
        'hdr_eyebrow': 'MANIFESTO EDITORIALE E STANDARD',
        'hdr_title': 'Audit in Incognito delle Crociere Fluviali.',
        'hdr_title_gold': 'Nessuna Condiscendenza Pubblicitaria.',
        'hdr_lead': 'Abbiamo fondato The Cruise Detective per sostituire le brochure promozionali con l\'esperienza verificata del viaggiatore. Quando prenoti una crociera a Parigi, Amsterdam o Londra, non esistono rimborsi per una serata rovinata. Paghiamo le nostre tariffe, viaggiamo in incognito e diciamo la verità.',
        'sec1_eyebrow': 'LA REALTÀ DEL VIAGGIO',
        'sec1_title': 'I Viaggi Non Hanno Politiche di Reso',
        'sec1_sub': 'Perché i blog turistici generici e le agenze di viaggi non aiutano quando sono in gioco serate romantiche e soldi reali.',
        'p1_title': 'Le recensioni online sono spesso ingannevoli',
        'p1_text': 'Tra voti pilotati e commenti di chi non ha mai provato altri battelli, i punteggi medi non raccontano l\'esperienza autentica.',
        'p2_title': 'Le agenzie promuovono chi offre commissioni più alte',
        'p2_text': 'I concierge spesso consigliano i battelli più remunerativi per loro, non quelli con il miglior cibo.',
        'p3_title': 'Una serata speciale non si può ripetere',
        'p3_text': 'Una cena scadente o un tavolo lontano dai finestrini può rovinare un\'intera vacanza. Ti aiutiamo a scegliere subito il battello giusto.',
        'founder_eyebrow': 'FONDATORE E INVESTIGATORE CAPO',
        'founder_name': 'Adam Dimitrov',
        'founder_role': 'Fondatore e Direttore Editoriale',
        'founder_p1': 'Ehi, sono Adam. Sono un imprenditore europeo con sede a Budapest e viaggio costantemente a Parigi, Amsterdam e Londra. Ho creato The Cruise Detective dopo aver vissuto in prima persona crociere fluviali deludenti e trappole per turisti.',
        'founder_p2': 'Il mio approccio: viaggio come un normale turista, pago il biglietto intero e scrivo guide dettagliatissime e imparziali.',
        'sec2_eyebrow': 'CODICE ETICO E TRASPARENZA',
        'sec2_title': 'I Nostri 5 Impegni Editoriali',
        'sec2_sub': 'Regole ferree per garantire indipendenza totale e proteggere i lettori.',
        'e1_title': '100% Biglietti Autofinanziati', 'e1_text': 'Nessun accredito stampa o cena omaggio.',
        'e2_title': 'Totale Anonimato a Bordo', 'e2_text': 'Il personale non sa che stiamo recensendo l\'esperienza.',
        'e3_title': 'Trasparenza sulle Affiliazioni', 'e3_text': 'Consigliamo il miglior battello a prescindere dal guadagno.',
        'e4_title': 'Verifiche Periodiche', 'e4_text': 'Torniamo regolarmente a bordo per verificare i cambi di menu.',
        'e5_title': 'Rettifiche Aperte', 'e5_text': 'Se una compagnia migliora la qualità del cibo o le navi, ne diamo conto.'
    },
    'ja': {
        'hdr_eyebrow': '編集部の行動指針・評価基準',
        'hdr_title': '現地覆面調査によるリバークルーズ検証。',
        'hdr_title_gold': 'PR・企業案件による妥協は一切なし。',
        'hdr_lead': 'The Cruise Detective は、美辞麗句が並ぶ旅行パンフレットではなく、乗船者の目線に立った真実をお届けするために設立されました。パリ、アムステルダム、ロンドンでの旅行において、失敗したディナーを取り戻す保証はありません。私たちは自費で乗船し、客観的に評価した情報のみをお届けします。',
        'sec1_eyebrow': '旅のシビアな現実',
        'sec1_title': '旅の思い出に「返品保証」はありません',
        'sec1_sub': '大切なお金と特別な夜をかけるとき、一般的な旅行ブログや宣伝サイトが役に立たない理由。',
        'p1_title': '口コミサイトの評価は偏りがち',
        'p1_text': '1回しか乗船していない旅行者の感想やステマ投稿では、本当の料理の質や座席の眺望を正しく比較できません。',
        'p2_title': '代理店は手数料の高い船を優先する',
        'p2_text': 'ホテルのコンシェルジュや販売代理店は、料理の美味しさではなく、自社の利益率が高いクルーズを勧めがちです。',
        'p3_title': '特別な夜の失敗は取り返せない',
        'p3_text': '冷めた食事や見通しの悪い席は、旅行全体の印象を台無しにします。最初から確実に納得のいく一隻を選んでいただくことが私たちの使命です。',
        'founder_eyebrow': '創設者 兼 主任調査員',
        'founder_name': 'Adam Dimitrov',
        'founder_role': '創設者 兼 編集長',
        'founder_p1': 'こんにちは、アダムです。ブダペストを拠点とする欧州の起業家で、パリ、アムステルダム、ロンドンを頻繁に訪れています。過去に自身が過大広告のクルーズで失敗した苦い経験から、本音で評価する専門メディアを立ち上げました。',
        'founder_p2': '私の検証手法はシンプルです。一般の観光客として自費でチケットを買い、全メニューを実食して徹底的に検証します。',
        'sec2_eyebrow': '編集倫理と透明性',
        'sec2_title': '編集部が遵守する5つの約束',
        'sec2_sub': '完全な中立性と読者の信頼を守るための厳格なルール。',
        'e1_title': '100% 自費での乗船', 'e1_text': '無料招待券や特別優待は受け取りません。',
        'e2_title': '完全覆面調査の徹底', 'e2_text': '乗組員に身元を明かさず、通常通りのサービスを受けます。',
        'e3_title': '収益に左右されない選定', 'e3_text': '手数料に関係なく、最も満足度の高い船を推薦します。',
        'e4_title': '定期的な再検証', 'e4_text': '季節やメニューの変更に合わせて現地調査を更新します。',
        'e5_title': '公正な再評価', 'e5_text': '料理や船体が改善された場合は、再度検証して反映します。'
    },
    'nl': {
        'hdr_eyebrow': 'REDACTIONEEL MANIFEST & STANDAARDEN',
        'hdr_title': 'Onafhankelijke Riviercruise Audits.',
        'hdr_title_gold': 'Zonder Gesponsorde Mooipraterij.',
        'hdr_lead': 'Wij richtten The Cruise Detective op om commerciële brochures te vervangen door geverifieerde realiteit. Bij een cruisevakantie in Parijs, Amsterdam of Londen is er geen retourrecht. We betalen onze eigen tickets, keuren schepen anoniem en rapporteren zonder filter.',
        'sec1_eyebrow': 'DE HARDE REALITEIT',
        'sec1_title': 'Vakanties Kennen Geen Tevredenheidsgarantie',
        'sec1_sub': 'Waarom algemene reisblogs en touroperators tekortschieten wanneer echt geld en romantische avonden op het spel staan.',
        'p1_title': 'TripAdvisor-reviews geven een vertekend beeld',
        'p1_text': 'Door neprecensies en toeristen die niets hebben om mee te vergelijken, zeggen algemene scores weinig over de kwaliteit.',
        'p2_title': 'Tussenpersonen sturen op de hoogste commissie',
        'p2_text': 'Veel concierges bevelen de schepen aan waar zij het meeste aan verdienen, niet de schepen met het beste diner.',
        'p3_title': 'Een avond in Parijs doe je niet zomaar over',
        'p3_text': 'Een kille maaltijd of een tafel zonder uitzicht bederft de hele avond. Wij zorgen dat u in één keer goed kiest.',
        'founder_eyebrow': 'OPRICHTER & HOOFDONDERZOEKER',
        'founder_name': 'Adam Dimitrov',
        'founder_role': 'Oprichter & Hoofdredacteur',
        'founder_p1': 'Hé, ik ben Adam. Ik ben een Europese ondernemer gevestigd in Boedapest en reis voortdurend tussen Parijs, Amsterdam en Londen. Ik richtte The Cruise Detective op na zelf teleurgesteld te zijn door toeristische valstrikken.',
        'founder_p2': 'Mijn aanpak: ik boek als normale toerist, betaal vol tarief en documenteer elk detail voor een betrouwbaar advies.',
        'sec2_eyebrow': 'ETHISCHE CODE & TRANSPARANTIE',
        'sec2_title': 'Onze 5 Redactionele Beloftes',
        'sec2_sub': 'Strikte normen om onze onafhankelijkheid en het vertrouwen van onze lezers te waarborgen.',
        'e1_title': '100% Zelfbekostigde Tickets', 'e1_text': 'Geen gratis tickets, persmaaltijden of voorkeursbehandeling.',
        'e2_title': 'Anoniem aan Boord', 'e2_text': 'De bemanning weet nooit dat we een review schrijven.',
        'e3_title': 'Onafhankelijk van Commissies', 'e3_text': 'We bevelen het beste schip aan, ongeacht de opbrengst.',
        'e4_title': 'Regelmatige Herkeuringen', 'e4_text': 'We toetsen veranderende menukaarten en schepen opnieuw.',
        'e5_title': 'Correctiebeleid', 'e5_text': 'Als een rederij verbetert, controleren we dat direct ter plaatse.'
    },
    'pl': {
        'hdr_eyebrow': 'MANIFEST REDAKCYJNY I STANDARDY',
        'hdr_title': 'Niezależny Audyt Rejsów Rzecznych.',
        'hdr_title_gold': 'Bez Sponsorowanego Lukrowania.',
        'hdr_lead': 'Założyliśmy The Cruise Detective, aby zastąpić foldery reklamowe zweryfikowaną rzeczywistością pasażera. Na wakacjach w Paryżu, Amsterdamie czy Londynie nie ma gwarancji zwrotu za nieudany wieczór. Płacimy za bilety pełną stawkę, testujemy incognito i mówimy prawdę.',
        'sec1_eyebrow': 'RZECZYWISTOŚĆ PODRÓŻY',
        'sec1_title': 'Wakacje Nie Mają Polityki Zwrotów',
        'sec1_sub': 'Dlaczego ogólne blogi i biura podróży zawodzą, gdy w grę wchodzą duże pieniądze i wyjątkowe chwile.',
        'p1_title': 'Opinie na TripAdvisorze bywają mylące',
        'p1_text': 'Pomiędzy opłacanymi wpisami a opiniami osób niemających porównania, średnie oceny rzadko oddają realną jakość dań i widoków.',
        'p2_title': 'Pośrednicy polecają rejsy z najwyższą prowizją',
        'p2_text': 'Konsjerże i portale często promują statki, które płacą im najwięcej, a nie te, które serwują wybitne jedzenie.',
        'p3_title': 'Nie powtórzysz wieczoru w Paryżu',
        'p3_text': 'Niedobre danie lub zły stolik mogą zepsuć całą wycieczkę. Naszym celem jest pomóc Ci dokonać bezbłędnego wyboru.',
        'founder_eyebrow': 'ZAŁOŻYCIEL I GŁÓWNY DETEKTYW',
        'founder_name': 'Adam Dimitrov',
        'founder_role': 'Założyciel i Redaktor Naczelny',
        'founder_p1': 'Cześć, jestem Adam. Jestem europejskim przedsiębiorcą mieszkającym w Budapeszcie i regularnie podróżującym po Paryżu, Amsterdamie i Londynie. Założyłem The Cruise Detective po tym, jak sam padłem ofiarą przereklamowanych rejsów.',
        'founder_p2': 'Moja metoda: wchodzę na pokład jako zwykły turysta, płacę pełną cenę i tworzę bezkompromisowe przewodniki.',
        'sec2_eyebrow': 'ETYKA REDAKCYJNA I PRZEJRZYSTOŚĆ',
        'sec2_title': 'Nasze 5 Zasad Niezależności',
        'sec2_sub': 'Rygorystyczne reguły chroniące rzetelność ocen i zaufanie naszych czytelników.',
        'e1_title': '100% Własne Finansowanie', 'e1_text': 'Nie przyjmujemy darmowych biletów ani zaproszeń prasowych.',
        'e2_title': 'Pełna Anonimowość', 'e2_text': 'Załoga statku nigdy nie wie, że recenzujemy ich usługę.',
        'e3_title': 'Czyste Zasady Afiliacji', 'e3_text': 'Polecamy najlepszy statek bez względu na wysokość prowizji.',
        'e4_title': 'Cykliczne Reaudyty', 'e4_text': 'Regularnie weryfikujemy zmiany w kartach dań i remonty statków.',
        'e5_title': 'Otwartość na Fakty', 'e5_text': 'Gdy armator podnosi standard kuchni, sprawdzamy to i aktualizujemy wpis.'
    },
    'ro': {
        'hdr_eyebrow': 'MANIFEST EDITORIAL ȘI STANDARDE',
        'hdr_title': 'Audit Sub Acoperire al Croazierelor Fluviale.',
        'hdr_title_gold': 'Fără Promovare Mascată.',
        'hdr_lead': 'Am fondat The Cruise Detective pentru a înlocui broșurile publicitare cu experiența reală și verificată a călătorului. Când rezervați o croazieră la Paris, Amsterdam sau Londra, nu există politică de retur pentru o seară ratată. Plătim biletele integral, evaluăm sub acoperire și relatăm sincer.',
        'sec1_eyebrow': 'REALITATEA DIN SPATELE CĂLĂTORIILOR',
        'sec1_title': 'Vacanțele Nu Au Politică de Retur',
        'sec1_sub': 'De ce blogurile generice și agențiile eșuează când sunt în joc bani reali și seri romantice.',
        'p1_title': 'Recenziile online sunt adesea distorsionate',
        'p1_text': 'Între evaluări plătite și turiști ocazionali care nu au termen de comparație, scorurile medii nu reflectă calitatea meniului.',
        'p2_title': 'Agențiile promovează navele cu comisioane mari',
        'p2_text': 'Concierge-ii recomandă frecvent vasele cele mai profitabile pentru ei, nu neapărat cele cu cea mai bună bucătărie.',
        'p3_title': 'O seară la Paris nu se poate relua',
        'p3_text': 'O masă slabă sau o vedere obstrucționată poate ruina un sejur întreg. Ne asigurăm că alegeți perfect din prima încercare.',
        'founder_eyebrow': 'FONDATOR ȘI DETECTIV ȘEF',
        'founder_name': 'Adam Dimitrov',
        'founder_role': 'Fondator și Redactor-Șef',
        'founder_p1': 'Hei, eu sunt Adam. Sunt un antreprenor european stabilit la Budapesta și călătoresc neîncetat între Paris, Amsterdam și Londra. Am creat The Cruise Detective după ce am experimentat direct croaziere dezamăgitoare și scumpe.',
        'founder_p2': 'Abordarea mea: rezerv ca un turist obișnuit, plătesc tariful standard și redactez ghiduri detaliate și nepărtinitoare.',
        'sec2_eyebrow': 'COD ETIC ȘI TRANSPARENȚĂ',
        'sec2_title': 'Cele 5 Angajamente Editoriale',
        'sec2_sub': 'Standarde stricte pentru a garanta independența totală și respectul față de cititori.',
        'e1_title': '100% Bilete Autofinanțate', 'e1_text': 'Fără bilete gratuite, invitații de presă sau tratament special.',
        'e2_title': 'Anonimat Desăvârșit la Bord', 'e2_text': 'Echipajul nu știe niciodată că este evaluat.',
        'e3_title': 'Transparență Totală', 'e3_text': 'Recomandăm cel mai bun vas indiferent de comision.',
        'e4_title': 'Re-evaluări Periodice', 'e4_text': 'Revenim frecvent pe apă pentru a testa noile meniuri.',
        'e5_title': 'Corectitudine Editorială', 'e5_text': 'Dacă o companie își modernizează flota sau mâncarea, consemnăm asta.'
    }
}

def build_about_main_html(lang):
    d = ABOUT_I18N[lang]

    return f'''
<main id="main-content">
  <!-- ABOUT HEADER -->
  <section class="ltt-about-header" style="background: radial-gradient(circle at 50% 18%, rgba(2, 132, 199, 0.16) 0%, transparent 60%), linear-gradient(180deg, #0a192f 0%, #0f172a 100%) !important; color: #ffffff; padding: 76px 20px 84px 20px; text-align: center;">
    <div class="ltt-container" style="max-width: 920px; margin: 0 auto;">
      <div class="ltt-section-eyebrow" style="color: #dfa732; font-weight: 800; letter-spacing: 0.1em; margin-bottom: 16px;">{d['hdr_eyebrow']}</div>
      <h1 class="ltt-about-main-title" style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 40px; font-weight: 800; line-height: 1.22; margin: 0 0 20px 0; color: #ffffff;">
        {d['hdr_title']}<br/>
        <span style="background: linear-gradient(135deg, #dfa732 0%, #fef08a 50%, #b88214 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{d['hdr_title_gold']}</span>
      </h1>
      <p class="ltt-about-intro-lead" style="font-size: 17px; line-height: 1.65; color: #cbd5e1; margin: 0 auto; max-width: 820px;">
        {d['hdr_lead']}
      </p>
    </div>
  </section>

  <!-- SECTION 1: MANIFESTO PILLARS -->
  <section class="ltt-section" style="padding: 72px 20px; max-width: 1180px; margin: 0 auto;">
    <div class="ltt-section-header" style="text-align: center; max-width: 760px; margin: 0 auto 48px auto;">
      <div class="ltt-section-eyebrow" style="color: #dfa732; font-weight: 800; letter-spacing: 0.1em; margin-bottom: 8px;">{d['sec1_eyebrow']}</div>
      <h2 class="ltt-section-title" style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 32px; font-weight: 800; color: #0f172a; margin: 0 0 12px 0;">{d['sec1_title']}</h2>
      <p class="ltt-section-subtitle" style="font-size: 16px; color: #64748b; line-height: 1.6; margin: 0;">{d['sec1_sub']}</p>
    </div>

    <div class="ltt-manifesto-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px;">
      <div class="ltt-manifesto-card" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 28px 24px;">
        <div style="font-size: 32px; margin-bottom: 14px;">📉</div>
        <h3 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 18px; font-weight: 800; color: #0f172a; margin: 0 0 10px 0;">{d['p1_title']}</h3>
        <p style="font-size: 14px; color: #64748b; line-height: 1.65; margin: 0;">{d['p1_text']}</p>
      </div>

      <div class="ltt-manifesto-card" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 28px 24px;">
        <div style="font-size: 32px; margin-bottom: 14px;">🤝</div>
        <h3 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 18px; font-weight: 800; color: #0f172a; margin: 0 0 10px 0;">{d['p2_title']}</h3>
        <p style="font-size: 14px; color: #64748b; line-height: 1.65; margin: 0;">{d['p2_text']}</p>
      </div>

      <div class="ltt-manifesto-card" style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 28px 24px;">
        <div style="font-size: 32px; margin-bottom: 14px;">🍷</div>
        <h3 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 18px; font-weight: 800; color: #0f172a; margin: 0 0 10px 0;">{d['p3_title']}</h3>
        <p style="font-size: 14px; color: #64748b; line-height: 1.65; margin: 0;">{d['p3_text']}</p>
      </div>
    </div>
  </section>

  <!-- SECTION 2: FOUNDER CARD -->
  <section class="ltt-section" style="padding: 0 20px 72px 20px; max-width: 1180px; margin: 0 auto;">
    <div class="ltt-author-card" style="max-width: 900px; margin: 0 auto; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 40px; box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06); display: flex; gap: 32px; align-items: center;">
      <img alt="{d['founder_name']}" class="ltt-author-img" height="120" src="/assets/cdn/652d0405192ba076b04f74a3/652d0405192ba076b04f792d_Adam-dimitrov-portrait-500x500.webp" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; flex-shrink: 0; border: 3px solid #dfa732;" width="120"/>
      <div>
        <div style="font-size: 11px; font-weight: 800; color: #dfa732; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 6px;">{d['founder_eyebrow']}</div>
        <h3 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 26px; font-weight: 800; color: #0f172a; margin: 0 0 4px 0;">{d['founder_name']}</h3>
        <div style="font-size: 14px; font-weight: 600; color: #64748b; margin-bottom: 14px;">{d['founder_role']}</div>
        <p style="font-size: 14.5px; color: #334155; line-height: 1.65; margin: 0 0 12px 0;">{d['founder_p1']}</p>
        <p style="font-size: 14.5px; color: #334155; line-height: 1.65; margin: 0;">{d['founder_p2']}</p>
      </div>
    </div>
  </section>

  <!-- SECTION 3: ETHICS POLICY -->
  <section class="ltt-section ltt-ethics-section" id="methodology" style="background: #f8fafc; border-top: 1px solid #e2e8f0; padding: 72px 20px; max-width: 100%;">
    <div style="max-width: 1180px; margin: 0 auto;">
      <div class="ltt-section-header" style="text-align: center; max-width: 760px; margin: 0 auto 48px auto;">
        <div class="ltt-section-eyebrow" style="color: #dfa732; font-weight: 800; letter-spacing: 0.1em; margin-bottom: 8px;">{d['sec2_eyebrow']}</div>
        <h2 class="ltt-section-title" style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 32px; font-weight: 800; color: #0f172a; margin: 0 0 12px 0;">{d['sec2_title']}</h2>
        <p class="ltt-section-subtitle" style="font-size: 16px; color: #64748b; line-height: 1.6; margin: 0;">{d['sec2_sub']}</p>
      </div>

      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px;">
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 18px;">
          <div style="font-size: 18px; margin-bottom: 8px;">💳</div>
          <h4 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 15px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0;">{d['e1_title']}</h4>
          <p style="font-size: 13px; color: #64748b; line-height: 1.55; margin: 0;">{d['e1_text']}</p>
        </div>

        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 18px;">
          <div style="font-size: 18px; margin-bottom: 8px;">🕵️</div>
          <h4 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 15px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0;">{d['e2_title']}</h4>
          <p style="font-size: 13px; color: #64748b; line-height: 1.55; margin: 0;">{d['e2_text']}</p>
        </div>

        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 18px;">
          <div style="font-size: 18px; margin-bottom: 8px;">⚖️</div>
          <h4 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 15px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0;">{d['e3_title']}</h4>
          <p style="font-size: 13px; color: #64748b; line-height: 1.55; margin: 0;">{d['e3_text']}</p>
        </div>

        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 18px;">
          <div style="font-size: 18px; margin-bottom: 8px;">🔄</div>
          <h4 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 15px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0;">{d['e4_title']}</h4>
          <p style="font-size: 13px; color: #64748b; line-height: 1.55; margin: 0;">{d['e4_text']}</p>
        </div>

        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px 18px;">
          <div style="font-size: 18px; margin-bottom: 8px;">📝</div>
          <h4 style="font-family: 'Plus Jakarta Sans', var(--font-sans); font-size: 15px; font-weight: 800; color: #0f172a; margin: 0 0 6px 0;">{d['e5_title']}</h4>
          <p style="font-size: 13px; color: #64748b; line-height: 1.55; margin: 0;">{d['e5_text']}</p>
        </div>
      </div>
    </div>
  </section>
</main>
'''

def upgrade_about_page(lang, rel_path):
    abs_path = os.path.join(BASE_DIR, rel_path)
    if not os.path.exists(abs_path):
        return

    with open(abs_path, 'r', encoding='utf-8') as f:
        html = f.read()

    main_html = build_about_main_html(lang)

    # Replace <main>...</main> or content between </header> and <div class="footer-section">
    pos_main_start = html.find('<main')
    pos_main_end = html.find('</main>')

    if pos_main_start != -1 and pos_main_end != -1:
        html = html[:pos_main_start] + main_html + html[pos_main_end+7:]
    else:
        pos_header = html.find('</header>')
        pos_footer = html.find('<div class="footer-section">')
        if pos_header != -1 and pos_footer != -1:
            html = html[:pos_header+len('</header>')] + '\n' + main_html + '\n' + html[pos_footer:]
        else:
            print(f"[{lang.upper()}] Could not locate insertion points for about page {rel_path}")
            return

    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[{lang.upper()}] Upgraded luxury about manifesto in: {rel_path}")

def main():
    for lang, rel_path in ABOUT_PAGES.items():
        upgrade_about_page(lang, rel_path)

if __name__ == '__main__':
    main()
