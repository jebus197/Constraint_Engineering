"""The memory ledger's counted-stamp must be a DATE, not any string at all.

WHY. On 2026-08-26 `resources/MEMORY_EXCLUSIONS.md` line 11 read:

    ## Accounting (counted BROKEN-STAMP ;OLD: 2026-08-26 00:53 BST)

`BROKEN-STAMP` appears in no Python source anywhere -- not a fixture, not a
constant. It was typed in by hand while checking that sv REFUSES to advance the
stamp when a count fails, and it was then swept into commit 80faf11 alongside
docs/CURRENT_STATE.md. The prose directly beneath it still reads "Every figure
below was counted from that directory on the date in this heading", pointing at
a non-date.

It survived a 3929-test suite. Two guards already watch this file -- one in
test_documentation_drift_guards_2026-08-25.py and one in
test_recovery_memory_doc_repairs.py -- and BOTH check the TOTAL. Nothing checked
the date beside it. That is the shape this project keeps finding: the number was
watched and the thing next to it was not.

WHAT THIS ASSERTS. The heading parses as the format sv itself writes,
"%Y-%m-%d %H:%M %Z", and a corrupted stamp does NOT pass. Not that the heading
exists -- that it means something.
"""
import datetime as dt
import pathlib
import re

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
LEDGER = REPO / "resources" / "MEMORY_EXCLUSIONS.md"

# The exact shape sv writes: scripts/cdsfl_sv.py builds it with
#   datetime.now().astimezone().strftime("%Y-%m-%d %H:%M %Z")
HEADING = re.compile(r"^##\s+Accounting\s+\(counted\s+(?P<stamp>[^)]+)\)\s*$", re.M)
STAMP = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{2}:\d{2})\s+(?P<tz>[A-Za-z]{2,5})$")


def _stamp_of(text: str) -> str:
    m = HEADING.search(text)
    assert m, "the ledger has no '## Accounting (counted ...)' heading at all"
    return m.group("stamp").strip()


def parse_stamp(stamp: str):
    """Return a date, or None when the stamp is not one. Never raises."""
    m = STAMP.match(stamp.strip())
    if not m:
        return None
    try:
        return dt.datetime.strptime(f"{m.group('date')} {m.group('time')}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None


class TestTheParserDiscriminates:
    """Commissioned before it is trusted: known-good and known-bad must differ."""

    @pytest.mark.parametrize("good", [
        "2026-08-25 23:21 BST",
        "2026-01-01 00:00 GMT",
        "2026-12-31 23:59 UTC",
    ])
    def test_known_good_a_real_stamp_parses(self, good):
        assert parse_stamp(good) is not None, f"a valid stamp was rejected: {good}"

    @pytest.mark.parametrize("bad", [
        "BROKEN-STAMP ;OLD: 2026-08-26 00:53 BST",   # the actual defect
        "BROKEN-STAMP",
        "",
        "unknown",
        "2026-08-26",                                 # date with no time or zone
        "2026-13-01 00:00 BST",                       # month 13
        "2026-08-32 00:00 BST",                       # day 32
        "26-08-2026 00:53 BST",                       # wrong order
        "2026-08-26 25:00 BST",                       # hour 25
    ])
    def test_known_bad_a_non_date_is_rejected(self, bad):
        assert parse_stamp(bad) is None, (
            f"a non-date was accepted as a counted stamp: {bad!r}. The heading "
            "would then assert a freshness nothing supports."
        )

    def test_the_two_answers_are_not_the_same(self):
        assert (parse_stamp("2026-08-25 23:21 BST") is None) != (
            parse_stamp("BROKEN-STAMP ;OLD: 2026-08-26 00:53 BST") is None), (
            "the parser answers the same way for a date and for the literal string "
            "that sat in a canonical document"
        )


class TestTheRealLedger:
    def test_the_counted_stamp_is_a_date(self):
        """The guard that was missing. It FAILS on the tree as found 2026-08-26."""
        stamp = _stamp_of(LEDGER.read_text(encoding="utf-8"))
        assert parse_stamp(stamp) is not None, (
            f"the ledger's counted stamp is not a date: {stamp!r}\n"
            "The heading claims a count happened at a moment; a string that is not "
            "a moment cannot support that claim. Regenerate with sv, or run "
            "python3 scripts/cdsfl_sv.py once the memory directory is readable."
        )

    def test_the_stamp_is_not_in_the_future(self):
        """A stamp ahead of the clock is the timestamp defect of 2026-08-26, when
        five were typed rather than read and three were in the future."""
        stamp = _stamp_of(LEDGER.read_text(encoding="utf-8"))
        parsed = parse_stamp(stamp)
        if parsed is None:
            pytest.skip("stamp is not a date; the test above is the one reporting that")
        now = dt.datetime.now()
        assert parsed <= now + dt.timedelta(hours=26), (
            f"the ledger says it was counted at {stamp}, which is ahead of the "
            f"clock ({now:%Y-%m-%d %H:%M}). A count cannot have happened yet."
        )

    def test_no_test_marker_strings_survive_in_the_ledger(self):
        """Broader than the stamp: nothing that looks like a scratch marker
        belongs in a canonical document."""
        text = LEDGER.read_text(encoding="utf-8")
        for marker in ("BROKEN-STAMP", "XXX-TEST", "PLACEHOLDER", "TODO-STAMP", "FIXME"):
            assert marker not in text, (
                f"the scratch marker {marker!r} is committed in "
                f"{LEDGER.relative_to(REPO)}. It reached the repository through "
                "sv's auto-staging on 2026-08-26 (commit 80faf11)."
            )
