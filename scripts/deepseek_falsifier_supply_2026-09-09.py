#!/usr/bin/env python3
"""Task 3.2: does DeepSeek's denied tool use actually starve falsifier supply?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

THE RULING, verbatim: *"Why does DeepSeek get a free pass on tool use? ... No
tool use is an unacceptable condition in the CDSFL schema, when an item exists
that is genuinely computable. Verdict, fix DeepSeek and test it."*

WHAT THE CODE ACTUALLY DOES. `bench/experiment_11_orchestrator.py:1442` sets
`tools = None` for this route unconditionally, with a comment dated 2026-06-06
recording why: DeepSeek-v4-pro's OpenAI tool-translation leaks tool calls as DSML
markup, so the tool loop returns exploration code rather than findings. It is a
documented MITIGATION with a compensator -- `_falsifier_format_repair` re-prompts
once so prose-style falsifiers become runnable blocks the runner re-runs.

THE OUTCOME THE SCHEMA REQUIRES is a falsifier the runner can execute, not a tool
call. This measures that outcome per seat across the archive.

RESULT: the concern is REFUTED for DeepSeek specifically. It supplies a runnable
falsifier in 103 of 468 archived replies, 22.01%, against 325 of 1925 for every
other seat pooled -- Fisher exact p = 0.0106, odds ratio 1.389, 95% CI
[1.083, 1.782], scipy and statsmodels agreeing. DeepSeek is significantly MORE
likely to supply one, not less.

TWO THINGS THIS DOES NOT SHOW, stated so they are not read into it. The ordering
is not simply tools-versus-no-tools: Gemini is tool-enabled and higher still at
25.54%. And the absolute rates are low for every seat, 12% to 35%, which is a
larger question than the one this script was written to answer.

THE INSTRUMENT WAS WRONG FIRST TIME. `extract_falsifiers` returns a
`(by_key, ordered)` tuple, and a first version took `len()` of the tuple -- so
every seat scored 100%, including on empty text. Checked by feeding it an empty
string before any figure was believed.
"""
import json, pathlib, re, collections, sys
# THE REPOSITORY THIS FILE IS IN. See the note in
# absorb_rule_disagreement_2026-09-05.py: an absolute path to the maintainer's
# checkout makes a clone-only defect invisible, because the script measures
# the maintainer's tree wherever it is launched from.
REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO/"bench"))

if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)

from bench.runner_core import extract_falsifiers

per_model = collections.Counter(); with_fals = collections.Counter()
for rd in sorted((REPO/"bench"/"logs").rglob("round_*.json")):
    try: d = json.loads(rd.read_text())
    except Exception: continue
    resp = d.get("responses") or d.get("model_responses") or {}
    if not isinstance(resp, dict): continue
    for label, text in resp.items():
        if not isinstance(text, str) or not text.strip(): continue
        base = label[:-4] if label.endswith("-SIM") else label
        per_model[base] += 1
        try: _bk, _ordered = extract_falsifiers(text); n = len(_ordered)
        except Exception: n = 0
        if n: with_fals[base] += 1

print(f"{'seat':12s} {'replies':>8s} {'with falsifier':>15s} {'rate':>8s}   95% CI (Wilson)")
from statsmodels.stats.proportion import proportion_confint
rows = []
for m, n in per_model.most_common():
    k = with_fals[m]
    lo, hi = proportion_confint(k, n, method="wilson") if n else (0, 0)
    rows.append((m, n, k, k/n if n else 0, lo, hi))
    print(f"{m:12s} {n:8d} {k:15d} {k/n if n else 0:8.4f}   [{lo*100:5.1f}%, {hi*100:5.1f}%]")

ds = [r for r in rows if r[0] == "DeepSeek"]
others = [r for r in rows if r[0] != "DeepSeek" and r[1] >= 10]
if ds and others:
    import numpy as np
    from scipy.stats import fisher_exact
    d = ds[0]
    ok = sum(r[2] for r in others); tot = sum(r[1] for r in others)
    table = [[d[2], d[1]-d[2]], [ok, tot-ok]]
    odds, p = fisher_exact(table)
    print(f"\nDeepSeek {d[2]}/{d[1]} vs every other seat {ok}/{tot}")
    print(f"Fisher exact p = {p:.6g}, odds ratio = {odds:.4f}   (scipy)")
    from statsmodels.stats.contingency_tables import Table2x2
    t = Table2x2(np.array(table))
    print(f"odds ratio {t.oddsratio:.4f}, 95% CI {t.oddsratio_confint()}   (statsmodels cross-check)")
