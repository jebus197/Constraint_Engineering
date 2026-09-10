"""The pre-commit gate's cost figure must come from the hook, not from prose.

Entry 1.1 quoted the gate's cost 3 times and corrected it twice, each correction
applied inside the previous one, until the sentence read "56 tests in 1.88 s
(CORRECTED: '56 tests in 1.88 s (CORRECTED: '28 tests in 1.26 s' never
reproduced)' never reproduced)". Three prose corrections to one figure and no
instrument at any point.

WHAT THE INSTRUMENT MUST DO THAT PROSE CANNOT. The hook's file list GREW -- it
gained 2 files while the entry still said 4 -- so any figure over the old list
was stale the moment the list changed. The script reads the list out of
`hooks/pre-commit`; these tests hold it to that.

Timing is NOT asserted here. A wall clock is a property of the machine under its
current load, and a test that pins one would fail on a loaded machine for no
reason connected to the gate. The COUNT is exact and is asserted.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "precommit_gate_cost_2026-09-10.py"
HOOK = ROOT / "hooks" / "pre-commit"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("gate_cost", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheListComesFromTheHook:
    def test_every_file_the_hook_names_is_returned(self, mod):
        """The exact defect: a token scan returned 5 of 6."""
        src = HOOK.read_text(encoding="utf-8")
        named = [ln.strip().strip('"').strip("'").replace("GUARDS=", "").strip('"')
                 for ln in src.splitlines() if "bench/tests/test_" in ln]
        named = [n for n in named if n.startswith("bench/tests/test_")]
        got = mod.gate_files()
        missing = [n for n in named if n not in got]
        assert not missing, (
            f"the script did not see {missing}; a file the hook runs that the "
            f"instrument cannot see makes every cost figure wrong")

    def test_the_list_is_not_hardcoded(self, mod, tmp_path, monkeypatch):
        """Substitute the hook and the answer must change."""
        fake = tmp_path / "pre-commit"
        fake.write_text('GUARDS="bench/tests/test_only_this_one.py"\n', encoding="utf-8")
        monkeypatch.setattr(mod, "HOOK", fake)
        assert mod.gate_files() == ["bench/tests/test_only_this_one.py"], (
            "the file list is typed into the script, not read from the hook")

    def test_every_named_file_exists(self, mod):
        for f in mod.gate_files():
            assert (ROOT / f).is_file(), (
                f"the hook runs {f} and it does not exist; the gate would fail "
                f"every commit")

    def test_a_malformed_guards_block_refuses_rather_than_guessing(self, mod, tmp_path, monkeypatch):
        fake = tmp_path / "pre-commit"
        fake.write_text("GUARDS=bench/tests/test_unquoted.py\n", encoding="utf-8")
        monkeypatch.setattr(mod, "HOOK", fake)
        with pytest.raises(SystemExit):
            mod.gate_files()

    def test_a_non_test_entry_refuses(self, mod, tmp_path, monkeypatch):
        fake = tmp_path / "pre-commit"
        fake.write_text('GUARDS="bench/tests/test_a.py\nrm -rf /"\n', encoding="utf-8")
        monkeypatch.setattr(mod, "HOOK", fake)
        with pytest.raises(SystemExit):
            mod.gate_files()


class TestTheCountIsExactAndCurrent:
    def test_the_entry_figure_matches_the_hook_today(self, mod):
        """Entry 1.1 now says 6 files and 169 tests. Both are checked here.

        If this fails because the gate grew again, UPDATE THE ENTRY AND THIS TEST
        together — that is the whole point. Do not delete it.
        """
        files = mod.gate_files()
        assert len(files) == 6, (
            f"the hook now runs {len(files)} guard files; entry 1.1 says 6 and "
            f"must be corrected in the same change as this test")
        assert mod.collected(files) == 174, (
            "the collected count has moved; entry 1.1 quotes 174. UPDATED 2026-09-10 14:20 BST\n"
            "from 169: adding 5 tests to test_done_markers_carry_evidence_2026-09-10.py (task V7)\n"
            "moved it, and this test went red exactly as its docstring says it should.")


class TestItRuns:
    def test_the_script_exits_zero(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--repeats", "1"],
                           cwd=ROOT, capture_output=True, text=True, timeout=1800)
        assert r.returncode == 0, f"{r.stdout[-1500:]}\n{r.stderr[-1500:]}"
        assert "tests collected:" in r.stdout
        assert "median" in r.stdout and "range" in r.stdout, (
            "a wall-clock figure must be reported with its spread, not as one number")
        assert "property of this machine" in r.stdout, (
            "the conditions caveat must travel with the figure")
