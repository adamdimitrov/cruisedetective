#!/usr/bin/env python3
"""
Apply 1:1 Budapest Adventures Layout Parity across The Cruise Detective
Matches budapestadventures.com/best-budapest-river-cruises:
1. Container & Grid Geometry:
   - .container-31, .container-26: max-width 1240px, margin 0 auto, padding 0 16px
   - .blog-grid-2, .blog-grid: padding-left 270px, position relative, display block
   - .content-left: width 230px, position absolute, top 0, bottom 0, left 0
   - .stick-wrapper: position sticky, top 88px, max-height calc(100vh - 104px)
   - .content-right_blog: max-width 920px, width 100%
   - .bpa-details-card: max-width 920px, width 100%
   - .ltt-editorial-wrapper: max-width 920px, width 100%, margin 60px auto 0 auto
2. Table of Contents Scope:
   - Desktop sidebar TOC strictly contains Top 10 Comparison, Detailed Breakdown, and the 10 cruise reviews.
   - Eliminates trailing Buyer's Guide clutter in #toc so it fits 100% cleanly without colliding with the bottom floating bar.
"""

import os
import glob
import re

BASE_DIR = '/Users/adamdimitrov/Development/cruisedetective'

PARITY_CSS = """
/* ==========================================================================
   CANONICAL BUDAPEST ADVENTURES PARITY GRID & TOC GEOMETRY
   ========================================================================== */
.container-31, .container-26 {
  width: 100% !important;
  max-width: 1240px !important;
  margin: 0 auto !important;
  padding: 0 16px !important;
  box-sizing: border-box !important;
}
.blog-grid-2, .blog-grid {
  position: relative !important;
  display: block !important;
  padding-left: 270px !important;
  box-sizing: border-box !important;
  width: 100% !important;
}
.content-left {
  display: block !important;
  width: 230px !important;
  position: absolute !important;
  top: 0 !important;
  bottom: 0 !important;
  left: 0 !important;
  inset: 0% auto 0% 0% !important;
}
.stick-wrapper {
  position: sticky !important;
  top: 88px !important;
  max-height: calc(100vh - 104px) !important;
  overflow-y: auto !important;
  z-index: 90 !important;
  padding-top: 6px !important;
}
.content-right_blog {
  width: 100% !important;
  max-width: 920px !important;
  box-sizing: border-box !important;
  display: block !important;
}
.container-33 {
  width: 100% !important;
  max-width: 100% !important;
  margin: 0 !important;
  padding: 0 !important;
}
.bpa-details-card {
  width: 100% !important;
  max-width: 920px !important;
  box-sizing: border-box !important;
}
.ltt-editorial-wrapper {
  width: 100% !important;
  max-width: 920px !important;
  margin: 60px auto 0 auto !important;
  box-sizing: border-box !important;
}
@media (max-width: 991px) {
  .blog-grid-2, .blog-grid {
    padding-left: 0 !important;
    display: block !important;
  }
  .content-left {
    display: none !important;
  }
  .content-right_blog {
    max-width: 100% !important;
    width: 100% !important;
  }
}
"""

def update_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # 1. Inject or update PARITY_CSS
    if 'CANONICAL BUDAPEST ADVENTURES PARITY GRID & TOC GEOMETRY' not in content:
        # Inject inside ltt-dubai-safari-styles or after #ltt-language-switcher-styles
        if '</style>' in content:
            content = content.replace('</style>', f'{PARITY_CSS}\n</style>', 1)
            changed = True

    # 2. Update syncSidebarTOC to not append guideSections into desktop #toc
    # Look for the block appending guideSections to desktop toc
    guide_block_regex = re.compile(
        r'if\s*\(\s*guideSections\.length\s*\)\s*\{\s*'
        r'var grp\s*=\s*document\.createElement\([\'"]div[\'"]\);\s*'
        r'grp\.className\s*=\s*[\'"]toc-group-label[\'"];\s*'
        r'grp\.textContent\s*=\s*[^;]+;\s*'
        r'frag\.appendChild\(grp\);\s*'
        r'guideSections\.forEach\(function\(g\)\s*\{[\s\S]*?items\.push\(\{[^\}]+\}\);\s*\}\);\s*'
        r'\}'
    )
    if guide_block_regex.search(content):
        # Remove it so desktop TOC only contains itemsData (the 10 reviews)
        content = guide_block_regex.sub('/* guideSections kept for mobile hybridSheet only */', content)
        changed = True

    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    files = glob.glob(os.path.join(BASE_DIR, '**/*.html'), recursive=True)
    count = 0
    for f in files:
        with open(f, 'r', encoding='utf-8') as fh:
            c = fh.read()
        if 'function updateFloatingCTA' in c:
            if update_file(f):
                count += 1
                print(f"Updated: {os.path.relpath(f, BASE_DIR)}")

    print(f"\nSuccessfully applied Budapest Adventures parity across {count} files.")

if __name__ == '__main__':
    main()
