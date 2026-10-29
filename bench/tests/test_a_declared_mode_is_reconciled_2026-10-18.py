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

WHY 4 OF 5 MODES WERE UNSOUND WHEN MEASURED ON 2026-10-18, AND WHY 0 ARE TODAY.
`*_is_gating` is written as `bool(getattr(cfg, <flag>, False))`, a copy of the
switch under a name that reads like a statement about behaviour.
`severity_admissibility` is stamped into every report regardless. No sk artefact
existed. And `gamma_gate_series`, the field whose comment says it "says which one
decided", is a hardcoded string literal, so when `location_keyed_convergence`
substitutes the gate's input it still names the original series.

3 were repaired the same day under entry B32 by recording each mode's EFFECT
instead of restating its flag. The 4th, `hierarchical_novelty_convergence`, was
worse than a circular artefact -- it was a mode with NO CONSUMER AT ALL -- and it
was WIRED on 2026-10-29 on his ruling of 2026-10-19, *"Verdict option 1"*. The
unsound set is therefore empty, which `test_the_unsound_set_is_named_and_not_silently_empty`
now asserts, and the comment there records why an empty set is a stronger claim
than the list it replaced rather than a weaker one.
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
    ABSENT, AGREE, CIRCULAR, INERT, SOUND, UNDECIDABLE, UNGATED,
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


def test_a_circular_or_ungated_artefact_is_never_treated_as_evidence():
    """Pinned on CONSTRUCTED reports, so it cannot go vacuous (entry B32).

    ★ WHY NOT A LOOP OVER MODES. It used to iterate the modes annotated CIRCULAR
    and UNGATED. Under B32 those annotations were upgraded to SOUND -- the runner
    now records each mode's EFFECT -- and the loop would then have iterated an
    EMPTY set and passed while testing nothing. A guard that silently empties is
    the defect class this project keeps finding, so the contract is now exercised
    on reports this test owns.

    The two refusals being pinned:
      * a key that is a COPY OF THE FLAG proves nothing, so it must not produce
        AGREE -- comparing the flag with itself can never disagree;
      * an artefact written UNCONDITIONALLY appears whether the mode is on or
        not, and reading it produced a disagreement on free_run1 that did not
        exist.
    """
    # The legacy circular key, now ignored: a declared True with a copy of the
    # flag beside it and NO effect record must be undecidable, not agreement.
    circular = {"_declared_config": {"location_keyed_convergence": True},
                "location_crit_series_is_gating": True}
    got = [f for f in reconcile(circular) if f.mode == "location_keyed_convergence"][0]
    assert got.verdict == UNDECIDABLE, (
        f"a copy of the flag was read as evidence and gave {got.verdict}; the "
        f"detector must require the effect record, not the restated switch")

    # The legacy ungated key, now ignored for the same reason.
    ungated = {"_declared_config": {"severity_spec_enabled": False},
               "severity_admissibility": {"severity_provenance": "simulated"}}
    got = [f for f in reconcile(ungated) if f.mode == "severity_spec_enabled"][0]
    assert got.verdict == UNDECIDABLE, (
        f"an unconditionally-written artefact was read as evidence and gave "
        f"{got.verdict}; on free_run1 that mistake invented a disagreement")


def test_an_inert_mode_has_no_consumer_in_the_runner():
    """INERT means the flag is read ONLY where a copy of it is published.

    Measured 2026-10-18 on the syntax tree: `hierarchical_novelty_convergence`
    is read exactly once in the whole runner, at the line writing
    `hierarchical_crit_series_is_gating`, and the series
    `hierarchical_novelty_series` computes reaches one report key and nothing
    else. The mode cannot operate however it is set, while the report publishes
    a field named `..._is_gating` that a reader would take as proof it gates.

    If the mode is ever WIRED, this test fails and the annotation must move off
    INERT -- which is the point: an understated annotation is as wrong as an
    overstated one.
    """
    tree = _tree()
    for mode in MODES:
        if mode.soundness != INERT:
            continue
        reads = []
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id == "getattr" and len(node.args) >= 2
                    and isinstance(node.args[1], ast.Constant)
                    and node.args[1].value == mode.name):
                reads.append(node.lineno)
            elif isinstance(node, ast.Attribute) and node.attr == mode.name:
                reads.append(node.lineno)
        assert reads, f"{mode.name} is annotated INERT but is not read at all"
        # Every read must sit on a write of its own circular artefact.
        publications = {a.lineno for a in _subscript_assigns(tree, mode.artefact)}
        stray = []
        for ln in sorted(set(reads)):
            # a read belongs to a publication when it is within that statement
            if not any(abs(ln - p) <= 2 for p in publications):
                stray.append(ln)
        assert stray == [], (
            f"{mode.name} is annotated INERT, meaning its only read publishes a "
            f"copy of itself, but it is also read at line(s) {stray}. If it has "
            f"been WIRED, move the annotation off INERT and give it a detector; "
            f"if those reads do nothing, the mode should be retired")


