#!/usr/bin/env python3
"""Every affiliate / OTA link carries rel="nofollow sponsored noopener".

    python3 scripts/fix_affiliate_rel.py                 # fix in place (idempotent)
    python3 scripts/fix_affiliate_rel.py --check         # write nothing, exit 1 if anything is missing
    python3 scripts/fix_affiliate_rel.py --check FILE..  # only these files
    python3 scripts/fix_affiliate_rel.py --report        # per-file counts (TSV), write nothing
    python3 scripts/fix_affiliate_rel.py --md            # per-file counts as a Markdown table

What it walks: every published .html / .js file (anything .vercelignore does not exclude),
every Python generator, and the translation tables listed in site.json, so regenerated
pages keep the rel. Never kit/, tests, archives or node_modules.

For each <a> tag whose href points at an affiliate or OTA host (AFFILIATE_HOSTS, any
tripadvisor.*, or any external host carrying a partner/ref/aid/... query parameter) the
tokens nofollow, sponsored and noopener are merged into the existing rel. Other rel tokens
are kept, nothing is duplicated, and the href, its tracking parameters, target and the link
text are never touched. A tag that already has all three tokens is left byte-for-byte as is.

Official ticket sites that pay no commission (site.json affiliate.plain_booking_hosts, e.g.
the Budapest bath ticket shops) get rel="nofollow noopener" only; a stray "sponsored" goes.

Generator templates whose href is a placeholder ({url}, %s, ' + x + ', ${x}) are covered
when the tag is clearly an affiliate slot: it already says "sponsored", or it is a rating
badge (bpa-rev-badge).

site.json (all optional):
    "affiliate": {
      "extra_hosts": ["partner.example"],         # always affiliate, on top of the kit list
      "plain_booking_hosts": ["tickets.x.hu"],    # rel="nofollow noopener", no "sponsored"
      "conditional_hosts": {"fareharbor.com": {"ref": "cruisedetective-asn"}},
                                                   # affiliate only with this param value
                                                   # (or another partner parameter)
      "never_hosts": ["example.org"],             # never affiliate
      "json": ["i18n/*.json"],                    # translation tables to fix too (globs)
      "skip": ["data/harvested_html/"]            # extra path prefixes to leave alone
    }
"""
import argparse
import fnmatch
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "checks"))
from sitecfg import ROOT, SITE, vercel_ignored  # noqa: E402

CFG = SITE.get("affiliate", {})
AFFILIATE_REL = ("nofollow", "sponsored", "noopener")
REQUIRED = AFFILIATE_REL
PLAIN_REL = ("nofollow", "noopener")

# Host suffixes: the host itself or any subdomain of it.
AFFILIATE_HOSTS = (
    # OTAs / marketplaces
    "getyourguide.com", "gyg.me", "viator.com", "tiqets.com", "fareharbor.com", "tourradar.com",
    "booking.com", "hostelworld.com", "klook.com", "civitatis.com", "musement.com", "headout.com",
    "expedia.com", "agoda.com", "hotels.com", "airbnb.com", "trip.com",
    # Affiliate networks and redirect / short-link domains
    "tp.st", "tp.media", "tpm.lv", "tpk.lv", "travelpayouts.com", "awin1.com", "prf.hn", "go2cloud.org",
    # Direct operator partners
    "legenda.hu", "budapestrivercruise.eu", "budapestrivercruise.com", "silver-line.hu",
    "budapestxplore.com", "guruwalk.com", "flynyon.com",
) + tuple(CFG.get("extra_hosts", []))
TRIPADVISOR = re.compile(r"(^|\.)tripadvisor\.[a-z.]+$")
PLAIN_BOOKING_HOSTS = tuple(CFG.get("plain_booking_hosts", []))
CONDITIONAL_HOSTS = CFG.get("conditional_hosts", {})

