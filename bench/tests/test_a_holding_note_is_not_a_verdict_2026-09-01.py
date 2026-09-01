"""A panel reply is accepted on substance, and rejection RETRIES.

On 2026-08-31 a panel reviewer returned 54 characters -- "Suite still running
-- I'll finalize once it completes" -- against a median panel reply of 7,512
characters. The harness recorded `ok=False` and kept the result, and the run
proceeded as though a verdict had been given.

The cause was that the only substance test in the system ran AFTER dispatch,
where it could annotate but never retry. `call_claude_cli` itself accepted any
non-empty string. Worse than the runway recorded it: the empty case raised
`CircuitBreakerTripped`, which the loop re-raises immediately, so the retry
path fired on neither an empty reply nor a short one.

Fixed 2026-09-01 by an optional `accept` predicate evaluated INSIDE the retry
loop (runway 0C.16). These tests pin the predicate and the retry.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "bench"))

import experiment_11_orchestrator as O  # noqa: E402
from experiment_11_orchestrator import verdict_is_substantive  # noqa: E402

THE_HOLDING_NOTE = "Suite still running - I'll finalize once it completes."


class TestThePredicate:
    def test_the_observed_holding_note_is_rejected(self):
        reason = verdict_is_substantive(THE_HOLDING_NOTE)
        assert reason is not None and "54 chars" in reason

    def test_empty_is_rejected(self):
        assert verdict_is_substantive("") == "empty"
        assert verdict_is_substantive("   \n ") == "empty"

    def test_a_long_tool_call_block_is_rejected(self):
        """Length alone must not rescue a reply that never concluded."""
        block = '<invoke name="Bash">' + "x" * 2000 + "</invoke>"
        assert verdict_is_substantive(block) is not None

    def test_a_real_length_reply_is_accepted(self):
        assert verdict_is_substantive("x" * 7512) is None

    def test_the_floor_is_a_floor_not_a_target(self):
        """801 characters is terse, not a holding note. It must pass."""
        assert verdict_is_substantive("x" * 801) is None
        assert verdict_is_substantive("x" * 799) is not None


class TestAShortConclusionIsStillAConclusion:
    """CC2, panel review 2026-09-01: gate on structure, not length alone.

    A pure length floor rejects a reviewer who genuinely has nothing to add,
    and then spends further dispatches re-asking a question already answered.

    CC2's concrete example, `[NO_NOVEL_FINDINGS]`, is NOT a token in this
    codebase -- a search of bench/ finds no such literal, so that exact reply
    could never have been rejected, because it is never sent. The class it
    points at is real, and the shape is pinned here so that introducing such a
    token later does not require rediscovering this.
    """

    def test_a_bracketed_protocol_token_is_accepted(self):
        assert verdict_is_substantive("[NO_NOVEL_FINDINGS]") is None
        assert verdict_is_substantive("[CONVERGED]") is None

    def test_a_terse_but_explicit_verdict_is_accepted(self):
        assert verdict_is_substantive(
            "VERDICT: all four fixes confirmed. Nothing further to add.") is None
        assert verdict_is_substantive(
            "NO FINDINGS. I ran the suite and reproduced each claim.") is None

    def test_the_holding_note_is_still_rejected(self):
        """The whole point: short-and-conclusive passes, short-and-pending does not."""
        reason = verdict_is_substantive(THE_HOLDING_NOTE)
        assert reason is not None and "no verdict marker" in reason

    def test_a_short_reply_that_merely_mentions_work_in_progress_is_rejected(self):
        for note in ("Still checking, back shortly.",
                     "Running the tests now; will report after.",
                     "Give me a moment to finish reading the diff."):
            assert verdict_is_substantive(note) is not None, note


class _FakeCompleted:
    def __init__(self, stdout):
        self.stdout, self.stderr, self.returncode = stdout, "", 0


class TestRejectionRetries:
    """The point of the fix: a bad reply is dispatched again, not recorded."""

    def _run(self, monkeypatch, replies, **kw):
        calls = {"n": 0}

        def fake_run(*a, **k):
            i = min(calls["n"], len(replies) - 1)
            calls["n"] += 1
            return _FakeCompleted(replies[i])

        monkeypatch.setattr(subprocess, "run", fake_run)
        monkeypatch.setattr(O, "CLAUDE_CLI", "/bin/true", raising=False)
        monkeypatch.setattr(O, "_get_panel_cwd_raw", lambda: None, raising=False)
        monkeypatch.setattr(O, "_get_tool_log_sink", lambda: None, raising=False)
        out = O.call_claude_cli("m", None, "p", max_retries=3, backoff_base=0,
                                **kw)
        return out, calls["n"]

    def test_a_holding_note_is_retried_to_exhaustion(self, monkeypatch):
        with pytest.raises(RuntimeError) as exc:
            self._run(monkeypatch, [THE_HOLDING_NOTE],
                      accept=verdict_is_substantive)
        assert "3 attempts" in str(exc.value)

    def test_a_holding_note_followed_by_a_real_reply_succeeds(self, monkeypatch):
        out, n = self._run(monkeypatch, [THE_HOLDING_NOTE, "y" * 3000],
                           accept=verdict_is_substantive)
        assert out == "y" * 3000
        assert n == 2, "the second attempt must actually have been dispatched"

    def test_without_accept_the_holding_note_is_still_returned(self, monkeypatch):
        """Default None must leave every existing caller's behaviour intact."""
        out, n = self._run(monkeypatch, [THE_HOLDING_NOTE])
        assert out == THE_HOLDING_NOTE
        assert n == 1


class TestTheHarnessesUseIt:
    """The predicate is worthless if the panel scripts still test after the fact."""

    @pytest.mark.parametrize("script", [
        "bench/confer_panel_2026-08-28.py",
        "bench/confer_convergence_panel_2026-08-23.py",
    ])
    def test_the_panel_harness_passes_accept(self, script):
        src = (REPO / script).read_text(encoding="utf-8")
        assert "accept=verdict_is_substantive" in src, (
            f"{script} dispatches without a substance test in the retry loop")
        assert 'bool(txt.strip()) and "<invoke" not in txt' not in src, (
            f"{script} still carries its own post-hoc copy of the test")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
