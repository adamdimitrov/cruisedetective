# Project: The Cruise Detective Staging-First Static Architecture Overhaul

## Architecture
- **Staging Isolation**: Dedicated branch `staging/static-overhaul` decoupled from `main`. Zero modifications to live production DNS (`proxy-ssl.linguana.io` / `35.187.176.9`) or live Webflow traffic.
- **Static Delivery & Routing**: Vercel configuration (`vercel.json`) serving static normalized HTML for the 5 core money hubs, executing comprehensive 301 redirects for 27 dead languages, and hosting serverless function `/api/tiqets-webhook.js`.
- **E-Commerce & Tracking Pipeline**: Client-side `webflow-sync.js` (cookie/localStorage capture, 90-day expiry, dynamic Tiqets link decoration with locked partner ID `thecruisedetective.com-176436`, `tq_campaign`, and `gclid`) connected to serverless `/api/tiqets-webhook.js` and cron sync `sync_tiqets_conversions.py` ingesting into Google Data Manager API (`https://datamanager.googleapis.com/v1/events:ingest`).
- **SEO & Information Architecture**: 6 approved languages (`en`, `ja`, `pl`, `ro`, `fr`, `nl`), 0 emoji/encoded anchor tags in headings, clean semantic HTML5 IDs, and canonical tags strictly targeting clean base URLs with 0 fragments.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | Git Branch Isolation | Initialize and switch to `staging/static-overhaul` without touching `main` or production DNS | M1 | Survey (Explorer 1) / R1 |
| 2 | Core Money Hubs Normalization | Normalize and locally store all 5 core money hubs (Seine, Dinner, Amsterdam, Thames, Side-by-Side) | M1 | Survey (Explorer 1) / R1 |
| 3 | Static Vercel Routing | Configure clean rewrite paths in `vercel.json` for all 5 hubs with correct plural slugs | M1 | Survey (Explorer 1) / R1 |
| 4 | Heading Emoji & NBSP Stripping | Remove all Unicode emojis and `\u00a0`/`&nbsp;` from all headings across the 5 money hubs | M2 | Survey (Explorer 2) / R2 |
| 5 | Semantic HTML5 Anchor IDs | Replace auto-generated hex/encoded IDs with clean semantic anchors (`#boat-<slug>`, `#comparison-matrix`) | M2 | Survey (Explorer 2) / R2 |
| 6 | Canonical Tag Strict Enforcement | Enforce self-referencing canonical tags pointing to `https://www.thecruisedetective.com/<slug>` with 0 `#` fragments | M2 | Survey (Explorer 2) / R2 |
| 7 | 6-Language Active Edition Retention | Retain English and the 5 approved high-converting languages (`ja`, `pl`, `ro`, `fr`, `nl`) representing 77 active URLs | M3 | Survey (Explorer 2) / R3 |
| 8 | 27 Dead Languages 301 Redirects | Generate 351 exact 1-to-1 301 redirects in `vercel.json` plus wildcard fallback rules for all 27 dead languages | M3 | Survey (Explorer 2) / R3 |
| 9 | Clean Sitemap Generation | Generate `sitemap.xml` with strictly the 77 active canonical URLs across the 6 approved languages (0 dead languages, 0 anchors) | M3 | Survey (Explorer 2) / R3 |
| 10 | Tiqets Partner Parameter Enforcement | Enforce `partner=thecruisedetective.com-176436` across 100% of outbound Tiqets links on static money hubs | M4 | Survey (Explorer 3) / R4 |
| 11 | Client-Side Click ID Capture & Link Decoration | Standardize `webflow-sync.js` (`getGclid()` string return, `subid`, `tq_campaign`) | M4 | Survey (Explorer 3) / R4 |
| 12 | Backend Google Data Manager Test Mock Alignment | Update test harness mocks (`test/conversion-upload.test.js`, `test/e2e-suite.test.js`) to support Google Data Manager API | M4 | Survey (Explorer 3) / R4 |
| 13 | Landing Pages Test Suite Harmonization | Update `test_landing_pages.py` to differentiate SEO partner ID from paid landing pages | M4 | Survey (Explorer 3) / R4 |
| 14 | Opaque-Box E2E Testing Suite (Tiers 1-4) | Requirements-driven E2E test suite published with `TEST_READY.md` covering all features | E2E Track | Dual Track Protocol |
| 15 | 100% E2E Pass & Staging Preview Verification | Pass 100% of E2E tests, deploy/verify Vercel staging preview URL, and perform Tier 5 hardening | M5 | Final Milestone / Acceptance |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Staging Isolation & Core Money Hubs Pipeline | Branch `staging/static-overhaul`, ingest all 5 hubs, configure `vercel.json` rewrites | none | PLANNED |
| M2 | HCU & Anchor Pollution Elimination | Strip heading emojis/nbsp, enforce clean semantic IDs, enforce 0-fragment canonical tags | M1 | PLANNED |
| M3 | 6-Language Architecture & 301 Pruning | 351+ 301 redirects in `vercel.json`, 27 languages pruned, clean 77-URL `sitemap.xml` | M1 | PLANNED |
| M4 | Tiqets S2S & Conversion Tracking Integrity | Partner ID enforcement, `webflow-sync.js` alignment, Google Data Manager mock sync, test suites pass | M1 | PLANNED |
| E2E | E2E Testing Track | Design and publish opaque-box test runner (Tiers 1-4) and create `TEST_READY.md` | none | PLANNED |
| M5 | Final Integration, 100% E2E Pass & Staging Preview | Run 100% E2E tests, verify Vercel Staging Preview URL, adversarial Tier 5 hardening | M2, M3, M4, E2E | PLANNED |

