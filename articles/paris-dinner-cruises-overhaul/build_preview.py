import re
import os
import json
import html

PKG_DIR = "/Users/adamdimitrov/Development/cruisedetective/articles/paris-dinner-cruises-overhaul"
OUTPUT_PATH = os.path.join(PKG_DIR, "live_preview.html")
ARTIFACT_PATH = "/Users/adamdimitrov/.gemini/antigravity/brain/07bd7a30-aad9-4274-a455-af539f9cf6b4/live_preview.html"

# Read inputs
with open(os.path.join(PKG_DIR, "01_editorial_content_expansion.md")) as f:
    md_text = f.read()

with open(os.path.join(PKG_DIR, "02_semantic_comparison_table.html")) as f:
    table_raw = f.read()

with open(os.path.join(PKG_DIR, "03_rich_json_ld_schema.html")) as f:
    schema_raw = f.read()

with open(os.path.join(PKG_DIR, "04_webflow_component_blocks.html")) as f:
    components_raw = f.read()

# Extract styles from table and components
table_style_match = re.search(r"<style>([\s\S]*?)</style>", table_raw)
table_css = table_style_match.group(1) if table_style_match else ""

# Extract table body without style
table_body_match = re.search(r"<div class=\"cd-table-container\"[\s\S]*?</div>\s*</div>", table_raw)
table_html = table_body_match.group(0) if table_body_match else ""

comp_style_match = re.search(r"<style id=\"cd-master-components-css\">([\s\S]*?)</style>", components_raw)
comp_css = comp_style_match.group(1) if comp_style_match else ""

# Extract JSON-LD script content
schema_script_match = re.search(r"<script type=\"application/ld\+json\">([\s\S]*?)</script>", schema_raw)
schema_json_text = schema_script_match.group(1).strip() if schema_script_match else "{}"

# Parse markdown to clean HTML
def parse_markdown(text):
    lines = text.splitlines()
    html_lines = []
    in_list = False
    in_table = False
    in_code = False
    
    for line in lines:
        stripped = line.strip()
        
        # Handle code blocks
        if stripped.startswith("```"):
            if in_code:
                html_lines.append("</pre></div>")
                in_code = False
            else:
                html_lines.append("<div class='article-code-wrapper'><pre class='article-code'>")
                in_code = True
            continue
        if in_code:
            html_lines.append(html.escape(line))
            continue
            
        # Handle markdown table skip (we will embed the real semantic table)
        if stripped.startswith("|") and stripped.endswith("|"):
            # skip markdown tables because we embed the gorgeous rich table
            continue
            
        # Empty line
        if not stripped:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            continue
            
        # Horizontal rule
        if stripped in ["---", "***", "___"]:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            html_lines.append("<hr class='article-hr' />")
            continue
            
        # Headers
        m_h = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m_h:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            level = len(m_h.group(1))
            h_text = m_h.group(2)
            
            # Map headings to IDs
            anchor_id = ""
            if "1. Bateaux Mouches" in h_text:
                anchor_id = 'id="1-dinner-cruise-bateaux-mouches"'
            elif "2. Bateaux Parisiens" in h_text:
                anchor_id = 'id="2-dinner-cruise-bateaux-parisiens"'
            elif "3. Paris City Vision" in h_text and "Early" not in h_text:
                anchor_id = 'id="3-dinner-cruise-paris-city-vision"'
            elif "4. Paris en Scene" in h_text or "4. Paris en Scène" in h_text:
                anchor_id = 'id="4-dinner-cruise-paris-en-scene"'
            elif "5. Le Diamant Bleu" in h_text:
                anchor_id = 'id="5-dinner-cruise-le-diamant-bleu"'
            elif "6. Trattoria en Seine" in h_text:
                anchor_id = 'id="6-trattoria-en-seine"'
            elif "7. Capitaine Fracasse" in h_text:
                anchor_id = 'id="7-capitaine-fracasse"'
            elif "8. Maxims de Paris" in h_text or "8. Maxim's" in h_text:
                anchor_id = 'id="8-maxim-de-paris"'
            elif "9. Ducasse Sur Seine" in h_text:
                anchor_id = 'id="9-ducasse-sur-seine"'
            elif "10. Paris City Vision Early" in h_text:
                anchor_id = 'id="10-paris-city-vision"'
            elif "Summary Comparison" in h_text:
                anchor_id = 'id="summary-comparison"'
            elif "Are Paris Dinner Cruises Worth" in h_text:
                anchor_id = 'id="is-it-worth-it"'
            elif "Seine River Dinner Cruise Route" in h_text:
                anchor_id = 'id="cruise-route-landmarks"'
            elif "Planning and Frequently Asked" in h_text:
                anchor_id = 'id="faq"'
            elif "Final Verdict" in h_text:
                anchor_id = 'id="final-verdict"'
            else:
                slug = re.sub(r"[^\w\s-]", "", h_text.lower()).strip().replace(" ", "-")
                anchor_id = f'id="{slug}"'
                
            h_tag = f"h{level}"
            formatted_title = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", h_text)
            html_lines.append(f'<{h_tag} {anchor_id} class="article-{h_tag}">{formatted_title}</{h_tag}>')
            
            # If this is the Summary Comparison heading, inject table immediately below
            if "Summary Comparison" in h_text:
                html_lines.append("<!-- TABLE_PLACEHOLDER -->")
            continue
            
        # Lists
        if stripped.startswith("- ") or stripped.startswith("* "):
            if not in_list:
                html_lines.append("<ul class='article-list'>")
                in_list = True
            item_text = stripped[2:]
            # format bold, italic, links
            item_text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", item_text)
            item_text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", item_text)
            item_text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', item_text)
            html_lines.append(f"<li>{item_text}</li>")
            continue
        elif re.match(r"^\d+\.\s+", stripped):
            if in_list:
                html_lines.append("</ul>")
                in_list = False
            item_text = re.sub(r"^\d+\.\s+", "", stripped)
            item_text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", item_text)
            item_text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", item_text)
            item_text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', item_text)
            html_lines.append(f"<div class='article-num-item'><span class='num-badge'>•</span> <div>{item_text}</div></div>")
            continue
        else:
            if in_list:
                html_lines.append("</ul>")
                in_list = False
                
        # Paragraphs
        p_text = stripped
        p_text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", p_text)
        p_text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", p_text)
        p_text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', p_text)
        
        # Check byline paragraph
        if "By Adam Dimitrov" in p_text:
            html_lines.append(f"<div class='article-byline'>{p_text}</div>")
        else:
            html_lines.append(f"<p class='article-p'>{p_text}</p>")
            
    if in_list:
        html_lines.append("</ul>")
        
    return "\n".join(html_lines)

