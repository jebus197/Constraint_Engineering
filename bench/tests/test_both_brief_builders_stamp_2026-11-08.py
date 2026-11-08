"""Both joint-brief builders stamp their artefacts. B125's prerequisite.

MEASURED BEFORE ANYTHING WAS CHANGED, and the figure is the finding:
`scripts/stamp_the_brief_artefacts_2026-11-06.py` was written on 2026-11-06,
carries 15 tests and its own mutation harness, and had stamped **0 of the 148
briefs on disk** -- Wilson 95% [0.000000, 0.025299], Clopper-Pearson
[0.000000, 0.024617].

THE CAUSE WAS NOT A FAULT IN THE STAMPER. It was reached by exactly 1 of the 2
joint-brief builders, and the only brief written on or after the day it was
built -- `severity_corrected_2026-11-06` -- came from the OTHER one,
`build_severity_joint_brief_2026-10-31.py`, which never called it. A mechanism
guarded by its own tests and reached by no production caller is the
addition-nothing-reaches half of the additive standard, confirmed 11 times in
this project's record.

★ MY FIRST MEASUREMENT OVER-MATCHED AND IS RECORDED HERE BECAUSE IT WOULD HAVE
MISLED. Searching the briefs for `sha256` returned 2 hits and I nearly reported
2 stamped briefs. Both were PROSE mentions -- `sha256;` and a backquoted
`sha256` -- in briefs dated 2026-10-06 and 2026-10-14, weeks before the stamper
existed. The stamper emits a specific heading, so the predicate is that
heading, and the true count is 0. A detector that matches a word instead of the
thing is the same shape as the 7 instrument false positives recorded earlier on
2026-11-08.

WHAT THIS DOES NOT DO, STATED SO THE ENTRY IS NOT READ AS CLOSED. B125's
accepted recommendation is a COMPOSED fix: the brief quotes the STATE of every
file it references, AND the dispatcher REFUSES when a referenced file has moved
since. This wires the existing stamp into the builder that was missing it,
which is the prerequisite for either half -- a stamp that reaches no brief
cannot be composed with anything. Neither half of the composition is built, and
no composability claim is made here, because nothing has been measured against
either part alone.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
STAMPER = REPO / "scripts/stamp_the_brief_artefacts_2026-11-06.py"
BUILDERS = (
    REPO / "scripts/build_period_joint_brief_2026-11-04.py",
    REPO / "scripts/build_severity_joint_brief_2026-10-31.py",
)
MARKER = "ARTEFACT STAMPS AT DISPATCH"


@pytest.fixture(scope="module")
def stamper():
    if not STAMPER.is_file():
        pytest.skip("the stamper is not in this checkout")
    spec = importlib.util.spec_from_file_location("_bs", STAMPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_placement_has_one_home(stamper):
    """Extracted so the second builder shares it instead of re-implementing."""
    assert callable(getattr(stamper, "insert_stamp", None)), (
        "the stamper exposes no insert_stamp, so each builder would have to "
        "carry the placement rule and the title-splitting bug could recur")


@pytest.mark.parametrize("builder", BUILDERS, ids=lambda p: p.name)
def test_every_joint_brief_builder_is_wired(builder):
    """THE DEFECT. 1 of 2 was wired, so 0 of 148 briefs carried a stamp."""
    if not builder.is_file():
        pytest.skip(f"{builder.name} is not in this checkout")
    src = builder.read_text(encoding="utf-8")
    assert "stamp_the_brief_artefacts_2026-11-06.py" in src, (
        f"{builder.name} does not load the stamper, so any brief it writes "
        f"records nothing about the state of the files it references")
    #: ★ NON-COMMENT LINES ONLY. The first version of this assertion matched
    #: the whole file, so a mutation that replaced the call with
    #: `pass  # text = _insert_stamp(text)` left the SUBSTRING in place and the
    #: test stayed green while the stamp was gone. A detector that matches a
    #: quotation of the call is the same shape as the 7 instrument false
    #: positives recorded earlier on 2026-11-08 -- this was the 8th.
    #: THE COMMENT IS STRIPPED FROM EACH LINE, not just skipped when the line
    #: BEGINS with one. The 2nd version of this check tested
    #: `not l.lstrip().startswith("#")`, and the mutation
    #: `pass  # text = _insert_stamp(text)` begins with `pass`, so the call
    #: still matched inside a mid-line comment. That was the 9th instance of
    #: this shape on 2026-11-08 and the 2nd in this one assertion.
    live = [l for l in src.splitlines()
            if "_insert_stamp(text)" in l.split("#", 1)[0]]
    assert live, (
        f"{builder.name} loads the stamper and never applies it on a live "
        f"line; a commented-out call does not stamp anything")


def test_the_stamp_actually_lands_in_a_brief(stamper):
    """EXECUTED on a synthetic brief rather than asserted about the source."""
    text = ("# A title\n\n## First subsection\n\nIt names "
            "`bench/reference_runner_v3.py` and `scripts/cdsfl_sv.py`.\n")
    out = stamper.insert_stamp(text, REPO)
    assert out != text, "insert_stamp returned the text unchanged"
    assert MARKER in out, f"the stamp block is absent from the result:\n{out[:300]}"
    assert "It names" in out, "the brief's own content was lost"


def test_a_two_line_title_is_not_split(stamper):
    """THE BUG THE EXTRACTION EXISTS TO AVOID REPEATING.

    The first version of the placement inserted after the FIRST `# ` line and
    split a 2-line title in half. That history is why the rule has 1 home
    rather than being copied into the second builder.
    """
    text = ("# Title line one\n# Title line two\n\n## Body\n\nnames "
            "`scripts/cdsfl_sv.py`.\n")
    out = stamper.insert_stamp(text, REPO)
    lines = out.splitlines()
    i1 = lines.index("# Title line one")
    i2 = lines.index("# Title line two")
    assert i2 == i1 + 1, (
        f"the title was split: line one at {i1}, line two at {i2}, with "
        f"{lines[i1 + 1]!r} between them")
    assert MARKER in out


def test_a_brief_with_no_subsection_still_gets_a_stamp(stamper):
    """The fallback branch. Without this the stamp would silently vanish."""
    text = "# Only a title\n\nnames `scripts/cdsfl_sv.py` and nothing else.\n"
    out = stamper.insert_stamp(text, REPO)
    assert MARKER in out, "a brief with no `## ` subsection lost its stamp"


def test_a_brief_naming_nothing_is_left_alone(stamper):
    """ANTI-VACUITY. If insert_stamp appended unconditionally, every test above
    would pass while the stamp said nothing about any real file."""
    text = "# A title\n\n## Body\n\nThis brief names no file at all.\n"
    out = stamper.insert_stamp(text, REPO)
    assert out == text, (
        "a brief referencing no artefact was still stamped, so the block is "
        "being appended unconditionally rather than describing real files")


def test_the_marker_is_the_stampers_own(stamper):
    """The predicate my first measurement got wrong.

    Searching for `sha256` matched prose in 2 briefs that predate the stamper.
    The heading is what identifies a real stamp, so this pins that the heading
    the guard looks for is the one the stamper emits.
    """
    text = "# T\n\n## B\n\nnames `scripts/cdsfl_sv.py`.\n"
    out = stamper.insert_stamp(text, REPO)
    assert MARKER in out, (
        f"the stamper no longer emits {MARKER!r}, so every brief-counting "
        f"measurement that looks for it silently reads 0")
