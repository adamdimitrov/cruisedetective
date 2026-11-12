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

# 1. Create Campaign Budget (€20/day)
budget_payload = {
    "operations": [
        {
            "create": {
                "name": "[TEST] Paris - Bateaux Parisiens Brand (Phrase €0.25) Budget €20",
                "amountMicros": "20000000",
                "deliveryMethod": "STANDARD"
            }
        }
    ]
}
try:
    budget_res = api_call('campaignBudgets:mutate', budget_payload)
    budget_resource = budget_res['results'][0]['resourceName']
except Exception:
    budget_resource = "customers/4899321613/campaignBudgets/15981871152"
print(f"Using Budget: {budget_resource}")

# 2. Create Campaign (Target Spend with Max CPC = €0.25)
campaign_payload = {
    "operations": [
        {
            "create": {
                "name": "[TEST] Paris - Bateaux Parisiens Brand (Phrase €0.25)",
                "status": "ENABLED",
                "advertisingChannelType": "SEARCH",
                "campaignBudget": budget_resource,
                "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING",
                "targetSpend": {
                    "cpcBidCeilingMicros": "250000"
                },
                "networkSettings": {
                    "targetGoogleSearch": True,
                    "targetSearchNetwork": False,
                    "targetContentNetwork": False
                },
                "geoTargetTypeSetting": {
                    "positiveGeoTargetType": "PRESENCE"
                }
            }
        }
    ]
}
camp_res = api_call('campaigns:mutate', campaign_payload)
campaign_resource = camp_res['results'][0]['resourceName']
print(f"Created Campaign: {campaign_resource}")

# 3. Add Language (English) & Negative Keywords to Campaign
negatives = [
    'contact', 'phone', 'telephone', 'jobs', 'careers', 'recruitment',
    'address', 'directions', 'metro', 'parking', 'cancel', 'cancellation',
    'refund', 'login', 'free', 'map'
]

criteria_operations = [
    {
        "create": {
            "campaign": campaign_resource,
            "language": {
                "languageConstant": "languageConstants/1000"
            }
        }
    }
]
for neg in negatives:
    criteria_operations.append({
        "create": {
            "campaign": campaign_resource,
            "negative": True,
            "keyword": {
                "text": neg,
                "matchType": "BROAD"
            }
        }
    })

crit_res = api_call('campaignCriteria:mutate', {"operations": criteria_operations})
print(f"Added {len(crit_res['results'])} campaign criteria (English + {len(negatives)} Negatives)")

# 4. Create Ad Group
ad_group_payload = {
    "operations": [
        {
            "create": {
                "name": "Bateaux Parisiens - Brand Phrase (€0.25)",
                "campaign": campaign_resource,
                "status": "ENABLED",
                "type": "SEARCH_STANDARD"
            }
        }
    ]
}
ag_res = api_call('adGroups:mutate', ad_group_payload)
ad_group_resource = ag_res['results'][0]['resourceName']
print(f"Created Ad Group: {ad_group_resource}")

# 5. Add Phrase Match Keyword: "bateaux parisiens"
kw_payload = {
    "operations": [
        {
            "create": {
                "adGroup": ad_group_resource,
                "status": "ENABLED",
                "keyword": {
                    "text": "bateaux parisiens",
                    "matchType": "PHRASE"
                }
            }
        }
    ]
}
kw_res = api_call('adGroupCriteria:mutate', kw_payload)
print(f"Added Keyword: {kw_res['results'][0]['resourceName']}")

# 6. Create 2 Responsive Search Ads
headlines = [
    {"text": "Bateaux Parisiens Tickets", "pinnedField": "HEADLINE_1"},
    {"text": "Official Pier 3 Eiffel Tower"},
    {"text": "Instant Mobile QR Ticket"},
    {"text": "Adults €18, Kids €9 (50% Off)"},
    {"text": "Children Under 4 Free"},
    {"text": "Skip The Ticket Line"},
    {"text": "Book Online & Board Anytime"},
    {"text": "Boats Every 30 Minutes"}
]

descriptions = [
    {"text": "Board at Pier 3 under the Eiffel Tower. Instant mobile QR ticket sent right to your phone."},
    {"text": "Avoid ticket counter lines. Boats depart every 30 minutes from Port de la Bourdonnais."},
    {"text": "Guaranteed boarding with digital barcode tickets. Flexible departures throughout the day."},
    {"text": "Cruise past the Eiffel Tower, Louvre & Notre-Dame with 360° upper deck views."}
]

ads_payload = {
    "operations": [
        {
            "create": {
                "adGroup": ad_group_resource,
                "status": "ENABLED",
                "ad": {
                    "finalUrls": ["https://deals.thecruisedetective.com/bateaux-parisiens-river-cruise-ticket-1"],
                    "responsiveSearchAd": {
                        "headlines": headlines,
                        "descriptions": descriptions,
                        "path1": "bateaux",
                        "path2": "parisiens"
                    }
                }
            }
        },
        {
            "create": {
                "adGroup": ad_group_resource,
                "status": "ENABLED",
                "ad": {
                    "finalUrls": ["https://deals.thecruisedetective.com/bateaux-parisiens-river-cruise-ticket-2"],
                    "responsiveSearchAd": {
                        "headlines": headlines,
                        "descriptions": descriptions,
                        "path1": "bateaux",
                        "path2": "parisiens"
                    }
                }
            }
        }
    ]
}
ads_res = api_call('adGroupAds:mutate', ads_payload)
print(f"Created {len(ads_res['results'])} RSAs with landing pages -1 and -2!")
print("ALL DONE SUCCESSFULLY!")
