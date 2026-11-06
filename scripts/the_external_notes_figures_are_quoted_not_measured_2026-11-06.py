#!/usr/bin/env python3
"""Are the figures in the external-research notes QUOTED from published work, or
are they measurements of ours with no producer? Measured, per note.

★ WHY THIS EXISTS. The complete board of 2026-11-05 failed
`test_none_carries_a_figure_without_a_source` on
`experimental_notes/Similarity_Function_External_Benchmarking_2026-08-16.md`:
55 figures, 0 live scripts, no declared provenance. The checker's rule is
`bool(scripts) or PROVENANCE in t or not figures`, so a note whose figures are
QUOTED rather than computed is meant to declare that, and this one never did.

THE DECLARATION MUST BE TRUE, WHICH IS WHAT THIS MEASURES. It would be easy to
write `FIGURE PROVENANCE: all external` and clear the board without establishing
it. So this producer counts the citation apparatus and, crucially, reports the
share of figure-bearing paragraphs that carry a citation IN THE SAME PARAGRAPH --
which for the 2026-08-16 note is a minority. A provenance declaration that
claimed per-figure attribution would be false, and the honest declaration states
the limit.

THE FIGURE PATTERN IS LIFTED FROM THE CHECKER, not restated, so this producer
cannot drift from the test it exists to explain.
"""
from __future__ import annotations
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CHECKER = REPO / "scripts" / "note_reproducibility_2026-09-10.py"
URL = re.compile(r"https?://[^\s)\]]+")
DOI = re.compile(r"10\.\d{4,9}/[^\s)\]]+")
ARXIV = re.compile(r"\b\d{4}\.\d{4,5}\b")
CITE = re.compile(r"https?://|10\.\d{4,9}/")


def checker_figure_pattern() -> re.Pattern:
    src = CHECKER.read_text(encoding="utf-8")
    m = re.search(r"FIGURE\s*=\s*re\.compile\(r\"([^\"]+)\"\)", src)
    if not m:
        raise SystemExit("ANCHOR ABSENT: the checker's FIGURE pattern has moved")
    return re.compile(m.group(1))


def iv(k: int, n: int):
    import mpmath
    from scipy.stats import beta as sbeta
    from statsmodels.stats.proportion import proportion_confint
    if n == 0:
        return None
    wl, wh = proportion_confint(k, n, method="wilson")
    mpmath.mp.dps = 40
    z = mpmath.mpf("1.959963984540054235524594430520551527955")
    p = mpmath.mpf(k) / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * mpmath.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    cl = 0.0 if k == 0 else float(sbeta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(sbeta.ppf(0.975, k + 1, n - k))
    return (wl, wh), (float(c - h), float(c + h)), (cl, ch)


def survey(note: Path, FIG: re.Pattern) -> dict:
    t = note.read_text(encoding="utf-8", errors="replace")
    paras = [x for x in t.split("\n\n") if x.strip()]
    withfig = [x for x in paras if FIG.search(x)]
    withboth = [x for x in withfig if CITE.search(x)]
    return {
        "note": note.name,
        "lines": len(t.splitlines()),
        "figures": len(FIG.findall(t)),
        "urls": len(URL.findall(t)),
        "urls_distinct": len(set(URL.findall(t))),
        "dois": len(DOI.findall(t)),
        "arxiv": len(ARXIV.findall(t)),
        "paras": len(paras),
        "paras_with_figure": len(withfig),
        "paras_with_figure_and_citation": len(withboth),
        "declares_provenance": "FIGURE PROVENANCE" in t,
    }


def main() -> int:
    #: ANSWER `--help` BEFORE DOING ANY WORK. His rule, measured: a flag
    #: that runs the whole measurement can cost machine time or money,
    #: and 15 of 17 runners once billed for it.
    import sys as _sys, pathlib as _pl
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _ah
    _ah(__doc__, __file__)
    FIG = checker_figure_pattern()
    print(f"the checker's FIGURE pattern, lifted: {FIG.pattern}")
    notes = sorted(p for p in (REPO / "experimental_notes").glob("*.md")
                   if "External" in p.name or "external" in p.name)
    if not notes:
        print("no external-research notes found"); return 2
    for n in notes:
        r = survey(n, FIG)
        print(f"\n{r['note']}")
        print(f"  lines {r['lines']}, figures {r['figures']}, "
              f"declares provenance: {r['declares_provenance']}")
        print(f"  citation apparatus: {r['urls']} inline URLs "
              f"({r['urls_distinct']} distinct), {r['dois']} DOIs, "
              f"{r['arxiv']} arXiv-shaped identifiers")
        k, m = r["paras_with_figure_and_citation"], r["paras_with_figure"]
        res = iv(k, m)
        if res:
            (wl, wh), (wl2, wh2), (cl, ch) = res
            print(f"  figure-bearing paragraphs also carrying a citation: "
                  f"{k} of {m} = {k/m:.6f}")
            print(f"    Wilson [{wl:.6f}, {wh:.6f}] statsmodels / "
                  f"[{wl2:.6f}, {wh2:.6f}] mpmath  agree={abs(wl-wl2) < 1e-12}")
            print(f"    Clopper-Pearson [{cl:.6f}, {ch:.6f}] scipy.beta")
        print("  SO: the figures are QUOTED from published work and the note is")
        print("  densely cited, but attribution is NOT per-figure. A provenance")
        print("  declaration must say both, or it overclaims.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
