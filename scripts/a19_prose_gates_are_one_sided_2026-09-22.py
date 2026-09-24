"""FALSIFIER for the one-sided prose rule (panel seat, 2026-09-22).

THE CLAIM UNDER TEST. On a prose target with `sk_score_prose_listings=True`,
`compute_sk` must never return ADMISSIBLE. It must return REJECTED when the fix
INTRODUCED a new defect into a fenced listing, and NO_SCORE otherwise -- and
NO_SCORE must leave R_k exactly where it was.

Runs the runner's own round-loop entry point `_evaluate_sk_for_findings` over
the five adversarial fixtures of `bench/tests/test_prose_acceptance_stem.py`, in
BOTH flag configurations, and additionally derives the aggregation result that
made the defect inevitable.

FAILS IFF THE DEFECT IS PRESENT: prints FALSIFIED and raises AssertionError when
any harmful fix is admitted or any unscored fix moves R_k. Exits cleanly when
the rule holds. Imports the REAL runner; nothing is retyped.

No Wolfram: a stored falsifier must run on a checkout that has none.
"""
import contextlib
import io
import os
import pathlib
import shutil
import sys
import tempfile

ROOT = pathlib.Path(os.environ.get("CE_ROOT", pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(ROOT))

import bench.tests.test_prose_acceptance_stem as T                    # noqa: E402
from bench.reference_runner_v3 import (                               # noqa: E402
    SK_ADMISSIBLE, SK_NO_SCORE, SK_REJECTED, _evaluate_sk_for_findings,
    _gates_introduced_new_defects, compute_sk,
)
from bench.tests.fixtures.stem.stem_fixtures import load_all          # noqa: E402

FAILURES = []
R0 = 0.5


def check(cond, msg):
    if not cond:
        FAILURES.append(msg)


# ── 1. Both flag configurations, through the round-loop entry point ──────────
print(f"{'fixture':<12} {'fix':<8} {'flag':<6} {'tristate':<11} "
      f"{'R_old':>7} {'R_new':>7}  reason")
print("-" * 96)
tmp = pathlib.Path(tempfile.mkdtemp())
try:
    for fx in load_all():
        bl = T._real_baseline(fx)
        for label, patches in (("harmful", fx.harmful_fix),
                               ("correct", fx.correct_fix)):
            for flag in (False, True):
                d = tmp / f"{fx.key}-{label}-{flag}"
                d.mkdir(parents=True, exist_ok=True)
                copy = d / fx.doc_path.name
                shutil.copy(fx.doc_path, copy)
                reg = T.FindingRegistry()
                cid = T._register(reg, T._fix_text(fx, patches, copy), copy)
                with contextlib.redirect_stdout(io.StringIO()):
                    _evaluate_sk_for_findings(
                        reg, fx.document, str(copy), bl, round_idx=1,
                        score_prose_listings=flag)
                r = reg.entries[cid].get("sk_result") or {}
                tri = r.get("tristate", "-")
                r_old, r_new = r.get("R_old", R0), r.get("R_new", R0)
                why = ((r.get("gate_details", {}).get("_prose_one_sided") or {})
                       .get("detail", ""))[:34]
                print(f"{fx.key:<12} {label:<8} {str(flag):<6} {tri:<11} "
                      f"{r_old:>7.4f} {r_new:>7.4f}  {why}")

                # PROPERTY 1 -- a harmful fix is never admitted.
                if label == "harmful":
                    check(tri != SK_ADMISSIBLE,
                          f"P1 {fx.key}/flag={flag}: harmful fix ADMITTED "
                          f"(sk={r.get('sk')})")
                # No prose fix of any kind is admitted.
                check(tri != SK_ADMISSIBLE,
                      f"ONE-SIDED {fx.key}/{label}/flag={flag}: prose fix "
                      f"ADMISSIBLE, the gates paid out on a clean static sweep")
                # PROPERTY 2 -- an UNSCORED fix moves R_k in neither direction.
                if tri == SK_NO_SCORE:
                    check(abs(r_new - r_old) < 1e-12,
                          f"P2 {fx.key}/{label}/flag={flag}: NO_SCORE moved "
                          f"R_k {r_old:.4f} -> {r_new:.4f}")
finally:
    shutil.rmtree(tmp, ignore_errors=True)

# ── 2. The rule DISCRIMINATES: it is not "reject everything" ─────────────────
# Anti-vacuity. If every case came back NO_SCORE the assertions above would pass
# while the machinery had learned nothing. The three harms that carry a static
# signal must be actively REJECTED; every correct fix must NOT be.
print("-" * 96)
rejected, scored = set(), {}
for fx in load_all():
    for label, patches in (("harmful", fx.harmful_fix), ("correct", fx.correct_fix)):
        with contextlib.redirect_stdout(io.StringIO()):
            res = compute_sk(T._fix_text(fx, patches, fx.doc_path), fx.document,
                             str(fx.doc_path), score_prose_listings=True,
                             baseline=T._real_baseline(fx))
        scored[(fx.key, label)] = res.tristate
        if label == "harmful" and res.tristate == SK_REJECTED:
            rejected.add(fx.key)
print("harmful fixes actively REJECTED:", sorted(rejected))
check(rejected == {"structural", "statistics", "numerical"},
      f"DISCRIMINATION: expected the 3 statically-visible harms to be "
      f"REJECTED, got {sorted(rejected)}")
false_rejects = [k for (k, l), t in scored.items()
                 if l == "correct" and t == SK_REJECTED]
check(not false_rejects,
      f"FALSE REJECTION: correct fixes rejected: {false_rejects}")

# ── 3. The escalation the old aggregation could not stop ─────────────────────
# A lint-clean fix introducing N new bandit HIGHs scored sk >= 1/3 ADMISSIBLE
# for every N, because E = (1/3)e3 + (2/3)e4 and e4 floors at 0. Must REJECT.
import re as _re                                                       # noqa: E402

# WIRED 2026-09-24 (CC1). This file works at MODULE level, so there is no
# main() for a help flag to intercept. Answered here, before any work.
import sys as _sys, pathlib as _pl
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[1]))
if str(_pl.Path(__file__).resolve().parents[1]).endswith('scripts'):
    pass
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parent.parent))
from _cli_help import answer_help  # noqa: E402
answer_help(__doc__, __file__)
fx = next(f for f in load_all() if f.key == "structural")
anchor = _re.search(r"```python\n(.*?)```", fx.document, _re.S
                    ).group(1).rstrip().splitlines()[-1]
