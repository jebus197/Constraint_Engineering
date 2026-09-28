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

WHAT WENT WRONG WITH THIS FILE'S OWN FIRST VERSION, 2026-09-28. Its 11 tests all
passed, and the gate they guarded refused every real authorisation. Each test
monkeypatched a SYNTHETIC ledger in a flat-list schema of its own invention, so
the green never once touched the committed record -- which is a MAPPING carrying
`authorisations[].rounds[]` and `founder_verbatim[]`, at a different path. A
fixture in a schema the production file does not use tests the fixture.

THE TWO CHANGES THAT FOLLOW FROM THAT. Every fixture here is now written in the
REAL schema and patched onto the reader the gate actually consults, so a schema
change breaks these tests instead of hiding from them. And the round-trip against
the real committed ledger lives in
`test_paid_dispatch_gate_reads_the_real_ledger_2026-09-28.py`, which monkeypatches
nothing at all.

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


def real_schema(round_name: str, *, quote: str | None = None, **extra) -> dict:
    """A ledger in the schema the COMMITTED file uses, not one of our own.

    The shape is asserted against the real record in
    `test_paid_dispatch_gate_reads_the_real_ledger_2026-09-28.py`, so this helper
    cannot quietly drift into a fixture-only dialect.
    """
    entry: dict = {
        "id": f"fixture-{round_name}",
        "date": "2026-09-28",
        "rounds": [round_name],
    }
    if quote is not None:
        entry["founder_verbatim"] = [quote]
    entry.update(extra)
    return {"authorisations": [entry]}


def point_the_reader_at(monkeypatch, mod, path: Path) -> None:
    """Redirect the ledger by patching THE READER the gate delegates to.

    Patching a path on the panel module would no longer redirect anything: the
    gate asks `bench/paid_dispatch_authorisations.py` where the ledger lives, so
    that module is what a test has to move. This is the point of having 1 parser.
    """
    monkeypatch.setattr(mod._paid_ledger, "AUTHORISATIONS", path)


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

    def test_free_and_paid_partition_the_roster_across_both_modules(self, mod):
        """2 MODULES NOW NAME THE MONEY BOUNDARY, so check they agree.

        The gate owns `FREE_SEATS`; the reader owns `PAID_SEATS`. Neither is
        derived from the other, so they can drift -- and a seat missing from both
        would be dispatched as free while billing, which is the exact direction
        that costs money. Every seat in the roster must be in exactly 1 set.
        """
        free = set(mod.FREE_SEATS)
        paid = set(mod._paid_ledger.PAID_SEATS)
        roster = {s[0] for s in mod._ALL}
        assert not (free & paid), f"seats claimed as both free and paid: {free & paid}"
        assert free | paid == roster, (
            f"roster and the 2 money sets disagree; unclassified: "
            f"{roster - (free | paid)}, named but not in the roster: "
            f"{(free | paid) - roster}"
        )

    def test_naming_only_free_seats_is_never_refused(self, mod):
        assert [s[0] for s in mod.select_models("cc2,fable", "any_round")] == ["cc2", "fable"]


