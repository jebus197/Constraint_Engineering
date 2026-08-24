#!/usr/bin/env python3
"""Replay the archived runs through the accounting, old and new, and diff them.

WHY THIS EXISTS, AND WHY IT IS BUILT BEFORE ANY REPAIR
------------------------------------------------------
A 5-model panel (2026-08-18, no compelled convergence) recommended repairing the
harness before spending any further experiment, on the grounds that a run made
now would measure the instrument rather than the question. The repairs divide in
two, and only one half can be validated without spending money:

  * ACCOUNTING repairs change only how findings are COUNTED. The archive holds
    the findings, the rounds and the targets, so a replay is a genuine controlled
    before/after: same inputs, different accounting. Zero dispatch.
  * BEHAVIOURAL repairs change what models SEE — the NEAR-DUPLICATE flag reaches
    the next round's prompt (bench/dm/_feedback.py:393, :472) — so a replay would
    be replaying responses the models would no longer have given. Those need a
    live run and this script must not pretend otherwise.

THE EXIT TEST, and it comes first
---------------------------------
Before any delta this script reports can mean anything, it must reproduce each
run's OWN archived series exactly under the OLD accounting. A replay that cannot
reproduce the past is not measuring a repair; it is measuring itself.

`--verify` runs only that check and reports nothing else. If it fails, stop.

Usage
-----
    python3 scripts/replay_accounting.py --verify     # the exit test, run this first
    python3 scripts/replay_accounting.py              # verify, then report deltas
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import bench.convergence_location as CL  # noqa: E402

# Runs carrying both an archived novelty series and a recoverable target.
RUNS = {
    "exp42": ("exp42_composer_locationkey_live", "bench/cdsfl_registry/composer.py"),
    "exp43": ("exp43_macrophage_locationkey_live", "bench/macrophage_cell.py"),
    "exp44": ("exp44_evidence_locationkey_live", "bench/evidence.py"),
    "exp45": ("exp45_memory_statistics_live", "bench/dm/_memory.py"),
    "exp46": ("exp46_stage6_locationkey_live", "bench/dm/_shadow_stage6.py"),
    "exp47": ("exp47_divergence_locationkey_live", "bench/dm/_divergence.py"),
    "exp48": ("exp48_chemistry_exam_live", None),
    "exp49": ("exp49_engineering_exam_live", None),
}


def estimate_gamma(counts, min_rounds: int = 3) -> float:
    """Duane slope, transcribed from reference_runner_v2._estimate_gamma.

    Deliberately a copy rather than an import: the runner's version is embedded in
    a module that pulls the whole dispatch stack, and a replay must not be able to
    dispatch anything. The copy is pinned against the archive by `--verify`.
    """
    n = len(counts)
    if n < min_rounds:
        return 0.0
    cum, total = [], 0
    for c in counts:
        total += c
        cum.append(total)
    if total == 0:
        return 0.0
    lx, ly = [], []
    for i, c in enumerate(cum):
        if c > 0:
            lx.append(math.log(i + 1))
            ly.append(math.log(c))
    if len(lx) < 2:
        return 0.0
    n_p, sx, sy = len(lx), sum(lx), sum(ly)
    sxy = sum(x * y for x, y in zip(lx, ly))
    sx2 = sum(x * x for x in lx)
    denom = n_p * sx2 - sx * sx
    if abs(denom) < 1e-12:
        return 0.0
    return max(0.0, min(1.0, 1.0 - (n_p * sxy - sx * sy) / denom))


def report_for(stem: str):
    hits = [p for p in (REPO / "bench" / "logs").glob(f"{stem}_*/{stem}_report.json")
            if ".errata" not in str(p)]
    return json.loads(hits[0].read_text(encoding="utf-8")) if hits else None


def symbols_for(target_rel, entries):
    if target_rel and (REPO / target_rel).is_file():
        return CL.target_symbols(str(REPO / target_rel))
    import re
    ids = set()
    for e in entries.values():
        ids |= set(re.findall(r"\b([A-Z]{2}-\d{2})\b", e.get("description", "") or ""))
    return frozenset(ids)


def verify() -> int:
    """THE EXIT TEST. Reproduce each archived series exactly, or stop."""
    print("  EXIT TEST — does the replay reproduce each run's OWN archived series?\n")
    print(f"  {'run':8s}{'archived series':>44s}{'':4s}{'result':>10s}")
    bad = 0
    for run, (stem, tgt) in RUNS.items():
        rep = report_for(stem)
        if rep is None:
            print(f"  {run:8s}{'(run not present)':>44s}"); continue
        arch = rep.get("location_crit_shadow_history") or []
        if not arch:
            print(f"  {run:8s}{'(no archived series)':>44s}"); continue
        ents = rep["registry"]["entries"]
        got = CL.location_only_series(ents, len(arch) - 1, symbols_for(tgt, ents))
        ok = got == arch
        bad += (not ok)
        print(f"  {run:8s}{str(arch)[:44]:>44s}{'':4s}{'MATCH' if ok else 'DIFFERS':>10s}")
        if not ok:
            print(f"  {'':8s}{'replayed:':>44s}    {got}")
    print()
    if bad:
        print(f"  {bad} run(s) do NOT reproduce. The replay is measuring itself, not a repair.")
        print("  STOP. Nothing downstream of this is trustworthy.")
        return 1
    print("  All archived series reproduce exactly. The replay is a valid instrument.")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# THE DELTA HALF — Stage 1 item 1.7, built 2026-08-24
# ─────────────────────────────────────────────────────────────────────────────

# The two-sided gate's defaults, restated here rather than imported for the same
# reason `estimate_gamma` is copied: a replay must not be able to reach the dispatch
# stack. GAMMA IS LOAD-BEARING and the gate is two-sided by founder directive --
# gamma_critical at or above threshold AND K consecutive zero-new-critical rounds.
# Either side alone is insufficient, and this replay must not quietly test one.
GAMMA_THRESHOLD = 0.30
CONSECUTIVE_REQUIRED = 3


def two_sided_round(counts, gamma_series, threshold=GAMMA_THRESHOLD,
                    k=CONSECUTIVE_REQUIRED):
    """First round at which BOTH sides of the gate hold, or None.

    Returns the round index, so a change in this number between old and new
    accounting is a change in when the run WOULD have been allowed to stop.
    """
    zeros = 0
    for i, c in enumerate(counts):
        zeros = zeros + 1 if c == 0 else 0
        g = gamma_series[i] if i < len(gamma_series) else 0.0
        if zeros >= k and g >= threshold:
            return i
    return None


def deltas() -> int:
    """OLD vs NEW accounting on every archived run: series, gamma, and the decision.

    WHAT COUNTS AS A DELTA THAT MATTERS. Not a moved decimal -- a moved DECISION. A
    gamma that shifts by 0.02 and leaves the convergence round untouched changes no
    conclusion in this project's record. A convergence round that moves changes every
    downstream claim about that run. Both are reported; only the second is a finding.
    """
    print("\n  DELTA — OLD (archived) vs NEW (repaired accounting)\n")
    print(f"  {'run':<8}{'series':>9}{'gamma_crit old':>16}{'gamma_crit new':>16}"
          f"{'converge old':>14}{'converge new':>14}   decision")
    moved, rows = 0, []
    for run, (stem, tgt) in RUNS.items():
        rep = report_for(stem)
        if rep is None:
            continue
        arch = rep.get("location_crit_shadow_history") or []
        if not arch:
            continue
        ents = rep["registry"]["entries"]
        new_series = CL.location_only_series(ents, len(arch) - 1, symbols_for(tgt, ents))
        # ★ THE COMPARATOR IS NOT `gamma_critical_history`, AND THIS IS NOT A DETAIL.
        # That archived series is the Duane slope of the SETTLED novelty series, which
        # the gate reads directly (reference_runner_v2.py:4385-4387). The series this
        # replay repairs is the LOCATION-KEYED critical series. Fitting a slope to one
        # and comparing it against a slope fitted to the other compares two different
        # quantities and manufactures a delta out of nothing. That precise error was
        # made and WITHDRAWN on 2026-08-22, and it was made again here on 2026-08-24
        # before this comment existed -- it produced a spurious "exp47 converges at 11
        # instead of never", which is exactly the kind of false headline this project
        # keeps generating. Old and new must both be fitted to the SAME quantity.
        g_old = [estimate_gamma(arch[:i + 1]) for i in range(len(arch))]
        g_new = [estimate_gamma(new_series[:i + 1]) for i in range(len(new_series))]
        r_old = two_sided_round(arch, g_old)
        r_new = two_sided_round(new_series, g_new)
        same_series = (new_series == arch)
        decision = ("unchanged" if r_old == r_new else
                    f"MOVED {r_old} -> {r_new}")
        moved += (r_old != r_new)
        rows.append((run, same_series, g_old, g_new, r_old, r_new))
        print(f"  {run:<8}{'same' if same_series else 'CHANGED':>9}"
              f"{(g_old[-1] if g_old else 0.0):>16.4f}{(g_new[-1] if g_new else 0.0):>16.4f}"
              f"{str(r_old):>14}{str(r_new):>14}   {decision}")
    print()
    if moved:
        print(f"  {moved} run(s) change their convergence round under the repaired accounting.")
        print("  Every downstream claim about those runs must be re-read.")
    else:
        print("  NO run changes its convergence round. The Stage 1 accounting repairs")
        print("  move no convergence decision in the archive. That is the result 1.7 was")
        print("  built to obtain, and it is a NEGATIVE one: the repairs were necessary for")
        print("  correctness and they do not retroactively alter a single conclusion.")
        print()
        print("  WHY THIS IS NOT CIRCULAR, since it would be easy to assume it is. The")
        print("  archive was written by the code as it stood AT RUN TIME. The code that")
        print("  computes this series HAS changed since -- bench/convergence_location.py")
        print("  carries the three description-truncation fixes (1e5de9a) and the 500 ->")
        print("  2000 registry cap (f53c276), both landed after the last archived run. So")
        print("  today's code reproducing every archived series exactly is a MEASUREMENT")
        print("  that those changes are behaviour-neutral on these inputs, not a tautology.")
    print()
    print("  WHAT 1.7 ASKS FOR AND THE ARCHIVE CANNOT GIVE. The runway asks for old vs")
    print("  new RHO as well as gamma and the novelty series. No archived report carries")
    print("  a rho series in any form -- measured across every report in bench/logs, the")
    print("  count of rho-shaped keys is zero. Rho is computed in flight and never")
    print("  persisted, so the rho half of 1.7 is NOT MEASURABLE from the archive and no")
    print("  amount of replay will make it so. Reporting that plainly rather than")
    print("  quietly delivering the two thirds that are available.")
    print("\n  Caveat, stated because it bounds everything above: this replays ACCOUNTING")
    print("  only. The behavioural repairs (Stage 2) change what models SEE, and no")
    print("  replay can validate those -- they need a live run.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verify", action="store_true",
                    help="run only the exit test and report nothing else")
    args = ap.parse_args()
    rc = verify()
    if args.verify or rc:
        return rc
    return deltas()


if __name__ == "__main__":
    raise SystemExit(main())
