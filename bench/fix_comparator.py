#!/usr/bin/env python3
"""Compare candidate fixes against the 3 formal standards. REFUSES more than it ranks.

HIS SPECIFICATION, 2026-10-17, quoted because it is the design: the classifier
aspect of the bound orchestrator becomes *"doubly useful"* once fixes fold back at
the close, because something must then decide *"which fixes are 'better' than
others, which compose and which don't and which meet our formal simplest
sufficient fix, additive and composability standards"*. And on what it is NOT:
*"not 'model voting'... more akin to the simple classifier work already done by
Haiku"*.

SO IT MUST BE DETERMINISTIC, and every verdict below is a function of the fix
text and the committed capability snapshot. No model is consulted and no
judgement is scored. `Findings confirmed programmatically or by HIL -- no model
voting` is a standing correction, and a comparator that asked a model which fix
was better would breach it in the one place it matters most.

★ THE CENTRAL DESIGN DECISION, AND IT IS A REFUSAL RATHER THAN A FEATURE.
This module does NOT score fixes on a rubric. It was tempting to give each
candidate a number per standard and sort, and that is precisely the move the
founder caught in 2026-05 when CC1 proposed replacing the model-derived severity
with a rubric: a rubric launders a judgement as a measurement. The archive-wide
lesson is recorded in `additive-standard` and the correction of 2026-10-28.

So each standard is handled according to what can actually be DECIDED:

  ADDITIVE          -> MECHANICALLY DECIDABLE. A fix that deletes a capability
                       name without a RETIRED entry breaches the standard. The
                       capability set and the RETIRED set already exist and are
                       already enforced by
                       `bench/tests/test_additive_standard_2026-09-07.py`.

  SIMPLEST SUFFICIENT -> NOT DECIDABLE HERE, and saying so is the honest output.
                       "Smallest change addressing the root cause AND the
                       downstream consequences traced in FOLLOW" needs the root
                       cause, which is not in the fix text. Lines changed is a
                       PROXY, and a proxy chosen without measuring its
                       alternatives is this project's single most recorded error
                       class. So the extent is REPORTED as an input to a human
                       or programmatic decision, never as a ranking.

  COMPOSABILITY     -> REFUSED WITHOUT A MEASUREMENT, which is his definition
                       and not a conservative reading of it. Verbatim, 2026-10-02:
                       "Composability doesn't mean composing two solutions just
                       because they can be composed. It means this principle
                       should be applied where two composed solutions demonstrably
                       provide a better, more robust and/or more efficient
                       solution than either fix in isolation. Where a single fix
                       out performs a composed one, that fix should continue to be
                       preferred." Measured 2026-10-31: 10 of 10 uses of the word
                       across the decisions file and the morning report took the
                       WEAK non-interference sense his definition excludes, Wilson
                       95% [0.722467, 1.000000]. This module therefore returns
                       MEASUREMENT_REQUIRED and names the property that must be
                       measured, rather than reporting that 2 fixes "compose".

WHAT IT IS FOR, then. It is a GATE on recommendations, not a ranker. Its useful
output is usually "these cannot be ranked, and here is exactly what is missing" --
which is a result, because the alternative is a confident ordering with nothing
behind it.
"""
from __future__ import annotations

import dataclasses
import difflib
import pathlib
import re
import sys
from typing import Any

