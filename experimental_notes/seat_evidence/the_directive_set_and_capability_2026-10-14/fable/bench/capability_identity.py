# PRESERVED SEAT EVIDENCE. Written by seat 'fable' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 86fb52fef3c63d4c00668230cbd6bf02c01851e7411e9445d1587b385aa6a0b5
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Stable model identity and measured-capability ordering for the routing ladder.

HIS RULING (2026-10-14, 4 times restated): *"the only thing that should impact
on capability is measured capability. A model's name should have little to do
with it, beyond recording this."* This module supplies the 3 pieces the frozen
`bench/routing.DEFAULT_FALSIFIER_STRENGTH` tuple cannot:

  1. STABLE IDENTITY. `stable_identity(provider, model_id, version)` -- a
     sha256 over the triple. The vendor NAME is provenance, recorded on the
     record, deciding nothing. 500 models cost 500 records, not 500 code edits.
  2. MEASURED CAPABILITY. The statistic is the ADMISSIBLE-CONFIRM rate: of
     falsifiers this identity wrote that the runner independently re-executed,
     the fraction that (a) CONFIRMED on re-run AND (b) passed admissibility
     (imported the real target -- the Exp 55 detached-falsifier failure is
     excluded by construction, and so is the finding-RATE statistic that
     ranked that model first). Ranking uses the WILSON LOWER BOUND, never the
     point estimate: a single success gives LB(1/1) = 0.2065, which cannot
     outrank a seasoned mid-rate identity -- the founder's guard that "simply
     counting when a model is successful" is not an improvement in capability.
  3. COLD START WITHOUT NAMES. An identity with fewer than
     RETIREMENT_MIN_OUTCOMES re-verified outcomes ranks AFTER all measured
     identities, ordered among themselves by measured dispatch cost ascending
     (money + latency are measured quantities, not names). The uniform
     fallback retires itself per identity at n >= 43, derived: to separate two
     identities whose true rates differ by delta = 0.3 at 95%, the worst-case
     (p = 1/2) interval half-width must be <= delta/2, and
     n >= z^2/delta^2 = 1.959963984540054^2/0.09 = 42.6829 -> 43.
     (SymPy: solve(z*sqrt(1/(4n)) = delta/2) -> n = z^2/delta^2; Wolfram
     Language: N[1.959963984540054^2/0.30^2] = 42.68287578549028; exact Wilson
     half-width at n = 43, p = 1/2 is 0.14319 <= 0.15.)

An identity absent from the records is LOUD -- `MissingIdentityError`, never a
silent default. Measured 2026-08-30 and recorded at
`bench/reference_runner_v3.py` ("COMPOSER FALLBACK"): Fable had no
COMPOSER_MODEL_MAP entry and composed to an EMPTY system prompt with nothing
said. That failure class ends here by construction.

WIRING STATUS, stated so this is not sold as done: the consumer is
`bench/routing.py`'s ladder-order source (`DEFAULT_FALSIFIER_STRENGTH`).
Re-pointing it changes what 23 routed configs dispatch, which is the founder's
ruling to apply, not this module's to take. The committed test
(bench/tests/test_capability_identity_2026-10-14.py) executes every function.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

#: Derived above; see module docstring. The founder may tighten delta, which
#: raises this: n = ceil(z^2 / delta^2).
RETIREMENT_MIN_OUTCOMES = 43

_Z = 1.959963984540054


class MissingIdentityError(KeyError):
    """A roster identity has no capability record. LOUD, never defaulted."""


def stable_identity(provider: str, model_id: str, version: str) -> str:
    """Hash of (provider, model identifier, version). Names decide nothing."""
    raw = "\x1f".join((provider.strip().lower(), model_id.strip().lower(),
                       version.strip().lower()))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class CapabilityRecord:
    """Measured falsification outcomes for one stable identity.

    `vendor_name` is PROVENANCE: recorded, displayed, never consulted by
    ranking. `dispatch_cost` is a measured quantity (money and/or latency in
    the founder's chosen units) with its source recorded by the caller.
    """
    identity: str
    vendor_name: str
    n_reverified: int          # falsifiers the runner independently re-ran
    n_admissible_confirms: int  # CONFIRMED on re-run AND admissible
    dispatch_cost: float        # measured; LOUD upstream if absent

    def wilson_lower(self) -> float:
        n, k = self.n_reverified, self.n_admissible_confirms
        if n == 0:
            return 0.0
        p = k / n
        d = 1.0 + _Z * _Z / n
        c = (p + _Z * _Z / (2 * n)) / d
        h = (_Z / d) * math.sqrt(p * (1 - p) / n + _Z * _Z / (4 * n * n))
        return max(0.0, c - h)

    @property
    def measured(self) -> bool:
        return self.n_reverified >= RETIREMENT_MIN_OUTCOMES


def rank_writers(
    roster: list[str],
    records: dict[str, CapabilityRecord],
) -> list[str]:
    """Ladder order for `roster` (a list of stable identities).

    Measured identities first, by Wilson lower bound on the admissible-confirm
    rate, descending. Cold-start identities after, by measured dispatch cost
    ascending (cheapest probe first). Ties broken by identity hash -- stable,
    deterministic, and semantically empty. Any roster identity without a
    record raises MissingIdentityError.
    """
    missing = [i for i in roster if i not in records]
    if missing:
        raise MissingIdentityError(
            f"no capability record for identities {missing}; refusing to "
            f"default. Every identity is recorded or the run does not route."
        )
    measured = [i for i in roster if records[i].measured]
    cold = [i for i in roster if not records[i].measured]
    measured.sort(key=lambda i: (-records[i].wilson_lower(), i))
    cold.sort(key=lambda i: (records[i].dispatch_cost, i))
    return measured + cold
