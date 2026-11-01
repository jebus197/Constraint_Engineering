#!/usr/bin/env python3
"""The note-ratchet pre-flight: it must be able to refuse, and must use `--as`.

WHY IT EXISTS. The commit gate runs the per-file note ratchet AFTER the test
suite, so a commit whose tests are entirely green is refused minutes later by a
word of prose. Measured 2026-11-01: a log reading `2333 passed, 9 skipped` ended
`COMMIT_EXIT=1` because the master task list went from 24 to 26 findings. That
happened twice in 2 hours, about 8 minutes each time.

THE SUBTLETY THIS GUARDS. The linter is PATH-SENSITIVE, so scoring a temp copy
of the committed version without `--as <logical path>` compares 2 different
questions -- the exact mistake measured on 2026-10-15 at 4 of 6 files. A
pre-flight that got this wrong would report false rises and be ignored, which is
worse than not having one.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
TOOL = REPO / "scripts" / "note_ratchet_preflight_2026-11-01.py"


@pytest.fixture(scope="module")
def mod():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("preflight", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["preflight"] = m
    spec.loader.exec_module(m)
    return m


class TestItRunsAndCostsNothing:
    def test_help_is_answered_for_free(self):
        r = subprocess.run([sys.executable, str(TOOL), "--help"],
                           capture_output=True, text=True, cwd=REPO)
        assert r.returncode == 0
        assert "usage:" in r.stdout
        assert "NOTE RATCHET PRE-FLIGHT" not in r.stdout

    def test_it_runs_against_the_real_checkout(self):
        """It must not raise on whatever state the tree is in."""
        r = subprocess.run([sys.executable, str(TOOL)], capture_output=True,
                           text=True, cwd=REPO)
        assert r.returncode in (0, 1), r.stderr[-800:]
        assert "NOTE RATCHET PRE-FLIGHT" in r.stdout


class TestItUsesTheLogicalPath:
    """★ THE LOAD-BEARING DETAIL, asserted by intercepting the real call."""

    def test_as_is_passed_when_scoring_a_copy(self, mod, monkeypatch):
        seen = []

        class R:
            stdout = "  0 finding(s).\n"

        monkeypatch.setattr(mod.subprocess, "run",
                            lambda cmd, **kw: (seen.append(cmd), R())[1])
        mod._findings(pathlib.Path("/tmp/copy.md"), logical="experimental_notes/x.md")
        assert "--as" in seen[-1], seen[-1]
        assert seen[-1][seen[-1].index("--as") + 1] == "experimental_notes/x.md"

    def test_as_is_absent_for_the_working_copy(self, mod, monkeypatch):
        seen = []

        class R:
            stdout = "  3 finding(s).\n"

        monkeypatch.setattr(mod.subprocess, "run",
                            lambda cmd, **kw: (seen.append(cmd), R())[1])
        assert mod._findings(pathlib.Path("experimental_notes/x.md")) == 3
        assert "--as" not in seen[-1]

    def test_an_unscoreable_file_is_not_silently_zero(self, mod, monkeypatch):
        class R:
            stdout = "the linter crashed\n"

        monkeypatch.setattr(mod.subprocess, "run", lambda cmd, **kw: R())
        assert mod._findings(pathlib.Path("x.md")) is None


class TestItCanRefuse:
    """A pre-flight that cannot go red is the vacuity trap met twice today."""

    def _drive(self, mod, monkeypatch, rows, in_head=True):
        monkeypatch.setattr(mod, "changed_notes", lambda: [f for f, _, _ in rows])
        cur = {f: c for f, _, c in rows}
        base = {f: b for f, b, _ in rows}

        monkeypatch.setattr(mod, "_findings",
                            lambda path, logical=None: (base if logical else cur)
                            .get(logical or str(path).replace(str(mod.REPO) + "/", "")))
        monkeypatch.setattr(mod.subprocess, "run", _fake_git(in_head))
        return mod.main()

    def test_a_worse_note_is_refused(self, mod, monkeypatch, capsys):
        rc = self._drive(mod, monkeypatch, [("notes/a.md", 3, 5)])
        out = capsys.readouterr().out
        assert rc == 1, out
        assert "WORSE" in out and "3 -> 5" in out

    def test_an_equal_note_passes(self, mod, monkeypatch, capsys):
        assert self._drive(mod, monkeypatch, [("notes/a.md", 3, 3)]) == 0
        assert "WORSE" not in capsys.readouterr().out

    def test_an_improved_note_passes(self, mod, monkeypatch):
        assert self._drive(mod, monkeypatch, [("notes/a.md", 9, 2)]) == 0

    def test_it_is_per_file_not_a_total(self, mod, monkeypatch, capsys):
        rc = self._drive(mod, monkeypatch,
                         [("notes/a.md", 9, 2), ("notes/b.md", 2, 9)])
        assert rc == 1, "a total-based pre-flight would pass this: 11 was 11"
        assert "notes/b.md" in capsys.readouterr().out

    def test_a_file_absent_from_head_is_new_not_a_rise(self, mod, monkeypatch,
                                                       capsys):
        rc = self._drive(mod, monkeypatch, [("notes/new.md", 0, 4)], in_head=False)
        out = capsys.readouterr().out
        assert rc == 0, out
        assert "new file, 4 finding(s)" in out

    def test_no_changed_notes_passes(self, mod, monkeypatch, capsys):
        monkeypatch.setattr(mod, "changed_notes", lambda: [])
        assert mod.main() == 0
        assert "no changed notes" in capsys.readouterr().out


class TestItReadsGitStatusCorrectly:
    def test_only_notes_are_picked_up(self, mod, monkeypatch):
        class R:
            stdout = (" M bench/x.py\n M experimental_notes/a.md\n"
                      "?? b.txt\n M c.json\n")
            returncode = 0
        monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: R())
        assert mod.changed_notes() == ["b.txt", "experimental_notes/a.md"]

    def test_a_rename_is_judged_on_its_destination(self, mod, monkeypatch):
        class R:
            stdout = 'R  old/a.md -> experimental_notes/new.md\n'
            returncode = 0
        monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: R())
        assert mod.changed_notes() == ["experimental_notes/new.md"]


def _fake_git(in_head: bool):
    """git cat-file -e / git show, without touching the repository."""
    def run(cmd, **kw):
        class R:
            returncode = 0 if in_head else 1
            stdout = "committed bytes\n"
        if cmd[:2] == ["git", "cat-file"]:
            return R()
        return R()
    return run
