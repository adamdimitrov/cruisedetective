import test, { beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';
import { JSDOM } from 'jsdom';
import handler, { resetCache } from '../api/tiqets-webhook.js';

// Load production webflow-sync.js script
const webflowSyncCode = fs.readFileSync(path.resolve('./webflow-sync.js'), 'utf8');

// Global original fetch & env backup
const originalFetch = globalThis.fetch;
const originalEnv = { ...process.env };

function setupFetchMock(mockImpl) {
  globalThis.fetch = async (url, options = {}) => {
    return mockImpl(String(url), options);
  };
}

function restoreEnvAndFetch() {
  globalThis.fetch = originalFetch;
  process.env = { ...originalEnv };
  resetCache();
}

beforeEach(() => {
  restoreEnvAndFetch();
});

afterEach(() => {
  restoreEnvAndFetch();
});

function createMockReqRes({ method = 'POST', headers = {}, body = null, rawBody = null, query = {} } = {}) {
  const reqHeaders = {};
  for (const [k, v] of Object.entries(headers)) {
    reqHeaders[k.toLowerCase()] = v;
  }
  let bodyBuffer = null;
  if (rawBody !== null) {
    bodyBuffer = Buffer.isBuffer(rawBody) ? rawBody : Buffer.from(rawBody);
  } else if (body !== null) {
    const str = typeof body === 'object' ? JSON.stringify(body) : String(body);
    bodyBuffer = Buffer.from(str);
  } else {
    bodyBuffer = Buffer.from('');
  }

  const req = {
    method,
    headers: reqHeaders,
    query,
    body: body,
    rawBody: bodyBuffer,
    async *[Symbol.asyncIterator]() {
      yield bodyBuffer;
    }
  };

  const res = {
    statusCode: 200,
    headers: {},
    body: null,
    status(code) {
      this.statusCode = code;
      return this;
    },
    setHeader(k, v) {
      this.headers[k.toLowerCase()] = v;
      return this;
    },
    json(data) {
      this.setHeader('content-type', 'application/json');
      this.body = data;
      return this;
    },
    send(data) {
      this.body = data;
      return this;
    }
  };

  return { req, res };
}

// -----------------------------------------------------------------------------
// Helper: Execute Production webflow-sync.js inside JSDOM Environment
// -----------------------------------------------------------------------------
function executeFrontendTracking({ urlStr, linksHtml = '', initialStorage = {}, initialCookie = '' }) {
  const dom = new JSDOM(linksHtml, { url: urlStr });
  const { window } = dom;
  const { document } = window;

  if (initialStorage && typeof initialStorage === 'object') {
    for (const [k, v] of Object.entries(initialStorage)) {
      window.localStorage.setItem(k, v);
    }
  }
  if (initialCookie) {
    document.cookie = initialCookie;
  }

  // Execute production webflow-sync.js script within JSDOM window context
  const runner = new Function('window', 'document', 'localStorage', 'location', 'MutationObserver', webflowSyncCode);
  runner(window, document, window.localStorage, window.location, window.MutationObserver);

  const decoratedLinks = Array.from(document.querySelectorAll('a')).map(link => {
    const rawHref = link.getAttribute('href');
    let u;
    try {
      u = new URL(link.href);
    } catch (e) {
      u = new URL(rawHref, urlStr);
    }
    return {
      originalHref: rawHref,
      href: link.href,
      tq_campaign: u.searchParams.get('tq_campaign'),
      gclid: u.searchParams.get('gclid'),
      click_id: u.searchParams.get('click_id'),
      subid: u.searchParams.get('subid'),
      textContent: link.textContent
    };
  });

  const storageObj = {};
  for (let i = 0; i < window.localStorage.length; i++) {
    const key = window.localStorage.key(i);
    storageObj[key] = window.localStorage.getItem(key);
  }

  return {
    url: urlStr,
    gclid: window.CruiseDetectiveTracking ? window.CruiseDetectiveTracking.getGclid() : null,
    storage: storageObj,
    cookie: document.cookie,
    decoratedLinks,
    window,
    document,
    dom
  };
}

// =============================================================================
// MAIN END-TO-END 6-STAGE LIFECYCLE SIMULATION
// =============================================================================

test('E2E Lifecycle: Full 6-Stage User Click to Google Ads Offline Conversion Upload', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';
  process.env.GOOGLE_ADS_CUSTOMER_ID = '489-932-1613';
  process.env.GOOGLE_ADS_DEVELOPER_TOKEN = 'WK-A1HREvXxnsvVLsWELNg';
  process.env.GOOGLE_ADS_CLIENT_ID = 'test_client_id';
  process.env.GOOGLE_ADS_CLIENT_SECRET = 'test_client_secret';
  process.env.GOOGLE_ADS_REFRESH_TOKEN = 'test_refresh_token';

  const outboundCalls = [];
  setupFetchMock(async (url, options) => {
    outboundCalls.push({ url, options });
    if (url.includes('oauth2.googleapis.com/token')) {
      return { ok: true, status: 200, async json() { return { access_token: 'e2e_mock_access_token_999', expires_in: 3600 }; } };
    }
    if (url.includes('googleAds:searchStream')) {
      return {
        ok: true,
        status: 200,
        async json() {
          return [{ results: [{ conversionAction: { resourceName: 'customers/4899321613/conversionActions/678901234' } }] }];
        }
      };
    }
    if (url.includes('uploadClickConversions')) {
      return {
        ok: true,
        status: 200,
        async json() {
          return {
            results: [{ conversionDateTime: '2026-08-10 14:35:00+00:00' }]
          };
        }
      };
    }
    return { ok: false, status: 404, async json() { return {}; } };
  });

  // STAGE 1: User Click Simulation with ?gclid=test1234 (Evaluates production webflow-sync.js via JSDOM)
  const stage1Url = 'https://thecruisedetective.com/seine-advertorial?gclid=test1234&utm_source=google&utm_medium=cpc';
  const stage1Html = '<a href="https://www.tiqets.com/en/paris-c66746/tickets-p982924/?partner=deals.cruisedetective.com&tq_campaign=adv-tldr">Book Tickets</a>';

  const frontendResult = executeFrontendTracking({
    urlStr: stage1Url,
    linksHtml: stage1Html
  });

  // STAGE 2: Storage Verification (localStorage & 90-day cookie)
  assert.equal(frontendResult.storage['cd_gclid'], 'test1234', 'localStorage must contain cd_gclid=test1234');
  assert.ok(frontendResult.cookie.includes('cd_gclid=test1234'), 'Cookie must contain cd_gclid=test1234');

  // STAGE 3: Outgoing Link Decoration (a[href*="tiqets.com"])
  assert.equal(frontendResult.decoratedLinks.length, 1);
  const decoratedLink = frontendResult.decoratedLinks[0];
  assert.equal(decoratedLink.tq_campaign, 'adv-tldr--gclid-test1234');
  assert.equal(decoratedLink.gclid, 'test1234');
  assert.equal(decoratedLink.click_id, 'test1234');
  assert.equal(decoratedLink.subid, 'test1234');

  // STAGE 4: Tiqets Webhook Trigger Payload Construction
  const webhookPayload = {
    event: 'order.created',
    order_id: 'TQ-E2E-SIM-1001',
    tq_campaign: decoratedLink.tq_campaign,
    financials: {
      total_price: 149.90,
      currency: 'EUR'
    },
    created_at: '2026-08-10T14:35:00Z'
  };

  // STAGE 5: Webhook Receiver HTTP Processing (/api/tiqets-webhook.js)
  const { req, res } = createMockReqRes({ body: webhookPayload });
  await handler(req, res);

  assert.equal(res.statusCode, 200, 'Webhook response status must be 200 OK');
  assert.equal(res.body.success, true, 'Response payload success must be true');
  assert.equal(res.body.order_id, 'TQ-E2E-SIM-1001');
  assert.equal(res.body.gclid, 'test1234');

  // STAGE 6: Google Ads API Payload Construction & REST v17 Upload Validation
  const uploadCall = outboundCalls.find(c => c.url.includes('uploadClickConversions'));
  assert.ok(uploadCall, 'Google Ads REST uploadClickConversions API must be called');

  // Verify headers
  assert.equal(uploadCall.options.headers['Authorization'], 'Bearer e2e_mock_access_token_999');
  assert.equal(uploadCall.options.headers['developer-token'], 'WK-A1HREvXxnsvVLsWELNg');
  assert.equal(uploadCall.options.headers['Content-Type'], 'application/json');

  // Verify payload body schema
  const uploadBody = JSON.parse(uploadCall.options.body);
  assert.equal(uploadBody.customerId, '4899321613');
  assert.equal(uploadBody.partialFailure, true);
  assert.equal(uploadBody.conversions.length, 1);

  const conversion = uploadBody.conversions[0];
  assert.equal(conversion.gclid, 'test1234');
  assert.equal(conversion.conversionAction, 'customers/4899321613/conversionActions/678901234');
  assert.equal(conversion.conversionDateTime, '2026-08-10 14:35:00+00:00');
  assert.equal(conversion.conversionValue, 149.90);
  assert.equal(conversion.currencyCode, 'EUR');
  assert.equal(conversion.orderId, 'TQ-E2E-SIM-1001');

  restoreEnvAndFetch();
});

