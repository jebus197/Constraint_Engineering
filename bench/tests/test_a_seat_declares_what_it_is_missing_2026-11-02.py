"""A seat says what it is missing, without leaking a key or spending a penny.

WHAT IS UNDER TEST. `bench/seat_readiness.py` and the `seats()` function it is
reached through in `bench/ux_backend_2026-10-20.py` -- the backend half of his
2026-11-02 ask that researchers be able to add models and keys trivially, and of
the 2026-10-20 authorisation to build the UX backend so a UX can map onto it.

THE 3 PROPERTIES THAT MATTER, AND WHY EACH IS EXECUTED RATHER THAN READ.

  1. NO CREDENTIAL VALUE CAN REACH A CALLER. A docstring promising this is worth
     nothing; the test sets a sentinel value in the environment and asserts it is
     absent from the serialised payload. That is the only form of this test that
     could fail if the code started leaking.

  2. NOTHING IS DISPATCHED. A probe IS a dispatch and no paid dispatch happens
     without his express authorisation, so the report must contact nothing. Tested
     by breaking the socket layer and asserting the report still succeeds -- which
     a mocked-out assertion about intent could not establish.

  3. THE CREDENTIAL MAP AGREES WITH WHAT THE DISPATCHER ACTUALLY READS. The map is
     a SECOND statement of something the dispatch code already says by reading
     environment variables in 8 places, and `execute-do-not-grep` applies: the
     names are lifted from `bench/experiment_11_orchestrator.py`'s own syntax tree
     and compared, so renaming a credential turns this red instead of silently
     making the UX report a configured seat as unconfigured.

ON STALENESS, because this file was written the day a sibling guard was repaired
for exactly that. `test_the_preflight_refuses_an_unregistered_seat_2026-11-02.py`
had asserted that Fable FAILS registration and began accusing correct code the
moment that gap closed. So the gap-detection test here uses a SYNTHETIC seat that
is absent by construction, never Fable, and never any seat the project might
later register.
"""
from __future__ import annotations

import ast
import json
import os
import pathlib
import socket
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import seat_readiness as SR                       # noqa: E402

SENTINEL = "sk-THIS-VALUE-MUST-NEVER-APPEAR-IN-A-PAYLOAD-7f3a9c"


class TestNoCredentialValueEscapes:
    """Property 1, with a sentinel rather than a promise."""

    @pytest.mark.parametrize("var", ["OPENROUTER_API_KEY", "DEEPSEEK_API_KEY",
                                     "GEMINI_API_KEY", "GOOGLE_API_KEY"])
    def test_a_sentinel_credential_never_reaches_the_payload(self, var, monkeypatch):
        monkeypatch.setenv(var, SENTINEL)
        blob = json.dumps(SR.readiness(), default=str)
        assert SENTINEL not in blob, (
            f"the value of {var} reached the payload; this surface is destined "
            f"for a UX and must never carry a key")

    def test_the_sentinel_is_nevertheless_DETECTED(self, monkeypatch):
        """The test above would pass vacuously if nothing read the variable.

        So the same sentinel must flip the route to present. Without this, a
        module that ignored credentials entirely would score a clean pass on the
        leak test, which is the vacuity trap this project keeps finding.
        """
        monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
        before = SR.credential_present("openrouter")
        monkeypatch.setenv("OPENROUTER_API_KEY", SENTINEL)
        after = SR.credential_present("openrouter")
        assert after is True, "setting the credential must be detected"
        assert SR.credential_source("openrouter") == "environment"
        # `before` may legitimately be True via .env, so it is reported rather
        # than asserted -- asserting False here would fail on a configured machine.
        assert before in (True, False)

    def test_dotenv_reading_yields_names_and_never_values(self):
        names = SR._dotenv_names()
        assert isinstance(names, frozenset)
        for n in names:
            assert "=" not in n, f"{n!r} looks like a whole line, not a name"
            assert n == n.strip()
        env = REPO / ".env"
        if env.is_file():
            # every value in the file must be absent from the returned set
            for line in env.read_text(errors="replace").splitlines():
                if "=" in line and not line.strip().startswith("#"):
                    val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if len(val) > 8:
                        assert val not in names


class TestNothingIsDispatched:
    """Property 2. A probe is a dispatch; a report must not be one."""

    def test_the_report_succeeds_with_the_socket_layer_broken(self, monkeypatch):
        def _no_network(*a, **k):
            raise AssertionError(
                "seat_readiness opened a socket; it must report configuration "
                "only, because a probe is a dispatch and no paid dispatch "
                "happens without his express authorisation")

        monkeypatch.setattr(socket, "socket", _no_network)
        monkeypatch.setattr(socket, "create_connection", _no_network)
        r = SR.readiness()
        assert r["counts"]["known"] >= 1

    def test_the_payload_says_it_is_configuration_only(self):
        """The caveat travels in the DATA, so a UX cannot present it as liveness."""
        r = SR.readiness()
        assert "no route was contacted" in r["caveat"]


