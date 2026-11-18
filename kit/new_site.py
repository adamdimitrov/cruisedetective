#!/usr/bin/env python3
"""Start a new site from the kit: same shared code, rules, checks and look from day one.

    python3 new_site.py --dir ../my-new-site --name "Rome Adventures" \\
        --domain https://www.romeadventures.com --tagline "Tested tours and tickets in Rome" \\
        --email hello@romeadventures.com

Run it from a site-kit checkout, into an empty folder (usually the freshly cloned, empty
GitHub repo the owner created). It writes:

  site.json, CLAUDE.md, .vercelignore, vercel.json, robots.txt, sitemap.xml
  data/menu/en.json          the menu (edit it, then: python3 scripts/menu.py build)
  scripts/layout_config.json  menu/footer sync settings (master page = index.html)
  index.html, about/, contact/, privacy/, 404.html   starter pages with [Owner: ...] gaps
  css/site.css, js/site-chrome.js   the shared look (menu, language switcher, footer, article)
then installs the kit (kit/, kit.lock, CI workflow, shared runtime and script stubs), runs the
layout sync (menu, footer, search index) and kit/checks/check_all.py, which must pass.

It never commits, pushes or deploys. Review, commit, push, connect the repo in Vercel, and
open the first PR as usual. English only for now: add languages later by adding masters to
scripts/layout_config.json and their menus to data/menu/<lang>.json.
"""
import argparse
import datetime
import hashlib
import html
import json
import os
import subprocess
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = os.path.join(HERE, "templates", "site")


def read(*p):
    return open(os.path.join(TPL, *p), encoding="utf-8").read()


def write(root, rel, text):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p) or root, exist_ok=True)
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)


def fill(text, values):
    for k, v in values.items():
        text = text.replace("{{%s}}" % k, v)
    return text


def default_menu(a):
    """A starter menu in the shared menu format: brand, one guides dropdown, About, Contact."""
    return {
        "lang": "en",
        "brand": {"name": a.name.upper(), "href": "/", "logo": a.logo or "", "aria": f"{a.name.upper()} Homepage"},
        "nav": [
            {"type": "link", "label": "About", "href": "/about"},
            {"type": "link", "label": "Contact", "href": "/contact"},
        ],
        "languages": [],
        "search": True,
    }


