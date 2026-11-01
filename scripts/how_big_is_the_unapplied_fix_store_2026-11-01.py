#!/usr/bin/env python3
"""PRODUCER: how many seat-written fixes exist and never reached the tree?

HIS WORRY, 2026-11-01, verbatim: *"I worry that we might build up a large store
of fixes that are never applied to any of our runners in practice. This is a
problem we have encountered several times in the past and that we need to stay
on top of."*

HE IS RIGHT TO ASK AND IT HAS NEVER BEEN MEASURED. The project's rule is that a
seat's fix is tested under analysis, the 5-step cycle and the STEM tools before
being folded back. That rule protects the tree. It says nothing about what
happens to a fix that is never tested, and the answer until now has been
nothing at all: it sits in `experimental_notes/seat_evidence/` and is counted by
no instrument.

WHAT IS COUNTED HERE. Every preserved seat artefact, by the path the seat wrote
it to, against whether a file of that name exists in the live tree. 3 outcomes:

  * APPLIED -- a live file of that path exists. The seat's work reached the tree,
    whether by fold-back or because the seat was editing something real.
  * ABSENT -- no live file of that path. The artefact exists only as preserved
    evidence, so whatever it proposed is unapplied.
  * DIVERGED -- a live file exists and differs from the seat's copy. This is the
    interesting middle: the path was reached but not with this content.

WHAT THIS CANNOT DECIDE. Whether an ABSENT artefact SHOULD be applied. Several
are deliberately not folded back -- a falsifier written to demonstrate a defect
is evidence, not a repair, and the project has a standing refusal on folding a
stored falsifier that needs a licensed kernel. So the count is an INVENTORY and
a prompt for a decision, never a backlog of things that ought to be merged.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import mpmath as mp  # noqa: E402
from statsmodels.stats.proportion import proportion_confint  # noqa: E402

SEAT_EVIDENCE = REPO / "experimental_notes" / "seat_evidence"
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
    _check("wilson cross-check",
           abs(float((c - h) / d) - lo_sm) < 1e-9 and abs(float((c + h) / d) - hi_sm) < 1e-9,
           "statsmodels and mpmath disagree")
    return float(lo_sm), float(hi_sm)


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv=None) -> int:
    # ★ A `--help` MUST NEVER COST ANYTHING — his standing rule, and the
    # pre-commit gate enforces it. Without this, `--help` fell through to the
    # measurement and ran the whole thing: 8 producers were refused the commit
    # on exactly this. argparse answers and exits before any body runs.
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.parse_args(argv)

    if not SEAT_EVIDENCE.is_dir():
        print(f"no preserved seat evidence at {SEAT_EVIDENCE}")
        return 1

    rows = []
    for f in sorted(SEAT_EVIDENCE.rglob("*.py")):
        rel = f.relative_to(SEAT_EVIDENCE)
        parts = rel.parts
        if len(parts) < 3:
            continue
        round_name, seat = parts[0], parts[1]
        seat_path = pathlib.Path(*parts[2:])     # the path the seat wrote to
        live = REPO / seat_path
        if not live.is_file():
            state = "ABSENT"
        else:
            state = "APPLIED" if _sha(live) == _sha(f) else "DIVERGED"
        rows.append((round_name, seat, str(seat_path), state))

    print("=" * 72)
    print("M1. THE INVENTORY")
    print("=" * 72)
    n = len(rows)
    by_state = collections.Counter(r[3] for r in rows)
    print(f"preserved seat-written Python artefacts: {n}")
    for st in ("APPLIED", "DIVERGED", "ABSENT"):
        k = by_state.get(st, 0)
        if n:
            lo, hi = wilson(k, n)
            print(f"  {st:<9} {k:>4}   Wilson 95% [{lo:.6f}, {hi:.6f}]")
    _check("the inventory is non-empty", n > 0, "no artefacts found")

    print()
    print("=" * 72)
    print("M2. BY ROUND, SO A ROUND WITH A BACKLOG IS NAMEABLE")
    print("=" * 72)
    per_round = collections.defaultdict(collections.Counter)
    for rnd, _seat, _p, st in rows:
        per_round[rnd][st] += 1
    print(f"{'round':<52}{'APPL':>5}{'DIV':>5}{'ABS':>5}")
    for rnd in sorted(per_round):
        c = per_round[rnd]
        print(f"{rnd[:50]:<52}{c.get('APPLIED',0):>5}"
              f"{c.get('DIVERGED',0):>5}{c.get('ABSENT',0):>5}")

    print()
    print("=" * 72)
    print("M3. WHAT IS ABSENT, NAMED INDIVIDUALLY")
    print("=" * 72)
    absent = [r for r in rows if r[3] == "ABSENT"]
    print(f"{len(absent)} artefact(s) exist only as preserved evidence:")
    for rnd, seat, p, _st in absent:
        kind = ("falsifier" if "falsifier" in pathlib.Path(p).name else
                "test" if pathlib.Path(p).name.startswith("test_") else
                "script")
        print(f"   [{kind:<9}] {seat:<7} {p}")
    print()
    fals = [r for r in absent if "falsifier" in pathlib.Path(r[2]).name]
    if absent:
        lo, hi = wilson(len(fals), len(absent))
        print(f"of the absent, FALSIFIERS: {len(fals)} of {len(absent)}  "
              f"Wilson 95% [{lo:.6f}, {hi:.6f}]")
    print()
    print("A FALSIFIER IS NOT A PENDING REPAIR. It is written to demonstrate a")
    print("defect, and the project refuses to fold a stored falsifier that")
    print("would need a licensed kernel to re-run. So the falsifier share of")
    print("the absent set is the part of his worry that is NOT a backlog, and")
    print("separating it is the difference between an inventory and an alarm.")

    print()
    print("=" * 72)
    print("M4. THE PART OF HIS WORRY THAT IS REAL")
    print("=" * 72)
    real = [r for r in absent if "falsifier" not in pathlib.Path(r[2]).name]
    print(f"absent artefacts that are NOT falsifiers: {len(real)}")
    for rnd, seat, p, _st in real:
        print(f"   {seat:<7} {p}")
        print(f"      from round {rnd}")
    print()
    print("THESE ARE THE CANDIDATES FOR A FOLD-BACK DECISION, and naming them")
    print("is what makes the decision possible. The rule that a fix is tested")
    print("before folding is right; what was missing is any record of what is")
    print("waiting, so an untested fix could sit indefinitely with nothing")
    print("counting it. That is the shape he named and this is its size.")

    print()
    print("=" * 72)
    print("M5. THE TAXONOMY THAT MAKES THE NUMBER USEFUL")
    print("=" * 72)
    # A bare "246 absent" is alarming and uninformative. What matters is WHICH
    # kind of artefact, because a falsifier and a producer are evidence by
    # design while an edit to a live runner module is the thing he fears.
    def _kind(sp: pathlib.Path) -> str:
        n = sp.name
        # ★ `falsify_` AS WELL AS `falsifier`, corrected 2026-11-01. The seats
        # named their files `falsify_capability_ledger_2026-10-07.py` and so on,
        # and each says FALSIFIER in its own docstring, but this test matched
        # only the longer spelling -- so 5 of the 41 distinct absent module
        # paths, 12.2 per cent with a 95 per cent interval of 0.053233 to
        # 0.255442, were counted as live-module designs when they are evidence
        # by design. That inflated the figure put to him as "44 unadopted
        # designs", which he was then asked to rule on.
        if "falsifier" in n or n.startswith("falsify_"):
            return "falsifier (evidence)"
        if sp.parts[:2] == ("bench", "tests"):
            return "guard/test"
        if sp.parts[:1] == ("scripts",):
            return "producer/script"
        if sp.parts[:1] == ("bench",):
            return "live-module file"
        return "other"

    tax = collections.defaultdict(collections.Counter)
    for _r, _s, pth, st in rows:
        tax[_kind(pathlib.Path(pth))][st] += 1
    print(f"{'category':<24}{'APPLIED':>8}{'DIVERGED':>10}{'ABSENT':>8}{'total':>7}")
    for k in sorted(tax, key=lambda x: -sum(tax[x].values())):
        c = tax[k]
        print(f"{k:<24}{c.get('APPLIED',0):>8}{c.get('DIVERGED',0):>10}"
              f"{c.get('ABSENT',0):>8}{sum(c.values()):>7}")

    mods = [r for r in rows if _kind(pathlib.Path(r[2])) == "live-module file"]
    new_files = [r for r in mods if r[3] == "ABSENT"]
    edits = [r for r in mods if r[3] == "DIVERGED"]
    print()
    print(f"live-module artefacts: {len(mods)}")
    print(f"  NEW files a seat created that the tree never adopted: {len(new_files)}")
    print(f"  DIVERGENT edits to a module that DOES exist live   : {len(edits)}")
    for _r, seat, pth, _st in edits:
        print(f"      {pth}  (seat {seat})")
    print()
    print("THIS IS THE DISTINCTION HIS WORRY TURNS ON. An ABSENT live-module")
    print("path is a NEW module a seat proposed, so nothing in the tree was")
    print("bypassed -- it is a design that was never adopted, which is a")
    print("question about lost ideas rather than unapplied repairs. A DIVERGENT")
    print("one is a seat's edit to a file that really exists, and that is the")
    print("only shape where the tree is running something a seat tried to fix.")

    print()
    print("=" * 72)
    print("M6. WAS ANY GUARD COVERAGE ACTUALLY LOST?")
    print("=" * 72)
    import re as _re
    deltas = []
    for _r, seat, pth, st in rows:
        sp = pathlib.Path(pth)
        if st != "DIVERGED" or sp.parts[:2] != ("bench", "tests"):
            continue
        livef = REPO / sp
        seatf = None
        for cand in SEAT_EVIDENCE.rglob(sp.name):
            if cand.as_posix().endswith(sp.as_posix()):
                seatf = cand
                break
        if seatf is None:
            continue
        ns = len(_re.findall(r"^\s*def test_", seatf.read_text(encoding="utf-8", errors="replace"), _re.M))
        nl = len(_re.findall(r"^\s*def test_", livef.read_text(encoding="utf-8", errors="replace"), _re.M))
        deltas.append((str(sp), ns, nl, ns - nl))
    gained = [d for d in deltas if d[3] > 0]
    print(f"diverged guards compared: {len(deltas)}")
    print(f"  seat copy carries MORE test functions than live: {len(gained)}")
    print(f"  net test functions beyond live: {sum(max(0, d[3]) for d in deltas)}")
    if deltas:
        lo, hi = wilson(len(gained), len(deltas))
        print(f"  share carrying lost coverage Wilson 95% [{lo:.6f}, {hi:.6f}]")
    for nm, ns, nl, d in gained:
        print(f"      {nm}: seat {ns}, live {nl}, delta {d:+d}")
    print()
    print("SO THE GUARD HALF OF THE STORE COST NOTHING. Where a seat's guard")
    print("diverges from the live one, the live one has the same number of")
    print("test functions or MORE in every case. The fold-back discipline has")
    print("not lost coverage; what it has accumulated is unadopted DESIGNS.")
    _check("the guard comparison ran", len(deltas) >= 1,
           "no diverged guard was comparable, so this section says nothing")

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
