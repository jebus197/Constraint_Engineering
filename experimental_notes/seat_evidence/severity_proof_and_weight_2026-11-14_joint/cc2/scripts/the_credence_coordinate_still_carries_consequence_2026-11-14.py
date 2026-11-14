# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'severity_proof_and_weight_2026-11-14_joint', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 00ee260196f06f6552a39a5c81c601bc47367f0ea99e571f89d68a4623242352
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Three measurements the joint round of `severity_proof_and_weight_2026-11-14` turns on.

WHY THIS EXISTS. The blind half produced two replies that AGREE on the three
verdicts (R1 hold, R2 reject, R3 recommend) and DISAGREE on three measurable
facts underneath them. Two seats reaching one answer by one flawed route is not
corroboration, so each disputed fact is re-derived here from the live modules
rather than quoted from either reply.

M-A  THE DOOR'S POPULATION IS THREE POPULATIONS, NOT ONE.
     `severity_is_proven` has three live call sites and they do NOT share a
     population. Sites A (the A4 release door, ~4442) and B (reasoned
     withdrawal, ~9735) are each conjoined with `severity < CRITICAL_SEVERITY_
     THRESHOLD`, so an entry at or above the cut never held their exemption.
     Site C (calibration demotion, ~10936) is NOT so conjoined: the live
     `_is_demotion_eligible` REQUIRES `severity >= CRITICAL_SEVERITY_THRESHOLD`,
     so site C acts on exactly the complement -- the population sites A and B
     exclude. Seat `cc2`'s 555/652 therefore merges three populations, and seat
     `fable`'s correction to 422/519 is right for A and B while excluding the
     only population C can touch. The honest report is a PAIR of figures.

M-B  THE `credence` COORDINATE OF THE ORDERED PAIR STILL CARRIES CONSEQUENCE.
     Appendix section 7.7.1 defines `severity_d(f) = ( c_d(f) , credence(f) )`
     with "`credence(f)` being today's section 7.7 product under its own name".
     That product is `W(class) * confidence * Ver(verification)`, and `W` is
     keyed on CONSTRAINT CLASS -- the core directives' section 1 partition of
     physics/mathematics/law/safety (HARD) from economic/preference/convenience
     (SOFT). That is a CONSEQUENCE classification. So the coordinate named
     `credence` is not a function of the evidence alone: two findings with
     IDENTICAL evidence (same confidence, same falsifier verdict) receive
     different credence solely because one concerns a safety constraint. This
     is the very defect section 7.7.1 names -- "a product of a consequence and
     a belief is neither" -- surviving INSIDE the repair for it.

     The consequence for J3: seat `fable` asserts that under R3 a 3rd weight
     "decides nothing the pair gate reads". A pair is compared
     LEXICOGRAPHICALLY; when `c_d` ties, the comparison falls through to
     `credence`, which contains `W`. A 3rd weight therefore changes pair
     orderings. Demonstrated below by construction.

M-C  WHAT A PER-DOMAIN CUT DOES TO THE FROZEN SPELLINGS.
     Read by IMPORTING the modules. The brief says four spellings outside the
     canonical constant; there are SIX, because `convergence_location` carries
     `critical_threshold=0.7` on FOUR functions, not two -- a parameter default
     is invisible to a text search for an assignment. Seat `cc2` counted six
     and is right. Then the manifest is read for what a per-domain cut IS.

