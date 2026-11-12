---
name: port-i18n
description: Bring translated pages in line with the EN page (cards, sections, dinner menus) using the translation memory, so only new strings get translated. Use after any EN change on a money page, when a translation is behind EN, or when a new page or language needs its first translation (Amsterdam, London, NYE, FR, NL).
---

# /port-i18n

Tool: `scripts/i18n/port.py`. Memory: `i18n/memory/<lang>.json` (EN string → translation, about 950 strings per language).
Every string is translated once and reused on every page and every later run. **Never translate a string the memory already has.**

## Existing page groups (presets)
`scripts/i18n/presets.json` defines `seine` and `dinner`: the EN page, each language's page, and what gets ported (cards, menus, sections and where they go).

```bash
python3 scripts/i18n/port.py sync seine --check     # what is missing per language, changes nothing
python3 scripts/i18n/port.py sync seine             # apply cards + sections (+ menus for dinner) in all languages
python3 scripts/i18n/port.py sync dinner --langs fr,nl
```

## When strings are missing (only new EN text)
1. `python3 scripts/i18n/port.py missing --lang de --en seine-river-cruises-paris --what cards`. Use `--what sections --ids a,b` or `--what menus` as needed. This writes `i18n/todo/<page>.<what>.<lang>.txt` (`n|EN`).
2. Write the translation as `…<lang>.done.txt` (`n|translation`) with the same numbering. Write only the new lines.
3. `python3 scripts/i18n/port.py learn --lang de --todo <todo> --done <done>`. This refuses em dashes.
4. Run `sync` again.

Do one language per todo file, and do all languages before running sync.

## New page group (Amsterdam, London, NYE, …)
1. Add a preset to `presets.json`: the `en` page, `pages` per language (from the EN page's hreflang links), and `cards`/`menus`/`sections`. Each section run needs `ids` plus a `place`:
   - `before-id:ID`
   - `before-closing-of:ID` (the wrapper div that ends right before element ID)
   - `before:LITERAL`

   Find the place by looking at what directly follows the section on the EN page and whether that element exists on the translated page.
2. If a translated page is already a faithful copy of EN (same markup, e.g. the rebuilt FR Seine page), harvest it instead of translating: `port.py harvest --lang fr --en seine-river-cruises-paris --tr fr/meilleures-croisieres-seine-paris --what cards`.
3. `sync <preset> --check`, then `missing`/`learn`, then `sync <preset>`.
4. Check that the sections are there and that the H2 order matches EN. Remove old duplicated blocks by hand if the translation had an older version of a section somewhere else.

## Rules the tool enforces or relies on
- **Card titles and rank tags stay the page's own.** If a product is on EN but not on the translated page, the cards command stops: fix the ranking first (move cards, as on 2026-11-11).
- **Links:** internal links are rewritten to the language's version via hreflang. NYE links stay EN until a translated NYE page exists. Anchors that don't exist on the page are dropped from the cards.
- **Dinner menus:** printed menus need `menus` before `cards`; `sync` does this order. Without the modal, the cards hide the menu buttons.
- **Context:** the same EN word can need different translations per context. Use `menus::EN` / `sections::EN` keys in the memory (e.g. Japanese "or").
- **No em dashes. Brand, ship and product names stay untranslated.**

## After applying
```bash
python3 scripts/cards/cards.py drift <en-page>    # facts and features vs EN
python3 scripts/qa/mobile_overflow.py             # 375px
python3 scripts/ship/preflight.py --fix           # em dashes, sitemap lastmod, links
```
Then `/ship`, and request indexing in Search Console (Chrome). The daily quota is about 10 URLs, so prioritise the pages with traffic.
