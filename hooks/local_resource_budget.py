#!/usr/bin/env python3
"""PreToolUse gate: refuse a fan-out that would over-commit the founder's own machine.

HIS RULING, 2026-10-11: *"You have to be aware of the resources you are working with. As you
said sq (when in force) tells you not to overload Anthropic's servers. But clearly I also have
limits, and unlike Anthropic, my resources don't change. So you will need to implement a
permanent fix for this."*

WHAT THIS PREVENTS, measured on 2026-10-11. One audit fan-out spawned 48 agents issuing 2,310
local Bash calls, of which 263 were pytest. The machine is a Macmini9,1 with 8 logical cores and
8 GiB of RAM. A pytest process tree on this repository peaks at 364.7 MiB (42 samples), and live
headroom was 1.91 GiB, so the machine holds about 5 concurrent heavy processes. The harness cap
is min(16, ncpu-2) = 6, i.e. ALREADY ABOVE CAPACITY, and it is derived from cores alone while
the binding constraint on 8 GiB is memory.

WHY A HOOK RATHER THAN A NOTE. The project's own standard is that a guard must be structurally
enforced rather than hoped for (`feedback_falsification_gate`). A directive in CLAUDE.md is read
once per session and can be forgotten mid-task; this runs on every call.

WHAT IT REFUSES, deliberately narrow to avoid false positives:
  * an Agent/Task call whose prompt instructs pytest or the full suite -- subagents must consult
    a cached board instead, because 263 invocations answered what 1 board answers;
  * a Workflow whose script both fans out AND instructs pytest.
Everything else is ADVISED, not blocked: the budget is injected so it cannot be unseen.

Exit codes: 0 allow (with context on stdout), 2 block with the reason on stderr.
"""
import json
import math
import os
import re
import subprocess
import sys

HEAVY_MIB = 364.7          # measured: one pytest tree on Constraint_Engineering
LIGHT_MIB = 80.0
HEADROOM_SHARE = 0.5
RESERVED_CORES = 2
GATED_TOOLS = {"Agent", "Task", "Workflow"}


def _sysctl(name, default=0):
    try:
        return int(subprocess.run(["sysctl", "-n", name], capture_output=True,
                                  text=True, timeout=10).stdout.strip())
    except Exception:
        return default


def _headroom_mib():
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout
    except Exception:
        return 0.0
    m = re.search(r"page size of (\d+) bytes", out)
    page = int(m.group(1)) if m else 4096
    tot = 0
    for label in ("Pages free", "Pages inactive", "Pages speculative"):
        mm = re.search(rf"{label}:\s+(\d+)", out)
        if mm:
            tot += int(mm.group(1))
    return tot * page / (1024 * 1024)


#: WHAT COUNTS AS INSTRUCTING A HEAVY VERIFICATION RUN, and why polarity matters.
#:
#: HIS RULING, 2026-10-17: "Make the guard aware of negation as you have
#: suggested."
#:
#: THE DEFECT, OBSERVED TWICE IN ONE TURN ON 2026-10-17. The predicate was a bare
#: substring search over the whole prompt, so a delegated brief whose text
#: FORBADE the tooling matched on the very words expressing the prohibition. The
#: first refusal fired on an explicit "do NOT run pytest"; the second, after that
#: word was removed, fired on "cost more than a full board run" inside the same
#: prohibition.
#:
#: WHY THAT IS WORSE THAN AN ANNOYANCE. An author who cannot state the limit in a
#: brief has 2 options left: drop the limit, or rephrase around the matcher.
#: Dropping it is actively dangerous, because a delegated agent with no stated
#: limit is MORE likely to invoke the tooling. So the false positive selected for
#: exactly the behaviour the guard exists to prevent. It is the same defect class
#: as `execute-do-not-grep`: a text matcher standing in for a judgement.
#:
#: THE RULE NOW: a mention must be IMPERATIVE -- a command form, or governed by a
#: verb of execution -- and must NOT sit inside a negation. The window is
#: deliberately short, because a negation 200 characters earlier does not govern
#: the sentence in hand, and treating it as though it did would let any brief
#: smuggle an instruction past the guard by opening with a disclaimer.
#: TWO CLASSES OF MENTION, because they are different parts of speech and the
#: existing contract test of 2026-10-11 is right about the first one.
#:
#: A COMMAND NAME is imperative by itself. `pytest` is an executable, so
#: `agent('pytest')` instructs it exactly as typing it at a shell would; no verb
#: is needed and demanding one let a real instruction through.
#: A NOUN PHRASE is not. "the suite has 606 tests" commands nothing, so "the
#: suite" and "full board" require a verb of execution nearby before they count.
#: Negation suppresses BOTH, which is the whole point of the change.
_COMMAND_MENTION = re.compile(
    r"\bpytest\b|python3?\s+-m\s+pytest", re.IGNORECASE)
