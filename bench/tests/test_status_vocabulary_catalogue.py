"""The status vocabulary is registered, enforced, and catalogued.

WHAT THIS PINS DOWN. `experimental_notes/Design_Reviews_Bugzilla_And_Perturbation_2026-08-21.md`
agreed a status table (Q1, :59-69) in which CONFIRMED, REFUTED, CLOSED and
MERGED are TOOL-ONLY, and in which CORROBORATED and WITHHELD are the states a
model attestation is actually allowed to produce. Measured on 2026-08-22: the
blocking BEHAVIOUR had landed at five sites, but `WITHHELD` had 0 references in
`reference_runner_v3.py` and `CORROBORATED` had 1 — in a comment. The
model-quorum site wrote CONFIRMED from a COUNT OF OPINIONS into the same field
the falsifier gate writes after executing code, and nothing in the entry
recorded which of the two had happened.

The load-bearing test here is `TestAModelCanNeverWriteAToolOnlyStatus`: it
sweeps every registered status as a starting point and every tool-only status
as a request, and asserts the request never lands. Its positive control sits
beside it — a tool-adjudicated caller still writes all four — so the pair
cannot pass by refusing everything, and cannot pass by refusing nothing.
"""
from __future__ import annotations

import json

import pytest

from bench.dm._types import Finding
from bench import reference_runner_v3 as rr
from bench.reference_runner_v3 import FindingRegistry, _update_finding_statuses

# Reached through the module rather than by `from ... import` so that the
# absence of the vocabulary shows up as a FAILING ASSERTION in each test rather
# than as a collection error that never runs.
DESTRUCTIVE_OR_DEMONSTRATED = ("CONFIRMED", "CLOSED", "MERGED")

# Literal, so the sweep below parametrises even where the vocabulary is absent.
ALL_STATUSES = [
    "CLOSED", "CONFIRMED", "CONTESTED", "CORROBORATED", "DUPLICATE",
    "ESCALATED", "MERGED", "OPEN", "REFUTED", "REOPENED", "UNCONFIRMED",
    "WITHHELD",
]


def _vocab():
    v = getattr(rr, "FINDING_STATUS_" + "VOCABULARY", None)
    assert v is not None, (
        "reference_runner_v3 registers no status vocabulary; CORROBORATED and "
        "WITHHELD were agreed on 2026-08-21 and must be real statuses")
    return v


def _finding(fid="f1", model="M1", severity=0.9, description="a defect"):
    return Finding(
        finding_id=fid, model_id=model, round_idx=0, flaw_class=2,
        severity=severity, abstraction_index=0.5, description=description,
    )


def _registry(n=1, severity=0.9):
    reg = FindingRegistry()
    ids = [reg.register(_finding(fid=f"f{i}", severity=severity), "M1")
           for i in range(1, n + 1)]
    return reg, ids


# ═════════════════════════════════════════════════════════════════════════════
# 1. The vocabulary exists, and says what was agreed
# ═════════════════════════════════════════════════════════════════════════════

class TestTheVocabularyIsRegistered:
    def test_corroborated_and_withheld_are_registered_statuses(self):
        for name in ("CORROBORATED", "WITHHELD"):
            assert name in _vocab(), (
                f"{name} was agreed in the 2026-08-21 design review and must "
                f"be a real registered status, not prose")

    def test_every_status_carries_the_fields_a_machine_needs(self):
        required = {"meaning", "who_may_assert", "in_from", "out_to",
                    "evidence_required", "terminal", "live"}
        for name, spec in _vocab().items():
            missing = required - set(spec)
            assert not missing, f"{name} is missing {sorted(missing)}"
            assert spec["meaning"].strip(), f"{name} has no meaning"
            assert spec["evidence_required"].strip(), (
                f"{name} names no evidence requirement")

    def test_the_tool_only_set_is_exactly_the_agreed_one(self):
        for name in ("CONFIRMED", "REFUTED", "CLOSED", "MERGED"):
            assert name in rr.TOOL_ONLY_STATUSES, (
                f"{name} is TOOL-ONLY in the agreed table")
        for name in ("OPEN", "CORROBORATED", "CONTESTED"):
            assert name not in rr.TOOL_ONLY_STATUSES
            assert name in rr.MODEL_ASSERTABLE_STATUSES

    def test_corroborated_is_model_assertable_and_withheld_is_not(self):
        assert _vocab()["CORROBORATED"]["who_may_assert"] == (
            "model",)
        # WITHHELD is written BY the chokepoint that refused a merge — never
        # asserted directly by a panel.
        assert _vocab()["WITHHELD"]["who_may_assert"] == (
            "runner",)

    def test_both_new_statuses_are_live_and_non_terminal(self):
        """The design's whole point: withholding must not delete a finding,
        and corroboration must not settle one."""
        for name in ("CORROBORATED", "WITHHELD"):
            assert _vocab()[name]["live"] is True
            assert _vocab()[name]["terminal"] is False
            assert name in rr.LIVE_STATUSES

    def test_the_transition_rules_are_the_agreed_ones(self):
        corr = _vocab()["CORROBORATED"]
        assert "OPEN" in corr["in_from"]
        assert "CONFIRMED" in corr["out_to"], (
            "corroboration must be able to become a demonstration")
        withheld = _vocab()["WITHHELD"]
        assert "OPEN" in withheld["in_from"]
        assert "OPEN" in withheld["out_to"], (
            "back to OPEN on new evidence — the design's stated exit")

    def test_corroborated_is_flagged_as_attestation_not_measurement(self):
        assert "CORROBORATED" in rr.ATTESTED_STATUSES
        assert "CONFIRMED" not in rr.ATTESTED_STATUSES


