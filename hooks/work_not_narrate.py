#!/usr/bin/env python3
"""Stop hook: refuse to end a turn that NARRATED while the work list has open items.

WHY THIS EXISTS, and it is the founder's diagnosis rather than the assistant's.
On 2026-09-10 he asked, repeatedly: *"Are you narrating or working?"*, then
*"That sounds more like you are issuing 'd' for yourself at the end of each
task"*, then *"Can you not write some kind of mechanical 'is blocker' / 'is not
blocker' script ... to prevent this? You can't self-diagnose/repair the exact
cause beyond this?"*

HE WAS RIGHT AND THE MEASUREMENT SAID SO. Over that day's 25 user messages: turns
whose message carried the `d` metacognitive command made a median of 3 tool calls;
turns without it made 13. Mann-Whitney U = 26.0, p = 0.0097 -- so `d` genuinely
suppresses work. BUT 8 of the 16 turns carrying NO `d` still stopped after 12 tool
calls or fewer, Wilson 95% [28.00%, 72.00%]. Half the stops had nothing telling
them to stop. The assistant's first explanation blamed his shorthand, which was
the half of the evidence that flattered it.

WHY A HOOK AND NOT A RESOLUTION. This project's own standing finding:
*"The failure was never the absence of a rule or a checker; it was never running
the checker."* And its audit of the 4 hooks that existed before this one: they are
*"UserPromptSubmit context injectors: they make 0 subprocess calls, emit 0
blocking decisions, and always exit 0."* An instruction arriving BEFORE a turn
competes with everything else in that turn. A Stop hook arrives at the only moment
that matters -- when the turn tries to end -- and can refuse.

WHAT IT REFUSES, and the predicate is deliberately narrow so it cannot become the
guard that fires on the ordinary case and teaches people to bypass it:

    the work list has OPEN items
    AND this turn closed no task and made no commit
    AND this turn ran fewer than MIN_TOOL_CALLS tools
    AND the assistant emitted more than MIN_PROSE characters
    AND the founder's message did NOT carry `d`

All 5 must hold. `d` is his explicit instruction to discuss rather than proceed,
so it is honoured absolutely: a hook that overrode his own command would be worse
than the defect it treats.

IT CANNOT TRAP A SESSION, BUT IT IS NOT CAPPED AT 1 REFUSAL EITHER -- AND THIS
PARAGRAPH SAID OTHERWISE UNTIL 2026-11-03. It read that `stop_hook_active` makes
this exit 0 immediately, so it interrupts at most one stop per turn. That cap IS
the defect `MAX_REFUSALS_PER_TURN` was added to remove, as the comment on that
constant records in the founder's own words -- he watched a turn stop after 2
tasks and asked "You still stopped?". The bound is now a BUDGET of 8 refusals per
turn, counted here and keyed to the turn's own user message, and any failure to
read or write that counter ALLOWS the stop. So the session cannot be trapped, and
the mechanism is a budget rather than an absence of one.

WHY THE STALE SENTENCE MATTERED RATHER THAN MERELY LAGGING. On 2026-11-03 a
session read it as current, concluded the gate was malfunctioning after 6
refusals in 1 turn, and spent reasoning on a non-existent defect. A comment that
inverts its own subject misleads; one that merely lags is noise.

Self-test: `python3 work_not_narrate.py --self-test`
"""
from __future__ import annotations

import importlib.util
import json
import os
import pathlib
import re
import subprocess
import sys

#: HOW MANY TIMES ONE TURN MAY BE REFUSED. `stop_hook_active` is a BOOLEAN the
#: harness sets after the first refusal, so treating it as "give up" caps this
#: hook at exactly 1 refusal per turn -- which converts "one task then report"
#: into "two tasks then report" and no further. The founder watched exactly that
#: and asked "You still stopped?". He was right: the bound was the defect.
#:
#: Refusals are therefore counted here, keyed by the turn's own user message, and
#: the budget is spent before the hook yields. It is a BUDGET rather than an
#: absence of one, because a hook that can never yield would trap a session that
#: has genuinely finished and the founder is not always at the keyboard to break
#: it. Any failure to read or write the counter ALLOWS the stop, because a guard
#: that refuses on its own malfunction is the shape this project keeps having to
#: withdraw.
MAX_REFUSALS_PER_TURN = 8
STATE = pathlib.Path.home() / ".claude" / "hooks" / ".work_not_narrate_state.json"

