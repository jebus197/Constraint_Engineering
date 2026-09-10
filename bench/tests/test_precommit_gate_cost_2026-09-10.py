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
import re
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


#: The task-list entry that declares the gate's cost, and the marker it carries.
TASK_LIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
_GATE_COST_RE = re.compile(
    r"<!--\s*gate-cost:\s*files=(\d+)\s+collected=(\d+)")


def _declared_gate_cost() -> tuple[int, int]:
    """Read entry 1.1's declared figures out of the task list.

    Read rather than restated, so the number lives in exactly 1 place. A missing
    marker is an error, not a default: silently substituting a fallback would
    turn this guard into one that cannot fail.
    """
    m = _GATE_COST_RE.search(TASK_LIST.read_text(encoding="utf-8"))
    assert m, (
        "entry 1.1 no longer carries its `<!-- gate-cost: files=N collected=M -->` "
        "declaration, so the gate's cost is claimed in prose only and nothing "
        "checks it. Restore the marker -- do not delete this test.")
    return int(m.group(1)), int(m.group(2))


class TestTheCountIsExactAndCurrent:
    def test_the_entry_figure_matches_the_hook_today(self, mod):
        """The entry's declared gate cost must equal what the hook collects today.

        SIXTH CORRECTION 2026-09-10, and this one changes the SHAPE rather than
        the number. The figure had been written twice -- once in entry 1.1's
        prose and once as a literal in this assertion -- so every correction was
        2 edits and 5 of the previous 6 were made by someone who had noticed only
        1 of them. Two representations of one truth with no comparator is the
        shape `execute-do-not-grep` names, and it was sitting inside the test
        whose whole job is to be the comparator.

        The entry now carries a machine-readable declaration and this test READS
        it. There is 1 place to update, and the test compares that place to the
        measurement. The treadmill is deliberately kept: the gate's cost is a
        function of the task list, because `test_done_markers_carry_evidence`
        parametrises 1 test per DONE entry, so closing an entry moves it and this
        test goes red until the entry is refreshed. That is the mechanism that
        has kept the figure true since 14:20 on 2026-09-10; a figure nobody is
        forced to refresh is how the first 3 corrections became possible.

        Refresh with: python3 scripts/precommit_gate_cost_2026-09-10.py
        """
        declared_files, declared_tests = _declared_gate_cost()
        files = mod.gate_files()
        assert len(files) == declared_files, (
            f"the hook now runs {len(files)} guard files; the task list declares "
            f"{declared_files}. Update the declaration in entry 1.1.")
        assert mod.collected(files) == declared_tests, (
            f"the collected count has moved to {mod.collected(files)}; the task "
            f"list declares {declared_tests}. This is EXPECTED whenever an entry "
            f"is closed -- refresh the declaration in entry 1.1 with:\n"
            f"  python3 scripts/precommit_gate_cost_2026-09-10.py")

    def test_the_declaration_is_actually_present_and_parseable(self):
        """ANTI-VACUITY. If the marker vanished, the test above would have
        nothing to compare against and could not fail for the right reason."""
        files, tests = _declared_gate_cost()
        assert files >= 4 and tests >= 50, (files, tests)


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
