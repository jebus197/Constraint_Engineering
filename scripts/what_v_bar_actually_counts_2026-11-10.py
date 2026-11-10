#!/usr/bin/env python3
"""B94 decision 1, settled on the factual half: `v_bar` counts a model's OWN
CLAIM, exclusively, and the execution path writes to an object it never reads.

B94 ASKS HIM WHICH QUANTITY HE WANTS. Its own text says the `verified` flag
*"can be set either by an execution or by the model writing `"VERIFIED": true`
in its own reply"*, and that **nothing in the stored fingerprints records which
setter produced a value**. The first half of that is true of the PROJECT and
false of the OBJECT `v_bar` reads, and this script establishes the difference.

WHAT `v_bar` READS. `bench/dm/_manager.py` computes it as
`sum(1 for f in model_findings if f.verified) / len(model_findings)` --
ATTRIBUTE access on the `Finding` dataclass of `bench/dm/_types.py`.

THE 2 POPULATIONS, ENUMERATED BY SYNTAX TREE rather than by grep, because a
comment mentioning `verified=True` is not a setter and 8 of the first 16 grep
hits were comments:

  * `Finding(..., verified=...)` CONSTRUCTION SITES -- the object `v_bar` reads.
  * `entry['verified'] = ...` / `e['verified'] = ...` DICT ASSIGNMENTS on
    registry entries -- a different object, which `v_bar` never touches.

AND THE CLASSIFICATION OF EACH CONSTRUCTION SITE is taken from where its value
comes from, read off the same tree: a value parsed out of the model's reply
(`fd.get("verified")`, `verified_raw.upper() == "TRUE"`, `m.group(n)`,
`changes.get("verified")`) is a MODEL CLAIM; a value set after a falsifier ran
is an EXECUTION.

★ THIS SCRIPT'S FIRST CONCLUSION WAS WRONG AND IS RECORDED HERE RATHER THAN
QUIETLY CORRECTED. Walking only `Finding(verified=...)` calls and attribute
assignments gave "0 of 8 sites set it from an execution", which was read as
*the project never verifies by execution*. The P-pass added 3 further routes --
dict subscript assignment, `dataclasses.replace`, and `setattr` -- and the
subscript route returned 18 hits. The execution path EXISTS; it simply writes
somewhere else. A claim of "0 of N" is only as strong as the set of places it
looked, and the first version had not looked in 3 of 5.

WHAT THIS DOES NOT DO. It changes no measurement and no field. Which quantity
the fingerprint should read is his decision under B94, and taking it here would
change a number that drives the experiment.

Run: python3 scripts/what_v_bar_actually_counts_2026-11-10.py
Exit 0 always: this reports a state.
"""
from __future__ import annotations

import argparse
import ast
import pathlib

#: Expressions that mean THE MODEL SAID SO. Matched as substrings of the
#: unparsed value expression, which is why each is distinctive enough not to
#: collide with an execution result.
CLAIM_MARKERS = (
    'fd.get(\'verified\'', 'fd.get("verified"',
    'f.get(\'verified\'', 'f.get("verified"',
    'changes.get(\'verified\'', 'changes.get("verified"',
)
#: Names a parsed-reply boolean is bound to before construction, resolved by
#: walking the enclosing function rather than assumed from the call site.
CLAIM_SOURCES = ("verified_raw", "m.group", "fields.get", "combined_text")


def _repo() -> pathlib.Path:
    for cand in (pathlib.Path(__file__).resolve().parent,
                 *pathlib.Path(__file__).resolve().parents):
        if (cand / "bench" / "dm" / "_types.py").is_file():
            return cand
    raise SystemExit("cannot locate the repository")


REPO = _repo()


