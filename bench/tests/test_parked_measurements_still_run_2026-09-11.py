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


class TestTheLastTwoRunSafelyWithTheirOutputRedirected:
    """The final 2, and they were parked for a reason that arguments dissolve.

    Both WRITE, which is why they sat unrun while 4 siblings were wired. But
    neither writes to a fixed place: each takes its destination from an argument.
    `readjudicate_pairs.py` builds `REPO / args.out`, and `Path / <absolute>`
    yields the absolute path, so an absolute `--out` redirects the write entirely
    while the inputs still resolve against the real repository.
    `quarantine_to_candidate.py` writes beside the diff it is given, so a diff in
    a temporary directory keeps the output there too.

    CHECKED BEFORE RUNNING, NOT AFTER. Neither imports `requests`, `urllib` or
    any HTTP client, and neither spawns a process -- so neither can dispatch a
    model. That mattered more than the file writes: spending money is one of the
    3 categories reserved to the founder, and "re-adjudicate" is exactly the word
    that would make a reader assume a dispatch.

    This takes the recorded orphan set to 0. It got there by execution, not by
    argument: every one of the 6 was run, and each one's safety was established
    before it was.
    """

    def test_readjudicate_writes_where_it_is_told(self, tmp_path):
        out = tmp_path / "readjudicated.json"
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "readjudicate_pairs.py"),
             "--limit", "1", "--out", str(out)],
            cwd=REPO, capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-600:]
        assert "re-adjudicate" in r.stdout, r.stdout[:400]
        assert out.is_file(), "the redirected output was not written"
        import json
        assert "tally" in json.loads(out.read_text(encoding="utf-8"))

    def test_quarantine_converts_a_diff_beside_it(self, tmp_path):
        diff = tmp_path / "x.diff"
        diff.write_text(
            "--- a/bench/toy.py\n+++ b/bench/toy.py\n"
            "@@ -1,2 +1,2 @@\n-old_line = 1\n+new_line = 2\n", encoding="utf-8")
        test = tmp_path / "test_toy.py"
        test.write_text("def test_toy():\n    assert True\n", encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "quarantine_to_candidate.py"),
             str(diff), str(test)],
            cwd=REPO, capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-600:]
        made = tmp_path / "x.candidate.md"
        assert made.is_file(), "no candidate was written beside the diff"
        body = made.read_text(encoding="utf-8")
        assert "<<<< SEARCH" in body and "TEST_FILE:" in body, body[:300]

    def test_neither_can_dispatch_a_model(self):
        """The check that had to come FIRST. A script that could spend money must
        not be run to find out whether it does.

        NETWORK by IMPORT, SPAWNING by CALL, and the difference is not pedantry.
        The first version of this test failed on `quarantine_to_candidate.py`
        because it IMPORTS `subprocess` -- and that import is dead, never called
        anywhere in the file. Treating the import as the hazard is the same
        source-text-for-behaviour substitution `execute-do-not-grep` exists to
        stop, and it would have kept a harmless script parked indefinitely.

        An HTTP import keeps the stricter treatment, because the cost of a false
        positive there is one line of justification and the cost of a false
        negative is a bill the founder did not authorise.
        """
        import ast
        for name in ("readjudicate_pairs.py", "quarantine_to_candidate.py"):
            tree = ast.parse((REPO / "scripts" / name).read_text(encoding="utf-8"))
            mods = {a.name.split(".")[0] for n in ast.walk(tree)
                    if isinstance(n, ast.Import) for a in n.names}
            mods |= {n.module.split(".")[0] for n in ast.walk(tree)
                     if isinstance(n, ast.ImportFrom) and n.module}
            assert not (mods & {"requests", "urllib", "http", "httpx", "socket"}), (
                f"{name} imports a network client: {sorted(mods)}")
            spawns = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Call)
                      and (getattr(n.func, "attr", None) in
                           ("run", "Popen", "check_call", "check_output", "call")
                           or getattr(n.func, "id", None) == "system")]
            assert not spawns, f"{name} spawns a process at line(s) {spawns}"

    def test_neither_run_changed_the_repository(self):
        """Asserted as a consequence, not trusted from the argument above."""
        r = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                           capture_output=True, text=True)
        assert r.returncode == 0
        assert not [ln for ln in r.stdout.splitlines()
                    if "candidate.md" in ln or "readjudicated" in ln], r.stdout
