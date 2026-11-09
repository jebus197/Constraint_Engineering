"""GUARD for scripts/the_refuted_rate_upper_bound_was_wrong_2026-11-09.py.

WHAT IT PROTECTS. A Wilson upper bound of 0.022696 for 2 of 319 was stated in 6
places across 5 live files. The true value is 0.022568. The figure had NO
producer -- it lived as prose in 4 documents and as a string literal in a
script -- so correcting it in prose alone would have left
`measured-rate-travels-with-its-script` violated identically.

THE 2 LOAD-BEARING TESTS ARE THE ONES THAT CAN FAIL FOR THE RIGHT REASON.

  1. ANTI-VACUITY. A detector reporting 0 wrong surfaces because it detects
     nothing is indistinguishable from one reporting 0 because nothing is
     wrong. `test_the_detector_can_see_a_wrong_value` writes the old value into
     a temporary copy and requires the producer's own predicate to report it.

  2. THE ARCHIVE MUST STAY DIRTY. 12 files under bench/logs/ carry the original
     value inside harvested seat output. That is correct and must remain so: a
     later pass that "finishes the job" by sweeping the archive would falsify
     records of what a model produced on a date. Asserting the archive still
     carries it is the only thing standing between this correction and that.
"""
from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import tempfile

import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PROD = (REPO / "scripts"
        / "the_refuted_rate_upper_bound_was_wrong_2026-11-09.py")
WRONG = "0.022696"
RIGHT = 0.022567848669


@pytest.fixture(scope="module")
def mod():
    assert PROD.is_file(), f"the corrected figure has no producer: {PROD}"
    spec = importlib.util.spec_from_file_location("_refuted_rate", PROD)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_refuted_rate"] = m
    spec.loader.exec_module(m)
    return m


class TestTheArithmetic:
    def test_four_routes_agree(self, mod):
        routes = mod.wilson_four_routes(mod.K, mod.N)
        assert len(routes) == 4, sorted(routes)
        his = [v[1] for v in routes.values()]
        assert max(his) - min(his) < 1e-12, routes
        assert abs(his[0] - RIGHT) < 5e-9, (his[0], RIGHT)

    def test_the_lower_bound_was_never_wrong(self, mod):
        """Only the UPPER was affected; the stated 0.001720 is correct."""
        lo = mod.wilson_four_routes(mod.K, mod.N)["statsmodels"][0]
        assert abs(lo - 0.001721035570) < 5e-9, lo
        assert f"{lo:.6f}" == "0.001721"

    def test_the_clopper_pearson_beside_it_was_already_right(self, mod):
        cp = mod.clopper_pearson(mod.K, mod.N)
        assert abs(cp[0] - 0.000760) < 5e-6, cp
        assert abs(cp[1] - 0.022463) < 5e-6, cp

    def test_the_stated_value_is_no_construction_at_a_sane_level(self, mod):
        """It is not a method choice, so it cannot be defended as one.

        Every row but the implied-z row must MISS, and the implied-z row
        exists to name the absurd level the stated value would require.
        """
        rows = mod.ruled_out(mod.K, mod.N, float(WRONG))
        matches = [r for r in rows if r[2]]
        assert len(matches) == 1, [r[0] for r in matches]
        assert "implied z" in matches[0][0], matches[0][0]
        assert len(rows) >= 11, len(rows)

    def test_the_error_is_in_the_conservative_direction(self, mod):
        """A WIDER stated interval overstates uncertainty, so no downstream
        conclusion was made over-confident. If this ever flips, the finding's
        severity changes and the prose saying so becomes wrong."""
        assert float(WRONG) > RIGHT, (WRONG, RIGHT)


