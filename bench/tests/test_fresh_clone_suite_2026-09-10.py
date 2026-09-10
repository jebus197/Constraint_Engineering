"""Task A2: the suite must pass for a reader who clones and follows the steps.

THE ENTRY'S PREMISE WAS FALSE BY THE TIME IT WAS WORKED. It said "11 failed,
5487 passed, exit 1, against 0 failures in the working tree", measured
2026-09-09. Re-measured 2026-09-10 at the same HEAD: the clone gave 22 failed,
6592 passed, and the WORKING TREE gave 6 -- the count had doubled in a day and
the maintainer's tree was not clean either. Both halves of the sentence needed
correcting before any repair could be aimed.

WHAT THIS FILE HOLDS. The 3 repairs whose failure modes are SECURITY- or
CORRECTNESS-critical, each with a control proving the widening did not open a
hole, plus the census that keeps the diagnosis honest. The other repairs are
guarded in the files they touch, because that is where a regression would show.

THE ONE TO READ TWICE is `_retarget_falsifier`'s rebase. It rewrites an absolute
path inside a falsifier before executing it. That is exactly the shape of change
this project discarded a whole experiment over, so it is bounded 3 ways -- it
matches only a path ending at a directory named like THIS project, identified
from the git remote rather than the folder name; it is used only when replaying
an ARCHIVED falsifier into an overlay; and it does not touch the containment
guard, which still refuses a live falsifier naming anything outside the tree.
The controls below are the evidence for each of those.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

CENSUS = ROOT / "scripts" / "fresh_clone_census_2026-09-10.py"
REJECTIONS = ROOT / "scripts" / "archived_falsifier_rejections_2026-09-10.py"


def _load(path: Path, name: str):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── the replay rebase, and why it is not a hole ──────────────────────────────

class TestTheReplayRebaseIsBounded:
    def test_it_rebases_this_project_named_from_another_checkout(self):
        from bench.reference_runner_v3 import _retarget_falsifier
        code = ("open('/Users/someone/Developer_Projects/Constraint_Engineering"
                "/bench/evidence.py')")
        out, n = _retarget_falsifier(code, Path("/tmp/here"), Path("/tmp/overlay"))
        assert n == 1, "the archived path was not recognised"
        assert "/tmp/overlay/bench/evidence.py" in out
        assert "Constraint_Engineering" not in out

    @pytest.mark.parametrize("code", [
        "open('/etc/passwd')",
        "open('/Users/someone/.ssh/id_rsa')",
        "open('/Users/someone/Documents/answer_key.json')",
        "open('/Users/someone/Other_Project/bench/evidence.py')",
        "open('/Users/someone/Constraint_Engineering_backup/x.py')",
    ])
    def test_it_touches_nothing_else(self, code):
        """The whole safety argument. A rebase that widened to any absolute path
        would let an archived falsifier reach anywhere the overlay can."""
        from bench.reference_runner_v3 import _retarget_falsifier
        out, n = _retarget_falsifier(code, Path("/tmp/here"), Path("/tmp/overlay"))
        assert (out, n) == (code, 0), f"{code} was rewritten"

    def test_the_containment_guard_is_unchanged(self):
        """The rebase must not be reachable from the guard. A LIVE falsifier
        naming a path outside the tree is still refused, because containment is
        about the filesystem and not about intent.

        THE BOUNDARY, STATED RATHER THAN OVERCLAIMED. This rule reads
        `_USER_PATH`, which matches home-shaped and volume-shaped roots -- `~/`,
        `$HOME/`, `/Users/x`, `/home/x`, `/Volumes/`, `/Library/`. `/etc/passwd`
        is NOT matched by it and never was; a first version of this control
        asserted otherwise and was refuted by running it. Whatever bounds
        `/etc` is elsewhere, it is not this rule, and a test that claimed
        credit for it would be describing a guard that does not exist.
        """
        from bench.falsifier_verify import scan_falsifier_source
        for bad in ("open('/Users/someone/Other_Project/x.py')",
                    "open('/home/someone/secrets/x.py')",
                    "open('/Users/someone/Constraint_Engineering_backup/x.py')"):
            assert scan_falsifier_source(bad), f"{bad} is no longer refused"
        assert scan_falsifier_source("open('/etc/passwd')") == [], (
            "this rule has started matching non-home absolute paths; that may "
            "be an improvement, but the docstring above no longer describes it")

    def test_the_identity_comes_from_the_repository_not_the_folder(self):
        """The defect that made the first 2 versions of this wrong.

        A clone sits wherever the reader put it, so `Path(root).name` is not the
        project's identity. The git remote is, and a clone carries it.
        """
        from bench.repo_paths import project_names
        names, source = project_names(ROOT)
        assert source in ("remote", "directory")
        if source == "remote":
            assert "Constraint_Engineering" in names, names
        assert ROOT.name in names, "the folder name is still kept as a fallback"

    def test_the_remote_wins_over_the_folder_name(self, tmp_path):
        """THE CONTROL THAT ACTUALLY BINDS, and the first version did not.

        My first identity control asserted `project_names(ROOT)` contains
        "Constraint_Engineering" -- which it does even with the remote lookup
        DELETED, because this checkout's folder happens to carry that name.
        Mutation-tested 2026-09-10: disabling the remote branch left every
        assertion green. A control that passes on the mutant is not a control.

        This builds a checkout under a DIFFERENT folder name whose only claim to
        the identity is its remote, so the remote lookup is the sole thing that
        can answer.
        """
        from bench.repo_paths import project_names, foreign_repo_roots
        r = tmp_path / "some_other_folder_name"
        r.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=r, check=True)
        # A PATH REMOTE, NOT A URL. The suite's netguard denies any subprocess
        # whose argv contains "https://" -- correctly, since that is how a test
        # would reach a paid endpoint -- so a URL remote here is refused before
        # git ever sees it. A path remote exercises the same code and stays
        # offline. (`git remote add` touches no network either way; the guard is
        # bounded by capability, not by intent, which is the right way round.)
        subprocess.run(["git", "remote", "add", "origin",
                        "/nonexistent/elsewhere/Constraint_Engineering.git"],
                       cwd=r, check=True)
        names, source = project_names(r)
        assert source == "remote", source
        assert "Constraint_Engineering" in names, names
        assert "some_other_folder_name" in names, "the folder fallback was dropped"
        assert foreign_repo_roots("/elsewhere/Constraint_Engineering/bench/x.py", r) \
            == ["/elsewhere/Constraint_Engineering"]

    def test_a_directory_rename_does_not_lose_the_identity(self):
        """Executed, not argued: a checkout under any name still answers to the
        remote's name, which is what makes the clone case work."""
        from bench.repo_paths import foreign_repo_roots, project_names
        names, source = project_names(ROOT)
        if source != "remote":
            pytest.skip("no git remote here, so the strong identity is absent")
        stale = "/some/other/machine/Constraint_Engineering/bench/x.py"
        assert foreign_repo_roots(stale, ROOT) == \
            ["/some/other/machine/Constraint_Engineering"]


