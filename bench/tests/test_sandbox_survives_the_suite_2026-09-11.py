"""Task A13's falsifier must be RUNNABLE, not merely committed.

WHY THIS FILE EXISTS, and it is the additive standard turned on my own work.
`scripts/sandbox_survives_the_suite_2026-09-11.py` settles A13 -- whether running
the suite inside a panel sandbox destroys that sandbox -- and its result is
quoted in the task list: 168 `bench/*.py` before collection, 168 after
collection, 168 after a full run of 6,748 passing tests, 0 lost at either point.

**Nothing called it.** Swept 2026-09-11 over every file added that day: 46 of 47
additions were reached by a test or a caller -- 97.8723%, Wilson
[88.8870%, 99.6234%], Clopper-Pearson [88.7062%, 99.9461%] -- and this script was
the 1 that was not. "An addition that nothing reaches is not additive" is the
standard's own symmetric half, and a falsifier nobody can run is a claim about
evidence rather than evidence.

AND THE SWEEP THAT FOUND IT WAS WRONG TWICE FIRST, which is worth recording
because it is the day's recurring shape happening inside a measurement OF that
shape. It asked "is this file named inside a test file?" -- but a TEST is reached
by pytest COLLECTION, not by another test naming it, so all 29 new test files came
back unreached. And `bench/tests/hook_fixture.py` is imported as
`bench.tests.hook_fixture`, a module path, so a filename scan reported it
unreached too. Asking the right question per file type gives 46 of 47.

WHAT IS RUN HERE. The script's full mode builds a sandbox and runs the whole
suite inside it, roughly 12 minutes -- that is a command a person runs, exactly
like the fresh-clone suite's full mode. `--tests` restricts it, so the whole
machinery executes here against 1 fast test file: build, census, collect, census,
run, census, tear down.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "scripts" / "sandbox_survives_the_suite_2026-09-11.py"

#: 0.58 s in this tree and it touches nothing the sandbox cares about.
FAST = "bench/tests/test_precommit_stage0_order_2026-09-10.py"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("sandbox_survives", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheCensusCounts:
    def test_it_counts_a_real_tree(self, mod):
        c = mod.census(REPO)
        assert c["bench/*.py"] > 100, c
        assert c["bench/**/*.py"] >= c["bench/*.py"], c

    def test_it_counts_an_empty_tree_as_zero(self, mod, tmp_path):
        """POSITIVE CONTROL. A census that returned a constant would report "no
        files lost" on a tree that had been emptied, which is the exact failure
        this script exists to detect."""
        (tmp_path / "bench").mkdir()
        c = mod.census(tmp_path)
        assert c["bench/*.py"] == 0, c

    def test_it_notices_a_file_disappearing(self, mod, tmp_path):
        (tmp_path / "bench").mkdir()
        (tmp_path / "bench" / "a.py").write_text("x = 1\n", encoding="utf-8")
        before = mod.census(tmp_path)
        (tmp_path / "bench" / "a.py").unlink()
        after = mod.census(tmp_path)
        assert before["bench/*.py"] == 1 and after["bench/*.py"] == 0, (before, after)


class TestItRunsEndToEnd:
    def test_the_sandbox_survives_one_fast_file(self):
        """THE WHOLE PATH: build, census, collect, census, run, census, tear down.

        Restricted to 1 fast test file. The full-suite mode is roughly 12
        minutes and is a command a person runs; what must not rot is the
        machinery.
        """
        r = subprocess.run(
            [sys.executable, str(SCRIPT), "--tests", FAST],
            cwd=REPO, capture_output=True, text=True, timeout=1800)
        out = r.stdout + r.stderr
        assert r.returncode == 0, out[-2000:]
        for line in ("canonical tree:", "BEFORE ", "AFTER COLLECT", "AFTER RUN"):
            assert line in out, f"{line!r} missing from:\n{out[-1500:]}"
        assert "bench/*.py lost during COLLECTION: 0" in out, out[-1500:]
        assert "bench/*.py lost during the RUN   : 0" in out, out[-1500:]

    def test_it_answers_help(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0
        assert "usage:" in r.stdout.lower()

    def test_an_unknown_flag_is_refused(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--nope"], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode != 0
        assert "unrecognized arguments" in r.stderr
