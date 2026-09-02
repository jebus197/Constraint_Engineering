"""Reusing your own finding ID must not delete a different defect.

`lookup_alias` keys on (model_id, finding_id) alone. When a model re-used its
own local id, the runner treated the second finding as a repeat of the first and
converted it into a CONFIRM vote -- discarding its description, its falsifier and
its proposed fix without ever registering them.

Found by fable in panel review on 2026-09-01, which traced the one parsed
`compute_source_hash` catch in the canary rehearsal to exactly this path. A
correct detection had a live route to oblivion regardless of whether the
reviewer had seen the plant.

It is the same class as "a model could delete a finding by repeating itself",
arriving through the absorb door rather than the verdict door.

The fix compares content before absorbing, using this project's own instrument
at its own calibrated threshold: Jaccard over STEM signatures, measured on
archive ground truth at median 0.542 for pairs the system merged against 0.000
for independently-confirmed distinct pairs (p = 1.9e-25).
"""

import ast
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from bench.convergence_location import (  # noqa: E402
    signature_similarity, stem_signature)

RUNNER = REPO / "bench" / "reference_runner_v3.py"
THRESHOLD = 0.20


def _overlap(a: str, b: str) -> float:
    return signature_similarity(stem_signature(a), stem_signature(b))


class TestTheDecisionRuleSeparatesDefects:
    """The instrument must tell a reworded repeat from a different defect."""

    SAME = ("pi_mem drops BETA_0 from the denominator so it returns exactly 1.0",
            "the pi_mem denominator omits BETA_0 and can therefore reach 1.0")
    DIFFERENT = (
        "pi_mem drops BETA_0 from the denominator so it returns exactly 1.0",
        "compute_source_hash iterates file_paths unsorted so the digest is "
        "order-dependent")

    def test_a_reworded_repeat_is_absorbed(self):
        assert _overlap(*self.SAME) >= THRESHOLD

    def test_a_genuinely_different_defect_is_not(self):
        assert _overlap(*self.DIFFERENT) < THRESHOLD, (
            "the two texts describe different defects; absorbing the second "
            "into the first deletes it")

    def test_the_two_cases_are_not_marginal(self):
        """A threshold that only just separates them would not survive drift."""
        same, diff = _overlap(*self.SAME), _overlap(*self.DIFFERENT)
        assert same - diff > 0.5, (
            f"separation is only {same - diff:.3f}; the calibration this "
            f"threshold rests on reports 0.542 against 0.000")


class TestTheRealPopulationNotTheEasyCase:
    """The signature test alone deletes 40% of real same-function pairs.

    REFUTED BY THE PANEL, 2026-09-02, on real data. Of 711 archived pairs that
    name the SAME function and carry DIFFERENT falsifier code -- different
    defects by this project's own tools-decide criterion -- 282 score at or
    above the 0.20 threshold: 39.7%, Wilson [36.1%, 43.3%]. Under a reused id
    every one of those would have been absorbed and deleted.

    The cause: a STEM signature is built from LOCATION tokens, identifiers and
    line numbers, median 4 of them. Two findings about one function collide by
    construction. The 0.20 threshold was calibrated for merging UNLOCATED
    findings -- the opposite population.

    My original test used a cross-file pair sharing zero tokens. I checked the
    easy case and shipped it as though it were the whole set.
    """

    SAME_FN_DIFFERENT_DEFECT = (
        "`record_experiment` (`bench/dm/_memory.py:232`) inverts the duplicate "
        "guard so a repeated `exp_id` is accepted by default",
        "`record_experiment` (`bench/dm/_memory.py:232`) does not strip "
        "`exp_id`, so whitespace variants bypass the membership test")

    def test_the_signature_test_alone_would_absorb_them(self):
        """Pin the weakness, so the falsifier rule cannot be quietly removed."""
        a, b = self.SAME_FN_DIFFERENT_DEFECT
        sim = _overlap(a, b)
        assert sim >= THRESHOLD, (
            f"overlap {sim:.3f}: this pair no longer demonstrates the "
            f"collision, so pick another same-function pair")

    def test_a_different_falsifier_decides_it_regardless(self):
        """The primary rule: different falsifier, different defect. Exact."""
        src = RUNNER.read_text(encoding="utf-8")
        i = src.index("PRIMARY TEST: A DIFFERENT FALSIFIER IS A DIFFERENT DEFECT")
        block = src[i:i + 2200]
        assert "_new_fals and _old_fals and _new_fals != _old_fals" in block, (
            "the falsifier comparison is gone; the signature test alone deletes "
            "40% of real same-function pairs")
        assert "_absorb = False" in block

    def test_the_signature_test_survives_as_a_fallback(self):
        """One side may carry no falsifier yet; that case still needs a test."""
        src = RUNNER.read_text(encoding="utf-8")
        i = src.index("PRIMARY TEST: A DIFFERENT FALSIFIER IS A DIFFERENT DEFECT")
        block = src[i:i + 2600]
        assert "SECONDARY" in block and "signature_similarity(" in block

    def test_the_report_says_which_rule_decided(self):
        src = RUNNER.read_text(encoding="utf-8")
        assert '"decided_by"' in src, (
            "without it, nobody can tell afterwards whether a separation was "
            "made on falsifiers or on a threshold known to be weak here")


class TestTheRunnerActuallyPerformsTheCheck:
    """A guard that exists but is never reached is the defect it replaced."""

    @pytest.fixture(scope="class")
    def absorb_branch(self):
        """The source of the else-branch that handles a reused finding id."""
        src = RUNNER.read_text(encoding="utf-8")
        i = src.index("existing = registry.lookup_alias(f.model_id, f.finding_id)")
        j = src.index("A REUSED FINDING ID IS NOT AUTOMATICALLY THE SAME DEFECT", i)
        k = src.index("immune_result = brain.run_immune_pipeline", j)
        return src[j:k]

    def test_it_compares_signatures(self, absorb_branch):
        assert "signature_similarity(" in absorb_branch, (
            "the absorb path no longer compares content; a reused id will "
            "again delete a different defect")

    def test_it_registers_rather_than_only_voting(self, absorb_branch):
        assert "registry.register(f, f.model_id)" in absorb_branch, (
            "on divergence the finding must be REGISTERED, not merely logged")

    def test_it_imports_what_it_uses(self, absorb_branch):
        """Without the local import the block raises and fails safe silently."""
        assert "from bench.convergence_location import" in absorb_branch, (
            "stem_signature/signature_similarity are not module-level here; "
            "without the local import this guard NameErrors, is swallowed by "
            "its own fail-safe, and never fires")

    def test_it_fails_toward_absorbing(self, absorb_branch):
        """An error in the guard must not invent findings."""
        assert "_absorb = True" in absorb_branch
        i = absorb_branch.index("except Exception")
        assert "absorbing" in absorb_branch[i:i + 400].lower(), (
            "the failure path must fall back to the previous behaviour")

    def test_the_divergence_is_recorded_in_the_report(self, absorb_branch):
        """Otherwise nobody can tell afterwards that it ever fired."""
        assert 'result.setdefault("id_reuse_registered"' in absorb_branch

    def test_the_branch_parses(self, absorb_branch):
        """Cheap guard against a syntax-level mangle of the edited region."""
        ast.parse(RUNNER.read_text(encoding="utf-8"))


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
