#!/usr/bin/env python3
"""Six-model paid panel: does the mathematical model need new mathematics?

Founder-authorised 2026-09-05. Roster: CC1 (the operator, participating with its
own position and synthesising the range), Codex, ChatGPT and DeepSeek on paid
routes, CC2 and Fable on the Max subscription.

NO COMPELLED CONVERGENCE. Each seat returns an independent verdict and its
strongest falsification. Disagreement is preserved as information rather than
smoothed into consensus.

A DISCLOSURE THAT BELONGS IN THE DISPATCHER, NOT ONLY THE BRIEF. The Codex and
ChatGPT seats currently share weights, route and system prompt. The designed
contrast between them -- Codex carrying OpenAI's own agent prompt via `codex
exec`, ChatGPT bare via OpenRouter -- was lost at Run 6 when the Codex seat moved
to OpenRouter to eliminate a 45-to-80-minute-per-round fallback. Recorded in
`project_model_panel_config.md` as "Not yet resolved". Measured 2026-09-05: 5 of
8 differentiating dimensions survive (phenotype, capability fingerprint, delivery
parameters, context budget, temperature); 3 do not (model_id, route, system
prompt). The panel is therefore closer to 4 distinct conditions than 5, and the
brief says so to the seats themselves.
"""
from __future__ import annotations
import concurrent.futures, json, os, sys, threading as _threading, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiment_11_orchestrator import (  # noqa: E402
    call_claude_cli, call_deepseek, call_moonshot, call_openrouter)
import panel_sandbox  # noqa: E402
_PANEL_SANDBOX_CWD: str | None = None

#: seat name -> its OWN sandbox. Added 2026-09-11.
#:
#: THE SEATS SHARED ONE WRITABLE DIRECTORY AND RAN IN IT CONCURRENTLY, which
#: destroys the independence the whole `pr` protocol rests on: "run WITHOUT
#: compelled convergence so each model returns an independent verdict". Measured
#: in round 10, and it is not a theoretical risk -- the fable seat's reply
#: describes the `.zenodo.json` identity tier that the cc2 seat had just
#: invented, and reports "my first (background) run reported 33/640 from a stale
#: .pyc (old repo_paths.py with no declared tier)". Fable reviewed cc2's edited
#: tree, not the tree under review. Agreement between seats was therefore not
#: evidence of anything, and `seat_proposals.diff` mixed both seats' edits with
#: no attribution.
#:
#: COST, MEASURED BEFORE CHANGING IT: 6.53 s and 606 MB per copy on this machine.
#: For a 2-seat round that is 13 s against a 15-to-25-minute panel, which is not
#: a reason to keep a broken control.
_SEAT_SANDBOXES: "dict[str, str]" = {}
_SEAT_SANDBOX_LOCK = _threading.Lock()

#: seat name -> [{attempt, path, built}], every tree the seat ever ran in.
#:
#: FOUNDER RULING (j), 2026-09-17, on the round-17 defect: a seat that timed out
#: retried IN THE SAME SANDBOX the timed-out attempt had been editing for half an
#: hour, so 14 of the 19 files it left had no reply behind them. Each attempt now
#: gets its own copy, and each copy is recorded here and harvested at the end --
#: *"the results do not end up simply being discarded, as has happened in the
#: recent past."*
_SEAT_ATTEMPTS: "dict[str, list]" = {}


def harvest_and_retain(seat_attempts: dict, logs_dir, repo, reap: "bool | None" = None) -> dict:
    """Take the results out of every attempt's copy, and KEEP the copies.

    FOUNDER RULING (j), 2026-09-17: *"Take care when a panel review or an
    experiment completes however that the sandbox does not simply get
    automatically deleted and that the results do not end up simply being
    discarded, as has happened in the recent past."*

    The line this replaces destroyed every copy on the way out. The diffs had
    been harvested, but a diff is not a file: a seat that wrote a new script, a
    data file or a figure lost the artefact itself, and round 15 lost even the
    diff to a decode error. So every attempt's tree is harvested into the run's
    own log directory -- whole files, not only diffs -- and the copies are then
    KEPT unless `PANEL_REAP_SANDBOXES=1` says otherwise.
    `panel_sandbox.release` refuses to remove a copy whose harvest did not
    complete, whatever that variable says.

    Separate from the dispatcher so the other runners the founder named -- *"all
    future panel reviews and experiments (both paid and simulated)"* -- can call
    the same rule instead of writing a second one.
    """
    if reap is None:
        reap = os.environ.get("PANEL_REAP_SANDBOXES", "").strip().lower() in ("1", "true", "yes")
    logs_dir = Path(logs_dir)
    manifest, kept, taken = [], [], 0
    for name, attempts in seat_attempts.items():
        for a in attempts:
            if not os.path.isdir(a["path"]):
                manifest.append({"seat": name, "attempt": a["attempt"],
                                 "sandbox": a["path"], "exists": False,
                                 "harvested": False,
                                 "note": "the copy was already gone"})
                continue
            m = panel_sandbox.release(
                Path(a["path"]), Path(repo),
                logs_dir / "sandbox_harvest" / name / f"attempt-{a['attempt']}",
                reap=reap)
            m.update({"seat": name, "attempt": a["attempt"]})
            manifest.append(m)
            taken += m.get("bytes", 0)
            if m.get("exists"):
                kept.append(a["path"])
    out = {"reap_requested": reap, "kept": kept, "harvest_bytes": taken,
           "per_attempt": manifest}
    logs_dir.mkdir(parents=True, exist_ok=True)
    (logs_dir / "sandbox_manifest.json").write_text(json.dumps(out, indent=2),
                                                    encoding="utf-8")
    print(f"    harvested {taken} byte(s) of seat-written files into "
          f"{logs_dir / 'sandbox_harvest'}")
    if kept:
        print(f"    {len(kept)} sandbox copy/copies KEPT, not deleted. They are listed in "
              f"{logs_dir / 'sandbox_manifest.json'}.")
        print("    To remove them when you are finished with them: re-run with "
              f"PANEL_REAP_SANDBOXES=1, or rm -rf {' '.join(kept)}")
    return out


def fresh_sandbox_for_attempt(name: str, attempt: int) -> "str | None":
    """The working directory attempt `attempt` of seat `name` runs in.

    Attempt 1 keeps the copy built before dispatch, so a round with no retry
    costs nothing extra (a copy is 6.53 s and 606 MB, measured). Every later
    attempt gets a NEW copy of the canonical tree, so a retry starts from the
    repository rather than from the wreckage of the attempt that timed out.
    """
    with _SEAT_SANDBOX_LOCK:
        seen = _SEAT_ATTEMPTS.setdefault(name, [])
        if attempt <= 1 and _SEAT_SANDBOXES.get(name):
            path = _SEAT_SANDBOXES[name]
            if not any(a["attempt"] == attempt for a in seen):
                seen.append({"attempt": attempt, "path": path, "built": False})
            set_panel_cwd(path)
            return path
    path = str(panel_sandbox.build(_REPO, blind_of=_BLIND_OF, blind_text=_blind_text_for(_BLIND_OF)))  # outside the lock: 6.53 s
    with _SEAT_SANDBOX_LOCK:
        _SEAT_SANDBOXES[name] = path
        _SEAT_ATTEMPTS.setdefault(name, []).append(
            {"attempt": attempt, "path": path, "built": True})
    set_panel_cwd(path)
    print(f"    {name} attempt {attempt} confined to a FRESH copy: {path}", flush=True)
    return path


def confine_this_thread(name: str) -> "str | None":
    """Set THIS thread's panel cwd to `name`'s own sandbox, and return it.

    EXTRACTED 2026-09-11 so the guard can CALL it. `test_panel_sandbox_2026-09-07`
    asserted that the literal string `set_panel_cwd(_PANEL_SANDBOX_CWD)` appeared
    in `dispatch`'s source. Giving each seat its OWN sandbox renamed the argument
    and the test went red while the behaviour was correct and stronger than
    before -- the third source-text guard broken by a correct refactor in a
    single day. `execute-do-not-grep`: a test that reads source proves only that
    the source describes itself.

    THE THREAD PART IS THE WHOLE POINT and is not incidental. `_PANEL_CWD_TLS` is
    a `threading.local()` and this runs inside a `ThreadPoolExecutor`, so a value
    set on the main thread is invisible here. The first attempt at the founder's
    confinement ruling failed silently for exactly that reason: main logged
    "seats confined to a copy", every worker passed cwd=None, and the seats ran
    in the live repository.
    """
    cwd = _SEAT_SANDBOXES.get(name) or _PANEL_SANDBOX_CWD
    if cwd:
        set_panel_cwd(cwd)
    return cwd
from experiment_11_orchestrator import set_panel_cwd  # noqa: E402
from experiment_11_orchestrator import accept_reply_or_work  # noqa: E402
from experiment_11_orchestrator import set_tool_log_sink  # noqa: E402
from openrouter_tools import (  # noqa: E402
    TOOL_SPECS as _VERIFY_TOOLS, call_openrouter_with_tools)
import build_experiment_tools as _ACCESS_TOOLS  # noqa: E402