def test_a_sound_mode_reads_an_effect_record_not_a_restated_flag():
    """SOUND requires an artefact the runner WRITES and that is not the flag."""
    tree = _tree()
    for mode in MODES:
        if mode.soundness != SOUND:
            continue
        assert mode.artefact, f"{mode.name} is SOUND with no artefact"
        assigns = _subscript_assigns(tree, mode.artefact)
        if not assigns:
            # `_declared_argv` is written by the report assembler, not as a
            # `result[...]` subscript; underscore-prefixed keys are allowed.
            assert mode.artefact.startswith("_"), (
                f"{mode.name} is SOUND but nothing writes {mode.artefact!r}")
            continue
        circularity = [a.lineno for a in assigns if _mentions_flag(a.value, mode.name)]
        assert circularity == [], (
            f"{mode.name} is annotated SOUND but its artefact is assigned FROM "
            f"its own flag at line(s) {circularity}, which is the CIRCULAR "
            f"defect wearing a SOUND label")


def _mentions_flag(node, flag: str) -> bool:
    for s in ast.walk(node):
        if isinstance(s, ast.Attribute) and s.attr == flag:
            return True
        if (isinstance(s, ast.Call) and isinstance(s.func, ast.Name)
                and s.func.id == "getattr" and len(s.args) >= 2
                and isinstance(s.args[1], ast.Constant) and s.args[1].value == flag):
            return True
    return False


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

#: Disagreements the archive REALLY CONTAINS, each with the reason it is not a
#: live defect. Keyed on the exact run directory, which makes the exemption
#: SELF-BOUNDING: a future run has a different directory name, so it cannot
#: inherit an exemption and a recurrence FAILS.
#:
#: WHY THERE IS NOW 1. Wiring `hierarchical_novelty_convergence` on 2026-10-29
#: (task B33, his ruling of 2026-10-19) replaced a CIRCULAR detector -- it read
#: `hierarchical_crit_series_is_gating`, which is `bool(getattr(cfg, <flag>))`,
#: the switch compared with itself -- with one that reads the effect record. The
#: new detector immediately found a TRUE historical disagreement the old one
#: could not express. That is the detector working, not a regression.
#:
#: THE SET IS CLOSED AT 1, MEASURED. 5 archived reports carry a declared config
#: and all 5 declare this mode TRUE, but 4 predate the `mode_effects` slot
#: itself (added 2026-10-18 under entry B32), so their detector returns None --
#: UNDECIDABLE, which is not a disagreement. Only this run falls in the window
#: where the slot existed and the wiring did not: after 2026-10-18 and before
#: 2026-10-29. 1 of 5 = 0.200000, Wilson [0.036224, 0.624465],
#: Clopper-Pearson [0.005051, 0.716418].
#:
#: THE REPORT IS NOT EDITED. His ruling that history is not rewritten applies:
#: the run genuinely declared a mode that genuinely did not operate, and that is
#: what the archive should go on saying.
KNOWN_ARCHIVE_DISAGREEMENTS = {
    "free_run3_no_spec_20261028T235529Z_20261028T235530Z":
        "hierarchical_novelty_convergence DECLARED_NOT_OPERATING",
}


