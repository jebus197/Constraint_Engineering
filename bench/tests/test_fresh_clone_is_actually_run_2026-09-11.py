"""A2's claim is "the suite passes in a fresh clone". Something must CLONE.

WHAT WAS MISSING, and it is the reason the claim was wrong twice. A2's declared
evidence, `bench/tests/test_fresh_clone_suite_2026-09-10.py`, guards the
individual repairs -- the replay rebase, the onboarding stamp, the archive-root
predicate -- and clones nothing. `scripts/fresh_clone_census_2026-09-10.py`
re-runs the named tests in THIS checkout, the tree whose greenness was never in
doubt. Both instruments were sound, both were about A2, and neither could see
A2's claim. So the claim was made on 2026-09-10 and again on 2026-09-11 and was
false both times, found each time by a person cloning by hand:

    clone at HEAD   3 failed, 6952 passed, 38 skipped, 1 xfailed
    working tree    6988 passed, 0 failed

`scripts/fresh_clone_suite_2026-09-11.py` performs the clone. This file runs it
end to end -- clone, pytest, parse, exit code -- on ONE fast test file, because
the machinery is what rots, and a machine that has never been run is the
condition this whole task is about.

COST, measured 2026-09-11 on this machine: the clone is 6.58 s and 549 MB with
`--no-hardlinks`, and the chosen test file is 0.58 s. The full-suite mode is
roughly 25 minutes and is deliberately NOT run here; it is a command a person
runs, and the task-list entry quotes its output with the HEAD it was run at.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "fresh_clone_suite_2026-09-11.py"

#: 0.58 s in this tree, and it touches only the task list and the marker parser.
FAST_TARGET = "bench/tests/test_precommit_stage0_order_2026-09-10.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("fresh_clone", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        spec.loader.exec_module(m)
    finally:
        sys.path.remove(str(REPO / "scripts"))
    return m


class TestItActuallyClonesAndRuns:
    def test_a_green_target_reports_green_from_the_clone(self, mod):
        """THE END-TO-END PATH. If this passes, the instrument works; if it is
        ever skipped or deleted, A2 is back to a claim nobody can check."""
        code, line, failures = mod.run([FAST_TARGET], timeout=1800)
        assert code == 0, f"{line}\n{failures}"
        assert "passed" in line, line
        assert failures == "", failures

    def test_it_refuses_a_clone_at_a_different_commit(self, mod, monkeypatch):
        """ANTI-VACUITY on the identity check. A measurement of a DIFFERENT
        commit reported as this one's is the defect the whole task is about."""
        monkeypatch.setattr(mod, "head", lambda repo=None: "0" * 40)
        with pytest.raises(SystemExit) as e:
            mod.run([FAST_TARGET], timeout=600)
        assert "different" in str(e.value)


class TestItSaysWhetherTheTreeIsClean:
    """A clone measures HEAD. A green clone with a dirty tree says nothing about
    what the next commit will ship, and that gap hid the 2026-09-11 defect for 2
    days."""

    def test_a_clean_scratch_repository_reads_clean(self, mod, tmp_path):
        r = tmp_path / "repo"
        r.mkdir()
        subprocess.run(["git", "init", "-q", "."], cwd=r, check=True)
        subprocess.run(["git", "config", "user.email", "t@e.invalid"], cwd=r, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=r, check=True)
        (r / "a.txt").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=r, check=True)
        subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "c"], cwd=r, check=True)
        clean, why = mod.working_tree_is_clean(r)
        assert clean is True and why == "clean"

    def test_an_uncommitted_edit_reads_dirty_and_names_the_file(self, mod, tmp_path):
        r = tmp_path / "repo"
        r.mkdir()
        subprocess.run(["git", "init", "-q", "."], cwd=r, check=True)
        subprocess.run(["git", "config", "user.email", "t@e.invalid"], cwd=r, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=r, check=True)
        (r / "a.txt").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=r, check=True)
        subprocess.run(["git", "commit", "-q", "--no-verify", "-m", "c"], cwd=r, check=True)
        (r / "a.txt").write_text("y\n", encoding="utf-8")
        clean, why = mod.working_tree_is_clean(r)
        assert clean is False
        assert "a.txt" in why

    def test_a_failing_git_is_UNKNOWN_not_clean(self, mod, tmp_path):
        """NOT `returncode == 0 and not stdout`. This project read exit 128 with
        empty output as "clean" once and as "untracked" once, 1 round apart."""
        not_a_repo = tmp_path / "plain"
        not_a_repo.mkdir()
        clean, why = mod.working_tree_is_clean(not_a_repo)
        assert clean is False
        assert "UNKNOWN" in why, why


