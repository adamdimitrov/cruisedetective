import test, { beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import handler, { resetCache, verifyTiqetsSignature, extractGclid, formatGoogleAdsDateTime } from '../api/tiqets-webhook.js';

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
// Milestone 2 Integration Tests (node:test + node:assert)
// -----------------------------------------------------------------------------

test('1. Valid webhook payload parsing & Google Ads upload request format', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';
  process.env.GOOGLE_ADS_CUSTOMER_ID = '489-932-1613';
  process.env.GOOGLE_ADS_DEVELOPER_TOKEN = 'WK-A1HREvXxnsvVLsWELNg';
  process.env.GOOGLE_ADS_CLIENT_ID = 'test_client_id';
  process.env.GOOGLE_ADS_CLIENT_SECRET = 'test_client_secret';
  process.env.GOOGLE_ADS_REFRESH_TOKEN = 'test_refresh_token';

  const calls = [];
  setupFetchMock(async (url, options) => {
    calls.push({ url, options });
    if (url.includes('oauth2.googleapis.com/token')) {
      return {
        ok: true,
        status: 200,
        async json() { return { access_token: 'mock_access_token_123', expires_in: 3600 }; },
        async text() { return ''; }
      };
    }
    if (url.includes('googleAds:searchStream')) {
      return {
        ok: true,
        status: 200,
        async json() {
          return [{ results: [{ conversionAction: { resourceName: 'customers/4899321613/conversionActions/678901234' } }] }];
        },
        async text() { return ''; }
      };
    }
    if (url.includes('uploadClickConversions')) {
      return {
        ok: true,
        status: 200,
        async json() { return { results: [{ conversionDateTime: '2026-08-10 14:30:00+00:00' }] }; },
        async text() { return ''; }
      };
    }
    return { ok: false, status: 404, async json() { return {}; }, async text() { return 'not found'; } };
  });

  const payload = {
    order_id: 'TQ-1001',
    tq_campaign: 'adv-tldr--gclid-Cj0KCQ12345',
    financials: { total_price: 89.50, currency: 'EUR' },
    created_at: '2026-08-10T14:30:00Z'
  };

  const { req, res } = createMockReqRes({ body: payload });
  await handler(req, res);

  assert.equal(res.statusCode, 200);
  assert.equal(res.body.success, true);
  assert.equal(res.body.order_id, 'TQ-1001');
  assert.equal(res.body.gclid, 'Cj0KCQ12345');

  // Verify Google Ads upload call details
  const uploadCall = calls.find(c => c.url.includes('uploadClickConversions'));
  assert.ok(uploadCall, 'uploadClickConversions endpoint must be invoked');
  assert.equal(uploadCall.options.headers['Authorization'], 'Bearer mock_access_token_123');
  assert.equal(uploadCall.options.headers['developer-token'], 'WK-A1HREvXxnsvVLsWELNg');

  const uploadBody = JSON.parse(uploadCall.options.body);
  assert.equal(uploadBody.customerId, '4899321613');
  assert.equal(uploadBody.conversions[0].gclid, 'Cj0KCQ12345');
  assert.equal(uploadBody.conversions[0].conversionValue, 89.50);
  assert.equal(uploadBody.conversions[0].currencyCode, 'EUR');
  assert.equal(uploadBody.conversions[0].conversionDateTime, '2026-08-10 14:30:00+00:00');
  assert.equal(uploadBody.conversions[0].orderId, 'TQ-1001');

  restoreEnvAndFetch();
});

test('2. Organic (non-GCLID) sale skipping (returns 200 skipped)', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';

  let fetchCalled = false;
  setupFetchMock(async () => {
    fetchCalled = true;
    return { ok: true, status: 200, async json() { return {}; } };
  });

  const payload = {
    order_id: 'TQ-ORGANIC-100',
    tq_campaign: 'organic-search-campaign',
    financials: { total_price: 60.0, currency: 'EUR' }
  };

  const { req, res } = createMockReqRes({ body: payload });
  await handler(req, res);

  assert.equal(res.statusCode, 200);
  assert.equal(res.body.status, 'skipped');
  assert.equal(res.body.reason, 'no_gclid_found');
  assert.equal(fetchCalled, false, 'Zero network requests should be dispatched for organic sales');

  // Test organic composite tag (e.g. adv-tldr--gclid-organic)
  fetchCalled = false;
  const organicCompositePayload = {
    order_id: 'TQ-ORGANIC-COMPOSITE-101',
    tq_campaign: 'adv-tldr--gclid-organic',
    financials: { total_price: 50.0, currency: 'EUR' }
  };
  const { req: req2, res: res2 } = createMockReqRes({ body: organicCompositePayload });
  await handler(req2, res2);

  assert.equal(res2.statusCode, 200);
  assert.equal(res2.body.status, 'skipped');
  assert.equal(res2.body.reason, 'no_gclid_found');
  assert.equal(fetchCalled, false, 'Zero network requests should be dispatched for organic composite sales');

  restoreEnvAndFetch();
});

