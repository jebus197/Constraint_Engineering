"""CDSFL Dynamic Management — Shadow Extensions (Observation-Only).

Shadow-mode implementations for two deferred AIS-inspired gaps:

    Gap 5 — Credit Assignment (ShadowCreditScorecard)
    Gap 4 — Anticipatory Dispatch (ShadowSteeringPredictor)

These components are strictly observation-only.  They log what WOULD happen
under the proposed mechanisms without mutating any live system state.  No
imports from the CDSFL codebase are used; the module is entirely self-contained.

Intended use: instantiate alongside the real dispatch/immune pipeline, feed
identical events, and compare shadow predictions against actual outcomes to
evaluate whether the full mechanisms warrant implementation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

__all__ = ["ShadowCreditScorecard", "ShadowSteeringPredictor"]

logger = logging.getLogger("cdsfl.shadow")


# ---------------------------------------------------------------------------
# Gap 5 — Credit Assignment
# ---------------------------------------------------------------------------


@dataclass
class ModelCredit:
    """Per-model empirical credit accumulator.

    Tracks findings submitted, confirmed, rejected, and uncertain counts.
    Derives two quality signals without touching CapabilityFingerprint.
    """

    model_id: str
    findings_submitted: int = 0
    confirmed: int = 0
    novel_confirmed: int = 0
    rejected: int = 0
    uncertain: int = 0

    @property
    def precision_estimate(self) -> float:
        """Beta-Binomial smoothed precision: (confirmed + 1) / (confirmed + rejected + 2).

        The +1/+2 Laplace smoothing prevents zero-division and avoids
        degenerate 0.0 or 1.0 estimates on small sample sizes.
        """
        return (self.confirmed + 1) / (self.confirmed + self.rejected + 2)

    @property
    def novelty_yield(self) -> float:
        """Novel confirmed findings as a fraction of total submitted.

        Only counts confirmed findings that were also classified as novel
        by the immune pipeline (is_novel=True in record_verdict).
        Returns 0.0 when no findings have been submitted (avoids ZeroDivisionError).
        """
        if self.findings_submitted == 0:
            return 0.0
        return self.novel_confirmed / self.findings_submitted


class ShadowCreditScorecard:
    """Shadow credit-assignment scorecard (Gap 5).

    Maintains a parallel empirical scorecard that tracks per-model performance
    without mutating ``CapabilityFingerprint`` or any live dispatch state.
    Logs what the composite dispatch weight WOULD be so the delta against the
    actual static weight can be assessed.

    Example::

        sc = ShadowCreditScorecard()
        sc.record_verdict("gemini-3.1-pro", "CONFIRMED", is_novel=True)
        sc.record_verdict("gemini-3.1-pro", "REJECTED", is_novel=False)
        w = sc.shadow_dispatch_weight("gemini-3.1-pro")
        print(sc.report())
    """

    def __init__(self) -> None:
        self._credits: Dict[str, ModelCredit] = {}

    # -- internal helpers ---------------------------------------------------

    def _ensure_model(self, model_id: str) -> ModelCredit:
        """Return existing ModelCredit or create a new one."""
        if model_id not in self._credits:
            self._credits[model_id] = ModelCredit(model_id=model_id)
        return self._credits[model_id]

    # -- public API ---------------------------------------------------------

    def record_verdict(
        self,
        model_id: str,
        verdict_type: str,
        is_novel: bool = False,
    ) -> None:
        """Record an immune-pipeline verdict for *model_id*.

        Args:
            model_id: Identifier of the model that produced the finding.
            verdict_type: One of CONFIRMED, REJECTED, UNCERTAIN, DUPLICATE,
                NOVEL.  Only CONFIRMED, REJECTED, and UNCERTAIN update the
                credit counters; DUPLICATE and NOVEL are informational.
            is_novel: Whether the finding was classified as novel by the
                immune pipeline.  When True AND verdict_type is CONFIRMED,
                the finding counts toward both ``confirmed`` and
                ``findings_submitted``; otherwise only ``findings_submitted``
                is incremented.
        """
        credit = self._ensure_model(model_id)
        credit.findings_submitted += 1

        vt = verdict_type.upper()
        if vt == "CONFIRMED":
            credit.confirmed += 1
            if is_novel:
                credit.novel_confirmed += 1
        elif vt == "REJECTED":
            credit.rejected += 1
        elif vt == "UNCERTAIN":
            credit.uncertain += 1
        # DUPLICATE and NOVEL are counted in findings_submitted only.

        logger.debug(
            "shadow-credit | model=%s verdict=%s novel=%s "
            "precision=%.3f novelty_yield=%.3f",
            model_id,
            vt,
            is_novel,
            credit.precision_estimate,
            credit.novelty_yield,
        )

    def shadow_dispatch_weight(self, model_id: str) -> float:
        """Compute the composite dispatch weight for *model_id*.

        weight = 0.5 * precision_estimate + 0.5 * novelty_yield

        This is what the dispatch weight WOULD be under credit-aware routing.
        The caller is responsible for comparing against the actual static
        weight and logging the delta.

        Returns 0.5 (the prior mean) for unknown models.
        """
        if model_id not in self._credits:
            logger.info(
                "shadow-credit | model=%s has no recorded verdicts; "
                "returning prior weight 0.500",
                model_id,
            )
            return 0.5

        credit = self._credits[model_id]
        weight = 0.5 * credit.precision_estimate + 0.5 * credit.novelty_yield

        logger.info(
            "shadow-credit | model=%s shadow_weight=%.3f "
            "(precision=%.3f, novelty_yield=%.3f)",
            model_id,
            weight,
            credit.precision_estimate,
            credit.novelty_yield,
        )
        return weight

    def report(self) -> Dict[str, Dict[str, object]]:
        """Return a dict of all model credits keyed by model_id.

        Each value contains the raw counters plus derived metrics::

            {
                "gemini-3.1-pro": {
                    "findings_submitted": 12,
                    "confirmed": 8,
                    "novel_confirmed": 5,
                    "rejected": 2,
                    "uncertain": 2,
                    "precision_estimate": 0.75,
                    "novelty_yield": 0.417,
                    "shadow_weight": 0.583,
                },
                ...
            }
        """
        out: Dict[str, Dict[str, object]] = {}
        for mid, credit in self._credits.items():
            out[mid] = {
                "findings_submitted": credit.findings_submitted,
                "confirmed": credit.confirmed,
                "novel_confirmed": credit.novel_confirmed,
                "rejected": credit.rejected,
                "uncertain": credit.uncertain,
                "precision_estimate": round(credit.precision_estimate, 4),
                "novelty_yield": round(credit.novelty_yield, 4),
                "shadow_weight": round(
                    0.5 * credit.precision_estimate + 0.5 * credit.novelty_yield,
                    4,
                ),
            }
        logger.info("shadow-credit | report requested, %d models tracked", len(out))
        return out


# ---------------------------------------------------------------------------
# Gap 4 — Anticipatory Dispatch
# ---------------------------------------------------------------------------


@dataclass
class SteeringPrediction:
    """A single anticipatory steering prediction for one model-round pair.

    Fields populated at prediction time:
        model_id, round_idx, suggested_focus_areas, predicted_novelty

    Fields populated after the round completes:
        actual_novelty, actual_flaw_classes
    """

    model_id: str
    round_idx: int
    suggested_focus_areas: List[str]
    predicted_novelty: float
    actual_novelty: Optional[float] = None
    actual_flaw_classes: Optional[Set[str]] = None


class ShadowSteeringPredictor:
    """Shadow anticipatory-dispatch predictor (Gap 4).

    Logs what steering notes WOULD have been generated for each model
    without injecting anything into actual prompts.  After each round the
    prediction is compared against actual outcomes so prediction accuracy
    can be assessed over time.

    Heuristic: suggest flaw classes that this model has NOT found but at
    least one other model HAS found.  Predicted novelty is the fraction of
    such classes relative to total known classes.

    Example::

        sp = ShadowSteeringPredictor()
        sp.record_model_round("gemini", 0, 0.8, {"null-deref", "overflow"})
        sp.record_model_round("claude", 0, 0.6, {"race-condition"})
        pred = sp.predict_focus("gemini", {"null-deref", "overflow", "race-condition"}, 1)
        sp.evaluate_prediction(pred, actual_novelty=0.5, actual_flaw_classes={"race-condition"})
        print(sp.report())
    """

    def __init__(self) -> None:
        # model_id -> round_idx -> novelty_rate
        self._novelty_history: Dict[str, Dict[int, float]] = {}
        # model_id -> set of flaw classes found across all rounds
        self._model_flaw_classes: Dict[str, Set[str]] = {}
        # All predictions issued, for accuracy tracking
        self._predictions: List[SteeringPrediction] = []
        # Running accuracy counters
        self._total_evaluated: int = 0
        self._focus_hits: int = 0  # predictions where >= 1 suggested area was found

    # -- public API ---------------------------------------------------------

    def record_model_round(
        self,
        model_id: str,
        round_idx: int,
        novelty_rate: float,
        flaw_classes_found: Set[str],
    ) -> None:
        """Record one model's results for a completed round.

        Args:
            model_id: The model identifier.
            round_idx: Zero-based round index.
            novelty_rate: Fraction of novel (non-duplicate) findings this round.
            flaw_classes_found: Set of flaw-class labels found this round.
        """
        self._novelty_history.setdefault(model_id, {})[round_idx] = novelty_rate
        self._model_flaw_classes.setdefault(model_id, set()).update(flaw_classes_found)

        logger.debug(
            "shadow-steering | recorded model=%s round=%d "
            "novelty=%.3f flaw_classes=%s",
            model_id,
            round_idx,
            novelty_rate,
            flaw_classes_found,
        )

    def predict_focus(
        self,
        model_id: str,
        all_flaw_classes: Set[str],
        round_idx: int,
    ) -> SteeringPrediction:
        """Predict which flaw areas *model_id* should focus on next.

        Heuristic: flaw classes present in *all_flaw_classes* (the global
        set found by any model) but NOT yet found by *model_id*.

        Predicted novelty: |suggested| / |all_flaw_classes| — the fraction
        of the global flaw space this model has not yet covered.  Bounded
        to [0.0, 1.0]; returns 0.0 when all_flaw_classes is empty.

        Args:
            model_id: The model to generate a prediction for.
            all_flaw_classes: Union of all flaw classes found by all models
                across all rounds so far.
            round_idx: The upcoming round index.

        Returns:
            A ``SteeringPrediction`` with suggested focus areas and predicted
            novelty.  ``actual_novelty`` and ``actual_flaw_classes`` are None
            until ``evaluate_prediction`` is called.
        """
        model_classes = self._model_flaw_classes.get(model_id, set())
        gaps = sorted(all_flaw_classes - model_classes)

        if len(all_flaw_classes) > 0:
            predicted_novelty = len(gaps) / len(all_flaw_classes)
        else:
            predicted_novelty = 0.0

        prediction = SteeringPrediction(
            model_id=model_id,
            round_idx=round_idx,
            suggested_focus_areas=gaps,
            predicted_novelty=predicted_novelty,
        )
        self._predictions.append(prediction)

        logger.info(
            "shadow-steering | PREDICT model=%s round=%d "
            "focus=%s predicted_novelty=%.3f",
            model_id,
            round_idx,
            gaps,
            predicted_novelty,
        )
        return prediction

    def evaluate_prediction(
        self,
        prediction: SteeringPrediction,
        actual_novelty: float,
        actual_flaw_classes: Set[str],
    ) -> None:
        """Compare a prior prediction against actual round outcomes.

        Updates the prediction object in place and logs accuracy.

        Args:
            prediction: A ``SteeringPrediction`` returned by ``predict_focus``.
            actual_novelty: The observed novelty rate for this model-round.
            actual_flaw_classes: The flaw classes actually found by this model
                in the predicted round.
        """
        prediction.actual_novelty = actual_novelty
        prediction.actual_flaw_classes = actual_flaw_classes

        self._total_evaluated += 1

        # A "hit" means the model found at least one of the suggested areas.
        suggested = set(prediction.suggested_focus_areas)
        hit = len(suggested & actual_flaw_classes) > 0 if suggested else False
        if hit:
            self._focus_hits += 1

        novelty_error = abs(prediction.predicted_novelty - actual_novelty)

        logger.info(
            "shadow-steering | EVALUATE model=%s round=%d "
            "predicted_novelty=%.3f actual_novelty=%.3f error=%.3f "
            "focus_hit=%s (suggested=%s, actual=%s)",
            prediction.model_id,
            prediction.round_idx,
            prediction.predicted_novelty,
            actual_novelty,
            novelty_error,
            hit,
            sorted(suggested),
            sorted(actual_flaw_classes),
        )

    def report(self) -> Dict[str, object]:
        """Return a summary of all predictions and their accuracy.

        Returns a dict with:
            - ``total_predictions``: number of predictions issued
            - ``total_evaluated``: number compared against actuals
            - ``focus_hit_rate``: fraction of evaluated predictions where the
              model found at least one suggested area (0.0 if none evaluated)
            - ``mean_novelty_error``: mean absolute error between predicted
              and actual novelty across evaluated predictions (None if none)
            - ``per_model``: per-model breakdown of novelty history and
              cumulative flaw classes
            - ``predictions``: list of all prediction records
        """
        # Compute mean novelty error across evaluated predictions.
        evaluated = [p for p in self._predictions if p.actual_novelty is not None]
        if evaluated:
            mean_error = sum(
                abs(p.predicted_novelty - p.actual_novelty)  # type: ignore[operator]
                for p in evaluated
            ) / len(evaluated)
        else:
            mean_error = None

        hit_rate = (
            self._focus_hits / self._total_evaluated
            if self._total_evaluated > 0
            else 0.0
        )

        per_model: Dict[str, Dict[str, object]] = {}
        all_models = set(self._novelty_history.keys()) | set(
            self._model_flaw_classes.keys()
        )
        for mid in sorted(all_models):
            per_model[mid] = {
                "novelty_history": dict(
                    sorted(self._novelty_history.get(mid, {}).items())
                ),
                "flaw_classes_found": sorted(
                    self._model_flaw_classes.get(mid, set())
                ),
            }

        prediction_records = []
        for p in self._predictions:
            prediction_records.append(
                {
                    "model_id": p.model_id,
                    "round_idx": p.round_idx,
                    "suggested_focus_areas": p.suggested_focus_areas,
                    "predicted_novelty": round(p.predicted_novelty, 4),
                    "actual_novelty": (
                        round(p.actual_novelty, 4)
                        if p.actual_novelty is not None
                        else None
                    ),
                    "actual_flaw_classes": (
                        sorted(p.actual_flaw_classes)
                        if p.actual_flaw_classes is not None
                        else None
                    ),
                }
            )

        out: Dict[str, object] = {
            "total_predictions": len(self._predictions),
            "total_evaluated": self._total_evaluated,
            "focus_hit_rate": round(hit_rate, 4),
            "mean_novelty_error": (
                round(mean_error, 4) if mean_error is not None else None
            ),
            "per_model": per_model,
            "predictions": prediction_records,
        }

        logger.info(
            "shadow-steering | report requested: %d predictions, "
            "%d evaluated, hit_rate=%.3f",
            len(self._predictions),
            self._total_evaluated,
            hit_rate,
        )
        return out
