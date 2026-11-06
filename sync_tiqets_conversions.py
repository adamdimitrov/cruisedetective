#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import os
import re
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

REPO_DIR = '/Users/adamdimitrov/Development/cruisedetective'
ENV_PATH = os.path.join(REPO_DIR, '.env')
STATE_FILE = os.path.join(REPO_DIR, 'uploaded_orders.json')

PRODUCT_NAMES = {
    973977: "Bateaux Parisiens — Seine Sightseeing Cruise",
    982924: "Bateaux Mouches — Paris Dinner Cruise",
    982823: "Bateaux Mouches — Seine Sightseeing Cruise",
    973666: "Amsterdam Canal Cruise",
    975431: "London Thames River Cruise",
    1071588: "Theo Trattoria — Italian Dinner Cruise",
    1052475: "Paris en Scène — Bistro Dinner Cruise",
    974358: "Bateaux Parisiens — Gourmet Dinner Cruise",
    1049009: "Le Diamant Bleu — Luxury Dinner Cruise",
    1085706: "Maxim's de Paris — Seine Dinner Cruise",
}

# Load .env
env_vars = {}
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env_vars[k.strip()] = v.strip()

client_id = env_vars.get('GOOGLE_ADS_CLIENT_ID', '')
client_secret = env_vars.get('GOOGLE_ADS_CLIENT_SECRET', '')
refresh_token = env_vars.get('GOOGLE_ADS_REFRESH_TOKEN', '')
customer_id = env_vars.get('GOOGLE_ADS_CUSTOMER_ID', '').replace('-', '')
conversion_action_id = env_vars.get('GOOGLE_ADS_CONVERSION_ACTION_ID', '7715980036')
tiqets_api_key = env_vars.get('TIQETS_API_KEY', '')

alert_email = env_vars.get('ALERT_EMAIL', 'adam.dimitrov.business@gmail.com')
gmail_user = env_vars.get('GMAIL_USER', 'adam.dimitrov.business@gmail.com')
gmail_app_password = env_vars.get('GMAIL_APP_PASSWORD', '')
gmail_client_id = env_vars.get('GMAIL_CLIENT_ID', '')
gmail_client_secret = env_vars.get('GMAIL_CLIENT_SECRET', '')
gmail_refresh_token = env_vars.get('GMAIL_REFRESH_TOKEN', '')

# Load state
uploaded_orders = {}
if os.path.exists(STATE_FILE):
    try:
        with open(STATE_FILE, 'r') as f:
            uploaded_orders = json.load(f)
    except Exception:
        uploaded_orders = {}


def get_google_access_token():
    data = urllib.parse.urlencode({
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())['access_token']


def get_gmail_access_token():
    data = urllib.parse.urlencode({
        'client_id': gmail_client_id,
        'client_secret': gmail_client_secret,
        'refresh_token': gmail_refresh_token,
        'grant_type': 'refresh_token'
    }).encode('utf-8')
    req = urllib.request.Request('https://oauth2.googleapis.com/token', data=data, method='POST')
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())['access_token']


def extract_click_id(campaign_str):
    if not campaign_str or not isinstance(campaign_str, str):
        return None
    # Match --gclid-<value>, --wbraid-<value>, --gbraid-<value>, or --fbclid-<value>
    m = re.search(r'(gclid|wbraid|gbraid|fbclid)-([a-zA-Z0-9_-]+)', campaign_str, re.IGNORECASE)
    if m:
        cid_type = m.group(1).lower()
        cid_val = m.group(2).split('--')[0].split('&')[0].split('?')[0].strip()
        if cid_val and not re.match(r'^(organic|direct|referral)$', cid_val, re.IGNORECASE):
            return {'type': cid_type, 'value': cid_val}
    return None


def classify_ad_attribution(order):
    campaign_str = order.get('campaign_name') or ''
    sitebrand = order.get('sitebrand') or ''
    click_info = extract_click_id(campaign_str)

    base_Placement = campaign_str.split('--')[0] if campaign_str else 'N/A'

    if click_info:
        ctype = click_info['type']
        if ctype in ('gclid', 'wbraid', 'gbraid'):
            return {
                'is_ad': True,
                'source_label': f'Google Ads ({ctype.upper()})',
                'placement': base_Placement,
                'click_info': click_info
            }
        elif ctype == 'fbclid':
            return {
                'is_ad': True,
                'source_label': 'Meta Ads (FBCLID)',
                'placement': base_Placement,
                'click_info': click_info
            }

    # Paid LP subdomain attribution even when iOS ITP / adblock strips click ID
    if sitebrand.lower() == 'deals.cruisedetective.com':
        return {
            'is_ad': True,
            'source_label': 'Paid Landing Page (deals.cruisedetective.com — Click ID stripped by browser)',
            'placement': base_Placement,
            'click_info': None
        }

    return {'is_ad': False, 'source_label': 'Organic / SEO', 'placement': base_Placement, 'click_info': None}


