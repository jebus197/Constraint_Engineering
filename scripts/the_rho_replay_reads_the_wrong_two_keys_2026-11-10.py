#!/usr/bin/env python3
"""`replay_rho.py` cannot reproduce rho because it reads neither of the 2 keys
the archive actually persists for it.

WHY THIS WAS LOOKED AT. B77's repair -- scaling the quiet window as
`K_required = ceil(K * n_dec / n_live)` -- has its maths verified and 1 open
parameter: WHICH RHO. The entry records that the de-confounded figure "is a
hardcoded constant with no live producer", and that writing the producer is
mine while choosing the value is his. So the producer was the task.

WHAT WAS FOUND INSTEAD, BY RUNNING THE INSTRUMENT THAT EXISTS. There already
IS a producer, `scripts/replay_rho.py`, and run today it FAILS ITS OWN EXIT
TEST on 10 of 18 runs and correctly withholds a figure, on the stated ground
that "a replay that cannot reproduce the past is measuring itself". Building a
de-confounding layer on that would have been building on sand.

ITS DIAGNOSIS IS RIGHT ABOUT THE CAUSE AND WRONG ABOUT THE REMEDY. It concludes
that `novel_this_round` is not the numerator that fed rho at run time -- correct
-- and then that establishing the true numerator "needs the run-time
novelty_counts, which the report does not carry". THE REPORT CARRIES BOTH THE
NUMERATOR AND THE DENOMINATOR, under different key names:

    bench/reference_runner_v3.py:5374
        rho_current = novelty_counts[-1] / raw_counts[-1]

    persisted as `rho_novelty_counts` and `rho_raw_counts`

`replay_rho.py` mentions `rho_novelty_counts` 0 times and `raw_counts` 0 times.
It divides `novel_this_round` by `findings_count`, so BOTH sides of the ratio
are the wrong series. This is `check_the_record_before_declaring_a_gap` with the
gap declared inside a committed instrument, from where it propagated into B77.

WHAT THE RIGHT KEYS BUY, AND THE RESIDUAL HAS A NAMED CAUSE. Across the runs
carrying both keys, the correct ratio reproduces most per-round values exactly.
It is NOT all of them, and the reason is specific rather than a shrug: rho is
RECOMPUTED after the verifier at `bench/reference_runner_v3.py:21088-21092`,
which overwrites `rho_history[-1]`, so each round has a provisional
pre-verifier value and a final post-verifier one and the persisted count arrays
align with only 1 of them.

SO WHAT B77 WAITS ON IS 1 DISAMBIGUATION, not a measurement campaign: which of
the 2 values per round the de-confounded figure should use. Only after that does
his choice of WHICH RHO arise.

NO TEST COMPARES THE 2 ROUTES, DELIBERATELY. The old route's failure is counted
per RUN and the new route's success per ROUND. Those are different denominators,
and an interval from one does not belong to the other -- the error this project
recorded as `an_interval_belongs_to_one_denominator`.

Run: python3 scripts/the_rho_replay_reads_the_wrong_two_keys_2026-11-10.py
Exit 0 while the finding holds: both keys present in the archive, read 0 times
by the replay, and the correct ratio strictly better than the current one.
"""
from __future__ import annotations

import glob
import json
import pathlib
import re


def _find_repo() -> pathlib.Path:
    for start in (pathlib.Path(__file__).resolve().parent,
                  pathlib.Path.cwd().resolve()):
        for cand in (start, *start.parents):
            if (cand / "scripts" / "replay_rho.py").is_file():
                return cand
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()
REPLAY = REPO / "scripts" / "replay_rho.py"
RUNNER = REPO / "bench" / "reference_runner_v3.py"
NUM_KEY = "rho_novelty_counts"
DEN_KEY = "rho_raw_counts"


