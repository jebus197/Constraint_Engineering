#!/usr/bin/env python3
"""The Stop gate credits FOLLOW only for a turn's FIRST FFAFP cycle.

WHAT THIS MEASURES. `ffafp_audit` builds the FOLLOW evidence for a turn as

    scan_text = " ".join(t for i, t in scans if first is None or i < first)

where `first` is `first_mut`, the index of the turn's FIRST mutation. A tree scan
that happens AFTER that index contributes nothing, which is the documented intent
-- the code's own words are "FOLLOW. A TREE SCAN naming the changed file or its
stem, before the edit." For a supervised turn, which is about one cycle, that is
exactly right.

WHY IT MATTERS FOR AN AUTONOMOUS RUN. `first_mut` is set ONCE PER TURN. An
overnight run performs many complete FFAFP cycles inside a single turn -- the turn
measured on 2026-11-01 held 262 tool calls and 26 tree scans -- so once the first
edit lands, FOLLOW cannot be satisfied again for the rest of the turn. A refusal
then stops distinguishing "never followed" from "followed 26 times, none of them
before edit 1", and the gate's own summary figure ("FOLLOW missing in N of the
last 40 work turns") cannot be read as a count of undisciplined turns.

★ 2 EARLIER DIAGNOSES OF MINE ARE WITHDRAWN HERE, AND THIS SCRIPT IS WHAT
REFUTED THEM. (1) That an 8 MiB `TAIL_BYTES` against a 638 MB transcript left no
turn-close boundary in the window: refuted, because across 35,111 inter-turn gaps
the largest is 1,605,379 bytes and 0 exceed the window. (2) That auditing an open
turn was a bug: refuted, because `scan` closes a turn only on a human prompt,
which is correct, and the audited turn IS the current one. The gate was right and
the first 2 explanations were mine.

IT CHANGES NOTHING. The repair would alter when the gate refuses, and that
behaviour is the founder's ruling of 2026-10-24.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import pathlib
import sys

HOOKS = pathlib.Path.home() / ".claude" / "hooks"
PROJECTS = pathlib.Path.home() / ".claude" / "projects"


def newest_transcript() -> pathlib.Path | None:
    c = sorted(PROJECTS.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime,
               reverse=True)
    return c[0] if c else None


def measure(transcript: pathlib.Path) -> dict:
    sys.path.insert(0, str(HOOKS))
    spec = importlib.util.spec_from_file_location(
        "gate_probe", HOOKS / "ffafp_stop_gate.py")
    gate = importlib.util.module_from_spec(spec)
    sys.modules["gate_probe"] = gate
    spec.loader.exec_module(gate)
    import ffafp_audit as fa

    tail = int(getattr(gate, "TAIL_BYTES", 8 * 1024 * 1024))
    size = transcript.stat().st_size
    state = {"offset": 0, "open": None, "seq": 0, "reads": {}}
    closed: list = []
    with transcript.open("r", errors="ignore") as fh:
        if size > tail:
            fh.seek(size - tail)
            fh.readline()
            state["offset"] = fh.tell()
        fa.scan(fh, state, on_close=closed.append)

    op = state.get("open") or {}
    scans = op.get("scans") or []
    first = op.get("first_mut")
    before = [i for i, _ in scans if first is None or i < first]
    after = [i for i, _ in scans if first is not None and i >= first]
    counted = " ".join(t for i, t in scans if first is None or i < first)
    every = " ".join(t for _, t in scans)
    verdict = gate.last_turn_verdict(transcript) or {}
    bases = sorted({pathlib.Path(f).name for f in (verdict.get("files") or [])
                    if not f.startswith("<")})
    return {
        "transcript_bytes": size,
        "window_bytes": tail,
        "turn_ts": op.get("ts"),
        "n_tools": op.get("n_tools"),
        "first_mut": first,
        "tree_scans": len(scans),
        "scans_before_first_edit": before,
        "scans_after_first_edit": after,
        "closed_turns_in_window": len(closed),
        "verdict_missing": verdict.get("missing"),
        "bases": bases,
        "base_in_counted": {b: (b in counted) for b in bases},
        "base_in_any_scan": {b: (b in every) for b in bases},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--transcript")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    t = (pathlib.Path(args.transcript) if args.transcript
         else newest_transcript())
    if t is None or not t.exists():
        print("no transcript found; nothing to measure")
        return 2
    r = measure(t)
    if args.json:
        print(json.dumps(r, indent=2))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"turn under audit     : {r['turn_ts']}  (opened by a human prompt)")
    print(f"  tool calls in it   : {r['n_tools']}")
    print(f"  first_mut index    : {r['first_mut']}")
    print(f"  tree scans         : {r['tree_scans']}")
    print(f"    before first edit (COUNTED) : {len(r['scans_before_first_edit'])}")
    print(f"    after  first edit (IGNORED) : {len(r['scans_after_first_edit'])}")
    print(f"  the gate reports missing      : {r['verdict_missing']}")
    print()
    if r["bases"]:
        print("  changed file basenames, and where they appear:")
        for b in r["bases"]:
            print(f"    {b:<32} counted={r['base_in_counted'][b]!s:<5} "
                  f"any_scan={r['base_in_any_scan'][b]}")
    print()
    unsatisfiable = (r["first_mut"] is not None
                     and not r["scans_before_first_edit"]
                     and r["scans_after_first_edit"])
    if unsatisfiable:
        print("UNSATISFIABLE FOR THE REST OF THIS TURN: CONFIRMED.")
        print("  Every tree scan in the turn falls after the first edit, so the")
        print("  FOLLOW evidence set is empty and no later action can refill it.")
        print("  The verdict is LITERALLY TRUE -- an edit did precede every scan --")
        print("  and it is also uninformative about the cycles that followed.")
    else:
        print("NOT in the unsatisfiable state on this transcript.")
    print()
    print("CANDIDATE REPAIRS, for the founder — NOT applied:")
    print("  1. Account per MUTATION: credit a scan naming the file that precedes")
    print("     THAT file's first mutation, so each cycle is judged on its own.")
    print("  2. Reset first_mut at a cycle boundary — needs a boundary definition")
    print("     the transcript does not currently carry.")
    print("  3. Leave it, and document that the figure is not a turn count.")
    print("  Recommendation: 1. It measures what the directive states — a trace")
    print("  before the change it relates to — rather than a property of how the")
    print("  work happens to be packaged into turns, and it adds no new concept.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
