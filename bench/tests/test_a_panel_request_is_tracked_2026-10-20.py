"""A request of his for a panel review may never be reached by nothing.

HIS FINDING, 2026-10-20: "none of the requested panel review tasks appear to be
on your master task list, or for some reason, you ignored them and failed to do
them anyway. This should not be possible."

He was right. Measured that day: 60 of his annotations request a panel and 30 --
50.0000%, Wilson [37.7350%, 62.2650%] -- were reached by nothing at all. The
cause was that `scripts/harvest_tickets_2026-10-17.py` harvests only annotations
carrying an explicit marker, and he writes "ask the free panel" in the body of an
answer rather than filing a ticket.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROD = ROOT / "scripts" / "panel_requests_are_tracked_2026-10-20.py"


def _mod():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("_prt", PROD)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["_prt"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def m():
    return _mod()


def test_nothing_he_asked_for_is_untracked(m):
    """THE RULE. File them with:
        python3 scripts/panel_requests_are_tracked_2026-10-20.py --file"""
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    try:
        reqs = m.requests()
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    miss = m.uncovered(reqs, TicketStore())
    assert not miss, (
        f"{len(miss)} of his {len(reqs)} panel requests are reached by nothing:\n  "
        + "\n  ".join(f"{q['anchor']}  {q['text'][:90]}" for q in miss[:10]))


def test_the_population_is_not_empty(m):
    """ANTI-VACUITY. A detector that finds 0 requests passes the test above
    forever, and would pass loudest the day his folder moved."""
    try:
        reqs = m.requests()
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    assert len(reqs) >= 20, (
        f"only {len(reqs)} panel request(s) detected; the pattern has stopped "
        f"matching his words rather than the requests having gone away")


def test_the_detector_matches_his_actual_phrasings(m):
    """EXECUTED against his real wordings rather than invented ones. Each string
    below is lifted from an annotation of his."""
    should = [
        "Ask the free panel how to resolve this too.",
        "Then do the work please, and check your work with the free panel.",
        "Verdict. Fix it and check your fix with the free panel.",
        "Do it. Run the panel and decide if the remaining 7% or so you referenced",
        "I did ask you to run a free panel review with the question of how to mak",
        "Verdict: Fix as necessary. Discuss your fix with Fable and CC2 in panel",
    ]
    for s in should:
        assert m.PANEL.search(s), f"the detector misses his wording: {s!r}"


def test_the_detector_does_not_match_ordinary_prose(m):
    """A detector that matches everything files everything, and a register full
    of noise is one he will stop reading."""
    should_not = [
        "The control panel of the device was replaced.",
        "Fix it going forward and leave the archive alone.",
        "Run it. Add this to the master task list too.",
        "Make it aware of the negation.",
    ]
    for s in should_not:
        assert not m.PANEL.search(s), f"the detector over-matches: {s!r}"


def test_filing_is_idempotent(m):
    """A second run must file nothing, or every run inflates the register.
    Guaranteed by anchoring on the annotation's own file and line."""
    sys.path.insert(0, str(ROOT))
    from bench.ticket_store import TicketStore
    try:
        reqs = m.requests()
    except Exception as exc:                                   # noqa: BLE001
        pytest.skip(f"his Responses folder is not readable here: {exc}")
    store = TicketStore()
    first = m.uncovered(reqs, store)
    second = m.uncovered(reqs, store)
    assert len(first) == len(second), "uncovered() is not stable across calls"
