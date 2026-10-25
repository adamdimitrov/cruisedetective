import test, { describe, it, beforeEach, afterEach } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { JSDOM } from 'jsdom';

const webflowSyncCode = fs.readFileSync(path.resolve('./webflow-sync.js'), 'utf8');
const originalFetch = globalThis.fetch;

beforeEach(() => {
  globalThis.fetch = originalFetch;
  if (typeof globalThis.localStorage !== 'undefined' && globalThis.localStorage.clear) {
    globalThis.localStorage.clear();
  }
  if (typeof globalThis.document !== 'undefined') {
    globalThis.document.cookie = 'cd_gclid=; max-age=0; path=/;';
    globalThis.document.cookie = 'cd_gclid_exp=; max-age=0; path=/;';
  }
});

afterEach(() => {
  globalThis.fetch = originalFetch;
  if (typeof globalThis.localStorage !== 'undefined' && globalThis.localStorage.clear) {
    globalThis.localStorage.clear();
  }
  if (typeof globalThis.document !== 'undefined') {
    globalThis.document.cookie = 'cd_gclid=; max-age=0; path=/;';
    globalThis.document.cookie = 'cd_gclid_exp=; max-age=0; path=/;';
  }
});

function initTestEnv(url, html = '') {
  const dom = new JSDOM(html, { url });
  const { window } = dom;
  const { document } = window;

  window.localStorage.clear();
  document.cookie = 'cd_gclid=; max-age=0; path=/;';
  document.cookie = 'cd_gclid_exp=; max-age=0; path=/;';

  // Execute production webflow-sync.js within the JSDOM window context
  const runner = new Function('window', 'document', 'localStorage', 'location', 'MutationObserver', webflowSyncCode);
  runner(window, document, window.localStorage, window.location, window.MutationObserver);

  return { dom, window, document };
}

