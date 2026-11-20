#!/usr/bin/env python3
"""Run every QC check for this site, in one go. CI runs exactly this.

    python3 kit/checks/check_all.py

Order: the kit's own integrity, then the site's local checks listed in
site.json (local_checks, e.g. its menu/sitemap sync and affiliate rel check;
these move into the kit in phase 4), then the shared kit checks.
Every check runs even when an earlier one fails; exit 1 if any failed.
"""
import os
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitecfg import ROOT, SITE  # noqa: E402

KIT_CHECKS = [
    "kit/checks/check_kit.py",
    "kit/checks/check_lazy_images.py",
    "kit/checks/check_filters.py",
    "kit/checks/check_archive.py",
    "kit/checks/check_listicle_layout.py",
    "kit/checks/check_gallery_clip.py",
    "kit/checks/check_photo_counts.py",
]


def main():
    cmds = [KIT_CHECKS[0]] + list(SITE.get("local_checks", [])) + KIT_CHECKS[1:]
    failed = []
    for cmd in cmds:
        print(f"\n=== {cmd}", flush=True)
        r = subprocess.run([sys.executable] + shlex.split(cmd), cwd=ROOT)
        if r.returncode != 0:
            failed.append(cmd)
    print("\n=== summary")
    for cmd in cmds:
        print(f"{'FAIL' if cmd in failed else 'ok  '}  {cmd}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