test('3. HMAC signature validation (valid, missing, invalid)', async () => {
  restoreEnvAndFetch();
  process.env.TIQETS_WEBHOOK_SECRET = 'my_super_secret_key';

  const payload = {
    order_id: 'TQ-HMAC-2002',
    tq_campaign: 'adv-tldr--gclid-Cj0KCQ_HMAC_TEST_12345',
    financials: { total_price: 100.0, currency: 'EUR' }
  };

  // Test missing signature header
  const { req: req1, res: res1 } = createMockReqRes({ body: payload, headers: {} });
  await handler(req1, res1);
  assert.equal(res1.statusCode, 401);
  assert.equal(res1.body.error, 'invalid_signature');

  // Test invalid signature header
  const { req: req2, res: res2 } = createMockReqRes({
    body: payload,
    headers: { 'X-Tiqets-Signature': 'invalid_signature_hash' }
  });
  await handler(req2, res2);
  assert.equal(res2.statusCode, 401);
  assert.equal(res2.body.error, 'invalid_signature');

  // Test valid signature header
  const rawBodyStr = JSON.stringify(payload);
  const validSig = crypto.createHmac('sha256', 'my_super_secret_key').update(rawBodyStr).digest('hex');
  const { req: req3, res: res3 } = createMockReqRes({
    body: payload,
    rawBody: rawBodyStr,
    headers: { 'X-Tiqets-Signature': `sha256=${validSig}` }
  });

  setupFetchMock(async (url) => {
    if (url.includes('oauth2.googleapis.com/token')) {
      return { ok: true, status: 200, async json() { return { access_token: 'token', expires_in: 3600 }; } };
    }
    return { ok: true, status: 200, async json() { return { results: [] }; } };
  });

  await handler(req3, res3);
  assert.equal(res3.statusCode, 200);

  restoreEnvAndFetch();
});

test('4. Composite tq_campaign regex extraction & direct/fallback GCLID parsing', async () => {
  // Composite --gclid- tag
  assert.equal(
    extractGclid({ tq_campaign: 'adv-tldr--gclid-Cj0KCQiA_composite_gclid_123' }),
    'Cj0KCQiA_composite_gclid_123'
  );

  // Uppercase composite tags
  assert.equal(
    extractGclid({ tq_campaign: 'adv-tldr--GCLID-CaseSensitive12345' }),
    'CaseSensitive12345'
  );
  assert.equal(
    extractGclid({ tq_campaign: 'adv-tldr--GCLID-Short123' }),
    'Short123'
  );

  // Organic composite tag
  assert.equal(
    extractGclid({ tq_campaign: 'adv-tldr--gclid-organic' }),
    null
  );

  // Composite with additional sub-delimiters
  assert.equal(
    extractGclid({ tq_campaign: 'paris-cruise--gclid-Cj0KCQiA111222333--sub-444' }),
    'Cj0KCQiA111222333'
  );

  // Raw GCLID parameter
  assert.equal(
    extractGclid({ tq_campaign: 'Cj0KCQiA_raw_gclid_99999999' }),
    'Cj0KCQiA_raw_gclid_99999999'
  );

  // Fallback gclid field
  assert.equal(
    extractGclid({ gclid: 'Cj0KCQiA_fallback_gclid_7777' }),
    'Cj0KCQiA_fallback_gclid_7777'
  );

  // Fallback subid field
  assert.equal(
    extractGclid({ subid: 'gclid:Cj0KCQiA_subid_gclid_8888' }),
    'Cj0KCQiA_subid_gclid_8888'
  );
});

test('5. Date formatting strictly as yyyy-mm-dd hh:mm:ss+zz:zz', async () => {
  // UTC ISO string
  const formatted1 = formatGoogleAdsDateTime('2026-08-10T14:30:00Z');
  assert.equal(formatted1, '2026-08-10 14:30:00+00:00');

  // Timezone offset string (+02:00) converted to UTC
  const formatted2 = formatGoogleAdsDateTime('2026-08-10T16:30:00+02:00');
  assert.equal(formatted2, '2026-08-10 14:30:00+00:00');

  // Regex pattern validation for yyyy-mm-dd hh:mm:ss+zz:zz
  const pattern = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{2}:\d{2}$/;
  assert.ok(pattern.test(formatted1), 'Timestamp must match yyyy-mm-dd hh:mm:ss+zz:zz pattern');
  assert.ok(pattern.test(formatted2), 'Timestamp must match yyyy-mm-dd hh:mm:ss+zz:zz pattern');
});

test('6. Method validation (reject non-POST HTTP methods with 405 Method Not Allowed)', async () => {
  restoreEnvAndFetch();

  const { req: getReq, res: getRes } = createMockReqRes({ method: 'GET' });
  await handler(getReq, getRes);
  assert.equal(getRes.statusCode, 405);
  assert.equal(getRes.body.error, 'method_not_allowed');

  const { req: putReq, res: putRes } = createMockReqRes({ method: 'PUT' });
  await handler(putReq, putRes);
  assert.equal(putRes.statusCode, 405);
  assert.equal(putRes.body.error, 'method_not_allowed');

  restoreEnvAndFetch();
});

test('7. Duplicate order handling (CLICK_CONVERSION_ALREADY_EXISTS)', async () => {
  restoreEnvAndFetch();
  process.env.NODE_ENV = 'test';

  setupFetchMock(async (url) => {
    if (url.includes('oauth2.googleapis.com/token')) {
      return { ok: true, status: 200, async json() { return { access_token: 'token', expires_in: 3600 }; } };
    }
    if (url.includes('uploadClickConversions')) {
      return {
        ok: false,
        status: 400,
        async json() {
          return {
            error: {
              code: 400,
              message: 'Conversion upload failed',
              details: [{ errors: [{ errorCode: { clickConversionError: 'CLICK_CONVERSION_ALREADY_EXISTS' } }] }]
            }
          };
        }
      };
    }
    return { ok: true, status: 200, async json() { return []; } };
  });

  const payload = {
    order_id: 'TQ-DUP-1001',
    tq_campaign: 'adv-tldr--gclid-Cj0KCQ_DUP_TEST_99999',
    financials: { total_price: 150.0, currency: 'EUR' }
  };

  const { req, res } = createMockReqRes({ body: payload });
  await handler(req, res);

  assert.equal(res.statusCode, 200, 'Duplicate conversion should return HTTP 200 OK gracefully');
  assert.equal(res.body.deduplicated, true);

  restoreEnvAndFetch();
});
