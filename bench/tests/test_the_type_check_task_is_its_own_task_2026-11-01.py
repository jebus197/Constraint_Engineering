#!/usr/bin/env python3
"""The type-check task: outside the commit check, per-file, and able to fail.

HIS RULING, 2026-11-01: *"Enable it as its own task, as you suggest."* The
recommendation he accepted keeps it OUT of the commit check until it is clear,
so that is asserted here rather than trusted.

★ B68's ORIGINAL MECHANISM IS REFUTED AND THE REAL ONE IS GUARDED INSTEAD. The
entry claimed `--ignore-missing-imports` turns project symbols into `Any`. It
does not; a probe calling a non-existent method on an imported project class is
caught with the flag on. What the namespace package actually does is ABORT the
checker -- "Source file found twice under different module names" -- so it never
reaches most files. `--explicit-package-bases` plus `MYPYPATH` is what prevents
that, and the test below EXECUTES the real command to check it rather than
grepping the source for the flag.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TASK = REPO / "scripts" / "type_check_task_2026-11-01.py"
PRECOMMIT = REPO / "hooks" / "pre-commit"


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("tc_task", TASK)
    m = importlib.util.module_from_spec(spec)
    sys.modules["tc_task"] = m
    spec.loader.exec_module(m)
    return m


class TestItIsItsOwnTask:
    def test_it_is_not_in_the_commit_check(self):
        """His ruling: out of the commit check until it is clear.

        ★ THIS ACCUSED CORRECT CODE ON 2026-11-09 AND THE PREDICATE IS
        NARROWED. It read `assert "type_check_task" not in text` over the
        hook's whole source. B103 then put every guard dated 2026-10-29 or
        later on the gate, including THIS FILE, whose own name contains
        `type_check_task` -- so the string matched a FILENAME IN THE GUARDS
        LIST and the guard refused a 26-minute board over its own presence.

        HIS RULING IS ABOUT THE TASK RUNNING, NOT ABOUT ITS GUARD BEING ON THE
        GATE. Running a test ABOUT the task is not running the task, and the 2
        are opposite in effect: the guard on the gate is what keeps the ruling
        enforced at commit time. So the predicate now asks the question the
        ruling asks -- is the task INVOKED -- in 2 narrower ways.

        The GUARDS list and the comments are excluded before the name search.
        Excluding comments is not cosmetic: this block now describes the
        defect, so a predicate reading its own explanation would match the
        scar and refuse forever, which is a shape recorded against 2026-11-02.
        """
        if not PRECOMMIT.is_file():
            pytest.skip("no pre-commit hook in this checkout")
        import re as _re
        text = PRECOMMIT.read_text(encoding="utf-8", errors="replace")

        # 1. THE TASK'S OWN PATH MUST NEVER APPEAR. A GUARDS entry is under
        #    bench/tests/, so this cannot be satisfied by a guard's filename.
        assert "scripts/type_check_task" not in text, (
            "the type-check task's script is invoked from the commit check, "
            "against his ruling that it stays out until it is clear")

        # 2. AND THE BARE NAME MUST NOT APPEAR OUTSIDE THE GUARDS LIST, so a
        #    future wiring by some other spelling is still caught.
        guards = _re.search(r'^GUARDS="(.*?)"\s*$', text, _re.M | _re.S)
        body = text.replace(guards.group(0), "") if guards else text
        live = "\n".join(l.split("#", 1)[0] for l in body.splitlines())
        assert "type_check_task" not in live, (
            "the type-check task is named in the commit check outside its "
            "GUARDS entry, so something other than its guard reaches it")

    def test_help_is_answered_for_free(self):
        r = subprocess.run([sys.executable, str(TASK), "--help"],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0
        assert "usage:" in r.stdout
        assert "TYPE CHECK TASK" not in r.stdout, "help ran the checker"

    def test_the_checker_actually_runs_rather_than_aborting(self, mod):
        """★ EXECUTED, NOT GREPPED. Without `--explicit-package-bases` mypy
        aborts at the 2nd file under `bench/` and never reaches the rest."""
        proj, third, raw = mod.run_checker(
            ["bench/build_acceptance.py", "bench/ticket_store.py"])
        assert "found twice under different module names" not in raw, (
            "the checker aborted on the namespace package, so most files are "
            "never examined:\n" + raw[:800])
        assert isinstance(proj, dict) and isinstance(third, dict)

    def test_third_party_codes_are_classified_apart(self, mod):
        assert "import-untyped" in mod.THIRD_PARTY_CODES
        assert "import-not-found" in mod.THIRD_PARTY_CODES


class TestTheRatchetCanFail:
    """A ratchet that cannot go red is the vacuity trap met twice today."""

    def _drive(self, mod, monkeypatch, now, base):
        monkeypatch.setattr(mod, "run_checker", lambda paths: (now, {}, ""))
        monkeypatch.setattr(mod, "load_ledger", lambda: {"files": base})
        return mod.main(["x"])

    def test_a_risen_count_is_refused(self, mod, monkeypatch, capsys):
        rc = self._drive(mod, monkeypatch, {"a.py": 5}, {"a.py": 3})
        assert rc == 1
        assert "RISEN: a.py was 3, now 5" in capsys.readouterr().out

    def test_an_unbaselined_file_with_findings_is_refused(self, mod, monkeypatch,
                                                          capsys):
        rc = self._drive(mod, monkeypatch, {"new.py": 2}, {})
        assert rc == 1
        assert "UNBASELINED with 2 finding(s): new.py" in capsys.readouterr().out

    def test_an_equal_count_passes(self, mod, monkeypatch):
        assert self._drive(mod, monkeypatch, {"a.py": 3}, {"a.py": 3}) == 0

    def test_an_improvement_passes_and_is_reported(self, mod, monkeypatch, capsys):
        rc = self._drive(mod, monkeypatch, {"a.py": 1}, {"a.py": 4})
        assert rc == 0
        assert "IMPROVED" in capsys.readouterr().out

    def test_the_ratchet_is_per_file_not_a_total(self, mod, monkeypatch, capsys):
        """One file improving may not pay for another getting worse."""
        rc = self._drive(mod, monkeypatch, {"a.py": 1, "b.py": 6},
                         {"a.py": 4, "b.py": 3})
        out = capsys.readouterr().out
        assert rc == 1, "a total-based ratchet would pass this: 7 was 7"
        assert "RISEN: b.py was 3, now 6" in out

    def test_a_third_party_rise_does_not_trip_it(self, mod, monkeypatch):
        """Reported, never ratcheted: a new scipy stub gap is not our defect."""
        monkeypatch.setattr(mod, "run_checker",
                            lambda paths: ({"a.py": 3}, {"a.py": 99}, ""))
        monkeypatch.setattr(mod, "load_ledger", lambda: {"files": {"a.py": 3}})
        assert mod.main(["x"]) == 0

    def test_the_error_pattern_reads_a_code_and_a_path(self, mod):
        m = mod._ERROR.match('bench/x.py:12: error: oh no  [union-attr]')
        assert m and m.group("path") == "bench/x.py"
        assert m.group("code") == "union-attr"
        assert mod._ERROR.match("bench/x.py:3: note: a hint") is None
