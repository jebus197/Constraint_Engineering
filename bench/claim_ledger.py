#!/usr/bin/env python3
"""The CLAIM as a unit of admissibility, recorded per target.

WHY THIS EXISTS. The free panel of 2026-09-30 was asked whether the harness
honours the founder's principle that models reason first and tools verify
second. Both seats refuted the brief's framing in the same place and converged
on the same finding, which is one level above what task A19's title says.

  A19 says:  "S_k classifies the TARGET, not the ELEMENT".
  cc2 found: "S_k classifies neither target nor element -- it classifies a FIX."
  fable found: the harness "has all three stages for findings; it lacks them as
               the unit of admissibility."

So nothing in the harness judged a CLAIM as its unit. The founder's ruling on
being shown the design: "Build it, apply it and test it before the next
simulated run."

THE DESIGN IS THE SEATS', NOT THIS FILE'S. fable generated 4 candidate
architectures and falsified 3 of its own before recommending the survivor
(design note: `experimental_notes/fable_intelligence_first_2026-09-30.md`, Q1).
Its 4 pieces, none of them a new instrument:

  1. a CLAIM LEDGER per target -- the REASON stage's output recorded as data;
  2. decidable claims carry falsifiers into the EXISTING `reverify_falsifier`
     and fix-efficacy path;
  3. non-decidable claims are ROUTED (HIL / [VERIFY:current]), NEVER DISCARDED
     -- the one-character near-miss of March 2026 is the standing warning;
  4. file-level admissibility becomes an AGGREGATE over the ledger.

`compute_sk` IS UNTOUCHED. It stays veto-only on fenced listings and `NO_SCORE`
keeps the meaning `docs/GLOSSARY.md:237` gives it -- "S_k has no opinion" --
and stops being read as document admissibility. This module reads the registry
and writes a report section; it moves no verdict and re-scores nothing.

INFORMATIVE ONLY IN v1, WHICH IS THE SEAT'S OWN RECOMMENDATION AND NOT A
DEFERRAL. fable: "whether claim-level verdicts may enter sigma/S_k (and hence
R_k) ... NOT in v1 -- the ledger is `informative_only` like
`target_complexity`, promoted only after a commissioning run measures its error
rate against the corpus's known ground truth." That is `feedback_shadow_not_deferred`
exactly: the channel is ON and populated now, and promotion needs evidence.

WHAT v1 DOES NOT CLOSE, STATED RATHER THAN GLOSSED. fable's own strongest
self-refutation: the design "assumes a model's REASON stage surfaces material
UNSTATED claims at a useful rate. Nothing offline can test that." v1 populates
the ledger from claims the seats DID state -- every registered finding is a
claim about the target -- so it makes the claim the unit of record and the unit
of aggregation. It does NOT manufacture claims for a document no finding names.
What would test that is the corpus extension fable specified: a planted defect
that is an unstated consequence of two individually-true stated values, run
blind through a panel. Until that exists this channel is justified by the
founder's principle and by one internal near-miss, not by measurement.
"""
from __future__ import annotations

import dataclasses
from typing import Any, Dict, Iterable, List, Optional

#: The verdict vocabulary is the falsifier path's own, NOT a new taxonomy.
#: fable: "verdict minted by `reverify_falsifier` (CONFIRMED / REFUTED / ERROR /
#: UNTOOLABLE) -- the same five-way vocabulary findings already use, including
#: INTEGRITY_VIOLATION. No new verdict taxonomy." A second taxonomy would be a
#: second description of the same thing, free to drift from the first.
CLAIM_VERDICTS = ("CONFIRMED", "REFUTED", "ERROR", "UNTOOLABLE",
                  "INTEGRITY_VIOLATION")

#: A claim with no verdict yet. Distinct from ERROR, which is a verdict that
#: the instrument could not look -- the distinction `bench/fix_efficacy.py`
#: says in its own comment the project keeps having to relearn.
UNVERIFIED = "UNVERIFIED"

#: The 3 file-level states, and they are deliberately 3 rather than 2.
#: fable, Q2: an aggregate "three-valued and honest about which state it is in".
CLAIM_ADDRESSABLE = "claim-addressable"
ROUTED_ONLY = "routed-only"
NO_DECIDABLE_CLAIMS = "no-decidable-claims"

