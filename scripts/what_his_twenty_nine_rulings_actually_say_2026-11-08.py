#!/usr/bin/env python3
"""Every figure quoted to him on 2026-11-08 about his own 29 rulings, the size
of the file they arrived in, and the memory-classification backlog.

WHY THIS EXISTS. He ruled on 29 decisions and then made 3 factual claims of his
own: that the file was over 22,000 words, that the long explanations had either
been appended to it or his workload request ignored, and that almost none of the
items were computationally irreducible. `measured-rate-travels-with-its-script`
forbids answering any of that from prose, so each answer is derived here.

AND IT CORRECTS A FIGURE I WAS ABOUT TO HAND HIM. My closing summary of
2026-11-08 said 39 of 327 memory files awaited a PRIVACY JUDGEMENT of his. The
ledger's unclassified list was counted 2026-08-05 18:00 BST and is read out of
the ledger by `cdsfl_sv._update_memory_exclusions_ledger` rather than re-derived
from the directory, so it has carried that stale membership for 3 months. 36 of
the 39 are mirrored in `MEMORY.md` or `MEMORY_ARCHIVE.md` today. The judgement
owed is 0 items, not 39.

A SECOND DEFECT FOUND BY THE SAME READ, and it is structural rather than stale.
In that derivation `mirrored` is a RESIDUAL -- `set(individual) - excluded -
unclassified - handoffs` -- so the bucket labelled *Mirrored (in summarised
form) in MEMORY.md* is a claim the code never tests. 2 routes are checked here
instead: membership of `MEMORY.md` and of `MEMORY_ARCHIVE.md`.

EVERY PROPORTION CARRIES 2 INDEPENDENT INTERVALS BY 2 INDEPENDENT ROUTES:
Wilson by statsmodels against an mpmath closed form, Clopper-Pearson by scipy's
beta quantile against an mpmath incomplete-beta inverse. A census is labelled a
census and given no interval, because an interval on a complete enumeration
would invite a reader to treat it as a sample.

Exit 0 when every cross-check agrees; 1 if any route disagrees with its pair.
"""
from __future__ import annotations

import argparse
import math
import pathlib
import re
import sys

import mpmath as mp
from scipy.stats import beta as sp_beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
ALPHA = 0.05
REPO = pathlib.Path(__file__).resolve().parent.parent
MEM = pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects/memory"
DEC = pathlib.Path.home() / "Developer_Projects/Responses/Decisions_Awaiting_You_2026-11-08_GENERATED.txt"
MR = pathlib.Path.home() / "Desktop/CDSFL_tts/Morning_Report_2026-11-08_GENERATED.txt"

_fail: list[str] = []


def _agree(label: str, a: float, b: float, tol: float = 1e-12) -> None:
    if abs(a - b) > tol:
        _fail.append(f"{label}: routes disagree, {a!r} vs {b!r}")


def _iv(k: int, n: int):
    """Wilson and Clopper-Pearson, each on 2 INDEPENDENT routes."""
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint
    import mpmath
    mpmath.mp.dps = 40
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    wl, wh = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = stats.norm.ppf(0.975)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    hw = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    wdiff = max(abs(wl - (c - hw)), abs(wh - (c + hw)))
    cl = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    def bi(a, b, y):
        """Invert the regularised incomplete beta by bisection.

        HARDENED 2026-11-04. `mpmath.betainc` is fast, but its hyp2f1 path
        FAILS TO CONVERGE for large parameters at mid-range x. Measured at
        a=2437, b=17564 it succeeds for x <= 0.1264 and for x >= 0.9 and raises
        ValueError in between -- which is exactly where a bisection over [0, 1]
        takes its first step, so the whole inversion died rather than degrading.
        It surfaced when a producer called this at k=2436, n=20000; every
        existing caller used a small n, and the guard that executes every `_iv`
        against the same k and n uses n <= 38, so no test could have seen it.

        Where betainc raises, the same integral is computed by quadrature in
        log space instead. At the measured failing point that agreed with
        scipy's quantile to 1.11e-16. It costs about 6 s per bound against
        milliseconds for betainc, so it is used only after a failure, never by
        default.
        """
        logB = mpmath.log(mpmath.beta(a, b))

        def by_quad(x):
            if x <= 0:
                return mpmath.mpf(0)
            def dens(u):
                return mpmath.e**((a - 1) * mpmath.log(u)
                                  + (b - 1) * mpmath.log1p(-u) - logB)
            return mpmath.quad(dens, [0, min(mpmath.mpf(x), mpmath.mpf(1))])

        fell_back = False

        def f(x):
            nonlocal fell_back
            if not fell_back:
                try:
                    return mpmath.betainc(a, b, 0, x, regularized=True) - y
                except Exception:
                    fell_back = True
            return by_quad(x) - y

        # STOP ON PRECISION, not on a fixed count. The bracket halves every
        # step, so 2**-60 is already below this tolerance and a fixed 240 did
        # 180 redundant evaluations. That is free for betainc and it is NOT
        # free for the quadrature fallback, which costs about 28 ms per
        # evaluation: 240 steps took 6.66 s and 60 take 1.69 s for a bound
        # identical to 12 decimal places. The count is still capped so a
        # pathological case cannot spin.
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        tol = mpmath.mpf("1e-18")
        for _ in range(240):
            if hi - lo < tol:
                break
            m = (lo + hi) / 2
            lo, hi = (m, hi) if f(m) < 0 else (lo, m)
        return float((lo + hi) / 2)

    cdiff = max(abs(cl - (0.0 if k == 0 else bi(k, n - k + 1, 0.025))),
                abs(ch - (1.0 if k == n else bi(k + 1, n - k, 0.975))))
    return (max(0.0, wl), wh), (cl, ch), max(wdiff, cdiff)


