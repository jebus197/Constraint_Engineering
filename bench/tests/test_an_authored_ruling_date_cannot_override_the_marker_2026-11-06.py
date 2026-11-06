#!/usr/bin/env python3
"""An authored ruling date may not contradict the marker's, silently or at all.

★ FOUND 2026-11-05. The morning report tells him "YOU RULED THIS ON 2026-08-07"
for R1. R1's only marker reads `ruled: 2026-10-30` -- the deferral whose entire
purpose is to stop R1 being put to him again. The report prints the FIRST of the
3 identical rulings he has given on it.

THE MECHANISM, and why the obvious fix is wrong.
`scripts/morning_report_build_2026-10-12.py:701` reads

    ruled = d.get("ruled") or it.get("ruled")

so the hand-written `data/morning_report_decisions.json` wins over the marker
parsed from the task list. That precedence is DELIBERATE and must not be flipped:
the merged record is built as `{**it, **d}`, so `d`'s value reaches the OUTPUT
either way, and reading `d` first is what keeps the routing predicate agreeing
with what is printed. Flipping it would recreate the 2026-10-19 defect, where a
reader of the record saw a ruling and the predicate did not -- and that one cost
him, because the report asked again about B31 after he had approved it.

MEASURED, so the ratchet starts from a known floor: of 8 authored rows naming a
task entry AND carrying a `ruled` date, exactly 1 disagreed with its marker --
0.125000, Wilson [0.022417, 0.470888] -- and 0 of the 8 changed
`ruling_is_spent`'s verdict. So the fault is confined to what he is TOLD, and the
repair is to make a disagreement impossible rather than to pick a winner.
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
#: OVERRIDABLE so the fix can be demonstrated against a copy while a board holds
#: the tree. The default is the committed file.
DETAIL = Path(os.environ.get("DECISIONS_DETAIL") or
              (REPO / "experimental_notes" / "data" / "morning_report_decisions.json"))


@pytest.fixture(scope="module")
def mr():
    spec = importlib.util.spec_from_file_location(
        "mrb", REPO / "scripts" / "morning_report_build_2026-10-12.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules["mrb"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def authored():
    raw = json.loads(DETAIL.read_text(encoding="utf-8"))
    return {k: v for k, v in raw.items()
            if not k.startswith("_") and isinstance(v, dict)}


def _pairs(mr, authored):
    """(ident, authored_ruled, marker_ruled) for every row that can be compared."""
    marker = {it["ident"]: it for it in mr.task_items()}
    out = []
    for key, row in authored.items():
        if not key.startswith("task:"):
            continue
        ruled = (row.get("ruled") or "").strip()
        if not ruled:
            continue
        ident = key.split(":", 1)[1]
        m = marker.get(ident)
        if m is None or not (m.get("ruled") or "").strip():
            continue
        out.append((ident, ruled, m["ruled"].strip()))
    return out


class TestTheTwoSourcesAgree:
    def test_there_is_something_to_compare(self, mr, authored):
        """A ratchet on an empty set would be vacuous on its first run."""
        pairs = _pairs(mr, authored)
        assert len(pairs) >= 5, (
            f"only {len(pairs)} comparable rows; this guard would be nearly "
            "vacuous. Check that authored rows still carry `ruled`.")

    def test_no_authored_date_contradicts_its_marker(self, mr, authored):
        bad = [(i, a, m) for i, a, m in _pairs(mr, authored) if a != m]
        assert not bad, (
            "an authored ruling date disagrees with the task list's marker, and "
            "the authored one is what he is shown:\n" +
            "\n".join(f"  {i}: authored {a}, marker {m}" for i, a, m in bad))

    def test_the_precedence_is_still_authored_first(self, mr):
        """Pin the deliberate precedence so a later repair cannot flip it.

        Flipping it is the tempting fix and it is the wrong one: `{**it, **d}`
        puts `d`'s value in the output regardless, so a marker-first predicate
        would disagree with the printed record. That disagreement is the
        2026-10-19 defect. This test fails if someone flips it.
        """
        src = (REPO / "scripts" / "morning_report_build_2026-10-12.py").read_text(
            encoding="utf-8")
        assert 'ruled = d.get("ruled") or it.get("ruled")' in src, (
            "the precedence at line 701 has changed. If that was deliberate, "
            "the merge at `{**it, **d}` must change with it, or the predicate "
            "and the printed record will disagree again.")


class TestR1Specifically:
    """R1 is the row that found this, and the governing ruling is the deferral."""

    def test_r1s_marker_names_the_deferral(self, mr):
        r1 = next((it for it in mr.task_items() if it["ident"] == "R1"), None)
        if r1 is None:
            pytest.skip("R1 is no longer a live entry")
        assert (r1.get("state") or "").upper() == "DEFERRED"
        assert r1.get("ruled") == "2026-10-30"

    def test_the_authored_row_names_the_same_ruling(self, authored):
        row = authored.get("task:R1")
        if row is None or not (row.get("ruled") or "").strip():
            pytest.skip("task:R1 carries no authored ruling date")
        assert row["ruled"] == "2026-10-30", (
            f"authored {row['ruled']} against the marker's 2026-10-30. The "
            "report prints the authored one, so he is told about the first of "
            "3 identical rulings instead of the deferral that closed it.")
