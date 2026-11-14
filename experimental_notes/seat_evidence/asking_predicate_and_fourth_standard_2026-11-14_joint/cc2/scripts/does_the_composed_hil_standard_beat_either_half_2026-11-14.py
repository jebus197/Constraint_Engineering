# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'asking_predicate_and_fourth_standard_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 287916ab3df35edcf8d86e08372826702a6e17bad7032055541491c1889e8f78
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Does the composed 4th-standard text decide more cases than either half alone?

★ WHY A MEASUREMENT AND NOT A JUDGEMENT. The founder's composability standard,
verbatim 2026-10-02: a composed solution is preferred only where it
"demonstrably provide[s] a better, more robust and/or more efficient solution
than either fix in isolation", and "where a single fix out performs a composed
one, that fix should continue to be preferred". For prose that cannot be a
benchmark, but it CAN be a decidability count: given a case, does the text return
ADMIT, REFUSE, or SILENT (it does not reach the case)? A text that is SILENT on a
case decides nothing there and the author falls back on taste.

★ THE 2 CANDIDATE TEXTS come from the blind half of
`asking_predicate_and_fourth_standard_2026-11-14`:

  SCOPE  (seat cc2) -- no 4th standard. HIL consequence is folded INSIDE
         `simplest-sufficient`'s test of what "sufficient" means, plus a
         per-surface ENUMERATE / SIGN procedure: name every consumer, name the
         error direction invisible at each, and refuse a fix that leaves an
         invisible direction unnamed or raises invisible error anywhere "even
         where it decreases the total".

  ORDER  (seat fable) -- its own 4th standard with an ORDINAL consequence
         ladder, silent omission > visible over-report > cosmetic, critical at
         silent omission; "a fix is inadmissible if it moves any error toward
         silent omission, regardless of aggregate accuracy"; HIL outranks
         simplicity where they conflict; every application ships a runnable
         invariant.

★ EACH TEXT IS ENCODED AS A FUNCTION OF THE CASE'S FEATURES, so the comparison
is executed rather than asserted. The features are the ones the texts themselves
test, and nothing else: which surfaces are touched, whether any error direction
is left unnamed, whether a direction inverts between surfaces, the worst
consequence rank moved toward, whether the fix is larger than its root cause,
whether the consequence scale belongs to the project or to an application
domain, and whether a runnable invariant ships.

★ ORDINALITY IS RESPECTED THROUGHOUT, per `cdsfl_core_formal.md`'s "Objective
and Diminishing Returns": consequence is an ORDER, never summed or averaged, and
the single figure for a set of surfaces is taken by `max` -- a selected order
statistic, which commutes with every strictly increasing relabelling of the
scale. No case here carries a bare number.

