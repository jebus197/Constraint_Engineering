#!/usr/bin/env python3
"""Reprocessor for Experiment 33 raw model responses.

Re-parses all raw response JSON files using the current (fixed) parser
pipeline, rebuilds the FindingRegistry and verdict ledger from scratch,
and reports whether the corrected parsing changes the outcome.

Runnable standalone:
    python3 bench/reprocess_exp33.py

Produces:
  - stdout summary
  - bench/logs/exp33_endocrine_20260405T110345Z/reprocessed_report.json
"""

from __future__ import annotations

import json
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ── Path setup ───────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from runner_core import parse_findings
from dynamic_management import Finding

# ── Configuration ────────────────────────────────────────────────────────

LOGS_DIR = (
    REPO_ROOT / "bench" / "logs" / "exp33_endocrine_20260405T110345Z"
)

# Convergence parameters (mirror run_exp33_endocrine.py)
EARLIEST_STOP_ROUND = 12
CONSECUTIVE_ROUNDS_REQUIRED = 2
MAX_NOVEL_FINDINGS = 2
MIN_ROUNDS_FOR_GAMMA = 3

# Verdict regex (identical to run_exp33_endocrine.py)
_VERDICT_RE = re.compile(
    r'^(CONFIRM|CHALLENGE|EXTEND|MERGE)\s+(C\d{4})(?:\s*[\|<\-]+\s*(.*))?$',
    re.MULTILINE,
)


# ── Minimal FindingRegistry ─────────────────────────────────────────────

class FindingRegistry:
    """Minimal reimplementation matching run_exp33_endocrine.FindingRegistry."""

    def __init__(self):
        self.entries: Dict[str, Dict[str, Any]] = {}
        self._next_id = 1
        self._alias_map: Dict[str, str] = {}

    def register(self, finding: Finding, model_id: str) -> str:
        canonical_id = f"C{self._next_id:04d}"
        self._next_id += 1
        self._alias_map[finding.finding_id] = canonical_id
        self.entries[canonical_id] = {
            "canonical_id": canonical_id,
            "source_model": model_id,
            "source_aliases": [finding.finding_id],
            "severity": finding.severity,
            "description": finding.description[:500],
            "proposed_fix": (
                finding.proposed_fix[:500] if finding.proposed_fix else ""
            ),
            "status": "OPEN",
            "open_since_round": getattr(finding, "round_idx", 0),
            "last_status_change_round": getattr(finding, "round_idx", 0),
            "verdicts": [],
            "verified": finding.verified,
            "escalated": getattr(finding, "escalated", False),
            "flaw_class": getattr(finding, "flaw_class", 0),
        }
        return canonical_id

    def add_verdict(
        self,
        canonical_id: str,
        model_id: str,
        verdict: str,
        round_idx: int,
        evidence: str = "",
    ):
        if canonical_id not in self.entries:
            return
        self.entries[canonical_id]["verdicts"].append({
            "model": model_id,
            "verdict": verdict,
            "round": round_idx,
            "evidence": evidence[:200],
        })
        self.entries[canonical_id]["last_status_change_round"] = round_idx

    def lookup_alias(self, model_local_id: str) -> Optional[str]:
        return self._alias_map.get(model_local_id)

    def open_crit_high_count(self) -> int:
        """Open findings with severity >= 0.7 (matches original runner)."""
        return sum(
            1 for e in self.entries.values()
            if e["status"] == "OPEN" and e["severity"] >= 0.7
        )

    def contested_count(self, current_round: int) -> int:
        count = 0
        for e in self.entries.values():
            if e["status"] != "OPEN":
                continue
            challenges = [
                v for v in e["verdicts"] if v["verdict"] == "CHALLENGE"
            ]
            confirms = [
                v for v in e["verdicts"] if v["verdict"] == "CONFIRM"
            ]
            if challenges and not confirms:
                oldest_challenge = min(v["round"] for v in challenges)
                if current_round - oldest_challenge > 1:
                    count += 1
        return count

    def status_counts(self) -> Dict[str, int]:
        counts: Dict[str, int] = defaultdict(int)
        for e in self.entries.values():
            counts[e["status"]] += 1
        return dict(counts)


# ── Gamma estimation (Duane model) ──────────────────────────────────────

