"""Shadow Stage 6 Calibration Logger.

Observation-only instrumentation for Exp 39. Collects the data needed
to calibrate the literature-calibrated extension parameters post-experiment:

  - Per-finding (nu_k_proxy, c_ext, H_ratio) triple
  - Per-source coverage data (c_s components)
  - Per-tool pass/fail rates (fail fraction as FPR proxy)
  - Shadow eta_combined (literature-calibrated vs baseline delta)
  - Shadow E-value computation (e = 1/fail_fraction proxy)
  - Shadow d_eff from E_combined (E-value to detection coupling)
  - Frequency-scaled detection confidence (c_freq from encounter counts)
  - Epistemic marking (SPECULATIVE tag for unverified-novel)
  - Per-pair source co-occurrence (for correlation estimation)

Zero effect on the load-bearing verdict path. All outputs are logged
to disk alongside existing shadow cell logs.

Design: 14 April 2026. Two-dimensional (nu_k, c_ext) reporting.
nu_k and c_ext are distinct reporting dimensions, never collapsed.
"""

from __future__ import annotations

import json
import logging
import math
import time
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger("cdsfl.shadow_stage6")


@dataclass
class PerSourceCoverage:
    """Coverage data for a single literature source."""
    source_name: str
    results_count: int = 0
    status: str = "not_queried"  # "live", "live_empty", "shadow_mock", "error"
    # c_s components (r, q, a) — proxies, not calibrated values
    recall_estimate: float = 0.0    # r_s: source recall
    query_quality: float = 0.0     # q_s: query match quality
    access_completeness: float = 0.0  # a_s: retrieval completeness
    c_s: float = 0.0  # computed r * q * a

    def to_dict(self) -> dict:
        return {
            "source_name": self.source_name,
            "results_count": self.results_count,
            "status": self.status,
            "recall_estimate": self.recall_estimate,
            "query_quality": self.query_quality,
            "access_completeness": self.access_completeness,
            "c_s": self.c_s,
        }


@dataclass
class PerFindingNoveltyLog:
    """Shadow novelty assessment for a single finding."""
    finding_id: str
    # Two distinct dimensions (never collapsed)
    nu_k_proxy: float = 0.0   # Retrieval sparsity proxy (NOT novelty — see HARD 6)
    c_ext_raw: float = 0.0    # Raw corroboration before gamma discount
    c_ext: float = 0.0        # Gamma-adjusted search corroboration (0-1)
    h_ratio: float = 0.0      # Abstraction level H/H_max (0-1), context only
    search_status: str = "unknown"  # "searched", "no_search", or "search_failed"
    # Per-source data
    sources: List[PerSourceCoverage] = field(default_factory=list)
    # Shadow eta computation
    eta_stage5: float = 0.0    # Baseline eta (without literature calibration)
    eta_stage6: float = 0.0    # Literature-calibrated eta
    delta: float = 0.0         # eta_stage5 - eta_stage6 (positive = more conservative)
    # Shadow frequency-scaled confidence
    shadow_c_base: float = 0.0  # Base detection confidence
    shadow_c_freq: float = 0.0  # Frequency-scaled: c_base * (1 + alpha * log(1+N))
    flaw_class: str = ""        # For encounter tracking
    encounter_count: int = 0    # N_k at time of assessment
    # Epistemic marking
    epistemic_tag: Optional[str] = None  # "SPECULATIVE" if unverified-novel
    # Metadata
    description_snippet: str = ""

    def to_dict(self) -> dict:
        d = {
            "finding_id": self.finding_id,
            "nu_k_proxy": self.nu_k_proxy,
            "c_ext_raw": self.c_ext_raw,
            "c_ext": self.c_ext,
            "h_ratio": self.h_ratio,
            "search_status": self.search_status,
            "sources": [s.to_dict() for s in self.sources],
            "eta_stage5": self.eta_stage5,
            "eta_stage6": self.eta_stage6,
            "delta": self.delta,
            "shadow_c_base": self.shadow_c_base,
            "shadow_c_freq": self.shadow_c_freq,
            "flaw_class": self.flaw_class,
            "encounter_count": self.encounter_count,
            "description_snippet": self.description_snippet,
        }
        if self.epistemic_tag:
            d["epistemic_tag"] = self.epistemic_tag
        return d