# ═════════════════════════════════════════════════════════════════════════════
# 2. THE LOAD-BEARING CLAIM: a model attestation can never write a tool status
# ═════════════════════════════════════════════════════════════════════════════

class TestAModelCanNeverWriteAToolOnlyStatus:
    @pytest.mark.parametrize("requested", DESTRUCTIVE_OR_DEMONSTRATED)
    @pytest.mark.parametrize("start", ALL_STATUSES)
    def test_no_starting_status_lets_a_model_reach_it(self, start, requested):
        """Sweep the whole state space. There is no start state from which a
        model-adjudicated call reaches CONFIRMED, CLOSED or MERGED."""
        reg, (cid,) = _registry()
        reg.entries[cid]["status"] = start          # place it directly
        target = reg.register(_finding(fid="f2"), "M2")
        reg.resolve(cid, requested, 3, merged_into=target,
                    adjudicator="model",
                    evidence="M1 and M2 both say so",
                    mechanism="panel_attestation")
        after = reg.entries[cid]["status"]
        # The claim is about ARRIVAL, not about the label: a finding already
        # sitting in a tool-only status stays there (the call is refused
        # outright), but no model-adjudicated call may MOVE one into it.
        assert after == start or after != requested, (
            f"a model attestation reached {requested} from {start}")
        assert not [t for t in reg.entries[cid].get("status_log", [])
                    if t["to"] == requested], (
            f"a model attestation logged a transition TO {requested}")
        assert reg.entries[cid]["refused_transitions"][-1]["requested"] == (
            requested), "the refusal must be on the record"

    @pytest.mark.parametrize("requested", DESTRUCTIVE_OR_DEMONSTRATED)
    def test_the_refusal_is_recorded_with_its_reason(self, requested):
        reg, (cid,) = _registry()
        target = reg.register(_finding(fid="f2"), "M2")
        reg.resolve(cid, requested, 3, merged_into=target,
                    adjudicator="model", evidence="two models agreed",
                    mechanism="panel_attestation")
        refusals = reg.entries[cid]["refused_transitions"]
        assert [r["requested"] for r in refusals] == [requested]
        assert "TOOL-ONLY" in refusals[0]["reason"]
        assert refusals[0]["evidence"] == "two models agreed"

    def test_a_model_confirm_becomes_corroborated(self):
        reg, (cid,) = _registry()
        reg.resolve(cid, "CONFIRMED", 2, adjudicator="model",
                    evidence="M2:CONFIRM@r2", mechanism="quorum")
        e = reg.entries[cid]
        assert e["status"] == "CORROBORATED"
        assert e["status_adjudicator"] == "runner"
        assert e["status_log"][-1]["refused"] == "CONFIRMED"

    def test_a_model_merge_becomes_withheld_and_keeps_the_pointer(self):
        reg, ids = _registry(n=2)
        cid, target = ids
        reg.resolve(cid, "MERGED", 2, merged_into=target, adjudicator="model",
                    evidence="two models proposed it", mechanism="merge_vote")
        e = reg.entries[cid]
        assert e["status"] == "WITHHELD"
        assert e["merge_candidate_of"] == target
        assert e["merge_blocked_reason"] == "two models proposed it"
        assert "merged_into" not in e, (
            "a withheld merge must NOT write the pointer — there is no unmerge")

    def test_closed_and_refuted_are_refused_outright(self):
        """Neither has a non-destructive equivalent: both are claims about an
        execution. The status must be left exactly as it was."""
        for requested in ("CLOSED", "REFUTED"):
            reg, (cid,) = _registry()
            reg.resolve(cid, requested, 2, adjudicator="model",
                        evidence="a model said so", mechanism="vote")
            assert reg.entries[cid]["status"] == "OPEN"
            assert reg.entries[cid]["refused_transitions"][0][
                "substituted"] is None

    def test_repeated_attestation_does_not_reset_the_staleness_timer(self):
        """A no-op re-attestation must stay countable without bumping
        last_status_change_round — otherwise nothing ever ages out."""
        reg, (cid,) = _registry()
        reg.resolve(cid, "CONFIRMED", 2, adjudicator="model", evidence="e")
        assert reg.entries[cid]["last_status_change_round"] == 2
        reg.resolve(cid, "CONFIRMED", 9, adjudicator="model", evidence="e")
        assert reg.entries[cid]["last_status_change_round"] == 2
        assert reg.entries[cid]["attestation_count"] == 2


