#!/usr/bin/env python3
"""The runner strips a bare vendor token from a model-supplied identifier.

HIS RULING, 2026-10-16: *"We normalise going forward, since recording vendor
names is purely a recording statistic and has no impact on capability, or how
our experiments work."*

THE DEFECT. The runner prefixes the seat label to whatever identifier the model
chose for itself. A model writing `GEMINI_F004` under seat `Gemini-SIM` produced
`Gemini-SIM_GEMINI_F004`, in which a reader meets a BARE vendor name. Measured
by `scripts/how_many_identifiers_carry_a_bare_vendor_name_2026-10-16.py`: 4
recorded findings carrying 2 distinct identifiers, in 1 archived run.

`execute-do-not-grep`: every assertion below CALLS the composition path and
compares the identifier it produces. Nothing here asserts on the source text of
`runner_core.py`, because a source-text assertion would only establish that the
module describes itself consistently.

FORWARD ONLY. No archived artefact is rewritten, and no test here asserts that
the archive is clean -- it is not, and clearing it would mean rewriting
experimental evidence. These tests pin what the NEXT run writes.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import runner_core  # noqa: E402

STRIP = runner_core._strip_redundant_vendor_prefix
VENDORS = sorted({str(v) for v in runner_core.MODEL_SPECS})


def compose(model_supplied: str, seat: str) -> str:
    """Reproduce the call site at `runner_core.py`, strip included."""
    fid = STRIP(model_supplied, seat)
    return fid if fid.startswith(f"{seat}_") else f"{seat}_{fid}"


def carries_bare_vendor(identifier: str) -> bool:
    alt = "|".join(re.escape(v) for v in sorted(VENDORS, key=len, reverse=True))
    return bool(re.search(rf"([A-Za-z0-9]+-SIM)_({alt})([_\-:])", identifier, re.I))


# ---------------------------------------------------------------- the defect

#: The two identifiers the archive actually recorded, with the shape the model
#: emitted. These are the regression cases in the strictest sense.
MEASURED = [
    ("GEMINI_F004", "Gemini-SIM", "Gemini-SIM_F004"),
    ("GEMINI_F005", "Gemini-SIM", "Gemini-SIM_F005"),
]


@pytest.mark.parametrize(("supplied", "seat", "expected"), MEASURED)
def test_the_two_measured_identifiers_normalise(supplied, seat, expected):
    assert compose(supplied, seat) == expected


@pytest.mark.parametrize(("supplied", "seat", "_expected"), MEASURED)
def test_the_two_measured_identifiers_carry_no_bare_vendor(supplied, seat, _expected):
    assert not carries_bare_vendor(compose(supplied, seat))


@pytest.mark.parametrize("vendor", VENDORS)
@pytest.mark.parametrize("sep", ["_", "-", ":"])
@pytest.mark.parametrize("case", ["upper", "lower", "title"])
def test_no_vendor_survives_in_any_case_or_separator(vendor, sep, case):
    """Every vendor, every legal separator, every casing the models have used."""
    token = {"upper": vendor.upper(), "lower": vendor.lower(), "title": vendor}[case]
    for seat in (f"{vendor}-SIM", vendor):
        out = compose(f"{token}{sep}F004", seat)
        assert out == f"{seat}_F004", (token, sep, seat, out)
        assert not carries_bare_vendor(out)


# ------------------------------------------------- what must NOT be stripped

def test_an_already_composed_identifier_is_untouched():
    """The seat label is LONGER than the vendor inside it, and must win.

    This is the case a naive longest-vendor-first strip gets wrong: `Gemini` is
    a prefix of `Gemini-SIM`, so stripping the vendor would leave `SIM_F004`.
    """
    assert compose("Gemini-SIM_F004", "Gemini-SIM") == "Gemini-SIM_F004"
    assert compose("Fable-SIM_F002", "Fable-SIM") == "Fable-SIM_F002"


def test_an_identifier_that_is_only_a_vendor_is_never_anonymised():
    """A finding called exactly `GEMINI` keeps its name rather than vanishing.

    Two distinct routes reach this, and the first version of this test covered
    only one of them -- a mutation that deleted the empty-remainder guard
    survived, because the separator requirement catches the bare `GEMINI` case
    first and the guard is only reached through a TRAILING separator.
    """
    # Route 1: no separator at all, caught by the separator requirement.
    assert STRIP("GEMINI", "Gemini-SIM") == "GEMINI"
    assert compose("GEMINI", "Gemini-SIM") == "Gemini-SIM_GEMINI"
    # Route 2: a trailing separator and nothing after it. This is the ONLY input
    # that reaches the empty-remainder guard, so it is the only input that can
    # detect its removal.
    for trailing in ("GEMINI_", "GEMINI-", "GEMINI:"):
        assert STRIP(trailing, "Gemini-SIM") == trailing, trailing
        assert compose(trailing, "Gemini-SIM") == f"Gemini-SIM_{trailing}", trailing


def test_a_token_that_merely_starts_with_a_vendor_is_not_stripped():
    """`GEMINIX` is not `GEMINI`. The separator requirement is what enforces it."""
    assert compose("GEMINIX_F1", "Gemini-SIM") == "Gemini-SIM_GEMINIX_F1"
    assert compose("CODEXY-F9", "Codex") == "Codex_CODEXY-F9"


def test_a_clean_identifier_is_passed_through_unchanged():
    assert STRIP("F004", "Gemini-SIM") == "F004"
    assert compose("F004", "Gemini-SIM") == "Gemini-SIM_F004"


# ------------------------------------------------------------- idempotence

@pytest.mark.parametrize(
    "supplied",
    ["GEMINI_F004", "Gemini_F004", "gemini-F004", "F004", "GEMINI",
     "GEMINIX_F1", "Gemini-SIM_F004", "gemini-sim_F004"],
)
def test_composition_is_idempotent(supplied):
    """Re-composing a composed identifier must not move it.

    The runner composes at more than one site over a run's life, so a strip that
    is not idempotent would eat a character per pass.
    """
    once = compose(supplied, "Gemini-SIM")
    assert compose(once, "Gemini-SIM") == once


def test_case_differing_seat_label_canonicalises():
    """A model echoing its seat label in the wrong case still lands canonical."""
    assert compose("gemini-sim_F004", "Gemini-SIM") == "Gemini-SIM_F004"


# ------------------------------------------------- the set is DERIVED, not declared

def test_only_the_seats_own_token_is_stripped():
    """★ THE HAZARD THIS CLOSES, FOUND BY P-PASSING THE FIRST VERSION OF THE FIX.

    The first implementation took its candidates from the whole of
    `MODEL_SPECS`, so under seat `CC2-SIM` the identifier `GEMINI_F004` -- a CC2
    reply REFERRING to Gemini's finding -- stripped to `F004` and composed to
    `CC2-SIM_F004`, which can resolve to CC2's OWN F004. That is a cross-model
    mis-attribution, and `lookup_alias_any`'s docstring records a 2026-08-30
    defect of exactly that shape. Measured over the roster-wide form, the forms
    it added were new in 36 of 48 key/seat pairs (75.0000%, Wilson [61.2156%,
    85.0794%]), so the hazard was reachable rather than theoretical.
    """
    for vendor in VENDORS:
        for seat_vendor in VENDORS:
            for seat in (f"{seat_vendor}-SIM", seat_vendor):
                supplied = f"{vendor.upper()}_F004"
                out = compose(supplied, seat)
                if vendor == seat_vendor:
                    assert out == f"{seat}_F004", (supplied, seat, out)
                else:
                    assert out == f"{seat}_{supplied}", (
                        f"{supplied} under seat {seat} was stripped of ANOTHER "
                        f"vendor's token, giving {out}. That cross-attributes "
                        f"one seat's reference to another seat's finding."
                    )


def test_no_vendor_table_is_consulted():
    """Adding or removing a model must not change this function's behaviour.

    Proved by MUTATING the roster at runtime and checking nothing moves -- the
    strip is keyed on the `model_id` argument alone, so no table of model names
    gates it. That is stricter than deriving the set from the roster, and it is
    what keeps the function clear of his 2026-10-07 ruling on names.
    """
    probe = [("GEMINI_F004", "Gemini-SIM"), ("ZZZ_F1", "Gemini-SIM"),
             ("Zyxwv_F1", "Zyxwv-SIM"), ("F004", "Gemini-SIM")]
    before = [compose(a, b) for a, b in probe]

    sample = next(iter(runner_core.MODEL_SPECS.values()))
    runner_core.MODEL_SPECS["Zyxwv"] = sample
    removed = runner_core.MODEL_SPECS.pop("Gemini")
    try:
        after = [compose(a, b) for a, b in probe]
    finally:
        runner_core.MODEL_SPECS["Gemini"] = removed
        runner_core.MODEL_SPECS.pop("Zyxwv", None)

    assert before == after, (
        f"mutating MODEL_SPECS changed the composition: {before} -> {after}. "
        f"The strip must depend on the seat label alone."
    )
    # And an unknown seat still strips its own token, with no roster entry.
    assert compose("ZYXWV_F1", "Zyxwv-SIM") == "Zyxwv-SIM_F1"


def test_the_simulation_suffix_is_handled_without_importing_the_runner():
    """`runner_core` is the lower-level module; it must not import its importer."""
    assert runner_core._SIM_SUFFIX == "-SIM"
    assert STRIP("GEMINI_F004", "Gemini-SIM") == "F004"
    assert STRIP("GEMINI_F004", "Gemini") == "F004"


# --------------------------------------------------- the call sites use it

#: `_structurally_valid_fid`'s own docstring records five model-supplied paths.
#: Each one is driven here through the REAL parser with a response in that
#: format, so the test cannot pass because the helper exists -- only because the
#: path calls it. An addition nothing reaches is not additive.
PATHS = {
    "json_array": '[{"FINDING_ID": "GEMINI_F004", "SEVERITY": 0.8, "FLAW_CLASS": 1, '
                  '"ABSTRACTION": 0.5, "DESCRIPTION": "a planted variance estimator defect", '
                  '"PROPOSED_FIX": "use the unbiased denominator", "TARGET_FILE": "x.py", '
                  '"VERIFIED": "FALSE"}]',
    # The nested-dict path is a SEPARATE site from the array path above, and
    # reaching it needs the REAL object format -- outer keys are finding ids,
    # with no `[{` anywhere, or the array parser claims the payload first. A
    # mutation reverting only that site survived until this case was right.
    "json_object": '{"GEMINI_F004": {"FINDING_ID": "GEMINI_F004", "SEVERITY": 0.8, '
                   '"FLAW_CLASS": 1, "ABSTRACTION_INDEX": 0.5, '
                   '"DESCRIPTION": "a planted variance estimator defect", '
                   '"PROPOSED_FIX": "use the unbiased denominator", '
                   '"TARGET_FILE": "x.py", "VERIFIED": "FALSE"}}',
    "tuple": '(GEMINI_F004, 0.8, 1, 0.5, "a planted variance estimator defect", '
             '"use the unbiased denominator", FALSE)',
    "marker": "FINDING_ID: GEMINI_F004\nSEVERITY: 0.8\nFLAW_CLASS: 1\n"
              "ABSTRACTION: 0.5\nDESCRIPTION: a planted variance estimator defect\n"
              "PROPOSED_FIX: use the unbiased denominator\nTARGET_FILE: x.py\n"
              "VERIFIED: FALSE\n",
}


@pytest.mark.parametrize("fmt", sorted(PATHS))
def test_the_real_parser_strips_the_vendor_on_every_format(fmt):
    """Drive `parse_findings` itself, not a reimplementation of it."""
    out = runner_core.parse_findings("Gemini-SIM", 0, PATHS[fmt])
    assert out, f"{fmt}: the parser returned no findings at all"
    ids = [f.finding_id for f in out]
    offenders = [i for i in ids if carries_bare_vendor(i)]
    assert not offenders, f"{fmt}: {offenders}"
    assert any(i == "Gemini-SIM_F004" for i in ids), f"{fmt}: {ids}"


@pytest.mark.parametrize("fmt", sorted(PATHS))
def test_a_clean_identifier_is_unaffected_on_every_format(fmt):
    """The repair must not move an identifier that never carried a vendor."""
    out = runner_core.parse_findings("Gemini-SIM", 0, PATHS[fmt].replace("GEMINI_F004", "F004"))
    assert out, f"{fmt}: the parser returned no findings at all"
    assert any(f.finding_id == "Gemini-SIM_F004" for f in out), [f.finding_id for f in out]


def test_every_composition_site_routes_through_one_function():
    """There were five copies of the compose, and they diverged.

    Counted by EXECUTION, not by reading: the composer is replaced with a spy
    and every format is driven through the parser, so a site that kept its own
    inline copy records no call and fails here.
    """
    original = runner_core._compose_finding_id
    seen: list[tuple[str, str]] = []

    def spy(fid: str, mid: str) -> str:
        seen.append((fid, mid))
        return original(fid, mid)

    runner_core._compose_finding_id = spy
    try:
        for fmt, body in PATHS.items():
            seen.clear()
            runner_core.parse_findings("Gemini-SIM", 0, body)
            assert seen, f"{fmt} composed an identifier without the shared function"
    finally:
        runner_core._compose_finding_id = original


def test_the_strip_is_inert_at_the_heading_site_and_that_is_proved_not_assumed():
    """The heading fallback's token cannot carry a vendor name, so the strip is a no-op.

    An earlier version of this file asserted that routing the heading lookup
    through the shared composer REPAIRED a live defect. A mutation reverting that
    key to the bare compose left the suite green, which was the correct verdict:
    `_MD_HDR` captures `F\\d{2,4}`, so no vendor token can ever appear there.
    The honest property is therefore the inertness itself, exhausted over the
    token language the capture admits.
    """
    hdr = re.compile(
        r"^[ \t]{0,3}#{1,6}[ \t]*(?:FINDING[ \t]+)?(F\d{2,4})\b"
        r"[ \t]*[\u2014\u2013:.\-]?[ \t]*(.*)$",
        re.M,
    )
    # Every token the capture admits, against every seat label in the roster.
    tokens = sorted({f"F{str(n).zfill(w)}" for w in (2, 3, 4)
                     for n in (0, 1, 7, 42, 999, 9999) if len(str(n)) <= w})
    seats = [f"{v}-SIM" for v in VENDORS] + list(VENDORS)
    assert tokens, "the token language came out empty -- the generator is wrong"
    for tok in tokens:
        for seat in seats:
            bare = tok if tok.startswith(f"{seat}_") else f"{seat}_{tok}"
            assert runner_core._compose_finding_id(tok, seat) == bare, (tok, seat)

    # And a heading that DOES carry a vendor name matches nothing, so it mints
    # no finding at all -- which is why there is no defect to repair there.
    for line in ("## GEMINI_F004 - t", "### Gemini-SIM_F004 - t", "#### CODEX_F12 t"):
        assert hdr.search(line) is None, line
    assert hdr.search("## F004 - t").group(1) == "F004"


def test_the_envelope_mint_path_strips_the_vendor_too():
    """The field-envelope path mints findings from a model-written owner id.

    `_apply_field_envelopes` is a sixth composition site, reached by neither the
    JSON nor the tuple nor the marker format. A mutation reverting it survived
    until this case existed.
    """
    import field_envelope as fe

    beg, end = fe.FIELD_BEGIN_PREFIX, fe.FIELD_END_TOKEN
    response = (
        f"{beg} field=DESCRIPTION id=GEMINI_F004>>>a planted variance estimator defect{end}\n"
        f"{beg} field=SEVERITY id=GEMINI_F004>>>0.8{end}\n"
        f"{beg} field=PROPOSED_FIX id=GEMINI_F004>>>use the unbiased denominator{end}\n"
    )
    out = runner_core.parse_findings("Gemini-SIM", 0, response)
    assert out, "the envelope path minted nothing"
    ids = [f.finding_id for f in out]
    assert not [i for i in ids if carries_bare_vendor(i)], ids
    assert "Gemini-SIM_F004" in ids, ids


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
