#!/usr/bin/env python3
"""Counting STEM imports ranks a producer's rigour nearly backwards.

THE AUDIT THAT PRODUCED THIS. On 2026-11-03 this session's 5 new producers were
audited against `sy` by counting how many of SymPy, z3, NumPy, SciPy,
statsmodels, mpmath, uncertainties, pint, astropy, PuLP and pandas each imports.
1 scored 0 and was reported as a violation; 4 scored 2 or 3 and passed.

THE PREDICATE WAS A PROXY, AND THE PROJECT HAD ALREADY MEASURED WHY. The
primary/secondary falsifier rule of 2026-10-31 turns on INDEPENDENCE, not count:
a secondary counts only where it is a different independence class and not the
same verifier function. Its own measurement records that `statsmodels` and
`scipy` both resolve to the identical verifier `_verify_statistical`, so the
canonical 2-tool statistical pair was 1 function called twice, and that every
same-formulation cross-check agreed to machine precision and caught nothing
while all 3 errors actually caught came from a different ROUTE to the quantity.

SO THE RIGHT QUESTION IS ROUTES PER QUANTITY, and 2 libraries computing 2
DIFFERENT intervals is not a cross-check of either one. Wilson from statsmodels
beside Clopper-Pearson from scipy is 2 quantities on 1 route each, which scores
2 by import count and 0 by the rule.

WHAT THIS SCRIPT ESTABLISHES, per `measured-rate-travels-with-its-script`,
because the reversals were stated to the founder before any producer existed.

NO RANK CORRELATION IS REPORTED. With 5 producers a correlation coefficient
cannot carry weight and would be the flattering-measure failure the record
already names 3 times. The reversals are named individually instead, each one
checkable by rerunning this script.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]
STEM = ("sympy", "z3", "numpy", "scipy", "statsmodels", "mpmath",
        "uncertainties", "pint", "astropy", "pulp", "pandas")

#: The producers written in the session that ran this audit. These are named
#: because the audit's subject was this session's own work.
SESSION_PRODUCERS = [
    "a_models_own_verified_flag_closes_it_2026-11-03",
    "a_bare_clock_was_dated_from_the_mtime_2026-11-03",
    "what_a_self_reported_v_bar_is_worth_2026-11-03",
    "c0001_provenance_does_not_reconcile_2026-11-03",
    "b96_the_report_against_the_note_standard_2026-11-03",
]


def population(rev: str | None) -> list[str]:
    """Every script defining an `_iv` interval helper, plus this session's own.

    THE FIRST VERSION HARD-CODED 6 NAMES AND THAT WAS A HAND-PICKED SAMPLE
    REPORTED AS COVERAGE -- the same defect as
    `feedback_my_instruments_are_the_weak_point`'s 2026-11-03 entry, committed
    hours earlier in this same session. It missed
    `does_the_register_need_a_forum_2026-11-02`, which this session REPAIRED
    while the list that justified the repair never examined it. So the `_iv`
    population is DISCOVERED: a file defining a function by that name is in
    scope whether or not anyone remembered it.
    """
    # THE DETECTOR MUST NOT DETECT ITSELF. This file necessarily contains the
    # literal it searches for and the regexes it matches with, so discovery
    # found it, reported it as a producer, and classified it as single-route
    # Clopper-Pearson because its own pattern text holds `betainc`. That is
    # `feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02`,
    # which that memory records as having fired twice already.
    me = pathlib.Path(__file__).stem
    names = list(SESSION_PRODUCERS)
    if rev is None:
        found = sorted(f.stem for f in (REPO / "scripts").glob("*.py")
                       if "def _iv" in f.read_text(errors="replace"))
    else:
        r = subprocess.run(["git", "ls-tree", "-r", "--name-only", rev,
                            "scripts/"], capture_output=True, text=True,
                           cwd=str(REPO))
        found = []
        for rel in (r.stdout or "").splitlines():
            if not rel.endswith(".py"):
                continue
            txt = read_at(rev, rel)
            if txt and "def _iv" in txt:
                found.append(pathlib.Path(rel).stem)
        found.sort()
    for f in found:
        if f not in names and f != me:
            names.append(f)
    return [n for n in names if n != me]

#: A quantity, and the independent routes that may compute it. 2 routes to the
#: SAME quantity is a cross-check; 1 route each to 2 quantities is not.
QUANTITY_ROUTES = {
    "Wilson": {
        "statsmodels proportion_confint": r"proportion_confint\([^)]*wilson",
        #: ★ WIDENED 2026-11-06. The same algebra written `z**2 / (2 * n)`
        #: was invisible, so producers carrying a genuine second route were
        #: classified single-route -- a guard accusing correct code. Measured:
        #: of 265 producers using the statsmodels Wilson call the old pattern
        #: saw a second route in 71 and this one sees 139, so 68 were FALSE
        #: ACCUSATIONS; coverage 139 of 265 = 0.524528, Wilson [0.464481,
        #: 0.583875], Clopper-Pearson [0.462531, 0.585971]. The blindness was
        #: already recorded on 2026-11-04 at 52 of 121 and this session
        #: enlarged it by writing producers in the invisible spelling.
        #: IT CANNOT CREATE A FALSE PASS: 2 DISTINCT routes to the SAME
        #: quantity are still required, so a text carrying only the
        #: statsmodels call matches neither alternative. Checked by execution.
        "written-out algebra": (
            r"z\s*\*\s*z\s*/\s*\(\s*2\s*\*\s*[nN]\s*\)"
            r"|z\s*\*\*\s*2\s*/\s*\(\s*2\s*\*\s*[nN]\s*\)"
        ),
    },
    "Clopper-Pearson": {
        "scipy beta quantile": r"stats\.beta\.ppf|beta\.ppf",
        "mpmath incomplete beta": r"betainc",
    },
    "a summation": {
        "numpy float accumulation": r"np\.asarray\([^)]*\)\.sum\(\)|np\.sum\(",
        "sympy exact rationals": r"sp\.Rational|sympy\.Rational",
    },
}


def stem_imports(text: str) -> list[str]:
    return sorted({m for m in STEM
                   if re.search(rf"^\s*(?:import|from)\s+{m}\b", text, re.M)})


def routes(text: str) -> dict[str, list[str]]:
    out = {}
    for q, rs in QUANTITY_ROUTES.items():
        found = [nm for nm, rx in rs.items() if re.search(rx, text)]
        if found:
            out[q] = found
    return out


def symbolic_derivation(text: str) -> bool:
    """A derived result, not an asserted one: the strongest form available."""
    return bool(re.search(r"sp\.simplify|sympy\.simplify|\.doit\(\)", text))


def read_at(rev: str | None, rel: str) -> str | None:
    """The file's text at a git revision, or from the working tree if None.

    WHY THIS EXISTS. The reversals this script was written to establish were
    REPAIRED in the same session that measured them, which left the producer
    reporting 0 of 6 and the finding living only as prose -- the exact defect
    `measured-rate-travels-with-its-script` names. Passing `--rev` reproduces
    the pre-repair state from git, so the historical figure is recomputed
    rather than remembered.
    """
    if rev is None:
        p = REPO / rel
        return p.read_text(errors="replace") if p.is_file() else None
    r = subprocess.run(["git", "show", f"{rev}:{rel}"], capture_output=True,
                       text=True, cwd=str(REPO))
    return r.stdout if r.returncode == 0 else None


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("Show that counting STEM imports misranks producer rigour "
                     "against the independence predicate."))
    ap.add_argument("--rev", default=None,
                    help=("read the producers from this git revision instead "
                          "of the working tree, so the pre-repair figure is "
                          "reproducible (e.g. --rev d6ea0538)"))
    args = ap.parse_args()
    print("=" * 78)
    print("COUNTING IMPORTS AGAINST COUNTING INDEPENDENT ROUTES")
    print("=" * 78)
    print(f"  source: {'git ' + args.rev if args.rev else 'the working tree'}")

    names = population(args.rev)
    print(f"  population: {len(names)} script(s) -- "
          f"{len(SESSION_PRODUCERS)} named for the session, "
          f"{len(names) - len(SESSION_PRODUCERS)} DISCOVERED by defining `_iv`")

    rows = []
    for name in names:
        t = read_at(args.rev, f"scripts/{name}.py")
        if t is None:
            print(f"  MISSING {name}")
            continue
        imps, rt, sym = stem_imports(t), routes(t), symbolic_derivation(t)
        alone = [q for q, r in rt.items() if len(r) == 1]
        crossed = [q for q, r in rt.items() if len(r) >= 2]
        rows.append((name, imps, rt, alone, crossed, sym))

    for name, imps, rt, alone, crossed, sym in rows:
        by_imports = "PASS" if len(imps) >= 2 else "FAIL"
        # NO QUANTITY MEANS NO INTERVAL IS OWED, which is not the same as a
        # quantity resting on 1 route. Folding the 2 together is the
        # "ask what a 0 is a 0 OF" error, and this classifier made it on its
        # first run against c0001.
        if not rt:
            by_routes = "N/A "
        elif alone:
            by_routes = "FAIL"
        else:
            by_routes = "PASS"
        flag = ("  <-- VERDICTS DISAGREE"
                if by_imports != by_routes and by_routes != "N/A " else "")
        print(f"\n  {name}")
        print(f"    STEM imports        : {len(imps)} {imps}")
        print(f"    by import count     : {by_imports}")
        for q, r in sorted(rt.items()):
            tag = "CROSS-CHECKED" if len(r) >= 2 else "STANDS ALONE"
            print(f"    {q:16s}    : {len(r)} route(s)  {tag}  {r}")
        if not rt:
            print("    quantities          : none reported")
        print(f"    symbolic derivation : {sym}")
        print(f"    by independence     : {by_routes}{flag}")

    hard = [r[0] for r in rows if r[3] and len(r[1]) >= 2]
    print("\n" + "=" * 78)
    print("THE REVERSALS, NAMED INDIVIDUALLY")
    print("=" * 78)
    for nm in hard:
        print(f"  PASSED on import count, FAILS on independence : {nm}")
        print("    a quantity there stands on a single route, so 2 library")
        print("    names bought 0 cross-checks.")
    strongest = [r[0] for r in rows if r[5] and r[4]]
    for nm in strongest:
        print(f"  RANKED UNREMARKABLE by import count, STRONGEST by the rule : {nm}")
        print("    it computes a quantity by 2 independent routes AND derives")
        print("    its result symbolically rather than asserting it.")
    print(f"\n  producers examined                       : {len(rows)}")
    print(f"  carrying a quantity on a SINGLE route    : {sum(1 for r in rows if r[3])}")
    print(f"  carrying a genuine cross-check           : {sum(1 for r in rows if r[4])}")
    print(f"  reporting no quantity needing an interval: {sum(1 for r in rows if not r[2])}")
    print("\n  AND THE ONE THE AUDIT FLAGGED WAS FLAGGED FOR THE WRONG REASON.")
    print("  c0001_provenance_does_not_reconcile reports no proportion at all,")
    print("  so it owed no interval; its claims are identifications over a")
    print("  complete enumeration. What it lacked was a SECOND ROUTE to the")
    print("  superlative, which counts entries against a threshold constant of")
    print("  1.0 where a maximum would do. Adding an interval there, as first")
    print("  drafted, would have answered a question nothing asked.")
    print("\n  NO PROPORTION IS REPORTED FOR THIS FINDING ITSELF, deliberately:")
    print("  this population is a complete enumeration of the scripts in scope")
    print("  wrote, and the claim is about NAMED reversals, not about a rate in")
    print("  a population. An interval here would answer a different question.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
