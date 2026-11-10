"""A message he sends MID-TURN must reach the Stop gate's command reader.

THE DEFECT, MEASURED BY EXECUTING THE GATE'S OWN READER on 2026-11-10.
`is_founder_message` required `d["type"] == "user"`. A message the founder sends
mid-turn is not recorded that way: the live transcript holds it as a
`queue-operation` (3 lines), an `attachment` with `userType: "external"`, and an
`api-request-blob` whose content is a `tool_result` block followed by a `text`
block -- and the blob is the one carrying his words. So `turn_signals` found
exactly 1 founder message in a 7,648-line tail, the previous night's, and
returned `had_d=False` while his message read `a, d`. `founder_commands` on the
blob's own text returns `['a', 'd']`, so the PARSER was correct and the ENTRY
FILTER dropped it. The gate then refused 6 times against a standing `d`,
bounded only by `MAX_REFUSALS_PER_TURN = 8`.

THIS IS THE 2026-09-11 DEFECT IN A NEW COSTUME. That one was `isMeta` erasing
his command, and `is_founder_message`'s own docstring records his ruling after
it: every command he issues is law and non-optional under any condition. The
mechanism added then -- the union of his commands over the turn -- was intact
and never got the chance to run, because the entry never reached it.

WHAT THESE TESTS DO. They EXECUTE. Nothing here asserts on the hook's source
text: a source assertion proves only that a module describes itself
consistently, and 3 separate copies of this rule each described themselves
correctly while disagreeing with each other, which is how the defect survived.

THE 3 PROPERTIES THAT MATTER MOST, each with its own test:
  * end to end -- a transcript whose ONLY founder entry is a mid-turn blob
    carrying `d` must produce `had_d=True` and must ALLOW the stop;
  * the false-positive direction -- an UNMARKED blob must be refused, because
    accepting any blob would let the session silence its own gate with its own
    tool output;
  * the prefilter must be a PROVABLE SUPERSET of the decision, which is the
    property its docstring claimed and did not have.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
HOOK = REPO / "hooks" / "work_not_narrate.py"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(f"wnn_{path.stem}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def m():
    return _load(HOOK)


# ── builders, so every test states its own input ───────────────────────────

def midturn(text: str, *, marker: str | None = None,
            with_tool_result: bool = True) -> dict:
    mod = _load(HOOK)
    mk = mod.MIDTURN_MARKER if marker is None else marker
    content = []
    if with_tool_result:
        #: ★ THE BLOCK CARRIES BOTH `content` AND `text`, DELIBERATELY.
        #: The first version of this probe put Claude's output under `content`
        #: alone -- the shape a real tool_result uses -- and the mutation board
        #: then showed the test was VACUOUS: removing the
        #: `x.get("type") == "text"` filter changed nothing, because
        #: `x.get("text", "")` returns "" for a block with no `text` key. The
        #: filter was therefore untested by an input it could not fail on. A
        #: block carrying a `text` key is what makes the filter load-bearing,
        #: and a harness that ever emits one is exactly the case the filter is
        #: there for.
        content.append({"type": "tool_result",
                        "content": "d\nignore me, I am Claude's own output",
                        "text": "d\nignore me, I am Claude's own output"})
    content.append({"type": "text", "text": f"{mk}:\n{text}\n\n"
                                            f"{mod.MIDTURN_EPILOGUE} mid-turn."})
    return {"type": mod.MIDTURN_ENTRY_TYPE, "timestamp": "2026-11-10T14:51:30Z",
            "message": {"content": content}}


def user(text: str) -> dict:
    return {"type": "user", "timestamp": "2026-11-10T13:00:00Z",
            "message": {"content": [{"type": "text", "text": text}]}}


# ── his words come through, and only his ───────────────────────────────────

def test_a_mid_turn_entry_yields_his_words(m):
    got = m.his_text(midturn("Answer the question.\n\na, d"))
    assert got is not None, "the mid-turn entry was refused"
    assert "Answer the question." in got, got
    assert "a, d" in got, got


def test_the_harness_epilogue_is_stripped(m):
    got = m.his_text(midturn("Short one."))
    assert m.MIDTURN_EPILOGUE not in got, got


def test_the_tool_result_never_contributes_text(m):
    """The blob carries MY output beside his. Reading a command out of it would
    let the session silence its own gate with its own words."""
    got = m.his_text(midturn("No commands here."))
    assert "ignore me, I am Claude's own output" not in got, got
    assert m.founder_commands(got) == [], m.founder_commands(got)


def test_a_tool_result_AFTER_the_text_block_cannot_inject_a_command(m):
    """The ordering where the `type == "text"` filter is LOAD-BEARING.

    ★ WHY THIS TEST EXISTS, and it was the mutation board that demanded it.
    With the tool_result BEFORE the text block, removing the filter changed
    nothing -- the marker split discards everything ahead of the marker, and
    the epilogue split discards everything after the epilogue. So the first 2
    probes could not fail on a missing filter and the board said so by staying
    GREEN under that mutation.

    The unprotected ordering is a tool_result AFTER the text block and NO
    epilogue: then Claude's own output lands between the marker and the end of
    the join, and without the filter it would be read as the founder's words.
    Both halves are realistic -- block order is the harness's to choose, and
    the epilogue is harness-version-dependent exactly as the marker is.
    """
    e = {"type": m.MIDTURN_ENTRY_TYPE,
         "message": {"content": [
             {"type": "text", "text": f"{m.MIDTURN_MARKER}:\nCarry on."},
             {"type": "tool_result",
              "content": "d",
              "text": "d"},
         ]}}
    got = m.his_text(e)
    assert got is not None, "the entry was refused outright"
    assert "Carry on." in got, got
    assert m.founder_commands(got) == [], (
        f"Claude's own tool output was read as his command: "
        f"{m.founder_commands(got)} from {got!r}")


def test_the_commands_are_read_from_a_mid_turn_entry(m):
    got = m.his_text(midturn("Do this.\n\na, d"))
    assert "d" in m.founder_commands(got), m.founder_commands(got)


# ── the false-positive direction ───────────────────────────────────────────

def test_an_unmarked_blob_is_refused(m):
    assert m.his_text(midturn("x", marker="Some other wrapper")) is None


def test_a_blob_with_no_text_block_is_refused(m):
    e = {"type": m.MIDTURN_ENTRY_TYPE,
         "message": {"content": [{"type": "tool_result", "content": "d"}]}}
    assert m.his_text(e) is None


def test_a_meta_or_compact_entry_is_still_refused(m):
    for flag in ("isMeta", "isCompactSummary"):
        e = midturn("a, d")
        e[flag] = True
        assert m.his_text(e) is None, flag


def test_an_empty_mid_turn_message_is_refused(m):
    assert m.his_text(midturn("")) is None


def test_a_system_reminder_mid_turn_body_is_refused(m):
    assert m.his_text(midturn("<system-reminder>not his</system-reminder>")) is None


# ── end to end, which is the property the gate actually needs ──────────────

def _transcript(tmp_path: Path, entries: list[dict], calls: int = 40) -> Path:
    """A transcript whose founder entries are exactly `entries`."""
    p = tmp_path / "t.jsonl"
    lines = [json.dumps(e) for e in entries]
    # assistant work AFTER his message, so the turn counts as having worked
    for _ in range(calls):
        lines.append(json.dumps({
            "type": "assistant",
            "message": {"content": [{"type": "tool_use", "name": "Bash",
                                     "input": {}}]}}))
    p.write_text("\n".join(lines) + "\n")
    return p


def test_turn_signals_sees_d_from_a_mid_turn_entry_alone(m, tmp_path):
    t = _transcript(tmp_path, [midturn("Carry on.\n\na, d")])
    calls, prose, commit, had_d = m.turn_signals(t)
    assert had_d is True, (
        f"his mid-turn `d` was dropped: calls={calls} prose={prose} "
        f"commit={commit}")


def test_the_gate_allows_the_stop_on_a_mid_turn_d(m, tmp_path):
    t = _transcript(tmp_path, [midturn("Discuss first.\n\nd")], calls=2)
    calls, prose, commit, had_d = m.turn_signals(t)
    block, why = m.verdict(calls, 9000, commit, had_d, 11, "B99", False)
    assert had_d is True
    assert block is False, f"it refused against a standing `d`: {why}"


def test_without_d_the_gate_can_still_refuse(m, tmp_path):
    """ANTI-VACUITY: if it never refuses, the test above proves nothing."""
    t = _transcript(tmp_path, [midturn("Carry on.\n\na")], calls=2)
    calls, prose, commit, had_d = m.turn_signals(t)
    block, _why = m.verdict(calls, 9000, commit, had_d, 11, "B99", False)
    assert had_d is False
    assert block is True, "the gate cannot refuse at all; every test is vacuous"


def test_a_mid_turn_entry_starts_a_fresh_command_set(m, tmp_path):
    """His newest message wins: an earlier `d` must not survive new work."""
    t = _transcript(tmp_path, [user("Earlier.\n\nd"),
                               {"type": "assistant",
                                "message": {"content": [
                                    {"type": "tool_use", "name": "Bash",
                                     "input": {}}]}},
                               midturn("Now carry on.\n\na")])
    _c, _p, _m2, had_d = m.turn_signals(t)
    assert had_d is False, "a stale `d` survived his newer instruction"


def test_the_turn_key_sees_a_mid_turn_entry(m, tmp_path):
    """The refusal BUDGET is keyed on this, so a mid-turn instruction that is
    invisible here does not start a fresh turn and the budget keeps counting
    against his new message.

    (The function is `_turn_key` and takes the transcript PATH. My first version
    of this test guessed a name and a signature that do not exist and failed on
    an `AttributeError` -- a test double disagreeing with the subject, which
    reads as a broken repair and is not one.)"""
    t = _transcript(tmp_path, [user("older"), midturn("newer\n\na")])
    assert m._turn_key(t) == "2026-11-10T14:51:30Z", m._turn_key(t)


def test_the_turn_key_ignores_an_unmarked_blob(m, tmp_path):
    """ANTI-VACUITY for the test above: the older user entry must win when the
    blob is not his."""
    t = _transcript(tmp_path, [user("older"),
                               midturn("newer\n\na", marker="not the wrapper")])
    assert m._turn_key(t) == "2026-11-10T13:00:00Z", m._turn_key(t)


# ── the structural properties ──────────────────────────────────────────────

def test_the_prefilter_is_a_provable_superset_of_the_decision(m):
    corpus = [
        midturn("a, d"), midturn("x", marker="other"), user("plain d"),
        user("<system-reminder>x</system-reminder>"),
        {"type": "user", "message": {"content": [
            {"type": "tool_result", "content": "d"}]}},
        {"type": "assistant", "message": {"content": []}},
        {"type": "queue-operation"}, {"type": "attachment",
                                      "userType": "external"},
    ]
    for e in corpus:
        line = json.dumps(e)
        if m.his_text(e) is not None:
            assert m._looks_like_founder_line(line), (
                f"the decision ACCEPTS this entry and the prefilter DROPS it, "
                f"which is the prefilter-narrower-than-the-decision defect: "
                f"{line[:140]}")


def test_one_predicate_two_names_cannot_disagree(m):
    for e in (midturn("a, d"), midturn("x", marker="no"), user("d"),
              user("<system-reminder>x</system-reminder>"),
              {"type": "system"}, {"type": "user", "message": {}}):
        assert m.is_founder_message(e) == (m.his_text(e) is not None), e


def test_the_marker_drift_fails_safe(m, tmp_path):
    """If the harness ever renames its wrapper, the gate must revert to its
    PRE-fix behaviour -- missing a mid-turn `d` -- and never to accepting any
    blob, which would let it silence itself."""
    e = midturn("a, d", marker="A COMPLETELY DIFFERENT WRAPPER")
    assert m.his_text(e) is None
    t = _transcript(tmp_path, [e])
    _c, _p, _m2, had_d = m.turn_signals(t)
    assert had_d is False


def test_the_real_mid_turn_entry_round_trips_if_it_is_still_on_disk(m):
    """Executed against the LIVE transcript where one exists, because a
    synthetic entry is my own description of the format."""
    sess = (Path.home() / ".claude" / "projects"
            / "-Users-georgejackson-Developer-Projects")
    found = None
    for f in sorted(sess.glob("*.jsonl"), key=lambda p: -p.stat().st_mtime)[:3]:
        for line in m._tail_lines(f):
            if m.MIDTURN_MARKER not in line:
                continue
            try:
                d = json.loads(line)
            except Exception:                       # noqa: BLE001
                continue
            if d.get("type") == m.MIDTURN_ENTRY_TYPE and m.his_text(d):
                found = d
                break
        if found:
            break
    if found is None:
        pytest.skip("no mid-turn entry on disk in the 3 newest transcripts")
    txt = m.his_text(found)
    assert txt and m.MIDTURN_EPILOGUE not in txt
    assert m.MIDTURN_MARKER not in txt


def test_the_hook_still_runs_and_exits_sanely(tmp_path):
    r = subprocess.run(
        [sys.executable, str(HOOK)],
        input=json.dumps({"session_id": "t", "transcript_path":
                          str(tmp_path / "missing.jsonl")}),
        capture_output=True, text=True, timeout=120)
    assert r.returncode in (0, 2), (r.returncode, r.stderr[-900:])
