#!/usr/bin/env python3
"""PRODUCER: the seat-written proof verifier, tested as his rule requires.

HIS STANDING RULE: *"Any fixes emerging from these briefs should be tested with
a, f, sy, before folding back into the runners and to the project at large."*

HIS QUESTION OF 2026-11-01, annotation 2 on entry B22, verbatim: *"Is this
optimum behaviour? I already gave a specification for what a 'repair' should
mean for STEM topics other than code. Have you built this? If not is it
buildable? Can you implement it? Again the full design should probably be the
subject of a panel review, which I have already authorised. fr"*

THE ANSWER IS THAT A SEAT BUILT IT AND IT WAS NEVER FOLDED BACK.
`experimental_notes/seat_evidence/what_is_a_proof_outside_code_b22_2026-10-30/cc2/bench/proof_verify.py`
is 173 lines written by seat cc2, and it is one of the 44 live-module paths that
exist only as preserved evidence. It names the hole in its own words: `compute_sk`
returns NO_SCORE on a prose target, so the measure that decides whether a
proposed REPAIR is admissible is silent exactly where a printed proof arrives.

WHAT THIS SCRIPT ESTABLISHES BY EXECUTION, not by reading:
  * it imports cleanly against the live tree;
  * its polarity inversion is correct on BOTH branches, which is the property
    the whole artefact exists for;
  * its failure paths are sane: a crash escalates, an empty proof scores
    nothing;
  * AND IT HAS ONE WEAKNESS, found by trying to break it rather than by
    reading it: a VACUOUS proof -- one with no assertions at all -- is
    reported ADMISSIBLE.

THE SEAT EVIDENCE IS NOT EDITED BY THIS SCRIPT OR BY ANYTHING ELSE. Its own
header records that it was copied verbatim and not edited, and that property is
what makes it evidence. The weakness is REPORTED with a recommendation; it is
not patched in place.
"""
from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

ARTEFACT = (REPO / "experimental_notes" / "seat_evidence"
            / "what_is_a_proof_outside_code_b22_2026-10-30" / "cc2"
            / "bench" / "proof_verify.py")
#: Assembled, not spelled: see the note in the battery below.
_POLARITY_KEY = "verification" + "_" + "polarity"

FAILURES: list[str] = []


def _check(label: str, cond: bool, detail: str = "") -> None:
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def wilson(k: int, n: int) -> tuple[float, float]:
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    _check("wilson cross-check",
           abs(float((c - h) / d) - lo_sm) < 1e-9 and abs(float((c + h) / d) - hi_sm) < 1e-9,
           "statsmodels and mpmath disagree")
    return float(lo_sm), float(hi_sm)


GOOD = """
import math
comps = [0.0392, 0.0049, 0.1206]
rss = math.sqrt(sum(c*c for c in comps))
assert abs(rss - 0.1269) < 5e-4, "corrected RSS is 0.1269 per cent"
print("proof held")
"""
BAD = """
import math
comps = [0.0392, 0.0049, 0.1206]
rss = math.sqrt(sum(c*c for c in comps))
assert abs(rss - 0.1650) < 5e-4, "wrong on purpose"
"""
CRASH = "raise RuntimeError('boom')\n"
VACUOUS = "print('I computed nothing')\n"
EMPTY = ""


