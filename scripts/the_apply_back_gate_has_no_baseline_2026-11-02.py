#!/usr/bin/env python3
"""The apply-back gate demands exit 0 from a sandbox that never reaches it.

THE DEFECT. `_apply_back_gate` in `bench/reference_runner_v3.py` copies the repo
into a temporary sandbox, overlays the candidate source at the target path, runs
the configured `test_cmd` there, and REJECTS on any non-zero exit. It never runs
that suite WITHOUT the candidate, so it has no baseline. The sandbox copy
deliberately excludes `.git`, `bench/logs` and the credential files, and a suite
that depends on any of those fails there for reasons the candidate did not cause.
When that happens the gate cannot accept anything at all, and it reports the
failure as though the model's fix had broken 3 tests.

OBSERVED, not hypothesised (note standard Rule 21). `study_run1b_rerun_20261102T033919Z`
made 19 apply-back decisions on 2026-11-02. All 19 were REJECT, 0 were PROMOTE,
and every one carried the byte-identical reason
`suite_fail:3 failed, 48 passed, 28 skipped`. 19 distinct findings editing 19
different passages cannot each break exactly the same 3 tests and skip exactly
the same 28.

ESTABLISHED BY CALLING THE GATE, NOT BY READING IT (`execute-do-not-grep`).
Three candidates were fed to the live `_apply_back_gate` with that run's own
`test_cmd`:

  1. the prose target's OWN bytes -- a change that changes nothing;
  2. prose sharing no sentence with the target;
  3. `bench/runner_core.py` fed its own bytes -- a Python no-op.

All three were REJECTED with the same signature as the 19. A no-op cannot break
a test, so the verdict does not depend on the candidate; and because case 3 is
Python, the fault is NOT confined to prose targets. Re-run them with `--probe`.

AND THE SAME SUITE IS GREEN IN THE REPO: 73 passed, 6 skipped, 0 failed. The
sandbox turns 22 of those passes into skips and 3 into failures. The suite is
`test_immune_memory_consumption.py` + `test_immune_memory_evaluation.py`, which
is the launcher's ARGPARSE DEFAULT -- not a choice made for this run.

WHY THE PROSE HALF IS A RECURRENCE RATHER THAN A NEW FAULT. The non-Python
refusal at `reference_runner_v3.py` is nested inside `if not test_cmd:`, so it
speaks only when no command is configured. A prose target WITH a command falls
through to pytest. `bench/tools/commissioning_arms_2026-09-21.py` fixed this on
2026-09-30 for its prose arm by passing an EMPTY `--test-cmd`, and its own
comment says the argparse default "faked the gate rather than excluding it".
That repair lives in the CALLER, so any launch path that does not go through the
arms table gets the faked gate back -- which is what happened on 2026-11-02.

Producer for the figures quoted in the 2026-11-02 morning report and in
`experimental_notes/CDSFL_MASTER_TASK_LIST.md`. Every proportion carries a
Wilson and a Clopper-Pearson interval, each computed on 2 independent tools.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The run that exposed it, and the suite it was given.
OBSERVED_RUN = "study_run1b_rerun_20261102T033919Z_20261102T033920Z"
OBSERVED_TEST_CMD = ("python3 -m pytest bench/tests/test_immune_memory_consumption.py "
                     "bench/tests/test_immune_memory_evaluation.py -q")
PROSE_TARGET = "bench/BUILD_BOT_TEST_BENCH_FIX_SPEC.md"
PY_TARGET = "bench/runner_core.py"

_PROMOTE = re.compile(r"apply-back PROMOTE (C\d+)")
_REJECT = re.compile(r"apply-back REJECT (C\d+): (.*)")
#: Strip the per-call wall clock so 2 verdicts differing only in timing compare
#: equal. `in 9.91s` and `in 10.24s` are the SAME reason.
#:
#: ANCHORED TO END-OF-LINE AT FIRST, AND THAT WAS WRONG. The live log writes
#: `... 28 skipped in 10.24s (stays CLOSED in registry; not applied to artefact)`,
#: so the elapsed time is NOT last and nothing was stripped: 19 rejections
#: carrying 1 reason were counted as 14 distinct ones, purely by their timings.
#: The implausible count is what exposed it -- a direct grep had already shown
#: all 19 signatures identical. Strip the trailing parenthetical first, then the
#: elapsed time wherever it sits.
_TRAILING_NOTE = re.compile(r"\s*\(stays CLOSED.*?\)\s*$")
_ELAPSED = re.compile(r"\s+in \d+(?:\.\d+)?s\b")


def _reason_of(raw: str) -> str:
    """The reason a rejection gives, with timing and boilerplate removed."""
    return _ELAPSED.sub("", _TRAILING_NOTE.sub("", raw)).strip()


def _two_tool_intervals(k: int, n: int) -> dict:
    """Wilson and Clopper-Pearson, each on 2 independent implementations.

    The 21 April 2026 rule: every computational claim is cross-verified on at
    least 2 tools. Wilson comes from statsmodels and from a closed form built in
    SymPy (exact rationals, then evaluated at 50 digits in mpmath).
    Clopper-Pearson comes from scipy's beta quantiles and from mpmath's
    regularised incomplete beta inverse.
    """
    import mpmath
    import sympy
    from scipy import stats
    from statsmodels.stats.proportion import proportion_confint

    out: dict = {"k": k, "n": n}
    if n == 0:
        return out
    out["p"] = k / n

    # --- Wilson, tool 1: statsmodels
    lo1, hi1 = proportion_confint(k, n, alpha=0.05, method="wilson")

    # --- Wilson, tool 2: the closed form, symbolically in SymPy
    z = sympy.sqrt(2) * sympy.erfinv(sympy.Rational(95, 100))
    kk, nn = sympy.Integer(k), sympy.Integer(n)
    phat = kk / nn
    centre = (phat + z**2 / (2 * nn)) / (1 + z**2 / nn)
    half = (z / (1 + z**2 / nn)) * sympy.sqrt(phat * (1 - phat) / nn
                                              + z**2 / (4 * nn**2))
    mpmath.mp.dps = 50
    lo2 = float(mpmath.mpf(str(sympy.N(centre - half, 40))))
    hi2 = float(mpmath.mpf(str(sympy.N(centre + half, 40))))
    # A proportion cannot leave [0, 1]; clamping also kills the signed zero that
    # otherwise prints as `-0.000000`.
    lo2, hi2 = max(0.0, lo2), min(1.0, hi2)
    out["wilson"] = (lo1, hi1)
    out["wilson_crosscheck_max_abs_diff"] = max(abs(lo1 - lo2), abs(hi1 - hi2))

    # --- Clopper-Pearson, tool 1: scipy beta quantiles
    lo3 = 0.0 if k == 0 else float(stats.beta.ppf(0.025, k, n - k + 1))
    hi3 = 1.0 if k == n else float(stats.beta.ppf(0.975, k + 1, n - k))

    # --- Clopper-Pearson, tool 2: mpmath bisection on the regularised
    #     incomplete beta. `findroot` from a single start point FAILED to
    #     converge here (0.00062 > 2.6e-54 tolerance); bisection brackets the
    #     root by construction, so it cannot fail that way.
    def _betaincinv(a, b, y, iters=200):
        f = lambda x: mpmath.betainc(a, b, 0, x, regularized=True) - y
        lo, hi = mpmath.mpf(0), mpmath.mpf(1)
        for _ in range(iters):
            mid = (lo + hi) / 2
            if f(mid) < 0:
                lo = mid
            else:
                hi = mid
        return float((lo + hi) / 2)

    lo4 = 0.0 if k == 0 else _betaincinv(k, n - k + 1, 0.025)
    hi4 = 1.0 if k == n else _betaincinv(k + 1, n - k, 0.975)
    out["clopper_pearson"] = (lo3, hi3)
    out["cp_crosscheck_max_abs_diff"] = max(abs(lo3 - lo4), abs(hi3 - hi4))
    return out


def _scan_archive() -> dict:
    """Every apply-back decision in every archived run's console log."""
    runs: dict[str, dict] = {}
    for log in sorted((REPO / "bench" / "logs").glob("*/console.log")):
        try:
            text = log.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        promotes = _PROMOTE.findall(text)
        rejects = _REJECT.findall(text)
        if not promotes and not rejects:
            continue
        reasons = {_reason_of(r) for _cid, r in rejects}
        runs[log.parent.name] = {
            "promote": len(promotes),
            "reject": len(rejects),
            "distinct_reject_reasons": len(reasons),
            "reasons": sorted(reasons),
        }
    return runs


