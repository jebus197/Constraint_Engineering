"""The execution-based duplicate matcher, run BESIDE the text matcher it may replace.

WHY THESE TESTS LOOK LIKE THIS
------------------------------
Item D8 changes how findings are matched. That is behavioural, so a test suite
that only proved the new matcher self-consistent would prove nothing anybody
needs to know. Every decision test here therefore runs BOTH matchers on the SAME
inputs and compares, and the suite deliberately contains pairs where the two
DISAGREE -- in both directions. An agreement-only suite would be green on the
day the switch was thrown and silent about what the switch did.

The findings under test are real defects in a real (tiny) module, and every
verdict below comes from actually running the falsifiers in the sandbox. Nothing
here asserts on the SOURCE TEXT of `bench/execution_based_matcher.py`: that would
only establish that the module describes itself consistently, which is the
failure mode `execute-do-not-grep` was ruled against after
`boundary_band_sensitivity` shipped as an unconditional constant and its
source-text guard passed all 8 of its assertions.

EVERY GUARD IS SHOWN TO CHANGE AN ANSWER. A guard whose removal changes nothing
is decoration, and this project has already shipped one. So the equipment-failure
refusal is paired with the same pair decided cleanly (`SAME`) once the broken
column is gone; the witness requirement is paired with a constant executor under
which an equality-only rule would return `SAME` for everything; and the
verdict's dependence on execution is shown by an executor that stops
distinguishing the falsifiers, which makes `DIFFERENT` disappear.

THE SYNTHETIC TARGET
--------------------
`pkg/widget.py` carries two INDEPENDENT one-line arithmetic defects, `scale`
(triples where it should double) and `offset` (adds 5 where it should add 1).
Two independent defects in one small file is exactly the configuration a text
matcher gets wrong, because the two are described in almost the same words.
"""

import hashlib
import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.execution_based_matcher import (            # noqa: E402
    DIFFERENT,
    SAME,
    UNDECIDED,
    Candidate,
    ExecutionBasedMatcher,
    compare_matchers,
    text_similarity,
    text_verdict,
)

TARGET_REL = "pkg/widget.py"
PRISTINE = (
    "def scale(x):\n"
    "    return x * 3\n"
    "\n"
    "\n"
    "def offset(x):\n"
    "    return x + 5\n"
)


def _falsifier(fn: str, arg: int, want: int) -> str:
    """A falsifier that IMPORTS the real target and asserts on what it returns."""
    return (
        f"from pkg.widget import {fn}\n"
        f"assert {fn}({arg}) == {want}, 'wrong result'\n"
    )


def _fix(old: str, new: str) -> str:
    """A SEARCH/REPLACE block in the form the runner emits and `_apply_fix_to_source` parses."""
    return f"<<<< SEARCH\n    {old}\n====\n    {new}\n>>>>\n"


# The two descriptions that make the text matcher wrong, and the one that makes
# it wrong the other way. A and B describe DIFFERENT defects in near-identical
# words; C describes the SAME defect as A in words sharing nothing with it.
DESC_A = ("The scale helper returns the wrong number for its input because the "
          "arithmetic constant in its one line body is wrong, so every caller "
          "downstream receives a wrong value.")
DESC_B = ("The offset helper returns the wrong number for its input because the "
          "arithmetic constant in its one line body is wrong, so every caller "
          "downstream receives a wrong value.")
DESC_C = "Multiplication factor mistaken; doubling expected, tripling delivered."


