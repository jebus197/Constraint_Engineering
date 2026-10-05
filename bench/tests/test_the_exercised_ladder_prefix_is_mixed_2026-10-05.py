#!/usr/bin/env python3
"""The rungs the ladder ACTUALLY TRIES must span more than one model, in the right order.

WHAT WAS WRONG, and it was wrong twice over.

`bench/routing.py` ranks falsifier writers strongest-first and
`resolve_via_routing` tries only the first `routing_max_rungs` of them, stopping on
the first CONFIRMED. The default budget is 2, matching the Exp 42 validation where a
2-rung ladder reached 7 of 7 after weak source models resolved 0 of 7.

**Defect 1 — the seat map (CC1, 2026-10-05).** A seat map was added so simulated seats
are answered by different models, and it was reported as giving "2 distinct models
across the 5 rungs". True, and materially incomplete: the 2nd model sat at rungs 4 and
5, which a budget of 2 never reaches. For every source seat the first 2 rungs are drawn
from {Codex-SIM, CC2-SIM, ChatGPT-SIM}, and a faithful map puts all 3 strong vendors on
the strong model. Measured: **0 of 6 source seats got a climb between two different
models.** The ladder ran, logged its rungs, and rehearsed nothing. Found by the fable
seat in panel review.

**Defect 2 — the proposed repair (fable seat, 2026-10-05).** Mapping `Codex-SIM` to the
weaker model yields 5 of 6 mixed prefixes, and that is what the seat delivered.
Falsified here by execution: rung 1 is the STRONGEST writer, so that map makes every
mixed prefix `(weak, strong)` — **0 of 6 in the ladder's own direction.** The simulated
ladder would try weak-then-strong and stop on the first CONFIRMED, rehearsing an
algorithm the real run does not execute.

**What holds instead.** Keep the faithful map and raise the budget for simulated runs
only. Measured across budgets, with the faithful map: budget 2 gives 0 of 6 mixed;
budget 3 gives 3 of 6, all correctly directed; **budget 4 gives 6 of 6 mixed and 6 of 6
correctly directed**. The added rungs land on the cheaper model and are reached only for
a critical that rungs 1 and 2 failed to resolve, which is the case the ladder exists
for.

Every assertion CALLS `rank_falsifier_writers` and the shipped seat map. None reads
source text.
"""
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.routing import rank_falsifier_writers  # noqa: E402
from bench.tools import sim_dispatch_shim as SHIM  # noqa: E402

SEATS = ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM", "DeepSeek-SIM",
         "Gemini-SIM", "Fable-SIM"]
#: The budget at which the mixed-climb property is ASSERTED. It is not the
#: default any more — see TestTheBudgetIsOptInAndDefaultsToParity. A run only
#: reaches these rungs by passing --routing-max-rungs.
SIM_BUDGET = 4


def _prefix(source, budget, smap):
    rungs = rank_falsifier_writers(SEATS, exclude=(source,))[:budget]
    return rungs, [smap.get(r, "opus") for r in rungs]


def _mixed(models):
    return len(set(models)) > 1


def _correctly_directed(models):
    """No weaker model appears before a stronger one. `opus` is the stronger."""
    return all(not (models[i] == "fable" and "opus" in models[i + 1:])
               for i in range(len(models)))


