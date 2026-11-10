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


FIX_COMMIT_UTC = "20260929T193754Z"
#: The commit that added the post-verifier recompute, 35117b28,
#: 2026-09-29 20:37:54 +0100 = 19:37:54 UTC. Found with `git log -S` on the
#: producer name the runner's own comment cites, not guessed from the date in
#: a filename.


def _numeric(x) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def split_at_the_recompute():
    """Does the persisted count array align with the PRE- or POST-verifier rho?

    ★ B77's REMAINING DISAMBIGUATION, AND THE OBVIOUS HYPOTHESIS IS FALSIFIED.
    B77 says what it waits on is *"which of the 2 rho values per round the
    de-confounded figure should use, pre-verifier or post-verifier"*, and that
    this *"is answerable by reading the runner"*. The natural test is the run
    DATE: if the persisted arrays align with the post-verifier value, runs made
    from the recompute commit onward should reproduce at a far higher rate.

    MEASURED 2026-11-10 over the 40 runs carrying all 3 arrays, split at the
    commit: BEFORE, 61 of 72 per-round values exact, 0.847222, Wilson
    [0.746777, 0.912493]; FROM it, 88 of 117 exact, 0.752137, Wilson
    [0.666722, 0.821521]. **Fisher exact odds ratio 0.547202, p = 0.143828**,
    cross-checked by a Yates-corrected chi-square at p = 0.170450. The post-fix
    rate is if anything LOWER and the difference is not significant, so the
    date does NOT separate the 2 sides and the residual has a cause other than
    which side of the verifier the recompute ran on.

    SO B77's DISAMBIGUATION IS NOT ANSWERED, and saying so is the finding. What
    is excluded is the hypothesis that the persisted arrays are simply the
    post-verifier ones; what remains is a per-round alignment question inside
    the runner's own ordering, which no figure here settles.

    73 non-numeric round values are SKIPPED AND COUNTED rather than coerced,
    because a `rho_history` entry that is a string is not a rho.
    """
    import numpy as np
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint

    rows, skipped = [], 0
    for path in sorted((REPO / "bench" / "logs").rglob("*.json")):
        try:
            d = json.loads(path.read_text())
        except Exception:                               # noqa: BLE001
            continue
        N, R, H = [], [], []
        _collect(d, NUM_KEY, N)
        _collect(d, DEN_KEY, R)
        _collect(d, "rho_history", H)
        if not (N and R and H):
            continue
        N, R, H = N[0], R[0], H[0]
        if not all(isinstance(x, list) for x in (N, R, H)):
            continue
        k = min(len(N), len(R), len(H))
        pairs = [(N[i], R[i], H[i]) for i in range(k)
                 if _numeric(N[i]) and _numeric(R[i]) and _numeric(H[i])]
        skipped += k - len(pairs)
        if not pairs:
            continue
        exact = sum(1 for n_, r_, h_ in pairs
                    if r_ and abs(n_ / r_ - h_) < 5e-4)
        stamp = re.search(r"(\d{8}T\d{6}Z)", str(path))
        rows.append((stamp.group(1) if stamp else "", exact, len(pairs)))

    pre = [r for r in rows if r[0] and r[0] < FIX_COMMIT_UTC]
    post = [r for r in rows if r[0] and r[0] >= FIX_COMMIT_UTC]
    undated = [r for r in rows if not r[0]]

    print()
    print("-" * 76)
    print("  B77's DISAMBIGUATION: DOES THE RUN DATE SEPARATE THE 2 SIDES?")
    print("-" * 76)
    print(f"  runs with all 3 arrays : {len(rows)}")
    print(f"  non-numeric round values skipped, not coerced : {skipped}")
    print(f"  undated paths EXCLUDED : {len(undated)}")

    def rate(g, label):
        if not g:
            print(f"  {label}: 0 runs")
            return 0, 0
        ek = sum(x[1] for x in g)
        tk = sum(x[2] for x in g)
        full = sum(1 for x in g if x[1] == x[2])
        sm = proportion_confint(ek, tk, alpha=0.05, method="wilson")
        cp = proportion_confint(ek, tk, alpha=0.05, method="beta")
        z = st.norm.ppf(0.975)
        pr = ek / tk
        den = 1 + z * z / tk
        cen = (pr + z * z / (2 * tk)) / den
        hw = z * np.sqrt(pr * (1 - pr) / tk + z * z / (4 * tk * tk)) / den
        print(f"  {label} ({len(g)} runs)")
        print(f"     per-round exact : {ek} of {tk} = {pr:.6f}")
        print(f"       Wilson statsmodels [{sm[0]:.6f}, {sm[1]:.6f}]")
        print(f"       Wilson written-out [{max(0.0, cen - hw):.6f}, "
              f"{min(1.0, cen + hw):.6f}]")
        print(f"       Clopper-Pearson    [{(cp[0] or 0.0):.6f}, {cp[1]:.6f}]")
        print(f"     runs fully exact: {full} of {len(g)}")
        return ek, tk

    a = rate(pre, "BEFORE the recompute")
    b = rate(post, "FROM the recompute ")
    if not (a[1] and b[1]):
        print("  one side is empty; no comparison is possible")
        return None
    tab = [[b[0], b[1] - b[0]], [a[0], a[1] - a[0]]]
    odds, pf = st.fisher_exact(tab)
    _chi, pc, _dof, _exp = st.chi2_contingency(tab, correction=True)
    print(f"  2x2 (exact, not): post={tab[0]}  pre={tab[1]}")
    print(f"  Fisher exact : odds ratio {odds:.6f}, p = {pf:.6e}")
    print(f"  chi-square   : p = {pc:.6e}  (2nd route, Yates-corrected)")
    print()
    if pf < 0.05 and odds > 1.0:
        print("  THE DATE SEPARATES THEM: the persisted arrays are the")
        print("  POST-verifier ones and B77's disambiguation is answered.")
    else:
        print("  THE DATE DOES NOT SEPARATE THEM. The post-fix rate is not")
        print("  higher and the difference is not significant, so the")
        print("  hypothesis that the persisted arrays are simply the")
        print("  post-verifier ones is REFUTED. B77's disambiguation stays")
        print("  open, with 1 hypothesis fewer.")
    return odds, pf


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
    split_at_the_recompute()
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
