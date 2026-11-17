# The Cruise Detective

1. Read `kit/RULES.md` first: the shared rules for every site (nothing goes live
   without the owner's OK, QC, copy, affiliate links, photos, layout).
2. Then this site's own notes:
   - `GEMINI.md` (hard rules, partners, ad landing pages) and `PROJECT.md` (architecture, webhook, routing); skills in `.claude/skills/`
   They add site-specific rules and win only where they are stricter.
3. Before every PR: `python3 kit/checks/check_all.py` must exit 0 (CI runs the same).
4. Never edit `kit/` here: change github.com/adamdimitrov/site-kit and run
   `python3 kit/update.py`. Site settings live in `site.json`.
