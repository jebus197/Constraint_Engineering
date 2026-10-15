#!/usr/bin/env python3
"""The coherence-budget recalibration cannot be satisfied by running the runs.

WHY THIS WAS LOOKED AT. `coherence_budget_recalibration` is 1 of the programme's
outstanding measurements, and task B6 item 1 names
`update_coherence_budgets_from_experiments` as the mechanism that will re-derive
the budgets from the 2 free runs. Those budgets gate the coherence pruner's
lean-versus-full ablation arm, which every proposed directive cut has been gated
on since 2026-07-18. So the question "can this actually be driven from the runs?"
is on the programme's critical path, and it was asked while run 1 was in its
post-convergence sweep.

THE ANSWER IS NO, FOR 3 INDEPENDENT REASONS, EACH SUFFICIENT ON ITS OWN.

  1. NOTHING CALLS IT. An AST walk over `bench/` and `scripts/`, excluding
     `bench/logs/`, finds 0 `ast.Call` nodes naming the function and 0
     `ImportFrom` nodes importing it. The only textual references are prose
     inside 4 test docstrings and 1 script comment, which a grep reports and an
     AST walk correctly does not. This is the "addition that nothing reaches"
     half of the additive standard, which has 11 prior confirmed instances in
     this project against 0 confirmed removals of something needed.

  2. IT PERSISTS NOTHING. The body is 2 lines: it calls
     `calibrate_coherence_thresholds(log_root)` and then
     `MODEL_COHERENCE_BUDGETS.update(calibrated)`. `MODEL_COHERENCE_BUDGETS` is a
     dict LITERAL in the source at `bench/cdsfl_registry/composer.py:69`. It is
     never read from disk and never written to disk anywhere outside tests, which
     save and restore it. So a calibration would live only for the lifetime of the
     process that performed it, and the next run would start from the literal again.

  3. THE RUNS DO NOT EMIT THE SHAPE IT READS, SO ON REAL DATA IT RETURNS ITS OWN
     DEFAULTS. The docstring asks for entries carrying `model`, `chars` and a
     response field, with at least `min_points_per_model = 5` points before a
     model is calibrated at all. Called on free run 1's own log directory it
     returns values IDENTICAL to the source literal for all 5 models, because the
     final loop is `thresholds.setdefault(model, fallback)` over
     `MODEL_COHERENCE_BUDGETS` itself. A function that returns its input when
     given a real experiment is a fixed point, not a calibration.

AND THE CALIBRATOR ITSELF IS NOT BROKEN, WHICH IS THE DISTINCTION THAT DECIDES
THE FIX. Fed a purpose-built fixture in exactly the documented shape, it moves
`opus_4_6` from the literal 0.02 to 0.0571. The algorithm works. The gap is a
SCHEMA MISMATCH between what the runner writes and what the calibrator reads,
so the repair belongs at the log-emission end or in an adapter, not in the
curve-fitting.

NOT FIXED HERE, AND THE REASON IS THE EXPERIMENT. Changing the composer's
budgets between run 1 and run 2 would destroy the matched pair the 2 runs exist
to form -- run 2 differs from run 1 by exactly 1 flag by design. The founder's
instruction to apply outstanding fixes was given BEFORE the runs; applying this
one BETWEEN them would make neither run attributable. It is recorded for after
run 2.
"""
from __future__ import annotations

import ast
import json
import pathlib
import sys
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
TARGET = "update_coherence_budgets_from_experiments"
RUN1 = REPO / ("bench/logs/free_run1_directive_whole_20261015T061123Z"
               "_20261015T061124Z")


def _py_files():
    for root in ("bench", "scripts"):
        for p in (REPO / root).rglob("*.py"):
            if "/logs/" in str(p):
                continue
            yield p


def layer1_no_caller() -> dict:
    calls, imports, text_refs = [], [], []
    for p in _py_files():
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if TARGET in src:
            text_refs.append(str(p.relative_to(REPO)))
        try:
            m = ast.parse(src)
        except SyntaxError:
            continue
        for n in ast.walk(m):
            if isinstance(n, ast.Call):
                name = getattr(n.func, "id", None) or getattr(n.func, "attr", None)
                if name == TARGET:
                    calls.append(f"{p.relative_to(REPO)}:{n.lineno}")
            if isinstance(n, ast.ImportFrom):
                for a in n.names:
                    if a.name == TARGET:
                        imports.append(f"{p.relative_to(REPO)}:{n.lineno}")
    return {"ast_call_sites": calls, "ast_imports": imports,
            "files_mentioning_it_textually": text_refs}


