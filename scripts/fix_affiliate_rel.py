"""Shared script: the code is kit/scripts/fix_affiliate_rel.py. Do not edit this stub.

Change it in github.com/adamdimitrov/site-kit and run python3 kit/update.py.
"""
import importlib.util as _u
import os as _os
import sys as _sys

_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "kit", "scripts", "fix_affiliate_rel.py")
_spec = _u.spec_from_file_location(__name__, _path)
_mod = _u.module_from_spec(_spec)
_mod.__dict__["__file__"] = _os.path.abspath(_path)
_sys.modules[__name__] = _mod
_spec.loader.exec_module(_mod)
