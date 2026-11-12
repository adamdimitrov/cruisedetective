#!/usr/bin/env python3
"""
Localize Webflow Assets & Purge Legacy WebFont Runtime
1. Downloads CSS files into /css/
2. Downloads all images/media into /assets/cdn/
3. Purges webfont.js and WebFont.load snippets from HTML files
4. Replaces external CDN links with local /assets/cdn/ and /css/ paths
"""
import os
import re
import urllib.request
import urllib.parse
import concurrent.futures

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS_DIR = os.path.join(BASE_DIR, "css")
CDN_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "cdn")

os.makedirs(CSS_DIR, exist_ok=True)
os.makedirs(CDN_ASSETS_DIR, exist_ok=True)

# 1. CSS Files to localize
CSS_URLS = [
    "https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/css/thecruisedetective-com.webflow.shared.3cc389acf.min.css",
    "https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/css/thecruisedetective-com.webflow.shared.5dcd01391.min.css",
    "https://cdn.prod.website-files.com/67d02edca7795b0f57073b59/css/luxurytraveltester.webflow.shared.7843214d4.min.css"
]

print("=== Downloading CSS files ===")
for url in CSS_URLS:
    fname = os.path.basename(urllib.parse.urlparse(url).path)
    dest_path = os.path.join(CSS_DIR, fname)
    if not os.path.exists(dest_path):
        print(f"Downloading CSS: {fname}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(dest_path, "wb") as f:
            f.write(resp.read())
        print(f" Saved to {dest_path}")
    else:
        print(f" CSS already exists: {fname}")

# 2. Collect all CDN URLs across codebase
print("\n=== Scanning for all Webflow CDN URLs ===")
raw_urls = set()
for root, dirs, files in os.walk(BASE_DIR):
    if any(p in root for p in [".git", "node_modules", "assets/cdn"]):
        continue
    for f in files:
        if f.endswith((".html", ".css", ".js", ".py")):
            filepath = os.path.join(root, f)
            with open(filepath, "r", encoding="utf-8", errors="ignore") as fp:
                text = fp.read()
                raw_urls.update(re.findall(r'\"(https?://cdn\.prod\.website-files\.com/[^\"]+)\"', text))
                raw_urls.update(re.findall(r'\'(https?://cdn\.prod\.website-files\.com/[^\']+)\'', text))
                raw_urls.update(re.findall(r'url\([\'\"]?(https?://cdn\.prod\.website-files\.com/[^\'\"\)]+)[\'\"]?\)', text))

asset_urls = set()
for entry in raw_urls:
    for part in entry.split(','):
        t = part.strip().split()
        if t and t[0].startswith("http"):
            # Exclude CSS files from image downloader (handled separately)
            if not t[0].endswith(".css"):
                asset_urls.add(t[0])

print(f"Found {len(asset_urls)} media/image assets on cdn.prod.website-files.com")

def download_asset(url):
    parsed = urllib.parse.urlparse(url)
    rel_path = parsed.path.lstrip("/")
    # rel_path is e.g. "652d0405192ba076b04f74a3/65847...webp"
    # Unquote for local disk storage
    disk_rel_path = urllib.parse.unquote(rel_path)
    dest_path = os.path.join(CDN_ASSETS_DIR, disk_rel_path)
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return (url, "already_downloaded", os.path.getsize(dest_path))
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
            return (url, "downloaded", len(data))
    except Exception as e:
        return (url, f"error: {e}", 0)

print(f"\n=== Downloading {len(asset_urls)} assets concurrently ===")
with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
    results = list(executor.map(download_asset, asset_urls))

downloaded = [r for r in results if r[1] == "downloaded"]
already = [r for r in results if r[1] == "already_downloaded"]
errors = [r for r in results if "error" in r[1]]
print(f"Downloaded: {len(downloaded)} | Existing: {len(already)} | Errors: {len(errors)}")
if errors:
    print("Errors:")
    for e in errors[:5]:
        print(" ", e)

