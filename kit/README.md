# site-kit

Shared code, checks and rules for every site: budapestadventures.com,
thecruisedetective.com, luxurytraveltester.com, adventuresinnewyork.com, and
every future site. The shared part of a site lives here and only here.

## How a site uses the kit

```
<site repo>/
  kit/              exact copy of a released kit (never edit by hand)
  kit.lock          version, source commit and fingerprint of that copy
  site.json         this site's settings (below)
  .github/workflows/layout-check.yml   copied from kit/ci/, runs check_all.py
```

Update a site to the latest kit: `python3 kit/update.py` (or `--ref vX.Y.Z`), review
the diff, open a PR. Update several sites from a site-kit checkout:
`python3 update.py --site ../budapest-adventures --site ../cruisedetective ...`.
`update.py` never commits, pushes or deploys.

Change the kit: edit this repo, bump `VERSION`, PR, merge, tag `vX.Y.Z`, then run
`update.py` on every site (one PR per site).

## What is in it

| Path | What |
| --- | --- |
| `RULES.md` | Shared rules for every session on every site |
| `checks/check_all.py` | Runs every check; CI runs exactly this |
| `checks/check_kit.py` | kit/ untouched, CI file current, local checks present |
| `checks/check_lazy_images.py` | Photos: loaders, first slide, missing files, hotlinks (`--fix` upgrades old slider runtimes) |
| `checks/check_archive.py` | Nothing (script, workflow, skill, settings) still calls a script in `scripts/archive/` |
| `checks/check_listicle_layout.py` | Listicle pages measured in a browser at phone and desktop width: rank tags and booking buttons fit on one line (tag not shrunk below 10 px), no sideways overflow. Skipped without Node + Playwright |
| `checks/check_photo_counts.py` | Listicle cards under 9 slider photos without a recorded reason (report only; site.json `photo_topup.strict` makes it fail) |
| `checks/check_gallery_clip.py` | No CSS rule unclips a card photo gallery (.cd-gal, thumbnails, slider) when a popover opens: a `*{overflow:visible}` escape hatch must add `:not(.cd-gal):not(.cd-gal *)` |
| `checks/check_filters.py` | Filter pills: `data-group` on every non-"All" pill, only "All" active |
| `checks/sitecfg.py`, `checks/kittree.py` | Shared helpers |
| `ci/layout-check.yml` | The CI workflow every site uses |
| `runtime/site-runtime.js` | Shared front-end runtime (sliders, filters, TOC, sticky bar, lazy photos), served as `/js/site-runtime.js?v=<hash>` on sites with `"runtime": {"shared": true}` |
| `runtime/listicle/i18n/<lang>.json` | Per-language strings of the listicle design: template strings (`ui`), shared JS strings (`js`, written into language pages as `<script type="application/json" id="listicle-ui">`; English pages have none and keep the English defaults), phrases many cards repeat (`text`) |
| `runtime/listicle/`, `runtime/listicle.py` | Shared listicle card design (river/dinner cruise template): CSS and JS served as `/css/listicle-*.css`, `/js/listicle-*.js?v=<hash>` on the pages listed in site.json `listicle.pages`; `migrate` swaps byte-identical inline copies for the files |
| `runtime/runtime.py` | `migrate`: move a site's pages from their inline runtime to the shared file (only byte-identical copies); `publish`: used by update.py |
| `scripts/*.py` | Shared site scripts (see below) |
| `update.py` | Install / update the kit in a site |

## Starting a new site

`python3 new_site.py --dir ../new-site --name "Rome Adventures" --domain https://www.romeadventures.com
--tagline "..." --email ...` writes a complete starter site into an empty folder (usually the freshly
cloned empty repo): site.json, CLAUDE.md, menu data (`data/menu/en.json`), layout config, starter pages
(home, about, contact, privacy, 404) from `templates/site/`, the shared look (`css/site.css`,
`js/site-chrome.js`, `js/site-search.js`: Budapest Adventures' menu, language switcher, search, footer
and article styles), sitemap, robots, vercel.json; then installs the kit, runs the layout sync and
`check_all.py`, which must pass. It never commits or deploys.