AGGREGATE_STATES = (CLAIM_ADDRESSABLE, ROUTED_ONLY, NO_DECIDABLE_CLAIMS)

#: What each state means, carried inline for the reason `status_meaning` is:
#: one exported record must be readable without a second file.
AGGREGATE_MEANINGS = {
    CLAIM_ADDRESSABLE: (
        "At least 1 claim in this target is decidable by computation, so the "
        "harness can form an opinion about its content."),
    ROUTED_ONLY: (
        "Claims exist and none is decidable by computation. They are routed to "
        "a human or to [VERIFY:current] -- NOT discarded, and NOT a statement "
        "that the target is non-computable."),
    NO_DECIDABLE_CLAIMS: (
        "No claims were produced for this target at all. This is the only "
        "state that corresponds to the founder's 'genuinely non-computable', "
        "and it attaches to the ABSENCE OF CLAIMS rather than to the absence "
        "of fenced code."),
}

#: Where a claim goes when computation cannot decide it. Routing is recorded so
#: that "nothing decided this" and "a human was asked" are distinguishable.
ROUTE_HIL = "HIL"
ROUTE_VERIFY_CURRENT = "VERIFY:current"

#: HOW THE ROUTE WAS OBTAINED, WHICH IS NOT THE SAME QUESTION AS THE ROUTE.
#:
#: FREE PANEL, 2026-10-01. This module's own docstring promises "Routing is
#: recorded so that 'nothing decided this' and 'a human was asked' are
#: distinguishable". It was not delivering that. `claim_from_entry` INFERRED the
#: route from `finding_category` -- `state` to [VERIFY:current], everything else
#: to HIL -- and never read the escalation the runner actually recorded. The
#: comment beside it cites `hil_escalated` as "the runner's own signal that it
#: did", and that field is written only by `bench/reference_runner.py`; v3
#: entries carry `escalated` instead, and the ledger read neither.
#:
#: MEASURED over every archived run: of 2059 routed (no-falsifier) claims, 2002
#: were labelled HIL while the entry's own `escalated` was False -- 97.2317%,
#: Wilson 95% [96.4303%, 97.8571%]. So the report said "2002 claims are with a
#: human" about claims no human was asked about. For the one channel whose
#: purpose is that claims are never silently dropped, a reassuring state it did
#: not measure is the worst available failure.
#:
#: STRICTLY ADDITIVE. The route itself is UNCHANGED, so every existing caller
#: and every existing assertion sees what it saw before. What is added is the
#: PROVENANCE of the route, which makes the inference visible instead of
#: indistinguishable from a recorded escalation. Whether the inferred default
#: should remain HIL at all is a question for the human, not for this module:
#: `bench/tests/test_claim_ledger_2026-10-01.py` asserts the HIL default twice,
#: and quietly editing an oracle to suit a fix is not a fix.
ROUTE_RECORDED = "recorded"
ROUTE_INFERRED = "inferred"
ROUTE_SOURCES = (ROUTE_RECORDED, ROUTE_INFERRED)

#: The fields that actually carry an escalation, across BOTH runners.
_ESCALATION_FIELDS = ("hil_escalated", "escalated")


@dataclasses.dataclass
class Claim:
    """One claim about one target, with the evidence that decided it.

    SHAPED ON THE CORPUS'S OWN `Claim`, per fable: "same shape as the corpus's
    `Claim` dataclass, which already exists". `anchor` is the located text, not
    the statement -- a claim whose anchor cannot be found in the target is a
    claim about a different document, and on 2026-09-30 an accessor reading
    `.text` instead of `.anchor` left 29 of 29 claims unlocated.
    """

    tag: str                                  # stable id, e.g. a canonical_id
    statement: str                            # what is claimed
    anchor: str = ""                          # where it is claimed, verbatim
    kind: str = ""                            # arithmetic / derivation / state
    decidable: bool = False                   # can computation settle it?
    falsifier: str = ""                       # the check, when there is one
    verdict: str = UNVERIFIED
    routed_to: str = ""                       # ROUTE_HIL / ROUTE_VERIFY_CURRENT
    tools: List[str] = dataclasses.field(default_factory=list)
    source: str = ""                          # which seat stated it
    severity: Optional[float] = None
    #: ROUTE_RECORDED when the entry itself carried an escalation, otherwise
    #: ROUTE_INFERRED. Empty for a decidable claim, which has no route.
    route_source: str = ""

    def __post_init__(self) -> None:
        if self.verdict not in CLAIM_VERDICTS and self.verdict != UNVERIFIED:
            raise ValueError(
                f"{self.verdict!r} is not a claim verdict. The vocabulary is "
                f"the falsifier path's own: {CLAIM_VERDICTS} or {UNVERIFIED}. "
                f"A new verdict name is a second taxonomy, which is how 2 "
                f"descriptions of one thing start to disagree.")
        # A claim that computation cannot settle MUST say where it went. The
        # March 2026 near-miss was a routed claim becoming a discarded one.
        if not self.decidable and not self.routed_to:
            self.routed_to = ROUTE_HIL

    def as_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


