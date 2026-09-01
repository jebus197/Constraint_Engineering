"""Commissioning tests for the four components that decide WHEN A RUN STOPS.

WHY THIS FILE EXISTS. The instrument inventory of 2026-08-22 found that four
components emit a stopping verdict and that NOT ONE of them was named by any test:
I02 the two-sided gamma gate, I04 the state-convergence check, I07 stall
convergence, I08 budget extension. Every convergence result in the archive was
declared by one of these four.

WHAT "COMMISSIONED" MEANS, and it is stricter than "tested". A component is
commissioned when a test feeds it a KNOWN-GOOD input and a KNOWN-BAD input and
asserts that it answers DIFFERENTLY. A test that only checks the happy path proves
the component can say yes; it does not prove the component can say no. Three of the
five instruments measured directly on 2026-08-22 had a test naming them and were
still not commissioned by this standard.

WHAT THIS FILE DOES NOT CLAIM. It does not claim these components are correct in
the sense of choosing the right stopping point — that is a scientific question about
the model, settled by experiment. It claims only that each one DISCRIMINATES: that
it can be made to fire and made not to fire, by inputs that differ in the way the
component is supposed to care about. That is the minimum property a verdict-emitting
instrument must have to carry any information at all.

STANDING CORRECTION THIS FILE RECORDS. On 2026-08-25 the founder pointed out that
the two-sided gamma gate HAS fired in production — exp40_slice_admissibility closed
with gamma=0.305 >= 0.3 at round 7, exp41c on three consecutive zero-critical
rounds, and four further runs closed on critical quiescence. That is correct, and an
earlier claim that these components had never been shown to distinguish a converged
run from an unconverged one was too strong and is withdrawn. Production firing is
evidence of function; these tests are the controlled confirmation that was missing,
not a rescue of something believed broken.

The runner is not modified by any of this. These tests read it only.
"""
import copy

import pytest

import bench.reference_runner_v3 as rr


def _cfg(**overrides):
    """A RunnerConfig with the gate knobs set explicitly.

    Defaults are read rather than assumed, then overridden per test, so a change to
    a default cannot silently turn one of these tests into a tautology.
    """
    cfg = rr.RunnerConfig()
    for k, v in overrides.items():
        assert hasattr(cfg, k), f"RunnerConfig has no attribute {k!r} — test is stale"
        setattr(cfg, k, v)
    return cfg


