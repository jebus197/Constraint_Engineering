"""Sev(f) is computed, the queue's count and bundle share one membership, and
an empty-ladder deferral is named -- the 2026-10-13 free-panel fixes, pinned.

THREE MECHANISMS, ONE ROUND, EACH WITH ITS EXECUTED FALSIFIER.

1. Sev(f) (Item 1). docs/MATHEMATICAL_APPENDIX.md section 7.7 specifies
   Sev(f) = W(class) * confidence * V(verification) and it was never computed:
   35 of 40 archived REFUTED findings carry non-zero severity (87.5000%,
   Wilson 95% [73.8879%, 94.5405%]; producer:
   scripts/severity_was_never_computed_from_the_model_2026-10-12.py).
   `compute_sev_f` + `stamp_sev_f` make it a DERIVED field, informative-only
   in v1 because 831 of 835 downward 0.7-cut crossers under V are V(None)
   halvings of UNVERIFIED claims (99.5210%, Wilson 95% [98.7748%, 99.8136%];
   producer: scripts/what_moves_when_v_is_applied_2026-10-13.py) -- gating
   V(None) would reward falsifier omission, the loophole the 2026-09-06
   one-directional rule exists to close.

2. Queue membership (Items 2/3). Executed 2026-10-13 against the pre-fix
   runner: a registry of 3 never-read criticals put irreducible_queue_count at
   3, fired build_irreducible_queue_alarm, and attached evidence for 0 items
   -- the sim45_memory_20260908T033012Z defect shape, reintroduced for the
   membership class the 2026-10-12 change added. Count and collector now both
   derive from `_irreducible_queue_members`.

3. Empty-ladder deferrals (Items 2/3). A sub-critical deferred to an EMPTY
   ladder reaches `ladder_empty_deferred_findings` (reporting; zero weight on
   convergence -- the founder's 2026-10-02 exclude-from-the-gate,
   name-it-in-the-report discipline). A CRITICAL in the same state fires the
   alarm at its FIRST occurrence when `cfg.alarm_on_empty_ladder` is on,
   because an empty ladder cannot be resolved by waiting; the flag defaults
   OFF and the next simulated run is its instrument.
"""
import types

import bench.reference_runner_v3 as rr


def _never_read_entry(sev):
    return {"status": "UNCONFIRMED", "severity": sev,
            "routing_history": [{"verdict": "UNRESOLVED", "resolved": False}],
            "verdicts": [], "falsifier_code": "", "falsifier_verdict": "",
            "routing_verdict_unreconciled": ""}


def _empty_ladder_entry(sev, boolean=True):
    e = {"status": "UNCONFIRMED", "severity": sev, "routing_deferred": True}
    if boolean:
        e["routing_ladder_empty"] = True
    else:
        e["routing_deferred_reason"] = (
            "routing ladder empty by construction: the roster carries no "
            "writer other than this finding's own source model, so no rung "
            "exists to try in any round")
    return e


class TestSevFIsComputedNotReported:
    def test_the_appendix_own_verified_examples(self):
        assert rr.compute_sev_f("HARD", 0.9, "CONFIRMED") == 0.90
        assert rr.compute_sev_f("HARD", 0.9, "REFUTED") == 0.00

    def test_the_key_property_a_disproved_finding_scores_zero(self):
        for conf in (0.0, 0.5, 1.0, None, "not a number"):
            for cls in ("HARD", "SOFT", None, "AMBIGUOUS"):
                assert rr.compute_sev_f(cls, conf, "REFUTED") == 0.0

    def test_every_default_is_the_stricter_reading(self):
        # Missing class -> HARD (section 1 of the core directives); missing
        # confidence -> 1.0; so omission can never LOWER the computed value.
        assert rr.compute_sev_f(None, None, "CONFIRMED") == 1.0
        assert rr.compute_sev_f("SOFT", None, "CONFIRMED") == 0.5
        assert rr.compute_sev_f(None, 2.0, "CONFIRMED") == 1.0  # clamped
        assert rr.compute_sev_f(None, -1.0, "CONFIRMED") == 0.0  # clamped

    def test_v_none_is_half_and_unrecognised_verdicts_fail_to_v_none(self):
        for verdict in (None, "", "UNTOOLABLE", "ERROR", "NON_DISCRIMINATING",
                        "SOMETHING_NEW"):
            assert rr.compute_sev_f("HARD", 1.0, verdict) == 0.5

    def test_the_stamp_is_a_default_off_no_op(self):
        reg = rr.FindingRegistry()
        reg.entries = {"C1": {"status": "OPEN", "severity": 0.85,
                              "falsifier_verdict": "REFUTED"}}
        assert rr.stamp_sev_f(reg, types.SimpleNamespace(), 3) == 0
        assert "sev_f" not in reg.entries["C1"]

    def test_the_stamp_never_touches_the_claimed_severity(self):
        reg = rr.FindingRegistry()
        reg.entries = {"C1": {"status": "OPEN", "severity": 0.85,
                              "falsifier_verdict": "REFUTED"},
                       "C2": {"status": "OPEN", "severity": 0.9,
                              "constraint_class": "SOFT", "confidence": 0.8,
                              "falsifier_verdict": "CONFIRMED"}}
        cfg = types.SimpleNamespace(sev_f_enabled=True)
        assert rr.stamp_sev_f(reg, cfg, 4) == 2
        assert reg.entries["C1"]["severity"] == 0.85
        assert reg.entries["C1"]["sev_f"]["value"] == 0.0
        assert reg.entries["C1"]["sev_f"]["informative_only"] is True
        assert reg.entries["C2"]["sev_f"]["value"] == 0.4  # 0.5 * 0.8 * 1.0
        assert reg.entries["C2"]["sev_f"]["constraint_class_defaulted"] is False
        assert reg.entries["C2"]["sev_f"]["confidence_defaulted"] is False