#: ★ THE CLAIM CHANNEL'S ENTRY INTO R_k, ON HIS RULING OF 2026-10-29.
#:
#: HIS RULING, annotation 8 of `Responses/Decisions_Awaiting_You_2026-10-29.txt`:
#: *"I accept your recommendation. fr"*, against the recommendation that the
#: informative-only channel's verdict should enter *"As a multiplier on R sub k,
#: by analogy with the ruling you already gave for the verification fact in
#: section 7.7"*. His earlier instruction of 2026-10-02 asked which of sigma,
#: S_k or R_k it should enter and whether as a multiplier or an addition; the
#: term and the form are now both decided.
#:
#: WHY A WEIGHT DEFAULTING TO 0 RATHER THAN A BOOLEAN. Section 7.7's own
#: precedent, `effective_severity`, is gated by `_SEVERITY_SPEC["on"]` so the
#: default path is byte-identical. The same discipline applies here for a reason
#: this module already states in its own header: fable's recommendation was that
#: promotion out of `informative_only` waits on *"a commissioning run [that]
#: measures its error rate against the corpus's known ground truth"*, and that
#: run does not exist. So the channel is ON and REPORTED now and inert in the
#: arithmetic until the evidence justifies a non-zero weight -- which is
#: `feedback_shadow_not_deferred` rather than a deferral.
CLAIM_CHANNEL_WEIGHT = 0.0

#: THE CEILING, AND WHY IT IS NOT 1. At weight 1 with full coverage the factor
#: is exactly 0 and residual risk is annihilated -- z3 confirms it, and it is a
#: far stronger claim than claim coverage can support: that every claim about a
#: target was tool-decided does not establish that no fault remains. At 1/2 the
#: proved floor is `R_k * C >= R_k / 2`, so the channel can at most halve
#: residual risk and can never reach 0 from a positive R_k (z3: unsat).
CLAIM_CHANNEL_MAX_WEIGHT = 0.5


def claim_channel_coverage(report: Dict[str, Any]) -> float:
    """What share of a target's claims a TOOL actually decided and CONFIRMED.

    Read from the ledger's own report so there is 1 definition of the numerator
    and the denominator, not a second copy here. 0.0 for an empty ledger, which
    makes the factor exactly 1 and the channel inert -- the honest reading of
    "nothing was verified", not of "nothing is wrong".
    """
    total = int(report.get("claims_total") or 0)
    if total <= 0:
        return 0.0
    confirmed = int((report.get("by_verdict") or {}).get("CONFIRMED") or 0)
    return max(0.0, min(1.0, confirmed / total))


