"""The kept severity is NOT a function of the assessments beneath it (task B39).

HIS RULING, 2026-10-19: *"Verdict: option 1, but do options 1 and 2 compose? Is
this a useful thing to do? Or is 1 preferable over the other?"*

OPTION 1, AS HE WAS GIVEN IT: *"Identify the rule that produces the kept value
first, and establish whether a value outside the range of its inputs is
intended. Neither panel fix should be built until that is answered."*

THE RULE, IDENTIFIED BY EXECUTION ON 2026-10-29, AND IT IS THE ABSENCE OF A RULE.
`FindingRegistry.resolve(..., "MERGED", merged_into=...)` is the single chokepoint
every merge passes through. It marks the DUPLICATE merged and never touches the
TARGET's severity: there is no `max`, no `median`, no `mean`, and no assignment to
the target entry at all. So the kept value is whichever entry happened to be the
merge TARGET, carrying its own first-recorded severity, and every other
assessment of the same defect is DISCARDED. The target does not even record that
a merge happened to it -- after a merge its only severity-related key is
`severity`, unchanged.

WHAT THAT SETTLES, AND IT IS THE HALF HIS QUESTION TURNS ON. B39 measured that
the kept value lies OUTSIDE the range of its inputs in 23.8095% of 147 cases,
35 of 147, interval 17.6469% to 31.3061%, with 24 above every assessment and 11
below, and 1 entry carrying assessments of 0.35 and 0.45 beside a kept value of
0.95. That is not a smoothing failure and not noise. It is the arithmetic
consequence of there being NO AGGREGATION STEP: with nothing combining the
assessments, the kept value is only coincidentally inside their range, and a
value outside it is not "intended" in any designed sense.

SO OPTIONS 1 AND 2 DO NOT COMPOSE CONCURRENTLY, AND 1 IS NOT MERELY PREFERABLE
-- IT IS LOGICALLY PRIOR. Option 2 was *"build the smoothing fix alone"*.
Smoothing presupposes an aggregate to smooth. There is none, so Option 2 is the
wrong SHAPE of fix rather than a lower-priority one: before anything can be
smoothed, someone must DECIDE that the assessments should be combined at all,
and that is a question about what severity MEANS -- which is the founder's own
open question, and which no archive can settle. Option 1's own text already
sequenced this: *"Neither panel fix should be built until that is answered."*

THIS FILE CHANGES NO BEHAVIOUR. It pins the rule that exists today so that the
decision is taken against a measured fact rather than an assumption, and so that
if an aggregation step is ever added, the test that assumed its absence FAILS and
says so.

Written under CDSFL note standard v1.8.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

RUNNER = REPO / "bench" / "reference_runner_v3.py"


@pytest.fixture()
def registry():
    from bench.reference_runner_v3 import FindingRegistry
    return FindingRegistry()


def _entry(cid, sev, desc="a fault in alpha()", rnd=0):
    return {"canonical_id": cid, "id": cid, "description": desc,
            "severity": sev, "open_since_round": rnd, "status": "UNCONFIRMED"}


class TestTheMergeDoesNotCombineAssessments:
    """EXECUTED through the real chokepoint, not read off its source."""

    def test_the_target_keeps_its_own_severity(self, registry):
        registry.entries["C0001"] = _entry("C0001", 0.35)
        registry.entries["C0002"] = _entry("C0002", 0.45)
        registry.resolve("C0002", "MERGED", 1, merged_into="C0001")
        assert registry.entries["C0001"]["severity"] == 0.35, (
            "the target's severity moved on merge; an aggregation step now "
            "exists and B39's analysis must be redone against it")

    def test_the_median_of_the_inputs_is_not_what_is_kept(self, registry):
        """The specific shape B39 measured: 21.0884% of cases equal the median,
        which is what you would expect by coincidence rather than by rule."""
        registry.entries["C0001"] = _entry("C0001", 0.35)
        registry.entries["C0002"] = _entry("C0002", 0.45)
        registry.resolve("C0002", "MERGED", 1, merged_into="C0001")
        assert registry.entries["C0001"]["severity"] != 0.40, (
            "the kept value is the median of [0.35, 0.45]; an aggregation rule "
            "has been introduced")

    def test_a_kept_value_can_sit_outside_the_range_of_its_inputs(self, registry):
        """B39's worst recorded case, reproduced: assessments of 0.35 and 0.45
        beside a kept value of 0.95. It happens because the TARGET is a third
        entry and the other 2 are discarded."""
        registry.entries["C0003"] = _entry("C0003", 0.95)
        registry.entries["C0001"] = _entry("C0001", 0.35)
        registry.entries["C0002"] = _entry("C0002", 0.45)
        registry.resolve("C0001", "MERGED", 1, merged_into="C0003")
        registry.resolve("C0002", "MERGED", 1, merged_into="C0003")
        kept = registry.entries["C0003"]["severity"]
        assert kept == 0.95
        assert kept > max(0.35, 0.45), (
            "the kept value is now inside the range of its inputs, so an "
            "aggregation step exists and B39 is answered differently")

    def test_the_discarded_assessment_survives_on_its_own_entry(self, registry):
        """It is DISCARDED FROM THE KEPT VALUE, not deleted from the record --
        the distinction matters, because it means the inputs are recoverable and
        an aggregation step could be added later without losing evidence."""
        registry.entries["C0001"] = _entry("C0001", 0.35)
        registry.entries["C0002"] = _entry("C0002", 0.45)
        registry.resolve("C0002", "MERGED", 1, merged_into="C0001")
        assert registry.entries["C0002"]["severity"] == 0.45
        assert registry.entries["C0002"]["status"] == "MERGED"

    def test_the_target_records_nothing_about_the_merge(self, registry):
        registry.entries["C0001"] = _entry("C0001", 0.35)
        registry.entries["C0002"] = _entry("C0002", 0.45)
        before = set(registry.entries["C0001"])
        registry.resolve("C0002", "MERGED", 1, merged_into="C0001")
        gained = sorted(set(registry.entries["C0001"]) - before)
        assert not [k for k in gained if "sever" in k.lower()], (
            f"the target gained severity-related key(s) {gained} on merge")


class TestTheChokepointHasNoAggregationInIt:
    """STRUCTURAL, and said so. It complements the executed tests above by
    showing the absence is in the code rather than only in these 5 cases."""

    def test_resolve_contains_no_aggregation_call(self):
        tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
        fn = None
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef) and n.name == "FindingRegistry":
                for m in n.body:
                    if isinstance(m, ast.FunctionDef) and m.name == "resolve":
                        fn = m
        assert fn is not None, "FindingRegistry.resolve has moved"
        called = set()
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
                called.add(n.func.id)
        aggregates = called & {"max", "min", "median", "mean", "fmean", "sum"}
        assert not aggregates, (
            f"resolve now calls {sorted(aggregates)}; if that is an aggregation "
            f"over merged assessments, B39's finding is superseded and this "
            f"file's premise must be re-derived")