class TestTheCredentialMapMatchesTheDispatcher:
    """Property 3, by executing against the dispatcher's own syntax tree."""

    def test_every_mapped_name_is_one_the_dispatcher_really_reads(self):
        orch = REPO / "bench" / "experiment_11_orchestrator.py"
        tree = ast.parse(orch.read_text())
        read: set[str] = set()
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            # os.environ.get("X") and os.getenv("X")
            if isinstance(f, ast.Attribute) and f.attr in ("get", "getenv"):
                for arg in node.args[:1]:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        read.add(arg.value)
        # os.environ["X"]
        for node in ast.walk(tree):
            if (isinstance(node, ast.Subscript)
                    and isinstance(node.slice, ast.Constant)
                    and isinstance(node.slice.value, str)):
                read.add(node.slice.value)

        assert any(n.endswith("_API_KEY") for n in read), (
            "the dispatcher reads no *_API_KEY at all; this test's extraction is "
            "wrong rather than the dispatcher having no credentials")

        mapped = {n for names in SR.API_CREDENTIALS.values() for n in names}
        unknown = sorted(mapped - read)
        assert not unknown, (
            f"seat_readiness maps credential name(s) the dispatcher never reads: "
            f"{unknown}. Either a route was renamed or the map invented a name; "
            f"a UX would then report a configured seat as unconfigured.")

    def test_a_cli_route_declares_no_credential_and_is_not_reported_as_missing(self):
        """Empty must mean "nothing to configure", never "unconfigured".

        Collapsing those would send a researcher hunting for a key that does not
        exist -- `claude_cli` and `codex_exec` run on his Max subscription.
        """
        for api in ("claude_cli", "codex_exec", "sim"):
            assert SR.API_CREDENTIALS[api] == ()
            assert SR.credential_present(api) is None
            assert SR.credential_source(api) is None

    def test_an_unknown_route_is_refused_rather_than_silently_passed(self):
        assert SR.credential_present("some_vendor_we_never_added") is False


class TestGapDetection:
    """Does it actually find a missing registration, and on a stale-proof subject."""

    def test_a_synthetic_absent_seat_is_reported_as_missing_from_every_table(self):
        """Absent by construction, so this can never accuse correct code.

        A name the project will not register is used instead of a real seat --
        the lesson from the Fable preflight guard repaired the same day.
        """
        gaps = SR.registration_gaps("Seat-That-Does-Not-Exist-2026-11-02")
        assert len(gaps) >= 5, (
            f"a wholly unregistered seat should miss every table; got {gaps}")
        assert any("MODEL_SPECS" in g for g in gaps)
        assert any("INITIAL_FINGERPRINTS" in g for g in gaps)

    def test_a_registered_seat_has_no_gaps_so_the_test_above_is_not_vacuous(self):
        """The control. Without it, a function returning everything would pass."""
        from bench import runner_core as rc
        some = sorted(rc.MODEL_SPECS)[0]
        assert SR.registration_gaps(some) == [], (
            f"{some} is in MODEL_SPECS and should be fully registered; if this "
            f"fails the project has a real gap, not a broken test")

    def test_not_asked_is_distinct_from_absent(self):
        """`models=None` must not be reported as "no route"."""
        unasked = {r["label"]: r for r in SR.seat_rows(None)}
        asked = {r["label"]: r for r in SR.seat_rows([])}
        label = next(iter(unasked))
        assert unasked[label]["has_route"] is None
        assert unasked[label]["ready"] is None
        assert asked[label]["has_route"] is False
        assert asked[label]["ready"] is False


class TestOneDeclarationOfTheKeying:
    """The drift this module's first version actually committed."""

    def test_the_gaps_come_from_model_admissions_own_target_list(self):
        """Executed, not grepped: break the single declaration, see gaps change.

        The first version of `seat_readiness` kept its own copy of the 5 tables
        and keyed all of them on the composer key, where 2 are keyed on the
        LABEL. It reported 6 of 6 seats as gapped. The keying now has exactly 1
        home and this proves `registration_gaps` reads it.
        """
        from bench import model_admission as MA

        calls: list[tuple[str, str]] = []
        real = MA.registration_targets

        def spy(model, ckey):
            calls.append((model, ckey))
            return real(model, ckey)

        MA.registration_targets = spy                     # type: ignore[assignment]
        try:
            SR.registration_gaps("CC2")
        finally:
            MA.registration_targets = real                # type: ignore[assignment]
        assert calls, (
            "registration_gaps did not consult "
            "model_admission.registration_targets, so a second copy of the "
            "keying has reappeared")

    def test_the_removed_second_declaration_stays_removed(self):
        with pytest.raises(NotImplementedError):
            SR._tables()


