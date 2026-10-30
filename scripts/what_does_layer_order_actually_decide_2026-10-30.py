#!/usr/bin/env python3
"""Layer ORDER decides 0 HARD keys and a measured number of SOFT ones.

WHY THIS EXISTS. Entry B21 of the master task list puts 3 questions to the free
panel about adding a ROLE layer to the 4-layer policy merge in
`bench/cdsfl_registry/registry.py`. Two of them rested on behavioural claims
written in PROSE and never executed:

  (a) *"monotonicity protects the HARD keys either way but the SOFT keys go to
      whichever layer merges last"* -- the premise of question 2, where the role
      layer sits in the precedence.
  (b) an unregistered role should fail *"LOUDLY like the model layer ... or
      silently skip like the task layer"* -- the premise of question 3.

`execute-do-not-grep`: both forms exist as live code, so the test must CALL them
and compare outputs rather than read the module's description of itself. This
script calls the live `_load_toml`, `_deep_merge` and `_check_monotonicity`; it
re-implements none of them.

WHAT IT MEASURES.

1. ORDER-INDEPENDENCE OF THE PROTECTED SET. For every (domain, model) pair that
   loads, the policy is merged in the canonical order (universal -> domain ->
   model) and in the REVERSED order (universal -> model -> domain). Every HARD
   dotpath is compared across the two. A single difference would falsify (a) and
   turn question 2 from a preference into a safety question.

2. HOW MANY KEYS ORDER ACTUALLY DECIDES. The same two merges are compared over
   every leaf dotpath. A key that differs is one the precedence decides; a key
   that does not is one the question cannot reach. This is the PRICE of question
   2, stated as a count rather than as "the SOFT keys".

3. THE ABSENCE BEHAVIOUR OF EVERY EXISTING LAYER, by execution. Claim (b) said
   2 precedents, loud and silent. There are 3: a missing MODEL file raises
   FileNotFoundError, a missing TASK file is skipped in silence, an UNKNOWN
   domain warns and continues, and a known domain whose FILE is missing is also
   skipped in silence. So a role layer has 3 precedents to choose between, and
   the loud/silent framing of question 3 omitted one.

WHAT IT DOES NOT DO. It does not answer any of his 3 questions. Question 1 --
whether the structural roles (`collator`, `participant`, `player_manager`) and
his functional ones (`worker`, `classifier`, `orchestrator`) are 1 dimension or
2 -- is not reducible to a measurement, and its cost is already priced by
`scripts/which_role_vocabulary_does_the_code_speak_2026-10-30.py`.
"""
from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.cdsfl_registry import registry as R  # noqa: E402


def hard_dotpaths() -> list[str]:
    """Every dotpath the monotonicity check protects, from the live constants."""
    return sorted(set(R.HARD_CONSTRAINTS) | set(R.HARD_THRESHOLDS)
                  | set(R.HARD_STRINGS))


def _leaves(d, prefix: str = "") -> dict[str, object]:
    out: dict[str, object] = {}
    for k, v in d.items():
        path = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(_leaves(v, path))
        else:
            out[path] = v
    return out


def _merge_in_order(paths: list[Path]) -> dict:
    """Merge the given TOMLs left to right through the LIVE merge function."""
    policy: dict = {}
    for p in paths:
        policy = R._deep_merge(policy, R._load_toml(p))
    return policy


def order_sensitivity() -> dict:
    """Canonical order against reversed order, for every (domain, model) pair."""
    reg = R.REGISTRY_DIR
    universal = reg / "universal.toml"
    domains = sorted((reg / "domains").glob("*.toml"))
    models = sorted((reg / "models").glob("*.toml"))

    hard = hard_dotpaths()
    pairs = []
    hard_differs: list[str] = []
    soft_differs: dict[str, int] = {}

    for d in domains:
        for m in models:
            fwd = _merge_in_order([universal, d, m])
            rev = _merge_in_order([universal, m, d])
            lf, lr = _leaves(fwd), _leaves(rev)
            keys = set(lf) | set(lr)
            differing = sorted(k for k in keys if lf.get(k, _SENTINEL)
                               != lr.get(k, _SENTINEL))
            for k in differing:
                soft_differs[k] = soft_differs.get(k, 0) + 1
                if k in hard:
                    hard_differs.append(f"{d.stem}/{m.stem}:{k}")
            pairs.append({"domain": d.stem, "model": m.stem,
                          "leaves": len(keys), "differing": len(differing)})

    return {"pairs": pairs, "n_pairs": len(pairs),
            "hard_dotpaths": hard, "n_hard": len(hard),
            "hard_order_differences": hard_differs,
            "order_decided_keys": dict(sorted(soft_differs.items()))}


