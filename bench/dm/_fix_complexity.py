"""Measure the structural complexity of a proposed fix, from the fix artefact.

WHY THIS EXISTS
---------------
The three-phase model's re-injection term nu is DEFINED in the mathematical
appendix as a complexity measure: "Localised one-line changes have low nu.
Changes to shared interfaces have higher nu."

The implementation does not measure any of that. `compute_rk` derives it as

    nu_eff = 1 - (1 - nu_b) * (1 - (1 - sk) * nu_f)      nu_b=0.05, nu_f=0.20

whose only free variables are the fix's efficacy and two CONSTANTS. It depends on
nothing about the fix: not its size, not how many places it touches, not whether
it moves a shared interface. So the mathematics for "the simplest sufficient
solution" is already in the model and its input is a constant.

This module supplies the missing measurement. It does NOT wire it into R_k.

WHY IT IS SHADOW ONLY, AND WHY THAT IS NOT CAUTION-FOR-ITS-OWN-SAKE
-------------------------------------------------------------------
CC2's audit (2026-08-19) refuted the claim that this is replay-validatable at
zero cost. `check_sk_threshold(sk, nu_b, nu_f, q, R, s_floor)` is called live;
below the break-even S* a fix is marked SK_REJECTED, which scores +3.0 in the
feedback priority and enters the next round's prompt. Changing nu therefore
changes which fixes are rejected, which changes prompts, which invalidates
replay. There were 467 Valley-of-Bad-Fixes log lines across the arc: this path
is live, not dormant.

CALIBRATION HONESTY (DeepSeek, 2026-08-19)
------------------------------------------
With no held-out outcome labels, a fitted probability would be overfitted to the
same archive it was fitted on. So this returns a PERCENTILE RANK in [0,1]
against the archived fix population - a complexity INDEX, not a re-injection
probability. It must not be presented as the latter.

THE ANTI-GAMING PROPERTY
------------------------
The value is computed from the fix ARTEFACT after generation and is never shown
to the generating model. Because nu sits in Phase 3, after resolution, that
ordering is enforced by the arithmetic rather than by a prompt. DeepSeek's
counter stands and is recorded: a hidden measure is good for anti-gaming and is
NOT an enforcement mechanism. If the goal is pressure toward simpler fixes the
model needs a signal; if the goal is accurate reporting, hidden is correct.
"""
from __future__ import annotations

import re
from typing import Dict, List, Optional

# A fix artefact as the runner emits it (runner_core.py:886):
#   <<<< SEARCH <path>
#   ...old...
#   ==== REPLACE
#   ...new...
#   >>>>
_OPEN = re.compile(r'^\s*<{4}\s*(SEARCH|OLD)\b(.*)$', re.IGNORECASE)
_SEP = re.compile(r'^\s*={4,}')
_CLOSE = re.compile(r'^\s*>{4}')

# Structural signals that a change reaches beyond one place.
_SIGNATURE = re.compile(r'^\s*(def|class|async def)\s+\w+', re.MULTILINE)
_IMPORT = re.compile(r'^\s*(import|from)\s+\w+', re.MULTILINE)
_DECORATOR = re.compile(r'^\s*@\w+', re.MULTILINE)


def parse_fix_blocks(text: str) -> List[Dict[str, str]]:
    """Split a fix artefact into its SEARCH/REPLACE blocks."""
    blocks, lines = [], (text or "").split("\n")
    i = 0
    while i < len(lines):
        m = _OPEN.match(lines[i])
        if not m:
            i += 1
            continue
        path = (m.group(2) or "").strip() or None
        old, new, seen_sep = [], [], False
        i += 1
        while i < len(lines) and not _CLOSE.match(lines[i]):
            if _SEP.match(lines[i]):
                seen_sep = True
            else:
                (new if seen_sep else old).append(lines[i])
            i += 1
        blocks.append({"path": path, "old": "\n".join(old), "new": "\n".join(new)})
        i += 1
    return blocks


def fix_complexity_features(fix_text: str) -> Dict[str, int]:
    """Raw structural features. No weighting, no scaling — those are decisions."""
    blocks = parse_fix_blocks(fix_text)
    old_all = "\n".join(b["old"] for b in blocks)
    new_all = "\n".join(b["new"] for b in blocks)
    old_lines = [ln for ln in old_all.split("\n") if ln.strip()]
    new_lines = [ln for ln in new_all.split("\n") if ln.strip()]
    return {
        "blocks": len(blocks),
        "distinct_paths": len({b["path"] for b in blocks if b["path"]}),
        "lines_removed": len(old_lines),
        "lines_added": len(new_lines),
        "lines_changed": len(old_lines) + len(new_lines),
        # A signature or import moving is the appendix's "shared interface" case.
        "signatures_touched": len(_SIGNATURE.findall(old_all)) + len(_SIGNATURE.findall(new_all)),
        "imports_touched": len(_IMPORT.findall(old_all)) + len(_IMPORT.findall(new_all)),
        "decorators_touched": len(_DECORATOR.findall(old_all)) + len(_DECORATOR.findall(new_all)),
    }


def raw_complexity(fix_text: str) -> float:
    """A single unnormalised magnitude. Ordering matters; the scale does not."""
    f = fix_complexity_features(fix_text)
    if f["blocks"] == 0:
        return 0.0
    # A shared-interface change counts for more than a line, per the appendix's
    # own definition. These weights set ORDER, not a probability.
    return float(
        f["lines_changed"]
        + 5 * f["distinct_paths"]
        + 10 * f["signatures_touched"]
        + 10 * f["imports_touched"]
        + 5 * f["decorators_touched"]
    )


def complexity_index(fix_text: str, population: Optional[List[float]] = None) -> Optional[float]:
    """Percentile rank of this fix's complexity within `population`, in [0, 1].

    Returns None when there is no population to rank against — an honest absence,
    not a default of 0.0, which would read as "maximally simple".
    """
    if not population:
        return None
    r = raw_complexity(fix_text)
    below = sum(1 for p in population if p < r)
    ties = sum(1 for p in population if p == r)
    return (below + 0.5 * ties) / len(population)
