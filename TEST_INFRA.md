# The Cruise Detective Staging-First Static Architecture Overhaul — Test Infrastructure & Strategy Documentation

## 1. Test Philosophy & Architecture

The testing strategy for **The Cruise Detective Staging-First Static Architecture Overhaul** follows a strict **opaque-box, requirement-driven E2E methodology**. System boundaries are treated as strict interface contracts defined in `PROJECT.md` and `ORIGINAL_REQUEST.md`, validating behavior against authoritative specifications rather than implementation internals.

### Core Principles
- **Native Zero-Dependency Test Harness**: Built using Node.js native test runner (`node:test`) and assertion library (`node:assert/strict`), executable with Node.js v24+ via the Antigravity runtime binary.
- **Production Asset Execution**: Evaluates production assets (`webflow-sync.js`, `api/tiqets-webhook.js`, `vercel.json`, `sitemap.xml`, and normalized money hub HTML templates) in realistic headless runtime environments (JSDOM with simulated DOM, cookies, `localStorage`, `MutationObserver`, and `ShadowDOM`). Inlined duplicate mocks or facade stubs are strictly forbidden.
- **Opaque-Box Boundary Testing**: Operates against publicly observable entry points:
  - **HTTP Crawlers & Routing**: Routing simulation for 351 exact 301 redirects, wildcard dead language fallbacks, and static rewrites in `vercel.json`.
  - **SEO & Canonical Integrity**: Verification of `<link rel="canonical">` URLs, 0 `#` fragment anchors, 0 heading Unicode emojis, and 0 non-breaking spaces.
  - **Affiliate & S2S Tracking**: Locked partner ID `thecruisedetective.com-176436`, contextual `tq_campaign` parameters, dynamic GCLID link decoration, HMAC webhook verification, and outbound Google Data Manager API v1 payload ingestion.
- **Progressive Testability & Isolation**: Tests set up their own isolated state, avoid order-dependent coupling, clean up side effects, and operate independently.

---

## 2. Runner Invocation & Test Execution

The E2E test suite is executed natively via:

```bash
# Primary E2E Test Suite Invocation (Antigravity Runtime)
ELECTRON_RUN_AS_NODE=1 /Applications/Antigravity.app/Contents/MacOS/Antigravity --test test/e2e-staging-overhaul.test.js

# Parallel execution with other test modules
ELECTRON_RUN_AS_NODE=1 /Applications/Antigravity.app/Contents/MacOS/Antigravity --test test/e2e-staging-overhaul.test.js test/click-id-capture.test.js test/conversion-upload.test.js

# Standard node invocation (when Node >= 18 is in PATH)
node --test test/e2e-staging-overhaul.test.js
```

---

## 3. Feature Checklist Mapping (Features 1–15 from `PROJECT.md`)

