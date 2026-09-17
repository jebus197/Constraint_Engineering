#!/usr/bin/env python3
"""How many DONE entries claim more than their evidence shows?

The brief that sends this to the panel quotes this rate, and
`measured-rate-travels-with-its-script` requires the producing script to be
committed beside it. It reads the committed audit evidence and recomputes from
scratch, so the figure in the brief is re-executable rather than typed -- the
defect that put 'gamma is 0.451' in front of 2 seats when the value was
0.415413.

Round 1 ids are intersected with the task list's real DONE ids, because 5 of the
29 upheld findings in that round were about entry ids that do not exist.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EVID = REPO / "experimental_notes" / "evidence" / "done_audit_2026-09-11"
TASKS = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"
ROUND2 = EVID / "round2_never_audited_13.json"


def round2_upheld() -> set[str]:
    """Round 2's overclaiming ids, DERIVED from the adjudication.

    THIS REPLACED A HAND-TYPED TUPLE, AND THE TUPLE WAS WRONG (2026-09-17).
    It read `("3.3", "9.2", "9.3", "9.4", "L2", "P7")` -- 6 ids transcribed by
    eye from the round-2 evidence, and never compared against the file they came
    from. That file marks SEVEN entries non-SUPPORTED: `7.3` carries verdict
    PARTIAL and was dropped in transcription, so the census reported 30 where
    its own committed evidence says 31.

    Found by the cc2 seat in panel round 16 and confirmed here independently
    before being accepted. It is the same defect class the 30 entries are being
    closed for -- a figure asserted rather than produced -- committed inside the
    instrument built to measure that class.

    Deriving is cheaper than guarding: it removes the failure mode by
    construction rather than adding a checker that could itself drift.
    """
    rows: list[dict] = []

    def walk(o) -> None:
        if isinstance(o, dict):
            if "id" in o and "verdict" in o:
                rows.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(json.loads(ROUND2.read_text(encoding="utf-8")))
    return {str(r["id"]).strip() for r in rows
            if str(r.get("verdict", "")).strip().upper() not in ("SUPPORTED", "")}


def done_ids() -> set[str]:
    text = TASKS.read_text(encoding="utf-8").split("# SUPPLEMENTARY LIST")[0]
    return {m.group(1) for m in
            re.finditer(r"<!--\s*task:\s*([A-Za-z0-9._]+)\s*\|\s*state:\s*DONE", text)}


def audited_ids() -> set[str]:
    """Every DONE entry an audit actually reached.

    THE DENOMINATOR WAS THE WRONG POPULATION (2026-09-17, found by the fable
    seat in panel round 16 and confirmed here). `n` counted TODAY's DONE
    markers while `k` came from the AUDITED population, so an entry that went
    DONE after the audit was silently counted as audited-and-clean. Exactly 1
    had: A11, closed earlier the same night. That is the defect class M1
    documents -- a count measured against a population it does not belong to --
    recurring inside the instrument built to measure that class.
    """
    r1 = {str(r["id"]).strip()
          for r in json.loads((EVID / "audit_findings.json").read_text(encoding="utf-8"))}
    return (r1 | _round2_ids()) & done_ids()


def _round2_ids() -> set[str]:
    rows: list[dict] = []

    def walk(o) -> None:
        if isinstance(o, dict):
            if "id" in o and "verdict" in o:
                rows.append(o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(json.loads(ROUND2.read_text(encoding="utf-8")))
    return {str(r["id"]).strip() for r in rows}


def overclaiming() -> tuple[set[str], set[str]]:
    real = audited_ids()
    verdicts = json.loads((EVID / "verification_verdicts.json").read_text(encoding="utf-8"))
    r1 = {str(r["id"]).strip() for r in verdicts if r.get("upheld") is True}
    # THE INTERSECTION IS SYMMETRIC. It used to be applied to round 1 only, so a
    # phantom id in the round-2 half could inflate the numerator unchecked --
    # and round 1 genuinely carried 5 ids that are not entries.
    return (r1 | round2_upheld()) & real, real


def wilson(k: int, n: int) -> tuple[float, float, float]:
    """Wilson 95% interval, computed 3 ways, returned with its worst disagreement.

    EVERY PROPORTION THIS PROJECT QUOTES IS CROSS-VERIFIED, and until 2026-09-17
    only the headline interval here was. The extension that added round 1 and the
    superseded figure computed them with statsmodels alone -- caught by
    `test_the_interval_is_cross_verified_inside_the_script`, which is exactly what
    that guard is for.

    THE AGREEMENT IS MEASURED, NOT TYPED. The previous version printed the
    literal string "agrees to 0.0e+00" beside an interval whose real worst
    disagreement is 5.55e-17. A typed agreement figure asserts a verification
    rather than reporting one, which is the defect class this script exists to
    close.
    """
    import numpy as np
    import scipy.stats as st
    import mpmath as mp
    from statsmodels.stats.proportion import proportion_confint

    lo, hi = proportion_confint(k, n, method="wilson")

    z = st.norm.ppf(0.975)
    p_ = k / n
    d = 1 + z * z / n
    c = (p_ + z * z / (2 * n)) / d
    h = z * np.sqrt(p_ * (1 - p_) / n + z * z / (4 * n * n)) / d

    mp.mp.dps = 30
    zm, nm, km = mp.mpf(str(z)), mp.mpf(n), mp.mpf(k)
    pm = km / nm
    dm = 1 + zm**2 / nm
    cm = (pm + zm**2 / (2 * nm)) / dm
    hm = zm * mp.sqrt(pm * (1 - pm) / nm + zm**2 / (4 * nm**2)) / dm

    worst = max(abs(lo - (c - h)), abs(hi - (c + h)),
                float(abs(mp.mpf(str(lo)) - (cm - hm))),
                float(abs(mp.mpf(str(hi)) - (cm + hm))))
    assert worst < 1e-12, f"the 3 implementations disagree by {worst:.3e}"
    return lo, hi, worst


def clopper_pearson(k: int, n: int) -> tuple[float, float, float]:
    """Clopper-Pearson 95%, statsmodels against scipy's beta quantiles directly."""
    import scipy.stats as st
    from statsmodels.stats.proportion import proportion_confint

    lo, hi = proportion_confint(k, n, method="beta")
    lo2 = st.beta.ppf(0.025, k, n - k + 1)
    hi2 = st.beta.ppf(0.975, k + 1, n - k)
    worst = max(abs(lo - lo2), abs(hi - hi2))
    assert worst < 1e-12, f"statsmodels and scipy disagree by {worst:.3e}"
    return lo, hi, worst


