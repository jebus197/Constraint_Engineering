#!/usr/bin/env python3
"""Every live task-list entry must carry the hash identity the store issues.

HIS INSTRUCTION, 2026-11-06: *"Is there a way you can reliably automate/mechanise
the whole process, so that yu can no longer simply 'forget' to do it."*

THE FACILITY ALREADY EXISTED AND NOTHING MADE ME USE IT. `scripts/harvest_tickets_2026-10-17.py
--sources task_list` derives a ticket, with its 12-character identity, from a
task-list entry, and `scripts/raise_an_entry_2026-11-02.py --entry X` reports in
about 2 seconds whether all 7 surfaces an entry must reach have been reached --
including the ticket. On 2026-11-06 I added 4 entries by hand, ran neither, and
the commit gate refused after 11 MINUTES for a fault the checker would have
named immediately. A tool I have to remember is a tool that fails.

SO THIS IS THE REMINDER, AT COMMIT TIME, WHERE IT CANNOT BE SKIPPED. It asserts
the invariant rather than the habit: every entry the generator treats as live has
a ticket in the store carrying a hash. Adding an entry without harvesting turns
this red before the 11-minute board is ever reached.

MEASURED BEFORE SHIPPING, because a ratchet that is red on arrival gets switched
off and a ratchet that is vacuous proves nothing: 41 of 41 live entries carry a
ticket today, 1.000000, Wilson [0.914332, 1.000000], Clopper-Pearson
[0.913956, 1.000000]. So it is green on a healthy tree and it has a real
population to be green over.

WHAT IT DOES NOT DO. It does not judge which KIND a ticket should carry, nor
which fix belongs to which issue. He reserved that judgement to me explicitly,
and a test that guessed it would be asserting an opinion.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if not (REPO / "bench").is_dir():
    REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
#: OVERRIDABLE so a mutation harness can point this guard at a MUTANT COPY of
#: the store and prove it discriminates, without ever writing to the real one.
STORE = Path(os.environ.get("TICKET_STORE_OVERRIDE") or
             (REPO / "bench" / "tickets" / "tickets.jsonl"))
HARVEST = "python3 scripts/harvest_tickets_2026-10-17.py --sources task_list"


@pytest.fixture(scope="module")
def live_idents() -> list[str]:
    spec = importlib.util.spec_from_file_location(
        "mrb", REPO / "scripts" / "morning_report_build_2026-10-12.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["mrb"] = m
    spec.loader.exec_module(m)
    return [it["ident"] for it in m.task_items()]


@pytest.fixture(scope="module")
def ticketed() -> dict[str, str]:
    """ident -> newest tid, from the append-only store."""
    if not STORE.is_file():
        pytest.skip(f"ticket store absent at {STORE}")
    out: dict[str, str] = {}
    for line in STORE.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except Exception:                                      # noqa: BLE001
            continue
        ref = str(row.get("task_ref") or "").split(":")[-1].strip()
        tid = str(row.get("tid") or "").strip()
        if ref and tid:
            out[ref] = tid
    return out


class TestTheInvariant:
    def test_there_is_a_population_to_be_green_over(self, live_idents):
        """A ratchet over 0 items is vacuous on its first run."""
        assert len(live_idents) >= 10, (
            f"only {len(live_idents)} live entries; this guard would be nearly "
            "vacuous. Check that task_items() still reads the list.")

    def test_every_live_entry_has_a_ticket(self, live_idents, ticketed):
        missing = sorted(i for i in live_idents if i not in ticketed)
        assert not missing, (
            "these live entries carry no ticket, so they have no hash identity "
            "and cannot be tied to a verdict of his:\n  "
            + ", ".join(missing)
            + f"\nThis is mechanical, not a judgement call. Run:\n  {HARVEST}")

    def test_every_identity_is_a_12_character_hash(self, live_idents, ticketed):
        bad = {i: ticketed[i] for i in live_idents
               if i in ticketed and (len(ticketed[i]) != 12
                                     or not all(c in "0123456789abcdef"
                                                for c in ticketed[i]))}
        assert not bad, f"identities that are not 12 hex characters: {bad}"

    def test_distinct_entries_do_not_share_an_identity(self, live_idents, ticketed):
        """A shared identity asserts a relation that does not hold."""
        seen: dict[str, str] = {}
        clash = []
        for i in live_idents:
            t = ticketed.get(i)
            if not t:
                continue
            if t in seen:
                clash.append((seen[t], i, t))
            seen[t] = i
        assert not clash, f"entries sharing 1 identity: {clash}"


class TestTheToolsThisGuardStandsFor:
    """The guard is the reminder; these are what it reminds me to run."""

    def test_the_harvester_exists(self):
        assert (REPO / "scripts" / "harvest_tickets_2026-10-17.py").is_file(), (
            "the harvester is what assigns the identity; without it this "
            "guard names a repair that cannot be made")

    def test_the_per_entry_checker_exists(self):
        p = REPO / "scripts" / "raise_an_entry_2026-11-02.py"
        assert p.is_file(), (
            "raise_an_entry is the 2-second check that makes an 11-minute "
            "gate refusal avoidable")
        src = p.read_text(encoding="utf-8")
        assert "harvest_tickets" in src, (
            "raise_an_entry no longer names the harvester in its remedy, so a "
            "reader of its refusal is not told how to fix it")
