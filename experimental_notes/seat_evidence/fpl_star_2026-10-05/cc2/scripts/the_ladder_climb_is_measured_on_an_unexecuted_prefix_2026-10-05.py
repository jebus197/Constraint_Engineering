# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fpl_star_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 6cf2a153b4b40bdba753c81ba1a2a901e5ee0c7e7f9bd9f1c7d2dbfc18dd7426
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The rung budget was raised to make a MIXED PREFIX appear. The prefix is not executed.

WHAT THIS MEASURES, and why the distinction decides the repair.

On 2026-10-05 the simulated runner was given `routing_max_rungs=4` so that "6 of 6
source seats get a climb between two different models". That figure is computed by
slicing `rank_falsifier_writers(...)[:4]` -- the list of rungs the ladder is PERMITTED
to try. It is not the sequence the ladder DISPATCHES. `resolve_via_routing` stops on
the first CONFIRMED, so a rung is dispatched only if every rung above it failed to
produce a CONFIRMED verdict from the re-verifier.

That is the same execution semantics CC1 used to falsify the fable seat's proposed
seat remap ("rung 1 is the STRONGEST writer and resolve_via_routing stops at the first
CONFIRMED"). This script applies it to CC1's own repair.

THREE THINGS IT DERIVES, each by execution and none by reading source text.

1. PARITY. No real experiment config sets `routing_max_rungs`. Every real run
   therefore uses the `RunnerConfig` default. The simulated runner setting 4 makes
   rungs 3 and 4 reachable in simulation and structurally unreachable in every run
   the simulation is compared against. The config block that was edited is itself
   headed "PARITY WITH THE REAL exp45 CONFIG ... Every value below differed, and each
   difference let the simulation behave in a way the run it is compared against
   structurally could not". The edit is a new instance of the class that block exists
   to remove.

2. EXECUTED CLIMB PROBABILITY. `resolve_via_routing` is CALLED with a recording
   `resolve_fn` and a `reverify_fn` that CONFIRMS at a chosen rung, so the models
   actually dispatched are observed rather than inferred. The probability that the
   dispatched sequence spans more than one model is then computed from the per-vendor
   rates `bench/routing.py` quotes in its own header, under BOTH available rate
   models, because the two disagree about magnitude and agree about direction.

3. THE BUDGET-2 CEILING. Exhaustively, over all 2**6 two-model seat maps: no map
   whatever reaches 6 of 6 mixed AND 6 of 6 correctly-directed at a budget of 2. The
   ceiling is 5 of 6 mixed with all 6 directed, and it is attained by a monotone map.
   So CC1 was right that the 6-of-6 figure needs a larger budget. The measurement
   below is about what that buys once execution is accounted for.

HONEST LIMIT ON (2). Neither rate model is a residual-resolution rate per rung for an
arbitrary finding; one is a first-pass confirm rate and the other is a 7-point
residual measurement. They are the only committed numbers this project has, they are
the numbers `bench/routing.py` itself cites, and they bracket the answer. The ratio,
not the level, is what the repair turns on, and the ratio is stable across both.

Read-only. Dispatches nothing. Exits 1 if any figure fails to reproduce.
"""
from __future__ import annotations

import argparse
import ast
import itertools
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

SEATS = ["CC2-SIM", "ChatGPT-SIM", "Codex-SIM", "DeepSeek-SIM",
         "Gemini-SIM", "Fable-SIM"]

#: Exp-42 per-vendor FIRST-PASS falsifier-confirm rates, quoted verbatim in
#: `bench/routing.py`'s header comment (Codex 90% / CC2 75% / ChatGPT 67% /
#: Gemini 80% / DeepSeek 28%). `Fable` postdates Exp 42 and has no rate; the pool
#: mean is used and is flagged as such.
FIRST_PASS = {"Codex": 0.90, "CC2": 0.75, "ChatGPT": 0.67,
              "Gemini": 0.80, "DeepSeek": 0.28}
FIRST_PASS["Fable"] = sum(FIRST_PASS.values()) / len(FIRST_PASS)

#: Exp-42 RESIDUAL-RESOLUTION rates, the measurement `bench/routing.py` actually
#: validated the ladder on: rung 1 (gpt-5.5/Codex) resolved 6 of 7 of the hardest
#: residuals, rung 2 (CC2) resolved the remaining 1 of 1. Rungs 3+ were never
#: reached, so no rate exists for them; the first-pass rate is used there and the
#: substitution is stated rather than hidden.
RESIDUAL = dict(FIRST_PASS, Codex=6 / 7, CC2=1.0)


def _base(m: str) -> str:
    return m[:-4] if m.endswith("-SIM") else m


def _parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=str(REPO))
    return ap.parse_args(argv)


# ---------------------------------------------------------------- section 1
def real_configs_setting_the_budget(repo: pathlib.Path):
    """Every config-shaped JSON in the tree, and which of them pin the budget.

    Archived panel records and seat-evidence copies are excluded: they are
    transcripts of reviews, not configs a runner was launched with.
    """
    scanned, hits = 0, []
    for p in repo.rglob("*.json"):
        sp = str(p)
        if any(x in sp for x in (".pytest_cache", "panel_records", "seat_evidence")):
            continue
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, dict) and ("experiment_name" in d or "routing_enabled" in d):
            scanned += 1
            if "routing_max_rungs" in d:
                hits.append(str(p.relative_to(repo)))
    return scanned, hits


def dataclass_default(repo: pathlib.Path) -> int:
    """RunnerConfig.routing_max_rungs' declared default, read by AST."""
    tree = ast.parse((repo / "bench" / "reference_runner_v3.py").read_text(encoding="utf-8"))
    for n in ast.walk(tree):
        if isinstance(n, ast.ClassDef) and n.name == "RunnerConfig":
            for s in n.body:
                if (isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name)
                        and s.target.id == "routing_max_rungs"):
                    return ast.literal_eval(s.value)
    raise SystemExit("RunnerConfig has no routing_max_rungs field")


