"""Archival validation of the latent-tagger + severity calibration, Exp 44-49.

Drives the REAL machinery — ``FindingRegistry``, ``tag_registry``,
``_is_demotion_eligible``, ``_apply_severity_calibration``,
``_settled_novelty_series``, ``_estimate_gamma``, ``_check_gamma_alt_convergence``,
all imported, none reimplemented — over the 293 archival findings from the six
completed live runs, with calibration OFF and ON.

The live per-round critical series is NOT reconstructible from a final registry
(section [0] measures why), so no claim is made about absolute convergence
rounds. Section [3] is a controlled counterfactual: same series both arms.

Read-only on bench/logs/: registries are deep-copied before any mutation.

Three questions, in order:

  Q1 TRUTHFULNESS. Of criticals the falsifier gate later REFUTED or could not
     demonstrate, how many does calibration demote below 0.7? Of criticals it
     CONFIRMED by runnable demonstration, how many does it wrongly demote?
     Reported as a confusion matrix with precision and recall.

  Q2 CEILING. Same matrix under an oracle tagger that tags EVERY entry latent.
     This bounds what any tagger could ever achieve through this calibrator, and
     so separates "the tagger is weak" from "the gate cannot reach the class".

  Q3 IN-SYSTEM EFFECT. Does turning calibration on move the convergence round on
     the real gate? Earlier convergence bought by demoting demonstrated criticals
     is a truthfulness LOSS, not a win, and is reported as such.

Usage:  python3 bench/validate_latent_tagger.py [--verbose]
"""

from __future__ import annotations

import copy
import glob
import json
import os
import sys
from typing import Any, Dict, List, Tuple

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bench.latent_tagger import tag_registry  # noqa: E402
from bench.reference_runner_v2 import (  # noqa: E402
    CRITICAL_SEVERITY_THRESHOLD,
    FindingRegistry,
    RunnerConfig,
    _apply_severity_calibration,
    _calibrate_finding_severity,
    _check_gamma_alt_convergence,
    _estimate_gamma,
    _is_demotion_eligible,
    _settled_novelty_series,
)

LOG_GLOB = os.path.join(_ROOT, "bench", "logs", "exp4[4-9]_*", "exp*_report.json")

# Ground truth for "the severity claim did not survive independent demonstration".
# UNTOOLABLE = no runnable falsifier existed; ERROR = the falsifier would not run;
# REFUTED = it ran and did not demonstrate the defect. All three mean the critical
# rating was never earned. CONFIRMED means it was.
UNEARNED_VERDICTS = {"REFUTED", "UNTOOLABLE", "ERROR"}


def load_runs() -> List[Tuple[str, Dict[str, Any]]]:
    runs = []
    for path in sorted(glob.glob(LOG_GLOB)):
        name = os.path.basename(os.path.dirname(path)).split("_")[0]
        with open(path, encoding="utf-8") as fh:
            runs.append((name, json.load(fh)))
    if not runs:
        raise SystemExit(f"no archival reports matched {LOG_GLOB}")
    return runs


def _cfg_from_report(report: Dict[str, Any], *, calibrate: bool) -> RunnerConfig:
    """RunnerConfig carrying the run's own recorded convergence settings."""
    conv = report.get("convergence_config") or {}
    cfg = RunnerConfig(
        experiment_name=report.get("experiment", "replay"),
        models=list(report.get("models") or ["CC2"]),
    )
    for key, val in conv.items():
        if hasattr(cfg, key):
            setattr(cfg, key, val)
    cfg.severity_calibration_enabled = calibrate
    cfg.latent_tagger_enabled = True
    return cfg


def _oracle_tag_all(registry: FindingRegistry) -> int:
    """Ceiling tagger: assert latent on everything, with no category veto."""
    n = 0
    for entry in registry.entries.values():
        entry["latent"] = True
        entry["finding_category"] = ""
        entry["latent_source"] = "oracle_tag_all"
        n += 1
    return n


