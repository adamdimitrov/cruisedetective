#!/usr/bin/env python3
"""Pre-ship checks for a branch, run from the worktree before opening the PR.

  python3 scripts/ship/preflight.py          # report only
  python3 scripts/ship/preflight.py --fix    # also bump sitemap lastmod for changed pages

Checks (against origin/main, including uncommitted changes):
  1. Em dashes (—) in added lines of site files (house rule: never in copy/meta/JSON-LD)
  2. Changed JS files: each must get a new ?v= in the HTML that loads it (.js is cached 1y immutable)
  3. vercel.json: the /webflow-sync.js cache rule must come after every generic .js rule
  4. sitemap.xml: lastmod bumped for every changed page that is in the sitemap
  5. Affiliate-link rules on changed pages that have comparison cards (scripts/cards/cards.py links)
Exit 1 when a check fails.
"""
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
SITE = "https://www.thecruisedetective.com"
SITE_EXT = (".html", ".json", ".md", ".txt", ".xml")


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True).stdout


def base():
    return sh("git merge-base origin/main HEAD").strip() or "origin/main"


def changed_files():
    out = sh(f"git -c core.quotePath=false diff --name-only {base()}; git -c core.quotePath=false ls-files -o --exclude-standard")
    return sorted({f for f in out.splitlines() if f.strip()})


def added_lines(path):
    diff = sh(f"git diff -U0 {base()} -- '{path}'")
    if not diff and (ROOT / path).exists() and path in sh("git -c core.quotePath=false ls-files -o --exclude-standard"):
        return (ROOT / path).read_text(encoding="utf-8", errors="ignore").splitlines()
    return [l[1:] for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]


def page_url(path):
    p = Path(path)
    if p.name != "index.html":
        return None
    rel = str(p.parent)
    return SITE + ("" if rel == "." else "/" + rel)


def main():
    fix = "--fix" in sys.argv
    files = changed_files()
    fails, warns = [], []
    print(f"{len(files)} changed file(s) vs merge-base with origin/main")

    # 1. em dashes
    for f in files:
        if not f.endswith(SITE_EXT) or f.startswith((".claude/", "scripts/", "reports/", "social/")):
            continue
        hits = [l.strip()[:100] for l in added_lines(f) if "—" in l and "<!--" not in l]
        if hits:
            fails.append(f"em dash in {f}: {len(hits)} added line(s), e.g. “{hits[0]}”")

    # 2. JS cache busting
    for f in files:
        if not f.endswith(".js") or f.startswith(("api/", "test/", "scripts/", ".claude/")):
            continue
        name = Path(f).name
        if name == "webflow-sync.js":
            continue  # has its own 5-minute cache rule
        bumped = re.search(re.escape(name) + r"\?v=", sh(f"git diff -U0 {base()} -- '*.html'"))
        if not bumped:
            fails.append(f"{f} changed but no HTML got a new {name}?v=… (browsers keep the old file for a year)")

    # 3. vercel.json rule order
    try:
        hdrs = json.loads((ROOT / "vercel.json").read_text())["headers"]
        js_rules = [i for i, h in enumerate(hdrs)
                    if re.search(r"(\(|\||\.|:)js(\)|\||$)", h["source"]) and "webflow-sync" not in h["source"]]
        wf = [i for i, h in enumerate(hdrs) if "webflow-sync.js" in h["source"]]
        if wf and js_rules and wf[0] < max(js_rules):
            fails.append("vercel.json: /webflow-sync.js rule must be after the generic .js rules (last match wins)")
    except Exception as e:
        fails.append(f"vercel.json unreadable: {e}")

    # 4. sitemap lastmod
    sm_path = ROOT / "sitemap.xml"
    sm = sm_path.read_text(encoding="utf-8")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:00:00+00:00")
    stale = []
    for f in files:
        url = page_url(f)
        if not url:
            continue
        for cand in {url, SITE + "/" + unquote(url[len(SITE) + 1:])} if url != SITE else {url, SITE + "/"}:
            m = re.search(r"<loc>" + re.escape(cand) + r"</loc>\s*<lastmod>([^<]+)</lastmod>", sm)
            if m:
                if "sitemap.xml" not in files or m.group(1)[:10] < now[:10]:
                    stale.append((cand, m.group(1)))
                break
    if stale:
        if fix:
            for loc, old in stale:
                sm = sm.replace(f"<loc>{loc}</loc>\n    <lastmod>{old}</lastmod>",
                                f"<loc>{loc}</loc>\n    <lastmod>{now}</lastmod>")
            sm_path.write_text(sm, encoding="utf-8")
            print(f"bumped lastmod to {now} for {len(stale)} URL(s)")
        else:
            fails.append(f"sitemap lastmod not bumped for {len(stale)} page(s): " +
                         ", ".join(l.replace(SITE, '') or '/' for l, _ in stale[:5]) + " (run with --fix)")

    # 5. affiliate links on changed card pages
    card_pages = [f for f in files if f.endswith("index.html") and (ROOT / f).exists()
                  and 'class="bpa-card"' in (ROOT / f).read_text(encoding="utf-8", errors="ignore")]
    if card_pages:
        r = subprocess.run([sys.executable, "scripts/cards/cards.py", "links", *card_pages],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode:
            fails.append("affiliate link problems:\n" + r.stdout.strip())

    for w in warns:
        print("⚠", w)
    for f in fails:
        print("✗", f)
    if not fails:
        print("✓ preflight passed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
