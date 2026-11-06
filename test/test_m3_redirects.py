#!/usr/bin/env python3
"""
Test Suite for Milestone 3: 6-Language Architecture & 301 Redirect Pruning.

Validates:
1. vercel.json 301 redirect configuration (>= 351 exact 1-to-1 redirects for 27 dead languages,
   legacy slug mappings, wildcard fallback rules, permanence, and clean destinations).
2. sitemap.xml clean generation (strictly 77 active canonical URLs across 6 approved languages,
   0 dead languages, 0 # anchor fragments, and strictly approved hreflangs).
3. Routing simulation ensuring approved languages are preserved while dead languages redirect.
"""

import os
import sys
import json
import re
import unittest
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERCEL_JSON_PATH = os.path.join(PROJECT_ROOT, "vercel.json")
SITEMAP_PATH = os.path.join(PROJECT_ROOT, "sitemap.xml")

APPROVED_LANGUAGES = ["en", "ja", "pl", "ro", "fr", "nl"]
ALLOWED_HREFLANGS = {"en", "en-us", "ja", "pl", "ro", "fr", "nl", "x-default"}

DEAD_LANGUAGES = [
    "ar", "bg", "ca", "cs", "da", "de", "el", "es", "fa", "fi",
    "he", "hi", "hr", "hu", "it", "ko", "no", "pt", "ru", "sk",
    "sr", "sv", "th", "tr", "uk", "vi", "zh"
]

def simulate_vercel_route(test_path, vercel_config):
    """Simulate Vercel redirect and rewrite evaluation matching Vercel runtime specification."""
    redirects = vercel_config.get("redirects", [])
    for r in redirects:
        src = r.get("source", "")
        if src == test_path:
            return {
                "action": "redirect",
                "destination": r.get("destination"),
                "permanent": r.get("permanent") is True or r.get("statusCode") in [301, 308]
            }
        if ":" in src:
            regex_str = "^" + src
            # Convert :lang(a|b|c) to named group
            regex_str = re.sub(r":lang\(([^)]+)\)", r"(?P<lang>\1)", regex_str)
            regex_str = re.sub(r":lang", r"(?P<lang>[a-zA-Z0-9_-]+)", regex_str)
            regex_str = re.sub(r":slug\*", r"(?P<slug>.*)", regex_str)
            regex_str = re.sub(r":slug", r"(?P<slug>[^/]+)", regex_str)
            regex_str = re.sub(r":path\*", r"(?P<path>.*)", regex_str)
            regex_str += "$"
            match = re.match(regex_str, test_path)
            if match:
                dest = r.get("destination", "")
                for k, v in match.groupdict().items():
                    dest = dest.replace(f":{k}*", v or "").replace(f":{k}", v or "")
                return {
                    "action": "redirect",
                    "destination": dest,
                    "permanent": r.get("permanent") is True or r.get("statusCode") in [301, 308]
                }

    rewrites = vercel_config.get("rewrites", [])
    for rw in rewrites:
        if rw.get("source") == test_path:
            return {
                "action": "rewrite",
                "destination": rw.get("destination")
            }

    return {"action": "none"}