def _w(label: str, k: int, n: int) -> str:
    lo, hi, worst = wilson(k, n)
    return (f"  {label} : [{100*lo:.4f}%, {100*hi:.4f}%]   (statsmodels, scipy "
            f"closed form and mpmath at 30 dp agree to {worst:.2e})")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ids", action="store_true", help="list the entry ids and exit")
    args = ap.parse_args()

    bad, real = overclaiming()
    never = sorted(done_ids() - real)
    if args.ids:
        print(" ".join(sorted(bad)))
        return 0
    k, n = len(bad), len(real)
    print(f"DONE entries that claim more than their evidence shows")
    print(f"  {k} of {n} = {100*k/n:.4f}%")
    print(_w("Wilson 95%", k, n))
    print(f"  ids: {' '.join(sorted(bad))}")
    # DISCLOSED, NEVER SILENTLY DROPPED. A reader must be able to see that the
    # denominator is the audited population and which entries are outside it.
    print(f"  DONE but never audited (excluded from the denominator): "
          f"{' '.join(never) if never else 'none'}")

    # EVERY FIGURE THE README STATES, DERIVED HERE. Until 2026-09-17 this
    # producer emitted the combined figure alone, so 9 of the README's 12
    # figures were prose with no code behind them -- including round 1's
    # headline, which is the one most readers meet first.
    r2_ids = _round2_ids()
    r1_bad, r1_real = sorted(bad - r2_ids), sorted(real - r2_ids)
    k1, n1 = len(r1_bad), len(r1_real)
    cl1, ch1, cw1 = clopper_pearson(k1, n1)
    print(f"\nROUND 1 ALONE, the figure the README states first")
    print(f"  {k1} of {n1} = {100*k1/n1:.4f}%")
    print(_w("Wilson 95%", k1, n1))
    print(f"  Clopper-Pearson 95% : [{100*cl1:.4f}%, {100*ch1:.4f}%]   "
          f"(statsmodels and scipy beta quantiles agree to {cw1:.2e})")

    # THE AUDITED POPULATION, NOT TODAY'S DONE COUNT. A11 closed after the
    # audit ran, so `done_ids()` is 85 now and was 84 then -- using it here
    # would restate a coverage figure against a population the auditors never
    # saw. This is the same wrong-denominator defect the panel caught in the
    # combined figure above, which is why both now read from `real`.
    print(f"\nROUND 1 COVERAGE of the {n} entries the audit examined")
    print(f"  {n1} of {n} = {100*n1/n:.4f}%")
    print(f"  (DONE today is {len(done_ids())}: {' '.join(never)} closed after "
          f"the audit and is outside every figure above)")

    # THE SUPERSEDED FIGURE, REPRODUCED SO THE CORRECTION IS CHECKABLE.
    # A note that says "SUPERSEDES 30 of 84" states 2 numbers, and the wrong
    # one needs a producer exactly as much as the right one -- otherwise a
    # reader cannot verify that the correction was a correction.
    k_old = len(bad) - 1          # the typed round-2 tuple omitted 7.3
    print(f"\nSUPERSEDED, retained so the correction can be checked")
    print(f"  {k_old} of {n} = {100*k_old/n:.4f}%  "
          f"(round 2 was a hand-typed tuple of 6 against an adjudication "
          f"marking 7; it omitted 7.3)")
    print(_w("Wilson 95%", k_old, n))
    assert "7.3" in bad, "7.3 is no longer among the upheld; this note is stale"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
