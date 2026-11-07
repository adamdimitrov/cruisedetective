#!/usr/bin/env python3
"""
test/test_m2_anchors.py
Milestone 2 Verification Test Suite: HCU & Anchor/Emoji Pollution Elimination

Exhaustively verifies:
1. 0 Unicode emojis in any <h1-6> heading across all 5 core money hubs.
2. 0 literal non-breaking spaces (\\u00a0) or &nbsp; entities in headings.
3. 0 hex-encoded emoji sequences in IDs (%F0%, %E2%, etc.).
4. 0 "cruisenbspwith" or "nbsp" in anchor IDs.
5. HTML5 ID syntax validity (non-empty, no whitespace).
6. In-page anchor links match target elements (0 broken internal anchors).
7. Semantic naming conventions for boat anchors (^boat-[a-z0-9-]+$).
8. Strict canonical tag format (https://www.thecruisedetective.com/<slug>, 0 fragments, 0 queries, no trailing slash).
9. Preservation of French accented characters without mojibake.
"""

import os
import re
import sys
import unittest
from bs4 import BeautifulSoup

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

CORE_MONEY_HUBS = [
    {
        "slug": "seine-river-cruises-paris",
        "file": os.path.join(PROJECT_ROOT, "seine-river-cruises-paris", "index.html"),
        "expected_canonical": "https://www.thecruisedetective.com/seine-river-cruises-paris",
        "expected_boat_ids": [
            "boat-bateaux-parisiens",
            "boat-bateaux-mouches",
            "boat-vedettes-de-paris",
            "boat-batobus",
            "boat-paris-canal"
        ]
    },
    {
        "slug": "dinner-cruises-paris",
        "file": os.path.join(PROJECT_ROOT, "dinner-cruises-paris", "index.html"),
        "expected_canonical": "https://www.thecruisedetective.com/dinner-cruises-paris",
        "expected_boat_ids": [
            "boat-bateaux-mouches",
            "boat-bateaux-parisiens",
            "boat-paris-city-vision",
            "boat-paris-en-scene",
            "boat-diamant-bleu"
        ]
    },
    {
        "slug": "canal-cruises-amsterdam",
        "file": os.path.join(PROJECT_ROOT, "canal-cruises-amsterdam", "index.html"),
        "expected_canonical": "https://www.thecruisedetective.com/canal-cruises-amsterdam",
        "expected_boat_ids": [
            "boat-lovers-canal",
            "boat-captain-jack",
            "boat-flagship",
            "boat-blue-boat",
            "boat-friendship"
        ]
    },
    {
        "slug": "thames-river-cruises-london",
        "file": os.path.join(PROJECT_ROOT, "thames-river-cruises-london", "index.html"),
        "expected_canonical": "https://www.thecruisedetective.com/thames-river-cruises-london",
        "expected_boat_ids": [
            "boat-thames-river-sightseeing",
            "boat-london-eye",
            "boat-city-cruises-sightseeing"
        ]
    },
    {
        "slug": "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison",
        "file": os.path.join(
            PROJECT_ROOT,
            "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison",
            "index.html"
        ),
        "expected_canonical": "https://www.thecruisedetective.com/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison",
        "expected_boat_ids": [
            "boat-bateaux-mouches",
            "boat-bateaux-parisiens"
        ]
    }
]

EMOJI_REGEX = re.compile(
    r"[\U00010000-\U0010FFFF\u2600-\u27BF\u2300-\u23FF\u2B50\u2B06\uFE0E\uFE0F\u200D]"
)

