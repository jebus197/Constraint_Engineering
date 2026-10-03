# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'falsifier_supply_and_integrity_r2_2026-10-02', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6603c28c7cfdc32a1be9f116831c24ce975edfa9abf35ac2c09a6d17f855a1c7
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""PRE-REGISTRATION, and population check, for the REPOINTING experiment (Q4).

Two reviewers independently proposed repointing as the only thing that settles
over-specificity, "because nothing in the archive was ever repointed". That is
correct and it is the reason the archive cannot answer the founder's question: a
falsifier that CONFIRMED on the artefact it was written for tells us nothing about
whether it would survive being aimed at a different one. Generality is a claim
about TRANSFER, and transfer was never measured.

This file is the pre-registration. It commits the population, the substitution
rule, the decider, the expected rates and the stopping condition BEFORE the run,
and it EXECUTES the population selection now so the numbers below are not
aspirational. It runs no model and spends nothing.

────────────────────────────────────────────────────────────────────────────────
WHY THE HYPOTHESIS IS NARROWER THAN THE BRIEF'S

The brief's CAUSE 1 -- a body naming a concrete file ERRORs at OR 4.3063 -- splits
cleanly, measured 2026-10-02 over 567 post-feature criticals carrying a body
(`scripts/supply_cause1_is_path_portability_2026-10-02.py`):

    names an ABSOLUTE path    6/132 =  4.55%  ERROR   OR 0.8874  p = 1.000
    names a RELATIVE file    12/ 79 = 15.19%  ERROR   OR 6.1433  p = 8.831828e-05
    names NO file            10/353 =  2.83%  ERROR   (reference cell)

(Fisher by scipy and by an independent mpmath hypergeometric sum, agreeing to
1e-9; the odds ratio 6.1432835820895522388 and the p-value
0.00008831827649719537 independently confirmed with Wolfram Language.)

So the ERROR excess is NOT in path portability -- absolute paths show no excess at
all -- it is in bodies bound to a named RELATIVE artefact. H1 below is therefore
about LOGIC coupling, and the absolute-path stratum is carried as a NEGATIVE
control: if it moves, the design is measuring the harness and not the falsifiers.

────────────────────────────────────────────────────────────────────────────────
POPULATION (frozen by this file; printed below from the live archive)

  P  post-feature criticals (run dir exp-number >= 42, or unnumbered), severity
     >= 0.7, carrying a non-empty falsifier body, whose recorded verdict is
     CONFIRMED. CONFIRMED only: a body that already ERRORed cannot show us
     anything about transfer, and including it would load the result.
  Strata, by the body's own text:
     S_rel  names at least one RELATIVE file and no absolute path   (treatment)
     S_abs  names at least one ABSOLUTE path                        (control)
     S_non  names no file at all                                   (ceiling)

SUBSTITUTION RULE (mechanical, no model in the loop)

  For each body b in P, and each named artefact a in b:
    1. Choose a DONOR artefact a' != a of the same kind (suffix) from the same
       repository, selected by the ranked rule: (i) a sibling in a's directory,
       (ii) else any file with a's suffix, choosing the one whose byte length is
       closest to a's, ties broken by sorted path order. Deterministic: no
       randomness, so the run is reproducible without a seed.
    2. Rewrite every occurrence of a in b to a'. NOTHING ELSE CHANGES -- not the
       assertions, not the imports, not the control flow. Repointing is a path
       substitution; if it required editing the logic, the body was coupled by
       construction and that is the finding, recorded as UNREPOINTABLE.
    3. Emit b' and record (b, a, a').

THE DECIDER is `bench.falsifier_verify.reverify_falsifier`, unmodified, with
`repo_root` set to the live checkout. Tools decide. No model and no reviewer sees
a verdict before it is recorded, and the model that wrote b is not consulted.

THE OUTCOME, per repointed body b':
  TRANSFERS    b' re-runs and returns CONFIRMED or REFUTED -- it still executes
               and still discriminates, so its logic was general.
  BREAKS       b' returns ERROR / INTEGRITY_VIOLATION / times out -- its logic
               was bound to the artefact it named.
  UNREPOINTABLE  no donor exists, or step 2 cannot be applied.

────────────────────────────────────────────────────────────────────────────────
PRE-REGISTERED RATES. These are committed now so the result cannot be read
backwards into whichever story the numbers happen to tell.

  H1 (over-specificity is real and large)
       break_rate(S_rel) >= 50%, and its Wilson 95% lower bound > 25%.
  H0 (over-specificity is a non-problem; falsifiers are general)
       break_rate(S_rel) <= 15%, Wilson 95% UPPER bound < 25%.
  INCONCLUSIVE
       any interval straddling 25%. Declared as INCONCLUSIVE and reported as
       such; the brief's "adjudicate, do not average" applies to the causes, not
       to a licence to round an overlapping interval into a verdict.
  DISCRIMINATION, the primary comparison
       Fisher exact on [[break(S_rel), transfer(S_rel)], [break(S_non),
       transfer(S_non)]]. Pre-registered direction: OR > 1. An OR <= 1 REFUTES
       the coupling hypothesis outright, whatever the marginal rates look like.
  NEGATIVE CONTROL, which can void the whole run
       break_rate(S_abs) must not exceed break_rate(S_rel). S_abs bodies name a
       path that does not exist in this checkout, so they break for a reason that
       has nothing to do with generality. If S_abs breaks MORE, the experiment is
       measuring relocation and its result is VOID -- reported, not rescued.

