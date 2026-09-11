#!/usr/bin/env python3
"""Which committed scripts are reached by nothing at all?

THE STANDARD THIS MEASURES, verbatim: *"Symmetrically, an addition that nothing
reaches is not additive either: every new flag, gate, subcommand or entry point
must be wired to a caller and executed by a test."* The project already ratchets
config fields nothing reads. Scripts had no such check.

MEASURED 2026-09-11: **111 of 119 scripts are reached -- 93.2773%, Wilson
[87.2935%, 96.5544%], Clopper-Pearson [87.1830%, 97.0531%]**. The 8 that are not
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
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]

#: Trees whose contents are ARCHIVAL COPIES rather than live references.
ARCHIVAL = ("experimental_notes/evidence/",)

#: Measured 2026-09-11. A RATCHET: it may fall, never rise. Raising it means a
#: new script exists that nothing calls, nothing cites and no document names.
UNREACHED = (
    "scripts/inventory_2026_09_06.py",
    "scripts/measure_round_zero_irreducible_escalations.py",
    "scripts/measure_toolonly_status_without_falsifier.py",
    "scripts/priority_starvation_simulation.py",
    "scripts/quarantine_to_candidate.py",
    "scripts/readjudicate_pairs.py",
    "scripts/scope_remaining_adjudication_and_materiality.py",
    "scripts/v2_vs_v3_runner_2026-09-10.py",
)


def _tracked() -> list[str]:
    r = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True,
                       text=True)
    if r.returncode != 0:
        raise SystemExit("not a git checkout, so reachability cannot be decided; "
                         "refusing rather than reporting everything unreached")
    return r.stdout.split()


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
            bodies[f] = (REPO / f).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
    out = []
    for s in scripts:
        stem = pathlib.Path(s).name
        module = s[:-3].replace("/", ".")
        if any(g != s and (stem in t or module in t) for g, t in bodies.items()):
            continue
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
