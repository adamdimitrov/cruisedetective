import urllib.request
import urllib.parse
import json
import sys

env_path = '/Users/adamdimitrov/Development/cruisedetective/.env'
env_vars = {}
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            env_vars[k.strip()] = v.strip()

data = urllib.parse.urlencode({
    'client_id': env_vars['GOOGLE_ADS_CLIENT_ID'],
    'client_secret': env_vars['GOOGLE_ADS_CLIENT_SECRET'],
    'refresh_token': env_vars['GOOGLE_ADS_REFRESH_TOKEN'],
    'grant_type': 'refresh_token'
}).encode('utf-8')
req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode())['access_token']

customer_id = env_vars['GOOGLE_ADS_CUSTOMER_ID'].replace('-', '')
dev_token = env_vars.get('GOOGLE_ADS_DEVELOPER_TOKEN', 'WK-A1HREvXxnsvVLsWELNg')

headers = {
    'Authorization': f'Bearer {token}',
    'developer-token': dev_token,
    'Content-Type': 'application/json'
}

def api_call(endpoint, payload):
    url = f'https://googleads.googleapis.com/v26/customers/{customer_id}/{endpoint}'
    r = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error on {endpoint}: {e.code}", e.read().decode(), file=sys.stderr)
        raise

def query_google_ads(query):
    url = f'https://googleads.googleapis.com/v26/customers/{customer_id}/googleAds:search'
    payload = {'query': query}
    r = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(r) as resp:
        return json.loads(resp.read().decode())

