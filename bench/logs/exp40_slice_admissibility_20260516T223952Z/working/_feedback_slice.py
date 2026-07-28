"""Exp 40 plan-D decomposition slice — the admissibility parser.

A standalone, self-contained extraction of `parse_admissibility_block`
(plus its single constant) from the plan-E cleaned `_feedback.py`
baseline. This is the small, finite, monitorable review target for the
plan-F convergence re-run: ~110 lines, one pure `str -> List[str]`
function, zero coupling to the feedback dataclass or the rest of the
channel. A small finite error space can actually be exhausted, which is
the regime the decay model needs to terminate.

Provenance: verbatim from bench/exp40_baseline/_feedback_cleaned.py
(lines 549, 552-661), itself the cumulative test-gated baseline built
by bench/exp40_fix_collation.py. The repo bench/dm/_feedback.py is
left pristine; this slice is the experiment artefact only.
"""
from __future__ import annotations

from typing import List

ADMISSIBILITY_GATES = ("S_min", "G-completeness", "d_tool", "σ_measured", "q_retest")


def parse_admissibility_block(finding_text: str) -> List[str]:
    """Extract failed gate names from a finding's ADMISSIBILITY block.

    Expected block format (from `cdsfl_operational.md` §15 and
    `reference_runner.py` prompt template)::

        ADMISSIBILITY:
          S_min: PASS (location=bench/foo.py:42, ...)
          G-completeness: PASS (verifier can reproduce ...)
          d_tool: PASS (pytest ran, ...)
          σ_measured: FAIL (no post-fix measurement available)
          q_retest: PASS (η from similarity, ...)

    Returns the list of gate names whose status is not "PASS". If the block
    is missing entirely, returns all five gates (total failure — the
    §17 feedback will tell the model to supply it).

    Parser is forgiving:
      * Case-insensitive for PASS/FAIL
      * Accepts either ':' or '-' or '=' between gate name and status
      * Accepts the σ character or the ASCII 'sigma' spelling
      * Whitespace-tolerant

    This is deliberately simple — a regex-plus-split, not a full grammar.
    The output feeds the feedback channel; format-strict rejection lives
    downstream in whatever gate we implement in Python, not here.
    """
    import re

    if not finding_text:
        return list(ADMISSIBILITY_GATES)

    # Find the ADMISSIBILITY: marker and extract the following block. The
    # block ends at the next all-caps section header (NOVELTY, VERIFIED,
    # CORROBORATION, etc.) or end of string.
    marker_match = re.search(
        r"^\s*(?:#{1,6}\s*)?ADMISSIBILITY\s*:?\s*(?:\([^)]*\))?\s*$",
        finding_text,
        re.IGNORECASE | re.MULTILINE,
    )
    if not marker_match:
        return list(ADMISSIBILITY_GATES)

    # Extract everything after the marker until next all-caps header. We
    # use a permissive boundary — any line starting with a known section
    # name in caps terminates the block.
    tail = finding_text[marker_match.end():]
    # FINDING_ID added to the alternation 15 May 2026 per Exp 40 panel
    # consensus. Four of five models (CC2, ChatGPT, Codex, DeepSeek)
    # independently produced findings reporting this terminator gap:
    # when the next finding's marker is FINDING_ID:, the regex fails
    # to match because `_ID` appears between FINDING and `:`. Result:
    # the ADMISSIBILITY block consumes text from the subsequent
    # finding, producing the parser-runaway pattern that polluted
    # canonical finding identifiers throughout Exp 40 (e.g.
    # 'Gemini_` has `_ID` before the colon...'). Reconciliation
    # canonical: C0008.
    section_terminator = re.search(
        r"^\s*(NOVELTY|VERIFIED|CORROBORATION|FALSIFICATION|FIX|ANALYSE|"
        r"FOLLOW|FIND|FLAW_CLASS|ABSTRACTION_INDEX|SEVERITY|"
        r"FINDING_ID|FINDING)\s*:",
        tail,
        re.MULTILINE,
    )
    block = tail[: section_terminator.start()] if section_terminator else tail

    failed: List[str] = []
    for gate in ADMISSIBILITY_GATES:
        # Permissive match: gate name, optional separator, then PASS or FAIL.
        # σ_measured has a unicode char; treat both σ and 'sigma' forms.
        gate_patterns = [re.escape(gate)]
        if gate == "σ_measured":
            gate_patterns.append(r"sigma[_\s]*measured")
        elif gate == "G-completeness":
            gate_patterns.extend([r"G[-_\s]+completeness", r"G completeness"])
        elif gate == "d_tool":
            gate_patterns.append(r"d[_\s]*tool")
        elif gate == "q_retest":
            gate_patterns.append(r"q[_\s]*retest")
        elif gate == "S_min":
            gate_patterns.append(r"S[_\s]*min")

        found_pass = False
        found_any = False
        status_pattern = r"(PASS|FAIL|N/A|NA)" if gate == "σ_measured" else r"(PASS|FAIL)"
        for pat in gate_patterns:
            # Find "gate_name [:|-|=] PASS|FAIL"; σ_measured may also be N/A
            # when no fix was proposed and no post-fix measurement is applicable.
            match = re.search(
                pat + r"\s*[:\-=]?\s*" + status_pattern,
                block,
                re.IGNORECASE,
            )
            if match:
                found_any = True
                status = match.group(1).upper()
                if status == "PASS" or (
                    gate == "σ_measured" and status in ("N/A", "NA")
                ):
                    found_pass = True
                break

        if not found_pass:
            failed.append(gate)
            if not found_any:
                # Gate wasn't mentioned at all. Still count as FAIL — models
                # are required by §15 to report PASS/FAIL for every gate.
                pass

    return failed
