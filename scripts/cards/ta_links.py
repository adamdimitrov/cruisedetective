#!/usr/bin/env python3
"""Tripadvisor rows in the card rating popover: turn static rows into Travelpayouts links.

The rating popover (details.bpa-rate-more > .bpa-rate-list) has one .bpa-rev-badge per site.
A row is a link (<a class="bpa-rev-badge is-link">) only when we know the exact listing.
PR #158 linked the rows it could verify by hand; the rows below stayed <span class="is-static">
because no listing had been matched yet. TA_LISTINGS is the record of those matches, keyed by
the card's product id (Tiqets pNNN / GYG tNNN from the card title link), so it works on the EN
page, every translation and any other page that carries the same card.

Each entry was checked live on tripadvisor.com (2026-11-16): same product, rating equal to the
card's Tripadvisor score, review count consistent with the card. A row is only converted when
its score still equals `score`, so a stale or different row is never linked by accident.

Usage
  python3 scripts/cards/ta_links.py            # apply to every card page
  python3 scripts/cards/ta_links.py --check    # exit 1 if a mapped row is still static;
                                               # also lists every remaining static Tripadvisor row
"""
import argparse
import re
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from cards import ROOT, card_pages  # noqa: E402

TA = "https://www.tripadvisor.com/"
TA_LISTINGS = {
    # Seine (seine-river-cruises-paris)
    "p973977": ("3.5", "AttractionProductReview-g187147-d11452714-Paris_Seine_River_Sightseeing_Cruise_with_Commentary_by_Bateaux_Parisiens-Paris_Il.html"),
    "p1003911": ("3.7", "AttractionProductReview-g187147-d28150848-Seine_River_Evening_Cruise_with_Music_Drink_Options-Paris_Ile_de_France.html"),
    "t409183": ("5.0", "AttractionProductReview-g187147-d23829547-Top_Private_Cruises_in_Paris_with_French_Champagne_and_surprises-Paris_Ile_de_Fran.html"),
    "t374289": ("4.0", "AttractionProductReview-g187147-d19260933-Seine_River_Cruise_French_Crepe_Tasting_by_the_Eiffel_Tower-Paris_Ile_de_France.html"),
    # Dinner (dinner-cruises-paris)
    "p974358": ("4.3", "AttractionProductReview-g187147-d11979678-Bateaux_Parisiens_Seine_River_Gourmet_Dinner_Sightseeing_Cruise-Paris_Ile_de_Franc.html"),
    "p1049009": ("4.6", "AttractionProductReview-g196560-d25267310-Paris_Gourmet_Dinner_Seine_River_Cruise_with_Singer_and_DJ_Set-Boulogne_Billancour.html"),
    # Thames (thames-river-cruises-london)
    "t207834": ("4.9", "AttractionProductReview-g186338-d11450740-Speedboat_Cruise_Tour_Embankment_OR_Westminster_Pier_70_minutes-London_England.html"),
    "t5275": ("4.1", "AttractionProductReview-g186338-d11449152-London_River_Thames_Dinner_Cruise_with_3_Course_Meal-London_England.html"),
    # Amsterdam (canal-cruises-amsterdam)
    "t313498": ("4.9", "AttractionProductReview-g188590-d15209893-Amsterdam_Classic_Saloon_Boat_Cruise_with_Drinks_and_Cheese-Amsterdam_North_Hollan.html"),
    # Buddha Lounge Boat: the 4.7 is the operator's Tripadvisor page; its only product page
    # (d19148521, 4.8 / 11 reviews) is not the rating we show.
    "t116764": ("4.7", "Attraction_Review-g188590-d17810175-Reviews-Buddha_Lounge_Boat-Amsterdam_North_Holland_Province.html"),
}

# The popover appears twice per pick: in the comparison card and in the pick's review section
# further down (details#N-slug > summary.bpa-details-summary). Both are segments here.
SEGMENT = re.compile(r'<div[^>]*class="bpa-card"|<details[^>]*>\s*<summary class="bpa-details-summary"')
BOOKING = re.compile(r'href="(https://www\.(?:getyourguide|tiqets)\.[^"]+)"')
STATIC = re.compile(
    r'<span class="bpa-rev-badge is-static">(<img alt="Tripadvisor".*?'
    r'<span class="bpa-rev-score">([\d.]+)</span>.*?<span class="bpa-rev-count">[^<]*</span>)</span>',
    re.S)
SUB_ID = re.compile(r'tp\.media/r\?[^"]*?sub_id=([A-Za-z0-9_]+)')


def product_id(href):
    href = href.replace("&amp;", "&")
    m = re.search(r"-(p\d{5,})/", href) or re.search(r"-(t\d{3,})/?", href)
    return m.group(1) if m else None


def page_sub_id(html, path):
    m = SUB_ID.search(html)
    if m:
        return m.group(1)
    return re.sub(r"[^a-z0-9]+", "_", path.parent.name.lower()).strip("_")[:28] + "_pop"


def tp_link(sub_id, ta_path):
    u = quote(TA + ta_path, safe="")
    return (f"https://tp.media/r?campaign_id=149&amp;marker=404154&amp;p=4456&amp;sub_id={sub_id}"
            f"&amp;trs=327188&amp;u={u}")


def process(path, apply):
    html = path.read_text(encoding="utf-8")
    starts = [m.start() for m in SEGMENT.finditer(html)] + [len(html)]
    sub_id = page_sub_id(html, path)
    out, last, linked, left = [], 0, [], []
    for s, e in zip(starts, starts[1:]):
        block = html[s:e]
        # the pick's own Tiqets/GYG links (title, button, popover rows) give its product ids
        pids = [p for p in dict.fromkeys(product_id(h) for h in BOOKING.findall(block)) if p]

        def repl(m):
            hit = [p for p in pids if p in TA_LISTINGS and TA_LISTINGS[p][0] == m.group(2)]
            pid = hit[0] if hit else next((p for p in pids if p in TA_LISTINGS), pids[0] if pids else None)
            want = TA_LISTINGS.get(pid)
            if hit:
                linked.append(pid)
                return (f'<a class="bpa-rev-badge is-link" href="{tp_link(sub_id, want[1])}" '
                        f'rel="noopener nofollow sponsored" target="_blank">{m.group(1)}'
                        f'<span class="bpa-rev-go" aria-hidden="true">→</span></a>')
            left.append((pid, m.group(2), "mapped, score differs" if want else "no listing on record"))
            return m.group(0)

        new = STATIC.sub(repl, block)
        out.append(html[last:s] + new)
        last = e
    out.append(html[last:])
    new_html = "".join(out)
    if apply and new_html != html:
        path.write_text(new_html, encoding="utf-8")
    return linked, left


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    total, bad = 0, 0
    for p in card_pages():
        linked, left = process(p, apply=not a.check)
        rel = p.relative_to(ROOT)
        if linked:
            total += len(linked)
            print(f"{'would link' if a.check else 'linked'} {len(linked):2d}  {rel}")
        for pid, score, why in left:
            print(f"   static  {rel}  {pid} Tripadvisor {score}: {why}")
    if a.check and total:
        print(f"{total} Tripadvisor rows have a verified listing but are still static")
        bad = 1
    sys.exit(bad)


if __name__ == "__main__":
    main()