def test_no_archived_report_yields_a_disagreement():
    """Every comparison that CAN be made agrees, except those recorded above
    with their reason. A failure here is either a real defect in a run or a
    detector of mine that is wrong; both need looking at."""
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
    unexplained = [x for x in found
                   if KNOWN_ARCHIVE_DISAGREEMENTS.get(x.split(":")[0].strip())
                   != x.split(":", 1)[1].strip()]
    assert unexplained == [], (
        f"unexplained mode disagreements in the archive: {unexplained}")
    # ANTI-ROT: an exemption for a run that no longer disagrees is an exemption
    # that has outlived its cause, and leaving it would silently widen the test.
    seen = {x.split(":")[0].strip() for x in found}
    idle = sorted(set(KNOWN_ARCHIVE_DISAGREEMENTS) - seen)
    assert idle == [], (
        f"{idle} are recorded as known disagreements and no longer disagree; "
        f"remove them rather than leaving the exemption standing")


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
        # ★ THE LAST ONE CAME OFF THIS LIST ON 2026-10-29, SO IT IS NOW EMPTY --
        # AND THIS TEST'S OWN INSTRUCTION IS WHAT SAID TO DO THAT. Its message
        # reads "If an effect record was wired, this is the test to update",
        # and `hierarchical_novelty_convergence` was wired on his ruling of
        # 2026-10-19, *"Verdict option 1"*. 3 came off on 2026-10-18 under entry
        # B32; this was the 4th and last.
        #
        # AN EMPTY SET IS NOT A SILENT EMPTYING, AND THAT DISTINCTION IS HELD BY
        # OTHER TESTS RATHER THAN ASSERTED HERE. The hazard this test was built
        # for is someone clearing the classification instead of the defect. 2
        # independent checks make that impossible:
        # `test_each_soundness_annotation_matches_the_runner_source` verifies
        # every mode's annotation AGAINST THE RUNNER'S SYNTAX TREE, so a mode
        # cannot be called SOUND without an effect record the runner really
        # writes; and `test_the_classification_covers_every_boolean_config_field`
        # stops a mode being dropped from `MODES` to escape scrutiny. So this
        # assertion is now a statement that every classified mode is witnessable,
        # which is a stronger claim than the list it replaces, not a weaker one.
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


# ── The effect records, contract by contract (entry B32) ─────────────────────
#
# ★ THESE EXIST BECAUSE 2 MUTATIONS ESCAPED. Making `_location_operating` return
# True unconditionally, and making `_sk_operating_from_effects` treat an
# unreached decision as operating, both left the suite green. A detector whose
# None/False handling nothing pins is a detector that can quietly start agreeing
# with everything, which is the failure these records were built to end.

def _finding(mode: str, rec) -> Finding:
    report = {"_declared_config": {mode: True}, "mode_effects": {mode: rec}}
    return [f for f in reconcile(report) if f.mode == mode][0]


def test_a_location_mode_asked_for_but_never_substituted_is_not_operating():
    """0 substitutions means the series was telemetry and never fed the gate."""
    got = _finding("location_keyed_convergence",
                   {"substituted": [], "fell_back": []})
    assert got.operating is False
    assert got.verdict == "DECLARED_NOT_OPERATING", (
        "a mode asked for that substituted in NO round did not operate, however "
        "quietly it failed to")


def test_a_location_mode_that_fell_back_every_round_is_not_operating():
    """The silent downgrade his ruling names, now loud."""
    got = _finding("location_keyed_convergence",
                   {"substituted": [], "fell_back": [2, 3, 4]})
    assert got.operating is False
    assert got.verdict == "DECLARED_NOT_OPERATING"


def test_a_location_mode_that_substituted_is_operating():
    got = _finding("location_keyed_convergence",
                   {"substituted": [1, 2], "fell_back": []})
    assert got.operating is True and got.verdict == AGREE


def test_a_missing_location_record_is_undecidable_not_false():
    """Every archived report predates the record; absence must not read as off."""
    report = {"_declared_config": {"location_keyed_convergence": True}}
    got = [f for f in reconcile(report)
           if f.mode == "location_keyed_convergence"][0]
    assert got.operating is None and got.verdict == UNDECIDABLE


def test_the_sk_decision_distinguishes_unreached_from_not_forced_off():
    """None means the branch was never reached; False means the mode ran."""
    assert _finding("sk_score_prose_listings",
                    {"forced_off": None}).verdict == UNDECIDABLE
    off = _finding("sk_score_prose_listings", {"forced_off": True})
    assert off.operating is False and off.verdict == "DECLARED_NOT_OPERATING", (
        "forced off means the target overrode the declared mode")
    on = _finding("sk_score_prose_listings", {"forced_off": False})
    assert on.operating is True and on.verdict == AGREE


def test_the_severity_effect_needs_a_refuted_finding_to_witness_it():
    """With 0 refuted findings nothing could be annihilated."""
    assert _finding("severity_spec_enabled",
                    {"refuted_findings": 0, "refuted_scored_zero": 0}
                    ).verdict == UNDECIDABLE, (
        "legs 1 and 2 together carried 0 refuted of 41, so this is the common "
        "case and must not read as the specification failing")
    good = _finding("severity_spec_enabled",
                    {"refuted_findings": 2, "refuted_scored_zero": 2})
    assert good.operating is True and good.verdict == AGREE
    bad = _finding("severity_spec_enabled",
                   {"refuted_findings": 2, "refuted_scored_zero": 0})
    assert bad.operating is False and bad.verdict == "DECLARED_NOT_OPERATING", (
        "refuted findings that were NOT annihilated means the specification's "
        "key property did not fire")


