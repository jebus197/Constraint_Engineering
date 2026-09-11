"""A stage-0 repair must reach the COMMIT, not just the working tree.

WHAT WAS WRONG, measured rather than suspected.  On 2026-09-11 task A2's DONE
claim -- "a fresh clone is green" -- was re-checked by cloning HEAD and running
the suite in the clone:

    3 failed, 6952 passed, 38 skipped, 1 xfailed in 1478.12s
      test_citation_content_2026-09-10.py
      test_experiment_run_ledger_2026-08-26.py
      test_measurement_survey_is_safe_2026-09-11.py

The same suite in the maintainer's tree was 6988 passed, 0 failed.

A pre-commit hook sees the STAGED snapshot.  Stage 0's repairs write the WORKING
TREE and did not `git add` what they wrote, so every commit shipped the
UNREPAIRED content and left the repair uncommitted for the NEXT commit to sweep
in.  The repairs ran correctly and were permanently 1 commit behind.  Nothing
local could see it: `git status` named the modified files and said nothing about
why, and the suite was green here on every one of those days.

WHY THIS FILE EXECUTES RATHER THAN READS.  `execute-do-not-grep`.  The staging
logic lives in exactly 1 place, `hooks/stage0_restage.sh`; the hook SOURCES it
and so does every test below, against a real git index in a scratch repository.
A test that read the hook's text would prove only that the hook describes itself
consistently -- which it already did, throughout the 2 days the defect shipped.

The 2 text assertions that remain are about WIRING, not behaviour: that the hook
calls each function at all.  An addition nothing reaches is not additive, and
there is no second representation of a call site to execute against.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
HOOK = REPO / "hooks" / "pre-commit"
LIB = REPO / "hooks" / "stage0_restage.sh"

#: Verbatim output formats, copied from the producing scripts rather than
#: invented, so a format drift shows up here as a red test.
#:   scripts/experiment_run_ledger.py:316
LEDGER_OK = "  refreshed experimental_notes/EXPERIMENT_RUN_LEDGER.md"
#:   scripts/experiment_run_ledger.py:308
LEDGER_DECLINED = ("  ledger NOT refreshed: this checkout has fewer artefacts "
                   "than the ledger declares")
#:   scripts/citation_content_guard_2026-09-10.py:97
CITATION_OK = "  experimental_notes/Note.md: 11354 -> 11456  (`_substitute_root`)"
#:   scripts/citation_content_guard_2026-09-10.py:136 -- REPORT mode, 4 spaces
CITATION_REPORT_LINE = ("    experimental_notes/Note.md:11354 names `f`, which "
                        "spans 11456-11500")
#:   scripts/citation_content_guard_2026-09-10.py:132 -- REPORT mode, no arrow
CITATION_REPORT_WILSON = "  23/127 = 18.1102%  Wilson [12.3818%, 25.7112%]  n=127"


def _git(repo: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    assert r.returncode == 0, f"git {' '.join(args)} -> {r.returncode}\n{r.stderr}"
    return r.stdout


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A scratch repository with 1 committed file and 1 uncommitted edit."""
    r = tmp_path / "repo"
    (r / "experimental_notes").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", "."], cwd=r, check=True)
    _git(r, "config", "user.email", "t@example.invalid")
    _git(r, "config", "user.name", "t")
    for name in ("EXPERIMENT_RUN_LEDGER.md", "Note.md", "Untouched.md"):
        (r / "experimental_notes" / name).write_text("BEFORE\n", encoding="utf-8")
    _git(r, "add", "-A")
    _git(r, "commit", "-q", "-m", "base")
    # Every file now differs in the working tree, exactly as it would after a
    # repair ran.  Nothing is staged.
    for name in ("EXPERIMENT_RUN_LEDGER.md", "Note.md", "Untouched.md"):
        (r / "experimental_notes" / name).write_text("REPAIRED\n", encoding="utf-8")
    return r


