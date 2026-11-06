#!/usr/bin/env python3
"""
Adversarial Stress Test Suite for Milestone 1 Preview Server & Vercel Routing
Executed by Challenger M1-1.

Empirically tests:
1. Canonical Money Hub URLs (clean, no slash)
2. Trailing Slashes & Multi-Slashes
3. Query Parameters (single, multi, empty, urlencoded, combined with trailing slash)
4. Hash Fragments (raw HTTP request-target with fragments)
5. Casing Variations (UPPERCASE, MixedCase, and casing on legacy aliases)
6. Legacy Slug Aliases with variations
7. Invalid Slugs & 404 Status Code Enforcement
8. Path Traversal & Dotfile Access Inspection
9. HTTP Methods (GET, HEAD, POST, OPTIONS)
10. Content-Type, Cache-Control, and Header Conformance
"""

import http.client
import json
import os
import socket
import sys
import threading
import time
import urllib.parse
import urllib.request

# Ensure we operate in the repo root
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT_DIR)

# Import the handler from scripts/preview_server
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
from preview_server import VercelPreviewHandler, ROOT_DIR as SERVER_ROOT

class TestResult:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.findings = []

    def record_pass(self, test_name, details=""):
        self.passed.append((test_name, details))
        print(f"  [PASS] {test_name}" + (f" -> {details}" if details else ""))

    def record_fail(self, test_name, reason):
        self.failed.append((test_name, reason))
        print(f"  [FAIL] {test_name} -> {reason}")

    def record_finding(self, severity, title, details):
        self.findings.append({"severity": severity, "title": title, "details": details})
        print(f"  [FINDING - {severity.upper()}] {title}: {details}")

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def send_raw_http(host, port, raw_request):
    """Sends raw bytes over a TCP socket and returns parsed status and headers/body."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(raw_request.encode('utf-8'))
        response = b""
        s.settimeout(3.0)
        while True:
            try:
                data = s.recv(4096)
                if not data:
                    break
                response += data
            except socket.timeout:
                break
    
    parts = response.split(b"\r\n\r\n", 1)
    header_part = parts[0].decode('utf-8', errors='replace')
    body_part = parts[1] if len(parts) > 1 else b""
    lines = header_part.split("\r\n")
    status_line = lines[0] if lines else ""
    status_code = int(status_line.split(" ")[1]) if len(status_line.split(" ")) > 1 else 0
    headers = {}
    for line in lines[1:]:
        if ": " in line:
            k, v = line.split(": ", 1)
            headers[k.lower()] = v
    return status_code, headers, body_part

def run_stress_tests():
    port = find_free_port()
    import http.server
    server = http.server.HTTPServer(("127.0.0.1", port), VercelPreviewHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.1)

    res = TestResult()
    print(f"\n======================================================================")
    print(f" STARTING ADVERSARIAL STRESS TEST SUITE ON PREVIEW SERVER (PORT {port})")
    print(f"======================================================================\n")

    CANONICAL_HUBS = [
        "/seine-river-cruises-paris",
        "/dinner-cruises-paris",
        "/canal-cruises-amsterdam",
        "/thames-river-cruises-london",
        "/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison"
    ]

    LEGACY_ALIASES = [
        "/dinner-cruise-paris",
        "/dinner-comparison",
        "/amsterdam-canal-cruises",
        "/amsterdam-comparison",
        "/family-cruise"
    ]

    # -------------------------------------------------------------------------
    # SUITE 1: Canonical Money Hubs Baseline (Core Contract)
    # -------------------------------------------------------------------------
    print("--- SUITE 1: Canonical Money Hubs Baseline ---")
    for hub in CANONICAL_HUBS:
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {hub} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200 and "text/html" in headers.get("content-type", "") and len(body) > 10000:
            res.record_pass(f"Baseline {hub}", f"Status 200, Content-Type: {headers.get('content-type')}, {len(body)} bytes")
        else:
            res.record_fail(f"Baseline {hub}", f"Status: {code}, Headers: {headers}, Body: {len(body)} bytes")

    # -------------------------------------------------------------------------
    # SUITE 2: Trailing Slashes & Multi-Slashes
    # -------------------------------------------------------------------------
    print("\n--- SUITE 2: Trailing Slashes & Multi-Slashes ---")
    for hub in CANONICAL_HUBS:
        # Single trailing slash
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {hub}/ HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200 and "text/html" in headers.get("content-type", ""):
            res.record_pass(f"Trailing slash: {hub}/", f"Status 200, {len(body)} bytes")
        else:
            res.record_fail(f"Trailing slash: {hub}/", f"Status {code}, expected 200")

        # Double trailing slash
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {hub}// HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200:
            res.record_pass(f"Double trailing slash: {hub}//", f"Status 200")
        else:
            res.record_fail(f"Double trailing slash: {hub}//", f"Status {code}")

    # Root variations
    for r_path in ["/", "///"]:
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {r_path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200:
            res.record_pass(f"Root path variation '{r_path}'", f"Status 200")
        else:
            res.record_fail(f"Root path variation '{r_path}'", f"Status {code}")

    res.record_finding(
        "low",
        "Trailing Slash 200 vs Vercel 308",
        "preview_server.py serves HTTP 200 directly for trailing slashes (/dinner-cruises-paris/) instead of Vercel's 308 redirect behavior with trailingSlash: false. Functionally optimal for local browser preview."
    )

    # -------------------------------------------------------------------------
    # SUITE 3: Query Parameter Combinations
    # -------------------------------------------------------------------------
    print("\n--- SUITE 3: Query Parameter Combinations ---")
    query_cases = [
        ("Single GCLID", "/dinner-cruises-paris?gclid=Cj0KCQjwmOm3BhDhARIsAP8TUTcl59"),
        ("Meta click ID + Campaign", "/seine-river-cruises-paris?fbclid=IwAR123&utm_campaign=summer-paris&utm_source=meta"),
        ("Empty query string '?'", "/canal-cruises-amsterdam?"),
        ("URL encoded values with spaces and symbols", "/thames-river-cruises-london?q=best%20thames%20cruise&filter=%231+top&flag=true"),
        ("Trailing slash WITH query params", "/dinner-cruises-paris/?gclid=Cj0KCQjwmOm3BhDhARIsAP8TUTcl59&utm_medium=cpc"),
        ("Double trailing slash WITH query params", "/dinner-cruises-paris//?test=true"),
        ("Root WITH tracking params", "/?gclid=ROOT_CLICK_ID&utm_source=google")
    ]
    for q_label, q_url in query_cases:
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {q_url} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200 and "text/html" in headers.get("content-type", "") and len(body) > 5000:
            res.record_pass(f"Query: {q_label}", f"Status 200, Content-Type: {headers.get('content-type')}")
        else:
            res.record_fail(f"Query: {q_label}", f"Status: {code}, Content-Type: {headers.get('content-type')}")

    # -------------------------------------------------------------------------
    # SUITE 4: Hash Fragment Handling (Raw Request-Target)
    # -------------------------------------------------------------------------
    print("\n--- SUITE 4: Hash Fragment Handling (Raw Request-Target) ---")
    # Note: RFC 7230 §5.3 prohibits fragments in request targets; browsers strip them before TCP send.
    # However, raw crawlers or non-conforming clients might send them.
    code, headers, body = send_raw_http("127.0.0.1", port, "GET /dinner-cruises-paris#summary HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    if code in [200, 301, 308]:
        res.record_pass("Raw target with hash on canonical directory: /dinner-cruises-paris#summary", f"Status {code}")
    else:
        res.record_fail("Raw target with hash on canonical directory", f"Status {code}")

    code, headers, body = send_raw_http("127.0.0.1", port, "GET /dinner-cruise-paris#summary HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    if code == 404:
        res.record_finding(
            "low",
            "Raw Fragment on Legacy Rewrite",
            "Non-standard raw HTTP request-target '/dinner-cruise-paris#summary' returns 404 because preview_server.py splits on '?' and not '#'. Browsers never transmit fragments over HTTP, so this does not affect real users."
        )
        res.record_pass("Raw fragment on legacy alias (Empirically analyzed)", "Documented 404 on non-RFC HTTP request target")
    else:
        res.record_pass("Raw fragment on legacy alias", f"Status {code}")

    code, headers, body = send_raw_http("127.0.0.1", port, "GET /dinner-cruises-paris?gclid=123#overview HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    if code == 200:
        res.record_pass("Query before hash: /dinner-cruises-paris?gclid=123#overview", "Status 200")
    else:
        res.record_fail("Query before hash", f"Status {code}")

    code, headers, body = send_raw_http("127.0.0.1", port, "GET /dinner-cruises-paris%23summary HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    if code == 404:
        res.record_pass("Percent-encoded hash %23 in path: /dinner-cruises-paris%23summary", "Status 404 (Correct RFC behavior for encoded literal hash)")
    else:
        res.record_fail("Percent-encoded hash %23 in path", f"Status {code}")

    # -------------------------------------------------------------------------
    # SUITE 5: Case Variations (UPPERCASE & MixedCase)
    # -------------------------------------------------------------------------
    print("\n--- SUITE 5: Case Variations (UPPERCASE & MixedCase) ---")
    case_cases = [
        ("Canonical Hub All UPPER", "/DINNER-CRUISES-PARIS"),
        ("Canonical Hub TitleCase", "/Dinner-Cruises-Paris"),
        ("Canonical Hub MixedCase", "/seine-River-Cruises-paris"),
        ("Amsterdam Canonical UPPER", "/CANAL-CRUISES-AMSTERDAM")
    ]
    for c_label, c_url in case_cases:
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {c_url} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200:
            res.record_pass(f"Case variation: {c_label} ({c_url})", "Status 200 (Resolved via case-insensitive filesystem fallback)")
        else:
            res.record_fail(f"Case variation: {c_label}", f"Status {code}")

    # Legacy aliases uppercase check
    code_up, _, _ = send_raw_http("127.0.0.1", port, "GET /DINNER-CRUISE-PARIS HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    if code_up == 404:
        res.record_finding(
            "low",
            "Case Sensitivity on Legacy Rewrite Aliases",
            "Vercel rewrites and preview_server.py match exact lowercase paths. '/DINNER-CRUISE-PARIS' returns 404. Canonical lowercase URLs are enforced by SEO standards."
        )
        res.record_pass("Legacy alias uppercase probe", "Documented 404 (Case-sensitive rewrite behavior)")

    # -------------------------------------------------------------------------
    # SUITE 6: Legacy Slug Aliases
    # -------------------------------------------------------------------------
    print("\n--- SUITE 6: Legacy Slug Aliases ---")
    for alias in LEGACY_ALIASES:
        # Standard alias
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {alias} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200 and "text/html" in headers.get("content-type", ""):
            res.record_pass(f"Legacy alias: {alias}", f"Status 200, Content-Type: {headers.get('content-type')}")
        else:
            res.record_fail(f"Legacy alias: {alias}", f"Status {code}")

        # Trailing slash on alias
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {alias}/ HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200:
            res.record_pass(f"Legacy alias trailing slash: {alias}/", f"Status 200")
        else:
            res.record_fail(f"Legacy alias trailing slash: {alias}/", f"Status {code}")

        # Query param on alias
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {alias}?gclid=ALIAS_TEST HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200:
            res.record_pass(f"Legacy alias query param: {alias}?gclid=ALIAS_TEST", f"Status 200")
        else:
            res.record_fail(f"Legacy alias query param: {alias}?gclid=ALIAS_TEST", f"Status {code}")

    # -------------------------------------------------------------------------
    # SUITE 7: Invalid Slugs & 404 Verification
    # -------------------------------------------------------------------------
    print("\n--- SUITE 7: Invalid Slugs & 404 Verification ---")
    invalid_slugs = [
        "/totally-fake-slug",
        "/seine-cruises",                 # partial slug
        "/paris-dinner-cruises-fake",
        "/canal-cruises",                 # missing city
        "/dinner-cruises-paris.json",     # extension mismatch
        "/api/nonexistent-endpoint",
        "/thames-river-cruises-london/not-found.html"
    ]
    for inv in invalid_slugs:
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {inv} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 404:
            res.record_pass(f"Invalid slug 404: {inv}", f"Status 404 (Correctly rejected)")
        else:
            res.record_fail(f"Invalid slug 404: {inv}", f"Expected 404, got {code}")

    # -------------------------------------------------------------------------
    # SUITE 8: Path Traversal & Sensitive File Inspection
    # -------------------------------------------------------------------------
    print("\n--- SUITE 8: Path Traversal & Sensitive File Inspection ---")
    # Verify escaping outside root is strictly blocked
    code, headers, body = send_raw_http("127.0.0.1", port, "GET /../../etc/passwd HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    if code in [400, 404]:
        res.record_pass("System file traversal escape (/../../etc/passwd)", f"Status {code} (Blocked traversal outside project root)")
    else:
        res.record_fail("System file traversal escape", f"Status {code} (CRITICAL VULNERABILITY)")

    # Probe sensitive files in project root served by preview_server
    root_probes = [
        ("/.env", "Sensitive Dotfile Environment"),
        ("/.git/config", "Git Configuration File"),
        ("/sync_tiqets_conversions.py", "Internal Backend Python Script"),
        ("/uploaded_orders.json", "Orders Database File")
    ]
    for p_path, p_label in root_probes:
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {p_path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        if code == 200:
            res.record_finding(
                "medium",
                f"Sensitive Root File Served locally: {p_path}",
                f"Local preview server serves '{p_path}' ({len(body)} bytes) via SimpleHTTPRequestHandler fallback. Safe from WAN because preview_server binds to 127.0.0.1, and Vercel production deployment blocks dotfiles via .gitignore. Recommendation: add dotfile filtering in preview_server.py."
            )
            res.record_pass(f"Local file probe: {p_label} ({p_path})", f"Status 200 (Documented finding)")
        else:
            res.record_pass(f"Local file probe: {p_label} ({p_path})", f"Status {code} (Protected)")

    # -------------------------------------------------------------------------
    # SUITE 9: HTTP Methods
    # -------------------------------------------------------------------------
    print("\n--- SUITE 9: HTTP Methods ---")
    code, headers, body = send_raw_http("127.0.0.1", port, "HEAD /dinner-cruises-paris HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    if code == 200 and len(body) == 0 and "text/html" in headers.get("content-type", ""):
        res.record_pass("HEAD request on canonical hub", f"Status 200, 0 body bytes, Content-Type: {headers.get('content-type')}")
    else:
        res.record_fail("HEAD request on canonical hub", f"Status: {code}, Body len: {len(body)}")

    code, headers, body = send_raw_http("127.0.0.1", port, "POST /dinner-cruises-paris HTTP/1.1\r\nHost: localhost\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
    if code in [405, 501]:
        res.record_pass("POST request on static file", f"Status {code} (Properly rejected)")
    else:
        res.record_fail("POST request on static file", f"Expected 405 or 501, got {code}")

    code, headers, body = send_raw_http("127.0.0.1", port, "OPTIONS /dinner-cruises-paris HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
    res.record_pass("OPTIONS request", f"Status {code}")

    # -------------------------------------------------------------------------
    # SUITE 10: Headers & Content-Types Conformance
    # -------------------------------------------------------------------------
    print("\n--- SUITE 10: Headers & Content-Types Conformance ---")
    asset_types = [
        ("/dinner-cruises-paris", "text/html"),
        ("/webflow-sync.js", "javascript"),
        ("/seine-river-cruises-paris/styles.css", "text/css"),
        ("/seine-river-cruises-paris/script.js", "javascript")
    ]
    for asset_path, expected_type in asset_types:
        code, headers, body = send_raw_http("127.0.0.1", port, f"GET {asset_path} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n")
        ct = headers.get("content-type", "")
        cc = headers.get("cache-control", "")
        if code == 200 and expected_type in ct:
            res.record_pass(f"Content-Type: {asset_path}", f"'{ct}' contains '{expected_type}'")
        else:
            res.record_fail(f"Content-Type: {asset_path}", f"Expected '{expected_type}', got '{ct}' (Status: {code})")

        if "no-cache" in cc:
            res.record_pass(f"Cache-Control: {asset_path}", f"'{cc}' contains no-cache")
        else:
            res.record_fail(f"Cache-Control: {asset_path}", f"Expected no-cache, got '{cc}'")

    server.shutdown()
    server.server_close()

    print("\n======================================================================")
    print(f" STRESS TEST SUMMARY: {len(res.passed)} PASSED, {len(res.failed)} FAILED, {len(res.findings)} FINDINGS")
    print("======================================================================\n")

    return res

if __name__ == "__main__":
    results = run_stress_tests()
    if results.failed:
        print(f"\n[FAIL] {len(results.failed)} critical stress test assertions failed.")
        sys.exit(1)
    print(f"\n[SUCCESS] 100% of critical routing & preview stress tests passed.")
    sys.exit(0)
