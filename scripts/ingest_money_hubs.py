#!/usr/bin/env python3
"""
scripts/ingest_money_hubs.py
Automated Ingestion and Normalization Script for the 5 Core Money Hubs
Milestone 1 — The Cruise Detective Staging Architecture Overhaul
"""

import os
import shutil
import urllib.request
import ssl
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

def log(msg):
    print(f"[INGEST] {msg}")

def fetch_url(url):
    log(f"Fetching live URL: {url}")
    ctx = ssl._create_unverified_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
    )
    with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="ignore")

def normalize_webflow_sync(html):
    # Replace remote jsDelivr CDN reference with local relative script
    pattern = r'<script\s+[^>]*src=[\"\x27]https://cdn\.jsdelivr\.net/gh/adamdimitrov/cruisedetective@main/webflow-sync\.js[\"\x27][^>]*>\s*</script>'
    replacement = '<script src="/webflow-sync.js" defer></script>'
    if re.search(pattern, html, flags=re.IGNORECASE):
        html = re.sub(pattern, replacement, html, flags=re.IGNORECASE)
    elif '<script src="/webflow-sync.js"' not in html and "<script src='/webflow-sync.js'" not in html:
        # Inject before </body>
        if "</body>" in html:
            html = html.replace("</body>", f"{replacement}\n</body>")
        else:
            html += f"\n{replacement}"
    return html

def ingest_dinner_cruises():
    src = os.path.join(ROOT, "articles", "paris-dinner-cruises-overhaul", "live_preview.html")
    dest_dir = os.path.join(ROOT, "dinner-cruises-paris")
    dest_file = os.path.join(dest_dir, "index.html")
    os.makedirs(dest_dir, exist_ok=True)

    with open(src, "r", encoding="utf-8") as f:
        content = f.read()

    content = normalize_webflow_sync(content)

    # Ensure canonical is clean
    if 'rel="canonical"' in content or "rel='canonical'" in content:
        content = re.sub(
            r'<link[^>]+rel=[\"\x27]canonical[\"\x27][^>]*>',
            '<link rel="canonical" href="https://www.thecruisedetective.com/dinner-cruises-paris">',
            content,
            flags=re.IGNORECASE
        )

    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(content)
    log(f"Wrote dinner-cruises-paris/index.html ({len(content)} bytes)")

