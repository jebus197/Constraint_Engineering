#!/usr/bin/env python3
"""Does the EXISTING verification channel already decide prose-borne claims the
S_k triage cannot see?  Executed through `falsifier_verify.reverify_falsifier`,
the runner's own decider -- not by reading the fixtures.

THE QUESTION THIS SETTLES FOR THE 2026-09-30 DESIGN REVIEW. The brief's Q1 asks
what "intelligence first, tools second" requires of the architecture. If the
corpus falsifiers still discriminate true-from-false on documents whose fenced
listings have been STRIPPED -- documents `compute_sk` refuses to engage with at
all (measured NO_SCORE by fable_sk_verdict_is_syntax_bound_2026-09-30.py) --
then the VERIFY stage needs no new machinery for prose: only the triage (the
REDUCE decision) is syntax-bound. The simplest sufficient design then touches
admissibility, not verification.

MATRIX, per fixture, all through reverify_falsifier:
  intact document            -> expected CONFIRMED  (false claim present)
  intact + correct_fix       -> expected REFUTED    (claim corrected)
  stripped document          -> measured, not assumed: does the falsifier
                                still read its values from prose?
  stripped + prose-only fix  -> measured
  empty document             -> expected ERROR      (2026-09-30 abstain guard)

Writes only to a tempdir it removes. Dispatches no model.
"""
from __future__ import annotations

import pathlib
import re
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))
sys.path.insert(0, str(REPO / "bench" / "tests" / "fixtures" / "stem"))


def main(argv=None) -> None:
    import argparse
    ap = argparse.ArgumentParser(
        description="Run every STEM fixture falsifier via reverify_falsifier "
                    "against intact / fixed / fence-stripped / empty copies of "
                    "its document. Temp files only; no model dispatched.")
    ap.parse_args(argv)

    from falsifier_verify import reverify_falsifier
    import stem_fixtures as S

    def strip(text):
        return re.sub(r"```.*?```", "", text, flags=re.S)

    results = {}
    with tempfile.TemporaryDirectory() as td:
        tdp = pathlib.Path(td)
        for fx in S.load_all():
            prose_fix = tuple(p for p in fx.correct_fix if p.region != "listing")
            variants = {
                "intact": fx.document,
                "fixed": fx.apply(fx.correct_fix),
                "stripped": strip(fx.document),
                "stripped_fixed": strip(fx.apply(prose_fix)) if prose_fix else None,
                "empty": "",
            }
            row = {}
            for name, text in variants.items():
                if text is None:
                    row[name] = "N/A"
                    continue
                doc = tdp / f"{fx.key}_{name}{pathlib.Path(fx.doc_name).suffix}"
                doc.write_text(text, encoding="utf-8")
                row[name] = reverify_falsifier(
                    fx.falsifier(doc), repo_root=str(REPO), cwd=str(tdp))
            results[fx.key] = row
            print(f"  {fx.key:12s} " + "  ".join(
                f"{k}={v}" for k, v in row.items()))

    n = len(results)
    ok_bidir = sum(1 for r in results.values()
                   if r["intact"] == "CONFIRMED" and r["fixed"] == "REFUTED")
    ok_strip = sum(1 for r in results.values() if r["stripped"] == "CONFIRMED")
    ok_strip_fix = sum(1 for r in results.values()
                       if r["stripped_fixed"] == "REFUTED")
    n_strip_fix = sum(1 for r in results.values() if r["stripped_fixed"] != "N/A")
    ok_empty = sum(1 for r in results.values() if r["empty"] == "ERROR")
    print(f"\n  bidirectional on intact docs (CONFIRMED/REFUTED): {ok_bidir} of {n}")
    print(f"  still CONFIRM the false claim with every fence stripped: "
          f"{ok_strip} of {n}")
    print(f"  still REFUTE after a prose-only correct fix, stripped: "
          f"{ok_strip_fix} of {n_strip_fix}")
    print(f"  abstain (ERROR) on an empty document: {ok_empty} of {n}")
    print("  substrate_independent_verify = "
          f"{ok_strip} of {n} falsifiers decide documents compute_sk scores "
          "NO_SCORE")


if __name__ == "__main__":
    main(sys.argv[1:])
