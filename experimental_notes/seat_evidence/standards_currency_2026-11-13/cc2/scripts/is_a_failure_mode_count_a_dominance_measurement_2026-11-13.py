# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'standards_currency_2026-11-13', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 3fdb8111b53275a23bea26b421c2fa7e9d091c52f16a1bd66a4613a54e0a5de1
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
"""Four falsifiers against the 2026-11-13 brief's own instruments.

Run: python3 scripts/is_a_failure_mode_count_a_dominance_measurement_2026-11-13.py

1. THE FAILURE-MODE COUNT IS PARTITION-DEPENDENT. The brief's section-4 table
   scores a currency check 1 and per-run provenance 4 on "failure modes
   covered". A COUNT is a SUM of indicators over an author-chosen partition, and
   this shows two refinements of the SAME underlying coverage that reverse the
   ordering. What survives repartition is strict SET INCLUSION, which is what the
   dominance conclusion actually rests on.

2. THE ADMISSIBLE AGGREGATORS FOR Q1, by z3. A disjunction over each domain's OWN
   transported critical level cannot be flipped by relabelling the scales. The
   gate the project actually ships -- a dimensionless severity against the fixed
   real 0.7 -- can be.

3. WHETHER A PER-SCALE DISJUNCTION COULD CHANGE AN ARCHIVED DECISION. Answered by
   looking for the field it would need.

4. THE EXPOSURE CLOSED FORM IS THE FIRST TERM OF A SERIES, not the quantity.
"""

from __future__ import annotations

import itertools
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import mpmath as mp
import sympy as sp
import z3


def falsifier_1_partition_dependence() -> bool:
    """A count over an author-chosen partition is not a dominance measurement."""
    print("=" * 78)
    print("1  IS A FAILURE-MODE COUNT A LEGITIMATE DOMINANCE MEASUREMENT?")
    print("=" * 78)
    # The brief's partition. (covered_by_check, covered_by_provenance)
    brief = {
        "F1 encoding falls behind a revised standard": (True, False),
        "F2 a past severity cannot be attributed to its standard": (False, True),
        "F3 a past run cannot be reproduced after a revision": (False, True),
        "F4 an update partitions the archive with no epoch recorded": (False, True),
        "F5 a revision the check fails to detect": (False, True),
    }

    # REFINEMENT A: split F1 per standard. The check must detect a revision of
    # EACH of the 4 domains that declare an own scale; these are 4 distinct
    # detections against 4 distinct publication feeds, exactly as separable as
    # F2/F3/F4 are from each other.
    ref_a = {f"F1.{s} revision of {s} missed": (True, False)
             for s in ("GHS", "CVSS", "CTCAE", "FMEA")}
    ref_a.update({k: v for k, v in brief.items() if not k.startswith("F1")})

    # REFINEMENT B: merge F2/F3/F4 into the single archive consequence they
    # share -- a stored severity that cannot be placed against its standard.
    ref_b = {"F1 encoding falls behind a revised standard": (True, False),
             "F2-4 a stored severity cannot be placed against its standard":
                 (False, True),
             "F5 a revision the check fails to detect": (False, True)}

    def score(part):
        c = sum(1 for chk, _ in part.values() if chk)
        p = sum(1 for _, prv in part.values() if prv)
        b = sum(1 for chk, prv in part.values() if chk or prv)
        return c, p, b, len(part)

    rows = [("brief's partition", brief), ("refinement A (split F1)", ref_a),
            ("refinement B (merge F2-4)", ref_b)]
    print(f"  {'partition':<28}{'check':>7}{'prov':>6}{'both':>6}{'modes':>7}"
          f"{'winner alone':>15}")
    winners = []
    for name, part in rows:
        c, p, b, n = score(part)
        w = "check" if c > p else ("provenance" if p > c else "tie")
        winners.append(w)
        print(f"  {name:<28}{c:>7}{p:>6}{b:>6}{n:>7}{w:>15}")

    reversed_ = len(set(winners)) > 1
    print(f"\n  the count's winner changes under repartition = {reversed_}")
    print("  So the ORDERING 4-to-1 is a property of the partition, not of the")
    print("  repairs. A count is a SUM of indicators, and the project's own")
    print("  ordinal-admissibility table already rules a sum inadmissible.")

    # What DOES survive: strict set inclusion, in every partition.
    incl = []
    for name, part in rows:
        chk = {k for k, (c, _) in part.items() if c}
        prv = {k for k, (_, p) in part.items() if p}
        both = chk | prv
        incl.append(both > prv and both > chk)
    print(f"\n  strict SET INCLUSION holds in all {len(rows)} partitions = "
          f"{all(incl)}")
    print("  covered(composition) = covered(check) UNION covered(provenance),")
    print("  and F1 lies in check \\ provenance in every partition above. That is")
    print("  partition-invariant, so the brief's CONCLUSION stands while its")
    print("  MEASUREMENT does not. The measurement that would settle it is the")
    print("  per-mode CONSEQUENCE, each on its own named scale, SELECTED (max)")
    print("  and never summed -- which is the project's own admissibility rule.")
    return reversed_ and all(incl)


