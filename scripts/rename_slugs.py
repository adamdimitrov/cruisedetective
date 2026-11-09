#!/usr/bin/env python3
"""
Rename mistranslated / malformed localized slugs and repair broken internal links.

For every OLD -> NEW path in SLUG_RENAMES:
  * moves the page directory (git mv),
  * rewrites every reference to the old path in site files (HTML, sitemap,
    llms*.txt, *.md) - absolute and relative, with a path-boundary check so
    e.g. "/pl/o" never matches "/pl/odkryj",
  * adds a permanent redirect OLD -> NEW to vercel.json.

LINK_FIXES rewrites hrefs that pointed at nonexistent pages (404s) and also
adds a redirect for them, in case they were crawled.

Idempotent: re-running after a successful run changes nothing.
"""

import json
import os
import re
import subprocess
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SLUG_RENAMES = {
    # Dutch: "uns" is German; "roondvarten" is a typo
    "/nl/over-uns": "/nl/over-ons",
    "/nl/beste-roondvarten-grachten-amsterdam": "/nl/beste-rondvaarten-grachten-amsterdam",
    # Romanian: "senine" is not a word; the Seine is "Sena"
    "/ro/cele-mai-bune-croaziere-râul-senine-paris": "/ro/cele-mai-bune-croaziere-sena-paris",
    # Polish: "/pl/o" is just the preposition "about"
    "/pl/o": "/pl/o-nas",
    # Japanese: 接触 = physical contact; お問い合わせ = contact/inquiries
    "/ja/接触": "/ja/お問い合わせ",
    # Japanese: the long-vowel mark ー was mangled into a hyphen
    "/ja/パリのベスト-セ-ヌ川クル-ズ": "/ja/パリのベスト-セーヌ川クルーズ",
    "/ja/パリのベスト-ディナ-クル-ズ": "/ja/パリのベスト-ディナークルーズ",
    "/ja/ベスト運河クル-ズ-アムステルダム": "/ja/ベスト運河クルーズ-アムステルダム",
    "/ja/ロンドンのテムズ川クル-ズ": "/ja/ロンドンのテムズ川クルーズ",
}

# Links to pages that never existed -> the right existing page (paths are post-rename)
LINK_FIXES = {
    "/fr/seine-river-cruise-review": "/fr/meilleures-croisieres-seine-paris",
    "/ro/dinner-cruises": "/ro/cele-mai-bune-cina-croaziere-paris",
    "/ja/dinner-cruises": "/ja/パリのベスト-ディナークルーズ",
    "/nl/london": "/nl/beste-boottochten-theems-londen",
}

SKIP_DIRS = {".git", "node_modules", "scripts", "reports", "articles", "test", ".agents", "credentials"}
EXTS = (".html", ".xml", ".txt", ".md")
BOUNDARY = r'(?=["\'#?/<\s)]|$)'


def site_files():
    for dirpath, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
        for f in files:
            if not f.endswith(EXTS):
                continue
            # at the repo root only public site files, not internal docs (GEMINI.md, PROJECT.md...)
            if dirpath == ROOT and not (f in ("sitemap.xml", "llms.txt", "llms-full.txt", "index.html")
                                        or (f.endswith(".md") and f[0].islower())):
                continue
            yield os.path.join(dirpath, f)


LEGACY_MAP = re.compile(r'(LINGUANA_PAGE_PATH_MAP = \{)([^}]*)(\})')


def fix_legacy_map(text):
    """Legacy (unused) Linguana slug map embedded in some pages: keep its values in sync."""
    bare = {o.split("/", 2)[2]: n.split("/", 2)[2] for o, n in SLUG_RENAMES.items()}

    def repl(m):
        body = m.group(2)
        for o, n in bare.items():
            body = body.replace(f': "{o}"', f': "{n}"')
        return m.group(1) + body + m.group(3)
    return LEGACY_MAP.sub(repl, text)


def replace_paths(text, mapping):
    text = fix_legacy_map(text)
    for old, new in mapping.items():
        pat = re.compile(r'(?<=["\'(\s])((?:https://www\.thecruisedetective\.com)?)' + re.escape(old) + BOUNDARY)
        text = pat.sub(lambda m: m.group(1) + new, text)
        pat2 = re.compile(r'(https://www\.thecruisedetective\.com)' + re.escape(old) + BOUNDARY)  # e.g. <loc>
        text = pat2.sub(lambda m: m.group(1) + new, text)
    return text


def main():
    # 1. move directories
    for old, new in SLUG_RENAMES.items():
        src, dst = ROOT + old, ROOT + new
        if os.path.isdir(src) and not os.path.exists(dst):
            subprocess.run(["git", "mv", src, dst], cwd=ROOT, check=True)
            print("moved", old, "->", new)

    # 2. rewrite references
    mapping = {**SLUG_RENAMES, **LINK_FIXES}
    changed = 0
    for p in site_files():
        with open(p, encoding="utf-8") as f:
            s = f.read()
        n = replace_paths(s, mapping)
        if n != s:
            with open(p, "w", encoding="utf-8") as f:
                f.write(n)
            changed += 1
    print(changed, "files rewritten")

    # 3. redirects
    vp = os.path.join(ROOT, "vercel.json")
    with open(vp, encoding="utf-8") as f:
        v = json.load(f)
    # Vercel matches redirect sources against the percent-encoded path, so
    # non-ASCII slugs must be written encoded or they never match.
    enc = lambda p: quote(p, safe="/:")
    existing = {r["source"] for r in v["redirects"]}
    new_rules = [{"source": enc(o), "destination": enc(n), "permanent": True}
                 for o, n in mapping.items() if enc(o) not in existing]
    # old paths may also be targets of older redirects -> point those straight at the new slug
    for r in v["redirects"]:
        if r["destination"] in SLUG_RENAMES:
            r["destination"] = SLUG_RENAMES[r["destination"]]
    v["redirects"] = new_rules + v["redirects"]
    with open(vp, "w", encoding="utf-8") as f:
        f.write(json.dumps(v, indent=2, ensure_ascii=False) + "\n")
    print(len(new_rules), "redirects added")


if __name__ == "__main__":
    main()