CAMPAIGN_CONFIGS = {
    '[BOF] Paris - Dinner Cruise (EN)': {
        'path1': 'paris',
        'path2': 'dinner',
        'url': 'https://deals.thecruisedetective.com/dinner-cruise-paris',
        'headlines': [
            ('Top 5 Seine Dinner Cruises', 'HEADLINE_1'),
            ('Best Dinner Cruise in Paris?', 'HEADLINE_1'),
            ('5 Paris Dinner Cruises Ranked', 'HEADLINE_1'),
            ('Compare Menus & Prices 2026', None),
            ('Bateaux Mouches vs Parisiens', None),
            ('Don\'t Book The Wrong Boat', None),
            ('Gourmet 3 & 4-Course Menus', None),
            ('Tested In Person: Top 5', None),
            ('Official Dinners From €65', None),
            ('Luxury €130 Prestige Options', None),
            ('Panoramic Glass Ceilings', None),
            ('Live Singer & Champagne', None),
            ('Guaranteed Window Seats', None),
            ('Free 24h Cancellation', None),
            ('Direct Mobile QR Vouchers', None)
        ],
        'descriptions': [
            'We tested top 5 Seine dinner cruises for food quality, views & seating. Compare & pick #1.',
            'Bateaux Mouches €135 or Paris en Scène €65? Compare menus & tables before booking.',
            'Avoid tourist traps on the Seine. Real menus, photos & official direct booking links.',
            'Live music, French chef menus & sparkling Eiffel Tower views. Official passes from €65.'
        ]
    },
    '[BOF] Amsterdam - Canal Cruise (EN)': {
        'path1': 'amsterdam',
        'path2': 'cruises',
        'url': 'https://deals.thecruisedetective.com/amsterdam-canal-cruises',
        'headlines': [
            ('Top 5 Amsterdam Canal Cruises', 'HEADLINE_1'),
            ('Best Amsterdam Canal Cruise?', 'HEADLINE_1'),
            ('5 Amsterdam Cruises Ranked', 'HEADLINE_1'),
            ('Compare 5 Canal Cruises 2026', None),
            ('Lovers vs Flagship Boats', None),
            ('Don\'t Book The Wrong Boat', None),
            ('Open-Air vs Covered Boats', None),
            ('Tested In Person: Top 5', None),
            ('Official Tickets From €16', None),
            ('Skip 45-Min Pier Queues', None),
            ('Central Station Departures', None),
            ('Free Audio Guide In 19 Langs', None),
            ('Adults €16, Kids €10', None),
            ('Boats Every 15-30 Minutes', None),
            ('Direct Smartphone QR Passes', None)
        ],
        'descriptions': [
            'We tested Amsterdam\'s top 5 canal cruises for views, audio & comfort. Compare now.',
            'Lovers, Flagship or Blue Boat? Compare station piers, prices & open-air decks.',
            'Skip ticket office queues at Central Station. Instant smartphone QR pass from €16.',
            '1-hour UNESCO canal loop past Anne Frank House & Skinny Bridge. Departures every 15-30m.'
        ]
    },
    '[BOF] Paris - Sightseeing Cruise (DE)': {
        'path1': 'paris',
        'path2': 'seine',
        'url': 'https://deals.thecruisedetective.com/de/seine-rundfahrt-paris',
        'headlines': [
            ('Top 5 Seine-Bootsfahrten', 'HEADLINE_1'),
            ('Welche Bootsfahrt in Paris?', 'HEADLINE_1'),
            ('5 Paris Bootsfahrten Rangliste', 'HEADLINE_1'),
            ('Preise & Schiffe Vergleichen', None),
            ('Bateaux Mouches vs Parisiens', None),
            ('Das Falsche Boot Vermeiden', None),
            ('360° Freideck vs Glasdach', None),
            ('Vor Ort Getestet: Top 5', None),
            ('Tickets ab 17€ Online', None),
            ('60 Min Warteschlange Sparen', None),
            ('Direkter Handy-QR-Einlass', None),
            ('Erwachsene 17€-18€, Kinder 9€', None),
            ('Abfahrt Direkt Am Eiffelturm', None),
            ('Abfahrten Alle 30 Minuten', None),
            ('Audioguide Auf Deutsch', None)
        ],
        'descriptions': [
            'Wir haben die 5 besten Seine-Schiffe getestet. Vergleichen Sie Preise, Decks & Aussicht.',
            'Bateaux Parisiens oder Bateaux Mouches? Vergleichen Sie Anleger & Preise vor der Buchung.',
            'Keine 60 Min Wartezeit am Eiffelturm-Kassenhäuschen. Sofortiges Handy-QR-Ticket ab 17€.',
            'Erwachsene ab 17€, Kinder 50% Rabatt (8€–9€), unter 4 gratis. Abfahrten alle 30 Minuten.'
        ]
    },
    '[BOF] Paris - Sightseeing Cruise (ES)': {
        'path1': 'paris',
        'path2': 'sena',
        'url': 'https://deals.thecruisedetective.com/es/crucero-sena-paris',
        'headlines': [
            ('Top 5 Cruceros Sena París', 'HEADLINE_1'),
            ('¿Cuál Crucero Es El Mejor?', 'HEADLINE_1'),
            ('5 Mejores Barcos de París', 'HEADLINE_1'),
            ('Compara Precios y Vistas', None),
            ('Bateaux Mouches vs Parisiens', None),
            ('Evita Elegir el Barco Erróneo', None),
            ('Cubiertas 360° vs Cerradas', None),
            ('Probados en Persona: Top 5', None),
            ('Entradas Desde 17€ Online', None),
            ('Sáltate 60 Min de Cola', None),
            ('Acceso Móvil QR Inmediato', None),
            ('Adultos 17€-18€, Niños 9€', None),
            ('Salidas Junto a Torre Eiffel', None),
            ('Salidas Cada 30 Minutos', None),
            ('Audioguía en Español', None)
        ],
        'descriptions': [
            'Probamos los 5 mejores paseos en barco por el Sena. Compara precios, cubiertas y vistas.',
            '¿Bateaux Parisiens o Bateaux Mouches? Compara muelles, precios (17€ vs 18€) y opiniones.',
            'Evita 60 min de cola en taquilla de la Torre Eiffel. Pase digital con código QR desde 17€.',
            'Adultos desde 17€, niños al 50% (8€–9€), menores de 4 gratis. Barcos cada 30 minutos.'
        ]
    },
    '[BOF] Paris - Sightseeing Cruise (IT)': {
        'path1': 'parigi',
        'path2': 'senna',
        'url': 'https://deals.thecruisedetective.com/it/crociera-senna-parigi',
        'headlines': [
            ('Top 5 Crociere Senna Parigi', 'HEADLINE_1'),
            ('Quale Crociera Scegliere?', 'HEADLINE_1'),
            ('5 Migliori Battelli Parigi', 'HEADLINE_1'),
            ('Confronta Prezzi e Viste', None),
            ('Bateaux Mouches vs Parisiens', None),
            ('Evita il Battello Sbagliato', None),
            ('Ponte Aperto 360° Panoramico', None),
            ('Testati di Persona: Top 5', None),
            ('Biglietti Ufficiali Da 17€', None),
            ('Salta la Coda di 60 Minuti', None),
            ('Biglietto QR su Smartphone', None),
            ('Adulti 17€-18€, Bambini 9€', None),
            ('Partenze Sotto Torre Eiffel', None),
            ('Un Battello Ogni 30 Minuti', None),
            ('Audioguida in Italiano', None)
        ],
        'descriptions': [
            'Abbiamo testato le 5 migliori crociere sulla Senna. Confronta prezzi, ponti e viste 360°.',
            'Bateaux Parisiens o Mouches? Confronta moli e prezzi (17€ vs 18€) prima di prenotare.',
            'Salta 60 minuti di fila in biglietteria alla Torre Eiffel. Biglietto digitale QR da 17€.',
            'Adulti da 17€, bambini al 50% (8€–9€), sotto i 4 anni gratis. Partenze ogni 30 minuti.'
        ]
    },
    '[BOF] Paris - Sightseeing Cruise (NL)': {
        'path1': 'parijs',
        'path2': 'seine',
        'url': 'https://deals.thecruisedetective.com/nl/rondvaart-seine-parijs',
        'headlines': [
            ('Top 5 Rondvaarten Seine', 'HEADLINE_1'),
            ('Welke Boottocht in Parijs?', 'HEADLINE_1'),
            ('5 Beste Rondvaarten Parijs', 'HEADLINE_1'),
            ('Vergelijk Prijzen & Boten', None),
            ('Bateaux Mouches vs Parisiens', None),
            ('Kies Niet de Verkeerde Boot', None),
            ('360° Bovendek vs Overdekt', None),
            ('Zelf Getest: De 5 Beste', None),
            ('Officiële Tickets Vanaf 17€', None),
            ('Geen 60 Min Kassa Wachtrij', None),
            ('Direct Mobiel QR-Ticket', None),
            ('Volwassenen 17€-18€, Kind 9€', None),
            ('Vertrek Aan De Eiffeltoren', None),
            ('Elke 30 Minuten Vertrek', None),
            ('Audiogids in het Nederlands', None)
        ],
        'descriptions': [
            'We hebben de top 5 Seine rondvaarten getest. Vergelijk prijzen, bovendekken en uitzicht.',
            'Bateaux Parisiens of Bateaux Mouches? Vergelijk steigers en prijzen voor je boekt.',
            'Sla 60 minuten kassa-wachtrij over bij de Eiffeltoren. Digitaal QR-ticket vanaf 17€.',
            'Volwassenen vanaf 17€, kinderen 50% korting (8€–9€), onder 4 gratis. Elke 30m vertrek.'
        ]
    },
    '[BOF] Paris - Sightseeing Cruise (FR)': {
        'path1': 'paris',
        'path2': 'seine',
        'url': 'https://deals.thecruisedetective.com/fr/croisiere-seine-paris',
        'headlines': [
            ('Top 5 Croisières sur la Seine', 'HEADLINE_1'),
            ('Quelle Croisière Choisir?', 'HEADLINE_1'),
            ('5 Meilleures Croisières Paris', 'HEADLINE_1'),
            ('Comparez Prix et Bateaux 2026', None),
            ('Bateaux Mouches vs Parisiens', None),
            ('Évitez le Mauvais Bateau', None),
            ('Pont Supérieur 360° vs Vitré', None),
            ('Testé en Personne: Le Top 5', None),
            ('Billets Officiels Dès 17€', None),
            ('Évitez 60 Min de File Guichet', None),
            ('Embarquement QR sur Mobile', None),
            ('Adultes 17€-18€, Enfants 9€', None),
            ('Départs au Pied Tour Eiffel', None),
            ('Départs Toutes les 30 Minutes', None),
            ('Audioguide Smartphone Inclus', None)
        ],
        'descriptions': [
            'Nous avons testé les 5 meilleures croisières Seine. Comparez terrasses 360° et prix.',
            'Bateaux Parisiens ou Bateaux Mouches? Comparez embarcadères et tarifs avant de réserver.',
            'Évitez 60 min de file au guichet Tour Eiffel. Billet coupe-file mobile instantané dès 17€.',
            'Adultes dès 17€, enfants à -50% (8€–9€), -4 ans gratuit. Bateaux toutes les 30 min.'
        ]
    },
    '[BOF] Paris - Dinner Cruise (FR)': {
        'path1': 'paris',
        'path2': 'diner',
        'url': 'https://deals.thecruisedetective.com/fr/croisiere-diner-paris',
        'headlines': [
            ('Top 5 Croisières Dîner Paris', 'HEADLINE_1'),
            ('Meilleur Dîner Croisière?', 'HEADLINE_1'),
            ('5 Dîners Croisières Comparés', 'HEADLINE_1'),
            ('Comparez Menus & Prix 2026', None),
            ('Bateaux Mouches vs Parisiens', None),
            ('Évitez les Pièges à Touristes', None),
            ('Menus Gastronomiques 3-4 Plats', None),
            ('Testé en Personne: Top 5', None),
            ('Dîner Officiel Dès 65€', None),
            ('Options Prestige Luxe à 130€', None),
            ('Verrières et Plafond Étoilé', None),
            ('Chanteuse Live et Champagne', None),
            ('Tables Bord de Baie Vitrée', None),
            ('Annulation Gratuite 24h', None),
            ('Bon Mobile QR Instantané', None)
        ],
        'descriptions': [
            'Nous avons testé les 5 meilleurs dîners croisières sur la Seine. Comparez menus et tables.',
            'Bateaux Mouches 135€ ou Paris en Scène 65€? Comparez les menus avant de réserver ce soir.',
            'Évitez les pièges sur la Seine. Photos réelles, avis certifiés et accès partenaire Tiqets.',
            'Musique live, cuisine de chef et Tour Eiffel scintillante. Billets officiels dès 65€.'
        ]
    }
}

