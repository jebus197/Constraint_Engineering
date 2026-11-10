"""The unproduced 10-of-12 error figure must not come back.

HIS RULING, 2026-11-09, verbatim: "on C111, my verdict is retire it as you
have suggested." (He confirmed in the next message that C111 was a typo for
B111.) The figure stated that of 12 errors on 2026-10-11, 10 were catchable by
reasoning before running anything, at 0.8333 with a Wilson interval and a
binomial p of 0.0193. No script reproduced any of those 4 figures and the
denominator could not be reconstructed: that date carries 14 memory files and
which 12 the figure counted was recorded nowhere.

RETIRED UNDER `additive-standard`'s REMOVAL CLAUSE, where the named property
the replacements dominate on is REPRODUCIBILITY. What replaces it has
producers, and this file asserts those producers still exist and still run --
a removal justified by a replacement is only sound while the replacement is
reachable.
"""
from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
FILES = {
    "project": REPO / ".claude" / "CLAUDE.md",
    "global": pathlib.Path.home() / ".claude" / "CLAUDE.md",
}
REPLACEMENTS = (
    "scripts/how_many_of_the_nights_errors_were_instruments_2026-11-03.py",
    "scripts/what_caught_my_errors_2026-10-29.py",
)
#: The retired claim, in the forms it was actually written in.
ASSERTED = re.compile(
    r"Of 12 errors[^.]{0,40}2026-10-11, 10 \(0\.8333|"
    r"10 of 12 errors on 2026-10-11 were catchable")


@pytest.mark.parametrize("where", sorted(FILES))
class TestTheFigureIsNotAsserted:
    def test_it_is_not_stated_as_a_live_measurement(self, where):
        f = FILES[where]
        if not f.is_file():
            pytest.skip(f"{where} CLAUDE.md is not present on this machine")
        assert not ASSERTED.search(f.read_text(encoding="utf-8")), (
            f"the retired 10-of-12 figure is asserted again in the {where} "
            f"CLAUDE.md; he ruled it retired on 2026-11-09")

    def test_any_surviving_mention_names_it_as_retired(self, where):
        f = FILES[where]
        if not f.is_file():
            pytest.skip(f"{where} CLAUDE.md is not present on this machine")
        txt = f.read_text(encoding="utf-8")
        for m in re.finditer(r"0\.8333", txt):
            near = txt[max(0, m.start() - 700):m.start() + 200]
            assert "RETIRED" in near or "retired" in near, (
                f"0.8333 appears in the {where} CLAUDE.md without being named "
                f"as retired: ...{near[-200:]}")

    def test_the_replacements_are_cited_there(self, where):
        f = FILES[where]
        if not f.is_file():
            pytest.skip(f"{where} CLAUDE.md is not present on this machine")
        txt = f.read_text(encoding="utf-8")
        missing = [r for r in REPLACEMENTS if r.rsplit("/", 1)[-1] not in txt]
        assert not missing, (
            f"the {where} CLAUDE.md retires the figure without citing its "
            f"replacements: {missing}. A removal is only sound while the "
            f"replacement it names is reachable.")


class TestTheReplacementsAreReachable:
    """A removal justified by a replacement needs the replacement to RUN."""

    @pytest.mark.parametrize("script", REPLACEMENTS)
    def test_the_producer_exists(self, script):
        assert (REPO / script).is_file(), (
            f"{script} is cited as the replacement for a retired figure and is "
            f"not in the tree")

    @pytest.mark.parametrize("script", REPLACEMENTS)
    def test_the_producer_runs_and_prints_its_figure(self, script):
        r = subprocess.run([sys.executable, str(REPO / script)],
                           capture_output=True, text=True, cwd=str(REPO),
                           timeout=300)
        assert r.returncode == 0, (
            f"{script} exits {r.returncode}: {r.stderr[-400:]}")
        assert re.search(r"0\.\d{4}", r.stdout), (
            f"{script} printed no figure at all, so it cannot carry the "
            f"argument the retired one used to carry")
