"""His commands are the union over the turn, and a harness notice is not him.

THE 2 DEFECTS THIS CLOSES, both found by EXECUTING `turn_signals` against the
live transcript of 2026-11-08 rather than by reading the hook.

1. LAST-WINS. `turn_signals` recomputed `had_d` on every accepted founder entry,
   so only the last one counted. He sent his instruction at 13:54:09 carrying
   `a` and `d`, then `rs` alone at 13:54:20. `founder_commands("rs")` holds no
   `d`, so `had_d` went False and the gate refused 8 times against a standing
   `d`. His ruling of 2026-09-11 is that his commands are law.

2. A HARNESS NOTICE COUNTED AS HIM. A `<task-notification>` user entry carries
   no `isMeta`, so the 2026-09-11 repair does not reach it. 3 sat in that turn's
   own window, each with no commands, so each reset `had_d`; and `_turn_key`
   reads the same predicate, so a background task completing mid-turn moved the
   budget key and handed the gate a fresh `MAX_REFUSALS_PER_TURN`.

WHY THE MARKER IS STRUCTURAL. Measured over a 200 MiB window, 75 of 104 entries
the hook accepted as his words were harness injections, and 75 of 75 of those
carried at least 1 of the 3 provenance fields -- 1.000000, Wilson [0.951276,
1.000000], Clopper-Pearson [0.952005, 1.000000], 0 unmarked. Matching the
literal tag would be a shape instead
(`feedback_an_explicit_marker_and_fixed_widths_beat_a_shape_2026-11-04`).

THESE TESTS CALL THE HOOK. A source-text assertion could not catch either
defect, because every line of the old code described itself correctly --
`execute-do-not-grep`. Producer:
`scripts/his_command_was_erased_by_his_own_next_line_2026-11-08.py`.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "work_not_narrate.py"

HIS_TS = "2026-11-08T13:54:09.000Z"
HIS_TS2 = "2026-11-08T13:54:20.000Z"
BOT_TS = "2026-11-08T13:54:15.000Z"

NOTICE = ("<task-notification>\n<task-id>b91pxs82y</task-id>\n"
          "<status>completed</status>\n</task-notification>")


@pytest.fixture(scope="module")
def hook():
    spec = importlib.util.spec_from_file_location("wnn_union", HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _his(ts: str, text: str) -> dict:
    """An entry exactly as the harness records one he typed."""
    return {"type": "user", "timestamp": ts, "promptSource": "sdk",
            "turnOrigin": "human", "origin": {"kind": "human"},
            "message": {"role": "user", "content": text}}


def _machine(ts: str, text: str = NOTICE, *, marker: str = "all") -> dict:
    """A harness notification. `marker` selects which provenance field it keeps."""
    d = {"type": "user", "timestamp": ts,
         "message": {"role": "user", "content": text}}
    if marker in ("all", "promptSource"):
        d["promptSource"] = "system"
    if marker in ("all", "turnOrigin"):
        d["turnOrigin"] = "task_notification"
    if marker in ("all", "origin"):
        d["origin"] = {"kind": "task-notification"}
    if marker == "none":
        d["promptSource"] = "sdk"
        d["turnOrigin"] = "human"
        d["origin"] = {"kind": "human"}
    return d


def _work(ts: str) -> dict:
    """An assistant turn that made a tool call."""
    return {"type": "assistant", "timestamp": ts,
            "message": {"role": "assistant",
                        "content": [{"type": "tool_use", "name": "Bash",
                                     "id": "x", "input": {}}]}}


def _t(tmp_path: pathlib.Path, *entries: dict) -> pathlib.Path:
    p = tmp_path / "t.jsonl"
    p.write_text("\n".join(json.dumps(e) for e in entries) + "\n", encoding="utf-8")
    return p


class TestTheFixtureIsFaithful:
    """ANTI-VACUITY. If the fixtures stop carrying what they are built to carry,
    every assertion below passes while testing nothing."""

    def test_his_fixture_carries_a_d_command(self, hook):
        assert "d" in hook.founder_commands("a, d")

    def test_the_second_line_carries_no_d(self, hook):
        assert "d" not in hook.founder_commands("rs")

    def test_the_machine_fixture_carries_every_marker(self, hook):
        assert len(hook.not_his(_machine(BOT_TS))) == 3

    @pytest.mark.parametrize("marker", ["promptSource", "turnOrigin", "origin"])
    def test_each_marker_alone_identifies_a_machine(self, hook, marker):
        """Any 1 of the 3 suffices, so losing 2 fields does not reopen this."""
        assert hook.not_his(_machine(BOT_TS, marker=marker))


class TestAHarnessNoticeIsNotHim:
    def test_a_notification_is_rejected(self, hook):
        assert hook.is_founder_message(_machine(BOT_TS)) is False

    def test_it_does_not_erase_his_command(self, hook, tmp_path):
        """THE LIVE CASE: his `a, d`, then 3 notices, then nothing of his."""
        t = _t(tmp_path, _his(HIS_TS, "do the work\n\na, d"),
               _machine("2026-11-08T13:54:11.000Z"),
               _machine("2026-11-08T13:54:12.000Z"),
               _machine("2026-11-08T13:54:13.000Z"))
        assert hook.turn_signals(t)[3] is True

    def test_it_does_not_move_the_refusal_budget_key(self, hook, tmp_path):
        """If the key moves, `refusals` resets and the bound never binds."""
        before = _t(tmp_path, _his(HIS_TS, "carry on"))
        key_before = hook._turn_key(before)
        after = _t(tmp_path, _his(HIS_TS, "carry on"), _machine(BOT_TS))
        assert hook._turn_key(after) == key_before


class TestHisWordsAreNeverRejected:
    """NEGATIVE CONTROL. The rejection must not reach him."""

    def test_his_own_message_is_accepted(self, hook):
        assert hook.is_founder_message(_his(HIS_TS, "a, d")) is True

    def test_an_entry_with_no_provenance_fields_is_accepted(self, hook):
        """An ABSENT field is not evidence of a machine. His ruling of
        2026-09-11 means the failure direction must be to obey him."""
        bare = {"type": "user", "timestamp": HIS_TS,
                "message": {"role": "user", "content": "a, d"}}
        assert hook.not_his(bare) == []
        assert hook.is_founder_message(bare) is True

    def test_a_machine_claiming_human_origin_is_still_accepted(self, hook):
        """Stated so the asymmetry is deliberate rather than accidental."""
        assert hook.is_founder_message(_machine(BOT_TS, marker="none")) is True


class TestTheCommandsAreTheUnionOverTheTurn:
    def test_a_later_line_of_his_does_not_cancel_an_earlier_command(self, hook, tmp_path):
        """THE EXACT FAILING CASE of 2026-11-08 13:54."""
        t = _t(tmp_path, _his(HIS_TS, "do the work\n\na, d"), _his(HIS_TS2, "rs"))
        assert hook.turn_signals(t)[3] is True, "his `d` was cancelled by his own `rs`"

    def test_the_order_does_not_matter(self, hook, tmp_path):
        t = _t(tmp_path, _his(HIS_TS, "rs"), _his(HIS_TS2, "a, d"))
        assert hook.turn_signals(t)[3] is True

    def test_work_between_his_messages_starts_a_fresh_command_set(self, hook, tmp_path):
        """THE BOUND. Without it a `d` from an earlier turn in the same tail
        would silence this gate indefinitely -- the opposite failure."""
        t = _t(tmp_path, _his(HIS_TS, "a, d"), _work(BOT_TS), _his(HIS_TS2, "carry on"))
        assert hook.turn_signals(t)[3] is False, "a spent `d` leaked into the next turn"

    def test_the_turn_start_still_moves_to_his_last_message(self, hook, tmp_path):
        """The union must not change WHERE the turn's work is counted from."""
        t = _t(tmp_path, _his(HIS_TS, "a, d"), _work(BOT_TS), _his(HIS_TS2, "go"),
               _work("2026-11-08T13:54:25.000Z"))
        calls, _, _, _ = hook.turn_signals(t)
        assert calls == 1, f"counted {calls} calls; only the 1 after his last message counts"

    def test_the_hook_still_refuses_when_he_said_nothing(self, hook, tmp_path):
        """IT KEEPS ITS TEETH. The union must not make the gate toothless."""
        t = _t(tmp_path, _his(HIS_TS, "finish the list"))
        assert hook.turn_signals(t)[3] is False
        block, _ = hook.verdict(1, 4000, False, False, 5, "B20", False)
        assert block is True

