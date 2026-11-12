---
name: ship
description: Ship a finished change on thecruisedetective.com - preflight checks, sitemap lastmod, phone-width QA, commit, PR, merge, GSC indexing. Use when the user says ship it, mehet, merge, élesítsd, or a batch of approved page changes is ready.
---

# /ship

One pass from "approved" to "live and submitted to Google". Run it once per approved batch, not once per tweak.

## 0. Batch first
- Iterate on a preview branch until the user approves. Small follow-ups (popover speed, pill wording) go into the same branch.
- Ship only what the user approved. Never ship a `wip:` commit; squash or drop it.
- Every deploy costs Vercel build minutes and storage, so 1 PR per approved batch beats 10 PRs for one feature.

## 1. Worktree
Work happens in a worktree (global rule). If you are in the main checkout, `EnterWorktree` first. Never touch other sessions' uncommitted files.

## 2. Preflight
```bash
python3 scripts/ship/preflight.py --fix
```
It checks em dashes in added copy, `?v=` bumps for changed JS, the `webflow-sync.js` cache rule order in `vercel.json`, sitemap `lastmod` for changed pages (bumps them with `--fix`), and affiliate links on changed card pages. Fix every ✗ before going on.

## 3. Phone check
```bash
python3 scripts/qa/mobile_overflow.py
```
It tests every changed page at 375px with all popovers open. Any ✗ blocks the ship. See the `mobile-qa` skill.

## 4. Cross-language check (card pages only)
If an EN money page changed: `python3 scripts/cards/cards.py drift <en-page>`. Product, price or rating mismatches mean the translations need the same fact change (see `port-card-feature`). "behind EN" feature lists are fine to ship but tell the user about them.

## 5. Commit, PR, merge
- Conventional commit: `feat(seine): …`, `content(dinner-paris): …`, `fix(cache): …`.
- `git fetch origin && git rebase origin/main`, then push and `gh pr create`. Use one PR per batch.
- Merge with `gh pr merge --merge --delete-branch` when the user has approved the change (the default all day). If unsure, ask.

## 6. After merge
- Wait for the Vercel production deploy to finish (`vercel:status` or the deployment list), then curl one changed URL and grep for a string from the change.
- Search Console in the user's Chrome (never the built-in browser): resubmit `sitemap.xml`, then URL Inspection, then REQUEST INDEXING for each changed EN page and any translations that changed.
- Report: PR link, the pages that went live, and whether indexing was requested.

## House rules this enforces
- No em dashes in site copy, meta or JSON-LD.
- Brand, ship and site names stay untranslated.
- Booking links only go to Tiqets or GetYourGuide. Viator appears only as a review badge.
- JS is cached for a year as immutable. Bump `?v=`. The `webflow-sync.js` rule must stay last.
