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


class TestTheExperimentsRefuseToRunUnsafely:
    """Both scripts mutate a TRACKED file and revert with `git checkout --`."""

    @pytest.mark.parametrize("script", [FRAGILITY, NEIGHBOUR])
    def test_a_dirty_tree_is_refused(self, script, tmp_path):
        m = _load(script, f"safety_{script.stem}")
        assert hasattr(m, "tree_is_clean"), (
            f"{script.name} no longer checks tree cleanliness before mutating a "
            f"tracked file, so a revert could destroy uncommitted work")
        src = script.read_text(encoding="utf-8")
        assert "REFUSING" in src and "git checkout" in src
        assert "finally:" in src, (
            "the revert is not in a finally block, so an exception mid-run "
            "leaves the repository mutated")

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
                end = es[k + 1].line_no - 1 if k + 1 < len(es) else len(lines)
                block = "\n".join(lines[e.line_no - 1:end])
                assert "0 of 84" in block, "the I11 result is not on the entry"
                assert "0 of 22" in block, "the I13 result is not on the entry"
                assert "29.7297%" in block, (
                    "the entry no longer records the figure that was WRONG, so "
                    "the correction it carries has lost its subject")
                return
        raise AssertionError("entry A6 is gone from the task list")
