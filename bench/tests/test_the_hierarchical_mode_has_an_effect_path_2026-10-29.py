"""The hierarchical novelty mode has an effect path, and it is witnessable (B33).

HIS RULING, 2026-10-19: *"Verdict option 1"* -- WIRE THE MODE so it does what its
report field claims. Retiring it and renaming the field were both rejected by
that choice.

WHAT WAS WRONG. The mode had 4 artefacts and 0 effect path: a config field, a
`mode_effects` slot, a published series and an `_is_gating` report field. Nothing
in the runner ever appended to its slot -- measured on the syntax tree, the only
appends were its sibling's and the severity spec's -- so the mode could not
operate however it was set, and it was the 1 INERT entry in `MODES`.

WHAT IS DELIBERATELY UNCHANGED. `hierarchical_crit_series_is_gating` still
carries the DECLARED value. B32 keeps the declaration and the observed effect
apart on purpose and B28 reconciles the 2, so making the field effect-derived
would collapse the comparison. The defect was that the OBSERVED side was
permanently empty, never that the declared side restated the flag.

HOW MUCH OF THIS IS EXECUTED, STATED PLAINLY RATHER THAN IMPLIED. The detector,
the series' whole-series behaviour and the end-to-end reconciliation are all
CALLED. The PRECEDENCE rule -- that the location substitution stands down when
the finer hierarchical rule is in force -- is asserted on the syntax tree,
because the substitution lives inside the runner's round loop and driving that
loop is not available to a unit test. That assertion is labelled structural
where it appears, and the executed proof is the simulated run, whose report will
carry `mode_effects.hierarchical_novelty_convergence` directly.

Written under CDSFL note standard v1.8.
"""
from __future__ import annotations

import ast
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.runner_mode_detection import (  # noqa: E402
    AGREE, INERT, MODES, SOUND, _hierarchical_operating, reconcile,
)

RUNNER = REPO / "bench" / "reference_runner_v3.py"
MODE = "hierarchical_novelty_convergence"


def _tree():
    return ast.parse(RUNNER.read_text(encoding="utf-8"))


class TestTheAnnotationMoved:
    def test_the_mode_is_no_longer_inert(self):
        m = {x.name: x for x in MODES}[MODE]
        assert m.soundness == SOUND, (
            f"{MODE} is annotated {m.soundness}; it was wired on his ruling of "
            f"2026-10-19 and an understated annotation is as wrong as an "
            f"overstated one")
        assert m.artefact == "mode_effects", (
            f"the artefact is still {m.artefact!r}; a detector reading "
            f"`..._is_gating` compares the flag with itself")

    def test_no_mode_is_inert_any_more(self):
        """ANTI-VACUITY for the sibling guard. `test_an_inert_mode_has_no_consumer`
        iterates only INERT modes, so once this is the last one to move that
        guard becomes vacuous -- which is correct, and recorded here so the
        vacuity is deliberate rather than unnoticed."""
        assert [m.name for m in MODES if m.soundness == INERT] == []


class TestTheDetectorReadsTheEffect:
    """EXECUTED. The old detector read a copy of the flag and could never
    disagree; this one must answer from the effect record."""

    @staticmethod
    def _report(rec):
        return {"_declared_config": {MODE: True}, "mode_effects": {MODE: rec}}

    def test_a_substituted_round_means_operating(self):
        got = _hierarchical_operating(
            self._report({"substituted": [1, 2], "fell_back": []}))
        assert got is True

    def test_asked_for_and_never_substituted_is_not_operating(self):
        got = _hierarchical_operating(
            self._report({"substituted": [], "fell_back": []}))
        assert got is False, (
            "a mode that substituted in NO round did not operate, however it "
            "was declared")

    def test_fell_back_every_round_is_not_operating(self):
        got = _hierarchical_operating(
            self._report({"substituted": [], "fell_back": [2, 3]}))
        assert got is False

    def test_a_missing_record_is_undecidable_not_false(self):
        assert _hierarchical_operating(
            {"_declared_config": {MODE: True}, "mode_effects": {}}) is None, (
            "an absent effect record is UNDECIDABLE; returning False would "
            "report a mode broken when nothing was measured")

    def test_it_does_not_read_the_circular_field(self):
        """The decisive difference from the old detector: a report carrying ONLY
        `..._is_gating` must still be undecidable."""
        assert _hierarchical_operating(
            {"_declared_config": {MODE: True},
             "hierarchical_crit_series_is_gating": True}) is None


