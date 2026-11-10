"""The verification set comes from the STEM topic, and it can both admit and refuse.

HIS RULING, 2026-11-10, verbatim: the suite "will come from which ever STEM
topic area under discussion and the tools/falsifiers/B-Cell machinery attached
to that STEM topic", because a researcher submitting a STEM paper "will almost
certainly have ... included both prose and calulations/formulas they wish to be
considered", so the models' job is to "use the tools/falsifiers assigned to that
subject area to calculate those elements of any given paper that are
computationally available/reducible to them."

WHAT THIS GUARDS, AND WHY THE ADMISSION COUNT IS THE POINT. On 2026-11-10 the
sibling prose branch shipped comparing a verdict against a constant that does
not exist, so it admitted 0 of 7 reachable verdicts while its own 9-test guard
stayed green -- because that guard computed its expected answer with the same
broken expression. The lesson is recorded as: derive the ANCHOR from the
subject, never the EXPECTATION. So these tests do not ask whether the gate
agrees with itself. They drive it with claims whose truth is settled
independently -- by SymPy, on expressions a reader can check by eye -- and
assert WHICH ones admit.

A gate that admits nothing is an addition nothing reaches, which
`additive-standard` forbids symmetrically; a gate that admits everything has
stopped discriminating. Both are red here.

MEASURED BOUND, STATED SO IT IS NOT OVERCLAIMED: the B-Cell verifiers need a
FORMALISED claim. Probed 2026-11-10, 0 of 11 plain-prose sentences drew a
definitive verdict -- `2 + 2 = 4` included, because it is not valid Python --
while 4 of 5 `Eq(...)` forms did, CONFIRMED and REJECTED at confidence 0.95.
So this route adds admission only for content the domain's tools genuinely
reduce, and prose that reduces to nothing is refused, which is correct.
"""
from __future__ import annotations

import importlib
import pathlib
import sys
import types

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))


@pytest.fixture(scope="module")
def di():
    return importlib.import_module("domain_immune")


def _finding(text: str, fid: str = "F1"):
    o = types.SimpleNamespace()
    o.description = text
    o.finding_id = fid
    o.title = ""
    o.evidence = ""
    return o


class TestTheOrphanIsNoLongerAnOrphan:
    """`bench/domain_immune.py` was imported by NOTHING before 2026-11-10."""

    def test_the_entry_point_exists_and_is_callable(self, di):
        assert callable(getattr(di, "domain_verification_set", None))

    def test_the_runner_reaches_it(self):
        src = (REPO / "bench" / "reference_runner_v3.py").read_text()
        assert "domain_verification_set" in src, (
            "the gate does not reach the domain machinery, so wiring it "
            "would be an addition nothing reaches")


class TestItCanRefuse:

    def test_prose_that_reduces_to_nothing_is_refused(self, di):
        r = di.domain_verification_set("mathematics",
                                       _finding("The section reads awkwardly."))
        assert r["admits"] is False
        assert r["tools"] == []

    def test_a_false_formalised_claim_is_refused(self, di):
        r = di.domain_verification_set("mathematics", _finding("Eq(2 + 2, 5)"))
        assert r["admits"] is False
        assert "against=sympy" in r["detail"], r["detail"]

    def test_an_unknown_domain_cannot_admit(self, di):
        r = di.domain_verification_set("no_such_domain", _finding("Eq(2 + 2, 4)"))
        assert r["admits"] is False

    def test_a_classify_failure_cannot_admit(self, di):
        # An object with no `.description` makes the classifier raise.
        r = di.domain_verification_set("mathematics", object())
        assert r["admits"] is False
        assert r["detail"], "a refusal must say why"


class TestItCanAdmit:
    """Without this class the whole mechanism could be inert and still green."""

    def test_a_true_formalised_claim_admits(self, di):
        r = di.domain_verification_set("mathematics",
                                       _finding("Eq(x**2 - 1, (x-1)*(x+1))"))
        assert r["admits"] is True, r
        assert r["claim_type"] == "mathematical"
        assert "sympy" in r["tools"]

    def test_a_second_independent_true_claim_admits(self, di):
        r = di.domain_verification_set(
            "mathematics", _finding("Eq(sin(x)**2 + cos(x)**2, 1)"))
        assert r["admits"] is True, r


