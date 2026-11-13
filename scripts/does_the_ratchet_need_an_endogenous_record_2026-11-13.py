#!/usr/bin/env python3
"""Entry B164: the 2 free panel seats disagreed about WHY a derived bound ratchets.

THE DISAGREEMENT, from the joint round of 2026-11-13, both seats having executed
their own instrument and reached opposite diagnoses of the same phenomenon:

  * cc2: the fault is DIRECTION. `max`-of-last-N is monotone non-decreasing in
    the record by construction, so it can only ever be conservative UPWARD. For
    a commit timeout -- whose too-small failure aborts a healthy commit -- upward
    is fail-safe and the ratchet is the feature. For a limit on human review
    load -- whose too-large failure admits unreviewed content -- upward is
    fail-UNSAFE. It states that fable's replacement quantity "inherits the
    defect you identified. You moved the quantity and kept the ratchet."

  * fable: the fault is the RECORD'S PROVENANCE. "a commit duration is driven by
    repo and machine (exogenous ...); a block size enters the record by passing
    the bound, so the record expands to fill the allowance." On that reading,
    per-entry review timestamps qualify because they are not downstream of the
    bound, and honoured sizes do not.

NEITHER RAN THE TEST THAT SEPARATES THEM. cc2's claim is falsifiable: drive the
SAME `max`-of-last-N bound with an EXOGENOUS record -- one the bound does not
gate -- and see whether it ratchets. If it does, cc2 is right and the quantity
is irrelevant. If it does not, the ratchet requires an ENDOGENOUS record and
fable's distinction is the load-bearing one.

THE DECISION RULE IS STATED BEFORE THE RUN so it can come out either way:
  * ENDOGENOUS (a value enters the record only if the bound admitted it):
    expect the bound to grow without limit and to bind ~never.
  * EXOGENOUS (values enter regardless of the bound):
    cc2 is right if the bound grows without limit anyway; fable is right if it
    tracks the series and binds when the series genuinely jumps.
"""
from __future__ import annotations

import pathlib
import sys

# ★ LOCATE `_cli_help` RATHER THAN ASSUME sys.path, 2026-11-13. The import was
# added without this preamble and the script stopped IMPORTING, which
# `test_operational_scripts.py` caught in the B165 clean run. It worked when the
# file was RUN, because sys.path[0] is then the script's own directory, and
# failed under `spec_from_file_location`, which sets no such entry. The caller
# this import was copied from carries the identical preamble and its comment
# records the same failure taking out 13 scripts on 2026-09-24 -- so this is a
# known defect reproduced by copying the line and not the mechanism.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

import numpy as np

FLOOR, HEADROOM, WINDOW = 300.0, 4.0, 10


def bound_with(record, stat, window):
    """The same bound shape with the statistic and the window as parameters.

    ★ THIS EXISTS BECAUSE cc2's REMEDY, AS STATED, DOES NOT WORK. Its joint-round
    position was that a bound on human load must use "an order statistic that is
    monotone NON-INCREASING in the record, or typed". Implemented as `min` over
    the SAME trailing window, that still admits everything on a drifting series:
    measured over 60 steps of 10 per cent growth, `min` of the last 10 binds 0
    times and reaches 4.269e+04.

    THE CONDITION IS EXACT AND DERIVABLE. A windowed statistic saves nothing
    whenever the series' growth ACROSS THE WINDOW stays below HEADROOM, because
    the oldest value in the window is then within a factor of HEADROOM of the
    newest. Here 1.10 ** 10 = 2.5937 against HEADROOM = 4.0, so every value is
    admitted. Only an UNWINDOWED order statistic is genuinely non-increasing:
    `min` over the whole record binds 45 of 60 and holds the bound at its floor.
    """
    w = record[-window:] if window else record
    if not w:
        return FLOOR
    return max(FLOOR, HEADROOM * stat(w))


def window_is_defeated(growth_per_step: float, window: int,
                       headroom: float = HEADROOM) -> bool:
    """True when a windowed statistic cannot bind on this growth rate.

    Derived, not typed: the oldest value in the window is `growth ** window`
    behind the newest, so a bound of `headroom x oldest` admits the newest
    exactly when that factor is below `headroom`.
    """
    return growth_per_step ** window < headroom


def bound(record: list[float]) -> float:
    """cc2's exact shape, read from scripts/cdsfl_sv.py: max(FLOOR, H * max(last N))."""
    if not record:
        return FLOOR
    return max(FLOOR, HEADROOM * max(record[-WINDOW:]))


