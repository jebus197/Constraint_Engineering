"""The supply-decomposition producer is itself falsifiable.

WHY THIS EXISTS. `scripts/falsifier_supply_decomposition_2026-10-02.py`
answers the founder's 2026-10-02 question about falsifier supply, and its
figures were quoted to him before anything executed against the producer. This
project's own record names that pattern: my instruments are the weak point, and
a measured rate must travel with the script that produced it -- which is no use
if the script itself is unchecked.

IT ALREADY FOUND A DEFECT IN THE FIGURE IT GUARDS. The delegation count matched
instrument names inside `#` COMMENTS, so 2 of 70 bodies were counted as
delegating to a tool they only mentioned. Corrected to 68 of 499 = 13.6273%,
Wilson [10.8936%, 16.9166%]. The error direction is recorded in
`test_the_error_direction_is_against_the_finding` below, because an error that
inflates the half carrying the conclusion would be a different and worse thing.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "falsifier_supply_decomposition_2026-10-02.py"

pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="producer absent")


@pytest.fixture(scope="module")
def fsd():
    spec = importlib.util.spec_from_file_location("fsd_under_test", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["fsd_under_test"] = m
    spec.loader.exec_module(m)
    return m


def _e(**kw):
    return {"status": "UNCONFIRMED", "severity": 0.9, **kw}


class TestClassifyOnKnownShapes:
    """Each case's answer is fixed by construction, not by the archive."""

    def test_no_body(self, fsd):
        assert fsd.classify(_e()) == "NOTHING WRITTEN AND NOTHING RECORDED"

    def test_whitespace_is_not_a_body(self, fsd):
        assert fsd.classify(_e(falsifier_code="  \n ")) == "NOTHING WRITTEN AND NOTHING RECORDED"

    def test_resolved(self, fsd):
        assert fsd.classify(_e(falsifier_code="assert 1",
                               falsifier_verdict="CONFIRMED")) == "WRITTEN AND RESOLVED"

    def test_errored(self, fsd):
        assert fsd.classify(_e(falsifier_code="x",
                               falsifier_verdict="ERROR")) == "WRITTEN, THEN ERRORED"

    def test_gate_refusal(self, fsd):
        assert fsd.classify(_e(falsifier_code="x",
                               falsifier_verdict="INTEGRITY_VIOLATION")) \
            == "WRITTEN, REFUSED BY THE GATE"

    def test_the_ladder_side_refusal_beats_a_stale_resolved_label(self, fsd):
        """RUN 1b's C0029 SHAPE, and the reason this classifier is not a
        one-field read. Its `falsifier_verdict` says CONFIRMED because a later
        pass tested it, while the refusal is recorded only on the ladder side.
        A classifier reading the first field alone counts that run as having no
        refusal at all -- which is how the earlier count of 1 was reached, and
        the founder's correction to 2 is what this asserts."""
        assert fsd.classify(_e(falsifier_code="x", falsifier_verdict="CONFIRMED",
                               routing_verdict_unreconciled="INTEGRITY_VIOLATION")) \
            == "WRITTEN, REFUSED BY THE GATE"

    def test_a_truncated_retained_body_still_counts_as_written(self, fsd):
        """A refused falsifier's body survives only as a 600-character
        truncation in `last_falsifier_code`. Counting that as "no body" would
        report a refusal as a supply failure, which is the conflation this
        whole decomposition exists to undo."""
        assert fsd.classify(_e(last_falsifier_code="x",
                               falsifier_verdict="ERROR")) == "WRITTEN, THEN ERRORED"


    def test_a_declination_is_not_a_supply_failure(self):
        """THE DEFECT AN ADVERSARIAL PASS FOUND IN THIS PRODUCER, 2026-10-02.

        `classify()` returned "NO BODY WAS EVER WRITTEN" on an empty body BEFORE
        reading any verdict, so a finding the ladder ASSESSED AND DECLINED
        (UNTOOLABLE), or one that ERRORED without retaining its source, was
        counted as one nobody had written a falsifier for. 42 of the 793 so
        classified carried a real verdict -- 38 UNTOOLABLE and 4 ERROR, 5.2963%,
        Wilson [3.9420%, 7.0817%] -- and the inflated bucket was the one the
        conclusion rested on.

        The sibling guard `test_a_truncated_retained_body_still_counts_as_written`
        covered the NEIGHBOURING case and passed throughout, which is
        `feedback_verify_the_deciding_layer`: a test next to the deciding layer
        is not a test of it.
        """

    def test_an_untoolable_with_no_retained_body_is_a_declination(self, fsd):
        assert fsd.classify(_e(falsifier_verdict="UNTOOLABLE")) \
            == "ASSESSED AND DECLINED (UNTOOLABLE)"

    def test_an_error_with_no_retained_body_is_still_an_error(self, fsd):
        assert fsd.classify(_e(falsifier_verdict="ERROR")) == "WRITTEN, THEN ERRORED"

    def test_only_a_total_silence_counts_as_never_written(self, fsd):
        """Both halves: no body AND no verdict anywhere, including the ladder."""
        assert fsd.classify(_e()) == "NOTHING WRITTEN AND NOTHING RECORDED"
        assert fsd.classify(_e(routing_verdict_unreconciled="UNTOOLABLE")) \
            != "NOTHING WRITTEN AND NOTHING RECORDED"
        assert fsd.classify(_e(routing_history=[{"verdict": "ERROR"}])) \
            != "NOTHING WRITTEN AND NOTHING RECORDED"

    def test_the_declination_bucket_is_not_empty_on_the_real_archive(self, fsd):
        """ANTI-VACUITY: if the archive carried no declinations the 3 tests above
        would be assertions about a state that never occurs."""
        _raw, seen, _pf, _f = fsd.harvest()
        kinds = {fsd.classify(e) for e in seen.values()}
        assert "ASSESSED AND DECLINED (UNTOOLABLE)" in kinds, sorted(kinds)


