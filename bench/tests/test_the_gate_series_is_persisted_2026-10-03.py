#!/usr/bin/env python3
"""The series the convergence gate decides on must survive into the saved state.

`gamma_history` is the ALL-SEVERITY decay curve. The two-sided gate reads
`gamma_critical`, the critical-only curve. That series is built in
`run_experiment` and was written to the REPORT but never to `runner_state.json`,
so the registry could not show why a run converged or did not.

MEASURED ACROSS THE ARCHIVE before the repair, by
`scripts/gate_input_is_not_persisted_2026-10-03.py`: 76 of 81 directories holding
a state or report file carry no `gamma_critical_history` at all, 93.8272%, Wilson
[86.3508%, 97.3347%]; of those 76, only 2 can recover it from a log line, 2.6316%,
Wilson [0.7247%, 9.0966%]. So 74 archived runs hold the gate's deciding input in no
durable place. Falsified against the obvious alternative: enumerating every
top-level key containing "gamma" across all 81 files gives `gamma_history` (65),
`gamma` (12), `gamma_gate_series` (5), `gamma_all_history` (5),
`gamma_critical_history` (5) and `gamma_threshold_profile` (4) -- the only gamma key
mentioning "crit" is the missing one, and the 3 richer keys occur in the same 5
well-instrumented files, so they do not rescue the other 76.

THE COST WAS REAL. A replay script fell back to `gamma_history` when the key was
absent and printed 0.4274 under the label `gamma_critical`; the run's true value was
0.732, and the wrong figure reached the founder repeatedly before a panel seat
caught it.

These tests check the PAYLOAD SHAPE by AST, because the dict literal sits inside an
18,000-line function that cannot be executed without running a whole experiment, and
they check the post-sweep merge BY EXECUTION, because that site overwrites the same
file and is where a key silently disappears.
"""
import ast
import json
import pathlib

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
RUNNER = REPO / "bench" / "reference_runner_v3.py"
KEY = "gamma_critical_history"
SIBLING = "gamma_history"


def _checkpoint_dicts():
    """Every dict literal in the runner that looks like the state payload."""
    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = {k.value for k in node.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)}
        # the state payload is identifiable by carrying BOTH of these
        if {"registry", SIBLING} <= keys:
            out.append((node.lineno, keys))
    return out


class TestThePremiseIsAlive:
    def test_the_state_payload_can_be_found_at_all(self):
        found = _checkpoint_dicts()
        assert found, (
            "no dict literal in the runner carries both 'registry' and "
            f"'{SIBLING}'; this guard can no longer locate the state payload and "
            "must be repaired rather than left passing vacuously"
        )

    def test_the_critical_series_variable_exists_in_the_runner(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert f"{KEY}: List[float] = []" in src or f"{KEY} = []" in src, (
            f"{KEY} is not built anywhere; persisting it would persist nothing"
        )
        assert f"{KEY}.append(" in src, f"{KEY} is never appended to"


class TestTheSeriesIsInThePayload:
    def test_every_state_payload_carries_the_gate_series(self):
        for lineno, keys in _checkpoint_dicts():
            assert KEY in keys, (
                f"the state payload at line {lineno} persists '{SIBLING}' (the "
                f"ALL-SEVERITY curve) but not '{KEY}' (the series the gate "
                f"actually decides on). A registry that cannot show the deciding "
                f"input cannot be audited, and a reader who falls back to "
                f"'{SIBLING}' is auditing a different curve under the gate's name."
            )

    def test_the_sibling_is_still_there_too(self):
        """Additive: the all-severity curve is not removed to make room."""
        for _lineno, keys in _checkpoint_dicts():
            assert SIBLING in keys


class TestThePostSweepMergeDoesNotDropIt:
    """The second write site overwrites the same file. It reads-then-updates, so
    unrelated keys must survive; this executes that merge rather than reading it."""

    def test_an_existing_gate_series_survives_the_post_sweep_update(self, tmp_path):
        path = tmp_path / "runner_state.json"
        path.write_text(json.dumps({
            KEY: [0.1, 0.5, 0.732],
            SIBLING: [0.2, 0.3, 0.4274],
            "registry": {"entries": {}},
        }), encoding="utf-8")

        # the merge as the runner performs it
        rs = json.loads(path.read_text(encoding="utf-8"))
        rs["registry"] = {"entries": {"C0001": {}}}
        rs["post_convergence_sweep"] = {"cleared": 1}
        path.write_text(json.dumps(rs, indent=2), encoding="utf-8")

        after = json.loads(path.read_text(encoding="utf-8"))
        assert after[KEY] == [0.1, 0.5, 0.732], (
            "the post-sweep write dropped the gate series; it must read-then-update"
        )
        assert after["registry"]["entries"], "the merge did not apply its own change"

    def test_a_wholesale_overwrite_would_lose_it(self, tmp_path):
        """The mutation, as a property rather than a patch: if that site ever
        stops reading the file first, the key goes. This records why the
        read-then-update shape is load-bearing."""
        path = tmp_path / "runner_state.json"
        path.write_text(json.dumps({KEY: [0.732]}), encoding="utf-8")
        path.write_text(json.dumps({"registry": {}}), encoding="utf-8")  # no read
        assert KEY not in json.loads(path.read_text(encoding="utf-8"))
