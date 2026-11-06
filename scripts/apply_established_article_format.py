#!/usr/bin/env python3
"""
Rebuilds Cruise Detective landing pages to follow the established article format
(Condé Nast Traveler / Wirecutter hybrid aesthetic + LuxuryTravelTester established architecture).

Full Editorial Architecture:
1. Luxury Editorial Navbar
2. Hero Header & Testing Protocol + Trust Strip
3. Interactive Comparison Deck (#ltt-cards-deck) with Category Filter Tabs
4. Intro Editorial Rich Text ("Are Paris Dinner Cruises Worth It?", "Itinerary & Landmark Sequence", "Video Guide")
5. Detailed Breakdown Top Bar with Expand All / Collapse All controls
6. In-Depth Field Reviews wrapped in <details open class="bpa-details-card">
   - Insider Tips (Sommelier / Pier Strategy)
   - Unified Luxury 2-Column Pros & Cons Grid
   - Full Firsthand Experiential Reviews
   - Dedicated Video Reviews (Responsive 16:9 Player)
   - Unfolded Detailed Breakdowns (Zero Height Clamps)
   - Full Course Menus (Prestige, Excellence, Courses, Pairings)
   - Quick Facts Specs Table
   - Meeting Point Logistics (Metro lines, Directions, Responsive Maps)
   - High-Converting Affiliate Conversion CTAs
7. Post-Review Editorial Buying Guide & Field Advice ("Tourist Traps vs Value", "Dress Code", "Seasons", "Photo Service", "Celebrations")
8. Hybrid Sticky Bar & Bottom-Sheet TOC
"""

import os, re, subprocess
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

# Load styles and scripts
with open(os.path.join(BASE_DIR, 'css', 'editorial-luxury.css')) as f:
    EMBEDDED_CSS = f.read()

with open(os.path.join(BASE_DIR, 'js', 'ltt-nav.js')) as f:
    EMBEDDED_JS = f.read()

def get_orig_soup(path):
    html = subprocess.check_output(['git', 'show', f'e43390f:{path}'], cwd=BASE_DIR).decode('utf-8', errors='ignore')
    return BeautifulSoup(html, 'html.parser')