REPO = pathlib.Path(__file__).resolve().parents[1]
for _p in (REPO, REPO / "scripts", REPO / "bench" / "tests"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

#: Verdicts. Deliberately not booleans: "I cannot decide" is a distinct and
#: common answer, and collapsing it into False would make an undecidable
#: comparison look like a failed one.
BREACHES = "BREACHES"
SATISFIES = "SATISFIES"
UNDECIDABLE = "UNDECIDABLE"
MEASUREMENT_REQUIRED = "MEASUREMENT_REQUIRED"


@dataclasses.dataclass
class Candidate:
    """One proposed fix. `fix_text` is a runner `proposed_fix` string."""
    label: str
    fix_text: str
    #: A property NAME the proposer claims this fix improves, with its measured
    #: before/after. Absent means no measurement, which is the normal case and
    #: is why composability is refused rather than assumed.
    measurement: dict[str, Any] | None = None


#: ★ THE REQUIRED KEYS OF A COMPOSED MEASUREMENT, DECLARED ONCE.
#:
#: FOUND 2026-11-03 by exercising this module rather than reading it: the
#: refusal message named 4 keys while the check enforced 5, so a caller
#: that obeyed the message was refused for `direction`, which the message
#: never mentioned. The message is now DERIVED from this set, so the 2
#: cannot drift apart again -- 1 declaration with 2 readers rather than 2
#: declarations asserted to agree. `direction` is load-bearing: without it
#: "dominates" is undefined, and the first version of this function called
#: a slower composition BETTER on a lower-is-better metric.
_COMPOSED_MEASUREMENT_KEYS = frozenset(
    {"property", "composed", "a_alone", "b_alone", "direction"})


def _extract(fix_text: str):
    """The live parser, not a re-implementation.

    `execute-do-not-grep`: 4 defects in this project were found by executing 2
    forms against each other and none was found by reading, so this calls the
    runner's own extractor rather than parsing SEARCH/REPLACE again here.
    """
    from bench.bugzilla_loop import extract_search_replace
    return extract_search_replace(fix_text or "")


#: WHICH CAPABILITY BUCKETS NAME THINGS A SOURCE EDIT CAN DELETE.
#:
#: ★ FOUND BY THIS MODULE'S OWN GUARD ON 2026-11-02, as a false-positive
#: generator of the worst kind. `capabilities()` has 4 buckets and one of them
#: is `mc_commands`, whose names are CHAT TOKENS: 24 of its 27 entries are
#: shorter than 3 characters -- `a`, `c`, `d`, `e`, `f`, `p`, `r`, `t`, `x`, `y`,
#: `ag`, `cx`, `cy`, `ds`, `ge`, `pr` and the rest. Matching `\ba\b` against a
#: diff fires on almost any English prose, so every candidate fix whose removed
#: text contained the word "a" was reported as DELETING A CAPABILITY.
#:
#: AND AN MC COMMAND CANNOT BE DELETED BY A SOURCE EDIT IN THE FIRST PLACE: it
#: is a token the founder types, declared in the instruction files, not a symbol
#: in the tree. Its removal half is already guarded by
#: `bench/tests/test_additive_standard_2026-09-07.py`, which reads the whole
#: snapshot and needs no diff. So excluding it here loses no coverage.
#:
#: The 3 included buckets carry 0 names shorter than 3 characters, measured, and
#: the identifier filter below is belt-and-braces so a future short name in a
#: code bucket cannot quietly reintroduce this.
CODE_IDENTIFIER_BUCKETS = ("runner_config_fields", "runner_public_entry_points",
                           "vault_subcommands")
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{2,}$")


def _capability_names() -> set[str]:
    """Capability names a source diff could plausibly delete."""
    import capability_snapshot as cs
    out: set[str] = set()
    caps = cs.capabilities() or {}
    for bucket in CODE_IDENTIFIER_BUCKETS:
        for n in (caps.get(bucket) or []):
            if _IDENTIFIER.match(str(n)):
                out.add(str(n))
    return out


def _retired_names() -> set[str]:
    """The RETIRED set the additive guard already maintains.

    Read from the guard rather than duplicated. A second copy of this set is
    exactly the producer/consumer drift this project keeps withdrawing.
    """
    try:
        import importlib.util
        p = REPO / "bench" / "tests" / "test_additive_standard_2026-09-07.py"
        spec = importlib.util.spec_from_file_location("_addstd", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        r = getattr(m, "RETIRED", None)
        return set(r) if r else set()
    except Exception:                                        # noqa: BLE001
        return set()


def additive_verdict(c: Candidate) -> tuple[str, str]:
    """Does this fix delete a known capability name without retiring it?

    DECIDABLE, and the decision is narrow on purpose: it answers only the
    REMOVAL half of the standard. The symmetric half -- that an addition
    nothing reaches is not additive either -- cannot be decided from a diff,
    because reachability is a property of the whole tree after the fix lands.
    That half is reported as UNDECIDABLE rather than guessed.
    """
    r = _extract(c.fix_text)
    if not r.success:
        return UNDECIDABLE, f"no parseable edit in the fix text: {r.reason}"
    old, new = r.old_code or "", r.new_code or ""
    caps, retired = _capability_names(), _retired_names()
    # A capability name present in the removed text and absent from the
    # replacement has been deleted by this fix.
    deleted = sorted(
        n for n in caps
        if re.search(rf"\b{re.escape(n)}\b", old)
        and not re.search(rf"\b{re.escape(n)}\b", new)
        and n not in retired)
    if deleted:
        return BREACHES, (
            f"deletes {len(deleted)} capability name(s) with no RETIRED entry: "
            f"{deleted[:6]}. The additive standard admits a removal only with a "
            f"COMMITTED MEASUREMENT showing the replacement dominates on a "
            f"named property.")
    # Shrinking without touching a NAMED capability is not decidable here.
    if len(new) < len(old):
        return UNDECIDABLE, (
            f"the replacement is shorter ({len(old)} -> {len(new)} chars) but "
            f"deletes no named capability. Whether anything was lost is not "
            f"decidable from the diff; a capability snapshot taken after the "
            f"fix lands would decide it.")
    return SATISFIES, (
        f"deletes no named capability ({len(old)} -> {len(new)} chars). This is "
        f"the REMOVAL half only; whether the addition is reached by a caller and "
        f"executed by a test is not decidable from a diff.")


def extent(c: Candidate) -> dict[str, Any]:
    """The INPUTS to a simplest-sufficient comparison. Never a score.

    Reported so a human or a programmatic rule can decide, because "smallest
    change addressing the root cause and its downstream consequences" needs the
    root cause, and the root cause is not in the fix text.
    """
    r = _extract(c.fix_text)
    old, new = (r.old_code or ""), (r.new_code or "")
    diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), n=0))
    return {
        "parses": bool(r.success),
        "file_hint": r.file_hint,
        "old_chars": len(old), "new_chars": len(new),
        "old_lines": len(old.splitlines()), "new_lines": len(new.splitlines()),
        "diff_hunks": sum(1 for d in diff if d.startswith("@@")),
        "net_lines": len(new.splitlines()) - len(old.splitlines()),
    }


