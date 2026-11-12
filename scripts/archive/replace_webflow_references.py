#!/usr/bin/env python3
"""
Replace all Webflow CDN and WebFont references across the codebase:
1. Strip webfont.js / WebFont.load
2. Replace Webflow CSS CDN links with /css/ local paths (remove SRI hashes)
3. Replace og:image, twitter:image, and JSON-LD CDN URLs with https://www.thecruisedetective.com/assets/cdn/...
4. Replace all other CDN URLs with /assets/cdn/...
"""
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Regex to strip WebFont loader
WEBFONT_REGEX = re.compile(
    r'<script[^>]*src=[\'"][^\'"]*webfont\.js[\'"][^>]*>\s*</script>\s*'
    r'<script[^>]*>\s*WebFont\.load\(\{[\s\S]*?\}\);\s*</script>',
    re.MULTILINE
)

# CSS mapping
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

def process_html(content):
    # 1. Purge WebFont
    content = WEBFONT_REGEX.sub('', content)

    # 2. Localize CSS
    for pat, repl in CSS_REPLACEMENTS:
        content = pat.sub(repl, content)

    # 3. JSON-LD scripts: use full https://www.thecruisedetective.com/assets/cdn/
    def replace_jsonld(match):
        s = match.group(0)
        return s.replace("https://cdn.prod.website-files.com/", "https://www.thecruisedetective.com/assets/cdn/")
    
    content = re.sub(r'<script[^>]*type=[\'"]application/ld\+json[\'"][^>]*>[\s\S]*?</script>', replace_jsonld, content)

    # 4. og:image and twitter:image meta tags
    def replace_meta_img(match):
        tag = match.group(0)
        return tag.replace("https://cdn.prod.website-files.com/", "https://www.thecruisedetective.com/assets/cdn/")

    content = re.sub(r'<meta[^>]+(?:og:image|twitter:image)[^>]+>', replace_meta_img, content)

    # 5. All other occurrences of https://cdn.prod.website-files.com/ -> /assets/cdn/
    content = content.replace("https://cdn.prod.website-files.com/", "/assets/cdn/")
    content = content.replace("http://cdn.prod.website-files.com/", "/assets/cdn/")

    return content

# Target files
html_count = 0
for root, dirs, files in os.walk(BASE_DIR):
    if any(p in root for p in [".git", "node_modules", "assets/cdn"]):
        continue
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as fp:
                orig = fp.read()
            updated = process_html(orig)
            if updated != orig:
                with open(filepath, 'w', encoding='utf-8') as fp:
                    fp.write(updated)
                html_count += 1
                print(f"Updated HTML: {os.path.relpath(filepath, BASE_DIR)}")

# Update CSS files
css_count = 0
for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'css')):
    for f in files:
        if f.endswith('.css'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as fp:
                orig = fp.read()
            updated = orig.replace("https://cdn.prod.website-files.com/", "/assets/cdn/")
            if updated != orig:
                with open(filepath, 'w', encoding='utf-8') as fp:
                    fp.write(updated)
                css_count += 1
                print(f"Updated CSS: {os.path.relpath(filepath, BASE_DIR)}")

# Update Python scripts
py_count = 0
for root, dirs, files in os.walk(os.path.join(BASE_DIR, 'scripts')):
    for f in files:
        if f.endswith('.py') and f != 'replace_webflow_references.py' and f != 'localize_webflow_assets.py':
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as fp:
                orig = fp.read()
            updated = orig.replace("https://cdn.prod.website-files.com/", "/assets/cdn/")
            if updated != orig:
                with open(filepath, 'w', encoding='utf-8') as fp:
                    fp.write(updated)
                py_count += 1
                print(f"Updated Script: {os.path.relpath(filepath, BASE_DIR)}")

print(f"\nCompleted! Total updated: {html_count} HTML, {css_count} CSS, {py_count} Python files.")