def _iv(k: int, n: int):
    """((wilson_lo, wilson_hi), (cp_lo, cp_hi), cross_check) -- the reserved
    project contract. Clopper-Pearson's second route is the EXACT BINOMIAL
    TAIL, because mpmath's `betainc` fails to converge at some (k, n) here."""
    import mpmath as mp
    import numpy as np
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint
    mp.mp.dps = 40
    sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    cp = proportion_confint(k, n, alpha=0.05, method="beta")
    z = st.norm.ppf(0.975)
    p = k / n if n else 0.0
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    w2 = (max(0.0, cen - hw), min(1.0, cen + hw))

    def tail(q, lo):
        rng = range(k, n + 1) if lo else range(0, k + 1)
        return mp.fsum([mp.binomial(n, i) * q ** i * (1 - q) ** (n - i)
                        for i in rng])

    def bisect(lo_tail):
        a, b = mp.mpf(0), mp.mpf(1)
        for _ in range(220):
            mid = (a + b) / 2
            v = tail(mid, lo_tail)
            if (v < mp.mpf("0.025")) == lo_tail:
                a = mid
            else:
                b = mid
        return float((a + b) / 2)

    cp2 = (0.0 if k == 0 else bisect(True), 1.0 if k == n else bisect(False))
    cross = max(abs(sm[0] - w2[0]), abs(sm[1] - w2[1]),
                abs((cp[0] or 0.0) - cp2[0]), abs(cp[1] - cp2[1]))
    return ((sm[0], sm[1]), ((cp[0] or 0.0), cp[1]), cross)


def _enclosing_source(fn: ast.AST) -> str:
    try:
        return ast.unparse(fn)
    except Exception:                                 # noqa: BLE001
        return ""


