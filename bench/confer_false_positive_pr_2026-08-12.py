#!/usr/bin/env python3
"""Panel review: how do you tell a false positive from a true finding
deterministically, on an artefact that may contain nothing wrong?

FOUNDER APPROVAL, 2026-08-12. Verbatim, on the false-positive problem:

    "This is clearly very serious! In essence a document (or proof) that contains
    zero errors, can potentially [produce] many false positives, despite all of
    the machinery we have in place to fix this? ... Do you want to run a panel
    review to see how it could be dealt with best?"

And, as the binding constraint on any answer:

    "CDSFL is not a voting system. It is not a democracy. Everything we do must be
    able to be computed deterministically, and be subject to the same falsification
    machinery as everything else. Intelligence + full determinism was always the
    goal, not one or the other."

WHAT CHANGED BETWEEN APPROVAL AND DISPATCH — read this before answering
----------------------------------------------------------------------
The figure that motivated this review ("22 critical findings on a clean document")
did not survive checking. It was re-measured before this prompt was written and it
was wrong. The corrected measurements are in section 2. They are given as
measurements, not as a conclusion, and the panel is asked to attack them.

RUN WITHOUT COMPELLED CONVERGENCE (`pr` semantics): each model returns its own
verdict and its strongest falsification of the position it expects the others to
take. Disagreement is preserved as information rather than smoothed to consensus.
CC1 participates with its own position and synthesises the range; it does not
arbitrate.

    python3 bench/confer_false_positive_pr_2026-08-12.py --dry-run
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
OUT = REPO / "bench/logs/pr_false_positives_2026-08-12"


def load_env() -> None:
    """experiment_11_orchestrator sources .env only under __main__."""
    env = REPO / ".env"
    if not env.exists():
        return
    for line in env.read_text().splitlines():
        m = re.match(r"\s*(?:export\s+)?([A-Z0-9_]+)\s*=\s*(.+)", line)
        if m:
            os.environ.setdefault(m.group(1), m.group(2).strip().strip('"').strip("'"))


QUESTION = r"""
# Telling a false positive from a true finding, deterministically

## 1. The system, in one paragraph

A five-model panel reviews a target document over successive rounds. Any finding
the panel rates critical must carry a RUNNABLE FALSIFIER: a small program written
to FAIL (raise AssertionError, or print FALSIFIED) if and only if the defect is
real. The runner re-executes that program itself. Only the runner's own execution
resolves anything — a model's prose verdict, however confident, resolves nothing.
This is called CONFIRM-only. A run stops when BOTH a decay-curve measure over
critical findings has flattened past a threshold AND K consecutive rounds produce
no new criticals.

## 2. The measurements, corrected 2026-08-12

A zero-plant control was built: a ~24 KB technical document whose claims are all
intended to be true, so that any critical finding against it is false by
construction. Two live five-model runs were made against it.

    Run A, 2026-07-29:  3 rounds parsed, 30 findings, 10 rated critical
    Run B, 2026-08-01:  4 rounds parsed, 55 findings, 29 rated critical

CORRECTIONS THAT MATTER TO YOUR ANSWER, all established by re-measurement today:

 (a) BOTH RUNS WERE INTERRUPTED. Neither produced a final report and neither wrote
     a registry. "Converged" is false with an empty reason on both. So the
     falsifier-verification stage's output does not exist for either run.

 (b) Run A ran against a REVISION OF THE CONTROL THAT WAS LATER REPAIRED — seven
     claims were corrected on 1 August. So an unknown share of Run A's 10 criticals
     may be TRUE findings. Run B ran against the post-repair document, whose
     content hash matches the published manifest exactly.

 (c) THE MODELS DID SUPPLY FALSIFIERS. Every model in every round emitted them
     (between 1 and 25 mentions per response). But no finding record in either
     run's structured output carries falsifier source, because — measured today —
     the field is declared on the finding type and was never serialised by the
     checkpoint writer, in any of the project's 56 archived runs across 8500+
     findings. That has been fixed today. It means the two control runs cannot
     tell us what the falsifiers would have decided.

