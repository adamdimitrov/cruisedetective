#!/usr/bin/env python3
"""
MASTER ESTABLISHED EDITORIAL PAGE BUILDER FOR THE CRUISE DETECTIVE
Conforming 100% to the Luxury Travel Tester Architectural Standard.

Builds:
1. /dinner-cruises-paris/index.html
2. /seine-river-cruises-paris/index.html
3. /canal-cruises-amsterdam/index.html
4. /thames-river-cruises-london/index.html
5. /bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html
"""

import os
import re
import subprocess
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

def get_orig_soup(rel_path):
    cmd = ['git', 'show', f'e43390f:{rel_path}']
    raw = subprocess.check_output(cmd, cwd=BASE_DIR, text=True)
    return BeautifulSoup(raw, 'html.parser')

def get_current_soup(rel_path):
    path = os.path.join(BASE_DIR, rel_path)
    with open(path, 'r', encoding='utf-8') as f:
        return BeautifulSoup(f.read(), 'html.parser')

def build_head(title, desc, canonical, schema_json=None):
    schema_markup = f'<script type="application/ld+json">\n{schema_json}\n</script>' if schema_json else ''
    return f'''<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <meta content="{desc}" name="description"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link rel="canonical" href="{canonical}"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin=""/>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet"/>
  <link rel="stylesheet" href="/css/editorial-luxury.css"/>
  {schema_markup}
  <!-- Google Analytics & GTM -->
  <script async="" src="https://www.googletagmanager.com/gtag/js?id=G-RN34XFKPQ6"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'G-RN34XFKPQ6');
  </script>
</head>'''

def build_navbar():
    return '''<header class="ltt-navbar" role="banner">
  <div class="ltt-nav-inner">
    <a href="/" class="ltt-brand" aria-label="The Cruise Detective Homepage">
      <span class="ltt-brand-emblem">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle>
          <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon>
        </svg>
      </span>
      <span class="ltt-brand-text">THE CRUISE DETECTIVE</span>
    </a>
    <nav class="ltt-nav-links" aria-label="Primary Navigation">
      <div class="ltt-nav-dropdown" id="lttExploreDropdown">
        <button type="button" class="ltt-nav-link ltt-dropdown-btn" aria-expanded="false" aria-haspopup="true">
          <span>Explore Guides</span>
          <svg class="ltt-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        <div class="ltt-mega-menu" role="menu">
          <div class="ltt-mega-col">
            <div class="ltt-mega-head">PARIS CRUISES</div>
            <a href="/dinner-cruises-paris/" class="ltt-mega-item">
              <span class="ltt-mega-icon">🍷</span>
              <div>
                <strong>Paris Dinner Cruises</strong>
                <p>10 tested floating restaurants on the Seine</p>
              </div>
            </a>
            <a href="/seine-river-cruises-paris/" class="ltt-mega-item">
              <span class="ltt-mega-icon">🗼</span>
              <div>
                <strong>Paris Sightseeing Cruises</strong>
                <p>Bateaux Parisiens vs. Mouches &amp; Vedettes</p>
              </div>
            </a>
            <a href="/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/" class="ltt-mega-item">
              <span class="ltt-mega-icon">⚖️</span>
              <div>
                <strong>Mouches vs. Parisiens</strong>
                <p>Head-to-head dinner cruise showdown</p>
              </div>
            </a>
          </div>
          <div class="ltt-mega-col">
            <div class="ltt-mega-head">EUROPEAN WATERWAYS</div>
            <a href="/canal-cruises-amsterdam/" class="ltt-mega-item">
              <span class="ltt-mega-icon">🧀</span>
              <div>
                <strong>Amsterdam Canal Cruises</strong>
                <p>Lovers, open sloops &amp; wine &amp; cheese</p>
              </div>
            </a>
            <a href="/thames-river-cruises-london/" class="ltt-mega-item">
              <span class="ltt-mega-icon">🇬🇧</span>
              <div>
                <strong>London Thames Cruises</strong>
                <p>Westminster to Greenwich &amp; speedboats</p>
              </div>
            </a>
          </div>
        </div>
      </div>
      <a href="/about/" class="ltt-nav-link">Undercover Manifesto</a>
    </nav>
    <div class="ltt-nav-right">
      <a href="#ltt-cards-deck" class="ltt-cta-pill">Top Picks ↓</a>
      <button type="button" class="ltt-hamburger" id="lttNavToggle" aria-label="Toggle navigation menu" aria-expanded="false">
        <span class="ltt-hamburger-bar"></span>
      </button>
    </div>
  </div>
  <div class="ltt-mobile-drawer" id="lttMobileDrawer" aria-hidden="true">
    <div class="ltt-mobile-section">
      <div class="ltt-mobile-label">FEATURED GUIDES</div>
      <a href="/dinner-cruises-paris/" class="ltt-mobile-link ltt-highlight">
        <span>🍷 Paris Dinner Cruises (Top 10)</span>
        <span class="ltt-mobile-tag">Tested</span>
      </a>
      <a href="/seine-river-cruises-paris/" class="ltt-mobile-link">
        <span>🗼 Paris Sightseeing Cruises</span>
      </a>
      <a href="/canal-cruises-amsterdam/" class="ltt-mobile-link">
        <span>🧀 Amsterdam Canal Cruises</span>
      </a>
      <a href="/thames-river-cruises-london/" class="ltt-mobile-link">
        <span>🇬🇧 London Thames Cruises</span>
      </a>
      <a href="/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/" class="ltt-mobile-link">
        <span>⚖️ Mouches vs. Parisiens Showdown</span>
      </a>
    </div>
    <div class="ltt-mobile-section ltt-mobile-footer-links">
      <a href="/about/" class="ltt-mobile-link">About &amp; Testing Protocol</a>
    </div>
    <div class="ltt-mobile-cta-wrap">
      <a href="#ltt-cards-deck" class="ltt-mobile-cta">View Tested Ranking ↓</a>
    </div>
  </div>
</header>'''

def build_footer():
    return '''<footer class="main-footer" style="background: var(--slate-950); color: #fff; padding: 60px 20px 100px 20px; border-top: 1px solid var(--slate-800); text-align: center;">
  <div style="max-width: 860px; margin: 0 auto;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 10px; margin-bottom: 16px;">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#d97706" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
      <span style="font-family: var(--font-serif); font-weight: 700; font-size: 18px; letter-spacing: 0.05em; color: #fff;">THE CRUISE DETECTIVE</span>
    </div>
    <p style="color: var(--slate-400); font-size: 13.5px; line-height: 1.6; margin-bottom: 24px;">
      Independent European Cruise Field Intelligence. 100% Anonymous Bookings • Zero Sponsored Placements • Field-Verified Unit Economics &amp; Pricing.
    </p>
    <div style="display: flex; justify-content: center; gap: 24px; flex-wrap: wrap; margin-bottom: 28px; font-size: 13px;">
      <a href="/dinner-cruises-paris/" style="color: var(--slate-300); text-decoration: none;">Paris Dinner Cruises</a>
      <a href="/seine-river-cruises-paris/" style="color: var(--slate-300); text-decoration: none;">Paris Sightseeing</a>
      <a href="/canal-cruises-amsterdam/" style="color: var(--slate-300); text-decoration: none;">Amsterdam Canals</a>
      <a href="/thames-river-cruises-london/" style="color: var(--slate-300); text-decoration: none;">London Thames</a>
      <a href="/about/" style="color: var(--slate-300); text-decoration: none;">About Manifesto</a>
    </div>
    <p style="color: var(--slate-600); font-size: 12px; margin: 0;">
      © 2026 The Cruise Detective. All rights reserved. Outbound partner links may earn an affiliate commission at zero extra cost to you.
    </p>
  </div>
</footer>'''

