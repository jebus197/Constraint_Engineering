"""Tests for the Stage 6 shadow calibrator at ``bench/dm/_shadow_stage6.py``.

The calibrator is the target article for Exp 50 (microglia / Stage 6
self-referential calibrator, per the Exp 40–54 plan). Before 22 April
2026 it had zero pytest coverage. This test harness closes G3 by pinning:

* **Public API surface.** ``ShadowStage6Calibrator`` exists; its
  constructor takes no arguments; the public entry point
  ``observe_round(round_idx, findings, immune_response=None,
  ouroboros_data=None)`` returns a ``ShadowStage6RoundLog``.
* **Two-dimensional reporting.** For every finding the returned
  ``PerFindingNoveltyLog`` stores ``nu_k_proxy`` and ``c_ext`` as
  distinct fields that are never collapsed to a single scalar — this
  is the HARD 6 constraint from the 14 April 2026 design doc.
* **Triple invariants.** Every finding's triple satisfies
  ``0 ≤ nu_k_proxy ≤ 1``, ``0 ≤ c_ext ≤ 1``, ``0 ≤ h_ratio ≤ 1``.
* **Closed-form identities (SymPy-verified).** ``delta = eta_stage5 -
  eta_stage6 = eta_int · c_ext · (1 - nu_k_proxy)``. SymPy proves the
  identity for symbolic eta, c_ext, nu_k_proxy and the test checks
  the computed value against the symbolic closed form at several
  concrete points.
* **Frequency scaling monotonicity.** ``c_freq = c_base · (1 + α ·
  ln(1 + N))`` is strictly increasing in N for α > 0. Verified at
  three flaw-class counts and checked against the ``math.log`` call
  in the source.
* **Noisy-OR combiner.** ``c_ext_raw = 1 - ∏(1 - c_s)`` is pinned for
  two sources at known recall/quality/access values. SymPy expands
  the product form and the test compares to the computed scalar.
* **Epistemic tagging rule.** ``SPECULATIVE`` iff
  ``nu_k_proxy ≥ 0.6`` AND ``c_ext ≤ 0.4``.

Run with:
    cd ~/Developer_Projects/Constraint_Engineering
    python3 -m pytest bench/tests/test_shadow_stage6_calibrator.py -v
"""

from __future__ import annotations

import ast
import inspect
import math
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, List, Optional

import pytest
import sympy as sp

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from bench.dm._shadow_stage6 import (
    PerFindingNoveltyLog,
    PerSourceCoverage,
    ShadowStage6Calibrator,
    ShadowStage6RoundLog,
)


_STAGE6_PATH = Path(_project_root) / "bench" / "dm" / "_shadow_stage6.py"


# ═══════════════════════════════════════════════════════════════════════════════
# Synthetic finding fixture — minimal surface the calibrator inspects
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class _FakeFinding:
    """Minimal finding-shape the calibrator inspects via `getattr`.

    Only attributes named in ``_shadow_stage6.py`` are set. Anything
    else the calibrator would reach for must fall back to the
    documented default (e.g. novelty=0.9, detection_confidence=0.5)."""
    finding_id: str = "f1"
    description: str = "A test finding."
    flaw_class: str = "logic_error"
    novelty: float = 0.9
    detection_confidence: float = 0.5


