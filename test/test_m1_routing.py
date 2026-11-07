#!/usr/bin/env python3
"""
Automated Routing & Preview Verification Test for Milestone 1.
Tests:
1. vercel.json schema and required rewrite mappings.
2. Physical index.html file presence and size across all 5 hubs.
3. HTTP 200 response, text/html content-type, canonical tags, and partner tracking.
4. Legacy slug alias backward compatibility.
Exit code 0 on 100% pass, non-zero on failure.
"""

import http.server
import json
import os
import sys
import threading
import urllib.request
import socket

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT_DIR)

TEST_HUBS = [
    {
        "slug": "/seine-river-cruises-paris",
        "file": "seine-river-cruises-paris/index.html",
        "min_bytes": 10000,
        "content_marker": "Seine",
        "partner_id": "thecruisedetective.com-176436"
    },
    {
        "slug": "/dinner-cruises-paris",
        "file": "dinner-cruises-paris/index.html",
        "min_bytes": 50000,
        "content_marker": "Bateaux Mouches",
        "partner_id": "thecruisedetective.com-176436"
    },
    {
        "slug": "/canal-cruises-amsterdam",
        "file": "canal-cruises-amsterdam/index.html",
        "min_bytes": 10000,
        "content_marker": "Amsterdam",
        "partner_id": "thecruisedetective.com-176436"
    },
    {
        "slug": "/thames-river-cruises-london",
        "file": "thames-river-cruises-london/index.html",
        "min_bytes": 10000,
        "content_marker": "Thames",
        "partner_id": "thecruisedetective.com-176436"
    },
    {
        "slug": "/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison",
        "file": "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html",
        "min_bytes": 10000,
        "content_marker": "Bateaux",
        "partner_id": "thecruisedetective.com-176436"
    }
]

LEGACY_ALIASES = [
    "/dinner-cruise-paris",
    "/amsterdam-canal-cruises",
    "/amsterdam-comparison"
]

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def run_tests():
    print("\n--- PHASE 1: vercel.json Configuration Verification ---")
    v_path = os.path.join(ROOT_DIR, "vercel.json")
    assert os.path.exists(v_path), "vercel.json not found!"
    with open(v_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    assert config.get("version") == 2, "vercel.json version must be 2"
    assert config.get("cleanUrls") is True, "cleanUrls must be true"
    assert config.get("trailingSlash") is False, "trailingSlash must be false"

    rewrites = config.get("rewrites", [])
    rewrite_map = {r["source"]: r["destination"] for r in rewrites}

    for hub in TEST_HUBS:
        slug = hub["slug"]
        expected_dest = "/" + hub["file"]
        assert slug in rewrite_map, f"Missing rewrite for canonical slug: {slug}"
        assert rewrite_map[slug] == expected_dest, f"Invalid destination for {slug}: got {rewrite_map[slug]}, expected {expected_dest}"
        print(f"  [PASS] vercel.json rewrite: {slug} -> {expected_dest}")

    for alias in LEGACY_ALIASES:
        assert alias in rewrite_map, f"Missing rewrite for legacy alias: {alias}"
        print(f"  [PASS] Legacy alias mapped: {alias} -> {rewrite_map[alias]}")

    print("\n--- PHASE 2: Physical Static File Verification ---")
    for hub in TEST_HUBS:
        fpath = os.path.join(ROOT_DIR, hub["file"])
        assert os.path.isfile(fpath), f"File not found on disk: {fpath}"
        size = os.path.getsize(fpath)
        assert size >= hub["min_bytes"], f"File {hub['file']} too small: {size} bytes (min: {hub['min_bytes']})"
        print(f"  [PASS] Static file: {hub['file']} ({size:,} bytes)")

    print("\n--- PHASE 3: Live Preview Server HTTP Verification ---")
    # Launch in-memory preview server
    class VercelTestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=ROOT_DIR, **kwargs)
        def translate_path(self, path):
            clean_path = path.split("?")[0].rstrip("/") or "/"
            for r in rewrites:
                if clean_path == (r["source"].rstrip("/") or "/"):
                    dest = r["destination"].lstrip("/")
                    target = os.path.join(ROOT_DIR, dest)
                    if os.path.isfile(target):
                        return target
            subpath = clean_path.lstrip("/")
            if subpath:
                cand = os.path.join(ROOT_DIR, subpath, "index.html")
                if os.path.isfile(cand):
                    return cand
            return super().translate_path(path)
        def log_message(self, format, *args):
            pass

    test_port = find_free_port()
    server = http.server.HTTPServer(("127.0.0.1", test_port), VercelTestHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        # Test 5 Canonical Hubs
        for hub in TEST_HUBS:
            url = f"http://127.0.0.1:{test_port}{hub['slug']}"
            req = urllib.request.Request(url, headers={"User-Agent": "M1-Verification-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                assert resp.status == 200, f"Expected 200, got {resp.status} for {url}"
                content_type = resp.headers.get("Content-Type", "")
                assert "text/html" in content_type, f"Expected text/html, got {content_type}"
                html = resp.read().decode("utf-8", errors="replace")

                # Assert HTML content marker
                assert hub["content_marker"] in html, f"Missing content marker '{hub['content_marker']}' in {hub['slug']}"

                # Assert Canonical Tag
                canon_expected = f"https://www.thecruisedetective.com{hub['slug']}"
                assert f'href="{canon_expected}"' in html or f"href='{canon_expected}'" in html, f"Missing or invalid canonical tag for {canon_expected}"
                assert f'href="{canon_expected}#' not in html, f"Canonical tag contains fragment '#' for {hub['slug']}"

                # Assert Partner Tracking
                assert hub["partner_id"] in html, f"Missing affiliate partner ID '{hub['partner_id']}' in {hub['slug']}"

                print(f"  [PASS] HTTP 200 + HTML OK: {hub['slug']} (Canonical & Partner ID verified)")

        # Test Legacy Aliases
        for alias in LEGACY_ALIASES:
            url = f"http://127.0.0.1:{test_port}{alias}"
            req = urllib.request.Request(url, headers={"User-Agent": "M1-Verification-Agent/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                assert resp.status == 200, f"Legacy alias {alias} failed with status {resp.status}"
                _ = resp.read()
                print(f"  [PASS] Legacy alias HTTP 200: {alias}")

        # Test Root URL
        with urllib.request.urlopen(f"http://127.0.0.1:{test_port}/", timeout=5) as resp:
            assert resp.status == 200, f"Root / failed with status {resp.status}"
            _ = resp.read()
            print(f"  [PASS] Root URL / HTTP 200")

    finally:
        server.shutdown()
        server.server_close()

    print("\n========================================================")
    print(" ALL 5 CORE MONEY HUBS & VERCEL REWRITES VERIFIED (100% PASS)")
    print("========================================================\n")

if __name__ == "__main__":
    try:
        run_tests()
        sys.exit(0)
    except AssertionError as e:
        print(f"\n[FAIL] VERIFICATION FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] UNEXPECTED EXCEPTION: {e}\n")
        sys.exit(2)
