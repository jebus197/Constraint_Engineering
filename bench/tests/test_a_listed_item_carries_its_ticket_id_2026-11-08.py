"""B132: the report generator must refuse to list an item with no ticket id.

HIS ENTRY'S WORDS: "the report generator must REFUSE, as it already refuses
with exit 3 when a live item has no authored entry, if it lists an item without
the ticket id the store issued for it -- a postcondition cannot be forgotten,
and a resolution to remember can. A guard and a reversal check are owed with
it."

THE SCOPE IS THE WHOLE DESIGN, and it was measured before the refusal was
written. Of 48 derived items, 40 come from the task list and all 40 carry a
ticket id; 8 come from STUDY_IN_FLIGHT.json and none does, because the store
issues ids for tickets and a study defect is not one. An unscoped refusal would
fire on those 8 and withhold his morning report, which is the opposite of what
B96 settled.

IT IS VACUOUS ON TODAY'S DATA BY DESIGN. 40 of 40 carry an id, so the refusal
fires on nothing. The anti-vacuity tests below prove the predicate CAN fire, so
the guard is not merely passing because it decides nothing -- the failure this
project has recorded repeatedly.
"""
from __future__ import annotations

import ast
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
BUILDER = REPO / "scripts" / "morning_report_build_2026-10-12.py"


@pytest.fixture(scope="module")
def M():
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("mrb_b132", BUILDER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["mrb_b132"] = m
    spec.loader.exec_module(m)
    return m


class TestTheKeySpellingCannotRegress:
    """The defect that made the FIRST measurement of this read 48 of 48."""

    def test_a_store_key_is_stripped_to_its_identifier(self, M):
        assert M._bare_ident("task:B20") == "B20"
        assert M._bare_ident("defect:some-slug") == "some-slug"
        assert M._bare_ident("B20") == "B20", (
            "a bare identifier must pass through unchanged, or every caller "
            "that already holds one breaks")

    def test_the_two_spellings_really_do_differ_at_the_store(self, M):
        """ANTI-VACUITY for the helper: if they agreed, it would be pointless."""
        bare = M.ticket_id("B20")
        keyed = M.ticket_id("task:B20")
        assert bare, "B20 has no ticket id at all; this test's premise is gone"
        assert not keyed, (
            "ticket_id now accepts a store key, so `_bare_ident` is no longer "
            "load-bearing -- check whether the store changed before deleting it")


class TestThePredicateCanFire:
    """ANTI-VACUITY. A refusal that cannot fire guards nothing."""

    def test_a_ticketed_item_with_no_id_is_reported(self, M):
        made_up = [{"key": "task:ZZ999"}]
        assert M.items_missing_a_ticket_id(made_up) == ["task:ZZ999"]

    def test_a_study_defect_is_exempt(self, M):
        """The scope: the store issues no id for a study defect."""
        assert M.items_missing_a_ticket_id(
            [{"key": "defect:no-such-defect-anywhere"}]) == []

    def test_an_item_with_no_key_is_ignored_rather_than_crashing(self, M):
        assert M.items_missing_a_ticket_id([{}, {"key": ""}]) == []

    def test_a_real_ticketed_item_passes(self, M):
        assert M.items_missing_a_ticket_id([{"key": "task:B20"}]) == []

    def test_an_UNCLASSIFIED_source_is_reported_not_skipped(self, M):
        """An exemption must be a DECISION, never an accident.

        The scope test is a `startswith`, so a key with an unrecognised prefix
        would otherwise be skipped silently and its missing id never reported.
        0 such keys exist today -- 40 `task:` and 8 `defect:` -- which is
        exactly why this is guarded: a 0 nobody counts is the shape this
        project records as asking what a 0 is a 0 OF.
        """
        out = M.items_missing_a_ticket_id([{"key": "newsource:thing"}])
        assert len(out) == 1, out
        assert "UNCLASSIFIED SOURCE" in out[0], out[0]

    def test_a_bare_key_with_no_prefix_is_also_reported(self, M):
        out = M.items_missing_a_ticket_id([{"key": "B20"}])
        assert len(out) == 1 and "UNCLASSIFIED SOURCE" in out[0], out

    def test_the_live_population_carries_no_unclassified_source(self, M):
        items = M.task_items() + M.study_items()
        bad = [x for x in M.items_missing_a_ticket_id(items)
               if "UNCLASSIFIED SOURCE" in x]
        assert bad == [], (
            "a derived item carries a source prefix nothing has classified, so "
            "nothing decided whether it owes a ticket id:\n  "
            + "\n  ".join(bad))


class TestTheLivePopulationHolds:

    def test_no_task_item_is_missing_its_ticket_id(self, M):
        items = M.task_items() + M.study_items()
        bad = M.items_missing_a_ticket_id(items)
        assert bad == [], (
            "these task items would be listed to him with no ticket id, so a "
            "code would reach him with nowhere to look it up:\n  "
            + "\n  ".join(bad))

    def test_the_exempt_class_is_not_empty_so_the_scope_matters(self, M):
        """If nothing were exempt, scoping would be dead code."""
        items = M.task_items() + M.study_items()
        exempt = [i for i in items
                  if not (i.get("key") or "").startswith(M._TICKETED_SOURCES)]
        assert exempt, (
            "nothing is exempt from the ticket-id requirement any more, so the "
            "scope in `items_missing_a_ticket_id` decides nothing. Either the "
            "study items gained ids or they left the population.")


class TestTheGeneratorActuallyConsultsIt:
    """STRUCTURAL, because running the generator writes files and takes time.

    An AST check rather than a substring: a text match cannot follow a call
    when it moves, and this project has 4 recorded defects found by executing
    2 forms against each other and 0 found by reading.
    """

    def test_main_calls_the_postcondition(self):
        tree = ast.parse(BUILDER.read_text(encoding="utf-8"))
        main = next((n for n in ast.walk(tree)
                     if isinstance(n, ast.FunctionDef) and n.name == "main"), None)
        assert main is not None, "main() is gone from the generator"
        called = {getattr(c.func, "id", None) for c in ast.walk(main)
                  if isinstance(c, ast.Call)}
        assert "items_missing_a_ticket_id" in called, (
            "main() no longer calls the postcondition, so an item could be "
            "listed with no ticket id and nothing would refuse")

    def test_it_returns_3_like_its_sibling_refusal(self):
        """The entry asks for the SAME exit code the authored-detail check uses.

        ★ THE WINDOW IS BOUNDED BY THE NEXT REFUSAL, corrected 2026-11-08. The
        first version took a fixed 1,200 characters from the call site, which
        reaches PAST this block into the authored-detail refusal and picks up
        ITS `return 3`. So changing this block's exit code to 0 left the test
        green -- caught by the mutation harness, which is the only reason it is
        not still vacuous. A window must end where the thing it describes ends.
        """
        src = BUILDER.read_text(encoding="utf-8")
        i = src.index("items_missing_a_ticket_id(items)")
        end = src.index("if missing or orphan:", i)
        window = src[i:end]
        assert "return 3" in window, (
            "the ticket-id refusal does not return 3 inside its OWN block (the "
            "window ends at the next refusal, so a neighbour's exit code "
            "cannot satisfy it); the entry asks for the same code as the "
            "authored-detail refusal")
        assert window.count("return ") == 1, (
            f"the bounded window holds {window.count('return ')} return "
            f"statements; it should hold exactly this block's, or the "
            f"assertion above can be satisfied by the wrong one")
