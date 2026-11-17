"""Shared helpers for every kit check: where the site is, its site.json, and
which HTML files are published.

A site repo holds the kit at <site>/kit/, so the site root is two levels above
this file's folder (kit/checks/site.py -> <site>/). SITE_ROOT overrides that,
which is how the kit's own tests point a check at any site checkout.
"""
import fnmatch
import json
import os

ROOT = os.environ.get("SITE_ROOT") or os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load_site():
    """The site's site.json (see the kit README for its fields)."""
    path = os.path.join(ROOT, "site.json")
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise SystemExit(f"site.json not found at {path}: every site needs one (see kit/README.md)")


SITE = load_site()


def vercel_ignored():
    """Patterns from .vercelignore: those files never reach the live site."""
    try:
        with open(os.path.join(ROOT, ".vercelignore"), encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return lambda f: False
    pats = [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#") and not ln.startswith("!")]

    def ignored(f):
        for p in pats:
            anchored = p.startswith("/")
            p2 = p.strip("/")
            if anchored and (fnmatch.fnmatch(f, p2) or f.startswith(p2 + "/")):
                return True
            if not anchored and (fnmatch.fnmatch(os.path.basename(f), p2) or fnmatch.fnmatch(f, p2)
                                 or f.startswith(p2 + "/") or ("/" + p2 + "/") in ("/" + f)):
                return True
        return False
    return ignored


def published_html():
    """Every .html file that .vercelignore does not exclude, repo-relative."""
    ignored = vercel_ignored()
    for dirpath, dirnames, filenames in os.walk(ROOT):
        rel_dir = os.path.relpath(dirpath, ROOT)
        dirnames[:] = sorted(d for d in dirnames if d not in (".git", "node_modules", "kit")
                             and not ignored(os.path.normpath(os.path.join(rel_dir, d))))
        for f in sorted(filenames):
            if f.endswith(".html"):
                rel = os.path.normpath(os.path.join(rel_dir, f))
                if not ignored(rel):
                    yield rel
