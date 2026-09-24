"""Q2: is the introduction rate nu (= b) measurable in this project's archive?

ANSWER, in three parts, all executed:
 (A) For the event the MODEL needs ("any flaw in class K"), NO: every admitted
     pre-repair state in this archive is CONFIRMED-FLAWED by construction, so the
     denominator of b (clean targets a repair touched) is never enumerated.
 (B) But a NARROW, ALREADY-RUNNING, ALREADY-BASELINED channel does exist and is
     being thrown away: the e3/e4 effect gates carry a pre-fix baseline and report
     `N new` -- a genuine clean->flawed transition in their own scope.
 (C) The heaviest gate, e2_regression (weight 2.0), does NOT carry a baseline,
     although `apply_and_score` already receives a `baseline` argument. That is a
     one-call gap, and closing it is what makes nu measurable at useful scope.

Run: python3 scripts/cc_nu_measurability_2026-09-20.py
Exit 0 = the report below is what the archive says. AssertionError = a claim broke.

RELOCATED 2026-09-24 (CC1), from scripts/ to scripts/panel_falsifiers/.

This is a DIAGNOSTIC FALSIFIER: it exits non-zero while the defect it describes
is LIVE, which is the opposite of what an ordinary measurement script does.
`bench/tests/test_operational_scripts.py` probes every script in scripts/ by
IMPORTING it and requires the import to succeed, so a falsifier that fires at
import made that guard red for a reason unconnected to the guard's subject.

scripts/panel_falsifiers/ is this project's existing home for that shape and is
outside the probe's one-level glob. The finding itself is unchanged and still
open; only the file's location moved.
"""
import ast, glob, json, os, re, sys, collections
import statsmodels.stats.proportion as smp

# WIRED 2026-09-22 (CC1). Delivered by a panel seat without it, so `--help`
# ran the whole measurement. A help flag must ANSWER, never ACT.
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
FAIL = []
def check(name, cond, note=""):
    print(("PASS " if cond else "FAIL ") + name + ("  " + note if note else ""))
    if not cond: FAIL.append(name)

# ---- (A) the model's own event: is any pre-repair CLEAN state recorded? -----
print("=== (A) does the archive ever admit a CLEAN pre-repair state? ===")
src = open("bench/fix_efficacy.py").read()
check("A1 fix_efficacy REFUSES a non-CONFIRMED baseline (pre-state must be FLAWED)",
      "INDETERMINATE_NO_BASELINE" in src and "nothing for a fix to cure" in src)
m = open("bench/execution_based_matcher.py").read()
check("A2 execution_based_matcher requires BOTH members CONFIRM on the pristine state",
      'BASELINE_STATE = "pristine"' in m)
absent = [p for p in ("post_fix_verdict","pre_fix_verdict","clean_baseline",
                      "verified_clean","introduction_rate","nu_measured")
          if not any(p in open(f, errors="ignore").read()
                     for f in glob.glob("bench/**/*.py", recursive=True))]
check("A3 no pre/post or clean-baseline field name exists anywhere in bench/",
      len(absent) == 6, f"absent={absent}")

# ---- (B) the channel that IS baselined: e3/e4 deltas ------------------------
print("\n=== (B) e3_ruff / e4_bandit DO carry a baseline and report a delta ===")
rr = open("bench/reference_runner.py").read()
check("B1 e3 takes a baseline argument", "baseline_violations" in rr)
check("B2 e3 computes an introduction DELTA", "delta = max(0, total_count - baseline_violations)" in rr)
rec = collections.defaultdict(list)
for f in glob.glob("bench/logs/**/*.json", recursive=True):
    try: d = json.load(open(f))
    except Exception: continue
    def w(o, dep=0):
        if dep > 7: return
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("e3_ruff", "e4_bandit") and isinstance(v, dict):
                    rec[k].append((os.path.basename(f), str(v.get("detail", ""))))
                w(v, dep + 1)
        elif isinstance(o, list):
            for v in o[:80]: w(v, dep + 1)
    w(d)
pr = re.compile(r"(\d+)\s+new\b")
res = {}
for gate in ("e3_ruff", "e4_bandit"):
    seen, intro, tot = set(), 0, 0
    for fn, det in rec[gate]:
        if (fn, det) in seen or "unavailable" in det.lower(): continue
        seen.add((fn, det))
        g = pr.search(det)
        if g:
            tot += 1
            intro += int(g.group(1)) > 0
    res[gate] = (intro, tot)
    if tot:
        lo, hi = smp.proportion_confint(intro, tot, alpha=0.05, method="wilson")
        print(f"  {gate}: introduction events {intro}/{tot} = {intro/tot:.4f}"
              f"  Wilson95=[{lo:.4f}, {hi:.4f}]")
        print(f"    implied R* = nu/(q+nu) at q=0.35: point {(intro/tot)/(0.35+intro/tot):.4f},"
              f" Wilson upper {hi/(0.35+hi):.4f}")
    else:
        print(f"  {gate}: {len(seen)} records, NONE reporting a delta (baseline unavailable)")
check("B3 e3_ruff yields a NON-ZERO scoped introduction rate from the live archive",
      res["e3_ruff"][1] > 0 and res["e3_ruff"][0] > 0, f"{res['e3_ruff'][0]}/{res['e3_ruff'][1]}")

# ---- (C) the one-call gap: e2 has no baseline -------------------------------
print("\n=== (C) e2_regression (weight 2.0, the heaviest gate) has NO baseline ===")
tree = ast.parse(rr)
sig, call_args = None, None
for n in ast.walk(tree):
    if isinstance(n, ast.FunctionDef) and n.name == "_run_effect_regression":
        sig = [a.arg for a in n.args.args]
    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id == "_run_effect_regression"):
        call_args = [getattr(a, "id", type(a).__name__) for a in n.args]
print(f"  _run_effect_regression signature : {sig}")
print(f"  its only call site passes        : {call_args}")
check("C1 e2 signature has NO baseline parameter (unlike e3/e4)",
      sig is not None and not any("baseline" in a for a in sig))
check("C2 e2 is called on the MODIFIED source only -- the pre-fix suite is never run",
      call_args is not None and "modified" in call_args and
      not any("source" == a for a in call_args[:1]))
check("C3 a `baseline` IS already threaded into the enclosing scorer (the gap is ONE call)",
      "if baseline is None:" in rr and "baseline = {}" in rr)

# ---- the fix, stated so it can be implemented and re-measured ---------------
print("""
=== FIX (additive, no new parameter, no new flag) =========================
In bench/reference_runner.py, beside the existing e2 call, add ONE more call on
the UNMODIFIED source and record it:

    e2b_score, e2b_detail = _run_effect_regression(source, source_path, test_cmd)
    details["e2_baseline"] = {"score": e2b_score, "detail": e2b_detail}

Then nu is estimable at the regression suite's scope, with no new parameter:
    introduction event  <=>  e2_baseline.score == 1.0  AND  e2_regression.score < 1.0
and nu_hat = (# introduction events) / (# fixes whose baseline suite was green),
reported with a Wilson interval, exactly as e3 already permits.

WHY IT MATTERS: without it, the 70 deduplicated e2 records in bench/logs cannot
be decomposed -- 44 are RED but there is no way to tell a PRE-EXISTING red suite
from one the fix broke. With it, they can. This is the difference between an
unidentified mixture and a measurement.
==========================================================================""")
print(f"{'ALL CHECKS PASSED' if not FAIL else 'FAILED: ' + ', '.join(FAIL)}")
sys.exit(1 if FAIL else 0)
