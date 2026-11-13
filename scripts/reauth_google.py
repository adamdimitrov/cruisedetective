#!/usr/bin/env python3
"""Re-mint a Google OAuth refresh token and write it into .env.

Usage:
    python3 scripts/reauth_google.py ads     # GOOGLE_ADS_REFRESH_TOKEN  (Google Ads + Data Manager)
    python3 scripts/reauth_google.py gmail   # GMAIL_REFRESH_TOKEN       (send booking alerts)

Opens Google's consent page in your browser, catches the redirect on a
localhost port, exchanges the code and updates the matching key in .env.
The token is never printed. Requires the OAuth client to be a "Desktop app"
type (loopback redirect). Stdlib only.
"""
import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import threading
import urllib.parse
import urllib.request
import webbrowser

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(REPO_DIR, '.env')

PROFILES = {
    'ads': {
        'prefix': 'GOOGLE_ADS',
        'scopes': [
            'https://www.googleapis.com/auth/adwords',
            'https://www.googleapis.com/auth/datamanager',
        ],
    },
    'gmail': {
        'prefix': 'GMAIL',
        'scopes': ['https://www.googleapis.com/auth/gmail.send'],
    },
}


def load_env():
    env = {}
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env


def set_env_key(key, value):
    with open(ENV_PATH) as f:
        lines = f.readlines()
    for i, line in enumerate(lines):
        if line.split('=', 1)[0].strip() == key:
            lines[i] = f'{key}={value}\n'
            break
    else:
        lines.append(f'{key}={value}\n')
    with open(ENV_PATH, 'w') as f:
        f.writelines(lines)


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in PROFILES:
        sys.exit(__doc__)
    profile = PROFILES[sys.argv[1]]
    env = load_env()
    client_id = env.get(f"{profile['prefix']}_CLIENT_ID")
    client_secret = env.get(f"{profile['prefix']}_CLIENT_SECRET")
    if not client_id or not client_secret:
        sys.exit(f"Missing {profile['prefix']}_CLIENT_ID / _CLIENT_SECRET in .env")

    result = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            result.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            msg = 'Authorized. You can close this tab.' if 'code' in q else f"Failed: {q.get('error', ['?'])[0]}"
            self.wfile.write(f'<p style="font-family:sans-serif">{msg}</p>'.encode())
            threading.Thread(target=self.server.shutdown, daemon=True).start()

        def log_message(self, *a):
            pass

    server = http.server.HTTPServer(('127.0.0.1', 0), Handler)
    redirect_uri = f'http://127.0.0.1:{server.server_port}'
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(16)

    auth_url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode({
        'client_id': client_id,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': ' '.join(profile['scopes']),
        'access_type': 'offline',
        'prompt': 'consent',
        'state': state,
        'code_challenge': challenge,
        'code_challenge_method': 'S256',
    })
    print('Opening Google sign-in in your browser. If it does not open, visit:\n' + auth_url)
    webbrowser.open(auth_url)
    server.serve_forever()

    if result.get('state') != state or 'code' not in result:
        sys.exit(f"Authorization failed: {result.get('error', 'state mismatch')}")

    data = urllib.parse.urlencode({
        'code': result['code'],
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'code_verifier': verifier,
    }).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data=data)) as r:
            tok = json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        sys.exit(f'Token exchange failed: {e.code} {e.read().decode()}')

    if 'refresh_token' not in tok:
        sys.exit('Google returned no refresh token; revoke the app at myaccount.google.com/permissions and retry.')
    granted = set(tok.get('scope', '').split())
    missing = [s for s in profile['scopes'] if s not in granted]
    if missing:
        sys.exit(f'Consent did not include: {", ".join(missing)} (tick every checkbox on the consent screen and retry).')

    set_env_key(f"{profile['prefix']}_REFRESH_TOKEN", tok['refresh_token'])
    print(f"Saved new {profile['prefix']}_REFRESH_TOKEN to .env with scopes: {', '.join(sorted(granted))}")


if __name__ == '__main__':
    main()
