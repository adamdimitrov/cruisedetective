"""Shared listicle card design (the river/dinner cruise template) as versioned files.

The card design used to be pasted into every page as inline <style>/<script> blocks. The kit
keeps them in runtime/listicle/ (see manifest.json: which inline blocks each file replaces, in
page order). A site opts pages in with site.json:

    "listicle": {"pages": ["best-budapest-river-cruises.html", "best-dinner-cruises-budapest.html"]}

publish(site)  copies the files to <site>/css/ and <site>/js/ and points every page's tag at the
               current ?v= (content hash), so long browser caches never serve an old copy.
migrate(site)  on each listed page, replaces each group of inline blocks with one tag at the same
               place, ONLY when the inline code is byte-identical to the kit file. Anything else is
               reported and left alone.
problems(site) used by check_kit.py: published copies current, pages on the current ?v=, and no
               listed page carrying an inline copy next to (or instead of) the shared file.

    python3 kit/runtime/listicle.py migrate|publish [site]
"""
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "listicle")
MANIFEST = json.load(open(os.path.join(SRC, "manifest.json"), encoding="utf-8"))["groups"]


def dest(g):
    return ("css/" if g["kind"] == "style" else "js/") + g["file"]


def version(g):
    return hashlib.sha256(open(os.path.join(SRC, g["file"]), "rb").read()).hexdigest()[:10]


def tag(g):
    url = f"/{dest(g)}?v={version(g)}"
    return f'<link rel="stylesheet" href="{url}">' if g["kind"] == "style" else f'<script src="{url}"></script>'


def tag_re(g):
    return re.compile(r"/" + re.escape(dest(g)) + r"\?v=[0-9a-f]+")


def pages(site):
    cfg = json.load(open(os.path.join(site, "site.json"), encoding="utf-8")).get("listicle", {})
    return cfg.get("pages", [])


def block_re(kind, block_id):
    return re.compile(r'<%s id="%s">(.*?)</%s>' % (kind, re.escape(block_id), kind), re.S)


def inline_text(g, s):
    """The group's inline blocks as one file's text, or None unless all are present, adjacent
    (only whitespace between them) and in manifest order. Returns (text, start, end)."""
    pos, parts, start = 0, [], None
    for i in g["ids"]:
        m = block_re(g["kind"], i).search(s, pos)
        if not m or (start is not None and s[pos:m.start()].strip()):
            return None
        start = m.start() if start is None else start
        parts.append((i, m.group(1)))
        pos = m.end()
    if g["kind"] == "style":
        text = "".join("/* ---- %s ---- */\n%s\n" % (i, b) for i, b in parts)
    else:
        text = parts[0][1]
    return text, start, pos


def publish(site):
    n = 0
    for g in MANIFEST:
        out = os.path.join(site, dest(g))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(os.path.join(SRC, g["file"]), "rb") as a, open(out, "wb") as b:
            b.write(a.read())
    for rel in pages(site):
        p = os.path.join(site, rel)
        if not os.path.exists(p):
            continue
        s = open(p, encoding="utf-8").read()
        s2 = s
        for g in MANIFEST:
            s2 = tag_re(g).sub(f"/{dest(g)}?v={version(g)}", s2)
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
            n += 1
    print(f"{site}: listicle files published, {n} page(s) re-pointed")


def migrate(site):
    publish(site)
    for rel in pages(site):
        p = os.path.join(site, rel)
        s = open(p, encoding="utf-8").read()
        moved, left = [], []
        for g in MANIFEST:
            if tag_re(g).search(s):
                continue
            hit = inline_text(g, s)
            want = open(os.path.join(SRC, g["file"]), encoding="utf-8").read()
            if not hit:
                left.append(f"{g['file']} (blocks missing or not together)")
                continue
            text, a, b = hit
            if text != want:
                left.append(f"{g['file']} (inline code differs from the kit)")
                continue
            s = s[:a] + tag(g) + s[b:]
            moved.append(g["file"])
        open(p, "w", encoding="utf-8").write(s)
        print(f"{rel}: {len(moved)} group(s) moved to shared files" + (f"; left inline: {', '.join(left)}" if left else ""))


def problems(site):
    out = []
    for g in MANIFEST:
        pub = os.path.join(site, dest(g))
        try:
            same = open(pub, "rb").read() == open(os.path.join(SRC, g["file"]), "rb").read()
        except FileNotFoundError:
            same = False
        if pages(site) and not same:
            out.append(f"{dest(g)} differs from the kit copy (run kit/update.py)")
    for rel in pages(site):
        p = os.path.join(site, rel)
        if not os.path.exists(p):
            out.append(f"site.json listicle.pages lists {rel}, which does not exist")
            continue
        s = open(p, encoding="utf-8").read()
        for g in MANIFEST:
            m = tag_re(g).search(s)
            if m and not m.group(0).endswith(version(g)):
                out.append(f"{rel}: loads an old /{dest(g)} (run kit/update.py)")
            for i in g["ids"]:
                if block_re(g["kind"], i).search(s):
                    out.append(f"{rel}: inline <{g['kind']} id=\"{i}\"> is a copy of the shared /{dest(g)}; "
                               "remove it (python3 kit/runtime/listicle.py migrate)")
            if not m:
                out.append(f"{rel}: does not load /{dest(g)}")
    return out


if __name__ == "__main__":
    cmds = {"migrate": migrate, "publish": publish}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit("usage: python3 kit/runtime/listicle.py migrate|publish [site]")
    cmds[sys.argv[1]](os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "..")))