class TestAPaidRequestIsRefusedWithoutALedgerEntry:
    def test_refused_when_the_ledger_is_absent(self, mod, monkeypatch, tmp_path):
        point_the_reader_at(monkeypatch, mod, tmp_path / "absent.json")
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx", "round_x")
        assert "REFUSED" in str(e.value)
        assert "cx" in str(e.value)
        assert "no authorisation ledger at" in str(e.value)

    def test_refused_when_the_round_is_not_in_the_ledger(self, mod, monkeypatch, tmp_path):
        led = tmp_path / "led.json"
        led.write_text(json.dumps(real_schema(
            "some_other_round", quote="y, spend up to 12 pounds on this")),
            encoding="utf-8")
        point_the_reader_at(monkeypatch, mod, led)
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx,ge", "round_x")
        assert "no ledger entry" in str(e.value)

    def test_refused_when_the_entry_carries_no_authorisation_quote(self, mod, monkeypatch, tmp_path):
        """An entry that merely names the round authorises nothing."""
        led = tmp_path / "led.json"
        led.write_text(json.dumps(real_schema("round_x")), encoding="utf-8")
        point_the_reader_at(monkeypatch, mod, led)
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx", "round_x")
        assert "no founder authorisation quote" in str(e.value)

    def test_refused_when_the_quote_is_too_short_to_be_his_words(self, mod, monkeypatch, tmp_path):
        """A 1-word entry is not an authorisation. The bound is the module's own."""
        led = tmp_path / "led.json"
        led.write_text(json.dumps(real_schema("round_x", quote="y")), encoding="utf-8")
        point_the_reader_at(monkeypatch, mod, led)
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx", "round_x")
        assert "no founder authorisation quote" in str(e.value)
        # EXTRACT the bound, never restate it: a hardcoded 20 here would keep
        # passing if the module raised its own threshold.
        assert str(mod._MIN_QUOTE_CHARS) in str(e.value)

    def test_refused_when_the_ledger_is_corrupt_rather_than_passing(self, mod, monkeypatch, tmp_path):
        """UNREADABLE IS NOT AUTHORISED. The same asymmetry the suite gate uses."""
        led = tmp_path / "led.json"
        led.write_text("{not json", encoding="utf-8")
        point_the_reader_at(monkeypatch, mod, led)
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx", "round_x")
        assert "unreadable" in str(e.value)

    def test_refused_when_the_ledger_is_the_wrong_shape(self, mod, monkeypatch, tmp_path):
        """A BARE LIST IS THE OLD, WRONG SCHEMA, and it must refuse rather than raise.

        This is the shape the first version of the gate demanded. A ledger in it
        now REFUSES, so the failure is a visible refusal and never a traceback
        halfway into a dispatch.
        """
        led = tmp_path / "led.json"
        led.write_text(json.dumps([{"round": "round_x",
                                    "founder_authorisation": "y, go ahead and spend it"}]),
                       encoding="utf-8")
        point_the_reader_at(monkeypatch, mod, led)
        with pytest.raises(SystemExit) as e:
            mod.select_models("cx", "round_x")
        assert "not a mapping" in str(e.value)


class TestAnAuthorisedRoundIsAllowed:
    """ANTI-VACUITY. A guard that refuses everything gets switched off."""

    def test_allowed_with_a_matching_entry_and_a_real_quote(self, mod, monkeypatch, tmp_path, capsys):
        led = tmp_path / "led.json"
        led.write_text(json.dumps(real_schema(
            "round_x", quote="y, run the paid panel on this one, budget 12 pounds")),
            encoding="utf-8")
        point_the_reader_at(monkeypatch, mod, led)
        chosen = [s[0] for s in mod.select_models("cx,cc2", "round_x")]
        assert chosen == ["cx", "cc2"]
        assert "PAID DISPATCH AUTHORISED" in capsys.readouterr().out

    def test_one_entry_may_authorise_several_rounds(self, mod, monkeypatch, tmp_path):
        """The committed record does this: 1 commission covers 6 named rounds."""
        led = tmp_path / "led.json"
        led.write_text(json.dumps({"authorisations": [{
            "id": "many", "date": "2026-09-28",
            "rounds": ["r_a", "r_b", "r_c"],
            "founder_verbatim": ["y, all 3 rounds are authorised, 12 pounds total"],
        }]}), encoding="utf-8")
        point_the_reader_at(monkeypatch, mod, led)
        for rn in ("r_a", "r_b", "r_c"):
            assert [s[0] for s in mod.select_models("cx", rn)] == ["cx"]
        with pytest.raises(SystemExit):
            mod.select_models("cx", "r_d")

    def test_rounds_match_exactly_and_never_by_prefix(self, mod, monkeypatch, tmp_path):
        """The reader's rule, restated as an executed check: 'was this authorised?'
        and never 'does this look like something that was?'."""
        led = tmp_path / "led.json"
        led.write_text(json.dumps(real_schema(
            "maths_panel_2026-09-20", quote="y, this one round only, 12 pounds")),
            encoding="utf-8")
        point_the_reader_at(monkeypatch, mod, led)
        assert [s[0] for s in mod.select_models("cx", "maths_panel_2026-09-20")] == ["cx"]
        for near_miss in ("maths_panel_2026-09-20_r2", "maths_panel_2026-09-2",
                          "maths_panel", "MATHS_PANEL_2026-09-20"):
            with pytest.raises(SystemExit):
                mod.select_models("cx", near_miss)


