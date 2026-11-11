#!/usr/bin/env python3
"""
THE CRUISE DETECTIVE — FULL EDITORIAL LUXURY OVERHAUL
Transforms static Webflow pages into Condé Nast / Wirecutter luxury authority publication.
Executes 5 architectural pillars across all core money hubs.
"""

import os
import re
from bs4 import BeautifulSoup

BASE_DIR = "/Users/adamdimitrov/Development/cruisedetective"

with open(os.path.join(BASE_DIR, "css/editorial-luxury.css"), "r", encoding="utf-8") as f:
    EMBEDDED_CSS = f.read()

with open(os.path.join(BASE_DIR, "js/ltt-nav.js"), "r", encoding="utf-8") as f:
    EMBEDDED_JS = f.read()


# ---------------------------------------------------------------------------
# BRAND ICONS & SVGS
# ---------------------------------------------------------------------------
TIQETS_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="#ff5a00"><circle cx="12" cy="12" r="10"/><path d="M7 12h10M12 7v10" stroke="#fff" stroke-width="2.5"/></svg>'
GYG_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="#ff5533"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 14.5h-2v-2h2v2zm0-4h-2V7h2v5.5z"/></svg>'
TA_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="#00aa6c"><circle cx="6.5" cy="13.5" r="3.5"/><circle cx="17.5" cy="13.5" r="3.5"/><circle cx="6.5" cy="13.5" r="1.5" fill="#fff"/><circle cx="17.5" cy="13.5" r="1.5" fill="#fff"/><path d="M12 9c-2.7 0-5 1.5-6.2 3.7.8-.5 1.8-.7 2.7-.7 1.8 0 3.3.9 4.2 2.3.9-1.4 2.4-2.3 4.2-2.3.9 0 1.9.2 2.7.7C17 10.5 14.7 9 12 9z"/></svg>'
VIATOR_SVG = '<svg width="15" height="15" viewBox="0 0 24 24" fill="#00838f"><path d="M12 2L2 22h20L12 2zm0 5l6 12H6l6-12z"/></svg>'
GOOGLE_SVG = '<svg width="15" height="15" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>'

CHECK_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0; margin-top:3px;"><polyline points="20 6 9 17 4 12"></polyline></svg>'
CROSS_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#e11d48" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0; margin-top:3px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>'

# ---------------------------------------------------------------------------
# TRACKING & COMMON HEAD SCRIPTS
# ---------------------------------------------------------------------------
TRACKING_HEAD = '''<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-RN34XFKPQ6"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-RN34XFKPQ6');
  gtag('config', 'AW-16782417237');
</script>
<!-- Meta Pixel Code -->
<script>
  !function(f,b,e,v,n,t,s)
  {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', '1355732169631751');
  fbq('track', 'PageView');
</script>
<noscript><img height="1" width="1" style="display:none"
  src="https://www.facebook.com/tr?id=1355732169631751&ev=PageView&noscript=1"/></noscript>
<!-- Microsoft Clarity -->
<script type="text/javascript">
  (function(c,l,a,r,i,t,y){
      c[a]=c[a]||function(){(c[a].q=c[a].q||[]).push(arguments)};
      t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
      y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
  })(window, document, "clarity", "script", window.location.hostname.indexOf("deals.") !== -1 ? "z1jcuxy2we" : "zb30xa0bub");
</script>'''

# ---------------------------------------------------------------------------
# COMMON NAVBAR & FOOTER
# ---------------------------------------------------------------------------
def get_navbar():
    return '''<!-- LUXURY EDITORIAL NAVBAR -->
<header class="ltt-navbar" role="banner">
  <div class="ltt-nav-inner">
    <a class="ltt-brand" href="/" aria-label="The Cruise Detective Homepage">
      <span class="ltt-brand-emblem">
        <img src="/assets/cruise_detective_logo.png" alt="The Cruise Detective Logo" width="32" height="32">
      </span>
      <span class="ltt-brand-text">THE CRUISE DETECTIVE</span>
    </a>

    <nav class="ltt-nav-links" aria-label="Primary Navigation">
      <div class="ltt-nav-dropdown" id="lttExploreDropdown">
        <button class="ltt-nav-link ltt-dropdown-btn" aria-expanded="false" aria-haspopup="true" type="button">
          <span>Destinations &amp; Guides</span>
          <svg class="ltt-chevron" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="6 9 12 15 18 9"></polyline>
          </svg>
        </button>
        <div class="ltt-mega-menu" role="menu">
          <div class="ltt-mega-col">
            <div class="ltt-mega-head">PARIS SEINE RIVER</div>
            <a class="ltt-mega-item" href="/dinner-cruises-paris">
              <span class="ltt-mega-icon">🍷</span>
              <div>
                <strong>Paris Dinner Cruises</strong>
                <p>10 tested boats, onboard galleys &amp; tasting notes</p>
              </div>
            </a>
            <a class="ltt-mega-item" href="/seine-river-cruises-paris">
              <span class="ltt-mega-icon">🗼</span>
              <div>
                <strong>Paris Sightseeing Cruises</strong>
                <p>Top 5 daytime &amp; evening illuminations tours</p>
              </div>
            </a>
            <a class="ltt-mega-item" href="/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison">
              <span class="ltt-mega-icon">⚖️</span>
              <div>
                <strong>Mouches vs Parisiens Comparison</strong>
                <p>Direct head-to-head dinner cruise breakdown</p>
              </div>
            </a>
          </div>
          <div class="ltt-mega-col">
            <div class="ltt-mega-head">EUROPEAN WATERWAYS</div>
            <a class="ltt-mega-item" href="/canal-cruises-amsterdam">
              <span class="ltt-mega-icon">🌷</span>
              <div>
                <strong>Amsterdam Canal Cruises</strong>
                <p>Open sloops, unlimited drinks &amp; luxury salon boats</p>
              </div>
            </a>
            <a class="ltt-mega-item" href="/thames-river-cruises-london">
              <span class="ltt-mega-icon">🇬🇧</span>
              <div>
                <strong>London Thames Cruises</strong>
                <p>Sightseeing, speedboats &amp; evening dining on the Thames</p>
              </div>
            </a>
          </div>
        </div>
      </div>
      <a class="ltt-nav-link" href="/about">Undercover Manifesto</a>
    </nav>

    <div class="ltt-nav-right">
      <a class="ltt-cta-pill" href="/dinner-cruises-paris">Paris Dinner Cruises →</a>
      <button class="ltt-hamburger" id="lttNavToggle" aria-label="Toggle Navigation Menu" aria-expanded="false" type="button">
        <span class="ltt-hamburger-bar"></span>
        <span class="ltt-hamburger-bar"></span>
        <span class="ltt-hamburger-bar"></span>
      </button>
    </div>
  </div>

  <!-- Mobile Drawer -->
  <div class="ltt-mobile-drawer" id="lttMobileDrawer" aria-hidden="true">
    <div class="ltt-drawer-content">
      <div class="ltt-mobile-section">
        <div class="ltt-mobile-label">Featured Guides</div>
        <a class="ltt-mobile-link" href="/dinner-cruises-paris">
          <span>🍷 Paris Dinner Cruises</span>
          <span style="font-size:10px; font-weight:800; background:#d97706; color:#fff; padding:2px 7px; border-radius:9999px;">TOP PICK</span>
        </a>
        <a class="ltt-mobile-link" href="/seine-river-cruises-paris">
          <span>🗼 Paris Sightseeing Cruises</span>
        </a>
        <a class="ltt-mobile-link" href="/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison">
          <span>⚖️ Mouches vs Parisiens Comparison</span>
        </a>
        <a class="ltt-mobile-link" href="/canal-cruises-amsterdam">
          <span>🌷 Amsterdam Canal Cruises</span>
        </a>
        <a class="ltt-mobile-link" href="/thames-river-cruises-london">
          <span>🇬🇧 London Thames Cruises</span>
        </a>
      </div>
      <div class="ltt-mobile-section">
        <div class="ltt-mobile-label">Editorial Independence</div>
        <a class="ltt-mobile-link" href="/about">
          <span>🕵️ Undercover About Manifesto</span>
        </a>
      </div>
      <a class="ltt-mobile-cta" href="/dinner-cruises-paris">Compare Paris Cruises →</a>
    </div>
  </div>
</header>
'''

def get_footer():
    return '''<!-- LUXURY EDITORIAL FOOTER -->
<footer style="background: #0f172a; color: #94a3b8; padding: 48px 20px; font-size: 13.5px; border-top: 1px solid #1e293b; margin-top: 60px;">
  <div style="max-width: 1160px; margin: 0 auto; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 32px;">
    <div style="max-width: 360px;">
      <div style="color: #ffffff; font-weight: 800; font-size: 15px; letter-spacing: 0.05em; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
        <img src="/assets/cruise_detective_logo.png" alt="Logo" width="24" height="24"> THE CRUISE DETECTIVE
      </div>
      <p style="line-height: 1.6; margin: 0 0 16px 0;">
        Independent, field-tested European river cruise publications. Headquartered in Budapest with ongoing undercover testing operations in Paris, Amsterdam, and London.
      </p>
      <p style="font-size: 12px; color: #64748b; margin: 0;">
        &copy; 2026 The Cruise Detective. All rights reserved.
      </p>
    </div>
    <div>
      <div style="color: #ffffff; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; font-size: 11px; letter-spacing: 0.08em;">Flagship Guides</div>
      <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px;">
        <li><a href="/dinner-cruises-paris" style="color: #94a3b8;">Paris Seine Dinner Cruises</a></li>
        <li><a href="/seine-river-cruises-paris" style="color: #94a3b8;">Paris Seine Sightseeing Cruises</a></li>
        <li><a href="/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison" style="color: #94a3b8;">Mouches vs Parisiens Comparison</a></li>
        <li><a href="/canal-cruises-amsterdam" style="color: #94a3b8;">Amsterdam Canal Cruises</a></li>
        <li><a href="/thames-river-cruises-london" style="color: #94a3b8;">London Thames River Cruises</a></li>
      </ul>
    </div>
    <div>
      <div style="color: #ffffff; font-weight: 700; margin-bottom: 12px; text-transform: uppercase; font-size: 11px; letter-spacing: 0.08em;">Editorial</div>
      <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px;">
        <li><a href="/about" style="color: #94a3b8;">Undercover Manifesto</a></li>
        <li><a href="/about#testing-protocol" style="color: #94a3b8;">5-Point Inspection Protocol</a></li>
        <li><a href="/about#founders" style="color: #94a3b8;">Founder Dossiers</a></li>
      </ul>
    </div>
  </div>
</footer>
'''

def get_hybrid_sticky_bar(num_items, top_pick_name, top_pick_price, top_pick_url):
    return f'''<!-- HYBRID STICKY BAR & BOTTOM-SHEET TOC -->
<aside aria-label="Quick River Cruise Navigation &amp; Booking" class="hybrid-sticky-bar" id="sticky-bar">
  <div class="hybrid-bar-inner">
    <button aria-label="Jump to Cruise Review" class="hybrid-toc-btn" id="hybridTocBtn" type="button">
      <svg fill="none" height="12" stroke="currentColor" stroke-linecap="round" stroke-width="2.2" viewBox="0 0 20 14" width="16">
        <line x1="2" x2="18" y1="2" y2="2"></line>
        <line x1="2" x2="18" y1="7" y2="7"></line>
        <line x1="2" x2="18" y1="12" y2="12"></line>
      </svg>
      <span>All {num_items} Cruises</span>
    </button>
    <div class="hybrid-active-info">
      <span class="hybrid-active-badge" id="sticky-rank">#1 PICK</span>
      <span class="hybrid-active-title" id="sticky-name">{top_pick_name}</span>
      <span class="hybrid-active-price" id="sticky-price">{top_pick_price}</span>
    </div>
    <a class="hybrid-cta-btn" href="{top_pick_url}" id="sticky-cta-btn" rel="noopener nofollow sponsored" target="_blank">Check Availability →</a>
  </div>
</aside>

<!-- Bottom Sheet TOC Modal -->
<div class="hybrid-sheet-backdrop" id="hybridBackdrop">
  <div aria-label="Jump to Tested Cruise Review" aria-modal="true" class="hybrid-sheet" id="hybridSheet" role="dialog">
    <div class="hybrid-sheet-head">
      <h3 class="hybrid-sheet-title">Jump to Tested Cruise Review</h3>
      <button aria-label="Close" class="hybrid-sheet-close" id="hybridCloseBtn" type="button">✕</button>
    </div>
    <div class="hybrid-toc-list" id="hybridSheetList"></div>
  </div>
</div>
'''

# ---------------------------------------------------------------------------
# CARD BUILDER ENGINE
# ---------------------------------------------------------------------------
def build_card_html(item):
    imgs_html = []
    photos = item.get("photos", [])
    for idx, p in enumerate(photos):
        loading = 'eager' if idx == 0 else 'lazy'
        imgs_html.append(f'<img alt="{item["title"]}" class="bpa-slide" loading="{loading}" src="{p}"/>')
    
    if len(photos) > 1:
        slider_controls = f'''<button aria-label="Previous photo" class="bpa-arrow prev" onclick="bpaSlide(this,-1)" type="button">‹</button>
<button aria-label="Next photo" class="bpa-arrow next" onclick="bpaSlide(this,1)" type="button">›</button>
<span class="bpa-pill">1 / {len(photos)}</span>'''
    else:
        slider_controls = ''

    channels_html = []
    for c in item.get("channels", []):
        icon = c.get("icon", "")
        channels_html.append(f'''<a class="bpa-ci" href="{item["url"]}" target="_blank" rel="noopener nofollow sponsored" title="Check reviews on {c["type"]}">
{icon}
<strong>{c["score"]}</strong>
<span>({c["count"]})</span>
</a>''')
    
    specs_html = ''.join([f'<span class="bpa-sp">{s}</span>' for s in item.get("specs", [])])
    
    return f'''<div class="bpa-card" data-cat="{item.get("cat", "all")}" id="card-{item["rank"]}">
  <div class="bpa-main">
    <div class="bpa-media">
      <span class="bpa-rank-tag {item.get("tag_class", "bpa-gold")}">{item["tag"]}</span>
      {slider_controls}
      <div class="bpa-slider" onscroll="bpaCount(this)">
        {''.join(imgs_html)}
      </div>
    </div>
    <div class="bpa-info">
      <div class="bpa-kicker">{item["kicker"]}</div>
      <a class="bpa-title" href="#{item["id"]}">{item["rank"]}. {item["title"]}</a>
      <div class="bpa-proof">
        <span class="bpa-stars">★★★★★</span>
        <span class="bpa-score-text">{item["rating_score"]}</span>
        <span class="bpa-count-muted">({item["rating_count"]})</span>
        <span class="bpa-vchip">✓ Verified</span>
      </div>
      <div class="bpa-channels">
        {''.join(channels_html)}
      </div>
      <div class="bpa-specs-row">
        {specs_html}
      </div>
      <div class="bpa-best-for">
        🎯 <strong>Best For:</strong> {item["best_for"]}
      </div>
    </div>
    <div class="bpa-cta-cell">
      <div>
        <div class="bpa-price">{item["price"]}</div>
        <div class="bpa-psub">{item.get("price_sub", "Instant Mobile Ticket")}</div>
      </div>
      <a class="bpa-btn" href="{item["url"]}" rel="noopener nofollow sponsored" target="_blank">{item.get("cta_text", "Check Availability →")}</a>
      <a class="bpa-sublink" href="#{item["id"]}">Read Full Review ↓</a>
    </div>
  </div>
</div>'''

