"""FALSIFIER: with `score_prose_listings=True`, S_k must never ADMIT on a
prose target -- it may convict (REJECTED) or abstain (NO_SCORE), and R_k must
hold on every unadmitted fix.

Run on the tree of 2026-09-22 BEFORE the veto-only repair, this raises
AssertionError on the first fixture: all 5 harmful and all 5 correct fixes
scored ADMISSIBLE (sk 0.5333..1.0000) and moved R_k 0.5000 -> as low as
0.3667, refuting the acceptance suite's Property 1 (5/5) and Property 2
(10/10). On the repaired tree it exits cleanly. Companion producer of the
original measurement: scripts/a19_flag_admits_harmful_fixes_2026-09-22.py
(which drives the same path but only prints).

Repo-relative on purpose: no operator-specific ROOT, no Wolfram, no network.
"""
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bench.tests.test_prose_acceptance_stem as T                # noqa: E402
from bench.reference_runner_v3 import (                           # noqa: E402
    SK_ADMISSIBLE, _evaluate_sk_for_findings,
)
from bench.tests.fixtures.stem.stem_fixtures import load_all      # noqa: E402

# WIRED 2026-09-24 (CC1). This file works at MODULE level, so there is no
# main() for a help flag to intercept. Answered here, before any work.
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
if str(_pl.Path(__file__).resolve().parents[1]).endswith('scripts'):
    pass
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)

tmp = pathlib.Path(tempfile.mkdtemp())
failures = []
try:
    for fx in load_all():
        baseline = T._real_baseline(fx)
        for label, patches in (("harmful", fx.harmful_fix),
                               ("correct", fx.correct_fix)):
            for flag in (False, True):
                d = tmp / f"{fx.key}-{label}-{flag}"
                d.mkdir(parents=True, exist_ok=True)
                copy = d / fx.doc_path.name
                shutil.copy(fx.doc_path, copy)
                reg = T.FindingRegistry()
                cid = T._register(reg, T._fix_text(fx, patches, copy), copy)
                stats = _evaluate_sk_for_findings(
                    reg, fx.document, str(copy), baseline,
                    round_idx=1, score_prose_listings=flag)
                r = reg.entries[cid].get("sk_result") or {}
                tri = r.get("tristate")
                r_old, r_new = r.get("R_old"), r.get("R_new")
                print(f"{fx.key:<12} {label:<8} flag={flag!s:<5} "
                      f"{tri:<12} R {r_old} -> {r_new}")
                if tri == SK_ADMISSIBLE or stats["admissible"] != 0:
                    failures.append(
                        f"{fx.key}/{label}/flag={flag}: ADMITTED ({tri})")
                if r_old is not None and r_new is not None and r_new != r_old:
                    failures.append(
                        f"{fx.key}/{label}/flag={flag}: R_k moved "
                        f"{r_old} -> {r_new} on an unadmitted fix")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

if failures:
    print("FALSIFIED")
    raise AssertionError(
        "S_k admitted or moved risk on a prose target:\n  "
        + "\n  ".join(failures))
print(f"OK: 20 evaluations (5 fixtures x 2 fixes x 2 flag states), "
      f"0 admissions, R_k held in every case.")