def replay(report: Dict[str, Any], *, calibrate: bool, oracle: bool = False):
    """Run the real tagger + calibrator + gate over one archival registry.

    The calibrator skips hard-terminal entries, and 220 of the 293 archival
    findings end their run CLOSED — so sweeping the FINAL registry would demote
    almost nothing and would misrepresent what the mechanism does live, where it
    sweeps every round and each finding spends rounds non-terminal. The
    counterfactual therefore applies the real ``_is_demotion_eligible`` and
    ``_calibrate_finding_severity`` over the whole population, modelling "the
    calibrator would have demoted this at the round it was still open".
    ``_apply_severity_calibration`` is still exercised first, so the shipped
    entry point is on the path.
    """
    registry = FindingRegistry.from_dict(copy.deepcopy(report["registry"]))
    cfg = _cfg_from_report(report, calibrate=calibrate)

    if oracle:
        n_latent = _oracle_tag_all(registry)
    else:
        n_latent = tag_registry(registry)

    max_round = int(report.get("total_rounds") or 1) - 1
    n_demoted = _apply_severity_calibration(registry, cfg, max_round)
    if calibrate:
        floor = cfg.severity_calibration_floor
        for entry in registry.entries.values():
            if _is_demotion_eligible(entry):
                if _calibrate_finding_severity(entry, floor, max_round):
                    n_demoted += 1
    demoted = [
        (cid, e) for cid, e in registry.entries.items()
        if e.get("severity_calibrated")
    ]

    # Real gate, evaluated round by round on the real settled series, with the
    # same arguments the runner passes at its own call site (line ~7042):
    # registry-derived unresolved/irreducible/contested counts, not stubs.
    all_s, crit_s = _settled_novelty_series(registry, max_round)
    converged_at = None
    reason = ""
    for r in range(max_round + 1):
        hist = crit_s[: r + 1]
        gamma_crit = _estimate_gamma(hist, min_rounds=cfg.min_rounds_for_gamma)
        gamma_all = _estimate_gamma(all_s[: r + 1],
                                    min_rounds=cfg.min_rounds_for_gamma)
        ok, why = _check_gamma_alt_convergence(
            r, gamma_all, hist, cfg,
            unresolved_critical=registry.unverified_critical_count(),
            contested=registry.contested_count(
                r, subcritical_exclusion=bool(
                    getattr(cfg, "falsifier_gate_enabled", False)),
            ),
            rho_churn=False,
            irreducible_queue=registry.irreducible_queue_count(),
            gamma_critical=gamma_crit,
            total_findings=len(registry.entries),
        )
        if ok:
            converged_at, reason = r, why
            break
    return {
        "n_latent": n_latent,
        "n_demoted": n_demoted,
        "demoted": demoted,
        "crit_series": crit_s,
        "converged_at": converged_at,
        "reason": reason,
        "registry": registry,
    }


def confusion(runs, *, oracle: bool) -> Dict[str, Any]:
    """Confusion matrix over criticals: would-demote? vs verdict-unearned?

    Population = entries at severity >= 0.7 before calibration. Positive class =
    the falsifier gate never demonstrated the defect (REFUTED / UNTOOLABLE /
    ERROR): those are the inflated severities calibration would need to catch.

    Eligibility is evaluated with the REAL ``_is_demotion_eligible``, and
    WITHOUT the calibrator's terminal-status skip. That is deliberate and it is
    the conservative choice — it *overstates* calibration's reach. A finding
    that ends the run CLOSED was non-terminal (status CONFIRMED) during the
    rounds between its falsifier verdict and its fix, and the calibrator sweeps
    every round, so it was genuinely eligible while the run was live. Judging
    eligibility on final status alone would shrink the addressable population to
    the handful still open at the end and flatter the mechanism by hiding every
    demotion it would really have made.
    """
    tp = fp = fn = tn = 0
    fp_rows, fn_rows, tp_rows = [], [], []
    for name, report in runs:
        registry = FindingRegistry.from_dict(copy.deepcopy(report["registry"]))
        if oracle:
            _oracle_tag_all(registry)
        else:
            tag_registry(registry)  # no skip: tag the whole run population
        for cid, e in registry.entries.items():
            if (e.get("severity") or 0.0) < CRITICAL_SEVERITY_THRESHOLD:
                continue
            unearned = e.get("falsifier_verdict") in UNEARNED_VERDICTS
            hit = _is_demotion_eligible(e)
            if unearned and hit:
                tp += 1
                tp_rows.append((name, cid, e))
            elif unearned and not hit:
                fn += 1
                fn_rows.append((name, cid, e))
            elif not unearned and hit:
                fp += 1
                fp_rows.append((name, cid, e))
            else:
                tn += 1
    precision = tp / (tp + fp) if (tp + fp) else None
    recall = tp / (tp + fn) if (tp + fn) else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": precision, "recall": recall,
            "fp_rows": fp_rows, "fn_rows": fn_rows, "tp_rows": tp_rows}


