"""The runway is measured against the point sv REFUSES, not the loader's cut.

THE DEFECT, from decision 28 of 2026-11-08. `cdsfl_sv` refuses a save at a
FRACTION of the loader's limit, and `headroom` returned the distance to the
LOADER's limit. So every runway figure overstated by exactly the reserve, and
`entries_left` inherited it through its character branch: with the index at
23,674 characters sv reported 1,326 characters and room for 11 more entries,
where 76 characters and 0 entries remained before its own refusal. The lines
budget had the same shape, 124 reported against 114 remaining. The
overstatement was 1,250 of 25,000 and 10 of 200 -- the reserve itself, which is
the signature of the cause rather than a coincidence. The instrument built to
warn about the limit was the thing hiding it.

AND HIS RULING NAMED A LIMIT THAT COULD NOT MOVE. Decision 28 option 1 is
*"Raise the character limit"*, and the entry told him the limit is "a loader
budget rather than a physical constraint". `_MEMORY_INDEX_LIMIT_CHARS` is
neither ours nor a preference: it is read out of the installed binary that
enforces it. Re-extracted 2026-11-08 it is still 25000, with 200 lines and the
enforcing function unchanged. Raising our constant past the loader's would not
enlarge the index, it would let the loader TRUNCATE it silently. So the ruling
moved the only limit that is ours, the reserve, 0.95 -> 0.98.

THE 2 CHANGES BELONG TOGETHER AND THAT IS WHY THEY ARE 1 COMMIT. Shrinking the
reserve makes the margin thinner; leaving the report overstated would have made
a thinner margin invisible as well. Neither is safe without the other.
"""
from __future__ import annotations

import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SV = REPO / "scripts/cdsfl_sv.py"
BINARY = pathlib.Path(
    "/opt/homebrew/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe")


@pytest.fixture(scope="module")
def sv():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_sv_runway", SV)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_sv_runway"] = m
    spec.loader.exec_module(m)
    return m


def _audit(sv, chars: int, lines: int, median: int = 394):
    """An audit object carrying only what the runway properties read.

    The class is FOUND by the properties it carries rather than by its name, so
    a rename does not silently make this guard skip; and it takes a required
    `path`, which is supplied as a path that need not exist because nothing
    here reads the file.
    """
    cls = next((getattr(sv, n) for n in dir(sv)
                if isinstance(getattr(sv, n), type)
                and hasattr(getattr(sv, n), "headroom")
                and hasattr(getattr(sv, n), "entries_left")), None)
    assert cls is not None, "the audit class carrying `headroom` was not found"
    a = cls(path=pathlib.Path("/nonexistent/MEMORY.md"))
    a.chars, a.lines, a.median_entry = chars, lines, median
    return a


class TestTheReferencePointIsTheRefusal:
    def test_headroom_stops_at_the_refusal_not_the_loader_limit(self, sv):
        """THE LIVE CASE of 2026-11-08: 23,674 characters."""
        a = _audit(sv, 23_674, 150)
        refuse = int(sv._MEMORY_INDEX_LIMIT_CHARS * sv._MEMORY_INDEX_REFUSE_FRACTION)
        assert a.headroom == refuse - 23_674
        assert a.headroom != sv._MEMORY_INDEX_LIMIT_CHARS - 23_674, (
            "headroom still measures the distance to the loader's cut, which is "
            "the overstatement decision 28 names")

    def test_lines_headroom_stops_at_the_refusal_too(self, sv):
        a = _audit(sv, 10_000, 150)
        refuse = int(sv._MEMORY_INDEX_LIMIT_LINES * sv._MEMORY_INDEX_REFUSE_FRACTION)
        assert a.lines_headroom == refuse - 150

    def test_entries_left_inherits_the_corrected_reference(self, sv):
        """It divides headroom by the median entry, so it was wrong by the same
        reserve. At 1 character short of refusal no further entry fits."""
        a = _audit(sv, int(sv._MEMORY_INDEX_LIMIT_CHARS
                           * sv._MEMORY_INDEX_REFUSE_FRACTION) - 1, 150)
        assert a.entries_left == 0

    def test_the_overstatement_was_exactly_the_reserve(self, sv):
        """ANTI-VACUITY ON THE DIAGNOSIS. If the 2 reference points ever
        coincide, every assertion above passes while testing nothing."""
        reserve = sv._MEMORY_INDEX_LIMIT_CHARS - int(
            sv._MEMORY_INDEX_LIMIT_CHARS * sv._MEMORY_INDEX_REFUSE_FRACTION)
        assert reserve > 0, (
            "the refuse fraction no longer holds anything back, so there is no "
            "overstatement to prevent and this guard is vacuous")


class TestTheLoaderLimitsAreNotOursToRaise:
    def test_the_constants_still_match_the_installed_binary(self):
        """★ READ FROM THE THING THAT ENFORCES THEM, not from our record of it.
        This is the assertion that stops a future reading of his ruling raising
        the loader figure: if the binary ever does raise it, this test tells us
        rather than us guessing."""
        if not BINARY.is_file():
            pytest.skip(f"the installed binary is not at {BINARY}")
        data = BINARY.read_bytes()
        chars = {m.group(1) for m in re.finditer(rb"PRe=(\d+)", data)}
        lines = {m.group(1) for m in re.finditer(rb"fie=(\d+)", data)}
        assert chars == {b"25000"}, f"the loader's character limit moved: {chars}"
        assert lines == {b"200"}, f"the loader's line limit moved: {lines}"

    def test_our_constants_do_not_exceed_the_loader(self, sv):
        """Exceeding it would not enlarge the index; it would let the loader
        truncate it silently."""
        assert sv._MEMORY_INDEX_LIMIT_CHARS <= 25_000
        assert sv._MEMORY_INDEX_LIMIT_LINES <= 200
        assert 0 < sv._MEMORY_INDEX_REFUSE_FRACTION <= 1.0

    def test_the_ruling_moved_the_reserve(self, sv):
        """His ruling of decision 28, recorded as a property rather than prose."""
        assert sv._MEMORY_INDEX_REFUSE_FRACTION >= 0.98, (
            "decision 28 option 1 raised the only limit that is ours")