def composability_verdict(a: Candidate, b: Candidate,
                          composed: Candidate | None = None) -> tuple[str, str]:
    """May the composition of `a` and `b` be RECOMMENDED? Almost never, by design.

    His definition requires a demonstration that the composition beats either
    part alone on a named property. Absent that measurement there is nothing to
    report but its absence, and reporting "they compose" would be the weak sense
    his definition explicitly excludes -- the sense 10 of 10 prior uses took.
    """
    m = (composed or Candidate("composed", "")).measurement
    if not m:
        return MEASUREMENT_REQUIRED, (
            f"no measurement supplied for the composition of {a.label!r} and "
            f"{b.label!r}. To recommend it, name the property and show the "
            f"composed fix dominating BOTH parts alone on that property. "
            f"Required keys: {', '.join(sorted(_COMPOSED_MEASUREMENT_KEYS))}.")
    # ★ `direction` IS REQUIRED, AND THIS WAS A LIVE DEFECT FOUND BY EXERCISING
    # THIS FUNCTION ON 2026-11-02 RATHER THAN BY READING IT. The first version
    # tested `comp > aa and comp > bb` unconditionally, so given a wall-clock
    # measurement -- composed 0.029 s against parts at 0.019 s and 0.010 s -- it
    # returned SATISFIES and recommended the SLOWEST option. "Dominates" has no
    # meaning until the measurement says which way is better, and inferring it
    # from the property NAME would be a proxy: `latency` and `throughput` run
    # opposite ways and both are plausible strings. A proxy chosen without
    # measuring its alternatives is this project's most recorded error class, so
    # the direction is DECLARED and its absence is refused.
    need = set(_COMPOSED_MEASUREMENT_KEYS)
    missing = sorted(need - set(m))
    if missing:
        return MEASUREMENT_REQUIRED, (
            f"the measurement omits {missing}; a composition cannot be "
            f"recommended on a partial one. `direction` must be "
            f"'higher_is_better' or 'lower_is_better': without it 'dominates' "
            f"is undefined, and a first version of this check recommended a "
            f"SLOWER composition because it assumed higher was better.")
    d = str(m.get("direction") or "").strip().lower()
    if d not in ("higher_is_better", "lower_is_better"):
        return MEASUREMENT_REQUIRED, (
            f"direction {m.get('direction')!r} is not one of "
            f"'higher_is_better' / 'lower_is_better'.")
    try:
        comp, aa, bb = float(m["composed"]), float(m["a_alone"]), float(m["b_alone"])
    except Exception as exc:                                 # noqa: BLE001
        return MEASUREMENT_REQUIRED, f"unreadable measurement: {exc}"
    dominates = ((comp > aa and comp > bb) if d == "higher_is_better"
                 else (comp < aa and comp < bb))
    if dominates:
        return SATISFIES, (
            f"the composition dominates both parts on {m['property']!r} "
            f"({d}): {comp} against {aa} and {bb}.")
    return BREACHES, (
        f"the composition does NOT dominate on {m['property']!r} ({d}): "
        f"{comp} against {aa} and {bb}. His standard is explicit that where a "
        f"single fix performs as well or better, the single fix is PREFERRED.")


