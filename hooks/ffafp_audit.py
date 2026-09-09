#!/usr/bin/env python3
"""UserPromptSubmit hook: say which OBSERVABLE TRACES of FFAFP the last work turn did NOT leave.

WHAT THIS IS, NAMED ACCURATELY
==============================
This is a TRACE DETECTOR. It is not an enforcer, and calling it one would be the same
over-statement this project has already had to withdraw twice (`cdsfl_session_2026-08-25_commissioning`).

FFAFP is Find, Follow, Analyse, Fix, P-pass (docs/REPRODUCING.md, the `f` row). Four of its
five steps happen in reasoning. A hook sees only the tool-call record. So the honest question
is not "did the turn do FFAFP" -- that is unobservable -- but "did the turn leave the traces
that FFAFP would NECESSARILY have left". Those two are not the same claim, and the difference
is the whole of what follows.

The detector is therefore ONE-SIDED. Absence of a trace is real evidence: a turn that changed
a Python file and ran no test, no assert and no STEM tool did not P-pass, whatever its prose
said. Presence of a trace is NOT evidence that the step happened: pytest may have run for an
unrelated reason, and the project has documented tests that passed with the model replaced by
the constant 42 (`execute-do-not-grep`). So this module reports MISSING traces and stays silent
about present ones. Silence here means "nothing detectable is absent", never "FFAFP was done".

WHY REMINDING WAS ALREADY TRIED AND IS NOT ENOUGH
=================================================
`mc_commands.py` has injected the standing `f` and `sy` obligation into EVERY prompt since
2026-08-30, unconditionally, as a hard constraint. It is a good hook and it did not close the
gap, for the reason its own docstring gives: an instruction arriving before the turn competes
with everything else in the turn. Nothing in the loop ever looks BACK and asks whether the
artefact appeared. That is the missing half, and it is the half this file adds.

The two hooks are complementary, not redundant. mc_commands states the obligation ex ante;
this one reports the observable shortfall ex post, on the next prompt, naming files and dates.

THE MEASUREMENT THAT JUSTIFIES BUILDING IT
==========================================
Run `python3 ~/.claude/hooks/ffafp_audit.py --survey <transcript.jsonl>` to reproduce every
number in this docstring. Per `measured-rate-travels-with-its-script`, no figure here is quoted
without the code in this same file that recomputes it.

Measured 2026-09-05 05:50 BST over all 5 transcripts in
~/.claude/projects/-Users-georgejackson-Developer-Projects/ (108.8 MB, 513 turns, of which
221 changed at least 1 non-transient file). The corpus is LIVE and grows as sessions run, so
re-running moves the denominators by a few turns; the shape holds, the last digits do not.

  * 38 of the 110 code-touching turns -- 34.5%, 95% Wilson [26.3%, 43.8%] -- changed a code
    file and then ran NOTHING that could have failed. No pytest, no unittest, no assert, at
    any point after the last edit. That is the P-pass step leaving no trace at all, and it
    is the single largest observable gap.
  * 28 of the 221 work turns -- 12.7% [8.9%, 17.7%] -- ran no STEM tool AND no test in the
    entire turn. The ANALYSE step had no tool output to be evidence.
  * 24 of the 221 -- 10.9% [7.4%, 15.6%] -- edited a file with no read, grep or search of
    any kind beforehand. FOLLOW cannot have happened in the turn that did the FIX.
  * A STEM tool appeared in only 68 of the 221 work turns, 30.8% [25.1%, 37.1%], against a
    standing `sy` constraint that `mc_commands.py` has injected into every single prompt
    since 2026-08-30. Reminding demonstrably did not close this.

VACUITY CHECK. Every signal fires on strictly more than none and strictly fewer than all of
the work turns, so none of them is a constant dressed as a measurement. `--survey` prints
this check on every run and marks any signal reaching 0% or 100% as VACUOUS, and the test
file asserts it rather than merely printing it. That check exists because this project
shipped `boundary_band_sensitivity` as an unconditional constant, vacuous in 41 of 41
archived reports, guarded by a test that read source text instead of calling the function.

THE NAIVE MUTATION DETECTOR, MEASURED AND REJECTED. Treating every `>` as a file write
produced 8693 matches across this corpus, of which 7893 -- 90.8% -- are not file writes:
4213 (48.5%) inside heredoc BODIES, where they are Python or awk source (`>=`, `>0.05`,
`>6s}`, `>127]`); 2765 (31.8%) `/dev/null`; and 915 (10.5%) not path-shaped (`> the`,
`> ",`, `> $(wc`, and the lone quote from `<noreply@anthropic.com>` in a commit message).
Only 800 (9.2%) survive and name a real file. The filters in `bash_mutations` are those
measurements, not a preference.

ONE FIX HERE IS UNEXERCISED, AND SAYING SO IS THE POINT. FOLLOW credits a search for the
edited file's basename OR its stem, so that `grep -rn immune_agents bench/` -- the canonical
"who imports this" search -- counts. Measured: that stem clause changes the FOLLOW grade of
0 of 219 real work turns, because a turn that greps the stem has almost always also read the
full path. It is kept because it makes the rule match its stated definition and introduces
no false positives, but it is NOT supported by evidence that it matters, and a later reader
should not assume it is load-bearing.

COST. Measured end-to-end with /usr/bin/time on the real 46.2 MB transcript: 2.23 s wall
for the cold start, including interpreter launch and the state write, and 0.06 s for the
next run on the same file, which read only the bytes appended since. The cold start is paid
ONCE per session. `--survey`, which walks the same loop over all 108.8 MB
without the per-turn state, reports 3.29 s. An earlier draft of this section quoted 0.20 s
for the 46.2 MB file, which was a bare json.loads probe doing no signal extraction -- two
different operations under one label. Wire the stanza with a timeout of at least 15 s.

REPORT, NEVER BLOCK
===================
Deliberate. A hook that blocked on a heuristic this soft would be switched off within a day,
and a false block on correct work costs more than a missed reminder. Exit status is always 0
and no `decision` field is ever emitted.

FALSE NEGATIVES -- it stays silent and FFAFP did not happen
===========================================================
1. INCIDENTAL CREDIT. `pytest` run for an unrelated file, or `numpy` imported in passing,
   satisfies the ANALYSE trace. The detector cannot tell a check aimed at the change from one
   that merely followed it.
2. A TAUTOLOGICAL CHECK. A test that cannot fail leaves exactly the trace a real one leaves.
   This project has found 3 substitution tautologies that passed with the model replaced by
   42; every one of them would satisfy this detector.
3. WRITES INSIDE A HEREDOC. `python3 - <<'PY'` with `open(path, "w")` in the body mutates a
   file while leaving no shell redirect and no Edit tool call. Such a turn is invisible here
   and is not counted as work at all. This is the largest known hole and it is unavoidable
   without executing the body.
4. FIND is not modelled. The evidence for an issue lives in prose and thinking blocks, which
   carry no structural marker. No attempt is made to detect it; a claim made with no edit and
   no tool call is not examined at all.
5. UNQUOTED-GREP CONFUSION. `grep -n pytest file` credits a test run. The lookbehind rejects
   the quoted form, not the bare one.

FALSE POSITIVES -- it complains and the work was correct
========================================================
1. THE CHECK RAN IN THE NEXT TURN. The common shape "edit now, run the suite after the founder
   answers" is flagged, because at report time the following turn does not exist yet. This is
   the dominant false positive. It is mitigated, not removed, by printing the rate across the
   recent window so one instance does not read as an indictment.
2. FFAFP IS A CYCLE OVER A TASK, NOT A TURN. Following the blast radius on turn N and editing
   on turn N+1 is correct practice and looks like a skipped FOLLOW. Mitigated by carrying
   read paths forward across a window of turns (`FOLLOW_LOOKBACK_TURNS`) and crediting them.
3. VERIFICATION BY A HUMAN. A change the founder inspects directly, or one confirmed by a
   running experiment's own output, leaves no failable check in the record.
4. NOT ALL EDITS OWE A TEST. Documentation-only turns are detected and exempted from the
   ANALYSE and P-PASS checks; files of unrecognised type are exempted for the same reason.
   Transient paths (/tmp, *.log, *.pid) are not treated as work at all.

WHY THE MUTATION DETECTOR IS SHAPED THE WAY IT IS
=================================================
The obvious form -- treat any `>` redirect as a file write -- was built first and MEASURED
against the real transcripts before being thrown away. Numbers in the MEASURED section below.
Two thirds of its matches were noise from `>/dev/null` and from `>=`, `>0.05`, `>6s}` and
`>127]` occurring inside heredoc bodies, which are Python and awk source rather than shell.
Hence two filters: heredoc bodies are excluded from redirect scanning (but NOT from STEM or
test scanning, since an `import sympy` inside a heredoc is exactly the evidence wanted), and
a redirect target must be path-shaped before it counts.

COST
====
Same technique as `compaction_watch.py`: the byte offset reached last time is stored per
session and only new bytes are read, so per-turn cost is proportional to one turn of output.
The one full pass, on first sight of a session, is affordable -- see the MEASURED section.

MUST ALWAYS EXIT 0.
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import re
import sys
import time

STATE_DIR = pathlib.Path(os.environ.get("FFAFP_AUDIT_STATE_DIR")
                        or (pathlib.Path.home() / ".claude" / ".ffafp_audit"))

#: Turns of history over which a read of a path still counts as FOLLOW for a later edit.
#: FFAFP is a cycle over a task, not over a turn: investigating on one turn and editing on
#: the next is correct practice, and flagging it would be a false positive (see above).
FOLLOW_LOOKBACK_TURNS = 20

#: Caps on what one turn stores, so the per-session state file cannot grow without bound
#: -- it is rewritten on every prompt. Measured 2026-09-05: the largest turn in the surveyed
#: corpus serialised to 135443 bytes, with 242 searches and 1109 read_path entries, most of
#: the latter duplicates. Deduplication cannot change a verdict, because FOLLOW is decided by
#: a membership test; the caps sit above the observed maxima and are inert today.
SEARCH_CAP = 400
READ_PATH_CAP = 400

#: Verdicts kept in the state file, so the notice can say whether a shortfall is isolated
#: or habitual. Bounded so the state file cannot grow without limit.
HISTORY_LIMIT = 40

#: Above this size, start from the tail rather than the beginning on first sight of a
#: session. A cold pass of a 46.2 MB transcript measured 2.29 s wall, so this is insurance
#: against a pathological file, not a routine path.
COLD_START_TAIL_BYTES = 32 * 1024 * 1024
COLD_START_MAX_FILE = 200 * 1024 * 1024

# --------------------------------------------------------------------------------------
# Shell text analysis
# --------------------------------------------------------------------------------------

#: Heredoc body. Group 3 is the body itself. Needed because a heredoc body is not shell:
#: it is Python, awk or prose, and `>` inside it is a comparison or a format spec, not a
#: redirect. Measured on one transcript: 1904 of 4219 naive redirect matches were inside
#: heredoc bodies.
_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1(.*?)^\2\s*$", re.S | re.M)

_REDIRECT = re.compile(r">>?\s*(?P<target>[^|&;<>\s][^|&;<>\s]*)")

#: A redirect target must look like a path before it counts. These characters mean the
#: match came from source code or prose -- `{type(e).__name__}`, `> ",`, `> $(wc` -- not
#: from a filename.
_NOT_A_PATH = re.compile(r"[{}()%,`\[\]*?!]")
_PATH_SHAPED = re.compile(r"^[\w.~$/@+-]*(?:/[\w.~$@+-]+|\.[A-Za-z][\w]{0,5})[\w.~$/@+-]*$")

#: Explicit in-place mutations that carry no redirect at all.
_INPLACE = re.compile(r"(?:\bsed\s+-i\b|\|\s*tee\b|\btee\s+[-\w./~$]|\bgit\s+apply\b|\bpatch\s+-p\d)")

#: STEM tools, credited only in an EXECUTION context -- an import, or on a python command
#: line. A bare mention would credit `grep -rn "sympy"`, which is a search, not an analysis.
_STEM_NAMES = r"sympy|z3|scipy|statsmodels|mpmath|uncertainties|numpy|wolframalpha|wolfram|sage|networkx|pint"
_STEM = re.compile(
    r"(?:(?:^|[\s;&|(])(?:import|from)\s+(?P<a>" + _STEM_NAMES + r")\b)"
    r"|(?:\bpython3?\b[^\n]{0,400}?\b(?P<b>" + _STEM_NAMES + r")\b)",
    re.I | re.M,
)

#: A test run. The lookbehind rejects the quoted form (`grep "pytest"`), which is a search.
_TEST = re.compile(r"(?<![\w'\"/-])(?:py\.test|pytest|nose2|tox)\b|(?:-m\s+unittest)\b")

#: A check that could have FAILED. Tests, or an explicit assertion in a one-liner or script.
_ASSERT = re.compile(r"(?<![\w'\"])assert[\s(]")

#: Read or search activity in shell. Used for the FOLLOW trace.
_SEARCH = re.compile(
    r"(?<![\w-])(?:grep|rg|ag|find|cat|head|tail|less|awk|wc|nl|"
    r"sed\s+-n|git\s+(?:log|show|diff|blame|grep))\b"
)

_READ_TOOLS = {"Read", "Grep", "Glob", "NotebookRead",
               "mcp__Desktop_Commander__read_file", "mcp__Desktop_Commander__read_multiple_files",
               "mcp__Desktop_Commander__start_search"}
_EDIT_TOOLS = {"Edit": "file_path", "Write": "file_path", "MultiEdit": "file_path",
               "NotebookEdit": "notebook_path",
               "mcp__Desktop_Commander__write_file": "path",
               "mcp__Desktop_Commander__edit_block": "file_path"}

_DOC_EXT = {".md", ".txt", ".rst", ".markdown"}
_CODE_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".bash", ".zsh", ".toml", ".cfg",
             ".ini", ".yaml", ".yml", ".json", ".sql", ".c", ".h", ".cpp", ".rs", ".go",
             ".rb", ".pl", ".r", ".jl"}


def heredoc_spans(cmd: str):
    """Character ranges of heredoc BODIES in a shell command."""
    return [(m.start(3), m.end(3)) for m in _HEREDOC.finditer(cmd)]


def classify_path(path: str) -> str:
    """One of 'code', 'doc', 'transient', 'other'.

    'transient' exists so that capturing a run's stdout to /tmp is not mistaken for
    changing the system. Measured: /tmp logs were the single most common redirect target
    in both transcripts surveyed, and none of them was a code change.
    """
    p = (path or "").strip().strip("\"'")
    low = p.lower()
    base = os.path.basename(low)
    if (low.startswith("/tmp/") or low.startswith("/private/tmp/") or low.startswith("/var/folders/")
            or "/scratchpad/" in low or low.startswith("/dev/")):
        return "transient"
    ext = os.path.splitext(base)[1]
    if ext in (".log", ".pid", ".tmp", ".lock", ".out", ".err"):
        return "transient"
    if ext in _DOC_EXT:
        return "doc"
    if ext in _CODE_EXT:
        return "code"
    return "other"


def redirect_verdict(target: str, at: int, bodies) -> str:
    """Why one `>` match is, or is not, a file write: 'heredoc', 'devnull', 'shape', 'write'.

    ONE decision point, called by both `bash_mutations` and `--survey`. An earlier draft
    had the rule written out twice and the two copies disagreed: the survey rejected
    /dev/null and the detector did not, and the pipeline only behaved because
    `classify_path` happened to catch it further down. Reading either function on its own
    could not have shown that; running them against each other did (test:
    test_filtered_and_naive_mutation_detectors_disagree_on_real_shapes).
    """
    if any(a <= at < b for a, b in bodies):
        return "heredoc"
    t = (target or "").strip().strip("\"'")
    # An EMPTY target is a quote artefact, not a discard. Measured 2026-09-05: 215 of them
    # in the surveyed corpus, nearly all from the `>` inside `<noreply@anthropic.com>` in a
    # commit message. Folding them into the /dev/null bucket got the write/not-write verdict
    # right while reporting the wrong REASON for it -- the same defect class as the verdict
    # counted under a label the code never emits, 2026-08-30. They belong with the other
    # things that merely do not look like paths.
    if not t or _NOT_A_PATH.search(t) or not _PATH_SHAPED.match(t):
        return "shape"
    if t.startswith("/dev/"):
        return "devnull"
    return "write"


def bash_mutations(cmd: str):
    """Paths this shell command plausibly WROTE, plus in-place edits.

    Conservative by measurement, not by taste: the naive redirect form was built, run
    against the real transcripts, and rejected. See the MEASURED section of the module
    docstring for the rejection rates that produced this shape.
    """
    out = []
    bodies = heredoc_spans(cmd)
    for m in _REDIRECT.finditer(cmd):
        target = m.group("target").strip().strip("\"'")
        if redirect_verdict(target, m.start(), bodies) == "write":
            out.append(target)
    if _INPLACE.search(cmd):
        # The file argument of `sed -i` is not reliably parseable across its many forms
        # (BSD sed needs an extension argument, GNU sed does not), so the mutation is
        # recorded with an unknown path rather than guessed wrongly.
        out.append("<in-place>")
    return out


def bash_signals(cmd: str) -> dict:
    """Traces visible in one shell command.

    STEM and test scanning deliberately include heredoc bodies -- `import sympy` in the
    body of a `python3 - <<'PY'` IS the evidence. Only redirect scanning excludes them.
    """
    return {
        "stem": sorted({(m.group("a") or m.group("b") or "").lower() for m in _STEM.finditer(cmd)} - {""}),
        "test": bool(_TEST.search(cmd)),
        "failable": bool(_TEST.search(cmd) or _ASSERT.search(cmd)),
        "search": bool(_SEARCH.search(cmd)),
        "mutations": bash_mutations(cmd),
    }


def _paths_in(text: str):
    """Path-shaped tokens in arbitrary text, for matching a search against an edited file."""
    out = []
    for tok in re.split(r"[\s;:|&\"'`=]+", text or ""):
        tok = tok.strip().rstrip(",.)")
        if tok and not _NOT_A_PATH.search(tok) and _PATH_SHAPED.match(tok):
            out.append(tok)
    return out


# --------------------------------------------------------------------------------------
# Turn accumulation
# --------------------------------------------------------------------------------------

def _add_read_paths(turn: dict, paths) -> None:
    """Record paths a turn looked at, deduplicated and capped. Order is kept for readability
    of the state file only; nothing depends on it."""
    seen = turn["read_paths"]
    for p in paths:
        if len(seen) >= READ_PATH_CAP:
            return
        if p not in seen:
            seen.append(p)


def new_turn(uuid: str = "", ts: str = "", prompt: str = "") -> dict:
    return {"id": uuid, "ts": ts, "prompt": (prompt or "")[:160], "n_tools": 0,
            "mutations": [], "first_mut": None, "last_mut": None,
            "stem": [], "test_idx": [], "failable_idx": [],
            "searches": [], "read_paths": []}


def record_tool(turn: dict, name: str, inp: dict) -> None:
    """Fold one tool call into a turn's signal accumulator. Order is preserved by index."""
    idx = turn["n_tools"]
    turn["n_tools"] = idx + 1
    inp = inp or {}

    if name in _EDIT_TOOLS:
        p = str(inp.get(_EDIT_TOOLS[name]) or "")
        if classify_path(p) != "transient":
            turn["mutations"].append(p)
            turn["first_mut"] = idx if turn["first_mut"] is None else turn["first_mut"]
            turn["last_mut"] = idx
        return

    if name in _READ_TOOLS:
        blob = " ".join(str(inp.get(k) or "") for k in ("file_path", "path", "pattern", "glob", "paths"))
        if len(turn["searches"]) < SEARCH_CAP:
            turn["searches"].append([idx, blob[:400]])
        _add_read_paths(turn, _paths_in(blob))
        return

    if name == "Bash":
        cmd = str(inp.get("command") or "")
        sig = bash_signals(cmd)
        for s in sig["stem"]:
            if s not in turn["stem"]:
                turn["stem"].append(s)
        if sig["test"]:
            turn["test_idx"].append(idx)
        if sig["failable"]:
            turn["failable_idx"].append(idx)
        if sig["search"]:
            if len(turn["searches"]) < SEARCH_CAP:
                turn["searches"].append([idx, cmd[:400]])
            _add_read_paths(turn, _paths_in(cmd))
        for p in sig["mutations"]:
            if classify_path(p) != "transient":
                turn["mutations"].append(p)
                turn["first_mut"] = idx if turn["first_mut"] is None else turn["first_mut"]
                turn["last_mut"] = idx
        return