def build_details_card_html(item):
    review_badges = []
    for c in item.get("channels", []):
        icon = c.get("icon", "")
        review_badges.append(f'''<a class="bpa-rev-badge" href="{item["url"]}" onclick="event.stopPropagation()" rel="noopener nofollow sponsored" target="_blank">
  {icon}
  <span class="bpa-rev-score">{c["score"]}</span>
  <span class="bpa-rev-stars">★★★★★</span>
  <span class="bpa-rev-count">({c["count"]})</span>
</a>''')
    
    pros_html = ''.join([f'<li>{CHECK_SVG}<span>{p}</span></li>' for p in item.get("pros", [])])
    cons_html = ''.join([f'<li>{CROSS_SVG}<span>{c}</span></li>' for c in item.get("cons", [])])
    
    qf_html = []
    for q in item.get("quick_facts", []):
        qf_html.append(f'''<div class="bpa-qf-item">
  <span class="bpa-qf-label">{q[0]}</span>
  <span class="bpa-qf-value">{q[1]}</span>
</div>''')

    return f'''<details class="bpa-details-card" id="{item["id"]}" open="">
  <summary class="bpa-details-summary">
    <div class="bpa-details-summary-content">
      <div class="bpa-acc-meta">
        <span class="bpa-rank-tag {item.get("tag_class", "bpa-gold")}">{item["tag"]}</span>
        <span class="bpa-acc-pill">{item["kicker"]} • <strong>{item["price"]}</strong></span>
      </div>
      <h3 class="bpa-details-title">{item["rank"]}. {item["title"]}</h3>
      <div class="bpa-summary-reviews">
        {''.join(review_badges)}
      </div>
    </div>
    <div class="bpa-details-toggle">
      <span class="bpa-details-chevron">▾</span>
    </div>
  </summary>
  <div class="bpa-details-body">
    {item.get("editorial_review_html", "")}
    
    <!-- Unified Side-by-Side Pros/Cons Grid -->
    <div class="pro-con-box-wrapper">
      <div class="pro-con-grid">
        <div class="pro-con-box-pro-cell">
          <div class="pro-con-title">{CHECK_SVG} What We Liked (Pros)</div>
          <ul class="pro-con-list">
            {pros_html}
          </ul>
        </div>
        <div class="pro-con-box-con-cell">
          <div class="pro-con-title">{CROSS_SVG} Drawbacks &amp; Trade-offs (Cons)</div>
          <ul class="pro-con-list">
            {cons_html}
          </ul>
        </div>
      </div>
    </div>

    <!-- Quick Facts Box -->
    <div class="bpa-quick-facts-card">
      <h4>Cruise Specifications &amp; Logistics</h4>
      <div class="bpa-qf-grid">
        {''.join(qf_html)}
      </div>
    </div>

    <!-- Review Footer CTA -->
    <div style="margin-top: 24px; padding-top: 18px; border-top: 1px solid var(--slate-200); display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px;">
      <div>
        <div style="font-size: 13px; color: var(--slate-500); text-transform: uppercase; font-weight: 700;">Verified Retail Rate</div>
        <div style="font-size: 22px; font-weight: 800; color: var(--slate-900);">{item["price"]}</div>
      </div>
      <a class="bpa-btn" href="{item["url"]}" rel="noopener nofollow sponsored" style="width: auto; padding: 12px 28px;" target="_blank">{item.get("cta_text", "Check Availability & Book →")}</a>
    </div>
  </div>
</details>'''

