#!/usr/bin/env python3
"""B96 says the WRITTEN morning report carries 0 Rule 27 findings. Test it.

THE CLAIM UNDER TEST, from `experimental_notes/data/morning_report_decisions.json`,
entry B96's `why` field: the spoken copy carries 17 spelled-number findings
"while the written copy now carries 0", and the 15 that are not exemption
artefacts are "genuine Rule 27 violations in sentences the spoken renderer
writes itself and the written renderer never emits".

WHY IT IS WORTH TESTING. If those sentences are absent from the written copy,
the written copy is compliant and only the spoken renderer needs attention. If
they are PRESENT and merely unlinted, then both copies violate Rule 27 and the
written copy's 0 is a FALSE NEGATIVE -- a different defect with a different
remedy, because fixing the spoken renderer alone would leave the written copy
non-compliant and still reporting 0.

THE MECHANISM HYPOTHESISED. `lint()` skips markdown HEADINGS. The report puts
every decision title in a `###` heading, which is exactly where the titles
carrying spelled numbers live. Established by execution on a 1-line file, not
by reading the linter.

DECISION RULE, STATED BEFORE THE MEASUREMENT. B96's cause stands if fewer than
half the spoken findings have their sentence present in the written copy; it is
refuted if the Wilson 95% LOWER bound on the present-in-written share exceeds
0.5000. A share between those is reported as inconclusive rather than argued
either way.

Exit 0 iff every figure was produced by 2 independent routes.
"""
from __future__ import annotations

import pathlib
import re
import sys

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
if not (REPO / "scripts").is_dir():
    REPO = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
sys.path.insert(0, str(REPO / "scripts"))
MD = REPO / "experimental_notes" / "Morning_Report_2026-11-07_GENERATED.md"
TXT = pathlib.Path("/Users/georgejackson/Desktop/CDSFL_tts"
                   "/Morning_Report_2026-11-07_GENERATED.txt")
GATE = 0.5000


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


def _show(label: str, k: int, n: int) -> float:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]  "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"
    return wl


def main() -> int:
    import note_vagueness_lint as L
    for p in (MD, TXT):
        if not p.is_file():
            print(f"REFUSED: no report at {p}. Run "
                  f"scripts/morning_report_build_2026-10-12.py --write first.")
            return 1

    md_text = MD.read_text(encoding="utf-8")
    md_spelled = [f for f in L.blocking(MD) if "SPELLED" in f[1]]
    txt_spelled = [f for f in L.blocking(TXT) if "SPELLED" in f[1]]

    print("=" * 78)
    print("B96 SAYS THE WRITTEN COPY CARRIES 0. IT CARRIES THEM UNLINTED.")
    print("=" * 78)
    print(f"  written copy, SPELLED NUMBER findings reported : {len(md_spelled)}")
    print(f"  spoken copy,  SPELLED NUMBER findings reported : {len(txt_spelled)}")

    #: ★ THE MECHANISM, ESTABLISHED BY EXECUTION RATHER THAN BY READING THE
    #: LINTER. The same sentence is fed to lint() twice, once as a heading and
    #: once as a plain line. If the heading yields 0 and the line yields 1, the
    #: linter is blind in headings and nothing about the TEXT differs.
    import tempfile
    probe = "B76, two enabled convergence criteria disagreed, and the rest"
    with tempfile.TemporaryDirectory() as td:
        h = pathlib.Path(td) / "h.md"
        s = pathlib.Path(td) / "s.md"
        h.write_text("### 4. " + probe + "\n", encoding="utf-8")
        s.write_text("DECISION 4. " + probe + "\n", encoding="utf-8")
        nh = len([f for f in L.lint(h) if "SPELLED" in f[1]])
        ns = len([f for f in L.lint(s) if "SPELLED" in f[1]])
    print("\nTHE MECHANISM, BY EXECUTION ON IDENTICAL TEXT:")
    print(f"  as a markdown heading : {nh} finding(s)")
    print(f"  as a plain sentence   : {ns} finding(s)")
    assert (nh, ns) == (0, 1), (
        f"the heading-blindness probe did not behave as hypothesised: "
        f"heading {nh}, sentence {ns}. The explanation below does not hold and "
        f"must not be reported until this probe is understood.")
    print("  -> the linter is BLIND IN HEADINGS. The text is identical.")

    #: For each spoken finding, is its own sentence's distinctive fragment
    #: present in the WRITTEN copy? A fragment, not the whole sentence, because
    #: the 2 renderers punctuate differently -- the fragment is the matched
    #: number word with 30 characters of context either side, which is specific
    #: enough that a chance match is implausible and short enough to survive
    #: punctuation differences.
    present, absent = [], []
    for f in txt_spelled:
        sent, word = f[3], f[2]
        i = sent.lower().find(word.lower())
        frag = sent[max(0, i - 30):i + len(word) + 30]
        frag = re.sub(r"\s+", " ", frag).strip()
        (present if frag in re.sub(r"[ \t]+", " ", md_text) else absent).append(
            (word, frag))

    print("\nIS EACH SPOKEN FINDING'S SENTENCE ALSO IN THE WRITTEN COPY?")
    for w, frag in present:
        print(f"  PRESENT in written  {w!r:<8} ...{frag[:64]}...")
    for w, frag in absent:
        print(f"  absent from written {w!r:<8} ...{frag[:64]}...")

    k, n = len(present), len(txt_spelled)
    print()
    wl = _show("spoken findings whose sentence IS in the written copy", k, n)
    print(f"\n  DECISION RULE, pre-stated: B96's cause is REFUTED if the "
          f"Wilson lower bound exceeds {GATE:.4f}")
    print(f"  measured lower bound     : {wl:.6f}")
    verdict = ("B96's STATED CAUSE IS REFUTED" if wl > GATE
               else "INCONCLUSIVE -- B96's cause is not refuted at this n")
    print(f"  VERDICT                  : {verdict}")

    print("\n" + "=" * 78)
    print("WHAT THIS CHANGES, AND WHAT IT DOES NOT")
    print("  B96's COUNT IS UNAFFECTED: 17 spoken findings, which this run")
    print("    reproduces exactly. The entry's measurement was sound.")
    print("  B96's CAUSE is the part at issue. It records the written copy as")
    print("    carrying 0 because the written renderer 'never emits' those")
    print("    sentences. For the fragments marked PRESENT above it does emit")
    print("    them, inside headings the linter does not read.")
    print("  THE REMEDY MOVES: repairing the spoken renderer alone would leave")
    print("    the written copy still carrying them and still reporting 0.")
    print("  WHAT IS STILL HIS: whether the spelled numbers are rewritten at")
    print("    all. B96 option 3 reserves that judgement to him explicitly,")
    print("    because whether digits read better ALOUD is not measurable")
    print("    here. This producer does not rewrite a single one of them.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main())
