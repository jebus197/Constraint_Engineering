#!/usr/bin/env python3
"""Would the two-sided gate fire on this registry? Replayed against the LIVE gate.

Answers one question: is a run's non-convergence a property of its FINDINGS, or
of WHEN the machinery looked at them? The residual-clearing sweep runs after the
verdict is written and cannot change it (verified: `converged` is assigned only
before the sweep, and the only post-sweep writes to the result dict come from
`stop_reason_fields`, which returns just `stop_reason` and
`stop_reason_recorded`). But the sweep DOES resolve findings. So if the gate
would fire on the POST-sweep registry while the run was recorded as
non-convergent, the blocker is ORDERING, not any threshold.

This calls the real `_check_gamma_alt_convergence` and the real registry
counters rather than reimplementing either -- a reimplementation would only
prove this script agrees with itself.
"""
import argparse, json, pathlib, sys
sys.path.insert(0, "bench")
import numpy as np
import reference_runner_v3 as R

ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
ap.add_argument("--state", default=None, help="a runner_state.json")
ap.add_argument("--rounds", type=int, default=8)
a = ap.parse_args()

if getattr(a, "state", None) is None:
    ap.error("--state is required")

p = pathlib.Path(a.state)
d = json.loads(p.read_text(errors="replace"))
entries = (d.get("registry") or {}).get("entries") or {}

reg = R.FindingRegistry()
reg.entries = entries

cfg = R.RunnerConfig()
final_round = a.rounds - 1

# THE SILENT `or` FALLBACK HERE MISLED A REPORT, 2026-10-03, and the fix is to
# make the substitution VISIBLE rather than to remove it.
#
# This read `d.get("gamma_critical_history") or d.get("gamma_history")` and then
# printed whatever came back under the label `gamma_critical`. Measured on
# study_run1b: `gamma_critical_history` is ABSENT from runner_state.json -- the
# only gamma key persisted is `gamma_history` -- so the ALL-SEVERITY curve, 0.4274,
# was reported to the founder as the gate's critical-only input, repeatedly, for
# hours. The run's real gamma_critical was 0.732; the console log carries it and
# the registry does not. The fable seat caught it in panel round 1.
#
# A fallback that substitutes a DIFFERENT SERIES under the same name is worse than
# an absent value, because an absent value is visible and a mislabelled one is not.
# The substitution is KEPT so this still runs on a registry lacking the series, and
# every print of the number now carries where it came from.
#
# THE REGISTRY DEFECT THIS EXPOSES IS THE LARGER ONE: the gate's deciding series is
# not persisted, so a convergence verdict cannot be audited from saved state. The
# founder's position is that the registry is the single source of truth for any
# experiment a researcher may run, and that cannot hold while the deciding input
# lives only in a log line.
gcrit_hist = d.get("gamma_critical_history")
novel_hist = d.get("novel_critical_history") or []
gamma_all = float((d.get("gamma_history") or [0.0])[-1])
if gcrit_hist:
    gamma_crit = float(gcrit_hist[-1])
    GAMMA_CRIT_SRC = "gamma_critical_history, the gate's own series"
else:
    gamma_crit = gamma_all
    GAMMA_CRIT_SRC = ("*** SUBSTITUTED, NOT THE GATE'S INPUT *** "
                      "gamma_critical_history is ABSENT from this registry; this "
                      "is gamma_history, the ALL-SEVERITY curve. Read the real "
                      "value from the run log's 'gamma_critical:' line.")

# the real counters
a4 = reg.unverified_critical_count()
contested = reg.contested_count(final_round)
irred = reg.irreducible_queue_count()
opench = reg.open_crit_high_count()

print(f"state: {p.parent.name}/{p.name}   entries: {len(entries)}")
print(f"final round_idx: {final_round}")
print()
print("GATE INPUTS (from the live registry counters):")
print(f"  gamma_critical                = {gamma_crit:.4f}   [{GAMMA_CRIT_SRC}]   "
      f"(threshold {cfg.gamma_alt_threshold})")
print(f"  gamma (all findings)          = {gamma_all:.4f}")
print(f"  novel_critical_history        = {novel_hist}")
print(f"  unverified_critical (A4)      = {a4}")
print(f"  contested                     = {contested}")
print(f"  irreducible_queue             = {irred}   "
      f"(bound {cfg.max_irreducible_queue})")
print(f"  open_crit_high                = {opench}")
print()

fired, reason = R._check_gamma_alt_convergence(
    round_idx=final_round,
    gamma=gamma_all,
    novel_critical_history=novel_hist,
    cfg=cfg,
    unresolved_critical=a4,
    contested=contested,
    rho_churn=False,
    irreducible_queue=irred,
    gamma_critical=gamma_crit,
    total_findings=len(entries),
)
print(f"LIVE GATE VERDICT: {'WOULD FIRE' if fired else 'WOULD NOT FIRE'}")
print(f"  reason: {reason}")
print()

# the streak side, shown explicitly
w = cfg.gamma_alt_consecutive_zero_crit
tail = novel_hist[-w:] if len(novel_hist) >= w else novel_hist
zeros = int(np.sum(np.array(tail) == 0)) if tail else 0
print(f"STREAK SIDE: window {w}, tail {tail}, zeros in tail {zeros}/{len(tail)}")
print(f"  streak satisfied: {len(tail) == w and zeros == w}")
print(f"GAMMA SIDE: {gamma_crit:.4f} >= {cfg.gamma_alt_threshold} -> "
      f"{gamma_crit >= cfg.gamma_alt_threshold}")
print()
print("BLOCKERS, in the gate's own order:")
if final_round < cfg.gamma_alt_earliest_round:
    print(f"  round {final_round} < earliest {cfg.gamma_alt_earliest_round}")
if a4 > 0:
    print(f"  A4: {a4} unverified critical(s)")
if contested > 0:
    print(f"  contested: {contested}")
if irred > cfg.max_irreducible_queue:
    print(f"  irreducible queue {irred} > bound {cfg.max_irreducible_queue}")
if gamma_crit < cfg.gamma_alt_threshold:
    print(f"  gamma_critical {gamma_crit:.4f} < {cfg.gamma_alt_threshold}")
if not (len(tail) == w and zeros == w):
    print(f"  streak not yet {w} consecutive zeros (tail {tail})")