class TestToolAuthorityIsUntouched:
    """The positive control. Without it, a guard that refused EVERYTHING would
    pass the class above."""

    @pytest.mark.parametrize("status", ["CONFIRMED", "REFUTED", "CLOSED"])
    def test_a_tool_still_writes_every_tool_only_status(self, status):
        reg, (cid,) = _registry()
        reg.resolve(cid, status, 4, adjudicator="tool",
                    evidence="falsifier fired, exit 1", mechanism="falsifier")
        assert reg.entries[cid]["status"] == status
        assert reg.entries[cid]["status_adjudicator"] == "tool"

    def test_the_default_caller_keeps_its_authority(self):
        """Every pre-existing call site passes three positional arguments and
        must keep writing what it always wrote."""
        reg, (cid,) = _registry()
        reg.resolve(cid, "CONFIRMED", 7)
        assert reg.entries[cid]["status"] == "CONFIRMED"
        assert reg.entries[cid]["last_status_change_round"] == 7

    def test_a_tool_merge_still_merges(self):
        reg, ids = _registry(n=2)
        cid, target = ids
        reg.resolve(cid, "MERGED", 4, merged_into=target, adjudicator="tool",
                    evidence="adjudicate_by_repair: SAME both directions",
                    mechanism="counterfactual_repair")
        assert reg.entries[cid]["status"] == "MERGED"
        assert reg.entries[cid]["merged_into"] == target


# ═════════════════════════════════════════════════════════════════════════════
# 3. The live runner writes them
# ═════════════════════════════════════════════════════════════════════════════

class TestTheLiveRunnerUsesTheVocabulary:
    def test_a_confirm_quorum_reaches_corroborated_not_confirmed(self):
        reg, (cid,) = _registry()
        reg.add_verdict(cid, "M2", "CONFIRM", round_idx=1, evidence="seen")
        reg.add_verdict(cid, "M3", "CONFIRM", round_idx=1, evidence="seen")
        _update_finding_statuses(reg, 1)
        e = reg.entries[cid]
        assert e["status"] == "CORROBORATED", (
            "a count of opinions is an attestation, not a demonstration")
        assert e["refused_transitions"][0]["requested"] == "CONFIRMED"
        assert "M2:CONFIRM@r1" in e["status_evidence"]
        assert e["status_mechanism"].startswith("model_confirm_quorum")

    def test_a_corroborated_critical_still_blocks_the_state_gate(self):
        """CORROBORATED is not a measurement, so an open critical holding it is
        still an open critical."""
        reg, (cid,) = _registry()
        reg.add_verdict(cid, "M2", "CONFIRM", round_idx=1)
        reg.add_verdict(cid, "M3", "CONFIRM", round_idx=1)
        _update_finding_statuses(reg, 1)
        assert reg.entries[cid]["status"] == "CORROBORATED"
        assert reg.open_crit_high_count() == 1

    def test_a_merge_vote_reaches_withheld_and_stays_countable(self):
        reg, ids = _registry(n=2)
        cid, target = ids
        for m in ("M2", "M3"):
            reg.add_verdict(cid, m, "MERGE", round_idx=1,
                            evidence=f"merged_into={target}")
        _update_finding_statuses(reg, 1)
        e = reg.entries[cid]
        assert e["status"] == "WITHHELD"
        assert e["merge_candidate_of"] == target
        assert "tool verdict" in e["merge_blocked_reason"]
        assert reg.open_crit_high_count() == 2, (
            "withholding must not remove the finding from the gate")

    def test_a_withheld_finding_is_still_judged_on_its_own_merits(self):
        """The 2026-08-21 repair, preserved: MERGE votes must not pin a
        finding out of the lifecycle."""
        reg, ids = _registry(n=2)
        cid, target = ids
        for m in ("M2", "M3"):
            reg.add_verdict(cid, m, "MERGE", round_idx=1,
                            evidence=f"merged_into={target}")
            reg.add_verdict(cid, m, "CONFIRM", round_idx=1)
        _update_finding_statuses(reg, 1)
        assert reg.entries[cid]["status"] == "CORROBORATED"


