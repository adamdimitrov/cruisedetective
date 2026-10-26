/**
 * E2E Programmatic Verification Suite: Paris Dinner Cruises Article Overhaul
 * 
 * Verifies all Acceptance Criteria across deliverables 01 through 04:
 *   - Deliverable 01: 01_editorial_content_expansion.md (R1)
 *   - Deliverable 02: 02_semantic_comparison_table.html (R2)
 *   - Deliverable 03: 03_rich_json_ld_schema.html (R3)
 *   - Deliverable 04: 04_webflow_component_blocks.html (R4)
 * 
 * Target Environment: Node.js standard runtime (ESM supported)
 * Dependencies: node:test, node:assert, node:fs, node:path, node:url
 */

import { describe, it } from 'node:test';
import assert from 'node:assert';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const BASE_DIR = path.resolve(__dirname);
const FILE_01 = path.join(BASE_DIR, '01_editorial_content_expansion.md');
const FILE_02 = path.join(BASE_DIR, '02_semantic_comparison_table.html');
const FILE_03 = path.join(BASE_DIR, '03_rich_json_ld_schema.html');
const FILE_04 = path.join(BASE_DIR, '04_webflow_component_blocks.html');

// Common Emoji Detection Regex (matches standard, supplemental, and symbol emojis)
const EMOJI_REGEX = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1FA00}-\u{1FAFF}\u{1F1E6}-\u{1F1FF}]/u;

