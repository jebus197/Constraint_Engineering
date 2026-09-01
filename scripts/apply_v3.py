#!/usr/bin/env python3
"""Apply the ten composed patches to the working tree, making v3.

v3 IS A DIRECT DERIVATION OF v2, NOT A REBUILD. Founder instruction, 2026-08-23.
The file keeps its name: `reference_runner_v3.py` is imported by configs, tests and
launchers, and renaming it would change the blast radius from "ten patches" to
"every import in the project" for no gain. The VERSION is metadata, and it lands in
each run's report, which is where a reader actually needs it.

Nothing here is invented. Every patch was accepted by the mechanical gate -- the
patch's own test must FAIL at the parent, PASS with the patch, and leave the suite
green against the parent's own failing set -- and the set was then proved to
compose: 10 of 10 applied, 141 accepted tests passing together, 3,759 suite passes
with zero failures the parent does not already have.

If any hunk fails to apply, every file this script has touched is restored and the
run aborts. A half-applied v3 is worse than no v3.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from bench import build_acceptance as BA  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "composer", REPO / "scripts/compose_all_2026-08-23.py")
_composer = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_composer)
ACCEPTED, ORDERS = _composer.ACCEPTED, _composer.ORDERS

LOGS = REPO / "bench/logs/build_experiment_2026-08-22"
ORDER = next(iter(ORDERS.values()))

MARKER = ('"""Parameterised reference runner for CDSFL experiments '
          '(Exp 37+, Bench Run 2).')

BANNER = MARKER + '''

RUNNER VERSION v3 (2026-08-23). A DIRECT DERIVATION OF v2, NOT A REBUILD.

v3 is v2 with ten mechanically-validated patches applied. Each was accepted by a
gate requiring the patch's own test to FAIL at the parent, PASS with the patch, and
leave the full suite green against the parent's own failing set -- no model vote and
no assistant judgement anywhere in that path. The set was then proved to compose:
10 of 10 applied in order, 141 accepted tests passing together, 3,759 suite passes
with zero failures the parent does not already have.

What changed, and why each mattered:

  T01  Discrimination failures now reach the escalation ladder. The sub-critical arm
       admitted ERROR and nothing else, so a falsifier that fired against a CORRECTED
       copy -- a broken instrument, not a refuted claim -- was never sent to a
       stronger writer.
  T02  The discrimination control is FED. It had eight outcomes and three self-probes
       and HAD NEVER FIRED ONCE in this project's life, because it waits on a
       corrected copy that nothing supplied. It is now derived from each finding's
       own proposed fix.
  T03  The survived-falsification ledger is WIRED. It records that a claim was tested
       and STOOD, closing the gap where a clean control run produces an ABSENCE
       indistinguishable from a dispatch failure or a document nobody read.
  T04  An equipment failure can no longer write a terminal status. Measured before
       the fix: 4 of 24 did, two of them writing REFUTED on a falsifier that never
       ran.
  T05  The Bugzilla status vocabulary and machine-readable catalogue. CORROBORATED
       makes co-discovery visible; every status declares who may assert it and what
       evidence it requires, enforced at the single status chokepoint.
  T06  The load balancer is SHELVED and marked in the documentation (founder ruling).
  T07  --dry-run for the null-perturbation control, which overwrote its own committed
       result when run with a limit.
  T08  The memory-ledger recount moves into the save-state path, after five
       consecutive manual corrections of the same figure.
  T09  The frozen critical-severity pre-registration is cited from the live queue,
       which governed the 0.7 threshold and never named it.
  T10  The 67 unmatchable fixes and 30 errored falsifiers are classified by cause.

TWO SETS IN THE ROUTING/DEMOTION SPLIT ARE LOAD-BEARING.
EQUIPMENT_FAILURE_VERDICTS drives DEMOTION -- the instrument produced no reading, so
no terminal status may stand on it. ROUTABLE_INSTRUMENT_FAULTS drives ROUTING and
additionally carries NON_DISCRIMINATING, whose instrument DID produce a reading that
simply does not depend on the target. Collapsing the two turns discrimination
BLOCKING on by the back door, and blocking is default-off by founder ruling
(RunnerConfig.discrimination_control_blocks). A first merge did exactly that and
three tests caught it, one written for precisely that purpose.
'''


def main() -> int:
    applied: list = []
    tests: list = []
    touched: dict = {}          # path -> content before this script ran

    for tid in ORDER:
        resp = (LOGS / ACCEPTED[tid]).read_text(encoding="utf-8", errors="replace")
        patches = BA.parse_patch(resp)
        tpath, tsrc = BA.parse_test(resp)
        for rel, search, replace in patches:
            f = REPO / rel
            if not f.is_file():
                _restore(touched)
                print(f"  ABORT at {tid}: target absent {rel}. Tree restored.")
                return 1
            text = f.read_text(encoding="utf-8", errors="replace")
            n = text.count(search)
            if n != 1:
                _restore(touched)
                print(f"  ABORT at {tid}: {rel} SEARCH matches {n}x. Tree restored.")
                return 1
            touched.setdefault(rel, text)
            f.write_text(text.replace(search, replace, 1), encoding="utf-8")
        if tpath:
            tf = REPO / tpath
            tf.parent.mkdir(parents=True, exist_ok=True)
            tf.write_text(tsrc, encoding="utf-8")
            tests.append(tpath)
        applied.append(tid)
        print(f"  {tid} applied: {sorted({p[0] for p in patches})}")

    runner = REPO / "bench/reference_runner_v3.py"
    src = runner.read_text(encoding="utf-8")
    if src.count(MARKER) != 1:
        _restore(touched)
        print("  ABORT: could not find the docstring anchor for the version banner.")
        return 1
    if "RUNNER VERSION v3" in src:
        print("  version banner already present; not duplicating")
    else:
        touched.setdefault("bench/reference_runner_v3.py", src)
        runner.write_text(src.replace(MARKER, BANNER, 1), encoding="utf-8")
        print("  version banner written: v3")

    (LOGS / "v3_applied.json").write_text(
        json.dumps({"version": "v3", "applied": applied, "tests": tests}, indent=1))
    print(f"\n  {len(applied)} patches applied, {len(tests)} test files added")
    return 0


def _restore(touched: dict) -> None:
    for rel, original in touched.items():
        (REPO / rel).write_text(original, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
