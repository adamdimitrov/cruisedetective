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

## 6. Layout
- Never hand-edit the header, mobile drawer or footer on a page. Edit the language's
  master page, then run the site's layout sync (`scripts/sync_layout.py`).

## 7. Photos
- Only our own photos (local files) or hosts listed in `site.json` `images.allowed_hosts`.
  Never hotlink a photo from someone else's site, never copy someone else's photos in.
- Image paths are absolute (`/assets/...`), never relative (`assets/...`) and never a
  local machine path (`/Users/...`).
- Carousels: never cap, pad or reorder a product's photos. One photo → no arrows, no pill.
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
