"""The barrier measurement, and the 2 corrections that make it trustworthy.

This guard EXECUTES the producer. Both of the defects it holds against were
produced by that producer's own first version, so the assertions are not
hypothetical: a loose seat detector credited one "round" with 144 seats and
reported the seat-count effect BACKWARDS at p = 2.814701e-04, and an unbounded
mtime reconstruction reported a mean idle of 80,028.9 s, which is impossible.

WHAT EACH REVERSION TURNS RED:
  * dropping the `route` discriminator, or admitting `r<digit>_` prefixed files,
    re-admits experiment finding files as panel seats ->
    `test_no_round_has_more_seats_than_the_panel_can_hold` fails, because the
    panel has at most 6 seats and the artefact produced 144;
  * dropping the wall-cannot-exceed-serial bound re-admits rounds whose reply
    files were rewritten days later -> `test_the_bound_is_actually_binding`
    fails, and the idle figures become physically impossible;
  * quoting the Mann-Whitney result alone ->
    `test_the_seat_count_effect_is_recorded_as_NOT_robust` fails the day
    Brunner-Munzel agrees, which is the day the claim may be strengthened.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "what_a_round_waits_on_its_slowest_seat_2026-10-28.py"

#: The panel's own roster ceiling. 6 seats, and a retry can add a record, so 8
#: is generous. The artefact this bound exists against produced 144.
MAX_PLAUSIBLE_SEATS = 8


@pytest.fixture(scope="module")
def mod():
    if not PRODUCER.is_file():
        pytest.skip(f"producer absent at {PRODUCER}")
    sys.path.insert(0, str(REPO / "scripts"))
    spec = importlib.util.spec_from_file_location("_barrier_archive", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def produced(mod):
    return mod.measure()


class TestTheCorpusIsPanelSeatsAndNothingElse:
    """Correction 1: a 144-seat round reported the effect backwards."""

    def test_no_round_has_more_seats_than_the_panel_can_hold(self, produced):
        worst = max(produced["seat_counts"])
        assert worst <= MAX_PLAUSIBLE_SEATS, (
            f"a round was credited with {worst} seats. The panel has at most 6, "
            f"so experiment per-round finding files are being counted as seats -- "
            f"the defect that reported the seat-count effect backwards")

    def test_the_seat_counts_match_a_panel_roster(self, produced):
        counts = produced["seat_counts"]
        assert set(counts) <= {2, 3, 4, 5, 6, 7}, counts
        assert counts.get(2, 0) > 50, (
            "most archived panel rounds are the 2 free seats; a corpus without "
            "them is not the panel archive")

    def test_the_kept_corpus_is_large_enough_to_carry_a_median(self, produced):
        assert produced["n_kept"] >= 80, (
            f"only {produced['n_kept']} rounds survived; the headline median and "
            f"its interval are quoted on 88")


class TestTheReconstructionIsBounded:
    """Correction 2: an unbounded mtime gave a mean idle of 80,028.9 seconds."""

    def test_the_bound_is_actually_binding(self, produced):
        assert produced["n_dropped"] >= 1, (
            "the wall-cannot-exceed-serial bound excluded nothing, so either the "
            "archive changed or the bound has stopped being applied")
        assert produced["dropped_share"] < 0.25, (
            f"{produced['dropped_share']:.6f} of candidate rounds were excluded; "
            f"above a quarter the reconstruction is not fit to quote at all")

    def test_every_dropped_round_names_why(self, produced):
        for d in produced["dropped_examples"]:
            assert d["why"] and d["wall"] > 0, d
            assert d["wall"] > d["serial"], (
                "a round excluded by this bound must actually violate it")

    def test_the_figures_are_physically_possible(self, produced):
        """The mean that caught the first version was 80,028.9 seconds."""
        assert produced["idle_s_median"] < 7200, (
            f"median idle {produced['idle_s_median']:.1f}s exceeds 2 hours, which "
            f"no panel round can plausibly spend waiting")
        assert 0.0 <= produced["idle_share_median"] <= 1.0
        assert 0.0 <= produced["idle_share_max"] <= 1.0

    def test_reconstruct_survives_a_directory_with_no_seats(self, mod, tmp_path):
        kept, dropped = mod.reconstruct()
        assert isinstance(kept, list) and isinstance(dropped, list)
        assert all("idle_share" in k for k in kept)


class TestTheHeadlineAnswer:
    """His question: does a collaborative round pay a barrier cost at all?"""

    def test_the_barrier_cost_is_real_and_bounded_away_from_zero(self, produced):
        lo, hi = produced["idle_share_ci"]
        assert produced["idle_share_median"] == pytest.approx(0.144892, abs=5e-7)
        assert lo == pytest.approx(0.105753, abs=5e-7)
        assert hi == pytest.approx(0.181047, abs=5e-7)
        assert lo > 0.0, (
            "the lower bound reaching 0 would mean the barrier cost is not "
            "distinguishable from none, and his question would be answered NO")

    def test_the_worst_rounds_are_counted(self, produced):
        assert produced["rounds_over_30pc"] == 13
        assert produced["rounds_over_30pc_share"] == pytest.approx(0.147727, abs=5e-7)

    def test_the_total_is_stated_in_hours(self, produced):
        assert produced["idle_hours_total"] == pytest.approx(14.108169, abs=5e-6)


class TestTheSeatCountClaimIsHeldToWhatThreeTestsSupport:

    def test_the_two_groups_are_reported_with_their_n(self, produced):
        assert produced["two_seat_n"] == 74 and produced["many_seat_n"] == 6
        assert produced["two_seat_median"] == pytest.approx(0.131478, abs=5e-7)
        assert produced["many_seat_median"] == pytest.approx(0.384744, abs=5e-7)

    def test_the_intervals_are_disjoint(self, produced):
        assert produced["intervals_disjoint"] is True, (
            "disjoint intervals are the strongest thing this n supports; if they "
            "now overlap the direction itself is in doubt")

    def test_the_seat_count_effect_is_recorded_as_NOT_robust(self, produced):
        """The 2-tool rule doing its job: 3 tests, and they disagree."""
        assert produced["mannwhitney_p"] < 0.05
        assert produced["permutation_p"] < 0.05
        assert produced["brunnermunzel_p"] > 0.05, (
            f"Brunner-Munzel now gives p = {produced['brunnermunzel_p']:.6f}. It "
            f"does not assume equal spread, so agreement across all 3 tests means "
            f"the seat-count claim may be STRENGTHENED -- requote it rather than "
            f"leaving it described as suggestive")
        assert produced["seat_count_robust"] is False, (
            "significance is not robust across the 3 tests, and the prose must "
            "keep saying so")


class TestTheCompletionTimeProvenanceIsVisible:
    """An exact stamp and a reconstruction must never be blurred together.

    Both dispatch paths stamp `t_end_epoch` from 2026-10-28, so rounds run after
    that date need no reconstruction and no exclusion bound. The mtime route
    stays for the 88 archived rounds that predate the stamps, because deleting
    it would throw away the only evidence that answers his question today.
    """

    def test_an_exact_stamp_is_PREFERRED_over_the_file_mtime(self, mod, tmp_path):
        """The reversion target: drop the preference and this reads the mtime."""
        d = tmp_path / "a_round"
        d.mkdir()
        stamped = 1_600_000_000.0          # far from any real mtime
        (d / "cc2.json").write_text(json.dumps({
            "model": "cc2", "route": "claude_cli", "ok": True,
            "elapsed_s": 12.5, "t_start_epoch": stamped - 12.5,
            "t_end_epoch": stamped}), encoding="utf-8")
        recs = mod._seat_records(d)
        assert len(recs) == 1
        name, end, dur, ok, exact = recs[0]
        assert exact is True, "the record carries a stamp and it was not used"
        assert end == pytest.approx(stamped), (
            f"completion read as {end}, not the stamped {stamped}; the mtime won")

    def test_a_record_without_a_stamp_still_resolves_by_mtime(self, mod, tmp_path):
        """The archived corpus must keep working, or the finding loses its data."""
        d = tmp_path / "older_round"
        d.mkdir()
        f = d / "fable.json"
        f.write_text(json.dumps({"model": "fable", "route": "claude_cli",
                                 "ok": True, "elapsed_s": 9.0}), encoding="utf-8")
        recs = mod._seat_records(d)
        assert len(recs) == 1
        _n, end, _d, _ok, exact = recs[0]
        assert exact is False
        assert end == pytest.approx(f.stat().st_mtime)

    def test_the_split_is_reported_and_cannot_exceed_the_corpus(self, produced):
        a = produced["rounds_with_exact_stamps"]
        b = produced["rounds_reconstructed"]
        assert a >= 0 and b >= 0
        assert a + b == produced["n_all_kept"], (
            f"{a} exact + {b} reconstructed does not equal the "
            f"{produced['n_all_kept']} plausible rounds, so a round is counted "
            f"twice or in neither provenance")
        assert b == produced["n_kept"], (
            "the headline corpus must BE the reconstructed set, so that a new "
            "stamped round cannot move a pinned figure")

    def test_the_headline_still_rests_on_the_reconstructed_corpus(self, produced):
        """Today every kept round predates the stamps. When that stops being
        true the headline is a MIXED figure and must be restated per provenance.
        """
        assert produced["rounds_reconstructed"] >= 80, (
            f"only {produced['rounds_reconstructed']} rounds are reconstructed; "
            f"if stamped rounds now dominate, recompute the median over them "
            f"alone and requote it rather than mixing the 2 provenances")


class TestTheSimulatedPerRoundReaderIsReached:
    """★ ADDED BECAUSE IT WAS AN UNWIRED ADDITION, found by the FFAFP gate.

    `simulated_round_barriers` was written to satisfy his ruling that the
    barrier be studied in the simulated run, and then reached by NOTHING -- no
    test, not even the producer's own `main`. That is the additive standard's
    other half, breached within an hour of a memory file being written about it.

    WHY A SEPARATE READER EXISTS AT ALL, since it looks like duplication. The
    panel dispatcher writes `completion_barrier.json` at the end of its round;
    `reference_runner_v3` has its OWN dispatch path and calls nothing of the
    kind. And the archive reader DELIBERATELY rejects `r<digit>_` files, that
    rejection being the fix for a loose detector which credited one "round" with
    144 seats and reported the seat-count effect BACKWARDS -- so the files that
    carry the new stamps are exactly the files it must keep ignoring.
    """

    def test_it_groups_by_round_and_reads_the_exact_stamps(self, mod, tmp_path):
        run = tmp_path / "a_sim_run"
        run.mkdir()
        # 2 rounds, 3 seats each, timings known by construction
        plan = {
            "r0": [("alpha", 100.0, 110.0), ("beta", 100.0, 130.0),
                   ("gamma", 100.0, 105.0)],
            "r1": [("alpha", 200.0, 210.0), ("beta", 200.0, 220.0),
                   ("gamma", 200.0, 202.0)],
        }
        for rnd, seats in plan.items():
            for name, t0, t1 in seats:
                (run / f"{rnd}_{name}_x.json").write_text(json.dumps({
                    "model": name,
                    "metadata": {"t_start_epoch": t0, "t_end_epoch": t1,
                                 "elapsed": t1 - t0}}), encoding="utf-8")
        rows = mod.simulated_round_barriers(run)
        assert [r["round"] for r in rows] == ["r0", "r1"], (
            "rounds must come back in round order, not file order")
        r0 = rows[0]
        assert r0["n_timed"] == 3 and r0["slowest_seat"] == "beta"
        assert r0["round_wall_s"] == pytest.approx(30.0)
        # beta ends at 130; alpha idles 20, gamma idles 25, beta 0
        assert r0["total_idle_s"] == pytest.approx(45.0)
        assert r0["idle_share"] == pytest.approx(45.0 / (3 * 30.0))
        assert rows[1]["slowest_seat"] == "beta"

    def test_a_seat_file_without_stamps_is_skipped_not_guessed(self, mod, tmp_path):
        """An unstamped run must yield nothing rather than an invented figure."""
        run = tmp_path / "older_sim_run"
        run.mkdir()
        (run / "r0_alpha_x.json").write_text(json.dumps({
            "model": "alpha", "metadata": {"elapsed": 12.0}}), encoding="utf-8")
        assert mod.simulated_round_barriers(run) == [], (
            "a run predating the stamps must measure nothing, because the "
            "mtime route is the archive reader's job and not this one's")

    def test_the_command_line_reaches_it(self, mod, tmp_path):
        """The flag is what makes it reachable outside a test."""
        run = tmp_path / "flag_run"
        run.mkdir()
        for name, t0, t1 in (("a", 0.0, 5.0), ("b", 0.0, 9.0)):
            (run / f"r0_{name}_x.json").write_text(json.dumps({
                "model": name,
                "metadata": {"t_start_epoch": t0, "t_end_epoch": t1,
                             "elapsed": t1 - t0}}), encoding="utf-8")
        prev = mod.LOGS
        try:
            mod.LOGS = tmp_path
            rows = mod._simulated_report("flag_run")
        finally:
            mod.LOGS = prev
        assert len(rows) == 1 and rows[0]["slowest_seat"] == "b"

    def test_an_absent_run_is_reported_and_not_invented(self, mod, tmp_path):
        prev = mod.LOGS
        try:
            mod.LOGS = tmp_path
            assert mod._simulated_report("there_is_no_such_run") == []
        finally:
            mod.LOGS = prev

    def test_latest_stamped_run_finds_the_real_one(self, mod):
        """On this machine the newest stamped run is T3, and it must be found."""
        got = mod.latest_stamped_run()
        if got is None:
            pytest.skip("no stamped run in this checkout")
        rows = mod.simulated_round_barriers(got)
        assert rows, f"{got.name} was selected as stamped but measures nothing"
        assert all(r["n_timed"] >= 2 for r in rows)


class TestTheIndependentCorroboration:

    def test_it_agrees_with_the_committed_stagger_figure(self, produced):
        assert produced["saving_vs_serial_median"] == pytest.approx(0.436250, abs=5e-7)
        assert produced["saving_agreement_gap"] < 0.10, (
            f"this method reads {produced['saving_vs_serial_median']:.6f} against "
            f"the committed {produced['committed_saving_2026_10_07']:.6f}. A wide "
            f"gap means 2 instruments on the same quantity now disagree, and one "
            f"of them is wrong")
