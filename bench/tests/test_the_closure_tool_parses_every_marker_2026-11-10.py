"""THE TOOL THAT CLOSES AN ENTRY MUST PARSE EVERY MARKER IN THE LIST.

`scripts/close_an_entry_2026-11-02.py` is the only instrument that closes a
task-list entry across all 3 of its surfaces -- the marker, its tickets, and
its authored detail -- or refuses and changes none. Its own docstring records
4 traps met while writing it. This file pins a 5th, met on 2026-11-10.

WHAT WENT WRONG. The marker pattern spelled out `state`, `status`,
`evidence` and `ruled` IN THAT ORDER and admitted nothing else. `responded:`
was added to the marker vocabulary by entry N1 on 2026-11-09, SEVEN DAYS
after this tool was written, so every entry carrying it became unclosable by
the only tool built to close one.

MEASURED: 7 of 248 markers, 0.028226, Wilson 95% [0.013738, 0.057106],
Clopper-Pearson [0.011422, 0.057289] -- B79, B88, B94, B104, B111, B125 and
B131. All 7 were live, and 4 of them were decisions in his own queue, which
is the worst place for this to bite: the entries most likely to need closing
were the ones the tool could not touch.

AND THE REFUSAL POINTED AT THE WRONG THING. It said "no marker for B79",
which a reader takes to mean the entry is absent. The marker was right there.
A refusal that misnames its own cause costs more than a crash, because it
sends the next reader looking for a missing entry.

A WIDER PATTERN ALONE WOULD HAVE SILENTLY LOST THE FIELD. The rebuild
re-emitted only state, status, evidence and ruled, so closing an entry would
have dropped `responded:` -- the very thing N1 exists to record, deleted by
the act of closing. The fields the tool does not manage are now carried
through in the marker's own order.
"""
import importlib.util
import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TOOL = REPO / "scripts" / "close_an_entry_2026-11-02.py"
LIST = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


@pytest.fixture(scope="module")
def tool():
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("_close_tool", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_close_tool"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def _markers():
    txt = LIST.read_text(encoding="utf-8")
    ids = re.findall(r"<!--\s*task:\s*([A-Za-z0-9]+)\s*\|[^>]*-->", txt)
    raws = re.findall(r"<!--\s*task:\s*[A-Za-z0-9]+\s*\|[^>]*-->", txt)
    return list(zip(ids, raws))


class TestEveryMarkerParses:
    def test_the_list_has_markers_to_parse(self):
        """ANTI-VACUITY: the assertion below passes on an empty list."""
        assert len(_markers()) > 100, (
            f"only {len(_markers())} markers found; the pattern this guard "
            f"uses to enumerate them has probably drifted")

    def test_the_tool_parses_all_of_them(self, tool):
        blind = [i for i, raw in _markers()
                 if tool._marker_re(i).search(raw) is None]
        assert blind == [], (
            f"the closure tool cannot parse {len(blind)} of {len(_markers())} "
            f"markers: {blind}. It is the only instrument that closes an entry "
            f"across all 3 surfaces, so an unparsable marker is an entry that "
            f"cannot be closed -- and in 2026-11-10's case 4 of them were "
            f"decisions in his own queue.")

    def test_a_field_added_later_does_not_blind_it(self, tool):
        """THE PROPERTY, not the instance. `responded:` was the field that
        did it; the next one must not."""
        probe = ("<!-- task: ZZ9 | state: OPEN | status: TESTED | evidence: "
                 "bench/tests/x.py | ruled: 2026-01-01 | responded: 2026-01-02 "
                 "| some_future_field: whatever -->")
        assert tool._marker_re("ZZ9").search(probe) is not None, (
            "a marker carrying an unknown field is unparsable again")


class TestUnmanagedFieldsSurviveAClose:
    def test_responded_is_carried_through(self, tool):
        body = ("state: OPEN | status: TESTED | evidence: old.py "
                "| ruled: 2026-01-01 | responded: 2026-01-02")
        fields = tool._marker_fields(body)
        keys = [k for k, _v in fields]
        assert keys == ["state", "status", "evidence", "ruled", "responded"], keys
        assert dict(fields)["responded"] == "2026-01-02"

    def test_the_field_order_is_preserved(self, tool):
        """He reads this file. Reordering a line he reads is noise."""
        body = "status: TESTED | state: OPEN | responded: 2026-01-02"
        assert [k for k, _v in tool._marker_fields(body)] == [
            "status", "state", "responded"]

    def test_a_real_close_keeps_the_unmanaged_fields(self, tool):
        """END TO END on a DRY RUN against a live entry carrying `responded`,
        so the property is pinned on the real file and not only on a probe."""
        candidates = [i for i, raw in _markers()
                      if "responded:" in raw and "state: DONE" not in raw]
        if not candidates:
            pytest.skip("no live entry carries `responded:` in this checkout")
        rec = tool.close_entry(
            candidates[0], evidence="bench/tests/x.py", resolution="r",
            verification="v", status="COMMITTED", dry_run=True)
        assert rec.get("refused") is None, rec.get("refused")
        assert "responded" in (rec.get("carried_through") or []), (
            f"closing {candidates[0]} would drop `responded:`, which is the "
            f"field entry N1 exists to record: {rec}")
        assert "responded:" in rec["marker"]["now"], rec["marker"]["now"]


class TestTheRefusalNamesItsCause:
    def test_a_truly_absent_entry_says_so(self, tool):
        rec = tool.close_entry("ZZ_NO_SUCH_ENTRY", evidence="bench/tests/x.py",
                               resolution="r", verification="v",
                               status="COMMITTED", dry_run=True)
        assert rec["refused"], "an absent entry was not refused"
        assert "no marker" in rec["refused"], rec["refused"]

    def test_an_already_done_entry_is_refused(self, tool):
        done = [i for i, raw in _markers() if "state: DONE" in raw]
        if not done:
            pytest.skip("no DONE entry in this checkout")
        rec = tool.close_entry(done[0], evidence="bench/tests/x.py",
                               resolution="r", verification="v",
                               status="COMMITTED", dry_run=True)
        assert rec["refused"] and "already DONE" in rec["refused"], rec