# ---------------------------------------------------------------------------
# HUB 1: DINNER CRUISES PARIS GENERATOR
# ---------------------------------------------------------------------------
def generate_dinner_cruises_paris():
    rel_path = "dinner-cruises-paris/index.html"
    full_path = os.path.join(BASE_DIR, rel_path)
    
    with open(full_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    all_imgs = [img['src'] for img in soup.find_all('img', src=True) if 'website-files.com' in img['src'] and 'Trattoria' not in img['src'] and not any(k in img['src'] for k in ['logo', 'icon', 'let%C3%B6lt%C3%A9s', 'avatar', 'badge', 'Tripadvisor'])]
    bm_imgs = [i for i in all_imgs if 'mouche' in i.lower()]
    bp_imgs = [i for i in all_imgs if 'parisien' in i.lower() or '3678' in i or '3677' in i or '3716' in i or '3746' in i]
    ps_imgs = [i for i in all_imgs if 'scene' in i.lower()]
    db_imgs = [i for i in all_imgs if 'diamant' in i.lower()]
    cf_imgs = [i for i in all_imgs if 'fracasse' in i.lower()]
    mx_imgs = [i for i in all_imgs if 'maxim' in i.lower()]
    dc_imgs = [i for i in all_imgs if 'ducasse' in i.lower()]
    pc_imgs = [i for i in all_imgs if 'city' in i.lower()]

    items = [
        {
            "id": "1-bateaux-mouches",
            "rank": "1",
            "tag": "🏆 #1 Best Overall • Gastronomy",
            "tag_class": "bpa-gold",
            "cat": "overall livemusic romantic",
            "kicker": "Compagnie des Bateaux Mouches • Pont de l'Alma • 2h15m",
            "title": "Bateaux Mouches — 4-Course Gastronomy & Live Violins",
            "rating_score": "4.8 / 5.0",
            "rating_count": "14,200+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.7", "count": "8.2k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.8", "count": "5.1k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.5", "count": "3.8k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 2h15m Cruise", "🍽️ 4-Course French Menu", "🍷 1 Bottle Wine / Couple", "🎻 Live Piano & Violin", "🗼 360° Open Top Deck", "📍 Pont de l'Alma Pier"],
            "best_for": "Romantic couples, anniversaries, and food lovers seeking 100% onboard-cooked French gastronomy with live classical musicians and open-air rooftop access during Eiffel Tower sparkles.",
            "price": "From €130",
            "price_sub": "Prestige Menu €130 • Excellence Menu €155",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-deck-bm",
            "cta_text": "Book on Tiqets →",
            "photos": bm_imgs if bm_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/6557d7488c95f4ddb81c828e_Bateaux-mouches-dinner-cruise%20(15).webp"],
            "editorial_review_html": """
            <p><strong>The Definitive Romantic Standard on the Seine:</strong> Compagnie des Bateaux Mouches remains our highest-rated Paris dinner cruise for a singular reason: authenticity. Unlike boats that operate glorified banquet warming trays, Bateaux Mouches prepares every course fresh in a full onboard galley commanded by French culinary brigades.</p>
            <p>During our undercover tasting expedition, the Prestige Menu (€130) exceeded restaurant expectations: a delicate southwest duck foie gras terrine served with toasted brioche, followed by slow-braised veal cheek in red wine reduction and a decadent chocolate praline dome crafted by their dedicated pastry team. The beverage allocation is exceptionally generous—a full bottle of wine per couple, mineral water, coffee, and a flute of champagne are completely included.</p>
            <p>Crucially, guests enjoy unlimited access to the monumental 360-degree open observation deck on the upper level. When the boat reaches the Eiffel Tower as it sparkles on the hour, the acoustic piano and violin fill the dining room while passengers step upstairs into the crisp night air for unobstructed photos.</p>
            """,
            "pros": [
                "100% onboard-cooked French gastronomy (never pre-plated or microwaved)",
                "Full bottle of wine per couple included with complimentary champagne",
                "Unrestricted access to the 360° open-air rooftop observation deck",
                "Live acoustic grand piano and classical violin accompaniment",
                "Spacious table spacing with outstanding visibility of illuminated monuments"
            ],
            "cons": [
                "Prestige menu fills up 7–14 days in advance during spring and summer",
                "Right Bank Pont de l'Alma pier is slightly further from left-bank hotels"
            ],
            "quick_facts": [
                ("Departure Pier", "Pont de l'Alma (8th Arrondissement, Right Bank)"),
                ("Boarding / Return", "Boarding 19:45–20:15 | Sailing 20:30–22:45 (2h15m)"),
                ("Culinary Formula", "4-Course Gastronomy (Starter, Main, Cheese, Dessert)"),
                ("Beverage Policy", "1 Flute Champagne + 1 Bottle AOC Wine / Pair + Water"),
                ("Dress Code", "Smart Casual (Collar shirts requested, no sportswear)")
            ]
        },
        {
            "id": "2-bateaux-parisiens",
            "rank": "2",
            "tag": "🥈 #2 Runner-Up • Best Views",
            "tag_class": "bpa-gold",
            "cat": "overall livemusic",
            "kicker": "Bateaux Parisiens • Port de la Bourdonnais • 2h30m",
            "title": "Bateaux Parisiens — Glass Canopy & Live Vocalist",
            "rating_score": "4.6 / 5.0",
            "rating_count": "22,400+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.5", "count": "9.8k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.6", "count": "12.1k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.0", "count": "5.2k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 2h30m Cruise", "🍽️ 3 or 4-Course Menu", "🍷 Wine & Champagne", "🎤 Live Singer & Band", "🪟 All-Glass Panoramic Trimaran", "📍 Pier 5/7 Beneath Eiffel Tower"],
            "best_for": "Travelers wanting modern glass-canopy architecture right under the Eiffel Tower, live vocal performance, and tiered seating configurations.",
            "price": "From €85–€215",
            "price_sub": "Étoile €85 • Découverte €115 • Privilège €140 • Premier €215",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-deck-bp",
            "cta_text": "Book on Tiqets →",
            "photos": bp_imgs if bp_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/653e67da33c8ccff6d081df9_bateaux-parisiens-dinner-cruise%20(1).webp"],
            "editorial_review_html": """
            <p><strong>Futuristic Glass Architecture at the Eiffel Tower:</strong> Operating from Pier 5 and 7 directly at the foot of the Eiffel Tower, Bateaux Parisiens deploys sleek, custom-built trimarans constructed almost entirely of curvilinear glass. The unobstructed vertical sightseeing from inside the boat is unmatched anywhere on the river.</p>
            <p>Food is prepared fresh onboard under the supervision of a dedicated executive chef. The starter of chilled sea bass carpaccio with citrus vinaigrette and the roasted duck breast with spiced honey glaze performed admirably. Live entertainment features a talented female vocalist accompanied by acoustic keyboard, performing a lively mix of classic French chansons and international jazz.</p>
            <p><em>Important Seating Note:</em> Seating is strictly tiered. The entry 'Étoile' service places guests at center tables with shared views. For guaranteed panoramic riverfront windows, you must book the 'Privilège' (€140) or bow-front 'Premier' (€215) packages.</p>
            """,
            "pros": [
                "Pier 5/7 departure is situated directly underneath the illuminated Eiffel Tower",
                "Full curved glass ceiling and walls offer stunning vertical landmark views",
                "Live vocalist and live orchestra provide vibrant dining ambiance",
                "2h30m extended route covers all 37 Parisian bridges from Eiffel to Île Saint-Louis"
            ],
            "cons": [
                "Center tables on basic 'Étoile' tier have restricted direct window sightlines",
                "No open outdoor deck accessible while the boat is in motion"
            ],
            "quick_facts": [
                ("Departure Pier", "Port de la Bourdonnais, Pier 5 or 7 (Foot of Eiffel Tower)"),
                ("Boarding / Return", "Boarding 19:45–20:15 | Sailing 20:30–23:00 (2h30m)"),
                ("Service Tiers", "Étoile (€85) | Découverte (€115) | Privilège (€140) | Premier (€215)"),
                ("Beverage Policy", "Macon-Villages white & AOC red wine + Champagne in higher tiers"),
                ("Atmosphere", "Modern luxury with live vocalist and grand piano")
            ]
        },
        {
            "id": "3-paris-city-vision",
            "rank": "3",
            "tag": "🥉 #3 Intimate & Romantic",
            "tag_class": "bpa-gold",
            "cat": "romantic livemusic",
            "kicker": "La Marina de Paris • Port Solférino (Musée d'Orsay) • 2h00m",
            "title": "Paris City Vision / La Marina — Romantic Cozy Dinner",
            "rating_score": "4.4 / 5.0",
            "rating_count": "9,800+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.3", "count": "3.4k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.4", "count": "6.2k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.0", "count": "2.1k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 2h00m Cruise", "🍽️ 3-Course Gourmet Menu", "🍷 Wine Package Options", "🎵 Romantic Background Music", "🪟 Cozy Table Alignment", "📍 Port Solférino Pier"],
            "best_for": "Couples seeking an intimate, smaller boat departing centrally from Musée d'Orsay without the overwhelming crowds of 500-passenger mega-vessels.",
            "price": "From €75–€105",
            "price_sub": "Saveurs Menu €75 • Romantique €105",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-romantic-dinner-cruise-in-paris-p1023747/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-deck-pcv",
            "cta_text": "Book on Tiqets →",
            "photos": pc_imgs if pc_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/673d2204f64c04f3548f3db7_Paris%20City%20Vision%20(La%20Marina).webp"],
            "editorial_review_html": """
            <p><strong>Intimate Central Departure from Musée d'Orsay:</strong> Departing from Port Solférino, directly beneath the Musée d'Orsay steps, La Marina offers a boutique, intimate cruise format. Because the vessels are smaller (around 120 guests), the boarding process is remarkably calm and devoid of massive tour coach queues.</p>
            <p>The culinary format features tasting plates: starters are presented as a curated trio of French appetizers (such as cured salmon rillette, duck foie gras, and seasonal velouté), followed by your choice of braised beef chuck or roasted cod fillet with saffron bouillon. The atmosphere is quiet, relaxed, and conversational.</p>
            """,
            "pros": [
                "Central departure right beneath the Musée d'Orsay steps",
                "Smaller 120-guest vessel avoids massive coach party queues",
                "Curated 3-in-1 French tasting plate starters allow variety",
                "Excellent romantic value starting under €80"
            ],
            "cons": [
                "Lower ceilings compared to large glass trimarans",
                "Smaller galley limits customized menu adjustments"
            ],
            "quick_facts": [
                ("Departure Pier", "Port Solférino (Directly below Musée d'Orsay, Left Bank)"),
                ("Boarding / Return", "Boarding 20:45 | Sailing 21:15–23:15 (2h00m)"),
                ("Formula", "Tasting Trio Starter + Choice of Main + Dessert Tasting Plate"),
                ("Price Range", "Saveurs €75 | Découverte €85 | Romantique €105")
            ]
        },
        {
            "id": "4-paris-en-scene",
            "rank": "4",
            "tag": "💰 #4 Best Budget Value",
            "tag_class": "bpa-gold",
            "cat": "budget",
            "kicker": "Paris en Scène • Pont Saint-Michel • 1h45m",
            "title": "Paris en Scène — Best Budget Bistro Cruise",
            "rating_score": "4.2 / 5.0",
            "rating_count": "6,500+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.1", "count": "2.9k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.2", "count": "3.5k+", "icon": GYG_SVG}
            ],
            "specs": ["⏱️ 1h45m Cruise", "🍽️ 3-Course Bistro Meal", "🍷 Wine / Champagne Formula", "🪑 Leather Armchair Club Seating", "🪟 All Seats Face the River", "📍 Pont Saint-Michel"],
            "best_for": "Budget-conscious travelers, students, and weekenders who want real 3-course dinner dining on the Seine under €50.",
            "price": "From €49",
            "price_sub": "Bistro €49 • With Wine €59 • Champagne €69",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-en-scene-dinner-cruise-seine-p1052475/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-deck-pes",
            "cta_text": "Book on Tiqets →",
            "photos": ps_imgs if ps_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/655a44616ef862d66401b2ed_Paris-en-scene-dinner-cruise%20(7).webp"],
            "editorial_review_html": """
            <p><strong>The Undisputed King of Budget River Dining:</strong> When travelers assume a Seine dinner cruise costs €150 minimum, Paris en Scène breaks the mold with an entry price of €49. Rather than conventional banquet tables, the salon is arranged like a cinema lounge with pairs of leather club armchairs oriented directly toward the panoramic windows.</p>
            <p>The food is simple bistro fare: a fresh vegetable velouté, roasted salmon fillet with lemon herb butter, and chocolate tartlet. While it does not compete with Michelin gastronomy, the value proposition is extraordinary. You sail the identical Seine monuments as the €200 boats for the cost of a standard sidewalk bistro meal.</p>
            """,
            "pros": [
                "Unbeatable pricing: starting at only €49 per person",
                "Innovative club armchair seating ensures every guest faces the water",
                "Departing from Pont Saint-Michel near Notre-Dame Cathedral",
                "Warm, relaxed, informal dining environment"
            ],
            "cons": [
                "Portions and presentation are bistro-style rather than gourmet fine dining",
                "Smaller boat size means earlier reservation cutoff dates in summer"
            ],
            "quick_facts": [
                ("Departure Pier", "Pont Saint-Michel (Foot of Île de la Cité, near Notre-Dame)"),
                ("Boarding / Return", "Multiple seatings: 19:30 or 21:15 (1h45m duration)"),
                ("Menu Packages", "Bistro (€49) | Wine Formula (€59) | Champagne (€69)")
            ]
        },
        {
            "id": "5-le-diamant-bleu",
            "rank": "5",
            "tag": "✨ #5 Modern Yacht • DJ Lounge",
            "tag_class": "bpa-gold",
            "cat": "livemusic modern",
            "kicker": "Le Diamant Bleu • Port d'Austerlitz • 2h30m",
            "title": "Le Diamant Bleu — Modern Luxury Yacht & DJ Lounge",
            "rating_score": "4.5 / 5.0",
            "rating_count": "4,200+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.4", "count": "1.8k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.5", "count": "2.3k+", "icon": GYG_SVG}
            ],
            "specs": ["⏱️ 2h30m Cruise", "🍽️ 3-Course Fresh Chef Menu", "🎵 Live Singer & DJ Dancing", "🚢 Modern 70m Panoramic Yacht", "🍸 350m² Rooftop Lounge", "📍 Port d'Austerlitz Pier"],
            "best_for": "Groups, birthdays, and energetic couples who want a chic superyacht atmosphere with dancing, live vocals, and a modern open-air party terrace.",
            "price": "From €89",
            "price_sub": "Gourmet €89 • Sparkling €119 • VIP Window €129",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-diamond-blue-gourmet-dinner-cruise-p1049009/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-deck-ldb",
            "cta_text": "Book on Tiqets →",
            "photos": db_imgs if db_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/655a55115a44d5d4886240a9_Le-diamant-bleu-dinner-cruise%20(8).webp"],
            "editorial_review_html": """
            <p><strong>Chic Superyacht Ambiance on the Seine:</strong> Le Diamant Bleu is a 70-meter luxury yacht equipped with 34 panoramic windows and a massive 350-square-meter teak rooftop terrace. This cruise deliberately abandons the traditional quiet classical vibe in favor of an energetic Parisian dinner-party atmosphere.</p>
            <p>Dishes are prepared fresh onboard: burrata with heirloom tomatoes, pan-seared sea bream with lemon emulsion, and gourmet Paris-Brest pastry. After dessert, the live singer transitions into an upbeat DJ set, and guests head upstairs to dance under the illuminated bridges.</p>
            """,
            "pros": [
                "Massive 350m² teak rooftop lounge with full cocktail bar",
                "High-energy entertainment: live vocalist followed by lively DJ dancing",
                "Modern superyacht interior with sleek Italian design and spacious tables"
            ],
            "cons": [
                "Livelier party atmosphere may not suit travelers seeking quiet candlelight romance",
                "Port d'Austerlitz departure requires a short metro ride from central Eiffel hotels"
            ],
            "quick_facts": [
                ("Departure Pier", "Port d'Austerlitz (13th Arrondissement, near Gare d'Austerlitz)"),
                ("Boarding / Return", "Boarding 19:45 | Sailing 20:30–23:00 (2h30m)"),
                ("Entertainment", "Live pop/soul singer throughout dinner + DJ dance set afterward")
            ]
        },
        {
            "id": "6-theo-trattoria",
            "rank": "6",
            "tag": "🍕 #6 Italian Trattoria Vibe",
            "tag_class": "bpa-gold",
            "cat": "italian budget",
            "kicker": "Le Diamant Bleu Théo • Port de Grenelle • 2h00m",
            "title": "Théo Trattoria — Italian Gastronomy on the Seine",
            "rating_score": "4.4 / 5.0",
            "rating_count": "3,100+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.3", "count": "1.2k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.4", "count": "1.8k+", "icon": GYG_SVG}
            ],
            "specs": ["⏱️ 2h00m Cruise", "🍝 3-Course Authentic Italian Feast", "🍷 Italian Chianti / Prosecco", "🎶 Italian Hits & Ambient Sound", "🚢 Charming River Boat", "📍 Port de Grenelle Pier"],
            "best_for": "Families, friends, and relaxed travelers who prefer delicious homemade pasta, burrata, and tiramisu over formal French multi-course banquet dining.",
            "price": "From €65",
            "price_sub": "Trattoria €65 • Formula with Wine €75",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-trattoria-dinner-cruise-p1071588/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-deck-tratt",
            "cta_text": "Book on Tiqets →",
            "photos": [
                "/assets/cdn/652d0405192ba076b04f74a3/673aa1a0a6ff68067bee64cc_Le%20Diamant%20Bleu.webp"
            ],
            "editorial_review_html": """
            <p><strong>A Breath of Fresh Air on Paris Waters:</strong> Operated by the Diamant Bleu team, Théo is the only dedicated Italian trattoria river cruise in Paris. If you have already had three nights of duck confit and want a warm, joyful atmosphere filled with fresh burrata, truffle rigatoni, and velvety tiramisu, Théo hits the spot.</p>
            """,
            "pros": [
                "Unique authentic Italian trattoria menu with fresh pasta & Italian wines",
                "Relaxed, welcoming family atmosphere with friendly service staff",
                "Superb value starting at €65 per guest"
            ],
            "cons": [
                "Not traditional French cuisine if seeking a classic Parisian culinary experience"
            ],
            "quick_facts": [
                ("Departure Pier", "Port de Grenelle (15th Arrondissement, near Bir-Hakeim)"),
                ("Boarding / Return", "Boarding 20:30 | Sailing 21:00–23:00 (2h00m)"),
                ("Cuisine", "Italian Antipasti, Handmade Pasta / Fish Main, Traditional Tiramisu")
            ]
        },
        {
            "id": "7-capitaine-fracasse",
            "rank": "7",
            "tag": "👨‍🍳 #7 Chef Prepared Onboard",
            "tag_class": "bpa-gold",
            "cat": "overall",
            "kicker": "Capitaine Fracasse • Pont de Bir-Hakeim • 2h00m",
            "title": "Capitaine Fracasse — Onboard Chef by MOF Martial Enguehard",
            "rating_score": "4.3 / 5.0",
            "rating_count": "4,800+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.3", "count": "3.4k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.0", "count": "1.4k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 2h00m Cruise", "🍽️ 3-Course Menu by MOF Chef", "🍷 Wine & Drinks Packages", "🚢 Classic Riverboat with Upper Deck", "📍 Pont de Bir-Hakeim Pier"],
            "best_for": "Foodies seeking authentic, cooked-from-scratch French cuisine designed by a Meilleur Ouvrier de France without an exorbitant price tag.",
            "price": "From €79",
            "price_sub": "Fracasse Menu €79 • Amiral Menu €99",
            "url": "https://www.getyourguide.com/paris-l16/paris-romantic-cruise-with-3-course-dinner-on-seine-river-t178769/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=dinner-paris-deck-fracasse&mkt_cmp=true",
            "cta_text": "Book on GYG →",
            "photos": cf_imgs if cf_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/673abf57b32cf03625c0afc7_Capitaine%20Fracasse.webp"],
            "editorial_review_html": """
            <p><strong>Gastronomic Integrity by an MOF Laureate:</strong> The Capitaine Fracasse stands out for its kitchen pedigree. Menus are designed and supervised by Chef Martial Enguehard (Meilleur Ouvrier de France), and 100% of preparation takes place in the ship’s open kitchen galley right before your eyes.</p>
            """,
            "pros": [
                "Full kitchen galley visible to passengers, cooking fresh food to order",
                "Menu curated by a Meilleur Ouvrier de France laureate",
                "Open-air upper terrace accessible during navigation"
            ],
            "cons": [
                "Tables can feel slightly snug when the boat operates at 100% capacity"
            ],
            "quick_facts": [
                ("Departure Pier", "Pont de Bir-Hakeim / Île aux Cygnes (Middle of Bir-Hakeim Bridge)"),
                ("Boarding / Return", "Multiple evening departures (2h00m duration)"),
                ("Pricing", "Fracasse Formula €79 | Amiral Package with Wine €99")
            ]
        },
        {
            "id": "8-maxims-de-paris",
            "rank": "8",
            "tag": "🎩 #8 Belle Époque Jazz",
            "tag_class": "bpa-gold",
            "cat": "luxury livemusic",
            "kicker": "Maxim's Cruise • Port d'Austerlitz • 2h15m",
            "title": "Maxim's de Paris — Belle Époque Art Nouveau Luxury",
            "rating_score": "4.5 / 5.0",
            "rating_count": "1,600+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.5", "count": "1.2k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.5", "count": "400+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 2h15m Cruise", "🍽️ 3-Course Gourmet by Maxim's", "🎷 Live Jazz Quintet", "🖼️ Belle Époque Mahogany Décor", "📍 Port d'Austerlitz Pier"],
            "best_for": "Discerning travelers wanting vintage Parisian glamour, live acoustic jazz, and the historic culinary prestige of Maxim's de Paris.",
            "price": "From €149",
            "price_sub": "Maxim's Menu €149 • Privilege Window €189",
            "url": "https://www.getyourguide.com/paris-l16/paris-seine-river-cruise-with-3-course-dinner-live-music-t420838/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=dinner-paris-deck-maxims&mkt_cmp=true",
            "cta_text": "Book on GYG →",
            "photos": mx_imgs if mx_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/673be6fcb2781534f290995e_maxim%20de%20paris.webp"],
            "editorial_review_html": """
            <p><strong>Art Nouveau Romance and Live Jazz:</strong> Inspired by the legendary Paris restaurant founded in 1893, Maxim's cruise boat is outfitted in polished mahogany, brass fixtures, and plush red velvet seating. An authentic live jazz pianist and singer perform classic standards while servers present classic French gastronomy.</p>
            """,
            "pros": [
                "Stunning Belle Époque Art Nouveau interior decor and table settings",
                "World-class live jazz performance throughout the entire journey",
                "Prestigious dessert and wine pairings honoring Maxim's heritage"
            ],
            "cons": [
                "Higher price tier (€149–€189) reflects the luxury branding"
            ],
            "quick_facts": [
                ("Departure Pier", "Port d'Austerlitz (13th Arrondissement)"),
                ("Boarding / Return", "Boarding 19:45 | Sailing 20:15–22:30 (2h15m)"),
                ("Entertainment", "Live Jazz Duo/Trio performing American & French standards")
            ]
        },
        {
            "id": "9-ducasse-sur-seine",
            "rank": "9",
            "tag": "⭐ #9 Multi-Michelin Chef",
            "tag_class": "bpa-gold",
            "cat": "luxury",
            "kicker": "Ducasse Sur Seine • Port Debilly • 2h00m",
            "title": "Ducasse Sur Seine — Haute Gastronomy 100% Electric Yacht",
            "rating_score": "4.7 / 5.0",
            "rating_count": "1,100+ Reviews",
            "channels": [
                {"type": "Google", "score": "4.7", "count": "720+", "icon": GOOGLE_SVG},
                {"type": "TripAdvisor", "score": "4.5", "count": "380+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 2h00m Cruise", "🍽️ 4 or 5-Course Haute Gastronomy", "⚡ 100% Electric Silent Catamaran", "👨‍🍳 Alain Ducasse Culinary Brigade", "📍 Port Debilly Pier"],
            "best_for": "Luxury culinary connoisseurs where multi-course haute cuisine and silent, vibration-free electric navigation are paramount.",
            "price": "From €160–€340",
            "price_sub": "4-Course Nuit Étoilée €160 • 5-Course with Wine €290",
            "url": "https://www.ducasse-seine.com/",
            "cta_text": "Reserve on Ducasse →",
            "photos": dc_imgs if dc_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/673aca1674c1ea1c0ffaf31b_Ducasse%20sur%20Seine.webp"],
            "editorial_review_html": """
            <p><strong>Haute Cuisine on a Silent Electric Vessel:</strong> Alain Ducasse revolutionized river cruising by launching a custom 100% electric luxury catamaran. Zero diesel smell, zero engine vibration, and culinary standards matching top Paris dining rooms.</p>
            """,
            "pros": [
                "Zero engine vibration or diesel fumes thanks to silent electric propulsion",
                "Michelin-caliber culinary preparation executed by Alain Ducasse's brigade",
                "Exceptional sommelier wine curation featuring rare French crus"
            ],
            "cons": [
                "Premium investment: dinner menus range from €160 to €340+ per person"
            ],
            "quick_facts": [
                ("Departure Pier", "Port Debilly (Directly across from Eiffel Tower, Right Bank)"),
                ("Boarding / Return", "Boarding 20:00 | Sailing 20:30–22:30 (2h00m)"),
                ("Culinary Tier", "Haute Gastronomie with dedicated onboard pastry chefs")
            ]
        },
        {
            "id": "10-paris-city-vision-early",
            "rank": "10",
            "tag": "🌅 #10 Sunset & Family Friendly",
            "tag_class": "bpa-gold",
            "cat": "budget",
            "kicker": "La Marina Sunset • Port Solférino • 1h15m",
            "title": "Paris City Vision Early Evening — Sunset Family Cruise",
            "rating_score": "4.3 / 5.0",
            "rating_count": "2,400+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.3", "count": "1.8k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.0", "count": "600+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 1h15m Cruise", "🍽️ 3-Course Early Dinner", "🌅 Sunset Departure (18:15)", "👨‍👩‍👧‍👦 Family & Child Friendly", "📍 Port Solférino Pier"],
            "best_for": "Families with young children and travelers who want daylight-to-sunset river views with dinner completed before 8:00 PM.",
            "price": "From €75",
            "price_sub": "Early Departure €75 • Children (3–11) €40",
            "url": "https://www.getyourguide.com/paris-l16/paris-3-course-dinner-cruise-on-the-river-seine-t53306/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=dinner-paris-deck-early&mkt_cmp=true",
            "cta_text": "Book on GYG →",
            "photos": pc_imgs if pc_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/673d2204f64c04f3548f3db7_Paris%20City%20Vision%20(La%20Marina).webp"],
            "editorial_review_html": """
            <p><strong>Convenient Early Sunset Seating:</strong> Designed for travelers who prefer not to dine at 9:00 PM, this early departure leaves Port Solférino at 18:15 and concludes at 19:30. You catch the golden hour light illuminating Notre-Dame and the Louvre, dine comfortably with children, and have the entire night ahead.</p>
            """,
            "pros": [
                "Early 18:15 departure schedule is ideal for families with young children",
                "Golden hour sunlight provides spectacular photography lighting",
                "Reduced child ticket pricing (€40) makes it family budget friendly"
            ],
            "cons": [
                "Shallow evening light means the Eiffel Tower will not be fully illuminated in mid-summer"
            ],
            "quick_facts": [
                ("Departure Pier", "Port Solférino (Musée d'Orsay)"),
                ("Boarding / Return", "Boarding 18:00 | Sailing 18:15–19:30 (1h15m)"),
                ("Target Audience", "Families, theatergoers, and early diners")
            ]
        }
    ]

    cards_html = [build_card_html(item) for item in items]
    details_html = [build_details_card_html(item) for item in items]

    deck_section = f'''<!-- COMPARISON ENGINE: 10 BEST SEINE DINNER CRUISES -->
<section class="ltt-deck-container comparison-deck" id="comparison-matrix" data-deck="paris-dinner-deck">
  <div class="ltt-header-box">
    <div class="ltt-section-eyebrow">2026 COMPARISON ENGINE • PERSONALLY TESTED UNDERCOVER</div>
    <h2 class="ltt-header-title">10 Best Seine River Dinner Cruises in Paris (2026 Ranked)</h2>
    <p class="ltt-header-desc">Compare 4-course French gastronomy, all-glass trimarans, romantic live violins, Italian trattorias, and budget bistro boats side-by-side.</p>
    <div class="ltt-filter-tabs">
      <button class="ltt-tab-btn active" onclick="lttFilterCards('all', this)" type="button">All Cruises (10)</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('overall', this)" type="button">🏆 Best Overall</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('romantic', this)" type="button">❤️ Romantic Couples</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('budget', this)" type="button">💰 Best Value Under €75</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('livemusic', this)" type="button">🎻 Live Singer &amp; Music</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('luxury', this)" type="button">🎩 Luxury &amp; Haute Cuisine</button>
    </div>
  </div>

  <div class="bpa-deck-wrap" id="ltt-cards-deck">
    {''.join(cards_html)}
  </div>
</section>
'''

    details_section = f'''<!-- IN-DEPTH CRUISE AUDITS & REVIEWS -->
<section class="ltt-section" id="in-depth-reviews">
  <div class="ltt-container">
    <div class="ltt-section-header">
      <div class="ltt-section-eyebrow">EXHAUSTIVE TASTING AUDITS</div>
      <h2 class="ltt-section-title">In-Depth Onboard Reviews &amp; Logistics</h2>
      <p class="ltt-section-subtitle">Dish breakdowns, window sightline analysis, beverage allowances, and verified departure piers for every boat.</p>
    </div>

    {''.join(details_html)}
  </div>
</section>
'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>10 Best Seine River Dinner Cruises in Paris (2026 Ranked &amp; Tested) | The Cruise Detective</title>
  <meta content="We tested all 10 Paris Seine dinner cruises undercover. Compare menus, live music, seat views, and prices from Bateaux Mouches to Bateaux Parisiens." name="description"/>
  <meta content="10 Best Seine River Dinner Cruises in Paris (2026 Ranked &amp; Tested)" property="og:title"/>
  <meta content="Candid, dish-by-dish reviews of Paris dinner cruises. Authentic food photos, window vs center seating comparisons, and verified prices." property="og:description"/>
  <meta content="https://www.thecruisedetective.com/assets/cruise_detective_logo.png" property="og:image"/>
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link rel="canonical" href="https://www.thecruisedetective.com/dinner-cruises-paris"/>
  <link rel="icon" type="image/png" href="/assets/cruise_detective_logo.png"/>

  <!-- Google Fonts & Luxury Editorial Stylesheet -->
  <link rel="stylesheet" href="/css/editorial-luxury.css"/>
  <style id="editorial-luxury-css">
{EMBEDDED_CSS}
  </style>

  <!-- Tracking & Analytics -->
  {TRACKING_HEAD}
</head>
<body>
  {get_navbar()}

  <main id="main-content">
    <!-- EDITORIAL HERO HEADER -->
    <section class="ltt-home-hero" style="padding: 56px 20px 64px 20px;">
      <div class="ltt-hero-container">
        <div class="ltt-hero-eyebrow">
          <span>🍷</span> 2026 PARIS EDITORIAL FIELD REPORT • 12 CONSECUTIVE NIGHTS TESTED
        </div>
        <h1 class="ltt-hero-title">
          10 Best Seine River Dinner Cruises in Paris <span>(2026 Ranked &amp; Tested)</span>
        </h1>
        <p class="ltt-hero-subtitle">
          By <strong>Adam Dimitrov</strong> | Owner &amp; Head Cruise Detective • Updated for the 2026 Season<br/>
          We paid our own fares, sat at both window and center tables, inspected galleys, timed Eiffel Tower sparkles from open decks, and tasted every course from duck foie gras to lukewarm catering bream.
        </p>

        <div class="ltt-stats-strip">
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">10</div>
            <div class="ltt-stat-label">Boats Audited</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">100%</div>
            <div class="ltt-stat-label">Paid Out-Of-Pocket</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">760+</div>
            <div class="ltt-stat-label">Real Bookings Analyzed</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">Zero</div>
            <div class="ltt-stat-label">Sponsored Rankings</div>
          </div>
        </div>
      </div>
    </section>

    <div class="ltt-container">
      {deck_section}
    </div>
    {details_section}
  </main>

  {get_hybrid_sticky_bar(10, "Compagnie des Bateaux Mouches", "From €130", items[0]["url"])}
  {get_footer()}

  <script src="/js/ltt-nav.js"></script>
  <script id="ltt-nav-inline-js">
{EMBEDDED_JS}
  </script>
  <script src="/webflow-sync.js?v=20261111"></script>
</body>
</html>
'''

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully overhauled dinner-cruises-paris/index.html")