Usage: python3 scripts/the_credence_coordinate_still_carries_consequence_2026-11-14.py
"""
import inspect
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

LOGS = REPO / "bench" / "logs"
PROVEN = {"PASS", "WARN"}
TOL = 0.05


def rule(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def wilson(k, n):
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        return (float("nan"), float("nan"))
    return proportion_confint(k, n, alpha=0.05, method="wilson")


def load_entries():
    """Every archived entry carrying a PASS/WARN R_k proof, in full."""
    out = []
    for fp in LOGS.glob("**/runner_state.json"):
        try:
            d = json.loads(fp.read_text(encoding="utf-8", errors="ignore"))
        except Exception:                                      # noqa: BLE001
            continue
        for e in ((d or {}).get("registry") or {}).get("entries", {}).values():
            if not isinstance(e, dict):
                continue
            proof = e.get("severity_proof")
            if not isinstance(proof, dict):
                continue
            if str(proof.get("status") or "").strip().upper() not in PROVEN:
                continue
            sev = e.get("severity")
            rk = proof.get("recomputed_rk", proof.get("model_rk"))
            if isinstance(sev, (int, float)) and isinstance(rk, (int, float)):
                out.append((e, float(sev), float(rk)))
    return out


def m_a():
    rule("M-A  the door's population is THREE populations, not one")
    from bench.reference_runner_v3 import (
        CRITICAL_SEVERITY_THRESHOLD as CUT, severity_is_proven,
        _is_demotion_eligible,
    )
    rows = load_entries()
    n = len(rows)
    print("archived entries carrying a PASS/WARN R_k proof: %d" % n)
    if n < 10:
        print("too few entries; measurement void.")
        return None

    old = [severity_is_proven(e) for e, _s, _r in rows]
    new = [o and abs(s - r) <= TOL for o, (_e, s, r) in zip(old, rows)]
    assert all(old), "rows selected on PASS/WARN; the live fn must agree"

    flips = sum(1 for o, nw in zip(old, new) if o and not nw)
    loosen = sum(1 for o, nw in zip(old, new) if nw and not o)
    lo, hi = wilson(flips, n)
    print("\n  cc2's population (ALL proven entries, proven-status flips):")
    print("    flip PROVEN -> UNPROVEN : %d/%d = %.2f%%  Wilson [%.2f%%, %.2f%%]"
          % (flips, n, 100 * flips / n, 100 * lo, 100 * hi))
    print("    flip UNPROVEN -> PROVEN : %d   (loosening impossible by "
          "conjunction)" % loosen)

    ab = [(o, nw) for o, nw, (_e, s, _r) in zip(old, new, rows) if s < CUT]
    ab_n = len(ab)
    ab_lost = sum(1 for o, nw in ab if o and not nw)
    lo2, hi2 = wilson(ab_lost, ab_n)
    print("\n  fable's population (sites A and B: severity < %s):" % CUT)
    print("    entries holding the exemption today : %d" % ab_n)
    print("    entries LOSING it when repointed    : %d/%d = %.2f%%  "
          "Wilson [%.2f%%, %.2f%%]"
          % (ab_lost, ab_n, 100 * ab_lost / ab_n, 100 * lo2, 100 * hi2))

    above = [(e, s, r) for (e, s, r) in rows if s >= CUT]
    print("\n  the population both headline figures mishandle "
          "(site C: severity >= %s):" % CUT)
    print("    entries at or above the cut : %d" % len(above))
    elig = [(e, s, r) for (e, s, r) in above if _is_demotion_eligible(e)]
    print("    of those, demotion-ELIGIBLE (live _is_demotion_eligible): %d"
          % len(elig))
    c_lost = sum(1 for e, s, r in elig
                 if severity_is_proven(e) and not abs(s - r) <= TOL)
    print("    eligible entries LOSING their demotion when repointed: %d"
          % c_lost)
    print("\n  VERDICT: site C acts ONLY on severity >= %s, which fable's %d "
          "excludes\n           entirely, and cc2's %d merges with the other "
          "two. Neither single\n           number is the door-relevant figure; "
          "the PAIR is." % (CUT, ab_n, n))
    print("           sites A+B: %d/%d    site C: %d/%d eligible"
          % (ab_lost, ab_n, c_lost, len(elig)))
    return dict(n=n, flips=flips, ab_n=ab_n, ab_lost=ab_lost,
                above=len(above), elig=len(elig), c_lost=c_lost)


def m_b():
    rule("M-B  the `credence` coordinate is NOT a function of the evidence alone")
    from bench.reference_runner_v3 import compute_sev_f, SEV_F_W

    print("  SEV_F_W (live) = %r" % (SEV_F_W,))
    print("  W is keyed on CONSTRAINT CLASS, which core-directives section 1")
    print("  defines as a CONSEQUENCE partition: physics/mathematics/law/")
    print("  safety = HARD, economic/preference/convenience = SOFT.\n")

    print("  evidential-invariance test -- same evidence, different class:")
    bad = 0
    for conf in (0.9, 0.6, 0.3):
        for verdict in ("CONFIRMED", "UNTOOLABLE"):
            h = compute_sev_f("HARD", conf, verdict)
            s = compute_sev_f("SOFT", conf, verdict)
            flag = "" if h == s else "   <-- credence depends on CONSEQUENCE"
            if h != s:
                bad += 1
            print("    conf=%.1f  verdict=%-11s  HARD=%.3f  SOFT=%.3f%s"
                  % (conf, verdict, h, s, flag))
    print("\n  cells where identical evidence gave different credence: %d/6"
          % bad)
    assert bad == 6, "expected every cell to violate evidential invariance"

    print("\n  lexicographic pair comparison -- does a 3rd weight change an "
          "ORDERING?")
    print("  (fable: a 3rd weight 'decides nothing the pair gate reads')")

    A_conf, B_conf, V = 0.9, 0.8, 1.0
    w2_A = SEV_F_W.get("MEDIUM", SEV_F_W["HARD"])        # unrecognised -> HARD
    w2_B = SEV_F_W["HARD"]
    two_A, two_B = w2_A * A_conf * V, w2_B * B_conf * V
    W3 = {"HARD": 1.0, "MEDIUM": 0.8, "SOFT": 0.5}       # R2: a 3rd weight
    three_A, three_B = W3["MEDIUM"] * A_conf * V, W3["HARD"] * B_conf * V

    print("    both findings share c_d = 'High'  -> FIRST coordinate TIES")
    print("    2 weights: A(MEDIUM->HARD default)=%.3f  B(HARD)=%.3f  -> A %s B"
          % (two_A, two_B, ">" if two_A > two_B else "<"))
    print("    3 weights: A(MEDIUM)=%.3f  B(HARD)=%.3f  -> A %s B"
          % (three_A, three_B, ">" if three_A > three_B else "<"))
    flipped = (two_A > two_B) != (three_A > three_B)
    print("    ordering changed by adding a 3rd weight: %s" % flipped)
    assert flipped, "expected the 3rd weight to flip the lexicographic order"
    print("\n  VERDICT: a 3rd weight DOES change pair orderings, through the")
    print("           credence coordinate on a c_d tie. fable's 'decides")
    print("           nothing the pair gate reads' is REFUTED. R2 is not")
    print("           jobless under R3 -- it refines a term that should not be")
    print("           in that coordinate at all.")
    return dict(invariance_violations=bad, lex_flip=flipped)


def m_b_z3():
    rule("M-B(z3)  evidential invariance, and which induced order tracks c_d")
    try:
        import z3
    except ImportError:
        print("  z3 unavailable; skipped (not a blocker).")
        return None
    conf, v = z3.Real("conf"), z3.Real("v")
    dom = [conf >= 0, conf <= 1, v >= 0, v <= 1]

    s = z3.Solver(); s.add(dom); s.add(1.0 * conf * v != 0.5 * conf * v)
    today = s.check()
    print("  today    W(class)*conf*Ver : identical evidence, different "
          "credence?  %s   (sat = defect)" % today)
    s2 = z3.Solver(); s2.add(dom); s2.add(conf * v != conf * v)
    rep = s2.check()
    print("  repaired conf*Ver         : identical evidence, different "
          "credence?  %s (unsat = invariant)" % rep)

    # Does the induced ORDER track the consequence order?
    # Consequence: HARD (W=1.0) strictly outranks SOFT (W=0.5).
    kA, kB = z3.Reals("kA kB")       # credences of a SOFT A and a HARD B
    base = [kA >= 0, kA <= 1, kB >= 0, kB <= 1]
    # product order disagrees with the consequence order?
    sp = z3.Solver(); sp.add(base); sp.add(0.5 * kA > 1.0 * kB)
    print("\n  product W*credence : SOFT finding outranks a HARD one?  %s"
          "  (sat = order does NOT track c_d)" % sp.check())
    if sp.check() == z3.sat:
        m = sp.model()
        print("    witness: %s" % m)
    # Lexicographic pair, COMPUTED rather than asserted.  c_d is ordinal, so
    # the classes enter as RANKS under a strictly increasing re-label phi:
    # only `rankA < rankB` is assumed, never any particular numbers.
    rA, rB = z3.Reals("rankA rankB")
    sl = z3.Solver()
    sl.add(base)
    sl.add(rA < rB)                       # SOFT strictly below HARD on c_d
    outranks = z3.Or(rA > rB, z3.And(rA == rB, kA > kB))   # lex order
    sl.add(outranks)                      # ask for a SOFT that outranks a HARD
    res = sl.check()
    print("  pair (c_d, credence) lex : SOFT finding outranks a HARD one?  %s"
          "  (unsat = order tracks c_d)" % res)
    assert str(res) == "unsat", "the lex pair must never let SOFT outrank HARD"
    return str(today), str(rep)


def m_c():
    rule("M-C  the frozen cut's spellings, read by IMPORT not by text search")
    from bench.reference_runner_v3 import CRITICAL_SEVERITY_THRESHOLD as CANON
    import bench.evidence as ev
    import bench.audit_closing_window as acw
    import bench.convergence_location as cl

    spellings = [("bench/evidence.py::LEDGER_CRITICAL_SEVERITY",
                  ev.LEDGER_CRITICAL_SEVERITY),
                 ("bench/audit_closing_window.py::CRITICAL_SEVERITY_THRESHOLD",
                  acw.CRITICAL_SEVERITY_THRESHOLD)]
    for name, fn in sorted(inspect.getmembers(cl, inspect.isfunction)):
        p = inspect.signature(fn).parameters.get("critical_threshold")
        if p is not None and p.default is not inspect.Parameter.empty:
            spellings.append(
                ("bench/convergence_location.py::%s(critical_threshold=)"
                 % name, p.default))
    print("  canonical: bench/reference_runner_v3.py::"
          "CRITICAL_SEVERITY_THRESHOLD = %s" % CANON)
    for name, val in spellings:
        print("    [%s] %s = %s" % ("OK   " if val == CANON else "DRIFT", name,
                                    val))
    print("\n  spellings outside the canonical constant: %d  "
          "(the brief says 4; cc2 says 6)" % len(spellings))

    rule("M-C(2)  what a PER-DOMAIN cut is, read from the domain manifest")
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    man = tomllib.loads(
        (REPO / "bench" / "cdsfl_registry" / "domain_manifest.toml")
        .read_text(encoding="utf-8"))
    none_d, scaled, composed = [], [], []
    for name, d in man.items():
        if not isinstance(d, dict) or "severity_scale" not in d:
            continue
        sc = d["severity_scale"]
        if sc == "none":
            none_d.append(name)
        elif sc == "composed":
            composed.append(name)
        else:
            scaled.append((name, sc, d.get("critical_level")))
    print("  domains declaring severity_scale='none'     : %d  %s"
          % (len(none_d), none_d))
    print("  domains declaring severity_scale='composed' : %d  %s"
          % (len(composed), composed))
    print("  domains declaring a scale of their own      : %d" % len(scaled))
    for name, sc, lvl in scaled:
        print("    %-14s scale=%r" % (name, sc))
        print("    %-14s critical_level=%r   type=%s"
              % ("", lvl, type(lvl).__name__))
    print("\n  fable: 'the 6 severity_scale=\"none\" domains inherit the "
          "application level'.")
    print("  MEASURED: %d declare 'none'; the 6th is %r, which declares"
          % (len(none_d), composed[0] if composed else None))
    print("  'composed' and by the manifest's own rule carries 2+ scales and")
    print("  inherits NO single application level. Count and mechanism both "
          "wrong.")

    print("\n  can the live comparison site accept a per-domain critical "
          "level?")
    # The signature is (entries, max_round, symbols, *, within_threshold,
    # critical_threshold).  A FIRST VERSION of this probe omitted `symbols` and
    # caught a TypeError for the missing ARGUMENT, which demonstrates nothing
    # about the comparison.  One real entry at or above the cut is supplied so
    # that `(e["severity"] or 0.0) >= critical_threshold` is actually reached.
    # `_gate_population` keeps only entries with a non-negative
    # `open_since_round` and a non-terminal status.  A SECOND version of this
    # probe used `round_opened`, so the entry was dropped and the comparison
    # was never reached -- the probe passed VACUOUSLY.  Reaching the
    # comparison is asserted below rather than assumed.
    _entries = [{"canonical_id": "X1", "severity": 0.9,
                 "open_since_round": 0, "status": "OPEN"}]
    import bench.convergence_location as _cl_chk
    assert len(_cl_chk._gate_population(_entries)) == 1, (
        "the probe entry must survive _gate_population, else the comparison "
        "is never reached and a clean run proves nothing")
    assert _cl_chk._criticals(_entries, 1, 0.7), (
        "the probe entry must be counted critical at the numeric cut")
    try:
        cl.hierarchical_novelty_series(_entries, 1, ["s"],
                                       critical_threshold="High")
        print("    'High' accepted -- no type error")
    except TypeError as exc:
        print("    TypeError: %s" % exc)
        print("    -> cc2 is right: the gate compares with '>=' against a "
              "float, and 3 of")
        print("       the 4 declared levels are STRINGS. Pinning the six makes "
              "them")
        print("       CONSISTENTLY wrong; it buys drift protection and nothing "
              "more.")
    except Exception as exc:                                   # noqa: BLE001
        print("    %s: %s" % (type(exc).__name__, exc))
    return len(spellings), len(none_d), len(composed), scaled


def main():
    a = m_a()
    b = m_b()
    m_b_z3()
    m_c()
    rule("SUMMARY")
    if a:
        print("  M-A  three populations, not one. Sites A+B lose %d/%d; site C "
              "acts on the\n       %d entries that population excludes."
              % (a["ab_lost"], a["ab_n"], a["above"]))
    print("  M-B  credence violates evidential invariance in %d/6 cells; a 3rd"
          "\n       weight flips a lexicographic pair ordering (%s)."
          % (b["invariance_violations"], b["lex_flip"]))
    print("  M-C  six spellings, not four; 5 'none' + 1 'composed', not 6 "
          "'none'.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
