# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'rung_promotion_and_model_ids_2026-10-08', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: e64c1168edd938771d50493d78f54831b624fcaa07def5e24b98c963b1e1f803
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Opaque model identifiers derived from the dispatch-determining configuration.

OPEN QUESTION 4. "5 models from one vendor, or 5 instances of the same model:
what must the identifier be derived from so that 2 genuinely identical
configurations are not merged and 1 configuration is not split?"

A random identifier cannot answer it. A random identifier assigned per roster
ENTRY splits one configuration listed twice, and assigned per vendor NAME merges
two different configurations of the same model. The identifier must therefore be
a function of the configuration - a content address - and of nothing else:

    model_uid = H(canonical(dispatch_determining_fields))

`dispatch_determining_fields` is every field that changes the output
distribution: the provider endpoint, the model slug (which carries the vendor
version), and the sampling and system parameters. Fields that do not change the
output distribution - a display name, a cost note, a comment - are excluded, or
an edited comment would split a configuration.

OPEN QUESTION 2, answered as a consequence rather than as a separate policy. The
model slug carries the vendor version, so a new release yields a DIFFERENT
content address and therefore a new identifier at 0 attempts. That is not a
choice; it falls out of the key. WHAT IS LOST is the prior record, and the cost
is the derived climb in `bench/promotion_gate.py`: 19 attempts per rung times 5
rungs = 95 attempts before the new identifier can hold the top rung at
beta=0.05. Inheriting the record instead would assert that the new release is at
least as capable as the old one, which is the judgement the founder's rule that
*"the only thing that should impact on capability is measured capability"*
forbids. The prior record is not discarded: it stays attached to the old
identifier, which is what makes a regression visible as two records rather than
one moving average.

WHY THIS IS NOT A HAND-WRITTEN LIST. The identifiers are computed from the
config files that already exist, so a roster of 700 needs no maintained tuple -
which is the defect `bench/the_cold_start_cannot_use_a_tuple_at_scale_2026-10-08.py`
measures at 0.8571% coverage for 700 seats.

WHAT THIS FIXES TODAY. `bench/experiment_11_orchestrator.py` assigns `model_id`
12 times with 10 distinct values ("opus" and "gpt-5.5" each twice), so the field
collides and cannot key a capability record; 9 of the 12 embed a vendor version
inside a field also used as a stable handle. Verified by the falsifier in
`bench/test_model_identity.py`, which parses that file rather than restating it.
"""
from __future__ import annotations

import hashlib
import json

#: The fields that change what a dispatch returns. Anything outside this set is
#: presentation and MUST NOT enter the identifier, or an edited label splits a
#: configuration that has not changed.
DISPATCH_DETERMINING = (
    "provider",        # which endpoint is called
    "model",           # vendor slug, carrying the vendor version
    "temperature",
    "top_p",
    "max_tokens",
    "system_prompt",
    "tools",           # tool availability changes what the model can do
    "reasoning_effort",
)


def canonical(config: dict) -> str:
    """Canonical JSON over the dispatch-determining fields only.

    Sorted keys, so dict insertion order cannot split one configuration.
    Integral floats are normalised to int, so 1 and 1.0 cannot split one
    configuration. Missing fields are omitted rather than defaulted, so adding a
    field with its default value to a config file does not change its identity.
    """
    def norm(v):
        if isinstance(v, bool):
            return v
        if isinstance(v, float) and v.is_integer():
            return int(v)
        if isinstance(v, (list, tuple)):
            return [norm(x) for x in v]
        if isinstance(v, dict):
            return {k: norm(v[k]) for k in sorted(v)}
        return v
    picked = {k: norm(config[k]) for k in sorted(DISPATCH_DETERMINING)
              if k in config and config[k] is not None}
    return json.dumps(picked, sort_keys=True, separators=(",", ":"))


def model_uid(config: dict, length: int = 16) -> str:
    """Opaque, stable, collision-resistant identifier for one configuration.

    Opaque: carries no vendor name, so it cannot smuggle in a prior.
    Stable: a function of the configuration, so the same configuration in two
    roster files gets ONE record.
    Distinct: any change to a dispatch-determining field gives a new identifier.
    """
    if length < 8 or length > 64:
        raise ValueError("length must be in [8, 64] hex chars")
    return "m-" + hashlib.blake2b(
        canonical(config).encode("utf-8"), digest_size=32
    ).hexdigest()[:length]


def assign_uids(roster: list) -> dict:
    """uid -> the list of roster indices that share it.

    A uid with more than one index is two identical configurations listed twice,
    which is ONE model and must hold ONE capability record. The caller needs
    this mapping rather than a flat list precisely so that case is visible
    instead of silently producing two records.
    """
    out = {}
    for i, cfg in enumerate(roster):
        out.setdefault(model_uid(cfg), []).append(i)
    return out
