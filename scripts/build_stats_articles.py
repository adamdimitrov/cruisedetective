#!/usr/bin/env python3
"""
Generate the three city tourism statistics pages for thecruisedetective.com:
- /paris-tourism-statistics/index.html
- /amsterdam-tourism-statistics/index.html
- /london-tourism-statistics/index.html

Strict compliance with STATS_ARTICLES.md:
- ZERO em dashes (—) anywhere
- Recomputed mathematics
- Question-style H2s
- Direct numerical answer in first sentence
- Inline responsive bar charts + <details> data tables
- Scoped CSS under native Cruise Detective layout
- Natural internal links (never inside data tables)
- Sources and methodology with exact URLs and dataset IDs
"""

import os
import re

BASE_DIR = "/Users/adamdimitrov/Development/cruisedetective-stats"

COMMON_HEAD_CSS = """<style id="cd-kill-webflow-badge">
.w-webflow-badge, a.w-webflow-badge, [class*="w-webflow-badge"] {
  display: none !important; opacity: 0 !important; visibility: hidden !important; pointer-events: none !important;
  position: absolute !important; top: -99999px !important; left: -99999px !important; width: 0 !important; height: 0 !important; z-index: -99999 !important;
}

/* Nav & Drawer styles */
.ltt-navbar {
  position: sticky !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 68px !important;
  background: rgba(255, 255, 255, 0.96) !important; backdrop-filter: blur(14px) !important; -webkit-backdrop-filter: blur(14px) !important;
  border-bottom: 1px solid #e2e8f0 !important; z-index: 100000 !important; box-sizing: border-box !important;
}
.ltt-nav-inner {
  max-width: 1240px !important; margin: 0 auto !important; padding: 0 20px !important; height: 100% !important;
  display: flex !important; align-items: center !important; justify-content: space-between !important; box-sizing: border-box !important;
}
.ltt-brand {
  display: inline-flex !important; align-items: center !important; gap: 10px !important; text-decoration: none !important;
  color: #0f172a !important; flex-shrink: 0 !important; font-weight: 800 !important; font-size: 15px !important;
  letter-spacing: 0.04em !important; text-transform: uppercase !important;
}
.ltt-brand-logo {
  width: 36px !important; height: 36px !important; object-fit: contain !important; display: block !important; flex-shrink: 0 !important;
}
.ltt-brand-text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important; }
.ltt-nav-links {
  display: flex !important; align-items: center !important; gap: 16px !important; margin: 0 !important; padding: 0 !important; list-style: none !important;
}
.ltt-nav-link {
  color: #334155 !important; text-decoration: none !important; font-size: 14px !important; font-weight: 600 !important;
  display: inline-flex !important; align-items: center !important; gap: 6px !important; padding: 8px 12px !important;
  border-radius: 8px !important; transition: all 0.15s ease !important; background: transparent !important; border: none !important; cursor: pointer !important;
}
.ltt-nav-link:hover { color: #0f172a !important; background: #f1f5f9 !important; }
.ltt-nav-dropdown { position: relative !important; }
.ltt-chevron { transition: transform 0.2s ease !important; }
.ltt-nav-dropdown.is-open .ltt-chevron { transform: rotate(180deg) !important; }
.ltt-mega-menu {
  position: absolute !important; top: calc(100% + 8px) !important; left: 0 !important; width: 560px !important;
  background: #ffffff !important; border: 1px solid #e2e8f0 !important; border-radius: 12px !important;
  box-shadow: 0 16px 36px -4px rgba(15,23,42,0.15) !important; padding: 16px !important; display: none !important;
  grid-template-columns: 1fr 1fr !important; gap: 16px !important; z-index: 100001 !important;
}
.ltt-nav-dropdown.is-open .ltt-mega-menu { display: grid !important; }
.ltt-mega-head { font-size: 11px !important; font-weight: 800 !important; color: #94a3b8 !important; letter-spacing: 0.08em !important; margin-bottom: 8px !important; }
.ltt-mega-item {
  display: flex !important; align-items: flex-start !important; gap: 10px !important; padding: 8px 10px !important;
  border-radius: 8px !important; text-decoration: none !important; color: #1e293b !important; font-size: 13px !important; transition: background 0.12s ease !important;
}
.ltt-mega-item:hover { background: #f8fafc !important; }
.ltt-mega-item strong { display: block !important; color: #0f172a !important; font-size: 13px !important; }
.ltt-mega-item p { margin: 2px 0 0 0 !important; font-size: 11.5px !important; color: #64748b !important; line-height: 1.3 !important; }
.ltt-mega-icon { font-size: 18px !important; line-height: 1 !important; flex-shrink: 0 !important; margin-top: 2px !important; }
.ltt-hamburger {
  width: 42px !important; height: 42px !important; padding: 10px 8px !important; background: transparent !important;
  border: 1px solid #cbd5e1 !important; border-radius: 10px !important; cursor: pointer !important;
  display: none !important; flex-direction: column !important; justify-content: space-between !important; align-items: center !important; box-sizing: border-box !important;
}
.ltt-hamburger-bar {
  display: block !important; width: 22px !important; height: 2px !important; background: #0f172a !important;
  border-radius: 2px !important; transition: transform 0.25s cubic-bezier(0.16,1,0.3,1), opacity 0.2s ease !important;
}
.ltt-hamburger.is-active .ltt-hamburger-bar:nth-child(1) { transform: translateY(10px) rotate(45deg) !important; }
.ltt-hamburger.is-active .ltt-hamburger-bar:nth-child(2) { opacity: 0 !important; }
.ltt-hamburger.is-active .ltt-hamburger-bar:nth-child(3) { transform: translateY(-10px) rotate(-45deg) !important; }
.ltt-mobile-drawer {
  position: fixed !important; top: 68px !important; left: 0 !important; width: 100% !important; height: calc(100vh - 68px) !important;
  background: #ffffff !important; overflow-y: auto !important; transform: translateX(100%) !important;
  transition: transform 0.25s ease !important; z-index: 99999 !important; padding: 20px !important; box-sizing: border-box !important;
}
.ltt-mobile-drawer.is-open { transform: translateX(0) !important; }
.ltt-mobile-section { margin-bottom: 24px !important; }
.ltt-mobile-label { font-size: 11px !important; font-weight: 800 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; color: #94a3b8 !important; margin-bottom: 8px !important; }
.ltt-mobile-link {
  display: flex !important; align-items: center !important; justify-content: space-between !important; padding: 12px 14px !important;
  border-radius: 8px !important; text-decoration: none !important; color: #0f172a !important; font-weight: 600 !important; font-size: 14px !important;
}
.ltt-mobile-link:hover { background: #f8fafc !important; }

@media (max-width: 991px) {
  .ltt-nav-links { display: none !important; }
  .ltt-hamburger { display: flex !important; }
}

html, body {
  overflow-x: hidden !important;
  max-width: 100vw !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

/* Page Parity Layout */
.container-31, .container-26 { width: 100% !important; max-width: 1240px !important; margin: 0 auto !important; padding: 0 16px !important; box-sizing: border-box !important; }
.blog-grid-2 { position: relative !important; display: block !important; padding-left: 270px !important; box-sizing: border-box !important; width: 100% !important; }
.content-left { display: block !important; width: 230px !important; position: absolute !important; top: 0 !important; bottom: 0 !important; left: 0 !important; }
.stick-wrapper { position: sticky !important; top: 88px !important; max-height: calc(100vh - 104px) !important; overflow-y: auto !important; z-index: 90 !important; padding-top: 6px !important; }
.content-right_blog { width: 100% !important; max-width: 920px !important; box-sizing: border-box !important; display: block !important; }

/* Sticky Table of Contents */
.bpa-toc-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 14px; font-size: 13px; line-height: 1.4; }
.bpa-toc-title { font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin-bottom: 10px; }
.bpa-toc-list { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 6px; }
.bpa-toc-list a { color: #334155; text-decoration: none; display: block; padding: 4px 6px; border-radius: 6px; transition: all 0.15s ease; font-weight: 600; font-size: 12.5px; }
.bpa-toc-list a:hover { color: #0f172a; background: #e2e8f0; }

@media (max-width: 991px) {
  .blog-grid-2 { padding-left: 0 !important; width: 100% !important; max-width: 100% !important; display: block !important; }
  .content-left { display: none !important; width: 0 !important; height: 0 !important; overflow: hidden !important; visibility: hidden !important; pointer-events: none !important; position: absolute !important; }
  .content-right_blog { max-width: 100% !important; width: 100% !important; }
  .w-layout-blockcontainer, .container, .w-container, .w-richtext { max-width: 100% !important; width: 100% !important; box-sizing: border-box !important; }
}

/* Editorial Hero Card */
.ltt-hero-wrap { width: 100% !important; max-width: 1240px !important; margin: 22px auto 0 !important; padding: 0 16px !important; box-sizing: border-box !important; color: #0f172a !important; }
.ltt-clean-card { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 20px; padding: 26px 32px 24px 32px; box-shadow: 0 4px 20px -4px rgba(15,23,42,0.05), 0 1px 3px rgba(15,23,42,0.02); box-sizing: border-box; }
.ltt-top-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
.ltt-breadcrumbs { display: inline-flex; align-items: center; flex-wrap: wrap; gap: 6px; font-size: 12.5px; font-weight: 600; color: #64748b; margin: 0; }
.ltt-breadcrumbs a { color: #475569 !important; text-decoration: none !important; transition: color 0.15s ease; }
.ltt-breadcrumbs a:hover { color: #0f172a !important; text-decoration: underline !important; }
.ltt-breadcrumbs .ltt-bc-sep { color: #cbd5e1; font-size: 11px; }
.ltt-breadcrumbs .ltt-bc-current { color: #0f172a; font-weight: 700; }
.ltt-hero-kicker-badge { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; color: #0369a1; background: #f0f9ff; border: 1px solid #bae6fd; padding: 4px 10px; border-radius: 999px; }
.ltt-editorial-h1 { font-size: clamp(26px, 3.2vw, 38px) !important; font-weight: 800 !important; line-height: 1.18 !important; letter-spacing: -0.025em !important; color: #0f172a !important; margin: 0 0 14px 0 !important; }
.ltt-editorial-h1 span.ltt-h1-muted { color: #475569; font-weight: 700; }
.ltt-trust-bar { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px; padding: 10px 14px; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; margin-bottom: 14px; }
.ltt-author-cluster { display: flex; align-items: center; gap: 12px; }
.ltt-author-avatar-wrap { position: relative; width: 42px; height: 42px; flex-shrink: 0; }
.ltt-author-avatar { width: 42px !important; height: 42px !important; border-radius: 50% !important; object-fit: cover !important; border: 2px solid #cbd5e1 !important; display: block !important; }
.ltt-author-meta { display: flex; flex-direction: column; gap: 2px; }
.ltt-author-line { font-size: 13.5px; color: #0f172a; font-weight: 700; }
.ltt-author-line a { color: #0f172a !important; text-decoration: underline !important; }
.ltt-author-role { font-size: 12px; color: #64748b; font-weight: 500; }
.ltt-author-role a { color: #0284c7; text-decoration: underline; }
.ltt-trust-pills { display: flex; align-items: center; flex-wrap: wrap; gap: 8px; }
.ltt-trust-pill { display: inline-block !important; font-size: 12px !important; font-weight: 600 !important; color: #334155 !important; background: #ffffff !important; border: 1px solid #e2e8f0 !important; padding: 5px 11px !important; border-radius: 8px !important; }
.ltt-lead-copy { font-size: 15.5px !important; line-height: 1.65 !important; color: #334155 !important; margin: 0 !important; }
.ltt-lead-copy p { margin: 0 0 10px 0 !important; }
.ltt-lead-copy p:last-child { margin-bottom: 0 !important; }

/* Article Typography & Section Structure */
.bpa-article { font-size: 16px; line-height: 1.7; color: #334155; }
.bpa-article h2 { font-size: 26px; font-weight: 800; color: #0f172a; margin: 44px 0 16px; letter-spacing: -0.02em; line-height: 1.25; scroll-margin-top: 84px; }
.bpa-article h3 { font-size: 20px; font-weight: 700; color: #0f172a; margin: 28px 0 12px; line-height: 1.3; }
.bpa-article p { margin-bottom: 16px; }
.bpa-article ul, .bpa-article ol { margin: 0 0 18px 24px; padding: 0; }
.bpa-article li { margin-bottom: 8px; }
.bpa-article strong { color: #0f172a; }

/* Key Takeaways Callout */
.bpa-callout { background: #f8fafc; border: 1px solid #cbd5e1; border-left: 4px solid #0284c7; border-radius: 12px; padding: 20px 24px; margin: 24px 0; }
.bpa-callout-title { font-size: 15px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.06em; color: #0f172a; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.bpa-callout ul { margin: 0 0 0 20px; padding: 0; }
.bpa-callout li { margin-bottom: 8px; font-size: 15px; line-height: 1.55; }
.bpa-callout li:last-child { margin-bottom: 0; }

/* Key Statistics Tiles Grid */
.bpa-tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: 20px 0 24px; }
.bpa-tile { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 14px; box-sizing: border-box; }
.bpa-tile-num { font-size: 32px; font-weight: 800; color: #0f172a; line-height: 1.1; letter-spacing: -0.02em; }
.bpa-tile-lab { font-size: 13px; color: #64748b; margin-top: 4px; line-height: 1.35; font-weight: 500; }
@media (max-width: 768px) {
  .bpa-tiles { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .bpa-tiles { grid-template-columns: 1fr; }
  .bpa-tile-num { font-size: 26px; }
}

/* Statistics Charts with Budapest Parity Markup */
.bpa-chart { background: #ffffff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 20px 20px 14px; margin: 20px 0 16px; box-sizing: border-box; }
.bpa-chart-head { margin-bottom: 8px; }
.bpa-chart-title { font-weight: 800; font-size: 16px; color: #0f172a; line-height: 1.3; }
.bpa-chart-sub { font-size: 13px; color: #64748b; margin-top: 2px; }
.bpa-legend { display: flex; flex-wrap: wrap; gap: 14px; margin: 12px 0 4px; font-size: 13px; color: #334155; }
.bpa-leg { display: inline-flex; align-items: center; gap: 6px; }
.bpa-leg i { display: inline-block; width: 12px; height: 12px; border-radius: 3px; }
.bpa-bars { margin-top: 12px; }
.bpa-row { display: grid; grid-template-columns: 92px 1fr; align-items: center; gap: 10px; margin: 7px 0; }
.bpa-lab { font-size: 13px; color: #334155; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bpa-track { display: flex; align-items: center; gap: 2px; min-width: 0; }
.bpa-seg { display: block; height: 18px; min-width: 2px; }
.bpa-track .bpa-seg:last-of-type { border-radius: 0 4px 4px 0; }
.bpa-val { font-size: 13px; font-weight: 700; color: #0f172a; margin-left: 8px; white-space: nowrap; }
.bpa-pair { display: flex; flex-direction: column; gap: 3px; min-width: 0; }
.bpa-pair .bpa-seg { height: 12px; }
.bpa-src { font-size: 12px; color: #64748b; margin-top: 12px; line-height: 1.5; }
.bpa-src a { color: #475569 !important; text-decoration: underline; }

/* Expandable Data Tables */
.bpa-details { margin: 4px 0 24px; width: 100% !important; max-width: 100% !important; box-sizing: border-box !important; }
.bpa-details summary { cursor: pointer; font-size: 13.5px; font-weight: 700; color: #0369a1; padding: 4px 0; display: inline-flex; align-items: center; gap: 6px; user-select: none; }
.bpa-details summary:hover { text-decoration: underline; }
.bpa-table-wrap { overflow-x: auto !important; -webkit-overflow-scrolling: touch !important; margin: 8px 0 20px; border: 1px solid #e2e8f0; border-radius: 10px; width: 100% !important; max-width: 100% !important; box-sizing: border-box !important; }
.bpa-table { width: 100%; min-width: 480px; border-collapse: collapse; font-size: 13.5px; font-variant-numeric: tabular-nums; background: #ffffff; }
.bpa-table caption { caption-side: bottom; text-align: left; font-size: 12px; color: #64748b; padding-top: 8px; }
.bpa-table th { text-align: left; font-weight: 700; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding: 9px 12px; white-space: nowrap; background: #f8fafc; }
.bpa-table td { border-bottom: 1px solid #f1f5f9; padding: 8px 12px; color: #334155; white-space: nowrap; }
.bpa-table tr:last-child td { border-bottom: none; }
.bpa-table td:not(:first-child), .bpa-table th:not(:first-child) { text-align: right; }
.bpa-table tr:hover td { background: #f8fafc; }
.bpa-cite { background: #fffbeb; border: 1px solid #fde68a; border-radius: 12px; padding: 16px; font-size: 14.5px; line-height: 1.6; color: #334155; margin: 20px 0; }
.bpa-cite a { color: #b45309; text-decoration: underline; font-weight: 600; }

@media (max-width: 520px) {
  .bpa-row { grid-template-columns: 68px 1fr; gap: 6px; }
  .bpa-chart { padding: 16px 12px 12px; }
  .bpa-val { font-size: 11.5px; margin-left: 5px; }
  .bpa-lab { font-size: 12px; }
}

/* Sources & Methodology Section */
.bpa-sources-box { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 24px 28px; margin: 40px 0 20px; }
.bpa-sources-box h3 { font-size: 17px; font-weight: 800; color: #0f172a; margin: 18px 0 8px; }
.bpa-sources-box h3:first-child { margin-top: 0; }
.bpa-sources-box p, .bpa-sources-box li { font-size: 14px; line-height: 1.6; color: #475569; }
.bpa-sources-box a { color: #0284c7; text-decoration: underline; }

/* Editorial Bookmark Cross-Link Card */
.cd-bookmark-wrapper { margin: 28px 0 24px 0 !important; width: 100% !important; }
.cd-editorial-bookmark {
  display: flex !important; flex-direction: row !important; justify-content: space-between !important;
  text-decoration: none !important; background: #ffffff !important; border: 1px solid #e2e8f0 !important;
  border-radius: 14px !important; overflow: hidden !important; box-shadow: 0 4px 14px rgba(15,23,42,0.04) !important;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease !important;
}
.cd-editorial-bookmark:hover { transform: translateY(-2px) !important; box-shadow: 0 8px 24px rgba(15,23,42,0.08) !important; border-color: #cbd5e1 !important; }
.cd-bookmark-content { padding: 18px 22px !important; flex: 1 !important; display: flex !important; flex-direction: column !important; justify-content: center !important; }
.cd-bookmark-kicker { font-size: 11px !important; font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; color: #0284c7 !important; margin-bottom: 4px !important; }
.cd-bookmark-title { font-size: 17px !important; font-weight: 800 !important; color: #0f172a !important; line-height: 1.3 !important; margin-bottom: 6px !important; }
.cd-bookmark-desc { font-size: 13.5px !important; color: #64748b !important; line-height: 1.4 !important; margin: 0 !important; }
.cd-bookmark-image-wrap { width: 180px !important; flex-shrink: 0 !important; background: #f1f5f9 !important; overflow: hidden !important; position: relative !important; }
.cd-bookmark-img { width: 100% !important; height: 100% !important; object-fit: cover !important; display: block !important; }

@media (max-width: 640px) {
  .cd-editorial-bookmark { flex-direction: column !important; }
  .cd-bookmark-image-wrap { width: 100% !important; height: 160px !important; }
  .ltt-clean-card { padding: 20px 16px; border-radius: 14px; }
}
</style>"""

