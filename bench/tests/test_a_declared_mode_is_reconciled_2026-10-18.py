#!/usr/bin/env python3
"""A declared mode must be reconciled against what the run did -- entry B28.

HIS RULING, 2026-10-07 and 2026-10-11: "state should be detected rather than
declared ... forgetting the variable silently downgraded the check."

WHAT THIS FILE DECIDES, so it is not another inert addition. It checks each mode's
SOUNDNESS ANNOTATION against the runner's own source, structurally:

  * a mode annotated SOUND must read an artefact the runner GATES on that flag;
  * a mode annotated CIRCULAR must really be circular -- its artefact assigned
    directly from the flag;
  * a mode annotated UNGATED must really be ungated;
  * a mode annotated ABSENT must really have no artefact.

So the annotations cannot go stale IN EITHER DIRECTION: if someone wires a real
effect record for one of the 4 unsound modes, this file fails until the annotation
is upgraded, and if someone adds a detector reading a copy of a flag, it fails
too. That is the whole mechanism -- the project's recurring defect is an addition
that decides nothing, and an annotation nothing checks would be exactly that.

WHY 4 OF 5 MODES ARE UNSOUND, measured 2026-10-18. `*_is_gating` is written as
`bool(getattr(cfg, <flag>, False))`, a copy of the switch under a name that reads
like a statement about behaviour. `severity_admissibility` is stamped into every
report regardless. No sk artefact exists. And `gamma_gate_series`, the field whose
comment says it "says which one decided", is a hardcoded string literal, so when
`location_keyed_convergence` substitutes the gate's input it still names the
original series.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench.runner_mode_detection import (  # noqa: E402
    ABSENT, AGREE, CIRCULAR, SOUND, UNDECIDABLE, UNGATED,
    MODES, Finding, as_report_field, disagreements, reconcile, summarise,
    unsound_modes,
)

RUNNER = REPO / "bench" / "reference_runner_v3.py"
CLASSIFIER = REPO / "scripts" / "which_runner_modes_are_declared_2026-10-18.py"


# ── The syntax-tree facts the annotations claim ──────────────────────────────

def _tree():
    return ast.parse(RUNNER.read_text(errors="ignore"))


def _parents(tree):
    out = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            out[child] = node
    return out


def _mentions(node, flag: str) -> bool:
    for s in ast.walk(node):
        if isinstance(s, ast.Attribute) and s.attr == flag:
            return True
        if (isinstance(s, ast.Call) and isinstance(s.func, ast.Name)
                and s.func.id == "getattr" and len(s.args) >= 2
                and isinstance(s.args[1], ast.Constant) and s.args[1].value == flag):
            return True
        if isinstance(s, ast.Constant) and s.value == flag:
            return True
    return False


def _subscript_assigns(tree, key: str) -> list[ast.Assign]:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if (isinstance(tgt, ast.Subscript)
                        and isinstance(tgt.slice, ast.Constant)
                        and tgt.slice.value == key):
                    out.append(node)
    return out


def _is_gated(tree, parents, node, flag: str) -> bool:
    cur = node
    while cur in parents:
        cur = parents[cur]
        if isinstance(cur, (ast.If, ast.IfExp)) and _mentions(cur.test, flag):
            return True
        if isinstance(cur, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
            return False
    return False


@pytest.mark.parametrize("mode", MODES, ids=lambda m: m.name)
def test_each_soundness_annotation_matches_the_runner_source(mode):
    tree = _tree()
    parents = _parents(tree)

    if mode.soundness == ABSENT:
        assert mode.artefact is None, (
            f"{mode.name} is annotated ABSENT but names artefact {mode.artefact!r}")
        return

    assert mode.artefact, f"{mode.name} is annotated {mode.soundness} with no artefact"
    assigns = _subscript_assigns(tree, mode.artefact)

    if mode.soundness == CIRCULAR:
        assert assigns, (
            f"{mode.name} is annotated CIRCULAR but the runner no longer writes "
            f"{mode.artefact!r} -- re-measure and update the annotation")
        assert all(_mentions(a.value, mode.name) for a in assigns), (
            f"{mode.name} is annotated CIRCULAR, meaning {mode.artefact!r} is "
            f"assigned FROM the flag, but at least one write does not read the "
            f"flag. If a real effect record has been wired, upgrade the "
            f"annotation to SOUND -- do not leave it understated")
    elif mode.soundness == UNGATED:
        assert assigns, (
            f"{mode.name} is annotated UNGATED but the runner no longer writes "
            f"{mode.artefact!r}")
        assert not any(_is_gated(tree, parents, a, mode.name) for a in assigns), (
            f"{mode.name} is annotated UNGATED, but {mode.artefact!r} is now "
            f"written inside a conditional on the flag. That is an EFFECT record: "
            f"upgrade the annotation to SOUND and give it a real detector")
    elif mode.soundness == SOUND:
        assert assigns or mode.artefact.startswith("_"), (
            f"{mode.name} is annotated SOUND but nothing writes {mode.artefact!r}")


def test_a_circular_artefact_is_never_treated_as_evidence():
    """A copy of the flag must yield UNDECIDABLE, never AGREE."""
    for mode in MODES:
        if mode.soundness != CIRCULAR:
            continue
        report = {"_declared_config": {mode.name: True}, mode.artefact: True}
        got = [f for f in reconcile(report) if f.mode == mode.name][0]
        assert got.verdict == UNDECIDABLE, (
            f"{mode.name} read a copy of its own flag as evidence and returned "
            f"{got.verdict}; a comparison of the flag with itself can never "
            f"disagree and must not be reported as agreement")


def test_an_ungated_artefact_is_never_treated_as_evidence():
    for mode in MODES:
        if mode.soundness != UNGATED:
            continue
        report = {"_declared_config": {mode.name: False}, mode.artefact: {"x": 1}}
        got = [f for f in reconcile(report) if f.mode == mode.name][0]
        assert got.verdict == UNDECIDABLE, (
            f"{mode.name} read an unconditionally-written artefact as evidence and "
            f"returned {got.verdict}. On free_run1 that exact mistake produced a "
            f"disagreement that did not exist")


# ── The honest-unknown contract ──────────────────────────────────────────────

def test_a_withheld_declaration_is_undecidable_not_false():
    """The redactor's placeholder must not read as a declared False.

    Measured 2026-10-18: 4 of 4 reports carrying a declared config withhold
    `location_keyed_convergence`, because its name contains "key". A plain
    bool() over that string is TRUE, and `bool("")`-style coercion elsewhere
    would make it False; either way it would invent a comparison.
    """
    report = {"_declared_config":
              {"models_were_declared": "<withheld: name matches a credential pattern>"},
              "_declared_argv": ["--models", "A", "B"]}
    got = [f for f in reconcile(report) if f.mode == "models_were_declared"][0]
    assert got.declared is None
    assert got.verdict == UNDECIDABLE
    assert "withheld" in got.note


def test_a_mode_that_could_not_be_checked_still_appears_in_the_record():
    """An omission reads as agreement, so every mode must be listed."""
    fields = as_report_field(reconcile({}))
    assert len(fields["modes"]) == len(MODES)
    assert set(fields["undecidable"]) == {m.name for m in MODES}


def test_the_declared_model_set_is_read_from_the_launch_not_the_model_list():
    """A non-empty model list is produced by DEFAULTS too.

    Measured on leg 3: 6 models recorded, argv carrying no `--models`, and
    `models_were_declared` correctly False. A detector reading the list called
    that a disagreement.
    """
    defaults = {"_declared_config": {"models_were_declared": False},
                "models": ["A", "B", "C"], "_declared_argv": ["--target", "t"]}
    got = [f for f in reconcile(defaults) if f.mode == "models_were_declared"][0]
    assert got.operating is False and got.verdict == AGREE

    declared = {"_declared_config": {"models_were_declared": True},
                "models": ["A"], "_declared_argv": ["--models", "A"]}
    got = [f for f in reconcile(declared) if f.mode == "models_were_declared"][0]
    assert got.operating is True and got.verdict == AGREE

    from_file = {"_declared_config": {"models_were_declared": True},
                 "_declared_argv": ["--config", "c.json"]}
    got = [f for f in reconcile(from_file) if f.mode == "models_were_declared"][0]
    assert got.verdict == UNDECIDABLE, (
        "a config file may declare models with no trace in argv, so this must be "
        "undecidable rather than a disagreement")


def test_a_real_disagreement_is_still_detected_and_named():
    """The mechanism must not be inert: a genuine mismatch must surface."""
    report = {"_declared_config": {"models_were_declared": True},
              "_declared_argv": ["--target", "t"]}
    fs = reconcile(report)
    bad = disagreements(fs)
    assert [f.mode for f in bad] == ["models_were_declared"]
    assert bad[0].verdict == "DECLARED_NOT_OPERATING"
    assert any("MODE DISAGREEMENT" in line for line in summarise(fs))


# ── Against the archive, and the classification behind it ────────────────────

def test_no_archived_report_yields_a_disagreement():
    """Every comparison that CAN be made agrees. A failure here is either a real
    defect in a run or a detector of mine that is wrong; both need looking at."""
    found = []
    for p in sorted((REPO / "bench" / "logs").rglob("*_report.json")):
        if "sandbox_harvest" in str(p):
            continue
        try:
            d = json.loads(p.read_text(errors="ignore"))
        except Exception:                                          # noqa: BLE001
            continue
        if isinstance(d, dict):
            for f in disagreements(reconcile(d)):
                found.append(f"{p.parent.name}: {f.mode} {f.verdict}")
    assert found == [], f"unexplained mode disagreements in the archive: {found}"


def test_the_classification_covers_every_boolean_config_field():
    """A flag with no judgement means the reasoned list has gone stale."""
    spec = importlib.util.spec_from_file_location("b28_classifier", CLASSIFIER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    src = RUNNER.read_text(errors="ignore")
    names = [n for n, _ in mod.bool_fields(src)]
    assert names, "no boolean config fields found -- the config shape has moved"
    unjudged = [n for n in names if n not in mod.MODE_JUDGEMENTS]
    stale = [n for n in mod.MODE_JUDGEMENTS if n not in names]
    assert unjudged == [], f"boolean config fields with no MODE/CHOICE judgement: {unjudged}"
    assert stale == [], f"judgements naming fields that no longer exist: {stale}"
    modes = {n for n in names if mod.MODE_JUDGEMENTS[n][0] == "MODE"}
    assert modes == {m.name for m in MODES}, (
        "the classifier's MODE set and the detector's MODES disagree, so one of "
        "them has been changed without the other")


def test_the_unsound_set_is_named_and_not_silently_empty():
    """B28's substance, callable rather than only written down."""
    unsound = {m.name: m.soundness for m in unsound_modes()}
    assert unsound == {
        "location_keyed_convergence": CIRCULAR,
        "hierarchical_novelty_convergence": CIRCULAR,
        "severity_spec_enabled": UNGATED,
        "sk_score_prose_listings": ABSENT,
    }, (
        "the set of modes whose effect no report can witness has changed. If an "
        "effect record was wired, this is the test to update -- and the "
        "corresponding detector must stop returning None"
    )