| Feature ID | Feature Name | Milestone | Scope | Test Coverage in `test/e2e-staging-overhaul.test.js` |
|:---|:---|:---:|:---|:---|
| **F1** | Git Branch Isolation | M1 | `staging/static-overhaul` decoupled from `main` | Verified via non-production DNS isolation assertions |
| **F2** | Core Money Hubs Normalization | M1 | 5 hubs locally ingested & normalized | Tier 1 (1.2.1–1.2.5), Tier 2 (2.1.1–2.1.5, 2.2.1–2.2.5) |
| **F3** | Static Vercel Routing | M1 | Clean rewrite rules in `vercel.json` | Tier 1 (1.3.1–1.3.5), Tier 3 (3.5), Tier 4 (4.4) |
| **F4** | Heading Emoji & NBSP Stripping | M2 | Strip emojis & `\u00a0`/`&nbsp;` from headings | Tier 2 (2.1.1–2.1.5) |
| **F5** | Semantic HTML5 Anchor IDs | M2 | Clean semantic IDs (`#boat-<slug>`) | Tier 2 (2.2.1–2.2.5) |
| **F6** | Canonical Tag Strict Enforcement | M2 | 0-fragment canonical tags to `thecruisedetective.com` | Tier 1 (1.1.1–1.1.5), Tier 2 (2.3.1–2.3.5) |
| **F7** | 6-Language Active Edition Retention | M3 | Retain `en`, `ja`, `pl`, `ro`, `fr`, `nl` | Tier 1 (1.4.1–1.4.5), Tier 4 (4.2) |
| **F8** | 27 Dead Languages 301 Redirects | M3 | 351 exact 301 redirects + wildcard fallbacks | Tier 1 (1.3.1–1.3.5), Tier 2 (2.4.1–2.4.5), Tier 4 (4.4) |
| **F9** | Clean Sitemap Generation | M3 | Strictly 77 active canonical URLs in `sitemap.xml` | Tier 1 (1.4.3–1.4.5), Tier 4 (4.2) |
| **F10** | Tiqets Partner Parameter Enforcement | M4 | Locked `thecruisedetective.com-176436` | Tier 1 (1.5.1–1.5.5), Tier 3 (3.1), Tier 4 (4.1) |
| **F11** | Client-Side Click ID Capture | M4 | Standardize `webflow-sync.js` (`getGclid`, `subid`) | Tier 2 (2.5.1–2.5.5), Tier 3 (3.1, 3.4), Tier 4 (4.1, 4.5) |
| **F12** | Google Data Manager Mock Alignment | M4 | S2S ingest to `datamanager.googleapis.com` | Tier 1 (1.6.1, 1.6.5), Tier 4 (4.1) |
| **F13** | Landing Pages Harmonization | M4 | Partition SEO partner ID from paid landing pages | Tier 1 (1.5.4) |
| **F14** | Opaque-Box E2E Testing Suite | E2E | 4-Tier requirement-driven verification | Fully implemented in `test/e2e-staging-overhaul.test.js` |
| **F15** | 100% E2E Pass & Staging Preview | M5 | Full pass and live preview verification | Final integration target across all 65 tests |

---

## 4. 4-Tier Test Suite Breakdown (65 Tests Total)

### Tier 1: Feature Coverage (30 Tests across 6 Features)
1. **Canonical Tag Strict Enforcement (5 Tests)**:
   - `1.1.1`: Canonical tag existence across all 5 money hubs.
   - `1.1.2`: Absolute HTTPS URLs targeting `https://www.thecruisedetective.com/`.
   - `1.1.3`: Strictly zero `#` fragment characters in canonical hrefs.
   - `1.1.4`: Normalized plural canonical slugs matching `PROJECT.md` interface contract.
   - `1.1.5`: Self-referencing canonical structure on localized approved editions (`/fr/`, `/nl/`, etc.).
2. **5 Core Money Hubs Normalization (5 Tests)**:
   - `1.2.1`: Local storage of all 5 core money hubs in project root.
   - `1.2.2`: Valid semantic HTML5 document skeleton in all money hubs.
   - `1.2.3`: Responsive comparison elements (table or matrix) present in each hub.
   - `1.2.4`: Strict heading hierarchy with exactly 1 `<h1>` per page.
   - `1.2.5`: Accessible primary CTA buttons linking to approved affiliate targets.
3. **301 Redirect Rules in `vercel.json` (5 Tests)**:
   - `1.3.1`: Redirects array in `vercel.json` with permanent redirect status.
   - `1.3.2`: 301 redirects for sample URLs across European, Asian, and Middle-East dead languages.
   - `1.3.3`: Redirect destinations contain no fragment hashes or dead parameters.
   - `1.3.4`: 301 redirects for legacy singular and alternative slugs.
   - `1.3.5`: Wildcard fallback redirect rule for all 27 dead language prefixes.
4. **6 Approved Languages Retention (5 Tests)**:
   - `1.4.1`: Exactly the 6 approved high-converting languages (`en`, `ja`, `pl`, `ro`, `fr`, `nl`).
   - `1.4.2`: Approved languages not caught by dead language redirect rules.
   - `1.4.3`: `sitemap.xml` contains strictly 77 active canonical URLs.
   - `1.4.4`: Sitemap `hreflang` links only reference approved languages and `x-default`.
   - `1.4.5`: Zero dead languages in sitemap.xml `<loc>` entries.