class TestTheBudgetIsOptInAndDefaultsToParity:
    """REWRITTEN 2026-10-05 after the cc2 seat falsified the first version.

    The launcher briefly pinned `routing_max_rungs=4` unconditionally. Two reasons
    that was wrong, both measured by the seat and both verified here:

      1. PARITY. 0 of 288 config-shaped files pin the budget; the dataclass default
         is 2. An unconditional 4 made rungs 3-4 reachable only in simulation,
         directly beneath the block that exists to remove exactly that class.
      2. The property it bought is measured on a prefix that is NOT DISPATCHED.
         `resolve_via_routing` stops at the first CONFIRMED, so rung 3 runs only
         when rungs 1 and 2 have both failed.

    So the deeper budget is now an ASK, not a default, and these tests hold that:
    the default is parity, and the mixed-climb property is asserted at an
    explicitly-opted-in budget rather than silently assumed.
    """

    def test_the_launcher_does_not_pin_the_budget(self):
        import ast
        src = (REPO / "bench" / "tools" / "run_simulated_experiment.py").read_text(
            encoding="utf-8")
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Call) and (
                    getattr(node.func, "attr", None)
                    or getattr(node.func, "id", None)) == "RunnerConfig":
                for kw in node.keywords:
                    if kw.arg == "routing_max_rungs":
                        assert not isinstance(kw.value, ast.Constant), (
                            "the launcher pins routing_max_rungs to a literal "
                            "again; it must default to the RunnerConfig value")

    def test_the_ask_is_selectable(self):
        """EXECUTED: the launcher's own --help offers it."""
        import subprocess
        r = subprocess.run(
            [sys.executable,
             str(REPO / "bench" / "tools" / "run_simulated_experiment.py"), "--help"],
            capture_output=True, text=True, timeout=120, cwd=str(REPO))
        assert r.returncode == 0
        assert "--routing-max-rungs" in r.stdout

    def test_rungs_beyond_the_second_are_dispatched_only_after_failures(self):
        """The fact that makes a deeper budget an ask rather than a default."""
        from bench.routing import resolve_via_routing
        seen = []

        def _resolve(model, finding):
            seen.append(model)
            return "assert False"

        seen.clear()
        resolve_via_routing({"finding_id": "C1"}, ["A", "B", "C", "D"],
                            _resolve, lambda c: "CONFIRMED", max_rungs=4)
        assert seen == ["A"], (
            f"a run confirming at rung 1 dispatched {seen}; the ladder does not "
            f"stop on the first CONFIRMED, which is the premise of the whole "
            f"budget argument")
        seen.clear()
        resolve_via_routing({"finding_id": "C1"}, ["A", "B", "C", "D"],
                            _resolve, lambda c: "ERROR", max_rungs=4)
        assert seen == ["A", "B", "C", "D"]


class TestTheExercisedPrefixIsMixed:
    @pytest.mark.parametrize("source", SEATS)
    def test_every_source_seat_gets_a_climb_between_different_models(self, source):
        """AT AN OPTED-IN BUDGET of 4. At the default of 2 this is false for
        all 6, which TestTheProbeIsNotVacuous holds explicitly."""
        _, models = _prefix(source, SIM_BUDGET, SHIM.DEFAULT_LADDER)
        assert _mixed(models), (
            f"a finding sourced from {source} is routed to {models} — every rung "
            f"the ladder will actually try is the same model, so the climb "
            f"rehearses nothing"
        )

    @pytest.mark.parametrize("source", SEATS)
    def test_the_climb_runs_strong_to_weak_not_weak_to_strong(self, source):
        _, models = _prefix(source, SIM_BUDGET, SHIM.DEFAULT_LADDER)
        assert _correctly_directed(models), (
            f"{source} -> {models}: a weaker model is tried BEFORE a stronger one. "
            f"rank_falsifier_writers returns strongest-first and "
            f"resolve_via_routing stops on the first CONFIRMED, so this rehearses "
            f"an algorithm the real run does not execute"
        )


class TestTheProbeIsNotVacuous:
    """Each defect this file was written against must still be detectable."""

    def test_the_old_budget_would_fail_this_guard(self):
        """Anti-vacuity for defect 1: at a budget of 2 the prefix is uniform."""
        mixed = sum(1 for s in SEATS
                    if _mixed(_prefix(s, 2, SHIM.DEFAULT_LADDER)[1]))
        assert mixed == 0, (
            f"at budget 2, {mixed} of {len(SEATS)} prefixes are mixed — the "
            f"defect this guard was written against no longer reproduces, so the "
            f"guard may be passing for the wrong reason")

    def test_the_seat_proposal_would_fail_the_direction_check(self):
        """Anti-vacuity for defect 2: Codex-SIM on the weak model inverts it."""
        inverted = dict(SHIM.DEFAULT_LADDER)
        inverted["Codex-SIM"] = "fable"
        bad = [s for s in SEATS
               if not _correctly_directed(_prefix(s, 2, inverted)[1])
               and _mixed(_prefix(s, 2, inverted)[1])]
        assert len(bad) == 5, (
            f"the seat's proposed map was measured as 5 of 6 mixed-but-inverted; "
            f"this run finds {len(bad)}, so the comparison in the docstring is "
            f"stale")

    def test_the_faithful_map_is_still_faithful(self):
        """The strong vendors must stay on the strong model, or the whole
        argument for raising the budget instead of remapping collapses."""
        for strong in ("Codex-SIM", "CC2-SIM", "ChatGPT-SIM"):
            assert SHIM.DEFAULT_LADDER.get(strong) == "opus", (
                f"{strong} is a top-3 vendor in the validated strength order and "
                f"is no longer on the strong model; if the map is remapped, the "
                f"budget rationale needs rewriting")