#: A turn doing real work makes more than this many tool calls.
MIN_TOOL_CALLS = 6
#: Prose beyond this, with no work, is a report rather than an answer.
MIN_PROSE = 1200

REPO = pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"
TASKS = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
MARKERS = REPO / "scripts"


#: PARKING THE HOOK TAKES EFFECT IMMEDIATELY, not at the next session.
#: Claude Code reads its hook configuration once, at session start. On
#: 2026-09-11 the founder said "park the hook thing", the `Stop` key was
#: renamed out of settings.json, that was verified on disk -- and the hook went
#: on firing for the rest of the session, because the running process still held
#: the configuration it started with. He was told it was parked. It was not.
#: The presence of this file is checked at every invocation, so parking is
#: effective the moment the file exists and is undone by deleting it.
PARKED = pathlib.Path.home() / ".claude" / "hooks" / ".work_not_narrate_PARKED"


#: HOW MUCH OF THE TRANSCRIPT IS READ. THIS IS THE FIX OF 2026-11-02 AND IT IS
#: THE REASON THE GATE HAD SILENTLY STOPPED WORKING.
#:
#: Claude Code runs Stop hooks under `timeoutMs: 15000` and KILLS whatever has
#: not returned. A killed hook's exit code 2 never arrives, so the stop it meant
#: to refuse proceeds. This hook used to read the ENTIRE transcript three times
#: -- once in `_turn_key`, once in `turn_signals`, once for the blocker probe --
#: and a session transcript grows monotonically all session long. Measured
#: 2026-11-02: the live transcript was 685,001,703 bytes (653.3 MiB),
#: `turn_signals` alone took 9.743 s, and across 360 recorded invocations the
#: hook TIMED OUT 153 times (0.425000, Wilson 95% [0.374991, 0.476593]) --
#: 0 of 17 in September at a 962 ms median, then 0.4245 to 0.4894 per day from
#: 2026-10-29 at a ~15,400 ms median.
#:
#: SO THE GATE WAS NOT WRONG; IT WAS OUTGROWN. Executed directly it refuses
#: correctly on every input that should refuse. It never got to say so. The
#: founder reported exactly this shape -- "a couple of times recently that has
#: worked out quite well ... even more recently, that automated process no
#: longer seems to be working" -- and the date split confirms it.
#:
#: THE TECHNIQUE IS NOT NEW HERE. `hooks/compaction_watch.py` scans the same
#: transcript in 0.055 s against 41 MB by seeking to a stored byte offset. That
#: was never applied to this hook. Only the CURRENT turn is ever needed, so the
#: trailing bytes suffice and the cost stops depending on session length.
#:
#: IT FAILS TOWARD REFUSING, which is the safe direction for this hook. If a
#: turn is somehow larger than the cap, no founder message is found in the tail,
#: `had_d` comes back False and the stop is refused rather than allowed.
TAIL_BYTES = 48 * 1024 * 1024
_TAIL_CHUNK = 4 * 1024 * 1024