def _feed(repo: Path, function: str, stdin: str) -> subprocess.CompletedProcess:
    """Source the REAL helper in the scratch repo and pipe output through it."""
    script = f'. "{LIB}"\n{function}\n'
    return subprocess.run(["sh", "-c", script], cwd=repo, input=stdin,
                          capture_output=True, text=True)


def _staged(repo: Path) -> set[str]:
    out = _git(repo, "diff", "--cached", "--name-only")
    return {ln for ln in out.splitlines() if ln}


class TestTheControlHolds:
    """ANTI-VACUITY.  If the fixture staged things by itself, every assertion
    below would pass for the wrong reason."""

    def test_nothing_is_staged_before_the_helper_runs(self, repo):
        assert _staged(repo) == set()

    def test_the_files_really_do_differ_from_head(self, repo):
        out = _git(repo, "status", "--porcelain")
        assert out.count(" M ") == 3, out


class TestAReportedPathIsStaged:
    def test_the_ledger_line_stages_the_ledger(self, repo):
        r = _feed(repo, "cdsfl_restage_from_ledger_output", LEDGER_OK + "\n")
        assert r.returncode == 0, r.stderr
        assert _staged(repo) == {"experimental_notes/EXPERIMENT_RUN_LEDGER.md"}

    def test_the_citation_line_stages_that_note(self, repo):
        r = _feed(repo, "cdsfl_restage_from_citation_output", CITATION_OK + "\n")
        assert r.returncode == 0, r.stderr
        assert _staged(repo) == {"experimental_notes/Note.md"}

    def test_the_staged_content_is_the_repaired_content(self, repo):
        """Staging the PATH is not the property; staging the NEW BYTES is."""
        _feed(repo, "cdsfl_restage_from_ledger_output", LEDGER_OK + "\n")
        blob = _git(repo, "show", ":experimental_notes/EXPERIMENT_RUN_LEDGER.md")
        assert blob == "REPAIRED\n", (
            "the index holds the pre-repair bytes; the commit would ship them")

    def test_it_says_what_it_staged(self, repo):
        r = _feed(repo, "cdsfl_restage_from_ledger_output", LEDGER_OK + "\n")
        assert "re-staged experimental_notes/EXPERIMENT_RUN_LEDGER.md" in r.stdout


class TestNothingElseIsSwept:
    """The reason this is not `git add -A`."""

    def test_an_unnamed_modified_file_stays_unstaged(self, repo):
        _feed(repo, "cdsfl_restage_from_ledger_output", LEDGER_OK + "\n")
        assert "experimental_notes/Untouched.md" not in _staged(repo)

    def test_the_ledger_decline_line_stages_nothing(self, repo):
        """`--refresh` DECLINES on a checkout holding fewer artefacts than the
        ledger declares.  It names no path, so nothing may be staged."""
        r = _feed(repo, "cdsfl_restage_from_ledger_output", LEDGER_DECLINED + "\n")
        assert r.returncode == 0, r.stderr
        assert _staged(repo) == set()

    def test_the_citation_guard_report_lines_stage_nothing(self, repo):
        """OVER-MATCHING CONTROL.  The first pattern written for this was
        `s/^  \\([^ :]*\\):.*->.*$/\\1/p` -- "2 spaces, then anything up to a
        colon, then an arrow somewhere".  Report mode prints lines with colons
        and the word `names`; the anchored form below cannot reach them."""
        stdin = CITATION_REPORT_LINE + "\n" + CITATION_REPORT_WILSON + "\n"
        r = _feed(repo, "cdsfl_restage_from_citation_output", stdin)
        assert r.returncode == 0, r.stderr
        assert _staged(repo) == set(), (
            "a report line was read as a repair; the guard's read-only mode "
            "would start staging files")

    def test_an_empty_stream_stages_nothing(self, repo):
        r = _feed(repo, "cdsfl_restage_from_citation_output", "")
        assert r.returncode == 0
        assert _staged(repo) == set()

    def test_the_no_op_summary_line_stages_nothing(self, repo):
        """The ordinary case: `repaired 0 citation(s)` and nothing else."""
        r = _feed(repo, "cdsfl_restage_from_citation_output",
                  "repaired 0 citation(s)\n")
        assert r.returncode == 0
        assert _staged(repo) == set()


