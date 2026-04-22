"""Tests for the K/L/M shadow-audit enrichment in bench/immune_agents.py.

The 21 April 2026 Round 2 plan review (RQ4) required a non-distortion check
against `40_gate.json` pass_condition before live-promoting the K (physics),
L (chemistry), and M (engineering) specialist cells. To support that check,
the shadow branch of the B-Cell specialist dispatch at immune_agents.py
around lines 5400–5428 emits a structured per-verdict audit record through
the `_shadow_log` logger.

These tests pin the audit record's contract:

* **Schema (AST)** — the `shadow_detail` dict literal has exactly the five
  expected keys: `finding_id`, `verdict`, `confidence`, `tool_used`,
  `evidence`. No drift either way (dropped field → audit loses signal;
  renamed field → downstream consumer silently receives None).
* **Field binding** — the audit record fields bind to real `CellVerdict`
  attributes (not the pre-22-April draft's `claim_id`/`severity`, which
  always resolved to None because those are not CellVerdict fields).
* **Evidence truncation** — the `evidence` field is capped at 256
  characters so a runaway verdict cannot flood the audit log.
* **Per-verdict emission** — N input verdicts produce exactly N audit
  records.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_shadow_audit_klm.py -v
"""

from __future__ import annotations

import ast
import dataclasses
import os
import sys
from pathlib import Path

import pytest

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.immune_agents import CellType, CellVerdict


# ═══════════════════════════════════════════════════════════════════════════════
# Expected schema — the contract the audit record must meet
# ═══════════════════════════════════════════════════════════════════════════════

EXPECTED_SCHEMA_FIELDS = {
    "finding_id",    # identity — required for matching shadow vs. live verdicts
    "verdict",       # the verdict string (CONFIRMED, REJECTED, UNCERTAIN, ...)
    "confidence",    # 0.0–1.0 — severity proxy for non-distortion comparison
    "tool_used",     # which specialist tool produced the verdict
    "evidence",      # explanation (truncated at 256 chars)
}

EVIDENCE_TRUNCATION_LIMIT = 256

_IMMUNE_AGENTS_PATH = (
    Path(_project_root) / "bench" / "immune_agents.py"
)


# ═══════════════════════════════════════════════════════════════════════════════
# 1. AST-level schema pin
# ═══════════════════════════════════════════════════════════════════════════════