class TestItIsReachable:
    """`additive-standard`: an addition nothing reaches is not additive."""

    def test_the_ux_backend_exposes_it(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "uxb", REPO / "bench" / "ux_backend_2026-10-20.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        r = m.seats()
        assert r["name"] == "Seats"
        assert "counts" in r and "routes" in r
        assert r["placement_is_his_decision"] is True

    def test_it_does_not_change_the_tab_list_which_is_his(self):
        """Wiring a function must not quietly re-specify his interface."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "uxb2", REPO / "bench" / "ux_backend_2026-10-20.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert "Seats" not in m.TABS, (
            "a Seats tab was added to TABS; where it sits in the chrome is his "
            "decision, taken from his own instruction about the Discourse tab")


class TestTheTwoRosterDeclarations:
    """The check that was MISSING from this surface when it was first built.

    ★ WHY IT WAS A GAP WORTH NAMING. The surface reported calibration gaps and a
    route, and said nothing about the roster being declared TWICE --
    `exp_config.models` for what is dispatched and a separate label list that
    every per-model denominator reads. The runner's own comment records what that
    costs: found 2026-08-30 when 6 ModelConfigs were supplied, the second list was
    left at its hardcoded 5, and the run REPORTED A 5-MODEL PANEL WHILE
    DISPATCHING A SIXTH with nothing warning at all. The runner now logs
    `** PANEL MISMATCH **` and PROCEEDS. Asking before a run spends anything is
    the point of a readiness surface, and it was the one question it did not ask.

    Found by reading an unadopted seat design, `roster_registry_2026-10-07.py`,
    whose answer to "what must a researcher edit to add a model" is ONE thing --
    and whose next paragraph is that the roster is declared twice.
    """

    def _m(self, label):
        class _C:
            def __init__(s, l):
                s.label = l
        return _C(label)

    def test_agreement_is_reported_when_the_lists_match(self):
        r = SR.roster_declarations_agree(
            [self._m("CC2"), self._m("Fable")], ["CC2", "Fable"])
        assert r["agree"] is True
        assert r["dispatched_not_counted"] == []
        assert r["counted_not_dispatched"] == []

    def test_a_seat_dispatched_but_not_counted_is_named(self):
        """Work paid for and dropped from every denominator -- the Fable case."""
        r = SR.roster_declarations_agree(
            [self._m("CC2"), self._m("Fable")], ["CC2"])
        assert r["agree"] is False
        assert r["dispatched_not_counted"] == ["Fable"]
        assert r["counted_not_dispatched"] == []

    def test_a_seat_counted_but_not_dispatched_is_named(self):
        """A denominator inflated by a seat that never answered."""
        r = SR.roster_declarations_agree([self._m("CC2")], ["CC2", "Gemini"])
        assert r["agree"] is False
        assert r["counted_not_dispatched"] == ["Gemini"]
        assert r["dispatched_not_counted"] == []

    def test_both_directions_are_reported_separately(self):
        """A total would say neither. The 2 differences mean different things."""
        r = SR.roster_declarations_agree(
            [self._m("CC2"), self._m("Fable")], ["CC2", "Gemini"])
        assert r["dispatched_not_counted"] == ["Fable"]
        assert r["counted_not_dispatched"] == ["Gemini"]

    def test_an_empty_list_is_not_agreement(self):
        """The vacuity trap: 2 empty lists are equal and prove nothing."""
        r = SR.roster_declarations_agree([], [])
        assert r["agree"] is False
        assert r["either_list_empty"] is True

    def test_the_surface_says_the_question_was_not_asked_without_both_lists(self):
        """Silence is worse than a stated gap: a UX must not assume it was asked."""
        r = SR.readiness()
        assert "not checked" in str(r["roster_declarations"])

    def test_the_ux_backend_reports_it_when_given_both(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "uxb3", REPO / "bench" / "ux_backend_2026-10-20.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        got = m.seats([self._m("CC2"), self._m("Fable")], counted_roster=["CC2"])
        assert got["rosters"]["agree"] is False
        assert got["rosters"]["dispatched_not_counted"] == ["Fable"]

    def test_the_runner_still_carries_the_comment_this_rests_on(self):
        """If the runner stops declaring the roster twice, re-measure rather than
        keeping a check for a shape that no longer exists."""
        runner = (REPO / "bench" / "reference_runner_v3.py").read_text()
        assert "THE TWO PANEL LISTS MUST AGREE" in runner, (
            "the runner no longer states the 2-list hazard; this check's premise "
            "may have been repaired at source, so re-measure before keeping it")