def audit(turn: dict, prior_reads=None) -> dict:
    """Which FFAFP traces the turn left, and which it did not.

    `prior_reads` is the set of paths read in recent EARLIER turns, so that investigating
    on one turn and editing on the next is not reported as a skipped FOLLOW.
    """
    prior_reads = prior_reads or set()
    muts = [m for m in turn.get("mutations") or []]
    kinds = {classify_path(m) for m in muts}
    is_work = bool(muts)
    code_touched = "code" in kinds
    doc_only = bool(muts) and kinds <= {"doc"}

    first = turn.get("first_mut")
    last = turn.get("last_mut")

    # FOLLOW. Graded, because "searched nothing at all" and "searched, but not for this"
    # are different failures and only the first is unambiguous.
    bases = set()
    for m in muts:
        if m == "<in-place>":
            continue
        base = os.path.basename(m)
        bases.add(base)
        stem = os.path.splitext(base)[0]
        # A search for the MODULE name is the canonical FOLLOW trace -- "who imports this".
        # The floor of 4 characters stops stems like `run`, `cli` or `x` from matching
        # every unrelated search and making the signal vacuous.
        if len(stem) >= 4:
            bases.add(stem)
    searches = turn.get("searches") or []
    before_text = " ".join(t for i, t in searches if first is None or i < first)
    targeted = any(b and b in before_text for b in bases)
    if not targeted:
        targeted = any(os.path.basename(p) in bases for p in prior_reads)
    searched_before = any(i < first for i, _ in searches) if first is not None else False
    follow = "targeted" if targeted else ("generic" if searched_before else "none")

    analysed = bool(turn.get("stem")) or bool(turn.get("test_idx"))
    verified_after = last is not None and any(i > last for i in (turn.get("failable_idx") or []))

    missing = []
    if is_work and follow == "none":
        missing.append("FOLLOW")
    if is_work and not doc_only and not analysed:
        missing.append("ANALYSE")
    if code_touched and not verified_after:
        missing.append("P-PASS")

    return {"is_work": is_work, "doc_only": doc_only, "code": code_touched,
            "follow": follow, "analysed": analysed, "verified_after": verified_after,
            "stem": list(turn.get("stem") or []), "missing": missing,
            "files": sorted({m for m in muts})[:6], "n_files": len(set(muts)),
            "id": turn.get("id"), "ts": turn.get("ts")}


