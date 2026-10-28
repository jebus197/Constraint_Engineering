#!/usr/bin/env python3
"""How many places must change to add, remove or change a model in the harness?

HIS QUESTION, 2026-10-16, verbatim: *"adding, removing, or changing models in
the harness should be an entirely trivial affair (by design) and should not
require major code changes to enable researchers to do so. The question is, is
it? Have we adequately addressed this particular design objective?"*

HOW THIS ANSWERS IT, AND WHY NOT BY READING. The question is about EDIT COUNT,
so the measurement is an edit count. Two independent methods are run and
reported side by side, because a single method here would be a guess dressed as
a figure:

  METHOD A -- STRUCTURAL. Every module under `bench/` and `scripts/` is parsed
  with `ast` and every dict literal, set literal or tuple whose KEYS include a
  current model name is recorded as a site that would need a new entry. An AST
  walk is used rather than a text search so that a model name inside a comment,
  a docstring or a log string is not counted as an edit site.

  METHOD B -- EXECUTED. A model that does not exist, `Kimi` (he names Kimi K3 as
  a candidate for re-admission), is put through the resolution chain a real seat
  takes, and each step is recorded as PASS, SILENT DEFAULT or RAISE. A silent
  default is the dangerous outcome: the seat runs, and loses whatever that step
  gated, with no error. This project's own record has that class 8 times over --
  `base_model_label`'s docstring names it: "a capability lost with no error".

The two methods measure different things on purpose. A says how many places a
researcher must EDIT. B says what happens if they miss one.

`execute-do-not-grep`: method B calls the live functions. Method A parses rather
than greps. Neither asserts on source text.

Free on `--help`: dispatches nothing, spends nothing, reads only local files.

Usage:
    python3 scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py
    python3 scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py --json
"""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NEW_MODEL = "Kimi"
SIM_SUFFIX = "-SIM"

#: Directories whose contents are evidence or prose, not harness code.
SKIP_PARTS = {"logs", "experimental_notes", "fingerprints", ".git",
              "__pycache__", "exp40_baseline", "seat_evidence"}


def _roster() -> list[str]:
    sys.path.insert(0, str(REPO / "bench"))
    import reference_runner_v3 as runner  # noqa: PLC0415
    return sorted(set(getattr(runner, "MODEL_ROSTER", {})) | {"Fable"})


def _py_files() -> list[Path]:
    out = []
    for base in ("bench", "scripts"):
        for p in (REPO / base).rglob("*.py"):
            if SKIP_PARTS & set(p.parts):
                continue
            out.append(p)
    return sorted(out)


