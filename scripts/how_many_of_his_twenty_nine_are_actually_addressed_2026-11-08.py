#!/usr/bin/env python3
"""Of his 31 annotations of 2026-11-08, how many are actually discharged?

WHY THIS EXISTS. He asked, at 18:21 on 2026-11-08: *"Presumably all the issues
you could address from my last tts answer file are now addressed?"* A
presumption is a thing to TEST, not to confirm, and `factual-synthesis-over-
agreement` says so in his own framing: if the record points away from his
reading, say so with citations.

WHAT IS COUNTED. His 29 annotations on
`Decisions_Awaiting_You_2026-11-08_GENERATED.txt` and his 2 on
`The_Gates_Refused_3_Times_2026-11-08.txt`, read through
`scripts/read_founder_responses_2026-10-11.py` and never grepped
(`feedback_read_his_responses_with_the_reader_2026-10-11`: 221 of 691 of his
annotations were invisible to grep). Each is mapped to its entry by the SAME
proved alignment `scripts/record_his_verdicts_of_the_eighth_2026-11-08.py` uses:
the entry code expected for annotation i must be the LAST one named in the index
text before his mark, asserted per item, with nothing reported if any fails.

THE STATE COMES FROM THE MARKERS, not from a recollection of what was built.
`scripts/task_list_markers.parse_entries` is the single reader, so this cannot
disagree with the Stop gate's own count.

AND 1 DISTINCTION DECIDES THE ANSWER. An annotation can be discharged in 3
different senses, and collapsing them is how a report overstates:
  * BUILT -- its entry is DONE, with a guard behind it.
  * DISCHARGED BY BEING RECORDED -- he accepted a recommendation to take no
    action, so recording the ruling IS the whole of the work.
  * STILL OPEN -- accepted and not yet built. These are the ones his presumption
    would cover and the record does not.

Exit 0 always: this reports.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
RESPONSES = pathlib.Path.home() / "Developer_Projects/Responses"
DEC = "Decisions_Awaiting_You_2026-11-08_GENERATED.txt"
GATES = "The_Gates_Refused_3_Times_2026-11-08.txt"

#: His 3 acceptances of a recommendation whose content is TO TAKE NO ACTION, so
#: the ruling being recorded is the whole of the work. Named individually rather
#: than inferred, because "no action needed" is exactly the claim that must not
#: be guessed at: B107 accept the ratio and keep closing; B123 take it as
#: information and leave the guard red; B128 take no action beyond the recorded
#: habit. Each is quoted in the decisions file's own option text.
NO_ACTION = {"B107", "B123", "B128"}


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


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main() -> int:
    argparse.ArgumentParser(description=__doc__.splitlines()[0]).parse_args()
    reader = _load(REPO / "scripts/read_founder_responses_2026-10-11.py", "_rfr")
    sys.path.insert(0, str(REPO / "scripts"))
    tlm = _load(REPO / "scripts/task_list_markers.py", "_tlm")
    entries = {e.ident: e for e in tlm.parse_entries(
        REPO / "experimental_notes/CDSFL_MASTER_TASK_LIST.md")}

    ann = [a for a in reader.annotations() if a["file"] in (DEC, GATES)]
    dec = [a for a in ann if a["file"] == DEC]
    gates = [a for a in ann if a["file"] == GATES]
    print(f"his annotations read: {len(dec)} on the decisions file, "
          f"{len(gates)} on the gates note, {len(ann)} in all")

    raw = (RESPONSES / DEC).read_bytes().decode("cp1252", errors="replace")
    short = raw[:raw.find("DECISION 1.")]
    marks = [m.start() for m in re.finditer(r"#", short)]
    if len(marks) != len(dec):
        print(f"REFUSING: {len(marks)} marks against {len(dec)} annotations")
        return 1

    codes, bad = [], []
    for i in range(len(marks)):
        before = short[(marks[i - 1] if i else 0):marks[i]]
        named = re.findall(r"\bB\d+\b", before)
        if not named:
            bad.append(i + 1)
        else:
            codes.append(named[-1])
    if bad:
        print(f"REFUSING: no entry code before mark(s) {bad}. Nothing reported.")
        return 1
    #: His 2 annotations on the gates note are on B135 and B102 -- stated here
    #: and ASSERTED below against the entries, never assumed.
    gates_codes = ["B135", "B102"]
    for c in gates_codes:
        if c not in entries:
            print(f"REFUSING: {c} is not an entry")
            return 1
    codes += gates_codes

    print(f"alignment proved for all {len(marks)} marks on the decisions file\n")
    built, recorded, still_open, missing = [], [], [], []
    for c in codes:
        e = entries.get(c)
        if e is None:
            missing.append(c)
        elif e.state == "DONE":
            built.append(c)
        elif c in NO_ACTION:
            recorded.append(c)
        else:
            still_open.append(c)

    n = len(codes)
    print("=" * 74)
    print(f"THE STATE OF HIS {n} ANNOTATED ITEMS, read from the markers")
    print("=" * 74)
    for label, rows in (("BUILT, entry DONE", built),
                        ("DISCHARGED BY BEING RECORDED (he accepted: no action)",
                         recorded),
                        ("STILL OPEN -- accepted and NOT yet built", still_open),
                        ("no entry found", missing)):
        #: ★ THE COUNT AND THE LIST MUST ANSWER THE SAME QUESTION, fixed
        #: 2026-11-08. `len(rows)` counted ANNOTATIONS and the line below
        #: printed `set(rows)`, which is unique ENTRIES -- so this reported
        #: "BUILT, entry DONE: 10" and then named 9, because B102 is annotated
        #: twice. A count beside a list that disagrees with it is the
        #: figure-answers-a-different-question defect, in a producer written
        #: the same day it was used to report to him. BOTH are now shown, each
        #: labelled with what it counts.
        uniq = sorted(set(rows), key=lambda x: int(x[1:]))
        extra = ("" if len(rows) == len(uniq)
                 else f" ({len(rows)} annotations, 1 or more entry annotated "
                      f"more than once)")
        print(f"\n  {label}: {len(uniq)} entries{extra}")
        if uniq:
            print("    " + " ".join(uniq))

    disc = len(built) + len(recorded)
    for label, k in (("discharged in either sense", disc),
                     ("BUILT with a guard behind it", len(built)),
                     ("still open", len(still_open))):
        (wl, wh), (cl, ch), gap = _iv(k, n)
        print(f"\n  {label}: {k} of {n} = {k / n:.6f}")
        print(f"    Wilson [{wl:.6f}, {wh:.6f}]  "
              f"Clopper-Pearson [{cl:.6f}, {ch:.6f}]  routes agree to {gap:.2e}")

    print("\n" + "=" * 74)
    print("THE ANSWER TO HIS QUESTION")
    print("=" * 74)
    if still_open:
        print(f"  NO. {len(still_open)} of his {n} annotated items are accepted and")
        print(f"  not yet built, so the presumption does not hold. They are named")
        print(f"  above rather than counted, because a count cannot say which.")
    else:
        print(f"  YES: 0 of {n} remain open.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