def launcher_budget(repo: pathlib.Path):
    """Whatever the simulated launcher pins, read by AST from its RunnerConfig call.

    Returns None when the launcher passes no keyword, which is the parity state.
    A non-literal (an expression reading argparse) is returned as its AST dump.
    """
    tree = ast.parse((repo / "bench" / "tools" / "run_simulated_experiment.py")
                     .read_text(encoding="utf-8"))
    found = None
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and (getattr(n.func, "attr", None)
                                        or getattr(n.func, "id", None)) == "RunnerConfig":
            for kw in n.keywords:
                if kw.arg == "routing_max_rungs":
                    try:
                        found = ast.literal_eval(kw.value)
                    except ValueError:
                        found = "<expression, not a literal>"
    return found


# ---------------------------------------------------------------- section 2
def executed_models(source: str, budget: int, smap: dict, confirm_at):
    """CALL resolve_via_routing and return the models it actually dispatched.

    ``confirm_at`` is the 1-based rung whose falsifier the re-verifier CONFIRMS,
    or None for "no rung ever confirms" (the HIL path).
    """
    from bench.routing import rank_falsifier_writers, resolve_via_routing
    rungs = rank_falsifier_writers(SEATS, exclude=(source,))
    seen, n = [], {"i": 0}

    def resolve_fn(model, finding):
        seen.append(model)
        return "code"

    def reverify_fn(code):
        n["i"] += 1
        return "CONFIRMED" if confirm_at == n["i"] else "REFUTED"

    resolve_via_routing({"id": "C0001"}, rungs, resolve_fn, reverify_fn,
                        max_rungs=budget)
    return [smap.get(m, "opus") for m in seen]


def p_executed_climb(budget: int, smap: dict, rate: dict) -> float:
    """P(the DISPATCHED sequence spans more than one model), averaged over a
    uniform source seat, with per-rung confirm events treated as independent."""
    from bench.routing import rank_falsifier_writers
    total = 0.0
    for s in SEATS:
        rungs = rank_falsifier_writers(SEATS, exclude=(s,))[:budget]
        models = [smap.get(r, "opus") for r in rungs]
        k = next((i for i, m in enumerate(models) if m != models[0]), None)
        if k is None:
            continue                      # no transition exists in this prefix
        p = 1.0
        for r in rungs[:k]:               # every rung above it must have failed
            p *= (1.0 - rate[_base(r)])
        total += p
    return total / len(SEATS)