def build_sticky_bar(pick_label, pick_desc, pick_price, pick_cta, pick_url):
    return f'''<aside class="hybrid-sticky-bar" id="sticky-bar" aria-label="Fast navigation &amp; top recommendation">
  <div class="hybrid-bar-inner">
    <button type="button" class="hybrid-toc-btn" id="hybridTocBtn" aria-label="Open Table of Contents">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="3" y1="12" x2="21" y2="12"></line>
        <line x1="3" y1="6" x2="21" y2="6"></line>
        <line x1="3" y1="18" x2="21" y2="18"></line>
      </svg>
      <span>Contents</span>
    </button>
    <div class="hybrid-active-info hybrid-pick-context">
      <span class="hybrid-active-badge hybrid-pick-badge">🏆 #1 TESTED PICK</span>
      <span class="hybrid-active-title hybrid-pick-title">{pick_label}</span>
      <span class="hybrid-active-price hybrid-pick-meta">{pick_desc} • <strong>{pick_price}</strong></span>
    </div>
    <div class="hybrid-cta-wrap">
      <a class="hybrid-cta-btn" href="{pick_url}" target="_blank" rel="noopener nofollow sponsored">
        {pick_cta}
      </a>
    </div>
  </div>
</aside>

<div class="hybrid-sheet-backdrop" id="hybridBackdrop">
  <div class="hybrid-sheet" id="hybridSheet">
    <div class="hybrid-sheet-header">
      <h3 class="hybrid-sheet-title">Jump to Tested Cruise Review</h3>
      <button type="button" class="hybrid-sheet-close" id="hybridCloseBtn" aria-label="Close Table of Contents">×</button>
    </div>
    <div class="hybrid-sheet-body" id="hybridSheetList"></div>
  </div>
</div>'''