## Interface Contracts
### `webflow-sync.js` &larr;&rarr; Outbound Tiqets Links
- Function `decorateLink(anchorElement, clickId)`:
  - Input: HTMLAnchorElement with `href` matching `tiqets.com`
  - Output: Enriched URL containing:
    - `partner=thecruisedetective.com-176436` (on SEO static pages)
    - `tq_campaign=<base_tag>--<type>-<value>` (or standalone value)
    - `gclid=<value>` (or `wbraid`/`gbraid`)
    - `click_id=<value>`
    - `subid=<type>:<value>`
  - Hash fragment preservation: strictly preserves any existing `#...` on the original URL without corruption.
- Function `getGclid()`:
  - Returns string click ID value (or `null`) for backwards compatibility with tests and consumers.
- Function `getClickId()`:
  - Returns `{ type: string, value: string }` (or `null`).

### `api/tiqets-webhook.js` &larr;&rarr; Google Data Manager API
- Endpoint: `https://datamanager.googleapis.com/v1/events:ingest`
- Headers:
  - `Content-Type: application/json`
  - `Authorization: Bearer <access_token>`
- Payload:
  - `destination: { account: "4899321613", productDestination: "7715980036" }`
  - `events: [ { eventName: "purchase", eventTime: "<ISO8601>", userData: { clickId: "<gclid>" }, customData: { ... } } ]`
- Response: HTTP 200 `{ status: "success" }`
- Fallback/Error handling: Duplicate conversions handled gracefully with status 200 `{ status: "duplicate_ignored" }`.

### `vercel.json` &larr;&rarr; HTTP Clients & Search Crawlers
- Redirects:
  - Status: HTTP 301 (or 308 permanent redirect).
  - Scope: 351 exact 1-to-1 URLs for 27 dead languages &rarr; corresponding English canonical URLs.
  - Wildcard fallback: `/:lang(ar|bg|ca|cs|da|de|el|es|fa|fi|he|hi|hr|hu|it|ko|no|pt|ru|sk|sr|sv|th|tr|uk|vi|zh)/:slug*` &rarr; `/`.
- Rewrites:
  - Clean mapping for 5 core money hubs:
    - `/seine-river-cruises-paris` &rarr; `/seine-river-cruises-paris/index.html` (or mapped static file)
    - `/dinner-cruises-paris` &rarr; `/dinner-cruises-paris/index.html`
    - `/canal-cruises-amsterdam` &rarr; `/canal-cruises-amsterdam/index.html`
    - `/thames-river-cruises-london` &rarr; `/thames-river-cruises-london/index.html`
    - `/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison` &rarr; `/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/index.html`

## Code Layout
- Root: `/Users/adamdimitrov/Development/cruisedetective/`
- Configuration:
  - `vercel.json` — Vercel static routing, rewrites, headers, and 301 redirects
  - `sitemap.xml` — Canonical sitemap covering 77 active URLs across 6 languages
- Static Money Hubs:
  - `seine-river-cruises-paris/` — Ingested & normalized static HTML/CSS/assets
  - `dinner-cruises-paris/` — Overhauled static HTML incorporating culinary expansion, semantic comparison table, JSON-LD schema
  - `canal-cruises-amsterdam/` — Normalized static HTML/CSS/assets
  - `thames-river-cruises-london/` — Ingested & normalized static HTML/CSS/assets
  - `bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison/` — Ingested & normalized comparison article
- Scripts & Backend:
  - `webflow-sync.js` — Client-side click ID capture and Tiqets link decoration
  - `api/tiqets-webhook.js` — Vercel serverless offline webhook handler
  - `sync_tiqets_conversions.py` — Scheduled order polling & sync script
- Test Suites:
  - `test/` — Unit and integration tests (`click-id-capture.test.js`, `conversion-upload.test.js`, `e2e-suite.test.js`, etc.)
  - `test_landing_pages.py` — Python landing page affiliate link verification
  - `test_e2e_overhaul.py` / `test/e2e-staging-overhaul.test.js` — E2E test suite covering Tiers 1-4