def layer2_no_persistence() -> dict:
    """EXECUTED, not grepped. Mutate the dict in one process, exit, read it in a
    fresh one. A text search for a writer is a heuristic and the first version of
    this check was one: it matched any module that merely NAMED the dict and also
    happened to write some unrelated file, which included this script itself.
    """
    import subprocess

    src = (REPO / "bench/cdsfl_registry/composer.py").read_text(encoding="utf-8")
    m = ast.parse(src)
    literal, lineno = False, None
    for n in ast.walk(m):
        tgt = None
        if isinstance(n, ast.AnnAssign):
            tgt = getattr(n.target, "id", "")
        elif isinstance(n, ast.Assign) and n.targets:
            tgt = getattr(n.targets[0], "id", "")
        if tgt == "MODEL_COHERENCE_BUDGETS":
            literal = isinstance(n.value, ast.Dict)
            lineno = n.lineno

    SENTINEL = 0.123456
    mutate = (
        "import sys; sys.path.insert(0, %r)\n"
        "from bench.cdsfl_registry import composer as C\n"
        "C.MODEL_COHERENCE_BUDGETS['opus_4_6'] = %r\n"
        "print(C.MODEL_COHERENCE_BUDGETS['opus_4_6'])\n"
    ) % (str(REPO), SENTINEL)
    reread = (
        "import sys; sys.path.insert(0, %r)\n"
        "from bench.cdsfl_registry import composer as C\n"
        "print(C.MODEL_COHERENCE_BUDGETS['opus_4_6'])\n"
    ) % (str(REPO),)

    r1 = subprocess.run([sys.executable, "-c", mutate],
                        capture_output=True, text=True, cwd=REPO)
    r2 = subprocess.run([sys.executable, "-c", reread],
                        capture_output=True, text=True, cwd=REPO)
    in_proc = r1.stdout.strip()
    after = r2.stdout.strip()
    survived = (in_proc == after)

    return {
        "defined_as_source_literal": literal,
        "defined_at_line": lineno,
        "value_after_mutation_in_process": in_proc,
        "value_in_a_fresh_process": after,
        "mutation_survived_the_process": survived,
        "method": "executed in 2 subprocesses, not inferred from a text search",
    }