// =============================================================================
// REAL-WORLD APPLICATION SCENARIOS (Tier 4 Integration Tests)
// =============================================================================

test('Scenario 1: Standard Paid Search Campaign Journey (Paris Seine Cruise)', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';

  const outboundCalls = [];
  setupFetchMock(async (url, options) => {
    outboundCalls.push({ url, options });
    if (url.includes('oauth2.googleapis.com/token')) {
      return { ok: true, status: 200, async json() { return { access_token: 'token_sc1', expires_in: 3600 }; } };
    }
    return { ok: true, status: 200, async json() { return { results: [] }; } };
  });

  // Step 1: User clicks Google Ad for Paris Seine Cruise
  const fe = executeFrontendTracking({
    urlStr: 'https://thecruisedetective.com/seine-advertorial?gclid=Cj0KCQiA_PARIS_SEINE_777',
    linksHtml: '<a href="https://www.tiqets.com/en/paris-c66746/tickets-p982924/?partner=deals.cruisedetective.com&tq_campaign=seine-bm">Book Tickets</a>'
  });

  // Step 2: Sale completed on Tiqets
  const webhookPayload = {
    order_id: 'TQ-PARIS-888',
    tq_campaign: fe.decoratedLinks[0].tq_campaign,
    financials: { total_price: 185.00, currency: 'EUR' },
    created_at: '2026-08-10T16:00:00Z'
  };

  const { req, res } = createMockReqRes({ body: webhookPayload });
  await handler(req, res);

  assert.equal(res.statusCode, 200);
  const uploadCall = outboundCalls.find(c => c.url.includes('uploadClickConversions'));
  const body = JSON.parse(uploadCall.options.body);
  assert.equal(body.conversions[0].gclid, 'Cj0KCQiA_PARIS_SEINE_777');
  assert.equal(body.conversions[0].conversionValue, 185.00);

  restoreEnvAndFetch();
});

