#!/usr/bin/env python3
"""ONE DECLARATION MUST BE SUFFICIENT TO ADMIT A MODEL. Proven by REMOVAL.

HIS INSTRUCTION, 2026-11-02: researchers *"should be able to search for/add
models trivially from a search box in the UX ... They shouldn't need to think, or
concern themselves with the underlying mechanics of how this works in reality.
Which is what I mean by making the process trivial."*

WHY REMOVAL IS THE ONLY TEST THAT PROVES ANYTHING HERE. With Fable's hard-coded
entries in place the preflight passes whether or not the declaration works, so
asserting a pass would be VACUOUS -- the `boundary_band_sensitivity` shape, which
shipped as an unconditional constant and was vacuous in 41 of 41 archived reports
because its guard asserted on source text instead of calling anything. So the
hard-coded path is removed IN PROCESS, the preflight is shown to FAIL without
either path, and only then is the declaration the thing under test.

NOTHING ON DISK IS MUTATED, and the restoration is ASSERTED rather than hoped
for. `feedback_a_harness_must_restore_what_it_found_2026-11-01` records a
`git checkout --` that ate the subject it was measuring, so the final check
compares every table against a snapshot taken before anything moved.
"""
from __future__ import annotations

import copy
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench import model_admission as MA              # noqa: E402
from bench import runner_core as rc                  # noqa: E402
from bench.cdsfl_registry import composer as co      # noqa: E402

#: Fable's 4 hard-coded entries, by (table, key). These are what a researcher
#: would otherwise have to add by hand, and removing them is the experiment.
HARDCODED = [
    (co.COMPOSER_MODEL_MAP, "Fable"),
    (co.COMPOSER_MODEL_MAP, "fable_5_1"),
    (co.PHENOTYPE_TRANSFORMS, "fable_5_1"),
    (co.MODEL_COHERENCE_BUDGETS, "fable_5_1"),
    (rc.INITIAL_FINGERPRINTS, "Fable"),
    (rc.MODEL_SPECS, "Fable"),
]


