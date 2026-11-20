#!/usr/bin/env python3
"""Build a new EN city listicle (kit listicle design) from a spec.

    python3 scripts/build_city_listicle.py <slug>          # spec: scripts/city_listicles/<slug>.py
    python3 scripts/build_city_listicle.py <slug> --photos # download the card photos first

The page shell (head, header, footer, kit CSS/JS, sticky bar) is the EN Warsaw page
(/vistula-river-cruises-warsaw), the newest city page on the kit listicle design. The
builder swaps the head meta, JSON-LD, hero (H1, intro, filters), card deck, detailed
breakdown, editorial sections and page config, writes the card data file
data/listicles/<slug>--index.json and renders the cards with the kit's
`listicle.py build`. Then run scripts/sync_layout.py (menu, footer, search index).

Spec (a Python module defining SPEC = dict(...)): see scripts/city_listicles/README.md.
Facts in a spec come from the live GetYourGuide / Tiqets listings on SPEC["checked"].
"""
import html
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://www.thecruisedetective.com"
TEMPLATE = ROOT / "vistula-river-cruises-warsaw" / "index.html"
TEMPLATE_DATA = ROOT / "data" / "listicles" / "vistula-river-cruises-warsaw--index.json"
GYG_PID = "YS414AJ"
TQ_PID = "thecruisedetective.com-176436"
STAR = ('<svg aria-hidden="true" viewbox="0 0 24 24"><path d="M11.9999 18.26L4.94691 22.208L6.52191 '
        '14.28L0.586914 8.792L8.61391 7.84L11.9999 0.5L15.3859 7.84L23.4129 8.792L17.4779 14.28L19.0529 '
        '22.208L11.9999 18.26Z"></path></svg>')
PLACEHOLDER = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 800 500'%3E%3C/svg%3E"
E = html.escape


