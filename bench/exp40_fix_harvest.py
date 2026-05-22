"""One-shot fix harvest from Exp 40 apply-back working copies.

Founder-directed 2026-05-22. Migrating the project off the apply-back-
during-review model (which created a moving target on small slices) and
back to the static-target model the project used from the outset. The
final step of the static-target migration: harvest the verified fixes
that the apply-back loop full-suite-gated across the 4 Exp 40 runs,
fold the green ones into the canonical `bench/dm/_feedback.py`, and
discard the rest with reasons logged.

Pipeline:
  1. Load every CLOSED registry entry with a `proposed_fix` field from
     the 4 Exp 40 report.json files.
  2. Parse each via the runner's `parse_search_replace_blocks` to
     extract (search, replace) pairs. (Path filtering is bypassed —
     the runner filters by basename, which would skip slice→live
     translation; we accept any block whose SEARCH content occurs
     exactly once in the live module.)
  3. Deduplicate identical (search, replace) pairs across runs.
  4. Apply cumulatively to a working copy of the live module: each
     candidate fix must (a) find its SEARCH exactly once in the current
     working source, (b) survive the focused test suite when overlaid
     in a sandbox repo copy.
  5. Write the final harvested module back to `bench/dm/_feedback.py`
     and run the full feedback-channel test surface as the final gate.

Output: a manifest of accepted / rejected fixes with reasons, and the
modified live module if all gates pass.

This tool runs once, then becomes archival. It does NOT live in the
runner.
"""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "bench"))

from bench.reference_runner_v2 import parse_search_replace_blocks  # noqa: E402


TARGET = REPO_ROOT / "bench" / "dm" / "_feedback.py"
TEST_CMD = (
    "python3 -m pytest "
    "bench/tests/test_feedback_channel.py "
    "bench/tests/test_finding_id_collision_detector.py "
    "-q --tb=line"
)


@dataclass
class Candidate:
    fingerprint: str    # hash(search + replace)
    canonical_id: str   # first cid that proposed this (for provenance)
    run: str            # run that produced it
    severity: float
    search: str
    replace: str
    origin_path: str    # the slice path the fix originally targeted


def load_candidates() -> List[Candidate]:
    cands: List[Candidate] = []
    seen: set[str] = set()
    reports = sorted(
        (REPO_ROOT / "bench" / "logs").glob("exp40_slice_*/*_report.json")
    )
    for report in reports:
        if "OUTAGE" in str(report):
            continue
        d = json.loads(report.read_text())
        run_name = report.parent.name
        for cid, entry in sorted(d.get("registry", {}).get("entries", {}).items()):
            if entry.get("status") != "CLOSED" or not entry.get("proposed_fix"):
                continue
            try:
                blocks = parse_search_replace_blocks(entry["proposed_fix"])
            except Exception as e:  # noqa: BLE001
                print(f"  WARN: {run_name}/{cid}: parse failed: {e}")
                continue
            for block in blocks:
                fp = hashlib.sha256(
                    (block.search + "\x00" + block.replace).encode("utf-8")
                ).hexdigest()[:16]
                if fp in seen:
                    continue
                seen.add(fp)
                cands.append(Candidate(
                    fingerprint=fp,
                    canonical_id=cid,
                    run=run_name,
                    severity=float(entry.get("severity", 0.0) or 0.0),
                    search=block.search,
                    replace=block.replace,
                    origin_path=block.file_path,
                ))
    return cands


def sandbox_gate(candidate_source: str) -> Tuple[bool, str]:
    """Overlay candidate_source at TARGET in a sandbox repo copy and
    run TEST_CMD. Returns (green, detail)."""
    with tempfile.TemporaryDirectory() as td:
        sb = Path(td) / "sb"
        shutil.copytree(
            REPO_ROOT, sb, symlinks=True,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".pytest_cache", "*.pyc", "logs"),
        )
        tgt = sb / TARGET.relative_to(REPO_ROOT)
        tgt.write_text(candidate_source, encoding="utf-8")
        try:
            r = subprocess.run(
                shlex.split(TEST_CMD),
                capture_output=True, text=True, cwd=str(sb), timeout=240,
                env={"PYTHONDONTWRITEBYTECODE": "1", "PATH": os.environ.get("PATH", "")},
            )
        except subprocess.TimeoutExpired:
            return False, "timeout"
        if r.returncode != 0:
            out = (r.stdout + r.stderr).strip().splitlines()
            tail = next((ln for ln in reversed(out) if "failed" in ln.lower()),
                        out[-1] if out else "")
            return False, f"suite_fail:{tail[:120]}"
    return True, "ok"


def harvest():
    print(f"=== Exp 40 fix harvest → {TARGET.relative_to(REPO_ROOT)} ===")
    cands = load_candidates()
    print(f"  loaded {len(cands)} unique (search, replace) pairs from 4 runs")
    # Sort by severity desc (high-severity attempts first)
    cands.sort(key=lambda c: -c.severity)

    live_src = TARGET.read_text(encoding="utf-8")
    working = live_src
    accepted: List[Candidate] = []
    rejected: List[Tuple[Candidate, str]] = []

    for c in cands:
        occ = working.count(c.search)
        if occ == 0:
            rejected.append((c, "search_not_found_in_live"))
            continue
        if occ > 1:
            rejected.append((c, f"search_ambiguous_{occ}_occurrences"))
            continue
        candidate = working.replace(c.search, c.replace, 1)
        if candidate == working:
            rejected.append((c, "no_change"))
            continue
        # AST parse pre-gate
        try:
            import ast
            ast.parse(candidate)
        except SyntaxError as e:
            rejected.append((c, f"ast:{e.msg}"))
            continue
        green, detail = sandbox_gate(candidate)
        if green:
            working = candidate
            accepted.append(c)
            print(f"  ✓ {c.canonical_id:6s} sev={c.severity:.2f}  "
                  f"({c.run.split('_')[2][:7]}…)  +{len(c.replace)-len(c.search):+5d} chars")
        else:
            rejected.append((c, detail))

    print("\n=== summary ===")
    print(f"  accepted: {len(accepted)}")
    print(f"  rejected: {len(rejected)}")
    by_reason: dict[str, int] = {}
    for _, reason in rejected:
        key = reason.split(":")[0]
        by_reason[key] = by_reason.get(key, 0) + 1
    for k, v in sorted(by_reason.items(), key=lambda x: -x[1]):
        print(f"    {k}: {v}")

    if accepted:
        # Final full-surface verification before writing
        print("\n=== final full-surface verification of harvested module ===")
        green, detail = sandbox_gate(working)
        if not green:
            print(f"  ✗ final sandbox gate FAILED: {detail}")
            print("  NOT writing to live module")
            return 1
        print("  ✓ final sandbox gate PASS")
        TARGET.write_text(working, encoding="utf-8")
        delta = len(working) - len(live_src)
        print(f"  ✓ wrote {len(accepted)} harvested fixes to "
              f"{TARGET.relative_to(REPO_ROOT)} (delta {delta:+d} chars)")
    else:
        print("\n=== no fixes accepted; live module unchanged ===")
    return 0


if __name__ == "__main__":
    sys.exit(harvest())
