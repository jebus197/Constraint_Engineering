#!/usr/bin/env python3
"""Generate a simulated panel's findings using AGENTS in place of the paid models.

    PANEL LABELS ARE `SIM-A`..`SIM-F` AND MUST STAY THAT WAY. They stand in for
    the six models — CC2, DeepSeek, ChatGPT, Gemini, Codex and Fable — but they
    are NOT those models. Labelling a simulated agent with a vendor name on
    2026-08-04 put two indistinguishable panels into the record, one real and one
    simulated, and results were reported as though vendors had produced them.
    That is a provenance failure, not a naming choice.

WHY THIS EXISTS
===============
Founder, 2026-08-30: *"The purpose of these simulated runs is to use agents in
place of our (now) 6 models in real experimental runs to both test all recent
fixes as they unfold and to not risk burning real money, only to discover in the
actual runs that things aren't working as specified. The remaining runway remains
short."*

`bench/tools/simulated_bench.py` has always accepted `--findings <json>`, and no
such file had ever been generated — checked 2026-08-30, the agent mode had never
once been run. This produces that file.

WHAT IT IS AND IS NOT
=====================
IS:     six independent agents, each given the real target and the real briefing,
        each returning findings in the schema the bench consumes. Their falsifiers
        are then run by the RUNNER, not trusted from the agent's claim — which is
        the honesty check `simulated_bench.py` already performs when `_ran` is set.

IS NOT: an experiment. A simulated panel's findings differ in character from six
        frontier models under the full directive. Nothing here is an experimental
        result and none of it belongs in the paper.

COST: none. These are Claude subagents on the founder's plan.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import pathlib
import re
import subprocess
import sys
import time

REPO = pathlib.Path(__file__).resolve().parents[2]
for p in (str(REPO), str(REPO / "bench")):
    if p not in sys.path:
        sys.path.insert(0, p)

#: Six stand-ins for six models. Named by letter, never by vendor.
SIM_AGENTS = ["SIM-A", "SIM-B", "SIM-C", "SIM-D", "SIM-E", "SIM-F"]

BRIEF = """You are reviewing one technical document for defects. Return ONLY JSON.

TARGET (read it first): {target}

Find claims in the document that are WRONG — arithmetic that does not check out,
a complexity claim contradicted by the code listing, a conclusion that does not
follow from its premise. Verify with tools: read the file, run python, compute.
Do not guess.

Return a JSON array. Each element:
  {{
    "finding_id":    "F001",              // yours, unique
    "severity":      0.85,                 // 0..1, >=0.7 means critical
    "description":   "one sentence naming the claim and why it is wrong",
    "falsifier_code": "python that RAISES AssertionError iff the defect is present",
    "proposed_fix":  "<<<< SEARCH\\n<exact text from the document>\\n==== REPLACE\\n<corrected text>\\n>>>>",
    "_ran":          true                  // true ONLY if you actually executed the falsifier
  }}

The falsifier MUST read the document by its ABSOLUTE path, {target}, and must
raise AssertionError with a message starting "FALSIFIED:" when the defect is
present. Keep it under 15 lines.

CROSS-REFERENCES ARE REQUIRED, not optional. Five reviewers are looking at this
document at the same time, and the most likely defect is the one in AL-03. So:

  * Your FIRST finding must begin its description with exactly:
        CONFIRM C0001 | <why you agree the first registered finding is right>
    unless you genuinely believe C0001 is wrong, in which case use CHALLENGE.
  * If you can name a consequence the first finding does NOT mention, add a
    SECOND finding whose description begins with exactly:
        EXTEND C0001 | <the consequence>

The archive holds 5282 CONFIRM and 209 EXTEND cross-references, so a panel that
emits none is not a realistic panel.

Return between 1 and 3 findings. JSON only, no prose, no markdown fence."""


def _one_agent(label: str, target: str, timeout: int) -> list:
    """Dispatch one agent; return its findings with the label stamped on."""
    prompt = BRIEF.format(target=target)
    t0 = time.monotonic()
    try:
        r = subprocess.run(
            ["claude", "-p", prompt, "--model", "sonnet", "--output-format", "text",
             "--no-session-persistence",
        "--setting-sources", "",  # panellists read the directive, not the operator config
             "--allowedTools", "Bash", "Read", "Grep", "Glob"],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(REPO), stdin=subprocess.DEVNULL,
        )
    except subprocess.TimeoutExpired:
        print(f"  [{label}] TIMEOUT after {timeout}s", flush=True)
        return []
    el = time.monotonic() - t0
    if r.returncode != 0:
        print(f"  [{label}] rc={r.returncode}: {r.stderr.strip()[:160]}", flush=True)
        return []
    txt = (r.stdout or "").strip()
    m = re.search(r"\[.*\]", txt, re.S)
    if not m:
        print(f"  [{label}] no JSON array in {len(txt)} chars", flush=True)
        return []
    try:
        rows = json.loads(m.group(0))
    except ValueError as e:
        print(f"  [{label}] JSON parse failed: {e}", flush=True)
        return []
    out = []
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict) or not row.get("description"):
            continue
        row["model_id"] = label                      # stamped HERE, never self-reported
        row["finding_id"] = f"{label}-{i:03d}"
        row.setdefault("round_idx", 0)
        row.setdefault("flaw_class", 3)
        row["severity"] = float(row.get("severity", 0.7))
        out.append(row)
    print(f"  [{label}] {len(out)} finding(s) in {el:.0f}s", flush=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", default="bench/tests/fixtures/stem/docs/ALG-02-REF-01.md")
    ap.add_argument("--out", default="bench/logs/sim_panel_findings.json")
    ap.add_argument("--agents", type=int, default=6)
    ap.add_argument("--timeout", type=int, default=420)
    args = ap.parse_args()

    target = str(REPO / args.target)
    if not pathlib.Path(target).is_file():
        print(f"target not found: {target}", file=sys.stderr)
        return 2
    labels = SIM_AGENTS[:args.agents]
    print(f"=== simulated panel: {len(labels)} agents on {args.target} ===", flush=True)
    print(f"    labels {labels} — stand-ins for six models, never named as them", flush=True)

    rows: list = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(labels)) as pool:
        for got in pool.map(lambda l: _one_agent(l, target, args.timeout), labels):
            rows.extend(got)

    dest = REPO / args.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    ran = sum(1 for r in rows if r.get("_ran"))
    print(f"\n  {len(rows)} findings from {len({r['model_id'] for r in rows})} agents; "
          f"{ran} claim their falsifier RAN")
    print(f"  written: {dest}")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())