#: THE SEATS COULD NOT READ THE THING THEY WERE REVIEWING. Found 2026-09-20,
#: mid-round, by reading a seat's own reply rather than its summary.
#:
#: The panel gave its seats 5 tools -- sympy_verify, z3_verify, pytest_run,
#: ruff_check, mypy_check -- and NOT ONE of them reads a file or runs a Python
#: script. The brief for that round asked seats to read the revised model's
#: specification, execute `CDSFL_revised_core.py`, and search `bench/logs/` for
#: paired repair states. All 3 were structurally impossible, and the seats spent
#: their budget discovering it: cx ran `pytest_run` against 4 standalone scripts
#: and got `no tests ran` 4 times, then reported "Most substantive package
#: claims remain UNVERIFIED in this seat". 2 of 3 paid seats hit the iteration
#: cap having executed almost nothing.
#:
#: WHY IT WENT UNNOTICED. Every seat was verified before dispatch to MAKE tool
#: calls -- 8 of 8 for DeepSeek via OpenRouter, 1 of 1 for Kimi, and so on --
#: and not one check asked WHICH tools. A seat calling a tool it cannot use is
#: still calling a tool, so the pre-flight passed while the capability it was
#: standing in for was absent. The CLI seats were unaffected: cc2 and fable
#: reach the tree through Bash, which is why the archive shows them at 2,754 and
#: 2,530 tool calls against cx's 48.
#:
#: THE UNION, because both halves are load-bearing: the symbolic verifiers that
#: make a claim decidable, and the access tools that let a seat reach the
#: artefact under review. `pytest_run` and `run_pytest` are near-duplicates and
#: both are kept -- a seat picking either gets a working tool, which is the
#: opposite of the failure above.
TOOL_SPECS = list(_VERIFY_TOOLS) + list(_ACCESS_TOOLS.TOOL_SPECS)

_REPO = Path(__file__).resolve().parent.parent
_env = _REPO / ".env"
if _env.is_file():
    for _l in _env.read_text().splitlines():
        _l = _l.strip()
        if not _l or _l.startswith("#") or "=" not in _l:
            continue
        if _l.startswith("export "):
            _l = _l[len("export "):].lstrip()
        _k, _, _v = _l.partition("=")
        os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))

# THE MODULE MUST BE IMPORTABLE. Task A22, 2026-09-11.
#
# This block used to run at IMPORT: it read `sys.argv[1]`, required a BRIEF.md
# beside it, and raised SystemExit(2) when either was missing. So NOTHING could
# import this file -- not a test wanting to inspect one function, not a tool,
# not a reader. The guard for the per-seat sandboxes had to set `sys.argv` and
# `PANEL_BRIEF_UNCHECKED=1` around its import to get in, which is a test working
# around the code rather than testing it.
#
# IT IS THE SAME IMPORT-TIME-SIDE-EFFECT CLASS as `compose_all_2026-08-23.py`,
# fixed under task A2 the day before: a module-level read of a file that need not
# exist, taking down every importer with it. It is also why `--help` on this
# dispatcher printed `no BRIEF.md in .../bench/logs/--help` instead of usage.
#
# WHAT IS PRESERVED EXACTLY: running it still requires the argument and the
# brief, still exits 2, and still prints the same messages. `resolve_brief()` is
# called from `main()`, so the behaviour of an actual run is unchanged -- and
# `bench/tests/test_panel_dispatcher_imports_2026-09-11.py` holds both halves.
LOGS = None
BRIEF = None
PROMPT = ""


def _logs_dir():
    """The run's log directory, or a legible error if the brief is unresolved.

    A22 MOVED THE BINDING OUT OF IMPORT TIME, and this is the price: `LOGS` is
    None until `resolve_brief()` runs, so code that used to find it already
    bound now gets None. Reached through a bare `LOGS / name` that produced
    `TypeError: unsupported operand type(s) for /: 'NoneType' and 'str'` -- a
    message that says nothing about what to do. Two tests found it within the
    hour; the diagnostic is the fix, not the binding.
    """
    if LOGS is None:
        raise RuntimeError(
            "the run directory is not resolved yet: call resolve_brief() "
            "(main() does) before using anything that reads the log directory")
    return LOGS


def resolve_brief(argv=None) -> None:
    """Bind LOGS, BRIEF and PROMPT from the command line. Called by main()."""
    global LOGS, BRIEF, PROMPT
    argv = list(sys.argv if argv is None else argv)
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print("usage: confer_maths_panel_2026-09-05.py <log-dir-name>",
              file=sys.stderr)
        raise SystemExit(0 if len(argv) > 1 else 2)
    LOGS = _REPO / "bench" / "logs" / argv[1]
    BRIEF = LOGS / "BRIEF.md"
    if not BRIEF.is_file():
        print(f"no BRIEF.md in {LOGS}", file=sys.stderr)
        raise SystemExit(2)
    PROMPT = BRIEF.read_text(encoding="utf-8")

# `import json as _json` STOOD HERE and is removed rather than left dead: the
# gate below was its only consumer, and it no longer parses the ledger itself.
# Measured before removing: 0 references to `_json` anywhere in this file and 0
# modules importing it from here. `json` is already imported plainly on line 24
# for anything that needs it, so no capability is lost.
import os as _os
from pathlib import Path as _Path
_ONLY = _os.environ.get("PANEL_ONLY", "")
#: Rounds this dispatch must be BLIND to, comma-separated. Panel review runs in
#: star topology -- each seat answers blind, then a joint round follows once the
#: blind replies are in -- and a sandbox is a whole-repository clone, so a blind
#: round stops being blind the moment an earlier round's replies are harvested
#: into the tree. Recorded as unfixed on 2026-10-03 ("ROUND 2 WAS NOT BLIND WITH
#: RESPECT TO ROUND 1"); it recurred on 2026-10-05 and is now purged and VERIFIED
#: by `panel_sandbox.build(..., blind_of=...)`, which refuses the sandbox rather
#: than returning one that merely looks blind.
_BLIND_OF = tuple(x for x in _os.environ.get("PANEL_BLIND_OF", "").split(",") if x.strip())

#: THE JOINT ROUND'S DECLARED PARENTS. A joint round's brief is NOT byte-identical to
#: the blind briefs -- it carries their replies -- so it cannot be grouped by brief
#: hash and must name what it follows. Enforced in `_refuse_if_topology_is_skipped`.
_JOINT_OF = tuple(x for x in _os.environ.get("PANEL_JOINT_OF", "").split(",") if x.strip())


def _blind_text_for(rounds):
    """Distinctive phrases from the named rounds' replies.

    A PATH PURGE ALONE IS NOT BLINDNESS, and assuming it was is the error this
    exists to stop. Measured 2026-10-05: after purging every path containing the
    round id, the sandbox still carried the other seat's whole verdict through
    `Panel_FULL_RECORD_Fingerprint_Ladder_2026-10-05.md` and
    `The_Blockers_Were_Shown_As_Settled_2026-10-05.md`, neither of which is named
    for the round. The purge reported 0 survivors and the seat could read
    everything. Phrases are taken from the replies themselves so the check cannot
    drift from what was actually said.
    """
    out = []
    for r in rounds:
        d = _REPO / "bench" / "logs" / str(r).strip()
        if d.is_dir():
            out.extend(panel_sandbox.round_fingerprints(d))
    return tuple(out)
# 6 SEATS, AND GEMINI IS BACK (founder ruling, 2026-09-20). Verbatim: *"There is
# no reason why you shouldn't include Gemini! Gemini has traditionally been
# present for most of the project. If you dropped it in a runner for the
# experiments, or in a panel review process, then that is clearly an error on
# your part."* It was absent from this table while the project instructions
# listed it, so the instructions described a panel that had not been running.
#
# THE 2 OPENAI SEATS NO LONGER SHARE A MODEL. Both were `openai/gpt-5.5`: 1
# architecture wearing 2 labels, 4 architectures reported as 5. His ruling,
# verbatim: *"we just run with a normal recent version of ChatGPT and with a
# separate instance of Codex 5.3 from this point on, until project completion. We
# mark the potential confound, state our reasons for this choice, and ensure that
# this choice stick through all future paid panel reviews and experiments."*
#
# THE CONFOUND, MARKED AS HE ASKED. Codex 5.3 and ChatGPT 5.5 are different
# MODELS, not the same weights under different operating conditions, so a
# difference between these 2 seats cannot be attributed to conditions alone. The
# reason for accepting it: the alternative was 2 identical seats, which measure
# nothing, and a system-prompt injection scheme whose premise runway 0C.59
# retracted on 2026-09-02.
_ALL = [
    ("cx",    "openai/gpt-5.3-codex",          "openrouter"),  # PAID -- Codex, a distinct model
    ("cgpt",  "openai/gpt-5.5",                "openrouter"),  # PAID -- ChatGPT mainline
    ("ge",    "google/gemini-3.1-pro-preview", "openrouter"),  # PAID -- RESTORED 2026-09-20
    ("ds",    "deepseek/deepseek-v4-pro",      "openrouter"),  # PAID -- MOVED OFF
    #   DeepSeek's own API 2026-09-20, keeping the SAME model. Founder: "No model
    #   gets a free pass on tool use ... Including Kimi and Deepseek?" Measured,
    #   and it is the SERVING and not the model: deepseek-v4-pro on DeepSeek's
    #   direct API made a structured tool call in 0 of 8 replies, Wilson
    #   [0.00%, 32.44%]; the identical model through OpenRouter made one in 8 of
    #   8, Wilson [67.56%, 100.00%]. Fisher exact p = 1.554002e-04, scipy and an
    #   mpmath hypergeometric tail agreeing exactly, chi-square with Yates
    #   p = 4.652582e-04.
    #
    #   THE DIRECT API REFUSES TO BE COMPELLED: tool_choice="required" returns
    #   400 "Thinking mode does not support this tool_choice" on both
    #   deepseek-v4-pro and deepseek-flash. Through OpenRouter the same model
    #   honours both "auto" and "required".
    #
    #   WHAT THE SEAT WAS DOING INSTEAD, and it is worse than not logging: asked
    #   to use a tool it either answered from reasoning in LaTeX, or emitted the
    #   literal text `<run_python> ... </run_python>` as its FINAL ANSWER --
    #   unexecuted code presented as a result. That is why the archive shows 0
    #   recorded tool calls across 8 DeepSeek replies. Not a logging hole.
    #
    #   The orchestrator's ModelConfig already carried this as the SECONDARY
    #   route; this promotes it to primary for the panel seat only.
    ("cc2",   "opus",                          "claude_cli"),  # Max, free
    ("fable", "fable",                         "claude_cli"),  # Max, free
    ("kimi",  "kimi-k3",                       "moonshot"),    # PAID -- the founder's
    #   OWN Moonshot credits, NOT OpenRouter. Founder, 2026-09-20: "Why not use
    #   the Kimi K3 credits I already paid for rather than burn more of my
    #   OpenAI credits?" The repository already reached Kimi at
    #   `moonshotai/kimi-k3` through OpenRouter, which is a proven route and the
    #   wrong one: it spends OpenRouter credit on a model whose credits are
    #   already bought. Direct endpoint measured, not assumed -- api.moonshot.ai
    #   authenticates and serves kimi-k3; api.moonshot.cn returns 401.
    #
    #   ITS FINDINGS ARE QUARANTINED, on the founder's instruction, because the
    #   seat is an untested quantity in this harness. See QUARANTINED_SEATS.
    #
    #   IT IS THE ONLY NON-DETERMINISTIC SEAT: kimi-k3 refuses any temperature
    #   but 1, measured as `400 invalid temperature: only 1 is allowed for this
    #   model`, while every other seat runs pinned at 0.0.
]

