#!/usr/bin/env python3
"""
Adversarial Canonical & Affiliate Link Stress Test Suite
Challenger M1-2 — The Cruise Detective Staging Architecture Overhaul
"""

import os
import re
import sys
import glob
from html.parser import HTMLParser
from urllib.parse import urlparse, parse_qs

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

HUBS = {
    "seine-river-cruises-paris": {
        "file": "seine-river-cruises-paris/index.html",
        "slug": "seine-river-cruises-paris",
        "expected_pids": {"973977", "982823", "1003911", "976735", "977685"}
    },
    "dinner-cruises-paris": {
        "file": "dinner-cruises-paris/index.html",
        "slug": "dinner-cruises-paris",
        "expected_pids": {"982924", "974358", "1052475", "1049009", "1023747", "1071588"}
    },
    "canal-cruises-amsterdam": {
        "file": "canal-cruises-amsterdam/index.html",
        "slug": "canal-cruises-amsterdam",
        "expected_pids": {"973666", "1018628", "1055262", "973884", "1113410"}
    },
    "thames-river-cruises-london": {
        "file": "thames-river-cruises-london/index.html",
        "slug": "thames-river-cruises-london",
        "expected_pids": {"975431"}
    },
    "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison": {
        "file": "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html",
        "slug": "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison",
        "expected_pids": {"982924", "974358"}
    }
}

class DOMParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals = []
        self.tiqets_links = []
        self.scripts = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "link" and d.get("rel", "").lower() == "canonical":
            self.canonicals.append(d)
        elif tag == "a" and "tiqets.com" in d.get("href", ""):
            self.tiqets_links.append(d)
        elif tag == "script" and "src" in d:
            self.scripts.append(d)

