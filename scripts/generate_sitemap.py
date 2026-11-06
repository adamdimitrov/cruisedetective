#!/usr/bin/env python3
"""
Generate clean sitemap.xml at project root containing strictly the 77 active canonical URLs
across the 6 approved languages (en, ja, pl, ro, fr, nl).

Enforces:
- Exactly 77 active canonical <loc> entries
- Strictly approved languages (en, en-us, ja, pl, ro, fr, nl) and x-default in xhtml:link alternates
- Zero dead languages
- Zero fragment hashes (#)
"""

import os
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITEMAP_OUTPUT_PATH = os.path.join(PROJECT_ROOT, "sitemap.xml")
BACKUP_SITEMAP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sitemap_production_backup.xml")

APPROVED_LANGUAGES = ["en", "ja", "pl", "ro", "fr", "nl"]
ALLOWED_HREFLANGS = {"en", "en-us", "ja", "pl", "ro", "fr", "nl", "x-default"}

DEAD_LANGUAGES = [
    "ar", "bg", "ca", "cs", "da", "de", "el", "es", "fa", "fi",
    "he", "hi", "hr", "hu", "it", "ko", "no", "pt", "ru", "sk",
    "sr", "sv", "th", "tr", "uk", "vi", "zh"
]

def load_source_sitemap_xml():
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

def is_approved_loc(loc):
    """Determine if a <loc> URL belongs to one of the 6 approved languages."""
    parsed = urllib.parse.urlparse(loc)
    path = parsed.path or "/"
    unquoted = urllib.parse.unquote(path)
    parts = unquoted.strip("/").split("/", 1)
    prefix = parts[0] if parts and parts[0] else ""

    # Dead language prefix check
    if prefix in DEAD_LANGUAGES:
        return False

    # Approved language prefixes or root/English
    if prefix in ["ja", "pl", "ro", "fr", "nl"]:
        return True
    
    # If prefix is not a known dead language and not an approved localized prefix, it is English (e.g. '', 'about', 'dinner-cruises-paris')
    return True

def generate_clean_sitemap(xml_content):
    """Filter and build clean 77-URL sitemap.xml."""
    root = ET.fromstring(xml_content)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}

    ET.register_namespace("", "http://www.sitemaps.org/schemas/sitemap/0.9")
    ET.register_namespace("xhtml", "http://www.w3.org/1999/xhtml")

    new_root = ET.Element("{http://www.sitemaps.org/schemas/sitemap/0.9}urlset")

    approved_urls = []
    for u in root.findall("sm:url", ns):
        loc_el = u.find("sm:loc", ns)
        if loc_el is None or not loc_el.text:
            continue
        loc = loc_el.text.strip()
        if "#" in loc:
            continue
        if is_approved_loc(loc):
            approved_urls.append((loc, u))

    print(f"Discovered {len(approved_urls)} approved URLs matching 6 approved languages.")
    assert len(approved_urls) == 77, f"Expected exactly 77 approved URLs, got {len(approved_urls)}"

    for loc, old_url in approved_urls:
        new_url = ET.SubElement(new_root, "{http://www.sitemaps.org/schemas/sitemap/0.9}url")

        new_loc = ET.SubElement(new_url, "{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        new_loc.text = loc

        lastmod_el = old_url.find("sm:lastmod", ns)
        if lastmod_el is not None and lastmod_el.text:
            new_lastmod = ET.SubElement(new_url, "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod")
            new_lastmod.text = lastmod_el.text.strip()

        for link in old_url.findall("xhtml:link", ns):
            hl = link.attrib.get("hreflang", "").lower()
            href = link.attrib.get("href", "").strip()
            if hl in ALLOWED_HREFLANGS and "#" not in href:
                new_link = ET.SubElement(new_url, "{http://www.w3.org/1999/xhtml}link")
                new_link.attrib["rel"] = "alternate"
                new_link.attrib["hreflang"] = hl
                new_link.attrib["href"] = href

    # Format XML with clean indentation
    ET.indent(new_root, space="  ", level=0)
    xml_str = ET.tostring(new_root, encoding="utf-8", xml_declaration=True)

    with open(SITEMAP_OUTPUT_PATH, "wb") as f:
        f.write(xml_str)
        f.write(b"\n")

    print(f"Clean sitemap successfully generated at {SITEMAP_OUTPUT_PATH} (77 URLs).")

def main():
    print("Loading source sitemap XML...")
    xml_content = load_source_sitemap_xml()

    print("Generating clean sitemap.xml for approved languages...")
    generate_clean_sitemap(xml_content)

if __name__ == "__main__":
    main()
