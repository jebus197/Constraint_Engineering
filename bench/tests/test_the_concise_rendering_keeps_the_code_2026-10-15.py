"""The concise rendering must not collapse the code it is asking a seat to review.

THE DEFECT, MEASURED BY CALLING THE FUNCTION rather than reading it.
`_apply_phenotype_transform` promises in its own docstring that it "transforms
the directive text without changing the underlying constraints" and that "only
presentation is modified". For CODE UNDER REVIEW that promise was false, because
in Python indentation IS syntax and a repeated definition IS the thing the
reviewer is being asked to look at.

On a situation packet holding 20 repeated function definitions, measured
2026-10-15 before the repair:

    format_style="full"     2,277 chars, 20 `def `, 80 indented lines
    format_style="concise"    193 chars,  1 `def `,  0 indented lines

2,085 characters lost, 91.5277%, and 19 of 20 function definitions DELETED. Step
5 strips every line and joins blocks with a space; step 6 then deduplicates
lines that are semantically similar, which near-identical function definitions
always are. The recorded defect notes the concise rendering reaches 4 of the 5
live models, 80.0000%, Wilson [37.5535%, 96.3776%] -- so 4 of 5 seats asked to
review code were shown 1 function of 20, unindented.

WHY FENCE PROTECTION ALONE WOULD NOT HAVE WORKED, and this is why the fix was
measured rather than assumed: the code is NOT fenced.
`_build_situation_packet` emits it under a plain `=== CODE EXTRACTS ===` section
marker. A first design that protected only ``` blocks would have passed its own
review and changed nothing. Both forms are protected.

THE RESTORE HAPPENS BEFORE THE LENGTH CAP, deliberately, so the cap measures the
true size. Restoring after it would let a seat's capacity limit be computed
against a placeholder, which is the same class of error as measuring a
configuration other than the one about to run.

THESE TESTS CALL THE TRANSFORM. A test that asserted on the source text of the
transform could not tell a protected pipeline from an unprotected one, because
each description is individually consistent.
"""

from __future__ import annotations

import sys
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import composer as C  # noqa: E402

STYLES_THAT_COMPRESS = ("concise", "minimal")


def _repeated_defs(n: int = 20) -> str:
    return "\n".join(
        f"def helper_{i}(values):\n"
        f"    total = 0\n"
        f"    for v in values:\n"
        f"        total += v\n"
        f"    return total / len(values)\n"
        for i in range(n)
    )


def _packet(code: str) -> str:
    return C._build_situation_packet(
        review_target="t.py", code_extracts=code, verified_facts="",
        explicit_unknowns="", adversarial_brief="b", interaction_surface="",
    ).text


def _indented(text: str) -> int:
    return sum(1 for line in text.split("\n") if line.startswith("    "))


# --------------------------------------------------------------------------
# The measured defect, as a property.
# --------------------------------------------------------------------------

@pytest.mark.parametrize("style", STYLES_THAT_COMPRESS)
def test_every_definition_survives(style):
    raw = _packet(_repeated_defs())
    out = C._apply_phenotype_transform(
        raw, C.PhenotypeTransform(format_style=style))
    assert out.count("def ") == 20, (
        f"{20 - out.count('def ')} of 20 function definitions were deleted by "
        f"format_style={style!r}; a seat cannot review code it was not shown"
    )


@pytest.mark.parametrize("style", STYLES_THAT_COMPRESS)
def test_indentation_survives(style):
    raw = _packet(_repeated_defs())
    out = C._apply_phenotype_transform(
        raw, C.PhenotypeTransform(format_style=style))
    assert _indented(out) == _indented(raw), (
        f"indentation was stripped by format_style={style!r}: "
        f"{_indented(raw)} indented lines became {_indented(out)}. In Python "
        "indentation is syntax, so this changes the meaning of the code."
    )


@pytest.mark.parametrize("style", STYLES_THAT_COMPRESS)
def test_the_code_section_is_character_for_character_identical(style):
    code = _repeated_defs(5)
    raw = _packet(code)
    out = C._apply_phenotype_transform(
        raw, C.PhenotypeTransform(format_style=style))
    assert code.strip() in out, (
        "the code extracts are no longer present verbatim; presentation was "
        "treated as separable from substance"
    )


def test_a_fenced_block_is_also_protected():
    """A model writes code back in fences, so both forms must survive."""
    fenced = ("=== ADVERSARIAL BRIEF ===\n"
              "```python\n"
              "def f(x):\n"
              "    if x:\n"
              "        return 1\n"
              "    return 0\n"
              "```\n"
              "=== END ADVERSARIAL BRIEF ===")
    out = C._apply_phenotype_transform(
        fenced, C.PhenotypeTransform(format_style="concise"))
    assert "    if x:" in out and "        return 1" in out, (
        "a fenced code block lost its indentation"
    )


def test_no_placeholder_leaks_into_the_output():
    """A leaked sentinel would reach a model as literal noise."""
    for style in ("full",) + STYLES_THAT_COMPRESS:
        out = C._apply_phenotype_transform(
            _packet(_repeated_defs(3)),
            C.PhenotypeTransform(format_style=style))
        assert "ZZVERBATIMBLOCK" not in out, (
            f"a protection placeholder survived into the output at "
            f"format_style={style!r}"
        )


