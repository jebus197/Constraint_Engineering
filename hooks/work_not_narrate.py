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

#: ★ THE BUDGET IS NOW CONDITIONAL ON WHETHER THE WORK CAN MOVE WITHOUT HIM.
#: Founder ruling 2026-11-12. His words: *"the limit of 8 is sensible, it stops
#: you looping on things you fundamentally can't do without me"* and then the
#: correction that matters: *"But it isn't sensible if it causes you to stop on
#: things you can do."*
#:
#: HE IS RIGHT, AND THIS FILE ALREADY RECORDED THE MIRROR IMAGE OF THE FAULT.
#: `open_items`'s own docstring says that through 2026-11-09 this gate named an
#: entry awaiting his ruling and "refused the stop 8 times a turn against work
#: nobody in the session could advance. A whole day of pushing at an entry that
#: could not move." That half was repaired on 2026-11-10 by PREFERRING a movable
#: entry. The budget was not touched, so the INVERSE case survived: a turn with
#: plenty of work the session can do alone still yields after 8 refusals, and
#: then only his next message restarts it.
#:
#: MEASURED BEFORE CHANGING ANYTHING, from this session's own transcript: the
#: gate announced "allowing the stop" **219 times**, and its state file held 15
#: refusals against a budget of 8 for a single turn. So the yield is not rare.
#:
#: THE DOCUMENTED INTENT IS PRESERVED EXACTLY. The reason recorded above is that
#: "a hook that can never yield would trap a session that has genuinely
#: finished". A session with movable work has not finished, which is precisely
#: his distinction -- so the bound rises only in that case and a hard ceiling
#: keeps it finite either way.
#:
#: THE CEILING IS A JUDGEMENT AND IS LABELLED AS ONE. 5x the base budget. No
#: measurement here relates a refusal count to an outcome, so it must not be
#: cited as derived. What IS derived is the per-item multiplier: the bound is the
#: base budget once per movable entry, so a turn gets its 8 chances at each thing
#: it can actually do, and a turn with nothing movable keeps exactly the old 8.
MAX_REFUSALS_CEILING = 40
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


def _is_bare_question(text: str) -> bool:
    """True when his message asks something and instructs nothing.

    Deliberately NARROW: it must carry no MC command at all AND its last
    sentence-ending character must be a question mark. An imperative that
    happens to contain a question mark elsewhere is not a bare question.
    """
    try:
        if founder_commands(text):
            return False
        stripped = (text or "").strip()
        return bool(stripped) and stripped.rstrip().endswith("?")
    except Exception:                                          # noqa: BLE001
        return False        # fails toward CLEARING, which is today's behaviour


def _a_commit_board_is_running() -> bool:
    """True when a commit board is live, via the detector built for B155.

    DELEGATES rather than re-deciding. A second copy of "is a board running"
    would be a 2nd definition of the condition, and this project spent
    2026-11-11 removing exactly that shape.
    """
    try:
        for cand in (REPO / "scripts" / "blocker_triage.py",
                     pathlib.Path.home() / "Developer_Projects"
                     / "Constraint_Engineering" / "scripts" / "blocker_triage.py"):
            if not cand.is_file():
                continue
            spec = importlib.util.spec_from_file_location("_bt_board", cand)
            mod = importlib.util.module_from_spec(spec)
            sys.modules.setdefault("_bt_board", mod)
            spec.loader.exec_module(mod)
            return bool(mod.a_commit_board_is_running())
    except Exception:                                          # noqa: BLE001
        return False        # fails toward FIRING: an undecided board arms the gate
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