def run_dinner_cruises():
    print("Rebuilding dinner-cruises-paris to follow established article format...")
    orig_soup = get_orig_soup('dinner-cruises-paris/index.html')
    
    # 1. Extract Intro Block
    h2_worth = orig_soup.find(lambda e: e.name == 'h2' and 'Worth It' in e.get_text())
    intro_div = BeautifulSoup(str(h2_worth.parent), 'html.parser') if h2_worth else None
    
    if intro_div:
        for ifr in intro_div.find_all('iframe'):
            src = ifr.get('src', '')
            p = ifr.parent
            if 'youtube' in src or 'tube.rvere.com' in src:
                p['class'] = ['responsive-video-wrap']
                p['style'] = ''
            elif 'google.com/maps' in src:
                p['class'] = ['google-maps']
                p['style'] = ''
        intro_content = str(intro_div)
    else:
        intro_content = ""

    # 2. Extract Post Guide Block
    h2_trap = orig_soup.find(lambda e: e.name == 'h2' and 'Tourist Traps' in e.get_text())
    post_div = BeautifulSoup(str(h2_trap.parent), 'html.parser') if h2_trap else None
    post_content = str(post_div) if post_div else ""

    # Load existing overhauled file
    with open(os.path.join(BASE_DIR, 'dinner-cruises-paris', 'index.html')) as f:
        curr_html = f.read()
    curr_soup = BeautifulSoup(curr_html, 'html.parser')

    navbar = str(curr_soup.find('header', class_='ltt-navbar'))
    hero = str(curr_soup.find('section', class_='ltt-home-hero'))
    deck = str(curr_soup.find('section', class_='ltt-deck-container'))
    sticky_bar = str(curr_soup.find('aside', class_='hybrid-sticky-bar'))
    backdrop = str(curr_soup.find('div', class_='hybrid-sheet-backdrop'))
    footer = str(curr_soup.find('footer', class_='ltt-footer'))

    # 3. Build Detailed Breakdown Reviews (All 10 Boats)
    boats_orig = orig_soup.find_all(class_='heading-33')
    
    boat_meta = [
        {"anchor": "1-bateaux-mouches", "rank": "1", "tag": "🏆 #1 Best Overall • Gastronomy", "pill": "Compagnie des Bateaux Mouches • Pont de l'Alma • 2h15m • From €130", "cta": "Book Bateaux Mouches (€130+) →", "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-bm", "scores": [("Tiqets", "4.7", "8.2k+"), ("GetYourGuide", "4.8", "5.1k+"), ("TripAdvisor", "4.5", "12.4k+")]},
        {"anchor": "2-bateaux-parisiens", "rank": "2", "tag": "🥈 #2 Runner-Up • Glass Canopy", "pill": "Bateaux Parisiens • Port de la Bourdonnais • 2h30m • From €85", "cta": "Book Bateaux Parisiens (€85+) →", "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-bp", "scores": [("Tiqets", "4.5", "9.8k+"), ("GetYourGuide", "4.6", "12.1k+")]},
        {"anchor": "3-paris-city-vision", "rank": "3", "tag": "🎶 #3 Best Live Vocals • Musée d'Orsay", "pill": "Paris Seine (La Marina) • Port Solférino • 2h00m • From €75", "cta": "Book Paris City Vision (€75+) →", "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-romantic-dinner-cruise-in-paris-p1023747/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-pcv", "scores": [("Tiqets", "4.4", "4.1k+"), ("GetYourGuide", "4.4", "6.2k+")]},
        {"anchor": "4-paris-en-scene", "rank": "4", "tag": "💰 #4 Best Budget Value", "pill": "Paris en Scène • Pont Saint-Michel • 1h45m • From €59", "cta": "Book Paris en Scène (€59+) →", "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-en-scene-dinner-cruise-seine-p1052475/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-pes", "scores": [("Tiqets", "4.2", "3.2k+"), ("GetYourGuide", "4.2", "4.8k+")]},
        {"anchor": "5-le-diamant-bleu", "rank": "5", "tag": "✨ #5 Modern Yacht • DJ Lounge", "pill": "Le Diamant Bleu • Port d'Austerlitz • 2h30m • From €89", "cta": "Book Le Diamant Bleu (€89+) →", "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-diamond-blue-gourmet-dinner-cruise-p1049009/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-ldb", "scores": [("Tiqets", "4.4", "1.8k+"), ("GetYourGuide", "4.5", "2.3k+")]},
        {"anchor": "6-theo-trattoria", "rank": "6", "tag": "🍕 #6 Italian Trattoria Vibe", "pill": "Le Diamant Bleu Théo • Port de Grenelle • 2h00m • From €65", "cta": "Book Théo Trattoria (€65+) →", "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-trattoria-dinner-cruise-p1071588/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-tratt", "scores": [("Tiqets", "4.3", "1.2k+")]},
        {"anchor": "7-capitaine-fracasse", "rank": "7", "tag": "👨‍🍳 #7 Chef MOF Cuisine", "pill": "Le Capitaine Fracasse • Île aux Cygnes • 2h00m • From €79", "cta": "Book Capitaine Fracasse (€79+) →", "url": "https://www.getyourguide.com/paris-l16/paris-romantic-cruise-with-3-course-dinner-on-seine-river-t178769/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=din-paris-det-fracasse&mkt_cmp=true", "scores": [("GetYourGuide", "4.3", "2.9k+")]},
        {"anchor": "8-maxims-de-paris", "rank": "8", "tag": "🎷 #8 Belle Époque Luxury & Jazz", "pill": "Maxim's de Paris • Port de Solférino • 2h15m • From €149", "cta": "Book Maxim's de Paris (€149+) →", "url": "https://www.getyourguide.com/paris-l16/paris-seine-river-cruise-with-3-course-dinner-live-music-t420838/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=din-paris-det-maxims&mkt_cmp=true", "scores": [("GetYourGuide", "4.6", "840+")]},
        {"anchor": "9-ducasse-sur-seine", "rank": "9", "tag": "⭐ #9 Michelin-Star Haute Gastronomy", "pill": "Ducasse Sur Seine • Port Debilly • 2h00m • From €160", "cta": "Check Availability →", "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&tq_campaign=din-paris-det-ducasse", "scores": [("GetYourGuide", "4.7", "510+")]},
        {"anchor": "10-paris-city-vision-early", "rank": "10", "tag": "🌅 #10 Sunset & Family Friendly", "pill": "Paris Seine Early Evening • Port Solférino • 1h15m • From €75", "cta": "Book Early Cruise (€75+) →", "url": "https://www.getyourguide.com/paris-l16/paris-3-course-dinner-cruise-on-the-river-seine-t53306/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=din-paris-det-early&mkt_cmp=true", "scores": [("GetYourGuide", "4.4", "1.9k+")]}
    ]

    details_cards = []

    for idx, b in enumerate(boats_orig):
        meta = boat_meta[idx]
        title_text = b.get_text(strip=True)
        parent = b.find_parent('div', class_='container') or b.find_parent('div', class_='w-container') or b.parent
        b_soup = BeautifulSoup(str(parent), 'html.parser')

        # 1. Sommelier Tip
        tip_el = b_soup.find(class_='cd-sommelier-tip')
        tip_html = str(tip_el) if tip_el else ''
        if tip_el:
            tip_el.decompose()

        # 2. Decompose heading-33 and deck card remnants
        for el in b_soup.find_all(class_=['heading-33', 'div-block-26', 'div-block-34', 'bpa-card', 'bpa-slider']):
            el.decompose()

        # 3. Decompose load-more buttons
        for el in b_soup.find_all(class_=['div-block-39']):
            el.decompose()

        # 4. Unwrap load-more-div to eliminate height clamps
        for el in b_soup.find_all(class_=['load-more-div']):
            el.unwrap()

        # 5. Extract Pros & Cons
        pro_el = b_soup.find(class_='pro-con-box-pro-cell-rich-text-block') or b_soup.find(class_='pro-con-box-pro-cell-3')
        con_el = b_soup.find(class_='pro-con-box-con-cell-rich-text-block') or b_soup.find(class_='pro-con-box-con-cell')

        pro_items = []
        con_items = []
        if pro_el:
            for p in pro_el.find_all(['p', 'li']):
                txt = p.get_text(strip=True).replace('Pros:', '').replace('✔️', '').strip()
                if txt and len(txt) > 3:
                    pro_items.append(txt)
        if con_el:
            for p in con_el.find_all(['p', 'li']):
                txt = p.get_text(strip=True).replace('Cons:', '').replace('❌', '').strip()
                if txt and len(txt) > 3:
                    con_items.append(txt)

        if not pro_items:
            fallback_pros = {
                5: ["Chic superyacht lounge vibe with high-energy modern party atmosphere", "Live female vocalist followed by post-dinner open-air DJ set", "Massive 350m² open teak rooftop terrace with full cocktail bar"],
                6: ["Unique Italian trattoria concept on the Seine with fresh pasta and antipasti", "Cozy, casual 120-guest boutique barge avoiding mega-vessel crowds", "Budget-friendly evening cruise starting at just €65"],
                7: ["Dishes designed by Meilleur Ouvrier de France (MOF) Martial Enguehard", "Prepared fresh onboard in a dedicated fully equipped floating galley", "Superb close-up views of the Statue of Liberty and Eiffel Tower"],
                8: ["Romantic Belle Époque art nouveau decor modeled after the legendary Paris restaurant", "Live pop-jazz trio (singer, pianist, violinist) performing all evening", "Intimate Parisian romance away from mass tourism coach groups"],
                9: ["100% electric yacht: silent, vibration-free navigation with zero diesel odor", "Cuisine designed by multi-Michelin-starred Chef Alain Ducasse", "Haute gastronomy and sommelier wine pairings at the highest culinary level"],
                10: ["Early 18:00 departure catches stunning golden-hour sunset light over the Seine", "Finishes by 19:15, ideal for families with young children or post-cruise theater", "Budget-friendly 3-course formula starting at €75"]
            }
            pro_items = fallback_pros.get(idx, ["High quality Seine river experience", "Reliable schedule and central boarding"])

        if not con_items:
            fallback_cons = {
                5: ["Rooftop terrace is locked during dining service and only opens after dessert", "Music is noticeably louder than classical dining cruises—not for quiet conversations"],
                6: ["Focuses strictly on Italian cuisine rather than traditional French gastronomy", "No open exterior rooftop terrace accessible during navigation"],
                7: ["Interior seating is somewhat compact during full weekend departures", "Dessert formula is fixed with limited alternatives for dietary changes"],
                8: ["Higher price point reflecting the premium Maxim's luxury heritage branding", "Departure pier at Port de Solférino requires a short walk from the metro"],
                9: ["Premium luxury pricing (from €160 to €300+) requires advance budgeting", "Formal dress code strictly enforced; sportswear not permitted"],
                10: ["Shorter duration (1h15m) compared to standard 2h to 2h30m dinner cruises", "Does not see the Eiffel Tower illuminate at night during summer months"]
            }
            con_items = fallback_cons.get(idx, ["Advance booking recommended during peak season"])

        old_pc = b_soup.find(class_=['grid-15', 'pro-con-box-wrapper-3', 'grid-28'])
        if old_pc:
            old_pc.decompose()
        for el in b_soup.find_all(class_=['pro-con-box-pro-cell-rich-text-block', 'pro-con-box-con-cell-rich-text-block', 'pro-con-box-pro-cell-3', 'pro-con-box-con-cell']):
            el.decompose()

        pro_li_html = "".join([f'<li><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:3px;"><polyline points="20 6 9 17 4 12"></polyline></svg><span>{t}</span></li>' for t in pro_items])
        con_li_html = "".join([f'<li><svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#dc2626" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:3px;"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg><span>{t}</span></li>' for t in con_items])

        pro_con_html = f'''
        <div class="pro-con-box-wrapper">
          <div class="pro-con-grid">
            <div class="pro-con-box-pro-cell">
              <div class="pro-con-title" style="color: #166534 !important;">PROS</div>
              <ul class="pro-con-list" style="list-style:none;padding:0;margin:12px 0 0 0;display:flex;flex-direction:column;gap:10px;">
                {pro_li_html}
              </ul>
            </div>
            <div class="pro-con-box-con-cell">
              <div class="pro-con-title" style="color: #991b1b !important;">CONS</div>
              <ul class="pro-con-list" style="list-style:none;padding:0;margin:12px 0 0 0;display:flex;flex-direction:column;gap:10px;">
                {con_li_html}
              </ul>
            </div>
          </div>
        </div>
        '''

        # 6. Responsive video & map embeds
        for ifr in b_soup.find_all('iframe'):
            src = ifr.get('src', '')
            p_div = ifr.parent
            if 'youtube' in src or 'tube.rvere.com' in src:
                if p_div and p_div.name == 'div':
                    p_div['class'] = ['responsive-video-wrap']
                    p_div['style'] = ''
            elif 'google.com/maps' in src:
                if p_div and p_div.name == 'div':
                    p_div['class'] = ['google-maps']
                    p_div['style'] = ''

        # 7. Clean up images
        for img in b_soup.find_all('img'):
            src = img.get('src', '')
            if 'Trattoria' in src:
                img['src'] = 'https://cdn.prod.website-files.com/652d0405192ba076b04f74a3/673aa1a0a6ff68067bee64cc_Le%20Diamant%20Bleu.webp'
            img['loading'] = 'lazy'

        # Score badges for summary
        score_badges_html = []
        for ch, sc, co in meta["scores"]:
            if ch == "Tiqets":
                svg = '<svg width="15" height="15" viewBox="0 0 24 24" fill="#ff5a00"><circle cx="12" cy="12" r="10"/><path d="M7 12h10M12 7v10" stroke="#fff" stroke-width="2.5"/></svg>'
            elif ch == "GetYourGuide":
                svg = '<svg width="15" height="15" viewBox="0 0 24 24" fill="#ff5533"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>'
            else:
                svg = '<svg width="15" height="15" viewBox="0 0 24 24" fill="#00aa6c"><circle cx="6.5" cy="13.5" r="3.5"/><circle cx="17.5" cy="13.5" r="3.5"/><path d="M12 4C7 4 3 8 3 8s4 4 9 4 9-4 9-4-4-4-9-4z"/></svg>'
            badge = f'''<a class="bpa-rev-badge" href="{meta['url']}" target="_blank" rel="noopener nofollow sponsored" onclick="event.stopPropagation()">
  {svg}
  <span class="bpa-rev-score">{sc}</span>
  <span class="bpa-rev-stars">★★★★★</span>
  <span class="bpa-rev-count">({co})</span>
</a>'''
            score_badges_html.append(badge)

        inner_body_content = str(b_soup)

        card_html = f'''
        <details class="bpa-details-card" id="{meta['anchor']}" open="">
          <summary class="bpa-details-summary">
            <div class="bpa-details-summary-content">
              <div class="bpa-acc-meta">
                <span class="bpa-rank-tag bpa-gold">{meta['tag']}</span>
                <span class="bpa-acc-pill">{meta['pill']}</span>
              </div>
              <h3 class="bpa-details-title">{title_text}</h3>
              <div class="bpa-summary-reviews">
                {''.join(score_badges_html)}
              </div>
            </div>
            <span class="bpa-details-chevron">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </span>
          </summary>
          <div class="bpa-details-body">
            {tip_html}
            {pro_con_html}
            <div class="w-richtext ltt-editorial-body">
              {inner_body_content}
            </div>
            <div style="margin-top: 32px; padding-top: 24px; border-top: 1px solid var(--slate-200);">
              <a class="bpa-btn" href="{meta['url']}" target="_blank" rel="noopener nofollow sponsored" style="max-width: 420px; margin: 0 auto; text-align: center;">
                {meta['cta']}
              </a>
            </div>
          </div>
        </details>
        '''
        details_cards.append(card_html)

    # 4. Assemble the Full Document
    full_html = f'''<!DOCTYPE html>
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

  <!-- Global Tracking & Analytics -->
  <script async="" src="https://www.googletagmanager.com/gtag/js?id=AW-16782417237"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'AW-16782417237');
    gtag('config', 'G-RN34XFKPQ6');
  </script>
  <script>
    !function(f,b,e,v,n,t,s)
    {{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?
    n.callMethod.apply(n,arguments):n.queue.push(arguments)}};
    if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
    n.queue=[];t=b.createElement(e);t.async=!0;
    t.src=v;s=b.getElementsByTagName(e)[0];
    s.parentNode.insertBefore(t,s)}}(window, document,'script',
    'https://connect.facebook.net/en_US/fbevents.js');
    fbq('init', '1355732169631751');
    fbq('track', 'PageView');
  </script>
  <noscript><img height="1" width="1" style="display:none"
    src="https://www.facebook.com/tr?id=1355732169631751&ev=PageView&noscript=1"
  /></noscript>
  <script type="text/javascript">
    (function(c,l,a,r,i,t,y){{
        c[a]=c[a]||function(){{(c[a].q=c[a].q||[]).push(arguments)}};
        t=l.createElement(r);t.async=1;t.src="https://www.clarity.ms/tag/"+i;
        y=l.getElementsByTagName(r)[0];y.parentNode.insertBefore(t,y);
    }})(window, document, "clarity", "script", "z1jcuxy2we");
  </script>
</head>
<body>
  {navbar}

  <main id="main-content">
    {hero}

    <!-- 1. COMPARISON DECK -->
    <div class="ltt-container">
      {deck}
    </div>

    <!-- 2. INTRO EDITORIAL RICH TEXT (ESTABLISHED ARTICLE FORMAT) -->
    <section class="ltt-section ltt-intro-section" id="editorial-intro">
      <div class="ltt-container">
        <div class="w-richtext ltt-editorial-body">
          {intro_content}
        </div>
      </div>
    </section>

    <!-- 3. DETAILED BREAKDOWN TOP BAR WITH CONTROLS -->
    <div class="ltt-container">
      <div class="bpa-breakdown-top-bar" id="breakdown-header">
        <div>
          <h2 class="bpa-breakdown-heading" id="paris-dinner-breakdown">Detailed Breakdown — 10 Best Seine River Dinner Cruises in Paris</h2>
          <p class="bpa-breakdown-sub">Personally field-tested • All reviews open by default • Click to collapse/expand</p>
        </div>
        <div class="bpa-acc-controls">
          <button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)" type="button">Expand All</button>
          <button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)" type="button">Collapse All</button>
        </div>
      </div>
    </div>

    <!-- 4. ALL 10 IN-DEPTH REVIEWS (UNFOLDED, ZERO HEIGHT CLAMPS) -->
    <div class="ltt-container" id="in-depth-reviews">
      {''.join(details_cards)}
    </div>

    <!-- 5. POST-REVIEW EDITORIAL BUYING GUIDE & FIELD ADVICE -->
    <section class="ltt-section ltt-post-guide" id="buying-guide">
      <div class="ltt-container">
        <div class="w-richtext ltt-editorial-body">
          {post_content}
        </div>
      </div>
    </section>
  </main>

  {sticky_bar}
  {backdrop}
  {footer}

  <script src="/js/ltt-nav.js"></script>
  <script id="ltt-nav-inline-js">
{EMBEDDED_JS}
  </script>
  <script src="/webflow-sync.js"></script>
</body>
</html>
'''

    out_path = os.path.join(BASE_DIR, 'dinner-cruises-paris', 'index.html')
    with open(out_path, 'w') as f:
        f.write(full_html)
    print(f"Successfully generated established format for dinner-cruises-paris ({len(full_html)} bytes)!")


