# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'the_directive_set_and_capability_2026-10-14', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 2fe503435e05f523a43a0f413f2d623c484e0c3f5324ebda94e479e796493195
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Stable model identity, and a falsifier-writer order derived from measured outcomes.

Replaces NOTHING. `bench/routing.py` already exposes the seam this module fills:
`rank_falsifier_writers(labels, strength_order=...)` takes the order as a
PARAMETER, with `DEFAULT_FALSIFIER_STRENGTH` only as its default. So a measured
order is supplied by passing one, and the frozen tuple stays where it is as the
documented last resort. That is the whole integration: no deletion, no flag.

WHY NAMES MUST NOT DECIDE, stated as the mechanism rather than as a principle
-----------------------------------------------------------------------------
A vendor name is not a stable key for a capability claim. Two failures are on
record in this repository, both realised:

  * `Fable` appears in no name-keyed table. On 2026-08-30 that composed to
    FileNotFoundError and a seat ran on 0 characters of system prompt
    (`bench/reference_runner_v3.py`). It still silently inherits the 8000-char
    phenotype default today.
  * Live models are mapped onto stale phenotypes -- Opus 4.7 onto an
    `opus_4_6` entry, DeepSeek V4 Pro onto a `deepseek_v3` entry. A name
    matched; a capability did not. The table reports a measurement of a model
    that is not the one being dispatched.

A hash over (provider, model_id, version) breaks both: the version is IN the
key, so an upgrade produces a NEW identity with no inherited score, and an
unknown identity is unknown rather than silently equal to an old one.

WHAT CAPABILITY IS MEASURED AS, AND WHY NOT FINDING RATE
--------------------------------------------------------
`rank_falsifier_writers` orders models for ONE job: writing a falsifier the
harness can re-run to a decision. The statistic must therefore be a property of
that job, measured by the arbiter.

FINDING RATE IS THE WRONG STATISTIC, and this is a derivation rather than a
preference. Finding rate counts PROPOSALS, and a proposal is a quantity the
model itself controls -- "a model cannot simply say nothing", so the count can
be inflated without bound at no cost to the model. Any ranking monotone in a
model-controlled quantity is a ranking the model can climb by behaviour that is
not the behaviour being rewarded. The failure is observed, not hypothetical:
the heterogeneity statistic offered as evidence for name-keyed capability
(chi-square 280.0138, df 4, p = 2.21e-59) is computed on finding rate, and it
ranks first a model that Exp 55 showed confirming 2 of 2 with DETACHED
falsifiers -- falsifiers that do not import the real target, and so are
inadmissible under the falsifier-integrity requirement. Note also that df = 4
implies 5 groups against a 6-seat roster: the statistic omits exactly the seat
that has no table entry.

DECISIVENESS RATE IS THE RIGHT STATISTIC. Every term is an output of
`reverify_falsifier`, which the project's own docstring states the runner owns:

    decisive(identity) = (CONFIRMED + REFUTED)
                       / (CONFIRMED + REFUTED + ERROR + UNTOOLABLE
                          + INTEGRITY_VIOLATION)

CONFIRMED and REFUTED are the two verdicts in which a falsifier DECIDED
something -- and both count, because a falsifier that cleanly refutes its own
claim did its job. ERROR (broken falsifier, timeout), UNTOOLABLE (no falsifier
supplied) and INTEGRITY_VIOLATION (reached for the answer) are the ways of
failing to decide. No model self-report enters the numerator or the
denominator, so the statistic cannot be climbed by asserting anything.

THE COLD START IS AN EXPLORATION PROBLEM, NOT A TIE-BREAK PROBLEM
-----------------------------------------------------------------
Asking "what breaks the tie when there is no data" accepts a false frame: with
no data there is nothing to break the tie WITH, and any answer -- a vendor
order, an alphabetical order, a frozen tuple -- encodes a capability claim that
no measurement supports. The correct behaviour is not to pick an order but to
allocate trials so that outcomes accumulate.

Thompson sampling on a per-identity Beta posterior does exactly that, and its
cold-start behaviour is derivable rather than asserted (derivations verified by
SymPy and by a 240,000-draw Monte Carlo in
`scripts/capability_cold_start_2026-10-14.py`):

  * Beta(1,1) = Uniform(0,1). With zero outcomes every identity draws from the
    same uniform, so the induced ordering is uniform over all k! permutations
    -- measured chi-square 23.6358 on df 23, p = 0.4242, indistinguishable from
    uniform. No identity is privileged, which is the property a frozen tuple
    cannot have.
  * The posterior mean is (1+s)/(2+s+f), the Laplace rule of succession. At
    s = f = 0 it is exactly 1/2 for EVERY identity: the tie is real, and the
    construction represents it honestly instead of concealing it behind an
    order.
  * Var[Beta(1+s,1+f)] = (1+s)(1+f)/((2+s+f)^2 (3+s+f)), which at balanced data
    is 1/(4(n+3)) -- monotone decreasing with derivative -1/(4(n+3)^2) and
    limit 0.

