"""The ranking mechanism may not carry the terminology he rejected.

HIS REJECTION, 2026-10-09, verbatim: *"we shouldn't have our code littered with
football references... or even 'leagues', as such"*, with *"in reality there
should probably be no distinction between models participating in an experiment
other than a 'ranking number'"*. Task C21 records that the rejection itself was
never written down anywhere, so nothing held it.

MEASURED BY AST, so a comment quoting him is not mistaken for code he objected
to: the ranking mechanism -- `bench/routing.py`,
`bench/reference_runner_v3.py`, `bench/runner_core.py` -- carries **0** of the
terms. It names things `strength_order`, `capability_identity` and
`season_strength_order`.

THE OTHER 28 HITS IN THE LIVE HARNESS ARE ACCOUNTED FOR, 9 plus 6 plus 13:
9 are `ZeroDivisionError`, a Python builtin caught by "division"; 6 are `player`
or `player_manager` as a ROLE NAME, predating the ladder discussion and present
inside ARCHIVED PROMPTS, so renaming them would edit the record of runs already
performed and is his call; and 13 quote or analyse his own football analogy in
the 2026-10-08 producers, where renaming would erase what was measured.

A CRUDE SUBSTRING SCAN WAS TRIED FIRST, which is why this uses the AST. It
reported 190 hits for "promot" -- the project's own SHADOW PROMOTION -- 64 for
"division", mostly arithmetic, and 25 for "fixture", which is pytest.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = (REPO / "scripts"
            / "is_the_ladder_littered_with_football_2026-10-17.py")


@pytest.fixture(scope="module")
def probe():
    sys.path.insert(0, str(REPO / "scripts"))
    sys.path.insert(0, str(REPO))
    spec = importlib.util.spec_from_file_location("football_probe", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["football_probe"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_the_ranking_mechanism_is_clean(probe):
    """THE RATCHET. A football word in the ranking code is a regression."""
    rows = probe.hits()
    in_ranking = [h for h in rows
                  if h[1].split("/")[-1] in probe.RANKING_MECHANISM]
    assert not in_ranking, (
        "his 2026-10-09 rejection is breached in the code that decides a "
        "model's rank:\n"
        + "\n".join(f"    {r[1]}:{r[2]}  {r[0]} {r[3]!r}" for r in in_ranking))


def test_the_detector_can_still_see(probe, monkeypatch, tmp_path):
    """ANTI-VACUITY on a planted file, not on the live tree being dirty."""
    planted = tmp_path / "routing.py"
    planted.write_text("league_table = {}\n", encoding="utf-8")
    real = probe._live_python
    monkeypatch.setattr(
        probe, "_live_python",
        lambda: list(real()) + [(planted, "bench/routing.py")])
    rows = probe.hits()
    assert any(r[3] == "league_table" for r in rows), (
        "a planted `league_table` in the ranking mechanism was not seen, so a "
        "real one would pass too")


def test_the_term_list_names_what_he_named(probe):
    """A detector whose pattern has been narrowed stops holding the ruling."""
    for word in ("league", "relegation", "football", "division"):
        assert probe.TERMS.search(word), f"{word} is no longer matched"
    assert probe.RANKING_MECHANISM, "the ranking file list is empty"
    for f in ("routing.py", "reference_runner_v3.py", "runner_core.py"):
        assert f in probe.RANKING_MECHANISM


def test_the_ranking_mechanism_files_exist(probe):
    """A file list naming nothing on disk would pass vacuously."""
    scanned = {rel.split("/")[-1] for _, rel in probe._live_python()}
    for f in probe.RANKING_MECHANISM:
        assert f in scanned, f"{f} is not in the live scan, so it is unchecked"
