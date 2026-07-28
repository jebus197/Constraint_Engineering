#!/usr/bin/env python3
"""
Confer: Crypto Signing Separation-of-Concerns Review
=====================================================
Dispatches to Gemini 3.1 Pro under full CDSFL + FFAFP protocol.

Evaluates the architectural claim that cryptographic signing + Merkle root +
blockchain anchoring of ouroboros cell (O1) outputs serves provenance and
immutability (NOT correctness/truthfulness), while correctness is the domain
of the falsification framework (R_k(i), P-pass) and the HIL.

Date: 12 April 2026
Protocol: CDSFL + FFAFP (Find, Follow, Analyse, Fix, P-pass)
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Repo setup
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "bench"))

from experiment_11_orchestrator import call_gemini

# Load .env
_env_file = REPO_ROOT / ".env"
if _env_file.exists():
    for _line in _env_file.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#"):
            continue
        if _line.startswith("export "):
            _line = _line[7:]
        if "=" in _line:
            _k, _, _v = _line.partition("=")
            _k = _k.strip()
            _v = _v.strip().strip("'\"")
            os.environ.setdefault(_k, _v)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

LOGS_DIR = REPO_ROOT / "bench" / "logs" / "confer_crypto_signing"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

GEMINI_MODEL = "gemini-3.1-pro-preview"

# ---------------------------------------------------------------------------
# Load CDSFL directives as system prompt
# ---------------------------------------------------------------------------

CDSFL_PATH = REPO_ROOT / "bench" / "directives" / "universal" / "cdsfl_core_formal.md"
CDSFL_TEXT = CDSFL_PATH.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Confer prompt
# ---------------------------------------------------------------------------

CONFER_PROMPT = """## Task

Under CDSFL and FFAFP (Find, Follow, Analyse, Fix, P-pass), evaluate the
following architectural claim about the ouroboros cell (O1) in the CDSFL
immune-inspired multi-model falsification framework.

Apply the full CDSFL + FFAFP protocol to your analysis. This means:
- Classify all constraints as HARD or SOFT before analysis.
- Apply the falsification loop (P-pass) to every non-trivial claim.
- Trace dependency chains to system boundaries.
- Flag [VERIFY:current] and [SPECULATIVE] where required.
- End with a definitive stance.

## Background

The CDSFL framework uses an immune-inspired multi-model architecture for
structured falsification of technical claims. A new cell type, the "ouroboros
cell" (O1), acts as an external research and self-improvement cell. It was
previously conceptualised as a "macrophage" in active mode and "microglia" in
self-referential mode.

All O1 research outputs, operations, and synthesised results are:
1. Cryptographically signed (per-operation signatures)
2. Rolled up into a Merkle root (batch integrity)
3. Anchored on a blockchain (immutable timestamped record)

## The Objection

In a previous confer round, you (Gemini) raised the objection that
cryptographic signing does not guarantee correctness or truthfulness of the
content being signed.

## The Architectural Claim (evaluate this)

The founder's response to the objection:

The entire PURPOSE of the immutable cryptographic record is NOT to guarantee
correctness or truthfulness. It exists to create an auditable evidence trail
so that the Human-in-the-Loop (HIL) can be the final arbiter of those
factors. The blockchain anchoring proves:

- WHAT was claimed (content integrity via signing)
- WHEN it was claimed (blockchain timestamp)
- BY WHOM it was claimed (signing identity)

It does NOT claim to prove the content is correct. That is the domain of:

- The falsification framework: R_k(i) recursive Bayesian self-assessment,
  P-pass cycles, convergence detection
- The Human-in-the-Loop (HIL): final arbiter of correctness and truth

Therefore, the original objection conflates the purpose of the signing
(provenance and immutability) with the purpose of the falsification framework
(correctness and truth). These are COMPLEMENTARY layers with DISTINCT
responsibilities:

  Layer 1 — Cryptographic signing + Merkle root + blockchain:
    Responsibility: provenance, integrity, immutability, auditability
    Does NOT claim: correctness, truthfulness, quality

  Layer 2 — Falsification framework (R_k(i), P-pass, FFAFP):
    Responsibility: correctness assessment, quality evaluation, convergence
    Does NOT claim: immutability, provenance

  Layer 3 — HIL (Human-in-the-Loop):
    Responsibility: final arbiter, approval authority, truth determination
    Authority: can override both Layer 1 and Layer 2

## Additional Mitigation: Shadow Mode

In this design, O1 will run purely in shadow mode for at least the first
stages of Experiment 39. This means:

- O1 observes and logs but does NOT affect the immune pipeline's actual
  decisions