class TestTheAdmissionCountIsExact:
    """Drive a settled set and assert HOW MANY admit — not that it self-agrees."""

    CASES = [
        ("mathematics", "Eq(x**2 - 1, (x-1)*(x+1))", True),
        ("mathematics", "Eq(sin(x)**2 + cos(x)**2, 1)", True),
        ("mathematics", "Eq(2 + 2, 5)", False),
        ("mathematics", "The section reads awkwardly.", False),
        ("no_such_domain", "Eq(2 + 2, 4)", False),
    ]

    def test_exactly_the_true_formalised_claims_admit(self, di):
        got = [(d, t, di.domain_verification_set(d, _finding(t))["admits"])
               for d, t, _ in self.CASES]
        want = [(d, t, w) for d, t, w in self.CASES]
        assert got == want, (
            f"admission pattern changed.\n got={got}\nwant={want}\n"
            "0 admissions means the mechanism is inert; 5 means it has "
            "stopped discriminating.")

    def test_the_domain_and_tools_are_recorded_for_the_ledger(self, di):
        r = di.domain_verification_set("mathematics",
                                       _finding("Eq(x**2 - 1, (x-1)*(x+1))"))
        assert r["domain"] == "mathematics"
        assert r["detail"].startswith("mathematics/"), r["detail"]
        assert r["verdicts"], "the per-tool verdicts must be recorded"


@pytest.fixture(scope="module")
def rr():
    return importlib.import_module("bench.reference_runner_v3")


class TestTheRouteFiresThroughTheRealGate:
    """`domain_verification_set` could be perfect and still reach no caller.

    These drive `_apply_back_gate` itself, which is the thing that decides,
    because a helper verified in isolation is the `additive-standard` orphan
    this build exists to remove.
    """

    PROSE = "notes/thing.md"

    def test_a_reducible_true_claim_is_admitted(self, rr):
        ok, why = rr._apply_back_gate(
            "repaired prose", self.PROSE, "",
            finding={"description": "Eq(x**2 - 1, (x-1)*(x+1))"},
            domain="mathematics")
        assert ok is True, why
        assert why.startswith("domain:"), why
        assert "for=sympy" in why, why

    def test_a_reducible_false_claim_is_refused_with_its_reason(self, rr):
        ok, why = rr._apply_back_gate(
            "repaired prose", self.PROSE, "",
            finding={"description": "Eq(2 + 2, 5)"},
            domain="mathematics")
        assert ok is False
        assert "against=sympy" in why, why

    def test_a_non_reducible_claim_keeps_the_OLD_refusal_word_for_word(self, rr):
        ok, why = rr._apply_back_gate(
            "repaired prose", self.PROSE, "",
            finding={"description": "The section reads awkwardly."},
            domain="mathematics")
        assert ok is False
        assert why.startswith("no suite can gate a non-Python target"), why

    def test_tools_that_RAN_but_could_not_decide_do_not_admit(self, rr):
        """THE HOLE A MUTATION FOUND, 2026-11-10, and it was green before this.

        The other refusal test uses a claim the domain classifies as
        `uncategorised`, so NO tool runs and the empty-tool-list branch answers.
        That input cannot test the decision rule at all. Making UNCERTAIN count
        as a definitive verdict in favour left every test in this file green
        while the gate would admit anything its tools merely LOOKED at -- the
        `feedback_the_passing_input_cannot_test_a_defence_2026-11-09` shape, a
        defence tested only on the input it does not defend against.

        A logical claim in mathematics routes to z3, sympy and deepseek_formal,
        all 3 of which return UNCERTAIN on natural-language syllogism. So the
        tools DO run, they produce verdicts, and none is definitive -- which is
        exactly the state that must refuse.
        """
        claim = "If A implies B and B implies C then A implies C."
        di = importlib.import_module("domain_immune")
        dv = di.domain_verification_set("mathematics", _finding(claim))
        assert dv["tools"], "this input must route to tools, or it tests nothing"
        assert dv["verdicts"], "the tools must have RUN"
        assert all(v[1] == "UNCERTAIN" for v in dv["verdicts"]), dv["verdicts"]
        assert dv["admits"] is False, dv

        ok, why = rr._apply_back_gate(
            "repaired prose", self.PROSE, "",
            finding={"description": claim}, domain="mathematics")
        assert ok is False, why
        assert "for=-" in why, why

    def test_no_domain_leaves_behaviour_EXACTLY_as_it_was(self, rr):
        """The additive half: an empty domain must change nothing."""
        ok, why = rr._apply_back_gate(
            "repaired prose", self.PROSE, "",
            finding={"description": "Eq(x**2 - 1, (x-1)*(x+1))"},
            domain="")
        assert ok is False
        assert why.startswith("no suite can gate a non-Python target"), why

    def test_a_falsifier_still_takes_precedence_over_the_domain_route(self, rr):
        """The probe is stricter, so it must be asked first."""
        ok, why = rr._apply_back_gate(
            "repaired prose", self.PROSE, "",
            finding={"description": "Eq(x**2 - 1, (x-1)*(x+1))",
                     "falsifier_code": "assert 1 == 1\n"},
            domain="mathematics")
        assert why.startswith("falsifier:") or why.startswith(
            "falsifier-probe-failed:"), why

    def test_the_finding_view_reads_a_plain_dict(self, rr):
        v = rr._FindingView({"description": "Eq(2 + 2, 4)",
                             "canonical_id": "C9"})
        assert v.description == "Eq(2 + 2, 4)"
        assert v.finding_id == "C9"
        # And it must not raise on an empty entry.
        assert rr._FindingView(None).description == ""