# Process each campaign
for camp_name, cfg in CAMPAIGN_CONFIGS.items():
    print(f"\n========================================================")
    print(f"UPDATING CAMPAIGN: {camp_name}")
    print(f"========================================================")

    # 1. Find ad group and current active ads
    q = f'''
    SELECT
      campaign.id,
      campaign.name,
      ad_group.id,
      ad_group.name,
      ad_group_ad.ad.id,
      ad_group_ad.resource_name,
      ad_group_ad.status
    FROM ad_group_ad
    WHERE campaign.name = '{camp_name}'
      AND ad_group_ad.status = 'ENABLED'
    '''
    res = query_google_ads(q)
    results = res.get('results', [])
    if not results:
        print(f"  ✗ No enabled ads found for {camp_name}, searching with all statuses...")
        q_any = f'''
        SELECT
          campaign.id,
          campaign.name,
          ad_group.id,
          ad_group.name,
          ad_group_ad.ad.id,
          ad_group_ad.resource_name,
          ad_group_ad.status
        FROM ad_group_ad
        WHERE campaign.name = '{camp_name}'
        LIMIT 5
        '''
        res_any = query_google_ads(q_any)
        results = res_any.get('results', [])
        if not results:
            print(f"  ✗ No ad group found at all for {camp_name}, skipping.")
            continue

    ag_id = results[0]['adGroup']['id']
    ag_res_name = f"customers/{customer_id}/adGroups/{ag_id}"
    old_ad_resources = [r['adGroupAd']['resourceName'] for r in results if r['adGroupAd']['status'] == 'ENABLED']

    # 2. Build headlines & descriptions
    hl_payload = []
    for text, pin in cfg['headlines']:
        item = {'text': text}
        if pin:
            item['pinnedField'] = pin
        hl_payload.append(item)

    desc_payload = [{'text': d} for d in cfg['descriptions']]

    # 3. Create New RSA
    create_payload = {
        'operations': [
            {
                'create': {
                    'adGroup': ag_res_name,
                    'status': 'ENABLED',
                    'ad': {
                        'finalUrls': [cfg['url']],
                        'responsiveSearchAd': {
                            'headlines': hl_payload,
                            'descriptions': desc_payload,
                            'path1': cfg['path1'],
                            'path2': cfg['path2']
                        }
                    }
                }
            }
        ]
    }

    try:
        create_res = api_call('adGroupAds:mutate', create_payload)
        new_ad_resource = create_res['results'][0]['resourceName']
        print(f"  ✓ Created new comparison RSA: {new_ad_resource}")
    except Exception as e:
        print(f"  ✗ Failed to create new RSA: {e}")
        continue

    # 4. Pause old ads
    if old_ad_resources:
        pause_ops = []
        for old_res in old_ad_resources:
            pause_ops.append({
                'updateMask': 'status',
                'update': {
                    'resourceName': old_res,
                    'status': 'PAUSED'
                }
            })
        try:
            pause_res = api_call('adGroupAds:mutate', {'operations': pause_ops})
            print(f"  ✓ Paused {len(pause_ops)} old unpinned ad(s)")
        except Exception as e:
            print(f"  ✗ Failed to pause old ads: {e}")

print("\nALL COMPARISON CAMPAIGNS UPDATED TO PINNED COMPARISON ADS!")