def test_the_reconciliation_reaches_the_report():
    """An addition nothing calls is not additive.

    Structural rather than textual: the runner must CALL reconcile and must
    ASSIGN the result into the report dict. Running the whole runner to prove it
    is not available in a test, so this reads the syntax tree -- the shape the
    interpreter executes -- rather than searching the source for a name.
    """
    tree = _tree()
    calls = [n for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
             and n.func.attr == "reconcile"]
    assert calls, (
        "the runner never calls reconcile, so the mode comparison runs nowhere "
        "and the only thing exercising it would be its own tests")
    writes = _subscript_assigns(tree, "mode_reconciliation")
    assert writes, (
        "nothing assigns `mode_reconciliation` into the report, so a disagreement "
        "would be computed and then discarded")
    # ★ THE ERROR HANDLER IS NOT THE WIRING, and a mutation proved this test
    # accepted it as such: deleting the real assignment left
    # `result["mode_reconciliation"] = {"error": ...}` in the except branch and
    # this check still passed. The write must carry the RESULT.
    real = [w for w in writes
            if any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                   and c.func.attr == "as_report_field" for c in ast.walk(w.value))]
    assert real, (
        "the only writes of `mode_reconciliation` are error handlers, so on a "
        "clean run the report would carry no comparison at all")
    logged = [n for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
              and n.func.attr == "summarise"]
    assert logged, (
        "the reasons are never summarised into the run log, so a disagreement "
        "would reach the report but not the operator watching the run")