COMMON_HEADER_HTML = """<header class="ltt-navbar" role="banner">
  <div class="ltt-nav-inner">
    <a aria-label="THE CRUISE DETECTIVE Homepage" class="ltt-brand" href="/">
      <img alt="THE CRUISE DETECTIVE Logo" class="ltt-brand-logo" height="36" src="/assets/cdn/652d0405192ba076b04f74a3/6570a89c8c97ba4e084ac5d5_webclip-cruise-detective.png" width="36"/>
      <span class="ltt-brand-text">THE CRUISE DETECTIVE</span>
    </a>
    <nav aria-label="Primary Navigation" class="ltt-nav-links">
      <div class="ltt-nav-dropdown" id="lttExploreDropdown">
        <button aria-expanded="false" aria-haspopup="true" class="ltt-nav-link ltt-dropdown-btn" type="button">
          <span>Destinations</span>
          <svg class="ltt-chevron" fill="none" height="12" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" viewBox="0 0 24 24" width="12">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        <div class="ltt-mega-menu" role="menu">
          <div class="ltt-mega-col">
            <div class="ltt-mega-head">PARIS SEINE RIVER</div>
            <a class="ltt-mega-item" href="/seine-river-cruises-paris">
              <span class="ltt-mega-icon">🗼</span>
              <div>
                <strong>Paris Sightseeing Cruises</strong>
                <p>Top daytime &amp; illuminations tours</p>
              </div>
            </a>
            <a class="ltt-mega-item" href="/dinner-cruises-paris">
              <span class="ltt-mega-icon">🍷</span>
              <div>
                <strong>Paris Dinner Cruises</strong>
                <p>10 tested boats &amp; evening tasting notes</p>
              </div>
            </a>
            <a class="ltt-mega-item" href="/paris-tourism-statistics">
              <span class="ltt-mega-icon">📊</span>
              <div>
                <strong>Paris Tourism Statistics</strong>
                <p>Official arrivals, nights &amp; spending</p>
              </div>
            </a>
          </div>
          <div class="ltt-mega-col">
            <div class="ltt-mega-head">AMSTERDAM &amp; LONDON</div>
            <a class="ltt-mega-item" href="/canal-cruises-amsterdam">
              <span class="ltt-mega-icon">🌷</span>
              <div>
                <strong>Amsterdam Canal Cruises</strong>
                <p>Open sloops &amp; classic salon boats</p>
              </div>
            </a>
            <a class="ltt-mega-item" href="/amsterdam-tourism-statistics">
              <span class="ltt-mega-icon">📊</span>
              <div>
                <strong>Amsterdam Tourism Statistics</strong>
                <p>Official CBS visitor &amp; tax data</p>
              </div>
            </a>
            <a class="ltt-mega-item" href="/thames-river-cruises-london">
              <span class="ltt-mega-icon">🇬🇧</span>
              <div>
                <strong>London Thames Cruises</strong>
                <p>Sightseeing &amp; speedboat tours</p>
              </div>
            </a>
            <a class="ltt-mega-item" href="/london-tourism-statistics">
              <span class="ltt-mega-icon">📊</span>
              <div>
                <strong>London Tourism Statistics</strong>
                <p>Official ONS visits &amp; spending data</p>
              </div>
            </a>
          </div>
        </div>
      </div>
      <a class="ltt-nav-link" href="/seine-river-cruises-paris">Paris Cruises</a>
      <a class="ltt-nav-link" href="/canal-cruises-amsterdam">Amsterdam Cruises</a>
      <a class="ltt-nav-link" href="/thames-river-cruises-london">London Cruises</a>
      <a class="ltt-nav-link" href="/about">About</a>
      <a class="ltt-nav-link" href="/contact">Contact</a>
    </nav>
    <div class="ltt-nav-right">
      <button aria-controls="lttMobileDrawer" aria-expanded="false" aria-label="Toggle Menu" class="ltt-hamburger" id="lttNavToggle" type="button">
        <span class="ltt-hamburger-bar"></span>
        <span class="ltt-hamburger-bar"></span>
        <span class="ltt-hamburger-bar"></span>
      </button>
    </div>
  </div>
  <div aria-hidden="true" inert class="ltt-mobile-drawer" id="lttMobileDrawer">
    <div class="ltt-drawer-content">
      <div class="ltt-mobile-section">
        <div class="ltt-mobile-label">Destinations &amp; Statistics</div>
        <a class="ltt-mobile-link" href="/seine-river-cruises-paris"><span>🗼 Paris Sightseeing Cruises</span></a>
        <a class="ltt-mobile-link" href="/dinner-cruises-paris"><span>🍷 Paris Dinner Cruises</span></a>
        <a class="ltt-mobile-link" href="/paris-tourism-statistics"><span>📊 Paris Tourism Statistics</span></a>
        <a class="ltt-mobile-link" href="/canal-cruises-amsterdam"><span>🌷 Amsterdam Canal Cruises</span></a>
        <a class="ltt-mobile-link" href="/amsterdam-tourism-statistics"><span>📊 Amsterdam Tourism Statistics</span></a>
        <a class="ltt-mobile-link" href="/thames-river-cruises-london"><span>🇬🇧 London Thames Cruises</span></a>
        <a class="ltt-mobile-link" href="/london-tourism-statistics"><span>📊 London Tourism Statistics</span></a>
      </div>
      <div class="ltt-mobile-section">
        <div class="ltt-mobile-label">Editorial</div>
        <a class="ltt-mobile-link" href="/about"><span>📖 About &amp; Manifesto</span></a>
        <a class="ltt-mobile-link" href="/contact"><span>✉️ Contact Editorial Desk</span></a>
      </div>
    </div>
  </div>
</header>"""

COMMON_FOOTER_HTML = """<footer class="footer-dark" role="contentinfo">
<div class="footer-section">
<div class="container-21">
<div class="w-layout-grid footer-grid-2">
<div class="logo-wrap">
<p class="footer-logo-paragraph paragraph-17 paragraph-18">
<a class="footer-logo-text-link" href="/" style="display: inline-flex; align-items: center; gap: 10px;">
<img alt="THE CRUISE DETECTIVE Logo" height="28" src="/assets/cruise_detective_logo.png" style="border-radius: 50%; display: inline-block; flex-shrink: 0;" width="28"/>
<span>THE CRUISE DETECTIVE</span>
</a>
</p>
<p class="footer-paragraph">TheCruiseDetective.com is your independent, field-tested guide to choosing the best river, canal, and dinner cruises across Europe, supported by rigorous city tourism data.</p>
</div>
<div class="w-layout-grid footer-links-grid">
<div class="footer-link-column">
<div class="footer-link-title">Popular Flagship Guides</div>
<a class="footer-link-3" href="/seine-river-cruises-paris">10 Best Seine River Cruises in Paris</a>
<a class="footer-link-3" href="/dinner-cruises-paris">Best Paris Dinner Cruises on the Seine</a>
<a class="footer-link-3" href="/canal-cruises-amsterdam">Best Canal Cruises in Amsterdam</a>
<a class="footer-link-3" href="/thames-river-cruises-london">Best Thames River Cruises in London</a>
</div>
<div class="footer-link-column">
<div class="footer-link-title">Tourism Statistics</div>
<a class="footer-link-3" href="/paris-tourism-statistics">Paris Tourism Statistics</a>
<a class="footer-link-3" href="/amsterdam-tourism-statistics">Amsterdam Tourism Statistics</a>
<a class="footer-link-3" href="/london-tourism-statistics">London Tourism Statistics</a>
<a class="footer-link-3" href="/about">About &amp; Manifesto</a>
<a class="footer-link-3" href="/contact">Contact</a>
</div>
</div>
</div>
<div class="grey-divider"></div>
<div class="legal-wrapper">
<div class="legal-text">&copy; 2026 TheCruiseDetective.com. All rights reserved. &middot; <a class="cd-legal-link" href="/privacy-policy" style="color: inherit; text-decoration: underline;">Privacy Policy</a> &middot; <a class="cd-legal-link" href="/terms-of-service" style="color: inherit; text-decoration: underline;">Terms of Service</a></div>
<div class="legal-text" style="color: rgba(255,255,255,0.45); font-size: 13px;">Data journalism and undercover field testing &bull; Independent editorial reviews</div>
</div>
</div>
</div>
</footer>"""

COMMON_SCRIPTS = """<script>
document.addEventListener('DOMContentLoaded', function() {
  var toggle = document.getElementById('lttNavToggle');
  var drawer = document.getElementById('lttMobileDrawer');
  var dropdownBtn = document.querySelector('#lttExploreDropdown .ltt-dropdown-btn');
  var dropdown = document.getElementById('lttExploreDropdown');

  if (toggle && drawer) {
    toggle.addEventListener('click', function(e) {
      e.stopPropagation();
      var isOpen = drawer.classList.contains('is-open');
      if (isOpen) {
        drawer.classList.remove('is-open');
        toggle.classList.remove('is-active');
        toggle.setAttribute('aria-expanded', 'false');
        drawer.setAttribute('aria-hidden', 'true');
        drawer.setAttribute('inert', '');
        document.body.classList.remove('ltt-drawer-open');
      } else {
        drawer.classList.add('is-open');
        toggle.classList.add('is-active');
        toggle.setAttribute('aria-expanded', 'true');
        drawer.removeAttribute('aria-hidden');
        drawer.removeAttribute('inert');
        document.body.classList.add('ltt-drawer-open');
      }
    });
  }

  if (dropdownBtn && dropdown) {
    dropdownBtn.addEventListener('click', function(e) {
      e.stopPropagation();
      var expanded = dropdownBtn.getAttribute('aria-expanded') === 'true';
      dropdownBtn.setAttribute('aria-expanded', !expanded);
      dropdown.classList.toggle('is-open');
    });

    document.addEventListener('click', function(e) {
      if (!dropdown.contains(e.target)) {
        dropdownBtn.setAttribute('aria-expanded', 'false');
        dropdown.classList.remove('is-open');
      }
    });
  }

  // Smooth scroll for TOC anchors
  var tocLinks = document.querySelectorAll('.content-left a[href^="#"]');
  tocLinks.forEach(function(link) {
    link.addEventListener('click', function(e) {
      var targetId = this.getAttribute('href').slice(1);
      var targetEl = document.getElementById(targetId);
      if (targetEl) {
        e.preventDefault();
        targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
        history.pushState(null, '', '#' + targetId);
      }
    });
  });
});
</script>"""


