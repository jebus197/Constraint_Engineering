"""The Wolfram rule, held by EXECUTION rather than by reading the prose that states it.

WHY THIS FILE EXISTS. On 2026-09-29 the founder read a tracker line saying *"panel
seats may not call Wolfram; that rule has been in force since he set it"* and
answered: *"There is no 'denial rule' for Wolfram. That is clearly an invention by
you in what probably seemed like a 'safe default'. But it is actually opposite to
what I recently said."* He was right. His actual rule, verbatim: *"where seats can
use Wolfram (in its recently revised 'best of both' configuration preferably), then
they should use it (as their secondary cross verification falsifier), where they
cannot, then they should default to equivalent Open Source tools."*

THE CODE WAS NEVER WRONG -- only the prose was. `DEFAULT_POLICY` has been `serial`
since his 2026-09-17 ruling. So a test that read the module's docstrings would have
passed throughout while the tracker told a reader the opposite, which is the failure
`execute-do-not-grep` names: two descriptions, each internally consistent, disagreeing
with each other. This file therefore does both halves -- it CALLS the policy layer,
and it separately asserts that no LIVE document re-asserts the denial without carrying
its retraction. A panel transcript is exempt: rewriting a transcript destroys the
record it exists to preserve.

The `deny` policy is NOT under test as an error. It is retained and selectable, and a
machine that has never had Wolfram installed must still pass. What is under test is
which policy is in force by DEFAULT, and what a seat is consequently told and given.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "bench"))

import wolfram_standard as W  # noqa: E402


# ═════════════════════════════════════════════════════════════════════════════
# THE DENY-PIN PREDICATE, EXTRACTED 2026-10-01 SO IT CAN BE CALLED
#
# It was an inline comprehension inside the test, which meant the only way to
# ask what it recognises was to read it -- the failure `execute-do-not-grep`
# names. Extracted, it is exercised below on lines whose answer is known.
#
# TWO FIXES LANDED WITH THE EXTRACTION.
#
# (1) SCOPE. `.claude/worktrees/wf_*` holds throwaway clones the agent tooling
#     makes, and 3 of them from 2026-09-30 took this guard red: they carry
#     COPIES of the two exempt files, and the exemptions are absolute prefixes
#     under REPO, so a copy one directory deeper matched neither. Nothing was
#     pinned to deny -- the scan had walked out of its subject. The exclusion is
#     the project's existing convention, already spelled `_SKIP_DIRS` in
#     test_declared_patterns_reach_the_live_path_2026-09-30 and
#     `_NOT_THE_PROJECT` in test_every_test_file_is_collected_2026-09-01.
#
# (2) REACH. The old pattern required the separator to follow the NAME
#     directly, so it recognised `CDSFL_WOLFRAM_POLICY=deny` and missed BOTH
#     spellings anyone would actually commit:
#         env["CDSFL_WOLFRAM_POLICY"] = "deny"      <-- Python
#         "CDSFL_WOLFRAM_POLICY": "deny"            <-- JSON/TOML config
#     A guard that catches only the shell form, over a file set that includes
#     .py and .json precisely because those are where it would be set, could
#     have let the founder's ruling be inverted in silence. Quotes and a closing
#     bracket may now sit between the name and the separator. Backticks may NOT,
#     so a prose mention like `CDSFL_WOLFRAM_POLICY`: deny is not a false hit.
_DENY_PIN = re.compile(r"""CDSFL_WOLFRAM_POLICY['"\]]*\s*[=:]\s*['"]?deny""")

_NOT_THE_REPOSITORY = ("/.git/", "/.claude/worktrees/")


def _deny_pins(grep_lines: list[str]) -> list[str]:
    """Which `grep -rn` lines pin the policy to deny, in the LIVE tree?"""
    return [ln for ln in grep_lines
            if not any(seg in ln for seg in _NOT_THE_REPOSITORY)
            and not ln.startswith(str(REPO / "bench" / "wolfram_standard.py"))
            and not ln.startswith(str(REPO / "bench" / "tests"))
            and _DENY_PIN.search(ln)]


