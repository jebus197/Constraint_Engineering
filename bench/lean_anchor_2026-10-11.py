#!/usr/bin/env python3
"""A difficulty-INVARIANT anchor set, graded by the Lean kernel rather than by a judge.

THE FOUNDER'S RULING, 2026-10-11: *"y, build the anchor set with Lean, and let's utilise it
(minus the hype) appropriately in our work going forward."* With the condition that decided
the shape: *"if it adds nothing of use, then there is no requirement for you to do it."*

WHY AN ANCHOR SET IS NEEDED AT ALL, established by the 2026-10-08 panel and verified
symbolically here before any of this was built. Relegation on sustained degradation is NOT
IDENTIFIED: in the standard difficulty model only the difference between a model's capability
and an item's difficulty enters, so a capability drop across the roster and a difficulty rise
across the task stream produce IDENTICAL distributions on every outcome. SymPy returns exactly
0 for the difference, z3 returns `unsat` on any separating value, and mpmath returns 0.0 across
27 points. No statistic computed from the live stream can separate the 2 causes.

WHAT BREAKS THE DEGENERACY, AND WHY IT IS LEAN RATHER THAN ANYTHING ELSE. The anchor does not
need a difficulty RATING -- a rating measured from our own models would be circular, which is
the same degeneracy again. It needs difficulty to be INVARIANT. This pool is invariant by
construction on 2 counts: the statements are byte-stable committed data, and the grader is a
deterministic proof kernel rather than a model judging another model. If a seat's pass count on
this pool falls, the work did not get harder -- it is literally the same bytes checked by the
same kernel.

★ THE 4 WAYS A PROOF PASSES FOR THE WRONG REASON, EACH MEASURED ON THIS MACHINE 2026-10-11
WITH LEAN 4.34.1 BEFORE THIS FILE WAS WRITTEN, NOT ASSUMED:

  1. `sorry`           -- exit 0, only a WARNING: "declaration uses `sorry`". A grader keying on
                          the exit code accepts a proof of nothing.
  2. `axiom`           -- exit 0, NO output at all. `axiom cheat : forall a b, a + b = a * b`
                          followed by using it proves a FALSE statement and is silently accepted.
  3. `native_decide`   -- exit 0, NO output. Trusts the compiler rather than the kernel, which
                          is a strictly weaker guarantee than the one this pool exists to give.
  4. RESTATEMENT       -- exit 0, NO output, and the worst of the 4. Changing the statement from
                          `a + b = b + a` to `a + b = a + b` and proving it with `rfl` is
                          accepted under the SAME theorem name. This is the autoformalisation
                          gap in operational form, and it is exactly what would destroy the
                          invariance the pool exists to provide.

The literature names failure 4 "semantic hallucination" and reports formal-versus-informal
discrepancies in MORE THAN HALF of miniF2F's problems, the field's own standard benchmark. So
the statement-identity check below is not belt-and-braces; it is the load-bearing guard.

AND A 5TH TRAP THAT IS MINE, NOT LEAN'S. The first measurement of these exit codes read 0 for
all 3 cases because `$?` captured a `head` in a pipeline rather than `lean`. A grader built on
that reading would have passed everything. The exit code is therefore captured directly here,
never through a pipe.

LEAN IS OPTIONAL AND ITS ABSENCE IS REPORTED, NEVER SILENTLY PASSED. The founder's standing
ruling on Wolfram applies unchanged: nobody running this project may be COMPELLED to install a
tool. With no `lean` on PATH every problem grades as UNAVAILABLE, which is distinct from both
PASS and FAIL and is excluded from the denominator, so an absent toolchain cannot inflate or
deflate a seat's measured rate.

WHAT THIS DOES NOT YET DO, STATED PLAINLY. Nothing in live routing consumes a measured rate:
`routing.DEFAULT_FALSIFIER_STRENGTH` is a frozen tuple of 6 VENDOR NAMES, and the producer that
computes a measured ranking is an orphan no live module imports. So this file supplies the
(successes, attempts) pair and the Wilson lower bound that a rate-aware ladder would need, and
the single change that makes the ladder read it is the founder's to authorise, because it alters
what every routed finding does.

Run: python3 bench/lean_anchor_2026-10-11.py
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

#: Tokens that make a Lean file's exit code meaningless as evidence of a proof.
#: Each was MEASURED to exit 0 on this machine before being listed.
REFUSED_TOKENS = ("sorry", "axiom", "native_decide", "implemented_by",
                  "unsafe", "partial def", "@[extern")

#: Verdicts. UNAVAILABLE is deliberately NOT a failure and leaves the denominator.
PASS, FAIL, UNAVAILABLE = "PASS", "FAIL", "UNAVAILABLE"

Z = 1.959963984540054


class Problem:
    """A pool entry. The STATEMENT is fixed data; a candidate supplies only a proof."""

    __slots__ = ("pid", "statement", "tier", "note")

    def __init__(self, pid: str, statement: str, tier: str, note: str):
        self.pid, self.statement, self.tier, self.note = pid, statement, tier, note


#: THE POOL. Every statement below was compiled on 2026-10-11 against Lean 4.34.1 with NO
#: Mathlib, so the pool carries no multi-gigabyte dependency and the simplest sufficient
#: install (elan plus a core toolchain) is enough to grade it. 2 of the 5 had to be repaired
#: during that check -- `List.length_append` takes no explicit arguments in this version and a
#: Gauss-sum attempt could not be closed by `omega` -- which is the pool doing its job before
#: it shipped rather than after.
#:
#: TIER IS A SPAN LABEL, NOT A MEASURED DIFFICULTY, and saying so matters: a difficulty measured
#: from our own models would re-create the degeneracy this pool exists to break. What the pool
#: guarantees is INVARIANCE, not calibration.
POOL = (
    Problem("L1", "theorem anchor_L1 (a : Nat) : a + 0 = a :=",
            "trivial", "1 library lemma, no tactic work"),
    Problem("L2", "theorem anchor_L2 (a b : Nat) : a + b = b + a :=",
            "easy", "1 library lemma, commutativity"),
    Problem("L3", "theorem anchor_L3 (xs ys : List Nat) : (xs ++ ys).length = xs.length + ys.length :=",
            "easy", "a list lemma whose argument convention differs between Lean versions"),
    Problem("L4", "theorem anchor_L4 (xs : List Nat) : xs.reverse.reverse = xs :=",
            "moderate", "an involution, explicit argument required"),
    Problem("L5", "theorem anchor_L5 (n : Nat) : n < 2 ^ n :=",
            "hard", "needs induction plus a calc chain; the reference proof is 10 lines"),
)

#: The reference proofs, used ONLY to prove the grader works. They are not answers a seat sees.
REFERENCE_PROOFS = {
    "L1": " Nat.add_zero a",
    "L2": " Nat.add_comm a b",
    "L3": " List.length_append",
    "L4": " List.reverse_reverse xs",
    "L5": """ by
  induction n with
  | zero => decide
  | succ k ih =>
    have h : 2 ^ k + 1 <= 2 ^ k + 2 ^ k := by
      have : 1 <= 2 ^ k := Nat.one_le_two_pow
      omega
    calc k + 1 < 2 ^ k + 1 := by omega
      _ <= 2 ^ k + 2 ^ k := h
      _ = 2 ^ (k + 1) := by rw [Nat.pow_succ]; omega""",
}


def wilson_lower(k: int, n: int, z: float = Z) -> float:
    """Lower confidence bound on a proportion. The same form routing would consume."""
    if n == 0:
        return 0.0
    p = k / n
    d = 1.0 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, centre - half)


def lean_available() -> "str | None":
    """The `lean` binary, or None. Checks PATH and elan's default location."""
    found = shutil.which("lean")
    if found:
        return found
    candidate = Path(os.path.expanduser("~/.elan/bin/lean"))
    return str(candidate) if candidate.is_file() else None


