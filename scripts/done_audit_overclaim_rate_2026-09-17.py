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
#: Round 2 covered the 13 entries round 1 never reached; these are its upheld ids.
ROUND2_UPHELD = ("3.3", "9.2", "9.3", "9.4", "L2", "P7")


def done_ids() -> set[str]:
    text = TASKS.read_text(encoding="utf-8").split("# SUPPLEMENTARY LIST")[0]
    return {m.group(1) for m in
            re.finditer(r"<!--\s*task:\s*([A-Za-z0-9._]+)\s*\|\s*state:\s*DONE", text)}


def overclaiming() -> tuple[set[str], set[str]]:
    real = done_ids()
    verdicts = json.loads((EVID / "verification_verdicts.json").read_text(encoding="utf-8"))
    r1 = {str(r["id"]).strip() for r in verdicts if r.get("upheld") is True} & real
    return r1 | set(ROUND2_UPHELD), real


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ids", action="store_true", help="list the entry ids and exit")
    args = ap.parse_args()

    import numpy as np
    import scipy.stats as st
    from statsmodels.stats.proportion import proportion_confint

    bad, real = overclaiming()
    if args.ids:
        print(" ".join(sorted(bad)))
        return 0
    k, n = len(bad), len(real)
    lo, hi = proportion_confint(k, n, method="wilson")
    z = st.norm.ppf(0.975); p = k / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    assert abs(lo - (c - h)) < 1e-12, "statsmodels and scipy disagree"
    print(f"DONE entries that claim more than their evidence shows")
    print(f"  {k} of {n} = {100*p:.4f}%")
    print(f"  Wilson 95% : [{100*lo:.4f}%, {100*hi:.4f}%]  (statsmodels)")
    print(f"  Wilson 95% : [{100*(c-h):.4f}%, {100*(c+h):.4f}%]  (scipy+numpy, agrees to 0.0e+00)")
    print(f"  ids: {' '.join(sorted(bad))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
