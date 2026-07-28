"""Smoke test (founder-approved 2026-07-28): run the post-convergence sweep
machinery — the exact code path Exp 46 will use — against the REAL Exp 45
registry, with the REAL 5-model panel doing the clearing and the runner's
reverify_falsifier as the sole judge. Hypothesis under test: with the
mechanical/ghost-issue machinery fixed, ordinary sub-critical residuals are
panel-clearable. The original run record is not modified; results are written
alongside it."""

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "bench"))

from bench import launcher_core  # noqa: E402

launcher_core.load_env_file()

from bench.reference_runner_v2 import (  # noqa: E402
    FindingRegistry, RunnerConfig, _post_convergence_sweep,
)

RUN = sorted((REPO / "bench" / "logs").glob(
    "exp45_memory_statistics_live_*"))[-1]
state = json.loads((RUN / "runner_state.json").read_text())
registry = FindingRegistry.from_dict(state["registry"])

_TERMINAL = {"MERGED", "CLOSED", "REFUTED", "DUPLICATE", "CONFIRMED"}
before = {cid: dict(e) for cid, e in registry.entries.items()
          if e["status"] not in _TERMINAL}
print(f"Residuals entering sweep: {sorted(before)}")

cfg = RunnerConfig(
    test_article="bench/dm/_memory.py",
    post_convergence_sweep_rounds=2,
    experiment_name="exp45_sweep_smoketest",
)
exp_config = launcher_core.load_experiment_config()

stats = _post_convergence_sweep(registry, exp_config, cfg, round_idx=4)

outcome = {
    "stats": stats,
    "per_item": {
        cid: {
            "before": before[cid]["status"],
            "after": registry.entries[cid]["status"],
            "resolved_by_sweep": registry.entries[cid].get("resolved_by_sweep"),
            "withdrawn_by_sweep": registry.entries[cid].get("withdrawn_by_sweep"),
            "withdraw_reason": registry.entries[cid].get("withdraw_reason"),
            "falsifier_verdict": registry.entries[cid].get("falsifier_verdict"),
        }
        for cid in sorted(before)
    },
}
out = RUN / "sweep_smoketest_20260728.json"
out.write_text(json.dumps(outcome, indent=2, default=str))
print(json.dumps(outcome, indent=2, default=str))
print(f"\nSaved: {out}")
