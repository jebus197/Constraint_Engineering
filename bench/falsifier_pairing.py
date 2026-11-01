#!/usr/bin/env python3
"""The primary/secondary falsifier rule, as code rather than prose.

FOUNDER, 2026-10-31, settling the shape: *"Isn't a better rule to use an
equivalent secondary falsifier/tool when such tools are available, and if not
to default exclusively to using the primary only?"* and, qualifying it in the
same message, that primary-only also applies when a secondary *"cannot be
installed from the curated list"*.

THE RULE IS NOT NEW, AND SAYING SO MATTERS, because it has been in force for
44 days without a mechanism. His ruling of 2026-09-28: *"Wolfram (when
available) however should remain the secondary falsifier ran against any output
produced from the installed Open Source tools and should never be considered the
primary falsifier route."* And on unavailability, 2026-09-17: *"The only
exception is when a tool may be literally physically unavailable to a
model/agent, in which case it should also fall back exclusively to the Open
Source tools it does have access to."* Today's message generalises both from
Wolfram to every tool. This module is the first thing that enforces either.

WHAT WAS MEASURED BEFORE THIS WAS WRITTEN
(producer: `scripts/the_secondary_falsifier_rule_2026-10-31.py`, exit 0, every
figure cross-verified on 2 tools):

  * `bench/immune_agents.py` ends its specialist loop with
    `break  # First definitive result wins`, so the B-Cell dispatch is
    SINGLE-TOOL BY CONSTRUCTION. No secondary falsifier existed in that path.
  * All 5 claim types carry 2 or more dispatchable tools (Wilson 95%
    [0.565518, 1.000000]), so the `break` discarded a candidate secondary
    every single time it fired.
  * `statsmodels` and `scipy` BOTH resolve to the identical verifier
    `_verify_statistical`. The canonical 2-tool pair for a statistical claim
    was literally 1 function called twice -- which is why independence, and
    not mere count, is the property the rule has to test.
  * `install_check` and `package_hint` were carried by 19 of 21 entries and
    read by 0 lines of live code. This module is their first consumer, so the
    curated list stops being data nothing reaches.
  * `deepseek_formal` reaches a PAID API and sits at position 12 of 12 in the
    `mathematical` dispatch order and 5 of 5 in `logical`. A selector that
    reached for "the next available tool" would therefore have been able to
    trigger paid dispatch, against the founder's standing constraint that no
    paid dispatch happens without his express authorisation. It is excluded
    by class, not ranked last.

WHY INDEPENDENCE AND NOT COUNT. Every same-formulation cross-check run on
2026-10-31 agreed to machine precision and caught nothing: statsmodels against
mpmath on Wilson intervals, scipy against mpmath on Fisher, NumPy against SymPy
on a cost quadratic, z3 against exhaustive enumeration on a polarity table.
Every error actually caught came from a different ROUTE to the quantity: a
SymPy model against the executing function, a fitted curve against committed
live-priced anchors, a sidecar census against the API's own field. Independent
route caught 3 of 3, same route 0 of 4, Fisher exact one-sided p = 0.028571.
**THAT IS WEAK EVIDENCE AND IS LABELLED AS SUCH**: n = 7, the classification is
post-hoc, and the sample is the cross-checks one session happened to record,
with the selection risk running in the direction that flatters the conclusion.
It is consistent with the rule; it does not test it. A real test needs a
pre-registered classification over the archive.

THE RULE, STATED SO IT CAN FAIL:
  1. A claim gets a PRIMARY tool -- the first dispatchable tool for its claim
     type, which is what the harness already did.
  2. A SECONDARY is consulted only if a candidate exists that is INDEPENDENT
     of the primary: a different `independence_class` AND not the same verifier
     function.
  3. A paid route is never selected as a secondary unless the caller passes
     `allow_paid=True`, which only the founder's authorisation justifies.
  4. An independent candidate that is not installed is NOT silently skipped:
     it is reported with its `package_hint`, so the curated list can be acted
     on rather than guessed at.
  5. Where no secondary survives 2 to 4, the primary stands ALONE and the
     record SAYS SO. "Say so" is the operative half -- an unmarked single-tool
     verdict is indistinguishable from a corroborated one.

WHAT THIS MODULE DELIBERATELY DOES NOT DO. It never overrides the primary's
verdict. A disagreeing secondary is recorded as a disagreement, loudly, and the
verdict is left as the primary gave it. Changing a verdict is a behavioural
change to a live experimental apparatus mid-arc and is the founder's call, not
a side effect of wiring a rule.
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Optional, Tuple

#: The 6 routes a tool can take to an answer. Documented in full in the header
#: of `bench/cdsfl_registry/tool_manifest.toml`, which is the source of truth.
INDEPENDENCE_CLASSES = frozenset({
    "symbolic", "numeric", "search", "artefact", "execute", "reference", "model",
})

#: A route whose cost is money rather than CPU. Never auto-selected.
PAID_CLASSES = frozenset({"model"})

# Outcome codes. These reach the archived record, so they are stable strings
# rather than enum members -- a code that changes spelling breaks every past
# report that carries it.
SELECTED = "SELECTED"
NO_CANDIDATES = "NO_CANDIDATES"
NO_INDEPENDENT_CANDIDATE = "NO_INDEPENDENT_CANDIDATE"
INDEPENDENT_CANDIDATE_IS_PAID = "INDEPENDENT_CANDIDATE_IS_PAID"
INDEPENDENT_CANDIDATE_NOT_INSTALLED = "INDEPENDENT_CANDIDATE_NOT_INSTALLED"

PRIMARY_ONLY_REASONS = frozenset({
    NO_CANDIDATES, NO_INDEPENDENT_CANDIDATE,
    INDEPENDENT_CANDIDATE_IS_PAID, INDEPENDENT_CANDIDATE_NOT_INSTALLED,
})


def independence_class(tool: str, manifest: Dict[str, Dict[str, Any]]) -> str:
    """The declared route of `tool`, or `""` when the manifest omits it.

    An omission is returned as empty rather than defaulted, because defaulting
    would silently make an unclassified tool independent of everything.
    """
    return (manifest.get(tool) or {}).get("independence_class") or ""


def is_paid_route(tool: str, manifest: Dict[str, Dict[str, Any]]) -> bool:
    return independence_class(tool, manifest) in PAID_CLASSES


def shares_verifier(a: str, b: str, manifest: Dict[str, Dict[str, Any]]) -> bool:
    """True when 2 manifest entries name the SAME verifier function.

    This is the zero-judgement half of independence and it is checked first:
    `statsmodels` and `scipy` both name `_verify_statistical`, so one cannot
    corroborate the other no matter what any class field says.
    """
    va = (manifest.get(a) or {}).get("verifier")
    vb = (manifest.get(b) or {}).get("verifier")
    return bool(va) and va == vb


def is_independent(primary: str, candidate: str,
                   manifest: Dict[str, Dict[str, Any]]) -> bool:
    """True when `candidate` takes a different route to the answer than `primary`.

    Both conditions are required, and an unclassified tool on either side is
    NOT independent -- the conservative reading, which costs a corroboration
    rather than inventing one.
    """
    if candidate == primary:
        return False
    if shares_verifier(primary, candidate, manifest):
        return False
    cp = independence_class(primary, manifest)
    cc = independence_class(candidate, manifest)
    if not cp or not cc:
        return False
    return cp != cc


def probe_available(tool: str, manifest: Dict[str, Dict[str, Any]],
                    cache: Optional[Dict[str, bool]] = None) -> bool:
    """Run the manifest's own `install_check` for `tool`.

    THIS IS THE FIRST CONSUMER OF `install_check` IN THE PROJECT. The field has
    existed on 19 of 21 entries, describing itself as "Python expression that
    returns truthy when the tool is installed", and was read by 0 lines of live
    code until this function.

    A tool with no `install_check` is reported AVAILABLE, because every such
    entry in the manifest is a delegated one whose owning cell decides its own
    availability -- not because absence of a check implies presence of a tool.
    """
    if cache is not None and tool in cache:
        return cache[tool]
    chk = (manifest.get(tool) or {}).get("install_check")
    if not chk:
        ok = True
    else:
        try:
            exec(compile(chk, f"<install_check:{tool}>", "exec"), {})  # noqa: S102
            ok = True
        except Exception:  # noqa: BLE001 -- any failure means "not usable here"
            ok = False
    if cache is not None:
        cache[tool] = ok
    return ok


def package_hint(tool: str, manifest: Dict[str, Dict[str, Any]]) -> str:
    """The PEP 508 hint for installing `tool` from the curated list.

    Second consumer of a field that had none. This is what makes the founder's
    "cannot be installed from the curated list" branch actionable instead of
    merely true: the record names what to install.
    """
    return (manifest.get(tool) or {}).get("package_hint") or ""


def select_secondary(
    primary: str,
    candidates: Iterable[str],
    manifest: Dict[str, Dict[str, Any]],
    *,
    allow_paid: bool = False,
    available: Optional[Callable[[str], bool]] = None,
    cache: Optional[Dict[str, bool]] = None,
) -> Tuple[Optional[str], str, str]:
    """Pick an independent secondary falsifier for `primary`, or explain why not.

    Returns `(tool_or_None, reason, detail)`. `reason` is one of the outcome
    codes above; every code other than `SELECTED` is in
    `PRIMARY_ONLY_REASONS` and means the primary stands alone.

    `available` is injectable so a test can state the availability of a tool
    without installing or uninstalling anything on the founder's machine.
    """
    avail = available or (lambda t: probe_available(t, manifest, cache))

    # A delegated tool is owned by another cell and is never run by this
    # dispatch, so it cannot corroborate anything. Excluded before the
    # independence test, not after, or it would consume the secondary slot.
    candidates = [c for c in candidates if not is_delegated(c, manifest)]
    independent = [c for c in candidates if is_independent(primary, c, manifest)]
    if not independent:
        considered = [c for c in candidates if c != primary]
        if not considered:
            return None, NO_CANDIDATES, f"no tool other than {primary}"
        shown = ", ".join(
            f"{c}({independence_class(c, manifest) or 'unclassified'})"
            for c in considered)
        return (None, NO_INDEPENDENT_CANDIDATE,
                f"{primary}({independence_class(primary, manifest)}) vs {shown}")

    # Unpaid first, in dispatch order, so a paid route is never preferred over
    # a free one that would do.
    unpaid = [c for c in independent if not is_paid_route(c, manifest)]
    pool = unpaid or ([] if not allow_paid else independent)

    if not pool:
        paid_names = ", ".join(independent)
        return (None, INDEPENDENT_CANDIDATE_IS_PAID,
                f"only independent candidate(s) {paid_names} reach a paid API; "
                f"the founder's authorisation is required, so primary only")

    not_installed = []
    for c in pool:
        if avail(c):
            cls = independence_class(c, manifest)
            return (c, SELECTED,
                    f"{primary}({independence_class(primary, manifest)}) "
                    f"corroborated by {c}({cls})")
        not_installed.append(c)

    hints = ", ".join(
        f"{c} [{package_hint(c, manifest) or 'no package_hint'}]"
        for c in not_installed)
    return (None, INDEPENDENT_CANDIDATE_NOT_INSTALLED,
            f"independent candidate(s) present in the curated list but not "
            f"installed: {hints}")


def is_delegated(tool: str, manifest: Dict[str, Dict[str, Any]]) -> bool:
    """True when another cell owns `tool`, so this dispatch never runs it.

    FOUND BY MEASUREMENT, 2026-10-31, and it was a defect in the first version
    of this module. `_specialist_b_cell_dispatch` skips a delegated entry
    inside its own invocation helper, so `ast_analysis` (B-Cell v2) and
    `test_runner` (CT cell) are NOT dispatchable here even though 3 domain
    TOMLs list them first. Without this filter the module reported
    `ast_analysis` as the primary for `code/code_structural` -- a tool that
    never runs -- and picked `test_runner` as a secondary for
    `code/code_behavioral`, spending the one secondary slot on a call that
    could only ever return nothing.
    """
    return bool((manifest.get(tool) or {}).get("delegate"))


def is_secondary_only(tool: str, manifest: Dict[str, Dict[str, Any]]) -> bool:
    """True when the manifest forbids `tool` from being a PRIMARY falsifier.

    Implements the founder's ruling of 2026-09-28 for Wolfram, generalised to
    any tool the manifest so marks. Without this, appending Wolfram to a claim
    type would have made it reachable at position 13 of the `mathematical`
    dispatch order -- a primary route whenever the 12 tools before it returned
    UNCERTAIN, which is precisely what the ruling forbids.
    """
    return bool((manifest.get(tool) or {}).get("secondary_only"))


def primary_candidates(candidates: Iterable[str],
                       manifest: Dict[str, Dict[str, Any]]) -> list:
    """`candidates` with the secondary-only tools removed, order preserved.

    Order is preserved because the dispatch's order is load-bearing: the loop
    in `bench/immune_agents.py` ends at the first definitive verdict, so
    position 1 is the primary. Reordering here would silently change which
    tool decides every claim.
    """
    return [c for c in candidates
            if not is_secondary_only(c, manifest)
            and not is_delegated(c, manifest)]


def pairing_note(primary: str, secondary: Optional[str], reason: str,
                 detail: str, agrees: Optional[bool] = None) -> str:
    """One audit line for the verdict record.

    The marking is the operative half of the rule: an unmarked single-tool
    verdict reads exactly like a corroborated one, which is the failure the
    rule exists to prevent.
    """
    if secondary is None:
        return f"[falsifier:primary-only {primary} reason={reason} ({detail})]"
    if agrees is None:
        return f"[falsifier:secondary {secondary} agreement=NOT_RUN ({detail})]"
    verdict = "AGREES" if agrees else "DISAGREES"
    return f"[falsifier:secondary {secondary} agreement={verdict} ({detail})]"
