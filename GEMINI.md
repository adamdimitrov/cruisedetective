# Communication Style & Operational Directives

- **Tone & Demeanor**: Strictly objective, direct, and candid.
- **Zero Sycophancy (No Ass-Kissing)**: Never flatter, over-praise, or use hyped promotional language. Do not use artificial enthusiasm or cheerleading.
- **Truth Over Politeness**: If the user's premise, math, assumption, or marketing approach has flaws, call it out plainly and immediately. Never hesitate to contradict the user when data, economics, or facts dictate otherwise.
- **Concise & Analytical**: Deliver hard numbers, real unit economics, structural constraints, and concrete action steps without fluff.

# Commercial & Unit Economics Context

- **Bateaux Parisiens Commission Rate**: **41.9%** (Locked partnership rate via Tiqets / partner `thecruisedetective.com-176436`).
- **Unit Economics Breakdown**:
  - Adult Ticket (€18.00): **€7.54** ($8.20) commission.
  - Child Ticket 4–11 (€9.00): **€3.77** ($4.11) commission (50% OFF standard adult ticket).
  - Standard Family Basket (2 Adults + 2 Children = €54.00): **€22.63** ($24.64) gross profit per converted order.
  - Break-Even at $0.40 CPC: **1.62% conversion rate** (1 sale every 62 clicks).
  - Target ROAS at 4% Conversion Rate: **~2.46x ROAS** ($14.64 net profit per order after ad spend).

# Ad Creative & Image Generation Directives (Nano Banana / Gemini Image)

- **Why Default AI Prompts Look Fake**: Native multimodal image models (`gemini-2.5-flash-image` / `gemini-3-pro-image` / Imagen 4) default to an overly airbrushed "commercial stock photo" aesthetic unless explicitly overridden.
- **Mandatory Photorealism Prompt Overrides**: Every ad generation prompt MUST explicitly enforce:
  - *"Realistic, candid iPhone photography lighting, natural skin textures, authentic everyday tourist clothing."*
  - *"Real product/venue geometry"* (e.g., *"real Bateaux Parisiens glass-top trimaran boats on the Seine"*), passing actual reference photos from the landing page whenever possible.
  - *"No floating 3D cartoon stopwatches, no cheesy clip-art icons, and no matching striped stock-photo outfits."*
- **Mandatory Offer & Price Anchoring**: Every static ad creative and ad copy variation must explicitly state the real unit pricing (e.g., **€18 Adults • €9 Kids (50% OFF, ages 4–11) • Under 4 FREE**) and concrete logistics (**Instant Smartphone QR Ticket**, **Pier 3 under the Eiffel Tower**) to prevent price-reseller skepticism.
- **Template-Conditioned Generation (Option B Workflow)**: Whenever generating static Meta ads in Antigravity, ALWAYS pass a winning Superscale layout template from `/Users/adamdimitrov/Development/cruisedetective/ads/reference_library/templates/` alongside a real venue photo from `/Users/adamdimitrov/Development/cruisedetective/ads/reference_library/venue_photos/` into `image-generator`, instructing it to preserve the exact UI card typography, padding, and layout hierarchy while removing the green corner bookmark icon (see `/Users/adamdimitrov/.gemini/config/skills/nano-banana-ad-generator/SKILL.md`).

# 365-Day Tiqets First-Party Data Intelligence (`CRUISEDETECTIVE_BRAND_BRAIN.md`)

- **365-Day Totals (Oct 2025 – Oct 2026)**: **761 fulfilled orders** | **€85,006.82 gross sales** | **€18,558.45 net commission** (`€24.39` avg commission/order).
- **Top Products by Net Commission**:
  1. **`982924` — Bateaux Mouches Dinner Cruise**: **96 orders** | €36,028.29 sales | **€5,707.19 commission** (**`€59.45` ($64.80) avg commission/order**).
  2. **`973977` — Bateaux Parisiens Sightseeing**: **255 orders** | €11,887.85 sales | **€5,124.26 commission** (**`€20.10` ($21.90) avg commission/order**).
  3. **`982823` — Bateaux Mouches Sightseeing**: **85 orders** | €4,043.46 sales | **€1,707.10 commission** (**`€20.08` avg commission/order**).
  4. **`973666` — Amsterdam Canal Cruise**: **99 orders** | €4,320.04 sales | **€1,408.77 commission** (`€14.23` avg).
  5. **`975431` — London Thames Cruise**: **73 orders** | €4,402.56 sales | **€1,045.17 commission** (`€14.32` avg).
  6. **`1071588` — Theo Trattoria Dinner Cruise**: **25 orders** | €5,478.51 sales | **€802.50 commission** (`€32.10` avg).
  7. **`1052475` — Paris en Scène Dinner Cruise**: **16 orders** | €3,058.29 sales | **€558.58 commission** (`€34.91` avg).
  8. **`974358` — Bateaux Parisiens Dinner Cruise**: **12 orders** | €4,655.48 sales | **€498.40 commission** (`€41.53` avg).
  9. **`1049009` — Le Diamant Bleu Dinner Cruise**: **9 orders** | €2,788.01 sales | **€405.63 commission** (`€45.07` avg).
- **Sightseeing (`973977`, n=255) vs. Dinner Cruises (`n=167`) Behavioral Split**:
  - **Booking Lead Time**: Sightseeing is **45% Same-Day (`0 days`) / 56% within 0–1 days** (in-destination impulse buy). Dinner Cruises are **only 2% Same-Day** and **64% booked 8+ days in advance** (pre-trip planned purchase).
  - **Device**: Sightseeing is **68% Mobile (`173` mobile / `77` desktop)**. Dinner Cruises are **59% Desktop (`99` desktop / `62` mobile)**.
  - **IP Location at Checkout**: Sightseeing #1 is **France (`FR`: 77)**, #2 `US` (71), #3 `GB` (38). Dinner Cruises #1 is **United States (`US`: 79 — 47%!)**, #2 `FR` (26).
  - **Basket Composition**: On Sightseeing (`973977`), **49.4% buy 2 tickets (Couples)** and **43.1% buy 3+ tickets (Families/Groups)**. On Dinner Cruises, **98% have no kids** (`65%` buy exactly 2 tickets).
- **Buyer Nationalities (n=761)**: `US` (311 — 40.9%; 56.9% of Dinner Cruises), `GB` (137 — 18.0%), `NL` (36 — 4.7%), `FR` (33 — 4.3%), `PL` / `CA` / `DE` (23 each — 3.0%), `AU` (17 — 2.2%), `JP` (15 — 2.0%), `IE` (13 — 1.7%). Combined Anglosphere = **65.8%**.
- **Active Pixels & Custom Audiences**:
  - Meta Pixel: `1355732169631751` | Google Ads Tag: `AW-16782417237` (`4899321613`) | GA4: `G-RN34XFKPQ6` | Clarity: `z1jcuxy2we`
  - `SEO & LP Visitors - Paris Sightseeing Cruises (30D Retargeting)`: `120251645526940010`
  - `SEO Visitors - Paris Dinner Cruises (30D Retargeting)`: `120251645527150010`
  - `SEO Historical Pool - Paris Sightseeing Cruises (180D Lookalike Seed)`: `120251645527340010`
  - `SEO Historical Pool - Paris Dinner Cruises (180D Lookalike Seed)`: `120251645527780010`
