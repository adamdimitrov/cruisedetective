#!/usr/bin/env python3
"""Nothing still calls an archived one-off script.

    python3 kit/checks/check_archive.py     # exit 1 on any problem (runs in CI)

One-off scripts live in scripts/archive/ (see its README): running one again can write an
old state back over the current pages. This check fails when a script, shell script,
workflow, skill or site setting outside the archive names an archived script, e.g. a new
script that imports an archived helper or a skill that tells a session to run one.
Docs, notes and the archive itself may mention them.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitecfg import ROOT  # noqa: E402

ARCHIVE = "scripts/archive/"
CALLERS = (".py", ".sh", ".yml", ".yaml", ".js", ".mjs")
CALLER_FILES = ("site.json", "vercel.json", "package.json")


def main():
    files = subprocess.run(["git", "-c", "core.quotepath=off", "ls-files", "-z"], cwd=ROOT,
                           capture_output=True, text=True).stdout.split("\0")
    archived = {}
    for f in files:
        if f.startswith(ARCHIVE) and f.endswith(".py"):
            name = os.path.basename(f)[:-3]
            archived.setdefault(name, f)
    live = {os.path.basename(f)[:-3] for f in files if f.endswith(".py") and not f.startswith(ARCHIVE)}
    names = {n: f for n, f in archived.items() if n not in live}  # a live script of the same name wins
    if not names:
        print("archive: nothing archived")
        return 0
    pat = re.compile(r"(?<![\w-])(" + "|".join(re.escape(n) for n in sorted(names, key=len, reverse=True)) + r")(?:\.py)?(?![\w-])")
    problems = []
    for f in files:
        if not f or f.startswith((ARCHIVE, "kit/", ".agents/", "drafts/", "node_modules/")):
            continue
        is_skill = f.startswith(".claude/") and f.endswith(".md")
        if not (f.endswith(CALLERS) or os.path.basename(f) in CALLER_FILES or is_skill):
            continue
        if f.endswith(".js") and not f.startswith("scripts/"):
            continue  # served front-end code: plain words, not script calls
        try:
            text = open(os.path.join(ROOT, f), encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in pat.finditer(text):
            problems.append(f"{f}: names archived script {names[m.group(1)]}")
            break
    for p in problems:
        print("FAIL", p)
    print(f"archive: {len(names)} archived script(s), {len(problems)} caller(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
