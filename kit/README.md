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
| `checks/check_filters.py` | Filter pills: `data-group` on every non-"All" pill, only "All" active |
| `checks/sitecfg.py`, `checks/kittree.py` | Shared helpers |
| `ci/layout-check.yml` | The CI workflow every site uses |
| `runtime/site-runtime.js` | Shared front-end runtime (sliders, filters, TOC, sticky bar, lazy photos), served as `/js/site-runtime.js?v=<hash>` on sites with `"runtime": {"shared": true}` |
| `runtime/runtime.py` | `migrate`: move a site's pages from their inline runtime to the shared file (only byte-identical copies); `publish`: used by update.py |
| `update.py` | Install / update the kit in a site |

Coming in later phases (see the plan): the shared site scripts (layout sync, sitemap,
affiliate rel, article builder), `templates/`, `new_site.py`.

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