5. **Tiqets Partner Parameter Enforcement (5 Tests)**:
   - `1.5.1`: Enforce `partner=thecruisedetective.com-176436` on 100% of outbound Tiqets links.
   - `1.5.2`: `ratings.json` uses the locked partner ID for all Tiqets URLs.
   - `1.5.3`: Preserve or attach `tq_campaign` parameters to all Tiqets links.
   - `1.5.4`: Non-Tiqets affiliate links (e.g. GetYourGuide) retain their own partner IDs intact.
   - `1.5.5`: Enforce `target="_blank"` and `rel="noopener"` on all outbound affiliate links.
6. **Offline Webhook Ingestion & S2S Pipeline (5 Tests)**:
   - `1.6.1`: Valid POST webhook with HMAC signature returns HTTP 200.
   - `1.6.2`: Reject webhook request with invalid or missing signature with HTTP 401.
   - `1.6.3`: Gracefully skip organic sale payloads with HTTP 200 `{ status: "skipped" }`.
   - `1.6.4`: Reject non-POST HTTP methods with HTTP 405 Method Not Allowed.
   - `1.6.5`: Google Data Manager payload formatting matching destinations and events contract.

### Tier 2: Boundary & Corner Cases (25 Tests across 5 Features)
1. **Headings: 0 Unicode Emojis and 0 NBSP (5 Tests)**:
   - `2.1.1`: Zero high-surrogate emojis in headings.
   - `2.1.2`: Zero literal non-breaking spaces (`\u00a0`) in headings.
   - `2.1.3`: Zero raw `&nbsp;` HTML entities in headings.
   - `2.1.4`: Valid UTF-8 encoding without mojibake on French accented characters.
   - `2.1.5`: Nested headings in comparison cards maintain zero emojis.
2. **Anchor IDs: HTML5 Validity & Hex/NBSP Elimination (5 Tests)**:
   - `2.2.1`: Zero hex-encoded emoji sequences in IDs (`%F0%9F...`).
   - `2.2.2`: Zero occurrences of `cruisenbspwith` or `nbsp` in anchor IDs.
   - `2.2.3`: HTML5 ID syntax compliance (no whitespace, non-empty).
   - `2.2.4`: In-page table of contents anchors match existing element IDs.
   - `2.2.5`: Semantic naming conventions (`#boat-<slug>` or `#<slug>`).
3. **Canonical URLs: Strict Format & Dirty Pattern Rejection (5 Tests)**:
   - `2.3.1`: Reject any canonical tag containing `#` fragments.
   - `2.3.2`: Reject query parameters in canonical tags.
   - `2.3.3`: Reject insecure `http://` protocol in canonical tags.
   - `2.3.4`: Reject unauthorized domains/subdomains (`deals.`, `vercel.app`).
   - `2.3.5`: Reject trailing slashes on article canonical paths.
4. **Wildcard Language Fallback Routing (5 Tests)**:
   - `2.4.1`: Redirect deep unmapped German paths (`/de/a/b/c`) to root `/`.
   - `2.4.2`: Redirect deep unmapped Spanish paths (`/es/...`) to root `/`.
   - `2.4.3`: Redirect bare dead language root paths (`/it` or `/it/`) to root `/`.
   - `2.4.4`: Approved language paths not redirected to root `/`.
   - `2.4.5`: Obscure dead languages (`/fa/`, `/he/`, `/hi/`, `/vi/`) redirect to `/`.
5. **Malformed Click IDs & Special Characters in GCLID Handling (5 Tests)**:
   - `2.5.1`: Safely sanitize XSS / HTML injection in `gclid` parameter.
   - `2.5.2`: Safely handle extremely long click IDs (500+ characters).
   - `2.5.3`: Cleanly decode and handle URL-encoded characters in `gclid`.
   - `2.5.4`: Ignore empty or whitespace-only `gclid` parameters.
   - `2.5.5`: Clear stored click ID when `cd_gclid_exp` timestamp is expired.

