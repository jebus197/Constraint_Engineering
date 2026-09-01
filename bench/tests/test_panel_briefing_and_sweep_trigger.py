"""Two things the panel and the ledger were told that were no longer true.

1. THE PANEL BRIEFING (reference_runner_v3.py ~1217)
   Every model, every round, was told: a parseable proposed_fix is applied to a
   sandbox copy, ruff + mypy + bandit + the test suite are run, and on a clean
   pass the finding transitions to CLOSED. On a prose target none of that
   happens. The tri-state repair of 2026-08-01 made a clean parse return
   NO_APPLICABLE_CHECKS, which does not close — so today's repair is what made
   the briefing false, and the briefing was not swept with it. A panel reading
   it would reasonably conclude that writing a good fix is the route to closure.
   It is not. On a prose target the route is a runnable falsifier.

2. THE SWEEP TRIGGER (reference_runner_v3.py ~8544)
   The residual-clearing sweep was gated on `converged`, so the cleaner was off
   in exactly the runs whose residual ledger is worst. Exp 53 halted at round 3
   of 16 with 20 of 40 findings escalated, and `post_convergence_sweep_rounds: 2`
   was configured and never executed. It now runs on a halt as well, and records
   which trigger fired.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from bench.reference_runner_v3 import (  # noqa: E402
    TARGET_KIND_PROSE,
    TARGET_KIND_PYTHON,
    Finding,
    FindingRegistry,
)

RUNNER = Path(__file__).resolve().parents[1] / "reference_runner_v3.py"


def _registry(kind: str) -> FindingRegistry:
    r = FindingRegistry()
    r.target_kind = kind
    r.register(
        Finding(
            finding_id="F1",
            model_id="deepseek",
            round_idx=1,
            flaw_class=3,
            severity=0.72,
            abstraction_index=0.5,
            description="Listing A's allow() accepts a negative cost.",
        ),
        "deepseek",
    )
    return r


class TestTheProseBriefingTellsTheTruth:
    def test_it_does_not_promise_linters_on_a_prose_target(self):
        # Written first as "ruff/mypy/bandit must not appear", which was wrong:
        # the prose branch NAMES them precisely in order to say they have no
        # purchase here. What must not appear is the PROMISE that they run.
        summary = _registry(TARGET_KIND_PROSE).build_summary(1)
        assert "the runner applies it to a sandbox copy" not in summary
        assert "runs ruff + mypy + bandit" not in summary, (
            "the panel is told the linters run and close the finding; on a "
            "prose target they do not, and a clean parse now returns "
            "NO_APPLICABLE_CHECKS")
        assert "On clean pass, the finding transitions" not in summary
        assert "have no" in summary and "purchase on prose" in summary

    def test_it_names_the_falsifier_as_the_route_to_settlement(self):
        summary = _registry(TARGET_KIND_PROSE).build_summary(1)
        assert "RUNNABLE FALSIFIER" in summary
        assert "opens this" in summary and "by path" in summary

    def test_it_says_a_fix_alone_cannot_close(self):
        summary = _registry(TARGET_KIND_PROSE).build_summary(1)
        assert "cannot close a finding" in summary, (
            "the whole point: a fix is recorded for the human, the falsifier "
            "is what settles the finding")

    def test_it_still_asks_for_fixes(self):
        # Fixes remain valuable to the human even where they cannot close.
        summary = _registry(TARGET_KIND_PROSE).build_summary(1)
        assert "Propose fixes as usual" in summary


class TestThePythonBriefingIsUnchanged:
    def test_the_code_target_still_gets_the_original_paragraph(self):
        summary = _registry(TARGET_KIND_PYTHON).build_summary(1)
        assert "ruff + mypy + bandit" in summary
        assert "transitions" in summary and "CLOSED" in summary

    def test_the_default_registry_is_python(self):
        # Back-compat: an un-updated caller must get the historical prompt.
        assert FindingRegistry().target_kind == TARGET_KIND_PYTHON

    def test_both_briefings_keep_the_do_not_re_describe_line(self):
        for kind in (TARGET_KIND_PROSE, TARGET_KIND_PYTHON):
            assert "do not re-describe them" in _registry(kind).build_summary(1)


class TestTheSweepRunsOnAHaltToo:
    """Checked structurally: exercising it needs live model dispatch."""

    def test_the_sweep_is_no_longer_gated_on_convergence(self):
        src = RUNNER.read_text()
        assert 'if converged and getattr(cfg, "post_convergence_sweep_rounds"' not in src, (
            "gated on convergence, the cleaner is off in exactly the runs with "
            "the worst residue — Exp 53 configured 2 rounds and ran none")
        assert 'if getattr(cfg, "post_convergence_sweep_rounds", 0):' in src

    def test_the_trigger_is_recorded_so_a_reader_can_tell_them_apart(self):
        src = RUNNER.read_text()
        assert 'result["sweep_trigger"] = _sweep_reason' in src
        assert '"convergence" if converged else "halt/round-cap exit"' in src

    def test_a_halt_sweep_is_logged_as_not_having_converged(self):
        # A residual-clearing pass on a failed run must not read, in the log or
        # the report, as though the run converged.
        src = RUNNER.read_text()
        i = src.index('_sweep_reason = "convergence"')
        window = src[i:i + 900]
        assert "run did NOT converge" in window

    def test_the_sweep_still_cannot_touch_the_verdict(self):
        # The property that makes running it on a halt safe at all.
        src = RUNNER.read_text()
        i = src.index("RESIDUAL-CLEARING SWEEP")
        window = src[i:i + 1600]
        assert "never touch convergence" in window
        assert "registers no new findings" in window


class TestTheBriefingIsBuiltFromABranchNotADuplicate:
    """A copy-paste of the paragraph would drift; a branch cannot."""

    def test_exactly_one_briefing_is_emitted(self):
        for kind in (TARGET_KIND_PROSE, TARGET_KIND_PYTHON):
            summary = _registry(kind).build_summary(1)
            assert summary.count("do not re-describe them") == 1

    def test_the_runner_sets_the_kind_on_the_registry(self):
        src = RUNNER.read_text()
        tree = ast.parse(src)
        assigns = [
            n for n in ast.walk(tree)
            if isinstance(n, ast.Assign)
            and any(isinstance(t, ast.Attribute) and t.attr == "target_kind"
                    and isinstance(t.value, ast.Name) and t.value.id == "registry"
                    for t in n.targets)
        ]
        assert assigns, (
            "the registry defaults to python; without this assignment a prose "
            "run silently gets the code briefing")