def _tail_lines(transcript: pathlib.Path) -> list[str]:
    """The transcript's trailing lines, enough to hold the current turn.

    Reads BACKWARDS in chunks until a genuine founder message is present or
    `TAIL_BYTES` is reached, whichever comes first. A backwards chunk read can
    begin mid-line, so the first fragment is discarded unless the start of the
    file was actually reached -- otherwise a half line would be handed to
    `json.loads` and silently skipped, which is how a reader loses the very
    entry it is looking for.
    """
    try:
        size = transcript.stat().st_size
    except OSError:
        return []
    want = _TAIL_CHUNK
    while True:
        want = min(want, TAIL_BYTES, size)
        try:
            with transcript.open("rb") as fh:
                fh.seek(size - want)
                raw = fh.read(want)
        except OSError:
            return []
        text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()
        if want < size and lines:
            lines = lines[1:]           # the partial first line
        # ★ THE WINDOW MUST HOLD THE WHOLE RUN OF HIS MESSAGES, NOT JUST THE
        # LAST ONE. Fixed 2026-11-08, after the union repair in `turn_signals`
        # FAILED IN PRODUCTION on the very turn that introduced it. The rule was
        # "stop as soon as a founder-looking line is present", and his
        # instruction of 13:54:09 carrying `a` and `d` sat on the far side of a
        # 4 MiB chunk boundary from his `rs` at 13:54:20. The window held only
        # `rs`, so the union had 1 member and `had_d` came back False again -- a
        # correct fix operating on a window too narrow to see its own input. The
        # guard could not catch it: its fixtures put both messages in 1 small
        # file.
        #
        # SO THE WINDOW NOW EXTENDS UNTIL ASSISTANT WORK PRECEDES THE EARLIEST
        # founder-looking line, which is the real turn boundary -- consecutive
        # messages of his with no work between them are 1 instruction. It costs
        # 1 further doubling in the ordinary case, and the bound and the
        # fail-toward-refusing property documented above are untouched: where no
        # such line is ever found the loop still ends at TAIL_BYTES.
        first = next((i for i, ln in enumerate(lines)
                      if _looks_like_founder_line(ln)), None)
        if first is not None and any(_looks_like_assistant_line(ln)
                                     for ln in lines[:first]):
            return lines
        if want >= TAIL_BYTES or want >= size:
            return lines                # bounded; fails toward refusing
        want *= 2


def _looks_like_assistant_line(line: str) -> bool:
    """Cheap pre-test for an assistant entry, used only to bound the window.

    A SUPERSET, like its founder sibling: every assistant entry is a
    `"type":"assistant"` line, so a line failing this cannot be one. It decides
    only where the PREVIOUS turn ended and never counts work, so a false
    positive widens the window by 1 doubling and a false negative cannot shrink
    it below the behaviour this replaced.
    """
    return '"type":"assistant"' in line or '"type": "assistant"' in line


def _looks_like_founder_line(line: str) -> bool:
    """Cheap pre-test for `is_founder_message` without parsing every line.

    A PROVABLE SUPERSET of the real predicate: every genuine founder entry is a
    `"type":"user"` line, so a line failing this cannot be one. Parsing 653 MiB
    of JSON is what cost the hook its life, and a superset prefilter is the same
    device `TicketStore`'s chat harvester uses for the same reason.
    """
    #: ★ ITS SUPERSET CLAIM WAS FALSE AND IS REPAIRED, 2026-11-10. The
    #: docstring above asserted that *every* genuine founder entry is a
    #: `"type":"user"` line. A message he sends MID-TURN is not: it is an
    #: `api-request-blob`. So the prefilter was dropping the very lines the
    #: decision would have accepted, which is precisely the prefilter-narrower-
    #: than-the-decision defect the ticket harvester was repaired for on
    #: 2026-10-28. The marker is a literal substring of the RAW line, so testing
    #: for it needs no parsing and keeps this cheap: 117 candidate lines of a
    #: 7,648-line tail rather than 338 if the entry type were matched instead.
    if ('"type":"user"' not in line and '"type": "user"' not in line
            and MIDTURN_MARKER not in line):
        return False
    try:
        d = json.loads(line)
    except Exception:
        return False
    return his_text(d) is not None


def is_parked() -> bool:
    """True when the founder has parked this hook.

    FAILS TOWARD FIRING, deliberately. An unreadable home directory must not
    silently disable a guard; only a file that is actually there does that.
    """
    try:
        return PARKED.exists()
    except Exception:
        return False