def run_thames_cruises():
    print("Rebuilding thames-river-cruises-london to follow established article format...")
    orig_soup = get_orig_soup('thames-river-cruises-london/index.html')
    
    # Extract London Itinerary
    h2_itin = orig_soup.find(lambda e: e.name == 'h2' and 'Itinerary' in e.get_text())
    itin_div = BeautifulSoup(str(h2_itin.parent), 'html.parser') if h2_itin else None
    if itin_div:
        for ifr in itin_div.find_all('iframe'):
            p = ifr.parent
            if p and p.name == 'div':
                p['class'] = ['google-maps']
                p['style'] = ''
        itin_content = str(itin_div)
    else:
        itin_content = ""

    # Load existing file
    with open(os.path.join(BASE_DIR, 'thames-river-cruises-london', 'index.html')) as f:
        curr_html = f.read()
    curr_soup = BeautifulSoup(curr_html, 'html.parser')

    navbar = str(curr_soup.find('header', class_='ltt-navbar'))
    hero = str(curr_soup.find('section', class_='ltt-home-hero'))
    deck = str(curr_soup.find('section', class_='ltt-deck-container'))
    details_sec = str(curr_soup.find('section', id='in-depth-reviews'))
    sticky_bar = str(curr_soup.find('aside', class_='hybrid-sticky-bar'))
    backdrop = str(curr_soup.find('div', class_='hybrid-sheet-backdrop'))
    footer = str(curr_soup.find('footer', class_='ltt-footer'))

    # Replace section header with bpa-breakdown-top-bar
    breakdown_top_bar = '''
    <div class="ltt-container">
      <div class="bpa-breakdown-top-bar" id="breakdown-header">
        <div>
          <h2 class="bpa-breakdown-heading" id="london-thames-breakdown">Detailed Breakdown — 10 Best Thames River Cruises in London</h2>
          <p class="bpa-breakdown-sub">Personally field-tested • All reviews open by default • Click to collapse/expand</p>
        </div>
        <div class="bpa-acc-controls">
          <button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)" type="button">Expand All</button>
          <button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)" type="button">Collapse All</button>
        </div>
      </div>
    </div>
    '''

    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>10 Best Thames River Cruises in London (2026 Ranked &amp; Tested) | The Cruise Detective</title>
  <meta content="We tested all 10 London Thames river cruises undercover. Compare Westminster to Greenwich routes, speedboats, afternoon tea, and evening dining tours." name="description"/>
  <meta content="10 Best Thames River Cruises in London (2026 Ranked &amp; Tested)" property="og:title"/>
  <meta content="In-depth reviews of Thames river sightseeing, speedboat rides, and evening dining boats in London. Verified piers, ticket prices, and booking tips." property="og:description"/>
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

  <!-- Global Tracking & Analytics -->
  <script async="" src="https://www.googletagmanager.com/gtag/js?id=AW-16782417237"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', 'AW-16782417237');
    gtag('config', 'G-RN34XFKPQ6');
  </script>