# --------------------------------------------------------------------------
# The fix must not become a blanket no-op.
# --------------------------------------------------------------------------

def test_prose_is_still_compressed():
    """If concise stopped compressing anything, the repair would have removed a
    capability rather than protected one."""
    prose = ("Why: this is rationale and should go.\n"
             "1. A directive that\n   continues on a second line.\n"
             "2. Another directive that\n   continues on a second line.\n")
    full = C._apply_phenotype_transform(
        prose, C.PhenotypeTransform(format_style="full"))
    concise = C._apply_phenotype_transform(
        prose, C.PhenotypeTransform(format_style="concise"))
    assert len(concise) < len(full), (
        "concise no longer compresses prose, so the protection is too broad"
    )


def test_the_length_cap_measures_the_restored_text():
    """The restore happens BEFORE the cap, so a capacity limit is computed
    against real content and not against a placeholder."""
    raw = _packet(_repeated_defs(40))
    cap = 500
    out = C._apply_phenotype_transform(
        raw, C.PhenotypeTransform(format_style="concise",
                                  max_directive_chars=cap))
    assert len(out) <= cap + len("\n[... truncated for model capacity]"), (
        "the cap did not apply to the restored text, so a seat's capacity "
        "limit was measured against a placeholder"
    )


def test_the_protected_section_list_is_reachable():
    """A constant nothing reads is not additive."""
    assert "CODE EXTRACTS" in C._VERBATIM_SITUATION_SECTIONS
    assert "INTERACTION SURFACE" in C._VERBATIM_SITUATION_SECTIONS


def test_every_section_the_builder_emits_is_classified():
    """A new section may not arrive unprotected BY OMISSION.

    ADDED 2026-10-17. `_VERBATIM_SITUATION_SECTIONS` was a 2-entry tuple while
    `_build_situation_packet` emitted 7 sections, so the other 5 were
    indistinguishable from 5 deliberate decisions to let them compress -- and a
    section added later would inherit that silence rather than a decision. The
    mapping is now complete and the protected tuple is DERIVED from it, so this
    compares what the builder emits against what has been classified.

    The emitted names are read from the builder's SOURCE deliberately: calling
    it would only reveal the sections a particular call happens to fill, and a
    section is unclassified whether or not today's arguments reach it.
    """
    src = pathlib.Path(C.__file__).read_text(encoding="utf-8")
    start = src.index("def _build_situation_packet(")
    end = src.index("\ndef ", start + 10)
    emitted = set(re.findall(r'f"=== ([A-Z][A-Z ]+) ===', src[start:end]))
    assert emitted, "no sections found; this test has gone blind"
    unclassified = sorted(emitted - set(C.SITUATION_SECTION_IS_VERBATIM))
    assert not unclassified, (
        "these sections are emitted but not classified as verbatim or "
        "compressible, so they are unprotected by omission: "
        + ", ".join(unclassified))
    # AND THE DERIVATION HOLDS: the tuple is exactly the True entries.
    assert set(C._VERBATIM_SITUATION_SECTIONS) == {
        k for k, v in C.SITUATION_SECTION_IS_VERBATIM.items() if v}


def test_a_compressible_section_really_does_compress():
    """The False entries are a decision, so it must be a decision with effect.

    Without this, every section could be marked True and the mapping would look
    complete while the phenotype transform did nothing -- the protection turned
    into a no-op, which is the other half of the additive standard.

    THE FIRST VERSION OF THIS ASSERTION WAS WRONG ABOUT THE CODE, not the other
    way round. It fed 12 identical unbulleted sentences and demanded the
    character count halve. Measured, that input goes 515 chars to 514 while
    going 13 lines to 1: step 5 joins a block into a single line, so step 6's
    LINE dedup never sees the repeats. Dedup fires across BLOCK boundaries, which
    is why 20 repeated `def ` lines collapsed to 1 -- each opened a new block.
    Both properties are now asserted on inputs where each one is real.
    """
    # PRESENTATION CHANGES on ordinary block-structured prose: 17 lines to 9.
    bulleted = "=== VERIFIED FACTS ===\n" + "\n".join(
        f"- The reading was repeated and agreed.\n  Supporting detail {i}."
        for i in range(8))
    out = C._apply_phenotype_transform(
        bulleted, C.PhenotypeTransform(format_style="concise"))
    assert len(out.split("\n")) < len(bulleted.split("\n")), (
        "a section marked compressible did not change presentation at all")

    # AND REPEATS ARE REMOVED where dedup can see them: 490 chars to 61.
    repeated = "=== VERIFIED FACTS ===\n" + "\n".join(
        "- The reading was repeated and agreed." for _ in range(12))
    out = C._apply_phenotype_transform(
        repeated, C.PhenotypeTransform(format_style="concise"))
    assert len(out) < len(repeated) / 2, (
        f"repeated lines in a compressible section were not deduplicated: "
        f"{len(repeated)} -> {len(out)} chars")

    # THE CONTRAST THAT MAKES THE MAPPING MEAN SOMETHING: the same repeated
    # lines inside a VERBATIM section survive untouched.
    protected = repeated.replace("VERIFIED FACTS", "CODE EXTRACTS")
    out = C._apply_phenotype_transform(
        protected, C.PhenotypeTransform(format_style="concise"))
    assert out.count("- The reading was repeated and agreed.") == 12, (
        "a verbatim section was deduplicated; the protection is not working")