PAGE_REVIEWS_DATA = {
    'dinner-cruises-paris': [
        # Boat 1: Bateaux Mouches
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.7', 'count': '+300', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-reviews-bm'},
                {'name': 'getyourguide', 'score': '4.5', 'count': '+3,470', 'url': 'https://www.getyourguide.com/paris-l16/paris-sightseeing-cruise-on-the-seine-with-4-course-dinner-t465480/?partner_id=YS414AJ&cmp=article-dinner-cruises-paris-h3-reviews-bateaux-mouches&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.4', 'count': '+4,590', 'url': 'https://www.viator.com/tours/Paris/Bateaux-Mouches-3-Hour-Seine-River-Cruise-Including-Dinner-and-Live-Music/d479-23561P3?pid=P00072830&mcid=42383&medium=link&campaign=article-dinner-cruises-paris-h3-reviews-bateaux-mouches'},
                {'name': 'tripadvisor', 'score': '4.4', 'count': '+1,550', 'url': 'https://tripadvisor.tp.st/zCpG1Y1H'}
            ]
        },
        # Boat 2: Bateaux Parisiens
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.6', 'count': '+310', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-reviews-bp'},
                {'name': 'getyourguide', 'score': '4.7', 'count': '+6,570', 'url': 'https://www.getyourguide.com/paris-l16/bateaux-parisiens-dinner-cruise-t51059/?partner_id=YS414AJ&cmp=article-dinner-cruises-paris-h3-reviews-bateaux-parisiens&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.4', 'count': '+6,630', 'url': 'https://www.viator.com/tours/Paris/Seine-River-Cruise-Bateaux-Parisiens-Sightseeing-Cruise-with-Dinner-and-Live-Music/d479-5836DINNERCRUISE?pid=P00072830&mcid=42383&medium=link&campaign=article-dinner-cruises-paris-h3-reviews-bateaux-parisiens'},
                {'name': 'tripadvisor', 'score': '4.4', 'count': '+2,830', 'url': 'https://tripadvisor.tp.st/nEUZLgkQ'}
            ]
        },
        # Boat 3: Paris City Vision (La Marina)
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.0', 'count': '+60', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-romantic-dinner-cruise-in-paris-p1023747/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-reviews-pcv'},
                {'name': 'getyourguide', 'score': '4.2', 'count': '+4,670', 'url': 'https://www.getyourguide.com/paris-l16/paris-3-course-dinner-cruise-on-the-river-seine-t53306/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-dinner-cruises-paris-h3-reviews-paris-city-vision&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.8', 'count': '+1,630', 'url': 'https://www.viator.com/tours/Paris/Marina-de-Paris-Seine-River-Cruise-with-3-Course-Meal/d479-2050DC?pid=P00072830&mcid=42383&medium=link&campaign=article-dinner-cruises-paris-h3-reviews-paris-city-vision'},
                {'name': 'tripadvisor', 'score': '3.7', 'count': '+310', 'url': 'https://tripadvisor.tp.st/zM4vsUOq'}
            ]
        },
        # Boat 4: Paris en Scène
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.1', 'count': '+220', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-en-scene-dinner-cruise-seine-p1052475/?partner=thecruisedetective.com-176436&tq_campaign=paris-din-rev-parenscene'},
                {'name': 'getyourguide', 'score': '4.2', 'count': '+9,530', 'url': 'https://www.getyourguide.com/paris-l16/paris-dinner-cruise-t179570/?partner_id=YS414AJ&cmp=article-dinner-cruises-paris-h3-reviews-paris-en-scene&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.7', 'count': '+2,970', 'url': 'https://www.viator.com/tours/Paris/Bistro-Style-Seine-River-Dinner-Cruise/d479-6557DINNERCRUISE?pid=P00072830&mcid=42383&medium=link&campaign=article-dinner-cruises-paris-h3-reviews-paris-en-scene'},
                {'name': 'tripadvisor', 'score': '3.7', 'count': '+750', 'url': 'https://tripadvisor.tp.st/70jsrckb'}
            ]
        },
        # Boat 5: Le Diamant Bleu
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.4', 'count': '+60', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-diamond-blue-gourmet-dinner-cruise-p1049009/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-reviews-dbl'},
                {'name': 'getyourguide', 'score': '4.5', 'count': '+2,280', 'url': 'https://www.getyourguide.com/paris-l16/paris-lounge-tapas-dinner-cruise-on-the-seine-river-t142833/?partner_id=YS414AJ&cmp=article-dinner-cruises-paris-h3-reviews-list-le-diamant-bleu&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.5', 'count': '+1,370', 'url': 'https://www.viator.com/tours/Paris/Gourmet-dinner-cruise-on-the-Seine-river-with-singer-and-DJ-Set/d479-45167P2?pid=P00072830&mcid=42383&medium=link&campaign=article-dinner-cruises-paris-h3-reviews-list-le-diamant-bleu'},
                {'name': 'tripadvisor', 'score': '4.7', 'count': '+1,060', 'url': 'https://tripadvisor.tp.st/jA8ACudO'}
            ]
        },
        # Boat 6: Théo Trattoria
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.3', 'count': '+270', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-trattoria-dinner-cruise-p1071588/?partner=thecruisedetective.com-176436&tq_campaign=din-cru-par-rev-tratt'},
                {'name': 'getyourguide', 'score': '4.3', 'count': '+1,940', 'url': 'https://www.getyourguide.com/paris-l16/paris-trattoria-on-seine-italian-dinner-cruise-t459219/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-dinner-cruises-paris-italian-dinner-le-diamant-bleu-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.2', 'count': '+1,000', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-italian-dinner-le-diamant-bleu-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Ftours%2FParis%2FTrattoria-on-Seine-Italian-dinner-cruise-in-Paris%2Fd479-45167P3&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '4.2', 'count': '+680', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-italian-dinner-le-diamant-bleu-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g196560-d25549723-Paris_Theo_Boat_Seine_River_Italian_Trattoria_Style_Dinner_Cruise-Boulogne_Billanc.html&campaign_id=149'}
            ]
        },
        # Boat 7: Capitaine Fracasse
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.2', 'count': '+2,170', 'url': 'https://www.getyourguide.com/paris-l16/paris-romantic-cruise-with-3-course-dinner-on-seine-river-t178769/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-dinner-cruises-paris-capitaine-fracasse-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.0', 'count': '+810', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-capitaine-fracasse-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Ftours%2FParis%2FParis-Seine-River-Cruise-with-3-Course-Dinner%2Fd479-6557FRACASSE&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '4.0', 'count': '+260', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-capitaine-fracasse-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g187147-d11477836-Paris_Capitaine_Fracasse_3_Course_Seine_River_Dinner_Cruise-Paris_Ile_de_France.html&campaign_id=149'}
            ]
        },
        # Boat 8: Maxim\'s de Paris
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.5', 'count': '+520', 'url': 'https://www.getyourguide.com/paris-l16/paris-seine-river-cruise-with-3-course-dinner-live-music-t420838/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-dinner-cruises-paris-maxim-de-paris-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.2', 'count': '+120', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-maxim-de-paris-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Ftours%2FParis%2FEiffel-Tower-Experience-and-Dinner-Cruise-with-Moulin-Rouge-Show-and-Champagne%2Fd479-2050P305&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '4.2', 'count': '+60', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-maxim-de-paris-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g187147-d17775540-Seine_River_Dinner_Cruise_Maxim_s_de_Paris_with_Champagne_and_Live_Music-Paris_Ile.html&campaign_id=149'}
            ]
        },
        # Boat 9: Ducasse Sur Seine
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.7', 'count': '+510', 'url': 'https://www.getyourguide.com/paris-l16/paris-ducasse-sur-seine-gourmet-dinner-cruise-t273821/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=din-paris-det-ducasse&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.0', 'count': '+160', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-ducasse-sur-seine-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Ftours%2FParis%2FDucasse-dinner-on-the-Seine-with-Alain-Ducasse-Chocolate-Bar%2Fd479-135588P1&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '4.0', 'count': '+150', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-ducasse-sur-seine-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g187147-d17330345-Paris_at_the_First_Lodges_Ducasse_sur_Seine_dinner_cruise-Paris_Ile_de_France.html&campaign_id=149'}
            ]
        },
        # Boat 10: Paris City Vision Early Sunset
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.4', 'count': '+1,940', 'url': 'https://www.getyourguide.com/paris-l16/paris-3-course-dinner-cruise-on-the-river-seine-t53306/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=din-paris-det-early&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.8', 'count': '+1,630', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-city-vision-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Fen-PH%2Ftours%2FParis%2FMarina-de-Paris-Seine-River-Cruise-with-3-Course-Meal%2Fd479-2050DC&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '3.8', 'count': '+190', 'url': 'https://tp.media/r?marker=404154.article-dinner-cruises-paris-city-vision-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g187147-d11446381-Paris_Seine_Gourmet_Dinner_Cruise_Champagne-Paris_Ile_de_France.html&campaign_id=149'}
            ]
        }
    ],
    'seine-river-cruises-paris': [
        # Boat 1: Bateaux Parisiens
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.3', 'count': '10,010+', 'url': 'https://www.tiqets.com/things-to-do-in-paris-c66746/tickets-for-sightseeing-cruise-on-the-seine-p973977?partner=thecruisedetective.com-176436&tq_campaign=seine-deck-bp'},
                {'name': 'getyourguide', 'score': '4.4', 'count': '67,060+', 'url': 'https://www.getyourguide.com/paris-l16/paris-bateaux-parisiens-seine-river-sightseeing-cruise-t51059/?partner_id=YS414AJ&cmp=seine-deck-bp&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.7', 'count': '2,190+', 'url': 'https://www.viator.com/tours/Paris/Bateaux-Parisiens-Seine-River-Sightseeing-Cruise/d479-5836P1?pid=P00072830&mcid=42383&medium=link&campaign=seine-deck-bp'},
                {'name': 'tripadvisor', 'score': '3.7', 'count': '960+', 'url': 'https://tripadvisor.tp.st/nEUZLgkQ'}
            ]
        },
        # Boat 2: Bateaux-Mouches
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.4', 'count': '10,120+', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-seine-river-cruise-by-bateaux-mouches-p982823/?partner=thecruisedetective.com-176436&tq_campaign=seine-deck-bm'},
                {'name': 'getyourguide', 'score': '4.5', 'count': '3,340+', 'url': 'https://www.getyourguide.com/paris-l16/paris-seine-river-cruise-by-bateaux-mouches-t178877/?partner_id=YS414AJ&cmp=seine-deck-bm&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.7', 'count': '800+', 'url': 'https://www.viator.com/tours/Paris/Bateaux-Mouches-Seine-River-Cruise/d479-22340P1?pid=P00072830&mcid=42383&medium=link&campaign=seine-deck-bm'},
                {'name': 'tripadvisor', 'score': '3.7', 'count': '580+', 'url': 'https://tripadvisor.tp.st/zCpG1Y1H'}
            ]
        },
        # Boat 3: Vedettes de Paris
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.3', 'count': '2,560+', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-aperitif-cruise-on-the-seine-p1003911/?partner=thecruisedetective.com-176436&tq_campaign=seine-deck-vdp'},
                {'name': 'getyourguide', 'score': '4.3', 'count': '20,000+', 'url': 'https://www.getyourguide.com/paris-l16/paris-vedettes-de-paris-seine-river-sightseeing-cruise-t16408/?partner_id=YS414AJ&cmp=seine-deck-vdp&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.9', 'count': '140+', 'url': 'https://www.viator.com/tours/Paris/Vedettes-de-Paris-Seine-River-Cruise/d479-5837P1?pid=P00072830&mcid=42383&medium=link&campaign=seine-deck-vdp'},
                {'name': 'tripadvisor', 'score': '3.9', 'count': '50+', 'url': 'https://tp.media/r?marker=404154.seine-deck-vdp'}
            ]
        },
        # Boat 4: Batobus Paris
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.4', 'count': '1,120+', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-batobus-riverboat-hop-on-hop-off-p976735/?partner=thecruisedetective.com-176436&tq_campaign=seine-deck-bato'},
                {'name': 'getyourguide', 'score': '4.3', 'count': '5,250+', 'url': 'https://www.getyourguide.com/paris-l16/batobus-hop-on-hop-off-boat-pass-t178871/?partner_id=YS414AJ&cmp=seine-deck-bato&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.0', 'count': '3,330+', 'url': 'https://www.viator.com/tours/Paris/Batobus-Hop-On-Hop-Off-Seine-River-Cruise/d479-5838P1?pid=P00072830&mcid=42383&medium=link&campaign=seine-deck-bato'},
                {'name': 'tripadvisor', 'score': '4.0', 'count': '1,680+', 'url': 'https://tp.media/r?marker=404154.seine-deck-bato'}
            ]
        },
        # Boat 5: Paris Canal
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.5', 'count': '340+', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-canal-saint-martin-cruise-from-musee-d-orsay-to-parc-de-la-villette-p977685/?partner=thecruisedetective.com-176436&tq_campaign=seine-deck-pcan'},
                {'name': 'getyourguide', 'score': '4.2', 'count': '2,140+', 'url': 'https://www.getyourguide.com/paris-l16/paris-canal-saint-martin-cruise-t178873/?partner_id=YS414AJ&cmp=seine-deck-pcan&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.5', 'count': '1,120+', 'url': 'https://www.viator.com/tours/Paris/Canal-Saint-Martin-Cruise/d479-5839P1?pid=P00072830&mcid=42383&medium=link&campaign=seine-deck-pcan'},
                {'name': 'tripadvisor', 'score': '3.5', 'count': '240+', 'url': 'https://tp.media/r?marker=404154.seine-deck-pcan'}
            ]
        }
    ],
    'canal-cruises-amsterdam': [
        # Boat 1: Lovers Canal Cruises
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.2', 'count': '3,374+', 'url': 'https://www.tiqets.com/en/things-to-do-in-amsterdam-c75061/tickets-for-1-hour-amsterdam-canal-cruise-p973666/?partner=thecruisedetective.com-176436&tq_campaign=amsterdam-deck-lovers'},
                {'name': 'getyourguide', 'score': '4.2', 'count': '14,830+', 'url': 'https://www.getyourguide.com/amsterdam-l36/amsterdam-1-hour-canal-cruise-t8271/?partner_id=YS414AJ&cmp=amsterdam-deck-lovers&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.6', 'count': '800+', 'url': 'https://www.viator.com/tours/Amsterdam/Amsterdam-Canal-Cruise-with-Lovers/d525-2484P1?pid=P00072830&mcid=42383&medium=link&campaign=amsterdam-deck-lovers'},
                {'name': 'tripadvisor', 'score': '3.2', 'count': '360+', 'url': 'https://tp.media/r?marker=404154.amsterdam-deck-lovers'}
            ]
        },
        # Boat 2: Captain Jack
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.7', 'count': '1,730+', 'url': 'https://www.getyourguide.com/amsterdam-l36/amsterdam-all-inclusive-canal-cruise-with-drinks-cheese-t394862/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=amsterdam-deck-captainjack&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.9', 'count': '15,640+', 'url': 'https://www.viator.com/tours/Amsterdam/Captain-Jack-Amsterdam-Canal-Cruise/d525-102553P1?pid=P00072830&mcid=42383&medium=link&campaign=amsterdam-deck-captainjack'},
                {'name': 'tripadvisor', 'score': '4.9', 'count': '13,450+', 'url': 'https://tp.media/r?marker=404154.amsterdam-deck-captainjack'}
            ]
        },
        # Boat 3: Flagship Amsterdam
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.6', 'count': '24,500+', 'url': 'https://www.getyourguide.com/amsterdam-l36/amsterdam-open-boat-canal-cruise-with-live-guide-t193132/?partner_id=YS414AJ&cmp=amsterdam-deck-flagship&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.9', 'count': '30,820+', 'url': 'https://www.viator.com/tours/Amsterdam/Flagship-Amsterdam-Open-Boat-Canal-Cruise/d525-108865P1?pid=P00072830&mcid=42383&medium=link&campaign=amsterdam-deck-flagship'},
                {'name': 'tripadvisor', 'score': '4.9', 'count': '27,190+', 'url': 'https://tp.media/r?marker=404154.amsterdam-deck-flagship'}
            ]
        },
        # Boat 4: Blue Boat Company
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.4', 'count': '18,880+', 'url': 'https://www.getyourguide.com/amsterdam-l36/amsterdam-city-canal-cruise-blue-boat-t8272/?partner_id=YS414AJ&cmp=amsterdam-deck-blueboat&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.0', 'count': '700+', 'url': 'https://www.viator.com/tours/Amsterdam/Blue-Boat-Amsterdam-Canal-Cruise/d525-2485P1?pid=P00072830&mcid=42383&medium=link&campaign=amsterdam-deck-blueboat'},
                {'name': 'tripadvisor', 'score': '3.9', 'count': '390+', 'url': 'https://tp.media/r?marker=404154.amsterdam-deck-blueboat'}
            ]
        },
        # Boat 5: Friendship Amsterdam
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.5', 'count': '3,380+', 'url': 'https://www.getyourguide.com/amsterdam-l36/amsterdam-luxury-boat-cruise-with-unlimited-drinks-t141525/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=amsterdam-deck-friendship&mkt_cmp=true'},
                {'name': 'viator', 'score': '5.0', 'count': '5,410+', 'url': 'https://www.viator.com/tours/Amsterdam/Friendship-Amsterdam-Luxury-Canal-Cruise/d525-12345P1?pid=P00072830&mcid=42383&medium=link&campaign=amsterdam-deck-friendship'},
                {'name': 'tripadvisor', 'score': '4.9', 'count': '5,370+', 'url': 'https://tp.media/r?marker=404154.amsterdam-deck-friendship'}
            ]
        }
    ],
    'thames-river-cruises-london': [
        # Boat 1: Thames River Sightseeing
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.4', 'count': '+410', 'url': 'https://www.tiqets.com/en/london-attractions-c67458/tickets-for-thames-cruise-westminster-to-greenwich-p975431/?partner=thecruisedetective.com-176436&tq_campaign=lond-reviews-thamesriv'},
                {'name': 'getyourguide', 'score': '4.5', 'count': '+21,210', 'url': 'https://www.getyourguide.com/london-l57/westminster-to-greenwich-sightseeing-cruise-t71379/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=eng-article-london-river-cruises-h3-reviews-thames-river-sightseeing&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.6', 'count': '+2,830', 'url': 'https://www.viator.com/en-GB/tours/London/Westminster-to-Greenwich-Sightseeing-Thames-Cruise/d737-37862P1?pid=P00072830&mcid=42383&medium=link&campaign=eng-article-london-river-cruises-h3-reviews-thames-river-sightseeing'},
                {'name': 'tripadvisor', 'score': '4.5', 'count': '+910', 'url': 'https://tp.media/r?marker=404154.eng-article-london-river-cruises-h3-reviews-thames-river-sightseeing&trs=204442&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d11483572-Westminster_to_Greenwich_Sightseeing_Thames_Cruise_in_London-London_England.html&campaign_id=149'}
            ]
        },
        # Boat 2: London Eye River Cruise
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.5', 'count': '+3,600', 'url': 'https://www.getyourguide.com/london-l57/coca-cola-london-eye-river-cruise-t193403/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=eng-article-best-london-river-cruises-london-eye-cruises-h3-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.7', 'count': '+1,360', 'url': 'https://www.viator.com/tours/London/London-Eye-River-Cruise/d737-2988P12?pid=P00072830&mcid=42383&medium=link&campaign=eng-article-london-river-cruises-h3-reviews-list-london-eye'},
                {'name': 'tripadvisor', 'score': '4.7', 'count': '+1,040', 'url': 'https://tp.media/r?marker=404154.eng-article-london-river-cruises-h3-reviews-list-london-eye&trs=204442&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d15750710-London_Eye_River_Cruise-London_England.html&campaign_id=149'}
            ]
        },
        # Boat 3: City Cruises Hop-On Hop-Off
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.4', 'count': '+3,000', 'url': 'https://www.getyourguide.com/london-l57/the-famous-city-cruises-hop-on-hop-off-sightseeing-cruise-t5273/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=eng-article-london-river-cruises-h3-reviews-city-cruises-sightseeing-cruise&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.1', 'count': '+1,240', 'url': 'https://www.viator.com/tours/London/Thames-Hop-On-Hop-Off-River-Cruise/d737-3542RRR?pid=P00072830&mcid=42383&medium=link&campaign=eng-article-london-river-cruises-h3-reviews-city-cruises-sightseeing-cruise'},
                {'name': 'tripadvisor', 'score': '4.1', 'count': '+660', 'url': 'https://tp.media/r?marker=404154.eng-article-london-river-cruises-h3-reviews-city-cruises-sightseeing-cruise&trs=204442&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d11449151-Thames_24_Hour_Hop_On_Hop_Off_River_Cruise-London_England.html&campaign_id=149'}
            ]
        },
        # Boat 4: Thames Rockets
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.9', 'count': '+770', 'url': 'https://www.getyourguide.com/london-l57/thames-boat-trip-waterway-london-adventure-t16670/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=eng-article-best-london-river-cruises-thames-rockets-h3-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '5.0', 'count': '+3,900', 'url': 'https://www.viator.com/tours/London/High-Speed-Thames-River-RIB-Cruise-in-London/d737-6918ULA?pid=P00072830&mcid=42383&medium=link&campaign=eng-article-best-london-river-cruises-thames-rockets-h3-reviews'},
                {'name': 'tripadvisor', 'score': '5.0', 'count': '+3,300', 'url': 'https://tp.media/r?marker=404154.eng-article-best-london-river-cruises-thames-rockets-h3-reviews&trs=204442&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d11454893-High_Speed_Thames_River_Speedboat_in_London-London_England.html&campaign_id=149'}
            ]
        },
        # Boat 5: Thames RIB Experience
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.8', 'count': '+300', 'url': 'https://www.getyourguide.com/london-l57/london-75-minute-thames-barrier-speedboat-rib-experience-t207834/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=eng-article-london-river-cruises-h3-reviews-thames-ribs-speedboat&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.9', 'count': '+770', 'url': 'https://tp.media/r?marker=404154.eng-article-london-river-cruises-h3-reviews-thames-ribs-speedboat&trs=204442&p=1922&u=https%3A%2F%2Fwww.viator.com%2Ftours%2FLondon%2FRiver-Thames-High-Speed-Cruise%2Fd737-5182SPEED&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '4.9', 'count': '+520', 'url': 'https://tp.media/r?marker=404154.eng-article-london-river-cruises-h3-reviews-thames-ribs-speedboat&trs=204442&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d11450740-Speedboat_Thames_Barrier_Experience_to_from_Embankment_Pier_70_minutes-London_Engl.html&campaign_id=149'}
            ]
        },
        # Boat 6: Thames River Lunch Cruise
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.5', 'count': '+1,910', 'url': 'https://www.getyourguide.com/london-l57/lunch-cruise-on-the-thames-t26664/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=eng-article-best-london-river-cruises-city-cruises-lunch-cruise-h3-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.5', 'count': '+960', 'url': 'https://www.viator.com/tours/London/Thames-Lunch-Cruise-with-2-Course-Meal/d737-3542LUNCHCRU?pid=P00072830&mcid=42383&medium=link&campaign=eng-article-best-london-river-cruises-city-cruises-lunch-cruise-h3-reviews'},
                {'name': 'tripadvisor', 'score': '4.4', 'count': '+330', 'url': 'https://tripadvisor.tp.st/nYFrD6vQ'}
            ]
        },
        # Boat 7: Thames River Sunset Cruise with Bubbly
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.4', 'count': '+2,380', 'url': 'https://www.getyourguide.com/london-l57/cruise-the-thames-with-a-glass-of-bubbly-canapes-t29923/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-river-cruises-london-city-cruises-bubbly-canapes-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.9', 'count': '+550', 'url': 'https://tp.media/r?marker=404154.article-river-cruises-london-city-cruises-bubbly-canapes-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Fen-PH%2Ftours%2FLondon%2FRiver-Thames-Sunset-Sightseeing-Cruise%2Fd737-3542EVENING&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '3.8', 'count': '+140', 'url': 'https://tp.media/r?marker=404154.article-river-cruises-london-city-cruises-bubbly-canapes-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d11449147-River_Thames_Evening_Cruise_with_Sparkling_wine_and_Canapes-London_England.html&campaign_id=149'}
            ]
        },
        # Boat 8: Thames Jazz Dinner Cruise
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.1', 'count': '+220', 'url': 'https://www.getyourguide.com/london-l57/thames-jazz-dinner-cruise-t37172/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-river-cruises-london-city-cruises-jazz-cruise-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '3.9', 'count': '+140', 'url': 'https://tp.media/r?marker=404154.article-river-cruises-london-city-cruises-jazz-cruise-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Fen-PH%2Ftours%2FLondon%2FThames-Jazz-Dinner-Cruise%2Fd737-3542P19&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '3.9', 'count': '+60', 'url': 'https://tp.media/r?marker=404154.article-river-cruises-london-city-cruises-jazz-cruise-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d11468827-Dinner_and_Jazz_Cruise_on_the_River_Thames-London_England.html&campaign_id=149'}
            ]
        },
        # Boat 9: Thames Hop-On Hop-Off Uber Boat
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.0', 'count': '+230', 'url': 'https://www.getyourguide.com/london-l57/london-uber-boat-by-thames-clippers-hop-on-hop-off-day-pass-t67981/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-river-cruises-london-thames-clippers-uberboat-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.0', 'count': '+680', 'url': 'https://tp.media/r?marker=404154.article-river-cruises-london-thames-clippers-uberboat-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Fen-PH%2Ftours%2FLondon%2FThames-Clippers-River-Roamer-Hop-On-Hop-Off-Pass%2Fd737-5021CLIPPER&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '4.0', 'count': '+590', 'url': 'https://tp.media/r?marker=404154.article-river-cruises-london-thames-clippers-uberboat-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d12078321-London_Uber_Boat_Hop_On_Hop_Off_1_Day_River_Thames_Pass-London_England.html&campaign_id=149'}
            ]
        },
        # Boat 10: Thames Evening Dinner Cruise
        {
            'channels': [
                {'name': 'getyourguide', 'score': '4.3', 'count': '+1,950', 'url': 'https://www.getyourguide.com/london-l57/the-london-showboat-dinner-dance-cruise-t5275/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=article-river-cruises-london-thames-city-cruises-dinner-cruise-reviews&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.2', 'count': '+1,690', 'url': 'https://tp.media/r?marker=404154.article-river-cruises-london-thames-city-cruises-dinner-cruise-reviews&trs=327188&p=1922&u=https%3A%2F%2Fwww.viator.com%2Fen-PH%2Ftours%2FLondon%2FThe-London-Showboat-Dinner-Cruise-on-the-Thames-River%2Fd737-3542SB&campaign_id=47'},
                {'name': 'tripadvisor', 'score': '4.2', 'count': '+350', 'url': 'https://tp.media/r?marker=404154.article-river-cruises-london-thames-city-cruises-dinner-cruise-reviews&trs=327188&p=4456&u=https%3A%2F%2Fwww.tripadvisor.com%2FAttractionProductReview-g186338-d11449152-London_Dinner_Cruise_on_the_Thames_River-London_England.html&campaign_id=149'}
            ]
        }
    ],
    'bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison': [
        # Boat 1: Bateaux Mouches
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.7', 'count': '+300', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=vs-deck-bm'},
                {'name': 'getyourguide', 'score': '4.5', 'count': '+3,470', 'url': 'https://www.getyourguide.com/paris-l16/paris-sightseeing-cruise-on-the-seine-with-4-course-dinner-t465480/?partner_id=YS414AJ&cmp=vs-deck-bm&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.4', 'count': '+4,590', 'url': 'https://www.viator.com/tours/Paris/Bateaux-Mouches-3-Hour-Seine-River-Cruise-Including-Dinner-and-Live-Music/d479-23561P3?pid=P00072830&mcid=42383&medium=link&campaign=vs-deck-bm'},
                {'name': 'tripadvisor', 'score': '4.4', 'count': '+1,550', 'url': 'https://tripadvisor.tp.st/zCpG1Y1H'}
            ]
        },
        # Boat 2: Bateaux Parisiens
        {
            'channels': [
                {'name': 'tiqets', 'score': '4.6', 'count': '+310', 'url': 'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&tq_campaign=vs-deck-bp'},
                {'name': 'getyourguide', 'score': '4.7', 'count': '+6,570', 'url': 'https://www.getyourguide.com/paris-l16/bateaux-parisiens-dinner-cruise-t51059/?partner_id=YS414AJ&cmp=vs-deck-bp&mkt_cmp=true'},
                {'name': 'viator', 'score': '4.4', 'count': '+6,630', 'url': 'https://www.viator.com/tours/Paris/Seine-River-Cruise-Bateaux-Parisiens-Sightseeing-Cruise-with-Dinner-and-Live-Music/d479-5836DINNERCRUISE?pid=P00072830&mcid=42383&medium=link&campaign=vs-deck-bp'},
                {'name': 'tripadvisor', 'score': '4.4', 'count': '+2,830', 'url': 'https://tripadvisor.tp.st/nEUZLgkQ'}
            ]
        }
    ]
}

