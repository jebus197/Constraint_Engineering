#!/usr/bin/env python3
"""How a seat's coherence budget is resolved, and what about it needs a ruling.

TWO FOUNDER RULINGS MEET HERE.

2026-10-07, on capability and names: *"We for sure had a big discussion about
removing model names as a mark of capability and replacing them with model IDs.
It seemed natural that these should be hashed model IDs? Names are recorded for
provenance only!"*

2026-10-16, on the coherence budget recalibration: *"It should be fixed,
providing it doesn't trim the operational directives. It exists so that models
never get fed work that is larger than they have been demonstrably proven to be
able to handle in any experiment. Not to trim the operational directives."*

THE RESOLUTION CHAIN HAS TWO HOPS, AND DROPPING THE SECOND ONE HAS ALREADY
CAUSED A WRONG WITHDRAWAL:

    base   = base_model_label(seat)               # Gemini-SIM  -> Gemini
    cmodel = COMPOSER_MODEL_MAP.get(base, base)   # Gemini      -> gemini_3_1_pro
    budget = MODEL_COHERENCE_BUDGETS.get(cmodel, DEFAULT_COHERENCE_BUDGET)

On 2026-10-16 the committed 2026-10-13 claim that the seats carry 4 distinct
budgets was measured WITHOUT the middle line, came out as one uniform budget,
and was withdrawn on that basis. It should not have been: through the full chain
the claim is correct. The withdrawal was reversed and the claim restored. The
first test below exists so that error cannot be repeated silently.

WHAT IS PINNED AS CORRECT, AND WHAT IS PINNED AS AWAITING HIS RULING. The
no-trim constraint is satisfied structurally and is pinned as a property. The
name-keyed capability is NOT pinned as correct: it is pinned as the current state
with the conflict stated, so that any change to it is deliberate and so that the
open question stays visible instead of dissolving into a green board.

NOTHING IS REMOVED. The table and the map stay exactly as they are.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "bench"))

from cdsfl_registry import composer as C  # noqa: E402
import reference_runner_v3 as R  # noqa: E402

SUFFIX = "-SIM"
#: Keys whose names denote a model version the current roster has moved past.
#: Measured by scripts/what_budget_does_each_seat_actually_get_2026-10-16.py.
STALE_VERSION_KEYS = ("opus_4_6", "chatgpt_5_4", "codex_5_3", "deepseek_v3")


def live_labels() -> list[str]:
    bases = sorted(set(R.MODEL_ROSTER) | {"Fable"})
    out: list[str] = []
    for b in bases:
        out += [b, f"{b}{SUFFIX}"]
    return out


def budget_for(label: str) -> float:
    """The FULL chain the runner evaluates, called rather than described."""
    base = R.base_model_label(label)
    cmodel = C.COMPOSER_MODEL_MAP.get(base, base)
    return C.MODEL_COHERENCE_BUDGETS.get(cmodel, C.DEFAULT_COHERENCE_BUDGET)


def budget_without_the_map_hop(label: str) -> float:
    """The resolution that caused the 2026-10-16 mis-withdrawal."""
    return C.MODEL_COHERENCE_BUDGETS.get(
        R.base_model_label(label), C.DEFAULT_COHERENCE_BUDGET)


# ───────────────── the dropped hop, which is my own recorded error ────────────

def test_the_two_resolutions_disagree_so_the_hop_cannot_be_dropped_silently():
    """The guard on the 2026-10-16 error itself.

    If these two ever agree, a future reader can drop the `COMPOSER_MODEL_MAP`
    hop and measure the budget wrongly without anything complaining -- which is
    exactly what happened. While they disagree, the naive form is detectably
    wrong.
    """
    full = {l: budget_for(l) for l in live_labels()}
    naive = {l: budget_without_the_map_hop(l) for l in live_labels()}
    differing = sorted(l for l in full if full[l] != naive[l])
    assert differing, (
        "the full chain and the map-less chain now agree on every seat, so the "
        "2026-10-16 measurement error is no longer self-revealing. Re-derive "
        "this guard before trusting any budget figure."
    )
    assert len(set(naive.values())) == 1, (
        "the map-less resolution no longer collapses to one value; the shape of "
        "the recorded error has changed and this test's premise needs re-reading"
    )


def test_the_committed_claim_of_four_distinct_budgets_holds():
    """The 2026-10-13 claim, re-measured through the full chain.

    It was attacked and the attack failed. Pinned so it does not have to be
    re-litigated a third time.
    """
    distinct = sorted({budget_for(l) for l in live_labels()})
    assert distinct == [0.01, 0.012, 0.015, 0.02], distinct


def test_a_simulated_seat_receives_the_same_budget_as_its_paid_base():
    """A `-SIM` stand-in must not be treated as more or less capable."""
    for base in sorted(set(R.MODEL_ROSTER) | {"Fable"}):
        assert budget_for(base) == budget_for(f"{base}{SUFFIX}"), base


# ─────────── name-keyed capability: pinned as OPEN, not as correct ────────────

def test_capability_is_still_keyed_on_a_model_name_and_this_awaits_his_ruling():
    """NEEDS HIS RULING. Pinned so the conflict stays visible.

    A seat's density allowance is resolved from its NAME, and 4 of the 5 keys
    name versions the roster has moved past -- `opus_4_6` against Opus 4.7,
    `chatgpt_5_4` and `codex_5_3` against GPT-5.5, `deepseek_v3` against
    DeepSeek V4 Pro. So a live seat inherits a dense-instruction allowance
    written for a superseded model, selected by name. His ruling of 2026-10-07
    is that names are recorded for provenance only.

    This test asserts the CURRENT state rather than the desired one, because the
    desired one is his to choose. It goes red the moment the resolution changes,
    which is the point: the change should be a ruling, not a drift.
    """
    stale_live = []
    for label in live_labels():
        base = R.base_model_label(label)
        cmodel = C.COMPOSER_MODEL_MAP.get(base, base)
        if cmodel in STALE_VERSION_KEYS:
            stale_live.append((label, cmodel, budget_for(label)))
    assert stale_live, (
        "no live seat resolves to a superseded version key any more. If that was "
        "a deliberate repair, record his ruling and re-derive this test; if it "
        "was a drift, it needs checking."
    )
    # And the allowance genuinely varies by name, which is the substance.
    by_name = {cmodel: b for _, cmodel, b in stale_live}
    assert len(set(by_name.values())) > 1, by_name


def test_the_declared_keys_are_still_recorded_and_not_deleted():
    """`additive-standard`: the table is a measurement record, not scratch."""
    for key in STALE_VERSION_KEYS + ("gemini_3_1_pro",):
        assert key in C.MODEL_COHERENCE_BUDGETS, (
            f"{key} was deleted from MODEL_COHERENCE_BUDGETS. It is the record "
            f"of what was once measured. Point at it; do not prune it."
        )


# ───────────────── his no-trim constraint, enforced structurally ──────────────

def test_the_directive_pruner_is_off_by_default():
    """His 2026-10-13 ruling retired it; his 2026-10-16 ruling says the budget
    must not 'trim the operational directives'. A True default puts the budget
    back in the business of deleting directive text."""
    assert getattr(R.RunnerConfig(), "composer_coherence_pruning") is False


def test_a_recalibrated_budget_changes_no_directive_text_while_pruning_is_off():
    """Executed, not reasoned: recompose with an impossible budget.

    `compose` is the real entry point and `rendered_text` is the real prompt, so
    this exercises what a seat actually receives.
    """
    label = sorted(set(R.MODEL_ROSTER))[0]
    cmodel = C.COMPOSER_MODEL_MAP.get(label, label)
    loose = C.compose("mathematics", cmodel, coherence_pruning=False)

    saved = C.MODEL_COHERENCE_BUDGETS.get(cmodel)
    C.MODEL_COHERENCE_BUDGETS[cmodel] = 1e-9
    try:
        tight = C.compose("mathematics", cmodel, coherence_pruning=False)
    finally:
        if saved is None:
            C.MODEL_COHERENCE_BUDGETS.pop(cmodel, None)
        else:
            C.MODEL_COHERENCE_BUDGETS[cmodel] = saved

    assert tight.coherence_budget == 1e-9, (
        "the forced budget never reached the composer, so this test proves "
        "nothing about trimming"
    )
    assert loose.rendered_text == tight.rendered_text, (
        "tightening the coherence budget by 7 orders of magnitude changed the "
        "composed directive text while pruning was OFF, so the budget can still "
        "trim operational directives. His 2026-10-16 ruling forbids exactly "
        f"this: {len(loose.rendered_text)} chars -> {len(tight.rendered_text)}"
    )
    assert not tight.pruned_soft, tight.pruned_soft


def test_the_pruner_does_trim_when_switched_on_so_the_test_above_is_not_vacuous():
    """The companion falsifier: prove the budget CAN trim, then that it does not.

    Without this, the test above would pass just as happily if the budget were
    inert for some unrelated reason, and would verify nothing.
    """
    label = sorted(set(R.MODEL_ROSTER))[0]
    cmodel = C.COMPOSER_MODEL_MAP.get(label, label)
    saved = C.MODEL_COHERENCE_BUDGETS.get(cmodel)
    C.MODEL_COHERENCE_BUDGETS[cmodel] = 1e-9
    try:
        pruned = C.compose("mathematics", cmodel, coherence_pruning=True)
        intact = C.compose("mathematics", cmodel, coherence_pruning=False)
    finally:
        if saved is None:
            C.MODEL_COHERENCE_BUDGETS.pop(cmodel, None)
        else:
            C.MODEL_COHERENCE_BUDGETS[cmodel] = saved

    assert pruned.rendered_text != intact.rendered_text or pruned.pruned_soft, (
        "switching pruning ON with an impossible budget changed nothing, so the "
        "no-trim test above is vacuous. Re-derive both before trusting either."
    )


# ─────────────── the recalibrator still has no measured input ────────────────

def test_the_composer_already_computes_the_field_the_recalibrator_needs():
    """`constraint_count` exists at composition time. It simply is not persisted.

    This matters for the fix: the recalibration's missing input is not missing,
    it is unrecorded, so making it measurable costs a field in the run record
    rather than new instrumentation.
    """
    label = sorted(set(R.MODEL_ROSTER))[0]
    cmodel = C.COMPOSER_MODEL_MAP.get(label, label)
    composed = C.compose("mathematics", cmodel, coherence_pruning=False)
    assert composed.constraint_count > 0, composed.constraint_count
    assert composed.token_estimate > 0, composed.token_estimate
    assert composed.constraint_density > 0, composed.constraint_density


def test_no_dispatch_record_carries_constraint_count_yet():
    """Pins the diagnosis so it goes red when recording starts.

    The recalibrator reads `constraint_count` and falls back to an estimator
    when it is absent. The estimator is `(chars//70)/(chars//4)`, which is
    independent of the prompt's actual constraint content, so every calibrated
    threshold it has ever produced is an artefact of that formula rather than a
    measurement of a model.
    """
    logs = REPO_ROOT / "bench" / "logs"
    if not logs.is_dir():
        pytest.skip("no archive to measure against")
    seen = 0
    with_count = 0
    for path in sorted(logs.rglob("*.json")):
        try:
            doc = json.loads(path.read_text(errors="replace"))
        except (OSError, ValueError):
            continue

        def walk(obj):
            nonlocal seen, with_count
            if isinstance(obj, dict):
                if "response" in obj or "model" in obj:
                    seen += 1
                    if "constraint_count" in obj:
                        with_count += 1
                for v in obj.values():
                    walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    walk(v)

        walk(doc)
    assert seen > 0, "no candidate dispatch entries found at all"
    assert with_count == 0, (
        f"{with_count} of {seen} dispatch entries now carry `constraint_count`, "
        f"so the recalibration can measure real density for the first time. Its "
        f"design question -- what the budget should govern now the pruner is "
        f"retired -- is live. Revisit it deliberately rather than deleting this."
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