def get_paris_html():
    canonical = "https://www.thecruisedetective.com/paris-tourism-statistics"
    title = "Paris Tourism Statistics 2026: How Many Tourists Visit?"
    meta_desc = "Paris recorded 18.49 million hotel arrivals and 41.92 million nights in 2025. Official INSEE data on visitors, busiest months, source countries and spending."
    og_image = "https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/656b5108d54edc5c99f86b14_best-river-cruises-paris-featured-image.webp"

    # Verify lengths
    assert len(title) <= 60, f"Title too long: {len(title)}"
    assert 140 <= len(meta_desc) <= 160, f"Meta description invalid length: {len(meta_desc)}"

    # Structured data
    json_ld = """{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Paris Tourism Statistics 2026: How Many Tourists Visit?",
  "description": "Paris recorded 18.49 million hotel arrivals and 41.92 million nights in 2025. Official INSEE data on visitors, busiest months, source countries and spending.",
  "datePublished": "2026-11-13",
  "dateModified": "2026-11-13",
  "inLanguage": "en",
  "mainEntityOfPage": "https://www.thecruisedetective.com/paris-tourism-statistics",
  "author": {
    "@type": "Person",
    "name": "Adam Dimitrov",
    "url": "https://www.thecruisedetective.com/about"
  },
  "publisher": {
    "@type": "Organization",
    "name": "The Cruise Detective",
    "url": "https://www.thecruisedetective.com/"
  },
  "citation": [
    "https://www.insee.fr/en/statistiques/serie/010598702",
    "https://www.insee.fr/en/statistiques/serie/010598705",
    "https://pro.visitparisregion.com/",
    "https://www.parisaeroport.fr/"
  ]
}"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<meta content="{meta_desc}" name="description"/>
<meta content="{title}" property="og:title"/>
<meta content="{meta_desc}" property="og:description"/>
<meta content="{og_image}" property="og:image"/>
<meta content="{canonical}" property="og:url"/>
<meta content="article" property="og:type"/>
<meta content="{title}" name="twitter:title"/>
<meta content="{meta_desc}" name="twitter:description"/>
<meta content="{og_image}" name="twitter:image"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<meta content="google-site-verification=jPygzQl3dLYHsZI7XMPOqvcxGUVZtEr6WiuGN_O2xjo" name="google-site-verification"/>

<link href="/favicon.ico" rel="icon" type="image/x-icon"/>
<link href="/favicon.ico" rel="shortcut icon" type="image/x-icon"/>
<link href="/assets/apple-touch-icon.png" rel="apple-touch-icon"/>
<link href="{canonical}" rel="canonical"/>
<link href="{canonical}" hreflang="en" rel="alternate"/>
<link href="{canonical}" hreflang="x-default" rel="alternate"/>

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet"/>

<!-- Core Stylesheets -->
<link href="/css/thecruisedetective-com.webflow.shared.3cc389acf.min.css" rel="stylesheet" type="text/css"/>

<!-- Analytics -->
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('set', 'developer_id.dZGVlNj', true);
gtag('set', 'developer_id.dYWYxNW', true);
gtag('js', new Date());
gtag('config', 'G-RN34XFKPQ6');

!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];}}(window,document);
fbq('init', '1355732169631751');
fbq('track', 'PageView');
</script>

<script type="application/ld+json">
{json_ld}
</script>

{COMMON_HEAD_CSS}
</head>
<body id="top">
{COMMON_HEADER_HTML}

<main id="main" role="main">
<div class="ltt-hero-wrap">
  <div class="ltt-clean-card">
    <div class="ltt-top-bar">
      <nav aria-label="Breadcrumb" class="ltt-breadcrumbs">
        <a href="/">Home</a>
        <span class="ltt-bc-sep">&rsaquo;</span>
        <span class="ltt-bc-current">Paris Tourism Statistics (2026)</span>
      </nav>
      <span class="ltt-hero-kicker-badge">Official INSEE Data &middot; 2019 to 2025</span>
    </div>
    <h1 class="ltt-editorial-h1">
      Paris Tourism Statistics 2026 <span class="ltt-h1-muted">(How Many Tourists Visit?)</span>
    </h1>
    <div class="ltt-trust-bar">
      <div class="ltt-author-cluster">
        <div class="ltt-author-avatar-wrap">
          <img alt="Adam Dimitrov" class="ltt-author-avatar" height="42" loading="eager" src="/assets/cdn/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp" width="42"/>
        </div>
        <div class="ltt-author-meta">
          <div class="ltt-author-line">
            By <a href="/about" target="_blank">Adam Dimitrov</a>, Owner &amp; Head Cruise Detective
          </div>
          <div class="ltt-author-role">Compiled from Official INSEE Data &bull; 6 Charts with Data Tables &bull; <a href="#sources-and-methodology">Methodology</a></div>
        </div>
      </div>
      <div class="ltt-trust-pills">
        <span class="ltt-trust-pill paragraph-26"><strong>Last updated</strong>: Nov 13, 2026</span>
      </div>
    </div>
    <div class="ltt-lead-copy">
      <p>Paris recorded <strong>18.49 million hotel arrivals</strong> and <strong>41.92 million hotel nights</strong> in 2025, reaching new records for the official INSEE series. Hotel arrivals grew 10.9% compared to 2024, while international travelers generated 67.9% of all overnight stays.</p>
      <p>This report compiles official <strong>Paris tourism statistics</strong> from the French National Institute of Statistics and Economic Studies (INSEE), Choose Paris Region, and Groupe ADP: visitor volumes, average duration of stay, monthly seasonality, key source countries, and total tourism expenditure. Each chart includes a structured data table and primary reference link for verification.</p>
    </div>
  </div>
</div>

<div class="blog-section">
  <div class="container-26">
    <div class="blog-grid-2">
      <div class="content-left">
        <div class="stick-wrapper">
          <div class="title-small-3" style="font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #f1f5f9;">Table of Contents</div>
          <div class="toc" id="toc">
            <a class="tocitem" href="#key-paris-tourism-statistics-2025">Key Paris tourism statistics (2025)</a>
            <a class="tocitem" href="#how-many-tourists-visit-paris-each-year">How many tourists visit Paris each year?</a>
            <a class="tocitem" href="#how-many-nights-do-tourists-spend-in-paris">How many nights do tourists spend in Paris?</a>
            <a class="tocitem" href="#how-long-do-visitors-stay-in-paris">How long do visitors stay in Paris?</a>
            <a class="tocitem" href="#when-do-most-tourists-visit-paris">When do most tourists visit Paris?</a>
            <a class="tocitem" href="#where-do-visitors-to-paris-come-from">Where do visitors to Paris come from?</a>
            <a class="tocitem" href="#how-much-do-tourists-spend-in-paris">How much do tourists spend in Paris?</a>
            <a class="tocitem" href="#how-busy-are-paris-airports">How busy are Paris airports?</a>
            <a class="tocitem" href="#what-are-the-top-destinations-to-visit-in-paris">What are the top destinations to visit in Paris?</a>
            <a class="tocitem" href="#sources-and-methodology">Sources and methodology</a>
          </div>
        </div>
      </div>
      <div class="content-right_blog" id="content">
        <div class="w-layout-blockcontainer container w-container">
          <div class="w-richtext">

            <h2 id="key-paris-tourism-statistics-2025">Key Paris tourism statistics (2025)</h2>
            <div class="bpa-tiles">
              <div class="bpa-tile">
                <div class="bpa-tile-num">18.49M</div>
                <div class="bpa-tile-lab">hotel arrivals in 2025, up 10.9% on 2024</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">41.92M</div>
                <div class="bpa-tile-lab">hotel nights in 2025, up 8.7%</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">67.9%</div>
                <div class="bpa-tile-lab">of hotel nights generated by foreign visitors</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">2.27</div>
                <div class="bpa-tile-lab">nights is the average hotel stay</div>
              </div>
            </div>
            <ul role="list">
              <li>Paris hotels (d&eacute;partement 75) recorded <strong>18,485,600 guest arrivals</strong> in 2025, representing a 10.9% gain over 2024 (16,671,000) and surpassing the 2019 pre-pandemic benchmark of 17,044,800 by 8.5%.</li>
              <li>Guests spent <strong>41,918,000 nights</strong> in Paris hotels during 2025, an 8.7% increase year-on-year and 10.2% above the 38,021,600 nights recorded in 2019.</li>
              <li>International travelers accounted for <strong>59.6% of arrivals</strong> (11,021,500) and <strong>67.9% of hotel nights</strong> (28,482,600).</li>
              <li>Across the wider Paris &Icirc;le-de-France region, total tourist arrivals reached <strong>48.7 million</strong> in 2024 according to Choose Paris Region, including 26.1 million French visitors and 22.6 million international tourists.</li>
              <li>The single busiest month for Paris hotel stays in 2025 was <strong>July</strong> with 3.87 million nights, followed by <strong>October</strong> (3.77 million) and <strong>May</strong> (3.76 million).</li>
              <li>Paris airports (Charles de Gaulle and Orly) handled <strong>103.41 million passengers</strong> in 2024, expanding 3.7% over 2023.</li>
              <li>Tourism spending in the Paris &Icirc;le-de-France region generated <strong>23.4 billion euros</strong> in 2024, with foreign travelers contributing 14.9 billion euros (63.7%).</li>
            </ul>

            <h2 id="how-many-tourists-visit-paris-each-year">How many tourists visit Paris each year?</h2>
            <p>Paris hotels welcomed <strong>18.49 million tourist arrivals</strong> in 2025, rising <strong>10.9%</strong> from 16.67 million in 2024. Across the broader Paris &Icirc;le-de-France administrative region, overall tourist volume reached 48.7 million in 2024.</p>

            <div class="bpa-chart" id="chart-paris-arrivals" role="figure" aria-labelledby="chart-paris-arrivals-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-paris-arrivals-t">Tourist arrivals in Paris hotels, 2019 to 2025</div>
                <div class="bpa-chart-sub">Registered hotel check-ins in the City of Paris (d&eacute;partement 75), millions</div>
              </div>
              <div class="bpa-legend">
                <span class="bpa-leg"><i style="background:#1e3a5f"></i>International</span>
                <span class="bpa-leg"><i style="background:#dfa732"></i>Domestic (France)</span>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:53.56%;background:#1e3a5f" title="2019 international: 9.90 million"></span>
                    <span class="bpa-seg" style="width:38.64%;background:#dfa732" title="2019 domestic: 7.14 million"></span>
                    <b class="bpa-val">17.04M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:50.15%;background:#1e3a5f" title="2022 international: 9.27 million"></span>
                    <span class="bpa-seg" style="width:35.65%;background:#dfa732" title="2022 domestic: 6.59 million"></span>
                    <b class="bpa-val">15.86M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:55.56%;background:#1e3a5f" title="2023 international: 10.27 million"></span>
                    <span class="bpa-seg" style="width:36.23%;background:#dfa732" title="2023 domestic: 6.70 million"></span>
                    <b class="bpa-val">16.97M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:54.62%;background:#1e3a5f" title="2024 international: 10.10 million"></span>
                    <span class="bpa-seg" style="width:35.57%;background:#dfa732" title="2024 domestic: 6.57 million"></span>
                    <b class="bpa-val">16.67M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2025</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:59.62%;background:#1e3a5f" title="2025 international: 11.02 million"></span>
                    <span class="bpa-seg" style="width:40.38%;background:#dfa732" title="2025 domestic: 7.46 million"></span>
                    <b class="bpa-val">18.49M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.insee.fr/en/statistiques/serie/010598702" rel="noopener" target="_blank">INSEE, Enqu&ecirc;te de fr&eacute;quentation h&ocirc;teli&egrave;re, Series 010598702, 010598703, 010598704</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Hotel arrivals in Paris (d&eacute;partement 75), INSEE official series</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Total Arrivals</th>
                      <th>International</th>
                      <th>Domestic</th>
                      <th>Change vs Previous Year</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>17,044,800</td>
                      <td>9,901,800</td>
                      <td>7,143,000</td>
                      <td>Baseline</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>15,860,000</td>
                      <td>9,270,300</td>
                      <td>6,589,700</td>
                      <td>-7.0% vs 2019</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>16,967,700</td>
                      <td>10,270,000</td>
                      <td>6,697,600</td>
                      <td>+7.0%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>16,671,000</td>
                      <td>10,096,300</td>
                      <td>6,574,600</td>
                      <td>-1.8%</td>
                    </tr>
                    <tr>
                      <td>2025</td>
                      <td>18,485,600</td>
                      <td>11,021,500</td>
                      <td>7,464,200</td>
                      <td>+10.9%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>An arrival measures one guest checking in at a commercial hotel located within the municipal limits of Paris (d&eacute;partement 75). A traveler who changes hotels during a single vacation is counted at each check-in, whereas day-trippers and visitors staying in private short-term apartment rentals (such as Airbnb or Vrbo) are not included in this series.</p>
            <p>The modest 1.8% contraction in 2024 hotel check-ins reflected temporary calendar displacement associated with the 2024 Summer Olympic Games. Traditional cultural leisure travelers postponed visits during the peak summer setup period, before demand rebounded sharply during autumn 2024 and throughout 2025.</p>

            <h2 id="how-many-nights-do-tourists-spend-in-paris">How many nights do tourists spend in Paris?</h2>
            <p>Tourists spent <strong>41.92 million nights</strong> in Paris hotels during 2025, an <strong>8.7%</strong> increase compared to 38.55 million in 2024. International visitors accounted for 28.48 million nights, or 67.9% of the total.</p>

            <div class="bpa-chart" id="chart-paris-nights" role="figure" aria-labelledby="chart-paris-nights-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-paris-nights-t">Hotel nights in Paris, 2019 to 2025</div>
                <div class="bpa-chart-sub">Total nights spent at commercial hotels, millions</div>
              </div>
              <div class="bpa-legend">
                <span class="bpa-leg"><i style="background:#1e3a5f"></i>International</span>
                <span class="bpa-leg"><i style="background:#dfa732"></i>Domestic (France)</span>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:60.15%;background:#1e3a5f" title="2019 international: 25.21 million"></span>
                    <span class="bpa-seg" style="width:30.55%;background:#dfa732" title="2019 domestic: 12.81 million"></span>
                    <b class="bpa-val">38.02M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:59.19%;background:#1e3a5f" title="2022 international: 24.81 million"></span>
                    <span class="bpa-seg" style="width:30.66%;background:#dfa732" title="2022 domestic: 12.85 million"></span>
                    <b class="bpa-val">37.66M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:63.90%;background:#1e3a5f" title="2023 international: 26.78 million"></span>
                    <span class="bpa-seg" style="width:30.66%;background:#dfa732" title="2023 domestic: 12.85 million"></span>
                    <b class="bpa-val">39.64M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:62.28%;background:#1e3a5f" title="2024 international: 26.11 million"></span>
                    <span class="bpa-seg" style="width:29.69%;background:#dfa732" title="2024 domestic: 12.45 million"></span>
                    <b class="bpa-val">38.55M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2025</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:67.95%;background:#1e3a5f" title="2025 international: 28.48 million"></span>
                    <span class="bpa-seg" style="width:32.05%;background:#dfa732" title="2025 domestic: 13.44 million"></span>
                    <b class="bpa-val">41.92M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.insee.fr/en/statistiques/serie/010598705" rel="noopener" target="_blank">INSEE, Series 010598705, 010598706, 010598707</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Hotel nights in Paris (INSEE, d&eacute;partement 75)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Total Nights</th>
                      <th>International</th>
                      <th>Domestic</th>
                      <th>International Share</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>38,021,600</td>
                      <td>25,213,900</td>
                      <td>12,807,700</td>
                      <td>66.3%</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>37,662,700</td>
                      <td>24,811,600</td>
                      <td>12,851,100</td>
                      <td>65.9%</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>39,638,100</td>
                      <td>26,783,800</td>
                      <td>12,854,300</td>
                      <td>67.6%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>38,552,800</td>
                      <td>26,105,500</td>
                      <td>12,447,300</td>
                      <td>67.7%</td>
                    </tr>
                    <tr>
                      <td>2025</td>
                      <td>41,918,000</td>
                      <td>28,482,600</td>
                      <td>13,435,400</td>
                      <td>67.9%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Foreign tourists generate more than two-thirds of all overnight volume in Paris hotels. Domestic travelers (French residents originating outside Paris) generate the remaining 32.1% of nights, averaging 13.44 million room nights in 2025.</p>
            <p>Across the entire Paris &Icirc;le-de-France region, total accommodation volume is substantially higher: regional hotels generated 68.0 million nights in 2024, while registered short-term apartment rentals contributed an additional 14.7 million nights.</p>

            <h2 id="how-long-do-visitors-stay-in-paris">How long do visitors stay in Paris?</h2>
            <p>The average hotel guest stayed <strong>2.27 nights</strong> in Paris in 2025. International visitors stayed <strong>2.58 nights</strong> on average, compared to <strong>1.80 nights</strong> for French domestic travelers.</p>

            <div class="bpa-chart" id="chart-paris-stay" role="figure" aria-labelledby="chart-paris-stay-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-paris-stay-t">Average length of stay in Paris hotels</div>
                <div class="bpa-chart-sub">Nights per guest by visitor origin, 2019 to 2025</div>
              </div>
              <div class="bpa-legend">
                <span class="bpa-leg"><i style="background:#1e3a5f"></i>International guests</span>
                <span class="bpa-leg"><i style="background:#dfa732"></i>Domestic guests</span>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:85.0%;background:#1e3a5f" title="2019 international: 2.55 nights"></span>
                      <b class="bpa-val">2.55</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:59.7%;background:#dfa732" title="2019 domestic: 1.79 nights"></span>
                      <b class="bpa-val">1.79</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:89.3%;background:#1e3a5f" title="2022 international: 2.68 nights"></span>
                      <b class="bpa-val">2.68</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:65.0%;background:#dfa732" title="2022 domestic: 1.95 nights"></span>
                      <b class="bpa-val">1.95</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:87.0%;background:#1e3a5f" title="2023 international: 2.61 nights"></span>
                      <b class="bpa-val">2.61</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:64.0%;background:#dfa732" title="2023 domestic: 1.92 nights"></span>
                      <b class="bpa-val">1.92</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:86.3%;background:#1e3a5f" title="2024 international: 2.59 nights"></span>
                      <b class="bpa-val">2.59</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:63.0%;background:#dfa732" title="2024 domestic: 1.89 nights"></span>
                      <b class="bpa-val">1.89</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2025</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:86.0%;background:#1e3a5f" title="2025 international: 2.58 nights"></span>
                      <b class="bpa-val">2.58</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:60.0%;background:#dfa732" title="2025 domestic: 1.80 nights"></span>
                      <b class="bpa-val">1.80</b>
                    </span>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: Computed from INSEE hotel survey tables (Series 010598705 and 010598702)</div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Average duration of stay in Paris hotels (nights per guest)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>All Guests</th>
                      <th>International</th>
                      <th>Domestic</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>2.23</td>
                      <td>2.55</td>
                      <td>1.79</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>2.37</td>
                      <td>2.68</td>
                      <td>1.95</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>2.34</td>
                      <td>2.61</td>
                      <td>1.92</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>2.31</td>
                      <td>2.59</td>
                      <td>1.89</td>
                    </tr>
                    <tr>
                      <td>2025</td>
                      <td>2.27</td>
                      <td>2.58</td>
                      <td>1.80</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>International guests stay roughly 43% longer per hotel check-in than domestic travelers (2.58 nights versus 1.80 nights in 2025). Domestic stays are heavily weighted by single-night business trips and weekend breaks from regional cities connected by high-speed TGV rail.</p>
            <p>Long-haul overseas travelers (particularly visitors from the United States, Canada, Australia, and Asia) typically stay between 4 and 6 nights in the Paris region, frequently combining hotel nights in central Paris with excursions to Versailles, Disneyland Paris, or the Champagne region.</p>

            <h2 id="when-do-most-tourists-visit-paris">When do most tourists visit Paris?</h2>
            <p>The busiest month in Paris hotels in 2025 was <strong>July</strong> with 3.87 million nights, while the quietest month was <strong>February</strong> with 2.72 million nights. <strong>October</strong> was the second busiest month with 3.77 million nights.</p>

            <div class="bpa-chart" id="chart-paris-months" role="figure" aria-labelledby="chart-paris-months-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-paris-months-t">Hotel nights in Paris by month, 2025</div>
                <div class="bpa-chart-sub">Monthly nights at commercial hotels (d&eacute;partement 75), millions</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">Jan</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:75.37%;background:#1e3a5f" title="Jan nights: 2.92 million"></span>
                    <b class="bpa-val">2.92M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Feb</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:70.12%;background:#1e3a5f" title="Feb nights: 2.72 million"></span>
                    <b class="bpa-val">2.72M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Mar</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:86.20%;background:#1e3a5f" title="Mar nights: 3.34 million"></span>
                    <b class="bpa-val">3.34M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Apr</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:96.25%;background:#1e3a5f" title="Apr nights: 3.73 million"></span>
                    <b class="bpa-val">3.73M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">May</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:97.15%;background:#1e3a5f" title="May nights: 3.76 million"></span>
                    <b class="bpa-val">3.76M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Jun</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:95.65%;background:#1e3a5f" title="Jun nights: 3.71 million"></span>
                    <b class="bpa-val">3.71M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Jul</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="Jul nights: 3.87 million"></span>
                    <b class="bpa-val">3.87M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Aug</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:94.13%;background:#1e3a5f" title="Aug nights: 3.65 million"></span>
                    <b class="bpa-val">3.65M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Sep</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:91.26%;background:#1e3a5f" title="Sep nights: 3.54 million"></span>
                    <b class="bpa-val">3.54M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Oct</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:97.40%;background:#1e3a5f" title="Oct nights: 3.77 million"></span>
                    <b class="bpa-val">3.77M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Nov</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:85.18%;background:#1e3a5f" title="Nov nights: 3.30 million"></span>
                    <b class="bpa-val">3.30M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Dec</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:93.40%;background:#1e3a5f" title="Dec nights: 3.62 million"></span>
                    <b class="bpa-val">3.62M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.insee.fr/en/statistiques/serie/010598705" rel="noopener" target="_blank">INSEE, Series 010598705 (Monthly hotel nights, Paris 75)</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Monthly hotel nights in Paris (INSEE figures, thousands)</caption>
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>2025 Nights</th>
                      <th>2024 Nights</th>
                      <th>Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>January</td>
                      <td>2,919,800</td>
                      <td>2,710,600</td>
                      <td>+7.7%</td>
                    </tr>
                    <tr>
                      <td>February</td>
                      <td>2,716,200</td>
                      <td>2,648,400</td>
                      <td>+2.6%</td>
                    </tr>
                    <tr>
                      <td>March</td>
                      <td>3,339,300</td>
                      <td>3,291,300</td>
                      <td>+1.5%</td>
                    </tr>
                    <tr>
                      <td>April</td>
                      <td>3,728,500</td>
                      <td>3,251,600</td>
                      <td>+14.7%</td>
                    </tr>
                    <tr>
                      <td>May</td>
                      <td>3,763,300</td>
                      <td>3,502,300</td>
                      <td>+7.5%</td>
                    </tr>
                    <tr>
                      <td>June</td>
                      <td>3,705,100</td>
                      <td>3,259,700</td>
                      <td>+13.7%</td>
                    </tr>
                    <tr>
                      <td>July</td>
                      <td>3,873,800</td>
                      <td>3,052,400</td>
                      <td>+26.9%</td>
                    </tr>
                    <tr>
                      <td>August</td>
                      <td>3,646,500</td>
                      <td>3,186,400</td>
                      <td>+14.4%</td>
                    </tr>
                    <tr>
                      <td>September</td>
                      <td>3,535,100</td>
                      <td>3,370,800</td>
                      <td>+4.9%</td>
                    </tr>
                    <tr>
                      <td>October</td>
                      <td>3,772,900</td>
                      <td>3,638,200</td>
                      <td>+3.7%</td>
                    </tr>
                    <tr>
                      <td>November</td>
                      <td>3,299,800</td>
                      <td>3,189,500</td>
                      <td>+3.5%</td>
                    </tr>
                    <tr>
                      <td>December</td>
                      <td>3,618,000</td>
                      <td>3,451,800</td>
                      <td>+4.8%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Paris maintains balanced year-round demand. Even in February, the quietest month on the calendar, Paris hotels still hosted 2.72 million nights. Tourism activity expands through two distinct surges: the spring peak (April to June) driven by conventions, business conferences, and cultural breaks, and the autumn peak (September to October) driven by major international trade fairs and Fashion Weeks.</p>
            <p>December experiences a significant seasonal rebound (3.62 million nights in 2025), propelled by festive holiday illuminations, Christmas markets, and New Year celebrations across the Champs-&Eacute;lys&eacute;es and the riverbanks.</p>

            <h2 id="where-do-visitors-to-paris-come-from">Where do visitors to Paris come from?</h2>
            <p>The <strong>United States</strong> is the largest foreign source market for Paris with <strong>2.70 million visitors</strong> in 2024, followed by the <strong>United Kingdom</strong> (2.60 million), <strong>Italy</strong> (1.60 million), and <strong>Germany</strong> (1.50 million).</p>

            <div class="bpa-chart" id="chart-paris-countries" role="figure" aria-labelledby="chart-paris-countries-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-paris-countries-t">Top international source markets for Paris Region, 2024</div>
                <div class="bpa-chart-sub">International tourist arrivals across Paris &Icirc;le-de-France, millions</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">United States</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="United States: 2.70 million"></span>
                    <b class="bpa-val">2.70M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">United Kingdom</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:96.3%;background:#1e3a5f" title="United Kingdom: 2.60 million"></span>
                    <b class="bpa-val">2.60M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Italy</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:59.3%;background:#1e3a5f" title="Italy: 1.60 million"></span>
                    <b class="bpa-val">1.60M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Germany</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:55.6%;background:#1e3a5f" title="Germany: 1.50 million"></span>
                    <b class="bpa-val">1.50M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Spain</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:51.9%;background:#1e3a5f" title="Spain: 1.40 million"></span>
                    <b class="bpa-val">1.40M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Belgium</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:40.7%;background:#1e3a5f" title="Belgium: 1.10 million"></span>
                    <b class="bpa-val">1.10M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Netherlands</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:33.3%;background:#1e3a5f" title="Netherlands: 0.90 million"></span>
                    <b class="bpa-val">0.90M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Switzerland</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:29.6%;background:#1e3a5f" title="Switzerland: 0.80 million"></span>
                    <b class="bpa-val">0.80M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://pro.visitparisregion.com/" rel="noopener" target="_blank">Choose Paris Region / CRT Paris &Icirc;le-de-France, Bilan annuel</a> (regional figures)</div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>International tourists in Paris &Icirc;le-de-France by country of origin (Choose Paris Region)</caption>
                  <thead>
                    <tr>
                      <th>Country</th>
                      <th>2024 Tourists</th>
                      <th>Share of International Visitors</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>United States</td>
                      <td>2,700,000</td>
                      <td>11.9%</td>
                    </tr>
                    <tr>
                      <td>United Kingdom</td>
                      <td>2,600,000</td>
                      <td>11.5%</td>
                    </tr>
                    <tr>
                      <td>Italy</td>
                      <td>1,600,000</td>
                      <td>7.1%</td>
                    </tr>
                    <tr>
                      <td>Germany</td>
                      <td>1,500,000</td>
                      <td>6.6%</td>
                    </tr>
                    <tr>
                      <td>Spain</td>
                      <td>1,400,000</td>
                      <td>6.2%</td>
                    </tr>
                    <tr>
                      <td>Belgium</td>
                      <td>1,100,000</td>
                      <td>4.9%</td>
                    </tr>
                    <tr>
                      <td>Netherlands</td>
                      <td>900,000</td>
                      <td>4.0%</td>
                    </tr>
                    <tr>
                      <td>Switzerland</td>
                      <td>800,000</td>
                      <td>3.5%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Country of origin statistics are compiled at the Paris &Icirc;le-de-France regional level by Choose Paris Region rather than for the city boundaries alone. The United States and the United Kingdom together generate 23.5% of all foreign tourist arrivals in the region.</p>
            <p>American visitors represent the largest economic contributor among all overseas markets, accounting for roughly 20% of foreign tourism expenditure. Travelers from European neighboring markets (the UK, Italy, Germany, Spain, Belgium, and the Netherlands) provide consistent visitor volume supported by Eurostar and high-speed rail links.</p>

            <h2 id="how-much-do-tourists-spend-in-paris">How much do tourists spend in Paris?</h2>
            <p>Tourists spent <strong>23.4 billion euros</strong> in the Paris &Icirc;le-de-France region in 2024, an increase of <strong>7.8%</strong> compared to 21.7 billion euros in 2023 and 6.8% higher than the 2019 pre-pandemic level (21.9 billion euros).</p>

            <div class="bpa-chart" id="chart-paris-spending" role="figure" aria-labelledby="chart-paris-spending-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-paris-spending-t">Tourism spending in Paris &Icirc;le-de-France, 2019 to 2024</div>
                <div class="bpa-chart-sub">Annual tourism spending at current prices, billion euros</div>
              </div>
              <div class="bpa-legend">
                <span class="bpa-leg"><i style="background:#1e3a5f"></i>International spend</span>
                <span class="bpa-leg"><i style="background:#dfa732"></i>Domestic spend</span>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:61.64%;background:#1e3a5f" title="2019 international: 13.5 billion euros"></span>
                    <span class="bpa-seg" style="width:38.36%;background:#dfa732" title="2019 domestic: 8.4 billion euros"></span>
                    <b class="bpa-val">&euro;21.9B</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:61.73%;background:#1e3a5f" title="2022 international: 12.1 billion euros"></span>
                    <span class="bpa-seg" style="width:38.27%;background:#dfa732" title="2022 domestic: 7.5 billion euros"></span>
                    <b class="bpa-val">&euro;19.6B</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:63.59%;background:#1e3a5f" title="2023 international: 13.8 billion euros"></span>
                    <span class="bpa-seg" style="width:36.41%;background:#dfa732" title="2023 domestic: 7.9 billion euros"></span>
                    <b class="bpa-val">&euro;21.7B</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:63.68%;background:#1e3a5f" title="2024 international: 14.9 billion euros"></span>
                    <span class="bpa-seg" style="width:36.32%;background:#dfa732" title="2024 domestic: 8.5 billion euros"></span>
                    <b class="bpa-val">&euro;23.4B</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://pro.visitparisregion.com/" rel="noopener" target="_blank">Choose Paris Region &amp; CCI Paris &Icirc;le-de-France, Bilan &eacute;conomique</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Tourism expenditure in Paris &Icirc;le-de-France (billion euros, current prices)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Total Spending</th>
                      <th>International</th>
                      <th>Domestic</th>
                      <th>Annual Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>&euro;21.9B</td>
                      <td>&euro;13.5B</td>
                      <td>&euro;8.4B</td>
                      <td>Baseline</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>&euro;19.6B</td>
                      <td>&euro;12.1B</td>
                      <td>&euro;7.5B</td>
                      <td>-10.5% vs 2019</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>&euro;21.7B</td>
                      <td>&euro;13.8B</td>
                      <td>&euro;7.9B</td>
                      <td>+10.7%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>&euro;23.4B</td>
                      <td>&euro;14.9B</td>
                      <td>&euro;8.5B</td>
                      <td>+7.8%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Spending is published by regional tourism authorities for Paris &Icirc;le-de-France rather than the municipality in isolation. International tourists generated 63.7% of all visitor spending in 2024 (14.9 billion euros), despite making up 46.4% of total visitors, averaging approximately 659 euros per trip.</p>
            <p>Choose Paris Region notes that 5.6 million high-contribution visitors (primarily luxury travelers from the United States, China, and the Gulf States) generated 6.9 billion euros in 2024, averaging more than 1,400 euros in spending per person.</p>

            <h2 id="how-busy-are-paris-airports">How busy are Paris airports?</h2>
            <p>Paris airports (Paris-Charles de Gaulle and Paris-Orly) handled <strong>103.41 million passengers</strong> in 2024, rising <strong>3.7%</strong> compared to 99.70 million in 2023 and reaching 95.8% of the 2019 record (108.00 million).</p>

            <div class="bpa-chart" id="chart-paris-airports" role="figure" aria-labelledby="chart-paris-airports-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-paris-airports-t">Passenger traffic at Paris airports, 2019 to 2024</div>
                <div class="bpa-chart-sub">Annual terminal passengers (Groupe ADP), millions</div>
              </div>
              <div class="bpa-legend">
                <span class="bpa-leg"><i style="background:#1e3a5f"></i>Charles de Gaulle (CDG)</span>
                <span class="bpa-leg"><i style="background:#10b981"></i>Orly (ORY)</span>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:70.51%;background:#1e3a5f" title="2019 CDG: 76.15 million"></span>
                    <span class="bpa-seg" style="width:29.49%;background:#10b981" title="2019 Orly: 31.85 million"></span>
                    <b class="bpa-val">108.00M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2020</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:20.61%;background:#1e3a5f" title="2020 CDG: 22.26 million"></span>
                    <span class="bpa-seg" style="width:10.06%;background:#10b981" title="2020 Orly: 10.86 million"></span>
                    <b class="bpa-val">33.12M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2021</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:24.26%;background:#1e3a5f" title="2021 CDG: 26.20 million"></span>
                    <span class="bpa-seg" style="width:14.55%;background:#10b981" title="2021 Orly: 15.71 million"></span>
                    <b class="bpa-val">41.91M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:53.21%;background:#1e3a5f" title="2022 CDG: 57.47 million"></span>
                    <span class="bpa-seg" style="width:27.06%;background:#10b981" title="2022 Orly: 29.23 million"></span>
                    <b class="bpa-val">86.70M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:62.43%;background:#1e3a5f" title="2023 CDG: 67.42 million"></span>
                    <span class="bpa-seg" style="width:29.89%;background:#10b981" title="2023 Orly: 32.28 million"></span>
                    <b class="bpa-val">99.70M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:65.08%;background:#1e3a5f" title="2024 CDG: 70.29 million"></span>
                    <span class="bpa-seg" style="width:30.67%;background:#10b981" title="2024 Orly: 33.12 million"></span>
                    <b class="bpa-val">103.41M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.parisaeroport.fr/" rel="noopener" target="_blank">Groupe ADP, Annual Traffic Results</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Paris airport passenger traffic (Groupe ADP)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Total Paris Traffic</th>
                      <th>Charles de Gaulle (CDG)</th>
                      <th>Orly (ORY)</th>
                      <th>Change vs Previous Year</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>108,000,000</td>
                      <td>76,150,000</td>
                      <td>31,850,000</td>
                      <td>Baseline</td>
                    </tr>
                    <tr>
                      <td>2020</td>
                      <td>33,120,000</td>
                      <td>22,260,000</td>
                      <td>10,860,000</td>
                      <td>-69.3%</td>
                    </tr>
                    <tr>
                      <td>2021</td>
                      <td>41,910,000</td>
                      <td>26,200,000</td>
                      <td>15,710,000</td>
                      <td>+26.5%</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>86,700,000</td>
                      <td>57,470,000</td>
                      <td>29,230,000</td>
                      <td>+106.9%</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>99,700,000</td>
                      <td>67,420,000</td>
                      <td>32,280,000</td>
                      <td>+15.0%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>103,410,000</td>
                      <td>70,290,000</td>
                      <td>33,120,000</td>
                      <td>+3.7%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Paris-Charles de Gaulle serves as the primary intercontinental hub for Air France and the SkyTeam alliance, processing 68.0% of Paris aviation passengers in 2024. Paris-Orly focuses primarily on domestic French, Southern European, and North African routes.</p>
            <p>In 2024, traffic at Paris-Orly reached 33.12 million passengers, surpassing its 2019 pre-pandemic record by 4.0% (104.0% of 2019 volume). Charles de Gaulle handled 70.29 million passengers, recovering to 92.3% of its 2019 peak as long-haul flights from Asia continued to rebuild.</p>

            <h2 id="what-are-the-top-destinations-to-visit-in-paris">What are the top destinations to visit in Paris?</h2>
            <p>Paris hosts some of the world's most visited cultural monuments and museums. Five of the city's top landmarks include:</p>
            <ul role="list">
              <li><strong>The Louvre Museum</strong>: Welcoming over 8.8 million visitors annually, the world's largest art museum houses masterworks including the <em>Mona Lisa</em>, the <em>Winged Victory of Samothrace</em>, and the <em>Venus de Milo</em>.</li>
              <li><strong>The Eiffel Tower</strong>: Designed by Gustave Eiffel for the 1889 Exposition Universelle, the 330-metre landmark welcomes over 6.3 million ticketed visitors each year.</li>
              <li><strong>The Banks of the Seine</strong>: Inscribed as a UNESCO World Heritage site in 1991, the river corridor between Pont de Sully and Pont d'I&eacute;na links the city's greatest monuments. Taking an undercover-tested <a href="/seine-river-cruises-paris">Seine sightseeing cruise</a> or an evening <a href="/dinner-cruises-paris">Paris dinner cruise</a> provides unobstructed views of Notre-Dame Cathedral, the Conciergerie, and the illuminated Eiffel Tower.</li>
              <li><strong>Mus&eacute;e d'Orsay</strong>: Situated inside a converted Beaux-Arts railway terminal on the Left Bank, the museum displays the world's largest collection of Impressionist and post-Impressionist masterpieces, welcoming over 3.8 million visitors annually.</li>
              <li><strong>Palace of Versailles</strong>: Located 20 kilometres southwest of central Paris, the former royal residence of the French monarchy attracts more than 8 million visitors annually to its Grand Apartments, Hall of Mirrors, and formal gardens.</li>
            </ul>

            <h2 id="sources-and-methodology">Sources and methodology</h2>
            <ul role="list">
              <li><strong>Hotel Arrivals, Nights and Length of Stay</strong>: Sourced directly from the French National Institute of Statistics and Economic Studies (<a href="https://www.insee.fr/en/statistiques/serie/010598702" rel="noopener" target="_blank">INSEE</a>), Enqu&ecirc;te de fr&eacute;quentation h&ocirc;teli&egrave;re. Monthly series IDs: 010598702 (Total arrivals), 010598703 (Non-resident arrivals), 010598704 (Resident arrivals), 010598705 (Total nights), 010598706 (Non-resident nights), 010598707 (Resident nights). Scope: Registered commercial hotels in the City of Paris (d&eacute;partement 75). Data accessed November 2026.</li>
              <li><strong>Regional Visitors, Country Origins and Tourism Spend</strong>: Sourced from <a href="https://pro.visitparisregion.com/" rel="noopener" target="_blank">Choose Paris Region</a> (Comit&eacute; R&eacute;gional du Tourisme Paris &Icirc;le-de-France) and the Paris &Icirc;le-de-France Chamber of Commerce and Industry (CCI Paris &Icirc;le-de-France) annual tourism surveys (Bilan de l'activit&eacute; touristique 2023, 2024). Geographic scope covers the eight departments of &Icirc;le-de-France.</li>
              <li><strong>Airport Passenger Volumes</strong>: Sourced from <a href="https://www.parisaeroport.fr/" rel="noopener" target="_blank">Groupe ADP</a> monthly and full-year traffic releases for Paris-Charles de Gaulle (CDG) and Paris-Orly (ORY) airports (2019 to 2024).</li>
              <li><strong>Definitions</strong>: An arrival represents a single check-in by a guest at a registered hotel. A visitor who relocates between two Parisian hotels during one trip is counted twice. Day-trippers, business travelers without overnight lodging, and stays in private residential rentals are excluded from the INSEE hotel series. Origin and expenditure statistics are reported at the Paris &Icirc;le-de-France regional level because city-only origin breakdowns are not isolated in official releases.</li>
            </ul>
            <div class="bpa-cite">
              <strong>Using these statistics?</strong> You are welcome to quote the figures and charts on this page. Please credit and link to <a href="/paris-tourism-statistics">The Cruise Detective, Paris Tourism Statistics</a>.
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</main>

{COMMON_FOOTER_HTML}
{COMMON_SCRIPTS}
</body>
</html>
"""
    return html

