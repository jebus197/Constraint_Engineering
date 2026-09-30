#!/usr/bin/env python3
"""FALSIFIER: the harness carries TWO independent fenced-Python extractors on
its two live prose paths, and they DISAGREE about whether a document carries
code.

Run from the repository root:

    python3 scripts/two_fence_extractors_disagree_2026-09-30.py

WHY THIS IS A PRODUCER/CONSUMER TEST, NOT A GREP. Both extractors are live
code reachable on a real run, and both answer the SAME question -- "does this
prose target carry Python?" -- about the SAME target:

  A. `reference_runner_v3._gateable_source`, via `_MD_PY_FENCE_ANY`.
     Decides what S_k's hard gates parse, and -- load-bearing -- whether the
     A19 prose-scoring flag engages AT ALL: `_scoring_prose` is conjoined with
     `bool(_reducible)` at reference_runner_v3.py:11404.

  B. `bugzilla_loop.run_verification`, via `_PY_FENCE`.
     Decides whether close-the-loop returns NO_APPLICABLE_CHECKS having read
     nothing, or runs its ast.parse veto over the listings
     (bugzilla_loop.py:462-514). This function's own comments record that
     answering this question wrongly HALTED the 2026-08-01 control run, three
     times, three different ways.

`execute-do-not-grep`: both are CALLED, on the same bytes, and their outputs
compared. Their regexes are printed for the reader but NO regex is retyped and
no verdict here is read off a pattern.

AN EARLIER VERSION OF THIS SCRIPT WAS ITSELF WRONG AND IS RECORDED AS SUCH.
It compared A against `run_verification`'s OUTCOME, treating
NO_APPLICABLE_CHECKS as "B saw no code". That is false: bugzilla_loop.py:496
returns NO_APPLICABLE_CHECKS when the listings were found AND PARSED CLEANLY,
because a clean parse is a veto that passed, not a check that ran. The bad
instrument reported the canonical ```python fence as a disagreement. The probe
below therefore compares the EXTRACTORS, which is the quantity actually in
question.

THE HARD ASSUMPTION UNDER TEST: that A and B agree, so "carries code" is a
single-valued property of the harness.

FALSIFIED (AssertionError) iff any document splits them. Clean exit iff they
agree everywhere -- in which case the assumption survives and there is no
finding here.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

BODY = "x = 1\nassert x == 1\n"

# Fence shapes a real author produces. DATA only; no detector logic retyped.
PROBES = {
    "```python          canonical": f"# D\n\n```python\n{BODY}```\n",
    "```py              abbrev": f"# D\n\n```py\n{BODY}```\n",
    "```Python          capitalised": f"# D\n\n```Python\n{BODY}```\n",
    "```python3         versioned": f"# D\n\n```python3\n{BODY}```\n",
    "~~~python          tilde fence": f"# D\n\n~~~python\n{BODY}~~~\n",
    "```python title=   attributes": f"# D\n\n```python title=\"a.py\"\n{BODY}```\n",
    "```{python}        Quarto/Rmd": "# D\n\n```{python}\n" + BODY + "```\n",
    "```                bare fence": f"# D\n\n```\n{BODY}```\n",
    "```python  CRLF    Windows": "# D\r\n\r\n```python\r\nx = 1\r\nassert x == 1\r\n```\r\n",
    "> ```python        blockquoted": f"# D\n\n> ```python\n> x = 1\n> ```\n",
    "    ```python      list-indented": "# D\n\n-  item:\n\n    ```python\n    x = 1\n    ```\n",
    "no code at all": "# D\n\nThe mood in the room improved.\n",
    "computable claim, no fence": "# D\n\nThe mean of 2, 4 and 6 is 4.5.\n",
}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Compares the harness's two live fenced-Python extractors "
                    "by calling both on identical bytes. Writes nothing.")
    ap.parse_args(argv)

    from reference_runner_v3 import _gateable_source, _MD_PY_FENCE_ANY
    from bugzilla_loop import _PY_FENCE

    print("the two live extractors, for the reader (NOT the basis of any "
          "verdict below):")
    print(f"  A  _MD_PY_FENCE_ANY = {_MD_PY_FENCE_ANY.pattern!r}")
    print(f"  B  _PY_FENCE        = {_PY_FENCE.pattern!r}\n")

    print(f"{'probe':34s} {'A sees code':>12s} {'B sees code':>12s}   agree")
    print("-" * 74)

    disagreements = []
    for label, doc in PROBES.items():
        # --- A: CALLED through its real entry point --------------------
        red, _why = _gateable_source(doc, "doc.md")
        a = red is not None
        # --- B: CALLED, the exact expression bugzilla_loop.py:468 uses --
        b = bool(_PY_FENCE.findall(doc))
        ok = (a == b)
        if not ok:
            disagreements.append((label, a, b))
        print(f"{label:34s} {str(a):>12s} {str(b):>12s}   "
              f"{'ok' if ok else 'DISAGREE'}")

    print("-" * 74)
    print(f"probes = {len(PROBES)}   disagreements = {len(disagreements)}")

    if not disagreements:
        print("\nNOT FALSIFIED: the extractors agreed on every probe.")
        return 0

    print("\nDISAGREEMENTS:")
    for label, a, b in disagreements:
        print(f"   {label:34s} A={a}  B={b}")
    print("\nCONSEQUENCE. Every disagreement is A=True, B=False: the S_k path "
          "sees code that close-the-loop cannot. On such a document the A19 "
          "flag engages and the prose gates run, while close-the-loop reads "
          "NOTHING and returns NO_APPLICABLE_CHECKS with the message 'carries "
          "no fenced Python listing' -- which is false of the document. The "
          "two paths disagree about the target's substrate, and the failure "
          "direction is that the weaker claim ('no code here') is the one "
          "recorded in the log.")
    print("\nFALSIFIED")
    raise AssertionError(
        f"{len(disagreements)} of {len(PROBES)} probes split the harness's two "
        f"live fenced-Python extractors: "
        f"{[d[0].strip() for d in disagreements]}"
    )


if __name__ == "__main__":
    sys.exit(main())