def claim_channel_factor(report: Dict[str, Any],
                         weight: Optional[float] = None) -> float:
    """The multiplier the claim channel contributes to R_k: ``1 - weight * coverage``.

    DIRECTION, STATED BECAUSE IT IS THE OPPOSITE OF SECTION 7.7's. There `V`
    multiplies SEVERITY and `V(REFUTED) = 0` annihilates it, because a disproved
    finding carries no weight. Here the multiplicand is RESIDUAL RISK, so the
    factor may only ever REDUCE it, and only in proportion to how much of the
    target's claim set a tool actually confirmed. A REFUTED claim contributes
    NOTHING to coverage and therefore no reduction -- it does not inflate R_k
    either, because the fault it reveals is already a finding carried by the
    detection term, and adding it here would count it twice.

    PROVED, by SymPy and independently by z3, over the box
    ``weight in [0, 1/2], coverage in [0, 1], R_k in [0, 1]``:
    the factor lies in [1/2, 1]; the product lies in [0, 1]; the product can
    never EXCEED R_k (z3: unsat), so the channel cannot manufacture risk; a
    weight of 0 and a coverage of 0 each leave R_k exactly unchanged; and a
    positive R_k cannot be driven to exactly 0 (z3: unsat). Producer:
    `scripts/the_claim_channel_enters_r_k_2026-10-29.py`.
    """
    w = CLAIM_CHANNEL_WEIGHT if weight is None else float(weight)
    if not (0.0 <= w <= CLAIM_CHANNEL_MAX_WEIGHT):
        raise ValueError(
            f"claim-channel weight {w} must lie in "
            f"[0, {CLAIM_CHANNEL_MAX_WEIGHT}]. The ceiling is not 1 because at "
            f"1 with full coverage the factor is 0 and residual risk is "
            f"annihilated, which claim coverage cannot establish.")
    return 1.0 - w * claim_channel_coverage(report)


def apply_claim_channel(r_k: float, report: Dict[str, Any],
                        weight: Optional[float] = None) -> float:
    """Apply the channel to an already-computed R_k. Clamped to [0, 1].

    SEPARATE FROM `compute_rk` ON PURPOSE. `compute_rk` is the 3-phase update and
    is reached by every runner and every archived recomputation check; wrapping
    it would put a new term inside a function whose arithmetic is pinned by the
    deterministic-recomputation validator. This composes AFTER it, exactly as
    `compute_rk_with_eta_channel` composes BEFORE it, so each channel has 1
    named entry point and the core update is untouched.
    """
    base = max(0.0, min(1.0, float(r_k)))
    return max(0.0, min(1.0, base * claim_channel_factor(report, weight)))


