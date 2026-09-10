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
        assert source in ("declared", "remote", "directory")
        assert "Constraint_Engineering" in names, names

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
                        "/nonexistent/elsewhere/Some_Other_Repo.git"],
                       cwd=r, check=True)
        names, _source = project_names(r)
        # A NAME THE DECLARED TIER CANNOT SUPPLY, so the remote is the only tier
        # that could have produced it. Rewritten 2026-09-11: the original
        # asserted `source == "remote"`, which stopped being observable once the
        # declared tier was added -- `.zenodo.json` always answers for the
        # RUNNING repository, so the label is always "declared" even while the
        # remote is still read for names. Asserting on the label would have made
        # this control a test of which tier reports rather than of which tiers
        # work.
        assert "Some_Other_Repo" in names, names
        assert "some_other_folder_name" in names, "the folder fallback was dropped"
        assert foreign_repo_roots("/elsewhere/Some_Other_Repo/bench/x.py", r) \
            == ["/elsewhere/Some_Other_Repo"]

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


def _calls(path: Path, func: str, names: set[str]) -> set[str]:
    """Which of `names` does `func` actually CALL? Parsed, never grepped."""
    import ast

    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == func:
            found = set()
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    f = sub.func
                    nm = getattr(f, "attr", None) or getattr(f, "id", None)
                    if nm in names:
                        found.add(nm)
            return found
    raise AssertionError(f"{func} is gone from {path.name}")


class TestTheDeclaredIdentityTier:
    """Identity must survive a checkout with no `.git` at all.

    FOUND 2026-09-11 by the cc2 seat in panel round 10, premise verified before
    acceptance: `bench/panel_sandbox.py:43` is `_NEVER_COPY = frozenset({".git"})`,
    so this project's own review sandbox -- where every one of these reviews runs
    -- has no git metadata, and neither does a ZIP, a Zenodo archive, or a
    vendored copy. The git-remote identity could not answer there, the folder
    name was the literal string "repo", and the whole A2 rebase recognised 0 of
    the 35 stale paths it exists to rebase. An addition nothing reaches, inside
    the fix for the previous instance of the same defect.
    """

    def _fake(self, tmp_path, folder: str, zenodo: bool):
        d = tmp_path / folder
        d.mkdir()
        if zenodo:
            import shutil
            shutil.copy(ROOT / ".zenodo.json", d / ".zenodo.json")
        return d

    def test_identity_survives_with_no_git_and_a_generic_folder(self, tmp_path):
        from bench.repo_paths import project_names
        d = self._fake(tmp_path, "repo", zenodo=True)
        names, source = project_names(d)
        assert source == "declared", source
        assert "Constraint_Engineering" in names, names

    def test_the_rebase_works_there(self, tmp_path):
        from bench.repo_paths import foreign_repo_roots
        d = self._fake(tmp_path, "repo", zenodo=True)
        assert foreign_repo_roots("/a/b/Constraint_Engineering/bench/x.py", d) \
            == ["/a/b/Constraint_Engineering"]

    def test_a_generic_folder_name_is_never_an_identity(self, tmp_path):
        """The hazard the filter removes: a checkout in a directory called
        `repo` would otherwise make every path ending `/repo` this tree."""
        from bench.repo_paths import project_names, _NOT_AN_IDENTITY
        d = self._fake(tmp_path, "repo", zenodo=False)
        names, source = project_names(d)
        assert "repo" not in names, names
        for generic in ("src", "tmp", "build", "sandbox"):
            assert generic in _NOT_AN_IDENTITY

    def test_a_specific_folder_name_is_still_kept(self, tmp_path):
        from bench.repo_paths import project_names
        d = self._fake(tmp_path, "ce_fresh", zenodo=False)
        names, _ = project_names(d)
        assert "ce_fresh" in names, names

    def test_only_the_declared_file_is_read_not_prose(self):
        """A prose scan would have been WRONG. `PAPER.md` cites
        github.com/jebus197/OpenBrain and github.com/jebus197/Project_Genesis;
        both would have become identities of THIS project and the rebase would
        rewrite paths into unrelated trees."""
        from bench.repo_paths import declared_project_names, DECLARED_IDENTITY_FILE
        assert DECLARED_IDENTITY_FILE == ".zenodo.json"
        names = declared_project_names(ROOT)
        assert names == {"Constraint_Engineering"}, names
        for foreign in ("OpenBrain", "Project_Genesis", "Metis"):
            assert foreign not in names


