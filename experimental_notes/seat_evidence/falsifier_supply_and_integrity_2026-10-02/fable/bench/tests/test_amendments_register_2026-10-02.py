# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_supply_and_integrity_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5360ebd161be1a1e84fdd5090c41e646d203254a9854819357e5a53c3ceca9bf
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""The rule-change amendments register (D-5 blast radius, 2026-10-02).

`--as-of` pins the CORPUS to an archived brief's date, so a figure invalidated
by corpus drift stays decidable forever. It cannot absorb a RULE change: the
access-only falsifier gate moved round 11's numerator at every date (2/640 ->
1/640, corpus unmoved), so a figure in the historical record stopped
re-executing with the record unedited and un-exempted.

THE REMEDY UNDER TEST. bench/amendments_register.json registers each such
invalidation: what was declared, which ruling superseded it, and what the same
producer prints as of the same date under the CURRENT rules. The validator
accepts the archived figure ONLY when the registered superseding value itself
re-executes in the same --as-of output. The register is held to evidence like
everything else, and these tests include both failure directions:

  * an UNREGISTERED stale figure refuses exactly as before, and
  * a TAMPERED register entry (a superseding value the producer does not
    print) refuses -- the register is not a whitewash channel.

EXECUTE, DO NOT GREP: every case runs the validator predicate.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "panel_brief_validate.py"
REGISTER = ROOT / "bench" / "amendments_register.json"
BRIEF = ROOT / "bench" / "logs" / "panel_round11_2026-09-11" / "BRIEF.md"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("pbv_amend", VALIDATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["pbv_amend"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture()
def round11_guard():
    if not BRIEF.is_file():
        pytest.skip("round 11's brief is not in this checkout")
    if not REGISTER.is_file():
        pytest.skip("amendments register absent")


def test_the_register_is_wellformed_and_append_only_in_shape():
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    assert isinstance(data.get("amendments"), list) and data["amendments"]
    for a in data["amendments"]:
        for k in ("amended_on", "ruling", "producer", "declared",
                  "reexecutes_as"):
            assert isinstance(a.get(k), str) and a[k], (k, a)


def test_a_registered_rule_change_reconciles_the_archived_brief(
        mod, round11_guard, capsys):
    problems = mod.check_declared_figures(
        BRIEF.read_text(), brief_path=BRIEF)
    stale = [p for p in problems if "2/640" in p]
    assert not stale, (
        f"the registered amendment did not reconcile the archived figure: "
        f"{stale}")
    err = capsys.readouterr().err
    assert "AMENDED FIGURE" in err, (
        "the acceptance was silent; a quiet amendment is how a rule change "
        "rots into an exemption")
    assert "2/640 = 0.3125%" in BRIEF.read_text(), (
        "the archived brief was EDITED -- the one fix the ruling forbids")


def test_an_unregistered_stale_figure_is_still_refused(mod, round11_guard):
    text = BRIEF.read_text().replace(
        "real-rejection rate : 2/640 = 0.3125%",
        "real-rejection rate : 3/640 = 0.4688%")
    problems = mod.check_declared_figures(text, brief_path=BRIEF)
    assert any("3/640" in p and "does not print it" in p for p in problems), (
        f"a figure with no amendment entry passed: {problems}")


def test_a_tampered_register_entry_is_refused(
        mod, round11_guard, tmp_path, monkeypatch):
    """DEMONSTRATED FAILING WHEN IT SHOULD: an entry whose superseding value
    the producer does not print must not reconcile anything."""
    fake_repo = tmp_path  # a register the test owns, not the committed one
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    data["amendments"][0]["reexecutes_as"] = (
        "real-rejection rate : 640/640 = 100.0000%")
    (fake_repo / "bench").mkdir()
    (fake_repo / "bench" / "amendments_register.json").write_text(
        json.dumps(data))
    monkeypatch.setattr(
        mod, "_rule_amendments",
        lambda repo: json.loads(
            (fake_repo / "bench" / "amendments_register.json").read_text()
        )["amendments"])
    problems = mod.check_declared_figures(
        BRIEF.read_text(), brief_path=BRIEF)
    assert any("2/640" in p and "does not print it" in p
               for p in problems), (
        "a TAMPERED register entry reconciled the brief -- the register is a "
        "whitewash channel")


def test_a_rule_amendment_on_a_fresh_brief_still_refuses(mod, tmp_path,
                                                         round11_guard):
    """The dodge stays shut: a brief written TODAY declaring the superseded
    figure fails the mtime gate before the register is ever consulted."""
    import shutil
    dodge = tmp_path / "BRIEF.md"
    shutil.copyfile(BRIEF, dodge)  # same text and dates; mtime NOW
    problems = mod.check_declared_figures(dodge.read_text(), brief_path=dodge)
    assert any("2/640" in p and "does not print it" in p
               for p in problems), (
        f"a freshly written brief re-declared a rule-superseded figure and "
        f"was not refused: {problems}")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