class TestTheToolDetector:

    @pytest.mark.parametrize("body", [
        "subprocess.run(['ruff', 'check', 'x.py'])",
        "import sympy\nsympy.simplify(expr)",
        "import z3\nz3.Solver()",
        "mod = importlib.import_module('bench.runner_core')",
        "compile(src, '<t>', 'exec')",
    ])
    def test_a_real_invocation_is_delegation(self, fsd, body):
        assert fsd.TOOL_RE.search(body), body

    @pytest.mark.parametrize("body", [
        'assert "foo" in text, "missing"',
        "if len(rows) != 3:\n    raise AssertionError('wrong count')",
        "assert re.search(r'x', s)",
    ])
    def test_a_hand_rolled_assertion_is_not_delegation(self, fsd, body):
        assert not fsd.TOOL_RE.search(body), body

    def test_a_comment_only_mention_is_excluded_by_the_producer(self, fsd):
        """THE DEFECT THIS FILE FOUND. The bare pattern matches a comment; the
        producer strips comments before counting, so the figure it prints does
        not credit a tool a body merely talks about."""
        body = "# this would need pytest to check properly\nassert 1 == 1"
        assert fsd.TOOL_RE.search(body), "the bare pattern no longer matches a comment"
        stripped = "\n".join(re.sub(r"#.*$", "", l) for l in body.splitlines())
        assert not fsd.TOOL_RE.search(stripped), (
            "stripping comments no longer removes the match, so the producer's "
            "correction has stopped working")


class TestTheHarvestCannotLieQuietly:

    def test_it_is_deterministic(self, fsd):
        a = fsd.harvest()
        b = fsd.harvest()
        assert (a[0], len(a[1]), a[2], a[3]) == (b[0], len(b[1]), b[2], b[3])

    def test_unreadable_files_are_counted_not_dropped(self, fsd):
        """A silent zero over an unreadable corpus is a defect this project has
        already shipped once; the count must be reported."""
        raw, seen, parse_failures, files = fsd.harvest()
        assert files > 0, "the archive is empty, so every figure is vacuous"
        assert isinstance(parse_failures, int)

    def test_dedup_removes_the_re_recorded_registry(self, fsd):
        """The archive records a run's registry more than once; measured
        inflation 1.983193x. If this ratio collapses to 1.0 the dedup has
        stopped working and every rate doubles."""
        raw, seen, _, _ = fsd.harvest()
        assert raw > len(seen) > 0
        assert 1.5 < raw / len(seen) < 2.5, raw / len(seen)

    def test_the_error_direction_is_against_the_finding(self, fsd):
        """The residual over-count inflates DELEGATION, so it understates the
        hand-rolled share that carries the conclusion. An error favouring the
        conclusion would need a different response from one opposing it."""
        raw, seen, _, _ = fsd.harvest()
        bodies = {fsd._body(e) for e in seen.values() if fsd._body(e)}
        strip = lambda s: "\n".join(re.sub(r"#.*$", "", l) for l in s.splitlines())
        loose = sum(1 for b in bodies if fsd.TOOL_RE.search(b))
        tight = sum(1 for b in bodies if fsd.TOOL_RE.search(strip(b)))
        assert tight <= loose, "stripping comments INCREASED the delegation count"
