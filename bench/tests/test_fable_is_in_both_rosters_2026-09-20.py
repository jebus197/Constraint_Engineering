#!/usr/bin/env python3
"""Fable is a seat on BOTH dispatch paths, not just the panel's.

FOUNDER, 2026-09-20: panels and paid experiments should both run 6 models.

WHAT WAS WRONG. `bench/confer_maths_panel_2026-09-05.py` carried 6 seats from
that day. `bench/experiment_11_orchestrator.load_default_config` carried 5. The
2 dispatch paths therefore disagreed about what "the panel" means, and a reader
of either file alone would have been correctly informed and wrong.

AVAILABLE IS NOT IMPOSED, and this file pins the distinction rather than
blurring it. An experiment runs the seats its own `RunnerConfig` names. Adding a
6th `ModelConfig` makes the seat REACHABLE; it does not change the composition of
anything already designed. Whether the Exp 40-54 arc should adopt a 6th seat
mid-arc is a comparability question -- a 6-seat run is not directly comparable
with the 5-seat runs before it -- and that is the founder's ruling to make.

THE SECONDARY ROUTE IS HONEST ABOUT WHAT IT IS. The founder's rule of 2026-05-22
is that every model carries a secondary, preferring the same underlying model on
another route. Fable has no second route. Its secondary is the other
Max-subscription CLI seat, which keeps billing consolidated -- the rule's other
stated aim -- and is a DIFFERENT model rather than the same one reached another
way. Tested below so that fact is recorded rather than assumed.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "bench" / "confer_maths_panel_2026-09-05.py"
sys.path.insert(0, str(ROOT))


def _roster():
    from bench.experiment_11_orchestrator import load_default_config
    return load_default_config().models


def _panel_seats():
    sys.path.insert(0, str(ROOT / "bench"))
    spec = importlib.util.spec_from_file_location("panel_roster_probe", PANEL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod._ALL


class TestBothRostersCarrySixSeats:

    def test_the_experiment_roster_has_6(self):
        labels = [m.label for m in _roster()]
        assert len(labels) == 6, f"expected 6 experiment seats, got {len(labels)}: {labels}"

    def test_the_panel_roster_has_6(self):
        seats = _panel_seats()
        assert len(seats) == 6, f"expected 6 panel seats, got {len(seats)}"

    def test_fable_is_on_both(self):
        assert "Fable" in [m.label for m in _roster()], (
            "Fable is missing from the experiment roster, so the 2 dispatch "
            "paths disagree about the panel's composition again")
        assert "fable" in [n for n, _, _ in _panel_seats()]

    def test_the_same_4_paid_vendors_appear_on_both(self):
        """The free CLI seats are CC2 and Fable on both sides; the paid ones are
        Codex, ChatGPT, Gemini and DeepSeek. A roster that drifted would show up
        here as a mismatch rather than as a surprise during a paid round."""
        exp_free = {m.label.lower() for m in _roster() if m.api == "claude_cli"}
        panel_free = {n for n, _, r in _panel_seats() if r == "claude_cli"}
        assert exp_free == {"cc2", "fable"}, exp_free
        assert panel_free == {"cc2", "fable"}, panel_free


class TestTheFableSeatIsUsable:

    def test_it_dispatches_through_the_CLI_not_a_paid_route(self):
        fable = next(m for m in _roster() if m.label == "Fable")
        assert fable.api == "claude_cli", (
            f"Fable is configured on {fable.api}, which would bill a seat the "
            f"Max subscription already covers")
        assert fable.model_id == "fable"

    def test_it_carries_a_secondary_like_every_other_seat(self):
        fable = next(m for m in _roster() if m.label == "Fable")
        assert fable.secondary_api and fable.secondary_model_id, (
            "founder rule 2026-05-22: every model carries a secondary route")

    def test_its_secondary_is_recorded_as_a_DIFFERENT_model(self):
        """Not a defect, and written down so it is never mistaken for one: the
        fallback reaches Opus, not Fable by another road."""
        fable = next(m for m in _roster() if m.label == "Fable")
        assert fable.secondary_model_id != fable.model_id
        assert fable.secondary_api == "claude_cli", (
            "the fallback should stay on the subscription rather than move the "
            "seat onto a paid route mid-round")

    def test_it_gets_the_CLI_timeout_budget_not_the_api_one(self):
        """A CLI seat is slower than an HTTP one. CC2 was moved to 900 s and 1
        retry in WP4a precisely to stop a timeout cascade; Fable inherits both."""
        fable = next(m for m in _roster() if m.label == "Fable")
        cc2 = next(m for m in _roster() if m.label == "CC2")
        assert fable.timeout == cc2.timeout == 900
        assert fable.max_retries == cc2.max_retries == 1


class TestAddingItChangedNoExistingExperiment:
    """The additive half: a new seat that silently rewrote a designed condition
    would not be additive, it would be a substitution."""

    def test_no_shipped_config_names_fable(self):
        named = []
        for cfg in (ROOT / "bench" / "exp56_configs").glob("*.json"):
            if "fable" in cfg.read_text(encoding="utf-8").lower():
                named.append(cfg.name)
        assert not named, (
            f"{named} now name Fable, so adopting the seat has changed an "
            f"already-designed experiment's composition. That is the founder's "
            f"ruling to make, not a side effect of adding the seat.")
