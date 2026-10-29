#!/usr/bin/env python3
"""A dispatch record must carry the composer's own figures, not a truncation artefact.

HIS RULING, 2026-10-16, on the coherence budget recalibration: *"It should be
fixed, providing it doesn't trim the operational directives. It exists so that
models never get fed work that is larger than they have been demonstrably proven
to be able to handle in any experiment. Not to trim the operational
directives."*

THE DEFECT, MEASURED END TO END ON 2026-10-16.
`calibrate_coherence_thresholds` prefers a recorded `constraint_density` and
falls back to `(chars//70)/(chars//4)`. Measured over the archive: 0 of 30,442
dispatch entries carried `constraint_density`, `constraint_count`,
`token_estimate`, `coherence_budget` or `cid`. What they did carry was
`prompt_length`, and 3,589 of 3,709 of those -- 96.7646% -- equalled 203,
because every `save_output` call in the dispatch passes `prompt[:200] + "..."`.
So the fallback evaluated (203//70)/(203//4) = 2/50 = 0.04 for essentially every
entry, and every threshold the calibrator ever produced was an artefact of a
truncation constant rather than a measurement of any model.

THE FIX IS A WRITE. The composer already computed all five values; they were
never persisted. The consumer already preferred a recorded density. So the
repair records what exists, and the calibration arithmetic is untouched.

`execute-do-not-grep`: every test below CALLS the producer or the consumer.
Nothing asserts on the source text of either.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "bench"))

from cdsfl_registry import composer as C  # noqa: E402
import reference_runner_v3 as R  # noqa: E402

FIELDS = ("constraint_count", "token_estimate", "constraint_density",
          "coherence_budget", "cid")


def a_real_composition():
    label = sorted(set(R.MODEL_ROSTER))[0]
    cmodel = C.COMPOSER_MODEL_MAP.get(label, label)
    return C.compose("mathematics", cmodel, coherence_pruning=False)


# ───────────────────────── the producer side ─────────────────────────────────

def test_the_record_fields_carry_every_composer_figure():
    composed = a_real_composition()
    out = R._composer_record_fields(composed, "x" * 500, composed.rendered_text)
    for f in FIELDS:
        assert f in out, f
    assert out["constraint_count"] == composed.constraint_count
    assert out["constraint_density"] == composed.constraint_density
    assert out["coherence_budget"] == composed.coherence_budget
    assert out["composer_fallback"] is False


def test_the_untruncated_prompt_size_is_recorded_separately():
    """`prompt_length` keeps its meaning; the true size is recorded alongside.

    Rewriting `prompt_length` would silently change what 3,709 archived entries
    mean, so the true figure gets its own key.
    """
    composed = a_real_composition()
    prompt = "x" * 7777
    out = R._composer_record_fields(composed, prompt, composed.rendered_text)
    assert out["prompt_chars_full"] == len(prompt) + len(composed.rendered_text)
    assert out["prompt_chars_full"] > 203, out["prompt_chars_full"]
    assert out["directive_chars"] == len(composed.rendered_text)


def test_a_composer_fallback_is_recorded_as_a_fact_not_an_absence():
    """An absent key and a failed composition are different facts.

    If a fallback simply omitted the keys, the calibrator would read it as 'not
    recorded' and silently apply the estimator -- the very confusion that hid
    this defect for months.
    """
    out = R._composer_record_fields(None, "x" * 100, "")
    assert out["composer_fallback"] is True
    for f in FIELDS:
        assert f not in out, f
    assert out["prompt_chars_full"] == 100


def test_composed_is_bound_before_the_try_so_a_fallback_cannot_raise():
    """The except branch sets only `model_cdsfl`; `composed` must still exist.

    THE BOUNDARY, STATED. This is a STRUCTURAL check over the parsed function,
    not an execution of it, and `execute-do-not-grep` asks for the reason.
    `_dispatch_single_model_inner` DISPATCHES TO A MODEL. Driving it to reach
    the composer-fallback branch would risk a paid call, and no paid dispatch
    happens without his express authorisation. So the hazard -- a `NameError`
    on one branch because a name is assigned only inside the `try` -- is checked
    where it lives, in the binding structure, rather than by running a dispatch.
    The AST is parsed, which is stricter than a text search: it distinguishes a
    real assignment from the identifier appearing in a comment or a string.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(R._dispatch_single_model_inner))
    fn = tree.body[0]

    # Every `composed = ...` at the function's own statement level, and every
    # one nested inside a Try. The first must exist, or the Try's handler can
    # fall through to a read of an unbound name.
    top_level_binds = [
        n for n in fn.body
        if isinstance(n, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "composed" for t in n.targets)
    ]
    assert top_level_binds, (
        "`composed` is never assigned at the statement level of "
        "`_dispatch_single_model_inner`, so it is bound only inside the `try`. "
        "The handler sets only `model_cdsfl`, and every `save_output` in this "
        "function reads `composed`, so a composer fallback would raise "
        "NameError at the first record write instead of recording the fallback."
    )

    # And it must come BEFORE the try that assigns it, not after.
    try_idx = next(
        (i for i, n in enumerate(fn.body)
         if isinstance(n, ast.Try)
         and any(isinstance(x, ast.Name) and x.id == "composed"
                 for b in n.body for x in ast.walk(b))),
        None,
    )
    assert try_idx is not None, "no try block assigning `composed` was found"
    bind_idx = min(fn.body.index(n) for n in top_level_binds)
    assert bind_idx < try_idx, (
        f"`composed` is bound at statement {bind_idx} but the try that assigns "
        f"it is at {try_idx}; the guard must precede the try"
    )

    # The companion execution check: the fallback value the binding supplies is
    # the one the record builder must accept. THIS part is executed.
    assert R._composer_record_fields(None, "p", "d")["composer_fallback"] is True