def render_header(menu):
    sys.path.insert(0, os.path.join(HERE, "scripts"))
    sys.path.insert(0, os.path.join(HERE, "checks"))
    import menu as menu_mod  # noqa: E402
    return menu_mod.render_header(menu)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True, help="empty folder for the new site (e.g. the cloned empty repo)")
    ap.add_argument("--name", required=True, help='site name, e.g. "Rome Adventures"')
    ap.add_argument("--domain", required=True, help="https://www.example.com")
    ap.add_argument("--tagline", default="", help="one sentence: what the site helps people choose")
    ap.add_argument("--email", default="", help="contact address shown on the contact page")
    ap.add_argument("--logo", default="", help="logo path on the site, e.g. /assets/logo-96.webp (optional)")
    a = ap.parse_args()

    root = os.path.abspath(a.dir)
    if os.path.exists(root) and [f for f in os.listdir(root) if f not in (".git", "README.md", ".gitignore", "LICENSE")]:
        sys.exit(f"{root} is not empty; new_site.py only writes into an empty folder")
    os.makedirs(root, exist_ok=True)
    if not os.path.isdir(os.path.join(root, ".git")):
        # the shared scripts list files through git; a plain folder gets a local repo (no commits)
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    domain = a.domain.rstrip("/")
    host = urllib.parse.urlsplit(domain).hostname or domain
    bare = host[4:] if host.startswith("www.") else host
    name_e = html.escape(a.name)
    tagline = a.tagline or f"Tested guides from {a.name}."

    # ---------------------------------------------------------------- settings
    site = {
        "name": a.name,
        "domain": domain,
        "languages": ["en"],
        "images": {"allowed_hosts": []},
        "local_checks": ["scripts/sync_layout.py --check", "scripts/fix_affiliate_rel.py --check"],
        "runtime": {"shared": True},
    }
    write(root, "site.json", json.dumps(site, indent=2, ensure_ascii=False) + "\n")
    layout = {
        "site": domain,
        "default_lang": "en",
        "masters": {"en": "index.html"},
        "footer_starts": ['<footer class="footer-dark ltt-footer"[^>]*>'],
        "footer_marker": 'class="footer-dark',
        "footer_link_class": "footer-link-item",
        "sync_blocks": [],
        "unlisted_ok": ["404.html"],
        "skip_dirs": ["node_modules", "drafts", "data"],
    }
    write(root, "scripts/layout_config.json", json.dumps(layout, indent=2) + "\n")
    menu = default_menu(a)
    write(root, "data/menu/en.json", json.dumps(menu, indent=2, ensure_ascii=False) + "\n")

    write(root, "CLAUDE.md", f"""# {a.name}

1. Read `kit/RULES.md` first: the shared rules for every site (nothing goes live
   without the owner's OK, QC, copy, affiliate links, photos, layout).
2. Then this site's own notes in `SITE.md` (add site-specific rules there; they win
   only where they are stricter).
3. Before every PR: `python3 kit/checks/check_all.py` must exit 0 (CI runs the same).
4. Never edit `kit/` here: change github.com/adamdimitrov/site-kit and run
   `python3 kit/update.py`. Site settings live in `site.json`; the menu in `data/menu/`.
""")
    write(root, "SITE.md", f"# {a.name}: site notes\n\n[Owner: partners, tone, anything sessions must know about this site.]\n")
    write(root, ".vercelignore", "\n".join([
        "# never served", ".git", ".claude", ".github", ".env", "kit/", "kit.lock", "site.json", "CLAUDE.md",
        "SITE.md", "scripts/", "data/", "drafts/", "tests/", "/*.py", "*.log", ""]))
    write(root, "vercel.json", json.dumps({"cleanUrls": True, "trailingSlash": False}, indent=2) + "\n")
    write(root, "robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {domain}/sitemap.xml\n")
    write(root, ".gitignore", "__pycache__/\n*.pyc\n.DS_Store\n.env\n")

    # ---------------------------------------------------------------- look (shared files)
    css = "".join("/* ---- %s ---- */\n%s\n" % (f, read("chrome", f)) for f in
                  ("base.css", "nav.css", "lang.css", "search.css", "footer.css", "article.css"))
    js = "".join("/* ---- %s ---- */\n%s\n" % (f, read("chrome", f)) for f in ("nav.js", "lang.js"))
    write(root, "css/site.css", css)
    write(root, "js/site-chrome.js", js)
    write(root, "js/site-search.js", read("chrome", "site-search.js"))
    css_v = hashlib.sha256(css.encode()).hexdigest()[:10]
    js_v = hashlib.sha256(js.encode()).hexdigest()[:10]

    # ---------------------------------------------------------------- pages
    header = render_header(menu)
    logo = (f'<img alt="{name_e} Logo" decoding="async" height="28" loading="lazy" src="{html.escape(a.logo)}" '
            f'style="border-radius: 50%; display: inline-block; flex-shrink: 0;" width="28"/>') if a.logo else ""
    cols = ('<div>\n<div class="footer-col-title">Company</div>\n<div class="footer-links-list">\n'
            '<a class="footer-link-item" href="/about">About</a>\n'
            '<a class="footer-link-item" href="/contact">Contact</a>\n'
            '<a class="footer-link-item" href="/privacy">Privacy</a>\n</div>\n</div>')
    footer = fill(read("footer.html"), {
        "LOGO_IMG": logo, "BRAND_UPPER": name_e.upper(), "BRAND_DESC": html.escape(tagline),
        "FOOTER_COLS": cols, "YEAR": str(datetime.date.today().year), "DOMAIN_NAME": html.escape(bare[:1].upper() + bare[1:]),
    }).rstrip("\n")
    common = {"NAME": name_e, "TAGLINE": html.escape(tagline), "CONTACT_EMAIL": html.escape(a.email or f"hello@{bare}"),
              "GUIDE_TILES": '<a class="site-tile" href="/about"><strong>How we test</strong><span>Who we are and how we pick what we recommend.</span></a>'}
    pages = [
        ("index.html", "/", f"{a.name}: {tagline}", tagline, "home.html"),
        ("about/index.html", "/about", f"About {a.name}", f"Who is behind {a.name} and how we test.", "about.html"),
        ("contact/index.html", "/contact", f"Contact {a.name}", f"How to reach {a.name}.", "contact.html"),
        ("privacy/index.html", "/privacy", f"Privacy policy | {a.name}", f"Privacy policy of {a.name}.", "privacy.html"),
        ("404.html", "/404", f"Page not found | {a.name}", "This page does not exist.", "404.html"),
    ]
    for rel, path, title, desc, body in pages:
        url = domain + ("" if path == "/" else path)
        ld = {"@context": "https://schema.org", "@type": "WebSite" if path == "/" else "WebPage",
              "name": title, "url": url}
        write(root, rel, fill(read("page.html"), {
            "LANG": "en", "TITLE": html.escape(title), "DESCRIPTION": html.escape(desc), "CANONICAL": url,
            "JSONLD": json.dumps(ld, ensure_ascii=False), "HEADER": header, "FOOTER": footer,
            "MAIN": fill(read("pages", body), common).strip("\n"), "CSS_V": css_v, "JS_V": js_v,
        }))
    today = datetime.date.today().isoformat()
    urls = "".join(f"  <url>\n    <loc>{domain}{'' if p == '/' else p}</loc>\n    <lastmod>{today}</lastmod>\n  </url>\n"
                   for _, p, _, _, _ in pages if p != "/404")
    write(root, "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")

    # ---------------------------------------------------------------- kit, sync, checks
    r = subprocess.run([sys.executable, os.path.join(HERE, "update.py"), "--site", root, "--no-check"])
    if r.returncode:
        sys.exit("kit install failed")
    subprocess.run([sys.executable, "scripts/sync_layout.py"], cwd=root, check=True)
    r = subprocess.run([sys.executable, "kit/checks/check_all.py"], cwd=root)
    print(f"\n{root}: new site written; checks {'PASSED' if r.returncode == 0 else 'FAILED'}")
    print("Next: fill the [Owner: ...] gaps, commit, push, connect the repo in Vercel, open a PR.")
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
