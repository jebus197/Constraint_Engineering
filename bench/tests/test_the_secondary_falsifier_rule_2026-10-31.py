"""GUARD: the primary/secondary falsifier rule, 2026-10-31.

FOUNDER, 2026-10-31: *"Isn't a better rule to use an equivalent secondary
falsifier/tool when such tools are available, and if not to default exclusively
to using the primary only?"*, qualified in the same message to cover a
secondary that *"cannot be installed from the curated list"*.

AND HIS EARLIER RULING, 2026-09-28, which the Wolfram half implements verbatim:
*"Wolfram (when available) however should remain the secondary falsifier ran
against any output produced from the installed Open Source tools and should
never be considered the primary falsifier route."*

THESE TESTS EXECUTE. Per `execute-do-not-grep`, the properties that matter are
checked by CALLING the selector and the dispatch, not by reading their source:
a source assertion would only prove the modules describe themselves
consistently. The 2 tests that do read text are the policy CLAUSES, where the
words sent to a seat ARE the artefact under test.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import os
import pathlib
import sys
import tomllib

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from bench import falsifier_pairing as fp  # noqa: E402
from bench import immune_agents as ia  # noqa: E402
from bench import wolfram_standard as ws  # noqa: E402

DOMAINS = REPO / "bench" / "cdsfl_registry" / "domains" / "immune"


@pytest.fixture(scope="module")
def man():
    return ia._load_tool_manifest()


def _ort():
    spec = importlib.util.spec_from_file_location(
        "_ort_under_test", REPO / "bench" / "openrouter_tools.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["_ort_under_test"] = m
    spec.loader.exec_module(m)
    return m


#: ★ THE OFFLINE SEAM, 2026-11-02. 2 tests in this file ERRORED under
#: `--netguard-strict` with `subprocess:wolframscript x2`, in the full-suite run
#: of 2026-11-01 and in the 2026-10-31 run before it.
#:
#: WHY A SEAM AND NOT AN EXEMPTION. `bench/tests/conftest.py`'s own
#: `KNOWN_OUTBOUND` list says "Shrink this list; never grow it without writing
#: down why here", so adding these 2 would be the wrong direction. And the
#: deeper reason is in this file already: the Wolfram version of the dispatch
#: test "stayed GREEN under the mutation for an accidental reason -- with the
#: suite offline the kernel cannot launch, so `wolfram` returns UNCERTAIN ...
#: Kernel availability was silently deciding the test." A test whose verdict
#: depends on whether a kernel happens to be installed is not a test.
#:
#: WHAT THIS PATCHES. `wolfram_standard.run_local` is the single subprocess
#: site: `_verify_wolfram` reaches the wire at exactly 1 line,
#: `r = _ws.run_local(code, ...)`. Returning a NOT-EVIDENCE result there drives
#: the code's OWN failure branch rather than a stub of it, so each test keeps
#: its property: a Wolfram call that did not answer must never be read as an
#: answer, and the dispatch must fall through to the primary tools.
@pytest.fixture
def no_wolfram_wire(monkeypatch):
    def _no_wire(code, *a, **k):
        return {"evidence": False, "reason": "offline seam: no kernel was asked",
                "stdout": "", "stderr": "", "attribution": ""}
    monkeypatch.setattr(ws, "run_local", _no_wire, raising=True)
    return _no_wire


class TestTheManifestCarriesTheAxis:
    def test_every_entry_declares_an_independence_class(self, man):
        missing = [k for k, v in man.items() if not v.get("independence_class")]
        assert missing == [], f"entries with no independence_class: {missing}"

    def test_every_class_is_in_the_closed_vocabulary(self, man):
        bad = {k: v["independence_class"] for k, v in man.items()
               if v["independence_class"] not in fp.INDEPENDENCE_CLASSES}
        assert bad == {}, f"unknown independence_class values: {bad}"

    def test_the_manifest_holds_both_a_same_class_and_a_cross_class_pair(self, man):
        """ANTI-VACUITY CONTROL.

        If every tool were in its own class, every pair would be independent
        and the whole rule would be untestable -- it would pass without ever
        refusing anything. If every tool shared one class, nothing would ever
        pair. Both failure modes make the suite green and the rule dead, so
        both are checked.
        """
        names = [k for k in man if not man[k].get("delegate")]
        same = [(a, b) for a in names for b in names
                if a < b and fp.independence_class(a, man) == fp.independence_class(b, man)]
        cross = [(a, b) for a in names for b in names
                 if a < b and fp.independence_class(a, man) != fp.independence_class(b, man)]
        assert same, "no same-class pair exists: the rule could never refuse"
        assert cross, "no cross-class pair exists: the rule could never pair"


class TestIndependenceIsDecidedByExecution:
    def test_statsmodels_and_scipy_share_one_verifier(self, man):
        """The measured case that motivates the rule.

        Both entries name `_verify_statistical`, so the canonical 2-tool pair
        for a statistical claim was 1 function called twice.
        """
        assert fp.shares_verifier("statsmodels", "scipy", man)
        assert man["statsmodels"]["verifier"] == man["scipy"]["verifier"]
        assert getattr(ia, man["scipy"]["verifier"], None) is not None

    def test_a_shared_verifier_is_never_independent(self, man):
        assert not fp.is_independent("statsmodels", "scipy", man)

    def test_a_shared_verifier_beats_a_DIFFERENT_class(self, man):
        """THE PROPERTY, SEPARATED FROM THE INCIDENTAL DATA.

        Added after a mutation run: disabling the `shares_verifier` check left
        the suite GREEN, because the only live pair that shares a verifier --
        `statsmodels` and `scipy` -- is ALSO same-class `numeric`, so the class
        test caught it anyway. The check was therefore unreachable by the real
        manifest, which under the additive standard is an addition nothing
        reaches. This constructs the pair that distinguishes them: same
        verifier, DIFFERENT class. Identity of code must win over declared
        route, because 1 function cannot corroborate itself however it is
        labelled.
        """
        m = dict(man)
        m["twin_a"] = {"verifier": "_verify_statistical",
                       "independence_class": "numeric"}
        m["twin_b"] = {"verifier": "_verify_statistical",
                       "independence_class": "symbolic"}
        assert fp.independence_class("twin_a", m) != fp.independence_class("twin_b", m)
        assert fp.shares_verifier("twin_a", "twin_b", m)
        assert not fp.is_independent("twin_a", "twin_b", m), (
            "two entries naming ONE function were treated as independent "
            "falsifiers because their declared classes differed")
        tool, reason, _ = fp.select_secondary("twin_a", ["twin_a", "twin_b"], m)
        assert tool is None and reason == fp.NO_INDEPENDENT_CANDIDATE

    def test_a_tool_is_not_independent_of_itself(self, man):
        assert not fp.is_independent("sympy", "sympy", man)

    def test_different_classes_are_independent(self, man):
        assert fp.independence_class("sympy", man) == "symbolic"
        assert fp.independence_class("z3", man) == "search"
        assert fp.is_independent("sympy", "z3", man)

    def test_an_unclassified_tool_is_not_independent(self, man):
        """Conservative by design: it costs a corroboration, never invents one."""
        m = dict(man)
        m["mystery"] = {"verifier": "_verify_nothing"}
        assert not fp.is_independent("sympy", "mystery", m)
        assert not fp.is_independent("mystery", "sympy", m)


class TestSelectionAndItsRefusals:
    def test_an_independent_candidate_is_selected(self, man):
        tool, reason, _ = fp.select_secondary("sympy", ["sympy", "z3"], man)
        assert (tool, reason) == ("z3", fp.SELECTED)

    def test_all_same_class_gives_primary_only_with_a_reason(self, man):
        tool, reason, detail = fp.select_secondary(
            "statsmodels", ["statsmodels", "scipy", "uncertainty_propagation"], man)
        assert tool is None
        assert reason == fp.NO_INDEPENDENT_CANDIDATE
        assert "numeric" in detail

    def test_a_lone_tool_gives_no_candidates(self, man):
        tool, reason, _ = fp.select_secondary("sympy", ["sympy"], man)
        assert tool is None and reason == fp.NO_CANDIDATES

    def test_a_paid_route_is_never_selected_by_default(self, man):
        """HARD CONSTRAINT: no paid dispatch without his express authorisation.

        `deepseek_formal` is class `model` and independent of z3, so a selector
        that merely ranked it last would still reach it.
        """
        assert fp.is_paid_route("deepseek_formal", man)
        tool, reason, _ = fp.select_secondary(
            "z3", ["z3", "deepseek_formal"], man)
        assert tool is None
        assert reason == fp.INDEPENDENT_CANDIDATE_IS_PAID

    def test_the_paid_flag_is_real_and_not_decorative(self, man):
        tool, reason, _ = fp.select_secondary(
            "z3", ["z3", "deepseek_formal"], man, allow_paid=True)
        assert (tool, reason) == ("deepseek_formal", fp.SELECTED)

    def test_a_free_route_is_preferred_over_a_paid_one(self, man):
        tool, _, _ = fp.select_secondary(
            "z3", ["z3", "deepseek_formal", "sympy"], man, allow_paid=True)
        assert tool == "sympy"

    def test_an_uninstalled_candidate_reports_its_package_hint(self, man):
        """His curated-list qualification, made actionable.

        The record must name WHAT to install, which is the first use this
        project has ever made of `package_hint`.
        """
        tool, reason, detail = fp.select_secondary(
            "sympy", ["sympy", "z3"], man, available=lambda t: False)
        assert tool is None
        assert reason == fp.INDEPENDENT_CANDIDATE_NOT_INSTALLED
        assert "z3-solver" in detail

    def test_every_refusal_is_in_the_primary_only_set(self, man):
        for reason in (fp.NO_CANDIDATES, fp.NO_INDEPENDENT_CANDIDATE,
                       fp.INDEPENDENT_CANDIDATE_IS_PAID,
                       fp.INDEPENDENT_CANDIDATE_NOT_INSTALLED):
            assert reason in fp.PRIMARY_ONLY_REASONS
        assert fp.SELECTED not in fp.PRIMARY_ONLY_REASONS

    def test_install_check_is_actually_executed(self, man):
        """`probe_available` is the first consumer of `install_check`.

        Executed rather than asserted: a tool whose check cannot import is
        reported unavailable, and one whose check imports is available.
        """
        m = dict(man)
        m["ghost"] = {"install_check": "import a_module_that_does_not_exist_x7"}
        m["present"] = {"install_check": "import sys"}
        assert fp.probe_available("present", m) is True
        assert fp.probe_available("ghost", m) is False


class TestWolframIsSecondaryOnlyEverywhere:
    def test_the_manifest_marks_it_secondary_only(self, man):
        assert man["wolfram"]["secondary_only"] is True
        assert fp.is_secondary_only("wolfram", man)

    def test_it_is_stripped_from_every_primary_pool(self, man):
        pool = fp.primary_candidates(["statsmodels", "wolfram"], man)
        assert "wolfram" not in pool

    def test_it_is_never_the_primary_in_any_domain_config(self, man):
        """HIS RULING OF 2026-09-28, EXECUTED OVER ALL 10 DOMAIN CONFIGS.

        This is the test that would have caught the trap: appending Wolfram to
        a claim type without `secondary_only` would have made it reachable at
        position 13 of the `mathematical` order -- a primary route whenever the
        12 tools before it returned UNCERTAIN.
        """
        offenders = []
        for tf in sorted(DOMAINS.glob("*.toml")):
            cfg = tomllib.loads(tf.read_text(encoding="utf-8"))
            vt = (cfg.get("immune") or {}).get("verification_tools") or {}
            for claim, tools in vt.items():
                pool = fp.primary_candidates(tools, man)
                if pool and pool[0] == "wolfram":
                    offenders.append((tf.stem, claim))
        assert offenders == [], f"wolfram is primary for {offenders}"

    def test_it_is_listed_somewhere_or_the_entry_reaches_nothing(self, man):
        """ADDITIVE STANDARD: an addition nothing reaches is not additive.

        The manifest entry alone puts Wolfram in front of no claim -- the
        dispatch reads the DOMAIN configs. This was a live error in the first
        version of this work.
        """
        listed = []
        for tf in sorted(DOMAINS.glob("*.toml")):
            cfg = tomllib.loads(tf.read_text(encoding="utf-8"))
            vt = (cfg.get("immune") or {}).get("verification_tools") or {}
            for claim, tools in vt.items():
                if "wolfram" in tools:
                    listed.append((tf.stem, claim))
        assert listed, "no domain config references wolfram: the entry is unreachable"

    def test_a_delegated_tool_is_excluded_from_both_roles(self, man):
        """Found by measurement: `ast_analysis` and `test_runner` are owned by
        other cells, so they can neither decide nor corroborate here."""
        assert fp.is_delegated("ast_analysis", man)
        assert "ast_analysis" not in fp.primary_candidates(
            ["ast_analysis", "type_checker"], man)
        tool, _, _ = fp.select_secondary(
            "symbolic_execution", ["symbolic_execution", "test_runner"], man)
        assert tool != "test_runner"


class TestTheMarkingIsTheOperativeHalf:
    def test_primary_only_and_corroborated_are_distinguishable(self):
        alone = fp.pairing_note("statsmodels", None,
                                fp.NO_INDEPENDENT_CANDIDATE, "all numeric")
        both = fp.pairing_note("sympy", "z3", fp.SELECTED, "ok", agrees=True)
        assert "primary-only" in alone and "secondary" not in alone.split()[0]
        assert "AGREES" in both
        assert alone != both

    def test_a_disagreement_is_said_out_loud(self):
        note = fp.pairing_note("sympy", "z3", fp.SELECTED, "d", agrees=False)
        assert "DISAGREES" in note

    def test_an_unrun_secondary_is_not_reported_as_agreement(self):
        note = fp.pairing_note("sympy", "z3", fp.SELECTED, "d", agrees=None)
        assert "NOT_RUN" in note
        assert "AGREES" not in note


class TestTheDispatchActuallyRunsIt:
    def _dispatch(self, tools, claim_type, claim):
        tfd = ia.TriagedFinding(
            finding=ia.Finding(finding_id="f1", model_id="m", round_idx=0,
                               flaw_class=1, severity=0.5,
                               abstraction_index=0.5, description=claim),
            claim_type=claim_type, extracted_claim=claim)
        cfg = {"immune": {"verification_tools": {claim_type.value: tools}}}
        return ia._specialist_b_cell_dispatch([tfd], cfg)

    def test_a_definitive_verdict_carries_a_pairing_note(self):
        """THE WIRING TEST. Calls the real dispatch; no source reading."""
        out = self._dispatch(["sympy", "z3"], ia.ClaimType.MATHEMATICAL,
                             "Eq(2+2, 4)")
        assert out, "the dispatch returned no verdict at all"
        assert out[0].verdict == "CONFIRMED"
        assert "[falsifier:" in out[0].evidence, out[0].evidence

    def test_the_primary_is_unchanged_by_the_secondary_pass(self):
        out = self._dispatch(["sympy", "z3"], ia.ClaimType.MATHEMATICAL,
                             "Eq(2+2, 4)")
        assert "[specialist:sympy]" in out[0].evidence

    def test_the_dispatch_refuses_a_secondary_only_primary_with_no_kernel(
            self, man, monkeypatch):
        """THE ENFORCEMENT TEST THAT DOES NOT DEPEND ON WOLFRAM BEING THERE.

        Added after a second mutation run. The Wolfram version of this test
        below stayed GREEN under the mutation for an accidental reason: with
        the suite offline the kernel cannot launch, so `wolfram` returns
        UNCERTAIN, the loop falls through to `sympy` anyway, and the assertion
        holds whether or not the filter is applied. Kernel availability was
        silently deciding the test.

        So the tool here is SYNTHETIC and DEFINITIVE: it is `secondary_only`
        and its verifier returns CONFIRMED immediately. If the dispatch
        iterated the raw list it would break on this tool and name it, which
        is precisely the ruling violation.
        """
        def _verify_fake_sec_only(claim, *a, **k):
            return ia.CellVerdict(
                cell_type=ia.CellType.B_CELL, finding_id="",
                verdict="CONFIRMED", confidence=0.99,
                evidence="fake secondary-only tool decided the claim",
                tool_used="fake_sec_only", elapsed_s=0.0)

        monkeypatch.setattr(ia, "_verify_fake_sec_only",
                            _verify_fake_sec_only, raising=False)
        patched = dict(man)
        patched["fake_sec_only"] = {
            "description": "synthetic", "verifier": "_verify_fake_sec_only",
            "needs_file": False, "claim_types": ["mathematical"],
            "independence_class": "reference", "secondary_only": True,
            "install_check": "import sys", "package_hint": "none",
        }
        monkeypatch.setattr(ia, "_TOOL_MANIFEST_CACHE", patched)

        out = self._dispatch(["fake_sec_only", "sympy"],
                             ia.ClaimType.MATHEMATICAL, "Eq(2+2, 4)")
        assert out, "the dispatch returned no verdict at all"
        assert "[specialist:sympy]" in out[0].evidence, (
            "a secondary_only tool was allowed to DECIDE the claim: "
            f"{out[0].evidence}")
        assert "[specialist:fake_sec_only]" not in out[0].evidence

    def test_the_dispatch_itself_refuses_a_secondary_only_primary(self, no_wolfram_wire):
        """HIS RULING OF 2026-09-28, ENFORCED AT THE DISPATCH AND NOT MERELY
        IN THE SELECTOR.

        Added after a mutation run: reverting the dispatch to iterate the raw
        tool list left the suite GREEN, because every wiring test used a list
        with no `secondary_only` tool in it -- so the filtered pool and the raw
        list were identical and the enforcement was never exercised. Here
        `wolfram` is listed FIRST. If the dispatch iterated the raw list it
        would make Wolfram the primary, which is exactly what the ruling
        forbids.
        """
        out = self._dispatch(["wolfram", "sympy"], ia.ClaimType.MATHEMATICAL,
                             "Eq(2+2, 4)")
        assert out, "the dispatch returned no verdict at all"
        assert "[specialist:sympy]" in out[0].evidence, (
            f"wolfram was allowed to decide the claim: {out[0].evidence}")
        assert "[specialist:wolfram]" not in out[0].evidence

    def test_a_lone_tool_is_marked_primary_only(self):
        out = self._dispatch(["sympy"], ia.ClaimType.MATHEMATICAL, "Eq(2+2, 4)")
        assert "primary-only" in out[0].evidence
        assert fp.NO_CANDIDATES in out[0].evidence

    def test_the_kill_switch_still_marks_the_record(self, monkeypatch):
        """A skipped secondary must never read as a corroborated one."""
        monkeypatch.setenv("CDSFL_FALSIFIER_SECONDARY", "0")
        out = self._dispatch(["sympy", "z3"], ia.ClaimType.MATHEMATICAL,
                             "Eq(2+2, 4)")
        assert "skipped by CDSFL_FALSIFIER_SECONDARY=0" in out[0].evidence
        assert "AGREES" not in out[0].evidence

    def test_wolfram_reaches_the_dispatch_as_a_secondary(self):
        """Executes the real kernel. Skipped where it is not installed, which
        is itself the founder's no-compulsion rule."""
        if not ws.real_wolframscript() or ws.policy() == "deny":
            pytest.skip("no local Wolfram Engine, or policy is deny")
        if os.environ.get("CDSFL_ALLOW_LIVE_DISPATCH") != "1":
            pytest.skip("the suite is offline by default and its netguard "
                        "denies a wolframscript subprocess -- which is itself "
                        "a deliberate property, held by "
                        "test_wolfram_secondary_source_2026-09-17.py")
        out = self._dispatch(["sympy", "wolfram"], ia.ClaimType.MATHEMATICAL,
                             "Eq(2+2, 4)")
        assert "[specialist:sympy]" in out[0].evidence
        assert "wolfram" in out[0].evidence


