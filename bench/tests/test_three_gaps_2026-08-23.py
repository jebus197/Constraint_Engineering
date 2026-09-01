"""Commissioning tests for the three gaps plugged on 2026-08-23.

Each is driven with a known-good AND a known-bad input, per the standard the
instrument inventory sets: a test that only ever exercises the happy path cannot
detect the failure mode this project keeps shipping.

  GAP 1  co-discovery was never recorded. 566 findings, 566 aliases, exactly 1.00
         per finding, zero raised by two or more models.
  GAP 2  no cost ledger was wired to either runner, so no experiment's spend was
         recorded anywhere.
  GAP 3  971 temp directories had accumulated, one per pytest process, no teardown.
"""
from __future__ import annotations

import json
import pathlib
import tempfile

import pytest

from bench.cost_ledger import CostLedger, UNMETERED_ROUTES
from bench.reference_runner_v3 import FindingRegistry


# ── GAP 1 ────────────────────────────────────────────────────────────────────
def _reg():
    r = FindingRegistry()
    r.entries["C0001"] = {
        "canonical_id": "C0001", "source_model": "Gemini",
        "source_aliases": ["F001"], "status": "OPEN", "severity": 0.8,
    }
    return r


def test_a_second_model_raising_the_same_defect_is_recorded():
    r = _reg()
    assert r.record_codiscovery("C0001", "Codex", "F007", 0.91) is True
    e = r.entries["C0001"]
    assert "Codex:F007" in e["source_aliases"]
    assert e["codiscovery"] == [
        {"model": "Codex", "finding_id": "F007", "similarity": 0.91}]


def test_recording_the_same_co_discovery_twice_is_a_no_op():
    """Rounds repeat. An alias list that grows on every round is not a record of
    who found it, it is a record of how many rounds ran."""
    r = _reg()
    assert r.record_codiscovery("C0001", "Codex", "F007", 0.91) is True
    assert r.record_codiscovery("C0001", "Codex", "F007", 0.91) is False
    assert len(r.entries["C0001"]["source_aliases"]) == 2


def test_an_unknown_canonical_id_is_refused():
    assert FindingRegistry().record_codiscovery("C9999", "Codex", "F1") is False


def test_an_empty_finding_id_is_refused():
    assert _reg().record_codiscovery("C0001", "Codex", "") is False


def test_recording_co_discovery_CANNOT_change_the_finding_s_status_or_severity():
    """THE POINT OF THE WHOLE DESIGN. Recording must never decide anything.

    Suppressing the duplicate's registration would be the natural 'fix' and would
    move `novel_this_round`, which feeds gamma, which ends runs. Recording is free;
    deciding is a founder ruling.
    """
    r = _reg()
    before = {k: v for k, v in r.entries["C0001"].items()
              if k in ("status", "severity", "canonical_id", "source_model")}
    r.record_codiscovery("C0001", "Codex", "F007", 0.91)
    after = {k: v for k, v in r.entries["C0001"].items()
             if k in ("status", "severity", "canonical_id", "source_model")}
    assert before == after


# ── GAP 2 ────────────────────────────────────────────────────────────────────
def test_the_ledger_records_a_dispatch(tmp_path):
    led = CostLedger(tmp_path)
    led.record(model="cx", route="openrouter", prompt_chars=4000,
               response_chars=800, elapsed_s=12.5, round_idx=3)
    d = json.loads((tmp_path / "cost_ledger.json").read_text())
    assert d["totals"]["dispatches"] == 1
    assert d["dispatches"][0]["est_input_tokens"] == 1000


def test_a_max_plan_route_is_counted_but_never_costed(tmp_path):
    led = CostLedger(tmp_path, prices={"cc2": {"in": 2.0, "out": 10.0}})
    led.record(model="cc2", route="claude_cli", prompt_chars=8000,
               response_chars=4000, elapsed_s=30.0)
    t = led.totals()
    assert "claude_cli" in UNMETERED_ROUTES
    assert t["unmetered_dispatches"] == 1
    assert t["metered_dispatches"] == 0
    assert "est_cost_usd" not in t, "a free route must contribute nothing to cost"


def test_no_price_means_NO_COST_FIGURE_not_a_guessed_one(tmp_path):
    """The known-bad input for this instrument: a metered dispatch with no price.

    A ledger that invents a number would be believed. It must instead make the gap
    visible.
    """
    led = CostLedger(tmp_path)                 # PRICES is empty by default
    led.record(model="unknown-model", route="openrouter", prompt_chars=4000,
               response_chars=400, elapsed_s=5.0)
    t = led.totals()
    assert "est_cost_usd" not in t
    assert t["unpriced_dispatches"] == 1
    assert t["est_input_tokens"] == 1000, "usage is still recorded without a price"