test('Scenario 2: Multi-Session Cross-Day Attribution Journey', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';

  const outboundCalls = [];
  setupFetchMock(async (url, options) => {
    outboundCalls.push({ url, options });
    if (url.includes('oauth2.googleapis.com/token')) {
      return { ok: true, status: 200, async json() { return { access_token: 'token_sc2', expires_in: 3600 }; } };
    }
    return { ok: true, status: 200, async json() { return { results: [] }; } };
  });

  // Day 1: Ad Click & storage setup
  const feDay1 = executeFrontendTracking({
    urlStr: 'https://thecruisedetective.com/dinner-advertorial?gclid=Cj0KCQ_MULTISESSION_888',
    linksHtml: '<a href="https://www.tiqets.com/en/paris-c66746/dinner-cruise">Book Dinner</a>'
  });

  // Day 14: Direct return visit (no URL gclid)
  const feDay14 = executeFrontendTracking({
    urlStr: 'https://thecruisedetective.com/dinner-advertorial',
    linksHtml: '<a href="https://www.tiqets.com/en/paris-c66746/dinner-cruise">Book Dinner</a>',
    initialStorage: feDay1.storage,
    initialCookie: feDay1.cookie
  });

  assert.equal(feDay14.gclid, 'Cj0KCQ_MULTISESSION_888', 'Must read stored gclid from cookie/storage');
  assert.equal(feDay14.decoratedLinks[0].gclid, 'Cj0KCQ_MULTISESSION_888');

  // Webhook for purchase 14 days later
  const webhookPayload = {
    order_id: 'TQ-MULTI-14DAYS',
    tq_campaign: feDay14.decoratedLinks[0].tq_campaign,
    financials: { total_price: 210.00, currency: 'EUR' },
    created_at: '2026-08-24T18:30:00Z'
  };

  const { req, res } = createMockReqRes({ body: webhookPayload });
  await handler(req, res);

  assert.equal(res.statusCode, 200);
  const uploadCall = outboundCalls.find(c => c.url.includes('uploadClickConversions'));
  const body = JSON.parse(uploadCall.options.body);
  assert.equal(body.conversions[0].gclid, 'Cj0KCQ_MULTISESSION_888');

  restoreEnvAndFetch();
});