#: Seats whose findings are held separately rather than mixed into the panel's
#: result. Founder, 2026-09-20, adding Kimi: *"But quarantine its findings
#: specifically, as it is clearly an untested quantity."* Quarantine is not
#: exclusion -- the seat runs, its reply is recorded in full, and its findings
#: are reported -- it means they are not counted as corroboration for anything
#: another seat found, because an untested instrument agreeing with a tested one
#: is not independent evidence until the instrument itself has a track record.
QUARANTINED_SEATS = {"kimi"}

#: RAISED FROM 10 TO 16 on 2026-09-20, after measuring the first round rather
#: than guessing. 3 of the 4 paid seats hit the cap: cx at 10 iterations with
#: `max_iterations_harvested`, ge at 10, ds at 10; only cgpt finished, in 5.
#: And they hit it having executed almost nothing useful, because the seats had
#: no tool that reads a file or runs a script -- cx spent 4 iterations running
#: `pytest_run` against standalone scripts and got `no tests ran` each time.
#:
#: The cap is raised WITH the tool fix, not instead of it. A seat that can read
#: the artefact needs more turns to do real work; a seat that cannot needs none.
#:
#: 16 IS COUNTED, NOT ROUNDED. What this brief asks of a seat: 3 turns to read
#: the specification, 1 to run the reference core, 3 for the package's own check
#: scripts, 5 for the symbolic and z3 checks of the derivations it is asked to
#: falsify, 2 for the appendix and the live gate, and 2 to search the archive for
#: paired repair states. Cost scales worse than linearly because the whole
#: history is re-sent each turn: measured against live OpenRouter pricing, the
#: worst case across the 4 paid seats is 1.64 pounds at 10, 3.56 at 16 and 5.23
#: at 20. 16 buys the work; 20 buys 4 spare turns for 1.67 pounds.
PANEL_TOOL_ITERATIONS = 16
# PANEL_ONLY re-dispatches a SUBSET, so a briefing defect that broke 2 seats does
# not cost a second full paid round for the 3 that worked.

#: THE FREE SEATS. Both ride the founder's Max subscription, so a round using only
#: these 2 costs nothing however many turns it takes.
FREE_SEATS = frozenset({"cc2", "fable"})

#: WHY THE DEFAULT CHANGED, and it is the founder's ruling rather than a
#: preference. Verbatim, 2026-09-28: *"There should be no paid dispatches without
#: my express authorisation. You should make sure this is the case going forward.
#: If the answers are useful however we should use them."*
#:
#: THE DEFECT THIS REPLACES. With `PANEL_ONLY` unset this line selected ALL 6
#: seats, 5 of them paid, so the SAFE path required remembering an environment
#: variable and the EXPENSIVE path was the default. On 2026-09-22 that omission
#: dispatched 5 paid seats on a round the founder had asked to be free; they were
#: killed 2m39s in, after the spend had begun. The existing guard
#: `TestNoPaidSeatWasDispatched` detects that AFTERWARDS, which is a receipt and
#: not a brake.
#:
#: WHY A LEDGER RATHER THAN ANOTHER ENVIRONMENT VARIABLE. An env var is something
#: this assistant can set for itself, so a guard resting on one guards nothing it
#: is meant to guard against. The ledger is a COMMITTED file: spending money
#: requires an entry naming the round and quoting the founder's authorisation, so
#: an unauthorised dispatch requires forging his words in a file that appears in
#: `git diff` and in review. The enforcement is auditability, not cleverness, and
#: this comment states the limit plainly rather than implying the guard is
#: unbypassable.
#:
#: NOTHING IS REMOVED. Paid dispatch remains available by exactly the same route
#: it always had, with an authorisation recorded alongside it.
#: THE PATH IS EXTRACTED FROM THE CANONICAL READER, NEVER SPELT AGAIN HERE.
#: THE DEFECT THIS REPLACES, measured 2026-09-28 by execution. This line used to
#: read `_Path(__file__).resolve().parent / "paid_dispatch_authorisations.json"`,
#: a SECOND spelling of a path the reader module already owns -- and the wrong
#: one. `bench/paid_dispatch_authorisations.json` does not exist; the committed
#: ledger is `bench/directives/universal/paid_dispatch_authorisations.json`, so
#: `is_file()` returned False and all 7 authorised rounds were refused. Repointing
#: the path alone did not help either: the real file is a MAPPING with
#: `authorisations[].rounds[]` and `founder_verbatim[]`, and the parser below
#: demanded a flat list, so it answered "not a list of entries" for all 7.
#:
#: WHY DELEGATE RATHER THAN PARSE AGAIN. `bench/paid_dispatch_authorisations.py`
#: is the reader, and its own docstring gives the reason: "The authorisation list
#: is a money constraint; 2 copies that could drift is exactly the shape to
#: avoid." This gate WAS the second copy. It now calls that module, so there is 1
#: parser and 1 path, and a schema change cannot green one while breaking the
#: other. 3 test files already read the ledger through the same module.
import paid_dispatch_authorisations as _paid_ledger  # noqa: E402  (bench is on sys.path, line 27)

#: Bound at import for the callers and messages that reference it. `_ledger_path()`
#: is the LIVE lookup, so the gate and the reader can never disagree about which
#: file is being consulted.
PAID_LEDGER = _paid_ledger.AUTHORISATIONS

#: Minimum length of the founder's own words an entry must carry. An entry that
#: merely names a round authorises nothing.
_MIN_QUOTE_CHARS = 20


def _ledger_path() -> _Path:
    """Where the authorisation ledger lives, asked of the reader every time."""
    return _paid_ledger.AUTHORISATIONS


def _founder_quote(entry: dict) -> str:
    """The founder's own words from a ledger entry, longest first.

    The committed schema records them as `founder_verbatim`, a LIST of his
    quotations. `founder_authorisation` is accepted as a single-string spelling of
    the same field so that no existing entry stops being readable.
    """
    words = entry.get("founder_verbatim") or entry.get("founder_authorisation") or ""
    if isinstance(words, str):
        quotes = [words]
    elif isinstance(words, (list, tuple)):
        quotes = [str(w) for w in words]
    else:
        quotes = []
    quotes = [q.strip() for q in quotes if str(q).strip()]
    return max(quotes, key=len) if quotes else ""


def _paid_is_authorised(round_name: str) -> tuple[bool, str]:
    """Is a paid dispatch authorised for this round? Returns (ok, reason).

    EVERY FAILURE IS A REFUSAL. Missing file, unreadable file, wrong schema,
    unnamed round and an entry without the founder's words all return False. A
    guard that degrades to no guard is the defect this project keeps recording.
    """
    ledger = _ledger_path()
    if not ledger.is_file():
        return False, f"no authorisation ledger at {ledger}"
    try:
        entry = _paid_ledger.authorisation_for(round_name)
    except (ValueError, OSError) as exc:
        return False, f"authorisation ledger unreadable: {exc}"
    except (AttributeError, TypeError) as exc:
        # The reader expects a mapping with an `authorisations` list. Anything
        # else -- a bare list, a string, a number -- lands here and REFUSES
        # rather than raising through into a dispatch.
        return False, (
            f"authorisation ledger is not a mapping with an 'authorisations' "
            f"list ({type(exc).__name__}: {exc})"
        )
    if entry is None:
        return False, f"no ledger entry for round {round_name!r}"
    quote = _founder_quote(entry)
    if len(quote) < _MIN_QUOTE_CHARS:
        return False, (
            f"ledger entry for round {round_name!r} carries no founder "
            f"authorisation quote (at least {_MIN_QUOTE_CHARS} characters required)"
        )
    return True, f"authorised for round {round_name!r}: {quote[:80]}"


def select_models(only: str, round_name: str) -> list[tuple[str, str, str]]:
    """The seats this run may dispatch.

    An empty `only` selects the FREE seats, never the whole panel. A request that
    names a paid seat is refused unless the ledger authorises this round.
    """
    if not only:
        return [m for m in _ALL if m[0] in FREE_SEATS]
    wanted = [w.strip() for w in only.split(",") if w.strip()]
    chosen = [m for m in _ALL if m[0] in wanted]
    paid = [m[0] for m in chosen if m[0] not in FREE_SEATS]
    if not paid:
        return chosen
    ok, reason = _paid_is_authorised(round_name)
    if not ok:
        raise SystemExit(
            f"REFUSED: PANEL_ONLY names paid seat(s) {', '.join(paid)} and {reason}.\n"
            f"  Paid dispatch needs an entry in {_ledger_path()} whose\n"
            f"  'authorisations' list carries an object with this round in its\n"
            f"  'rounds' list and the founder's words in 'founder_verbatim', e.g.\n"
            '    {"authorisations": [{"id": "...", "date": "YYYY-MM-DD",\n'
            '       "rounds": ["<log-dir-name>"],\n'
            '       "founder_verbatim": ["<his words, 20+ characters>"]}]}\n'
            "  This is the founder's ruling of 2026-09-28, not a transport limit."
        )
    print(f"    PAID DISPATCH AUTHORISED -- {reason}")
    return chosen