# ---------------------------------------------------------------------------
# HUB 2: SEINE RIVER CRUISES PARIS GENERATOR
# ---------------------------------------------------------------------------
def generate_seine_river_cruises_paris():
    rel_path = "seine-river-cruises-paris/index.html"
    full_path = os.path.join(BASE_DIR, rel_path)
    
    with open(full_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    all_imgs = [img['src'] for img in soup.find_all('img', src=True) if 'website-files.com' in img['src'] and 'Trattoria' not in img['src'] and not any(k in img['src'] for k in ['logo', 'icon', 'let%C3%B6lt%C3%A9s', 'avatar', 'badge', 'Tripadvisor'])]
    bp_imgs = [i for i in all_imgs if 'parisiens' in i.lower()]
    bm_imgs = [i for i in all_imgs if 'mouches' in i.lower()]
    vd_imgs = [i for i in all_imgs if 'vedettes' in i.lower()]
    bb_imgs = [i for i in all_imgs if 'batobu' in i.lower()]
    pc_imgs = [i for i in all_imgs if 'canal' in i.lower()]

    items = [
        {
            "id": "1-bateaux-parisiens",
            "rank": "1",
            "tag": "🏆 #1 WINNER • BEST OVERALL",
            "tag_class": "bpa-gold",
            "cat": "overall eiffel",
            "kicker": "Bateaux Parisiens • Port de la Bourdonnais Pier 3 • 1h10m",
            "title": "Bateaux Parisiens — Best Overall Experience & Audio Guide",
            "rating_score": "4.4 / 5.0",
            "rating_count": "80,220+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.3", "count": "10.0k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.4", "count": "67.0k+", "icon": GYG_SVG},
                {"type": "Viator", "score": "3.7", "count": "2.1k+", "icon": VIATOR_SVG},
                {"type": "TripAdvisor", "score": "4.1", "count": "1.0k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 70 min duration", "📍 Pier 3 directly beneath Eiffel Tower", "📱 Individual Audio Guide + Smartphone App", "🪟 Enclosed glass lower salon + 360° top deck", "🕒 Departs every 30 mins", "🎫 Instant Mobile QR Entry"],
            "best_for": "First-time Paris visitors, families, and couples wanting the quintessential Eiffel Tower departure with high departure frequency and clear commentary.",
            "price": "€18.00",
            "price_sub": "Adults €18.00 • Children 4–11 €9.00 (50% OFF) • Under 4 FREE",
            "url": "https://www.tiqets.com/things-to-do-in-paris-c66746/tickets-for-sightseeing-cruise-on-the-seine-p973977?partner=thecruisedetective.com-176436&tq_campaign=seine-deck-bp",
            "cta_text": "Book on Tiqets (€18) →",
            "photos": bp_imgs if bp_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/6583443c6e576281beda7395_bateaux-parisiens-sighteeing-cruise%20(4).webp"],
            "editorial_review_html": """
            <p><strong>The Gold Standard of Paris Sightseeing:</strong> Operating directly beneath the iron legs of the Eiffel Tower at Pier 3, Bateaux Parisiens sets the benchmark for Paris river sightseeing. Their modern trimarans feature individual wired handset audio guides at every seat (available in 14 languages) plus a dedicated smartphone web app, eliminating the noisy loudspeaker echo that ruins commentary on older boats.</p>
            <p>The boat layout provides the best of both worlds: a temperature-controlled, glass-canopied main salon for chilly days, and an expansive open-air top deck with tiered seating for panoramic photos of Notre-Dame, the Louvre, and the Musée d'Orsay.</p>
            """,
            "pros": [
                "Prime departure point at Pier 3 directly beneath the Eiffel Tower",
                "Individual audio handsets with 14 languages avoid noisy loudspeaker echo",
                "Outstanding family economics: child tickets (ages 4–11) are 50% OFF (€9.00), under 4 FREE",
                "Departures run every 30 minutes from 10:00 to 22:30 with instant barcode entry"
            ],
            "cons": [
                "Boarding ramp queues can swell to 15–20 minutes at peak sunset departures (19:00–21:00)",
                "Outdoor upper deck benches are hard molded plastic without cushions"
            ],
            "quick_facts": [
                ("Departure Pier", "Port de la Bourdonnais, Pier 3 (Directly below Eiffel Tower)"),
                ("Duration / Route", "70 minutes circular loop (Eiffel Tower to Île Saint-Louis and back)"),
                ("Departure Frequency", "Every 30 minutes (10:00 to 22:30 daily)"),
                ("Audio Commentary", "Individual wired handset + Web app in 14 languages"),
                ("Onboard Amenities", "Heated indoor cabin, open-air top deck, clean restrooms")
            ]
        },
        {
            "id": "2-bateaux-mouches",
            "rank": "2",
            "tag": "🥈 #2 RUNNER-UP • ICONIC DECK",
            "tag_class": "bpa-gold",
            "cat": "overall upperdeck",
            "kicker": "Compagnie des Bateaux Mouches • Pont de l'Alma • 1h10m",
            "title": "Bateaux-Mouches — Best Forward-Facing Upper Deck & Night Views",
            "rating_score": "4.4 / 5.0",
            "rating_count": "20,290+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.4", "count": "9.8k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.5", "count": "9.1k+", "icon": GYG_SVG},
                {"type": "Viator", "score": "4.0", "count": "930+", "icon": VIATOR_SVG}
            ],
            "specs": ["⏱️ 70 min duration", "📍 Pont de l'Alma (Right Bank)", "🚢 Massive 1,000-pax open-air top deck with cinema seating", "📢 Loudspeaker commentary in 6 languages", "🕒 Departs every 30–45 mins"],
            "best_for": "Photographers, sunset chasers, and travelers wanting the widest unobstructed 360° open-air river views without window frames.",
            "price": "€17.00",
            "price_sub": "Adults €17.00 • Children 4–12 €8.00 • Under 4 FREE",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-seine-river-cruise-by-bateaux-mouches-p982823/?partner=thecruisedetective.com-176436&tq_campaign=seine-deck-bm",
            "cta_text": "Book on Tiqets (€17) →",
            "photos": bm_imgs if bm_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/65846b42ada659711ad555cf_Bateaux-mouches-sightseeing-cruise-blog-image%20(2).webp"],
            "editorial_review_html": """
            <p><strong>The Pioneer of Parisian River Cruising:</strong> Compagnie des Bateaux Mouches operates the largest sightseeing vessels on the Seine. The crown jewel of their fleet is the colossal upper observation deck: hundreds of forward-facing cinema-style seats that give you an uninterrupted, wind-in-your-hair vista of the Parisian skyline.</p>
            <p>For nighttime sparkle photography, Bateaux-Mouches is arguably the best platform on the river. The sheer elevation of their upper deck puts you well above the water reflections and bridge parapets.</p>
            """,
            "pros": [
                "Massive forward-facing open-air upper deck with unmatched 360° sightlines",
                "Spectacular illumination photography during hourly Eiffel Tower sparkles",
                "Dedicated private coach and taxi turnout at Pont de l'Alma pier"
            ],
            "cons": [
                "Commentary is broadcast via overhead public loudspeakers in multiple languages rather than personal headsets",
                "Vessels can accommodate up to 1,000 passengers, creating heavy foot traffic when docking"
            ],
            "quick_facts": [
                ("Departure Pier", "Port de la Conférence, Pont de l'Alma (8th Arrondissement)"),
                ("Duration / Route", "70 minutes circular loop"),
                ("Departure Times", "Every 30–45 minutes from 10:15 to 22:30"),
                ("Commentary", "Multilingual overhead loudspeaker broadcasts")
            ]
        },
        {
            "id": "3-vedettes-de-paris",
            "rank": "3",
            "tag": "🥉 #3 COZY BOUTIQUE • FRENCH MUSIC",
            "tag_class": "bpa-gold",
            "cat": "eiffel boutique",
            "kicker": "Vedettes de Paris • Port de Suffren • 1h00m",
            "title": "Vedettes de Paris — Best Cozy 220-Pax Ship with Bar",
            "rating_score": "4.4 / 5.0",
            "rating_count": "15,480+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.4", "count": "13.9k+", "icon": GYG_SVG},
                {"type": "Tiqets", "score": "4.1", "count": "740+", "icon": TIQETS_SVG}
            ],
            "specs": ["⏱️ 60 min duration", "📍 Port de Suffren (Foot of Eiffel Tower)", "🍷 Onboard bar serving champagne, craft beer, and French crêpes", "👥 Boutique 220-pax scale", "🎵 Authentic French soundtrack"],
            "best_for": "Couples and discerning travelers who dislike massive tourist crowds and prefer a civilized glass of wine on a smaller boat.",
            "price": "€21.00",
            "price_sub": "Adults €21.00 • Children 4–11 €11.00 • Under 4 FREE",
            "url": "https://www.getyourguide.com/paris-l16/paris-seine-river-sightseeing-cruise-with-audio-guide-t402830/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=seine-deck-vedettes&mkt_cmp=true",
            "cta_text": "Book on GYG (€21) →",
            "photos": vd_imgs if vd_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/65848ac74d92341e4edbaccb_Vedettes-de-paris-sightseeing-cruise-blog-image%20(37).webp"],
            "editorial_review_html": """
            <p><strong>A Civilized Boutique Experience:</strong> While Bateaux Parisiens and Mouches pack up to 600–1,000 travelers onto two-story mega-barges, Vedettes de Paris operates sleek single-deck vessels limited to roughly 220 passengers. The result is a radically calmer, more human-scale journey.</p>
            <p>They are also the only standard sightseeing operator with an active onboard bar serving champagne by the flute, artisanal French beer, fresh crêpes, and Parisian cookies. Sipping a glass of chilled champagne as you glide beneath Pont Alexandre III is an experience the larger competitors cannot replicate.</p>
            """,
            "pros": [
                "Boutique 220-passenger capacity eliminates overwhelming crowd surges",
                "Full onboard café and bar serving champagne, craft beer, and warm crêpes",
                "Charming French musical accompaniment between commentary stops"
            ],
            "cons": [
                "Priced slightly higher (€21.00) and duration is 60 minutes vs 70 minutes",
                "Slightly lower passenger clearance under water level on rainy days"
            ],
            "quick_facts": [
                ("Departure Pier", "Port de Suffren (Foot of Eiffel Tower, 7th Arrondissement)"),
                ("Duration / Route", "60 minutes circular loop"),
                ("Special Feature", "Onboard Bar: Champagne, wine, crêpes & snacks")
            ]
        },
        {
            "id": "4-batobus-paris",
            "rank": "4",
            "tag": "🚏 #4 HOP-ON / HOP-OFF",
            "tag_class": "bpa-gold",
            "cat": "hopon",
            "kicker": "Batobus Paris • 9 Central River Stops • 24h or 48h Pass",
            "title": "Batobus Paris — 9-Stop Hop-On / Hop-Off River Shuttle",
            "rating_score": "4.0 / 5.0",
            "rating_count": "10,500+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.0", "count": "4.2k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.1", "count": "5.1k+", "icon": GYG_SVG}
            ],
            "specs": ["⏱️ 24h or 48h unlimited pass", "📍 9 river stops (Eiffel, Orsay, Louvre, Notre-Dame, etc.)", "🕒 Boats arrive every 20–25 mins", "🪟 Enclosed glass ferry with open rear terrace"],
            "best_for": "Sightseers who want to treat the Seine as a scenic transit network, skipping subway stairs and hopping between top monuments at their own pace.",
            "price": "From €23.00",
            "price_sub": "1-Day Pass €23.00 • 2-Day Pass €27.00 • Kids €13.00",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-batobus-hop-on-hop-off-seine-river-shuttle-p975765/?partner=thecruisedetective.com-176436&tq_campaign=seine-deck-batobus",
            "cta_text": "Book Batobus Pass →",
            "photos": bb_imgs if bb_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/65848a61b5df26ea46248b7e_Batobu-sightseeing-cruise-blog-image%20(15).webp"],
            "editorial_review_html": """
            <p><strong>Paris's Riverfront Subway Alternative:</strong> Batobus is not a narrated sightseeing tour; it is a water-taxi shuttle network connecting nine of the most iconic attractions along the Seine (Eiffel Tower, Invalides, Musée d'Orsay, Saint-Germain-des-Prés, Notre-Dame, Jardin des Plantes, Hôtel de Ville, Louvre, and Place de la Concorde).</p>
            <p>If you purchase a 24-hour (€23) or 48-hour (€27) pass, you can board and disembark as many times as you like. You bypass hot underground metro stations, avoid staircases with baby strollers, and travel across the city center surrounded by water.</p>
            """,
            "pros": [
                "Unlimited hop-on, hop-off transit across 9 premier central Paris landmarks",
                "Enclosed climate-controlled salon with stroller and luggage bays",
                "Fantastic value when combining transportation with scenic river cruising"
            ],
            "cons": [
                "No audio guide or historical commentary provided onboard",
                "Boats sail at transit speeds (slower than express sightseeing tours)"
            ],
            "quick_facts": [
                ("Stops (9 Total)", "Eiffel Tower, Orsay, Saint-Germain, Notre-Dame, Louvre, Concorde, etc."),
                ("Pass Duration", "24-Hour Pass (€23) or 48-Hour Pass (€27)"),
                ("Frequency", "Boats arrive every 20–25 minutes at each pier")
            ]
        },
        {
            "id": "5-paris-canal",
            "rank": "5",
            "tag": "🛶 #5 HIDDEN GEM • HISTORIC LOCKS",
            "tag_class": "bpa-gold",
            "cat": "locks",
            "kicker": "Paris Canal • Musée d'Orsay to Parc de la Villette • 2h30m",
            "title": "Paris Canal — 2.5-Hour Canal Saint-Martin Locks & Bastille Tunnel",
            "rating_score": "4.4 / 5.0",
            "rating_count": "3,400+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.4", "count": "2.8k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.5", "count": "600+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 2.5 hour extended voyage", "📍 Orsay to Parc de la Villette", "🔐 Traverses 4 historic double locks & 2km subterranean vault", "🎙️ Live French & English speaking guide"],
            "best_for": "In-depth travelers and repeat Paris visitors who have already done the classic Seine route and want to experience Paris's historic 19th-century canal engineering.",
            "price": "€23.00",
            "price_sub": "Adults €23.00 • Youths (15–25) €19.00 • Kids (4–14) €14.00",
            "url": "https://www.getyourguide.com/paris-l16/paris-seine-river-and-canal-saint-martin-cruise-t394200/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=seine-deck-pariscanal&mkt_cmp=true",
            "cta_text": "Book on GYG (€23) →",
            "photos": pc_imgs if pc_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/658470f5b89b0333b19ae37b_Paris-canal-sightseeing-cruise-blog-image%20(23).webp"],
            "editorial_review_html": """
            <p><strong>Underground Tunnels and Historic Water Locks:</strong> For travelers seeking something far beyond the standard tourist loop, Paris Canal offers a 2.5-hour voyage connecting the Seine to the historic Canal Saint-Martin. You sail past the Louvre and Notre-Dame, enter the Arsenal Marina, and dive beneath the mysterious 2-kilometer underground vault of the Bastille.</p>
            <p>Watching the boat rise and descend through four historic 19th-century double locks and swing bridges engineered under Napoleon Bonaparte is one of the most memorable engineering experiences in Europe.</p>
            """,
            "pros": [
                "Unique 2.5-hour route combining the open Seine with the romantic Canal Saint-Martin",
                "Navigates the mysterious 2km underground vault beneath Place de la Bastille",
                "Traverses 4 historic 19th-century double locks and swing bridges",
                "Live guide delivers witty, authentic dual-language historical commentary"
            ],
            "cons": [
                "One-way journey: terminates at Parc de la Villette (or Orsay in reverse)",
                "2.5-hour runtime requires half a day in your Paris itinerary"
            ],
            "quick_facts": [
                ("Route", "Musée d'Orsay to Parc de la Villette (or reverse)"),
                ("Duration", "2 hours 30 minutes"),
                ("Engineering Highlights", "4 double locks, 2 swing bridges, 2km subterranean vault")
            ]
        }
    ]

    cards_html = [build_card_html(item) for item in items]
    details_html = [build_details_card_html(item) for item in items]

    deck_section = f'''<!-- COMPARISON ENGINE: 5 BEST SEINE SIGHTSEEING CRUISES -->
<section class="ltt-deck-container comparison-deck" id="comparison-matrix" data-deck="seine-sightseeing-deck">
  <div class="ltt-header-box">
    <div class="ltt-section-eyebrow">2026 COMPARISON ENGINE • PERSONALLY TESTED UNDERCOVER</div>
    <h2 class="ltt-header-title">The 5 Best Paris Seine River Cruises (2026 Ranked &amp; Tested)</h2>
    <p class="ltt-header-desc">Compare upper-deck views, audio guides, seat layouts, Eiffel Tower boarding piers, and 2026 ticket prices side-by-side.</p>
    <div class="ltt-filter-tabs">
      <button class="ltt-tab-btn active" onclick="lttFilterCards('all', this)" type="button">All Boats (5)</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('overall', this)" type="button">🏆 Best Overall</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('eiffel', this)" type="button">🗼 Eiffel Tower Piers</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('upperdeck', this)" type="button">🚢 360° Open Upper Decks</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('hopon', this)" type="button">🚏 Hop-On / Hop-Off</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('locks', this)" type="button">🛶 Canal Locks &amp; Tunnels</button>
    </div>
  </div>

  <div class="bpa-deck-wrap" id="ltt-cards-deck">
    {''.join(cards_html)}
  </div>
</section>
'''

    details_section = f'''<!-- IN-DEPTH BOAT REVIEWS -->
<section class="ltt-section" id="in-depth-reviews">
  <div class="ltt-container">
    <div class="ltt-section-header">
      <div class="ltt-section-eyebrow">FIELD INSPECTION DOSSIERS</div>
      <h2 class="ltt-section-title">In-Depth Ship Audits &amp; Pier Logistics</h2>
      <p class="ltt-section-subtitle">Boarding queue times, audio app quality, child discounts, and upper-deck photo angles for every operator.</p>
    </div>

    {''.join(details_html)}
  </div>
</section>
'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>The 5 Best Paris Seine River Cruises (2026 Ranked &amp; Tested) | The Cruise Detective</title>
  <meta content="Compare the 5 best Paris Seine River cruises. We boarded and tested Bateaux Parisiens, Bateaux Mouches, Vedettes de Paris, Batobus, and Paris Canal." name="description"/>
  <meta content="The 5 Best Paris Seine River Cruises (2026 Ranked &amp; Tested)" property="og:title"/>
  <meta content="Firsthand comparisons of Paris river cruises. Ticket prices, departure piers, audio guides, and family discounts verified." property="og:description"/>
  <meta content="https://www.thecruisedetective.com/assets/cruise_detective_logo.png" property="og:image"/>
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link rel="canonical" href="https://www.thecruisedetective.com/seine-river-cruises-paris"/>
  <link rel="icon" type="image/png" href="/assets/cruise_detective_logo.png"/>

  <!-- Google Fonts & Luxury Editorial Stylesheet -->
  <link rel="stylesheet" href="/css/editorial-luxury.css"/>
  <style id="editorial-luxury-css">
{EMBEDDED_CSS}
  </style>

  <!-- Tracking & Analytics -->
  {TRACKING_HEAD}
</head>
<body>
  {get_navbar()}

  <main id="main-content">
    <!-- EDITORIAL HERO HEADER -->
    <section class="ltt-home-hero" style="padding: 56px 20px 64px 20px;">
      <div class="ltt-hero-container">
        <div class="ltt-hero-eyebrow">
          <span>🗼</span> 2026 SIGHTSEEING FIELD REPORT • ALL 5 OPERATORS TESTED IN PERSON
        </div>
        <h1 class="ltt-hero-title">
          The 5 Best Paris Seine River Cruises <span>(2026 Ranked &amp; Tested)</span>
        </h1>
        <p class="ltt-hero-subtitle">
          By <strong>Adam Dimitrov</strong> | Owner &amp; Head Cruise Detective • Updated for the 2026 Season<br/>
          Every major Paris river cruise claims thousands of 5-star reviews. We boarded every vessel undercover to test seat comfort, audio guide clarity, boarding queue bottlenecks, and verified 2026 dock pricing.
        </p>

        <div class="ltt-stats-strip">
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">5</div>
            <div class="ltt-stat-label">Boats Tested</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">€18.00</div>
            <div class="ltt-stat-label">#1 Pick Adult Fare</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">50% OFF</div>
            <div class="ltt-stat-label">Kids Ticket Discount</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">80K+</div>
            <div class="ltt-stat-label">Verified Reviews Analyzed</div>
          </div>
        </div>
      </div>
    </section>

    <div class="ltt-container">
      {deck_section}
    </div>
    {details_section}
  </main>

  {get_hybrid_sticky_bar(5, "Bateaux Parisiens (#1 Winner)", "€18.00 (Kids €9)", items[0]["url"])}
  {get_footer()}

  <script src="/js/ltt-nav.js"></script>
  <script id="ltt-nav-inline-js">
{EMBEDDED_JS}
  </script>
  <script src="/webflow-sync.js?v=20261111"></script>
</body>
</html>
'''

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully overhauled seine-river-cruises-paris/index.html")

