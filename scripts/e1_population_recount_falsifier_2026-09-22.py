#!/usr/bin/env python3
"""FALSIFIER: the e1 probe population is 124 distinct records, not 248.

Every commissioning run stores each scored entry's `fix_efficacy` dict in BOTH
`runner_state.json` and the run's `*_report.json` (arm 4 adds a third copy in
`experiment_chain.json`). A glob matching more than `runner_state.json`
therefore counts each record at least twice: 124 distinct records become 248,
23 non-curing become 46, and the Wilson interval narrows from
[12.69%, 26.30%] to [14.20%, 23.85%] with no new information.

This script recounts the DISTINCT population (runner_state.json only, one per
run) and asserts that scripts/e1_mechanism_consequences_2026-09-22.py's
docstring states that population rather than the doubled one.

Exit 1 while the docstring claims 248; exit 0 once it states 124/23.

SCOPED 2026-10-01. This file took the first clean full-suite run red with no
defect present. Its recount globbed every `commissioning_*` run, so once the
2026-09-29/30 arms landed it measured 265 records and 50 non-curing and demanded
the consequences docstring state those instead of 124/23. But that docstring
names its own population -- "the 4 commissioning arms of 2026-09-21/22" -- and
is a DATED measurement, so satisfying the assertion would have overwritten a
correct record with a later figure. The recount is now scoped to the runs the
claim names, and the whole-archive figure is PRINTED alongside rather than
asserted on. Per-run arithmetic, sympy and mpmath agreeing: claim scope
69+9+30+16 = 124 and 16+3+2+2 = 23; later arms 42+58+10+17+14 = 141 and
12+8+3+4+0 = 27; whole archive 265 and 50.

Run:  python3 scripts/e1_population_recount_falsifier_2026-09-22.py
"""
import glob
import json
import sys
from collections import Counter
from pathlib import Path

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
# Placed after the HEADER imports, not the last import: this file has a
# late import and the call landed after the work on the first attempt.
# `_cli_help` lives in scripts/. Locate it rather than assume a depth: the
# first version of this preamble inserted parents[1] (the repo ROOT) and so
# worked when the file was RUN (sys.path[0] is the script dir) and failed when
# it was IMPORTED, which is how 13 scripts stopped importing on 2026-09-24.
import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402
# GUARDED 2026-09-24 (CC1). At MODULE level this read the HOST's argv:
# the operational-script probe imports via `python3 -c "..." <path>`, so
# sys.argv[1] was the script's own path and the guard refused it, exit 2.
# `__name__` is still "__main__" when the file is RUN, so `--help` answers
# exactly as before; on IMPORT it is skipped and argv is never inspected.
if __name__ == "__main__":
    answer_help(__doc__, __file__)
REPO = Path(__file__).resolve().parents[1]

# THE CLAIM IS DATED, SO THE RECOUNT MUST BE TOO. Scoped 2026-10-01 after this
# file took the clean suite red without any defect being present.
#
# The claim under test is the consequences script's "Across the 4 commissioning
# arms of 2026-09-21/22, 124 proposed fixes carry a fix-efficacy probe result.
# 23 of them are FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER". That sentence NAMES its
# population. This recount globbed `commissioning_*` instead, so when the
# 2026-09-29/30 arms landed it counted 265 records and 50 non-curing and
# demanded the docstring state THOSE -- which would have overwritten a dated
# measurement with a later one and destroyed the record
# `measured-rate-travels-with-its-script` exists to keep.
#
# Verified at the time of scoping, per-run, sympy and mpmath agreeing:
#   claim scope  69+9+30+16 = 124 records, 16+3+2+2 = 23 non-curing
#   later arms   42+58+10+17+14 = 141 records, 12+8+3+4+0 = 27 non-curing
#   whole archive                 265 records,              50 non-curing
# 23/124 = 18.5484%, Wilson [12.6898%, 26.2972%] -- the docstring's own figures
# to 4 decimal places. So the claim was never wrong; the denominator drifted.
#
# The DOUBLING defect this file was built to catch is unaffected: a run
# serialising each record twice still doubles the count WITHIN its own scope.
CLAIM_SCOPE = ("20260921", "20260922")


def _in_claim_scope(path: str) -> bool:
    """Does this run belong to the population the claim names?"""
    return any(stamp in Path(path).parent.name for stamp in CLAIM_SCOPE)


tot = Counter()
_all = Counter()
for f in sorted(glob.glob(str(REPO / "bench/logs/commissioning_*/runner_state.json"))):
    doc = json.load(open(f))
    sinks = (tot, _all) if _in_claim_scope(f) else (_all,)
    def walk(x):
        if isinstance(x, dict):
            v = x.get("fix_efficacy")
            if isinstance(v, dict) and "outcome" in v:
                for sink in sinks:
                    sink[v["outcome"]] += 1
            for y in x.values():
                walk(y)
        elif isinstance(x, list):
            for y in x:
                walk(y)
    walk(doc)

n = sum(tot.values())
k = tot.get("FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER", 0)
print(f"distinct probe records: {n}; non-curing: {k}   [claim scope: "
      f"{'/'.join(CLAIM_SCOPE)}]")

# REPORTED ALONGSIDE, NOT ASSERTED ON. The whole archive to date is the more
# interesting number for anyone pricing the mechanism today, and withholding it
# because it is not the asserted one would be its own silence.
n_all = sum(_all.values())
k_all = _all.get("FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER", 0)
print(f"whole archive to date:  {n_all}; non-curing: {k_all}   "
      f"[NOT asserted on -- later runs are outside the dated claim]")
from statsmodels.stats.proportion import proportion_confint

lo, hi = proportion_confint(k, n, method="wilson")
print(f"Wilson: [{100*lo:.4f}%, {100*hi:.4f}%]")

doc = (REPO / "scripts/e1_mechanism_consequences_2026-09-22.py").read_text()
head = doc.split('"""')[1]
# A LABELLED HISTORICAL MENTION IS NOT A LIVE CLAIM (same rule as the
# resume-pointer disclaimer tests of 2026-09-21): the docstring may RECORD
# that an earlier draft said 46 of 248, but must not STATE 248 as the
# population. The live-claim form is "248\nproposed fixes carry".
assert "248\nproposed fixes carry" not in head, (
    "FALSIFIED: the consequences script's docstring still claims the doubled "
    "population of 248 as live")
assert str(n) in head and str(k) in head, (
    f"docstring does not state the distinct population {k}/{n}")
print("clean exit: the docstring states the distinct population")
sys.exit(0)
