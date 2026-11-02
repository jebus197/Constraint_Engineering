#!/usr/bin/env python3
"""P-PASS the tail-read fix by EXECUTING both forms against the same transcript.

`execute-do-not-grep` (2026-09-04): a test that reads the source establishes only
that the source describes itself consistently. Where both forms exist as live
code the test must CALL them and compare outputs. The pre-change copy is kept at
`work_not_narrate.py.bak-20261102-timeout` precisely so this comparison can run.

WHAT WOULD FALSIFY THE FIX: any input on which the two forms return different
(calls, prose, commit, had_d), or a different turn key, or a different verdict.
A faster hook that decides differently is not a fix, it is a second defect.
"""
from __future__ import annotations
import importlib.util, pathlib, sys, time

# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# project has already had a helper import break when a script moved.
import sys as _sys, pathlib as _pl
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

HOOKS = pathlib.Path.home() / ".claude" / "hooks"
NEW = HOOKS / "work_not_narrate.py"
# The pre-change form, copied to a .py path because importlib refuses a
# .bak suffix -- it returned spec=None and the script CRASHED rather than
# quietly comparing a module against itself, which is the correct failure.
OLD = pathlib.Path("/private/tmp/claude-501/-Users-georgejackson-Developer-Projects/"
                   "a07b3790-0a2a-4978-aedb-bd842c0493d3/scratchpad/wnn_old_form.py")
T = pathlib.Path("/Users/georgejackson/.claude/projects/"
                 "-Users-georgejackson-Developer-Projects/"
                 "a07b3790-0a2a-4978-aedb-bd842c0493d3.jsonl")


def load(p: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    answer_help(__doc__, __file__)
    if not OLD.is_file():
        print(f"NO PRE-CHANGE COPY at {OLD}; the comparison cannot run and")
        print("nothing is concluded. That is a result, not a pass.")
        return 1
    old, new = load(OLD, "wnn_old"), load(NEW, "wnn_new")
    print("=" * 78)
    print("TAIL READ vs FULL READ — EXECUTED, NOT INSPECTED")
    print("=" * 78)
    print(f"  transcript: {T.stat().st_size:,} bytes")

    t0 = time.perf_counter(); o_sig = old.turn_signals(T); t_old = time.perf_counter() - t0
    t0 = time.perf_counter(); n_sig = new.turn_signals(T); t_new = time.perf_counter() - t0
    t0 = time.perf_counter(); o_key = old._turn_key(T); tk_old = time.perf_counter() - t0
    t0 = time.perf_counter(); n_key = new._turn_key(T); tk_new = time.perf_counter() - t0

    ok = True
    print(f"\n  turn_signals  OLD {t_old:7.3f} s -> {o_sig}")
    print(f"                NEW {t_new:7.3f} s -> {n_sig}")
    if o_sig != n_sig:
        ok = False; print("    *** DIFFERENT. The fix changes the decision. REJECT. ***")
    else:
        print(f"    IDENTICAL. speed-up {t_old/max(t_new,1e-9):.1f}x")
    print(f"\n  _turn_key     OLD {tk_old:7.3f} s -> {o_key!r}")
    print(f"                NEW {tk_new:7.3f} s -> {n_key!r}")
    if o_key != n_key:
        ok = False; print("    *** DIFFERENT. REJECT. ***")
    else:
        print(f"    IDENTICAL. speed-up {tk_old/max(tk_new,1e-9):.1f}x")

    # The decision itself, over the full input lattice, both forms.
    print(f"\n  verdict() OVER THE FULL INPUT LATTICE (both forms)")
    diffs = 0; n = 0
    for calls in (0, 5, 6, 21, 40):
        for prose in (0, 1200, 3000):
            for commit in (False, True):
                for had_d in (False, True):
                    for n_open in (0, 1, 12):
                        for raised in (False, True):
                            n += 1
                            a, _ = old.verdict(calls, prose, commit, had_d, n_open, "B20", raised)
                            b, _ = new.verdict(calls, prose, commit, had_d, n_open, "B20", raised)
                            if a != b:
                                diffs += 1
    print(f"    {n} input combinations, {diffs} disagreement(s)")
    if diffs:
        ok = False

    # Does the whole hook now fit the budget? Sum of the three reads it makes.
    total = t_new + tk_new
    print(f"\n  BUDGET: Claude Code kills a Stop hook at 15.000 s")
    print(f"    OLD, the two readers alone : {t_old + tk_old:7.3f} s"
          f"  {'OVER' if t_old + tk_old > 15 else 'under'}")
    print(f"    NEW, the two readers alone : {total:7.3f} s"
          f"  {'OVER' if total > 15 else 'under'}")
    print(f"    (the old hook made a THIRD full read for the blocker probe,")
    print(f"     so its real cost was higher than the figure above)")

    print("\n" + "=" * 78)
    if ok:
        print("BEHAVIOUR PRESERVED AND THE HOOK NOW FITS ITS BUDGET.")
        return 0
    print("THE FIX CHANGES BEHAVIOUR. It must not ship in this form.")
    return 2


if __name__ == "__main__":
    sys.exit(main())