def scan(roots=("bench", "scripts"), base: pathlib.Path | None = None):
    """Every route that can set the flag, with each construction site classed.

    ★ `roots` AND `base` ARE PARAMETERS SO THIS IS TESTABLE AT ALL. With the
    tree hardcoded, a guard could only observe what the LIVE tree happens to
    contain -- and the mutation board proved the cost: disabling the `setattr`
    branch left the guard GREEN, because the live tree has 0 setattr sites and
    an assertion that none exists stays true whether the scanner can see them
    or not. A test can now plant one in a temporary tree and require it to be
    found, which is the difference between a ratchet and a check.
    """
    base = base or REPO
    ctor, subscript, replace_calls, setattrs = [], [], [], []
    for root in roots:
        for p in sorted((base / root).rglob("*.py")):
            if "logs" in p.parts or "tests" in p.parts:
                continue
            try:
                src = p.read_text(errors="replace")
                tree = ast.parse(src)
            except Exception:                          # noqa: BLE001
                continue
            fns = [n for n in ast.walk(tree)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            for n in ast.walk(tree):
                if isinstance(n, ast.Call):
                    f = ast.unparse(n.func)
                    for kw in (n.keywords or []):
                        if kw.arg != "verified":
                            continue
                        val = ast.unparse(kw.value)
                        rec = (str(p.relative_to(base)), n.lineno, f, val)
                        if "replace" in f:
                            replace_calls.append(rec)
                        else:
                            ctor.append(rec)
                    if f == "setattr" and len(n.args) >= 2:
                        try:
                            if ast.literal_eval(n.args[1]) == "verified":
                                setattrs.append(
                                    (str(p.relative_to(base)), n.lineno, f, ""))
                        except Exception:              # noqa: BLE001
                            pass
                if isinstance(n, ast.Assign):
                    for t in n.targets:
                        if (isinstance(t, ast.Subscript)
                                and isinstance(t.slice, ast.Constant)
                                and t.slice.value == "verified"):
                            subscript.append(
                                (str(p.relative_to(base)), n.lineno,
                                 ast.unparse(t.value)[:30],
                                 ast.unparse(n.value)[:20]))
            # classify each ctor site in this file by its enclosing function
            for i, (fp, ln, f, val) in enumerate(list(ctor)):
                if fp != str(p.relative_to(base)):
                    continue
                if any(mk in val for mk in CLAIM_MARKERS):
                    continue                           # already decidable
                #: ★ A LITERAL IS NEVER A PARSED REPLY, and the first version
                #: of this classifier said it was. It decided by the ENCLOSING
                #: FUNCTION's text, so `verified=False` at runner_core.py:1272
                #: was labelled a parsed reply because `verified_raw` appears
                #: elsewhere in the same function -- and the `literal_false`
                #: tally then read 0, because it compared against a value
                #: expression this loop had already annotated. A classifier
                #: that annotates before it counts reports its own edits.
                if val.strip() in ("False", "True"):
                    continue
                host = next((fn for fn in fns
                             if fn.lineno <= ln <= (fn.end_lineno or ln)), None)
                if host is None:
                    continue
                body = _enclosing_source(host)
                if any(_m in body for _m in CLAIM_SOURCES):
                    ctor[i] = (fp, ln, f, val + "   [<- parsed reply]")
    return ctor, subscript, replace_calls, setattrs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0])
    ap.parse_args(argv)
    ctor, subscript, repl, setat = scan()

    def is_claim(val: str) -> bool:
        return (any(mk in val for mk in CLAIM_MARKERS)
                or "[<- parsed reply]" in val)

    claims = [c for c in ctor if is_claim(c[3])]
    literal_false = [c for c in ctor
                     if c[3].split("   [<-")[0].strip() in ("False", "True")]
    other = [c for c in ctor if c not in claims and c not in literal_false]

    print("=" * 78)
    print("B94 DECISION 1: WHAT `v_bar` ACTUALLY COUNTS")
    print("=" * 78)
    print("  `v_bar` = sum(1 for f in model_findings if f.verified)/len(...)")
    print("  -> ATTRIBUTE access on the Finding dataclass, bench/dm/_types.py")
    print()
    print(f"  Finding(..., verified=...) construction sites : {len(ctor)}")
    for fp, ln, f, val in ctor:
        print(f"     {fp}:{ln}  verified={val}")
    print()
    n = len(ctor)
    print("  of those, populated from the MODEL'S OWN REPLY:")
    (wlo, whi), (clo, chi), cross = _iv(len(claims), n)
    print(f"    {len(claims)} of {n} = {len(claims)/n:.6f}")
    print(f"    Wilson          [{wlo:.6f}, {whi:.6f}]")
    print(f"    Clopper-Pearson [{clo:.6f}, {chi:.6f}]")
    print(f"    2 routes per interval agree to {cross:.3e}")
    print(f"  a literal False (no claim either way)        : "
          f"{len(literal_false)}")
    print(f"  from anything else                            : {len(other)}")
    for fp, ln, f, val in other:
        print(f"     {fp}:{ln}  verified={val}")
    print()
    print(f"  entry['verified'] = ... DICT assignments       : {len(subscript)}")
    print("    THE EXECUTION PATH, and it writes to a DIFFERENT OBJECT -- a")
    print("    registry entry dict, which `v_bar` never reads.")
    for fp, ln, tgt, val in subscript[:10]:
        print(f"     {fp}:{ln}  {tgt}['verified'] = {val}")
    if len(subscript) > 10:
        print(f"     ... and {len(subscript) - 10} more withheld, of "
              f"{len(subscript)}")
    print()
    print(f"  dataclasses.replace(verified=...)             : {len(repl)}")
    print(f"  setattr(obj, 'verified', ...)                 : {len(setat)}")
    print()
    print("=" * 78)
    if len(claims) == n - len(literal_false) and subscript:
        print("  THE FACTUAL HALF OF B94's DECISION 1 IS SETTLED: every")
        print("  construction site that sets a TRUE-capable value takes it from")
        print("  the model's own reply, so `v_bar` measures how often a model")
        print("  CLAIMS verification and the name is the thing that is wrong.")
        print("  The execution path exists and writes to a registry entry dict")
        print("  that `v_bar` does not read, so the 2 quantities ALREADY exist")
        print("  in 2 places and are simply not joined.")
    else:
        print("  THE PATTERN DID NOT HOLD; no claim is drawn from this run.")
    print("  WHICH quantity the fingerprint should read stays HIS under B94.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