class TestTheLiveSurfaces:
    def test_no_live_surface_states_the_wrong_value(self, mod):
        bad = [(rel, n) for rel, exists, n in mod.live_state() if n or not exists]
        assert not bad, f"still carrying {WRONG} or missing: {bad}"

    def test_the_live_list_is_not_empty_and_every_path_exists(self, mod):
        state = mod.live_state()
        assert len(state) >= 5, state
        missing = [rel for rel, exists, _ in state if not exists]
        assert not missing, missing

    def test_the_corrected_value_is_actually_present(self):
        """ANTI-VACUITY for the replacement: absence of the wrong value could
        also mean the sentence was deleted."""
        for rel in ("resources/RECOVERY.md",
                    "experimental_notes/CDSFL_MASTER_TASK_LIST.md"):
            txt = (REPO / rel).read_text(errors="replace")
            assert "0.022568" in txt, f"{rel} lost the corrected figure"
            assert "2 of 319" in txt or "319 findings" in txt, rel


class TestTheDetectorIsNotVacuous:
    def test_the_detector_can_see_a_wrong_value(self, mod, tmp_path,
                                                monkeypatch):
        """THE LOAD-BEARING TEST. Point the producer at a tree whose copy of a
        live surface still carries the old value, and require it to say so."""
        fake = tmp_path / "repo"
        for rel in mod.LIVE:
            p = fake / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("Wilson [0.001720, 0.022696].\n", encoding="utf-8")
        monkeypatch.setattr(mod, "REPO", fake)
        state = mod.live_state()
        assert all(exists for _, exists, _ in state), state
        assert all(n == 1 for _, _, n in state), state
        assert sum(n for _, _, n in state) == len(mod.LIVE)

    def test_a_missing_surface_is_reported_not_skipped(self, mod, tmp_path,
                                                       monkeypatch):
        """A path that has moved must read as MISSING rather than as clean --
        a grep verdict cannot see its subject removed."""
        monkeypatch.setattr(mod, "REPO", tmp_path / "empty")
        state = mod.live_state()
        assert all(not exists for _, exists, _ in state), state


class TestTheArchiveStaysVerbatim:
    def test_the_archive_still_carries_the_original_value(self, mod):
        """DELIBERATE. Harvested seat output records what a model produced on a
        date. Sweeping it would falsify the record, and the repository's own
        count/interval guard skips harvested seat files for the same reason.
        A FLOOR, not an equality: the archive grows."""
        n = mod.archived_count()
        assert n >= 1, (
            "0 archived files carry the original value. Either the archive was "
            "swept -- which falsifies records of what a seat produced -- or "
            "bench/logs is absent from this checkout")

    def test_the_producer_names_the_archive_as_deliberate(self):
        """So a later reader cannot mistake it for work left undone."""
        src = PROD.read_text(errors="replace")
        assert "Left deliberately" in src, (
            "the producer no longer says the archive is untouched on purpose")


class TestItRuns:
    def test_it_exits_zero_and_reaches_a_verdict(self):
        r = subprocess.run([sys.executable, str(PROD)], capture_output=True,
                           text=True, cwd=str(REPO), timeout=600)
        assert r.returncode == 0, r.stdout[-1500:] + r.stderr[-1500:]
        assert "VERDICT:" in r.stdout
        assert "0.022568" in r.stdout
        assert "WHAT THIS SUPPORTS AND WHAT IT DOES NOT" in r.stdout

    def test_it_fails_loudly_if_a_live_surface_regresses(self, tmp_path):
        """EXECUTED. Re-point the producer's REPO at a tree carrying the old
        value and require a NON-ZERO exit, so the check can actually refuse."""
        fake = tmp_path / "repo"
        (fake / "scripts").mkdir(parents=True)
        (fake / "bench" / "logs").mkdir(parents=True)
        spec = importlib.util.spec_from_file_location("_rr_fail", PROD)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        m.REPO = fake
        for rel in m.LIVE:
            p = fake / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("Wilson [0.001720, 0.022696].\n", encoding="utf-8")
        with tempfile.TemporaryDirectory():
            code = m.main()
        assert code != 0, (
            "the producer exited 0 while every live surface still carried the "
            "wrong value, so it cannot refuse anything")
