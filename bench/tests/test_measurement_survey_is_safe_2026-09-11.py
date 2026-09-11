"""Task A16: a survey meant to READ must not run things that WRITE.

WHAT WENT WRONG. The intent was to find which committed measurement scripts no
longer execute. But `scripts/` mixes MEASUREMENTS with ACTIONS, and the survey
regenerated 5 tracked files before it was killed -- the fifth OVERWRITING A
DELIBERATELY PRESERVED ARCHIVE, `experimental_notes/data/adjudication_by_repair.json`,
which records what the adjudicator produced BEFORE the 2026-08-28 errored-leg
fix. The severity is not that files changed; it is that a survey intended to READ
ran things that WRITE.

THE FIX DECLARES THE DISTINCTION RATHER THAN INFERRING IT, which is what the
entry asked for. `scripts/measurement_scripts_only_2026-09-11.py` classes a
script as a MEASUREMENT only when it neither writes to the tree nor spawns a
process that could. All 4 scripts the entry names come back ACTION, each with the
line that decided it.

CONSERVATIVE BY CONSTRUCTION, because the failure is asymmetric: a measurement
wrongly classed as an action costs a missing row in a survey; an action wrongly
classed as a measurement overwrites a preserved archive. Anything unresolvable --
an unrecognised call, a computed file mode, any `subprocess` -- is an ACTION.

AND THE SURVEY THEN DID ITS JOB. Running the 54 measurement scripts with `--help`
found 5 that did not answer cleanly, all failing the SAME way: the flag was not
recognised, so it was consumed as a positional argument -- a report path, a note
to lint, a log to read. One crashed with FileNotFoundError on the literal string
`--help`; the others silently ran a full measurement when the caller asked for
usage. This project already carries the rule in its strong form, "a `--help` must
never cost money", written after 15 of 17 runners billed a live dispatch on an
unrecognised argument. All 5 are repaired; the count is now 0 of 54.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "measurement_scripts_only_2026-09-11.py"

#: The 4 the entry names. Each MUST come back ACTION.
NAMED_ACTIONS = ("cdsfl_sv.py", "cdsfl_qc.py", "cdsfl_recover.py",
                 "adjudicate_by_repair.py")


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("measonly", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["measonly"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheFourNamedScriptsAreActions:
    @pytest.mark.parametrize("name", NAMED_ACTIONS)
    def test_it_is_classed_as_an_action(self, m, name):
        p = ROOT / "scripts" / name
        if not p.is_file():
            pytest.skip(f"{name} is no longer in scripts/")
        kind, reasons = m.classify(p)
        assert kind == "ACTION", (
            f"{name} is classed MEASUREMENT, so the survey would RUN it. This "
            f"is the script that overwrote a preserved archive.")
        assert reasons, "classed ACTION with no reason given"


class TestTheClassifierIsConservative:
    def test_a_pure_reader_is_a_measurement(self, m, tmp_path):
        f = tmp_path / "reader.py"
        f.write_text("import pathlib\n"
                     "def main():\n"
                     "    print(pathlib.Path('x').read_text())\n", encoding="utf-8")
        assert m.classify(f)[0] == "MEASUREMENT"

    @pytest.mark.parametrize("body", [
        "import pathlib\npathlib.Path('x').write_text('y')\n",
        "import shutil\nshutil.rmtree('x')\n",
        "import subprocess\nsubprocess.run(['ls'])\n",
        "open('x', 'w')\n",
        "with open('x', 'a') as f:\n    pass\n",
        "import os\nos.system('rm -rf x')\n",
    ])
    def test_every_writing_shape_is_an_action(self, m, tmp_path, body):
        f = tmp_path / "w.py"
        f.write_text(body, encoding="utf-8")
        kind, reasons = m.classify(f)
        assert kind == "ACTION", (body, reasons)

    def test_an_unparseable_file_is_an_action(self, m, tmp_path):
        f = tmp_path / "broken.py"
        f.write_text("def (:\n", encoding="utf-8")
        assert m.classify(f)[0] == "ACTION"

    def test_a_computed_file_mode_is_an_action(self, m, tmp_path):
        f = tmp_path / "dyn.py"
        f.write_text("mode = 'w'\nopen('x', mode)\n", encoding="utf-8")
        assert m.classify(f)[0] == "ACTION"


class TestTheSurveyWritesNothing:
    def test_running_the_measurement_set_leaves_the_tree_untouched(self):
        """THE CLAIM THAT MATTERS, checked by running it.

        A classification is an argument; a clean `git status` afterwards is
        evidence. This is the exact failure the entry records, inverted.
        """
        before = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                                capture_output=True, text=True).stdout
        r = subprocess.run([sys.executable, str(SCRIPT), "--run"], cwd=ROOT,
                           capture_output=True, text=True, timeout=3600)
        assert r.returncode == 0, r.stderr[-400:]
        after = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT,
                               capture_output=True, text=True).stdout
        assert before == after, (
            f"the measurement survey changed the tree:\n"
            f"before:\n{before}\nafter:\n{after}")

    def test_it_runs_nothing_without_the_flag(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=900)
        assert r.returncode == 0
        assert "NOTHING WAS RUN" in r.stdout


class TestEveryMeasurementScriptAnswersHelp:
    def test_none_consumes_the_flag_as_data(self):
        """The finding the survey existed to produce, kept true."""
        r = subprocess.run([sys.executable, str(SCRIPT), "--run"], cwd=ROOT,
                           capture_output=True, text=True, timeout=3600)
        line = [ln for ln in r.stdout.splitlines() if "did not answer" in ln]
        assert line, r.stdout[-400:]
        assert line[0].startswith("0 of "), (
            f"{line[0]} -- a measurement script is treating `--help` as a "
            f"positional argument again")

    def test_a_genuine_missing_path_still_fails(self):
        """THE DISTINCTION THE REPAIR MUST PRESERVE. `--help` is a request the
        program can satisfy; a typo'd path is not, and must still exit non-zero
        so it cannot read as a clean note."""
        r = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "note_vagueness_lint.py"),
             "/tmp/a-file-that-does-not-exist-at-all.md"],
            cwd=ROOT, capture_output=True, text=True, timeout=300)
        assert r.returncode != 0, r.stdout[-300:]
