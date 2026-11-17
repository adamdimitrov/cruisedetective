#!/usr/bin/env python3
"""The site's kit/ copy is exactly the released kit it claims to be.

    python3 kit/checks/check_kit.py     # exit 1 on any problem (runs in CI)

Fails when:
  1. kit/ was edited by hand: its fingerprint no longer matches kit.lock.
     Change the kit in the site-kit repo instead, release it, then run
     python3 kit/update.py in the site.
  2. .github/workflows/layout-check.yml differs from kit/ci/layout-check.yml.
  3. a check that site.json lists under local_checks is missing.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kittree import tree_sha256  # noqa: E402
from sitecfg import ROOT, SITE  # noqa: E402

KIT = os.path.join(ROOT, "kit")


def main():
    probs = []
    try:
        with open(os.path.join(ROOT, "kit.lock"), encoding="utf-8") as fh:
            lock = json.load(fh)
    except FileNotFoundError:
        lock = {}
        probs.append("kit.lock is missing: install the kit with update.py")
    if lock:
        now = tree_sha256(KIT)
        if now != lock.get("tree_sha256"):
            probs.append(f"kit/ was changed by hand (fingerprint {now[:12]} != kit.lock {str(lock.get('tree_sha256'))[:12]}); "
                         "change the site-kit repo and run kit/update.py instead")
    wf_site = os.path.join(ROOT, ".github", "workflows", "layout-check.yml")
    wf_kit = os.path.join(KIT, "ci", "layout-check.yml")
    try:
        if open(wf_site, encoding="utf-8").read() != open(wf_kit, encoding="utf-8").read():
            probs.append(".github/workflows/layout-check.yml differs from kit/ci/layout-check.yml (run kit/update.py)")
    except FileNotFoundError as e:
        probs.append(f"missing {os.path.relpath(e.filename, ROOT)}")
    for cmd in SITE.get("local_checks", []):
        script = cmd.split()[0]
        if not os.path.isfile(os.path.join(ROOT, script)):
            probs.append(f"site.json local_checks lists {script}, which does not exist")
    for p in probs:
        print(f"FAIL {p}")
    print(f"kit {lock.get('version', '?')}: {'OK' if not probs else str(len(probs)) + ' problem(s)'}")
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
