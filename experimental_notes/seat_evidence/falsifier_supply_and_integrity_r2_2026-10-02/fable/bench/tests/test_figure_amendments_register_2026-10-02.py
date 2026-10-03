# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: a47ffdd77e527867955687899b388899eeb243cfcd2721e18c3a42fd3cd454f0
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""A figure invalidated by a RULE change is superseded loudly, never silenced.

Q5 RULING, 2026-10-02. `--as-of` pins the CORPUS to an archived brief's date;
it cannot absorb a RULE change, because a rule change moves the numerator at
every date. The access-only narrowing of the falsifier-integrity gate turned
the round-11 brief's `real-rejection rate : 2/640 = 0.3125%` into 1/640
retroactively, and the figure stopped re-executing while the record stood.

The remedy under test: a committed amendments register
(scripts/figure_amendments_register.json) that the validator consults ONLY
after the strict check and the plain --as-of check both fail. Acceptance
requires the producer, as-of the brief's date, to print the REGISTERED
amended value exactly. Everything else still refuses:

  * a figure matching neither declared nor amended value   -> refused
  * a register entry carrying a WRONG amended value        -> refused
  * a figure the register never recorded                   -> refused
  * a brief written today claiming a past date (the dodge) -> refused (mtime)

EXECUTE, DO NOT GREP: every case runs check_declared_figures for real, so the
producer is genuinely re-executed with --as-of underneath.
"""
from __future__ import annotations

import calendar
import importlib.util
import json
import os
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
VALIDATE = ROOT / "scripts" / "panel_brief_validate.py"
REGISTER = ROOT / "scripts" / "figure_amendments_register.json"
PRODUCER = "scripts/archived_falsifier_rejections_2026-09-10.py"

DECLARED = "real-rejection rate : 2/640 = 0.3125%"
AMENDED = "real-rejection rate : 1/640 = 0.1562%"
LABEL = "archived falsifier rejections that are NOT location artefacts"


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("pbv_amend", VALIDATE)
    m = importlib.util.module_from_spec(spec)
    sys.modules["pbv_amend"] = m
    spec.loader.exec_module(m)
    return m


def _brief(tmp_path: Path, value: str) -> Path:
    b = tmp_path / "BRIEF.md"
    b.write_text(
        f"<!-- figure: {LABEL} | {PRODUCER} | {value} -->\n"
        f"dated 2026-09-11\n")
    # Backdate the mtime to the brief's own date, as a genuine archived brief
    # has. The dodge test below does NOT do this -- that is its point.
    eod = calendar.timegm(time.strptime("2026-09-11", "%Y-%m-%d")) + 3600
    os.utime(b, (eod, eod))
    return b


class TestTheRegisterPath:
    def test_the_registered_amended_value_is_accepted_loudly(
            self, mod, tmp_path, capsys):
        b = _brief(tmp_path, DECLARED)
        problems = mod.check_declared_figures(b.read_text(), brief_path=b)
        err = capsys.readouterr().err
        assert problems == [], problems
        assert "SUPERSEDED BY RULE" in err and "A-2026-10-02-access-only-gate" in err, (
            "the acceptance was silent, or did not name the rule change")

    def test_a_third_value_is_still_refused(self, mod, tmp_path):
        """The register converts ONE refusal into ONE named acceptance; it
        must not become an exemption for the producer's whole output."""
        b = _brief(tmp_path, "real-rejection rate : 3/640 = 0.4688%")
        problems = mod.check_declared_figures(b.read_text(), brief_path=b)
        assert problems, "a figure matching neither declared nor amended passed"

    def test_a_wrong_amended_value_in_the_register_is_refused(
            self, mod, tmp_path, monkeypatch):
        """The register itself is falsifiable: an entry whose amended value
        the producer does not print buys nothing."""
        reg = json.loads(REGISTER.read_text())
        reg["amendments"][0]["amended"] = "real-rejection rate : 9/640 = 1.4062%"
        fake = tmp_path / "register.json"
        fake.write_text(json.dumps(reg))
        monkeypatch.setattr(mod, "_AMENDMENTS_REGISTER", fake)
        b = _brief(tmp_path, DECLARED)
        problems = mod.check_declared_figures(b.read_text(), brief_path=b)
        assert problems, (
            "a register entry carrying a value the producer does not print "
            "was accepted -- the register has become an assertion, not a "
            "measurement")

    def test_a_missing_register_fails_closed(self, mod, tmp_path, monkeypatch):
        monkeypatch.setattr(mod, "_AMENDMENTS_REGISTER",
                            tmp_path / "no_such_register.json")
        b = _brief(tmp_path, DECLARED)
        problems = mod.check_declared_figures(b.read_text(), brief_path=b)
        assert problems, "with no register the original refusal must stand"

    def test_the_dodge_is_still_shut(self, mod, tmp_path):
        """A brief written TODAY (mtime now) declaring the superseded figure
        must still be refused: the register does not reopen the mtime gate."""
        b = tmp_path / "B.md"
        b.write_text(
            f"<!-- figure: {LABEL} | {PRODUCER} | {DECLARED} -->\n"
            f"dated 2026-09-11\n")   # mtime is NOW
        problems = mod.check_declared_figures(b.read_text(), brief_path=b)
        assert problems, (
            "a freshly written brief re-declared a rule-superseded figure "
            "and was not refused")


class TestTheArchivedBrief:
    def test_round_11_is_whole_and_accepted(self, mod, capsys):
        brief = ROOT / "bench/logs/panel_round11_2026-09-11/BRIEF.md"
        if not brief.is_file():
            pytest.skip("round 11's brief is not in this checkout")
        text = brief.read_text()
        assert "2/640 = 0.3125%" in text, "the archived brief was EDITED"
        problems = mod.check_declared_figures(text, brief_path=brief)
        assert problems == [], problems


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
