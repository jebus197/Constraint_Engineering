#!/usr/bin/env python3
"""Would a PER-ROUND predicate catch anything the watchdog's absence detectors miss?

HIS DEFINITION, 2026-11-02: *"'Scewy' simply means not functioning as expected."*
B20 names the monitoring judgement `cy` encodes as its highest-risk arm, because
nothing said what screwy meant. His definition supplies a comparison against a
stated expectation -- ★ AND A CLAIM OF CC1'S IS WITHDRAWN HERE, having been told to the founder
TWICE: that the watchdog's 13 event kinds are ALL absence detectors, firing only
when nothing is happening. THAT IS FALSE. `TROUBLE` is a CONTENT channel: its
pattern at `scripts/cy_watchdog_2026-10-02.py:61` is
`Traceback|Exception|FATAL|CRITICAL|Segmentation|MemoryError|Killed|OOM|
RecursionError|PermissionError|HALTED|ALARM|REFUSED|UNRECORDED_STOP`, and it
forwards any matching line out of the run's own output. `REFUSED` is precisely
what the convergence gate logs when it declines, so lines like
`γ-alt: hardened REFUSED at R3: 1 contested finding(s) still in dispute` are
ALREADY reported per round. `PROCESS GONE` is likewise not an alarm -- it reads
"the run has ended" and fires on every normal termination.

SO THE GAP IS NARROWER AND MORE PRECISE THAN CC1 STATED. The watchdog already
reports a divergence the runner logs with a word on that fixed keyword list. What
it cannot report is a divergence the runner logs NEUTRALLY -- gamma dipping with
no matching keyword on the line. That is the only thing a per-round predicate
would add.

CC1 PROPOSED A PER-ROUND PREDICATE AND THIS MEASURES IT BEFORE IT IS BUILT, which
is his composability standard applied: a composed mechanism may be recommended
only with evidence it beats either part alone on a named property.

HYPOTHESIS: a per-round predicate over round-keyed quantities would fire on runs
where no absence detector fired.

WHAT FALSIFIES IT: if every run carrying a round-level divergence ALSO carried an
absence-detector event, the predicate adds nothing the watchdog does not already
report, and the proposal should be dropped as the pre-registration one was.

★ THE 2 DIVERGENCE DEFINITIONS ARE DERIVED FROM THE PROJECT'S OWN SEMANTICS, NOT
INVENTED, because a proxy chosen without measuring its alternatives is this
project's most recorded error class:

  (1) GAMMA DECREASED between consecutive rounds. Gamma is the decay curve and
      the standing directive of 2026-06-10 states it is "an ACTIVE, central
      measure of convergence". A decay curve that steepens is the run getting
      WORSE at converging, which is "not functioning as expected" in his words.

  (2) THE GATE FLIPPED FROM PASS TO FAIL. `gate_history` is a per-round boolean
      and the gate requires CONSECUTIVE passes, so a flip discards accumulated
      progress -- the runner makes that explicit with `gate_history.clear()` at
      `reference_runner_v3.py:21148`. A run that passed and then stopped passing
      has diverged from its own trajectory.

★ AND THE HONEST LIMIT, STATED BEFORE THE RESULT. This compares at RUN
granularity, not round granularity, because the watchdog log carries wall-clock
times and the round series carry no timestamps, so the two cannot be aligned in
time from what is stored. A run-level comparison can show that a divergence
occurred where no detector spoke; it cannot show WHICH round. Saying otherwise
would be the stronger claim the data does not support.
"""
from __future__ import annotations
import json, math, pathlib, re, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: ★ `PROCESS GONE` WAS IN THIS SET AND HAD TO COME OUT, 2026-11-02. It reads
#: "pid N is no longer running; the run has ended" and fires on EVERY normal
#: termination, so including it made 8 of 8 runs "alarmed" -- a verdict that
#: never varies, which `feedback_a_signal_is_not_a_measurement_2026-10-30` names
#: as the cheapest available signal that a predicate is wrong. The filter was
#: written to prevent exactly that and still got it wrong on the first pass.
ALARM_KINDS = ("TROUBLE", "STALLED", "LOG TRUNCATED", "BACKLOG")
_EVENT = re.compile(r"^\[cy \d\d:\d\d:\d\d\]\s+([A-Z][A-Z ]*?):", re.M)


def wilson(k: int, n: int):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n; z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def gamma_dips(hist) -> list[int]:
    out = []
    vals = [v for v in (hist or []) if isinstance(v, (int, float))]
    for i in range(1, len(vals)):
        if vals[i] < vals[i - 1]:
            out.append(i)
    return out


def gate_flips(hist) -> list[int]:
    out = []
    h = [bool(v) for v in (hist or [])]
    for i in range(1, len(h)):
        if h[i - 1] and not h[i]:
            out.append(i)
    return out