class TestTheVerifierNeverBlocks:
    def test_a_dangerous_function_is_refused(self):
        v = ia._verify_wolfram('Import["/etc/passwd"] = 1')
        assert v.verdict == "UNCERTAIN"
        assert "BLOCKED" in v.evidence

    def test_an_absent_kernel_is_uncertain_not_an_exception(self, monkeypatch):
        monkeypatch.setattr(ws, "real_wolframscript", lambda *a, **k: None)
        v = ia._verify_wolfram("Eq(2+2, 4)")
        assert v.verdict == "UNCERTAIN"
        assert "not installed" in v.evidence

    def test_the_deny_policy_is_honoured(self, monkeypatch):
        monkeypatch.setattr(ws, "policy", lambda *a, **k: "deny")
        v = ia._verify_wolfram("Eq(2+2, 4)")
        assert v.verdict == "UNCERTAIN"
        assert "deny" in v.evidence

    def test_bare_equals_is_rewritten_and_operators_are_not(self):
        """`=` is ASSIGNMENT in Wolfram Language and equality in these claims,
        so the rewrite is required for correctness. The operators that must NOT
        be touched are checked in the same test, because a greedy pattern that
        broke `<=` would still pass the positive case alone."""
        sub = ia._WOLFRAM_BARE_EQ.sub
        assert sub("==", "2 + 2 = 4") == "2 + 2 == 4"
        for keep in ("x == y", "a <= b", "a >= b", "a != b"):
            assert sub("==", keep) == keep


