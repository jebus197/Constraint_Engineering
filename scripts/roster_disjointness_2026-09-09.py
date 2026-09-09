#!/usr/bin/env python3
"""How many archived runs would the first _declared_models have silently gagged?

MEASURED, and committed alongside the figures it produces
(`measured-rate-travels-with-its-script`).

The first version of `_declared_models` treated a NON-EMPTY `cfg.models` as an
arm's declaration and returned the empty list when nothing in the orchestrator
roster matched it. `RunnerConfig.models` defaults to a hardcoded 5 vendor labels,
so any run whose dispatched roster used a different vocabulary -- simulated seats
labelled SIM-A..E, say -- would have had routing and the post-convergence sweep
reduced to nobody, silently.

This walks the archived run reports, reads the panel actually dispatched, and
counts how many carry NO label matching the hardcoded default after -SIM
normalisation. Those are the runs the defect would have gagged.
"""
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

DEFAULT = ["CC2", "Codex", "Gemini", "DeepSeek", "ChatGPT"]


def base(label):
    label = str(label or "")
    return label[:-4] if label.endswith("-SIM") else label


def panels():
    """(run_name, dispatched_panel, source) for every archived run naming one.

    TWO INDEPENDENT SOURCES, because a single key could be written by one path
    and miss runs recorded by another. `*_report.json` carries a top-level
    `models` list; `runner_state.json` carries `raw_counts_per_model`, whose keys
    are the seats that actually produced findings. Where a run has both, they are
    compared and any disagreement is reported rather than silently preferred.
    """
    for report in sorted((REPO / "bench" / "logs").rglob("*_report.json")):
        try:
            d = json.loads(report.read_text())
        except Exception:
            continue
        if isinstance(d, dict) and isinstance(d.get("models"), list) and d["models"]:
            yield report.parent.name, [str(x) for x in d["models"]], "report"
    for state in sorted((REPO / "bench" / "logs").rglob("runner_state.json")):
        try:
            d = json.loads(state.read_text())
        except Exception:
            continue
        counts = (d or {}).get("raw_counts_per_model")
        if isinstance(counts, dict) and counts:
            yield state.parent.name, [str(k) for k in counts], "runner_state"


def main():
    want = {base(m) for m in DEFAULT}
    rows = list(panels())
    seen, srcs, disjoint, conflicts = {}, {}, [], []
    for name, panel, src in rows:
        if name in seen:
            if {base(x) for x in seen[name]} != {base(x) for x in panel}:
                conflicts.append((name, srcs[name], seen[name], src, panel))
            continue
        seen[name], srcs[name] = panel, src
        if not ({base(p) for p in panel} & want):
            disjoint.append((name, panel))
    print(f"panel records read                        : {len(rows)}")
    print(f"runs where the 2 sources disagree         : {len(conflicts)}")
    for c in conflicts[:5]:
        print(f"    {c[0]}: {c[1]}={sorted(c[2])} vs {c[3]}={sorted(c[4])}")

    n, k = len(seen), len(disjoint)
    print(f"archived runs naming a dispatched panel : {n}")
    print(f"panels DISJOINT from the hardcoded default: {k}")
    if not n:
        return
    p = k / n
    print(f"proportion                                : {p:.4f}")

    # TWO TOOLS, as the project requires for any computational claim.
    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(k, n, method="wilson")
    lo_c, hi_c = proportion_confint(k, n, method="beta")
    print(f"Wilson 95%          : [{lo_w*100:.1f}%, {hi_w*100:.1f}%]  (statsmodels)")
    print(f"Clopper-Pearson 95% : [{lo_c*100:.1f}%, {hi_c*100:.1f}%]  (statsmodels/beta)")

    from scipy.stats import beta as sbeta
    lo_s = 0.0 if k == 0 else sbeta.ppf(0.025, k, n - k + 1)
    hi_s = 1.0 if k == n else sbeta.ppf(0.975, k + 1, n - k)
    print(f"Clopper-Pearson 95% : [{lo_s*100:.1f}%, {hi_s*100:.1f}%]  (scipy, cross-check)")
    agree = abs(lo_s - lo_c) < 1e-9 and abs(hi_s - hi_c) < 1e-9
    print(f"the two tools agree to 1e-9               : {agree}")

    if disjoint:
        print("\nruns that would have been gagged:")
        for name, panel in disjoint[:15]:
            print(f"  {name:48s} {panel}")
        if len(disjoint) > 15:
            print(f"  ... and {len(disjoint)-15} more")


if __name__ == "__main__":
    main()
