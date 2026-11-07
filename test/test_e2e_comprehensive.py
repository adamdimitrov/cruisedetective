#!/usr/bin/env python3
"""
The Cruise Detective Staging Architecture Overhaul — Comprehensive Python E2E Suite
Treats system boundaries as strict interface contracts defined in PROJECT.md.
Executes natively via python3 without requiring external npm/node dependencies.
"""

import os
import sys
import re
import json
import hmac
import hashlib
import time
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

APPROVED_LANGUAGES = ['en', 'ja', 'pl', 'ro', 'fr', 'nl']
DEAD_LANGUAGES = [
    "ar", "bg", "ca", "cs", "da", "de", "el", "es", "fa", "fi",
    "he", "hi", "hr", "hu", "it", "ko", "no", "pt", "ru", "sk",
    "sr", "sv", "th", "tr", "uk", "vi", "zh"
]

CORE_MONEY_HUBS = [
    'seine-river-cruises-paris',
    'dinner-cruises-paris',
    'canal-cruises-amsterdam',
    'thames-river-cruises-london',
    'bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison'
]

LOCKED_TIQETS_PARTNER_ID = 'thecruisedetective.com-176436'


class TestTier1FeatureCoverage(unittest.TestCase):
    """Tier 1: Core Feature Verification against interface contracts."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(BASE_DIR, 'vercel.json'), 'r', encoding='utf-8') as f:
            cls.vercel_config = json.load(f)
        with open(os.path.join(BASE_DIR, 'sitemap.xml'), 'r', encoding='utf-8') as f:
            cls.sitemap_tree = ET.parse(f)
        with open(os.path.join(BASE_DIR, 'ratings.json'), 'r', encoding='utf-8') as f:
            cls.ratings = json.load(f)

    # 1.1 Canonical Tag Strict Enforcement
    def test_1_1_1_canonical_tags_present(self):
        for hub in CORE_MONEY_HUBS:
            index_path = os.path.join(BASE_DIR, hub, 'index.html')
            self.assertTrue(os.path.exists(index_path), f"Hub {hub} missing index.html")
            with open(index_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            canonical_tag = soup.find('link', rel=lambda r: r and 'canonical' in r)
            self.assertIsNotNone(canonical_tag, f"Canonical tag missing in {hub}")

    def test_1_1_2_canonical_absolute_https_domain(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            canonical_url = soup.find('link', rel=lambda r: r and 'canonical' in r).get('href', '')
            parsed = urlparse(canonical_url)
            self.assertEqual(parsed.scheme, 'https', f"Canonical scheme not https in {hub}")
            self.assertEqual(parsed.netloc, 'www.thecruisedetective.com', f"Canonical domain invalid in {hub}")

    def test_1_1_3_canonical_has_zero_fragments(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            canonical_url = soup.find('link', rel=lambda r: r and 'canonical' in r).get('href', '')
            self.assertNotIn('#', canonical_url, f"Canonical URL in {hub} contains '#' fragment: {canonical_url}")

    def test_1_1_4_canonical_normalized_slug(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            canonical_url = soup.find('link', rel=lambda r: r and 'canonical' in r).get('href', '')
            self.assertEqual(canonical_url, f"https://www.thecruisedetective.com/{hub}")

    # 1.2 5 Core Money Hubs Normalization
    def test_1_2_1_all_5_hubs_stored_locally(self):
        for hub in CORE_MONEY_HUBS:
            p = os.path.join(BASE_DIR, hub, 'index.html')
            self.assertTrue(os.path.isfile(p), f"Missing physical file {p}")
            self.assertGreater(os.path.getsize(p), 10000, f"File {p} suspiciously small")

    def test_1_2_2_valid_html5_skeleton(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn('<!DOCTYPE html>', content, f"{hub} missing DOCTYPE")
            soup = BeautifulSoup(content, 'html.parser')
            self.assertIsNotNone(soup.html)
            self.assertIsNotNone(soup.head)
            self.assertIsNotNone(soup.body)

    def test_1_2_3_comparison_elements_present(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            has_comparison = bool(soup.find(id='comparison-matrix')) or bool(soup.find('table')) or bool(soup.find(class_=re.compile(r'matrix|comparison|table', re.I)))
            self.assertTrue(has_comparison, f"No comparison elements found in {hub}")

    def test_1_2_4_strict_heading_hierarchy_single_h1(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            h1s = soup.find_all('h1')
            self.assertEqual(len(h1s), 1, f"Expected exactly 1 <h1> in {hub}, got {len(h1s)}")

    def test_1_2_5_primary_cta_buttons(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            ctas = soup.find_all('a', href=re.compile(r'tiqets\.com|getyourguide\.com'))
            self.assertGreater(len(ctas), 0, f"No primary affiliate CTAs in {hub}")

    # 1.3 301 Redirect Rules in vercel.json
    def test_1_3_1_vercel_redirects_structure(self):
        redirects = self.vercel_config.get('redirects', [])
        self.assertGreaterEqual(len(redirects), 350)
        for r in redirects:
            self.assertEqual(r.get('permanent'), True)
            self.assertNotIn('#', r.get('destination', ''))

    def test_1_3_2_redirects_for_all_dead_languages(self):
        redirects = self.vercel_config.get('redirects', [])
        sources = [r['source'] for r in redirects]
        for dl in DEAD_LANGUAGES:
            matched = any(s.startswith(f"/{dl}/") or s == f"/{dl}" or f"({dl}|" in s or f"|{dl})" in s for s in sources)
            self.assertTrue(matched, f"Dead language {dl} missing from redirect rules")

    def test_1_3_3_destinations_have_zero_hash_or_dead_params(self):
        redirects = self.vercel_config.get('redirects', [])
        for r in redirects:
            dest = r['destination']
            self.assertNotIn('#', dest, f"Fragment in destination: {dest}")
            self.assertNotIn('cruisenbspwith', dest)

    def test_1_3_4_legacy_alias_rewrites(self):
        rewrites = self.vercel_config.get('rewrites', [])
        sources = [r['source'] for r in rewrites]
        self.assertIn('/dinner-cruise-paris', sources)
        self.assertIn('/amsterdam-canal-cruises', sources)
        self.assertIn('/amsterdam-comparison', sources)

    # 1.4 6 Approved Languages Retention
    def test_1_4_1_approved_languages_count(self):
        self.assertEqual(len(APPROVED_LANGUAGES), 6)

    def test_1_4_2_approved_languages_not_redirected(self):
        redirects = self.vercel_config.get('redirects', [])
        sources = [r['source'] for r in redirects]
        for app in ['ja', 'pl', 'ro', 'fr', 'nl']:
            self.assertNotIn(f"/{app}", sources, f"Approved language {app} redirect blocked")
            self.assertNotIn(f"/{app}/", sources, f"Approved language {app} redirect blocked")

    def test_1_4_3_sitemap_has_77_canonical_urls(self):
        root = self.sitemap_tree.getroot()
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locs = [el.text for el in root.findall('sm:url/sm:loc', ns)]
        self.assertEqual(len(locs), 77, f"Expected 77 URLs in sitemap, got {len(locs)}")

    def test_1_4_4_sitemap_hreflangs_conform(self):
        root = self.sitemap_tree.getroot()
        ns = {
            'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'xhtml': 'http://www.w3.org/1999/xhtml'
        }
        allowed_hreflangs = set(APPROVED_LANGUAGES) | {'x-default', 'en-us'}
        for url_node in root.findall('sm:url', ns):
            alts = url_node.findall('xhtml:link', ns)
            for alt in alts:
                lang = alt.get('hreflang')
                self.assertIn(lang, allowed_hreflangs, f"Invalid hreflang {lang} in sitemap")

    def test_1_4_5_zero_dead_languages_in_sitemap(self):
        root = self.sitemap_tree.getroot()
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        locs = [el.text for el in root.findall('sm:url/sm:loc', ns)]
        for loc in locs:
            path = urlparse(loc).path.strip('/')
            first = path.split('/')[0] if '/' in path else ''
            if first:
                self.assertNotIn(first, DEAD_LANGUAGES, f"Dead language in sitemap: {loc}")

    # 1.5 Tiqets Partner Enforcement
    def test_1_5_1_tiqets_links_use_locked_partner_id(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            tiqets_links = [a.get('href') for a in soup.find_all('a', href=True) if 'tiqets.com' in a.get('href', '')]
            self.assertGreater(len(tiqets_links), 0, f"No Tiqets links in {hub}")
            for link in tiqets_links:
                self.assertIn(f"partner={LOCKED_TIQETS_PARTNER_ID}", link, f"Link in {hub} missing partner: {link}")

    def test_1_5_2_ratings_json_locked_partner_id(self):
        tiqets_keys = [k for k in self.ratings.keys() if 'tiqets.com' in k and 'partner=' in k]
        for k in tiqets_keys:
            self.assertIn(f"partner={LOCKED_TIQETS_PARTNER_ID}", k)

    def test_1_5_3_tq_campaign_preserved(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            tiqets_links = [a.get('href') for a in soup.find_all('a', href=True) if 'tiqets.com' in a.get('href', '')]
            for link in tiqets_links:
                self.assertIn("tq_campaign=", link, f"Missing tq_campaign in {hub}: {link}")

    def test_1_5_4_affiliate_links_target_blank_rel_noopener(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            for a in soup.find_all('a', href=re.compile(r'tiqets\.com|getyourguide\.com')):
                self.assertEqual(a.get('target'), '_blank', f"Missing target=_blank in {hub}: {a}")
                rel = a.get('rel', [])
                if isinstance(rel, list):
                    rel = ' '.join(rel)
                self.assertIn('noopener', rel, f"Missing noopener in {hub}: {a}")


class TestTier2BoundaryAndCornerCases(unittest.TestCase):
    """Tier 2: Boundary conditions, encoding, and sanitization."""

    # 2.1 Headings: 0 Emojis, 0 literal NBSP, 0 &nbsp;
    def test_2_1_1_zero_unicode_emojis_in_headings(self):
        emoji_pattern = re.compile(
            r'[\U00010000-\U0010ffff\u2600-\u26ff\u2700-\u27bf\u2300-\u23ff\u2b50\u200d\ufe0f]'
        )
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                text = h.get_text()
                self.assertIsNone(emoji_pattern.search(text), f"Emoji in {hub} heading: {text}")

    def test_2_1_2_zero_literal_nbsp_in_headings(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                self.assertNotIn('\u00a0', h.get_text(), f"Literal NBSP in {hub} heading: {h}")

    def test_2_1_3_zero_raw_nbsp_entities_in_headings(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                self.assertNotIn('&nbsp;', str(h), f"Raw &nbsp; entity in {hub} heading: {h}")

    # 2.2 Anchor IDs: HTML5 Validity
    def test_2_2_1_zero_hex_encoded_emojis_in_ids(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            for el in soup.find_all(id=True):
                self.assertNotIn('%', el['id'], f"Hex-encoded char in {hub} id: {el['id']}")

    def test_2_2_2_zero_cruisenbspwith_in_ids(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            for el in soup.find_all(id=True):
                self.assertNotIn('cruisenbspwith', el['id'], f"cruisenbspwith in {hub} id: {el['id']}")
                self.assertNotIn('nbsp', el['id'].lower(), f"nbsp in {hub} id: {el['id']}")

    def test_2_2_3_html5_id_syntax(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            for el in soup.find_all(id=True):
                eid = el['id']
                self.assertTrue(len(eid) > 0, f"Empty id in {hub}")
                self.assertFalse(bool(re.search(r'\s', eid)), f"Whitespace in id in {hub}: {eid}")

    def test_2_2_4_in_page_anchors_have_matching_targets(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            existing_ids = {el['id'] for el in soup.find_all(id=True)}
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('#') and len(href) > 1:
                    target = href[1:]
                    self.assertIn(target, existing_ids, f"Broken internal anchor #{target} in {hub}")

    # 2.3 Canonical URLs: Strict Rejection of Dirty Patterns
    def test_2_3_1_canonical_rejects_query_parameters(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            canonical_url = soup.find('link', rel=lambda r: r and 'canonical' in r).get('href', '')
            parsed = urlparse(canonical_url)
            self.assertEqual(parsed.query, '', f"Query params in canonical in {hub}: {canonical_url}")

    def test_2_3_2_canonical_rejects_unauthorized_domains(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            canonical_url = soup.find('link', rel=lambda r: r and 'canonical' in r).get('href', '')
            self.assertTrue(canonical_url.startswith('https://www.thecruisedetective.com/'))


class TestTier3CrossFeatureIntegrations(unittest.TestCase):
    """Tier 3: Link Decoration & Webhook Extraction Simulation."""

    def test_3_1_link_decoration_with_tq_campaign_composition(self):
        def format_tq_campaign(existing_campaign, click_id_type, click_id_value):
            if not existing_campaign:
                return f"{click_id_type}-{click_id_value}"
            match = re.search(r'--(fbclid|gclid|wbraid|gbraid)-', existing_campaign)
            if match:
                base_tag = existing_campaign[:match.start()]
                return f"{base_tag}--{click_id_type}-{click_id_value}" if base_tag else f"{click_id_type}-{click_id_value}"
            if existing_campaign == click_id_value:
                return click_id_value
            return f"{existing_campaign}--{click_id_type}-{click_id_value}"

        gclid = "Cj0KCQ_cross_feat_123"
        result1 = format_tq_campaign("adv-tldr", "gclid", gclid)
        self.assertEqual(result1, f"adv-tldr--gclid-{gclid}")

        # Idempotent re-decoration does not duplicate
        result2 = format_tq_campaign(result1, "gclid", gclid)
        self.assertEqual(result2, f"adv-tldr--gclid-{gclid}")

    def test_3_2_webhook_click_id_extraction_rules(self):
        def extract_click_id(payload):
            if not payload or not isinstance(payload, dict):
                return None
            tq_campaign = payload.get('tq_campaign') or payload.get('campaign') or ''
            if isinstance(tq_campaign, str) and tq_campaign.strip():
                trimmed = tq_campaign.strip()
                match = re.search(r'(gclid|wbraid|gbraid)-([a-zA-Z0-9_-]+)', trimmed, re.I)
                if match and match.group(2):
                    extracted = re.split(r'--|[&?#]', match.group(2))[0].strip()
                    if extracted and not re.search(r'organic|direct|referral|social|banner', extracted, re.I):
                        return {'type': match.group(1).lower(), 'value': extracted}
                if re.match(r'^[a-zA-Z0-9_-]{20,}$', trimmed) and not re.search(r'organic|direct|referral', trimmed, re.I):
                    return {'type': 'gclid', 'value': trimmed}
            for t in ['gclid', 'wbraid', 'gbraid']:
                val = payload.get(t)
                if isinstance(val, str) and len(val.strip()) >= 15 and not re.search(r'organic|direct|referral', val, re.I):
                    return {'type': t, 'value': val.strip()}
            subid = payload.get('subid')
            if isinstance(subid, str):
                m = re.search(r'(gclid|wbraid|gbraid):([^|?&#]+)', subid, re.I)
                if m and m.group(2):
                    return {'type': m.group(1).lower(), 'value': m.group(2).strip()}
            return None

        # Composite tag
        res = extract_click_id({"tq_campaign": "adv-tldr--gclid-Cj0KCQ_test_composite_456"})
        self.assertEqual(res, {'type': 'gclid', 'value': 'Cj0KCQ_test_composite_456'})

        # Raw string
        res = extract_click_id({"tq_campaign": "Cj0KCQ_raw_long_gclid_1234567890"})
        self.assertEqual(res, {'type': 'gclid', 'value': 'Cj0KCQ_raw_long_gclid_1234567890'})

        # Subid fallback
        res = extract_click_id({"subid": "gclid:Cj0KCQ_subid_test_789"})
        self.assertEqual(res, {'type': 'gclid', 'value': 'Cj0KCQ_subid_test_789'})

        # Organic skipped
        res = extract_click_id({"tq_campaign": "organic-search"})
        self.assertIsNone(res)


class TestTier4RealWorldScenarios(unittest.TestCase):
    """Tier 4: Realistic Crawler & User Journey Simulations."""

    def test_4_1_crawler_sitemap_completeness(self):
        tree = ET.parse(os.path.join(BASE_DIR, 'sitemap.xml'))
        root = tree.getroot()
        ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [el.text for el in root.findall('sm:url/sm:loc', ns)]
        self.assertEqual(len(urls), len(set(urls)), "Duplicate URLs detected in sitemap.xml")
        for hub in CORE_MONEY_HUBS:
            self.assertIn(f"https://www.thecruisedetective.com/{hub}", urls)

    def test_4_2_local_script_inclusion_in_all_hubs(self):
        for hub in CORE_MONEY_HUBS:
            with open(os.path.join(BASE_DIR, hub, 'index.html'), 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertIn('/webflow-sync.js', content, f"{hub} missing local /webflow-sync.js")
            self.assertNotIn('cdn.jsdelivr.net/gh/adamdimitrov/cruisedetective@main/webflow-sync.js', content,
                             f"{hub} still coupled to production jsDelivr main!")


if __name__ == '__main__':
    unittest.main()