# Our own sites and plain reference hosts: never affiliate, even with a ?ref=-style param.
NEVER = (
    "budapestadventures.com", "thecruisedetective.com", "luxurytraveltester.com",
    "adventuresinnewyork.com", "cruisedetective.store",
    "google.com", "goo.gl", "youtube.com", "youtu.be", "instagram.com", "tiktok.com",
    "facebook.com", "apple.com", "wa.me", "googleapis.com", "gstatic.com", "cloudflare.com",
    "jsdelivr.net",
) + tuple(CFG.get("never_hosts", []))
PARTNER_PARAMS = {"partner", "partner_id", "partnerid", "aid", "affi", "affid", "aff_id", "affiliate",
                  "affiliate_id", "ref", "pid", "marker", "code", "mcid", "awinaffid", "subid",
                  "sub_id", "clickref", "awc", "irclickid", "asn"}

TAG = re.compile(r"<a\b(?:[^>\"']|\"[^\"]*\"|'[^']*')*>", re.I)
HREF = re.compile(r"""\bhref\s*=\s*(\\?["'])(.*?)\1""", re.I | re.S)
REL = re.compile(r"""\brel\s*=\s*(\\?["'])(.*?)\1""", re.I | re.S)
CLASS = re.compile(r"""\bclass\s*=\s*(\\?["'])(.*?)\1""", re.I | re.S)
TARGET = re.compile(r"""\s+target\s*=""", re.I)
TEMPLATED = re.compile(r"\{|%s|%\(|'\s*\+|\"\s*\+|\$\{")
# A generator that adds the rel through a variable (<a href="{url}" {REL}>) handles it itself.
QUOTED = re.compile(r"\\?\"[^\"]*\"|\\?'[^']*'")
BARE_PLACEHOLDER = re.compile(r"\s(\{[^{}\s]+\}|%s|\$\{[^}]+\})")

SKIP = (".claude/", ".github/", "node_modules/", "kit/", "scripts/archive/", "archive/", "test/",
        "tests/", "assets/") + tuple(CFG.get("skip", []))


def host_match(host, suffixes):
    return any(host == s or host.endswith("." + s) for s in suffixes)


def classify(href, tag=""):
    """'aff', 'plain' or None for an <a> tag's href."""
    raw = html.unescape(href.replace("\\/", "/")).strip()
    if TEMPLATED.search(raw) and not re.match(r"(https?:)?//[\w.-]+\.[a-z]{2,}[/?]", raw):
        rel = REL.search(tag)
        cls = CLASS.search(tag)
        if rel and "sponsored" in rel.group(2).split():
            return "aff"
        if cls and "bpa-rev-badge" in cls.group(2).split():
            return "aff"
        return None
    if raw.startswith("//"):
        raw = "https:" + raw
    if not re.match(r"https?://", raw, re.I):
        return None
    try:
        u = urllib.parse.urlsplit(raw)
    except ValueError:
        return None
    host = (u.hostname or "").lower()
    if not host or host_match(host, NEVER):
        return None
    if host_match(host, PLAIN_BOOKING_HOSTS):
        return "plain"
    q = {k.lower(): v for k, v in urllib.parse.parse_qsl(u.query, keep_blank_values=True)}
    for h, need in CONDITIONAL_HOSTS.items():
        if host_match(host, (h,)):
            ok = all(q.get(k) == v for k, v in need.items()) or bool(set(q) & PARTNER_PARAMS)
            return "aff" if ok else None
    if host_match(host, AFFILIATE_HOSTS) or TRIPADVISOR.search(host):
        return "aff"
    return "aff" if set(q) & PARTNER_PARAMS else None


def is_affiliate(href):
    return bool(href) and classify(href) == "aff"


def merged_rel(existing, required):
    seen, out = set(), []
    for t in list(required) + existing.split():
        k = t.lower()
        if k not in seen:
            seen.add(k)
            out.append(t if k not in required else k)
    return " ".join(out)


