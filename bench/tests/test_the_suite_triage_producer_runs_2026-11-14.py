"""The suite-triage producer is EXECUTED here, not merely named.

★ WHY THIS FILE EXISTS AT ALL. `test_an_unreached_producer_set_cannot_grow_
2026-11-08.py` admits no producer that no test reaches, which is the
addition-nothing-reaches half of `additive-standard`. The surveyor behind it
checks whether a test NAMES the producer, so a file that merely mentioned the
path would silence the refusal while proving nothing -- recorded on 2026-11-14
in entry B195, the unwatchable commit board. Everything below CALLS it.

★ AND IT PINS NO FIGURE. The 2 logs it was written against live outside the
repository, so a clone has neither; and a partition over 2 logs is a fact about
those 2 runs, not about the project. What is asserted is the PROPERTY: that the
parser recovers every verdict row including the awkward one, that the partition
arithmetic closes in both directions, and that the producer REFUSES rather than
reporting a smaller number when its 2 counting routes disagree.

★ THE AWKWARD ROW IS REAL AND IS THE REASON THE PARSER WAS REWRITTEN. This
suite contains a test whose node id carries SPACES inside a parametrize label --
`test_the_labelled_set[I23: exhausted_round_threshold defaults to 8 while
max_rounds is 8-True]`. The first parser used `(\\S+?)` for the node id, could
not span it, failed to match the line at all, and silently dropped it from BOTH
logs, reporting 22 carried-over failures where the truth was 23.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_suite_triage_2026-11-14.py"

#: The real node id that defeated the first parser, reproduced verbatim.
AWKWARD = ("bench/tests/test_blocker_triage_2026-09-10.py::"
           "TestItAnswersTheRightQuestion::test_the_labelled_set"
           "[I23: exhausted_round_threshold defaults to 8 while max_rounds is 8-True]")


@pytest.fixture(scope="module")
def mod():
    if not PRODUCER.is_file():
        pytest.skip("the producer is not in this checkout")
    spec = importlib.util.spec_from_file_location("suite_triage", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["suite_triage"] = m
    spec.loader.exec_module(m)
    return m


def _log(*nodeids: str) -> str:
    body = "\n".join(f"FAILED {n}" for n in nodeids)
    return (f"{body}\n{len(nodeids)} failed, 10 passed, 0 skipped in 1.00s\n")


class TestTheParserRecoversEveryRow:
    def test_a_node_id_with_spaces_is_not_dropped(self, mod):
        """THE HISTORICAL DEFECT. A `\\S+?` node id cannot span this one."""
        parsed = mod.rows(_log(AWKWARD, "a.py::test_b"))
        assert AWKWARD in parsed, (
            "the parametrized node id with spaces was dropped; this is the "
            "exact row that made the partition read 22 where it was 23")
        assert len(parsed) == 2

    def test_a_reason_tail_is_split_off_but_a_label_is_not(self, mod):
        nid, reason = mod.split_reason("a.py::test_x - AssertionError: boom")
        assert nid == "a.py::test_x" and reason == "AssertionError: boom"
        nid2, reason2 = mod.split_reason(AWKWARD)
        assert nid2 == AWKWARD and reason2 == "", (
            "a parametrize label was mistaken for a reason tail")

    def test_a_separator_inside_a_label_does_not_cut_the_node_id(self, mod):
        """The search starts AFTER the last bracket, so a label cannot be cut."""
        nid = "a.py::test_x[alpha - beta]"
        got, reason = mod.split_reason(nid + " - KeyError: k")
        assert got == nid and reason == "KeyError: k"

    def test_an_error_row_is_parsed_as_well_as_a_failure(self, mod):
        text = "FAILED a.py::test_a\nERROR b.py::test_b\n2 failed, 1 error in 1.00s\n"
        parsed = mod.rows(text)
        assert set(parsed) == {"a.py::test_a", "b.py::test_b"}
        assert parsed["b.py::test_b"]["kind"] == "ERROR"


class TestItRefusesRatherThanReportingTheSmallerNumber:
    def test_a_parse_matching_the_line_count_is_accepted(self, mod):
        text = _log(AWKWARD, "a.py::test_b", "c.py::test_d")
        assert len(mod.parse_or_refuse(text, "fixture")) == 3

    def test_two_rows_colliding_on_one_node_id_is_refused(self, mod):
        """ANTI-VACUITY in the other direction: the check must be able to fire."""
        text = "FAILED a.py::test_a\nFAILED a.py::test_a\n2 failed in 1.00s\n"
        with pytest.raises(SystemExit) as e:
            mod.parse_or_refuse(text, "fixture")
        assert "REFUSED" in str(e.value)


class TestThePartitionArithmeticCloses:
    def test_carried_fixed_and_new_reconstruct_both_sides(self, mod):
        today = mod.parse_or_refuse(_log(AWKWARD, "a::t1", "b::t2"), "today")
        base = mod.parse_or_refuse(_log(AWKWARD, "a::t1", "c::t3", "d::t4"), "base")
        carried = set(today) & set(base)
        fixed = set(base) - set(today)
        new = set(today) - set(base)
        assert len(carried) == 2 and len(fixed) == 2 and len(new) == 1
        assert len(carried) + len(new) == len(today)
        assert len(carried) + len(fixed) == len(base)


class TestItAnswersHelpWithoutMeasuringAnything:
    def test_help_prints_a_usage_line_and_exits_zero(self):
        import subprocess
        if not PRODUCER.is_file():
            pytest.skip("the producer is not in this checkout")
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"],
                           capture_output=True, text=True, timeout=60,
                           cwd=str(REPO))
        assert r.returncode == 0, r.stderr[-800:]
        assert any(ln.lstrip().lower().startswith("usage:")
                   for ln in r.stdout.splitlines()), (
            "exit 0 is not an answer; a usage line is")