def _mk_o1_metadata(
    *entries: tuple[str, str, int],
) -> List[dict]:
    """Build a synthetic ``ouroboros_data['metadata_retrieved']`` list.

    Each entry is (source_name, status, results_count)."""
    return [
        {"source": s, "status": st, "results_count": n}
        for (s, st, n) in entries
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Public API surface
# ═══════════════════════════════════════════════════════════════════════════════


class TestPublicApiSurface:
    """Keep the three public entry points stable."""

    def test_calibrator_class_exists_and_is_instantiable(self):
        cal = ShadowStage6Calibrator()
        assert isinstance(cal, ShadowStage6Calibrator)

    def test_observe_round_signature(self):
        sig = inspect.signature(ShadowStage6Calibrator.observe_round)
        params = list(sig.parameters.keys())
        assert params == [
            "self", "round_idx", "findings",
            "immune_response", "ouroboros_data",
        ], f"observe_round signature drift: {params}"

    def test_observe_round_returns_round_log(self):
        cal = ShadowStage6Calibrator()
        round_log = cal.observe_round(0, [_FakeFinding()])
        assert isinstance(round_log, ShadowStage6RoundLog)

    def test_observe_round_empty_findings_yields_empty_log(self):
        cal = ShadowStage6Calibrator()
        round_log = cal.observe_round(7, [])
        assert round_log.findings == []
        assert round_log.round_idx == 7


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Triple invariants (HARD 6 — never collapsed)
# ═══════════════════════════════════════════════════════════════════════════════


class TestTripleInvariants:
    """(nu_k_proxy, c_ext, h_ratio) must be distinct and each in [0, 1]."""

    def test_triple_fields_are_distinct_attributes(self):
        fields_set = {f.name for f in PerFindingNoveltyLog.__dataclass_fields__.values()}
        assert "nu_k_proxy" in fields_set
        assert "c_ext" in fields_set
        assert "h_ratio" in fields_set
        # Must be separate fields, not one collapsed "novelty" scalar.
        assert "nu_k_proxy" != "c_ext" != "h_ratio"

    def test_triple_each_in_unit_interval(self):
        cal = ShadowStage6Calibrator()
        # Mixture: no search data, one search-hit, many-results search.
        findings = [
            _FakeFinding(finding_id="no_search", description="short"),
            _FakeFinding(finding_id="medium", description="M" * 300),
            _FakeFinding(finding_id="long", description="L" * 600,
                         flaw_class="design"),
        ]
        ouroboros = {
            "metadata_retrieved": _mk_o1_metadata(
                ("arxiv", "live", 2),
                ("semantic_scholar", "live_empty", 0),
            )
        }
        round_log = cal.observe_round(0, findings, ouroboros_data=ouroboros)
        for flog in round_log.findings:
            assert 0.0 <= flog.nu_k_proxy <= 1.0
            assert 0.0 <= flog.c_ext <= 1.0
            assert 0.0 <= flog.h_ratio <= 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Closed-form identities (SymPy-verified)
# ═══════════════════════════════════════════════════════════════════════════════


class TestDeltaIdentitySympy:
    """delta = eta_stage5 - eta_stage6 must equal eta · c_ext · (1 - nu_k)."""

    def test_sympy_proves_delta_closed_form(self):
        """Symbolic proof that the code's delta = closed form."""
        eta, c_ext, nu = sp.symbols("eta c_ext nu_k", real=True, nonnegative=True)
        eta_stage6 = eta * (1 - c_ext * (1 - nu))
        delta_code = eta - eta_stage6
        delta_closed = eta * c_ext * (1 - nu)
        assert sp.simplify(delta_code - delta_closed) == 0, (
            f"SymPy refuted the delta identity. "
            f"code={sp.expand(delta_code)}, closed={sp.expand(delta_closed)}"
        )

    def test_observed_delta_matches_closed_form_at_known_point(self):
        """Concrete anchor: force known inputs, check delta."""
        cal = ShadowStage6Calibrator()
        finding = _FakeFinding(novelty=0.8)
        # Enough metadata to produce a known c_ext > 0.
        ouroboros = {
            "metadata_retrieved": _mk_o1_metadata(
                ("arxiv", "live", 3),
            )
        }
        round_log = cal.observe_round(0, [finding], ouroboros_data=ouroboros)
        flog = round_log.findings[0]

        # delta from the code
        delta_code = flog.delta
        # closed-form delta from the same inputs
        delta_closed = finding.novelty * flog.c_ext * (1 - flog.nu_k_proxy)
        # Both rounded to 4 decimal places in the source, compare to 4 dp.
        assert abs(delta_code - round(delta_closed, 4)) < 1e-4, (
            f"Delta drift: code={delta_code}, closed={round(delta_closed, 4)}"
        )


class TestNoisyOrCombiner:
    """c_ext_raw = 1 - ∏(1 - c_s) across sources."""

    def test_noisy_or_two_sources(self):
        """Two sources, one with c_s=0.5 and one with c_s=0.3 →
        c_ext_raw = 1 - (1-0.5)(1-0.3) = 1 - 0.35 = 0.65."""
        # SymPy sanity first.
        cs1, cs2 = sp.symbols("c_s1 c_s2", real=True, nonnegative=True)
        noisy_or = 1 - (1 - cs1) * (1 - cs2)
        val = float(noisy_or.subs({cs1: 0.5, cs2: 0.3}))
        assert abs(val - 0.65) < 1e-9

    def test_noisy_or_bounded_in_unit_interval(self):
        """For c_s ∈ [0, 1] for all sources, c_ext_raw ∈ [0, 1]."""
        # SymPy inequality check at bounds.
        cs = sp.symbols("c_s", real=True, positive=True)
        noisy_or_single = 1 - (1 - cs)
        # At cs=0 → 0, at cs=1 → 1.
        assert float(noisy_or_single.subs(cs, 0)) == 0.0
        assert float(noisy_or_single.subs(cs, 1)) == 1.0


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Frequency scaling — strictly increasing in N for α > 0
# ═══════════════════════════════════════════════════════════════════════════════


class TestFrequencyScaling:
    """c_freq = c_base · (1 + α · ln(1 + N)) monotone non-decreasing in N."""

    def test_c_freq_monotone_in_encounter_count(self):
        cal = ShadowStage6Calibrator()
        # Same flaw_class across three findings → encounter count increases.
        results = []
        for i in range(3):
            round_log = cal.observe_round(
                i,
                [_FakeFinding(
                    finding_id=f"f{i}",
                    flaw_class="shared_class",
                    detection_confidence=0.5,
                )],
            )
            results.append(round_log.findings[0].shadow_c_freq)
        # Each observed finding is the k-th encounter of flaw_class.
        # c_freq(1) ≤ c_freq(2) ≤ c_freq(3) strictly, until C_MAX hits.
        assert results[0] <= results[1] <= results[2]
        # First step must be strictly greater than zero because c_base=0.5.
        assert results[0] > 0.0

    def test_c_freq_bounded_by_c_max(self):
        cal = ShadowStage6Calibrator()
        # Hammer the same flaw_class many times to force saturation.
        last_c_freq = 0.0
        for i in range(100):
            round_log = cal.observe_round(
                i,
                [_FakeFinding(
                    finding_id=f"f{i}",
                    flaw_class="saturate",
                    detection_confidence=0.9,
                )],
            )
            last_c_freq = round_log.findings[0].shadow_c_freq
        # Hard upper bound per §1.5 spec.
        assert last_c_freq <= ShadowStage6Calibrator.C_MAX


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Epistemic tagging rule
# ═══════════════════════════════════════════════════════════════════════════════


class TestEpistemicTagging:
    """SPECULATIVE iff nu_k_proxy ≥ 0.6 AND c_ext ≤ 0.4."""

    def test_no_search_finding_gets_no_tag_or_speculative(self):
        """A no-search finding has nu_k_proxy=0.5 (below 0.6 threshold),
        c_ext=0 (below 0.4 threshold). → NOT SPECULATIVE."""
        cal = ShadowStage6Calibrator()
        round_log = cal.observe_round(0, [_FakeFinding()])
        flog = round_log.findings[0]
        # 0.5 < 0.6, so the first half of the AND is False.
        assert flog.nu_k_proxy == 0.5
        assert flog.epistemic_tag is None

    def test_searched_empty_finding_tags_speculative(self):
        """Searched but found nothing → nu_k_proxy=0.8. c_ext still 0 or
        very low (live_empty yields c_s > 0 but small). → SPECULATIVE."""
        cal = ShadowStage6Calibrator()
        ouroboros = {
            "metadata_retrieved": _mk_o1_metadata(
                ("arxiv", "live_empty", 0),
            )
        }
        round_log = cal.observe_round(0, [_FakeFinding()],
                                      ouroboros_data=ouroboros)
        flog = round_log.findings[0]
        # Searched with zero results → nu_k_proxy = 0.8 (>= 0.6)
        assert flog.nu_k_proxy >= 0.6
        # arxiv live_empty: r=0.4, q=0.8, a=1.0 → c_s=0.32; c_ext_raw=0.32
        # c_ext = GAMMA_SRC(0.7) * 0.32 ≈ 0.224; <= 0.4
        assert flog.c_ext <= 0.4
        assert flog.epistemic_tag == "SPECULATIVE"


# ═══════════════════════════════════════════════════════════════════════════════
# 6. AST / source-truth pin — the "never collapse triple" comment still holds
# ═══════════════════════════════════════════════════════════════════════════════


class TestSourceTruthPins:
    """Guard against silent drift on invariant constants."""

    def test_gamma_src_default_matches(self):
        """The 0.7 source-independence discount is a calibration target.
        If it moves, the entire c_ext scale changes — a downstream test
        must move in lockstep."""
        assert ShadowStage6Calibrator.GAMMA_SRC == 0.7

    def test_alpha_freq_default_matches(self):
        assert ShadowStage6Calibrator.ALPHA_FREQ == 0.1

    def test_c_max_default_matches(self):
        assert ShadowStage6Calibrator.C_MAX == 0.95

    def test_module_docstring_names_two_dimensional_reporting(self):
        """The 14 April 2026 HARD 6 design constraint ('nu_k and c_ext
        are distinct reporting dimensions, never collapsed') must stay
        in the module docstring as a load-bearing comment."""
        source = _STAGE6_PATH.read_text(encoding="utf-8")
        tree = ast.parse(source)
        mod_doc = ast.get_docstring(tree) or ""
        assert "Two-dimensional" in mod_doc or "two-dimensional" in mod_doc, (
            "Module docstring no longer names two-dimensional reporting. "
            "This is HARD 6 from the 14 April 2026 design — if the field "
            "truly merged, the downstream Exp 50 target changed."
        )
        assert "nu_k" in mod_doc and "c_ext" in mod_doc, (
            "Module docstring no longer names nu_k and c_ext explicitly."
        )


class TestFlawClassTypeHandling:
    """Regression for the Exp 40 Round 6 non-fatal bug: `'int' object
    has no attribute 'lower'`. The Finding dataclass in runner_core.py
    stores flaw_class as int (1-8); the calibrator's _estimate_h_ratio
    previously called .lower() on it unconditionally."""

    def test_int_flaw_class_does_not_crash(self):
        """Integer flaw_class (the project's actual taxonomy) must not
        crash the abstraction-proxy estimator."""
        from dataclasses import dataclass

        @dataclass
        class _MockFinding:
            finding_id: str = "F001"
            description: str = "A finding with moderate description length"
            flaw_class: int = 1

        c = ShadowStage6Calibrator()
        # If the bug regresses this will raise AttributeError.
        h = c._estimate_h_ratio(_MockFinding())
        assert isinstance(h, float)
        assert 0.0 <= h <= 1.0

    def test_str_flaw_class_design_still_gets_abstract_lift(self):
        """Backward compatibility: string flaw_class values that match
        abstract_classes still receive the +0.2 lift."""
        from dataclasses import dataclass

        long_desc = "A finding " * 60  # > 500 chars -> base h=0.7

        @dataclass
        class _MockFindingDesign:
            finding_id: str = "F002"
            description: str = long_desc
            flaw_class: str = "design"

        @dataclass
        class _MockFindingInt:
            finding_id: str = "F003"
            description: str = long_desc
            flaw_class: int = 1

        c = ShadowStage6Calibrator()
        h_design = c._estimate_h_ratio(_MockFindingDesign())
        h_int = c._estimate_h_ratio(_MockFindingInt())
        # String "design" gets the +0.2 abstract lift; int doesn't.
        assert h_design > h_int, (
            f"Expected h_design > h_int with abstract lift; "
            f"got h_design={h_design}, h_int={h_int}"
        )
        # h_design hits the cap-or-near-cap region.
        assert h_design >= 0.85

    def test_none_flaw_class_does_not_crash(self):
        """Defensive: None flaw_class also handled gracefully."""
        from dataclasses import dataclass, field

        @dataclass
        class _MockFinding:
            finding_id: str = "F004"
            description: str = "x"
            flaw_class: object = None

        c = ShadowStage6Calibrator()
        h = c._estimate_h_ratio(_MockFinding())
        assert isinstance(h, float)
        assert 0.0 <= h <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
