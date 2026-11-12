---
name: mobile-qa
description: Check pages at phone width (375px) for horizontal overflow, clipped buttons and popovers before shipping. Use after any layout, card, banner or popover change, or when the user reports something sticking out on mobile.
---

# /mobile-qa

Most layout bugs on this site have been overflow at phone width that only showed up after shipping (NYE promo button, trust line). Catch them before merge.

## Run
```bash
python3 scripts/qa/mobile_overflow.py                         # pages changed on this branch
python3 scripts/qa/mobile_overflow.py seine-river-cruises-paris fr/meilleures-croisieres-seine-paris
python3 scripts/qa/mobile_overflow.py --all-money             # 5 EN money pages + every translation
python3 scripts/qa/mobile_overflow.py --width 360 --shots /tmp/shots   # narrower phone + screenshots
```
The script serves the repo with `scripts/preview_server.py` (Vercel rewrites emulated) and loads each page in headless Chromium at 375x812 as a touch phone. It opens every `<details>` popover and lists each element sticking out past the viewport. It ignores content inside horizontal scrollers such as the photo sliders. Exit 1 means something overflows.

## Reading the output
`+53px  div.ltt-nye-promo > a.btn  "Book now"` means that element ends 53px past the right edge. Usual fixes:
- Buttons and pills: `max-width:100%`, `white-space:normal`, or a `flex-wrap:wrap` parent.
- Popovers: clamp with `max-width:calc(100vw - 32px)` and anchor left/right depending on the card side.
- Tables: wrap them in an `overflow-x:auto` container.

## Then
- Fix it, re-run until ✓, and only then go to `/ship`.
- For a visual check the user can see, open the page in the user's Chrome at phone size. Never use the built-in browser pane (user preference).