# ── the onboarding discriminator, both directions ────────────────────────────

class TestTheOnboardingDiscriminator:
    def _repo(self, tmp_path: Path) -> Path:
        r = tmp_path / "clone"
        r.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=r, check=True)
        return r

    def test_a_never_onboarded_clone_is_recognised(self, tmp_path):
        r = self._repo(tmp_path)
        got = subprocess.run(["git", "config", "--local", "--get", "cdsfl.onboarded"],
                             cwd=r, capture_output=True, text=True).stdout.strip()
        assert got == "", "a fresh clone must carry no stamp"

    def test_onboarding_writes_the_stamp_and_it_survives_unwiring(self, tmp_path):
        """The case that must stay RED. If unsetting core.hooksPath also cleared
        the stamp, turning the guard off would look like never installing it."""
        onb = _load(ROOT / "scripts" / "cdsfl_onboard.py", "onb")
        r = self._repo(tmp_path)
        (r / "hooks").mkdir()
        (r / "hooks" / "pre-commit").write_text("#!/bin/sh\nexit 0\n")
        (r / "hooks" / "pre-commit").chmod(0o755)
        assert onb.wire_git_hooks(r) is True
        stamp = subprocess.run(["git", "config", "--local", "--get", "cdsfl.onboarded"],
                               cwd=r, capture_output=True, text=True).stdout.strip()
        assert stamp, "onboarding left no stamp"
        subprocess.run(["git", "config", "--unset", "core.hooksPath"], cwd=r, check=False)
        after = subprocess.run(["git", "config", "--local", "--get", "cdsfl.onboarded"],
                               cwd=r, capture_output=True, text=True).stdout.strip()
        assert after == stamp, (
            "unsetting core.hooksPath cleared the stamp, so a removed guard "
            "would be misread as a clone that was never set up")

    def test_the_old_discriminator_really_was_unreachable(self):
        """The finding, checked rather than asserted: `--get user.email` falls
        back to global config, so the old skip could not fire here."""
        got = subprocess.run(["git", "config", "--get", "user.email"],
                             cwd=ROOT, capture_output=True, text=True).stdout.strip()
        local = subprocess.run(["git", "config", "--local", "--get", "user.email"],
                               cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if not got:
            pytest.skip("this machine has no git identity at all, so the "
                        "unreachability cannot be demonstrated here")
        assert got and not local or got == local, (got, local)


    def test_a_wired_checkout_without_the_stamp_is_a_regression(self):
        """THE TRAP THIS MECHANISM SETS, and it caught me within the hour.

        `is_onboarded_checkout` now gates the Desktop-mirror guards. The moment
        it was wired, 5 of them SKIPPED in the canonical tree -- because this
        checkout had been wired long before the stamp existed, so it carried
        `core.hooksPath=hooks` and no stamp, and the ownership test read that as
        "not my mirror". A guard that silently goes quiet is worse than one that
        fails, and this is the shape the additive standard's symmetric half
        names: a gate nothing satisfies.

        WIRED AND UNSTAMPED IS NOW AN ERROR, not a skip. It can only arise from
        the stamp mechanism regressing or from a checkout wired by hand, and
        both want the same 1-line remedy.
        """
        from bench.repo_paths import is_onboarded_checkout
        wired = subprocess.run(["git", "config", "--get", "core.hooksPath"],
                               cwd=ROOT, capture_output=True,
                               text=True).stdout.strip()
        if wired != "hooks":
            pytest.skip("this checkout is not the wired one, so the pairing "
                        "cannot be checked here")
        assert is_onboarded_checkout(ROOT), (
            "this checkout has core.hooksPath=hooks but no cdsfl.onboarded "
            "stamp, so every guard keyed on ownership is SKIPPING here rather "
            "than running. Fix with: python3 scripts/cdsfl_onboard.py")


# ── the corpus helper must fail closed ───────────────────────────────────────

class TestTheCorpusHelperCannotHideADisagreement:
    def test_a_sufficient_population_never_skips(self):
        from bench import archive_corpus as corpus
        assert corpus.shortfall(10, 10, "x") is None
        assert corpus.shortfall(11, 10, "x") is None

    def test_a_short_population_gives_a_reason_that_names_the_rule(self):
        from bench import archive_corpus as corpus
        r = corpus.shortfall(0, 10, "seat replies")
        assert r and "gitignore:41" in r and "NOT verified" in r

    def test_missing_names_the_absent_paths_only(self, tmp_path):
        from bench import archive_corpus as corpus
        there = tmp_path / "a.txt"
        there.write_text("x")
        assert corpus.missing([there], "x") is None
        r = corpus.missing([there, tmp_path / "gone.txt"], "the check")
        assert r and "gone.txt" in r and "a.txt" not in r


# ── the census keeps the diagnosis honest ────────────────────────────────────

class TestTheCensus:
    def test_it_runs_and_names_every_cause(self):
        r = subprocess.run([sys.executable, str(CENSUS)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stdout[-800:] + r.stderr[-400:]
        for cause in ("stale-absolute-path", "corpus-absent", "both-trees",
                      "import-time-io", "environment"):
            assert cause in r.stdout, f"the census no longer names {cause}"

    def test_every_file_it_names_still_exists(self):
        mod = _load(CENSUS, "census")
        for row in mod.CENSUS:
            assert (ROOT / row[0]).is_file(), row[0]

    def test_it_reports_that_the_working_tree_was_not_clean(self):
        """The entry's premise. If this sentence goes, the correction is lost."""
        r = subprocess.run([sys.executable, str(CENSUS)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert "MAINTAINER'S tree too" in r.stdout


class TestTheRejectionClassifier:
    def test_it_runs_here(self):
        r = subprocess.run([sys.executable, str(REJECTIONS)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stdout[-600:] + r.stderr[-400:]
        assert "REAL rejections" in r.stdout and "LOCATION ARTEFACTS" in r.stdout

    def test_the_real_rejection_count_is_location_independent(self):
        """2 of 640, in the maintainer's tree and in a clone alike. That
        invariance IS the finding; the raw rejection count is not."""
        mod = _load(REJECTIONS, "rejections")
        sources, real, _artefact = mod.survey()
        assert len(sources) > 400, len(sources)
        assert len(real) == 2, sorted(w[0] for w in real.values())
