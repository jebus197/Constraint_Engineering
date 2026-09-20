#!/usr/bin/env python3
"""The spend-gate both paid launchers share: a RED suite record stops a dispatch.

FOUNDER, 2026-09-20, approving this as 1 of 3 items: the launchers should
consult the suite record before dispatching. 4 of the 6 seats are paid.

WHY A RED SUITE IS A SPEND QUESTION AND NOT A HOUSEKEEPING ONE. This project
has twice paid for a round it could not use. On 2026-09-05, 16 of 17 tool calls
errored and the errors were read as results. On 2026-09-10 a brief carried a
gamma figure wrong in its 3rd decimal and 2 seats spent part of their round on
it. A red suite is the cheapest available statement that the harness the seats
are about to reason over does not presently do what it says.

THE ASYMMETRY IS THE DESIGN, and it is what keeps the gate switched on. A record
1 commit behind HEAD is STALE, which is the normal condition of every record
after every save, and refusing on that would refuse nearly every dispatch. A RED
record is a positive claim that something is broken. A MISSING record is neither,
and unknown is not a licence to spend.

ONE IMPLEMENTATION, TWO CALLERS. `suite_record.gate` is called by
`bench/confer_maths_panel_2026-09-05.py` and by `reference_runner_v3.run_preflight`.
2 copies of a rule drift, and a drifted gate is worse than no gate: it reads as
protection that is not there. Both call sites are executed below, not read.

Every case below is EXECUTED against the real function with a real record file.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PANEL = ROOT / "bench" / "confer_maths_panel_2026-09-05.py"

GREEN = {"command": "python3 -m pytest bench/tests/ -q --netguard-strict",
         "commit": "abc1234", "when": "2026-09-20T02:00:00+01:00", "exit_code": 0,
         "tree_clean_at_record_time": True, "passed": 8011, "failed": 0,
         "skipped": 5, "xfailed": 1, "seconds": 1399.53}
RED = {**GREEN, "exit_code": 1, "passed": 8029, "failed": 5}


@pytest.fixture
def panel(monkeypatch, tmp_path):
    """The real dispatcher module, with its suite record pointed at a temp file.

    Imported by path rather than by name so this file does not depend on the
    package layout, and dispatched nothing: the gate under test runs before any
    seat is built.
    """
    sys.path.insert(0, str(ROOT / "bench"))
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("panel_under_test", PANEL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    import suite_record
    monkeypatch.setattr(suite_record, "RECORD", tmp_path / "suite_record.json")
    monkeypatch.delenv("PANEL_SUITE_UNCHECKED", raising=False)
    return mod, suite_record


def _write(rec, data):
    rec.RECORD.write_text(json.dumps(data), encoding="utf-8")


class TestAGreenRecordLetsTheDispatchProceed:
    """ANTI-VACUITY. A gate that refuses everything is not a gate."""

    def test_green_returns_without_raising(self, panel, capsys):
        mod, rec = panel
        _write(rec, GREEN)
        mod._refuse_if_the_suite_state_is_unknown()
        assert "GREEN" in capsys.readouterr().out

    def test_green_but_stale_still_proceeds_and_says_so(self, panel, capsys):
        """Every commit ages the record. Refusing on age would refuse nearly
        every dispatch, and a gate that refuses everything gets switched off."""
        mod, rec = panel
        _write(rec, {**GREEN, "commit": "0000000"})
        mod._refuse_if_the_suite_state_is_unknown()
        out = capsys.readouterr().out
        assert "GREEN" in out
        assert "0000000" in out, "a stale green record did not report its age"


class TestARedRecordStopsTheSpend:

    def test_red_raises_SystemExit_2(self, panel):
        mod, rec = panel
        _write(rec, RED)
        with pytest.raises(SystemExit) as e:
            mod._refuse_if_the_suite_state_is_unknown()
        assert e.value.code == 2

    def test_the_refusal_names_the_failure_count_and_the_repair_command(self, panel, capsys):
        mod, rec = panel
        _write(rec, RED)
        with pytest.raises(SystemExit):
            mod._refuse_if_the_suite_state_is_unknown()
        err = capsys.readouterr().err
        assert "5 failed" in err
        assert "suite_record.py record" in err, (
            "the refusal does not tell the operator how to clear it, which is "
            "how a gate becomes something people route around")
        assert "PANEL_SUITE_UNCHECKED=1" in err


class TestAMissingRecordIsUnknownNotGreen:

    def test_no_record_raises(self, panel):
        mod, rec = panel
        assert not rec.RECORD.exists()
        with pytest.raises(SystemExit) as e:
            mod._refuse_if_the_suite_state_is_unknown()
        assert e.value.code == 2

    def test_an_unreadable_record_raises_rather_than_passing(self, panel):
        """A failed lookup is a failed lookup. It is never a green suite."""
        mod, rec = panel
        rec.RECORD.write_text("{not json", encoding="utf-8")
        with pytest.raises(SystemExit):
            mod._refuse_if_the_suite_state_is_unknown()


class TestTheOverrideIsDeliberateAndLoud:

    def test_the_env_var_lets_a_red_record_through(self, panel, monkeypatch, capsys):
        mod, rec = panel
        _write(rec, RED)
        monkeypatch.setenv("PANEL_SUITE_UNCHECKED", "1")
        mod._refuse_if_the_suite_state_is_unknown()
        err = capsys.readouterr().err
        assert "dispatching anyway" in err, (
            "an override that is silent turns a deliberate decision into an "
            "invisible one")

    def test_the_override_says_what_it_is_overriding(self, panel, monkeypatch, capsys):
        mod, rec = panel
        _write(rec, RED)
        monkeypatch.setenv("PANEL_SUITE_UNCHECKED", "1")
        mod._refuse_if_the_suite_state_is_unknown()
        assert "exit code 1" in capsys.readouterr().err


class TestItIsWiredIntoTheOnlyPathToAPaidSeat:

    def test_main_calls_it(self):
        import ast
        tree = ast.parse(PANEL.read_text(encoding="utf-8"))
        main = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                   and n.func.id == "_refuse_if_the_suite_state_is_unknown"
                   for n in ast.walk(main)), (
            "main() no longer calls the suite gate, so it guards nothing")

    def test_it_runs_before_any_sandbox_is_built(self):
        """Order matters: a copy is 6.53 s and 606 MB per seat, measured. The
        refusal must land before that cost, not after it."""
        import ast
        tree = ast.parse(PANEL.read_text(encoding="utf-8"))
        main = next(n for n in tree.body
                    if isinstance(n, ast.FunctionDef) and n.name == "main")
        gate_line = build_line = None
        for n in ast.walk(main):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id == "_refuse_if_the_suite_state_is_unknown":
                gate_line = n.lineno
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr == "build" and build_line is None:
                build_line = n.lineno
        assert gate_line is not None and build_line is not None
        assert gate_line < build_line, (
            f"the suite gate is at line {gate_line}, after the first sandbox "
            f"build at {build_line}; it would refuse only after paying the copy cost")


class TestTheExperimentRunnerUsesTheSameGate:
    """`run_preflight` dispatches a connectivity probe to EVERY configured
    model, which is a paid call on every paid route. The suite check therefore
    has to sit above that probe, not beside it."""

    @pytest.fixture
    def runner(self, monkeypatch, tmp_path):
        sys.path.insert(0, str(ROOT / "bench"))
        sys.path.insert(0, str(ROOT / "scripts"))
        import reference_runner_v3 as rr
        import suite_record
        monkeypatch.setattr(suite_record, "RECORD", tmp_path / "suite_record.json")
        monkeypatch.delenv("RUNNER_SUITE_UNCHECKED", raising=False)
        return rr, suite_record

    @staticmethod
    def _configs(apis):
        """A roster and the cfg that selects it, as run_preflight reads them."""
        class _M:
            def __init__(self, label, api):
                self.label, self.api = label, api

        class _Exp:
            pass

        class _Cfg:
            pass

        exp, cfg = _Exp(), _Cfg()
        exp.models = [_M(f"S{i}", api) for i, api in enumerate(apis)]
        cfg.models = [m.label for m in exp.models]
        return exp, cfg

    def test_a_red_record_makes_preflight_return_False_when_seats_are_paid(self, runner):
        rr, rec = runner
        _write(rec, RED)
        exp, cfg = self._configs(["openrouter", "claude_cli"])
        assert rr.run_preflight(exp, "", cfg) is False, (
            "preflight passed with a red suite record and a paid seat, so the "
            "gate guards nothing")

    def test_a_missing_record_makes_preflight_return_False_when_seats_are_paid(self, runner):
        rr, rec = runner
        assert not rec.RECORD.exists()
        exp, cfg = self._configs(["deepseek"])
        assert rr.run_preflight(exp, "", cfg) is False

    def test_it_returns_False_rather_than_raising(self, runner):
        """main() reads the bool and exits 1 on it. A SystemExit escaping from
        inside preflight would bypass the runner's own abort message."""
        rr, rec = runner
        _write(rec, RED)
        exp, cfg = self._configs(["openrouter"])
        result = rr.run_preflight(exp, "", cfg)
        assert result is False and not isinstance(result, BaseException)

    def test_an_all_FREE_roster_is_not_gated_even_on_a_red_record(self, runner):
        """The deadlock this avoids, and it is not hypothetical: on 2026-09-20
        the suite was red BECAUSE task A8 was waiting on a Section P review,
        and Section P is discharged by a free cc2-and-fable round. A gate that
        refused it would block the review that turns the suite green."""
        rr, rec = runner
        _write(rec, RED)
        exp, cfg = self._configs(["claude_cli", "claude_cli"])
        # The connectivity probe is stubbed, so this asserts the GATE let the
        # round through and nothing was actually dispatched to do it.
        sent = []

        def _fake(mc, prompt, system):
            sent.append(mc.label)
            return "STATUS: OK\nMODEL: stub", 0.1

        import pytest as _pytest  # noqa: PLC0415
        mp = _pytest.MonkeyPatch()
        mp.setattr(rr, "dispatch_to_model", _fake)
        try:
            assert rr.run_preflight(exp, "", cfg) is True, (
                "a round with 0 paid seats was refused; there is no spend to protect")
        finally:
            mp.undo()
        assert sent == ["S0", "S1"], (
            f"the gate should have passed the round to the probe; got {sent}")

    def test_a_green_record_lets_preflight_reach_the_model_loop(self, runner):
        """ANTI-VACUITY: with no models configured the loop is empty and the
        answer is True. If green also returned False the gate would be a block,
        not a gate, and nothing would ever run."""
        rr, rec = runner
        _write(rec, GREEN)
        exp, cfg = self._configs([])
        assert rr.run_preflight(exp, "", cfg) is True

    def test_the_gate_precedes_the_connectivity_dispatch(self):
        import ast
        src = (ROOT / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8")
        tree = ast.parse(src)
        fn = next(n for n in ast.walk(tree)
                  if isinstance(n, ast.FunctionDef) and n.name == "run_preflight")
        gate_line = dispatch_line = None
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr == "gate":
                gate_line = n.lineno
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) \
                    and n.func.id == "dispatch_to_model" and dispatch_line is None:
                dispatch_line = n.lineno
        assert gate_line and dispatch_line and gate_line < dispatch_line, (
            f"the suite gate is at line {gate_line} and the paid connectivity "
            f"probe at {dispatch_line}; the gate must come first")