def apply_reviews_and_proof(soup, page_slug):
    page_data = PAGE_REVIEWS_DATA.get(page_slug, [])

    # 1. Update Comparison Deck Cards
    cards = soup.find_all(class_='bpa-card')
    for i, card in enumerate(cards):
        # Update bpa-proof: eliminate generic reviews line, leave strictly verified badge
        proof = card.find(class_='bpa-proof')
        if proof:
            proof.clear()
            v_span = soup.new_tag('span', **{'class': 'bpa-verified'})
            v_span.string = '✓ Personally Field-Tested'
            proof.append(v_span)

        # Update bpa-channels: populate authentic OTA review badges with NO brand names
        if i < len(page_data):
            ch_container = card.find(class_='bpa-channels')
            if ch_container:
                ch_container.clear()
                for ch in page_data[i]['channels']:
                    a_tag = soup.new_tag('a', **{
                        'class': 'bpa-ci',
                        'href': ch['url'],
                        'target': '_blank',
                        'rel': 'noopener nofollow sponsored',
                        'title': f"Check reviews on {ch['name'].capitalize()}"
                    })
                    img_tag = soup.new_tag('img', **{
                        'class': 'bpa-rev-icon',
                        'src': f"/assets/icons/{ch['name']}.png",
                        'alt': '',
                        'width': '16',
                        'height': '16',
                        'loading': 'lazy'
                    })
                    strong_tag = soup.new_tag('strong')
                    strong_tag.string = ch['score']
                    cnt_span = soup.new_tag('span', **{'class': 'bpa-rev-count'})
                    cnt_span.string = f"({ch['count']})"

                    a_tag.append(img_tag)
                    a_tag.append(strong_tag)
                    a_tag.append(cnt_span)
                    ch_container.append(a_tag)

    # 2. Update Detailed Reviews Accordions
    details = soup.find_all('details', class_='bpa-details-card')
    for i, det in enumerate(details):
        if i < len(page_data):
            sr = det.find(class_='bpa-summary-reviews')
            if sr:
                sr.clear()
                for ch in page_data[i]['channels']:
                    a_tag = soup.new_tag('a', **{
                        'class': 'bpa-rev-badge',
                        'href': ch['url'],
                        'target': '_blank',
                        'rel': 'noopener nofollow sponsored',
                        'onclick': 'event.stopPropagation()',
                        'title': f"Check reviews on {ch['name'].capitalize()}"
                    })
                    img_tag = soup.new_tag('img', **{
                        'class': 'bpa-rev-icon',
                        'src': f"/assets/icons/{ch['name']}.png",
                        'alt': '',
                        'width': '16',
                        'height': '16',
                        'loading': 'lazy'
                    })
                    score_span = soup.new_tag('span', **{'class': 'bpa-rev-score'})
                    score_span.string = ch['score']
                    cnt_span = soup.new_tag('span', **{'class': 'bpa-rev-count'})
                    cnt_span.string = f"({ch['count']})"

                    a_tag.append(img_tag)
                    a_tag.append(score_span)
                    a_tag.append(cnt_span)
                    sr.append(a_tag)

