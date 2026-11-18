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
| `checks/check_filters.py` | Filter pills: `data-group` on every non-"All" pill, only "All" active |
| `checks/sitecfg.py`, `checks/kittree.py` | Shared helpers |
| `ci/layout-check.yml` | The CI workflow every site uses |
| `runtime/site-runtime.js` | Shared front-end runtime (sliders, filters, TOC, sticky bar, lazy photos), served as `/js/site-runtime.js?v=<hash>` on sites with `"runtime": {"shared": true}` |
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
| `slider_photo_order.py` | Applies the card photo orders in the site's `scripts/slider_photo_order_data.py` to every language version |
| `fix_affiliate_rel.py` | Every affiliate link carries `rel="nofollow sponsored noopener"`; settings under `affiliate` in site.json |
| `listicle.py` | Listicle cards (`bpa-card`, river/dinner cruise design) as data: `extract <page>` writes `data/listicles/<slug>.json`, `build <page>` renders the cards back into the page (only the card region), `stats <page>` shows structured vs raw. Test: `python3 tests/test_listicle_roundtrip.py --site ../budapest-adventures` (extract -> build must be byte-identical) |

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
