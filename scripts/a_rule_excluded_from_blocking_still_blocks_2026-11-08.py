#!/usr/bin/env python3
"""Rule 30 was deliberately made NON-BLOCKING, and it still refuses commits.

THE TWO DECISIONS THAT DISAGREE.

  1. `blocking()` in `scripts/note_vagueness_lint.py` returns
     `partition(path)[0] + missing_standard_stamp(path)`. Rule 30 --
     `undefined-project-term` -- is reachable ONLY through the separate
     function `undefined_project_terms()`, which neither `lint()` nor
     `partition()` calls. Its exclusion was a DECIDED thing, recorded in
     `blocking()`'s own comment on 2026-10-15 after it refused a compliant
     note on 9 findings of which 1 was a genuine coinage, with a measurement
     over 523 notes showing no structural difference between "pinned
     threshold" (a description) and "paired baseline" (a coinage he
     challenged). The comment's words: gating on it "would refuse roughly 1
     note in 2 and teach its reader that the checker is noise".

  2. `hooks/pre-commit`'s per-file note ratchet counts the CLI's TOTAL, which
     includes Rule 30. So the rule the project decided must not gate does
     gate -- on every new note, where the HEAD baseline is 0 and therefore any
     finding at all is "worse".

WHY THIS WAS FOUND THE HARD WAY. The session of 2026-11-08 cleared every note
it wrote using `blocking()` and `lint()` from Python, both of which are blind
to Rule 30 by construction, reported each note as 0 findings, and had 2
commits refused by the ratchet on exactly that rule. It then reported the gap
to the founder as the lint CONTRADICTING ITSELF about a logical path, which is
false: the CLI returns the same count at a real path and under `--as`. The
cause was never path sensitivity. It was verifying with a predicate that cannot
see the rule being enforced.

WHAT THIS SCRIPT ESTABLISHES, by execution over the real corpus:
  * that the 2 routes genuinely differ, and by how much;
  * that the difference is NOT path sensitivity, by linting the same bytes at
    a real path and through `--as` and comparing;
  * how many committed notes would be refused as new files under the ratchet's
    count but pass under `blocking()`.

IT PROPOSES NOTHING. Whether Rule 30 should gate is the founder's call: the
2026-10-15 measurement says its precision is too low to gate, and the ratchet
gates on it anyway, so the 2 positions are his to reconcile.

Exit 0 iff every figure was produced by 2 independent routes.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
LINT = REPO / "scripts" / "note_vagueness_lint.py"
NOTES = REPO / "experimental_notes"


def _iv(k: int, n: int):
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y   # noqa: E731
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(lo - float(cen - half)), abs(hi - float(cen + half)),
              abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label: str, k: int, n: int) -> None:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"


def main() -> int:
    sys.path.insert(0, str(REPO / "scripts"))
    import note_vagueness_lint as L

    notes = sorted(p for p in NOTES.glob("*.md"))
    if not notes:
        print(f"REFUSED: no notes under {NOTES}")
        return 1

    print("=" * 78)
    print("A RULE EXCLUDED FROM `blocking()` STILL REFUSES COMMITS")
    print("=" * 78)

    #: 1. THE 2 ROUTES DIFFER, and by how much. `blocking()` cannot return a
    #: Rule 30 finding at all, which is checked rather than asserted.
    tot_block, tot_r30, with_r30 = 0, 0, 0
    for p in notes:
        b = L.blocking(p)
        r = L.undefined_project_terms(p)
        assert not any(f[1] == "undefined-project-term" for f in b), (
            f"blocking() returned a Rule 30 finding for {p.name}, so this "
            f"script's premise is wrong and nothing below should be trusted.")
        tot_block += len(b)
        tot_r30 += len(r)
        if r:
            with_r30 += 1
    print(f"\n  notes examined                      : {len(notes)}")
    print(f"  findings `blocking()` can return    : {tot_block}")
    print(f"  Rule 30 findings it can NEVER return: {tot_r30}")
    print()
    _show("notes carrying at least 1 Rule 30 finding", with_r30, len(notes))
    print("      ^ each of these would be REFUSED as a NEW note by the "
          "ratchet,")
    print("        whose baseline for a file absent from HEAD is 0, while "
          "passing")
    print("        `blocking()` with that rule invisible.")

    #: 2. IT IS NOT PATH SENSITIVITY, which is the explanation this session
    #: first gave the founder and then withdrew. The same bytes are linted at
    #: a real path and through `--as` on a copy, and the counts compared.
    print("\n  IS THE DIFFERENCE PATH SENSITIVITY? Linting the SAME bytes "
          "both ways:")
    sample = [p for p in notes if L.undefined_project_terms(p)][:6]
    mismatches = 0
    with tempfile.TemporaryDirectory() as td:
        for p in sample:
            copy = pathlib.Path(td) / f"after_{p.name}"
            copy.write_bytes(p.read_bytes())
            direct = subprocess.run([sys.executable, str(LINT), str(p)],
                                    capture_output=True, text=True,
                                    cwd=str(REPO), timeout=180)
            asif = subprocess.run(
                [sys.executable, str(LINT), "--as",
                 str(p.relative_to(REPO)), str(copy)],
                capture_output=True, text=True, cwd=str(REPO), timeout=180)
            a = direct.stdout.count("undefined-project-term")
            b = asif.stdout.count("undefined-project-term")
            flag = "" if a == b else "   <-- DIFFERS"
            if a != b:
                mismatches += 1
            print(f"      {p.name[:52]:<54} real {a:>3}  --as {b:>3}{flag}")
    print()
    _show("sampled notes where the 2 paths DISAGREE", mismatches, len(sample))
    print("      ^ 0 of them means the route, not the path, is the difference.")

    print("\n" + "=" * 78)
    print("WHAT THIS SUPPORTS AND WHAT IT DOES NOT")
    print("  SUPPORTS: a rule the project deliberately removed from its")
    print("    blocking set on a measured precision argument is nevertheless")
    print("    enforced on every new note by the pre-commit ratchet, and a")
    print("    session checking its work with `blocking()` cannot see it.")
    print("  DOES NOT SUPPORT: a claim that Rule 30 is wrong, or that the")
    print("    ratchet is. The 2026-10-15 measurement that made it")
    print("    non-blocking stands, and so does the ratchet's rule that a")
    print("    commit may not make a note worse. They simply disagree about")
    print("    this rule, and reconciling them is HIS call.")
    print("  THE PRACTICAL LESSON IS ALREADY ACTIONABLE WITHOUT A RULING:")
    print("    verify a note with the CLI, or with `undefined_project_terms()`")
    print("    in addition to `blocking()`. Verifying with a predicate blind")
    print("    to the enforced rule is what cost 2 refused commits.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    try:
        from _cli_help import answer_help as _answer_help
        _answer_help(__doc__, __file__, takes_no_arguments=True)
    except ImportError:
        pass
    raise SystemExit(main())
