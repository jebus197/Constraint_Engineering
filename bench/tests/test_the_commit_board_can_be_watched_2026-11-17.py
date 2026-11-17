"""`_git(stream=True)` makes a long child watchable, and changes nothing else.

★ ENTRY B195. His standing directive is to keep a terminal showing the full
current tail of any running process. For the commit board -- about 29 minutes,
the longest-running thing in the project -- that was UNSATISFIABLE, because
`scripts/cdsfl_sv.py:_git` opened the child with both pipes captured and waited
on `communicate()`, which returns only at exit. Measured 2026-11-14 on a child
printing 10 lines over 3 s: the buffered arm showed **0 of 10** lines before
exit across 11 watcher wake-ups; a line-buffered reader showed **10 of 10**,
the first at 0.02 s.

★ THE REPAIR IS OPT-IN AND THAT IS THE MEASUREMENT IT HAS TO CARRY. `_git` has
24 call sites and 23 of them want the captured string, not 30 minutes of
streamed output. `stream` defaults to False, so those 23 reach exactly the code
they reached before. This file asserts that default EXECUTABLY rather than by
reading the signature in prose, and drives BOTH arms against real git to show
the return value is unchanged.

★ WHAT MUST SURVIVE. The timeout-and-reap block is load-bearing: it reaps the
whole process group and SAYS what it abandoned, which is this project's
`a swallowed exception is not a record` repair. The streamed path enforces the
same deadline across its read loop and calls the same reaper.
"""
from __future__ import annotations

import importlib.util
import inspect
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
SV = REPO / "scripts" / "cdsfl_sv.py"


@pytest.fixture(scope="module")
def sv():
    spec = importlib.util.spec_from_file_location("sv_stream", SV)
    m = importlib.util.module_from_spec(spec)
    sys.modules["sv_stream"] = m
    try:
        spec.loader.exec_module(m)
    except SystemExit:
        pass
    return m


class TestTheDefaultIsOff:
    def test_stream_defaults_to_false(self, sv):
        """23 of 24 call sites must be untouched, and this is how that is held."""
        p = inspect.signature(sv._git).parameters
        assert "stream" in p, "the streaming parameter is gone"
        assert p["stream"].default is False, (
            f"stream defaults to {p['stream'].default!r}; a True default would "
            f"stream 30 minutes of board output through 23 callers that want a "
            f"captured string")

    def test_the_streamed_helper_exists_and_is_separate(self, sv):
        """A separate function, so the non-streaming path stays readable."""
        assert hasattr(sv, "_git_streamed")
        assert sv._git_streamed is not sv._git


class TestBothArmsReturnTheSameThing:
    """EXECUTED against real git. A caller swapping `stream=True` in loses nothing."""

    def test_the_two_arms_agree_on_a_real_command(self, sv):
        if not (REPO / ".git").exists():
            pytest.skip("no .git in this checkout")
        buffered = sv._git("log", "--oneline", "-3", root=REPO)
        streamed = sv._git("log", "--oneline", "-3", root=REPO, stream=True)
        assert streamed == buffered, (
            "the streamed arm returned something different from the buffered "
            "one, so swapping it in would change what callers see")
        assert buffered.strip(), "both arms returned empty; this proves nothing"

    def test_only_the_streamed_arm_writes_to_stdout(self, sv, capsys):
        """The observable difference, asserted rather than described."""
        if not (REPO / ".git").exists():
            pytest.skip("no .git in this checkout")
        sv._git("log", "--oneline", "-3", root=REPO)
        quiet = capsys.readouterr().out
        sv._git("log", "--oneline", "-3", root=REPO, stream=True)
        loud = capsys.readouterr().out
        assert quiet == "", (
            f"the buffered arm wrote {len(quiet)} characters to stdout; it must "
            f"stay silent or 23 callers start printing")
        assert loud.strip(), (
            "the streamed arm wrote nothing to stdout, so nothing can be "
            "watched and the repair does not exist")


class TestTheReaperStillGuards:
    def test_a_timeout_on_the_streamed_arm_raises_and_says_so(self, sv, capsys):
        """ANTI-VACUITY in the dangerous direction: the deadline must still bite.

        A streaming reader that never times out would hang the save for ever,
        which is strictly worse than the defect being repaired.
        """
        if not (REPO / ".git").exists():
            pytest.skip("no .git in this checkout")
        with pytest.raises(subprocess.TimeoutExpired):
            # `git log` over the whole history, with a deadline it cannot meet.
            sv._git("log", "--format=%H%n%B", root=REPO, timeout=0, stream=True)
        err = capsys.readouterr().err
        assert "reaped the whole process group" in err, (
            "the streamed arm timed out without saying what it abandoned, "
            "which is the swallowed-record defect this project already repaired")

    def test_the_buffered_arm_still_reaps_too(self, sv, capsys):
        if not (REPO / ".git").exists():
            pytest.skip("no .git in this checkout")
        with pytest.raises(subprocess.TimeoutExpired):
            sv._git("log", "--format=%H%n%B", root=REPO, timeout=0)
        assert "reaped the whole process group" in capsys.readouterr().err
