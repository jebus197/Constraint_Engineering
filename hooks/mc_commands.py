#!/usr/bin/env python3
"""UserPromptSubmit hook: when the founder issues MC commands, put their OBLIGATIONS in context.

Written 2026-08-30 for the CDSFL founder.

THE FAILURE THIS PREVENTS
=========================
`mc_commands_nonoptional.md`, dated 20 April 2026, already says MC commands are directives
and must be executed in full, in order, without skipping or compressing. The founder's own
words there: "Do not waste tokens explaining why you didn't do as you were told. Just do it
in full!" It says to mark the rule in every memory and recovery resource. It was marked.

It did not work. Measured from the session transcript on 2026-08-30:

  * `sy` issued 5 times across the session.
  * Night of 2026-08-29/30: ONE genuine STEM-tool invocation across 223 tool calls (0.45%) --
    a single z3 call at 23:13.
  * The 21 April two-tool cross-verification rule: satisfied ZERO times that night.
  * A headline the founder was given ("slightly more than half of fixes fail") was falsified
    the next morning by ONE statsmodels call that should have been made at the time. The
    95% Wilson interval is [45.0%, 57.4%] and spans 50%.

WHY MARKING IT AGAIN CANNOT WORK
================================
The rule was already written in six places and recalled correctly when asked. The failure is
not recall -- it is that an MC command reads as a MODE ("be rigorous") rather than as a
REQUIRED ARTEFACT ("emit a tool call"). Nothing in the turn forces the artefact, so under
load the mode is satisfied in prose and the artefact never appears.

This project's own standing rule covers exactly this case: falsification must be
STRUCTURALLY ENFORCED, not hoped for (`feedback_falsification_gate.md`). A hook is the
structural version. The obligation arrives in context on the same turn as the command,
every time, without depending on anything being remembered.

MUST ALWAYS EXIT 0. A hook that blocks a prompt is worse than a missed directive.
"""
import json
import re
import sys

#: Trailing-directive lines only. `a, d` at the end of a message is a command;
#: the letter "a" inside a sentence is not.
_KNOWN = {"a", "d", "f", "p", "sy", "e", "re", "rg", "rc", "rs", "rt", "r",
          "c", "cy", "sq", "pr", "sv", "t", "ag", "ext", "y", "x", "cc2",
          "cx", "ge", "cgpt", "ds", "sth", "qc"}

#: What each command REQUIRES to appear in the turn. Phrased as an artefact, not a mood.
_OBLIGATION = {
    "sy":  "SY — REQUIRES an actual STEM-tool invocation this turn (SymPy, z3, SciPy, "
           "NumPy, statsmodels, mpmath, pint, Wolfram). Prose reasoning does NOT satisfy it. "
           "AND the 21 Apr 2026 rule: every computational claim cross-verified with at "
           "least TWO tools (z3+SymPy, scipy+statsmodels, NumPy+mpmath). Any proportion "
           "you report needs a confidence interval.",
    "f":   "F — FFAFP, five steps, all of them: FIND the issue with evidence; FOLLOW the "
           "blast radius BEFORE touching anything; ANALYSE with tools (the tool output IS "
           "the evidence); FIX the root cause; P-PASS by actively trying to break the fix. "
           "A fix you have not tried to break is a hypothesis, not a fix.",
    "rg":  "RG — read the anchoring resources END-TO-END. No summary, no truncation, no "
           "distilled ledger (standing clause, 20 Apr 2026). Chunk with offset/limit if a "
           "file exceeds one read. Then NAME the resources consulted in one line.",
    "p":   "P — P-pass: actively try to DISPROVE the conclusion before presenting it. "
           "Iterate until diminishing returns.",
    "a":   "A — analyse dispassionately. Evidence over agreement; if the record contradicts "
           "the founder's framing, say so with citations.",
    "d":   "D — DISCUSS before proceeding. Do not start implementing.",
    "t":   "T — produce the artefact PAIR: a TTS-friendly .txt in the project's Desktop "
           "tts folder AND a markdown mirror in experimental_notes/.",
    "e":   "E — extrapolate: what generalises, boundary conditions, new falsifiable "
           "questions. Mark [SPECULATIVE] / [VERIFY:current].",
    "sq":  "SQ — strictly sequential tool use for the rest of the session. One call at a "
           "time, no parallel batches. Sub-agents inherit the constraint.",
    "sv":  "SV — save state: read canonical docs SEQUENTIALLY, update ONBOARDING and "
           "RECOVERY, commit and push.",
    "re":  "RE — external research (web, arXiv, Semantic Scholar).",
    "ext": "EXT — external research, same as `re`.",
    "pr":  "PR — full panel review, NO compelled convergence. Preserve disagreement as "
           "information. CC1 holds its own position and does not merely synthesise.",
    "c":   "C — confer with Codex via CLI, bounded rounds, CC->CX direction.",
    "cy":  "CY — continue AND monitor any running experiment at ~60s cadence; keep a "
           "terminal tailing its output for the founder.",
    "ag":  "AG — use agents to parallelise independent work.",
    "sth": "STH — synthesise: consolidate the findings into one coherent statement.",
    "qc":  "QC — sweep related documentation for staleness before committing.",
}