class TestTheAwkwardPaths:
    def test_a_path_containing_a_space_is_staged(self, repo):
        p = repo / "experimental_notes" / "A Note.md"
        p.write_text("NEW\n", encoding="utf-8")
        line = "  experimental_notes/A Note.md: 10 -> 12  (`f`)"
        r = _feed(repo, "cdsfl_restage_from_citation_output", line + "\n")
        assert r.returncode == 0, r.stderr
        assert _staged(repo) == {"experimental_notes/A Note.md"}

    def test_a_named_path_that_does_not_exist_is_skipped_not_fatal(self, repo):
        line = "  refreshed experimental_notes/Vanished.md"
        r = _feed(repo, "cdsfl_restage_from_ledger_output", line + "\n")
        assert r.returncode == 0, "stage 0 must never be able to refuse a commit"
        assert "not a file" in r.stderr
        assert _staged(repo) == set()

    def test_several_paths_in_one_stream_all_land(self, repo):
        stdin = (CITATION_OK + "\n"
                 + "  experimental_notes/Untouched.md: 3 -> 4  (`g`)\n")
        _feed(repo, "cdsfl_restage_from_citation_output", stdin)
        assert _staged(repo) == {"experimental_notes/Note.md",
                                 "experimental_notes/Untouched.md"}


class TestItReachesTheCommit:
    """The end-to-end property, which is the only one that actually mattered."""

    def test_a_repair_run_from_a_hook_lands_in_head(self, repo):
        hooks = repo / ".git" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        hook = hooks / "pre-commit"
        hook.write_text(
            "#!/bin/sh\n"
            "set -u\n"
            f'. "{LIB}"\n'
            # Stand in for the real repairs: write the tree, print the format.
            "printf 'REPAIRED-BY-HOOK\\n' > experimental_notes/Note.md\n"
            "echo '  experimental_notes/Note.md: 1 -> 2  (`f`)' "
            "| cdsfl_restage_from_citation_output\n"
            "exit 0\n", encoding="utf-8")
        hook.chmod(0o755)
        (repo / "experimental_notes" / "Untouched.md").write_text(
            "STAGED-BY-AUTHOR\n", encoding="utf-8")
        _git(repo, "add", "experimental_notes/Untouched.md")
        _git(repo, "commit", "-q", "-m", "with the hook")

        assert _git(repo, "show", "HEAD:experimental_notes/Note.md") \
            == "REPAIRED-BY-HOOK\n", (
                "the repair did not reach the commit -- this IS the 2026-09-11 "
                "defect, and a clone of this HEAD would be broken")
        assert _git(repo, "status", "--porcelain") \
            .count("experimental_notes/Note.md") == 0, (
                "the repair landed but was left dirty as well")

    def test_without_the_restage_it_does_not(self, repo):
        """MUTATION CONTROL.  The same hook with the staging line removed must
        FAIL to reach HEAD, or the test above proves nothing."""
        hooks = repo / ".git" / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        hook = hooks / "pre-commit"
        hook.write_text(
            "#!/bin/sh\n"
            "printf 'REPAIRED-BY-HOOK\\n' > experimental_notes/Note.md\n"
            "exit 0\n", encoding="utf-8")
        hook.chmod(0o755)
        (repo / "experimental_notes" / "Untouched.md").write_text(
            "STAGED-BY-AUTHOR\n", encoding="utf-8")
        _git(repo, "add", "experimental_notes/Untouched.md")
        _git(repo, "commit", "-q", "-m", "without the restage")

        assert _git(repo, "show", "HEAD:experimental_notes/Note.md") == "BEFORE\n", (
            "the defect did not reproduce, so the positive test above is not "
            "measuring what it claims")
        assert "experimental_notes/Note.md" in _git(repo, "status", "--porcelain")