# --------------------------------------------------------------------------------------
# Transcript scanning
# --------------------------------------------------------------------------------------

def is_human_prompt(entry: dict) -> bool:
    """A founder prompt, which is what starts a turn.

    Tool results arrive as `type: "user"` entries too -- 460 of them against 31 real
    prompts in one measured slice -- so the discriminator is `origin.kind`, not the type.
    Compaction summaries and meta entries are excluded: neither is a turn the assistant took.
    """
    if entry.get("type") != "user" or entry.get("isSidechain"):
        return False
    if entry.get("isMeta") or entry.get("isCompactSummary") is True:
        return False
    origin = entry.get("origin")
    return isinstance(origin, dict) and origin.get("kind") == "human"


def scan(fh, state: dict, on_close=None, on_tool=None) -> dict:
    """Fold new transcript bytes into `state`. Only lines after the stored offset are read.

    `on_close` receives each finished turn's verdict; `on_tool` receives every tool call.
    Both exist so that --survey walks THIS loop rather than a second copy of it: a survey
    that re-implemented the walk could agree with itself while disagreeing with the hook,
    and this project has found 4 defects of exactly that shape.
    """
    fh.seek(state.get("offset", 0))
    for line in fh:
        if '"type"' not in line:
            continue
        try:
            d = json.loads(line)
        except Exception:                                    # noqa: BLE001
            continue                                         # a partially flushed final line
        if d.get("isSidechain"):
            continue
        if is_human_prompt(d):
            close_turn(state, on_close)
            content = (d.get("message") or {}).get("content")
            state["open"] = new_turn(d.get("uuid") or "", d.get("timestamp") or "",
                                     content if isinstance(content, str) else "")
            state["seq"] = int(state.get("seq", 0)) + 1
            continue
        if d.get("type") != "assistant" or state.get("open") is None:
            continue
        for b in (d.get("message") or {}).get("content") or []:
            if isinstance(b, dict) and b.get("type") == "tool_use":
                name, inp = b.get("name") or "", b.get("input") or {}
                if on_tool is not None:
                    on_tool(name, inp)
                record_tool(state["open"], name, inp)
    state["offset"] = fh.tell()
    return state


