# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 22b163f5b5484e488fb8a580ff2cda64e8e1d2af9e0e0dcfca19aeb9a100b3e4
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The paid-dispatch gate must read the ledger the founder actually committed.

PANEL FINDING (seat B), 2026-09-28. The gate shipped pointing at
`bench/paid_dispatch_authorisations.json` -- a file that does not exist -- and
parsing a flat-list schema the committed ledger at
`bench/directives/universal/paid_dispatch_authorisations.json` does not use
(it is a dict with "authorisations" entries carrying "rounds" and
"founder_verbatim"). Fail-closed, so no unauthorised spend was possible; but
every round the founder HAD authorised would have been REFUSED, and the only
way to green the gate was to write a SECOND ledger file -- the exact
two-copies drift `bench/paid_dispatch_authorisations.py` documents as the
shape to avoid. Its own suite passed because every test monkeypatched
PAID_LEDGER to a synthetic file in the flat schema; no test executed the gate
against the committed record.

EVERY CASE HERE RUNS AGAINST THE REAL COMMITTED FILE, plus one flat-schema
case so the earlier tests' shape keeps working.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "bench" / "confer_maths_panel_2026-09-05.py"
COMMITTED = ROOT / "bench" / "directives" / "universal" / "paid_dispatch_authorisations.json"


@pytest.fixture
def mod():
    sys.path.insert(0, str(ROOT / "bench"))
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("panel_paid_gate_real", PANEL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_gate_points_at_the_committed_ledger(mod):
    assert Path(mod.PAID_LEDGER) == COMMITTED, (
        f"gate reads {mod.PAID_LEDGER}, audit guards read {COMMITTED}; "
        "two ledgers is the drift the sibling module forbids"
    )
    assert COMMITTED.is_file(), "the committed ledger is missing"


def test_a_round_the_founder_authorised_is_actually_allowed(mod, capsys):
    """ANTI-VACUITY against the REAL record: the gate must pass at least one
    round the committed ledger names, or the authorisation half is unwired."""
    data = json.loads(COMMITTED.read_text(encoding="utf-8"))
    rounds = [r for e in data.get("authorisations", []) for r in e.get("rounds", [])]
    assert rounds, "committed ledger names no rounds; premise gone, re-examine"
    ok, reason = mod._paid_is_authorised(rounds[0])
    assert ok, f"committed authorisation for {rounds[0]!r} was refused: {reason}"
    chosen = [s[0] for s in mod.select_models("cx", rounds[0])]
    assert chosen == ["cx"]
    assert "PAID DISPATCH AUTHORISED" in capsys.readouterr().out


def test_an_unauthorised_round_is_still_refused_on_the_real_ledger(mod):
    ok, reason = mod._paid_is_authorised("round_that_was_never_authorised")
    assert not ok
    with pytest.raises(SystemExit) as e:
        mod.select_models("cx", "round_that_was_never_authorised")
    assert "REFUSED" in str(e.value)


def test_the_flat_test_schema_still_parses(mod, monkeypatch, tmp_path):
    """The earlier suite stages flat-list ledgers; both shapes must keep working."""
    led = tmp_path / "led.json"
    led.write_text(json.dumps([
        {"round": "round_y", "founder_authorisation": "y, spend up to 12 pounds on it",
         "date": "2026-09-28"}]), encoding="utf-8")
    monkeypatch.setattr(mod, "PAID_LEDGER", led)
    assert mod._paid_is_authorised("round_y")[0]
    assert not mod._paid_is_authorised("round_z")[0]
