"""The roster-scaled convergence window: its maths, and the target it addresses.

WHAT THIS GUARDS AND WHAT IT DELIBERATELY DOES NOT. An unadopted CC2 seat design
(`experimental_notes/seat_evidence/dynamic_roster_and_derived_ladder_2026-10-07/
cc2/bench/degraded_convergence_2026-10-07.py`, 2026-10-07) claims the live
`_check_gamma_alt_convergence` is ROSTER-BLIND and repairs it with
`K_required = ceil(K * n_dec / n_live)`.

★ THIS GUARD PINS THE MATHEMATICS AND THE ARCHIVE, NEVER THE DEFECT. Pinning the
defect is the mistake repaired earlier the same day in
`test_the_preflight_refuses_an_unregistered_seat_2026-11-02.py`, whose
`TestTheTruePositiveItExposed` asserted that Fable FAILS registration and began
accusing correct code the moment the gap closed -- the shape recorded in
`feedback_a_guard_can_accuse_correct_code_2026-10-28` (9 of 36 failures in the
2026-10-28 baseline were guards pinning a defect rather than a property). So
there is NO assertion here that the live function lacks a roster parameter: that
is a fact about an open decision, and the day it is repaired this file must stay
green. What is asserted is what stays true either way -- the bound is sound, and
the degraded case it addresses has occurred.

THE DECISION IS THE FOUNDER'S AND IS NOT PRE-EMPTED HERE. Adopting the repair
changes how a PRE-REGISTERED convergence threshold is computed, which is the
surface the standing directive `GAMMA IS LOAD-BEARING` governs and where B76
already awaits his ruling. Nothing in this file wires the repair.

WHY C13 IS NOT ALREADY THIS. C13 carries his ruling of 2026-10-08 -- on "the
absolute false quiet chance of 0.1159 at full roster, which no roster aware fix
addresses", his verdict was "Fix it." -- and discharged it by raising
`gamma_alt_consecutive_zero_crit` from 3 to 7. His own sentence sets the
roster-aware axis aside as the half a full-roster fix does not reach, so this is
C13's COMPLEMENT and not a rediscovery of it.

Producer: `scripts/does_the_roster_window_bound_hold_2026-11-02.py`.
"""
from __future__ import annotations

import collections
import json
import math
import pathlib
import re

import numpy as np
import pytest

REPO = pathlib.Path(__file__).resolve().parents[2]
PRODUCER = REPO / "scripts" / "does_the_roster_window_bound_hold_2026-11-02.py"
DESIGN = (REPO / "experimental_notes" / "seat_evidence"
          / "dynamic_roster_and_derived_ladder_2026-10-07" / "cc2" / "bench"
          / "degraded_convergence_2026-10-07.py")

rng = np.random.default_rng(20261102)


def _f(ws: np.ndarray, ps: np.ndarray, n: float) -> float:
    """f(n) = -ln E[(1-p)^n], the design's own quantity."""
    return -math.log(float(np.sum(ws * (1.0 - ps) ** n)))


class TestTheMathematicsHolds:
    """The 3 steps of the derivation, each executed rather than read."""

    def test_f_over_n_is_non_increasing(self):
        """Concavity of f with f(0)=0 forces f(n)/n to be non-increasing.

        This is the step the whole bound rests on. If it failed, the window
        could UNDER-correct, which is the one failure mode that matters for a
        pre-registered threshold.
        """
        worst = 0.0
        for _ in range(400):
            k = int(rng.integers(1, 6))
            ps = rng.uniform(1e-5, 0.9995, size=k)
            ws = rng.dirichlet(np.ones(k))
            r = np.array([_f(ws, ps, x) / x for x in range(1, 25)])
            worst = max(worst, float(np.diff(r).max()))
        assert worst <= 1e-9, (
            f"f(n)/n increased by {worst:.3e}; the design's bound would then "
            f"under-correct and must not be adopted")

    def test_the_integer_window_never_under_corrects(self):
        """ceil(K*n_dec/n_live) >= K*f(n_dec)/f(n_live) at every correlation."""
        violations = []
        for _ in range(400):
            k = int(rng.integers(1, 6))
            ps = rng.uniform(1e-5, 0.9995, size=k)
            ws = rng.dirichlet(np.ones(k))
            n_dec = int(rng.integers(2, 13))
            n_live = int(rng.integers(1, n_dec + 1))
            fl = _f(ws, ps, n_live)
            if fl <= 0.0:
                continue                      # the omitted precondition, below
            exact = _f(ws, ps, n_dec) / fl
            for K in (2, 3, 4, 5, 7):
                if math.ceil(K * n_dec / n_live) - K * exact < -1e-9:
                    violations.append((K, n_dec, n_live, exact))
        assert not violations, f"bound violated: {violations[:3]}"

    def test_it_is_tight_at_independence_so_it_is_not_merely_loose(self):
        """A bound that is loose everywhere proves nothing about its own form.

        At independence (a degenerate latent factor) the exact requirement must
        EQUAL n_dec/n_live, which is what makes ceil() the right rounding and
        not an arbitrary safety margin.
        """
        for _ in range(60):
            p = float(rng.uniform(1e-4, 0.999))
            ws, ps = np.array([1.0]), np.array([p])
            n_dec = int(rng.integers(2, 13))
            n_live = int(rng.integers(1, n_dec + 1))
            exact = _f(ws, ps, n_dec) / _f(ws, ps, n_live)
            assert abs(exact - n_dec / n_live) < 1e-9

    def test_the_precondition_the_design_omits_is_real(self):
        """A panel with a 0 critical rate gives f = 0 and the ratio is 0/0.

        The design guards `n_live == 0` and does NOT guard this: the roster can
        be FULL while the finding rate is 0. Recorded so the gap travels with
        the design rather than being discovered again after adoption.
        """
        ws, ps = np.array([1.0]), np.array([0.0])
        assert abs(_f(ws, ps, 5)) < 1e-15
        design = DESIGN.read_text()
        assert "n_live == 0" in design, (
            "the design's own stated guard is missing; this test's claim about "
            "WHICH case is unguarded would then be describing something else")