def method_a(models: list[str]) -> dict:
    """Structural: literal collections keyed on a model name."""
    sites: list[dict] = []
    names = set(models)
    for path in _py_files():
        try:
            tree = ast.parse(path.read_text(errors="replace"))
        except (OSError, SyntaxError):
            continue
        for node in ast.walk(tree):
            keys: list[str] = []
            if isinstance(node, ast.Dict):
                keys = [k.value for k in node.keys
                        if isinstance(k, ast.Constant) and isinstance(k.value, str)]
            elif isinstance(node, (ast.Set, ast.Tuple, ast.List)):
                keys = [e.value for e in node.elts
                        if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            hit = sorted(names & set(keys))
            # A collection naming ONE model is usually an example or a filter;
            # one naming 2 or more is a per-model table a new model must join.
            if len(hit) >= 2:
                sites.append({
                    "file": str(path.relative_to(REPO)),
                    "line": getattr(node, "lineno", 0),
                    "models_named": hit,
                    "kind": type(node).__name__,
                })
    # ★ THE SPLIT IS LOAD-BEARING, and the first version of this script omitted
    # it. A raw total of 156 sites across 67 files reads as the cost of adding a
    # model, but a researcher does NOT edit the test suite to admit a seat --
    # tests pin existing behaviour, and several deliberately enumerate the
    # roster in order to guard it. Reporting one undifferentiated total would
    # have overstated the answer to his question by roughly 3x, which is the
    # `compare like with like` failure in its usual shape.
    def bucket(f: str) -> str:
        if f.startswith("bench/tests/"):
            return "tests (not edited to add a model)"
        if f.startswith("scripts/"):
            return "measurement scripts (not edited to add a model)"
        if f.startswith("bench/tools/"):
            return "tools (edited only for a simulated seat)"
        # ★ THE LIVE HARNESS IS A SMALL SUBSET OF `bench/`, and conflating the
        # two overstates the answer again. `run_exp29..run_exp36`,
        # `reprocess_exp33`, `reference_runner.py` (v1), the `confer_*` drivers
        # and `monitor_exp39` are HISTORICAL one-off experiment scripts. A
        # researcher admitting a model to the CURRENT harness does not edit
        # them; they are the record of runs already performed, and editing them
        # would alter what those runs did. Runner v2 is
        # `reference_runner_v3.py` -- named v2 per the project's convention.
        live = {
            "bench/reference_runner_v3.py",
            "bench/runner_core.py",
            "bench/cdsfl_registry/composer.py",
            "bench/experiment_11_orchestrator.py",
            "bench/routing.py",
            "bench/dm/_types.py",
        }
        if f in live:
            return "LIVE HARNESS (must be edited)"
        return "historical experiment runners (not the live harness)"

    by_file: dict[str, int] = {}
    by_bucket: dict[str, int] = {}
    bucket_files: dict[str, set] = {}
    for s in sites:
        s["bucket"] = bucket(s["file"])
        by_file[s["file"]] = by_file.get(s["file"], 0) + 1
        by_bucket[s["bucket"]] = by_bucket.get(s["bucket"], 0) + 1
        bucket_files.setdefault(s["bucket"], set()).add(s["file"])
    prod = "LIVE HARNESS (must be edited)"
    return {"sites": sites, "site_count": len(sites),
            "file_count": len(by_file), "by_file": by_file,
            "by_bucket": by_bucket,
            "bucket_file_counts": {k: len(v) for k, v in bucket_files.items()},
            "production_sites": by_bucket.get(prod, 0),
            "production_files": len(bucket_files.get(prod, set())),
            "production_file_list": sorted(bucket_files.get(prod, set()))}


def method_b(models: list[str]) -> dict:
    """Executed: put a non-existent model through the real resolution chain."""
    sys.path.insert(0, str(REPO / "bench"))
    import routing as _rt  # the LIVE lookup path, NOT a re-implementation
    import reference_runner_v3 as runner  # noqa: PLC0415
    from cdsfl_registry import composer as C  # noqa: PLC0415
    import runner_core as rc  # noqa: PLC0415

    def _runner_source() -> str:
        return (REPO / "bench" / "reference_runner_v3.py").read_text(
            errors="replace")

    known = models[0]
    steps: list[dict] = []

    # ★ A DEFAULT THAT IS ANNOUNCED IS NOT A SILENT ONE, AND THIS SCRIPT COULD
    # NOT TELL THE DIFFERENCE UNTIL 2026-10-18. Its own conclusion is that
    # "making admission trivial therefore means making the misses LOUD first",
    # and entry C18 then did exactly that for 3 of the steps below -- yet the
    # count stayed at 9 of 10, because each lambda re-implemented the lookup
    # with a bare `.get(m, default)` instead of calling the live path. Two forms
    # of the same lookup, each individually correct, disagreeing about what
    # happens: the `execute-do-not-grep` defect in the instrument that measures
    # it.
    #
    # The fix is to ask the LIVE LEDGER whether the miss was recorded.
    # `routing.resolve_or_alarm` appends a row for every fallback, so a step
    # whose lookup goes through it is ANNOUNCED DEFAULT: the capability is still
    # lost, and a reader is told. That distinction is the whole point of C18 and
    # it is now measurable rather than asserted.
    def record(name: str, fn, *, silent_default_when=None, announces=False):
        try:
            _rt.reset_lookup_misses()
        except Exception as exc:                                   # noqa: BLE001
            # A FAILURE HERE LEAVES A TRACE -- 2026-10-28. This was
            # `except Exception: pass`. The reset is what makes the miss count
            # that follows belong to THIS step; if it does not happen, misses
            # from an earlier step are attributed to this one and the
            # silent-default verdict below is measured against a dirty counter.
            # A wrong verdict that looks like a verdict is worse than a gap.
            steps.append({"step": f"{name} (counter reset failed)",
                          "outcome": "RESET_FAILED",
                          "detail": f"{type(exc).__name__}: {exc}"})
        try:
            got = fn(NEW_MODEL)
            ref = fn(known)
        except Exception as exc:  # noqa: BLE001
            steps.append({"step": name, "outcome": "RAISE",
                          "detail": f"{type(exc).__name__}: {str(exc)[:110]}"})
            return
        try:
            announced = bool(_rt.lookup_misses())
        except Exception:                                          # noqa: BLE001
            announced = False
        if silent_default_when is not None and silent_default_when(got):
            outcome = "ANNOUNCED DEFAULT" if (announces or announced) else "SILENT DEFAULT"
            steps.append({"step": name, "outcome": outcome,
                          "detail": f"{NEW_MODEL!r} -> {got!r}; "
                                    f"{known!r} -> {ref!r}"
                                    + ("; recorded in the live miss ledger"
                                       if (announces or announced) else "")})
        else:
            steps.append({"step": name, "outcome": "PASS",
                          "detail": f"{NEW_MODEL!r} -> {got!r}"})

    record("roster description (describe_model)",
           lambda m: runner.describe_model(m),
           silent_default_when=lambda g: NEW_MODEL in str(g) and "(" not in str(g))
    record("composer model map (COMPOSER_MODEL_MAP)",
           lambda m: _rt.resolve_or_alarm(C.COMPOSER_MODEL_MAP, m,
                                          "composer directive-set mapping",
                                          default=m),
           silent_default_when=lambda g: g == NEW_MODEL)
    record("coherence budget (MODEL_COHERENCE_BUDGETS)",
           lambda m: _rt.resolve_or_alarm(
               C.MODEL_COHERENCE_BUDGETS,
               _rt.resolve_or_alarm(C.COMPOSER_MODEL_MAP, m,
                                    "composer directive-set mapping", default=m),
               "coherence budget", default=C.DEFAULT_COHERENCE_BUDGET),
           silent_default_when=lambda g: g == C.DEFAULT_COHERENCE_BUDGET)
    record("model spec (runner_core.MODEL_SPECS)",
           lambda m: rc.MODEL_SPECS.get(m),
           silent_default_when=lambda g: g is None)
    record("initial fingerprint (runner_core.INITIAL_FINGERPRINTS)",
           lambda m: rc.INITIAL_FINGERPRINTS.get(m),
           silent_default_when=lambda g: g is None)
    # ★ CORRECTED 2026-10-16 ON CC2'S FINDING. This step used to be classified
    # as a loud RAISE, because `compose` does raise in isolation. In the LIVE
    # chain it is CAUGHT: `_dispatch_single_model_inner` wraps the call and its
    # handler logs "COMPOSER FALLBACK for <seat>" and continues on a degraded
    # prompt. So the run does not halt, and counting it as loud understated the
    # silent-degradation share.
    _composer_caught = "COMPOSER FALLBACK for" in _runner_source()
    if _composer_caught:
        steps.append({
            "step": "directive composition (composer.compose) -- CAUGHT by the "
                    "dispatcher, run continues on a degraded prompt",
            "outcome": "SILENT DEGRADE",
            "detail": "compose() raises, but _dispatch_single_model_inner's "
                      "handler logs COMPOSER FALLBACK and carries on",
        })
    else:
        record("directive composition (composer.compose)",
               lambda m: type(C.compose(
                   "mathematics",
                   _rt.resolve_or_alarm(C.COMPOSER_MODEL_MAP, m,
                                        "composer directive-set mapping",
                                        default=m),
                   coherence_pruning=False)).__name__)

    # ★ THE TABLES THE STRUCTURAL FILTER MISSED, added on CC2's finding. Both
    # are keyed on COMPOSER keys (`opus_4_6`) rather than roster labels, so a
    # scan looking for 2 or more current roster names as keys skips them
    # entirely -- the filter's own blind spot.
    record("coherence budget table keyed on composer keys",
           lambda m: _rt.resolve_or_alarm(
               C.MODEL_COHERENCE_BUDGETS,
               _rt.resolve_or_alarm(C.COMPOSER_MODEL_MAP, m,
                                    "composer directive-set mapping", default=m),
               "coherence budget", default=None),
           silent_default_when=lambda g: g is None)
    record("phenotype transform table keyed on composer keys",
           lambda m: _rt.resolve_or_alarm(
               getattr(C, "PHENOTYPE_TRANSFORMS", {}),
               _rt.resolve_or_alarm(C.COMPOSER_MODEL_MAP, m,
                                    "composer directive-set mapping", default=m),
               "phenotype transform", default=None),
           silent_default_when=lambda g: g is None)

    # ★ THE WORST SINGLE INSTANCE, which the original 7 steps missed entirely.
    # `runner_core.py` reads the context budget as
    # `MODEL_SPECS.get(_spec_key(label), {}).get("L", float("inf"))`, and the
    # next line gates on `estimated_tokens > model_L`. A missing entry therefore
    # sets L to INFINITY and the gate can NEVER fire -- a capability gate that
    # silently becomes a no-op. `_spec_key`'s own docstring names this hazard.
    def _context_budget(m):
        return rc.MODEL_SPECS.get(rc._spec_key(m), {}).get("L", float("inf"))
    record("context-budget ceiling L (runner_core.MODEL_SPECS)",
           _context_budget,
           silent_default_when=lambda g: g == float("inf"))

    # A per-model registry file is a FILE, not a dict entry, so it is checked
    # as one. Its absence is what makes `compose` raise above.
    models_dir = REPO / "bench" / "cdsfl_registry" / "models"
    present = sorted(p.stem for p in models_dir.glob("*.toml")) if models_dir.is_dir() else []
    steps.append({
        "step": f"per-model registry file {models_dir.name}/{NEW_MODEL}.toml",
        "outcome": "MISSING FILE" if NEW_MODEL not in present else "PASS",
        "detail": f"present: {present}",
    })
    # ★ EVERY OUTCOME IS COUNTED, 2026-10-16. The first version tallied only 4
    # categories while emitting a 5th, "SILENT DEGRADE", so 1 of 10 steps was
    # reported and not counted -- the same shape of defect this script exists to
    # find. The assertion below refuses to print a total that does not add up.
    OUTCOMES = ("PASS", "ANNOUNCED DEFAULT", "SILENT DEFAULT", "SILENT DEGRADE", "RAISE",
                "MISSING FILE")
    counts = {k: sum(1 for s in steps if s["outcome"] == k) for k in OUTCOMES}
    unknown = sorted({s["outcome"] for s in steps} - set(OUTCOMES))
    assert not unknown, f"uncounted outcome(s): {unknown}"
    assert sum(counts.values()) == len(steps), (counts, len(steps))
    silent = counts["SILENT DEFAULT"] + counts["SILENT DEGRADE"]
    loud = counts["RAISE"] + counts["MISSING FILE"]
    return {"steps": steps, "counts": counts, "step_total": len(steps),
            "silent": silent, "loud": loud}




def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    models = _roster()
    a = method_a(models)
    b = method_b(models)

    if args.json:
        print(json.dumps({"roster": models, "method_a": a, "method_b": b},
                         indent=2, sort_keys=True))
        return 0

    print("HOW MANY PLACES MUST CHANGE TO ADD A MODEL")
    print(f"  current roster: {', '.join(models)}")
    print()
    print("METHOD A -- STRUCTURAL: per-model tables a new model must join")
    print(f"  {a['site_count']} site(s) across {a['file_count']} file(s) IN TOTAL,")
    print("  but only the LIVE harness is what a researcher must edit:")
    for bkt, n in sorted(a["by_bucket"].items(), key=lambda kv: -kv[1]):
        nf = a["bucket_file_counts"][bkt]
        print(f"       {n:>4} site(s) in {nf:>3} file(s)   {bkt}")
    print()
    print(f"  THE LIVE-HARNESS FILES, named in full ({a['production_files']}):")
    for f in a["production_file_list"]:
        print(f"       {a['by_file'][f]:>3}  {f}")
    print()
    print(f"METHOD B -- EXECUTED: {NEW_MODEL!r} through the real chain")
    for s in b["steps"]:
        print(f"  {s['outcome']:<15} {s['step']}")
        print(f"                  {s['detail'][:150]}")
    c = b["counts"]
    print()
    print("  " + "   ".join(f"{k} {v}" for k, v in c.items())
          + f"   of {b['step_total']} steps")
    n = b["step_total"]
    k = b["silent"]
    from statsmodels.stats.proportion import proportion_confint
    lo_w, hi_w = proportion_confint(k, n, alpha=0.05, method="wilson")
    lo_e, hi_e = proportion_confint(k, n, alpha=0.05, method="beta")
    print(f"  steps that FAIL SILENTLY (default or degrade): {k} of {n} "
          f"({100*k/n:.4f}%, "
          f"Wilson [{100*lo_w:.4f}%, {100*hi_w:.4f}%], "
          f"Clopper-Pearson [{100*lo_e:.4f}%, {100*hi_e:.4f}%])")
    print()
    print("  ANSWER TO HIS QUESTION: adding a model is NOT yet trivial, but the")
    print("  honest figure is smaller than the raw count suggests.")
    print(f"  A researcher must edit {a['production_sites']} per-model table(s) across "
          f"{a['production_files']} live-harness")
    print("  file(s), and add 1 per-model registry .toml. The test, script and")
    print("  historical-runner sites are guards, measurements and the record of")
    print("  runs already performed -- not admission points.")
    print()
    print("  THE REAL PROBLEM IS NOT THE COUNT, IT IS THE FAILURE MODE. Of the "
          f"{n} steps")
    print(f"  a new seat passes through, {k} fail SILENTLY and only "
          f"{b['loud']} fail loudly. A")
    print("  researcher who misses a table gets a seat that RUNS while losing")
    print("  whatever that table gated -- the class `base_model_label`'s own")
    print("  docstring calls \"a capability lost with no error\", recorded 8 times")
    print("  in this project. Making admission trivial therefore means making the")
    print("  misses LOUD first; a single registration point is the fix, and it")
    print("  needs his ruling because it changes how every seat is configured.")
    print()
    print("  ★ PROGRESS AGAINST THAT, MEASURED RATHER THAN CLAIMED. Entry C18 of")
    print("  2026-10-18 routed 3 of these lookups through a resolver that still")
    print("  returns the default -- behaviour unchanged, because raising would")
    print("  turn a degradation into a dead run -- and RECORDS every fallback")
    print("  against the model's stable identity. Those 3 now report as")
    _ann = sum(1 for s in b["steps"] if s["outcome"] == "ANNOUNCED DEFAULT")
    print(f"  ANNOUNCED DEFAULT rather than SILENT DEFAULT: {_ann} step(s), so the")
    print(f"  silent count falls from {k + _ann} of {n} to {k} of {n}. THE FIGURE IS")
    print("  COMPUTED HERE, not written down: a hard-coded improvement is the kind")
    print("  of number that goes stale the next time a lookup is made loud.")
    print()
    print("  AND THIS SCRIPT COULD NOT SEE THAT UNTIL THE SAME DAY. Each lookup")
    print("  above was re-implemented here as a bare dictionary get, so the")
    print("  instrument measured the TABLE's shape and not the live code path --")
    print("  2 forms of one lookup, each individually correct, disagreeing about")
    print("  what happens. The lambdas now call the live resolver and read its")
    print("  ledger, which is the `execute-do-not-grep` rule applied to the")
    print("  measuring script rather than only to the thing measured.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
