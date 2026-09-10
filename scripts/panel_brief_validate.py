#!/usr/bin/env python3
"""Refuse a panel brief that does not meet the founder's 2026-09-09 format ruling.

WHY THIS EXISTS, measured rather than asserted. Across the 49 briefs archived
before 2026-09-09: 0 required a seat to use the mathematical model as an
instrument, 8 required a fix, and 2 required the fix to be tested. They were
hand-written markdown read straight off disk -- no template, no schema, no
validation, no test. The founder's ruling names exactly those gaps.

WHY IT REFUSES RATHER THAN WARNS. 3 of the 5 panel seats are PAID. A defective
brief costs money and returns something unusable, and the project's own record
holds a case where a briefing defect broke 2 seats and cost a re-dispatch. A
warning printed above a dispatch that proceeds anyway is a guard that cannot fail.

WHAT IT DELIBERATELY DOES NOT CHECK. The formal schema, no-compelled-convergence,
the additive standard and the one-shot notice reach every seat through the
dispatcher's SYSTEM string by construction and are covered by
bench/tests/test_panel_runs_under_the_schema_2026-09-07.py. Checking them here
would be a second representation with no comparator -- the shape this project
keeps getting caught by.

THE CHECKS ARE DELIBERATELY SHALLOW. They ask whether the brief SAYS the required
things, which a keyword test can answer. Whether it says them WELL is a judgement
no validator should pretend to make, and the template exists to carry that.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TEMPLATE = REPO / "bench" / "directives" / "universal" / "panel_brief_template.md"

#: The instruments a brief may name to satisfy the model-as-instrument clause.
#: `nu` is matched with word boundaries so it does not fire inside "number".
INSTRUMENTS = (r"\bgamma\b", r"\brho\b", r"\bS_k\b", r"\bsigma\b", r"\bnu\b",
               r"two-sided gate", r"\bseverity\b", r"\bDuane\b", r"\bWilson\b")

CHECKS = (
    ("names the artefact under review",
     (r"\b[\w./-]+\.(?:py|md|json|toml|sh)\b",),
     "name the file or files under review by path, so the seat reads the same thing you did"),
    ("requires the harness to be USED",
     (r"\brun\b", r"\bexecute\b", r"\bexecuting\b"),
     "say the seat must RUN things, not describe them"),
    ("names a mathematical instrument",
     INSTRUMENTS,
     "name at least 1 of gamma, rho, S_k, sigma, nu, the two-sided gate, severity, "
     "Duane or Wilson, and say what it should tell the seat about this question"),
    ("requires a fix, not only a finding",
     (r"\bfix\b", r"\brepair\b", r"\bremedy\b"),
     "require a fix; a finding on its own is half an answer"),
    ("requires the fix to be TESTED",
     (r"falsifier", r"\btest\b\w*\s+(?:the|your|that)\s+fix", r"\bexecuted?\b.*\bfalsifier\b"),
     "require a runnable falsifier that the seat has EXECUTED, and its output"),
    ("asks what would refute the seat",
     (r"refut", r"overturn", r"\bfalsif\w*\s+your\b", r"what would change your"),
     "require each seat to state what evidence would overturn its own answer"),
    # TIGHTENED 2026-09-09 by its own test. The first version accepted a bare
    # `## Output` heading with nothing under it, so a brief could satisfy the
    # check while specifying no fields at all -- a heading is not a shape. It now
    # requires at least 1 named FIELD, which is what the check is actually for.
    ("states a termination criterion",
     (r"terminat", r"\bstop when\b", r"diminishing returns"),
     "say when to stop; diminishing returns is this project's own criterion"),
)



def _section(text: str, heading_pattern: str) -> str | None:
    """The body of the first section whose heading matches, or None.

    SECTION SCOPING ADDED 2026-09-09, by this module's own test. The output check
    searched the WHOLE document for a field name, so a brief mentioning "verdict"
    anywhere -- in passing, in another section -- satisfied it while specifying no
    output shape at all. Removing the entire output specification from a compliant
    fixture left the check green, which is a check that cannot fail in the
    direction it exists to check. A document-wide search is the wrong instrument
    for a question about one section.
    """
    lines = text.splitlines()
    start = None
    level = 0
    for i, line in enumerate(lines):
        m = re.match(r"^(#+)\s*(.*)$", line)
        if m and re.search(heading_pattern, m.group(2), re.I):
            start, level = i + 1, len(m.group(1))
            break
    if start is None:
        return None
    body = []
    for line in lines[start:]:
        m = re.match(r"^(#+)\s", line)
        if m and len(m.group(1)) <= level:
            break
        body.append(line)
    return "\n".join(body)

#: A brief may DECLARE the figures it quotes, so they can be re-executed rather
#: than trusted. One per line, anywhere in the brief:
#:
#:     <!-- figure: <label> | <script path, repo-relative> | <exact string> -->
#:
#: The validator runs the script and requires the exact string in its output.
#:
#: WHY THIS EXISTS. On 2026-09-10 the round-4 brief stated "gamma is 0.451" when
#: the value was 0.415413. `GAMMA_BANDS` puts the boundary at 0.45, so the brief
#: upgraded the convergence evidence by 1 band -- in a brief whose subject was 9
#: figures that were wrong. BOTH SEATS caught it independently and each raised it
#: as their strongest disagreement with the brief. The 7 checks above have no way
#: to see a wrong number: they ask whether the brief SAYS the required things.
#: `measured-rate-travels-with-its-script` covered notes, commit messages and code
#: comments, and had never covered the one artefact that instructs the panel.
FIGURE = re.compile(
    r"<!--\s*figure:\s*(?P<label>[^|]+?)\s*\|\s*(?P<script>[^|]+?)\s*\|\s*"
    r"(?P<value>[^>]+?)\s*-->")

#: Anything that OPENS like a figure declaration, parseable or not. Compared
#: against FIGURE's matches so a MALFORMED declaration refuses instead of
#: silently escaping the check (panel round 7, 2026-09-10, demonstrated by
#: execution): `<!-- figure: g | s.py -->` with its value field missing matched
#: nothing, was skipped, and the brief PASSED with zero checks run. Opt-in
#: means an ABSENT declaration passes -- not a broken one.
FIGURE_OPENER = re.compile(r"<!--\s*figure:")

#: A character that CONTINUES a word or a number on either side of a match.
_TIGHT = re.compile(r"[0-9A-Za-z_]")

#: Characters that bind a number into a LARGER number when they sit between
#: digits: the thousands comma, the time colon, the ratio slash. `1,234` must
#: not satisfy a declared `234`; `entries, 234` must still satisfy it, so the
#: rule is conditioned on a digit sitting on the far side, not on the
#: separator alone.
_GROUPERS = ",:/"


def _figure_token_found(want: str, haystack: str) -> bool:
    """True iff `want` occurs in `haystack` as a whole figure.

    WHY THIS REPLACED A CHARACTER CLASS (2026-09-10, panel round 7, found by
    execution and reproduced before acting). The round-6 repair expressed
    "whole token" as `(?<![0-9A-Za-z.\\-])` ... `(?![0-9A-Za-z.\\-])`, which is
    wrong in BOTH directions, and both were measured:

      * IT STILL PASSED WRONG NUMBERS. `,` is not in that class, so a declared
        `234` reproduced against a script printing `entries = 1,234` -- the
        round-6 defect exactly, one separator over, and off by a factor of 5.
        A printed `elapsed 12:345` satisfied a declared `345` the same way.
      * IT REFUSED RIGHT NUMBERS. `.` is in that class unconditionally, so a
        script printing `gamma is 0.294998.` -- the figure at the end of a
        sentence -- could not be declared at all. A guard that refuses a
        correct brief is bypassed, which costs more than the defect it caught.

    The distinction a fixed character class cannot draw is CONTEXT-SENSITIVE:
    a `.` or a `,` continues a number only when a digit sits on the far side
    of it. So each occurrence is judged by looking one character PAST the
    delimiter, rather than by membership in a set.

    Nothing is removed: every input the round-6 rule refused is still refused
    (see bench/tests/test_declared_figure_token_boundary_2026-09-10.py, which
    re-runs the round-6 table against this predicate directly).
    """
    if not want:
        return False
    n = len(haystack)
    for m in re.finditer(re.escape(want), haystack):
        i, j = m.start(), m.end()
        before = haystack[i - 1] if i else ""
        after = haystack[j] if j < n else ""
        # --- left boundary -------------------------------------------------
        if before:
            if _TIGHT.match(before):
                continue                  # inside a word or a number
            if before == "-":
                continue                  # a sign: 0.25 must not ride on -0.25
            if before == "." and not want[:1].isalpha():
                continue                  # inside a decimal: 294998 in 0.294998
            if before in _GROUPERS and i >= 2 and haystack[i - 2].isdigit():
                continue                  # inside a grouped number: 234 in 1,234
        # --- right boundary ------------------------------------------------
        if after:
            nxt = haystack[j + 1] if j + 1 < n else ""
            if _TIGHT.match(after):
                continue                  # 0.29 must not ride on 0.294998
            if after == "-":
                continue                  # 2026 must not ride on 2026-09-10
            if after == "." and nxt.isdigit():
                continue                  # the decimal continues
            if after in _GROUPERS and nxt.isdigit():
                continue                  # 1 must not ride on 1,234
        return True
    return False


def check_declared_figures(text: str, repo: Path = REPO,
                           timeout: int = 600) -> list[str]:
    """Re-execute every declared figure. Empty list means all reproduced.

    A brief that declares NOTHING passes -- the mechanism is opt-in, because
    retrofitting it to 49 archived briefs would refuse them all for a reason
    unrelated to why they are being validated. A brief that declares a figure and
    gets it wrong is refused, which is the case that cost this project a panel
    round.
    """
    problems: list[str] = []
    matches = list(FIGURE.finditer(text))
    opened = len(FIGURE_OPENER.findall(text))
    if opened != len(matches):
        problems.append(
            f"{opened - len(matches)} figure declaration(s) open with "
            f"'<!-- figure:' but do not parse as "
            f"'<!-- figure: <label> | <script> | <value> -->'. A declaration "
            f"that announces itself and then escapes checking is worse than "
            f"none: fix the comment or remove it")
    for m in matches:
        label = m.group("label")
        rel = m.group("script")
        want = m.group("value")
        # THE SCRIPT MUST LIVE INSIDE THE REPOSITORY (panel round 7,
        # 2026-09-10, demonstrated by execution). `repo / rel` with rel
        # starting `../` -- or absolute, which pathlib joins by REPLACING the
        # left side -- executed an arbitrary script OUTSIDE the tree and
        # accepted its output as evidence. A figure is a committed measurement
        # only if it re-executes from the repository; refuse BEFORE running.
        script = (repo / rel).resolve()
        if not script.is_relative_to(Path(repo).resolve()):
            problems.append(
                f"declared figure {label!r}: the script path {rel!r} escapes "
                f"the repository, so the figure is not a committed measurement "
                f"and was not executed")
            continue
        if not script.is_file():
            problems.append(
                f"declared figure {label!r}: the script {rel} does not exist, so "
                f"the figure cannot be re-executed")
            continue
        try:
            r = subprocess.run([sys.executable, str(script)], cwd=repo,
                               capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            problems.append(f"declared figure {label!r}: {rel} did not finish in "
                            f"{timeout}s")
            continue
        if r.returncode != 0:
            problems.append(
                f"declared figure {label!r}: {rel} exited {r.returncode} and "
                f"produced no figure. A cited script that does not run is the "
                f"6.2 defect")
            continue
        # ORDER IS LOAD-BEARING (2026-09-10). This check sat FIRST and took 2
        # existing tests red: a declared `1` against a MISSING script reported
        # "fewer than 3 significant characters" instead of "the script does not
        # exist". A guard must report the most fundamental failure it found, or
        # it sends the reader to fix the wrong thing. Infrastructure first,
        # then the figure.
        # A DECLARED FIGURE MUST BE DISTINCTIVE (2026-09-10, fable's residual in
        # panel round 6, confirmed by execution). Whole-token matching still
        # accepted a declared `1`, because `1` is a genuine token in "pass 1:".
        # fable named the remedy: require at least 3 significant characters, so a
        # figure is specific enough that appearing in the output means something.
        # A count like `84` must therefore be declared with its context -- the
        # script should print `entries = 84`, and the brief declare `entries = 84`.
        if len(re.sub(r"[^0-9A-Za-z]", "", want)) < 3:
            problems.append(
                f"declared figure {label!r}: {want!r} carries fewer than 3 "
                f"significant characters, so finding it in the output proves "
                f"nothing. Declare it with its label, e.g. 'gamma = 0.3'")
            continue
        # WHOLE-TOKEN, NOT SUBSTRING (2026-09-10, panel round 6; both seats found it
        # independently and CC1 reproduced it). `want not in output` accepted a
        # declared `0.29` against a printed `0.294998`, and a declared `1` rode on
        # the words "pass 1:". Measured across 7 cases the substring form scored
        # 4 of 7, Wilson [25.05%, 84.18%] -- a guard built to catch a wrong number
        # that passes wrong numbers.
        #
        # THE FIRST REPAIR WAS A FIXED CHARACTER CLASS AND IT WAS WRONG BOTH WAYS
        # (corrected 2026-09-10, panel round 7, by execution). It read "a token is
        # delimited by anything that is not a digit, a letter, a dot or a minus
        # sign", which let a declared `234` reproduce against a printed `1,234`
        # -- the round-6 defect one separator over, wrong by a factor of 5 -- and
        # refused a correct `0.294998` against a printed `gamma is 0.294998.`
        # because the sentence ended. The boundary is context-sensitive and is now
        # decided per occurrence in `_figure_token_found` above.
        #
        # THE "8 of 8" SCORE FOR THE ROUND-6 REPAIR OVERSTATES ITS SUPPORT. Of the
        # 8 cases in bench/tests/test_panel_brief_format_2026-09-09.py, 4 (`0.2`,
        # `0.4`, `1`, `9`) are refused by the 3-significant-character rule below
        # and never reach the token rule, and 2 (`0.451`, `0.415413`) are absent
        # from the output and would be refused by a plain substring test. Exactly
        # 1 case, `0.29`, exercises the boundary: 1 of 1, Wilson [20.66%, 100.00%].
        # The cases that were missing are in
        # bench/tests/test_declared_figure_token_boundary_2026-09-10.py.
        # THE TWO STREAMS ARE JOINED WITH A NEWLINE, not concatenated (2026-09-10,
        # panel round 7, demonstrated). `r.stdout + r.stderr` splices the last
        # character of stdout onto the first of stderr, synthesising a token
        # neither stream printed: a script writing `rate = 0.2` to stdout with no
        # trailing newline and `9 done` to stderr satisfied a declared
        # `rate = 0.29`. A figure must be found in output that was actually
        # emitted, not in the seam between two streams.
        if not _figure_token_found(want, r.stdout + "\n" + r.stderr):
            problems.append(
                f"declared figure {label!r}: the brief says {want!r} and {rel} "
                f"does not print it. A number typed into a brief is a claim "
                f"about evidence, not evidence")
    return problems


def validate(text: str) -> list[str]:
    """Return a list of failures. Empty means the brief is dispatchable."""
    low = text.lower()
    problems: list[str] = []
    if len(text.strip()) < 400:
        problems.append(
            f"the brief is {len(text.strip())} characters, which is too short to "
            f"carry the required sections; an under-specified brief is the "
            f"'simple open ended prompt' the founder's ruling forbids")
    for label, patterns, remedy in CHECKS:
        if not any(re.search(p, low, re.M) for p in patterns):
            problems.append(f"{label}: NOT FOUND — {remedy}")

    # The output check is SECTION SCOPED, unlike the rest. See _section().
    body = _section(text, r"output|deliverable|what to return")
    if body is None:
        problems.append(
            "states the output shape: NOT FOUND — there is no output section at all; "
            "state field by field what the seat must return")
    elif not re.search(r"\bverdict\b|\bfalsifier\b|\breasoning\b|\bdisagreement\b",
                       body, re.I):
        problems.append(
            "states the output shape: NOT FOUND — the output section names no fields. "
            "A heading with nothing under it is not an output shape.")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate a CDSFL panel brief.")
    # `nargs="?"` is DELIBERATE, added 2026-09-09 after the suite refused this
    # script. With a required positional, argparse reports the missing argument
    # BEFORE it reaches an unrecognised flag, so `--fix-timestamps` -- a flag this
    # script does not have -- produced "the following arguments are required"
    # rather than "unrecognized arguments". The repository guard on that exists
    # because a script that silently accepts a retired flag and does nothing with
    # it is the 118-day no-op again. Making the positional optional lets argparse
    # reach the unknown-flag check; the requirement is then enforced below, with a
    # clearer message than argparse's own.
    ap.add_argument("brief", type=Path, nargs="?", help="path to BRIEF.md")
    ap.add_argument("--quiet", action="store_true")
    a = ap.parse_args()
    if a.brief is None:
        ap.error("a path to a BRIEF.md is required")
    if not a.brief.is_file():
        print(f"panel-brief: {a.brief} does not exist", file=sys.stderr)
        return 2
    text = a.brief.read_text(encoding="utf-8", errors="replace")
    problems = validate(text)
    # Declared figures are RE-EXECUTED, not trusted. See check_declared_figures.
    problems += check_declared_figures(text)
    if problems:
        print(f"panel-brief: REFUSED — {a.brief} fails {len(problems)} required check(s):",
              file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(f"\n  The format is {TEMPLATE.relative_to(REPO)}.", file=sys.stderr)
        print("  3 of the 5 seats are PAID; a defective brief costs money and "
              "returns nothing usable.", file=sys.stderr)
        return 1
    if not a.quiet:
        print(f"panel-brief: {a.brief.name} carries all {len(CHECKS)} required sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