def run_suite():
    print("======================================================================")
    print("CHALLENGER M1-2: ADVERSARIAL CANONICAL & AFFILIATE LINK STRESS SUITE")
    print("======================================================================\n")

    failures = []
    total_tests = 0
    total_canonicals = 0
    total_tiqets = 0

    # -------------------------------------------------------------------------
    # SUITE 1: CANONICAL TAGS IN 5 CORE MONEY HUBS
    # -------------------------------------------------------------------------
    print("--- SUITE 1: Canonical Tag Rigor across 5 Core Money Hubs ---")
    for name, meta in HUBS.items():
        fpath = os.path.join(ROOT, meta["file"])
        assert os.path.exists(fpath), f"File missing: {fpath}"
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        parser = DOMParser()
        parser.feed(content)

        total_tests += 1
        if len(parser.canonicals) != 1:
            failures.append(f"{name}: Expected exactly 1 canonical tag, found {len(parser.canonicals)}")
            continue

        c_href = parser.canonicals[0].get("href", "")
        total_canonicals += 1

        # Test: Zero '#' fragments
        total_tests += 1
        if "#" in c_href:
            failures.append(f"{name}: Canonical contains '#' fragment: {c_href}")

        # Test: Zero legacy subdomains
        total_tests += 1
        if "deals.thecruisedetective.com" in c_href or "deals.cruisedetective.com" in c_href:
            failures.append(f"{name}: Canonical references deals subdomain: {c_href}")

        # Test: Absolute URL with exact host and slug
        total_tests += 1
        u = urlparse(c_href)
        expected_url = f"https://www.thecruisedetective.com/{meta['slug']}"
        if c_href != expected_url:
            failures.append(f"{name}: Canonical mismatch. Got '{c_href}', expected '{expected_url}'")

        if u.scheme != "https" or u.netloc != "www.thecruisedetective.com" or u.path != f"/{meta['slug']}":
            failures.append(f"{name}: Malformed canonical URI structure: {c_href}")

        print(f"  [PASS] {name} -> {c_href}")

    # -------------------------------------------------------------------------
    # SUITE 2: GLOBAL CANONICAL HASH FRAGMENT AUDIT
    # -------------------------------------------------------------------------
    print("\n--- SUITE 2: Global Canonical Tag Audit across Entire Repository ---")
    all_html = glob.glob(os.path.join(ROOT, "**/*.html"), recursive=True)
    fragment_violations = []
    for hfile in all_html:
        if ".agents" in hfile or "node_modules" in hfile:
            continue
        with open(hfile, "r", encoding="utf-8", errors="ignore") as f:
            c = f.read()
        p = DOMParser()
        p.feed(c)
        for can in p.canonicals:
            chref = can.get("href", "")
            if "#" in chref:
                fragment_violations.append((hfile, chref))

    total_tests += 1
    if fragment_violations:
        failures.append(f"Found canonical tags with '#' fragments: {fragment_violations}")
    else:
        print(f"  [PASS] 0 canonical tags with '#' fragments found across {len(all_html)} HTML files.")

    # -------------------------------------------------------------------------
    # SUITE 3: OUTBOUND TIQETS AFFILIATE LINKS IN 5 HUBS
    # -------------------------------------------------------------------------
    print("\n--- SUITE 3: Outbound Tiqets Affiliate Link Audit in 5 Hubs ---")
    for name, meta in HUBS.items():
        fpath = os.path.join(ROOT, meta["file"])
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        parser = DOMParser()
        parser.feed(content)

        hub_tiqets = parser.tiqets_links
        total_tests += 1
        if len(hub_tiqets) == 0:
            failures.append(f"{name}: No Tiqets links found!")
            continue

        print(f"  Testing {len(hub_tiqets)} Tiqets links in {name}...")
        for i, link in enumerate(hub_tiqets, 1):
            raw_href = link.get("href", "")
            total_tiqets += 1

            # Test: No deals subdomain in link href
            total_tests += 1
            if "deals.cruisedetective.com" in raw_href or "deals.thecruisedetective.com" in raw_href:
                failures.append(f"{name} Link {i}: Legacy deals domain found in href: {raw_href}")

            parsed = urlparse(raw_href)
            qs = parse_qs(parsed.query)

            # Test: Valid partner parameter
            total_tests += 1
            partner = qs.get("partner", [None])[0]
            if partner != "thecruisedetective.com-176436":
                failures.append(f"{name} Link {i}: Invalid partner '{partner}' in {raw_href}")

            # Test: Product ID extraction
            total_tests += 1
            m = re.search(r"-p(\d+)/?", parsed.path)
            if not m:
                failures.append(f"{name} Link {i}: No product ID found in path: {raw_href}")
            else:
                pid = m.group(1)
                total_tests += 1
                if pid not in meta["expected_pids"]:
                    failures.append(f"{name} Link {i}: Unexpected product ID p{pid} for hub {name}")

            # Test: Campaign parameter present
            total_tests += 1
            campaign = qs.get("tq_campaign", [None])[0]
            if not campaign:
                failures.append(f"{name} Link {i}: Missing tq_campaign in {raw_href}")

            # Test: Protocol HTTPS
            total_tests += 1
            if parsed.scheme != "https":
                failures.append(f"{name} Link {i}: Non-HTTPS scheme in {raw_href}")

            # Test: Hash fragment
            total_tests += 1
            if parsed.fragment:
                failures.append(f"{name} Link {i}: Fragment present on Tiqets URL: {raw_href}")

        print(f"    [PASS] All {len(hub_tiqets)} Tiqets links in {name} verified.")

    # -------------------------------------------------------------------------
    # SUITE 4: SCRIPT DECOUPLING & PARTNER INTEGRITY
    # -------------------------------------------------------------------------
    print("\n--- SUITE 4: Script Decoupling & Parameter Preservation ---")
    for name, meta in HUBS.items():
        fpath = os.path.join(ROOT, meta["file"])
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        total_tests += 1
        if "cdn.jsdelivr.net/gh/adamdimitrov/cruisedetective@main/webflow-sync.js" in content:
            failures.append(f"{name}: Coupled to GitHub main via jsDelivr CDN!")
        else:
            print(f"  [PASS] {name} is decoupled from jsDelivr main")

        total_tests += 1
        if '<script src="/webflow-sync.js"' not in content and "<script src='/webflow-sync.js'" not in content:
            failures.append(f"{name}: Missing /webflow-sync.js inclusion!")
        else:
            print(f"  [PASS] {name} includes local /webflow-sync.js")

    # -------------------------------------------------------------------------
    # SUMMARY & VERDICT
    # -------------------------------------------------------------------------
    print("\n======================================================================")
    print(f"TOTAL ASSERTIONS RUN: {total_tests}")
    print(f"CANONICAL TAGS AUDITED: {total_canonicals}")
    print(f"TIQETS AFFILIATE LINKS AUDITED: {total_tiqets}")
    print(f"FAILURES DETECTED: {len(failures)}")
    print("======================================================================")

    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        print("\nVERDICT: REJECT")
        sys.exit(1)
    else:
        print("\nVERDICT: APPROVE")
        sys.exit(0)

if __name__ == "__main__":
    run_suite()
