"""T04 — a crashed falsifier must not write a terminal status (2026-08-22).

A falsifier that returned ERROR (it crashed) or UNTOOLABLE (there was nothing
to run) did not measure anything: it is an EQUIPMENT FAILURE, not evidence in
either direction. Founder ruling 2026-08-22: equipment error counts as
UNRESOLVED, escalates to HIL, and is subject to re-routing.

MEASURED 2026-08-22: 4 of 24 findings whose falsifier returned ERROR or
UNTOOLABLE still carried a terminal status; two carried REFUTED with
verified=False.

The three leak paths pinned here:

  1. ``auto_resolve_contested`` writes REFUTED on three CHALLENGE votes and
     never checks whether the falsifier ran. It executes AFTER the gate in the
     same round, so a vote overwrote the gate's escalation in the same breath.
  2. The gate's own demotion read only ``status == "CONFIRMED"``, so a REFUTED
     written by the earlier vote pass survived an ERROR verdict untouched.
  3. ``_apply_routing`` admitted only ERROR for sub-critical re-routing, so an
     UNTOOLABLE finding sat in HIL limbo while the ladder — the one mechanism
     built to obtain the missing falsifier — stood idle.

Gate verdicts below come from the REAL ``reverify_falsifier`` executing real
code (no stubbed verdicts), so the tests pin what the runner actually does.
"""
from __future__ import annotations

from types import SimpleNamespace

from bench.dm._types import Finding
from bench.reference_runner_v2 import (
    FindingRegistry, RunnerConfig, apply_falsifier_verdicts, _apply_routing,
)


BROKEN = "import nonexistent_module_xyz_t04"   # reverify -> ERROR
DEMONSTRATION = "assert False, 'real defect'"  # reverify -> CONFIRMED
CLEAN = "assert True"                          # reverify -> REFUTED


def _mk(fid, sev, fcode):
    return Finding(finding_id=fid, model_id="DeepSeek", round_idx=0,
                   flaw_class=2, severity=sev, abstraction_index=0.5,
                   description=f"claim {fid}", falsifier_code=fcode)


def _register(reg, fid, sev, fcode, status="OPEN"):
    cid = reg.register(_mk(fid, sev, fcode), "DeepSeek")
    reg.entries[cid]["status"] = status
    return cid


def _gate(reg):
    apply_falsifier_verdicts(
        reg, 1, cfg=RunnerConfig(falsifier_gate_enabled=True), repo_root=".")


# ── leak path 1: a vote buried an errored falsifier ──────────────────────────

class TestVotesCannotBuryAnErroredFalsifier:
    def test_contested_finding_with_errored_falsifier_is_not_vote_refuted(self):
        """THE T04 DEFECT. The gate records ERROR and escalates; three
        CHALLENGE votes then write REFUTED in the same round. The record then
        says a test that never ran dropped the claim."""
        reg = FindingRegistry()
        cid = _register(reg, "f1", 0.5, BROKEN, status="CONTESTED")
        for model in ("CC2", "Codex", "Gemini"):
            reg.add_verdict(cid, model, "CHALLENGE", 1)
        _gate(reg)
        e = reg.entries[cid]
        assert e["falsifier_verdict"] == "ERROR"

        reg.auto_resolve_contested(1)  # the vote pass; runs after the gate

        assert e["status"] != "REFUTED", (
            "three CHALLENGE votes refuted a finding whose falsifier crashed "
            "— a terminal status written by a test that never ran")
        assert e["status"] == "UNCONFIRMED"
        assert e["verified"] is False
        assert e["escalated"] is True
        assert e.get("equipment_failure") is True
        assert "ERROR" in e.get("hil_reason", "")

    def test_no_terminal_status_survives_an_equipment_failure(self):
        """CLOSED, CONFIRMED, REFUTED, DUPLICATE and MERGED are ALL refused
        while the finding's only verdict is an equipment failure."""
        reg = FindingRegistry()
        cid = _register(reg, "f2", 0.5, BROKEN)
        other = _register(reg, "f3", 0.5, DEMONSTRATION)
        _gate(reg)
        e = reg.entries[cid]
        for status in ("CLOSED", "CONFIRMED", "REFUTED", "DUPLICATE"):
            reg.resolve(cid, status, 2)
            assert e["status"] == "UNCONFIRMED", f"{status} was written"
        reg.resolve(cid, "MERGED", 2, merged_into=other)
        assert e["status"] == "UNCONFIRMED"
        assert e.get("merged_into") is None, (
            "a finding whose falsifier never ran was merged away")


# ── leak path 2: the gate's demotion read only CONFIRMED ─────────────────────