def drive(series, endogenous: bool):
    """Run the series through the bound.

    endogenous=True  -- a value is RECORDED only if the bound admitted it, which
                        is what "the record expands to fill the allowance" means.
    endogenous=False -- every value is recorded regardless, which is what an
                        exogenously-driven quantity like a commit duration does.
    """
    record, binds, admitted = [], 0, 0
    for v in series:
        b = bound(record)
        ok = v <= b
        binds += (not ok)
        admitted += ok
        if endogenous:
            if ok:
                record.append(v)
        else:
            record.append(v)
    return {"binds": binds, "admitted": admitted,
            "final_bound": bound(record),
            "max_in_record": max(record) if record else 0.0}


def main() -> int:
    rng = np.random.default_rng(20261113)
    N = 60
    SERIES = {
        "stationary (exogenous in nature)":
            list(rng.uniform(150, 320, N)),
        "slow drift, 10 per cent per step":
            [100.0 * (1.10 ** k) for k in range(N)],
        "growth at the headroom ratio (x4)":
            [100.0 * (4.0 ** k) for k in range(min(N, 25))],
        "stationary with 1 genuine jump":
            list(rng.uniform(150, 320, N // 2)) + [50000.0]
            + list(rng.uniform(150, 320, N // 2)),
    }

    print("=" * 78)
    print("DOES max-of-last-N RATCHET? The same bound, 2 record disciplines.")
    print("=" * 78)
    print(f"  bound = max({FLOOR:.0f}, {HEADROOM:.0f} x max(last {WINDOW}))   "
          f"-- cc2's shape, read from scripts/cdsfl_sv.py")
    print()
    print(f"  {'series':36} {'record':11} {'binds':>6} {'final bound':>14}")
    rows = {}
    for name, series in SERIES.items():
        for endo in (True, False):
            r = drive(series, endogenous=endo)
            rows[(name, endo)] = r
            print(f"  {name:36} {'ENDOGENOUS' if endo else 'exogenous':11} "
                  f"{r['binds']:>6} {r['final_bound']:>14.4g}")
    print()

    print("=" * 78)
    print("THE SEPARATING CASE: slow drift, which neither reading disputes is")
    print("the shape a growing preferences block takes.")
    print("=" * 78)
    endo = rows[("slow drift, 10 per cent per step", True)]
    exo = rows[("slow drift, 10 per cent per step", False)]
    print(f"  ENDOGENOUS record: binds {endo['binds']:>3}, "
          f"final bound {endo['final_bound']:.4g}")
    print(f"  exogenous  record: binds {exo['binds']:>3}, "
          f"final bound {exo['final_bound']:.4g}")
    print()
    print("  Both grow, because the SERIES grows -- so on a growing series the")
    print("  record's provenance changes nothing and cc2 is right that the")
    print("  direction is what matters.")
    print()

    print("=" * 78)
    print("AND THE CASE THAT DECIDES IT: a STATIONARY exogenous record, which is")
    print("what a review-timestamp gap actually is.")
    print("=" * 78)
    st_exo = rows[("stationary (exogenous in nature)", False)]
    st_endo = rows[("stationary (exogenous in nature)", True)]
    print(f"  exogenous  : binds {st_exo['binds']:>3}, final bound "
          f"{st_exo['final_bound']:.4g}, max in record {st_exo['max_in_record']:.4g}")
    print(f"  ENDOGENOUS : binds {st_endo['binds']:>3}, final bound "
          f"{st_endo['final_bound']:.4g}, max in record {st_endo['max_in_record']:.4g}")
    ratio = st_exo["final_bound"] / (HEADROOM * 320.0)
    print(f"  the exogenous bound stays within {ratio:.3f} of HEADROOM x the")
    print("  series maximum, so it TRACKS the series rather than escaping it.")
    print()

    print("=" * 78)
    print("AND cc2's OWN REMEDY FAILS AS STATED, which neither seat tested.")
    print("=" * 78)
    drift = SERIES["slow drift, 10 per cent per step"]
    print(f"  {'statistic':34}{'binds':>7}{'final bound':>15}")
    for label, stat, win in (("max over last 10 (as shipped)", max, WINDOW),
                             ("MIN over last 10 (cc2's remedy)", min, WINDOW),
                             ("MIN over the WHOLE record", min, None)):
        rec, binds = [], 0
        for v in drift:
            if v > bound_with(rec, stat, win):
                binds += 1
            rec.append(v)
        print(f"  {label:34}{binds:>7}{bound_with(rec, stat, win):>15.4g}")
    g = drift[1] / drift[0]
    print(f"  growth across the window = {g:.2f} ** {WINDOW} = {g ** WINDOW:.4f} "
          f"against HEADROOM = {HEADROOM}")
    print(f"  window_is_defeated({g:.2f}, {WINDOW}) = "
          f"{window_is_defeated(g, WINDOW)}")
    assert window_is_defeated(g, WINDOW), (
        "the fixture no longer demonstrates that a windowed statistic is "
        "defeated, so this section proves nothing")
    print("  SO 'NON-INCREASING IN THE RECORD' MUST MEAN THE WHOLE RECORD.")
    print("  A windowed min grows with the series and is not non-increasing.")
    print()

    jump_exo = rows[("stationary with 1 genuine jump", False)]
    print(f"  and a stationary record with 1 genuine jump binds "
          f"{jump_exo['binds']} time(s), so the bound still REFUSES a real excursion.")
    print()

    print("=" * 78)
    print("VERDICT, against the decision rule stated before the run")
    print("=" * 78)
    # ★ THE VERDICT IS DERIVED FROM THE SERIES, NOT FROM A TYPED THRESHOLD. The
    # first version asserted `final_bound > 1e6` and FAILED on its own first
    # run, because 60 steps of 10 per cent drift reach 1.107e+05 -- the finding
    # was intact and the threshold was arbitrary. "It ratchets" does not mean
    # "it exceeds some number"; it means the bound NEVER BINDS however far the
    # series travels. That is a property of the pair, so it is read off the pair.
    drift_series = SERIES["slow drift, 10 per cent per step"]
    drift_span = max(drift_series) / min(drift_series)
    drift_runaway = (endo["binds"] == 0 and exo["binds"] == 0 and drift_span > 100)
    st_series = SERIES["stationary (exogenous in nature)"]
    st_span = max(st_series) / min(st_series)
    stationary_tracks = (
        st_exo["binds"] == 0
        and st_exo["final_bound"] <= HEADROOM * max(st_series) * 1.001)
    print(f"  the drifting series spans a factor of {drift_span:,.0f} and the")
    print(f"  bound binds {endo['binds']} time(s) endogenous, {exo['binds']} exogenous")
    print(f"  -> on a GROWING series both disciplines run away : {drift_runaway}")
    print(f"  the stationary series spans a factor of {st_span:.2f} and the bound")
    print(f"  settles at {st_exo['final_bound']:.4g} against HEADROOM x max = "
          f"{HEADROOM * max(st_series):.4g}")
    print(f"  -> on a STATIONARY exogenous series the bound TRACKS : {stationary_tracks}")
    assert drift_runaway, (
        f"the growing case no longer demonstrates the ratchet: binds "
        f"{endo['binds']}/{exo['binds']} over a span of {drift_span:,.0f}")
    assert stationary_tracks, (
        f"the stationary exogenous case no longer tracks: bound "
        f"{st_exo['final_bound']:.4g} against HEADROOM x max "
        f"{HEADROOM * max(st_series):.4g}, binds {st_exo['binds']}")
    print()
    print("  SO BOTH SEATS ARE PARTLY RIGHT AND NEITHER ALONE IS SUFFICIENT.")
    print("  cc2 is right that the record's provenance does NOT save a")
    print("  non-decreasing statistic once the underlying series grows: on slow")
    print("  drift the exogenous bound runs away exactly as the endogenous one")
    print("  does. fable is right that provenance decides whether the series")
    print("  grows AT ALL: an endogenous record grows BECAUSE the bound admits")
    print("  it, while an exogenous stationary one does not.")
    print()
    print("  THE RATCHET THEREFORE NEEDS BOTH -- a non-decreasing statistic AND")
    print("  a series that grows. Breaking EITHER stops it, which is why the 2")
    print("  diagnoses looked contradictory while both were sound.")
    print()
    print("  FOR A BOUND ON HUMAN REVIEW LOAD the safe construction satisfies")
    print("  both at once: an order statistic monotone NON-INCREASING in the")
    print("  record (cc2), over a record the bound does not gate (fable).")
    print("  Neither constraint is redundant: a non-increasing statistic over an")
    print("  endogenous record still measures only what was admitted, and a")
    print("  non-decreasing statistic over an exogenous record still runs away")
    print("  the moment the series drifts upward.")
    return 0


if __name__ == "__main__":
    # ★ `--help` MUST BE ANSWERED, NOT MERELY SURVIVED. Without this the flag is
    # ignored and the whole measurement runs, which is what
    # `test_help_is_answered_2026-09-11.py` refuses: `exit 0 but no usage line`.
    # The project's own helper is used rather than argparse, because a sibling
    # guard forbids a script carrying both.
    answer_help(__doc__, __file__)
    sys.exit(main())
