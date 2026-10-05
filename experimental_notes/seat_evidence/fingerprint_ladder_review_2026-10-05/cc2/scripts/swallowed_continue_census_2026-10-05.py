# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fingerprint_ladder_review_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 611656021700b2694692752963b7aed7e2ab1b52c80f1c8725ee48cf1f7736af
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""`except Exception: continue` is invisible to the swallowed-exception guard.

`bench/tests/test_operational_scripts.py::TestNoScriptSwallowsAnErrorIntoSilence
::test_no_bare_or_silently_swallowed_exception_handlers` flags a bare `except:`
and a broad `except Exception` whose body is EXACTLY `pass`. A handler whose body
is a lone `continue` or `break`, with no name bound and nothing recorded, is the
same defect -- the failure happened, nothing recorded it, the loop proceeded --
and the guard cannot see it.

WHY THIS IS A CENSUS AND NOT A LINT. This script exists to size the job before
anyone widens that guard. Widening it reds every site below at once, which is not
additive. The one site repaired on 2026-10-05 is
`scripts/the_blockers_are_shown_as_settled_2026-10-05.py`, because its handler
dropped a whole archived run from the numerator of a QUOTED figure while the
denominator kept it. Guarded by
`bench/tests/test_blocker_census_reports_its_own_faults_2026-10-05.py`.

The census reads the guard's own `_sources()` population, so the two can never
disagree about which files are in scope.

Run:  python3 scripts/swallowed_continue_census_2026-10-05.py
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
GUARD = REPO / "bench" / "tests" / "test_operational_scripts.py"


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="swallowed_continue_census_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--show", type=int, default=0,
                   help="print at most N sites (0 = all)")
    return p.parse_args(argv)


def _population():
    """The guard's own `_sources()`, loaded rather than reimplemented."""
    spec = importlib.util.spec_from_file_location("_guard", GUARD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_guard"] = m
    spec.loader.exec_module(m)
    return m._sources()


def silent_flow_handlers(src: str):
    """Broad handlers whose entire body is one `continue`/`break`, no name bound."""
    out = []
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, ast.ExceptHandler) or node.type is None:
            continue
        if node.name is not None:          # a bound name can still be reported
            continue
        body = [s for s in node.body
                if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
        if len(body) == 1 and isinstance(body[0], (ast.Continue, ast.Break)) \
                and ast.unparse(node.type) in ("Exception", "BaseException"):
            out.append((node.lineno, type(body[0]).__name__.lower()))
    return out


def main(argv=None) -> int:
    args = _parse_args(argv)
    srcs = _population()
    sites = []
    for path, src in sorted(srcs.items()):
        for lineno, kind in silent_flow_handlers(src):
            sites.append((str(path.relative_to(REPO)), lineno, kind))
    print("=" * 78)
    print("BROAD HANDLERS WHOSE WHOLE BODY IS `continue`/`break`")
    print("=" * 78)
    print(f"population (the guard's own _sources())   : {len(srcs)}")
    print(f"sites the existing guard cannot see       : {len(sites)}")
    print()
    shown = sites if args.show == 0 else sites[:args.show]
    for rel, lineno, kind in shown:
        print(f"  {rel}:{lineno}: except Exception: {kind}")
    if len(shown) < len(sites):
        print(f"  ... {len(sites) - len(shown)} more (pass --show 0 for all)")
    print()
    print("CONSEQUENCE. Widening the guard reds all of these at once. The")
    print("2026-10-05 repair was scoped to the one site load-bearing for a quoted")
    print("figure; the rest are recorded here rather than silently left out.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
