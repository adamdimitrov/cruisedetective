#!/usr/bin/env python3
"""Measure listicle pages in a real browser: what longer languages break.

    python3 kit/checks/check_listicle_layout.py                 # every page in site.json listicle.pages
    python3 kit/checks/check_listicle_layout.py de/page/index.html other.html
    python3 kit/checks/check_listicle_layout.py --strict        # fail (not skip) when no browser

Opens each page at phone width (390 px) and desktop width (1440 px) from a local server (external
hosts blocked) and fails on:
  - a rank tag on a card photo that is cut off, or that listicle-cards.js had to shrink below 10 px
    (the translation is too long: shorten it in data/listicles/i18n/<page>/<lang>.json),
  - a booking button whose label is cut off,
  - sideways overflow (the page is wider than the screen).

Needs Node with Playwright and Chromium (`npm i playwright` and `npx playwright install chromium`).
Without them it prints "skipped" and exits 0, so CI without a browser still passes; `listicle.py
build-lang` runs it on the page it just built.
"""
import http.server
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitecfg import ROOT, SITE  # noqa: E402

MIN_TAG_PX = 10
VIEWPORTS = [("phone", {"viewport": {"width": 390, "height": 844}, "isMobile": True, "hasTouch": True}),
             ("desktop", {"viewport": {"width": 1440, "height": 900}})]

NODE = r"""
const { chromium } = require('playwright');
const [base, pagesJson, vpJson, minTag] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const out = {};
  for (const page of JSON.parse(pagesJson)) {
    out[page] = [];
    for (const [name, opts] of JSON.parse(vpJson)) {
      const ctx = await b.newContext(opts); const p = await ctx.newPage();
      await p.route('**/*', r => r.request().url().startsWith(base) ? r.continue() : r.abort());
      try { await p.goto(base + '/' + page, { waitUntil: 'load', timeout: 60000 }); }
      catch (e) { out[page].push(name + ': page did not load (' + e.message.split('\n')[0] + ')'); await ctx.close(); continue; }
      await p.waitForTimeout(900);
      const probs = await p.evaluate(minTag => {
        const res = [], cut = el => el.scrollWidth > el.clientWidth + 1;
        const txt = el => el.innerText.replace(/\s+/g, ' ').trim().slice(0, 60);
        document.querySelectorAll('.bpa-card').forEach((c, i) => {
          const id = c.id || ('card ' + (i + 1));
          const tag = c.querySelector('.bpa-media .bpa-rank-tag'), media = c.querySelector('.bpa-media');
          if (tag && tag.offsetParent) {
            const fs = parseFloat(getComputedStyle(tag).fontSize);
            if (cut(tag)) res.push(id + ': rank tag cut off: "' + txt(tag) + '" (shorten the translation)');
            else if (fs < minTag) res.push(id + ': rank tag shrunk to ' + fs + 'px to fit: "' + txt(tag) + '" (shorten the translation)');
            if (media && tag.getBoundingClientRect().height > media.getBoundingClientRect().height * 0.25)
              res.push(id + ': rank tag covers ' + Math.round(tag.getBoundingClientRect().height / media.getBoundingClientRect().height * 100) + '% of the photo');
          }
          c.querySelectorAll('.bpa-btn').forEach(btn => {
            if (btn.offsetParent && cut(btn)) res.push(id + ': booking button cut off: "' + txt(btn) + '"');
          });
        });
        const sw = document.documentElement.scrollWidth, iw = window.innerWidth;
        if (sw > iw + 1) res.push('page is ' + sw + 'px wide on a ' + iw + 'px screen (sideways overflow)');
        return res;
      }, +minTag);
      probs.forEach(x => out[page].push(name + ': ' + x));
      await ctx.close();
    }
  }
  await b.close(); console.log(JSON.stringify(out));
})().catch(e => { console.error(e.message); process.exit(3); });
"""


def browser_available():
    """True when `node` can load Playwright (and so drive Chromium)."""
    if not shutil.which("node"):
        return False
    r = subprocess.run(["node", "-e", "require('playwright')"], capture_output=True, text=True)
    return r.returncode == 0


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def measure(pages):
    """{page: [problem, ...]} for site-relative page paths; None when no browser is available."""
    if not browser_available():
        return None
    handler = lambda *a, **k: _Quiet(*a, directory=ROOT, **k)  # noqa: E731
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False) as fh:
            fh.write(NODE)
            script = fh.name
        r = subprocess.run(["node", script, f"http://127.0.0.1:{srv.server_address[1]}", json.dumps(pages),
                            json.dumps(VIEWPORTS), str(MIN_TAG_PX)], capture_output=True, text=True, timeout=900)
        os.unlink(script)
        if r.returncode != 0:
            raise RuntimeError(f"browser run failed: {r.stderr.strip()[:300]}")
        return json.loads(r.stdout.strip().splitlines()[-1])
    finally:
        srv.shutdown()


def check(pages, strict=False, quiet=False):
    """Print the result; return 0 when every page passes (or no browser and not strict), else 1."""
    res = measure(pages)
    if res is None:
        print("listicle layout: skipped, no browser (Node + Playwright); run it where one is installed")
        return 1 if strict else 0
    bad = 0
    for page in pages:
        probs = res.get(page, [])
        if probs:
            bad += 1
            print(f"{page}: {len(probs)} layout problem(s)")
            print("\n".join("  " + x for x in probs))
        elif not quiet:
            print(f"{page}: layout ok (phone and desktop)")
    print(f"listicle layout: {len(pages)} page(s) measured, {bad} with problems")
    return 1 if bad else 0


def main(argv):
    strict = "--strict" in argv
    pages = [a for a in argv if not a.startswith("--")] or SITE.get("listicle", {}).get("pages", [])
    if not pages:
        print("listicle layout: no listicle pages in site.json")
        return 0
    return check(pages, strict=strict)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
