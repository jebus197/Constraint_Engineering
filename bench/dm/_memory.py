"""CDSFL Dynamic Management — Persistent Immune Memory (Phase 4).

Cross-experiment memory that learns per-flaw-class confirmation rates and
blends them into the base prior for R_k(0). Advisory-only: memory informs
but never overrides pipeline verdicts.

Key properties:
- Per-flaw-class (confirmed, rejected) counts with exponential decay
- Beta-Binomial smoothed pi_mem for each flaw class
- Blended prior: pi = (1 - rho) * pi_base + rho * pi_mem
- CUSUM drift detection: flags when incoming flaw rates diverge from memory
- JSON persistence with file-hash grounding for invalidation
- Advisory-only: memory cannot override pipeline verdicts

Created: 12 April 2026 (Phase 4 — Persistent Memory).
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger("cdsfl.memory")


@dataclass
class FlawClassRecord:
    """Per-flaw-class memory record.

    Tracks confirmed/rejected counts across experiments with exponential
    decay so recent experiments weigh more than distant ones.
    """

    flaw_class: int
    confirmed: float = 0.0  # decayed confirmed count
    rejected: float = 0.0  # decayed rejected count
    experiments_seen: int = 0  # number of experiments contributing

    @property
    def total(self) -> float:
        return self.confirmed + self.rejected

    def to_dict(self) -> dict:
        return {
            "flaw_class": self.flaw_class,
            "confirmed": self.confirmed,
            "rejected": self.rejected,
            "experiments_seen": self.experiments_seen,
        }

    @classmethod
    def from_dict(cls, d: dict) -> FlawClassRecord:
        return cls(
            flaw_class=d["flaw_class"],
            confirmed=d.get("confirmed", 0.0),
            rejected=d.get("rejected", 0.0),
            experiments_seen=d.get("experiments_seen", 0),
        )


@dataclass
class DriftState:
    """CUSUM drift detector state for one flaw class."""

    cusum_pos: float = 0.0
    cusum_neg: float = 0.0
    drift_detected: bool = False


class ImmuneMemory:
    """Persistent cross-experiment immune memory.

    Stores per-flaw-class confirmation rates from prior experiments and
    provides a blended prior for R_k(0) initialisation. Advisory-only:
    the blended prior is a suggestion, not a mandate.

    Example::

        mem = ImmuneMemory(decay_rate=0.1, drift_threshold=2.0)
        mem.record_experiment(exp_id="exp37", flaw_counts={
            0: (10, 2),  # flaw_class 0: 10 confirmed, 2 rejected
            1: (5, 8),   # flaw_class 1: 5 confirmed, 8 rejected
        })
        pi = mem.blended_prior(flaw_class=0, pi_base=0.5, rho=0.2)
    """

    # Beta-Binomial smoothing pseudocounts (Jeffreys prior)
    ALPHA_0: float = 0.5
    BETA_0: float = 0.5

    def __init__(
        self,
        decay_rate: float = 0.1,
        drift_threshold: float = 2.0,
        source_hash: Optional[str] = None,
    ) -> None:
        self.decay_rate = decay_rate
        self.drift_threshold = drift_threshold
        self.source_hash = source_hash  # hash of source files for invalidation
        self._records: Dict[int, FlawClassRecord] = {}
        self._drift: Dict[int, DriftState] = {}
        self._experiment_count: int = 0

    def record_experiment(
        self,
        exp_id: str,
        flaw_counts: Dict[int, Tuple[int, int]],
    ) -> None:
        """Ingest results from a completed experiment.

        Args:
            exp_id: Experiment identifier (for logging).
            flaw_counts: {flaw_class: (confirmed_count, rejected_count)}.
        """
        # Apply decay to all existing records before adding new data
        decay_factor = math.exp(-self.decay_rate)
        for rec in self._records.values():
            rec.confirmed *= decay_factor
            rec.rejected *= decay_factor

        # Add new observations
        for fc, (confirmed, rejected) in flaw_counts.items():
            if fc not in self._records:
                self._records[fc] = FlawClassRecord(flaw_class=fc)
            rec = self._records[fc]
            rec.confirmed += confirmed
            rec.rejected += rejected
            rec.experiments_seen += 1

        self._experiment_count += 1
        logger.info(
            "Recorded experiment %s (total: %d experiments, %d flaw classes)",
            exp_id, self._experiment_count, len(self._records),
        )

    def pi_mem(self, flaw_class: int) -> float:
        """Beta-Binomial smoothed confirmation rate for a flaw class.

        pi_mem = (confirmed + alpha_0) / (confirmed + rejected + alpha_0 + beta_0)

        Returns value in (0, 1) — never exactly 0 or 1 due to pseudocounts.
        """
        rec = self._records.get(flaw_class)
        if rec is None:
            # No data: return uninformative prior
            return self.ALPHA_0 / (self.ALPHA_0 + self.BETA_0)

        return (rec.confirmed + self.ALPHA_0) / (
            rec.confirmed + rec.rejected + self.ALPHA_0 + self.BETA_0
        )

    def blended_prior(
        self,
        flaw_class: int,
        pi_base: float,
        rho: float,
    ) -> float:
        """Compute blended prior: pi = (1 - rho) * pi_base + rho * pi_mem.

        Advisory-only: this value SUGGESTS a prior, it does not override
        the pipeline's own verdict computation.

        Args:
            flaw_class: The flaw class to compute prior for.
            pi_base: Base prior (from domain config or uniform).
            rho: Blending weight in [0, 1]. 0 = ignore memory entirely.

        Returns:
            Blended prior in [0, 1].
        """
        pm = self.pi_mem(flaw_class)
        return (1.0 - rho) * pi_base + rho * pm

    def update_drift(
        self,
        flaw_class: int,
        observed_rate: float,
    ) -> bool:
        """CUSUM drift detection for a flaw class.

        Compares observed confirmation rate against memory prediction.
        Returns True if drift is detected (incoming data diverges from
        memory enough to warrant caution).

        Uses two-sided CUSUM: detects both upward and downward shifts.
        """
        expected = self.pi_mem(flaw_class)
        residual = observed_rate - expected

        if flaw_class not in self._drift:
            self._drift[flaw_class] = DriftState()
        ds = self._drift[flaw_class]

        # Two-sided CUSUM
        ds.cusum_pos = max(0.0, ds.cusum_pos + residual)
        ds.cusum_neg = min(0.0, ds.cusum_neg + residual)

        ds.drift_detected = (
            ds.cusum_pos > self.drift_threshold
            or abs(ds.cusum_neg) > self.drift_threshold
        )

        if ds.drift_detected:
            logger.warning(
                "Drift detected for flaw_class %d: CUSUM+ = %.3f, CUSUM- = %.3f "
                "(threshold: %.3f). Memory predictions may be stale.",
                flaw_class, ds.cusum_pos, ds.cusum_neg, self.drift_threshold,
            )

        return ds.drift_detected

    def is_drifting(self, flaw_class: int) -> bool:
        """Check if a flaw class has active drift detection."""
        ds = self._drift.get(flaw_class)
        return ds.drift_detected if ds else False

    def reset_drift(self, flaw_class: int) -> None:
        """Reset drift detector for a flaw class."""
        self._drift.pop(flaw_class, None)

    # --- Persistence ---

    @staticmethod
    def compute_source_hash(file_paths: List[str]) -> str:
        """Compute SHA-256 hash of source files for invalidation.

        If source code changes significantly, memory built on old code
        may no longer be valid. The hash allows detection of this.
        """
        h = hashlib.sha256()
        for path in sorted(file_paths):
            try:
                with open(path, "rb") as f:
                    h.update(f.read())
            except (OSError, IOError):
                h.update(path.encode("utf-8"))
        return h.hexdigest()

    def save(self, path: str) -> None:
        """Save memory state to JSON file."""
        data = {
            "version": 1,
            "experiment_count": self._experiment_count,
            "decay_rate": self.decay_rate,
            "drift_threshold": self.drift_threshold,
            "source_hash": self.source_hash,
            "records": {
                str(fc): rec.to_dict() for fc, rec in self._records.items()
            },
        }
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        logger.info("Saved immune memory to %s", path)

    @classmethod
    def load(
        cls,
        path: str,
        expected_hash: Optional[str] = None,
    ) -> ImmuneMemory:
        """Load memory state from JSON file.

        Args:
            path: Path to JSON file.
            expected_hash: If provided, invalidate memory if source hash
                          doesn't match (code has changed).

        Returns:
            Loaded ImmuneMemory instance. If file doesn't exist or hash
            mismatches, returns a fresh (empty) instance.
        """
        p = Path(path)
        if not p.exists():
            logger.info("No memory file at %s, starting fresh", path)
            return cls()

        try:
            with open(path) as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load memory from %s: %s", path, exc)
            return cls()

        stored_hash = data.get("source_hash")
        if expected_hash and stored_hash and stored_hash != expected_hash:
            logger.warning(
                "Source hash mismatch (stored: %s, current: %s). "
                "Memory invalidated — starting fresh.",
                stored_hash[:12], expected_hash[:12],
            )
            return cls(
                decay_rate=data.get("decay_rate", 0.1),
                drift_threshold=data.get("drift_threshold", 2.0),
                source_hash=expected_hash,
            )

        mem = cls(
            decay_rate=data.get("decay_rate", 0.1),
            drift_threshold=data.get("drift_threshold", 2.0),
            source_hash=stored_hash,
        )
        mem._experiment_count = data.get("experiment_count", 0)
        for fc_str, rec_dict in data.get("records", {}).items():
            rec = FlawClassRecord.from_dict(rec_dict)
            mem._records[rec.flaw_class] = rec

        logger.info(
            "Loaded immune memory from %s (%d experiments, %d flaw classes)",
            path, mem._experiment_count, len(mem._records),
        )
        return mem