class TestThePolicyInForceIsEnablement:
    """Executed against the live module, not read from its comments."""

    def test_the_default_policy_is_serial(self):
        assert W.DEFAULT_POLICY == "serial"
        assert W.policy({}) == "serial", "an empty environment must resolve to the founder's default"

    def test_the_live_seat_arguments_carry_no_wolfram_denial(self):
        args = W.claude_cli_args()
        assert "--disallowedTools" not in args, (
            f"a seat is being denied Wolfram by default; args={args!r}. The founder's rule is the "
            "opposite: where a seat CAN use Wolfram it SHOULD, as the secondary falsifier.")
        joined = " ".join(args)
        assert "wolframscript" not in joined and "WolframKernel" not in joined

    def test_the_seat_is_given_the_serial_gate_not_the_refusing_one(self):
        assert W.gate_dir().name == "serial"
        assert W.gate_dir() == W.SERIAL_GATE

    def test_the_seat_is_TOLD_to_use_it(self):
        clause = W.panel_clause()
        assert clause == W.SERIAL_CLAUSE
        low = clause.lower()
        assert "wolfram" in low
        assert "not exempt" in low, "the clause must instruct use, not merely mention the name"

    def test_deny_is_still_selectable_because_a_wolfram_free_machine_must_pass(self):
        """The removal half of the additive standard: `deny` is retained, not deleted."""
        assert W.policy({W.POLICY_ENV: "deny"}) == "deny"
        assert "--disallowedTools" in W.claude_cli_args("deny")
        assert W.gate_dir("deny") == W.DENY_GATE

    def test_nothing_in_the_repository_switches_the_default_to_deny(self):
        """A committed `CDSFL_WOLFRAM_POLICY=deny` would silently restore the inverted rule."""
        out = subprocess.run(
            ["/usr/bin/grep", "-rn", "--include=*.py", "--include=*.sh", "--include=*.json",
             "--include=*.toml", "--include=*.cfg", "--include=*.ini",
             "CDSFL_WOLFRAM_POLICY", str(REPO)],
            capture_output=True, text=True).stdout.splitlines()
        offenders = _deny_pins(out)
        assert offenders == [], f"something pins the policy to deny: {offenders}"


class TestTheSeatEnvironmentActuallyReachesTheGate:
    """`seat_environment` is the only thing that puts the gate where a seat can use it."""

    def test_the_serial_gate_is_first_on_the_seat_path(self):
        sys.path.insert(0, str(REPO))
        from bench.experiment_11_orchestrator import seat_environment
        env = seat_environment(seat="cc2")
        first = env["PATH"].split(os.pathsep)[0]
        assert first == str(W.SERIAL_GATE), f"gate not first on PATH; got {first!r}"

    def test_the_gate_directory_is_real_and_carries_the_shim(self):
        assert W.SERIAL_GATE.is_dir()
        assert (W.SERIAL_GATE / "wolframscript").is_file()



def _quoted_spans(line: str) -> list[tuple[int, int]]:
    """Character spans of double-quoted runs, straight or typographic."""
    spans, open_at, i = [], None, 0
    while i < len(line):
        ch = line[i]
        if ch in '"\u201c\u201d':
            if open_at is None:
                open_at = i + 1
            else:
                spans.append((open_at, i))
                open_at = None
        i += 1
    return spans

#: A live document is one a canonical document points a reader at. A panel transcript
#: records what a seat SAID and must not be rewritten -- see task 7.1's ruling.
_TRANSCRIPT = re.compile(r"FULL_RECORD|panel_records_|/evidence/", re.I)

#: What counts as a retraction sitting beside a denial sentence.
_RETRACTED = re.compile(r"CORRECTED 2026-09-29|RETRACT|invention by you|false rule|was FALSE|OVERRULED", re.I)

_DENIAL = re.compile(
    r"denial (?:is the standing|stands|remains the default|is the default)"
    r"|seats may not call Wolfram"
    r"|Wolfram is (?:denied|excluded) (?:to|from) (?:panel )?seats",
    re.I)


