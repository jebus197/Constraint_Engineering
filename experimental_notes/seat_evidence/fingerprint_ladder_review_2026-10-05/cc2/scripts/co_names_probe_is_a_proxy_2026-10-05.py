# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3fe446674761230a48df9724978c4b52778b875487642dc56541f650b96a973a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""`co_names` is immune to comments. It is not a reachability proof.

Producer for the table in
`bench/tests/test_wiring_probe_is_a_call_not_a_mention_2026-10-05.py`.

Compiles seven one-function modules and reports, for each, whether the probed
name appears in `__code__.co_names` and `__code__.co_consts`, and whether a
CALL-family opcode consumes it. Four shapes satisfy `co_names` without being a
call (FALSE PASS) and two behaviour-preserving refactors empty it (FALSE FAIL).

Run:  python3 scripts/co_names_probe_is_a_proxy_2026-10-05.py
"""
from __future__ import annotations

import argparse
import dis
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench" / "tests"))

SHAPES = [
    ("if False: target(1)", "FALSE PASS",
     "def f(cfg):\n    if False:\n        target(1)\n    return 1\n"),
    ("if cfg.never_true: target(1)", "FALSE PASS",
     "def f(cfg):\n    if cfg.never_true:\n        target(1)\n    return 1\n"),
    ("bare mention, never called", "FALSE PASS",
     "def f(cfg):\n    target\n    return 1\n"),
    ("cfg.target (attribute)", "FALSE PASS",
     "def f(cfg):\n    return cfg.target\n"),
    ("target(cfg)  [the real thing]", "must pass",
     "def f(cfg):\n    return target(cfg)\n"),
    ("call moved into a helper", "FALSE FAIL",
     "def h(cfg):\n    target(cfg)\ndef f(cfg):\n    return h(cfg)\n"),
    ("call moved into a lambda", "FALSE FAIL",
     "def f(cfg):\n    g = lambda c: target(c)\n    return g(cfg)\n"),
    ('getattr(mod, "target")(cfg)', "FALSE PASS on co_consts",
     'def f(cfg, mod):\n    return getattr(mod, "target")(cfg)\n'),
]


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="co_names_probe_is_a_proxy_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--name", default="target", help="the probed global name")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)
    # THE PREDICATE IS IMPORTED FROM THE TEST, not re-typed here. A producer
    # carrying its own copy would report on a function the suite does not use.
    import importlib.util
    _t = REPO / "bench" / "tests" / \
        "test_wiring_probe_is_a_call_not_a_mention_2026-10-05.py"
    _spec = importlib.util.spec_from_file_location("_wiring_probe", _t)
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    _calls = _mod._calls
    name = args.name
    print("=" * 78)
    print("WHAT `co_names` / `co_consts` DO AND DO NOT ESTABLISH")
    print("=" * 78)
    print(f"{'shape':34s} {'co_names':>9s} {'co_consts':>10s} {'CALLed':>7s}  note")
    print("-" * 78)
    for label, note, src in SHAPES:
        ns: dict = {}
        exec(compile(src, "<probe>", "exec"), ns)
        co = ns["f"].__code__
        print(f"{label:34s} {str(name in co.co_names):>9s} "
              f"{str(name in co.co_consts):>10s} {str(_calls(co, name)):>7s}  {note}")
    print()
    print("READ IT THIS WAY. `co_names` beats a source-text match on comments,")
    print("docstrings and commented-out code, and on nothing else. It is not a")
    print("reachability proof, and it is MORE fragile than a grep under a")
    print("refactor that moves the call to another code object.")
    print(f"Python {sys.version.split()[0]}, dis opcode set {len(dis.opname)} entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
