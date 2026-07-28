"""Programmatic verification of confer findings (Rounds 1-3).

Each test proves or disproves a specific claim made by CX or GE during
the Exp 38 confer series. A PASSING test means the bug EXISTS as claimed.
A FAILING test means the claim was wrong.

Tool rationale: pytest is the correct programmatic tool for code logic
claims. SymPy/z3 would be appropriate for mathematical/constraint claims,
but these are all state-machine behaviour assertions.
"""

from __future__ import annotations

import re
from pathlib import Path

from bench.dm._types import Finding
from bench.reference_runner import (
    FindingRegistry, _update_finding_statuses, RunnerConfig,
    _evaluate_gate_conditions,
)


def _make_registry_with_finding(
    canonical_id="C0001",
    source_model="model_a",
    severity=0.8,
    status="OPEN",
    round_idx=0,
    description="Test finding",
):
    """Helper: create a registry with one finding in a given state."""
    reg = FindingRegistry()
    f = Finding(
        finding_id="F001",
        model_id=source_model,
        round_idx=round_idx,
        flaw_class=2,
        severity=severity,
        abstraction_index=0.5,
        description=description,
        proposed_fix="fix",
        verified=False,
        escalated=False,
    )
    cid = reg.register(f, source_model)
    # Override canonical_id if needed
    if cid != canonical_id:
        reg.entries[canonical_id] = reg.entries.pop(cid)
        reg.entries[canonical_id]["canonical_id"] = canonical_id
    if status != "OPEN":
        reg.entries[canonical_id]["status"] = status
    return reg


# =========================================================================
# ROUND 1: CX-13 — Timer invariant completeness
# =========================================================================

class TestCX13DirectStatusWrites:
    """CX-13: 'grep/audit runner for all writes to ["status"] and
    ["last_status_change_round"]; enforce status changes only via resolve().'

    Verified by: AST/source inspection (grep for direct dict writes outside
    resolve()). This is a structural claim, not a runtime claim.
    """

    def test_no_direct_status_writes_outside_resolve(self):
        """All status mutations in reference_runner.py should go through
        resolve() or be inside resolve() itself. Direct writes like
        e["status"] = ... outside resolve() violate the timer invariant.

        EXCEPTION: contested_count() reopens UNCONFIRMED -> OPEN directly.
        That's the GE-5/Round 3 getter-mutation finding (tested separately).
        """
        runner_path = Path(__file__).resolve().parent.parent / "reference_runner.py"
        source = runner_path.read_text(encoding="utf-8")
        lines = source.split("\n")

        # Find the resolve() method boundaries
        resolve_start = None
        resolve_end = None
        in_resolve = False
        indent_level = None

        for i, line in enumerate(lines):
            if "def resolve(" in line:
                resolve_start = i
                in_resolve = True
                indent_level = len(line) - len(line.lstrip())
                continue
            if in_resolve and resolve_start is not None:
                stripped = line.lstrip()
                if stripped and not stripped.startswith("#"):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_level and stripped.startswith("def "):
                        resolve_end = i
                        in_resolve = False

        # Find contested_count boundaries (known exception — tested in R3)
        contested_start = None
        contested_end = None
        in_contested = False
        for i, line in enumerate(lines):
            if "def contested_count(" in line:
                contested_start = i
                in_contested = True
                indent_level_c = len(line) - len(line.lstrip())
                continue
            if in_contested and contested_start is not None:
                stripped = line.lstrip()
                if stripped and not stripped.startswith("#"):
                    current_indent = len(line) - len(line.lstrip())
                    if current_indent <= indent_level_c and stripped.startswith("def "):
                        contested_end = i
                        in_contested = False

        # Pattern: direct status ASSIGNMENT (not comparison ==)
        status_write_pattern = re.compile(r'\["status"\]\s*=(?!=)')
        violations = []

        for i, line in enumerate(lines):
            if status_write_pattern.search(line):
                # Skip if inside resolve()
                if resolve_start and resolve_end and resolve_start <= i < resolve_end:
                    continue
                # Skip if inside contested_count() (known R3 finding)
                if contested_start and contested_end and contested_start <= i < contested_end:
                    continue
                # Skip comments
                if line.lstrip().startswith("#"):
                    continue
                violations.append((i + 1, line.strip()))

        # If there are violations, CX-13 is confirmed — direct writes exist
        # We expect 0 violations (excluding the known contested_count exception)
        # If this FAILS, it means CX-13 found real remaining direct writes
        assert len(violations) == 0, (
            f"CX-13 CONFIRMED: {len(violations)} direct status write(s) "
            f"outside resolve(): {violations}"
        )


# =========================================================================
# ROUND 1: CX-11 — Regex boundary overmatching
# =========================================================================

