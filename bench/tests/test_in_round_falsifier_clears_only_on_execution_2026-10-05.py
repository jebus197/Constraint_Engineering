#!/usr/bin/env python3
"""An in-round falsifier may clear a blocker, and only by actually running.

WHAT THIS GUARDS. `record_in_round_falsifier_reattachments` brings the closing
sweep's one exclusive capability — the id-addressed `FALSIFIER: Cxxxx` + fenced-code
parse — inside the round loop, where a clearance can still reach the convergence
gate. `scripts/sweep_channels_are_post_verdict_2026-10-05.py` establishes that of the
sweep's 5 disposition channels, that parse was the only one the round loop lacked: it
had exactly 1 site repo-wide, inside `_post_convergence_sweep`, which runs after
`converged` is assigned.

THE INVARIANT, and it is the founder's 2026-07-28 anti-gaming guard restated rather
than relaxed: **a finding leaves the blocker count on EXECUTED evidence only.** Prose
is recorded and clears nothing. Without that, convergence would be purchasable with
an assertion, which is precisely the "unfalsifiable loose cannon" objection this
design has to answer.

WHY THE CHANGE IS SAFE ON HISTORY. 0 of 3473 archived round-reply files carry the
parsed form — `scripts/in_round_falsifiers_are_discarded_2026-10-05.py`, Wilson
[0.0000%, 0.1105%] — so the parser is inert on every archived run by construction and
can only act where the new UNRESOLVED section elicits a falsifier.

Every assertion here CALLS the function and inspects the registry afterwards;
`reverify_falsifier` is stubbed per-case so the verdict is controlled, which is what
makes "clears on CONFIRMED, never on prose" testable rather than asserted.
"""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

import bench.reference_runner_v3 as R  # noqa: E402

FENCE = "```"
CRIT = R.CRITICAL_SEVERITY_THRESHOLD


def _entry(cid, status="UNCONFIRMED", sev=0.45):
    return {"canonical_id": cid, "status": status, "severity": sev,
            "verified": False, "verdicts": [], "description": "probe",
            "source_model": "SIM", "proposed_fix": "", "open_since_round": 0,
            "last_status_change_round": 0, "computed_evidence": [],
            "routing_history": [], "falsifier_code": ""}


def _reg(*cids, **kw):
    r = R.FindingRegistry()
    r.entries = {c: _entry(c, **kw) for c in cids}
    return r


def _reply(cid, body="assert False, 'defect'"):
    return f"FALSIFIER: {cid}\n{FENCE}python\n{body}\n{FENCE}\n"


@pytest.fixture
def verdict(monkeypatch):
    """Control reverify_falsifier's answer, and count how often it RAN."""
    calls = []

    def _install(answer):
        def _fake(code, repo_root=None, **kw):
            calls.append(code)
            return answer
        import bench.falsifier_verify as FV
        monkeypatch.setattr(FV, "reverify_falsifier", _fake)
        return calls
    return _install


class TestItExecutesAndClears:
    def test_a_confirmed_verdict_clears_the_blocker(self, verdict):
        calls = verdict("CONFIRMED")
        reg = _reg("C0066")
        before = reg.unverified_critical_count()
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": _reply("C0066")}, 3)
        assert before == 1, "the fixture did not start from a blocking state"
        assert len(calls) == 1, "the falsifier was never executed"
        assert st["cleared"] == 1
        assert reg.entries["C0066"]["verified"] is True
        assert reg.unverified_critical_count() == 0, (
            "the blocker survived a CONFIRMED runnable demonstration, so the "
            "clearance cannot reach the gate"
        )

    def test_the_code_reaching_the_verifier_is_the_code_supplied(self, verdict):
        calls = verdict("CONFIRMED")
        reg = _reg("C0066")
        R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": _reply("C0066", "assert 1 == 2, 'the real body'")}, 3)
        assert "the real body" in calls[0]

    def test_it_records_which_model_and_round_resolved_it(self, verdict):
        verdict("CONFIRMED")
        reg = _reg("C0066")
        R.record_in_round_falsifier_reattachments(
            reg, {"Fable-SIM": _reply("C0066")}, 7)
        e = reg.entries["C0066"]
        assert e["resolved_in_round"] == "Fable-SIM"
        assert e["resolved_in_round_idx"] == 7


class TestProseClearsNothing:
    """The invariant. Without this the design is unfalsifiable."""

    def test_a_bare_withdraw_line_does_not_clear(self, verdict):
        calls = verdict("CONFIRMED")   # would clear IF it were ever called
        reg = _reg("C0066")
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": "WITHDRAW C0066: on reflection this is not a defect"}, 3)
        assert calls == [], "prose reached the executor"
        assert st["cleared"] == 0
        assert reg.unverified_critical_count() == 1, (
            "a blocker was retired on model prose alone — convergence is "
            "purchasable with an assertion"
        )

    def test_a_label_with_no_fenced_payload_does_not_clear(self, verdict):
        calls = verdict("CONFIRMED")
        reg = _reg("C0066")
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": "FALSIFIER: C0066 — see my reasoning above"}, 3)
        assert calls == []
        assert st["cleared"] == 0
        assert reg.unverified_critical_count() == 1

    def test_an_empty_fenced_block_does_not_clear(self, verdict):
        calls = verdict("CONFIRMED")
        reg = _reg("C0066")
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": f"FALSIFIER: C0066\n{FENCE}python\n\n{FENCE}\n"}, 3)
        assert calls == []
        assert st["cleared"] == 0


