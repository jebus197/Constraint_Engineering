"""Panel round 12: five defects in the instruments that produced this session's figures.

EVERY NUMBER IN ROUND 12'S BRIEF WAS PRODUCED BY A SCRIPT I ALSO WROTE. That was
named in the brief as the weakest structural property of the session, and the
fable seat attacked it directly. Four of its five findings were defects in MY
instruments; all are reproduced here before the fix and pinned after it.

1. `overstated_entries` FABRICATED A 100% FAILURE RATE wherever git cannot
   answer. `git ls-files --error-unmatch` exits 0 tracked, 1 untracked, **128
   not a git repository** -- and `tracked()` returned False for 1 and 128 alike.
   In the panel's own sandbox the script printed "11 of 11 fail = 100.0000%,
   Wilson [74.1167%, 100.0000%]": three intervals on a fabricated number, and
   the exact inversion of the truth. **It is the same defect the cc2 seat found
   in `orphan_figures` ONE ROUND EARLIER**, in a script written the same day,
   with the correct pattern already in `bench/archive_corpus.py`. Writing the
   repair once did not stop the next script repeating it.

2. TWO OF FOUR CHECKS STILL READ THE ENTRY LINE, the population error the
   script's own docstring says was "caught before it became the answer". It was
   caught in ONE of three. Measured: **21 entries carry a figure on their first
   line, 47 in their block** -- so the clearance issued for 1.1, 5.1, 6.2, 6.5
   and M1 came from an instrument blind to more than half its population. Over
   the block it found W1 quoting `p = 2.199086e-14` with no producer; W1 now
   names one, because `measured-rate-travels-with-its-script` applies to a
   BLOCKED entry exactly as to a closed one.

3. A7's "almost certainly the one that was meant" is WITHDRAWN. Seven candidate
   predicates: dropping the severity filter also reproduces the anchor
   `exp55_v3_control = 8` with a total of 32; a strict `> 0.7` gives 20. One
   family figure cannot identify a predicate. ANONYMOUS is 0 under every
   candidate, so the conclusion never moved -- the identification was overstated.

4. A16's classifier PASSED FIVE RESOLVABLE WRITE FORMS as MEASUREMENT, in the
   asymmetric direction it exists to prevent: `Path("x").open("w")`,
   `os.open(...)`, `io.open(...)`, `open("x", mode="w")`, `f.truncate(0)`. The
   docstring's guarantee -- "anything this cannot resolve is an ACTION" -- was
   false for the method form, whose mode is not at `args[1]`.

5. A18's census DROPPED EVERY LIST-VALUED KEY, so `api_access` -- the key that
   entry's own "the arm is not lying to its reader" argument depends on -- was
   never in the default population. A census that cannot see a key can never
   report it unread.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


class TestGitExitCodesAreTheAnswer:
    def test_the_three_codes_are_what_this_assumes(self):
        """The premise, checked rather than believed."""
        d = tempfile.mkdtemp()
        codes = {}
        for label, cwd, path in (("no repo", d, "x.py"),
                                 ("untracked", ROOT, "no_such_file_xyz.py"),
                                 ("tracked", ROOT, "bench/repo_paths.py")):
            r = subprocess.run(["git", "ls-files", "--error-unmatch", path],
                               cwd=cwd, capture_output=True, text=True)
            codes[label] = r.returncode
        assert codes == {"no repo": 128, "untracked": 1, "tracked": 0}, codes

    def test_tracked_refuses_rather_than_saying_untracked(self):
        m = _load("scripts/overstated_entries_2026-09-11.py", "oe12")
        real = m.REPO
        try:
            m.REPO = pathlib.Path(tempfile.mkdtemp())
            with pytest.raises(m.NotAGitCheckout):
                m.tracked("anything.py")
        finally:
            m.REPO = real

    def test_it_still_answers_inside_a_checkout(self):
        m = _load("scripts/overstated_entries_2026-09-11.py", "oe12b")
        assert m.tracked("bench/repo_paths.py") is True
        assert m.tracked("a_file_that_is_not_tracked_xyz.py") is False


class TestTheChecksReadTheBlock:
    def test_a_figure_in_a_continuation_paragraph_is_seen(self):
        m = _load("scripts/overstated_entries_2026-09-11.py", "oe12c")
        by_id = m.entries()
        blocks = m.blocks(by_id)
        line_carriers = sum(1 for i, e in by_id.items()
                            if m.FIGURE.findall(e.text))
        block_carriers = sum(1 for i in by_id if m.FIGURE.findall(blocks[i]))
        assert block_carriers > line_carriers * 1.5, (
            f"blocks {block_carriers} vs lines {line_carriers}: the checks are "
            f"reading first lines again")

    def test_no_entry_carries_a_figure_without_a_producer(self):
        m = _load("scripts/overstated_entries_2026-09-11.py", "oe12d")
        by_id = m.entries()
        assert m.check_figures_have_producers(by_id, m.blocks(by_id)) == []

    def test_w1_names_its_producer(self):
        """The instance the block-wide sweep found. A BLOCKED entry quoting a
        p-value is subject to the same rule as a closed one."""
        m = _load("scripts/overstated_entries_2026-09-11.py", "oe12e")
        blk = m.blocks(m.entries())["W1"]
        assert "2.199086e-14" in blk
        assert "wolfram_route_health_2026-09-10.py" in blk


class TestTheActionClassifierResolvesEveryWriteForm:
    @pytest.mark.parametrize("body", [
        'import pathlib\npathlib.Path("x").open("w")\n',
        'import os\nos.open("x", os.O_WRONLY)\n',
        'import io\nio.open("x", "w")\n',
        'open("x", mode="w")\n',
        'f = open("x")\nf.truncate(0)\n',
    ])
    def test_a_resolvable_write_is_an_action(self, body, tmp_path):
        m = _load("scripts/measurement_scripts_only_2026-09-11.py", "mso12")
        f = tmp_path / "w.py"
        f.write_text(body, encoding="utf-8")
        kind, reasons = m.classify(f)
        assert kind == "ACTION", (body, reasons)

    def test_a_read_only_open_is_still_a_measurement(self, tmp_path):
        """THE CHEAP DIRECTION MUST STAY CHEAP. Widening until everything is an
        ACTION would satisfy every case above and survey nothing."""
        m = _load("scripts/measurement_scripts_only_2026-09-11.py", "mso12b")
        f = tmp_path / "r.py"
        f.write_text('print(open("data.txt").read())\n', encoding="utf-8")
        assert m.classify(f)[0] == "MEASUREMENT"


class TestWritesDelegatedAcrossAnImportAreSeen:
    def test_the_sealer_is_an_action(self):
        """cc2's material hole: `cdsfl_seal_logs.py` SEALS LOG DIRECTORIES on
        its default invocation and was classed MEASUREMENT, because it writes
        through `save_json` -- a METHOD on a class imported from another
        module. A scan that resolves one file cannot see across the import."""
        m = _load("scripts/measurement_scripts_only_2026-09-11.py", "mso12c")
        kind, reasons = m.classify(ROOT / "scripts" / "cdsfl_seal_logs.py")
        assert kind == "ACTION", reasons
        assert any("verification_chain" in r for r in reasons), reasons

    def test_a_pure_reader_importing_a_pure_reader_stays_a_measurement(self, tmp_path):
        """ANTI-VACUITY FOR THE WIDENING. If importing anything made a script an
        ACTION, the survey would run nothing and every assertion above would
        hold."""
        m = _load("scripts/measurement_scripts_only_2026-09-11.py", "mso12d")
        f = tmp_path / "r.py"
        f.write_text(
            "from bench.repo_paths import is_archived_run_output\n"
            "def main():\n"
            "    print(is_archived_run_output('bench/logs/x'))\n",
            encoding="utf-8")
        assert m.classify(f)[0] == "MEASUREMENT", m.classify(f)[1]


class TestTheTreeProbeCanFail:
    def test_the_guard_refuses_when_git_cannot_answer(self):
        """cc2's finding: `git status --porcelain` outside a work tree exits 128
        with EMPTY stdout, byte-identical to a clean tree. The guard for the
        archive-overwrite incident could only ever pass."""
        import subprocess as sp
        import tempfile as tf
        d = tf.mkdtemp()
        r = sp.run(["git", "status", "--porcelain"], cwd=d,
                   capture_output=True, text=True)
        assert r.returncode != 0 and r.stdout == "", (r.returncode, r.stdout)
        src = (ROOT / "bench" / "tests"
               / "test_measurement_survey_is_safe_2026-09-11.py").read_text()
        assert "r.returncode == 0" in src, (
            "the tree probe no longer checks git's exit status, so it compares "
            "empty output with empty output and passes on anything")


class TestTheConfigCensusSeesListValuedKeys:
    def test_api_access_is_in_the_population(self):
        m = _load("scripts/config_fields_are_read_2026-09-11.py", "cfr12")
        keys = m.declared_fields("bench/exp56_configs/*.json")
        assert "api_access" in keys, (
            "the key entry A18's argument depends on is invisible to its own "
            "census again")

    def test_a_list_valued_key_can_be_reported_unread(self, tmp_path):
        m = _load("scripts/config_fields_are_read_2026-09-11.py", "cfr12b")
        import json
        (tmp_path / "arm.json").write_text(
            json.dumps({"never_read_list_key": [1, 2]}), encoding="utf-8")
        real = m.REPO
        try:
            m.REPO = tmp_path
            keys = m.declared_fields("*.json")
            assert "never_read_list_key" in keys
        finally:
            m.REPO = real


class TestTheA7IdentificationIsQuotedWithItsFamily:
    def test_the_script_says_the_predicate_is_underdetermined(self):
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "escalation_paths_2026-09-11.py")],
            cwd=ROOT, capture_output=True, text=True, timeout=900)
        assert r.returncode == 0, r.stderr[-300:]
        assert "UNDERDETERMINED" in r.stdout
        assert "{20, 22, 32}" in r.stdout, (
            "the family is no longer quoted, so 22 reads as identified again")
