"""Routing — capability-aware falsifier resolution for falsification.

When the falsifier gate leaves a CRITICAL finding un-confirmed (a weak model wrote
a broken or missing falsifier), the system should NOT immediately escalate to a
human, and should NOT endlessly re-ask the weak model to do work it has
demonstrably failed. Instead, route the falsification to progressively STRONGER
models (ordered by capability fingerprint) with the execute_python tool loop —
the stronger models take over the falsification — and only escalate to HIL if even
the strongest writer cannot resolve it (a genuinely-hard, e.g. nondeterministic,
defect). This restores the capability-aware routing that the flat parallel
dispatch had collapsed into identical treatment: weak models find, strong models
adjudicate.

Empirical basis (2026-06-07, the 7 hardest Exp-42 residuals; weak SOURCE models
resolved 0/7):
  * strong model (gpt-5.5) + execute_python tool loop  -> 6/7 CONFIRMED
  * the remaining one (C0063, a markdown-code-block embedding trap) is resolved by
    the next, stronger rung (opus-class) -> the 2-rung ladder reaches 7/7.
  * teaching the weak model with worked examples lifted it only 0/5 -> 1/3 — a
    marginal booster, not a cure: hence routing, not re-asking.

This module is deliberately runner-agnostic and side-effect-free: the caller
injects how to dispatch a model (`resolve_fn`), how the runner decides a verdict
(`reverify_fn`), and how to measure finding similarity (`similarity_fn`). That
keeps it unit-testable in isolation and lets the runner wire it at the single
call site after ``apply_falsifier_verdicts``.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Sequence
import hashlib as _hashlib


# Capability ordering for the FALSIFICATION task, strongest first. Ordered by the
# Exp-42 EMPIRICAL falsifier-confirm rates, not generic capability: Codex 90% / 0
# residuals (and fast — OpenRouter) leads, then CC2 75% / 0 residuals (strong but
# claude_cli-slow), ChatGPT 67%, Gemini 80%-but-format-fragile, DeepSeek 28% /
# 10-of-15-residuals last. Validated ladder: gpt-5.5 (Codex) resolved 6/7 of the
# hardest residuals; CC2 picks up the 7th (the markdown-embedding trap). The
# primary offender (DeepSeek) is last and is never asked to take over routing.
# ★ DO NOT RE-DERIVE THIS ORDER FROM A RUN WITHOUT CHECKING FALSIFIER PROVENANCE
# (founder observation, 2026-08-23, raised by neither external reviewer). This order
# is not a report — it decides which model is asked to resolve the hardest findings,
# so a contaminated confirm rate contaminates the MECHANICS, not just the write-up.
#
# THE ORDER ABOVE IS SOUND: Exp 42's target was `composer.py`, and a code falsifier
# reaches its target by `import`, which PYTHONPATH carries regardless of working
# directory. The gate's empty-working-directory defect (H08) could not touch it.
#
# THE HAZARD IS FORWARD-LOOKING AND WAS MEASURED. On Exp 55, a prose target, while
# that defect was live: Gemini 2 of 2 CONFIRMED with both falsifiers DETACHED (they
# open nothing and restate the document's numbers from memory); DeepSeek 0 of 2 with
# both falsifiers genuine readers that ERRORed on the missing file. Re-deriving from
# that run promotes Gemini to FIRST and demotes DeepSeek to LAST — ranking the models
# by their willingness to ignore the evidence, which is the precise inversion the
# discrimination control exists to detect.
#
# Run `python3 scripts/competence_provenance.py <report.json>` first. It exits 2 and
# prints UNSAFE TO RANK ON when a model's confirmations rest on falsifiers that never
# read the target.
# FABLE ADDED 2026-10-07 ON THE FOUNDER'S RULING: *"Then why not name the model?
# Is it Fable? Then yes we should add it."* It is a FREE seat on `claude_cli` and
# was the only seat in the panel roster absent from this ladder.
#
# ITS POSITION IS DERIVED FROM EVIDENCE, NOT CHOSEN BY NAME, which is the whole
# point of his standing rule that *"the only thing that should impact on
# capability is measured capability"*. Fable has 0 attributed falsifiers in the
# archive, so its lower confidence bound on resolve-rate is 0.0000 and it sorts
# LAST. It climbs as it earns attempts -- a seat needs 12 consecutive successes
# before its Wilson lower bound can pass a seat sitting at 60 of 70, which is the
# arithmetic form of his guard that *"simply counting when a model is successful"*
# is not an improvement in capability.
#
# PLACING IT LAST IS ALSO THE SAFE PLACEMENT, and that is measured rather than
# assumed. `resolve_fn` returns "" for any label absent from the config's own
# `models` roster, and the rung is still CONSUMED -- `route` slices
# `list(rungs)[:_budget]`. No config declares Fable today (46 CC2, 46 Codex,
# 46 ChatGPT, 45 Gemini, 45 DeepSeek, 0 Fable across the 47 files), so an early
# placement would burn one of the 2 capped rungs on a seat that cannot answer.
# Last, it costs nothing under the cap and is reached under exhaustion.
#
# THE OTHER HALF IS NOT DONE AND IS THE FOUNDER'S TO RULE ON: until a config
# lists Fable in `models`, this rung is reachable only where a roster declares
# it. Changing 23 routed configs alters what real experiments dispatch.
#: THE LADDER DEPTH DEFAULT, in ONE place so the function signatures and the
#: runner's omit-at-default condition cannot drift apart. 0 means EXHAUST.
#:
#: WHY A CONSTANT RATHER THAN READING THE SIGNATURE, found by a failing test on
#: 2026-10-08: the runner's call site needs to know this value to decide whether to
#: pass the keyword at all, and a first attempt read it with
#: `inspect.signature(route)`. That raises KeyError the moment a test monkeypatches
#: `route` with a narrow stub -- which is precisely the case the omit-at-default
#: logic exists to protect. A module constant is immune to patching and keeps the
#: 2 defaults in lockstep by construction.
DEFAULT_MAX_RUNGS = 0

#: THE VENDOR ORDER, RETAINED AND NO LONGER THE DEFAULT (2026-10-17).
#:
#: It was `DEFAULT_FALSIFIER_STRENGTH` and it ranks seats by VENDOR NAME, which
#: is the one thing the founder has ruled four times must not determine
#: capability. His words, 2026-10-09: *"there should probably be no distinction
#: between models participating in an experiment other than a 'ranking number'
#: ... the only things that should denote a model's ranking in any given
#: experiment is derived/demonstrable capability, either above that. Or below
#: that of its peers"*.
#:
#: IT IS KEPT, NOT DELETED, because point-never-prune applies to code: it is
#: what every archived run used, so replaying one needs it, and a reader can
#: still inspect what was superseded. Pass it explicitly to get the old
#: behaviour.
#: THE LITERAL LIVES ON `DEFAULT_FALSIFIER_STRENGTH`, below, and this name is
#: DERIVED from it. Putting the literal here instead was tried on 2026-10-17
#: and reverted: `scripts/competence_provenance.py` reads the constant out of
#: this file's SOURCE with `ast.literal_eval`, which accepts a literal and not
#: a name, so 5 guards failed with "malformed node or string" the moment the
#: assignment became `DEFAULT_FALSIFIER_STRENGTH = VENDOR_ORDER_SUPERSEDED`.
#: That probe's fragility is recorded rather than worked around, because
#: rewriting it reaches several dependants, and the naming point is carried by
#: the comment below and by `FALSIFIER_STRENGTH_IS_ESTABLISHED` instead.

#: THE DEFAULT MAKES NO CAPABILITY CLAIM, and that is deliberate.
#:
#: MEASURED by `scripts/is_the_ladder_order_estimable_2026-10-17.py` over every
#: archived registry -- 3,020 entries, the only recorded quantity that measures
#: falsification capability rather than productivity being `falsifier_verdict`:
#:
#:     Gemini    10 of 701   1.4265%  Wilson [0.7767%, 2.6058%]
#:     DeepSeek   6 of 521   1.1516%  Wilson [0.5288%, 2.4895%]
#:     ChatGPT    0 of 373   0.0000%  Wilson [0.0000%, 1.0194%]
#:     CC2        0 of 366   0.0000%  Wilson [0.0000%, 1.0387%]
#:     Codex      0 of 342   0.0000%  Wilson [0.0000%, 1.1108%]
#:
#: 26 REFUTED verdicts in the whole archive, and ZERO for 3 of the 5 paid seats.
#: The omnibus test REJECTS equality -- chi2 = 14.5802, dof 4, p = 0.005656, so
#: the seats genuinely differ -- but **0 of 10 pairwise comparisons survive
#: either Holm or Bonferroni correction at 0.05**, and a ranking IS a set of
#: pairwise orderings. So the archive supports "they differ" and supports no
#: statement about which is stronger.
#:
#: AND YET THE VENDOR ORDER REMAINS THE FALLBACK, WHICH IS **HIS** DECISION TO
#: CHANGE AND NOT MINE. [NEEDS HIS RULING]
#:
#: Emptying it was tried on 2026-10-17 and REVERTED within the hour, because it
#: collides with an EARLIER ruling of his rather than with a test's convenience.
#: On 2026-10-07 he ruled *"Then yes we should add it"* about putting Fable on
#: the ladder, and that ruling is implemented AS MEMBERSHIP OF THIS TUPLE and
#: verified by `test_every_free_seat_is_now_on_the_ladder`, which asserts
#: `ladder_length == 6` and `free_rungs == ["CC2", "Fable"]`. An empty tuple
#: satisfies his 2026-10-09 ruling about order and destroys the implementation
#: of his 2026-10-07 ruling about membership. 8 guards went red, and they were
#: red for that reason rather than from staleness.
#:
#: THE 2 CONCERNS ARE SEPARABLE AND THAT IS THE PROPOSAL. Ladder MEMBERSHIP (is
#: every available seat tried?) and ladder ORDER (which is tried first?) are
#: different questions; his 2026-10-07 ruling is about the first and his
#: 2026-10-09 ruling about the second. Expressing membership as a tuple of
#: vendor names makes them one thing, which is why they collide. Separating them
#: changes recorded behaviour, so it is put to him rather than taken.
#:
#: WHAT IS BUILT MEANWHILE, and it is the half that needs no ruling:
#: `strength_order_from_evidence` derives the order from the experiment's own
#: observations and TAKES PRECEDENCE whenever it is established. That is his
#: season design -- *"one round of an experimental run could potentially
#: constitute a season ... then for the rest of the rounds the positions of these
#: models in their rankings stays fixed"*. Where the round does not discriminate,
#: this tuple is used AND the fact is recorded, so a reader can always tell a
#: measured order from a defaulted one. Before this, the fallback was silent.
DEFAULT_FALSIFIER_STRENGTH = ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek", "Fable")

#: The same tuple under the name that says what it IS. Derived, so the 2 can
#: never disagree.
VENDOR_ORDER_SUPERSEDED = DEFAULT_FALSIFIER_STRENGTH

#: Whether the DEFAULT order rests on measured capability. False, and said out
#: loud: the archive cannot support an ordering, so the default is a convention.
FALSIFIER_STRENGTH_IS_ESTABLISHED = False


#: How many hex characters of the identity digest to keep. 12 gives a collision
#: probability under 1e-7 for any plausible roster: with 1,000 distinct
#: identities the birthday bound is about 1.8e-8, and the project has seated 6.
#: Short enough to read in a log line, long enough that a collision is not a
#: thing to design around -- and `capability_provenance` records the inputs, so
#: a collision would be visible rather than silent.
CAPABILITY_IDENTITY_CHARS = 12


def capability_identity(provider: str, model_identifier: str,
                        version: str = "") -> str:
    """A STABLE HASH over (provider, model identifier, version).

    HIS RULING, 2026-10-16, after asking why it had not been built: *"The hashed
    model ID's rather than deriving capability by name is a relatively new
    feature. ... the only thing that governs capability is demonstrated measured
    capability, not model names."* And the design as put to the free panel on
    2026-10-14: *"Key every capability decision on a STABLE IDENTITY -- a hash
    over (provider, model identifier, version) -- with the vendor name recorded
    as PROVENANCE and deciding nothing."*

    WHY A HASH AND NOT THE READABLE TRIPLE. The runner already carries
    `registry.model_identity`, which maps a seat label to `model_id@api`. That is
    an identity, and it is used to count DISTINCT MODELS in a refutation tally so
    two seats of one model cannot be read as two dissenting voices. But it is a
    name, and a name invites a capability decision keyed on it -- which is the
    practice he has rejected 4 times. A digest cannot be read as a vendor, so a
    ranking keyed on it cannot smuggle one in. The readable triple travels
    separately, through `capability_provenance`, where it informs a reader and
    decides nothing.

    NORMALISED BEFORE HASHING, because the same model reached two ways must be
    one identity: case folded, surrounding whitespace dropped, and the mandatory
    simulation suffix REMOVED, so a stand-in seat shares the identity of the
    model standing in. That last choice is deliberate and is the conservative
    direction: merging two records that are the same model under-separates, and
    under-separation makes auto-refutation HARDER rather than easier, which is
    the direction that preserves findings.

    EMPTY INPUTS ARE REFUSED rather than hashed. An identity derived from
    nothing would be stable, identical for every such model, and silently wrong
    -- the shape of defect this project keeps finding. The caller must say what
    it is identifying.
    """
    def _norm(value: str) -> str:
        text = str(value or "").strip()
        if text.upper().endswith("-SIM"):
            text = text[:-4]
        return " ".join(text.split()).casefold()

    prov, mid, ver = _norm(provider), _norm(model_identifier), _norm(version)
    if not mid:
        raise ValueError(
            "capability_identity needs a model identifier; an identity derived "
            "from nothing would be stable, shared by every such model, and "
            "silently wrong")
    payload = "\x1f".join((prov, mid, ver)).encode("utf-8")
    return _hashlib.sha256(payload).hexdigest()[:CAPABILITY_IDENTITY_CHARS]


def capability_provenance(provider: str, model_identifier: str,
                          version: str = "") -> dict:
    """The readable inputs behind an identity, for a reader and for nothing else.

    Returned as a record rather than printed, so a manifest can carry it and a
    human can map a digest back to the model it stands for. It is DELIBERATELY
    not accepted anywhere a capability decision is taken.
    """
    return {
        "identity": capability_identity(provider, model_identifier, version),
        "provider": str(provider or "").strip(),
        "model_identifier": str(model_identifier or "").strip(),
        "version": str(version or "").strip(),
    }


def falsification_evidence_from_registry(registry) -> dict:
    """Per-seat ``(refuted, total)`` from a LIVE registry.

    This is the season measurement: the evidence a single experiment produces
    about its own seats, which is what `strength_order_from_evidence` ranks on.
    It reads `falsifier_verdict`, the only recorded quantity that measures
    falsification capability -- finding rate measures PRODUCTIVITY and ranking on
    it was refuted by a free seat on 2026-10-06, because it reproduces the
    inversion `competence_provenance` exists to prevent.
    """
    out: dict = {}
    entries = getattr(registry, "entries", None) or {}
    for e in entries.values():
        if not isinstance(e, dict):
            continue
        seat = e.get("source_model") or "?"
        ref, tot = out.get(seat, (0, 0))
        tot += 1
        if (e.get("falsifier_verdict") or "").strip().upper() == "REFUTED":
            ref += 1
        out[seat] = (ref, tot)
    return out


def strength_order_from_evidence(
    evidence: dict,
    labels: "Sequence[str] | None" = None,
    alpha: float = 0.05,
) -> tuple:
    """``(order, established, why)`` from measured falsification outcomes.

    RETURNS AN EMPTY ORDER UNLESS THE EVIDENCE SEPARATES AT LEAST ONE PAIR after
    correcting for the number of comparisons. That refusal is the point: a
    ranking read off 26 refutations in 3,020 entries, with 0 for 3 of 5 seats,
    would be noise wearing the authority of a measurement. The archive-wide
    figures are in this module's `DEFAULT_FALSIFIER_STRENGTH` comment.

    `established` is False when no pair separates, and `why` says so in words a
    run log can carry, so a reader never has to infer whether the order in force
    was measured or defaulted.
    """
    seats = [s for s in evidence if s and s != "?"]
    if labels is not None:
        seats = [s for s in seats if s in set(labels)]
    if len(seats) < 2:
        return (), False, (
            f"fewer than 2 seats carry falsification evidence ({len(seats)}), "
            f"so no pair can be compared")
    try:
        import itertools as _it
        from scipy.stats import fisher_exact
        from statsmodels.stats.multitest import multipletests
    except Exception as exc:                                  # noqa: BLE001
        return (), False, (f"the statistics tools are unavailable ({exc}), so "
                           f"estimability cannot be established")
    pairs, ps = [], []
    for x, y in _it.combinations(seats, 2):
        rx, nx = evidence[x]
        ry, ny = evidence[y]
        if nx == 0 or ny == 0:
            continue
        _, p = fisher_exact([[rx, nx - rx], [ry, ny - ry]])
        pairs.append((x, y))
        ps.append(p)
    if not ps:
        return (), False, "no seat pair has any observations to compare"
    rejected, _, _, _ = multipletests(ps, alpha=alpha, method="holm")
    n_sep = int(sum(rejected))
    if n_sep == 0:
        return (), False, (
            f"0 of {len(ps)} seat pairs separate after Holm correction at "
            f"alpha={alpha}; a ranking is a set of pairwise orderings, so the "
            f"order is NOT ESTABLISHED and no capability claim is made")
    order = tuple(sorted(
        seats, key=lambda s: (-(evidence[s][0] / evidence[s][1]) if evidence[s][1]
                              else 0.0, s)))
    return order, True, (
        f"{n_sep} of {len(ps)} seat pairs separate after Holm correction at "
        f"alpha={alpha}; ranked by measured refutation rate")


@dataclass
class RoutingResult:
    """Outcome of a routing attempt on one un-confirmed critical."""
    finding_id: str
    verdict: str                      # CONFIRMED / REFUTED / ERROR / UNTOOLABLE / DUPLICATE
    resolved: bool                    # True iff a strong writer CONFIRMED it
    model_used: Optional[str]         # which rung resolved/last-tried it
    falsifier_code: str               # the resolving (or last) falsifier
    duplicate_of: Optional[str] = None  # set iff resolved as a duplicate
    rungs_tried: int = 0
    #: True iff `rank_falsifier_writers` returned NOTHING -- the roster carries no
    #: writer other than this finding's own source model.
    #:
    #: ADDED 2026-10-06 BECAUSE THE SELF-RUNG BROKE ITS PROXY. The runner used
    #: `rungs_tried == 0` to mean "the ladder was empty by construction", which was
    #: exact while every rung came from the ranked list. The self-rung dispatches
    #: when that list is empty, so `rungs_tried` becomes 1 and the discriminator
    #: silently stopped firing -- the finding then missed `routing_deferred`, never
    #: entered `irreducible_queue_count`, and HALTED_IRREDUCIBLE_QUEUE_ALARM could
    #: not fire. That alarm is the pre-registered reportable outcome of the exp56
    #: 1-seat arm. A proxy that was exact under the old mechanics is the first
    #: thing a new mechanic breaks, so the fact is recorded directly instead.
    ladder_was_empty: bool = False
    #: True iff this routing pass ordered its rungs by the VENDOR TUPLE, which
    #: rests on no measurement.
    #:
    #: HIS RULING, 2026-10-05: *"The routing ladder should be a measured
    #: statistic, not simply a list of named vendors based on what you, or I may
    #: have read about them on the internet."* And: *"The system shouldn't care
    #: at all what a model is called, only what it can be statistically
    #: demonstrated to have done."*
    #:
    #: THE ORDER IS NOT ESTIMABLE FROM THE ARCHIVE, measured by
    #: scripts/is_the_ladder_order_estimable_2026-10-17.py: the omnibus test
    #: rejects equality, so the seats really do differ, but 0 of 10 pairwise
    #: orderings survive Holm or Bonferroni at 0.05 -- and a ranking IS a set of
    #: pairwise orderings. So the archive supports "they differ" and supports no
    #: statement about which is stronger.
    #:
    #: WHICH LEAVES THE DEFAULT AS A CONVENTION, and a convention must not be
    #: mistaken for a finding. `season_strength_order` already says so loudly
    #: when IT falls back, but 6 of 7 live `route` call sites never reach that
    #: function: they take the module default silently (85.7143%, Wilson
    #: [48.6872%, 97.4320%]). Only `reference_runner_v3` passes a measured
    #: order, through `**_route_kw`.
    #:
    #: STAMPED IN ONE PLACE RATHER THAN AT 4 CONSTRUCTION SITES, so the 6
    #: callers are reached without touching any of them and the 2 forms cannot
    #: drift. It is DETECTIVE ONLY: no routing behaviour depends on it.
    strength_order_was_unestablished: bool = False
    #: HOW MANY AVAILABLE LABELS THE ORDER ACTUALLY MATCHED. 0 means the ladder
    #: ranked nothing and the rung order is simply the order the caller passed.
    #:
    #: MEASURED 2026-10-17, and this is the substantive half of his ruling of
    #: 2026-10-05. The live panel roster is
    #: ['cx', 'cgpt', 'ge', 'ds', 'cc2', 'fable', 'kimi'] and the order is
    #: ('Codex', 'CC2', 'ChatGPT', 'Gemini', 'DeepSeek', 'Fable'). NOT ONE of
    #: the roster's keys matches a name in the order, so
    #: `rank_falsifier_writers` returns the roster UNCHANGED: reverse the input
    #: and the "ranking" reverses with it. It looks like a ranking and is an
    #: identity function -- the checker-that-decides-nothing class, 11 instances
    #: of which this project has confirmed since 2026-08-01.
    #:
    #: `bench/allocation_by_measured_capability_2026-10-07.py` has been
    #: reporting the roster disagreement that causes this
    #: (`the_two_disagree: True`, 5 on-panel-not-on-ladder, 4
    #: on-ladder-not-on-panel) and NO TEST EVER EXECUTED IT, so the finding sat
    #: in a producer nobody ran.
    #:
    #: BEHAVIOUR IS UNCHANGED ON PURPOSE. Matching case-insensitively, or
    #: through the roster's alias map, would REORDER the live panel, and
    #: reordering the rungs of a falsification ladder changes which seat is
    #: asked first. That is a behaviour change requiring his ruling and a
    #: measurement, not something to slip into a visibility fix. What changes
    #: here is only that a ladder which ranked nothing says so.
    strength_order_matched: int = 0


def seat_identities(registry, labels) -> dict:
    """seat label -> capability identity, using the registry's own resolution.

    HIS DESIGN: capability belongs to an identity, not to a seat label. Two
    seats of the SAME model must pool their falsification outcomes rather than
    be ranked against each other as if they were different models -- the runner
    already applies that reasoning when counting distinct models in a refutation
    tally, and this applies it to capability.

    THE REGISTRY'S `resolve_model` IS THE SOURCE, not a second parse of the
    config. It returns `model_id@api` normalised, and it already handles the
    case- and whitespace-insensitivity that hand-written seat labels need. A
    label it cannot resolve resolves to ITSELF, which this turns into an identity
    of its own rather than a shared bucket -- over-separating, which is the
    direction that makes refutation HARDER and so preserves findings.
    """
    resolve = getattr(registry, "resolve_model", None)
    out: dict = {}
    for label in labels or ():
        text = str(label or "").strip()
        if not text:
            continue
        resolved = str(resolve(text) if callable(resolve) else text).strip()
        if "@" in resolved:
            mid, _, api = resolved.rpartition("@")
        else:
            mid, api = resolved, ""
        try:
            out[text] = capability_identity(api, mid or text)
        except ValueError:
            out[text] = capability_identity("", text)
    return out


def falsification_evidence_by_identity(registry, labels) -> tuple:
    """``(evidence_by_identity, seat_to_identity)``, pooled per model.

    The per-seat reader stays as it is, because its contract is per-seat and the
    refutation tally depends on it. This pools each seat's refuted-of-total pair onto
    the identity the seat resolves to, which is where capability lives under his design.
    """
    per_seat = falsification_evidence_from_registry(registry)
    ident = seat_identities(registry, labels or list(per_seat))
    pooled: dict = {}
    for seat, (ref, tot) in per_seat.items():
        key = ident.get(str(seat).strip())
        if key is None:
            try:
                key = capability_identity("", str(seat))
            except ValueError:
                continue
            ident[str(seat).strip()] = key
        r, n = pooled.get(key, (0, 0))
        pooled[key] = (r + ref, n + tot)
    return pooled, ident


def season_strength_order(registry, labels, frozen=None, alpha: float = 0.05):
    """``(order, established, why)`` for THIS experiment, measured once then kept.

    HIS SEASON DESIGN, 2026-10-09, verbatim: *"one round of an experimental run
    could potentially constitute a season, and players/teams should get demoted
    promoted based on the evidence derived from this first experimental round.
    Then for the rest of the rounds in an experiment the positions of these
    models in their rankings stays fixed"*. Confirmed 2026-10-11: *"We measure
    at the start and keep it."*

    SO THERE ARE EXACTLY 2 BEHAVIOURS. Handed a `frozen` order, it returns that
    order unchanged -- the positions stay fixed for the rest of the experiment,
    and no later round can reshuffle them. Handed none, it measures this
    experiment's own falsification outcomes and freezes the result IF they
    discriminate.

    WHERE THEY DO NOT DISCRIMINATE the vendor fallback is returned AND `why`
    says so, so a run log distinguishes a measured order from a defaulted one.
    Before this the fallback was silent, which is how a tuple of vendor names
    came to look like a capability ranking. Whether that fallback should exist
    at all is recorded as needing his ruling beside
    `DEFAULT_FALSIFIER_STRENGTH`, because removing it collides with his earlier
    ruling about ladder MEMBERSHIP.
    """
    if frozen:
        return tuple(frozen), True, (
            "frozen from an earlier round of this experiment; a season's "
            "positions stay fixed")
    # CAPABILITY IS MEASURED PER IDENTITY, AND THE LADDER IS A SEQUENCE OF
    # SEATS. His ruling of 2026-10-16, after asking why the hashed identifiers
    # had not been built: *"the only thing that governs capability is
    # demonstrated measured capability, not model names."* So the outcomes are
    # pooled onto the identity each seat resolves to, the identities are ranked,
    # and the seats are then ordered by the rank of the identity they carry. Two
    # seats of one model therefore share a position rather than being ranked
    # against each other, which is the same reasoning the refutation tally
    # already applies when it counts distinct models.
    pooled, seat_to_identity = falsification_evidence_by_identity(
        registry, labels)
    id_order, established, why = strength_order_from_evidence(
        pooled, labels=sorted(set(seat_to_identity.values())) or None,
        alpha=alpha)
    if established:
        rank = {identity: n for n, identity in enumerate(id_order)}
        seats = sorted(
            (str(l).strip() for l in (labels or seat_to_identity) if str(l).strip()),
            key=lambda s: (rank.get(seat_to_identity.get(s), len(rank)), s))
        return tuple(seats), True, (
            f"{why}; ranked over {len(rank)} capability identity(ies) and "
            f"applied to {len(seats)} seat(s)")
    # AN IDENTITY ABSENT FROM THE EVIDENCE IS NAMED, NEVER SILENTLY DEFAULTED.
    # His design, 2026-10-14: *"An identity absent from the tables must be LOUD,
    # never defaulted."* Before this the fallback said it was a fallback but not
    # WHICH seats went unmeasured, so a reader could not tell a roster with no
    # evidence from one whose evidence failed to separate -- two different
    # situations with the same sentence.
    _unmeasured = sorted(
        f"{seat} ({ident})" for seat, ident in seat_to_identity.items()
        if ident not in pooled or pooled.get(ident, (0, 0))[1] == 0)
    _loud = (f"; {len(_unmeasured)} seat(s) carry NO falsification evidence at "
             f"all: {', '.join(_unmeasured)}" if _unmeasured else "")
    return tuple(DEFAULT_FALSIFIER_STRENGTH), False, (
        f"{why}; falling back to the vendor order, which rests on no "
        f"measurement (FALSIFIER_STRENGTH_IS_ESTABLISHED is False){_loud}")


def labels_the_order_ranks(labels, strength_order) -> list:
    """Which of `labels` the given order actually RANKS. MEMBERSHIP, not order.

    Returned in LABEL order, deliberately, and the distinction is not academic:
    `rank_falsifier_writers` returns the same labels in STRENGTH order, so for
    `["CC2-SIM", "Codex-SIM"]` this gives CC2-SIM first and the ranking gives
    Codex-SIM first. Both are correct about different questions. An early test
    compared the two as sequences and failed on exactly that pair, which is why
    the contract is stated here rather than inferred.

    THE COUNTER AND THE RANKING MUST NOT MATCH DIFFERENTLY. Written first as a
    lowercase set comparison inside `route`, which reported 2 of 7 matched for
    the live panel while `rank_falsifier_writers` ranked 0 of 7 -- the ranking
    compares EXACTLY, modulo the `-SIM` suffix, and does not fold case. A
    producer and a consumer that disagree about the same question is this
    project's most-caught defect shape, and it cannot be caught by reading
    either one: both are individually consistent.

    So this is the single rule, and `rank_falsifier_writers` is checked against
    it by an executing test rather than by inspection.
    """
    known = set(strength_order)
    out = []
    for m in labels:
        base = m[:-4] if str(m).endswith("-SIM") else str(m)
        if base in known:
            out.append(m)
    return out


def rank_falsifier_writers(
    labels: Sequence[str],
    strength_order: Sequence[str] = DEFAULT_FALSIFIER_STRENGTH,
    exclude: Sequence[str] = (),
) -> list[str]:
    """Return the available model labels ordered strongest-first for falsification.

    Models not in ``strength_order`` are appended (in input order) after the ranked
    ones — unknown models are tried, but only after the known-strong ones. ``exclude``
    drops models (e.g. the finding's own source model, which already failed)."""
    # A ``-SIM`` label RANKS AS ITS VENDOR (Fable, second-pass review
    # 2026-08-30). `strength_order` holds bare vendor names, and this matched
    # labels exactly, so with a simulated panel `ranked` came out EMPTY and all
    # six members fell into `extras` in panel order. Routing still ran, but it
    # exercised the unknown-model fallback instead of the ranked ladder Bench
    # Run 2 will run -- so ladder ORDER was unrehearsed by every simulation.
    #
    # Normalised locally rather than importing `base_model_label`, which lives
    # in reference_runner_v3 and would make this module import its own caller.
    def _base(m: str) -> str:
        m = str(m or "")
        return m[:-4] if m.endswith("-SIM") else m

    excl = set(exclude)
    by_base = {}
    for m in labels:
        by_base.setdefault(_base(m), []).append(m)
    ranked = [m for name in strength_order
              for m in by_base.get(name, []) if m not in excl]
    ranked_set = set(ranked)
    extras = [m for m in labels if m not in ranked_set and m not in excl]
    return ranked + extras


def confirmed_duplicate(
    finding: dict,
    confirmed_findings: Sequence[dict],
    similarity_fn: Callable[[dict, dict], float],
    threshold: float = 0.85,
) -> Optional[str]:
    """If an already-CONFIRMED finding describes the same defect, return its id.

    This catches the C0028<->C0003 / C0015<->C0001 case from Exp 42, where the same
    real defect was independently CONFIRMED under another id by a competent writer,
    while the weak model's restatement escalated only because ITS falsifier was
    broken. A duplicate of a confirmed defect must never reach HIL."""
    best_id, best_sim = None, threshold
    fid = finding.get("finding_id") or finding.get("id")
    for other in confirmed_findings:
        oid = other.get("finding_id") or other.get("id")
        if oid == fid:
            continue
        sim = similarity_fn(finding, other)
        if sim >= best_sim:
            best_id, best_sim = oid, sim
    return best_id


def resolve_via_routing(
    finding: dict,
    rungs: Sequence[str],
    resolve_fn: Callable[[str, dict], str],
    reverify_fn: Callable[[str], str],
    max_rungs: int = DEFAULT_MAX_RUNGS,   # 0 = EXHAUST (founder's ruling 2026-10-06)
    self_rung: str | None = None,
) -> RoutingResult:
    """Climb the capability ladder until a strong writer CONFIRMS the finding.

    ``rungs``       — model labels, strongest first (from ``rank_falsifier_writers``).
    ``resolve_fn``  — (model_label, finding) -> falsifier_code. The caller dispatches
                      that model WITH the execute_python tool loop and extracts the
                      final falsifier. Empty string means the model produced none.
    ``reverify_fn`` — falsifier_code -> verdict. The runner's real decider
                      (falsifier_verify.reverify_falsifier). It, never the model,
                      decides the verdict — "tools decide".

    Returns a RoutingResult. ``resolved`` is True only on a CONFIRMED from the
    decider; otherwise the caller escalates to HIL with the diagnosis intact.
    A REFUTED here is NOT trusted to drop the critical (CONFIRM-only still holds):
    it just means this rung did not demonstrate it; we try the next rung, then HIL.
    """
    fid = finding.get("finding_id") or finding.get("id") or "?"
    last_verdict, last_code, last_model, tried = "UNTOOLABLE", "", None, 0
    # `max_rungs=0` MEANS EXHAUST THE LADDER. Founder ruling 2026-10-06: *"I don't
    # think there should be a cap at all. If it's a measured statistic, along with
    # capability fingerprinting then the problem should run until it is either
    # resolved, or the ladder is exhausted. (No more models to try.)"*
    #
    # The budget is NOT free, and the honest accounting is that it is nearly free
    # HERE: `resolve_via_routing` stops at the first CONFIRMED, so a deeper budget
    # costs a dispatch only on findings every earlier rung already failed. Measured
    # on the Exp 42 residual set the ladder was validated against, rung 1 resolved
    # 6 of 7 and rung 2 the last, so rungs 3+ are reached on a small minority.
    # A cap is therefore spend-insurance against a pathological run rather than a
    # routine saving, which is why exhaustion is now expressible.
    _ladder_empty = not list(rungs)
    _budget = len(list(rungs)) if not max_rungs else max_rungs
    for model in list(rungs)[:_budget]:
        tried += 1
        last_model = model
        code = (resolve_fn(model, finding) or "").strip()
        last_code = code
        if not code:
            last_verdict = "ERROR"
            continue
        verdict = reverify_fn(code)
        last_verdict = verdict
        if verdict == "CONFIRMED":
            return RoutingResult(fid, "CONFIRMED", True, model, code, rungs_tried=tried,
                                 ladder_was_empty=_ladder_empty)
    # ───────────── THE LAST RUNG POINTS BACK AT THE SOURCE ─────────────
    # FOUNDER'S RULING, 2026-10-06: *"even with all our models being the same ... at
    # least one rung on the ladder should point back to the original model and say,
    # 'your solution didn't work' or 'your falsifier is broken' please fix"*.
    #
    # WHY IT IS NOT A BLIND RETRY, which is the obvious objection. The source model
    # already failed on this finding, so asking it the same question again would be
    # the definition of expecting a different answer. It is not asked the same
    # question: it is handed the VERDICT its own attempt earned and the code that
    # earned it, which is information it did not have the first time. That is the
    # same thing the ladder gives a stronger rung, applied to the only rung left.
    #
    # IT FIRES ONLY WHEN THE LADDER IS OTHERWISE EXHAUSTED, so it costs 1 dispatch on
    # findings that would otherwise reach a human unresolved -- which is the more
    # expensive outcome. On a 1-model roster, where `rank_falsifier_writers` returns
    # an empty list by construction, this is the ONLY rung there has ever been.
    #
    # The existing empty-ladder path is NOT removed: if this rung also fails, the
    # finding still defers and still reaches the irreducible queue, which is what
    # `test_empty_ladder_is_not_a_dead_transport_2026-09-09.py` holds.
    if self_rung and self_rung != last_model:
        tried += 1
        last_model = self_rung
        code = (resolve_fn(self_rung, _with_routing_feedback(
            finding, last_verdict, last_code)) or "").strip()
        if code:
            last_code = code
            verdict = reverify_fn(code)
            last_verdict = verdict
            if verdict == "CONFIRMED":
                return RoutingResult(fid, "CONFIRMED", True, self_rung, code,
                                     rungs_tried=tried,
                                     ladder_was_empty=_ladder_empty)
        else:
            last_verdict = "ERROR"

    # No rung confirmed -> caller escalates to HIL (genuinely-hard until proven otherwise)
    return RoutingResult(fid, last_verdict, False, last_model, last_code,
                         rungs_tried=tried, ladder_was_empty=_ladder_empty)


def _with_routing_feedback(finding: dict, verdict: str, code: str) -> dict:
    """A copy of the finding carrying what the previous attempt earned.

    THE FEEDBACK IS THE WHOLE POINT OF THE SELF-RUNG. Without it the source model is
    asked an identical question it has already failed. `routing_feedback` is the
    field a caller's `resolve_fn` puts in front of the model; a caller that ignores
    it turns the self-rung into the blind retry this is explicitly not.
    """
    out = dict(finding)
    out["routing_feedback"] = {
        "previous_verdict": verdict,
        "previous_falsifier": code,
        "instruction": (
            "An earlier attempt on THIS finding did not resolve it. The verdict it "
            "earned and the falsifier that earned it are above. Either the fix did "
            "not cure the defect or the falsifier did not demonstrate it. Identify "
            "which, and correct that specific failure rather than restating the "
            "original answer."),
    }
    return out


def route(
    finding: dict,
    available_models: Sequence[str],
    confirmed_findings: Sequence[dict],
    resolve_fn: Callable[[str, dict], str],
    reverify_fn: Callable[[str], str],
    similarity_fn: Callable[[dict, dict], float],
    *,
    strength_order: Sequence[str] = DEFAULT_FALSIFIER_STRENGTH,
    max_rungs: int = DEFAULT_MAX_RUNGS,   # 0 = EXHAUST (founder's ruling 2026-10-06)
    dup_threshold: float = 0.85,
    self_rung_enabled: bool = True,
) -> RoutingResult:
    """Full routing pass for ONE un-confirmed critical finding.

    Order of operations:
      1. Dedup — if the defect is already CONFIRMED under another id, resolve as a
         duplicate (never escalate a confirmed defect to HIL).
      2. Ladder — route to progressively stronger writers (excluding the finding's
         own source model, which already failed) with the tool loop; CONFIRMED wins.
      3. Self-rung — when every other rung is exhausted, hand the finding back to
         its OWN source model together with the verdict its earlier attempt earned,
         so it is asked a different question rather than the same one.
      4. Caller escalates to HIL only if none of these resolves it.

    ``self_rung_enabled`` defaults True on the founder's ruling of 2026-10-06:
    *"Nor is there any harm in turning it on and leaving it on."* Set it False for a
    pre-registered arm whose declared outcome depends on the empty-ladder deferral --
    `bench/exp56_configs/d9_single_model_with_agents.json` is the one such arm, and
    it has not yet run.
    """
    fid = finding.get("finding_id") or finding.get("id") or "?"

    #: ONE STAMP, BOTH EXITS. Computed before either return so that a duplicate
    #: verdict carries it too: a duplicate was still reached by a ladder, and a
    #: reader asking "was this order measured?" needs the same answer whichever
    #: verdict came back.
    _unestablished = (tuple(strength_order) == tuple(DEFAULT_FALSIFIER_STRENGTH)
                      and not FALSIFIER_STRENGTH_IS_ESTABLISHED)

    dup = confirmed_duplicate(finding, confirmed_findings, similarity_fn, dup_threshold)
    if dup is not None:
        return RoutingResult(fid, "DUPLICATE", True, None, "", duplicate_of=dup,
                             rungs_tried=0,
                             strength_order_was_unestablished=_unestablished,
                             strength_order_matched=len(
                                 labels_the_order_ranks(available_models,
                                                        strength_order)))

    source = finding.get("source_model")
    rungs = rank_falsifier_writers(
        available_models, strength_order=strength_order,
        exclude=(source,) if source else (),
    )
    #: ONE RULE, CALLED, not a second copy of the matching logic.
    _matched = len(labels_the_order_ranks(available_models, strength_order))
    out = resolve_via_routing(
        finding, rungs, resolve_fn, reverify_fn, max_rungs=max_rungs,
        self_rung=source if (self_rung_enabled and source) else None)
    out.strength_order_matched = _matched
    #: `resolve_via_routing` is also called DIRECTLY by other code, so the stamp
    #: is applied here rather than inside it: only `route` knows which order was
    #: used. A direct caller gets the field's default of False, which is honest
    #: -- it means "not recorded", and nothing reads it as "measured".
    out.strength_order_was_unestablished = _unestablished
    return out