def close_turn(state: dict, on_close=None) -> None:
    """Move the open turn into history, keeping it if it contained work.

    The verdict is taken BEFORE this turn's own reads are folded into the lookback set,
    so a turn cannot credit its own FOLLOW with a read it made after the edit.
    """
    t = state.get("open")
    if not t:
        return
    if on_close is not None:
        on_close(audit(t, prior_read_paths(state)))
    seq = int(state.get("seq", 0))
    reads = state.setdefault("reads", {})
    for p in t.get("read_paths") or []:
        reads[p] = seq
    for p in list(reads):
        if seq - reads[p] > FOLLOW_LOOKBACK_TURNS:
            del reads[p]
    if t.get("mutations"):
        state["last_work"] = t
    state["open"] = None


def prior_read_paths(state: dict) -> set:
    return set((state.get("reads") or {}).keys())


# --------------------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------------------

_WHY = {
    "FOLLOW": "no read, grep or search of ANY kind ran before the first edit. FOLLOW comes "
              "before FIX: the blast radius is mapped first, or the fix is a guess.",
    "ANALYSE": "no STEM tool and no test ran in the whole turn. The tool output IS the "
               "evidence (`sy` is a standing hard constraint, 2026-08-30); prose is not.",
    "P-PASS": "code changed and NOTHING failable ran afterwards -- no pytest, no assert. "
              "A fix you have not tried to break is a hypothesis, not a fix.",
}


