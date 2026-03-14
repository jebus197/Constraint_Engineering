#!/usr/bin/env python3
"""Scoring engine for CDSFL seeded-fault benchmark results.

Reads raw results from run_benchmark.py and emits a report-oriented evaluation
schema consumed directly by report.py.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Detection logic
# ---------------------------------------------------------------------------


def _tokenise(text: str) -> list[str]:
    """Split text into lowercase alphanumeric tokens."""
    return re.findall(r"[a-z0-9]+", text.lower())



def _extract_keywords(fault: dict[str, Any]) -> list[str]:
    """Pull searchable keywords from a fault's type, description, and hint."""
    parts: list[str] = []
    if fault.get("type"):
        parts.extend(_tokenise(str(fault["type"])))
    if fault.get("description"):
        parts.extend(_tokenise(str(fault["description"])))
    if fault.get("location_hint"):
        parts.extend(_tokenise(str(fault["location_hint"])))

    stopwords = {
        "a", "an", "the", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "shall", "should", "may", "might", "must", "can",
        "could", "of", "in", "to", "for", "with", "on", "at", "from",
        "by", "as", "into", "through", "during", "before", "after",
        "and", "but", "or", "nor", "not", "no", "so", "if", "then",
        "than", "that", "this", "it", "its",
    }
    return [token for token in parts if len(token) > 2 and token not in stopwords]



def fault_detected(response: str, fault: dict[str, Any], threshold: int = 2) -> bool:
    """Return True if response mentions enough keywords from a seeded fault."""
    if not response:
        return False
    keywords = _extract_keywords(fault)
    if not keywords:
        return False
    response_lower = response.lower()
    hits = sum(1 for keyword in set(keywords) if keyword in response_lower)
    return hits >= threshold


# ---------------------------------------------------------------------------
# False-positive approximation
# ---------------------------------------------------------------------------

_FP_INDICATORS = ["error", "flaw", "issue", "problem", "violation", "impossible"]



def _count_unmatched_indicators(response: str, faults: list[dict[str, Any]]) -> int:
    """Count issue words that do not map cleanly onto seeded-fault keywords."""
    if not response:
        return 0

    response_lower = response.lower()
    all_fault_keywords: set[str] = set()
    for fault in faults:
        all_fault_keywords.update(_extract_keywords(fault))

    count = 0
    for indicator in _FP_INDICATORS:
        occurrences = response_lower.count(indicator)
        if occurrences and indicator not in all_fault_keywords:
            count += occurrences
    return count


# ---------------------------------------------------------------------------
# Curve fitting: C(n) = 1 - (1-p)^n
# ---------------------------------------------------------------------------


def _fit_cumulative_curve(cumulative_rates: list[float]) -> dict[str, Any]:
    """Fit C(n) = 1 - (1-p)^n to observed cumulative detection fractions."""
    if not cumulative_rates:
        return {"estimated_p": None, "r_squared": None, "note": "no data points"}

    n_values = list(range(1, len(cumulative_rates) + 1))
    observed = cumulative_rates

    try:
        from scipy.optimize import curve_fit  # type: ignore[import-untyped]
        import numpy as np  # type: ignore[import-untyped]
    except ImportError:
        p_est = observed[0]
        return {
            "estimated_p": round(p_est, 6),
            "r_squared": None,
            "fitted_values": None,
            "note": "scipy not installed; estimated_p derived from first pass only",
        }

    def model(n: Any, p: float) -> Any:
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

        ss_res = sum((obs - fit) ** 2 for obs, fit in zip(observed, fitted))
        mean_obs = sum(observed) / len(observed)
        ss_tot = sum((obs - mean_obs) ** 2 for obs in observed)
        r_sq = 1.0 - ss_res / ss_tot if ss_tot > 0 else 1.0

        return {
            "estimated_p": round(p_fit, 6),
            "r_squared": round(r_sq, 6),
            "fitted_values": [round(value, 6) for value in fitted],
        }
    except Exception as exc:  # pragma: no cover - defensive fallback
        return {
            "estimated_p": None,
            "r_squared": None,
            "note": f"curve_fit failed: {exc}",
        }


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------


