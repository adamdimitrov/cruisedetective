#!/usr/bin/env python3
"""Card photo galleries stay clipped when a popover opens.

    python3 kit/checks/check_gallery_clip.py     # exit 1 on any problem (runs in CI)

Popovers (price dropdown, pill dropdowns) escape their card with a rule like
`.bpa-card:has(.cd-pdd[open]) *{overflow:visible!important}`. A blanket `*` like that
also unclips every thumbnail (.cd-thumb) and the slider, so the photos lose their
rounded corners and spill over the gaps while the popover is open (kit v0.11.2 fix).

This check fails on any CSS rule, in a .css file or a page's inline <style>, that sets
overflow (or overflow-x/-y) to visible on
  - a descendant `*` selector that does not exclude the gallery with
    `:not(.cd-gal):not(.cd-gal *)`, or
  - the gallery itself: .cd-gal, .cd-thumbs, .cd-thumb, .bpa-slider.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitecfg import ROOT  # noqa: E402

SKIP_DIRS = ("css/purged/", "scripts/archive/", "node_modules/", "archive/")
GALLERY = re.compile(r"\.(?:cd-gal|cd-thumbs?|bpa-slider)(?![\w-])")
RULE = re.compile(r"([^{}]*)\{([^{}]*)\}")
VISIBLE = re.compile(r"overflow(?:-[xy])?\s*:\s*visible", re.I)
STYLE = re.compile(r"<style[^>]*>(.*?)</style>", re.S | re.I)
EXCLUDES = ":not(.cd-gal):not(.cd-gal *)"


def bad_selectors(css):
    for m in RULE.finditer(css):
        if not VISIBLE.search(m.group(2)):
            continue
        sel_text = m.group(1).split(";")[-1].strip()
        if sel_text.startswith("@"):
            continue
        for sel in (s.strip() for s in sel_text.split(",")):
            compact = re.sub(r"\s+", " ", sel)
            last = re.split(r"\s+|>|~|\+", re.sub(r":not\([^)]*\)", "", compact).strip())[-1]
            if last.startswith("*") and " " in compact.strip() and EXCLUDES not in compact:
                yield compact
            elif GALLERY.search(last):
                yield compact


def main():
    files = subprocess.run(["git", "-c", "core.quotepath=off", "ls-files", "-z", "*.css", "*.html"],
                           cwd=ROOT, capture_output=True, text=True).stdout.split("\0")
    problems = 0
    checked = 0
    for f in filter(None, files):
        if f.startswith(SKIP_DIRS):
            continue
        try:
            with open(os.path.join(ROOT, f), encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except FileNotFoundError:
            continue
        if "overflow" not in text:
            continue
        checked += 1
        css = text if f.endswith(".css") else "\n".join(STYLE.findall(text))
        for sel in bad_selectors(css):
            problems += 1
            print(f"FAIL {f}: `{sel}` sets overflow:visible on the card gallery; "
                  f"add {EXCLUDES} after the `*`")
    print(f"checked {checked} file(s): {problems} rule(s) unclip a card gallery")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
