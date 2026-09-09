#!/usr/bin/env python3
"""How many note-lint findings are the quote-exemption defect rather than real vagueness?

`scripts/note_vagueness_lint.py` deliberately exempts quoted text: line 163 strips
`"[^"]*"` before testing, with the stated reason that a sentence which "quotes
someone else's vagueness in order to name it is not being vague".

The exemption is defeated by its own scope. The checker examines ONE SENTENCE at a
time (line 151), while the stripper needs a BALANCED PAIR of quote marks inside
whatever it is handed. A quotation spanning more than 1 sentence therefore carries
an unbalanced quote mark in every sentence except its last, and loses the
exemption on all of them.

This matters for more than tidiness. The founder's rulings are quoted verbatim and
at length throughout the notes, and the notes remediation is scoped at 1158
findings. Any part of that total which is this defect is work that should not be
done at all. The file's own comments warn twice that "false positives are how a
report-only linter becomes ignored"; this measures how close that already is.

The rate travels with this script per `measured-rate-travels-with-its-script`.
Two tools per proportion: statsmodels for the intervals, mpmath for a closed-form
Wilson sharing none of statsmodels' code.
"""
from __future__ import annotations

import pathlib
import re
import sys

import mpmath as mp
from scipy import stats as sps
from statsmodels.stats.proportion import proportion_confint

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import note_vagueness_lint as lint  # noqa: E402

NOTES = sorted((REPO / "experimental_notes").rglob("*.md"))


def inside_multi_sentence_quote(paragraph: str, sentence: str) -> bool:
    """Would this finding disappear if the exemption were applied per PARAGRAPH?"""
    if sentence not in paragraph:
        return False
    stripped_para = re.sub(r'"[^"]*"', " ", paragraph)
    stripped_sent = re.sub(r'"[^"]*"', " ", sentence)
    # The finding is a quote artefact when the vague phrase survives sentence-wise
    # stripping but does NOT survive paragraph-wise stripping.
    for v in lint.VAGUE_SUBJECTS:
        if re.search(rf"{re.escape(v)}\b", stripped_sent.lower()):
            if not re.search(rf"{re.escape(v)}\b", stripped_para.lower()):
                return True
    return False


def wilson_mp(k: int, n: int, conf: float = 0.95) -> tuple[float, float]:
    mp.mp.dps = 30
    z = mp.mpf(str(sps.norm.ppf(1 - (1 - conf) / 2)))
    p, N = mp.mpf(k) / n, mp.mpf(n)
    c = (p + z**2 / (2 * N)) / (1 + z**2 / N)
    h = (z / (1 + z**2 / N)) * mp.sqrt(p * (1 - p) / N + z**2 / (4 * N**2))
    return float(c - h), float(c + h)


def main() -> int:
    total = quote_artefacts = unnamed_total = 0
    worst: list[tuple[str, str]] = []
    for note in NOTES:
        try:
            text = note.read_text(errors="replace")
            findings = lint.lint(note)
        except Exception:
            continue
        paras = text.split("\n\n")
        for f in findings:
            total += 1
            kind = f[1] if len(f) > 1 else ""
            if "UNNAMED SUBJECT" not in str(kind):
                continue
            unnamed_total += 1
            sentence = str(f[3]) if len(f) > 3 else ""
            para = next((p for p in paras if sentence[:60] and sentence[:60] in p), "")
            if para and inside_multi_sentence_quote(para, sentence):
                quote_artefacts += 1
                if len(worst) < 6:
                    worst.append((note.name, sentence[:110]))

    print(f"notes scanned                         : {len(NOTES)}")
    print(f"findings of every kind                : {total}")
    print(f"UNNAMED SUBJECT findings              : {unnamed_total}")
    print(f"of those, quote-exemption artefacts   : {quote_artefacts}")
    if unnamed_total:
        lo_w, hi_w = proportion_confint(quote_artefacts, unnamed_total, alpha=0.05, method="wilson")
        lo_c, hi_c = proportion_confint(quote_artefacts, unnamed_total, alpha=0.05, method="beta")
        lo_m, hi_m = wilson_mp(quote_artefacts, unnamed_total)
        print(f"\n  share of UNNAMED SUBJECT that is a false positive: {quote_artefacts/unnamed_total:.2%}")
        print(f"    Wilson 95%          [statsmodels] : [{lo_w:.2%}, {hi_w:.2%}]")
        print(f"    Wilson 95%          [mpmath     ] : [{lo_m:.2%}, {hi_m:.2%}]   agree={abs(lo_w-lo_m)<1e-12}")
        print(f"    Clopper-Pearson 95% [statsmodels] : [{lo_c:.2%}, {hi_c:.2%}]")
    if worst:
        print("\n  examples:")
        for name, s in worst:
            print(f"    {name}: {s}...")
    print("\n  A finding counted here is one that survives SENTENCE-wise quote stripping")
    print("  but not PARAGRAPH-wise stripping. It is an artefact of the exemption's")
    print("  scope, not of the note's prose.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