THAT LAST RESULT ANSWERS THE RETIREMENT QUESTION BY DISSOLVING IT. There is no
outcome count at which a fallback "retires", because the prior's influence
decays continuously; a discrete switch would have to be invented, and an
invented constant is the thing this module exists to remove. What CAN be stated
is the n at which the order is reliably capability-driven, against a named
criterion. Measured, for 4 identities with true decisiveness
(0.80, 0.60, 0.40, 0.20):

    n per identity :    0      5      20     100
    P(best first)  : 0.2530 0.6733 0.9021 0.9989

So at a 90%-correct-first-pick criterion the answer is about 20 harness-arbitrated
outcomes per identity. That number travels with its criterion and with the
script that produced it; change the criterion and it changes.

REPRODUCIBILITY. The permutation is drawn from a seeded generator and the seed
is returned in the result, so a run is reproducible from its logged inputs --
the requirement that rules out unseeded randomness here.

SCOPE. This module orders falsifier WRITERS. It does not decide convergence, it
is not consulted by any convergence gate, and nothing in it accepts a model's
declaration as input. Convergence remains the harness's.
"""
from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

#: Verdicts from `reverify_falsifier` in which the falsifier DECIDED something.
#: REFUTED counts: a falsifier that ran cleanly and declined to demonstrate the
#: defect has done the job asked of it.
DECISIVE_VERDICTS: frozenset[str] = frozenset({"CONFIRMED", "REFUTED"})

#: Verdicts in which the falsifier failed to decide. Enumerated rather than
#: taken as "anything else", so a NEW verdict added to `reverify_falsifier`
#: raises here instead of being silently scored as a failure.
INDECISIVE_VERDICTS: frozenset[str] = frozenset(
    {"ERROR", "UNTOOLABLE", "INTEGRITY_VIOLATION"}
)

SCORED_VERDICTS: frozenset[str] = DECISIVE_VERDICTS | INDECISIVE_VERDICTS

#: Verdicts deliberately NOT scored. DUPLICATE says the finding was already
#: confirmed elsewhere; it is a property of the registry, not of the writer.
UNSCORED_VERDICTS: frozenset[str] = frozenset({"DUPLICATE"})


class UnknownVerdict(ValueError):
    """A verdict this module has no scoring rule for. Raised, never defaulted."""


@dataclass(frozen=True)
class ModelIdentity:
    """A capability key. The vendor name is PROVENANCE and decides nothing.

    `provider`, `model_id` and `version` form the hashed key. `display_name` is
    carried for logs and for a human reading a report; no function in this
    module branches on it, which is the point.
    """
    provider: str
    model_id: str
    version: str
    display_name: str = ""

    @property
    def key(self) -> str:
        """Stable 16-hex-char digest over (provider, model_id, version).

        Canonicalised through `json.dumps(sort_keys=True)` so the digest cannot
        drift with field order or with whitespace. Case- and
        whitespace-normalised so "OpenAI" and "openai " are one identity, which
        is the only normalisation applied -- version strings are NOT normalised
        beyond that, because "4.6" and "4.7" must stay distinct.
        """
        canonical = json.dumps(
            {
                "provider": self.provider.strip().lower(),
                "model_id": self.model_id.strip().lower(),
                "version": self.version.strip().lower(),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    def __str__(self) -> str:
        label = self.display_name or f"{self.provider}/{self.model_id}"
        return f"{label}@{self.version} [{self.key}]"


@dataclass
class OutcomeTally:
    """Harness-arbitrated falsifier outcomes for one identity.

    Every field is incremented from a `reverify_falsifier` verdict. Nothing
    here can be written by a model.
    """
    decisive: int = 0
    indecisive: int = 0
    by_verdict: dict[str, int] = field(default_factory=dict)

    @property
    def n(self) -> int:
        return self.decisive + self.indecisive

    @property
    def posterior_mean(self) -> float:
        """Laplace rule of succession, (1+s)/(2+s+f).

        At n = 0 this is exactly 0.5 for every identity. Reported so a reader
        can see the tie rather than infer it from an ordering.
        """
        return (1 + self.decisive) / (2 + self.n)

    @property
    def posterior_variance(self) -> float:
        """Var[Beta(1+s,1+f)] = (1+s)(1+f)/((2+s+f)^2 (3+s+f)).

        Monotone decreasing in n. This is the quantity that makes a discrete
        "fallback retirement" threshold unnecessary: it shrinks continuously.
        """
        a, b = 1 + self.decisive, 1 + self.indecisive
        return (a * b) / ((a + b) ** 2 * (a + b + 1))

    def record(self, verdict: str) -> None:
        v = str(verdict or "").strip().upper()
        if v in UNSCORED_VERDICTS:
            return
        if v not in SCORED_VERDICTS:
            raise UnknownVerdict(
                f"no scoring rule for verdict {v!r}; add it to DECISIVE_VERDICTS "
                f"or INDECISIVE_VERDICTS deliberately rather than letting it "
                f"default. Known: {sorted(SCORED_VERDICTS | UNSCORED_VERDICTS)}"
            )
        self.by_verdict[v] = self.by_verdict.get(v, 0) + 1
        if v in DECISIVE_VERDICTS:
            self.decisive += 1
        else:
            self.indecisive += 1


class CapabilityLedger:
    """Per-identity falsifier-writing outcomes, and the order they imply."""

    def __init__(self) -> None:
        self._tallies: dict[str, OutcomeTally] = {}
        self._identities: dict[str, ModelIdentity] = {}

    # -- recording ---------------------------------------------------------

    def record(self, identity: ModelIdentity, verdict: str) -> None:
        """Record one harness verdict against one identity."""
        self._identities.setdefault(identity.key, identity)
        self._tallies.setdefault(identity.key, OutcomeTally()).record(verdict)

    def tally(self, identity: ModelIdentity) -> OutcomeTally:
        """Tally for an identity, empty (and so at the cold-start tie) if unseen."""
        return self._tallies.get(identity.key, OutcomeTally())

    # -- the measured statistic -------------------------------------------

    def decisiveness(self, identity: ModelIdentity) -> float | None:
        """Raw decisive/(decisive+indecisive), or None with no outcomes.

        Returns None rather than a number at n = 0, so a caller cannot mistake
        an absence of evidence for a measurement of 0.5.
        """
        t = self.tally(identity)
        return None if t.n == 0 else t.decisive / t.n

    # -- the order ---------------------------------------------------------

    def rank(
        self,
        identities: Sequence[ModelIdentity],
        *,
        seed: int,
    ) -> dict:
        """Order identities strongest-first by Thompson sampling, reproducibly.

        One draw per identity from Beta(1+decisive, 1+indecisive), sorted
        descending. With no outcomes every posterior is Beta(1,1) = Uniform(0,1)
        and the ordering is uniform over permutations; as outcomes accumulate
        the draws concentrate and the ordering becomes capability-driven. There
        is no switch between the two regimes.

        `seed` is REQUIRED and is returned in the result, because a run must be
        reproducible from its logged inputs.

        Uses `random.Random` rather than numpy so this module adds no
        dependency to the routing path.
        """
        import random

        rng = random.Random(seed)
        rows = []
        for ident in identities:
            t = self.tally(ident)
            rows.append({
                "identity": ident,
                "key": ident.key,
                "provenance_name": ident.display_name,
                "n_outcomes": t.n,
                "decisive": t.decisive,
                "indecisive": t.indecisive,
                "posterior_mean": t.posterior_mean,
                "posterior_variance": t.posterior_variance,
                "measured_decisiveness": self.decisiveness(ident),
                "draw": rng.betavariate(1 + t.decisive, 1 + t.indecisive),
            })
        # Tie-break on the identity KEY, not the name: deterministic, and
        # uncorrelated with vendor for the same reason a digest is.
        rows.sort(key=lambda r: (-r["draw"], r["key"]))
        return {
            "seed": seed,
            "order": [r["identity"] for r in rows],
            "rows": rows,
            "cold_start": all(r["n_outcomes"] == 0 for r in rows),
            "total_outcomes": sum(r["n_outcomes"] for r in rows),
        }


# ---------------------------------------------------------------------------
# Integration with bench/routing.py -- via the parameter that already exists
# ---------------------------------------------------------------------------

def strength_order_from_ledger(
    ledger: CapabilityLedger,
    label_to_identity: Mapping[str, ModelIdentity],
    *,
    seed: int,
) -> tuple[str, ...]:
    """Build a `strength_order` for `rank_falsifier_writers` from measurements.

    Returns bare seat labels in measured-strongest-first order, which is the
    shape `rank_falsifier_writers(strength_order=...)` already accepts. Passing
    this is the entire integration: `DEFAULT_FALSIFIER_STRENGTH` is untouched
    and remains the default for callers that supply nothing.
    """
    by_key = {}
    for label, ident in label_to_identity.items():
        by_key.setdefault(ident.key, []).append(label)
    ranked = ledger.rank(list(dict.fromkeys(label_to_identity.values())), seed=seed)
    out: list[str] = []
    for ident in ranked["order"]:
        out.extend(by_key.get(ident.key, []))
    return tuple(out)


def unregistered(
    labels: Iterable[str], label_to_identity: Mapping[str, ModelIdentity]
) -> list[str]:
    """Seat labels with no identity. LOUD by construction -- never defaulted.

    This is the `Fable` check, generalised. A caller that gets a non-empty list
    back must refuse or report; it must not substitute a default, which is what
    `PHENOTYPE_TRANSFORMS.get(label, PhenotypeTransform())` does today.
    """
    return [l for l in labels if l not in label_to_identity]