def get_amsterdam_html():
    canonical = "https://www.thecruisedetective.com/amsterdam-tourism-statistics"
    title = "Amsterdam Tourism Statistics 2026: How Many Tourists Visit?"
    meta_desc = "Amsterdam recorded 9.55 million hotel guests and 22.20 million nights in 2025. Official CBS data on visitors, busiest months, source countries and spending."
    og_image = "https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/656b5237222689efacce475b_best-amsterdam-canal-cruises-featured-image.webp"

    assert len(title) <= 60, f"Title too long: {len(title)}"
    assert 140 <= len(meta_desc) <= 160, f"Meta description invalid length: {len(meta_desc)}"

    json_ld = """{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Amsterdam Tourism Statistics 2026: How Many Tourists Visit?",
  "description": "Amsterdam recorded 9.55 million hotel guests and 22.20 million nights in 2025. Official CBS data on visitors, busiest months, source countries and spending.",
  "datePublished": "2026-11-13",
  "dateModified": "2026-11-13",
  "inLanguage": "en",
  "mainEntityOfPage": "https://www.thecruisedetective.com/amsterdam-tourism-statistics",
  "author": {
    "@type": "Person",
    "name": "Adam Dimitrov",
    "url": "https://www.thecruisedetective.com/about"
  },
  "publisher": {
    "@type": "Organization",
    "name": "The Cruise Detective",
    "url": "https://www.thecruisedetective.com/"
  },
  "citation": [
    "https://opendata.cbs.nl/statline/#/CBS/en/dataset/82061NED",
    "https://www.schiphol.nl/en/annual-reports/",
    "https://onderzoek.amsterdam.nl/"
  ]
}"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<meta content="{meta_desc}" name="description"/>
<meta content="{title}" property="og:title"/>
<meta content="{meta_desc}" property="og:description"/>
<meta content="{og_image}" property="og:image"/>
<meta content="{canonical}" property="og:url"/>
<meta content="article" property="og:type"/>
<meta content="{title}" name="twitter:title"/>
<meta content="{meta_desc}" name="twitter:description"/>
<meta content="{og_image}" name="twitter:image"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<meta content="google-site-verification=jPygzQl3dLYHsZI7XMPOqvcxGUVZtEr6WiuGN_O2xjo" name="google-site-verification"/>

<link href="/favicon.ico" rel="icon" type="image/x-icon"/>
<link href="/favicon.ico" rel="shortcut icon" type="image/x-icon"/>
<link href="/assets/apple-touch-icon.png" rel="apple-touch-icon"/>
<link href="{canonical}" rel="canonical"/>
<link href="{canonical}" hreflang="en" rel="alternate"/>
<link href="{canonical}" hreflang="x-default" rel="alternate"/>

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet"/>

<!-- Core Stylesheets -->
<link href="/css/thecruisedetective-com.webflow.shared.3cc389acf.min.css" rel="stylesheet" type="text/css"/>

<!-- Analytics -->
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('set', 'developer_id.dZGVlNj', true);
gtag('set', 'developer_id.dYWYxNW', true);
gtag('js', new Date());
gtag('config', 'G-RN34XFKPQ6');

!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];}}(window,document);
fbq('init', '1355732169631751');
fbq('track', 'PageView');
</script>

<script type="application/ld+json">
{json_ld}
</script>

{COMMON_HEAD_CSS}
</head>
<body id="top">
{COMMON_HEADER_HTML}

<main id="main" role="main">
<div class="ltt-hero-wrap">
  <div class="ltt-clean-card">
    <div class="ltt-top-bar">
      <nav aria-label="Breadcrumb" class="ltt-breadcrumbs">
        <a href="/">Home</a>
        <span class="ltt-bc-sep">&rsaquo;</span>
        <span class="ltt-bc-current">Amsterdam Tourism Statistics (2026)</span>
      </nav>
      <span class="ltt-hero-kicker-badge">Official CBS Data &middot; 2019 to 2025</span>
    </div>
    <h1 class="ltt-editorial-h1">
      Amsterdam Tourism Statistics 2026 <span class="ltt-h1-muted">(How Many Tourists Visit?)</span>
    </h1>
    <div class="ltt-trust-bar">
      <div class="ltt-author-cluster">
        <div class="ltt-author-avatar-wrap">
          <img alt="Adam Dimitrov" class="ltt-author-avatar" height="42" loading="eager" src="/assets/cdn/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp" width="42"/>
        </div>
        <div class="ltt-author-meta">
          <div class="ltt-author-line">
            By <a href="/about" target="_blank">Adam Dimitrov</a>, Owner &amp; Head Cruise Detective
          </div>
          <div class="ltt-author-role">Compiled from Official CBS StatLine Data &bull; 6 Charts with Data Tables &bull; <a href="#sources-and-methodology">Methodology</a></div>
        </div>
      </div>
      <div class="ltt-trust-pills">
        <span class="ltt-trust-pill paragraph-26"><strong>Last updated</strong>: Nov 13, 2026</span>
      </div>
    </div>
    <div class="ltt-lead-copy">
      <p>Amsterdam recorded <strong>9.55 million hotel guests</strong> and <strong>22.20 million hotel nights</strong> in 2025, according to official figures from Statistics Netherlands (CBS). International visitors generated 80.7% of all hotel guests and 84.7% of overnight stays.</p>
      <p>This report compiles official <strong>Amsterdam tourism statistics</strong> from CBS StatLine, the City of Amsterdam Research and Statistics bureau (OIS), and Royal Schiphol Group: annual arrivals, overnight stays, length of stay, monthly seasonality, leading source markets, tourist tax receipts, and airport passenger volumes. Every chart is paired with a verifiable data table.</p>
    </div>
  </div>
</div>

<div class="blog-section">
  <div class="container-26">
    <div class="blog-grid-2">
      <div class="content-left">
        <div class="stick-wrapper">
          <div class="title-small-3" style="font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #f1f5f9;">Table of Contents</div>
          <div class="toc" id="toc">
            <a class="tocitem" href="#key-amsterdam-tourism-statistics-2025">Key Amsterdam tourism statistics (2025)</a>
            <a class="tocitem" href="#how-many-tourists-visit-amsterdam-each-year">How many tourists visit Amsterdam each year?</a>
            <a class="tocitem" href="#how-many-nights-do-tourists-spend-in-amsterdam">How many nights do tourists spend in Amsterdam?</a>
            <a class="tocitem" href="#how-long-do-visitors-stay-in-amsterdam">How long do visitors stay in Amsterdam?</a>
            <a class="tocitem" href="#when-do-most-tourists-visit-amsterdam">When do most tourists visit Amsterdam?</a>
            <a class="tocitem" href="#where-do-visitors-to-amsterdam-come-from">Where do visitors to Amsterdam come from?</a>
            <a class="tocitem" href="#how-much-do-tourists-spend-in-amsterdam">How much do tourists spend in Amsterdam?</a>
            <a class="tocitem" href="#how-busy-is-amsterdam-airport-schiphol">How busy is Amsterdam Airport Schiphol?</a>
            <a class="tocitem" href="#what-are-the-top-destinations-to-visit-in-amsterdam">What are the top destinations to visit in Amsterdam?</a>
            <a class="tocitem" href="#sources-and-methodology">Sources and methodology</a>
          </div>
        </div>
      </div>
      <div class="content-right_blog" id="content">
        <div class="w-layout-blockcontainer container w-container">
          <div class="w-richtext">

            <h2 id="key-amsterdam-tourism-statistics-2025">Key Amsterdam tourism statistics (2025)</h2>
            <div class="bpa-tiles">
              <div class="bpa-tile">
                <div class="bpa-tile-num">9.55M</div>
                <div class="bpa-tile-lab">hotel guests in 2025, up 2.6% on 2024</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">22.20M</div>
                <div class="bpa-tile-lab">hotel nights in 2025, up 4.4%</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">84.7%</div>
                <div class="bpa-tile-lab">of nights generated by foreign visitors</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">2.33</div>
                <div class="bpa-tile-lab">nights is the average hotel stay</div>
              </div>
            </div>
            <ul role="list">
              <li>Amsterdam hotels (municipality GM0363) welcomed <strong>9,546,000 guests</strong> in 2025, a 2.6% increase compared to 2024 (9,305,000) and 3.7% above the 2019 baseline (9,209,000).</li>
              <li>Guests spent <strong>22,200,000 nights</strong> in Amsterdam hotels during 2025, a 4.4% increase over 2024 and 20.8% higher than the 18,375,000 nights registered in 2019.</li>
              <li>Foreign visitors accounted for <strong>80.7% of guests</strong> (7,701,000) and <strong>84.7% of hotel nights</strong> (18,811,000).</li>
              <li>The <strong>United States</strong> was the leading international source market in 2025 with 2.82 million nights (+14.0% vs 2024), closely followed by the <strong>United Kingdom</strong> with 2.77 million nights (+7.9%).</li>
              <li>The single busiest month for hotel stays in 2025 was <strong>August</strong> with 2.22 million nights, while <strong>February</strong> was the quietest with 1.48 million nights.</li>
              <li>Amsterdam Airport Schiphol handled <strong>66.8 million passengers</strong> in 2024, an 8.0% expansion over 2023.</li>
              <li>The municipality of Amsterdam collected approximately <strong>242.5 million euros</strong> in tourist tax revenues in 2024 following an increase in the tax rate to 12.5%.</li>
            </ul>

            <h2 id="how-many-tourists-visit-amsterdam-each-year">How many tourists visit Amsterdam each year?</h2>
            <p>Amsterdam hotels welcomed <strong>9.55 million guests</strong> in 2025, an increase of <strong>2.6%</strong> from 9.31 million in 2024. Total hotel guest numbers have exceeded their 2019 pre-pandemic volume (9.21 million) for two consecutive years.</p>

            <div class="bpa-chart" id="chart-ams-guests" role="figure" aria-labelledby="chart-ams-guests-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-ams-guests-t">Hotel guests in Amsterdam, 2019 to 2025</div>
                <div class="bpa-chart-sub">Registered guests at hotels and boarding houses (Municipality GM0363), millions</div>
              </div>
              <div class="bpa-legend">
                <span class="bpa-leg"><i style="background:#1e3a5f"></i>International</span>
                <span class="bpa-leg"><i style="background:#dfa732"></i>Domestic (Netherlands)</span>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:79.32%;background:#1e3a5f" title="2019 international: 7.57 million"></span>
                    <span class="bpa-seg" style="width:17.15%;background:#dfa732" title="2019 domestic: 1.64 million"></span>
                    <b class="bpa-val">9.21M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2020</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:21.87%;background:#1e3a5f" title="2020 international: 2.09 million"></span>
                    <span class="bpa-seg" style="width:9.12%;background:#dfa732" title="2020 domestic: 0.87 million"></span>
                    <b class="bpa-val">2.96M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2021</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:18.27%;background:#1e3a5f" title="2021 international: 1.74 million"></span>
                    <span class="bpa-seg" style="width:11.97%;background:#dfa732" title="2021 domestic: 1.14 million"></span>
                    <b class="bpa-val">2.89M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:59.07%;background:#1e3a5f" title="2022 international: 5.64 million"></span>
                    <span class="bpa-seg" style="width:18.58%;background:#dfa732" title="2022 domestic: 1.77 million"></span>
                    <b class="bpa-val">7.41M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:72.96%;background:#1e3a5f" title="2023 international: 6.97 million"></span>
                    <span class="bpa-seg" style="width:19.93%;background:#dfa732" title="2023 domestic: 1.90 million"></span>
                    <b class="bpa-val">8.87M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:77.17%;background:#1e3a5f" title="2024 international: 7.37 million"></span>
                    <span class="bpa-seg" style="width:20.30%;background:#dfa732" title="2024 domestic: 1.94 million"></span>
                    <b class="bpa-val">9.31M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2025</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:80.67%;background:#1e3a5f" title="2025 international: 7.70 million"></span>
                    <span class="bpa-seg" style="width:19.33%;background:#dfa732" title="2025 domestic: 1.85 million"></span>
                    <b class="bpa-val">9.55M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://opendata.cbs.nl/statline/#/CBS/en/dataset/82061NED" rel="noopener" target="_blank">Statistics Netherlands (CBS), StatLine Table 82061NED</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Hotel guests in Amsterdam municipality (CBS Table 82061NED)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Total Guests</th>
                      <th>International</th>
                      <th>Domestic</th>
                      <th>Change vs Previous Year</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>9,209,000</td>
                      <td>7,572,000</td>
                      <td>1,637,000</td>
                      <td>Baseline</td>
                    </tr>
                    <tr>
                      <td>2020</td>
                      <td>2,959,000</td>
                      <td>2,088,000</td>
                      <td>871,000</td>
                      <td>-67.9%</td>
                    </tr>
                    <tr>
                      <td>2021</td>
                      <td>2,887,000</td>
                      <td>1,744,000</td>
                      <td>1,143,000</td>
                      <td>-2.4%</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>7,413,000</td>
                      <td>5,639,000</td>
                      <td>1,774,000</td>
                      <td>+156.8%</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>8,868,000</td>
                      <td>6,965,000</td>
                      <td>1,903,000</td>
                      <td>+19.6%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>9,305,000</td>
                      <td>7,367,000</td>
                      <td>1,938,000</td>
                      <td>+4.9%</td>
                    </tr>
                    <tr>
                      <td>2025</td>
                      <td>9,546,000</td>
                      <td>7,701,000</td>
                      <td>1,845,000</td>
                      <td>+2.6%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>CBS tracks hotel guests across hotels, motels, boarding houses, and youth accommodation facilities with at least 5 bed spaces within the municipality of Amsterdam (GM0363). A traveler checking into multiple hotels during their stay is registered at each establishment.</p>
            <p>During the pandemic low of 2021, total guest numbers dropped to 2.89 million. By 2025, international guest volume reached 7.70 million, fully recovering from border restrictions and setting an all-time record for foreign visitation to Amsterdam.</p>

            <h2 id="how-many-nights-do-tourists-spend-in-amsterdam">How many nights do tourists spend in Amsterdam?</h2>
            <p>Guests spent <strong>22.20 million nights</strong> in Amsterdam hotels in 2025, an increase of <strong>4.4%</strong> from 21.26 million in 2024 and <strong>20.8%</strong> above the 2019 baseline (18.38 million). International guests accounted for 18.81 million nights (84.7%).</p>

            <div class="bpa-chart" id="chart-ams-nights" role="figure" aria-labelledby="chart-ams-nights-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-ams-nights-t">Hotel overnight stays in Amsterdam, 2019 to 2025</div>
                <div class="bpa-chart-sub">Nights spent at commercial hotels (Municipality GM0363), millions</div>
              </div>
              <div class="bpa-legend">
                <span class="bpa-leg"><i style="background:#1e3a5f"></i>International</span>
                <span class="bpa-leg"><i style="background:#dfa732"></i>Domestic (Netherlands)</span>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:69.77%;background:#1e3a5f" title="2019 international: 15.49 million"></span>
                    <span class="bpa-seg" style="width:13.00%;background:#dfa732" title="2019 domestic: 2.89 million"></span>
                    <b class="bpa-val">18.38M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2020</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:19.32%;background:#1e3a5f" title="2020 international: 4.29 million"></span>
                    <span class="bpa-seg" style="width:6.82%;background:#dfa732" title="2020 domestic: 1.51 million"></span>
                    <b class="bpa-val">5.80M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2021</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:17.33%;background:#1e3a5f" title="2021 international: 3.85 million"></span>
                    <span class="bpa-seg" style="width:8.68%;background:#dfa732" title="2021 domestic: 1.93 million"></span>
                    <b class="bpa-val">5.78M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:60.39%;background:#1e3a5f" title="2022 international: 13.41 million"></span>
                    <span class="bpa-seg" style="width:15.18%;background:#dfa732" title="2022 domestic: 3.37 million"></span>
                    <b class="bpa-val">16.78M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:75.40%;background:#1e3a5f" title="2023 international: 16.74 million"></span>
                    <span class="bpa-seg" style="width:16.42%;background:#dfa732" title="2023 domestic: 3.65 million"></span>
                    <b class="bpa-val">20.39M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:79.65%;background:#1e3a5f" title="2024 international: 17.68 million"></span>
                    <span class="bpa-seg" style="width:16.10%;background:#dfa732" title="2024 domestic: 3.57 million"></span>
                    <b class="bpa-val">21.26M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2025</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:84.73%;background:#1e3a5f" title="2025 international: 18.81 million"></span>
                    <span class="bpa-seg" style="width:15.27%;background:#dfa732" title="2025 domestic: 3.39 million"></span>
                    <b class="bpa-val">22.20M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://opendata.cbs.nl/statline/#/CBS/en/dataset/82061NED" rel="noopener" target="_blank">Statistics Netherlands (CBS), StatLine Table 82061NED</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Hotel nights in Amsterdam municipality (CBS Table 82061NED)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Total Nights</th>
                      <th>International</th>
                      <th>Domestic</th>
                      <th>International Share</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>18,375,000</td>
                      <td>15,489,000</td>
                      <td>2,886,000</td>
                      <td>84.3%</td>
                    </tr>
                    <tr>
                      <td>2020</td>
                      <td>5,802,000</td>
                      <td>4,288,000</td>
                      <td>1,513,000</td>
                      <td>73.9%</td>
                    </tr>
                    <tr>
                      <td>2021</td>
                      <td>5,775,000</td>
                      <td>3,848,000</td>
                      <td>1,926,000</td>
                      <td>66.6%</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>16,775,000</td>
                      <td>13,406,000</td>
                      <td>3,369,000</td>
                      <td>79.9%</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>20,385,000</td>
                      <td>16,739,000</td>
                      <td>3,646,000</td>
                      <td>82.1%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>21,258,000</td>
                      <td>17,683,000</td>
                      <td>3,574,000</td>
                      <td>83.2%</td>
                    </tr>
                    <tr>
                      <td>2025</td>
                      <td>22,200,000</td>
                      <td>18,811,000</td>
                      <td>3,389,000</td>
                      <td>84.7%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Total overnight stays have grown substantially faster than arrivals, reflecting a lengthening duration of stay among international visitors. International guests generated 84.7% of all hotel room nights in 2025 (18.81 million nights), cementing Amsterdam as one of the most internationally dominated city destinations in Europe.</p>
            <p>Dutch domestic travelers contributed 3.39 million nights in 2025 (15.3% of the municipal total), down slightly from 3.57 million nights in 2024 as higher room rates and hotel taxes led some regional domestic travelers to choose short-stay alternatives outside the A10 ring road.</p>

            <h2 id="how-long-do-visitors-stay-in-amsterdam">How long do visitors stay in Amsterdam?</h2>
            <p>The average hotel guest stayed <strong>2.33 nights</strong> in Amsterdam in 2025, up from 2.00 nights in 2019. International guests averaged <strong>2.44 nights</strong>, while domestic guests stayed <strong>1.84 nights</strong>.</p>

            <div class="bpa-chart" id="chart-ams-stay" role="figure" aria-labelledby="chart-ams-stay-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-ams-stay-t">Average length of stay in Amsterdam hotels</div>
                <div class="bpa-chart-sub">Nights per guest by visitor origin, 2019 to 2025</div>
              </div>
              <div class="bpa-legend">
                <span class="bpa-leg"><i style="background:#1e3a5f"></i>International guests</span>
                <span class="bpa-leg"><i style="background:#dfa732"></i>Domestic guests</span>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:82.0%;background:#1e3a5f" title="2019 international: 2.05 nights"></span>
                      <b class="bpa-val">2.05</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:70.4%;background:#dfa732" title="2019 domestic: 1.76 nights"></span>
                      <b class="bpa-val">1.76</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2021</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:88.4%;background:#1e3a5f" title="2021 international: 2.21 nights"></span>
                      <b class="bpa-val">2.21</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:67.6%;background:#dfa732" title="2021 domestic: 1.69 nights"></span>
                      <b class="bpa-val">1.69</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:95.2%;background:#1e3a5f" title="2022 international: 2.38 nights"></span>
                      <b class="bpa-val">2.38</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:76.0%;background:#dfa732" title="2022 domestic: 1.90 nights"></span>
                      <b class="bpa-val">1.90</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:96.0%;background:#1e3a5f" title="2023 international: 2.40 nights"></span>
                      <b class="bpa-val">2.40</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:76.8%;background:#dfa732" title="2023 domestic: 1.92 nights"></span>
                      <b class="bpa-val">1.92</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:96.0%;background:#1e3a5f" title="2024 international: 2.40 nights"></span>
                      <b class="bpa-val">2.40</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:73.6%;background:#dfa732" title="2024 domestic: 1.84 nights"></span>
                      <b class="bpa-val">1.84</b>
                    </span>
                  </span>
                </div>
                <div class="bpa-row bpa-row-pair">
                  <span class="bpa-lab">2025</span>
                  <span class="bpa-pair">
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:97.6%;background:#1e3a5f" title="2025 international: 2.44 nights"></span>
                      <b class="bpa-val">2.44</b>
                    </span>
                    <span class="bpa-track">
                      <span class="bpa-seg" style="width:73.6%;background:#dfa732" title="2025 domestic: 1.84 nights"></span>
                      <b class="bpa-val">1.84</b>
                    </span>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: Computed from CBS StatLine Table 82061NED (Overnachtingen divided by Gasten)</div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Average duration of hotel stay in Amsterdam (nights per guest)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>All Guests</th>
                      <th>International</th>
                      <th>Domestic</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>2.00</td>
                      <td>2.05</td>
                      <td>1.76</td>
                    </tr>
                    <tr>
                      <td>2020</td>
                      <td>1.96</td>
                      <td>2.05</td>
                      <td>1.74</td>
                    </tr>
                    <tr>
                      <td>2021</td>
                      <td>2.00</td>
                      <td>2.21</td>
                      <td>1.69</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>2.26</td>
                      <td>2.38</td>
                      <td>1.90</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>2.30</td>
                      <td>2.40</td>
                      <td>1.92</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>2.28</td>
                      <td>2.40</td>
                      <td>1.84</td>
                    </tr>
                    <tr>
                      <td>2025</td>
                      <td>2.33</td>
                      <td>2.44</td>
                      <td>1.84</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>The average duration of stay in Amsterdam hotels has steadily increased by 16.5% compared to 2019 (from 2.00 nights to 2.33 nights). Foreign visitors stay roughly one-third longer on average (2.44 nights) than Dutch domestic travelers (1.84 nights).</p>
            <p>Intercontinental travelers from long-haul markets record the longest hotel durations in Amsterdam: American guests averaged 2.48 nights in 2025, Canadian guests averaged 2.61 nights, and Australian guests averaged 2.68 nights.</p>

            <h2 id="when-do-most-tourists-visit-amsterdam">When do most tourists visit Amsterdam?</h2>
            <p>The peak month for hotel stays in Amsterdam in 2025 was <strong>August</strong> with 2.22 million nights, closely followed by <strong>April</strong> with 2.11 million nights. <strong>February</strong> was the quietest month with 1.48 million nights.</p>

            <div class="bpa-chart" id="chart-ams-months" role="figure" aria-labelledby="chart-ams-months-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-ams-months-t">Hotel overnight stays in Amsterdam by month, 2025</div>
                <div class="bpa-chart-sub">Monthly hotel nights (CBS Municipality GM0363), millions</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">Jan</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:69.14%;background:#1e3a5f" title="Jan nights: 1.54 million"></span>
                    <b class="bpa-val">1.54M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Feb</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:66.80%;background:#1e3a5f" title="Feb nights: 1.48 million"></span>
                    <b class="bpa-val">1.48M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Mar</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:79.01%;background:#1e3a5f" title="Mar nights: 1.75 million"></span>
                    <b class="bpa-val">1.75M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Apr</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:95.14%;background:#1e3a5f" title="Apr nights: 2.11 million"></span>
                    <b class="bpa-val">2.11M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">May</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:87.97%;background:#1e3a5f" title="May nights: 1.95 million"></span>
                    <b class="bpa-val">1.95M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Jun</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:87.03%;background:#1e3a5f" title="Jun nights: 1.93 million"></span>
                    <b class="bpa-val">1.93M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Jul</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:93.24%;background:#1e3a5f" title="Jul nights: 2.07 million"></span>
                    <b class="bpa-val">2.07M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Aug</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="Aug nights: 2.22 million"></span>
                    <b class="bpa-val">2.22M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Sep</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:81.35%;background:#1e3a5f" title="Sep nights: 1.81 million"></span>
                    <b class="bpa-val">1.81M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Oct</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:88.65%;background:#1e3a5f" title="Oct nights: 1.97 million"></span>
                    <b class="bpa-val">1.97M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Nov</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:77.43%;background:#1e3a5f" title="Nov nights: 1.72 million"></span>
                    <b class="bpa-val">1.72M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Dec</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:74.23%;background:#1e3a5f" title="Dec nights: 1.65 million"></span>
                    <b class="bpa-val">1.65M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://opendata.cbs.nl/statline/#/CBS/en/dataset/82061NED" rel="noopener" target="_blank">CBS StatLine Table 82061NED (Monthly hotel data)</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Monthly hotel overnight stays in Amsterdam (CBS figures, thousands)</caption>
                  <thead>
                    <tr>
                      <th>Month</th>
                      <th>2025 Nights</th>
                      <th>2024 Nights</th>
                      <th>Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>January</td>
                      <td>1,535,000</td>
                      <td>1,416,000</td>
                      <td>+8.4%</td>
                    </tr>
                    <tr>
                      <td>February</td>
                      <td>1,483,000</td>
                      <td>1,431,000</td>
                      <td>+3.6%</td>
                    </tr>
                    <tr>
                      <td>March</td>
                      <td>1,754,000</td>
                      <td>1,755,000</td>
                      <td>-0.1%</td>
                    </tr>
                    <tr>
                      <td>April</td>
                      <td>2,112,000</td>
                      <td>1,920,000</td>
                      <td>+10.0%</td>
                    </tr>
                    <tr>
                      <td>May</td>
                      <td>1,953,000</td>
                      <td>1,906,000</td>
                      <td>+2.5%</td>
                    </tr>
                    <tr>
                      <td>June</td>
                      <td>1,932,000</td>
                      <td>1,799,000</td>
                      <td>+7.4%</td>
                    </tr>
                    <tr>
                      <td>July</td>
                      <td>2,070,000</td>
                      <td>2,062,000</td>
                      <td>+0.4%</td>
                    </tr>
                    <tr>
                      <td>August</td>
                      <td>2,220,000</td>
                      <td>2,053,000</td>
                      <td>+8.1%</td>
                    </tr>
                    <tr>
                      <td>September</td>
                      <td>1,806,000</td>
                      <td>1,793,000</td>
                      <td>+0.7%</td>
                    </tr>
                    <tr>
                      <td>October</td>
                      <td>1,968,000</td>
                      <td>1,849,000</td>
                      <td>+6.4%</td>
                    </tr>
                    <tr>
                      <td>November</td>
                      <td>1,719,000</td>
                      <td>1,653,000</td>
                      <td>+4.0%</td>
                    </tr>
                    <tr>
                      <td>December</td>
                      <td>1,648,000</td>
                      <td>1,598,000</td>
                      <td>+3.1%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Amsterdam exhibits a major spring peak in April and May, coinciding with the world-famous Dutch tulip bloom season, Keukenhof gardens opening, and King's Day (Koningsdag) celebrations on April 27. In 2025, April hotel nights reached 2.11 million, expanding 10.0% over April 2024.</p>
            <p>Summer visitation peaks in July and August (2.22 million nights in August 2025), before autumn cultural events, the Amsterdam Dance Event (ADE) in October (1.97 million nights), and Amsterdam Light Festival in December provide sustained volume through year-end.</p>

            <h2 id="where-do-visitors-to-amsterdam-come-from">Where do visitors to Amsterdam come from?</h2>
            <p>The <strong>United States</strong> is the largest foreign source market for Amsterdam hotels with <strong>2.82 million nights</strong> in 2025 (+14.0% vs 2024), narrowly overtaking the <strong>United Kingdom</strong> (2.77 million nights). <strong>Germany</strong> ranks third with 2.01 million nights.</p>

            <div class="bpa-chart" id="chart-ams-countries" role="figure" aria-labelledby="chart-ams-countries-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-ams-countries-t">Top 10 source countries in Amsterdam hotels, 2025</div>
                <div class="bpa-chart-sub">Hotel overnight stays (Municipality GM0363), millions</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">Netherlands</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#dfa732" title="Netherlands: 3.39 million"></span>
                    <b class="bpa-val">3.39M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">United States</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:83.15%;background:#1e3a5f" title="United States: 2.82 million"></span>
                    <b class="bpa-val">2.82M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">United Kingdom</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:81.68%;background:#1e3a5f" title="United Kingdom: 2.77 million"></span>
                    <b class="bpa-val">2.77M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Germany</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:59.31%;background:#1e3a5f" title="Germany: 2.01 million"></span>
                    <b class="bpa-val">2.01M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">France</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:34.79%;background:#1e3a5f" title="France: 1.18 million"></span>
                    <b class="bpa-val">1.18M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Italy</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:31.48%;background:#1e3a5f" title="Italy: 1.07 million"></span>
                    <b class="bpa-val">1.07M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Spain</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:30.63%;background:#1e3a5f" title="Spain: 1.04 million"></span>
                    <b class="bpa-val">1.04M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Belgium</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:17.65%;background:#1e3a5f" title="Belgium: 0.60 million"></span>
                    <b class="bpa-val">0.60M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Australia</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:13.04%;background:#1e3a5f" title="Australia: 0.44 million"></span>
                    <b class="bpa-val">0.44M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Canada</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:12.33%;background:#1e3a5f" title="Canada: 0.42 million"></span>
                    <b class="bpa-val">0.42M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://opendata.cbs.nl/statline/#/CBS/en/dataset/82061NED" rel="noopener" target="_blank">Statistics Netherlands (CBS), StatLine Table 82061NED</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Hotel nights in Amsterdam municipality by country of residence (CBS)</caption>
                  <thead>
                    <tr>
                      <th>Country</th>
                      <th>2025 Nights</th>
                      <th>2024 Nights</th>
                      <th>Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Netherlands (Domestic)</td>
                      <td>3,389,000</td>
                      <td>3,574,000</td>
                      <td>-5.2%</td>
                    </tr>
                    <tr>
                      <td>United States</td>
                      <td>2,818,000</td>
                      <td>2,471,000</td>
                      <td>+14.0%</td>
                    </tr>
                    <tr>
                      <td>United Kingdom</td>
                      <td>2,768,000</td>
                      <td>2,566,000</td>
                      <td>+7.9%</td>
                    </tr>
                    <tr>
                      <td>Germany</td>
                      <td>2,010,000</td>
                      <td>2,066,000</td>
                      <td>-2.7%</td>
                    </tr>
                    <tr>
                      <td>France</td>
                      <td>1,179,000</td>
                      <td>1,181,000</td>
                      <td>-0.2%</td>
                    </tr>
                    <tr>
                      <td>Italy</td>
                      <td>1,067,000</td>
                      <td>1,003,000</td>
                      <td>+6.4%</td>
                    </tr>
                    <tr>
                      <td>Spain</td>
                      <td>1,038,000</td>
                      <td>955,000</td>
                      <td>+8.7%</td>
                    </tr>
                    <tr>
                      <td>Belgium</td>
                      <td>598,000</td>
                      <td>574,000</td>
                      <td>+4.2%</td>
                    </tr>
                    <tr>
                      <td>Australia</td>
                      <td>442,000</td>
                      <td>404,000</td>
                      <td>+9.4%</td>
                    </tr>
                    <tr>
                      <td>Canada</td>
                      <td>418,000</td>
                      <td>346,000</td>
                      <td>+20.8%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Unlike many national statistics offices that only publish country data for the country as a whole, Statistics Netherlands publishes origin country data directly for the Amsterdam municipality (GM0363). The United States and the United Kingdom are the dominant foreign markets, together accounting for 5.59 million hotel nights (29.7% of all foreign nights in Amsterdam).</p>
            <p>Long-haul travel demonstrated rapid growth in 2025: Canadian visitor nights surged 20.8% (to 418,000), American nights expanded 14.0% (to 2.82 million), and Australian nights grew 9.4% (to 442,000).</p>

            <h2 id="how-much-do-tourists-spend-in-amsterdam">How much do tourists spend in Amsterdam?</h2>
            <p>The City of Amsterdam budgeted approximately <strong>242.5 million euros</strong> in tourist tax revenues in 2024, after raising its tourist tax rate to <strong>12.5%</strong>. Across the Netherlands as a whole, total tourism expenditure reached <strong>111.2 billion euros</strong> in 2024 according to CBS.</p>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Tourism economics and tourist tax receipts, Amsterdam &amp; Netherlands</caption>
                  <thead>
                    <tr>
                      <th>Metric</th>
                      <th>2024 Value</th>
                      <th>2023 Value</th>
                      <th>Source &amp; Scope</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Amsterdam Tourist Tax Revenue</td>
                      <td>&euro;242.5M</td>
                      <td>&euro;165.0M</td>
                      <td>Gemeente Amsterdam (Municipality GM0363)</td>
                    </tr>
                    <tr>
                      <td>Amsterdam Tourist Tax Rate</td>
                      <td>12.5%</td>
                      <td>7% + &euro;3/night</td>
                      <td>City of Amsterdam tax ordinance</td>
                    </tr>
                    <tr>
                      <td>Netherlands Total Tourism Spend</td>
                      <td>&euro;111.2B</td>
                      <td>&euro;105.3B</td>
                      <td>CBS Tourism Satellite Accounts (National)</td>
                    </tr>
                    <tr>
                      <td>Inbound Foreign Visitor Spend</td>
                      <td>&euro;38.2B</td>
                      <td>&euro;34.5B</td>
                      <td>CBS (National total for all international visitors)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>In 2024, the City Council of Amsterdam enacted an increase in the municipal tourist tax (<em>toeristenbelasting</em>) to 12.5% of the net accommodation price, creating the highest tourist tax rate in the European Union. This policy was designed to generate municipal revenue to fund public services and manage visitor pressure in historic central neighbourhoods.</p>
            <p>At the national level, CBS Tourism Satellite Accounts report that total tourism spending in the Netherlands reached 111.2 billion euros in 2024, with foreign travelers contributing 38.2 billion euros. Amsterdam accounts for the largest municipal share of inbound visitor expenditure in the country.</p>

            <h2 id="how-busy-is-amsterdam-airport-schiphol">How busy is Amsterdam Airport Schiphol?</h2>
            <p>Amsterdam Airport Schiphol handled <strong>66.8 million passengers</strong> in 2024, an increase of <strong>8.0%</strong> compared to 61.9 million in 2023, while recording <strong>473,815 aircraft movements</strong>.</p>

            <div class="bpa-chart" id="chart-ams-schiphol" role="figure" aria-labelledby="chart-ams-schiphol-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-ams-schiphol-t">Passenger traffic at Amsterdam Airport Schiphol, 2019 to 2024</div>
                <div class="bpa-chart-sub">Annual terminal passengers (Royal Schiphol Group), millions</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="2019 Schiphol: 71.7 million passengers"></span>
                    <b class="bpa-val">71.7M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2020</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:29.15%;background:#1e3a5f" title="2020 Schiphol: 20.9 million passengers"></span>
                    <b class="bpa-val">20.9M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2021</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:35.56%;background:#1e3a5f" title="2021 Schiphol: 25.5 million passengers"></span>
                    <b class="bpa-val">25.5M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:73.22%;background:#1e3a5f" title="2022 Schiphol: 52.5 million passengers"></span>
                    <b class="bpa-val">52.5M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:86.33%;background:#1e3a5f" title="2023 Schiphol: 61.9 million passengers"></span>
                    <b class="bpa-val">61.9M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:93.17%;background:#1e3a5f" title="2024 Schiphol: 66.8 million passengers"></span>
                    <b class="bpa-val">66.8M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.schiphol.nl/en/annual-reports/" rel="noopener" target="_blank">Royal Schiphol Group, Traffic Reviews and Annual Reports</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Traffic performance at Amsterdam Airport Schiphol (Royal Schiphol Group)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Total Passengers</th>
                      <th>Commercial Flights</th>
                      <th>Change vs Previous Year</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>71,700,000</td>
                      <td>496,826</td>
                      <td>Baseline</td>
                    </tr>
                    <tr>
                      <td>2020</td>
                      <td>20,900,000</td>
                      <td>227,304</td>
                      <td>-70.9%</td>
                    </tr>
                    <tr>
                      <td>2021</td>
                      <td>25,500,000</td>
                      <td>266,967</td>
                      <td>+22.0%</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>52,500,000</td>
                      <td>397,646</td>
                      <td>+105.9%</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>61,900,000</td>
                      <td>441,963</td>
                      <td>+17.9%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>66,800,000</td>
                      <td>473,815</td>
                      <td>+7.9%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Amsterdam Airport Schiphol operates as one of Europe's top four international hub airports and the global headquarters of KLM Royal Dutch Airlines. In 2024, 45.3 million passengers travelled to or from European destinations, while 21.5 million were intercontinental travelers.</p>
            <p>Across the wider Royal Schiphol Group (which includes regional hubs Eindhoven Airport and Rotterdam The Hague Airport), total passenger volume reached 75.9 million travelers in 2024 on 529,248 flight movements.</p>

            <h2 id="what-are-the-top-destinations-to-visit-in-amsterdam">What are the top destinations to visit in Amsterdam?</h2>
            <p>Amsterdam offers an exceptional concentration of 17th-century cultural heritage and art museums. Five of the most visited sights include:</p>
            <ul role="list">
              <li><strong>Rijksmuseum</strong>: The national museum of the Netherlands welcoming over 2.7 million visitors annually, showcasing Dutch Golden Age masterpieces including Rembrandt's <em>The Night Watch</em> and Vermeer's <em>The Milkmaid</em>.</li>
              <li><strong>Van Gogh Museum</strong>: Housing the largest collection of Vincent van Gogh's artwork in the world, including 200 paintings and 500 drawings, welcoming over 2.2 million visitors each year.</li>
              <li><strong>The 17th-Century Canal Ring (Grachtengordel)</strong>: Inscribed as a UNESCO World Heritage site in 2010, the historic network of concentric waterways (Herengracht, Keizersgracht, and Prinsengracht) is the city's defining feature. Exploring by an undercover-reviewed <a href="/canal-cruises-amsterdam">Amsterdam canal cruise</a> on an open electric sloop or classic salon boat is the quintessential visitor experience.</li>
              <li><strong>Anne Frank House</strong>: Located on the Prinsengracht canal, the historic biographical museum preserving the secret annex where Anne Frank hid during World War II receives roughly 1.2 million visitors annually.</li>
              <li><strong>Vondelpark</strong>: The city's most celebrated 47-hectare public park, welcoming over 10 million visits annually from residents and travelers for walking, cycling, and open-air concerts.</li>
            </ul>

            <h2 id="sources-and-methodology">Sources and methodology</h2>
            <ul role="list">
              <li><strong>Hotel Guests, Nights and Country of Residence</strong>: Sourced directly from Statistics Netherlands (<a href="https://opendata.cbs.nl/statline/#/CBS/en/dataset/82061NED" rel="noopener" target="_blank">Centraal Bureau voor de Statistiek &ndash; CBS</a>), StatLine Table 82061NED: <em>Hotels; gasten, overnachtingen, woonland, regio</em>. Geographic scope: Municipality of Amsterdam (Gemeentecode GM0363). Data accessed November 2026.</li>
              <li><strong>Tourist Tax and Local Municipal Finance</strong>: Sourced from Gemeente Amsterdam, Directie Financi&euml;n and Onderzoek en Statistiek (OIS), municipal budget and actual tax revenue reports (2023, 2024).</li>
              <li><strong>National Tourism Expenditure</strong>: Sourced from CBS Tourism Satellite Accounts (Toeristische bestedingen in Nederland, 2023 and 2024).</li>
              <li><strong>Airport Traffic Statistics</strong>: Sourced from <a href="https://www.schiphol.nl/en/annual-reports/" rel="noopener" target="_blank">Royal Schiphol Group</a> annual traffic reviews and operational statistics for Amsterdam Airport Schiphol (2019 to 2024).</li>
              <li><strong>Definitions</strong>: CBS figures cover hotels, motels, boarding houses, hotel-apartments, youth accommodation, and bed &amp; breakfasts with a capacity of at least 5 beds. Private short-term holiday rentals (e.g. Airbnb) and day visits are excluded from the hotel series. Duration of stay is computed as total overnight stays divided by registered hotel guests.</li>
            </ul>
            <div class="bpa-cite">
              <strong>Using these statistics?</strong> You are welcome to quote the figures and charts on this page. Please credit and link to <a href="/amsterdam-tourism-statistics">The Cruise Detective, Amsterdam Tourism Statistics</a>.
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</main>

{COMMON_FOOTER_HTML}
{COMMON_SCRIPTS}
</body>
</html>
"""
    return html

