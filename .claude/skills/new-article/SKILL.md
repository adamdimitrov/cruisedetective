---
name: new-article
description: Create a new comparison article on thecruisedetective.com in one loop - topic gate, live-listing research, draft from the article template, fix until scripts/qa/article_lint.py and the ship checks pass, then stop at a preview link for approval. Use when the user says write an article about X, new article, új cikk, or picks a topic for a new page. New articles only, not refreshes of existing pages.
---

# /new-article

The pipeline behind `/private-cruises-paris`, made repeatable. The value of these articles is a logistical comparison nobody else lays out side by side, built from verified live-listing facts. It is not volume. One good article beats five thin ones, and scaled near-duplicates are what Google's spam policies penalise.

The loop runs on its own through step 5 and **stops at the preview link**. Nothing merges, publishes or gets submitted to Google until the user approves.

## 0. Worktree
Global rule: `EnterWorktree` first if you are in the main checkout. Branch name `article/<slug>`.

## 1. Topic gate (before any drafting)
Answer these in 3-6 lines to the user. If any is "no", stop and say why, or suggest a section on an existing page instead.

- **Distinct products.** List the bookable products on GetYourGuide and Tiqets (Tiqets first where it sells them). There is no minimum count. The question is whether they differ enough (price, duration, what is included, pier or pickup, group size, timing) or are popular enough that comparing them helps someone choose. Five near-identical listings fail. Three really different ones pass.
- **Not already covered.** No existing page on this site answers the same search (`grep -ril "<topic words>" */index.html`, plus `search/en.json`). Overlap means a section or a filter on that page, not a new URL.
- **Room on page 1.** Look at the top Google results in the user's Chrome. If one already has a good side-by-side comparison with current prices, this article has to beat it on facts or logistics, or it does not get written.
- **Bookable.** Affiliate-only: GetYourGuide or Tiqets links (Captain Jack Amsterdam = FareHarbor ASN). Viator only as a review badge. No product we can't link with a partner tag goes on as a card.

## 2. Research (live listings, user's Chrome, never the built-in browser)
Follow `/verify-ota-facts` section 2 for every product: adult price at a normal date, kids price, rating and review count per site (weighted rating), duration, pier or pickup, time type, languages, what is included, cancellation. Record the check date.

Then collect the **logistics that make the comparison**, the part other sites skip. Pick what fits the topic, for example:
- time actually spent at the destination vs on the road (day trips, bus tours)
- price per hour, price per person at the minimum group size
- start point and how to get there, last return time
- max group size, private vs shared, kids policy
- which products overlap (same boat or operator sold twice) and which to skip

Photos: 5-8 of the best listing photos per product, saved as AVIF in `assets/<slug>/` with descriptive filenames. Never hotlink.

## 3. Draft from the template
Copy the structure of `private-cruises-paris/index.html` (the newest article, already in the layout master system):
- H1 with the current year, intro callout as one sentence, quick picks
- `div.bpa-card` comparison cards (same markup, so `scripts/cards/cards.py` can read them), ranked, each with a Pick/Skip line
- filters for the real decision axes from step 2
- buyer's guide: is it worth it, logistics table, best time, FAQ, **methodology** (what was compared, from which listings, on which date)
- JSON-LD: Article (with `datePublished` and `dateModified`), BreadcrumbList, ItemList, FAQPage

Honesty rules:
- "Personally tested" or "tested" only where the user really did it (Seine, dinner and so on). Comparison-only articles say "Compared on <date> using live listings" in the methodology and byline area. No invented experiences, quotes or photos.
- No em dashes anywhere. Brand, ship and operator names stay in their original form.
- Prices and ratings only from step 2. Unknown facts get left out, not guessed.

Wiring:
- `sitemap.xml` entry (with `en` + `x-default` hreflang), `vercel.json` rewrite like the other articles
- `python3 scripts/sync_layout.py` for menu, footer and the search index
- contextual links **from at least 2 related existing pages** (in body copy, not only menu or footer) and from the new page out to the related money pages

## 4. Fix-until-green loop
Run all of these. Fix every ✗, then run them all again. Repeat until clean. Don't ask the user about anything a check can settle.

```bash
python3 scripts/qa/article_lint.py <slug>       # meta, wiring, em dashes, JSON-LD, images, links
python3 scripts/cards/cards.py links <slug>     # card affiliate rules
python3 scripts/ship/preflight.py --fix         # diff-level ship checks + sitemap lastmod
python3 scripts/sync_layout.py --check          # layout drift
python3 scripts/qa/mobile_overflow.py <slug>    # 375px, all popovers open
```
⚠ warnings (meta description length, outbound source hosts) get a look. Fix them when it is cheap. They don't block.

If the same ✗ survives 3 rounds, stop and tell the user what is stuck instead of looping.

## 5. Stop: preview for approval
Commit (`article: <title>`), push the branch, wait for the Vercel preview, and give the user:
- the preview URL of the article (always, see memory),
- a short table: product, price, rating, check date, source,
- what the gate said in step 1, and anything you could not verify.

**Wait here.** Changes the user asks for go into the same branch, then back to step 4.

## 6. After approval
`/ship` (PR, merge, Search Console indexing). Translations come later via `/port-i18n`, only when the user asks. New pages are EN-first.