def send_booking_email_alert(order, attribution, google_sync_note):
    order_id = str(order.get('order_reference_id'))
    product_id = order.get('product_id')
    product_name = PRODUCT_NAMES.get(product_id, f"Tiqets Product #{product_id}")
    tickets = order.get('number_of_tickets', 1)
    gross_val = float(order.get('sale_order_value') or 0.0)
    commission = float(order.get('estimated_commission') or 0.0)
    currency = order.get('currency', 'EUR')
    visit_date = order.get('visit_date', 'N/A')
    created_at = order.get('order_created_timestamp', 'N/A')
    status = order.get('order_status', 'done')
    source_label = attribution['source_label']
    placement = attribution['placement']
    click_info = attribution['click_info']
    click_str = f"{click_info['type']}={click_info['value']}" if click_info else "None (Direct on Paid LP)"

    subject = f"💰 New Tiqets Ad Booking: +€{commission:.2f} Profit (Order #{order_id} | {tickets}x Tickets)"

    text_body = (
        f"New Tiqets Ad Booking Detected!\n"
        f"========================================\n"
        f"Order Reference : #{order_id}\n"
        f"Order Status    : {status.upper()}\n"
        f"Product         : {product_name} (ID: {product_id})\n"
        f"Tickets         : {tickets}\n"
        f"Visit Date      : {visit_date}\n"
        f"Gross Sale      : {currency} {gross_val:.2f}\n"
        f"Net Commission  : {currency} {commission:.2f}\n"
        f"----------------------------------------\n"
        f"Ad Source       : {source_label}\n"
        f"LP CTA Tag      : {placement}\n"
        f"Click ID        : {click_str}\n"
        f"Google Ads Sync : {google_sync_note}\n"
        f"Timestamp (UTC) : {created_at}\n"
    )

    html_body = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 560px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; overflow: hidden;">
      <div style="background: #0f172a; color: #ffffff; padding: 20px 24px;">
        <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #38bdf8; font-weight: 700;">Cruise Detective • Ad Conversion Alert</div>
        <h2 style="margin: 6px 0 0; font-size: 22px; color: #ffffff;">+€{commission:.2f} Net Commission</h2>
        <div style="font-size: 13px; color: #94a3b8; margin-top: 4px;">Order #{order_id} • {status.upper()}</div>
      </div>
      <div style="padding: 20px 24px; background: #ffffff;">
        <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
          <tr>
            <td style="padding: 8px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Product</td>
            <td style="padding: 8px 0; font-weight: 600; color: #0f172a; text-align: right; border-bottom: 1px solid #f1f5f9;">{product_name}</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Tickets & Visit Date</td>
            <td style="padding: 8px 0; font-weight: 600; color: #0f172a; text-align: right; border-bottom: 1px solid #f1f5f9;">{tickets}x Tickets • {visit_date}</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Gross Ticket Sale</td>
            <td style="padding: 8px 0; font-weight: 600; color: #0f172a; text-align: right; border-bottom: 1px solid #f1f5f9;">€{gross_val:.2f} {currency}</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Your Net Profit</td>
            <td style="padding: 8px 0; font-weight: 700; color: #16a34a; font-size: 16px; text-align: right; border-bottom: 1px solid #f1f5f9;">+€{commission:.2f} {currency}</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Ad Traffic Source</td>
            <td style="padding: 8px 0; font-weight: 600; color: #2563eb; text-align: right; border-bottom: 1px solid #f1f5f9;">{source_label}</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">LP Button / Placement</td>
            <td style="padding: 8px 0; font-family: monospace; color: #0f172a; text-align: right; border-bottom: 1px solid #f1f5f9;">{placement}</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Google Ads API Sync</td>
            <td style="padding: 8px 0; color: #0f172a; text-align: right; border-bottom: 1px solid #f1f5f9;">{google_sync_note}</td>
          </tr>
          <tr>
            <td style="padding: 8px 0; color: #64748b;">Order Timestamp</td>
            <td style="padding: 8px 0; color: #64748b; font-size: 12px; text-align: right;">{created_at}</td>
          </tr>
        </table>
      </div>
    </div>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = f"Cruise Detective Alerts <{gmail_user}>"
    msg['To'] = alert_email
    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    # Method 1: Gmail SMTP App Password (if configured in .env)
    if gmail_app_password:
        try:
            clean_pass = gmail_app_password.replace(' ', '')
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(gmail_user, clean_pass)
                server.sendmail(gmail_user, [alert_email], msg.as_string())
            print(f"[EMAIL-SMTP] Sent booking alert for #{order_id} to {alert_email}")
            return True
        except Exception as e:
            print(f"[EMAIL-SMTP ERROR] {e} — falling back to Gmail OAuth API...")

    # Method 2: Gmail API via existing OAuth Refresh Token (zero password needed)
    if gmail_client_id and gmail_client_secret and gmail_refresh_token:
        try:
            g_token = get_gmail_access_token()
            raw_msg = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            req = urllib.request.Request(
                'https://gmail.googleapis.com/gmail/v1/users/me/messages/send',
                data=json.dumps({'raw': raw_msg}).encode('utf-8'),
                headers={
                    'Authorization': f'Bearer {g_token}',
                    'Content-Type': 'application/json'
                },
                method='POST'
            )
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode())
                print(f"[EMAIL-API] Sent booking alert for #{order_id} to {alert_email} (Msg ID: {res_data.get('id')})")
                return True
        except Exception as e:
            print(f"[EMAIL-API ERROR] Failed sending email for #{order_id}: {e}")
            return False

    print(f"[EMAIL SKIPPED] No GMAIL_APP_PASSWORD or GMAIL_REFRESH_TOKEN configured.")
    return False


