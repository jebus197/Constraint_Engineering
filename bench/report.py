#!/usr/bin/env python3
"""
CDSFL Benchmark Report Generator

Takes evaluation JSON (from evaluate.py) and produces:
  - Formatted ASCII table to stdout
  - Optional CSV file (--csv path)

Expected evaluation JSON schema:

{
  "metadata": {
    "model": "...",
    "timestamp": "...",
    "task_count": 30,
    "domains": ["hardware", "software", "logistics"],
    "passes": 5
  },
  "summary": {
    "control": {
      "detection_rate": 0.423,
      "critical_misses": 17,
      "false_positives": 3,
      "total_claims": 300
    },
    "experimental": {
      "detection_rate": 0.876,
      "critical_misses": 4,
      "false_positives": 5,
      "total_claims": 300
    }
  },
  "per_domain": {
    "hardware": {
      "control":      {"detection_rate": 0.40, "critical_misses": 6, "false_positives": 1},
      "experimental": {"detection_rate": 0.90, "critical_misses": 1, "false_positives": 2}
    },
    "software": { ... },
    "logistics": { ... }
  },
  "per_pass": [
    {"pass": 1, "cumulative_detection_rate": 0.45},
    {"pass": 2, "cumulative_detection_rate": 0.70},
    ...
  ],
  "corroboration_fit": {
    "estimated_p": 0.45,
    "r_squared": 0.97
  }
}
"""

import argparse
import csv
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# ASCII table helpers
# ---------------------------------------------------------------------------

def _fmt_pct(value):
    """Format a float as a right-aligned percentage string."""
    return f"{value * 100:>5.1f}%"


def _fmt_int(value):
    """Format an integer right-aligned in 5 chars."""
    return f"{value:>5d}"


def _rule(widths, char="-", joint="+"):
    """Horizontal rule for a table with given column widths."""
    return joint.join(char * w for w in widths)


def _row(cells, widths):
    """Format a row of cells padded to given widths."""
    parts = []
    for cell, w in zip(cells, widths):
        parts.append(f"{cell:<{w}}" if parts == [] else f"{cell:>{w}}")
    # First column left-aligned, rest right-aligned
    first = f"{cells[0]:<{widths[0]}}"
    rest = [f"{cells[i]:>{widths[i]}}" for i in range(1, len(cells))]
    return "|".join([first] + rest)


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def print_header(meta):
    print()
    print("=" * 60)
    print("  CDSFL Benchmark Results")
    print("=" * 60)
    if meta:
        parts = []
        if "model" in meta:
            parts.append(f"Model: {meta['model']}")
        if "timestamp" in meta:
            parts.append(f"Run: {meta['timestamp']}")
        if "task_count" in meta:
            parts.append(f"Tasks: {meta['task_count']}")
        if "passes" in meta:
            parts.append(f"Passes: {meta['passes']}")
        if parts:
            print(f"  {' | '.join(parts)}")
            print()


def print_summary_table(summary):
    """Print the control vs experimental summary table."""
    print("--- Overall Results ---")
    print()

    headers = ["Condition", "Detection Rate", "Critical Misses", "False Positives"]
    widths = [16, 16, 17, 17]

    print(_row(headers, widths))
    print(_rule(widths))

    for label, key in [("Control", "control"), ("Experimental", "experimental")]:
        s = summary[key]
        cells = [
            label,
            _fmt_pct(s["detection_rate"]),
            _fmt_int(s["critical_misses"]),
            _fmt_int(s["false_positives"]),
        ]
        print(_row(cells, widths))

    # Delta row
    ctrl = summary["control"]
    exp = summary["experimental"]
    delta_rate = exp["detection_rate"] - ctrl["detection_rate"]
    delta_misses = exp["critical_misses"] - ctrl["critical_misses"]
    delta_fp = exp["false_positives"] - ctrl["false_positives"]

    print(_rule(widths, char=" ", joint=" "))
    sign = "+" if delta_rate >= 0 else ""
    cells = [
        "Delta (E-C)",
        f"{sign}{delta_rate * 100:>4.1f}pp",
        f"{delta_misses:>+5d}",
        f"{delta_fp:>+5d}",
    ]
    print(_row(cells, widths))
    print()


def print_domain_table(per_domain):
    """Print per-domain breakdown."""
    print("--- Per-Domain Breakdown ---")
    print()

    headers = ["Domain", "Cond.", "Detection", "Misses", "FP"]
    widths = [14, 14, 12, 8, 5]

    print(_row(headers, widths))
    print(_rule(widths))

    for domain in sorted(per_domain.keys()):
        d = per_domain[domain]
        for label, key in [("control", "control"), ("experimental", "experimental")]:
            s = d[key]
            cells = [
                domain if label == "control" else "",
                label,
                _fmt_pct(s["detection_rate"]),
                _fmt_int(s["critical_misses"]),
                _fmt_int(s["false_positives"]),
            ]
            print(_row(cells, widths))
        print(_rule(widths, char=".", joint="+"))

    print()


