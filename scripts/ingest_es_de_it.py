#!/usr/bin/env python3
"""
Ingest and Localize Spanish (es), German (de), and Italian (it) Pages
"""

import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import concurrent.futures

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(BASE_DIR, "css")
CDN_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "cdn")
BACKUP_SITEMAP_PATH = os.path.join(BASE_DIR, "scripts", "sitemap_production_backup.xml")

NEW_LANGS = ["es", "de", "it"]

tree = ET.parse(BACKUP_SITEMAP_PATH)
root = tree.getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

all_locs = [u.find("sm:loc", ns).text.strip() for u in root.findall("sm:url", ns)]

target_urls = set()
for loc in all_locs:
    clean_loc = loc.split('#')[0]
    for lang in NEW_LANGS:
        if f"/{lang}/" in clean_loc or clean_loc.endswith(f"/{lang}"):
            target_urls.add(clean_loc)

for lang in NEW_LANGS:
    target_urls.add(f"https://www.thecruisedetective.com/{lang}")

target_urls = sorted(list(target_urls))
print(f"Discovered {len(target_urls)} URLs to ingest for {NEW_LANGS}:")
for u in target_urls:
    print(" ", u)

WEBFONT_REGEX = re.compile(
    r'<script[^>]*src=[\'"][^\'"]*webfont\.js[\'"][^>]*>\s*</script>\s*'
    r'<script[^>]*>\s*WebFont\.load\(\{[\s\S]*?\}\);\s*</script>',
    re.MULTILINE
)

PRECONNECT_CDN_REGEX = re.compile(r'<link[^>]*href=["\']https://cdn\.prod\.website-files\.com["\'][^>]*>\s*')

CSS_REPLACEMENTS = [
    (
        re.compile(r'<link[^>]*href=[\'"]https://cdn\.prod\.website-files\.com/652d0405192ba076b04f74a3/css/thecruisedetective-com\.webflow\.shared\.3cc389acf\.min\.css[\'"][^>]*>'),
        '<link rel="stylesheet" type="text/css" href="/css/thecruisedetective-com.webflow.shared.3cc389acf.min.css"/>'
    ),
    (
        re.compile(r'<link[^>]*href=[\'"]https://cdn\.prod\.website-files\.com/652d0405192ba076b04f74a3/css/thecruisedetective-com\.webflow\.shared\.5dcd01391\.min\.css[\'"][^>]*>'),
        '<link rel="stylesheet" type="text/css" href="/css/thecruisedetective-com.webflow.shared.5dcd01391.min.css"/>'
    ),
    (
        re.compile(r'<link[^>]*href=[\'"]https://cdn\.prod\.website-files\.com/67d02edca7795b0f57073b59/css/luxurytraveltester\.webflow\.shared\.7843214d4\.min\.css[\'"][^>]*>'),
        '<link rel="stylesheet" type="text/css" href="/css/luxurytraveltester.webflow.shared.7843214d4.min.css"/>'
    )
]

def fetch_url(url):
    quoted = urllib.parse.quote(url, safe="/:")
    req = urllib.request.Request(quoted, headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            return (url, resp.status, content)
    except Exception as e:
        return (url, 0, str(e))

print(f"\n=== Fetching {len(target_urls)} pages concurrently ===")
with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
    fetched = list(executor.map(fetch_url, target_urls))

success_pages = [p for p in fetched if p[1] == 200]
error_pages = [p for p in fetched if p[1] != 200]

print(f"Successfully fetched: {len(success_pages)} | Errors: {len(error_pages)}")
if error_pages:
    for u, status, err in error_pages:
        print(f"  [ERROR {status}] {u}: {err}")

# Check for missing images
print("\n=== Discovering and downloading any missing image assets ===")
new_asset_urls = set()
for url, status, html in success_pages:
    found = re.findall(r'https?://cdn\.prod\.website-files\.com/[^\s\"\'\)\>]+', html)
    for asset in found:
        tokens = asset.split()
        if tokens and tokens[0].startswith("http"):
            clean_url = tokens[0].split(',')[0].strip().rstrip('.,;')
            if not clean_url.endswith(".css"):
                new_asset_urls.add(clean_url)

def download_missing_asset(url):
    parsed = urllib.parse.urlparse(url)
    rel_path = urllib.parse.unquote(parsed.path.lstrip("/"))
    dest_path = os.path.join(CDN_ASSETS_DIR, rel_path)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return False
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            with open(dest_path, "wb") as f:
                f.write(data)
            return True
    except Exception:
        return False

with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    downloaded_flags = list(executor.map(download_missing_asset, new_asset_urls))

newly_downloaded = sum(1 for d in downloaded_flags if d)
print(f"Checked {len(new_asset_urls)} referenced assets. Newly downloaded: {newly_downloaded}")

# Process and save HTML files
print("\n=== Saving HTML files ===")
saved_count = 0
for url, status, html in success_pages:
    parsed = urllib.parse.urlparse(url)
    unquoted_path = urllib.parse.unquote(parsed.path).strip("/")
    
    dest_file = os.path.join(BASE_DIR, unquoted_path, "index.html")
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

    content = WEBFONT_REGEX.sub("", html)
    content = PRECONNECT_CDN_REGEX.sub("", content)

    for pat, repl in CSS_REPLACEMENTS:
        content = pat.sub(repl, content)

    def replace_jsonld(match):
        return match.group(0).replace("https://cdn.prod.website-files.com/", "https://www.thecruisedetective.com/assets/cdn/")
    content = re.sub(r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>[\s\S]*?</script>', replace_jsonld, content)

    def replace_meta_img(match):
        return match.group(0).replace("https://cdn.prod.website-files.com/", "https://www.thecruisedetective.com/assets/cdn/")
    content = re.sub(r'<meta[^>]+(?:og:image|twitter:image)[^>]+>', replace_meta_img, content)

    content = content.replace("https://cdn.prod.website-files.com/", "/assets/cdn/")
    content = content.replace("http://cdn.prod.website-files.com/", "/assets/cdn/")

    if "/webflow-sync.js" not in content and "webflow-sync.js" not in content:
        if "</body>" in content:
            content = content.replace("</body>", '  <script src="/webflow-sync.js"></script>\n</body>')
        else:
            content += '\n<script src="/webflow-sync.js"></script>'

    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(content)
    saved_count += 1
    print(f"Saved: {os.path.relpath(dest_file, BASE_DIR)}")

print(f"\nIngested {saved_count} pages for {NEW_LANGS}.")
