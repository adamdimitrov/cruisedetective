# Shared rules for every site

Applies to budapestadventures.com, thecruisedetective.com, luxurytraveltester.com,
adventuresinnewyork.com and every future site. A site's own `SITE.md` / `GEMINI.md` /
`PROJECT.md` adds site-specific rules (partners, languages, commissions) and wins
only where it is stricter. Breaking one of these costs money or rankings.

## 1. Nothing goes live without the owner's OK
- Work on a branch cut from `origin/main`. Never commit to `main`, never force-push a
  branch someone else works on.
- Open a PR and stop. **Do not merge, do not deploy to production, do not promote a
  Vercel deployment** unless the owner says so for that PR. Preview deployments are fine.
- One topic per PR (one language per PR for translations). Small, reviewable commits.

## 2. The kit is the single source of shared code
- Never edit `kit/` in a site repo. Change the `site-kit` repo, release it, then run
  `python3 kit/update.py` in each site. CI (`check_kit.py`) fails on a hand-edited `kit/`.
- Site settings (domain, languages, partners, allowed image hosts) live in `site.json`,
  not in code.
- Never re-run an old one-off fix script without reading what it writes: many of them
  rewrite pages to an old state (e.g. `fix_sliders_and_photos.py` re-adds hotlinked photos).

## 3. QC before every PR (CI runs the same)
- `python3 kit/checks/check_all.py` must exit 0. It runs:
  - `check_kit.py` – kit copy untouched, CI file current;
  - the site's `local_checks` from `site.json` (menu/footer/sitemap sync, affiliate rel);
  - `check_lazy_images.py` – every lazy photo has a loader, the first slide is a real photo,
    every image file exists, no photo hotlinked from another site;
  - `check_filters.py` – every filter pill except "All" has `data-group`, only "All" starts active.
  - `check_archive.py` – nothing calls a one-off script in `scripts/archive/` (never run those).
- After changing any page's text (intro, cards, headings, meta description), run
  `python3 scripts/sync_layout.py` before the commit: it rebuilds the menu, footer and the
  site search index (`search/<lang>.json`). Otherwise the CI layout check fails on main and
  the menu search keeps finding the old text.
- Open every new or changed page at phone width (375 px) before the PR: filters grey
  except "All", carousels show photos after a swipe and after an arrow tap, nothing
  sticks out sideways, no console errors.

## 4. Copy
- **No em dashes (—)** anywhere: body, titles, meta, JSON-LD, alt text. Use a comma,
  colon, period or parentheses. En dashes in ranges (10–12) are fine.
- **Never translate brand names** (companies, boats, venues, the site's own name).
- Translate naturally for a native reader. Prices, durations, ratings and review counts
  stay identical to the English source page. Never invent facts.
- "Personally tested" (and its translations) only where the owner really tested it.
- Never narrate what a booking platform showed ("GetYourGuide showed…", "only N spots
  left"). Use a neutral note: "Checked on the booking page on <date>".

## 5. Affiliate links
- Never add, change or remove a booking URL unless the English source page has the same
  one. Keep every affiliate parameter exactly as on the English page; never "clean up"
  query strings. Missing link on a translation: stop and leave a note, never guess a URL.
- Every affiliate/OTA link carries `rel="nofollow sponsored noopener"` (the site's
  affiliate check enforces it). Official ticket sites that pay nothing: `rel="nofollow noopener"`.

## 5b. Listicle cards (river/dinner cruise design)
- Every card has exactly 5 "questions travellers ask", each answered from facts already on
  the page or the live listing. `check_kit.py` fails on any other count.
- The intro follows the river cruise page (best-budapest-river-cruises), two short paragraphs:
  1. Hook: "The right <thing> is the one that fits your <evening/trip>:" then 3-4 kinds of
     evening in the reader's words (bold), the ones another guide covers better linked to it,
     then "This page gets you to that <boat/tour> in under a minute."
  2. Proof: "To make the choice easy, I <rode/booked/tried> N of these M myself" and what all M
     were compared on (the 5-6 things that decide it), "checked on each seller's own page"
     (plus the review count only if it was really counted), then the next step: the finder,
     the filters, or "scroll straight to the ranking".
  No dates in the intro (the "Last updated" pill carries it), no claims the cards don't back.
- Language versions take their cards from the English card data: translate in
  `data/listicles/i18n/<slug>/<lang>.json`, then `python3 scripts/listicle.py build-lang <english-page> <lang>`
  (`missing` lists what is untranslated). Never edit cards on a language page by hand; prices, times,
  photos and booking links always come from English (`urls` in the file only localizes a link target).
  Order of work: harvest what the site already has (`scripts/listicle_harvest.py`), translate the rest
  (`listicle.py translate`, validated), review, port the page design if it is older than English
  (`port_page_i18n.py --listicle-cards`; `build-lang` refuses otherwise), then `build-lang`. Facts come
  from English, never from an old translation.
- Rank tags on photos and booking buttons stay on one line in every language: keep rank tags within
  42 characters (or the English length); `build-lang` and `check_listicle_layout.py` measure it.

## 6. Layout
- Never hand-edit the header, mobile drawer or footer on a page. Edit the language's
  master page, then run the site's layout sync (`scripts/sync_layout.py`).

## 7. Photos
- Only local files (`/assets/...`) or hosts listed in `site.json` `images.allowed_hosts`.
  Never hotlink a photo from someone else's site.
- A card's photos come only from the exact product the card books (its own listing on
  GetYourGuide, Tiqets, TourRadar, Hostelworld, the operator's product page) or are our own.
  Never another tour's photos, never the same operator's other product.
- Image paths are absolute (`/assets/...`), never relative (`assets/...`) and never a
  local machine path (`/Users/...`).
- Card sliders hold 9-10 photos where the listing has them: top up with
  `scripts/photo_topup.py` (new articles: put the whole product gallery in the spec's
  `gallery`). If the listing has fewer, the card stays short and `photo_topup.py skip`
  records why. Keep our own photos.
- Order each slider to sell the card's promise: first photo = the money shot, then the
  story. Drop off-topic shots, menus, maps, text boards and near-duplicates. Pick from the
  contact sheet, never by filename. One photo → no arrows, no pill.
- Replacing an image: new filename, never overwrite an existing asset (1-year cache).

## 8. Caching and infrastructure
- `.js` files and `/assets` are cached for a year: a changed JS file gets a new `?v=` on
  every page that loads it.
- Do not touch `vercel.json`, analytics / tag snippets (GA4, Google tag, Clarity, Meta
  pixel) or anything under `api/` unless the task is exactly that.
- Never put API keys, tokens or passwords in a repo; read them from the environment.
  Internal files (`*.py`, `scripts/`, `kit/`, `site.json`, notes) are listed in
  `.vercelignore` so they never reach the live site.

## 9. Communication
- Objective, direct, candid. No flattery or hype. If a premise, number or plan is wrong,
  say so plainly with the evidence.
