"""Regression tests for Exp 40 continuation fix 1b — LLM classifier
log-message honesty.

Bug class (continuation Anomaly 3): the `typed_llm_classifier` OVERRIDE
log line printed `threshold=%.2f` unconditionally, including in
`llm_primary` (software-domain) mode where the confidence threshold is
NOT applied at all — any valid disagreeing classification wins because
regex agreement is ~15% in software. A correct llm-primary override at
conf=0.68 therefore read as a sub-threshold bug. A parallel defect on
the skip path logged "below threshold 0.70" for findings skipped
because `llm_type == UNCATEGORISED` (e.g. continuation showed
Codex_UNSTRUCTURED at conf=0.88 — above 0.70 — logged "below threshold
0.70", self-contradictory).

This was a logging-honesty defect, NOT a logic defect. The override
LOGIC is intentional. These tests pin the LOG MESSAGES so they state
the actual gating reason in each of the four decision branches:

  1. llm_primary OVERRIDE → "llm-primary [software]: threshold N/A"
  2. non-primary OVERRIDE → "threshold=0.70 cleared"
  3. disagree + UNCATEGORISED → "llm=uncategorised: no valid reclass"
  4. non-primary + valid + below threshold → "below threshold 0.70"

Fix surface: bench/immune_agents.py, typed_llm_classifier override/skip
log branches.

The Claude CLI subprocess is mocked so these tests run offline.
"""

from __future__ import annotations

import logging
from unittest.mock import patch

import pytest

from bench.dm._types import Finding
from bench.immune_agents import (
    ClaimType,
    TriagedFinding,
    typed_llm_classifier,
)


def _mk(fid: str, desc: str = "a defect description") -> Finding:
    return Finding(
        finding_id=fid,
        model_id="TestModel",
        round_idx=1,
        flaw_class=3,
        severity=0.7,
        abstraction_index=0.5,
        description=desc,
    )


class _FakeCompleted:
    def __init__(self, stdout: str):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = 0


def _run_classifier(
    caplog,
    *,
    regex_type: ClaimType,
    llm_line: str,
    conf: float,
    domain: str,
):
    """Drive typed_llm_classifier with a mocked CLI returning
    `<llm_line>\\n<conf>`."""
    f = _mk("TestModel_F001")
    triaged = [TriagedFinding(finding=f, claim_type=regex_type)]
    fake_stdout = f"{llm_line}\n{conf}\n"

    with patch(
        "bench.immune_agents._get_claude_cli", return_value="/bin/true",
    ), patch(
        "bench.immune_agents.sp.run",
        return_value=_FakeCompleted(fake_stdout),
    ):
        with caplog.at_level(logging.INFO):
            typed_llm_classifier(
                [f], triaged,
                override_threshold=0.70,
                domain=domain,
            )
    return caplog.text


class TestOverrideLogHonesty:
    def test_llm_primary_override_does_not_claim_threshold(self, caplog):
        # Software domain, regex=mathematical, llm=code_behavioral,
        # conf=0.68 (below 0.70). In llm_primary mode this is a
        # CORRECT override; the log must not present it as
        # threshold-gated.
        text = _run_classifier(
            caplog,
            regex_type=ClaimType.MATHEMATICAL,
            llm_line="code_behavioral",
            conf=0.68,
            domain="software",
        )
        assert "LLM classifier OVERRIDE" in text
        assert "llm-primary [software]" in text
        assert "threshold N/A" in text
        # The misleading "threshold=0.70" token must NOT appear on the
        # override line in llm-primary mode.
        override_lines = [
            ln for ln in text.splitlines()
            if "LLM classifier OVERRIDE" in ln
        ]
        assert override_lines, "expected an OVERRIDE log line"
        for ln in override_lines:
            assert "threshold=0.70" not in ln, (
                f"llm-primary override line still claims a numeric "
                f"threshold: {ln!r}"
            )

    def test_non_primary_override_states_threshold_cleared(self, caplog):
        # Non-software domain, regex=code_structural,
        # llm=code_behavioral, conf=0.85 (above 0.70). Override fires
        # via the threshold path; the log should say so.
        text = _run_classifier(
            caplog,
            regex_type=ClaimType.CODE_STRUCTURAL,
            llm_line="code_behavioral",
            conf=0.85,
            domain="mathematics",
        )
        assert "LLM classifier OVERRIDE" in text
        assert "threshold=0.70 cleared" in text
        assert "llm-primary" not in text


class TestSkipLogHonesty:
    def test_uncategorised_skip_not_labelled_below_threshold(
        self, caplog,
    ):
        # Continuation reproduction: conf=0.88 (ABOVE 0.70) but
        # llm=uncategorised. Old code logged "below threshold 0.70"
        # which is self-contradictory. New log must state the real
        # reason.
        text = _run_classifier(
            caplog,
            regex_type=ClaimType.CODE_BEHAVIORAL,
            llm_line="uncategorised",
            conf=0.88,
            domain="software",
        )
        assert "no valid reclass target" in text
        assert "below threshold" not in text

    def test_genuine_below_threshold_still_labelled(self, caplog):
        # Non-software, valid llm_type, conf=0.50 (below 0.70). This
        # is the ONE case where "below threshold" is the honest
        # reason — it must still be logged that way.
        text = _run_classifier(
            caplog,
            regex_type=ClaimType.CODE_STRUCTURAL,
            llm_line="code_behavioral",
            conf=0.50,
            domain="mathematics",
        )
        assert "below threshold 0.70" in text
        assert "LLM classifier OVERRIDE" not in text


class TestLogicUnchanged:
    """The fix is logging-only. Confirm the override DECISION itself
    is unchanged: llm-primary still overrides sub-threshold; non-primary
    still respects the threshold."""

    def test_llm_primary_still_overrides_sub_threshold(self, caplog):
        f = _mk("TestModel_F001")
        triaged = [
            TriagedFinding(finding=f, claim_type=ClaimType.MATHEMATICAL)
        ]
        with patch(
            "bench.immune_agents._get_claude_cli",
            return_value="/bin/true",
        ), patch(
            "bench.immune_agents.sp.run",
            return_value=_FakeCompleted("code_behavioral\n0.55\n"),
        ):
            typed_llm_classifier(
                [f], triaged, override_threshold=0.70, domain="software",
            )
        # In-place mutation: the triaged finding's claim_type should
        # now be the llm type (override applied despite conf < 0.70).
        assert triaged[0].claim_type == ClaimType.CODE_BEHAVIORAL

    def test_non_primary_respects_threshold(self, caplog):
        f = _mk("TestModel_F001")
        triaged = [
            TriagedFinding(
                finding=f, claim_type=ClaimType.CODE_STRUCTURAL,
            )
        ]
        with patch(
            "bench.immune_agents._get_claude_cli",
            return_value="/bin/true",
        ), patch(
            "bench.immune_agents.sp.run",
            return_value=_FakeCompleted("code_behavioral\n0.50\n"),
        ):
            typed_llm_classifier(
                [f], triaged,
                override_threshold=0.70,
                domain="mathematics",
            )
        # conf 0.50 < 0.70 in non-primary mode → NO override; the
        # claim_type stays at the regex value.
        assert triaged[0].claim_type == ClaimType.CODE_STRUCTURAL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
