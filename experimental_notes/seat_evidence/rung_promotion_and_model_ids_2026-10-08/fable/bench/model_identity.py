# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 5c76361af88c11830b7bbc7bdb86505802fa95c46088e5e00a192f97403e7437
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Capability records keyed by a configuration digest, not a random identifier.

THE FOUNDER'S WORDS (2026-10-08): *"the only way to tell them apart is through a
randomly assigned model ID"*. The need is real -- `model_id` in
bench/experiment_11_orchestrator.py has 12 occurrences with only 10 distinct
values (`opus` and `gpt-5.5` each appear twice), so the project has no stable
unique key for a capability record today. But RANDOM assignment is the wrong
derivation, and the defect is measurable: 2 instances of a genuinely identical
configuration would receive 2 different random identifiers, their attempt
records would never pool, and each would pay the full cold-start price
separately -- the measured price is 21 attempts at a 0.40 capability gap and
350 at 0.10 (bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py),
so splitting doubles wall-clock rounds to separation for no benefit.

THE RULE. Two levels, because they answer different questions:

  capability_key  = SHA-256 digest of the canonical JSON of every field that
                    changes the model's OUTPUT DISTRIBUTION. Same distribution
                    -> same key -> records pool (exchangeable, statistically
                    valid). Any distribution-changing difference -> new key at
                    0 attempts. A vendor release changes `model_version`, so it
                    gets a new key AUTOMATICALLY -- which is the founder's own
                    bidirectional rule ("No new model is inherently trusted")
                    enforced by construction rather than by policy.
  instance_id     = random token for DISPATCH bookkeeping only (which process,
                    which slot). Never keys a capability record.

The digest carries no vendor prior: it orders nothing and smuggles nothing --
it is opaque to sorting, exactly as the founder wants, while still merging what
is identical and splitting what is not.
"""
from __future__ import annotations

import hashlib
import json
import secrets

#: Every field that changes what the model emits. Extend ONLY with fields that
#: change the output distribution; cosmetic fields (display name, owner,
#: billing tag) must stay out or identical configs will wrongly split.
DISTRIBUTION_FIELDS = (
    "provider",        # e.g. "openrouter", "claude_cli" -- the harness differs
    "model_version",   # FULL vendor string, e.g. "openai/gpt-5.5-2026-08-01"
    "temperature",
    "top_p",
    "max_tokens",
    "system_prompt",   # hashed into the digest via its text
    "tool_set",        # sorted tool names
    "quantisation",    # e.g. "fp8", None for vendor-hosted
)


def capability_key(config: dict) -> str:
    """Deterministic digest over distribution-affecting fields only."""
    canon = {}
    for f in DISTRIBUTION_FIELDS:
        v = config.get(f)
        if f == "tool_set" and v is not None:
            v = sorted(v)
        canon[f] = v
    blob = json.dumps(canon, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def instance_id() -> str:
    """Random token for dispatch bookkeeping. NEVER keys a capability record."""
    return secrets.token_hex(8)
