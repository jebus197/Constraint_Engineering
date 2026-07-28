#!/usr/bin/env python3
"""Exp 39 monitoring script.

Polls the experiment log directory every 60 seconds and reports:
- Current round
- Findings count
- Model health
- Convergence metrics (gamma, rho)
- Any anomalies

Usage:
    python3 bench/monitor_exp39.py [--interval 60] [--logs-dir <path>]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOGS = REPO_ROOT / "bench" / "logs"


def find_latest_exp39_dir(logs_dir: Path) -> Path | None:
    """Find the most recent exp39 log directory."""
    candidates = sorted(
        logs_dir.glob("exp39_0_gate_*"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def read_report(exp_dir: Path) -> dict | None:
    """Read the partial or final report JSON."""
    for name in ["exp39_0_gate_report.json", "runner_state.json"]:
        report_path = exp_dir / name
        if report_path.exists():
            try:
                return json.loads(report_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
    return None


def read_round_files(exp_dir: Path) -> list[dict]:
    """Read per-round JSON files."""
    rounds = []
    for rpath in sorted(exp_dir.glob("round_*.json")):
        try:
            data = json.loads(rpath.read_text(encoding="utf-8"))
            rounds.append(data)
        except (json.JSONDecodeError, OSError):
            pass
    return rounds


def check_anomalies(rounds: list[dict]) -> list[str]:
    """Check for anomalous patterns."""
    anomalies = []
    if not rounds:
        return anomalies

    latest = rounds[-1]

    # Check if any model failed to respond
    models_responded = latest.get("models_responded", [])
    expected = ["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"]
    missing = [m for m in expected if m not in models_responded]
    if missing:
        anomalies.append(f"MISSING MODELS: {', '.join(missing)}")

    # Check for zero findings
    if latest.get("findings_count", 0) == 0:
        anomalies.append("ZERO FINDINGS this round")

    # Check for rho spike (novelty resurgence)
    rho = latest.get("rho", 0)
    if len(rounds) >= 3 and rho > 0.8:
        prev_rho = rounds[-2].get("rho", 0)
        if rho - prev_rho > 0.4:
            anomalies.append(f"RHO SPIKE: {prev_rho:.3f} -> {rho:.3f}")

    # Check for gamma regression
    if len(rounds) >= 2:
        prev_gamma = rounds[-2].get("gamma", 0)
        curr_gamma = latest.get("gamma", 0)
        if curr_gamma < prev_gamma - 0.05:
            anomalies.append(f"GAMMA REGRESSION: {prev_gamma:.3f} -> {curr_gamma:.3f}")

    # Check for very long round
    elapsed = latest.get("elapsed_s", 0)
    if elapsed > 600:
        anomalies.append(f"SLOW ROUND: {elapsed:.0f}s (>10min)")

    return anomalies


def monitor_cycle(exp_dir: Path) -> dict:
    """Run one monitoring cycle."""
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "exp_dir": str(exp_dir),
    }

    rounds = read_round_files(exp_dir)
    result["rounds_completed"] = len(rounds)

    if rounds:
        latest = rounds[-1]
        result["current_round"] = latest.get("round", "?")
        result["findings_this_round"] = latest.get("findings_count", 0)
        result["novel_this_round"] = latest.get("novel_this_round", 0)
        result["gamma"] = latest.get("gamma", 0)
        result["rho"] = latest.get("rho", 0)
        result["rho_avg"] = latest.get("rho_avg", 0)
        result["models"] = latest.get("models_responded", [])
        result["elapsed_s"] = latest.get("elapsed_s", 0)
        result["open_crit_high"] = latest.get("open_crit_high", 0)
    else:
        result["current_round"] = "waiting"

    report = read_report(exp_dir)
    if report:
        result["registry_total"] = len(report.get("registry", {}).get("entries", {}))
        if "converged_at" in report:
            result["converged_at"] = report["converged_at"]
            result["convergence_reason"] = report.get("convergence_reason", "?")

    result["anomalies"] = check_anomalies(rounds)
    return result


def print_status(status: dict) -> None:
    """Print a human-readable status line."""
    ts = status["timestamp"][:19]
    rnd = status.get("current_round", "?")
    findings = status.get("findings_this_round", "?")
    novel = status.get("novel_this_round", "?")
    gamma = status.get("gamma", 0)
    rho = status.get("rho", 0)
    rho_avg = status.get("rho_avg", 0)
    models = status.get("models", [])
    elapsed = status.get("elapsed_s", 0)
    reg_total = status.get("registry_total", "?")
    och = status.get("open_crit_high", 0)

    print(f"\n[{ts}] Round {rnd} | "
          f"F={findings} N={novel} | "
          f"gamma={gamma:.3f} rho={rho:.3f} rho_avg={rho_avg:.3f} | "
          f"OCH={och} Reg={reg_total} | "
          f"{len(models)} models | {elapsed:.0f}s", flush=True)

    if "converged_at" in status:
        print(f"  *** CONVERGED at round {status['converged_at']}: "
              f"{status.get('convergence_reason', '?')} ***", flush=True)

    anomalies = status.get("anomalies", [])
    if anomalies:
        for a in anomalies:
            print(f"  *** ANOMALY: {a} ***", flush=True)


def main():
    parser = argparse.ArgumentParser(description="Monitor Exp 39 execution")
    parser.add_argument("--interval", type=int, default=60,
                        help="Poll interval in seconds (default: 60)")
    parser.add_argument("--logs-dir", type=str, default=str(DEFAULT_LOGS),
                        help="Logs directory")
    parser.add_argument("--once", action="store_true",
                        help="Run one cycle and exit")
    args = parser.parse_args()

    logs_dir = Path(args.logs_dir)
    print(f"Monitoring Exp 39 in {logs_dir}...", flush=True)

    while True:
        exp_dir = find_latest_exp39_dir(logs_dir)
        if exp_dir:
            status = monitor_cycle(exp_dir)
            print_status(status)

            if "converged_at" in status:
                print("\nExperiment complete. Exiting monitor.", flush=True)
                break
        else:
            print(f"[{datetime.now(timezone.utc).isoformat()[:19]}] "
                  f"Waiting for exp39 logs...", flush=True)

        if args.once:
            break

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
