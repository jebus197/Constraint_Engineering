# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_period_reviewed_2026-11-04', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6f8ec04c27cb6ea7733174be6679bd1534d48f6fb191a50d23ee34c08b7033ef
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The B108 census producer must EXECUTE, not merely exist.

Added 2026-11-04 by the panel. The producer
`scripts/the_census_counts_what_the_reader_excludes_2026-11-04.py` was the
evidence behind task entry B108, and the entry records it as "4 steps, exit 0".
It exited 1 and printed a verdict that contradicted its own checks, for four
months' worth of a single root cause: B108's repair landed in
`read_founder_responses_2026-10-11.py`, the producer still asserted the
PRE-repair identity, and nothing ever ran it. The only test touching it,
`test_the_census_counts_only_his_writing_2026-11-04.py::
test_the_producer_exists_and_is_reachable`, reads its SOURCE TEXT for `def`
lines. A source-text check cannot see a producer that runs and is wrong.

This file executes it. That is the whole point, and it is deliberately the
smallest thing that would have caught the defect.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_census_counts_what_the_reader_excludes_2026-11-04.py"


def _run():
    return subprocess.run([sys.executable, str(PRODUCER)], cwd=str(REPO),
                          capture_output=True, text=True, timeout=600)


def _corpus_present() -> bool:
    """The producer reads the founder's response folder, which lives outside
    the repository. Absent it, there is nothing to measure and skipping is the
    honest outcome -- but the skip must be visible, never a silent pass."""
    # The module name carries dashes, so load it by path rather than by import.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_rfr", REPO / "scripts" / "read_founder_responses_2026-10-11.py")
    if spec is None or spec.loader is None:
        return False
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:
        return False
    return bool(getattr(mod, "RESPONSES", None) and mod.RESPONSES.is_dir())


pytestmark = pytest.mark.skipif(
    not _corpus_present(),
    reason="the founder's Responses folder is not on this machine; "
           "the producer has nothing to read and the check is vacuous here")


def test_the_producer_exits_zero():
    r = _run()
    assert r.returncode == 0, (
        "the producer behind entry B108 did not discharge its own checks.\n"
        f"--- stdout tail ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}")


def test_the_verdict_is_gated_on_the_checks_not_appended_to_them():
    """The original VERDICT line was an unconditional f-string with the check
    flag appended, so a failed check still shipped the assertion. Either the
    checks hold and the claim is made, or they do not and it is withheld."""
    r = _run()
    out = r.stdout
    assert "VERDICT:" in out, "the producer printed no verdict at all"
    claimed = "over-reported his verdicts by" in out
    withheld = "NOT ESTABLISHED" in out
    assert claimed != withheld, (
        "the verdict must be EITHER asserted OR withheld, never both and never "
        f"neither. asserted={claimed} withheld={withheld}")
    if claimed:
        assert "All structural checks held: False" not in out, (
            "a failed structural check shipped alongside an asserted claim -- "
            "this is the exact defect the 2026-11-04 repair removed")


def test_the_decomposition_identity_holds_by_an_independent_route():
    """broad == his + residue, recomputed here from the reader rather than
    parsed out of the producer's own printing."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_rfr2", REPO / "scripts" / "read_founder_responses_2026-10-11.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    broad = [p for p in sorted(mod.RESPONSES.glob("*")) if mod.is_a_response_file(p)]
    broad_total = sum(len(mod._annotations_in(p)) for p in broad)
    his = len(mod.annotations())
    residue = sum(len(mod._annotations_in(p)) for p in broad
                  if not mod.is_one_of_his_annotated_responses(p))
    assert broad_total == his + residue, (
        f"{broad_total} != {his} + {residue}")
    assert broad_total > his, (
        "if the two predicates agree there is no over-count to report and "
        "entry B108 would be describing a defect that is not there")