class TestGateDemotesEveryTerminalStatus:
    def test_status_already_refuted_before_the_gate_is_demoted(self):
        """The vote-based status pass runs BEFORE the gate; it can already
        have written REFUTED. An ERROR verdict must demote it — this is the
        measured 'REFUTED with verified=False' pair."""
        reg = FindingRegistry()
        cid = _register(reg, "f4", 0.5, BROKEN, status="REFUTED")
        _gate(reg)
        e = reg.entries[cid]
        assert e["falsifier_verdict"] == "ERROR"
        assert e["status"] == "UNCONFIRMED"
        assert e["verified"] is False
        assert e["escalated"] is True

    def test_untoolable_critical_refuted_status_is_demoted(self):
        """Same defect, UNTOOLABLE flavour: a critical with no falsifier whose
        status a vote had set REFUTED."""
        reg = FindingRegistry()
        cid = _register(reg, "f5", 0.8, "", status="REFUTED")
        _gate(reg)
        e = reg.entries[cid]
        assert e["falsifier_verdict"] == "UNTOOLABLE"
        assert e["status"] == "UNCONFIRMED"
        assert e["escalated"] is True

    def test_untoolable_critical_confirmed_still_demoted(self):
        """Regression pin for the behaviour that already worked."""
        reg = FindingRegistry()
        cid = _register(reg, "f6", 0.8, "", status="CONFIRMED")
        _gate(reg)
        e = reg.entries[cid]
        assert e["status"] == "UNCONFIRMED"
        assert e["escalated"] is True


# ── leak path 3: UNTOOLABLE never reached the routing ladder ─────────────────

class TestEquipmentFailureIsReRouted:
    def _routing(self, monkeypatch, verdict_obj):
        calls = []

        def fake_route(finding, models, confirmed, resolve_fn, reverify, sim):
            calls.append(finding["id"])
            return verdict_obj

        import bench.routing as routing_mod
        monkeypatch.setattr(routing_mod, "route", fake_route)
        exp_config = SimpleNamespace(models=[SimpleNamespace(label="CC2")])
        return calls, exp_config, RunnerConfig(routing_enabled=True)

    def test_subcritical_untoolable_enters_the_routing_ladder(self, monkeypatch):
        """'subject to re-routing'. Before T04 the admission read only ERROR,
        so an UNTOOLABLE sub-critical was parked in HIL for ever with the
        absorber standing idle."""
        unresolved = SimpleNamespace(verdict="", resolved=False,
                                     duplicate_of=None, falsifier_code="",
                                     model_used="")
        calls, exp_config, cfg = self._routing(monkeypatch, unresolved)
        reg = FindingRegistry()
        cid = _register(reg, "f7", 0.3, "", status="UNCONFIRMED")
        reg.entries[cid]["falsifier_verdict"] = "UNTOOLABLE"
        reg.entries[cid]["escalated"] = True
        _apply_routing(reg, 6, exp_config, cfg=cfg)
        assert calls == [cid], (
            "an UNTOOLABLE sub-critical must be re-routed like an ERROR one")

    def test_routed_resolution_still_confirms(self, monkeypatch):
        """The guard must not block the repair: a ladder rung that produces a
        CONFIRMED demonstration replaces the verdict and settles the finding."""
        resolved = SimpleNamespace(verdict="CONFIRMED", resolved=True,
                                   duplicate_of=None,
                                   falsifier_code="assert False, 'shown'",
                                   model_used="CC2")
        calls, exp_config, cfg = self._routing(monkeypatch, resolved)
        reg = FindingRegistry()
        cid = _register(reg, "f8", 0.3, "", status="UNCONFIRMED")
        reg.entries[cid]["falsifier_verdict"] = "UNTOOLABLE"
        reg.entries[cid]["escalated"] = True
        _apply_routing(reg, 6, exp_config, cfg=cfg)
        e = reg.entries[cid]
        assert e["status"] == "CONFIRMED"
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert e["verified"] is True
        assert e["escalated"] is False


# ── the guard must not block real evidence ───────────────────────────────────

class TestRealEvidenceStillSettlesFindings:
    def test_demonstration_still_confirms(self):
        reg = FindingRegistry()
        cid = _register(reg, "f9", 0.8, DEMONSTRATION)
        _gate(reg)
        e = reg.entries[cid]
        assert e["falsifier_verdict"] == "CONFIRMED"
        assert e["status"] == "CONFIRMED" and e["verified"] is True

    def test_clean_run_still_drops_a_subcritical(self):
        reg = FindingRegistry()
        cid = _register(reg, "f10", 0.5, CLEAN)
        _gate(reg)
        assert reg.entries[cid]["status"] == "REFUTED"

    def test_finding_with_no_verdict_resolves_unchanged(self):
        """The guard keys on the verdict, never on its absence — the gate is
        default-off and vote-only runs must stay byte-identical."""
        reg = FindingRegistry()
        cid = _register(reg, "f11", 0.5, "")
        reg.resolve(cid, "CLOSED", 1)
        assert reg.entries[cid]["status"] == "CLOSED"

    def test_a_later_demonstration_lifts_the_guard(self):
        """Equipment failure is UNRESOLVED, not unclosable: every legitimate
        repair path (gate, ladder, sweep) replaces the verdict BEFORE
        resolving, and that must settle the finding."""
        reg = FindingRegistry()
        cid = _register(reg, "f12", 0.5, BROKEN)
        _gate(reg)
        e = reg.entries[cid]
        assert e["status"] == "OPEN"  # escalated, and NOT terminal
        e["falsifier_verdict"] = "CONFIRMED"
        reg.resolve(cid, "CONFIRMED", 2)
        assert e["status"] == "CONFIRMED"