# ═════════════════════════════════════════════════════════════════════════════
# 4. The catalogue
# ═════════════════════════════════════════════════════════════════════════════

class TestTheCatalogueExport:
    def test_one_record_per_finding(self):
        reg, ids = _registry(n=3)
        records = rr.export_finding_catalogue(reg)
        assert len(records) == 3
        assert [r["canonical_id"] for r in records] == ids

    def test_every_record_carries_status_evidence_and_mechanism(self):
        reg, (cid,) = _registry()
        reg.resolve(cid, "CONFIRMED", 2, adjudicator="tool",
                    evidence="falsifier exit 1 vs sha abc123",
                    mechanism="falsifier_rerun")
        (rec,) = rr.export_finding_catalogue(reg)
        assert rec["status"] == "CONFIRMED"
        assert rec["evidence"] == "falsifier exit 1 vs sha abc123"
        assert rec["mechanism"] == "falsifier_rerun"
        assert rec["adjudicator"] == "tool"
        assert rec["status_meaning"] == (
            _vocab()["CONFIRMED"]["meaning"])
        assert rec["tool_only"] is True

    def test_an_unresolved_finding_is_catalogued_as_filed(self):
        reg, (cid,) = _registry()
        (rec,) = rr.export_finding_catalogue(reg)
        assert rec["status"] == "OPEN"
        assert rec["mechanism"] == "registration"
        assert rec["adjudicator"] == "model"
        assert rec["evidence"] == "filed by M1"

    def test_demonstrated_is_true_only_where_a_falsifier_fired(self):
        reg, ids = _registry(n=2)
        attested, demonstrated = ids
        reg.resolve(attested, "CONFIRMED", 1, adjudicator="model",
                    evidence="two models agreed")
        reg.entries[demonstrated]["falsifier_verdict"] = "CONFIRMED"
        reg.resolve(demonstrated, "CONFIRMED", 1, adjudicator="tool",
                    evidence="fired", mechanism="falsifier_rerun")
        by_id = {r["canonical_id"]: r for r in rr.export_finding_catalogue(reg)}
        assert by_id[attested]["demonstrated"] is False
        assert by_id[attested]["status"] == "CORROBORATED"
        assert by_id[demonstrated]["demonstrated"] is True

    def test_the_record_carries_the_refusal_trail(self):
        reg, (cid,) = _registry()
        reg.resolve(cid, "CONFIRMED", 1, adjudicator="model", evidence="votes")
        (rec,) = rr.export_finding_catalogue(reg)
        assert rec["refused_transitions"][0]["requested"] == "CONFIRMED"
        assert rec["transitions"][0]["from"] == "OPEN"
        assert rec["transitions"][0]["to"] == "CORROBORATED"

    def test_it_writes_json_lines_a_machine_can_read_back(self, tmp_path):
        reg, ids = _registry(n=2)
        reg.resolve(ids[0], "CONFIRMED", 1, adjudicator="model",
                    evidence="votes", mechanism="quorum")
        path = tmp_path / "catalogue.jsonl"
        rr.export_finding_catalogue(reg, path)
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 2
        parsed = [json.loads(ln) for ln in lines]
        assert parsed[0]["status"] == "CORROBORATED"
        assert parsed[0]["vocabulary_version"] == rr.STATUS_VOCABULARY_VERSION
        for rec in parsed:
            assert rec["status_is_registered"] is True

    def test_the_vocabulary_ships_with_the_catalogue(self, tmp_path):
        path = tmp_path / "vocab.json"
        doc = rr.export_status_vocabulary(path)
        loaded = json.loads(path.read_text(encoding="utf-8"))
        assert loaded == json.loads(json.dumps(doc))
        assert "CORROBORATED" in loaded["statuses"]
        assert "WITHHELD" in loaded["statuses"]
        assert sorted(loaded["tool_only_statuses"]) == sorted(
            rr.TOOL_ONLY_STATUSES)
        assert loaded["model_assertion_substitute"] == dict(
            rr.MODEL_ASSERTION_SUBSTITUTE)
        assert loaded["statuses"]["CONFIRMED"]["tool_only"] is True
        assert loaded["statuses"]["CORROBORATED"]["tool_only"] is False

    def test_an_unregistered_status_is_flagged_not_silently_accepted(self):
        """A status the vocabulary does not know must be visible as such —
        a catalogue that renders anything as legitimate catalogues nothing."""
        reg, (cid,) = _registry()
        reg.entries[cid]["status"] = "SORT_OF_FINE"
        (rec,) = rr.export_finding_catalogue(reg)
        assert rec["status_is_registered"] is False
        assert "UNREGISTERED" in rec["status_meaning"]