def compare(candidates: list[Candidate]) -> dict[str, Any]:
    """Classify every candidate; rank only where ranking is decidable."""
    rows = []
    for c in candidates:
        verdict, why = additive_verdict(c)
        rows.append({"label": c.label, "additive": verdict,
                     "additive_reason": why, "extent": extent(c),
                     "simplest_sufficient": UNDECIDABLE,
                     "simplest_sufficient_reason":
                         "the root cause is not in the fix text; extent is "
                         "reported as an input, never as a ranking"})
    survivors = [r for r in rows if r["additive"] != BREACHES]
    breaches = [r for r in rows if r["additive"] == BREACHES]

    if len(survivors) == 1 and breaches:
        ranked, why = survivors[0]["label"], (
            f"{len(breaches)} candidate(s) breach the additive standard by "
            f"deleting a capability with no RETIRED entry, leaving exactly 1. "
            f"That is a decision by ELIMINATION and not a judgement of quality.")
    else:
        ranked, why = None, (
            f"{len(survivors)} candidate(s) survive the additive check and the "
            f"remaining standards are not decidable from the fix text. NOT "
            f"RANKABLE. To rank them, supply a measurement naming the property "
            f"each fix is claimed to improve -- which is what the composability "
            f"standard requires of a composition and what simplest-sufficient "
            f"requires of a root cause.")
    return {"candidates": rows, "recommended": ranked, "reason": why,
            "n_breaching": len(breaches), "n_surviving": len(survivors)}


# ───────────────────────────────────────────────────────────────────────────
# A CLI, SO THIS IS NOT AN UNWIRED ADDITION.
#
# `additive-standard`'s symmetric half: "an addition that nothing reaches is not
# additive either -- every new flag, gate, subcommand or entry point must be
# wired to a caller and executed by a test." This module IS executed by 21 tests
# in `bench/tests/test_the_fix_comparator_refuses_to_rank_2026-11-02.py`, and it
# has 0 PRODUCTION callers, because the bound orchestrator that would call it is
# the remaining B20 work. That is a declared state rather than a hidden one.
#
# The CLI closes the gap for a human today: a researcher with 2 candidate fixes
# in files can get the classification now, without waiting for the orchestrator.
def main() -> int:
    import argparse
    import json

    ap = argparse.ArgumentParser(
        prog="fix_comparator.py",
        description="Classify candidate fixes against the 3 formal standards. "
                    "It REFUSES to rank where ranking is undecidable, which is "
                    "the normal outcome and is a result rather than a failure.")
    ap.add_argument("--fix", action="append", default=[], metavar="LABEL=PATH",
                    help="a candidate: a label and a file holding its "
                         "proposed_fix text. Repeatable.")
    ap.add_argument("--measurement", default=None, metavar="JSON_PATH",
                    help="a file holding the composition measurement: "
                         "property, composed, a_alone, b_alone, direction "
                         "('higher_is_better' or 'lower_is_better'). Without "
                         "it a composition cannot be recommended at all.")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if not a.fix:
        ap.error("give at least 1 --fix LABEL=PATH; with 1 it reports that "
                 "candidate's standing, with 2 or more it attempts a comparison")

    cands = []
    for spec in a.fix:
        if "=" not in spec:
            ap.error(f"--fix must be LABEL=PATH, got {spec!r}")
        label, path = spec.split("=", 1)
        p = pathlib.Path(path)
        if not p.is_file():
            ap.error(f"no such file for candidate {label!r}: {path}")
        cands.append(Candidate(label, p.read_text(encoding="utf-8",
                                                  errors="replace")))

    result = compare(cands)
    if a.measurement and len(cands) >= 2:
        mp = pathlib.Path(a.measurement)
        if not mp.is_file():
            ap.error(f"no such measurement file: {a.measurement}")
        m = json.loads(mp.read_text())
        v, why = composability_verdict(
            cands[0], cands[1], Candidate("composed", "", measurement=m))
        result["composability"] = {"verdict": v, "reason": why}
    elif len(cands) >= 2:
        v, why = composability_verdict(cands[0], cands[1])
        result["composability"] = {"verdict": v, "reason": why}

    if a.json:
        print(json.dumps(result, indent=1, default=str))
        return 0

    print("=" * 74)
    print("CANDIDATE FIXES AGAINST THE 3 FORMAL STANDARDS")
    print("=" * 74)
    for row in result["candidates"]:
        e = row["extent"]
        print(f"\n  {row['label']}")
        print(f"    ADDITIVE            : {row['additive']}")
        print(f"      {row['additive_reason']}")
        print(f"    SIMPLEST SUFFICIENT : {row['simplest_sufficient']}")
        print(f"      {row['simplest_sufficient_reason']}")
        print(f"    extent (an input, never a score): "
              f"{e['old_lines']} -> {e['new_lines']} lines, "
              f"net {e['net_lines']:+d}, {e['diff_hunks']} hunk(s), "
              f"file hint {e['file_hint']!r}")
    if "composability" in result:
        print(f"\n  COMPOSABILITY         : {result['composability']['verdict']}")
        print(f"    {result['composability']['reason']}")
    print(f"\n  RECOMMENDED : {result['recommended'] or 'NONE'}")
    print(f"  {result['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
