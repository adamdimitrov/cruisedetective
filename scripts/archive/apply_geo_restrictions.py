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
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        print(f"Error on query: {e.code}", e.read().decode(), file=sys.stderr)
        raise

# Countries definition:
# US: 2840, GB: 2826, CA: 2124, AU: 2036, NZ: 2554, IE: 2372, FR: 2250, NL: 2528
# DE: 2276, AT: 2040, CH: 2756, BE: 2056, ES: 2724, IT: 2380

COUNTRIES = {
    'EN_PARIS': ['2840', '2826', '2124', '2036', '2554', '2372', '2250'],
    'EN_AMSTERDAM': ['2840', '2826', '2124', '2036', '2554', '2372', '2528'],
    'DE': ['2276', '2040', '2756', '2250'],
    'FR': ['2250', '2056', '2756', '2124'],
    'ES': ['2724', '2250'],
    'IT': ['2380', '2756', '2250'],
    'NL': ['2528', '2056', '2250']
}

# 1. Fetch all target campaigns
q = '''
SELECT
  campaign.id,
  campaign.name,
  campaign.status,
  campaign.geo_target_type_setting.positive_geo_target_type
FROM campaign
WHERE campaign.status IN ('ENABLED', 'PAUSED')
ORDER BY campaign.name
'''
res = query_google_ads(q)
campaigns = [row['campaign'] for row in res.get('results', []) if row['campaign']['name'].startswith('[BOF]') or row['campaign']['name'].startswith('[TEST]')]

print(f"Found {len(campaigns)} target BOF/TEST campaigns.")

for c in campaigns:
    cid = c['id']
    name = c['name']
    c_res_name = f"customers/{customer_id}/campaigns/{cid}"

    # Determine geo bucket
    if '(EN)' in name or 'Brand (Phrase €0.25)' in name or 'High Intent' in name:
        if 'Amsterdam' in name:
            target_geo = COUNTRIES['EN_AMSTERDAM']
            geo_desc = "Anglosphere + NL"
        else:
            target_geo = COUNTRIES['EN_PARIS']
            geo_desc = "Anglosphere + FR"
    elif '(DE)' in name:
        target_geo = COUNTRIES['DE']
        geo_desc = "DE, AT, CH + FR"
    elif '(FR)' in name:
        target_geo = COUNTRIES['FR']
        geo_desc = "FR, BE, CH, CA"
    elif '(ES)' in name:
        target_geo = COUNTRIES['ES']
        geo_desc = "ES + FR"
    elif '(IT)' in name:
        target_geo = COUNTRIES['IT']
        geo_desc = "IT, CH + FR"
    elif '(NL)' in name:
        target_geo = COUNTRIES['NL']
        geo_desc = "NL, BE + FR"
    else:
        print(f"Skipping unrecognized campaign: {name}")
        continue

    print(f"\nProcessing {name} (ID: {cid}) -> {geo_desc} (PositiveGeo: PRESENCE)")

    # 1. Update Campaign Setting to PRESENCE
    update_payload = {
        "operations": [
            {
                "updateMask": "geoTargetTypeSetting.positiveGeoTargetType",
                "update": {
                    "resourceName": c_res_name,
                    "geoTargetTypeSetting": {
                        "positiveGeoTargetType": "PRESENCE"
                    }
                }
            }
        ]
    }
    try:
        api_call('campaigns:mutate', update_payload)
        print(f"  ✓ Set positiveGeoTargetType to PRESENCE")
    except Exception as e:
        print(f"  ✗ Failed to update geoTargetTypeSetting: {e}")

    # 2. Add location criteria
    crit_operations = []
    for gid in target_geo:
        crit_operations.append({
            "create": {
                "campaign": c_res_name,
                "location": {
                    "geoTargetConstant": f"geoTargetConstants/{gid}"
                }
            }
        })

    try:
        crit_res = api_call('campaignCriteria:mutate', {"operations": crit_operations})
        print(f"  ✓ Added {len(crit_res.get('results', []))} country criteria: {target_geo}")
    except Exception as e:
        print(f"  ✗ Failed to add campaign criteria: {e}")

print("\nALL CAMPAIGNS SUCCESSFULLY RESTRICTED!")