## Shared scripts

The code of a shared script lives in `kit/scripts/<name>.py`. Each site keeps a short stub
at `scripts/<name>.py` that loads the kit copy, so `python3 scripts/<name>.py ...` and
`import <name>` work as before. `update.py` writes the stubs; `check_kit.py` fails when a
stub is missing or edited. A shared script reads the site's root from `checks/sitecfg.py`
(never from its own `__file__`, which points into `kit/`) and its settings from `site.json`.
A site that still needs its own version of a script lists it in `site.json` as
`"own_scripts": ["sync_layout.py"]`; it then gets no stub for it.

| Script | What |
| --- | --- |
| `search_index.py` | Per-language search index (`search/<lang>.json`) for the menu search |
| `menu.py` | The menu as data: `extract` writes each master page's header to `data/menu/<lang>.json` (content as fields, formatting as small `_fmt` hints), `build [--lang xx] [--check]` renders it back into the master (then run `sync_layout.py`); `render_header(menu)` for other kit code. Round-trip test: `tests/test_menu_roundtrip.py` |
| `sync_layout.py` | Header, footer, active menu item and language switcher from the master pages, search index, affiliate rel; settings in the site's `scripts/layout_config.json` |
| `photo_topup.py` | Tops card sliders up to 9-10 photos from the exact product's listing: `scan` (cards under 9), `snippet gyg` (browser JS that reads a GetYourGuide product gallery), `stage` (download, drop duplicates of the card's and the page's other photos, numbered contact sheet), `apply --order E1,C4,...` (new .avif files, slider + thumbnails in that order, page and its language galleries rebuilt), `skip --reason` (why a card stays short) |
| `slider_photo_order.py` | Applies the card photo orders in the site's `scripts/slider_photo_order_data.py` to every language version |
| `fix_affiliate_rel.py` | Every affiliate link carries `rel="nofollow sponsored noopener"`; settings under `affiliate` in site.json |
| `listicle.py` | Listicle cards (`bpa-card`, river/dinner cruise design) as data: `extract <page>` writes `data/listicles/<slug>.json`, `build <page>` renders the cards back into the page (only the card region), `stats <page>` shows structured vs raw. Test: `python3 tests/test_listicle_roundtrip.py --site ../budapest-adventures` (extract -> build must be byte-identical). Language versions: `build-lang <english-page> <lang> [--check]` renders the language page's cards (the page its hreflang link names) from the ENGLISH card data plus `data/listicles/i18n/<slug>/<lang>.json` (text keyed by the English fragment, `urls` for localized links) and the kit table `runtime/listicle/i18n/<lang>.json` (template and JS strings, common phrases); `missing <english-page> <lang> [--todo=FILE] [--prune]` lists what is untranslated. Test: `python3 tests/test_listicle_i18n.py` |
| `listicle_harvest.py` | Reuses translations a language page already has: `<english-page> <lang|all>` aligns the old translated page with the English version it was translated from (found in git history) and reads the port / listicle memories, then adds the pairs whose English is still used by the card data to `data/listicles/i18n/<slug>/<lang>.json` (never overwriting), with provenance and skipped pairs in `<lang>.harvest.json`. See "Listicle language versions" below |

## site.json

```json
{
  "name": "Budapest Adventures",
  "domain": "https://www.budapestadventures.com",
  "languages": ["en", "hu"],
  "images": {
    "allowed_hosts": ["cdn.prod.website-files.com", "www.facebook.com"],
    "data_more_prefix": "/assets/cdn/60e43c7d6d05b671dff0dc1a/"
  },
  "local_checks": ["scripts/sync_layout.py --check", "scripts/fix_affiliate_rel.py --check"],
  "runtime": {"shared": true}
}
```

- `images.allowed_hosts`: the only external hosts a photo may come from (our own CDN,
  partner CDNs, the Meta pixel). Everything else fails as a hotlink.