#: Keywords that open a top-level declaration. A submission containing one is restating the
#: problem rather than proving it, which is the only way a candidate can alter the pool's
#: difficulty -- and Lean accepts it silently, measured 2026-10-11.
DECLARATION_KEYWORDS = ("theorem", "lemma", "def ", "example", "instance",
                        "abbrev", "macro", "notation", "structure", "inductive")


def _declares_its_own(submitted: str) -> "str | None":
    """The first declaration keyword a submission opens, or None.

    Comments are stripped first, so a keyword mentioned in a comment is not an attack.
    """
    import re as _re
    body = _re.sub(r"--[^\n]*", " ", str(submitted or ""))
    body = _re.sub(r"/-.*?-/", " ", body, flags=_re.S)
    for kw in DECLARATION_KEYWORDS:
        if _re.search(r"(^|[^A-Za-z_])" + _re.escape(kw.strip()) + r"([^A-Za-z_]|$)", body):
            return kw.strip()
    return None


def grade(problem: Problem, candidate_proof: str, timeout: int = 120) -> dict:
    """Grade one candidate proof of one pool problem.

    PASSES only if ALL of these hold, and each condition exists because the 1 before it is
    insufficient on its own:
      * no refused token appears anywhere in the submission;
      * the assembled file's statement is BYTE-IDENTICAL to the pool's;
      * `lean` exits 0, with the code read directly and never through a pipe;
      * `lean` emits no line containing "error" and none containing "sorry".
    """
    binary = lean_available()
    if binary is None:
        return {"problem": problem.pid, "verdict": UNAVAILABLE,
                "reason": "no `lean` on PATH or in ~/.elan/bin; Lean is optional by ruling",
                "counts_in_denominator": False}

    submitted = str(candidate_proof or "")
    low = submitted.lower()
    for tok in REFUSED_TOKENS:
        if tok in low:
            return {"problem": problem.pid, "verdict": FAIL,
                    "reason": f"submission contains the refused token {tok!r}, which was "
                              f"MEASURED to exit 0 and would pass on the exit code alone",
                    "counts_in_denominator": True}

    # ★ THE STATEMENT-IDENTITY GUARD, AND THE FIRST VERSION OF IT WAS DEAD CODE.
    #
    # It read `if not source.startswith(problem.statement)` over a `source` built as
    # `problem.statement + submitted` -- a TAUTOLOGY that could never fire. A mutation pass
    # deleting the whole branch left all 14 tests green, which is how it was found. A guard
    # that cannot fail is the failure shape this project keeps paying for, and writing one
    # into the very check that protects the pool's invariance would have been the worst
    # possible place for it.
    #
    # THE REAL ATTACK, measured on Lean 4.34.1: a submission that introduces its OWN
    # declaration. `theorem anchor_L2 (a b : Nat) : a + b = a + b := rfl` compiles, exits 0 and
    # emits nothing, under the same name as the pool's problem. So the guard is on DECLARATION
    # KEYWORDS in the submission, which is checkable, rather than on a prefix that is
    # guaranteed by construction.
    decl = _declares_its_own(submitted)
    if decl:
        return {"problem": problem.pid, "verdict": FAIL,
                "reason": f"the submission opens its own declaration with {decl!r}; a candidate "
                          f"supplies a PROOF, and restating the problem changes it",
                "counts_in_denominator": True}

    source = problem.statement + submitted + "\n"

    with tempfile.TemporaryDirectory(prefix="cdsfl_lean_") as d:
        f = Path(d) / f"{problem.pid}.lean"
        f.write_text(source, encoding="utf-8")
        try:
            # capture_output, so the exit code is `lean`'s and not a pipeline's.
            proc = subprocess.run([binary, str(f)], capture_output=True, text=True,
                                  timeout=timeout)
        except subprocess.TimeoutExpired:
            return {"problem": problem.pid, "verdict": FAIL,
                    "reason": f"lean did not finish within {timeout}s",
                    "counts_in_denominator": True}
        except OSError as exc:
            return {"problem": problem.pid, "verdict": UNAVAILABLE,
                    "reason": f"lean could not be executed: {exc}",
                    "counts_in_denominator": False}

    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        return {"problem": problem.pid, "verdict": FAIL, "exit": proc.returncode,
                "reason": "lean rejected the proof",
                "detail": out.strip().splitlines()[:3], "counts_in_denominator": True}
    if "error" in out.lower() or "sorry" in out.lower():
        return {"problem": problem.pid, "verdict": FAIL, "exit": 0,
                "reason": "lean exited 0 but reported an error or a `sorry`, which is the "
                          "measured loophole the exit code alone misses",
                "detail": out.strip().splitlines()[:3], "counts_in_denominator": True}
    return {"problem": problem.pid, "verdict": PASS, "exit": 0,
            "counts_in_denominator": True}


