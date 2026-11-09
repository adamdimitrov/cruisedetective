import time
import urllib.request
import urllib.parse
import json
import sys

with open('/Users/adamdimitrov/Development/cruisedetective/.env') as f:
    env_vars = dict(line.strip().split('=', 1) for line in f if '=' in line and not line.startswith('#'))

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
dev_token = env_vars.get('GOOGLE_ADS_DEVELOPER_TOKEN')

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

def duplicate_campaign(src_camp_id, new_camp_name, new_final_url, status="PAUSED"):
    print(f"\n==================================================")
    print(f"Cloning Campaign {src_camp_id} -> '{new_camp_name}'")
    print(f"Target URL: {new_final_url}")
    print(f"==================================================")

    # 1. Fetch original campaign info
    q_camp = f"""
    SELECT
      campaign.id, campaign.name, campaign.status, campaign.bidding_strategy_type,
      campaign.target_spend.cpc_bid_ceiling_micros, campaign.campaign_budget,
      campaign.network_settings.target_google_search, campaign.network_settings.target_search_network,
      campaign.network_settings.target_content_network, campaign.geo_target_type_setting.positive_geo_target_type
    FROM campaign WHERE campaign.id = {src_camp_id}
    """
    url_search = f'https://googleads.googleapis.com/v26/customers/{customer_id}/googleAds:search'
    r = urllib.request.Request(url_search, data=json.dumps({'query': q_camp}).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(r) as resp:
        camp_res = json.loads(resp.read().decode())['results'][0]['campaign']

    cpc_ceiling = camp_res.get('targetSpend', {}).get('cpcBidCeilingMicros')

    # Fetch budget amount
    budget_rn = camp_res['campaignBudget']
    q_b = f"SELECT campaign_budget.amount_micros FROM campaign_budget WHERE campaign_budget.resource_name = '{budget_rn}'"
    r = urllib.request.Request(url_search, data=json.dumps({'query': q_b}).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(r) as resp:
        budget_micros = json.loads(resp.read().decode())['results'][0]['campaignBudget']['amountMicros']

    # 2. Create Budget
    b_payload = {
        "operations": [{
            "create": {
                "name": f"{new_camp_name} Budget " + str(int(time.time())),
                "amountMicros": budget_micros,
                "deliveryMethod": "STANDARD"
            }
        }]
    }
    b_res = api_call('campaignBudgets:mutate', b_payload)
    new_budget_rn = b_res['results'][0]['resourceName']
    print(f"  ✓ Budget created: {new_budget_rn} ({int(budget_micros)/1e6:.2f} EUR/day)")

    # 3. Create Campaign
    c_create = {
        "name": new_camp_name,
        "status": status,
        "advertisingChannelType": "SEARCH",
        "campaignBudget": new_budget_rn,
        "networkSettings": {
            "targetGoogleSearch": True,
            "targetSearchNetwork": False,
            "targetContentNetwork": False
        },
        "geoTargetTypeSetting": {
            "positiveGeoTargetType": "PRESENCE"
        },
        "containsEuPoliticalAdvertising": "DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING"
    }
    if cpc_ceiling:
        c_create["targetSpend"] = {"cpcBidCeilingMicros": cpc_ceiling}
    else:
        c_create["targetSpend"] = {}

    c_payload = {"operations": [{"create": c_create}]}
    c_res = api_call('campaigns:mutate', c_payload)
    new_camp_rn = c_res['results'][0]['resourceName']
    print(f"  ✓ Campaign created: {new_camp_rn}")

    # 4. Copy Geo Targets (Campaign Criteria)
    q_geo = f"SELECT campaign_criterion.location.geo_target_constant FROM campaign_criterion WHERE campaign.id = {src_camp_id} AND campaign_criterion.type = 'LOCATION'"
    r = urllib.request.Request(url_search, data=json.dumps({'query': q_geo}).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(r) as resp:
        geo_res = json.loads(resp.read().decode()).get('results', [])

    geo_ops = []
    for g in geo_res:
        geo_constant = g['campaignCriterion']['location']['geoTargetConstant']
        geo_ops.append({
            "create": {
                "campaign": new_camp_rn,
                "location": {"geoTargetConstant": geo_constant}
            }
        })
    if geo_ops:
        api_call('campaignCriteria:mutate', {"operations": geo_ops})
        print(f"  ✓ Added {len(geo_ops)} Geo Locations (PRESENCE)")

    # 5. Fetch Original Ad Group
    q_ag = f"SELECT ad_group.id, ad_group.name, ad_group.cpc_bid_micros FROM ad_group WHERE campaign.id = {src_camp_id} LIMIT 1"
    r = urllib.request.Request(url_search, data=json.dumps({'query': q_ag}).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(r) as resp:
        orig_ag = json.loads(resp.read().decode())['results'][0]['adGroup']
    
    orig_ag_id = orig_ag['id']
    ag_create = {
        "name": orig_ag['name'],
        "campaign": new_camp_rn,
        "status": "ENABLED",
        "type": "SEARCH_STANDARD"
    }
    if orig_ag.get('cpcBidMicros'):
        ag_create['cpcBidMicros'] = orig_ag['cpcBidMicros']
    
    ag_res = api_call('adGroups:mutate', {"operations": [{"create": ag_create}]})
    new_ag_rn = ag_res['results'][0]['resourceName']
    print(f"  ✓ Ad Group created: {new_ag_rn}")

    # 6. Copy Keywords
    q_kw = f"SELECT ad_group_criterion.keyword.text, ad_group_criterion.keyword.match_type FROM ad_group_criterion WHERE ad_group.id = {orig_ag_id} AND ad_group_criterion.type = 'KEYWORD'"
    r = urllib.request.Request(url_search, data=json.dumps({'query': q_kw}).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(r) as resp:
        kw_res = json.loads(resp.read().decode()).get('results', [])

    kw_ops = []
    for k in kw_res:
        kw_info = k['adGroupCriterion']['keyword']
        kw_ops.append({
            "create": {
                "adGroup": new_ag_rn,
                "status": "ENABLED",
                "keyword": {
                    "text": kw_info['text'],
                    "matchType": kw_info['matchType']
                }
            }
        })
    if kw_ops:
        api_call('adGroupCriteria:mutate', {"operations": kw_ops})
        print(f"  ✓ Added {len(kw_ops)} Keywords")

    # 7. Copy RSA Ad with New Final URL
    q_ad = f"""
    SELECT
      ad_group_ad.ad.responsive_search_ad.headlines,
      ad_group_ad.ad.responsive_search_ad.descriptions,
      ad_group_ad.ad.responsive_search_ad.path1,
      ad_group_ad.ad.responsive_search_ad.path2
    FROM ad_group_ad
    WHERE ad_group.id = {orig_ag_id} AND ad_group_ad.status = 'ENABLED'
    LIMIT 1
    """
    r = urllib.request.Request(url_search, data=json.dumps({'query': q_ad}).encode('utf-8'), headers=headers, method='POST')
    with urllib.request.urlopen(r) as resp:
        orig_ad = json.loads(resp.read().decode())['results'][0]['adGroupAd']['ad']['responsiveSearchAd']

    clean_headlines = []
    for h in orig_ad['headlines']:
        item = {"text": h['text']}
        if h.get('pinnedField'):
            item["pinnedField"] = h['pinnedField']
        clean_headlines.append(item)

    clean_descriptions = []
    for d in orig_ad['descriptions']:
        item = {"text": d['text']}
        if d.get('pinnedField'):
            item["pinnedField"] = d['pinnedField']
        clean_descriptions.append(item)

    ad_create = {
        "finalUrls": [new_final_url],
        "responsiveSearchAd": {
            "headlines": clean_headlines,
            "descriptions": clean_descriptions,
            "path1": orig_ad.get('path1', ''),
            "path2": orig_ad.get('path2', '')
        }
    }
    ad_op = {
        "operations": [{
            "create": {
                "adGroup": new_ag_rn,
                "status": "ENABLED",
                "ad": ad_create
            }
        }]
    }
    ad_res = api_call('adGroupAds:mutate', ad_op)
    new_ad_rn = ad_res['results'][0]['resourceName']
    print(f"  ✓ RSA Ad created with Final URL: {new_final_url}")
    print(f"  ✓ Campaign Ready: {new_camp_rn} (Status: {status})")

if __name__ == '__main__':
    # 1. Duplicate Sightseeing Campaign
    duplicate_campaign(
        src_camp_id=24392538626,
        new_camp_name="[BOF] Paris - Sightseeing Cruise (EN) - Flagship SEO LP",
        new_final_url="https://www.thecruisedetective.com/seine-river-cruises-paris",
        status="PAUSED"
    )

    # 2. Duplicate Dinner Campaign
    duplicate_campaign(
        src_camp_id=24385060719,
        new_camp_name="[BOF] Paris - Dinner Cruise (EN) - Flagship SEO LP",
        new_final_url="https://www.thecruisedetective.com/dinner-cruises-paris",
        status="PAUSED"
    )