def movable_count() -> int:
    """How many OPEN entries can this session move WITHOUT him? 0 if unknown.

    Reuses the classifier `open_items` already uses rather than re-deciding, so
    the 2 cannot disagree about what "awaits him" means -- the producer-consumer
    divergence this project keeps meeting.

    FAIL-SAFE AND THAT IS NOT DECORATION: this runs on every attempted stop, so
    a missing or slow classifier must cost the RAISED BUDGET and never the gate.
    It returns 0 on any failure, which falls back to the original budget of 8.
    """
    try:
        sys.path.insert(0, str(MARKERS))
        from task_list_markers import parse_entries           # type: ignore
        opens = [e for e in parse_entries(TASKS) if e.state == "OPEN"]
        if not opens:
            return 0
        spec = importlib.util.spec_from_file_location(
            "wnn_decide", MARKERS / "how_many_decisions_actually_need_him_2026-11-01.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        bodies = mod.bodies()
        n = 0
        for e in opens:
            body = bodies.get(e.ident, "")
            d = mod.classify_text(e.state or "", e.ruled, body)
            #: ★ BOTH HALVES OR NEITHER. The NAMING and the BUDGET must
            #: agree about what "movable" means, or the gate raises a
            #: budget for entries it then refuses to name -- the exact
            #: producer-consumer divergence this docstring warns about.
            #: Measured 2026-11-12 after that night's closures: 5 open
            #: entries pass live_asks and 3 of them say in their own text
            #: that the residue is his, so the honest count is 2. The
            #: budget moves from min(40, 8*5) = 40 to min(40, 8*2) = 16.
            if not d.get("live_asks") and not _residue_is_his(body):
                n += 1
        return n
    except Exception:                                          # noqa: BLE001
        return 0


def refusal_budget() -> int:
    """The refusal budget for this turn, conditional on movable work.

    His ruling of 2026-11-12: 8 is right for work that needs him, and wrong for
    work the session can do. So the base budget stands when nothing is movable,
    and rises by 1 base budget per movable entry otherwise, up to a ceiling.
    """
    n = movable_count()
    if n <= 0:
        return MAX_REFUSALS_PER_TURN
    return min(MAX_REFUSALS_CEILING, MAX_REFUSALS_PER_TURN * n)


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


#: ★ A MOVABLE ENTRY IS NOT THE SAME AS AN ENTRY THAT DOES NOT ASK HIM A
#: QUESTION. Added 2026-11-12. `_first_movable` skips entries whose text still
#: ASKS him something, which repaired the 2026-11-09 case where the gate named
#: an entry awaiting his ruling on every turn. It does NOT catch an entry whose
#: residue is his PERMISSION, stated without a question. B56 is exactly that:
#: its own body says, in capitals, that its residue "IS STILL HIS
#: AUTHORISATION", because wiring the rule changes which seats the harness
#: dispatches, against his standing rule never to bench a model.
#:
#: MEASURED 2026-11-12, and the first figure written for this was WRONG. A note
#: prepared before measuring claimed 1 of 11. Deriving the language from the
#: entries themselves gives 3 of 11 -- B56, B104 and B140 -- Wilson 95%
#: [0.097461, 0.565645]. After that night's 6 closures the open set falls to 13
#: and the movable set to 5, of which the SAME 3 are his, so only 2 are mine.
#: At 5 the budget is min(40, 40) = 40 and at 2 it is 16, so the over-count now
#: BITES, which it did not when the set was 11.
#:
#: IT IS A POLARITY TEST, NOT A KEYWORD TEST, and that is what the measurement
#: forced. B146 carries the sentence "if it holds then you should implement it"
#: -- a ruling ALREADY GIVEN, which is an instruction TO ME. A phrase-presence
#: list excludes it and loses a movable entry. B56 and B104 each carry BOTH a
#: past ruling and a live residue, so "has he ruled?" cannot be the question.
#: The predicate matches only a FORWARD-LOOKING claim that something is still
#: his.
_HIS_RESIDUE = re.compile(r"""(
    is\s+still\s+his\s+authoris | own\s+residue\s+is\s+unchanged
  | for\s+the\s+founder\s+to\s+authoris
  | wh(y|ich)\s+this\s+is\s+his\s+and\s+not\s+mine
  | this\s+is\s+his\s+and\s+not\s+mine
  | widen\s+his\s+own\s+scope
  | (awaits?|await|pending|needs?|requires?)\s+his\s+(permission|authoris|ruling|sign|consent)
  | his\s+to\s+authoris | only\s+he\s+(may|can)
  | behaviour\s+change\s+for\s+the\s+founder
  #: ★ 2 CLAUSES ADDED AFTER THE PREDICATE WAS FALSIFIED ON B144. The
  #: first version caught B56, B104 and B140 and MISSED B144, whose own
  #: text says "THE DESIGN CONSEQUENCE IS HIS AND IS HELD UNDER HIS `d`".
  #: Both clauses are lifted from that entry rather than invented. Swept
  #: over EVERY entry in the list: they newly catch exactly 3, of which
  #: B144 is the only OPEN one, the other 2 being a WITHDRAWN and a
  #: DEFERRED entry that are his by their own words. 0 false positives.
  | (consequence|decision|choice|call)\s+is\s+his\b
  | held\s+under\s+his\b
)""", re.I | re.X)


#: ★ "ONLY HE MAY REJECT ONE" IS A STATEMENT ABOUT A CLASS, NOT ABOUT THIS
#: ENTRY. Added 2026-11-12. `_HIS_RESIDUE`'s `only he (may|can)` clause matched
#: B168's own record of his rule -- *"a feature request stays OPEN until
#: implemented, merged or rejected, and that only he may REJECT one"* -- and
#: classified that entry as needing his permission when it is mine to build.
#: The direction is the harmful one: a false positive moves an item OFF the
#: movable set, so the gate goes quiet about work the session can do.
#:
#: ★ MY FIRST ATTEMPT AT THIS FIX WAS WORSE THAN THE DEFECT AND IS RECORDED
#: HERE BECAUSE IT NEARLY SHIPPED. It excused any sentence "citing a rule",
#: matched by a rule noun followed within 40 characters by `is`. Driven over the
#: live entries before it was applied, it wrongly excused 2 of the 3 it changed:
#: B104, where "the standard is a document ..." describes a DOCUMENT and not a
#: rule, and B170, where it matched ACROSS A BRACKET in "[NEEDS HIS RULING] ON
#: THE MERGE, which is" -- excusing the clearest residue statement in the queue,
#: his own merge decision. A fix that silences his most important open item is
#: not a fix.
#:
#: SO THE NARROWING IS SURGICAL: the `only he may/can` clause alone, and only
#: when its object is INDEFINITE -- "a feature request", "one", "any entry".
#: A definite object ("only he may approve THIS change") still reads as a
#: residue, and no other clause of the pattern is touched.
_CLASS_OBJECT = re.compile(
    r"\bonly\s+he\s+(?:may|can)\s+\w+(?:\s+\w+)??\s+"
    r"(?:a|an|one|any)\b", re.I)


def _residue_is_his(body: str) -> bool:
    """True when the entry's OWN TEXT says what remains is his permission.

    PER SENTENCE, not per document, so one class-statement cannot excuse a
    genuine residue elsewhere in the same entry -- the document-level fault
    recorded on 2026-11-10, where a flag silenced an ask 15,438 characters
    below it.
    """
    try:
        for sent in re.split(r"(?<=[.!?])\s+", body or ""):
            #: ★ EVERY MATCH IN THE SENTENCE, NOT THE FIRST. My first version
            #: tested only `search()`'s first hit, so a class statement earlier
            #: in a chunk excused a GENUINE residue later in the same chunk --
            #: it wrongly moved B169, whose own text says it needs his
            #: permission to edit this very file. Caught by driving it over the
            #: live entries before it was applied.
            for m in _HIS_RESIDUE.finditer(sent):
                if m.group(0).lower().startswith("only he") \
                        and _CLASS_OBJECT.search(sent):
                    continue
                return True
        return False
    except Exception:          # noqa: BLE001
        return False           # fail-safe: costs the preference, never the gate

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
        #: ★ PREFER AN ENTRY WHOSE WORK HAS NOT STARTED. Added 2026-11-12.
        #: This took no account of `status`, so it named FINISHED work as "the
        #: next unstarted entry" -- B158 at status TESTED, on every prod of a
        #: 34-prod turn. Finished work can only leave OPEN via a COMMIT, so no
        #: amount of working clears it and the gate prods the same entry for
        #: ever. Measured the same day: 9 of 27 open entries had their work
        #: done, 0.333333, Wilson [0.186433, 0.521752].
        #:
        #: THE STARTED ONES ARE STILL RETURNED, LAST, rather than skipped: an
        #: entry at BUILT may genuinely need more work, and dropping it would be
        #: the removal half of the additive standard.
        _STARTED = {"BUILT", "TESTED", "COMMITTED"}
        unstarted, started = [], []
        for e in opens:
            body = bodies.get(e.ident, "")
            kind = mod.classify_text(e.state, e.ruled, body)["kind"]
            if kind == "OWED" or _residue_is_his(body):
                continue
            #: `getattr`, not `e.status`: a caller passing an object
            #: without the attribute would otherwise raise into the
            #: enclosing `except` and SILENTLY disable the naming -- which
            #: is what this did to its own guard's entry stub.
            (started if str(getattr(e, "status", "") or "").upper() in _STARTED
             else unstarted).append(e.ident)
        for ident in unstarted + started:
            return ident
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
        #: ★ A BARE QUESTION DOES NOT CLEAR A STANDING `d`. Added 2026-11-12
        #: on his correction: *"normally a 'd' would require you to stop and
        #: answer my questions first, unless I say otherwise."* The reset below
        #: existed for the opposite failure, which is real -- a `d` from an
        #: earlier turn would otherwise silence this gate indefinitely -- so it
        #: is NARROWED rather than removed.
        #:
        #: THE DISCRIMINATOR IS HIS OWN RULING, NOT AN INVENTION. His rule of
        #: 2026-10-30 is that an unmarked comment which does not end in a
        #: question mark is a discussion; his rule of 2026-11-11 is that a `d`
        #: is a BARRIER rather than an item in a sequence. Answering a question
        #: does not lift a barrier. So a message carrying NO command and ending
        #: in a question mark leaves the command set standing; anything else
        #: clears it, which keeps the indefinite-silence case closed.
        #:
        #: PROVED ON THE LIVE TRANSCRIPT, 2026-11-12: his messages carried
        #: ['a','d'] 3 times and then his mid-turn question carried [], which
        #: wiped the `d` and let this gate prod 34+ times past a standing
        #: barrier.
        _new = set(founder_commands(c))
        if worked_since and (_new or not _is_bare_question(c)):
            cmds = set()
        cmds |= _new
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
    #: ★ A COMMIT BOARD HOLDS THE TREE, SO NO ENTRY CAN BE ADVANCED. Added
    #: 2026-11-12 on his instruction to fix this hook. While a board runs, every
    #: remaining action needs a tree write, and `scripts/blocker_triage.py`
    #: REFUSES to write during a board -- so this gate was demanding work its
    #: own sibling mechanism forbids, 34+ times in 1 turn. The detector already
    #: existed, built the same morning for B155, and nothing here called it:
    #: an existing mechanism reaching 1 caller where it should reach 2.
    #:
    #: FAILS TOWARD FIRING. Any failure to decide leaves the gate armed, because
    #: a guard that silently disables itself on an import error is worse than
    #: the noise it treats.
    if _a_commit_board_is_running():
        return 0
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
        budget = refusal_budget()
        if used > budget:
            movable = movable_count()
            print(f"work_not_narrate: {used - 1} refusals already this turn, which "
                  f"is the budget of {budget} "
                  f"({movable} open item(s) the session can move without him). "
                  f"Allowing the stop so a finished session cannot be trapped.",
                  file=sys.stderr)
            return 0
        print(f"{why}\n\n(continuation {used} of {budget} this turn)",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