class TestMilestone2AnchorsAndHeadings(unittest.TestCase):

    def setUp(self):
        self.hubs_data = {}
        for hub in CORE_MONEY_HUBS:
            self.assertTrue(
                os.path.exists(hub["file"]),
                f"Core money hub HTML must exist at {hub['file']}"
            )
            with open(hub["file"], "r", encoding="utf-8") as f:
                content = f.read()
            soup = BeautifulSoup(content, "html.parser")
            self.hubs_data[hub["slug"]] = {
                "config": hub,
                "raw_html": content,
                "soup": soup
            }

    # =========================================================================
    # Group 1: Headings - Zero Unicode Emojis & Zero NBSP
    # =========================================================================

    def test_headings_contain_zero_unicode_emojis(self):
        """Verify 100% of <h1-6> headings contain zero Unicode emojis."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            headings = soup.find_all(re.compile(r"^h[1-6]$"))
            self.assertGreater(len(headings), 0, f"{slug} must contain heading tags")
            for h in headings:
                text = h.get_text()
                match = EMOJI_REGEX.search(text)
                self.assertIsNone(
                    match,
                    f"Heading in {slug} contains forbidden emoji '{match.group(0) if match else ''}' in: '{text}'"
                )

    def test_headings_contain_zero_literal_nbsp(self):
        """Verify 100% of headings contain zero literal \\u00a0 characters."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            headings = soup.find_all(re.compile(r"^h[1-6]$"))
            for h in headings:
                text = h.get_text()
                self.assertNotIn(
                    "\u00a0",
                    text,
                    f"Heading in {slug} contains literal \\u00a0 non-breaking space: '{text}'"
                )

    def test_headings_contain_zero_raw_nbsp_entities(self):
        """Verify 100% of heading markup contains zero &nbsp; HTML entities."""
        for slug, data in self.hubs_data.items():
            raw_html = data["raw_html"]
            heading_matches = re.findall(r"<h[1-6][^>]*>[\s\S]*?<\/h[1-6]>", raw_html, re.I)
            for h_markup in heading_matches:
                self.assertNotIn(
                    "&nbsp;",
                    h_markup,
                    f"Heading markup in {slug} contains raw &nbsp; entity: '{h_markup}'"
                )

    def test_french_accents_preserved_without_mojibake(self):
        """Verify valid French accented characters are preserved without UTF-8 mojibake."""
        for slug, data in self.hubs_data.items():
            raw_html = data["raw_html"]
            self.assertNotIn("Ã©", raw_html, f"{slug} contains mojibake 'Ã©'")
            self.assertNotIn("Ã¨", raw_html, f"{slug} contains mojibake 'Ã¨'")
            self.assertNotIn("Ã ", raw_html, f"{slug} contains mojibake 'Ã '")
            self.assertNotIn("Ã´", raw_html, f"{slug} contains mojibake 'Ã´'")

    def test_card_headings_and_matrix_columns_contain_zero_emojis(self):
        """Verify nested headings in comparison cards maintain zero emojis."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            card_headings = soup.select(".boat-card h2, .boat-card h3, .cd-col-boat, .card h3")
            for ch in card_headings:
                text = ch.get_text()
                match = EMOJI_REGEX.search(text)
                self.assertIsNone(
                    match,
                    f"Card heading in {slug} contains emoji '{match.group(0) if match else ''}': '{text}'"
                )

    # =========================================================================
    # Group 2: Anchor IDs & Semantic HTML5 Standards
    # =========================================================================

    def test_zero_hex_encoded_emoji_ids(self):
        """Verify 0 hex-encoded emoji sequences in any id attribute."""
        hex_pattern = re.compile(r"%F0%|%E2%|%8F%|%9F%", re.I)
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            elements_with_id = soup.find_all(id=True)
            for el in elements_with_id:
                eid = el["id"]
                self.assertFalse(
                    hex_pattern.search(eid),
                    f"Element in {slug} has hex-encoded emoji id: '{eid}'"
                )

    def test_zero_cruisenbspwith_or_nbsp_in_ids(self):
        """Verify 0 occurrences of 'cruisenbspwith' or 'nbsp' in anchor IDs."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            elements_with_id = soup.find_all(id=True)
            for el in elements_with_id:
                eid = el["id"].lower()
                self.assertNotIn(
                    "cruisenbspwith",
                    eid,
                    f"Element in {slug} has corrupt 'cruisenbspwith' id: '{el['id']}'"
                )
                self.assertNotIn(
                    "nbsp",
                    eid,
                    f"Element in {slug} has corrupt 'nbsp' id: '{el['id']}'"
                )

    def test_html5_id_specifications(self):
        """Verify all IDs conform to HTML5 spec (non-empty, no whitespace)."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            elements_with_id = soup.find_all(id=True)
            self.assertGreater(len(elements_with_id), 0, f"{slug} must have IDs")
            for el in elements_with_id:
                eid = el["id"]
                self.assertGreater(len(eid), 0, f"Empty ID found in {slug}")
                self.assertFalse(
                    bool(re.search(r"\s", eid)),
                    f"Whitespace found in ID in {slug}: '{eid}'"
                )

    def test_boat_anchor_ids_conform_to_semantic_format(self):
        """Verify any ID with 'boat-' strictly conforms to ^boat-[a-z0-9-]+$."""
        boat_pattern = re.compile(r"^boat-[a-z0-9-]+$")
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            boat_elements = [el for el in soup.find_all(id=True) if "boat-" in el["id"]]
            for el in boat_elements:
                eid = el["id"]
                self.assertTrue(
                    boat_pattern.match(eid),
                    f"Boat anchor ID in {slug} must match ^boat-[a-z0-9-]+$, got: '{eid}'"
                )

    def test_expected_boat_ids_present(self):
        """Verify all required semantic boat IDs are present in their respective hubs."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            all_ids = set(el["id"] for el in soup.find_all(id=True))
            for expected_id in data["config"]["expected_boat_ids"]:
                self.assertIn(
                    expected_id,
                    all_ids,
                    f"Required semantic ID '{expected_id}' missing from {slug}"
                )

    def test_internal_anchor_links_have_matching_targets(self):
        """Verify 100% of in-page anchor links match a valid element ID (0 broken anchors)."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            all_ids = set(el["id"] for el in soup.find_all(id=True))
            anchors = [
                a["href"] for a in soup.find_all("a", href=True)
                if a["href"].startswith("#") and a["href"] != "#"
            ]
            for href in anchors:
                target_id = href[1:]
                self.assertIn(
                    target_id,
                    all_ids,
                    f"Broken internal anchor '{href}' in {slug} has no matching element id"
                )

    def test_comparison_matrix_id_present(self):
        """Verify #comparison-matrix ID exists in all core money hubs."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            all_ids = set(el["id"] for el in soup.find_all(id=True))
            self.assertIn(
                "comparison-matrix",
                all_ids,
                f"Missing required '#comparison-matrix' ID in {slug}"
            )

    # =========================================================================
    # Group 3: Canonical Tag Strict Enforcement
    # =========================================================================

    def test_canonical_tag_exists_and_matches_exact_slug(self):
        """Verify canonical tag is present and points to clean HTTPS canonical URL."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            canon = soup.find("link", rel=lambda v: v and "canonical" in v.lower())
            self.assertIsNotNone(canon, f"Canonical tag missing from {slug}")
            href = canon.get("href", "")
            expected = data["config"]["expected_canonical"]
            self.assertEqual(
                href,
                expected,
                f"Canonical href in {slug} must equal '{expected}', got '{href}'"
            )

    def test_canonical_tag_has_zero_fragments(self):
        """Verify canonical tags contain zero '#' fragment characters."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            canon = soup.find("link", rel=lambda v: v and "canonical" in v.lower())
            href = canon.get("href", "")
            self.assertNotIn("#", href, f"Canonical href in {slug} contains fragment '#': '{href}'")

    def test_canonical_tag_has_zero_query_parameters(self):
        """Verify canonical tags contain zero '?' query parameters."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            canon = soup.find("link", rel=lambda v: v and "canonical" in v.lower())
            href = canon.get("href", "")
            self.assertNotIn("?", href, f"Canonical href in {slug} contains query '?': '{href}'")

    def test_canonical_tag_rejects_insecure_or_unauthorized_domains(self):
        """Verify canonical tags use HTTPS and production domain thecruisedetective.com."""
        for slug, data in self.hubs_data.items():
            soup = data["soup"]
            canon = soup.find("link", rel=lambda v: v and "canonical" in v.lower())
            href = canon.get("href", "")
            self.assertTrue(
                href.startswith("https://www.thecruisedetective.com/"),
                f"Canonical in {slug} must start with 'https://www.thecruisedetective.com/', got '{href}'"
            )
            self.assertNotIn("deals.thecruisedetective.com", href)
            self.assertNotIn("vercel.app", href)
            self.assertFalse(href.endswith("/"), f"Canonical in {slug} must not have trailing slash: '{href}'")

if __name__ == "__main__":
    print("=== Running Milestone 2 Anchor & Heading Test Suite ===")
    unittest.main(verbosity=2)
