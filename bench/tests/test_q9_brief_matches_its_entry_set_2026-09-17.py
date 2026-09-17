#!/usr/bin/env python3
"""The Question 9 brief names exactly the entries its producer derives.

The brief lists 34 entries in 4 groups, and 3 out-of-scope lists. Those lists
are prose a seat reads; `scripts/q9_engineering_entry_set_2026-09-17.py`
derives the same sets from the committed records. This test CALLS the producer
and compares its output with what the brief actually says, so an entry dropped
from a group, or a held entry sent by mistake, fails here rather than surfacing
in a seat's reply.
"""
from __future__ import annotations

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PRODUCER = ROOT / "scripts" / "q9_engineering_entry_set_2026-09-17.py"
BRIEF = ROOT / "experimental_notes" / "panel_briefs" / "Engineering_Entries_Brief_2026-09-17.md"
ID = r"[A-Z]\d+[a-z]?"


@pytest.fixture(scope="module")
def derived():
    spec = importlib.util.spec_from_file_location("q9set", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.entry_set()


def _bullet_ids(prefix: str) -> list[str]:
    line = next(x for x in BRIEF.read_text(encoding="utf-8").splitlines() if x.startswith(prefix))
    return re.findall(rf"\b({ID})\b", line.split(":", 1)[1])


def _group_ids() -> list[str]:
    ids = []
    for line in BRIEF.read_text(encoding="utf-8").splitlines():
        if line.startswith("- **Group "):
            head = line.split(":**", 1)[1] if ":**" in line else line.split("**", 2)[2]
            head = head.split(" A withdrawal is")[0]
            ids += re.findall(rf"\b({ID})\b", head)
    return ids


def test_the_groups_are_the_derived_set(derived):
    groups = _group_ids()
    assert len(groups) == len(set(groups)), "an entry appears in 2 groups"
    assert sorted(groups) == sorted(derived["set"]), (
        f"brief only: {sorted(set(groups) - set(derived['set']))}; "
        f"producer only: {sorted(set(derived['set']) - set(groups))}")
    assert len(derived["set"]) == 34


def test_held_for_the_founder_matches(derived):
    held = set(_bullet_ids("- Held for the founder by category"))
    model = set(_bullet_ids("- Held because the claim is about the mathematical model"))
    assert held | model == set(derived["held"]) | set(derived["model_bound"])
    assert model == {"A19", *derived["model_bound"]}


def test_reviewed_by_round_16_matches(derived):
    assert sorted(_bullet_ids("- Reviewed by panel round 16")) == sorted(derived["reviewed_by_round16"])


def test_the_staged_dispatch_copy_is_the_committed_brief():
    staged = ROOT / "bench" / "logs" / "panel_round17_2026-09-17" / "BRIEF.md"
    if not staged.exists():
        pytest.skip("bench/logs is not in every clone")
    assert staged.read_bytes() == BRIEF.read_bytes()


def test_the_producer_is_inert_under_help():
    r = subprocess.run([sys.executable, str(PRODUCER), "--help"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 0 and r.stdout.startswith("usage:") and "entries under review" not in r.stdout
