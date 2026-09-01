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

OPERATIONAL STATE (measured 2026-08-12, stated here because the key
properties above read as implemented facts and three of them are not):

* RECORDING is live. Eleven shipped configs set ``immune_memory_enabled``;
  the memory on disk was written by exactly three completed runs (Exp 47,
  48, 49) and reproduces byte-for-byte from their reports.
* CONSUMPTION is off. ``immune_memory_consume_rk0`` is set by no config, so
  ``blended_prior`` has never seeded R_k(0) in any run.
* DRIFT DETECTION is UNREACHED. ``update_drift`` has no caller outside the
  test suite, so it has never fired because it has never run. Replayed over
  the three recorded runs it would not have fired either: peak CUSUM+ 0.560,
  trough CUSUM− −0.500, against a threshold of 2.0.
* HASH GROUNDING is UNUSED. Nothing calls ``compute_source_hash`` and no
  caller passes ``expected_hash``; the memory on disk carries
  ``source_hash: null``. The invalidation path below is therefore a
  capability, not an active guard — and until 2026-08-12 a null stored hash
  was silently treated as a match, so arming it would not have caught this
  file. See ``load``.
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


class MemoryIntegrityError(ValueError):
    """The memory was asked to accept something that would corrupt its counts.

    Deliberately a ``ValueError``. These are invalid-value conditions, and the
    Exp 45 panel's own falsifier for the ``decay_rate`` defect below is written
    as ``except (ValueError, TypeError): return`` — the shape a repair was
    expected to take. Raising outside that family would leave a correct fix
    looking like a broken falsifier.

    Raised rather than absorbed. Both production call sites (the recording and
    consumption blocks in ``reference_runner_v3``) already wrap this module in
    ``try/except`` that writes the failure into the run report AND logs it, so
    refusing leaves a trace on two channels and never kills a run — while
    accepting would leave a memory nobody can audit and no later reader could
    tell from a sound one.
    """


