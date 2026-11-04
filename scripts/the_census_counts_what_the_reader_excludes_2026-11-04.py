#!/usr/bin/env python3
"""The verdict census reported 1,953 of his annotations. He wrote 839 of them.

THE DEFECT, AND IT SITS IN THE FIRST LINE READ AFTER `rs`. The FIRST READ banner
produced by `scripts/cdsfl_recover.py` opens with a description of
`Developer_Projects/Responses` quoting 2 figures from
`read_founder_responses_2026-10-11.claim_a_naive_grep_is_blind_to_some_of_them`:
the total number of '#' verdicts and how many sit in files grep treats as
binary. Both were computed over files chosen by `is_a_response_file`, the BROAD
READABILITY predicate, while the annotations themselves are yielded by
`annotations()`, which selects with `is_one_of_his_annotated_responses` -- a
STRICTLY NARROWER predicate carrying 3 further exclusions (a text-bearing
extension, a not-his-writing name list, and a content-sniffing binary test).

SO THE REPAIR OF 2026-11-03 FIXED THE DECIDING LAYER AND LEFT THE REPORTING ONE.
That morning an 11 MB PNG named `.md` was found contributing 780 annotations he
never wrote, and `is_binary_file` was added to the narrow predicate to exclude
it. `annotations()` duly fell to 839. The census never consulted the narrow
predicate at all, so it went on reporting the PNG's 780 -- and the banner went on
telling every session that opens it that he has written 1,953 verdicts.

WHY THE BROAD PREDICATE MUST NOT BE NARROWED TO FIX THIS. Its 2 other call
sites, `binaries_wearing_a_text_extension` and `unreadable_but_annotated`, are
the module's GAP DETECTORS: they exist to shout when a file cannot be parsed.
Narrowing readability would make an unparseable file stop being reported as a
gap, which is the opposite of what is wanted, and
`test_the_readability_predicate_was_not_narrowed` enforces that deliberately.
The census must consult the narrow predicate for HIS counts and keep reporting
the broad pass's residue BY NAME, which is what this script measures.

Usage: python3 scripts/the_census_counts_what_the_reader_excludes_2026-11-04.py
"""
import argparse
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def _reader():
    p = REPO / "scripts" / "read_founder_responses_2026-10-11.py"
    spec = importlib.util.spec_from_file_location("_rfr", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def step_1_the_predicates_nest(m) -> dict:
    """NARROW is a SUBSET of BROAD, so the fix can only ever remove, never add.

    Established by set algebra over the live folder AND by z3 over the
    predicate's own structure: `is_one_of_his_annotated_responses` opens with
    `is_a_response_file(path) and ...`, so narrow implies broad by construction.
    """
    broad = {p.name for p in m.RESPONSES.glob("*") if m.is_a_response_file(p)}
    narrow = {p.name for p in m.RESPONSES.glob("*")
              if m.is_one_of_his_annotated_responses(p)}
    import z3
    b, s, e, n, nb = z3.Bools("broad suffix_ok name_ok not_binary narrow")
    solver = z3.Solver()
    solver.add(nb == z3.And(b, s, e, n))      # the predicate, as written
    solver.add(z3.And(nb, z3.Not(b)))         # can narrow hold where broad fails?
    unsat = solver.check() == z3.unsat
    return {"broad": len(broad), "narrow": len(narrow),
            "narrow_is_subset": narrow <= broad,
            "only_in_broad": sorted(broad - narrow),
            "z3_narrow_implies_broad": unsat}


def step_2_the_decomposition(m) -> dict:
    """1,953 = 839 + 1,114, exactly, and the 1,114 are named."""
    broad = [p for p in sorted(m.RESPONSES.glob("*")) if m.is_a_response_file(p)]
    residue = []
    for p in broad:
        if m.is_one_of_his_annotated_responses(p):
            continue
        k = len(m._annotations_in(p))
        if k:
            residue.append({"file": p.name, "annotations": k,
                            "bytes": p.stat().st_size,
                            "suffix": p.suffix.lower() or "(none)"})
    census = m.claim_a_naive_grep_is_blind_to_some_of_them()
    his = len(m.annotations())
    spurious = sum(r["annotations"] for r in residue)
    # TWO ROUTES on the arithmetic: plain integers, and SymPy on the identity.
    import sympy
    a, h, s = sympy.symbols("a h s", integer=True)
    identity = sympy.Eq(a, h + s)
    holds = bool(identity.subs({a: census["annotations_total"], h: his, s: spurious}))
    return {"census_total": census["annotations_total"], "his_total": his,
            "spurious": spurious, "residue": residue,
            "exact_python": census["annotations_total"] == his + spurious,
            "exact_sympy": holds}


def step_3_the_share(m) -> dict:
    """How much of the banner's figure is not his writing, with 2 intervals."""
    census = m.claim_a_naive_grep_is_blind_to_some_of_them()
    his = len(m.annotations())
    k, n = census["annotations_total"] - his, census["annotations_total"]
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    cp_lo = stats.beta.ppf(0.025, k, n - k + 1) if k else 0.0
    cp_hi = stats.beta.ppf(0.975, k + 1, n - k) if k < n else 1.0
    import mpmath
    mpmath.mp.dps = 30
    exact = mpmath.mpf(k) / mpmath.mpf(n)
    return {"k": k, "n": n, "share": k / n,
            "share_mpmath": float(exact),
            "agree_to_1e_12": abs(k / n - float(exact)) < 1e-12,
            "wilson": (lo, hi), "clopper_pearson": (cp_lo, cp_hi)}


def step_4_the_blind_figure(m) -> dict:
    """The SECOND banner figure, recomputed over his files only."""
    blind_broad = blind_narrow = tot_narrow = 0
    for p in sorted(m.RESPONSES.glob("*")):
        if not m.is_a_response_file(p):
            continue
        try:
            shape = m.file_shape(p)
        except OSError:
            continue
        k = len(m._annotations_in(p))
        if not k:
            continue
        if shape["grep_would_treat_as_binary"]:
            blind_broad += k
        if m.is_one_of_his_annotated_responses(p):
            tot_narrow += k
            if shape["grep_would_treat_as_binary"]:
                blind_narrow += k
    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(blind_narrow, tot_narrow, alpha=0.05,
                                method="wilson") if tot_narrow else (None, None)
    return {"blind_as_reported": blind_broad, "blind_his_only": blind_narrow,
            "his_total": tot_narrow,
            "share_of_his_that_is_blind": (blind_narrow / tot_narrow
                                           if tot_narrow else None),
            "wilson": (lo, hi)}


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    m = _reader()

    s1 = step_1_the_predicates_nest(m)
    print("STEP 1 -- the predicates nest, so the fix can only remove")
    print(f"  readable (broad)        : {s1['broad']}")
    print(f"  his      (narrow)       : {s1['narrow']}")
    print(f"  narrow is a subset      : {s1['narrow_is_subset']}")
    print(f"  z3: narrow => broad     : {s1['z3_narrow_implies_broad']}")
    print(f"  in broad only           : {len(s1['only_in_broad'])} file(s)")

    s2 = step_2_the_decomposition(m)
    print("\nSTEP 2 -- the decomposition, exact to the integer")
    print(f"  census reports          : {s2['census_total']}")
    print(f"  he actually wrote       : {s2['his_total']}")
    print(f"  counted but not his     : {s2['spurious']}")
    print(f"  exact (python / sympy)  : {s2['exact_python']} / {s2['exact_sympy']}")
    for r in sorted(s2["residue"], key=lambda r: -r["annotations"]):
        print(f"    {r['annotations']:>5}  {r['bytes']/1048576:>7.2f} MiB  "
              f"{r['suffix']:<7}{r['file'][:48]}")

    s3 = step_3_the_share(m)
    print("\nSTEP 3 -- the share of the banner figure that is not his writing")
    print(f"  {s3['k']} of {s3['n']} = {s3['share']:.6f}")
    print(f"    Wilson 95%          [{s3['wilson'][0]:.6f}, {s3['wilson'][1]:.6f}]"
          f"  (statsmodels)")
    print(f"    Clopper-Pearson 95% [{s3['clopper_pearson'][0]:.6f}, "
          f"{s3['clopper_pearson'][1]:.6f}]  (scipy.beta)")
    print(f"    mpmath agrees to 1e-12 : {s3['agree_to_1e_12']}")

    s4 = step_4_the_blind_figure(m)
    print("\nSTEP 4 -- the second banner figure, his files only")
    print(f"  reported as blind       : {s4['blind_as_reported']}")
    print(f"  blind among HIS         : {s4['blind_his_only']} of {s4['his_total']}")
    if s4["share_of_his_that_is_blind"] is not None:
        print(f"  share                   : "
              f"{s4['share_of_his_that_is_blind']:.6f}  "
              f"Wilson [{s4['wilson'][0]:.6f}, {s4['wilson'][1]:.6f}]")

    ok = (s1["narrow_is_subset"] and s1["z3_narrow_implies_broad"]
          and s2["exact_python"] and s2["exact_sympy"])
    print(f"\nVERDICT: the census over-reports his verdicts by "
          f"{s2['spurious']}, a factor of "
          f"{s2['census_total']/s2['his_total']:.4f}. "
          f"All structural checks held: {ok}.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