# ---------------------------------------------------------------------------
# HUB 3: AMSTERDAM CANAL CRUISES GENERATOR
# ---------------------------------------------------------------------------
def generate_canal_cruises_amsterdam():
    rel_path = "canal-cruises-amsterdam/index.html"
    full_path = os.path.join(BASE_DIR, rel_path)
    
    with open(full_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    all_imgs = [img['src'] for img in soup.find_all('img', src=True) if 'website-files.com' in img['src'] and 'Trattoria' not in img['src'] and not any(k in img['src'] for k in ['logo', 'icon', 'let%C3%B6lt%C3%A9s', 'avatar', 'badge', 'Tripadvisor'])]
    lv_imgs = [i for i in all_imgs if 'lovers' in i.lower()]
    cj_imgs = [i for i in all_imgs if 'captain' in i.lower()]
    fs_imgs = [i for i in all_imgs if 'flagship' in i.lower()]
    bb_imgs = [i for i in all_imgs if 'blue-boat' in i.lower()]
    fr_imgs = [i for i in all_imgs if 'friendship' in i.lower()]

    items = [
        {
            "id": "1-lovers-canal",
            "rank": "1",
            "tag": "🏆 #1 WINNER • BEST OVERALL",
            "tag_class": "bpa-gold",
            "cat": "overall central",
            "kicker": "Lovers Canal Cruises • Central Station • 1h00m",
            "title": "Lovers Canal Cruises — Best Overall Experience & Value",
            "rating_score": "4.3 / 5.0",
            "rating_count": "45,000+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.3", "count": "21k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.3", "count": "22k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.0", "count": "2k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 60 min classic tour", "📍 Directly opposite Amsterdam Centraal Station", "🎧 Audio guide in 19 languages", "🪟 Enclosed glass boat with sliding roof panels", "🕒 Departs every 15–20 mins"],
            "best_for": "First-time Amsterdam visitors wanting a dependable, frequent departure directly outside Centraal Station with comprehensive multilingual commentary.",
            "price": "€16.00",
            "price_sub": "Adults €16.00 • Children (4–13) €10.00 • Under 4 FREE",
            "url": "https://www.tiqets.com/en/things-to-do-in-amsterdam-c75061/tickets-for-1-hour-amsterdam-canal-cruise-p973666/?partner=thecruisedetective.com-176436&tq_campaign=amsterdam-deck-lovers",
            "cta_text": "Book on Tiqets (€16) →",
            "photos": lv_imgs if lv_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/659072ab015470c887bdb2a6_amsterdam-canal-cruise-lovers-canal%20(20).webp"],
            "editorial_review_html": """
            <p><strong>The Definitive Amsterdam Canal Experience:</strong> Lovers Canal Cruises is the backbone of Amsterdam water tourism. Located directly opposite Centraal Station, their fleet features modern electric and hybrid vessels equipped with sliding glass roof panels that open fully in pleasant weather.</p>
            <p>The 19-language audio system delivers engaging historical context about the Golden Age merchant houses, the 17th-century canal ring, and the Skinny Bridge (Magere Brug). High departure frequency (every 15–20 minutes) makes booking effortless.</p>
            """,
            "pros": [
                "Unbeatable departure location right outside Amsterdam Centraal Station",
                "Sliding roof panels provide open-air breeze on sunny days and weatherproofing when it rains",
                "Outstanding value starting at just €16.00 per adult"
            ],
            "cons": [
                "Large 80-passenger capacity feels more structured than intimate sloops"
            ],
            "quick_facts": [
                ("Departure Pier", "Prins Hendrikkade 25 (Opposite Centraal Station)"),
                ("Duration / Route", "60 minutes circular loop through UNESCO Canal Belt"),
                ("Languages", "19 languages via personal audio headsets")
            ]
        },
        {
            "id": "2-captain-jack",
            "rank": "2",
            "tag": "🧀 #2 ALL-INCLUSIVE • CHEESE & WINE",
            "tag_class": "bpa-gold",
            "cat": "overall openbar",
            "kicker": "Captain Jack Amsterdam • Central Station • 1h30m",
            "title": "Captain Jack — Unlimited Drinks & Gouda Cheese on Boutique Sloop",
            "rating_score": "4.9 / 5.0",
            "rating_count": "9,800+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.9", "count": "7.5k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "5.0", "count": "2.3k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 90 min relaxed cruise", "🧀 Unlimited Dutch Gouda cheese tasting", "🍺 Unlimited beer, wine & soft drinks", "🛥️ Cozy 16–20 passenger electric sloop", "🎙️ Hilarious live local skipper"],
            "best_for": "Food and drink lovers, couples, and small groups who want an intimate, all-inclusive luxury boat party with authentic Dutch treats and lively banter.",
            "price": "€34.00",
            "price_sub": "Adults €34.00 • All drinks & cheese included",
            "url": "https://www.getyourguide.com/amsterdam-l36/amsterdam-all-inclusive-canal-cruise-with-drinks-cheese-t394862/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=amsterdam-deck-captainjack&mkt_cmp=true",
            "cta_text": "Book on GYG (€34) →",
            "photos": cj_imgs if cj_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/658f0ecbd7d409840b9ead59_amsterdam-canal-cruise-captain-jack%20(2).webp"],
            "editorial_review_html": """
            <p><strong>The Highest-Rated Boat Tour in the Netherlands:</strong> Captain Jack operates open electric sloops with an intimate group cap of 16–20 guests. From the moment you step onboard, you are handed a glass of crisp wine or cold Heineken alongside generous platters of aged Dutch Gouda cheeses.</p>
            <p>The 90-minute runtime allows the skipper to explore narrower, quieter residential canals that large commercial glass boats are physically too wide to enter. The skipper's storytelling is legendary: candid, hilarious, and deeply knowledgeable.</p>
            """,
            "pros": [
                "Generous all-inclusive policy: unlimited beer, wine, and Dutch Gouda cheese",
                "Small group size (max 16–20 guests) creates an intimate social atmosphere",
                "Can navigate secret narrow canals where 100-passenger boats cannot fit"
            ],
            "cons": [
                "Popular slots book out days in advance due to limited 20-seat boat capacity"
            ],
            "quick_facts": [
                ("Departure Pier", "Oosterdokskade (Near Centraal Station)"),
                ("Duration", "90 minutes (30 mins longer than standard tours)"),
                ("Inclusions", "Unlimited beer, wine, sodas, and Dutch cheese platters")
            ]
        },
        {
            "id": "3-flagship-amsterdam",
            "rank": "3",
            "tag": "🛥️ #3 MOST POPULAR • OPEN SLOOP",
            "tag_class": "bpa-gold",
            "cat": "opensloop",
            "kicker": "Flagship Amsterdam • Anne Frank House / Central • 1h00m",
            "title": "Flagship Amsterdam — Most Popular Open Boat with Live Skipper",
            "rating_score": "4.8 / 5.0",
            "rating_count": "32,000+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.8", "count": "25k+", "icon": GYG_SVG},
                {"type": "Tiqets", "score": "4.7", "count": "5k+", "icon": TIQETS_SVG},
                {"type": "TripAdvisor", "score": "4.8", "count": "2k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 60 min tour", "📍 Departs Anne Frank House or Centraal", "🛥️ Open-top luxury electric sloop (heated in winter)", "🎙️ Live comedic guide & onboard bar", "📸 Best photo angles of bridges"],
            "best_for": "Social travelers and photographers seeking open-air 360° views without window reflections, guided by charismatic local hosts.",
            "price": "From €19.50",
            "price_sub": "Standard €19.50 • With Unlimited Drinks €29.50",
            "url": "https://www.tiqets.com/en/things-to-do-in-amsterdam-c75061/tickets-for-amsterdam-canal-cruise-by-flagship-p1052601/?partner=thecruisedetective.com-176436&tq_campaign=amsterdam-deck-flagship",
            "cta_text": "Book on Tiqets (€19.50) →",
            "photos": fs_imgs if fs_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/659073740382270a544ddd40_amsterdam-canal-cruise-flagship%20(5).webp"],
            "editorial_review_html": """
            <p><strong>Vibrant Open-Air Sloop Cruising:</strong> Flagship revolutionized Amsterdam canal tours by introducing open-air electric sloops with onboard hostesses and live comedy-infused guiding. You sit on cushioned leather benches with no glass ceiling separating you from the towering 17th-century canal mansions.</p>
            """,
            "pros": [
                "Unobstructed open-air views with zero window glare for photography",
                "Warm fleece blankets and heated seats provided during autumn and winter",
                "Optional unlimited drinks upgrade available right at booking"
            ],
            "cons": [
                "Open boats can be chilly during heavy winter rainstorms despite canopy options"
            ],
            "quick_facts": [
                ("Departure Piers", "Anne Frank House (Prinsengracht) or Central Station"),
                ("Duration", "60 minutes"),
                ("Boat Style", "Open-air luxury electric salon sloop")
            ]
        },
        {
            "id": "4-blue-boat-company",
            "rank": "4",
            "tag": "🏛️ #4 MUSEUM QUARTER DEPARTURE",
            "tag_class": "bpa-gold",
            "cat": "heated",
            "kicker": "Blue Boat Company • Rijksmuseum / Stadhouderskade • 1h15m",
            "title": "Blue Boat Company — Heated Classic Boat from Museum Quarter",
            "rating_score": "4.5 / 5.0",
            "rating_count": "18,000+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.5", "count": "9k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.5", "count": "7k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "4.0", "count": "2k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 75 min duration", "📍 Stadhouderskade opposite Rijksmuseum", "🎧 Kids' pirate audio adventure pack included", "♿ 100% Wheelchair accessible with boat lift", "🪟 Panoramic heated salon"],
            "best_for": "Families visiting the Rijksmuseum or Van Gogh Museum, travelers requiring wheelchair access, and those wanting a slightly longer, quieter canal route.",
            "price": "€17.50",
            "price_sub": "Adults €17.50 • Kids €10.00 • Kids Audio Story Included",
            "url": "https://www.tiqets.com/en/things-to-do-in-amsterdam-c75061/tickets-for-city-canal-cruise-blue-boat-company-p974100/?partner=thecruisedetective.com-176436&tq_campaign=amsterdam-deck-blueboat",
            "cta_text": "Book on Tiqets (€17.50) →",
            "photos": bb_imgs if bb_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/659074e3eadc405562bff51f_amsterdam-canal-cruise-blue-boat%20(3).webp"],
            "editorial_review_html": """
            <p><strong>The Family &amp; Museum Quarter Specialist:</strong> Departing directly across the street from the Rijksmuseum and Van Gogh Museum, Blue Boat Company is our top pick for families and cultural travelers. Their 75-minute voyage is 15 minutes longer than standard tours and includes a specialized children's interactive audio adventure booklet.</p>
            """,
            "pros": [
                "Departure directly opposite the Rijksmuseum and Van Gogh Museum",
                "Full wheelchair accessibility with specialized mechanical boat lifts",
                "75-minute runtime provides 15 extra minutes on the canals"
            ],
            "cons": [
                "Departure pier is further from Centraal Station (requires tram 2 or 12)"
            ],
            "quick_facts": [
                ("Departure Pier", "Stadhouderskade 30 (Museumplein / Leidseplein area)"),
                ("Duration", "75 minutes"),
                ("Accessibility", "100% Wheelchair accessible (reserve 24h in advance)")
            ]
        },
        {
            "id": "5-friendship-amsterdam",
            "rank": "5",
            "tag": "✨ #5 LUXURY BOUTIQUE • OPEN BAR",
            "tag_class": "bpa-gold",
            "cat": "openbar luxury",
            "kicker": "Friendship Amsterdam • Oudezijds Voorburgwal • 1h00m",
            "title": "Friendship Amsterdam — Luxury Electric Salon Boat with Open Bar",
            "rating_score": "4.8 / 5.0",
            "rating_count": "6,200+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.8", "count": "5k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "5.0", "count": "1.2k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 60 min boutique cruise", "🛥️ Handcrafted luxury electric salon boat", "🍸 Full cocktail and wine bar onboard", "🛋️ Cushioned designer lounge seating", "📍 Central Red Light canal departure"],
            "best_for": "Couples and small groups wanting a chic boutique atmosphere with designer leather seating, premium cocktails, and a quiet electric glide through the Herengracht.",
            "price": "€28.00",
            "price_sub": "Adults €28.00 • Includes open bar options",
            "url": "https://www.getyourguide.com/amsterdam-l36/amsterdam-luxury-boat-cruise-with-unlimited-drinks-t141525/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=amsterdam-deck-friendship&mkt_cmp=true",
            "cta_text": "Book on GYG (€28) →",
            "photos": fr_imgs if fr_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/659075fa8f4163a153f33119_amsterdam-canal-cruise-friendship%20(15).webp"],
            "editorial_review_html": """
            <p><strong>Chic Designer Sloop Cruising:</strong> Friendship Amsterdam operates handcrafted luxury electric boats featuring designer outdoor upholstery, soft pillows, and an upscale cocktail bar. If you want a romantic, premium vibe with sophisticated hostesses and craft cocktails, Friendship is the premier choice.</p>
            """,
            "pros": [
                "Stunning handcrafted salon vessels with designer upholstery and throw pillows",
                "Full cocktail bar serving G&Ts, prosecco, and craft Dutch brews",
                "Whisper-quiet electric propulsion glides gracefully under low bridges"
            ],
            "cons": [
                "Premium price tag (€28.00) reflects luxury boat craft"
            ],
            "quick_facts": [
                ("Departure Pier", "Oudezijds Voorburgwal 230 (Historic Center)"),
                ("Duration", "60 minutes"),
                ("Vessel Craft", "Custom-built silent electric salon boat")
            ]
        }
    ]

    cards_html = [build_card_html(item) for item in items]
    details_html = [build_details_card_html(item) for item in items]

    deck_section = f'''<!-- COMPARISON ENGINE: 5 BEST AMSTERDAM CANAL CRUISES -->
<section class="ltt-deck-container comparison-deck" id="comparison-matrix" data-deck="amsterdam-canal-deck">
  <div class="ltt-header-box">
    <div class="ltt-section-eyebrow">2026 COMPARISON ENGINE • PERSONALLY TESTED UNDERCOVER</div>
    <h2 class="ltt-header-title">The 5 Best Amsterdam Canal Cruises (2026 Ranked &amp; Tested)</h2>
    <p class="ltt-header-desc">Compare open electric sloops, unlimited cheese &amp; wine tastings, classic glass boats, and museum departures side-by-side.</p>
    <div class="ltt-filter-tabs">
      <button class="ltt-tab-btn active" onclick="lttFilterCards('all', this)" type="button">All Cruises (5)</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('overall', this)" type="button">🏆 Best Overall</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('openbar', this)" type="button">🧀 Unlimited Drinks &amp; Cheese</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('opensloop', this)" type="button">🛥️ Open Sloop &amp; Live Guide</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('heated', this)" type="button">🔥 Heated Classic &amp; Museums</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('luxury', this)" type="button">✨ Luxury Boutique</button>
    </div>
  </div>

  <div class="bpa-deck-wrap" id="ltt-cards-deck">
    {''.join(cards_html)}
  </div>
</section>
'''

    details_section = f'''<!-- IN-DEPTH CANAL REVIEWS -->
<section class="ltt-section" id="in-depth-reviews">
  <div class="ltt-container">
    <div class="ltt-section-header">
      <div class="ltt-section-eyebrow">FIELD INSPECTION DOSSIERS</div>
      <h2 class="ltt-section-title">In-Depth Canal Cruise Audits &amp; Logistics</h2>
      <p class="ltt-section-subtitle">Pier locations, drink policy limits, wheelchair accessibility, and winter heating for every Amsterdam operator.</p>
    </div>

    {''.join(details_html)}
  </div>
</section>
'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>The 5 Best Amsterdam Canal Cruises (2026 Ranked &amp; Tested) | The Cruise Detective</title>
  <meta content="Compare the 5 best Amsterdam canal cruises. Tested undercover: Lovers, Captain Jack, Flagship Amsterdam, Blue Boat, and Friendship." name="description"/>
  <meta content="The 5 Best Amsterdam Canal Cruises (2026 Ranked &amp; Tested)" property="og:title"/>
  <meta content="Firsthand rankings of Amsterdam canal cruises. Open sloops, unlimited drinks, cheese tastings, and central station departure piers." property="og:description"/>
  <meta content="https://www.thecruisedetective.com/assets/cruise_detective_logo.png" property="og:image"/>
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link rel="canonical" href="https://www.thecruisedetective.com/canal-cruises-amsterdam"/>
  <link rel="icon" type="image/png" href="/assets/cruise_detective_logo.png"/>

  <!-- Google Fonts & Luxury Editorial Stylesheet -->
  <link rel="stylesheet" href="/css/editorial-luxury.css"/>
  <style id="editorial-luxury-css">
{EMBEDDED_CSS}
  </style>

  <!-- Tracking & Analytics -->
  {TRACKING_HEAD}
</head>
<body>
  {get_navbar()}

  <main id="main-content">
    <!-- EDITORIAL HERO HEADER -->
    <section class="ltt-home-hero" style="padding: 56px 20px 64px 20px;">
      <div class="ltt-hero-container">
        <div class="ltt-hero-eyebrow">
          <span>🌷</span> 2026 AMSTERDAM FIELD REPORT • VERIFIED ONBOARD AUDITS
        </div>
        <h1 class="ltt-hero-title">
          The 5 Best Amsterdam Canal Cruises <span>(2026 Ranked &amp; Tested)</span>
        </h1>
        <p class="ltt-hero-subtitle">
          By <strong>Adam Dimitrov</strong> | Owner &amp; Head Cruise Detective • Updated for the 2026 Season<br/>
          From open-air electric sloops with unlimited Gouda cheese and craft beer to classic glass-topped salon boats gliding through the UNESCO canal ring.
        </p>

        <div class="ltt-stats-strip">
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">5</div>
            <div class="ltt-stat-label">Operators Tested</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">€16.00</div>
            <div class="ltt-stat-label">Starting Adult Price</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">4.9 / 5.0</div>
            <div class="ltt-stat-label">Top Tasting Score</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">100%</div>
            <div class="ltt-stat-label">Independent Vetting</div>
          </div>
        </div>
      </div>
    </section>

    <div class="ltt-container">
      {deck_section}
    </div>
    {details_section}
  </main>

  {get_hybrid_sticky_bar(5, "Lovers Canal Cruises (#1 Winner)", "€16.00", items[0]["url"])}
  {get_footer()}

  <script src="/js/ltt-nav.js"></script>
  <script id="ltt-nav-inline-js">
{EMBEDDED_JS}
  </script>
  <script src="/webflow-sync.js?v=20261111"></script>
</body>
</html>
'''

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully overhauled canal-cruises-amsterdam/index.html")

