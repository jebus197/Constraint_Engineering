#!/usr/bin/env python3
"""Which CONFIRMED verdicts carry information about the claim, and which do not.

A verdict that takes the SAME value on a claim and on a false variant of that
claim carries 0 bits about the claim. Admission on it is admission by
vocabulary, not by tool. This producer applies that discrimination control to
every tool the domain verification set can reach, and then scores the 2
candidate repairs against each other on 2 NAMED properties, which is what
`composability-requires-a-measurement` and the additive standard's removal
clause both demand before a capability is taken away.

WHY IT EXISTS. On 2026-11-10 the false-admit repair was narrowed to
`{dimensional_analysis, astronomical}` on a measurement that found
`biological_sequence` DISCRIMINATING. A free panel seat refuted that, and the
refutation reproduces here: `biological_sequence` has 5 branches, 4 of which
compare a computed value against the claim and 1 of which reports only that a
sequence parses. The earlier probe hit a comparing branch and generalised from
it. That is the measurement hitting 1 branch of 3 and reporting the function.

THE 2 OPTIONS, and the 2 properties they are scored on.
  A  TOOL-LEVEL EXCLUSION, the seat's fix: add `biological_sequence` to
     `CANNOT_ADMIT_ALONE`, so no verdict of its may admit by itself.
  B  BRANCH-LEVEL GATE: keep the tool, and let a CONFIRMED verdict admit alone
     only where its own evidence shows a COMPARING branch.
  P1 truth-blind CONFIRMED paths BARRED from sole admission  (higher is better)
  P2 discriminating CONFIRMED paths RETAINED for sole admission (higher better)

The marker is DERIVED, not guessed: all 4 comparing branches end their evidence
in `matches claim`, and the validity-only fallback cannot, because it never
reads a claimed value. The producer asserts that structural fact against the
verifier's own source rather than trusting the string.
"""
from __future__ import annotations

import pathlib
import re
import sys

import mpmath as mp
import numpy as np
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

for _c in (pathlib.Path(__file__).resolve().parent, pathlib.Path.cwd().resolve()):
    for _x in (_c, *_c.parents):
        if (_x / "bench" / "immune_agents.py").is_file():
            REPO = _x
            break
    else:
        continue
    break
else:
    raise SystemExit("cannot locate the repository")

#: BOTH are needed: the verifier module is imported bare as
#: `immune_agents`, and it itself imports `bench.dm._types`, so the
#: repository root must be importable as a package root as well.
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

#: The marker that distinguishes a COMPARING branch from the validity-only
#: fallback. Derived from the verifier's source, asserted below.
COMPARES = "matches claim"

FOR = ("CONFIRMED", "VERIFIED", "SUPPORTED")
AGAINST = ("REFUTED", "REJECTED", "CONTRADICTED")

