#!/usr/bin/env python3
import os
import sys
import copy
import json
from dotenv import load_dotenv

# Load Meta API Credentials from giddyup env
GIDDYUP_DIR = "/Users/adamdimitrov/Development/giddyup"
if os.path.exists(os.path.join(GIDDYUP_DIR, "config.env")):
    load_dotenv(os.path.join(GIDDYUP_DIR, "config.env"))
else:
    load_dotenv(os.path.join(GIDDYUP_DIR, ".env"))

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad

ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
AD_ACCOUNT_ID = os.getenv("META_AD_ACCOUNT_ID", "act_3429452147352518")
APP_ID = os.getenv("META_APP_ID")
APP_SECRET = os.getenv("META_APP_SECRET")

TARGET_URL = "https://deals.thecruisedetective.com/family-pass"
ORIG_CAMPAIGN_ID = "120251632900810010"

def main():
    print(f"Initializing Meta Ads API for account {AD_ACCOUNT_ID}...")
    FacebookAdsApi.init(APP_ID, APP_SECRET, ACCESS_TOKEN)
    account = AdAccount(AD_ACCOUNT_ID)

    # 1. Fetch original campaign
    orig_campaign = Campaign(ORIG_CAMPAIGN_ID).api_get(fields=[
        'name', 'objective', 'buying_type', 'special_ad_categories'
    ])
    new_campaign_name = f"{orig_campaign['name']} [Family Pass LP]"
    print(f"Creating duplicate Campaign: '{new_campaign_name}'...")

    new_campaign = account.create_campaign(params={
        Campaign.Field.name: new_campaign_name,
        Campaign.Field.objective: orig_campaign['objective'],
        Campaign.Field.buying_type: orig_campaign.get('buying_type', 'AUCTION'),
        Campaign.Field.status: 'ACTIVE',
        Campaign.Field.special_ad_categories: orig_campaign.get('special_ad_categories', []),
        'is_adset_budget_sharing_enabled': False,
    })
    new_campaign_id = new_campaign['id']
    print(f" Campaign Created: ID={new_campaign_id}")

    # 2. Fetch original ad sets
    adset_ids = [
        "120251633455600010", # 1-Hour Paris Cruise
        "120251632927380010", # Skip the Dock Line
    ]

    new_adsets = {}
    for asid in adset_ids:
        orig_adset = AdSet(asid).api_get(fields=[
            'name', 'daily_budget', 'billing_event', 'optimization_goal',
            'bid_strategy', 'targeting', 'promoted_object', 'destination_type',
            'attribution_spec'
        ])
        new_set_name = f"{orig_adset['name']} [Family Pass LP]"
        print(f"\nCreating duplicate Ad Set: '{new_set_name}'...")

        adset_params = {
            AdSet.Field.name: new_set_name,
            AdSet.Field.campaign_id: new_campaign_id,
            AdSet.Field.daily_budget: orig_adset['daily_budget'],
            AdSet.Field.billing_event: orig_adset['billing_event'],
            AdSet.Field.optimization_goal: orig_adset['optimization_goal'],
            AdSet.Field.bid_strategy: orig_adset.get('bid_strategy', 'LOWEST_COST_WITHOUT_CAP'),
            AdSet.Field.targeting: orig_adset['targeting'].export_all_data(),
            AdSet.Field.promoted_object: orig_adset['promoted_object'].export_all_data(),
            AdSet.Field.destination_type: orig_adset.get('destination_type', 'WEBSITE'),
            AdSet.Field.status: 'ACTIVE',
        }
        if orig_adset.get('attribution_spec'):
            adset_params[AdSet.Field.attribution_spec] = orig_adset['attribution_spec']

        new_adset = account.create_ad_set(params=adset_params)
        new_adset_id = new_adset['id']
        print(f" Ad Set Created: ID={new_adset_id}")
        new_adsets[asid] = new_adset_id

        # 3. Fetch active ads inside original ad set
        ads = AdSet(asid).get_ads(fields=['id', 'name', 'status', 'creative'])
        active_ads = [ad for ad in ads if ad['status'] == 'ACTIVE']
        print(f"Found {len(active_ads)} active ads to clone for this ad set.")

        for ad in active_ads:
            ad_name = ad['name']
            cid = ad['creative']['id']
            orig_cr = AdCreative(cid).api_get(fields=[
                'name', 'object_story_spec', 'asset_feed_spec', 'degrees_of_freedom_spec'
            ])
            cr_data = orig_cr.export_all_data()

            # Swap destination URL in asset_feed_spec
            asset_feed = copy.deepcopy(cr_data['asset_feed_spec'])
            asset_feed['link_urls'] = [{'website_url': TARGET_URL}]

            new_cr_name = f"{orig_cr.get('name', ad_name)} [Pass LP]"
            cr_params = {
                AdCreative.Field.name: new_cr_name,
                AdCreative.Field.object_story_spec: cr_data['object_story_spec'],
                AdCreative.Field.asset_feed_spec: asset_feed,
            }
            if 'degrees_of_freedom_spec' in cr_data:
                cr_params['degrees_of_freedom_spec'] = cr_data['degrees_of_freedom_spec']

            new_creative = account.create_ad_creative(params=cr_params)
            new_cid = new_creative['id']
            print(f"   Created Creative: ID={new_cid} -> Destination: {TARGET_URL}")

            # Create Ad
            new_ad_name = f"{ad_name.replace('Family LP', 'Pass LP')}"
            new_ad = account.create_ad(params={
                Ad.Field.name: new_ad_name,
                Ad.Field.adset_id: new_adset_id,
                Ad.Field.creative: {'creative_id': new_cid},
                Ad.Field.status: 'ACTIVE',
            })
            print(f"   Created Ad: '{new_ad_name}' (ID={new_ad['id']}) [ACTIVE]")

    print("\n All duplicated campaigns, ad sets, and ads are successfully live!")

if __name__ == "__main__":
    main()
