# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'joint_what_is_a_proof_outside_code_2026-10-31', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 711e4c57d94c70a106238d82e4720580fe240be7a255e4b8af32ef09e45b3db8
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""An asserted-critical escalated to HIL leaves gamma's critical novelty series.

ROUND-2 FINDING, seat fable, joint `what_is_a_proof_outside_code_b22`. cc2
reported in round 1 that the proof/falsifier polarity collision "manufactures
apparent convergence" and attributed it to `spec_verification_factor`: V=0.0
annihilates `effective_severity`, the finding drops below
`CRITICAL_SEVERITY_THRESHOLD`, and it vanishes from the series gamma is
estimated from. I set out to refute that and my own falsifier refuted ME: the
numbers reproduce exactly -- (4,3,2,1) becomes (2,1,1,0), gamma 0.3247 becomes
0.4652 -- but NOT by that mechanism, and the real one is worse.

WHAT ACTUALLY HAPPENS, established by driving the REAL gate:

  * `_settled_novelty_series` reads `entry["severity"]`, the ASSERTED number,
    and never calls `effective_severity`. Measured: `effective_severity` has
    exactly two live call sites in `reference_runner_v3` -- the A4/blocker door
    and one `mode_effects` reporting read -- and neither is the novelty series.
    So V cannot move gamma, and the severity specification need not even be on.
    It was on in 0 of 65 archived runs.

  * The entry leaves the series through the STATUS channel instead.
    `apply_falsifier_verdicts` refuses to write status REFUTED on an
    asserted-critical -- the CONFIRM-only ruling of 2026-08-03, backed by the
    Exp 42 audit in which 2 of 3 REFUTED criticals were themselves wrong -- and
    escalates it to HIL as UNCONFIRMED instead. But UNCONFIRMED is a member of
    `_NON_NOVEL_TERMINAL_STATUSES`, so the escalation removes the finding from
    the critical novelty count just as completely as a refutation would have.

  * So the mechanism that PROTECTS a real critical from being faked away in the
    status channel is the same mechanism that deletes it from the
    convergence-measurement channel. An unresolved critical in a human queue is
    counted as if the round produced no critical at all, which lowers the later
    terms of the series and raises the depletion exponent.

MEASURED OVER THE ARCHIVE
(`scripts/how_many_archived_runs_lose_escalated_criticals_from_gamma_2026-10-31.py`,
65 runs, 3,115 entries):

  * 85 asserted-critical entries sit at status UNCONFIRMED and are therefore
    absent from the series. By falsifier verdict: 38 with no verdict at all,
    27 UNTOOLABLE, 19 ERROR, 1 REFUTED.
  * 18 of 65 runs have a different critical novelty series once they are
    counted.
  * Recomputing the SETTLED series the way the current gate reads it
    (`_settled_novelty_series`, the F4 fix), 1 archived registry --
    `exp40_gate_20260514T020550Z` -- satisfies the K=2 consecutive-zero test at
    round 8 and would NEVER satisfy it with its 11 escalated criticals counted;
    gamma falls 0.3018 -> 0.2328, crossing the 0.30 threshold and moving the
    band from "Moderate depletion" to "Weak depletion -- state closure may be
    premature". 2 of 65 registries cross that threshold.
  * STATED PRECISELY, BECAUSE THE DISTINCTION DECIDES THE SEVERITY: that run
    did NOT converge. Its `gate_history` ends `[false, false]` and it is a May
    2026 run that predates F4, so this is a forward-looking recomputation on
    the current gate code, not a demonstrated past premature release. And
    release is independently held: `unverified_critical_count()` counts an
    escalated critical as a blocker (verified by execution below, 3 of 3). So
    the loss is in the REPORTED convergence measurement -- CDSFL section 10
    category 3, verification-integrity corruption, and category 4, silent
    evidence loss -- and NOT in release safety, where its reach is zero.
  * The PROOF-POLARITY route specifically accounts for 1 of those 85, so the
    polarity hazard is latent while the channel it feeds is live. Equipment
    escalations (UNTOOLABLE/ERROR/no falsifier) are 84 of 85.

Gamma arithmetic independently reproduced three ways: `scipy.stats.linregress`,
`statsmodels.OLS`, and Wolfram Language (local Wolfram Engine via
`wolframscript`, exit 0, result line printed) -- 0.32474169, 0.46516139,
0.30182092, 0.23284622, agreeing with `_estimate_gamma` to 8 digits.