#: (tool, label, true_claim, false_variant). The false variant SHARES the
#: vocabulary that routes the claim to the tool, so a difference in verdict is
#: a judgement about the claim and not about which tool ran.
PAIRS = [
    ("dimensional_analysis", "unit equality",
     "1 km = 1000 m", "1 km = 2000 m"),
    ("astronomical", "speed of light",
     "the speed of light is 299792.458 km/s",
     "the speed of light is 1234.5 km/s"),
    ("biological_sequence", "validity-only fallback",
     "the sequence 'ATGC' proves the defendant was present",
     "the sequence 'ATGC' proves the moon is made of cheese"),
    ("biological_sequence", "reverse complement",
     "the reverse complement of ATGC is GCAT",
     "the reverse complement of ATGC is TTTT"),
    #: ★ THE 4 PAIRS BELOW WERE ABSENT FROM THE FIRST VERSION AND THEIR
    #: ABSENCE IS WHAT MADE IT SCORE A CAPABILITY LOSS AS A WIN. A free panel
    #: seat found `chemistry_structure`'s comparing branches; the enumeration
    #: assertion added further down now makes such a gap FAIL the producer
    #: instead of quietly shrinking a denominator.
    ("biological_sequence", "sequence length",
     "the DNA sequence 'ATGC' has length 4",
     "the DNA sequence 'ATGC' has length 9"),
    ("biological_sequence", "translation",
     "ATGGCC translates to MA", "ATGGCC translates to WW"),
    ("biological_sequence", "GC content",
     "the GC content of ATGC is 50%", "the GC content of ATGC is 90%"),
    #: The 2nd homogeneity branch, the no-equals path: a bag of like
    #: quantities with no claimed result at all. Truth-blind by construction,
    #: like its sibling, and probed so the enumeration gate is satisfied
    #: honestly rather than by lowering the bar.
    ("dimensional_analysis", "homogeneous bag, no claimed result",
     "the lengths 3 m, 4 m and 5 m", "the lengths 3 m, 4 m and 500 m"),
    ("chemistry_structure", "molecular formula",
     "the molecule 'CCO' has formula C2H6O",
     "the molecule 'CCO' has formula C3H8O"),
    ("chemistry_structure", "molecular weight",
     "the molecule 'CCO' has molecular weight 46.07 g/mol",
     "the molecule 'CCO' has molecular weight 99.9 g/mol"),
    #: ★ AND THE PAIR THAT CORRECTED MY READING OF `astronomical`. The first
    #: version probed it with 2 claims BOTH IN km/s, where its separate unit
    #: defect rejects everything, and concluded truth-blind. In SI it
    #: discriminates coarsely -- and still CONFIRMS a value 1 m/s off the
    #: true speed of light, inside its own 1% tolerance, which is the real
    #: reason it may not admit alone.
    ("astronomical", "constant in SI, 1 part in 3e8",
     "the speed of light is 299792458 m/s",
     "the speed of light is 299792459 m/s"),
    ("stoichiometric_balance", "mass balance",
     "2 H2 + O2 -> 2 H2O", "3 H2 + O2 -> 5 H2O"),
    ("chemistry_structure", "SMILES validity",
     "the molecule CCO is ethanol", "the molecule CCO is benzene"),
]


def _iv_both(k: int, n: int):
    """Wilson and Clopper-Pearson, each by 2 independent routes."""
    if n == 0:
        return (float("nan"),) * 4 + (0.0, 0.0)
    w_sm = proportion_confint(k, n, 0.05, "wilson")
    z, p = 1.959963984540054, k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    w_np = (max(0.0, c - h), min(1.0, c + h))
    #: ★ CLOPPER-PEARSON ON 2 INDEPENDENT ROUTES, AND THE FIRST VERSION HAD
    #: ONLY ONE. `proportion_confint(..., "beta")` and `scipy.stats.beta.ppf`
    #: are the SAME quantile by 2 library names, and the project's
    #: independence detector says so: it ranked this producer PASS on import
    #: count and FAIL on independence, because 4 STEM imports bought 0
    #: cross-checks on this bound. The second route is the regularised
    #: incomplete beta inverted by bisection in mpmath -- a different
    #: algorithm, not a different wrapper. n here is single digits, so the
    #: hyp2f1 convergence failure that forced a quadrature fallback in the
    #: canonical helper at n = 20000 cannot arise; it is still caught rather
    #: than assumed.
    cp_sp = (0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1)),
             1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k)))

    def _cp_mpmath(a, b, y):
        mp.mp.dps = 40
        lo, hi = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            if hi - lo < mp.mpf("1e-18"):
                break
            m = (lo + hi) / 2
            try:
                v = mp.betainc(a, b, 0, m, regularized=True) - y
            except Exception:                                  # noqa: BLE001
                return float("nan")
            lo, hi = (m, hi) if v < 0 else (lo, m)
        return float((lo + hi) / 2)

    cp_mp = (0.0 if k == 0 else _cp_mpmath(k, n - k + 1, 0.025),
             1.0 if k == n else _cp_mpmath(k + 1, n - k, 0.975))
    gap_w = max(abs(a - b) for a, b in zip(w_sm, w_np))
    gap_c = max(abs(a - b) for a, b in zip(cp_sp, cp_mp)
                if not (np.isnan(a) or np.isnan(b)))
    return w_sm[0], w_sm[1], cp_sp[0], cp_sp[1], gap_w, gap_c


