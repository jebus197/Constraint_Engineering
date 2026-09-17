"""Task A6: two unmeasured classes, measured. Both came back better than feared.

I11 -- A SOURCE-TEXT TEST BREAKS ON AN EDIT THAT CHANGES NOTHING IT ASSERTS.
This is `execute-do-not-grep`'s converse and it is not hypothetical: it fired 4
times on 2026-09-10 and 09-11, every time on a CORRECT change, and twice on
guards written the same day they broke. Every instance was a COMMENT GROWING
under a window, an index, or a body slice.

  Census: 70 of 5026 test functions assert that a literal appears in the text of
  a Python source file -- 1.3928%, Wilson [1.1039%, 1.7559%].

  Experiment, against `bench/reference_runner_v3.py` and the 84 test files that
  name it. An inert comment APPENDED AFTER THE LAST LINE reddens **0 of 84**,
  0.0000%, Wilson [0.0000%, 4.3732%]: no test in this suite asserts on the
  runner's raw bytes. An inert comment INSERTED INSIDE A FUNCTION reddens 2 of
  84, 2.3810%, Wilson [0.6554%, 8.2714%] -- and both are LEGITIMATE, because
  `test_citation_content` and `test_experiment_run_ledger` cite the runner BY
  LINE NUMBER and noticing that lines moved is their job. Both are repaired at
  stage 0 of the pre-commit hook.

I13 -- A TEST IS GREEN BECAUSE A NEIGHBOUR CATCHES THE REGRESSION. Measured by
destroying a function outright (`return None`) and asking which of the files
naming it go red.

  First answer: 11 of 37 "claimants" survived, 29.7297%. THAT NUMBER WAS WRONG
  AND A 15-MINUTE READ OF 3 SURVIVORS REFUTED IT. All 3 were correct:
  `test_fix_complexity` asserts `"compute_rk" not in called` -- it names the
  symbol to require it is NOT called; `test_target_complexity_is_reported`
  AST-scans for CALL SITES, which emptying a function does not move; and
  `test_instrument_gaps_from_panel`'s own docstring RECORDS a prior mutation
  study of the same function.

  So "names it" is a bad proxy for "claims to cover it". Refined to files that
  actually CALL the symbol: **0 of 22 survived, 0.0000%, Wilson [0.0000%,
  14.8655%], Clopper-Pearson [0.0000%, 15.4373%]**.

  I13 IS NOT SUPPORTED OVER THIS SAMPLE, and the boundary is stated rather than
  buried: 5 functions in 1 module. The upper bound is 15%, not 0, and a wider
  sweep could still find instances. What is settled is that the alarming figure
  was an artefact of the proxy.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CENSUS = ROOT / "scripts" / "source_text_assertions_2026-09-11.py"
FRAGILITY = ROOT / "scripts" / "source_text_fragility_2026-09-11.py"
NEIGHBOUR = ROOT / "scripts" / "neighbour_catches_it_2026-09-11.py"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


class TestTheCensusDetectorSeesItsOwnWorkedExamples:
    """THE CONTROL THAT MADE THE CENSUS TRUSTWORTHY, and it failed first.

    The detector tracked only names bound DIRECTLY to `read_text()`. Built from
    3 of the 4 guards that actually broke here, the control detected 1 of 3 --
    so `51 of 5026` was a fact about the detector. A census whose instrument
    cannot see its own worked examples measures the instrument.
    """

    def _probe(self, tmp_path):
        d = tmp_path / "bench" / "tests"
        d.mkdir(parents=True)
        (d / "test_probe.py").write_text(
            "from pathlib import Path\n"
            "REPO = Path('.')\n"
            "SRC = (REPO / 'hooks' / 'pre-commit').read_text()\n"
            "\n"
            "def test_window_form():\n"
            "    src = (REPO / 'bench' / 'reference_runner_v3.py').read_text()\n"
            "    window = src[10:410]\n"
            "    assert 'literal' in window\n"
            "\n"
            "def test_body_slice_form():\n"
            "    src = (REPO / 'bench' / 'x.py').read_text()\n"
            "    body = src[src.index('def f'):]\n"
            "    assert 'literal' in body\n"
            "\n"
            "def test_module_level_form():\n"
            "    assert 'GUARDS=' in SRC\n",
            encoding="utf-8")
        return d

    def test_all_three_shapes_are_detected(self, tmp_path):
        m = _load(CENSUS, "census_probe")
        m.TESTS = self._probe(tmp_path)
        rows, total = m.survey()
        assert total == 3, total
        found = {r[1] for r in rows}
        assert found == {"test_window_form", "test_body_slice_form",
                         "test_module_level_form"}, found

    def test_a_test_that_calls_code_is_not_flagged(self, tmp_path):
        """ANTI-VACUITY. A detector that flagged everything would 'detect' the
        3 shapes above and mean nothing."""
        m = _load(CENSUS, "census_probe2")
        d = tmp_path / "bench" / "tests"
        d.mkdir(parents=True)
        (d / "test_clean.py").write_text(
            "from bench.repo_paths import is_archived_run_output\n"
            "\n"
            "def test_it_executes():\n"
            "    assert is_archived_run_output('bench/logs/x') is True\n",
            encoding="utf-8")
        m.TESTS = d
        rows, total = m.survey()
        assert total == 1 and rows == [], rows


class TestTheCensusIsCurrent:
    def test_the_class_has_not_grown_silently(self):
        """A RATCHET, not a pin. The count may fall freely; a RISE means a new
        source-text assertion was written and should be justified in its own
        docstring rather than arriving unnoticed.
        """
        m = _load(CENSUS, "census_live")
        rows, total = m.survey()
        assert total > 4000, f"only {total} test functions scanned"
        assert len(rows) <= 80, (
            f"{len(rows)} source-text assertions, up from the 70 measured on "
            f"2026-09-11. Re-read scripts/source_text_assertions_2026-09-11.py's "
            f"docstring before raising this number: 4 guards of this class broke "
            f"on CORRECT changes in a single day.")

    def test_the_census_runs(self):
        r = subprocess.run([sys.executable, str(CENSUS)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-400:]
        assert "CENSUS, NOT A VERDICT" in r.stdout


#: Arguments that make each script mutate `mod.py` in a scratch repository.
_SCRIPT_ARGS = {
    FRAGILITY.name: ["--target", "mod.py", "--mode", "eof"],
    NEIGHBOUR.name: ["--module", "mod.py", "--symbol", "f"],
}
_COMMITTED_MOD = "def f():\n    return 1\n"
_UNCOMMITTED_LINE = "# UNCOMMITTED WORK the refusal exists to protect\n"


def _git_env():
    """The parent environment minus GIT_*: under the pre-commit hook GIT_INDEX_FILE
    and GIT_DIR point at the REAL repository, and a scratch `git` must not use them."""
    import os
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _scratch_repo(tmp_path, script):
    """A git repository holding a copy of `script` (so its REPO is this tree), a
    committed `mod.py` and 1 committed test file that names and calls it."""
    import shutil
    if shutil.which("git") is None:
        pytest.skip("git is not on PATH")
    repo = tmp_path / "repo"
    (repo / "scripts").mkdir(parents=True)
    (repo / "bench" / "tests").mkdir(parents=True)
    copy = repo / "scripts" / script.name
    shutil.copy(script, copy)
    (repo / "mod.py").write_text(_COMMITTED_MOD, encoding="utf-8")
    (repo / "bench" / "tests" / "test_x.py").write_text(
        "# covers mod.py\nimport sys, pathlib\n"
        "sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))\n"
        "from mod import f\n\n\ndef test_f():\n    assert f() == 1\n",
        encoding="utf-8")
    # Loading the copy in-process writes scripts/__pycache__/, which would make
    # the tree dirty and turn every run into a refusal.
    (repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    env = _git_env()
    for args in (["init", "-q"], ["add", "-A"],
                 ["-c", "user.name=t", "-c", "user.email=t@example.invalid",
                  "-c", "commit.gpgsign=false", "commit", "-q", "--no-verify",
                  "-m", "base"]):
        r = subprocess.run(["git", *args], cwd=repo, env=env,
                           capture_output=True, text=True)
        assert r.returncode == 0, f"git {args} -> {r.returncode}\n{r.stderr}"
    return repo, copy


class TestTheExperimentsRefuseToRunUnsafely:
    """Both scripts mutate a TRACKED file and revert with `git checkout --`.

    EXECUTED, not read (panel round 16, 2026-09-17). The test this replaces
    asserted that `REFUSING`, `git checkout` and `finally:` appear in each
    script's text, inside the file whose subject is that such assertions do not
    test behaviour. A copy of either script with its first `tree_is_clean()`
    check disabled kept all 3 strings, passed, and then destroyed an
    uncommitted edit. Both properties are now run: the refusal on a dirty tree,
    and the revert when the mutated run raises."""

    @pytest.mark.parametrize("script", [FRAGILITY, NEIGHBOUR], ids=lambda p: p.stem)
    def test_a_dirty_tree_is_refused(self, script, tmp_path):
        repo, copy = _scratch_repo(tmp_path, script)
        (repo / "mod.py").write_text(_COMMITTED_MOD + _UNCOMMITTED_LINE,
                                     encoding="utf-8")
        r = subprocess.run([sys.executable, str(copy), *_SCRIPT_ARGS[script.name]],
                           cwd=repo, env=_git_env(), capture_output=True,
                           text=True, timeout=300)
        survived = _UNCOMMITTED_LINE in (repo / "mod.py").read_text(encoding="utf-8")
        assert survived, (
            f"{script.name} ran on a dirty tree and its `git checkout --` revert "
            f"destroyed uncommitted work (exit {r.returncode})")
        assert r.returncode == 2 and "REFUSING" in r.stderr, (
            f"{script.name} did not refuse a dirty tree: exit {r.returncode}\n"
            f"{r.stderr[-2000:]}")

    @pytest.mark.parametrize("script", [FRAGILITY, NEIGHBOUR], ids=lambda p: p.stem)
    def test_the_revert_runs_when_the_mutated_run_raises(self, script, tmp_path,
                                                         monkeypatch):
        """The `finally`, executed: the 2nd test run (the one made while the
        target is mutated) raises, and the target must still be restored."""
        repo, copy = _scratch_repo(tmp_path, script)
        for k in [k for k in __import__("os").environ if k.startswith("GIT_")]:
            monkeypatch.delenv(k)
        m = _load(copy, f"revert_{script.stem}")
        assert m.REPO == repo, f"the copy resolved REPO to {m.REPO}, not the scratch tree"
        calls = []

        def run(paths, timeout=3600):
            calls.append(list(paths))
            if len(calls) == 2:
                assert (repo / "mod.py").read_text(encoding="utf-8") != _COMMITTED_MOD, (
                    "the 2nd run was reached with the target unmutated")
                raise RuntimeError("injected failure during the mutated run")
            return (0, []) if script == FRAGILITY else []

        monkeypatch.setattr(m, "run", run)
        monkeypatch.setattr(sys, "argv", [str(copy), *_SCRIPT_ARGS[script.name]])
        with pytest.raises(RuntimeError, match="injected failure"):
            m.main()
        assert len(calls) == 2, f"the run was not reached as expected: {calls}"
        assert (repo / "mod.py").read_text(encoding="utf-8") == _COMMITTED_MOD, (
            f"{script.name} left the target mutated after an exception mid-run")

    def test_the_neighbour_script_separates_naming_from_calling(self):
        """The refinement that moved the headline from 29.7297% to 0.0000%."""
        m = _load(NEIGHBOUR, "neighbour_live")
        assert m.calls_it("bench/tests/test_fix_complexity.py", "compute_rk") is False, (
            "test_fix_complexity asserts compute_rk is NOT called; counting it "
            "as a coverage claim is what produced the wrong figure")
        assert m.claimants("compute_rk"), "nothing names compute_rk at all"


class TestTheFindingsAreRecordedWhereAReaderWillLook:
    def test_the_task_list_entry_carries_both_figures(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import task_list_markers as tlm
        lines = (ROOT / "experimental_notes"
                 / "CDSFL_MASTER_TASK_LIST.md").read_text().splitlines()
        es = sorted(tlm.parse_entries(), key=lambda e: e.line_no)
        for k, e in enumerate(es):
            if e.ident == "A6":
                end = es[k + 1].line_no - 1 if k + 1 < len(es) else tlm.end_of_entries(lines)
                block = "\n".join(lines[e.line_no - 1:end])
                assert "0 of 84" in block, "the I11 result is not on the entry"
                assert "0 of 22" in block, "the I13 result is not on the entry"
                assert "29.7297%" in block, (
                    "the entry no longer records the figure that was WRONG, so "
                    "the correction it carries has lost its subject")
                return
        raise AssertionError("entry A6 is gone from the task list")