def load_spec(slug):
    p = ROOT / "scripts" / "city_listicles" / (slug.replace("-", "_") + ".py")
    spec = importlib.util.spec_from_file_location("spec_" + slug.replace("-", "_"), p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.SPEC


# ------------------------------------------------------------------ links and numbers
def gyg_url(S, c, tag=None):
    path = c["gyg"]
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path += "/"
    cmp = f"article-{S['slug']}-{tag or c['key']}"
    return f"https://www.getyourguide.com{path}?partner_id={GYG_PID}&utm_medium=online_publisher&cmp={cmp}&mkt_cmp=true"


def tq_url(S, c, tag=None):
    path = c["tq"].strip("/")
    camp = f"{S['slug']}-{tag or c['key']}"
    return f"https://www.tiqets.com/en/{path}/?partner={TQ_PID}&tq_campaign={camp}"


def book_url(S, c, tag=None):
    return tq_url(S, c, tag) if c.get("site") == "Tiqets" else gyg_url(S, c, tag)


def site_of(c):
    return c.get("site", "GetYourGuide")


def rating_link(S, c, site, rest):
    """Affiliate link for a rating badge: the booked site, or the other partner when the card has its path."""
    tag = c["key"] + "-pop"
    if site == site_of(c):
        return book_url(S, c, tag)
    if site == "GetYourGuide" and c.get("gyg"):
        return gyg_url(S, c, tag)
    if site == "Tiqets" and c.get("tq"):
        return tq_url(S, c, tag)
    return rest[0] if rest and rest[0] else None


def money(v):
    if v is None:
        return ""
    if abs(v - round(v)) < 0.005:
        return f"€{int(round(v)):,}"
    return f"€{v:,.2f}"


def count(n):
    return f"{n:,}"


def weighted(ratings):
    tot = sum(r[2] for r in ratings)
    if not tot:
        return 0.0, 0
    return sum(r[1] * r[2] for r in ratings) / tot, tot


def per_hour(c):
    h = c.get("hours")
    if not h or not c.get("price"):
        return ""
    return money(round(c["price"] / h))


def maps(q):
    from urllib.parse import quote_plus
    return "https://www.google.com/maps/search/?api=1&query=" + quote_plus(q)


def anchor(S, c):
    return f"{S['prefix']}-{c['key']}"


# ------------------------------------------------------------------ photos
def photo_dir(S):
    return ROOT / "assets" / S["slug"]


def photo_files(S, c):
    d = photo_dir(S)
    stem = f"{S['photo_stem']}-{c['key']}-"
    if not d.exists():
        return []
    return sorted(f.name for f in d.iterdir() if f.name.startswith(stem) and re.fullmatch(re.escape(stem) + r"\d\d\.avif", f.name))


def photo_src(S, name):
    return f"/assets/{S['slug']}/{name}"


def alt_of(c, i, n):
    alts = c.get("alts") or []
    if i < len(alts) and alts[i]:
        return alts[i]
    return f"{c['title']}, photo {i + 1}"


def fact(c, *names):
    for k, v in c.get("facts", []):
        if k in names:
            return v
    return None


def auto_pills(c):
    """The card's own pills plus the river-card standard ones (time first; meeting point, cancellation and
    price per hour after), built only from facts already on the card, up to 8 pills."""
    own = list(c["pills"])
    emojis = {p[0] for p in own}
    labels = " ".join(p[1].lower() for p in own)
    out = []
    if not emojis & {"⏱️", "🕰️"}:
        out.append(("⏱️", c["len"], f"{fact(c, 'Duration') or c['dur']}.", None))
    out += own
    if "📍" not in emojis and len(out) < 8:
        mp = fact(c, "Meeting point", "Departure", "Start", "Location", "Pick-up", "Dock")
        out.append(("📍", c["pier"], f"{mp or c['pier']}.", None))
    if "↩️" not in emojis and "refundable" not in labels and "cancel" not in labels and len(out) < 8:
        cx = fact(c, "Cancellation") or ""
        if "Non-refundable" in cx or c.get("cancel") is False:
            out.append(("🎟️", "Non-refundable", "This ticket can't be cancelled or changed.", "Book once your dates are fixed."))
        elif cx:
            out.append(("↩️", "Free cancellation", f"{cx}.", "Reserve now, pay later."))
    ph = c.get("per_hour") or per_hour(c)
    if ph and c.get("unit", "adult") == "adult" and len(out) < 8 and len(out) < 6:
        out.append(("💶", f"{ph} an hour", f"{money(c['price'])} for {c['len']},", f"about {ph} an hour per adult.", None))
    if c.get("unit", "adult") != "adult" and len(out) < 6:
        n = c.get("max_people", 5)
        out.append(("👥", f"Up to {n} people", f"{money(c['price'])} for the whole {c['unit']},",
                    f"about {money(round(c['price'] / n, 2))} each if {n} share.", None))
    return out[:8]


# ------------------------------------------------------------------ card data (kit listicle format)
def card_data(S, n, c):
    files = photo_files(S, c)
    if not files:
        raise SystemExit(f"no photos for {c['key']} in assets/{S['slug']}/")
    photos = []
    for i, f in enumerate(files):
        a = [["alt", alt_of(c, i, len(files))], ["height", "534"], ["width", "800"]]
        if i == 0:
            a += [["loading", "eager"], ["fetchpriority", "high"] if n == 1 else ["decoding", "async"], ["src", photo_src(S, f)]]
        else:
            a += [["loading", "lazy"], ["decoding", "async"], ["data-src", photo_src(S, f)], ["src", PLACEHOLDER]]
        photos.append(a)
    url = book_url(S, c)
    avg, tot = weighted(c["ratings"])
    sites = []
    for site, score, cnt, *rest in c["ratings"]:
        link = rating_link(S, c, site, rest)
        if link:
            sites.append({"kind": "link", "site": site, "score": f"{score:.1f}", "count": f"({count(cnt)})",
                          "url": link, "rel": "noopener nofollow sponsored", "target": "_blank"})
        else:
            sites.append({"kind": "static", "site": site, "score": f"{score:.1f}", "count": f"({count(cnt)})"})
    if len(c["ratings"]) > 1:
        meta = f"{count(tot)} reviews · {len(c['ratings'])} sites"
        heading = "Average of the booking sites, weighted by number of reviews"
    else:
        meta = f"{count(tot)} reviews · {c['ratings'][0][0]}"
        heading = f"Rating on {c['ratings'][0][0]}"
    pills = []
    for pl in auto_pills(c):
        emoji, label, lead = pl[:3]
        rest, note = (pl[3], pl[4]) if len(pl) == 5 else (None, pl[3])
        pop = f"<strong>{lead}</strong>" + (f" {rest}" if rest else "") + (f'<span class="bpa-lang-note">{note}</span>' if note else "")
        pills.append({"cls": "bpa-lang", "emoji": emoji, "label": label, "pop_html": pop})
    rows = [{"label": l, "small": s, "price": ("From " + money(p)) if isinstance(p, (int, float)) else p}
            for l, s, p in c.get("rows") or [("Adult", c["dur"].lower(), c["price"])]]
    unit = c.get("unit", "adult")
    price = {"main": money(c["price"]), "sub": c.get("psub", f"per {unit}, from"), "rows": rows}
    if c.get("total", True) and unit == "adult":
        price["total"] = {"label": "2 adults", "price": "From " + money(round(c["price"] * 2, 2))}
    price["note"] = "The final price is shown before you pay."
    trust = c.get("trust") or (["<b>Free cancellation</b>", "<b>Reserve now, pay later</b>"] if c.get("cancel", True) else ["<b>Instant confirmation</b>"])
    card = {
        "id": f"card-{n}",
        "cats": c["cats"].split(),
        "gallery": {"rank": {"text": c["rank"], "medal": c.get("medal", "")}, "photos": photos,
                    "thumbs": [{"src": photo_src(S, f)} for f in files]},
        "kicker": [c["operator"], f"⏱️ {c['dur']}",
                   {"url": maps(c["maps"]), "onclick": "event.stopPropagation()", "rel": "noopener noreferrer",
                    "target": "_blank", "map": f"📍 {c['pier']}"}],
        "title": {"url": url, "rel": "noopener nofollow sponsored", "target": "_blank", "text": E(c["title"], quote=False)},
        "reviews": {"ratings": {"stars": f"{avg:.2f}", "score": f"{avg:.1f}", "meta": meta, "heading": heading, "sites": sites}},
        "pills": pills,
        "best_for": {"pick_html": c["pick"], "skip_html": c["skip"]},
        "faq": {"items": [{"q": q, "a": a} for q, a in c["faq"]]},
        "price": price,
        "cta": {"btn": {"url": url, "rel": "noopener nofollow sponsored", "target": "_blank", "text": "Check Availability →"},
                "via": f"Booked securely via {site_of(c)}", "trust": trust,
                "sublink": {"url": "#" + anchor(S, c), "text": "Read Review ↓"}},
    }
    if len(c["faq"]) != 5:
        raise SystemExit(f"{c['key']}: needs exactly 5 card questions, has {len(c['faq'])}")
    return card


# ------------------------------------------------------------------ breakdown (details) blocks
def rate_block(S, c, icons):
    avg, tot = weighted(c["ratings"])
    badges = []
    for site, score, cnt, *rest in c["ratings"]:
        icon = f'<img alt="{site}" class="bpa-rev-icon" loading="lazy" src="{icons.get(site, "")}"/>'
        inner = (icon + f'<span class="bpa-rev-site">{site}</span><span class="bpa-rev-score">{score:.1f}</span>'
                 f'<span class="bpa-rev-stars">{STAR * 5}</span><span class="bpa-rev-count">({count(cnt)})</span>')
        link = rating_link(S, c, site, rest)
        if link:
            badges.append(f'<a class="bpa-rev-badge is-link" href="{E(link)}" rel="noopener nofollow sponsored" target="_blank">'
                          + inner + '<span class="bpa-rev-go" aria-hidden="true">→</span></a>')
        else:
            badges.append('<span class="bpa-rev-badge is-static">' + inner + '</span>')
    if len(c["ratings"]) > 1:
        meta, head = f"{count(tot)} reviews · {len(c['ratings'])} sites", "Average of the booking sites, weighted by number of reviews"
    else:
        meta, head = f"{count(tot)} reviews · {c['ratings'][0][0]}", f"Rating on {c['ratings'][0][0]}"
    return ('<div class="bpa-reviews-line"><div class="bpa-summary-reviews bpa-rate"><details class="bpa-lang bpa-rate-more">'
            f'<summary class="bpa-rate-sum"><span class="bpa-stars" style="--r:{avg:.2f}" aria-hidden="true"></span>'
            f'<b class="bpa-rate-score">{avg:.1f}</b><span class="bpa-rate-meta">{meta}</span>'
            '<span class="bpa-lang-chev" aria-hidden="true">▾</span></summary><div class="bpa-lang-pop">'
            f'<strong>{head}</strong><span class="bpa-rate-list">{"".join(badges)}</span></div></details></div></div>')


def details_block(S, n, c, icons):
    files = photo_files(S, c)
    slides = "".join(f'<div class="ltt-strip-slide"><img alt="{E(alt_of(c, i, len(files)))}" loading="lazy" '
                     f'src="{photo_src(S, f)}"/></div>' for i, f in enumerate(files))
    pros = "".join(f"<li><strong>{b}</strong>{': ' + t if t else ''}</li>" for b, t in c["pros"])
    cons = "".join(f"<li><strong>{b}</strong>{': ' + t if t else ''}</li>" for b, t in c["cons"])
    summ = "".join(f"<p>{p}</p>" for p in c["summary"])
    facts = "".join(f'<div class="qf1-row"><div class="qf1-label">{k}</div><div class="qf1-val">{v}</div></div>' for k, v in c["facts"])
    url = book_url(S, c, c["key"] + "-review")
    return f'''<details class="bpa-details-card" data-cat="{c['cats']}" id="{anchor(S, c)}"{' open=""' if n == 1 else ''}>
<summary class="bpa-details-summary">
<div class="bpa-details-summary-content">
<div class="bpa-details-top-row">
<span class="bpa-rank-tag {c.get('medal', '')}">{c['rank']}</span>
<div class="bpa-kicker">{E(c['operator'], quote=False)} • ⏱️ {c['dur']} • <a class="bpa-kicker-map-link" href="{E(maps(c['maps']))}" onclick="event.stopPropagation()" rel="noopener noreferrer" target="_blank">📍 {E(c['pier'], quote=False)}</a></div>
</div>
<h3 class="bpa-details-title">{E(c['title'], quote=False)}</h3>
{rate_block(S, c, icons)}
</div>
<div class="bpa-details-right">
<span class="bpa-details-price">From {money(c['price'])}</span>
<div class="bpa-details-toggle">
<span class="bpa-details-state-text"></span>
<span class="bpa-details-chevron">▾</span>
</div>
</div>
</summary>
<div class="bpa-details-body">
<div class="pro-con-box-wrapper"><div class="w-layout-grid grid-15"><div class="pro-con-box-pro-cell" data-wf-pbl="layout-grid-1x2-vertical"><div class="pro-con-box-pro-cell-rich-text-block w-richtext"><h3><strong>Pros:</strong></h3><ul>{pros}</ul></div></div><div class="pro-con-box-con-cell" data-wf-pbl="layout-grid-1x2-vertical"><div class="pro-con-box-con-cell-rich-text-block w-richtext"><h3><strong>Cons:</strong></h3><ul>{cons}</ul></div></div></div></div><details class="ltt-bento-group" open=""><summary class="ltt-bento-group-head"><span class="ltt-bento-group-title">📸 Photos</span><span class="ltt-bento-right"><span class="ltt-mini-pill">Swipe {len(files)} Photos →</span><span class="ltt-bento-chev">▾</span></span></summary><div class="ltt-bento-group-body" style="padding: 12px 14px !important;"><div class="ltt-filmstrip-wrap"><button aria-label="Previous photo" class="ltt-film-btn ltt-film-prev is-disabled" onclick="window.lttFilmSlide(this, -1)" type="button">‹</button><button aria-label="Next photo" class="ltt-film-btn ltt-film-next" onclick="window.lttFilmSlide(this, 1)" type="button">›</button><div class="ltt-filmstrip" onscroll="window.lttFilmSync(this)">{slides}</div></div></div></details><details class="ltt-bento-group" open="">
<summary class="ltt-bento-group-head">
<span class="ltt-bento-group-title">Summary &amp; Review</span>
<span class="ltt-bento-right">
<span class="ltt-mini-pill">Overview</span>
<span class="ltt-bento-chev">▾</span>
</span>
</summary>
<div class="ltt-bento-group-body">
<div class="w-richtext">{summ}</div>
</div>
</details>
<div class="qf1-wrap"><div class="qf1-title-row"><h4 class="qf1-title">Quick Facts</h4><span class="qf1-badge">{E(c['pier'], quote=False)}</span></div><div class="qf1-table">{facts}</div></div>
<a class="bpa-btn" href="{E(url)}" rel="noopener nofollow sponsored" style="margin-top:14px;display:block;text-align:center" target="_blank">Check Availability: From {money(c['price'])} →</a></div>
</details>'''


# ------------------------------------------------------------------ editorial
def logistics_table(S):
    cols = S.get("table_cols", [])
    head = "<th>Tour</th><th>Boards at</th><th>Length</th><th>Price</th><th>Per hour</th>" + "".join(f"<th>{h}</th>" for h, _ in cols)
    rows = []
    for i, c in enumerate(S["cards"], 1):
        extra = "".join(f"<td>{c.get('table', {}).get(k, '')}</td>" for _, k in cols)
        rows.append(f'<tr><td><a href="#{anchor(S, c)}">{i}. {E(c["short_name"], quote=False)}</a></td><td>{E(c["pier"], quote=False)}</td>'
                    f'<td>{c["len"]}</td><td>{money(c["price"])}</td><td>{c.get("per_hour") or per_hour(c)}</td>{extra}</tr>')
    return f'<div class="wc-table-wrap"><table class="wc-table"><thead><tr>{head}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


NAMES = {
    "chicago-architecture-boat-tours": "Chicago architecture boat tours",
    "boat-tours-boston": "Boston boat tours",
    "niagara-falls-boat-tours": "Niagara Falls boat tours",
    "boat-tours-san-diego": "San Diego whale watching and harbor cruises",
    "boat-tours-miami": "Miami boat tours",
    "boat-tours-new-orleans": "New Orleans steamboat and swamp tours",
    "gondola-rides-venice": "Venice gondola rides",
    "boat-tours-lake-como": "Lake Como boat tours",
    "ha-long-bay-cruises": "Ha Long Bay cruises",
    "chao-phraya-river-cruises-bangkok": "Chao Phraya river cruises in Bangkok",
}


def related_html(S):
    rel = [r for r in S.get("related", []) if r in NAMES and r != S["slug"]]
    if not rel:
        return ""
    links = [f'<a href="/{r}">{NAMES[r]}</a>' for r in rel]
    return "<p>More boat trips compared side by side: " + ", ".join(links[:-1]) + " and " + links[-1] + ".</p>"


def sections_html(S):
    out = ['<style>.ltt-editorial-wrapper section{margin-bottom:0!important}.ltt-editorial-wrapper section h2{margin-top:32px!important}'
           '.ltt-editorial-wrapper section:first-of-type h2{margin-top:40px!important}.ltt-editorial-wrapper section h3{margin-top:22px!important}</style>']
    for i, (sid, toc, body) in enumerate(S["sections"]):
        body = body.replace("{TABLE}", logistics_table(S))
        if i == 0:
            body += related_html(S)
        out.append(f'<section data-toc="{toc}" id="{S["prefix"]}-{sid}"><div class="w-richtext">{body}</div></section>')
    faq = "".join(f"<h3>{q}</h3><p>{a}</p>" for q, a in S["faq"])
    out.append(f'<section data-toc="FAQ" id="{S["prefix"]}-faq"><div class="w-richtext"><h2>{S["faq_h2"]}</h2>{faq}</div></section>')
    out.append(f'<section data-toc="How I Compared" id="{S["prefix"]}-methodology"><div class="w-richtext"><h2>{S["method_h2"]}</h2>{S["method"]}</div></section>')
    return "".join(out)


def filters_html(S):
    rows = []
    for gi, (label, chips) in enumerate(S["filters"]):
        cls = "cd-frow cd-frow-main" if gi == 0 else "cd-frow cd-frow-more"
        btns = "".join(f'<button class="ltt-tab-btn" data-cat="{cat}" onclick="lttFilterCruises(\'{cat}\', this)" type="button" '
                       f'aria-pressed="false">{text} <span class="cd-n"></span></button>' for cat, text in chips)
        rows.append(f'<div class="{cls}"><span class="cd-flab">{label}</span><div class="cd-fchips">{btns}</div></div>')
    n = len(S["cards"])
    noun = S.get("noun", "tours")
    return (f'<div class="ltt-integrated-filter-bar cd-fbox" id="cd-filters" role="group" aria-label="Filter {noun}">' + "".join(rows)
            + '<button type="button" class="cd-fmore" aria-expanded="false" hidden>More filters <span class="cd-fmore-n"></span> ▾</button>'
            f'<div class="cd-ffoot"><span class="cd-fcount" aria-live="polite">Showing <b>{n}</b> of {n} {noun}</span>'
            '<div class="cd-fapplied"></div><button type="button" class="cd-fclear" hidden onclick="lttFilterCruises(\'all\')">Clear all</button></div></div>')


def hero_html(S):
    intro = "".join(f"<p>{p}</p>" for p in S["intro"])
    return f'''<div class="ltt-top-bar">
<nav aria-label="Breadcrumb" class="ltt-breadcrumbs">
<a href="/">Home</a>
<span class="ltt-bc-sep">›</span>
<span class="ltt-bc-current">{S['h1']} ({S['year']})</span>
</nav>
<span class="ltt-hero-kicker-badge">{S['badge']}</span>
</div>
<h1 class="ltt-editorial-h1">{S['h1']} <span class="ltt-h1-muted">({S['year']})</span></h1>
<div class="ltt-trust-bar">
<div class="ltt-author-cluster">
<div class="ltt-author-avatar-wrap">
<img alt="Adam Dimitrov" class="ltt-author-avatar" src="/assets/cdn/652d0405192ba076b04f74a3/652d0405192ba076b04f792e_Adam-dimitrov-portrait-75x75.webp"/>
</div>
<div class="ltt-author-meta">
<div class="ltt-author-line">
            By <a href="/about" target="_blank">Adam Dimitrov</a>, Owner &amp; Head Cruise Detective
          </div>
<div class="ltt-author-role">Independent side-by-side comparison</div>
</div>
</div>
<div class="ltt-trust-pills">
<span class="ltt-trust-pill paragraph-26"><strong>Last updated</strong>: {S['updated']}</span>
</div>
</div>
<div class="ltt-lead-copy">
{intro}
</div>
{filters_html(S)}'''


def jsonld(S, card_q):
    url = f"{SITE}/{S['slug']}"
    first = [f"{SITE}{photo_src(S, photo_files(S, c)[0])}" for c in S["cards"]]
    items = []
    for i, c in enumerate(S["cards"], 1):
        items.append({"@type": "ListItem", "position": i, "url": f"{url}#{anchor(S, c)}",
                      "item": {"@type": "Product", "name": c["title"], "image": first[i - 1],
                               "brand": {"@type": "Brand", "name": c["operator"]},
                               "offers": {"@type": "Offer", "price": f"{c['price']:.2f}", "priceCurrency": "EUR",
                                          "url": book_url(S, c), "availability": "https://schema.org/InStock"},
                               "aggregateRating": {"@type": "AggregateRating", "ratingValue": f"{weighted(c['ratings'])[0]:.1f}",
                                                   "reviewCount": weighted(c["ratings"])[1], "bestRating": "5"}}})
    faq = [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
           for q, a in S["faq"] + card_q]
    g = {"@context": "https://schema.org", "@graph": [
        {"@type": "Article", "@id": f"{url}#article", "headline": f"{S['h1']} ({S['year']})", "description": S["meta_desc"],
         "image": first, "datePublished": S["published"], "dateModified": S["modified"], "inLanguage": "en",
         "mainEntityOfPage": {"@type": "WebPage", "@id": url},
         "author": {"@type": "Person", "name": "Adam Dimitrov", "jobTitle": "Owner & Head Cruise Detective", "url": f"{SITE}/about"},
         "publisher": {"@type": "Organization", "name": "The Cruise Detective", "url": SITE,
                       "logo": {"@type": "ImageObject", "url": f"{SITE}/assets/cdn/652d0405192ba076b04f74a3/6570a89c8c97ba4e084ac5d5_webclip-cruise-detective.png"}},
         "mainEntity": {"@id": f"{url}#list"}},
        {"@type": "BreadcrumbList", "@id": f"{url}#breadcrumb", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": f"{S['h1']} ({S['year']})", "item": url}]},
        {"@type": "ItemList", "@id": f"{url}#list", "name": S["h1"], "numberOfItems": len(items), "itemListElement": items},
        {"@type": "FAQPage", "@id": f"{url}#faq", "mainEntity": faq}]}
    return json.dumps(g, ensure_ascii=False, indent=2)


# ------------------------------------------------------------------ assemble
def balanced_div_end(s, start):
    depth = 0
    for t in re.finditer(r"<(/?)div\b[^>]*>", s[start:]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            return start + t.end()
    raise SystemExit("unbalanced div")


def build(slug):
    S = load_spec(slug)
    S["slug"] = slug
    S.setdefault("prefix", "cl")
    for c in S["cards"]:
        c.setdefault("short_name", c["operator"])
        c.setdefault("len", c["dur"].replace(" Hours", " h").replace(" Hour", " h").replace(" Min", " min"))
    src = TEMPLATE.read_text()
    icons = json.loads(TEMPLATE_DATA.read_text())["icons"]
    old_url = f"{SITE}/vistula-river-cruises-warsaw"
    url = f"{SITE}/{slug}"
    first_photo = f"{SITE}{photo_src(S, photo_files(S, S['cards'][0])[0])}"

    # head
    src = re.sub(r"<title>[^<]*</title>", f"<title>{E(S['meta_title'], quote=False)}</title>", src, count=1)
    src = re.sub(r'<meta content="[^"]*" name="description"/>', f'<meta content="{E(S["meta_desc"])}" name="description"/>', src, count=1)
    for prop in ("og:title", "twitter:title"):
        src = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda m: f'<meta content="{E(S["h1"] + " (" + S["year"] + ")")}" {m.group(1)}="{prop}"/>', src, count=1)
    for prop in ("og:description", "twitter:description"):
        src = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda m: f'<meta content="{E(S["meta_desc"])}" {m.group(1)}="{prop}"/>', src, count=1)
    for prop in ("og:image", "twitter:image"):
        src = re.sub(rf'<meta content="[^"]*" (property|name)="{prop}"/>', lambda m: f'<meta content="{first_photo}" {m.group(1)}="{prop}"/>', src, count=1)
    src = re.sub(r'<link href="[^"]*" hreflang="pl" rel="alternate"/>\n', "", src)
    src = src.replace(old_url, url)
    src = re.sub(r'<link as="image" fetchpriority="high" href="[^"]*" rel="preload"/>',
                 f'<link as="image" fetchpriority="high" href="{photo_src(S, photo_files(S, S["cards"][0])[0])}" rel="preload"/>', src, count=1)

    # card questions for FAQPage
    card_q = [(f"{c['operator']}: {q}", a) for c in S["cards"] for q, a in c["faq"]]
    src = re.sub(r'<script id="vistula-schema-jsonld" type="application/ld\+json">.*?</script>',
                 lambda m: f'<script id="{S["prefix"]}-schema-jsonld" type="application/ld+json">{jsonld(S, card_q)}</script>', src, count=1, flags=re.S)

    # hero + filters
    a = src.index('<div class="ltt-top-bar">')
    fb = src.index('<div class="ltt-integrated-filter-bar cd-fbox"')
    b = balanced_div_end(src, fb)
    src = src[:a] + hero_html(S) + src[b:]

    # deck: cards -> marker
    deck_id = f"{S['prefix']}-deck"
    src = src.replace('id="warsaw-vistula-cruise-deck"', f'id="{deck_id}"')
    spans = [m.start() for m in re.finditer(r'<div class="bpa-card"[ >]', src)]
    c0 = spans[0]
    cend = balanced_div_end(src, spans[-1])
    src = src[:c0] + "<!-- listicle:cards -->" + src[cend:]

    # breakdown
    bt = src.index('<div class="bpa-breakdown-top-bar" id="breakdown-header">')
    last = src.rfind("</details>", bt, src.index("<style>\n\n.ltt-editorial-wrapper", bt)) + len("</details>")
    n = len(S["cards"])
    top = f'''<div class="bpa-breakdown-top-bar" id="breakdown-header">
<div>
<h2 class="bpa-breakdown-heading" id="{S['prefix']}-breakdown">{S['breakdown_h2']}</h2>
<p class="bpa-breakdown-sub">{S['breakdown_sub']}</p>
</div>
<div class="bpa-acc-controls">
<button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(true)" type="button">Expand All</button>
<button class="bpa-acc-ctrl-btn" onclick="toggleAllDetails(false)" type="button">Collapse All</button>
</div>
</div>'''
    src = src[:bt] + top + "\n".join(details_block(S, i, c, icons) for i, c in enumerate(S["cards"], 1)) + src[last:]

    # editorial sections
    s0 = src.index('<style>.ltt-editorial-wrapper section{')
    s1 = src.index("</div></div></div></div></div></main>", s0)
    src = src[:s0] + sections_html(S) + "\n" + src[s1:]

    # sticky bar, sheet, page config
    c1 = S["cards"][0]
    src = re.sub(r'(<span>All )10 Vistula Cruises(</span>)', lambda m: f"{m.group(1)}{n} {S['sheet_noun']}{m.group(2)}", src)
    src = re.sub(r'(<span class="hybrid-active-title" id="sticky-name">)[^<]*', lambda m: m.group(1) + E(c1["short"], quote=False), src)
    src = re.sub(r'(<span class="hybrid-active-price" id="sticky-price">)[^<]*', lambda m: m.group(1) + "From " + money(c1["price"]), src)
    src = re.sub(r'(<a class="hybrid-cta-btn" href=")[^"]*(" id="sticky-cta-btn")', lambda m: m.group(1) + E(book_url(S, c1, c1["key"] + "-sticky")) + m.group(2), src)
    src = src.replace('aria-label="Jump to a Warsaw Cruise"', f'aria-label="Jump to a {E(S["sheet_one"])}"')
    src = src.replace('<h3 class="hybrid-sheet-title">Jump to a Warsaw Cruise</h3>', f'<h3 class="hybrid-sheet-title">Jump to a {E(S["sheet_one"], quote=False)}</h3>')
    cfg = {"deckId": deck_id, "tocDeckLabel": S["toc_deck"], "tocBreakdownLabel": f"Detailed Breakdown ({n} {S['sheet_noun'].split()[-1]})",
           "shortTitles": [c["short"] for c in S["cards"]]}
    src = re.sub(r"window\.LTT_PAGE_CONFIG = \{.*?\};", lambda m: "window.LTT_PAGE_CONFIG = " + json.dumps(cfg, ensure_ascii=False) + ";", src, count=1, flags=re.S)
    src = src.replace('<style id="vistula-extra-css">', f'<style id="{S["prefix"]}-extra-css">')
    if S.get("noun") and S["noun"] != "cruises":
        nn = S["noun"]
        src = src.replace('aria-label="Filter cruises"', f'aria-label="Filter {nn}"')
        ui = {"showing": f"Showing <b>{{shown}}</b> of {{total}} {nn}", "mini_count": f"<b>{{shown}}</b> of {{total}} {nn}",
              "breakdown_filtered": f"Showing {{shown}} of {{total}} {nn} matching your filters"}
        tag = '<script type="application/json" id="listicle-ui">' + json.dumps(ui, ensure_ascii=False) + "</script>\n"
        i = src.index('<script src="/js/listicle-lang.js')
        src = src[:i] + tag + src[i:]

    out = ROOT / slug / "index.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(src)
    data = {"format": 1, "icons": {k: v for k, v in icons.items() if any(r[0] == k for c in S["cards"] for r in c["ratings"])},
            "cards": [card_data(S, i, c) for i, c in enumerate(S["cards"], 1)]}
    dp = ROOT / "data" / "listicles" / f"{slug}--index.json"
    if dp.exists():  # keep recorded photo top-up decisions (photo_topup.py skip) across rebuilds
        old = {c.get("id"): c for c in json.loads(dp.read_text()).get("cards", [])}
        for c in data["cards"]:
            for k, v in old.get(c["id"], {}).items():
                if k.startswith("_"):
                    c[k] = v
    dp.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "listicle.py"), "build", str(out)], capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stdout + r.stderr)
    left = [m.group(0) for m in re.finditer(r"(?i)[^\n]{0,40}(warsaw|vistula)[^\n]{0,40}", out.read_text())]
    hdr = out.read_text()
    left = [x for x in left if "href=\"/vistula-river-cruises-warsaw\"" not in x and "/pl/" not in x]
    print(f"built /{slug}: {n} cards, {sum(len(photo_files(S, c)) for c in S['cards'])} photos")
    if left:
        print("template words left (check):", *left[:12], sep="\n  ")


