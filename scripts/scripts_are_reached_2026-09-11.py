#!/usr/bin/env python3
"""Which committed scripts are reached by nothing at all?

THE STANDARD THIS MEASURES, verbatim: *"Symmetrically, an addition that nothing
reaches is not additive either: every new flag, gate, subcommand or entry point
must be wired to a caller and executed by a test."* The project already ratchets
config fields nothing reads. Scripts had no such check.

MEASURED 2026-09-11: **119 of 122 scripts are reached -- 97.5410%, Wilson
[93.0192%, 99.1602%], Clopper-Pearson [92.9818%, 99.4900%]**, both intervals
cross-checked by 2 tools.

PINNED TO A COMMIT WAS STILL NOT ENOUGH, which is the 4th statement of this
figure in a day. 114 of 120, 115 of 121, 116 of 122, 118 of 122, now 119 of 122 --
the first 3 moved because scripts were ADDED, and this one moved because 2
orphans were WIRED. A figure over a set that is being actively worked on is a
snapshot of the moment it was taken, and no amount of dating or pinning changes
that. Re-run the producer.

3 OF THE 6 ORPHANS WERE WIRED RATHER THAN RULED ON, 2026-09-11. Wiring is not the
half that needs the founder: the removal clause demands a committed measurement
before anything is taken away, while "an addition that nothing reaches is not
additive either" is discharged by giving a script a caller.
`bench/tests/test_parked_measurements_still_run_2026-09-11.py` EXECUTES all 3, and
all 3 still work. The other 3 write files, or spawn a script that writes, so they
stay parked and unrun -- running the scripts directory as a survey once overwrote a preserved
archive, and that instruction stands.

THE RATCHET IS THE DURABLE CLAIM. The percentage is a snapshot of one revision;
the set of 6 named scripts is what may not grow. Re-run the producer rather than
quoting either., both intervals
cross-checked by 2 tools (statsmodels against a 50-digit mpmath Wilson closed
form; statsmodels `beta` against `scipy.stats.beta` for Clopper-Pearson).

THE RATCHET WAS LOWERED RATHER THAN LEFT SLACK, 2026-09-11. 2 of the 8 came off
because the reason they were unreached turned out to be a defect with a fix, not
a disposition awaiting a ruling: their FIGURES had travelled without them.
`measure_toolonly_status_without_falsifier.py` produced "118 of 864 ... 13.66%,
Wilson [11.53%, 16.11%]", quoted in 2 documents that named no producer, and its
own docstring calls that the fourth repeat of the same omission.
`v2_vs_v3_runner_2026-09-10.py` produced the 153-definition comparison quoted in
task 8.2 and carries `measured-rate-travels-with-its-script` in its docstring
while nothing outside an archival panel record named it. Naming the producer
discharges the founder's ruling AND wires the script; the 2 are the same act.

THE OTHER 6 WERE CHECKED THE SAME WAY AND CANNOT BE WIRED BY CITATION. 2 carry no
figure at all in their docstrings. For the rest the apparent matches were an
extractor artefact: `3660816` in `priority_starvation_simulation.py` is a COMMIT
HASH, not a measurement, and short tokens like "08" matched dates. Wiring on any
of those would have been an addition made to move a number, which is the thing
this ratchet exists to detect. The 8 that are not
are named in `UNREACHED` below.

A FIRST PASS SAID 5, AND THE DIFFERENCE IS THE ARCHIVAL EXCLUSION. Counting
mentions inside mirrored panel diffs made 3 more scripts look reached -- so the
flattering number came from the review record being preserved that morning, not
from anything calling them. A measurement that improves when you file your
paperwork is measuring the filing.

REACHED MEANS 3 DIFFERENT THINGS AND ALL 3 COUNT, because a script can be
legitimate without having a caller:

  * something CALLS it -- a test, another script, a hook;
  * a NOTE CITES it as the producer of a figure, which
    `measured-rate-travels-with-its-script` requires and which makes an
    uncalled script load-bearing rather than dead;
  * it is named in a canonical document as a command a reader runs.

A MIRRORED PANEL DIFF IS NOT A CITATION, and excluding it is the difference
between a real answer and a flattering one. All 5 unreached scripts are mentioned
in `experimental_notes/evidence/*/seat_proposals.diff` -- archival copies of what
a reviewing model proposed, committed on 2026-09-11. Counting those would have
made every one of them look reached the moment the review record was preserved,
which is a measurement reporting on its own filing.

THIS SCRIPT DECIDES NOTHING. Whether an unreached script is wired or retired is a
disposition, and the additive standard's removal clause requires a committed
measurement that something better replaces it -- which is exactly what is absent
for these 5. They are recorded for the founder's ruling, as `update_drift` was.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Trees whose contents are ARCHIVAL COPIES rather than live references.
ARCHIVAL = ("experimental_notes/evidence/",)

#: Files that carry a ROLL-CALL of unreached scripts. Only the roll-call LINES
#: are ignored in these files, never the whole file: the test genuinely runs this
#: script, and excluding it wholesale made this script itself read as unreached.
#:
#: THIS INSTRUMENT INVALIDATED ITSELF BY BEING COMMITTED. `UNREACHED` below lists
#: 8 script paths, and `unreached()` asks whether any tracked file mentions a
#: script -- so the moment this file was committed, its own list declared all 8
#: reached and the figure jumped from 111 of 119 to 120 of 120. A ratchet whose
#: record of the orphans makes them non-orphans measures nothing at all, and the
#: only reason it was caught within 8 minutes is that `--check` was re-run
#: against the figure that had just been published.
#:
#: The same trap is in the parked note and in this module's own docstring, which
#: quote the 8 paths so a reader knows which they are.
#:
#: THE FIRST FIX OVER-CORRECTED, and that is why the filter is line-wise. It
#: excluded 3 WHOLE FILES, one of them the test -- which carries no roll-call
#: line at all and genuinely runs this script. Throwing the file away threw away
#: a real caller, and the count went to 111 of 120 with THIS script as the 9th
#: orphan: the instrument reported itself unreached because the fix for it
#: reading everything as reached had deleted its only caller. Ignoring the
#: roll-call LINES leaves every other line in those files counting, which is
#: what `_ROLL_CALL` does, and the count returns to 112 of 120.
#:
#: `test_every_self_referential_file_carries_a_roll_call` holds the list to files
#: that actually have one, so a name cannot be added here to make an
#: inconvenient orphan disappear.
#: THIS MODULE, excluded WHOLLY rather than line-wise, and the distinction is the
#: whole lesson. It never CALLS any script it measures, so it can hold no real
#: reference to lose -- unlike the test, whose wholesale exclusion on the first
#: attempt deleted a genuine caller and made this file report itself unreached.
#:
#: LINE-WISE WAS NOT ENOUGH HERE, FOUND 2026-09-11 BY IT HAPPENING. The docstring
#: above explains why `priority_starvation_simulation.py` cannot be wired -- and
#: writing that sentence made the script read as REACHED, because a prose mention
#: is not a roll-call line. The record of an orphan declaring it a non-orphan, for
#: the third time in one morning, now caused by the paragraph explaining the first
#: two. A file whose job is to name orphans can never be evidence about them.
INSTRUMENT = (
    "scripts/scripts_are_reached_2026-09-11.py",
    "bench/tests/test_scripts_are_reached_2026-09-11.py",
    "experimental_notes/PARKED_FOR_THE_FOUNDER.md",
)

#: Retained name for the module itself, which is the narrowest member.
DIAGNOSTIC = ("scripts/scripts_are_reached_2026-09-11.py",)

#: Files that carry a ROLL-CALL but may also hold real references, so only the
#: roll-call LINES are dropped. The parked note cites producers as well as listing
#: orphans, so excluding it wholly would lose those citations.
SELF_REFERENTIAL = (
    "experimental_notes/PARKED_FOR_THE_FOUNDER.md",
)

#: Measured 2026-09-11. A RATCHET: it may fall, never rise. Raising it means a
#: new script exists that nothing calls, nothing cites and no document names.
UNREACHED = (
    "scripts/quarantine_to_candidate.py",
    "scripts/readjudicate_pairs.py",
    "scripts/scope_remaining_adjudication_and_materiality.py",
)


#: A line that is nothing but one script path, in any form a roll call is
#: plausibly written in: `"scripts/x.py",`, a bare indented path, or a markdown
#: bullet or numbered item, with or without backticks.
#:
#: THE LIST FORMS WERE IN THE DOCSTRING AND NOT IN THE PATTERN. Panel round 15,
#: both seats: the old comment claimed "quotes, comma or list marker" and the
#: test docstring said "in a fenced list", while `- scripts/x.py`, `* ...`,
#: `1. ...` and `` - `...` `` all returned False. The roll call worked only
#: because `PARKED_FOR_THE_FOUNDER.md` happens to use bare indented paths;
#: reformatting that note as a bullet list would have made every orphan read as
#: reached. A documented-but-unimplemented form is the same false zero as an
#: over-anchored pattern, pointing the other way.
_ROLL_CALL = re.compile(
    r'(?:[-*+]\s+|\d+[.)]\s+)?["\'`]?(scripts/[\w./-]+\.py)["\'`]?,?')


def _tracked() -> list[str]:
    r = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                       text=True)
    if r.returncode != 0:
        raise SystemExit("not a git checkout, so reachability cannot be decided; "
                         "refusing rather than reporting everything unreached")
    return r.stdout.split()


def vouches(voucher: str, target: str) -> bool:
    """May a mention of `target` inside `voucher` count as reaching it?

    AN INSTRUMENT FILE MAY ONLY VOUCH FOR ANOTHER INSTRUMENT FILE, and the
    asymmetry is the whole rule. Writing ABOUT an orphan is not reaching it: 4
    times in one morning a sentence explaining why a script could not be wired
    made that script read as reached -- first the roll call itself, then this
    module's docstring, then the test's. Prose is not a caller.

    The exception runs the other way. The test genuinely RUNS this module, and
    deleting that reference is precisely what made the module report ITSELF
    unreached on the first attempt at this fix.

    A SEPARATE FUNCTION BECAUSE IT COULD NOT OTHERWISE BE TESTED. Inlined, the
    asymmetry was invisible to every test: mutating it to the symmetric form left
    all 13 green, because `CDSFL_OUTCOMES_LOG.md` happens to name this module and
    an ordinary document vouches for it regardless. The test that was meant to
    prove the asymmetry was passing for an unrelated reason -- which is the thing
    this project keeps finding, and it does not stop being that when the
    instrument in question is the one built to find it.
    """
    if voucher == target:
        return False
    return not (voucher in INSTRUMENT and target not in INSTRUMENT)


def unreached() -> list[str]:
    """Scripts that nothing calls, nothing cites and no document names."""
    tracked = _tracked()
    scripts = [f for f in tracked
               if f.startswith("scripts/") and f.endswith(".py")]
    bodies = {}
    for f in tracked:
        if any(f.startswith(a) for a in ARCHIVAL):
            continue
        if not f.endswith((".py", ".sh", ".md", ".toml", ".json", ".txt")) \
                and f != "hooks/pre-commit":
            continue
        try:
            text = (REPO / f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if f in SELF_REFERENTIAL:
            # Drop only the roll-call lines -- a line whose whole content is one
            # script path, with optional quotes, comma or list marker. Everything
            # else in the file, including a citation to a producer, still counts.
            text = "\n".join(
                ln for ln in text.splitlines()
                if not _ROLL_CALL.fullmatch(ln.strip()))
        bodies[f] = text
    out = []
    for s in scripts:
        stem = pathlib.Path(s).name
        module = s[:-3].replace("/", ".")
        for g, t in bodies.items():
            if not vouches(g, s):
                continue
            if stem in t or module in t:
                break
        else:
            out.append(s)
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="exit non-zero if the unreached set has grown")
    a = ap.parse_args()

    now = unreached()
    tracked = [f for f in _tracked()
               if f.startswith("scripts/") and f.endswith(".py")]
    n, k = len(tracked), len(tracked) - len(now)
    print(f"scripts/: {n}")
    print(f"  reached by a caller, a citation or a document: {k}")
    print(f"  reached by NOTHING                           : {len(now)}")
    for s in now:
        print(f"      {s}")
    if n:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(k, n, method="wilson")
        lo_b, hi_b = proportion_confint(k, n, method="beta")
        print(f"\n  reached: {k}/{n} = {k / n:.4%}")
        print(f"    Wilson 95%          : [{lo:.4%}, {hi:.4%}]")
        print(f"    Clopper-Pearson 95% : [{lo_b:.4%}, {hi_b:.4%}]")

    grew = [s for s in now if s not in UNREACHED]
    gone = [s for s in UNREACHED if s not in now]
    if gone:
        print(f"\n  {len(gone)} previously-unreached script(s) are now reached; "
              f"lower the ratchet: {gone}")
    if grew:
        print(f"\n  NEW unreached script(s): {grew}")
    if a.check:
        return 1 if grew else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
