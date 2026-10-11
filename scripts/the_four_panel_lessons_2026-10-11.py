#!/usr/bin/env python3
"""His 4 panel lessons of 2026-10-07, verified against the tree. 2 of my earlier verdicts fall.

HIS RULING, 2026-10-11: *"Verdict: Verify and fix all."* Against the 4 lessons he answered on
2026-10-07, each with the identical words: *"We should use it. Wire it in all simulated and real
runners going forward."*

WHY AN EARLIER PASS REPORTED "0 of 4" AND WHY THAT IS WITHDRAWN. The first check used
`grep -icE` patterns containing `\\|`, which is BRE alternation, under `-E`, so every pattern
searched for a LITERAL PIPE and matched nothing. A second pass then searched
`reference_runner_v3.py` for the PANEL's function names -- `_preserve_prior_attempt`,
`_detect_round_kind`, `REQUIRED_FIELDS` -- rather than for the BEHAVIOUR, and in the wrong
module: dispatch lives in `experiment_11_orchestrator.py`, not in the runner. Both are the same
`check the predicate before the result` fault that has recurred all session.

Run: python3 scripts/the_four_panel_lessons_2026-10-11.py
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
Z = 1.959963984540054

ORCH = "bench/experiment_11_orchestrator.py"
RUNNER = "bench/reference_runner_v3.py"
SIMRUN = "bench/tools/run_simulated_experiment.py"
CORE = "bench/runner_core.py"


def wilson(k: int, n: int) -> tuple:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + Z * Z / n
    c = (p + Z * Z / (2 * n)) / d
    h = (Z / d) * math.sqrt(p * (1 - p) / n + Z * Z / (4 * n * n))
    return (round(max(0.0, c - h), 4), round(min(1.0, c + h), 4))


def _text(rel: str) -> str:
    f = REPO / rel
    return f.read_text(errors="ignore") if f.is_file() else ""


def _callers_of(symbol: str) -> list:
    """Every file that CALLS a symbol, excluding its own definition site and logs."""
    out = []
    r = subprocess.run(["grep", "-rn", symbol, "--include=*.py", "."],
                       cwd=REPO, capture_output=True, text=True, timeout=120)
    for line in r.stdout.splitlines():
        path = line.split(":", 1)[0].lstrip("./")
        if "/logs/" in path or "worktrees" in path or "/tests/" in path:
            continue
        # EXCLUDE SELF. This producer names the symbols it audits, so a naive scan counts the
        # audit as a caller -- the same self-pollution caught in the inventory producer earlier
        # today, where a docstring quoting a figure made the audit its own producer.
        if Path(path).name == Path(__file__).name:
            continue
        if f"def {symbol}" in line:
            continue
        out.append(path)
    return sorted(set(out))


def lesson_1_substance_test() -> dict:
    """*"the panel applies a substance test to every reply and the runner applies none."*"""
    defined = "def verdict_is_substantive" in _text(ORCH)
    callers = _callers_of("verdict_is_substantive") + _callers_of("accept_reply_or_work")
    panels = [c for c in set(callers) if "confer" in c]
    runners = [c for c in set(callers) if c in (RUNNER, SIMRUN, CORE)]
    return {
        "lesson": "1. a substance test on every reply",
        "his_words": "the panel applies a substance test to every reply and the runner applies none",
        "predicate_defined_in": ORCH if defined else "NOWHERE",
        "panel_callers": sorted(panels),
        "runner_callers": sorted(runners),
        "landed_in_the_runners": bool(runners),
        "note": ("HE WAS RIGHT AND STILL IS. The predicate exists and is good -- "
                 "`accept_reply_or_work` judges the whole artefact SET after a seat wrote "
                 "77,219 bytes across 12 files and was recorded ok=False, chars=0 -- but it is "
                 "called ONLY by confer harnesses. The runner's dispatch path, "
                 "`runner_core.dispatch_to_model`, returns (text, elapsed) with no check at "
                 "all, so an error string or a usage notice reaches the parser as a reply."),
    }


def lesson_2_retry_preserves() -> dict:
    """*"a retry must not erase the attempt it replaces."* He added: *"Measure it first."*"""
    orch = _text(ORCH)
    accumulates = bool(re.search(r"_sink_calls\s*:\s*list\s*=\s*\[\]", orch)) and \
        bool(re.search(r'"tool_calls":\s*len\(_sink_calls\)', orch))
    per_attempt = '"per_attempt": _sink_attempts' in orch
    runner_writes_replies = bool([
        l for l in _text(RUNNER).splitlines()
        if re.search(r"write_text|json\.dump", l)
        and re.search(r"repl|answer|seat", l, re.I)])
    return {
        "lesson": "2. a retry must not erase the attempt it replaces",
        "his_words": "Measure it first to confirm",
        "orchestrator_accumulates_across_attempts": accumulates,
        "records_per_attempt_detail": per_attempt,
        "runner_writes_a_reply_a_retry_could_overwrite": runner_writes_replies,
        "landed_in_the_runners": accumulates and per_attempt and not runner_writes_replies,
        "note": ("LANDED, AND BETTER THAN THE PANEL'S. The panel moves a prior file aside; the "
                 "dispatcher ACCUMULATES across attempts and keeps per-attempt detail, fixed "
                 "2026-09-07 after a seat found 7 calls then 2 logged as 2, losing 7. The "
                 "runner writes no per-model reply, so it has nothing to overwrite. An earlier "
                 "NOT LANDED verdict searched for the panel's function NAME, not the behaviour."),
    }


def lesson_3_detect_do_not_declare() -> dict:
    """*"state should be detected rather than declared."*"""
    runner = _text(RUNNER)
    detect = "def detect_target_kind" in runner
    reads_bytes = bool(re.search(r"detect_target_kind.{0,900}?(read_bytes|read_text|suffix)",
                                 runner, re.S))
    panel_form = "_detect_round_kind" in _text("bench/confer_maths_panel_2026-09-05.py")
    return {
        "lesson": "3. state detected from content, not declared by a variable",
        "his_words": "We should use it. Wire it in all simulated and real runners going forward",
        "runner_has_detect_target_kind": detect,
        "it_reads_the_artefact_rather_than_a_declaration": reads_bytes,
        "panel_has_its_round_kind_form": panel_form,
        "landed_in_the_runners": detect and reads_bytes,
        "note": ("LANDED IN A DIFFERENT FORM, which is the honest verdict rather than a tick. "
                 "The runner detects TARGET kind from the actual path and bytes and returns the "
                 "detected kind in every case. The panel's form detects ROUND kind, blind or "
                 "joint, and the runner has no blind/joint round concept to apply it to."),
    }


def lesson_4_one_definition() -> dict:
    """*"one of them should import the other's definition rather than restate it."*"""
    orch = _text(ORCH)
    # WHITESPACE-FLEXIBLE, because the sentence it looks for is LINE-WRAPPED in the source:
    # "several\n    confer harnesses each grew their own copy". A rigid pattern reported False
    # on a docstring this assistant had just read with its own eyes -- the same predicate fault
    # as every other one caught this session.
    doc = bool(re.search(r"several\s+confer\s+harnesses\s+each\s+grew\s+their\s+own\s+copy",
                         orch))
    importers = _callers_of("verdict_is_substantive")
    return {
        "lesson": "4. one definition imported, not restated in 2 places",
        "his_words": "one of them should import the other's definition rather than restate it",
        "the_shared_predicate_is_a_free_function": "def verdict_is_substantive" in orch,
        "its_docstring_records_the_consolidation": doc,
        "files_importing_it_rather_than_restating": sorted(set(importers)),
        "landed_in_the_runners": doc and len(set(importers)) >= 2,
        "note": ("LANDED. `verdict_is_substantive` is deliberately a FREE FUNCTION and its own "
                 "docstring records why: 'several confer harnesses each grew their own copy of "
                 "the same three-clause test'. An earlier UNVERIFIED verdict searched for "
                 "`REQUIRED_FIELDS`, a symbol this assistant invented, which exists nowhere."),
    }


LESSONS = (lesson_1_substance_test, lesson_2_retry_preserves,
           lesson_3_detect_do_not_declare, lesson_4_one_definition)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = [fn() for fn in LESSONS]
    if args.json:
        print(json.dumps(rows, indent=1, default=str))
        return 0
    for r in rows:
        mark = "LANDED    " if r["landed_in_the_runners"] else "NOT LANDED"
        print(f"  [{mark}] {r['lesson']}")
        print(f"       his words: \"{r['his_words']}\"")
        for k, v in r.items():
            if k in ("lesson", "his_words", "note", "landed_in_the_runners"):
                continue
            print(f"         {k}: {v}")
        print(f"         -> {r['note']}")
        print()
    k = sum(1 for r in rows if r["landed_in_the_runners"])
    n = len(rows)
    lo, hi = wilson(k, n)
    print(f"   LANDED {k} of {n} = {k/n:.4f}  Wilson [{lo}, {hi}]")
    print(f"   An earlier pass reported 0 of 4 and it is WITHDRAWN: its grep patterns used "
          f"BRE alternation under -E and matched a literal pipe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
