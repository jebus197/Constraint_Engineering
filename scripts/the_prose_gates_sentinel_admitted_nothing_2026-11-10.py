#!/usr/bin/env python3
"""The prose apply-back branch compared its verdict against a constant that
does not exist, so it admitted 0 of 7 reachable verdicts.

HIS RULING, 2026-11-10, verbatim: the suite "will come from which ever STEM
topic area under discussion and the tools/falsifiers/B-Cell machinery attached
to that STEM topic". The branch built for it routes a non-Python target to
`fix_efficacy.probe`, which is stricter than a green suite.

THE DEFECT, AND IT WAS MINE, FOUND BEFORE THE COMMIT LANDED. The admission
test read:

    if _verdict == getattr(_fe, "CURED", "CURED"):

`bench/fix_efficacy.py` defines no `CURED`. So `getattr` fell back to the bare
literal "CURED" and compared it against the 7 verdict values `probe()` can
actually return -- none of which is "CURED". The branch was wired to a caller
and executed by a guard and could still admit NOTHING: `additive-standard`'s
symmetric failure, an addition nothing reaches.

WORSE, THE GUARD PASSED. Its admitting fixture built the fake verdict from the
IDENTICAL expression, so it fed the gate whatever sentinel the gate looked for.
A guard that derives its input from its subject cannot disagree with it, for any
value of the subject. That is the lesson, and it is more general than this bug.

THE CORRECT SENTINEL is `FIX_CURES = "FIX_CURES_ITS_OWN_FALSIFIER"`.

WHAT THIS SCRIPT DOES. It resolves the sentinel the way the product resolves it,
enumerates by AST every verdict `probe()` can return, drives the comparison, and
reports the admission count with intervals on 2 independent routes. It is
written so it would FAIL LOUDLY if the names drift again in either direction.

Run: python3 scripts/the_prose_gates_sentinel_admitted_nothing_2026-11-10.py
Exit 0 when the live tree admits exactly 1 of the reachable verdicts; 1 if not.
"""
from __future__ import annotations

import ast
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

BROKEN_SENTINEL_EXPR = '"CURED"'       # what the first version compared against
CORRECT_CONST = "FIX_CURES"            # what fix_efficacy actually defines


def verdicts_reachable_from_probe() -> dict[str, str]:
    """Every verdict value `fix_efficacy.probe()` can return, by AST."""
    import fix_efficacy as fe
    consts = {k: v for k, v in vars(fe).items()
              if k.isupper() and isinstance(v, str) and not k.startswith("_")}
    src = pathlib.Path(fe.__file__).read_text()
    probe = next(n for n in ast.walk(ast.parse(src))
                 if isinstance(n, ast.FunctionDef) and n.name == "probe")
    out: dict[str, str] = {}
    for node in ast.walk(probe):
        if isinstance(node, ast.Return) and node.value is not None:
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Name) and sub.id in consts:
                    out[sub.id] = consts[sub.id]
    return out


def intervals(k: int, n: int) -> dict[str, tuple[float, float]]:
    """Wilson and Clopper-Pearson on 2 independent routes each."""
    import numpy as np
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint

    sm_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    sm_cp = proportion_confint(k, n, alpha=0.05, method="beta")

    # Route 2, Wilson from first principles.
    z = st.norm.ppf(0.975)
    p = k / n
    den = 1.0 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    np_w = (max(0.0, cen - hw), min(1.0, cen + hw))

    # Route 2, Clopper-Pearson. For k == 0 the upper limit has a closed form,
    # 1 - (alpha/2)**(1/n); the general root-find fails at that boundary, and a
    # tool that errored verified nothing, so the closed form is used there.
    import mpmath as mp
    mp.mp.dps = 40
    if k == 0:
        cp_lo, cp_hi = 0.0, float(1 - mp.mpf("0.025") ** (mp.mpf(1) / n))
    elif k == n:
        cp_lo, cp_hi = float(mp.mpf("0.025") ** (mp.mpf(1) / n)), 1.0
    else:
        cp_lo = float(mp.findroot(
            lambda q: mp.betainc(k, n - k + 1, q, 1, regularized=True) - 0.025,
            mp.mpf(k) / n / 2))
        cp_hi = float(mp.findroot(
            lambda q: mp.betainc(k + 1, n - k, 0, q, regularized=True) - 0.025,
            min(0.999, (mp.mpf(k) / n + 1) / 2)))
    return {
        "wilson_statsmodels": (float(sm_w[0]), float(sm_w[1])),
        "wilson_scipy_numpy": np_w,
        "cp_statsmodels": (float(sm_cp[0] or 0.0), float(sm_cp[1])),
        "cp_mpmath": (cp_lo, cp_hi),
    }


