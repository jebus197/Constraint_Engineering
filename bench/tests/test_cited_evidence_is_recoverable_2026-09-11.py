"""Task A8: cited evidence must be recoverable from the repository, and the
set that is not may not grow.

THE ENTRY ASKED THE WRONG QUESTION, and the right one is measurable. A8 asks
whether 23 cited `bench/logs/` paths should be tracked, relocated, or
accepted-and-labelled. `.gitignore:41` excludes that directory by design -- it
was 353 MB across 5,840 files -- so *relocate* cannot make a cited path tracked:
the note still names the original and the original stays excluded. Measured
2026-09-11: mirroring every review record moved the untracked count not at all.

**RECOVERABILITY is the property that matters**, and over every cited
`bench/logs/` path: **167 of 215 recoverable -- 77.6744%, Wilson
[71.6500%, 82.7272%], Clopper-Pearson [71.5125%, 83.0563%]**; 138 tracked
directly and 29 through a mirrored copy.

**THE RESIDUE A RULING IS ACTUALLY ABOUT IS 20 FILES AND 1.63 MB** -- cited,
present on this machine, and in no commit. The other 28 unrecoverable paths are
absent here too: `round_XX.json` and `exp42_.../round7.json` are ellipsis
templates and worked examples, not citations to anything. **20 of 215 = 9.3023%,
Wilson [6.1026%, 13.9308%], Clopper-Pearson [5.7750%, 14.0009%]**, statsmodels
and scipy agreeing to 0.0e+00.

**THIS FILE DOES NOT DECIDE THE DISPOSITION**, which is the founder's. It is a
RATCHET: whatever he rules, new cited evidence must not join the unrecoverable
set silently. The residue is run artefacts -- simulation checkpoints, immune
pipeline logs, the build experiment's `CY_LIVE.log`, target-mutation snapshots --
so the review-record mirror correctly excludes them and a separate decision is
needed rather than a wider glob.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "resolve_cited_evidence_2026-09-11.py"

#: Measured 2026-09-11. A RATCHET, not a target: it may fall, never rise.
#: Raising it means new cited evidence exists on 1 machine only, which is the
#: condition A8 exists to close.
MAX_UNRECOVERABLE_PRESENT = 21

#: ★ THE PIN IS A SET, NOT A COUNT, FROM 2026-10-16.
#:
#: WHY THE COUNT WAS THE WRONG INSTRUMENT, learned by paying for it. On
#: 2026-10-16 this ratchet failed with `assert 21 <= 20`. That told the reader
#: the number had grown and NOTHING about which path was new, so establishing
#: whether the growth was caused by the session's own work took half a dozen
#: separate measurements -- resolving every cited path, listing the citing
#: document for each, and running `git log -S` on two candidates to date them.
#: The answer was that both citations predated the session by 1 to 2 days, so
#: the failure was inherited rather than caused. A ratchet that cannot say what
#: tripped it makes every reader redo that work.
#:
#: A SET ANSWERS IT IMMEDIATELY and is strictly stronger: it implies the count,
#: and it also catches a SWAP -- one path becoming recoverable while another
#: becomes unrecoverable, which leaves the count at 21 and would pass the old
#: form silently. The count assertion is KEPT as well, so nothing is removed.
#:
#: HOW TO CHANGE THIS LIST. Adding a path means a reader cannot reach evidence
#: that is cited, so the entry belongs here only with a reason. Prefer making
#: the path recoverable -- commit it, or mirror it under
#: `experimental_notes/evidence/` -- over widening the pin. `POINT, NEVER
#: PRUNE` applies: do not delete the artefact to make the citation go away.
UNRECOVERABLE_PRESENT_PIN = frozenset({
    "bench/logs/_suite/full_suite_2026-10-02_pm.log",
    "bench/logs/_suite/full_suite_2026-10-05_2026-10-05_004000.log",
    "bench/logs/_suite/full_suite_2026-10-05_postfix.log",
    "bench/logs/_suite/run_full_suite_2026-10-02_pm.sh",
    "bench/logs/_suite/run_full_suite_2026-10-02_pm2.sh",
    "bench/logs/build_experiment_2026-08-22/CY_LIVE.log",
    "bench/logs/build_experiment_2026-08-22/composition_both_orders.json",
    "bench/logs/commissioning_2026-09-21_arm1.log",
    "bench/logs/commissioning_2026-09-22_arm2.log",
    "bench/logs/exp36_evidence_latest/exp36_report.json",
    "bench/logs/exp36_evidence_latest/runner_state.json",
    "bench/logs/exp55.pid",
    "bench/logs/falsifier_root_cause_2026-09-30/sandbox_harvest/cc2/attempt-1/files/scripts/falsify_e2_inherits_default_2026-09-30.py",
    "bench/logs/falsifier_root_cause_2026-09-30/sandbox_harvest/cc2/attempt-1/files/scripts/falsify_prose_falsifier_supply_2026-09-30.py",
    "bench/logs/falsifier_root_cause_2026-09-30/sandbox_harvest/fable/attempt-1/files/scripts/falsifier_supply_fable_2026-09-30.py",
    "bench/logs/fingerprint_ladder_review_2026-10-05/sandbox_harvest/fable/attempt-1/files/scripts/the_provenance_gate_reads_text_not_behaviour_2026-10-05.py",
    "bench/logs/fresh_clone_last_run.txt",
    "bench/logs/sim45_memory_20260901T040540Z/immune_pipeline.log",
    "bench/logs/sim_panel_findings.json",
    "bench/logs/target_mutation_watch_2026-09-08/snapshots/SEAT_064003_03845310.py",
    "bench/logs/target_mutation_watch_2026-09-08/target_state_transitions.log",
})


def _in_a_git_checkout() -> bool:
    r = subprocess.run(["git", "rev-parse", "--git-dir"], cwd=REPO,
                       capture_output=True, text=True)
    return r.returncode == 0


@pytest.fixture(scope="module")
def mod():
    if not _in_a_git_checkout():
        pytest.skip("tracking cannot be decided outside a git checkout, and "
                    "reporting everything untracked would be a fabricated "
                    "figure -- the defect panel round 12 found in "
                    "overstated_entries")
    spec = importlib.util.spec_from_file_location("resolver", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["resolver"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def rows(mod):
    return [mod.resolve(p) for p in mod.cited_paths()]


class TestTheRatchet:
    def test_the_unrecoverable_present_set_has_not_grown(self, rows):
        here = [r["path"] for r in rows
                if not (r["tracked"] or r["mirror"]) and r["present"]]
        assert len(here) <= MAX_UNRECOVERABLE_PRESENT, (
            f"{len(here)} cited paths exist on this machine and in no commit, "
            f"up from {MAX_UNRECOVERABLE_PRESENT}. New evidence has been cited "
            f"that a reader cannot reach:\n  "
            + "\n  ".join(sorted(here)[:15]))

    def test_the_unrecoverable_set_is_exactly_the_pinned_one(self, rows):
        """NAMES what changed, which the count above cannot.

        A count tells a reader the number moved. This tells them which path,
        and in which direction -- so a failure here is actionable in one read
        instead of half a dozen measurements.
        """
        here = {r["path"] for r in rows
                if not (r["tracked"] or r["mirror"]) and r["present"]}
        added = sorted(here - UNRECOVERABLE_PRESENT_PIN)
        gone = sorted(UNRECOVERABLE_PRESENT_PIN - here)
        assert not added, (
            f"{len(added)} cited path(s) are newly unreachable to a reader. "
            f"Prefer making them recoverable -- commit them, or mirror them "
            f"under experimental_notes/evidence/ -- over widening the pin:\n  "
            + "\n  ".join(added))
        assert not gone, (
            f"{len(gone)} pinned path(s) are no longer unrecoverable, which is "
            f"good news: remove them from UNRECOVERABLE_PRESENT_PIN so the pin "
            f"keeps describing the real state rather than excusing a path that "
            f"no longer needs excusing:\n  " + "\n  ".join(gone))

    def test_no_mirror_has_diverged_from_its_source(self, rows):
        """A copy that silently diverged is worse than no copy: it looks like
        the record."""
        bad = [r["path"] for r in rows if r["identical"] is False]
        assert not bad, bad


class TestTheMeasurementIsNotVacuous:
    def test_there_are_cited_paths_to_resolve(self, rows):
        assert len(rows) >= 150, (
            f"only {len(rows)} cited paths found; the extractor has probably "
            f"stopped matching and the ratchet is guarding nothing")

    def test_the_mirror_route_is_actually_used(self, rows):
        """ANTI-VACUITY on the resolver itself. If no path resolved THROUGH a
        mirror, the whole relocation half would be untested and the ratchet
        would be measuring only what git tracks."""
        via = [r["path"] for r in rows if r["mirror"] and not r["tracked"]]
        assert len(via) >= 10, (
            f"only {len(via)} cited paths resolve through a mirrored copy; the "
            f"resolver's relocation route is not being exercised")

    def test_a_tracked_path_resolves_as_tracked(self, mod):
        """POSITIVE CONTROL, on a path that is certainly tracked."""
        r = mod.resolve("scripts/orphan_figures_2026-09-10.py")
        assert r["tracked"] is True

    def test_a_path_that_exists_nowhere_resolves_as_unrecoverable(self, mod):
        r = mod.resolve("bench/logs/there-is-no-such-round/nothing.json")
        assert r["tracked"] is False
        assert r["mirror"] is None
        assert r["present"] is False


class TestItSurvivesTheArchiveAsItIs:
    def test_a_dangling_symlink_does_not_raise(self, mod):
        """`bench/logs/exp36_evidence_latest` points at a directory that is
        gone. The mirror's date fallback called `f.stat()` over `iterdir()`
        unguarded and died on it -- found the moment this resolver became its
        second caller, which is what wiring an addition to a caller is for. A
        dangling link is a legitimate state in an archive, not an error."""
        r = mod.resolve("bench/logs/exp36_evidence_latest/exp36_report.json")
        assert isinstance(r, dict)

    def test_the_script_runs_end_to_end(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=REPO,
                           capture_output=True, text=True, timeout=1800)
        assert r.returncode in (0, 1), r.stderr[-800:]
        assert "recoverable from the tree" in r.stdout
