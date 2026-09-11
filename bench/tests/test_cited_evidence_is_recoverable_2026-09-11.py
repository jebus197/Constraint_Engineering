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
MAX_UNRECOVERABLE_PRESENT = 20


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
