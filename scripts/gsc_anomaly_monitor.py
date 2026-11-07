#!/usr/bin/env python3
"""
Google Search Console Macro Anomaly Detection Pipeline.
Monitors thecruisedetective.com and budapestadventures.com for macro organic drops.

Compares:
  - Period A (Recent): [T-3 - days] to [T-3] (buffered for 3-day GSC reporting delay)
  - Period B (Baseline): Prior equivalent window

Flags:
  - Click drops >= 20% on pages/queries with significant volume
  - Impression drops >= 25%
  - Average position drops >= 2.0
  - Vanishing queries (traffic in baseline, zero in recent period)
"""

import os
import sys
import argparse
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, List, Tuple, Any, Optional

try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
except ImportError:
    print("Error: Missing Google API dependencies. Install via: pip install google-api-python-client google-auth")
    sys.exit(1)

REPO_DIR = '/Users/adamdimitrov/Development/cruisedetective'
ENV_PATH = os.path.join(REPO_DIR, '.env')
DEFAULT_CREDS_PATH = os.path.join(REPO_DIR, 'credentials', 'gsc_service_account.json')
REPORTS_DIR = os.path.join(REPO_DIR, 'reports')

# Load .env
env_vars = {}
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


def parse_args():
    parser = argparse.ArgumentParser(description="Google Search Console Anomaly Monitor")
    parser.add_argument("--property", type=str, default="", help="GSC site URL (e.g. sc-domain:thecruisedetective.com)")
    parser.add_argument("--days", type=int, default=7, help="Comparison window in days (default: 7)")
    parser.add_argument("--creds", type=str, default="", help="Path to service account JSON")
    parser.add_argument("--min-clicks", type=int, default=5, help="Minimum baseline clicks to trigger an alert")
    parser.add_argument("--force-email", action="store_true", help="Send email even if no critical anomalies are found")
    return parser.parse_args()


def get_service(creds_path: str):
    if not os.path.exists(creds_path):
        print(f"\n[!] Service Account JSON not found at: {creds_path}")
        print("Please follow the setup instructions to create and download the key file.")
        sys.exit(1)
    
    credentials = service_account.Credentials.from_service_account_file(
        creds_path, scopes=SCOPES
    )
    return build('searchconsole', 'v1', credentials=credentials)


def fetch_period_data(service, site_url: str, start_date: str, end_date: str, dimension: str) -> Dict[str, Dict[str, float]]:
    request_body = {
        'startDate': start_date,
        'endDate': end_date,
        'dimensions': [dimension],
        'rowLimit': 5000
    }
    try:
        response = service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
        rows = response.get('rows', [])
        data = {}
        for r in rows:
            key = r['keys'][0]
            data[key] = {
                'clicks': r.get('clicks', 0),
                'impressions': r.get('impressions', 0),
                'ctr': r.get('ctr', 0.0),
                'position': r.get('position', 0.0)
            }
        return data
    except Exception as e:
        print(f"Error querying GSC for {site_url} ({dimension}): {e}")
        return {}


def analyze_anomalies(
    current_data: Dict[str, Dict[str, float]], 
    baseline_data: Dict[str, Dict[str, float]], 
    min_clicks: int = 5,
    min_impressions: int = 50
) -> List[Dict[str, Any]]:
    anomalies = []
    all_keys = set(current_data.keys()).union(set(baseline_data.keys()))

    for key in all_keys:
        curr = current_data.get(key, {'clicks': 0, 'impressions': 0, 'ctr': 0.0, 'position': 0.0})
        base = baseline_data.get(key, {'clicks': 0, 'impressions': 0, 'ctr': 0.0, 'position': 0.0})

        base_clicks = base['clicks']
        curr_clicks = curr['clicks']
        base_impr = base['impressions']
        curr_impr = curr['impressions']
        base_pos = base['position']
        curr_pos = curr['position']

        # Skip low-significance keys
        if base_clicks < min_clicks and base_impr < min_impressions:
            continue

        clicks_diff = curr_clicks - base_clicks
        clicks_pct = (clicks_diff / base_clicks * 100) if base_clicks > 0 else 0.0
        
        impr_diff = curr_impr - base_impr
        impr_pct = (impr_diff / base_impr * 100) if base_impr > 0 else 0.0

        pos_diff = curr_pos - base_pos if (base_pos > 0 and curr_pos > 0) else 0.0

        issues = []

        # Vanished
        if base_clicks >= min_clicks and curr_clicks == 0 and curr_impr == 0:
            issues.append(f"VANISHED (Lost all {base_clicks:.0f} clicks and {base_impr:.0f} impr)")
        # Click drop >= 20%
        elif base_clicks >= min_clicks and clicks_pct <= -20.0:
            issues.append(f"CLICK_DROP ({clicks_pct:.1f}%: {base_clicks:.0f} -> {curr_clicks:.0f})")

        # Impression drop >= 25%
        if base_impr >= min_impressions and impr_pct <= -25.0:
            issues.append(f"IMPRESSION_DROP ({impr_pct:.1f}%: {base_impr:.0f} -> {curr_impr:.0f})")

        # Rank drop >= 2.0
        if base_pos > 0 and curr_pos > 0 and pos_diff >= 2.0 and base_clicks >= min_clicks:
            issues.append(f"RANK_DROP (+{pos_diff:.1f} spots worse: #{base_pos:.1f} -> #{curr_pos:.1f})")

        if issues:
            anomalies.append({
                'key': key,
                'issues': issues,
                'base_clicks': base_clicks,
                'curr_clicks': curr_clicks,
                'clicks_pct': clicks_pct,
                'base_impr': base_impr,
                'curr_impr': curr_impr,
                'impr_pct': impr_pct,
                'base_pos': base_pos,
                'curr_pos': curr_pos,
                'pos_diff': pos_diff,
            })

    # Sort anomalies by magnitude of lost clicks, then lost impressions
    anomalies.sort(key=lambda x: (x['curr_clicks'] - x['base_clicks'], x['curr_impr'] - x['base_impr']))
    return anomalies


