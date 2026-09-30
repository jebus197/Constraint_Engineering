#!/usr/bin/env python3
"""Q6a(b) of the 2026-09-30 brief: does prose need a NEW fix-efficacy
instrument, or only wiring?  Answered by driving the LIVE probe
(`bench/fix_efficacy.probe`, tripwire -> baseline -> patched) on the STEM
corpus's prose documents.

MEASURED 2026-09-30 (this script's first run, figures in the design note):
  * falsifier bound to the document's ABSOLUTE path -> structural:
    FIX_CURES_ITS_OWN_FALSIFIER in 51.8 s. The apparatus's
    `_retarget_falsifier` rewrites the absolute path into the overlay, so the
    existing instrument ALREADY measures prose fix efficacy end-to-end.
  * falsifier bound to a RELATIVE path -> INDETERMINATE_NO_BASELINE (the
    falsifier cannot find the target from the probe's cwd and the 2026-09-30
    absent-target guard correctly abstains). So the wiring requirement is a
    PATH-BINDING contract, not a new instrument.

FULL-RUN HISTORY, same day: the first --all run measured 2/5 FIX_CURES with
3/5 INDETERMINATE_NOT_INTERCEPTED -- three falsifiers raised AssertionError
(the decider's CONFIRMED token) on evidence-carrier failures, so the probe's
tripwire pass could not distinguish them from target-insensitive falsifiers
and correctly refused a verdict. After the carrier-abstain repair to
`stem_fixtures.py` (AssertionError reserved for a positively located false
claim; carrier/instrument failures exit SystemExit ERROR), the same run
measures **5/5 FIX_CURES** (46.7-49.6 s each).

Default runs ONE fixture (~1 min: three overlay passes). --all runs all five
(~5 min) -- deliberately not the default so a review pass stays cheap.
"""
from __future__ import annotations

import pathlib
import sys
import time

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO / "bench" / "tests" / "fixtures" / "stem"))


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(
        description="Drive the live fix-efficacy probe over STEM corpus prose "
                    "documents with their own correct fixes. Overlay copies "
                    "only; the repository is not modified. No model dispatched.")
    ap.add_argument("--all", action="store_true",
                    help="probe all five fixtures (~5 min) instead of one")
    args = ap.parse_args(argv)

    import stem_fixtures as S
    from fix_efficacy import probe

    fixtures = list(S.load_all())
    if not args.all:
        fixtures = fixtures[:1]

    cures = 0
    for fx in fixtures:
        rel = f"bench/tests/fixtures/stem/docs/{fx.doc_name}"
        fixtxt = "".join(f"<<<< SEARCH\n{p.old}\n====\n{p.new}\n>>>> REPLACE\n"
                         for p in fx.correct_fix)
        t0 = time.monotonic()
        r = probe({"falsifier_code": fx.falsifier(),
                   "proposed_fix": fixtxt}, rel, repo_root=REPO, timeout=25)
        cures += r.outcome.startswith("FIX_CURES")
        print(f"  {fx.key:12s} {r.outcome}  ({time.monotonic() - t0:.1f}s)  "
              f"{r.detail[:90]}")
    print(f"\n  correct fixes measured FIX_CURES: {cures} of {len(fixtures)} "
          f"({'all five' if args.all else 'one fixture; pass --all for five'})")


if __name__ == "__main__":
    main(sys.argv[1:])