def layer3_shape_mismatch() -> dict:
    from bench.cdsfl_registry import composer as C
    from statsmodels.stats.proportion import proportion_confint
    from scipy import stats as sstats

    before = dict(C.MODEL_COHERENCE_BUDGETS)
    out: dict = {"source_literal": before}

    if not RUN1.exists():
        out["run1_present"] = False
        return out
    out["run1_present"] = True

    on_real = C.calibrate_coherence_thresholds(RUN1)
    out["returned_on_run1"] = on_real
    out["identical_to_literal"] = on_real == before

    have = total = 0
    for p in sorted(RUN1.rglob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for e in (d if isinstance(d, list) else [d]):
            if isinstance(e, dict):
                total += 1
                if "model" in e and "chars" in e:
                    have += 1
    out["entries_with_model_and_chars"] = [have, total]
    lo, hi = proportion_confint(have, total, method="wilson")
    lob, hib = proportion_confint(have, total, method="beta")
    out["shape_rate_wilson"] = [lo, hi]
    out["shape_rate_clopper_pearson"] = [lob, hib]
    # cross-check CP upper for k=0 by first principles: 1 - 0.025**(1/n)
    cp_hi_exact = 1.0 - 0.025 ** (1.0 / total) if total else None
    out["cp_upper_cross_check"] = cp_hi_exact
    out["cp_upper_agrees"] = (abs(hib - cp_hi_exact) < 1e-9) if total else None

    # Does the calibrator work when fed the documented shape?
    rows = []
    for chars, nfind in [(1000, 10), (2000, 20), (3000, 30), (4000, 12),
                         (5000, 8), (6000, 4), (7000, 2), (8000, 1)]:
        rows.append({"model": "opus_4_6", "chars": chars,
                     "response": "x" * (nfind * 400), "findings": nfind})
    with tempfile.TemporaryDirectory() as td:
        f = pathlib.Path(td) / "fixture.json"
        f.write_text(json.dumps(rows))
        on_fixture = C.calibrate_coherence_thresholds(f.parent)
    out["returned_on_fixture"] = on_fixture
    out["calibrator_works_when_fed_its_shape"] = (
        on_fixture.get("opus_4_6") != before.get("opus_4_6")
    )
    out["pure_call_left_module_dict_untouched"] = dict(C.MODEL_COHERENCE_BUDGETS) == before
    return out


def main() -> int:
    l1 = layer1_no_caller()
    l2 = layer2_no_persistence()
    l3 = layer3_shape_mismatch()

    print("=" * 78)
    print("LAYER 1 — NOTHING CALLS IT")
    print("=" * 78)
    print(f"  ast.Call sites naming it      : {len(l1['ast_call_sites'])} {l1['ast_call_sites']}")
    print(f"  ImportFrom sites importing it : {len(l1['ast_imports'])} {l1['ast_imports']}")
    print(f"  files mentioning it in TEXT   : {len(l1['files_mentioning_it_textually'])}")
    for f in l1["files_mentioning_it_textually"]:
        print(f"      {f}")
    print("  (a grep sees these; an AST walk correctly does not call them callers)")

    print()
    print("=" * 78)
    print("LAYER 2 — IT PERSISTS NOTHING")
    print("=" * 78)
    print(f"  MODEL_COHERENCE_BUDGETS is a source literal : {l2['defined_as_source_literal']}")
    print(f"  defined at composer.py line                 : {l2['defined_at_line']}")
    print(f"  value after mutation, in-process            : {l2['value_after_mutation_in_process']}")
    print(f"  value re-read in a FRESH process            : {l2['value_in_a_fresh_process']}")
    print(f"  the mutation survived the process           : {l2['mutation_survived_the_process']}")
    print(f"  method                                      : {l2['method']}")

    print()
    print("=" * 78)
    print("LAYER 3 — THE RUNS DO NOT EMIT THE SHAPE IT READS")
    print("=" * 78)
    if l3.get("run1_present"):
        have, total = l3["entries_with_model_and_chars"]
        lo, hi = l3["shape_rate_wilson"]
        lob, hib = l3["shape_rate_clopper_pearson"]
        print(f"  entries carrying 'model' AND 'chars' : {have} of {total} = {have/total*100:.4f}%")
        print(f"    Wilson          95% [{lo*100:.4f}%, {hi*100:.4f}%]")
        print(f"    Clopper-Pearson 95% [{lob*100:.4f}%, {hib*100:.4f}%]")
        print(f"    CP upper cross-checked by 1 - 0.025^(1/n): {l3['cp_upper_agrees']}")
        print(f"  returned on run 1   : {l3['returned_on_run1']}")
        print(f"  source literal      : {l3['source_literal']}")
        print(f"  IDENTICAL           : {l3['identical_to_literal']}")
        print()
        print(f"  on a purpose-built fixture in the documented shape:")
        print(f"    {l3['returned_on_fixture']}")
        print(f"    calibrator moves off the literal : {l3['calibrator_works_when_fed_its_shape']}")
        print(f"    so the ALGORITHM is sound; the gap is a SCHEMA MISMATCH")
        print(f"  pure call left the module dict untouched: {l3['pure_call_left_module_dict_untouched']}")

    inert = (
        not l1["ast_call_sites"] and not l1["ast_imports"]
        and l2["defined_as_source_literal"]
        and not l2["mutation_survived_the_process"]
        and l3.get("identical_to_literal") is True
        and l3.get("calibrator_works_when_fed_its_shape") is True
    )
    print()
    print("=" * 78)
    print("VERDICT")
    print("=" * 78)
    print(f"  inert on all 3 layers, algorithm sound: {inert}")
    print("  CONSEQUENCE: the programme's coherence_budget_recalibration")
    print("  measurement CANNOT be satisfied by running the 2 free runs, and the")
    print("  coherence pruner's lean-versus-full ablation arm therefore stays")
    print("  un-runnable until the schema gap is closed.")
    print("  NOT FIXED BETWEEN THE RUNS: it would change the composer and destroy")
    print("  the matched pair that run 1 and run 2 exist to form.")

    dest = REPO / "experimental_notes/evidence/coherence_recalibration_inert_2026-10-15.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"layer1": l1, "layer2": l2, "layer3": l3,
                                "inert_on_all_three": inert}, indent=2) + "\n")
    print(f"  evidence -> {dest.relative_to(REPO)}")
    return 0 if inert else 1


if __name__ == "__main__":
    sys.exit(main())
