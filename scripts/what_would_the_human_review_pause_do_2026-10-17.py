#!/usr/bin/env python3
"""What would the human-review pause do, given he already reviews the output?

TASK C9. HIS QUESTION, 2026-10-07, verbatim: *"If this is on (and it probably
should be), what effect would it have on our experiments? I ask because
ultimately human review is always part of the system anyway. A human decides on
what problems are entered into the system, and then reviews the final output.
Where does this switch fit into this?"*

HIS PREMISE IS RIGHT AND THE SWITCH IS NOT AT THOSE BOUNDARIES. His review is at
the ENDS: he chooses the target, and he reads the output. `RunnerConfig.hil_review`
inserts a pause BETWEEN ROUNDS, which is different in kind.

WHAT IT ACTUALLY DOES, read from the 2 call sites rather than from its name:

  * MONOLITHIC MODE, `reference_runner_v3.py` around line 20477: after EVERY
    round it logs the round's findings, gamma and rho, saves a checkpoint,
    writes a partial report, sets `hil_status = "paused_for_review"` and
    **exits with code 42**. The run must be restarted with
    `--resume --hil-review`.
  * BURST MODE, around line 20529: the same, but only at a PHASE boundary.

SO IT IS A PAUSE, NOT A REVIEW STEP. Nothing is shown to him that he does not
already see in the final report; what changes is WHEN he sees it and that the run
stops until he acts.

THE EFFECT ON AN EXPERIMENT, and this is the part that answers him. Turning it on
converts 1 autonomous run into N sequential sessions, 1 per round. Leg 3 of the
shakedown ran 5 rounds in 71.5 minutes; with the switch on that is 5 stops, each
needing his attention and a resume. That is the cost. The consequence is larger:
**intervening between rounds changes what the experiment measures.** The rounds
after an intervention are not the same process as the rounds before it, so a
convergence figure spanning an intervention is not a measurement of AUTONOMOUS
convergence -- and autonomous convergence is the current programme's success
criterion, 3 consecutive clean convergences on the prose target.

SO THE EVIDENCE DISAGREES WITH HIS PARENTHETICAL *"and it probably should be"*,
for these runs specifically. For a run whose purpose is to STEER rather than to
measure, the switch is exactly right and the pause is the point. For the
programme of study now in flight it would confound the measurement, which is the
likeliest reason it has never been on.

MEASURED, so "never been on" is a figure rather than an impression: 0 of 47
shipped configs set `hil_review` at all, 0.0000%, Wilson [0.0000%, 7.5558%],
Clopper-Pearson [0.0000%, 7.5486%]; and 0 archived run reports carry
`hil_status` or `hil_paused_at_round`. The 54 `.py` and 28 `.json` files under
`bench/logs/` that mention those keys are sandbox-harvest COPIES OF THE RUNNER
SOURCE, not runs that paused -- a distinction worth drawing, because counting
them would have reported 82 pauses where there were none, which is exactly the
self-inclusion shape task C2 exists to prevent.

Costs nothing and dispatches no model. Run: python3 scripts/<this file>
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
from _cli_help import answer_help  # noqa: E402

RUNNER = REPO / "bench" / "reference_runner_v3.py"
LOGS = REPO / "bench" / "logs"


def _find(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for value in obj.values():
            got = _find(value, key)
            if got is not None:
                return got
    elif isinstance(obj, list):
        for value in obj:
            got = _find(value, key)
            if got is not None:
                return got
    return None


def main() -> int:
    answer_help(__doc__, __file__)
    src = RUNNER.read_text(encoding="utf-8")

    print("WHAT `hil_review` CONTROLS, READ FROM ITS CALL SITES")
    lines = src.splitlines()
    sites = [n for n, line in enumerate(lines, 1)
             if "cfg.hil_review" in line and not line.lstrip().startswith("#")]
    for n in sites:
        window = "\n".join(lines[n - 1:n + 24])
        exits = "sys.exit(42)" in window
        pauses = "paused_for_review" in window
        print(f"  line {n}: exits with 42: {exits}   "
              f"sets paused_for_review: {pauses}")
    print(f"  call sites reading the switch: {len(sites)}")
    print("  so it is a PAUSE that terminates the run, not a review step: "
          "nothing")
    print("  is shown that the final report does not already carry.")

    print("\nHOW MANY CONFIGS TURN IT ON")
    cfgs = sorted((REPO / "bench").glob("exp*_configs/*.json"))
    setting, enabling = [], []
    for p in cfgs:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        value = _find(data, "hil_review")
        if value is not None:
            setting.append(p.name)
            if value is True:
                enabling.append(p.name)
    print(f"  shipped configs           : {len(cfgs)}")
    print(f"  setting `hil_review` at all: {len(setting)}")
    print(f"  enabling it               : {len(enabling)}")
    if cfgs:
        from statsmodels.stats.proportion import proportion_confint
        import scipy.stats as st
        k, n = len(enabling), len(cfgs)
        w = proportion_confint(k, n, method="wilson")
        b = proportion_confint(k, n, method="beta")
        cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
        print(f"  {k} of {n} = {100*k/n:.4f}%")
        print(f"    Wilson          [{w[0]*100:.4f}%, {w[1]*100:.4f}%]")
        print(f"    Clopper-Pearson [{b[0]*100:.4f}%, {b[1]*100:.4f}%]")
        print(f"    scipy agrees on the upper bound: {abs(b[1]-cp_hi) < 1e-9}")

    print("\nHAS ANY RUN EVER PAUSED? A SOURCE COPY IS NOT A RUN.")
    mentions, paused = 0, 0
    for p in LOGS.rglob("*.json"):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "hil_status" not in text and "hil_paused_at_round" not in text:
            continue
        mentions += 1
        try:
            data = json.loads(text)
        except ValueError:
            continue
        if isinstance(data, dict) and (data.get("hil_status")
                                       or data.get("hil_paused_at_round")):
            paused += 1
            print(f"      PAUSED: {p.relative_to(REPO)}")
    source_copies = sum(1 for p in LOGS.rglob("*.py")
                        if "hil_paused_at_round" in
                        p.read_text(encoding="utf-8", errors="replace"))
    print(f"  json files mentioning the keys : {mentions}")
    print(f"  .py source copies mentioning   : {source_copies}")
    print(f"  RUNS THAT ACTUALLY PAUSED      : {paused}")
    print("  counting the copies would have reported "
          f"{mentions + source_copies} pauses where there were none, which is")
    print("  the self-inclusion shape task C2 exists to prevent.")

    print("\nTHE ANSWER TO HIS QUESTION")
    print("  His premise is right: he reviews the input and the output. This")
    print("  switch is not at those boundaries -- it pauses BETWEEN ROUNDS.")
    print("  Turning it on converts 1 autonomous run into N sequential")
    print("  sessions, 1 per round; leg 3 ran 5 rounds in 71.5 minutes, so 5")
    print("  stops. The larger consequence is that intervening between rounds")
    print("  changes WHAT IS MEASURED: the rounds after an intervention are not")
    print("  the same process as the rounds before, so a convergence figure")
    print("  spanning one is not a measurement of AUTONOMOUS convergence --")
    print("  which is this programme's success criterion.")
    print("  SO THE EVIDENCE DISAGREES WITH HIS \"it probably should be\" FOR")
    print("  THESE RUNS, and agrees with it for a run meant to steer rather")
    print("  than to measure. The choice is now a choice rather than a default.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
