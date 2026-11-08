#!/usr/bin/env python3
"""Put the canonical `_iv` into the producers B135's detector cannot see.

HIS RULING, 2026-11-08, on `The_Gates_Refused_3_Times_2026-11-08.txt`: *"Use the
first fix and not the 'cheaper' second."* Option 1 is to replace the Wilson
detector's PATTERN MATCH with EXECUTION of a shared helper, which the board
guard `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py` already
does for every script defining `def _iv`.

WHY THE CAUSE MATTERS AND HE WAS NOT TOLD IT WHEN HE RULED. All 13 invisible
producers are invisible for 1 reason, measured 2026-11-08: the sample size is
named `nn` in 12 of 13 and `N_` in 1, and the detector's strict pattern requires
the character after the `n` to be whitespace or a bracket. Every one of the 13
computes the identical algebra and asserts it against statsmodels. So option 2
would have been a 1-line widening reaching 13 of 13. His ruling is still right
under this project's own `execute-do-not-grep`: a wider pattern is a better
PROXY, while execution removes the proxy.

THE HELPER IS LIFTED BY AST, BYTE-IDENTICAL, never retyped. A retyped copy is a
2nd implementation wearing the canonical name, and the board guard asserts every
`_iv` agrees with every other at 6 (k, n) pairs.

AND THE DELEGATION IS NOT COSMETIC. Adding `_iv` while leaving the file's own
algebra in place would make the detector rank the producer as cross-checked on
the strength of a helper the producer never calls -- gaming the instrument. Each
file's existing helper is rewritten to call `_iv` and to preserve its own return
shape exactly, and the proof is the file's stdout BYTE FOR BYTE against a
baseline captured before any edit.

★ THIS FILE DELIBERATELY DOES NOT SPELL THE CALL IT IS ABOUT. A first version
quoted the statsmodels Wilson call verbatim in the template docstring, and
`scripts/counting_imports_ranks_producers_backwards_2026-11-03.py` then read
THIS TOOL as a producer carrying a Wilson quantity on 1 route, turning its board
guard red. A transformation tool is not a producer, and a detector cannot tell
the difference when the tool spells the detector's own pattern --
`feedback_a_detector_must_not_spell_out_its_own_pattern_2026-11-02`, the 3rd
instance of that shape on 2026-11-08. The methods are named in prose instead.

ONE REAL DIFFERENCE IS POSSIBLE AND IS CHECKED RATHER THAN ASSUMED. The
canonical helper returns `max(0.0, wl)`, where these producers returned
statsmodels' raw lower bound. At k = 0 that bound can be a tiny negative, which
prints as `-0.0` after rounding -- a form this repository does contain. Any such
change is a changed published figure, not a tidy-up, and is reported.

Exit 0 when every target carries the canonical helper and still prints exactly
what it printed before.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
CANON = REPO / "scripts/how_many_of_the_nights_errors_were_instruments_2026-11-03.py"

#: Files whose own helper returns Wilson as a rounded PERCENTAGE pair. The 3 are
#: textually identical in substance; `rk_pairing_reach` nests its copy inside a
#: function, so the canonical helper goes in at MODULE level regardless -- the
#: guard finds it with `hasattr(module, "_iv")`.
PERCENT_PAIR = [
    "gate_input_is_not_persisted_2026-10-03",
    "rk_pairing_reach_2026-10-03",
    "where_the_plan_went_2026-10-04",
]

#: Files whose own helper returns BOTH intervals as a pair of pairs. Measured
#: 2026-11-08: `panel_harvest_loss` draws BOTH from statsmodels -- `method=
#: "wilson"` and `method="beta"` -- so its "2 routes" are 1 library called
#: twice, which is the exact defect `bench/falsifier_pairing.py` was built for
#: ("statsmodels and scipy both resolve to the identical verifier, so the
#: canonical 2-tool pair was 1 function called twice"). Delegating gives Wilson
#: on statsmodels against mpmath and Clopper-Pearson on scipy against mpmath,
#: at identical values.
BOTH_PAIRS = ["panel_harvest_loss_2026-09-22"]

#: ★ NOT EVERY ONE OF THE 13 CAN BE DELEGATED, AND SAYING SO IS PART OF THE
#: ANSWER TO HIS RULING. `the_joint_debt_is_discharged_by_a_directory_2026-10-14`
#: already computes the 2 routes INDEPENDENTLY -- statsmodels and a hand-written
#: mpmath interval -- and wraps each in a named-failure arm, printing *INTERVAL
#: TOOL MISSING* rather than silently dropping a confidence interval from a
#: reported proportion. Its own comment records why: a swallowed import removes
#: an interval with no trace. The canonical `_iv` imports at call time and would
#: RAISE instead, so delegating this file would REMOVE a deliberate feature.
#: `additive-standard` permits a removal only on a committed measurement showing
#: the replacement dominates on a named property, and there is none: on the
#: happy path the 2 are equivalent, and on the unhappy path this file is better.
#: So it is EXCLUDED, with the reason recorded, not quietly skipped.
EXCLUDED = {
    "the_joint_debt_is_discharged_by_a_directory_2026-10-14":
        "already 2 independent routes WITH named-failure arms; delegating would "
        "remove the named failure, and no measurement shows `_iv` dominates it",
}

DELEGATE_PAIRS = '''{ind}def interval(k: int, n: int):
{ind}    """Wilson and Clopper-Pearson, from the canonical helper.

