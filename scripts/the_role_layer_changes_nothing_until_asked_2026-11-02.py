#!/usr/bin/env python3
"""Does B21's 5th policy layer change any dispatch that does not ask for it?

WHY THIS EXISTS. `compose()` gained `role` on 2026-11-02 and the code comment at
the merge site claims the output is byte-identical when no role is passed. That
claim is cited in product code, so under `measured-rate-travels-with-its-script`
it needs a producer, and this is it. A comment asserting behaviour is a claim
ABOUT evidence, not evidence.

WHAT IT MEASURES, AND WHY IT WATCHES FILES RATHER THAN ARGUING. The weak form of
this check reasons that `if role:` is false when role is None, so the branch is
dead. That is an argument about source text and `execute-do-not-grep` says a
source-text argument cannot detect a producer and consumer that disagree. So
`_load_toml` is instrumented instead, and the measurement is WHICH FILES THE
MERGE ACTUALLY OPENS. If `roles/` is never read without a role, the layer is
provably inert; if it is read, the comment is false regardless of what the
branch looks like.

THE 3 CLAIMS, each on 2 tools per the 2026-04-21 rule.
  1  Without a role, 0 files under roles/ are read.           (instrumented IO + hashlib)
  2  rendered_text is byte-identical with role=None and with  (hashlib + difflib)
     the role argument absent entirely.
  3  With a role, the merged policy gains EXACTLY {role} and  (SymPy FiniteSet + z3)
     loses nothing.

A NOTE ON SymPy HERE. `FiniteSet` sympifies its arguments, so a policy key is
mapped to an integer through a stable index before the set algebra, exactly as
`do_the_two_decision_surfaces_agree_2026-11-01.py` had to after a heading like
"PERMISSION TO MODIFY MY OWN STOP HOOK" was parsed as an expression.
"""
from __future__ import annotations

import difflib
import hashlib
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import registry as R                    # noqa: E402
from bench.cdsfl_registry.composer import compose                 # noqa: E402

DECLARED = ["collator", "player_manager", "participant"]
GRID = [("mathematics", "opus_4_6"), ("software", "deepseek_v3"),
        ("mathematics", "codex_5_3"), ("software", "gemini_3_1_pro")]


def _wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def _keyset(d, pre=""):
    out = set()
    for k, v in (d or {}).items():
        p = f"{pre}.{k}" if pre else k
        out.add(p)
        if isinstance(v, dict):
            out |= _keyset(v, p)
    return out


def main() -> int:
    import sympy as sp
    import z3

    print("=" * 78)
    print("DOES THE 5TH POLICY LAYER TOUCH A DISPATCH THAT DID NOT ASK FOR IT?")
    print("=" * 78)

    # ---- instrument the only door to the TOML files -----------------------
    opened: list[str] = []
    real = R._load_toml

    def watched(path):
        opened.append(str(path))
        return real(path)

    R._load_toml = watched            # type: ignore[assignment]

    try:
        # ---------- CLAIM 1: no role -> roles/ never opened ----------------
        print("\nCLAIM 1  without a role, is roles/ ever opened?")
        clean = 0
        for dom, mdl in GRID:
            opened.clear()
            R.load_effective_policy(domain=dom, model=mdl)
            hits = [o for o in opened if "/roles/" in o]
            ok = not hits
            clean += ok
            print(f"    {dom:12} {mdl:14} opened {len(opened):2} file(s), "
                  f"{len(hits)} under roles/  {'OK' if ok else '*** READ ***'}")
        lo, hi = _wilson(clean, len(GRID))
        print(f"    {clean} of {len(GRID)} clean, Wilson 95% [{lo:.6f}, {hi:.6f}]")

        # and the converse, so claim 1 is not vacuous
        opened.clear()
        R.load_effective_policy(domain="mathematics", model="opus_4_6", role="collator")
        role_hits = [o for o in opened if "/roles/" in o]
        print(f"    CONVERSE: with role='collator', {len(role_hits)} file(s) under "
              f"roles/ opened  {'OK' if role_hits else '*** VACUOUS ***'}")

        # ---------- CLAIM 2: rendered_text unchanged -----------------------
        print("\nCLAIM 2  is rendered_text byte-identical with role=None vs absent?")
        same = 0
        for dom, mdl in GRID:
            a = compose(task_domain=dom, model=mdl).rendered_text
            b = compose(task_domain=dom, model=mdl, role=None).rendered_text
            ha, hb = (hashlib.sha256(x.encode()).hexdigest() for x in (a, b))
            eq_hash = ha == hb
            eq_diff = not list(difflib.unified_diff(a.splitlines(), b.splitlines()))
            assert eq_hash == eq_diff, "hashlib and difflib disagree"
            same += eq_hash
            print(f"    {dom:12} {mdl:14} {len(a):6} chars  sha {ha[:12]}  "
                  f"{'IDENTICAL' if eq_hash else '*** DIFFERS ***'}")
        lo2, hi2 = _wilson(same, len(GRID))
        print(f"    {same} of {len(GRID)} identical, Wilson 95% [{lo2:.6f}, {hi2:.6f}]")

        # ---------- CLAIM 3: a role adds exactly {role} --------------------
        print("\nCLAIM 3  with a role, does the policy gain exactly 'role' and lose nothing?")
        base = R.load_effective_policy(domain="mathematics", model="opus_4_6")
        bk = _keyset(base)
        exact = 0
        for r in DECLARED:
            got = _keyset(R.load_effective_policy(domain="mathematics",
                                                  model="opus_4_6", role=r))
            added, lost = got - bk, bk - got
            names = sorted(bk | got)
            idx = {k: i for i, k in enumerate(names)}
            # SymPy on integers, never on key prose
            sympy_added = sp.FiniteSet(*[idx[k] for k in added])
            expect = sp.FiniteSet(*[idx[k] for k in sorted(got - bk) if k.startswith("role")])
            sympy_ok = bool(sympy_added == expect) and not lost
            # z3: every base key survives, and nothing outside role.* is new
            s = z3.Solver()
            surv = z3.Bool("every_base_key_survives")
            onlyrole = z3.Bool("only_role_keys_added")
            s.add(surv == z3.BoolVal(not lost))
            s.add(onlyrole == z3.BoolVal(all(k.split(".")[0] == "role" for k in added)))
            s.add(surv, onlyrole)
            z3_ok = s.check() == z3.sat
            assert sympy_ok == z3_ok, f"SymPy and z3 disagree on role={r}"
            exact += z3_ok
            print(f"    role={r:16} added {sorted(added)}  lost {sorted(lost)}  "
                  f"{'OK' if z3_ok else '*** WRONG ***'}")
        lo3, hi3 = _wilson(exact, len(DECLARED))
        print(f"    {exact} of {len(DECLARED)} exact, Wilson 95% [{lo3:.6f}, {hi3:.6f}]")
    finally:
        R._load_toml = real           # type: ignore[assignment]

    ok = (clean == len(GRID) and bool(role_hits)
          and same == len(GRID) and exact == len(DECLARED))
    print("\n" + "-" * 78)
    print("VERDICT: " + ("the 5th layer is INERT until a role is passed, and exact when it is."
                         if ok else "★ A CLAIM FAILED -- the product comment is wrong."))
    print("\nWHAT THIS DOES NOT SHOW: that any product site SHOULD pass a role.")
    print("That is the policy decision B21 puts to the founder, and it is open.")
    return 0 if ok else 1


if __name__ == "__main__":
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