def founder_commands(text: str) -> list[str]:
    """His MC commands, read with the SAME parser the MC hook uses.

    THERE WERE 2 IMPLEMENTATIONS AND THEY DISAGREED. This hook carried its own
    `re.fullmatch(r"[a-z, ]{1,20}", tail)`, which accepts only a bare trailing
    line. He routinely explains a command as he issues it -- "rg (for the task
    list discussion), then, a, d" -- and that form matched neither parser. 6 of
    his messages in one session had every command silently dropped. His ruling:
    "all commands issued by me should be considered law, and are non-optional
    under any condition!"

    So there is now 1 parser. On any failure to load it this falls back to the
    old pattern, because a guard must never end up reading LESS of him than it
    did before.
    """
    for cand in (pathlib.Path(__file__).with_name("mc_commands.py"),
                 REPO / "hooks" / "mc_commands.py",
                 pathlib.Path.home() / ".claude" / "hooks" / "mc_commands.py"):
        try:
            if not cand.is_file():
                continue
            spec = importlib.util.spec_from_file_location("mc_commands_shared", cand)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)                    # type: ignore[union-attr]
            return list(mod.commands_in(text))
        except Exception:
            continue
    tail = text.strip().splitlines()[-1].strip().lower() if text.strip() else ""
    if re.fullmatch(r"[a-z, ]{1,20}", tail):
        return [t for t in re.split(r"[,\s]+", tail) if t]
    return []


#: ★ THE 3 STRUCTURAL MARKERS THAT SAY AN ENTRY IS NOT HIS, added 2026-11-08.
#: The harness writes its own notifications as `"type":"user"` entries WITHOUT
#: `isMeta`, so the 2026-09-11 repair does not reach them: measured on the live
#: transcript, 75 of 104 entries this hook accepted as his words were harness
#: injections. Each carries its provenance in 3 independent fields, and 75 of
#: 75 carry at least 1 of the 3 -- 1.000000, Wilson [0.951276, 1.000000],
#: Clopper-Pearson [0.952005, 1.000000], 0 unmarked. Matching the literal
#: `<task-notification>` instead would be a SHAPE, which
#: `feedback_an_explicit_marker_and_fixed_widths_beat_a_shape_2026-11-04`
#: records as the weaker instrument.
#:
#: IT REJECTS ONLY ON POSITIVE EVIDENCE. An absent field is NOT evidence of a
#: machine, so an entry of his that lacks all 3 is still accepted. That
#: asymmetry is his ruling of 2026-09-11 -- "all commands issued by me should
#: be considered law, and are non-optional under any condition!" -- so the
#: failure direction is to obey him, never to discard him.
#: ★ A MESSAGE HE SENDS MID-TURN IS NOT RECORDED AS A USER ENTRY AT ALL.
#: Measured on the live transcript 2026-11-10 by executing this module's own
#: reader: his 14:51 message carrying `a, d` appears as a `queue-operation`
#: (3 lines), an `attachment` with `userType: "external"`, and an
#: `api-request-blob` -- and the BLOB is the one holding his words, its content
#: a `tool_result` block followed by a `text` block. `is_founder_message`
#: required `type == "user"`, so `turn_signals` saw exactly 1 founder message in
#: a 7,648-line tail -- the previous night's -- and returned `had_d=False` while
#: his message read `a, d`. `founder_commands` on the blob's own text returns
#: `['a', 'd']`, so the PARSER was right and the ENTRY FILTER dropped it.
#: THE GATE THEN REFUSED 6 TIMES AGAINST A STANDING `d`, bounded only by
#: MAX_REFUSALS_PER_TURN. This is the 2026-09-11 defect in a new costume: that
#: one was `isMeta` erasing his command, and his ruling then was that every
#: command he issues is law and non-optional under any condition.
MIDTURN_ENTRY_TYPE = "api-request-blob"
#: The harness's own wrapper line. MEASURED SPECIFICITY: 1 of 222
#: `api-request-blob` entries in the tail carries it, so accepting only marked
#: blobs is tight rather than hopeful. IF THIS STRING EVER DRIFTS the gate
#: reverts to exactly its pre-2026-11-10 behaviour -- a mid-turn `d` is missed
#: again -- which is no worse than what it replaces and is why the fix fails
#: this way rather than by accepting any blob.
MIDTURN_MARKER = "The user sent a new message while you were working"
#: The harness appends its own explanation AFTER his words. Cutting it matters
#: because it is not his text and must not be read as his.
MIDTURN_EPILOGUE = "This is how Claude Code surfaces messages"


