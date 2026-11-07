import test, { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { JSDOM } from 'jsdom';
import webhookHandler, { resetCache, verifyTiqetsSignature, extractClickId } from '../api/tiqets-webhook.js';

// =============================================================================
// Project Configuration & Paths
// =============================================================================
const PROJECT_ROOT = path.resolve('.');
const WEBFLOW_SYNC_PATH = path.join(PROJECT_ROOT, 'webflow-sync.js');
const VERCEL_JSON_PATH = path.join(PROJECT_ROOT, 'vercel.json');
const SITEMAP_PATH = path.join(PROJECT_ROOT, 'sitemap.xml');
const RATINGS_PATH = path.join(PROJECT_ROOT, 'ratings.json');

const LOCKED_TIQETS_PARTNER_ID = 'thecruisedetective.com-176436';
const APPROVED_LANGUAGES = ['en', 'ja', 'pl', 'ro', 'fr', 'nl'];
const DEAD_LANGUAGES = [
  'ar', 'bg', 'ca', 'cs', 'da', 'de', 'el', 'es', 'fa', 'fi',
  'he', 'hi', 'hr', 'hu', 'it', 'ko', 'no', 'pt', 'ru', 'sk',
  'sr', 'sv', 'th', 'tr', 'uk', 'vi', 'zh'
];

const CORE_MONEY_HUBS = [
  'seine-river-cruises-paris',
  'dinner-cruises-paris',
  'canal-cruises-amsterdam',
  'thames-river-cruises-london',
  'bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison'
];

// Fallback legacy directories during progressive milestone rollout
const LEGACY_HUB_FALLBACKS = {
  'seine-river-cruises-paris': path.join(PROJECT_ROOT, 'seine-comparison', 'index.html'),
  'dinner-cruises-paris': fs.existsSync(path.join(PROJECT_ROOT, 'articles', 'paris-dinner-cruises-overhaul', 'live_preview.html'))
    ? path.join(PROJECT_ROOT, 'articles', 'paris-dinner-cruises-overhaul', 'live_preview.html')
    : path.join(PROJECT_ROOT, 'dinner-comparison', 'index.html'),
  'canal-cruises-amsterdam': path.join(PROJECT_ROOT, 'amsterdam-comparison', 'index.html'),
  'thames-river-cruises-london': null,
  'bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison': null
};

// Load production client-side script
const webflowSyncCode = fs.existsSync(WEBFLOW_SYNC_PATH)
  ? fs.readFileSync(WEBFLOW_SYNC_PATH, 'utf8')
  : '';

// Global mock state
const originalFetch = globalThis.fetch;
const originalEnv = { ...process.env };

beforeEach(() => {
  globalThis.fetch = originalFetch;
  process.env = { ...originalEnv };
  resetCache();
});

afterEach(() => {
  globalThis.fetch = originalFetch;
  process.env = { ...originalEnv };
  resetCache();
});

// =============================================================================
// Helper Utilities
// =============================================================================

function loadHubHtml(hubSlug) {
  const targetPath = path.join(PROJECT_ROOT, hubSlug, 'index.html');
  if (fs.existsSync(targetPath)) {
    return { path: targetPath, html: fs.readFileSync(targetPath, 'utf8'), isTarget: true };
  }
  const fallback = LEGACY_HUB_FALLBACKS[hubSlug];
  if (fallback && fs.existsSync(fallback)) {
    return { path: fallback, html: fs.readFileSync(fallback, 'utf8'), isTarget: false };
  }
  return null;
}

function loadVercelConfig() {
  assert.ok(fs.existsSync(VERCEL_JSON_PATH), `vercel.json must exist at ${VERCEL_JSON_PATH}`);
  return JSON.parse(fs.readFileSync(VERCEL_JSON_PATH, 'utf8'));
}

function evaluateVercelRoute(testPath, vercelConfig) {
  const redirects = vercelConfig.redirects || [];
  for (const r of redirects) {
    if (r.source === testPath) {
      return {
        action: 'redirect',
        destination: r.destination,
        permanent: r.permanent === true || r.statusCode === 301 || r.statusCode === 308,
        statusCode: r.statusCode || (r.permanent ? 301 : 307)
      };
    }
    // Pattern matching for wildcard/regex routes
    if (r.source.includes(':')) {
      const regexStr = '^' + r.source
        .replace(/:lang\(([^)]+)\)/g, '(?<lang>$1)')
        .replace(/:lang/g, '(?<lang>[a-zA-Z0-9_-]+)')
        .replace(/:slug\*/g, '(?<slug>.*)')
        .replace(/:slug/g, '(?<slug>[^/]+)')
        .replace(/:path\*/g, '(?<path>.*)') + '$';
      const regex = new RegExp(regexStr);
      const match = testPath.match(regex);
      if (match) {
        let dest = r.destination;
        if (match.groups) {
          for (const [k, v] of Object.entries(match.groups)) {
            dest = dest.replace(`:${k}*`, v || '').replace(`:${k}`, v || '');
          }
        }
        return {
          action: 'redirect',
          destination: dest,
          permanent: r.permanent === true || r.statusCode === 301 || r.statusCode === 308,
          statusCode: r.statusCode || (r.permanent ? 301 : 307)
        };
      }
    }
  }

  const rewrites = vercelConfig.rewrites || [];
  for (const rw of rewrites) {
    if (rw.source === testPath) {
      return { action: 'rewrite', destination: rw.destination };
    }
  }

  return { action: 'none' };
}

function initDomEnv(url, html = '', initialStorage = {}) {
  const dom = new JSDOM(html, { url });
  const { window } = dom;
  const { document } = window;

  // Polyfill getElementById via querySelector for this JSDOM build
  if (!document.getElementById) {
    document.getElementById = (id) => document.querySelector('#' + id);
  }

  window.localStorage.clear();
  document.cookie = 'cd_gclid=; max-age=0; path=/;';
  document.cookie = 'cd_gclid_exp=; max-age=0; path=/;';

  if (initialStorage && typeof initialStorage === 'object') {
    for (const [k, v] of Object.entries(initialStorage)) {
      window.localStorage.setItem(k, v);
    }
  }

  const runner = new Function(
    'window',
    'document',
    'localStorage',
    'location',
    'MutationObserver',
    webflowSyncCode
  );
  runner(window, document, window.localStorage, window.location, window.MutationObserver);

  return { dom, window, document };
}

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

// =============================================================================
// TEST SUITE: The Cruise Detective Staging-First Static Architecture Overhaul
// =============================================================================