parsed_article = parse_markdown(md_text)

# Inject table
parsed_article = parsed_article.replace("<!-- TABLE_PLACEHOLDER -->", f"<div class='table-embed-wrapper'>{table_html}</div>")

# Extract the specific showcase component blocks to inject under each boat
def get_component(html_source, start_marker, end_marker):
    idx = html_source.find(start_marker)
    if idx == -1: return ""
    idx_end = html_source.find(end_marker, idx)
    if idx_end == -1: return html_source[idx:]
    return html_source[idx:idx_end]

# Boat 1 Components
bm_tip = get_component(components_raw, '<aside class="cd-sommelier-tip" role="note" aria-label="Sommelier Insider Tip for Bateaux Mouches">', '<!-- Example 2:')
bm_pros = get_component(components_raw, '<div class="cd-review-breakdown" role="region" aria-label="Bateaux Mouches Review Breakdown">', '<!-- Example 2: Bateaux Parisiens Pros & Cons')
bm_badge = get_component(components_raw, '<div class="cd-verified-reviews-bar" role="complementary" aria-label="Verified Customer Ratings for Bateaux Mouches">', '<!-- Example 2: Bateaux Parisiens')

# Boat 2 Components
bp_tip = get_component(components_raw, '<aside class="cd-sommelier-tip" role="note" aria-label="Sommelier Insider Tip for Bateaux Parisiens">', '<!-- Example 3:')
bp_pros = get_component(components_raw, '<div class="cd-review-breakdown" role="region" aria-label="Bateaux Parisiens Review Breakdown">', '<!-- Example 3: Paris City Vision')
bp_badge = get_component(components_raw, '<div class="cd-verified-reviews-bar" role="complementary" aria-label="Verified Customer Ratings for Bateaux Parisiens">', '<!-- Example 3: Paris City Vision')

# Boat 3 Components
pcv_tip = get_component(components_raw, '<aside class="cd-sommelier-tip" role="note" aria-label="Sommelier Insider Tip for Paris City Vision">', '<!-- Example 4:')
pcv_pros = get_component(components_raw, '<div class="cd-review-breakdown" role="region" aria-label="Paris City Vision / La Marina de Paris Review Breakdown">', '<!-- Example 4: Paris en Scène')
pcv_badge = get_component(components_raw, '<div class="cd-verified-reviews-bar" role="complementary" aria-label="Verified Customer Ratings for Paris City Vision / La Marina de Paris">', '<!-- Example 4: Paris en Scène')

# Boat 4 Components
pes_pros = get_component(components_raw, '<div class="cd-review-breakdown" role="region" aria-label="Paris en Scène Review Breakdown">', '</div>\n  </div>\n\n</div>\n\n\n  <!-- =========================================================================\n       SECTION 3:')
pes_badge = get_component(components_raw, '<div class="cd-verified-reviews-bar" role="complementary" aria-label="Verified Customer Ratings for Paris en Scène">', '<!-- Example 5: Le Diamant Bleu')

