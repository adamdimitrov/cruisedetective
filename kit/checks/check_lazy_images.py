#!/usr/bin/env python3
"""Every lazy-loaded photo on every published page actually gets loaded.

    python3 kit/checks/check_lazy_images.py            # report only, exit 1 on any problem
    python3 kit/checks/check_lazy_images.py --fix      # upgrade old slider runtimes in place, then re-check
    python3 kit/checks/check_lazy_images.py --report   # per-file counts

Why: images are often shipped as a blank placeholder (src="data:...") with the
real URL in data-src / data-srcset, and some JavaScript has to swap it in. If a
page has the placeholders but not the loader, the photo stays blank (this hit
39 pages in Nov 2026: carousel slides 2+ were empty dark cards).

What it checks, on every .html file that .vercelignore does not exclude:

  1. Carousel photos (img[data-src] inside .bpa-slider): the page runtime must
     define loadSliderImages(), call it from bpaSlide() (arrow buttons), and
     bind it to swipe/touch/hover via initLazySliders() which initAll() runs.
     If any slider uses data-srcset, the loader must copy data-srcset too.
  2. The first photo of each carousel has a real src (not a placeholder), so
     the visible slide is never blank before any interaction.
  3. Menu thumbnails (img.ltt-thumb[data-src]): the page must have the menu
     thumbnail loader.
  3b. Carousels with data-more="a.webp,/assets/b.webp" (extra slides appended by
     script): the page has the data-more loader, and it does not double the
     CDN prefix onto paths that are already absolute.
  4. Any other element with a lazy attribute (data-src, data-srcset, data-bg,
     data-lazy, data-original, ...) is an unknown pattern with no known loader
     and fails, so a new lazy-loading scheme cannot ship without a check here.
  4b. No photo is hotlinked from someone else's site: <img> src/data-src must be a
     local file or a host in ALLOWED_IMAGE_HOSTS.
  5. Every local image URL used by a photo (src, data-src, srcset,
     data-srcset) points at a file that exists in the repo.

--fix upgrades the known old runtime (bpaSlide without loadSliderImages) to the
current one; anything else it reports for a manual fix.
"""

import argparse
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitecfg import ROOT, SITE, published_html  # noqa: E402
LAZY_ATTRS = ("data-src", "data-srcset", "data-bg", "data-background",
              "data-lazy", "data-lazy-src", "data-original", "data-bg-src")
# Photos may only come from our own files or the hosts in site.json images.allowed_hosts.
# Anything else is a hotlink to someone else's site: it can vanish or block us any day.
ALLOWED_IMAGE_HOSTS = {h.lower() for h in SITE.get("images", {}).get("allowed_hosts", [])}
DATA_MORE_CDN = SITE.get("images", {}).get("data_more_prefix", "/assets/")
# the old data-more loader prefixed the CDN folder even onto absolute paths -> /assets/.../\/assets/...
OLD_DATA_MORE = 'img.src = f.startsWith("http") ? f : BPA_CDN + f;'
NEW_DATA_MORE = 'img.src = (f.startsWith("http") || f.startsWith("/")) ? f : BPA_CDN + f;'
VOID = {"img", "br", "input", "meta", "link", "source", "hr", "wbr", "area", "base", "col", "embed", "param", "track"}

# --- the runtime upgrade applied by --fix (same code the up-to-date pages ship) ---
OLD_SLIDER = """  // 1. Slider controls
  window.bpaSlide = function(btn, dir) {
    var media = btn.closest('.bpa-media');
    if (!media) return;
    var slider = media.querySelector('.bpa-slider');
    if (!slider) return;
    var w = slider.clientWidth;"""
NEW_SLIDER = """  // 1. Slider controls with Progressive Lazy-Loading
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

  function initLazySliders() {
    document.querySelectorAll('.bpa-slider').forEach(function(slider) {
      if (slider._lazyBound) return;
      slider._lazyBound = true;
      var media = slider.closest('.bpa-media');
      if (media) {
        media.addEventListener('mouseenter', function() { loadSliderImages(slider); }, { once: true, passive: true });
        media.addEventListener('touchstart', function() { loadSliderImages(slider); }, { once: true, passive: true });
      }
      slider.addEventListener('scroll', function() { loadSliderImages(slider); }, { once: true, passive: true });
    });
  }

  window.bpaSlide = function(btn, dir) {
    var media = btn.closest('.bpa-media');
    if (!media) return;
    var slider = media.querySelector('.bpa-slider');
    if (!slider) return;
    loadSliderImages(slider);
    var w = slider.clientWidth;"""