def get_london_html():
    canonical = "https://www.thecruisedetective.com/london-tourism-statistics"
    title = "London Tourism Statistics 2026: How Many Tourists Visit?"
    meta_desc = "London welcomed 22.0 million overseas visits and 123.8 million nights in 2024. Official ONS data on visitors, length of stay, source countries and spending."
    og_image = "https://www.thecruisedetective.com/assets/cdn/652d0405192ba076b04f74a3/656b5269b59a73ed77082a40_best-london-river-cruises-featured-image.webp"

    assert len(title) <= 60, f"Title too long: {len(title)}"
    assert 140 <= len(meta_desc) <= 160, f"Meta description invalid length: {len(meta_desc)}"

    json_ld = """{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "London Tourism Statistics 2026: How Many Tourists Visit?",
  "description": "London welcomed 22.0 million overseas visits and 123.8 million nights in 2024. Official ONS data on visitors, length of stay, source countries and spending.",
  "datePublished": "2026-11-13",
  "dateModified": "2026-11-13",
  "inLanguage": "en",
  "mainEntityOfPage": "https://www.thecruisedetective.com/london-tourism-statistics",
  "author": {
    "@type": "Person",
    "name": "Adam Dimitrov",
    "url": "https://www.thecruisedetective.com/about"
  },
  "publisher": {
    "@type": "Organization",
    "name": "The Cruise Detective",
    "url": "https://www.thecruisedetective.com/"
  },
  "citation": [
    "https://www.ons.gov.uk/peoplepopulationandcommunity/leisureandtourism/bulletins/traveltrends/2023",
    "https://data.london.gov.uk/",
    "https://www.visitbritain.org/",
    "https://www.heathrow.com/company/investor-centre/reports/traffic-statistics"
  ]
}"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>{title}</title>
<meta content="{meta_desc}" name="description"/>
<meta content="{title}" property="og:title"/>
<meta content="{meta_desc}" property="og:description"/>
<meta content="{og_image}" property="og:image"/>
<meta content="{canonical}" property="og:url"/>
<meta content="article" property="og:type"/>
<meta content="{title}" name="twitter:title"/>
<meta content="{meta_desc}" name="twitter:description"/>
<meta content="{og_image}" name="twitter:image"/>
<meta content="summary_large_image" name="twitter:card"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<meta content="google-site-verification=jPygzQl3dLYHsZI7XMPOqvcxGUVZtEr6WiuGN_O2xjo" name="google-site-verification"/>

<link href="/favicon.ico" rel="icon" type="image/x-icon"/>
<link href="/favicon.ico" rel="shortcut icon" type="image/x-icon"/>
<link href="/assets/apple-touch-icon.png" rel="apple-touch-icon"/>
<link href="{canonical}" rel="canonical"/>
<link href="{canonical}" hreflang="en" rel="alternate"/>
<link href="{canonical}" hreflang="x-default" rel="alternate"/>

<!-- Google Fonts -->
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&amp;family=Plus+Jakarta+Sans:wght@400;500;600;700;800&amp;display=swap" rel="stylesheet"/>

<!-- Core Stylesheets -->
<link href="/css/thecruisedetective-com.webflow.shared.3cc389acf.min.css" rel="stylesheet" type="text/css"/>

<!-- Analytics -->
<script>
window.dataLayer = window.dataLayer || [];
function gtag(){{dataLayer.push(arguments);}}
gtag('set', 'developer_id.dZGVlNj', true);
gtag('set', 'developer_id.dYWYxNW', true);
gtag('js', new Date());
gtag('config', 'G-RN34XFKPQ6');

!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;
n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];}}(window,document);
fbq('init', '1355732169631751');
fbq('track', 'PageView');
</script>

<script type="application/ld+json">
{json_ld}
</script>

{COMMON_HEAD_CSS}
</head>
<body id="top">
{COMMON_HEADER_HTML}

<main id="main" role="main">
<div class="ltt-hero-wrap">
  <div class="ltt-clean-card">
    <div class="ltt-top-bar">
      <nav aria-label="Breadcrumb" class="ltt-breadcrumbs">
        <a href="/">Home</a>
        <span class="ltt-bc-sep">&rsaquo;</span>
        <span class="ltt-bc-current">London Tourism Statistics (2026)</span>
      </nav>
      <span class="ltt-hero-kicker-badge">Official ONS &amp; VisitBritain Data &middot; 2019 to 2024</span>
    </div>
    <h1 class="ltt-editorial-h1">
      London Tourism Statistics 2026 <span class="ltt-h1-muted">(How Many Tourists Visit?)</span>
    </h1>
    <div class="ltt-trust-bar">
      <div class="ltt-author-cluster">
        <div class="ltt-author-avatar-wrap">
          <img alt="Adam Dimitrov" class="ltt-author-avatar" height="42" loading="eager" src="/assets/cdn/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp" width="42"/>
        </div>
        <div class="ltt-author-meta">
          <div class="ltt-author-line">
            By <a href="/about" target="_blank">Adam Dimitrov</a>, Owner &amp; Head Cruise Detective
          </div>
          <div class="ltt-author-role">Compiled from Official ONS &amp; VisitBritain Data &bull; 6 Charts with Data Tables &bull; <a href="#sources-and-methodology">Methodology</a></div>
        </div>
      </div>
      <div class="ltt-trust-pills">
        <span class="ltt-trust-pill paragraph-26"><strong>Last updated</strong>: Nov 13, 2026</span>
      </div>
    </div>
    <div class="ltt-lead-copy">
      <p>London welcomed an estimated <strong>22.0 million overseas visits</strong> and <strong>123.8 million visitor nights</strong> in 2024, fully regaining pre-pandemic volume according to the Office for National Statistics (ONS) International Passenger Survey.</p>
      <p>This report compiles official <strong>London tourism statistics</strong> from the ONS, VisitBritain, the Greater London Authority (London Datastore), and Heathrow Airport: inbound visits, domestic tourism trips, length of stay, leading country markets, total expenditure, and aviation traffic figures. All charts include verifiable data tables and primary reference sources.</p>
    </div>
  </div>
</div>

<div class="blog-section">
  <div class="container-26">
    <div class="blog-grid-2">
      <div class="content-left">
        <div class="stick-wrapper">
          <div class="title-small-3" style="font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; margin-bottom: 12px; padding-bottom: 6px; border-bottom: 1px solid #f1f5f9;">Table of Contents</div>
          <div class="toc" id="toc">
            <a class="tocitem" href="#key-london-tourism-statistics-2024">Key London tourism statistics (2024)</a>
            <a class="tocitem" href="#how-many-tourists-visit-london-each-year">How many tourists visit London each year?</a>
            <a class="tocitem" href="#how-many-nights-do-tourists-spend-in-london">How many nights do tourists spend in London?</a>
            <a class="tocitem" href="#how-long-do-visitors-stay-in-london">How long do visitors stay in London?</a>
            <a class="tocitem" href="#where-do-visitors-to-london-come-from">Where do visitors to London come from?</a>
            <a class="tocitem" href="#how-much-do-tourists-spend-in-london">How much do tourists spend in London?</a>
            <a class="tocitem" href="#how-important-is-domestic-tourism-to-london">How important is domestic tourism to London?</a>
            <a class="tocitem" href="#how-busy-is-london-heathrow-airport">How busy is London Heathrow Airport?</a>
            <a class="tocitem" href="#what-are-the-top-destinations-to-visit-in-london">What are the top destinations to visit in London?</a>
            <a class="tocitem" href="#sources-and-methodology">Sources and methodology</a>
          </div>
        </div>
      </div>
      <div class="content-right_blog" id="content">
        <div class="w-layout-blockcontainer container w-container">
          <div class="w-richtext">

            <h2 id="key-london-tourism-statistics-2024">Key London tourism statistics (2024)</h2>
            <div class="bpa-tiles">
              <div class="bpa-tile">
                <div class="bpa-tile-num">22.0M</div>
                <div class="bpa-tile-lab">overseas visits in 2024, up 8.5% on 2023</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">123.8M</div>
                <div class="bpa-tile-lab">visitor nights in London in 2024</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">&pound;18.0B</div>
                <div class="bpa-tile-lab">inbound international visitor spend</div>
              </div>
              <div class="bpa-tile">
                <div class="bpa-tile-num">5.63</div>
                <div class="bpa-tile-lab">nights is the average overseas stay</div>
              </div>
            </div>
            <ul role="list">
              <li>London welcomed approximately <strong>22.0 million overseas visits</strong> in 2024, an 8.5% gain compared to 2023 (20.28 million) and exceeding the pre-pandemic 2019 baseline of 21.71 million visits.</li>
              <li>International visitors spent <strong>123.8 million nights</strong> in the capital in 2024, up 6.9% from 115.79 million in 2023.</li>
              <li>Overseas tourist expenditure in London reached approximately <strong>&pound;18.0 billion</strong> in 2024, expanding 7.8% over 2023 (&pound;16.70 billion) and 14.6% higher than 2019 (&pound;15.70 billion).</li>
              <li>The <strong>United States</strong> is London's dominant international source market, delivering 3.4 million visits and generating more than 22% of total inbound visitor spend.</li>
              <li>Domestic overnight tourism from other regions of Great Britain generated <strong>15.9 million trips</strong> to London in 2023, while domestic day visitors made an additional <strong>217 million day trips</strong>.</li>
              <li>London Heathrow Airport set an all-time annual passenger record in 2024, processing <strong>83.86 million passengers</strong> (+5.9% vs 2023).</li>
            </ul>

            <h2 id="how-many-tourists-visit-london-each-year">How many tourists visit London each year?</h2>
            <p>London welcomed approximately <strong>22.0 million international visits</strong> in 2024, up <strong>8.5%</strong> from 20.28 million in 2023. International visitor volume has now fully recovered past its pre-pandemic high of 21.71 million recorded in 2019.</p>

            <div class="bpa-chart" id="chart-london-visits" role="figure" aria-labelledby="chart-london-visits-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-london-visits-t">Inbound overseas visits to London, 2019 to 2024</div>
                <div class="bpa-chart-sub">Overseas resident visits to London (ONS International Passenger Survey), millions</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:98.68%;background:#1e3a5f" title="2019 visits: 21.71 million"></span>
                    <b class="bpa-val">21.71M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2021</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:12.48%;background:#1e3a5f" title="2021 visits: 2.75 million"></span>
                    <b class="bpa-val">2.75M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:73.30%;background:#1e3a5f" title="2022 visits: 16.13 million"></span>
                    <b class="bpa-val">16.13M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:92.18%;background:#1e3a5f" title="2023 visits: 20.28 million"></span>
                    <b class="bpa-val">20.28M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="2024 visits: 22.00 million"></span>
                    <b class="bpa-val">22.00M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.ons.gov.uk/peoplepopulationandcommunity/leisureandtourism/bulletins/traveltrends/2023" rel="noopener" target="_blank">Office for National Statistics (ONS), Travel trends</a> &amp; London Datastore</div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Inbound visits to London by overseas residents (ONS International Passenger Survey)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Inbound Visits</th>
                      <th>Annual Change</th>
                      <th>Share of Total UK Inbound Visits</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>21,714,000</td>
                      <td>Baseline</td>
                      <td>53.1%</td>
                    </tr>
                    <tr>
                      <td>2021</td>
                      <td>2,746,000</td>
                      <td>-87.4% vs 2019</td>
                      <td>43.1%</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>16,126,000</td>
                      <td>+487.3%</td>
                      <td>51.6%</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>20,277,000</td>
                      <td>+25.7%</td>
                      <td>53.4%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>22,000,000</td>
                      <td>+8.5%</td>
                      <td>53.8%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>The International Passenger Survey (IPS) is conducted continuously by the ONS at all major UK airports, seaports, and the Eurostar terminal. Following severe disruption during 2020 and 2021 when international borders were restricted, London recaptured its role as the primary UK gateway destination.</p>
            <p>London captures more than half of all overseas visits to the United Kingdom (53.4% in 2023 and 53.8% in 2024). Holiday travel accounts for 53% of visits to London, followed by visits to friends and relatives (VFR) at 27%, and business trips at 16%.</p>

            <h2 id="how-many-nights-do-tourists-spend-in-london">How many nights do tourists spend in London?</h2>
            <p>Overseas visitors spent an estimated <strong>123.8 million nights</strong> in London during 2024, up <strong>6.9%</strong> compared to 115.79 million in 2023 and 4.1% higher than the 118.87 million nights recorded in 2019.</p>

            <div class="bpa-chart" id="chart-london-nights" role="figure" aria-labelledby="chart-london-nights-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-london-nights-t">Inbound visitor nights in London, 2019 to 2024</div>
                <div class="bpa-chart-sub">Nights spent in London by overseas residents (ONS IPS), millions</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:96.02%;background:#1e3a5f" title="2019 nights: 118.87 million"></span>
                    <b class="bpa-val">118.87M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:84.09%;background:#1e3a5f" title="2022 nights: 104.10 million"></span>
                    <b class="bpa-val">104.10M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:93.53%;background:#1e3a5f" title="2023 nights: 115.79 million"></span>
                    <b class="bpa-val">115.79M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="2024 nights: 123.80 million"></span>
                    <b class="bpa-val">123.80M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://data.london.gov.uk/" rel="noopener" target="_blank">GLA Economics, London Datastore &amp; ONS IPS</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Inbound visitor nights in London (ONS International Passenger Survey)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Total Nights</th>
                      <th>Average Nights per Visit</th>
                      <th>Annual Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>118,872,000</td>
                      <td>5.47</td>
                      <td>Baseline</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>104,100,000</td>
                      <td>6.46</td>
                      <td>-12.4% vs 2019</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>115,787,000</td>
                      <td>5.71</td>
                      <td>+11.2%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>123,800,000</td>
                      <td>5.63</td>
                      <td>+6.9%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Unlike continental European city destinations such as Paris or Amsterdam where visitor statistics are derived from hotel registry forms, London's official tourism metrics come from traveler surveys. As a result, ONS figures capture all accommodation types: commercial hotels, short-stay holiday apartments, hostels, and nights spent staying with friends and relatives.</p>
            <p>Total overnight volume reached 123.8 million in 2024, demonstrating that travelers are making slightly longer trips than before 2020. The expansion of remote working and combined "bleisure" trips (combining business travel with weekend leisure stays) has supported sustained room night volumes.</p>

            <h2 id="how-long-do-visitors-stay-in-london">How long do visitors stay in London?</h2>
            <p>The average overseas visitor stayed <strong>5.63 nights</strong> in London in 2024, compared to 5.71 nights in 2023 and 5.47 nights in 2019.</p>

            <div class="bpa-chart" id="chart-london-stay" role="figure" aria-labelledby="chart-london-stay-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-london-stay-t">Average length of stay in London (nights per visit)</div>
                <div class="bpa-chart-sub">Average duration of stay for inbound overseas visitors, 2019 to 2024</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:84.67%;background:#1e3a5f" title="2019 stay: 5.47 nights"></span>
                    <b class="bpa-val">5.47</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="2022 stay: 6.46 nights"></span>
                    <b class="bpa-val">6.46</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:88.39%;background:#1e3a5f" title="2023 stay: 5.71 nights"></span>
                    <b class="bpa-val">5.71</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:87.15%;background:#1e3a5f" title="2024 stay: 5.63 nights"></span>
                    <b class="bpa-val">5.63</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: Computed from ONS International Passenger Survey data (Nights divided by Visits)</div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Length of stay and expenditure per visit in London (ONS IPS)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Nights per Visit</th>
                      <th>Spend per Visit</th>
                      <th>Spend per Night</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>5.47</td>
                      <td>&pound;723</td>
                      <td>&pound;132</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>6.46</td>
                      <td>&pound;877</td>
                      <td>&pound;136</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>5.71</td>
                      <td>&pound;823</td>
                      <td>&pound;144</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>5.63</td>
                      <td>&pound;818</td>
                      <td>&pound;145</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>London's average stay of 5.63 nights is substantially longer than that of Paris (2.27 hotel nights) or Amsterdam (2.33 hotel nights) because the UK figures encompass all forms of accommodation and reflect London's status as a major global hub for long-haul vacationers and family reunions.</p>
            <p>Duration varies sharply by purpose of visit. Holidaymakers stay an average of 4.5 nights, business travelers stay 3.8 nights, and travelers visiting friends or relatives average 8.4 nights in the capital.</p>

            <h2 id="where-do-visitors-to-london-come-from">Where do visitors to London come from?</h2>
            <p>The <strong>United States</strong> is London's largest international market, generating <strong>3.40 million visits</strong> (16.8% of all overseas arrivals), followed by <strong>France</strong> (1.80 million), <strong>Germany</strong> (1.50 million), and the <strong>Republic of Ireland</strong> (1.20 million).</p>

            <div class="bpa-chart" id="chart-london-countries" role="figure" aria-labelledby="chart-london-countries-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-london-countries-t">Top international source markets for London (visits in millions)</div>
                <div class="bpa-chart-sub">Annual overseas resident visits (VisitBritain &amp; ONS IPS)</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">United States</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="United States: 3.40 million"></span>
                    <b class="bpa-val">3.40M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">France</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:52.94%;background:#1e3a5f" title="France: 1.80 million"></span>
                    <b class="bpa-val">1.80M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Germany</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:44.12%;background:#1e3a5f" title="Germany: 1.50 million"></span>
                    <b class="bpa-val">1.50M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Rep. of Ireland</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:35.29%;background:#1e3a5f" title="Rep. of Ireland: 1.20 million"></span>
                    <b class="bpa-val">1.20M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Spain</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:32.35%;background:#1e3a5f" title="Spain: 1.10 million"></span>
                    <b class="bpa-val">1.10M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Italy</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:29.41%;background:#1e3a5f" title="Italy: 1.00 million"></span>
                    <b class="bpa-val">1.00M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Australia</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:23.53%;background:#1e3a5f" title="Australia: 0.80 million"></span>
                    <b class="bpa-val">0.80M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Netherlands</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:20.59%;background:#1e3a5f" title="Netherlands: 0.70 million"></span>
                    <b class="bpa-val">0.70M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.visitbritain.org/" rel="noopener" target="_blank">VisitBritain Inbound Market Insights &amp; ONS IPS</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Leading international source countries for London visits (VisitBritain)</caption>
                  <thead>
                    <tr>
                      <th>Country</th>
                      <th>Inbound Visits</th>
                      <th>Share of Total Overseas Visits</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>United States</td>
                      <td>3,400,000</td>
                      <td>16.8%</td>
                    </tr>
                    <tr>
                      <td>France</td>
                      <td>1,800,000</td>
                      <td>8.9%</td>
                    </tr>
                    <tr>
                      <td>Germany</td>
                      <td>1,500,000</td>
                      <td>7.4%</td>
                    </tr>
                    <tr>
                      <td>Republic of Ireland</td>
                      <td>1,200,000</td>
                      <td>5.9%</td>
                    </tr>
                    <tr>
                      <td>Spain</td>
                      <td>1,100,000</td>
                      <td>5.4%</td>
                    </tr>
                    <tr>
                      <td>Italy</td>
                      <td>1,000,000</td>
                      <td>4.9%</td>
                    </tr>
                    <tr>
                      <td>Australia</td>
                      <td>800,000</td>
                      <td>3.9%</td>
                    </tr>
                    <tr>
                      <td>Netherlands</td>
                      <td>700,000</td>
                      <td>3.5%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>The United States represents London's most valuable overseas tourism market. American visitors account for roughly one in six overseas trips to the city and generate more than 22% of total inbound visitor expenditure. Nearly half of all nights spent by Americans visiting the UK are spent in London.</p>
            <p>Close European neighbours (France, Germany, Ireland, Spain, and Italy) generate a steady volume of city breaks and cultural getaways throughout the year, bolstered by direct flights and high-frequency Eurostar train services into St Pancras International.</p>

            <h2 id="how-much-do-tourists-spend-in-london">How much do tourists spend in London?</h2>
            <p>Inbound overseas visitors spent an estimated <strong>&pound;18.0 billion</strong> in London in 2024, expanding <strong>7.8%</strong> over 2023 (&pound;16.70 billion) and <strong>14.6%</strong> above the 2019 pre-pandemic baseline (&pound;15.70 billion).</p>

            <div class="bpa-chart" id="chart-london-spend" role="figure" aria-labelledby="chart-london-spend-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-london-spend-t">Inbound overseas visitor spending in London, 2019 to 2024</div>
                <div class="bpa-chart-sub">Total tourism expenditure at current prices (ONS IPS), billion pounds</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:87.22%;background:#1e3a5f" title="2019 spending: 15.70 billion pounds"></span>
                    <b class="bpa-val">&pound;15.70B</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:78.61%;background:#1e3a5f" title="2022 spending: 14.15 billion pounds"></span>
                    <b class="bpa-val">&pound;14.15B</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:92.78%;background:#1e3a5f" title="2023 spending: 16.70 billion pounds"></span>
                    <b class="bpa-val">&pound;16.70B</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="2024 spending: 18.00 billion pounds"></span>
                    <b class="bpa-val">&pound;18.00B</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://data.london.gov.uk/" rel="noopener" target="_blank">GLA Economics &amp; ONS Travel trends</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Overseas visitor expenditure in London (current prices)</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Nominal Spending</th>
                      <th>Average Spend per Visit</th>
                      <th>Annual Change</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>&pound;15,700,000,000</td>
                      <td>&pound;723</td>
                      <td>Baseline</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>&pound;14,149,000,000</td>
                      <td>&pound;877</td>
                      <td>-9.9% vs 2019</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>&pound;16,697,000,000</td>
                      <td>&pound;823</td>
                      <td>+18.0%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>&pound;18,000,000,000</td>
                      <td>&pound;818</td>
                      <td>+7.8%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Spending is published in current nominal prices by the ONS and GLA Economics. Part of the expenditure growth between 2019 and 2024 reflects post-pandemic inflation across hotel room rates, restaurants, and theater tickets. In constant 2019 prices, 2023 spending equated to approximately &pound;13.78 billion.</p>
            <p>London captures approximately 54% of all international visitor expenditure in the United Kingdom (&pound;16.70 billion of the UK total &pound;31.1 billion in 2023). Average spend per visit was &pound;818 in 2024, equating to approximately &pound;145 per night.</p>

            <h2 id="how-important-is-domestic-tourism-to-london">How important is domestic tourism to London?</h2>
            <p>British residents took <strong>15.9 million domestic overnight trips</strong> to London in 2023, while domestic day visitors made an additional <strong>217 million tourism day visits</strong> generating &pound;14.8 billion in spending.</p>

            <div class="bpa-chart" id="chart-london-domestic" role="figure" aria-labelledby="chart-london-domestic-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-london-domestic-t">Visitor volume breakdown for London, 2023</div>
                <div class="bpa-chart-sub">Visits and trips by visitor category (VisitBritain &amp; ONS IPS)</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">Overseas Visits</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:9.35%;background:#1e3a5f" title="Overseas overnight visits: 20.28 million"></span>
                    <b class="bpa-val">20.28M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Domestic Trips</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:7.33%;background:#dfa732" title="Domestic overnight trips: 15.90 million"></span>
                    <b class="bpa-val">15.90M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">Domestic Days</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#10b981" title="Domestic day visits: 217.0 million"></span>
                    <b class="bpa-val">217.0M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.visitbritain.org/" rel="noopener" target="_blank">VisitBritain (GBTS &amp; GBDVS) &amp; ONS IPS</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Domestic vs international tourism volume in London (2023)</caption>
                  <thead>
                    <tr>
                      <th>Visitor Segment</th>
                      <th>Volume</th>
                      <th>Total Spend</th>
                      <th>Share of England Volume</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>Inbound Overseas Visits</td>
                      <td>20,280,000</td>
                      <td>&pound;16.70B</td>
                      <td>53.4% of UK total</td>
                    </tr>
                    <tr>
                      <td>Domestic Overnight Trips</td>
                      <td>15,900,000</td>
                      <td>&pound;4.23B</td>
                      <td>16.0% of England total</td>
                    </tr>
                    <tr>
                      <td>Domestic Tourism Day Visits</td>
                      <td>217,000,000</td>
                      <td>&pound;14.80B</td>
                      <td>21.0% of England total</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>According to VisitBritain's Great Britain Tourism Survey (GBTS), London's share of all domestic overnight trips in England rose from 15% in 2022 to 16% in 2023 and 17% in 2024, demonstrating renewed preference for urban cultural city breaks.</p>
            <p>Domestic day trips represent massive economic volume for London's leisure sector. In 2023, visitors living in the South East, East of England, and the Home Counties made 217 million leisure day visits into London (+24% year-on-year), contributing 14.8 billion pounds in retail, dining, and attraction spending.</p>

            <h2 id="how-busy-is-london-heathrow-airport">How busy is London Heathrow Airport?</h2>
            <p>London Heathrow Airport processed <strong>83.86 million passengers</strong> in 2024, setting an all-time annual record with a <strong>5.9%</strong> increase over 2023 (79.15 million) and surpassing its pre-pandemic 2019 record of 80.89 million.</p>

            <div class="bpa-chart" id="chart-heathrow-traffic" role="figure" aria-labelledby="chart-heathrow-traffic-t">
              <div class="bpa-chart-head">
                <div class="bpa-chart-title" id="chart-heathrow-traffic-t">Passenger traffic at London Heathrow Airport, 2019 to 2024</div>
                <div class="bpa-chart-sub">Annual terminal passengers (Heathrow Airport Limited), millions</div>
              </div>
              <div class="bpa-bars">
                <div class="bpa-row">
                  <span class="bpa-lab">2019</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:96.46%;background:#1e3a5f" title="2019 Heathrow: 80.89 million"></span>
                    <b class="bpa-val">80.89M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2020</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:26.37%;background:#1e3a5f" title="2020 Heathrow: 22.11 million"></span>
                    <b class="bpa-val">22.11M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2021</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:23.13%;background:#1e3a5f" title="2021 Heathrow: 19.40 million"></span>
                    <b class="bpa-val">19.40M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2022</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:73.47%;background:#1e3a5f" title="2022 Heathrow: 61.61 million"></span>
                    <b class="bpa-val">61.61M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2023</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:94.38%;background:#1e3a5f" title="2023 Heathrow: 79.15 million"></span>
                    <b class="bpa-val">79.15M</b>
                  </span>
                </div>
                <div class="bpa-row">
                  <span class="bpa-lab">2024</span>
                  <span class="bpa-track">
                    <span class="bpa-seg" style="width:100.0%;background:#1e3a5f" title="2024 Heathrow: 83.86 million"></span>
                    <b class="bpa-val">83.86M</b>
                  </span>
                </div>
              </div>
              <div class="bpa-src">Source: <a href="https://www.heathrow.com/company/investor-centre/reports/traffic-statistics" rel="noopener" target="_blank">Heathrow Airport Limited, Traffic Statistics</a></div>
            </div>

            <details class="bpa-details">
              <summary>Show the data table</summary>
              <div class="bpa-table-wrap">
                <table class="bpa-table">
                  <caption>Terminal passenger traffic at London Heathrow Airport</caption>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>Terminal Passengers</th>
                      <th>Annual Change</th>
                      <th>vs 2019 Baseline</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td>2019</td>
                      <td>80,886,589</td>
                      <td>Baseline</td>
                      <td>100.0%</td>
                    </tr>
                    <tr>
                      <td>2020</td>
                      <td>22,109,726</td>
                      <td>-72.7%</td>
                      <td>27.3%</td>
                    </tr>
                    <tr>
                      <td>2021</td>
                      <td>19,392,178</td>
                      <td>-12.3%</td>
                      <td>24.0%</td>
                    </tr>
                    <tr>
                      <td>2022</td>
                      <td>61,611,838</td>
                      <td>+217.7%</td>
                      <td>76.2%</td>
                    </tr>
                    <tr>
                      <td>2023</td>
                      <td>79,151,723</td>
                      <td>+28.5%</td>
                      <td>97.9%</td>
                    </tr>
                    <tr>
                      <td>2024</td>
                      <td>83,860,000</td>
                      <td>+5.9%</td>
                      <td>103.7%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </details>

            <p>Heathrow stands as the busiest airport in Europe and the primary hub for British Airways and the oneworld alliance. Transatlantic capacity between London and North American gateways expanded significantly in 2024, driving the airport to its busiest operational year in history.</p>
            <p>Across the wider London airport system (comprising Heathrow, Gatwick, Stansted, Luton, and London City), total passenger volume exceeded 165 million travelers in 2024, maintaining London's status as the busiest city airspace system in the world.</p>

            <h2 id="what-are-the-top-destinations-to-visit-in-london">What are the top destinations to visit in London?</h2>
            <p>London features an extraordinary collection of historic Royal palaces, national museums, and UNESCO heritage sites. Five of the most popular attractions include:</p>
            <ul role="list">
              <li><strong>The British Museum</strong>: Dedicated to human history, art, and culture, the Bloomsbury institution welcomes over 5.8 million visitors annually, housing treasures such as the Rosetta Stone and the Parthenon Sculptures.</li>
              <li><strong>The Tower of London</strong>: Founded by William the Conqueror in 1066, this historic fortress and UNESCO World Heritage site houses the Crown Jewels and attracts approximately 2.8 million visitors per year.</li>
              <li><strong>The River Thames and Waterfront Landmarks</strong>: The Thames flows past London's most historic sights, from the Houses of Parliament and Big Ben to Tower Bridge and Greenwich. Booking an undercover-tested <a href="/thames-river-cruises-london">Thames river cruise</a> between Westminster Pier and Greenwich provides the best vantage point for photographing the South Bank, the London Eye, and St Paul's Cathedral.</li>
              <li><strong>Tate Modern</strong>: Located in the repurposed Bankside Power Station on the south bank of the Thames, Britain's national museum of modern and contemporary art welcomes roughly 4.7 million visitors annually.</li>
              <li><strong>The National Gallery</strong>: Overlooking Trafalgar Square, this premier institution houses more than 2,300 Western European paintings dating from the mid-13th century to 1900, welcoming over 3.1 million visitors each year.</li>
            </ul>

            <h2 id="sources-and-methodology">Sources and methodology</h2>
            <ul role="list">
              <li><strong>Inbound International Visits, Nights and Expenditure</strong>: Sourced from the Office for National Statistics (<a href="https://www.ons.gov.uk/peoplepopulationandcommunity/leisureandtourism/bulletins/traveltrends/2023" rel="noopener" target="_blank">ONS</a>), International Passenger Survey (IPS) and annual <em>Travel trends</em> publications (2019 to 2024). Regional breakdown tables for London retrieved via the Greater London Authority (<a href="https://data.london.gov.uk/" rel="noopener" target="_blank">London Datastore</a>). Data accessed November 2026. Note that the United Kingdom is not included in Eurostat datasets after 2020.</li>
              <li><strong>Domestic Tourism and Day Visits</strong>: Sourced from <a href="https://www.visitbritain.org/" rel="noopener" target="_blank">VisitBritain</a>, Great Britain Tourism Survey (GBTS) for domestic overnight trips and Great Britain Day Visits Survey (GBDVS) for leisure day visits (2022, 2023, 2024). GBTS figures from 2022 onward represent official statistics in development under new survey methodology.</li>
              <li><strong>Heathrow Airport Statistics</strong>: Sourced from <a href="https://www.heathrow.com/company/investor-centre/reports/traffic-statistics" rel="noopener" target="_blank">Heathrow Airport Limited</a> investor centre traffic reports and annual passenger traffic releases (2019 to 2024).</li>
              <li><strong>Definitions</strong>: An inbound visit represents an international trip by an overseas resident that involves at least one night spent in London. Length of stay is calculated as total overseas visitor nights divided by overseas visits. Expenditure represents total spending in London by foreign visitors during their stay, excluding international airfares.</li>
            </ul>
            <div class="bpa-cite">
              <strong>Using these statistics?</strong> You are welcome to quote the figures and charts on this page. Please credit and link to <a href="/london-tourism-statistics">The Cruise Detective, London Tourism Statistics</a>.
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</div>
</main>

{COMMON_FOOTER_HTML}
{COMMON_SCRIPTS}
</body>
</html>
"""
    return html

