"""A dispatch whose STREAM BROKE must be retried, and never recorded as a reply.

THE DEFECT, MEASURED ON SIMULATED RUN 1, 2026-10-02. The Claude CLI exits 0 and
prints its transport failure into STDOUT, so a dispatch that died halfway reads
as a successful dispatch whose answer happens to be an error sentence. 4 of 5
seats returned 141 to 246 characters ending "API Error: Response stalled
mid-stream. The response above may be incomplete." -- 80.0000%, Wilson
[37.5535%, 96.3776%] -- and EACH WAS CREDITED WITH 1 FINDING. The 5th seat
returned 39,616 characters. Round 0 would have been built from 4 near-empty
seats and 1 real one, and the run would still have reported a number.

THE CAUSE WAS NOT CODE: the operator toggles a VPN on the machine the run
executes on, which he does routinely -- *"Sometimes I need to turn vpn on and
off on my Mac Mini. The outage is only ever brief."* His instruction: *"You
should fix it so a short network outage will not break a run."*

THIS IS THE RULE THIS PROJECT ALREADY WROTE FOR WOLFRAM, applied to the seat
transport. `.claude/CLAUDE.md`: "a failed call is NOT a result ... A Wolfram
result whose text begins with `[HTTP Error` ... is NOT EVIDENCE. It is a failed
measurement." The transport differs; the shape is identical.

WHY A TRUNCATED REPLY IS WORSE THAN AN EMPTY ONE, and why the marker is matched
ANYWHERE rather than at the start: the marker arrives APPENDED to whatever the
seat managed to say. A seat that produced 3 of its 9 findings before the stream
died leaves a PARTIAL registry that looks complete. An empty reply at least
announces itself.
"""
from __future__ import annotations

import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
for _p in (str(ROOT), str(ROOT / "bench"), str(ROOT / "bench" / "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from experiment_11_orchestrator import (  # noqa: E402
    STALL_RETRY_MIN_WAIT, stalled_mid_stream)

REAL_STALL = ("Let me verify my SEARCH blocks match exactly (whitespace-sensitive) "
              "before filing.\nAPI Error: Response stalled mid-stream. The response "
              "above may be incomplete.")


class TestThePredicate:

    @pytest.mark.parametrize("text", [
        REAL_STALL,
        "API Error: Response stalled mid-stream.",
        "api error: response stalled mid-stream",
        "API ERROR: RESPONSE STALLED MID-STREAM",
        "work done\nAPI Error: Request was aborted.",
        "API Error: Connection error.",
        "API Error: Terminated",
        "API Error: fetch failed",
        "API Error: socket hang up",
    ])
    def test_every_broken_stream_marker_is_recognised(self, text):
        assert stalled_mid_stream(text), f"{text[:40]!r} was not recognised"

    @pytest.mark.parametrize("text", [
        "Finding 1: the mandated regex fails to stop at a known label.",
        "",
        "   ",
        "No findings this round. The spec's anchors all resolve.",
        # the words apart, in ordinary prose, must NOT trip it
        "The API error handling in this module is sound and the stream is fine.",
    ])
    def test_a_healthy_or_empty_reply_is_not_called_broken(self, text):
        assert stalled_mid_stream(text) is None, f"{text[:40]!r} false-positived"

    def test_a_partial_reply_with_the_marker_appended_is_still_rejected(self):
        """THE DANGEROUS CASE. Real content, then a dead stream."""
        partial = ("Finding 1: §1.B's regex is case-sensitive.\n"
                   "Finding 2: the stop anchor misses a known label.\n"
                   "API Error: Response stalled mid-stream.")
        assert stalled_mid_stream(partial), (
            "a truncated registry would be recorded as a complete one")

    def test_the_wait_is_seconds_not_milliseconds(self):
        """A VPN handshake outlasts backoff_base=1.0."""
        assert STALL_RETRY_MIN_WAIT >= 10.0


@pytest.fixture
def shim(monkeypatch):
    import sim_dispatch_shim as S
    monkeypatch.setattr(S.time, "sleep", lambda *_a: None)
    return S


def _fake_run(sequence):
    """subprocess.run that returns each queued stdout in turn."""
    calls = {"n": 0}

    def run(*_a, **_kw):
        i = calls["n"]
        calls["n"] += 1
        out = sequence[min(i, len(sequence) - 1)]
        return subprocess.CompletedProcess(args=["claude"], returncode=0,
                                           stdout=out, stderr="")
    return run, calls


class TestTheSimulatedShimRetries:

    def _mc(self):
        return types.SimpleNamespace(label="CC2", api="sim")

    def test_a_stall_then_a_good_reply_returns_the_good_reply(self, shim, monkeypatch):
        good = "Finding 1: a real finding with substance." * 5
        run, calls = _fake_run([REAL_STALL, good])
        monkeypatch.setattr(shim.subprocess, "run", run)
        dispatch = shim.make_shim(model="opus", timeout=60)
        text, _el = dispatch(self._mc(), "prompt", "")
        assert text.strip() == good.strip(), "the stall was returned as the reply"
        assert calls["n"] == 2, f"expected a retry, made {calls['n']} call(s)"

    def test_all_attempts_stalling_RAISES_rather_than_returning_the_stall(
            self, shim, monkeypatch):
        run, calls = _fake_run([REAL_STALL])
        monkeypatch.setattr(shim.subprocess, "run", run)
        dispatch = shim.make_shim(model="opus", timeout=60)
        with pytest.raises(RuntimeError, match="stalled mid-stream"):
            dispatch(self._mc(), "prompt", "")
        assert calls["n"] == shim.STALL_ATTEMPTS, (
            f"expected {shim.STALL_ATTEMPTS} attempts, made {calls['n']}")

    def test_a_good_first_reply_costs_no_extra_dispatch(self, shim, monkeypatch):
        """ANTI-REGRESSION: the healthy path must not pay for this."""
        run, calls = _fake_run(["Finding 1: fine." * 10])
        monkeypatch.setattr(shim.subprocess, "run", run)
        dispatch = shim.make_shim(model="opus", timeout=60)
        dispatch(self._mc(), "prompt", "")
        assert calls["n"] == 1, f"made {calls['n']} calls for a healthy reply"

    def test_the_stall_is_never_silent(self, shim, monkeypatch, capsys):
        run, _c = _fake_run([REAL_STALL, "Finding 1: ok." * 10])
        monkeypatch.setattr(shim.subprocess, "run", run)
        dispatch = shim.make_shim(model="opus", timeout=60)
        dispatch(self._mc(), "prompt", "")
        out = capsys.readouterr().out
        assert "STALLED" in out, "a retried stall left no trace in the log"


class TestTheRealPanelRouteRetriesToo:
    """`call_claude_cli` had `max_retries=3` and an `accept` hook all along.

    Nothing rejected a stall, and `accept` defaults to None, so the stall was
    returned as the answer no matter what any caller did. The check now runs
    BEFORE the caller's substance test.
    """

    def test_a_stall_is_retried_with_no_accept_supplied(self, monkeypatch):
        import experiment_11_orchestrator as O
        monkeypatch.setattr(O.time, "sleep", lambda *_a: None)
        good = "A real panel reply with substance." * 20
        run, calls = _fake_run([REAL_STALL, good])
        monkeypatch.setattr(O.subprocess, "run", run)
        monkeypatch.setattr(O, "CLAUDE_CLI", "claude", raising=False)
        text = O.call_claude_cli("opus", None, "prompt", timeout=30,
                                 max_retries=3, backoff_base=0.0)
        assert text.strip() == good.strip()
        assert calls["n"] == 2, f"expected a retry, made {calls['n']}"
