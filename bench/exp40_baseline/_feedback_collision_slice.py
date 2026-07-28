"""Exp 40 plan-D decomposition slice — the finding-ID collision detector.

A standalone, self-contained extraction of `detect_finding_id_collisions`
(plus its module-level accumulator) from the plan-E cleaned `_feedback.py`
baseline. This is the second small, finite, monitorable review target
for the hardened-gate convergence campaign: ~45 lines, one pure
`List[Finding] -> List[dict]` observation-only function, zero coupling
to the feedback dataclass or the rest of the channel (AST refs: []).
A small finite error space can actually be exhausted, which is the
regime the decay model needs to terminate.

Provenance: verbatim from bench/exp40_baseline/_feedback_cleaned.py
(lines 30-104: the import block, the `cdsfl.feedback` logger, the
collision-detector section comment, the `_finding_id_collisions`
accumulator, and `detect_finding_id_collisions`), itself the cumulative
test-gated baseline built by bench/exp40_fix_collation.py. The repo
bench/dm/_feedback.py is left pristine; this slice is the experiment
artefact only. The detector is observation-only by design — it records
the silent-overwrite condition without repairing it; that deferral is
itself the Exp 41 UUID-namespace evidence gate.
"""
from __future__ import annotations

import logging
from collections import Counter
from typing import Any, Dict, List

_LOG = logging.getLogger("cdsfl.feedback")

# ─────────────────────────────────────────────────────────────────────────────
# Finding-ID collision detector (Exp 40 timing re-confer, 2026-05-16)
# ─────────────────────────────────────────────────────────────────────────────
#
# The 2026-05-16 neutral confer converged that the UUID-namespace
# architectural change is real but unobserved, and deferred it to
# pre-Exp-41 ON CONDITION that R17-R21 is instrumented to convert the
# theoretical collision-overwrite risk into an observable. This
# detector is that instrument: it is OBSERVATION-ONLY. It does NOT
# alter the `{f.finding_id: f for f in findings}` comprehension or any
# dedup/merge behaviour — changing reconciliation behaviour pre-resume
# is precisely the risky work being deferred. It only detects and
# records when two findings in the same round share a finding_id (the
# silent-overwrite condition the panel diagnosed) so the Exp 40-54
# canonical plan's Q2/UUID deferral is evidence-gated, not blind.
#
# Module-level accumulator mirrors the established `_itc_hil_flags`
# pattern so post-mortem tooling can quantify collisions across a run.
# The runner clears it at experiment start.
_finding_id_collisions: List[Dict[str, Any]] = []


def detect_finding_id_collisions(
    findings: List[Any], round_idx: int = -1,
) -> List[Dict[str, Any]]:
    """Detect (do not repair) duplicate finding_id within one round.

    Returns a list of collision records; each record is
    ``{"round", "finding_id", "count", "model_ids"}``. A non-empty
    return means the `{f.finding_id: f for f in findings}` map would
    silently drop ``count - 1`` finding(s) for that id. model_ids
    distinguishes the cross-model case (two different models, the
    case UUID-namespace specifically targets) from the same-model
    case (one model emitting a duplicate id), which informs the
    Exp 41 UUID-namespace go/no-go.

    Observation-only: callers must NOT change behaviour based on this;
    it exists to gather the evidence the deferred UUID decision needs.
    """
    ids = [getattr(f, "finding_id", None) for f in findings]
    counts = Counter(i for i in ids if i is not None)
    collisions: List[Dict[str, Any]] = []
    for fid, n in counts.items():
        if n > 1:
            model_ids = sorted({
                getattr(f, "model_id", "?")
                for f in findings
                if getattr(f, "finding_id", None) == fid
            })
            rec = {
                "round": round_idx,
                "finding_id": fid,
                "count": n,
                "model_ids": model_ids,
                "cross_model": len(model_ids) > 1,
            }
            collisions.append(rec)
            _finding_id_collisions.append(rec)
            _LOG.warning(
                "FINDING_ID_COLLISION round=%s id=%r count=%d "
                "model_ids=%s cross_model=%s — silent-overwrite "
                "condition (UUID-namespace evidence gate, Q2 confer "
                "2026-05-16)",
                round_idx, fid, n, model_ids, len(model_ids) > 1,
            )
    return collisions