# ---------------------------------------------------------------- section 3
def budget_two_ceiling():
    """Exhaustive over all 2**6 two-model seat maps at a budget of 2."""
    from bench.routing import rank_falsifier_writers, DEFAULT_FALSIFIER_STRENGTH
    order = list(DEFAULT_FALSIFIER_STRENGTH)

    def directed(ms):
        return all(not (ms[i] == "fable" and "opus" in ms[i + 1:])
                   for i in range(len(ms)))

    def monotone(sm):
        ranked = [sm[m] for m in sorted((s for s in SEATS if _base(s) in order),
                                        key=lambda s: order.index(_base(s)))]
        return all(not (ranked[i] == "fable" and "opus" in ranked[i + 1:])
                   for i in range(len(ranked)))

    rows = []
    for bits in itertools.product(("opus", "fable"), repeat=len(SEATS)):
        sm = dict(zip(SEATS, bits))
        pre = {s: [sm[x] for x in rank_falsifier_writers(SEATS, exclude=(s,))[:2]]
               for s in SEATS}
        rows.append((sum(len(set(v)) > 1 for v in pre.values()),
                     sum(directed(v) for v in pre.values()),
                     monotone(sm), sm))
    return rows


def main(argv=None) -> int:
    args = _parse_args(argv)
    repo = pathlib.Path(args.repo).resolve()
    from bench.tools.sim_dispatch_shim import DEFAULT_LADDER
    from bench.routing import rank_falsifier_writers
    bad = []

    print("THE LADDER CLIMB WAS MEASURED ON AN UNEXECUTED PREFIX")
    print("=" * 78)

    # ---- 1
    scanned, hits = real_configs_setting_the_budget(repo)
    dflt = dataclass_default(repo)
    pinned = launcher_budget(repo)
    print("\n1. PARITY -- does any REAL run reach rungs 3 and 4?")
    print(f"   config-shaped JSON files scanned                : {scanned}")
    print(f"   of those pinning routing_max_rungs              : {len(hits)} {hits}")
    print(f"   RunnerConfig.routing_max_rungs default          : {dflt}")
    print(f"   simulated launcher pins                         : {pinned!r}")
    if len(hits) == 0 and isinstance(pinned, int) and pinned > dflt:
        print(f"   => rungs {dflt + 1}..{pinned} are reachable ONLY in simulation. The "
              f"simulated\n      run's routing and HIL statistics are not comparable "
              f"to the real run\n      the config block says it is compared against.")
    else:
        print("   => PARITY HOLDS or is explicit: the launcher does not silently "
              "deepen\n      the ladder beyond what every real config reaches.")
    if scanned < 50:
        bad.append(f"only {scanned} configs scanned; refusing to report 0 from a "
                   f"population that may not have been read")

    # ---- 2
    print("\n2. EXECUTION -- which models does resolve_via_routing actually DISPATCH?")
    print("   (CALLED, not inferred; the rung whose falsifier CONFIRMS is varied)")
    print(f"   source seat CC2-SIM, shipped seat map")
    print(f"   {'confirms at rung':<18} {'budget 2':<34} {'budget 4'}")
    for confirm_at in (1, 2, 3, 4, None):
        a = executed_models("CC2-SIM", 2, DEFAULT_LADDER, confirm_at)
        b = executed_models("CC2-SIM", 4, DEFAULT_LADDER, confirm_at)
        print(f"   {str(confirm_at):<18} {str(a):<34} {b}")
    print("   => at budget 4 the dispatched sequence is mixed ONLY when rungs 1 and 2")
    print("      both failed to confirm. At budget 2 it is never mixed.")

    k1 = {m: ("opus" if _base(m) == "Codex" else "fable") for m in SEATS}
    cands = {
        "shipped map, budget 2 (state before 2026-10-05)": (2, DEFAULT_LADDER),
        "shipped map, budget 4 (CC1's repair tonight)":     (4, DEFAULT_LADDER),
        "Codex-only-on-opus map, budget 2":                 (2, k1),
    }
    print(f"\n   {'candidate':<48} {'mixed prefix':<14} {'P(exec) 1st-pass':<18} "
          f"{'P(exec) residual'}")
    results = {}
    for name, (b, sm) in cands.items():
        mixed = sum(1 for s in SEATS
                    if len({sm.get(x, "opus")
                            for x in rank_falsifier_writers(SEATS, exclude=(s,))[:b]}) > 1)
        pf = p_executed_climb(b, sm, FIRST_PASS)
        pr = p_executed_climb(b, sm, RESIDUAL)
        results[name] = (mixed, pf, pr)
        print(f"   {name:<48} {str(mixed) + ' of 6':<14} {pf:<18.4%} {pr:.4%}")
    cc1 = results["shipped map, budget 4 (CC1's repair tonight)"]
    alt = results["Codex-only-on-opus map, budget 2"]
    rr = "infinite (denominator 0)" if cc1[2] == 0 else f"{alt[2] / cc1[2]:.2f}x"
    print(f"\n   ratio (Codex-only-on-opus @2) / (shipped @4): "
          f"first-pass {alt[1] / cc1[1]:.2f}x, residual {rr}")
    print("   => the 6-of-6 figure is a property of the PERMITTED prefix. On the")
    print("      DISPATCHED sequence, raising the budget buys a climb in a few per")
    print("      cent of routed criticals, and under the residual rates Exp 42")
    print("      actually measured (rung 2 resolved 1 of 1) it buys none at all.")
    print("   NOT A RECOMMENDATION TO ADOPT THE THIRD MAP: it moves 2 of 6 seats off")
    print("   the strong model, so it wins on ladder rehearsal and LOSES on per-seat")
    print("   capability fidelity. It does not dominate, so it does not displace the")
    print("   shipped map under the founder's removal standard. It is here to size")
    print("   what the budget change actually bought.")
    if not (0.0 <= cc1[1] <= 0.10):
        bad.append(f"budget-4 executed-climb probability {cc1[1]:.4%} is outside the "
                   f"range this script was written against")

    # ---- 3
    rows = budget_two_ceiling()
    both = [r for r in rows if r[0] == 6 and r[1] == 6]
    ceiling = max(r[0] for r in rows if r[1] == 6 and r[2])
    best = sorted((r for r in rows if r[0] == ceiling and r[1] == 6 and r[2]),
                  key=lambda r: -p_executed_climb(2, r[3], FIRST_PASS))
    print(f"\n3. THE BUDGET-2 CEILING -- exhaustive over all {len(rows)} two-model maps")
    print(f"   maps with 6 of 6 mixed AND 6 of 6 correctly directed : {len(both)}")
    print(f"   best monotone map, all 6 directed                    : "
          f"{ceiling} of 6 mixed")
    print(f"   attaining maps ({len(best)}), best first by executed probability:")
    for _, _, _, sm in best[:3]:
        print(f"      P(exec)={p_executed_climb(2, sm, FIRST_PASS):.4%}  {dict(sm)}")
    print("   DERIVED: 6 of 6 at budget 2 would need rank1 != rank2 AND rank2 != rank3,")
    print("   i.e. rank1 == rank3 != rank2, which is NON-monotone in the strength")
    print("   order. With 2 models the monotone ceiling at budget 2 is 5 of 6. CC1 is")
    print("   therefore RIGHT that 6 of 6 needs a deeper budget, and that is not the")
    print("   question the repair turns on.")
    if len(both) != 0:
        bad.append("a 6-of-6 map at budget 2 was found; section 3's derivation is stale")
    if ceiling != 5:
        bad.append(f"monotone ceiling at budget 2 is {ceiling}, not 5; derivation stale")

    print("\n" + "=" * 78)
    if bad:
        print("STALE / FAILED TO REPRODUCE:")
        for b in bad:
            print(f"  *** {b}")
        return 1
    print("every figure above reproduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
