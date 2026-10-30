#!/usr/bin/env python3
"""One module object under both names, so the capability miss ledger cannot split.

THE DEFECT, OBSERVED RATHER THAN PREDICTED, 2026-10-29. `bench/routing.py` is
importable as `routing` (with `bench/` on the path) and as `bench.routing` (with
the repository root on it). Python treats those as 2 different modules and gives
each its own `_LOOKUP_MISSES` list. Every live caller uses the same dual-path
form -- `from bench import routing` first, falling back to `import routing` --
which looks safe and is not: which branch wins depends on what is importable AT
THAT MOMENT, so 2 modules in 1 process can resolve differently.

IT HAPPENED. Running `scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py`
as a script, `reference_runner_v3` bound the TOP-LEVEL module while the script
bound `bench.routing`. `describe_model` recorded its miss in one ledger and the
reader asked the other, which reported 0 and classified an ANNOUNCED default as
SILENT. **The announcement was made and nobody could hear it**, which is worse
than not making it, because the instrument then reports working code as
defective. With the alias in place the same script reports 1 silent step of 10
instead of 5.

WHY AN ALIAS AND NOT A CONVENTION. Asking every caller to import it the same way
is the arrangement that just failed, and a convention nothing enforces is not a
mechanism.
"""
from __future__ import annotations

import importlib
import pathlib
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
for extra in (REPO, REPO / "bench"):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))


class TestBothNamesAreOneObject:
    def test_the_two_names_resolve_to_the_same_module(self):
        top = importlib.import_module("routing")
        pkg = importlib.import_module("bench.routing")
        assert top is pkg, (
            "routing and bench.routing are different module objects, so a miss "
            "recorded by one is invisible to the other")

    def test_they_share_one_ledger_list(self):
        """Identity of the LIST, not equality: 2 empty lists compare equal."""
        top = importlib.import_module("routing")
        pkg = importlib.import_module("bench.routing")
        assert top._LOOKUP_MISSES is pkg._LOOKUP_MISSES

    def test_a_miss_recorded_under_one_name_is_visible_under_the_other(self):
        """The property itself, exercised rather than inferred from identity."""
        top = importlib.import_module("routing")
        pkg = importlib.import_module("bench.routing")
        top.reset_lookup_misses()
        top.resolve_or_alarm({}, "AbsentModelForThisTest", "a test lookup",
                             default="fallback")
        assert len(pkg.lookup_misses()) == 1, (
            "a miss recorded through one name was not visible through the other")
        top.reset_lookup_misses()

    def test_the_reporter_says_it_is_shared(self):
        top = importlib.import_module("routing")
        shared, detail = top.ledger_is_shared()
        assert shared, detail


class TestTheAliasIsSafe:
    def test_it_does_not_overwrite_a_different_module(self, monkeypatch):
        """A DIFFERENT object already under the other name must be left alone.

        Overwriting would hide a real conflict and could swap a module under
        code already holding a reference to it. The condition is REPORTED by
        `ledger_is_shared` instead.
        """
        top = importlib.import_module("routing")
        sentinel = object()
        monkeypatch.setitem(sys.modules, "bench.routing", sentinel)
        top._register_under_both_names()
        assert sys.modules["bench.routing"] is sentinel, (
            "the alias overwrote a different module registered under that name")
        shared, detail = top.ledger_is_shared()
        assert not shared and "SPLIT LEDGER" in detail, detail

    def test_it_is_idempotent(self):
        top = importlib.import_module("routing")
        before = sys.modules.get("bench.routing")
        top._register_under_both_names()
        top._register_under_both_names()
        assert sys.modules.get("bench.routing") is before


