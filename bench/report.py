#!/usr/bin/env python3
"""CDSFL benchmark report generator.

Reads evaluation JSON from evaluate.py and produces:
  - formatted ASCII tables to stdout
  - optional CSV file (--csv path)
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# ASCII table helpers
# ---------------------------------------------------------------------------


def _fmt_pct(value: float | None) -> str:
    """Format a float as a right-aligned percentage string."""
    if value is None:
        return "    n/a"
    return f"{value * 100:>6.1f}%"



def _fmt_int(value: int | None) -> str:
    """Format an integer right-aligned in 6 chars."""
    if value is None:
        return "   n/a"
    return f"{value:>6d}"



def _rule(widths: list[int], char: str = "-", joint: str = "+") -> str:
    """Horizontal rule for a table with given column widths."""
    return joint.join(char * width for width in widths)



def _row(cells: list[str], widths: list[int]) -> str:
    """Format a row of cells padded to given widths."""
    first = f"{cells[0]:<{widths[0]}}"
    rest = [f"{cells[index]:>{widths[index]}}" for index in range(1, len(cells))]
    return "|".join([first] + rest)


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------


def _normalise_fit(fit: dict[str, Any] | None) -> dict[str, Any]:
    """Accept current or legacy corroboration-fit field names."""
    if not fit:
        return {}

    if "estimated_p" in fit:
        return fit

    legacy = dict(fit)
    if "p" in legacy and "estimated_p" not in legacy:
        legacy["estimated_p"] = legacy["p"]
    return legacy



def _normalise_data(data: dict[str, Any]) -> dict[str, Any]:
    """Upgrade legacy evaluation data into the report schema if needed."""
    if "summary" in data and isinstance(data["summary"], dict) and "control" in data["summary"]:
        normalised = dict(data)
        normalised["corroboration_fit"] = _normalise_fit(data.get("corroboration_fit"))
        for domain, payload in normalised.get("per_domain", {}).items():
            if isinstance(payload, dict) and "corroboration_fit" in payload:
                payload["corroboration_fit"] = _normalise_fit(payload["corroboration_fit"])
        return normalised

    raise ValueError("evaluation JSON missing expected report schema")


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------


def print_header(meta: dict[str, Any] | None) -> None:
    print()
    print("=" * 76)
    print("  CDSFL Benchmark Results")
    print("=" * 76)
    if not meta:
        print()
        return

    parts = []
    if meta.get("model"):
        parts.append(f"Model: {meta['model']}")
    if meta.get("provider"):
        parts.append(f"Provider: {meta['provider']}")
    if meta.get("timestamp"):
        parts.append(f"Run: {meta['timestamp']}")
    if meta.get("task_count") is not None:
        parts.append(f"Tasks: {meta['task_count']}")
    if meta.get("total_faults") is not None:
        parts.append(f"Faults: {meta['total_faults']}")
    if meta.get("passes") is not None:
        parts.append(f"Passes: {meta['passes']}")
    if parts:
        print(f"  {' | '.join(parts)}")
    condition = meta.get("directive_condition")
    if condition and condition != "universal-only":
        cond_line = f"  Directive condition: {condition}"
        if meta.get("variant"):
            cond_line += f" (variant: {meta['variant']})"
        if meta.get("domain_directives_source"):
            cond_line += f" from {meta['domain_directives_source']}"
        print(cond_line)
    if meta.get("domains"):
        print(f"  Domains: {', '.join(meta['domains'])}")
    print()



def print_summary_table(summary: dict[str, Any]) -> None:
    print("--- Overall Results ---")
    print()

    headers = ["Condition", "Detection Rate", "Critical Misses", "False Positives"]
    widths = [16, 16, 17, 17]

    print(_row(headers, widths))
    print(_rule(widths))

    for label, key in [("Control", "control"), ("Experimental", "experimental")]:
        section = summary[key]
        cells = [
            label,
            _fmt_pct(section.get("detection_rate")),
            _fmt_int(section.get("critical_misses")),
            _fmt_int(section.get("false_positives")),
        ]
        print(_row(cells, widths))

    control = summary["control"]
    experimental = summary["experimental"]
    delta_rate = (experimental.get("detection_rate") or 0.0) - (control.get("detection_rate") or 0.0)
    delta_misses = (experimental.get("critical_misses") or 0) - (control.get("critical_misses") or 0)
    delta_fp = (experimental.get("false_positives") or 0) - (control.get("false_positives") or 0)

    print(_rule(widths, char=" ", joint=" "))
    cells = [
        "Delta (E-C)",
        f"{delta_rate * 100:+6.1f}pp",
        f"{delta_misses:+6d}",
        f"{delta_fp:+6d}",
    ]
    print(_row(cells, widths))
    print()



def print_domain_table(per_domain: dict[str, Any]) -> None:
    print("--- Per-Domain Breakdown ---")
    print()

    headers = ["Domain", "Cond.", "Detection", "Misses", "FP"]
    widths = [18, 14, 12, 8, 8]

    print(_row(headers, widths))
    print(_rule(widths))

    for domain in sorted(per_domain.keys()):
        payload = per_domain[domain]
        for label, key in [("control", "control"), ("experimental", "experimental")]:
            section = payload[key]
            cells = [
                domain if label == "control" else "",
                label,
                _fmt_pct(section.get("detection_rate")),
                _fmt_int(section.get("critical_misses")),
                _fmt_int(section.get("false_positives")),
            ]
            print(_row(cells, widths))
        print(_rule(widths, char=".", joint="+"))

    print()



def print_pass_table(per_pass: list[dict[str, Any]]) -> None:
    print("--- Per-Pass Cumulative Detection ---")
    print()

    headers = ["Pass", "Marginal", "Cumulative", "Bar"]
    widths = [6, 12, 14, 32]

    print(_row(headers, widths))
    print(_rule(widths))

    for entry in per_pass:
        pass_number = int(entry["pass"])
        marginal_rate = float(entry.get("marginal_detection_rate", 0.0))
        cumulative_rate = float(entry.get("cumulative_detection_rate", 0.0))
        bar_len = int(round(cumulative_rate * 28))
        bar = "#" * bar_len + "." * (28 - bar_len)
        cells = [
            f"{pass_number:>4d}",
            _fmt_pct(marginal_rate),
            _fmt_pct(cumulative_rate),
            f"[{bar}]",
        ]
        print(_row(cells, widths))

    print()



def print_detection_comparison(summary: dict[str, Any], per_domain: dict[str, Any]) -> None:
    """Print cumulative vs final-output-only detection comparison."""
    final_only = summary.get("experimental_final_only")
    if not final_only:
        return

    print("--- Cumulative vs Final-Output Detection ---")
    print()

    headers = ["Metric", "Control", "Cumulative", "Final Only"]
    widths = [18, 12, 14, 14]

    print(_row(headers, widths))
    print(_rule(widths))

    control_rate = summary.get("control", {}).get("detection_rate", 0.0)
    cumulative_rate = summary.get("experimental", {}).get("detection_rate", 0.0)
    final_rate = final_only.get("detection_rate", 0.0)

    cells = [
        "Overall",
        _fmt_pct(control_rate),
        _fmt_pct(cumulative_rate),
        _fmt_pct(final_rate),
    ]
    print(_row(cells, widths))
    print(_rule(widths, char=".", joint="+"))

    for domain in sorted(per_domain.keys()):
        payload = per_domain[domain]
        d_control = payload.get("control", {}).get("detection_rate", 0.0)
        d_cumulative = payload.get("experimental", {}).get("detection_rate", 0.0)
        d_final = payload.get("experimental_final_only", {}).get("detection_rate", 0.0)
        cells = [
            domain,
            _fmt_pct(d_control),
            _fmt_pct(d_cumulative),
            _fmt_pct(d_final),
        ]
        print(_row(cells, widths))

    print()
    gap = cumulative_rate - final_rate
    if gap > 0.001:
        print(
            f"  Note: cumulative rate exceeds final-output rate by "
            f"{gap * 100:.1f}pp. This gap indicates faults mentioned "
            f"during intermediate passes but absent from the final answer."
        )
    elif gap < -0.001:
        print(
            f"  Note: final-output rate exceeds cumulative rate by "
            f"{abs(gap) * 100:.1f}pp (unexpected — review scoring logic)."
        )
    else:
        print("  Note: cumulative and final-output rates are equal.")
    print()


def print_corroboration(fit: dict[str, Any]) -> None:
    fit = _normalise_fit(fit)
    if not fit:
        return

    print("--- Corroboration Curve Fit ---")
    print()

    estimated_p = fit.get("estimated_p")
    r_squared = fit.get("r_squared")

    if estimated_p is None:
        print("  Estimated p:  unavailable")
    else:
        print(f"  Estimated p:  {estimated_p:.4f}")

    if r_squared is None:
        print("  R-squared:    unavailable")
    else:
        print(f"  R-squared:    {r_squared:.4f}")

    if estimated_p is not None:
        print(f"  Model:        C(n) = 1 - (1 - {estimated_p:.4f})^n")
    print()

    if fit.get("note"):
        print(f"  Note:         {fit['note']}")
        print()

    if r_squared is not None:
        if r_squared >= 0.95:
            quality = "excellent"
        elif r_squared >= 0.85:
            quality = "good"
        elif r_squared >= 0.70:
            quality = "moderate"
        else:
            quality = "poor"
        print(f"  Fit quality:  {quality} (R^2 = {r_squared:.4f})")

    if estimated_p is not None and estimated_p > 0.01:
        print()
        print("  Predicted corroboration:")
        for n in [1, 3, 5, 10]:
            corroboration = 1 - (1 - estimated_p) ** n
            print(f"    C({n:>2d}) = {corroboration:.3f}")
    print()


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------


def write_csv(data: dict[str, Any], path: str) -> None:
    """Write evaluation data to CSV."""
    rows: list[list[Any]] = []

    rows.append([
        "section",
        "condition",
        "domain",
        "pass",
        "detection_rate",
        "critical_misses",
        "false_positives",
        "estimated_p",
        "r_squared",
        "final_only_detection_rate",
    ])

    summary = data.get("summary", {})
    for label in ["control", "experimental"]:
        section = summary.get(label, {})
        rows.append([
            "summary",
            label,
            "",
            "",
            section.get("detection_rate", ""),
            section.get("critical_misses", ""),
            section.get("false_positives", ""),
            "",
            "",
            "",
        ])
    # Final-only summary row
    final_only = summary.get("experimental_final_only", {})
    if final_only:
        rows.append([
            "summary",
            "experimental_final_only",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            final_only.get("detection_rate", ""),
        ])

    per_domain = data.get("per_domain", {})
    for domain in sorted(per_domain.keys()):
        payload = per_domain[domain]
        for label in ["control", "experimental"]:
            section = payload.get(label, {})
            rows.append([
                "per_domain",
                label,
                domain,
                "",
                section.get("detection_rate", ""),
                section.get("critical_misses", ""),
                section.get("false_positives", ""),
                "",
                "",
                "",
            ])
        # Final-only per-domain row
        domain_final = payload.get("experimental_final_only", {})
        if domain_final:
            rows.append([
                "per_domain",
                "experimental_final_only",
                domain,
                "",
                "",
                "",
                "",
                "",
                "",
                domain_final.get("detection_rate", ""),
            ])

    for entry in data.get("per_pass", []):
        rows.append([
            "per_pass",
            "experimental",
            "",
            entry.get("pass", ""),
            entry.get("cumulative_detection_rate", ""),
            "",
            "",
            "",
            "",
            "",
        ])

    fit = _normalise_fit(data.get("corroboration_fit"))
    if fit:
        rows.append([
            "corroboration_fit",
            "",
            "",
            "",
            "",
            "",
            "",
            fit.get("estimated_p", ""),
            fit.get("r_squared", ""),
            "",
        ])

    out = Path(path)
    with out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerows(rows)

    print(f"CSV written to {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Format CDSFL benchmark evaluation results.",
        epilog="Reads evaluation JSON from evaluate.py. Prints formatted "
               "tables to stdout and optionally writes CSV.",
    )
    parser.add_argument(
        "evaluation_json",
        help="Path to evaluation JSON file (output of evaluate.py)",
    )
    parser.add_argument(
        "--csv",
        metavar="PATH",
        help="Write results to CSV file at PATH",
    )
    args = parser.parse_args()

    path = Path(args.evaluation_json)
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with path.open("r", encoding="utf-8") as handle:
        try:
            data = json.load(handle)
        except json.JSONDecodeError as exc:
            print(f"Error: invalid JSON in {path}: {exc}", file=sys.stderr)
            sys.exit(1)

    try:
        data = _normalise_data(data)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print_header(data.get("metadata"))
    print_summary_table(data["summary"])

    if data.get("per_domain"):
        print_domain_table(data["per_domain"])

    if data.get("per_pass"):
        print_pass_table(data["per_pass"])

    if data.get("summary", {}).get("experimental_final_only"):
        print_detection_comparison(data["summary"], data.get("per_domain", {}))

    if data.get("corroboration_fit"):
        print_corroboration(data["corroboration_fit"])

    if args.csv:
        write_csv(data, args.csv)


if __name__ == "__main__":
    main()