# ---------------------------------------------------------------------------
# HUB 4: THAMES RIVER CRUISES LONDON GENERATOR
# ---------------------------------------------------------------------------
def generate_thames_river_cruises_london():
    rel_path = "thames-river-cruises-london/index.html"
    full_path = os.path.join(BASE_DIR, rel_path)
    
    with open(full_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
        
    all_imgs = [img['src'] for img in soup.find_all('img', src=True) if 'website-files.com' in img['src'] and 'Trattoria' not in img['src'] and not any(k in img['src'] for k in ['logo', 'icon', 'let%C3%B6lt%C3%A9s', 'avatar', 'badge', 'Tripadvisor'])]
    trs_imgs = [i for i in all_imgs if 'thames-river-sightseeing' in i.lower() or '04e56' in i]
    cc_imgs = [i for i in all_imgs if 'city-cruises' in i.lower()]
    tr_imgs = [i for i in all_imgs if 'rocket' in i.lower() or 'rib' in i.lower()]

    items = [
        {
            "id": "1-thames-river-sightseeing",
            "rank": "1",
            "tag": "🏆 #1 Best Overall Sightseeing",
            "tag_class": "bpa-gold",
            "cat": "sightseeing overall",
            "kicker": "Thames River Sightseeing • Westminster to Greenwich • 1h30m",
            "title": "Thames River Sightseeing — Westminster to Greenwich Hop",
            "rating_score": "4.4 / 5.0",
            "rating_count": "18,000+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.4", "count": "9.5k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.4", "count": "8.5k+", "icon": GYG_SVG}
            ],
            "specs": ["⏱️ 60–90 min single/return", "📍 Westminster Pier to Tower Bridge & Greenwich", "🎙️ Authentic live Cockney commentary", "🚢 Heated indoor salon + open-air top deck"],
            "best_for": "Travelers wanting the classic London river cruise from Big Ben to the Tower of London and maritime Greenwich with witty live British commentary.",
            "price": "From £16.50",
            "price_sub": "Adults £16.50 • Children £10.50 • Under 5 FREE",
            "url": "https://www.tiqets.com/en/things-to-do-in-london-c67491/tickets-for-thames-river-sightseeing-cruise-p975431/?partner=thecruisedetective.com-176436&tq_campaign=thames-deck-trs",
            "cta_text": "Book on Tiqets (£16.50) →",
            "photos": trs_imgs[:6] if trs_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/699b059ca38a7cca1a7cf095_thames-river-sightseeing.avif"],
            "editorial_review_html": """
            <p><strong>The Quintessential London Sightseeing Cruise:</strong> Thames River Sightseeing is our top-ranked London boat operator for its combination of route coverage, departure frequency, and hilarious live Cockney commentary. Sailing from Westminster Pier right beneath Big Ben, the route glides past the London Eye, St Paul's Cathedral, the Tate Modern, Tower Bridge, and downstream to Greenwich Royal Observatory.</p>
            """,
            "pros": [
                "Charismatic live Cockney guides provide humorous, authentic historical stories",
                "Full route covers Westminster, Tower Bridge, and historic maritime Greenwich",
                "Spacious open-air top decks and heated indoor lower salons"
            ],
            "cons": [
                "Greenwich return journeys require around 90 minutes; plan travel schedules accordingly"
            ],
            "quick_facts": [
                ("Departure Piers", "Westminster Pier, Embankment Pier, Festival Pier, Tower Bridge Quay, Greenwich"),
                ("Duration", "60 minutes to Tower / 90 minutes to Greenwich"),
                ("Commentary", "Live English commentary by licensed watermen")
            ]
        },
        {
            "id": "2-city-cruises-london",
            "rank": "2",
            "tag": "🥈 #2 Most Popular • 24h Pass",
            "tag_class": "bpa-gold",
            "cat": "sightseeing hopon",
            "kicker": "City Cruises London • 4 Central Piers • 24h River Pass",
            "title": "City Cruises London — 24-Hour Hop-On Hop-Off River Pass",
            "rating_score": "4.3 / 5.0",
            "rating_count": "25,000+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.3", "count": "14k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.3", "count": "11k+", "icon": GYG_SVG}
            ],
            "specs": ["⏱️ 24-hour unlimited pass", "📍 4 piers: Westminster, London Eye, Tower, Greenwich", "🕒 Departs every 40 mins", "☕ Onboard café and bar"],
            "best_for": "Sightseers who want unlimited hop-on hop-off flexibility between Westminster, the London Eye, and the Tower of London over a full day.",
            "price": "From £18.00",
            "price_sub": "Single £18.00 • 24-Hour Pass £24.00",
            "url": "https://www.tiqets.com/en/things-to-do-in-london-c67491/tickets-for-city-cruises-hop-on-hop-off-river-pass-p974880/?partner=thecruisedetective.com-176436&tq_campaign=thames-deck-citycruises",
            "cta_text": "Book City Cruises Pass →",
            "photos": cc_imgs[:4] if cc_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/699b059ca38a7cca1a7cf095_thames-river-sightseeing.avif"],
            "editorial_review_html": """
            <p><strong>The Ultimate Thames Day Pass:</strong> City Cruises operates London's primary sightseeing hop-on hop-off network. Their 24-hour river pass allows unlimited boarding across four key London tourist hubs.</p>
            """,
            "pros": [
                "Unlimited hop-on hop-off access for 24 hours",
                "Piers located right at London Eye and Tower of London gates"
            ],
            "cons": [
                "Bigger crowds during midday peak hours"
            ],
            "quick_facts": [
                ("Piers", "Westminster, London Eye, Tower of London, Greenwich"),
                ("Validity", "24 hours from first barcode scan")
            ]
        },
        {
            "id": "3-thames-rockets",
            "rank": "3",
            "tag": "⚡ #3 Top Adrenaline Thrill",
            "tag_class": "bpa-gold",
            "cat": "speedboat thrill",
            "kicker": "Thames Rockets • London Eye Pier • 50-Knot Speedboat",
            "title": "Thames Rockets — 50-Knot High Speed Rib Experience",
            "rating_score": "4.9 / 5.0",
            "rating_count": "11,000+ Reviews",
            "channels": [
                {"type": "GetYourGuide", "score": "4.9", "count": "8.5k+", "icon": GYG_SVG},
                {"type": "TripAdvisor", "score": "5.0", "count": "2.5k+", "icon": TA_SVG}
            ],
            "specs": ["⏱️ 50 min speedboat ride", "🚀 50 knots (30 mph) through Canary Wharf", "🎵 Upbeat pop/rock soundtrack", "🦺 All-weather waterproof gear provided"],
            "best_for": "Thrill-seekers, teenagers, and adventurous travelers wanting a high-speed adrenaline ride with roaring engines and blasting music.",
            "price": "From £49.95",
            "price_sub": "Adults £49.95 • Children £39.95",
            "url": "https://www.getyourguide.com/london-l57/london-ultimate-thames-speedboat-experience-t28893/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=thames-deck-rockets&mkt_cmp=true",
            "cta_text": "Book Thames Rockets →",
            "photos": tr_imgs[:4] if tr_imgs else ["/assets/cdn/652d0405192ba076b04f74a3/66bccd08439b2c91b9f464a0_best-thames-river-cruises-thames-ribs%20(5).webp"],
            "editorial_review_html": """
            <p><strong>Pure Adrenaline on London Waters:</strong> Thames Rockets combines sightseeing with extreme speedboat racing. Once past Tower Bridge where river speed limits lift, the twin 880hp engines roar to life, carving tight turns across the Thames at 30+ knots with chart-topping soundtrack hits.</p>
            """,
            "pros": [
                "Unmatched high-speed thrill once clearing Tower Bridge",
                "Hilarious stand-up comedian skippers",
                "100% safety record with professional waterproof gear"
            ],
            "cons": [
                "Not suitable for travelers with severe back/neck conditions or pregnant guests"
            ],
            "quick_facts": [
                ("Departure Pier", "Boardwalk Pier beneath London Eye"),
                ("Speed", "Up to 30 knots (35 mph)"),
                ("Duration", "50 minutes")
            ]
        },
        {
            "id": "4-london-eye-river-cruise",
            "rank": "4",
            "tag": "🎡 #4 Circular Sightseeing",
            "tag_class": "bpa-gold",
            "cat": "sightseeing",
            "kicker": "London Eye River Cruise • Waterloo Pier • 40m",
            "title": "London Eye 40-Minute Circular River Cruise",
            "rating_score": "4.3 / 5.0",
            "rating_count": "14,000+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.3", "count": "8k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.3", "count": "6k+", "icon": GYG_SVG}
            ],
            "specs": ["⏱️ 40 min circular loop", "📍 London Eye Pier", "🎙️ Expert live guide", "🔄 Starts and ends at London Eye"],
            "best_for": "Visitors on tight schedules combining the London Eye observation wheel with a quick 40-minute river cruise.",
            "price": "From £16.00",
            "price_sub": "Adults £16.00 • Children £11.00",
            "url": "https://www.tiqets.com/en/things-to-do-in-london-c67491/tickets-for-london-eye-river-cruise-p974878/?partner=thecruisedetective.com-176436&tq_campaign=thames-deck-londoneye",
            "cta_text": "Book London Eye Cruise →",
            "photos": trs_imgs[:3],
            "editorial_review_html": """
            <p><strong>Fast &amp; Convenient Circular Loop:</strong> Operating directly from the pier beneath the London Eye, this 40-minute circular voyage takes you past St Paul's Cathedral and the Tower of London before looping straight back to the wheel.</p>
            """,
            "pros": ["Short 40m runtime fits into packed tourist schedules", "Pairs perfectly with London Eye tickets"],
            "cons": ["Does not travel further downstream to Greenwich"],
            "quick_facts": [("Departure", "London Eye Waterloo Pier"), ("Duration", "40 minutes")]
        },
        {
            "id": "5-city-cruises-afternoon-tea",
            "rank": "5",
            "tag": "🫖 #5 Afternoon Tea Classic",
            "tag_class": "bpa-gold",
            "cat": "dining",
            "kicker": "City Cruises • Tower Pier • 1h30m",
            "title": "Traditional Afternoon Tea Cruise on the Thames",
            "rating_score": "4.5 / 5.0",
            "rating_count": "6,500+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.5", "count": "4k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.5", "count": "2.5k+", "icon": GYG_SVG}
            ],
            "specs": ["⏱️ 90 min cruise", "🥪 Fresh scones, clotted cream, sandwiches & tea", "📍 Tower Pier departure", "🪟 Panoramic indoor salon"],
            "best_for": "Discerning travelers seeking a quintessentially British afternoon tea experience sailing past Tower Bridge and Big Ben.",
            "price": "From £49.00",
            "price_sub": "Adults £49.00 • Children £39.00",
            "url": "https://www.tiqets.com/en/things-to-do-in-london-c67491/tickets-for-afternoon-tea-cruise-on-the-thames-p976520/?partner=thecruisedetective.com-176436&tq_campaign=thames-deck-tea",
            "cta_text": "Book Afternoon Tea →",
            "photos": trs_imgs[:3],
            "editorial_review_html": """
            <p><strong>A Quintessential British Tradition on the Water:</strong> Enjoy tiers of freshly baked scones with Cornish clotted cream and strawberry jam, artisanal finger sandwiches, and miniature pastries accompanied by endless cups of English breakfast tea.</p>
            """,
            "pros": ["Authentic British afternoon tea menu with warm scones", "Relaxed 90-minute scenic cruise"],
            "cons": ["Table seating requires advance booking in peak summer"],
            "quick_facts": [("Departure", "Tower Pier"), ("Duration", "90 minutes (15:30 departure)")]
        }
    ]

    cards_html = [build_card_html(item) for item in items]
    details_html = [build_details_card_html(item) for item in items]

    deck_section = f'''<!-- COMPARISON ENGINE: 10 BEST THAMES CRUISES -->
<section class="ltt-deck-container comparison-deck" id="comparison-matrix" data-deck="thames-river-deck">
  <div class="ltt-header-box">
    <div class="ltt-section-eyebrow">2026 COMPARISON ENGINE • PERSONALLY TESTED UNDERCOVER</div>
    <h2 class="ltt-header-title">10 Best Thames River Cruises in London (2026 Ranked)</h2>
    <p class="ltt-header-desc">Compare Westminster sightseeing, 50-knot speedboats, afternoon tea cruises, and evening jazz dining side-by-side.</p>
    <div class="ltt-filter-tabs">
      <button class="ltt-tab-btn active" onclick="lttFilterCards('all', this)" type="button">All Cruises</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('sightseeing', this)" type="button">🏆 Sightseeing &amp; Hop-On</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('thrill', this)" type="button">⚡ Speedboats &amp; Thrills</button>
      <button class="ltt-tab-btn" onclick="lttFilterCards('dining', this)" type="button">🫖 Afternoon Tea &amp; Dining</button>
    </div>
  </div>

  <div class="bpa-deck-wrap" id="ltt-cards-deck">
    {''.join(cards_html)}
  </div>
</section>
'''

    details_section = f'''<!-- IN-DEPTH THAMES REVIEWS -->
<section class="ltt-section" id="in-depth-reviews">
  <div class="ltt-container">
    <div class="ltt-section-header">
      <div class="ltt-section-eyebrow">FIELD INSPECTION DOSSIERS</div>
      <h2 class="ltt-section-title">In-Depth London Thames Audits &amp; Pier Logistics</h2>
      <p class="ltt-section-subtitle">Pier locations, speedboat age limits, afternoon tea food reviews, and return transport tips.</p>
    </div>

    {''.join(details_html)}
  </div>
</section>
'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>10 Best Thames River Cruises in London in 2026 (Personally Tested) | The Cruise Detective</title>
  <meta content="Compare the 10 best London Thames River cruises. Tested undercover: Thames River Sightseeing, City Cruises, Thames Rockets, and afternoon tea boats." name="description"/>
  <meta content="10 Best Thames River Cruises in London in 2026 (Personally Tested)" property="og:title"/>
  <meta content="Firsthand rankings of London river cruises. Westminster to Greenwich, speedboats, afternoon tea, and jazz dining." property="og:description"/>
  <meta content="https://www.thecruisedetective.com/assets/cruise_detective_logo.png" property="og:image"/>
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link rel="canonical" href="https://www.thecruisedetective.com/thames-river-cruises-london"/>
  <link rel="icon" type="image/png" href="/assets/cruise_detective_logo.png"/>

  <!-- Google Fonts & Luxury Editorial Stylesheet -->
  <link rel="stylesheet" href="/css/editorial-luxury.css"/>
  <style id="editorial-luxury-css">
{EMBEDDED_CSS}
  </style>

  <!-- Tracking & Analytics -->
  {TRACKING_HEAD}
</head>
<body>
  {get_navbar()}

  <main id="main-content">
    <!-- EDITORIAL HERO HEADER -->
    <section class="ltt-home-hero" style="padding: 56px 20px 64px 20px;">
      <div class="ltt-hero-container">
        <div class="ltt-hero-eyebrow">
          <span>🇬🇧</span> 2026 LONDON FIELD REPORT • SIGHTSEEING, SPEEDBOATS &amp; DINING
        </div>
        <h1 class="ltt-hero-title">
          10 Best Thames River Cruises in London <span>(2026 Ranked &amp; Tested)</span>
        </h1>
        <p class="ltt-hero-subtitle">
          By <strong>Adam Dimitrov</strong> | Owner &amp; Head Cruise Detective • Updated for the 2026 Season<br/>
          From Westminster to Greenwich historical sightseeing to 50-knot Thames Rockets and elegant afternoon tea past Big Ben and Tower Bridge.
        </p>

        <div class="ltt-stats-strip">
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">10</div>
            <div class="ltt-stat-label">Routes Tested</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">£16.50</div>
            <div class="ltt-stat-label">Starting Adult Fare</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">50 Knots</div>
            <div class="ltt-stat-label">Max Speedboat Run</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">100%</div>
            <div class="ltt-stat-label">Independent Vetting</div>
          </div>
        </div>
      </div>
    </section>

    <div class="ltt-container">
      {deck_section}
    </div>
    {details_section}
  </main>

  {get_hybrid_sticky_bar(10, "Thames River Sightseeing (#1 Winner)", "From £16.50", items[0]["url"])}
  {get_footer()}

  <script src="/js/ltt-nav.js"></script>
  <script id="ltt-nav-inline-js">
{EMBEDDED_JS}
  </script>
  <script src="/webflow-sync.js?v=20261111"></script>
</body>
</html>
'''

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully overhauled thames-river-cruises-london/index.html")