class TestThePartialCommitNotice:
    def test_a_temporary_index_is_announced(self, repo, tmp_path):
        fake = tmp_path / "next-index-1234.lock"
        fake.write_bytes((repo / ".git" / "index").read_bytes())
        r = subprocess.run(
            ["sh", "-c", f'. "{LIB}"\ncdsfl_warn_if_partial_commit\n'],
            cwd=repo, capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin",
                 "GIT_INDEX_FILE": str(fake)})
        assert r.returncode == 0, "a notice must never refuse a commit"
        assert "pathspec commit" in r.stderr

    def test_an_ordinary_commit_is_silent(self, repo):
        r = subprocess.run(
            ["sh", "-c", f'. "{LIB}"\ncdsfl_warn_if_partial_commit\n'],
            cwd=repo, capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin",
                 "GIT_INDEX_FILE": ".git/index"})
        assert r.stderr == "", (
            "a notice on the ordinary case teaches people to ignore it")

    def test_the_real_index_path_is_not_derived_from_the_variable(self, repo,
                                                                  tmp_path):
        """THE CHECK THAT COULD NOT FAIL, caught on 2026-09-11 by this file.

        The first version asked `git rev-parse --git-path index` for the real
        index.  That command RETURNS $GIT_INDEX_FILE verbatim when the variable
        is set, so it compared the variable with itself and returned "ordinary
        commit" for every input, temporary index included.  `sh -x` showed it:
        `_real=` resolved to the fake lock path that had just been exported.

        This case pins the property the bug violated -- the answer must depend
        on the variable's VALUE, not merely echo it -- using git's own naming
        for a pathspec commit's temporary index, measured in a scratch
        repository: `.git/next-index-<pid>.lock`.
        """
        fake = repo / ".git" / "next-index-27618.lock"
        fake.write_bytes((repo / ".git" / "index").read_bytes())
        r = subprocess.run(
            ["sh", "-c", f'. "{LIB}"\ncdsfl_warn_if_partial_commit\n'],
            cwd=repo, capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin",
                 "GIT_INDEX_FILE": str(fake)})
        assert r.returncode == 0
        assert "pathspec commit" in r.stderr, (
            "the notice is silent on git's own temporary-index name, so it can "
            "never fire on the case it exists for")

    @pytest.mark.parametrize("name", ["index.lock", "index"])
    def test_the_real_index_and_its_lock_are_silent(self, repo, name):
        """`index.lock` IS THE REAL INDEX, and both panel seats found this.

        Measured from a live hook, git 2.50.1:

            git commit           .git/index                      real index
            git commit --amend   .git/index                      real index
            git commit -a        <gitdir>/index.lock             real index
            git commit -- <path> <gitdir>/next-index-<pid>.lock  TEMPORARY

        Without the index.lock escape EVERY `git commit -am` was told "this is a
        pathspec commit" and that files outside the pathspec would land -- both
        false, on the commonest commit command there is. The first version of
        this notice could never fire; that one fired when it must not."""
        path = repo / ".git" / name
        r = subprocess.run(
            ["sh", "-c", f'. "{LIB}"\ncdsfl_warn_if_partial_commit\n'],
            cwd=repo, capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin",
                 "GIT_INDEX_FILE": str(path)})
        assert r.stderr == "", (
            f"the notice fired on {name}, which is the real index")

    def test_every_commit_form_is_judged_correctly_end_to_end(self, repo):
        """EXECUTED through real `git commit` invocations, not set variables.

        A version change that renamed either index would fail this test rather
        than silently passing -- which is what the string comparison alone
        would do."""
        hooks = repo / "hooks"
        hooks.mkdir(parents=True, exist_ok=True)
        (hooks / "stage0_restage.sh").write_text(
            LIB.read_text(encoding="utf-8"), encoding="utf-8")
        hook = hooks / "pre-commit"
        hook.write_text("#!/bin/sh\n"
                        ". hooks/stage0_restage.sh\n"
                        "cdsfl_warn_if_partial_commit\n"
                        "exit 0\n", encoding="utf-8")
        hook.chmod(0o755)
        _git(repo, "config", "core.hooksPath", "hooks")
        a = repo / "experimental_notes" / "Note.md"
        b = repo / "experimental_notes" / "Untouched.md"

        def commit(*args) -> str:
            r = subprocess.run(["git", "commit", *args], cwd=repo,
                               capture_output=True, text=True, timeout=300)
            return r.stdout + r.stderr

        a.write_text("1\n", encoding="utf-8")
        b.write_text("1\n", encoding="utf-8")
        _git(repo, "add", "-A")
        assert "pathspec commit" not in commit("-q", "-m", "plain")

        a.write_text("2\n", encoding="utf-8")
        assert "pathspec commit" not in commit("-q", "-a", "-m", "dash-a"), (
            "git commit -a was called a pathspec commit")

        a.write_text("3\n", encoding="utf-8")
        b.write_text("3\n", encoding="utf-8")
        assert "pathspec commit" in commit(
            "-q", "-m", "pathspec", "--", "experimental_notes/Untouched.md"), (
            "a real pathspec commit was NOT announced, so the notice has become "
            "one that cannot fire")

    def test_it_is_silent_when_git_sets_nothing(self, repo):
        r = subprocess.run(
            ["sh", "-c", f'. "{LIB}"\ncdsfl_warn_if_partial_commit\n'],
            cwd=repo, capture_output=True, text=True,
            env={"PATH": "/usr/bin:/bin:/usr/local/bin"})
        assert r.stderr == ""