#: Bound by `main()` once the run directory is known, because the ledger keys on
#: the round name. Kept importable at module level so the 37 callers that read
#: `MODELS` are unaffected when no run is in progress.
#: PAID SEATS DO NOT EXIST AT MODULE LEVEL (panel seat's finding, 2026-09-28,
#: reproduced here by execution). The previous binding honoured `PANEL_ONLY`
#: verbatim, so `PANEL_ONLY=cx,cgpt` plus a bare `import` yielded a MODELS list
#: carrying 2 paid seats that NO ledger check had seen -- `select_models` is only
#: reached through `main()`, so any importer dispatching from module state walked
#: straight past the gate. The ledger can only authorise a ROUND, and at import
#: time no round exists, so at import time no paid seat can be authorised.
#: `main()` rebinds through `select_models` (which can refuse) before any
#: dispatch, so nothing a real run may legitimately do is removed.
MODELS = [m for m in _ALL if m[0] in FREE_SEATS] if not _ONLY else [
    m for m in _ALL if m[0] in _ONLY.split(",") and m[0] in FREE_SEATS
]

# THE PANEL HAS NEVER RUN UNDER THE CDSFL SCHEMA. Measured 2026-09-07: of the 37
# dispatchers that call `call_claude_cli`, **0** call the registry composer, and
# this one carried a 3,015-character hand-written system prompt instead. Meanwhile
# 28 of them load `bench/directives/universal/cdsfl_core_formal.md` -- 28,183
# characters, the formal schema itself, covering constraint classification and
# precedence, the P-pass loop, the proportionality gate, the corroboration model,
# extended P-pass as a DAG, the survival predicate, epistemic marking, and (§10)
# Sufficiency Assessment and Convergence Declaration.
#
# CC1 first reported "8 of 37 compose the schema, Wilson [11.4%, 37.2%]". That was
# a SUBSTRING match on "cdsfl_registry", and those files reference it to load a
# TARGET MODULE, not to compose directives. The true figure is 0 of 37, Wilson
# [0.0%, 9.4%]. `compose()` is the experiment runners' mechanism for per-model
# directive composition; it is not what a review panel needs.
#
# ADDITIVE, STRICTLY. The schema is PREPENDED and every rule below is kept: none
# of "no compelled convergence", the additive standard, the one-shot notice or
# "tools decide, not votes" appears in the formal document (checked: 0 occurrences
# each), and the one-shot rule is what stopped fable returning a holding note.
# Removing any of them to make room would be the subtractive failure the additive
# standard forbids. Cost: the seat prompt goes from ~3.0K to ~31.2K characters,
# about 7,800 tokens, which is the schema doing its job rather than overhead.
from wolfram_standard import panel_clause as _wolfram_clause  # noqa: E402

_SCHEMA_DOC = _REPO / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
_SCHEMA = _SCHEMA_DOC.read_text(encoding="utf-8")

SYSTEM = (
    _SCHEMA + "\n\n" +
    "You are on a six-seat review panel for CDSFL, a research framework that uses "
    "structured Popperian falsification and a multi-model panel to find defects in "
    "STEM artefacts. Biological component names are ANALOGY ONLY -- module names, "
    "not biology.\n\n"
    "NAME THINGS BY THEIR FORMAL NAME. Use the identifier, function or file as it "
    "appears in the code, the term as docs/GLOSSARY.md defines it, or the standard "
    "software-engineering term for the construct. DO NOT COIN A LABEL. A coined "
    "label reads as project vocabulary to the next reader and is nobody's agreed "
    "term: measured 2026-10-05, one seat's phrase 'release valve' spread from a "
    "single comment to 12 identifier sites and 10 comments while appearing 0 times "
    "in the glossary. If no formal name exists, describe the mechanism in full "
    "rather than naming it, and say that you are doing so.\n\n"
    "CDSFL's founding principle is TOOLS DECIDE, NOT VOTES. A finding is confirmed "
    "when a tool independently re-executes a falsifier, never by model agreement. "
    "Hold yourself to it: prefer a claim you can check to one that sounds right. "
    "Where you assert a mathematical result, DERIVE it.\n\n"
    "NO COMPELLED CONVERGENCE. Return YOUR verdict and YOUR strongest falsification. "
    "Do not attempt to agree with the other seats. Disagreement is preserved as "
    "information.\n\n"
    "You are expected to declare the reasoning SOUND where it is. This panel is not "
    "scored on finding faults, and a clean verdict backed by derivation is as useful "
    "as a refutation.\n\n"
    "Do not pad. Every word is read."
    # THE ADDITIVE STANDARD REACHES EVERY SEAT BY CONSTRUCTION (2026-09-07).
    # It had been pasted into ONE brief, on 2026-08-31, and into no standing
    # file and no system prompt -- so the rule governing whether work is
    # additive was itself an addition wired to nothing. Here it cannot be
    # omitted by whoever writes the next brief.
    "\n\n" "THE ADDITIVE STANDARD (founder, standing). Work is additive: it adds to the reliability, functionality, accuracy, robustness and stated aims of the project. NEVER disable or remove a feature -- removal ONLY when something better renders it redundant, and 'better' means a COMMITTED MEASUREMENT showing the replacement dominates on a named property. A judgement that something is better is not evidence that it is. Symmetrically: an addition that nothing reaches is not additive either -- every new flag, gate or entry point must be wired to a caller and executed by a test. Measured over this project's own record since 2026-08-01: 11 confirmed defects were additions that did nothing, and 0 were removals of something needed."

    # SIMPLEST SUFFICIENT AND COMPOSABILITY, added 2026-10-02 on the founder's
    # instruction, and his instruction was that they go in the DISPATCHER rather
    # than in one brief: "These principles should be mechanically written into
    # all panel dispatches and not just this single dispatch." Measured when he
    # asked: "additive" appeared 7 times in this file and "simplest sufficient"
    # and "composab" 0 times each, so 2 of the 3 standards reached no seat.
    # Guarded by bench/tests/test_panel_carries_the_three_standards_2026-10-02.py.
    "\n\n" "THE SIMPLEST SUFFICIENT SOLUTION (founder, standing). Default to the simplest solution that is SUFFICIENT -- sufficient meaning it actually discharges the requirement, not that it is small. The exception is prose, graphics and UX, where richer expression may be what serves the task. A fix that is more elaborate than the problem requires is not a better fix; it is more surface to go wrong, and this project has shipped additions nothing reached 11 times."
    "\n\n" "COMPOSABILITY, AND IT IS NOT 'BOTH FIXES CAN COEXIST' (founder, verbatim, 2026-10-02). \"Composability doesn't mean composing two solutions just because they can be composed. It means this principle should be applied where two composed solutions demonstrably provide a better, more robust and/or more efficient solution than either fix in isolation. Where a single fix out performs a composed one, that fix should continue to be preferred. In all cases any fix should also take the first two conditions fully into consideration also.\" So: compose ONLY on a demonstrated advantage over each fix alone, and the demonstration is a measurement, not a judgement. If one fix alone performs as well, prefer it. And a composed fix must still satisfy the additive standard and the simplest-sufficient standard -- it does not get an exemption from either by virtue of being a synthesis."
    # THE SEAT GETS ONE TURN (2026-09-07). Diagnosed after fable spent 647 s,
    # made 0 tool calls, and returned "I'll hold until the completion
    # notification" -- a reply only reachable in a multi-turn session.
    # `claude -p` is one-shot: the turn that ends IS the answer. Nothing we
    # sent corrected that belief, because the prompt never said so.
    "\n\n"
    "THIS IS A ONE-SHOT DISPATCH. You will NOT be re-invoked and there is no "
    "later turn. Do not end your turn waiting for a background task or a "
    "notification: whatever you have written when the turn ends IS your answer. "
    "Do not start the full test suite -- it takes over 8 minutes and you will "
    "lose the budget waiting. Run targeted tests instead. If you run short of "
    "time, WRITE YOUR FINDINGS SO FAR. A partial answer carrying evidence is "
    "worth everything; a holding note is worth nothing."
    # THE WOLFRAM STANDARD REACHES EVERY SEAT BY CONSTRUCTION (Question 11,
    # 2026-09-17). Seats run with `--setting-sources ""`, so .claude/CLAUDE.md,
    # where the standard lived, never reached them: the audit read this SYSTEM
    # at 29,924 characters and found "wolfram", "Out[" and "UNVERIFIED" 0 times.
    # The words follow the POLICY the launcher applies -- under the default
    # `serial` the seat is told to use Wolfram as the second falsifier and given
    # a queuing gate; under `deny` it is told not to, and given a refusing one.
    # A seat is never told one thing while the launcher does another.
    "\n\n" + _wolfram_clause()
)


