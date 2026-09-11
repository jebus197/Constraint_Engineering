"""Task A12: every founder-ruled tracker item is CARRIED or DECLARED EXCLUDED.

THE PROBLEM. The master task list calls itself "the ordered executable subset" of
a 121-item inventory, so an item's absence is scoped rather than silent -- but it
named none of the exclusions, and a reader cannot tell a deliberate omission from
a lost item.

THE 15 RULED ITEMS ARE NOT ONE KIND, and conflating them is how the original
measurement read 11 as a defect rather than as a scope:

  RUNWAY (11)          work scheduled for a named point on the path to Bench Run
                       2. Deliberately not on this list; DECLARED EXCLUDED.
  STUDY PROGRAMME (4)  things to MEASURE DURING a simulated run -- the founder's
                       "mark it in our simulated run programme of study". Not
                       executable entries and never should be. One of the 4
                       (item 46) is touched by the list; the other 3 are now
                       declared.

Unaccounted: 3 of 15 = 20.0000% before the declaration, 0 of 15 after, Wilson
[0.0000%, 20.3883%], Clopper-Pearson [0.0000%, 21.8019%].

TWO INSTRUMENT DEFECTS IN ONE MEASUREMENT, both of which reported a FALSE ZERO.

  The first used `(acc if pat.search(block) else []) and acc.append(n)`, which
  short-circuits on an EMPTY list and never appends. It reported that A12
  declared nothing while the entry visibly names 11 items.

  The second required `item` and the number to be adjacent, and the declaration
  reads `item **14 critical-severity ceiling**` -- markdown emphasis sits between
  the word and the number. The text was there; the pattern was not looking at
  the text a human sees.

A clever one-liner that silently does nothing, and a pattern that cannot see its
own subject, are the same failure as a guard that cannot fire.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "ruled_items_are_accounted_2026-09-11.py"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("ruled", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["ruled"] = mod
    spec.loader.exec_module(mod)
    return mod


class TestTheTrackerIsRead:
    def test_it_finds_both_kinds(self, m):
        items = m.ruled_items()
        kinds = {k for k, _t in items.values()}
        assert kinds == {"RUNWAY", "STUDY PROGRAMME"}, kinds

    def test_the_split_is_eleven_and_four(self, m):
        items = m.ruled_items()
        runway = [n for n, (k, _t) in items.items() if k == "RUNWAY"]
        study = [n for n, (k, _t) in items.items() if k == "STUDY PROGRAMME"]
        assert len(runway) == 11, sorted(runway)
        assert len(study) == 4, sorted(study)

    def test_it_reads_rather_than_restates(self):
        """TWO REPRESENTATIONS WITH A COMPARATOR. If the numbers were typed into
        the script, an item added to the tracker would be silently absent from
        the comparison -- which is the shape this whole entry is about."""
        src = SCRIPT.read_text(encoding="utf-8")
        body = src[src.index("def ruled_items"):src.index("def _a12_block")]
        for n in ("17", "19", "20", "24", "31", "34", "36", "37", "38", "42", "43"):
            assert f"({n})" not in body and f"= {n}" not in body, (
                f"item {n} looks hard-coded into the reader")


class TestNothingIsUnaccounted:
    def test_every_ruled_item_is_carried_or_declared(self, m):
        items = m.ruled_items()
        block, rest = m._a12_block()
        bad = [(n, k, t) for n, (k, t) in sorted(items.items())
               if m.account(n, block, rest) == "UNACCOUNTED"]
        assert not bad, (
            f"these founder-ruled items are neither carried on the list nor "
            f"declared excluded, so a reader cannot tell a deliberate omission "
            f"from a lost item: {bad}")

    def test_the_check_can_fire(self, m):
        """POSITIVE CONTROL. A number nothing mentions must come back
        UNACCOUNTED, or the assertion above is passing on a pattern that matches
        everything."""
        block, rest = m._a12_block()
        assert m.account(99999, block, rest) == "UNACCOUNTED"

    def test_markdown_emphasis_does_not_hide_a_declaration(self, m):
        """THE SECOND FALSE ZERO, pinned. `item **14 ...` is how a reader wants
        to see it, and a pattern requiring adjacency reported it absent."""
        assert m.account(14, "declared as item **14 the ceiling**", "") == \
            "DECLARED EXCLUDED"
        assert m.account(14, "declared as item 14 the ceiling", "") == \
            "DECLARED EXCLUDED"


class TestTheScriptRuns:
    def test_it_exits_zero_and_reports_the_split(self):
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stderr[-400:]
        assert "STUDY PROGRAMME" in r.stdout and "RUNWAY" in r.stdout
        assert "READ, NOT RESTATED" in r.stdout
