#!/usr/bin/env python3
"""Card sliders hold 9-10 photos: list every listicle card under 9 that has no recorded reason.

    python3 kit/checks/check_photo_counts.py

A card under 9 photos is fine only when its listing has no more usable photos; then
`python3 scripts/photo_topup.py skip <page> <card> --reason "..."` records why (kept in the
card data as _photo_topup.skip). Everything else is topped up with scripts/photo_topup.py.

Report only (exit 0) by default, so a site can adopt the kit before its top-up is done.
site.json "photo_topup": {"strict": true} makes unexplained short cards fail the check (CI).
"""
import io
import os
import sys
from contextlib import redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
from sitecfg import SITE  # noqa: E402
import photo_topup  # noqa: E402


def main():
    with redirect_stdout(io.StringIO()):
        rows = photo_topup.scan()
    todo = [r for r in rows if not r.get("skip")]
    kept = len(rows) - len(todo)
    for r in todo:
        n = "?" if r["photos"] is None else r["photos"]
        print(f"  {r['page']} {r['card']}: {n} photos, no reason recorded ({r['url'] or 'no booking link'})")
    strict = SITE.get("photo_topup", {}).get("strict", False)
    print(f"photo counts: {len(todo)} card(s) under {photo_topup.MIN} photos to top up, "
          f"{kept} kept short with a reason" + ("" if strict or not todo else " (report only: site.json photo_topup.strict is off)"))
    if todo:
        print("  top up: python3 scripts/photo_topup.py stage|apply (see its --help); "
              "or record why: python3 scripts/photo_topup.py skip <page> <card> --reason \"...\"")
    return 1 if (strict and todo) else 0


if __name__ == "__main__":
    sys.exit(main())