def _pct(x):
    return "undefined (no positive predictions)" if x is None else f"{x:.3f}"


def main() -> int:
    verbose = "--verbose" in sys.argv
    runs = load_runs()
    total = sum(len(r["registry"]["entries"]) for _, r in runs)

    print("=" * 78)
    print("LATENT-TAGGER + SEVERITY CALIBRATION — ARCHIVAL VALIDATION")
    print(f"corpus: {len(runs)} live runs, {total} findings "
          f"(Exp 44-49, five-model panel)")
    print("=" * 78)

    # ── instrument check: state plainly what this harness can reproduce ──
    print("\n[0] INSTRUMENT CHECK — what this harness can and cannot reproduce")
    print("""
    A replay of the convergence gate from the FINAL registry does NOT
    reproduce the live per-round critical series, and cannot. The runner
    overwrites only novel_critical_history[-1] each round, from the registry
    AS IT STOOD THEN. A critical escalated to UNCONFIRMED at round r is
    excluded from the series at r; when routing later resolves it to CLOSED
    it becomes included — retroactively, in a slot the live gate had already
    read. The final registry therefore reports MORE novel criticals in early
    rounds than the live run ever saw.

    Measured below. The absolute convergence round is consequently NOT
    reconstructible offline, and no claim about it is made anywhere in this
    report. Section [3] is a CONTROLLED COUNTERFACTUAL instead: the same
    settled series in both arms, calibration the only difference. That
    isolates calibration's effect, which is the question being asked.
    """)
    print(f"    {'run':>6}  {'recorded conv':>13}  post-hoc settled critical series")
    for name, report in runs:
        off = replay(report, calibrate=False)
        print(f"    {name:>6}  {str(report.get('converged_at')):>13}  "
              f"{off['crit_series']}")
    ex = next(r for n, r in runs if n == "exp45")
    print("\n    worked example (exp45). The live gate recorded:")
    print(f"      {str(ex.get('convergence_reason'))[:150]}...")
    print("    ...a [0, 0, 0] live tail. The post-hoc settled series for the")
    print(f"    same run is {replay(ex, calibrate=False)['crit_series']} — different numbers, same run.")
    reopened = 0
    for _, report in runs:
        for e in report["registry"]["entries"].values():
            if (e.get("status") == "CLOSED"
                    and (e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD
                    and (e.get("last_status_change_round") or 0)
                    > (e.get("open_since_round") or 0)):
                reopened += 1
    print("\n    criticals that reached CLOSED in a LATER round than they")
    print(f"    opened (the mechanism above): {reopened} of 293.")

    # ── Q1 ──
    print("\n" + "=" * 78)
    print("[1] TRUTHFULNESS — does calibration demote the inflated severities?")
    print("    population: criticals (severity >= 0.7) before calibration")
    print("    positive class: falsifier verdict REFUTED / UNTOOLABLE / ERROR")
    print("=" * 78)
    m = confusion(runs, oracle=False)
    pop = m["tp"] + m["fp"] + m["fn"] + m["tn"]
    print(f"\n    critical population: {pop}")
    print(f"    positives (unearned severity): {m['tp'] + m['fn']}")
    print(f"    negatives (demonstrated real): {m['fp'] + m['tn']}\n")
    print("                          | demoted | not demoted |")
    print("    ----------------------+---------+-------------+")
    print(f"    unearned  (should be) | {m['tp']:^7} | {m['fn']:^11} |")
    print(f"    confirmed (must not)  | {m['fp']:^7} | {m['tn']:^11} |")
    print(f"\n    precision = {_pct(m['precision'])}")
    print(f"    recall    = {_pct(m['recall'])}")
    if m["fn_rows"]:
        print("\n    MISSED (unearned criticals calibration left at critical):")
        for name, cid, e in m["fn_rows"]:
            print(f"      {name} {cid}  sev={e['severity']}  "
                  f"verdict={e['falsifier_verdict']}  status={e['status']}")
    if m["fp_rows"]:
        print("\n    WRONGLY DEMOTED (demonstrated-real criticals):")
        for name, cid, e in m["fp_rows"]:
            print(f"      {name} {cid}  sev={e['severity']}  "
                  f"verdict={e['falsifier_verdict']}")

    # ── Q2 ──
    print("\n" + "=" * 78)
    print("[2] CEILING — same matrix with an ORACLE tagger that tags EVERY")
    print("    finding latent. This is the best any tagger could possibly do")
    print("    through this calibrator.")
    print("=" * 78)
    o = confusion(runs, oracle=True)
    print("\n                          | demoted | not demoted |")
    print("    ----------------------+---------+-------------+")
    print(f"    unearned  (should be) | {o['tp']:^7} | {o['fn']:^11} |")
    print(f"    confirmed (must not)  | {o['fp']:^7} | {o['tn']:^11} |")
    print(f"\n    ceiling precision = {_pct(o['precision'])}")
    print(f"    ceiling recall    = {_pct(o['recall'])}")

    # ── Q3 ──
    print("\n" + "=" * 78)
    print("[3] IN-SYSTEM COUNTERFACTUAL — real convergence gate, real registry,")
    print("    same settled series in both arms, calibration the only difference.")
    print("    Absolute rounds here are NOT the live rounds (see [0]); only the")
    print("    OFF-vs-ON difference is meaningful.")
    print("=" * 78)
    print(f"\n    {'run':>6}  {'latent':>6}  {'demoted':>7}  {'conv OFF':>8}  "
          f"{'conv ON':>7}  {'shift':>5}")
    any_shift = False
    for name, report in runs:
        off = replay(report, calibrate=False)
        on = replay(report, calibrate=True)
        shift = ("same" if off["converged_at"] == on["converged_at"]
                 else f"{off['converged_at']}->{on['converged_at']}")
        any_shift |= (shift != "same")
        print(f"    {name:>6}  {on['n_latent']:>6}  {on['n_demoted']:>7}  "
              f"{str(off['converged_at']):>8}  {str(on['converged_at']):>7}  "
              f"{shift:>5}")
        if verbose:
            for cid, e in on["demoted"]:
                print(f"        demoted {cid}: {e.get('severity_original')} -> "
                      f"{e.get('severity')} | cat={e.get('finding_category')!r} "
                      f"| {e.get('latent_evidence','')[:100]}")
    print(f"\n    convergence verdict changed by calibration: {any_shift}")

    # ── evidence-availability audit ──
    print("\n" + "=" * 78)
    print("[4] EVIDENCE AUDIT — what the tagger had to read")
    print("=" * 78)
    src: Dict[str, int] = {}
    trunc = 0
    for name, report in runs:
        reg = FindingRegistry.from_dict(copy.deepcopy(report["registry"]))
        tag_registry(reg)
        for e in reg.entries.values():
            src[e.get("latent_source", "?")] = src.get(
                e.get("latent_source", "?"), 0) + 1
            if len(e.get("description") or "") >= 500:
                trunc += 1
    print()
    for k, v in sorted(src.items(), key=lambda kv: -kv[1]):
        print(f"    {v:5d}  {k}")
    print("\n    findings whose stored description is truncated at the 500-char")
    print(f"    registry cap (latency prose, if any, may be cut): {trunc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