class TestTheWindowReachesBothOfHisMessages:
    """THE PRODUCTION FAILURE OF 2026-11-08, and the class above could not catch
    it. The union fix was correct and `_tail_lines` stopped at the first chunk
    holding any user-type line, so his `a, d` at 13:54:09 fell outside the
    window and only his `rs` at 13:54:20 was read -- `had_d` False again.

    ★ AND THE FIRST VERSION OF THIS TEST PUT ASSISTANT WORK BETWEEN HIS 2
    MESSAGES, which by the bound in `turn_signals` CORRECTLY cancels the earlier
    command, so it failed for the right reason against a correct fix. What made
    the real pair straddle a 4 MiB boundary was not work between them -- there
    were 11 seconds and nothing else -- but the SIZE of his first message, which
    carried 2 attached files. The fixture reproduces that: a large message of
    his, then his short one, with no work in between.
    """

    @staticmethod
    def _pad(i: int) -> dict:
        return {"type": "assistant", "timestamp": f"2026-11-08T13:4{i % 10}:00.000Z",
                "message": {"role": "assistant",
                            "content": [{"type": "text", "text": "x" * 2000}]}}

    def _fixture(self, tmp_path) -> pathlib.Path:
        big = "do the work on the attached\n\n" + ("context line. " * 400) + "\n\na, d"
        return _t(tmp_path,
                  _work("2026-11-08T13:30:00.000Z"),
                  *[self._pad(i) for i in range(20)],
                  _his(HIS_TS, big),
                  _his(HIS_TS2, "rs"))

    def test_the_probe_really_straddles_a_boundary(self, tmp_path):
        """ANTI-VACUITY, and it is the assertion that matters most here. If his
        2 messages ever fit inside 1 chunk the test below passes for the OLD
        reason and proves nothing."""
        t = self._fixture(tmp_path)
        raw = t.read_text(encoding="utf-8")
        tail_from_his_last = len(raw) - raw.rindex('"rs"')
        assert tail_from_his_last < 2048, "his last message is not inside the first chunk"
        first_msg_at = len(raw) - raw.index("do the work on the attached")
        assert first_msg_at > 2048, (
            "his FIRST message is inside the first chunk too, so no boundary "
            "falls between them and the test below is vacuous")

    def test_both_of_his_messages_are_read_across_a_chunk_boundary(
            self, hook, tmp_path, monkeypatch):
        t = self._fixture(tmp_path)
        monkeypatch.setattr(hook, "_TAIL_CHUNK", 2048)
        assert hook.turn_signals(t)[3] is True, (
            "the window stopped at his last message and lost the one before it")

    def test_work_between_them_still_cancels_the_earlier_command(
            self, hook, tmp_path, monkeypatch):
        """THE BOUND SURVIVES THE WIDER WINDOW. A wider window must not make a
        spent `d` reach forward -- that is the opposite failure."""
        big = "earlier instruction\n\n" + ("context line. " * 400) + "\n\na, d"
        t = _t(tmp_path,
               _work("2026-11-08T13:30:00.000Z"),
               *[self._pad(i) for i in range(20)],
               _his(HIS_TS, big),
               _work("2026-11-08T13:54:15.000Z"),
               _his(HIS_TS2, "rs"))
        monkeypatch.setattr(hook, "_TAIL_CHUNK", 2048)
        assert hook.turn_signals(t)[3] is False, "a spent `d` leaked into the next turn"

    def test_the_window_still_terminates_at_the_cap(self, hook, tmp_path, monkeypatch):
        """The fail-toward-refusing property must survive: a transcript with no
        assistant line before his message must still terminate rather than loop."""
        t = _t(tmp_path, _his(HIS_TS, "carry on"))
        monkeypatch.setattr(hook, "_TAIL_CHUNK", 64)
        monkeypatch.setattr(hook, "TAIL_BYTES", 256)
        assert isinstance(hook._tail_lines(t), list)