// Helper: Extract all markdown headings (#, ##, ###, ####)
function extractMarkdownHeadings(content) {
  return content
    .split('\n')
    .filter(line => /^#{1,6}\s+/.test(line.trim()))
    .map(line => line.replace(/^#{1,6}\s+/, '').trim());
}

// Helper: Extract all HTML headings (h1, h2, h3, h4, h5, h6)
function extractHtmlHeadings(content) {
  const matches = [...content.matchAll(/<h([1-6])[^>]*>([\s\S]*?)<\/h\1>/gi)];
  return matches.map(m => m[2].replace(/<[^>]+>/g, '').trim());
}

// Helper: Extract all CSS selectors from <style> blocks
function extractCssSelectors(content) {
  const styleBlocks = [...content.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)].map(m => m[1]);
  const selectors = [];

  for (const block of styleBlocks) {
    // Strip comments
    const clean = block.replace(/\/\*[\s\S]*?\*\//g, '');
    // Match rule blocks: selector { declarations }
    const rules = clean.split('}');
    for (const rule of rules) {
      if (!rule.includes('{')) continue;
      let selPart = rule.split('{')[0].trim();
      // Handle nested @media
      if (selPart.includes('@media')) {
        const parts = selPart.split('{');
        selPart = parts[parts.length - 1].trim();
      }
      if (!selPart || selPart.startsWith('@')) continue;

      // Split multiple selectors
      const individualSelectors = selPart.split(',').map(s => s.trim()).filter(Boolean);
      selectors.push(...individualSelectors);
    }
  }
  return selectors;
}

// ============================================================================
// SUITE 1: Deliverables Existence and Baseline Size Verification
// ============================================================================
describe('Suite 1: Deliverables Existence and Baseline Size', () => {
  it('01_editorial_content_expansion.md exists and contains comprehensive editorial text (>50KB)', () => {
    assert.ok(fs.existsSync(FILE_01), `Missing deliverable: ${FILE_01}`);
    const stat = fs.statSync(FILE_01);
    assert.ok(stat.size > 50000, `01_editorial_content_expansion.md is only ${stat.size} bytes (expected > 50000)`);
  });

  it('02_semantic_comparison_table.html exists and contains complete comparison matrix (>20KB)', () => {
    assert.ok(fs.existsSync(FILE_02), `Missing deliverable: ${FILE_02}`);
    const stat = fs.statSync(FILE_02);
    assert.ok(stat.size > 20000, `02_semantic_comparison_table.html is only ${stat.size} bytes (expected > 20000)`);
  });

  it('03_rich_json_ld_schema.html exists and contains structured data script (>8KB)', () => {
    assert.ok(fs.existsSync(FILE_03), `Missing deliverable: ${FILE_03}`);
    const stat = fs.statSync(FILE_03);
    assert.ok(stat.size > 8000, `03_rich_json_ld_schema.html is only ${stat.size} bytes (expected > 8000)`);
  });

  it('04_webflow_component_blocks.html exists and contains component library (>50KB)', () => {
    assert.ok(fs.existsSync(FILE_04), `Missing deliverable: ${FILE_04}`);
    const stat = fs.statSync(FILE_04);
    assert.ok(stat.size > 50000, `04_webflow_component_blocks.html is only ${stat.size} bytes (expected > 50000)`);
  });
});

// ============================================================================
// SUITE 2: Editorial Content & Culinary Depth Rigor (Deliverable 01)
// ============================================================================
describe('Suite 2: Editorial Content & Culinary Depth Rigor (Deliverable 01)', () => {
  const content = fs.readFileSync(FILE_01, 'utf-8');

  it('Mandatory heading rule: exactly ZERO emoji characters in any heading tag (#, ##, ###, ####)', () => {
    const headings = extractMarkdownHeadings(content);
    assert.ok(headings.length > 50, `Expected >50 headings in article, found ${headings.length}`);
    const emojiHeadings = headings.filter(h => EMOJI_REGEX.test(h));
    assert.strictEqual(
      emojiHeadings.length,
      0,
      `Found ${emojiHeadings.length} heading(s) containing forbidden emojis:\n${emojiHeadings.join('\n')}`
    );
  });

  it('All 10 dinner cruise operators have dedicated numbered H2 review sections', () => {
    const requiredBoats = [
      { num: 1, name: 'Bateaux Mouches' },
      { num: 2, name: 'Bateaux Parisiens' },
      { num: 3, name: 'Paris City Vision' },
      { num: 4, name: 'Paris en Sc' }, // matches Scène / Scene
      { num: 5, name: 'Le Diamant Bleu' },
      { num: 6, name: 'Trattoria en Seine' },
      { num: 7, name: 'Capitaine Fracasse' },
      { num: 8, name: 'Maxim' },
      { num: 9, name: 'Ducasse' },
      { num: 10, name: 'Paris City Vision Early Sunset' }
    ];

    for (const boat of requiredBoats) {
      const headingPattern = new RegExp(`##\\s+${boat.num}\\.\\s+.*${boat.name}`, 'i');
      assert.ok(
        headingPattern.test(content),
        `Missing dedicated H2 review section for Boat #${boat.num} (${boat.name})`
      );
    }
  });

  it('Every boat review section includes dedicated course-by-course dish assessments', () => {
    // Split article into boat review sections
    const boatSections = content.split(/## (?=\d+\.)/).slice(1, 11);
    assert.strictEqual(boatSections.length, 10, 'Expected exactly 10 boat review sections');

    // Culinary terms: starters/appetizers, mains, desserts, wine, specific tasting notes
    const culinaryKeywords = /(course|starter|entrée|main|dessert|tasting|menu|chef|dish|pasta|carpaccio|scallop|veal|profiterole|chocolate|duckling|sauce|wine|champagne)/i;

    boatSections.forEach((section, index) => {
      const boatNum = index + 1;
      const firstLine = section.split('\n')[0];
      assert.ok(
        culinaryKeywords.test(section),
        `Boat #${boatNum} (${firstLine}) lacks granular course-by-course culinary dish assessments`
      );
    });
  });

  it('Every boat review section documents specific seating tier trade-offs and sightline realities', () => {
    const boatSections = content.split(/## (?=\d+\.)/).slice(1, 11);
    // Seating terms: window vs central, tiers, surcharge, upper deck, reflections, sightlines, acoustics
    const seatingKeywords = /(seating|tier|window|table|sightline|aisle|central|deck|rooftop|reflection|terrace|glare|condensation|acoustic|spacing)/i;

    boatSections.forEach((section, index) => {
      const boatNum = index + 1;
      const firstLine = section.split('\n')[0];
      assert.ok(
        seatingKeywords.test(section),
        `Boat #${boatNum} (${firstLine}) lacks dedicated seating tier and sightline breakdown`
      );
    });
  });

  it('Includes comprehensive traveler logistics FAQ sections covering all core booking questions', () => {
    const faqTopics = [
      { name: 'Dress Code', pattern: /dress\s*code/i },
      { name: 'Eiffel Tower Sparkle Timing', pattern: /sparkle/i },
      { name: 'Planning Proposals / Anniversaries', pattern: /proposal|anniversary|celebrat/i },
      { name: 'Cancellation & Refund Policies', pattern: /cancellation|refund/i }
    ];

    for (const topic of faqTopics) {
      assert.ok(
        topic.pattern.test(content),
        `Article FAQ is missing essential logistics section for: ${topic.name}`
      );
    }
  });
});

// ============================================================================
// SUITE 3: Affiliate Link Integrity & Revenue Protection (Deliverables 01 & 02)
// ============================================================================
describe('Suite 3: Affiliate Link Integrity & Revenue Protection', () => {
  const content01 = fs.readFileSync(FILE_01, 'utf-8');
  const content02 = fs.readFileSync(FILE_02, 'utf-8');

  it('Strict Revenue Protection: Sightseeing ticket p973977 is NEVER linked in place of dinner cruise', () => {
    assert.strictEqual(
      content01.includes('973977'),
      false,
      'CRITICAL REVENUE LEAK: Forbidden sightseeing product p973977 found in 01_editorial_content_expansion.md'
    );
    assert.strictEqual(
      content02.includes('973977'),
      false,
      'CRITICAL REVENUE LEAK: Forbidden sightseeing product p973977 found in 02_semantic_comparison_table.html'
    );
  });

  it('Strict Dead Link Prevention: Dead Tiqets PCV redirect p1023747 is strictly eliminated', () => {
    assert.strictEqual(
      content01.includes('1023747'),
      false,
      'BROKEN LINK: Dead Tiqets product p1023747 found in 01_editorial_content_expansion.md'
    );
    assert.strictEqual(
      content02.includes('1023747'),
      false,
      'BROKEN LINK: Dead Tiqets product p1023747 found in 02_semantic_comparison_table.html'
    );
  });

  it('Bateaux Mouches correctly links to Tiqets product p982924 with partner thecruisedetective.com-176436', () => {
    const bmPattern = /https:\/\/www\.tiqets\.com\/[^\s\)]*p982924[^\s\)]*partner=thecruisedetective\.com-176436/;
    assert.ok(bmPattern.test(content01), '01 is missing verified Tiqets affiliate link for Bateaux Mouches (p982924)');
    assert.ok(bmPattern.test(content02), '02 is missing verified Tiqets affiliate link for Bateaux Mouches (p982924)');
  });

  it('Bateaux Parisiens correctly links to Gourmet Dinner Tiqets product p974358 with partner thecruisedetective.com-176436', () => {
    const bpPattern = /https:\/\/www\.tiqets\.com\/[^\s\)]*p974358[^\s\)]*partner=thecruisedetective\.com-176436/;
    assert.ok(bpPattern.test(content01), '01 is missing verified Tiqets dinner link for Bateaux Parisiens (p974358)');
    assert.ok(bpPattern.test(content02), '02 is missing verified Tiqets dinner link for Bateaux Parisiens (p974358)');
  });

  it('Paris City Vision / La Marina correctly links directly to GetYourGuide product t53306 with partner YS414AJ', () => {
    const pcvPattern = /https:\/\/www\.getyourguide\.com\/[^\s\)]*t53306[^\s\)]*partner_id=YS414AJ/;
    assert.ok(pcvPattern.test(content01), '01 is missing verified GetYourGuide affiliate link for PCV (t53306)');
    assert.ok(pcvPattern.test(content02), '02 is missing verified GetYourGuide affiliate link for PCV (t53306)');
  });

  it('All HTML comparison table affiliate links enforce target="_blank" and rel="noopener"', () => {
    const linkTags = [...content02.matchAll(/<a\b[^>]*href=["'][^"']*(?:tiqets|getyourguide)[^"']*["'][^>]*>/gi)];
    assert.ok(linkTags.length >= 5, `Expected at least 5 affiliate links in table, found ${linkTags.length}`);
    for (const tag of linkTags) {
      assert.ok(
        tag[0].includes('target="_blank"'),
        `Affiliate link missing target="_blank": ${tag[0]}`
      );
      assert.ok(
        tag[0].includes('rel="noopener"'),
        `Affiliate link missing rel="noopener": ${tag[0]}`
      );
    }
  });
});

// ============================================================================
// SUITE 4: Semantic Comparison Matrix Technical SEO & Accessibility (Deliverable 02)
// ============================================================================
describe('Suite 4: Semantic Comparison Matrix Technical SEO & Accessibility (Deliverable 02)', () => {
  const content = fs.readFileSync(FILE_02, 'utf-8');

  it('Contains valid semantic HTML5 table structure (table, caption, thead, tbody, th, td)', () => {
    assert.ok(content.includes('<table class="cd-comparison-table">'), 'Missing <table class="cd-comparison-table">');
    assert.ok(content.includes('<caption class="cd-sr-only">'), 'Missing accessible <caption class="cd-sr-only">');
    assert.ok(content.includes('<thead>') && content.includes('</thead>'), 'Missing semantic <thead>');
    assert.ok(content.includes('<tbody>') && content.includes('</tbody>'), 'Missing semantic <tbody>');
    assert.ok(content.includes('<th>') || content.includes('<th '), 'Missing semantic <th> headers');
    assert.ok(content.includes('<td>') || content.includes('<td '), 'Missing semantic <td> cells');
  });

  it('Strictly avoids all deprecated HTML presentation attributes', () => {
    const deprecatedAttrs = ['border=', 'cellpadding=', 'cellspacing=', 'bgcolor=', 'align='];
    for (const attr of deprecatedAttrs) {
      assert.strictEqual(
        content.toLowerCase().includes(attr),
        false,
        `Found deprecated HTML attribute "${attr}" in 02_semantic_comparison_table.html`
      );
    }
  });

  it('Features exactly 9 columns in the mandatory semantic order', () => {
    const expectedColumns = [
      'Boat Name & Rank',
      'Overall Rating & Review Volume',
      'Price Range',
      'Menu Courses & Quality',
      'Drinks Included',
      'Music Type',
      'Rooftop Deck',
      'Seating Highlights',
      'Direct Booking'
    ];

    const colHeaders = [...content.matchAll(/<th\b[^>]*scope="col"[^>]*>([\s\S]*?)<\/th>/gi)]
      .map(m => m[1].replace(/<[^>]+>/g, '').replace(/&amp;/g, '&').trim());

    assert.strictEqual(
      colHeaders.length,
      9,
      `Expected 9 columns, found ${colHeaders.length}: ${JSON.stringify(colHeaders)}`
    );

    expectedColumns.forEach((expected, i) => {
      assert.strictEqual(
        colHeaders[i],
        expected,
        `Column #${i + 1} mismatch: expected "${expected}", received "${colHeaders[i]}"`
      );
    });
  });

  it('Implements explicit row-level header associations (<th scope="row">) for all boats', () => {
    const rowHeaders = [...content.matchAll(/<th\b[^>]*scope="row"[^>]*>/gi)];
    assert.ok(
      rowHeaders.length >= 5,
      `Expected at least 5 <th scope="row"> row headers for boat rows, found ${rowHeaders.length}`
    );
  });

  it('Emphasizes #1 Tested Winner (Bateaux Mouches) with Gold Winner visual styling', () => {
    assert.ok(content.includes('cd-row-winner'), 'Missing .cd-row-winner class on Bateaux Mouches row');
    assert.ok(content.includes('cd-rank-gold'), 'Missing .cd-rank-gold badge for #1 winner');
    assert.ok(content.includes('cd-btn-bm'), 'Missing .cd-btn-bm gold CTA button styling');
  });

  it('Enforces zero emoji characters in table headings', () => {
    const headings = extractHtmlHeadings(content);
    assert.ok(headings.length >= 1, 'Expected at least 1 heading in table deliverable');
    const emojiHeadings = headings.filter(h => EMOJI_REGEX.test(h));
    assert.strictEqual(emojiHeadings.length, 0, `Table headings contain emojis: ${emojiHeadings.join(', ')}`);
  });

  it('All CSS classes and style rules are strictly scoped with .cd-* namespace', () => {
    const selectors = extractCssSelectors(content);
    assert.ok(selectors.length > 10, `Expected >10 CSS selectors, found ${selectors.length}`);

    const unscoped = selectors.filter(sel => {
      if (sel === ':root' || sel === ':host') return false;
      return !sel.includes('.cd-');
    });

    assert.strictEqual(
      unscoped.length,
      0,
      `Found unscoped CSS selectors in comparison table: ${unscoped.join(', ')}`
    );
  });
});

// ============================================================================
// SUITE 5: Rich JSON-LD Structured Data Schema Validation (Deliverable 03)
// ============================================================================
describe('Suite 5: Rich JSON-LD Structured Data Schema Validation (Deliverable 03)', () => {
  const rawHtml = fs.readFileSync(FILE_03, 'utf-8');

  it('Wrapped in a valid <script type="application/ld+json"> tag', () => {
    assert.ok(
      /<script\s+type=["']application\/ld\+json["']>[\s\S]*?<\/script>/i.test(rawHtml),
      '03_rich_json_ld_schema.html is missing outer <script type="application/ld+json"> wrapper'
    );
  });

  it('Parses as 100% valid JSON with zero syntax errors', () => {
    const scriptMatch = rawHtml.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/i);
    assert.ok(scriptMatch, 'Failed to extract JSON payload from script tag');
    let parsed;
    assert.doesNotThrow(() => {
      parsed = JSON.parse(scriptMatch[1]);
    }, 'JSON-LD schema failed JSON.parse validation');

    assert.strictEqual(parsed['@context'], 'https://schema.org', '@context must be "https://schema.org"');
    assert.ok(Array.isArray(parsed['@graph']), '@graph must be an array of schema entities');
    assert.strictEqual(parsed['@graph'].length, 3, '@graph must contain exactly 3 root entities (Article, ItemList, FAQPage)');
  });

  it('Article schema entity meets all E-E-A-T and technical SEO specifications', () => {
    const scriptMatch = rawHtml.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/i);
    const graph = JSON.parse(scriptMatch[1])['@graph'];
    const article = graph.find(e => e['@type'] === 'Article');
    assert.ok(article, 'Missing Article entity in @graph');

    // Headline verification
    assert.strictEqual(
      article.headline,
      '10 Best Seine Dinner Cruises in Paris in 2026 (Personally Tested)',
      'Article headline mismatch'
    );

    // Author E-E-A-T verification
    assert.ok(article.author, 'Article missing author entity');
    assert.strictEqual(article.author['@type'], 'Person', 'Author must be of type Person');
    assert.strictEqual(article.author.name, 'Adam Dimitrov', 'Author name must be Adam Dimitrov');
    assert.strictEqual(article.author.url, 'https://www.thecruisedetective.com/about', 'Author URL mismatch');
    assert.ok(article.author.jobTitle, 'Author missing jobTitle credential');

    // Publisher and logo verification (fixing the live-site empty logo bug)
    assert.ok(article.publisher, 'Article missing publisher entity');
    assert.strictEqual(article.publisher.name, 'The Cruise Detective', 'Publisher name mismatch');
    assert.ok(article.publisher.logo, 'Publisher missing logo object');
    assert.strictEqual(
      article.publisher.logo.url,
      'https://cdn.prod.website-files.com/6369a6904656314914c2bae2/6369a8d295be04a841e17ea5_logo.svg',
      'Publisher logo URL must point to valid absolute CDN SVG'
    );
    assert.ok(article.publisher.logo.width > 0 && article.publisher.logo.height > 0, 'Publisher logo dimensions missing');

    // Dates verification
    assert.ok(article.datePublished, 'Article missing datePublished');
    assert.ok(article.dateModified, 'Article missing dateModified');

    // Relationship link to ItemList
    const aboutList = Array.isArray(article.about) ? article.about : [article.about];
    const hasItemListRef = aboutList.some(item =>
      item && item['@id'] && item['@id'].includes('#itemlist')
    );
    assert.ok(hasItemListRef, 'Article must link to ItemList in "about" property');
  });

  it('ItemList schema entity contains all 10 ranked boats in strict sequential order', () => {
    const scriptMatch = rawHtml.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/i);
    const graph = JSON.parse(scriptMatch[1])['@graph'];
    const itemList = graph.find(e => e['@type'] === 'ItemList');
    assert.ok(itemList, 'Missing ItemList entity in @graph');

    assert.strictEqual(itemList.numberOfItems, 10, 'ItemList numberOfItems must equal 10');
    assert.strictEqual(itemList.itemListElement.length, 10, 'ItemList must contain exactly 10 itemListElement nodes');

    const expectedBoats = [
      'Bateaux Mouches',
      'Bateaux Parisiens',
      'Paris City Vision',
      'Paris en Scène',
      'Le Diamant Bleu',
      'Trattoria en Seine',
      'Capitaine Fracasse',
      'Maxim',
      'Ducasse',
      'Early'
    ];

    const expectedAnchors = [
      '#1-dinner-cruise-bateaux-mouches',
      '#2-dinner-cruise-bateaux-parisiens',
      '#3-dinner-cruise-paris-city-vision',
      '#4-dinner-cruise-paris-en-scene',
      '#5-dinner-cruise-le-diamant-bleu',
      '#6-trattoria-en-seine',
      '#7-capitaine-fracasse',
      '#8-maxim-de-paris',
      '#9-ducasse-sur-seine',
      '#10-paris-city-vision'
    ];

    itemList.itemListElement.forEach((item, idx) => {
      const pos = idx + 1;
      assert.strictEqual(item['@type'], 'ListItem', `Item #${pos} @type must be ListItem`);
      assert.strictEqual(item.position, pos, `Item #${pos} position must be ${pos}`);
      assert.ok(item.name && item.name.length > 0, `Item #${pos} missing name`);
      assert.ok(
        item.name.toLowerCase().includes(expectedBoats[idx].toLowerCase()),
        `Item #${pos} name ("${item.name}") does not match expected boat "${expectedBoats[idx]}"`
      );
      assert.strictEqual(
        item.url,
        `https://www.thecruisedetective.com/dinner-cruises-paris${expectedAnchors[idx]}`,
        `Item #${pos} URL ("${item.url}") must match expected canonical anchor "${expectedAnchors[idx]}"`
      );
      assert.ok(item.description && item.description.length > 20, `Item #${pos} missing detailed description`);
    });
  });

  it('FAQPage schema entity answers the 5 critical traveler logistics questions', () => {
    const scriptMatch = rawHtml.match(/<script\s+type=["']application\/ld\+json["']>([\s\S]*?)<\/script>/i);
    const graph = JSON.parse(scriptMatch[1])['@graph'];
    const faq = graph.find(e => e['@type'] === 'FAQPage');
    assert.ok(faq, 'Missing FAQPage entity in @graph');

    assert.strictEqual(faq.mainEntity.length, 5, 'FAQPage must contain exactly 5 Question entities');

    const requiredQuestions = [
      { id: 'dress_code', pattern: /dress\s*code/i },
      { id: 'sparkle_timing', pattern: /sparkle/i },
      { id: 'departure_hours', pattern: /departure|hour|sunset/i },
      { id: 'proposal_anniversary', pattern: /proposal|anniversary/i },
      { id: 'refund_cancellation', pattern: /refund|cancellation|water/i }
    ];

    requiredQuestions.forEach(rq => {
      const match = faq.mainEntity.find(q => rq.pattern.test(q.name));
      assert.ok(match, `FAQPage missing question matching topic: ${rq.id}`);
      assert.strictEqual(match['@type'], 'Question', `Entity for ${rq.id} must be of @type Question`);
      assert.ok(match.acceptedAnswer, `Question ${rq.id} missing acceptedAnswer`);
      assert.strictEqual(match.acceptedAnswer['@type'], 'Answer', `Answer for ${rq.id} must be of @type Answer`);
      assert.ok(match.acceptedAnswer.text.length > 50, `Answer for ${rq.id} is too short or empty`);
    });
  });
});

// ============================================================================
// SUITE 6: Webflow Component Styling & Callout Architecture (Deliverable 04)
// ============================================================================
describe('Suite 6: Webflow Component Styling & Callout Architecture (Deliverable 04)', () => {
  const content = fs.readFileSync(FILE_04, 'utf-8');

  it('Contains all 4 required Webflow components across the showcase', () => {
    // 1. Sommelier Pro Tips
    assert.ok(content.includes('cd-sommelier-tip'), 'Missing Component 1: Sommelier Pro Tips (.cd-sommelier-tip)');
    assert.ok(content.includes('cd-tip-badge'), 'Missing Sommelier tip badge element (.cd-tip-badge)');

    // 2. Structured 2-Column Pros & Cons Breakdown
    assert.ok(content.includes('cd-review-breakdown'), 'Missing Component 2: Review Breakdown container');
    assert.ok(content.includes('cd-pros-cons-grid'), 'Missing 2-column pros/cons grid container');
    assert.ok(content.includes('cd-pros-card'), 'Missing "What We Loved" positive card (.cd-pros-card)');
    assert.ok(content.includes('cd-cons-card'), 'Missing "Keep in Mind" negative card (.cd-cons-card)');
    assert.ok(content.includes('What We Loved'), 'Missing "What We Loved" title in Component 2');
    assert.ok(content.includes('Keep in Mind'), 'Missing "Keep in Mind" title in Component 2');

    // 3. Multi-Platform Verified Review Badges Bar
    assert.ok(content.includes('cd-verified-reviews-bar'), 'Missing Component 3: Verified Reviews Bar');
    assert.ok(content.includes('cd-platform-chips-grid'), 'Missing platform chips grid');
    assert.ok(content.includes('cd-platform-chip'), 'Missing platform chips (.cd-platform-chip)');
    assert.ok(content.includes('Tiqets'), 'Missing Tiqets platform label');
    assert.ok(content.includes('GetYourGuide'), 'Missing GetYourGuide platform label');
    assert.ok(content.includes('Viator'), 'Missing Viator platform label');
    assert.ok(content.includes('TripAdvisor'), 'Missing TripAdvisor platform label');

    // 4. Standalone Self-Contained Drop-in Embed Code Snippets
    assert.ok(
      content.includes('STANDALONE SELF-CONTAINED EMBED SNIPPETS') || content.includes('cd-standalone-embed'),
      'Missing Component 4: Standalone Self-Contained Drop-In Embed Code Snippets'
    );
  });

  it('Strictly scopes 100% of CSS rules and classes to prevent Webflow layout bleed', () => {
    const selectors = extractCssSelectors(content);
    assert.ok(selectors.length > 20, `Expected >20 CSS selectors, found ${selectors.length}`);

    const unscoped = selectors.filter(sel => {
      if (sel === ':root' || sel === ':host' || sel.startsWith('/*')) return false;
      return !sel.includes('.cd-');
    });

    assert.strictEqual(
      unscoped.length,
      0,
      `Found unscoped CSS selectors in Webflow component blocks: ${unscoped.join(', ')}`
    );
  });

  it('Enforces zero emoji characters in all HTML component headings (h2, h3, h4)', () => {
    const headings = extractHtmlHeadings(content);
    assert.ok(headings.length > 5, 'Expected >5 headings in component library');
    const emojiHeadings = headings.filter(h => EMOJI_REGEX.test(h));
    assert.strictEqual(
      emojiHeadings.length,
      0,
      `Component library headings contain forbidden emojis:\n${emojiHeadings.join('\n')}`
    );
  });

  it('Embeds accessible inline SVGs with aria-hidden="true" to eliminate external font dependencies', () => {
    const svgMatches = [...content.matchAll(/<svg\b[^>]*>/gi)];
    assert.ok(svgMatches.length >= 10, `Expected at least 10 inline SVGs, found ${svgMatches.length}`);
    for (const svg of svgMatches) {
      assert.ok(
        svg[0].includes('aria-hidden="true"'),
        `Inline SVG missing accessible aria-hidden="true": ${svg[0]}`
      );
    }
  });

  it('Includes responsive media queries for mobile viewports (max-width: 768px)', () => {
    assert.ok(
      content.includes('@media (max-width: 768px)') || content.includes('@media(max-width:768px)'),
      'Missing responsive 768px breakpoint media query for 2-column mobile collapse'
    );
  });
});

// ============================================================================
// SUITE 7: Cross-Deliverable Alignment & E-E-A-T Consistency
// ============================================================================
describe('Suite 7: Cross-Deliverable Alignment & E-E-A-T Consistency', () => {
  const c01 = fs.readFileSync(FILE_01, 'utf-8');
  const c02 = fs.readFileSync(FILE_02, 'utf-8');
  const c03 = fs.readFileSync(FILE_03, 'utf-8');
  const c04 = fs.readFileSync(FILE_04, 'utf-8');

  it('Consistent ranking: Bateaux Mouches is Rank #1 across all deliverables', () => {
    assert.ok(c01.includes('1. Bateaux Mouches'), '01 must rank Bateaux Mouches as #1');
    assert.ok(c02.includes('Bateaux Mouches') && c02.includes('cd-row-winner'), '02 must rank Bateaux Mouches as winner');
    assert.ok(c03.includes('Bateaux Mouches (Prestige & Excellence Dinner Cruise)'), '03 must rank Bateaux Mouches at position 1');
    assert.ok(c04.includes('Bateaux Mouches'), '04 must include Bateaux Mouches component examples');
  });

  it('Consistent ranking: Bateaux Parisiens is Rank #2 across all deliverables', () => {
    assert.ok(c01.includes('2. Bateaux Parisiens'), '01 must rank Bateaux Parisiens as #2');
    assert.ok(c02.includes('Bateaux Parisiens'), '02 must include Bateaux Parisiens as #2');
    assert.ok(c03.includes('Bateaux Parisiens (Gourmet Dinner Cruise)'), '03 must rank Bateaux Parisiens at position 2');
    assert.ok(c04.includes('Bateaux Parisiens'), '04 must include Bateaux Parisiens component examples');
  });

  it('Consistent Author E-E-A-T credentials for Adam Dimitrov across deliverables', () => {
    assert.ok(c01.includes('Adam Dimitrov'), '01 editorial copy must reference author Adam Dimitrov');
    assert.ok(c03.includes('Adam Dimitrov'), '03 schema must reference author Adam Dimitrov');
    assert.ok(c03.includes('Head Cruise Detective & Founder'), '03 schema must feature exact founder credentials');
  });

  it('Zero emojis across all heading levels in all 4 deliverables simultaneously', () => {
    const allHeadings = [
      ...extractMarkdownHeadings(c01),
      ...extractHtmlHeadings(c02),
      ...extractHtmlHeadings(c04)
    ];
    const emojiMatches = allHeadings.filter(h => EMOJI_REGEX.test(h));
    assert.strictEqual(
      emojiMatches.length,
      0,
      `Cross-deliverable emoji audit failed. Found ${emojiMatches.length} emojis in headings:\n${emojiMatches.join('\n')}`
    );
  });
});