#: ★ WIDENED 2026-11-21, ENTRY B182, ON HIS RULING: *"I accept your
#: recommendation"* -- widen the noun-phrase side to the forms this project
#: actually writes, and add a case for a bare path such as `bench/tests/`.
#:
#: WHAT IT MISSED AND BY HOW MUCH. The previous alternation named 4 forms, and
#: `scripts/the_budget_gate_is_blind_to_its_own_subject_2026-11-13.py` drives a
#: grid of 5 verbs by 10 nouns by 3 tails -- 150 cells, every one a genuine
#: instruction this guard exists to refuse. Re-executed 2026-11-21 before the
#: change: 126 of 150 passed straight through, 0.840000, Wilson
#: [0.772960, 0.890060] and Clopper-Pearson [0.771351, 0.894713], both routes
#: agreeing exactly. A gate that blind supplies assurance it cannot deliver.
#:
#: THE FORMS ARE TAKEN FROM THE PRODUCER, NOT INVENTED. The 10 nouns it measures
#: are the project's own vocabulary, so widening to anything else would be
#: fitting a pattern to my imagination and then measuring it against the same
#: imagination. The misses were the `test suite` variants -- `whole suite` does
#: not match `whole test suite` -- the named boards, and the bare path.
#:
#: LOOSENESS IS SAFE HERE AND THAT IS STRUCTURAL, not optimism: a noun phrase
#: still needs an imperative verb within the window before it counts, and a
#: negation anywhere in the window suppresses it. That is what makes `suite`
#: admissible as a bare stem where it would be reckless in a pattern that
#: decided alone. The 2 false positives of 2026-10-17 came from refusing on
#: AMBIGUITY, and that behaviour is untouched.
#: ★ WIDENED 2026-11-22 ON A PANEL FINDING, VERIFIED BEFORE ADOPTION. The grid
#: the B182 repair closed was built from 10 nouns chosen by the hand that wrote
#: the pattern, so closing it could only ever show that the LISTED phrasings are
#: caught. Counted against the project's own .md/.py/.txt, the forms it actually
#: writes and this pattern did not hold were: bare `the board` with no
#: qualifier, `bench/tests` with no trailing slash, and `the guards`.
#:
#: TWO OF THEM ARE SENTENCES THE PROJECT WRITES AT ITSELF, which is what lifts
#: this above a vocabulary quibble. This hook's own refusal message says "run
#: the board ONCE yourself, save the result", and the panel brief dispatched on
#: 2026-11-22 said "Run the guards." Both passed straight through the gate that
#: exists to refuse exactly those instructions.
_NOUN_MENTION = re.compile(
    r"\bbench/tests\b"
    r"|\b(?:the\s+|a\s+)?(?:full\s+|whole\s+|entire\s+)?(?:test\s+)?suite\b"
    r"|\b(?:the\s+|a\s+)?(?:full\s+|commit\s+|verification\s+|guard\s+|test\s+)?board\b"
    r"|\b(?:the\s+|all\s+(?:the\s+)?)?guards\b",
    re.IGNORECASE)
#: ★ `kick off` ADDED 2026-11-21, AND IT WAS FOUND BY THE NOUN FIX RATHER THAN
#: BY READING. Entry B182's ruling covered the noun side; widening that took the
#: blind rate from 126 of 150 to 30 of 150, and the residual 30 was EXACTLY
#: 10 nouns x 3 tails x 1 verb -- every remaining miss was the phrase `kick
#: off`, which this alternation never held. `start` was here and its commonest
#: idiom was not.
#:
#: SO THE NOUN SIDE WAS NOT THE WHOLE DEFECT, and the arithmetic says so without
#: appeal to judgement: 30 = 10 x 3 x 1 leaves no room for a noun still missing.
#: Adding the verb is mine under his handover of 2026-11-21 -- it is a missing
#: synonym in a detector, not safety, legality, or a change in how the system
#: works -- and leaving it would have left 1 in 5 real instructions passing
#: through the guard that exists to refuse them.
#:
#: THE HYPHENATED AND INFLECTED FORMS GO IN TOO, because a detector that holds
#: `kick off` and not `kicks off` is the same defect one tense along.
_IMPERATIVE = re.compile(
    r"\b(run|runs|running|invoke|invokes|invoking|execute|executes|executing|"
    r"call|calls|calling|launch|launches|launching|start|starts|starting|"
    r"fire|fires|spawn|spawns|"
    r"kick[\s-]?off|kicks[\s-]?off|kicking[\s-]?off|"
    #: ★ UNHYPHENATED `rerun` ADDED 2026-11-22. `\brun\b` already catches
    #: `re-run`, because the hyphen is a word boundary, and catches nothing in
    #: `rerun`, where it is not. The 2 seats disagreed on whether the
    #: unhyphenated form is written here at all -- one counted 398, the other
    #: 0 -- so it was counted directly: 444 unhyphenated against 7,162
    #: hyphenated across the project's .md/.py/.txt, an unhyphenated share of
    #: 0.058375, Wilson [0.053326, 0.063870] and Clopper-Pearson
    #: [0.053210, 0.063881] on 2 agreeing routes. The dominant form is
    #: hyphenated and was never at risk; the minority form is 444 occurrences,
    #: which is not 0.
    r"rerun|reruns|rerunning|reran)\b", re.IGNORECASE)