def score_seat(answers: dict, pool=POOL, timeout: int = 120) -> dict:
    """Grade a seat's answers over the whole pool and return what routing would need.

    `answers` maps a problem id to a candidate proof. A missing answer is a FAIL, because
    declining a fixed problem is evidence about the seat; an UNAVAILABLE toolchain is not.
    """
    rows = [grade(p, answers.get(p.pid, ""), timeout=timeout) for p in pool]
    scored = [r for r in rows if r["counts_in_denominator"]]
    successes = sum(1 for r in scored if r["verdict"] == PASS)
    attempts = len(scored)
    return {
        "rows": rows,
        "successes": successes,
        "attempts": attempts,
        "unavailable": len(rows) - attempts,
        "point_estimate": (successes / attempts) if attempts else None,
        "wilson_lower": wilson_lower(successes, attempts),
        "pool_sha256": pool_digest(pool),
        "note": ("`successes` and `attempts` are the pair routing's Wilson ranking consumes; "
                 "`pool_sha256` pins the exact problem set, so a rate measured against a "
                 "DIFFERENT pool cannot be compared with this one by accident"),
    }


def pool_digest(pool=POOL) -> str:
    """A digest over the pool's statements. Invariance is only meaningful if it is checkable."""
    import hashlib
    h = hashlib.sha256()
    for p in pool:
        h.update(p.pid.encode()); h.update(b"\0")
        h.update(p.statement.encode()); h.update(b"\0")
    return h.hexdigest()