def render(verdict: dict, history: list) -> str:
    """The notice. Short on purpose: a long block every turn becomes wallpaper."""
    if not verdict.get("missing"):
        return ""
    when = (verdict.get("ts") or "")[:19].replace("T", " ") or "the last work turn"
    files = ", ".join(verdict.get("files") or []) or "unnamed files"
    lines = [f"[ffafp] The last work turn ({when}, {verdict.get('n_files', 0)} file(s)) left NO "
             f"OBSERVABLE TRACE of: {', '.join(verdict['missing'])}."]
    for code in verdict["missing"]:
        lines.append(f"  {code}: {_WHY[code]}")
    lines.append(f"  files: {files}")
    if verdict.get("stem"):
        lines.append(f"  present: STEM tools {', '.join(verdict['stem'])}.")
    recent = [h for h in history if h.get("work")]
    if len(recent) >= 4:
        n = len(recent)
        for code in verdict["missing"]:
            k = sum(1 for h in recent if code in (h.get("missing") or []))
            lines.append(f"  {code} missing in {k} of the last {n} work turns.")
    lines.append("  This detects MISSING TRACES, not missing rigour. A check you run in THIS "
                 "turn for last turn's edit is invisible to it, and a note needs no test. If "
                 "the trace is genuinely owed, produce it now rather than asserting it was done.")
    return "\n".join(lines)