class TestTheCaseThatFailedNowPasses:
    def test_the_producer_run_as_a_script_sees_the_announcements(self):
        """END TO END, as a SCRIPT, because that is the context that failed.

        Run in-process the producer already reported ANNOUNCED; only as a script
        did the ledgers split. So this invokes it the way the failure occurred.
        """
        prod = REPO / "scripts" / "how_many_places_must_change_to_add_a_model_2026-10-16.py"
        if not prod.is_file():
            pytest.skip(f"producer absent: {prod}")
        r = subprocess.run([sys.executable, str(prod), "--json"],
                           capture_output=True, text=True, cwd=str(REPO),
                           timeout=600)
        assert r.returncode == 0, r.stderr[-400:]
        import json
        steps = json.loads(r.stdout)["method_b"]["steps"]
        roster = [s for s in steps if s["step"].startswith("roster description")]
        assert roster, "the roster-description step is gone from the producer"
        assert roster[0]["outcome"] == "ANNOUNCED DEFAULT", (
            f"the roster description reads {roster[0]['outcome']!r} when run as a "
            f"script, which is the split-ledger symptom this file guards")
        silent = [s for s in steps if "SILENT DEFAULT" in s["outcome"]]
        assert not silent, (
            f"{len(silent)} step(s) still report SILENT DEFAULT: "
            f"{[s['step'] for s in silent]}")


def test_the_alias_also_sets_the_attribute_on_the_parent_package():
    """A DOTTED NAME RESOLVES BY ATTRIBUTE TRAVERSAL, NOT BY `sys.modules`.

    ★ ADDED 2026-10-30, after the aliasing fix in this file's subject was found
    to have broken a test it had nothing to do with.

    THE DEFECT. `_register_under_both_names` put the one module object into
    `sys.modules` under both names and stopped there. A real import also sets the
    submodule as an ATTRIBUTE of its parent package, and `monkeypatch.setattr`
    with a dotted string target resolves by that attribute, not by reading
    `sys.modules`. So `monkeypatch.setattr("bench.routing.route", ...)` raised
    `AttributeError: 'module' object at bench.routing has no attribute 'routing'`
    and `test_the_ladder_order_is_measured_not_a_vendor_tuple_2026-10-17.py` went
    red -- whenever the aliasing path happened to be the FIRST importer.

    WHY A 13,465-TEST BOARD PASSED IT ANYWAY, which is the lesson worth keeping:
    ORDER DEPENDENCE. Somewhere in a full board an earlier test imports
    `bench.routing` conventionally and the import machinery sets the attribute
    itself, so the ladder test passed on luck of ordering. Run on its own it
    failed in 1.02 s. A board's green is not evidence that a test passes, and
    this project already records that a flaky guard is worse than a red one.

    THE PROPERTY, asserted rather than the implementation: whichever name reached
    this module first, `bench.routing` must be reachable by attribute traversal
    and must be the SAME object as the top-level name. That is exactly what a
    dotted monkeypatch target needs, so a future change that satisfies
    `sys.modules` alone fails here.
    """
    import bench
    top = sys.modules.get("routing")
    pkg = sys.modules.get("bench.routing")
    assert top is not None or pkg is not None, "neither name is imported at all"

    attr = getattr(bench, "routing", None)
    assert attr is not None, (
        "`bench` has no `routing` attribute, so a dotted target like "
        "\"bench.routing.route\" cannot be resolved by attribute traversal and "
        "every monkeypatch using one raises AttributeError")
    for name, mod in (("routing", top), ("bench.routing", pkg)):
        if mod is not None:
            assert attr is mod, (
                f"`bench.routing` as an ATTRIBUTE is a different object from "
                f"sys.modules[{name!r}]; a patch applied through one would be "
                f"invisible to code holding the other")

    #: AND THE DOTTED PATCH ITSELF, exercised rather than reasoned about, because
    #: the attribute being present is the means and the patch working is the end.
    import bench.routing as _br
    sentinel = object()
    saved = getattr(_br, "route", None)
    try:
        setattr(sys.modules["bench.routing"], "route", sentinel)
        resolved = getattr(getattr(bench, "routing"), "route")
        assert resolved is sentinel, (
            "a value set on sys.modules['bench.routing'] is not visible through "
            "attribute traversal from `bench`, so the 2 paths disagree")
    finally:
        if saved is not None:
            setattr(sys.modules["bench.routing"], "route", saved)
