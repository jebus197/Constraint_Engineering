"""Route a finding back to its author when its severity carries no worked proof.

FOUNDER RULING, 2026-09-06: "If a model can demonstrably be shown to be using the
mathematical model (and tools) to calculate severity, then is that really a vote?
The difference is in requiring the models to provide worked proofs in all cases."

The round prompt already tells every model that findings missing a section will be
rejected, and the runner already re-derives R_k from the model's stated parameters
to check it. Nothing acted on the result, so the promise in the prompt was empty.
This builds the section that makes it true: the model is told which of its own
findings failed to reproduce, with its own two numbers, and asked to supply the
working or withdraw the claim.

Deliberately NOT a rejection of the finding. A defect reported without a proof may
still be a real defect; what it may not do is carry an unrecomputable severity that
moves a gate. So the finding stays, keeps blocking at its claimed severity, and the
model is asked for the arithmetic that would let it be demoted, cleared or closed.
"""
from __future__ import annotations

from typing import Optional, Sequence, Tuple

# (canonical_id, status, model_rk, recomputed_rk)
ProofRequest = Tuple[str, str, Optional[float], Optional[float]]

_EXPLAIN = {
    "FAIL": ("your stated parameters do not reproduce your stated R_k"),
    "SKIP": ("no recomputable CORROBORATION block was found -- the parameters "
             "were absent, or the working stated a formula but never its result"),
    "ABSENT": ("no CORROBORATION block was recorded for this finding at all"),
}


def build_proof_requests(
    requests: Sequence[ProofRequest],
    max_entries: int = 10,
    max_chars: int = 2200,
) -> str:
    """Build the next round's severity-proof request section.

    Returns the empty string when nothing needs a proof, so the caller can inject
    it unconditionally.
    """
    if not requests:
        return ""

    lines = [
        "SEVERITY PROOF REQUIRED — these findings cannot be acted on as scored",
        "",
        "A severity that cannot be recomputed from its own stated inputs is an",
        "assertion, not a measurement, and this system does not decide anything by",
        "assertion. Each finding below is RETAINED and still counts at the severity",
        "you gave it. What it cannot do, until the arithmetic reproduces, is be",
        "demoted, cleared or closed.",
        "",
        "Re-emit a CORROBORATION block for each, stating every value you used:",
        "  R_old, eta, d, p, q = eta*d*p, R_det, S_k, nu_b, nu_f, nu_eff, R_k",
        "Write each parameter and its RESULT on one line, or put the result on a",
        "continuation line beginning with '='. State the number you arrive at; a",
        "formula with no evaluated result reads as no answer. If you cannot produce",
        "the arithmetic, withdraw the finding instead — a withdrawal is a legitimate",
        "outcome and costs you nothing.",
        "",
    ]
    shown = 0
    for cid, status, model_rk, recomputed in requests:
        if shown >= max_entries:
            break
        why = _EXPLAIN.get((status or "").strip().upper(), _EXPLAIN["ABSENT"])
        if model_rk is not None and recomputed is not None:
            detail = (f"you stated R_k = {model_rk:.4f}; your own stated inputs "
                      f"give {recomputed:.4f} (difference {abs(model_rk - recomputed):.4f})")
        else:
            detail = why
        lines.append(f"  {cid}: {detail}")
        shown += 1
    remaining = len(requests) - shown
    if remaining > 0:
        lines.append(f"  ... and {remaining} further finding(s) awaiting a severity proof.")

    out = "\n".join(lines)
    if len(out) > max_chars:
        out = out[:max_chars].rsplit("\n", 1)[0] + "\n  ... (truncated)"
    return out
