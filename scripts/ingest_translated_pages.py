#!/usr/bin/env python3
"""
Ingest, Localize, and Self-Host Active Translated Pages (Choice 2)
Scope: 64 active URLs across the 5 approved languages (ja, fr, nl, pl, ro).

1. Fetches rendered HTML from live production.
2. Purges legacy WebFont scripts.
3. Localizes Webflow CSS links to /css/.
4. Localizes image CDN URLs to /assets/cdn/ and downloads any missing image assets.
5. Injects client-side webflow-sync.js tracking.
6. Saves static HTML into <lang>/<slug>/index.html.
"""

import os
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import concurrent.futures

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(BASE_DIR, "css")
CDN_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "cdn")
SITEMAP_PATH = os.path.join(BASE_DIR, "sitemap.xml")

APPROVED_LANGS = ["ja", "fr", "nl", "pl", "ro"]

# 1. Discover all active URLs from sitemap.xml
tree = ET.parse(SITEMAP_PATH)
root = tree.getroot()
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

all_locs = [u.find("sm:loc", ns).text.strip() for u in root.findall("sm:url", ns)]

target_urls = set()
for loc in all_locs:
    for lang in APPROVED_LANGS:
        if f"/{lang}/" in loc or loc.endswith(f"/{lang}"):
            target_urls.add(loc)

for lang in APPROVED_LANGS:
    target_urls.add(f"https://www.thecruisedetective.com/{lang}")

target_urls = sorted(list(target_urls))
print(f"Discovered {len(target_urls)} active translated URLs to ingest.")

# Regex patterns for cleanup
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

# Check for any new image assets from scraped pages
print("\n=== Discovering and downloading any new image assets ===")
new_asset_urls = set()
for url, status, html in success_pages:
    found = re.findall(r'https?://cdn\.prod\.website-files\.com/[^\s\"\'\)\>]+', html)
    for asset in found:
        asset_clean = asset.split(',')[0].strip().rstrip('.,;()')
        if not asset_clean.endswith(".css"):
            new_asset_urls.add(asset_clean)

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

# Process and save each translated page
print("\n=== Processing and saving translated HTML files ===")
saved_count = 0

for url, status, html in success_pages:
    parsed = urllib.parse.urlparse(url)
    unquoted_path = urllib.parse.unquote(parsed.path).strip("/")
    
    # Target directory on disk
    dest_file = os.path.join(BASE_DIR, unquoted_path, "index.html")
    os.makedirs(os.path.dirname(dest_file), exist_ok=True)

    # 1. Purge WebFont
    content = WEBFONT_REGEX.sub("", html)

    # 2. Purge Webflow preconnect
    content = PRECONNECT_CDN_REGEX.sub("", content)

    # 3. Localize CSS
    for pat, repl in CSS_REPLACEMENTS:
        content = pat.sub(repl, content)

    # 4. JSON-LD scripts: use full https://www.thecruisedetective.com/assets/cdn/
    def replace_jsonld(match):
        s = match.group(0)
        return s.replace("https://cdn.prod.website-files.com/", "https://www.thecruisedetective.com/assets/cdn/")
    
    content = re.sub(r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>[\s\S]*?</script>', replace_jsonld, content)

    # 5. og:image and twitter:image meta tags
    def replace_meta_img(match):
        tag = match.group(0)
        return tag.replace("https://cdn.prod.website-files.com/", "https://www.thecruisedetective.com/assets/cdn/")

    content = re.sub(r'<meta[^>]+(?:og:image|twitter:image)[^>]+>', replace_meta_img, content)

    # 6. All other occurrences of https://cdn.prod.website-files.com/ -> /assets/cdn/
    content = content.replace("https://cdn.prod.website-files.com/", "/assets/cdn/")
    content = content.replace("http://cdn.prod.website-files.com/", "/assets/cdn/")

    # 7. Ensure webflow-sync.js tracking script is present before </body>
    if "/webflow-sync.js" not in content and "webflow-sync.js" not in content:
        if "</body>" in content:
            content = content.replace("</body>", '  <script src="/webflow-sync.js"></script>\n</body>')
        else:
            content += '\n<script src="/webflow-sync.js"></script>'

    with open(dest_file, "w", encoding="utf-8") as f:
        f.write(content)
    saved_count += 1
    print(f"Saved: {os.path.relpath(dest_file, BASE_DIR)}")

print(f"\nIngestion Complete! Successfully saved {saved_count} translated pages.")
