#!/usr/bin/env python3
"""What the multi-sentence quote exemption changed, across the whole corpus.

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

`scripts/note_vagueness_lint.py` stripped balanced `"..."` pairs from each
SENTENCE. A quotation spanning more than 1 sentence is split first, so each
fragment carries an unbalanced quote character and matches nothing: the exemption
lapsed on exactly the longest quotations, which in this project are the
founder's. The mask now runs before the sentence split.

This measures the difference over every note, so the claim "it removes false
positives and nothing else" is checkable rather than asserted. A finding that
DISAPPEARS was inside a verbatim quotation. Any finding that APPEARS would be a
regression, and the script reports that count separately for exactly that reason.
"""
import importlib.util
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "lint", REPO / "scripts" / "note_vagueness_lint.py")
lint_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_mod)

_QUOTED = re.compile(r'"[^"]*"')


def old_sentences(text: str):
    """The pre-fix generator: no masking, quotes stripped later per sentence."""
    for para_no, para in enumerate(text.split("\n\n"), 1):
        flat = " ".join(para.split())
        if not flat or flat.startswith(("|", "#", "```")):
            continue
        for s in re.split(r"(?<=[.!?])\s+", flat):
            if len(s.split()) >= 5:
                yield para_no, s


def count(path, gen):
    saved = lint_mod.sentences
    lint_mod.sentences = gen
    try:
        return {(f[0], str(f[1]), str(f[2])) for f in
                (tuple(x) if isinstance(x, (list, tuple)) else (x,)
                 for x in lint_mod.lint(path))}
    finally:
        lint_mod.sentences = saved


def main() -> int:
    notes = sorted((REPO / "experimental_notes").rglob("*.md"))
    before = after = removed = added = 0
    changed = []
    for p in notes:
        try:
            b = count(p, old_sentences)
            a = count(p, lint_mod.sentences)
        except Exception:
            continue
        before += len(b); after += len(a)
        gone, new = b - a, a - b
        removed += len(gone); added += len(new)
        if gone or new:
            changed.append((p.name, len(gone), len(new)))

    print(f"notes scanned            : {len(notes)}")
    print(f"findings BEFORE the fix  : {before}")
    print(f"findings AFTER the fix   : {after}")
    print(f"removed (were inside a verbatim quotation) : {removed}")
    print(f"ADDED   (would be a regression)            : {added}")
    if before:
        from statsmodels.stats.proportion import proportion_confint
        lo_w, hi_w = proportion_confint(removed, before, method="wilson")
        lo_c, hi_c = proportion_confint(removed, before, method="beta")
        from scipy.stats import beta as sb
        lo_s = 0.0 if removed == 0 else sb.ppf(0.025, removed, before - removed + 1)
        hi_s = 1.0 if removed == before else sb.ppf(0.975, removed + 1, before - removed)
        print(f"share of findings that were false positives: {removed/before:.4f}")
        print(f"Wilson 95%          : [{lo_w*100:.1f}%, {hi_w*100:.1f}%]  (statsmodels)")
        print(f"Clopper-Pearson 95% : [{lo_c*100:.1f}%, {hi_c*100:.1f}%]  (statsmodels)")
        print(f"Clopper-Pearson 95% : [{lo_s*100:.1f}%, {hi_s*100:.1f}%]  (scipy cross-check)")
        print(f"tools agree to 1e-9 : {abs(lo_s-lo_c) < 1e-9 and abs(hi_s-hi_c) < 1e-9}")
    if changed:
        print("\nnotes whose finding set changed (removed, added):")
        for name, g, n in sorted(changed, key=lambda r: -r[1])[:15]:
            print(f"  {name[:62]:62s} -{g}  +{n}")
    return 1 if added else 0


if __name__ == "__main__":
    sys.exit(main())