_NEGATION = re.compile(
    r"\b(do not|don't|dont|never|must not|mustn't|cannot|can't|without|avoid|"
    r"refrain|no need to|skip|forbid|forbidden|prohibit|prohibited|"
    r"not to|rather than|instead of)\b", re.IGNORECASE)
_BEFORE, _AFTER = 140, 60


def _instructs_heavy_verification(text: str) -> bool:
    """True only where the text COMMANDS a heavy verification run.

    Returns False for a prohibition, which is the point: a brief that forbids the
    tooling must be writable without tripping the guard that forbids it.
    """
    for pattern, needs_a_verb in ((_COMMAND_MENTION, False),
                                  (_NOUN_MENTION, True)):
        for m in pattern.finditer(text):
            before = text[max(0, m.start() - _BEFORE):m.start()]
            after = text[m.end():m.end() + _AFTER]
            if _NEGATION.search(before) or _NEGATION.search(after):
                continue                  # a prohibition, not an instruction
            if not needs_a_verb:
                return True               # a command name needs no verb
            if _IMPERATIVE.search(before) or _IMPERATIVE.search(after):
                return True
            # A noun phrase with neither a verb nor a negation nearby is
            # AMBIGUOUS, and ambiguity is allowed. Refusing on ambiguity is
            # what produced both false positives of 2026-10-17.
    return False