def _executable_text(src: str) -> str:
    """`src` with comments and docstrings removed.

    THE DETECTOR MUST NOT READ ITS OWN SCAR AS A WOUND. The repaired gate
    carries a comment quoting the broken expression `getattr(_fe, "CURED",
    "CURED")` so the defect cannot be reintroduced by someone who does not know
    why the sentinel is what it is. A substring check over raw source then
    reports the EXPLANATION as the DEFECT -- which is exactly what the first
    run of this script did, and it is a shape this project has already
    recorded: a detector that spells out its own pattern accuses the comment
    that documents it. So the check runs over executable text only. The
    comment stays; the detector stops reading it.
    """
    import io
    import tokenize

    out: list[str] = []
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError):
        # Fail LOUD rather than silently passing a file we cannot tokenise.
        raise
    prev_type = None
    for tok in toks:
        if tok.type == tokenize.COMMENT:
            continue
        # A STRING in statement position is a docstring; keep real string
        # literals, which are the ones a sentinel comparison would use.
        if (tok.type == tokenize.STRING
                and prev_type in (tokenize.INDENT, tokenize.NEWLINE,
                                  tokenize.NL, None)):
            continue
        out.append(tok.string)
        if tok.type not in (tokenize.NL, tokenize.NEWLINE):
            prev_type = tok.type
        else:
            prev_type = tok.type
    return " ".join(out)


def main(argv=None) -> int:
    #: A `--help` MUST NEVER COST MINUTES -- his standing rule, and the
    #: project enforces it. This producer had no argparse at all, so `--help`
    #: was ignored and the whole measurement ran. The description is taken
    #: from the module docstring so the usage text cannot drift from the file.
    import argparse
    _ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0] if __doc__ else "")
    _ap.parse_args(argv)
    import fix_efficacy as fe

    print("=" * 78)
    print("THE PROSE GATE'S SENTINEL — what it resolves to, and what it admits")
    print("=" * 78)

    broken = getattr(fe, "CURED", "CURED")
    print(f"\n  hasattr(fix_efficacy, 'CURED')     = {hasattr(fe, 'CURED')}")
    print(f"  the FIRST version compared against = {broken!r}")
    correct = getattr(fe, CORRECT_CONST, None)
    print(f"  fix_efficacy.{CORRECT_CONST:<21s} = {correct!r}")

    reach = verdicts_reachable_from_probe()
    print(f"\n  verdicts probe() can return: {len(reach)}")
    for name, val in sorted(reach.items()):
        broke = "ADMITS" if val == broken else "refused"
        fixed = "ADMITS" if val == correct else "refused"
        print(f"    {name:<30s} broken:{broke:<8s} fixed:{fixed:<8s} {val!r}")

    n = len(reach)
    k_broken = sum(1 for v in reach.values() if v == broken)
    k_fixed = sum(1 for v in reach.values() if v == correct)

    print(f"\n  BROKEN sentinel admitted {k_broken} of {n}")
    iv = intervals(k_broken, n)
    for label, (lo, hi) in iv.items():
        print(f"    {label:<22s} [{lo:.6f}, {hi:.6f}]")
    gap = abs(iv["wilson_statsmodels"][1] - iv["wilson_scipy_numpy"][1])
    print(f"    2-route Wilson upper gap: {gap:.3e}")
    print(f"\n  FIXED  sentinel admits   {k_fixed} of {n}")

    # The live tree must admit exactly 1. 0 is the 2026-11-10 defect; more than
    # 1 is a gate that has stopped discriminating.
    import importlib
    import inspect
    rr = importlib.import_module("bench.reference_runner_v3")
    src = inspect.getsource(rr._apply_back_gate)
    code = _executable_text(src)
    names_in_src = CORRECT_CONST in code
    still_broken = BROKEN_SENTINEL_EXPR in code
    print(f"\n  the live gate names {CORRECT_CONST}: {names_in_src}")
    print(f"  the live gate still names the broken literal: {still_broken}")
    print(f"  (comments stripped: {len(src)} chars of source -> "
          f"{len(code)} of code)")

    ok = k_fixed == 1 and names_in_src and not still_broken
    print("\n" + "=" * 78)
    if ok:
        print("  PASS — the gate names a sentinel probe() can produce, and")
        print("         exactly 1 reachable verdict admits.")
    else:
        print("  FAIL — the prose gate admits the wrong number of verdicts, or")
        print("         still carries the broken literal. See above.")
    print("=" * 78)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
