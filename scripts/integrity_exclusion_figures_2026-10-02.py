#!/usr/bin/env python3
"""Every figure quoted by the 2026-10-02 integrity-exclusion merge.

WHY THIS EXISTS. The merge of the cc2 and fable panel fixes carries 3 numeric
claims in its code comments, and all 3 arrived as PROSE in a seat's reply. A
number that exists only as prose is a claim about evidence, not evidence
(`measured-rate-travels-with-its-script`). This script is committed beside
them and reproduces each one, or contradicts it.

IT ALREADY CONTRADICTED ONE. The cc2 seat's A4 justification cited "156 of 263
UNCONFIRMED criticals (59.32%) carry ZERO verdicts". Over the 57 archived
`runner_state.json` registries this script reads, the population is 86, not
263, and the rate is 58 of 86. The seat's denominator could not be
reproduced -- most likely the report/state double-count this project already
records as having corrupted 2 measurements in 1 night, both in the reassuring
direction. THE QUALITATIVE CLAIM SURVIVES IN BOTH READINGS, which is why the
merge keeps the argument and changes the figure: the valve opens for a
MINORITY either way, and the Wilson lower bound here is above 50%.

Cross-verification: Wilson by statsmodels against an independent mpmath closed
form, as the 21 Apr 2026 two-tool rule requires. No Wolfram result is used.
"""
from __future__ import annotations

import json
import pathlib
import sys

# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# first version of this preamble inserted the repo ROOT and so worked when the
# file was RUN (sys.path[0] is the script dir) and failed when it was IMPORTED,
# which is how 13 scripts stopped importing on 2026-09-24.
for _cand in (pathlib.Path(__file__).resolve().parent,
              *pathlib.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402


ROOT = pathlib.Path(__file__).resolve().parents[1]
RUN_1B = "prose_convergence_run1b_2026-10-02_20261002T044234Z"
CRITICAL = 0.7


def wilson(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    import mpmath as mp
    lo_sm, hi_sm = proportion_confint(k, n, method="wilson")
    mp.mp.dps = 40
    z = mp.mpf("1.959963984540054235524594430520551527955")
    p, d = mp.mpf(k) / n, 1 + mp.mpf(z) ** 2 / n
    c = p + z ** 2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return (float(lo_sm), float(hi_sm)), (float((c - h) / d), float((c + h) / d))


def zero_verdict_rate():
    """How often the `exhausted` release valve CANNOT open.

    The valve in `unverified_critical_count` requires `len(verdicts) > 0`. An
    UNCONFIRMED critical with no verdicts can never pass it, so excusing a
    key-access refusal from the HALT BOUND alone would leave those entries
    blocking A4 until `max_rounds`.
    """
    tot = zero = runs = 0
    for st in sorted((ROOT / "bench" / "logs").glob("*/runner_state.json")):
        try:
            reg = json.loads(st.read_text()).get("registry", {}).get("entries", {})
        except Exception:                                      # noqa: BLE001
            continue
        runs += 1
        for e in reg.values():
            if not isinstance(e, dict) or e.get("status") != "UNCONFIRMED":
                continue
            if (e.get("severity") or 0.0) < CRITICAL:
                continue
            tot += 1
            if not (e.get("verdicts") or e.get("votes") or []):
                zero += 1
    return runs, zero, tot


def run_1b_halt():
    """Run 1b halted with BOTH halves of the two-sided gate satisfied."""
    d = ROOT / "bench" / "logs" / RUN_1B
    rep = json.loads(next(d.glob("*_report.json")).read_text())
    last = [r for r in rep.get("rounds", []) if r.get("round") == 2]
    alarm = rep.get("irreducible_queue_alarm", {})
    return {
        "stop_reason": rep.get("stop_reason"),
        "gamma_critical_r2": last[0].get("gamma_critical") if last else None,
        "gamma_all_r2": last[0].get("gamma_all") if last else None,
        "queue_count": alarm.get("count"),
        "queue_bound": alarm.get("bound"),
        "alarm_round": alarm.get("round"),
    }


def ladder_side_residual():
    """The D-6 case: how many entries carry an integrity verdict, and where."""
    d = ROOT / "bench" / "logs" / RUN_1B
    reg = json.loads((d / "runner_state.json").read_text())["registry"]["entries"]
    out = []
    for cid, e in reg.items():
        if not isinstance(e, dict):
            continue
        fv = (e.get("falsifier_verdict") or "").upper()
        ru = (e.get("routing_verdict_unreconciled") or "").upper()
        if "INTEGRITY" in fv or "INTEGRITY" in ru:
            rh = e.get("routing_history") or []
            out.append({
                "cid": cid, "status": e.get("status"),
                "severity": e.get("severity"),
                "falsifier_verdict": e.get("falsifier_verdict"),
                "routing_verdict_unreconciled": e.get("routing_verdict_unreconciled"),
                "routing_history_last": rh[-1].get("verdict") if rh else None,
                "routing_deferred": bool(e.get("routing_deferred")),
            })
    return len(reg), out


def main() -> int:
    runs, zero, tot = zero_verdict_rate()
    print("THE RELEASE VALVE CANNOT OPEN FOR MOST UNCONFIRMED CRITICALS")
    print(f"  archived runner_state.json registries read : {runs}")
    print(f"  UNCONFIRMED criticals (severity >= {CRITICAL})    : {tot}")
    print(f"  of those, carrying ZERO verdicts            : {zero}")
    (l1, h1), (l2, h2) = wilson(zero, tot)
    print(f"  rate {zero}/{tot} = {100*zero/tot:.4f}%  "
          f"Wilson statsmodels [{100*l1:.4f}%, {100*h1:.4f}%]  "
          f"mpmath [{100*l2:.4f}%, {100*h2:.4f}%]")
    print(f"  AGREE to 1e-9: {abs(l1-l2) < 1e-9 and abs(h1-h2) < 1e-9}")
    print(f"  MAJORITY (lower bound above 50%): {l1 > 0.5}")
    print("  NOT REPRODUCED: the cc2 seat's '156 of 263 (59.32%)'. Same "
          "direction, different denominator.")

    print("\nRUN 1b HALTED WITH BOTH HALVES OF THE GATE SATISFIED")
    for k, v in run_1b_halt().items():
        print(f"  {k:22s}: {v}")

    n, rows = ladder_side_residual()
    print(f"\nTHE LADDER-SIDE RESIDUAL (D-6), over {n} entries in run 1b")
    if not rows:
        print("  NONE -- the D-6 case is absent from this run, so the comment "
              "that cites it must be re-stated.")
    for r in rows:
        print(f"  {r}")
    return 0


if __name__ == "__main__":
    # A `--help` MUST NEVER COST ANYTHING (founder ruling, after 15 of 17
    # runners billed a live dispatch on an unrecognised argument). Without
    # this call the flag is ignored and the whole archive measurement runs
    # in answer to a request to be told what the script does -- which is
    # what made the survey guard take minutes.
    answer_help(__doc__, __file__)
    raise SystemExit(main())