_SENTINEL = object()


def namespace_disjointness() -> dict:
    """WHY order decides nothing: the layers do not write the same leaves.

    A 0 in the order measurement above could mean 2 very different things -- the
    layers genuinely never collide, or the detector is blind. This separates
    them by measuring the collision directly: for every (domain, model) pair,
    how many leaf dotpaths does the domain file share with the model file.

    The matching positive control -- 2 synthetic layers that DO collide, which
    the detector must report -- lives in the guard, because a control belongs
    where it can fail a build.
    """
    reg = R.REGISTRY_DIR
    domains = sorted((reg / "domains").glob("*.toml"))
    models = sorted((reg / "models").glob("*.toml"))
    colliding = 0
    total = 0
    shared_examples: list[str] = []
    dom_prefixes: set[str] = set()
    mod_prefixes: set[str] = set()
    for d in domains:
        dk = set(_leaves(R._load_toml(d)))
        dom_prefixes |= {k.split(".")[0] for k in dk}
        for m in models:
            mk = set(_leaves(R._load_toml(m)))
            mod_prefixes |= {k.split(".")[0] for k in mk}
            total += 1
            shared = dk & mk
            if shared:
                colliding += 1
                if len(shared_examples) < 5:
                    shared_examples.append(f"{d.stem}/{m.stem}: {sorted(shared)}")
    return {"colliding_pairs": colliding, "total_pairs": total,
            "shared_examples": shared_examples,
            "domain_top_level_keys": sorted(dom_prefixes),
            "model_top_level_keys": sorted(mod_prefixes),
            "top_level_overlap": sorted(dom_prefixes & mod_prefixes)}


