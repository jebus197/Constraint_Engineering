#!/usr/bin/env python3
"""The already-found check must narrow, not flood, and must be able to say nothing.

DRAFTED 2026-11-22; destination `bench/tests/`, and onto `GUARDS`.

WHY. `scripts/has_this_already_been_found_2026-11-22.py` exists because 9
findings were re-derived on 2026-11-22 that were already in the record. Its
value is entirely in being RUN, and a tool that floods is a tool that stops
being run after the second use. 2 properties carry that:

  1. EVERY term must match, not any. 1 shared word -- "gate", "pulse", "board" --
     appears in a large fraction of this repository, so an `any` search returns
     most of it and teaches the reader to ignore the output.
  2. It must be able to return NOTHING. A search that always finds something
     cannot distinguish "already done" from "not done", which is the only
     question it is asked.

★ EVERY CASE IS CONSTRUCTED. A guard reading the real `scripts/` would change
its verdict whenever a file lands, and would be guarding the repository rather
than the tool.
"""
from __future__ import annotations

import importlib.util
import os
import pathlib
import sys

import pytest


def _find_repo() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for c in [here.parent, *here.parents]:
        if (c / "bench" / "tests").is_dir() and (c / "hooks").is_dir():
            return c
    return pathlib.Path.home() / "Developer_Projects" / "Constraint_Engineering"


REPO = _find_repo()
TOOL = pathlib.Path(os.environ.get(
    "CDSFL_ALREADY_FOUND",
    REPO / "scripts" / "has_this_already_been_found_2026-11-22.py"))


@pytest.fixture(scope="module")
def mod():
    spec = importlib.util.spec_from_file_location("already_found", TOOL)
    m = importlib.util.module_from_spec(spec)
    sys.modules["already_found"] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture
def planted(tmp_path):
    """A scripts/ dir holding 1 relevant producer and 2 decoys."""
    d = tmp_path / "scripts"
    d.mkdir(parents=True)
    (d / "the_real_one.py").write_text(
        '"""The gate calls a live watchdog absent for most of every cycle."""\n'
        "# watchdog pulse freshness, measured\n")
    (d / "decoy_watchdog_only.py").write_text('"""A watchdog that does other things."""\n')
    (d / "decoy_pulse_only.py").write_text('"""A pulse writer, nothing to do with gates."""\n')
    return d


class TestItNarrowsRatherThanFloods:
    def test_every_term_must_match_not_any(self, mod, planted):
        """THE DESIGN DECISION. `watchdog` alone matches 2 of the 3 files;
        `watchdog`+`pulse` matches only the one that is actually relevant."""
        wide = mod._grep(planted, ["watchdog"], ".py")
        narrow = mod._grep(planted, ["watchdog", "pulse"], ".py")
        assert len(wide) == 2, f"the decoy setup is wrong: {sorted(p.name for p in wide)}"
        assert len(narrow) == 1, (
            f"an ALL-terms search must narrow; got {sorted(p.name for p in narrow)}")
        assert next(iter(narrow)).name == "the_real_one.py"

    def test_it_can_return_nothing(self, mod, planted):
        """ANTI-VACUITY. A search that always finds something cannot answer the
        only question it is asked."""
        assert mod._grep(planted, ["nonexistentsubjectxyz"], ".py") == {}

    def test_a_missing_directory_is_not_a_crash(self, mod, tmp_path):
        assert mod._grep(tmp_path / "does_not_exist", ["anything"], ".py") == {}

    def test_pycache_is_excluded(self, mod, planted):
        """A compiled copy would double every hit and halve the signal."""
        c = planted / "__pycache__"
        c.mkdir()
        (c / "the_real_one.py").write_text("watchdog pulse\n")
        hits = mod._grep(planted, ["watchdog", "pulse"], ".py")
        assert all("__pycache__" not in p.parts for p in hits)
        assert len(hits) == 1


class TestTheAnswerIsReadable:
    def test_it_prints_the_docstring_line_that_answers_the_question(self, mod, planted):
        """The first docstring line is usually the whole answer, so a hit that
        printed only a path would leave the reader to open every file."""
        line = mod._first_doc_line(planted / "the_real_one.py")
        assert "watchdog" in line.lower(), f"got {line!r}"
        assert not line.startswith(("#!", "#", "import", "from"))

    def test_a_file_with_no_docstring_does_not_crash(self, mod, tmp_path):
        p = tmp_path / "bare.py"
        p.write_text("#!/usr/bin/env python3\nimport os\n")
        assert mod._first_doc_line(p) == ""

    def test_an_unreadable_file_does_not_crash(self, mod, tmp_path):
        p = tmp_path / "gone.py"
        assert mod._first_doc_line(p) == ""


class TestItRefusesToDecide:
    def test_the_places_each_carry_a_meaning(self, mod):
        """A bare path tells the reader nothing about whether to stop."""
        assert mod.PLACES, "no places configured"
        for rel, meaning in mod.PLACES:
            assert len(meaning) > 20, f"{rel} has no usable meaning: {meaning!r}"

    def test_it_searches_the_producer_directory_first(self, mod):
        """Order matters: a producer is where a measurement most often already
        lives, and it was a producer that was duplicated on 2026-11-22."""
        assert mod.PLACES[0][0] == "scripts"
