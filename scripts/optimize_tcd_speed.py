#!/usr/bin/env python3
"""
Optimization Script for The Cruise Detective (TCD):
1. Defer Emerald (emrld.cc) tracking script to user interaction across all pages.
2. Deduplicate Google Fonts and clean up preconnects across all pages.
3. Progressive Lazy Loading for Photo Carousels (.bpa-slider slides 2..N).
4. Responsive sizes attribute on .ltt-sp-card images.
5. Injects/ensures global slider hydration runtime across all pages with sliders.
"""

import os
import glob
import re
from bs4 import BeautifulSoup

REPO_ROOT = '/Users/adamdimitrov/Development/cruisedetective'
SVG_PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 500'%3E%3C/svg%3E"

SLIDER_RUNTIME_SCRIPT = """<script id="bpa-slider-perf-runtime">
(function() {
  function loadSliderImages(slider) {
    if (!slider || slider._loaded) return;
    slider._loaded = true;
    var lazyImgs = slider.querySelectorAll('img[data-src]');
    for (var i = 0; i < lazyImgs.length; i++) {
      var img = lazyImgs[i];
      if (img.getAttribute('data-srcset')) {
        img.setAttribute('srcset', img.getAttribute('data-srcset'));
        img.removeAttribute('data-srcset');
      }
      img.src = img.getAttribute('data-src');
      img.removeAttribute('data-src');
    }
  }
  window._loadSliderImages = loadSliderImages;

  document.addEventListener('click', function(e) {
    var btn = e.target && e.target.closest && e.target.closest('.bpa-prev, .bpa-next, [onclick*="bpaSlide"]');
    if (btn) {
      var media = (btn.closest && btn.closest('.bpa-media, .bpa-slider-wrap, .bpa-gallery')) || btn.parentElement;
      var slider = media ? media.querySelector('.bpa-slider') : null;
      if (slider) loadSliderImages(slider);
    }
  }, true);

  document.addEventListener('pointerenter', function(e) {
    var target = e.target;
    if (target && target.closest) {
      var media = target.closest('.bpa-media, .bpa-slider');
      if (media) {
        var slider = media.classList.contains('bpa-slider') ? media : media.querySelector('.bpa-slider');
        if (slider) loadSliderImages(slider);
      }
    }
  }, true);

  document.addEventListener('touchstart', function(e) {
    var target = e.target;
    if (target && target.closest) {
      var media = target.closest('.bpa-media, .bpa-slider');
      if (media) {
        var slider = media.classList.contains('bpa-slider') ? media : media.querySelector('.bpa-slider');
        if (slider) loadSliderImages(slider);
      }
    }
  }, { passive: true, capture: true });

  document.addEventListener('scroll', function(e) {
    if (e.target && e.target.classList && e.target.classList.contains('bpa-slider')) {
      loadSliderImages(e.target);
    }
  }, { passive: true, capture: true });
})();
</script>"""

