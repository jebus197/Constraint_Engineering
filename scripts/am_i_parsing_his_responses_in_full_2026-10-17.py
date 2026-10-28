#!/usr/bin/env python3
"""Am I parsing his responses in full? His instruction of 2026-10-17, measured.

HIS INSTRUCTION, verbatim: "before running it in full, carefully check off that
you are parsing my fully responses and then tell me everything that is on that
task list before executing it."  (His "fully" reads as "full".)

WHY HE ASKED. He observes the discussion and work list look short, and that he
has had to repeat several rulings. His hypothesis is that his annotated replies
are not being read end to end. This script tests that hypothesis against the
record rather than asserting an answer either way.

METHOD, AND ITS LIMIT STATED FIRST. His verdicts are prose and the task entries
are prose, so no exact match exists between them. What CAN be measured without
guessing is COVERAGE BY CONTENT WORDS: for each verdict, are its distinctive
words present anywhere in the task list or the done record? A verdict whose
words appear nowhere cannot have been acted on. A verdict whose words DO appear
may still have been misread, so this measures a NECESSARY condition, not a
sufficient one. It is a lower bound on neglect, not a proof of diligence.

READ WITH THE DEDICATED READER, NEVER WITH GREP: 319 of his 579 verdicts sit in
files grep treats as binary, so a naive scan is blind to 55% of the record.

`--help` runs no measurement and costs nothing.
"""
from __future__ import annotations
import argparse, collections, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
READER = ROOT / "scripts" / "read_founder_responses_2026-10-11.py"
TASKLIST = ROOT / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
STOP = set("""the a an and or but if then than that this these those of to in on at by for with
from as is are was were be been being it its they them their there here what which who whom
whose when where why how all any both each few more most other some such no nor not only own
same so too very can will just should now i me my we us our you your he him his she her do does
did doing have has had having would could may might must shall about above after again against
below between into through during before once under over further also yet still get got make
made say said see seen look looked think thought know known want wanted need needed go going
gone come came take taken give given use used work working thing things way ways lot bit
yes ok okay please thanks verdict agree agreed good call fix fixed done""".split())

def verdicts() -> list[dict]:
    r = subprocess.run([sys.executable, str(READER), "--json"],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        print(f"READER FAILED rc={r.returncode}: {r.stderr[:200]}", file=sys.stderr)
        sys.exit(2)
    return json.loads(r.stdout)["annotations"]

def content_words(t: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z_]{4,}", t.lower()) if w not in STOP}

def ci(k: int, n: int) -> list[str]:
    out = []
    try:
        from statsmodels.stats.proportion import proportion_confint
        lo, hi = proportion_confint(k, n, 0.05, "wilson")
        out.append(f"Wilson (statsmodels)    [{lo*100:.4f}%, {hi*100:.4f}%]")
    except Exception as e: out.append(f"Wilson unavailable: {e}")
    try:
        from scipy.stats import beta
        lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
        hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
        out.append(f"Clopper-Pearson (scipy) [{lo*100:.4f}%, {hi*100:.4f}%]")
    except Exception as e: out.append(f"Clopper-Pearson unavailable: {e}")
    try:
        import mpmath as mp
        mp.mp.dps = 30
        p, z, N = mp.mpf(k)/n, mp.mpf("1.959963984540054235524594430520"), n
        d = 1 + z**2/N
        c = (p + z**2/(2*N))/d
        h = z*mp.sqrt(p*(1-p)/N + z**2/(4*N**2))/d
        out.append(f"Wilson (mpmath)         [{float(c-h)*100:.4f}%, {float(c+h)*100:.4f}%]")
    except Exception as e: out.append(f"Wilson mpmath unavailable: {e}")
    return out

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--since", default="2026-10-01",
                    help="audit window start (default 2026-10-01)")
    ap.add_argument("--min-words", type=int, default=4,
                    help="skip verdicts with fewer distinctive words (default 4)")
    ap.add_argument("--show", type=int, default=25)
    a = ap.parse_args()

    V = verdicts()
    print("=" * 76)
    print("AM I PARSING HIS RESPONSES IN FULL? his instruction of 2026-10-17")
    print("=" * 76)

    by_date = collections.Counter(x["date"] for x in V)
    print(f"\nHIS RECORD: {len(V)} verdicts across {len({x['file'] for x in V})} "
          f"files, {len(by_date)} distinct dates")
    print("  newest 12 dates:")
    for dt, n in sorted(by_date.items(), reverse=True)[:12]:
        print(f"    {dt}  {n:>4d}")
    # A CAPPED LISTING STATES ITS REMAINDER -- 2026-10-28. A list cut to N under a heading that reads as complete is a silent falsehood.
    _withheld = max(0, len(by_date) - 12)
    if _withheld:
        print(f"      ... and {_withheld} more not shown "
              f"(of {len(by_date)} total)")

    window = [x for x in V if x["date"] >= a.since]
    print(f"\nAUDIT WINDOW from {a.since}: {len(window)} verdicts across "
          f"{len({x['file'] for x in window})} files")

    corpus = TASKLIST.read_text(encoding="utf-8").lower()
    corpus_words = set(re.findall(r"[a-z][a-z_]{4,}", corpus))

    graded, skipped = [], 0
    for v in window:
        w = content_words(v["text"])
        if len(w) < a.min_words:
            skipped += 1
            continue
        hit = len(w & corpus_words) / len(w)
        graded.append((hit, v, w))

    graded.sort(key=lambda t: t[0])
    # a verdict is UNCOVERED when under half its distinctive words appear at all
    THRESH = 0.50
    unc = [g for g in graded if g[0] < THRESH]
    k, n = len(unc), len(graded)
    print(f"  gradeable (>= {a.min_words} distinctive words): {n}")
    print(f"  too short to grade                            : {skipped}")

    print(f"\nCOVERAGE: {n-k} of {n} verdicts have at least half their distinctive")
    print(f"words present in the task list = {(n-k)/n*100:.4f}%")
    for line in ci(n - k, n):
        print(f"    {line}")
    print(f"\nUNCOVERED (under half their words present): {k} of {n} = {k/n*100:.4f}%")
    for line in ci(k, n):
        print(f"    {line}")

    print(f"\nTHE {min(a.show, k)} LEAST-COVERED VERDICTS -- these are the ones to")
    print("read again by hand, because low coverage CANNOT be explained by paraphrase:\n")
    for hit, v, w in unc[:a.show]:
        txt = " ".join(v["text"].split())
        print(f"  [{hit*100:5.1f}%] {v['date']}  {pathlib.Path(v['file']).name[:44]}")
        print(f"           {txt[:150]}")

    print("\n" + "=" * 76)
    print("LIMIT RESTATED: high coverage is a NECESSARY condition for having acted")
    print("on a verdict, never a sufficient one. A verdict whose words all appear")
    print("may still have been misread -- as 1 was on 2026-10-16, when a question")
    print("ending in a question mark was recorded as an assertion. This measures")
    print("NEGLECT, which is detectable, not COMPREHENSION, which is not.")
    print("=" * 76)
    return 0

if __name__ == "__main__":
    sys.exit(main())