def fix_tag(tag):
    """(new_tag, kind, was_missing)."""
    hm = HREF.search(tag)
    if not hm:
        return tag, None, False
    kind = classify(hm.group(2), tag)
    if not kind:
        return tag, None, False
    required = AFFILIATE_REL if kind == "aff" else PLAIN_REL
    forbidden = () if kind == "aff" else ("sponsored",)
    rm = REL.search(tag)
    if not rm and BARE_PLACEHOLDER.search(QUOTED.sub("", tag)):
        return tag, kind, False
    if rm:
        have = {t.lower() for t in rm.group(2).split()}
        if all(r in have for r in required) and not have & set(forbidden):
            return tag, kind, False
        q = rm.group(1)
        kept = " ".join(t for t in rm.group(2).split() if t.lower() not in forbidden)
        return tag[:rm.start()] + f"rel={q}{merged_rel(kept, required)}{q}" + tag[rm.end():], kind, True
    q = hm.group(1)
    attr = f"rel={q}{' '.join(required)}{q}"
    tm = TARGET.search(tag)
    if tm:
        return tag[:tm.start()] + " " + attr + tag[tm.start():], kind, True
    end = len(tag) - (2 if tag.endswith("/>") else 1)
    sep = "" if tag[end - 1].isspace() else " "
    return tag[:end] + sep + attr + tag[end:], kind, True


def process(text, code=False):
    """code=True for .py/.js/.json sources: only single-line tags, so a match never spans
    program code between two string literals."""
    stats = {"aff": 0, "plain": 0, "missing": 0}

    def sub(m):
        if code and "\n" in m.group(0):
            return m.group(0)
        new, kind, missing = fix_tag(m.group(0))
        if kind:
            stats[kind] += 1
            stats["missing"] += missing
        return new

    return TAG.sub(sub, text), stats


def files():
    out = subprocess.run(
        ["git", "-c", "core.quotepath=off", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT, capture_output=True, text=True, check=True).stdout.split("\0")
    ignored = vercel_ignored()
    globs = CFG.get("json", [])
    for f in sorted(set(out)):
        if not f or f.startswith(SKIP) or not os.path.isfile(os.path.join(ROOT, f)):
            continue
        if f.endswith(".py"):
            yield f
        elif f.endswith(".json") and any(fnmatch.fnmatch(f, g) for g in globs):
            yield f
        elif f.endswith((".html", ".htm", ".js")) and not f.endswith(".min.js") and not ignored(f):
            yield f


def run(write, only=None):
    """Scan (and with write=True fix). Returns [(relpath, links, missing)] for files with links."""
    rows = []
    for f in (only or files()):
        path = os.path.join(ROOT, f)
        try:
            with open(path, encoding="utf-8") as fh:
                s = fh.read()
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if "<a" not in s and "<A" not in s:
            continue
        new, st = process(s, code=not f.endswith((".html", ".htm")))
        if st["aff"] or st["plain"]:
            rows.append((f, st["aff"] + st["plain"], st["missing"]))
        if write and st["missing"]:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(new)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="write nothing, exit 1 if any link lacks its rel")
    ap.add_argument("--report", action="store_true", help="write nothing, print per-file counts as TSV")
    ap.add_argument("--md", action="store_true", help="print per-file counts as a Markdown table")
    ap.add_argument("files", nargs="*", help="only these files (default: everything above)")
    args = ap.parse_args()
    dry = args.check or args.report
    rows = run(write=not dry, only=args.files or None)
    links = sum(r[1] for r in rows)
    missing = sum(r[2] for r in rows)
    bad = [r for r in rows if r[2]]
    summary = f"{links} affiliate/booking link(s) in {len(rows)} file(s), {missing} missing rel in {len(bad)} file(s)"
    if args.md:
        print("| File | Links | Missing |\n|---|---:|---:|")
        for f, n, m in rows:
            print(f"| `{f}` | {n} | {m} |")
        print(f"| **Total ({len(rows)} files)** | **{links}** | **{missing}** |")
    elif args.report:
        print("file\tlinks\tmissing_rel")
        for f, n, m in rows:
            print(f"{f}\t{n}\t{m}")
    if args.check:
        for f, _, m in bad:
            print(f"  {f}: {m} link(s) without the required rel")
        print(f"{'FAIL' if bad else 'OK'}: {summary}" + (". Fix with: python3 scripts/fix_affiliate_rel.py" if bad else ""))
        return 1 if bad else 0
    if not dry:
        print(f"Fixed: {summary}; {len(bad)} file(s) written")
    else:
        print(f"# {summary}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
