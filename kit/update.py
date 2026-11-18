#!/usr/bin/env python3
"""Install or update the kit in a site repo.

From a site repo (the usual way):
    python3 kit/update.py                      # latest main of github.com/adamdimitrov/site-kit
    python3 kit/update.py --ref v0.2.0         # a released version
    python3 kit/update.py --source ../site-kit # a local site-kit checkout

From a site-kit checkout (first install, or to update several sites at once):
    python3 update.py --site ../budapest-adventures --site ../cruisedetective

What it does, per site:
  1. replaces <site>/kit/ with an exact copy of the kit (never edit kit/ by hand),
  2. writes <site>/kit.lock (version, source commit, fingerprint),
  3. copies kit/ci/layout-check.yml to <site>/.github/workflows/layout-check.yml,
  3b. sites with "runtime": {"shared": true} in site.json: publishes /js/site-runtime.js
      and points every page at its current ?v= (move pages over once with
      python3 kit/runtime/runtime.py migrate),
  3b'. sites with "listicle": {"pages": [...]}: publishes the shared card design files
      (/css/listicle-*.css, /js/listicle-*.js) and points those pages at their current ?v=,
  3c. writes a stub scripts/<name>.py for every shared script in kit/scripts/ (the stub loads
      the kit copy, so old commands and imports keep working),
  4. runs kit/checks/check_all.py (skip with --no-check).
It never commits, pushes or deploys: review the diff, open a PR, merge when approved.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_URL = "https://github.com/adamdimitrov/site-kit"
NOT_SHIPPED = {".git", ".github", "tests", "__pycache__"}

sys.path.insert(0, os.path.join(HERE, "checks"))
from kittree import tree_sha256  # noqa: E402


def is_kit_source(d):
    return os.path.isfile(os.path.join(d, "VERSION")) and not os.path.isfile(os.path.join(os.path.dirname(d), "kit.lock")) \
        and os.path.basename(d) != "kit"


def source_commit(src):
    try:
        return subprocess.run(["git", "-C", src, "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def install(src, site, check=True):
    site = os.path.abspath(site)
    if not os.path.isfile(os.path.join(site, "site.json")):
        sys.exit(f"{site}: no site.json; write one first (see kit README)")
    kit = os.path.join(site, "kit")
    if os.path.isdir(kit):
        shutil.rmtree(kit)
    shutil.copytree(src, kit, ignore=shutil.ignore_patterns(*NOT_SHIPPED, "*.pyc", ".DS_Store"))
    version = open(os.path.join(src, "VERSION"), encoding="utf-8").read().strip()
    lock = {"version": version, "source": REPO_URL, "commit": source_commit(src), "tree_sha256": tree_sha256(kit)}
    with open(os.path.join(site, "kit.lock"), "w", encoding="utf-8") as fh:
        json.dump(lock, fh, indent=2)
        fh.write("\n")
    if json.load(open(os.path.join(site, "site.json"), encoding="utf-8")).get("runtime", {}).get("shared"):
        sys.path.insert(0, os.path.join(kit, "runtime"))
        import runtime  # noqa: E402
        runtime.publish(site)
        sys.path.pop(0)
        sys.modules.pop("runtime", None)
    if json.load(open(os.path.join(site, "site.json"), encoding="utf-8")).get("listicle", {}).get("pages"):
        sys.path.insert(0, os.path.join(kit, "runtime"))
        import listicle  # noqa: E402
        listicle.publish(site)
        sys.path.pop(0)
        sys.modules.pop("listicle", None)
    sys.path.insert(0, os.path.join(kit, "scripts"))
    import shim  # noqa: E402
    shim.write_stubs(site)
    sys.path.pop(0)
    sys.modules.pop("shim", None)
    wf = os.path.join(site, ".github", "workflows")
    os.makedirs(wf, exist_ok=True)
    shutil.copyfile(os.path.join(kit, "ci", "layout-check.yml"), os.path.join(wf, "layout-check.yml"))
    print(f"{site}: kit {version} installed ({lock['tree_sha256'][:12]})")
    if check:
        r = subprocess.run([sys.executable, "kit/checks/check_all.py"], cwd=site)
        if r.returncode != 0:
            print(f"{site}: checks FAILED, fix before opening the PR")
            return False
    return True


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", action="append", help="site repo to update (default: the site this kit/ sits in)")
    ap.add_argument("--source", help="local site-kit checkout to install from")
    ap.add_argument("--ref", default="main", help="branch or tag to fetch when no --source (default: main)")
    ap.add_argument("--no-check", action="store_true")
    args = ap.parse_args()

    sites = args.site or ([os.path.dirname(HERE)] if os.path.basename(HERE) == "kit" else [])
    if not sites:
        sys.exit("which site? pass --site <site repo>")

    tmp = None
    if args.source:
        src = os.path.abspath(args.source)
    elif is_kit_source(HERE):
        src = HERE
    else:
        tmp = tempfile.mkdtemp(prefix="site-kit-")
        subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", args.ref, REPO_URL, tmp], check=True)
        src = tmp
    try:
        ok = all([install(src, s, check=not args.no_check) for s in sites])
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
