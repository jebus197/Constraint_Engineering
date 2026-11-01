"""A comment about `coherence_pruning` must not contradict the real default.

WHY THIS EXISTS, AND IT IS A CLASS THE EXISTING RULES DO NOT COVER. This project
already forbids a test that asserts on SOURCE TEXT instead of calling the code
(`execute-do-not-grep`), on the measured grounds that a module can describe
itself consistently while a producer and a consumer disagree. On 2026-11-01 the
same failure arrived from the other side: `bench/cdsfl_registry/composer.py`
carried the comment *"default True preserves behaviour byte-for-byte"* 87 lines
below a signature reading `coherence_pruning: bool = False`. Nothing could catch
it, because a comment is not executable — and it inverted a SAFETY-RELEVANT
default. It then caused a task-list entry to report 16 of 18 live call sites as
exposed to a provably counterproductive mechanism when all 16 inherit the safe
value.

WHAT THIS TEST DOES. It executes `inspect.signature` for the real default, then
reads the comment region and refuses any sentence that asserts a DIFFERENT
default for the same flag. So the prose is checked against the code rather than
against itself. The subject here is narrow on purpose: this flag gates a
mechanism that z3 has shown to be counterproductive, so a reader who believes
the wrong default draws the wrong conclusion about whether the harness is
affected — which is exactly what happened.

WHY NOT A BLANKET COMMENT CHECKER. A rule matching "default X" across the tree
would accuse correct prose wherever a comment legitimately describes a
DIFFERENT function's default, which is the 9-of-36 false-accusation class
measured on 2026-10-28. This is scoped to one flag in one module, named
explicitly, and it is cheap.
"""
from __future__ import annotations

import inspect
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COMPOSER = REPO / "bench" / "cdsfl_registry" / "composer.py"
FLAG = "coherence_pruning"

#: A sentence claiming a default for this flag, in the forms the project writes.
_CLAIMS_DEFAULT = re.compile(r"default\s+(True|False)\b", re.IGNORECASE)


def real_default():
    import sys
    sys.path.insert(0, str(REPO))
    from bench.cdsfl_registry import composer as C
    return inspect.signature(C.compose).parameters[FLAG].default


def test_the_flag_still_exists_and_has_a_boolean_default():
    d = real_default()
    assert isinstance(d, bool), (
        f"{FLAG}'s default is {d!r}, not a bool. This test's premise is that it "
        "is a boolean switch; if that changed, re-derive the check rather than "
        "loosening it.")


def test_the_runner_default_agrees_with_the_composer_default():
    """2 defaults for 1 switch must not disagree, which is the deeper hazard."""
    import sys
    sys.path.insert(0, str(REPO))
    import bench.reference_runner_v3 as rr
    runner = getattr(rr.RunnerConfig(), "composer_coherence_pruning")
    assert runner == real_default(), (
        f"RunnerConfig.composer_coherence_pruning is {runner!r} but "
        f"compose()'s default is {real_default()!r}. 2 sources of truth for 1 "
        "switch is how a caller gets behaviour nobody chose — the same shape as "
        "the max_rounds disagreement recorded under B21.")


def test_no_comment_in_the_composer_claims_the_opposite_default():
    """The prose must be checked against the code, not against itself."""
    actual = real_default()
    text = COMPOSER.read_text(errors="ignore")
    offenders = []
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        # only lines that are talking about THIS flag, or sit in its comment block
        window = "\n".join(text.splitlines()[max(0, i - 12):i + 12])
        if FLAG not in window and "_prune_for_coherence" not in window:
            continue
        m = _CLAIMS_DEFAULT.search(stripped)
        if not m:
            continue
        claimed = m.group(1).lower() == "true"
        # A line may quote the OLD wrong claim in order to correct it; such a
        # line names the correction explicitly.
        if re.search(r"said|corrected|stale|inverted|wrong|used to", stripped,
                     re.IGNORECASE):
            continue
        if claimed != actual:
            offenders.append(f"{COMPOSER.name}:{i}: {stripped[:100]}")
    assert not offenders, (
        f"{FLAG}'s real default is {actual!r}, and these comments claim "
        "otherwise. A comment is not executable, so a divergence here cannot be "
        "caught by any other check and misleads every reader:\n  "
        + "\n  ".join(offenders))