def fetch_photos(slug):
    """Download each card's GetYourGuide gallery (hashes in c['gallery'], order = c['order'] or listing order),
    cover-crop to 1200x800 and save as AVIF. Never overwrites."""
    S = load_spec(slug)
    S["slug"] = slug
    sys.path.insert(0, str(ROOT / "kit" / "scripts"))
    import io
    import urllib.request
    from PIL import Image
    from photo_topup import fit, UA
    d = photo_dir(S)
    d.mkdir(parents=True, exist_ok=True)
    for c in S["cards"]:
        if photo_files(S, c):
            continue
        srcs = c.get("photo_urls") or [f"https://cdn.getyourguide.com/image/fit=cover,width=1200,height=800/tour_img/{h}" for h in c["gallery"]]
        for i, u in enumerate(srcs[:10], 1):
            req = urllib.request.Request(u, headers={"User-Agent": UA})
            im = Image.open(io.BytesIO(urllib.request.urlopen(req, timeout=40).read()))
            dest = d / f"{S['photo_stem']}-{c['key']}-{i:02d}.avif"
            fit(im).save(dest, "AVIF", quality=60)
        print(c["key"], len(srcs[:10]))


if __name__ == "__main__":
    slug = sys.argv[1]
    if "--photos" in sys.argv:
        fetch_photos(slug)
    build(slug)
