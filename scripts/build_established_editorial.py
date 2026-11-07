#!/usr/bin/env python3
"""
THE CRUISE DETECTIVE — ESTABLISHED EDITORIAL ARTICLE BUILDER
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
    <div class="hybrid-pick-context">
      <span class="hybrid-pick-badge">🏆 #1 TESTED PICK</span>
      <span class="hybrid-pick-title">{pick_label}</span>
      <span class="hybrid-pick-meta">{pick_desc} • <strong>{pick_price}</strong></span>
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

print("Loaded base builder module.")