# Boat 5 Components
dbleu_tip = get_component(components_raw, '<aside class="cd-sommelier-tip" role="note" aria-label="Sommelier Insider Tip for Le Diamant Bleu">', '</div>\n  </div>\n\n</div>\n\n\n  <!-- =========================================================================\n       SECTION 2:')
dbleu_badge = get_component(components_raw, '<div class="cd-verified-reviews-bar" role="complementary" aria-label="Verified Customer Ratings for Le Diamant Bleu">', '</div>\n  </div>\n\n</div>\n\n\n  <!-- =========================================================================\n       SECTION 4:')

# Inject components after each boat section header or pros/cons
if '<h2 id="1-dinner-cruise-bateaux-mouches"' in parsed_article:
    # Inject Boat 1 blocks right after Pros & Cons section
    inject_bm = f"""
    <div class="embedded-cd-block">
        {bm_tip}
        {bm_pros}
        {bm_badge}
        <div style="margin: 1.5rem 0; text-align: center;">
            <a href="https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=thecruisedetective.com-176436&tq_campaign=review-bm-button" class="cd-btn-large btn-gold" target="_blank" rel="noopener">
                🏆 Check Live Availability for Bateaux-Mouches (From €130) →
            </a>
        </div>
    </div>
    """
    target = '### Pros and Cons of Bateaux Mouches'
    parsed_article = parsed_article.replace('<h3 id="pros-and-cons-of-bateaux-mouches" class="article-h3">Pros and Cons of Bateaux Mouches</h3>', f'<h3 id="pros-and-cons-of-bateaux-mouches" class="article-h3">Pros and Cons of Bateaux Mouches</h3>{inject_bm}')

if '<h2 id="2-dinner-cruise-bateaux-parisiens"' in parsed_article:
    inject_bp = f"""
    <div class="embedded-cd-block">
        {bp_tip}
        {bp_pros}
        {bp_badge}
        <div style="margin: 1.5rem 0; text-align: center;">
            <a href="https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-gourmet-dinner-cruise-on-the-seine-p974358/?partner=thecruisedetective.com-176436&tq_campaign=review-bp-button" class="cd-btn-large btn-navy" target="_blank" rel="noopener">
                ⭐ Reserve Bateaux Parisiens Gourmet Dinner (From €115) →
            </a>
        </div>
    </div>
    """
    parsed_article = parsed_article.replace('<h3 id="pros-and-cons-of-bateaux-parisiens" class="article-h3">Pros and Cons of Bateaux Parisiens</h3>', f'<h3 id="pros-and-cons-of-bateaux-parisiens" class="article-h3">Pros and Cons of Bateaux Parisiens</h3>{inject_bp}')

if '<h2 id="3-dinner-cruise-paris-city-vision"' in parsed_article:
    inject_pcv = f"""
    <div class="embedded-cd-block">
        {pcv_tip}
        {pcv_pros}
        {pcv_badge}
        <div style="margin: 1.5rem 0; text-align: center;">
            <a href="https://www.getyourguide.com/paris-l16/paris-3-course-dinner-cruise-on-the-river-seine-t53306/?partner_id=YS414AJ&utm_medium=online_publisher&cmp=review-pcv-button&mkt_cmp=true" class="cd-btn-large btn-wine" target="_blank" rel="noopener">
                🕯️ Check La Marina Dinner Cruise on GetYourGuide (From €85) →
            </a>
        </div>
    </div>
    """
    parsed_article = parsed_article.replace('<h3 id="pros-and-cons-of-la-marina-de-paris" class="article-h3">Pros and Cons of La Marina de Paris</h3>', f'<h3 id="pros-and-cons-of-la-marina-de-paris" class="article-h3">Pros and Cons of La Marina de Paris</h3>{inject_pcv}')

if '<h2 id="4-dinner-cruise-paris-en-scene"' in parsed_article:
    inject_pes = f"""
    <div class="embedded-cd-block">
        {pes_pros}
        {pes_badge}
        <div style="margin: 1.5rem 0; text-align: center;">
            <a href="https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-en-scene-dinner-cruise-seine-p1052475/?partner=thecruisedetective.com-176436&tq_campaign=review-pes-button" class="cd-btn-large btn-emerald" target="_blank" rel="noopener">
                🎟️ Book Paris en Scène (From €65) →
            </a>
        </div>
    </div>
    """
    parsed_article = parsed_article.replace('<h3 id="pros-and-cons-of-paris-en-scene" class="article-h3">Pros and Cons of Paris en Scène</h3>', f'<h3 id="pros-and-cons-of-paris-en-scene" class="article-h3">Pros and Cons of Paris en Scène</h3>{inject_pes}')