def print_pass_table(per_pass):
    """Print per-pass cumulative detection rates."""
    print("--- Per-Pass Cumulative Detection ---")
    print()

    headers = ["Pass", "Cumulative Rate", "Bar"]
    widths = [6, 17, 30]

    print(_row(headers, widths))
    print(_rule(widths))

    for entry in per_pass:
        n = entry["pass"]
        rate = entry["cumulative_detection_rate"]
        bar_len = int(rate * 28)
        bar = "#" * bar_len + "." * (28 - bar_len)
        cells = [
            f"{n:>4d}",
            _fmt_pct(rate),
            f" [{bar}]",
        ]
        print(_row(cells, widths))

    print()


def print_corroboration(fit):
    """Print corroboration curve fit results."""
    print("--- Corroboration Curve Fit ---")
    print()
    p = fit["estimated_p"]
    r2 = fit["r_squared"]
    print(f"  Estimated p:  {p:.4f}")
    print(f"  R-squared:    {r2:.4f}")
    print(f"  Model:        C(n) = 1 - (1 - {p:.4f})^n")
    print()

    # Interpretation
    if r2 >= 0.95:
        quality = "excellent"
    elif r2 >= 0.85:
        quality = "good"
    elif r2 >= 0.70:
        quality = "moderate"
    else:
        quality = "poor"

    print(f"  Fit quality:  {quality} (R^2 = {r2:.4f})")

    if p > 0.01:
        # Show predicted corroboration at key pass counts
        print()
        print("  Predicted corroboration:")
        for n in [1, 3, 5, 10]:
            c = 1 - (1 - p) ** n
            print(f"    C({n:>2d}) = {c:.3f}")
    print()


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

def write_csv(data, path):
    """Write evaluation data to CSV."""
    rows = []

    summary = data.get("summary", {})
    meta = data.get("metadata", {})

    # Section 1: Overall summary
    rows.append(["section", "condition", "domain", "pass", "detection_rate",
                 "critical_misses", "false_positives", "estimated_p", "r_squared"])

    for label in ["control", "experimental"]:
        s = summary.get(label, {})
        rows.append([
            "summary", label, "", "",
            s.get("detection_rate", ""),
            s.get("critical_misses", ""),
            s.get("false_positives", ""),
            "", "",
        ])

    # Section 2: Per-domain
    per_domain = data.get("per_domain", {})
    for domain in sorted(per_domain.keys()):
        d = per_domain[domain]
        for label in ["control", "experimental"]:
            s = d.get(label, {})
            rows.append([
                "per_domain", label, domain, "",
                s.get("detection_rate", ""),
                s.get("critical_misses", ""),
                s.get("false_positives", ""),
                "", "",
            ])

    # Section 3: Per-pass
    per_pass = data.get("per_pass", [])
    for entry in per_pass:
        rows.append([
            "per_pass", "experimental", "", entry["pass"],
            entry["cumulative_detection_rate"],
            "", "", "", "",
        ])

    # Section 4: Corroboration fit
    fit = data.get("corroboration_fit", {})
    if fit:
        rows.append([
            "corroboration_fit", "", "", "",
            "", "", "",
            fit.get("estimated_p", ""),
            fit.get("r_squared", ""),
        ])

    out = Path(path)
    with out.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"CSV written to {out}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Format CDSFL benchmark evaluation results.",
        epilog="Reads evaluation JSON from evaluate.py. "
               "Prints formatted table to stdout, optionally writes CSV.",
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

    # Load evaluation data
    path = Path(args.evaluation_json)
    if not path.exists():
        print(f"Error: {path} not found", file=sys.stderr)
        sys.exit(1)

    with path.open() as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: invalid JSON in {path}: {e}", file=sys.stderr)
            sys.exit(1)

    # Validate minimum required keys
    missing = []
    for key in ["summary"]:
        if key not in data:
            missing.append(key)
    if missing:
        print(f"Error: evaluation JSON missing required keys: {', '.join(missing)}",
              file=sys.stderr)
        sys.exit(1)

    # Print report
    print_header(data.get("metadata"))
    print_summary_table(data["summary"])

    if "per_domain" in data:
        print_domain_table(data["per_domain"])

    if "per_pass" in data:
        print_pass_table(data["per_pass"])

    if "corroboration_fit" in data:
        print_corroboration(data["corroboration_fit"])

    # CSV output
    if args.csv:
        write_csv(data, args.csv)


if __name__ == "__main__":
    main()