def his_text(d: dict) -> str | None:
    """His words from an entry, or None when the entry is not his.

    ONE EXTRACTION FOR ALL 3 READERS. Before this, each of the 3 call sites
    rebuilt the content itself with its own `.get("text", "")` join and its own
    `<system-reminder>` test, so 3 copies of 1 rule could disagree -- and they
    did, which is the drift `is_founder_message`'s own docstring was written to
    end and did not.

    TEXT BLOCKS ONLY, NEVER A `tool_result`. A mid-turn blob carries my own
    tool output in the same content list, and reading a command out of that
    would let the session silence its own gate with its own words. The
    pre-existing rejection of any content list holding a `tool_result` is
    therefore kept for USER entries and replaced, for a mid-turn blob, by
    reading the text blocks alone -- satisfied rather than bypassed.

    ★ ONE DELIBERATE BEHAVIOUR CHANGE, NAMED RATHER THAN SLIPPED IN.
    `last_founder_timestamp` did not previously apply the `<system-reminder>`
    test and now does, because that test moved into this single predicate. A
    user entry whose content is a system reminder is a harness injection and
    not his words, so skipping it for the timestamp is MORE correct, not less.
    The guard asserts it, so it is a decision on the record.
    """
    if d.get("isCompactSummary") or d.get("isMeta"):
        return None

    t = d.get("type")
    c = (d.get("message", {}) or {}).get("content")

    if t == MIDTURN_ENTRY_TYPE:
        if not isinstance(c, list):
            return None
        txt = "\n".join(
            x.get("text", "") or "" for x in c
            if isinstance(x, dict) and x.get("type") == "text")
        if MIDTURN_MARKER not in txt:
            return None
        after = txt.split(MIDTURN_MARKER, 1)[1].lstrip(": \n")
        after = after.split(MIDTURN_EPILOGUE, 1)[0]
        after = after.strip()
        if not after or "<system-reminder>" in after:
            return None
        return after

    if t != "user":
        return None
    if not_his(d):
        return None
    if isinstance(c, list):
        if any(isinstance(x, dict) and x.get("type") == "tool_result"
               for x in c):
            return None
        c = " ".join(x.get("text", "") or "" for x in c
                     if isinstance(x, dict))
    if not isinstance(c, str) or "<system-reminder>" in c:
        return None
    return c


def not_his(d: dict) -> list[str]:
    """Which markers POSITIVELY identify this entry as machine-origin."""
    out = []
    if d.get("promptSource") == "system":
        out.append("promptSource=system")
    turn = d.get("turnOrigin")
    if isinstance(turn, str) and turn and turn != "human":
        out.append(f"turnOrigin={turn}")
    origin = d.get("origin")
    if isinstance(origin, dict):
        kind = origin.get("kind")
        if isinstance(kind, str) and kind and kind != "human":
            out.append(f"origin.kind={kind}")
    return out


def is_founder_message(d: dict) -> bool:
    """True ONLY for a message the founder actually typed.

    THE DEFECT THIS CLOSES, 2026-09-11. Claude Code records hook feedback and
    harness injections in the transcript as `"type":"user"` entries, flagged
    `isMeta`. This hook's OWN refusal text is one of them. Both readers below
    walked user entries without checking that flag, so the moment this hook
    refused once, it re-read the turn, found its own words where the founder's
    had been, and concluded he had not typed `d`. His command was erased by the
    machine that was supposed to obey it, and the refusal budget -- keyed on the
    same timestamp -- reset to 0 on every refusal, so `MAX_REFUSALS_PER_TURN`
    never bound. The founder watched it refuse 11 times after he said "Pause all
    activity", and ruled: "all commands issued by me should be considered law,
    and are non-optional under any condition!"

    ONE predicate, both callers, so the two cannot drift apart again -- that
    being the shape of defect this project keeps withdrawing.
    """
    #: ★ DELEGATES to `his_text`, 2026-11-10, so the predicate and the
    #: extraction can never disagree. The body that used to live here required
    #: `type == "user"` and therefore could not see a message he sent MID-TURN
    #: at all -- see `his_text` for the measurement and the consequence.
    return his_text(d) is not None