{ind}    ★ DELEGATED 2026-11-08 on his ruling for B135 option 1, and here the
{ind}    delegation fixes a second thing. This returned
{ind}    statsmodels' own Wilson method beside its own beta method -- 2
{ind}    intervals from 1 LIBRARY, which
{ind}    is the single-tool-by-construction shape `bench/falsifier_pairing.py`
{ind}    exists to prevent. `_iv` computes Wilson on statsmodels against an
{ind}    mpmath closed form and Clopper-Pearson on scipy against an mpmath
{ind}    incomplete-beta inverse, at the same values.
{ind}    """
{ind}    w, cp, _disagreement = _iv(k, n)
{ind}    return w, cp
'''

DELEGATE = '''{ind}def wilson(k, n):
{ind}    """Wilson as a rounded percentage pair, from the canonical helper.

{ind}    ★ DELEGATED 2026-11-08 on his ruling for B135 option 1. The algebra
{ind}    that stood here was correct and the detector could not SEE it, because
{ind}    it named the sample size `nn` where the pattern required `n`. It is
{ind}    replaced by a call rather than by a wider pattern, so the cross-check
{ind}    is executed instead of being inferred from a spelling. `_iv` is lifted
{ind}    byte-identical from the canonical producer and the board guard asserts
{ind}    every copy agrees with every other.
{ind}    """
{ind}    wl, wh = _iv(k, n)[0]
{ind}    return round(100 * wl, 4), round(100 * wh, 4)
'''


def canonical_iv() -> str:
    src = CANON.read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "_iv")
    return "".join(src.splitlines(keepends=True)[fn.lineno - 1:fn.end_lineno])


def rewrite(path: pathlib.Path, iv: str, pairs: bool = False) -> str:
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    want = "interval" if pairs else "wilson"
    fn = next((n for n in ast.walk(tree)
               if isinstance(n, ast.FunctionDef) and n.name == want), None)
    if fn is None:
        raise SystemExit(f"{path.name}: no `{want}` to delegate")
    lines = src.splitlines(keepends=True)
    ind = " " * (len(lines[fn.lineno - 1]) - len(lines[fn.lineno - 1].lstrip()))
    tmpl = DELEGATE_PAIRS if pairs else DELEGATE
    lines[fn.lineno - 1:fn.end_lineno] = [tmpl.format(ind=ind)]
    out = "".join(lines)
    if "\ndef _iv(" not in out:
        # after the last top-level import, so `math` and the rest are bound
        t2 = ast.parse(out)
        imps = [n for n in t2.body if isinstance(n, (ast.Import, ast.ImportFrom))]
        at = imps[-1].end_lineno if imps else 1
        l2 = out.splitlines(keepends=True)
        if "import math" not in out:
            l2.insert(at, "import math\n")
            at += 1
        l2.insert(at, "\n\n" + iv.rstrip("\n") + "\n")
        out = "".join(l2)
    ast.parse(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--baseline", default=None,
                    help="JSON of pre-edit stdout, for the byte comparison")
    a = ap.parse_args()
    iv = canonical_iv()
    print(f"canonical `_iv`: {len(iv)} chars, "
          f"sha256 {hashlib.sha256(iv.encode()).hexdigest()[:16]}")
    for stem, excuse in sorted(EXCLUDED.items()):
        print(f"  {stem[:52]:54s} EXCLUDED: {excuse[:60]}")
    for stem in PERCENT_PAIR + BOTH_PAIRS:
        p = REPO / "scripts" / f"{stem}.py"
        out = rewrite(p, iv, pairs=stem in BOTH_PAIRS)
        print(f"  {stem[:52]:54s} {len(p.read_text())} -> {len(out)} chars")
        if a.write:
            p.write_text(out, encoding="utf-8")
    if not a.write:
        print("\nDRY RUN -- nothing written. Re-run with --write.")
        return 0
    if not a.baseline:
        print("\nWRITTEN, but no --baseline given, so nothing is PROVEN unchanged.")
        return 1
    before = json.loads(pathlib.Path(a.baseline).read_text(encoding="utf-8"))
    bad = []
    print("\nBYTE COMPARISON AGAINST THE PRE-EDIT BASELINE")
    for stem in PERCENT_PAIR + BOTH_PAIRS:
        r = subprocess.run([sys.executable, f"scripts/{stem}.py"], cwd=REPO,
                           capture_output=True, text=True, timeout=240)
        sha = hashlib.sha256(r.stdout.encode()).hexdigest()
        ok = (r.returncode == before[stem]["rc"] and sha == before[stem]["sha"])
        print(f"  {stem[:52]:54s} rc {before[stem]['rc']}->{r.returncode}  "
              f"stdout {'IDENTICAL' if sha == before[stem]['sha'] else 'CHANGED'}")
        if not ok:
            bad.append(stem)
    if bad:
        print(f"\n★ OUTPUT CHANGED in {len(bad)}: {bad}. A changed figure is a "
              f"changed claim; report it rather than accepting it.")
        return 1
    print("\nall targets delegate to the canonical helper with identical output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