describe('Click ID Capture (R1) Unit & Integration Test Suite', () => {

  describe('Tier 1: Primary Behavior (Happy Path)', () => {

    it('1.1 Should detect gclid from URL, store in localStorage (with ~90-day exp) and cookie', () => {
      const initialHtml = `<a id="link1" href="https://www.tiqets.com/en/paris-c66746/?partner=deals.cruisedetective.com&tq_campaign=adv-tldr">Tiqets Link</a>`;
      const testGclid = 'Cj0KCQ_tier1_url_gclid_12345';
      const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

      const { window, document } = initTestEnv(testUrl, initialHtml);

      // Verify localStorage persistence
      const storedGclid = window.localStorage.getItem('cd_gclid');
      assert.strictEqual(storedGclid, testGclid, 'localStorage cd_gclid must match URL gclid');

      const storedExp = window.localStorage.getItem('cd_gclid_exp');
      assert.ok(storedExp, 'localStorage cd_gclid_exp must be set');
      const expTime = parseInt(storedExp, 10);
      const now = Date.now();
      const expectedMinExp = now + (89 * 24 * 60 * 60 * 1000);
      const expectedMaxExp = now + (91 * 24 * 60 * 60 * 1000);
      assert.ok(expTime >= expectedMinExp && expTime <= expectedMaxExp, 'cd_gclid_exp should be set ~90 days in future');

      // Verify Cookie persistence
      assert.ok(document.cookie.includes(`cd_gclid=${testGclid}`), 'Cookie cd_gclid must contain active gclid');

      // Verify Window Export
      assert.ok(window.CruiseDetectiveTracking, 'window.CruiseDetectiveTracking must be defined');
      assert.strictEqual(window.CruiseDetectiveTracking.getGclid(), testGclid);
    });

    it('1.2 Should decorate Tiqets links with tq_campaign (<base>--gclid-<gclid>), gclid, click_id, and subid', () => {
      const html = `
        <a id="link-base" href="https://www.tiqets.com/en/paris-c66746/?partner=deals.cruisedetective.com&tq_campaign=adv-tldr">Link with Base Tag</a>
        <a id="link-nobase" href="https://www.tiqets.com/en/rome-c66746/?partner=deals.cruisedetective.com">Link without Campaign Tag</a>
      `;
      const testGclid = 'Cj0KCQ_tier1_decor_67890';
      const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

      const { document } = initTestEnv(testUrl, html);

      const linkBase = document.querySelector('#link-base');
      const urlBase = new URL(linkBase.href);
      assert.strictEqual(urlBase.searchParams.get('tq_campaign'), `adv-tldr--gclid-${testGclid}`);
      assert.strictEqual(urlBase.searchParams.get('gclid'), testGclid);
      assert.strictEqual(urlBase.searchParams.get('click_id'), testGclid);
      assert.strictEqual(urlBase.searchParams.get('subid'), testGclid);
      assert.strictEqual(urlBase.searchParams.get('partner'), 'deals.cruisedetective.com');

      const linkNoBase = document.querySelector('#link-nobase');
      const urlNoBase = new URL(linkNoBase.href);
      assert.strictEqual(urlNoBase.searchParams.get('tq_campaign'), testGclid);
      assert.strictEqual(urlNoBase.searchParams.get('gclid'), testGclid);
      assert.strictEqual(urlNoBase.searchParams.get('click_id'), testGclid);
      assert.strictEqual(urlNoBase.searchParams.get('subid'), testGclid);
    });

  });

  describe('Tier 2: Boundary & Edge Cases', () => {

    it('2.1 Should be idempotent and avoid duplicating --gclid- tags when scanAndDecorate is run multiple times', () => {
      const html = `<a id="link-pre" href="https://www.tiqets.com/en/paris/?tq_campaign=adv-tldr--gclid-Cj0KCQ_idempotent&gclid=Cj0KCQ_idempotent">Pre-decorated Link</a>`;
      const testGclid = 'Cj0KCQ_idempotent';
      const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

      const { window, document } = initTestEnv(testUrl, html);

      // Re-run scanAndDecorate manually
      window.CruiseDetectiveTracking.scanAndDecorate();
      window.CruiseDetectiveTracking.scanAndDecorate();

      const link = document.querySelector('#link-pre');
      const url = new URL(link.href);
      assert.strictEqual(url.searchParams.get('tq_campaign'), `adv-tldr--gclid-${testGclid}`);
      const matches = (link.href.match(/--gclid-/g) || []).length;
      assert.strictEqual(matches, 1, 'Should contain exactly one --gclid- tag');
    });

    it('2.2 Should preserve hash fragments in URLs during link decoration', () => {
      const html = `<a id="link-hash" href="https://www.tiqets.com/en/barcelona/?tq_campaign=barcelona-pass#reviews">Link with Hash</a>`;
      const testGclid = 'Cj0KCQ_hash_test';
      const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

      const { document } = initTestEnv(testUrl, html);

      const link = document.querySelector('#link-hash');
      assert.ok(link.href.endsWith('#reviews'), 'Hash fragment #reviews must be preserved');
      const url = new URL(link.href);
      assert.strictEqual(url.searchParams.get('tq_campaign'), `barcelona-pass--gclid-${testGclid}`);
    });

    it('2.3 Should leave non-Tiqets links untouched', () => {
      const html = `<a id="link-external" href="https://example.com/tiqets.com">External Link</a>`;
      const testGclid = 'Cj0KCQ_external_test';
      const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

      const { document } = initTestEnv(testUrl, html);

      const link = document.querySelector('#link-external');
      assert.strictEqual(link.href, 'https://example.com/tiqets.com');
    });

    it('2.4 Should handle empty or whitespace gclid parameters gracefully', () => {
      const html = `<a id="link1" href="https://www.tiqets.com/en/paris/">Tiqets Link</a>`;
      const testUrl = `https://thecruisedetective.com/?gclid=%20%20`;

      const { window, document } = initTestEnv(testUrl, html);

      assert.strictEqual(window.localStorage.getItem('cd_gclid'), null);
      assert.strictEqual(window.CruiseDetectiveTracking.getGclid(), null);
      const link = document.querySelector('#link1');
      assert.strictEqual(link.href, 'https://www.tiqets.com/en/paris/');
    });

    it('2.5 Should return null and clear effective gclid when stored localStorage timestamp is expired', () => {
      const testGclid = 'Cj0KCQ_expired_gclid';
      const pageUrl = 'https://thecruisedetective.com/expired';
      const html = `<a id="link-exp" href="https://www.tiqets.com/en/venice/">Expired Ticket</a>`;

      const dom = new JSDOM(html, { url: pageUrl });
      const { window } = dom;
      const { document } = window;

      // Seed expired timestamp (1 second in past)
      window.localStorage.setItem('cd_gclid', testGclid);
      window.localStorage.setItem('cd_gclid_exp', (Date.now() - 1000).toString());

      const runner = new Function('window', 'document', 'localStorage', 'location', 'MutationObserver', webflowSyncCode);
      runner(window, document, window.localStorage, window.location, window.MutationObserver);

      assert.strictEqual(window.CruiseDetectiveTracking.getGclid(), null);
      const link = document.querySelector('#link-exp');
      const url = new URL(link.href);
      assert.strictEqual(url.searchParams.get('gclid'), null);
    });

  });

  describe('Tier 3: Cross-Page Persistence & Storage Fallback', () => {

    it('3.1 Should fallback to localStorage on subsequent navigation without ?gclid in URL', () => {
      const testGclid = 'Cj0KCQ_cross_page_local_storage';
      const pageUrl = 'https://thecruisedetective.com/dinner-cruises';
      const html = `<a id="link-sub" href="https://www.tiqets.com/en/paris/">Dinner Cruise Ticket</a>`;

      const dom = new JSDOM(html, { url: pageUrl });
      const { window } = dom;
      const { document } = window;

      // Pre-seed valid localStorage
      window.localStorage.setItem('cd_gclid', testGclid);
      window.localStorage.setItem('cd_gclid_exp', (Date.now() + 864000000).toString());

      const runner = new Function('window', 'document', 'localStorage', 'location', 'MutationObserver', webflowSyncCode);
      runner(window, document, window.localStorage, window.location, window.MutationObserver);

      assert.strictEqual(window.CruiseDetectiveTracking.getGclid(), testGclid);
      const link = document.querySelector('#link-sub');
      const url = new URL(link.href);
      assert.strictEqual(url.searchParams.get('gclid'), testGclid);
    });

    it('3.2 Should fallback to Cookie and repopulate localStorage when localStorage is empty', () => {
      const testGclid = 'Cj0KCQ_cookie_fallback_gclid';
      const pageUrl = 'https://thecruisedetective.com/sightseeing';
      const html = `<a id="link-cookie" href="https://www.tiqets.com/en/amsterdam/">Sightseeing Ticket</a>`;

      const dom = new JSDOM(html, { url: pageUrl });
      const { window } = dom;
      const { document } = window;

      // Pre-seed Cookie only
      document.cookie = `cd_gclid=${testGclid}; max-age=7776000; path=/`;

      const runner = new Function('window', 'document', 'localStorage', 'location', 'MutationObserver', webflowSyncCode);
      runner(window, document, window.localStorage, window.location, window.MutationObserver);

      assert.strictEqual(window.CruiseDetectiveTracking.getGclid(), testGclid);
      assert.strictEqual(window.localStorage.getItem('cd_gclid'), testGclid);
      assert.ok(window.localStorage.getItem('cd_gclid_exp'));

      const link = document.querySelector('#link-cookie');
      const url = new URL(link.href);
      assert.strictEqual(url.searchParams.get('gclid'), testGclid);
    });

  });

  describe('Tier 4: Real-World Browser Flow (DOM Mutation & Shadow DOM)', () => {

    it('4.1 Should automatically decorate dynamically inserted Tiqets links via MutationObserver', () => {
      const testGclid = 'Cj0KCQ_mutation_observer_test';
      const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

      const { window, document } = initTestEnv(testUrl, '<div>Initial Page Content</div>');

      // Dynamically add a container with a Tiqets link
      const container = document.createElement('div');
      container.innerHTML = `<a id="dynamic-link" href="https://www.tiqets.com/en/london-c66746/?tq_campaign=london-pass">Dynamic Link</a>`;
      document.body.appendChild(container);

      const dynamicLink = document.querySelector('#dynamic-link');
      assert.ok(dynamicLink, 'Dynamic link must exist');

      const url = new URL(dynamicLink.href);
      assert.strictEqual(url.searchParams.get('tq_campaign'), `london-pass--gclid-${testGclid}`);
      assert.strictEqual(url.searchParams.get('gclid'), testGclid);
      assert.strictEqual(url.searchParams.get('click_id'), testGclid);
      assert.strictEqual(url.searchParams.get('subid'), testGclid);
    });

    it('4.2 Should decorate Tiqets links inside Shadow DOM embeds upon click interaction', () => {
      const testGclid = 'Cj0KCQ_shadow_dom_test';
      const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

      const { window, document } = initTestEnv(testUrl, '<div id="shadow-host"></div>');

      const host = document.querySelector('#shadow-host');
      const shadow = host.attachShadow({ mode: 'open' });

      const shadowLink = document.createElement('a');
      shadowLink.setAttribute('id', 'shadow-tiqets-link');
      shadowLink.setAttribute('href', 'https://www.tiqets.com/en/vienna/?tq_campaign=vienna-attraction');
      shadowLink.textContent = 'Shadow Tiqets Link';
      shadow.appendChild(shadowLink);

      // Dispatch click event simulating user click on Shadow DOM link
      const clickEvent = new window.Event('click', { bubbles: true, composed: true });
      shadowLink.dispatchEvent(clickEvent);

      const urlAfter = new URL(shadowLink.href);
      assert.strictEqual(urlAfter.searchParams.get('tq_campaign'), `vienna-attraction--gclid-${testGclid}`);
      assert.strictEqual(urlAfter.searchParams.get('gclid'), testGclid);
      assert.strictEqual(urlAfter.searchParams.get('click_id'), testGclid);
      assert.strictEqual(urlAfter.searchParams.get('subid'), testGclid);
    });

  });

});
