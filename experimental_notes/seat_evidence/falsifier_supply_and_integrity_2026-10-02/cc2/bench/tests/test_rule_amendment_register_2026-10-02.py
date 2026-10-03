# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: b5119c9079d4e3b4e6bb0ffb0207089c90fc86262aa236315185723222c5883a
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""A figure invalidated by a RULE CHANGE, and the register that must not be a
free pass. (Panel dispute D-5 blast radius; Q5, 2026-10-02.)

THE SITUATION. `bench/logs/panel_round11_2026-09-11/BRIEF.md` declares
`real-rejection rate : 2/640 = 0.3125%`. Under the access-only gate the second
of those two rejections -- refused on the vocabulary token `seeded_fault`, not
on a key access -- is no longer a rejection, so the producer prints 1/640 AT
EVERY DATE. `--as-of` pins the DENOMINATOR; the NUMERATOR is what moved. A
figure in the historical record stopped re-executing because a rule changed
beneath it, retroactively, and the record is not editable.

THE NAMED HAZARD IS THAT THE REMEDY CANNOT FAIL. A register the validator
merely consults is a licence to paper over any discrepancy, and this project
has shipped a cannot-fail guard twice (`check_sk_threshold` hardwired to
`return True` passed 321 tests; A19's `e4_bandit` reported 0 HIGH forever).
So every one of the 5 admissibility conditions is DEMONSTRATED FAILING here,
each by mutating the register alone and requiring a REFUSAL:

  1. no entry for this brief                    -> refused
  2. `superseded` absent from the brief's text  -> refused
  3. `superseded == current` (a wildcard)       -> refused
  4. `producer` redirected to another script    -> refused
  5. `current` does not re-execute              -> refused

and the live register ACCEPTS, loudly, while the brief stays unedited.

Run:  python3 -m pytest bench/tests/test_rule_amendment_register_2026-10-02.py -q
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

VALIDATE = ROOT / "scripts" / "panel_brief_validate.py"
BRIEF = ROOT / "bench" / "logs" / "panel_round11_2026-09-11" / "BRIEF.md"
PRODUCER = "scripts/archived_falsifier_rejections_2026-09-10.py"
WANT = "real-rejection rate : 2/640 = 0.3125%"
CURRENT = "real-rejection rate : 1/640 = 0.1562%"
LABEL = "archived falsifier rejections that are NOT location artefacts"

pytestmark = pytest.mark.skipif(
    not BRIEF.is_file() or not VALIDATE.is_file(),
    reason="round 11's brief or the validator is not in this checkout")


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("_pbv", VALIDATE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _entry(**over):
    e = {"figure": LABEL,
         "brief": "bench/logs/panel_round11_2026-09-11/BRIEF.md",
         "producer": PRODUCER,
         "as_of": "2026-09-11",
         "superseded": WANT,
         "current": CURRENT,
         "amended": "2026-10-02",
         "rule": "the integrity gate narrowed to access-only"}
    e.update(over)
    return e


def _register(tmp_path, *entries):
    p = tmp_path / "amend.jsonl"
    p.write_text("".join(json.dumps(e) + "\n" for e in entries))
    return p


def _ask(mod, register):
    """The register's answer for the round-11 figure. None means REFUSED."""
    return mod._rule_amendment_reproduction(
        WANT, LABEL, ROOT / PRODUCER, BRIEF, BRIEF.read_text(encoding="utf-8"),
        ROOT, 600, register=register)


# -- the guard working ------------------------------------------------------

def test_the_live_register_accepts_the_round_11_figure(mod):
    """The committed register, not a fixture: the real file must work."""
    got = _ask(mod, None)
    assert got is not None, (
        "the committed register does not reconcile the round-11 figure; the "
        "historical record is still broken")
    assert got["current"] == CURRENT
    assert got["producer"] == PRODUCER


def test_the_archived_brief_is_not_edited(mod):
    assert WANT in BRIEF.read_text(encoding="utf-8"), (
        "the archived brief was EDITED, which falsifies the record of what "
        "the seats were given -- the one fix this ruling forbids")


def test_a_fixture_register_matching_the_live_one_also_accepts(mod, tmp_path):
    """Proves the acceptances below are refused for their stated reason and
    not because the harness cannot accept anything at all."""
    assert _ask(mod, _register(tmp_path, _entry())) is not None


# -- the 5 conditions, each demonstrated FAILING ----------------------------

def test_1_an_empty_register_leaves_the_validator_exactly_as_strict(mod, tmp_path):
    p = tmp_path / "empty.jsonl"
    p.write_text("")
    assert _ask(mod, p) is None


def test_1b_an_entry_for_a_different_brief_does_not_transfer(mod, tmp_path):
    reg = _register(tmp_path, _entry(brief="bench/logs/panel_round9/BRIEF.md"))
    assert _ask(mod, reg) is None, (
        "an amendment registered against another brief was honoured here; "
        "one entry would then excuse every brief")


def test_2_a_superseded_value_the_brief_never_declared_is_refused(mod, tmp_path):
    reg = _register(tmp_path, _entry(superseded="real-rejection rate : 9/640 = 1.4062%"))
    assert _ask(mod, reg) is None, (
        "an amendment was accepted against a figure the brief does not carry")


def test_3_an_entry_that_amends_nothing_is_refused(mod, tmp_path):
    """THE WILDCARD. superseded == current asserts no change, so it is not an
    amendment; honouring it would accept any figure that stopped reproducing."""
    reg = _register(tmp_path, _entry(current=WANT))
    assert _ask(mod, reg) is None


def test_4_redirecting_to_a_friendlier_producer_is_refused(mod, tmp_path):
    """`scripts/orphan_figures_2026-09-10.py` is the brief's OTHER declared
    producer and supports --as-of; naming it here must not launder the figure."""
    reg = _register(tmp_path, _entry(producer="scripts/orphan_figures_2026-09-10.py"))
    assert _ask(mod, reg) is None


def test_5_a_current_value_that_does_not_re_execute_is_refused(mod, tmp_path):
    """THE LOAD-BEARING CONDITION. The register's claim about the NEW value is
    re-executed, never trusted. Without this the register is a free pass."""
    reg = _register(tmp_path, _entry(current="real-rejection rate : 7/640 = 1.0938%"))
    assert _ask(mod, reg) is None


def test_5b_a_producer_that_is_not_in_the_tree_is_refused(mod, tmp_path):
    reg = _register(tmp_path, _entry(producer="scripts/does_not_exist_2026.py"))
    assert _ask(mod, reg) is None


# -- the register's own hygiene ---------------------------------------------

def test_a_malformed_or_incomplete_entry_contributes_nothing(mod, tmp_path):
    p = tmp_path / "bad.jsonl"
    p.write_text("not json at all\n"
                 + json.dumps({"figure": LABEL}) + "\n"      # missing keys
                 + json.dumps(["a", "list"]) + "\n")
    assert mod._load_rule_amendments(p) == []
    assert _ask(mod, p) is None


def test_the_committed_register_parses_and_every_entry_is_admissible(mod):
    entries = mod._load_rule_amendments(None)
    assert entries, "the committed register has no admissible entry"
    for e in entries:
        assert (ROOT / e["producer"]).is_file(), e["producer"]
        assert (ROOT / e["brief"]).is_file(), e["brief"]
        assert e["superseded"].strip() != e["current"].strip(), e
        assert e["superseded"] in (ROOT / e["brief"]).read_text(
            encoding="utf-8", errors="replace"), e


def test_the_validator_accepts_the_brief_and_says_the_rule_moved():
    """End to end, through the real entry point, and LOUDLY: a silent
    acceptance is how an exemption rots into a hole."""
    import subprocess
    r = subprocess.run([sys.executable, str(VALIDATE), str(BRIEF)],
                       cwd=ROOT, capture_output=True, text=True, timeout=1800)
    out = r.stdout + "\n" + r.stderr
    assert r.returncode == 0, out[-1200:]
    assert "RULE AMENDMENT" in out, (
        "the brief was accepted without saying the rule moved")
    assert "do NOT reuse this figure" in out
