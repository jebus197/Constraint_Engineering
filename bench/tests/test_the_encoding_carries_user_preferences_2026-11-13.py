"""The encoding template's user-preferences section, and its tie to the schema.

ENTRY B163, the explicit user-led form. His proposal, verbatim: *"there should
probably be a section in each encoding to store 'user preferences'."*

★ THE POINT OF THESE CONTRACTS IS THAT THE SECTION REUSES THE PARAMETER SCHEMA
RATHER THAN INVENTING A FORMAT. `bench/cdsfl_registry/schema.toml` already gives
every parameter a `constraint_class` of HARD or SOFT -- which IS the
mandatory-versus-latitude distinction -- plus `min_layer`, `default`, `type` and
`description`. A second preferences format would be 2 declarations of 1 fact.
C2 fails if the template names a field the schema does not have, so the 2 cannot
drift apart.
"""
from __future__ import annotations

import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
TEMPLATE = REPO / "bench" / "directives" / "universal" / "expert_encoding_template.md"
SCHEMA = REPO / "bench" / "cdsfl_registry" / "schema.toml"
ENGINE = REPO / "bench" / "cdsfl_registry" / "engine.py"


@pytest.fixture(scope="module")
def section() -> str:
    t = TEMPLATE.read_text()
    marker = "SECTION: User Preferences"
    assert marker in t, (
        "the encoding template carries no user-preferences section. His proposal "
        "was that each encoding hold one; without it there is nowhere for a "
        "researcher's stated preferences to live.")
    return t[t.index(marker):]


def test_c1_the_section_requires_provenance_on_every_entry(section):
    """A preference you cannot trace cannot be questioned, or withdrawn."""
    # ★ SCOPED TO THE ENTRY SHAPE, not the whole section. The first version
    # tested `field in section`, and these names also appear in the prose
    # explaining why they are required -- so mutation T1 removed `stated_by`
    # from the shape and the contract STAYED GREEN. A substring present twice is
    # not evidence that either occurrence survives.
    shape = section[section.index("[user_preferences."):]
    shape = shape[:shape.index("# ---")]
    declared = set(re.findall(r"^#\s{3}(\w+)\s+=", shape, re.M))
    for field in ("stated_by", "stated_on", "source"):
        assert field in declared, (
            f"the ENTRY SHAPE does not carry {field!r}; it declares {sorted(declared)}. "
            f"The explicit form exists so a preference can be pointed at and "
            f"struck; one with no author and no date cannot be.")
    assert re.search(r"REQUIRED", section), (
        "provenance is described but not required, so it will be omitted")


def test_c2_every_field_named_exists_in_the_real_schema(section):
    """★ The anti-drift contract. The template must not invent a vocabulary."""
    schema = SCHEMA.read_text()
    declared = set(re.findall(r"^#\s{3}(\w+)\s+=", section, re.M))
    assert declared, "no entry fields were parsed from the section"
    schema_fields = set(re.findall(r"^(\w+)\s*=", schema, re.M))
    provenance = {"stated_by", "stated_on", "source"}
    borrowed = declared - provenance
    missing = sorted(f for f in borrowed if f not in schema_fields)
    assert not missing, (
        f"the section names field(s) the parameter schema does not have: "
        f"{missing}. Either the schema changed and this section is stale, or a "
        f"new format is being invented beside the existing one.")
    assert "constraint_class" in borrowed, (
        "the section no longer reuses constraint_class, which IS the "
        "mandatory-versus-latitude distinction the schema already carries")


def test_c3_the_harness_may_propose_and_may_not_write(section):
    """The boundary the panel reached independently on standards currency."""
    # ★ THE NORMATIVE SENTENCE, not the heading. Section 3's own heading reads
    # "THE HARNESS MAY PROPOSE. THE HARNESS MAY NOT WRITE.", so a section-wide
    # search for that phrase survives deleting the rule itself -- mutation T3
    # replaced the rule with "A machine may update this file" and this contract
    # STAYED GREEN. The heading announces; the sentence binds.
    body = section[section.index("3. THE HARNESS MAY PROPOSE"):]
    body = body[body.index("\n"):]            # drop the heading line itself
    # ★ STRIP THE COMMENT PREFIXES FIRST. The template wraps prose across lines
    # as `A machine may\n# NOT write this file.`, so a pattern expecting
    # whitespace between the words cannot match -- `#` is not whitespace. The
    # rule is present and the contract could not see it. Normalise, then match.
    body = re.sub(r"\n#\s?", " ", body)
    assert re.search(r"may\s+NOT\s+write", body, re.I), (
        "the section's BODY does not forbid the harness writing it; a heading "
        "that says so is an announcement, not a rule")
    assert not re.search(r"may\s+(?:update|write|edit)\s+this\s+file", body, re.I), (
        "the body permits the harness to write the file, which is a machine "
        "mutating a human's stated constraint with no human in the loop")
    assert "ticket_store" in section, (
        "no proposal route is named, so 'propose, do not write' has nowhere to "
        "go and becomes 'do nothing'")


def test_c4_the_contested_decisions_are_named_not_silently_decided(section):
    """What is deliberately absent must be stated, or a reader assumes it was missed."""
    assert re.search(r"NOT\s+SPECIFIED", section, re.I), (
        "the section does not say what it deliberately leaves open")
    assert re.search(r"LENGTH BOUND", section, re.I), (
        "the length bound is not named as deferred; a reader will think it was "
        "forgotten rather than sequenced")
    assert "engine.py" in section, (
        "the layer-position decision is not named, and it is the one that "
        "decides what a preference may override")


def test_c5_the_layer_decision_is_still_genuinely_open(section):
    """If a `user` layer ever lands, this contract must be revisited, not ignored."""
    engine = ENGINE.read_text()
    m = re.search(r"VALID_LAYERS\s*=\s*\{([^}]*)\}", engine)
    assert m, "VALID_LAYERS is gone from the engine"
    layers = set(re.findall(r'"(\w+)"', m.group(1)))
    assert layers == {"universal", "domain", "task", "model"}, (
        f"the engine's layers changed to {sorted(layers)}. If `user` has been "
        f"added, the template's 'NOT SPECIFIED' note about layer position is "
        f"now stale and must be updated rather than left contradicting the code.")