def _check_count(value: float, what: str) -> float:
    """A count must be a real, finite, non-negative number. Nothing else."""
    try:
        v = float(value)
    except (TypeError, ValueError) as exc:
        raise MemoryIntegrityError(f"{what}: not a number ({value!r})") from exc
    if not math.isfinite(v):
        raise MemoryIntegrityError(f"{what}: not finite ({v!r})")
    if v < 0.0:
        raise MemoryIntegrityError(f"{what}: negative ({v!r})")
    return v


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
        # DECAY MUST DECAY (Exp 45 finding C0031, CONFIRMED 2026-07-27, still
        # live when measured 2026-08-12). `record_experiment` multiplies every
        # existing count by `math.exp(-self.decay_rate)`. A negative decay_rate
        # makes that factor GREATER THAN 1, so the step named "decay" amplifies
        # the memory on every run — counts and π_mem climbing toward certainty
        # with no new evidence, and nothing in the pipeline able to tell. The
        # rate is read straight out of the persisted JSON by `load`, so the
        # memory file is a live route to it, not a theoretical one.
        self.decay_rate = _check_count(decay_rate, "decay_rate")
        self.drift_threshold = drift_threshold
        self.source_hash = source_hash  # hash of source files for invalidation
        self._records: Dict[int, FlawClassRecord] = {}
        self._drift: Dict[int, DriftState] = {}
        self._experiment_count: int = 0
        # Which experiments produced these counts. Persisted, so the file
        # carries its own provenance and a re-ingestion can be refused across
        # the load → record → save cycle the runner actually uses.
        self._experiment_ids: List[str] = []

    @property
    def experiment_ids(self) -> Tuple[str, ...]:
        """The experiments already folded into these counts, in ingest order."""
        return tuple(self._experiment_ids)

    @property
    def provenance_complete(self) -> bool:
        """True when every counted experiment is NAMED in this memory.

        THE DUPLICATE GUARD IS ONLY AS GOOD AS THIS (added 2026-08-12 by
        adversarial verification of the guard immediately above). The guard
        refuses an ``exp_id`` it has seen; a memory written before the ledger
        existed carries ``experiment_count`` but NO ``experiment_ids``, so it
        cannot recognise a single one of its own sources and re-ingesting any
        of them is accepted in silence — the exact defect the guard was added
        to close. Measured on the live file that day: ``experiment_count = 3``,
        ``experiment_ids = ()``; re-recording Exp 47 lifted flaw class 1's
        confirmed count from 56.90 to 92.49 with no error raised.

        A guard that is inert on the only file that exists, and says nothing
        about it, is a guard reporting success it has not achieved. This
        property makes the state answerable, and ``load`` announces it.
        Backfilling ``experiment_ids`` into a legacy file closes the gap.
        """
        return len(self._experiment_ids) == self._experiment_count

    def record_experiment(
        self,
        exp_id: str,
        flaw_counts: Dict[int, Tuple[int, int]],
        allow_reingest: bool = False,
    ) -> None:
        """Ingest results from a completed experiment.

        Args:
            exp_id: Experiment identifier. Recorded, not merely logged — it is
                the file's only provenance and the key the duplicate guard uses.
            flaw_counts: {flaw_class: (confirmed_count, rejected_count)}.
            allow_reingest: Deliberate override for a genuine repeat replicate
                that reuses an experiment name. Off by default.

        Raises:
            MemoryIntegrityError: on an unnamed experiment, a count that is not
                a finite non-negative number, or a re-ingestion of an ``exp_id``
                already folded in.

        THE DEFECT THIS GUARD CLOSES (found 2026-08-12). The runner records at
        run end whenever ``immune_memory_enabled`` is set, and the cycle is
        load → record → save against one shared file. A resumed run, or any
        re-run of the same config, therefore added its whole registry a SECOND
        time on top of the first, silently: no error, no report field, no
        difference a later reader could detect. The counts are this component's
        entire epistemic content, so a silent doubling is unrecoverable — the
        only reason the current file's provenance could be established at all
        was that the three source run reports happened to survive on disk.
        """
        if not exp_id or not str(exp_id).strip():
            raise MemoryIntegrityError(
                "record_experiment requires a non-empty exp_id: an unlabelled "
                "contribution cannot be audited or de-duplicated afterwards")
        exp_id = str(exp_id)
        if exp_id in self._experiment_ids and not allow_reingest:
            raise MemoryIntegrityError(
                f"experiment {exp_id!r} is already recorded in this memory "
                f"(ingested: {self._experiment_ids}). Re-ingesting would "
                f"double-count its findings and silently shift every prior "
                f"derived from them. Pass allow_reingest=True only if this is "
                f"a genuine repeat replicate that reuses the name.")

        validated: Dict[int, Tuple[float, float]] = {}
        for fc, pair in flaw_counts.items():
            try:
                confirmed, rejected = pair
            except (TypeError, ValueError) as exc:
                raise MemoryIntegrityError(
                    f"flaw class {fc}: expected (confirmed, rejected), got "
                    f"{pair!r}") from exc
            validated[int(fc)] = (
                _check_count(confirmed, f"flaw class {fc} confirmed"),
                _check_count(rejected, f"flaw class {fc} rejected"),
            )
        flaw_counts = validated  # type: ignore[assignment]

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
        self._experiment_ids.append(exp_id)
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
            # Provenance. Without this the file is a set of numbers with no
            # statement of where they came from — the state it was in until
            # 2026-08-12, when establishing it took a replay of three run
            # reports that could as easily have been deleted.
            "experiment_ids": list(self._experiment_ids),
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

        Raises:
            MemoryIntegrityError: if the file parses but carries a count that
                is not a finite non-negative number. Such a file yields a
                π_mem outside [0, 1] and so a blended prior outside [0, 1],
                breaking the bound this class documents; a missing file and a
                corrupt one are different situations and only the first is
                safe to treat as "start fresh".
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
        # UNGROUNDED is not GROUNDED-AND-MATCHING (fixed 2026-08-12). The
        # original condition required BOTH hashes to be truthy, so a file with
        # `source_hash: null` — which is what every memory written to date
        # carries, because nothing calls compute_source_hash — passed the
        # invalidation check silently. A caller that armed this guard would
        # have got a clean load and no warning on exactly the file the guard
        # exists to catch. Unknown provenance now invalidates.
        if expected_hash and stored_hash != expected_hash:
            logger.warning(
                "Source hash %s (stored: %s, current: %s). "
                "Memory invalidated — starting fresh.",
                "missing" if not stored_hash else "mismatch",
                (stored_hash or "<none>")[:12], expected_hash[:12],
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
        mem._experiment_ids = [str(x) for x in data.get("experiment_ids", [])]
        for fc_str, rec_dict in data.get("records", {}).items():
            rec = FlawClassRecord.from_dict(rec_dict)
            _check_count(rec.confirmed, f"{path}: flaw class {rec.flaw_class} confirmed")
            _check_count(rec.rejected, f"{path}: flaw class {rec.flaw_class} rejected")
            mem._records[rec.flaw_class] = rec

        logger.info(
            "Loaded immune memory from %s (%d experiments, %d flaw classes)",
            path, mem._experiment_count, len(mem._records),
        )
        if not mem.provenance_complete:
            # Loud, on the same channel the recording block already logs to.
            # Not fatal: refusing the load would disable recording outright for
            # every run against a legacy file, which is a larger harm than the
            # one being reported. See `provenance_complete`.
            logger.warning(
                "Immune memory at %s names %d of its %d experiments "
                "(experiment_ids=%s). The duplicate-ingestion guard CANNOT "
                "refuse a re-run of an unnamed one, so those counts can still "
                "be silently doubled. Backfill experiment_ids to close this.",
                path, len(mem._experiment_ids), mem._experiment_count,
                list(mem._experiment_ids),
            )
        return mem
