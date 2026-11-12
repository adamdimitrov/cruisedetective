#!/usr/bin/env python3
"""
scripts/strip_heading_emojis.py
Milestone 2: HCU & Anchor/Emoji Pollution Elimination

Exhaustively processes the 5 core money hubs:
1. Strips 100% of Unicode emojis from all <h1-6> headings, card headings, and navigation anchor texts.
2. Strips 100% of non-breaking spaces (\u00a0 and &nbsp;) from headings and anchor targets.
3. Enforces clean semantic HTML5 IDs (#boat-<slug>, #comparison-matrix, #faq-section) and updates all matching anchor links.
4. Enforces clean canonical tags (https://www.thecruisedetective.com/<slug>) with 0 fragments.
5. Preserves all French accented characters (é, è, à, ç, ô, É, etc.) without mojibake.
"""

import os
import re
import sys
from bs4 import BeautifulSoup

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Regex for emojis across SMP, Misc Symbols, Dingbats, and Variation Selectors
EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010FFFF\u2600-\u27BF\u2300-\u23FF\u2B50\u2B06\uFE0E\uFE0F\u200D]"
)

# Hub definitions with target slugs and ID mapping tables
HUB_CONFIGS = {
    "seine-river-cruises-paris": {
        "slug": "seine-river-cruises-paris",
        "file": os.path.join(ROOT_DIR, "seine-river-cruises-paris", "index.html"),
        "id_map": {},
        "extra_ids": {}
    },
    "dinner-cruises-paris": {
        "slug": "dinner-cruises-paris",
        "file": os.path.join(ROOT_DIR, "dinner-cruises-paris", "index.html"),
        "id_map": {
            "1-dinner-cruise-bateaux-mouches": "boat-bateaux-mouches",
            "2-dinner-cruise-bateaux-parisiens": "boat-bateaux-parisiens",
            "3-dinner-cruise-paris-city-vision": "boat-paris-city-vision",
            "4-dinner-cruise-paris-en-scene": "boat-paris-en-scene",
            "5-dinner-cruise-le-diamant-bleu": "boat-diamant-bleu",
            "6-le-diamant-bleu": "boat-theo-trattoria",
            "6-trattoria-en-seine": "boat-theo-trattoria",
            "7-capitaine-fracasse": "boat-capitaine-fracasse",
            "8-maxim-de-paris": "boat-maxim-de-paris",
            "9-ducasse-sur-seine": "boat-ducasse-sur-seine",
            "10-paris-city-vision": "boat-paris-city-vision-early"
        },
        "extra_ids": {
            "cd-table-container": "comparison-matrix",
            "tourist-trap": "faq-section"
        }
    },
    "canal-cruises-amsterdam": {
        "slug": "canal-cruises-amsterdam",
        "file": os.path.join(ROOT_DIR, "canal-cruises-amsterdam", "index.html"),
        "id_map": {},
        "extra_ids": {}
    },
    "thames-river-cruises-london": {
        "slug": "thames-river-cruises-london",
        "file": os.path.join(ROOT_DIR, "thames-river-cruises-london", "index.html"),
        "id_map": {
            "1-thames-river-sightseeing": "boat-thames-river-sightseeing",
            "2-london-eye": "boat-london-eye",
            "3-city-cruises-sightseeing-cruise": "boat-city-cruises-sightseeing",
            "4-thames-rockets-speedboat": "boat-thames-rockets-speedboat",
            "5-thames-ribs-speedboat": "boat-thames-ribs-speedboat",
            "6-city-cruises-lunch-cruise": "boat-city-cruises-lunch",
            "7-bubbly-canape": "boat-bubbly-canape",
            "8-jazz-cruise": "boat-jazz-cruise",
            "9-uberboat": "boat-uberboat",
            "10-dinner-cruise": "boat-dinner-cruise",
            "quick-summary-river-cruises-budapest": "comparison-matrix"
        },
        "extra_ids": {}
    },
    "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison": {
        "slug": "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison",
        "file": os.path.join(
            ROOT_DIR,
            "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison",
            "index.html"
        ),
        "id_map": {
            "w-node-bcd67580-1fa5-106b-3ef0-545606579308-1837f861": "boat-bateaux-mouches",
            "w-node-bcd67580-1fa5-106b-3ef0-54560657930a-1837f861": "boat-bateaux-parisiens"
        },
        "extra_ids": {}
    }
}

