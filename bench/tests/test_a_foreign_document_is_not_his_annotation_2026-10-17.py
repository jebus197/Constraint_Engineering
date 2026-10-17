"""A document he merely dropped in the folder is not a verdict he wrote.

On 2026-10-17 he attached a Gemini Web design brief at
`Responses/design_brief.txt`. Its own title block opens 3 lines with a hash --
"DESIGN BRIEF: CHRONOS MEMORY SYSTEM (CMS)", "TARGET AGENT: ...",
"SPECIFICATION VERSION: 2.0" -- and the reader counted all 3 as annotations of
his. The register guard caught it as 318 live tickets against 321 annotations,
and the commit was refused.

FOUR SHAPE-BASED FIXES WERE MEASURED AND ALL FOUR REFUTED, which is why the
exclusion is an explicit per-file list rather than a clever rule:

  1. a dated-filename filter drops 8 of 598, 1.3378% Wilson [0.6794%, 2.6174%];
  2. markdown-structure detection marks FINAL_REPORT_FOR_OPUS_2026-08-27.md,
     which holds a real verdict, and misses design_brief.txt entirely;
  3. removing the `.md`-only gate on the heading filter drops 18 of 598,
     3.0100% Wilson [1.9123%, 4.7076%], 12 of them REAL verdicts;
  4. deriving an area from `subjects` resolves for 11.0865% of tickets only.

THE DANGEROUS DIRECTION IS OVER-REACH, not under-reach. An extra annotation is
visible as a count mismatch; a LOST verdict is invisible, and the project has
already had 221 of 691 of his rulings invisible to grep once. So the heart of
this file is `test_the_short_verdicts_that_shape_rules_would_have_eaten`, which
names the actual texts at risk and fails if any goes missing.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
READER = REPO / "scripts" / "read_founder_responses_2026-10-11.py"


def _reader():
    spec = importlib.util.spec_from_file_location("_fr", READER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R = _reader()

#: Real verdicts of his that each refuted rule would have eaten. Named, not
#: counted: a count cannot say WHICH one went missing, and a swap of one for
#: another would leave a count unchanged.
AT_RISK = (
    "Verdict: y",
    "Go with option B",
    "Go with option A",
    "Then this should also be fixed",
    "Same response",
)


@pytest.mark.skipif(not R.RESPONSES.is_dir(),
                    reason="his Responses folder is not on this machine")
def test_the_short_verdicts_that_shape_rules_would_have_eaten_are_all_present():
    """THE ASSERTION THAT MATTERS. Over-reach is the invisible failure."""
    texts = {r["text"].strip() for r in R.annotations()}
    missing = [t for t in AT_RISK if t not in texts]
    assert not missing, (
        f"{len(missing)} of his real verdicts are no longer being read: "
        f"{missing}. Something narrowed the reader. A short ruling of his is "
        f"still a ruling -- 'Verdict: y' is a decision, and losing it means "
        f"acting against what he decided while believing he never answered.")


@pytest.mark.skipif(not R.RESPONSES.is_dir(), reason="folder absent")
def test_the_brief_he_attached_contributes_nothing():
    rows = [r for r in R.annotations() if "design_brief" in r["file"]]
    assert not rows, (
        f"{len(rows)} lines of the attached design brief are being counted as "
        f"his annotations: {[r['text'][:50] for r in rows]}")


@pytest.mark.skipif(not R.RESPONSES.is_dir(), reason="folder absent")
def test_no_excluded_file_contributes_anything():
    rows = [r for r in R.annotations()
            if r["file"] in R.NOT_HIS_ANNOTATIONS]
    assert not rows, f"excluded files still contributing: {rows[:3]}"


def test_every_exclusion_names_a_reason():
    """An exclusion without a reason is one nobody can object to."""
    assert R.NOT_HIS_ANNOTATIONS, "the exclusion list is empty; this is vacuous"
    unexplained = [k for k, v in R.NOT_HIS_ANNOTATIONS.items()
                   if not (v or "").strip()]
    assert not unexplained, f"excluded with no reason given: {unexplained}"


@pytest.mark.skipif(not R.RESPONSES.is_dir(), reason="folder absent")
def test_every_exclusion_still_corresponds_to_a_file_that_exists():
    """A DEAD EXCLUSION IS AN UNWIRED ADDITION, the shape this project keeps
    producing. If he deletes a foreign document, its entry should go too."""
    gone = [k for k in R.NOT_HIS_ANNOTATIONS
            if not (R.RESPONSES / k).exists()]
    assert not gone, (
        f"{len(gone)} exclusions name files that no longer exist: {gone}. They "
        f"exclude nothing and should be removed from the list.")


@pytest.mark.skipif(not R.RESPONSES.is_dir(), reason="folder absent")
def test_the_exclusion_does_not_reach_any_other_file():
    """The over-reach check stated as a set, not as a count."""
    excluded = {p.name for p in R.RESPONSES.glob("*")
                if R.is_a_response_file(p)
                and not R.is_one_of_his_annotated_responses(p)}
    assert excluded == set(R.NOT_HIS_ANNOTATIONS), (
        f"the set of files actually excluded is {sorted(excluded)}, which is "
        f"not the set named in NOT_HIS_ANNOTATIONS "
        f"({sorted(R.NOT_HIS_ANNOTATIONS)}). A file is being dropped by "
        f"something other than the explicit list.")


@pytest.mark.skipif(not R.RESPONSES.is_dir(), reason="folder absent")
def test_the_readability_predicate_was_not_narrowed():
    """`is_a_response_file` answers 'can the reader read this at all?' and the
    reader-gap check depends on it. Narrowing it would make an unparseable file
    stop being reported as a gap -- the opposite of what is wanted."""
    for name in R.NOT_HIS_ANNOTATIONS:
        p = R.RESPONSES / name
        if not p.exists():
            continue
        assert R.is_a_response_file(p), (
            f"{name} is no longer considered readable, so a genuine reader gap "
            f"in it would go unreported. The exclusion belongs in "
            f"is_one_of_his_annotated_responses, not in is_a_response_file.")


@pytest.mark.skipif(not R.RESPONSES.is_dir(), reason="folder absent")
def test_the_heading_filter_is_still_only_applied_to_markdown():
    """EXECUTED, not read. Applying it to .txt was measured at 18 of 598 lost,
    so this asserts the behaviour the measurement licensed, both ways."""
    # It still fires on a markdown heading...
    assert R._looks_like_a_markdown_heading("# Recommendation")
    # ...and one of his real short verdicts would be caught by it, which is
    # precisely why it must not reach his files.
    assert R._looks_like_a_markdown_heading("# Go with option B"), (
        "the filter no longer matches 'Go with option B'. If it has been "
        "weakened, re-measure before widening the extensions it reaches.")
    texts = {r["text"].strip() for r in R.annotations()}
    assert "Go with option B" in texts, (
        "the filter has been applied beyond markdown and is eating his "
        "verdicts")