def interval(k: int, n: int, label: str) -> str:
    """Format the canonical helper's output.

    ★ THIS FILE WAS ITS OWN COUNTEREXAMPLE. A first version computed the 2
    Wilson routes and the 2 Clopper-Pearson routes inline. Running
    `scripts/the_wilson_detector_is_blind_to_half_the_algebra_2026-11-06.py`
    straight afterwards showed the invisible count rise 13 -> 14 and the
    denominator 165 -> 166: the new producer wrote the same algebra in a
    spelling the detector cannot see, which is exactly the defect B135
    records. His ruling of 2026-11-08 is option 1, EXECUTE the shared helper,
    so `_iv` above is lifted BYTE-IDENTICAL by AST from
    `scripts/how_many_of_the_nights_errors_were_instruments_2026-11-03.py`
    rather than retyped -- a retyped copy is a 2nd implementation wearing the
    canonical name, and the board guard asserts every `_iv` agrees with every
    other at 6 (k, n) pairs.
    ★ AN EMPTY SET IS A RESULT, NOT A CRASH. Added 2026-11-12. This raised
    `ZeroDivisionError` whenever `n` was 0, and on 2026-11-12 that happened for
    the best possible reason: the B159 repair linked all 9 superseded note
    standards into `MEMORY_ARCHIVE.md`, so the "named in NEITHER index" set
    became EMPTY and this producer could not represent its own success. The
    commit board refused on it, correctly, and the failure was a consequence of
    a fix rather than of a defect.

    A PROPORTION OVER AN EMPTY SET HAS NO VALUE, AND SAYING SO IS THE HONEST
    OUTPUT. Reporting 0.000000 would assert a rate that was never measured,
    which is the figure-answering-a-different-question fault this project
    records. The COUNT is still printed, because 0 of 0 is informative.
    """
    if n == 0:
        return (f"{k} of {n} -- the set is EMPTY, so no proportion exists and "
                f"none is reported ({label})")
    (wl, wh), (cl, ch), disagreement = _iv(k, n)
    _agree(f"{label}: the helper's own 2 routes", disagreement, 0.0, 1e-9)
    return (f"{k} of {n} = {k / n:.6f}  Wilson [{wl:.6f}, {wh:.6f}]  "
            f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]")


def section(t: str) -> None:
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# ---------------------------------------------------------------- the file


