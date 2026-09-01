"""No config key the runner honours may be silently dropped by the launcher.

This failure class has bitten the project FOUR times (routing 2026-07-12,
max_contested_rounds 2026-07-27, feedback_channel_enabled 2026-07-29, and the
gamma/stall trio 2026-07-29 — the last of which meant the 2x2 factorial's
primary factor would have run ON in every cell). The launcher maps by explicit
whitelist, so any new RunnerConfig field is dropped by default. This test makes
that failure loud at test time instead of silent at experiment time.
"""
from __future__ import annotations

import os
import sys
from types import SimpleNamespace

_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _root not in sys.path:
    sys.path.insert(0, _root)

from bench.launcher_core import build_runner_config_from_dict  # noqa: E402
from bench.reference_runner_v3 import RunnerConfig  # noqa: E402

# Every field whose value changes experimental behaviour. A field added to
# RunnerConfig and omitted here is caught by test_no_unreviewed_fields below.
BEHAVIOURAL = [
    ("routing_enabled", True), ("falsifier_gate_enabled", True),
    ("location_keyed_convergence", True), ("max_contested_rounds", 3),
    ("post_convergence_sweep_rounds", 2), ("immune_memory_enabled", True),
    ("immune_memory_rho", 0.35), ("immune_memory_consume_rk0", True),
    ("gamma_alt_threshold", 0.35), ("gamma_alt_consecutive_zero_crit", 4),
    ("stall_gamma_terminate", 1.01), ("stall_gamma_advisory", 1.01),
    ("gamma_telemetry_only_until", 20), ("hardened_gate_enabled", False),
    ("merge_arbitration_enabled", True), ("apply_fixes_back_enabled", False),
    ("panel_cwd", "/tmp"),
]


def _both_paths(key, value):
    cfg = {"experiment_name": "t", "models": ["CC2"], "test_article": "x.md", key: value}
    return (getattr(RunnerConfig.from_dict(dict(cfg)), key, "<missing>"),
            getattr(build_runner_config_from_dict(cfg, SimpleNamespace(resume=False)),
                    key, "<missing>"))


class TestNoSilentDrops:
    def test_every_behavioural_key_survives_both_paths(self):
        dropped = []
        for key, value in BEHAVIOURAL:
            runner, launcher = _both_paths(key, value)
            if runner != value or launcher != value:
                dropped.append(f"{key}: runner={runner!r} launcher={launcher!r} want={value!r}")
        assert not dropped, "SILENTLY DROPPED BY A CONFIG PATH:\n  " + "\n  ".join(dropped)

    def test_gamma_telemetry_key_specifically(self):
        """The one with teeth: JSON 20 must not become the code default 14."""
        runner, launcher = _both_paths("gamma_telemetry_only_until", 20)
        assert runner == 20 and launcher == 20

    def test_feedback_and_divergence_factors_survive(self):
        """The 2x2's two factors — if either is dropped, every cell is identical."""
        for key in ("feedback_channel_enabled", "divergence_channel_enabled"):
            runner, launcher = _both_paths(key, False)
            assert runner is False and launcher is False, f"{key} dropped"


class TestNoFieldCanEverBeDroppedAgain:
    """Exhaustive, not a hand-maintained list.

    `BEHAVIOURAL` above is curated by hand, which is why this failure class kept
    recurring: a field added to RunnerConfig is dropped by the launcher's
    whitelist until somebody remembers BOTH to add the mapping AND to add the
    field to that list. Nobody reliably does either.

    A systematic sweep on 2026-08-01 compared EVERY RunnerConfig field across
    both ingestion paths and found TWENTY silently dropped — among them
    `max_open_crit_high`, `gamma_hard_threshold`, `gamma_soft_threshold`,
    `min_rounds_for_gamma`, `stall_window`, `rho_earliest_round` (all
    convergence-critical) and `max_irreducible_queue`, the setting whose
    mis-application halted the zero-plant control. No shipped config set any of
    them, so nothing on the record was affected — the gap was latent, and would
    have fired the moment one was set.

    The launcher now fills any unmapped RunnerConfig field straight from the
    JSON, so the two paths agree by construction rather than by upkeep. This
    test enforces that property directly and needs no maintenance.
    """

    # Set from CLI argv, not from the experiment JSON — out of scope by design.
    CLI_OWNED = {"resume", "hil_review"}
    # Structural inputs handled explicitly by the builder.
    STRUCTURAL = {"experiment_name", "models", "test_article", "context_files",
                  "model_configs"}

    @staticmethod
    def _probe(field):
        """A value guaranteed to differ from the field's default."""
        d = field.default
        if isinstance(d, bool):
            return not d
        if isinstance(d, int):
            return d + 7
        if isinstance(d, float):
            return round(d + 0.13, 4)
        if isinstance(d, str):
            return (d + "_x") if d else "/tmp"
        return None

    def test_every_scalar_field_survives_both_paths(self):
        import dataclasses
        base = {"experiment_name": "t", "models": ["CC2"], "test_article": "x.md"}
        skip = self.CLI_OWNED | self.STRUCTURAL
        dropped, checked = [], 0
        for f in dataclasses.fields(RunnerConfig):
            if f.name in skip:
                continue
            value = self._probe(f)
            if value is None:          # non-scalar default; not probeable this way
                continue
            cfg = {**base, f.name: value}
            try:
                runner = getattr(RunnerConfig.from_dict(dict(cfg)), f.name, "<missing>")
                launcher = getattr(
                    build_runner_config_from_dict(dict(cfg), SimpleNamespace(resume=False)),
                    f.name, "<missing>")
            except Exception:          # a field the builder legitimately rejects
                continue
            checked += 1
            if runner == value and launcher != value:
                dropped.append(f"{f.name}: config={value!r} launcher gave {launcher!r}")
        assert checked >= 50, (
            f"only {checked} fields probed — the probe has gone blind, which would "
            f"make this test pass vacuously")
        assert not dropped, (
            f"{len(dropped)} RunnerConfig field(s) are silently dropped by the "
            f"launcher path — the class this test exists to end:\n  "
            + "\n  ".join(sorted(dropped)))

    def test_the_specific_key_that_halted_the_control(self):
        """`max_irreducible_queue` gates convergence on the zero-plant control.

        The code default of 2 is calibrated for CODE review, where a genuinely
        irreducible defect is rare. On a prose document with nothing planted,
        findings no tool can settle are the EXPECTED output, so the control needs
        a higher bound — which is useless if the launcher discards it.
        """
        runner, launcher = _both_paths("max_irreducible_queue", 8)
        assert runner == launcher == 8