@dataclass
class PerToolFPRLog:
    """Pass/fail tracking for a single verification tool."""
    tool_name: str
    passes: int = 0
    fails: int = 0
    inconclusive: int = 0

    @property
    def total(self) -> int:
        return self.passes + self.fails + self.inconclusive

    @property
    def fail_fraction(self) -> Optional[float]:
        """Fraction of determinate outcomes recorded as fail.

        WARNING: NOT a false positive rate (FPR). FPR = P(PASS | H_0
        true) requires ground-truth labels. This metric conflates tool
        strictness with tool accuracy and can REVERSE tool rankings:
        a strict tool that correctly rejects most findings appears to
        have high fail_fraction, producing low e-values, while a
        permissive tool that incorrectly passes most findings gets
        high e-values. Use for relative calibration only. Production
        e-values require ground-truth finding validity labels.
        """
        denom = self.passes + self.fails
        if denom < 5:  # Need minimum sample
            return None
        return self.fails / denom

    @property
    def shadow_e_pass(self) -> Optional[float]:
        """Shadow e-value for a PASS verdict from this tool.

        e = 1/fail_fraction. See fail_fraction docstring for why this
        is NOT a valid FPR-based e-value. Shadow proxy only.
        """
        ff = self.fail_fraction
        if ff is None or ff == 0.0:
            return None  # Cannot compute; either insufficient data or zero fails
        return 1.0 / ff

    def to_dict(self) -> dict:
        return {
            "tool_name": self.tool_name,
            "passes": self.passes,
            "fails": self.fails,
            "inconclusive": self.inconclusive,
            "total": self.total,
            "fail_fraction": self.fail_fraction,
            "shadow_e_pass": self.shadow_e_pass,
        }


@dataclass
class ShadowStage6RoundLog:
    """Complete calibration data for one round."""
    round_idx: int
    findings: List[PerFindingNoveltyLog] = field(default_factory=list)
    tool_fpr: Dict[str, PerToolFPRLog] = field(default_factory=dict)
    # Aggregate shadow metrics
    mean_nu_k_proxy: float = 0.0
    mean_c_ext: float = 0.0
    mean_delta: float = 0.0
    # Shadow E-value (round-level, from this round's verdicts)
    shadow_e_values: Dict[str, float] = field(default_factory=dict)
    shadow_e_combined: Optional[float] = None
    shadow_d_eff: Optional[float] = None  # d from E_combined
    # Epistemic marking counts
    speculative_count: int = 0
    # Source co-occurrence (for correlation estimation)
    source_cooccurrence: Dict[str, int] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "round_idx": self.round_idx,
            "findings": [f.to_dict() for f in self.findings],
            "tool_fpr": {k: v.to_dict() for k, v in self.tool_fpr.items()},
            "mean_nu_k_proxy": self.mean_nu_k_proxy,
            "mean_c_ext": self.mean_c_ext,
            "mean_delta": self.mean_delta,
            "shadow_e_values": self.shadow_e_values,
            "shadow_e_combined": self.shadow_e_combined,
            "shadow_d_eff": self.shadow_d_eff,
            "speculative_count": self.speculative_count,
            "source_cooccurrence": self.source_cooccurrence,
            "timestamp": self.timestamp,
        }