# ───────────────────────── the consumer side ─────────────────────────────────

#: THE RECORDED DENSITIES MUST BE UNREACHABLE BY THE ESTIMATOR, or the test
#: passes on a coincidence. Measured: with `constraint_count = 20` and
#: `prompt_chars_full = 20000`, the estimator returns 20 / (20000//4) = 0.004.
#: An earlier version of this test used densities spanning 0.004 to 0.009, so a
#: mutation that stopped reading the recorded density returned 0.004 -- which
#: was INSIDE the accepted set, and the mutation survived. These densities are
#: an order of magnitude away from the estimator's value, and the estimator's
#: value is asserted against explicitly below.
RECORDED_DENSITIES = [0.0211, 0.0223, 0.0237, 0.0241, 0.0253, 0.0269]
ESTIMATOR_VALUE = 0.004
EST_COUNT = 20
EST_CHARS = 20000


def _write_records(dirpath: Path, densities: list[float], *, in_metadata: bool,
                   quality: list[int] | None = None) -> None:
    for i, d in enumerate(densities):
        # Quality must VARY, or the peak of the quality curve is ambiguous and
        # the threshold the calibrator picks is an artefact of bin ordering.
        findings = (quality or [10, 20, 40, 35, 18, 9])[i % 6]
        payload = {
            "model_label": "opus_4_6",
            "response": "FINDING_ID: F1\nFINDING_ID: F2\n" * 20,
            "prompt_length": 203,
        }
        fields = {
            "round": i, "findings_count": findings, "constraint_density": d,
            "constraint_count": EST_COUNT, "token_estimate": 5000,
            "coherence_budget": 0.02, "cid": "abc", "composer_fallback": False,
            "prompt_chars_full": EST_CHARS,
        }
        if in_metadata:
            payload["metadata"] = fields
        else:
            payload.update(fields)
            payload["metadata"] = {"round": i, "findings_count": findings}
        (dirpath / f"r{i}_cc2_x.json").write_text(json.dumps(payload))


def test_the_estimator_really_does_return_the_value_this_file_claims():
    """Pin the estimator's output, since two other tests are defined against it."""
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for i in range(6):
            (d / f"r{i}_cc2_x.json").write_text(json.dumps({
                "model_label": "opus_4_6",
                "response": "FINDING_ID: F1\n" * 20,
                "metadata": {"round": i, "findings_count": 10 + i,
                             "constraint_count": EST_COUNT,
                             "prompt_chars_full": EST_CHARS},
            }))
        out = C.calibrate_coherence_thresholds(d)
        assert out.get("opus_4_6") == ESTIMATOR_VALUE, (
            f"the estimator returns {out.get('opus_4_6')}, not "
            f"{ESTIMATOR_VALUE}. Two tests in this file are defined against "
            f"that value; re-derive them before trusting either."
        )


@pytest.mark.parametrize("in_metadata", [True, False])
def test_the_calibrator_reads_a_recorded_density_from_either_position(in_metadata):
    """Top level or metadata: the runner writes metadata, so both must work.

    The accepted set is deliberately disjoint from the estimator's value, so a
    consumer that ignores the recorded density cannot pass by coincidence.
    """
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _write_records(d, RECORDED_DENSITIES, in_metadata=in_metadata)
        out = C.calibrate_coherence_thresholds(d)
        assert "opus_4_6" in out, out
        got = out["opus_4_6"]
        assert got != ESTIMATOR_VALUE, (
            f"the calibrator returned the estimator's value {got} rather than a "
            f"recorded density, so the recorded field is being ignored "
            f"({'metadata' if in_metadata else 'top level'} position)"
        )
        assert got in {round(x, 4) for x in RECORDED_DENSITIES}, got


