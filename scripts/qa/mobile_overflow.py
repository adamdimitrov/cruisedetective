#!/usr/bin/env python3
"""Phone-width overflow check (375px) for static pages, run before shipping.

Usage
  python3 scripts/qa/mobile_overflow.py                      # pages changed vs origin/main
  python3 scripts/qa/mobile_overflow.py seine-river-cruises-paris dinner-cruises-paris
  python3 scripts/qa/mobile_overflow.py --all-money          # the 4 EN money pages + translations
  options: --width 375  --no-details (don't open <details> popovers)  --shots DIR

Reports any element whose box sticks out past the viewport (horizontal scroll on a
phone), ignoring content inside horizontal scrollers such as the photo sliders.
Exit 1 when something overflows.
"""
import argparse
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]

PROBE = r"""
(openDetails) => {
  if (openDetails) document.querySelectorAll('details').forEach(d => d.open = true);
  const vw = document.documentElement.clientWidth;
  const inScroller = el => {
    for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) {
      const s = getComputedStyle(p);
      if (/(auto|scroll|hidden|clip)/.test(s.overflowX) && p.scrollWidth > p.clientWidth + 1) return true;
    }
    return false;
  };
  const visible = el => {
    const s = getComputedStyle(el);
    return s.display !== 'none' && s.visibility !== 'hidden' && s.position !== 'fixed' && el.offsetParent !== null;
  };
  const path = el => {
    const parts = [];
    for (let e = el; e && e !== document.body && parts.length < 4; e = e.parentElement) {
      let p = e.tagName.toLowerCase();
      if (e.id) { p += '#' + e.id; parts.unshift(p); break; }
      if (e.classList.length) p += '.' + [...e.classList].slice(0, 2).join('.');
      parts.unshift(p);
    }
    return parts.join(' > ');
  };
  const hits = [];
  for (const el of document.body.querySelectorAll('*')) {
    if (!visible(el)) continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0) continue;
    const over = Math.round(r.right - vw);
    if (over > 1 || r.left < -1) {
      if (inScroller(el)) continue;
      hits.push({sel: path(el), over, left: Math.round(r.left), width: Math.round(r.width),
                 text: (el.innerText || '').trim().slice(0, 60)});
    }
  }
  // keep only the outermost offenders
  const out = hits.filter(h => !hits.some(o => o !== h && h.sel.startsWith(o.sel + ' >')));
  return {vw, scrollWidth: document.documentElement.scrollWidth, hits: out.slice(0, 15)};
}
"""

MONEY = ["seine-river-cruises-paris", "dinner-cruises-paris", "thames-river-cruises-london",
         "canal-cruises-amsterdam", "new-years-eve-cruises-paris"]


def changed_pages():
    cmd = "git -c core.quotePath=false diff --name-only origin/main...HEAD; git -c core.quotePath=false diff --name-only; git -c core.quotePath=false ls-files -o --exclude-standard"
    out = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True).stdout
    pages = sorted({str(Path(f).parent) for f in out.split() if f.endswith("index.html")})
    return [p if p != "." else "" for p in pages]


def free_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pages", nargs="*")
    ap.add_argument("--width", type=int, default=375)
    ap.add_argument("--all-money", action="store_true")
    ap.add_argument("--no-details", action="store_true")
    ap.add_argument("--shots")
    a = ap.parse_args()

    pages = a.pages
    if a.all_money:
        sys.path.insert(0, str(ROOT / "scripts" / "cards"))
        from cards import extract, page_path  # noqa
        pages = []
        for p in MONEY:
            pages.append(p)
            alts = extract(page_path(p))["alternates"]
            for lang, url in alts.items():
                if lang not in ("en", "x-default"):
                    pages.append(url.split(".com/", 1)[1])
    if not pages:
        pages = changed_pages()
    if not pages:
        print("No changed pages. Pass page folders explicitly.")
        return 0

    port = free_port()
    srv = subprocess.Popen([sys.executable, str(ROOT / "scripts" / "preview_server.py"), str(port)],
                           cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    bad = 0
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            br = pw.chromium.launch()
            ctx = br.new_context(viewport={"width": a.width, "height": 812}, device_scale_factor=2,
                                 is_mobile=True, has_touch=True)
            page = ctx.new_page()
            for p in pages:
                url = f"http://127.0.0.1:{port}/{quote(p.strip('/'))}"
                try:
                    page.goto(url, wait_until="load", timeout=30000)
                except Exception as e:
                    print(f"✗ {p or '/'}: load failed: {e}")
                    bad += 1
                    continue
                page.wait_for_timeout(400)
                res = page.evaluate(PROBE, not a.no_details)
                if res["hits"]:
                    bad += 1
                    print(f"✗ {p or '/'}  (scrollWidth {res['scrollWidth']} > {res['vw']})" if res["scrollWidth"] > res["vw"]
                          else f"✗ {p or '/'}  (clipped elements)")
                    for h in res["hits"]:
                        print(f"    +{h['over']}px  {h['sel']}  “{h['text']}”")
                else:
                    print(f"✓ {p or '/'}")
                if a.shots:
                    Path(a.shots).mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=str(Path(a.shots) / (p.replace('/', '_') or 'home') ) + ".png", full_page=False)
            br.close()
    finally:
        srv.terminate()
    print(f"\n{bad} page(s) with overflow out of {len(pages)} at {a.width}px")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
