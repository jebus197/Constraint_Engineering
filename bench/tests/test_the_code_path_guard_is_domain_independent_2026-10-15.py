"""The code-path guard protects a code claim in EVERY domain, not only software.

WHAT CHANGED AND WHY. `typed_llm_classifier` carried 2 guards against moving a
claim to a verifier that cannot ground it, and each was wired to fire in only 1
domain:

    math_guard          = regex is MATHEMATICAL and NOT llm_primary
    code_path_protected = llm_primary and regex is CODE and llm is not CODE

So in the software domain code claims were protected and mathematical ones were
not; outside software mathematical claims were protected and CODE CLAIMS WERE
NOT. The code-path guard's own rationale in `immune_agents.py` is entirely about
CLAIM TYPE — only the CT cell can ground a claim against the target source, the
abstract verifiers return "cannot ground claim in source AST" -> UNCERTAIN, and
demoting a true code claim off the CT path causes false convergence — and none of
it is an argument about the domain label.

MEASURED BEFORE THE CHANGE, over 220 archived classifier logs and 2,273 override
lines: 10 DISTINCT findings of 333 distinct SEMI-ACTIVE overrides were code ->
non-code demotions let through unguarded, 3.0030%, 95% Wilson [1.6392%,
5.4387%]. 8 of the 10 are from exp38, the live experiment the guard's own comment
cites as its motivation. The same move was refused 128 times in software.
Producer: `scripts/the_code_path_guard_is_off_in_non_software_2026-10-15.py`.

THIS SUPERSEDES `test_guard_is_software_only` in
`test_llm_classifier_log_honesty.py`, which asserted the absence of the guard
outside software. That test pinned the defect as intended behaviour; it is
amended there with a pointer here.

THESE TESTS ASSERT THE DECISION, NOT ONLY THE LOG. A guard that logs a refusal
while the reclassification lands anyway is the exact "addition nothing reaches"
shape this project keeps finding, and a log-only assertion cannot tell the 2
apart. Every case below therefore checks the resulting `claim_type` on the
triaged finding, which is what the downstream verifier cells actually read.

The Claude CLI subprocess is mocked, so these tests run offline and cost nothing.
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

CODE_TYPES = (ClaimType.CODE_BEHAVIORAL, ClaimType.CODE_STRUCTURAL)


def _mk(fid: str = "TestModel_F001") -> Finding:
    return Finding(
        finding_id=fid,
        model_id="TestModel",
        round_idx=1,
        flaw_class=3,
        severity=0.7,
        abstraction_index=0.5,
        description="a defect description",
    )


class _FakeCompleted:
    def __init__(self, stdout: str):
        self.stdout = stdout
        self.stderr = ""
        self.returncode = 0


def _classify(caplog, *, regex_type, llm_line, conf, domain):
    """Return (log_text, resulting_claim_type, comparison_record).

    The resulting claim type is the DECIDING layer: `typed_llm_classifier`
    mutates `triaged` in place and the verifier cells read that, not the log.
    """
    f = _mk()
    triaged = [TriagedFinding(finding=f, claim_type=regex_type)]
    with patch(
        "bench.immune_agents._get_claude_cli", return_value="/bin/true",
    ), patch(
        "bench.immune_agents.sp.run",
        return_value=_FakeCompleted(f"{llm_line}\n{conf}\n"),
    ):
        with caplog.at_level(logging.INFO):
            records = typed_llm_classifier(
                [f], triaged, override_threshold=0.70, domain=domain,
            )
    return caplog.text, triaged[0].claim_type, (records[0] if records else {})


# --------------------------------------------------------------------------
# The defect that was measured: a code claim demoted outside software.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("domain", ["mathematics", "statistics", "physics"])
@pytest.mark.parametrize(
    "regex_type,llm_line",
    [
        (ClaimType.CODE_BEHAVIORAL, "logical"),
        (ClaimType.CODE_BEHAVIORAL, "statistical"),
        (ClaimType.CODE_BEHAVIORAL, "mathematical"),
        (ClaimType.CODE_STRUCTURAL, "logical"),
        (ClaimType.CODE_STRUCTURAL, "statistical"),
    ],
)
def test_code_claim_keeps_its_verifier_in_non_software(
    caplog, domain, regex_type, llm_line,
):
    """High confidence must NOT move a code claim off the CT path."""
    text, final, rec = _classify(
        caplog, regex_type=regex_type, llm_line=llm_line, conf=0.95,
        domain=domain,
    )
    assert final == regex_type, (
        f"the claim was demoted to {final} in domain {domain!r}; the CT cell "
        "can no longer ground it"
    )
    assert "BLOCKED by CODE-PATH guard" in text
    assert "LLM classifier OVERRIDE" not in text
    assert rec.get("code_path_protected") is True
    assert rec.get("overridden") is False


def test_the_guard_still_fires_in_software(caplog):
    """Unchanged behaviour in the domain it always covered."""
    text, final, rec = _classify(
        caplog, regex_type=ClaimType.CODE_BEHAVIORAL, llm_line="logical",
        conf=0.90, domain="software",
    )
    assert final == ClaimType.CODE_BEHAVIORAL
    assert "BLOCKED by CODE-PATH guard" in text
    assert rec.get("code_path_protected") is True


# --------------------------------------------------------------------------
# The asymmetry is the point: the Exp 38 RESCUE direction must survive.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("llm_line", ["code_behavioral", "code_structural"])
def test_the_rescue_direction_works_in_software(caplog, llm_line):
    """non-code -> code still overrides in software. This is why the guard
    exists at all, and the code-path guard must never block this direction."""
    text, final, rec = _classify(
        caplog, regex_type=ClaimType.MATHEMATICAL, llm_line=llm_line,
        conf=0.90, domain="software",
    )
    assert final in CODE_TYPES, (
        "the Exp 38 rescue was blocked; a code bug misrouted to mathematics "
        "can no longer reach the CT cell"
    )
    assert "LLM classifier OVERRIDE" in text
    assert "BLOCKED by CODE-PATH guard" not in text
    assert rec.get("code_path_protected") is False


@pytest.mark.parametrize("domain", ["mathematics", "statistics", "physics"])
@pytest.mark.parametrize("llm_line", ["code_behavioral", "code_structural"])
@pytest.mark.parametrize("conf", [0.70, 0.90, 0.98])
def test_the_rescue_direction_now_WORKS_outside_software(caplog, domain, llm_line, conf):
    """★ INVERTED ON HIS RULING, 2026-10-16: "Verdict, yes, fix it."

    This test previously asserted the OPPOSITE and said so in its own docstring:
    it pinned the defect deliberately and recorded that it would invert when he
    ruled. He has. `math_guard` now carries `and llm_type not in _code_types`,
    so the Exp 38 rescue -- moving a claim the regex filed as mathematical onto
    the only path that can ground a claim about code -- is reachable in EVERY
    domain, subject to the confidence threshold.

    WHAT THE RULING RESTED ON. Of 539 mathematical-guard block lines across 220
    archived classifier logs, 408 had a CODE destination: 75.6957%, 95% Wilson
    [71.9011%, 79.1267%] over the archive before leg 3 and 71.3322% [67.5644%,
    74.8254%] after it, across 327 distinct (run, finding, move) occasions and 32
    runs. 5 fired inside leg 3 itself at confidences 0.65 to 0.92, on a target
    that is prose carrying real Python.

    AND IT IS A NARROWING, NOT A REMOVAL. The 3 tests below hold the other
    directions: mathematical -> logical is still refused, the confidence
    threshold still applies, and the code-path guard still stops a code claim
    leaving the code path. If this test passes while any of those fails, the
    guard was deleted rather than narrowed.
    """
    text, final, rec = _classify(
        caplog, regex_type=ClaimType.MATHEMATICAL, llm_line=llm_line,
        conf=conf, domain=domain,
    )
    assert final in CODE_TYPES, (
        f"the rescue is still refused in {domain!r} at conf={conf}: the claim "
        f"stayed {final}. His ruling of 2026-10-16 is not in force."
    )
    assert "LLM classifier OVERRIDE" in text
    assert "BLOCKED by MATHEMATICAL guard" not in text
    assert rec.get("overridden") is True


def test_the_narrowing_did_not_delete_the_guard(caplog):
    """mathematical -> logical must STILL be refused outside software."""
    text, final, _ = _classify(
        caplog, regex_type=ClaimType.MATHEMATICAL, llm_line="logical",
        conf=0.99, domain="mathematics",
    )
    assert final == ClaimType.MATHEMATICAL, (
        "the guard was removed, not narrowed: a mathematical claim moved to a "
        "verifier that cannot ground it"
    )
    assert "BLOCKED by MATHEMATICAL guard" in text


def test_the_confidence_threshold_still_applies_to_the_rescue(caplog):
    """The rescue is permitted, not unconditional."""
    _text, final, _ = _classify(
        caplog, regex_type=ClaimType.MATHEMATICAL, llm_line="code_behavioral",
        conf=0.50, domain="mathematics",
    )
    assert final == ClaimType.MATHEMATICAL, (
        "a sub-threshold rescue was applied; the narrowing removed the "
        "confidence test as well as the type test"
    )


# --------------------------------------------------------------------------
# The mathematical guard is untouched, and the 2 guards cannot contend.
# --------------------------------------------------------------------------

def test_mathematical_guard_is_untouched(caplog):
    text, final, _ = _classify(
        caplog, regex_type=ClaimType.MATHEMATICAL, llm_line="logical",
        conf=0.99, domain="mathematics",
    )
    assert final == ClaimType.MATHEMATICAL
    assert "BLOCKED by MATHEMATICAL guard" in text


def test_the_two_guards_are_disjoint_by_construction():
    """`math_guard` needs regex == MATHEMATICAL; the code-path guard needs
    regex in the code types. No input can satisfy both, so their order in the
    elif chain cannot matter. Asserted over the whole claim-type space."""
    both = [
        t for t in ClaimType
        if t == ClaimType.MATHEMATICAL and t in CODE_TYPES
    ]
    assert both == [], f"these types would trigger both guards: {both}"


# --------------------------------------------------------------------------
# Cases the guard must NOT capture, so it does not become a blanket refusal.
# --------------------------------------------------------------------------

def test_code_to_code_is_not_a_demotion(caplog):
    """CODE_STRUCTURAL -> CODE_BEHAVIORAL stays on the CT path, so the guard
    must not engage; below threshold is then the honest reason."""
    text, final, rec = _classify(
        caplog, regex_type=ClaimType.CODE_STRUCTURAL,
        llm_line="code_behavioral", conf=0.50, domain="mathematics",
    )
    assert rec.get("code_path_protected") is False
    assert "BLOCKED by CODE-PATH guard" not in text
    assert "below threshold 0.70" in text
    assert final == ClaimType.CODE_STRUCTURAL


def test_code_to_code_above_threshold_still_overrides(caplog):
    text, final, rec = _classify(
        caplog, regex_type=ClaimType.CODE_STRUCTURAL,
        llm_line="code_behavioral", conf=0.90, domain="mathematics",
    )
    assert rec.get("code_path_protected") is False
    assert final == ClaimType.CODE_BEHAVIORAL
    assert "LLM classifier OVERRIDE" in text


def test_uncategorised_is_reported_as_itself_not_as_a_code_path_block(caplog):
    """UNCATEGORISED never overrides anyway; the honest log is the
    no-valid-reclass-target one, which the guard must not mask."""
    text, final, rec = _classify(
        caplog, regex_type=ClaimType.CODE_BEHAVIORAL, llm_line="uncategorised",
        conf=0.95, domain="mathematics",
    )
    assert rec.get("code_path_protected") is False
    assert "BLOCKED by CODE-PATH guard" not in text
    assert "uncategorised" in text.lower()
    assert final == ClaimType.CODE_BEHAVIORAL