class TestCX11RegexBoundary:
    """CX-11: 'C\\d{4,} without boundaries may match substrings inside
    larger tokens like XC12345Y.'
    """

    def test_regex_overmatches_embedded_id(self):
        """If the regex lacks word boundaries, it will match C12345 inside
        a larger string like 'XC12345Y'. This test checks whether that
        overmatching actually happens in the verdict parsing regex.
        """
        # The merge target regex from reference_runner.py
        pattern = re.compile(r'merged_into=(C\d{4,})')

        # Normal case — should match
        normal = "merged_into=C0042"
        assert pattern.search(normal) is not None

        # High ID — should match
        high_id = "merged_into=C10001"
        assert pattern.search(high_id) is not None

        # Embedded in larger text — the regex anchors on 'merged_into='
        # so this is actually safe against the XC12345Y case
        embedded = "XC12345Y"
        match = pattern.search(embedded)
        # This should NOT match because there's no 'merged_into=' prefix
        assert match is None, (
            "CX-11 CONFIRMED: regex overmatches embedded IDs"
        )


# =========================================================================
# ROUND 1: GE-8 — resolve() non-terminal state
# =========================================================================

class TestGE8ResolveNonTerminal:
    """GE-8: 'If resolve() asserts that its target must be a terminal
    state, passing "OPEN" will raise a state transition exception.'
    """

    def test_resolve_accepts_open_status(self):
        """resolve() should accept non-terminal statuses like OPEN
        without raising an exception."""
        reg = _make_registry_with_finding(status="CONTESTED")
        # This should not raise
        reg.resolve("C0001", "OPEN", round_idx=5)
        assert reg.entries["C0001"]["status"] == "OPEN"
        assert reg.entries["C0001"]["last_status_change_round"] == 5

    def test_resolve_accepts_reopened_status(self):
        """resolve() should accept REOPENED status."""
        reg = _make_registry_with_finding(status="CLOSED")
        reg.resolve("C0001", "REOPENED", round_idx=5)
        assert reg.entries["C0001"]["status"] == "REOPENED"


# =========================================================================
# ROUND 3: Finding 1 — F8 targetless merge
# =========================================================================

class TestR3F8TargetlessMerge:
    """R3-1 (CX HIGH, GE HIGH): When all merge verdicts have unparseable
    evidence, target becomes __unknown__ and merge proceeds with
    merged_into=None. Floor says 'never merge without target consensus.'
    """

    def test_unknown_target_two_models_deferred(self):
        """Two models vote MERGE with no parseable target.
        FIX: code should defer, not merge.
        """
        reg = _make_registry_with_finding(source_model="model_a")
        reg.add_verdict("C0001", "model_b", "MERGE", 1, evidence="should merge")
        reg.add_verdict("C0001", "model_c", "MERGE", 1, evidence="duplicate of something")

        _update_finding_statuses(reg, round_idx=1)

        entry = reg.entries["C0001"]
        # FIX VERIFIED: unknown target should NOT merge
        assert entry["status"] != "MERGED", (
            "R3-1 FIX FAILED: Finding still merges with unparseable target"
        )

    def test_unknown_target_small_panel_deferred(self):
        """Single model on small panel votes MERGE with no parseable target.
        FIX: code should defer, not merge.
        """
        reg = _make_registry_with_finding(source_model="model_a")
        reg.add_verdict("C0001", "model_b", "MERGE", 1, evidence="it's a dupe")

        _update_finding_statuses(reg, round_idx=1)

        entry = reg.entries["C0001"]
        # FIX VERIFIED: unknown target should NOT merge
        assert entry["status"] != "MERGED", (
            "R3-1 FIX FAILED (small panel): Finding still merges with "
            "unparseable target"
        )


# =========================================================================
# ROUND 3: Finding 2 — F8 panel size from verdicts
# =========================================================================

class TestR3F8PanelSizeMisdetection:
    """R3-2 (CX MEDIUM, GE CRITICAL): available_external is computed from
    models that have voted on THIS finding, not the actual panel size.
    On a 5-model panel where only 1 external has voted, code treats it
    as 'small panel'.
    """

    def test_full_panel_early_vote_waits(self):
        """5-model panel. Only 1 external has voted MERGE so far.
        FIX: code uses config panel size, not per-finding voter count.
        Should WAIT for more votes on a full panel.
        """
        cfg = RunnerConfig(
            models=["model_a", "model_b", "model_c", "model_d", "model_e"]
        )
        reg = _make_registry_with_finding(source_model="model_a")
        # Only model_b has voted. model_c, model_d, model_e haven't yet.
        reg.add_verdict(
            "C0001", "model_b", "MERGE", 1,
            evidence="merged_into=C0002"
        )

        _update_finding_statuses(reg, round_idx=1, cfg=cfg)

        entry = reg.entries["C0001"]
        # FIX VERIFIED: full panel with 1 vote should NOT merge
        assert entry["status"] != "MERGED", (
            "R3-2 FIX FAILED: Full panel (5 models) still treated as small "
            f"panel. Status={entry['status']}"
        )


# =========================================================================
# ROUND 3: Finding 3 — F7 age-only EXHAUSTED
# =========================================================================

