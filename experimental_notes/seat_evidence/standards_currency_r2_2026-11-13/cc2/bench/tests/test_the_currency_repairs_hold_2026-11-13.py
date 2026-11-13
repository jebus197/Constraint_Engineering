# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'standards_currency_r2_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 8236ad071ef9c90d3b01ee67f936e9d770d5db7d2cfc4f8436dd91f2f31206a9
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The joint-round currency repairs, EXECUTED rather than described.

WHAT THESE GUARD, and why each exists rather than reads well.

R1  THE FIGURE LEDGER. `test_the_standards_currency_producer_holds_2026-11-13`
    re-reads the DISPATCH BRIEF at test time and required every figure the brief
    declares to still be printed. The brief is history and cannot be re-issued,
    so the contract had 3 failure modes, all 3 demonstrated by execution on
    2026-11-13 against the brief on disk:
      1. it went RED when `composed_covers` was WITHDRAWN for being a count
         rather than a measurement -- and `the_standards_currency_mutations`
         REFUSES to run on a red baseline, so 0 of its 5 mutations were
         exercised. A guard that goes red on a correction pays the next seat to
         keep the refuted figure;
      2. it passed SILENTLY when `share_version_bearing` moved 0.253054 ->
         0.282700, because it matched only the text left of `=`;
      3. it would have reported `archive_epochs_at_T30 = 4` as HOLDING, because
         the refuted figure's declared string still appears VERBATIM inside its
         own refutation.
    The repair is the pin-and-supersession pattern applied to the brief's own
    figures: status is DECLARED where the figure is produced, and the guard
    reads the declaration instead of inferring status from stdout.

R2  PER-REPLY IDENTITY PROVENANCE. The panel's own tool-log sink recorded
    `"model": "opus"` -- the alias ASKED FOR. The resolved id was already in the
    same bytes: `--output-format stream-json` is in force whenever a sink is
    set, and its terminal `result` record carries `modelUsage`. Reading it there
    closes the TOCTOU window a boot-time probe leaves open, because the id comes
    from the SAME reply rather than from an earlier one.

R3  THE RATCHET. A bound of the shape max(FLOOR, HEADROOM * max(last N)) binds
    on the RATIO of consecutive entries and never on their SIZE, so growth at
    any ratio <= HEADROOM is admitted without limit.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
PRODUCER = REPO / "scripts" / "standards_currency_and_model_staleness_2026-11-13.py"
RATCHET = REPO / "scripts" / "does_a_max_of_last_n_bound_ratchet_2026-11-13.py"
ORCH = REPO / "bench" / "experiment_11_orchestrator.py"

#: A REAL envelope captured on this machine on 2026-11-13 by
#: `claude --model opus -p "say ok" --output-format json`, trimmed to the fields
#: under test. Typed fixtures that nothing ever observed are how a parser comes
#: to pass against a format the transport does not emit.
REAL_ENVELOPE = json.dumps({
    "is_error": False, "num_turns": 15, "type": "result",
    "modelUsage": {"claude-opus-5": {
        "inputTokens": 28, "outputTokens": 2907,
        "canonicalModel": "claude-opus-5", "provider": "firstParty"}},
})


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def prod():
    return _load(PRODUCER, "cdsfl_currency_producer")


@pytest.fixture(scope="module")
def ratchet():
    return _load(RATCHET, "cdsfl_ratchet")


@pytest.fixture(scope="module")
def orch():
    sys.path.insert(0, str(REPO / "bench"))
    import experiment_11_orchestrator as m
    return m


# ----------------------------------------------------------------- R1 ledger

def test_r1_the_producer_declares_a_figure_ledger(prod):
    """Status is DECLARED, never inferred from whether a label still prints."""
    ledger = getattr(prod, "FIGURE_LEDGER", None)
    assert isinstance(ledger, dict) and ledger, (
        "no FIGURE_LEDGER. Without it a WITHDRAWN figure is indistinguishable "
        "from one that silently stopped printing.")
    for label, entry in ledger.items():
        assert len(entry) == 4, f"{label}: expected (status, was, now, why)"
        status, was, now, why = entry
        assert status in ("SUPERSEDED", "WITHDRAWN"), (
            f"{label}: {status!r} is not a status a reader can act on")
        assert was, f"{label}: the superseded value must be recorded, not dropped"
        assert len(why or "") > 40, (
            f"{label}: a status with no recorded reason is a figure retired by "
            f"assertion. The reason is what a human merges or refuses.")
        if status == "SUPERSEDED":
            assert now, f"{label}: SUPERSEDED must name the replacement value"


def test_r1_the_ledger_covers_the_three_demonstrated_failure_modes(prod):
    """Each entry answers a failure mode that was EXECUTED, not imagined."""
    ledger = prod.FIGURE_LEDGER
    assert ledger.get("composed_covers", (None,))[0] == "WITHDRAWN", (
        "mode 1: the withdrawal that took the mutation harness offline")
    assert ledger.get("share_version_bearing", (None,))[0] == "SUPERSEDED", (
        "mode 2: the value that moved while the label did not")
    assert ledger.get("archive_epochs_at_T30", (None,))[0] == "WITHDRAWN", (
        "mode 3: the refuted figure whose declared string survives verbatim "
        "inside its own refutation")


