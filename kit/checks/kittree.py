"""Fingerprint of a kit/ folder, so a site can prove its copy is untouched.

No side effects on import: used by update.py (in the kit source and in a site)
and by check_kit.py.
"""
import hashlib
import os

SKIP_DIRS = {"__pycache__", ".git"}


def kit_files(kit_dir):
    """Every file under kit_dir, repo-style relative paths, sorted."""
    out = []
    for dirpath, dirnames, filenames in os.walk(kit_dir):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for f in filenames:
            if f.endswith(".pyc") or f == ".DS_Store":
                continue
            out.append(os.path.relpath(os.path.join(dirpath, f), kit_dir).replace(os.sep, "/"))
    return sorted(out)


def tree_sha256(kit_dir):
    """One hash over every file's path and bytes."""
    h = hashlib.sha256()
    for rel in kit_files(kit_dir):
        h.update(rel.encode() + b"\0")
        with open(os.path.join(kit_dir, rel), "rb") as fh:
            h.update(hashlib.sha256(fh.read()).digest())
    return h.hexdigest()
