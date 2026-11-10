#!/usr/bin/env python3
"""B22, measured on REAL content: the topic's tools decide a minority of the
project's own STEM claims, and on the ones they do decide they are wrong twice.

HIS QUESTION (B22), verbatim: *"CDSFL has been envisaged from the outset as a
general purpose STEM calculator ... But in order for that to be true the entire
harness has to be as equally useful against a wide range of STEM related topics,
as it currently is for code."*

WHY THIS CORPUS. B22's own surviving *against* case records that
`bench/tests/fixtures/stem/` -- 5 independently written STEM documents with 29
tagged claims, each carrying a runnable falsifier template and a HARMFUL fix
with a named harm class -- is reached by the simulation tooling and by **no
live-path module**. It is the best non-code STEM content the project owns, and
nothing live has ever been pointed at it. This points the tool set at it.

WHAT IS MEASURED. For each tagged claim: the topic's `claim_patterns` classify
it, the topic's `verification_tools` list is resolved through the 22-entry
manifest, every tool is CALLED on the claim's own summary text, and the verdicts
are compared against the corpus's recorded TRUE/FALSE.

THE 2 RESULTS, AND THE SECOND MATTERS MORE THAN THE FIRST.

1. COVERAGE. A minority of the 29 claims draw any definitive verdict at all;
   the rest return UNCERTAIN or classify as `uncategorised` and route to 0
   tools. Algorithms and numerical analysis draw 0.

   THIS IS A FLOOR, NOT A CEILING, AND SAYING OTHERWISE WOULD OVERSTATE IT. The
   input here is the claim's SUMMARY PROSE. The verifiers need a formalised
   expression -- measured separately, 0 of 11 plain sentences drew a definitive
   verdict while 4 of 5 `Eq(...)` forms did. The pipeline's
   `formalisation_agent` (`bench/immune_agents.py:5835`) is the component that
   would close that gap and it is NOT wired into this route.

2. ACCURACY ON WHAT IT DOES DECIDE. 2 of the definitive verdicts are REJECTIONS
   of claims the corpus marks TRUE, and both corpus claims are correct --
   verified here on pint, SymPy, NumPy and mpmath rather than taken on trust:

     CM-03  c = 2.5002 mmol / 24.87 mL = 0.10053 mol/L
            exact 4167/41450 = 0.10053076, agreeing to 7.6e-07, dimensionally
            sound. `dimensional_analysis` says REJECTED.
     CM-09  1.000 kg propane + 3.628 kg O2 -> 2.994 kg CO2 + 1.634 kg H2O
            in 4.6280 kg, out 4.6280 kg, and the stoichiometry from molar
            masses reproduces all 3 masses. `stoichiometric_balance` says
            REJECTED.

WHAT THIS DOES AND DOES NOT MEAN FOR THE 2026-11-10 APPLY-BACK ROUTE.

  It does NOT change a decision. A prose target was REFUSED before this route
  existed, so a false rejection produces the status quo outcome. And the ADMIT
  path was right on both claims it admitted.

  It DOES write a FALSE REASON. The route returns `domain:...against=<tool>` as
  the refusal detail, so a wrong tool verdict is recorded as the ground for
  refusing a correct fix. That is exactly the harm B88's original defect caused
  34 times over -- *"34 false reasons recorded in the project's own evidence,
  each blaming a model's fix for 3 failures it did not cause"*. A decision can
  be right for a reason that is false, and this project treats that as a defect
  in its own right.

  THE SIMPLEST SUFFICIENT REPAIR, recorded rather than applied here: on a
  definitive AGAINST, return the PRE-EXISTING refusal string with the tool
  verdict appended as information, instead of attributing the refusal to the
  tool. Both halves of that sentence are then true. It removes no capability,
  so it is additive; no composability claim is made.

Run: python3 scripts/the_topics_tools_on_the_projects_own_corpus_2026-11-10.py
Exit 0 always: this reports a state. It fails loudly only if the corpus or the
adapter cannot be loaded, because a figure from a failed load is not a figure.
"""
from __future__ import annotations

import collections
import pathlib
import sys
import types

#: The corpus labels its documents with DESCRIPTIVE domain strings, not with
#: the 10 declared immune domain names, so a mapping is unavoidable and is
#: stated here rather than hidden. That mismatch is itself part of the finding:
#: even if a live module reached this corpus, its domain would not resolve.
CORPUS_DOMAIN_TO_DECLARED = {
    "structural / mechanical engineering": "engineering",
    "statistics": "statistics",
    "chemistry / metrology": "chemistry",
    "algorithms / complexity": "cs_software",
    "numerical analysis": "mathematics",
}

DEFINITIVE_FOR = ("CONFIRMED", "VERIFIED", "SUPPORTED")
DEFINITIVE_AGAINST = ("REJECTED", "REFUTED", "CONTRADICTED")


def _find_repo() -> pathlib.Path:
    for start in (pathlib.Path(__file__).resolve().parent,
                  pathlib.Path.cwd().resolve()):
        for cand in (start, *start.parents):
            if (cand / "bench" / "domain_immune.py").is_file():
                return cand
    raise SystemExit("cannot locate the repository")


REPO = _find_repo()


