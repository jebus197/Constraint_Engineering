#!/usr/bin/env python3
"""B84 field 1: the HARD/SOFT class is recorded, and its reader is no longer an orphan.

★ WHY THIS IS BUILT WHEN THE REST OF B84 IS NOT. B87 settled it: *"ADDING THE
HARD/SOFT FIELD IS SEPARABLE AND IS NOT A DECISION: the directive already
requires the classification, so recording it is carrying out an instruction
rather than changing one."* Verified against the directive itself -- section 11
of `bench/directives/universal/cdsfl_operational.md` reads *"Before producing
any output, classify every constraint as HARD or SOFT."* The TERM
`constraint_class` appears 0 times there; the REQUIREMENT is what matters and it
is unambiguous. B84's other 3 fields each need a second ruling and are NOT built.

★ THE READER EXISTED AND HAD NO WRITER, which is this project's own
`additive-standard` symmetric defect seen from the other side.
`reference_runner_v3.stamp_sev_f` has read `e.get("constraint_class")` since the
severity work and NOTHING ever wrote the key, so `constraint_class_defaulted`
was True on every entry it ever stamped. This wires the writer, so the field is
not an addition nothing reaches -- it is the missing half of something already
reached.

★ IT REJECTS RATHER THAN COERCES, which is `_envelope_field_changes`'s own
stated discipline applied to a 2-valued field. The directive admits exactly HARD
and SOFT; anything else is a seat saying something the vocabulary has no room
for, and writing "" silently or guessing HARD would be worse than recording
nothing. A rejected value is NAMED in the log so the reply can be inspected.
"""
from __future__ import annotations

import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "bench"))

from bench.dm._types import Finding                            # noqa: E402
from bench.runner_core import parse_findings                   # noqa: E402
from bench import field_envelope as fe                         # noqa: E402

REPLY = """FINDING_ID: F1
SEVERITY: 0.7
FLAW_CLASS: 2
ABSTRACTION_INDEX: 0.5
DESCRIPTION: the retry loop never terminates

<<<CDSFL_FIELD id=F1 field=CONSTRAINT_CLASS>>>
{value}
<<<CDSFL_FIELD_END>>>
"""


class TestTheDirectiveActuallyRequiresIt:
    def test_the_requirement_is_in_the_directive_text(self):
        """★ THE CITATION IS CHECKED, not assumed. B87's justification rests
        entirely on the directive demanding this, and an unchecked citation is
        a shape this project has recorded propagating before."""
        d = ROOT / "bench" / "directives" / "universal" / "cdsfl_operational.md"
        assert d.is_file(), f"{d} is missing"
        text = d.read_text(encoding="utf-8")
        assert "classify every constraint as HARD or SOFT" in text, (
            "the directive no longer requires the HARD/SOFT classification, so "
            "B87's grounds for this field being buildable WITHOUT a ruling of "
            "his have gone. Stop and ask him.")


class TestTheFieldExistsAndDefaultsEmpty:
    def test_the_dataclass_carries_it(self):
        f = Finding(finding_id="F", model_id="m", round_idx=1, flaw_class=1,
                    severity=0.5, abstraction_index=0.5)
        assert f.constraint_class == "", "the default must be empty, not a guess"

    def test_positional_construction_is_unbroken(self):
        """★ THE FROZEN DATACLASS CONTRACT. The field is appended LAST so every
        existing positional construction site still works."""
        f = Finding("F2", "m", 1, 1, 0.5, 0.5)
        assert f.finding_id == "F2" and f.constraint_class == ""

    def test_it_is_a_canonical_envelope_field(self):
        assert "CONSTRAINT_CLASS" in fe.CANONICAL_FIELDS


class TestItTravelsEndToEnd:
    @pytest.mark.parametrize("given,want", [("HARD", "HARD"),
                                            ("soft", "SOFT"),
                                            ("  Hard  ", "HARD")])
    def test_a_valid_class_reaches_the_finding(self, given, want):
        got = [f.constraint_class for f in
               parse_findings("m", 1, REPLY.format(value=given))]
        assert got == [want], (
            f"the envelope carried {given!r} and the finding got {got}. The "
            f"reader `stamp_sev_f` would still see a defaulted class.")

    @pytest.mark.parametrize("bad", ["probably important", "CRITICAL", "0.8", ""])
    def test_an_unrecognised_value_is_refused_not_coerced(self, bad):
        got = [f.constraint_class for f in
               parse_findings("m", 1, REPLY.format(value=bad))]
        assert got == [""], (
            f"{bad!r} was coerced to {got}. The directive admits HARD and SOFT "
            f"only; writing a guess is worse than recording nothing.")


class TestTheRegistryWritesIt:
    def test_the_writer_names_the_key(self):
        """Executed rather than grepped where possible; here the write is deep
        inside `register`, so the declaration is asserted AND the reader is
        asserted to look for the same key, which is the pairing that was broken."""
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        assert '"constraint_class": getattr(finding, "constraint_class", "")' in src, (
            "the registry no longer writes constraint_class, so its reader is "
            "an orphan again")
        assert 'e.get("constraint_class")' in src, (
            "the reader that justified this writer has gone; re-check whether "
            "the field is still wired to anything")
