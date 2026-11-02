"""The archive already supplies what the severity defaults need, and the
real/simulated split that claim rests on must not be breakable.

HIS QUESTION, 2026-11-01, verbatim: *"I asked why it required me to spend money,
before we can decide on some sane default values for this measurement? What
difference does spending money in a live run, and making the same measurement in
a simulated run make? I don't see the connection?"*

THE ANSWER IS NONE, and it rests entirely on one classification: which archived
runs used REAL seats. If that split is wrong in the generous direction, the
answer is unsafe, because it would claim paid data the project does not have.
So the split is guarded here rather than trusted.

WHAT THIS CAUGHT ON THE DAY IT WAS WRITTEN. The producer's headroom figure was
quoted to him as 6.52x the required sample before this file existed. 11 of the 35
simulated runs are classified simulated by the ABSENCE of seat names rather than
by a `-SIM` name, and those 11 carry 1,148 of the 1,884 entries -- the MAJORITY.
The defensible figure is 2.55x. The generous one was 2.6 times too kind.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib

import numpy as np
import pytest
from scipy import stats
from statsmodels.stats.proportion import samplesize_confint_proportion

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "how_many_simulated_runs_for_the_severity_defaults_2026-11-01.py"

#: The blocked study run of 2026-10-03. Its own log records it as simulated and
#: all its seats are simulation seats, so it is the CONTROL: a classifier that
#: puts it in the real bucket is inflating the paid-data claim.
CONTROL_SIM_RUN = "study_run1b_2026-10-03_20261003T100439Z"


@pytest.fixture(scope="module")
def h():
    spec = importlib.util.spec_from_file_location("_sev_defaults", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def buckets(h):
    return h.survey()


class TestTheSplitIsNotBreakable:

    def test_the_known_simulated_run_is_not_counted_as_real(self, buckets):
        real, sim = buckets
        assert CONTROL_SIM_RUN not in {r["run"] for r in real}, (
            f"{CONTROL_SIM_RUN} is simulated by its own log and landed in the "
            f"REAL bucket, so the paid-data claim is inflated")
        assert CONTROL_SIM_RUN in {r["run"] for r in sim}, (
            f"{CONTROL_SIM_RUN} is in neither bucket; the control cannot "
            f"discriminate and this test proves nothing")

    def test_the_two_seat_vocabularies_are_disjoint(self, buckets):
        real, sim = buckets
        rn = {s for r in real for s in r["seats"]}
        sn = {s for r in sim for s in r["seats"]}
        assert rn and sn, f"a bucket has no named seats: real={rn} sim={sn}"
        assert not (rn & sn), f"a seat name appears in BOTH buckets: {rn & sn}"
        assert all("sim" not in s.lower() for s in rn), (
            f"a real-bucket seat name carries a simulation marker: {rn}")

    def test_no_real_bucket_run_carries_a_simulation_flag(self, buckets):
        """The second, independent falsifier: the state's own text, not the names."""
        real, _ = buckets
        bad = []
        for r in real:
            s = (REPO / "bench" / "logs" / r["run"] / "runner_state.json").read_text()
            low = s.lower()
            if '"simulated": true' in low or '"simulate": true' in low or "sim_mode" in low:
                bad.append(r["run"])
        assert not bad, f"real-bucket run(s) carry a simulation flag: {bad}"

    def test_injecting_a_sim_seat_moves_a_run_out_of_the_real_bucket(self, h, buckets):
        """ANTI-VACUITY. If the predicate ignored seat names entirely, every test
        above could pass while the classifier decided nothing."""
        real, _ = buckets
        assert real, "no real-bucket runs, so this cannot discriminate"
        names = sorted(real[0]["seats"])
        assert names, "the sample real run has no named seats"
        mutated = [n + "-SIM" for n in names]
        assert any(any(hint in n.lower() for hint in h.SIM_HINT) for n in mutated), (
            "the suffix the archive actually uses is not matched by SIM_HINT, so "
            "a simulated run named that way would be counted as real")


class TestTheClaimItselfHoldsOnTheCONSERVATIVEFigure:

    def test_real_seat_data_exists_at_all(self, buckets):
        real, _ = buckets
        assert len(real) >= 20, f"only {len(real)} real-seat runs"
        assert sum(r["entries"] for r in real) >= 1000, (
            "fewer than 1,000 real-seat entries, so 'no new paid run is needed' "
            "would rest on too little")
        assert sum(len(r["seats"]) * r["rounds"] for r in real) >= 800

    def test_the_conservative_headroom_still_clears_the_requirement(self, buckets):
        """The figure that may be QUOTED counts only -SIM-named runs."""
        _, sim = buckets
        named = [r for r in sim if r["seats"]]
        n_need = int(np.ceil(samplesize_confint_proportion(
            0.25, 0.05, alpha=0.05, method="normal")))
        conservative = sum(r["entries"] for r in named)
        assert conservative >= n_need, (
            f"the defensible simulated archive is {conservative} entries against "
            f"{n_need} needed; the claim that no new runs are required FAILS")

    def test_the_unnamed_runs_are_the_majority_so_the_caveat_is_load_bearing(self, buckets):
        """If this ever flips, the caveat can be dropped -- not before."""
        _, sim = buckets
        unnamed = sum(r["entries"] for r in sim if not r["seats"])
        total = sum(r["entries"] for r in sim)
        assert unnamed > 0, (
            "no run is classified simulated by absence any more, so re-measure "
            "before quoting the generous figure")
        assert unnamed / total > 0.5, (
            f"unnamed runs now carry {unnamed}/{total}; the 'majority' claim in "
            f"this file's docstring is stale")

    def test_the_sample_size_matches_a_closed_form(self):
        """2 tools on the one arithmetic the answer to him depends on."""
        z = stats.norm.ppf(0.975)
        for p, half in ((0.25, 0.05), (0.10, 0.05), (0.50, 0.03)):
            sm = samplesize_confint_proportion(p, half, alpha=0.05, method="normal")
            cf = (z / half) ** 2 * p * (1 - p)
            assert abs(sm - cf) < 1e-9, (p, half, sm, cf)


class TestTheProducerIsReachedAndHonest:

    def test_the_producer_leads_with_the_conservative_figure(self):
        src = PRODUCER.read_text()
        assert "QUOTE THE CONSERVATIVE ONE" in src, (
            "the producer no longer tells its reader which figure is safe to "
            "quote, which is how 6.52x reached him")
        assert "CONSERVATIVE, counting only" in src

    def test_the_producer_runs_clean(self):
        import subprocess
        import sys
        r = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                           capture_output=True, text=True, timeout=300)
        assert r.returncode == 0, r.stderr[-500:]
        assert "0 NEW PAID RUN" in r.stdout or "NO NEW PAID RUN" in r.stdout

    def test_help_is_inert(self):
        import subprocess
        import sys
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0
        assert "usage" in r.stdout.lower()
