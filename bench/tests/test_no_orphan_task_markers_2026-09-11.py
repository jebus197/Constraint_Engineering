"""A task marker that follows a non-entry line is read by nobody and lies to a human.

FOUND 2026-09-11 while working V2. The master task list carried 94 markers for 88
distinct ids. Two of the duplicates were ORPHANS -- `<!-- task: 2.1 | state: DONE
| status: ENABLED -->` and the same for 5.1, each sitting under a continuation
PARAGRAPH rather than under an entry line.

WHY THAT IS WORSE THAN IT LOOKS. `task_list_markers.parse_entries` reads the
marker from the line IMMEDIATELY AFTER an entry line and nowhere else, so an
orphan is invisible to every guard in the suite: the DONE-evidence check, the
state census, the pre-commit gate. A human reading the file sees "DONE, ENABLED"
with NO EVIDENCE FIELD and has no way to know the machine never saw it. That is 2
representations of one truth with 1 of them dead -- the shape `execute-do-not-grep`
names, appearing in the tracker rather than in code.

AND 4 MORE WERE A NAME COLLISION I CREATED. Closing tonight's work I added
entries P1 to P4; Section P's own CONDITIONS are already called P1 to P4 at the
top of the same file. Six ids carried 2 markers each and no guard noticed.
Renamed to A20 to A23.

THE DETECTION USES THE PROJECT'S OWN PATTERN, imported rather than restated. A
first cut wrote its own "looks like an entry" regex and matched
`**The gap is constrained deliberately.**` -- "The" is `[A-Z]` followed by
letters and a space -- so it judged the orphan to be live and removed nothing.
Two representations of one rule is the defect this file is about.
"""
from __future__ import annotations

import collections
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import task_list_markers as tlm  # noqa: E402

LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def _marker_lines():
    lines = LIST.read_text(encoding="utf-8").splitlines()
    for i, ln in enumerate(lines):
        m = tlm.MARKER.match(ln)
        if m:
            yield i + 1, m.group(1), (lines[i - 1] if i else "")


class TestEveryMarkerIsReachable:
    def test_no_marker_follows_a_non_entry_line(self):
        orphans = [(n, ident, prev[:70])
                   for n, ident, prev in _marker_lines()
                   if not tlm._is_entry(prev)]
        assert not orphans, (
            f"these markers follow a continuation paragraph, so parse_entries "
            f"never reads them and no guard in the suite can see them, while a "
            f"human reads them as state: {orphans}")

    def test_no_task_id_carries_two_markers(self):
        ids = [ident for _n, ident, _p in _marker_lines()]
        dupes = {k: v for k, v in collections.Counter(ids).items() if v > 1}
        assert not dupes, (
            f"these ids carry more than 1 marker, so which one is authoritative "
            f"depends on where parse_entries happens to look: {dupes}")

    def test_every_parsed_entry_has_a_marker(self):
        """The other direction. An entry with NO marker has no state at all."""
        missing = [e.ident for e in tlm.parse_entries(LIST) if e.state is None]
        assert not missing, f"entries with no marker, and so no state: {missing}"


class TestTheCheckIsNotVacuous:
    def test_the_list_actually_has_markers(self):
        n = sum(1 for _ in _marker_lines())
        assert n >= 50, f"only {n} markers found; the pattern has stopped matching"

    def test_an_orphan_is_detected_when_one_exists(self, tmp_path):
        """POSITIVE CONTROL. If the detector could not fire, the assertions above
        would be passing on a file it cannot read."""
        f = tmp_path / "LIST.md"
        f.write_text(
            "**A1. A real entry.** Body text.\n"
            "<!-- task: A1 | state: DONE | status: COMMITTED | evidence: x.py -->\n"
            "\n"
            "**A continuation paragraph, not an entry.** More text.\n"
            "<!-- task: A1 | state: DONE | status: ENABLED -->\n",
            encoding="utf-8")
        lines = f.read_text().splitlines()
        found = [i + 1 for i, ln in enumerate(lines)
                 if tlm.MARKER.match(ln) and i and not tlm._is_entry(lines[i - 1])]
        assert found == [5], found

    def test_the_projects_own_entry_pattern_is_used(self):
        """The defect that made the first cut of this useless: a hand-rolled
        'looks like an entry' regex matched a bold prose opener."""
        assert not tlm._is_entry("**The gap is constrained deliberately.** More.")
        assert tlm._is_entry("**A19. S_k classifies the TARGET.** Body.")
        assert tlm._is_entry("**6.1 Record all run stop reasons.** Body.")
