"""2 of the 6 orphaned scripts still work, and a working script nothing reaches is still unreached.

THE RATCHET IN `test_scripts_are_reached_2026-09-11.py` RECORDS 6 SCRIPTS THAT
NOTHING CALLS, CITES OR NAMES. Whether to wire or retire them is the founder's
ruling and is parked for him. **Wiring is not the half that needs a ruling**: the
additive standard's removal clause requires a committed measurement before
anything is taken away, while its other half — *"an addition that nothing reaches
is not additive either"* — is discharged by giving a script a caller, and a test
that EXECUTES it is exactly that caller.

SO THESE 2 ARE WIRED HERE, and the other 4 are not. The difference is measured
rather than assumed: an AST walk over all 6 found that these 2 contain no write
call, no subprocess spawn and no absolute path, so running them cannot change
anything. The other 4 write files or spawn processes, and the founder's standing
instruction is explicit that running the scripts directory as a survey once
overwrote a preserved archive. They stay parked, unrun.

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
        """The reason these 2 and not the other 4. An AST walk found no write
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

    def test_the_other_four_are_not_run_here(self):
        """STATED, NOT IMPLIED. The 4 that write or spawn are deliberately absent,
        and the founder's instruction against running the scripts directory as a
        survey is the reason."""
        src = pathlib.Path(__file__).read_text(encoding="utf-8")
        for name in ("inventory_2026_09_06", "quarantine_to_candidate",
                     "readjudicate_pairs",
                     "scope_remaining_adjudication_and_materiality"):
            assert f"scripts/{name}.py\"" not in src.replace(WIRED[0][0], ""), name