class TestTheGuardIsWiredIntoMain:
    """An unreached guard guards nothing -- the additive standard's own words."""

    def test_main_reaches_select_models_before_the_suite_spend_gate(self, mod, monkeypatch):
        """EXECUTE, DO NOT GREP. This used to assert that the substring
        "select_models(" appeared in main()'s source, which proves only that
        main() describes itself consistently -- the defect class this project has
        recorded 4 times. It now CALLS main() with the 2 gates replaced by spies
        and reads the order off the call log.

        THE ORDER IS THE POINT. `suite_record.gate` returns without refusing when
        `paid_seats` is 0, and the module-level MODELS binding carries no paid
        seat, so if the suite gate ran BEFORE this rebind it would count 0 paid
        seats and a red suite would stop blocking paid rounds.
        """
        calls: list[str] = []
        sentinel = RuntimeError("stop after the rebind")

        # `resolve_brief` is what binds LOGS, so stubbing it means binding LOGS
        # here instead -- otherwise main() dies on an unresolved run directory
        # and this test never reaches the thing it is measuring. (Writing it the
        # naive way is how the bare `LOGS.name` on that line was found: it gave
        # "AttributeError: 'NoneType' object has no attribute 'name'" instead of
        # the legible message `_logs_dir()` is there to produce.)
        monkeypatch.setattr(mod, "resolve_brief", lambda *a, **k: None)
        monkeypatch.setattr(mod, "_validate_brief_or_refuse", lambda *a, **k: None)
        monkeypatch.setattr(mod, "LOGS", ROOT / "bench" / "logs" / "a_round_name")
        monkeypatch.setattr(mod, "_refuse_if_the_suite_state_is_unknown",
                            lambda *a, **k: calls.append("suite_gate"))

        def spy_select(only, round_name):
            calls.append(f"select_models({only!r}, {round_name!r})")
            raise sentinel

        monkeypatch.setattr(mod, "select_models", spy_select)
        with pytest.raises(RuntimeError):
            mod.main()

        assert calls, "main() reached neither gate; the guard is unwired"
        assert calls[0].startswith("select_models("), (
            f"main() did not call select_models first; call order was {calls}. "
            f"With the suite gate first it counts 0 paid seats and waves through "
            f"a red suite."
        )
        # And it is called with the ROUND, not with nothing: the ledger keys on it.
        assert f"{mod.LOGS.name!r}" in calls[0], (
            f"select_models was not given the round name; got {calls[0]}"
        )

    def test_select_models_is_executed_not_merely_defined(self, mod):
        free = mod.select_models("", "r")
        assert free, "select_models returned no seats at all"
        assert all(s[2] == "claude_cli" for s in free)

    def test_module_level_MODELS_can_never_carry_a_paid_seat(self, monkeypatch):
        """THE IMPORT-TIME HOLE, closed 2026-09-28 (panel seat's finding).

        `select_models` is reached only through `main()`, so an importer that
        dispatched from module state walked past the ledger entirely. Measured
        before the fix: `PANEL_ONLY=cx,cgpt` plus a bare import gave a MODELS list
        of 2 paid seats that no ledger check had seen. A round is what the ledger
        authorises and no round exists at import time, so no paid seat can be
        authorised at import time.

        THE ENVIRONMENT VARIABLE IS THE WHOLE TEST, so this imports its own copy
        of the module rather than taking the shared `mod` fixture. That fixture
        imports with PANEL_ONLY unset, under which MODELS is free however the
        binding is written -- the assertion would hold vacuously and would keep
        holding with the fix reverted.
        """
        monkeypatch.setenv("PANEL_ONLY", "cx,cgpt")
        spec = importlib.util.spec_from_file_location("panel_paid_import_hole", PANEL)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)

        assert m._ONLY == "cx,cgpt", (
            f"the import did not see PANEL_ONLY; _ONLY is {m._ONLY!r} and this "
            f"test would prove nothing"
        )
        named_paid = [s[0] for s in m._ALL
                      if s[0] in m._ONLY.split(",") and s[2] != "claude_cli"]
        assert named_paid == ["cx", "cgpt"], (
            f"the roster no longer routes cx and cgpt as paid; got {named_paid}, "
            f"so this test is no longer exercising a paid PANEL_ONLY"
        )
        paid_at_import = [s[0] for s in m.MODELS if s[2] != "claude_cli"]
        assert not paid_at_import, (
            f"module-level MODELS carries paid seat(s) {paid_at_import} that no "
            f"ledger check has seen"
        )

    def test_a_free_seat_named_in_PANEL_ONLY_still_appears_at_import(self, monkeypatch):
        """ANTI-VACUITY FOR THE TEST ABOVE, and this half is the panel seat's own.

        "No paid seat at import" is also satisfied by a roster that is always
        EMPTY, which would break every importer reading MODELS. Dropping the paid
        seat must not drop the free one named beside it.
        """
        monkeypatch.setenv("PANEL_ONLY", "cc2,cx")
        spec = importlib.util.spec_from_file_location("panel_free_survives", PANEL)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        assert m._ONLY == "cc2,cx"
        assert [s[0] for s in m.MODELS] == ["cc2"], (
            f"PANEL_ONLY=cc2,cx should leave exactly the free seat cc2 at import; "
            f"got {[s[0] for s in m.MODELS]}"
        )