def test_a_supplied_price_produces_a_labelled_estimate(tmp_path):
    led = CostLedger(tmp_path, prices={"cx": {"in": 2.0, "out": 10.0}})
    led.record(model="cx", route="openrouter", prompt_chars=4_000_000,
               response_chars=400_000, elapsed_s=9.0)
    t = led.totals()
    assert t["est_cost_usd"] == pytest.approx(1.0 * 2.0 + 0.1 * 10.0, rel=1e-6)
    assert "ESTIMATED" in t["caveat"]
    assert "invoice is the authority" in t["caveat"]


def test_a_ledger_failure_never_raises(tmp_path):
    """A cost record must never be able to kill an experiment."""
    led = CostLedger(tmp_path)
    out = led.record(model="x", route="openrouter", prompt_chars="not-a-number",
                     response_chars=1, elapsed_s=1.0)
    assert "error" in out


def test_the_ledger_survives_a_resume(tmp_path):
    CostLedger(tmp_path).record(model="cx", route="openrouter", prompt_chars=400,
                                response_chars=40, elapsed_s=1.0)
    again = CostLedger(tmp_path)               # a resumed run reopens the file
    again.record(model="ge", route="openrouter", prompt_chars=400,
                 response_chars=40, elapsed_s=1.0)
    assert again.totals()["dispatches"] == 2, "a resume must not lose earlier rows"


# ── GAP 3 ────────────────────────────────────────────────────────────────────
def test_the_shadow_log_dir_registers_a_teardown():
    src = pathlib.Path(__file__).resolve().parents[1] / "immune_agents.py"
    text = src.read_text(encoding="utf-8")
    i = text.index('mkdtemp(prefix="cdsfl_test_shadow_logs_")')
    window = text[i:i + 700]
    assert "atexit.register" in window.replace("_atexit", "atexit"), (
        "the temp dir is created with no teardown — this is the 971-directory leak")


def test_no_stale_shadow_log_dirs_are_left_by_this_test_session():
    """Weak by construction and deliberately so: it asserts a bound, not zero,
    because a concurrently running pytest process legitimately owns one."""
    n = len(list(pathlib.Path(tempfile.gettempdir()).glob("cdsfl_test_shadow_logs_*")))
    assert n < 200, f"{n} shadow-log temp dirs present; the teardown is not working"


# ── The prose fallback, found mid-run in Exp 55 ──────────────────────────────
class TestProseAnchorFallback:
    """Exp 55 round 0 declined ALL TEN corrected-copy candidates with "does not
    occur verbatim", so T02 derived nothing and the discrimination control did not
    fire -- pre-registered prediction 1, failing. The cause was not paraphrase:
    models strip markdown emphasis when they quote. `_apply_prose_fix` in
    scripts/adjudicate_by_repair.py had already solved and measured this and was
    never wired into the runner.
    """

    TARGET = ("# Note\n\n"
              "**Claim CT-01.** The rate satisfies the criterion, because\n"
              "`f_s = 400 Hz` exceeds `f_max = 180 Hz`.\n\n"
              "**Claim CT-02.** The resolution is `1.5625 Hz`.\n")
    CORRECTED = "Claim CT-01. The rate satisfies the criterion, because f_s > 2 * f_max."

    def test_a_bare_quote_of_a_marked_up_passage_now_derives(self):
        from bench.reference_runner_v3 import _splice_corrected_copy
        bare = ("Claim CT-01. The rate satisfies the criterion, because "
                "f_s = 400 Hz exceeds f_max = 180 Hz.")
        copy, reason = _splice_corrected_copy(self.TARGET, bare, self.CORRECTED,
                                              "notes/control.md")
        assert copy, f"declined: {reason}"
        assert "NORMALISED" in reason

    def test_an_exact_quote_still_takes_the_exact_path(self):
        from bench.reference_runner_v3 import _splice_corrected_copy
        exact = ("**Claim CT-01.** The rate satisfies the criterion, because\n"
                 "`f_s = 400 Hz` exceeds `f_max = 180 Hz`.")
        copy, reason = _splice_corrected_copy(self.TARGET, exact, self.CORRECTED,
                                              "notes/control.md")
        assert copy and "NORMALISED" not in reason, (
            "an exact match must win outright; normalised is the FALLBACK")

    def test_an_ambiguous_normalised_match_is_REFUSED_not_guessed(self):
        from bench.reference_runner_v3 import _splice_corrected_copy
        # BOTH paragraphs carry the markdown, so the EXACT count is 0 and the
        # normalised count is 2. A first version of this test used one marked-up
        # and one bare paragraph, which is exact-count 1 -- the exact path
        # correctly won and the fallback was never reached. The test was wrong,
        # not the code.
        doc = "**A.** the same words here.\n\n**A.** the same words here.\n"
        copy, reason = _splice_corrected_copy(doc, "A. the same words here.",
                                              "A. different words.", "notes/x.md")
        assert not copy, "two paragraphs match once formatting is ignored"
        assert "cannot tell which claim" in reason

    def test_the_fallback_does_NOT_apply_to_code(self):
        """On .py, exact is both correct and achievable. Loosening it would let a
        patch land somewhere it was never meant to, which is far worse than a
        decline."""
        from bench.reference_runner_v3 import _splice_corrected_copy
        code = "def compute(x):\n    # a comment here\n    return x * 2\n"
        loose = "def compute(x):\n        # a comment here\n        return x * 2"
        copy, reason = _splice_corrected_copy(code, loose, "def compute(x):\n    return x * 3",
                                              "bench/x.py")
        assert not copy and "verbatim" in reason


