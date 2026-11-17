"""The board's exit code must reach the refusal, and no guard checked that.

B202. `hooks/pre-commit` runs its guard board at line 1037 and refuses on a
non-zero code at `cheap-guards-red`. Measured 2026-11-17: **0** tests reference
that cause and the 3 guards that EXECUTE the hook all trip
`guard-file-missing`, 208 lines earlier, so the verdict path was exercised by
nothing. A plausible 1-line readability change -- piping the board through
`tee` so a 27-minute run can be watched -- makes `CODE=$?` read `tee`'s status
instead of pytest's, turning a red board green. It would have passed all
17,832 tests.

WHY THIS GUARD EXECUTES THE HOOK'S OWN LINE INSTEAD OF GREPPING IT.
A test asserting the source text does not contain a pipe asserts only that the
hook describes itself consistently, and `execute-do-not-grep` records 4 defects
in this project found by running 2 forms against each other and 0 found by
reading. So the board line is EXTRACTED from the live hook, retargeted at a
tree that fails on purpose, and RUN. If someone reintroduces a pipeline the
captured code becomes 0 and these tests go red -- without the defect needing to
be live, which `a regression guard must not need a live defect` requires.

IT DOES NOT RUN THE REAL BOARD. The board is a median 30.57 min (ledger,
n = 79). A guard that cost that could never sit on the gate it guards.
"""
from __future__ import annotations

import os
import pathlib
import re
import subprocess
import tempfile

import pytest

def _find_hook() -> pathlib.Path:
    """Walk up for hooks/pre-commit.

    Counting parents breaks the moment this file is run from anywhere but
    bench/tests/, and a guard that fails because of WHERE it sits reports a
    defect that is not there.
    """
    here = pathlib.Path(__file__).resolve()
    for d in (here, *here.parents):
        c = d / "hooks" / "pre-commit"
        if c.is_file():
            return c
    return here.parent.parent.parent / "hooks" / "pre-commit"


#: CDSFL_HOOK_PATH re-aims this guard at a MUTATED copy of the hook. It is the
#: seam the mutation harness drives, so the harness does not have to perform
#: string surgery on this file's own source -- which silently stops matching the
#: moment the file is edited, and then reports a pass it never established.
HOOK = pathlib.Path(os.environ.get("CDSFL_HOOK_PATH") or _find_hook())
REPO = HOOK.parent.parent

#: The board invocation: assigns OUT from a pytest run, then reads CODE.
BOARD_RE = re.compile(
    r'^(OUT=\$\(.*?python3 -m pytest .*?\))\s*\n\s*(CODE=\$\?)', re.M | re.S)


def _hook_src() -> str:
    return HOOK.read_text(encoding="utf-8")


def board_line() -> str:
    """The hook's own board invocation, lifted verbatim."""
    m = BOARD_RE.search(_hook_src())
    assert m, (
        "the board invocation could not be located in hooks/pre-commit, so this "
        "guard cannot test the verdict path. If the hook was restructured, "
        "update BOARD_RE -- do NOT delete the test, because the property it "
        "holds is that a red board refuses the commit.")
    return m.group(1)


def _mk(p: pathlib.Path) -> pathlib.Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _tree(d: pathlib.Path, *, failing: bool) -> pathlib.Path:
    f = d / "test_board_verdict_probe.py"
    f.write_text(
        "def test_ok():\n    assert True\n" +
        ("def test_bad():\n    assert False, 'deliberate'\n" if failing else ""),
        encoding="utf-8")
    return f


def _run_board_line(target: pathlib.Path, cwd: pathlib.Path) -> int:
    """Run the hook's REAL board line against `target`, return the code it records."""
    line = board_line()
    # retarget: the hook runs $GUARDS; we substitute one probe file.
    line = re.sub(r'\$GUARDS|\$\{GUARDS\}', str(target), line)
    script = cwd / "probe.sh"
    script.write_text(
        "#!/bin/sh\n" + line + "\nCODE=$?\nprintf '%s' \"$CODE\"\n",
        encoding="utf-8")
    r = subprocess.run(["/bin/sh", str(script)], cwd=cwd,
                       capture_output=True, text=True, timeout=300)
    tail = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
    assert tail.isdigit(), f"the probe printed no code: {r.stdout!r} {r.stderr!r}"
    return int(tail)


class TestTheBoardVerdictReachesTheRefusal:
    def test_a_red_board_yields_a_non_zero_code(self):
        """The property the gate depends on. Goes red if the board is piped."""
        with tempfile.TemporaryDirectory(prefix="cdsfl_verdict_") as td:
            d = pathlib.Path(td)
            code = _run_board_line(_tree(d, failing=True), d)
        assert code != 0, (
            "a FAILING guard board produced exit code 0, so hooks/pre-commit "
            "would record `cheap-guards-red` as passing and ALLOW the commit. "
            "The usual cause is a pipeline: `OUT=$(pytest ... | tee ...)` makes "
            "CODE=$? the status of the LAST element, and tee always succeeds. "
            "Stream via a temp file and a background tail instead, so there is "
            "no pipe and $? stays pytest's own.")

    def test_a_green_board_yields_zero(self):
        """The falsifier: a guard that always refused would block every commit."""
        with tempfile.TemporaryDirectory(prefix="cdsfl_verdict_") as td:
            d = pathlib.Path(td)
            code = _run_board_line(_tree(d, failing=False), d)
        assert code == 0, (
            f"a PASSING guard board produced exit code {code}, so the gate would "
            f"refuse every commit regardless of the tests")

    def test_the_two_verdicts_are_distinguished(self):
        """Both directions in one assertion, so a constant return cannot pass."""
        with tempfile.TemporaryDirectory(prefix="cdsfl_verdict_") as td:
            d = pathlib.Path(td)
            rd, gd = _mk(d / "r"), _mk(d / "g")
            red = _run_board_line(_tree(rd, failing=True), rd)
            green = _run_board_line(_tree(gd, failing=False), gd)
        assert (red, green) != (0, 0), "the board cannot report failure at all"
        assert red != green, (
            f"the board returns {red} for a red tree and {green} for a green "
            f"one, so its verdict carries no information")

    def test_the_board_invocation_is_still_locatable(self):
        """If this fails, the guard above is vacuous and must be repaired first."""
        assert "pytest" in board_line()
        assert board_line().startswith("OUT=$(")

    @pytest.mark.parametrize("cause", ["cheap-guards-red"])
    def test_the_refusal_cause_still_exists(self, cause):
        """The cause this guard protects must still be the one the hook records."""
        assert f'CDSFL_REFUSAL="{cause}' in _hook_src(), (
            f"hooks/pre-commit no longer records {cause!r}; the verdict path was "
            f"renamed or removed and this guard needs re-aiming")