So the honest position is: THE FALSE-POSITIVE RATE UNDER CONFIRM-ONLY HAS NEVER
ACTUALLY BEEN MEASURED ON THIS SYSTEM. What is measured is that a five-model panel
rates a substantial number of findings critical against a document believed clean,
BEFORE the falsifier stage adjudicates them.

## 3. The mechanism that was supposed to catch this, and why it is degenerate here

A discrimination control was built. For a finding accusing claim C, it takes the
CONFIRMED falsifier and re-runs it against a CORRECTED COPY of the target in which
C is repaired. The logic: a falsifier genuinely testing C should stop failing once C
is fixed. If it still fails, it was never testing C, and the finding is spurious.

ON A CLEAN DOCUMENT THIS COLLAPSES. If C is already true, its honest "corrected
copy" is the document unchanged. There is nothing to compare against. The control
is structurally unable to fire in exactly the case it was built to police.

A second signal survives and needs no corrected copy: whether the falsifier ever
OPENED THE TARGET AT ALL. A falsifier that never read the passage it accuses has
not demonstrated anything about it. Measured on archived prose falsifiers, this
signal is currently computable on about 32%, and the discrimination control returns
any usable verdict on about 20%. The binding limit is that nothing populates the
corrected copy in production; the open-the-target check needs nothing and could in
principle run on 100%.

## 4. A defect found today, which may explain part of the effect

The verdict reader classified a falsifier's failure by KEYWORD. A falsifier that
died in its own setup — for example asserting its target file exists, before
reading anything — was recorded as HAVING DEMONSTRATED THE DEFECT unless the author
happened to use the words "setup", "precondition" or "guard" in the assertion
message. Measured across three phrasings of one identical fault, two produced a
false confirmation. The control's targets are staged OUTSIDE the repository, so
"target does not resolve" is the ordinary failure mode for a mis-pathed falsifier.
This is being fixed. Treat it as a live hypothesis for part of the effect, not as
the established cause.

## 5. What the panel is asked

Answer in your own voice, and attack the framing if it deserves attacking.

 Q1. Is the open-the-target check sound as a blocking criterion? If a falsifier
     never reads the passage it accuses, is it CORRECT to refuse to let it close a
     critical finding? State the strongest case AGAINST, including any legitimate
     falsifier that would be wrongly refused. Be concrete.

 Q2. What ELSE is computable, deterministically and without asking a model to
     adjudicate, that separates "this falsifier demonstrates the named defect" from
     "this falsifier fails for an unrelated reason"? Rank your proposals by what
     they cost to build against what they would actually catch. Assume access to:
     the falsifier source, its execution trace, stdout/stderr, the target document,
     the accused claim's text and location, and the full archive of past findings.
     Sub-question worth answering separately: is there a cheap check with real
     discriminating power in comparing the COMPUTED OUTCOME two findings assert —
     the numbers, constants or derived values — rather than comparing their prose?

 Q3. Is a zero-plant control the right instrument at all? It has no answer key and
     the "all claims true" property is itself an assumption made by its authors. If
     it is the wrong instrument, name a better one that stays deterministic.

 Q4. Given (a)-(c) in section 2, what is the MINIMUM work needed to make the
     false-positive rate honestly measurable on this system? Assume money is tight
     and a live five-model run is expensive. What is the cheapest experiment that
     would actually settle it?

 Q5. Steelman the position that this is NOT a defect. A reviewer instructed to find
     problems in a correct document will find candidate problems; that is what
     adversarial review does, and CONFIRM-only exists precisely so those candidates
     do not become results. On that reading the machinery is working and the only
     real faults are the mechanical ones in section 4 and 2(c). Say whether you
     accept that reading, and if not, exactly where it fails.

HARD CONSTRAINT ON EVERY ANSWER. No proposal may resolve a finding by model
adjudication, model voting, or model confidence. Anything you propose must be
computable by the runner and itself falsifiable. If your best idea violates that,
say so explicitly and give the deterministic second-best rather than quietly
relaxing the constraint.

Give your verdict, your reasoning, and your single strongest falsification of the
position you expect the other models to take.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    load_env()
    from bench.experiment_11_orchestrator import load_default_config
    from bench.launcher_core import load_cdsfl_directive
    from bench.reference_runner_v3 import dispatch_to_model

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