class TestNoLiveDocumentReAssertsTheInventedRule:
    """The prose half. A denial sentence is allowed ONLY beside its retraction."""

    def test_every_surviving_denial_sentence_carries_its_correction(self):
        notes = REPO / "experimental_notes"
        bad = []
        for f in sorted(list(notes.rglob("*.md")) + list((REPO / "docs").rglob("*.md"))):
            if _TRANSCRIPT.search(str(f.relative_to(REPO))):
                continue
            lines = f.read_text(errors="replace").splitlines()
            for i, line in enumerate(lines, 1):
                if not _DENIAL.search(line):
                    continue
                # A retraction may sit on the same line or in the following paragraph,
                # because a dated correction appended under a historical statement is
                # the treatment this project uses for a document that WAS true.
                window = " ".join(lines[i - 1:i + 3])
                if _RETRACTED.search(window):
                    continue
                # REPORTED SPEECH IS NOT AN ASSERTION. A retraction has to be able to
                # QUOTE the sentence it retracts; on 2026-09-29 this test failed on the
                # retraction document itself, at a line reading `recorded as "denial
                # stands. Unanimous"`. A denial phrase sitting inside quotation marks,
                # in a file that carries a retraction somewhere, is the retraction
                # doing its job. Both conditions are required: a bare quoted denial in
                # a file with no retraction anywhere still fails.
                m = _DENIAL.search(line)
                quoted = any(a <= m.start() and m.end() <= b
                             for a, b in _quoted_spans(line))
                if quoted and _RETRACTED.search(f.read_text(errors="replace")):
                    continue
                bad.append(f"{f.relative_to(REPO)}:{i}")
        assert bad == [], (
            "these live lines assert a Wolfram denial rule with no retraction beside them: "
            + ", ".join(bad))

    def test_the_regex_can_actually_fail(self):
        """A guard that cannot fire is the defect this project keeps finding."""
        assert _DENIAL.search("Wolfram in panel reviews: denial stands.")
        assert _DENIAL.search("panel seats may not call Wolfram")
        assert not _DENIAL.search("Wolfram is enabled for every seat as the second falsifier.")
        assert _RETRACTED.search("... denial stands. [CORRECTED 2026-09-29 ...]")
        assert not _RETRACTED.search("denial stands. Unanimous.")


class TestTheConnectorBoundaryIsRecordedAsCapabilityNotPolicy:
    """The measured gap: a headless seat sees no Wolfram MCP server. Not a denial."""

    def test_the_serial_args_do_not_name_an_mcp_config(self):
        """`--strict-mcp-config` with no `--mcp-config` leaves a seat 0 MCP servers.

        Measured 2026-09-29: a headless `claude -p` seat reports 0 tools whose name
        contains "olfram" WITH OR WITHOUT the flag, so the flag is not what removes
        the connector -- it was never in the headless CLI's server list. The flag is
        load-bearing for CONFINEMENT (the founder: "none of the models ... should
        ever be able to reach the real repo"), so it stays. This test pins the shape
        so that adding a Wolfram-only `--mcp-config` later is a deliberate, visible
        change rather than a silent one.
        """
        args = W.claude_cli_args("serial")
        assert "--strict-mcp-config" in args
        assert "--mcp-config" not in args


class TestQuotationIsNotAssertion:
    """The discrimination added 2026-09-29, and the hole it must not open."""

    def test_quoted_spans_finds_straight_and_typographic_quotes(self):
        assert _quoted_spans('a "b" c') == [(3, 4)]
        assert _quoted_spans('a \u201cb\u201d c') == [(3, 4)]
        assert _quoted_spans('no quotes here') == []

    def test_a_quoted_denial_in_a_file_with_NO_retraction_still_fails(self, tmp_path):
        """Both conditions are required, or the guard is trivially evadable."""
        line = 'the panel recorded as "denial stands. Unanimous" and that was that'
        assert _DENIAL.search(line), "the phrase must still be detected inside quotes"
        assert not _RETRACTED.search(line), "this line carries no retraction marker"
        m = _DENIAL.search(line)
        assert any(a <= m.start() and m.end() <= b for a, b in _quoted_spans(line)), (
            "the span check must see the phrase as quoted")

    def test_an_UNQUOTED_denial_is_never_excused_by_quotes_elsewhere(self):
        line = 'He said "hello" and denial is the standing default.'
        m = _DENIAL.search(line)
        assert not any(a <= m.start() and m.end() <= b for a, b in _quoted_spans(line)), (
            "an unquoted denial must not be excused by an unrelated quotation")


