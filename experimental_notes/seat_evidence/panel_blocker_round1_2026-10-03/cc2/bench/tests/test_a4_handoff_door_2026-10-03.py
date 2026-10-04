# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'panel_blocker_round1_2026-10-03', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3027a25267b30d258d073e88b3f1e2dfb4be05eb8a0e8ab51139d3c7339b55a0
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A4's recorded-handoff door — panel round 1, 2026-10-03 (study_run1b).

EXECUTES THE REAL MODULE against the REAL archived registry. Nothing here
asserts on source text: every assertion is the return value of a shipped
function called on a registry rehydrated through `FindingRegistry.from_dict`.

Four properties:
  1. POSITION A IS INERT. Deleting the `severity >= 0.7` clause from the
     `exhausted` valve leaves A4 at 2 on study_run1b's registry at every round
     tested, because `has_reviews` is False for both blockers.
  2. THE DOOR DRAINS A4 on the real archived state (2 -> 0) and the gate then
     returns converged.
  3. THE DOOR IS NOT A DEAD-INSTRUMENT RELEASE. Five adversarial mutants of a
     released entry each put it straight back in the count.
  4. EXCLUDED IMPLIES REPORTED over randomised registries.

MUTATION CHECK: reverting the fix fails test_door_drains_a4_on_the_real_run,
test_excluded_implies_reported and test_predicate_exists_and_is_severity_free
(AttributeError / count 2 != 0). Test 1 and the mutant test pass either way by
construction -- that is the point of test 1.
"""
import copy
import importlib.util
import json
import random
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
STATE = (REPO / "bench" / "logs" / "study_run1b_2026-10-03_20261003T100439Z"
         / "runner_state.json")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def rr3():
    return _load("rr3_under_test", RUNNER)


@pytest.fixture(scope="module")
def raw_registry():
    if not STATE.exists():
        pytest.skip(f"archived registry absent: {STATE}")
    return json.load(STATE.open())["registry"]


def _reg(rr3, raw_registry):
    return rr3.FindingRegistry.from_dict(copy.deepcopy(raw_registry))


# ── 0. the archived state is the state the brief describes ──────────────────

def test_archived_blockers_are_the_two_named(rr3, raw_registry):
    reg = _reg(rr3, raw_registry)
    assert len(reg.entries) == 75
    blockers = [cid for cid, e in reg.entries.items()
                if e.get("status") == "UNCONFIRMED"
                and not (e.get("falsifier_code") or "").strip()]
    assert sorted(blockers) == ["C0066", "C0073"], blockers
    assert reg.entries["C0066"]["severity"] == 0.45
    assert reg.entries["C0073"]["severity"] == 0.50
    # Both BELOW the 0.7 the exhausted valve gates on, and both with zero
    # verdicts -- the valve's OTHER precondition.
    for cid in ("C0066", "C0073"):
        e = reg.entries[cid]
        assert e["severity"] < 0.7
        assert e["verdicts"] == []
        assert "routing_history" not in e
        assert e.get("hil_has_computed_evidence") is True
        kinds = {r.get("kind") for r in e.get("computed_evidence") or []}
        assert "reasoned_withdrawal" in kinds, kinds


# ── 1. POSITION A IS INERT (passes with or without the fix, by design) ──────

def test_position_a_severity_clause_removal_does_not_move_a4(rr3, raw_registry,
                                                             tmp_path):
    src = RUNNER.read_text()
    old = ('        if (e["status"] in EXHAUSTED_VALVE_STATUSES\n'
           '                and e["severity"] >= 0.7):')
    new = '        if (e["status"] in EXHAUSTED_VALVE_STATUSES):'
    assert src.count(old) == 1, "exhausted-valve severity clause not found"
    mutant = tmp_path / "rr3_position_a.py"
    mutant.write_text(src.replace(old, new))
    mod = _load("rr3_position_a", mutant)

    cfg = mod.RunnerConfig()
    for rnd in (8, 9, 20, 100):
        reg = mod.FindingRegistry.from_dict(copy.deepcopy(raw_registry))
        # Strip the handoff door so Position A is measured ALONE.
        for e in reg.entries.values():
            e.pop("hil_has_computed_evidence", None)
        mod._update_finding_statuses(reg, rnd, cfg)
        assert reg.unverified_critical_count() == 2, (
            f"round {rnd}: Position A alone moved A4")
        for cid in ("C0066", "C0073"):
            # The valve set it to FALSE, not True: has_reviews is False.
            assert reg.entries[cid].get("exhausted") is False


# ── 2. the door drains A4 on the real archived state ────────────────────────

def test_predicate_exists_and_is_severity_free(rr3):
    import inspect
    assert hasattr(rr3, "_handed_to_human")
    body = inspect.getsource(rr3._handed_to_human)
    # Executed form of "severity is not consulted": the predicate's verdict is
    # invariant under every severity in [0, 1].
    base = {"status": "UNCONFIRMED", "hil_has_computed_evidence": True,
            "verdicts": [], "falsifier_code": "",
            "computed_evidence": [{"kind": "reasoned_withdrawal"}]}
    verdicts = {rr3._handed_to_human(dict(base, severity=s / 100.0))
                for s in range(0, 101)}
    assert verdicts == {True}, verdicts
    # The predicate's BODY never reaches `e["severity"]`: tracked by executing
    # it against a dict that raises if severity is touched.
    class _Trap(dict):
        def get(self, k, d=None):
            assert k != "severity", "predicate consulted severity"
            return dict.get(self, k, d)
    assert rr3._handed_to_human(_Trap(base)) is True
    assert body


def test_door_drains_a4_on_the_real_run(rr3, raw_registry):
    reg = _reg(rr3, raw_registry)
    assert reg.unverified_critical_count() == 0, "A4 did not drain"
    assert reg.handed_to_human_ids() == ["C0066", "C0073"]


def test_gate_after_the_door_round7_blocks_on_the_COUNT_side_not_a4(rr3,
                                                                    raw_registry):
    """The brief's premise -- "exactly 2 registry entries hold it" -- is FALSE.

    study_run1b's own round-7 log prints `novel_crit_recent=[1, 0, 0]`: TWO
    consecutive zero-new-critical rounds against `gamma_alt_consecutive_zero_crit
    = 3`. So with A4 fully drained the gate STILL refuses at round 7, and the
    refusal names the count side. A4 was necessary, not sufficient.
    """
    reg = _reg(rr3, raw_registry)
    cfg = rr3.RunnerConfig(falsifier_gate_enabled=True)
    assert reg.unverified_critical_count() == 0
    converged, reason = rr3._check_gamma_alt_convergence(
        round_idx=7, gamma=0.4274,
        novel_critical_history=[1, 3, 0, 0, 1, 0, 1, 0, 0],  # run 1b, tail [1,0,0]
        cfg=cfg,
        unresolved_critical=reg.unverified_critical_count(),
        contested=reg.contested_count(7, subcritical_exclusion=True),
        rho_churn=False, irreducible_queue=reg.irreducible_queue_count(),
        gamma_critical=0.7323, total_findings=len(reg.entries))
    assert converged is False
    assert "A4" not in reason, reason
    assert "zero-new-critical" in reason, reason


def test_gate_after_the_door_converges_at_round8_and_a4_is_the_decider(
        rr3, raw_registry):
    """One more round (tail [0,0,0]) and the door is EXACTLY what decides.

    max_rounds was 8 (rounds 0..7), so run 1b never got that round. With it:
    A4 == 0 -> converged; A4 == 2 -> blocked, naming A4. That is the fix's
    load-bearing measurement.
    """
    cfg = rr3.RunnerConfig(falsifier_gate_enabled=True)
    hist = [1, 3, 0, 0, 1, 0, 1, 0, 0, 0]    # one more round -> tail [0,0,0]

    reg = _reg(rr3, raw_registry)
    conv_fixed, reason_fixed = rr3._check_gamma_alt_convergence(
        round_idx=8, gamma=0.4274, novel_critical_history=hist, cfg=cfg,
        unresolved_critical=reg.unverified_critical_count(),
        contested=reg.contested_count(8, subcritical_exclusion=True),
        rho_churn=False, irreducible_queue=reg.irreducible_queue_count(),
        gamma_critical=0.7323, total_findings=len(reg.entries))

    stripped = _reg(rr3, raw_registry)                 # door closed again
    for e in stripped.entries.values():
        e.pop("hil_has_computed_evidence", None)
    conv_before, reason_before = rr3._check_gamma_alt_convergence(
        round_idx=8, gamma=0.4274, novel_critical_history=hist, cfg=cfg,
        unresolved_critical=stripped.unverified_critical_count(),
        contested=stripped.contested_count(8, subcritical_exclusion=True),
        rho_churn=False, irreducible_queue=stripped.irreducible_queue_count(),
        gamma_critical=0.7323, total_findings=len(stripped.entries))

    assert stripped.unverified_critical_count() == 2
    assert conv_before is False and "A4 BLOCK" in reason_before, reason_before
    assert conv_fixed is True, reason_fixed


# ── 3. NOT a dead-instrument release ───────────────────────────────────────

@pytest.mark.parametrize("mutate,label", [
    (lambda e: e.update(hil_has_computed_evidence=False), "stamp absent"),
    (lambda e: e.update(computed_evidence=[
        {"kind": "discrimination_control:NON_DISCRIMINATING"}]),
     "instrument-health record only"),
    (lambda e: e.update(computed_evidence=[]), "empty evidence (dead router)"),
    (lambda e: e.update(verdicts=[{"model": "X", "verdict": "CONFIRM",
                                   "round": 7, "evidence": ""}]),
     "a verdict is pending"),
    (lambda e: e.update(routing_history=[{"verdict": "UNTOOLABLE"}]),
     "the ladder ran"),
    (lambda e: e.update(falsifier_code="assert False"), "a test exists"),
])
def test_door_stays_shut_for_every_dead_instrument_shape(rr3, raw_registry,
                                                         mutate, label):
    reg = _reg(rr3, raw_registry)
    mutate(reg.entries["C0066"])
    assert rr3._handed_to_human(reg.entries["C0066"]) is False, label
    assert reg.unverified_critical_count() == 1, label
    assert "C0066" not in reg.handed_to_human_ids(), label


def test_door_is_severity_blind_for_a_critical_too(rr3, raw_registry):
    """A sev-0.95 entry of the same SHAPE is released identically.

    Stated so no later reader mistakes this for a sub-critical carve-out: it is
    not one, and that is the point. The release is bought by the RECORD, which
    a broken instrument cannot produce, never by the float.
    """
    reg = _reg(rr3, raw_registry)
    reg.entries["C0066"]["severity"] = 0.95
    assert reg.unverified_critical_count() == 0
    assert "C0066" in reg.handed_to_human_ids()


# ── 4. excluded implies reported, over randomised registries ───────────────

def test_excluded_implies_reported_randomised(rr3):
    rng = random.Random(20261003)
    STATUSES = ["UNCONFIRMED", "OPEN", "CONTESTED", "CLOSED", "REFUTED",
                "MERGED", "CONFIRMED", "REOPENED", "WITHHELD"]
    KINDS = ["reasoned_withdrawal", "critical_refuted_evidence_recorded",
             "discrimination_control:PASS",
             "discrimination_control:NON_DISCRIMINATING", "other"]
    for trial in range(400):
        reg = rr3.FindingRegistry()
        n = rng.randint(1, 14)
        for i in range(n):
            e = {
                "canonical_id": f"C{i:04d}",
                "status": rng.choice(STATUSES),
                "severity": round(rng.random(), 2),
                "verdicts": ([] if rng.random() < 0.6
                             else [{"model": "M", "verdict": "CONFIRM",
                                    "round": 1, "evidence": ""}]),
                "falsifier_code": "" if rng.random() < 0.6 else "assert False",
                "falsifier_verdict": rng.choice(["", "CONFIRMED", "REFUTED"]),
                "computed_evidence": ([] if rng.random() < 0.4 else
                                      [{"kind": rng.choice(KINDS)}]),
            }
            if rng.random() < 0.6:
                e["hil_has_computed_evidence"] = True
            if rng.random() < 0.2:
                e["routing_history"] = [{"verdict": "UNTOOLABLE"}]
            reg.entries[e["canonical_id"]] = e

        reported = set(reg.handed_to_human_ids())
        excluded = {cid for cid, e in reg.entries.items()
                    if rr3._handed_to_human(e)}
        assert excluded == reported, (trial, excluded ^ reported)

        # And the exclusion is MONOTONE SAFE: A4 with the door is never larger
        # than A4 without it, and the difference is exactly the reported set
        # restricted to entries that would otherwise have been counted.
        with_door = reg.unverified_critical_count()
        stripped = rr3.FindingRegistry()
        stripped.entries = copy.deepcopy(reg.entries)
        for e in stripped.entries.values():
            e.pop("hil_has_computed_evidence", None)
        without_door = stripped.unverified_critical_count()
        assert with_door <= without_door, (trial, with_door, without_door)