def build_page_skeleton(head_html, hero_img_url, hero_img_alt, breadcrumb_text, h1_title, date_text, intro_content_html, comparison_table_html, right_content_html, sticky_bar_html, page_slug=None):
    hero_img_markup = f'''<div class="hero-image-wrapper">
  <img class="hero-image" src="{hero_img_url}" alt="{hero_img_alt}" loading="eager"/>
</div>''' if hero_img_url else ''

    raw_html = f'''<!DOCTYPE html>
<html lang="en">
{head_html}
<body>
{build_navbar()}

{hero_img_markup}

<div class="article-hero-container w-container">
  <div class="component-breadcrumb-rich-text w-richtext">
    <p><a href="/">Home</a> » {breadcrumb_text}</p>
  </div>
  <h1 class="component-heading-2">{h1_title}</h1>
  <p class="paragraph-26"><strong>Last updated:</strong> {date_text}</p>
  <div class="div-block-45">
    <img alt="Adam Dimitrov" class="component-author-image" src="https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp"/>
    <div class="rich-text-block-35 w-richtext">
      <p><strong>Author:</strong> <a href="/about/">Adam Dimitrov</a> — Chief Cruise Detective • Personally Field-Tested</p>
    </div>
  </div>
  <div class="divider-2"></div>
</div>

<div class="container-intro-section w-container">
  <div class="rich-text-block-36 w-richtext">
    {intro_content_html}
  </div>
</div>

<div class="comparison-table">
  <div class="container-27">
    {comparison_table_html}
  </div>
</div>

<div class="blog-section-2">
  <div class="container-31">
    <div class="blog-grid-2">
      <div class="content-left">
        <div class="stick-wrapper">
          <div class="title-small-6" style="font-size:12px; font-weight:800; text-transform:uppercase; letter-spacing:0.06em; color:var(--slate-900); margin-bottom:12px;">Table of Contents</div>
          <div class="toc" id="toc"></div>
        </div>
      </div>
      <div class="content-right_blog" id="content">
        {right_content_html}
      </div>
    </div>
  </div>
</div>

{build_footer()}

{sticky_bar_html}

<script src="/webflow-sync.js" defer=""></script>
<script src="/js/ltt-nav.js" defer=""></script>
</body>
</html>'''

    soup = BeautifulSoup(raw_html, 'html.parser')
    if page_slug:
        apply_reviews_and_proof(soup, page_slug)
    return str(soup)

