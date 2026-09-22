#!/usr/bin/env python3
"""FALSIFIER: blob-level hard gates swallow a fix that breaks a GOOD listing.

THE CLAIM. `_gateable_source` concatenates every fenced listing into ONE blob
and the baseline guard tests THAT BLOB. On a document that also carries an
illustrative fragment (e.g. a bare `elif` arm -- never parseable alone), the
baseline blob is unparseable, so ANY post-fix syntax failure is excused as
"also failed before this fix" -- including a fix that newly breaks a listing
that parsed perfectly at baseline. The gate returns 1 where the defect it
exists to catch is present. The docstring of `_baseline_code_is_parseable`
admits the residue ("a fix that breaks a listing DIFFERENTLY from how the
baseline was broken is swallowed"); this demonstrates it is not an edge case
but the generic state of any real design note, since illustrative fragments
are routine.

Fails (raises AssertionError / prints FALSIFIED) iff the defect is present.
Exits clean iff per-hunk gating convicts the regression while still excusing
the untouched fragment.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

from bench.reference_runner_v3 import (  # noqa: E402
    _run_hard_gate_ast, _run_hard_gate_compile,
)

BASELINE = """# Design note

A good, complete listing:

```python
def good():
    return 1
```

An ILLUSTRATIVE FRAGMENT -- one arm of a conditional, never parseable alone:

```python
elif retriable(exc):
    delay *= 2
```
"""

# The fix breaks the previously-GOOD listing and leaves the fragment alone.
BROKEN = BASELINE.replace("def good():", "def good(:")

PATH = "/staged/design_note.md"


def main() -> None:
    failures = []

    # 1. THE DEFECT. A fix that breaks working code must be REJECTED even
    #    though an unrelated fragment made the baseline blob unparseable.
    g1, d1 = _run_hard_gate_ast(BROKEN, PATH, original_source=BASELINE)
    g2, d2 = _run_hard_gate_compile(BROKEN, PATH, original_source=BASELINE)
    #    STRENGTHENED 2026-09-22 (CC1): this tested the PRODUCT g1*g2, which is
    #    0 whenever EITHER gate convicts -- so a regression in ONE gate passed.
    #    Measured by mutation: deleting the per-hunk call from either gate alone
    #    left this falsifier and cc2's test both green. Assert each gate.
    for _name, _g, _d in (("_run_hard_gate_ast", g1, d1),
                          ("_run_hard_gate_compile", g2, d2)):
        if _g != 0:
            failures.append(
                f"a fix that broke a previously-parseable listing passed "
                f"{_name} ({_g!r} {_d!r}) because the baseline BLOB was "
                f"unparseable -- the excuse is not attributable per hunk")

    # 2. NON-REGRESSION. The guard's original purpose must survive: a fix that
    #    touches only prose on the same document is NOT convicted for the
    #    fragment's pre-existing unparseability.
    prose_fix = BASELINE.replace("A good, complete listing",
                                 "A good and complete listing")
    g1p, d1p = _run_hard_gate_ast(prose_fix, PATH, original_source=BASELINE)
    g2p, d2p = _run_hard_gate_compile(prose_fix, PATH, original_source=BASELINE)
    if g1p * g2p != 1:
        failures.append(
            f"a prose-only edit on a fragment-bearing document was convicted "
            f"(g1={g1p!r} {d1p!r} / g2={g2p!r} {d2p!r})")

    # 3. NON-REGRESSION. Editing the fragment itself (still a fragment) is
    #    excused: the failure is not attributable to the fix.
    frag_fix = BASELINE.replace("delay *= 2", "delay *= 3")
    g1f, d1f = _run_hard_gate_ast(frag_fix, PATH, original_source=BASELINE)
    if g1f != 1:
        failures.append(
            f"editing an illustrative fragment into another fragment was "
            f"convicted (g1={g1f!r} {d1f!r})")

    if failures:
        print("FALSIFIED")
        for f in failures:
            print(" -", f)
        raise AssertionError("; ".join(failures))
    print("clean: per-hunk attribution convicts the regression, excuses the "
          "fragment, and admits the prose edit")


if __name__ == "__main__":
    # WIRED 2026-09-22 (CC1). As delivered by the seat this ran the whole
    # falsifier on `--help`, which the project forbids: a help flag must
    # answer, never act. Caught by test_help_never_acts_2026-09-11.
    from _cli_help import answer_help   # scripts/ is sys.path[0] here
    answer_help(__doc__, __file__)
    main()
