#!/usr/bin/env python3
"""
Generate exact 1-to-1 301 redirects in vercel.json for all 351 dead language URLs
across all 27 dead languages plus wildcard fallback rules.

Preserves existing vercel.json rewrites, functions, cleanUrls, and trailingSlash settings.
"""

import os
import sys
import json
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERCEL_JSON_PATH = os.path.join(PROJECT_ROOT, "vercel.json")
BACKUP_SITEMAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sitemap_production_backup.xml")

APPROVED_LANGUAGES = ["en", "ja", "pl", "ro", "fr", "nl", "es", "de", "it"]
DEAD_LANGUAGES = [
    "ar", "bg", "ca", "cs", "da", "el", "fa", "fi",
    "he", "hi", "hr", "hu", "ko", "no", "pt", "ru", "sk",
    "sr", "sv", "th", "tr", "uk", "vi", "zh"
]

def load_sitemap_xml():
    """Load sitemap XML from local backup or live production endpoint."""
    if os.path.exists(BACKUP_SITEMAP_PATH):
        with open(BACKUP_SITEMAP_PATH, "rb") as f:
            return f.read()
    
    url = "https://www.thecruisedetective.com/sitemap.xml"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        content = resp.read()
        with open(BACKUP_SITEMAP_PATH, "wb") as f:
            f.write(content)
        return content

def extract_redirect_mappings(xml_content):
    """Extract exact 1-to-1 mappings from dead language URLs to English canonical destinations."""
    root = ET.fromstring(xml_content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}

    dead_langs_set = set(DEAD_LANGUAGES)
    redirects = []
    seen_sources = set()

    for u in root.findall("sm:url", ns):
        loc = u.find("sm:loc", ns).text.strip()
        parsed_loc = urllib.parse.urlparse(loc)
        path = parsed_loc.path or "/"
        unquoted_path = urllib.parse.unquote(path)

        parts = unquoted_path.strip("/").split("/", 1)
        lang = parts[0] if parts else ""

        if lang in dead_langs_set:
            # Find English canonical target in hreflang alternates
            target_href = None
            for link in u.findall("xhtml:link", ns):
                hl = link.attrib.get("hreflang")
                if hl in ["en-us", "en"]:
                    target_href = link.attrib.get("href")
                    break
                elif hl == "x-default" and not target_href:
                    target_href = link.attrib.get("href")

            if not target_href:
                raise ValueError(f"No canonical English target found for {loc}")

            target_path = urllib.parse.urlparse(target_href).path or "/"

            if unquoted_path not in seen_sources:
                redirects.append({
                    "source": unquoted_path,
                    "destination": target_path,
                    "permanent": True
                })
                seen_sources.add(unquoted_path)

    # Legacy singular & alternate slug redirects
    legacy_mappings = [
        ("/dinner-cruise-paris", "/dinner-cruises-paris"),
        ("/amsterdam-canal-cruises", "/canal-cruises-amsterdam"),
        ("/it/migliori-crociere-cena-parigi", "/dinner-cruises-paris"),
        ("/zh/巴黎塞纳河晚餐游船", "/dinner-cruises-paris")
    ]
    for src, dst in legacy_mappings:
        if src not in seen_sources:
            redirects.append({
                "source": src,
                "destination": dst,
                "permanent": True
            })
            seen_sources.add(src)

    # Wildcard fallback rules
    lang_pattern = "|".join(DEAD_LANGUAGES)
    fallback_with_slug = f"/:lang({lang_pattern})/:slug*"
    fallback_bare = f"/:lang({lang_pattern})"

    redirects.append({
        "source": fallback_with_slug,
        "destination": "/",
        "permanent": True
    })
    redirects.append({
        "source": fallback_bare,
        "destination": "/",
        "permanent": True
    })

    return redirects

def update_vercel_json(redirects):
    """Inject redirects into vercel.json while preserving all other configuration keys."""
    if not os.path.exists(VERCEL_JSON_PATH):
        raise FileNotFoundError(f"vercel.json not found at {VERCEL_JSON_PATH}")

    with open(VERCEL_JSON_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)

    config["redirects"] = redirects

    with open(VERCEL_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        f.write("\n")

def main():
    print("Loading production sitemap XML...")
    xml_content = load_sitemap_xml()

    print("Extracting 301 redirect mappings for dead languages...")
    redirects = extract_redirect_mappings(xml_content)
    print(f"Generated {len(redirects)} redirect rules (including fallbacks & legacy mappings).")

    print(f"Updating {VERCEL_JSON_PATH}...")
    update_vercel_json(redirects)
    print("Successfully updated vercel.json with 301 redirect configuration.")

if __name__ == "__main__":
    main()