class TestPartialStagingStagesOnlyTheDelta:
    """`git add -- <path>` stages the WHOLE file.

    Both panel seats found this independently on 2026-09-11 and each built a
    fix. They disagreed on the mechanism, and the disagreement was settled by
    MEASUREMENT rather than by argument -- repair at a varying distance from the
    author's unstaged hunk, 8-line file, real index:

        gap  3-way `git merge-file`   zero-context `git apply --cached`
         0   CONFLICT                 FAILED            (same line, no answer)
         1   CONFLICT                 OK, WIP excluded
         2   OK                       OK
         3   OK                       OK

    Zero-context apply succeeds everywhere merge-file does AND at gap 1, which
    is the common geometry: a citation repair 1 line from an edit in progress.
    """

    #: The author's WIP is on line 4 of an 8-line file.
    WIP_LINE = 4

    def _repo_with_partial_staging(self, repo: Path, gap: int) -> Path:
        f = repo / "experimental_notes" / "Note.md"
        f.write_text("".join(f"L{i} original\n" for i in range(1, 9)),
                     encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "--no-verify", "-m", "eight lines")
        lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
        lines[0] = "L1 AUTHOR-STAGED\n"
        f.write_text("".join(lines), encoding="utf-8")
        _git(repo, "add", "experimental_notes/Note.md")
        lines[self.WIP_LINE - 1] = "L4 AUTHOR-WIP\n"
        f.write_text("".join(lines), encoding="utf-8")
        return f

    def _snapshot_repair_and_stage(self, repo: Path, f: Path, gap: int
                                   ) -> subprocess.CompletedProcess:
        """Snapshot BEFORE the repair writes, exactly as hooks/pre-commit does."""
        script = (f'. "{LIB}"\n'
                  'cdsfl_snapshot_partially_staged\n'
                  'python3 "$1" "$2" "$3" "$4"\n'
                  'printf "experimental_notes/Note.md\\n" | cdsfl_restage_paths\n'
                  'cdsfl_snapshot_cleanup\n')
        editor = repo / "edit.py"
        editor.write_text(
            "import pathlib, sys\n"
            "p = pathlib.Path(sys.argv[1]); gap = int(sys.argv[2])\n"
            "lines = p.read_text().splitlines(keepends=True)\n"
            "i = int(sys.argv[3]) - 1 + gap\n"
            "lines[i] = f'L{i+1} REPAIRED\\n'\n"
            "p.write_text(''.join(lines))\n", encoding="utf-8")
        return subprocess.run(
            ["sh", "-c", script, "sh", str(editor), str(f), str(gap),
             str(self.WIP_LINE)],
            cwd=repo, capture_output=True, text=True)

    def _index(self, repo: Path) -> str:
        return _git(repo, "show", ":experimental_notes/Note.md")

    @pytest.mark.parametrize("gap", [1, 2, 3])
    def test_the_delta_lands_and_the_withheld_hunk_does_not(self, repo, gap):
        f = self._repo_with_partial_staging(repo, gap)
        r = self._snapshot_repair_and_stage(repo, f, gap)
        idx = self._index(repo)
        assert "REPAIRED" in idx, f"the repair did not reach the index\n{r.stderr}"
        assert "AUTHOR-WIP" not in idx, (
            "the author's withheld hunk was swept into the commit -- this is "
            "the defect both seats found")
        assert "L1 AUTHOR-STAGED" in idx, (
            "the author's own staged edit was lost")
        assert "staged only the repair's delta" in r.stdout, r.stdout

    def test_a_collision_on_the_same_line_refuses_rather_than_guessing(self, repo):
        """gap 0: the repair and the withheld hunk touch the SAME line. There is
        no right answer without asking, so it must not stage either."""
        f = self._repo_with_partial_staging(repo, 0)
        r = self._snapshot_repair_and_stage(repo, f, 0)
        idx = self._index(repo)
        assert "REPAIRED" not in idx
        assert "AUTHOR-WIP" not in idx
        assert "L1 AUTHOR-STAGED" in idx, "the author's staged edit was disturbed"
        assert "will lag 1 commit behind" in r.stderr, r.stderr

    def test_the_working_tree_is_never_touched(self, repo):
        """The index is the only thing written. If the hook dies there is
        nothing to lose, which is why this is not a stash."""
        f = self._repo_with_partial_staging(repo, 2)
        before = f.read_text(encoding="utf-8")
        self._snapshot_repair_and_stage(repo, f, 2)
        after = f.read_text(encoding="utf-8")
        assert "AUTHOR-WIP" in after and "REPAIRED" in after
        assert after != before, "the probe did not actually repair anything"

    def test_the_mechanism_being_replaced_really_does_sweep(self, repo):
        """MUTATION CONTROL, on the RIGHT mutation.

        The first version of this control dropped the snapshot and expected the
        sweep to reappear. It does not: with no snapshot
        `cdsfl_stage_repair_delta` returns non-zero and the file -- being
        partially staged -- takes the REFUSE branch, which is also safe. That is
        worth knowing (the fix degrades to a visible lag, not to the defect),
        but it tests nothing about the sweep.

        The mechanism the fix REPLACES is a plain `git add` on the same state.
        This runs exactly that and requires the withheld hunk to land, so the
        delta tests above are measured against a defect that genuinely
        reproduces.
        """
        f = self._repo_with_partial_staging(repo, 2)
        lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
        lines[self.WIP_LINE + 1] = "L6 REPAIRED\n"
        f.write_text("".join(lines), encoding="utf-8")
        _git(repo, "add", "--", "experimental_notes/Note.md")
        idx = self._index(repo)
        assert "AUTHOR-WIP" in idx, (
            "a plain `git add` did NOT sweep the withheld hunk in, so the "
            "delta tests above are not measuring against a real defect")
        assert "REPAIRED" in idx

    def test_a_path_containing_a_space_takes_the_delta_path(self, repo):
        """A GAP A PANEL SEAT NAMED AS UNCHECKED, and it was real.

        The POSIX intersection used `for _b in $_both`, which WORD-SPLITS. A
        path with a space became several words, matched nothing, was never
        snapshotted, and the file therefore took the collision branch --
        printing "the repair collides with a hunk you left out" when nothing had
        collided, and leaving the repair a commit behind. It fails SAFE, but the
        repair does not land and the message is false.
        """
        f = repo / "experimental_notes" / "A Note With Spaces.md"
        f.write_text("".join(f"L{i} original\n" for i in range(1, 9)),
                     encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "--no-verify", "-m", "spaced")
        lines = f.read_text(encoding="utf-8").splitlines(keepends=True)
        lines[0] = "L1 AUTHOR-STAGED\n"
        f.write_text("".join(lines), encoding="utf-8")
        _git(repo, "add", "experimental_notes/A Note With Spaces.md")
        lines[3] = "L4 AUTHOR-WIP\n"
        f.write_text("".join(lines), encoding="utf-8")

        script = (f'. "{LIB}"\n'
                  'cdsfl_snapshot_partially_staged\n'
                  'python3 -c "import pathlib,sys; p=pathlib.Path(sys.argv[1]); '
                  "l=p.read_text().splitlines(keepends=True); l[5]='L6 REPAIRED\\n'; "
                  'p.write_text(str().join(l))" "$1"\n'
                  'printf "%s\\n" "experimental_notes/A Note With Spaces.md" '
                  '| cdsfl_restage_paths\n'
                  'cdsfl_snapshot_cleanup\n')
        r = subprocess.run(["sh", "-c", script, "sh", str(f)], cwd=repo,
                           capture_output=True, text=True)
        idx = _git(repo, "show", ":experimental_notes/A Note With Spaces.md")
        assert "REPAIRED" in idx, f"{r.stdout}\n{r.stderr}"
        assert "AUTHOR-WIP" not in idx
        assert "L1 AUTHOR-STAGED" in idx

    def test_a_repair_that_changed_nothing_says_nothing(self, repo):
        """P-PASS ON THIS FIX, and it found a false alarm.

        `cdsfl_stage_repair_delta` returned 1 for an EMPTY patch, which is the
        same code as a failed apply, so a repair that reported a path without
        changing it made the hook announce a collision. Nothing collided and
        nothing needed staging. A guard that cries wolf on the ordinary case
        decays the same way as one that cannot fire.
        """
        f = repo / "experimental_notes" / "Note.md"
        f.write_text("L1 original\nL2 original\nL3 original\n", encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "--no-verify", "-m", "three")
        f.write_text("L1 STAGED\nL2 original\nL3 original\n", encoding="utf-8")
        _git(repo, "add", "experimental_notes/Note.md")
        f.write_text("L1 STAGED\nL2 original\nL3 WIP\n", encoding="utf-8")

        script = (f'. "{LIB}"\n'
                  'cdsfl_snapshot_partially_staged\n'
                  'printf "experimental_notes/Note.md\\n" | cdsfl_restage_paths\n'
                  'cdsfl_snapshot_cleanup\n')
        r = subprocess.run(["sh", "-c", script], cwd=repo, capture_output=True,
                           text=True)
        assert "collides" not in r.stderr, (
            f"a repair that changed nothing was reported as a collision:\n"
            f"{r.stderr}")
        assert r.stderr.strip() == "", r.stderr

    def test_a_file_that_is_not_partially_staged_uses_the_plain_add(self, repo):
        """REGRESSION. The narrow path is added BESIDE the old one, not over it:
        the ordinary case must behave exactly as before."""
        r = _feed(repo, "cdsfl_restage_from_ledger_output", LEDGER_OK + "\n")
        assert "re-staged experimental_notes/EXPERIMENT_RUN_LEDGER.md" in r.stdout
        assert "delta" not in r.stdout