class TestM3Redirects(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        assert os.path.exists(VERCEL_JSON_PATH), f"vercel.json must exist at {VERCEL_JSON_PATH}"
        with open(VERCEL_JSON_PATH, "r", encoding="utf-8") as f:
            cls.vercel_config = json.load(f)

        assert os.path.exists(SITEMAP_PATH), f"sitemap.xml must exist at {SITEMAP_PATH}"
        cls.sitemap_tree = ET.parse(SITEMAP_PATH)
        cls.sitemap_root = cls.sitemap_tree.getroot()
        cls.ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9", "xhtml": "http://www.w3.org/1999/xhtml"}

    # --------------------------------------------------------------------------
    # 1. vercel.json Integrity & Structure
    # --------------------------------------------------------------------------
    def test_01_vercel_json_basic_structure(self):
        """vercel.json must contain cleanUrls, trailingSlash, functions, and rewrites."""
        self.assertEqual(self.vercel_config.get("version"), 2)
        self.assertTrue(self.vercel_config.get("cleanUrls"))
        self.assertFalse(self.vercel_config.get("trailingSlash"))
        self.assertIn("functions", self.vercel_config)
        self.assertIn("rewrites", self.vercel_config)
        self.assertIn("redirects", self.vercel_config)

    def test_02_redirects_count_and_permanence(self):
        """vercel.json must contain at least 351 redirects, all permanent."""
        redirects = self.vercel_config.get("redirects", [])
        self.assertGreaterEqual(len(redirects), 351, f"Expected >= 351 redirects, found {len(redirects)}")
        for r in redirects:
            is_permanent = r.get("permanent") is True or r.get("statusCode") in [301, 308]
            self.assertTrue(is_permanent, f"Redirect rule {r} must be permanent")
            self.assertNotIn("#", r.get("destination", ""), f"Redirect destination cannot have #: {r}")

    def test_03_sample_redirect_from_all_27_dead_languages(self):
        """Every single one of the 27 dead languages must have active redirects."""
        redirects = self.vercel_config.get("redirects", [])
        sources = [r["source"] for r in redirects]

        for lang in DEAD_LANGUAGES:
            # Check for direct language root or localized path
            has_lang_redirect = any(
                src == f"/{lang}" or src.startswith(f"/{lang}/") for src in sources
            )
            self.assertTrue(
                has_lang_redirect,
                f"Dead language '{lang}' must have at least one exact redirect source"
            )

    def test_04_specific_sample_dead_language_mappings(self):
        """Test specific high-priority dead language URLs redirect to canonical English destinations."""
        samples = [
            ("/de/besten-bootsfahrten-mit-abendessen-paris", "/dinner-cruises-paris"),
            ("/es/mejores-cruceros-canales-amsterdam", "/canal-cruises-amsterdam"),
            ("/it/migliori-crociere-cena-parigi", "/dinner-cruises-paris"),
            ("/ru/лучшие-круизы-с-ужином-париж", "/dinner-cruises-paris"),
            ("/zh/巴黎塞纳河晚餐游船", "/dinner-cruises-paris"),
            ("/de/themse-kreuzfahrten-london", "/thames-river-cruises-london"),
            ("/de/bateaux-mouches-gegen-bateaux-parisiens-dinner-kreuzfahrt-nebeneinander-vergleich",
             "/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison")
        ]
        for src, expected_dst in samples:
            route = simulate_vercel_route(src, self.vercel_config)
            self.assertEqual(route["action"], "redirect", f"Route {src} must redirect")
            self.assertEqual(route["destination"], expected_dst, f"Route {src} must redirect to {expected_dst}")
            self.assertTrue(route["permanent"])

    def test_05_legacy_slug_redirects(self):
        """Legacy singular/custom slugs must redirect to canonical plural slugs."""
        legacy = [
            ("/dinner-cruise-paris", "/dinner-cruises-paris"),
            ("/amsterdam-canal-cruises", "/canal-cruises-amsterdam")
        ]
        for src, dst in legacy:
            route = simulate_vercel_route(src, self.vercel_config)
            self.assertEqual(route["action"], "redirect")
            self.assertEqual(route["destination"], dst)
            self.assertTrue(route["permanent"])

    def test_06_wildcard_fallback_rules(self):
        """Arbitrary unmapped paths under dead languages must fall back to /."""
        test_paths = [
            "/de/a/b/c",
            "/es/random-page-999",
            "/it",
            "/it/",
            "/fa/unknown-article",
            "/he/something",
            "/ru/arbitrary-slug-test"
        ]
        for path in test_paths:
            route = simulate_vercel_route(path, self.vercel_config)
            self.assertEqual(route["action"], "redirect", f"Path {path} should redirect via fallback")
            self.assertEqual(route["destination"], "/", f"Path {path} should redirect to /")
            self.assertTrue(route["permanent"])

    def test_07_approved_languages_not_redirected_by_fallback(self):
        """Approved language paths must NOT be caught by dead language fallback rules."""
        for lang in ["ja", "pl", "ro", "fr", "nl"]:
            test_path = f"/{lang}/dinner-cruises-paris"
            route = simulate_vercel_route(test_path, self.vercel_config)
            self.assertNotEqual(
                route.get("destination"),
                "/",
                f"Approved language path {test_path} must NOT be redirected to root"
            )

    # --------------------------------------------------------------------------
    # 2. sitemap.xml Validation
    # --------------------------------------------------------------------------
    def test_08_sitemap_exact_url_count(self):
        """sitemap.xml must contain strictly 77 active canonical URLs."""
        urls = self.sitemap_root.findall("sm:url", self.ns)
        self.assertEqual(len(urls), 77, f"Expected exactly 77 URLs, found {len(urls)}")

    def test_09_sitemap_zero_anchor_pollution(self):
        """sitemap.xml <loc> and alternate links must contain 0 fragment hashes (#)."""
        urls = self.sitemap_root.findall("sm:url", self.ns)
        for u in urls:
            loc = u.find("sm:loc", self.ns).text.strip()
            self.assertNotIn("#", loc, f"Found fragment hash in sitemap <loc>: {loc}")
            for link in u.findall("xhtml:link", self.ns):
                href = link.attrib.get("href", "")
                self.assertNotIn("#", href, f"Found fragment hash in sitemap alternate link: {href}")

    def test_10_sitemap_zero_dead_languages(self):
        """sitemap.xml <loc> must contain 0 URLs belonging to the 27 dead languages."""
        urls = self.sitemap_root.findall("sm:url", self.ns)
        for u in urls:
            loc = u.find("sm:loc", self.ns).text.strip()
            for dead in DEAD_LANGUAGES:
                self.assertFalse(
                    re.search(rf"://www\.thecruisedetective\.com/{dead}(/|$)", loc),
                    f"Dead language '{dead}' found in sitemap <loc>: {loc}"
                )

    def test_11_sitemap_approved_hreflang_tags_only(self):
        """Alternate hreflang links must strictly belong to approved languages or x-default."""
        urls = self.sitemap_root.findall("sm:url", self.ns)
        alternate_count = 0
        for u in urls:
            for link in u.findall("xhtml:link", self.ns):
                hl = link.attrib.get("hreflang", "").lower()
                self.assertIn(
                    hl,
                    ALLOWED_HREFLANGS,
                    f"Forbidden hreflang '{hl}' found in sitemap alternate link"
                )
                alternate_count += 1
        self.assertGreater(alternate_count, 0, "sitemap.xml must have alternate hreflang links")

    def test_12_sitemap_covers_all_6_approved_languages(self):
        """sitemap.xml must contain representation across all 6 approved languages."""
        urls = self.sitemap_root.findall("sm:url", self.ns)
        all_locs = [u.find("sm:loc", self.ns).text.strip() for u in urls]

        for lang in APPROVED_LANGUAGES:
            if lang == "en":
                has_lang = any(
                    not re.search(r"://www\.thecruisedetective\.com/(ja|pl|ro|fr|nl)(/|$)", loc)
                    for loc in all_locs
                )
            else:
                has_lang = any(f"/{lang}" in loc for loc in all_locs)
            self.assertTrue(has_lang, f"Approved language '{lang}' must have URLs in sitemap.xml")

if __name__ == "__main__":
    unittest.main()