# ---------------------------------------------------------------------------
# I02 — the two-sided gamma gate (_check_gamma_alt_convergence)
# ---------------------------------------------------------------------------
class TestI02TwoSidedGammaGate:
    """The gate converges only when BOTH sides of the diminishing-returns coin agree:
    the decay slope has flattened AND consecutive rounds have produced no new
    critical findings. Either alone must not be enough."""

    BASE = dict(gamma_alt_threshold=0.30, gamma_alt_consecutive_zero_crit=3)

    def test_fires_when_both_conditions_hold(self):
        ok, reason = rr._check_gamma_alt_convergence(
            round_idx=8, gamma=0.55, novel_critical_history=[4, 2, 0, 0, 0],
            cfg=_cfg(**self.BASE), gamma_critical=0.55,
        )
        assert ok is True, f"known-GOOD input did not converge: {reason}"
        assert reason, "a firing verdict must carry a reason"

    def test_does_not_fire_when_criticals_are_still_arriving(self):
        """KNOWN-BAD: slope flat but new criticals every round. Must NOT converge."""
        ok, reason = rr._check_gamma_alt_convergence(
            round_idx=8, gamma=0.55, novel_critical_history=[2, 2, 2, 2, 2],
            cfg=_cfg(**self.BASE), gamma_critical=0.55,
        )
        assert ok is False, (
            "gate fired on a CONSTANT critical arrival rate — the worst case, not "
            "the best. This is the vacuous-curve degeneracy repaired in 2887106."
        )

    def test_it_fires_for_the_STATED_reason_not_merely_fires(self):
        """This project's own central lesson applied to its own test suite.

        The falsifier gate measured that a test FIRED and never that it fired
        BECAUSE of the claim. A commissioning test can commit the same error: pass
        because the component answered correctly by accident. So the reason string
        is asserted, not just the boolean."""
        ok, reason = rr._check_gamma_alt_convergence(
            round_idx=8, gamma=0.55, novel_critical_history=[4, 2, 0, 0, 0],
            cfg=_cfg(**self.BASE), gamma_critical=0.55)
        assert ok is True
        assert "gamma_critical" in reason and ">=" in reason, (
            f"converged without citing the decay arm: {reason}")
        assert "zero-new-critical" in reason, (
            f"converged without citing the quiescence arm: {reason}")

        bad_ok, bad_reason = rr._check_gamma_alt_convergence(
            round_idx=8, gamma=0.55, novel_critical_history=[2, 2, 2, 2, 2],
            cfg=_cfg(**self.BASE), gamma_critical=0.55)
        assert bad_ok is False
        assert "novel_crit_recent" in bad_reason, (
            "refused for an unstated reason — it must fail on the COUNT arm here, "
            f"since gamma is above threshold: {bad_reason}")

    def test_implementation_matches_its_stated_rule_exhaustively(self):
        """`sy`: enumerate the input space rather than sampling two points of it.

        Two hand-picked inputs prove the gate discriminates. They do not prove it
        implements the rule it documents. This enumerates 8 gamma values against
        1,344 history patterns and compares every answer against the stated rule:
        converge if and only if the decay slope is at or above threshold AND K
        consecutive rounds produced no new critical finding.
        """
        import itertools
        th, k = 0.30, 3
        cfg = _cfg(gamma_alt_threshold=th, gamma_alt_consecutive_zero_crit=k)
        gammas = [0.0, 0.15, 0.29, 0.30, 0.31, 0.55, 0.99, 1.0]
        patterns = [list(p) for n in (3, 4, 5)
                    for p in itertools.product([0, 1, 2, 5], repeat=n)]
        disagreements = []
        for g in gammas:
            for h in patterns:
                got, _ = rr._check_gamma_alt_convergence(
                    round_idx=9, gamma=g, novel_critical_history=h,
                    cfg=cfg, gamma_critical=g)
                want = (g >= th and len(h) >= k and all(v == 0 for v in h[-k:]))
                if got != want:
                    disagreements.append((g, h, got, want))
        assert not disagreements, (
            f"{len(disagreements)} of {len(gammas)*len(patterns)} cases disagree with "
            f"the stated rule; first: {disagreements[:3]}")

    def test_neither_vacuous_series_converges_on_the_decay_arm_alone(self):
        """Commit 2887106 repaired a degeneracy in which two OPPOSITE series both
        drive a Duane fit to about zero: no critical ever found, which is the best
        possible outcome, and criticals arriving at a constant rate, which is the
        worst. Neither may converge on the slope alone."""
        cfg = _cfg(**self.BASE)
        for label, hist in [("no critical ever", [0] * 5),
                            ("constant arrival", [2] * 5)]:
            ok, _ = rr._check_gamma_alt_convergence(
                round_idx=9, gamma=0.0, novel_critical_history=hist,
                cfg=cfg, gamma_critical=0.0)
            assert ok is False, f"{label} converged on a flat curve alone"

    def test_discriminates_between_the_two_inputs(self):
        """The commissioning assertion proper: same gate, different answers."""
        good, _ = rr._check_gamma_alt_convergence(
            round_idx=8, gamma=0.55, novel_critical_history=[4, 2, 0, 0, 0],
            cfg=_cfg(**self.BASE), gamma_critical=0.55)
        bad, _ = rr._check_gamma_alt_convergence(
            round_idx=8, gamma=0.55, novel_critical_history=[2, 2, 2, 2, 2],
            cfg=_cfg(**self.BASE), gamma_critical=0.55)
        assert good != bad, "gate returns the same verdict for opposite inputs"