_ALWAYS = ("MC commands are DIRECTIVES, not suggestions (20 Apr 2026). Execute every one in "
           "the sequence, in full, in order. Do not skip, compress, merge or silently drop "
           "a step; if one is blocked, NAME the blocker. Do not spend tokens explaining a "
           "non-execution — execute it.")


def commands_in(text: str):
    """MC tokens from trailing directive lines, in issue order, de-duplicated."""
    out, seen = [], set()
    # Widened after P-passing the first version, which missed four real shapes:
    #   * a list longer than 8 -- and the founder's own documented example
    #     `rg, sq, a, sy, sth, p, d, t` is exactly 8, so nine would have missed
    #   * commands more than 3 lines from the end
    #   * a stray courtesy word, e.g. "rg a d please"
    # Widened deliberately, then re-tested against the false-positive set: a line
    # still only counts when MOST of it is commands and at least two are present,
    # or it is a single bare command like `y`.
    lines = [ln for ln in text.strip().splitlines() if ln.strip()][-6:]
    for line in lines:
        raw = [t.strip().lower().rstrip(".!?") for t in re.split(r"[,\s]+", line.strip()) if t.strip()]
        if not raw or len(raw) > 14:
            continue
        known = [t for t in raw if t in _KNOWN]
        if not known:
            continue
        # A line of ordinary prose has few known tokens relative to its length.
        # Require the line to be overwhelmingly commands.
        if len(known) < len(raw) - 1:
            continue
        if len(known) == 1 and len(raw) > 1:
            continue
        for t in known:
            if t not in seen:
                seen.add(t)
                out.append(t)
    return out


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:                                    # noqa: BLE001
        return
    prompt = payload.get("prompt") or ""
    cmds = commands_in(prompt)

    # THE STANDING PAIR. Founder, 2026-08-30, verbatim: "you should use 'f' on
    # all your work exclusively, and 'sy' on all work that can be computationally
    # checked and determined! This is a hard constraint and should never be
    # bypassed!" So `f` and `sy` are UNCONDITIONAL -- they apply whether or not
    # the founder types them, and this fires on every turn.
    standing = [
        "[mc] STANDING HARD CONSTRAINT (founder 2026-08-30, never bypassed):",
        f"  • {_OBLIGATION['f']}",
        f"  • {_OBLIGATION['sy']}",
    ]
    if not cmds:
        print("\n".join(standing))
        return
    lines = standing + ["", f"[mc] {len(cmds)} MC command(s) ALSO issued: {', '.join(cmds)}",
                        "", _ALWAYS, ""]
    for c in cmds:
        ob = _OBLIGATION.get(c)
        if ob:
            lines.append(f"  • {ob}")
    lines.append("")
    lines.append("Before ending this turn, confirm each of the above actually produced its "
                 "artefact in this turn. An MC satisfied only in prose is an MC not executed.")
    print("\n".join(lines))


if __name__ == "__main__":
    try:
        main()
    except Exception:                                    # noqa: BLE001
        pass
    sys.exit(0)