# --------------------------------------------------------------------------------------
# Survey mode -- the script that reproduces every number in the docstring
# --------------------------------------------------------------------------------------

def wilson(k: int, n: int, z: float = 1.959963984540054):
    """Wilson score interval for a proportion. Closed form, so the hook needs no SciPy.

    Cross-verified against statsmodels.proportion_confint(method='wilson') and against a
    direct SciPy construction in the test file, per the two-tool rule of 2026-04-21.
    """
    if n <= 0:
        return (0.0, 0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (p, max(0.0, centre - half), min(1.0, centre + half))


def survey(paths) -> dict:
    """Recompute the docstring's figures from real transcripts.

    Also reports each signal's FIRE RATE and flags any signal that fires on every work turn
    or on none of them. A detector whose signal is constant is vacuous, and this project
    shipped exactly that once: `boundary_band_sensitivity` was an unconditional constant,
    vacuous in 41 of 41 archived reports, and its guard never noticed because it read the
    source text instead of calling the function.
    """
    st = {"turns": 0, "work": 0, "code": 0, "doc_only": 0,
          "miss_follow": 0, "miss_analyse": 0, "miss_ppass": 0,
          "follow_targeted": 0, "stem": 0, "test": 0,
          "naive_redirects": 0, "rej_devnull": 0, "rej_heredoc": 0, "rej_shape": 0,
          "kept_redirects": 0, "bash": 0, "parse_seconds": 0.0, "bytes": 0}

    def count_redirects(name, inp):
        if name != "Bash":
            return
        cmd = str((inp or {}).get("command") or "")
        st["bash"] += 1
        bodies = heredoc_spans(cmd)
        for m in _REDIRECT.finditer(cmd):
            st["naive_redirects"] += 1
            verdict = redirect_verdict(m.group("target"), m.start(), bodies)
            st[{"heredoc": "rej_heredoc", "devnull": "rej_devnull",
                "shape": "rej_shape", "write": "kept_redirects"}[verdict]] += 1

    for path in paths:
        p = pathlib.Path(path)
        if not p.is_file():
            continue
        st["bytes"] += p.stat().st_size
        t0 = time.time()
        state = {"offset": 0, "open": None, "seq": 0, "reads": {}}
        history = []
        with p.open("r", errors="ignore") as fh:
            scan(fh, state, on_close=history.append, on_tool=count_redirects)
        if state.get("open"):
            history.append(audit(state["open"], prior_read_paths(state)))
        st["parse_seconds"] += time.time() - t0
        for v in history:
            st["turns"] += 1
            if not v["is_work"]:
                continue
            st["work"] += 1
            st["code"] += 1 if v["code"] else 0
            st["doc_only"] += 1 if v["doc_only"] else 0
            st["follow_targeted"] += 1 if v["follow"] == "targeted" else 0
            st["stem"] += 1 if v["stem"] else 0
            st["test"] += 1 if v["analysed"] else 0
            st["miss_follow"] += 1 if "FOLLOW" in v["missing"] else 0
            st["miss_analyse"] += 1 if "ANALYSE" in v["missing"] else 0
            st["miss_ppass"] += 1 if "P-PASS" in v["missing"] else 0
    return st


def _print_survey(st: dict) -> None:
    w, c = st["work"], st["code"]
    print(f"transcript bytes      : {st['bytes'] / 1e6:.1f} MB, parsed in {st['parse_seconds']:.2f} s")
    print(f"turns                 : {st['turns']}   work turns: {w}   code-touching: {c}   doc-only: {st['doc_only']}")
    print(f"bash calls            : {st['bash']}")
    print("naive `>` redirect detector, rejected by filter:")
    print(f"  matches             : {st['naive_redirects']}")
    for key, label in (("rej_devnull", "/dev/null"), ("rej_heredoc", "inside heredoc body"),
                       ("rej_shape", "not path-shaped"), ("kept_redirects", "KEPT as a write")):
        n = st[key]
        pct = 100.0 * n / st["naive_redirects"] if st["naive_redirects"] else 0.0
        print(f"  {label:<20}: {n} ({pct:.1f}%)")
    print("signal fire rates over work turns (a rate of 0% or 100% would be VACUOUS):")
    for key, label, denom in (("follow_targeted", "FOLLOW targeted", w), ("stem", "STEM tool used", w),
                              ("test", "ANALYSE trace", w), ("miss_follow", "FOLLOW missing", w),
                              ("miss_analyse", "ANALYSE missing", w), ("miss_ppass", "P-PASS missing", c)):
        if not denom:
            print(f"  {label:<18}: n/a")
            continue
        p, lo, hi = wilson(st[key], denom)
        flag = "  <-- VACUOUS" if st[key] in (0, denom) else ""
        print(f"  {label:<18}: {st[key]} of {denom} = {100 * p:.1f}%  95% Wilson [{100 * lo:.1f}%, {100 * hi:.1f}%]{flag}")


# --------------------------------------------------------------------------------------
# Hook entry
# --------------------------------------------------------------------------------------

def find_transcript(session_id: str):
    if not session_id:
        return None
    root = pathlib.Path.home() / ".claude" / "projects"
    try:
        for p in root.glob(f"*/{session_id}.jsonl"):
            return p
    except Exception:                                        # noqa: BLE001
        pass
    return None


def load_state(sf: pathlib.Path) -> dict:
    st = {"offset": 0, "open": None, "seq": 0, "reads": {}, "last_work": None,
          "reported": None, "history": []}
    try:
        if sf.exists():
            st.update(json.loads(sf.read_text()))
    except Exception:                                        # noqa: BLE001
        pass
    return st


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--survey":
        _print_survey(survey(sys.argv[2:]))
        return

    try:
        payload = json.load(sys.stdin)
    except Exception:                                        # noqa: BLE001
        payload = {}
    sid = str(payload.get("session_id") or "").replace("/", "_")[:128]
    event = str(payload.get("hook_event_name") or "UserPromptSubmit")

    tpath = payload.get("transcript_path") or find_transcript(sid)
    if not tpath:
        return
    tpath = pathlib.Path(tpath)
    if not tpath.is_file():
        return

    STATE_DIR.mkdir(parents=True, exist_ok=True)
    sf = STATE_DIR / (sid or "default")
    state = load_state(sf)

    try:
        size = tpath.stat().st_size
    except Exception:                                        # noqa: BLE001
        return
    # A rotated or truncated transcript must not be scanned from a stale offset.
    if state.get("offset", 0) > size:
        state = {"offset": 0, "open": None, "seq": 0, "reads": {}, "last_work": None,
                 "reported": None, "history": []}
    if state.get("offset", 0) == 0 and size > COLD_START_MAX_FILE:
        state["offset"] = size - COLD_START_TAIL_BYTES

    try:
        with tpath.open("r", errors="ignore") as fh:
            if state.get("offset", 0) > 0 and not state.get("aligned"):
                # A cold start from the tail lands mid-line. Discard the partial line and
                # RECORD the realigned offset, because scan() seeks to state["offset"]
                # itself -- an earlier draft did the readline and then had it undone by
                # that seek, which is the kind of defect only running the thing reveals.
                fh.seek(state["offset"])
                fh.readline()
                state["offset"] = fh.tell()
            scan(fh, state)
        state["aligned"] = True
    except Exception:                                        # noqa: BLE001
        pass

    # The turn that just finished is the OPEN one if this prompt's line is not yet written,
    # and the last CLOSED work turn otherwise. Both orders occur, so take whichever is real
    # and de-duplicate on the turn's uuid so the same turn is never reported twice.
    candidate = None
    if state.get("open") and (state["open"].get("mutations")):
        candidate = state["open"]
    elif state.get("last_work"):
        candidate = state["last_work"]

    if candidate:
        verdict = audit(candidate, prior_read_paths(state))
        already = state.get("reported") == verdict.get("id")
        hist = state.get("history") or []
        if not already:
            hist.append({"id": verdict["id"], "ts": verdict["ts"], "work": verdict["is_work"],
                         "missing": verdict["missing"]})
            state["history"] = hist[-HISTORY_LIMIT:]
            state["reported"] = verdict.get("id")
        msg = "" if already else render(verdict, state.get("history") or [])
    else:
        msg = ""

    try:
        sf.write_text(json.dumps(state))
    except Exception:                                        # noqa: BLE001
        pass

    if not msg:
        return
    # Suppressed from the transcript by default: the notice is addressed to the assistant,
    # and a visible block on every work turn becomes wallpaper. FFAFP_AUDIT_VISIBLE=1 surfaces
    # it for the founder when he wants to watch the hook working.
    print(json.dumps({
        "suppressOutput": os.environ.get("FFAFP_AUDIT_VISIBLE", "") != "1",
        "hookSpecificOutput": {"hookEventName": event, "additionalContext": msg},
    }))


if __name__ == "__main__":
    try:
        main()
    except Exception:                                        # noqa: BLE001
        pass
    sys.exit(0)