def _estimate_gamma(per_round_counts: List[int]) -> float:
    """Simple Duane gamma from per-round finding counts."""
    n = len(per_round_counts)
    if n < MIN_ROUNDS_FOR_GAMMA:
        return 0.0
    cumulative = []
    total = 0
    for c in per_round_counts:
        total += c
        cumulative.append(total)
    if cumulative[0] <= 0 or cumulative[-1] <= cumulative[0]:
        return 0.0 if cumulative[-1] == 0 else 1.0
    try:
        beta = (
            (math.log(cumulative[-1]) - math.log(cumulative[0]))
            / math.log(n)
        )
        return 1.0 - beta
    except (ValueError, ZeroDivisionError):
        return 0.0


def _gamma_trajectory(per_round_counts: List[int]) -> List[float]:
    """Compute gamma at each round from 0..N-1."""
    trajectory = []
    for i in range(len(per_round_counts)):
        trajectory.append(_estimate_gamma(per_round_counts[: i + 1]))
    return trajectory


# ── Convergence check ───────────────────────────────────────────────────

def _check_convergence(
    round_idx: int,
    registry: FindingRegistry,
    novel_counts: List[int],
) -> Tuple[bool, str]:
    """State-based convergence gate (no gamma gate in reprocessor —
    gamma is telemetry-only until R15, and the original never converged)."""
    if round_idx < EARLIEST_STOP_ROUND:
        return False, f"Too early (round {round_idx} < {EARLIEST_STOP_ROUND})"

    if len(novel_counts) < CONSECUTIVE_ROUNDS_REQUIRED:
        return False, "Insufficient rounds for consecutive check"

    recent_novel = novel_counts[-CONSECUTIVE_ROUNDS_REQUIRED:]

    # Condition: zero open CRIT/HIGH (severity >= 0.7)
    open_ch = registry.open_crit_high_count()
    if open_ch > 0:
        return False, f"Open CRIT/HIGH: {open_ch}"

    # Condition: novel findings <= threshold for consecutive rounds
    if any(n > MAX_NOVEL_FINDINGS for n in recent_novel):
        return False, (
            f"Novel findings too high: {recent_novel} "
            f"(need <= {MAX_NOVEL_FINDINGS} for "
            f"{CONSECUTIVE_ROUNDS_REQUIRED} rounds)"
        )

    # Condition: no contested findings for >1 round
    contested = registry.contested_count(round_idx)
    if contested > 0:
        return False, f"Contested findings: {contested}"

    return True, (
        f"STATE_CONVERGED at round {round_idx}: "
        f"novel={recent_novel}, open_ch={open_ch}"
    )


# ── File discovery ──────────────────────────────────────────────────────

def discover_response_files() -> Dict[int, List[Path]]:
    """Find all r<N>_<model>_<ts>.json files, grouped by round."""
    pattern = re.compile(r'^r(\d+)_(?!ound)([a-zA-Z0-9]+)_\d{8}T\d{6}Z\.json$')
    grouped: Dict[int, List[Path]] = defaultdict(list)
    for p in sorted(LOGS_DIR.iterdir()):
        m = pattern.match(p.name)
        if m:
            round_num = int(m.group(1))
            grouped[round_num].append(p)
    return dict(grouped)


# ── Parse verdicts ──────────────────────────────────────────────────────

def parse_verdicts(
    response_text: str,
) -> List[Tuple[str, str, str]]:
    """Extract (verdict_type, canonical_id, evidence) from response."""
    results = []
    for m in _VERDICT_RE.finditer(response_text):
        results.append((m.group(1), m.group(2), (m.group(3) or "").strip()))
    return results


# ── Main reprocessor ────────────────────────────────────────────────────

