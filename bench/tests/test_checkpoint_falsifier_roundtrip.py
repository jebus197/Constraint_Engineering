"""A falsifier must survive a checkpoint save/resume cycle.

Found 2026-08-12 while verifying a figure for a panel prompt. ``falsifier_code``
is declared on ``Finding`` but was never written by ``_save_checkpoint`` or
``_save_round_json``, and never read back by ``load_checkpoint``. Measured across
all 56 archived runs and 8500+ findings: not one checkpoint carried a falsifier.

SCOPE — the first reading of this was wrong and the correction is the useful part.
It looked like a convergence defect: CONFIRM-only resolves a critical by a runnable
falsifier and nothing else, so a resume that dropped falsifiers would leave
criticals permanently unresolvable. Resume is routine (33 run artefacts; Exp 47 was
resumed from round 5 twice), so that would have been severe.

It was refuted by measurement. reference_runner_v2 keeps a SECOND checkpoint,
runner_state.json, which persists the registry including falsifier source and
verdict and restores it on resume. Exp 47's post-resume registry still holds 58
falsifiers with 55 CONFIRMED. No run's convergence was affected.

What remains, and why this is still worth pinning: runner_state.json is a single
point of failure for the one artefact the discipline depends on, and the loader at
reference_runner_v2.py:8178 already handles finding it corrupted. When that happens
the falsifiers should survive in the other checkpoint instead of being gone. Replay
and analysis tooling reading checkpoint.json also sees them now.

Same class as the provenance-field fix of 13 April 2026.
"""
from __future__ import annotations

import json

import pytest

from bench.dm._types import DynamicManagementConfig
from bench.insect_brain import Finding, InsectBrain


FALSIFIER = (
    "from pathlib import Path\n"
    "t = Path('target.md')\n"
    "assert 'rate limit' in t.read_text(), 'FALSIFIED: clause absent'\n"
)


def _finding(**kw) -> Finding:
    base = dict(
        finding_id="F001", model_id="Codex", round_idx=0, flaw_class=2,
        severity=0.85, abstraction_index=0.45, description="d", proposed_fix="p",
    )
    base.update(kw)
    return Finding(**base)


@pytest.fixture()
def brain(tmp_path):
    b = InsectBrain(
        config=DynamicManagementConfig(), logs_dir=tmp_path, source_paths=["x.py"])
    b.initialise(["CC2", "Gemini", "DeepSeek", "Codex", "ChatGPT"])
    return b


def test_falsifier_survives_checkpoint_roundtrip(brain):
    """The regression itself: save, reload, and the falsifier is still there."""
    brain.state.all_findings = [[_finding(
        falsifier_code=FALSIFIER, falsifier_verdict="CONFIRMED", verified=True)]]
    brain._save_checkpoint()

    brain.state.all_findings = []          # simulate the fresh process a resume starts in
    assert brain.load_checkpoint() is True

    restored = brain.state.all_findings[0][0]
    assert restored.falsifier_code == FALSIFIER, (
        "falsifier lost across resume — the finding is now unresolvable under "
        "CONFIRM-only despite having been demonstrated before the interruption")
    assert restored.falsifier_verdict == "CONFIRMED"


def test_checkpoint_json_actually_contains_the_falsifier(brain, tmp_path):
    """Guards against a round trip that passes by luck rather than by storage."""
    brain.state.all_findings = [[_finding(falsifier_code=FALSIFIER)]]
    brain._save_checkpoint()

    payload = json.loads((tmp_path / "checkpoint.json").read_text())
    entry = payload["all_findings"][0][0]
    assert entry.get("falsifier_code") == FALSIFIER


def test_falsifier_is_not_truncated(brain):
    """A clipped falsifier looks present and then fails to execute.

    That is strictly worse than an absent one, so the checkpoint stores it whole.
    """
    long_falsifier = "# padding\n" * 2000 + "assert False, 'FALSIFIED'\n"
    brain.state.all_findings = [[_finding(falsifier_code=long_falsifier)]]
    brain._save_checkpoint()
    brain.state.all_findings = []
    brain.load_checkpoint()

    restored = brain.state.all_findings[0][0]
    assert restored.falsifier_code == long_falsifier
    assert restored.falsifier_code.endswith("assert False, 'FALSIFIED'\n"), (
        "tail lost — a truncated falsifier will not run")


def test_pre_fix_checkpoints_still_load(brain, tmp_path):
    """The 56 archived checkpoints predate the field and must remain readable.

    They legitimately carry no falsifier; loading must yield an empty one rather
    than raising, so the absence stays visible instead of becoming a crash.
    """
    brain.state.all_findings = [[_finding()]]
    brain._save_checkpoint()

    path = tmp_path / "checkpoint.json"
    payload = json.loads(path.read_text())
    for rnd in payload["all_findings"]:            # strip the new keys entirely
        for entry in rnd:
            entry.pop("falsifier_code", None)
            entry.pop("falsifier_verdict", None)
            entry.pop("corroboration_present", None)
    path.write_text(json.dumps(payload))

    brain.state.all_findings = []
    assert brain.load_checkpoint() is True
    assert brain.state.all_findings[0][0].falsifier_code == ""


def test_corroboration_present_is_restored_without_being_a_field(brain):
    """runner_core attaches this dynamically, so it cannot go through __init__.

    Pinned because the obvious implementation — passing it to the constructor —
    raises TypeError, and the equally obvious writer — reading it as a plain
    attribute — raises AttributeError on findings that never met the gate.
    """
    f = _finding()
    object.__setattr__(f, "corroboration_present", True)
    brain.state.all_findings = [[f]]
    brain._save_checkpoint()

    brain.state.all_findings = []
    brain.load_checkpoint()
    assert getattr(brain.state.all_findings[0][0], "corroboration_present") is True


def test_writer_tolerates_a_finding_that_never_met_the_gate(brain):
    """A Finding built directly has no corroboration_present attribute at all."""
    brain.state.all_findings = [[_finding()]]
    brain._save_checkpoint()          # must not raise AttributeError
    brain.state.all_findings = []
    assert brain.load_checkpoint() is True
