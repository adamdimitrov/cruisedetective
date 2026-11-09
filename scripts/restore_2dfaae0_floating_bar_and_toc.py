#!/usr/bin/env python3
"""
Restore 2dfaae0 Floating Bar & TOC Logic Sitewide across The Cruise Detective
Restores:
1. Floating sticky bar boundary condition:
   - Only active during Top 10 Comparison Cards and Detailed Review Breakdown.
   - Hidden at Hero (window.scrollY <= 350).
   - Hidden at Map & Intro (between comparison deck and breakdown header).
   - Hidden at Buyer's Guide & Methodology (once review #10 scrolls past: lastBottom < 100).
   - Completely eliminates false #10 PICK over Google Map and eliminates TOC occlusion.
2. Table of Contents max-height expansion:
   - Expands max-height from calc(100vh - 205px) to calc(100vh - 120px) so the entire
     TOC fits naturally without artificial truncation or scrollbars.
"""

import os
import glob
import re

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

OLD_BAR_REGEX = re.compile(
    r'var footer = document\.querySelector\([^\)]+\) \|\| document\.querySelector\([^\)]+\) \|\| document\.querySelector\([^\)]+\);\s*'
    r'var isPastFooter = footer \? \(footer\.getBoundingClientRect\(\)\.top < window\.innerHeight - 20\) : false;\s*'
    r'var hasPassedHero = \(window\.scrollY > \d+\);\s*'
    r'if \(!hasPassedHero \|\| isPastFooter\) \{\s*'
    r'bar\.classList\.remove\([^\)]+\);\s*'
    r'return;\s*'
    r'\}'
)

NEW_BAR_CODE = """var lastRev = reviews.length ? reviews[reviews.length - 1] : cards[cards.length - 1];
    var lastBottom = lastRev.getBoundingClientRect().bottom;

    var hasPassedHero = (window.scrollY > 350);
    var isPastReviews = (lastBottom < 100);
    var deck = document.getElementById(deckId) || document.getElementById('ltt-cards-deck');
    var brk = document.getElementById('breakdown-header');
    var isBetweenDeckAndReviews = (deck && brk && deck.getBoundingClientRect().bottom < vCenter && brk.getBoundingClientRect().top > vCenter);

    if (!hasPassedHero || isPastReviews || isBetweenDeckAndReviews) {
      bar.classList.remove('visible', 'is-visible');
      return;
    }"""

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # 1. Update floating bar boundary condition
    if OLD_BAR_REGEX.search(content):
        content = OLD_BAR_REGEX.sub(NEW_BAR_CODE, content, count=1)
        changed = True

    # 2. Update TOC max-height
    if 'max-height: calc(100vh - 205px) !important;' in content:
        content = content.replace('max-height: calc(100vh - 205px) !important;', 'max-height: calc(100vh - 120px) !important;')
        changed = True

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = glob.glob(os.path.join(BASE_DIR, '**/*.html'), recursive=True)
    updated = 0
    for f in files:
        if process_file(f):
            updated += 1
            print(f"Updated: {os.path.relpath(f, BASE_DIR)}")

    print(f"\nSuccessfully updated {updated} files with 2dfaae0 floating bar & TOC restoration.")

if __name__ == '__main__':
    main()