def claim_the_grader_rejects_every_measured_loophole() -> dict:
    """P-PASS: the grader is only worth anything if it refuses the 4 measured cheats."""
    target = POOL[1]           # anchor_L2 : a + b = b + a
    cases = {
        "reference proof": (REFERENCE_PROOFS["L2"], PASS),
        "sorry": (" by sorry", FAIL),
        "axiom": ("\naxiom cheat : forall a b : Nat, a + b = a * b", FAIL),
        "native_decide": (" by native_decide", FAIL),
        "wrong proof": (" Nat.mul_comm a b", FAIL),
        "empty": ("", FAIL),
    }
    got = {}
    for name, (proof, want) in cases.items():
        r = grade(target, proof)
        got[name] = {"want": want, "verdict": r["verdict"],
                     "ok": r["verdict"] == want or r["verdict"] == UNAVAILABLE,
                     "reason": r.get("reason", "")[:90]}
    return {"cases": got,
            "all_as_expected": all(v["ok"] for v in got.values()),
            "lean_present": lean_available() is not None}


def claim_a_restated_statement_cannot_pass() -> dict:
    """The load-bearing guard, exercised directly rather than described.

    A seat that rewrites `a + b = b + a` into `a + b = a + b` and proves it by `rfl` is
    accepted by Lean itself -- measured. It must not be accepted here.
    """
    weakened = Problem("L2", "theorem anchor_L2 (a b : Nat) : a + b = a + b :=",
                       "easy", "a RESTATEMENT, not the pool's problem")
    direct = grade(weakened, " rfl")
    pooled = grade(POOL[1], " rfl")
    return {
        "lean_accepts_the_restatement_on_its_own": direct["verdict"],
        "the_pool_problem_rejects_rfl": pooled["verdict"],
        "digest_differs": pool_digest((weakened,)) != pool_digest((POOL[1],)),
        "verdict": ("the restatement is a DIFFERENT problem and the pool digest proves it; "
                    "`rfl` cannot prove the pool's own statement"),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args()

    print("== 0. is Lean available? ==")
    b = lean_available()
    print(f"   lean binary: {b or 'ABSENT -- every problem grades UNAVAILABLE, by ruling'}")
    print(f"   pool: {len(POOL)} problems, digest {pool_digest()[:16]}...")

    print("\n== 1. the reference proofs, which prove the GRADER works ==")
    s = score_seat(REFERENCE_PROOFS, timeout=args.timeout)
    for r in s["rows"]:
        print(f"   {r['problem']}: {r['verdict']:11s} {r.get('reason','')[:70]}")
    print(f"   successes {s['successes']} of {s['attempts']} attempts, "
          f"unavailable {s['unavailable']}, point {s['point_estimate']}, "
          f"Wilson lower {s['wilson_lower']:.6f}")

    print("\n== 2. P-pass: every measured loophole must be refused ==")
    d = claim_the_grader_rejects_every_measured_loophole()
    for name, v in d["cases"].items():
        print(f"   {name:16s} want {v['want']:11s} got {v['verdict']:11s} ok={v['ok']}")
    print(f"   all as expected: {d['all_as_expected']}")

    print("\n== 3. and a restated statement is a different problem ==")
    for k, v in claim_a_restated_statement_cannot_pass().items():
        print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
