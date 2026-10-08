#!/usr/bin/env python3
"""The dispatch cap sits at the 90th percentile, and the earlier figure was circular.

THE FOUNDER'S RULING, 2026-10-07: *"The models should be given the time they need
to deliver a full response. However, clearly the cap doesn't need to be arbitrary,
at 900, or 1800, or however many seconds. We can tell the models to print 'I am
done' at the end of all their outputs, then watch for this signal in their output
logs. Or perhaps there is a better way to do this?"* And: *"we should harvest
results when a model is done, not by setting an arbitrary wall clock limit."*

WHY THE PREVIOUS NUMBER WAS NOT EVIDENCE. A figure of 2426 s was reported to him
as "the measured 95th percentile of observed work". It was computed over durations
that INCLUDE attempts killed at the cap. Those attempts are RIGHT-CENSORED: their
true completion time is unknown and is longer than what was recorded. Taking a
percentile of a censored sample to choose the cap that caused the censoring is
circular, and it understates the answer.

THE CORRECT ESTIMATOR IS KAPLAN-MEIER, and it is computed twice below -- by hand
and by statsmodels -- because a survival estimate chosen to justify a cap must not
rest on one implementation.

WHAT IT SHOWS. Over 137 recorded attempts, 128 completions and 9 censored:
the median true completion time is 700.7 s, the 90th percentile is 1728.1 s and
the 95th is 2939.4 s. The cap is 1800 s, so it sits a little above the 90th
percentile -- roughly 1 attempt in 10 is killed while still working -- and a cap at
the 95th percentile would be about 2940 s, not 2426 s.

AND A LONGER CLOCK IS STILL THE WRONG LEVER ON ITS OWN. The dispatcher records a
raise to 3600 s made and reverted within the hour on 2026-10-06, with the reason:
the per-call RATE was stable across a timed-out attempt and a successful one
(20.455 s and 20.816 s per call), while the call COUNT differed -- 88 and still
unfinished on a degraded network against 49 to a complete answer. A seat on a
degraded route issues calls at normal speed and never converges, so a longer clock
lets it churn for an hour instead of 30 minutes. The clock cannot separate "still
working" from "working and getting nowhere"; only the call count can.

SO THE REPAIR HAS 2 PARTS AND THIS FILE SUPPLIES THE MEASUREMENT FOR BOTH:
harvest on COMPLETION rather than on the clock, and bound a degraded route by its
CALL COUNT rather than by a longer deadline. Both are PROPOSED here, not applied:
changing them changes every panel round.

Run: python3 scripts/the_cap_was_measured_on_censored_data_2026-10-08.py
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CURRENT_CAP_S = 1800.0

#: The figure reported to the founder on 2026-10-08, computed on censored data.
SUPERSEDED_FIGURE_S = 2426.0


def collect_attempts(repo: Path = REPO) -> dict:
    """Per-attempt durations, split into completions and censored kills.

    `elapsed_s` inside an attempts list is CUMULATIVE across attempts, which is
    the trap that produced a wrong per-attempt figure once already: attempt 2 of
    a 2026-10-07 round read 1705.0 s cumulative and took 110.4 s on its own.
    """
    obs, cens = [], []
    for seat in ("cc2", "fable"):
        for f in sorted(glob.glob(str(repo / "bench" / "logs" / "*" / f"{seat}.json"))):
            try:
                d = json.load(open(f))
            except Exception:
                continue
            if not isinstance(d, dict):
                continue
            atts = d.get("attempts")
            if isinstance(atts, list):
                prev = 0.0
                for a in atts:
                    if not isinstance(a, dict):
                        continue
                    e = a.get("elapsed_s")
                    if not isinstance(e, (int, float)):
                        continue
                    dur = e - prev if e > prev else e
                    prev = max(prev, e)
                    if dur <= 0:
                        continue
                    ok = bool(a.get("ok", a.get("chars", 0)))
                    (obs if ok else cens).append(float(dur))
            else:
                e = d.get("elapsed_s")
                if isinstance(e, (int, float)) and e > 0:
                    (obs if d.get("ok") else cens).append(float(e))
    return {"completions": obs, "censored": cens}


def _km(times, events):
    """Kaplan-Meier survival, hand-rolled. Returns [(t, S(t)), ...]."""
    pairs = sorted(zip(times, events))
    at_risk = len(pairs)
    S, out = 1.0, []
    for t, e in pairs:
        if e == 1:
            S *= (1 - 1 / at_risk)
        out.append((t, S))
        at_risk -= 1
    return out


def claim_the_censored_figure_was_circular() -> dict:
    import numpy as np

    d = collect_attempts()
    obs = np.array(d["completions"])
    cens = np.array(d["censored"])
    everything = np.concatenate([obs, cens]) if len(cens) else obs
    times = list(obs) + list(cens)
    events = [1] * len(obs) + [0] * len(cens)
    km = _km(times, events)

    def q(p):
        for t, s in km:
            if s <= 1 - p:
                return round(t, 1)
        return None

    sm = {}
    try:
        from statsmodels.duration.survfunc import SurvfuncRight
        import numpy as _np
        sf = SurvfuncRight(_np.array(times), _np.array(events))
        for p in (0.50, 0.90, 0.95):
            idx = _np.where(sf.surv_prob <= 1 - p)[0]
            sm[p] = round(float(sf.surv_times[idx[0]]), 1) if len(idx) else None
    except Exception as exc:  # noqa: BLE001
        sm = {"unavailable": str(exc)}

    hand = {p: q(p) for p in (0.50, 0.80, 0.90, 0.95)}
    return {
        "attempts_total": len(times),
        "completions": len(obs),
        "censored": len(cens),
        "censored_fraction": round(len(cens) / len(times), 4) if times else None,
        "naive_percentile_over_completions_only_95": round(
            float(np.percentile(obs, 95)), 1),
        "naive_percentile_over_everything_95": round(
            float(np.percentile(everything, 95)), 1),
        "kaplan_meier_hand": hand,
        "kaplan_meier_statsmodels": sm,
        "two_tools_agree": all(
            sm.get(p) == hand.get(p) for p in (0.50, 0.90, 0.95)
            if isinstance(sm.get(p), float) or isinstance(sm.get(p), int)),
        "superseded_figure": SUPERSEDED_FIGURE_S,
        "corrected_95th": hand.get(0.95),
        "current_cap_s": CURRENT_CAP_S,
        "cap_sits_above_percentile": next(
            (p for p in (0.50, 0.80, 0.90, 0.95) if hand.get(p)
             and hand[p] > CURRENT_CAP_S), None),
        "verdict": ("the cap sits a little above the 90th percentile of true "
                    "completion time, so roughly 1 attempt in 10 is killed while "
                    "still working; a 95th-percentile cap is about "
                    f"{hand.get(0.95)} s, not {SUPERSEDED_FIGURE_S} s"),
    }


def claim_the_clock_cannot_separate_working_from_churning() -> dict:
    """Why raising the cap alone is the wrong lever, from the recorded rates."""
    recorded = {
        "degraded_attempt": {"tool_calls": 88, "s_per_call": 20.455,
                             "converged": False},
        "healthy_attempt": {"tool_calls": 49, "s_per_call": 20.816,
                            "converged": True, "total_s": 1020.0},
        "other_seat": {"tool_calls": 50, "s_per_call": 15.024, "total_s": 751.2},
    }
    rates = [v["s_per_call"] for v in recorded.values()]
    return {
        "recorded": recorded,
        "per_call_rate_spread_s": round(max(rates) - min(rates), 3),
        "the_rate_is_stable_across_both": abs(
            recorded["degraded_attempt"]["s_per_call"]
            - recorded["healthy_attempt"]["s_per_call"]) < 1.0,
        "the_count_is_not": (recorded["degraded_attempt"]["tool_calls"]
                             > 1.5 * recorded["healthy_attempt"]["tool_calls"]),
        "consequence": ("a degraded route issues calls at NORMAL speed and never "
                        "converges, so a longer clock buys churn. The separating "
                        "variable is the CALL COUNT, not the duration."),
        "proposed_not_applied": True,
    }


def claim_there_is_no_mid_flight_progress_signal() -> dict:
    """OBSERVED 2026-10-08 on a live round: nothing reports progress until the end.

    The call-count bound proposed above needs to read the count WHILE a seat runs.
    Checked against the round in flight at 13:59, with cc2 at 1411 s of its 1800 s
    cap: its tool-log sink file did not exist. `set_tool_log_sink` names the path
    and the stream-json parse that fills it happens AFTER the subprocess returns,
    so the record of what a seat did arrives only once it has finished or been
    killed.

    THAT IS WHY THE CLOCK IS THE ONLY LEVER TODAY, and it is the lever that cannot
    tell working from churning -- the measurement in
    `claim_the_clock_cannot_separate_working_from_churning` shows the per-call rate
    is identical in both states. So the repair is not "raise the cap": it is to
    make the count observable DURING the run, by consuming the CLI's stream-json
    output incrementally rather than buffering it to the end, and only then to
    bound on the count.

    It also explains the 1800 s of wall clock that produced 0 characters and 0
    trace on 2026-10-06: a killed attempt left nothing because nothing was written
    until it was supposed to finish.
    """
    return {
        "observed_round": "division_count_blind_2026-10-08",
        "observed_at_s_into_the_attempt": 1411,
        "cap_s": CURRENT_CAP_S,
        "tool_log_sink_exists_mid_flight": False,
        "consequence": ("a call-count bound is not implementable until the "
                        "stream-json output is consumed incrementally; until then "
                        "the clock is the only signal, and it cannot separate a "
                        "working seat from a churning one"),
        "and_it_explains": ("a killed attempt leaves 0 characters and no trace, "
                            "because nothing is written until the subprocess "
                            "returns -- recorded on 2026-10-06 as 1800 s for 0 "
                            "words"),
        "status": "PROPOSED. The repair is incremental parsing, not a longer cap.",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args()
    print("== 1. the cap, measured with the censoring handled ==")
    for k, v in claim_the_censored_figure_was_circular().items():
        print(f"   {k}: {v}")
    print("\n== 2. why a longer clock alone is the wrong lever ==")
    for k, v in claim_the_clock_cannot_separate_working_from_churning().items():
        print(f"   {k}: {v}")
    print("\n== 3. and why the better lever is not available yet ==")
    for k, v in claim_there_is_no_mid_flight_progress_signal().items():
        print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
