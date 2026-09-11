"""Every panel round run under Section P must have a FULL RECORD note.

THE DIRECTIVE, verbatim: *"All P-pass results, external reviews (human or
machine), and both potential and actual adversarial findings, must be presented
in full and in unfiltered format ... Never summarise in place of the full
output."*

WHY A RATCHET AND NOT A ONE-OFF. Round 4's record was written by hand on
2026-09-10. Rounds 5 to 14 then had none, because writing one by hand is an ACT
and an act does not repeat -- the same reason the raw-record mirror had to become
`scripts/mirror_panel_records_2026-09-11.py`. Measured 2026-09-11 before this
guard: 14 rounds dispatched on or after the Section P ruling of 2026-09-09, and
**10 with a record -- 71.4286%, Wilson [45.3509%, 88.2786%], Clopper-Pearson
[41.8965%, 91.6111%]**. Now 14 of 14.

SCOPED TO THE RULING, NOT TO THE WHOLE ARCHIVE. 78 directories hold review
output and most predate the condition that a record be written; demanding a note
for a confer run from May would be asking the past to have been the present,
which is the scoping error that turned the paid-seat assertion red when its
population widened.

A NOTE IS MATCHED BY NAMING ITS DIRECTORY, WHICH CAUGHT A FALSE ZERO IN THE
FIRST VERSION OF THIS VERY MEASUREMENT. It searched the first 4,000 characters
of each note, and a record names its source directory in the closing "Where the
raw record lives" section -- past that window -- so it reported 0 of 14 covered
when the true figure was 10. Round 4's hand-written note genuinely did not name
its directory at all, and now does.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LOGS = REPO / "bench" / "logs"
NOTES = REPO / "experimental_notes"

#: The date Section P made a panel review a precondition on closing any entry.
RULING = "2026-09-09"

def _mirror():
    """The 1 module that decides what a review round IS and when it ran.

    IMPORTED, NOT REIMPLEMENTED. This file briefly carried its own copy of the
    seat-file list and of the 2 date regular expressions, making 3 copies of each
    across the compliance script, the Section-P guard and here -- all written on
    2026-09-11, while correcting exactly this defect elsewhere. The morning's own
    evidence is that copies drift: the disagreement pattern was repaired in the
    guard and not in the script, and the paid-seat population in the script and
    not in the guard.
    """
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "mirror_records", REPO / "scripts" / "mirror_panel_records_2026-09-11.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _post_ruling_rounds() -> list[str]:
    m = _mirror()
    if not LOGS.is_dir():
        return []
    return [d.name for d in sorted(p for p in LOGS.iterdir() if p.is_dir())
            if m.holds_review_output(d) and (m.round_date(d.name) or "") >= RULING]


def _all_record_text() -> str:
    """THE WHOLE OF EVERY NOTE, not a prefix. See the module docstring."""
    return "\n".join(p.read_text(encoding="utf-8", errors="replace")
                     for p in sorted(NOTES.glob("*FULL_RECORD*.md")))


class TestEveryPostRulingRoundHasARecord:
    def test_none_is_missing(self):
        if not _post_ruling_rounds():
            import pytest
            pytest.skip("this checkout has no bench/logs panel archive -- "
                        ".gitignore:41 excludes it, so a clone has none")
        text = _all_record_text()
        missing = [r for r in _post_ruling_rounds() if r not in text]
        assert not missing, (
            f"{len(missing)} panel round(s) dispatched under Section P have no "
            f"FULL RECORD note naming them: {missing}\n"
            f"Build one with:\n"
            f"  python3 scripts/make_panel_full_record_2026-09-11.py "
            f"<round_dir> '<title>' <Out_Name.md> < context.txt")

    def test_the_population_is_not_empty(self):
        """ANTI-VACUITY. With no post-ruling rounds the test above asserts
        nothing, and it would pass loudest the day the archive moved."""
        rounds = _post_ruling_rounds()
        if not rounds:
            import pytest
            pytest.skip("no panel archive in this checkout")
        assert len(rounds) >= 10, (
            f"only {len(rounds)} rounds found on or after {RULING}; the "
            f"coverage assertion is running on almost nothing")


class TestTheRecordsAreRealRecords:
    def test_each_record_reproduces_a_seat_verbatim(self):
        """A note that summarised instead of reproducing would satisfy a
        name-matching check and defeat the directive it exists to serve."""
        thin = []
        for p in sorted(NOTES.glob("*FULL_RECORD*.md")):
            t = p.read_text(encoding="utf-8", errors="replace")
            if "verbatim-begin" not in t and len(t) < 8000:
                thin.append(f"{p.name} ({len(t)} bytes, no verbatim region)")
        assert not thin, (
            f"these records carry no verbatim region and are short enough to be "
            f"summaries rather than records: {thin}")

    def test_a_foot_line_where_present_is_the_final_content(self):
        """Note standard: the foot-line is the note's FINAL content. Appending a
        section after it is how round 4's note briefly ended in the wrong place.

        TWO SCOPING CORRECTIONS, BOTH MADE WHEN THIS TEST WENT RED ON ITS OWN
        FIRST RUNS, and both are the same error at different widths.

        First it demanded v1.7. The standard says in terms that "Notes written
        under earlier versions retain their version-specific foot-lines", and 4
        records legitimately end with v1.4.

        Then it demanded a foot-line at all. Four records -- the geometry
        dialogue, the independent review, and 2 others -- have none, because they
        PREDATE the convention, and the standard says so itself: "A missing
        foot-line flags a note that predates or violates the standard." Adding
        v1.7 to a note from August would misdate it, and editing an archival
        record to satisfy a checker is the act task V8 exists to prevent.

        So the rule asserted is the one that actually holds for every note: IF a
        foot-line is present, it is the last content. Records written under the
        standard are held to HAVING one by the test below.
        """
        FOOT = "Written under CDSFL note standard v"
        bad = []
        for p in sorted(NOTES.glob("*FULL_RECORD*.md")):
            text = p.read_text(encoding="utf-8", errors="replace")
            if FOOT not in text:
                continue
            lines = [ln for ln in text.splitlines() if ln.strip()]
            if not lines[-1].startswith(FOOT):
                bad.append(f"{p.name} -> {lines[-1][:60]}")
        assert not bad, (
            "a foot-line is present but is not the note's final content:\n  "
            + "\n  ".join(bad))

    def test_a_record_for_a_post_ruling_round_carries_a_foot_line(self):
        """Records written under the standard must carry one. This is the half
        the scoping above must not quietly drop."""
        if not _post_ruling_rounds():
            import pytest
            pytest.skip("no panel archive in this checkout")
        FOOT = "Written under CDSFL note standard v"
        missing = []
        for p in sorted(NOTES.glob("*FULL_RECORD*.md")):
            text = p.read_text(encoding="utf-8", errors="replace")
            if not any(r in text for r in _post_ruling_rounds()):
                continue
            if FOOT not in text:
                missing.append(p.name)
        assert not missing, (
            f"{missing} document a round run under Section P and carry no "
            f"foot-line, so they were written under the standard without "
            f"declaring it")