class TestTheTranslationIsSafeOrAbsent:
    """The pair is handed ONE claim string but the 2 tools read different
    syntaxes. Found by a failing test on 2026-10-31: without translation every
    Wolfram secondary on a SymPy-decidable claim returned NOT EVIDENCE, so the
    whole secondary pass would have been wired and inert."""

    def test_an_equality_is_translated(self):
        assert ia._sympy_claim_to_wolfram("Eq(2+2, 4)") == "(2+2) == (4)"

    def test_allow_listed_functions_become_bracket_form(self):
        got = ia._sympy_claim_to_wolfram("Eq(sin(x)**2 + cos(x)**2, 1)")
        assert got == "(Sin[x]^2 + Cos[x]^2) == (1)"

    def test_a_constant_is_translated(self):
        assert ia._sympy_claim_to_wolfram("Eq(sin(pi), 0)") == "(Sin[Pi]) == (0)"

    def test_an_unknown_lowercase_call_is_refused(self):
        assert ia._sympy_claim_to_wolfram("Eq(f(x), 1)") is None

    def test_an_unknown_CAPITALISED_call_is_also_refused(self):
        """The first guard tested for lowercase only and let this through.

        `Integral` is not a Wolfram function -- it is `Integrate` -- so the
        kernel would have read it as a product. A capitalised SymPy name is
        exactly as untranslatable as a lowercase one.
        """
        assert ia._sympy_claim_to_wolfram("Eq(Integral(x, (x,0,1)), 1)") is None

    def test_an_argument_order_hazard_is_refused(self):
        """`atan2` exists in both systems with DIFFERENT argument order, which
        is the silent-wrong-answer class. It is deliberately not mapped."""
        assert ia._sympy_claim_to_wolfram("Eq(atan2(1,1), pi/4)") is None

    def test_grouping_parentheses_survive_the_bracket_walk(self):
        got = ia._sympy_claim_to_wolfram("Eq(sqrt((x+1)*(x+1)), x+1)")
        assert got == "(Sqrt[(x+1)*(x+1)]) == (x+1)"

    def test_unbalanced_input_is_refused_not_mangled(self):
        assert ia._sympy_claim_to_wolfram("Eq(sqrt(4, 2)") is None

    @pytest.mark.parametrize("claim,truth", [
        ("Eq(2+2, 4)", "CONFIRMED"),
        ("Eq(2+2, 5)", "REJECTED"),
        ("Eq(x+0, x)", "CONFIRMED"),
        ("Eq(sin(x)**2 + cos(x)**2, 1)", "CONFIRMED"),
        ("Eq(exp(0), 1)", "CONFIRMED"),
        ("Eq(sqrt(4), 2)", "CONFIRMED"),
        ("Eq(sqrt(4), 3)", "REJECTED"),
    ])
    def test_the_translation_never_returns_a_WRONG_boolean(self, claim, truth):
        """THE PROPERTY THAT MATTERS MOST.

        A mistranslation that returns no answer costs a corroboration. One
        that returns the WRONG answer manufactures a false corroboration or a
        false disagreement, which is worse than having no secondary at all.
        UNCERTAIN is always acceptable here; the opposite verdict never is.
        """
        if not ws.real_wolframscript() or ws.policy() == "deny":
            pytest.skip("no local Wolfram Engine, or policy is deny")
        if os.environ.get("CDSFL_ALLOW_LIVE_DISPATCH") != "1":
            pytest.skip("the suite is offline by default")
        got = ia._verify_wolfram(claim).verdict
        assert got in (truth, "UNCERTAIN"), (
            f"{claim}: truth is {truth} and Wolfram said {got}")