test('Scenario 3: Multi-Currency High-Volume Sales Scenario (USD, EUR, GBP)', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';

  const outboundCalls = [];
  setupFetchMock(async (url, options) => {
    outboundCalls.push({ url, options });
    if (url.includes('oauth2.googleapis.com/token')) {
      return { ok: true, status: 200, async json() { return { access_token: 'token_sc3', expires_in: 3600 }; } };
    }
    return { ok: true, status: 200, async json() { return { results: [] }; } };
  });

  const sales = [
    { orderId: 'TQ-USD-1', gclid: 'Cj0KCQ_USD_1', amount: 120.00, currency: 'USD' },
    { orderId: 'TQ-EUR-2', gclid: 'Cj0KCQ_EUR_2', amount: 95.50, currency: 'EUR' },
    { orderId: 'TQ-GBP-3', gclid: 'Cj0KCQ_GBP_3', amount: 85.00, currency: 'GBP' }
  ];

  for (const sale of sales) {
    const payload = {
      order_id: sale.orderId,
      tq_campaign: `adv-tldr--gclid-${sale.gclid}`,
      financials: { total_price: sale.amount, currency: sale.currency }
    };
    const { req, res } = createMockReqRes({ body: payload });
    await handler(req, res);
    assert.equal(res.statusCode, 200);
  }

  const uploadCalls = outboundCalls.filter(c => c.url.includes('uploadClickConversions'));
  assert.equal(uploadCalls.length, 3);

  assert.equal(JSON.parse(uploadCalls[0].options.body).conversions[0].currencyCode, 'USD');
  assert.equal(JSON.parse(uploadCalls[1].options.body).conversions[0].currencyCode, 'EUR');
  assert.equal(JSON.parse(uploadCalls[2].options.body).conversions[0].currencyCode, 'GBP');

  restoreEnvAndFetch();
});

test('Scenario 4: Transient API Outage & Graceful Webhook Recovery Scenario', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';

  let attempt = 0;
  setupFetchMock(async (url) => {
    if (url.includes('oauth2.googleapis.com/token')) {
      return { ok: true, status: 200, async json() { return { access_token: 'token_sc4', expires_in: 3600 }; } };
    }
    if (url.includes('uploadClickConversions')) {
      attempt++;
      if (attempt === 1) {
        return { ok: false, status: 503, async json() { return { error: 'Service Unavailable' }; } };
      }
      return { ok: true, status: 200, async json() { return { results: [] }; } };
    }
    return { ok: true, status: 200, async json() { return []; } };
  });

  const payload = {
    order_id: 'TQ-RETRY-OUTAGE',
    tq_campaign: 'adv-tldr--gclid-Cj0KCQ_RETRY_OUTAGE',
    financials: { total_price: 130.00, currency: 'EUR' }
  };

  // First attempt fails with 500
  const { req: req1, res: res1 } = createMockReqRes({ body: payload });
  await handler(req1, res1);
  assert.equal(res1.statusCode, 500);

  // Second attempt (Tiqets webhook retry) succeeds with 200
  const { req: req2, res: res2 } = createMockReqRes({ body: payload });
  await handler(req2, res2);
  assert.equal(res2.statusCode, 200);

  restoreEnvAndFetch();
});

test('Scenario 5: Dynamic Webflow Component Embed & Shadow DOM Widget Scenario', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';

  const outboundCalls = [];
  setupFetchMock(async (url, options) => {
    outboundCalls.push({ url, options });
    if (url.includes('oauth2.googleapis.com/token')) {
      return { ok: true, status: 200, async json() { return { access_token: 'token_sc5', expires_in: 3600 }; } };
    }
    return { ok: true, status: 200, async json() { return { results: [] }; } };
  });

  // Simulating link insertion inside DOM widget
  const fe = executeFrontendTracking({
    urlStr: 'https://thecruisedetective.com/bateaux-parisiens-landing?gclid=Cj0KCQ_SHADOW_EMBED_555',
    linksHtml: '<a href="https://www.tiqets.com/en/paris-c66746/bateaux-parisiens-ticket">Book Widget Ticket</a>'
  });

  assert.equal(fe.decoratedLinks[0].tq_campaign, 'Cj0KCQ_SHADOW_EMBED_555');

  // Verify dynamic decoration on newly added elements via scanAndDecorate
  const newLink = fe.document.createElement('a');
  newLink.href = 'https://www.tiqets.com/en/paris-c66746/dynamic-widget-ticket';
  newLink.textContent = 'Dynamic Ticket';
  fe.document.body.appendChild(newLink);

  fe.window.CruiseDetectiveTracking.scanAndDecorate();
  const updatedUrl = new URL(newLink.href);
  assert.equal(updatedUrl.searchParams.get('gclid'), 'Cj0KCQ_SHADOW_EMBED_555');
  assert.equal(updatedUrl.searchParams.get('tq_campaign'), 'Cj0KCQ_SHADOW_EMBED_555');

  const webhookPayload = {
    order_id: 'TQ-SHADOW-100',
    tq_campaign: fe.decoratedLinks[0].tq_campaign,
    financials: { total_price: 79.00, currency: 'EUR' }
  };

  const { req, res } = createMockReqRes({ body: webhookPayload });
  await handler(req, res);

  assert.equal(res.statusCode, 200);
  const uploadCall = outboundCalls.find(c => c.url.includes('uploadClickConversions'));
  const body = JSON.parse(uploadCall.options.body);
  assert.equal(body.conversions[0].gclid, 'Cj0KCQ_SHADOW_EMBED_555');

  restoreEnvAndFetch();
});