</head>
<body>
  {navbar}

  <main id="main-content">
    {hero}

    <!-- 1. COMPARISON DECK -->
    <div class="ltt-container">
      {deck}
    </div>

    <!-- 2. INTRO EDITORIAL ITINERARY -->
    <section class="ltt-section ltt-intro-section" id="editorial-intro">
      <div class="ltt-container">
        <div class="w-richtext ltt-editorial-body">
          {itin_content}
        </div>
      </div>
    </section>

    <!-- 3. DETAILED BREAKDOWN TOP BAR WITH CONTROLS -->
    {breakdown_top_bar}

    <!-- 4. IN-DEPTH REVIEWS -->
    {details_sec}
  </main>

  {sticky_bar}
  {backdrop}
  {footer}

  <script src="/js/ltt-nav.js"></script>
  <script id="ltt-nav-inline-js">
{EMBEDDED_JS}
  </script>
  <script src="/webflow-sync.js"></script>
</body>
</html>
'''

    out_path = os.path.join(BASE_DIR, 'thames-river-cruises-london', 'index.html')
    with open(out_path, 'w') as f:
        f.write(full_html)
    print(f"Successfully generated established format for thames-river-cruises-london ({len(full_html)} bytes)!")


def unify_breakdown_bars_in_other_hubs():
    print("Unifying breakdown top bars across remaining hubs...")
    for hub, title, count in [
        ('seine-river-cruises-paris', '5 Best Seine River Cruises in Paris', 5),
        ('canal-cruises-amsterdam', '5 Best Amsterdam Canal Cruises', 5),
        ('bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison', 'Bateaux Mouches vs. Bateaux Parisiens Comparison', 2)
    ]:
        p = os.path.join(BASE_DIR, hub, 'index.html')
        with open(p) as f:
            c = f.read()

        # Update CSS block
        c = re.sub(r'<style id="editorial-luxury-css">.*?</style>', f'<style id="editorial-luxury-css">\n{EMBEDDED_CSS}\n  </style>', c, flags=re.DOTALL)
        # Update JS block
        c = re.sub(r'<script id="ltt-nav-inline-js">.*?</script>', f'<script id="ltt-nav-inline-js">\n{EMBEDDED_JS}\n  </script>', c, flags=re.DOTALL)

        # Replace ltt-section-header with bpa-breakdown-top-bar
        old_header = r'<div class="ltt-section-header">.*?</div>'
        new_header = f'''<div class="bpa-breakdown-top-bar" id="breakdown-header">
        <div>
          <h2 class="bpa-breakdown-heading">{title}</h2>
          <p class="bpa-breakdown-sub">Personally field-tested • All reviews open by default • Click to collapse/expand</p>
        </div>
        <div class="bpa-acc-controls">
          <button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)" type="button">Expand All</button>
          <button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)" type="button">Collapse All</button>
        </div>
      </div>'''
        c = re.sub(old_header, new_header, c, count=1, flags=re.DOTALL)

        with open(p, 'w') as f:
            f.write(c)
        print(f"Updated {hub} with unified breakdown top bar!")


if __name__ == '__main__':
    run_dinner_cruises()
    run_thames_cruises()
    unify_breakdown_bars_in_other_hubs()