def test_the_co_discovery_wiring_is_where_the_registry_actually_is():
    """The bug that Exp 55 caught live at 15:31, pinned.

    The first wiring sat inside `_build_feedback_for_next_round`, which takes no
    `registry` and no `**kwargs`. It raised NameError on every round, and that
    function's own defensive handler swallowed the exception and returned empty
    feedback -- so the only symptom was the feedback channel silently going dark.
    A defect whose sole visible effect is the disappearance of a feature is the
    hardest kind to notice, which is why this asserts the placement rather than
    the behaviour.
    """
    import re
    src = (pathlib.Path(__file__).resolve().parents[1]
           / "reference_runner_v3.py").read_text(encoding="utf-8")
    assert 'kwargs.get("registry")' not in src, (
        "the wiring reads a kwargs that does not exist in its enclosing function")
    i = src.index("record_codiscovery(\n")
    # walk back to the enclosing def and confirm the call is in the round loop
    head = src[:i]
    enclosing = head[head.rindex("\ndef "):].splitlines()[0]
    assert "def run_experiment" in enclosing or "registry" in src[i - 900:i], (
        f"record_codiscovery is called from {enclosing!r}, which may not hold a "
        f"registry")


def test_a_co_discovery_failure_is_logged_LOUDLY_not_swallowed():
    """The first version's exception vanished into a handler that returned {}.

    A recording failure must not kill a run and must not disappear either.
    """
    src = (pathlib.Path(__file__).resolve().parents[1]
           / "reference_runner_v3.py").read_text(encoding="utf-8")
    i = src.index("[co-discovery] recording failed")
    assert "_log(" in src[i - 200:i], "the failure path does not log"


class TestRelativePathFalsifiersReachTheOverlay:
    """Exp 55, measured twice: EVERY discrimination record came back
    INDETERMINATE_NOT_INTERCEPTED, because a falsifier reading its target by a
    RELATIVE path resolved it against a throwaway scratch dir where nothing
    exists. `_retarget_falsifier` rewrites only ABSOLUTE repo paths.
    """

    CODE = ('from pathlib import Path\n'
            'p = Path("bench/cdsfl_registry/targets/control_two_distinct_defects.md")\n'
            'print("EXISTS" if p.exists() else "MISSING")\n')

    def test_without_cwd_a_relative_reader_finds_nothing(self):
        from bench.falsifier_verify import execute_python
        assert "MISSING" in execute_python(self.CODE, repo_root=".")

    def test_with_cwd_at_the_overlay_it_reads_the_REPLACED_target(self):
        import shutil
        from bench.falsifier_verify import execute_python
        from bench.reference_runner_v3 import (REPO_ROOT,
                                               _build_discrimination_overlay)
        tgt = "bench/cdsfl_registry/targets/control_two_distinct_defects.md"
        root = _build_discrimination_overlay(REPO_ROOT, tgt, "# REPLACED\n")
        try:
            out = execute_python(self.CODE, repo_root=str(root), cwd=str(root))
            assert "EXISTS" in out
        finally:
            shutil.rmtree(root, ignore_errors=True)

    def test_the_snippet_is_never_written_into_the_overlay(self):
        """The overlay is a SYMLINK TREE. A stray .py written into it could land
        in the real repository, so the snippet stays in the scratch dir."""
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "falsifier_verify.py").read_text(encoding="utf-8")
        assert src.count("dir=_snippet_dir") == 2, "both exec paths must use it"
        assert "_snippet_dir = _scratch" in src

    def test_the_control_passes_cwd_at_every_execution_site(self):
        src = (pathlib.Path(__file__).resolve().parents[1]
               / "reference_runner_v3.py").read_text(encoding="utf-8")
        # Scoped to run_discrimination_control, NOT the whole file: `cwd=str(` also
        # appears at two unrelated pre-existing sandbox call sites, and a file-wide
        # count would silently pass on the wrong five. Measured, not guessed -- a
        # first version of this assertion guessed 5 file-wide and was wrong.
        i = src.index("def run_discrimination_control")
        j = src.index("\ndef ", i + 10)
        body = src[i:j]
        assert body.count("cwd=str(") == 5, (
            f"the control has five execution sites -- baseline, two determinism "
            f"probes, the tripwire and the corrected run -- and {body.count('cwd=str(')} "
            f"are redirected. A partial interception is silently partial")