- `images.data_more_prefix`: folder that bare file names in a carousel's `data-more`
  resolve to (only sites that use `data-more`).
- `runtime.shared`: the site loads `/js/site-runtime.js` instead of inline copies;
  check_kit fails on any page that still carries one or loads an old `?v=`.
- `local_checks`: the site's own checks that `check_all.py` also runs, until they
  move into the kit.

## Listicle language versions

Facts (prices, times, ratings, photos, booking links) always come from the English card data; a
language file only holds text. A new or outdated language version goes through these steps:

1. **Harvest** what the site already has: `python3 scripts/listicle_harvest.py <english-page> all`
   (or one language). It pairs the old translated page with the English version it was made from
   (git history, matched on photos, link targets, structure and numbers), card by card and element
   by element, and reuses the page port memories (`data/i18n/port/*/<lang>.json`) and the other
   listicles' language files. A pair is only kept when its English is still used word for word and
   it passes the guard: same numbers, currency, links and markup as English (else it belongs to an
   older fact), looks translated (not English, right script), no added label or dropped brackets, not
   one translation reused for different English strings. Where each entry came from, and what was
   skipped and why, is in `data/listicles/i18n/<slug>/<lang>.harvest.json`. `--dry-run` writes nothing.
2. **Translate** the rest: `python3 scripts/listicle.py missing <english-page> <lang> --todo=todo.json`, then
   `python3 scripts/listicle.py translate <english-page> <lang> --todo=todo.json`. It sends the strings in
   batches (about 12,000 characters each, `--batch-chars=N`) to the Claude API: model
   `LISTICLE_TRANSLATE_MODEL` (default `claude-opus-5-5`), key `ANTHROPIC_API_KEY` or the site's `.env`.
   The prompt carries the house rules (keep tags, numbers, times, currency, URLs, placeholders, emoji and
   the names of boats, operators and docks; the reader is addressed as on the existing pages; no em
   dashes) and the language's existing translations as a glossary; each string comes with where it sits
   on the card. Every answer goes through `validate()` (same tag sequence and attributes, same digits,
   24-hour times, currency signs, URLs, `{placeholders}` and emoji; not empty, not English, no em dash):
   failures are listed (`--rejects=FILE`) and never written. Written entries are listed in
   `<lang>.translated.json` for the review. `--dry-run` prints the prompt, the batches and the estimated
   tokens; without a key it stops with a message and changes nothing.
3. **Review** the language file (the `.harvest.json` / `.translated.json` side files say what to look at),
   then delete the side files.
4. **Port the page design** if the language page is older than the English one (different filter
   pills, sticky bar, intro): `python3 scripts/port_page_i18n.py <english-page> --langs <lang> --cache-only
   --listicle-cards` (`--dump-todo DIR` lists the page texts still to translate into
   `data/i18n/port/<slug>/<lang>.json`). `build-lang` refuses a page whose filter pills differ from English.
5. **Build**: `python3 scripts/listicle.py build-lang <english-page> <lang>`, then QC as for any page.
   `build-lang` then measures the page in a browser (`checks/check_listicle_layout.py`, phone and desktop):
   a rank tag on a photo or a booking button that does not fit on one line fails it.

**Longer languages (one-line labels).** The rank tag on the photo and the booking button stay on one
line on every page: the CSS keeps them on one line and `listicle-cards.js` shrinks the text a little when
it does not fit (button: tighter padding first, then down to 12 px; tag: down to 9 px; then an ellipsis).
So the text has to be short enough: `validate()` rejects a rank tag over 42 visible characters (or the
English length, if longer), `missing` lists existing ones over the budget (and `translate` redoes them),
and `check_listicle_layout.py` fails a tag shrunk below 10 px, anything cut off, or sideways overflow.
The budgets are in `FIT_BUDGET` in `scripts/listicle.py`.

Tests: `python3 tests/test_listicle_translate.py` (validator, harvest guard, no-key run).

