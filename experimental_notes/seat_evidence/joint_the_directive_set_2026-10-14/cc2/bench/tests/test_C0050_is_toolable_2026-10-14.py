# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_the_directive_set_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: c849a70bf4e140c2a0e576c322524ad84483e581f8229d6b2c44012fb75b60b3
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The 1 'genuinely irreducible' finding in the archive is not irreducible.

JOINT ROUND J5, 2026-10-14. Seat cc2's blind reply records exactly 1 genuinely
irreducible finding in 41 UNTOOLABLE rows -- `sim45_memory_20260908T033012Z`
C0050 -- and argues the record should carry the exception rather than a sweep.
Seat fable records 0 and treats it as equipment failure. Neither position was
decided by a tool, so this file decides it.

THE WIRING. `scripts/falsifier_C0050_is_not_irreducible_2026-10-14.py` is the
producer. This test EXECUTES it in both directions as a subprocess, so the
producer cannot drift from the assertion that cites it, and an unwired script is
not left in the tree. A measured rate travels with its producing script; this is
the caller that reaches it.

WHAT IT DECIDES. C0050's dispositive sub-claim sets 20,563 against 20,605 and
concludes the reviewed artefact "matches neither HEAD nor any observed
working-tree state". Those are the CHARACTER count and the BYTE count of one
unchanged file; the 42-char gap is UTF-8 multibyte. The artefact header matched
HEAD exactly. And the only recorded falsifier attempt tests a different
proposition (`ImmuneMemory.load` type-handling of ``experiment_ids``) and
stopped at rung 2 of 6 with verdict ERROR, so no machine tried this claim.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "falsifier_C0050_is_not_irreducible_2026-10-14.py"
RUN = REPO / "bench" / "logs" / "sim45_memory_20260908T033012Z" / "runner_state.json"
TARGET = REPO / "bench" / "dm" / "_memory.py"


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(PRODUCER), *args],
                          capture_output=True, text=True, timeout=120)


def test_the_producer_exists_and_is_help_free():
    assert PRODUCER.is_file(), PRODUCER
    p = _run("--help")
    assert p.returncode == 0, p.stderr


def test_RED_cc2s_proposition_is_falsified():
    """RED: asserting C0050 is genuinely irreducible must FAIL."""
    p = _run("--claim", "cc2")
    assert p.returncode == 1, (p.returncode, p.stdout, p.stderr)
    assert "FALSIFIED" in p.stdout, p.stdout


def test_GREEN_the_amended_proposition_holds():
    """GREEN: asserting C0050 is toolable must exit cleanly."""
    p = _run("--claim", "amended")
    assert p.returncode == 0, (p.returncode, p.stdout, p.stderr)
    assert "FALSIFIED" not in p.stdout, p.stdout
    assert "AMENDED CLAIM HOLDS" in p.stdout, p.stdout


def test_the_char_byte_arithmetic_directly():
    """The two numbers, recomputed here independently of the producer."""
    if not TARGET.is_file():
        pytest.skip(f"target absent: {TARGET}")
    raw = TARGET.read_bytes()
    assert len(raw.decode("utf-8")) == 20563, len(raw.decode("utf-8"))
    assert len(raw) == 20605, len(raw)
    assert len(raw) - len(raw.decode("utf-8")) == 42


def test_the_only_recorded_attempt_targets_a_different_claim():
    if not RUN.is_file():
        pytest.skip(f"run record absent: {RUN}")
    e = json.loads(RUN.read_text(encoding="utf-8"))["registry"]["entries"]["C0050"]
    rh = e["routing_history"][0]
    code = rh["last_falsifier_code"]
    assert "experiment_ids" in code                       # the attempt's subject
    assert "oscillat" not in code and "artifact header" not in code  # not C0050's
    assert rh["rungs_tried"] < rh["rungs_available"], rh  # ladder not exhausted
    assert e["falsifier_verdict"] == "UNTOOLABLE", e["falsifier_verdict"]
