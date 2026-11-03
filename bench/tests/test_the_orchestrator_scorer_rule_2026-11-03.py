"""A perfect run with few adjudications is INDETERMINATE, never FALSIFIED.

THE DEFECT THIS GUARDS, FOUND BY EXERCISING THE SCORER BEFORE THE ARM EXISTED.
`scripts/score_the_orchestrator_arm_2026-11-03.py` scores 3 pre-registered
predictions for the bound-orchestrator arm. Its first verdict rule for O1 read
HOLDS when the Wilson 95% lower bound cleared a floor of 0.80 and FALSIFIED
otherwise.

Run against the archive that called **10 of 28** scorable runs FALSIFIED, and
**7 of those 10 have a point estimate of EXACTLY 1.0**, with sample sizes of 8,
9, 10, 10, 10, 13 and 15. A run whose every adjudication is tool-made first
clears a 0.80 Wilson floor at **n = 16**. The rule was falsifying runs for being
SMALL and reporting it as evidence against the hypothesis.

THE CORRECTED RULE IS ONE-SIDED AND 3-VALUED, and it is the same form the
project's own P3 pre-registered prediction uses when it requires its interval to
exclude 0.5: FALSIFIED only when the Wilson UPPER bound falls below the floor,
HOLDS when the lower bound clears it, INDETERMINATE when the interval straddles
it. Under it the archive gives 18 HOLDS, 9 INDETERMINATE and 1 FALSIFIED.

A SECOND DEFECT IS GUARDED HERE TOO. O1's predicate originally read a
`mechanism` field out of `*_report.json` and returned NOT SCORABLE in 347 of 347
archived runs, because the fields are `status_adjudicator` and
`status_mechanism` and they live in `runner_state.json`. It also treated
anything not naming a quorum as tool-made -- the error
`scripts/were_the_shakedown_adjudications_tool_made_2026-10-17.py` records its
OWN first version making, which returned 79 of 79 instead of 77. The repair was
to EXTRACT `classify_adjudication` from that producer rather than re-derive it,
so this file pins that the extraction still reproduces 77 of 79 and that the
scorer and the producer share 1 implementation.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SCORER = REPO / "scripts" / "score_the_orchestrator_arm_2026-11-03.py"
CANON = (REPO / "scripts"
         / "were_the_shakedown_adjudications_tool_made_2026-10-17.py")


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def S():
    if not SCORER.is_file():
        pytest.fail(f"the scorer is not at {SCORER}")
    return _load(SCORER, "_scorer_guard")


@pytest.fixture(scope="module")
def C():
    return _load(CANON, "_canon_guard")


def _run_dir(tmp_path, entries):
    """A run directory carrying `entries` in runner_state.json."""
    (tmp_path / "runner_state.json").write_text(json.dumps(
        {"registry": {"entries": entries}}))
    return tmp_path


def _tool(n):
    return {f"C{i:04d}": {"status_adjudicator": "tool"} for i in range(n)}


def _assertion(n):
    return {f"C{i:04d}": {"status_adjudicator": "runner",
                          "status_mechanism": "model_confirm_quorum"}
            for i in range(n)}


class TestTheVerdictRuleDoesNotPunishSmallSamples:
    @pytest.mark.parametrize("n", [1, 3, 8, 9, 10, 13, 15])
    def test_a_perfect_but_small_run_is_indeterminate(self, S, tmp_path, n):
        """THE DEFECT. Every adjudication tool-made, so the share is 1.0; the
        interval is merely wide. That is not evidence against the hypothesis."""
        r = S.score_o1(_run_dir(tmp_path, _tool(n)))
        assert r["share"] == 1.0
        assert r["verdict"] == "INDETERMINATE", (
            f"a run with {n} of {n} tool-made adjudications was called "
            f"{r['verdict']}; a wide interval is not a falsification")

    def test_a_perfect_and_large_run_holds(self, S, tmp_path):
        """ANTI-VACUITY. If everything were INDETERMINATE the test above would
        pass on a constant, so HOLDS must be reachable."""
        r = S.score_o1(_run_dir(tmp_path, _tool(40)))
        assert r["verdict"] == "HOLDS", (
            f"40 of 40 tool-made must clear the floor, got {r['verdict']}")

    def test_the_floor_is_first_cleared_at_sixteen(self, S, tmp_path):
        """The boundary itself, pinned: the figure quoted in the pre-registration
        and in entry B20 is that a perfect run clears 0.80 at n = 16."""
        assert S.score_o1(_run_dir(tmp_path, _tool(15)))["verdict"] == "INDETERMINATE"
        assert S.score_o1(_run_dir(tmp_path, _tool(16)))["verdict"] == "HOLDS"

    def test_an_all_assertion_run_is_falsified(self, S, tmp_path):
        """ANTI-VACUITY the other way. FALSIFIED must be reachable, or the rule
        could never disagree with the hypothesis. This is the shape of the 1
        archived run that genuinely falsifies O1, sim45_memory_20260830T161215Z
        at 0 of 16."""
        r = S.score_o1(_run_dir(tmp_path, _assertion(16)))
        assert r["share"] == 0.0
        assert r["verdict"] == "FALSIFIED"

    def test_an_empty_run_is_not_scorable_rather_than_zero(self, S, tmp_path):
        """A 0 must be a 0 OF something. No adjudications means no denominator,
        which is NOT the same as 0 tool-made."""
        r = S.score_o1(_run_dir(tmp_path, {}))
        assert r["verdict"] == "NOT SCORABLE"
        assert "0 of NOTHING" in r.get("why", "") or r["n"] == 0


class TestTheScorerReadsTheFieldsThatExist:
    def test_a_mechanism_only_entry_does_not_count_as_tool_made(self, S, tmp_path):
        """The predicate error that returned 79 of 79. An entry carrying a
        tool's OUTPUT but no adjudicator was not DECIDED by a tool."""
        ents = {"C0001": {"status_mechanism": "falsifier_verdict"}}
        r = S.score_o1(_run_dir(tmp_path, ents))
        assert r["n"] == 0, (
            "an entry with a mechanism but no adjudicator was scored; carrying "
            "a tool's output is not the same as having been decided by one")

    def test_it_reads_runner_state_not_the_report(self, S, tmp_path):
        """The probe-location error that returned NOT SCORABLE in 347 of 347."""
        (tmp_path / "x_report.json").write_text(json.dumps(
            {"registry": {"entries": _tool(20)}}))
        assert S.score_o1(tmp_path)["verdict"] == "NOT SCORABLE", (
            "the scorer found adjudications in the report file; they live in "
            "runner_state.json and reading the wrong file is what made this "
            "predicate vacuous")
        (tmp_path / "runner_state.json").write_text(json.dumps(
            {"registry": {"entries": _tool(20)}}))
        assert S.score_o1(tmp_path)["verdict"] == "HOLDS"


