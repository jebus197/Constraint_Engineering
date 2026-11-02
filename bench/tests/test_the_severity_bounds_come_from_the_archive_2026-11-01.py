"""The severity bounds are set from the archive, and the claim must be breakable.

HIS RULING, 2026-11-01: *"Use the archive to set the severity bounds."*

THE HEADLINE, and it is good news that must stay falsifiable: the Youden-optimal
critical cut computed from 545 falsifier-decided findings across the real-seat
archive is 0.70, which is EXACTLY the pre-registered live cut. Sensitivity
0.7316, specificity 0.8125, J 0.5441, and 0.0000 J lost by keeping it. A finding
that flatters the existing design is the kind most in need of a falsifier, which
is what `test_shuffling_the_labels_destroys_the_discrimination` is for.

WHAT THIS FILE PINS, and why each one:
  1. The truth signal is `falsifier_verdict`, never `status`. `status` carries
     model CONFIRM votes and the standing rule forbids a model vote as evidence.
  2. The AUC's interval is bootstrapped over FINDINGS. A first version used
     Wilson over n1*n2 PAIRS and was 17.9x too narrow.
  3. Discrimination survives: the conservative lower bound is above 0.5.
  4. Shuffling the confirmed/refuted labels collapses the AUC to chance. If it
     does not, the measurement is reading something other than the labels.
  5. The producer does NOT silently estimate d_i or nu, which are not estimable
     from raised findings -- recall and attribution respectively.
"""
from __future__ import annotations

import importlib.util
import pathlib

import numpy as np
import pytest
from scipy import stats

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "the_severity_bounds_from_the_archive_2026-11-01.py"


@pytest.fixture(scope="module")
def m():
    spec = importlib.util.spec_from_file_location("_sev_bounds", PRODUCER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def split(m):
    conf, refu, other = m.decided_findings()
    return np.array(conf), np.array(refu), other


class TestTheSignalIsProgrammatic:

    def test_the_producer_reads_the_falsifier_not_the_status(self):
        src = PRODUCER.read_text()
        assert 'it.get("falsifier_verdict")' in src, (
            "the producer no longer reads the falsifier verdict")
        assert 'it.get("status")' not in src, (
            "the producer reads `status`, which carries model CONFIRM votes. "
            "The standing rule is programmatic or HIL confirmation, never a "
            "model vote, so a bound derived from `status` is inadmissible.")

    def test_undecidable_outcomes_are_excluded_and_counted(self, split):
        _, _, other = split
        assert "ERROR" in other and "UNTOOLABLE" in other, other
        assert other["ERROR"] + other["UNTOOLABLE"] > 0, (
            "no ERROR or UNTOOLABLE falsifier outcomes at all; either the "
            "archive changed or the reader stopped seeing them, and silently "
            "scoring them as decided is how a red result reads green")


class TestTheDiscriminationHoldsAndIsBreakable:

    def test_the_population_is_large_enough_to_bound_anything(self, split):
        c, r, _ = split
        assert len(c) >= 400, f"only {len(c)} confirmed findings"
        assert len(r) >= 10, f"only {len(r)} refuted findings"

    def test_the_full_range_is_covered_unlike_the_2026_09_02_audit(self, split):
        c, r, _ = split
        lo, hi = min(c.min(), r.min()), max(c.max(), r.max())
        assert hi - lo > 0.5, (
            f"severities span only [{lo}, {hi}], width {hi-lo:.4f}. The whole "
            f"point of using real runs is that the 2026-09-02 audit's 0.09-wide "
            f"window had power 0.144250 and could settle nothing.")

    def test_severity_discriminates_above_chance(self, m, split):
        c, r, _ = split
        point = m.auc(c, r)
        n1, n2 = len(c), len(r)
        q1, q2 = point / (2 - point), 2 * point ** 2 / (1 + point)
        se = float(np.sqrt((point * (1 - point) + (n1 - 1) * (q1 - point ** 2)
                            + (n2 - 1) * (q2 - point ** 2)) / (n1 * n2)))
        lower = point - stats.norm.ppf(0.975) * se
        assert lower > 0.5, (
            f"AUC {point:.6f} with Hanley-McNeil lower bound {lower:.6f}; "
            f"severity no longer discriminates and every bound derived from it "
            f"must be withdrawn")

    def test_shuffling_the_labels_destroys_the_discrimination(self, m, split):
        """THE FALSIFIER. A measurement that survives label destruction is
        reading an artefact of the data's shape, not the labels."""
        c, r, _ = split
        pooled = np.concatenate([c, r])
        rng = np.random.default_rng(7)
        aucs = []
        for _ in range(400):
            rng.shuffle(pooled)
            aucs.append(m.auc(pooled[:len(c)], pooled[len(c):]))
        mean_shuffled = float(np.mean(aucs))
        real = m.auc(c, r)
        assert abs(mean_shuffled - 0.5) < 0.05, (
            f"shuffled AUC averages {mean_shuffled:.6f}, not ~0.5, so the "
            f"statistic is biased by the class sizes rather than measuring "
            f"separation")
        assert real > np.percentile(aucs, 97.5), (
            f"the real AUC {real:.6f} is inside the shuffled null's 95% band "
            f"(upper {np.percentile(aucs, 97.5):.6f}); the discrimination is "
            f"not distinguishable from chance")

    def test_the_interval_is_over_findings_not_pairs(self):
        src = PRODUCER.read_text()
        assert "bootstrap over FINDINGS" in src and "QUOTE THIS" in src
        assert "WRONG, over PAIRS" in src, (
            "the pairwise interval is no longer labelled as wrong, which is how "
            "a 17.9x-too-narrow figure reached him once already")


class TestWhatIsNotClaimed:

    def test_the_producer_refuses_to_estimate_recall_or_reinjection(self):
        src = PRODUCER.read_text()
        assert "is RECALL and is not estimable" in src, (
            "the producer no longer states that d_i is not estimable from "
            "raised findings, which is the one way this measurement could be "
            "mistaken for a detection-power estimate")
        assert "NOT used" in src and "open_since_round" in src, (
            "the re-injection proxy is no longer explicitly declined")

    def test_the_live_cut_is_named_so_a_change_to_it_is_loud(self, m):
        assert m.LIVE_CRITICAL_CUT == 0.7, (
            f"the live critical cut is now {m.LIVE_CRITICAL_CUT}; the "
            f"archive's Youden point was 0.70 and that agreement is the "
            f"finding, so re-measure before trusting it")


class TestTheProducerRuns:

    def test_it_exits_clean(self):
        import subprocess
        import sys
        r = subprocess.run([sys.executable, str(PRODUCER)], cwd=REPO,
                           capture_output=True, text=True, timeout=600)
        assert r.returncode == 0, r.stdout[-900:] + r.stderr[-400:]
        assert "FAILURES: 0" in r.stdout

    def test_help_is_inert(self):
        import subprocess
        import sys
        r = subprocess.run([sys.executable, str(PRODUCER), "--help"], cwd=REPO,
                           capture_output=True, text=True, timeout=60)
        assert r.returncode == 0 and "usage" in r.stdout.lower()
