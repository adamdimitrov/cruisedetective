#!/usr/bin/env python3
"""
UPGRADE ALL HUB SLIDERS TO 100% AUTHENTIC PHOTOS
Extracts full authentic photos from Webflow sources (comparison rows + review dossiers)
and updates .bpa-media across:
1. dinner-cruises-paris/index.html
2. seine-river-cruises-paris/index.html
3. canal-cruises-amsterdam/index.html
4. thames-river-cruises-london/index.html
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup

BASE_DIR = Path('/Users/adamdimitrov/Development/cruisedetective')
SKILL_DIR = Path('/Users/adamdimitrov/.gemini/config/skills/luxury-editorial-system')
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from compile_webflow_article import extract_slider_images_from_webflow

HUBS = [
    (
        BASE_DIR / 'dinner-cruises-paris' / 'index.html',
        SKILL_DIR / 'sources' / 'dinner_cruises_paris_webflow.html',
        'Dinner Cruises Paris'
    ),
    (
        BASE_DIR / 'seine-river-cruises-paris' / 'index.html',
        SKILL_DIR / 'sources' / 'seine_river_cruises_webflow.html',
        'Seine River Cruises Paris'
    ),
    (
        BASE_DIR / 'canal-cruises-amsterdam' / 'index.html',
        SKILL_DIR / 'sources' / 'canal_cruises_amsterdam_full_webflow.html',
        'Amsterdam Canal Cruises'
    ),
    (
        BASE_DIR / 'thames-river-cruises-london' / 'index.html',
        SKILL_DIR / 'sources' / 'thames_river_cruises_london_full_webflow.html',
        'London Thames River Cruises'
    )
]

def upgrade_page_sliders(html_path: Path, src_path: Path, label: str):
    print(f"\nProcessing {label}...")
    src_soup = BeautifulSoup(open(src_path, 'r', encoding='utf-8'), 'html.parser')
    page_soup = BeautifulSoup(open(html_path, 'r', encoding='utf-8'), 'html.parser')
    
    cards = page_soup.select('.bpa-card')
    num_cards = len(cards)
    print(f"  Found {num_cards} cards on disk.")
    
    slider_imgs = extract_slider_images_from_webflow(src_soup, num_items=num_cards)
    extracted_counts = [len(x) for x in slider_imgs]
    print(f"  Extracted authentic photo counts from source: {extracted_counts}")
    
    for idx, card in enumerate(cards):
        media = card.select_one('.bpa-media')
        if not media:
            continue
        
        rank_tag = media.select_one('.bpa-rank-tag')
        rank_tag_html = str(rank_tag) if rank_tag else ''
        
        imgs = slider_imgs[idx] if idx < len(slider_imgs) else []
        count = len(imgs)
        
        title_tag = card.select_one('.bpa-title')
        title_text = title_tag.get_text(strip=True) if title_tag else f'Vessel {idx+1}'
        alt = title_text.replace('"', '&quot;')
        
        imgs_rendered = []
        for i, img in enumerate(imgs):
            src = img.get('src', '')
            srcset = img.get('srcset', '')
            sizes = img.get('sizes', '(max-width: 767px) 420px, (max-width: 991px) 55vw, (max-width: 1439px) 49vw, 50vw')
            loading = 'eager' if (idx == 0 and i == 0) else 'lazy'
            fetchpriority = ' fetchpriority="high"' if (idx == 0 and i == 0) else ''
            srcset_attr = f' srcset="{srcset}"' if srcset else ''
            sizes_attr = f' sizes="{sizes}"' if sizes else ''
            imgs_rendered.append(f'<img src="{src}" loading="{loading}"{fetchpriority}{sizes_attr}{srcset_attr} alt="{alt}"/>')
        
        imgs_str = '\n                '.join(imgs_rendered)
        
        if count > 1:
            controls_html = f"""<button type="button" class="bpa-arrow prev" onclick="bpaSlide(this,-1)" aria-label="Previous photo">‹</button>
              <button type="button" class="bpa-arrow next" onclick="bpaSlide(this,1)" aria-label="Next photo">›</button>
              <span class="bpa-pill">1 / {count}</span>"""
            onscroll_attr = ' onscroll="bpaCount(this)"'
        else:
            controls_html = ''
            onscroll_attr = ''
        
        new_media_html = f"""<div class="bpa-media">
              {rank_tag_html}
              {controls_html}
              <div class="bpa-slider"{onscroll_attr}>
                {imgs_str}
              </div>
            </div>"""
        
        new_media_soup = BeautifulSoup(new_media_html, 'html.parser').select_one('.bpa-media')
        media.replace_with(new_media_soup)
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(page_soup))
    
    # Verify written file
    verify_soup = BeautifulSoup(open(html_path, 'r', encoding='utf-8'), 'html.parser')
    verified_counts = [len(c.select('.bpa-slider img')) for c in verify_soup.select('.bpa-card')]
    print(f"  ✓ Successfully updated {html_path.name}! Final slider counts: {verified_counts}")

def main():
    print("==================================================================")
    print("UPGRADING ALL CRUISE DETECTIVE HUBS TO 100% AUTHENTIC SLIDERS")
    print("==================================================================")
    for html_path, src_path, label in HUBS:
        upgrade_page_sliders(html_path, src_path, label)
    print("\nAll 4 English Money Hubs Successfully Upgraded!")

if __name__ == '__main__':
    main()