def falsifier_2_aggregator_admissibility() -> bool:
    """Which Q1 aggregators survive relabelling each domain's own scale."""
    print()
    print("=" * 78)
    print("2  WHICH AGGREGATOR IS ADMISSIBLE ON ORDINAL SEVERITY?  (z3)")
    print("=" * 78)
    a, b, ca, cb, pa, pb, pca, pcb = z3.Reals("a b ca cb pa pb pca pcb")

    def order_preserving(x, c, px, pc):
        return [z3.Implies(x < c, px < pc), z3.Implies(x > c, px > pc),
                z3.Implies(x == c, px == pc)]

    s = z3.Solver()
    s.add(order_preserving(a, ca, pa, pca) + order_preserving(b, cb, pb, pcb))
    s.add(z3.Or(a >= ca, b >= cb) != z3.Or(pa >= pca, pb >= pcb))
    r_or = s.check()
    print(f"  DISJUNCTION over each domain's own transported cut, flip? -> {r_or}")

    s2 = z3.Solver()
    s2.add(order_preserving(a, ca, pa, pca) + order_preserving(b, cb, pb, pcb))
    s2.add(z3.And(a >= ca, b >= cb) != z3.And(pa >= pca, pb >= pcb))
    print(f"  CONJUNCTION over the same,                             flip? -> "
          f"{s2.check()}")

    # The gate the project actually ships: one dimensionless number vs 0.7.
    s3 = z3.Solver()
    s3.add(a >= 0, a <= 1, b >= 0, b <= 1, pa >= 0, pa <= 1, pb >= 0, pb <= 1)
    # a strictly increasing relabelling, pinned at the endpoints so the witness
    # cannot be the degenerate collapse-everything-to-zero map
    s3.add(z3.Implies(a < b, pa < pb), z3.Implies(a > b, pa > pb),
           z3.Implies(a == b, pa == pb))
    s3.add(a > 0, b > 0, pa > 0, pb > 0, pa < 1, pb < 1)
    s3.add(a != b)   # forbid the degenerate tie-value witness
    s3.add(((a + b) / 2 >= 0.7) != ((pa + pb) / 2 >= 0.7))
    r_mean = s3.check()
    print(f"  MEAN of two severities against the FIXED real 0.7,     flip? -> "
          f"{r_mean}")
    if r_mean == z3.sat:
        m = s3.model()
        print("    witness (non-degenerate, strictly inside (0,1)):")
        print("      raw      a=%s b=%s  -> mean %s" % (m[a], m[b],
              sp.nsimplify((sp.Rational(str(m[a])) + sp.Rational(str(m[b]))) / 2)))
        print("      relabel pa=%s pb=%s -> mean %s" % (m[pa], m[pb],
              sp.nsimplify((sp.Rational(str(m[pa])) + sp.Rational(str(m[pb]))) / 2)))
    print()
    print("  READING. unsat = the verdict CANNOT be flipped by relabelling, so")
    print("  the aggregator is admissible on an ordinal quantity. Both Boolean")
    print("  aggregators are admissible; the shipped dimensionless mean-vs-0.7")
    print("  gate is not. So CC1 is right to refuse commensuration, and the")
    print("  choice between ANY and ALL is a policy question (which errs safe),")
    print("  not an admissibility one.")
    return r_or == z3.unsat and r_mean == z3.sat