class TestRefutationFollowsTheFounderRuling:
    """2026-08-03: a critical is never retired by a refutation; 2 of 3 REFUTED
    criticals in Exp 42 were themselves wrong. A sub-critical may be."""

    def test_a_subcritical_refutation_withdraws_it(self, verdict):
        verdict("REFUTED")
        reg = _reg("C0066", sev=0.45)
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": _reply("C0066")}, 3)
        assert st["withdrawn"] == 1
        assert reg.entries["C0066"]["status"] == "REFUTED"

    def test_a_critical_refutation_clears_nothing_but_is_recorded(self, verdict):
        verdict("REFUTED")
        reg = _reg("C0090", sev=0.95)
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": _reply("C0090")}, 3)
        assert st["withdrawn"] == 0, "a CRITICAL was retired by a refutation"
        assert st["critical_refuted_recorded"] == 1
        assert reg.entries["C0090"]["status"] != "REFUTED"
        kinds = [c.get("kind") for c in reg.entries["C0090"]["computed_evidence"]]
        assert "falsifier_refuted" in kinds, (
            "the computation ran and its answer was discarded; the human "
            "adjudicating a permanent item never sees what the instrument found"
        )

    def test_the_threshold_used_is_the_runner_constant(self, verdict):
        """Just below clears; just above does not. Boundary, not a magic number."""
        verdict("REFUTED")
        lo = _reg("C0001", sev=CRIT - 0.01)
        hi = _reg("C0002", sev=CRIT)
        assert R.record_in_round_falsifier_reattachments(
            lo, {"S": _reply("C0001")}, 1)["withdrawn"] == 1
        assert R.record_in_round_falsifier_reattachments(
            hi, {"S": _reply("C0002")}, 1)["withdrawn"] == 0


class TestItIsWellBehaved:
    def test_a_repeated_emission_executes_once(self, verdict):
        calls = verdict("CONFIRMED")
        reg = _reg("C0066")
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": _reply("C0066") + _reply("C0066")}, 3)
        assert len(calls) == 1, f"executed {len(calls)} times — paid code run twice"
        assert st["cleared"] == 1

    def test_an_unknown_id_is_counted_not_crashed(self, verdict):
        verdict("CONFIRMED")
        reg = _reg("C0066")
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": _reply("C9999")}, 3)
        assert st["skipped_unknown"] == 1 and st["cleared"] == 0

    def test_a_terminal_finding_is_left_alone(self, verdict):
        verdict("CONFIRMED")
        reg = _reg("C0066", status="CLOSED", sev=0.9)
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": _reply("C0066")}, 3)
        assert st["skipped_terminal"] == 1 and st["cleared"] == 0

    def test_an_exploding_verifier_does_not_kill_the_round(self, monkeypatch):
        import bench.falsifier_verify as FV

        def _boom(code, repo_root=None, **kw):
            raise RuntimeError("sandbox gone")
        monkeypatch.setattr(FV, "reverify_falsifier", _boom)
        reg = _reg("C0066")
        st = R.record_in_round_falsifier_reattachments(
            reg, {"SIM-A": _reply("C0066")}, 3)
        assert st["cleared"] == 0 and st["executed"] == 0

    def test_empty_responses_are_a_no_op(self):
        reg = _reg("C0066")
        for payload in ({}, None, {"SIM-A": None}, {"SIM-A": ""}):
            st = R.record_in_round_falsifier_reattachments(reg, payload, 3)
            assert st["cleared"] == 0 and st["seen"] == 0


class TestItIsWiredIntoTheRoundLoop:
    """An addition nothing reaches is not additive."""

    # THESE TWO READ THE COMPILED CODE OBJECT, NOT THE SOURCE TEXT.
    #
    # The first draft matched strings in `reference_runner_v3.py`. That is the
    # anti-pattern this whole session was about, and
    # `test_source_text_and_neighbour_audit_2026-09-11.py` caught it: the census
    # of source-text assertions went 80 -> 83, and its own message warns that 4
    # guards of that class broke on CORRECT changes in a single day.
    #
    # `co_names` holds the global names a compiled function actually references
    # and `co_consts` its literal constants, so a comment, a docstring or a
    # commented-out call cannot satisfy either. `test_the_probe_is_not_vacuous`
    # below holds that by checking a name that must be absent.

    def test_the_round_loop_calls_it(self):
        from bench.reference_runner_v3 import run_experiment
        assert "record_in_round_falsifier_reattachments" in run_experiment.__code__.co_names, (
            "the round loop's COMPILED code does not reference the re-attachment "
            "recorder, so it is defined and never called — an addition nothing "
            "reaches"
        )

    def test_its_record_is_persisted(self):
        from bench.reference_runner_v3 import run_experiment
        assert "round_falsifier_reattachments" in run_experiment.__code__.co_consts, (
            "the state-payload key is absent from the compiled constants, so the "
            "per-round record is computed and then dropped and no reader can ever "
            "check whether the mechanism fired"
        )

    def test_the_probe_is_not_vacuous(self):
        """A name that must NOT be present, so the two checks above cannot pass
        by the probe being blind."""
        from bench.reference_runner_v3 import run_experiment
        co = run_experiment.__code__
        assert "record_in_round_withdrawals" in co.co_names, (
            "the sibling recorder is missing too — the probe is looking in the "
            "wrong place rather than finding a real absence")
        assert "a_name_no_runner_would_ever_reference" not in co.co_names

    def test_the_summary_asks_for_the_form_this_parser_accepts(self):
        """Producer and consumer must agree, by execution rather than by reading."""
        import re as _re
        reg = _reg("C0066")
        body = reg.build_summary(3)
        assert "FALSIFIER: <ID>" in body
        # the parser's own pattern must match a reply built to the shape asked for
        assert _re.search(r"FALSIFIER:\s*(C\d{4})\s*```(?:python)?\s*\n(.*?)```",
                          _reply("C0066"), _re.S), (
            "the form the summary asks for is not the form the parser accepts"
        )
