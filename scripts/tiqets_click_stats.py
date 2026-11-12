#!/usr/bin/env python3
"""Tiqets click-through stats from the server-side /go/tiqets counter.

Usage:  python3 scripts/tiqets_click_stats.py [YYYY-MM-DD]   (default: today, UTC)

Reads the day's counters from Upstash Redis (written by api/go-tiqets.js) and
joins the Google click ids to Google Ads campaigns via click_view, so you get
per campaign: ad clicks, visitors who clicked through to Tiqets, Tiqets CTR.

Needs in .env: KV_REST_API_URL, KV_REST_API_TOKEN (from `vercel env pull` after
the Upstash integration is added) and the existing GOOGLE_ADS_* credentials.

Day boundaries: the counter uses UTC days, Google Ads uses the account's time
zone, so numbers near midnight can shift by a few clicks between days.
"""
import collections
import datetime
import json
import os
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADS_API = 'https://googleads.googleapis.com/v26'


def load_env():
    env = {}
    path = os.path.join(ROOT, '.env')
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip().strip('"')
    env.update({k: v for k, v in os.environ.items() if k.startswith(('KV_', 'GOOGLE_ADS_'))})
    return env


def redis(env, *cmd):
    req = urllib.request.Request(
        env['KV_REST_API_URL'].rstrip('/'),
        data=json.dumps(list(cmd)).encode(),
        headers={'Authorization': 'Bearer ' + env['KV_REST_API_TOKEN'], 'Content-Type': 'application/json'},
    )
    return json.load(urllib.request.urlopen(req))['result']


def ads_session(env):
    tok = json.load(urllib.request.urlopen(urllib.request.Request(
        'https://oauth2.googleapis.com/token',
        data=urllib.parse.urlencode({
            'client_id': env['GOOGLE_ADS_CLIENT_ID'],
            'client_secret': env['GOOGLE_ADS_CLIENT_SECRET'],
            'refresh_token': env['GOOGLE_ADS_REFRESH_TOKEN'],
            'grant_type': 'refresh_token',
        }).encode())))['access_token']
    cid = env['GOOGLE_ADS_CUSTOMER_ID'].replace('-', '')
    headers = {'Authorization': 'Bearer ' + tok, 'developer-token': env['GOOGLE_ADS_DEVELOPER_TOKEN'],
               'Content-Type': 'application/json'}

    def search(query):
        out, page = [], None
        while True:
            body = {'query': query}
            if page:
                body['pageToken'] = page
            r = urllib.request.Request(f'{ADS_API}/customers/{cid}/googleAds:search',
                                       data=json.dumps(body).encode(), headers=headers)
            res = json.load(urllib.request.urlopen(r))
            out += res.get('results', [])
            page = res.get('nextPageToken')
            if not page:
                return out
    return search


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.utcnow().strftime('%Y-%m-%d')
    env = load_env()
    if not env.get('KV_REST_API_URL'):
        sys.exit('KV_REST_API_URL / KV_REST_API_TOKEN missing in .env (run `vercel env pull .env.kv` and copy them).')

    key = f'tqc:{day}'
    flat = redis(env, 'HGETALL', key) or []
    counts = {flat[i]: int(flat[i + 1]) for i in range(0, len(flat), 2)}
    ids = set(redis(env, 'SMEMBERS', key + ':ids') or [])

    print(f'== Tiqets clicks on {day} (UTC), counted on our server')
    print(f"total {counts.get('total', 0)} | from ad visitors {counts.get('ad', 0)} "
          f"({len(ids)} distinct ad clicks) | organic {counts.get('organic', 0)} | bots skipped {counts.get('bot', 0)}")

    for prefix, title in (('page:', 'By page'), ('pl:', 'By placement')):
        rows = sorted(((k[len(prefix):], v) for k, v in counts.items() if k.startswith(prefix)), key=lambda r: -r[1])
        if rows:
            print(f'\n== {title}')
            for name, n in rows:
                print(f'{n:5}  {name}')

    if not env.get('GOOGLE_ADS_REFRESH_TOKEN'):
        return
    search = ads_session(env)
    d = datetime.date.fromisoformat(day)
    prev = (d - datetime.timedelta(days=1)).isoformat()

    # Which campaign each Google click id belongs to (click may be from the day before).
    gclid_campaign = {}
    for dd in (prev, day):
        for x in search(f"SELECT click_view.gclid, campaign.name FROM click_view WHERE segments.date = '{dd}'"):
            gclid_campaign[x['clickView']['gclid']] = x['campaign']['name']

    ad_clicks = collections.Counter()
    for x in search(f"SELECT campaign.name, metrics.clicks FROM campaign WHERE segments.date = '{day}' AND metrics.clicks > 0"):
        ad_clicks[x['campaign']['name']] += int(x['metrics']['clicks'])

    through = collections.Counter()
    for item in ids:
        typ, _, cid = item.partition(':')
        through[gclid_campaign.get(cid, '(gbraid/wbraid or unmatched)') if typ == 'gclid' else '(gbraid/wbraid or unmatched)'] += 1

    print(f'\n== By campaign: ad clicks vs. visitors who clicked through to Tiqets')
    print(f"{'ad clicks':>9} {'to Tiqets':>9} {'CTR':>6}  campaign")
    for name in sorted(set(ad_clicks) | set(through), key=lambda n: -ad_clicks.get(n, 0)):
        a, t = ad_clicks.get(name, 0), through.get(name, 0)
        ctr = f'{100 * t / a:5.1f}%' if a else '    -'
        print(f'{a:9} {t:9} {ctr:>6}  {name}')
    a, t = sum(ad_clicks.values()), sum(through.values())
    print(f"{a:9} {t:9} {(f'{100 * t / a:5.1f}%' if a else '    -'):>6}  TOTAL")


if __name__ == '__main__':
    main()