def optimize_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    modified = False
    soup = BeautifulSoup(content, 'html.parser')

    # 1. Deduplicate Google Fonts
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href', '')
        if 'fonts.googleapis.com' in href and 'Plus+Jakarta+Sans' not in href and 'Playfair' in href:
            has_combined = any('Plus+Jakarta+Sans' in l.get('href', '') for l in soup.find_all('link', rel='stylesheet'))
            if has_combined:
                link.decompose()
                modified = True

    # Consolidate preconnects
    seen_preconnects = set()
    for link in soup.find_all('link', rel='preconnect'):
        href = link.get('href', '')
        if href in seen_preconnects:
            link.decompose()
            modified = True
        else:
            seen_preconnects.add(href)

    # 2. Defer Emerald (emrld.cc) tracking script
    for script in soup.find_all('script'):
        text = script.string or script.text or ''
        if 'emrld.cc' in text and 'loadEmerald' not in text:
            new_emerald_js = """
window.addEventListener('load', function() {
  function loadEmerald() {
    if (window._emLoaded) return;
    window._emLoaded = true;
    var script = document.createElement('script');
    script.async = 1;
    script.src = 'https://emrld.cc/MjA0NDQy.js?t=204442';
    document.head.appendChild(script);
  }
  ['scroll', 'touchstart', 'mousemove'].forEach(function(evt) {
    window.addEventListener(evt, loadEmerald, { once: true, passive: true });
  });
  setTimeout(loadEmerald, 6000);
});
"""
            script.string = new_emerald_js
            modified = True

    # 3. Progressive Lazy-Loading for .bpa-slider
    sliders = soup.find_all(class_='bpa-slider')
    deferred_count = 0
    if sliders:
        for slider in sliders:
            imgs = slider.find_all('img')
            for img in imgs[1:]:
                src = img.get('src', '')
                if src and not src.startswith('data:'):
                    img['data-src'] = src
                    img['src'] = SVG_PLACEHOLDER
                    if img.get('srcset'):
                        img['data-srcset'] = img['srcset']
                        del img['srcset']
                    img['loading'] = 'lazy'
                    img['decoding'] = 'async'
                    deferred_count += 1
                    modified = True

    # 4. Spec cards responsive sizes
    sp_cards = soup.find_all(class_='ltt-sp-card')
    sp_updated = 0
    for card in sp_cards:
        img = card.find('img')
        if img and img.get('sizes') == '100vw':
            img['sizes'] = '(max-width: 640px) 100vw, 420px'
            sp_updated += 1
            modified = True

    if not modified:
        return False, 0, 0

    result_html = str(soup)

    # 5. Inject slider runtime script if sliders exist and runtime script not yet present
    if sliders and 'bpa-slider-perf-runtime' not in result_html:
        if '</body>' in result_html:
            result_html = result_html.replace('</body>', f'{SLIDER_RUNTIME_SCRIPT}\n</body>', 1)
        else:
            result_html += f'\n{SLIDER_RUNTIME_SCRIPT}'

    # Also make sure existing bpaSlide calls loadSliderImages if present
    old_bpa_slide_1 = """  // 1. Slider controls
  window.bpaSlide = function(btn, dir) {
    var media = btn.closest('.bpa-media');
    if (!media) return;
    var slider = media.querySelector('.bpa-slider');
    if (!slider) return;
    var w = slider.clientWidth;
    slider.scrollBy({ left: dir * w, behavior: 'smooth' });
  };"""

    new_bpa_slide_1 = """  // 1. Slider controls with Progressive Lazy-Loading
  function loadSliderImages(slider) {
    if (!slider || slider._loaded) return;
    slider._loaded = true;
    var lazyImgs = slider.querySelectorAll('img[data-src]');
    for (var i = 0; i < lazyImgs.length; i++) {
      var img = lazyImgs[i];
      if (img.getAttribute('data-srcset')) {
        img.setAttribute('srcset', img.getAttribute('data-srcset'));
        img.removeAttribute('data-srcset');
      }
      img.src = img.getAttribute('data-src');
      img.removeAttribute('data-src');
    }
  }

  window.bpaSlide = function(btn, dir) {
    var media = btn.closest('.bpa-media');
    if (!media) return;
    var slider = media.querySelector('.bpa-slider');
    if (!slider) return;
    loadSliderImages(slider);
    var w = slider.clientWidth;
    slider.scrollBy({ left: dir * w, behavior: 'smooth' });
  };"""

    if old_bpa_slide_1 in result_html:
        result_html = result_html.replace(old_bpa_slide_1, new_bpa_slide_1, 1)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(result_html)

    return True, deferred_count, sp_updated

def main():
    all_html = sorted(glob.glob(os.path.join(REPO_ROOT, '**/*.html'), recursive=True))
    prod_files = []
    for h in all_html:
        rel = os.path.relpath(h, REPO_ROOT)
        if rel.startswith('ads/') or rel.startswith('assets/'):
            continue
        base = os.path.basename(rel)
        if any(k in base for k in ['mockup', 'preview', 'prototype', 'comparison_deck', 'recovered_', 'original_']):
            continue
        prod_files.append(h)

    print(f"Total TCD production files to process: {len(prod_files)}")
    modified_files = 0
    total_deferred_imgs = 0
    total_sp_updated = 0

    for path in prod_files:
        mod, def_count, sp_count = optimize_file(path)
        if mod:
            modified_files += 1
            total_deferred_imgs += def_count
            total_sp_updated += sp_count

    print(f"\nTCD Optimization Complete!")
    print(f"  Files modified: {modified_files} / {len(prod_files)}")
    print(f"  Total off-screen slider images deferred: {total_deferred_imgs}")
    print(f"  Total spec card image sizes corrected: {total_sp_updated}")

if __name__ == '__main__':
    main()