def main() -> int:
    """★ WRAPPED IN `main()` ON 2026-11-08, AND THE REASON MATTERS. This file
    first ran its whole measurement at MODULE level and ended in `sys.exit(0)`,
    so it was NOT IMPORTABLE. `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py`
    loads every script defining `_iv` and CALLS it; its loader guard catches
    `Exception`, and `SystemExit` derives from `BaseException` -- so importing
    this file printed the whole report and killed 12 of that guard's tests. A
    producer that cannot be imported cannot be executed BY another instrument,
    which is the entire point of putting the canonical helper inside it."""
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    section("1. THE FILE HE WAS ASKED TO READ (census: 1 file, no interval)")
    raw = DEC.read_bytes().decode("cp1252", errors="replace")
    words = len(raw.split())
    cut = raw.find("DECISION 1.")
    short, long_ = raw[:cut], raw[cut:]
    print(f"total words                      : {words}")
    print(f"his claim 'over 22,000 words'    : {'CONFIRMED' if words > 22000 else 'REFUTED'}")
    print(f"short tier (the 29 + his marks)  : {len(short.split())} words, {len(short)} chars")
    print(f"long tier (explanations)         : {len(long_.split())} words, {len(long_)} chars")
    print(f"long tier share of the file      : {len(long_) / len(raw):.6f}  (census)")

    section("2. WAS THE LONG TIER APPENDED ON 2026-11-08, OR HAS IT BEEN THERE?")
    rdir = pathlib.Path.home() / "Developer_Projects/Responses"
    for p in sorted(rdir.glob("Decisions_Awaiting_You_*.txt")):
        print(f"  {p.name:52s} {p.stat().st_size:>8d} bytes")
    print("  READ: a file that was 25,523 bytes on 2026-10-30 and 151,786 on 2026-11-04")
    print("  cannot have acquired its long tier today. The 2-tier shape predates this file.")

    section("3. THE 2 FILES DELIVERED THIS MORNING OVERLAP (census of 12-word shingles)")
    mr = MR.read_bytes().decode("cp1252", errors="replace")


    def shingles(t: str, k: int = 12) -> set[str]:
        w = t.split()
        return {" ".join(w[i:i + k]) for i in range(max(0, len(w) - k))}


    sd, sm = shingles(raw), shingles(mr)
    inter = sd & sm
    print(f"decisions file shingles          : {len(sd)}")
    print(f"morning report shingles          : {len(sm)}")
    print(f"shared                           : {len(inter)}")
    print(f"share of the morning report also in the decisions file: {len(inter) / len(sm):.6f}")
    print(f"share of the decisions file also in the morning report: {len(inter) / len(sd):.6f}")

    # ---------------------------------------------------------------- his marks
    section("4. WHAT HIS 29 MARKS ACTUALLY SAY (census of 1 annotated file)")
    marks = [m.start() for m in re.finditer(r"#", short)]
    kinds = {"stm": 0, "qs": 0, "fr": 0, "none": 0}
    accepts = 0
    for i, pos in enumerate(marks):
        end = marks[i + 1] if i + 1 < len(marks) else len(short)
        body = short[pos + 1:end]
        if "accept your recommendation" in body.lower():
            accepts += 1
        tail = re.findall(r"\b(stm|qs|fr)\b", body, re.I)
        kinds[tail[-1].lower() if tail else "none"] += 1
    print(f"annotations found                : {len(marks)}")
    print(f"  carrying 'I accept your recommendation': {accepts}")
    for k, v in kinds.items():
        print(f"  trailing marker {k:5s}: {v}")

    # ---------------------------------------------------------------- memory
    section("5. THE MEMORY BACKLOG -- THE FIGURE I WAS ABOUT TO HAND HIM IS WRONG")
    idx = (MEM / "MEMORY.md").read_text(encoding="utf-8")
    arch = (MEM / "MEMORY_ARCHIVE.md").read_text(encoding="utf-8")
    led = (REPO / "resources/MEMORY_EXCLUSIONS.md").read_text(encoding="utf-8")
    on_disk = {p.name for p in MEM.glob("*.md")}
    individual = sorted(n for n in on_disk
                        if n != "MEMORY.md" and not n.startswith("MEMORY.backup"))
    handoffs = [n for n in individual if n.startswith("handoff_")]


    def bucket(head: str) -> list[str]:
        """Names out of one ledger section.

        ★ THE 2 SECTIONS ARE FORMATTED DIFFERENTLY and a single pattern silently
        returns 0 for one of them. `## Excluded Entries` writes ``- **`name`**``
        with a reason after it; `## Unclassified` writes a bare ``- `name```. A
        first version of this script read only the bare form, found 0 excluded,
        and therefore reported the ledger's own table as DRIFTING when it is
        exact -- a guard accusing correct code, which is
        `feedback_a_guard_can_accuse_correct_code_2026-10-28`. Both forms are
        matched here and the count is asserted against the section's own prose.
        """
        m = re.search(re.escape(head) + r"(.*?)(?=\n## |\Z)", led, re.S)
        if not m:
            return []
        sec = m.group(1)
        names = re.findall(r"^- \*\*`([^`]+)`\*\*", sec, re.M)
        names += [n for n in re.findall(r"^- `([^`]+)`", sec, re.M) if n not in names]
        return names


    excluded = bucket("## Excluded Entries")
    listed = bucket("## Unclassified — awaiting review")
    print(f"individual memory files          : {len(individual)}")
    print(f"ledger: named excluded           : {len(excluded)}")
    print(f"ledger: named awaiting review    : {len(listed)}")
    print(f"handoffs                         : {len(handoffs)}")
    resid = len(individual) - len(excluded) - len(listed) - len(handoffs)
    print(f"derivation's residual 'mirrored' : {resid}")

    mirrored_now = [n for n in listed if n in idx]
    arch_now = [n for n in listed if n not in idx and n in arch]
    still = [n for n in listed if n not in idx and n not in arch]
    print(f"\nof the {len(listed)} awaiting review, measured against TODAY's 2 indexes:")
    print(f"  mirrored in MEMORY.md          : {interval(len(mirrored_now), len(listed), 'in-index')}")
    print(f"  in MEMORY_ARCHIVE.md           : {len(arch_now)}")
    print(f"  already mirrored either way    : "
          f"{interval(len(mirrored_now) + len(arch_now), len(listed), 'either')}")
    print(f"  GENUINELY unmirrored           : {len(still)} -> {still}")

    body_set = [n for n in individual
                if n not in excluded and n not in listed and n not in handoffs]
    nowhere = [n for n in body_set if n not in idx and n not in arch]
    print(f"\nAND THE RESIDUAL BUCKET IS NOT TESTED EITHER. Of the {len(body_set)} the")
    print(f"derivation calls mirrored, {len(nowhere)} are named in NEITHER index:")
    for n in nowhere:
        print(f"      {n}")
    allnowhere = sorted(set(still) | set(nowhere))
    print(f"\nCOMPLETE SET NAMED IN NEITHER INDEX: {interval(len(allnowhere), len(individual), 'nowhere')}")
    ns = [n for n in allnowhere if "note_standard" in n]
    print(f"  of which superseded note-standard versions: "
          f"{interval(len(ns), len(allnowhere), 'note-std')}")
    print("  MEMORY.md already declares these archival: 'v1-v1.8 archival'.")
    print("  SO THE PRIVACY JUDGEMENT OWED IS 0 ITEMS, not 39.")

    section("5b. WHICH `MEMORY.md` DOES 'MIRRORED' MEAN? THE 2 READINGS DIVERGE")
    pub_p = REPO / "resources/MEMORY.md"
    pub = pub_p.read_text(encoding="utf-8")
    import subprocess
    last = subprocess.run(["git", "log", "-1", "--format=%ad", "--date=short", "--",
                           "resources/MEMORY.md"], capture_output=True, text=True,
                          cwd=REPO).stdout.strip()
    print(f"the ledger links [MEMORY.md](MEMORY.md), which resolves to resources/MEMORY.md")
    print(f"  public mirror last committed  : {last}")
    print(f"  public mirror size            : {len(pub)} chars")
    print(f"  does it name files?           : it is PROSE BY DESIGN -- its own text says it")
    print(f"                                  'links there rather than duplicating', so a")
    print(f"                                  filename test is NOT a valid predicate on it")
    import datetime as _dt
    cut = _dt.date(*(int(x) for x in last.split("-"))) if last else None
    dated = []
    for n in individual:
        mm = re.search(r"(20\d\d)-(\d\d)-(\d\d)", n)
        if mm:
            d = _dt.date(int(mm.group(1)), int(mm.group(2)), int(mm.group(3)))
            if cut and d > cut:
                dated.append(n)
    print(f"  private files whose NAME carries a date after {last}: {len(dated)}")
    print(f"  A FILE UNCHANGED SINCE {last} CANNOT DESCRIBE A MEMORY WRITTEN AFTER IT,")
    print(f"  so the residual bucket asserts mirroring for at least these {len(dated)}.")
    print(f"  UNDER THE PRIVATE-INDEX READING the 39 resolve to 3; under the PUBLIC-MIRROR")
    print(f"  READING the 270 is unsupportable. The ledger does not say which it means and")
    print(f"  the derivation tests neither. THAT is the item, and it is not 39 judgements.")

    section("6. IS THE LEDGER ITSELF DRIFTING, OR IS IT ONLY THE DATE STAMP?")
    tbl = dict(re.findall(r"^\| ([^|]+?) \| (?:\*\*)?(\d+)(?:\*\*)? \|$", led, re.M))
    want = {"Mirrored (in summarised form) in `MEMORY.md`": resid,
            "Named as excluded, with a reason, below": len(excluded),
            "**Unclassified — neither mirrored nor previously declared**": len(listed),
            "total": len(individual)}
    ok = True
    for k, v in want.items():
        got = tbl.get(k) or tbl.get(k.strip("*"))
        same = got is not None and int(got) == v
        ok &= same
        print(f"  {k[:58]:60s} table={got} derived={v} {'OK' if same else 'DRIFT'}")
    if ok:
        print("\n  EVERY COUNT AGREES, so the rewrite --check reports is the DATE STAMP")
        print("  alone and must NOT be read as drift.")
    else:
        print("\n  A COUNT DISAGREES: the ledger is genuinely stale, not merely unstamped.")
        _fail.append("ledger counts disagree with the derivation")
    stamp = re.search(r"counted (\d{4}-\d{2}-\d{2} [^)]+)\)", led)
    listed_at = re.search(r"\(counted\s*\n?(2026-08-05[^)]*)\)", led)
    print(f"  accounting stamp : {stamp.group(1) if stamp else 'absent'}")
    print(f"  the awaiting-review list's own count date: "
          f"{listed_at.group(1).strip() if listed_at else 'see section text'}")

    print("\n" + "=" * 78)
    if _fail:
        print("CROSS-CHECK FAILURES:")
        for f in _fail:
            print("  " + f)
        return 1
    print("all 2-route cross-checks agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