class TestTheRemoteSeatsCanReachIt:
    def test_the_tool_is_in_the_host_side_surface(self):
        m = _ort()
        names = [s["function"]["name"] for s in m.TOOL_SPECS]
        assert "wolfram_verify" in names
        assert "wolfram_verify" in m._TOOL_DISPATCH

    def test_the_panel_exposes_it_to_a_remote_seat(self):
        spec = importlib.util.spec_from_file_location(
            "_panel_under_test",
            REPO / "bench" / "confer_maths_panel_2026-09-05.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["_panel_under_test"] = m
        try:
            spec.loader.exec_module(m)
        except SystemExit:
            pass
        names = [s["function"]["name"] for s in m.TOOL_SPECS]
        assert "wolfram_verify" in names, (
            "a remote seat has no shell, so without this tool his 2026-09-28 "
            "secondary-falsifier ruling is unreachable for 4 of 6 seats")

    def test_a_failure_cannot_be_read_as_an_answer(self, no_wolfram_wire):
        m = _ort()
        import json
        out = json.loads(m.dispatch_tool_call(
            "wolfram_verify", '{"code": "ThisIsNotAFunction[[["}'))
        assert out["verdict"] == "NOT_EVIDENCE"
        assert out["evidence"] is False

    def test_a_missing_argument_is_an_error_not_a_crash(self):
        m = _ort()
        import json
        out = json.loads(m.dispatch_tool_call("wolfram_verify", "{}"))
        assert "error" in out

    def test_both_routes_are_named_in_the_clause_a_seat_receives(self):
        """The CLAUSE is the artefact: these words are what the seat is sent."""
        serial = ws.panel_clause("serial")
        assert "wolframscript -code" in serial, "the shell route must stay named"
        assert "wolfram_verify" in serial, (
            "a remote seat was being told to use Bash, which it does not have")

    def test_the_deny_clause_bars_the_tool_too(self):
        assert "wolfram_verify" in ws.panel_clause("deny")


class TestTheLicenceFalseAlarmCannotRecur:
    def test_a_lapse_points_at_the_automation_not_at_a_manual_step(self):
        w = ws.licence_warning("2026-01-01", today=dt.date(2026, 2, 1))
        assert w is not None and "EXPIRED" in w
        assert "AUTOMATION failed" in w

    def test_near_expiry_says_no_action_is_expected(self):
        """FOUNDER, 2026-10-31: stop rediscovering a solved problem.

        Renewal is automated, so the licence sits inside a 14-day horizon
        routinely. The old text said it "did not auto-renew last time" and to
        renew by hand -- true once in September 2026, self-perpetuating since.
        """
        w = ws.licence_warning("2026-02-10", today=dt.date(2026, 2, 1))
        assert w is not None
        assert "NO ACTION IS EXPECTED" in w
        assert "by hand" not in w

    def test_a_healthy_licence_warns_about_nothing(self):
        assert ws.licence_warning("2026-12-01", today=dt.date(2026, 2, 1)) is None

    def test_live_expiry_prefers_the_kernel_over_the_constant(self):
        if (not ws.real_wolframscript()
                or os.environ.get("CDSFL_ALLOW_LIVE_DISPATCH") != "1"):
            pytest.skip("no local kernel, or the suite's netguard is active")
        live = ws.live_expiry()
        assert live is not None
        assert live != ws.RECORDED_LICENCE_EXPIRY, (
            "the kernel and the frozen constant agree, so this test proves "
            "nothing today -- but the constant is stale by design and the "
            "point is that the kernel is what gets read")

    def test_live_expiry_returns_none_rather_than_raising(self, monkeypatch):
        monkeypatch.setattr(ws, "real_wolframscript", lambda *a, **k: None)
        assert ws.live_expiry() is None
