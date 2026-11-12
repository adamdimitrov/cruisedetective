import { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import handler, { safeTarget, parseCampaign, redisCommands, buildEvent } from '../api/go-tiqets.js';

const AD_URL = 'https://www.tiqets.com/en/paris-c66746/?partner=thecruisedetective.com-176436'
  + '&tq_campaign=paris-riv-cru-compar-bp--gclid-Cj0KCQabc&subid=Cj0KCQabc';

function mockRes() {
  return {
    statusCode: 200, headers: {}, ended: false,
    setHeader(k, v) { this.headers[k.toLowerCase()] = v; },
    end() { this.ended = true; },
  };
}

const origFetch = globalThis.fetch;
let calls;
beforeEach(() => {
  calls = [];
  process.env.KV_REST_API_URL = 'https://kv.example';
  process.env.KV_REST_API_TOKEN = 't';
  globalThis.fetch = async (url, opts) => { calls.push({ url, body: JSON.parse(opts.body) }); return { ok: true }; };
});
afterEach(() => {
  globalThis.fetch = origFetch;
  delete process.env.KV_REST_API_URL;
  delete process.env.KV_REST_API_TOKEN;
});

describe('safeTarget', () => {
  it('accepts https tiqets hosts', () => {
    assert.ok(safeTarget('https://www.tiqets.com/x'));
    assert.ok(safeTarget('https://tiqets.com/x'));
  });
  it('rejects other hosts, lookalikes and http', () => {
    for (const u of ['https://evil.com/?tiqets.com', 'https://tiqets.com.evil.com/', 'https://eviltiqets.com/',
      'http://www.tiqets.com/', 'javascript:alert(1)', '', undefined, '//www.tiqets.com']) {
      assert.strictEqual(safeTarget(u), null, String(u));
    }
  });
});

describe('parseCampaign', () => {
  it('splits placement and click id', () => {
    assert.deepStrictEqual(parseCampaign(new URL(AD_URL)),
      { placement: 'paris-riv-cru-compar-bp', clickType: 'gclid', clickId: 'Cj0KCQabc' });
  });
  it('keeps organic placement', () => {
    assert.deepStrictEqual(parseCampaign(new URL('https://www.tiqets.com/?tq_campaign=seine-tbl')),
      { placement: 'seine-tbl', clickType: null, clickId: null });
  });
});

describe('redisCommands', () => {
  it('counts bots separately and logs nothing else', () => {
    const ev = buildEvent({ query: { p: '/x' }, headers: { 'user-agent': 'Googlebot/2.1' } }, new URL(AD_URL));
    const cmds = redisCommands(ev);
    assert.deepStrictEqual(cmds[0], ['HINCRBY', `tqc:${ev.day}`, 'bot', '1']);
    assert.ok(!cmds.some(c => c[0] === 'RPUSH'));
  });
});

describe('handler', () => {
  it('records an ad click and redirects to the exact URL', async () => {
    const res = mockRes();
    await handler({ query: { u: AD_URL, p: '/seine-river-cruises-paris?x=1' }, headers: { 'user-agent': 'Mozilla/5.0' } }, res);
    assert.strictEqual(res.statusCode, 302);
    assert.strictEqual(res.headers.location, new URL(AD_URL).toString());
    assert.strictEqual(res.headers['cache-control'], 'no-store');
    assert.strictEqual(calls.length, 1);
    assert.strictEqual(calls[0].url, 'https://kv.example/pipeline');
    const flat = calls[0].body.map(c => c.join(' '));
    assert.ok(flat.some(c => /^HINCRBY tqc:\d{4}-\d\d-\d\d total 1$/.test(c)));
    assert.ok(flat.some(c => / ad 1$/.test(c)));
    assert.ok(flat.some(c => / page:\/seine-river-cruises-paris 1$/.test(c)));
    assert.ok(flat.some(c => / pl:paris-riv-cru-compar-bp 1$/.test(c)));
    assert.ok(flat.some(c => /^SADD tqc:.*:ids gclid:Cj0KCQabc$/.test(c)));
  });

  it('still redirects when storage fails', async () => {
    globalThis.fetch = async () => { throw new Error('down'); };
    const res = mockRes();
    await handler({ query: { u: AD_URL }, headers: {} }, res);
    assert.strictEqual(res.statusCode, 302);
    assert.strictEqual(res.headers.location, new URL(AD_URL).toString());
  });

  it('sends unsafe targets to the Tiqets home page without recording', async () => {
    const res = mockRes();
    await handler({ query: { u: 'https://evil.com/' }, headers: {} }, res);
    assert.strictEqual(res.headers.location, 'https://www.tiqets.com/');
    assert.strictEqual(calls.length, 0);
  });
});
