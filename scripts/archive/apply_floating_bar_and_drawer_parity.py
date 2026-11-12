#!/usr/bin/env python3
"""
Cruisedetective Parity Synchronizer
Fixes across all HTML files:
1. Floating sticky bottom bar visibility & footer cutoff logic (no premature accordion disappearance).
2. Symmetrical 'X' animation on hamburger menu button.
3. Mobile drawer z-index (100000) vs sticky bar (9990) and drawer-open conflict suppression.
4. Body class toggling 'ltt-drawer-open' on open/close.
"""

import os
import re
from bs4 import BeautifulSoup

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

EXTRA_CSS = """
/* Navigation & Mobile Drawer z-index hierarchy */
.ltt-navbar {
  z-index: 100000 !important;
}
.ltt-mobile-drawer {
  z-index: 100000 !important;
}
.ltt-drawer-content {
  padding-bottom: 50px !important;
}

/* Floating Sticky Bottom Bar z-index & Mobile Drawer conflict suppression */
.hybrid-sticky-bar,
.sticky-mobile-bar,
#sticky-bar {
  z-index: 9990 !important;
}

body.ltt-drawer-open #sticky-bar,
body.ltt-drawer-open .hybrid-sticky-bar,
body.ltt-drawer-open .sticky-mobile-bar,
body:has(.ltt-mobile-drawer.is-open) #sticky-bar,
body:has(.ltt-mobile-drawer.is-open) .hybrid-sticky-bar,
body:has(.ltt-mobile-drawer.is-open) .sticky-mobile-bar {
  display: none !important;
  opacity: 0 !important;
  pointer-events: none !important;
  visibility: hidden !important;
  transform: translateY(150%) !important;
}

/* Mobile Toggle Hamburger Button & Symmetrical X Animation */
.ltt-hamburger {
  width: 42px !important;
  height: 42px !important;
  padding: 10px 8px !important;
  background: transparent !important;
  border: 1px solid #cbd5e1 !important;
  border-radius: 10px !important;
  cursor: pointer !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  align-items: center !important;
  box-sizing: border-box !important;
  position: relative !important;
}
.ltt-hamburger:hover {
  background: #f8fafc !important;
}
.ltt-hamburger-bar {
  display: block !important;
  width: 22px !important;
  height: 2px !important;
  background: #0f172a !important;
  border-radius: 2px !important;
  transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.2s ease !important;
  transform-origin: center !important;
}
.ltt-hamburger.is-active .ltt-hamburger-bar:nth-child(1) {
  transform: translateY(10px) rotate(45deg) !important;
}
.ltt-hamburger.is-active .ltt-hamburger-bar:nth-child(2) {
  opacity: 0 !important;
  transform: scaleX(0) !important;
}
.ltt-hamburger.is-active .ltt-hamburger-bar:nth-child(3) {
  transform: translateY(-10px) rotate(-45deg) !important;
}
"""

def update_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # 1. Update style tag #ltt-language-switcher-styles
    if 'id="ltt-language-switcher-styles"' in content:
        if '/* Navigation & Mobile Drawer z-index hierarchy */' not in content:
            content = content.replace('</style>', f'{EXTRA_CSS}\n</style>', 1)
            changed = True

    # 2. Fix updateFloatingCTA logic
    # Replace premature accordion disappearance:
    # Pattern: var isPastReviews = (lastBottom < 100); ... if (!hasPassedHero || isPastReviews)
    if 'updateFloatingCTA' in content:
        old_pattern = re.compile(
            r'(function updateFloatingCTA\(\)\s*\{[\s\S]*?)(var lastRev\s*=\s*reviews\.length\s*\?\s*reviews\[reviews\.length\s*-\s*1\]\s*:\s*cards\[cards\.length\s*-\s*1\];[\s\S]*?var isPastReviews\s*=\s*\(lastBottom\s*<\s*100\);[\s\S]*?if\s*\(!hasPassedHero\s*\|\|\s*isPastReviews\)\s*\{\s*bar\.classList\.remove\([^\)]+\);\s*return;\s*\})',
            re.MULTILINE
        )
        def replace_floating(m):
            header = m.group(1)
            # Ensure drawer check
            if 'document.body.classList.contains(\'ltt-drawer-open\')' not in header:
                header = header.replace(
                    'var bar = document.getElementById(\'sticky-bar\');',
                    'if (document.body.classList.contains(\'ltt-drawer-open\')) return;\n    var bar = document.getElementById(\'sticky-bar\') || document.querySelector(\'.hybrid-sticky-bar\');'
                )
            replacement = (
                'var lastRev = reviews.length ? reviews[reviews.length - 1] : cards[cards.length - 1];\n'
                '    var lastBottom = lastRev.getBoundingClientRect().bottom;\n'
                '    var hasPassedHero = (window.scrollY > 350);\n'
                '    var isPastReviews = (lastBottom < 100);\n'
                '    var deck = document.getElementById(deckId) || document.getElementById(\'ltt-cards-deck\');\n'
                '    var brk = document.getElementById(\'breakdown-header\');\n'
                '    var isBetweenDeckAndReviews = (deck && brk && deck.getBoundingClientRect().bottom < vCenter && brk.getBoundingClientRect().top > vCenter);\n'
                '    if (!hasPassedHero || isPastReviews || isBetweenDeckAndReviews) {\n'
                '      bar.classList.remove(\'visible\', \'is-visible\');\n'
                '      return;\n'
                '    }'
            )
            return header + replacement

        new_content, n = old_pattern.subn(replace_floating, content)
        if n > 0:
            content = new_content
            changed = True

    # 3. Fix drawer toggle to add/remove 'ltt-drawer-open' on document.body
    if 'lttNavToggle' in content and 'ltt-drawer-open' not in content:
        # Check standard toggle block
        old_drawer_open = "drawer.classList.add('is-open');\n            toggle.classList.add('is-active');\n            toggle.setAttribute('aria-expanded', 'true');\n            drawer.setAttribute('aria-hidden', 'false');"
        new_drawer_open = "drawer.classList.add('is-open');\n            toggle.classList.add('is-active');\n            toggle.setAttribute('aria-expanded', 'true');\n            drawer.setAttribute('aria-hidden', 'false');\n            document.body.classList.add('ltt-drawer-open');"

        old_drawer_close = "drawer.classList.remove('is-open');\n            toggle.classList.remove('is-active');\n            toggle.setAttribute('aria-expanded', 'false');\n            drawer.setAttribute('aria-hidden', 'true');"
        new_drawer_close = "drawer.classList.remove('is-open');\n            toggle.classList.remove('is-active');\n            toggle.setAttribute('aria-expanded', 'false');\n            drawer.setAttribute('aria-hidden', 'true');\n            document.body.classList.remove('ltt-drawer-open');"

        if old_drawer_open in content:
            content = content.replace(old_drawer_open, new_drawer_open)
            changed = True
        if old_drawer_close in content:
            content = content.replace(old_drawer_close, new_drawer_close)
            changed = True

    if changed:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    print("Beginning parity update across The Cruise Detective...")
    target_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith('.html'):
                target_files.append(os.path.join(root, f))

    print(f"Found {len(target_files)} HTML files in cruisedetective.")
    updated_count = 0
    for tf in target_files:
        if update_file(tf):
            updated_count += 1

    print(f"Successfully updated {updated_count} files in The Cruise Detective!")

if __name__ == '__main__':
    main()