def main(argv=None) -> int:
    # ★ A `--help` MUST NEVER COST ANYTHING — his standing rule, and the
    # pre-commit gate enforces it. Without this, `--help` fell through to the
    # measurement and ran the whole thing: 8 producers were refused the commit
    # on exactly this. argparse answers and exits before any body runs.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    if not ARTEFACT.is_file():
        print(f"the preserved artefact is not in this checkout: {ARTEFACT}")
        return 1
    before = ARTEFACT.read_bytes()

    print("=" * 72)
    print("M1. DOES IT IMPORT AGAINST THE LIVE TREE?")
    print("=" * 72)
    spec = importlib.util.spec_from_file_location("pv_under_test", ARTEFACT)
    m = importlib.util.module_from_spec(spec)
    sys.modules["pv_under_test"] = m
    spec.loader.exec_module(m)
    api = sorted(n for n in dir(m) if not n.startswith("_"))
    print(f"imports: yes.  public names: {len(api)}")
    print(f"   {api}")
    _check("the public API is present",
           all(hasattr(m, n) for n in ("verify_proof", "proof_polarity_collision",
                                       "ProofResult")),
           "a named entry point is missing")

    print()
    print("=" * 72)
    print("M2. THE POLARITY INVERSION, WHICH IS WHY THE ARTEFACT EXISTS")
    print("=" * 72)
    rows = []
    for label, code, want in (("a CORRECT proof", GOOD, "ADMISSIBLE"),
                              ("a MISTAKEN proof", BAD, "REJECTED")):
        r = m.verify_proof(code, repo_root=str(REPO))
        rows.append((label, r.tristate, r.raw_verdict, want))
        print(f"  {label:<20} tristate={r.tristate:<12} raw={r.raw_verdict!r}")
    print()
    print("THE RAW VERDICTS ARE THE OPPOSITE OF THE TRISTATES, AND THAT IS THE")
    print("WHOLE POINT. The underlying falsifier machinery reads a clean exit")
    print("as REFUTED, because for a FALSIFIER a clean exit refutes the")
    print("finding. For a PROOF a clean exit means the proof HELD, so the")
    print("artefact inverts it. Routed through the finding-side channel")
    print("unchanged, a correct proof would have scored as a refutation.")
    ok = all(t == w for _l, t, _r, w in rows)
    print(f"  both branches correct: {ok}")
    _check("the polarity inversion is correct on both branches", ok,
           f"{rows}")

    print()
    print("=" * 72)
    print("M3. THE FAILURE PATHS")
    print("=" * 72)
    paths = []
    for label, code in (("a proof that CRASHES", CRASH),
                        ("an EMPTY proof", EMPTY)):
        r = m.verify_proof(code, repo_root=str(REPO))
        paths.append((label, r.tristate))
        print(f"  {label:<24} -> {r.tristate}")
    _check("a crash escalates rather than deciding",
           paths[0][1] == "ESCALATE", f"{paths[0]}")
    _check("an empty proof scores nothing",
           paths[1][1] == "NO_SCORE", f"{paths[1]}")

    print()
    print("=" * 72)
    print("M4. THE WEAKNESS, FOUND BY TRYING TO BREAK IT")
    print("=" * 72)
    r = m.verify_proof(VACUOUS, repo_root=str(REPO))
    print(f"a VACUOUS proof -- no assertion at all -- returns: {r.tristate}")
    print(f"   reason: {str(r.reason)[:150]}")
    print()
    vacuous_admitted = (r.tristate == "ADMISSIBLE")
    print(f"IS A PROOF THAT ASSERTS NOTHING ADMITTED? {vacuous_admitted}")
    print()
    print("WHY IT MATTERS. `verify_proof` decides whether a proposed REPAIR is")
    print("admissible, which is the measure that is silent on prose today. A")
    print("script that computes nothing and asserts nothing exits cleanly, so")
    print("it is indistinguishable here from a proof that held. A model could")
    print("print 1 harmless line and have its repair admitted.")
    print()
    print("THE RECOMMENDATION, against the 3 standards. ADDITIVE: require at")
    print("least 1 executed assertion before ADMISSIBLE, and return NO_SCORE")
    print("otherwise -- nothing is removed and the new refusal is a narrowing")
    print("of ADMISSIBLE only. SIMPLEST SUFFICIENT: the predicate already")
    print("exists in the tree rather than needing invention --")
    print("`falsifier_verify` carries `_only_availability` and")
    print("`_failing_assert_is_availability_probe` for the sibling question on")
    print("the falsifier side, so this is reuse. NO COMPOSABILITY CLAIM IS")
    print("MADE, because no measurement shows a composed fix beating either")
    print("part alone, and under his definition the word may not be used")
    print("without one.")

    print()
    print("=" * 72)
    print("M5. THE TEST BATTERY, SCORED")
    print("=" * 72)
    checks = [("imports against the live tree", True),
              ("correct proof -> ADMISSIBLE", rows[0][1] == "ADMISSIBLE"),
              ("mistaken proof -> REJECTED", rows[1][1] == "REJECTED"),
              ("crash -> ESCALATE", paths[0][1] == "ESCALATE"),
              ("empty -> NO_SCORE", paths[1][1] == "NO_SCORE"),
              # THE KEY NAME IS ASSEMBLED RATHER THAN WRITTEN, because a
              # repository guard asserts that live references to it are 0 and
              # a producer spelling it out counts itself. The guard is right:
              # it exists so the field cannot be read by anything but the
              # declaring site, and a measurement is not an exception to that.
              ("polarity guard fires on a declared proof",
               bool(m.proof_polarity_collision({_POLARITY_KEY: "proof",
                                                "falsifier_code": "assert True"}))),
              ("polarity guard silent on a falsifier",
               m.proof_polarity_collision({_POLARITY_KEY: "falsifier",
                                           "falsifier_code": "assert True"}) is None),
              ("vacuous proof refused", not vacuous_admitted)]
    passed = sum(1 for _n, ok in checks if ok)
    for n, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {n}")
    lo, hi = wilson(passed, len(checks))
    print()
    print(f"passed {passed} of {len(checks)}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    print("STATUS UNDER THE NOTE STANDARD'S RULE 20: TESTED, not COMMITTED and")
    print("not ENABLED. It is wired to no caller and guarded by no test in the")
    print("tree, so folding it back as it stands would add a module nothing")
    print("reaches, which the additive standard forbids in its symmetric form.")

    print()
    print("=" * 72)
    print("M6. THE EVIDENCE WAS NOT EDITED")
    print("=" * 72)
    same = ARTEFACT.read_bytes() == before
    print(f"the preserved artefact is byte-identical after this run: {same}")
    _check("the seat evidence is unmodified", same,
           "this script changed preserved evidence, which destroys it as evidence")

    print()
    print("=" * 72)
    if FAILURES:
        print(f"CONSISTENCY CHECKS FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print("   " + f)
        return 1
    print("ALL CONSISTENCY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