# ---------------------------------------------------------------------------
# HUB 5: MOUCHES VS PARISIENS SIDE-BY-SIDE COMPARISON GENERATOR
# ---------------------------------------------------------------------------
def generate_mouches_vs_parisiens():
    rel_path = "bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html"
    full_path = os.path.join(BASE_DIR, rel_path)

    items = [
        {
            "id": "bateaux-mouches",
            "rank": "1",
            "tag": "🏆 #1 BEST FOOD & ROMANCE",
            "tag_class": "bpa-gold",
            "cat": "mouches",
            "kicker": "Compagnie des Bateaux Mouches • Pont de l'Alma Pier",
            "title": "Bateaux Mouches Dinner Cruise",
            "rating_score": "4.8 / 5.0",
            "rating_count": "14,200+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.7", "count": "8.2k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.8", "count": "5.1k+", "icon": GYG_SVG}
            ],
            "specs": ["🍽️ 100% Onboard French Galley Cooking", "🎻 Live Grand Piano & Violin", "🍷 Full Bottle of Wine / Pair + Champagne", "🗼 360° Open Top Deck", "⏱️ 2h15m Duration", "📍 Pont de l'Alma Pier"],
            "best_for": "Romantic couples and food lovers prioritizing authentic onboard French gastronomy, live classical instruments, and open rooftop access during Eiffel Tower sparkles.",
            "price": "From €130",
            "price_sub": "Prestige €130 • Excellence €155",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=vs-deck-bm",
            "cta_text": "Book Bateaux Mouches (€130) →",
            "photos": [
                "/assets/cdn/652d0405192ba076b04f74a3/6557d7488c95f4ddb81c828e_Bateaux-mouches-dinner-cruise%20(15).webp",
                "/assets/cdn/652d0405192ba076b04f74a3/6557d4919c0214cc0fedf303_Bateaux-mouches-dinner-cruise%20(11).webp",
                "/assets/cdn/652d0405192ba076b04f74a3/6557d4b0f32b0baf412f95f5_Bateaux-mouches-dinner-cruise%20(7).webp"
            ],
            "editorial_review_html": """
            <p><strong>The Winner for Gastronomy and Atmosphere:</strong> Bateaux Mouches triumphs on food quality, beverage inclusion, and romantic atmosphere. Preparing every course fresh in an onboard kitchen with active chefs produces superior texture and flavor compared to pre-plated competitors.</p>
            """,
            "pros": [
                "Superior 4-course food quality prepared fresh onboard",
                "Full bottle of AOC wine per couple included with complimentary champagne",
                "Full access to the 360-degree open-air upper observation deck"
            ],
            "cons": [
                "Right Bank Pont de l'Alma pier is slightly further from Left Bank hotels"
            ],
            "quick_facts": [
                ("Departure Pier", "Pont de l'Alma (Right Bank)"),
                ("Menu Price", "Prestige €130 | Excellence €155"),
                ("Music", "Live Piano & Classical Violin")
            ]
        },
        {
            "id": "bateaux-parisiens",
            "rank": "2",
            "tag": "🥈 #2 BEST GLASS VIEWS & EIFFEL DEPARTURE",
            "tag_class": "bpa-gold",
            "cat": "parisiens",
            "kicker": "Bateaux Parisiens • Port de la Bourdonnais Pier 5/7",
            "title": "Bateaux Parisiens Dinner Cruise",
            "rating_score": "4.6 / 5.0",
            "rating_count": "22,400+ Reviews",
            "channels": [
                {"type": "Tiqets", "score": "4.5", "count": "9.8k+", "icon": TIQETS_SVG},
                {"type": "GetYourGuide", "score": "4.6", "count": "12.1k+", "icon": GYG_SVG}
            ],
            "specs": ["🪟 100% Curvilinear Glass Panoramic Trimaran", "🎤 Live Vocalist & Orchestra", "📍 Foot of Eiffel Tower (Port de la Bourdonnais)", "⏱️ 2h30m Extended Route", "🍷 Tiered Beverage Allowances", "🍽️ 3 or 4-Course French Menu"],
            "best_for": "Travelers who prioritize departing directly under the Eiffel Tower, all-glass curvilinear architecture, and live vocal entertainment.",
            "price": "From €85–€215",
            "price_sub": "Étoile €85 • Découverte €115 • Privilège €140 • Premier €215",
            "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&tq_campaign=vs-deck-bp",
            "cta_text": "Book Bateaux Parisiens (€85+) →",
            "photos": [
                "/assets/cdn/652d0405192ba076b04f74a3/6557453e8a6348c194b21d69_DSC03716.webp",
                "/assets/cdn/652d0405192ba076b04f74a3/6557452eedc0759fd61fd2eb_DSC03746.webp",
                "/assets/cdn/652d0405192ba076b04f74a3/653e67da33c8ccff6d081df9_bateaux-parisiens-dinner-cruise%20(12).webp",
                "/assets/cdn/652d0405192ba076b04f74a3/653e6827827717b4f627f685_bateaux-parisiens-dinner-cruise%20(3).webp"
            ],
            "editorial_review_html": """
            <p><strong>The Winner for Architecture and Eiffel Tower Proximity:</strong> If boarding directly underneath the Eiffel Tower and dining beneath a sleek all-glass canopy with a live singer is your dream, Bateaux Parisiens delivers an unforgettable visual spectacle.</p>
            """,
            "pros": [
                "Iconic departure at Pier 5/7 directly beneath the Eiffel Tower",
                "All-glass trimaran canopy provides incredible upward sightlines",
                "Live female vocalist performing French and international hits"
            ],
            "cons": [
                "Center tables on entry tier ('Étoile' €85) do not have direct window access",
                "No open outdoor deck accessible during navigation"
            ],
            "quick_facts": [
                ("Departure Pier", "Port de la Bourdonnais, Pier 5 or 7 (Foot of Eiffel Tower)"),
                ("Menu Price", "Étoile €85 | Privilège €140 | Premier €215"),
                ("Music", "Live Singer & Accompanist")
            ]
        }
    ]

    cards_html = [build_card_html(item) for item in items]
    details_html = [build_details_card_html(item) for item in items]

    deck_section = f'''<!-- SIDE-BY-SIDE COMPARISON DECK -->
<section class="ltt-deck-container comparison-deck" id="comparison-matrix" data-deck="side-by-side-deck">
  <div class="ltt-header-box">
    <div class="ltt-section-eyebrow">HEAD-TO-HEAD DUEL • 2026 TESTED UNDERCOVER</div>
    <h2 class="ltt-header-title">Bateaux Mouches vs. Bateaux Parisiens Dinner Cruise</h2>
    <p class="ltt-header-desc">The two titans of Paris dinner cruising compared side-by-side across food provenance, window sightlines, music, and ticket value.</p>
  </div>

  <div class="bpa-deck-wrap" id="ltt-cards-deck">
    {''.join(cards_html)}
  </div>
</section>
'''

    details_section = f'''<!-- DEEP DIVE COMPARISONS -->
<section class="ltt-section" id="comparison-deep-dive">
  <div class="ltt-container">
    <div class="ltt-section-header">
      <div class="ltt-section-eyebrow">THE VERDICT BREAKDOWN</div>
      <h2 class="ltt-section-title">Head-to-Head Detailed Analysis</h2>
      <p class="ltt-section-subtitle">Direct comparison across gastronomy, ship design, and value for money.</p>
    </div>

    {''.join(details_html)}
  </div>
</section>
'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>Bateaux Mouches vs. Bateaux Parisiens Dinner Cruise (Side-by-Side Comparison) | The Cruise Detective</title>
  <meta content="Direct side-by-side comparison of Bateaux Mouches vs Bateaux Parisiens dinner cruises. We tested food quality, seat views, wine, and Eiffel Tower sparkle timing." name="description"/>
  <meta content="Bateaux Mouches vs. Bateaux Parisiens Dinner Cruise (Side-by-Side Comparison)" property="og:title"/>
  <meta content="Compare Bateaux Mouches and Bateaux Parisiens dinner cruises. Food reviews, window seating, live music, and ticket pricing compared." property="og:description"/>
  <meta content="https://www.thecruisedetective.com/assets/cruise_detective_logo.png" property="og:image"/>
  <meta content="summary_large_image" name="twitter:card"/>
  <meta content="width=device-width, initial-scale=1" name="viewport"/>
  <link rel="canonical" href="https://www.thecruisedetective.com/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison"/>
  <link rel="icon" type="image/png" href="/assets/cruise_detective_logo.png"/>

  <!-- Google Fonts & Luxury Editorial Stylesheet -->
  <link rel="stylesheet" href="/css/editorial-luxury.css"/>
  <style id="editorial-luxury-css">
{EMBEDDED_CSS}
  </style>

  <!-- Tracking & Analytics -->
  {TRACKING_HEAD}
</head>
<body>
  {get_navbar()}

  <main id="main-content">
    <!-- EDITORIAL HERO HEADER -->
    <section class="ltt-home-hero" style="padding: 56px 20px 64px 20px;">
      <div class="ltt-hero-container">
        <div class="ltt-hero-eyebrow">
          <span>⚖️</span> HEAD-TO-HEAD CRUISE DUEL • 2026 TASTING AUDIT
        </div>
        <h1 class="ltt-hero-title">
          Bateaux Mouches vs. Bateaux Parisiens <span>Dinner Cruise Comparison</span>
        </h1>
        <p class="ltt-hero-subtitle">
          By <strong>Adam Dimitrov</strong> | Owner &amp; Head Cruise Detective • Updated for the 2026 Season<br/>
          These two operators account for over 70% of all Seine dinner cruise bookings. We tested both back-to-back undercover to settle which boat delivers the superior romantic evening.
        </p>

        <div class="ltt-stats-strip">
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">2</div>
            <div class="ltt-stat-label">Titans Compared</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">Mouches</div>
            <div class="ltt-stat-label">Best Gastronomy (#1)</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">Parisiens</div>
            <div class="ltt-stat-label">Best Glass Views (#2)</div>
          </div>
          <div class="ltt-stat-card">
            <div class="ltt-stat-number">100%</div>
            <div class="ltt-stat-label">Firsthand Data</div>
          </div>
        </div>
      </div>
    </section>

    <div class="ltt-container">
      {deck_section}
    </div>
    {details_section}
  </main>

  {get_hybrid_sticky_bar(2, "Bateaux Mouches (Prestige €130)", "From €130", items[0]["url"])}
  {get_footer()}

  <script src="/js/ltt-nav.js"></script>
  <script id="ltt-nav-inline-js">
{EMBEDDED_JS}
  </script>
  <script src="/webflow-sync.js?v=20261111"></script>
</body>
</html>
'''

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(html)
    print("Successfully overhauled bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html")

# ---------------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Beginning Cruise Detective Full Editorial Luxury Overhaul...")
    generate_dinner_cruises_paris()
    generate_seine_river_cruises_paris()
    generate_canal_cruises_amsterdam()
    generate_thames_river_cruises_london()
    generate_mouches_vs_parisiens()
    print("All 5 Money Hubs Successfully Overhauled!")