def dispatch(name, model_id, route):
    # SET THE SANDBOX CWD ON *THIS* THREAD (2026-09-06). `_PANEL_CWD_TLS` is a
    # `threading.local()`, and this function runs inside a ThreadPoolExecutor, so a
    # value set on the main thread is invisible here -- each worker reads its own,
    # which is None. Proven: main sees the path, both pool workers see None.
    #
    # That is why the first attempt at founder ruling 35's second half FAILED
    # SILENTLY: main logged "seats confined to a copy", every worker passed
    # cwd=None, and the seats ran in the live repository. cc2 caught it by running
    # `pwd`, and fable had already written a file into the canonical tree.
    _seat_cwd = confine_this_thread(name)
    """EVERY SEAT GETS TOOLS. Founder ruling 2026-09-05: "Tool use is at the core
    of what CDSFL is."

    The first dispatch of this panel used the tool-FREE OpenRouter and DeepSeek
    paths, so 3 of 5 seats could only reason. That inverts the founding principle
    -- a seat that cannot execute cannot decide by execution, and the panel
    degenerates toward exactly the model agreement CDSFL exists to reject.

    `bench/openrouter_tools.py` was built for precisely this (Exp 40 item 1E.11)
    and its own docstring says so: the non-Anthropic seats "have no tool execution
    unless the host wires structured function-calling". It was built and not used.

    Tools offered: sympy_verify, z3_verify, pytest_run, ruff_check, mypy_check.
    Every tool call made by a `claude_cli` or `openrouter` seat is recorded in
    the seat's JSON, so the claim "this panel used tools" is checkable rather
    than asserted. The `deepseek` branch is the remaining gap: it is passed
    TOOL_SPECS but returns only text, so its n_tool_calls is still structurally
    0 and must be read as "not recorded", never as "ran nothing".
    """
    t0 = time.time()
    tool_log = []
    try:
        if route == "claude_cli":
            # 900s, NOT the 300s default. THE PROJECT ALREADY LEARNED THIS AND I
            # DID NOT CARRY IT ACROSS. experiment_11_orchestrator.py:136 sets
            # `timeout=900,  # WP4a: 300->900s to prevent CC2 timeout cascade`
            # for exactly this seat. This dispatcher took the function default
            # instead, so on 2026-09-06 the cc2 seat failed 3 attempts at 300s
            # each -- 900s of wall clock producing nothing -- on a brief that
            # fable completed in 237s. The seat did not fail on merit; it ran out
            # of clock while executing the tool work the brief demanded, and the
            # seat that was asked to DEFEND the proposal was the one lost.
            # 1800s, raised from 900 on 2026-09-07: BOTH seats hit the 900 s wall
            # with 0 chars on a brief that asked them to run archive-scanning
            # work. The clock, not the task, was the binding constraint.
            #
            # 1800s RETAINED. A raise to 3600 was made and REVERTED within the
            # hour on 2026-10-06, and the reversal is recorded because the
            # reasoning that produced it was wrong in an instructive way.
            #
            # WHAT WAS CLAIMED: that the 1800 s clock was the binding constraint on
            # the cc2 seat, inferred from a timed-out attempt that had made 88 tool
            # calls at a measured 20.455 s per call while still working.
            #
            # WHAT REFUTED IT, the same night: the identical brief then completed in
            # 1020.0 s with 2581 words, having made 49 tool calls at 20.816 s per
            # call. 49 calls is what the brief actually needs, and 1800 s leaves 76%
            # headroom over the 1020 s it took. The clock was never binding.
            #
            # WHAT WAS ACTUALLY HAPPENING, and it is a diagnostic signature worth
            # keeping. The per-call RATE was stable across all 3 attempts -- 20.455
            # and 20.816 s per call -- so the seat was never slowed down. The call
            # COUNT changed: 88 and still unfinished during the founder's reported
            # network outages at about 04:22 and 05:03, against 49 to a complete
            # answer once the link was stable. A seat on a degraded route keeps
            # issuing tool calls at its normal speed and never converges, because
            # the calls themselves are failing and being retried. fable, for
            # comparison, answered in 751.2 s with 50 calls at 15.024 s per call.
            #
            # SO A LONGER TIMEOUT IS THE WRONG LEVER AND WOULD HAVE MADE IT WORSE:
            # it lets a degraded round churn for an hour instead of 30 minutes. The
            # remedy for a dead or degraded route is to detect it BEFORE the brief
            # is sent -- `_refuse_if_a_seat_is_not_alive`, which established the
            # route in 5.91 s -- and to re-dispatch when it recovers, which
            # `scripts/panel_round_watchdog_2026-10-06.py` does.
            #
            # THE CONTENTION HYPOTHESIS BELOW IS NOT REFUTED EITHER, and the earlier
            # version of this comment wrongly said it was. Those 2 failures happened
            # while the seats were serialised, but they also happened during network
            # outages, so they are not a clean test of contention. The block below
            # still correctly describes itself as uninterventional.
            # THE SUBSTANCE TEST WAS BUILT AND NEVER PASSED HERE.
            # accept_reply_or_work (experiment_11_orchestrator.py:781) exists for
            # exactly this and takes the sandbox path: it accepts a SHORT reply
            # only when real work sits beside it, and rejects a holding note.
            # Without it a 168-character "I'll hold until..." was recorded as
            # ok=True and counted as a seat that answered. max_retries=2 bounds
            # the cost.
            # THE TOOL-CALL COUNTER WAS 0 BY CONSTRUCTION, NOT BY MEASUREMENT.
            # 2026-09-07. `tool_log` is initialised empty and, on this branch,
            # was never assigned again -- only the `openrouter` branch below
            # ever set it. So `n_tool_calls` read 0 for cc2 and fable on every
            # panel ever run here, however much work the seats actually did,
            # while the docstring above promised the opposite: "Every tool call
            # made by every seat is recorded in the seat's JSON, so the claim
            # 'this panel used tools' is itself checkable rather than asserted."
            # It was not checkable. It was 0 with no way to be anything else.
            #
            # Concretely, fable.json of 2026-09-06 23:01 carries n_tool_calls 0
            # beside a reply quoting verbatim `pwd` output and a real sandbox
            # path -- unreadable as either proof or fabrication, because the
            # only field that could tell them apart was hard-wired to 0.
            #
            # BUILT AND UNWIRED, again, and this file NAMES that shape 40 lines
            # below about `set_panel_cwd`: "carried this at HIGH ... describing
            # the confinement half as unbuilt when in fact it was built and
            # unwired -- the project's most repeated failure shape." The sibling
            # mechanism, in the same file, had the same defect at the same time.
            #
            # `set_tool_log_sink` (experiment_11_orchestrator.py:331) is thread-
            # local, which is what makes it safe under the ThreadPoolExecutor
            # below, and setting it also switches the CLI from --output-format
            # text to stream-json, which is the ONLY format carrying tool_use
            # blocks. Pattern copied from confer_panel_2026-08-28.py:173, the 1
            # of 37 dispatchers that had it right.
            _sink = _logs_dir() / f"{name}.tools.json"
            # A STALE SINK WOULD BE READ AS THIS RUN'S (cc2, 2026-09-07). Two
            # dispatches into the same LOGS directory -- exactly what a
            # PANEL_ONLY re-dispatch does -- would otherwise report the earlier
            # run's tool calls as belonging to this one.
            _sink.unlink(missing_ok=True)
            set_tool_log_sink(str(_sink))
            try:
                resp = call_claude_cli(
                    model_id, SYSTEM, PROMPT, timeout=1800, max_retries=2,
                    accept=accept_reply_or_work(_seat_cwd or str(_REPO)),
                    # RULING (j): a retry gets a tree of its own, never the one
                    # the timed-out attempt was halfway through editing.
                    on_attempt=lambda n, _s=name: fresh_sandbox_for_attempt(_s, n),
                )  # native Bash
            finally:
                set_tool_log_sink(None)
            # Read the sink BACK into the seat record. The reference dispatcher
            # leaves it in a side file, which keeps n_tool_calls wrong in the
            # record a reader actually opens.
            if _sink.is_file():
                try:
                    tool_log = json.loads(_sink.read_text(encoding="utf-8")).get("calls", [])
                except (OSError, ValueError) as _e:  # noqa: BLE001
                    print(f"  [{name}] tool log unreadable: {_e}", flush=True)
        elif route in ("deepseek", "moonshot"):
            # NO SEAT IS INVISIBLE (founder, 2026-09-20: "No model gets a free
            # pass on tool use"). Both direct-API routes return TEXT, so before
            # today their tool calls had nowhere to go: the archive shows
            # DeepSeek at 0 recorded calls across 8 replies while the OpenRouter
            # seats recorded 5 of 9 and 5 of 7. `record` is passed here and read
            # straight into `tool_log`, so these seats count toward the Section P
            # condition P3 on the same footing as every other route.
            _calls: list = []
            _fn = call_deepseek if route == "deepseek" else call_moonshot
            # KIMI NEEDS LONGER THAN THE 300 s DEFAULT. Round 1 of this review
            # lost the seat entirely to `APITimeoutError: Request timed out`
            # after 904.5 s with 0 tool calls, on a brief of about 2,900 tokens
            # with a 16-iteration tool budget. The short probe that verified the
            # route used a 1-line question and answered in seconds, so it
            # measured the route and not the workload -- which is exactly the
            # gap between "the seat works" and "the seat can do this job".
            _timeout = 1500 if route == "moonshot" else 300
            resp = _fn(model_id, SYSTEM, PROMPT, tools=TOOL_SPECS,
                       record=_calls, timeout=_timeout,
                       max_tool_iters=PANEL_TOOL_ITERATIONS)
            tool_log = _calls
        else:
            # TOOL BUDGET RAISED AT THE CALL SITE, not in the shared default
            # (founder's spend approval, 2026-09-20: up to 10 pounds, cheaper
            # better). MAX_TOOL_ITERATIONS is 6 and every other caller keeps it.
            # A round-trip can carry SEVERAL tool calls, so 6 is less tight than
            # it reads -- but this brief asks a seat to run 4 separate check
            # scripts and verify a collapse both symbolically and numerically,
            # and a seat that runs out mid-verification returns an UNCHECKED it
            # could have answered. Estimated worst case at 10: about 2 pounds
            # for the round, against 0.99 at 6.
            r = call_openrouter_with_tools(model_id, SYSTEM, PROMPT,
                                           tools=TOOL_SPECS, max_tokens=32768,
                                           timeout=300, max_iterations=PANEL_TOOL_ITERATIONS)
            resp = r.get("final_text", "")
            tool_log = r.get("tool_calls", [])
            # WHY THE SEAT RECORD CARRIES THIS (audit finding, 2026-09-20).
            # The tool budget was raised from 6 to 10 iterations the same night,
            # and the comment justifying it named the risk exactly: "a seat that
            # runs out mid-verification returns an UNCHECKED it could have
            # answered". `call_openrouter_with_tools` RETURNS the field that
            # answers whether that happened, and it was being discarded -- so a
            # seat cut off at the cap was recorded identically to one that
            # finished, and the raise could never be evaluated.
            stopped_reason = r.get("stopped_reason")
            tool_iterations = r.get("iterations")
        ok = bool(resp and resp.strip())
        out = {"model": name, "route": route, "ok": ok, "chars": len(resp or ""),
               "tool_calls": tool_log, "n_tool_calls": len(tool_log),
               "stopped_reason": locals().get("stopped_reason"),
               "tool_iterations": locals().get("tool_iterations"),
               "elapsed_s": round(time.time() - t0, 1), "response": resp or "",
               # RULING (j): "recording the attempt number in the reply". A
               # reader can now tell which tree a verdict was measured in.
               "attempts": list(_SEAT_ATTEMPTS.get(name, []))}
    except Exception as e:  # noqa: BLE001
        # READ THE SINK ON THE FAILURE PATH TOO (cc2, 2026-09-08, SS-2b).
        # The previous fix kept the counter KEYS here but not the counter VALUE.
        # `tool_log` is only assigned after `call_claude_cli` RETURNS, so when it
        # raises -- a timeout, every attempt rejected, a vanished cwd -- this arm
        # reported n_tool_calls=0 while the sink on disk held the real count.
        # Measured by the seat that found it: "RESULT C all-attempts-rejected:
        # ok=False n_tool_calls=0 (sink on disk says 13)".
        #
        # That is the counter reading 0 EXACTLY WHEN A SEAT FAILS, which is the
        # case this panel actually hit on 2026-09-06 and again on 2026-09-07 --
        # so the original "0 by construction" defect survived, in the one branch
        # where the evidence matters most, inside the commit that repaired it.
        if not tool_log:
            try:
                _s = _logs_dir() / f"{name}.tools.json"
                if _s.is_file():
                    tool_log = json.loads(_s.read_text(encoding="utf-8")).get("calls", [])
            except (OSError, ValueError):
                pass
        out = {"model": name, "route": route, "ok": False,
               "error": f"{type(e).__name__}: {e}",
               "tool_calls": tool_log, "n_tool_calls": len(tool_log),
               "elapsed_s": round(time.time() - t0, 1), "response": "",
               "attempts": list(_SEAT_ATTEMPTS.get(name, []))}
    (_logs_dir() / f"{name}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    # A seat that hit the cap says so ON THE CONSOLE LINE, not only in the
    # JSON, because the console line is what an operator reads during a round.
    _stopped = out.get("stopped_reason")
    _cut = f" STOPPED={_stopped}" if _stopped and _stopped != "finish" else ""
    print(f"  [{name}] ok={out['ok']} chars={out.get('chars', 0)} "
          f"tools={out.get('n_tool_calls', 'native')} {out['elapsed_s']}s{_cut}"
          + (f" ERR={out.get('error')}" if not out["ok"] else ""), flush=True)
    return out


def _validate_brief_or_refuse() -> None:
    """Refuse a brief that does not meet the format, BEFORE any seat is paid.

    MOVED INSIDE main() 2026-09-09, within an hour of being written at module
    level, because the full suite went red at 4 tests. Two test files IMPORT this
    module to read its real `SYSTEM` string -- executing it rather than grepping
    it, which is the project's own rule -- and stage a stub BRIEF.md purely to get
    past the file-exists check. They never dispatch. A validation running at
    import punished INSPECTION, which is not the thing that costs money.

    The guard belongs at the point of spend. main() is the only path to a paid
    seat, so this is both the correct place and the one that leaves the tests
    honest: neither was edited to accommodate it.

    4 of the 6 seats are PAID since 2026-09-20 (cx, cgpt, ge, ds; cc2 and fable
    run on the Max subscription), and the record holds a case where a briefing
    defect broke 2 seats and forced a re-dispatch. Measured when this was wired: all 49
    archived briefs would be refused, failing 1 to 7 of the checks, mean 2.4 --
    the spread being what shows the rule discriminates rather than rejecting
    uniformly.
    """
    sys.path.insert(0, str(_REPO / "scripts"))
    try:
        from panel_brief_validate import validate as _validate
        from panel_brief_validate import check_declared_figures as _figures
    except Exception as exc:
        print(f"panel: brief validator unavailable ({exc}); refusing rather than "
              f"dispatching unchecked", file=sys.stderr)
        raise SystemExit(2)
    problems = _validate(PROMPT)
    # DECLARED FIGURES ARE RE-EXECUTED BEFORE DISPATCH (2026-09-10). The
    # round-4 brief said gamma was 0.451 when it was 0.415413, crossing a
    # GAMMA_BANDS boundary, and both seats spent part of their round on it.
    # The 7 shape checks cannot see a wrong number; this can.
    problems += _figures(PROMPT)
    if not problems:
        return
    if os.environ.get("PANEL_BRIEF_UNCHECKED"):
        print(f"panel: brief has {len(problems)} unmet check(s), dispatching anyway "
              f"because PANEL_BRIEF_UNCHECKED is set", file=sys.stderr)
        return
    print(f"panel: REFUSED — {BRIEF} fails {len(problems)} required check(s) and "
          f"3 of the 5 seats are paid:", file=sys.stderr)
    for p in problems:
        print(f"  - {p}", file=sys.stderr)
    print("  format: bench/directives/universal/panel_brief_template.md", file=sys.stderr)
    print("  to dispatch anyway, deliberately: PANEL_BRIEF_UNCHECKED=1", file=sys.stderr)
    raise SystemExit(2)


def _refuse_if_the_suite_state_is_unknown() -> None:
    """Refuse to spend money against a harness whose last suite run was RED.

    FOUNDER, 2026-09-20, approving this as item 2 of 3: the launchers should
    check the suite record before dispatching.

    THE CASE FOR IT IS THIS PROJECT'S OWN RECORD. On 2026-09-05 a panel round
    ran with 16 of 17 tool calls erroring, and the errors were read as results.
    On 2026-09-10 a round-4 brief carried a gamma figure that was wrong in its
    3rd decimal and 2 seats spent part of their round on it. Both were paid.
    A suite that is RED is the cheapest available warning that the harness the
    seats are about to reason over does not currently do what it says.

    STALENESS IS A WARNING, NOT A REFUSAL, and the distinction matters. Every
    commit makes the record 1 commit older, so refusing on staleness would
    refuse almost every dispatch and be switched off within a week. A RED
    record, by contrast, is a positive statement that something is broken.
    A MISSING record is neither red nor green; it is unknown, and unknown is
    not a licence to spend, so it refuses.

    Override, deliberately and visibly: PANEL_SUITE_UNCHECKED=1.
    """
    sys.path.insert(0, str(_REPO / "scripts"))
    paid_n = len([m for m in MODELS if m[2] != "claude_cli"])
    try:
        import suite_record
    except Exception as exc:                                       # noqa: BLE001
        print(f"panel: the suite gate is unavailable ({type(exc).__name__}: {exc}); "
              f"refusing rather than dispatching {paid_n} paid seats unchecked",
              file=sys.stderr)
        raise SystemExit(2)
    suite_record.gate(spend=f"panel ({paid_n} of {len(MODELS)} seats paid)",
                      override_env="PANEL_SUITE_UNCHECKED", paid_seats=paid_n)


def _load_aliveness():
    """Load the dated aliveness module. importlib because the filename carries a date."""
    import importlib.util, sys as _sys
    _p = Path(__file__).resolve().parent / "seat_aliveness_2026-10-06.py"
    spec = importlib.util.spec_from_file_location("cdsfl_seat_aliveness", _p)
    m = importlib.util.module_from_spec(spec)
    _sys.modules["cdsfl_seat_aliveness"] = m   # dataclasses need this registered
    spec.loader.exec_module(m)
    return m


def _probe_caller(model_id, route, prompt, timeout):
    """A 0-argument caller for 1 seat, over the SAME route the round will use.

    Reusing the dispatcher's own call functions is the point: a probe that took a
    different path would establish the liveness of something other than the route
    about to carry the brief.
    """
    def _call() -> str:
        if route == "claude_cli":
            return call_claude_cli(model_id=model_id, system_prompt=None,
                                   user_prompt=prompt, max_tokens=16,
                                   timeout=timeout, max_retries=1)
        if route in ("deepseek", "moonshot"):
            _fn = call_deepseek if route == "deepseek" else call_moonshot
            return _fn(model_id, None, prompt, max_tokens=16, timeout=timeout,
                       max_retries=1)
        return call_openrouter(model_id, None, prompt, max_tokens=16,
                               timeout=timeout, max_retries=1)
    return _call


def _refuse_if_a_seat_is_not_alive(models) -> int:
    """Ask every seat to print Ready! before the brief is built or sent.

    THE FOUNDER'S ASK, 2026-10-06: *"perhaps we should build a simple 'aliveness
    test', where the models get up to 3 attempts, by simply asking it to print
    'Ready!'"*

    MEASURED THE SAME NIGHT, which is why it runs HERE rather than after the
    sandboxes: the cc2 seat consumed 2423.7 seconds and returned 0 words because
    the network had dropped. Everything between this line and the dispatch --
    6.53 seconds and 606 MB of sandbox per seat, the brief build, the whole reply
    window -- was spent to discover a fact a 1-word probe establishes in seconds.

    A DEAD SEAT REFUSES THE ROUND; IT IS NEVER DROPPED FROM THE ROSTER, because
    skipping a model is benching it and that is forbidden. The watchdog then
    retries cheaply, which is the composition the founder asked for.

    Returns 0 to proceed, or a non-zero exit code.
    """
    if _os.environ.get("PANEL_SKIP_ALIVENESS"):
        print("    aliveness probe SKIPPED because PANEL_SKIP_ALIVENESS is set",
              flush=True)
        return 0
    try:
        AL = _load_aliveness()
    except Exception as exc:  # noqa: BLE001
        # A probe that cannot be LOADED has not passed. Same trap as the POST.
        print(f"    REFUSED: the aliveness probe could not be loaded: "
              f"{type(exc).__name__}: {exc}", flush=True)
        return 2
    callers = {n: _probe_caller(m, r, AL.PROBE_PROMPT, AL.DEFAULT_TIMEOUT_S)
               for n, m, r in models}
    print(f"    aliveness probe: asking {len(callers)} seat(s) to print "
          f"{AL.PROBE_TOKEN.capitalize()}!, up to {AL.DEFAULT_ATTEMPTS} attempts "
          f"each, serialised", flush=True)
    results = AL.probe_roster(callers, attempts=AL.DEFAULT_ATTEMPTS,
                              timeout=AL.DEFAULT_TIMEOUT_S)
    for n, r in results.items():
        print(f"      {n}: {'ALIVE' if r.alive else 'NO ANSWER'}  "
              f"({r.elapsed_s}s, {r.detail})", flush=True)
    refusal = AL.refusal_for(results)
    if refusal:
        print(refusal, flush=True)
        print("    to dispatch anyway, deliberately: PANEL_SKIP_ALIVENESS=1",
              flush=True)
        return 3
    return 0


def _load_star():
    """Load the dated star-topology module. importlib because of the date in the name."""
    import importlib.util, sys as _sys
    _p = Path(__file__).resolve().parent / "star_topology_2026-10-06.py"
    spec = importlib.util.spec_from_file_location("cdsfl_star_topology", _p)
    m = importlib.util.module_from_spec(spec)
    _sys.modules["cdsfl_star_topology"] = m
    spec.loader.exec_module(m)
    return m


def _refuse_if_topology_is_skipped(models) -> int:
    """Blind round first, joint round second — checked, not remembered.

    THE FOUNDER'S RULING, 2026-10-06: *"I didn't just state it as a 'preference', I
    stated that it should be built into all confer round machinery going forward so
    it couldn't be skipped."*

    IT RUNS BEFORE THE ALIVENESS PROBE because it reads local files and costs no
    network. A round that must be refused should be refused for free.

    2 checks, and the grouping key for the first is the BRIEF ITSELF. Rounds asking
    the same question have a byte-identical BRIEF.md, so sha256 over the brief finds
    the siblings with nothing for an operator to label or forget. A sibling that
    holds a LANDED reply and is not named in PANEL_BLIND_OF is a refusal, because its
    reply is reachable from this seat's sandbox copy of the tree.

    Returns 0 to proceed, or a non-zero exit code.
    """
    if _os.environ.get("PANEL_SKIP_TOPOLOGY"):
        print("    star topology check SKIPPED because PANEL_SKIP_TOPOLOGY is set",
              flush=True)
        return 0
    try:
        ST = _load_star()
    except Exception as exc:  # noqa: BLE001
        print(f"    REFUSED: the star-topology check could not be loaded: "
              f"{type(exc).__name__}: {exc}", flush=True)
        return 2
    logs_root = _logs_dir().parent
    round_name = _logs_dir().name
    roster = [n for n, _m, _r in models]

    # THE KIND IS DETECTED, NOT DECLARED. Reading it off `PANEL_JOINT_OF` meant that
    # forgetting the variable silently downgraded a joint round to the blind check --
    # which then passed trivially, because a joint brief is never byte-identical to a
    # blind brief and so has no siblings. The gate the founder asked to be unskippable
    # was skippable by omission, which is the commonest way a control is skipped.
    # `round_kind` decides from what the brief CONTAINS: a brief carrying another
    # round's reply verbatim is a joint brief.
    kind = ST.round_kind(logs_root, round_name).upper()
    if kind == "JOINT":
        quoted = ST.quotes_other_rounds(logs_root, round_name)
        declared = {x.strip() for x in (_JOINT_OF or ()) if str(x).strip()}
        undeclared = [q for q in quoted if q not in declared]
        if undeclared:
            print("REFUSED: this brief quotes the replies of round(s) "
                  f"{undeclared}, so it is a JOINT round and must declare what it "
                  "follows.\n"
                  f"  this round: {round_name}\n"
                  f"  declared  : {sorted(declared) or '(nothing)'}\n"
                  f"  Re-run with: PANEL_JOINT_OF={','.join(quoted)}", flush=True)
            print("    to dispatch anyway, deliberately: PANEL_SKIP_TOPOLOGY=1",
                  flush=True)
            return 4
        refusal = ST.check_joint_round(logs_root, round_name, _JOINT_OF, roster)
    else:
        refusal = ST.check_blind_round(logs_root, round_name, _BLIND_OF)
    if refusal:
        print(refusal, flush=True)
        print("    to dispatch anyway, deliberately: PANEL_SKIP_TOPOLOGY=1",
              flush=True)
        return 4
    sibs = ST.sibling_rounds_on_the_same_question(logs_root, round_name)
    print(f"    star topology: {kind} round; {len(sibs)} answered sibling(s) on the "
          f"same brief, all declared", flush=True)
    return 0


def main() -> int:
    # BIND THE BRIEF HERE, not at import. See `resolve_brief`.
    resolve_brief()
    _validate_brief_or_refuse()
    # SPEND-GATE 0 OF 2 -- EARLIEST OF THE THREE, and it decides WHICH seats exist
    # rather than whether the run may proceed. An empty PANEL_ONLY now yields the
    # 2 free seats; naming a paid seat is refused unless the committed ledger
    # authorises this round. Founder's ruling, 2026-09-28. Rebinding the module
    # global is what WIRES `select_models` -- an unreached guard guards nothing,
    # which is the failure mode the additive standard names on the addition side.
    #
    # ORDER IS LOAD-BEARING (panel seat's finding, 2026-09-28, confirmed by
    # execution). This must run BEFORE the suite gate below, because that gate
    # counts paid seats by reading MODELS and `suite_record.gate` RETURNS without
    # refusing when `paid_seats` is 0. Measured against a red record: paid_seats=0
    # proceeds, paid_seats=2 exits 2. Since the module-level binding above now
    # carries no paid seat, counting before this rebind would tell the spend gate
    # there is no spend to protect and a red suite would stop blocking paid
    # rounds. The 2 changes are 1 fix; applying either alone regresses the other.
    #
    # `_logs_dir()` RATHER THAN A BARE `LOGS`, which is what A22 built it for. An
    # unresolved brief makes `LOGS` None, and `LOGS.name` then raises
    # "AttributeError: 'NoneType' object has no attribute 'name'" -- the exact
    # illegible shape A22's docstring records as the price of moving the binding
    # out of import time. `_logs_dir()` says to call `resolve_brief()` instead.
    # A real run is unaffected: `resolve_brief()` above always binds it.
    global MODELS
    MODELS = select_models(_ONLY, _logs_dir().name)

    # SPEND-GATE 2 OF 2, and it runs before any seat is built, for the same
    # reason the brief check does: main() is the only path to a paid seat.
    _refuse_if_the_suite_state_is_unknown()

    paid = [m for m in MODELS if m[2] != "claude_cli"]
    print(f"=== maths panel — {len(MODELS)} dispatched seats + CC1 ===")
    print(f"    PAID seats: {', '.join(n for n, _, _ in paid)}  "
          f"(brief {len(PROMPT):,} chars, about {len(PROMPT)//4:,} tokens each)")
    print(f"    free seats: cc2, fable (Max subscription)")

    # SEATS WORK IN A COPY, NOT THE LIVE TREE (founder ruling 35, second half,
    # 2026-09-06). `--allowedTools` already withholds Write and Edit and says "No
    # file modification", and a seat still edited 4 tracked files -- through Bash,
    # which no tool list can restrain. Confinement has to be positional.
    #
    # The cwd mechanism has existed since August (`set_panel_cwd`, fail-closed on a
    # bad path) and was never called. Runway 0C.9 has carried this at HIGH since
    # then, describing the confinement half as unbuilt when in fact it was built
    # and unwired -- the project's most repeated failure shape.
    # ─────── STAR TOPOLOGY, checked first because it costs no network ───────
    _topo_rc = _refuse_if_topology_is_skipped(MODELS)
    if _topo_rc:
        return _topo_rc

    # ─────────── ALIVENESS PROBE, before anything expensive ───────────
    _alive_rc = _refuse_if_a_seat_is_not_alive(MODELS)
    if _alive_rc:
        return _alive_rc

    global _PANEL_SANDBOX_CWD
    baseline = panel_sandbox.fingerprint(_REPO)
    # THE CONTROL PLANE IS OUTSIDE THE REPO AND WAS UNWATCHED (2026-09-07).
    # A seat wrote to the operator's real ~/.claude/settings.json at 15:04:45
    # and `canonical_was_touched` did not fire, because it digests the repo's
    # tracked files and $HOME is not among them. That write appended a hook --
    # code that then runs on every turn of every unrelated session.
    home_baseline = panel_sandbox.control_plane_fingerprint()
    # ONE SANDBOX PER SEAT (2026-09-11). See `_SEAT_SANDBOXES` above for why: a
    # shared writable copy made the seats' verdicts dependent on each other and
    # left the proposals diff unattributable.
    sandboxes = {}
    for _n, _m, _r in MODELS:
        sandboxes[_n] = panel_sandbox.build(_REPO, blind_of=_BLIND_OF, blind_text=_blind_text_for(_BLIND_OF))
        _SEAT_SANDBOXES[_n] = str(sandboxes[_n])
        print(f"    {_n} confined to its own copy: {sandboxes[_n]}")
    # Kept for any caller still reading it; every seat now uses its OWN.
    sandbox = next(iter(sandboxes.values()))
    _PANEL_SANDBOX_CWD = str(sandbox)
    try:
        # SEATS SHARING ONE SUBSCRIPTION ARE SERIALISED AMONG THEMSELVES.
        #
        # Every `claude_cli` seat authenticates against the SAME Max subscription,
        # and until 2026-10-05 all seats were submitted to a pool sized to the
        # whole roster, so both free seats hit `claude -p` in the same instant.
        #
        # THE EVIDENCE THAT THIS IS THE BINDING CONSTRAINT, measured by
        # `scripts/why_cc2_times_out_2026-10-05.py`:
        #  * The 2 seats are NOT different in speed. Mann-Whitney over 64 cc2 and
        #    65 fable successful replies: U = 2258.0, p = 0.4031, with an
        #    independent rank computation agreeing. Medians 809.5s and 720.7s.
        #  * cc2 is NOT failing more than fable. Fisher p = 0.7183 overall and
        #    1.0000 on recent rounds; Barnard 0.6179 and 0.8396. The founder's
        #    report of "cc2 timing out" is real as an observation and wrong as an
        #    attribution: BOTH free seats roughly tripled (cc2 4.08% -> 15.00%,
        #    fable 2.08% -> 10.00%).
        #  * Failures are NOT independent across seats. 3 of the 5 failing rounds
        #    lost BOTH seats at near-identical durations -- 1956.0/1956.2,
        #    902.0/902.0, 18.7/18.8 seconds. Against an independence model at the
        #    measured per-seat rate, 3 of 5 such rounds gives a binomial
        #    p = 1.556646e-07. A shared cause is the only thing that produces
        #    matched failure times in two separate processes.
        #  * The failure rate HAS risen: Fisher p = 0.046723, Barnard p = 0.044514.
        #
        # STATUS: HYPOTHESIS WITH STRONG CORRELATIONAL SUPPORT, NOT AN
        # INTERVENTIONAL RESULT. Contention explains matched failure times, the
        # rise as briefs grew heavier, and tonight's shape (fable 74 tool calls and
        # 12,711 chars; cc2 0 tool calls and 0 chars across 2 full 1800s attempts).
        # It has NOT been tested by running a panel both ways. The measurement that
        # would settle it is in the study programme; until it runs, this change is
        # a scheduling change with a stated reason, not a demonstrated cure.
        #
        # ADDITIVE: no seat is dropped and no capability is removed. Seats on other
        # routes still run concurrently with each other and with the serialised
        # group, so a mixed roster is no slower than before. The cost is wall clock
        # for the free panel only, bounded by the sum rather than the max of 2
        # seats, against a measured ~1 in 8 recent loss of a whole seat.
        _shared = [(n, m, r) for n, m, r in MODELS if r == "claude_cli"]
        _independent = [(n, m, r) for n, m, r in MODELS if r != "claude_cli"]

        def _run_shared_group():
            """One subscription, one at a time, in roster order."""
            out = []
            for n, m, r in _shared:
                out.append(dispatch(n, m, r))
            return out

        results = []
        _workers = max(1, len(_independent) + (1 if _shared else 0))
        with concurrent.futures.ThreadPoolExecutor(max_workers=_workers) as pool:
            futs = []
            if _shared:
                futs.append(pool.submit(_run_shared_group))
            for n, m, r in _independent:
                futs.append(pool.submit(dispatch, n, m, r))
            for f in concurrent.futures.as_completed(futs):
                got = f.result()
                results.extend(got if isinstance(got, list) else [got])
    finally:
        _PANEL_SANDBOX_CWD = None
        set_panel_cwd(None)
        # KEEP what a seat changed rather than discarding it. The 2026-09-06 seat's
        # edit was CORRECT -- it repaired a real false-convergence path -- so
        # throwing such work away to enforce hygiene would be its own loss. It
        # returns as a PROPOSAL for CC1 to test under f and sy, which is what the
        # founder asked for.
        # PER SEAT, so a proposal carries the name of whoever wrote it. Before
        # 2026-09-11 all seats shared 1 copy and this diff was the union with no
        # attribution -- round 10 produced 29 files and no way to tell which seat
        # left which, which is exactly the provenance failure the project's own
        # "no fake model labels" rule exists to prevent.
        proposals = {}
        # EVERY ATTEMPT'S TREE, not just the one the seat ended in (ruling (j)).
        # A seat that timed out and retried leaves 2 trees, and round 17 showed
        # what reading only 1 of them costs: 14 files with no reply behind them.
        for _n, _atts in _SEAT_ATTEMPTS.items():
            for _a in _atts:
                if not os.path.isdir(_a["path"]):
                    continue
                for rel, d in panel_sandbox.changes(Path(_a["path"]), _REPO).items():
                    proposals[f"{_n}:attempt-{_a['attempt']}:{rel}"] = d
        if proposals:
            (_logs_dir() / "seat_proposals.diff").write_text(
                "\n".join(f"### {rel}\n{d}" for rel, d in sorted(proposals.items())),
                encoding="utf-8")
            print(f"    seats proposed edits to {len(proposals)} file(s) IN THE COPY "
                  f"-> {_logs_dir() / 'seat_proposals.diff'} (untested; not applied)")
        # DETECTION for what a sandbox cannot prevent: a seat writing to an
        # absolute path it already knows. vault_keys.sh records that limit exactly.
        home_touched = panel_sandbox.control_plane_was_touched(home_baseline)
        if home_touched:
            print(f"    *** OPERATOR CONTROL PLANE MODIFIED DURING THE PANEL: "
                  f"{home_touched} ***")
            (_logs_dir() / "control_plane_touched.json").write_text(
                json.dumps(home_touched, indent=2), encoding="utf-8")
        touched = panel_sandbox.canonical_was_touched(baseline, _REPO)
        if touched:
            print(f"    *** CANONICAL TREE MODIFIED DURING THE PANEL: {touched} ***")
            (_logs_dir() / "canonical_touched.json").write_text(
                json.dumps(touched, indent=2), encoding="utf-8")
            # TASK A5: SAY WHOSE DOING IT WAS, or say that it cannot be shown.
            # This alarm fired on 14 files in round 2, 8 in round 8 and 11 in
            # round 9, and every one was the operator's own concurrent edit. A
            # human re-derived that from the tool logs each time. The evidence
            # was already on disk; now the alarm reads it.
            try:
                # EVERY seat's sandbox is excluded, not just one, now that each
                # has its own; and the CANONICAL ROOT is passed, so only an
                # ABSOLUTE path naming it counts as evidence of an escape.
                attrib = panel_sandbox.attribute_canonical_touch(
                    touched, LOGS, sandbox_root=list(sandboxes.values()),
                    repo_root=_REPO)
                (_logs_dir() / "canonical_attribution.json").write_text(
                    json.dumps(attrib, indent=2), encoding="utf-8")
                if attrib["_any_attributable"]:
                    print("    *** AND AT LEAST ONE IS ATTRIBUTABLE TO A SEAT. "
                          "This is the containment failure, not a false alarm. ***")
                    for _rel, _v in attrib["_per_path"].items():
                        if _v["attributable_to_a_seat"]:
                            print(f"        {_rel}: {_v['hits'][0]['seat']} via "
                                  f"{_v['hits'][0]['tool']}")
                else:
                    print("    NO SEAT IS SHOWN TO HAVE TOUCHED ANY OF THEM "
                          "(operator's own edits are the ordinary cause).")
                    print("    NOTE: an input preview is truncated, so this is "
                          "'not shown', never 'did not'.")
            except Exception as _at_exc:                  # noqa: BLE001
                print(f"    attribution FAILED: {type(_at_exc).__name__}: "
                      f"{_at_exc} -- the alarm stands unattributed")
        else:
            print("    canonical tree unchanged (7900 tracked files re-hashed)")
        # NOTHING IS DELETED UNLESS THE OPERATOR ASKS (founder ruling (j),
        # 2026-09-17): *"Take care when a panel review or an experiment completes
        # however that the sandbox does not simply get automatically deleted and
        # that the results do not end up simply being discarded, as has happened
        # in the recent past."*
        #
        # The line this replaces destroyed every copy on the way out. The diff
        # had been harvested, but a diff is not a file: a seat that wrote a new
        # script, a data file or a figure lost the artefact itself. So every
        # attempt's tree is harvested INTO THE RUN'S OWN LOG DIRECTORY first --
        # whole files, not only diffs -- and the copies are then KEPT unless
        # PANEL_REAP_SANDBOXES=1 says otherwise. `release` refuses to remove a
        # copy whose harvest did not complete, whatever that variable says.
        harvest_and_retain(_SEAT_ATTEMPTS, _logs_dir(), _REPO)
        _SEAT_SANDBOXES.clear()

    ok = sum(1 for r in results if r["ok"])
    print(f"\n  {ok}/{len(MODELS)} responded. Logs: {LOGS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
