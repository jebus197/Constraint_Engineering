#!/usr/bin/env python3
"""C5 Experiment: Post-Hoc Verification and Analysis.

Reads C5 transcript from logs directory, extracts findings, cross-references
against the Master Finding Registry, and evaluates success/falsification
criteria for the three-layer schema.

Usage:
    python3 bench/c5_verify.py <logs_dir>
    python3 bench/c5_verify.py bench/logs/c5_20260404T...

Outputs analysis to stdout and saves results JSON to the logs directory.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

REGISTRY_PATH = (
    REPO_ROOT / "experimental_notes" / "Master_Finding_Registry_2026-04-04.md"
)


# ---------------------------------------------------------------------------
# Registry parsing
# ---------------------------------------------------------------------------

def parse_registry_ids() -> Dict[str, str]:
    """Parse MF-XX IDs and their short titles from the registry.

    Returns {id: title} e.g. {"MF-01": "MATH_PATTERN Overbroad Regex"}.
    """
    text = REGISTRY_PATH.read_text()
    findings = {}
    for m in re.finditer(r'^###\s+(MF-\d+):\s+(.+)$', text, re.MULTILINE):
        findings[m.group(1)] = m.group(2).strip()
    return findings


# ---------------------------------------------------------------------------
# C5 finding extraction from R8 summary certificate
# ---------------------------------------------------------------------------

def extract_c5_findings(transcript_path: Path) -> List[Dict[str, str]]:
    """Extract structured findings from the R8 summary certificate.

    Looks for C5-XX identifiers and associated structured fields.
    Returns list of finding dicts with available fields.
    """
    text = transcript_path.read_text()

    # Find R8 section
    r8_start = text.rfind("ROUND 8")
    if r8_start == -1:
        print("WARNING: No Round 8 found in transcript. Using full text.")
        r8_text = text
    else:
        r8_text = text[r8_start:]

    findings = []
    # Split on C5-XX markers
    parts = re.split(r'(?=C5-\d+)', r8_text)

    for part in parts:
        id_match = re.match(r'(C5-\d+)', part)
        if not id_match:
            continue

        finding = {"id": id_match.group(1), "raw": part[:2000]}

        # Extract structured fields (flexible matching)
        field_patterns = {
            "component": r'(?:COMPONENT|Component)[:\s]*([^\n]+)',
            "classification": r'(?:CLASSIFICATION|Classification)[:\s]*([^\n]+)',
            "severity": r'(?:SEVERITY|Severity)[:\s]*([^\n]+)',
            "description": r'(?:DESCRIPTION|Description)[:\s]*([^\n]+)',
            "fix_type": r'(?:FIX TYPE|Fix Type|FIX_TYPE)[:\s]*([^\n]+)',
            "prior_match": r'(?:PRIOR MATCH|Prior Match|PRIOR_MATCH)[:\s]*([^\n]+)',
            "status": r'(?:STATUS|Status)[:\s]*([^\n]+)',
        }

        for field, pattern in field_patterns.items():
            m = re.search(pattern, part, re.IGNORECASE)
            if m:
                finding[field] = m.group(1).strip()

        findings.append(finding)

    return findings


# ---------------------------------------------------------------------------
# Cross-reference analysis
# ---------------------------------------------------------------------------

def cross_reference(
    c5_findings: List[Dict[str, str]],
    registry: Dict[str, str],
) -> Dict[str, Any]:
    """Cross-reference C5 findings against master registry.

    Returns analysis dict with overlap, novel, and missing counts.
    """
    # Extract MF-XX references from C5 findings
    confirmed_mf: Set[str] = set()
    novel_findings: List[str] = []
    retracted: List[str] = []
    fix_types = {"PATCH": 0, "NOVEL CONSTRUCT": 0, "ARCHITECTURAL": 0, "UNKNOWN": 0}

    for f in c5_findings:
        # Check if retracted
        status = f.get("status", "").upper()
        if "RETRACT" in status:
            retracted.append(f["id"])
            continue

        # Check prior match
        prior = f.get("prior_match", "")
        mf_refs = re.findall(r'MF-\d+', prior)
        if mf_refs:
            confirmed_mf.update(mf_refs)
        elif "NOVEL" in prior.upper() or not mf_refs:
            novel_findings.append(f["id"])

        # Count fix types
        ft = f.get("fix_type", "UNKNOWN").upper()
        if "NOVEL" in ft:
            fix_types["NOVEL CONSTRUCT"] += 1
        elif "ARCH" in ft:
            fix_types["ARCHITECTURAL"] += 1
        elif "PATCH" in ft:
            fix_types["PATCH"] += 1
        else:
            fix_types["UNKNOWN"] += 1

    # What registry findings were NOT confirmed?
    unconfirmed_mf = set(registry.keys()) - confirmed_mf

    # Count by component
    components: Dict[str, int] = {}
    for f in c5_findings:
        if f["id"] in retracted:
            continue
        comp = f.get("component", "Unknown").strip()
        components[comp] = components.get(comp, 0) + 1

    # Identify cross-component findings
    cross_component = [
        f for f in c5_findings
        if f["id"] not in retracted
        and ("cross" in f.get("component", "").lower()
             or "pipeline" in f.get("component", "").lower()
             or "interaction" in f.get("classification", "").lower())
    ]

    # Count formal proofs
    proof_keywords = ["proof", "prove", "QED", "contradiction", "∀", "∃",
                      "set theory", "formal", "algebraic"]
    findings_with_proofs = 0
    for f in c5_findings:
        if f["id"] in retracted:
            continue
        raw = f.get("raw", "").lower()
        if any(kw.lower() in raw for kw in proof_keywords):
            findings_with_proofs += 1

    # Count severity distribution
    severities = {"P0": 0, "P1": 0, "P2": 0, "P3": 0, "UNKNOWN": 0}
    for f in c5_findings:
        if f["id"] in retracted:
            continue
        sev = f.get("severity", "UNKNOWN").upper()
        matched = False
        for p in ["P0", "P1", "P2", "P3"]:
            if p in sev:
                severities[p] += 1
                matched = True
                break
        if not matched:
            severities["UNKNOWN"] += 1

    return {
        "total_findings": len(c5_findings),
        "surviving": len(c5_findings) - len(retracted),
        "retracted": len(retracted),
        "retracted_ids": retracted,
        "confirmed_mf_count": len(confirmed_mf),
        "confirmed_mf_ids": sorted(confirmed_mf),
        "unconfirmed_mf_count": len(unconfirmed_mf),
        "unconfirmed_mf_ids": sorted(unconfirmed_mf),
        "novel_count": len(novel_findings),
        "novel_ids": novel_findings,
        "cross_component_count": len(cross_component),
        "cross_component_ids": [f["id"] for f in cross_component],
        "findings_with_proofs": findings_with_proofs,
        "fix_types": fix_types,
        "severities": severities,
        "components": components,
    }


# ---------------------------------------------------------------------------
# Success / falsification evaluation
# ---------------------------------------------------------------------------

def evaluate_criteria(
    analysis: Dict[str, Any],
    results_json: Dict[str, Any],
) -> Dict[str, Any]:
    """Evaluate C5 results against success and falsification criteria."""

    surviving = analysis["surviving"]
    total_mf = 40
    confirmed_rate = analysis["confirmed_mf_count"] / total_mf if total_mf else 0
    findings_with_fixes = (
        analysis["fix_types"]["PATCH"]
        + analysis["fix_types"]["NOVEL CONSTRUCT"]
        + analysis["fix_types"]["ARCHITECTURAL"]
    )
    fix_rate = findings_with_fixes / surviving if surviving else 0
    novel_constructs = analysis["fix_types"]["NOVEL CONSTRUCT"]
    itc_triggered = results_json.get("itc_triggered", False)
    itc_before_r5 = results_json.get("itc_before_r5", False)
    total_time_min = results_json.get("total_elapsed_s", 0) / 60

    # Success criteria
    success = {
        "total_verified_ge_30": {
            "value": surviving,
            "threshold": 30,
            "passed": surviving >= 30,
        },
        "cross_component_ge_3": {
            "value": analysis["cross_component_count"],
            "threshold": 3,
            "passed": analysis["cross_component_count"] >= 3,
        },
        "formal_proofs_ge_5": {
            "value": analysis["findings_with_proofs"],
            "threshold": 5,
            "passed": analysis["findings_with_proofs"] >= 5,
        },
        "prior_confirmed_ge_80pct": {
            "value": f"{confirmed_rate:.0%}",
            "threshold": "80%",
            "passed": confirmed_rate >= 0.80,
        },
        "novel_findings_ge_3": {
            "value": analysis["novel_count"],
            "threshold": 3,
            "passed": analysis["novel_count"] >= 3,
        },
        "fixes_ge_90pct": {
            "value": f"{fix_rate:.0%}",
            "threshold": "90%",
            "passed": fix_rate >= 0.90,
        },
        "novel_constructs_ge_3": {
            "value": novel_constructs,
            "threshold": 3,
            "passed": novel_constructs >= 3,
        },
        "no_itc_trigger": {
            "value": not itc_triggered,
            "threshold": True,
            "passed": not itc_triggered,
        },
        "time_under_20_min": {
            "value": f"{total_time_min:.1f} min",
            "threshold": "< 20 min",
            "passed": total_time_min < 20,
        },
    }

    # Falsification criteria
    falsification = {
        "below_c1_baseline": {
            "value": surviving,
            "threshold": "< 25",
            "triggered": surviving < 25,
        },
        "zero_cross_component": {
            "value": analysis["cross_component_count"],
            "threshold": "== 0",
            "triggered": analysis["cross_component_count"] == 0,
        },
        "fewer_proofs_than_c4": {
            "value": analysis["findings_with_proofs"],
            "threshold": "< 11 (C4 had 11)",
            "triggered": analysis["findings_with_proofs"] < 11,
        },
        "itc_before_r5": {
            "value": itc_before_r5,
            "threshold": True,
            "triggered": itc_before_r5,
        },
    }

    success_count = sum(1 for v in success.values() if v["passed"])
    falsification_count = sum(1 for v in falsification.values() if v["triggered"])

    schema_validated = (
        success_count == len(success) and falsification_count == 0
    )

    return {
        "success_criteria": success,
        "success_passed": success_count,
        "success_total": len(success),
        "falsification_criteria": falsification,
        "falsification_triggered": falsification_count,
        "schema_validated": schema_validated,
        "verdict": (
            "THREE-LAYER SCHEMA VALIDATED"
            if schema_validated
            else "THREE-LAYER SCHEMA: PARTIAL"
            if falsification_count == 0
            else "THREE-LAYER SCHEMA FALSIFIED"
        ),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bench/c5_verify.py <logs_dir>")
        print("  e.g. python3 bench/c5_verify.py bench/logs/c5_20260404T...")
        sys.exit(1)

    logs_dir = Path(sys.argv[1])
    if not logs_dir.exists():
        # Try as relative to REPO_ROOT
        logs_dir = REPO_ROOT / sys.argv[1]
    if not logs_dir.exists():
        print(f"ERROR: Logs directory not found: {logs_dir}")
        sys.exit(1)

    transcript_path = logs_dir / "full_transcript.txt"
    results_path = logs_dir / "results.json"

    if not transcript_path.exists():
        print(f"ERROR: No transcript found at {transcript_path}")
        sys.exit(1)

    print(f"C5 Verification: {logs_dir}")
    print("=" * 60)

    # Load experiment results
    results_json = {}
    if results_path.exists():
        results_json = json.loads(results_path.read_text())

    # Parse registry
    registry = parse_registry_ids()
    print(f"Master Finding Registry: {len(registry)} findings")

    # Extract C5 findings
    c5_findings = extract_c5_findings(transcript_path)
    print(f"C5 findings extracted: {len(c5_findings)}")

    if not c5_findings:
        print("\nWARNING: No C5-XX findings found in transcript.")
        print("The model may have used a different numbering scheme.")
        print("Manual review of the transcript is required.")

        # Try alternative extraction — look for numbered findings
        text = transcript_path.read_text()
        r8_start = text.rfind("ROUND 8")
        if r8_start >= 0:
            r8_text = text[r8_start:]
            numbered = re.findall(r'^\s*(\d+)\.\s', r8_text, re.MULTILINE)
            if numbered:
                print(f"Found {len(numbered)} numbered items in R8 "
                      f"(may need manual mapping)")

    # Cross-reference
    analysis = cross_reference(c5_findings, registry)
    print(f"\nSurviving findings: {analysis['surviving']}")
    print(f"Retracted: {analysis['retracted']}")
    print(f"Registry confirmed: {analysis['confirmed_mf_count']}/40")
    print(f"Novel findings: {analysis['novel_count']}")
    print(f"Cross-component: {analysis['cross_component_count']}")
    print(f"Findings with proofs: {analysis['findings_with_proofs']}")
    print(f"\nFix types: {json.dumps(analysis['fix_types'], indent=2)}")
    print(f"Severities: {json.dumps(analysis['severities'], indent=2)}")
    print(f"Components: {json.dumps(analysis['components'], indent=2)}")

    if analysis["unconfirmed_mf_ids"]:
        print(f"\nUnconfirmed registry findings ({analysis['unconfirmed_mf_count']}):")
        for mf_id in analysis["unconfirmed_mf_ids"]:
            print(f"  {mf_id}: {registry.get(mf_id, '?')}")

    # Evaluate criteria
    evaluation = evaluate_criteria(analysis, results_json)

    print("\n" + "=" * 60)
    print("SUCCESS CRITERIA")
    print("=" * 60)
    for name, crit in evaluation["success_criteria"].items():
        status = "PASS" if crit["passed"] else "FAIL"
        print(f"  [{status}] {name}: {crit['value']} "
              f"(threshold: {crit['threshold']})")

    print(f"\nPassed: {evaluation['success_passed']}/{evaluation['success_total']}")

    print("\n" + "=" * 60)
    print("FALSIFICATION CRITERIA")
    print("=" * 60)
    for name, crit in evaluation["falsification_criteria"].items():
        status = "TRIGGERED" if crit["triggered"] else "OK"
        print(f"  [{status}] {name}: {crit['value']} "
              f"(threshold: {crit['threshold']})")

    print(f"\nTriggered: {evaluation['falsification_triggered']}")

    print("\n" + "=" * 60)
    verdict = evaluation["verdict"]
    print(f"VERDICT: {verdict}")
    print("=" * 60)

    # Save full analysis
    full_analysis = {
        "analysis": analysis,
        "evaluation": evaluation,
        "c5_findings_count": len(c5_findings),
        "c5_finding_ids": [f["id"] for f in c5_findings],
    }
    output_path = logs_dir / "verification_analysis.json"
    output_path.write_text(json.dumps(full_analysis, indent=2) + "\n")
    print(f"\nFull analysis saved to: {output_path}")


if __name__ == "__main__":
    main()
