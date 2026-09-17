#!/usr/bin/env python3
"""The P5 clause about CC1's own position has an instrument, and it is executed.

FOUNDER, 2026-09-17: *"If this is a missing test/instrument, then build it and
implement it, and add it to the program of study for the next simulated run."*

The `pr` protocol says the panel runs without compelled convergence and that
*"CC1 actively participates with its own position and synthesizes the range"*.
Every other clause of P5 had an instrument; this half had none.

EVERY TEST HERE CALLS THE SCRIPT OR ITS FUNCTIONS against records built for the
purpose, and 1 runs it against the REAL round-17 record. The script itself is
never asserted about by reading its source: what is checked is what it returns
when it is handed a record that does or does not satisfy the clause.

THE INSTRUMENT MUST BE ABLE TO SAY NO. `test_a_record_with_no_cc1_section_is_not
_satisfied` and `test_a_position_that_misses_a_disagreed_entry_is_not_satisfied`
are the negative controls: an instrument that returns SATISFIED for every record
measures nothing, which is the failure this project has found 11 times.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "p5_cc1_position_2026-09-17.py"
REAL_RECORD = ROOT / "experimental_notes" / "Panel_Round17_FULL_RECORD_2026-09-17.md"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("p5_probe", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _record(tmp_path, cc1_section: str = "", *, fable_a23="HOLDS", name="r.md") -> Path:
    """A minimal round record in the shape the real ones have."""
    text = f"""# Panel round 99 — the full record

## Seats and cost

2 seats.

{cc1_section}
## Seat: cc2

## VERDICTS

- **entry**: A23
- **verdict**: **FAILS**

- **entry**: A40
- **verdict**: **HOLDS**

## Seat: fable

## Per-entry verdicts

- **A23** — claim: something. **{fable_a23}.** Refutation: a thing.
- **A40** — claim: another. **HOLDS.** Refutation: another thing.
"""
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


class TestTheRangeIsDerivedFromTheSeatsOwnWords:
    def test_it_reads_both_verdict_shapes_the_seats_actually_write(self, mod, tmp_path):
        got = mod.measure(_record(tmp_path))
        assert got["seats"] == {"cc2": 2, "fable": 2}, got["seats"]
        assert set(got["range"]) == {"A23"}, got["range"]
        assert got["range"]["A23"] == {"cc2": "FAILS", "fable": "HOLDS"}

    def test_agreement_everywhere_is_reported_as_vacuous_not_as_a_pass(self, mod, tmp_path):
        """0 of 0 covered is not evidence that anything was synthesised."""
        rec = _record(tmp_path, "## CC1's own position\n\nAll HOLDS.\n",
                      fable_a23="FAILS")
        got = mod.measure(rec)
        assert got["range"] == {}
        assert got["verdict"] == "VACUOUS"


class TestItCanSayNo:
    def test_a_record_with_no_cc1_section_is_not_satisfied(self, mod, tmp_path):
        got = mod.measure(_record(tmp_path))
        assert got["cc1_position_section"] is False
        assert got["verdict"] == "NO_CC1_POSITION"
        assert got["range_missing"] == ["A23"]

    def test_a_position_that_misses_a_disagreed_entry_is_not_satisfied(self, mod, tmp_path):
        rec = _record(tmp_path, "## CC1's own position and synthesis\n\n"
                                "A40 HOLDS, and that is all I have to say.\n")
        got = mod.measure(rec)
        assert got["verdict"] == "RANGE_NOT_COVERED"
        assert got["range_missing"] == ["A23"], got

    def test_naming_the_entry_without_a_verdict_is_not_a_position(self, mod, tmp_path):
        rec = _record(tmp_path, "## CC1's own position and synthesis\n\n"
                                "The seats differ on A23. I leave it to the reader.\n")
        assert mod.measure(rec)["verdict"] == "RANGE_NOT_COVERED"


class TestItCanSayYes:
    def test_a_position_naming_every_disagreed_entry_is_satisfied(self, mod, tmp_path):
        rec = _record(tmp_path, "## CC1's own position, and the range across the seats\n\n"
                                "A23: cc2 says FAILS, fable says HOLDS, and my position is "
                                "FAILS, because execution reproduces both defects.\n")
        got = mod.measure(rec)
        assert got["verdict"] == "SATISFIED"
        assert got["range_covered"] == ["A23"] and got["range_missing"] == []


class TestAgainstTheRealRound:
    def test_round_17_carries_a_cc1_position_covering_its_range(self):
        """The clause, implemented as well as measured (founder ruling, 2026-09-17).
        Round 17's seats disagreed on 2 entries; both are answered in the record."""
        r = subprocess.run([sys.executable, str(SCRIPT), str(REAL_RECORD)],
                           capture_output=True, text=True, timeout=300, cwd=ROOT)
        assert r.returncode == 0, r.stdout[-900:] + r.stderr[-300:]
        got = json.loads(r.stdout[r.stdout.index("{"):r.stdout.rindex("}") + 1])
        assert got["verdict"] == "SATISFIED"
        assert sorted(got["range"]) == ["A22", "A23"], got["range"]
        assert got["range"]["A23"] == {"cc2": "FAILS", "fable": "HOLDS"}

    def test_the_script_is_read_only_and_exits_non_zero_when_the_clause_is_unmet(
            self, tmp_path):
        rec = _record(tmp_path, name="unmet.md")
        before = rec.read_bytes()
        r = subprocess.run([sys.executable, str(SCRIPT), str(rec)],
                           capture_output=True, text=True, timeout=300, cwd=ROOT)
        assert r.returncode == 3, r.stdout[-400:]
        assert rec.read_bytes() == before, "the instrument edited the record it measured"
