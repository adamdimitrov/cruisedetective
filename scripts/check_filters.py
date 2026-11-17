#!/usr/bin/env python3
"""Filter pills on comparison pages render correctly on load.

    python3 scripts/check_filters.py     # report only, exit 1 on any problem (runs in CI)

Why: the shared filter runtime (lttFilterItems + btnGroup) only treats buttons
that carry data-group as filters. A button without data-group behaves like
"All", so on load every pill is orange (active) and shows the total count.
This hit 12 pages built by scripts/build_article.py in Nov 2026.

Rules, on every published page whose filter runtime uses btnGroup:
  1. Every .ltt-tab-btn except data-cat="all" has a data-group.
  2. Exactly one button is active in the markup, and it is data-cat="all".
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_lazy_images import ROOT, published_html  # noqa: E402

BTN = re.compile(r'<button\b[^>]*class="ltt-tab-btn[^"]*"[^>]*>')


def problems(html):
    if "function btnGroup" not in html:
        return []
    out = []
    btns = BTN.findall(html)
    ungrouped = [b for b in btns if 'data-cat="all"' not in b and "data-group=" not in b]
    if ungrouped:
        cats = [re.search(r'data-cat="([^"]*)"', b).group(1) for b in ungrouped]
        out.append(f"{len(ungrouped)} filter button(s) without data-group (all pills render active): {', '.join(cats[:6])}")
    active = [b for b in btns if re.search(r'class="ltt-tab-btn[^"]*\bactive\b', b)]
    if btns and (len(active) != 1 or 'data-cat="all"' not in active[0]):
        out.append(f"{len(active)} button(s) active in the markup; expected only the \"all\" button")
    return out


def main():
    bad = pages = 0
    for rel in published_html():
        with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
            probs = problems(fh.read())
        pages += 1
        if probs:
            bad += 1
            print(f"FAIL {rel}")
            for p in probs:
                print(f"     - {p}")
    print(f"checked {pages} pages: {bad} page(s) with filter problems")
    if bad:
        print('Fix: give every non-"all" .ltt-tab-btn a data-group (build_article.py uses "fit").')
        sys.exit(1)


if __name__ == "__main__":
    main()
