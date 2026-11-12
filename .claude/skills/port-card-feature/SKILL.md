---
name: port-card-feature
description: Carry a comparison-card feature or fact change (pills, popovers, ratings, sliders, Pick/Skip, menus, ranking order) from the EN money page to the other money pages and all 8 translations, using the card data layer. Use when the user says do the same on dinner / Thames / Amsterdam, or bring the translations up to date.
---

# /port-card-feature

The card system (`div.bpa-card`) is on about 47 pages: 4 EN money pages plus 8 translations each, plus NYE. Features get built on the EN Seine page first and then have to reach the rest. Before this skill that was done by hand ("Seine card system step 1, step 2" on dinner, the French Seine page rebuilt).

## 1. See where things stand
```bash
python3 scripts/cards/cards.py all
```
For each EN money page and each translation this shows:
- **issues**: different product, price or rating at the same rank, or fewer photos. These are factual drift and must be fixed.
- **behind EN**: card features the EN page has and the translation lacks (`rate_popover`, `tested_popover`, `time_pill`, `lang_popover`, `route_popover`, `pick_skip`, `kids_price`, `photo_captions`, `menu_pill`). To register a new feature, add its CSS selector to `FEATURES` in `scripts/cards/cards.py`.

## 2. Port in one scripted pass, not page by page

**Use `/port-i18n` (`scripts/i18n/port.py sync <preset>`) for this now**: it rebuilds the cards from EN with the translation memory. The manual steps below are only for a feature the tool does not cover yet.

1. Build and get approval on the EN page first.
2. Write one throwaway script in the session scratchpad. It reads the EN card (BeautifulSoup, `div.bpa-card#card-N`) and the matching translated card, and copies the structure over. It keeps the translated strings, translates only the new strings, and leaves numbers, links and brand names alone.
3. Order matters: fix ranking and products first (move the whole card block), then facts, then features.
4. Put the CSS the feature needs into each page's `<style>` (pages are standalone). Check that the class names match the EN page.
5. Re-run `cards.py drift <en-page>` until the issues are 0 and the feature is gone from "behind EN".

## 3. Translation rules
- Native-sounding copy, same meaning as EN. Keep the Pick/Skip structure.
- Never translate operator, ship, product or site names.
- No em dashes in any language.
- Keep each language's own currency format and decimal separator, with the same numbers.

## 4. Check and ship
`python3 scripts/qa/mobile_overflow.py <changed pages>`, because longer translated labels overflow more often (DE, NL, PL). Then `/ship` with every changed language in one PR.

## Next step (not built yet)
Full JSON-to-HTML rendering: the cards rendered from `data/cards/<page>.<lang>.json` with one template. Start it once the card design stops changing daily. Until then, `cards.py extract` is the data layer and `drift` is the guard.
