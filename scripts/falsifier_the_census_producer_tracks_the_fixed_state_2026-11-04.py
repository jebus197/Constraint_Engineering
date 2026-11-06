#!/usr/bin/env python3
"""FALSIFIER for the B108 census repair: does the producer track the FIXED state?

★ SPECIFIED BY A FREE PANEL SEAT, 2026-11-04, AND NEVER LANDED. The seat found
that the producer's `step_2` still asserted the PRE-FIX identity after the B108
fix inverted its oracle, so the producer exited 1 while its entry claimed exit 0.
It specified this falsifier alongside the repair and delivered it as a diff,
because the sandbox refused the write. 5 of that round's 10 named deliverables
never reached the tree; this was one.

TWO HALVES, AND BOTH MUST HOLD.

  HALF 1  THE FIXED CONTRACT. `broad == his + spurious`, checked by SymPy and
          independently by z3, plus the 2 structural claims the verdict rests on:
          the census reports HIS count, and names the residue separately.

  HALF 2  THE REVERSION IS CAUGHT. The pre-fix identity is DERIVED from the live
          one by swapping the broad term for the census term -- never retyped --
          and must FAIL on today's data. If it passed, the repair would be
          decorative and this falsifier would be asserting nothing.

IT IMPORTS THE PRODUCER'S OWN `step_2_the_decomposition` rather than restating
its arithmetic, so a producer and its falsifier cannot describe themselves
consistently while disagreeing (`execute-do-not-grep`).
"""
from __future__ import annotations
import importlib.util
import sys
from pathlib import Path

REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
PRODUCER = REPO / "scripts" / "the_census_counts_what_the_reader_excludes_2026-11-04.py"

fails: list[str] = []
def ck(label, got, want):
    ok = got == want
    print(f"  {'OK  ' if ok else 'FAIL'} {label:62s} {got!r}")
    if not ok: fails.append(label)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec); sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    #: ANSWER `--help` BEFORE DOING ANY WORK. His rule, measured: a flag
    #: that runs the whole measurement can cost machine time or money,
    #: and 15 of 17 runners once billed for it.
    import sys as _sys, pathlib as _pl
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _ah
    _ah(__doc__, __file__)
    if not PRODUCER.is_file():
        print(f"producer absent at {PRODUCER}"); return 2
    prod = _load(PRODUCER, "census_producer")
    reader = prod._reader()
    if reader is None:
        print("the founder's Responses corpus is unreadable; "
              "nothing can be falsified. UNVERIFIED, not passed.")
        return 2
    s2 = prod.step_2_the_decomposition(reader)

    b, h, s = s2["broad_total"], s2["his_total"], s2["spurious"]
    c = s2["census_total"]
    print("0. THE FIGURES, FROM THE PRODUCER'S OWN step_2")
    print(f"   broad {b}   his {h}   spurious {s}   census {c}")

    print("\nHALF 1 -- THE FIXED CONTRACT")
    import sympy as sp
    b_, h_, s_ = sp.symbols("b h s", integer=True, nonnegative=True)
    live = sp.Eq(b_, h_ + s_)
    ck("SymPy: broad = his + spurious holds on today's data",
       bool(live.subs({b_: b, h_: h, s_: s})), True)
    from z3 import Int, Solver, unsat
    zb, zh, zs = Int("b"), Int("h"), Int("s")
    sol = Solver(); sol.add(zb == b, zh == h, zs == s, zb != zh + zs)
    ck("z3: no model contradicts it", sol.check() == unsat, True)
    ck("the producer's own python flag agrees", s2["exact_python"], True)
    ck("the producer's own sympy flag agrees", s2["exact_sympy"], True)
    ck("the census reports HIS count, not the broad one",
       s2["census_reports_his_count"], True)
    ck("and names the excluded residue separately",
       s2["residue_is_named_by_the_census"], True)

    print("\nHALF 2 -- THE REVERSION MUST BE CAUGHT")
    #: DERIVED, NOT RETYPED. The pre-fix identity is the live one with the broad
    #: term replaced by the census term. Deriving it means a change to the live
    #: identity cannot leave this half testing a stale formula.
    c_ = sp.Symbol("c", integer=True, nonnegative=True)
    prefix = live.subs(b_, c_)
    ck("the derived pre-fix identity is census = his + spurious",
       str(prefix), str(sp.Eq(c_, h_ + s_)))
    ck("and it is NOT the live identity", str(prefix) == str(live), False)
    reverted_holds = bool(prefix.subs({c_: c, h_: h, s_: s}))
    ck("SymPy: the pre-fix identity FAILS on today's data", reverted_holds, False)
    sol2 = Solver(); zc = Int("c")
    sol2.add(zc == c, zh == h, zs == s, zc == zh + zs)
    ck("z3: and is unsatisfiable, so the repair is load-bearing",
       sol2.check() == unsat, True)
    print(f"   the gap the repair closed: census {c} against his+spurious {h + s}"
          f"  -> difference {c - (h + s)}")

    print()
    if fails:
        print(f"{len(fails)} FAILED -- the producer does NOT track the fixed state:")
        for f in fails: print(f"   - {f}")
        return 1
    print("both halves hold: the contract is satisfied and its reversion is caught.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
