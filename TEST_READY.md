# E2E Test Suite Ready — Staging Static Architecture Overhaul

## Test Runner
- **Command**: `ELECTRON_RUN_AS_NODE=1 /Applications/Antigravity.app/Contents/MacOS/Antigravity --test test/e2e-staging-overhaul.test.js`
- **Alternative / Standard Node**: `node --test test/e2e-staging-overhaul.test.js`
- **Test File**: `test/e2e-staging-overhaul.test.js`

## Coverage Summary
| Tier | Test Count | Description |
|:---|:---:|:---|
| **Tier 1: Feature Coverage** | 30 | Happy-path tests for Canonical Tags, 5 Core Money Hubs, 301 Redirects in `vercel.json`, 6 Approved Languages Retention, Tiqets Partner Enforcement, and Offline Webhook S2S Ingestion. |
| **Tier 2: Boundary & Corner Cases** | 25 | Boundary edge cases: 0 Unicode emojis in headings, 0 NBSP / `&nbsp;`, HTML5 anchor ID validity, strict canonical URL format, wildcard language fallbacks, and malformed/expired click IDs. |
| **Tier 3: Cross-Feature Combinations** | 5 | Cross-feature interactions: outbound link decoration on localized pages, composite `tq_campaign` vs direct GCLID webhook extraction, Shadow DOM dynamic link decoration, dual storage cross-session synchronization, and Vercel routing precedence. |
| **Tier 4: Real-World Scenarios** | 5 | End-to-end full simulations: Google Ad search journey to Google Data Manager conversion upload, crawler full audit of `sitemap.xml`, organic visitor journey, international traveler legacy 301 redirection, and high-frequency DOM mutation re-rendering. |
| **Total** | **65** | **Comprehensive opaque-box coverage across all features in PROJECT.md** |

## Feature Checklist Matrix
| Feature | Milestone | Tier 1 (>=5) | Tier 2 (>=5) | Tier 3 (>=1) | Tier 4 (>=1) |
|:---|:---:|:---:|:---:|:---:|:---:|
| Canonical Tag Strict Enforcement | M2 | ✓ (5 tests) | ✓ (5 tests) | ✓ | ✓ |
| 5 Core Money Hubs Normalization | M1 | ✓ (5 tests) | ✓ (5 tests) | ✓ | ✓ |
| Static Vercel 301 Routing | M3 | ✓ (5 tests) | ✓ (5 tests) | ✓ | ✓ |
| 6 Approved Languages Retention | M3 | ✓ (5 tests) | ✓ (5 tests) | ✓ | ✓ |
| Tiqets Partner Tracking Enforcement | M4 | ✓ (5 tests) | ✓ (5 tests) | ✓ | ✓ |
| Offline Webhook S2S Pipeline | M4 | ✓ (5 tests) | ✓ (5 tests) | ✓ | ✓ |

## Test Suite Execution Baseline (Current vs Target)
- **Current Execution Status**: **45 / 65 Passing** (69.2% passing on baseline codebase).
- **Target Status (Post M1–M4 Implementation)**: **65 / 65 Passing (100%)**.
- **Pending Implementations Tracked by Failing Tests**:
  - **M1 (5 tests)**: Ingest missing money hubs (`thames-river-cruises-london`, `bateaux-mouches-vs-bateaux-parisiens...`) to local project root.
  - **M2 (2 tests)**: Enforce clean self-referencing canonical tags on `https://www.thecruisedetective.com/<slug>` with 0 fragments.
  - **M3 (11 tests)**: Add 351 exact 301 redirects and wildcard fallbacks to `vercel.json`; generate 77-URL clean `sitemap.xml`.
  - **M4 (2 tests)**: Ensure 100% of outbound Tiqets links in static money hubs use `thecruisedetective.com-176436`.