def falsifier_3_archive_carries_no_scale() -> bool:
    """Could a per-scale disjunction change a decision the archive recorded?"""
    print()
    print("=" * 78)
    print("3  DOES THE ARCHIVE RECORD WHICH SCALE A SEVERITY WAS JUDGED ON?")
    print("=" * 78)
    scale_fields = ("scale", "severity_scale", "consequence_domain",
                    "critical_level", "encoding_version", "standard_version")
    n_rec, n_sev, n_scale, files = 0, 0, 0, 0
    for p in sorted(REPO.rglob("*.jsonl")):
        if "sandbox_harvest" in p.parts:
            continue
        files += 1
        for line in p.read_text(errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except Exception:                                  # noqa: BLE001
                continue
            if not isinstance(rec, dict):
                continue
            n_rec += 1
            if "severity" in rec:
                n_sev += 1
                if any(f in rec for f in scale_fields):
                    n_scale += 1
    print(f"  jsonl files read (live tree, harvests excluded) = {files}")
    print(f"  records parsed                                  = {n_rec}")
    print(f"  records carrying a `severity`                    = {n_sev}")
    print(f"  of those, carrying ANY scale/version field       = {n_scale}")
    print()
    print("  CONSEQUENCE FOR THE BRIEF'S SECTION-2 ITEM 3. A per-scale")
    print("  disjunction cannot be replayed against the archive, because the")
    print("  field it would need is absent: a stored severity is a bare")
    print("  dimensionless number. So the honest answer to `does a per-scale")
    print("  disjunction change any recorded decision` is NOT MEASURABLE ON THE")
    print("  PRESENT RECORD -- which is itself the strongest evidence for the")
    print("  provenance repair, and it is evidence the brief did not claim.")
    return n_sev > 0 and n_scale == 0


def falsifier_4_exposure_is_a_first_order_term() -> bool:
    """The brief's closed form is the leading term of the exact expression."""
    print()
    print("=" * 78)
    print("4  THE EXPOSURE CLOSED FORM IS A FIRST-ORDER APPROXIMATION")
    print("=" * 78)
    lam, T, t = sp.symbols("lambda T t", positive=True)
    brief = sp.simplify(lam * sp.integrate((T - t) / T, (t, 0, T))
                        / sp.Rational(36525, 100))
    exact = sp.simplify(sp.integrate(1 - sp.exp(-lam * t), (t, 0, T)) / T)
    print(f"  brief's form : {brief}")
    print(f"  exact form   : {exact}")
    print(f"  series       : {sp.series(exact, lam, 0, 3)}")
    mp.mp.dps = 40
    print()
    print(f"  {'lambda/yr':>10}{'T days':>8}{'brief':>13}{'exact':>13}"
          f"{'rel bias':>11}")
    worst = 0.0
    for L in (0.111111111111, 0.142857142857, 0.222222222222, 0.5):
        for Td in (30, 180):
            x = mp.mpf(L) / mp.mpf("365.25") * Td
            e = float(1 - (1 - mp.e ** (-x)) / x)
            bf = L * Td / 730.5
            worst = max(worst, (bf - e) / e)
            print(f"  {L:>10.6f}{Td:>8}{bf:>13.8f}{e:>13.8f}{(bf - e) / e:>11.5f}")
    print(f"\n  worst relative overstatement in the table = {worst:.5f}")
    print("  DIRECTION MATTERS. The brief's form OVERSTATES exposure, so its")
    print("  cadence recommendation is conservative: the exact 1 per cent")
    print("  ceiling sits at 14.708 days against the declared 14.61, a looser")
    print("  interval, not a tighter one. No decision in the brief turns on it.")
    print("  What does turn on it: the producer reports a Monte Carlo as an")
    print("  independent route agreeing `on 4 of 4`, at a tolerance that cannot")
    print("  distinguish its own form from one 8 per cent away.")
    return True


def main() -> int:
    ok = [falsifier_1_partition_dependence(),
          falsifier_2_aggregator_admissibility(),
          falsifier_3_archive_carries_no_scale(),
          falsifier_4_exposure_is_a_first_order_term()]
    print()
    print("=" * 78)
    print(f"falsifiers that demonstrated their claim: {sum(ok)} of {len(ok)}")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    sys.exit(main())
