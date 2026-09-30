#!/usr/bin/env python3
"""FALSIFIER / REGRESSION GUARD: every live prose path must agree about whether
a document carries Python.

Run from the repository root:

    python3 scripts/one_extractor_invariant_2026-09-30.py

This is the CONSUMER-SIDE form of
`scripts/two_fence_extractors_disagree_2026-09-30.py`. That script compares the
two regex objects. This one compares what the two live ENTRY POINTS actually
do, which is the property that matters and the one `execute-do-not-grep`
demands:

  A. `reference_runner_v3._gateable_source(doc, path)` -- gates S_k, and
     decides whether the A19 prose-scoring flag engages at all
     (reference_runner_v3.py:11404).
  B. `bugzilla_loop.run_verification(path, ...)` -- decides whether
     close-the-loop reads the listings or returns NO_APPLICABLE_CHECKS having
     read nothing.

B's "I found listings" signal is `vetoes_run` being non-empty: bugzilla_loop
records the ast.parse veto there whenever listings were extracted, and leaves
it empty on the no-code path (bugzilla_loop.py:462-514). It is NOT the
outcome -- NO_APPLICABLE_CHECKS is returned BOTH when nothing was found AND
when listings were found and parsed cleanly, because a clean parse is a veto
that passed rather than a check that ran. An earlier draft of the sibling
script used the outcome and reported a false disagreement on the canonical
```python fence. That error is recorded here so the next reader does not
repeat it.

PRE-FIX MEASUREMENT, for the record: 3 of these 13 shapes split the two paths
(tilde fence, info-string attribute, CRLF document), and a fourth
(list-indented) produced a false FAIL -- "the fix leaves 1 of 1 listing(s)
unparseable: unexpected indent" against a document whose Python is valid --
because the narrow regex did not strip the markdown prefix.

FALSIFIED (AssertionError) iff any shape splits the two live paths, or any
shape with valid Python produces a FAIL. Clean exit iff the invariant holds.
"""
from __future__ import annotations

import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

B = "x = 1\nassert x == 1\n"

# (document, does it contain VALID python?)
PROBES = {
    "```python          canonical": (f"# D\n\n```python\n{B}```\n", True),
    "```py              abbrev": (f"# D\n\n```py\n{B}```\n", True),
    "```Python          capitalised": (f"# D\n\n```Python\n{B}```\n", None),
    "```python3         versioned": (f"# D\n\n```python3\n{B}```\n", None),
    "~~~python          tilde fence": (f"# D\n\n~~~python\n{B}~~~\n", True),
    "```python title=   attributes": (f"# D\n\n```python title=\"a.py\"\n{B}```\n", True),
    "```{python}        Quarto/Rmd": ("# D\n\n```{python}\n" + B + "```\n", None),
    "```                bare fence": (f"# D\n\n```\n{B}```\n", None),
    "```python  CRLF    Windows": ("# D\r\n\r\n```python\r\nx = 1\r\nassert x == 1\r\n```\r\n", True),
    "> ```python        blockquoted": ("# D\n\n> ```python\n> x = 1\n> ```\n", True),
    ">  ```python       bq + indent": ("# D\n\n>  ```python\n>  x = 1\n>  ```\n", True),
    "    ```python      list-indented": ("# D\n\n-  item:\n\n    ```python\n    x = 1\n    ```\n", True),
    "no code at all": ("# D\n\nThe mood in the room improved.\n", False),
    "computable claim, no fence": ("# D\n\nThe mean of 2, 4 and 6 is 4.5.\n", False),
}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(
        description="Drives both live prose entry points on identical bytes "
                    "and asserts they agree. Writes only to a temp dir.")
    ap.parse_args(argv)

    from reference_runner_v3 import _gateable_source
    from bugzilla_loop import run_verification, VerificationOutcome

    print(f"{'probe':34s} {'A sees code':>12s} {'B sees code':>12s} "
          f"{'B outcome':>22s}  ok")
    print("-" * 92)

    splits, false_fails = [], []
    with tempfile.TemporaryDirectory() as td:
        for label, (doc, valid_py) in PROBES.items():
            a = _gateable_source(doc, "doc.md")[0] is not None
            p = pathlib.Path(td) / "doc.md"
            p.write_text(doc, encoding="utf-8", newline="")
            vr = run_verification(p, test_cmd=None, timeout=20)
            b = bool(vr.vetoes_run)
            ok = (a == b)
            if not ok:
                splits.append((label, a, b))
            # A document whose Python is valid must never come back FAIL.
            if valid_py is True and vr.outcome is VerificationOutcome.FAIL:
                false_fails.append((label, vr.failures[:1]))
            print(f"{label:34s} {str(a):>12s} {str(b):>12s} "
                  f"{vr.outcome.name:>22s}  {'ok' if ok else 'SPLIT'}")

    print("-" * 92)
    print(f"probes = {len(PROBES)}   path splits = {len(splits)}   "
          f"false FAILs on valid Python = {len(false_fails)}")

    if not splits and not false_fails:
        print("\nINVARIANT HOLDS: both live prose paths agree on every shape, "
              "and no document carrying valid Python is accused of a syntax "
              "failure.")
        print("NOT FALSIFIED")
        return 0

    for label, a, b in splits:
        print(f"   SPLIT      {label:34s} A={a} B={b}")
    for label, why in false_fails:
        print(f"   FALSE FAIL {label:34s} {why}")
    print("\nFALSIFIED")
    raise AssertionError(
        f"{len(splits)} shape(s) split the live prose paths and "
        f"{len(false_fails)} document(s) carrying valid Python were reported "
        f"FAIL.")


if __name__ == "__main__":
    sys.exit(main())