def format_report_markdown(site_url: str, p_curr: Tuple[str, str], p_base: Tuple[str, str], page_anomalies: List[Dict], query_anomalies: List[Dict]) -> str:
    lines = [
        f"# GSC Anomaly Audit: {site_url}",
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Recent Period (Buffered)**: {p_curr[0]} to {p_curr[1]}",
        f"**Baseline Period**: {p_base[0]} to {p_base[1]}",
        "",
        "---",
        ""
    ]

    # Page Anomalies
    lines.append(f"## Page-Level Anomalies ({len(page_anomalies)} detected)")
    if not page_anomalies:
        lines.append("*No significant page-level drops detected.*")
    else:
        lines.append("| Page | Clicks (Base -> Curr) | Impress. (Base -> Curr) | Avg Pos | Issues |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for a in page_anomalies[:20]:
            clean_url = a['key'].replace(site_url.replace('sc-domain:', 'https://'), '/')
            pos_str = f"#{a['base_pos']:.1f} -> #{a['curr_pos']:.1f}" if a['base_pos'] > 0 else "N/A"
            issues_str = "<br>".join(a['issues'])
            lines.append(f"| `{clean_url}` | {a['base_clicks']:.0f} -> {a['curr_clicks']:.0f} ({a['clicks_pct']:+.0f}%) | {a['base_impr']:.0f} -> {a['curr_impr']:.0f} ({a['impr_pct']:+.0f}%) | {pos_str} | {issues_str} |")
    
    lines.append("")
    lines.append(f"## Query-Level Anomalies ({len(query_anomalies)} detected)")
    if not query_anomalies:
        lines.append("*No significant query-level drops detected.*")
    else:
        lines.append("| Query | Clicks (Base -> Curr) | Impress. (Base -> Curr) | Avg Pos | Issues |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for a in query_anomalies[:25]:
            pos_str = f"#{a['base_pos']:.1f} -> #{a['curr_pos']:.1f}" if a['base_pos'] > 0 else "N/A"
            issues_str = "<br>".join(a['issues'])
            lines.append(f"| **{a['key']}** | {a['base_clicks']:.0f} -> {a['curr_clicks']:.0f} ({a['clicks_pct']:+.0f}%) | {a['base_impr']:.0f} -> {a['curr_impr']:.0f} ({a['impr_pct']:+.0f}%) | {pos_str} | {issues_str} |")

    lines.append("")
    return "\n".join(lines)


def send_email_alert(subject: str, markdown_content: str, to_email: str):
    gmail_user = env_vars.get('GMAIL_USER')
    gmail_app_password = env_vars.get('GMAIL_APP_PASSWORD')
    
    if not gmail_user or not gmail_app_password:
        print("[!] GMAIL_USER or GMAIL_APP_PASSWORD not set in .env. Skipping email notification.")
        return

    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = gmail_user
    msg['To'] = to_email

    # Plain text version
    part1 = MIMEText(markdown_content, 'plain')
    msg.attach(part1)

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, [to_email], msg.as_string())
        server.quit()
        print(f"[+] Alert email sent to {to_email}")
    except Exception as e:
        print(f"[!] Failed to send email alert: {e}")


def main():
    args = parse_args()
    creds_path = args.creds or env_vars.get('GSC_CREDENTIALS_PATH') or DEFAULT_CREDS_PATH
    alert_email = env_vars.get('ALERT_EMAIL', 'adam.dimitrov.business@gmail.com')

    if not os.path.exists(creds_path):
        print("=" * 70)
        print("GOOGLE SEARCH CONSOLE SERVICE ACCOUNT CREDENTIALS MISSING")
        print("=" * 70)
        print(f"Target path: {creds_path}")
        print("\nPlease follow these 3 steps to activate automated monitoring:")
        print("1. Enable Google Search Console API in Google Cloud Console.")
        print("2. Create a Service Account, generate a JSON key, and save it to:")
        print(f"   {creds_path}")
        print("3. In Google Search Console (Settings -> Users and permissions),")
        print("   add the service account email with 'Restricted' permissions.")
        print("=" * 70)
        sys.exit(0)

    service = get_service(creds_path)

    # Determine site properties to audit
    site_properties = []
    if args.property:
        site_properties = [args.property]
    elif env_vars.get('GSC_PROPERTIES'):
        site_properties = [p.strip() for p in env_vars.get('GSC_PROPERTIES').split(',')]
    else:
        # Discover accessible sites
        try:
            sites_resp = service.sites().list().execute()
            site_entries = sites_resp.get('siteEntry', [])
            site_properties = [s['siteUrl'] for s in site_entries if s.get('permissionLevel') != 'siteRestrictedUserDeleted']
            if not site_properties:
                site_properties = ['sc-domain:thecruisedetective.com']
        except Exception as e:
            site_properties = ['sc-domain:thecruisedetective.com']

    # Date calculations with 3-day latency buffer
    # GSC data for today T is only reliable up to T-3
    today = datetime.now().date()
    curr_end = today - timedelta(days=3)
    curr_start = curr_end - timedelta(days=args.days)
    base_end = curr_start
    base_start = base_end - timedelta(days=args.days)

    p_curr = (curr_start.isoformat(), curr_end.isoformat())
    p_base = (base_start.isoformat(), base_end.isoformat())

    print(f"\n[GSC Anomaly Monitor] Running {args.days}-Day Window Audit")
    print(f"Current Buffered Window: {p_curr[0]} to {p_curr[1]}")
    print(f"Baseline Window:         {p_base[0]} to {p_base[1]}\n")

    os.makedirs(REPORTS_DIR, exist_ok=True)

    for site_url in site_properties:
        print(f"--> Auditing {site_url}...")
        
        # 1. Page Analysis
        curr_pages = fetch_period_data(service, site_url, p_curr[0], p_curr[1], 'page')
        base_pages = fetch_period_data(service, site_url, p_base[0], p_base[1], 'page')
        page_anomalies = analyze_anomalies(curr_pages, base_pages, min_clicks=args.min_clicks)

        # 2. Query Analysis
        curr_queries = fetch_period_data(service, site_url, p_curr[0], p_curr[1], 'query')
        base_queries = fetch_period_data(service, site_url, p_base[0], p_base[1], 'query')
        query_anomalies = analyze_anomalies(curr_queries, base_queries, min_clicks=args.min_clicks)

        # 3. Report
        report_md = format_report_markdown(site_url, p_curr, p_base, page_anomalies, query_anomalies)
        
        # Save to disk
        slug = site_url.replace('https://', '').replace('sc-domain:', '').replace('/', '_')
        report_filename = f"gsc_audit_{slug}_{curr_end.isoformat()}.md"
        report_path = os.path.join(REPORTS_DIR, report_filename)
        with open(report_path, 'w') as f:
            f.write(report_md)
        print(f"Saved audit report: {report_path}")

        # Console Summary
        print(f"    Page anomalies:  {len(page_anomalies)}")
        print(f"    Query anomalies: {len(query_anomalies)}")

        # Alert if critical drops exist
        has_critical = len(page_anomalies) > 0 or len(query_anomalies) > 0
        if has_critical or args.force_email:
            subject = f"[ALERT] GSC Drops Detected ({site_url}) — {curr_end.isoformat()}"
            if not has_critical:
                subject = f"[INFO] GSC Audit Clean ({site_url}) — {curr_end.isoformat()}"
            send_email_alert(subject, report_md, alert_email)
        else:
            print("    Status: Clean. No critical anomalies meeting volume thresholds.")


if __name__ == '__main__':
    main()