# ---------------------------------------------------------------------------
# I07 — stall convergence (_check_stall_convergence)
# ---------------------------------------------------------------------------
class _FakeRegistry:
    """Stand-in exposing exactly the three methods the stopping checks read.

    The interface was DISCOVERED rather than assumed: a first version of this class
    carried only the two methods the stall check needs, and the state-convergence
    tests failed on a missing ``undemonstrated_subcritical_ids``. That failure is
    the reason this class lists all three — a fake narrower than the real interface
    produces tests that pass for the wrong reason or not at all.
    """

    def __init__(self, open_ch, contested, undemonstrated=()):
        self._open_ch, self._contested = open_ch, contested
        self._undemonstrated = list(undemonstrated)

    def open_crit_high_count(self):
        return self._open_ch

    def contested_count(self, *_a, **_k):
        return self._contested

    def undemonstrated_subcritical_ids(self, *_a, **_k):
        return list(self._undemonstrated)


class TestI07StallConvergence:
    """A stall is two counts staying EXACTLY static across a window while the decay
    slope is high. A run whose counts move is not stalled, however high the slope."""

    BASE = dict(stall_window=3, stall_earliest_round=5,
                stall_gamma_terminate=0.45, stall_gamma_advisory=0.30,
                stall_gamma_termination_enabled=True)

    def test_fires_on_a_genuinely_static_window(self):
        cfg = _cfg(**self.BASE)
        hist = [{"open_ch": 4, "contested": 1}, {"open_ch": 4, "contested": 1}]
        res = rr._check_stall_convergence(
            round_idx=9, registry=_FakeRegistry(4, 1), gamma=0.60,
            stall_history=hist, cfg=cfg)
        assert res["stalled"] is True, f"known-GOOD stall not detected: {res['reason']}"
        assert res["terminate"] is True

    def test_does_not_fire_when_the_counts_are_moving(self):
        """KNOWN-BAD: identical gamma, but the counts change. Must NOT stall."""
        cfg = _cfg(**self.BASE)
        hist = [{"open_ch": 7, "contested": 3}, {"open_ch": 5, "contested": 2}]
        res = rr._check_stall_convergence(
            round_idx=9, registry=_FakeRegistry(4, 1), gamma=0.60,
            stall_history=hist, cfg=cfg)
        assert res["stalled"] is False, (
            "stall declared on a run whose open-critical and contested counts were "
            "still moving — it would end live runs early"
        )

    def test_respects_the_earliest_round_guard(self):
        cfg = _cfg(**self.BASE)
        hist = [{"open_ch": 4, "contested": 1}, {"open_ch": 4, "contested": 1}]
        res = rr._check_stall_convergence(
            round_idx=1, registry=_FakeRegistry(4, 1), gamma=0.99,
            stall_history=hist, cfg=cfg)
        assert res["stalled"] is False, "fired before stall_earliest_round"

    def test_discriminates_between_the_two_inputs(self):
        cfg = _cfg(**self.BASE)
        static = rr._check_stall_convergence(
            round_idx=9, registry=_FakeRegistry(4, 1), gamma=0.60,
            stall_history=[{"open_ch": 4, "contested": 1}] * 2, cfg=cfg)["stalled"]
        moving = rr._check_stall_convergence(
            round_idx=9, registry=_FakeRegistry(4, 1), gamma=0.60,
            stall_history=[{"open_ch": 7, "contested": 3},
                           {"open_ch": 5, "contested": 2}], cfg=cfg)["stalled"]
        assert static != moving, "stall check returns the same verdict for opposite inputs"