for n in (1, 20):
    body = "\n".join(f'cmd{i} = "rm -rf /"\nsubprocess.call(cmd{i}, shell=True)'
                     for i in range(n))
    txt = (f"<<<< SEARCH {fx.doc_path}\n{anchor}\n==== REPLACE\n"
           f"{anchor}\nimport subprocess\n{body}\n>>>>\n")
    with contextlib.redirect_stdout(io.StringIO()):
        res = compute_sk(txt, fx.document, str(fx.doc_path),
                         score_prose_listings=True,
                         baseline=T._real_baseline(fx))
    print(f"injected {n:>2} new bandit HIGH -> {res.tristate}")
    check(res.tristate == SK_REJECTED,
          f"SATURATION n={n}: {n} new HIGHs returned {res.tristate}")

# ── 4. The helper reads NEW, not TOTAL ───────────────────────────────────────
check(_gates_introduced_new_defects(
    {"e3_ruff": {"detail": "2 total, 0 new (baseline: 2)"},
     "e4_bandit": {"detail": "3 HIGH/0 MEDIUM (baseline: 3H/0M, new: 0H/0M)"}}) == [],
    "PRE-EXISTING DEFECTS were charged to the fix")
check(len(_gates_introduced_new_defects(
    {"e3_ruff": {"detail": "5 total, 1 new (baseline: 4)"},
     "e4_bandit": {"detail": "1 HIGH/0 MEDIUM (baseline: 0H/0M, new: 1H/0M)"}})) == 2,
    "NEW defects were not detected")
check(_gates_introduced_new_defects({"e3_ruff": {"detail": "garbled"}}) == [],
      "an unreadable gate detail became an accusation")

print("-" * 96)
if FAILURES:
    print("FALSIFIED")
    for f in FAILURES:
        print("  *", f)
    raise AssertionError(f"{len(FAILURES)} property violation(s)")
print("rule holds: no prose fix admitted; 3/5 harms actively rejected; "
      "0/5 correct fixes rejected; every NO_SCORE held R_k")
