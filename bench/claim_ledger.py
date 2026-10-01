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


class ClaimLedger:
    """Every claim about one target, and the file-level aggregate over them.

    It decides nothing about admissibility by itself -- `aggregate()` reports a
    state, and `informative_only` records that the state is not wired into
    sigma, S_k or R_k in v1.
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
        return {
            "target": self.target,
            "informative_only": self.informative_only,
            "aggregate": state,
            "aggregate_meaning": AGGREGATE_MEANINGS[state],
            "claims_total": len(self.claims),
            "decidable": len(self.decidable()),
            "routed": len(self.routed()),
            "decided": len(self.decided()),
            "discarded": len(self.discarded()),
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
