#!/usr/bin/env python3
"""What does the concise rendering actually remove from a live directive?

WHY THIS EXISTS. `_apply_phenotype_transform` in `bench/cdsfl_registry/composer.py`
compresses a directive for a small-context seat: it joins a block's lines into
one, then removes lines that are semantically duplicate, then caps the total
length. For CODE the first 2 steps are destructive, because in Python
indentation IS syntax and a repeated definition IS the evidence a
reviewer must see. A protection landed on 2026-10-15: fenced blocks and the named sections
`CODE EXTRACTS` and `INTERACTION SURFACE` are stashed verbatim.

This script asks what the rendering removes in practice, and ATTRIBUTES the loss
to the step responsible, because the answer turned out to be none of the steps
under suspicion.

MEASURED 2026-10-17, by running the live `chatgpt_5_4` phenotype over every file
under the composer's own `DIRECTIVES_DIR`:

  * DEDUPLICATION REMOVES 2 CHARACTERS IN TOTAL across the 5 largest live
    directives, which is line-join arithmetic rather than content: 1 character
    each in 2 files and 0 in the other 3.
  * THE LENGTH CAP DOES THE CUTTING. Every rendering comes out at exactly 8,035
    characters, so `universal/cdsfl_operational.md` loses 38,339 of its 46,374
    characters, 82.6735%, to the cap alone, and the 5 largest lose between
    27.1400% and 82.6735%. That is not a new finding: it is the already-open
    parked item C0040, which records that every model receives a fraction of
    the universal directive.
  * THE DESTRUCTIVE CODE CASE IS REAL BUT LATENT. 20 identical definitions with
    no fence and no section marker go from 1,406 characters, 20 definitions and
    40 indented lines to 85 characters, 1 definition and 0 indented lines. Under
    `=== CODE EXTRACTS ===` all 20 survive. No live path produces the former:
    `_build_situation_packet` is the only producer that embeds code and it always
    marks it.

FOUR PREDICATES WERE WRONG BEFORE THIS ONE, and each produced a figure that had
to be withdrawn. Searching `bench/cdsfl_registry` instead of `bench/directives`
gave 3 files and an interval to 70.7598%. Counting indented runs flagged wrapped
bullet continuations as code. Requiring a source line to appear verbatim in the
output flagged every re-wrapped line, giving 19.4444%. Allowing for re-wrapping
but not for markdown-marker normalisation flagged 6 surviving headings as
missing, because `## REQUIRED SECTION 1 -- The question` is rendered as
`REQUIRED SECTION 1 -- The question:`. The lesson is in the shape: an aggregate
over a proxy kept producing a number, and only reading one small file end to end
produced the truth.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _cli_help import answer_help  # noqa: E402

MIN_RUN = 3


def longest_unfenced_indented_run(text: str) -> tuple[int, int]:
    """(longest run, line number where it starts). Fenced blocks are skipped."""
    run = best = best_at = 0
    start = 0
    in_fence = False
    for n, line in enumerate(text.split("\n"), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            run = 0
            continue
        if in_fence:
            continue
        if line.startswith("    ") and line.strip():
            if run == 0:
                start = n
            run += 1
            if run > best:
                best, best_at = run, start
        else:
            run = 0
    return best, best_at


def main() -> int:
    answer_help(__doc__, __file__)
    from bench.cdsfl_registry import composer as C_MOD
    from bench.cdsfl_registry.composer import (
        DIRECTIVES_DIR, PHENOTYPE_TRANSFORMS, SITUATION_SECTION_IS_VERBATIM,
        _VERBATIM_SITUATION_SECTIONS, PhenotypeTransform,
        _apply_phenotype_transform)

    root = pathlib.Path(DIRECTIVES_DIR)
    print(f"DIRECTIVES_DIR = {root}")
    if not root.is_dir():
        print("the directive root does not exist. Measurement void.")
        return 3
    files = sorted(p for p in root.rglob("*")
                   if p.is_file() and p.suffix in (".txt", ".md"))
    hits = []
    for p in files:
        n, at = longest_unfenced_indented_run(
            p.read_text(encoding="utf-8", errors="replace"))
        if n >= MIN_RUN:
            hits.append((n, at, p))

    print(f"\nINDENTED RUNS OUTSIDE A FENCE (>= {MIN_RUN} lines)")
    print(f"  directive files examined : {len(files)}")
    print(f"  files with such a run    : {len(hits)}")
    if files:
        from statsmodels.stats.proportion import proportion_confint
        import scipy.stats as st
        k, n = len(hits), len(files)
        w = proportion_confint(k, n, method="wilson")
        b = proportion_confint(k, n, method="beta")
        cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
        print(f"  {k} of {n} = {100*k/n:.4f}%")
        print(f"    Wilson          [{w[0]*100:.4f}%, {w[1]*100:.4f}%]")
        print(f"    Clopper-Pearson [{b[0]*100:.4f}%, {b[1]*100:.4f}%]")
        print(f"    scipy agrees on the upper bound: {abs(b[1] - cp_hi) < 1e-9}")

    print("\n  EACH HIT, WITH ITS CONTENT, because a run is not a verdict:")
    for n, at, p in sorted(hits, reverse=True):
        print(f"    {p.relative_to(root)}  {n} lines from line {at}")
        lines = p.read_text(encoding="utf-8", errors="replace").split("\n")
        for ln in lines[max(0, at - 2):at - 1 + n]:
            print(f"        | {ln[:96]}")

    print("\nWHAT DEDUPLICATION REMOVES, ISOLATED")
    live = PHENOTYPE_TRANSFORMS["chatgpt_5_4"]
    biggest = sorted(files, key=lambda q: -q.stat().st_size)[:5]
    dedup_chars = 0
    for q in biggest:
        txt = q.read_text(encoding="utf-8", errors="replace")
        with_d = _apply_phenotype_transform(txt, live)
        orig = C_MOD._semantically_duplicate
        C_MOD._semantically_duplicate = lambda a, b: False
        try:
            without_d = _apply_phenotype_transform(txt, live)
        finally:
            C_MOD._semantically_duplicate = orig
        lost_c = len(without_d) - len(with_d)
        lost_l = len(without_d.split("\n")) - len(with_d.split("\n"))
        dedup_chars += lost_c
        print(f"  {q.relative_to(root)}")
        print(f"      source {len(txt):>6} chars -> rendering {len(with_d):>6}")
        print(f"      dedup removed {lost_c:>6} chars, {lost_l:>3} lines")

    print("\nWHAT THE LENGTH CAP REMOVES")
    for q in biggest:
        txt = q.read_text(encoding="utf-8", errors="replace")
        out = _apply_phenotype_transform(txt, live)
        cut = len(txt) - len(out)
        print(f"  {q.relative_to(root)}: {len(txt):>6} -> {len(out):>6}"
              f"  cut {cut:>6} = {100*cut/len(txt):.4f}%")
    print(f"  the cap is max_directive_chars = {live.max_directive_chars}")

    print("\nWHAT THE TRANSFORM DOES TO UNMARKED CODE, for scale")
    ident = "def handler(request):\n    value = request.get('x')\n    return value\n"
    bare = "=== TASK ===\nReview this.\n\n" + "\n".join(ident for _ in range(20))
    out = _apply_phenotype_transform(
        bare, PhenotypeTransform(format_style="concise"))

    def _ind(s):
        return sum(1 for l in s.split("\n") if l.startswith("    "))

    print(f"  unmarked: {len(bare)} chars, {bare.count('def ')} definitions, "
          f"{_ind(bare)} indented lines")
    print(f"  concise : {len(out)} chars, {out.count('def ')} definitions, "
          f"{_ind(out)} indented lines")
    marked = ("=== TASK ===\nReview this.\n\n=== CODE EXTRACTS ===\n"
              + "\n".join(ident for _ in range(20)) + "\n")
    out2 = _apply_phenotype_transform(
        marked, PhenotypeTransform(format_style="concise"))
    print(f"  under === CODE EXTRACTS ===: {len(out2)} chars, "
          f"{out2.count('def ')} definitions, {_ind(out2)} indented lines")

    print("\nSECTION CLASSIFICATION")
    print(f"  classified : {len(SITUATION_SECTION_IS_VERBATIM)}")
    print(f"  verbatim   : {list(_VERBATIM_SITUATION_SECTIONS)}")
    n_concise = sum(1 for v in PHENOTYPE_TRANSFORMS.values()
                    if v.format_style in ("concise", "minimal"))
    print(f"  seats receiving a compressed rendering: {n_concise} of "
          f"{len(PHENOTYPE_TRANSFORMS)}")

    print("\nVERDICT")
    print(f"  deduplication removed {dedup_chars} characters across the "
          f"{len(biggest)} largest live directives, against a stated threshold "
          f"of 1% of a rendering.")
    print("  the cutting is done by the LENGTH CAP, which is the already-open")
    print("  parked item C0040, not a defect of the concise rendering.")
    print("  the destructive code case needs unmarked code whose lines each open")
    print("  a block; no live path produces that.")
    # THE CRITERION IS STATED, not implied by an exit code. Deduplication is
    # allowed to cost line-join arithmetic -- joining a block changes a
    # character or two -- and is NOT allowed to cost content. 1% of a single
    # rendering is the line, because the smallest rendering here is 8,034
    # characters and 1% of that is 80, far above the 2 characters measured and
    # far below the hundreds a removed directive would cost.
    budget = 0.01 * 8034 * len(biggest)
    if dedup_chars <= budget:
        return 0
    print(f"  REFUSING: {dedup_chars} characters exceeds the {budget:.0f} "
          f"allowed. Deduplication is removing content, not whitespace.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