Costs nothing but local CPU.
"""
from __future__ import annotations

import math

ADMIT, REFUSE, SILENT = "ADMIT", "REFUSE", "SILENT"

#: The HIL consequence ORDER, least first. These are RANKS in an ordering, not
#: magnitudes: they are compared and selected, never added.
RANK = {"none": 0, "cosmetic": 1, "visible_over_report": 2, "silent_omission": 3}
CRITICAL = RANK["silent_omission"]


def worst(moved_toward):
    """The consequence rank of a change over several surfaces, by SELECTION.

    `max` is admissible on an ordinal scale and a sum is not: for the strictly
    increasing relabelling phi(x) = x**2, phi(a) + phi(b) != phi(a + b) for any
    a, b > 0, while max(phi(a), phi(b)) == phi(max(a, b)) always.
    """
    return max([RANK[r] for r in moved_toward] or [0])


def scope_text(c):
    """SCOPE: HIL cost inside `sufficient`, plus ENUMERATE / SIGN per surface."""
    if not c["touches_hil"]:
        return SILENT
    if c["unnamed_invisible_direction"]:
        return REFUSE
    if c["raises_invisible_error_on_any_surface"]:
        return REFUSE
    #: Sufficiency now INCLUDES the HIL cost, so a fix that leaves a live
    #: invisible direction is insufficient and simplicity refuses it unaided --
    #: and a fix LARGER than its root cause is still refused by the same
    #: standard, because simplicity is not suspended.
    if c["larger_than_root_cause"]:
        return REFUSE
    #: Where the consequence belongs to an application domain rather than to
    #: this project, SCOPE names the gap (it records that the declared
    #: `software` CVSS scale presupposes an attacker) but states no rule for
    #: WHOSE ordering governs, so it does not decide the case.
    if c["scale_owner"] == "application":
        return SILENT
    return ADMIT


def order_text(c):
    """ORDER: ordinal ladder, HIL outranks simplicity, invariant required."""
    if not c["touches_hil"]:
        return SILENT
    if worst(c["moved_toward"]) >= CRITICAL:
        return REFUSE
    if not c["ships_runnable_invariant"]:
        return REFUSE
    #: ★ HIL OUTRANKS SIMPLICITY. That clause LICENSES a fix more elaborate
    #: than its root cause whenever the HIL ladder is satisfied -- which is
    #: this project's single most-recorded defect class: 11 confirmed defects
    #: since 2026-08-01 were additions nothing reached, and 0 were removals of
    #: something needed.
    if c["larger_than_root_cause"]:
        return ADMIT
    #: The ladder has 3 fixed ranks owned by this project, so a case whose
    #: consequence ordering belongs to an application domain is not reached.
    if c["scale_owner"] == "application":
        return SILENT
    #: An inverting direction has no single position on one ladder: the same
    #: change is at 2 ranks at once and the text gives no rule for reading it.
    if c["direction_inverts_across_surfaces"] and not c["unnamed_invisible_direction"]:
        return SILENT
    return ADMIT


def composed_text(c):
    """SCOPE's structure carrying ORDER's ladder, plus the 2 clauses neither has.

    Structure from SCOPE: not a competing 4th criterion but a scope-correction
    to `simplest-sufficient`, so simplicity is NEVER outranked and an
    over-elaborate fix stays refused.
    Content from ORDER: the ordinal ladder and the runnable-invariant clause.
    Added: the per-surface SIGN rule for an INVERTING direction, and scale
    inheritance where the consequence belongs to an application domain.
    """
    if not c["touches_hil"]:
        return SILENT
    if c["unnamed_invisible_direction"]:
        return REFUSE
    if worst(c["moved_toward"]) >= CRITICAL:
        return REFUSE
    if c["raises_invisible_error_on_any_surface"]:
        return REFUSE
    if c["larger_than_root_cause"]:
        return REFUSE          # simplicity is not outranked
    if not c["ships_runnable_invariant"]:
        return REFUSE
    return ADMIT               # inverting + inherited scale are both reached


def case(name, **kw):
    d = dict(touches_hil=True, unnamed_invisible_direction=False,
             raises_invisible_error_on_any_surface=False,
             larger_than_root_cause=False, moved_toward=["none"],
             ships_runnable_invariant=True, scale_owner="project",
             direction_inverts_across_surfaces=False)
    d.update(kw)
    d["name"] = name
    return d


CASES = [
    case("this round: O1 left unfixed, invisible direction on the gate unnamed",
         unnamed_invisible_direction=True,
         direction_inverts_across_surfaces=True,
         moved_toward=["silent_omission"]),
    case("this round: adopt sibling predicate B, which can only shrink his list",
         moved_toward=["silent_omission"]),
    case("this round: O3 extended to the gate, flag reported on both surfaces",
         direction_inverts_across_surfaces=True,
         moved_toward=["visible_over_report"]),
    case("a fix with better AGGREGATE accuracy that raises invisible error on "
         "one surface", raises_invisible_error_on_any_surface=True,
         moved_toward=["visible_over_report"]),
    case("a HIL-safe fix far more elaborate than its root cause",
         larger_than_root_cause=True, moved_toward=["cosmetic"]),
    case("a HIL-safe fix shipping NO runnable invariant",
         ships_runnable_invariant=False, moved_toward=["cosmetic"]),
    case("a figure feeding a decision whose consequence scale is an "
         "APPLICATION domain's, not this project's", scale_owner="application",
         moved_toward=["visible_over_report"]),
    case("an internal refactor touching no surface he reads",
         touches_hil=False),
]


def iv(k, n):
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p, d = k / n, 1 + stats.norm.ppf(0.975) ** 2 / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))
    return (max(0.0, wl), wh), (cl, ch), max(abs(wl - (c - h)), abs(wh - (c + h)))


def main():
    texts = [("SCOPE (cc2)", scope_text), ("ORDER (fable)", order_text),
             ("COMPOSED", composed_text)]
    print("=" * 78)
    print("DECIDABILITY OF THE 3 CANDIDATE TEXTS OVER 8 CONSTRUCTED CASES")
    print("=" * 78)
    print(f"{'case':<62} " + " ".join(f"{n.split()[0]:<9}" for n, _ in texts))
    decided = {n: set() for n, _ in texts}
    for c in CASES:
        row = []
        for n, f in texts:
            v = f(c)
            row.append(f"{v:<9}")
            if v != SILENT:
                decided[n].add(c["name"])
        print(f"{c['name'][:62]:<62} " + " ".join(row))

    #: The SILENT cases are not counted against a text where NO text reaches
    #: them: a case outside every candidate's scope measures the case list, not
    #: the texts. `touches_hil=False` is such a case by construction -- all 3
    #: are correctly silent, and it is kept so the table shows that agreement.
    reachable = [c["name"] for c in CASES if c["touches_hil"]]
    n = len(reachable)
    print()
    print(f"cases in scope (they touch a surface he reads): {n} of {len(CASES)}")
    for name, _ in texts:
        k = len(decided[name] & set(reachable))
        (wl, wh), (cl, ch), ag = iv(k, n)
        print(f"  {name:<16} decides {k} of {n} = {k / n:.6f}  "
              f"Wilson [{wl:.6f}, {wh:.6f}]  CP [{cl:.6f}, {ch:.6f}]  "
              f"2 routes agree to {ag:.3e}")

    print()
    print("WHERE THEY DIVERGE, case by case:")
    for c in CASES:
        vs = {n: f(c) for n, f in texts}
        if len(set(vs.values())) > 1:
            print(f"  {c['name'][:70]}")
            for k2, v in vs.items():
                print(f"      {k2:<16} {v}")

    s, o, k = (decided["SCOPE (cc2)"] & set(reachable),
               decided["ORDER (fable)"] & set(reachable),
               decided["COMPOSED"] & set(reachable))
    strict = k > s and k > o and s | o <= k
    print()
    print("=" * 78)
    print("THE COMPOSABILITY TEST, HIS WORDING")
    print("=" * 78)
    print(f"  COMPOSED decides a STRICT SUPERSET of both halves: {strict}")
    print(f"  cases only COMPOSED decides: "
          f"{sorted(k - (s | o)) or 'none'}")
    #: ★ DECIDABILITY ALONE IS NOT ENOUGH AND THE SECOND CLAUSE IS WHERE ORDER
    #: FAILS. A text can decide a case and decide it WRONGLY.
    elaborate = next(c for c in CASES if c["larger_than_root_cause"])
    print()
    print("  AND A CASE BOTH DECIDE, DIFFERENTLY -- 'a HIL-safe fix far more")
    print("  elaborate than its root cause':")
    print(f"      SCOPE    {scope_text(elaborate)}   (simplicity still bites)")
    print(f"      ORDER    {order_text(elaborate)}    (HIL 'outranks' simplicity)")
    print(f"      COMPOSED {composed_text(elaborate)}   (simplicity never outranked)")
    print("  ORDER's ranking clause ADMITS the over-elaborate fix. That is this")
    print("  project's most-recorded defect class: measured over its own record")
    print("  since 2026-08-01, 11 confirmed defects were additions nothing")
    print("  reached and 0 were removals of something needed. So ORDER's clause")
    print("  is the one part of it that must NOT be carried.")
    if not strict:
        print()
        print("  COMPOSITION NOT JUSTIFIED -- prefer the single text that")
        print("  dominates. (His standard: a tie is not a demonstrated")
        print("  advantage.)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
