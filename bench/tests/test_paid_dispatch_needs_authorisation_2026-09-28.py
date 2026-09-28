"""Paid dispatch is refused unless a COMMITTED ledger authorises the round.

FOUNDER'S RULING, 2026-09-28, verbatim: *"There should be no paid dispatches
without my express authorisation. You should make sure this is the case going
forward. If the answers are useful however we should use them."*

WHAT WENT WRONG, and why an after-the-fact guard was not enough. On 2026-09-22 a
round the founder had asked to be free dispatched 5 PAID seats, because
`PANEL_ONLY=cc2,fable` was omitted and the module's default selected ALL 6 seats.
The safe path required remembering an environment variable; the expensive path was
what you got by forgetting. The existing guard `TestNoPaidSeatWasDispatched`
notices afterwards, which is a receipt, not a brake.

THE LIMIT OF THIS GUARD, STATED RATHER THAN IMPLIED. An environment variable is
something this assistant can set for itself, so a check resting on one checks
nothing it is meant to check. The ledger is a committed FILE: spending requires an
entry quoting the founder's authorisation, so an unauthorised dispatch means
forging his words somewhere that shows up in `git diff`. The enforcement is
AUDITABILITY, not impossibility.

NOTHING IS REMOVED. Paid dispatch works by the same route it always did, with an
authorisation recorded beside it.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "bench" / "confer_maths_panel_2026-09-05.py"


@pytest.fixture
def mod():
    sys.path.insert(0, str(ROOT / "bench"))
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("panel_paid_guard", PANEL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


class TestTheDefaultCostsNothing:
    def test_no_PANEL_ONLY_selects_only_free_seats(self, mod):
        assert [s[0] for s in mod.select_models("", "any_round")] == sorted(
            [s[0] for s in mod._ALL if s[0] in mod.FREE_SEATS],
            key=lambda n: [x[0] for x in mod._ALL].index(n))

    def test_the_free_set_is_exactly_the_claude_cli_seats(self, mod):
        """FREE_SEATS must not drift from the routes that actually cost nothing."""
        by_route = {s[0] for s in mod._ALL if s[2] == "claude_cli"}
        assert set(mod.FREE_SEATS) == by_route, (
            "FREE_SEATS and the claude_cli routes disagree; one of them is wrong"
        )

    def test_naming_only_free_seats_is_never_refused(self, mod):
        assert [s[0] for s in mod.select_models("cc2,fable", "any_round")] == ["cc2", "fable"]


class TestAPaidRequestIsRefusedWithoutALedgerEntry:
    def test_refused_when_the_ledger_is_absent(self, mod, monkeypatch, tmp_path):
        monkeypatch.setattr(mod, "PAID_LEDGER", tmp_path / "absent.json")
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx", "round_x")
        assert "REFUSED" in str(e.value)
        assert "cx" in str(e.value)

    def test_refused_when_the_round_is_not_in_the_ledger(self, mod, monkeypatch, tmp_path):
        led = tmp_path / "led.json"
        led.write_text(json.dumps([
            {"round": "some_other_round", "founder_authorisation": "y, spend up to 12 pounds on this",
             "date": "2026-09-28"}]), encoding="utf-8")
        monkeypatch.setattr(mod, "PAID_LEDGER", led)
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx,ge", "round_x")
        assert "no ledger entry" in str(e.value)

    def test_refused_when_the_entry_carries_no_authorisation_quote(self, mod, monkeypatch, tmp_path):
        """An entry that merely names the round authorises nothing."""
        led = tmp_path / "led.json"
        led.write_text(json.dumps([{"round": "round_x", "date": "2026-09-28"}]), encoding="utf-8")
        monkeypatch.setattr(mod, "PAID_LEDGER", led)
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx", "round_x")
        assert "no founder authorisation quote" in str(e.value)

    def test_refused_when_the_ledger_is_corrupt_rather_than_passing(self, mod, monkeypatch, tmp_path):
        """UNREADABLE IS NOT AUTHORISED. The same asymmetry the suite gate uses."""
        led = tmp_path / "led.json"
        led.write_text("{not json", encoding="utf-8")
        monkeypatch.setattr(mod, "PAID_LEDGER", led)
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx", "round_x")
        assert "unreadable" in str(e.value)

    def test_refused_when_the_ledger_is_not_a_list(self, mod, monkeypatch, tmp_path):
        led = tmp_path / "led.json"
        led.write_text(json.dumps({"round": "round_x"}), encoding="utf-8")
        monkeypatch.setattr(mod, "PAID_LEDGER", led)
        with pytest.raises(SystemExit):
            mod.select_models("cx", "round_x")


class TestAnAuthorisedRoundIsAllowed:
    """ANTI-VACUITY. A guard that refuses everything gets switched off."""

    def test_allowed_with_a_matching_entry_and_a_real_quote(self, mod, monkeypatch, tmp_path, capsys):
        led = tmp_path / "led.json"
        led.write_text(json.dumps([
            {"round": "round_x",
             "founder_authorisation": "y, run the paid panel on this one, budget 12 pounds",
             "date": "2026-09-28"}]), encoding="utf-8")
        monkeypatch.setattr(mod, "PAID_LEDGER", led)
        chosen = [s[0] for s in mod.select_models("cx,cc2", "round_x")]
        assert chosen == ["cx", "cc2"]
        assert "PAID DISPATCH AUTHORISED" in capsys.readouterr().out


class TestTheGuardIsWiredIntoMain:
    """An unreached guard guards nothing -- the additive standard's own words."""

    def test_main_rebinds_MODELS_through_select_models(self):
        src = PANEL.read_text(encoding="utf-8")
        body = src[src.index("def main()"):]
        assert "select_models(" in body, (
            "main() does not call select_models; the guard is unwired and the "
            "default roster is whatever module import left behind"
        )

    def test_select_models_is_executed_not_merely_defined(self, mod):
        """EXECUTE, DO NOT GREP: the assertion above reads the source, so this one
        CALLS the function and compares its output against the roster table."""
        free = mod.select_models("", "r")
        assert free, "select_models returned no seats at all"
        assert all(s[2] == "claude_cli" for s in free)