describe('The Cruise Detective Staging Architecture Overhaul — Comprehensive E2E Suite', () => {

  // ===========================================================================
  // TIER 1: Feature Coverage (>=5 tests per feature)
  // ===========================================================================
  describe('Tier 1: Feature Coverage', () => {

    // -------------------------------------------------------------------------
    // Feature 1: Canonical Tag Strict Enforcement
    // -------------------------------------------------------------------------
    describe('1.1 Canonical Tag Strict Enforcement', () => {
      it('1.1.1 Should contain a valid canonical tag in all 5 core money hubs', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          assert.ok(loaded, `Money hub ${hub} must have HTML content available`);
          const dom = new JSDOM(loaded.html);
          const canonical = dom.window.document.querySelector('link[rel="canonical"]');
          assert.ok(canonical, `Money hub ${hub} must contain a <link rel="canonical"> element`);
          const href = canonical.getAttribute('href');
          assert.ok(href && href.trim().length > 0, `Canonical tag in ${hub} must have a non-empty href`);
        }
      });

      it('1.1.2 Should enforce absolute HTTPS URLs on the official domain (thecruisedetective.com)', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const href = dom.window.document.querySelector('link[rel="canonical"]')?.getAttribute('href') || '';
          assert.match(
            href,
            /^https:\/\/www\.thecruisedetective\.com\//,
            `Canonical URL in ${hub} must use https://www.thecruisedetective.com/, got: "${href}"`
          );
        }
      });

      it('1.1.3 Should contain strictly zero "#" fragment characters in canonical hrefs', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const href = dom.window.document.querySelector('link[rel="canonical"]')?.getAttribute('href') || '';
          assert.ok(!href.includes('#'), `Canonical URL in ${hub} must contain 0 fragment hashes, got: "${href}"`);
        }
      });

      it('1.1.4 Should use normalized plural canonical slugs matching PROJECT.md interface contract', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const href = dom.window.document.querySelector('link[rel="canonical"]')?.getAttribute('href') || '';
          const expectedSlug = hub;
          assert.ok(
            href.includes(expectedSlug),
            `Canonical URL for ${hub} must point to /${expectedSlug}, got: "${href}"`
          );
        }
      });

      it('1.1.5 Should enforce self-referencing canonical structure on localized approved editions', () => {
        for (const lang of ['fr', 'nl', 'pl', 'ro', 'ja']) {
          const localizedCanonical = `https://www.thecruisedetective.com/${lang}/dinner-cruises-paris`;
          const parsed = new URL(localizedCanonical);
          assert.strictEqual(parsed.protocol, 'https:');
          assert.strictEqual(parsed.hostname, 'www.thecruisedetective.com');
          assert.ok(!parsed.hash, 'Localized canonical must not have hash');
          assert.ok(parsed.pathname.startsWith(`/${lang}/`), `Localized canonical must start with /${lang}/`);
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 2: 5 Core Money Hubs Normalization
    // -------------------------------------------------------------------------
    describe('1.2 5 Core Money Hubs Normalization', () => {
      it('1.2.1 Should locally store all 5 core money hubs in project root as specified by PROJECT.md', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const targetDir = path.join(PROJECT_ROOT, hub);
          const targetIndex = path.join(targetDir, 'index.html');
          assert.ok(
            fs.existsSync(targetIndex),
            `Money hub ${hub} must exist locally at ${targetIndex} per PROJECT.md § Code Layout`
          );
        }
      });

      it('1.2.2 Should provide valid semantic HTML5 document skeleton in all money hubs', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          assert.match(loaded.html, /<!DOCTYPE html>/i, `${hub} must declare <!DOCTYPE html>`);
          assert.match(loaded.html, /<html[^>]*>/i, `${hub} must contain <html> root tag`);
          assert.match(loaded.html, /<head[^>]*>[\s\S]*<\/head>/i, `${hub} must contain valid <head> block`);
          assert.match(loaded.html, /<body[^>]*>[\s\S]*<\/body>/i, `${hub} must contain valid <body> block`);
        }
      });

      it('1.2.3 Should contain responsive comparison elements (table or matrix) in each money hub', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const hasTableOrMatrix =
            loaded.html.includes('<table') ||
            loaded.html.includes('cd-table') ||
            loaded.html.includes('comparison-table') ||
            loaded.html.includes('comparison-matrix') ||
            loaded.html.includes('matrix-container');
          assert.ok(hasTableOrMatrix, `Money hub ${hub} must include a comparison table or matrix component`);
        }
      });

      it('1.2.4 Should maintain strict heading hierarchy with exactly 1 <h1> per page', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const h1List = dom.window.document.querySelectorAll('h1');
          assert.strictEqual(
            h1List.length,
            1,
            `Money hub ${hub} must have exactly 1 <h1> heading, found: ${h1List.length}`
          );
          assert.ok(h1List[0].textContent.trim().length > 0, `<h1> in ${hub} must not be empty`);
        }
      });

      it('1.2.5 Should provide accessible primary CTA buttons linking to approved affiliate targets', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const ctas = dom.window.document.querySelectorAll('a[href*="tiqets.com"], a[href*="getyourguide.com"]');
          assert.ok(ctas.length > 0, `Money hub ${hub} must contain outbound CTA booking links`);
          for (const cta of ctas) {
            const label = cta.textContent.trim() || cta.getAttribute('aria-label') || '';
            assert.ok(label.length > 0, `CTA link ${cta.getAttribute('href')} in ${hub} must have accessible text`);
          }
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 3: 301 Redirect Rules in vercel.json
    // -------------------------------------------------------------------------
    describe('1.3 301 Redirect Rules in vercel.json', () => {
      it('1.3.1 Should define a redirects array in vercel.json with permanent redirect status', () => {
        const config = loadVercelConfig();
        assert.ok(Array.isArray(config.redirects), 'vercel.json must define a "redirects" array');
        assert.ok(config.redirects.length > 0, 'vercel.json redirects array must not be empty');
        for (const r of config.redirects) {
          const isPerm = r.permanent === true || r.statusCode === 301 || r.statusCode === 308;
          assert.ok(isPerm, `Redirect rule for "${r.source}" must be permanent (301/308 or permanent: true)`);
        }
      });

      it('1.3.2 Should provide 301 redirects for sample URLs across European, Asian, and Middle-East dead languages', () => {
        const config = loadVercelConfig();
        const testSamples = [
          { url: '/de/besten-bootsfahrten-mit-abendessen-paris', target: '/dinner-cruises-paris' },
          { url: '/es/mejores-cruceros-canales-amsterdam', target: '/canal-cruises-amsterdam' },
          { url: '/it/migliori-crociere-cena-parigi', target: '/dinner-cruises-paris' },
          { url: '/ru/лучшие-круизы-с-ужином-париж', target: '/dinner-cruises-paris' },
          { url: '/zh/巴黎塞纳河晚餐游船', target: '/dinner-cruises-paris' }
        ];

        for (const sample of testSamples) {
          const result = evaluateVercelRoute(sample.url, config);
          assert.strictEqual(
            result.action,
            'redirect',
            `Dead language URL ${sample.url} must be redirected`
          );
          assert.ok(result.permanent, `Redirect for ${sample.url} must be permanent`);
          assert.strictEqual(
            result.destination,
            sample.target,
            `Redirect destination for ${sample.url} must match canonical English ${sample.target}`
          );
        }
      });

      it('1.3.3 Should ensure redirect destinations do not contain fragment hashes or dead parameters', () => {
        const config = loadVercelConfig();
        for (const r of config.redirects || []) {
          assert.ok(
            !r.destination.includes('#'),
            `Redirect destination "${r.destination}" from "${r.source}" must not contain "#" fragment`
          );
        }
      });

      it('1.3.4 Should include 301 redirect rules for legacy singular and alternative slugs', () => {
        const config = loadVercelConfig();
        const legacyMappings = [
          { from: '/dinner-cruise-paris', to: '/dinner-cruises-paris' },
          { from: '/amsterdam-canal-cruises', to: '/canal-cruises-amsterdam' }
        ];

        for (const mapping of legacyMappings) {
          const result = evaluateVercelRoute(mapping.from, config);
          assert.strictEqual(
            result.action,
            'redirect',
            `Legacy slug ${mapping.from} must redirect to canonical ${mapping.to}`
          );
          assert.strictEqual(result.destination, mapping.to);
          assert.ok(result.permanent);
        }
      });

      it('1.3.5 Should include wildcard fallback redirect rule for all 27 dead language prefixes', () => {
        const config = loadVercelConfig();
        for (const lang of DEAD_LANGUAGES) {
          const testPath = `/${lang}/arbitrary-unmapped-article-path-123`;
          const result = evaluateVercelRoute(testPath, config);
          assert.strictEqual(
            result.action,
            'redirect',
            `Arbitrary unmapped path under dead language ${lang} must redirect to /`
          );
          assert.strictEqual(result.destination, '/');
          assert.ok(result.permanent);
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 4: 6 Approved Languages Active Retention
    // -------------------------------------------------------------------------
    describe('1.4 6 Approved Languages Retention', () => {
      it('1.4.1 Should verify exactly the 6 approved high-converting languages are defined', () => {
        assert.deepStrictEqual(
          APPROVED_LANGUAGES.sort(),
          ['en', 'fr', 'ja', 'nl', 'pl', 'ro'].sort(),
          'Approved languages must strictly match [en, ja, pl, ro, fr, nl]'
        );
      });

      it('1.4.2 Should ensure none of the 6 approved languages are caught by dead language redirect rules', () => {
        const config = loadVercelConfig();
        for (const lang of ['ja', 'pl', 'ro', 'fr', 'nl']) {
          const activePath = `/${lang}/dinner-cruises-paris`;
          const result = evaluateVercelRoute(activePath, config);
          assert.notStrictEqual(
            result.destination,
            '/',
            `Approved language edition ${activePath} must NOT be redirected to root by fallback`
          );
        }
      });

      it('1.4.3 Should verify sitemap.xml exists and contains strictly active canonical URLs', () => {
        assert.ok(fs.existsSync(SITEMAP_PATH), `sitemap.xml must exist at ${SITEMAP_PATH}`);
        const sitemapContent = fs.readFileSync(SITEMAP_PATH, 'utf8');
        const urlMatches = sitemapContent.match(/<loc>[\s\S]*?<\/loc>/g) || [];
        assert.strictEqual(
          urlMatches.length,
          77,
          `sitemap.xml must contain exactly 77 active canonical URLs, found: ${urlMatches.length}`
        );
      });

      it('1.4.4 Should ensure sitemap hreflang links only reference approved languages and x-default', () => {
        assert.ok(fs.existsSync(SITEMAP_PATH), `sitemap.xml must exist at ${SITEMAP_PATH}`);
        const sitemapContent = fs.readFileSync(SITEMAP_PATH, 'utf8');
        const allowedHreflang = new Set(['en', 'en-us', 'ja', 'pl', 'ro', 'fr', 'nl', 'x-default']);
        const hreflangMatches = [...sitemapContent.matchAll(/hreflang=["']([^"']+)["']/g)];
        assert.ok(hreflangMatches.length > 0, 'sitemap.xml must contain alternate hreflang entries');
        for (const m of hreflangMatches) {
          const code = m[1].toLowerCase();
          assert.ok(
            allowedHreflang.has(code),
            `Forbidden hreflang "${code}" found in sitemap.xml; only approved languages allowed`
          );
        }
      });

      it('1.4.5 Should verify zero dead languages exist in sitemap.xml <loc> entries', () => {
        assert.ok(fs.existsSync(SITEMAP_PATH), `sitemap.xml must exist at ${SITEMAP_PATH}`);
        const sitemapContent = fs.readFileSync(SITEMAP_PATH, 'utf8');
        for (const dead of DEAD_LANGUAGES) {
          const deadLocRegex = new RegExp(`<loc>https://www\\.thecruisedetective\\.com/${dead}/`, 'i');
          assert.ok(
            !deadLocRegex.test(sitemapContent),
            `Dead language ${dead} must NOT appear in sitemap <loc> URLs`
          );
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 5: Tiqets Partner Parameter Enforcement
    // -------------------------------------------------------------------------
    describe('1.5 Tiqets Partner Parameter Enforcement', () => {
      it('1.5.1 Should enforce partner=thecruisedetective.com-176436 on 100% of outbound Tiqets links in money hubs', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const tiqetsLinks = dom.window.document.querySelectorAll('a[href*="tiqets.com"]');
          assert.ok(tiqetsLinks.length > 0, `${hub} must contain at least one Tiqets booking link`);
          for (const link of tiqetsLinks) {
            const href = link.getAttribute('href');
            assert.ok(
              href.includes(`partner=${LOCKED_TIQETS_PARTNER_ID}`),
              `Outbound Tiqets link in ${hub} must have partner=${LOCKED_TIQETS_PARTNER_ID}, found: "${href}"`
            );
          }
        }
      });

      it('1.5.2 Should verify ratings.json uses the locked partner ID for all Tiqets URLs', () => {
        assert.ok(fs.existsSync(RATINGS_PATH), `ratings.json must exist at ${RATINGS_PATH}`);
        const ratings = JSON.parse(fs.readFileSync(RATINGS_PATH, 'utf8'));
        const tiqetsPartnerKeys = Object.keys(ratings).filter(k => k.includes('tiqets.com') && k.includes('partner='));
        assert.ok(tiqetsPartnerKeys.length > 0, 'ratings.json must have Tiqets partner URLs');
        for (const urlKey of tiqetsPartnerKeys) {
          assert.ok(
            urlKey.includes(`partner=${LOCKED_TIQETS_PARTNER_ID}`),
            `Key in ratings.json must use ${LOCKED_TIQETS_PARTNER_ID}, found: "${urlKey}"`
          );
        }
      });

      it('1.5.3 Should preserve or attach tq_campaign parameters to all Tiqets links', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const tiqetsLinks = dom.window.document.querySelectorAll('a[href*="tiqets.com"]');
          for (const link of tiqetsLinks) {
            const href = link.getAttribute('href');
            assert.match(
              href,
              /tq_campaign=[^&]+/,
              `Tiqets link "${href}" in ${hub} must include a tq_campaign parameter`
            );
          }
        }
      });

      it('1.5.4 Should leave non-Tiqets affiliate links (e.g. GetYourGuide) with their own partner IDs intact', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const gygLinks = dom.window.document.querySelectorAll('a[href*="getyourguide.com"]');
          for (const link of gygLinks) {
            const href = link.getAttribute('href');
            assert.ok(
              !href.includes(LOCKED_TIQETS_PARTNER_ID),
              `GetYourGuide link "${href}" in ${hub} must NOT contain Tiqets partner ID`
            );
          }
        }
      });

      it('1.5.5 Should enforce target="_blank" and rel="noopener" on all outbound affiliate links', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const links = dom.window.document.querySelectorAll('a[href*="tiqets.com"], a[href*="getyourguide.com"]');
          for (const link of links) {
            assert.strictEqual(
              link.getAttribute('target'),
              '_blank',
              `Affiliate link "${link.getAttribute('href')}" in ${hub} must specify target="_blank"`
            );
            const rel = link.getAttribute('rel') || '';
            assert.ok(
              rel.includes('noopener'),
              `Affiliate link "${link.getAttribute('href')}" in ${hub} must specify rel containing "noopener"`
            );
          }
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 6: Offline Webhook Ingestion & S2S Pipeline
    // -------------------------------------------------------------------------
    describe('1.6 Offline Webhook Ingestion & S2S Pipeline', () => {
      it('1.6.1 Should accept valid POST webhook payload with HMAC signature and return HTTP 200', async () => {
        let uploadedPayload = null;
        globalThis.fetch = async (url, opts = {}) => {
          if (String(url).includes('datamanager.googleapis.com')) {
            uploadedPayload = JSON.parse(opts.body);
            return {
              ok: true,
              status: 200,
              json: async () => ({ status: 'success' }),
              text: async () => JSON.stringify({ status: 'success' })
            };
          }
          return { ok: true, status: 200, json: async () => ({}) };
        };

        const secret = 'test-tiqets-secret-key-123';
        process.env.TIQETS_WEBHOOK_SECRET = secret;
        process.env.NODE_ENV = 'test';

        const payloadObj = {
          order_id: 'TQ-E2E-TEST-001',
          created_at: new Date().toISOString(),
          tq_campaign: 'table-paris-bm--gclid-Cj0KCQ_tier1_webhook_valid',
          financials: { total_price: '150.00', commission_amount: '62.85', currency: 'EUR' }
        };
        const rawBody = Buffer.from(JSON.stringify(payloadObj));
        const sig = 'sha256=' + crypto.createHmac('sha256', secret).update(rawBody).digest('hex');

        const { req, res } = createMockReqRes({
          method: 'POST',
          headers: { 'x-tiqets-signature': sig },
          rawBody
        });

        await webhookHandler(req, res);

        assert.strictEqual(res.statusCode, 200, `Expected HTTP 200, got ${res.statusCode}`);
        assert.ok(uploadedPayload, 'Should have invoked Google Data Manager API');
        assert.strictEqual(uploadedPayload.events[0].transactionId, 'TQ-E2E-TEST-001');
        assert.strictEqual(uploadedPayload.events[0].adIdentifiers.gclid, 'Cj0KCQ_tier1_webhook_valid');
      });

      it('1.6.2 Should reject webhook request with invalid or missing HMAC signature with HTTP 401', async () => {
        const secret = 'strict-webhook-secret';
        process.env.TIQETS_WEBHOOK_SECRET = secret;
        process.env.NODE_ENV = 'production';

        const payload = { order_id: 'BAD-SIG-001', gclid: 'Cj0KCQ_bad_sig' };
        const rawBody = Buffer.from(JSON.stringify(payload));

        const { req, res } = createMockReqRes({
          method: 'POST',
          headers: { 'x-tiqets-signature': 'sha256=invalidhash99999' },
          rawBody
        });

        await webhookHandler(req, res);
        assert.strictEqual(res.statusCode, 401, 'Invalid signature must return HTTP 401');
      });

      it('1.6.3 Should gracefully skip organic sale payloads with HTTP 200 and reason no_gclid_found', async () => {
        let fetchCalled = false;
        globalThis.fetch = async () => {
          fetchCalled = true;
          return { ok: true, status: 200, json: async () => ({}) };
        };

        const payload = {
          order_id: 'ORGANIC-SALE-999',
          tq_campaign: 'table-paris-bm', // Naked organic campaign tag without click ID
          financials: { total_price: '180.00', commission_amount: '75.42', currency: 'EUR' }
        };

        const { req, res } = createMockReqRes({ method: 'POST', body: payload });
        await webhookHandler(req, res);

        assert.strictEqual(res.statusCode, 200, 'Organic sale must return HTTP 200');
        assert.strictEqual(res.body.status, 'skipped');
        assert.strictEqual(res.body.reason, 'no_gclid_found');
        assert.strictEqual(fetchCalled, false, 'Google Ads API must not be called for organic sales');
      });

      it('1.6.4 Should reject non-POST HTTP methods with HTTP 405 Method Not Allowed', async () => {
        for (const method of ['GET', 'PUT', 'DELETE', 'PATCH']) {
          const { req, res } = createMockReqRes({ method });
          await webhookHandler(req, res);
          assert.strictEqual(res.statusCode, 405, `Method ${method} must return HTTP 405`);
        }
      });

      it('1.6.5 Should format Google Data Manager payload matching destinations and events contract', async () => {
        let sentBody = null;
        globalThis.fetch = async (url, opts = {}) => {
          if (String(url).includes('datamanager.googleapis.com')) {
            sentBody = JSON.parse(opts.body);
            return { ok: true, status: 200, json: async () => ({ status: 'success' }) };
          }
          return { ok: true, status: 200, json: async () => ({}) };
        };

        const payload = {
          order_id: 'TQ-CONTRACT-VERIFY-1',
          created_at: '2026-11-06T00:00:00Z',
          wbraid: 'wbraid_ios_click_token_123',
          financials: { total_price: '220.00', commission_amount: '92.18', currency: 'EUR' }
        };

        const { req, res } = createMockReqRes({ method: 'POST', body: payload });
        await webhookHandler(req, res);

        assert.strictEqual(res.statusCode, 200);
        assert.ok(sentBody.destinations && sentBody.destinations.length > 0);
        assert.strictEqual(sentBody.destinations[0].operatingAccount.accountType, 'GOOGLE_ADS');
        assert.strictEqual(sentBody.events[0].conversionValue, 92.18);
        assert.strictEqual(sentBody.events[0].currency, 'EUR');
        assert.strictEqual(sentBody.events[0].adIdentifiers.wbraid, 'wbraid_ios_click_token_123');
      });
    });

  });

  // ===========================================================================
  // TIER 2: Boundary & Corner Cases (>=5 tests per feature)
  // ===========================================================================
  describe('Tier 2: Boundary & Corner Cases', () => {

    // -------------------------------------------------------------------------
    // Feature 1: Headings: 0 Unicode Emojis and 0 NBSP
    // -------------------------------------------------------------------------
    describe('2.1 Headings: 0 Unicode Emojis and 0 NBSP', () => {
      const EMOJI_REGEX = /[\u{1F000}-\u{1FFFF}\u{2600}-\u{27BF}]/u;

      it('2.1.1 Should contain 0 high-surrogate emojis in any heading across all money hubs', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const headings = dom.window.document.querySelectorAll('h1, h2, h3, h4, h5, h6');
          for (const h of headings) {
            const text = h.textContent;
            assert.ok(
              !EMOJI_REGEX.test(text),
              `Heading in ${hub} contains forbidden emoji: "${text}"`
            );
          }
        }
      });

      it('2.1.2 Should contain 0 literal non-breaking space characters (\\u00a0) in headings', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const headings = dom.window.document.querySelectorAll('h1, h2, h3, h4, h5, h6');
          for (const h of headings) {
            assert.ok(
              !h.textContent.includes('\u00a0'),
              `Heading in ${hub} contains literal \\u00a0 non-breaking space: "${h.textContent}"`
            );
          }
        }
      });

      it('2.1.3 Should contain 0 raw &nbsp; HTML entities inside heading markup', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const headingMatches = loaded.html.match(/<h[1-6][^>]*>[\s\S]*?<\/h[1-6]>/gi) || [];
          for (const hMarkup of headingMatches) {
            assert.ok(
              !hMarkup.includes('&nbsp;'),
              `Heading markup in ${hub} contains &nbsp; entity: "${hMarkup}"`
            );
          }
        }
      });

      it('2.1.4 Should preserve valid French accented characters without mojibake in headings', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          // Must not contain common UTF-8 double-encoding artifacts (e.g. Ã©, Ã¨)
          assert.ok(
            !loaded.html.includes('Ã©') && !loaded.html.includes('Ã¨'),
            `Money hub ${hub} contains corrupted mojibake encoding`
          );
        }
      });

      it('2.1.5 Should ensure nested headings in comparison cards maintain zero emojis', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const cardHeadings = dom.window.document.querySelectorAll('.boat-card h2, .boat-card h3, .cd-col-boat, .card h3');
          for (const ch of cardHeadings) {
            assert.ok(
              !EMOJI_REGEX.test(ch.textContent),
              `Card heading in ${hub} contains emoji: "${ch.textContent}"`
            );
          }
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 2: Anchor IDs: HTML5 Validity & Hex/NBSP Elimination
    // -------------------------------------------------------------------------
    describe('2.2 Anchor IDs: HTML5 Validity & Hex/NBSP Elimination', () => {
      it('2.2.1 Should contain 0 hex-encoded emoji sequences in any id attribute', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const elementsWithId = dom.window.document.querySelectorAll('[id]');
          for (const el of elementsWithId) {
            const id = el.getAttribute('id');
            assert.ok(
              !/%F0%|%E2%|%8F%|%9F%/i.test(id),
              `Element in ${hub} has hex-encoded emoji id: "${id}"`
            );
          }
        }
      });

      it('2.2.2 Should contain 0 occurrences of "cruisenbspwith" or "nbsp" in anchor IDs', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const elementsWithId = dom.window.document.querySelectorAll('[id]');
          for (const el of elementsWithId) {
            const id = el.getAttribute('id').toLowerCase();
            assert.ok(
              !id.includes('cruisenbspwith') && !id.includes('nbsp'),
              `Element in ${hub} contains corrupt nbsp id: "${id}"`
            );
          }
        }
      });

      it('2.2.3 Should conform to HTML5 ID specifications (no whitespace, non-empty)', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const elementsWithId = dom.window.document.querySelectorAll('[id]');
          for (const el of elementsWithId) {
            const id = el.getAttribute('id');
            assert.ok(id.length > 0, `Empty ID attribute found in ${hub}`);
            assert.ok(!/\s/.test(id), `Whitespace found in ID attribute in ${hub}: "${id}"`);
          }
        }
      });

      it('2.2.4 Should ensure in-page table-of-contents anchor links match target elements', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const anchorLinks = dom.window.document.querySelectorAll('a[href^="#"]:not([href="#"])');
          for (const a of anchorLinks) {
            const targetId = a.getAttribute('href').slice(1);
            const targetEl = dom.window.document.getElementById(targetId);
            assert.ok(
              targetEl !== null,
              `Broken internal anchor link href="#${targetId}" in ${hub} has no matching element ID`
            );
          }
        }
      });

      it('2.2.5 Should follow semantic naming conventions (#boat-<slug> or #<slug>)', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const boatElements = dom.window.document.querySelectorAll('[id*="boat-"]');
          for (const el of boatElements) {
            const id = el.getAttribute('id');
            assert.match(
              id,
              /^boat-[a-z0-9-]+$/,
              `Boat anchor ID in ${hub} must match format ^boat-[a-z0-9-]+$, got: "${id}"`
            );
          }
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 3: Canonical URLs: Strict Format & Dirty Pattern Rejection
    // -------------------------------------------------------------------------
    describe('2.3 Canonical URLs: Strict Format & Dirty Pattern Rejection', () => {
      it('2.3.1 Should reject any canonical tag containing fragment identifiers (#)', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const href = dom.window.document.querySelector('link[rel="canonical"]')?.getAttribute('href') || '';
          assert.strictEqual(href.indexOf('#'), -1, `Canonical tag in ${hub} contains "#": ${href}`);
        }
      });

      it('2.3.2 Should reject query parameters in canonical tags (?partner=, ?gclid=, etc.)', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const href = dom.window.document.querySelector('link[rel="canonical"]')?.getAttribute('href') || '';
          assert.strictEqual(href.indexOf('?'), -1, `Canonical tag in ${hub} contains query string "?": ${href}`);
        }
      });

      it('2.3.3 Should reject insecure http:// protocol in canonical tags', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const href = dom.window.document.querySelector('link[rel="canonical"]')?.getAttribute('href') || '';
          assert.ok(
            !href.startsWith('http://'),
            `Canonical tag in ${hub} must not use insecure http://: ${href}`
          );
        }
      });

      it('2.3.4 Should reject unauthorized domains/subdomains (deals.thecruisedetective.com, vercel.app)', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const href = dom.window.document.querySelector('link[rel="canonical"]')?.getAttribute('href') || '';
          assert.ok(
            !href.includes('deals.thecruisedetective.com') && !href.includes('vercel.app'),
            `Canonical tag in ${hub} must point strictly to production root domain, found: ${href}`
          );
        }
      });

      it('2.3.5 Should reject trailing slashes on article canonical paths', () => {
        for (const hub of CORE_MONEY_HUBS) {
          const loaded = loadHubHtml(hub);
          if (!loaded) continue;
          const dom = new JSDOM(loaded.html);
          const href = dom.window.document.querySelector('link[rel="canonical"]')?.getAttribute('href') || '';
          assert.ok(
            !href.endsWith('/'),
            `Canonical tag in ${hub} should not contain trailing slash: ${href}`
          );
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 4: Wildcard Language Fallback Routing
    // -------------------------------------------------------------------------
    describe('2.4 Wildcard Language Fallback Routing', () => {
      it('2.4.1 Should redirect deep unmapped German paths (/de/a/b/c) to root /', () => {
        const config = loadVercelConfig();
        const res = evaluateVercelRoute('/de/a/b/c', config);
        assert.strictEqual(res.action, 'redirect');
        assert.strictEqual(res.destination, '/');
        assert.ok(res.permanent);
      });

      it('2.4.2 Should redirect deep unmapped Spanish paths (/es/non-existent) to root /', () => {
        const config = loadVercelConfig();
        const res = evaluateVercelRoute('/es/non-existent', config);
        assert.strictEqual(res.action, 'redirect');
        assert.strictEqual(res.destination, '/');
        assert.ok(res.permanent);
      });

      it('2.4.3 Should redirect bare dead language root paths (/it or /it/) to root /', () => {
        const config = loadVercelConfig();
        const res = evaluateVercelRoute('/it', config);
        assert.strictEqual(res.action, 'redirect');
        assert.strictEqual(res.destination, '/');
      });

      it('2.4.4 Should NOT redirect approved language paths to root /', () => {
        const config = loadVercelConfig();
        for (const lang of ['ja', 'pl', 'ro', 'fr', 'nl']) {
          const res = evaluateVercelRoute(`/${lang}/dinner-cruises-paris`, config);
          assert.notStrictEqual(res.destination, '/', `Approved lang ${lang} must not be caught by fallback`);
        }
      });

      it('2.4.5 Should redirect obscure dead languages (e.g. /fa/..., /he/...) to root /', () => {
        const config = loadVercelConfig();
        for (const obscure of ['fa', 'he', 'hi', 'uk', 'vi']) {
          const res = evaluateVercelRoute(`/${obscure}/something`, config);
          assert.strictEqual(res.action, 'redirect');
          assert.strictEqual(res.destination, '/');
        }
      });
    });

    // -------------------------------------------------------------------------
    // Feature 5: Malformed Click IDs & Special Characters in GCLID Handling
    // -------------------------------------------------------------------------
    describe('2.5 Malformed Click IDs & Special Characters in GCLID Handling', () => {
      it('2.5.1 Should safely sanitize XSS / HTML injection in gclid parameter', () => {
        const xssPayload = '"><script>alert("xss")</script>';
        const initialHtml = `<a id="cta" href="https://www.tiqets.com/en/paris-c66746/?partner=${LOCKED_TIQETS_PARTNER_ID}">Book</a>`;
        const { window, document } = initDomEnv(`https://thecruisedetective.com/?gclid=${encodeURIComponent(xssPayload)}`, initialHtml);

        const link = document.getElementById('cta');
        assert.ok(!link.href.includes('<script>'), 'Injected script tags must not be rendered raw in href');
      });

      it('2.5.2 Should safely handle extremely long click IDs (500+ characters) without throwing', () => {
        const longId = 'Cj0KCQ_' + 'A'.repeat(500);
        const initialHtml = `<a id="cta" href="https://www.tiqets.com/en/paris-c66746/?partner=${LOCKED_TIQETS_PARTNER_ID}">Book</a>`;
        assert.doesNotThrow(() => {
          initDomEnv(`https://thecruisedetective.com/?gclid=${longId}`, initialHtml);
        });
      });

      it('2.5.3 Should cleanly decode and handle URL-encoded characters in gclid', () => {
        const cleanVal = 'test-click-val_123';
        const initialHtml = `<a id="cta" href="https://www.tiqets.com/en/paris-c66746/?partner=${LOCKED_TIQETS_PARTNER_ID}">Book</a>`;
        const { window } = initDomEnv(`https://thecruisedetective.com/?gclid=${encodeURIComponent(cleanVal)}`, initialHtml);

        const stored = window.localStorage.getItem('cd_gclid');
        assert.ok(stored.includes(cleanVal), 'Stored click ID should contain clean decoded value');
      });

      it('2.5.4 Should ignore empty or whitespace-only gclid parameters', () => {
        const initialHtml = `<a id="cta" href="https://www.tiqets.com/en/paris-c66746/?partner=${LOCKED_TIQETS_PARTNER_ID}">Book</a>`;
        const { window } = initDomEnv(`https://thecruisedetective.com/?gclid=%20%20%20`, initialHtml);

        const stored = window.localStorage.getItem('cd_gclid');
        assert.strictEqual(stored, null, 'Whitespace-only gclid must not be stored in localStorage');
      });

      it('2.5.5 Should clear stored click ID when cd_gclid_exp timestamp is expired', () => {
        const initialHtml = `<a id="cta" href="https://www.tiqets.com/en/paris-c66746/?partner=${LOCKED_TIQETS_PARTNER_ID}">Book</a>`;
        const { window } = initDomEnv('https://thecruisedetective.com/', initialHtml, {
          cd_gclid: 'EXPIRED_CLICK_ID_999',
          cd_gclid_exp: String(Date.now() - 86400000)
        });

        const effectiveGclid = window.CruiseDetectiveTracking?.getGclid();
        const value = typeof effectiveGclid === 'object' ? effectiveGclid?.value : effectiveGclid;
        assert.ok(!value, 'Expired click ID must return falsy (null or undefined)');
      });
    });

  });

  // ===========================================================================
  // TIER 3: Cross-Feature Combinations
  // ===========================================================================
  describe('Tier 3: Cross-Feature Combinations', () => {

    it('3.1 Should decorate outbound Tiqets links with locked partner ID and GCLID on approved localized pages', () => {
      const gclid = 'Cj0KCQ_localized_cross_test_123';
      const initialHtml = `
        <header><nav><a href="/fr/meilleurs-diners-croisieres-paris">FR</a></nav></header>
        <main>
          <a id="cta1" href="https://www.tiqets.com/fr/things-to-do-in-paris-c66746/tickets-for-dinner-p982924?partner=${LOCKED_TIQETS_PARTNER_ID}&tq_campaign=fr-dinner">Réserver</a>
        </main>
      `;

      const { document } = initDomEnv(`https://thecruisedetective.com/fr/dinner-cruises-paris?gclid=${gclid}`, initialHtml);
      const link = document.querySelector('#cta1');
      assert.ok(link.href.includes(`partner=${LOCKED_TIQETS_PARTNER_ID}`), 'Must preserve locked partner ID');
      assert.ok(link.href.includes(`gclid=${gclid}`) || link.href.includes(gclid), 'Must decorate with active GCLID');
      assert.ok(link.href.includes('fr-dinner'), 'Must preserve base campaign tag');
    });

    it('3.2 Should parse both composite tq_campaign and direct GCLID in offline conversion webhook', () => {
      // 1. Composite tag extraction
      const payloadComposite = {
        order_id: 'TQ-COMPOSITE-1',
        tq_campaign: 'table-paris-bm--gclid-COMPOSITE_GCLID_TOKEN_123'
      };
      const extracted1 = extractClickId(payloadComposite);
      assert.strictEqual(extracted1.type, 'gclid');
      assert.strictEqual(extracted1.value, 'COMPOSITE_GCLID_TOKEN_123');

      // 2. Direct payload extraction
      const payloadDirect = {
        order_id: 'TQ-DIRECT-1',
        tq_campaign: 'table-paris-bm',
        gclid: 'RAW_GCLID_TOKEN_456789'
      };
      const extracted2 = extractClickId(payloadDirect);
      assert.strictEqual(extracted2.type, 'gclid');
      assert.strictEqual(extracted2.value, 'RAW_GCLID_TOKEN_456789');
    });

    it('3.3 Should intercept and decorate links dynamically injected inside Shadow DOM roots', () => {
      const gclid = 'Cj0KCQ_shadow_dom_cross_feature';
      const initialHtml = `<div id="host"></div>`;
      const { window, document } = initDomEnv(`https://thecruisedetective.com/?gclid=${gclid}`, initialHtml);

      const host = document.querySelector('#host');
      const shadow = host.attachShadow({ mode: 'open' });
      const shadowLink = document.createElement('a');
      shadowLink.id = 'shadow-cta';
      shadowLink.href = `https://www.tiqets.com/en/paris-c66746/?partner=${LOCKED_TIQETS_PARTNER_ID}&tq_campaign=shadow-test`;
      shadowLink.textContent = 'Shadow CTA';
      shadow.appendChild(shadowLink);

      // Simulate click event bubbling with composed path
      const clickEvent = new window.Event('click', { bubbles: true, composed: true });
      shadowLink.dispatchEvent(clickEvent);

      assert.ok(shadowLink.href.includes(gclid), 'Shadow DOM link must be decorated on click interaction');
      assert.ok(shadowLink.href.includes(`partner=${LOCKED_TIQETS_PARTNER_ID}`));
    });

    it('3.4 Should synchronize across sessions via dual storage (cookie + localStorage fallback)', () => {
      const gclid = 'Cj0KCQ_session_sync_dual_storage';
      const initialHtml = `<a id="cta" href="https://www.tiqets.com/en/paris-c66746/?partner=${LOCKED_TIQETS_PARTNER_ID}&tq_campaign=sync-test">Book</a>`;

      // Session 1: Arrival with GCLID in URL
      const env1 = initDomEnv(`https://thecruisedetective.com/?gclid=${gclid}`, initialHtml);
      const cookieVal = env1.document.cookie;
      assert.ok(cookieVal.includes('cd_gclid='), 'Cookie must be populated on arrival');

      // Session 2: Internal navigation without query params, localStorage empty
      const dom2 = new JSDOM(initialHtml, { url: 'https://thecruisedetective.com/dinner-cruises-paris' });
      if (!dom2.window.document.getElementById) {
        dom2.window.document.getElementById = (id) => dom2.window.document.querySelector('#' + id);
      }
      dom2.window.document.cookie = cookieVal; // Pass along cookie
      dom2.window.localStorage.clear();

      const runner = new Function('window', 'document', 'localStorage', 'location', 'MutationObserver', webflowSyncCode);
      runner(dom2.window, dom2.window.document, dom2.window.localStorage, dom2.window.location, dom2.window.MutationObserver);

      const link = dom2.window.document.querySelector('#cta');
      assert.ok(link.href.includes(gclid), 'Link must be decorated via cookie fallback on secondary page');
      assert.strictEqual(
        dom2.window.localStorage.getItem('cd_gclid'),
        gclid,
        'Cookie fallback must repopulate localStorage'
      );
    });

    it('3.5 Should enforce Vercel routing precedence: 301 redirects execute before static rewrites', () => {
      const config = loadVercelConfig();
      // Ensure dead language paths with potential static collisions are redirected first
      const deadPath = '/de/dinner-cruises-paris';
      const routeResult = evaluateVercelRoute(deadPath, config);
      assert.strictEqual(
        routeResult.action,
        'redirect',
        `Dead language path ${deadPath} must be redirected, not rewritten`
      );
    });

  });

  // ===========================================================================
  // TIER 4: Real-World Scenarios
  // ===========================================================================
  describe('Tier 4: Real-World Scenarios', () => {

    it('4.1 Scenario 1: End-to-End Paid Search Journey to Conversion Upload', async () => {
      // 1. Visitor arrives from Google Ad with GCLID
      const gclid = 'Cj0KCQ_real_world_journey_full_e2e_999';
      const landingHtml = `
        <h1>Paris Dinner Cruises</h1>
        <div class="cd-table-container">
          <a id="btn-bm" href="https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-dinner-cruise-by-bateaux-mouches-p982924/?partner=${LOCKED_TIQETS_PARTNER_ID}&tq_campaign=table-paris-bm">Book Mouches</a>
        </div>
      `;

      const { document } = initDomEnv(`https://thecruisedetective.com/dinner-cruises-paris?gclid=${gclid}`, landingHtml);
      const button = document.querySelector('#btn-bm');

      // 2. Button is decorated with partner ID and GCLID
      assert.ok(button.href.includes(`partner=${LOCKED_TIQETS_PARTNER_ID}`));
      assert.ok(button.href.includes(gclid));

      // 3. User buys ticket on Tiqets -> Tiqets fires S2S Webhook
      let uploadTarget = null;
      let uploadHeaders = null;
      let uploadBody = null;

      globalThis.fetch = async (url, opts = {}) => {
        if (String(url).includes('datamanager.googleapis.com')) {
          uploadTarget = String(url);
          uploadHeaders = opts.headers;
          uploadBody = JSON.parse(opts.body);
          return { ok: true, status: 200, json: async () => ({ status: 'success' }) };
        }
        return { ok: true, status: 200, json: async () => ({}) };
      };

      const webhookPayload = {
        order_id: 'TIQETS-REAL-ORDER-4421',
        created_at: new Date().toISOString(),
        tq_campaign: `table-paris-bm--gclid-${gclid}`,
        financials: {
          total_price: '270.00',
          commission_amount: '113.13', // 41.9% commission
          currency: 'EUR'
        }
      };

      const { req, res } = createMockReqRes({ method: 'POST', body: webhookPayload });
      await webhookHandler(req, res);

      // 4. Verification of Google Data Manager S2S conversion payload
      assert.strictEqual(res.statusCode, 200);
      assert.strictEqual(uploadTarget, 'https://datamanager.googleapis.com/v1/events:ingest');
      assert.ok(uploadHeaders.Authorization.startsWith('Bearer '));
      assert.strictEqual(uploadBody.events[0].transactionId, 'TIQETS-REAL-ORDER-4421');
      assert.strictEqual(uploadBody.events[0].conversionValue, 113.13);
      assert.strictEqual(uploadBody.events[0].adIdentifiers.gclid, gclid);
    });

    it('4.2 Scenario 2: Search Engine Crawler Full Audit of sitemap.xml', () => {
      assert.ok(fs.existsSync(SITEMAP_PATH), 'sitemap.xml must exist for crawler audit');
      const sitemap = fs.readFileSync(SITEMAP_PATH, 'utf8');

      // 1. Crawler extracts all canonical locations
      const locRegex = /<loc>(https:\/\/www\.thecruisedetective\.com\/[^<]+)<\/loc>/g;
      const locations = [...sitemap.matchAll(locRegex)].map(m => m[1]);

      assert.strictEqual(locations.length, 77, 'Crawler must discover exactly 77 active canonical URLs');

      // 2. Crawler verifies zero anchor pollution
      for (const loc of locations) {
        assert.ok(!loc.includes('#'), `Crawler discovered dirty anchor URL in sitemap: ${loc}`);
      }

      // 3. Crawler verifies representation across all 6 approved languages
      for (const lang of ['en', 'ja', 'pl', 'ro', 'fr', 'nl']) {
        const hasLang = locations.some(loc =>
          lang === 'en' ? !loc.match(/www\.thecruisedetective\.com\/(ja|pl|ro|fr|nl)\//) : loc.includes(`/${lang}/`)
        );
        assert.ok(hasLang, `Crawler must find URLs for approved language: ${lang}`);
      }
    });

    it('4.3 Scenario 3: Organic Visitor Non-Ad Journey', async () => {
      const initialHtml = `<a id="cta" href="https://www.tiqets.com/en/paris-c66746/?partner=${LOCKED_TIQETS_PARTNER_ID}&tq_campaign=seo-organic">Book</a>`;
      const { document } = initDomEnv('https://thecruisedetective.com/seine-river-cruises-paris', initialHtml);

      const link = document.querySelector('#cta');
      assert.ok(link.href.includes(`partner=${LOCKED_TIQETS_PARTNER_ID}`));
      assert.ok(!link.href.includes('gclid='), 'Organic visitor links must not contain gclid');

      // Tiqets reports organic order
      let fetchCalled = false;
      globalThis.fetch = async () => { fetchCalled = true; return { ok: true, status: 200, json: async () => ({}) }; };

      const organicOrder = {
        order_id: 'ORGANIC-TQ-7712',
        tq_campaign: 'seo-organic',
        financials: { total_price: '54.00', commission_amount: '22.63', currency: 'EUR' }
      };

      const { req, res } = createMockReqRes({ method: 'POST', body: organicOrder });
      await webhookHandler(req, res);

      assert.strictEqual(res.statusCode, 200);
      assert.strictEqual(res.body.status, 'skipped');
      assert.strictEqual(fetchCalled, false, 'Organic conversions must not call Google Ads');
    });

    it('4.4 Scenario 4: International Traveler Legacy URL Redirection to Canonical Hubs', () => {
      const config = loadVercelConfig();
      const legacyJourneys = [
        { requested: '/de/besten-bootsfahrten-mit-abendessen-paris', target: '/dinner-cruises-paris' },
        { requested: '/es/mejores-cruceros-canales-amsterdam', target: '/canal-cruises-amsterdam' },
        { requested: '/ru/лучшие-круизы-с-ужином-париж', target: '/dinner-cruises-paris' },
        { requested: '/de/themse-kreuzfahrten-london', target: '/thames-river-cruises-london' },
        { requested: '/de/bateaux-mouches-gegen-bateaux-parisiens-dinner-kreuzfahrt-nebeneinander-vergleich', target: '/bateaux-mouches-vs-bateaux-parisiens-dinner-cruise-side-by-side-comparison' }
      ];

      for (const journey of legacyJourneys) {
        const route = evaluateVercelRoute(journey.requested, config);
        assert.strictEqual(route.action, 'redirect');
        assert.strictEqual(route.destination, journey.target);
        assert.ok(route.permanent);
      }
    });

    it('4.5 Scenario 5: Dynamic Filter Re-Rendering and Batch CTA Link Decoration', () => {
      const gclid = 'Cj0KCQ_batch_mutation_stress_test';
      const initialHtml = `<div id="filter-container"></div>`;
      const { window, document } = initDomEnv(`https://thecruisedetective.com/?gclid=${gclid}`, initialHtml);

      const container = document.querySelector('#filter-container');

      // Inject 20 dynamic comparison cards simultaneously (simulating interactive category filter)
      for (let i = 0; i < 20; i++) {
        const card = document.createElement('div');
        card.className = 'boat-card';
        card.innerHTML = `
          <h3>Boat #${i}</h3>
          <a class="cta-link" href="https://www.tiqets.com/en/things-to-do-in-paris-c66746/p${1000 + i}?partner=${LOCKED_TIQETS_PARTNER_ID}&tq_campaign=filter-view-${i}">Book #${i}</a>
        `;
        container.appendChild(card);
      }

      // Manually trigger scan or let MutationObserver catch it
      window.CruiseDetectiveTracking?.scanAndDecorate();

      const links = document.querySelectorAll('.cta-link');
      assert.strictEqual(links.length, 20);
      for (const l of links) {
        assert.ok(l.href.includes(`partner=${LOCKED_TIQETS_PARTNER_ID}`), 'Dynamic link must preserve partner ID');
        assert.ok(l.href.includes(gclid), 'Dynamic link must be decorated with GCLID');
      }
    });

  });

});
