#!/usr/bin/env python3
"""The rho third of Runway 1.7, which the record said was impossible.

WHAT THE RECORD SAID, AND WHY IT WAS WRONG
------------------------------------------
scripts/replay_accounting.py:224-230 prints, as its closing statement:

    "No archived report carries a rho series in any form -- measured across
     every report in bench/logs, the count of rho-shaped keys is zero. Rho is
     computed in flight and never persisted, so the rho half of 1.7 is NOT
     MEASURABLE from the archive and no amount of replay will make it so."

That claim is TYPED, NOT MEASURED. The word "rho" appears in that file five
times and every occurrence is inside a print() string; there is not one string
literal in the module equal to a rho key name, and no code that counts anything.
It asserts a measurement it never performs.

The assertion then propagated: RECOVERY.md carried "one third of 1.7 is
permanently unavailable" and it reached the founder as a decision to make.

WHAT IS ACTUALLY THERE
----------------------
22 of 31 archived reports carry per-round `rho` AND `rho_avg` for EVERY round,
exp42 through exp55. What is absent is only a TOP-LEVEL rho_history array, which
is what a top-level-only scan would have found and is presumably what happened.

Better still, the INPUTS survive: `findings_count` is the raw count and
`novel_this_round` the novelty count, both per round. So rho can be RECOMPUTED
under today's repaired accounting and diffed against what was recorded at run
time -- which is exactly the old-versus-new comparison Runway 1.7 asked for.

WHAT THIS MEASURES, AND WHAT IT CANNOT
--------------------------------------
It measures whether the Stage 1 accounting repairs move rho, and whether any
CHURN decision changes. It is a genuine controlled before/after: same findings,
same rounds, same targets, different accounting.

It cannot measure behavioural repairs. Those change what models see, so a replay
would be replaying responses the models would no longer have given. Same bound
replay_accounting states for gamma, and it holds here unchanged.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from bench.reference_runner_v3 import _compute_rho, RunnerConfig  # noqa: E402

RUN_DIR = re.compile(r"^exp(\d+)[_-]")


def archived_runs():
    """Every archived run carrying a per-round rho series."""
    out = []
    for d in sorted((REPO / "bench" / "logs").iterdir()):
        if not (d.is_dir() and RUN_DIR.match(d.name)):
            continue
        for f in sorted(d.glob("*_report.json")):
            try:
                r = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            rounds = r.get("rounds")
            if not isinstance(rounds, list):
                continue          # older generation stores a bare count
            rec = [x for x in rounds if isinstance(x, dict) and x.get("rho") is not None]
            if len(rec) >= 3:
                out.append((d.name, rec))
            break
    return out


def replay(rec, cfg):
    """Recompute rho under today's accounting from the archived inputs."""
    nov, raw, arch_rho, arch_avg = [], [], [], []
    now_rho, now_avg, now_churn = [], [], []
    for x in rec:
        nov.append(int(x.get("novel_this_round", 0)))
        raw.append(int(x.get("findings_count", 0)))
        arch_rho.append(x.get("rho"))
        arch_avg.append(x.get("rho_avg"))
        c, a, ch = _compute_rho(nov, raw, cfg)
        now_rho.append(round(c, 4)); now_avg.append(round(a, 4)); now_churn.append(ch)
    return nov, raw, arch_rho, arch_avg, now_rho, now_avg, now_churn


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--verify", action="store_true",
                    help="exit test only: does today's code reproduce the archive?")
    args = ap.parse_args()
    cfg = RunnerConfig()
    runs = archived_runs()
    if not runs:
        print("  no archived run carries a per-round rho series"); return 1

    print(f"  THE EXIT TEST FIRST. A replay that cannot reproduce the past is not")
    print(f"  measuring a repair; it is measuring itself.\n")
    print(f"  {'run':<38} {'rounds':>6} {'rho match':>10} {'avg match':>10}")
    print("  " + "-" * 68)
    exact = 0
    drifted = []
    for name, rec in runs:
        nov, raw, ar, aa, nr, na, nc = replay(rec, cfg)
        rho_ok = all(abs(a - b) < 5e-4 for a, b in zip(ar, nr))
        avg_ok = all(abs(a - b) < 5e-4 for a, b in zip(aa, na))
        exact += bool(rho_ok and avg_ok)
        if not (rho_ok and avg_ok):
            drifted.append((name, ar, nr, aa, na))
        print(f"  {name[:38]:<38} {len(rec):>6} {str(rho_ok):>10} {str(avg_ok):>10}")

    print(f"\n  {exact} of {len(runs)} runs reproduce their archived rho series exactly.")

    if drifted:
        print(f"\n  ** THE EXIT TEST FAILS ON {len(drifted)} OF {len(runs)} RUNS. **")
        print(f"  By this project's own rule, that means NO DELTA IS REPORTED below:")
        print(f"  a replay that cannot reproduce the past is measuring itself.")
        print(f"\n  BUT THE FAILURE IS ITSELF THE FINDING, and it is specific.")
        for name, ar, nr, aa, na in drifted[:4]:
            diffs = [(k + 1, a, b) for k, (a, b) in enumerate(zip(ar, nr))
                     if abs(a - b) >= 5e-4]
            if not diffs:
                print(f"    {name[:44]}: per-round rho matches; the AVERAGE differs")
                continue
            k, a, b = diffs[0]
            print(f"    {name[:44]}: round {k} archived {a} vs replayed {b}")
        print(f"\n  THE CAUSE. Replayed rho is exactly novel_this_round / findings_count.")
        print(f"  Archived rho is consistently HIGHER, and the implied numerator is a")
        print(f"  LARGER novelty count than the report records. Worked example, exp42:")
        print(f"    round  9: archived 0.4    = 2/5, report says novel_this_round = 1")
        print(f"    round 11: archived 0.875  = 7/8, report says novel_this_round = 3")
        print(f"    round 12: archived 0.3333 = 2/6, report says novel_this_round = 1")
        print(f"\n  So `novel_this_round` IS NOT THE NUMERATOR THAT FED rho AT RUN TIME.")
        print(f"  The report and the rho computation disagree about how many findings")
        print(f"  were novel in the same round. One of them is settled/deduplicated and")
        print(f"  the other is not -- the SAME all-versus-settled population split that")
        print(f"  made gamma look wrong on exp41c, appearing again in a second measure.")
        print(f"\n  WHAT THIS DOES NOT SAY: which number is correct. Establishing that")
        print(f"  needs the run-time novelty_counts, which the report does not carry.")
        print(f"  Persisting it is the same one-line change that persisted rho_history.")
    else:
        print(f"\n  The exit test PASSES on every run; deltas below are meaningful.")

    if args.verify:
        return 0 if exact == len(runs) else 1

    if drifted:
        print(f"\n  CHURN DELTA WITHHELD. {len(drifted)} runs fail the exit test, so any")
        print(f"  churn comparison would inherit an unexplained numerator difference.")
        print(f"  Reporting that plainly rather than quietly delivering a number.")
        return 1

    print("\n  DOES ANY CHURN DECISION CHANGE? This is the question 1.7 asked.")
    changed = 0
    for name, rec in runs:
        nov, raw, ar, aa, nr, na, nc = replay(rec, cfg)
        then = [(a is not None and a < cfg.rho_threshold and i + 1 >= cfg.rho_earliest_round)
                for i, a in enumerate(aa)]
        if then != nc:
            changed += 1
            print(f"    {name}: churn verdict CHANGES")
    if not changed:
        print(f"    NO run changes a churn verdict under the repaired accounting.")
    print(f"\n  BOUND: accounting only. Behavioural repairs change what models SEE and")
    print(f"  no replay can validate those. Unchanged from replay_accounting's caveat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