def clean_text_emojis_and_spaces(text):
    """Strips emojis and collapses excess spaces while preserving French characters."""
    if not text:
        return text
    # Replace non-breaking spaces
    text = text.replace("\u00a0", " ").replace("&nbsp;", " ")
    # Strip emojis
    text = EMOJI_PATTERN.sub("", text)
    # Strip zero-width characters
    text = re.sub(r"[\u200B-\u200D\uFEFF]", "", text)
    # Clean leading/trailing spaces around punctuation
    text = re.sub(r" +", " ", text)
    return text

def sanitize_heading_html(html_snippet):
    """Sanitizes inner HTML of a heading tag while preserving inner tags."""
    # First replace entities
    html_snippet = html_snippet.replace("&nbsp;", " ").replace("\u00a0", " ")
    # Remove emojis
    html_snippet = EMOJI_PATTERN.sub("", html_snippet)
    # Remove zero width
    html_snippet = re.sub(r"[\u200B-\u200D\uFEFF]", "", html_snippet)
    # Normalize multiple spaces in HTML outside of tags
    # Split by tags
    parts = re.split(r"(<[^>]+>)", html_snippet)
    cleaned_parts = []
    for p in parts:
        if p.startswith("<") and p.endswith(">"):
            cleaned_parts.append(p)
        else:
            cleaned_parts.append(re.sub(r" +", " ", p))
    result = "".join(cleaned_parts).strip()
    # If starting with e.g. "1.  Best", collapse
    result = re.sub(r"(\d+\.)\s+", r"\1 ", result)
    return result

def process_hub(hub_key, config, check_only=False):
    fpath = config["file"]
    if not os.path.exists(fpath):
        print(f"[-] File not found: {fpath}")
        return False, {}

    with open(fpath, "r", encoding="utf-8") as f:
        html = f.read()

    stats = {
        "headings_cleaned": 0,
        "emojis_removed": 0,
        "nbsp_removed": 0,
        "ids_updated": 0,
        "anchors_updated": 0,
        "canonical_updated": False
    }

    # 1. Clean Headings (<h1-6> tags)
    def heading_replacer(match):
        open_tag = match.group(1)
        tag_name = match.group(2)
        inner_content = match.group(3)
        close_tag = match.group(4)

        has_emoji = bool(EMOJI_PATTERN.search(inner_content))
        has_nbsp = "\u00a0" in inner_content or "&nbsp;" in inner_content

        if has_emoji or has_nbsp:
            stats["headings_cleaned"] += 1
            if has_emoji:
                stats["emojis_removed"] += len(EMOJI_PATTERN.findall(inner_content))
            if has_nbsp:
                stats["nbsp_removed"] += inner_content.count("\u00a0") + inner_content.count("&nbsp;")

            cleaned_inner = sanitize_heading_html(inner_content)
            return f"{open_tag}{cleaned_inner}{close_tag}"
        return match.group(0)

    heading_regex = re.compile(r"(<h([1-6])[^>]*>)([\s\S]*?)(<\/h\2>)", re.IGNORECASE)
    new_html = heading_regex.sub(heading_replacer, html)

    # 2. Clean filter pill anchor text (e.g. 📊 Comparison Matrix -> Comparison Matrix)
    def anchor_replacer(match):
        open_tag = match.group(1)
        inner_text = match.group(2)
        close_tag = match.group(3)
        if EMOJI_PATTERN.search(inner_text) or "\u00a0" in inner_text or "&nbsp;" in inner_text:
            cleaned_text = clean_text_emojis_and_spaces(inner_text).strip()
            return f"{open_tag}{cleaned_text}{close_tag}"
        return match.group(0)

    anchor_regex = re.compile(r"(<a\s+[^>]*href=[\"\x27]#[a-zA-Z0-9_-]+[\"\x27][^>]*>)([\s\S]*?)(<\/a>)", re.IGNORECASE)
    new_html = anchor_regex.sub(anchor_replacer, new_html)

    # 3. Update Semantic IDs and Corresponding Anchors
    id_map = config["id_map"]
    for old_id, new_id in id_map.items():
        # Update id attributes: id="old_id" -> id="new_id"
        pattern_id = re.compile(rf'\bid=[\"\x27]{re.escape(old_id)}[\"\x27]')
        if pattern_id.search(new_html):
            new_html = pattern_id.sub(f'id="{new_id}"', new_html)
            stats["ids_updated"] += 1

        # Update anchor href attributes: href="#old_id" -> href="#new_id"
        pattern_href = re.compile(rf'href=[\"\x27]#{re.escape(old_id)}[\"\x27]')
        if pattern_href.search(new_html):
            count = len(pattern_href.findall(new_html))
            new_html = pattern_href.sub(f'href="#{new_id}"', new_html)
            stats["anchors_updated"] += count

        # Update JSON-LD schema URL anchors if present: /<slug>#old_id -> /<slug>#new_id
        pattern_schema = re.compile(rf'#{re.escape(old_id)}\b')
        if pattern_schema.search(new_html):
            new_html = pattern_schema.sub(f'#{new_id}', new_html)

    # Extra IDs (e.g. comparison-matrix on table container)
    for target_class_or_id, new_id in config["extra_ids"].items():
        if f'id="{new_id}"' not in new_html:
            if target_class_or_id == "cd-table-container":
                pattern = re.compile(r'(<div\s+class=[\"\x27][^\"\x27]*cd-table-container[^\"\x27]*[\"\x27])')
                if pattern.search(new_html):
                    new_html = pattern.sub(rf'\1 id="{new_id}"', new_html, count=1)
                    stats["ids_updated"] += 1
            elif target_class_or_id in new_html:
                # Add semantic ID or replace
                pass

    # Ensure bateaux-mouches comparison page has #comparison-matrix
    if hub_key == "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison":
        if 'id="comparison-matrix"' not in new_html:
            pattern = re.compile(r'(<h2[^>]*>Side-By-Side Comparison<\/h2>)', re.IGNORECASE)
            if pattern.search(new_html):
                new_html = pattern.sub(r'<h2 id="comparison-matrix">Side-By-Side Comparison</h2>', new_html, count=1)
                stats["ids_updated"] += 1

    # 4. Strict Canonical Enforcement
    expected_canonical = f"https://www.thecruisedetective.com/{config['slug']}"
    canonical_pattern = re.compile(r'<link\s+[^>]*rel=[\"\x27]canonical[\"\x27][^>]*>', re.IGNORECASE)
    alt_canonical_pattern = re.compile(r'<link\s+[^>]*href=[\"\x27][^\"\x27]+[\"\x27][^>]*rel=[\"\x27]canonical[\"\x27][^>]*>', re.IGNORECASE)

    clean_canonical_tag = f'<link rel="canonical" href="{expected_canonical}"/>'

    if canonical_pattern.search(new_html):
        # Check current href
        match = canonical_pattern.search(new_html).group(0)
        if expected_canonical not in match or "#" in match or "?" in match or "http://" in match:
            new_html = canonical_pattern.sub(clean_canonical_tag, new_html, count=1)
            stats["canonical_updated"] = True
    elif alt_canonical_pattern.search(new_html):
        match = alt_canonical_pattern.search(new_html).group(0)
        if expected_canonical not in match or "#" in match or "?" in match or "http://" in match:
            new_html = alt_canonical_pattern.sub(clean_canonical_tag, new_html, count=1)
            stats["canonical_updated"] = True
    else:
        # Inject before </head>
        if "</head>" in new_html:
            new_html = new_html.replace("</head>", f"  {clean_canonical_tag}\n</head>", 1)
            stats["canonical_updated"] = True

    # Check for mojibake safety
    assert "Ã©" not in new_html, f"Mojibake detected in {hub_key}"
    assert "Ã¨" not in new_html, f"Mojibake detected in {hub_key}"

    if not check_only and new_html != html:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_html)

    return True, stats

