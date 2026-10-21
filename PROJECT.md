# Project: Google Ads Offline Conversion Tracking (Tiqets S2S)

## Commercial Parameters & Unit Economics
- **Partner Account**: `thecruisedetective.com-176436`
- **Bateaux Parisiens Commission Rate**: **41.9%**
- **Basket Unit Economics**:
  - 1 Adult (€18.00): **€7.54** ($8.20) gross profit.
  - 1 Child 4–11 (€9.50): **€3.98** ($4.34) gross profit.
  - Standard Family Basket (2A + 2C = €55.00): **€23.05** ($25.10) gross profit per converted order.
  - Max Allowable CPA at breakeven: **€23.05** ($25.10).
  - Target CPA (for 2.0x+ ROAS): **< €11.50** (< $12.50).

## Architecture
- **Frontend (Webflow / Landing Pages)**: Tracking snippet in `webflow-sync.js` (and included in advertorial HTML/Webflow pages) capturing `gclid` from URL query string into `localStorage` (`cd_gclid`) & 90-day Cookie (`cd_gclid`). Automatically decorates outgoing Tiqets links (`a[href*="tiqets.com"]`) with `tq_campaign`, preserving existing campaign tags and appending `gclid`, `click_id`, and `subid`.
- **Backend (Vercel Serverless Endpoint)**: Vercel Node.js 18+/20+ serverless function at `/api/tiqets-webhook.js`. Listens for Tiqets Partner Portal POST webhooks, parses `tq_campaign` for `gclid` (supporting composite tags `--gclid-<value>`), authenticates with Google Ads REST API v17 via OAuth2 refresh token, and uploads `ClickConversion` to Customer ID `4899321613` under Conversion Action `Tiqets Offline Sale`.
- **Dual Track E2E Test Infra**: Automated test harnesses for both Click ID Capture (JSDOM/browser simulation of `?gclid=test1234` link decoration) and Backend Webhook API (Supertest/dry-run simulation of Tiqets payload & Google Ads `ClickConversion` request validation).

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | URL GCLID Detection | Detect `gclid` parameter from landing page URL | M1 | ORIGINAL_REQUEST §R1 |
| 2 | Dual Persistence | Store `gclid` in `localStorage` (`cd_gclid`) and 90-day cookie (`cd_gclid`) | M1 | ORIGINAL_REQUEST §R1 |
| 3 | Dynamic Link Decoration | Dynamically append `gclid` to outgoing Tiqets links as `tq_campaign` (plus `gclid`, `click_id`, `subid`), preserving existing campaign tags | M1 | ORIGINAL_REQUEST §R1 |
| 4 | Mutation & Shadow DOM Handling | Support dynamic link insertion via `MutationObserver` and Shadow DOM event delegation | M1 | Survey Explorer 1 |
| 5 | Click ID Verification Test | Programmatic test simulating `?gclid=test1234` navigation and asserting link decoration | M1 / M3 | ORIGINAL_REQUEST Acceptance Criteria |
| 6 | Project Scaffolding | Create `package.json`, `vercel.json`, and `.env.example` for Vercel deployment | M2 | Survey Explorer 2 |
| 7 | Webhook Receiver Endpoint | `/api/tiqets-webhook.js` endpoint to receive POST webhooks from Tiqets Partner Portal | M2 | ORIGINAL_REQUEST §R2 |
| 8 | Payload & GCLID Parsing | Parse Tiqets webhook payload (`tq_campaign`, `order_id`, `financials.total_price`, `financials.currency`, `created_at`) and extract `gclid` | M2 | ORIGINAL_REQUEST §R2 |
| 9 | Google Ads API Auth & Upload | Authenticate via OAuth2 and upload `ClickConversion` via Google Ads REST API v17 (`customers/4899321613:uploadClickConversions`) | M2 | ORIGINAL_REQUEST §R2 |
| 10 | Idempotency & Error Handling | Handle missing GCLID (HTTP 200 skipped), order deduplication, and Google Ads API error codes | M2 | Survey Explorer 2 |
| 11 | Conversion Upload Verification Test | Integration test simulating Tiqets webhook payload and asserting Google Ads API request construction | M2 / M3 | ORIGINAL_REQUEST Acceptance Criteria |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M1 | Click ID Capture (Frontend) | Webflow frontend tracking snippet in `webflow-sync.js`, URL gclid detection, dual persistence, link decoration | none | DONE |
| M2 | Webhook Receiver & Google Ads API Upload (Backend) | Project scaffolding (`package.json`, `vercel.json`), Vercel serverless function `/api/tiqets-webhook.js`, Tiqets payload parser, OAuth2 auth, Google Ads API upload | none | DONE |
| M3 | E2E Test Suite & Acceptance Verification | Test harness for Click ID Capture verification test and Conversion Upload verification test (Tiers 1-4 + Tier 5 adversarial) | M1, M2 | DONE |

## Interface Contracts
### Frontend ↔ Tiqets Links
- Query string format: `https://www.tiqets.com/.../?partner=thecruisedetective.com-176436&tq_campaign=<base_tag>--gclid-<gclid_value>&gclid=<gclid_value>`

### Tiqets Webhook ↔ Backend `/api/tiqets-webhook`
- Method: `POST`
- Content-Type: `application/json`
- Header: `X-Tiqets-Signature` (or secret query param / Bearer token)
- Body attributes: `{ "tq_campaign": "adv-tldr--gclid-Cj0KCQ...", "order_id": "TQ-12345", "financials": { "total_price": 75.50, "currency": "EUR" }, "created_at": "2026-08-10T14:35:00Z" }`

### Backend ↔ Google Ads REST API v17
- POST `https://googleads.googleapis.com/v17/customers/4899321613:uploadClickConversions`
- Headers:
  - `Authorization: Bearer <access_token>`
  - `developer-token: WK-A1HREvXxnsvVLsWELNg`
- Body:
  ```json
  {
    "conversions": [
      {
        "gclid": "Cj0KCQ...",
        "conversionAction": "customers/4899321613/conversionActions/<conversion_action_id>",
        "conversionDateTime": "2026-08-10 14:35:00+00:00",
        "conversionValue": 75.50,
        "currencyCode": "EUR",
        "orderId": "TQ-12345"
      }
    ],
    "partialFailure": true
  }
  ```

## Code Layout
- `webflow-sync.js` (Frontend Webflow tracking snippet)
- `package.json` (Project dependencies, Node.js scripts, test scripts)
- `vercel.json` (Vercel deployment configuration)
- `.env.example` (Environment variables template)
- `api/tiqets-webhook.js` (Vercel serverless function webhook endpoint)
- `test/click-id-capture.test.js` (Programmatic unit/integration test for Click ID Capture)
- `test/conversion-upload.test.js` (Integration test for Webhook Receiver & Google Ads API Upload)
