#!/usr/bin/env python3
"""Panel review: can two defects at the same location be told apart reliably?

FOUNDER RULING 1, 2026-08-03. Verbatim:

    "if a reasonable solution exists there is no reason why we cannot research
    it, build it and test it... traditionally this is why the panel review
    process exists. Whenever we have encountered a deadlock in the past and you
    didn't know exactly what to do about it, we have turned to the panel...
    given everything we have, including the full CDSFL schema, all our tools,
    all the mechanics we have built, our mathematical model, and all the current
    research that exists, is there genuinely no way to resolve this? No way to
    reliably tell if one defect or issue is meaningfully different from another?"

WHY THIS IS BEING ASKED RATHER THAN DECIDED
-------------------------------------------
CC1 previously reported the problem as unresolvable. That was an overstatement,
and the founder caught it: what was actually refuted was TWO CHEAP
APPROXIMATIONS, not the problem itself.

The panel gets the measurements, not the conclusion. Both approaches and both
failure modes are stated so a model can attack the measurement rather than
inherit a verdict.

RUN WITHOUT COMPELLED CONVERGENCE (`pr` semantics): each model returns its own
verdict and its strongest falsification of the others' likely positions.
Disagreement is preserved as information. CC1 participates with its own position
and synthesises the range; it does not arbitrate.

    python3 bench/confer_semantic_distinctness_pr_2026-08-04.py --dry-run
    python3 bench/confer_semantic_distinctness_pr_2026-08-04.py            # dispatches
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
OUT = REPO / "bench/logs/pr_semantic_distinctness_2026-08-04"


def load_env() -> None:
    """experiment_11_orchestrator sources .env only under __main__."""
    env = REPO / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        m = re.match(r"\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.+)", line)
        if m:
            os.environ.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))


QUESTION = """
THE PROBLEM, STATED PRECISELY

CDSFL is an LLM-reliability research harness for STEM. A panel of five frontier
models reviews a target artefact over successive rounds; the run stops when the
decay curve has flattened AND K consecutive rounds produce no new critical
finding. (Both sides of that gate are required. The decay curve, gamma, is
load-bearing and is NOT under discussion here.)

"New" is currently decided by LOCATION. Each finding is keyed to a symbol in the
target — a function, a named claim, a heading. If the panel finds a SECOND,
genuinely different critical defect at a location it has already flagged, the
system does not count it as new.

So the honest description of the current stopping rule is: K consecutive rounds
with no new critical finding AT A PREVIOUSLY UNMENTIONED LOCATION. That is
narrower than "no new critical finding", which is what a reader assumes.

WHY LOCATION KEYING EXISTS (it is not an oversight)

Before it, novelty was decided by the finding ID the model chose. Models relabel
the same defect every round. Measured on Exp 42: the late rounds showed "4 new
criticals" three rounds running, and those were ~4 REAL defects being re-found
and relabelled each round. The three-zero streak could never form. The system had
substantively converged by round 5 and could not recognise it. Location keying
fixed that and unblocked the arc. It is a trade, not a mistake.

WHAT WAS TRIED, AND THE MEASUREMENTS THAT KILLED IT

Approach 1 — semantic similarity via sentence embeddings. Two findings are the
same defect if cosine similarity exceeds a threshold.
  MEASURED: on the two hand-built test cases (two genuinely DIFFERENT defects at
  one location), similarity scored 0.684 and 0.781 against a threshold of 0.55.
  Both were declared repeats. The method asserts identity where a human sees two
  different problems. Raising the threshold to separate them puts it above the
  similarity of genuine re-finds, which is the failure it exists to prevent.

Approach 2 — lexical overlap (Jaccard on token sets).
  MEASURED: correctly separated both test cases (0.081 and 0.152). But replayed
  against six COMPLETED runs, it destroyed convergence in all six: ordinary
  rewording between rounds reads as a brand-new defect, so the streak never
  forms and the run never stops.

Also considered and rejected before measurement: hashing the proposed fix (too
fine — two fixes for one defect differ), and overlap of the fix target (too
coarse — one function, many defects). Comparing falsifier code was judged
intractable.

WHAT THE PROJECT HAS AVAILABLE

Five frontier models per round with a runnable-falsifier discipline: a critical
is only resolved by a demonstration the runner re-executes itself. A full local
STEM tool envelope (SymPy, z3, SciPy, statsmodels, mpmath, pint, NumPy, rdkit,
biopython, networkx, crosshair, AST/dis/inspect, and Wolfram for
cross-verification). A mathematical model of convergence with a two-sided gate.
Per-finding metadata: severity, flaw class, abstraction index, proposed fix,
falsifier code and its verdict, source model, round of first appearance, and the
location key itself. Roughly 274 archived real findings across Exp 45-53 to
calibrate or falsify any proposal against.

THE QUESTION

1. Is there a reliable way to decide whether two findings at the SAME location
   are the same defect or two different defects? Reliable means: it separates the
   two known test cases AND does not destroy convergence when replayed against
   the six completed runs. Both, not either.

2. If you propose a method, state exactly how it would be FALSIFIED, and what
   data already in the archive would falsify it.

3. Consider specifically whether the FALSIFIER — a runnable test that the runner
   executes — is a better identity signal than the finding's prose. Two findings
   are arguably the same defect if and only if a demonstration of one also
   demonstrates the other. Is that decidable in practice? What does it cost?

4. If you believe no reliable method exists with current technology, say so
   plainly and give your strongest argument, including whether the honest
   fallback — leave the rule as it is and state the limitation in the paper — is
   defensible for a research release.

Answer in your own voice. Do not converge on the others. Give your verdict, your
reasoning, and your single strongest falsification of the position you expect
the other models to take.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    load_env()
    from bench.experiment_11_orchestrator import load_default_config
    from bench.launcher_core import load_cdsfl_directive
    from bench.reference_runner_v2 import dispatch_to_model

    cfg = load_default_config()
    directive = load_cdsfl_directive()
    system = directive + (
        "\n\nYou are participating in a PANEL REVIEW under `pr` semantics: no "
        "compelled convergence. Disagreement is preserved as information. Do not "
        "soften your position to match the others.")

    print(f"  panel   : {[m.label for m in cfg.models]}")
    print(f"  prompt  : {len(QUESTION)} chars   system: {len(system)} chars")
    if args.dry_run:
        print("  DRY RUN — nothing dispatched.")
        return 0

    OUT.mkdir(parents=True, exist_ok=True)
    results = {}
    for mc in cfg.models:
        t0 = time.monotonic()
        print(f"  -> {mc.label} ...", flush=True)
        try:
            resp, meta = dispatch_to_model(mc, QUESTION, system)
        except Exception as e:  # noqa: BLE001 — one model must not take the panel down
            resp, meta = f"[DISPATCH FAILED] {type(e).__name__}: {e}", {}
        el = time.monotonic() - t0
        results[mc.label] = {"response": resp, "meta": meta, "elapsed_s": round(el, 1)}
        (OUT / f"{mc.label}.json").write_text(
            json.dumps(results[mc.label], indent=2), encoding="utf-8")
        print(f"     {mc.label}: {len(resp)} chars in {el:.0f}s", flush=True)

    (OUT / "_all.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n  written to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