OLD_COUNT = "  window.bpaCount = function(slider) {\n    var media"
NEW_COUNT = "  window.bpaCount = function(slider) {\n    loadSliderImages(slider);\n    var media"
OLD_INIT = "  function initAll() {\n    initHybridSheet();\n"
NEW_INIT = "  function initAll() {\n    initLazySliders();\n    initHybridSheet();\n"


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, class)
        self.slider_depth = None
        self.slider_first = None  # first img of the current slider seen?
        self.sliders = 0
        self.slider_lazy = 0
        self.slider_srcset = 0
        self.blank_first = 0
        self.thumbs = 0
        self.data_more = 0
        self.hotlinks = []
        self.unknown = []
        self.urls = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = a.get("class") or ""
        classes = cls.split()
        in_slider = self.slider_depth is not None
        if tag == "img":
            for k in ("src", "data-src"):
                if a.get(k):
                    self.urls.append(a[k])
                    m = re.match(r"(?:https?:)?//([^/]+)", a[k])
                    if m and m.group(1).lower() not in ALLOWED_IMAGE_HOSTS:
                        self.hotlinks.append(a[k])
            for k in ("srcset", "data-srcset"):
                for part in (a.get(k) or "").split(","):
                    if part.strip():
                        self.urls.append(part.strip().split()[0])
        if "data-more" in a and "bpa-slider" in classes:
            # extra slides appended by the page's data-more loader (bare names get the CDN prefix)
            self.data_more += 1
            for f in (a.get("data-more") or "").split(","):
                f = f.strip()
                if f:
                    self.urls.append(f if f.startswith(("/", "http")) else DATA_MORE_CDN + f)
        lazy = [k for k in a if k in LAZY_ATTRS]
        if tag == "img" and in_slider:
            if self.slider_first:
                self.slider_first = False
                src = a.get("src") or ""
                if not src or src.startswith("data:") or "data-src" in a:
                    self.blank_first += 1
            if lazy:
                self.slider_lazy += 1
                if "data-srcset" in a:
                    self.slider_srcset += 1
                if set(lazy) - {"data-src", "data-srcset"}:
                    self.unknown.append(f"<{tag} {' '.join(lazy)}> in .bpa-slider")
        elif lazy:
            if tag == "img" and "ltt-thumb" in classes and set(lazy) == {"data-src"}:
                self.thumbs += 1
            else:
                self.unknown.append(f"<{tag} class=\"{cls[:40]}\" {' '.join(lazy)}>")
        if tag in VOID:
            return
        self.stack.append((tag, cls))
        if "bpa-slider" in classes and not in_slider:
            self.slider_depth = len(self.stack)
            self.slider_first = True
            self.sliders += 1

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                break
        if self.slider_depth is not None and len(self.stack) < self.slider_depth:
            self.slider_depth = None
            self.slider_first = None


def strip_comments(js):
    return re.sub(r"/\*.*?\*/", "", js, flags=re.S)