- O1's research outputs are recorded (and signed/anchored) but not injected
  into the falsification pipeline
- O1 cannot corrupt the pipeline while in shadow mode, even if its research
  is entirely wrong
- Exit from shadow mode requires explicit HIL approval
- Shadow mode metrics (precision, novelty yield, false positive rate) must
  meet defined thresholds before promotion is even considered

## Questions for FFAFP Review

Apply the full five-step FFAFP cycle:

1. **FIND:** Is the separation of concerns (signing for provenance,
   falsification for correctness, HIL for truth) architecturally sound?
   Does it have gaps? Was the original objection valid, partially valid,
   or misplaced?

2. **FOLLOW:** Trace the consequences. If signing provides provenance but
   not correctness, and falsification provides correctness assessment but not
   immutability, are there failure modes in the composition? Can the two
   layers interact in ways that create false confidence? What happens at the
   boundary between Layer 1 and Layer 2?

3. **ANALYSE:** Under what conditions could the three-layer architecture
   FAIL to achieve its stated goals? Consider:
   - Signing key compromise
   - Blockchain reorg or anchoring service failure
   - HIL cognitive overload (too much auditable data to actually audit)
   - R_k(i) convergence on incorrect conclusions that are then immutably
     recorded
   - Shadow mode exit criteria gaming

4. **FIX:** Propose any architectural corrections, additional safeguards,
   or constraints needed to make the separation robust.

5. **P-PASS:** Falsify the integrated three-layer architecture. Under what
   conditions does the complementary design FAIL to be complementary? Is
   there a scenario where the layers interfere rather than complement?

## Additional Questions

A. **Scope of original objection:** Given this separation of concerns,
   was the original objection (signing doesn't guarantee correctness)
   actually identifying a real gap, or was it applying the wrong evaluation
   criterion to the signing layer?

B. **Shadow mode sufficiency:** Is shadow mode observation-only operation
   a sufficient safeguard during initial O1 deployment? What additional
   constraints would you impose on the shadow-to-live transition?

C. **Audit scalability:** The signing creates an auditable trail, but
   auditability is only valuable if the HIL can actually audit. At what
   volume of O1 operations does the audit trail become effectively
   unauditable? What summarisation or filtering mechanisms would preserve
   auditability at scale?

Respond with rigorous FFAFP analysis. Be concrete and specific. If the
architectural claim is flawed, say so and explain why. If it is sound,
state the conditions under which it remains sound and the boundaries
beyond which it breaks.
"""

# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def run_confer():
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print(f"\n{'='*72}")
    print(f"  CONFER: Crypto Signing Separation-of-Concerns Review")
    print(f"  Timestamp: {ts}")
    print(f"  Protocol: CDSFL + FFAFP")
    print(f"  Model: Gemini 3.1 Pro")
    print(f"{'='*72}\n")

    # --- Gemini ---
    print("Dispatching to Gemini 3.1 Pro...")
    t0 = time.monotonic()
    try:
        ge_response = call_gemini(
            model_id=GEMINI_MODEL,
            system_prompt=CDSFL_TEXT,
            user_prompt=CONFER_PROMPT,
            max_tokens=32768,
            timeout=300,
            max_retries=5,
            backoff_base=3.0,
        )
        ge_time = time.monotonic() - t0
        print(f"  Gemini responded in {ge_time:.1f}s ({len(ge_response)} chars)")

        result = {
            "model": GEMINI_MODEL,
            "timestamp": ts,
            "protocol": "CDSFL + FFAFP",
            "topic": "crypto_signing_separation_of_concerns",
            "response": ge_response,
            "time_s": round(ge_time, 1),
            "chars": len(ge_response),
        }

    except Exception as e:
        ge_time = time.monotonic() - t0
        print(f"  Gemini FAILED after {ge_time:.1f}s: {e}")
        result = {
            "model": GEMINI_MODEL,
            "timestamp": ts,
            "protocol": "CDSFL + FFAFP",
            "topic": "crypto_signing_separation_of_concerns",
            "error": str(e),
            "time_s": round(ge_time, 1),
        }

    # --- Save results ---
    out_path = LOGS_DIR / f"crypto_signing_{ts}.json"
    out_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nResults saved to: {out_path}")

    # Print response
    if "error" in result:
        print(f"\n{'='*72}")
        print(f"  GEMINI: ERROR -- {result['error']}")
        print(f"{'='*72}")
    else:
        print(f"\n{'='*72}")
        print(f"  GEMINI ({result['model']}) -- {result['time_s']}s")
        print(f"{'='*72}\n")
        print(result["response"])

    return result


if __name__ == "__main__":
    run_confer()