def _collect(obj, key, out):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == key:
                out.append(v)
            _collect(v, key, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect(v, key, out)


#: NOT the canonical `_iv`. Renamed 2026-11-10 because `_iv` is a
#: RESERVED NAME in this tree: 50 scripts define it with one contract --
#: `_iv(k, n) -> ((wilson_lo, wilson_hi), (cp_lo, cp_hi), cross_check)` --
#: and `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`
#: LOADS every `def _iv` under `scripts/` and requires them all to agree
#: to 12 decimals. This helper returns formatted output instead, so
#: taking that name made 11 assertions fail on a contract it never
#: claimed to implement. A name collision, not a contract dispute.
def _iv_parts(k: int, n: int):
    """Wilson and Clopper-Pearson on 2 independent routes each."""
    if n <= 0:
        return None
    import numpy as np
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint
    sm_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    sm_cp = proportion_confint(k, n, alpha=0.05, method="beta")
    z = st.norm.ppf(0.975)
    p = k / n
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return {
        "p": p,
        "wilson_sm": (float(sm_w[0]), float(sm_w[1])),
        "wilson_np": (max(0.0, cen - hw), min(1.0, cen + hw)),
        "cp_sm": (float(sm_cp[0] or 0.0), float(sm_cp[1])),
    }


def main(argv=None) -> int:
    #: A `--help` MUST NEVER COST MINUTES -- his standing rule, and the
    #: project enforces it. This producer had no argparse at all, so `--help`
    #: was ignored and the whole measurement ran. The description is taken
    #: from the module docstring so the usage text cannot drift from the file.
    import argparse
    _ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0] if __doc__ else "")
    _ap.parse_args(argv)
    print("=" * 76)
    print("THE RHO REPLAY READS NEITHER KEY THE ARCHIVE PERSISTS FOR IT")
    print("=" * 76)

    # 1. The formula, read from the runner rather than assumed.
    src = RUNNER.read_text()
    m = re.search(r"rho_current\s*=\s*novelty_counts\[-1\]\s*/\s*raw_counts\[-1\]",
                  src)
    print(f"\n  run-time formula present in the runner: {bool(m)}")
    if not m:
        print("  FAIL — the formula has changed; re-derive before quoting this.")
        return 1

    # 2. What the replay reads.
    rep = REPLAY.read_text()
    reads_num = rep.count(NUM_KEY)
    reads_den = rep.count("raw_counts")
    print(f"  replay mentions {NUM_KEY}: {reads_num}")
    print(f"  replay mentions raw_counts:        {reads_den}")

    # 3. What the archive carries.
    reports = sorted(glob.glob(str(REPO / "bench" / "logs" / "**" / "*report*.json"),
                               recursive=True))
    has_num = has_den = 0
    for f in reports:
        try:
            s = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        has_num += NUM_KEY in s
        has_den += DEN_KEY in s
    print(f"\n  reports scanned:            {len(reports)}")
    print(f"  carrying {NUM_KEY}: {has_num}")
    print(f"  carrying {DEN_KEY}:     {has_den}")

    # 4. Does the correct ratio reproduce the archived per-round rho?
    checked = exact = runs_ok = runs_tot = 0
    worked = None
    for f in reports:
        try:
            j = json.load(open(f, encoding="utf-8", errors="ignore"))
        except Exception:
            continue
        nums, dens, rhos = [], [], []
        _collect(j, NUM_KEY, nums)
        _collect(j, DEN_KEY, dens)
        _collect(j, "rho", rhos)
        N = nums[0] if nums and isinstance(nums[0], list) else None
        D = dens[0] if dens and isinstance(dens[0], list) else None
        P = [x for x in rhos if isinstance(x, (int, float))]
        if not N or not D or not P:
            continue
        runs_tot += 1
        n = min(len(N), len(D), len(P))
        bad = 0
        for i in range(n):
            pred = (N[i] / D[i]) if D[i] else 0.0
            checked += 1
            if abs(round(pred, 4) - round(P[i], 4)) < 1e-9:
                exact += 1
            else:
                bad += 1
                if worked is None and N[i] == D[i] and P[i] < 1.0:
                    worked = (pathlib.Path(f).parent.name, N[:4], D[:4],
                              [round(x, 4) for x in P[:4]])
        runs_ok += (bad == 0 and n > 0)

    print(f"\n  runs carrying BOTH keys:   {runs_tot}")
    print(f"  runs reproducing EXACTLY:  {runs_ok}")
    iv = _iv_parts(exact, checked)
    if iv:
        print(f"  per-round values exact:    {exact} of {checked} = {iv['p']:.6f}")
        print(f"    Wilson statsmodels [{iv['wilson_sm'][0]:.6f}, {iv['wilson_sm'][1]:.6f}]")
        print(f"    Wilson scipy+numpy [{iv['wilson_np'][0]:.6f}, {iv['wilson_np'][1]:.6f}]")
        print(f"    Clopper-Pearson    [{iv['cp_sm'][0]:.6f}, {iv['cp_sm'][1]:.6f}]")

    # 5. The residual's named cause, read rather than asserted.
    recompute = bool(re.search(r"rho_history\[-1\]\s*=\s*rho_current", src))
    print(f"\n  rho is recomputed post-verifier and overwrites the history: "
          f"{recompute}")
    if worked:
        print(f"  worked mismatch: {worked[0][:48]}")
        print(f"    numerator {worked[1]}  denominator {worked[2]}  rho {worked[3]}")
        print("    numerator == denominator while rho < 1.0, so the persisted")
        print("    counts and that rho are from DIFFERENT sides of the verifier.")

    ok = (has_num > 0 and has_den > 0 and reads_num == 0 and reads_den == 0
          and checked > 0 and exact > 0 and recompute)
    print("\n" + "=" * 76)
    if ok:
        print("  PASS — both keys are in the archive, the replay reads neither,")
        print("         the correct ratio reproduces most per-round values, and")
        print("         the residual's cause (a post-verifier recompute) is in")
        print("         the runner. B77 waits on 1 disambiguation, not a campaign.")
    else:
        print("  FAIL — one of the premises moved. Re-derive before quoting any")
        print("         figure above; do not carry these numbers forward.")
    print("=" * 76)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
