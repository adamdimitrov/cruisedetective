# Google Ads Offline Conversion Tracking (Tiqets S2S) — Test Infrastructure & Strategy Documentation

## 1. Test Philosophy & Architecture

The testing strategy for the **Google Ads Offline Conversion Tracking (Tiqets S2S)** project follows an **opaque-box, requirement-driven E2E test strategy**. The suite treats system boundaries as strict interfaces defined in `PROJECT.md` and `ORIGINAL_REQUEST.md`, validating behavior against authoritative specifications rather than implementation internals.

Key Principles:
- **Zero-Dependency Core Harness**: Built using Node.js native test runner (`node:test`) and assertion library (`node:assert`).
- **Opaque-Box Verification**: Tests operate against publicly observable entry points:
  - Frontend: URL navigation, DOM link href state, `localStorage`, `document.cookie`, `MutationObserver`, and `ShadowDOM` click events.
  - Backend: HTTP POST webhook invocation to `/api/tiqets-webhook.js`, HTTP status codes, and outbound Google Ads REST API v17 requests.
- **Production Asset Execution**: Frontend tests load `/webflow-sync.js` via `fs.readFileSync` and evaluate it inside JSDOM using `new Function('window', 'document', 'localStorage', 'location', 'MutationObserver', webflowSyncCode)`. Inlined mock functions (such as `runTrackingScript`) are strictly prohibited.
- **Progressive Testability & Isolation**: Every test case sets up its own isolated state, avoids inter-test coupling, cleans up side effects, and operates independently.

---

## 2. Runner Invocation & Test Execution

Tests are executed using standard Node.js test runner commands:

```bash
# Execute entire test suite (all files in test/*.test.js)
npm test

# Unit test suite execution (click ID capture + backend conversion upload)
npm run test:unit

# End-to-End full suite execution
npm run test:e2e

# Direct runner invocation for all test files
node --test --test-concurrency=1 test/*.test.js

# Target specific test files
node --test --test-concurrency=1 test/click-id-capture.test.js
node --test --test-concurrency=1 test/conversion-upload.test.js
node --test --test-concurrency=1 test/e2e-suite.test.js

# Environment fallback runner invocation (when system node path requires Antigravity binary context):
ELECTRON_RUN_AS_NODE=1 /Applications/Antigravity.app/Contents/MacOS/Antigravity --test --test-concurrency=1 test/*.test.js
```

---

## 3. Feature Checklist Mapping (Features 1–11 from `PROJECT.md`)

| Feature ID | Feature Name | Description | Target Milestone | Test Coverage Module |
|------------|--------------|-------------|------------------|----------------------|
| **F1** | URL GCLID Detection | Extract `gclid` query parameter from landing page URL | M1 | `test/click-id-capture.test.js` |
| **F2** | Dual Persistence | Persist `gclid` in `localStorage` (`cd_gclid`) and 90-day cookie (`cd_gclid`) | M1 | `test/click-id-capture.test.js` |
| **F3** | Dynamic Link Decoration | Update outgoing `a[href*="tiqets.com"]` links with `tq_campaign`, `gclid`, `click_id`, `subid` | M1 | `test/click-id-capture.test.js` |
| **F4** | Mutation & Shadow DOM Handling | Intercept dynamic link additions (`MutationObserver`) & Shadow DOM clicks (`composedPath`) | M1 | `test/click-id-capture.test.js` |
| **F5** | Click ID Verification Test | Programmatic test simulating `?gclid=test1234` navigation & link decoration assertions | M1 / M3 | `test/click-id-capture.test.js` |
| **F6** | Project Scaffolding | Manifest (`package.json`), Vercel config (`vercel.json`), `.env.example` setup | M2 | `test/conversion-upload.test.js` |
| **F7** | Webhook Receiver Endpoint | `/api/tiqets-webhook.js` Vercel serverless HTTP POST endpoint receiver | M2 | `test/conversion-upload.test.js` |
| **F8** | Payload & GCLID Parsing | Parse Tiqets webhook payload (`tq_campaign`, `order_id`, `financials`, `created_at`) & extract `gclid` | M2 | `test/conversion-upload.test.js` |
| **F9** | Google Ads API Auth & Upload | Authenticate via OAuth2 and upload `ClickConversion` via Google Ads REST API v17 | M2 | `test/conversion-upload.test.js` |
| **F10** | Idempotency & Error Handling | Handle missing GCLID (HTTP 200 skipped), order deduplication, and Google Ads API error codes | M2 | `test/conversion-upload.test.js` |
| **F11** | Conversion Upload Verification Test | Integration test simulating Tiqets webhook payload and asserting Google Ads API request payload | M2 / M3 | `test/e2e-suite.test.js` |