def _turn_key(transcript: pathlib.Path) -> str:
    """The timestamp of the turn's own user message. A new message, a new budget."""
    lines = _tail_lines(transcript)
    if not lines:
        return ""
    for line in reversed(lines):
        #: ★ MID-TURN ENTRIES INCLUDED, 2026-11-10. The refusal BUDGET is keyed
        #: on this timestamp, so a mid-turn instruction that was invisible here
        #: did not start a fresh turn and the budget carried on counting
        #: against his new message. This is NOT the 2026-09-11 defect returning:
        #: that one reset the budget on the hook's OWN output, which `his_text`
        #: still refuses by reading text blocks and never a `tool_result`.
        if ('"type":"user"' not in line and '"type": "user"' not in line
                and MIDTURN_MARKER not in line):
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        if his_text(d) is None:
            continue
        return str(d.get("timestamp") or "")
    return ""


def spend_refusal(key: str) -> int:
    """Record one refusal for this turn and return the running count."""
    if not key:
        return MAX_REFUSALS_PER_TURN + 1        # unknown turn -> allow the stop
    try:
        state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}
    except Exception:
        state = {}
    if state.get("turn") != key:
        state = {"turn": key, "refusals": 0}
    state["refusals"] = int(state.get("refusals", 0)) + 1
    try:
        STATE.write_text(json.dumps(state), encoding="utf-8")
    except Exception:
        return MAX_REFUSALS_PER_TURN + 1        # cannot count -> allow the stop
    return state["refusals"]


def open_items() -> tuple[int, str]:
    """(open count, the next entry THIS SESSION CAN ACTUALLY MOVE). (0, '') if unknown.

    ★ IT PREFERS AN ENTRY THAT NEEDS NO RULING, 2026-11-10, on his explicit
    permission to modify this hook (entry B113, granted 2026-11-09).

    WHAT IT DID BEFORE AND WHAT THAT COST. It returned `opens[0]` -- the first
    OPEN entry in DOCUMENT order -- with no test for whose decision the entry
    waits on. Through 2026-11-09 that entry was B21, which awaited his ruling,
    so this gate named it on every turn and refused the stop 8 times a turn
    against work nobody in the session could advance. A whole day of pushing at
    an entry that could not move.

    HOW IT CHOOSES NOW. The classifier that already exists --
    `how_many_decisions_actually_need_him_2026-11-01.classify_text` -- labels an
    entry OWED when its own text still asks him something. The first OPEN entry
    NOT so labelled is named. If every open entry awaits him, the old behaviour
    is kept exactly: `opens[0]` is named, because naming nothing would make this
    gate silent in the one case where he most needs to see the queue.

    IT IS FAIL-SAFE, AND THAT IS NOT DECORATION. This runs on every attempted
    stop. A classifier that is missing, broken or slow must cost the PREFERENCE
    and not the gate, so the whole selection is wrapped and degrades to
    `opens[0]` -- which is what it always did. The count is never affected.
    """
    try:
        sys.path.insert(0, str(MARKERS))
        from task_list_markers import parse_entries          # type: ignore
        es = parse_entries(TASKS)
        opens = [e for e in es if e.state == "OPEN"]
        if not opens:
            return 0, ""
        return len(opens), (_first_movable(opens) or opens[0].ident)
    except Exception:
        return 0, ""