def main() -> int:
    answer_help(__doc__, __file__)
    print("=" * 78)
    print("WOULD A PER-ROUND PREDICATE CATCH WHAT THE ABSENCE DETECTORS MISS?")
    print("=" * 78)
    rows = []
    for d in sorted(LOGS.glob("*")):
        if not d.is_dir():
            continue
        st, wd = d / "runner_state.json", d / "cy_watchdog.log"
        if not (st.is_file() and wd.is_file()):
            continue
        try:
            j = json.loads(st.read_text(errors="ignore"))
        except Exception:
            continue
        if not isinstance(j, dict):
            continue
        gh = j.get("gamma_history") or j.get("gamma_critical_history") or []
        gt = j.get("gate_history") or []
        kinds = [k.strip() for k in _EVENT.findall(wd.read_text(errors="replace"))]
        alarms = [k for k in kinds if k in ALARM_KINDS]
        rows.append({
            "run": d.name, "rounds": max(len(gh), len(gt)),
            "gamma_dips": gamma_dips(gh), "gate_flips": gate_flips(gt),
            "alarm_kinds": sorted(set(alarms)), "n_alarms": len(alarms),
            "all_kinds": sorted(set(kinds)),
        })

    print(f"\n  runs with BOTH round data and a watchdog log: {len(rows)}")
    if not rows:
        print("  NOT TESTABLE: no run carries both. That is a result, not a pass.")
        return 1

    print(f"\n  {'run':46s} {'rnds':>4s} {'dips':>5s} {'flips':>5s} {'alarms':>6s}  kinds")
    for r in rows:
        print(f"  {r['run'][:46]:46s} {r['rounds']:4d} "
              f"{len(r['gamma_dips']):5d} {len(r['gate_flips']):5d} "
              f"{r['n_alarms']:6d}  {','.join(r['alarm_kinds']) or '-'}")

    diverged = [r for r in rows if r["gamma_dips"] or r["gate_flips"]]
    silent = [r for r in diverged if r["n_alarms"] == 0]
    alarmed_no_div = [r for r in rows
                      if r["n_alarms"] and not (r["gamma_dips"] or r["gate_flips"])]

    print(f"\n  RUNS THAT DIVERGED (gamma dipped or the gate flipped): "
          f"{len(diverged)} of {len(rows)}")
    p, lo, hi = wilson(len(silent), len(diverged)) if diverged else (0, 0, 0)
    print(f"  OF THOSE, HOW MANY HAD **NO** ABSENCE ALARM: {len(silent)} of "
          f"{len(diverged)}" + (f" = {p:.6f}  Wilson 95% [{lo:.6f}, {hi:.6f}]"
                                if diverged else ""))
    for r in silent:
        print(f"     SILENT: {r['run'][:52]} -- {len(r['gamma_dips'])} gamma dip(s), "
              f"{len(r['gate_flips'])} gate flip(s), 0 alarms")
    print(f"  AND THE CONVERSE, an alarm with no divergence: {len(alarmed_no_div)}")

    print("\n" + "=" * 78)
    if not diverged:
        print("NOT TESTABLE. No run in the overlap carries a divergence, so nothing")
        print("can be said about whether a predicate would have caught one. A")
        print("proposal with no denominator is neither supported nor refuted, and")
        print("reporting it as supported would be the flattering reading.")
        return 1
    # ★ THE VERDICT WAS OVERSTATED AND IS CORRECTED, 2026-11-02. A first version
    # printed "HYPOTHESIS FALSIFIED" on finding 0 silent runs. That conclusion
    # does not follow from this comparison, and saying it did would be the
    # mirror of the flattering reading: the test is whether a TROUBLE line
    # exists ANYWHERE in the run, which cannot distinguish "the divergence was
    # reported" from "something unrelated was reported". A line reading
    # `corrected copy REFUSED C0007 from Fable-SIM` is not a report of gamma
    # dipping, and counting it as one credits the watchdog with a detection it
    # did not make. Round alignment would settle it and is impossible from
    # stored data: the watchdog log carries wall-clock times and the round
    # series carry none.
    print("NOT TESTABLE AT ROUND GRANULARITY, which is the only granularity that")
    print("answers the question. Measured facts, which stand:")
    print(f"  * {len(diverged)} of {len(rows)} runs diverged on a round-keyed quantity")
    print(f"  * {len(silent)} of {len(diverged)} diverging runs had NO alarm anywhere"
          + (f" ({p:.6f}, Wilson 95% [{lo:.6f}, {hi:.6f}])" if diverged else ""))
    print(f"  * {len(alarmed_no_div)} run(s) alarmed with no divergence at all")
    print("WHAT THIS CANNOT SHOW: whether the alarms that fired were ABOUT the")
    print("divergences. They are matched only by co-occurrence within one run, and")
    print("the TROUBLE lines actually present are mostly about refused corrected")
    print("copies, which have nothing to do with gamma. So the proposal is neither")
    print("supported nor refuted, and the honest next step is to make the runner")
    print("stamp its round series with a time, which costs almost nothing and")
    print("makes this exact comparison decidable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