class TestAFigureThatIsAHundredPercentByConstruction:
    """`git ls-files` failing must refuse the figure, not fabricate it."""

    def test_it_refuses_rather_than_reporting_100_percent(self, tmp_path):
        import shutil
        mod = _load(ROOT / "scripts" / "orphan_figures_2026-09-10.py", "orphan1")
        d = tmp_path / "nogit"
        d.mkdir()
        for name in ("experimental_notes",):
            shutil.copytree(ROOT / name, d / name, dirs_exist_ok=True)
        mod.REPO = d
        with pytest.raises(mod.GitCannotAnswer):
            mod.untracked_cited_paths()

    def test_refusing_a8_does_not_silence_a19(self):
        """The regression the seat caught in its OWN first cut: raising
        SystemExit took down a figure that needed no git at all."""
        r = subprocess.run([sys.executable,
                            str(ROOT / "scripts" / "orphan_figures_2026-09-10.py")],
                           cwd=ROOT, capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-500:]
        assert "ENTRY A19" in r.stdout and "NO_SCORE:" in r.stdout

    def test_the_census_no_longer_reimplements_identity(self):
        """A second implementation of a rule is a second rule. The census's own
        copy gave 33 of 640 where the shared predicate gives 2 of 640."""
        import ast
        src = (ROOT / "scripts"
               / "archived_falsifier_rejections_2026-09-10.py").read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "project_names":
                calls = {getattr(c.func, "attr", None) or getattr(c.func, "id", None)
                         for c in ast.walk(node) if isinstance(c, ast.Call)}
                assert "_pn" in calls or "project_names" in calls, (
                    "the census re-derives identity locally again")
                return
        raise AssertionError("the census no longer exposes project_names at all")


class TestASafetyClaimIsNeverGatedByTheCorpus:
    """The line between "too few to conclude" and "there is one right there".

    FOUND 2026-09-11 by the fable seat in panel round 10, reproduced here before
    the fix was accepted. Making `test_panel_conditions_are_met` corpus-aware, I
    put the NO-PAID-SEAT check behind `corpus.shortfall(n, 10)` alongside its
    anti-vacuity sibling. A checkout holding 1 to 9 replies -- a partial commit,
    a run in progress -- would then SKIP a founder-reserved money constraint with
    a paid seat sitting in the records.

    The 2 claims are different kinds. A RATE needs a population. A VIOLATION does
    not: 1 paid reply is a violation whether it is 1 of 3 or 1 of 300.
    """

    def _plant(self, tmp_path, n_free, paid):
        import json
        d = tmp_path / "bench" / "logs" / "panel_round99_2026-09-11"
        d.mkdir(parents=True)
        for i in range(n_free):
            (d / f"free{i}.json").write_text(json.dumps(
                {"model": f"free{i}", "route": "claude_cli", "n_tool_calls": 3}))
        if paid:
            (d / "paid.json").write_text(json.dumps(
                {"model": "PAID", "route": "anthropic_api", "n_tool_calls": 3}))
        return [(d.name, __import__("json").loads(f.read_text()))
                for f in sorted(d.glob("*.json"))]

    def test_a_paid_seat_among_three_is_caught_not_skipped(self, tmp_path):
        replies = self._plant(tmp_path, 2, paid=True)
        assert len(replies) == 3, "the population must be BELOW the vacuity floor"
        paid = [(r, d["model"]) for r, d in replies if d.get("route") != "claude_cli"]
        assert paid, "the plant did not take; this control would prove nothing"
        from bench import archive_corpus as corpus
        gated = corpus.shortfall(len(replies), 10, "panel seat replies")
        assert gated, (
            "3 replies must be BELOW the shortfall floor, or this control does "
            "not exercise the window where the defect lived")
        # THE ASSERTION THAT MATTERS: the shipped test must not consult `gated`.
        #
        # READ AS CODE, NOT AS TEXT. My first version searched the function's
        # source for the word "shortfall" and went red on the COMMENT that
        # explains why the gate was removed -- the substring-versus-token defect,
        # recurrence 7 in this project, inside a control written to prevent a
        # different recurrence 2 hours earlier. An AST walk sees calls.
        assert not _calls(ROOT / "bench" / "tests"
                          / "test_panel_conditions_are_met_2026-09-10.py",
                          "test_zero_paid_replies_in_any_round_under_section_p",
                          {"shortfall", "skip"}), (
            "the no-paid-seat check calls a corpus gate or skips; a checkout "
            "with 1 to 9 replies would skip past a money constraint")

    def test_the_vacuity_sibling_is_still_allowed_to_skip(self):
        """The distinction, from the other side. The RATE claim may skip.

        ANTI-VACUITY FOR THE CONTROL ABOVE. If neither function called a gate,
        the assertion above would pass on a file where the whole mechanism had
        been deleted.
        """
        assert _calls(ROOT / "bench" / "tests"
                      / "test_panel_conditions_are_met_2026-09-10.py",
                      "test_the_rounds_under_the_ruling_exist_at_all",
                      {"shortfall"}), (
            "the anti-vacuity sibling no longer consults the corpus, so a clone "
            "with 0 replies reports a red test for an unavoidable fact")


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
