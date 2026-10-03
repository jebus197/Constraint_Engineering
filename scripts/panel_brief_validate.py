#!/usr/bin/env python3
"""Refuse a panel brief that does not meet the founder's 2026-09-09 format ruling.

WHY THIS EXISTS, measured rather than asserted. Across the 49 briefs archived
before 2026-09-09: 0 required a seat to use the mathematical model as an
instrument, 8 required a fix, and 2 required the fix to be tested. They were
hand-written markdown read straight off disk -- no template, no schema, no
validation, no test. The founder's ruling names exactly those gaps.

ANNOTATED 2026-09-17: no committed script prints the 8 and the 2 above; they are
a reader's count. This module's own lexical checks, run over the same 49 briefs
by `scripts/brief_archive_refusal_rate_2026-09-10.py`, find 43 meeting "requires
a fix" and 27 meeting "requires the fix to be TESTED" -- a looser test than that
reading, so the 2 pairs of figures do not measure the same thing.

WHY IT REFUSES RATHER THAN WARNS. 4 of the 6 panel seats are PAID. A defective
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
import calendar
import re
import subprocess
import sys
import time
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
    # ADDED 2026-09-17 (task P4). THE DELIVERY RULE REACHED BRIEFS BY COPYING.
    # Rounds 5 and 6 returned 0 source files because both seats wrote their
    # fixes into scratch space that `panel_sandbox.teardown` destroyed; round 7's
    # brief told them to write INTO the sandbox repository tree at the real path,
    # and rounds 7 to 15 copied that paragraph forward. Nothing required it: the
    # template never mentioned the sandbox tree, no check here asked where a fix
    # is written, and the round-16 brief of 2026-09-17 carries none of the
    # phrases below. Measured over the post-ruling briefs before enabling:
    # rounds 7 to 15 pass it, and roster_fix, roster_round2, rounds 4, 5, 6, the
    # verification-gap round and round 16 do not. Printed per check by
    # scripts/brief_archive_refusal_rate_2026-09-10.py and held by
    # bench/tests/test_brief_check_breakdown_2026-09-17.py.
    ("requires the fix to be DELIVERED as a file",
     (r"\breal path\b", r"\bsandbox (?:repository )?tree\b",
      r"\bdeliver\w*\s+(?:your\s+|the\s+|each\s+)?fix(?:es)?\s+as\s+a\s+file\b"),
     "require the seat to write its fix INTO the sandbox repository tree at its "
     "real path; a fix left in prose or in scratch space is destroyed at "
     "teardown and is not delivered"),
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


#: A brief may be validated long after dispatch, against an archive that has
#: grown. The historical path below only opens when the brief demonstrably
#: EXISTED at the date it claims: its mtime must sit within this slack of that
#: date's end. A brief written today that carries only past dates fails this
#: gate and is refused exactly as before -- the dodge is closed by evidence,
#: not by trust.
_HISTORICAL_MTIME_SLACK = 48 * 3600

_DATE_RE = re.compile(r"20\d\d-\d\d-\d\d")


def _historical_reproduction(want: str, script: Path, brief_path,
                             text: str, repo: Path, timeout: int):
    """The as-of date iff `want` re-executes against the archive AS OF the
    brief's own date, else None.

    ADDED 2026-09-29 (panel, green-board item 1). The subject of this guard's
    REFUSAL is a brief about to be DISPATCHED: 4 of 6 seats are paid, and a
    wrong number in a dispatched brief costs a round. An ARCHIVED brief is a
    record of what the seats were given, and a declared figure in it is a
    claim about evidence AS OF its date. The round-11 brief's
    `2/640 = 0.3125%` was true on 2026-09-11; the archive then grew to 716
    with the numerator unchanged. Editing the brief falsifies the record;
    exempting archived briefs un-checks them. This does neither: the figure is
    STILL RE-EXECUTED, against the corpus its date names, via the producer's
    own `--as-of`. Nothing is trusted and nothing is exempt:

      * At dispatch the brief's latest date is the dispatch date, and as-of
        that date is today's corpus -- so this path cannot pass a figure the
        strict check would refuse. Not weakened, measured: the dodge test in
        bench/tests/test_declared_figure_as_of_2026-09-29.py writes a brief
        TODAY carrying only past dates and it is refused on the mtime gate.
      * A producer without `--as-of` exits non-zero and the refusal stands
        unchanged (fail closed).
      * A figure that never was true fails as-of its date too, and refuses.
    """
    if brief_path is None:
        return None
    brief_path = Path(brief_path)
    if not brief_path.is_file():
        return None
    dates = _DATE_RE.findall(text)
    if not dates:
        return None
    as_of = max(dates)
    try:
        eod = calendar.timegm(time.strptime(as_of, "%Y-%m-%d")) + 86399
    except ValueError:
        return None
    if brief_path.stat().st_mtime > eod + _HISTORICAL_MTIME_SLACK:
        return None                    # written after the date it claims
    try:
        r = subprocess.run([sys.executable, str(script), "--as-of", as_of],
                           cwd=repo, capture_output=True, text=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None                    # no --as-of support: refusal stands
    if _figure_token_found(want, r.stdout + "\n" + r.stderr):
        return as_of
    return None


def check_declared_figures(text: str, repo: Path = REPO,
                           timeout: int = 600, brief_path=None) -> list[str]:
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
        # 1 case, `0.29`, exercises the boundary: 1 of 1, Wilson [20.65%, 100.00%].
        # (The lower bound is rounded DOWN. cc2 wrote 20.66%, rounding 20.6549% UP,
        # which NARROWS an interval into a stronger claim than the data supports --
        # caught by scripts/wilson_interval_consistency.py, in the very comment
        # correctly warning that '8 of 8' overstates its own support.)
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
            hist = _historical_reproduction(want, script, brief_path, text,
                                            repo, timeout)
            if hist is not None:
                # LOUD BY DESIGN, and never silenced by --quiet: a quiet
                # historical acceptance is how an exemption rots into a hole.
                print(f"panel-brief: HISTORICAL FIGURE — {label!r}: {want!r} "
                      f"does not re-execute against today's archive, but DOES "
                      f"re-execute with --as-of {hist}, the latest date this "
                      f"brief carries, and the brief's mtime is consistent "
                      f"with that date. The record stands as a claim about "
                      f"evidence as of {hist}; re-run {rel} before REUSING "
                      f"this figure.", file=sys.stderr)
                continue
            problems.append(
                f"declared figure {label!r}: the brief says {want!r} and {rel} "
                f"does not print it. A number typed into a brief is a claim "
                f"about evidence, not evidence")
    return problems


#: Paths a brief names, worth checking for currency. Anything else it mentions
#: (a log directory, an archive) is not code that could have moved under it.
_NAMED_PATH_RE = re.compile(
    r"`?((?:scripts|bench|resources|experimental_notes|hooks)/[\w./-]+\.(?:py|sh|md|json))`?")


#: A numeric claim in PROSE. A figure declaration proves that a DECLARED value
#: re-executes; it says nothing about the numbers written in the brief's own
#: sentences, which is where the defect that created task V6 lived.
_NUMERIC_CLAIM = re.compile(r"(?<![\w.])(\d+\.\d+)(?=\D|$)")


def undeclared_figures(text: str) -> list[str]:
    """Numeric claims in the prose that no declared figure backs.

    WHY THIS EXISTS, task V6 reopened 2026-09-11 by BOTH panel seats in round 11,
    independently. `check_declared_figures` re-executes every DECLARED figure and
    refuses when the script does not print it -- which is sound, and which the
    round-4 defect walks straight past. That defect was a WRONG INSTRUMENT VALUE
    TYPED IN PROSE: the brief said `gamma` is 0.451 and it is 0.415413. Declaring
    nothing keeps the gate green. A brief can state a false number beside a true
    declaration and pass every check.

    IT REPORTS, IT DOES NOT REFUSE, and that is deliberate rather than timid. The
    precedent is `check_currency` in this same module: refusing here would refuse
    every brief in the archive -- the 6 most recent carry 1, 2, 4, 7, 8 and 56
    prose claims each -- and this module's own words are that a guard which
    refuses a correct brief teaches people to skip the validator.

    THE BOUNDARY IS CONTEXT-SENSITIVE, and getting it wrong is the round-7 defect
    documented in this file: a trailing `.` ends a sentence and must not be read
    as part of the number, so `0.415413.` is the number `0.415413`. The
    look-behind and look-ahead here allow a `.` only when a digit follows it.
    """
    declared = {m.group("value").strip() for m in FIGURE.finditer(text)}
    dated = bool(re.search(r"20\d\d-\d\d-\d\d", text))
    declared_numbers = set()
    for d in declared:
        declared_numbers |= set(_NUMERIC_CLAIM.findall(d))
    # The declaration comments themselves are not prose.
    prose = FIGURE.sub(" ", text)
    seen, out = set(), []
    for m in _NUMERIC_CLAIM.finditer(prose):
        v = m.group(1)
        if v in declared_numbers or v in seen:
            continue
        seen.add(v)
        out.append(v)
    return out


def check_currency(brief_path, repo: Path = REPO) -> list[str]:
    """Is the brief OLDER than an artefact it tells the panel about?

    TASK A4. The round-2 brief asserted that a question had not been asked. That
    was true when it was written at 20:37 and FALSE by the 21:12 dispatch,
    because a test answering it landed in the 35 minutes between. Both seats
    spent effort on a bolted door. The validator checked the brief's 7 required
    sections and nothing about whether the brief had been overtaken.

    It happened again on 2026-09-10: cc2's round-9 reply opens a disagreement
    with "Section 3.4 is already closed and the brief does not say so."

    WHAT THIS CAN AND CANNOT SEE. It compares modification times. A file the
    brief names that changed AFTER the brief was written is a file the brief may
    describe wrongly -- that is a WARNING, not proof, because an unrelated edit
    to the same file is common. It cannot see a change to something the brief
    describes without naming, and it says so rather than implying coverage.
    """
    brief_path = Path(brief_path)
    if not brief_path.is_file():
        return []
    brief_mtime = brief_path.stat().st_mtime
    text = brief_path.read_text(encoding="utf-8", errors="replace")
    stale = []
    for rel in sorted(set(_NAMED_PATH_RE.findall(text))):
        f = repo / rel
        if not f.is_file():
            continue
        if f.stat().st_mtime > brief_mtime:
            drift = (f.stat().st_mtime - brief_mtime) / 60.0
            stale.append(f"{rel} changed {drift:.1f} min AFTER the brief was written")
    return stale


def validate(text: str) -> list[str]:
    """Return a list of failures. Empty means the brief is dispatchable."""
    low = text.lower()
    problems: list[str] = []
    if len(text.strip()) < 400:
        problems.append(
            f"the brief is {len(text.strip())} characters, which is too short to "
            f"carry the required sections; an under-specified brief is the "
            f"'simple open ended prompt' the founder's ruling forbids")
    # re.I, ADDED 2026-09-17 (found under task A4): the brief is lowercased above,
    # so the 3 patterns written with capitals -- S_k, Duane and Wilson -- could
    # never match, and a brief naming only 1 of them was refused on the
    # instrument check. Every other pattern is lowercase, so re.I changes nothing
    # else. test_every_check_pattern_can_match_2026-09-17.py holds it.
    for label, patterns, remedy in CHECKS:
        if not any(re.search(p, low, re.M | re.I) for p in patterns):
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

    # DISAGREEMENT IS A FIELD, NOT A HOPE, and it must be named in the OUTPUT
    # section specifically.
    #
    # MEASURED 2026-10-02 on the round this check exists for. The blind brief of
    # `integrity_advisory_2026-10-02` made it a mandatory output field and BOTH
    # seats carried a disagreement. The STAR brief of
    # `integrity_advisory_r2_2026-10-02` replaced the output shape with
    # RESOLUTION / WHO WAS RIGHT / EVIDENCE / FIX / WHAT WOULD REFUTE THIS /
    # CONFIDENCE and dropped the field; it asked for disagreement only as prose
    # in the termination section. One of the 2 seats then omitted it, and
    # `TestP5DisagreementIsPreserved` caught the round.
    #
    # WHY THE SCOPE MATTERS, and the first version of this check failed on it. A
    # whole-document regex is defeated by a star brief, which embeds the previous
    # round's replies VERBATIM. Measured on the defective brief itself: the word
    # appears on 7 of its lines, so a document-wide check PASSES it, while its
    # OUTPUT SECTION names no disagreement at all. Section scoping is the only
    # form that separates the two.
    #
    # WHAT JUSTIFIES THE CHECK: THE TEMPLATE ALREADY REQUIRED THIS. The output
    # section of `bench/directives/universal/panel_brief_template.md` asks for
    # "the strongest disagreement with the brief's own framing" by name, and the
    # template passes this check unchanged. The defect was a validator that
    # permitted divergence from the standard it exists to enforce: 12 of 95
    # archived briefs diverged and nothing caught them.
    #
    # WHAT DOES NOT JUSTIFY IT, AND THE FIRST VERSION OF THIS COMMENT CLAIMED IT
    # DID. Whether naming the field changes what seats return is NOT ESTABLISHED.
    # Measured over 50 rounds carrying both a brief and replies: with the field,
    # 32 of 38 rounds had every seat state a disagreement; without it, 9 of 12.
    # Fisher exact two-sided p = 6.675478e-01 (within-period p = 6.187658e-01),
    # scipy and mpmath agreeing to 1e-9. The 1 round that motivated this check is
    # consistent with chance, and the check is kept for template conformance
    # alone.
    #
    # THE 2 FIGURES THAT STOOD HERE UNTIL 2026-10-02 WERE BOTH FALSE. They said
    # a whole-document scope refuses 78 of 95 (82.1053%) and the section scope
    # "1 of the 3 briefs carrying an output section" -- asserted after looking at
    # 3 briefs by hand. Measured over all 95: section scope refuses 12
    # (12.6316%, Wilson [7.3757%, 20.7921%]), whole-document 15 (15.7895%,
    # Wilson [9.8085%, 24.4296%]). Producer:
    # scripts/brief_disagreement_field_effect_2026-10-02.py.
    #
    # A STAR ROUND IS WHERE THIS MATTERS MOST. Its purpose is to reconcile, so it
    # is the round most able to produce agreement by deference -- which is not
    # evidence, and which this project does not accept as confirmation.
    elif not re.search(r"\bdisagree", body, re.I):
        problems.append(
            "requires the seat to state its DISAGREEMENT: NOT FOUND — name "
            "disagreement as a FIELD in the output section, not as prose "
            "elsewhere. A round that reconciles is the one most likely to "
            "converge by deference, and deference is not evidence.")
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
    # TASK A4: CURRENCY, checked at dispatch and reported as a WARNING.
    # It does not refuse: an unrelated edit to a named file is common and a
    # validator that blocks on it teaches people to skip the validator. It says
    # what moved and by how long, and the dispatcher decides.
    _stale = check_currency(a.brief)
    if _stale and not a.quiet:
        print("panel-brief: CURRENCY WARNING — the brief may have been overtaken:",
              file=sys.stderr)
        for _s in _stale:
            print(f"  {_s}", file=sys.stderr)
        print("  A brief that describes a file as it was is how 2 seats spent a "
              "round on a\n  bolted door (round 2, 2026-09-09). Re-read those "
              "sections before dispatch.", file=sys.stderr)
        print("  It compares MODIFICATION TIMES only: it cannot see a change to "
              "something the\n  brief describes without naming.", file=sys.stderr)
    text = a.brief.read_text(encoding="utf-8", errors="replace")
    # TASK V6, SECOND HALF: numeric claims in the PROSE that nothing re-executes.
    # Reported, never refused -- see `undeclared_figures`.
    _bare = undeclared_figures(text)
    if _bare and not a.quiet:
        print(f"panel-brief: FIGURE COVERAGE — {len(_bare)} numeric claim(s) in "
              f"the prose are backed by no declared figure:", file=sys.stderr)
        print("  " + ", ".join(_bare[:12])
              + (f", ... and {len(_bare) - 12} more" if len(_bare) > 12 else ""),
              file=sys.stderr)
        print("  A declared figure is RE-EXECUTED. A number typed in a sentence "
              "is not,", file=sys.stderr)
        print("  and that is exactly how `gamma is 0.451` reached 2 seats when "
              "it is 0.415413.", file=sys.stderr)
        if not re.search(r"20\d\d-\d\d-\d\d", text):
            # A RATE TRAVELS WITH ITS DATE, the sibling of
            # `measured-rate-travels-with-its-script`. Added 2026-09-11 after a
            # seat pointed out that round 12's brief quoted 67 DONE entries,
            # 5026 test functions and 112 scripts as though current, against a
            # list that was at 80, 5091 and 113 by the time it was read. None of
            # it changed a conclusion; all of it invites the reproduction
            # failures the brief was asking about.
            print("  AND THIS BRIEF CARRIES NO DATE AT ALL. Every count above "
                  "is measured against a\n  corpus that grows; undated, a "
                  "reader cannot tell drift from disagreement.",
                  file=sys.stderr)
    problems = validate(text)
    # Declared figures are RE-EXECUTED, not trusted. See check_declared_figures.
    problems += check_declared_figures(text, brief_path=a.brief)
    if problems:
        print(f"panel-brief: REFUSED — {a.brief} fails {len(problems)} required check(s):",
              file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(f"\n  The format is {TEMPLATE.relative_to(REPO)}.", file=sys.stderr)
        print("  4 of the 6 seats are PAID; a defective brief costs money and "
              "returns nothing usable.", file=sys.stderr)
        return 1
    if not a.quiet:
        print(f"panel-brief: {a.brief.name} carries all {len(CHECKS)} required sections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
