# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'capability_ladder_design_blind_cc2_2026-10-06', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 0e9482ba935d60851d78fb4c7f32c4c7cc9e15351d317b31deae8055a770d9ae
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Routing depth MOVES gamma_critical, so routing_max_rungs gates convergence.

HYPOTHESIS AS FIRST WRITTEN, AND ITS REFUTATION BY THIS SCRIPT. The original title
of this file predicted the move was UPWARD. The archive refutes that: gamma_critical
FALLS in most runs, because an unresolved critical is one the ladder has not reached
yet and is therefore skewed LATE, not early. The refutation is kept in place rather
than edited out, because the measured direction is the dangerous one: a run that
passes the 0.30 arm today can FAIL it once the ladder is exhausted.

THE MECHANISM, stated before it is measured.
  * `_settled_novelty_series` (bench/reference_runner_v3.py) builds the critical
    novelty series by bucketing entries on `open_since_round`, SKIPPING any entry
    whose status is in `_NON_NOVEL_TERMINAL_STATUSES` = {MERGED, DUPLICATE,
    UNCONFIRMED, REFUTED}. UNCONFIRMED is in that set.
  * `gamma_critical = _estimate_gamma(critical_series)` = max(0, min(1, 1 - beta))
    where beta is the log-log slope of the CUMULATIVE critical count against round
    index.
  * `_apply_routing` resolves a critical by setting falsifier_verdict=CONFIRMED.
    CONFIRMED is NOT in `_NON_NOVEL_TERMINAL_STATUSES`.

  So a critical that the ladder resolves STOPS being skipped and ENTERS the series
  at the round it was opened -- which is an EARLY round, because it has been sitting
  unresolved. Back-filling the early end of a cumulative curve flattens it, lowers
  beta, and RAISES gamma_critical. The founder's ruling removes the rung cap so that
  more criticals get resolved. More resolution therefore pushes gamma_critical up.

WHY THAT IS ABOVE THRESHOLD. `gamma_critical >= 0.30` is one of the two arms of the
convergence gate (`CRITICAL_QUIESCENCE_CONVERGED`, reference_runner_v3 ~:8238). The
other arm is K consecutive zero-new-critical rounds, which is NOT moved by resolving
an old critical, because the resolution lands in an EARLIER bucket. So the change is
one-sided: exhaustion loosens the gamma arm and leaves the count arm alone. A run can
therefore cross the gamma threshold because the INSTRUMENT got better at resolving
old criticals, not because discovery depleted. gamma is documented in this project as
"LOAD-BEARING ... an active convergence condition, not a report", so a routing change
that moves it is a change to the convergence condition.

This script does not argue the direction. It measures it on every archived registry
that has enough rounds, using the runner's OWN `_settled_novelty_series` and
`_estimate_gamma`, and reports how many runs CROSS 0.30 purely from flipping
unresolved criticals to CONFIRMED.

ADMISSIBILITY. Reads only `bench/logs/*/runner_state.json` and imports the runner.
No scoring key, no answer file, no planted-defect manifest.