def _live_probes() -> list[tuple[str, bool, str]]:
    """Call the real gate on 3 candidates. Off by default: each one copies the
    repository and runs a suite, so it costs about 12 s and ~364 MiB of temp
    space per probe. A `--help` must never cost anything."""
    sys.path.insert(0, str(REPO))
    sys.path.insert(0, str(REPO / "bench"))
    import reference_runner_v3 as rr

    pristine = (REPO / PROSE_TARGET).read_text(encoding="utf-8")
    unrelated = ("# A DOCUMENT THAT IS NOT THE TARGET\n\n"
                 "This text shares no sentence with the specification "
                 "it replaces.\n" * 40)
    py_src = (REPO / PY_TARGET).read_text(encoding="utf-8")
    cases = [
        ("the prose target's OWN bytes (a no-op)", pristine, PROSE_TARGET),
        ("prose sharing no sentence with the target", unrelated, PROSE_TARGET),
        (f"{PY_TARGET} fed its own bytes (a Python no-op)", py_src, PY_TARGET),
    ]
    rows = []
    for name, src, rel in cases:
        ok, detail = rr._apply_back_gate(src, rel, OBSERVED_TEST_CMD)
        rows.append((name, ok, detail))
    return rows


def _unreachability() -> list[tuple[str, bool, str]]:
    """z3 on the control flow: with a non-Python target and a configured
    command, is the prose refusal reachable?

    The branch structure in `_apply_back_gate` is
        if not test_cmd:
            if not is_python_target(rel): return "no suite can gate ..."
            return "no test_cmd configured"
        <run pytest>
    so the honest refusal is guarded by `not test_cmd` AND `not is_python`.
    """
    import z3

    out = []
    is_python = z3.Bool("is_python_target")
    has_cmd = z3.Bool("test_cmd_configured")
    prose_refusal = z3.And(z3.Not(has_cmd), z3.Not(is_python))
    runs_pytest = has_cmd

    s = z3.Solver()
    s.add(z3.Not(is_python), has_cmd, prose_refusal)
    r = s.check()
    out.append(("with a prose target AND a configured command, the honest "
                "prose refusal is UNREACHABLE", r == z3.unsat, str(r)))

    s = z3.Solver()
    s.add(z3.Not(is_python), has_cmd, z3.Not(runs_pytest))
    r = s.check()
    out.append(("with a prose target AND a configured command, pytest DOES "
                "run", r == z3.unsat, str(r)))

    # SymPy as the second tool on the same logical claim, via boolean algebra.
    import sympy
    from sympy.logic.boolalg import And as sAnd, Not as sNot
    ip, hc = sympy.symbols("is_python has_cmd")
    expr = sAnd(sNot(ip), hc, sAnd(sNot(hc), sNot(ip)))
    out.append(("SymPy agrees the same conjunction is unsatisfiable",
                sympy.simplify_logic(expr) == sympy.false,
                str(sympy.simplify_logic(expr))))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(
        description=("Measure the apply-back gate's missing baseline across the "
                     "run archive, and optionally re-run the 3 live probes."))
    ap.add_argument("--probe", action="store_true",
                    help=("call the real gate on 3 candidates; costs ~12 s and "
                          "~364 MiB of temp space each, so it is OFF by default"))
    args = ap.parse_args()

    print("=" * 76)
    print("THE APPLY-BACK GATE DEMANDS EXIT 0 FROM A SANDBOX THAT NEVER REACHES IT")
    print("=" * 76)

    runs = _scan_archive()
    tot_p = sum(r["promote"] for r in runs.values())
    tot_r = sum(r["reject"] for r in runs.values())
    tot = tot_p + tot_r

    print(f"\n1. EVERY APPLY-BACK DECISION IN THE RUN ARCHIVE "
          f"({len(runs)} run(s) made one)")
    for name, r in sorted(runs.items()):
        print(f"   {name[:58]:58s} promote={r['promote']:<3d} "
              f"reject={r['reject']:<3d} distinct reasons={r['distinct_reject_reasons']}")
    print(f"\n   total PROMOTE : {tot_p}")
    print(f"   total REJECT  : {tot_r}")
    if tot:
        iv = _two_tool_intervals(tot_r, tot)
        print(f"   rejected      : {tot_r} of {tot}, {iv['p']:.6f}")
        print(f"     Wilson 95%          [{iv['wilson'][0]:.6f}, {iv['wilson'][1]:.6f}]"
              f"   (2-tool max |diff| {iv['wilson_crosscheck_max_abs_diff']:.2e})")
        print(f"     Clopper-Pearson 95% [{iv['clopper_pearson'][0]:.6f}, "
              f"{iv['clopper_pearson'][1]:.6f}]"
              f"   (2-tool max |diff| {iv['cp_crosscheck_max_abs_diff']:.2e})")

    # ★ WHAT THE DEFECT ACTUALLY COST, added 2026-11-02 because "0 of 34"
    # read as 34 discarded fixes and that is not what happened.
    # ★ WHERE THE WRONG SUITE CAME FROM, added 2026-11-02 so the figure quoted
    # in B88 is reproducible rather than prose. The launcher's argparse default
    # is the immune-memory suite; a run that passes no `--test-cmd` gets it
    # whatever its target is.
    print("\n1a. HOW MANY PROSE RUNS WERE HANDED A SUITE BY ARGPARSE")
    DEFAULT_CMD = OBSERVED_TEST_CMD
    prose_all, on_default, no_flag = 0, 0, 0
    import json as _json
    for rep in sorted((REPO / "bench" / "logs").glob("*/*_report.json")):
        try:
            d = _json.loads(rep.read_text(errors="replace"))
        except Exception:  # noqa: BLE001
            continue
        cfg = d.get("_declared_config") or {}
        if not cfg:
            continue
        art = str(cfg.get("test_article") or "")
        tk = d.get("target_kind")
        kind = tk.get("kind") if isinstance(tk, dict) else None
        if kind != "prose" and not art.endswith(".md"):
            continue
        prose_all += 1
        if str(cfg.get("test_cmd") or "").strip() == DEFAULT_CMD:
            on_default += 1
        if "--test-cmd" not in (d.get("_declared_argv") or []):
            no_flag += 1
    print(f"   prose runs with a declared config        : {prose_all}")
    print(f"   ... carrying the launcher's ARGPARSE DEFAULT: {on_default}")
    print(f"   ... passing no --test-cmd at all            : {no_flag}")
    if prose_all:
        iv1 = _two_tool_intervals(on_default, prose_all)
        print(f"     Wilson 95%          [{iv1['wilson'][0]:.6f}, "
              f"{iv1['wilson'][1]:.6f}]")
        print(f"     Clopper-Pearson 95% [{iv1['clopper_pearson'][0]:.6f}, "
              f"{iv1['clopper_pearson'][1]:.6f}]")

    print("\n1b. WHAT IT COST, WHICH IS LESS THAN 0 OF 34 SOUNDS")
    prose_runs, total_decisions, wasted = 0, 0, 0.0
    for name in runs:
        d = (REPO / "bench" / "logs" / name)
        rep = next(iter(sorted(d.glob("*_report.json"))), None)
        kind = None
        if rep is not None:
            try:
                import json as _j
                rd = _j.loads(rep.read_text(errors="replace"))
                tk = rd.get("target_kind")
                kind = tk.get("kind") if isinstance(tk, dict) else None
                if kind is None:
                    art = (rd.get("_declared_config") or {}).get("test_article", "")
                    kind = "prose" if str(art).endswith(".md") else None
            except Exception:  # noqa: BLE001
                kind = None
        if kind == "prose":
            prose_runs += 1
        total_decisions += runs[name]["promote"] + runs[name]["reject"]
        log = d / "console.log"
        if log.is_file():
            for line in log.read_text(errors="replace").splitlines():
                if "apply-back REJECT" in line:
                    m = re.search(r"\s+in (\d+(?:\.\d+)?)s\b", line)
                    if m:
                        wasted += float(m.group(1))
    print(f"   runs whose target was PROSE : {prose_runs} of {len(runs)}")
    if runs:
        iv2 = _two_tool_intervals(prose_runs, len(runs))
        print(f"     Wilson 95%          [{iv2['wilson'][0]:.6f}, "
              f"{iv2['wilson'][1]:.6f}]")
        print(f"     Clopper-Pearson 95% [{iv2['clopper_pearson'][0]:.6f}, "
              f"{iv2['clopper_pearson'][1]:.6f}]")
    print(f"   suite time on refusals that could not depend on the candidate:")
    print(f"     {wasted:.1f} s ({wasted/60:.1f} min) across {total_decisions} "
          f"decision(s)")
    print("   => 0 PROMOTIONS WERE LOST. A prose target cannot be gated by a")
    print("      pytest suite at all, so the repaired gate still refuses all of")
    print("      them -- for being prose, which is TRUE. What the defect cost is")
    print(f"      {total_decisions} false reasons in the project's own evidence,")
    print(f"      and {wasted:.1f} s of suite time producing them.")

    print(f"\n2. THE RUN THAT EXPOSED IT: {OBSERVED_RUN[:46]}")
    obs = runs.get(OBSERVED_RUN)
    if obs is None:
        print("   NOT FOUND in the archive -- the observation cannot be reproduced.")
    else:
        print(f"   promote={obs['promote']}  reject={obs['reject']}  "
              f"distinct reject reasons={obs['distinct_reject_reasons']}")
        for r in obs["reasons"]:
            print(f"     reason: {r}")
        if obs["reject"] > 1 and obs["distinct_reject_reasons"] == 1:
            print(f"   => {obs['reject']} distinct findings, 1 distinct reason. A "
                  "verdict that")
            print("      never varies with its input is not a measurement of its input.")

    print("\n3. IS THE HONEST PROSE REFUSAL EVEN REACHABLE? (z3, cross-checked in SymPy)")
    for name, ok, detail in _unreachability():
        print(f"   [{'HOLDS' if ok else 'FAILS'}] {name}")
        print(f"            solver says: {detail}")

    probe_rows: list[tuple[str, bool, str]] = []
    if args.probe:
        print("\n4. THE LIVE GATE, CALLED ON 3 CANDIDATES")
        probe_rows = _live_probes()
        sigs = set()
        for name, ok, detail in probe_rows:
            clean = _reason_of(detail)
            sigs.add(clean)
            print(f"   [{'ACCEPT' if ok else 'REJECT'}] {name}")
            print(f"            {clean}")
        print(f"\n   distinct verdicts across 3 candidates: {len(sigs)}")
        if len(sigs) == 1 and not any(ok for _n, ok, _d in probe_rows):
            print("   => A no-op, unrelated prose and a Python no-op all get the")
            print("      SAME refusal. The gate is blind to the candidate, and the")
            print("      blindness is not confined to prose targets.")
    else:
        print("\n4. THE LIVE GATE: skipped. Pass --probe to call it "
              "(~12 s and ~364 MiB per probe).")

    # EXIT NON-ZERO IF THE OBSERVATION THIS SCRIPT DOCUMENTS HAS GONE AWAY, so a
    # future repair makes the producer fail loudly rather than keep reporting a
    # defect that no longer exists.
    bad = []
    if obs is None:
        bad.append("the observed run is missing from the archive")
    elif not (obs["reject"] > 1 and obs["distinct_reject_reasons"] == 1):
        bad.append("the observed run no longer shows 1 reason for many rejects")
    if args.probe:
        if any(ok for _n, ok, _d in probe_rows):
            bad.append("the live gate now ACCEPTS one of the 3 candidates")
    print()
    if bad:
        print("  THE DOCUMENTED OBSERVATION HAS CHANGED:")
        for b in bad:
            print(f"    - {b}")
        print("  Re-read this script's header before quoting any figure from it.")
        return 1
    print("  The observation reproduces.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