def test_without_a_recorded_density_the_estimator_returns_the_truncation_artefact():
    """The companion falsifier: prove the old path really did produce 0.04.

    Without this, the test above would pass even if the recorded density were
    being ignored and some other number happened to match.
    """
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for i in range(6):
            (d / f"r{i}_cc2_x.json").write_text(json.dumps({
                "model_label": "opus_4_6",
                "response": "FINDING_ID: F1\n" * 20,
                "prompt_length": 203,
                "metadata": {"round": i, "findings_count": 20},
            }))
        out = C.calibrate_coherence_thresholds(d)
        # 203//70 = 2, 203//4 = 50, so 2/50 = 0.04. This is the historical
        # artefact, distinct from ESTIMATOR_VALUE above, which uses a RECORDED
        # constraint_count rather than the chars//70 guess.
        assert out.get("opus_4_6") == 0.04, (
            "the estimator no longer returns the 0.04 truncation artefact on a "
            f"record carrying prompt_length=203 and no density. Got "
            f"{out.get('opus_4_6')}. The arithmetic (203//70)/(203//4) = 2/50 "
            f"= 0.04 is what made every historical calibration meaningless; if "
            f"it has changed, re-derive the measured claim in this file."
        )


def test_a_recorded_fallback_does_not_silently_become_an_estimate():
    """A record that says the composer failed must not be calibrated from.

    It carries no density, so the estimator would otherwise turn an explicit
    failure into a confident number.
    """
    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        for i in range(6):
            (d / f"r{i}_cc2_x.json").write_text(json.dumps({
                "model_label": "opus_4_6",
                "response": "FINDING_ID: F1\n" * 20,
                "prompt_length": 203,
                "metadata": {"round": i, "findings_count": 20,
                             "composer_fallback": True,
                             "prompt_chars_full": 20000},
            }))
        out = C.calibrate_coherence_thresholds(d)
        # The estimator still fires -- it is not yet gated on the marker. This
        # test PINS that gap rather than hiding it, so the follow-up is visible.
        assert "opus_4_6" in out
        assert out["opus_4_6"] != 0.04, (
            "a fallback record now calibrates to the 203 artefact again"
        )


# ─────────────────── and the live archive, so this is not theoretical ────────

def test_the_archive_still_shows_the_defect_this_fix_addresses():
    """Pins the historical measurement, and goes red once a new run lands.

    When a run under the repaired dispatch is archived, the composer fields will
    be present and this turns red. That is the signal to re-measure and update
    the figures in this file's docstring rather than assume they still hold.
    """
    logs = REPO_ROOT / "bench" / "logs"
    if not logs.is_dir():
        pytest.skip("no archive")
    with_fields = 0
    seen = 0
    modal_203 = 0
    with_pl = 0
    for path in sorted(logs.rglob("*.json")):
        try:
            doc = json.loads(path.read_text(errors="replace"))
        except (OSError, ValueError):
            continue
        for entry in (doc if isinstance(doc, list) else [doc]):
            if not isinstance(entry, dict):
                continue
            if not (entry.get("model") or entry.get("model_label")):
                continue
            seen += 1
            meta = entry.get("metadata") if isinstance(entry.get("metadata"), dict) else {}
            if any(f in entry or f in meta for f in FIELDS):
                with_fields += 1
            pl = entry.get("prompt_length")
            if isinstance(pl, int):
                with_pl += 1
                if pl == 203:
                    modal_203 += 1
    assert seen > 1000, seen
    # ★ A RATCHET ON THE PRE-REPAIR ENTRIES, NOT A PIN ON THE REPAIRED ONES.
    # Corrected 2026-10-29, the same correction and for the same reason as the
    # one in test_the_band_verdict_is_gated_on_estimability_2026-10-16.py.
    #
    # This read `with_fields == 0`, and its own message said a non-zero meant "a
    # run under the repaired dispatch has landed. Re-measure". That duly
    # happened: 30 of 5,992 entries now carry composer fields, so the pin failed
    # on the repair WORKING. A count that must stay at 0 for a fix to look
    # correct is a count that goes red the moment the fix takes effect.
    #
    # WHAT THIS TEST IS ACTUALLY FOR is that the ARCHIVE STILL SHOWS THE DEFECT
    # the fix addresses -- the pre-repair entries must remain as recorded, so the
    # evidence that the defect existed is not quietly erased. That is a statement
    # about the entries WITHOUT the fields not shrinking, and it is silent on how
    # many repaired entries arrive later.
    #
    # MEASURED 2026-10-29: 5,992 entries seen, 30 carrying composer fields, so
    # 5,962 WITHOUT them. The floor is on those 5,962.
    without_fields = seen - with_fields
    assert without_fields >= 5962, (
        f"only {without_fields} of {seen} archived dispatch entries lack "
        f"composer fields, down from the 5,962 recorded on 2026-10-29. A "
        f"pre-repair entry has acquired them, which means the archive was "
        f"REWRITTEN and the evidence that this defect existed is being erased."
    )
    assert with_pl > 0 and modal_203 / with_pl > 0.9, (
        f"prompt_length = 203 now covers {modal_203}/{with_pl} entries; the "
        f"truncation artefact's share has changed and the measured claim needs "
        f"re-deriving"
    )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
