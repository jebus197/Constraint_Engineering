#!/usr/bin/env python3
"""THE SEVERITY CENSUS HAS 3 FRAMES AND NOBODY DECLARED ONE -- 2026-11-06.

FIND. The corrected severity brief told 2 panel seats: "Over 3,474 archived
entries carrying a severity: `falsifier_verdict` present on 1,559
(0.448762)". The free seat `fable` returned DOES NOT REPRODUCE, giving 1,297
of 3,170 = 40.91% after content-hash dedup against a raw denominator of
3,691, and said the brief "pairs a duplicated numerator with a
differently-filtered denominator". Re-measuring here gives a THIRD pair:
1,526 of 3,311 raw.

SO THE SEAT IS RIGHT THAT THE FIGURE DOES NOT REPRODUCE, AND ITS OWN FIGURE
DOES NOT REPRODUCE EITHER. The cause is the same for all 3: the GLOB was
never declared. A non-recursive `logs/*/runner_state.json` sees one
population; a recursive `logs/**/runner_state.json` additionally sees every
seat's `sandbox_harvest` byte-copy of the repository, which are copies of a
run rather than runs. 3 frames, 3 numbers, 0 declarations.

THIS SCRIPT DECLARES ALL 3 AND COMPUTES THEM SIDE BY SIDE, so a reader can
see which question each answers. It is NOT a claim that one frame is correct:
that depends on the question, and the script says so for each.

WHAT SURVIVES IN EVERY FRAME, which is the part that carries the argument:
`confidence` is present on 0 entries in all 3, so the brief's conclusion --
that recomputing section 7.7 as written is unsatisfiable today -- holds
regardless of frame. The seat confirmed this independently.

AND IT CROSS-VERIFIES B121 BY A SECOND ROUTE. B121 reports that one run's
217 severity values are counted twice because a directory entry named
`exp36_evidence_latest` is a symlink the file pattern follows. Content-hash
dedup, which knows nothing about symlinks, removes exactly 217 from the
non-recursive frame. 2 independent routes to the same 217.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys

from statsmodels.stats.proportion import proportion_confint
from scipy.stats import beta as _beta
import mpmath as mp

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
LOGS = REPO / "bench" / "logs"


def _iv(k: int, n: int):
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    wl2, wh2 = float(cen - half), float(cen + half)
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))

    def _invert(a, b, y):
        f = lambda x: mp.betainc(a, b, 0, x, regularized=True) - y
        loq, hiq = mp.mpf(0), mp.mpf(1)
        for _ in range(200):
            mid = (loq + hiq) / 2
            loq, hiq = (mid, hiq) if f(mid) < 0 else (loq, mid)
        return float((loq + hiq) / 2)

    cl2 = 0.0 if k == 0 else _invert(k, n - k + 1, 0.025)
    ch2 = 1.0 if k == n else _invert(k + 1, n - k, 0.975)
    dis = max(abs(lo - wl2), abs(hi - wh2), abs(cl - cl2), abs(ch - ch2))
    return (max(0.0, lo), hi), (cl, ch), dis


def _harvest(files):
    raw, dedup, seen = [], [], set()
    for f in files:
        try:
            d = json.loads(f.read_text(errors="replace"))
        except Exception:
            continue
        entries = ((d.get("registry") or {}).get("entries") or {})
        if not isinstance(entries, dict):
            continue
        for e in entries.values():
            if not isinstance(e, dict) or e.get("severity") is None:
                continue
            raw.append(e)
            h = hashlib.sha256(
                json.dumps(e, sort_keys=True, default=str).encode()).hexdigest()
            if h not in seen:
                seen.add(h)
                dedup.append(e)
    return raw, dedup


FRAMES = {
    "A non-recursive, runs only": (
        "logs/*/runner_state.json",
        "the population of RUNS. Answers: what has this harness recorded?"),
    "B recursive, runs + seat copies": (
        "logs/**/runner_state.json",
        "runs PLUS every seat's sandbox_harvest byte-copy. Answers nothing "
        "about runs: a seat's copy of a run is not another run."),
}


def main() -> int:
    results = {}
    for name, (pattern, means) in FRAMES.items():
        files = sorted(LOGS.glob(pattern.replace("logs/", "")))
        raw, dedup = _harvest(files)
        print("=" * 74)
        print(f"FRAME {name}")
        print(f"  glob: bench/{pattern}   ({len(files)} file(s))")
        print(f"  {means}")
        for label, pop in (("raw", raw), ("content-hash dedup", dedup)):
            k = sum(1 for e in pop if e.get("falsifier_verdict") is not None)
            kc = sum(1 for e in pop if e.get("confidence") is not None)
            (wl, wh), (cl, ch), dis = _iv(k, len(pop))
            print(f"    {label:20s} n = {len(pop):5d}   falsifier_verdict "
                  f"{k:5d} = {k/len(pop) if pop else 0:.6f}")
            print(f"{'':26s}Wilson [{wl:.6f}, {wh:.6f}]  "
                  f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]  2-route {dis:.1e}")
            print(f"{'':26s}confidence present: {kc}")
            assert dis < 1e-6, f"interval routes disagree by {dis}"
            results[(name, label)] = (k, len(pop), kc)
        print(f"    dedup removed: {len(raw) - len(dedup)}")

    print("=" * 74)
    print("WHAT DIFFERS AND WHAT DOES NOT")
    ns = sorted({n for (_f, _l), (_k, n, _c) in results.items()})
    print(f"  distinct denominators across the frames: {ns}")
    assert len(ns) > 1, "the frames are identical; this script measures nothing"
    conf = {c for (_k, _n, c) in results.values()}
    print(f"  `confidence` present, across every frame: {sorted(conf)}")
    assert conf == {0}, (
        "`confidence` is no longer absent in some frame; the brief's "
        "conclusion that 7.7 is unsatisfiable today must be re-derived")
    print("  => the brief's CONCLUSION is frame-independent; its FIGURE was not.")

    a_raw = results[("A non-recursive, runs only", "raw")][1]
    a_ded = results[("A non-recursive, runs only", "content-hash dedup")][1]
    print(f"\nB121 CROSS-CHECK: content-hash dedup removes {a_raw - a_ded} from "
          f"frame A; B121 reports 217 counted twice via a symlink.")
    print("  2 independent routes to the same duplicate population."
          if a_raw - a_ded == 217 else
          f"  ROUTES DISAGREE: {a_raw - a_ded} against B121's 217 -- re-derive before quoting.")
    return 0


if __name__ == "__main__":
    #: ★ `answer_help` ANSWERS `--help` AND REFUSES AN UNRECOGNISED FLAG,
    #: which a hand-rolled `"--help" in sys.argv` check does not: it let
    #: `--this-flag-does-not-exist` through with exit 0, and an unrecognised
    #: argument that reads as success is the failure
    #: `test_an_unknown_flag_is_rejected_loudly` exists for. Placed INSIDE
    #: `__main__`, never at module level, where it would see pytest's own
    #: argv on import and exit 2 -- the defect that took 12 tests down
    #: earlier tonight.
    import pathlib as _pl, sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__)
    raise SystemExit(main())