class TestTheReconciliationWitnessesIt:
    """END TO END through the real `reconcile`, which is what B28 consumes."""

    def test_a_declared_and_substituted_mode_agrees(self):
        report = {"_declared_config": {MODE: True},
                  "mode_effects": {MODE: {"substituted": [0, 1], "fell_back": []}}}
        found = {f.mode: f for f in reconcile(report)}
        assert found[MODE].verdict == AGREE, (
            f"declared True and substituted in 2 rounds, yet reconcile says "
            f"{found[MODE].verdict}")

    def test_a_declared_mode_that_never_substituted_does_not_agree(self):
        report = {"_declared_config": {MODE: True},
                  "mode_effects": {MODE: {"substituted": [], "fell_back": [0, 1]}}}
        found = {f.mode: f for f in reconcile(report)}
        assert found[MODE].verdict != AGREE, (
            "a mode asked for that fell back every round must not read as "
            "agreeing; that is the silent downgrade B28 exists to catch")


def _ent(i, desc, rnd, status="CONFIRMED", severity=0.9):
    return {"canonical_id": i, "id": i, "description": desc,
            "severity": severity, "open_since_round": rnd, "status": status}


SYMS = ["alpha", "beta", "gamma"]
BASE = [_ent("A", "a fault in alpha()", 0), _ent("B", "a fault in beta()", 1)]


class TestTheSeriesTheGateWouldNowRead:
    """EXECUTED, and every expected value here was MEASURED before it was
    written down rather than predicted.

    A first draft of this class asserted `first == first[:]`, which is vacuous,
    and its fixtures used `status="UNCONFIRMED"` -- a status `_gate_population`
    EXCLUDES -- so every series came back `[0, 0, 0]` and every comparison
    passed trivially. Running the function is what exposed both faults. The
    expected values below are what `hierarchical_novelty_series` actually
    returns.
    """

    @staticmethod
    def _series(entries, max_round=2, syms=None):
        from bench.convergence_location import hierarchical_novelty_series
        return hierarchical_novelty_series(entries, max_round, syms or SYMS)

    def test_the_baseline_counts_each_new_location_once(self):
        assert self._series(BASE) == [1, 1, 0]

    def test_a_refind_in_the_same_round_is_not_novel(self):
        got = self._series(BASE + [_ent("C", "a fault in alpha()", 0)])
        assert got == [1, 1, 0], f"a re-find inflated the series: {got}"

    def test_a_refind_in_a_LATER_round_does_not_reset_the_streak(self):
        """THE WHOLE REASON THE MODE EXISTS, and the reason wiring it matters.

        A defect re-found under a fresh model id in a later round must NOT
        count as new, because the ID-proxy series counts it and thereby resets
        the zero-streak the convergence gate reads -- the cross-round dedup
        failure. Round 2 stays 0."""
        got = self._series(BASE + [_ent("E", "a fault in alpha()", 2)])
        assert got == [1, 1, 0], (
            f"a re-found defect counted as new in round 2: {got}. Gating on this "
            f"series would reset the quiet streak, which is the failure the mode "
            f"is meant to fix")

    def test_a_genuinely_new_location_does_count(self):
        """ANTI-VACUITY. Without this the test above would pass on a series that
        is always zero."""
        got = self._series(BASE + [_ent("D", "a fault in gamma()", 2)])
        assert got == [1, 1, 1], f"a new location was missed: {got}"

    def test_an_excluded_prior_does_not_flag_its_location(self):
        """The `_gate_population` defect of 2026-08-12, kept checkable: an
        UNCONFIRMED round-0 finding must not flag gamma, or the genuine round-2
        critical there would be merged away and round 2 would read 0."""
        got = self._series(BASE + [
            _ent("F", "a fault in gamma()", 0, status="UNCONFIRMED"),
            _ent("G", "a fault in gamma()", 2)])
        assert got == [1, 1, 1], (
            f"an excluded prior flagged its location, hiding the real finding: "
            f"{got}")

    def test_a_sub_threshold_finding_is_not_critical(self):
        got = self._series(BASE + [
            _ent("H", "a fault in gamma()", 2, severity=0.5)])
        assert got == [1, 1, 0], f"a 0.5-severity finding was counted: {got}"


class TestPrecedence:
    """STRUCTURAL, AND SAID SO. The substitution is inside the runner's round
    loop, which a unit test cannot drive; the executed proof is the simulated
    run's `mode_effects`."""

    def test_the_location_substitution_stands_down_for_the_finer_rule(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert "_hier_gates" in src, "the precedence flag is absent"
        assert "_gates and not _hier_gates" in src, (
            "the location substitution is not guarded against the hierarchical "
            "rule, so with both modes declared both would write the gate's "
            "input and the later write would win silently -- leaving "
            "mode_effects.location_keyed_convergence recording a substitution "
            "that did not survive the round")

    def test_the_mode_appends_to_its_own_effect_slot(self):
        """The append that did not exist before 2026-10-29."""
        tree = _tree()
        appends = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "append"):
                tgt = ast.unparse(node.func.value)
                if MODE in tgt and "mode_effects" in tgt:
                    appends.append(node.lineno)
        assert appends, (
            f"nothing appends to mode_effects[{MODE!r}], so the mode still has "
            f"no effect path and the detector can only ever return None")
