#!/usr/bin/env python3
"""What commissioning arm 1 actually did, measured from its own record.

THE RUN. 5 simulated seats (`CC2-SIM`, `Codex-SIM`, `Gemini-SIM`, `DeepSeek-SIM`,
`ChatGPT-SIM`) against `bench/cdsfl_registry/engine.py`, launched 2026-09-21
22:54:07 BST through `run_simulated_experiment_sandboxed.sh`, finished
2026-09-22 02:59 with exit code 0. 8 rounds, 245.5 minutes, 69 findings,
`converged_at: None` -- it exhausted the round cap rather than converging, which
is 1 of the project's 2 legitimate stopping conditions.

FIVE THINGS IT ESTABLISHED, each measured here rather than asserted.

1. THE SANDBOX HELD AND THE PANEL CONFINEMENT DID NOT. The report records a
   TARGET INTEGRITY EVENT at round 4: the target's hash moved and its size went
   from 21,265 to 22,069 bytes. A seat rewrote the file mid-run. The live
   repository was untouched -- verified independently, byte-identical and a
   clean tree -- so the disposable copy did its job. But the panel confinement
   did not stop the write, which is exactly what the runner's own comment
   predicted: "A cwd confines RELATIVE paths. Seats are handed the ABSOLUTE repo
   path ... Bash is a superset of write, so an absolute path defeats any cwd."
   The run also narrows the culprit: 4 of the 5 seats have a dispatch window
   containing the file's mtime. This is a KNOWN, DOCUMENTED, UNFIXED gap, now
   reproduced under controlled conditions with attribution data.

2. THE SEVERITY SWEEP RAN AND ITS DEMOTION HALF NEVER FIRED, AS PREDICTED.
   10 findings were latent-tagged across rounds 3 to 7; 0 were demoted. The
   prediction is in `run_simulated_experiment.py`, written 2026-09-07: "the
   rehearsal exercises the tagger and the sweep, not the demotion", because
   demotion needs BOTH `latent` and `severity_is_proven`. The tagger is
   therefore commissioned as working, and the demotion path is confirmed
   unreachable on this target. THE REPORT DOES NOT RECORD WHY each demotion was
   skipped, so attributing it to the proof interlock specifically is consistent
   with finding 3 but is NOT established by this run.

3. THE FALSIFIER GATE NEVER REFUTED ANYTHING. Across 8 gates and 45 decisions:
   30 CONFIRMED, 15 to HIL, 0 REFUTED. That is 0.0000%, Wilson
   [0.0000%, 7.8652%], Clopper-Pearson [0.0000%, 7.8705%] -- so the true rate
   could be as high as about 8% and 0 of 45 is not proof of impossibility. It is
   NOT the first time: the instrument audit of 2026-08-05 recorded "71 findings,
   60 confirmed, 0 refuted". Two separate exercises, no refutations in either.

4. SEATS UNDERSTATE THEIR OWN R_k. See
   `scripts/rk_self_report_bias_2026-09-21.py`, which measures direction and
   magnitude over the same log.

5. THE OLD 900s SEAT CAP WAS MARGINAL. Dispatch wall-clock is computed below.
   Nothing died at the current 3600s cap.

Every proportion carries an interval from 2 independent routes.

Run:  python3 scripts/commissioning_arm1_results_2026-09-22.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOG = REPO / "bench" / "logs" / "commissioning_2026-09-21_arm1.log"
RUN = REPO / "bench" / "logs" / "commissioning_arm1_panel_20260921T215405Z"
REPORT = RUN / "commissioning_arm1_panel_report.json"

GATE = re.compile(
    r"falsifier gate \(tools decide\): (\d+) CONFIRMED, (\d+) REFUTED, (\d+) -> HIL")
DISPATCH = re.compile(r"\[([A-Za-z0-9-]+-SIM)\] (\d+) chars, (\d+)s")


def interval(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    w = proportion_confint(k, n, alpha=0.05, method="wilson")
    cp = proportion_confint(k, n, alpha=0.05, method="beta")
    return w, cp


def main() -> int:
    if not LOG.is_file():
        print(f"no arm 1 log at {LOG}", file=sys.stderr)
        return 2
    text = LOG.read_text(errors="replace")

    print("COMMISSIONING ARM 1 — what the run established")
    print()

    # --- the run's own summary -------------------------------------------
    if REPORT.is_file():
        d = json.loads(REPORT.read_text())
        print(f"  rounds recorded : {len(d.get('rounds', []))}")
        print(f"  findings        : {d.get('total_findings')}")
        ev = d.get("target_integrity_events") or []
        print(f"  target integrity events : {len(ev)}")
        for e in ev:
            att = e.get("attribution", {})
            f = att.get("file", {})
            print(f"      round {e['round']}: size now {f.get('size')} bytes, "
                  f"mtime {f.get('mtime')}")
            names = att.get("seats_whose_window_contains_mtime", [])
            print(f"      seats whose dispatch window contains that mtime: "
                  f"{len(names)} of 5 -- {', '.join(names)}")
        sc = d.get("severity_calibration_series") or []
        tagged = sum(r["latent_tagged"] for r in sc)
        demoted = sum(r["demoted"] for r in sc)
        print(f"  severity sweep  : {tagged} latent-tagged, {demoted} demoted "
              f"over {len(sc)} rounds")
        if tagged and not demoted:
            print("      -> the tagger fires; the demotion half does not. This is the")
            print("         2026-09-07 prediction confirmed, not a new defect.")
    else:
        print(f"  (no report at {REPORT})")

    # --- the falsifier gate ----------------------------------------------
    rows = [tuple(map(int, m)) for m in GATE.findall(text)]
    if rows:
        c = sum(r[0] for r in rows)
        rf = sum(r[1] for r in rows)
        h = sum(r[2] for r in rows)
        n = c + rf + h
        (wlo, whi), (clo, chi) = interval(rf, n)
        print()
        print(f"  falsifier gate  : {len(rows)} gates, {n} decisions")
        print(f"      CONFIRMED {c}   REFUTED {rf}   HIL {h}")
        print(f"      REFUTED rate {rf}/{n} = {100*rf/n:.4f}%")
        print(f"        Wilson 95%          [{100*wlo:.4f}%, {100*whi:.4f}%]")
        print(f"        Clopper-Pearson 95% [{100*clo:.4f}%, {100*chi:.4f}%]")
        if rf == 0:
            print("      -> 0 of {} is NOT proof the outcome cannot fire; the upper".format(n))
            print("         bound is about 8%. The 2026-08-05 audit saw the same shape:")
            print("         71 findings, 60 confirmed, 0 refuted.")

    # --- dispatch wall clock ----------------------------------------------
    secs = [int(s) for _, _, s in DISPATCH.findall(text)]
    if secs:
        import numpy as np
        a = np.array(secs)
        over_old = int((a > 900).sum())
        print()
        print(f"  dispatches      : {len(a)}")
        print(f"      median {np.median(a):.0f}s  mean {a.mean():.0f}s  max {a.max()}s")
        print(f"      exceeding the OLD 900s cap : {over_old}")
        print(f"      slowest as a fraction of the CURRENT 3600s cap: {a.max()/3600:.3f}")
        print(f"      slowest as a fraction of the OLD 900s cap     : {a.max()/900:.3f}")

    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