def page_problems(path, html):
    s = Scan()
    s.feed(html)
    s.close()
    probs = []
    scripts = strip_comments("\n".join(re.findall(r"<script\b[^>]*>(.*?)</script>", html, flags=re.S | re.I)))

    if s.slider_lazy:
        if "function loadSliderImages" not in scripts:
            probs.append(f"{s.slider_lazy} carousel photo(s) use data-src but the page has no loadSliderImages() loader")
        else:
            m = re.search(r"window\.bpaSlide\s*=\s*function[^{]*\{(.*?)\n  \};", scripts, flags=re.S)
            if not m or "loadSliderImages(" not in m.group(1):
                probs.append("bpaSlide() (arrow buttons) does not call loadSliderImages()")
            wired_events = ("function initLazySliders" in scripts
                            and re.search(r"^\s*initLazySliders\(\);", scripts, flags=re.M))
            io = re.search(r"new IntersectionObserver\(", scripts)
            wired_observer = bool(io) and "loadSliderImages(" in scripts[io.start():io.start() + 800]
            wired_delegated = any(
                "loadSliderImages(" in scripts[m.end():m.end() + 500]
                for m in re.finditer(r"document\.addEventListener\('(?:touchstart|scroll)'", scripts))
            mc = re.search(r"window\.bpaCount\s*=\s*function[^{]*\{(.*?)\n  \};", scripts, flags=re.S)
            wired_count = bool(mc) and "loadSliderImages(" in mc.group(1) and 'onscroll="bpaCount(this)"' in html
            if not (wired_events or wired_observer or wired_delegated or wired_count):
                probs.append("swipe/touch loading is not wired: no initLazySliders() call, no delegated touch/scroll listener, no "
                             "loadSliderImages() in bpaCount() and no "
                             "IntersectionObserver that calls loadSliderImages()")
            if s.slider_srcset and "data-srcset" not in scripts:
                probs.append("carousel photos use data-srcset but the loader never copies it")
    if s.data_more:
        if OLD_DATA_MORE in html:
            probs.append("data-more loader doubles absolute paths (/assets/... gets the CDN prefix again)")
        elif "[data-more]" not in scripts:
            probs.append(f"{s.data_more} carousel(s) use data-more but the page has no data-more loader")
    if s.blank_first:
        probs.append(f"{s.blank_first} carousel(s) start with a placeholder as the first photo (visible slide is blank)")
    if s.thumbs and not re.search(r"ltt-thumb\[data-src\][^\n]*getAttribute\('data-src'\)", scripts):
        probs.append(f"{s.thumbs} menu thumbnail(s) use data-src but the page has no thumbnail loader")
    for u in sorted(set(s.unknown))[:5]:
        probs.append(f"lazy attribute with no known loader: {u} (add a loader and a rule in this check)")

    for u in sorted(set(s.hotlinks))[:5]:
        probs.append(f"photo hotlinked from another site (can break any day): {u}")
    if len(set(s.hotlinks)) > 5:
        probs.append(f"... and {len(set(s.hotlinks)) - 5} more hotlinked photo(s)")

    missing = set()
    page_dir = os.path.dirname(path)
    for u in s.urls:
        if u.startswith(("data:", "http:", "https:", "//", "{", "#")) or "{" in u or "${" in u:
            continue
        p = urllib.parse.unquote(u.split("?")[0].split("#")[0])
        full = os.path.join(ROOT, p.lstrip("/")) if p.startswith("/") else os.path.join(ROOT, page_dir, p)
        if not os.path.isfile(full):
            missing.add(u)
    for u in sorted(missing)[:5]:
        probs.append(f"image file not found: {u}")
    if len(missing) > 5:
        probs.append(f"... and {len(missing) - 5} more missing image file(s)")
    return probs, s


def fix(rel, html):
    html = html.replace(OLD_DATA_MORE, NEW_DATA_MORE)
    if (OLD_COUNT in html and "function loadSliderImages" in html
            and page_problems(rel, html)[0] and "loadSliderImages(slider);\n    var media" not in html):
        probs = page_problems(rel, html)[0]
        if any("swipe/touch loading is not wired" in p for p in probs):
            return html.replace(OLD_COUNT, NEW_COUNT, 1)
    if OLD_SLIDER in html and "function loadSliderImages" not in html and html.count(OLD_INIT) == 1:
        return html.replace(OLD_SLIDER, NEW_SLIDER, 1).replace(OLD_INIT, NEW_INIT, 1)
    return html


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    bad = 0
    pages = sliders = 0
    for rel in published_html():
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as fh:
            html = fh.read()
        if args.fix:
            new = fix(rel, html)
            if new != html:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                print(f"fixed: {rel}")
                html = new
        probs, s = page_problems(rel, html)
        pages += 1
        sliders += s.sliders
        if args.report and (s.sliders or s.thumbs):
            print(f"{rel}: {s.sliders} carousel(s), {s.slider_lazy} lazy photo(s), {s.thumbs} lazy thumb(s)")
        if probs:
            bad += 1
            print(f"FAIL {rel}")
            for p in probs:
                print(f"     - {p}")
    print(f"checked {pages} pages, {sliders} carousels: {bad} page(s) with problems")
    if bad:
        print("Fix the runtime with: python3 kit/checks/check_lazy_images.py --fix")
        sys.exit(1)


if __name__ == "__main__":
    main()
