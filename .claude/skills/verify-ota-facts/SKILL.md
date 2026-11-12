---
name: verify-ota-facts
description: Verify prices, ratings, review counts, times, piers and booking links on a cruise comparison page against the live Tiqets / GetYourGuide / Viator / Tripadvisor listings, then sync the facts to every translation. Use before publishing or refreshing a money page, or when the user says prices or ratings are wrong.
---

# /verify-ota-facts

Wrong prices are the most common QC complaint ("the prices are wrong again"). This is the fixed procedure.

## 1. Dump what the page claims
```bash
python3 scripts/cards/cards.py extract <page> -o /tmp/claims.json
```
For each card this gives the product id (Tiqets `p…` or GYG `t…`), price, was-price, kids price, rating, review counts per site, pills (time, pier, language, route), Pick/Skip line and photo count.

## 2. Check each card against the live listing
Open the card's `title_href` product in the user's Chrome. Never use the built-in browser. Record:
- **Adult price** at the lowest normal date (not a promo-only date). Kids price and the free-under age.
- **Rating and review count** on Tiqets, GYG, Viator and Tripadvisor. The weighted rating is Σ(score×count)/Σcount. Put it in `--r` (2 decimals) and show it with 1 decimal.
- **Duration, pier, time type** (flexible vs fixed slot), **audio languages**, what is included (food or drink only when included in the linked ticket).
- **Is it still sold?** A discontinued product gets removed or replaced. Ask before swapping it in.

## 3. Rules
- Booking links (title and button) go only to Tiqets or GetYourGuide, with `partner=thecruisedetective.com-176436` plus `tq_campaign` for Tiqets and `partner_id=YS414AJ` for GYG.
- Viator only as a review badge.
- Tiqets 40% commission applies only to some products. Ask before switching a GYG card to Tiqets for that reason.
- No em dashes. Brand and ship names stay untranslated.
- Don't claim "price guarantee" or "personally tested" unless it is true for that card.

## 4. Validate and spread to translations
```bash
python3 scripts/cards/cards.py links <page>          # link rules
python3 scripts/cards/cards.py drift <en-page>       # every translation vs EN: product, price, rating, photos
```
Fix every product, price or rating mismatch in all 8 translations in the same branch. Translate the surrounding words, never the numbers or brand names. Then `/ship`.

## 5. Report
Give the user a short table of card, old to new price and rating, what was verified where, and anything unclear. Ask about unclear items instead of guessing.
