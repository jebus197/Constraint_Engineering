"""The harvester's queue-operation repair is live code that NO TEST REACHED.

WHY THIS FILE EXISTS. B102 measured that 206 of 1,421 distinct messages of his
exist ONLY as a `queue-operation` entry, because he typed them while a turn was
already running, and that `from_chat` dropped every one of them. The repair was
applied inline in `scripts/harvest_tickets_2026-10-17.py` and cites B102's own
figure in its comment. But measured 2026-11-08, `queue-operation` appears 0
times and `enqueue` 0 times in `bench/tests/test_ticket_harvest_2026-10-17.py`,
and the only guard in the suite mentioning either guards the UNION READER
`scripts/his_messages.py` rather than the harvester. So the repair was an
addition nothing executed -- the symmetric half of `additive-standard`, which
requires every new branch to be wired to a caller AND executed by a test.

WHAT IT ASSERTS, BY EXECUTION RATHER THAN BY READING THE SOURCE. The real
`from_chat` is called against a fixture transcript, with the module's
`TRANSCRIPTS` constant pointed at a temporary directory. No production code is
changed to make this testable. `execute-do-not-grep`: a test that asserted on
the presence of the `queue-operation` literal would pass just as well against a
branch that had stopped working.

THE PROPERTY THAT MATTERS IS `ruled`, NOT MERELY THE TEXT. B102's own words:
the repair matters "because `ruled` depends on the role, which the queue entry
lacks". A queued message carries no `message.role`, so a reader that recovered
the text but defaulted the role would produce a row with an EMPTY `ruled` --
indistinguishable downstream from a message he never ruled on. The row must
come back as `chat:user` with `ruled` set.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = REPO / "scripts/harvest_tickets_2026-10-17.py"


def _module():
    """A fresh copy of the harvester, so monkeypatching cannot leak."""
    spec = importlib.util.spec_from_file_location("_harvest_under_test", PROD)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


TS = "2026-11-08T03:14:15.000Z"
#: Ends with the marker because that is the form `MARKER` accepts and the form
#: he actually uses -- his own instruction of 2026-10-30 ends "... treat it as
#: a ds. fr". A marker followed by a space and a word does NOT match, so a
#: fixture written as "pf the detector should ..." would make every assertion
#: below vacuous while looking correct.
TEXT = "The detector should execute its helper rather than match source text. pf"


def _queue_line(operation: str = "enqueue", text: str = TEXT) -> str:
    """A mid-turn message as the harness records it: TOP-LEVEL `content`.

    This shape is the whole point. There is no `message` dict, so a reader
    doing `d.get("message") or {}` gets an empty dict and an empty string.
    """
    return json.dumps({"type": "queue-operation", "operation": operation,
                       "content": text, "timestamp": TS})


def _prompt_line(text: str = TEXT) -> str:
    """The ordinary record, for contrast: text under `message.content`."""
    return json.dumps({"type": "user", "timestamp": TS,
                       "message": {"role": "user", "content": text}})


@pytest.fixture
def harvester(tmp_path, monkeypatch):
    mod = _module()
    monkeypatch.setattr(mod, "TRANSCRIPTS", tmp_path)
    return mod, tmp_path


def _write(tmp_path, *lines):
    (tmp_path / "session.jsonl").write_text("\n".join(lines) + "\n",
                                            encoding="utf-8")


class TestAQueuedMarkerIsHarvested:
    def test_the_fixture_is_not_silently_unmarked(self, harvester):
        """ANTI-VACUITY ON THE FIXTURE ITSELF, FIRST.

        Every assertion below rests on `TEXT` actually raising a marker. If
        `MARKER` stopped matching it -- a space after `pf`, a reworded
        sentence -- the harvest would return 0 rows and the tests would read
        as 'the branch is broken' when the fixture was the fault. That is the
        probe-manufactured failure recorded on 2026-11-02.
        """
        mod, _ = harvester
        assert mod.MARKER.search(TEXT), (
            f"the fixture text raises no marker, so every assertion in this "
            f"file would be vacuous: {TEXT!r}")
        assert mod.CANDIDATE_LINE.search(TEXT), "the cheap prefilter rejects it"
        assert not mod.CITATION.search(TEXT), "the fixture reads as a citation"

    def test_a_queued_only_marker_is_harvested(self, harvester):
        """THE DEFECT B102 MEASURED: a mid-turn marker reaching the store."""
        mod, tmp = harvester
        _write(tmp, _queue_line())
        rows = mod.from_chat("2026-11-01")
        assert len(rows) == 1, (
            f"a queue-operation enqueue carrying a marker was not harvested; "
            f"got {rows!r}")
        assert rows[0]["kind"] == "pf"
        assert TEXT[:40] in rows[0]["verbatim"]

    def test_the_role_is_user_so_ruled_is_set(self, harvester):
        """B102's stated reason: `ruled` depends on the role the queue lacks."""
        mod, tmp = harvester
        _write(tmp, _queue_line())
        row = mod.from_chat("2026-11-01")[0]
        assert row["source"] == "chat:user", (
            f"a queued message is his by construction, so the role must be "
            f"`user`; got {row['source']!r}")
        assert row["ruled"] == TS[:10], (
            f"an empty `ruled` is indistinguishable downstream from a message "
            f"he never ruled on; got {row['ruled']!r}")

    def test_only_enqueue_is_read(self, harvester):
        """NEGATIVE CONTROL. `remove` is bookkeeping, not a message.

        B102 records a 4th entry shape, `operation: "remove"` with
        `reason: "absorbed_mid_turn"`. Harvesting it would double-count every
        mid-turn message he sends.
        """
        mod, tmp = harvester
        _write(tmp, _queue_line(operation="remove"))
        assert mod.from_chat("2026-11-01") == [], (
            "a `remove` bookkeeping operation was harvested as a message")

    def test_the_ordinary_prompt_record_still_works(self, harvester):
        """The repair must be ADDITIVE: it adds a record and breaks none."""
        mod, tmp = harvester
        _write(tmp, _prompt_line())
        rows = mod.from_chat("2026-11-01")
        assert len(rows) == 1 and rows[0]["source"] == "chat:user"

    def test_both_records_of_one_message_collapse_to_one_item(self, harvester):
        """A mid-turn message is usually recorded TWICE, queued and absorbed.

        Both carry the same text at the same timestamp, and the anchor is
        keyed on exactly that pair, so the store must not end up with 2 items
        for 1 thing he typed once.
        """
        mod, tmp = harvester
        _write(tmp, _queue_line(), _prompt_line())
        rows = mod.from_chat("2026-11-01")
        anchors = {r["anchor"] for r in rows}
        assert len(anchors) == 1, (
            f"one message typed once produced {len(anchors)} distinct "
            f"anchors: {anchors}")

    def test_the_since_filter_still_bounds_the_harvest(self, harvester):
        """A window later than the fixture must return nothing."""
        mod, tmp = harvester
        _write(tmp, _queue_line())
        assert mod.from_chat("2026-12-01") == []
