"""Tests for DeepSeek '### Finding N:' header adapter in parse_findings.

Item 1B.3 from Exp 40 execution plan. In Exp 39-0 R5, the parser captured
only 1 of 6 actual findings because DeepSeek emitted '### Finding N: Title'
markdown headers with FIND/FOLLOW/ANALYSE/FIX blocks, but no explicit
FINDING_ID/SEVERITY/FLAW_CLASS markers. The Exp 40 fix preprocesses these
headers into synthetic marker lines that the existing marker parser
(Format 3) can consume.

These tests confirm:
  1. Single '### Finding N: Title' is recognised and produces a finding.
  2. Multiple findings in one response all parse.
  3. Header numbers propagate into FINDING_ID.
  4. Title flows into DESCRIPTION.
  5. Explicit markers still take precedence when present.
  6. Exp 39-0 R5 replay: 6 findings extract from the real DeepSeek output.
"""

from __future__ import annotations

import pytest

from bench.runner_core import parse_findings


class TestHeaderAdapter:
    def test_single_finding_header_parses(self):
        resp = """
### Finding 1: Type Safety Violation in Fingerprint Handling

**FIND**
- Issue: The get_effective_context_budget() function assumes fingerprints values are dictionaries.

**FIX**
<<<< SEARCH bench/runner_core.py
    if not fingerprints:
        return ceiling
====
    if not fingerprints:
        return ceiling
    fp = fingerprints.get(mod, {}) if isinstance(mod, dict) else {}
>>>>
"""
        findings = parse_findings(model_id="DeepSeek", round_idx=5, response=resp)
        assert len(findings) >= 1
        # Title should flow into description
        desc = findings[0].description.lower()
        assert "type safety" in desc or "fingerprint" in desc

    def test_multiple_findings_all_parse(self):
        resp = """
### Finding 1: First Issue

FIND: description A
FIX: fix A

### Finding 2: Second Issue

FIND: description B
FIX: fix B

### Finding 3: Third Issue

FIND: description C
FIX: fix C
"""
        findings = parse_findings(model_id="DeepSeek", round_idx=5, response=resp)
        assert len(findings) == 3

    def test_finding_ids_propagate_header_number(self):
        resp = """
### Finding 7: Seventh Issue

FIND: description
"""
        findings = parse_findings(model_id="DeepSeek", round_idx=5, response=resp)
        assert len(findings) == 1
        # finding_id format is '<model_id>_<fid>'; fid should be F007
        assert "F007" in findings[0].finding_id

    def test_title_flows_into_description(self):
        resp = """
### Finding 1: A Very Specific And Memorable Title

FIND: some detail
"""
        findings = parse_findings(model_id="DeepSeek", round_idx=5, response=resp)
        assert len(findings) == 1
        assert "memorable title" in findings[0].description.lower()

    def test_explicit_markers_take_precedence(self):
        """If explicit FINDING_ID/SEVERITY markers present, they override adapter defaults."""
        resp = """
FINDING_ID: EXPLICIT_42
SEVERITY: 0.95
FLAW_CLASS: 3
DESCRIPTION: Explicit finding

PROPOSED_FIX: something
"""
        findings = parse_findings(model_id="DeepSeek", round_idx=5, response=resp)
        assert len(findings) == 1
        assert "EXPLICIT_42" in findings[0].finding_id
        assert findings[0].severity == 0.95
        assert findings[0].flaw_class == 3

    def test_default_severity_is_critical_threshold(self):
        """Default severity 0.7 keeps adapter-parsed findings at CRITICAL level.

        Otherwise they would be silently filtered by the autoimmune gate.
        """
        resp = """
### Finding 1: Something

FIND: detail
"""
        findings = parse_findings(model_id="DeepSeek", round_idx=5, response=resp)
        assert len(findings) == 1
        assert findings[0].severity >= 0.7

    def test_case_insensitive_header(self):
        """'### finding 1:' (lowercase) also matches."""
        resp = """
### finding 1: lowercase header

FIND: detail
"""
        findings = parse_findings(model_id="DeepSeek", round_idx=5, response=resp)
        assert len(findings) >= 1


class TestExp390R5Replay:
    """Replay the Exp 39-0 R5 DeepSeek output pattern: 6 findings with H3 headers."""

    def test_6_findings_extract(self):
        resp = """
### Finding 1: Type Safety Violation

**FIND**
- Issue: first

### Finding 2: Interface Break

**FIND**
- Issue: second

### Finding 3: Logic Error

**FIND**
- Issue: third

### Finding 4: Completeness Gap

**FIND**
- Issue: fourth

### Finding 5: Edge Case

**FIND**
- Issue: fifth

### Finding 6: Integration Failure

**FIND**
- Issue: sixth
"""
        findings = parse_findings(model_id="DeepSeek", round_idx=5, response=resp)
        # Previously only 1 of 6 extracted; now should be 6
        assert len(findings) == 6