WHAT THIS FILE DOES AND DELIBERATELY DOES NOT DO. It pins the mechanism by
execution so the loss is visible and any future change to either channel trips
a test instead of moving a published gamma silently. It changes NO gate
decision, NO severity ruler and NO gamma value -- the severity ruler has been
defended against four proposals and gamma is load-bearing by standing
directive, so the repair here is an instrument, not a ruler change. Whether the
series SHOULD count an escalated critical is the founder's call, and this is the
measurement he would need to make it.
"""
from __future__ import annotations

import inspect

import pytest

from bench.dm._types import Finding
from bench.reference_runner_v3 import (
    CRITICAL_SEVERITY_THRESHOLD,
    FindingRegistry,
    RunnerConfig,
    _NON_NOVEL_TERMINAL_STATUSES,
    _estimate_gamma,
    _settled_novelty_series,
    apply_falsifier_verdicts,
    effective_severity,
    spec_verification_factor,
)
import bench.reference_runner_v3 as rr


# A printed proof in the founder's step-3 sense: it computes with a real tool,
# the comparison succeeds, it exits 0. Under the falsifier convention a clean
# exit means "no defect demonstrated", so the re-verifier returns REFUTED.
PROOF_HOLDS = (
    "import math\n"
    "rss = math.sqrt(0.0392**2 + 0.0049**2 + 0.1206**2)\n"
    "assert abs(rss - 0.1269) < 5e-4, 'the combination does not reproduce'\n"
    "print('proof holds: combined relative u =', round(rss, 4), 'per cent')\n"
)
DEMONSTRATION = "assert False, 'real defect demonstrated'"

TOTAL_CRIT = [4, 3, 2, 1]
PROOF_BEARING = [2, 2, 1, 1]


def _registry_with_proof_polarity_criticals() -> FindingRegistry:
    reg = FindingRegistry()
    n = 0
    for rnd, (total, proofs) in enumerate(zip(TOTAL_CRIT, PROOF_BEARING)):
        for j in range(total):
            n += 1
            cid = reg.register(
                Finding(finding_id=f"f{n}", model_id="fable", round_idx=rnd,
                        flaw_class=2, severity=0.85, abstraction_index=0.5,
                        description=f"claim {n}",
                        falsifier_code=(PROOF_HOLDS if j < proofs
                                        else DEMONSTRATION)),
                "fable")
            reg.entries[cid]["status"] = "CONFIRMED"
            reg.entries[cid]["open_since_round"] = rnd
    return reg


def _first_k_consecutive_zero(series, k: int = 2):
    run = 0
    for i, count in enumerate(series):
        run = run + 1 if count == 0 else 0
        if run >= k:
            return i
    return None


class TestTheSeverityChannelIsNotTheRoute:
    """cc2's arithmetic reproduces; cc2's mechanism does not."""

    def test_v_is_inverted_for_a_proof_polarity_artefact(self):
        """NOT in dispute, pinned as a tripwire. A proof that HOLDS scores 0.0
        and a proof whose own assertion FIRES scores 1.0 -- the ordering is
        inverted relative to what the artefact demonstrated."""
        rr._SEVERITY_SPEC["on"] = True
        try:
            held = {"severity": 0.85, "falsifier_verdict": "REFUTED"}
            failed = {"severity": 0.85, "falsifier_verdict": "CONFIRMED"}
            assert spec_verification_factor(held) == 0.0
            assert spec_verification_factor(failed) == 1.0
            assert effective_severity(held) == 0.0
            assert effective_severity(failed) == pytest.approx(0.85)
        finally:
            rr._SEVERITY_SPEC["on"] = False

    def test_the_novelty_series_never_reads_effective_severity(self):
        """Why the severity channel cannot be the route to gamma."""
        src = inspect.getsource(_settled_novelty_series)
        assert 'e.get("severity")' in src
        assert "effective_severity" not in src

    def test_effective_severity_has_no_novelty_or_gamma_call_site(self):
        """Executed census of the live call sites, not a claim about them."""
        lines = inspect.getsource(rr).splitlines()
        sites = [n for n, line in enumerate(lines, 1)
                 if "effective_severity(" in line
                 and "def effective_severity" not in line]
        assert len(sites) == 2, (
            f"effective_severity call sites moved: {sites}. If a new one is "
            f"inside _settled_novelty_series or _estimate_gamma, the severity "
            f"specification has become able to move gamma and this file's "
            f"finding needs re-measuring.")
        for site in sites:
            region = "\n".join(lines[max(0, site - 60):site])
            assert "def _settled_novelty_series" not in region
            assert "def _estimate_gamma" not in region


class TestTheStatusChannelIsTheRoute:
    """The real mechanism, driven through the real gate."""

    def test_escalating_a_critical_removes_it_from_the_critical_series(self):
        reg = _registry_with_proof_polarity_criticals()
        max_round = len(TOTAL_CRIT) - 1
        _all_before, crit_before = _settled_novelty_series(reg, max_round)
        assert crit_before == TOTAL_CRIT

        apply_falsifier_verdicts(
            reg, 1, cfg=RunnerConfig(falsifier_gate_enabled=True),
            repo_root=".")

        # The gate honoured CONFIRM-only: it did NOT write status REFUTED on any
        # asserted-critical. It escalated them.
        proof_entries = [e for e in reg.entries.values()
                         if e.get("falsifier_verdict") == "REFUTED"]
        assert len(proof_entries) == sum(PROOF_BEARING)
        for e in proof_entries:
            assert float(e["severity"]) >= CRITICAL_SEVERITY_THRESHOLD
            assert e["status"] == "UNCONFIRMED", (
                "the CONFIRM-only ruling is not holding; this file's finding "
                "assumes a REFUTED critical is escalated, not refuted")
            assert e.get("escalated") is True

        _all_after, crit_after = _settled_novelty_series(reg, max_round)
        expected = [t - p for t, p in zip(TOTAL_CRIT, PROOF_BEARING)]
        assert crit_after == expected, (
            "THE LOSS: six criticals sitting in a human queue are counted as "
            "rounds that produced no critical at all")
        assert crit_after == [2, 1, 1, 0]

    def test_the_loss_raises_the_depletion_exponent(self):
        """The consequence, in the number the gate reads."""
        gamma_with = _estimate_gamma(TOTAL_CRIT)
        gamma_without = _estimate_gamma([2, 1, 1, 0])
        assert gamma_with == pytest.approx(0.3247416905, abs=1e-9)
        assert gamma_without == pytest.approx(0.4651613946, abs=1e-9)
        assert gamma_without > gamma_with, (
            "deleting unresolved criticals must not be able to FLATTER "
            "depletion, and it does")
        assert rr._interpret_gamma(gamma_without).startswith("Strong depletion")
        assert rr._interpret_gamma(gamma_with).startswith("Moderate depletion")

    def test_unconfirmed_is_what_makes_the_escalation_invisible(self):
        """Name the member that carries the loss, rather than describing it."""
        assert "UNCONFIRMED" in _NON_NOVEL_TERMINAL_STATUSES
        assert "REFUTED" in _NON_NOVEL_TERMINAL_STATUSES

    def test_the_blocker_count_still_holds_release(self):
        """THE LIMIT OF THIS FINDING, and the reason it is a measurement defect
        rather than a release defect. The same escalated criticals that vanish
        from the novelty series are still counted by
        `unverified_critical_count`, so the A4 door stays shut. The two
        channels disagree about the same three findings, and only one of them
        is wrong."""
        reg = _registry_with_proof_polarity_criticals()
        apply_falsifier_verdicts(
            reg, 1, cfg=RunnerConfig(falsifier_gate_enabled=True),
            repo_root=".")
        blocked = reg.unverified_critical_count()
        _all_after, crit_after = _settled_novelty_series(
            reg, len(TOTAL_CRIT) - 1)
        assert blocked >= sum(PROOF_BEARING), (
            "if the blocker count ever stops holding these, the finding is no "
            "longer latent on release and must be re-rated")
        assert sum(crit_after) < sum(TOTAL_CRIT)
        assert blocked > 0 and sum(crit_after) < sum(TOTAL_CRIT), (
            f"{blocked} findings block release while the convergence series "
            f"reports {crit_after}")

    def test_the_archived_series_recomputation_reproduces(self):
        """exp40_gate_20260514T020550Z, the one archived registry that moves.

        The SETTLED series as the current gate reads it, versus the same series
        with its 11 escalated criticals counted. K=2 is satisfied at round 8 in
        the first and never in the second, and gamma crosses 0.30 downward.
        This is a recomputation on archived data, not a claim that the run
        converged -- it did not (`gate_history` ends false).
        """
        as_gated = [6, 4, 2, 1, 1, 1, 3, 0, 0, 1, 0, 3, 0, 1, 0, 2, 2, 1, 4,
                    3, 5, 5, 4, 9, 2, 1, 3, 0, 5]
        counted = [6, 4, 2, 1, 1, 1, 3, 1, 0, 1, 0, 3, 1, 1, 0, 4, 2, 1, 5,
                   5, 5, 5, 5, 10, 4, 1, 3, 0, 5]
        assert _first_k_consecutive_zero(as_gated) == 8
        assert _first_k_consecutive_zero(counted) is None
        g_gated = _estimate_gamma(as_gated)
        g_counted = _estimate_gamma(counted)
        assert g_gated == pytest.approx(0.3018209153, abs=1e-9)
        assert g_counted == pytest.approx(0.2328462240, abs=1e-9)
        assert g_gated >= 0.30 > g_counted, (
            "the archived registry satisfies the gamma threshold only because "
            "its escalated criticals are absent from the recomputed series")
