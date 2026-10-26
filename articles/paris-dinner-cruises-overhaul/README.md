# Paris Dinner Cruises Overhaul: Webflow Deployment & Integration Manual

> **Flagship Article:** `https://www.thecruisedetective.com/dinner-cruises-paris`  
> **Package Directory:** `/Users/adamdimitrov/Development/cruisedetective/articles/paris-dinner-cruises-overhaul/`  
> **Author & Maritime Tourism Specialist:** Adam Dimitrov  
> **Last Verification Run:** Passed 36/36 Automated E2E Tests (100% Pass Rate)

---

## 1. Executive Summary & Package Architecture

This deployment package delivers a complete commercial, editorial, and technical SEO overhaul for the flagship Paris Dinner Cruises review guide. It addresses critical revenue leakage, solves technical schema errors, introduces firsthand E-E-A-T culinary depth across 10 operators, and provides responsive Webflow-isolated UI components designed to maximize conversions for high-value dinner bookings.

### Commercial & Unit Economics Context
* **Core Commission Rate:** **41.9%** locked partnership rate via Tiqets (`thecruisedetective.com-176436`).
* **Operator Revenue Impact:**
  * **Bateaux Mouches (#1 Ranked Winner):** Highest producing dinner cruise on the platform (**€59.45 / $64.80** average net commission per order, 96 orders, €36,028 sales).
  * **Bateaux Parisiens Gourmet Dinner (#2 Ranked):** Generates **€41.53** average net commission per order.
  * **Revenue Protection Warning:** Historical cross-linking to Bateaux Parisiens sightseeing cruise (`p973977` @ €7.54 commission) resulted in an immediate **€33.99 revenue loss per order**. All links in this package strictly enforce gourmet dinner cruise product `p974358`.
  * **Dead Link Elimination:** Paris City Vision / La Marina previously routed through Tiqets `p1023747` (which dead-redirects to a generic category page). All links in this package route directly to GetYourGuide product `t53306` (`YS414AJ`), preserving conversion tracking.

---

## 2. Deliverables Directory Index

```
articles/paris-dinner-cruises-overhaul/
├── 01_editorial_content_expansion.md   # Complete 11,300+ word editorial text ready for CMS/Rich Text
├── 02_semantic_comparison_table.html   # Position-0 accessible HTML comparison table with gold styling
├── 03_rich_json_ld_schema.html         # Unified Schema.org JSON-LD (Article, ItemList, FAQPage)
├── 04_webflow_component_blocks.html    # Isolated .cd-* Webflow component showcase & standalone embeds
├── 05_verification_suite.js            # Automated E2E test suite asserting all Acceptance Criteria
└── README.md                           # This comprehensive deployment and integration manual
```

---

## 3. Webflow Deployment Guide

### Step 1: Head Code Injection — Rich JSON-LD Schema (`03_rich_json_ld_schema.html`)

Injecting structured data into the document `<head>` provides Google search crawlers with unambiguous entity signals, E-E-A-T author credentials, ranked carousels, and rich FAQ snippets.

#### Webflow Navigation
1. Open the Webflow Designer.
2. In the left sidebar, click the **Pages** panel (`P`).
3. Hover over the **Paris Dinner Cruises** page (`/dinner-cruises-paris`) and click the **Settings (gear icon)**.
4. Scroll down to the **Custom Code** section.
5. In the **Inside `<head>` code** text box, paste the complete contents of `03_rich_json_ld_schema.html`.
6. Click **Save** and **Publish**.

#### What This Schema Solves
* **Fixes Publisher Logo Bug:** The previous live site emitted `"logo": { "@type": "ImageObject", "url": "" }`, generating Google Rich Results errors. Deliverable 03 provides the valid absolute SVG CDN URL (`https://cdn.prod.website-files.com/6369a6904656314914c2bae2/6369a8d295be04a841e17ea5_logo.svg`) with explicit dimensions (`124` width, `40` height).
* **Author E-E-A-T Signals:** Links author `Adam Dimitrov` (`Person`) with job title `Head Cruise Detective & Founder`, verified bio, portrait headshot, and canonical about profile (`https://www.thecruisedetective.com/about`).
* **Ranked `ItemList` (10 Boats):** Encodes all 10 dinner cruise operators in positions 1 through 10 with deep anchor links (`#1-dinner-cruise-bateaux-mouches` to `#10-paris-city-vision`). Note: Boat #6 is canonically mapped to `#6-trattoria-en-seine` to align with the overhauled brand heading. When updating the Webflow article, set the Boat #6 section container ID to `6-trattoria-en-seine` (and optionally embed `<a id="6-le-diamant-bleu"></a>` to preserve legacy inbound deep links).
* **Rich `FAQPage` Markup:** Encodes 5 high-intent logistics questions (dress code, Eiffel Tower sparkle timing, departure hour selection, marriage proposal planning, and weather/river flood refund policies).

---

### Step 2: Google Position-0 Comparison Matrix Embed (`02_semantic_comparison_table.html`)

Google extracts tabular Position-0 featured snippets directly from accessible `<table>` markup. Standard Webflow tables often suffer from responsive squishing and CMS styling bleed. Deliverable 02 is self-contained with responsive horizontal scrolling and namespaced CSS.

#### Webflow Placement
1. In the Webflow Designer, navigate to the body section of the Paris Dinner Cruises article.
2. Locate the spot immediately following the article summary verdict (directly beneath `## Summary Comparison of the 10 Best Paris Dinner Cruises`).
3. Click **Add Elements (`+`)** -> Scroll to **Advanced** -> Drag an **HTML Embed** component onto the canvas.
4. Copy the **entire contents** of `02_semantic_comparison_table.html` and paste into the HTML Embed code editor.
5. Click **Save & Close**.

#### Key Architectural Highlights
* **9 Semantic Columns in Order:**
  1. `Boat Name & Rank` (`<th scope="col">` and `<th scope="row">` associations)
  2. `Overall Rating & Review Volume`
  3. `Price Range`
  4. `Menu Courses & Quality`
  5. `Drinks Included`
  6. `Music Type`
  7. `Rooftop Deck`
  8. `Seating Highlights`
  9. `Direct Booking`
* **Gold Winner Prominence:** Bateaux Mouches (Row 1) is styled with `.cd-row-winner` (warm gold background `#fffdf7`, 4px gold left border `#d97706`, `#1 BEST OVERALL` gold badge, and a high-contrast amber-gold booking button `.cd-btn-bm`).
* **Zero Webflow Reset Conflicts:** All classes are namespaced with `.cd-*` and use `!important` declarations to resist Webflow's `.w-richtext` overrides.

---

### Step 3: Editorial Copy CMS / Rich Text Guide (`01_editorial_content_expansion.md`)

The editorial text in `01_editorial_content_expansion.md` contains over 11,300 words of firsthand tasting notes, seating trade-offs, and logistics.

#### Webflow Integration Options
* **Option A: Static Page (Standard Webflow Page):**
  If the page is built using native Webflow layout elements, copy sections from the markdown file directly into corresponding Webflow Rich Text or Text Block elements.
* **Option B: Webflow CMS Collection Item:**
  If the article lives inside a Blog/Articles CMS Collection:
  1. Open the Webflow **CMS Collection** for articles.
  2. Open the `Paris Dinner Cruises` item.
  3. Convert markdown to HTML (using any standard markdown renderer) or paste directly into the Webflow CMS Rich Text field.
  4. Note: Webflow Rich Text handles standard markdown shortcuts (`#`, `##`, `*`, `>`) when pasting plain text.

#### Editorial Rules Enforced
1. **Strictly ZERO Emojis in Headings:** Google search quality guidelines prioritize clean, professional headings for informational intent. All 77 headings across `#`, `##`, `###`, and `####` have zero emojis. Do NOT re-add decorative emojis to headings.
2. **Dedicated Course-by-Course Dish Assessments:** Every boat includes firsthand reviews of starters, mains, desserts, and beverage pairings, highlighting both triumphs (warm chocolate profiteroles on Bateaux Mouches, seared scallops on Bateaux Parisiens) and honest culinary flaws (chewy duckling on Bateaux Parisiens, wobbly tables on Le Diamant Bleu).
3. **Seating Tier Realities:** Clearly distinguishes window tables, sunken central aisles, surcharge structures, glass canopy reflections, and seasonal window condensation.

---

### Step 4: Webflow Component Placement Guide (`04_webflow_component_blocks.html`)

Deliverable 04 provides four production-ready component types. There are two deployment strategies:

#### Deployment Strategy A: Master Stylesheet + Lightweight HTML (Recommended)
1. Copy the master CSS block (from `<style id="cd-master-components-css">` to `</style>` at lines 15–233 of `04_webflow_component_blocks.html`).
2. Paste this into Webflow Page Settings -> **Inside `<head>` code** (right after the JSON-LD schema) OR into an HTML Embed component at the very top of the page.
3. Throughout the article, insert lightweight HTML Embed blocks copying the specific component markup (without repeating the CSS).

#### Deployment Strategy B: Standalone Self-Contained Drop-In Embeds
If you prefer not to touch page head settings, navigate to **Section 4: Standalone Self-Contained Embed Snippets** (lines 1215–1440 of `04_webflow_component_blocks.html`). Each snippet contains its own inline `<style>` block and can be pasted independently into any Webflow Custom Code Embed.

#### In-Article Component Mapping

| Component Type | CSS Container Class | Recommended Placement in Article | Purpose |
|---|---|---|---|
| **Sommelier Pro Tip** | `.cd-sommelier-tip` | Directly below the Menu & Wine Tasting sub-sections for Bateaux Mouches, Bateaux Parisiens, Paris City Vision, and Le Diamant Bleu. | Delivers insider sommelier advice (wine serving temperatures, bottle sharing rules, rooftop deck timing). |
| **2-Column Pros & Cons** | `.cd-review-breakdown` | Directly beneath the H2 operator heading and summary specs for each major boat review. | Provides high-contrast, skimmable decision cards ("What We Loved" vs. "Keep in Mind") with SVG icons. |
| **Multi-Platform Review Badges** | `.cd-verified-reviews-bar` | Directly below the vessel introduction before detailed pricing breakdowns. | Aggregates verified review ratings across Tiqets, GetYourGuide, Viator, and TripAdvisor with exact review counts. |

---

## 4. Affiliate Deeplink Architecture & Commercial Mapping

All affiliate links across the deliverables are validated active and configured to prevent conversion drop-offs.

| Boat Operator | Product Type | Network / Partner | Product ID | Campaign Tag | Target URL |
|---|---|---|---|---|---|
| **Bateaux Mouches** | Prestige / Excellence Dinner | Tiqets (`thecruisedetective.com-176436`) | `p982924` | `dinner-paris-compariso-bm` | `https://www.tiqets.com/...-p982924/?partner=thecruisedetective.com-176436&tq_campaign=dinner-paris-compariso-bm` |
| **Bateaux Parisiens** | Gourmet Dinner Cruise | Tiqets (`thecruisedetective.com-176436`) | `p974358` | `din-cru-compa-bp` | `https://www.tiqets.com/...-p974358/?partner=thecruisedetective.com-176436&tq_campaign=din-cru-compa-bp` |
| **Paris City Vision / La Marina** | 3-Course Seine Dinner | GetYourGuide (`YS414AJ`) | `t53306` | `cmp=table-paris-pcv` | `https://www.getyourguide.com/...-t53306/?partner_id=YS414AJ&utm_medium=online_publisher...` |
| **Paris en Scène** | Panoramic Bistro Dinner | Tiqets (`thecruisedetective.com-176436`) | `p1052475` | `paris-din-comp-parenscene` | `https://www.tiqets.com/...-p1052475/?partner=thecruisedetective.com-176436&tq_campaign=paris-din-comp-parenscene` |
| **Le Diamant Bleu** | Catamaran Dinner Cruise | Tiqets (`thecruisedetective.com-176436`) | `p1049009` | `din-cru-compa-dbleu` | `https://www.tiqets.com/...-p1049009/?partner=thecruisedetective.com-176436&tq_campaign=din-cru-compa-dbleu` |
| **Trattoria en Seine** | Italian Pasta Cruise (*Théo*) | Tiqets (`thecruisedetective.com-176436`) | `p1071588` | `din-cru-par-comp-tratt` | `https://www.tiqets.com/...-p1071588/?partner=thecruisedetective.com-176436&tq_campaign=din-cru-par-comp-tratt` |
| **Capitaine Fracasse** | Chef-Cooked Bistro Dinner | GetYourGuide (`YS414AJ`) | `t178769` | `article-dinner-cruises-paris-capitaine-fracasse-reviews` | `https://www.getyourguide.com/...-t178769/?partner_id=YS414AJ...` |
| **Maxim's de Paris** | Belle Époque Jazz Dinner | GetYourGuide (`YS414AJ`) | `t420838` | `article-dinner-cruises-paris-maxim-de-paris-reviews` | `https://www.getyourguide.com/...-t420838/?partner_id=YS414AJ...` |
| **Ducasse sur Seine** | Electric Haute Gastronomy | Viator via Travelpayouts (`404154`) | `135588P1` | `article-dinner-cruises-paris-ducasse-sur-seine-reviews` | `https://tp.media/r?marker=404154...&u=https%3A%2F%2Fwww.viator.com%2Ftours%2FParis%2FDucasse-dinner...-135588P1` |
| **Paris City Vision Early Sunset** | 18:45 Sunset Dinner | GetYourGuide (`YS414AJ`) | `t53306` | `cmp=table-paris-pcv-early` | `https://www.getyourguide.com/...-t53306/?partner_id=YS414AJ...` |

---

## 5. Automated Verification & Quality Assurance

The programmatic test suite in `05_verification_suite.js` executes comprehensive assertions covering all acceptance criteria across the entire package.

### Executing the Test Suite
Run the following command from the project root:

```bash
ELECTRON_RUN_AS_NODE=1 /Applications/Antigravity.app/Contents/MacOS/Antigravity /Users/adamdimitrov/Development/cruisedetective/articles/paris-dinner-cruises-overhaul/05_verification_suite.js
```

### Test Suite Results Summary
```
▶ Suite 1: Deliverables Existence and Baseline Size (4/4 passed)
▶ Suite 2: Editorial Content & Culinary Depth Rigor (5/5 passed)
▶ Suite 3: Affiliate Link Integrity & Revenue Protection (6/6 passed)
▶ Suite 4: Semantic Comparison Matrix Technical SEO & Accessibility (7/7 passed)
▶ Suite 5: Rich JSON-LD Structured Data Schema Validation (5/5 passed)
▶ Suite 6: Webflow Component Styling & Callout Architecture (5/5 passed)
▶ Suite 7: Cross-Deliverable Alignment & E-E-A-T Consistency (4/4 passed)

ℹ tests 36
ℹ suites 7
ℹ pass 36
ℹ fail 0
```

### External Validation Tools
Before pushing to production, verify live staging with these external Google tools:
1. **Google Rich Results Test:** [https://search.google.com/test/rich-results](https://search.google.com/test/rich-results)
   * Paste the contents of `03_rich_json_ld_schema.html` or inspect the live staging URL.
   * Expected: Detects valid `Article` and `FAQPage` rich results with 0 warnings and 0 errors.
2. **Schema.org Validator:** [https://validator.schema.org/](https://validator.schema.org/)
   * Expected: Confirms valid `@graph` containing `Article`, `ItemList` (10 items), and `FAQPage` (5 questions).
3. **W3C Nu HTML Checker:** [https://validator.w3.org/nu/](https://validator.w3.org/nu/)
   * Validate snippet from `02_semantic_comparison_table.html` to confirm semantic table validity.