def _post():
    """The live preflight, loaded by path because its filename carries a date."""
    p = REPO / "scripts" / "preflight_health_check_2026-10-06.py"
    spec = importlib.util.spec_from_file_location("post_live", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _registered(post, seat: str):
    status, detail, notes = (post.check_every_seat_is_fully_registered([seat])
                             + (None,))[:3]
    return status, " ".join([str(detail)] + list(notes or []))


@pytest.fixture
def stripped():
    """Remove Fable's hard-coded entries, yield, then put every one back.

    Snapshots the WHOLE table, not just the removed key, so a test that
    accidentally writes a neighbouring entry is caught too.
    """
    snapshot = [(t, copy.copy(t)) for t, _k in HARDCODED]
    removed = []
    for table, key in HARDCODED:
        if key in table:
            removed.append((table, key, table.pop(key)))
    try:
        yield removed
    finally:
        for table, original in snapshot:
            table.clear()
            table.update(original)


def test_the_declaration_exists_and_parses():
    decl = MA.declaration("Fable")
    assert decl, "Fable carries no [admission] block"
    assert not decl.get("_error"), decl.get("_error")
    for field in ("composer_key", "coherence_budget", "phenotype",
                  "fingerprint", "spec"):
        assert field in decl, f"the declaration omits {field}"


def test_WITHOUT_either_path_the_preflight_FAILS(stripped):
    """THE CONTROL. If this passes, every other assertion here is vacuous."""
    assert len(stripped) == len(HARDCODED), (
        f"only {len(stripped)} of {len(HARDCODED)} entries were present to "
        f"remove; the test is measuring a different state than it describes")
    post = _post()
    status, blob = _registered(post, "Fable-SIM")
    assert status == post.FAIL, (
        "with the hard-coded entries removed the preflight must FAIL. It did "
        "not, so something else is admitting Fable and this test proves "
        "nothing about the declaration.")
    assert "Fable" in blob


def test_THE_DECLARATION_ALONE_ADMITS_THE_MODEL(stripped):
    """The whole point: 1 file, and the preflight goes green."""
    post = _post()
    assert _registered(post, "Fable-SIM")[0] == post.FAIL, "control broken"

    rec = MA.admit_declared_models()
    assert not rec["errors"], rec["errors"]
    assert rec["applied"], (
        "the declaration filled NOTHING. A function that mutates module dicts "
        "and reports no change is indistinguishable from an inert one -- see "
        "the_coherence_recalibration_is_inert_three_ways_2026-10-15.")

    status, blob = _registered(_post(), "Fable-SIM")
    assert status == post.PASS, (
        f"the declaration did not admit the model. Still missing: {blob}")

    filled = {(r["table"], r["key"]) for r in rec["applied"]}
    assert len(filled) >= 4, f"only {len(filled)} table(s) filled: {filled}"


def test_the_declared_values_match_what_was_hardcoded(stripped):
    """A declaration that admits the model with DIFFERENT values is not a fix.

    This is the property that makes the removal safe rather than merely green:
    the declaration must reproduce the hand-added configuration, not substitute
    its own. The directive budget is checked explicitly because its silent 8000
    default is the measured defect this whole thread began with.
    """
    MA.admit_declared_models()
    assert co.COMPOSER_MODEL_MAP.get("Fable") == "fable_5_1"
    assert co.MODEL_COHERENCE_BUDGETS.get("fable_5_1") == pytest.approx(0.020)
    pt = co.PHENOTYPE_TRANSFORMS.get("fable_5_1")
    assert pt is not None and pt.max_directive_chars == 12000, (
        "the declared work bound must be 12000, its sibling's value. The "
        "silent dataclass default is 8000, which is the third-less-directive "
        "defect measured on 2026-11-02.")
    assert pt.spec_chars is None, (
        "spec_chars must stay unset: his ruling of 2026-10-14 is that the "
        "SPECIFICATION is not work and is delivered whole")
    fp = rc.INITIAL_FINGERPRINTS.get("Fable")
    assert fp is not None and fp.A == pytest.approx(0.85)


def test_a_hardcoded_entry_always_WINS_so_the_change_is_additive():
    """GAPS ONLY. With everything present, admission must change nothing.

    This is what keeps the module from altering the configuration of the 6
    seats that already run, which is the strict reading of additive-standard.
    """
    before = {id(t): copy.copy(t) for t, _k in HARDCODED}
    rec = MA.admit_declared_models()
    assert rec["applied"] == [], (
        f"admission overwrote a hard-coded entry: {rec['applied']}")
    assert rec["skipped"], "it should have reported what it left alone"
    for table, _k in HARDCODED:
        assert table == before[id(table)], "a table changed under gaps-only"


def test_the_fixture_restores_every_table():
    """The harness must restore what it found. Asserted, not assumed."""
    snap = {id(t): copy.copy(t) for t, _k in HARDCODED}
    gen = stripped.__wrapped__()
    next(gen)
    for table, key in HARDCODED:
        assert key not in table, f"{key} should be removed inside the fixture"
    with pytest.raises(StopIteration):
        next(gen)
    for table, _k in HARDCODED:
        assert table == snap[id(table)], (
            "the fixture did not restore a table it emptied")


def test_a_malformed_declaration_is_reported_not_swallowed(tmp_path, monkeypatch):
    """An unreadable declaration must say why. A swallowed exception written
    into the output is a failure that looks like data --
    feedback_a_swallowed_exception_is_not_a_record_2026-11-02."""
    monkeypatch.setattr(MA, "MODELS_DIR", tmp_path)
    (tmp_path / "Broken.toml").write_text("[admission\nnot = toml")
    d = MA.declaration("Broken")
    assert d.get("_error"), "a malformed declaration must report its error"
    rec = MA.admit_declared_models(dry_run=True)
    assert rec["errors"], "and admission must surface it, not skip silently"
