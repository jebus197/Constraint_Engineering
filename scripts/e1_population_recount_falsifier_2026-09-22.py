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

tot = Counter()
for f in sorted(glob.glob(str(REPO / "bench/logs/commissioning_*/runner_state.json"))):
    doc = json.load(open(f))
    def walk(x):
        if isinstance(x, dict):
            v = x.get("fix_efficacy")
            if isinstance(v, dict) and "outcome" in v:
                tot[v["outcome"]] += 1
            for y in x.values():
                walk(y)
        elif isinstance(x, list):
            for y in x:
                walk(y)
    walk(doc)

n = sum(tot.values())
k = tot.get("FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER", 0)
print(f"distinct probe records: {n}; non-curing: {k}")
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
