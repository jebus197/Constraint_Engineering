#!/usr/bin/env python3
"""Scoring engine for seeded-fault benchmark results.

Takes raw results JSON (from run_benchmark.py) and computes detection rates,
cumulative detection curves, curve-fit parameters, false positive estimates,
and per-domain breakdowns.
"""

import argparse
import json
import math
import re
import sys
from collections import defaultdict


# ---------------------------------------------------------------------------
# Detection logic
# ---------------------------------------------------------------------------

def _tokenise(text: str) -> list[str]:
    """Split text into lowercase alphanumeric tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())


def _extract_keywords(fault: dict) -> list[str]:
    """Pull searchable keywords from a fault's type, description, and location_hint."""
    parts: list[str] = []
    if fault.get("type"):
        parts.extend(_tokenise(fault["type"]))
    if fault.get("description"):
        parts.extend(_tokenise(fault["description"]))
    if fault.get("location_hint"):
        parts.extend(_tokenise(fault["location_hint"]))
    # Drop very short / stopword-like tokens
    stopwords = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "shall", "should", "may", "might", "must", "can",
        "could", "of", "in", "to", "for", "with", "on", "at", "from",
        "by", "as", "into", "through", "during", "before", "after",
        "and", "but", "or", "nor", "not", "no", "so", "if", "then",
        "than", "that", "this", "it", "its",
    }
    return [t for t in parts if len(t) > 2 and t not in stopwords]


def fault_detected(response: str, fault: dict, threshold: int = 2) -> bool:
    """Return True if *response* mentions >= *threshold* keywords from *fault*."""
    if not response:
        return False
    response_lower = response.lower()
    keywords = _extract_keywords(fault)
    if not keywords:
        return False
    hits = sum(1 for kw in set(keywords) if kw in response_lower)
    return hits >= threshold


# ---------------------------------------------------------------------------
# False-positive approximation
# ---------------------------------------------------------------------------

_FP_INDICATORS = ["error", "flaw", "issue", "problem", "violation", "impossible"]


def _count_unmatched_indicators(response: str, faults: list[dict]) -> int:
    """Count occurrences of generic issue-words that don't correspond to any seeded fault."""
    if not response:
        return 0
    response_lower = response.lower()
    # Build set of all fault keywords so we can check overlap
    all_fault_keywords: set[str] = set()
    for f in faults:
        all_fault_keywords.update(_extract_keywords(f))

    count = 0
    for indicator in _FP_INDICATORS:
        occurrences = response_lower.count(indicator)
        if occurrences and indicator not in all_fault_keywords:
            count += occurrences
    return count


# ---------------------------------------------------------------------------
# Curve fitting: C(n) = 1 - (1-p)^n
# ---------------------------------------------------------------------------

def _fit_cumulative_curve(cumulative_rates: list[float]) -> dict:
    """Fit C(n) = 1 - (1-p)^n to observed cumulative detection fractions.

    Returns dict with 'p', 'r_squared', and 'fitted_values', or an error note
    if scipy is unavailable or the fit fails.
    """
    if not cumulative_rates:
        return {"error": "no data points"}

    n_values = list(range(1, len(cumulative_rates) + 1))
    observed = cumulative_rates

    try:
        from scipy.optimize import curve_fit  # type: ignore[import-untyped]
        import numpy as np  # type: ignore[import-untyped]
    except ImportError:
        # Graceful fallback: estimate p from first data point only
        p_est = 1.0 - (1.0 - observed[0]) if observed[0] < 1.0 else 1.0
        return {
            "p": round(p_est, 6),
            "r_squared": None,
            "fitted_values": None,
            "note": "scipy not installed; p estimated from first data point only",
        }

    def model(n, p):
        return 1.0 - (1.0 - p) ** n

    try:
        popt, _ = curve_fit(
            model,
            np.array(n_values, dtype=float),
            np.array(observed, dtype=float),
            p0=[0.3],
            bounds=(0.0, 1.0),
        )
        p_fit = float(popt[0])
        fitted = [float(model(n, p_fit)) for n in n_values]

        # R²
        ss_res = sum((o - f) ** 2 for o, f in zip(observed, fitted))
        mean_obs = sum(observed) / len(observed)
        ss_tot = sum((o - mean_obs) ** 2 for o in observed)
        r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

        return {
            "p": round(p_fit, 6),
            "r_squared": round(r_sq, 6),
            "fitted_values": [round(v, 6) for v in fitted],
        }
    except Exception as exc:
        return {"error": f"curve_fit failed: {exc}"}


# ---------------------------------------------------------------------------
# Main scoring
# ---------------------------------------------------------------------------

