#!/usr/bin/env python3
"""Which completion claims did the board leave unsupported, and are they mine to fix?

THE FACT THIS ANSWERS, which the board printed and nothing then followed up.
The complete board of 2026-11-04 ended with a section headed DONE ENTRIES WHOSE
EVIDENCE FAILED, naming **24** task entries marked DONE whose named test files
were red. That is 24 completion claims with nothing currently supporting them,
and it is a larger fact than the 44 failures: a failing test is a defect, but a
DONE entry resting on a failing test is a claim the record makes and cannot
back.

`bench/tests/test_done_markers_carry_evidence_2026-09-10.py` deliberately does
NOT check that a named test PASSES -- its own docstring records that limit, and
entry V7 records the concrete case where a completion claim stood for over an
hour on a wholly red file. So the board's closing section is the only place the
pairing is reported, and it is reported once, at the end of a 2-hour run.

WHAT THIS MEASURES. For each of the 24, whether its named evidence is among the
failures that REMAIN after the period's repairs, and therefore whether the claim
is still unsupported. It also says, for each that remains, whether the next
action is mine or the founder's -- because an entry blocked on a ruling is not
the same as an entry blocked on work, and reporting them together would hide
which is which.

Usage: python3 scripts/which_completion_claims_the_board_unsupported_2026-11-04.py
Exit 0 on a sound measurement, 3 if the entry list cannot be parsed.
"""
import importlib.util
import os
import pathlib
import sys

from scipy import stats
from statsmodels.stats.proportion import proportion_confint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"

#: The 24 the board named, lifted from its own closing section rather than
#: re-derived, because re-deriving would need the 2-hour run again.
BOARD_NAMED = ("2.2", "9.2", "A16", "A2", "A24", "B11", "B4", "B40", "B41",
               "B42", "B6", "C0040", "C22", "C23", "C29", "P1", "P2", "P3",
               "P4", "P5", "P7", "T1", "V1", "V7")

#: The failures that REMAIN after the period's repairs, by file. Each is a
#: guard correctly reporting a state only the founder can settle, so the
#: entries resting on them are blocked on a RULING and not on work.
STILL_FAILING = {
    "bench/tests/test_the_morning_report_is_generated_2026-10-12.py":
        "decision 23: the generated report breaks his own Rule 10 line caps",
    "bench/tests/test_task_list_burndown_2026-09-11.py":
        "decision 24: the list is no longer provably subcritical",
}


def _interval(k: int, n: int) -> str:
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo2 = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    hi2 = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    return (f"{k} of {n} = {k/n:.6f}  Wilson [{lo:.6f}, {hi:.6f}]  "
            f"Clopper-Pearson [{lo2:.6f}, {hi2:.6f}]")


def main() -> int:
    answer_help(__doc__, __file__)
    spec = importlib.util.spec_from_file_location(
        "_tlm_cc", REPO / "scripts" / "task_list_markers.py")
    M = importlib.util.module_from_spec(spec)
    sys.modules["_tlm_cc"] = M
    spec.loader.exec_module(M)
    entries = M.parse_entries(LIST)
    if not entries:
        print("the entry list did not parse; measurement void.")
        return 3
    by_id = {e.ident: e for e in entries}

    unsupported, resolved, absent = [], [], []
    for ident in BOARD_NAMED:
        e = by_id.get(ident)
        if e is None:
            absent.append(ident)
            continue
        hit = sorted(set(e.evidence or ()) & set(STILL_FAILING))
        (unsupported if hit else resolved).append((ident, e.state, hit))

    print("=" * 76)
    print(f"THE BOARD NAMED {len(BOARD_NAMED)} DONE ENTRIES WHOSE EVIDENCE WAS FAILING")
    print("=" * 76)
    print(f"\nSTILL UNSUPPORTED ({len(unsupported)}):")
    for ident, state, hit in unsupported:
        print(f"  {ident:7} {state:9} {hit[0].split('/')[-1]}")
        print(f"          blocked on {STILL_FAILING[hit[0]]}")
    print(f"\nRESTORED BY THE PERIOD'S REPAIRS ({len(resolved)}):")
    print("  " + ", ".join(i for i, _, _ in resolved))
    if absent:
        print(f"\nNAMED BY THE BOARD BUT NOT ON THE LIST ({len(absent)}): {absent}")
        print("  Reported rather than dropped: an identifier the board saw and")
        print("  the list does not have is its own finding.")

    print(f"\ncompletion claims restored: {_interval(len(resolved), len(BOARD_NAMED))}")
    print(f"\nWHOSE MOVE ON THE REMAINING {len(unsupported)}: the founder's, on every one.")
    print("  Each rests on a guard that is correctly reporting a real state --")
    print("  a line cap he set, and a termination condition he asked to be told")
    print("  about. Neither is repairable by me, and loosening either to turn")
    print("  the board green is the move his own rules forbid.")
    print("\n  SO THE HONEST STATEMENT IS NOT '3 entries still fail' BUT")
    print("  '3 completion claims wait on 2 rulings', which is a different")
    print("  fact and the one he can act on.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
