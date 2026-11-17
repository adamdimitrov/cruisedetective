"""Shared site scripts: the code lives in kit/scripts/, each site keeps a stub in scripts/.

The stub (written by kit/update.py, checked by kit/checks/check_kit.py) loads the kit copy
under its old name, so `python3 scripts/<name>.py ...` and `import <name>` keep working.
Never edit the stub or kit/scripts/ in a site: change github.com/adamdimitrov/site-kit.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
NOT_SHARED = {"shim.py"}

STUB = '''"""Shared script: the code is kit/scripts/{name}. Do not edit this stub.

Change it in github.com/adamdimitrov/site-kit and run python3 kit/update.py.
"""
import importlib.util as _u
import os as _os
import sys as _sys

_path = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "kit", "scripts", "{name}")
_spec = _u.spec_from_file_location(__name__, _path)
_mod = _u.module_from_spec(_spec)
_mod.__dict__["__file__"] = _os.path.abspath(_path)
_sys.modules[__name__] = _mod
_spec.loader.exec_module(_mod)
'''


def shared():
    return sorted(f for f in os.listdir(HERE) if f.endswith(".py") and f not in NOT_SHARED)


def stub(name):
    return STUB.format(name=name)


def write_stubs(site):
    os.makedirs(os.path.join(site, "scripts"), exist_ok=True)
    for name in shared():
        with open(os.path.join(site, "scripts", name), "w", encoding="utf-8") as fh:
            fh.write(stub(name))


def stub_problems(site):
    out = []
    for name in shared():
        p = os.path.join(site, "scripts", name)
        try:
            ok = open(p, encoding="utf-8").read() == stub(name)
        except FileNotFoundError:
            out.append(f"scripts/{name} is missing (run kit/update.py)")
            continue
        if not ok:
            out.append(f"scripts/{name} was edited by hand; it must be the kit stub "
                       f"(change kit/scripts/{name} in site-kit, then run kit/update.py)")
    return out