def reprocess() -> Dict[str, Any]:
    files_by_round = discover_response_files()
    if not files_by_round:
        print(f"ERROR: No response files found in {LOGS_DIR}")
        sys.exit(1)

    rounds_sorted = sorted(files_by_round.keys())
    print(f"Discovered {sum(len(v) for v in files_by_round.values())} "
          f"response files across {len(rounds_sorted)} rounds "
          f"(R{rounds_sorted[0]}–R{rounds_sorted[-1]})")
    print()

    registry = FindingRegistry()

    # Accumulators
    per_round_novel: List[int] = []
    per_round_total: List[int] = []
    per_round_stats: List[Dict[str, Any]] = []
    model_finding_totals: Dict[str, int] = defaultdict(int)
    model_verdict_totals: Dict[str, Dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    global_verdict_totals: Dict[str, int] = defaultdict(int)
    all_findings_flat: List[Finding] = []

    for round_idx in rounds_sorted:
        round_files = files_by_round[round_idx]
        round_findings: List[Finding] = []
        round_verdicts: List[Tuple[str, str, str, str]] = []  # (type, cid, ev, model)
        round_per_model: Dict[str, int] = {}
        round_verdict_per_model: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for fpath in round_files:
            with open(fpath, "r") as f:
                data = json.load(f)

            model_label = data.get("model_label", "unknown")
            response_text = data.get("response", "")

            # Parse findings
            findings = parse_findings(model_label, round_idx, response_text)
            round_per_model[model_label] = len(findings)
            model_finding_totals[model_label] += len(findings)
            round_findings.extend(findings)
            all_findings_flat.extend(findings)

            # Register findings
            for finding in findings:
                registry.register(finding, model_label)

            # Parse verdicts
            verdicts = parse_verdicts(response_text)
            for vtype, cid, evidence in verdicts:
                registry.add_verdict(cid, model_label, vtype, round_idx, evidence)
                round_verdicts.append((vtype, cid, evidence, model_label))
                round_verdict_per_model[model_label][vtype] += 1
                model_verdict_totals[model_label][vtype] += 1
                global_verdict_totals[vtype] += 1

        novel_this_round = len(round_findings)
        per_round_novel.append(novel_this_round)
        per_round_total.append(len(registry.entries))

        # Convergence check for this round
        converged, reason = _check_convergence(
            round_idx, registry, per_round_novel,
        )

        round_stat = {
            "round": round_idx,
            "novel_findings": novel_this_round,
            "registry_total": len(registry.entries),
            "per_model_findings": dict(round_per_model),
            "verdicts_this_round": {
                k: sum(d[k] for d in round_verdict_per_model.values())
                for k in set().union(
                    *(d.keys() for d in round_verdict_per_model.values())
                )
            } if round_verdict_per_model else {},
            "verdict_per_model": {
                m: dict(d) for m, d in round_verdict_per_model.items()
            },
            "open_crit_high": registry.open_crit_high_count(),
            "contested": registry.contested_count(round_idx),
            "convergence_check": converged,
            "convergence_reason": reason,
        }
        per_round_stats.append(round_stat)

    # ── Post-processing ──────────────────────────────────────────────
    gamma_trajectory = _gamma_trajectory(per_round_novel)
    final_gamma = gamma_trajectory[-1] if gamma_trajectory else 0.0

    # Convergence assessment
    convergence_achieved = False
    convergence_round = None
    convergence_reason = "Never converged"
    for stat in per_round_stats:
        if stat["convergence_check"]:
            convergence_achieved = True
            convergence_round = stat["round"]
            convergence_reason = stat["convergence_reason"]
            break

    # If not converged, report why at final round
    if not convergence_achieved and per_round_stats:
        last = per_round_stats[-1]
        convergence_reason = (
            f"Did not converge. Final round ({last['round']}): "
            f"{last['convergence_reason']}"
        )

    # Registry final state
    status_counts = registry.status_counts()

    # Build report
    report = {
        "reprocessor_version": "1.0",
        "source_dir": str(LOGS_DIR),
        "total_rounds": len(rounds_sorted),
        "total_response_files": sum(
            len(v) for v in files_by_round.values()
        ),
        "total_findings_reprocessed": len(registry.entries),
        "original_total_findings": 84,
        "delta_findings": len(registry.entries) - 84,
        "per_model_totals": dict(model_finding_totals),
        "original_per_model": {
            "ChatGPT": 16, "Codex": 18, "CC2": 11,
            "Gemini": 3, "DeepSeek": 36,
        },
        "per_model_delta": {
            model: model_finding_totals.get(model, 0) - orig
            for model, orig in {
                "ChatGPT": 16, "Codex": 18, "CC2": 11,
                "Gemini": 3, "DeepSeek": 36,
            }.items()
        },
        "verdict_totals": dict(global_verdict_totals),
        "verdict_per_model": {
            m: dict(d) for m, d in model_verdict_totals.items()
        },
        "gamma_final": round(final_gamma, 4),
        "gamma_trajectory": [round(g, 4) for g in gamma_trajectory],
        "per_round_novel_counts": per_round_novel,
        "convergence_assessment": {
            "converged": convergence_achieved,
            "convergence_round": convergence_round,
            "reason": convergence_reason,
        },
        "registry_final_state": status_counts,
        "per_round_detail": per_round_stats,
    }

    return report


def print_report(report: Dict[str, Any]) -> None:
    """Print human-readable summary to stdout."""
    print("=" * 72)
    print("  EXPERIMENT 33 — REPROCESSED RESULTS")
    print("=" * 72)
    print()

    print(f"Rounds processed:      {report['total_rounds']}")
    print(f"Response files:        {report['total_response_files']}")
    print()

    # Findings comparison
    print("─── FINDINGS ───────────────────────────────────────────────")
    print(f"Total findings (reprocessed): {report['total_findings_reprocessed']}")
    print(f"Total findings (original):    {report['original_total_findings']}")
    delta = report['delta_findings']
    sign = "+" if delta > 0 else ""
    print(f"Delta:                        {sign}{delta}")
    print()

    print("Per-model breakdown:")
    print(f"  {'Model':<12} {'Reprocessed':>12} {'Original':>10} {'Delta':>8}")
    print(f"  {'-'*12} {'-'*12} {'-'*10} {'-'*8}")
    for model in ["CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini"]:
        rp = report["per_model_totals"].get(model, 0)
        orig = report["original_per_model"].get(model, 0)
        d = rp - orig
        ds = f"+{d}" if d > 0 else str(d)
        print(f"  {model:<12} {rp:>12} {orig:>10} {ds:>8}")
    print()

    # Verdicts
    print("─── VERDICTS ───────────────────────────────────────────────")
    vt = report["verdict_totals"]
    for vtype in ["CONFIRM", "CHALLENGE", "EXTEND", "MERGE"]:
        print(f"  {vtype:<12}: {vt.get(vtype, 0)}")
    print()

    print("  Verdicts per model:")
    vpm = report["verdict_per_model"]
    all_vtypes = sorted(
        set().union(*(d.keys() for d in vpm.values())) if vpm else []
    )
    header = f"    {'Model':<12}" + "".join(f"{v:>12}" for v in all_vtypes)
    print(header)
    print(f"    {'-'*12}" + "".join(f"{'-'*12}" for _ in all_vtypes))
    for model in ["CC2", "ChatGPT", "Codex", "DeepSeek", "Gemini"]:
        if model in vpm:
            row = f"    {model:<12}"
            for v in all_vtypes:
                row += f"{vpm[model].get(v, 0):>12}"
            print(row)
    print()

    # Gamma
    print("─── GAMMA TRAJECTORY ───────────────────────────────────────")
    traj = report["gamma_trajectory"]
    for i, g in enumerate(traj):
        marker = ""
        if 0.45 <= g:
            marker = " (strong depletion)"
        elif 0.30 <= g < 0.45:
            marker = " (moderate depletion)"
        elif 0.20 <= g < 0.30:
            marker = " (weak depletion)"
        elif g > 0 and g < 0.20:
            marker = " (disagrees with convergence)"
        print(f"  R{i:>2}: gamma = {g:.4f}{marker}")
    print(f"\n  Final gamma: {report['gamma_final']:.4f}")
    print()

    # Per-round novel counts
    print("─── PER-ROUND NOVEL FINDINGS ───────────────────────────────")
    for i, c in enumerate(report["per_round_novel_counts"]):
        bar = "#" * c
        print(f"  R{i:>2}: {c:>3}  {bar}")
    print()

    # Convergence
    print("─── CONVERGENCE ASSESSMENT ─────────────────────────────────")
    ca = report["convergence_assessment"]
    if ca["converged"]:
        print(f"  CONVERGED at round {ca['convergence_round']}")
    else:
        print(f"  DID NOT CONVERGE")
    print(f"  Reason: {ca['reason']}")
    print()

    # Registry final state
    print("─── REGISTRY FINAL STATE ───────────────────────────────────")
    for status, count in sorted(report["registry_final_state"].items()):
        print(f"  {status:<16}: {count}")
    print()

    print("=" * 72)


def main():
    report = reprocess()

    print_report(report)

    # Save JSON report
    out_path = LOGS_DIR / "reprocessed_report.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Report saved to: {out_path}")


if __name__ == "__main__":
    main()