class TestTheCountAndTheBundleShareOneMembership:
    def test_the_executed_falsifier_now_passes(self):
        """Pre-fix: count 3, alarm fired, evidence 0. Now evidence == count."""
        reg = rr.FindingRegistry()
        reg.entries = {"C0001": _never_read_entry(0.9),
                       "C0002": _never_read_entry(0.9),
                       "C0003": _never_read_entry(0.4)}
        cfg = types.SimpleNamespace(max_irreducible_queue=2)
        alarm = rr.build_irreducible_queue_alarm(reg, cfg, round_idx=5)
        assert alarm is not None
        assert alarm["count"] == 3
        assert len(alarm["evidence"]) == alarm["count"], (
            "the bundle must name every item the count fired on -- an empty "
            "bundle on a fired alarm is the sim45 defect shape")
        assert {x["canonical_id"] for x in alarm["evidence"]} == {
            "C0001", "C0002", "C0003"}

    def test_split_equals_membership_counts(self):
        reg_entries = {
            "A": {"status": "OPEN", "severity": 0.9,
                  "irreducible_escalation": True},
            "B": {"status": "OPEN", "severity": 0.9, "routing_deferred": True},
            "C": _never_read_entry(0.3),
            "D": {"status": "REFUTED", "severity": 0.9,
                  "irreducible_escalation": True},  # terminal, excluded
        }
        members = rr._irreducible_queue_members(reg_entries)
        locked, deferred = rr._irreducible_queue_split(reg_entries)
        assert locked == sum(1 for _c, k in members if k == "ladder_exhausted")
        assert deferred == sum(1 for _c, k in members if k == "never_assessed")
        assert ("D", "ladder_exhausted") not in members


class TestAnEmptyLadderIsNamedAndACriticalOneCanAlarm:
    def test_subcritical_reaches_the_report_reader_not_the_alarm(self):
        reg = rr.FindingRegistry()
        reg.entries = {"C0020": _empty_ladder_entry(0.45, boolean=False)}
        cfg_on = types.SimpleNamespace(max_irreducible_queue=2,
                                       alarm_on_empty_ladder=True)
        assert rr.build_irreducible_queue_alarm(reg, cfg_on, 1) is None, (
            "a SUB-critical empty-ladder deferral must not halt the run")
        rows = rr.ladder_empty_deferred_findings(reg.entries)
        assert [r["canonical_id"] for r in rows] == ["C0020"]
        assert rows[0]["severity"] == 0.45

    def test_the_flag_defaults_off_and_off_is_byte_identical(self):
        assert rr.RunnerConfig().alarm_on_empty_ladder is False
        reg = rr.FindingRegistry()
        reg.entries = {"C0010": _empty_ladder_entry(0.9)}
        cfg_off = types.SimpleNamespace(max_irreducible_queue=2)
        assert rr.build_irreducible_queue_alarm(reg, cfg_off, 1) is None

    def test_one_structural_critical_fires_at_first_occurrence_when_enabled(self):
        reg = rr.FindingRegistry()
        reg.entries = {"C0010": _empty_ladder_entry(0.9)}
        cfg_on = types.SimpleNamespace(max_irreducible_queue=2,
                                       alarm_on_empty_ladder=True)
        alarm = rr.build_irreducible_queue_alarm(reg, cfg_on, 1)
        assert alarm is not None
        assert alarm["structural_empty_ladder"] == ["C0010"]
        assert len(alarm["evidence"]) == 1, (
            "a structural-only firing must still attach its evidence")

    def test_the_structural_predicate_reads_fact_then_fallback(self):
        assert rr._routing_deferred_structural(_empty_ladder_entry(0.9)) is True
        assert rr._routing_deferred_structural(
            _empty_ladder_entry(0.9, boolean=False)) is True
        # An equipment-failure deferral is NOT structural: retry can resolve it.
        assert rr._routing_deferred_structural(
            {"routing_deferred": True,
             "routing_deferred_reason": "not escalated at round 3: ..."}) is False
        assert rr._routing_deferred_structural({"routing_ladder_empty": True}) is False

    def test_sev_f_default_off_in_config(self):
        assert rr.RunnerConfig().sev_f_enabled is False
