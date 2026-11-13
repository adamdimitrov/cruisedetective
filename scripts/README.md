# scripts/

## Daily tools
| Script | What it does | Skill |
|---|---|---|
| `ship/preflight.py [--fix]` | Pre-merge checks: em dashes, JS `?v=` bumps, cache-rule order, sitemap lastmod, affiliate links | `/ship` |
| `qa/mobile_overflow.py [pages…]` | 375px horizontal-overflow check with popovers open | `/mobile-qa` |
| `cards/cards.py extract/drift/links/all` | Card data layer: facts per card, translation drift vs EN, affiliate link rules | `/port-card-feature`, `/verify-ota-facts` |
| `i18n/port.py sync <preset>` | Port EN cards, sections and dinner menus to every translation from the translation memory (`i18n/memory/`); `missing`/`learn` for new strings, `harvest` from already translated pages | `/port-i18n` |
| `preview_server.py [port]` | Local server with Vercel rewrites and cleanUrls | |
| `reauth_google.py ads\|gmail` | Get a fresh Google Ads or Gmail refresh token and write it into `.env` (token never printed) | |
| `generate_sitemap.py` | Rebuild `sitemap.xml` | |
| `gsc_anomaly_monitor.py` | GSC anomaly alerts (launchd `com.adamdimitrov.gsc-monitor`) | |
| `scan_untranslated_content.py` | Find English left on translated pages | |
| `fix_hreflang.py`, `generate_301_redirects.py` | hreflang and redirect maintenance | |
| `duplicate_bof_campaigns.py`, `update_all_comparison_ads.py` | Google Ads campaign tooling | |

## archive/
These are one-off migration scripts (Webflow import, translation rollout, layout overhauls). They are kept for reference only. Their paths assume they ran from `scripts/`, so check before re-running one.

New one-off scripts go in the session scratchpad, not in this folder. A script only lands here once it is reused.