class ShadowStage6Calibrator:
    """Shadow-mode calibration data collector for literature-calibrated extension.

    Runs after each round alongside existing shadow cells. Collects
    the data needed to calibrate all extension parameters without
    affecting pipeline decisions.

    Shadow instrumentation covers:
    - (nu_k, c_ext, H/H_max) triples and eta deltas
    - E-value computation from tool fail fractions
    - E-value → d_eff coupling
    - Frequency-scaled detection confidence (c_freq)
    - Epistemic marking for unverified-novel findings
    - Source co-occurrence for correlation estimation
    """

    # Default source recall estimates (calibration targets)
    DEFAULT_SOURCE_RECALL = {
        "arxiv": 0.4,             # Good for STEM preprints
        "semantic_scholar": 0.5,  # Broader coverage, citation graph
        "unpaywall": 0.3,         # OA full text only
        "core": 0.2,              # Institutional repos
        "openalex": 0.4,          # Bibliometric metadata
    }

    # Source independence discount (calibration target)
    GAMMA_SRC = 0.7

    # Frequency-scaling coefficient (calibration target)
    ALPHA_FREQ = 0.1

    # Maximum c_freq — prevents frequency alone from reaching certainty (§1.5)
    C_MAX = 0.95

    # E-value significance level
    ALPHA_EVALUE = 0.05  # Threshold = 1/alpha = 20

    def __init__(self) -> None:
        self._round_logs: List[ShadowStage6RoundLog] = []
        self._cumulative_tool_fpr: Dict[str, PerToolFPRLog] = {}
        # Flaw class encounter counts (for c_freq)
        self._flaw_class_counts: Dict[str, int] = defaultdict(int)
        # Source co-occurrence matrix: (src_a, src_b) -> count of rounds
        # where both returned results
        self._source_cooccurrence: Dict[str, Dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

    def observe_round(
        self,
        round_idx: int,
        findings: List[Any],
        immune_response: Optional[Any] = None,
        ouroboros_data: Optional[Dict[str, Any]] = None,
    ) -> ShadowStage6RoundLog:
        """Observe a completed round and compute all shadow data.

        Args:
            round_idx: Index of the completed round.
            findings: Finding objects from the round.
            immune_response: ImmuneResponse with verdicts and cell data.
            ouroboros_data: Shadow data from O1 cell (queries, metadata).

        Returns:
            ShadowStage6RoundLog with per-finding novelty triples,
            tool FPR tracking, shadow E-values, c_freq, epistemic
            tags, and source co-occurrence data.
        """
        round_log = ShadowStage6RoundLog(round_idx=round_idx)

        # --- Per-finding novelty assessment ---
        o1_metadata = []
        if ouroboros_data and isinstance(ouroboros_data, dict):
            o1_metadata = ouroboros_data.get("metadata_retrieved", [])

        for finding in findings:
            flog = self._assess_finding(finding, o1_metadata)
            round_log.findings.append(flog)
            if flog.epistemic_tag:
                round_log.speculative_count += 1

        # --- Per-tool FPR tracking ---
        if immune_response:
            self._track_tool_fpr(immune_response, round_log)

        # --- Shadow E-value computation (round-level) ---
        self._compute_shadow_e_values(immune_response, round_log)

        # --- Source co-occurrence tracking ---
        self._track_source_cooccurrence(o1_metadata, round_log)

        # --- Aggregate metrics ---
        if round_log.findings:
            n = len(round_log.findings)
            round_log.mean_nu_k_proxy = sum(
                f.nu_k_proxy for f in round_log.findings
            ) / n
            round_log.mean_c_ext = sum(
                f.c_ext for f in round_log.findings
            ) / n
            round_log.mean_delta = sum(
                f.delta for f in round_log.findings
            ) / n

        # Copy cumulative FPR into round log
        round_log.tool_fpr = {
            k: PerToolFPRLog(
                tool_name=v.tool_name,
                passes=v.passes,
                fails=v.fails,
                inconclusive=v.inconclusive,
            )
            for k, v in self._cumulative_tool_fpr.items()
        }

        self._round_logs.append(round_log)
        return round_log

    def _assess_finding(
        self,
        finding: Any,
        o1_metadata: List[Dict[str, Any]],
    ) -> PerFindingNoveltyLog:
        """Compute shadow (nu_k, c_ext, H/H_max) + c_freq + epistemic tag."""
        fid = getattr(finding, "finding_id", str(id(finding)))
        desc = getattr(finding, "description", "")[:120]
        flaw_class = getattr(finding, "flaw_class", "unknown")

        # --- Track flaw class encounters (for c_freq) ---
        self._flaw_class_counts[flaw_class] += 1
        n_k = self._flaw_class_counts[flaw_class]

        # --- Estimate H/H_max from finding properties ---
        h_ratio = self._estimate_h_ratio(finding)

        # --- Estimate per-source coverage from O1 data ---
        sources = self._estimate_source_coverage(o1_metadata)

        # --- Compute c_ext from sources (HARD 7: log both raw and adjusted) ---
        if sources:
            product = 1.0
            for s in sources:
                product *= (1.0 - s.c_s)
            c_ext_raw = 1.0 - product
            c_ext = self.GAMMA_SRC * c_ext_raw
        else:
            c_ext_raw = 0.0
            c_ext = 0.0

        # --- Estimate retrieval sparsity (used as nu_k proxy) ---
        nu_k_proxy = self._estimate_retrieval_sparsity(finding, o1_metadata)

        # --- Compute shadow eta ---
        eta_int = getattr(finding, "novelty", 0.9)
        eta_stage6 = eta_int * (1.0 - c_ext * (1.0 - nu_k_proxy))
        delta = eta_int - eta_stage6

        # --- Frequency-scaled detection confidence ---
        # c_freq(k) = c_base * (1 + alpha * log(1 + N_k))
        # N_k here is WITHIN-EXPERIMENT encounter count only (resets per
        # calibrator instance). Section 1.5 defines N_k as a decayed count
        # from persistent memory across prior experiments. Production c_freq
        # requires persistent immune memory (Gap 1 from AIS integration).
        # c_base: use finding's detection confidence if available, else 0.5
        c_base = getattr(finding, "detection_confidence", 0.5)
        c_freq = c_base * (1.0 + self.ALPHA_FREQ * math.log(1.0 + n_k))
        c_freq = min(self.C_MAX, c_freq)  # Bounded at 0.95 per spec §1.5

        # --- Epistemic marking ---
        epistemic_tag = None
        if nu_k_proxy >= 0.6 and c_ext <= 0.4:
            epistemic_tag = "SPECULATIVE"

        # --- Search status (SOFT 6: explicit no-search state) ---
        if o1_metadata:
            has_live = any(
                m.get("status") in ("live", "live_empty")
                for m in o1_metadata
            )
            search_status = "searched" if has_live else "search_failed"
        else:
            search_status = "no_search"

        return PerFindingNoveltyLog(
            finding_id=fid,
            nu_k_proxy=round(nu_k_proxy, 4),
            c_ext_raw=round(c_ext_raw, 4),
            c_ext=round(c_ext, 4),
            h_ratio=round(h_ratio, 4),
            search_status=search_status,
            sources=sources,
            eta_stage5=round(eta_int, 4),
            eta_stage6=round(eta_stage6, 4),
            delta=round(delta, 4),
            shadow_c_base=round(c_base, 4),
            shadow_c_freq=round(c_freq, 4),
            flaw_class=flaw_class,
            encounter_count=n_k,
            epistemic_tag=epistemic_tag,
            description_snippet=desc,
        )

    def _estimate_h_ratio(self, finding: Any) -> float:
        """Estimate H/H_max for a finding.

        Uses finding properties as proxies for abstraction level.
        Real H(x) computation uses the full Abstraction Index (section 7.2).
        """
        flaw_class = getattr(finding, "flaw_class", "")
        desc = getattr(finding, "description", "")

        desc_len = len(desc)
        if desc_len > 500:
            h_proxy = 0.7
        elif desc_len > 200:
            h_proxy = 0.5
        else:
            h_proxy = 0.3

        abstract_classes = {"design", "architecture", "framework", "protocol",
                           "specification", "model", "theory"}
        # Defensive: flaw_class can be int (1-8 per Finding dataclass in
        # runner_core.py) or str. Only apply the abstract-class lift
        # when flaw_class is a string label matching the set. Integer
        # flaw_class values (the project's actual taxonomy) do not
        # match these labels and produce no adjustment, which preserves
        # the existing semantic intent for string-labelled callers
        # without crashing on int values. Bug surfaced in Exp 40 Round 6
        # (15 May 2026 fix): `'int' object has no attribute 'lower'`.
        if isinstance(flaw_class, str) and flaw_class.lower() in abstract_classes:
            h_proxy = min(1.0, h_proxy + 0.2)

        return h_proxy

    def _estimate_source_coverage(
        self,
        o1_metadata: List[Dict[str, Any]],
    ) -> List[PerSourceCoverage]:
        """Extract per-source coverage from O1's search results."""
        sources = []
        seen_sources: Set[str] = set()

        for meta in o1_metadata:
            source_name = meta.get("source", "unknown")
            if source_name in seen_sources:
                continue
            seen_sources.add(source_name)

            status = meta.get("status", "not_queried")
            results_count = meta.get("results_count", 0)

            # Estimate c_s components (proxies — not calibrated values)
            r_s = self.DEFAULT_SOURCE_RECALL.get(source_name, 0.2)
            if status == "live_empty":
                q_s = 0.8   # Query executed successfully; empty space confirmed
            elif status == "live" and results_count > 0:
                q_s = min(1.0, results_count / 3.0)
            else:
                q_s = 0.2   # Error or un-queried
            a_s = 1.0 if status in ("live", "live_empty") else 0.0

            c_s = r_s * q_s * a_s

            sources.append(PerSourceCoverage(
                source_name=source_name,
                results_count=results_count,
                status=status,
                recall_estimate=round(r_s, 3),
                query_quality=round(q_s, 3),
                access_completeness=round(a_s, 3),
                c_s=round(c_s, 4),
            ))

        return sources

    def _estimate_retrieval_sparsity(
        self,
        finding: Any,
        o1_metadata: List[Dict[str, Any]],
    ) -> float:
        """Estimate retrieval sparsity from O1's search result counts.

        WARNING: This is NOT a novelty measurement. It conflates at
        least four quantities: search volume, query breadth, field
        publication density, and actual novelty. A novel finding in a
        sparse field and a known finding with a bad query both score
        high. The field name 'nu_k_proxy' is retained for data
        compatibility but this proxy measures retrieval sparsity only.
        Production nu_k requires embedding-based semantic similarity.
        """
        if not o1_metadata:
            return 0.5  # No search — uncertain, not novel

        total_results = sum(m.get("results_count", 0) for m in o1_metadata)

        if total_results == 0:
            return 0.8  # Searched, found nothing — likely novel
        elif total_results <= 2:
            return 0.6  # Sparse results — possibly novel
        elif total_results <= 5:
            return 0.4  # Moderate results — possibly known
        else:
            return 0.2  # Many results — likely known

    def _track_tool_fpr(
        self,
        immune_response: Any,
        round_log: ShadowStage6RoundLog,
    ) -> None:
        """Track per-tool pass/fail rates."""
        cell_verdicts = getattr(immune_response, "cell_verdicts", {})

        for cell_name, verdicts in cell_verdicts.items():
            if cell_name not in self._cumulative_tool_fpr:
                self._cumulative_tool_fpr[cell_name] = PerToolFPRLog(
                    tool_name=cell_name,
                )

            tracker = self._cumulative_tool_fpr[cell_name]

            for verdict in verdicts:
                v = verdict if isinstance(verdict, str) else getattr(
                    verdict, "verdict", "UNCERTAIN"
                )
                if v in ("CONFIRMED", "PASS"):
                    tracker.passes += 1
                elif v in ("REJECTED", "FAIL"):
                    tracker.fails += 1
                elif v == "DUPLICATE":
                    tracker.inconclusive += 1  # Redundant, not invalid
                else:
                    tracker.inconclusive += 1

    def _compute_shadow_e_values(
        self,
        immune_response: Optional[Any],
        round_log: ShadowStage6RoundLog,
    ) -> None:
        """Compute shadow E-values from this round's verdicts.

        Per-TOOL composition: each tool contributes its e_pass AT MOST
        ONCE per round. The specification requires per-finding composition
        across tools, but the current data structure lacks per-finding-
        per-tool mapping. Per-tool composition is the correct shadow
        approximation. (HARD 1 fix: was per-verdict, causing ~10^12x
        magnitude error.)

        Verdict-to-e mapping per tool:
          Any PASS from tool  -> e = 1/fail_fraction (if available), else 1
          Any FAIL/REJECTED   -> e = 0 (tool found evidence against)
          DUPLICATE           -> e = 1 (inconclusive — redundant, not invalid)
          All UNCERTAIN       -> e = 1 (inconclusive)

        E_combined = product of per-tool e-values.
        d_eff = 1 - 1/(1 + E/T) — sigmoid preserving evidence ordering.

        NOTE: E-values computed from fail_fraction (NOT true FPR).
        fail_fraction = fails/(passes+fails) conflates tool strictness
        with tool accuracy. Can reverse tool rankings. NOT valid for
        production calibration — ground-truth labels required.
        """
        if not immune_response:
            return

        cell_verdicts = getattr(immune_response, "cell_verdicts", {})
        if not cell_verdicts:
            return

        e_combined = 1.0  # Empty product = 1 (inconclusive)
        has_any_evidence = False

        # Per-tool composition: each tool contributes once (HARD 1 fix)
        for cell_name, verdicts in cell_verdicts.items():
            tracker = self._cumulative_tool_fpr.get(cell_name)
            if tracker is None:
                continue

            e_pass = tracker.shadow_e_pass  # 1/fail_fraction or None

            # Reduce this tool's verdicts to a single e-value
            tool_has_pass = False
            tool_has_fail = False
            for verdict in verdicts:
                v = verdict if isinstance(verdict, str) else getattr(
                    verdict, "verdict", "UNCERTAIN"
                )
                if v in ("CONFIRMED", "PASS"):
                    tool_has_pass = True
                elif v in ("REJECTED", "FAIL"):
                    tool_has_fail = True
                # DUPLICATE: e=1 (inconclusive, not invalid — HARD 3 fix)
                # UNCERTAIN: e=1 (inconclusive)

            if tool_has_fail:
                e_combined *= 0.0
                has_any_evidence = True
            elif tool_has_pass and e_pass is not None:
                e_combined *= e_pass  # Contribute once per tool
                has_any_evidence = True
            # else: all inconclusive/duplicate — e=1, no effect

            if e_combined == 0.0:
                break

        if has_any_evidence:
            round_log.shadow_e_combined = round(e_combined, 4)

            # Per-tool shadow e-values (from cumulative data)
            for name, tracker in self._cumulative_tool_fpr.items():
                ep = tracker.shadow_e_pass
                if ep is not None:
                    round_log.shadow_e_values[name] = round(ep, 4)

            # Shadow d_eff: sigmoid mapping (HARD 4 fix).
            # 1 - 1/(1 + E/T) is monotone, concave, never saturates.
            # d(E=T) = 0.50, d(E=5T) = 0.83, d(E->inf) -> 1.0
            threshold = 1.0 / self.ALPHA_EVALUE
            if e_combined > 0:
                round_log.shadow_d_eff = round(
                    1.0 - 1.0 / (1.0 + e_combined / threshold), 4
                )
            else:
                round_log.shadow_d_eff = 0.0

    def _track_source_cooccurrence(
        self,
        o1_metadata: List[Dict[str, Any]],
        round_log: ShadowStage6RoundLog,
    ) -> None:
        """Track which sources returned results together.

        Builds a co-occurrence matrix for post-experiment estimation
        of pairwise source correlation, which could replace the global
        gamma_src discount with per-pair weights.
        """
        # Identify which sources had results this round
        active_sources: Set[str] = set()
        queried_sources: Set[str] = set()

        for meta in o1_metadata:
            source_name = meta.get("source", "unknown")
            status = meta.get("status", "not_queried")
            results_count = meta.get("results_count", 0)

            if status in ("live", "live_empty"):
                queried_sources.add(source_name)
            if status == "live" and results_count > 0:
                active_sources.add(source_name)

        if len(queried_sources) < 2:
            return  # Need at least 2 sources for co-occurrence

        # Update co-occurrence for all queried pairs
        for src_a, src_b in combinations(sorted(queried_sources), 2):
            pair_key = f"{src_a}|{src_b}"
            a_active = src_a in active_sources
            b_active = src_b in active_sources

            if a_active and b_active:
                self._source_cooccurrence[pair_key]["both"] += 1
            elif a_active:
                self._source_cooccurrence[pair_key]["a_only"] += 1
            elif b_active:
                self._source_cooccurrence[pair_key]["b_only"] += 1
            else:
                self._source_cooccurrence[pair_key]["neither"] += 1

        # Snapshot into round log
        round_log.source_cooccurrence = {
            pair: dict(counts)
            for pair, counts in self._source_cooccurrence.items()
        }

    def get_calibration_summary(self) -> Dict[str, Any]:
        """Return cumulative calibration summary across all rounds.

        This is the primary output for post-experiment analysis.
        Includes all shadow metrics for calibration.
        """
        if not self._round_logs:
            return {"rounds_observed": 0}

        all_findings = []
        for rlog in self._round_logs:
            all_findings.extend(rlog.findings)

        n = len(all_findings) if all_findings else 1

        # Count epistemic tags
        speculative_total = sum(
            1 for f in all_findings if f.epistemic_tag == "SPECULATIVE"
        )

        # Latest E-value data (from most recent round with data)
        latest_e = None
        latest_d = None
        for rlog in reversed(self._round_logs):
            if rlog.shadow_e_combined is not None:
                latest_e = rlog.shadow_e_combined
                latest_d = rlog.shadow_d_eff
                break

        return {
            "rounds_observed": len(self._round_logs),
            "findings_assessed": len(all_findings),
            # Two-dimensional novelty
            "mean_nu_k_proxy": round(
                sum(f.nu_k_proxy for f in all_findings) / n, 4
            ),
            "mean_c_ext": round(
                sum(f.c_ext for f in all_findings) / n, 4
            ),
            "mean_h_ratio": round(
                sum(f.h_ratio for f in all_findings) / n, 4
            ),
            "mean_delta": round(
                sum(f.delta for f in all_findings) / n, 4
            ),
            # Frequency-scaled confidence
            "mean_c_base": round(
                sum(f.shadow_c_base for f in all_findings) / n, 4
            ),
            "mean_c_freq": round(
                sum(f.shadow_c_freq for f in all_findings) / n, 4
            ),
            "flaw_class_encounter_counts": dict(self._flaw_class_counts),
            # Epistemic marking
            "speculative_count": speculative_total,
            "speculative_fraction": round(speculative_total / n, 4),
            # E-value shadow
            "latest_shadow_e_combined": latest_e,
            "latest_shadow_d_eff": latest_d,
            "e_value_alpha": self.ALPHA_EVALUE,
            "e_value_threshold": 1.0 / self.ALPHA_EVALUE,
            # Tool data
            "tool_fpr": {
                k: v.to_dict() for k, v in self._cumulative_tool_fpr.items()
            },
            # Source correlation
            "source_cooccurrence": {
                pair: dict(counts)
                for pair, counts in self._source_cooccurrence.items()
            },
            # Parameters used
            "gamma_src_used": self.GAMMA_SRC,
            "alpha_freq_used": self.ALPHA_FREQ,
        }
