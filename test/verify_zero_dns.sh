#!/usr/bin/env bash
set -euo pipefail

echo "=== ZERO-DNS ISOLATION VERIFICATION ==="

# Check 1: Authoritative Nameservers on Hover
NS_RECORDS=$(dig thecruisedetective.com NS +short | sort)
echo "1. Checking Authoritative Nameservers:"
echo "$NS_RECORDS"
if echo "$NS_RECORDS" | grep -qi "hover.com"; then
    echo "   [PASS] Nameservers verified on Hover (isolated from Git/Vercel)."
else
    echo "   [FAIL] Nameservers unexpected: $NS_RECORDS"
    exit 1
fi

# Check 2: Apex A-Record on Linguana
APEX_IP=$(dig thecruisedetective.com A +short | head -n 1)
echo "2. Checking Apex A-Record:"
echo "   Apex IP: $APEX_IP"
if [ "$APEX_IP" = "35.187.176.9" ]; then
    echo "   [PASS] Apex points strictly to Linguana (35.187.176.9)."
else
    echo "   [FAIL] Apex IP changed: $APEX_IP"
    exit 1
fi

# Check 3: WWW CNAME on Linguana Proxy
WWW_CNAME=$(dig www.thecruisedetective.com CNAME +short)
echo "3. Checking WWW CNAME Record:"
echo "   WWW CNAME: $WWW_CNAME"
if [ "$WWW_CNAME" = "proxy-ssl.linguana.io." ]; then
    echo "   [PASS] WWW CNAME points strictly to Linguana proxy (proxy-ssl.linguana.io.)."
else
    echo "   [FAIL] WWW CNAME changed: $WWW_CNAME"
    exit 1
fi

# Check 4: Live Production Server Headers
echo "4. Checking Live Production HTTP Server Response:"
SERVER_HEADER=$(curl -sI https://www.thecruisedetective.com | grep -i '^server:' | tr -d '\r')
echo "   Server header: $SERVER_HEADER"
if echo "$SERVER_HEADER" | grep -qiE 'caddy|gunicorn'; then
    echo "   [PASS] Live production responds with Caddy/gunicorn (Linguana/Webflow active)."
else
    echo "   [FAIL] Unexpected server header on live production!"
    exit 1
fi

# Check 5: Git Branch Isolation
echo "5. Checking Git Branch Isolation:"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "   Current Git branch: $CURRENT_BRANCH"
if [ "$CURRENT_BRANCH" = "staging/static-overhaul" ]; then
    echo "   [PASS] Working on staging/static-overhaul (decoupled from main)."
else
    echo "   [FAIL] Expected branch 'staging/static-overhaul', got '$CURRENT_BRANCH'"
    exit 1
fi

echo "=========================================="
echo "ALL ZERO-DNS CHECKS PASSED: 100% ISOLATED"
echo "=========================================="