class TestOneImplementationNotTwo:
    def test_the_scorer_uses_the_canonical_classifier(self, S, C):
        """The scorer must not carry its own copy of the predicate.

        COMPARED BY OUTPUT, NOT BY OBJECT IDENTITY. A first version of this test
        asserted `S._classifier() is C.classify_adjudication` and FAILED while
        the property held: the scorer loads the producer with its own
        `importlib` call, so it holds a separately-loaded instance of the same
        function. Object identity was a proxy for "the same predicate", and the
        proxy was false while the predicate was shared -- the same class of
        error this file exists to guard. Comparing the verdicts the 2 functions
        give over every shape detects genuine drift and tolerates a second load.
        """
        f = S._classifier()
        g = C.classify_adjudication
        assert f.__name__ == g.__name__ == "classify_adjudication"
        cases = [{"status_adjudicator": a} for a in
                 ("tool", "Tool", "  TOOL  ", "runner", "panel", "seat",
                  "quorum", "", None, "TOOLS", "tool ")]
        cases += [{}, {"status_mechanism": "falsifier_verdict"},
                  {"status_adjudicator": "tool",
                   "status_mechanism": "model_confirm_quorum"}]
        disagree = [c for c in cases if f(c) != g(c)]
        assert not disagree, (
            f"the scorer's classifier and the canonical one disagree on "
            f"{len(disagree)} input shape(s): {disagree[:3]}")
        # and it must be loading THAT file, not a copy of it
        import inspect
        assert pathlib.Path(inspect.getsourcefile(f)).resolve() == CANON.resolve(), (
            "the scorer's classifier does not come from the canonical producer")

    def test_the_canonical_classifier_still_reproduces_its_figure(self, C):
        """The extraction must be behaviour-preserving. The committed figure of
        77 of 79 is produced THROUGH `classify_adjudication`, so a change to it
        moves that figure rather than silently diverging from it."""
        logs = REPO / "bench" / "logs"
        missing = [leg for leg in C.LEGS
                   if not (logs / leg / "runner_state.json").is_file()]
        if missing:
            pytest.skip(f"shakedown legs absent here: {len(missing)}")
        tool = assertion = 0
        for leg in C.LEGS:
            ents = (json.loads(
                (logs / leg / "runner_state.json").read_text(errors="replace"))
                .get("registry") or {}).get("entries") or {}
            for e in ents.values():
                if not isinstance(e, dict):
                    continue
                v = C.classify_adjudication(e)
                if v == "tool":
                    tool += 1
                elif v == "assertion":
                    assertion += 1
        assert (tool, tool + assertion) == (77, 79), (
            f"the extracted classifier gives {tool} of {tool+assertion}, not "
            f"77 of 79; the figure entry B20 quotes has moved")

    @pytest.mark.parametrize("adj,expect", [
        ("tool", "tool"), ("Tool", "tool"), ("  TOOL  ", "tool"),
        ("runner", "assertion"), ("panel", "assertion"),
        ("", "unknown"), (None, "unknown"),
    ])
    def test_the_classifier_is_case_and_space_insensitive(self, C, adj, expect):
        assert C.classify_adjudication({"status_adjudicator": adj}) == expect
