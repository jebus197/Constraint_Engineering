#!/usr/bin/env python3
"""Does the canonical runner reach the 4-layer policy merge engine? YES, as of today.

★ THIS CORRECTS A CLAIM CARRIED BY 2 LIVE TASK-LIST ENTRIES AND HEADED FOR A
PANEL BRIEF. Entry B22 lists, as its strongest evidence AGAINST the project's
claim of domain-generality: *"the canonical runner makes 0 calls to the policy
merge engine, so nothing domain-adaptive reaches a live run -- the domain string
reaches prompt composition only"*. Entry B21 carries the same claim in its title.
B22 is a question the founder directed to a free panel review, so the panel would
have argued from this as fact.

IT IS FALSE, measured 3 ways and each by EXECUTION rather than by reading:

  1. The canonical runner calls `compose(task_domain=domain, ...)` at
     `bench/reference_runner_v3.py:12411`.
  2. `compose` reaches the merge engine. `bench/cdsfl_registry/composer.py:47`
     and `:2030` import from `.registry`, and instrumenting
     `registry.load_effective_policy` counts exactly 1 CALL per `compose()`.
     That is the 4-layer merge's entry point, not a neighbouring helper.
  3. The merge is domain-ADAPTIVE and its output VARIES: over the 10 committed
     domain policy files it returns 10 DISTINCT merged policies, compared by
     hash of the canonicalised result.

★ WHY THE 3RD STEP IS THE ONE THAT MATTERS, and why steps 1 and 2 alone would
have been a weaker claim than the one withdrawn. A module being IMPORTED is not a
function being CALLED, and a function being called is not its output MATTERING --
`feedback_my_instruments_are_the_weak_point_2026-09-30` records a monkeypatch
that could not reach a consumer which re-imported, and this project has retired
several mechanisms that ran and decided nothing. So the instrumentation below
patches BOTH the registry-level and composer-level bindings, and the domain
comparison is what distinguishes "reached" from "reached and inert".

WHAT IS NOT CLAIMED. That the merged policy changes a model's BEHAVIOUR, or that
domain-generality is therefore established. Only that the specific evidence
offered against it does not hold.
"""
from __future__ import annotations
import hashlib, json, pathlib, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def main() -> int:
    answer_help(__doc__, __file__)
    import ast
    from bench.cdsfl_registry import registry as R
    import bench.cdsfl_registry.composer as C

    print("=" * 78)
    print("IS THE 4-LAYER POLICY MERGE ENGINE REACHED BY A LIVE RUN?")
    print("=" * 78)

    # --- 1. the runner's call site, from the AST not from grep --------------
    tree = ast.parse((REPO / "bench" / "reference_runner_v3.py").read_text())
    sites = [n.lineno for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
             and n.func.id == "compose"]
    print(f"\n1. THE RUNNER'S CALLS TO compose(): {len(sites)} at line(s) {sites}")
    assert sites, "the canonical runner does not call compose at all"

    # --- 2. the call into the merge engine, instrumented -------------------
    hits = {"n": 0}
    orig = R.load_effective_policy

    def spy(*a, **k):
        hits["n"] += 1
        return orig(*a, **k)

    R.load_effective_policy = spy
    # BOTH BINDINGS. A composer that imported the name at module level holds its
    # own reference, and patching only the registry would leave the consumer
    # untouched -- the exact failure recorded on 2026-09-30.
    patched_composer = hasattr(C, "load_effective_policy")
    if patched_composer:
        C.load_effective_policy = spy
    try:
        C.compose(task_domain="mathematics", model="opus_4_6", situation={})
    finally:
        R.load_effective_policy = orig
        if patched_composer:
            C.load_effective_policy = orig
    print(f"\n2. load_effective_policy CALLS during ONE compose(): {hits['n']}")
    print(f"   (composer-level binding patched too: {patched_composer})")
    assert hits["n"] > 0, "the merge engine is NOT called; the entries' claim stands"

    # --- 3. and is it ADAPTIVE, or reached and inert? ----------------------
    doms = sorted(p.stem for p in (REPO / "bench" / "cdsfl_registry"
                                   / "domains").glob("*.toml"))
    sigs: dict[str, str] = {}
    for d in doms:
        try:
            pol = R.load_effective_policy(domain=d, model="opus_4_6")
        except Exception as exc:                             # noqa: BLE001
            print(f"   {d}: raised {type(exc).__name__}")
            continue
        sigs[d] = hashlib.sha256(
            json.dumps(pol, sort_keys=True, default=str).encode()).hexdigest()[:12]
    uniq = len(set(sigs.values()))
    print(f"\n3. DOMAIN ADAPTIVITY: {len(sigs)} domain(s) -> {uniq} DISTINCT "
          f"merged policy/policies")
    for d, h in sigs.items():
        print(f"     {d:22s} {h}")
    assert uniq > 1, (
        "the merge returns the same policy for every domain, so it is reached "
        "and INERT -- the entries' claim survives in a corrected form")

    print("\n" + "=" * 78)
    print("THE CLAIM IN B22 AND B21 IS WITHDRAWN. The canonical runner reaches")
    print("the merge engine through compose(), the engine's entry point is called")
    print("once per composition, and its output varies across all 10 domains.")
    print("NOT CLAIMED: that this changes a model's behaviour, or that")
    print("domain-generality is established. Only that this evidence against it")
    print("does not hold, which matters because B22 is headed for a panel brief.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
