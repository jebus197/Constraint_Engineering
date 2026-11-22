#!/usr/bin/env python3
"""THE BOARD'S GUARD PHASE STREAMS, AND STREAMING MUST NOT COST THE VERDICT.

Guard for entry B202, the board's 27-minute test phase that could not stream.
His ruling, 2026-11-21: stream the test phase.

THIS FILE EXTRACTS THE HOOK'S OWN SHELL BLOCK AND RUNS IT, per
`execute-do-not-grep`. A test that asserted on the hook's source text could only
confirm the hook describes itself consistently -- and the specific defect to be
prevented here is INVISIBLE to reading, because `| tee` looks correct and is
correct about everything except the one thing the gate exists for. The exit code
has to be observed, so the block is driven against children rigged to pass, to
fail, and to fail on stderr alone.

ONE TEXT ASSERTION IS KEPT DELIBERATELY, and it is a ratchet rather than a
description: no pipeline may stand between pytest and `$?` in this file again.
That is a claim about ABSENCE, which execution cannot establish from outside.

Companion measurement: `scripts/the_board_can_stream_without_losing_its_verdict_2026-11-21.py`.
Mutations: `scripts/the_streaming_board_mutations_2026-11-21.py`.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tempfile
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
HOOK = ROOT / "hooks" / "pre-commit"

#: The block is located by the 2 lines that bracket it in the live hook, not by
#: line number: an anchor that drifts turns a guard into a no-op silently.
START = '_CDSFL_BOARD_LOG="${TMPDIR:-/tmp}/cdsfl_board_$$.log"'
END = 'rm -f "$_CDSFL_BOARD_LOG" 2>/dev/null'
PYTEST_LINE = re.compile(
    r"^python3 -u -m pytest .*>> \"\$_CDSFL_BOARD_LOG\" 2>&1$", re.M)


def _block() -> str:
    src = HOOK.read_text(encoding="utf-8")
    assert src.count(START) == 1, f"START anchor found {src.count(START)} times"
    assert src.count(END) == 1, f"END anchor found {src.count(END)} times"
    i = src.index(START)
    j = src.index(END) + len(END)
    return src[i:j]


def _run(child_src: str) -> tuple[int, str, float, float]:
    """Run the hook's real block with its pytest call swapped for a rigged child.

    Returns (recorded CODE, captured OUT, seconds streamed before the end,
    total wall clock).
    """
    work = pathlib.Path(tempfile.mkdtemp(prefix="b202_guard_"))
    child = work / "child.py"
    child.write_text(child_src, encoding="utf-8")
    block = _block()
    swapped, n = PYTEST_LINE.subn(
        f'{sys.executable} -u {child} >> "$_CDSFL_BOARD_LOG" 2>&1', block)
    assert n == 1, (
        "the pytest invocation inside the streaming block no longer matches; "
        "the probe is broken, not the hook")
    script = work / "form.sh"
    script.write_text(
        "#!/bin/sh\n" + swapped
        + '\nprintf "%s" "$CODE" > "' + str(work) + '/code"\n'
          'printf "%s" "$OUT" > "' + str(work) + '/out"\n',
        encoding="utf-8")
    t0 = time.monotonic()
    proc = subprocess.Popen(["/bin/sh", str(script)], cwd=work,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, bufsize=1)
    first = None
    assert proc.stdout is not None
    for _line in proc.stdout:
        if first is None:
            first = time.monotonic() - t0
    proc.wait()
    total = time.monotonic() - t0
    code = int((work / "code").read_text(encoding="utf-8").strip() or "-1")
    out = (work / "out").read_text(encoding="utf-8")
    lead = (total - first) if first is not None else -1.0
    return code, out, lead, total


#: Each child writes 3 times with a pause between, so a form that only reveals
#: output at the end cannot clear the streaming threshold by luck.
_TICKER = ("import sys, time\n"
           "for i in range(3):\n"
           "    print('tick %d' % i, flush=True)\n"
           "    time.sleep(0.4)\n")

CHILDREN = [
    ("a passing board", _TICKER + "print('5145 passed')\nsys.exit(0)\n", 0),
    ("a failing board", _TICKER + "print('FAILED test_x')\nsys.exit(1)\n", 1),
    ("a board that fails on stderr only",
     "import sys, time\n"
     "for i in range(3):\n"
     "    print('boom %d' % i, file=sys.stderr, flush=True)\n"
     "    time.sleep(0.4)\n"
     "sys.exit(2)\n", 2),
]


class TestThePremiseIsAlive:
    def test_the_hook_is_the_live_hook(self):
        """`core.hooksPath` points at the repo copy, so there is no mirror."""
        pr = subprocess.run(["git", "config", "core.hooksPath"],
                            capture_output=True, text=True, cwd=ROOT)
        assert pr.returncode == 0, pr.stderr
        assert pathlib.Path(pr.stdout.strip()).resolve() == (ROOT / "hooks").resolve()

    def test_the_streaming_block_is_present_and_singular(self):
        block = _block()
        assert "tail -n +1 -f" in block
        assert PYTEST_LINE.search(block) is not None


@pytest.mark.parametrize("name,src,expected", CHILDREN,
                         ids=[c[0].replace(" ", "_") for c in CHILDREN])
class TestTheVerdictSurvivesStreaming:
    def test_the_exit_code_is_the_childs_own(self, name, src, expected):
        code, _out, _lead, _total = _run(src)
        assert code == expected, (
            f"{name}: the block recorded {code}, the child exited {expected} — "
            f"a gate that cannot see a failure is a rubber stamp")

    def test_output_is_observable_before_the_child_exits(self, name, src, expected):
        _code, _out, lead, total = _run(src)
        assert lead >= 0.3, (
            f"{name}: nothing was observable until {lead:.2f}s before the end "
            f"of a {total:.2f}s run")

    def test_the_captured_text_is_what_the_downstream_greps_read(self, name, src, expected):
        """6 greps in the hook read `$OUT`; a changed byte changes what they match."""
        _code, out, _lead, _total = _run(src)
        for i in range(3):
            token = f"tick {i}" if "tick" in src else f"boom {i}"
            assert token in out, f"{name}: {token!r} missing from the capture"


class TestTheRejectedFormCannotReturn:
    def test_no_pipeline_stands_between_pytest_and_its_exit_code(self):
        """★ A RATCHET ON ABSENCE, which execution cannot establish from outside.

        `| tee` streams correctly and loses the verdict: measured 0 of 3 exit
        codes kept, including 0 on a tree rigged to exit 1. `${PIPESTATUS[0]}`
        is bash-only and 0-indexed, zsh spells it `${pipestatus[1]}` and
        1-indexes it, and this hook is `#!/bin/sh`.
        """
        #: ★ COMMENTS ARE STRIPPED FIRST, AND THE FIRST VERSION OF THIS TEST DID
        #: NOT STRIP THEM AND FAILED AGAINST CORRECT CODE. The hook's own comment
        #: NAMES both forbidden spellings in order to explain why they are
        #: forbidden, so a whole-file scan reads the explanation as the offence —
        #: a scar read as a wound, which this project has recorded before. A
        #: detector must not be defeated by the documentation of what it detects.
        code_lines = [ln for ln in HOOK.read_text(encoding="utf-8").splitlines()
                      if not ln.lstrip().startswith("#")]
        for line in code_lines:
            if "-m pytest" not in line:
                continue
            assert "|" not in line, (
                f"a pipeline now carries pytest's output, so `$?` is the last "
                f"element's status and not pytest's: {line.strip()!r}")
        code = "\n".join(code_lines)
        assert "PIPESTATUS" not in code and "pipestatus" not in code

    def test_the_measurement_behind_the_choice_is_committed(self):
        """`measured-rate-travels-with-its-script`."""
        prod = ROOT / "scripts" / "the_board_can_stream_without_losing_its_verdict_2026-11-21.py"
        assert prod.is_file()
        assert prod.name in HOOK.read_text(encoding="utf-8")

    def test_unbuffered_python_is_not_dropped(self):
        """Without `-u`, redirected stdout block-buffers at 8 KiB.

        `-q` emits 1 character per test, so an 8 KiB buffer surfaces about once
        per 8,000 tests and a 5,145-test board would stream nothing at all.
        """
        assert PYTEST_LINE.search(_block()) is not None
        assert "python3 -u -m pytest" in _block()

    def test_the_follower_is_killed_before_the_code_is_read(self):
        block = _block()
        kill_at = block.index('kill "$_CDSFL_TAIL_PID"')
        out_at = block.index('OUT=$(cat "$_CDSFL_BOARD_LOG"')
        code_at = block.index("CODE=$?")
        assert code_at < kill_at < out_at, (
            "the order must be: capture CODE, kill the follower, then read OUT")