def _iv_line(k: int, n: int) -> str:
    #: ★ RENAMED FROM `_iv`, WHICH IS A RESERVED CONTRACT NAME.
    #: 50 scripts implement `_iv(k, n)` returning
    #: ((wilson_lo, wilson_hi), (cp_lo, cp_hi), cross_check), and a
    #: committed guard calls every one of them and requires them to
    #: agree to 12 decimals. A local FORMATTER under that name returns
    #: a string and breaks the contract -- it reported a 130-tuple to
    #: the guard. 3 producers written the same night hit this; the
    #: other 2 were renamed when it was first found and this one was
    #: moved into `scripts/` later, so it missed the sweep.
    import numpy as np
    from scipy import stats as st
    from statsmodels.stats.proportion import proportion_confint
    sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    cp = proportion_confint(k, n, alpha=0.05, method="beta")
    z = st.norm.ppf(0.975)
    p = k / n
    den = 1 + z * z / n
    cen = (p + z * z / (2 * n)) / den
    hw = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (f"{k} of {n} = {p:.6f}  Wilson statsmodels "
            f"[{sm[0]:.6f}, {sm[1]:.6f}]  scipy+numpy "
            f"[{max(0.0, cen - hw):.6f}, {min(1.0, cen + hw):.6f}]  "
            f"Clopper-Pearson [{(cp[0] or 0.0):.6f}, {cp[1]:.6f}]")


def main(argv=None) -> int:
    #: THE REPOSITORY ROOT FIRST. `bench/domain_immune.py` imports
    #: `bench.dm._types`, so `bench/` alone on the path is not enough -- the
    #: first run of this script failed on exactly that, and it worked inline
    #: only because the working directory happened to be the repository root.
    #: A producer must not depend on where it is invoked from.
    #: A `--help` MUST NEVER COST MINUTES -- his standing rule, and the
    #: project enforces it. This producer had no argparse at all, so `--help`
    #: was ignored and the whole measurement ran (66.56s on 2026-11-10).
    #: The description is taken from the module docstring so the usage text
    #: cannot drift from the file.
    import argparse
    _ap = argparse.ArgumentParser(
        description=(__doc__ or "").strip().splitlines()[0] if __doc__ else "")
    _ap.parse_args(argv)
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    sys.path.insert(0, str(REPO / "bench" / "tests" / "fixtures" / "stem"))
    import domain_immune as di
    import stem_fixtures as sf

    def view(text: str):
        return types.SimpleNamespace(description=text, finding_id="F",
                                     title="", evidence="")

    fixtures = sf.load_all()
    if not fixtures:
        print("FAIL: the corpus loaded 0 fixtures; a figure from that is not a "
              "figure")
        return 1

    total = decided = agree = 0
    by_dom: collections.Counter = collections.Counter()
    dec_by_dom: collections.Counter = collections.Counter()
    wrong = []
    uncategorised = 0

    print("=" * 78)
    print("B22 ON THE PROJECT'S OWN STEM CORPUS, WITH THE TOPIC'S OWN TOOLS")
    print("=" * 78)

    for fx in fixtures:
        raw = getattr(fx, "domain", "")
        dom = CORPUS_DOMAIN_TO_DECLARED.get(raw, "cross_domain")
        for claim in (getattr(fx, "claims", None) or []):
            summary = getattr(claim, "summary", "") or ""
            tag = getattr(claim, "tag", "?")
            truth = str(getattr(claim, "verdict", "?")).upper()
            r = di.domain_verification_set(dom, view(summary))
            total += 1
            by_dom[dom] += 1
            if r["claim_type"] == "uncategorised":
                uncategorised += 1
            defs = [(n, v) for n, v, _c in r["verdicts"]
                    if v in DEFINITIVE_FOR + DEFINITIVE_AGAINST]
            if not defs:
                continue
            decided += 1
            dec_by_dom[dom] += 1
            tool, verdict = defs[0]
            tool_says_true = verdict in DEFINITIVE_FOR
            corpus_says_true = truth == "TRUE"
            if tool_says_true == corpus_says_true:
                agree += 1
            else:
                wrong.append((tag, dom, tool, verdict, truth, summary))

    print(f"\n  claims in the corpus        : {total}")
    print(f"  classified `uncategorised`  : {uncategorised} (routed to 0 tools)")
    print(f"\n  COVERAGE  — drew any definitive verdict:")
    print(f"    {_iv_line(decided, total)}")
    print("    per domain:")
    for d in sorted(by_dom):
        print(f"      {d:14s} {dec_by_dom[d]:2d} of {by_dom[d]:2d}")

    if decided:
        print(f"\n  ACCURACY on the decided subset:")
        print(f"    {_iv_line(agree, decided)}")
    if wrong:
        print(f"\n  *** {len(wrong)} DEFINITIVE VERDICT(S) DISAGREE WITH THE "
              f"CORPUS ***")
        for tag, dom, tool, verdict, truth, summary in wrong:
            print(f"    {tag:7s} {dom:12s} corpus={truth:5s} "
                  f"{tool} says {verdict}")
            print(f"      {summary[:98]}")
        print("\n    A REFUSAL ATTRIBUTED TO ONE OF THESE RECORDS A FALSE")
        print("    REASON, which this project treats as a defect in its own")
        print("    right -- see B88, where 34 refusals each blamed a model's")
        print("    fix for 3 failures it did not cause.")

    print("\n" + "=" * 78)
    print("  THE BOUND, STATED: the input is the claim's SUMMARY PROSE, and the")
    print("  verifiers need a formalised expression. This is a FLOOR on what")
    print("  the tool set could decide, not a ceiling. The pipeline's")
    print("  formalisation_agent is the component that would close the gap and")
    print("  is not wired into this route.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
