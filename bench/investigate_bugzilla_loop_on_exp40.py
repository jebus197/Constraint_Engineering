#!/usr/bin/env python3
"""Investigation: how does the Bugzilla CLOSED-loop perform on Exp 40's
actual findings?

This is the empirical test the founder asked for before integrating the
close-the-loop into the runner. It runs each step of the pipeline on
every finding in the Exp 40 report and reports where things succeed or
fail. The script does NOT mutate any registry.

Output: per-step counts (parseable, sandbox-appliable, verifiable) plus
representative samples of failure modes.

Usage:
    python3 bench/investigate_bugzilla_loop_on_exp40.py
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

import bugzilla_loop


REPORT_PATH = (
    REPO_ROOT / "bench" / "logs" / "exp40_gate_20260514T020550Z"
    / "exp40_gate_report.json"
)
TARGET_PATH = REPO_ROOT / "bench" / "dm" / "_feedback.py"
TEST_CMD = "python3 -m pytest bench/tests/test_feedback_channel.py -q --tb=line"


def collect_findings_from_round_files(log_dir: Path) -> list[dict]:
    """Flatten findings from the per-round JSON files in the experiment
    log dir. The top-level report's findings schema drops `proposed_fix`;
    the per-round files carry the full schema."""
    findings: list[dict] = []
    for round_file in sorted(log_dir.glob("round_[0-9][0-9].json")):
        d = json.loads(round_file.read_text())
        for f in d.get("findings", []):
            findings.append(f)
    return findings


def main() -> int:
    if not REPORT_PATH.exists():
        print(f"ERROR: report not found at {REPORT_PATH}")
        return 1
    if not TARGET_PATH.exists():
        print(f"ERROR: target not found at {TARGET_PATH}")
        return 1

    log_dir = REPORT_PATH.parent
    findings = collect_findings_from_round_files(log_dir)
    print(f"Loaded {len(findings)} findings from "
          f"per-round files in {log_dir.name}/")
    print(f"Target: {TARGET_PATH.relative_to(REPO_ROOT)}")
    print(f"Test cmd: {TEST_CMD}")
    print()

    # Stage 1: how many findings carry a non-empty proposed_fix?
    with_fix = [f for f in findings if (f.get("proposed_fix") or "").strip()]
    print(f"Stage 1 — non-empty proposed_fix: {len(with_fix)}/{len(findings)}")

    if not with_fix:
        print("\nNo findings with proposed_fix text. Aborting investigation.")
        return 0

    # Stage 2: how many parse to a SEARCH/REPLACE block?
    parseable = []
    parse_failure_reasons: Counter[str] = Counter()
    for f in with_fix:
        r = bugzilla_loop.extract_search_replace(f["proposed_fix"])
        if r.success:
            parseable.append((f, r))
        else:
            parse_failure_reasons[r.reason] += 1
    print(
        f"Stage 2 — parseable as SEARCH/REPLACE block: "
        f"{len(parseable)}/{len(with_fix)}"
    )
    if parse_failure_reasons:
        print("  Parse-failure reasons (top 5):")
        for reason, n in parse_failure_reasons.most_common(5):
            print(f"    {n:4d} × {reason[:80]}")
    print()

    if not parseable:
        print("No findings parse to a SEARCH/REPLACE block. "
              "This is the bottleneck: the panel's proposed_fix format "
              "is not consistent with the runner's parser expectations.")
        print()
        print("Sample of non-parseable proposed_fix text:")
        for f in with_fix[:3]:
            pf = f["proposed_fix"]
            print(f"  finding_id={f.get('finding_id')!r}")
            print(f"  first 300 chars: {pf[:300]!r}")
            print()
        return 0

    # Stage 3: how many can be applied to the target sandbox?
    appliable = []
    apply_failure_reasons: Counter[str] = Counter()
    for f, extract in parseable:
        sb, reason = bugzilla_loop.apply_fix_to_sandbox(
            TARGET_PATH, extract.old_code, extract.new_code
        )
        if sb is not None:
            appliable.append((f, extract, sb))
        else:
            apply_failure_reasons[reason] += 1
    print(
        f"Stage 3 — sandbox-appliable (exactly-once match): "
        f"{len(appliable)}/{len(parseable)}"
    )
    if apply_failure_reasons:
        print("  Apply-failure reasons (top 5):")
        for reason, n in apply_failure_reasons.most_common(5):
            print(f"    {n:4d} × {reason[:80]}")
    print()

    # Clean up any sandbox files we won't be verifying (only verify top N)
    VERIFY_LIMIT = 5
    to_verify = appliable[:VERIFY_LIMIT]
    for _, _, sb in appliable[VERIFY_LIMIT:]:
        try:
            sb.unlink(missing_ok=True)
        except OSError:
            pass

    if not appliable:
        print("No findings can be applied to the sandbox. "
              "This is the bottleneck: parseable fixes are not matching "
              "the target file content exactly.")
        return 0

    # Stage 4: of the applied sandboxes, how many pass verification?
    # Cap verification at the first few because each verification run
    # can take 30-60 seconds.
    print(f"Stage 4 — running verification on first {len(to_verify)} "
          f"appliable findings (each run is 30-60s)...")
    print()

    verified = 0
    for f, extract, sandbox in to_verify:
        verify = bugzilla_loop.run_verification(sandbox, TEST_CMD)
        print(f"  {f.get('finding_id'):30s}  passed={verify.passed}  "
              f"elapsed={verify.elapsed_s:.1f}s")
        if not verify.passed:
            print(f"    failures: {'; '.join(verify.failures)[:200]}")
        if verify.passed:
            verified += 1
        try:
            sandbox.unlink(missing_ok=True)
        except OSError:
            pass

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  Total findings: {len(findings)}")
    print(f"  With proposed_fix: {len(with_fix)}")
    print(f"  Parseable: {len(parseable)} "
          f"({100*len(parseable)/len(with_fix):.0f}% of fixed)")
    print(f"  Sandbox-appliable: {len(appliable)} "
          f"({100*len(appliable)/len(parseable):.0f}% of parseable)" if parseable else "")
    print(f"  Verified (of {len(to_verify)} sampled): {verified} "
          f"({100*verified/len(to_verify):.0f}% of sampled)" if to_verify else "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