class TestTheDenyPinPredicateRecognisesWhatItClaimsTo:
    """ANTI-VACUITY AND FALSIFIER for `_deny_pins`, added 2026-10-01.

    An exclusion added to a scanner can make the scan vacuous, and the scan
    would still pass. So the predicate is called here on lines whose verdict is
    known, including the 2 spellings it used to miss.
    """

    _LIVE = [
        f"{REPO}/bench/experiment_11_orchestrator.py:12:CDSFL_WOLFRAM_POLICY=deny",
        f"{REPO}/scripts/run.sh:4:export CDSFL_WOLFRAM_POLICY=deny",
        f'{REPO}/scripts/foo.py:3:env["CDSFL_WOLFRAM_POLICY"] = "deny"',
        f"{REPO}/scripts/foo.py:3:env['CDSFL_WOLFRAM_POLICY'] = 'deny'",
        f'{REPO}/bench/directives/x.json:9:  "CDSFL_WOLFRAM_POLICY": "deny"',
    ]
    # THE FILENAMES ARE CHOSEN, NOT ARBITRARY. `test_line_citations_resolve`
    # scans every tracked file for `path:line` citations and fails on one
    # naming a file that does not exist. These probe strings LOOK like
    # citations, so they are built from basenames its PLACEHOLDER pattern
    # already recognises as illustrative (test.py, example.py). Renaming
    # them to anything else takes that guard red for a file nobody touched.
    _IGNORED = [
        f"{REPO}/.claude/worktrees/wf_1/bench/wolfram_standard.py:69:CDSFL_WOLFRAM_POLICY=deny",
        f"{REPO}/.claude/worktrees/wf_1/bench/tests/test.py:74:CDSFL_WOLFRAM_POLICY=deny",
        f"{REPO}/bench/wolfram_standard.py:69:CDSFL_WOLFRAM_POLICY=deny",
        f"{REPO}/bench/tests/example.py:74:CDSFL_WOLFRAM_POLICY=deny",
        f"{REPO}/bench/x.py:1:CDSFL_WOLFRAM_POLICY=enable",
        f"{REPO}/bench/x.py:1:CDSFL_WOLFRAM_POLICY=serial",
        f"{REPO}/scripts/notes.py:8:# `CDSFL_WOLFRAM_POLICY`: deny is retained and selectable",
    ]

    def test_it_catches_every_spelling_a_committer_would_use(self):
        missed = [ln for ln in self._LIVE if not _deny_pins([ln])]
        assert missed == [], (
            "a live pin to deny evaded the guard; the founder's enablement "
            "ruling could be inverted in silence:\n" + "\n".join(missed))

    def test_it_ignores_transient_copies_exempt_files_and_other_policies(self):
        wrong = [ln for ln in self._IGNORED if _deny_pins([ln])]
        assert wrong == [], (
            "a false hit makes the guard's output start being ignored:\n"
            + "\n".join(wrong))

    def test_the_two_spellings_the_old_pattern_missed_are_the_reason_it_widened(self):
        """FALSIFIER: revert the widening and exactly these 2 lines escape."""
        narrow = re.compile(r"CDSFL_WOLFRAM_POLICY\s*[=:]\s*[\"']?deny")
        escaped = [ln for ln in self._LIVE if not narrow.search(ln)]
        assert len(escaped) == 3, escaped          # 2 quoted forms + the JSON pair
        assert all(_DENY_PIN.search(ln) for ln in escaped), (
            "the widening does not actually recover the lines it was made for")