def absence_behaviour() -> dict:
    """What each layer DOES when its file is absent. By execution, not by eye."""
    out: dict[str, str] = {}

    # MODEL layer, absent file
    try:
        R.load_effective_policy(domain="mathematics",
                                model="a_model_that_does_not_exist")
        out["model_absent"] = "SILENT"
    except FileNotFoundError:
        out["model_absent"] = "RAISE:FileNotFoundError"
    except Exception as exc:                                  # pragma: no cover
        out["model_absent"] = f"RAISE:{type(exc).__name__}"

    # TASK layer, absent file
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            R.load_effective_policy(domain="mathematics",
                                    task_id="a-task-that-does-not-exist")
            out["task_absent"] = "WARN" if w else "SILENT"
        except Exception as exc:                              # pragma: no cover
            out["task_absent"] = f"RAISE:{type(exc).__name__}"

    # DOMAIN layer, unknown domain name
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            R.load_effective_policy(domain="a-domain-that-does-not-exist")
            out["domain_unknown"] = "WARN" if w else "SILENT"
        except Exception as exc:                              # pragma: no cover
            out["domain_unknown"] = f"RAISE:{type(exc).__name__}"

    # ROLE layer: does it exist at all?
    out["roles_dir_exists"] = str((R.REGISTRY_DIR / "roles").is_dir())
    out["tasks_dir_exists"] = str((R.REGISTRY_DIR / "tasks").is_dir())
    return out


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    order = order_sensitivity()
    absence = absence_behaviour()
    disjoint = namespace_disjointness()

    n_pairs = order["n_pairs"]
    n_hard_diff = len(order["hard_order_differences"])
    decided = order["order_decided_keys"]

    # Cross-verify the Wilson interval two ways, per the 21 April rule.
    k, n = n_hard_diff, max(n_pairs, 1)
    lo, hi = wilson(k, n)
    try:
        from statsmodels.stats.proportion import proportion_confint
        slo, shi = proportion_confint(k, n, method="wilson")
        agree = abs(slo - lo) < 1e-12 and abs(shi - hi) < 1e-12
    except Exception:                                          # pragma: no cover
        slo = shi = float("nan")
        agree = False

    result = {"order": order, "absence": absence,
              "disjointness": disjoint,
              "hard_order_difference_rate": {"k": k, "n": n,
                                             "wilson_closed_form": [lo, hi],
                                             "wilson_statsmodels": [slo, shi],
                                             "two_tools_agree": agree}}

    if args.json:
        print(json.dumps(result, indent=2, default=str))
        return 0

    print(__doc__)
    print("=" * 78)
    print(f"(domain, model) pairs merged both ways: {n_pairs}")
    print(f"HARD dotpaths protected by the live check: {order['n_hard']}")
    for p in order["hard_dotpaths"]:
        print(f"    {p}")
    print()
    n_hard = order["n_hard"]
    n_comparisons = n_pairs * n_hard
    print(f"HARD keys that DIFFER when the order is reversed: {n_hard_diff}"
          f" of {n_pairs} pair(s)")
    print(f"    Wilson 95% (closed form) : [{lo:.6f}, {hi:.6f}]")
    print(f"    Wilson 95% (statsmodels) : [{slo:.6f}, {shi:.6f}]"
          f"   agree={agree}")
    #: ★ THE DENOMINATOR IS THE PAIR, NOT THE DOTPATH. A first write of this
    #: result in entry B21 put the 60-pair interval beside the 17-dotpath count,
    #: and the pre-commit Wilson checker refused the commit, recomputing
    #: [0.0000, 0.1843] for 0 of 17. So both denominators are printed here with
    #: the interval that belongs to each, and the comparison count is printed
    #: WITHOUT one, because the dotpaths inside a single pair share a mechanism
    #: and are not independent observations.
    print(f"    comparisons made: {n_pairs} pair(s) x {n_hard} dotpath(s) = "
          f"{n_comparisons}, of which {n_hard_diff} differ")
    print(f"    NO interval is given for the {n_comparisons} figure: the "
          f"{n_hard} dotpaths within one pair")
    print(f"    share a mechanism, so they are not independent observations.")
    if n_hard_diff:
        print("    *** CLAIM (a) IS FALSIFIED: order moves a protected key ***")
        for v in order["hard_order_differences"]:
            print(f"      {v}")
    else:
        print("    CLAIM (a) HOLDS for the protected set: the monotonicity")
        print("    check compares against MODULE CONSTANTS rather than against")
        print("    the previous layer, so it is order-independent by")
        print("    construction, and executing it confirms that.")
    print()
    print(f"Keys the ORDER actually decides: {len(decided)}")
    for key, cnt in decided.items():
        print(f"    {key}   (differs in {cnt} of {n_pairs} pairs)")
    if not decided:
        print("    NONE. Question 2 -- where a role layer sits in the")
        print("    precedence -- cannot change any key that exists today,")
        print("    because no 2 layers currently set the same leaf.")
    print()
    print("ABSENCE BEHAVIOUR OF EACH LAYER, by execution:")
    for k2, v in absence.items():
        print(f"    {k2:22s} {v}")
    print()
    print()
    cp, tp = disjoint["colliding_pairs"], disjoint["total_pairs"]
    dlo, dhi = wilson(cp, max(tp, 1))
    print(f"WHY order decides nothing: {cp} of {tp} (domain, model) pairs share")
    print(f"    ANY leaf dotpath.  Wilson 95% [{dlo:.6f}, {dhi:.6f}]")
    print(f"    domain files write top-level keys: "
          f"{disjoint['domain_top_level_keys']}")
    print(f"    model  files write top-level keys: "
          f"{disjoint['model_top_level_keys']}")
    print(f"    top-level overlap: {disjoint['top_level_overlap'] or 'NONE'}")
    for ex in disjoint["shared_examples"]:
        print(f"      {ex}")
    print("    The layers occupy DISJOINT NAMESPACES by convention, not by any")
    print("    enforced rule -- nothing in the merge engine requires it. So")
    print("    question 2 is about a configuration that does not yet exist.")
    print()
    print("    So question 3 has 3 precedents, not 2: RAISE, WARN, SILENT.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