class ClaimLedger:
    """Every claim about one target, and the file-level aggregate over them.

    It decides nothing about admissibility by itself -- `aggregate()` reports a
    state, and `informative_only` records that the state is not wired into
    sigma, S_k or R_k in v1.

    ★ IT IS STILL TRUE, AND `apply_claim_channel` DOES NOT CHANGE THAT, recorded
    here 2026-10-30 because a reader should learn it from this module rather than
    from a report about it. `apply_claim_channel` was built 2026-10-29 and has NO
    caller in the harness: its only caller outside this module is its own producer,
    `scripts/the_claim_channel_enters_r_k_2026-10-29.py`. The live computation is
    `R_k = R_base * (1 - nu_eff) + nu_eff` at `bench/reference_runner_v3.py:15774`
    and `:15848`, and neither reaches it. So the PATHWAY exists and is unreached,
    which is the addition-that-does-nothing shape the additive standard names 11
    prior instances of.

    WHY IT IS NOT WIRED TONIGHT, having been described as a 1-line change and not
    being one. Both `R_k` sites are pure arithmetic over `sk`, `R_det`, `R_old`,
    `nu_b` and `nu_f`; neither has access to a ledger, and `apply_claim_channel`
    needs this ledger's COVERAGE. Wiring therefore means threading a new input
    through the scoring functions and their callers, which is a design change and
    not plumbing.

    AND WHY THIS FLAG IS NOT DERIVED FROM THE WEIGHT, which was proposed and is
    refused. `CLAIM_CHANNEL_WEIGHT == 0.0` would read as the same fact and is not:
    this flag records WIRING. A weight raised above 0 while the wiring still did
    not exist would make a weight-derived flag report False and so claim the
    channel was in use when nothing calls it -- strictly less honest than the
    hand-set constant it would replace.
    """

    informative_only = True

    def __init__(self, target: str = "") -> None:
        self.target = target
        self.claims: List[Claim] = []

    def add(self, claim: Claim) -> Claim:
        self.claims.append(claim)
        return claim

    def extend(self, claims: Iterable[Claim]) -> None:
        for c in claims:
            self.add(c)

    # ── the aggregate ──────────────────────────────────────────────────────
    def decidable(self) -> List[Claim]:
        return [c for c in self.claims if c.decidable]

    def routed(self) -> List[Claim]:
        return [c for c in self.claims if not c.decidable]

    def decided(self) -> List[Claim]:
        """Claims a tool actually reached a verdict on."""
        return [c for c in self.claims
                if c.decidable and c.verdict in ("CONFIRMED", "REFUTED")]

    def aggregate(self) -> str:
        """The file-level state. 3-valued, never a gate in front of the claims."""
        if not self.claims:
            return NO_DECIDABLE_CLAIMS
        if self.decidable():
            return CLAIM_ADDRESSABLE
        return ROUTED_ONLY

    def discarded(self) -> List[Claim]:
        """Claims that are neither decidable nor routed: must always be empty.

        Kept as a QUERY rather than an assertion so a caller can report it.
        `Claim.__post_init__` routes an undecidable claim to HIL by
        construction, so a non-empty result here means something built a Claim
        by another path and dropped it.
        """
        return [c for c in self.claims if not c.decidable and not c.routed_to]

    def report(self) -> Dict[str, Any]:
        """The section a run's report carries. Counts, states, and the claims."""
        state = self.aggregate()
        rep = {
            "target": self.target,
            "informative_only": self.informative_only,
            "aggregate": state,
            "aggregate_meaning": AGGREGATE_MEANINGS[state],
            "claims_total": len(self.claims),
            "decidable": len(self.decidable()),
            "routed": len(self.routed()),
            "decided": len(self.decided()),
            "discarded": len(self.discarded()),
            # ★ THE CHANNEL'S CONTRIBUTION, REPORTED WHETHER OR NOT IT IS
            # WEIGHTED. His ruling of 2026-10-29 fixed the term (R_k) and the
            # form (a multiplier); fable's condition for a NON-ZERO weight is a
            # commissioning run that does not yet exist. Reporting the factor at
            # the live weight AND at the ceiling is what makes the promotion
            # decision measurable instead of argued: a reader sees what the
            # channel would do before anything turns it on.
            "claim_channel_weight": CLAIM_CHANNEL_WEIGHT,
            "claim_channel_coverage": None,   # filled below; needs by_verdict
            "claim_channel_factor": None,
            "claim_channel_factor_at_ceiling": None,
            "by_verdict": {v: sum(1 for c in self.claims if c.verdict == v)
                           for v in (UNVERIFIED, *CLAIM_VERDICTS)},
            "by_route": {r: sum(1 for c in self.routed() if c.routed_to == r)
                         for r in (ROUTE_HIL, ROUTE_VERIFY_CURRENT)},
            # THE ROUTE AND ITS PROVENANCE ARE 2 FACTS, AND THE REPORT CARRIED
            # ONLY THE FIRST. `routes_inferred` is how many of the routed
            # claims this module ASSUMED a destination for because the entry
            # recorded none. A reader of `by_route` alone cannot tell the
            # difference, and 97.2317% of the archive's routed claims are of
            # the assumed kind.
            "by_route_source": {
                k: sum(1 for c in self.routed() if c.route_source == k)
                for k in ROUTE_SOURCES},
            "routes_inferred": sum(1 for c in self.routed()
                                   if c.route_source == ROUTE_INFERRED),
            "claims": [c.as_dict() for c in self.claims],
            # SAID IN THE ARTEFACT, not only in this module's docstring, so a
            # reader of a report knows what the channel does not yet cover.
            "not_covered": (
                "v1 records claims the seats STATED. It does not manufacture "
                "claims for a target no finding names, so it does not test "
                "whether a REASON stage surfaces material UNSTATED claims. "
                "That needs the corpus extension specified in "
                "experimental_notes/fable_intelligence_first_2026-09-30.md Q1."),
        }
        #: FILLED AFTER THE DICT because the factor is computed FROM the report's
        #: own counts -- 1 definition of the numerator and the denominator, not a
        #: second copy. `claim_channel_coverage` reads `claims_total` and
        #: `by_verdict`, so it cannot disagree with the numbers printed beside it.
        rep["claim_channel_coverage"] = claim_channel_coverage(rep)
        rep["claim_channel_factor"] = claim_channel_factor(rep)
        rep["claim_channel_factor_at_ceiling"] = claim_channel_factor(
            rep, weight=CLAIM_CHANNEL_MAX_WEIGHT)
        return rep