class TestTheResultLineParser:
    @pytest.mark.parametrize("blob,expected", [
        ("3 failed, 6952 passed, 38 skipped, 1 xfailed in 1478.12s",
         "3 failed, 6952 passed, 38 skipped, 1 xfailed in 1478.12s"),
        ("6988 passed in 1401.55s (0:23:21)", "6988 passed in 1401.55s (0:23:21)"),
        ("2 errors in 0.51s", "2 errors in 0.51s"),
    ])
    def test_it_finds_the_result_line(self, mod, blob, expected):
        assert mod._RESULT_RE.findall("noise\n" + blob + "\nmore noise")[-1] \
            .strip() == expected

    def test_a_run_with_no_result_line_says_so_rather_than_inventing_one(self, mod):
        assert mod._RESULT_RE.findall("collected 0 items\n") == []


class TestTheHelperIsNotUsedWhereArgparseAlreadyWorks:
    """A TRAP WALKED INTO WHILE WRITING THIS SCRIPT, so it is pinned.

    The first draft called `answer_help` at the top of `main()` AND built an
    argparse parser below it. `answer_help` answers first, so `--help` printed
    `usage: fresh_clone_suite_2026-09-11.py [-h]` and hid --subset, --only,
    --keep and --timeout from the reader. The helper exists for scripts with NO
    parser; using it where argparse already works makes the help text worse,
    which is the opposite of its purpose."""

    def test_no_script_uses_both(self):
        offenders = []
        for p in sorted((REPO / "scripts").glob("*.py")):
            src = p.read_text(encoding="utf-8")
            if "answer_help(" in src and "ArgumentParser" in src:
                offenders.append(p.name)
        assert not offenders, (
            f"{offenders} call answer_help AND build an argparse parser. "
            f"answer_help answers --help first, so argparse's flag list never "
            f"reaches the reader. Drop the answer_help call; argparse already "
            f"does the job.")

    def test_this_script_lists_its_real_flags(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"],
                           capture_output=True, text=True, timeout=300, cwd=REPO)
        assert r.returncode == 0
        for flag in ("--subset", "--only", "--keep", "--timeout"):
            assert flag in r.stdout, f"--help does not mention {flag}"


class TestTheTranscriptSurvives:
    """A clone run that reports only WHICH test failed discards the evidence.

    MEASURED 2026-09-11. The I38 artefact-classifier flake reproduced in a clone
    at `37cc328` -- the FIRST reproduction since diagnostics were added to its
    assertion for exactly that moment -- and the run reported the test's name and
    nothing else. The diagnostics built to be read from a log could not be read
    from the log, which is why I38 stayed OBSERVED rather than diagnosed across
    7 full-size runs.

    An instrument that discards the evidence it was extended to capture is the
    same shape as a scanner reporting a false zero: it answers, and the answer is
    missing the thing you needed.
    """

    def test_the_full_output_is_written_somewhere(self, tmp_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("fcs", SCRIPT)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        dest = tmp_path / "transcript.txt"
        rc, line, _shown = m.run(["bench/tests/test_flake_rate_2026-09-11.py"],
                                 timeout=1800, transcript=dest)
        assert dest.is_file(), "the clone run kept no transcript"
        blob = dest.read_text(encoding="utf-8")
        assert "passed" in blob, blob[:300]
        # ANTI-VACUITY: the transcript must be the pytest output, not the summary
        # line the caller already had.
        assert len(blob) > len(line) + 40, (len(blob), len(line))

    def test_a_failure_keeps_its_assertion_detail(self, tmp_path):
        """The property that matters. A name is not a diagnosis."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("fcs", SCRIPT)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        dest = tmp_path / "t.txt"
        # A file that FAILS in a clone at this HEAD would make this exact, but
        # the set changes; so force a failure that cannot depend on the tree.
        rc, _line, _shown = m.run(["bench/tests/does_not_exist_at_all.py"],
                                  timeout=900, transcript=dest)
        assert rc != 0
        blob = dest.read_text(encoding="utf-8")
        assert "does_not_exist_at_all" in blob, (
            "the transcript does not name what went wrong, so a reader still "
            "cannot diagnose from it")