class TestPartialStagingIsAnnounced:
    """SUPERSEDED IN SUBSTANCE, KEPT AS THE RECORD OF A WEAKER FIX.

    For 2 hours the helper STAGED THE WHOLE FILE and printed a notice saying so,
    on the argument that a visible extra hunk beats a silent broken clone. Both
    panel seats rejected that as insufficient within the hour and each delivered
    a delta-staging fix; the class above is the measured result. What remains
    asserted here is that the ordinary cases stay SILENT, because a notice on
    the ordinary case teaches people to ignore it.
    """

    def test_a_file_with_nothing_staged_is_silent(self, repo):
        r = _feed(repo, "cdsfl_restage_from_citation_output", CITATION_OK + "\n")
        assert "partially staged" not in r.stderr, r.stderr

    def test_a_fully_staged_file_is_silent(self, repo):
        _git(repo, "add", "experimental_notes/Note.md")
        r = _feed(repo, "cdsfl_restage_from_citation_output", CITATION_OK + "\n")
        assert "partially staged" not in r.stderr, r.stderr


class TestTheHookActuallyCallsIt:
    """WIRING.  An addition nothing reaches is not additive."""

    def test_both_repairs_pipe_into_the_helper(self):
        text = HOOK.read_text(encoding="utf-8")
        for fn in ("cdsfl_restage_from_ledger_output",
                   "cdsfl_restage_from_citation_output"):
            assert f"| {fn}" in text, (
                f"the hook no longer pipes a repair's output into {fn}, so that "
                f"repair is back to lagging 1 commit behind")

    def test_the_helper_is_sourced(self):
        assert '. "$RESTAGE_LIB"' in HOOK.read_text(encoding="utf-8")

    def test_the_snapshot_runs_BEFORE_any_repair_writes(self):
        """Order is the whole mechanism: a snapshot taken after a repair has
        already written records the repaired file as the author's own work."""
        text = HOOK.read_text(encoding="utf-8")
        snap = text.index("cdsfl_snapshot_partially_staged")
        for script in ("scripts/experiment_run_ledger.py",
                       "scripts/citation_content_guard_2026-09-10.py"):
            assert snap < text.index(f"if [ -f {script} ]"), (
                f"the snapshot runs after {script}, so it captures the REPAIRED "
                f"file and the delta comes out empty")
        assert text.index("cdsfl_snapshot_cleanup") > snap


