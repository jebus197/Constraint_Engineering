#!/usr/bin/env python3
"""PRODUCER: is the morning report's verdict list clean? 2026-10-31.

FOUNDER, 2026-10-31: *"But everything I need to know/rule on is in the updated
tts? There are no repetitions there either, or things I have already ruled on?"*

HE IS RIGHT TO ASK, AND THE RECORD SAYS SO RATHER THAN MY JUDGEMENT. The
project's own feedback index carries `feedback_already_ruled_and_misread_rates`
-- 11 of 45 items presented to him as open were already decided, and it
RECURRED on 2026-10-17. Answering this from confidence would be the third
instance. So the structural half is measured here and the judgement half is
labelled as judgement.

WHAT A SCRIPT CAN DECIDE, and does below: ordering, numbering gaps, pairwise
near-duplication, items whose text makes them CONDITIONAL on another item, and
coverage against the task list's own open entries and `ruled:` dates.

WHAT A SCRIPT CANNOT DECIDE: whether a given question is substantively the same
decision he already made in different words. That needs his words read, and it
is reported separately as a reading with the evidence attached, never as a
mechanical verdict.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

REPORT = REPO / "experimental_notes" / "Morning_Report_2026-10-31.txt"
FAILURES: list[str] = []


def _check(label: str, cond: bool, detail: str = "") -> None:
    if not cond:
        FAILURES.append(f"{label}: {detail}")


def wilson(k: int, n: int) -> tuple[float, float]:
    lo_sm, hi_sm = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054")
    p = mp.mpf(k) / n
    d = 1 + z**2 / n
    c = p + z**2 / (2 * n)
    h = z * mp.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))
    lo_mp, hi_mp = float((c - h) / d), float((c + h) / d)
    _check("wilson cross-check", abs(lo_sm - lo_mp) < 1e-9 and abs(hi_sm - hi_mp) < 1e-9,
           f"statsmodels vs mpmath disagree: {lo_sm},{hi_sm} / {lo_mp},{hi_mp}")
    return float(lo_sm), float(hi_sm)


STOP = set("""a an and are as at be because but by can does for from has have her his
if in into is it its my of on or our should so than that the their them then there
this to was were what when where which who will with would you your i me not no now
be been being do done just also only very more most some any each both other same
such own too s t don now d ll m o re ve y ain aren couldn didn doesn hadn hasn haven
isn ma mightn mustn needn shan shouldn wasn weren won wouldn""".split())


def tokens(text: str) -> set:
    return {w for w in re.findall(r"[a-z]{3,}", text.lower()) if w not in STOP}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main(argv=None) -> int:
    # ★ A `--help` MUST NEVER COST ANYTHING — his standing rule, and the
    # pre-commit gate enforces it. Without this, `--help` fell through to the
    # measurement and ran the whole thing: 8 producers were refused the commit
    # on exactly this. argparse answers and exits before any body runs.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    body = REPORT.read_text(encoding="utf-8")
    m = re.search(r"^PART 7\..*?\n(.*?)\nPART 8\.", body, re.S | re.M)
    assert m, "PART 7 not found"
    block = m.group(1)

    items: list[tuple[int, str]] = []
    for line in block.splitlines():
        mm = re.match(r"^(\d+)\.\s+(.*)$", line.strip())
        if mm:
            items.append((int(mm.group(1)), mm.group(2)))

    print("=" * 72)
    print("M1. STRUCTURE: ORDER, GAPS, DUPLICATE NUMBERS")
    print("=" * 72)
    nums = [n for n, _ in items]
    print(f"items parsed: {len(items)}")
    print(f"numbers as they appear: {nums}")
    in_order = nums == sorted(nums)
    print(f"printed in ascending order: {in_order}")
    out_of_place = [(i, n) for i, n in enumerate(nums)
                    if n != sorted(nums)[i]]
    if not in_order:
        print(f"positions where the printed number differs from sorted order: "
              f"{[(pos + 1, n) for pos, n in out_of_place]}")
        print("THIS MATTERS BECAUSE HE READS BY TTS: a reader hearing '8' then")
        print("'7' then jumping to '12, 13, 11' cannot track what is left.")
    expected = set(range(1, max(nums) + 1))
    print(f"missing numbers in 1..{max(nums)}: {sorted(expected - set(nums))}")
    dupes = {n for n in nums if nums.count(n) > 1}
    print(f"duplicate numbers: {sorted(dupes)}")
    _check("no duplicate item numbers", not dupes, f"{sorted(dupes)}")

    print()
    print("=" * 72)
    print("M2. NEAR-DUPLICATION BETWEEN ITEMS")
    print("=" * 72)
    toks = {n: tokens(t) for n, t in items}
    pairs = []
    for i, (na, _) in enumerate(items):
        for nb, _ in items[i + 1:]:
            j = jaccard(toks[na], toks[nb])
            pairs.append((j, na, nb))
    pairs.sort(reverse=True)
    print("the 5 most similar pairs, by shared distinctive words:")
    for j, na, nb in pairs[:5]:
        print(f"   items {na} and {nb}: Jaccard {j:.4f}")
        print(f"      shared: {sorted(toks[na] & toks[nb])[:12]}")
    THRESH = 0.30
    near = [(j, na, nb) for j, na, nb in pairs if j >= THRESH]
    lo, hi = wilson(len(near), len(pairs))
    print()
    print(f"pairs at or above Jaccard {THRESH}: {len(near)} of {len(pairs)}  "
          f"Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print("A HIGH SCORE IS NOT A DUPLICATE. These items share vocabulary by")
    print("subject -- 3 of them are about the same new mechanism -- so the")
    print("score flags candidates for reading, and the reading is below.")

    print()
    print("=" * 72)
    print("M3. ITEMS THAT ARE CONDITIONAL ON ANOTHER ITEM")
    print("=" * 72)
    # Mechanical: an item whose text defers to a decision named in another item.
    DEFER = re.compile(r"\b(wait for your|until your|pre ?empt|depends on|"
                       r"conditional on|after your)\b", re.I)
    dependent = [(n, t) for n, t in items if DEFER.search(t)]
    print(f"items whose own text says they wait on another decision: "
          f"{len(dependent)}")
    for n, t in dependent:
        print(f"   item {n}: {t[:150]}")
    print()
    print("An item that cannot be answered until another is answered is not an")
    print("independent decision for him. It belongs UNDER its parent, so the")
    print("list states the number of decisions he actually has to make.")

    print()
    print("=" * 72)
    print("M4. COVERAGE AGAINST THE TASK LIST'S OWN OPEN ENTRIES")
    print("=" * 72)
    import task_list_markers as tlm
    entries = tlm.parse_entries()
    open_entries = [e for e in entries if e.state == "OPEN"]
    print(f"OPEN entries on the master list: {len(open_entries)}")
    covered, uncovered = [], []
    for e in open_entries:
        named = re.search(rf"\b{re.escape(e.ident)}\b", block)
        (covered if named else uncovered).append(e.ident)
    lo, hi = wilson(len(covered), len(open_entries))
    print(f"OPEN entries named by code in PART 7: {len(covered)} of "
          f"{len(open_entries)}  Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print(f"   named:   {covered}")
    print(f"   NOT named: {uncovered}")
    print()
    print("NAMING BY CODE IS NOT THE ONLY WAY TO COVER AN ENTRY, so an unnamed")
    print("entry is a candidate rather than a gap -- PART 7 describes several")
    print("items in prose without their code, which is the format he asked")
    print("for. Each unnamed one is read below.")

    print()
    print("=" * 72)
    print("M5. WHICH OPEN ENTRIES CARRY A `ruled:` DATE ALREADY")
    print("=" * 72)
    ruled = [(e.ident, e.ruled) for e in open_entries if getattr(e, "ruled", None)]
    unruled = [e.ident for e in open_entries if not getattr(e, "ruled", None)]
    print(f"OPEN entries with a recorded ruling date: {len(ruled)}")
    for ident, d in ruled:
        print(f"   {ident}: ruled {d}")
    print(f"OPEN entries with NO recorded ruling: {unruled}")
    print()
    print("A `ruled:` DATE ON AN OPEN ENTRY IS NOT A CONTRADICTION. The field")
    print("records that HE DECIDED something about the entry; the entry stays")
    print("OPEN because work or a further decision remains. But it IS the exact")
    print("place where an item gets re-presented as though undecided, which is")
    print("the 11-of-45 failure of 2026-10-05 that recurred on 2026-10-17.")

    print()
    print("=" * 72)
    if FAILURES:
        print(f"CONSISTENCY CHECKS FAILED: {len(FAILURES)}")
        for f in FAILURES:
            print("   " + f)
        return 1
    print("ALL CONSISTENCY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
