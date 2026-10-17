#!/usr/bin/env python3
"""B21 step 1, measured: wiring the policy merge would cap every experiment.

B21's own plan, written before this was measured, says: *"(1) wire
`load_effective_policy` into v3, which is the single change that makes every
later step declarative"*, and that steps 1 and 4 are *"each a handful of
lines"*. THE MEASUREMENT CONTRADICTS THE PLAN, and the plan was mine.

THREE FIGURES SETTLE IT.

  1. THE TWO VOCABULARIES BARELY OVERLAP. The merged policy for
     `domain=mathematics` has 46 leaves. Exactly 1 of them shares a name with
     a `RunnerConfig` field: `protocol.max_rounds`. The other 45 have no
     counterpart at all, so there is nothing to "wire" for them -- wiring
     needs a correspondence and there is none.

  2. THE ONE THAT DOES OVERLAP, CONFLICTS. The runner's default is 21 and the
     policy says 5. Both mean the same thing: the schema's own description is
     "Maximum rounds for CDSFL experiments" and the runner's field sits under
     "# Round limits".

  3. AND THE POLICY'S VALUE AGREES WITH NO EXPERIMENT. Across 47 shipped
     configs, 0 leave `max_rounds` unset -- 0.0000%, Wilson [0.0000%,
     7.5558%] -- so the runner's 21 is DEAD and the configs always decide.
     The values are 2, 6, 8, 10, 12, 15, 16, 20 and 29, with 19 configs at 16
     and 9 at 12. NOT ONE is 5.

SO WIRING IT AS THE PLAN DESCRIBES WOULD CAP 46 OF THE 47 CONFIGS BELOW THEIR
CONFIGURED ROUND COUNT -- every one except the single config at 2 -- and
truncate the experimental programme. That is not a handful of lines; it is a
change to what every experiment is permitted to do.

WHAT THE REAL QUESTION IS, and it is his rather than mine: WHICH LAYER OWNS
`max_rounds`. Two sources of truth for one quantity disagree 47 times out of
47, and the project's own rule is that encoding one fact twice means the two
can drift -- which they already have. The options are to make the policy the
owner and raise its value, to make the config the owner and delete the policy
key, or to let the config override a policy ceiling and record when it does.
Each has a different consequence for replay against the archive.

WHAT IS SAFE AND IS DONE SEPARATELY: B21 step 4, wiring `validate_all_policies`
as a run-level preflight. It only ever refuses a run whose policy layers do not
merge, so it cannot change a passing run's behaviour. Measured now: 17 layers
validate and 0 are broken, so it lands green and acts as a ratchet.

Costs nothing: reads local TOML and JSON and dispatches to no model.

Usage: python3 scripts/would_wiring_the_policy_engine_change_a_run_2026-10-17.py
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def _proportion(k, n):
    from statsmodels.stats.proportion import proportion_confint
    import scipy.stats as st
    if n == 0:
        return None
    w = proportion_confint(k, n, method="wilson")
    b = proportion_confint(k, n, method="beta")
    cp_hi = 1.0 if k == n else float(st.beta.ppf(0.975, k + 1, n - k))
    return {"k": k, "n": n, "pct": 100.0 * k / n,
            "wilson": (w[0] * 100, w[1] * 100),
            "cp": (b[0] * 100, b[1] * 100),
            "agrees": abs(b[1] - cp_hi) < 1e-9}


def _say(label, p):
    if p is None:
        print(f"  {label}: no denominator")
        return
    print(f"  {label}: {p['k']} of {p['n']} = {p['pct']:.4f}%")
    print(f"      Wilson [{p['wilson'][0]:.4f}%, {p['wilson'][1]:.4f}%]  "
          f"Clopper-Pearson [{p['cp'][0]:.4f}%, {p['cp'][1]:.4f}%]  "
          f"scipy agrees {p['agrees']}")


def _flatten(d, prefix=""):
    out = {}
    for key, value in (d or {}).items():
        full = f"{prefix}{key}"
        if isinstance(value, dict):
            out.update(_flatten(value, full + "."))
        else:
            out[full] = value
    return out


def config_values(field: str = "max_rounds") -> collections.Counter:
    found = collections.Counter()

    def dig(obj):
        if isinstance(obj, dict):
            if field in obj:
                return obj[field]
            for value in obj.values():
                got = dig(value)
                if got is not None:
                    return got
        elif isinstance(obj, list):
            for value in obj:
                got = dig(value)
                if got is not None:
                    return got
        return None

    for path in sorted((ROOT / "bench").glob("exp*_configs/*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        found[dig(data)] += 1
    return found


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__)
    parser.add_argument("--domain", default="mathematics",
                        help="which domain's merged policy to compare")
    args = parser.parse_args(argv)

    from bench.cdsfl_registry.registry import (load_effective_policy,
                                               validate_all_policies)
    from bench.reference_runner_v3 import RunnerConfig

    print("1. DO THE TWO VOCABULARIES OVERLAP AT ALL?")
    policy = _flatten(load_effective_policy(args.domain))
    fields = set(RunnerConfig.__dataclass_fields__)
    cfg = RunnerConfig()
    shared = [(k, getattr(cfg, k.split(".")[-1]), v)
              for k, v in sorted(policy.items())
              if k.split(".")[-1] in fields]
    print(f"  merged policy leaves (domain={args.domain}) : {len(policy)}")
    print(f"  RunnerConfig fields                        : {len(fields)}")
    _say("policy leaves with a matching field name", 
         _proportion(len(shared), len(policy)))
    print("  WIRING NEEDS A CORRESPONDENCE. For the leaves with no matching")
    print("  field there is nothing to wire, so 'wire the policy in' cannot")
    print("  be a handful of lines -- it is a mapping that does not exist yet.")

    print("\n2. WHERE THEY OVERLAP, DO THEY AGREE?")
    disagree = [(k, cur, val) for k, cur, val in shared if cur != val]
    for k, cur, val in shared:
        print(f"  {'DIFFERS' if cur != val else 'agrees ':<8} {k}: "
              f"runner={cur!r} policy={val!r}")
    _say("shared leaves that DISAGREE", _proportion(len(disagree), max(len(shared), 1)))

    print("\n3. DOES THE POLICY'S VALUE AGREE WITH ANY EXPERIMENT?")
    counts = config_values("max_rounds")
    total = sum(counts.values())
    unset = counts.get(None, 0)
    print("  max_rounds across the shipped configs:")
    for value, n in sorted(counts.items(), key=lambda kv: (kv[0] is None,
                                                           kv[0])):
        print(f"    {str(value):<8} {n} config(s)")
    _say("configs leaving it unset, so the runner default applies",
         _proportion(unset, total))
    policy_rounds = policy.get("protocol.max_rounds")
    matching = counts.get(policy_rounds, 0)
    _say(f"configs whose value equals the policy's ({policy_rounds})",
         _proportion(matching, total))
    capped = sum(n for v, n in counts.items()
                 if v is not None and policy_rounds is not None
                 and v > policy_rounds)
    _say(f"configs that would be CAPPED by the policy value",
         _proportion(capped, total))

    print("\n4. WHAT IS SAFE: B21 STEP 4, THE PREFLIGHT VALIDATOR")
    results = validate_all_policies()
    bad = {k: v for k, v in results.items() if v != "ok"}
    _say("policy layers validating cleanly",
         _proportion(len(results) - len(bad), len(results)))
    for k, v in list(bad.items())[:5]:
        print(f"      {k}: {v[:90]}")
    print("  It only ever refuses a run whose layers do not merge, so it")
    print("  cannot change a passing run. It lands green and acts as a ratchet.")

    print("\nTHE ANSWER")
    print("  STEP 4 IS SAFE AND IS DONE. STEP 1 IS NOT A WIRING TASK: it is the")
    print("  question of WHICH LAYER OWNS `max_rounds`, because 2 sources of")
    print("  truth for 1 quantity already disagree with every experiment. That")
    print("  is his decision, and each option has a different consequence for")
    print("  replay against the archive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
