#!/usr/bin/env python3
"""Every affiliate / OTA link carries rel="nofollow sponsored noopener".

  python3 scripts/fix_affiliate_rel.py            # fix in place, print per-file before/after counts
  python3 scripts/fix_affiliate_rel.py --check    # report only, exit 1 if any affiliate link lacks the tokens
  python3 scripts/fix_affiliate_rel.py --check FILE ...   # only these files
  python3 scripts/fix_affiliate_rel.py --md       # print the per-file counts as a Markdown table

Idempotent. Only the rel attribute of <a> tags whose href is an affiliate / OTA link is touched:
existing rel tokens are kept, missing ones are appended, nothing is duplicated. href, tracking
parameters, target and link text stay byte-for-byte the same.

Affiliate / OTA link = href host is getyourguide.com, tiqets.com, viator.com, tripadvisor.*,
tp.media / *.tp.st (Travelpayouts), fareharbor.com with ref=cruisedetective-asn, or any other
external host whose query has a partner/affiliate parameter (partner, partner_id, aid, pid,
marker, ref, affiliate, subid, ...). Internal links, Maps and plain operator sites are left alone.

Files walked: every tracked .html, the i18n/*.json string tables (keys and values), and tracked
.py / .js generators outside scripts/archive that contain literal affiliate <a> tags.
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ("nofollow", "sponsored", "noopener")
OTA_HOSTS = ("getyourguide.com", "tiqets.com", "viator.com", "tp.media", "tp.st", "tourradar.com")
OWN_HOSTS = ("thecruisedetective.com",)
AFF_PARAMS = {"partner", "partner_id", "aid", "pid", "marker", "ref", "affiliate", "affiliate_id",
              "aff_id", "affid", "subid", "sub_id", "clickref", "awc", "irclickid", "asn"}
SKIP_DIRS = (".claude/", "node_modules/", "scripts/archive/", "assets/", "test/")

A_TAG = re.compile(r"<a\b[^>]*>", re.I | re.S)
HREF = re.compile(r"""\shref\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>]+))""", re.I)
REL = re.compile(r"""(\srel\s*=\s*)(?:"([^"]*)"|'([^']*)'|([^\s>"']+))""", re.I)


def is_affiliate(href):
    if not href:
        return False
    href = html.unescape(href).strip()
    if not href.lower().startswith(("http://", "https://", "//")):
        return False
    u = urlparse(href if not href.startswith("//") else "https:" + href)
    host = (u.hostname or "").lower()
    if not host or any(host == h or host.endswith("." + h) for h in OWN_HOSTS):
        return False
    if any(host == h or host.endswith("." + h) for h in OTA_HOSTS):
        return True
    if host.startswith("tripadvisor.") or ".tripadvisor." in host:
        return True
    q = {k.lower(): v for k, v in parse_qs(u.query).items()}
    if host.endswith("fareharbor.com"):
        return q.get("ref", [""])[0] == "cruisedetective-asn" or bool(q.keys() & AFF_PARAMS)
    if "google." in host or host.endswith("goo.gl"):
        return False
    return bool(q.keys() & AFF_PARAMS)


def fix_tag(tag):
    """Return (new_tag, was_affiliate, was_missing)."""
    m = HREF.search(tag)
    href = m and next(g for g in m.groups() if g is not None)
    if not is_affiliate(href):
        return tag, False, False
    r = REL.search(tag)
    if r:
        val = next((g for g in r.groups()[1:] if g is not None), "")
        toks = val.split()
        low = {t.lower() for t in toks}
        add = [t for t in REQUIRED if t not in low]
        if not add:
            return tag, True, False
        new = " ".join(toks + add)
        return tag[:r.start()] + f'{r.group(1)}"{new}"' + tag[r.end():], True, True
    end = len(tag) - (2 if tag.endswith("/>") else 1)
    sep = "" if tag[end - 1].isspace() else " "
    return tag[:end] + f'{sep}rel="{" ".join(REQUIRED)}"' + tag[end:], True, True


def fix_text(s):
    stats = {"aff": 0, "missing": 0}

    def sub(m):
        new, aff, miss = fix_tag(m.group(0))
        stats["aff"] += aff
        stats["missing"] += miss
        return new
    return A_TAG.sub(sub, s), stats["aff"], stats["missing"]


def fix_json(path, write):
    raw = path.read_text(encoding="utf-8")
    if "<a" not in raw:
        return 0, 0
    data = json.loads(raw)
    tot = [0, 0]

    def walk(o):
        if isinstance(o, str):
            new, a, m = fix_text(o)
            tot[0] += a
            tot[1] += m
            return new
        if isinstance(o, list):
            return [walk(x) for x in o]
        if isinstance(o, dict):
            return {walk(k): walk(v) for k, v in o.items()}
        return o
    new = walk(data)
    if write and tot[1]:
        im = re.match(r"[{\[]\n( +)", raw)
        indent = len(im.group(1)) if im else None
        out = json.dumps(new, ensure_ascii=False, indent=indent)
        path.write_text(out + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
    return tot


def targets():
    out = subprocess.run(["git", "-c", "core.quotePath=false", "ls-files", "-z"], cwd=ROOT,
                         capture_output=True, text=True).stdout.split("\0")
    for f in out:
        if not f or f.startswith(SKIP_DIRS):
            continue
        if f.endswith(".html") or (f.startswith("i18n/") and f.endswith(".json") and "/" not in f[5:]):
            yield f
        elif f.endswith((".py", ".js")) and not f.startswith("api/"):
            yield f


def main():
    args = sys.argv[1:]
    check = "--check" in args
    md = "--md" in args
    files = [a for a in args if not a.startswith("--")] or list(targets())
    rows, total_aff, total_before = [], 0, 0
    for f in files:
        p = ROOT / f
        if not p.exists() or p.suffix not in (".html", ".json", ".py", ".js"):
            continue
        if f == "scripts/fix_affiliate_rel.py" or f.endswith("scripts/ship/preflight.py"):
            continue
        if p.suffix == ".json":
            aff, miss = fix_json(p, not check)
        else:
            src = p.read_text(encoding="utf-8", errors="surrogateescape")
            new, aff, miss = fix_text(src)
            if not check and miss:
                p.write_text(new, encoding="utf-8", errors="surrogateescape")
        if aff:
            rows.append((f, aff, miss))
            total_aff += aff
            total_before += miss
    after = 0 if not check else total_before
    if md:
        print("| File | Affiliate links | Missing before | Missing after |\n|---|---:|---:|---:|")
        for f, a, m in rows:
            print(f"| `{f}` | {a} | {m} | {m if check else 0} |")
        print(f"| **Total ({len(rows)} files)** | **{total_aff}** | **{total_before}** | **{after}** |")
    else:
        for f, a, m in rows:
            if m:
                print(f"{'✗' if check else 'fixed'} {f}: {m} of {a} affiliate link(s) "
                      f"{'missing' if check else 'were missing'} {'/'.join(REQUIRED)}")
        print(f"{total_aff} affiliate link(s) in {len(rows)} file(s); {total_before} "
              f"{'missing rel tokens' if check else 'fixed'}")
    return 1 if check and total_before else 0


if __name__ == "__main__":
    sys.exit(main())
