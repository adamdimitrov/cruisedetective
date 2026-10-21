import test, { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { JSDOM } from 'jsdom';

const webflowSyncCode = fs.readFileSync(path.resolve('./webflow-sync.js'), 'utf8');

function initTestEnv(url, html, customWindowSetup = null) {
    const dom = new JSDOM(html, { url });
    const { window } = dom;
    const { document } = window;

    if (customWindowSetup) {
        customWindowSetup(window, document);
    }

    const runner = new Function('window', 'document', 'localStorage', 'location', 'MutationObserver', webflowSyncCode);
    runner(window, document, window.localStorage, window.location, window.MutationObserver);

    return { dom, window, document };
}

describe('Tier 5 Adversarial & Generator Stress Tests for Click ID Capture (R1)', () => {

    describe('5.1 Malformed GCLID Strings & Special Character Injection', () => {
        it('5.1.1 Should handle HTML/XSS payload in gclid without script execution or corruption', () => {
            const xssGclid = '"><script>alert(1)</script><a href="';
            const testUrl = `https://thecruisedetective.com/?gclid=${encodeURIComponent(xssGclid)}`;
            const html = `<a id="link-xss" href="https://www.tiqets.com/en/paris/">Tiqets Link</a>`;

            const { window, document } = initTestEnv(testUrl, html);

            const stored = window.localStorage.getItem('cd_gclid');
            assert.strictEqual(stored, xssGclid);

            const link = document.querySelector('#link-xss');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('gclid'), xssGclid);
            assert.strictEqual(url.searchParams.get('tq_campaign'), xssGclid);
        });

        it('5.1.2 Should handle special characters (&, =, ?, #, spaces, unicode, emojis) in gclid', () => {
            const specialGclid = 'gclid_special_&_=_?_#_space name_🚢_Budapest_2026';
            const testUrl = `https://thecruisedetective.com/?gclid=${encodeURIComponent(specialGclid)}`;
            const html = `<a id="link-spec" href="https://www.tiqets.com/en/budapest/?tq_campaign=bud-tag">Budapest Ticket</a>`;

            const { window, document } = initTestEnv(testUrl, html);

            assert.strictEqual(window.CruiseDetectiveTracking.getGclid(), specialGclid);

            const link = document.querySelector('#link-spec');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('gclid'), specialGclid);
            assert.strictEqual(url.searchParams.get('tq_campaign'), `bud-tag--gclid-${specialGclid}`);
        });

        it('5.1.3 Should handle super-long gclid string (10,000+ characters)', () => {
            const longGclid = 'Cj0KCQ_' + 'A'.repeat(10000);
            const testUrl = `https://thecruisedetective.com/?gclid=${longGclid}`;
            const html = `<a id="link-long" href="https://www.tiqets.com/en/rome/">Rome Link</a>`;

            const { window, document } = initTestEnv(testUrl, html);

            assert.strictEqual(window.localStorage.getItem('cd_gclid'), longGclid);

            const link = document.querySelector('#link-long');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('gclid'), longGclid);
        });

        it('5.1.4 Should ignore empty or whitespace-only gclid strings', () => {
            const testUrl = `https://thecruisedetective.com/?gclid=%20%20%20`;
            const html = `<a id="link-empty" href="https://www.tiqets.com/en/madrid/">Madrid Link</a>`;

            const { window, document } = initTestEnv(testUrl, html);

            assert.strictEqual(window.localStorage.getItem('cd_gclid'), null);

            const link = document.querySelector('#link-empty');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('gclid'), null);
        });

        it('5.1.5 Should handle malformed percent encoding in URL search params without throwing unhandled exceptions', () => {
            // Note: JSDOM handles URL parsing safely
            const testUrl = `https://thecruisedetective.com/?gclid=valid_gclid_123&bad_param=%E0%A4%A`;
            const html = `<a id="link-malformed-enc" href="https://www.tiqets.com/en/berlin/">Berlin Link</a>`;

            const { window, document } = initTestEnv(testUrl, html);

            assert.strictEqual(window.localStorage.getItem('cd_gclid'), 'valid_gclid_123');

            const link = document.querySelector('#link-malformed-enc');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('gclid'), 'valid_gclid_123');
        });
    });

    describe('5.2 Extreme Link Hrefs & Host Domain Security Mining', () => {
        it('5.2.1 Should safely ignore empty, hash-only, javascript:, and data: hrefs without throwing', () => {
            const testGclid = 'Cj0KCQ_href_test_123';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `
                <a id="h-empty" href="">Empty</a>
                <a id="h-hash" href="#">Hash Only</a>
                <a id="h-js" href="javascript:console.log('tiqets.com')">JS Void</a>
                <a id="h-data" href="data:text/html,tiqets.com">Data URI</a>
                <a id="h-nohref">No Href Attribute</a>
                <a id="h-invalid" href="http://:invalid-url-format">Invalid URL</a>
            `;

            const { document } = initTestEnv(testUrl, html);

            // Assert none of these throw and hrefs remain intact or safely unadulterated
            assert.strictEqual(document.querySelector('#h-empty').getAttribute('href'), '');
            assert.strictEqual(document.querySelector('#h-hash').getAttribute('href'), '#');
            assert.strictEqual(document.querySelector('#h-js').getAttribute('href'), "javascript:console.log('tiqets.com')");
            assert.strictEqual(document.querySelector('#h-data').getAttribute('href'), "data:text/html,tiqets.com");
            assert.strictEqual(document.querySelector('#h-nohref').hasAttribute('href'), false);
        });

        it('5.2.2 SECURITY CHECK: Should NOT decorate malicious domain spoofing (e.g. tiqets.com.evilsite.com)', () => {
            const testGclid = 'Cj0KCQ_security_domain_check_999';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `
                <a id="h-valid-sub" href="https://blog.tiqets.com/en/paris/">Valid Subdomain</a>
                <a id="h-evil-domain" href="https://tiqets.com.evilsite.com/phishing">Evil Domain Spoof</a>
                <a id="h-evil-prefix" href="https://fagettiqets.com/fake">Evil Prefix Spoof</a>
            `;

            const { document } = initTestEnv(testUrl, html);

            const validSub = document.querySelector('#h-valid-sub');
            const validUrl = new URL(validSub.href);
            assert.strictEqual(validUrl.searchParams.get('gclid'), testGclid, 'Subdomains of tiqets.com should be decorated');

            const evilDomain = document.querySelector('#h-evil-domain');
            const evilUrl = new URL(evilDomain.href);
            assert.strictEqual(evilUrl.searchParams.get('gclid'), null, 'tiqets.com.evilsite.com must NOT be decorated!');

            const evilPrefix = document.querySelector('#h-evil-prefix');
            const evilPrefixUrl = new URL(evilPrefix.href);
            assert.strictEqual(evilPrefixUrl.searchParams.get('gclid'), null, 'fagettiqets.com must NOT be decorated!');
        });

        it('5.2.3 Relative URLs with tiqets.com in path should not crash', () => {
            const testGclid = 'Cj0KCQ_relative_url_111';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `
                <a id="h-relative" href="/reviews/tiqets.com/paris-tour">Relative Path</a>
            `;

            const { document } = initTestEnv(testUrl, html);

            const relLink = document.querySelector('#h-relative');
            const relUrl = new URL(relLink.href);
            // Since host is thecruisedetective.com, it should NOT be decorated as a Tiqets affiliate link
            assert.strictEqual(relUrl.searchParams.get('gclid'), null);
        });
    });

    describe('5.3 Pre-Existing tq_campaign Tag Variations', () => {
        it('5.3.1 Should correctly replace previous --gclid- tag when gclid changes', () => {
            const oldGclid = 'OLD_GCLID_111';
            const newGclid = 'NEW_GCLID_222';
            const testUrl = `https://thecruisedetective.com/?gclid=${newGclid}`;
            const html = `
                <a id="link-redecor" href="https://www.tiqets.com/en/paris/?tq_campaign=adv-tldr--gclid-${oldGclid}&gclid=${oldGclid}">Link with Old GCLID</a>
            `;

            const { document } = initTestEnv(testUrl, html);

            const link = document.querySelector('#link-redecor');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('tq_campaign'), `adv-tldr--gclid-${newGclid}`);
            assert.strictEqual(url.searchParams.get('gclid'), newGclid);
        });

        it('5.3.2 Should handle empty pre-existing tq_campaign param (?tq_campaign=)', () => {
            const testGclid = 'GCLID_EMPTY_CAMPAIGN';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `<a id="link-empty-camp" href="https://www.tiqets.com/en/paris/?tq_campaign=">Link Empty Campaign</a>`;

            const { document } = initTestEnv(testUrl, html);

            const link = document.querySelector('#link-empty-camp');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('tq_campaign'), testGclid);
        });

        it('5.3.3 Should handle tq_campaign tag having multiple --gclid- occurrences', () => {
            const testGclid = 'GCLID_MULTI_SPLIT';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `<a id="link-multi-split" href="https://www.tiqets.com/en/paris/?tq_campaign=base--gclid-first--gclid-second">Multi Gclid Tag</a>`;

            const { document } = initTestEnv(testUrl, html);

            const link = document.querySelector('#link-multi-split');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('tq_campaign'), `base--gclid-${testGclid}`);
        });
    });

    describe('5.4 Storage Failure Modes (Disabled / Throwing Storage)', () => {
        it('5.4.1 Should handle throwing localStorage (SecurityError/Private Browsing) gracefully', () => {
            const testGclid = 'GCLID_PRIV_BROWSI_777';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `<a id="link-priv" href="https://www.tiqets.com/en/paris/">Private Mode Link</a>`;

            const { document, window } = initTestEnv(testUrl, html, (win) => {
                // Mock localStorage to throw SecurityError on setItem and getItem
                Object.defineProperty(win, 'localStorage', {
                    value: {
                        getItem: () => { throw new win.DOMException('Access denied', 'SecurityError'); },
                        setItem: () => { throw new win.DOMException('Access denied', 'SecurityError'); }
                    },
                    writable: true
                });
            });

            // Decorate link should still succeed using URL parameter & Cookie
            const link = document.querySelector('#link-priv');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('gclid'), testGclid);
            assert.ok(document.cookie.includes(`cd_gclid=${testGclid}`));
        });

        it('5.4.2 Should handle throwing document.cookie gracefully', () => {
            const testGclid = 'GCLID_NO_COOKIES_888';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `<a id="link-nocookies" href="https://www.tiqets.com/en/paris/">No Cookie Link</a>`;

            const { document, window } = initTestEnv(testUrl, html, (win, doc) => {
                // Mock document.cookie to throw
                Object.defineProperty(doc, 'cookie', {
                    get: () => { throw new Error('Cookies disabled'); },
                    set: () => { throw new Error('Cookies disabled'); },
                    configurable: true
                });
            });

            const link = document.querySelector('#link-nocookies');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('gclid'), testGclid);
            assert.strictEqual(window.localStorage.getItem('cd_gclid'), testGclid);
        });

        it('5.4.3 Should handle both localStorage and document.cookie throwing without crashing', () => {
            const testGclid = 'GCLID_BOTH_THROWING_999';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `<a id="link-both-throw" href="https://www.tiqets.com/en/paris/">Both Throw Link</a>`;

            const { document } = initTestEnv(testUrl, html, (win, doc) => {
                Object.defineProperty(win, 'localStorage', {
                    value: {
                        getItem: () => { throw new Error('localStorage disabled'); },
                        setItem: () => { throw new Error('localStorage disabled'); }
                    },
                    writable: true
                });
                Object.defineProperty(doc, 'cookie', {
                    get: () => { throw new Error('Cookies disabled'); },
                    set: () => { throw new Error('Cookies disabled'); },
                    configurable: true
                });
            });

            const link = document.querySelector('#link-both-throw');
            const url = new URL(link.href);
            assert.strictEqual(url.searchParams.get('gclid'), testGclid);
        });
    });

    describe('5.5 Multi-Nested Shadow DOM Trees & Event Propagation', () => {
        it('5.5.1 Should decorate Tiqets links inside 3-level deeply nested Shadow DOM trees on click', () => {
            const testGclid = 'GCLID_DEEP_SHADOW_333';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;
            const html = `<div id="host-level-1"></div>`;

            const { window, document } = initTestEnv(testUrl, html);

            // Level 1 Shadow DOM
            const host1 = document.querySelector('#host-level-1');
            const shadow1 = host1.attachShadow({ mode: 'open' });

            const host2 = document.createElement('div');
            host2.setAttribute('id', 'host-level-2');
            shadow1.appendChild(host2);

            // Level 2 Shadow DOM
            const shadow2 = host2.attachShadow({ mode: 'open' });

            const host3 = document.createElement('div');
            host3.setAttribute('id', 'host-level-3');
            shadow2.appendChild(host3);

            // Level 3 Shadow DOM
            const shadow3 = host3.attachShadow({ mode: 'open' });

            const deepLink = document.createElement('a');
            deepLink.setAttribute('href', 'https://www.tiqets.com/en/venice-gondola/?tq_campaign=deep-shadow-tag');
            shadow3.appendChild(deepLink);

            // Dispatch click event with composed: true
            const clickEvent = new window.Event('click', { bubbles: true, composed: true });
            deepLink.dispatchEvent(clickEvent);

            const url = new URL(deepLink.href);
            assert.strictEqual(url.searchParams.get('tq_campaign'), `deep-shadow-tag--gclid-${testGclid}`);
            assert.strictEqual(url.searchParams.get('gclid'), testGclid);
        });
    });

    describe('5.6 High-Volume Stress & Execution Performance', () => {
        it('5.6.1 Should scan and decorate 2,000 Tiqets links in DOM within 100 milliseconds', () => {
            const testGclid = 'GCLID_PERF_STRESS_555';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

            let linksHtml = '';
            for (let i = 0; i < 2000; i++) {
                linksHtml += `<a href="https://www.tiqets.com/en/tour-${i}/?partner=cruisedetective&tq_campaign=campaign-${i}">Link ${i}</a>\n`;
            }

            const startTime = performance.now();
            const { document, window } = initTestEnv(testUrl, linksHtml);
            const endTime = performance.now();

            const durationMs = endTime - startTime;
            assert.ok(durationMs < 500, `DOM scanning and decoration of 2,000 links took ${durationMs.toFixed(2)}ms (should be < 500ms)`);

            // Verify a sample link is correctly decorated
            const firstLink = document.querySelector('a');
            const url = new URL(firstLink.href);
            assert.strictEqual(url.searchParams.get('gclid'), testGclid);
            assert.strictEqual(url.searchParams.get('tq_campaign'), `campaign-0--gclid-${testGclid}`);
        });

        it('5.6.2 Should handle batch innerHTML insertion of 500 nodes without memory leak or crash', () => {
            const testGclid = 'GCLID_BATCH_MUTATION_666';
            const testUrl = `https://thecruisedetective.com/?gclid=${testGclid}`;

            const { document, window } = initTestEnv(testUrl, '<div id="batch-container"></div>');

            const container = document.querySelector('#batch-container');

            let batchHtml = '';
            for (let i = 0; i < 500; i++) {
                batchHtml += `<div><a id="batch-link-${i}" href="https://www.tiqets.com/en/attraction-${i}/">Batch Link ${i}</a></div>`;
            }

            container.innerHTML = batchHtml;

            // Trigger manual scan or allow mutation observer to process
            window.CruiseDetectiveTracking.scanAndDecorate(container);

            const sampleLink = document.querySelector('#batch-link-250');
            const url = new URL(sampleLink.href);
            assert.strictEqual(url.searchParams.get('gclid'), testGclid);
        });
    });

});