def ingest_seine_cruises():
    src_dir = os.path.join(ROOT, "seine-comparison")
    dest_dir = os.path.join(ROOT, "seine-river-cruises-paris")
    os.makedirs(dest_dir, exist_ok=True)

    # Copy styles
    shutil.copy2(os.path.join(src_dir, "styles.css"), os.path.join(dest_dir, "styles.css"))

    # Copy and normalize script.js
    with open(os.path.join(src_dir, "script.js"), "r", encoding="utf-8") as f:
        script_content = f.read()
    script_content = script_content.replace("deals.cruisedetective.com", "thecruisedetective.com-176436")
    with open(os.path.join(dest_dir, "script.js"), "w", encoding="utf-8") as f:
        f.write(script_content)

    # Normalize index.html
    with open(os.path.join(src_dir, "index.html"), "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Normalize Canonical
    content = content.replace(
        'https://deals.thecruisedetective.com/seine-river-cruises-paris',
        'https://www.thecruisedetective.com/seine-river-cruises-paris'
    )
    # 2. Normalize Stylesheet Path & Script Path
    content = content.replace('/seine-comparison/styles.css', '/seine-river-cruises-paris/styles.css')
    content = content.replace('/seine-comparison/script.js', '/seine-river-cruises-paris/script.js')
    # 3. Normalize Tiqets Partner Parameter and any deals.cruisedetective.com
    content = content.replace('partner=deals.cruisedetective.com', 'partner=thecruisedetective.com-176436')
    content = content.replace('deals.cruisedetective.com', 'thecruisedetective.com-176436')
    content = content.replace('deals.thecruisedetective.com', 'www.thecruisedetective.com')
    # 4. Inject / normalize webflow-sync.js
    content = normalize_webflow_sync(content)

    with open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(content)
    log(f"Wrote seine-river-cruises-paris/index.html ({len(content)} bytes)")

def ingest_amsterdam_cruises():
    src_dir = os.path.join(ROOT, "amsterdam-comparison")
    dest_dir = os.path.join(ROOT, "canal-cruises-amsterdam")
    os.makedirs(dest_dir, exist_ok=True)

    # Copy styles
    shutil.copy2(os.path.join(src_dir, "styles.css"), os.path.join(dest_dir, "styles.css"))

    # Copy and normalize script.js
    with open(os.path.join(src_dir, "script.js"), "r", encoding="utf-8") as f:
        script_content = f.read()
    script_content = script_content.replace("deals.cruisedetective.com", "thecruisedetective.com-176436")
    with open(os.path.join(dest_dir, "script.js"), "w", encoding="utf-8") as f:
        f.write(script_content)

    # Normalize index.html
    with open(os.path.join(src_dir, "index.html"), "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Normalize Canonical and Slug
    content = content.replace(
        'https://deals.thecruisedetective.com/amsterdam-canal-cruises',
        'https://www.thecruisedetective.com/canal-cruises-amsterdam'
    )
    # 2. Normalize Stylesheet Path & Script Path
    content = content.replace('/amsterdam-comparison/styles.css', '/canal-cruises-amsterdam/styles.css')
    content = content.replace('/amsterdam-comparison/script.js', '/canal-cruises-amsterdam/script.js')
    # 3. Normalize Tiqets Partner Parameter and any deals.cruisedetective.com
    content = content.replace('partner=deals.cruisedetective.com', 'partner=thecruisedetective.com-176436')
    content = content.replace('deals.cruisedetective.com', 'thecruisedetective.com-176436')
    content = content.replace('deals.thecruisedetective.com', 'www.thecruisedetective.com')
    # 4. Inject / normalize webflow-sync.js
    content = normalize_webflow_sync(content)

    with open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(content)
    log(f"Wrote canal-cruises-amsterdam/index.html ({len(content)} bytes)")

def ingest_thames_cruises():
    dest_dir = os.path.join(ROOT, "thames-river-cruises-london")
    os.makedirs(dest_dir, exist_ok=True)
    url = "https://www.thecruisedetective.com/thames-river-cruises-london"
    content = fetch_url(url)
    content = normalize_webflow_sync(content)
    content = content.replace('deals.cruisedetective.com', 'thecruisedetective.com-176436')
    content = content.replace('deals.thecruisedetective.com', 'www.thecruisedetective.com')

    with open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(content)
    log(f"Wrote thames-river-cruises-london/index.html ({len(content)} bytes)")

def ingest_side_by_side():
    dest_dir = os.path.join(ROOT, "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison")
    os.makedirs(dest_dir, exist_ok=True)
    url = "https://www.thecruisedetective.com/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison"
    content = fetch_url(url)
    content = normalize_webflow_sync(content)
    content = content.replace('deals.cruisedetective.com', 'thecruisedetective.com-176436')
    content = content.replace('deals.thecruisedetective.com', 'www.thecruisedetective.com')

    # Enforce locked Tiqets partner links for Bateaux Mouches (p982924) and Bateaux Parisiens Gourmet Dinner (p974358)
    tiqets_bm_intro = 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&amp;tq_campaign=sidebyside-intro-bm'
    tiqets_bp_intro = 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&amp;tq_campaign=sidebyside-intro-bp'
    tiqets_bm_table = 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&amp;tq_campaign=sidebyside-table-bm'
    tiqets_bp_table = 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&amp;tq_campaign=sidebyside-table-bp'

    # Intro links
    content = re.sub(
        r'<a\s+href=[\"\x27]https://www\.getyourguide\.com/[^\"]*intro-bateaux-mouches[\"\x27][^>]*>Bateaux Mouches</a>',
        f'<a href="{tiqets_bm_intro}" target="_blank" rel="noopener">Bateaux Mouches</a>',
        content
    )
    content = re.sub(
        r'<a\s+href=[\"\x27]https://www\.getyourguide\.com/[^\"]*intro-bateaux-parisiens[\"\x27][^>]*>Bateaux Parisiens</a>',
        f'<a href="{tiqets_bp_intro}" target="_blank" rel="noopener">Bateaux Parisiens</a>',
        content
    )

    # Comparison table header links
    content = re.sub(
        r'<a\s+href=[\"\x27]https://www\.getyourguide\.com/[^\"]*comparison-table-bateaux-mouches[\"\x27][^>]*>Bateaux Mouche Dinner Cruise</a>',
        f'<a href="{tiqets_bm_table}" target="_blank" rel="noopener">Bateaux Mouche Dinner Cruise</a>',
        content
    )
    content = re.sub(
        r'<a\s+href=[\"\x27]https://www\.getyourguide\.com/[^\"]*comparison-table-bateaux-parisiens[\"\x27][^>]*>Bateaux Parisiens Dinner Cruise</a>',
        f'<a href="{tiqets_bp_table}" target="_blank" rel="noopener">Bateaux Parisiens Dinner Cruise</a>',
        content
    )

    # Ensure remaining GetYourGuide widget links have rel="noopener sponsored"
    content = content.replace('rel="sponsored" href="https://www.getyourguide.com/paris-l16/"', 'rel="noopener sponsored" href="https://www.getyourguide.com/paris-l16/"')

    with open(os.path.join(dest_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(content)
    log(f"Wrote bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html ({len(content)} bytes)")

def main():
    log("Beginning Milestone 1 Money Hubs Ingestion...")
    ingest_dinner_cruises()
    ingest_seine_cruises()
    ingest_amsterdam_cruises()
    ingest_thames_cruises()
    ingest_side_by_side()
    log("All 5 money hubs successfully ingested and normalized.")

if __name__ == "__main__":
    main()