# ---------------------------------------------------------------------------
# I08 — budget extension (_check_budget_extension)
# ---------------------------------------------------------------------------
class TestI08BudgetExtension:
    """Records this component's measured state as of 2026-08-25.

    Its own docstring records that it raised NameError on EVERY call after 1cec60d,
    unnoticed because it is only reached at round_idx == max_rounds - 1 and exp44-49
    all converged first. The parameter is present now, so the test below is the
    regression pin that would have caught it.

    Founder position 2026-08-25: the mechanism has never produced a measurable
    benefit and only ever cost money, and should probably be removed. Independently
    measured: only the 14 exp39 configs permit an extension at all — NO config from
    exp40 onward sets extension_cap above max_rounds — so it cannot fire in the
    current arc. These tests pin behaviour so that a later removal is a deliberate
    deletion of something understood, not of something unexamined.
    """

    def test_it_is_callable_without_raising(self):
        """The regression pin for the NameError that went unseen for a month."""
        try:
            rr._check_budget_extension(
                round_idx=5, registry=_FakeRegistry(3, 1),
                gamma=0.20, gamma_prev=0.18, cfg=_cfg())
        except NameError as exc:  # pragma: no cover - the defect being pinned
            pytest.fail(f"_check_budget_extension raised NameError again: {exc}")

    def test_returns_a_two_tuple_of_decision_and_reason(self):
        out = rr._check_budget_extension(
            round_idx=5, registry=_FakeRegistry(3, 1),
            gamma=0.20, gamma_prev=0.18, cfg=_cfg())
        assert isinstance(out, tuple) and len(out) == 2
        assert isinstance(out[0], bool), "a verdict component must return a boolean"

    def test_no_modern_config_permits_an_extension(self):
        """Measured claim, pinned: extension is inert for the whole exp40+ arc."""
        import glob, json, os
        offenders = []
        for path in glob.glob("bench/exp[45]*_configs/*.json"):
            try:
                j = json.load(open(path))
            except Exception:
                continue
            mr, ec = j.get("max_rounds"), j.get("extension_cap")
            if mr is not None and ec is not None and ec > mr:
                offenders.append(os.path.basename(path))
        assert not offenders, (
            f"a modern config re-enabled the budget extension: {offenders}. "
            "The standing corrective is extension_cap == max_rounds."
        )


# ---------------------------------------------------------------------------
# I04 — the state-convergence check (_check_state_convergence)
# ---------------------------------------------------------------------------
class TestI04StateConvergence:
    """Converges only when the underlying gate passes for N CONSECUTIVE rounds.
    One passing round must not be enough, or a single quiet round ends a run."""

    BASE = dict(consecutive_rounds_required=3, earliest_stop_round=2,
                max_open_crit_high=5, rho_threshold=0.0,
                open_ch_stability_window=1)

    def _call(self, history, cfg, open_ch=0, novel=0):
        return rr._check_state_convergence(
            round_idx=9, registry=_FakeRegistry(open_ch, 0), novel_this_round=novel,
            gamma=0.60, gate_history=list(history), cfg=cfg,
            open_ch_history=[open_ch, open_ch, open_ch], rho_rolling_avg=1.0)

    def test_fires_after_enough_consecutive_passes(self):
        cfg = _cfg(**self.BASE)
        ok, reason = self._call([True, True], cfg)
        assert ok is True, f"known-GOOD input did not converge: {reason}"
        assert "STATE_CONVERGED" in reason

    def test_does_not_fire_on_a_single_pass(self):
        """KNOWN-BAD: the gate passes this round but not consecutively."""
        cfg = _cfg(**self.BASE)
        ok, reason = self._call([False, False], cfg)
        assert ok is False, (
            "converged on one passing round — a single quiet round would end a run"
        )

    def test_does_not_fire_with_too_many_open_criticals(self):
        """KNOWN-BAD: unresolved critical findings above the configured ceiling."""
        cfg = _cfg(**self.BASE)
        ok, _ = self._call([True, True], cfg, open_ch=99)
        assert ok is False, "converged while critical findings were still open"

    def test_discriminates_between_the_two_inputs(self):
        cfg = _cfg(**self.BASE)
        good, _ = self._call([True, True], cfg)
        bad, _ = self._call([False, False], cfg)
        assert good != bad, "state check returns the same verdict for opposite inputs"