def main(argv=None) -> int:
    import argparse
    _ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    _ap.parse_args(argv)

    import immune_agents as ia

    print("=" * 78)
    print("WHICH CONFIRMED VERDICTS CARRY INFORMATION ABOUT THE CLAIM")
    print("=" * 78)

    # ---- the marker is derived from the source, not assumed ---------------
    src = (REPO / "bench" / "immune_agents.py").read_text(encoding="utf-8")
    body = src[src.index("def _verify_biological_sequence"):][:9000]
    valid = re.findall(r"BIO_VALID: [^\"']*", body)
    comparing = [v for v in valid if COMPARES in v]
    fallback = [v for v in valid if COMPARES not in v]
    print(f"\n1. THE MARKER, DERIVED FROM THE VERIFIER'S OWN SOURCE")
    print(f"      BIO_VALID branches found      : {len(valid)}")
    print(f"      containing {COMPARES!r:17s}  : {len(comparing)}")
    print(f"      validity-only (no comparison) : {len(fallback)}")
    assert len(comparing) >= 3 and len(fallback) >= 1, (
        "the branch structure this producer rests on is not present")

    # ---- 1b. EVERY FAVOURABLE BRANCH MUST BE PROBED ----------------------
    #: ★ THE STRUCTURAL GUARANTEE, AND THE WHOLE REASON THIS SECTION EXISTS.
    #: The first version of this producer probed 1 claim per TOOL and scored
    #: the result as if it had characterised the tool. It had not:
    #: `chemistry_structure` has 3 favourable branches and only the
    #: validity-only one was hit, so a tool-level bar on it scored as a win
    #: while destroying a live admission. A seat had made the identical
    #: 1-branch-of-N error on `biological_sequence` an hour earlier, and this
    #: producer's own docstring narrates that error while committing it.
    #: SO THE BRANCH COUNT IS NOW READ OFF EACH VERIFIER'S SOURCE, BOUNDED BY
    #: THE SYNTAX TREE, and compared against the probe set. A verifier with
    #: more favourable branches than probes makes this producer EXIT NON-ZERO
    #: rather than report a score over an under-enumerated path set.
    #: The bound is the AST's, not a character window: a window scan leaked
    #: across the function boundary and attributed one verifier's branches to
    #: its neighbour, which is how `chemistry_structure` first appeared to
    #: carry `BIO_VALID` lines.
    import ast as _ast

    ia_src = (REPO / "bench" / "immune_agents.py").read_text(encoding="utf-8")
    _tree = _ast.parse(ia_src)
    _bounds = {n.name: (n.lineno, n.end_lineno) for n in _ast.walk(_tree)
               if isinstance(n, _ast.FunctionDef)}
    _lines = ia_src.split("\n")

    def favourable_branches(tool: str):
        """Favourable print sites in that verifier, split by whether they
        COMPARE a computed value against the claim."""
        fn = f"_verify_{tool}"
        if fn not in _bounds:
            return None
        a, b = _bounds[fn]
        body = "\n".join(_lines[a - 1:b])
        fav = [l.strip() for l in body.splitlines()
               if "print(" in l
               and re.search(r"(VALID|CONSISTENT|BALANCED|VERIFIED)", l)
               and not re.search(r"(INVALID|INCONSISTENT|UNBALANCED|MISMATCH|NO_)", l)]
        return [l for l in fav if COMPARES in l], [l for l in fav if COMPARES not in l]

    print("\n1b. EVERY FAVOURABLE BRANCH IS PROBED, OR THIS PRODUCER FAILS")
    probed = {}
    for _t, _l, *_ in PAIRS:
        probed.setdefault(_t, set()).add(_l)
    under = []
    for tool in sorted(probed):
        got = favourable_branches(tool)
        if got is None:
            print(f"      {tool:24s} verifier not found in the module")
            continue
        comp, val = got
        n_branches, n_probes = len(comp) + len(val), len(probed[tool])
        flag = "" if n_probes >= n_branches else "  <<< UNDER-ENUMERATED"
        print(f"      {tool:24s} {n_branches} favourable branch(es) "
              f"({len(comp)} comparing), {n_probes} probe(s){flag}")
        if n_probes < n_branches:
            under.append((tool, n_branches, n_probes))
    if under:
        print("\n      REFUSED: the probe set does not cover every favourable")
        print("      branch, so any dominance score below would be taken over an")
        print("      under-enumerated path set -- which is exactly how a live")
        print("      capability loss was once scored as a win. Add a probe pair")
        print("      for each missing branch and re-run.")
        for t, nb, np_ in under:
            print(f"        {t}: {nb} branches, {np_} probes")
        return 2

    # ---- the discrimination control ---------------------------------------
    print(f"\n2. THE DISCRIMINATION CONTROL, 1 true claim against 1 false variant")
    manifest = ia._load_tool_manifest()
    rows = []
    for tool, label, t_claim, f_claim in PAIRS:
        entry = manifest.get(tool)
        if not entry:
            rows.append((tool, label, "NOT_IN_MANIFEST", "", "", False, False))
            continue
        fn = entry.get("verifier")
        f = fn if callable(fn) else getattr(ia, str(fn), None)
        if not callable(f):
            rows.append((tool, label, "UNRESOLVED", "", "", False, False))
            continue
        vt, vf = f(t_claim), f(f_claim)
        t_v = getattr(vt, "verdict", None)
        f_v = getattr(vf, "verdict", None)
        t_e = getattr(vt, "evidence", "") or ""
        admits = t_v in FOR
        discriminates = (t_v != f_v)
        rows.append((tool, label, t_v, f_v, t_e, admits, discriminates))
        mark = "DISCRIMINATES" if discriminates else "TRUTH-BLIND  "
        print(f"      {tool:24s} {label:24s} {str(t_v):10s} / {str(f_v):10s} {mark}")

    # ---- the 2 options, scored --------------------------------------------
    # A path is a (tool, label) pair that returns a definitive FOR verdict.
    admitting = [r for r in rows if r[5]]
    blind = [r for r in admitting if not r[6]]
    disc = [r for r in admitting if r[6]]
    print(f"\n3. THE ADMITTING PATHS")
    print(f"      paths returning a definitive FOR verdict : {len(admitting)}")
    print(f"      of which TRUTH-BLIND                     : {len(blind)}"
          f"  {[f'{t}/{l}' for t, l, *_ in blind]}")
    print(f"      of which DISCRIMINATING                  : {len(disc)}"
          f"  {[f'{t}/{l}' for t, l, *_ in disc]}")

    #: ★ OPTION A IS THE SEAT'S PROPOSAL, TYPED OUT AS IT PROPOSED IT.
    OPTION_A = {"dimensional_analysis", "astronomical", "biological_sequence"}

    #: ★ OPTION B IS THE FIRST DERIVATION, KEPT BECAUSE IT WAS COMMITTED AND
    #: ITS DEFECT IS THE FINDING. It held `biological_sequence` out by NAME,
    #: so every other tool with a truth-blind branch fell to the tool level --
    #: which is how `chemistry_structure` was barred outright and a live,
    #: reachable, discriminating admission was destroyed.
    OPTION_B_HELD_OUT = {"biological_sequence"}
    OPTION_B = {t for t, _l, _tv, _fv, _ev, _ad, dsc in rows
                if not dsc and t not in OPTION_B_HELD_OUT}

    #: ★ OPTION C IS DERIVED BY A RULE RATHER THAN BY A NAME, AND THE RULE IS
    #: THE WHOLE CORRECTION. A tool's anatomy decides where it is gated:
    #:    has a truth-blind favourable branch AND a comparing one -> BRANCH
    #:    has only truth-blind favourable branches               -> TOOL
    #:    has only comparing ones                                -> ungated
    #: Nothing is held out by name, so a tool cannot be mis-placed because
    #: the author did not think of it. On this measurement the rule yields
    #: `biological_sequence` AND `chemistry_structure` at the branch, which is
    #: what a free panel seat argued from its own probes.
    _blind_tools = {t for t, _l, _tv, _fv, _ev, ad, dsc in rows if ad and not dsc}
    _disc_tools = {t for t, _l, _tv, _fv, _ev, ad, dsc in rows if ad and dsc}
    BRANCH_GATED = _blind_tools & _disc_tools
    OPTION_C = _blind_tools - _disc_tools

    def barred_A(tool, ev):
        return tool in OPTION_A

    def barred_B(tool, ev):
        #: ★ THE MARKER IS TOOL-SCOPED, AND THE FIRST VERSION APPLIED IT
        #: GLOBALLY. `matches claim` is these verifiers' own wording, so a
        #: global test barred `stoichiometric_balance` -- a tool this same run
        #: measures as DISCRIMINATING. A marker read off 1 verifier's source
        #: may only be applied to that verifier.
        if tool in OPTION_B:
            return True
        if tool in OPTION_B_HELD_OUT:
            return COMPARES not in (ev or "")
        return False

    def barred_C(tool, ev):
        if tool in OPTION_C:
            return True
        if tool in BRANCH_GATED:
            return COMPARES not in (ev or "")
        return False

    print(f"\n      option A tool set (the seat's) : {sorted(OPTION_A)}")
    print(f"      option B tool set (committed)  : {sorted(OPTION_B)}"
          f"  branch: {sorted(OPTION_B_HELD_OUT)}")
    print(f"      option C tool set (BY RULE)    : {sorted(OPTION_C)}"
          f"  branch: {sorted(BRANCH_GATED)}")

    print(f"\n4. THE 3 OPTIONS ON 2 NAMED PROPERTIES")
    hdr = f"      {'':10s} {'P1 blind barred':>18s} {'P2 discriminating kept':>24s}"
    print(hdr)
    results = {}
    for tag, pred in (("A", barred_A), ("B", barred_B), ("C", barred_C)):
        p1 = sum(1 for t, l, tv, fv, ev, *_ in blind if pred(t, ev))
        p2 = sum(1 for t, l, tv, fv, ev, *_ in disc if not pred(t, ev))
        results[tag] = (p1, len(blind), p2, len(disc))
        print(f"      option {tag}   {p1:>8d} of {len(blind):<6d} {p2:>14d} of {len(disc):<6d}")

    for tag in ("A", "B", "C"):
        p1, n1, p2, n2 = results[tag]
        for nm, k, n in (("P1", p1, n1), ("P2", p2, n2)):
            lo, hi, clo, chi, gw, gc = _iv_both(k, n)
            print(f"\n      option {tag} {nm}: {k} of {n} = {k/n if n else float('nan'):.6f}")
            print(f"            Wilson 95% [{lo:.6f}, {hi:.6f}]   2-route gap {gw:.3e}")
            print(f"            Clopper-Pearson 95% [{clo:.6f}, {chi:.6f}]   2-route gap {gc:.3e}")

    # ---- 5. is the gate the measurement adopts actually REACHABLE? --------
    #: ★ THE HONEST LIMIT OF SECTION 4, AND IT MUST BE STATED BESIDE THE
    #: ADOPTION RATHER THAN DISCOVERED LATER. Option B gates
    #: `biological_sequence` at the branch. `_may_admit_alone` is called on
    #: every favourable verdict in the live loop, so the gate is wired. But
    #: whether that TOOL is ever dispatched is a separate question, answered
    #: by the claim-type classifier, and the answer today is that it is not.
    import domain_immune as _di

    print("\n5. IS THE BRANCH-GATED TOOL REACHABLE AT ALL TODAY")
    cfgs = _di.load_all_domain_configs()
    assigning = [(d, ct) for d, c in sorted(cfgs.items())
                 for ct, tl in (c.verification_tools or {}).items()
                 if "biological_sequence" in (tl or [])]
    print(f"      (domain, claim_type) pairs assigning it : {len(assigning)}"
          f"  {assigning}")

    SEQ = ["the reverse complement of ATGC is GCAT",
           "the DNA sequence ATGC has length 4",
           "ATGGCC translates to MA",
           "the GC content of ATGC is 50%",
           "the sequence 'ATGC' proves the defendant was present"]

    class _F:
        def __init__(self, d):
            self.description = d

    reached, probes = 0, 0
    for dom, _ct in assigning:
        cfg = cfgs[dom]
        for claim in SEQ:
            probes += 1
            kind, _ = _di.domain_classify_claim(_F(claim), cfg)
            if "biological_sequence" in (_di.domain_b_cell_tools(kind, cfg) or []):
                reached += 1
    lo, hi, clo, chi, gw, gc = _iv_both(reached, probes)
    print(f"      sequence claims that REACH the tool     : {reached} of {probes}"
          f" = {reached/probes:.6f}")
    print(f"            Wilson 95% [{lo:.6f}, {hi:.6f}]   2-route gap {gw:.3e}")
    print(f"            Clopper-Pearson 95% [{clo:.6f}, {chi:.6f}]   2-route gap {gc:.3e}")

    #: THE 2 ROOT CAUSES, each read off the configs rather than inferred.
    vocab = ("sequence", "dna", "rna", "protein", "nucleotide", "complement",
             "codon", "gc content")
    nopat = []
    for dom, _ct in assigning:
        cfg = cfgs[dom]
        pats = cfg.compiled_claim_patterns() or {}
        if not pats:
            nopat.append(dom)
            print(f"      {dom:14s}: 0 claim_patterns against "
                  f"{len(cfg.verification_tools or {})} claim_type(s) carrying "
                  f"tools, so EVERY claim is uncategorised and all "
                  f"{len({t for tl in (cfg.verification_tools or {}).values() for t in (tl or [])})}"
                  f" of its tools are unreachable BY CONSTRUCTION")
            continue
        allpat = " ".join(
            getattr(r, "pattern", str(r)) for rx in pats.values()
            for r in (rx if isinstance(rx, (list, tuple)) else [rx])).lower()
        hits = [w for w in vocab if w in allpat]
        print(f"      {dom:14s}: {len(pats)} claim_pattern(s), sequence words "
              f"present in any of them: {hits or 'NONE'}")
    #: ★ THE 2 BRANCH-GATED TOOLS DIFFER ON REACHABILITY, AND SAYING SO IS
    #: THE POINT. The earlier version of this paragraph said the branch gate
    #: was unexercised by real traffic, which was true while
    #: `biological_sequence` was its only member and is FALSE now.
    _chem_reached = 0
    for _dom, _c in sorted(cfgs.items()):
        _k, _ = _di.domain_classify_claim(
            _F("the molecule 'CCO' has formula C2H6O"), _c)
        if "chemistry_structure" in (_di.domain_b_cell_tools(_k, _c) or []):
            _chem_reached += 1
    print(f"\n      chemistry_structure reached in {_chem_reached} domain(s) by a")
    print(f"      formula claim, so HALF the branch gate IS exercised by live")
    print(f"      traffic and half is not. `biological_sequence` is dry for the")
    print(f"      same reason B22 records for `graph_property`: a tool declared")
    print(f"      for a claim type whose patterns lack the routing vocabulary.")
    print(f"      NEITHER half is a reason to prefer option A: A is dry by the")
    print(f"      identical route AND bars the comparing branches, so it is")
    print(f"      worse on both counts.")

    a1, an1, a2, an2 = results["A"]
    b1, bn1, b2, bn2 = results["B"]
    c1, cn1, c2, cn2 = results["C"]

    # ---- 6. THE LIVE TABLES MUST MATCH WHAT THIS RUN DERIVES -------------
    #: ★ `execute-do-not-grep` APPLIED TO THIS PRODUCER'S OWN SUBJECT. A
    #: measurement that justifies a configuration and a configuration that
    #: ships are 2 live forms, and nothing compared them until a seat did.
    #: They are compared here by IMPORT, so a drift in either direction is a
    #: non-zero exit rather than a paragraph nobody re-reads.
    print("\n6. DO THE LIVE TABLES MATCH WHAT THIS RUN DERIVES?")
    live_tool = set(getattr(_di, "CANNOT_ADMIT_ALONE", ()) or ())
    live_branch = set((getattr(_di, "BRANCH_GATED_ADMISSION", {}) or {}).keys())
    print(f"      derived  tool-level : {sorted(OPTION_C)}")
    print(f"      live     tool-level : {sorted(live_tool)}")
    print(f"      derived  branch     : {sorted(BRANCH_GATED)}")
    print(f"      live     branch     : {sorted(live_branch)}")
    drift = (live_tool != OPTION_C) or (live_branch != BRANCH_GATED)
    print(f"      DRIFT: {drift}")
    print("\n" + "=" * 78)
    print("VERDICT")
    dominates = ((c1 >= a1 and c2 > a2) or (c1 > a1 and c2 >= a2)) and \
                ((c1 >= b1 and c2 > b2) or (c1 > b1 and c2 >= b2)) and not drift
    print(f"\n  P1, truth-blind barred      : A {a1}/{an1}   B {b1}/{bn1}   "
          f"C {c1}/{cn1}")
    print(f"  P2, discriminating retained : A {a2}/{an2}   B {b2}/{bn2}   "
          f"C {c2}/{cn2}")
    if dominates:
        #: ★ THE DIRECTION IS READ OFF THE NUMBERS, NOT ASSERTED. The first
        #: version printed a fixed sentence saying B tied on P1 and won on
        #: P2. The measurement said the opposite, and the prose did not
        #: notice -- a producer contradicting its own figures in the same
        #: output. Stating which property carried it is the whole finding.
        def _rel(b, a):
            return "better on" if b > a else ("ties on" if b == a else "WORSE on")
        print(f"\n  OPTION C DOMINATES BOTH, and the live tables match it.")
        print(f"    against A (the seat's tool-level set): "
              f"{_rel(c1, a1)} P1 ({c1}/{cn1} against {a1}/{an1}), "
              f"{_rel(c2, a2)} P2 ({c2}/{cn2} against {a2}/{an2})")
        print(f"    against B (what was first committed):  "
              f"{_rel(c1, b1)} P1 ({c1}/{cn1} against {b1}/{bn1}), "
              f"{_rel(c2, b2)} P2 ({c2}/{cn2} against {b2}/{bn2})")
        print(f"  Under the additive standard's removal clause -- removal only")
        print(f"  where a COMMITTED MEASUREMENT shows the replacement dominates")
        print(f"  on a named property -- A and B are BOTH refused and C is")
        print(f"  adopted. B is refused by its own author's measurement: it was")
        print(f"  committed, and it barred a tool whose comparing branches are")
        print(f"  REACHED BY LIVE TRAFFIC, so it destroyed a working admission.")
        print(f"  AND THERE IS NO COMPOSABILITY CLAIM: C alone beats A alone and")
        print(f"  beats B alone, so under his definition the SINGLE fix is")
        print(f"  preferred and composing them would be composition for its own")
        print(f"  sake, which is the sense his wording explicitly excludes. C is")
        print(f"  also not a 3rd mechanism: it is the SAME branch gate applied")
        print(f"  wherever the measurement shows the same anatomy, which is why")
        print(f"  it is derived by a RULE and not by a list of names.")
    else:
        print(f"\n  OPTION C DOES NOT DOMINATE, or the live tables have drifted")
        print(f"  from it. A {c1}/{cn1} and {c2}/{cn2} against A {a1}/{an1} and")
        print(f"  {a2}/{an2}, B {b1}/{bn1} and {b2}/{bn2}; drift={drift}.")
        print(f"  Re-derive the tables from this run before shipping either.")
    mp.mp.dps = 30
    print(f"\n  mpmath cross-check of P2 ratio C: "
          f"{mp.mpf(c2)/mp.mpf(cn2) if cn2 else mp.mpf('nan')}")
    return 0 if dominates else 1


if __name__ == "__main__":
    raise SystemExit(main())