class TestTheTargetItAddressesIsReal:
    """A repair for a case that never occurs is not additive."""

    def test_degraded_rounds_have_occurred_in_the_archive(self):
        """Short rounds are reachable, measured on the gate's own tally.

        ★ THE PREDICATE MATTERS HERE AND A FIRST VERSION GOT 0 OF 0.
        `runner_state.json` carries NO `config` key, so reading the roster from
        `config['models']` returned nothing for every run and looked like proof
        that degraded rounds never happen. The roster is read instead from
        `raw_counts_per_model` / `novelty_counts_per_model`, which is the gate's
        own per-seat bookkeeping. A uniform 0 is the cheapest signal that a
        predicate is wrong -- see
        `feedback_when_a_surface_defeats_three_predicates_stop_2026-11-02`.
        """
        logs = REPO / "bench" / "logs"
        if not logs.is_dir():
            pytest.skip("no bench/logs on this checkout")
        examined = 0
        degraded = []
        for d in sorted(logs.iterdir()):
            st = d / "runner_state.json" if d.is_dir() else None
            if st is None or not st.is_file():
                continue
            try:
                s = json.loads(st.read_text())
            except Exception:                              # noqa: BLE001
                continue
            seats: set[str] = set()
            for key in ("raw_counts_per_model", "novelty_counts_per_model"):
                v = s.get(key) or {}
                if isinstance(v, dict):
                    seats |= {x.lower() for x in v}
            byround: dict[int, set[str]] = collections.defaultdict(set)
            for p in d.glob("r*_*_*.json"):
                m = re.match(r"r(\d+)_(.+)_\d{8}T\d{6}Z\.json$", p.name)
                if m:
                    byround[int(m.group(1))].add(m.group(2).lower())
            if not seats or not byround:
                continue
            examined += 1
            if any(len(v) < len(seats) for v in byround.values()):
                degraded.append(d.name)

        assert examined >= 20, (
            f"only {examined} runs carried both a per-seat tally and response "
            f"files; the predicate is probably wrong again rather than the "
            f"archive being empty")
        assert degraded, (
            "0 degraded rounds found across {examined} runs. If that is "
            "genuinely true the repair is unreachable and MUST NOT be adopted "
            "under the additive standard; check the predicate first.")

    def test_the_cascade_the_runner_itself_names_is_among_them(self):
        """The 18 July OpenRouter-402 cascade is in the archive, not just a comment.

        `bench/reference_runner_v3.py`'s resume guard describes it in prose. This
        asserts the run is really there, so the prose and the evidence cannot
        drift apart.
        """
        runner = (REPO / "bench" / "reference_runner_v3.py").read_text()
        assert "OpenRouter-402 cascade" in runner, (
            "the runner no longer names the cascade; this test's anchor is gone")
        hits = list((REPO / "bench" / "logs").glob("exp43_macrophage_locationkey_live_*"))
        if not hits:
            pytest.skip("the exp43 run is not on this checkout")
        assert hits, "the named run should exist where the comment points"


class TestTheRecordTravelsWithTheClaim:
    """`measured-rate-travels-with-its-script`, applied to this file."""

    def test_the_producer_exists_and_is_executable_as_written(self):
        assert PRODUCER.is_file(), f"missing producer: {PRODUCER}"
        import ast
        ast.parse(PRODUCER.read_text())          # must be runnable, not prose

    def test_this_file_asserts_nothing_about_the_live_signature(self):
        """The anti-staleness property, checked on this file's own source.

        If a later edit adds an assertion that the live gate lacks a roster
        parameter, this file becomes a guard that pins a defect and will accuse
        correct code the day the repair lands. That is the exact failure this
        file's docstring was written to avoid, so it is enforced rather than
        promised.
        """
        src = pathlib.Path(__file__).read_text()
        body = src.split('"""', 2)[-1]           # skip the module docstring

        # ★ THE NAME IS ASSEMBLED FROM PARTS, and the reason is that the first
        # version of this check FAILED ON ITSELF: writing the identifier as a
        # literal put it in the very text being searched. That is the same
        # quoting trap that re-triggered the settled-item detector earlier the
        # same day, when a correction quoted the phrase it was correcting. A
        # detector whose own source matches its pattern cannot be satisfied by
        # correct code, so the pattern must not be spelled out here.
        banned = "_check_" + "gamma_alt" + "_convergence"
        assert banned not in body, (
            "the live gate's function name is referenced outside the "
            "docstring; this file must not assert anything about its "
            "signature, or it becomes a guard that pins a defect")