STOPPING CONDITION. Fixed-N, not sequential, because a stopping rule that reads
the running estimate inflates the error rate and this project has been burned by
post-hoc cuts twice in the figures this brief carries.

  Run the whole of S_rel and S_non. Stop. No interim look, no top-N truncation,
  no retry of a BREAKS result. If any body is dropped for an operational reason,
  the count dropped and the reason are printed -- "no silent caps": a bounded
  sweep reported without its exclusions reads as full coverage when it is not.
  n is adequate iff the Wilson width on break_rate(S_rel) is < 20 percentage
  points; if it is not, say so and do NOT substitute a narrower claim.

WHAT WOULD REFUTE THE EXPERIMENT ITSELF, as opposed to the hypothesis. If
TRANSFERS bodies turn out to CONFIRM on the donor artefact at a high rate, they
are not general -- they are vacuous, confirming whatever they are pointed at, the
`check_sk_threshold` family. So every TRANSFERS body is additionally passed
through `bench.cdsfl_registry.bidirectional`, and a body that confirms on both a
pristine and a repaired donor is reclassified VACUOUS, not TRANSFERS. Without this
the experiment's success condition would be satisfiable by the worst possible
falsifier.

Run:  python3 scripts/prereg_repointing_experiment_2026-10-02.py
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_SPEC = importlib.util.spec_from_file_location(
    "_c1", ROOT / "scripts" / "supply_cause1_is_path_portability_2026-10-02.py")
_C1 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_C1)


def main() -> int:
    print(__doc__.split("Run:")[0].rstrip())
    print("\n" + "=" * 78)
    print("POPULATION AS IT STANDS IN THIS CHECKOUT (executed, not projected)")
    print("=" * 78)

    rows = _C1.entries()
    post = {k: v for k, v in rows.items()
            if _C1.expno(k[0]) is None or _C1.expno(k[0]) >= 42}
    strata: Counter[str] = Counter()
    donors_available: Counter[str] = Counter()

    # Donor availability, by suffix, in this checkout. A stratum with no donors
    # is UNREPOINTABLE wholesale and the experiment cannot be run on it.
    by_suffix: dict[str, int] = Counter()
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix in (".py", ".md", ".json", ".toml", ".txt"):
            by_suffix[p.suffix] += 1

    for (run, cid), (r, tgt, body, e) in post.items():
        if not body or _C1.verdict(e) != "CONFIRMED":
            continue
        if _C1.ABS_RE.search(body):
            s = "S_abs"
        elif _C1.FILE_RE.search(body):
            s = "S_rel"
        else:
            s = "S_non"
        strata[s] += 1
        named = set(_C1.FILE_RE.findall(body))
        if any(by_suffix.get(pathlib.Path(n).suffix, 0) >= 2 for n in named):
            donors_available[s] += 1

    N = sum(strata.values())
    print(f"  post-feature criticals                 : {len(post)}")
    print(f"  ...CONFIRMED and carrying a body (= P)  : {N}")
    for s in ("S_rel", "S_abs", "S_non"):
        _C1.show(f"  {s} share of P", strata[s], N, pad=34)
    print(f"\n  donors exist in this checkout for: "
          f"S_rel {donors_available['S_rel']}/{strata['S_rel']}, "
          f"S_abs {donors_available['S_abs']}/{strata['S_abs']}")
    print(f"  candidate donor files by suffix: {dict(by_suffix)}")

    # Is the pre-registered precision reachable at this n? Width of the Wilson
    # interval at the least-favourable p (0.5), which is the widest it can be.
    lo, hi, _ = _C1.wilson(strata["S_rel"] // 2, strata["S_rel"])
    width = 100 * (hi - lo)
    print(f"\n  WIDEST Wilson width on break_rate(S_rel) at n={strata['S_rel']}"
          f" (p=0.5): {width:.2f} points")
    print(f"  pre-registered adequacy threshold: < 20.00 points  -> "
          f"{'ADEQUATE' if width < 20 else 'UNDERPOWERED: report the width, do not narrow the claim'}")
    print(f"\n  treatment vs ceiling comparison is available: "
          f"{strata['S_rel'] > 0 and strata['S_non'] > 0}")
    print("  NOT YET RUN. This file commits the design; it dispatches nothing.")
    return 0


if __name__ == "__main__":
    import argparse
    argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None).parse_args()
    raise SystemExit(main())