def main():
    print("Generating city statistics articles...")
    pages = {
        os.path.join(BASE_DIR, "paris-tourism-statistics", "index.html"): get_paris_html(),
        os.path.join(BASE_DIR, "amsterdam-tourism-statistics", "index.html"): get_amsterdam_html(),
        os.path.join(BASE_DIR, "london-tourism-statistics", "index.html"): get_london_html()
    }

    for path, content in pages.items():
        # Check hard rule: ZERO em dashes
        em_dash_matches = [m.start() for m in re.finditer(r'—', content)]
        if em_dash_matches:
            raise ValueError(f"EM DASH DETECTED in {path} at character indices {em_dash_matches}!")
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Wrote {path} ({len(content)} bytes) - 0 em dashes found.")

    # Update sitemap.xml
    sitemap_path = os.path.join(BASE_DIR, "sitemap.xml")
    with open(sitemap_path, "r", encoding="utf-8") as f:
        sitemap = f.read()

    new_urls = [
        "https://www.thecruisedetective.com/paris-tourism-statistics",
        "https://www.thecruisedetective.com/amsterdam-tourism-statistics",
        "https://www.thecruisedetective.com/london-tourism-statistics"
    ]

    for url in new_urls:
        if url not in sitemap:
            entry = f"""  <url>
    <loc>{url}</loc>
    <lastmod>2026-11-13T00:00:00+00:00</lastmod>
    <xhtml:link rel="alternate" hreflang="en" href="{url}" />
    <xhtml:link rel="alternate" hreflang="x-default" href="{url}" />
  </url>
"""
            # Insert before </urlset>
            idx = sitemap.rfind("</urlset>")
            if idx != -1:
                sitemap = sitemap[:idx] + entry + sitemap[idx:]
                print(f"Added {url} to sitemap.xml")

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print("Sitemap updated.")

if __name__ == "__main__":
    main()