# ═════════════════════════════════════════════════════════════════════════════
# POPULATION FROM WHAT ALREADY EXISTS
#
# Every registered finding IS a claim about the target: a statement, with an
# originating seat, and either a runnable falsifier or none. So v1 needs no new
# collection apparatus and no brief change to produce a populated ledger on the
# next simulated run -- which is what the founder asked for.
#
# DECIDABLE MEANS A FALSIFIER EXISTS, not that one fired. A finding carrying
# `falsifier_code` is a claim computation can settle; one without is routed. The
# runner's own severity rule already says a critical without a falsifier is a
# defect, and `scripts/escalation_paths_2026-09-11.py` counts them -- so this
# reading is the project's existing one, not a new convention.
_DECIDED = {"CONFIRMED", "REFUTED", "ERROR", "UNTOOLABLE",
            "INTEGRITY_VIOLATION"}


def claim_from_entry(cid: str, entry: Dict[str, Any]) -> Claim:
    """One registry entry, read as the claim it already is."""
    falsifier = (entry.get("falsifier_code") or "").strip()
    verdict = (entry.get("falsifier_verdict") or "").strip().upper()
    sev = entry.get("severity")
    try:
        sev = float(sev) if sev is not None else None
    except (TypeError, ValueError):
        sev = None
    return Claim(
        tag=cid or entry.get("canonical_id", ""),
        statement=(entry.get("description") or "")[:2000],
        anchor=(entry.get("source_ref") or "")[:500],
        kind=entry.get("finding_category") or "",
        decidable=bool(falsifier),
        falsifier=falsifier[:4000],
        verdict=verdict if verdict in _DECIDED else UNVERIFIED,
        # A claim with no falsifier is routed, and WHICH route matters: a claim
        # about present-day state goes to [VERIFY:current], everything else to
        # a human. `hil_escalated` is the runner's own signal that it did.
        routed_to=("" if falsifier else
                   (ROUTE_VERIFY_CURRENT
                    if (entry.get("finding_category") or "") == "state"
                    else ROUTE_HIL)),
        route_source=("" if falsifier else
                      (ROUTE_RECORDED
                       if any(entry.get(f) for f in _ESCALATION_FIELDS)
                       else ROUTE_INFERRED)),
        source=entry.get("source_model") or "",
        severity=sev,
    )


def ledger_from_registry(registry: Any, target: str = "") -> ClaimLedger:
    """Build a populated ledger from a run's registry. Reads, never writes."""
    entries = getattr(registry, "entries", registry)
    if isinstance(entries, dict):
        items = sorted(entries.items())
    else:
        items = [(e.get("canonical_id", ""), e) for e in (entries or [])]
    led = ClaimLedger(target=target)
    for cid, entry in items:
        if isinstance(entry, dict):
            led.add(claim_from_entry(cid, entry))
    return led


def main(argv: Optional[List[str]] = None) -> int:
    """Report the ledger over an archived run, so the channel is inspectable."""
    import argparse
    import json
    import pathlib

    ap = argparse.ArgumentParser(description=(__doc__ or "").split("\n")[0])
    ap.add_argument("runner_state", nargs="?", default=None,
                    help="path to a run's runner_state.json")
    args = ap.parse_args(argv)
    if not args.runner_state:
        ap.error("a runner_state.json path is required")
    doc = json.loads(pathlib.Path(args.runner_state).read_text(encoding="utf-8"))
    reg = (doc.get("registry") or {}).get("entries") or {}
    led = ledger_from_registry(reg, target=args.runner_state)
    rep = led.report()
    print(f"CLAIM LEDGER for {pathlib.Path(args.runner_state).parent.name}")
    print(f"  aggregate      : {rep['aggregate']}")
    print(f"  meaning        : {rep['aggregate_meaning']}")
    print(f"  claims total   : {rep['claims_total']}")
    print(f"    decidable    : {rep['decidable']}")
    print(f"    routed       : {rep['routed']}   {rep['by_route']}")
    print(f"    decided      : {rep['decided']}")
    print(f"    DISCARDED    : {rep['discarded']}   (must be 0)")
    print(f"  by verdict     : {rep['by_verdict']}")
    print(f"  informative_only: {rep['informative_only']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