class TestAMissingHelperRefuses:
    """A guard that cannot fail is not a guard: if the helper were merely
    optional, deleting it would silently restore the defect."""

    def _scratch_with_hook(self, tmp_path: Path, with_lib: bool) -> Path:
        r = tmp_path / "hookrepo"
        (r / "hooks").mkdir(parents=True)
        subprocess.run(["git", "init", "-q", "."], cwd=r, check=True)
        (r / "hooks" / "pre-commit").write_text(
            HOOK.read_text(encoding="utf-8"), encoding="utf-8")
        (r / "hooks" / "pre-commit").chmod(0o755)
        if with_lib:
            (r / "hooks" / "stage0_restage.sh").write_text(
                LIB.read_text(encoding="utf-8"), encoding="utf-8")
        return r

    def test_it_refuses_and_says_why(self, tmp_path):
        r = self._scratch_with_hook(tmp_path, with_lib=False)
        p = subprocess.run(["sh", "hooks/pre-commit"], cwd=r,
                           capture_output=True, text=True, timeout=120)
        assert p.returncode == 1
        assert "stage0_restage.sh is missing" in p.stderr
        assert "every clone at HEAD" in p.stderr

    def test_with_the_helper_present_it_gets_past_that_check(self, tmp_path):
        """POSITIVE CONTROL.  The scratch repo has no guard files, so the hook
        still exits 1 -- but for a DIFFERENT, later reason.  Without this, the
        test above would pass even if the hook refused everything always."""
        r = self._scratch_with_hook(tmp_path, with_lib=True)
        p = subprocess.run(["sh", "hooks/pre-commit"], cwd=r,
                           capture_output=True, text=True, timeout=120)
        assert "stage0_restage.sh is missing" not in p.stderr
        assert "guard file(s) missing" in p.stderr, p.stderr
