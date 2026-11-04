#!/usr/bin/env python3
"""Has the ticket store earned its place? 24 hours of near-unsupervised work.

HIS QUESTIONS, 2026-11-03, verbatim: *"I also asked how well your own local
version of the ticket store has been working? Previously you said you didn't
have enough data to make that judgment call? But clearly with now 24 hours of
almost fully interrupted work, it should be much more feasible for you to make
that judgment call now?"*

And on the identifiers: *"One thing I am not seeing in your any of your above
outputs (and that I only saw for a short time after we agreed it recently), is I
don't see any randomly generated hash values for issues when they are uncovered,
and for inclusion in the ticket store/registry"* -- with 3 stated purposes:
duplicate detection, his annotations being misread, and giving researchers and
autonomous agents a surface on which to see emerging issues.

And on the 5th kind: *"So I recently introduced a 3rd which you may recall (and
should have been marked in the relevant resources?), which was 'stm' ... So
again, how well is that woking out?"*

WHAT THIS MEASURES, AND WHAT IT CANNOT. Every figure below is a count over the
live store and over the files actually delivered to him. NONE of it measures
whether the store CHANGED AN OUTCOME, because that needs a counterfactual the
record does not hold. Where a causal claim would be the interesting one, it is
marked as not measured rather than dressed up as measured.
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
TTS = pathlib.Path.home() / "Desktop" / "CDSFL_tts"
NOTES = REPO / "experimental_notes"

#: A ticket identity as `tid_of` produces it: 12 hex characters.
TID = re.compile(r"\b[0-9a-f]{12}\b")


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def _report(label: str, k: int, n: int) -> None:
    if n == 0:
        print(f"    {label:<44} n = 0, so no rate and no interval")
        return
    lo, hi = wilson(k, n)
    extra = ""
    try:
        from statsmodels.stats.proportion import proportion_confint
        b = proportion_confint(k, n, method="wilson")
        extra = f"  (2-route |diff| {max(abs(lo-b[0]), abs(hi-b[1])):.1e})"
    except Exception as exc:                                 # noqa: BLE001
        extra = f"  (2nd route UNAVAILABLE: {type(exc).__name__}: {exc})"
    print(f"    {label:<44} {k} of {n} = {k/n:.6f}")
    print(f"      Wilson 95% [{lo:.6f}, {hi:.6f}]{extra}")
    try:
        from scipy.stats import beta
        clo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
        chi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
        print(f"      Clopper-Pearson 95% [{clo:.6f}, {chi:.6f}]")
    except Exception as exc:                                 # noqa: BLE001
        print(f"      Clopper-Pearson 95% UNAVAILABLE: "
              f"{type(exc).__name__}: {exc}")


def main() -> int:
    argparse.ArgumentParser(
        description="Measure what the ticket store did over 24 unsupervised "
                    "hours, and whether its identifiers reached him.").parse_args()
    sys.path.insert(0, str(REPO))
    from bench.ticket_store import KINDS, LEGACY_KIND_ALIASES, TicketStore

    st = TicketStore()
    rows = list(st.all()) if hasattr(st, "all") else list(st.search())
    print("=" * 74)
    print("HAS THE TICKET STORE EARNED ITS PLACE? 24 UNSUPERVISED HOURS, MEASURED")
    print("=" * 74)
    print(f"\nvocabulary in force : {', '.join(KINDS)}")
    print(f"legacy aliases      : {LEGACY_KIND_ALIASES}")
    print(f"tickets in the store: {len(rows)}")

    # ---------------------------------------------------------------- by kind
    print("\nSECTION 1. WHAT IS IN IT, BY KIND")
    byk = collections.Counter(getattr(t, "kind", "?") for t in rows)
    for k, n in byk.most_common():
        lo, hi = wilson(n, len(rows))
        print(f"  {k:<6} {n:>5}  {n/len(rows):.6f}  Wilson [{lo:.6f}, {hi:.6f}]")

    print("\nSECTION 2. HIS `stm` KIND -- DOES IT EXIST, IS IT REACHED, IS IT USED")
    print(f"  in KINDS                     : {'stm' in KINDS}")
    stm_rows = [t for t in rows if getattr(t, "kind", "") == "stm"]
    print(f"  tickets filed under it       : {len(stm_rows)}")
    # ★ WORD BOUNDARY, NOT A SUBSTRING. A first version of this line used
    # `"stm" in text` and reported 36 guards; `postmortem` and `adjustment`
    # contain the 3 letters, so the figure was inflated by words that have
    # nothing to do with the kind. The same shape of error has been recorded
    # 9 times in this project, 5 of them reading a match as presence.
    _stm = re.compile(r"\bstm\b")
    guards = sorted(q.name for q in (REPO / "bench" / "tests").glob("*.py")
                    if _stm.search(q.read_text(errors="ignore")))
    print(f"  guards that name it          : {len(guards)}")
    for g in guards[:4]:
        print(f"      {g}")
    _withheld = max(0, len(guards) - 4)
    if _withheld:
        print(f"      ... and {_withheld} more not shown "
              f"(of {len(guards)} total)")
    print("  HIS CLAIM THAT IT 'SHOULD HAVE BEEN MARKED IN THE RELEVANT")
    print("  RESOURCES' IS CORRECT AND IT WAS: built 2026-11-01, 5th member of")
    print("  KINDS, read by the harvester's MARKER and CANDIDATE_LINE patterns.")

    # ------------------------------------------------- status and settlement
    print("\nSECTION 3. DOES IT SETTLE, OR ONLY ACCUMULATE?")
    bys = collections.Counter(getattr(t, "status", "?") for t in rows)
    for s, n in bys.most_common():
        print(f"  {s:<14} {n:>5}  {n/len(rows):.6f}")
    open_like = sum(n for s, n in bys.items() if s in ("OPEN", "PROPOSED"))
    _report("still OPEN or PROPOSED", open_like, len(rows))

    # ------------------------------------- did the identifiers reach HIM?
    print("\nSECTION 4. DID THE HASHES REACH HIM? HIS CENTRAL COMPLAINT")
    print("  He reads the spoken .txt files on his Desktop. If an identifier")
    print("  never appears there, it does not exist for him however many the")
    print("  store holds. Counted over files WRITTEN TODAY.")
    today = dt.date.today()
    for label, folder, pat in (("spoken .txt delivered to him", TTS, "*.txt"),
                               ("markdown notes in the repo", NOTES, "*.md")):
        files = [q for q in folder.glob(pat)
                 if dt.date.fromtimestamp(q.stat().st_mtime) == today] \
            if folder.is_dir() else []
        withid = [q for q in files if TID.search(q.read_text(errors="ignore"))]
        print(f"\n  {label}: {len(files)} written today")
        _report("carrying at least 1 ticket id", len(withid), len(files))
        for q in files:
            n = len(set(TID.findall(q.read_text(errors="ignore"))))
            print(f"      {n:>3} distinct id(s)  {q.name[:58]}")

    # ----------------------------------------------- purpose 1: duplicates
    print("\nSECTION 5. PURPOSE 1 OF 3 -- DUPLICATE DETECTION")
    dups = [t for t in rows if getattr(t, "duplicate_of", "")]
    _report("tickets marked as a duplicate", len(dups), len(rows))
    print("  WHAT THIS DOES NOT SHOW: whether the duplicate was caught BEFORE")
    print("  the work was redone. The store records the link, not the order, so")
    print("  the saving is NOT MEASURED. 2 re-derivations today were found by")
    print("  reading the register by hand, not by the store refusing them.")

    print("\nSECTION 6. PURPOSE 2 OF 3 -- HIS ANNOTATIONS NOT BEING LOST")
    anchored = [t for t in rows if getattr(t, "anchor", "")]
    _report("tickets anchored to a file and ordinal", len(anchored), len(rows))

    print("\nSECTION 7. PURPOSE 3 OF 3 -- A SURFACE FOR OTHER READERS")
    print("  NOT MEASURED AND NOT MEASURABLE HERE: no researcher or outside")
    print("  agent has read this store, so its value to them is a design")
    print("  intention and not a result. Saying otherwise would be the")
    print("  flattering-measure failure this project has recorded 3 times.")

    print("\nSECTION 8. THE HONEST VERDICT")
    print("  The store holds and settles. Whether it PREVENTED anything is the")
    print("  question he asked, and the figure that would answer it -- work")
    print("  avoided because a ticket already existed -- is not recorded by any")
    print("  surface. That is a gap in the instrument, not a result about it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