def test_r1_the_ledger_is_reached_by_a_caller_and_printed(prod):
    """An addition nothing reaches is this project's most frequent defect."""
    lines = prod.figure_ledger_lines()
    assert lines, "figure_ledger_lines() returned nothing"
    for label, (status, _was, _now, _why) in prod.FIGURE_LEDGER.items():
        assert any(f"FIGURE {status}: {label}" in ln for ln in lines), (
            f"{label} is declared but not emitted in a form a guard can parse")
    src = ast.parse(PRODUCER.read_text(errors="replace"))
    called = {n.func.id for n in ast.walk(src)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "figure_ledger_lines" in called, (
        "figure_ledger_lines() has no caller in the producer, so the ledger "
        "would never print and the guard would never see it")


# ------------------------------------------------- R1b derived cross-check

def test_r1b_the_cross_check_tolerance_is_derived_not_typed(prod):
    """The MC tolerance must be the simulation's OWN sampling error.

    The block this replaces asserted a typed `err < 0.12` against the FIRST-
    ORDER form on a SINGLE seed. 0.12 is wider than that form's own truncation
    error (0.0838 at T=180), so the cross-check could not distinguish its own
    answer from a wrong one.
    """
    assert len(prod.CROSS_CHECK_SEEDS) >= 2, (
        "1 seed cannot separate a biased form from sampling noise")
    assert len(set(prod.CROSS_CHECK_SEEDS)) == len(prod.CROSS_CHECK_SEEDS)
    mean, se = prod.exposure_simulated_many(0.5, 180.0)
    assert se > 0, "a standard error of 0 would make every z infinite"
    exact = prod.exposure_exact_value(0.5, 180.0)
    first = 0.5 * 180.0 / 2 / 365.25
    z_exact = abs(mean - exact) / se
    z_first = abs(mean - first) / se
    assert z_exact < prod.CROSS_CHECK_Z, (
        f"the EXACT form must survive its own cross-check; z={z_exact:.2f}")
    assert z_first > z_exact, (
        f"the cross-check must PREFER the exact form over its first-order "
        f"term: z_exact={z_exact:.2f}, z_first_order={z_first:.2f}. If it does "
        f"not, the tolerance is absorbing the truncation error again.")


# ------------------------------------------------------------- R2 identity

def test_r2_the_resolved_id_comes_from_the_transport_envelope(orch):
    """Read from the client's own envelope -- never from the model's prose."""
    assert orch.resolved_model_from_stream_json(REAL_ENVELOPE) == "claude-opus-5"


def test_r2_an_absent_envelope_is_none_and_never_an_exception(orch):
    """`None` means the transport named nothing. That is a reportable answer."""
    for bad in ("", None, "not json", '{"type":"result"}', '{"modelUsage":{}}'):
        assert orch.resolved_model_from_stream_json(bad) is None


def test_r2_a_model_claiming_a_name_in_prose_is_not_identity(orch):
    """The founding principle: tools decide, not votes -- including self-votes."""
    prose = json.dumps({"type": "result",
                        "result": "I am claude-fable-5-2, the newest Fable."})
    assert orch.resolved_model_from_stream_json(prose) is None, (
        "a model's claim about its own identity is a model vote and must not "
        "be accepted as a measurement of it")


def test_r2_the_sink_records_the_resolved_id_beside_the_alias(orch):
    """Guard against an addition nothing reaches: the WRITE SITE must carry it.

    `bench/logs/standards_currency_2026-11-13/cc2.tools.attempt1.json.txt`
    recorded `"model": "opus"` and nothing else, which is the alias asked for.
    """
    src = ast.parse(ORCH.read_text(errors="replace"))
    keys = {k.value for n in ast.walk(src) if isinstance(n, ast.Dict)
            for k in n.keys if isinstance(k, ast.Constant)}
    assert "resolved_model" in keys, (
        "no sink dict carries `resolved_model`, so the id is extracted and "
        "then thrown away -- an addition nothing reaches")
    assert "identity_match" in keys, (
        "the comparison against the intended alias must be recorded too; a "
        "resolved id nobody compares reports nothing")


# -------------------------------------------------------------- R3 ratchet

def test_r3_a_max_of_last_n_bound_ratchets(ratchet):
    """It binds on the RATIO, never on the SIZE. Arithmetic, not opinion."""
    H = ratchet.HEADROOM
    for r in (1.0, 2.0, 3.0, H - 0.1, float(H)):
        _, refusals, _, _ = ratchet.drive([100 * r ** i for i in range(30)], "")
        assert refusals == 0, (
            f"growth at ratio {r} <= HEADROOM={H} was refused; the bound was "
            f"expected to grow to meet it")
    for r in (H + 0.1, 8.0):
        _, refusals, _, _ = ratchet.drive([100 * r ** i for i in range(30)], "")
        assert refusals > 0, (
            f"growth at ratio {r} > HEADROOM={H} was admitted; the bound is "
            f"then vacuous at every ratio and is not a bound at all")


def test_r3_the_bound_is_monotone_non_decreasing_in_the_record(ratchet):
    """Which is why it can only ever be conservative UPWARD.

    That direction is correct for a TOLERANCE (a commit timeout too small
    aborts a healthy commit) and inverted for a LIMIT ON HUMAN REVIEW LOAD (a
    bound too large admits unreviewed content).
    """
    base = [100, 120, 140, 160]
    for extra in (50, 100, 200, 5000):
        assert ratchet.bound(base + [extra]) >= ratchet.bound(base), (
            "adding an observation lowered the bound; max-of-last-N cannot do "
            "that within a window, and the claim rests on it")
