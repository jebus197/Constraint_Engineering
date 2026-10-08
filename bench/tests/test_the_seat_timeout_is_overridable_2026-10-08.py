"""One round may raise a seat's wall-clock ceiling; the default must not move.

FOUNDER'S RULING, 2026-10-07: *"The models should be given the time they need to
deliver a full response."* On 2026-10-08 a seat hit the 1800 s ceiling twice on
the same brief while a co-seat completed it in 1305.4 s with 36 tool calls -- so
the route was healthy and the brief answerable, and the ceiling was the binding
constraint for that seat alone.

WHY AN OVERRIDE RATHER THAN A NEW DEFAULT. `call_claude_cli` has roughly 20
callers in this repository, most of them dated confer scripts that pass no
timeout at all and take the 300 s function default. Moving that default to serve
one panel round would silently change every one of them. The override is scoped
to the panel dispatcher's own call site and the default is asserted unchanged
below, which is what makes this additive rather than a quiet reach into 20 files.

THE SIZING FIGURE, which corrects one given to the founder the same morning.
2426 s was reported as "the measured 95th percentile of observed work". It was a
percentile over durations that INCLUDE attempts killed at the cap -- right-
censored observations whose true durations are longer than recorded -- so it was
used to choose the cap that caused the censoring. Kaplan-Meier over 137 attempts,
128 completions and 9 censored, computed by hand and by statsmodels to identical
values: median 700.7 s, 90th 1728.1 s, 95th 2939.4 s. Producer:
`scripts/the_cap_was_measured_on_censored_data_2026-10-08.py`.

AND A LONGER CLOCK IS STILL NOT THE GENERAL REPAIR. The dispatcher records a
3600 s raise made and reverted within the hour on 2026-10-06: the per-call rate
is the same whether a seat is working or failing and retrying (20.455 s against
20.816 s), so the clock cannot separate those states and a bigger number buys
churn. The real repair is incremental stream-json parsing so the CALL COUNT is
observable mid-flight; measured 2026-10-08, the tool-log sink does not exist
until the subprocess returns, so no progress signal exists today.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]

#: The censoring-corrected percentiles the override is sized against.
KM_MEDIAN_S, KM_P90_S, KM_P95_S = 700.7, 1728.1, 2939.4


@pytest.fixture(scope="module")
def D():
    argv = list(sys.argv)
    sys.argv = ["test", "_guard_only"]
    try:
        spec = importlib.util.spec_from_file_location(
            "cmp_timeout", REPO / "bench" / "confer_maths_panel_2026-09-05.py")
        m = importlib.util.module_from_spec(spec)
        sys.modules["cmp_timeout"] = m
        spec.loader.exec_module(m)
    finally:
        sys.argv = argv
    return m


class TestTheDefaultDoesNotMove:
    def test_it_is_still_1800(self, D):
        assert D.DEFAULT_SEAT_TIMEOUT_S == 1800, (
            "the default moved; roughly 20 call sites of call_claude_cli depend "
            "on the panel NOT redefining the shared ceiling")

    def test_an_unset_variable_gives_the_default(self, D, monkeypatch):
        monkeypatch.delenv("PANEL_SEAT_TIMEOUT_S", raising=False)
        assert D._seat_timeout_seconds() == 1800

    def test_an_empty_variable_gives_the_default(self, D, monkeypatch):
        monkeypatch.setenv("PANEL_SEAT_TIMEOUT_S", "  ")
        assert D._seat_timeout_seconds() == 1800

    def test_the_default_sits_between_the_measured_90th_and_95th(self):
        """It kills roughly 1 attempt in 10 while still working. Stating that is
        the difference between a chosen number and a known one."""
        assert KM_P90_S < 1800 < KM_P95_S, (KM_P90_S, KM_P95_S)


class TestAnOverrideIsHonoured:
    def test_an_explicit_value_is_used(self, D, monkeypatch):
        monkeypatch.setenv("PANEL_SEAT_TIMEOUT_S", "3000")
        assert D._seat_timeout_seconds() == 3000

    def test_a_float_is_accepted_and_truncated(self, D, monkeypatch):
        monkeypatch.setenv("PANEL_SEAT_TIMEOUT_S", "2939.4")
        assert D._seat_timeout_seconds() == 2939

    def test_the_value_used_for_this_round_clears_the_95th_percentile(self):
        assert 3000 > KM_P95_S, (
            "a raise below the measured 95th percentile would still kill the "
            "slowest 1 attempt in 20")


class TestAMalformedValueRefusesRatherThanFallingBack:
    """MUTATION-GRADE. `except ValueError: return DEFAULT` would pass every test
    above while running a round at a ceiling the caller did not ask for."""

    def test_a_non_numeric_value_raises(self, D, monkeypatch):
        monkeypatch.setenv("PANEL_SEAT_TIMEOUT_S", "abc")
        with pytest.raises(SystemExit):
            D._seat_timeout_seconds()

    def test_zero_raises(self, D, monkeypatch):
        monkeypatch.setenv("PANEL_SEAT_TIMEOUT_S", "0")
        with pytest.raises(SystemExit):
            D._seat_timeout_seconds()

    def test_a_negative_value_raises(self, D, monkeypatch):
        monkeypatch.setenv("PANEL_SEAT_TIMEOUT_S", "-60")
        with pytest.raises(SystemExit):
            D._seat_timeout_seconds()


class TestTheCallSiteActuallyUsesIt:
    """An addition nothing reaches is not additive. Asserted on the AST rather
    than on a substring, so a commented-out call cannot satisfy it."""

    def test_the_dispatch_call_passes_the_function_not_a_literal(self):
        import ast
        src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text()
        calls = [n for n in ast.walk(ast.parse(src))
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "call_claude_cli"]
        assert calls, "call_claude_cli is no longer called from the dispatcher"
        timeouts = []
        for c in calls:
            for kw in c.keywords:
                if kw.arg == "timeout":
                    timeouts.append(kw.value)
        assert timeouts, "no call passes a timeout at all"
        assert any(isinstance(v, ast.Call) and isinstance(v.func, ast.Name)
                   and v.func.id == "_seat_timeout_seconds" for v in timeouts), (
            "the dispatch call site passes a literal timeout, so the override is "
            "an addition nothing reaches")
