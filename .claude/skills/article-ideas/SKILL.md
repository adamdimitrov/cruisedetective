---
name: article-ideas
description: Find, validate and rank new article ideas for thecruisedetective.com from Search Console demand, the live SERP and bookable GYG/Tiqets inventory, and keep articles/BACKLOG.md current. Use when the user says find article ideas, what should we write next, következő cikk, or before /new-article when the backlog has no validated idea.
---

# /article-ideas

The user does not hand out topics. You find them, prove each one, and keep a ranked backlog so `/new-article` can always take the top item. An idea only goes into the backlog with evidence. A guess never does.

## 1. Demand we can prove (GSC)
```bash
python3 scripts/ideas/gsc_gaps.py --days 90 --json /tmp/gaps.json
```
- **Gap topics** (`[amsterdam: private]`): query words no ranking page covers. Google already shows us for them, usually at position 25-60 with an off-topic page. Each is a candidate.
- **Refresh**: the page covers the query and ranks 8-20. Not a new article: note it under *Refresh* in the backlog (better section, filter or FAQ on the existing page).
- Merge synonyms into one candidate (`eiffel` + `tower`, `night` + `evening` only if the SERP treats them the same, see step 2).
- Ignore brand-name topics for a single operator (`marina`, `bateaux`) unless step 2 shows a review/comparison SERP. Those are refresh items for the existing card.
- Also scan `--lang all` once a month: a gap in FR or DE that EN does not have is a translation-first idea, not an EN article.

## 2. Is it a separate page? (SERP, in the user's Chrome, never the built-in browser)
Search the top 1-2 queries of the candidate on google.com in English.
- **New page** only if at least 3 of the top 5 results are pages dedicated to that modifier ("private canal cruise amsterdam" → listicles of private boats). Google treats it as its own intent.
- **Section on the existing page** if the top 5 are general guides that mention it. Then it goes under *Refresh*, not *New*.
- Note what format wins (listicle of products, informational guide, single-operator review) and what the top results lack (prices, piers, dates checked, what is not included). That gap is our angle.

## 3. Can we fill it with real products? (inventory)
Search GetYourGuide and Tiqets for the topic in that city, in Chrome. Rules from memory apply: only GYG/Tiqets-bookable products get cards (Captain Jack Amsterdam = FareHarbor link), Viator only for review badges.
- **Comparison article** needs products that really differ (price, duration, what is included, pier, group size, timing), usually 3+ from different operators or clearly different boats, each with reviews. Same rule as the `/new-article` topic gate. Near-identical listings → a refresh section, not a page.
- Write down product ids (GYG `t…`, Tiqets `p…`), price, rating, review count. These go into the backlog row.

## 4. Score and write the backlog
`articles/BACKLOG.md` has three tables: **New**, **Refresh**, **Rejected** (with the reason, so the idea is not re-researched). Score each new idea:

| factor | how |
|---|---|
| demand | GSC impressions of the topic in 90 days |
| winnable | our current position (40+ means no dedicated page yet, best upside) and SERP strength (forums/Reddit/thin pages in top 5 = easy) |
| money | avg commission of the products (Tiqets data in GEMINI.md: dinner €30-60, sightseeing €14-20, private boats high ticket) |
| fit | links naturally to and from an existing money page |

Rank by demand × winnable × money, with fit as tie-break. Keep the row short: topic, slug, target queries + impressions, SERP verdict, products (ids), angle, score, date researched.

## 5. Hand-off
- If called on its own: show the user the top 5 as a short table and say which one `/new-article` will build next. Do not wait for approval to keep researching; the user approves at the preview stage.
- If called from `/new-article`: go straight on with the top row.
- Commit `BACKLOG.md` together with the next article's branch, not as its own PR.
- An idea older than 60 days gets its inventory re-checked before it is built.
