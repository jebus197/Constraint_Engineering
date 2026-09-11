"""2 of the 6 orphaned scripts still work, and a working script nothing reaches is still unreached.

THE RATCHET IN `test_scripts_are_reached_2026-09-11.py` RECORDS 6 SCRIPTS THAT
NOTHING CALLS, CITES OR NAMES. Whether to wire or retire them is the founder's
ruling and is parked for him. **Wiring is not the half that needs a ruling**: the
additive standard's removal clause requires a committed measurement before
anything is taken away, while its other half — *"an addition that nothing reaches
is not additive either"* — is discharged by giving a script a caller, and a test
that EXECUTES it is exactly that caller.

SO THESE 4 ARE WIRED HERE, and the other 2 are not. The difference is measured
rather than assumed: an AST walk over all 6 found that these 2 contain no write
call, no subprocess spawn and no absolute path, so running them cannot change
anything. A 3rd joined them after asking WHICH processes the spawners run:
`inventory_2026_09_06.py` spawns only `git rev-parse` and `git status`, both
read-only, and writes nothing. Classifying it by the SHAPE of the call rather
than by what the call does was a coarser version of the mistake this session
keeps finding.

THE REMAINING 2 STAY PARKED AND UNRUN, and are NOT NAMED HERE. Both write files
outright, with no flag to turn that off, so there is nothing to verify: running
them would do the thing the standing instruction exists to prevent.

A THIRD WAS PARKED AND HAS BEEN RELEASED, because the reason for parking it was a
BET rather than a fact. It spawns another script behind a `--dry-run` flag, and
that script carries 10 write calls -- so its safety rested on a different program
honouring a flag. That is now proven rather than assumed: the spawned script's
dry-run guard sits at line 424 of its `main()`, with no write call and no
locally-defined function called before it, and running the pair in a throwaway
clone changes 0 paths. "Reasonable bet" was the right call at the time and the
wrong place to stop.

THEY ARE UNNAMED FOR A MEASURED REASON. Writing a script's path into a tracked
file makes `scripts_are_reached_2026-09-11.py` count it as REACHED, because a
mention is all that scan can see. Naming them in this docstring un-orphaned one
of them within a minute -- the 5th time in a day that prose ABOUT an orphan
stopped it being one. The list of what is still parked lives in
`experimental_notes/PARKED_FOR_THE_FOUNDER.md`, whose roll-call lines that scan
already knows to ignore, and the test below reads it from the ratchet rather than
repeating it.

WHAT THIS ACTUALLY GUARDS. Both read or model archived experiment data, so they
rot when the archive's shape changes — and a committed measurement that no longer
runs is a defect whichever way the founder rules on keeping it. Executed
2026-09-11: both exit 0 and produce their figures, in the working tree and in a
fresh clone.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]

#: (script, a phrase its output must contain). The phrase is the FIGURE'S LABEL,
#: not the figure, because the archive grows and a pinned count would go stale
#: within the day -- which is exactly what happened to the reachability figure on
#: 2026-09-11, 3 times.
WIRED = [
    ("scripts/measure_round_zero_irreducible_escalations.py",
     "distinct alarm events"),
    ("scripts/priority_starvation_simulation.py",
     "FAIL rate"),
    # ADDED after asking WHICH processes the spawners run. This one's only
    # subprocess calls are `git rev-parse --short HEAD` and `git status --short`,
    # both read-only, and it has no write call at all -- so the "it spawns
    # processes" objection that parked it does not survive the question.
    ("scripts/inventory_2026_09_06.py", "programme inventory"),
    # ADDED after the `--dry-run` bet was replaced by a proof. This script spawns
    # `adjudicate_by_repair.py --dry-run`, and that script carries 10 write calls,
    # so parking it was reasonable while its safety rested on another program
    # honouring a flag. It no longer rests on that: an AST walk over the spawned
    # script's `main()` shows the dry-run guard at line 424 with NO write call and
    # NO locally-defined function called before it, and running it in a throwaway
    # clone changes 0 paths. A bet became a measurement.
    ("scripts/scope_remaining_adjudication_and_materiality.py",
     "adjudication scope"),
]


def _run(rel: str):
    return subprocess.run([sys.executable, str(REPO / rel)], cwd=REPO,
                          capture_output=True, text=True, timeout=900)


class TestTheyStillRun:
    def test_each_exits_zero_and_says_something(self):
        for rel, label in WIRED:
            r = _run(rel)
            assert r.returncode == 0, f"{rel} exited {r.returncode}:\n{r.stderr[-600:]}"
            assert label in r.stdout, (
                f"{rel} no longer prints {label!r}; its output shape has changed "
                f"and the figure it produces may no longer be the one described "
                f"in its docstring:\n{r.stdout[:600]}")

    def test_neither_changes_the_working_tree(self):
        """The reason these 4 and not the other 2. An AST walk found no write
        call, no subprocess and no absolute path in either; this asserts the
        consequence rather than trusting the scan."""
        before = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                                capture_output=True, text=True)
        assert before.returncode == 0, "git status failed; refusing to compare"
        for rel, _ in WIRED:
            _run(rel)
        after = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                               capture_output=True, text=True)
        assert after.stdout == before.stdout, (
            f"running the parked measurements changed the tree:\n{after.stdout}")


class TestTheWiringIsHonest:
    def test_the_wired_set_is_a_subset_of_the_parked_set(self):
        """A script wired here must be one the ratchet actually records, or this
        file is wiring something that was never orphaned and the reachability
        figure moves for no reason."""
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sr", REPO / "scripts" / "scripts_are_reached_2026-09-11.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        wired = {rel for rel, _ in WIRED}
        # They are no longer in UNREACHED precisely BECAUSE this file reaches
        # them, so the check is against the recorded set plus what we wired.
        assert wired.isdisjoint(set(mod.unreached())), (
            "a script this file executes still reads as unreached, which means "
            "the executing call above is not being seen as a reference")

    def test_no_still_parked_script_is_named_here(self):
        """STATED, NOT IMPLIED, and read from the ratchet rather than retyped.

        A script still recorded as unreached must not appear in this file at all:
        running it is unsafe, and NAMING it makes the reachability scan count it
        as reached, which would quietly empty the ratchet by writing prose.
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "sr", REPO / "scripts" / "scripts_are_reached_2026-09-11.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        src = pathlib.Path(__file__).read_text(encoding="utf-8")
        named = [u for u in mod.UNREACHED if u in src]
        assert not named, (
            f"{named} are recorded as unreached and are named in this file, "
            f"which both risks running them and makes the scan read them as "
            f"reached")