# ==============================================================================
# 1. BUILD DINNER CRUISES PARIS
# ==============================================================================
def build_dinner_cruises_paris():
    print("Building /dinner-cruises-paris/index.html ...")
    cur_soup = get_current_soup('dinner-cruises-paris/index.html')
    
    # 1. Comparison Table
    deck_box = cur_soup.find(class_='ltt-header-box')
    deck_grid = cur_soup.find(id='ltt-cards-deck')
    comp_html = f'{str(deck_box)}\n{str(deck_grid)}'

    # 2. Intro Content
    intro_html = '''<p>Over 2.5 million travelers book a Seine cruise every year, but dinner cruises carry the highest variance in Paris travel. Prices range from €65 bistro cruises to €300+ haute gastronomy electric superyachts. With 10 major operators all promising "panoramic views and gourmet dining," picking the wrong one means lukewarm microwaved food, obstructed views next to the galley, or loud coach tour crowds.</p>
<p>We booked, paid out-of-pocket, and personally tested all 10 dinner cruise operators in Paris. We measured course pacing, tested table view angles, tasted every menu option, and mapped exact boarding pier logistics.</p>
<blockquote>💡 <strong>Tested Sommelier &amp; Captain Tip:</strong> For proposals, romantic milestones, and prime sunset lighting, book the <strong>20:00 or 20:30 departures</strong>. Cruises pace their navigation loop to float directly in front of the illuminated Eiffel Tower during its mesmerizing 5-minute diamond sparkle display at the top of the hour.</blockquote>'''

    # 3. Right Content
    intro_section = cur_soup.find(id='editorial-intro')
    intro_block_inner = ''
    if intro_section:
        intro_container = intro_section.find(class_='ltt-container')
        intro_block_inner = ''.join(str(c) for c in intro_container.children if c.name) if intro_container else str(intro_section)

    bd_header = cur_soup.find(id='breakdown-header')
    bd_header_html = str(bd_header) if bd_header else ''

    details_cards = cur_soup.find_all('details', class_='bpa-details-card')
    details_html = '\n'.join(str(c) for c in details_cards)

    buying_guide = cur_soup.find(id='buying-guide')
    buying_guide_inner = ''
    if buying_guide:
        bg_container = buying_guide.find(class_='ltt-container')
        buying_guide_inner = ''.join(str(c) for c in bg_container.children if c.name) if bg_container else str(buying_guide)

    right_content = f'''<div class="w-richtext ltt-editorial-body" style="margin-bottom: 40px;">
  {intro_block_inner}
</div>
{bd_header_html}
<div id="in-depth-reviews">
  {details_html}
</div>
<div class="ltt-post-guide" id="buying-guide">
  {buying_guide_inner}
</div>'''

    sticky = build_sticky_bar(
        'Bateaux Mouches 20:30 Prestige',
        'Pont de l\'Alma Pier • 4-Course French Cuisine',
        'From €130',
        'Book Bateaux Mouches (€130) →',
        'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-on-the-seine-p982924/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-mouches'
    )

    head = build_head(
        '10 Best Seine River Dinner Cruises in Paris (2026 Ranked & Tested) | The Cruise Detective',
        'We tested all 10 Paris Seine dinner cruises undercover. Compare menus, live music, seat views, and prices from Bateaux Mouches to Bateaux Parisiens.',
        'https://www.thecruisedetective.com/dinner-cruises-paris'
    )

    page_html = build_page_skeleton(
        head_html=head,
        hero_img_url='https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/65562265e60663a885093897_paris-dinner-cruises-featured-image.webp',
        hero_img_alt='Paris Seine River Dinner Cruise with illuminated Eiffel Tower',
        breadcrumb_text='10 Best Seine River Dinner Cruises in Paris (2026 Ranked & Tested)',
        h1_title='10 Best Seine River Dinner Cruises in Paris (2026 Ranked & Tested)',
        date_text='March 2026 • Personally Field-Tested Undercover',
        intro_content_html=intro_html,
        comparison_table_html=comp_html,
        right_content_html=right_content,
        sticky_bar_html=sticky,
        page_slug='dinner-cruises-paris'
    )

    out_path = os.path.join(BASE_DIR, 'dinner-cruises-paris/index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"Saved {out_path} ({len(page_html)} bytes)")

# ==============================================================================
# 2. BUILD SEINE RIVER CRUISES PARIS
# ==============================================================================
def build_seine_river_cruises_paris():
    print("Building /seine-river-cruises-paris/index.html ...")
    orig_soup = get_orig_soup('seine-river-cruises-paris/index.html')
    cur_soup = get_current_soup('seine-river-cruises-paris/index.html')

    # 1. Comparison Table
    deck_box = cur_soup.find(class_='ltt-header-box')
    deck_grid = cur_soup.find(id='ltt-cards-deck')
    comp_html = f'{str(deck_box)}\n{str(deck_grid)}'

    # 2. Intro Content (from authentic warning callout + tldr winner box)
    warn_el = orig_soup.find(class_='warning-callout')
    tldr_el = orig_soup.find(class_='tldr-winner-box')
    intro_html = f'''<div class="warning-callout" style="background: #fffbeb; border-left: 4px solid var(--gold-primary); padding: 20px 24px; border-radius: 0 12px 12px 0; margin-bottom: 24px;">
  {str(warn_el.find('h3')) if warn_el and warn_el.find('h3') else '<h3>Is a Seine Sightseeing Cruise Worth It—And What Are the Hidden Traps?</h3>'}
  {str(warn_el.find('p')) if warn_el and warn_el.find('p') else ''}
</div>
<div class="tldr-winner-box" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #fff; padding: 24px 28px; border-radius: 16px; margin-bottom: 24px;">
  <span style="display: inline-block; background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 999px; margin-bottom: 8px;">👑 THE QUICK ANSWER</span>
  <h3 style="color: #fff; font-family: var(--font-serif); font-size: 22px; margin: 0 0 10px 0;">Our #1 Overall Recommendation: Bateaux Parisiens</h3>
  <p style="color: #cbd5e1; font-size: 14.5px; line-height: 1.6; margin: 0;">If you want the most reliable, best-equipped 1-hour sightseeing cruise right beneath the Eiffel Tower: <strong>Bateaux Parisiens</strong> is our #1 tested choice. Departing every 30 minutes from Pier 3 directly under the Eiffel Tower, featuring crystal-clear individual audio handsets in 14 languages, a 360° open upper deck, and instant mobile barcode entry with open dates.</p>
</div>'''

    # 3. Right Content: Breakdown top bar + 5 details cards + Post-review buying guide
    bd_top_bar = '''<div class="bpa-breakdown-top-bar" id="breakdown-header">
  <div style="flex: 1; min-width: 260px;">
    <h2 class="bpa-breakdown-heading">Detailed Breakdown — 5 Best Seine River Cruises in Paris</h2>
    <p class="bpa-breakdown-sub">Personally field-tested • All reviews open by default • Click to collapse/expand</p>
  </div>
  <div class="bpa-acc-controls">
    <button type="button" class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)">Expand All</button>
    <button type="button" class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)">Collapse All</button>
  </div>
</div>'''

    details_cards = cur_soup.find_all('details', class_='bpa-details-card')
    details_html = '\n'.join(str(c) for c in details_cards)

    # Post-review sections from orig_soup
    timeline = orig_soup.find(id='route-timeline')
    timeline_html = str(timeline) if timeline else ''
    
    audio_deck = orig_soup.find(id='audio-deck-section')
    audio_deck_html = str(audio_deck) if audio_deck else ''

    faq = orig_soup.find(id='faq-section')
    faq_html = str(faq) if faq else ''

    verdict = orig_soup.find(class_='final-verdict-box')
    verdict_html = str(verdict) if verdict else ''

    right_content = f'''{bd_top_bar}
<div id="in-depth-reviews">
  {details_html}
</div>
<div class="ltt-post-guide" id="buying-guide">
  {timeline_html}
  {audio_deck_html}
  {faq_html}
  {verdict_html}
</div>'''

    sticky = build_sticky_bar(
        'Bateaux Parisiens Sightseeing',
        'Pier 3 Eiffel Tower • 70m Audio Cruise',
        '€18 Adult • €9 Child',
        'Book Bateaux Parisiens (€18) →',
        'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-bateaux-parisiens-seine-river-cruise-p973977/?partner=thecruisedetective.com-176436&tq_campaign=sight-paris-det-bp'
    )

    head = build_head(
        'The 5 Best Paris Seine River Cruises (2026 Ranked & Tested) | The Cruise Detective',
        'Compare the 5 best Paris sightseeing boat tours on the Seine. Tested in person: Bateaux Parisiens vs Bateaux-Mouches vs Vedettes de Paris vs Batobus.',
        'https://www.thecruisedetective.com/seine-river-cruises-paris'
    )

    page_html = build_page_skeleton(
        head_html=head,
        hero_img_url='https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/699480970fd56c513a2749e0_bateaux-parisiens-sighteeing-cruise-00002.avif',
        hero_img_alt='Paris Seine Sightseeing Cruise passing Pont Alexandre III and Eiffel Tower',
        breadcrumb_text='5 Best Paris Seine River Cruises (2026 Ranked & Tested)',
        h1_title='The 5 Best Paris Seine River Cruises (2026 Ranked & Tested)',
        date_text='March 2026 • Personally Field-Tested Undercover',
        intro_content_html=intro_html,
        comparison_table_html=comp_html,
        right_content_html=right_content,
        sticky_bar_html=sticky,
        page_slug='seine-river-cruises-paris'
    )

    out_path = os.path.join(BASE_DIR, 'seine-river-cruises-paris/index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"Saved {out_path} ({len(page_html)} bytes)")

# ==============================================================================
# 3. BUILD AMSTERDAM CANAL CRUISES
# ==============================================================================
def build_canal_cruises_amsterdam():
    print("Building /canal-cruises-amsterdam/index.html ...")
    orig_soup = get_orig_soup('canal-cruises-amsterdam/index.html')
    cur_soup = get_current_soup('canal-cruises-amsterdam/index.html')

    deck_box = cur_soup.find(class_='ltt-header-box')
    deck_grid = cur_soup.find(id='ltt-cards-deck')
    comp_html = f'{str(deck_box)}\n{str(deck_grid)}'

    # Authenticate intro content from e43390f
    intro_html = '''<div class="warning-callout" style="background: #fffbeb; border-left: 4px solid var(--gold-primary); padding: 20px 24px; border-radius: 0 12px 12px 0; margin-bottom: 24px;">
  <h3 style="font-family: var(--font-serif); font-size: 20px; color: var(--slate-900); margin: 0 0 8px 0;">Is an Amsterdam Canal Cruise Worth It—And What Are the 4 Costly Rookie Traps?</h3>
  <p style="color: var(--slate-700); font-size: 15px; line-height: 1.6; margin: 0;">At €16 to €42 for a 60–90 minute voyage through 100+ kilometers of UNESCO-listed waterways, an Amsterdam canal cruise is an indispensable experience. However, low-budget operators often cram 100+ passengers into suffocating glass tunnels with fogged windows, distorted multilingual speakers, and zero open-air ventilation. We field-tested all major operators to uncover the top 5 standout experiences.</p>
</div>
<div class="tldr-winner-box" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #fff; padding: 24px 28px; border-radius: 16px; margin-bottom: 24px;">
  <span style="display: inline-block; background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; padding: 4px 12px; border-radius: 999px; margin-bottom: 8px;">👑 OUR #1 TESTED RECOMMENDATION</span>
  <h3 style="color: #fff; font-family: var(--font-serif); font-size: 22px; margin: 0 0 10px 0;">Lovers Canal Cruises (Central Station)</h3>
  <p style="color: #cbd5e1; font-size: 14.5px; line-height: 1.6; margin: 0;">The gold-standard 1-hour Amsterdam canal cruise: modern all-weather glass saloon with sliding roof panels, GPS audio commentary in 19 languages with complimentary earphones, and departures every 15–30 minutes directly opposite Amsterdam Centraal Station.</p>
</div>'''

    bd_top_bar = '''<div class="bpa-breakdown-top-bar" id="breakdown-header">
  <div style="flex: 1; min-width: 260px;">
    <h2 class="bpa-breakdown-heading">Detailed Breakdown — 5 Best Amsterdam Canal Cruises</h2>
    <p class="bpa-breakdown-sub">Personally field-tested • All reviews open by default • Click to collapse/expand</p>
  </div>
  <div class="bpa-acc-controls">
    <button type="button" class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)">Expand All</button>
    <button type="button" class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)">Collapse All</button>
  </div>
</div>'''

    details_cards = cur_soup.find_all('details', class_='bpa-details-card')
    details_html = '\n'.join(str(c) for c in details_cards)

    spec = orig_soup.find(id='specialized-cruises')
    open_cov = orig_soup.find(id='open-vs-covered')
    route_g = orig_soup.find(id='canal-route-guide')
    faq = orig_soup.find(id='faq-section')
    verdict = orig_soup.find(class_='final-verdict-box')

    post_sections = '\n'.join(str(s) for s in [spec, open_cov, route_g, faq, verdict] if s)

    right_content = f'''{bd_top_bar}
<div id="in-depth-reviews">
  {details_html}
</div>
<div class="ltt-post-guide" id="buying-guide">
  {post_sections}
</div>'''

    sticky = build_sticky_bar(
        'Lovers Canal Cruises',
        'Central Station Pier • 1h00m Audio Cruise',
        'From €16',
        'Book Lovers Canal Cruise (€16+) →',
        'https://www.tiqets.com/en/things-to-do-in-amsterdam-c75061/tickets-for-1-hour-canal-cruise-from-central-station-p973666/?partner=thecruisedetective.com-176436&tq_campaign=ams-can-det-lovers'
    )

    head = build_head(
        'The 5 Best Amsterdam Canal Cruises (2026 Ranked & Tested) | The Cruise Detective',
        'Compare the 5 best Amsterdam canal boat tours. Tested in person: Lovers Canal Cruises vs Captain Jack vs Flagship Amsterdam vs Blue Boat.',
        'https://www.thecruisedetective.com/canal-cruises-amsterdam'
    )

    page_html = build_page_skeleton(
        head_html=head,
        hero_img_url='https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/65562265e60663a885093897_paris-dinner-cruises-featured-image.webp',
        hero_img_alt='Amsterdam Historic Canal Ring Cruise passing illuminated bridge',
        breadcrumb_text='5 Best Amsterdam Canal Cruises (2026 Ranked & Tested)',
        h1_title='The 5 Best Amsterdam Canal Cruises (2026 Ranked & Tested)',
        date_text='March 2026 • Personally Field-Tested Undercover',
        intro_content_html=intro_html,
        comparison_table_html=comp_html,
        right_content_html=right_content,
        sticky_bar_html=sticky,
        page_slug='canal-cruises-amsterdam'
    )

    out_path = os.path.join(BASE_DIR, 'canal-cruises-amsterdam/index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"Saved {out_path} ({len(page_html)} bytes)")

# ==============================================================================
# 4. BUILD LONDON THAMES CRUISES
# ==============================================================================
def build_thames_cruises_london():
    print("Building /thames-river-cruises-london/index.html ...")
    cur_soup = get_current_soup('thames-river-cruises-london/index.html')

    deck_box = cur_soup.find(class_='ltt-header-box')
    deck_grid = cur_soup.find(id='ltt-cards-deck')
    comp_html = f'{str(deck_box)}\n{str(deck_grid)}'

    intro_html = '''<p>With tidal currents shifting up to 7 meters twice daily and iconic bridges framing the Houses of Parliament, Tower Bridge, and Greenwich, the River Thames is London's true historic spine. But choosing the wrong cruise can turn a scenic milestone into an overcrowded commute.</p>
<p>We personally tested and benchmarked all 10 major Thames river cruise options—from budget sightseeing boats to 50-knot high-speed rigid inflatable speedboats and sunset jazz dinners—to help you pick the perfect voyage for your London itinerary.</p>
<blockquote>💡 <strong>Tested Captain Tip:</strong> For the most dramatic skyline transition and open-air photography, take the <strong>Westminster to Greenwich route</strong> around 16:30–17:30 to catch the golden hour light hitting St. Paul's Cathedral and the Tower of London before passing beneath Tower Bridge.</blockquote>'''

    itin = cur_soup.find(id='london-itinerary')
    itin_html = str(itin) if itin else ''

    bd_top_bar = '''<div class="bpa-breakdown-top-bar" id="breakdown-header">
  <div style="flex: 1; min-width: 260px;">
    <h2 class="bpa-breakdown-heading">Detailed Breakdown — 10 Best Thames River Cruises in London</h2>
    <p class="bpa-breakdown-sub">Personally field-tested • All reviews open by default • Click to collapse/expand</p>
  </div>
  <div class="bpa-acc-controls">
    <button type="button" class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)">Expand All</button>
    <button type="button" class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)">Collapse All</button>
  </div>
</div>'''

    details_cards = cur_soup.find_all('details', class_='bpa-details-card')
    details_html = '\n'.join(str(c) for c in details_cards)

    right_content = f'''{itin_html}
{bd_top_bar}
<div id="in-depth-reviews">
  {details_html}
</div>'''

    sticky = build_sticky_bar(
        'Thames River Sightseeing',
        'Westminster to Greenwich • Multi-Pier Single / Return',
        'From £15.50',
        'Book Thames Sightseeing (£15.50+) →',
        'https://www.tiqets.com/en/things-to-do-in-london-c67491/tickets-for-thames-river-sightseeing-cruise-p975431/?partner=thecruisedetective.com-176436&tq_campaign=ldn-thm-det-trs'
    )

    head = build_head(
        '10 Best Thames River Cruises in London (2026 Ranked & Tested) | The Cruise Detective',
        'Compare the 10 best London Thames river cruises. Tested in person: Thames River Sightseeing vs City Cruises vs Thames Rockets speedboat.',
        'https://www.thecruisedetective.com/thames-river-cruises-london'
    )

    page_html = build_page_skeleton(
        head_html=head,
        hero_img_url='https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/656b5269b59a73ed77082a40_best-london-river-cruises-featured-image.webp',
        hero_img_alt='London Thames River Cruise passing Tower Bridge and The Shard',
        breadcrumb_text='10 Best Thames River Cruises in London (2026 Ranked & Tested)',
        h1_title='10 Best Thames River Cruises in London (2026 Ranked & Tested)',
        date_text='March 2026 • Personally Field-Tested Undercover',
        intro_content_html=intro_html,
        comparison_table_html=comp_html,
        right_content_html=right_content,
        sticky_bar_html=sticky,
        page_slug='thames-river-cruises-london'
    )

    out_path = os.path.join(BASE_DIR, 'thames-river-cruises-london/index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"Saved {out_path} ({len(page_html)} bytes)")

# ==============================================================================
# 5. BUILD BATEAUX MOUCHES VS BATEAUX PARISIENS
# ==============================================================================
def build_head_to_head():
    print("Building /bateaux-mouches-vs-bateaux-parisiens.../index.html ...")
    orig_soup = get_orig_soup('bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html')
    cur_soup = get_current_soup('bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html')

    # Intro content
    intro_html = '''<p>Bateaux Mouches and Bateaux Parisiens are the two undisputed titans of Paris river dining. Together, they host more than 60% of all evening diners on the Seine. Yet despite similar pricing (€115–€165), their onboard atmospheres, seating geometries, culinary methodologies, and route viewpoints are fundamentally distinct.</p>
<div class="warning-callout" style="background: #fffbeb; border-left: 4px solid var(--gold-primary); padding: 20px 24px; border-radius: 0 12px 12px 0; margin: 24px 0;">
  <h3 style="font-family: var(--font-serif); font-size: 20px; color: var(--slate-900); margin: 0 0 8px 0;">Want A Quick Answer? Here's The Verdict:</h3>
  <p style="color: var(--slate-700); font-size: 15px; line-height: 1.6; margin: 0;"><strong>Choose Bateaux Mouches (Pont de l'Alma)</strong> if you want traditional romantic grand dining, live piano and violin throughout the meal, and an open-air 360° roof deck accessible anytime.<br/>
  <strong>Choose Bateaux Parisiens (Pier 3, Eiffel Tower)</strong> if you want contemporary all-glass greenhouse visibility with zero center partitions, refined modern plated gastronomy, and departure directly at the foot of the Eiffel Tower.</p>
</div>'''

    # Comparison deck / matrix from current soup
    deck = cur_soup.find(id='ltt-cards-deck') or cur_soup.find(class_='bpa-deck-grid')
    deck_box = cur_soup.find(class_='ltt-header-box')
    comp_html = f'{str(deck_box) if deck_box else ""}\n{str(deck) if deck else ""}'

    # Main comparison sections
    main_art = cur_soup.find('main') or cur_soup.find('article') or cur_soup.find(class_='content-right_blog')
    details_cards = cur_soup.find_all('details', class_='bpa-details-card')
    details_html = '\n'.join(str(c) for c in details_cards)

    bd_top_bar = '''<div class="bpa-breakdown-top-bar" id="breakdown-header">
  <div style="flex: 1; min-width: 260px;">
    <h2 class="bpa-breakdown-heading">Detailed Head-to-Head Comparison &amp; Field Audits</h2>
    <p class="bpa-breakdown-sub">Personally field-tested • All sections open by default • Click to collapse/expand</p>
  </div>
  <div class="bpa-acc-controls">
    <button type="button" class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)">Expand All</button>
    <button type="button" class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)">Collapse All</button>
  </div>
</div>'''

    right_content = f'''{bd_top_bar}
<div id="in-depth-reviews">
  {details_html}
</div>'''

    sticky = build_sticky_bar(
        'Bateaux Mouches 20:30 Prestige',
        'Pont de l\'Alma Pier • Traditional French Piano & Violin',
        'From €130',
        'Book Bateaux Mouches (€130) →',
        'https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-on-the-seine-p982924/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-mouches'
    )

    head = build_head(
        'Bateaux Mouches vs. Bateaux Parisiens Dinner Cruise (Side-by-Side Comparison) | The Cruise Detective',
        'Compare Bateaux Mouches vs Bateaux Parisiens dinner cruises. We tested both: menus, prices, views, live music, and seating compared side by side.',
        'https://www.thecruisedetective.com/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison'
    )

    page_html = build_page_skeleton(
        head_html=head,
        hero_img_url='https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/65562265e60663a885093897_paris-dinner-cruises-featured-image.webp',
        hero_img_alt='Bateaux Mouches vs Bateaux Parisiens Seine Dinner Cruise comparison',
        breadcrumb_text='Bateaux Mouches vs. Bateaux Parisiens Dinner Cruise Showdown',
        h1_title='Bateaux Mouches vs. Bateaux Parisiens Dinner Cruise (Side-by-Side Comparison)',
        date_text='March 2026 • Personally Field-Tested Undercover',
        intro_content_html=intro_html,
        comparison_table_html=comp_html,
        right_content_html=right_content,
        sticky_bar_html=sticky,
        page_slug='bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison'
    )

    out_path = os.path.join(BASE_DIR, 'bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(page_html)
    print(f"Saved {out_path} ({len(page_html)} bytes)")

if __name__ == '__main__':
    build_dinner_cruises_paris()
    build_seine_river_cruises_paris()
    build_canal_cruises_amsterdam()
    build_thames_cruises_london()
    build_head_to_head()
    print("ALL 5 ESTABLISHED EDITORIAL PAGES SUCCESSFULLY REBUILT!")