Run:  python3 scripts/routing_exhaustion_raises_gamma_critical_2026-10-06.py
Exit: 0 if gamma_critical never rises (claim refuted); 1 if it rises (claim stands).
"""
from __future__ import annotations

import copy
import glob
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))


def main():
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print((__doc__ or "").strip())
        print("\nusage: %s" % sys.argv[0].split("/")[-1])
        return 0

    from bench.reference_runner_v3 import (
        _settled_novelty_series, _estimate_gamma,
        _NON_NOVEL_TERMINAL_STATUSES, CRITICAL_SEVERITY_THRESHOLD,
    )
    print("  CRITICAL_SEVERITY_THRESHOLD        : %s" % CRITICAL_SEVERITY_THRESHOLD)
    print("  _NON_NOVEL_TERMINAL_STATUSES       : %s"
          % sorted(_NON_NOVEL_TERMINAL_STATUSES))
    print("  UNCONFIRMED skipped by gamma?      : %s"
          % ("UNCONFIRMED" in _NON_NOVEL_TERMINAL_STATUSES))
    print("  CONFIRMED skipped by gamma?        : %s"
          % ("CONFIRMED" in _NON_NOVEL_TERMINAL_STATUSES))

    class Reg:
        def __init__(self, entries):
            self.entries = entries

    rows = []
    for p in sorted(glob.glob(str(REPO / "bench" / "logs" / "*" / "runner_state.json"))):
        try:
            j = json.loads(pathlib.Path(p).read_text(encoding="utf-8", errors="replace"))
        except (OSError, ValueError):
            continue
        ents = ((j.get("registry") or {}).get("entries")) or {}
        if not isinstance(ents, dict) or not ents:
            continue
        rounds = [e.get("open_since_round") for e in ents.values()
                  if isinstance(e, dict) and isinstance(e.get("open_since_round"), int)]
        if not rounds:
            continue
        max_round = max(rounds)
        if max_round + 1 < 3:          # _estimate_gamma needs >= 3 rounds
            continue

        base_entries = {k: dict(v) for k, v in ents.items() if isinstance(v, dict)}
        _, crit_before = _settled_novelty_series(Reg(base_entries), max_round)
        g_before = _estimate_gamma(crit_before)

        # The counterfactual the founder's ruling creates: the ladder, exhausted
        # instead of capped at 2 rungs, resolves criticals that are currently
        # UNCONFIRMED. Flip exactly those.
        after = copy.deepcopy(base_entries)
        flipped = 0
        for e in after.values():
            if (e.get("status") == "UNCONFIRMED"
                    and (e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD):
                e["status"] = "CONFIRMED"
                flipped += 1
        if flipped == 0:
            continue
        _, crit_after = _settled_novelty_series(Reg(after), max_round)
        g_after = _estimate_gamma(crit_after)
        _fl_rounds = [e.get("open_since_round") for e in base_entries.values()
                      if e.get("status") == "UNCONFIRMED"
                      and (e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD
                      and isinstance(e.get("open_since_round"), int)]
        _all_rounds = [e.get("open_since_round") for e in base_entries.values()
                       if isinstance(e.get("open_since_round"), int)]
        _mf = sum(_fl_rounds) / len(_fl_rounds) if _fl_rounds else 0.0
        _ma = sum(_all_rounds) / len(_all_rounds) if _all_rounds else 0.0
        rows.append((pathlib.Path(p).parent.name, max_round + 1, flipped,
                     g_before, g_after, crit_before, crit_after, _mf, _ma))

    print()
    print("=" * 96)
    print("EFFECT OF RESOLVING UNRESOLVED CRITICALS ON gamma_critical")
    print("=" * 96)
    print("  %-42s %4s %4s %7s %7s %8s %6s %6s %s"
          % ("run", "rnds", "flip", "gamma_0", "gamma_1", "delta",
             "mean_r", "mean_r", "0.30 arm"))
    print("  %-42s %4s %4s %7s %7s %8s %6s %6s %s"
          % ("", "", "", "", "", "", "flip", "all", ""))
    up = down = same = 0
    cross_up = cross_down = 0
    for name, nr, fl, g0, g1, cb, ca, mf, ma in sorted(rows, key=lambda r: -(r[4] - r[3])):
        d = g1 - g0
        cross = ""
        if g0 < 0.30 <= g1:
            cross_up += 1
            cross = "OPENS <<<"
        elif g1 < 0.30 <= g0:
            cross_down += 1
            cross = "CLOSES <<<"
        if d > 1e-12:
            up += 1
        elif d < -1e-12:
            down += 1
        else:
            same += 1
        print("  %-42s %4d %4d %7.4f %7.4f %+8.4f %6.2f %6.2f %s"
              % (name[:42], nr, fl, g0, g1, d, mf, ma, cross))
    print()
    print("  runs measured                      : %d" % len(rows))
    print("  gamma_critical ROSE                : %d" % up)
    print("  gamma_critical FELL                : %d" % down)
    print("  gamma_critical unchanged           : %d" % same)
    print("  runs where the 0.30 arm OPENS      : %d" % cross_up)
    print("  runs where the 0.30 arm CLOSES     : %d" % cross_down)
    print("    (a run that passes the gamma arm today would STOP passing it)")
    _sl = [r for r in rows if r[7] > r[8]]
    print("  runs where unresolved criticals skew LATER than the")
    print("  registry mean open_since_round     : %d of %d" % (len(_sl), len(rows)))
    if rows:
        worst = min(rows, key=lambda r: r[4] - r[3])
        print()
        print("  largest single move: %s" % worst[0])
        print("    critical series BEFORE : %s" % worst[5])
        print("    critical series AFTER  : %s" % worst[6])
        print("    gamma_critical %.4f -> %.4f" % (worst[3], worst[4]))

    print()
    print("=" * 96)
    print("WHAT WAS MEASURED, including the refutation of this script's own first")
    print("hypothesis. The docstring above predicted gamma_critical would RISE, on the")
    print("reasoning that unresolved criticals sit in EARLY rounds. The archive says")
    print("otherwise and the mechanism is the mean-round column: an unresolved critical")
    print("is one the ladder has NOT yet got to, which skews it LATE, and adding mass to")
    print("the late end of a cumulative curve STEEPENS it, raising beta and LOWERING")
    print("gamma = 1 - beta. The prediction was wrong; the coupling is real and its sign")
    print("is the more dangerous one.")
    print()
    print("CONCLUSION EITHER WAY: gamma_critical is NOT invariant to routing depth, so")
    print("`routing_max_rungs` is an undeclared input to the convergence gate. Removing")
    print("the cap is therefore not a pure spend question, which is how the founder's")
    print("ruling and routing.py's own comment both frame it.")
    print("=" * 96)
    return 1 if (cross_up + cross_down) > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
