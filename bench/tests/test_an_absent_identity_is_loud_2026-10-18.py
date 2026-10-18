#!/usr/bin/env python3
"""An identity absent from a capability table is LOUD, never silently defaulted.

ENTRY C18, SECOND CLAUSE. The panel design of 2026-10-14 ends: *"An identity
absent from the tables must be LOUD, never defaulted."* The identity itself was
built on 2026-10-17 and is guarded by
`test_capability_is_keyed_on_an_identity_not_a_name_2026-10-17.py`; THIS FILE
DELIBERATELY DOES NOT RE-TEST IT. It covers only the clause that was missing.

WHY THIS FILE EXISTS AND AN EARLIER ONE DOES NOT. A
`bench/capability_identity.py` was written on 2026-10-18 and DELETED the same
night: it reproduced `routing.capability_identity` bit for bit -- both return
`273630e1d5dc` for ("anthropic", "opus", "4-8") -- and added a second label
parse, which `routing.seat_identities` explicitly forbids in its own docstring:
*"THE REGISTRY'S `resolve_model` IS THE SOURCE, not a second parse of the
config."* Two identity functions is the producer/consumer drift this project
keeps finding, so there is one.

THE REALISED COST OF SILENCE. The runner records a panel finding of 2026-08-30
that *"Fable had no COMPOSER_MODEL_MAP entry and no .toml, so it composed to
FileNotFoundError -> 0 chars"* -- a model ran on an EMPTY SYSTEM PROMPT and
nothing said so, while 2 other seats received 6,008 and 5,559 characters.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from bench import routing as R  # noqa: E402

RUNNER = REPO / "bench" / "reference_runner_v3.py"
COMPOSER = REPO / "bench" / "cdsfl_registry" / "composer.py"


def test_a_present_key_is_returned_and_records_nothing():
    R.reset_lookup_misses()
    assert R.resolve_or_alarm({"opus": "opus.toml"}, "opus", "t",
                              default="x") == "opus.toml"
    assert R.lookup_misses() == []


def test_a_miss_still_falls_back_so_a_run_is_not_killed():
    """Raising would turn a seat composing to 0 characters into a dead run."""
    R.reset_lookup_misses()
    assert R.resolve_or_alarm({"opus": 1}, "fable", "coherence budget",
                              default=0.015) == 0.015
    assert len(R.lookup_misses()) == 1


def test_the_announcement_carries_the_table_and_the_SHARED_identity():
    """The digest must be the one capability decisions use, not a second parse.

    An announcement keyed on a different digest from the decision it describes
    would be worse than no announcement: a reader would chase 2 identities for
    1 model.
    """
    R.reset_lookup_misses()
    said: list = []
    R.resolve_or_alarm({"opus": 1}, "fable", "coherence budget",
                       default=0.015, log=said.append)
    assert said, "a miss that announces nothing is the defect, not the fix"
    assert "coherence budget" in said[0], "the announcement must name the TABLE"
    assert "fable" in said[0]
    shared = R.capability_identity("", "fable", "")
    assert shared in said[0], (
        "the announcement must carry the identity from `capability_identity`")
    assert R.lookup_misses()[0]["identity"] == shared


def test_a_repeated_miss_is_recorded_every_time_and_announced_once():
    """The composer runs once per seat per round: 20 rounds x 6 seats = 120."""
    R.reset_lookup_misses()
    said: list = []
    for _ in range(5):
        R.resolve_or_alarm({"opus": 1}, "fable", "coherence budget",
                           default=0.015, log=said.append)
    assert len(R.lookup_misses()) == 5, "the count must survive deduplication"
    assert len(said) == 1
    R.resolve_or_alarm({"opus": 1}, "sonnet", "coherence budget",
                       default=0.015, log=said.append)
    assert len(said) == 2, "a DIFFERENT identity must announce again"


def test_the_named_defect_reproduces_on_the_live_phenotype_table():
    """`Fable -> no entry, silently inheriting the 8,000 default`, EXECUTED."""
    from bench.cdsfl_registry import composer as C
    R.reset_lookup_misses()
    opus = R.resolve_or_alarm(C.PHENOTYPE_TRANSFORMS, "opus_4_6",
                              "phenotype transform",
                              default=C.PhenotypeTransform())
    fable = R.resolve_or_alarm(C.PHENOTYPE_TRANSFORMS, "fable",
                               "phenotype transform",
                               default=C.PhenotypeTransform())
    assert "opus_4_6" in C.PHENOTYPE_TRANSFORMS
    assert opus.max_directive_chars == 12000, "re-measure: the entry has moved"
    assert "fable" not in C.PHENOTYPE_TRANSFORMS, (
        "fable now HAS a phenotype entry -- the defect is fixed at source and "
        "this test should record that rather than be deleted")
    assert fable.max_directive_chars == 8000
    assert len(R.lookup_misses()) == 1


@pytest.mark.parametrize("path,table", [
    (COMPOSER, "PHENOTYPE_TRANSFORMS"),
    (COMPOSER, "MODEL_COHERENCE_BUDGETS"),
    (RUNNER, "COMPOSER_MODEL_MAP"),
])
def test_the_named_table_is_no_longer_read_by_a_bare_get(path, table):
    """STRUCTURAL: a comment mentioning `.get` does not trip it."""
    tree = ast.parse(path.read_text(errors="ignore"))
    bare = [n.lineno for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "get" and isinstance(n.func.value, ast.Name)
            and n.func.value.id == table and len(n.args) >= 2]
    assert bare == [], (
        f"{table} is still read by a bare .get with a default at line(s) {bare} "
        f"in {path.name}: a missing identity would be silently defaulted")
    assert [n for n in ast.walk(tree)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
            and n.func.attr == "resolve_or_alarm"], (
        f"{path.name} never calls resolve_or_alarm, so no lookup in it is loud")


def test_there_is_exactly_one_identity_function_in_the_tree():
    """A duplicate is not additive, and one was written and deleted tonight."""
    dupes = sorted(p.relative_to(REPO) for p in (REPO / "bench").rglob("*.py")
                   if "logs" not in p.parts
                   and p.name == "capability_identity.py")
    assert dupes == [], (
        f"a second capability-identity module exists at {dupes}: "
        f"`routing.capability_identity` is the one every decision uses, and 2 "
        f"identity functions is the producer/consumer drift to avoid")


def test_the_misses_reach_the_run_report():
    """An addition nothing reaches is not additive."""
    tree = ast.parse(RUNNER.read_text(errors="ignore"))
    writes = [n for n in ast.walk(tree) if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Subscript)
                      and isinstance(t.slice, ast.Constant)
                      and t.slice.value == "capability_lookup_misses"
                      for t in n.targets)]
    assert writes, "nothing assigns `capability_lookup_misses` into the report"
    parents: dict = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parents[child] = node

    def _blk(n):
        cur = n
        while cur in parents:
            cur = parents[cur]
            if isinstance(cur, (ast.Try, ast.FunctionDef)):
                return cur
        return None

    real = [w.lineno for w in writes
            if (b := _blk(w)) is not None
            and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                    and c.func.attr == "lookup_misses" for c in ast.walk(b))]
    assert real, (
        "no write sits in a block that reads the miss ledger, so on a clean run "
        "the report would carry no record at all")
