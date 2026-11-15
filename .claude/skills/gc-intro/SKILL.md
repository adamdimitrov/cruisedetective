---
name: gc-intro
description: Rewrite the intro of an existing thecruisedetective article (or all of them) the Grow and Convert way, using the facts already on the page, then port it to every translation. New articles are written fully G&C instead. Use when the user says "írjuk át az introt", "G&C intro", "javítsd az introt", "minden intro", or an EN money page gets a refresh.
---

# /gc-intro

Load the `growandconvert-content` skill first. It holds the philosophy; this skill is the TCD procedure.

## Scope
- **Existing articles: intro only.** Do not touch the cards, sections or FAQs in the same pass, even if they are not G&C yet. Note big body problems for the user instead.
- **New articles: the whole article is G&C** (angle, intro, cards with pick/skip, CTAs). This skill covers only the intro part of that.
- The intro is the `<p>` elements inside `<div class="ltt-lead-copy">`. Keep the `cd-verdict-callout` aside ("Short on time?") and any `cd-bookmark-wrapper` figure as they are, after the new paragraphs.
- Statistics pages (`*-tourism-statistics`) are informational. Skip them unless the user asks; they have no booking reader.

## 1. Gather the facts from the page, never from memory
```bash
python3 scripts/cards/cards.py extract <page>
```
Pull: number of cruises compared, price range (lowest and highest card price), piers, departure times, duration, what is included, and which cards are personally tested (the page's own tested badges and the article memory). The intro may only state facts the cards below it already state. If a card price looks stale, run `verify-ota-facts` before writing.

Tested claims that are true today: Seine sightseeing top 5, Paris dinner top 5, Thames top 5, Amsterdam canal top 5, Bateaux Mouches vs Bateaux Parisiens (both). Private and NYE pages are compared, not tested. Never widen a tested claim.

## 2. Find the hook
Pick the one pitfall that makes this reader book wrong, and open with it. Examples of the shape:
- NYE: most dinner boats are back at the quay before midnight.
- Private: prices are per boat and none include pickup, so the pier decides it.
- Dinner: the same €100+ ticket buys a window table on one boat and a middle-row table on another.
Test: could a competitor's page start with the same sentence? Then it is not the hook.

## 3. Write it (2-4 short paragraphs, each under ~300 characters)
1. Hook: the reader's situation or the pitfall, with a number.
2. Proof: what I did (rode / compared side by side) and on which deciding details, with specifics (count, price range, pier, minutes).
3. Promise and transition: exactly what is below (the N best, the filter, the #1 pick) and when prices were last checked if the page shows a date.

Bold only the decision-making facts. First person singular ("I"), not "we".

Kill on sight in existing intros:
- "I embarked on a journey", "incredibly detailed rundown", "definitive answers", "genuine floating culinary gems": filler a competitor could write.
- "thousands of glowing reviews", review totals, platform names (Tiqets, GetYourGuide, Viator, Tripadvisor).
- "undercover", "to rank them honestly", anything that apologises for or narrates the method.
- Em dashes (—). Use a comma, colon or a new sentence.

## 4. Check, then show the user
- `python3 scripts/ship/preflight.py` (em dashes, links).
- Read the new intro next to the first card: every number in the intro must match a card.
- Show the user old vs new for each page and wait for approval before translating. Batch all EN pages into one approval round.

## 5. Translations
After EN approval, port the intro with `port-i18n` (translation memory: only the new strings get translated). Brand, ship and site names stay untranslated. Same structure and the same bolded facts in every language.

## 6. Ship
One PR for the approved batch via `ship`. Give the Vercel preview URL of each changed page.