def load_raw_results(path: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load raw benchmark results from either list or object form."""
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    if isinstance(payload, list):
        return {}, payload

    if isinstance(payload, dict) and isinstance(payload.get("results"), list):
        return payload.get("benchmark_meta", {}), payload["results"]

    print(
        "Error: input JSON must be either a raw list of task results or an "
        "object containing benchmark_meta/results.",
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Main scoring
# ---------------------------------------------------------------------------


def _compute_detection_metrics(records: list[dict[str, Any]], n_passes: int) -> dict[str, Any]:
    """Compute control/experimental detection metrics for a record set."""
    total_faults = len(records)
    if total_faults == 0:
        empty_per_pass = [
            {
                "pass": pass_number,
                "new_detections": 0,
                "marginal_detection_rate": 0.0,
                "cumulative_detection_rate": 0.0,
            }
            for pass_number in range(1, n_passes + 1)
        ]
        return {
            "total_faults": 0,
            "control_hits": 0,
            "experimental_hits": 0,
            "final_only_hits": 0,
            "control_detection_rate": 0.0,
            "experimental_detection_rate": 0.0,
            "final_only_detection_rate": 0.0,
            "control_critical_misses": 0,
            "experimental_critical_misses": 0,
            "per_pass": empty_per_pass,
            "cumulative_curve": [0.0 for _ in range(n_passes)],
            "curve_fit": _fit_cumulative_curve([]),
        }

    control_hits = sum(1 for record in records if record["control_detected"])
    experimental_hits = sum(1 for record in records if record["experimental_detected"])
    final_only_hits = sum(
        1 for record in records if record.get("experimental_final_only_detected", False)
    )

    detected_by_pass: dict[int, int] = defaultdict(int)
    for record in records:
        detected_pass = record["experimental_detected_on_pass"]
        if detected_pass is not None:
            detected_by_pass[detected_pass] += 1

    cumulative_hits = 0
    per_pass: list[dict[str, Any]] = []
    cumulative_curve: list[float] = []
    for pass_number in range(1, n_passes + 1):
        newly = detected_by_pass.get(pass_number, 0)
        cumulative_hits += newly
        cumulative_rate = round(cumulative_hits / total_faults, 6)
        per_pass.append(
            {
                "pass": pass_number,
                "new_detections": newly,
                "marginal_detection_rate": round(newly / total_faults, 6),
                "cumulative_detection_rate": cumulative_rate,
            }
        )
        cumulative_curve.append(cumulative_rate)

    return {
        "total_faults": total_faults,
        "control_hits": control_hits,
        "experimental_hits": experimental_hits,
        "final_only_hits": final_only_hits,
        "control_detection_rate": round(control_hits / total_faults, 6),
        "experimental_detection_rate": round(experimental_hits / total_faults, 6),
        "final_only_detection_rate": round(final_only_hits / total_faults, 6),
        "control_critical_misses": total_faults - control_hits,
        "experimental_critical_misses": total_faults - experimental_hits,
        "per_pass": per_pass,
        "cumulative_curve": cumulative_curve,
        "curve_fit": _fit_cumulative_curve(cumulative_curve),
    }



def score_results(
    raw_meta: dict[str, Any],
    results: list[dict[str, Any]],
) -> dict[str, Any]:
    """Score raw task results and return the evaluation schema for report.py."""
    all_fault_records: list[dict[str, Any]] = []
    domain_fault_records: dict[str, list[dict[str, Any]]] = defaultdict(list)

    fp_totals = {
        "control": 0,
        "experimental": 0,
    }
    fp_responses = {
        "control": 0,
        "experimental": 0,
    }
    domain_fp_totals: dict[str, dict[str, int]] = defaultdict(lambda: {"control": 0, "experimental": 0})
    domain_fp_responses: dict[str, dict[str, int]] = defaultdict(lambda: {"control": 0, "experimental": 0})

    max_passes = 0
    for task in results:
        task_passes = task.get("experimental", {}).get("passes", [])
        if task_passes:
            max_passes = max(max_passes, max(p.get("pass_number", 0) for p in task_passes))

    for task in results:
        task_id = task.get("task_id", "unknown")
        domain = task.get("domain", "unknown")
        faults = task.get("seeded_faults", [])
        control_response = task.get("control", {}).get("response", "")
        passes = sorted(
            task.get("experimental", {}).get("passes", []),
            key=lambda item: item.get("pass_number", 0),
        )

        fp_responses["control"] += 1
        domain_fp_responses[domain]["control"] += 1
        control_fp = _count_unmatched_indicators(control_response, faults)
        fp_totals["control"] += control_fp
        domain_fp_totals[domain]["control"] += control_fp

        for p in passes:
            experimental_response = p.get("response", "")
            fp_responses["experimental"] += 1
            domain_fp_responses[domain]["experimental"] += 1
            experimental_fp = _count_unmatched_indicators(experimental_response, faults)
            fp_totals["experimental"] += experimental_fp
            domain_fp_totals[domain]["experimental"] += experimental_fp

        # Get the final response for final-output-only scoring
        final_response = task.get("experimental", {}).get("final_response", "")

        for fault in faults:
            record = {
                "task_id": task_id,
                "domain": domain,
                "fault_id": fault.get("id", "unknown"),
                "fault_type": fault.get("type", ""),
                "control_detected": fault_detected(control_response, fault),
                "experimental_detected_on_pass": None,
                "experimental_detected": False,
                "experimental_final_only_detected": fault_detected(
                    final_response, fault
                ),
            }

            for p in passes:
                pass_number = p.get("pass_number", 0)
                response = p.get("response", "")
                if fault_detected(response, fault):
                    if record["experimental_detected_on_pass"] is None:
                        record["experimental_detected_on_pass"] = pass_number
                    record["experimental_detected"] = True

            all_fault_records.append(record)
            domain_fault_records[domain].append(record)

    overall = _compute_detection_metrics(all_fault_records, max_passes)

    per_domain: dict[str, dict[str, Any]] = {}
    for domain in sorted(domain_fault_records):
        metrics = _compute_detection_metrics(domain_fault_records[domain], max_passes)
        per_domain[domain] = {
            "control": {
                "detection_rate": metrics["control_detection_rate"],
                "critical_misses": metrics["control_critical_misses"],
                "false_positives": domain_fp_totals[domain]["control"],
                "total_faults": metrics["total_faults"],
            },
            "experimental": {
                "detection_rate": metrics["experimental_detection_rate"],
                "critical_misses": metrics["experimental_critical_misses"],
                "false_positives": domain_fp_totals[domain]["experimental"],
                "total_faults": metrics["total_faults"],
            },
            "experimental_final_only": {
                "detection_rate": metrics["final_only_detection_rate"],
                "total_faults": metrics["total_faults"],
            },
            "per_pass": metrics["per_pass"],
            "corroboration_fit": metrics["curve_fit"],
            "false_positive_detail": {
                "control": {
                    "total_unmatched_indicators": domain_fp_totals[domain]["control"],
                    "responses_checked": domain_fp_responses[domain]["control"],
                    "rate_per_response": round(
                        domain_fp_totals[domain]["control"] / domain_fp_responses[domain]["control"],
                        6,
                    ) if domain_fp_responses[domain]["control"] else 0.0,
                },
                "experimental": {
                    "total_unmatched_indicators": domain_fp_totals[domain]["experimental"],
                    "responses_checked": domain_fp_responses[domain]["experimental"],
                    "rate_per_response": round(
                        domain_fp_totals[domain]["experimental"] / domain_fp_responses[domain]["experimental"],
                        6,
                    ) if domain_fp_responses[domain]["experimental"] else 0.0,
                },
            },
        }

    metadata: dict[str, Any] = {
        "schema_version": "cdsfl-eval-v2",
        "model": raw_meta.get("model"),
        "provider": raw_meta.get("provider"),
        "timestamp": raw_meta.get("timestamp_utc"),
        "task_count": raw_meta.get("task_count", len(results)),
        "domains": raw_meta.get("domains") or sorted(per_domain.keys()),
        "passes": raw_meta.get("num_passes", max_passes),
        "directives_source": raw_meta.get("directives_source"),
        "directive_condition": raw_meta.get("directive_condition", "universal-only"),
        "total_faults": overall["total_faults"],
    }
    if raw_meta.get("domain_directives_source"):
        metadata["domain_directives_source"] = raw_meta["domain_directives_source"]
    if raw_meta.get("variant"):
        metadata["variant"] = raw_meta["variant"]

    summary = {
        "control": {
            "detection_rate": overall["control_detection_rate"],
            "critical_misses": overall["control_critical_misses"],
            "false_positives": fp_totals["control"],
            "total_faults": overall["total_faults"],
        },
        "experimental": {
            "detection_rate": overall["experimental_detection_rate"],
            "critical_misses": overall["experimental_critical_misses"],
            "false_positives": fp_totals["experimental"],
            "total_faults": overall["total_faults"],
        },
        "experimental_final_only": {
            "detection_rate": overall["final_only_detection_rate"],
            "total_faults": overall["total_faults"],
        },
    }

    false_positive_detail = {
        "control": {
            "total_unmatched_indicators": fp_totals["control"],
            "responses_checked": fp_responses["control"],
            "rate_per_response": round(fp_totals["control"] / fp_responses["control"], 6)
            if fp_responses["control"] else 0.0,
        },
        "experimental": {
            "total_unmatched_indicators": fp_totals["experimental"],
            "responses_checked": fp_responses["experimental"],
            "rate_per_response": round(fp_totals["experimental"] / fp_responses["experimental"], 6)
            if fp_responses["experimental"] else 0.0,
        },
    }

    control_vs_experimental = {
        "control_detection_rate": overall["control_detection_rate"],
        "experimental_detection_rate": overall["experimental_detection_rate"],
        "final_only_detection_rate": overall["final_only_detection_rate"],
        "detection_rate_lift": round(
            overall["experimental_detection_rate"] - overall["control_detection_rate"],
            6,
        ),
        "final_only_lift": round(
            overall["final_only_detection_rate"] - overall["control_detection_rate"],
            6,
        ),
        "critical_miss_delta": (
            overall["experimental_critical_misses"] - overall["control_critical_misses"]
        ),
        "false_positive_delta": fp_totals["experimental"] - fp_totals["control"],
    }

    return {
        "metadata": metadata,
        "summary": summary,
        "per_domain": per_domain,
        "per_pass": overall["per_pass"],
        "corroboration_fit": overall["curve_fit"],
        "control_vs_experimental": control_vs_experimental,
        "false_positive_detail": false_positive_detail,
        "fault_details": all_fault_records,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score seeded-fault benchmark results.",
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

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: {input_path} not found", file=sys.stderr)
        sys.exit(1)

    raw_meta, results = load_raw_results(input_path)
    scored = score_results(raw_meta, results)
    output_json = json.dumps(scored, indent=2)

    if args.output:
        Path(args.output).write_text(output_json + "\n", encoding="utf-8")
    else:
        print(output_json)


if __name__ == "__main__":
    main()