def fetch_recent_tiqets_orders():
    headers = {
        'Authorization': f'Token {tiqets_api_key}',
        'Accept': 'application/json'
    }
    req = urllib.request.Request('https://api.tiqets.com/v2/orders', headers=headers)
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        return data.get('orders', [])


def upload_to_data_manager(order, click_info, access_token):
    order_id = str(order.get('order_reference_id'))
    created_at = order.get('order_created_timestamp')
    if created_at and '.' in created_at:
        ts_part = created_at.split('.')[0]
        if not ts_part.endswith('Z'):
            ts_part += 'Z'
    else:
        ts_part = created_at or datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    raw_comm = order.get('estimated_commission')
    if raw_comm is not None:
        value = round(float(raw_comm), 2)
    else:
        value = round(float(order.get('sale_order_value', 0.0)), 2)
    currency = order.get('currency', 'EUR')

    url = "https://datamanager.googleapis.com/v1/events:ingest"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    event = {
        "eventName": "purchase",
        "eventTimestamp": ts_part,
        "eventSource": "WEB",
        "conversionValue": value,
        "currency": currency,
        "transactionId": order_id,
        "adIdentifiers": {
            click_info['type']: click_info['value']
        }
    }

    payload = {
        "destinations": [
            {
                "operatingAccount": {
                    "accountType": "GOOGLE_ADS",
                    "accountId": customer_id
                },
                "productDestinationId": conversion_action_id
            }
        ],
        "events": [event],
        "validateOnly": False
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            res_data = json.loads(resp.read().decode())
            print(f"[SUCCESS] Order {order_id} uploaded to Google Data Manager. Request ID: {res_data.get('requestId')}")
            return True, res_data.get('requestId')
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        print(f"[ERROR] Failed uploading order {order_id}: {e.code} {err}")
        return False, err


def sync():
    orders = fetch_recent_tiqets_orders()
    print(f"Fetched {len(orders)} recent orders from Tiqets.")
    new_actions = 0
    token = None

    for order in orders:
        order_id = str(order.get('order_reference_id'))
        status = order.get('order_status', '')
        if status == 'cancelled':
            continue

        attribution = classify_ad_attribution(order)
        if not attribution['is_ad']:
            continue

        click_info = attribution['click_info']
        needs_google_upload = bool(click_info and click_info['type'] in ('gclid', 'wbraid', 'gbraid'))

        existing_record = uploaded_orders.get(order_id, {})
        already_uploaded = bool(existing_record.get('request_id')) or not needs_google_upload
        already_emailed = bool(existing_record.get('email_sent'))

        if already_uploaded and already_emailed:
            continue

        google_sync_note = "N/A (No Google Click ID)"

        # 1. Upload to Google Ads Data Manager if Google Click ID present
        if click_info and click_info['type'] in ('gclid', 'wbraid', 'gbraid'):
            if not already_uploaded:
                print(f"Found Google Ads order {order_id} with {click_info['type']}={click_info['value']} (Commission: €{order.get('estimated_commission')})")
                if not token:
                    token = get_google_access_token()
                success, req_id = upload_to_data_manager(order, click_info, token)
                if success:
                    existing_record['uploaded_at'] = datetime.utcnow().isoformat() + 'Z'
                    existing_record['request_id'] = req_id
                    existing_record['click_id_type'] = click_info['type']
                    existing_record['click_id'] = click_info['value']
                    google_sync_note = f"✅ Uploaded (Req: {req_id[:8]}...)"
                else:
                    google_sync_note = f"❌ Upload failed"
            else:
                req_id = existing_record.get('request_id', '')
                google_sync_note = f"✅ Uploaded (Req: {req_id[:8]}...)"

        # 2. Send Email Notification if not yet sent
        if not already_emailed:
            email_ok = send_booking_email_alert(order, attribution, google_sync_note)
            if email_ok:
                existing_record['email_sent'] = True
                existing_record['email_sent_at'] = datetime.utcnow().isoformat() + 'Z'

        existing_record['gross_value'] = order.get('sale_order_value')
        existing_record['commission'] = order.get('estimated_commission')
        existing_record['value'] = round(float(order.get('estimated_commission') or order.get('sale_order_value') or 0.0), 2)
        existing_record['source'] = attribution['source_label']
        existing_record['placement'] = attribution['placement']
        uploaded_orders[order_id] = existing_record
        new_actions += 1

    with open(STATE_FILE, 'w') as f:
        json.dump(uploaded_orders, f, indent=2)

    print(f"Sync complete. {new_actions} ad order(s) processed.")


if __name__ == '__main__':
    sync()