def test_the_severity_effect_must_be_computed_by_calling_not_by_reading():
    """★ The stored field is the ASSERTED number and the spec does not mutate it.

    Executed against leg 3's own catalogue rather than asserted: its 2 refuted
    findings both STORE severity 0.5, and `effective_severity` returns 0.0 for
    both with the specification on. A runner that counted zeros by reading
    `entry["severity"]` would have recorded 0 of 2 annihilated and reported a
    working specification as broken.
    """
    import json
    cat = (REPO / "bench" / "logs" / "leg3_final_shakedown_20261015T220118Z"
           / "leg3_final_shakedown_finding_catalogue.jsonl")
    if not cat.exists():
        pytest.skip("leg 3 catalogue absent; this check needs its real findings")
    rows = [json.loads(l) for l in cat.read_text().splitlines() if l.strip()]
    refuted = [r for r in rows
               if str(r.get("falsifier_verdict") or "").strip().upper() == "REFUTED"]
    assert refuted, "leg 3 carried refuted findings; if none are found, re-measure"

    import bench.reference_runner_v3 as R
    saved = R._SEVERITY_SPEC.get("on")
    try:
        R._SEVERITY_SPEC["on"] = True
        by_calling = sum(1 for r in refuted if R.effective_severity(r) == 0.0)
        by_reading = sum(1 for r in refuted
                         if float(r.get("severity") or 0.0) == 0.0)
    finally:
        R._SEVERITY_SPEC["on"] = saved
    assert by_calling == len(refuted), (
        f"with the specification on, every refuted finding must be annihilated; "
        f"{by_calling} of {len(refuted)} were")
    assert by_reading == 0, (
        "the stored severities are NOT zero -- that is the whole point. If they "
        "are, the specification has started mutating the asserted number and the "
        "runner's effect record should be re-derived")

    # And the runner must CALL it IN THE EFFECT COMPUTATION, not merely
    # somewhere in the file. A first version of this check only asserted that
    # `effective_severity` is called at all, and a mutation that swapped the
    # effect computation to read `entry["severity"]` left it green -- the gate
    # calls the scorer elsewhere, so the call still existed. The check now finds
    # the statement that assigns `refuted_scored_zero` and requires the call
    # inside THAT enclosing block, which is the structural form of "here".
    tree = _tree()

    def _enclosing_blocks(target):
        parents, found = {}, []
        for node in ast.walk(tree):
            for child in ast.iter_child_nodes(node):
                parents[child] = node
        for node in ast.walk(tree):
            if (isinstance(node, ast.Assign)
                    and any(isinstance(x, ast.Subscript)
                            and isinstance(x.slice, ast.Constant)
                            and x.slice.value == target for x in node.targets)):
                cur, chain = node, []
                while cur in parents:
                    cur = parents[cur]
                    chain.append(cur)
                    if isinstance(cur, (ast.Try, ast.FunctionDef)):
                        break
                found.append(chain[-1] if chain else node)
        return found

    blocks = _enclosing_blocks("refuted_scored_zero")
    assert blocks, (
        "nothing assigns `refuted_scored_zero`, so the severity effect is not "
        "recorded at all")
    for blk in blocks:
        calls = [n for n in ast.walk(blk)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                 and n.func.id == "effective_severity"]
        assert calls, (
            "the block that records `refuted_scored_zero` does not call "
            "`effective_severity`, so it is counting the STORED asserted number "
            "-- which on leg 3 would have reported a working specification as "
            "broken, 0 of 2 annihilated instead of 2 of 2")


def test_an_empty_effect_record_is_undecidable_not_off():
    """A record present but carrying neither key establishes nothing.

    ★ A mutation escaped here. Deleting the `sub is None and fell is None` guard
    left `bool(None)` returning False, so an effect record that exists but is
    empty would have read as "the mode did not operate" -- a disagreement
    manufactured out of a record that says nothing. The absent-record case was
    already covered; the present-but-empty one was not.
    """
    got = _finding("location_keyed_convergence", {})
    assert got.operating is None, (
        "an effect record with neither `substituted` nor `fell_back` says "
        "nothing about the mode and must not be read as False")
    assert got.verdict == UNDECIDABLE
