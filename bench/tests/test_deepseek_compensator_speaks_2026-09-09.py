"""The DeepSeek route denies the tool loop, so its compensator must never fail quietly.

Task 3.2. Founder ruling, verbatim: *"Why does DeepSeek get a free pass on tool
use? ... No tool use is an unacceptable condition in the CDSFL schema, when an
item exists that is genuinely computable. Verdict, fix DeepSeek and test it."*

THE PREMISE IS REFUTED FOR DEEPSEEK SPECIFICALLY, and the refutation is the
finding. `bench/experiment_11_orchestrator.py:1442` sets `tools = None` for this
route, with a comment dated 2026-06-06 recording why: DeepSeek-v4-pro's OpenAI
tool-translation leaks tool calls as DSML markup, so the tool loop returns
exploration code rather than findings. It is a documented mitigation with a
compensator, `_falsifier_format_repair`.

What the schema requires is a falsifier the runner can EXECUTE, not a tool call.
Measured by `scripts/deepseek_falsifier_supply_2026-09-09.py`: DeepSeek supplies
one in **103 of 468 archived replies, 22.01%, Wilson [18.5%, 26.0%]**, against
325 of 1925 for every other seat pooled — **Fisher exact p = 0.0106, odds ratio
1.389, 95% CI [1.083, 1.782]**, scipy and statsmodels agreeing. It is
significantly MORE likely to supply one, not less.

SO THE FIX IS NOT TO RESTORE THE BROKEN TOOL LOOP. It is that the compensator
failed SILENTLY at 3 points, which meant the measurement above was the only
evidence the mitigation works and could not have been repeated on a run whose
repair had quietly failed:

  1. the caller's `except Exception: pass`
  2. the function's `except Exception: return response`
  3. the repair dispatching and returning nothing runnable

Only the SUCCESS path spoke. These tests drive each ending and assert it does.
"""

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

import bench.decomposed_dispatch as DD  # noqa: E402

#: A reply that HAS a finding and NO runnable falsifier -- the only shape the
#: repair acts on. The marker must match `_FINDING_PRESENT_RE`, which wants
#: `FINDING_ID`, a `### Finding` heading, or `F` plus 2-3 digits at line start.
#: A first version wrote "FINDING F001:" and matched none of them, so the
#: function returned early, never dispatched, and 3 tests asserted on an empty
#: log. Pinned by `test_the_fixture_actually_needs_repair` below.
NEEDS_REPAIR = (
    "### Finding 1\n"
    "FINDING_ID: F001\n"
    "The stated clearance is the retracted value.\n"
    "ATTEMPT: check that the constant equals 3.\n"
)


class _Client:
    """A stand-in chat client. No network, no cost."""

    def __init__(self, behaviour):
        self.behaviour = behaviour
        outer = self

        class _Completions:
            def create(self, **kw):
                return outer.behaviour(kw)

        class _Chat:
            completions = _Completions()

        self.chat = _Chat()


def _captured(capsys):
    """`_log` writes to STDERR, not stdout — a first version read `.out` and
    asserted against an empty string, which passes for the wrong reason on any
    message that is never emitted."""
    c = capsys.readouterr()
    return c.out + c.err


def _reply(text):
    class _M:  # noqa: D401
        content = text
    class _C:
        message = _M()
    class _R:
        choices = [_C()]
    return _R()


def test_the_fixture_actually_needs_repair():
    """Guards every test below against passing on a no-op."""
    assert not DD._RUNNABLE_FALSIFIER_RE.search(NEEDS_REPAIR)
    assert DD._FINDING_PRESENT_RE.search(NEEDS_REPAIR)


def test_a_dispatch_failure_is_announced(capsys):
    def _boom(kw):
        raise RuntimeError("HTTP 402 payment required")
    out = DD._falsifier_format_repair(_Client(_boom), "deepseek-v4-pro",
                                      NEEDS_REPAIR, 1000, 30)
    assert out == NEEDS_REPAIR, "a failed repair must keep the original"
    printed = _captured(capsys)
    assert "FAILED to dispatch" in printed and "402" in printed, printed


def test_a_repair_that_returns_nothing_runnable_is_announced(capsys):
    out = DD._falsifier_format_repair(
        _Client(lambda kw: _reply("I could not produce a test.")),
        "deepseek-v4-pro", NEEDS_REPAIR, 1000, 30)
    assert out == NEEDS_REPAIR, (
        "a repair with no runnable block must not replace the original")
    printed = _captured(capsys)
    assert "no runnable block" in printed, printed


def test_a_successful_repair_is_announced_and_used(capsys):
    good = "FALSIFIER:\n```python\nassert 0, 'FALSIFIED'\n```\n"
    out = DD._falsifier_format_repair(_Client(lambda kw: _reply(good)),
                                      "deepseek-v4-pro", NEEDS_REPAIR, 1000, 30)
    # The function strips what it receives, so compare on the stripped form.
    assert out == good.strip()
    assert "format-repair applied" in _captured(capsys)


def test_a_response_needing_no_repair_never_dispatches():
    """The no-op path must stay free: it is the common case and it costs money."""
    calls = []

    def _count(kw):
        calls.append(kw)
        return _reply("should not be reached")

    already = "FALSIFIER:\n```python\nassert 0\n```\n"
    out = DD._falsifier_format_repair(_Client(_count), "deepseek-v4-pro",
                                      already, 1000, 30)
    assert out == already
    assert calls == [], "a paid dispatch was made for a response needing no repair"


def test_the_caller_no_longer_swallows_the_failure():
    """The orchestrator's own except clause, read as source because the
    surrounding function performs a PAID dispatch and cannot be executed here.

    Asserting on source text is normally refused in this project. It is
    justified narrowly: the 3 executing tests above cover the compensator's own
    behaviour, and what remains is whether the caller discards it. The bare
    `except Exception: pass` is the exact string being forbidden."""
    src = (REPO / "bench" / "experiment_11_orchestrator.py").read_text(
        encoding="utf-8")
    i = src.index("if _ds_repair:")
    block = src[i:i + 2200]
    assert "except Exception:  # noqa: BLE001\n                        pass" not in block, (
        "the caller swallows a format-repair failure again; this route has no "
        "tool loop, so the repair is the only thing making its falsifiers runnable")
    assert "FORMAT-REPAIR DID NOT RUN" in block, block[:400]