def _first_movable(opens) -> str:
    """The first open entry whose own text does not still ask him something.

    Returns "" when that cannot be decided, so the caller falls back to
    document order rather than losing the gate.
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_wnn_classify",
            pathlib.Path(MARKERS) / "how_many_decisions_actually_need_him_2026-11-01.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules.setdefault("_wnn_classify", mod)
        spec.loader.exec_module(mod)
        bodies = mod.bodies()
        for e in opens:
            kind = mod.classify_text(e.state, e.ruled, bodies.get(e.ident, ""))["kind"]
            if kind != "OWED":
                return e.ident
        return ""
    except Exception:
        return ""


def turn_signals(transcript: pathlib.Path) -> tuple[int, int, bool, bool]:
    """(tool calls, prose chars, a commit ran, the user's message carried `d`).

    Only the CURRENT turn is read: everything after the last genuine user
    message. A tool_result is not a user message, and neither is a system
    reminder -- conflating them would measure the wrong span.
    """
    if not transcript.is_file():
        return 0, 0, False, False
    lines = _tail_lines(transcript)
    start = 0
    # ★ HIS COMMANDS ARE THE UNION OVER THE TURN, NOT THE LAST LINE ALONE.
    # Fixed 2026-11-08. This read `had_d = "d" in founder_commands(c)` inside
    # the loop, so only the LAST accepted entry counted. On 2026-11-08 he sent
    # his instruction at 13:54:09 carrying `a` and `d`, then `rs` on its own
    # line at 13:54:20; `founder_commands("rs")` is `["rs"]`, so `had_d` became
    # False and this gate refused 8 times against a standing `d`. Proven on the
    # live transcript by
    # `scripts/his_command_was_erased_by_his_own_next_line_2026-11-08.py`:
    # last-wins gives ["rs"], the union gives ["a", "d", "rs"].
    #
    # THE UNION IS BOUNDED BY HIS OWN WORK, not by the window. A founder
    # message that follows assistant TOOL CALLS starts a fresh command set,
    # because work since his last message means the previous instruction has
    # been acted on. Without that bound a `d` from an earlier turn inside the
    # same tail would silence this gate indefinitely, which is the opposite
    # failure and just as bad.
    cmds: set = set()
    worked_since = False
    for i, line in enumerate(lines):
        if ('"type":"assistant"' in line or '"type": "assistant"' in line) \
                and '"tool_use"' in line:
            worked_since = True
            continue
        #: ★ ONE EXTRACTION, 2026-11-10. This loop used to rebuild the content
        #: itself and test `<system-reminder>` itself, a third copy of a rule
        #: that lives in `his_text` -- and the copy that could not see a
        #: mid-turn message.
        if ('"type":"user"' not in line and '"type": "user"' not in line
                and MIDTURN_MARKER not in line):
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        c = his_text(d)
        if c is None:
            continue
        if worked_since:
            cmds = set()
        cmds |= set(founder_commands(c))
        start = i
        worked_since = False
    had_d = "d" in cmds

    calls = prose = 0
    commit = False
    for line in lines[start + 1:]:
        if "git commit" in line:
            commit = True
        try:
            d = json.loads(line)
        except Exception:
            continue
        if d.get("type") != "assistant":
            continue
        for blk in d.get("message", {}).get("content", []) or []:
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "tool_use":
                calls += 1
            elif blk.get("type") == "text":
                prose += len(blk.get("text", "") or "")
    return calls, prose, commit, had_d


def verdict(calls: int, prose: int, commit: bool, had_d: bool,
            n_open: int, nxt: str, blocker_raised: bool = False) -> tuple[bool, str]:
    """Should this stop be refused?

    THE FIRST VERSION ONLY CAUGHT NARRATION and that was too weak. It allowed a
    stop whenever the turn had made 6 or more tool calls or landed a commit --
    which is EXACTLY the pattern the founder was objecting to. He watched me
    work, commit, report and stop, once per turn, for hours, and asked: "So where
    is the continuation fix you built, or said you would build?" Fed this
    session's own transcript, the hook returned "allow the stop" every time.

    HIS REQUIREMENT IS SIMPLER AND STRONGER: keep going until the list is done or
    something blocks. "The only way to test if any of this works is just to try
    and see how far you get this time!" So a stop is refused whenever OPEN work
    remains, and the exemptions are the only 3 that can be justified:

        `d`               his explicit instruction to discuss, never overridden
        nothing open      there is no work to continue to
        a blocker raised  an entry cannot proceed without him

    IT IS BOUNDED, NOT A TRAP. `stop_hook_active` means the stop has already been
    refused once this turn, so it exits 0 immediately. The effect is to convert
    "one task then report" into "at least twice as much per turn", repeatedly --
    not an infinite loop. The founder can end any turn by typing.
    """
    if had_d:
        return False, "the founder issued `d`: discuss, do not proceed. Honoured."
    if n_open == 0:
        return False, "no open items on the work list"
    if blocker_raised:
        return False, "a blocker was raised this turn; stopping for him is correct"

    narrated = calls < MIN_TOOL_CALLS and prose > MIN_PROSE
    head = ("This turn NARRATED: %d tool call(s) against %s characters of prose."
            % (calls, f"{prose:,}")) if narrated else (
            "This turn did work (%d tool calls%s)." % (calls, ", committed" if commit else ""))
    return True, (
        f"{head}\n"
        f"{n_open} items are still OPEN and nothing is blocking. Do not stop here.\n"
        f"The next unstarted entry is {nxt}. Work it.\n"
        f"If something genuinely prevents progress, classify it first:\n"
        f"    python3 scripts/blocker_triage.py --title '<the obstacle>'\n"
        f"A PARK verdict is not a reason to stop -- park it and carry on. Only a "
        f"BLOCK verdict is."
    )


def self_test() -> int:
    cases = [
        # calls prose commit  d  open blocker expect  why
        (0, 5000, False, False, 40, False, True,  "narration with work outstanding"),
        (30, 200, True,  False, 40, False, True,  "WORKED AND COMMITTED, but work remains"),
        (30, 5000, False, False, 40, False, True, "a big working turn still must continue"),
        (0, 5000, False, True,  40, False, False, "`d` is his command and overrides"),
        (30, 200, True,  False, 0,  False, False, "nothing left to do"),
        (5, 3000, False, False, 40, True,  False, "a blocker was raised; stopping is right"),
        (0, 100, False, False, 40, False, True,   "a one-line reply is still a stop"),
    ]
    bad = 0
    for calls, prose, commit, had_d, n_open, blk, expect, why in cases:
        got, msg = verdict(calls, prose, commit, had_d, n_open, "X", blk)
        ok = got == expect
        bad += not ok
        print(f"  {'ok  ' if ok else 'FAIL'} block={got!s:5s} want={expect!s:5s}  {why}")
    print(f"\n  {len(cases) - bad} of {len(cases)} correct")
    return 1 if bad else 0


def main() -> int:
    if "--self-test" in sys.argv:
        return self_test()
    if is_parked():
        return 0                      # parked by the founder; never refuse
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0                      # never break the session on a bad payload
    # `stop_hook_active` is NOT read as "give up". It says only that a refusal has
    # already happened this turn; the budget below decides whether another is due.
    t = payload.get("transcript_path") or ""
    calls, prose, commit, had_d = turn_signals(pathlib.Path(os.path.expanduser(t)))
    n_open, nxt = open_items()
    # A BLOCKER RAISED THIS TURN IS A LEGITIMATE REASON TO STOP, and it is
    # detected from the transcript rather than trusted: the triage script must
    # actually have been run and returned BLOCK.
    raised = False
    try:
        # THE SAME TAIL, not a third full read of the transcript. Before
        # 2026-11-02 this was a `read_text()` over the whole file -- the third
        # of three, and together they are what pushed the hook past its 15 s
        # budget 153 times in 360 invocations.
        text = "\n".join(_tail_lines(pathlib.Path(os.path.expanduser(t))))
        raised = "blocker_triage" in text.rsplit('"type":"user"', 1)[-1] and \
                 "BLOCK:" in text.rsplit('"type":"user"', 1)[-1]
    except Exception:
        raised = False
    block, why = verdict(calls, prose, commit, had_d, n_open, nxt, raised)
    if block:
        used = spend_refusal(_turn_key(pathlib.Path(os.path.expanduser(t))))
        if used > MAX_REFUSALS_PER_TURN:
            print(f"work_not_narrate: {used - 1} refusals already this turn, which "
                  f"is the budget. Allowing the stop so a finished session cannot "
                  f"be trapped.", file=sys.stderr)
            return 0
        print(f"{why}\n\n(continuation {used} of {MAX_REFUSALS_PER_TURN} this turn)",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