def score_results(results: list[dict]) -> dict:
    """Score a list of task results and return a full metrics dict."""

    all_fault_records: list[dict] = []
    domain_fault_records: dict[str, list[dict]] = defaultdict(list)

    total_fp_control = 0
    total_fp_experimental = 0
    total_control_responses = 0
    total_experimental_responses = 0

    # Determine max pass count across all tasks
    max_passes = 0
    for task in results:
        passes = task.get("experimental", {}).get("passes", [])
        if passes:
            max_passes = max(max_passes, max(p.get("pass_number", 0) for p in passes))

    for task in results:
        task_id = task.get("task_id", "unknown")
        domain = task.get("domain", "unknown")
        faults = task.get("seeded_faults", [])
        control_resp = task.get("control", {}).get("response", "")
        passes = task.get("experimental", {}).get("passes", [])

        # Sort passes by pass_number
        passes_sorted = sorted(passes, key=lambda p: p.get("pass_number", 0))

        # False positives — control
        total_control_responses += 1
        total_fp_control += _count_unmatched_indicators(control_resp, faults)

        # False positives — experimental
        for p in passes_sorted:
            total_experimental_responses += 1
            total_fp_experimental += _count_unmatched_indicators(
                p.get("response", ""), faults
            )

        for fault in faults:
            record: dict = {
                "task_id": task_id,
                "domain": domain,
                "fault_id": fault.get("id", "unknown"),
                "fault_type": fault.get("type", ""),
                "control_detected": fault_detected(control_resp, fault),
                "experimental_detected_on_pass": None,  # first pass that detects it
                "experimental_detected": False,
            }

            for p in passes_sorted:
                pnum = p.get("pass_number", 0)
                resp = p.get("response", "")
                if fault_detected(resp, fault):
                    if record["experimental_detected_on_pass"] is None:
                        record["experimental_detected_on_pass"] = pnum
                    record["experimental_detected"] = True

            all_fault_records.append(record)
            domain_fault_records[domain].append(record)

    # ------------------------------------------------------------------
    # Aggregate metrics
    # ------------------------------------------------------------------
    total_faults = len(all_fault_records)

    def _compute_metrics(records: list[dict], n_passes: int) -> dict:
        n = len(records)
        if n == 0:
            return {
                "total_faults": 0,
                "control_detection_rate": 0.0,
                "experimental_detection_rate": 0.0,
                "per_pass_marginal": [],
                "cumulative_curve": [],
                "curve_fit": {"error": "no faults"},
            }

        control_hits = sum(1 for r in records if r["control_detected"])
        exp_hits = sum(1 for r in records if r["experimental_detected"])

        # Per-pass marginal and cumulative
        detected_by_pass: dict[int, int] = defaultdict(int)
        for r in records:
            p = r["experimental_detected_on_pass"]
            if p is not None:
                detected_by_pass[p] += 1

        cumulative = 0
        per_pass_marginal: list[dict] = []
        cumulative_curve: list[float] = []
        for pn in range(1, n_passes + 1):
            newly = detected_by_pass.get(pn, 0)
            cumulative += newly
            per_pass_marginal.append({
                "pass": pn,
                "new_detections": newly,
                "marginal_rate": round(newly / n, 6) if n else 0.0,
            })
            cumulative_curve.append(round(cumulative / n, 6) if n else 0.0)

        fit = _fit_cumulative_curve(cumulative_curve) if cumulative_curve else {"error": "no passes"}

        return {
            "total_faults": n,
            "control_detection_rate": round(control_hits / n, 6),
            "experimental_detection_rate": round(exp_hits / n, 6),
            "per_pass_marginal": per_pass_marginal,
            "cumulative_curve": cumulative_curve,
            "curve_fit": fit,
        }

    overall = _compute_metrics(all_fault_records, max_passes)

    # Per-domain
    per_domain: dict[str, dict] = {}
    for dom in sorted(domain_fault_records):
        per_domain[dom] = _compute_metrics(domain_fault_records[dom], max_passes)

    # False positive summary
    fp_summary = {
        "control": {
            "total_unmatched_indicators": total_fp_control,
            "responses_checked": total_control_responses,
            "rate_per_response": (
                round(total_fp_control / total_control_responses, 6)
                if total_control_responses
                else 0.0
            ),
        },
        "experimental": {
            "total_unmatched_indicators": total_fp_experimental,
            "responses_checked": total_experimental_responses,
            "rate_per_response": (
                round(total_fp_experimental / total_experimental_responses, 6)
                if total_experimental_responses
                else 0.0
            ),
        },
    }

    # Control vs experimental comparison
    comparison = {
        "control_detection_rate": overall["control_detection_rate"],
        "experimental_detection_rate": overall["experimental_detection_rate"],
        "lift": round(
            overall["experimental_detection_rate"] - overall["control_detection_rate"], 6
        ),
    }

    return {
        "summary": {
            "total_tasks": len(results),
            "total_faults": total_faults,
            "max_passes": max_passes,
        },
        "overall": overall,
        "per_domain": per_domain,
        "false_positives": fp_summary,
        "control_vs_experimental": comparison,
        "fault_details": all_fault_records,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score seeded-fault benchmark results."
    )
    parser.add_argument(
        "input",
        help="Path to raw results JSON file (from run_benchmark.py).",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Write scored output JSON to this file (default: stdout).",
    )
    args = parser.parse_args()

    with open(args.input, "r") as f:
        results = json.load(f)

    if not isinstance(results, list):
        print("Error: input JSON must be a list of task results.", file=sys.stderr)
        sys.exit(1)

    scored = score_results(results)
    output_json = json.dumps(scored, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output_json)
            f.write("\n")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