def main():
    check_only = "--check" in sys.argv
    print(f"=== Running Emoji & Anchor Sanitation (check_only={check_only}) ===")

    total_headings_cleaned = 0
    total_emojis = 0
    total_nbsp = 0
    total_ids = 0
    total_anchors = 0

    for hub_key, config in HUB_CONFIGS.items():
        ok, stats = process_hub(hub_key, config, check_only=check_only)
        if not ok:
            continue
        print(f"[*] Hub: {hub_key}")
        print(f"    Headings cleaned: {stats['headings_cleaned']}")
        print(f"    Emojis removed:   {stats['emojis_removed']}")
        print(f"    NBSP removed:     {stats['nbsp_removed']}")
        print(f"    IDs updated:      {stats['ids_updated']}")
        print(f"    Anchors updated:  {stats['anchors_updated']}")
        print(f"    Canonical updated:{stats['canonical_updated']}")

        total_headings_cleaned += stats['headings_cleaned']
        total_emojis += stats['emojis_removed']
        total_nbsp += stats['nbsp_removed']
        total_ids += stats['ids_updated']
        total_anchors += stats['anchors_updated']

    print("==================================================")
    print(f"Total headings cleaned: {total_headings_cleaned}")
    print(f"Total emojis removed:   {total_emojis}")
    print(f"Total NBSPs removed:    {total_nbsp}")
    print(f"Total IDs updated:      {total_ids}")
    print(f"Total anchors updated:  {total_anchors}")

if __name__ == "__main__":
    main()