class TestTheRunnersDefaultDomainIsNotInert:
    """`RunnerConfig.domain` defaults to "software", which is NOT a declared
    immune domain. Before 2026-11-10 that made this whole route do nothing on
    a default run: `software` yielded `tools=[]` and the gate fell through to
    the pre-existing refusal, while `code` and `mathematics` both admitted.

    `immune_agents._DOMAIN_ALIAS` maps `software` to `code` and
    `bench/domain_immune.py` did not apply it, so 2 loaders disagreed about
    the same name.

    THE INPUT HERE IS THE DEGRADED ONE. A test using only `mathematics` passed
    before the fix too, which proves nothing about the fix.
    """

    PROSE = "notes/thing.md"
    REDUCIBLE = "Eq(x**2 - 1, (x-1)*(x+1))"

    def test_the_runners_default_is_still_software(self, rr):
        """If this default changes, the case below stops being the default."""
        import dataclasses
        fields = {f.name: f for f in dataclasses.fields(rr.RunnerConfig)}
        assert "domain" in fields, sorted(fields)
        assert fields["domain"].default == "software", (
            "the runner's default domain changed; re-aim the test below at "
            f"the new default, which is {fields['domain'].default!r}")

    def test_the_alias_is_imported_not_restated(self, di):
        import importlib
        ia = importlib.import_module("immune_agents")
        assert di._resolve_domain_alias("software") == ia._DOMAIN_ALIAS["software"]
        # and a name with no alias passes through untouched
        assert di._resolve_domain_alias("mathematics") == "mathematics"

    def test_the_default_domain_admits_a_reducible_claim(self, rr):
        ok, why = rr._apply_back_gate(
            "repaired prose", self.PROSE, "",
            finding={"description": self.REDUCIBLE}, domain="software")
        assert ok is True, (
            f"the route is inert on the runner's default domain: {why}")
        assert why.startswith("domain:"), why

    def test_an_unknown_domain_STILL_refuses(self, rr):
        """The fail-closed direction, so the fix is not a loosening."""
        for dom in ("", "no_such_domain"):
            ok, why = rr._apply_back_gate(
                "repaired prose", self.PROSE, "",
                finding={"description": self.REDUCIBLE}, domain=dom)
            assert ok is False, (dom, why)