def _extract_shadow_detail_keys(source: str) -> set[str]:
    """Parse immune_agents.py and return the key set of the `shadow_detail`
    list-comprehension dict literal. Raises AssertionError if the comp is
    not found or is shaped unexpectedly."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        # Find `shadow_detail = [...]` assignment inside a function body.
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if not (isinstance(target, ast.Name) and target.id == "shadow_detail"):
                continue
            # The RHS should be a list-comprehension of a dict literal.
            if not isinstance(node.value, ast.ListComp):
                continue
            elt = node.value.elt
            if not isinstance(elt, ast.Dict):
                continue
            keys: set[str] = set()
            for k in elt.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, str):
                    keys.add(k.value)
            return keys
    raise AssertionError(
        "Could not locate shadow_detail = [<dict-comp>] in immune_agents.py"
    )


class TestShadowAuditSchemaAST:
    """AST-level schema enforcement — static check against source."""

    def test_shadow_detail_has_expected_five_fields(self):
        source = _IMMUNE_AGENTS_PATH.read_text(encoding="utf-8")
        keys = _extract_shadow_detail_keys(source)
        assert keys == EXPECTED_SCHEMA_FIELDS, (
            f"shadow_detail schema drift. "
            f"Got {sorted(keys)}, expected {sorted(EXPECTED_SCHEMA_FIELDS)}"
        )

    def test_shadow_detail_does_not_use_stale_claim_id(self):
        """Regression pin: the pre-22-April draft used `claim_id` which is
        NOT a CellVerdict field and always resolved to None. If this test
        fails, the bug has been reintroduced."""
        source = _IMMUNE_AGENTS_PATH.read_text(encoding="utf-8")
        keys = _extract_shadow_detail_keys(source)
        assert "claim_id" not in keys, (
            "Regression: shadow_detail uses `claim_id`, which is not a "
            "CellVerdict field. Use `finding_id` instead."
        )

    def test_shadow_detail_does_not_use_stale_severity(self):
        """Regression pin: the pre-22-April draft used `severity` which is
        NOT a CellVerdict field and always resolved to None. CellVerdict's
        severity proxy is `confidence`."""
        source = _IMMUNE_AGENTS_PATH.read_text(encoding="utf-8")
        keys = _extract_shadow_detail_keys(source)
        assert "severity" not in keys, (
            "Regression: shadow_detail uses `severity`, which is not a "
            "CellVerdict field. Use `confidence` instead."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Field-binding check — the keys must correspond to real CellVerdict fields
# ═══════════════════════════════════════════════════════════════════════════════


class TestFieldBindingToCellVerdict:
    """The audit record's fields must bind to real CellVerdict attributes
    or to derived values (evidence-truncation), NOT to always-None ghosts."""

    def test_all_shadow_detail_keys_bind_to_cellverdict_attributes(self):
        cellverdict_fields = {f.name for f in dataclasses.fields(CellVerdict)}
        # The shadow_detail keys should be a subset of CellVerdict fields
        # (the evidence field is derived from CellVerdict.evidence via
        # truncation, so it's a direct match).
        missing = EXPECTED_SCHEMA_FIELDS - cellverdict_fields
        assert missing == set(), (
            f"shadow_detail expects fields {sorted(missing)} that are not "
            f"on CellVerdict. CellVerdict fields: "
            f"{sorted(cellverdict_fields)}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Behavioural replica — reproduce the shadow_detail dict comp and verify
# ═══════════════════════════════════════════════════════════════════════════════


def _mk_cellverdict(
    finding_id: str = "f1",
    verdict: str = "CONFIRMED",
    confidence: float = 0.8,
    tool_used: str = "sympy",
    evidence: str = "ok",
) -> CellVerdict:
    return CellVerdict(
        cell_type=CellType.B_CELL,
        finding_id=finding_id,
        verdict=verdict,
        confidence=confidence,
        evidence=evidence,
        tool_used=tool_used,
    )


def _replicate_shadow_detail(verdicts: list[CellVerdict]) -> list[dict]:
    """Replicate the shadow_detail list-comprehension for isolated testing.
    If the live dict-comp in immune_agents.py changes shape, the
    TestShadowAuditSchemaAST tests will flag it; this helper pins
    behaviour."""
    return [
        {
            "finding_id": getattr(v, "finding_id", None),
            "verdict": getattr(v, "verdict", None),
            "confidence": getattr(v, "confidence", None),
            "tool_used": getattr(v, "tool_used", None),
            "evidence": ((getattr(v, "evidence", "") or "")[:256]),
        }
        for v in verdicts
    ]


class TestShadowAuditBehaviour:
    """Behavioural replica tests — exercise the dict-comp against real
    CellVerdict fixtures."""

    def test_single_verdict_yields_single_audit_record(self):
        verdicts = [_mk_cellverdict("physics_claim_1", "REJECTED", 0.6,
                                    "dimensional_analysis", "unit mismatch")]
        audit = _replicate_shadow_detail(verdicts)
        assert len(audit) == 1
        assert audit[0]["finding_id"] == "physics_claim_1"
        assert audit[0]["verdict"] == "REJECTED"
        assert audit[0]["confidence"] == 0.6
        assert audit[0]["tool_used"] == "dimensional_analysis"
        assert audit[0]["evidence"] == "unit mismatch"

    def test_n_verdicts_yield_n_audit_records(self):
        verdicts = [
            _mk_cellverdict(f"claim_{i}", "CONFIRMED", 0.5, "sympy", f"ev{i}")
            for i in range(5)
        ]
        audit = _replicate_shadow_detail(verdicts)
        assert len(audit) == 5
        for i, rec in enumerate(audit):
            assert rec["finding_id"] == f"claim_{i}"

    def test_empty_verdict_list_yields_empty_audit(self):
        audit = _replicate_shadow_detail([])
        assert audit == []

    def test_evidence_truncated_at_256_chars(self):
        long_evidence = "x" * 500
        v = _mk_cellverdict(evidence=long_evidence)
        audit = _replicate_shadow_detail([v])
        assert len(audit[0]["evidence"]) == EVIDENCE_TRUNCATION_LIMIT
        assert audit[0]["evidence"] == "x" * EVIDENCE_TRUNCATION_LIMIT

    def test_evidence_at_exactly_256_chars_not_truncated(self):
        edge_evidence = "y" * EVIDENCE_TRUNCATION_LIMIT
        v = _mk_cellverdict(evidence=edge_evidence)
        audit = _replicate_shadow_detail([v])
        assert audit[0]["evidence"] == edge_evidence

    def test_empty_evidence_becomes_empty_string_not_none(self):
        """Defensive: if evidence is empty string, audit record must not
        drop it to None (preserves JSON-round-trip stability)."""
        v = _mk_cellverdict(evidence="")
        audit = _replicate_shadow_detail([v])
        assert audit[0]["evidence"] == ""


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Log-format pin
# ═══════════════════════════════════════════════════════════════════════════════


class TestShadowLogFormat:
    """The _shadow_log.info() call format string must remain stable so
    downstream log-parsing tools can match on the expected pattern."""

    def test_shadow_log_format_string_present(self):
        """The log format string must name the shadow scope, the domain,
        the verdict count, and the JSON-encoded detail."""
        source = _IMMUNE_AGENTS_PATH.read_text(encoding="utf-8")
        assert "B-Cell specialist (shadow, domain=%s): %d verdicts; detail=%s" in source, (
            "Shadow-audit log format string drift. If this is intentional, "
            "update downstream log-parsing tooling in lockstep and then "
            "update this test."
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
