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

import pathlib
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

        ★ CONVERTED FROM A SOURCE-TEXT MATCH TO AN EXECUTING CHECK, 2026-11-07.
        It used to assert that the literal
        `ruled = d.get("ruled") or it.get("ruled")` appears in
        `scripts/morning_report_build_2026-10-12.py`. That asserts only that the
        module spells itself a particular way: it breaks on a rename that
        changes nothing, and it cannot see a producer and a consumer that
        disagree, which is the very defect it was written to pin. The census
        guard's own remedy prefers conversion over widening the pinned set, and
        2 of the 4 assertions added on 2026-10-06 were converted this way.

        So the precedence is now EXERCISED: `decisions` is called with an item
        whose marker carries one ruling date and authored detail that carries
        another, and the merged record must show the AUTHORED one. The inverse
        is checked too, because a precedence that always returns the same side
        is not a precedence.
        """
        import json as _json

        def _run(marker_ruled, detail_ruled, tmp):
            body = {"task:ZZTEST": {"title": "t", "what": "w", "why": "y"}}
            if detail_ruled is not None:
                body["task:ZZTEST"]["ruled"] = detail_ruled
            p = tmp / "detail.json"
            p.write_text(_json.dumps(body), encoding="utf-8")
            old = mr.DETAIL
            try:
                mr.DETAIL = p
                item = {"key": "task:ZZTEST", "ident": "ZZTEST", "state": "OPEN"}
                if marker_ruled is not None:
                    item["ruled"] = marker_ruled
                attached, _missing, _orphan = mr.decisions([item])
            finally:
                mr.DETAIL = old
            assert attached, "the crafted item produced no attached record"
            return attached[0].get("ruled")

        import tempfile
        with tempfile.TemporaryDirectory() as td:
            tmp = pathlib.Path(td)
            #: authored detail WINS when it has a date
            got = _run("2026-01-01", "2026-02-02", tmp)
            assert got == "2026-02-02", (
                f"the authored ruling date must take precedence; got {got!r}. "
                f"If the precedence was flipped deliberately, the merge at "
                f"`{{**it, **d}}` must change with it, or the predicate and the "
                f"printed record will disagree again -- the 2026-10-19 defect.")
            #: and FALLS BACK to the marker when it has none
            got = _run("2026-01-01", None, tmp)
            assert got == "2026-01-01", (
                f"with no authored date the marker's must show through; got "
                f"{got!r}. A precedence that returns the same side either way "
                f"is not a precedence.")


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
