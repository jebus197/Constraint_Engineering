# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_directive_set_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 1a12e681f0925d10ea6bfe5342f348491f1604dd03ad8c772c9610b807d8eeb8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Falsifier: `sim45_memory_20260908T033012Z` C0050 is NOT genuinely irreducible.

JOINT ROUND J5, 2026-10-14. Seat cc2's blind reply records exactly 1 genuinely
irreducible finding in 41 UNTOOLABLE rows and names C0050 as that one case, on
the ground that a falsifier was attempted and the record states a structural
bar: "it cannot be falsified by any test importing `_memory.py`."

This script decides the question by EXECUTION on the artefact and its declared
inputs only -- the archived `runner_state.json` of that run and the target file
`bench/dm/_memory.py` that the run reviewed. It reads no scoring key, no answer
file, no planted-defect manifest and no prior-round report.

TWO INDEPENDENT GROUNDS, EITHER OF WHICH DEFEATS THE EXCEPTION.

GROUND 1 -- the dispositive sub-claim is arithmetic, and it is FALSE.
C0050's closing sentence is:

    "The artifact header states 20,563 chars; HEAD is 20,605. So the text I was
     asked to review matches neither HEAD nor any observed working-tree state."

`bench/dm/_memory.py` is 20,563 CHARACTERS and 20,605 BYTES. The two numbers the
finding sets against each other are a character count and a byte count of the
SAME file; the gap is UTF-8 multibyte, not a mismatch. The artifact header
therefore matched HEAD exactly, and the inference drawn from it is refuted by
two subtractions. A claim refuted by arithmetic is not irreducible.

GROUND 2 -- no falsifier was ever attempted against C0050's claim.
`routing_history[0].last_falsifier_code` is a 600-char program whose own
docstring says it tests whether `ImmuneMemory.load` type-checks
``experiment_ids``. That is a different proposition from C0050's. The routing
ladder stopped at rungs_tried=2 of rungs_available=6 with verdict ERROR. So the
record does not show "a machine tried and failed"; it shows a machine tried a
DIFFERENT claim and stopped with 4 rungs in hand. The run's own
`routing_defer_reason` says as much in terms: "no falsifier and no S_k
evaluation exist, so nothing has been assessed yet. 'Irreducible' would assert a
machine tried and failed."

USAGE
    python3 scripts/falsifier_C0050_is_not_irreducible_2026-10-14.py --claim cc2
        RED. Asserts cc2's proposition (C0050 is genuinely irreducible). The
        assertion fails and the token FALSIFIED is printed.
    python3 scripts/falsifier_C0050_is_not_irreducible_2026-10-14.py --claim amended
        GREEN. Asserts the amended proposition (C0050 is toolable and its
        dispositive sub-claim is false). Exits 0, prints no FALSIFIED token.

Exit status is 1 on a demonstrated defect and 0 otherwise, so a harness may read
either the token or the status.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
RUN = REPO / "bench" / "logs" / "sim45_memory_20260908T033012Z" / "runner_state.json"
TARGET = REPO / "bench" / "dm" / "_memory.py"

#: The two numbers C0050 sets against each other, quoted from its own text.
HEADER_CHARS_CLAIMED = 20563
HEAD_CHARS_CLAIMED = 20605


def measure() -> dict:
    """Every number this falsifier decides on, computed, never asserted."""
    entry = json.loads(RUN.read_text(encoding="utf-8"))["registry"]["entries"]["C0050"]
    raw = TARGET.read_bytes()
    text = raw.decode("utf-8")

    rh = (entry.get("routing_history") or [{}])[0]
    code = rh.get("last_falsifier_code") or ""

    return {
        "target_chars": len(text),
        "target_bytes": len(raw),
        "multibyte_delta": len(raw) - len(text),
        "numbers_are_chars_and_bytes_of_one_file": (
            len(text) == HEADER_CHARS_CLAIMED and len(raw) == HEAD_CHARS_CLAIMED
        ),
        "falsifier_verdict": entry.get("falsifier_verdict"),
        "rungs_tried": rh.get("rungs_tried"),
        "rungs_available": rh.get("rungs_available"),
        "routing_verdict": rh.get("verdict"),
        "attempt_subject_is_experiment_ids": "experiment_ids" in code,
        "attempt_mentions_rewrite_churn": any(
            tok in code for tok in ("oscillat", "rewritten", "artifact header")
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--claim", choices=("cc2", "amended"), default="cc2",
                    help="cc2 = C0050 is genuinely irreducible (RED). "
                         "amended = C0050 is toolable, sub-claim false (GREEN).")
    args = ap.parse_args()

    m = measure()
    for k, v in m.items():
        print(f"  {k:42s} {v!r}"[:200])

    if args.claim == "cc2":
        try:
            assert not m["numbers_are_chars_and_bytes_of_one_file"], (
                "GROUND 1: C0050's two numbers are the character count and the byte "
                f"count of one unchanged file ({m['target_chars']} chars, "
                f"{m['target_bytes']} bytes, delta {m['multibyte_delta']} from UTF-8 "
                "multibyte). The artifact header MATCHED HEAD; the inference drawn "
                "from the pair is false and two subtractions decide it.")
            assert not (m["attempt_subject_is_experiment_ids"]
                        and not m["attempt_mentions_rewrite_churn"]), (
                "GROUND 2: the only recorded attempt tests `experiment_ids` type "
                f"handling, not C0050's claim, and stopped at rung "
                f"{m['rungs_tried']} of {m['rungs_available']} with verdict "
                f"{m['routing_verdict']}. No machine tried this claim.")
        except AssertionError as exc:
            print("FALSIFIED")
            print(f"  {exc}")
            return 1
        print("cc2's proposition survives: C0050 is genuinely irreducible.")
        return 0

    assert m["numbers_are_chars_and_bytes_of_one_file"], m
    assert m["attempt_subject_is_experiment_ids"], m
    assert not m["attempt_mentions_rewrite_churn"], m
    assert m["rungs_tried"] < m["rungs_available"], m
    print("AMENDED CLAIM HOLDS: C0050 is toolable; its dispositive sub-claim is "
          "refuted by arithmetic; genuinely-irreducible count is 0 of 41.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