def _candidates() -> dict:
    return {
        # A and C are the SAME defect (scale), repaired two different ways.
        "A": Candidate("A", _falsifier("scale", 2, 4),
                       _fix("return x * 3", "return x * 2"), DESC_A, 1),
        "C": Candidate("C", _falsifier("scale", 1, 2),
                       _fix("return x * 3", "return 2 * x"), DESC_C, 2),
        # B is a DIFFERENT defect (offset) described almost exactly like A.
        "B": Candidate("B", _falsifier("offset", 0, 1),
                       _fix("return x + 5", "return x + 1"), DESC_B, 1),
        # D's falsifier PASSES on the pristine target: it never reproduced.
        "D": Candidate("D", _falsifier("scale", 1, 3),
                       _fix("return x + 5", "return x + 1"), DESC_A, 1),
        # E and F carry no proposed fix at all, so neither mints a state.
        "E": Candidate("E", _falsifier("offset", 1, 2), "", DESC_B, 1),
        "F": Candidate("F", _falsifier("scale", 3, 6), "", DESC_A, 1),
        # G is a real finding about scale whose "repair" makes the function
        # raise. Every scale falsifier ERRORs on G's column -- a genuine,
        # executed equipment failure, not a simulated one.
        "G": Candidate("G", _falsifier("scale", 4, 8),
                       _fix("return x * 3", 'raise RuntimeError("scale unavailable")'),
                       DESC_A, 1),
        # H and I are about scale; their fixes APPLY but repair offset, so
        # nothing in their columns ever moves.
        "H": Candidate("H", _falsifier("scale", 5, 10),
                       _fix("return x + 5", "return x + 4"), DESC_A, 1),
        "I": Candidate("I", _falsifier("scale", 6, 12),
                       _fix("return x + 5", "return x + 6"), DESC_A, 1),
    }


