"""Publish the shared runtime into a site and move pages onto it.

Used by update.py (publish) and by `python3 kit/runtime/runtime.py migrate`.
A site opts in with site.json: {"runtime": {"shared": true}}.

publish(site)  copies kit/runtime/site-runtime.js to <site>/js/site-runtime.js and points
               every page's <script src="/js/site-runtime.js?v=..."> at the current version
               (the ?v= is a content hash, so year-long JS caches never serve an old copy).
migrate(site)  replaces a page's inline runtime (<script>…UNIFIED PAGE RUNTIME…</script>
               + <script id="bpa-slider-perf-runtime">) with one <script src> tag, ONLY when
               the inline code is byte-identical to the kit's, or is a variant listed in
               compat.json (diffed by hand, judged safe). Anything else is reported and
               left alone, so behaviour cannot change silently.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "site-runtime.js")
PUBLISHED = "js/site-runtime.js"
TAG_RE = re.compile(r'/js/site-runtime\.js\?v=[0-9a-f]+')
RUNTIME_MARK = "UNIFIED PAGE RUNTIME"
PERF_ID = 'id="bpa-slider-perf-runtime"'


def version():
    return hashlib.sha256(open(SRC, "rb").read()).hexdigest()[:10]


def tag():
    return f'<script src="/js/site-runtime.js?v={version()}"></script>'


def parts():
    """The two inline blocks the shared file replaces, exactly as pages carried them."""
    s = open(SRC, encoding="utf-8").read()
    a = s.index("/* ---- 1. page runtime ---- */\n") + len("/* ---- 1. page runtime ---- */\n")
    b = s.index("\n\n/* ---- 2. slider lazy-load fallbacks ---- */\n")
    c = b + len("\n\n/* ---- 2. slider lazy-load fallbacks ---- */\n")
    return s[a:b], s[c:].rstrip("\n")


def _html_files(site, published_only=True):
    sys.path.insert(0, os.path.join(site, "kit", "checks"))
    os.environ["SITE_ROOT"] = site
    from sitecfg import published_html  # noqa: E402
    return list(published_html())


def publish(site):
    os.makedirs(os.path.join(site, "js"), exist_ok=True)
    with open(SRC, "rb") as a, open(os.path.join(site, PUBLISHED), "wb") as b:
        b.write(a.read())
    v, n = version(), 0
    for rel in _html_files(site):
        p = os.path.join(site, rel)
        s = open(p, encoding="utf-8").read()
        s2 = TAG_RE.sub(f"/js/site-runtime.js?v={v}", s)
        if s2 != s:
            open(p, "w", encoding="utf-8").write(s2)
            n += 1
    print(f"{site}: runtime {v} published, {n} page(s) re-pointed")


def accepted(body, rt):
    """Byte-identical to the kit runtime, or a variant listed in compat.json (diffed by hand)."""
    body = body.strip("\n")
    if body == rt.strip("\n"):
        return True
    import json
    h = hashlib.md5(body.encode()).hexdigest()
    known = json.load(open(os.path.join(HERE, "compat.json"), encoding="utf-8"))["accepted"]
    return any(h.startswith(k) for k in known)


def _script_blocks(s):
    for m in re.finditer(r"<script\b([^>]*)>(.*?)</script>", s, re.S):
        yield m


def migrate(site):
    rt, perf = parts()
    moved, skipped = 0, []
    for rel in _html_files(site):
        p = os.path.join(site, rel)
        s = open(p, encoding="utf-8").read()
        if RUNTIME_MARK not in s:
            continue
        rt_m = next((m for m in _script_blocks(s) if RUNTIME_MARK in m.group(2)[:400] and "src=" not in m.group(1)), None)
        pf_m = next((m for m in _script_blocks(s) if PERF_ID in m.group(1)), None)
        if not rt_m or not accepted(rt_m.group(2), rt) or (pf_m and pf_m.group(2).strip("\n") != perf.strip("\n")):
            skipped.append(rel)
            continue
        out = s
        if pf_m:
            out = out[:pf_m.start()] + out[pf_m.end():]
        out = out[:rt_m.start()] + tag() + out[rt_m.end():]
        open(p, "w", encoding="utf-8").write(out)
        moved += 1
    print(f"{site}: {moved} page(s) moved to the shared runtime")
    for rel in skipped:
        print(f"  left alone (inline code differs from the kit runtime): {rel}")
    return skipped


# ---------------------------------------------------------------- adapt
# For pages whose inline runtime is an older or localised variant: move every reviewed
# difference into page options, then load the shared file. A page is touched only when
# EVERY diff hunk against the reference runtime is in compat.json reviewed_hunks.

CFG_RE = re.compile(r"window\.LTT_PAGE_CONFIG\s*=\s*(\{.*?\});", re.S)
JS_TOKEN = re.compile(r"'(?:[^'\\]|\\.)*'|\(i \+ 1\)|[A-Za-z_][A-Za-z0-9_.]*")
TEMPLATE_VARS = {"visibleCount": "{visible}", "cards.length": "{total}", "filterLabel": "{filter}", "(i + 1)": "{n}"}


def _hunks(ref, body):
    import difflib
    out, cur = [], []
    for ln in difflib.unified_diff(ref.strip("\n").splitlines(), body.strip("\n").splitlines(), n=0, lineterm=""):
        if ln.startswith("@@"):
            if cur:
                out.append("\n".join(cur))
            cur = []
        elif not ln.startswith(("---", "+++")):
            cur.append(ln)
    if cur:
        out.append("\n".join(cur))
    return out


def _concat_to_template(expr):
    out = ""
    for tok in JS_TOKEN.findall(expr):
        if tok.startswith("'"):
            out += tok[1:-1].replace("\\'", "'")
        elif tok in TEMPLATE_VARS:
            out += TEMPLATE_VARS[tok]
        else:
            return None
    return out


def page_options(body):
    """Options the shared runtime needs to behave like this inline variant."""
    import json
    opts = {}
    m = re.search(r'cfg\.tocGuideLabel \|\| ("(?:[^"\\]|\\.)*")', body)
    if m and json.loads(m.group(1)) != "Buyer's Guide & Methodology":
        opts["tocGuideLabel"] = json.loads(m.group(1))
    m = re.search(r"cfg\.tocBreakdownLabel \|\| '((?:[^'\\]|\\.)*)'", body)
    if m and m.group(1) != "Detailed Breakdown":
        opts["tocBreakdownLabel"] = m.group(1).replace("\\'", "'")
    m = re.search(r"subEl\.textContent = (visibleCount \+ [^;]*);", body)
    if m:
        opts["filterSummary"] = _concat_to_template(m.group(1))
    m = re.search(r"badge: ([^,\n]*),\n", body)
    if m and m.group(1).strip() != "'#' + (i + 1) + ' PICK'":
        opts["pickBadge"] = _concat_to_template(m.group(1))
    if "sec.querySelectorAll('h2[id]')" in body:
        opts["tocSubHeadings"] = True
    return {k: v for k, v in opts.items() if v is not None}


def adapt(site):
    import json
    known = json.load(open(os.path.join(HERE, "compat.json"), encoding="utf-8"))["reviewed_hunks"]
    ref = open(os.path.join(HERE, "..", known["reference"]), encoding="utf-8").read()
    ok_hunks = set(known["md5"])
    _, perf = parts()
    moved, skipped = 0, []
    for rel in _html_files(site):
        p = os.path.join(site, rel)
        s = open(p, encoding="utf-8").read()
        if RUNTIME_MARK not in s:
            continue
        rt_m = next((m for m in _script_blocks(s) if RUNTIME_MARK in m.group(2)[:400] and "src=" not in m.group(1)), None)
        pf_m = next((m for m in _script_blocks(s) if PERF_ID in m.group(1)), None)
        if not rt_m or (pf_m and pf_m.group(2).strip("\n") != perf.strip("\n")):
            skipped.append((rel, "perf runtime differs"))
            continue
        body = rt_m.group(2)
        bad = [h for h in _hunks(ref, body) if hashlib.md5(h.encode()).hexdigest() not in ok_hunks]
        if bad:
            skipped.append((rel, f"{len(bad)} unreviewed difference(s)"))
            continue
        opts = page_options(body)
        out = s
        if pf_m:
            out = out[:pf_m.start()] + out[pf_m.end():]
        out = out[:rt_m.start()] + tag() + out[rt_m.end():]
        if opts:
            cm = CFG_RE.search(out)
            if cm:
                cfg = json.loads(cm.group(1))
                cfg.update({k: v for k, v in opts.items() if k not in cfg})
                out = out[:cm.start(1)] + json.dumps(cfg, ensure_ascii=False) + out[cm.end(1):]
            else:
                i = out.index(tag())
                out = out[:i] + "<script>\nwindow.LTT_PAGE_CONFIG = " + json.dumps(opts, ensure_ascii=False) + ";\n</script>\n" + out[i:]
        open(p, "w", encoding="utf-8").write(out)
        moved += 1
    print(f"{site}: {moved} page(s) adapted to the shared runtime")
    for rel, why in skipped:
        print(f"  left alone ({why}): {rel}")
    return skipped


if __name__ == "__main__":
    cmds = {"migrate": migrate, "publish": publish, "adapt": adapt}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit("usage: python3 kit/runtime/runtime.py migrate|adapt|publish [site]")
    site = os.path.abspath(sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", ".."))
    cmds[sys.argv[1]](site)