class TestAFreePanelRoundIsNotGated:
    """The same rule on the panel side, where PANEL_ONLY=cc2,fable is the
    ordinary way a free Section P round is dispatched."""

    def test_zero_paid_seats_proceeds_on_a_red_record(self, panel, capsys):
        mod, rec = panel
        _write(rec, RED)
        rec.gate(spend="panel (0 of 2 seats paid)",
                 override_env="PANEL_SUITE_UNCHECKED", paid_seats=0)
        err = capsys.readouterr().err
        assert "0 paid seats" in err and "Proceeding" in err

    def test_one_paid_seat_still_refuses(self, panel):
        mod, rec = panel
        _write(rec, RED)
        with pytest.raises(SystemExit) as e:
            rec.gate(spend="panel (1 of 2 seats paid)",
                     override_env="PANEL_SUITE_UNCHECKED", paid_seats=1)
        assert e.value.code == 2

    def test_the_panel_passes_its_own_count_through(self):
        """Executed wiring: the call site must forward paid_seats, or the
        free-round exemption is unreachable from the dispatcher."""
        import ast
        tree = ast.parse(PANEL.read_text(encoding="utf-8"))
        calls = [n for n in ast.walk(tree)
                 if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                 and n.func.attr == "gate"]
        assert calls, "the panel no longer calls the shared gate"
        assert any(k.arg == "paid_seats" for c in calls for k in c.keywords), (
            "the panel calls the gate without paid_seats, so every free round "
            "is gated as though it spent money")