---

## 4. Test Suite Breakdown & 4-Tier Coverage Methodology

The test suite consists of 21 tests distributed across 3 test files and 4 tiers of coverage:

### Test Suite Structure

1. **`test/click-id-capture.test.js`** (11 tests across 5 describe blocks):
   - **Tier 1 (Happy Path)**:
     - `1.1`: Detect `gclid` from URL, store in `localStorage` (`cd_gclid` + `cd_gclid_exp` ~90-day expiry) and `document.cookie` (`cd_gclid`).
     - `1.2`: Decorate outgoing Tiqets links with `tq_campaign` (`<base>--gclid-<gclid>`), `gclid`, `click_id`, and `subid`.
   - **Tier 2 (Boundary & Edge Cases)**:
     - `2.1`: Idempotency — preserve single `--gclid-` tag across multiple decoration scans.
     - `2.2`: Preserve URL hash fragments (`#reviews`) during link decoration.
     - `2.3`: Non-Tiqets link isolation (`example.com` links remain untouched).
     - `2.4`: Handle empty or whitespace `gclid` parameters gracefully.
     - `2.5`: Clear effective `gclid` when `localStorage` timestamp is expired.
   - **Tier 3 (Cross-Page Persistence)**:
     - `3.1`: Fallback to `localStorage` on subsequent internal navigation without `?gclid` in URL.
     - `3.2`: Fallback to `cookie` and repopulate `localStorage` when `localStorage` is empty.
   - **Tier 4 (Real-World Browser Flow)**:
     - `4.1`: Automatically decorate dynamically inserted Tiqets links via `MutationObserver`.
     - `4.2`: Decorate Tiqets links inside Shadow DOM embeds upon click interaction.

2. **`test/conversion-upload.test.js`** (7 tests):
   - `1`: Valid webhook payload parsing & Google Ads upload request formatting (`ClickConversion` REST v17 body, headers, OAuth token).
   - `2`: Organic (non-GCLID) sale skipping (HTTP 200 skipped response, zero network requests).
   - `3`: HMAC signature validation (valid `X-Tiqets-Signature`, missing signature, invalid signature).
   - `4`: Composite `tq_campaign` regex extraction & direct/fallback GCLID parsing.
   - `5`: Date formatting strictly as `yyyy-mm-dd hh:mm:ss+zz:zz`.
   - `6`: Method validation (HTTP 405 Method Not Allowed for non-POST HTTP methods).
   - `7`: Duplicate order handling (`CLICK_CONVERSION_ALREADY_EXISTS` returns HTTP 200 with `deduplicated: true`).

3. **`test/e2e-suite.test.js`** (3 tests):
   - `Stage 1-4 E2E`: Paid Search Campaign Journey (URL GCLID capture $\rightarrow$ Dual persistence $\rightarrow$ Link decoration $\rightarrow$ Webhook parsing $\rightarrow$ Google Ads REST API upload).
   - `Stage 1-4 E2E`: Organic Non-Ad Journey verification (No GCLID $\rightarrow$ Webhook skipped).
   - `Stage 1-4 E2E`: Idempotent Duplicate Webhook Delivery handling.

---

## 5. Verification & Integrity Standard

To ensure genuine implementation and prevent facade testing:
- Tests **MUST NOT** inline duplicate or mock versions of `webflow-sync.js` tracking logic.
- Tests **MUST** load and execute `/webflow-sync.js` inside JSDOM.
- Mutating `/webflow-sync.js` must produce immediate, observable test failures (`AssertionError`).