@pytest.fixture(scope="module")
def repo(tmp_path_factory):
    root = tmp_path_factory.mktemp("ebm_repo")
    (root / "pkg").mkdir()
    (root / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    (root / TARGET_REL).write_text(PRISTINE, encoding="utf-8")
    return root


@pytest.fixture(scope="module")
def profiled(repo):
    """One profile over every candidate. The expensive pass runs ONCE.

    That is the shape of the design under test: N findings and up to N+1 target
    states are executed once, and every pair verdict is then a slice. The
    pairwise script this method comes from re-ran falsifiers per pair.
    """
    cands = _candidates()
    matcher = ExecutionBasedMatcher(repo, TARGET_REL, enabled=True, timeout=15)
    profile = matcher.profile(list(cands.values()), PRISTINE)
    return matcher, profile, cands


# ─────────────────────────────────────────────────────────────────────────────
# BOTH MATCHERS, SAME INPUTS. This is the point of the file.


class TestTheTwoMatchersSideBySide:

    def test_they_disagree_in_both_directions_on_the_same_three_findings(self, profiled):
        matcher, profile, cands = profiled
        report = compare_matchers(
            matcher, profile, [cands["A"], cands["B"], cands["C"]],
            pairs=[("A", "B"), ("A", "C"), ("B", "C")],
        )
        rows = {(r.a, r.b): r for r in report.rows}

        # A and B are two DIFFERENT defects. Execution proves it -- each
        # survives the other's repair. The text matcher merges them, because
        # they are described in almost the same words.
        assert rows[("A", "B")].execution == DIFFERENT
        assert rows[("A", "B")].text == SAME

        # A and C are ONE defect repaired two ways. Execution proves it -- each
        # repair cures both falsifiers. The text matcher splits them, because
        # the two descriptions share almost no vocabulary.
        assert rows[("A", "C")].execution == SAME
        assert rows[("A", "C")].text == DIFFERENT

        # And they do agree somewhere, so this is a disagreement measurement
        # and not a matcher that simply inverts the incumbent.
        assert rows[("B", "C")].execution == DIFFERENT
        assert rows[("B", "C")].text == DIFFERENT

        assert report.counts() == {
            "pairs": 3,
            "execution_decided": 3,
            "agree": 1,
            "disagree": 2,
            "text_merges_what_execution_separates": 1,
            "text_separates_what_execution_merges": 1,
        }

    def test_the_disagreement_survives_either_similarity_backend(self, profiled):
        """The incumbent has two backends; the disagreement must not be an
        artefact of which one loaded.

        `finding_similarity` prefers sentence-transformer cosine and falls back
        to unigram/bigram Jaccard when the model is absent. Both are CALLED
        here, on the same pair objects the comparison used, because a
        disagreement that existed only under one backend would be a fact about
        this machine's huggingface cache.
        """
        from bench.dm._similarity import jaccard_similarity
        from bench.dm._types import Finding

        _matcher, _profile, cands = profiled

        def _f(c):
            return Finding(c.finding_id, "m", 0, c.flaw_class, 0.8, 0.0,
                           description=c.description)

        for a, b, above in (("A", "B", True), ("A", "C", False)):
            live = text_similarity(cands[a], cands[b])
            lex = jaccard_similarity(_f(cands[a]), _f(cands[b]))
            assert (live >= 0.50) is above, (a, b, live)
            assert (lex >= 0.50) is above, (a, b, lex)


# ─────────────────────────────────────────────────────────────────────────────
# The execution decision itself.


class TestExecutionDecides:

    def test_a_repair_that_cures_both_makes_them_one_defect(self, profiled):
        matcher, profile, _ = profiled
        v = matcher.match(profile, "A", "C")
        assert (v.verdict, v.reason) == (SAME, "shared_repair")
        # Both repairs are witnesses: each flipped BOTH falsifiers.
        assert set(v.witness) == {"fix:A", "fix:C"}
        assert v.vector_a == v.vector_b == ("CONFIRMED", "REFUTED", "REFUTED")

    def test_a_defect_that_survives_the_other_repair_is_a_second_defect(self, profiled):
        matcher, profile, _ = profiled
        v = matcher.match(profile, "A", "B")
        assert (v.verdict, v.reason) == (DIFFERENT, "surviving_repair")
        assert v.vector_a == ("CONFIRMED", "REFUTED", "CONFIRMED")
        assert v.vector_b == ("CONFIRMED", "CONFIRMED", "REFUTED")

    def test_rewriting_the_prose_moves_the_text_verdict_and_not_the_execution_verdict(
            self, repo, profiled):
        """The claim of the whole module, made falsifiable.

        A's description is replaced with B's, character for character. The text
        matcher must move (it now sees one finding twice); the execution verdict
        must not, because nothing either falsifier DOES has changed.
        """
        matcher, profile, cands = profiled
        before_text = text_verdict(cands["A"], cands["B"])
        before_exec = matcher.match(profile, "A", "B").verdict

        twin = Candidate("A", cands["A"].falsifier_code, cands["A"].proposed_fix,
                         DESC_B, cands["B"].flaw_class)
        after_text = text_verdict(twin, cands["B"])
        # Same falsifier, same fix -> the profile is unchanged, so the execution
        # verdict is read from the very same matrix.
        after_exec = matcher.match(profile, "A", "B").verdict

        assert before_exec == after_exec == DIFFERENT
        assert after_text == SAME
        assert text_similarity(twin, cands["B"]) > text_similarity(
            cands["A"], cands["B"])
        assert before_text == SAME     # it was already merging them

    def test_changing_what_the_falsifier_tests_moves_the_execution_verdict(self, repo):
        """The other half of the same claim: execution is not inert either.

        B keeps its description, its flaw class and its `offset` repair, and its
        FALSIFIER is pointed at `scale` -- the defect A raised. Nothing a text
        matcher can see has moved, so its verdict is unchanged; the execution
        verdict goes from DIFFERENT to SAME, because A's repair now settles
        both.

        A FIRST VERSION OF THIS TEST ASSERTED THE WRONG THING and is recorded
        because the module was right and the test was wrong. It widened A's FIX
        to repair `offset` as well and expected SAME. The matcher returned
        DIFFERENT, correctly: A's `scale` defect still survives B's repair, so
        they are still two defects. A fix that cures more is not two findings
        becoming one.
        """
        cands = _candidates()
        twin = Candidate("B", _falsifier("scale", 7, 14), cands["B"].proposed_fix,
                         cands["B"].description, cands["B"].flaw_class)
        matcher = ExecutionBasedMatcher(repo, TARGET_REL, enabled=True, timeout=15)
        profile = matcher.profile([cands["A"], twin], PRISTINE)

        assert matcher.match(profile, "A", "B").verdict == SAME
        # Held constant, and shown to be held constant.
        assert twin.description == cands["B"].description
        assert twin.proposed_fix == cands["B"].proposed_fix
        assert text_verdict(cands["A"], twin) == text_verdict(cands["A"], cands["B"])


# ─────────────────────────────────────────────────────────────────────────────
# Every guard, shown to change an answer.


class TestTheGuardsAreLoadBearing:

    def test_equipment_failure_refuses_the_verdict_the_clean_columns_would_give(
            self, repo, profiled):
        """G's own repair makes `scale` raise, so its column is ERROR for both.

        The pair is refused. Remove only the broken column -- same two findings,
        same falsifiers, same baseline -- and it decides SAME. That difference
        IS the guard; without it an instrument failure would have produced a
        merge.
        """
        matcher, profile, cands = profiled
        refused = matcher.match(profile, "A", "G")
        assert (refused.verdict, refused.reason) == (UNDECIDED, "equipment_failure")
        assert "ERROR" in refused.vector_a and "ERROR" in refused.vector_b

        unbroken = Candidate("G", cands["G"].falsifier_code, "", DESC_A, 1)
        m2 = ExecutionBasedMatcher(repo, TARGET_REL, enabled=True, timeout=15)
        p2 = m2.profile([cands["A"], unbroken], PRISTINE)
        assert m2.match(p2, "A", "G").verdict == SAME

    def test_agreement_with_nothing_moving_is_not_identity(self, profiled):
        """H and I have IDENTICAL vectors and are still not called the same.

        Their repairs apply and mend the wrong function, so both falsifiers
        CONFIRM on every column. An equality-only rule returns SAME here. The
        witness clause is the difference between a matcher and a constant.
        """
        matcher, profile, _ = profiled
        v = matcher.match(profile, "H", "I")
        assert v.vector_a == v.vector_b        # equality alone would say SAME
        assert (v.verdict, v.reason) == (UNDECIDED, "no_witness")
        assert set(v.vector_a) == {"CONFIRMED"}

    def test_a_constant_executor_can_never_yield_SAME(self, repo):
        """Substitute the executor with a stub that always says CONFIRMED.

        This is the substitution check the project ruled after three tests were
        found passing with the model replaced by the constant 42. If the
        matcher were reading anything but execution, or if the witness clause
        were absent, this profile -- in which every vector is identical --
        would be merged wholesale.
        """
        cands = _candidates()
        calls = []

        def always_confirmed(code, repo_root=None, timeout=None):
            calls.append(code)
            return "CONFIRMED"

        matcher = ExecutionBasedMatcher(repo, TARGET_REL, enabled=True,
                                        reverify=always_confirmed)
        profile = matcher.profile(list(cands.values()), PRISTINE)
        verdicts = matcher.match_all(profile)
        assert calls, "the stub was never reached"
        assert {v.verdict for v in verdicts} == {UNDECIDED}
        # `no_witness` must be the reason for the pairs that HAVE columns; the
        # rest are the two candidates carrying no fix, refused earlier. Asserted
        # as a partition rather than a single value so the test says which guard
        # refused which pair.
        assert {v.reason for v in verdicts} == {"no_witness", "no_applicable_fix"}
        # 9 candidates, so 36 pairs. Exactly one of them (E, F) has no fix on
        # either side and is refused for want of a column; the other 35 reach
        # the witness clause and are refused there.
        witnessless = [v for v in verdicts if v.reason == "no_witness"]
        assert (len(verdicts), len(witnessless)) == (36, 35)
        assert all(len(set(v.vector_a)) == 1 for v in witnessless)

    def test_an_executor_that_ignores_the_falsifier_loses_the_DIFFERENT_verdict(
            self, repo):
        """Answer from the target state alone and A/B stops being two defects.

        The stub reads the overlay's copy of the target and replies CONFIRMED on
        the pristine text, REFUTED on anything else -- identically for every
        candidate. All vectors collapse to one, so A and B become SAME. The real
        matcher calls them DIFFERENT, and this is where that verdict comes from:
        running each falsifier, not comparing anything about them.
        """
        cands = _candidates()

        def state_only(code, repo_root=None, timeout=None):
            seen = (Path(repo_root) / TARGET_REL).read_text(encoding="utf-8")
            return "CONFIRMED" if seen == PRISTINE else "REFUTED"

        matcher = ExecutionBasedMatcher(repo, TARGET_REL, enabled=True,
                                        reverify=state_only)
        profile = matcher.profile([cands["A"], cands["B"]], PRISTINE)
        assert matcher.match(profile, "A", "B").verdict == SAME

    def test_a_falsifier_that_never_fired_on_the_pristine_target_decides_nothing(
            self, profiled):
        """D passes on the unmodified file, so it reproduced no defect.

        Its repaired columns nonetheless mirror A's exactly, inverted -- which
        is what a SAME pattern looks like to a rule that skips the baseline
        check. The refusal is the baseline requirement doing work.
        """
        matcher, profile, _ = profiled
        v = matcher.match(profile, "A", "D")
        assert (v.verdict, v.reason) == (UNDECIDED, "no_baseline")
        assert v.vector_b[0] == "REFUTED"
        # Something DID move in D's columns -- the refusal is not for want of a
        # witness, it is for want of a reproduction.
        assert len(set(v.vector_b)) > 1

    def test_two_findings_with_no_applicable_fix_mint_no_columns(self, profiled):
        matcher, profile, _ = profiled
        v = matcher.match(profile, "E", "F")
        assert (v.verdict, v.reason) == (UNDECIDED, "no_applicable_fix")
        assert v.columns == ("pristine",)
        assert profile.skipped["E"] == "no_proposed_fix"
        assert profile.skipped["F"] == "no_proposed_fix"


# ─────────────────────────────────────────────────────────────────────────────
# Default off, and the repository is never written to.


class TestDefaultOffAndRepositorySafety:

    def test_disabled_runs_no_falsifier_at_all(self, repo):
        """Off means nothing executes -- not "executes and is discarded"."""
        calls = []

        def spy(code, repo_root=None, timeout=None):
            calls.append(code)
            return "CONFIRMED"

        cands = _candidates()
        matcher = ExecutionBasedMatcher(repo, TARGET_REL, reverify=spy)
        assert matcher.enabled is False          # the constructor default
        profile = matcher.profile(list(cands.values()), PRISTINE)
        assert calls == []
        assert profile.executions == 0
        assert profile.states == ()
        v = matcher.match(profile, "A", "B")
        assert (v.verdict, v.reason) == (UNDECIDED, "disabled")

    def test_the_target_is_byte_identical_afterwards(self, repo, profiled):
        assert (repo / TARGET_REL).read_text(encoding="utf-8") == PRISTINE

    def test_no_overlay_survives_the_profile(self, repo, tmp_path, monkeypatch):
        """Every probe overlay is torn down, and the check can SEE a leak.

        THE FIRST VERSION OF THIS TEST WATCHED THE SHARED SYSTEM TEMP DIRECTORY
        and is recorded because it flaked within an hour of being written. The
        overlay builder names its directories `cdsfl_disc_*` there, and so does
        the runner's discrimination control -- so ANY other process on this
        machine creating one during the profile failed this assertion and
        blamed this module for a directory it never made. Reproduced
        deliberately: with a second process minting `cdsfl_disc_*` at 0.4 s
        intervals the test fails every time, with the matcher behaving
        perfectly. A test that reports a defect nobody committed is a false
        alarm, and this project has already absorbed 92 of those from the
        macrophage.

        `tempfile.tempdir` is redirected instead, so the observation covers
        this process's overlays and nothing else.
        """
        private = tmp_path / "tmp"
        private.mkdir()
        monkeypatch.setattr(tempfile, "tempdir", str(private))
        cands = _candidates()

        matcher = ExecutionBasedMatcher(repo, TARGET_REL, enabled=True, timeout=15)
        matcher.profile([cands["A"], cands["B"]], PRISTINE)
        assert list(private.glob("cdsfl_disc_*")) == []

        # And the check is not vacuous: with teardown disabled the same profile
        # leaves overlays behind, and this assertion sees them.
        class _NoTeardown:
            @staticmethod
            def rmtree(*_a, **_k):
                return None

        monkeypatch.setattr("bench.execution_based_matcher.shutil", _NoTeardown)
        leaky = ExecutionBasedMatcher(repo, TARGET_REL, enabled=True, timeout=15)
        leaky.profile([cands["A"], cands["B"]], PRISTINE)
        assert list(private.glob("cdsfl_disc_*"))

    def test_a_mutating_executor_is_caught_and_named(self, repo):
        """The no-write guarantee is MEASURED, not asserted in a docstring.

        Other agents edit this repository while a run is in flight, so a silent
        breach would corrupt a file somebody else is holding. The executor here
        writes to the real target; `profile()` must raise and name the path.
        """
        def vandal(code, repo_root=None, timeout=None):
            (repo / TARGET_REL).write_text("def scale(x):\n    return 0\n",
                                           encoding="utf-8")
            return "CONFIRMED"

        cands = _candidates()
        matcher = ExecutionBasedMatcher(repo, TARGET_REL, enabled=True,
                                        reverify=vandal)
        try:
            with pytest.raises(RuntimeError, match=r"mutated the repository"):
                matcher.profile([cands["A"]], PRISTINE)
        finally:
            (repo / TARGET_REL).write_text(PRISTINE, encoding="utf-8")


# ─────────────────────────────────────────────────────────────────────────────
# The archive. Real findings, real falsifiers, real repository code.

EXP44_REPORT = next(
    (p for p in (REPO / "bench" / "logs").glob(
        "exp44_evidence_locationkey_live_*/exp44_evidence_locationkey_live_report.json")
     if ".errata" not in str(p)), None)
EXP44_TARGET = REPO / "bench" / "evidence.py"
# The content the figures in `execution_based_matcher.__doc__` were measured
# against. The exp44 falsifiers import this file, so a different file is a
# different measurement; the test disarms rather than reporting a false alarm.
EXP44_TARGET_SHA = "731ff271983e30fcdcdb9cacc4e5823f9a0b013ea7d51012aa7b7e530919cd70"


def _exp44_unchanged() -> bool:
    if not (EXP44_REPORT and EXP44_TARGET.is_file()):
        return False
    return hashlib.sha256(
        EXP44_TARGET.read_bytes()).hexdigest() == EXP44_TARGET_SHA


@pytest.mark.skipif(
    not _exp44_unchanged(),
    reason="exp44 archive absent, or bench/evidence.py is not the content the "
           "recorded figures were measured against",
)
class TestTheArchiveMeasurementReproduces:
    """`measured-rate-travels-with-its-script`, executed.

    Every figure quoted in the module docstring is recomputed here from the
    archived exp44 registry and the repository file its falsifiers import. The
    numbers are not read from a note; they are produced by
    `compare_against_repair_adjudication`, which is committed beside them.
    """

    @pytest.fixture(scope="class")
    def measured(self):
        from bench.execution_based_matcher import (
            compare_against_repair_adjudication)
        return compare_against_repair_adjudication("exp44")

    def test_the_execution_side_reproduces(self, measured):
        # Backend-independent: nothing here consults the text matcher.
        assert measured["counts"]["pairs"] == 15
        assert measured["counts"]["execution_decided"] == 12
        assert measured["states"] == 9
        assert measured["executions"] == 81

    def test_it_agrees_with_the_stored_repair_adjudication_except_on_ERROR_legs(
            self, measured):
        """12 of 15, and every one of the 3 exceptions is a contaminated row.

        `scripts/adjudicate_by_repair.py` gained an equipment-failure refusal on
        2026-08-28 -- SAME had been its fall-through, so an ERRORed leg produced
        a verdict rather than merely contaminating one. The stored JSON was
        never recomputed, so it still carries those rows. Each of this module's
        3 disagreements with the file is one of them, identifiable from the
        file's own `detail` string.
        """
        vs = measured["vs_stored_repair_adjudication"]
        assert (vs["pairs"], vs["agree"], vs["disagree"]) == (15, 12, 3)
        assert vs["disagreements_whose_stored_row_has_an_ERROR_leg"] == 3

    def test_the_text_matcher_merges_seven_pairs_execution_separates(self, measured):
        from bench.dm._similarity import _get_embedding_model
        if _get_embedding_model() is None:
            pytest.skip("recorded against the embedding backend; lexical "
                        "fallback scores this archive far lower")
        c = measured["counts"]
        assert c["agree"] == 5
        assert c["disagree"] == 7
        assert c["text_merges_what_execution_separates"] == 7
        # NOT ONE runs the other way. The incumbent's error on this archive is
        # entirely false merges, which is the direction that deletes a real
        # second defect from the count and lets the gate close on it.
        assert c["text_separates_what_execution_merges"] == 0

    def test_the_disagreements_are_readable_from_the_row(self, measured):
        """A verdict whose evidence must be recomputed is a claim about evidence."""
        rows = {(r["a"], r["b"]): r for r in measured["rows"]}
        merged = [r for r in rows.values()
                  if r["execution"] == DIFFERENT and r["text"] == SAME]
        assert len(merged) == 7
        for r in merged:
            assert r["execution_reason"] == "surviving_repair"
            assert r["similarity"] >= 0.50
        assert json.dumps(measured["rows"])          # serialisable for an artefact
