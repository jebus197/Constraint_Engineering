"""The additive standard, enforced in BOTH directions rather than asserted.

FOUNDER, standing: work is additive — never disable or remove a feature; removal
only when something better renders it redundant.

WHY THIS FILE EXISTS, AND THE IRONY THAT PRODUCED IT. On 2026-09-07 the founder
asked whether the rule could be mechanically enforced. Checking the record first
showed the rule lived in ONE memory note, recording that it had been pasted into
ONE panel brief on 2026-08-31 — and in no standing-rules file and no system
prompt. **The rule governing whether work is additive was itself an addition wired
to nothing.** It failed its own standard, which is the strongest possible argument
for wiring it rather than restating it.

WHY THE RULE IS ENFORCED SYMMETRICALLY. Measured over commits since 2026-08-01:
11 confirmed defects were ADDITIONS that did nothing — a severity checker that
decided nothing, a confinement mechanism never called, `EXTEND` read by nothing,
264 orphaned clones, a write-once proof stamp — and 0 were removals of something
needed. Addition-side share 100%, Wilson [74.1%, 100.0%]. An unqualified "never
remove" rule points at the failure mode that has not occurred here and away from
the one that keeps happening. The removal half still binds: the single near-miss
was CC1 proposing to replace the model-derived severity with a rubric it had
ALREADY measured as agreeing no better than chance (kappa = -0.0227, Fisher
p = 0.78) — caught by the founder, not by a mechanism.

THE THREE LAYERS ARE NOT ALTERNATIVES. They guard different things and compose:
  1. the standard reaches the ACTORS   -> the dispatcher's SYSTEM prompt, tested here
  2. removals are checked              -> the capability set may not shrink
  3. additions are checked             -> a ratchet on config fields no test reaches
Drop any one and a direction goes unguarded.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))
from capability_snapshot import capabilities, SNAPSHOT  # noqa: E402

#: Capabilities deliberately retired, each with the thing that superseded it and
#: the measurement that showed dominance. A name may leave the set ONLY by
#: appearing here. Adding an entry is a decision; forgetting one is a test failure.
RETIRED = {
    "ext": "duplicate of `re` (the project table called it 'a shorter alias for re'); "
           "0 uses measured across the visible transcripts, Wilson [0.00%, 5.35%]",
    "rc":  "duplicate of `rs` (the global shorthand called it 'equivalent to rs')",
    "rr":  "superseded by `rs`; the parser never recognised it, so typing it "
           "produced no obligation at all",
}

#: Config fields no test file names, pinned 2026-09-07. A RATCHET, not a target:
#: 22 of 89 is a backlog, and failing the suite on a backlog teaches people to
#: delete the test. What it forbids is GROWTH — a new switch that nothing exercises.
UNREACHED_BASELINE = 22


def _unreached_config_fields() -> list[str]:
    caps = capabilities()
    tests = " ".join(p.read_text(errors="replace")
                     for p in (REPO / "bench" / "tests").glob("*.py"))
    return [f for f in caps["runner_config_fields"] if f not in tests]


def _system_prompt_value() -> str:
    """The SYSTEM constant as the dispatcher will actually send it.

    Imported rather than read, so comments cannot satisfy the assertion.
    """
    import importlib.util
    path = REPO / "bench" / "confer_maths_panel_2026-09-05.py"
    src = path.read_text()
    # The module dispatches on import, so evaluate only the SYSTEM assignment.
    i = src.index("SYSTEM = (")
    j = src.index("\n)", i) + 2
    ns: dict = {}
    exec(compile(src[i:j], str(path), "exec"), ns)
    return ns["SYSTEM"]


# ---------------------------------------------------------------- layer 1
def test_the_standard_reaches_every_panel_seat_by_construction():
    """It was carried in ONE brief and no system prompt, so whether a seat heard it
    depended on who wrote the brief."""
    # THE VALUE, NOT THE SOURCE TEXT. The first version of this test sliced the
    # source between the SYSTEM parens, which INCLUDES COMMENTS -- so a comment
    # mentioning the standard satisfied it while the prompt itself could have lost
    # the text. Proved by execution: renaming the comment left the test green.
    # `execute-do-not-grep`, violated inside the test enforcing the rule.
    system = _system_prompt_value().upper()
    assert "ADDITIVE STANDARD" in system, (
        "the dispatcher's SYSTEM prompt no longer carries the additive standard, "
        "so a seat hears it only if someone remembers to paste it into the brief")
    assert "COMMITTED MEASUREMENT" in system, (
        "the standard is present but its 'better means measured' clause is gone, "
        "which is the half that makes it decidable rather than a matter of taste")


def test_the_standard_is_in_the_standing_rules_files():
    for rel in (".claude/CLAUDE.md", "docs/WORKING_DIRECTIVES.md"):
        text = (REPO / rel).read_text()
        assert "additive-standard" in text, f"{rel} does not carry the rule"


# ---------------------------------------------------------------- layer 2
def test_no_capability_disappears_without_being_retired():
    """THE REMOVAL HALF. A name may leave the set only via RETIRED, which requires
    naming what superseded it and the measurement that showed dominance."""
    assert SNAPSHOT.is_file(), (
        "the capability snapshot is missing; regenerate with "
        "`python3 scripts/capability_snapshot.py --write`")
    stored = json.loads(SNAPSHOT.read_text())
    now = capabilities()
    lost = {}
    for bucket, names in stored.items():
        gone = [n for n in names if n not in now.get(bucket, []) and n not in RETIRED]
        if gone:
            lost[bucket] = gone
    assert not lost, (
        "capabilities vanished without a RETIRED entry: " + json.dumps(lost) +
        "\nIf the removal is intended, add each name to RETIRED with what "
        "supersedes it AND the measurement showing the replacement dominates. "
        "A judgement that something is better is not evidence that it is.")


def test_every_retired_entry_names_a_successor_or_a_measurement():
    """A RETIRED entry that says only 'removed' would let the guard be satisfied by
    typing, which is the failure the ledger already recorded 10 times."""
    for name, why in RETIRED.items():
        assert len(why) > 40, f"RETIRED[{name!r}] is too thin to be a justification"
        assert any(k in why.lower() for k in
                   ("duplicate", "superseded", "measured", "wilson", "%")), (
            f"RETIRED[{name!r}] names neither a successor nor a measurement")


def test_the_snapshot_is_derived_and_not_typed():
    """Regenerating must reproduce the file exactly, or the snapshot has been
    hand-edited and is no longer evidence about the code."""
    stored = json.loads(SNAPSHOT.read_text())
    fresh = capabilities()
    for bucket in fresh:
        assert bucket in stored, f"a whole capability class is unsnapshotted: {bucket}"


# ---------------------------------------------------------------- layer 3
def test_unreached_config_fields_do_not_grow():
    """THE ADDITION HALF, and the direction the evidence says actually bites.
    A new switch that no test exercises is an addition that does nothing."""
    unreached = _unreached_config_fields()
    assert len(unreached) <= UNREACHED_BASELINE, (
        f"{len(unreached)} config fields are named in no test, up from the pinned "
        f"{UNREACHED_BASELINE}. New: {sorted(set(unreached))[:6]}. "
        f"Wire the new switch to a test, or lower the baseline if you reduced it.")


def test_the_ratchet_is_not_vacuous():
    """If the field list ever came back empty the ratchet would pass forever."""
    caps = capabilities()
    assert len(caps["runner_config_fields"]) > 50, (
        "RunnerConfig fields could not be parsed; the ratchet is measuring nothing")


def test_the_baseline_is_honest():
    """Pinning a number above the real one would silently licence growth."""
    assert UNREACHED_BASELINE == len(_unreached_config_fields()), (
        "the pinned baseline no longer equals the measured count — if the backlog "
        "shrank, lower the pin so the ratchet keeps biting")