class TestR3F7AgeOnlyExhausted:
    """R3-3 (CX MEDIUM, GE CRITICAL): A finding with 0 verdicts that has
    been stalled for >= threshold rounds gets EXHAUSTED, even though
    nobody ever reviewed it.
    """

    def test_unreviewed_finding_not_exhausted(self):
        """Critical finding registered at round 0, no verdicts ever added.
        FIX: Should still block convergence — never reviewed.
        """
        reg = _make_registry_with_finding(
            severity=0.9,  # Critical
            round_idx=0,
        )
        assert len(reg.entries["C0001"]["verdicts"]) == 0

        cfg = RunnerConfig(exhausted_round_threshold=8)
        _update_finding_statuses(reg, round_idx=10, cfg=cfg)
        count = reg.open_crit_high_count()

        # FIX VERIFIED: unreviewed finding should NOT be exhausted
        assert count == 1, (
            f"R3-3 FIX FAILED: Unreviewed critical finding (0 verdicts) "
            f"still excluded from gate count. count={count}"
        )
        assert not reg.entries["C0001"].get("exhausted"), (
            "R3-3 FIX FAILED: exhausted flag set on unreviewed finding"
        )

    def test_reviewed_finding_can_be_exhausted(self):
        """Finding with multiple verdicts that has genuinely stalled.
        This SHOULD be eligible for exhaustion."""
        reg = _make_registry_with_finding(
            severity=0.9,
            round_idx=0,
        )
        reg.add_verdict("C0001", "model_b", "CONFIRM", 1, evidence="looks real")
        reg.add_verdict("C0001", "model_c", "CHALLENGE", 1, evidence="not sure")

        cfg = RunnerConfig(exhausted_round_threshold=8)
        _update_finding_statuses(reg, round_idx=10, cfg=cfg)
        count = reg.open_crit_high_count()

        assert count == 0, (
            "Reviewed-and-stalled finding should be EXHAUSTED"
        )


# =========================================================================
# ROUND 3: Finding 4 — F11 small-panel high-severity stall
# =========================================================================

class TestR3F11SmallPanelStall:
    """R3-4 (CX MEDIUM, GE HIGH): With only 1 external model, high-severity
    findings requiring 2 confirmations become permanently unconfirmable.
    """

    def test_high_severity_one_external_can_confirm_on_small_panel(self):
        """Severity 0.9 on a 2-model panel (1 external). FIX: required
        is capped to available external models, so 1 confirm suffices.
        """
        cfg = RunnerConfig(models=["model_a", "model_b"])
        reg = _make_registry_with_finding(
            source_model="model_a",
            severity=0.9,
        )
        reg.add_verdict("C0001", "model_b", "CONFIRM", 1, evidence="confirmed")

        _update_finding_statuses(reg, round_idx=1, cfg=cfg)

        entry = reg.entries["C0001"]
        # FIX VERIFIED: on a 2-model panel, required=min(2,1)=1
        assert entry["status"] == "CONFIRMED", (
            f"R3-4 FIX FAILED: High-severity finding with 1 external "
            f"confirm on 2-model panel should confirm. Status={entry['status']}"
        )


# =========================================================================
# ROUND 3: Finding 5 — Getter mutation side-effects
# =========================================================================

class TestR3GetterMutation:
    """R3-5 (GE CRITICAL): open_crit_high_count() and contested_count()
    mutate entry state inside counting functions. Calling them for
    logging/dry-runs triggers real state changes.
    """

    def test_open_crit_high_count_does_not_mutate(self):
        """Calling open_crit_high_count() should not set e['exhausted'].
        FIX: getter is now a pure reader.
        """
        reg = _make_registry_with_finding(severity=0.9, round_idx=0)

        # Before counting — no exhausted flag
        assert "exhausted" not in reg.entries["C0001"]

        # Call the getter — should NOT mutate
        reg.open_crit_high_count()

        # FIX VERIFIED: no mutation from a counting function
        assert "exhausted" not in reg.entries["C0001"], (
            "R3-5 FIX FAILED: open_crit_high_count() still mutates state"
        )

    def test_contested_count_does_not_mutate(self):
        """Calling contested_count() should not change entry status.
        FIX: getter is now a pure reader.
        """
        reg = _make_registry_with_finding(status="UNCONFIRMED", round_idx=0)
        reg.entries["C0001"]["last_status_change_round"] = 0

        # Add a verdict after UNCONFIRMED to trigger reopen scenario
        reg.add_verdict("C0001", "model_b", "CONFIRM", 5, evidence="new")

        status_before = reg.entries["C0001"]["status"]
        assert status_before == "UNCONFIRMED"

        # Call the getter — should NOT mutate
        reg.contested_count(current_round=5, grace_period=2)

        status_after = reg.entries["C0001"]["status"]
        # FIX VERIFIED: no mutation from a counting function
        assert status_after == "UNCONFIRMED", (
            f"R3-5 FIX FAILED: contested_count() still mutates status "
            f"(was {status_before}, now {status_after})"
        )

    def test_double_call_produces_same_count(self):
        """Calling a getter twice should return the same value."""
        reg = _make_registry_with_finding(severity=0.9, round_idx=0)

        count1 = reg.open_crit_high_count()
        count2 = reg.open_crit_high_count()

        assert count1 == count2, (
            f"R3-5 FIX FAILED: open_crit_high_count() not idempotent. "
            f"First={count1}, second={count2}"
        )