### Tier 3: Cross-Feature Combinations (5 Tests)
- `3.1`: Outbound link decoration with locked partner ID and GCLID on approved localized pages.
- `3.2`: Webhook parsing of composite `tq_campaign` (`table-paris-bm--gclid-...`) vs direct `gclid`.
- `3.3`: Dynamic link decoration inside Shadow DOM embeds upon click interaction.
- `3.4`: Cross-session synchronization via dual storage (`localStorage` + cookie fallback).
- `3.5`: Vercel routing precedence: 301 redirects execute before static rewrites.

### Tier 4: Real-World Scenarios (5 Tests)
- `4.1`: **Scenario 1 — Full Paid Search Lifecycle**: Google Ad arrival with GCLID -> Dual persistence -> CTA click decoration -> Webhook delivery -> Google Data Manager ingestion.
- `4.2`: **Scenario 2 — Search Engine Crawler Audit**: Sitemap loading -> 77 active canonical URLs -> 0 dead languages -> 0 fragment URLs.
- `4.3`: **Scenario 3 — Organic Visitor Journey**: No GCLID arrival -> Clean affiliate click with partner ID -> Webhook skipped response.
- `4.4`: **Scenario 4 — International Traveler Redirection**: Legacy translated URLs in dead languages 301-redirect to canonical English money hubs.
- `4.5`: **Scenario 5 — High-Frequency Filter Mutation**: Dynamic injection of 20+ comparison cards batch-decorated with partner ID and GCLID.

---

## 5. Current Test Execution Baseline & Escalation Breakdown

### Baseline Run Results
- **Command**: `ELECTRON_RUN_AS_NODE=1 /Applications/Antigravity.app/Contents/MacOS/Antigravity --test test/e2e-staging-overhaul.test.js`
- **Total Tests**: **65 tests** across 16 suites
- **Passed**: **45 passed** (69.2%)
- **Failed**: **20 failed** (30.8%)

### Root Cause Analysis of Pending Test Failures
All 20 failing tests are genuine implementation deficits awaiting milestone execution:

1. **Milestone M1 Pending (5 Failures)**:
   - Tests `1.2.1` and `1.1.1`: Local directories and `index.html` for `thames-river-cruises-london` and `bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison` are not yet created in the project root.
2. **Milestone M2 Pending (2 Failures)**:
   - Tests `1.1.2` and `1.1.4`: Existing un-migrated comparison files (`seine-comparison`, `amsterdam-comparison`) currently point their canonical tags to `deals.thecruisedetective.com` instead of `https://www.thecruisedetective.com/<slug>`.
3. **Milestone M3 Pending (11 Failures)**:
   - Tests `1.3.1`, `1.3.2`, `1.3.4`, `1.3.5`, `2.4.1`, `2.4.2`, `2.4.3`, `2.4.5`, `3.5`, `4.4`: `vercel.json` does not yet contain the `"redirects"` array mapping the 27 dead languages (351 URLs) and wildcard fallback rules.
   - Tests `1.4.3`, `1.4.4`, `1.4.5`, `4.2`: `sitemap.xml` does not yet exist at the project root with the 77 active canonical URLs.
4. **Milestone M4 Pending (2 Failures)**:
   - Test `1.5.1`: `seine-comparison/index.html` currently contains affiliate links hardcoded with `deals.cruisedetective.com` instead of `thecruisedetective.com-176436`.

---

## 6. Verification & Integrity Standard

- **No Facade Testing**: Every assertion directly inspects filesystem contents, actual DOM nodes, HTTP status codes, or payload objects.
- **Progressive Milestone Completion Target**: As Workers M1, M2, M3, and M4 complete their deliverables, the pass rate will advance from 45/65 to 65/65 (100%).