def budget(per_mib):
    cores = _sysctl("hw.ncpu", os.cpu_count() or 1)
    head = _headroom_mib()
    core_c = max(1, cores - RESERVED_CORES)
    mem_c = max(1, math.floor(head * HEADROOM_SHARE / per_mib))
    chosen = min(core_c, mem_c)
    try:
        la1 = os.getloadavg()[0]
    except Exception:
        la1 = 0.0
    # 0.6 rather than 0.7 per core, plus an independent memory-pressure arm. Measured
    # 2026-10-11: at load 5.42 on 8 cores the 0.7 threshold (5.6) did not fire, while
    # headroom had already fallen to 1224.2 MiB. A near-miss on a safety threshold is a defect.
    if la1 > 0.6 * cores or head < 2 * per_mib:
        chosen = max(1, chosen // 2)
    return chosen, core_c, mem_c, round(head, 1), cores, round(la1, 2)


#: DEPTH BEFORE BREADTH -- the 3 statements a fan-out brief must carry.
#:
#: HIS QUESTION, 2026-10-25: *"But can't we somehow direct you to use some of that
#: reasoning depth prior to using these facilities also? What do you suggest?"*
#:
#: This is the suggestion, and it is deliberately EXACT LITERAL MARKERS rather than
#: any judgement about whether a prompt "looks thought through". A similarity-based
#: version of exactly this check was written on 2026-10-24 for note asks and failed
#: in BOTH directions -- 5 of 5 false positives, then it cleared the one true case
#: -- and was replaced with an exact id rule. The same discipline applies here.
#:
#: The markers cost 3 lines in a brief that should carry them anyway: the Agent tool's
#: own description says the brief is the only context the subagent will ever have.
DEPTH_MARKERS = (
    ("HYPOTHESIS:", "what the fan-out is meant to test"),
    ("FALSIFIED BY:", "the result that would prove the hypothesis wrong"),
    ("WHY NOT ONE CONTEXT:", "why depth in this context cannot answer it"),
)


def _missing_depth_markers(blob: str) -> list[tuple[str, str]]:
    """Which of the 3 required statements the brief does not carry.

    Case-insensitive literal substring, nothing cleverer. A brief that cannot name
    its own falsifier is not breadth; it is delegation of the thinking.
    """
    up = blob.upper()
    return [(m, why) for m, why in DEPTH_MARKERS if m not in up]


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tool = payload.get("tool_name") or ""
    if tool not in GATED_TOOLS:
        return 0
    ti = payload.get("tool_input") or {}
    blob = " ".join(str(ti.get(k, "")) for k in ("prompt", "script", "description", "args"))
    low = blob.lower()

    heavy_b, core_c, mem_c, head, cores, la1 = budget(HEAVY_MIB)
    light_b, *_ = budget(LIGHT_MIB)

    wants_pytest = _instructs_heavy_verification(low)
    fans_out = bool(re.search(r"\bparallel\s*\(|\bpipeline\s*\(|batch|fan.?out", low))

    # ★ BOTH REASONS ARE REPORTED, NOT THE FIRST ONE -- repair 2026-10-28.
    #
    # The depth check was added on 2026-10-25 and placed BEFORE the pytest
    # prohibition, with its own `return 2`. So a brief that both omitted the
    # depth statements AND instructed pytest inside delegated work was refused
    # for the depth statements alone, and the operator was never told the thing
    # that actually protects the machine: run the board once and consult a
    # cached result. Measured by the full-suite baseline of 2026-10-28, which
    # caught it through `test_the_local_resource_budget_binds_2026-10-11.py`:
    # the refusal arrived with returncode 2 and no mention of the remedy, and a
    # read-only agent was refused with the wrong message too.
    #
    # Half a refusal is worse than either half alone, because the operator fixes
    # what they were told about and the second refusal looks like a new problem.
    reasons: list[str] = []

    missing = _missing_depth_markers(blob)
    if wants_pytest and (tool in ("Agent", "Task") or fans_out):
        reasons.append(
            "REFUSED by local_resource_budget: this call instructs pytest inside delegated "
            f"work.\n  The founder's machine has {cores} cores and {head} MiB live headroom; "
            f"one pytest tree peaks at {HEAVY_MIB} MiB, so it holds {mem_c} concurrent heavy "
            f"process(es) (budget {heavy_b}).\n  Measured 2026-10-11: 263 delegated pytest "
            "invocations cost 4557.8 s at the cheapest observed rate against 3998.65 s for ONE "
            "full board.\n  DO THIS INSTEAD: run the board ONCE yourself, save the result, and "
            "have the delegated work consult that cached file.\n  His ruling of 2026-10-11: "
            '"you will need to implement a permanent fix for this."\n')
    if missing:
        reasons.append(
            "REFUSED by local_resource_budget: DEPTH BEFORE BREADTH.\n"
            f"  This {tool} brief is missing {len(missing)} of "
            f"{len(DEPTH_MARKERS)} required statement(s):\n"
            + "".join(f"      {m:24s} {why}\n" for m, why in missing)
            + "  HIS QUESTION, 2026-10-25: \"But can't we somehow direct you to use "
              "some of that reasoning depth prior to using these facilities also?\"\n"
              "  This is that direction. Add the 3 lines to the prompt and retry. They\n"
              "  cost nothing you should not already be writing -- the brief is the ONLY\n"
              "  context the delegated work will ever have.\n"
              "  A fan-out that cannot name its own falsifier is not breadth; it is\n"
              "  delegation of the thinking.\n"
              "  Measured: 10 of 12 errors on 2026-10-11 were catchable by reasoning\n"
              "  BEFORE running anything. Only 2 required execution.\n"
              "  See `reasoning-depth-before-breadth` in CLAUDE.md (local and global).\n")

    if reasons:
        # The PYTEST reason first when both apply: it is the one that protects
        # the 8 GiB, and it carries the concrete remedy.
        sys.stderr.write("\n".join(reasons))
        return 2

    print(f"[local-budget] founder's machine: {cores} cores, {head} MiB headroom, load {la1}. "
          f"Concurrent agent budget: {heavy_b} heavy (pytest/import-grade), {light_b} light "
          f"(grep/read-grade). Memory-bound at {mem_c}; harness default is "
          f"{min(16, max(1, cores - 2))} and is CORE-derived, so it over-commits 8 GiB. "
          f"Scale the fan-out to the budget, not to the token allowance.\n"
          f"[token-arm] HIS SECOND RESOURCE, raised 2026-10-04: \"a big spike in my Anthropic "
          f"Max plan usage quota, and right now I am nearly out of my weekly allowance ... I "
          f"usually only barely scratch the surface.\" Agents spend that allowance; reasoning "
          f"effort spends it too but costs 0 local CPU. BEFORE this fan-out, call "
          f"mcp__ccd_session_mgmt__get_usage and read the WEEKLY window. Prefer DEPTH "
          f"(more reasoning, more falsification passes on one claim) over BREADTH (more "
          f"agents): of 12 errors measured on 2026-10-11, 10 were catchable by reasoning "
          f"before running and only 2 needed execution.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