if '<h2 id="5-dinner-cruise-le-diamant-bleu"' in parsed_article:
    inject_dbleu = f"""
    <div class="embedded-cd-block">
        {dbleu_tip}
        {dbleu_badge}
        <div style="margin: 1.5rem 0; text-align: center;">
            <a href="https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-paris-diamond-blue-gourmet-dinner-cruise-p1049009/?partner=thecruisedetective.com-176436&tq_campaign=review-dbleu-button" class="cd-btn-large btn-indigo" target="_blank" rel="noopener">
                💎 Reserve Le Diamant Bleu 70m Mega-Yacht (From €89) →
            </a>
        </div>
    </div>
    """
    parsed_article = parsed_article.replace('<h3 id="pros-and-cons-of-le-diamant-bleu" class="article-h3">Pros and Cons of Le Diamant Bleu</h3>', f'<h3 id="pros-and-cons-of-le-diamant-bleu" class="article-h3">Pros and Cons of Le Diamant Bleu</h3>{inject_dbleu}')

# Generate Master Interactive HTML Preview Document
html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Paris Dinner Cruises Overhaul — Live Interactive Inspection Studio</title>
  
  <!-- Playfair Display & Inter Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600&display=swap" rel="stylesheet">
  
  <!-- Master Styles -->
  <style>
    {table_css}
    {comp_css}
    
    /* App Shell & Inspection Studio Styling */
    :root {{
      --studio-bg: #0f172a;
      --studio-bar: #1e293b;
      --studio-border: #334155;
      --studio-text: #f8fafc;
      --studio-accent: #f59e0b;
      --article-max-width: 960px;
    }}
    
    * {{
      box-sizing: border-box;
    }}
    
    body {{
      margin: 0;
      padding: 0;
      background: #f1f5f9;
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      color: #1e293b;
      -webkit-font-smoothing: antialiased;
    }}
    
    /* Top Global Control Toolbar */
    .studio-top-bar {{
      position: sticky;
      top: 0;
      z-index: 9999;
      background: var(--studio-bar);
      border-bottom: 1px solid var(--studio-border);
      color: var(--studio-text);
      padding: 0.65rem 1.25rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 1rem;
      box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }}
    
    .studio-brand {{
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }}
    
    .studio-logo {{
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.1rem;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}
    
    .studio-title {{
      font-size: 0.95rem;
      font-weight: 800;
      letter-spacing: -0.01em;
      color: #fff;
    }}
    
    .studio-pill {{
      font-size: 0.68rem;
      font-weight: 800;
      background: rgba(245, 158, 11, 0.2);
      border: 1px solid rgba(245, 158, 11, 0.4);
      color: #fbbf24;
      padding: 0.2rem 0.55rem;
      border-radius: 9999px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    
    /* Mode Tab Switcher */
    .studio-tabs {{
      display: flex;
      align-items: center;
      background: #0f172a;
      padding: 0.25rem;
      border-radius: 8px;
      border: 1px solid var(--studio-border);
      gap: 0.25rem;
    }}
    
    .tab-btn {{
      background: transparent;
      border: none;
      color: #94a3b8;
      font-size: 0.82rem;
      font-weight: 700;
      padding: 0.45rem 0.85rem;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.4rem;
      transition: all 0.15s ease;
    }}
    
    .tab-btn:hover {{
      color: #f8fafc;
      background: rgba(255,255,255,0.06);
    }}
    
    .tab-btn.active {{
      background: var(--studio-accent);
      color: #0f172a;
      font-weight: 800;
      box-shadow: 0 2px 8px rgba(245, 158, 11, 0.35);
    }}
    
    /* Device Controls */
    .device-controls {{
      display: flex;
      align-items: center;
      background: #0f172a;
      padding: 0.25rem;
      border-radius: 8px;
      border: 1px solid var(--studio-border);
      gap: 0.2rem;
    }}
    
    .device-btn {{
      background: transparent;
      border: none;
      color: #94a3b8;
      font-size: 0.78rem;
      font-weight: 600;
      padding: 0.4rem 0.65rem;
      border-radius: 5px;
      cursor: pointer;
      transition: all 0.15s;
    }}
    
    .device-btn:hover {{
      color: #fff;
    }}
    
    .device-btn.active {{
      background: #334155;
      color: #fff;
      font-weight: 700;
    }}
    
    /* Jump Navigation Bar */
    .studio-subnav {{
      background: #ffffff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0.6rem 1.5rem;
      display: flex;
      align-items: center;
      gap: 0.75rem;
      overflow-x: auto;
      white-space: nowrap;
      box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }}
    
    .subnav-label {{
      font-size: 0.75rem;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #94a3b8;
    }}
    
    .subnav-link {{
      font-size: 0.8rem;
      font-weight: 700;
      color: #475569;
      text-decoration: none;
      padding: 0.25rem 0.65rem;
      border-radius: 9999px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      transition: all 0.15s ease;
    }}
    
    .subnav-link:hover {{
      background: #fef3c7;
      color: #92400e;
      border-color: #fde68a;
    }}
    
    .subnav-link.winner {{
      background: #fef3c7;
      color: #b45309;
      border-color: #f59e0b;
      font-weight: 800;
    }}
    
    /* Canvas Viewport Frame */
    .studio-viewport-container {{
      padding: 2.5rem 1rem 5rem 1rem;
      display: flex;
      justify-content: center;
      min-height: calc(100vh - 120px);
      transition: all 0.25s ease;
    }}
    
    .viewport-frame {{
      width: 100%;
      max-width: var(--article-max-width);
      background: #ffffff;
      border-radius: 16px;
      box-shadow: 0 20px 45px -10px rgba(15, 23, 42, 0.12), 0 2px 10px rgba(15, 23, 42, 0.04);
      border: 1px solid #e2e8f0;
      overflow: hidden;
      transition: max-width 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    
    /* Device Size Modes */
    .device-desktop {{
      --article-max-width: 980px;
    }}
    
    .device-tablet {{
      --article-max-width: 768px;
    }}
    
    .device-mobile {{
      --article-max-width: 390px;
    }}
    
    /* Webflow Simulation Article Header */
    .webflow-site-nav {{
      background: #ffffff;
      border-bottom: 1px solid #f1f5f9;
      padding: 1.1rem 2.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    
    .webflow-nav-brand {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
      font-family: 'Playfair Display', Georgia, serif;
      font-weight: 800;
      font-size: 1.25rem;
      color: #0f172a;
      text-decoration: none;
    }}
    
    .webflow-nav-links {{
      display: flex;
      gap: 1.5rem;
      font-size: 0.88rem;
      font-weight: 600;
      color: #475569;
    }}
    
    .article-body-wrapper {{
      padding: 3rem 3.5rem;
    }}
    
    @media (max-width: 768px) {{
      .article-body-wrapper {{
        padding: 1.75rem 1.25rem;
      }}
      .webflow-site-nav {{
        padding: 0.85rem 1.25rem;
      }}
    }}
    
    /* Typography for Article Content */
    .article-h1 {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 2.6rem;
      font-weight: 800;
      line-height: 1.2;
      color: #0f172a;
      margin: 0 0 1rem 0;
      letter-spacing: -0.02em;
    }}
    
    .article-byline {{
      font-size: 0.92rem;
      color: #64748b;
      margin-bottom: 2rem;
      padding-bottom: 1.5rem;
      border-bottom: 1.5px solid #e2e8f0;
      line-height: 1.6;
    }}
    
    .article-h2 {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 1.85rem;
      font-weight: 800;
      color: #0f172a;
      margin: 3.5rem 0 1.25rem 0;
      padding-top: 1.5rem;
      border-top: 1px solid #f1f5f9;
      line-height: 1.3;
      letter-spacing: -0.01em;
    }}
    
    .article-h3 {{
      font-size: 1.25rem;
      font-weight: 800;
      color: #1e293b;
      margin: 2rem 0 0.85rem 0;
      line-height: 1.35;
    }}
    
    .article-p {{
      font-size: 1.05rem;
      line-height: 1.75;
      color: #334155;
      margin: 0 0 1.4rem 0;
    }}
    
    .article-list {{
      margin: 0 0 1.75rem 1.5rem;
      padding: 0;
      font-size: 1.02rem;
      line-height: 1.7;
      color: #334155;
    }}
    
    .article-list li {{
      margin-bottom: 0.65rem;
    }}
    
    .article-num-item {{
      display: flex;
      gap: 0.75rem;
      margin-bottom: 0.85rem;
      font-size: 1.02rem;
      line-height: 1.65;
      color: #334155;
    }}
    
    .num-badge {{
      color: var(--studio-accent);
      font-weight: 800;
    }}
    
    .article-code-wrapper {{
      background: #0f172a;
      border-radius: 12px;
      padding: 1.25rem 1.5rem;
      margin: 1.75rem 0;
      overflow-x: auto;
      border: 1px solid #334155;
    }}
    
    .article-code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: #38bdf8;
      font-size: 0.85rem;
      line-height: 1.6;
      margin: 0;
    }}
    
    .article-hr {{
      border: none;
      height: 1px;
      background: #e2e8f0;
      margin: 3.5rem 0;
    }}
    
    /* CTA Large Button */
    .cd-btn-large {{
      display: inline-block;
      text-decoration: none;
      font-size: 1rem;
      font-weight: 800;
      padding: 0.95rem 1.75rem;
      border-radius: 10px;
      transition: all 0.2s ease;
      color: #ffffff !important;
      box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }}
    
    .cd-btn-large:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(0,0,0,0.22);
      filter: brightness(1.08);
    }}
    
    .btn-gold {{
      background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
    }}
    .btn-navy {{
      background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
    }}
    .btn-wine {{
      background: linear-gradient(135deg, #991b1b 0%, #7f1d1d 100%);
    }}
    .btn-emerald {{
      background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
    }}
    .btn-indigo {{
      background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%);
    }}
    
    /* Dedicated Views for Tabs */
    .studio-view {{
      display: none;
    }}
    .studio-view.active {{
      display: block;
    }}
    
    /* Export Center & Schema Viewers */
    .code-panel {{
      background: #0f172a;
      color: #f8fafc;
      border-radius: 12px;
      padding: 1.5rem;
      font-family: ui-monospace, Menlo, Monaco, Consolas, monospace;
      font-size: 0.85rem;
      line-height: 1.6;
      overflow-x: auto;
      border: 1px solid #334155;
      max-height: 600px;
      position: relative;
    }}
    
    .copy-btn {{
      position: absolute;
      top: 1rem;
      right: 1rem;
      background: #f59e0b;
      color: #0f172a;
      border: none;
      font-size: 0.75rem;
      font-weight: 800;
      padding: 0.4rem 0.85rem;
      border-radius: 6px;
      cursor: pointer;
      transition: all 0.15s;
    }}
    
    .copy-btn:hover {{
      background: #fbbf24;
      transform: scale(1.03);
    }}
    
    /* Success notification */
    .toast-notice {{
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      background: #10b981;
      color: #ffffff;
      padding: 0.75rem 1.25rem;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.9rem;
      box-shadow: 0 10px 25px rgba(16, 185, 129, 0.4);
      display: none;
      z-index: 10000;
      animation: fadeIn 0.2s ease;
    }}
    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(10px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
  </style>
</head>
<body class="device-desktop">

  <!-- Top Studio Control Bar -->
  <header class="studio-top-bar">
    <div class="studio-brand">
      <div class="studio-logo">🔍</div>
      <div>
        <div class="studio-title">The Cruise Detective • Paris Flagship Inspection Studio</div>
        <div style="font-size: 0.72rem; color: #94a3b8;">Article Overhaul • Position-0 Matrix • Schema v15.0</div>
      </div>
      <span class="studio-pill">36/36 Passed E2E</span>
    </div>
    
    <!-- Tab Controls -->
    <div class="studio-tabs">
      <button class="tab-btn active" onclick="switchView('article')">
        <span>📰</span> Full Article Live
      </button>
      <button class="tab-btn" onclick="switchView('table')">
        <span>📊</span> Position-0 Matrix
      </button>
      <button class="tab-btn" onclick="switchView('components')">
        <span>🧩</span> UI Callouts
      </button>
      <button class="tab-btn" onclick="switchView('schema')">
        <span>🏷️</span> Rich Schema (JSON-LD)
      </button>
      <button class="tab-btn" onclick="switchView('export')">
        <span>📋</span> Webflow Exporter
      </button>
    </div>
    
    <!-- Device Controls -->
    <div class="device-controls">
      <button class="device-btn active" onclick="setDevice('desktop')">💻 Desktop</button>
      <button class="device-btn" onclick="setDevice('tablet')">📱 Tablet</button>
      <button class="device-btn" onclick="setDevice('mobile')">📱 Mobile</button>
    </div>
  </header>

  <!-- Quick Anchor Navigation Bar -->
  <nav class="studio-subnav">
    <span class="subnav-label">Quick Jump:</span>
    <a href="#summary-comparison" class="subnav-link">📊 Comparison Table</a>
    <a href="#is-it-worth-it" class="subnav-link">💶 Is It Worth It?</a>
    <a href="#cruise-route-landmarks" class="subnav-link">🗺️ Cruise Route</a>
    <a href="#1-dinner-cruise-bateaux-mouches" class="subnav-link winner">🏆 #1 Bateaux Mouches</a>
    <a href="#2-dinner-cruise-bateaux-parisiens" class="subnav-link">⭐ #2 Bateaux Parisiens</a>
    <a href="#3-dinner-cruise-paris-city-vision" class="subnav-link">🕯️ #3 La Marina</a>
    <a href="#4-dinner-cruise-paris-en-scene" class="subnav-link">🎟️ #4 Paris en Scène</a>
    <a href="#5-dinner-cruise-le-diamant-bleu" class="subnav-link">💎 #5 Diamant Bleu</a>
    <a href="#6-trattoria-en-seine" class="subnav-link">🍝 #6 Trattoria en Seine</a>
    <a href="#7-capitaine-fracasse" class="subnav-link">🍷 #7 Capitaine Fracasse</a>
    <a href="#8-maxim-de-paris" class="subnav-link">🎷 #8 Maxim's de Paris</a>
    <a href="#9-ducasse-sur-seine" class="subnav-link">⚡ #9 Ducasse sur Seine</a>
    <a href="#10-paris-city-vision" class="subnav-link">🌅 #10 PCV Early Sunset</a>
    <a href="#faq" class="subnav-link">❓ Logistics FAQ</a>
  </nav>

  <!-- Viewport Area -->
  <main class="studio-viewport-container">
    <div class="viewport-frame">
      
      <!-- VIEW 1: FULL ARTICLE LIVE -->
      <section id="view-article" class="studio-view active">
        <!-- Simulated Webflow Site Header -->
        <div class="webflow-site-nav">
          <a href="https://www.thecruisedetective.com" class="webflow-nav-brand" target="_blank" rel="noopener">
            <span style="font-size: 1.4rem;">🚢</span> The Cruise Detective
          </a>
          <div class="webflow-nav-links">
            <span>Paris Cruises</span>
            <span>Budapest Cruises</span>
            <span>London Cruises</span>
            <span>Amsterdam</span>
            <span style="color: #d97706; font-weight: 700;">★ Best Deals</span>
          </div>
        </div>
        
        <!-- Rendered Full Article Body -->
        <article class="article-body-wrapper">
          {parsed_article}
        </article>
      </section>

      <!-- VIEW 2: ISOLATED POSITION-0 MATRIX -->
      <section id="view-table" class="studio-view" style="padding: 2.5rem 2rem;">
        <div style="margin-bottom: 1.5rem;">
          <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.8rem; margin: 0 0 0.5rem 0;">
            Google Position-0 Semantic HTML Comparison Table
          </h2>
          <p style="color: #64748b; font-size: 0.95rem; margin: 0;">
            This is the exact responsive <code>&lt;table&gt;</code> embed destined for Webflow below the intro. It contains all 10 vessels, semantic headers, rating volumes, and direct booking links.
          </p>
        </div>
        {table_html}
      </section>

      <!-- VIEW 3: COMPONENT BLOCKS SHOWCASE -->
      <section id="view-components" class="studio-view" style="padding: 2.5rem 2rem;">
        <div style="margin-bottom: 2rem;">
          <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.8rem; margin: 0 0 0.5rem 0;">
            Webflow Component Library Showcase
          </h2>
          <p style="color: #64748b; font-size: 0.95rem; margin: 0;">
            Pre-styled, isolated component widgets: Sommelier Pro Tips, 2-Column Pros &amp; Cons containers, and Multi-platform review badges.
          </p>
        </div>
        
        <h3 style="color: #d97706; border-bottom: 2px solid #fef3c7; padding-bottom: 0.5rem; margin-top: 2rem;">
          1. Insider Sommelier Pro Tips
        </h3>
        <div style="margin-bottom: 2rem;">{bm_tip}</div>
        <div style="margin-bottom: 2rem;">{bp_tip}</div>
        <div style="margin-bottom: 2rem;">{pcv_tip}</div>
        <div style="margin-bottom: 2rem;">{dbleu_tip}</div>

        <h3 style="color: #16a34a; border-bottom: 2px solid #dcfce7; padding-bottom: 0.5rem; margin-top: 3rem;">
          2. 2-Column Pros &amp; Cons Containers
        </h3>
        <div style="margin-bottom: 2rem;">{bm_pros}</div>
        <div style="margin-bottom: 2rem;">{bp_pros}</div>
        <div style="margin-bottom: 2rem;">{pcv_pros}</div>
        <div style="margin-bottom: 2rem;">{pes_pros}</div>

        <h3 style="color: #0284c7; border-bottom: 2px solid #e0f2fe; padding-bottom: 0.5rem; margin-top: 3rem;">
          3. Multi-Platform Verified Review Badges
        </h3>
        <div style="margin-bottom: 2rem;">{bm_badge}</div>
        <div style="margin-bottom: 2rem;">{bp_badge}</div>
        <div style="margin-bottom: 2rem;">{pcv_badge}</div>
        <div style="margin-bottom: 2rem;">{pes_badge}</div>
      </section>

      <!-- VIEW 4: SCHEMA.ORG JSON-LD -->
      <section id="view-schema" class="studio-view" style="padding: 2.5rem 2rem;">
        <div style="margin-bottom: 1.5rem;">
          <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.8rem; margin: 0 0 0.5rem 0;">
            Schema.org JSON-LD Structured Data
          </h2>
          <p style="color: #64748b; font-size: 0.95rem; margin: 0;">
            Paste this inside Webflow <strong>Page Settings &rarr; Custom Code &rarr; Inside &lt;head&gt;</strong>. Includes unified <code>Article</code>, ranked 10-boat <code>ItemList</code>, and verified <code>FAQPage</code>.
          </p>
        </div>
        <div class="code-panel">
          <button class="copy-btn" onclick="copySchema()">📋 Copy Schema Code</button>
          <pre id="schema-code-block">{html.escape(schema_raw)}</pre>
        </div>
      </section>

      <!-- VIEW 5: WEBFLOW EXPORT CENTER -->
      <section id="view-export" class="studio-view" style="padding: 2.5rem 2rem;">
        <div style="margin-bottom: 2rem;">
          <h2 style="font-family: 'Playfair Display', Georgia, serif; font-size: 1.8rem; margin: 0 0 0.5rem 0;">
            Webflow Production Code Exporter
          </h2>
          <p style="color: #64748b; font-size: 0.95rem; margin: 0;">
            One-click copy-paste snippets prepared for immediate deployment in Webflow.
          </p>
        </div>

        <div style="margin-bottom: 2.5rem;">
          <h3 style="font-size: 1.15rem; margin: 0 0 0.5rem 0;">
            Step 1: Position-0 HTML Comparison Table Embed
          </h3>
          <p style="font-size: 0.88rem; color: #64748b; margin: 0 0 0.75rem 0;">
            Paste into an <strong>HTML Embed</strong> component directly under your introductory hook.
          </p>
          <div class="code-panel">
            <button class="copy-btn" onclick="copySnippet('table-snippet')">📋 Copy Table Embed</button>
            <pre id="table-snippet">{html.escape(table_raw)}</pre>
          </div>
        </div>

        <div style="margin-bottom: 2.5rem;">
          <h3 style="font-size: 1.15rem; margin: 0 0 0.5rem 0;">
            Step 2: Rich Schema.org JSON-LD (Head Code)
          </h3>
          <p style="font-size: 0.88rem; color: #64748b; margin: 0 0 0.75rem 0;">
            Paste into <strong>Page Settings &rarr; Custom Code &rarr; Inside &lt;head&gt;</strong>.
          </p>
          <div class="code-panel">
            <button class="copy-btn" onclick="copySnippet('schema-snippet')">📋 Copy Schema Head Code</button>
            <pre id="schema-snippet">{html.escape(schema_raw)}</pre>
          </div>
        </div>

        <div style="margin-bottom: 2.5rem;">
          <h3 style="font-size: 1.15rem; margin: 0 0 0.5rem 0;">
            Step 3: Master Component Stylesheet
          </h3>
          <p style="font-size: 0.88rem; color: #64748b; margin: 0 0 0.75rem 0;">
            Paste into Page Settings Custom Code Head if you use standalone component HTML blocks.
          </p>
          <div class="code-panel">
            <button class="copy-btn" onclick="copySnippet('comp-css-snippet')">📋 Copy CSS Stylesheet</button>
            <pre id="comp-css-snippet">&lt;style id="cd-master-components-css"&gt;\n{html.escape(comp_css)}\n&lt;/style&gt;</pre>
          </div>
        </div>
      </section>

    </div>
  </main>

  <div id="toast" class="toast-notice">✅ Copied to clipboard!</div>

  <!-- Interactive JavaScript Engine -->
  <script>
    function switchView(viewName) {{
      // Update tab buttons
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      event.currentTarget.classList.add('active');
      
      // Update active view
      document.querySelectorAll('.studio-view').forEach(v => v.classList.remove('active'));
      const activeSection = document.getElementById('view-' + viewName);
      if (activeSection) {{
        activeSection.classList.add('active');
      }}
      window.scrollTo({{ top: 0, behavior: 'smooth' }});
    }}

    function setDevice(device) {{
      document.querySelectorAll('.device-btn').forEach(b => b.classList.remove('active'));
      event.currentTarget.classList.add('active');
      
      document.body.classList.remove('device-desktop', 'device-tablet', 'device-mobile');
      document.body.classList.add('device-' + device);
    }}

    function copySnippet(elementId) {{
      const text = document.getElementById(elementId).innerText;
      navigator.clipboard.writeText(text).then(() => {{
        showToast("✅ Code snippet copied to clipboard!");
      }});
    }}

    function copySchema() {{
      const text = document.getElementById('schema-code-block').innerText;
      navigator.clipboard.writeText(text).then(() => {{
        showToast("✅ Schema markup copied to clipboard!");
      }});
    }}

    function showToast(msg) {{
      const t = document.getElementById('toast');
      t.innerText = msg;
      t.style.display = 'block';
      setTimeout(() => {{
        t.style.display = 'none';
      }}, 2600);
    }}
  </script>
</body>
</html>
"""

# Write to package folder
with open(OUTPUT_PATH, "w") as f:
    f.write(html_template)

# Write to brain artifact folder
os.makedirs(os.path.dirname(ARTIFACT_PATH), exist_ok=True)
with open(ARTIFACT_PATH, "w") as f:
    f.write(html_template)

print(f"Generated live_preview.html successfully ({len(html_template)} bytes)")
