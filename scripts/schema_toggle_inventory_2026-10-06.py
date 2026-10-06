#!/usr/bin/env python3
"""Every boolean schema toggle: its default, what the simulation sets, what real runs set.

THE FOUNDER'S ASK, 2026-10-06: a UX design brief offering *"toggles for ITC/burst/all
major schema features, with explanations and recommendations"*.

WHY THIS SCRIPT EXISTS RATHER THAN A HAND-WRITTEN TABLE. A brief recommending defaults
is a document full of numbers -- how many real runs enabled a facility, what the
simulation diverges on -- and `measured-rate-travels-with-its-script` makes a number
with no producer a claim ABOUT evidence rather than evidence. Every figure in
`experimental_notes/CDSFL_Schema_Toggle_Design_Brief_2026-10-06.md` comes from here and
can be re-derived by running it.

IT ALSO ANSWERS A QUESTION THE BRIEF CANNOT ANSWER BY INSPECTION: which toggles are
ENABLED NOWHERE. A facility armed in no real config and no simulation has never run,
and the additive standard's symmetric half says an addition nothing reaches is not
additive. Those are the rows a reader should look at first.

Run: python3 scripts/schema_toggle_inventory_2026-10-06.py
     python3 scripts/schema_toggle_inventory_2026-10-06.py --markdown
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
import glob
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

SIM_LAUNCHER = REPO / "bench" / "tools" / "run_simulated_experiment.py"


def simulated_settings() -> dict:
    """What the simulated launcher passes to RunnerConfig, by AST.

    Read from the launcher rather than by running it, because running it now
    dispatches a panel.
    """
    out = {}
    src = SIM_LAUNCHER.read_text(encoding="utf-8")
    for node in ast.walk(ast.parse(src)):
        if not (isinstance(node, ast.Call) and (
                getattr(node.func, "attr", None)
                or getattr(node.func, "id", None)) == "RunnerConfig"):
            continue
        for kw in node.keywords:
            if kw.arg is None:
                continue
            try:
                out[kw.arg] = ast.literal_eval(kw.value)
            except (ValueError, TypeError):
                # A computed value (a flag, a conditional). Record that it is SET.
                out[kw.arg] = "<computed from a flag>"
    return out


def real_config_settings() -> tuple[dict, int]:
    """How many shipped real configs set each key, and to what."""
    counts = {}
    # BOTH GLOBS, OR THE DENOMINATOR IS WRONG. The first version used only the
    # directory form and reported 47, against the 49 that
    # `what_the_sim_runner_never_carried_over_2026-10-05.py` reports and that this
    # project's prose cites. The difference is 2 configs that sit directly in
    # `bench/` rather than in an `exp<N>_configs/` directory. A denominator that
    # silently drops 2 members makes every proportion built on it wrong.
    files = sorted(glob.glob(str(REPO / "bench" / "exp*_config*" / "*.json"))) + \
        sorted(glob.glob(str(REPO / "bench" / "exp*_config.json")))
    for f in files:
        try:
            d = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for k, v in (d.items() if isinstance(d, dict) else ()):
            counts.setdefault(k, []).append(v)
    return counts, len(files)


def inventory():
    from bench.reference_runner_v3 import RunnerConfig
    sim = simulated_settings()
    real, n_real = real_config_settings()
    rows = []
    for f in dataclasses.fields(RunnerConfig):
        if not isinstance(f.default, bool):
            continue
        vals = real.get(f.name, [])
        rows.append({
            "name": f.name,
            "default": f.default,
            "sim": sim.get(f.name, None),
            "sim_sets": f.name in sim,
            "real_sets": len(vals),
            "real_true": sum(1 for v in vals if v is True),
            "n_real": n_real,
        })
    return sorted(rows, key=lambda r: r["name"]), n_real


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="schema_toggle_inventory_2026-10-06.py", description=__doc__.split("\n\n")[0])
    p.add_argument("--markdown", action="store_true")
    args = p.parse_args(argv)

    rows, n_real = inventory()
    #: COMPUTED VALUES CANNOT BE CLASSIFIED FROM THE SOURCE, AND SAYING SO IS THE
    #: HONEST ANSWER. The first version treated `sim is not True` as "not enabled in
    #: simulation", which swept in every value the launcher computes from a flag --
    #: and `latent_tagger_enabled` and `severity_calibration_enabled` are both
    #: computed and default ON, so it reported 2 live facilities as enabled nowhere.
    COMPUTED = "<computed from a flag>"
    never = [r for r in rows
             if r["real_true"] == 0 and r["sim"] is not True and r["sim"] != COMPUTED]
    computed = [r for r in rows if r["sim"] == COMPUTED]
    always_on = [r for r in rows if r["default"] is True]

    if args.markdown:
        print("| toggle | default | simulation | real configs enabling it |")
        print("|---|---|---|---|")
        for r in rows:
            simv = ("not set" if not r["sim_sets"] else str(r["sim"]))
            print(f"| `{r['name']}` | {r['default']} | {simv} | "
                  f"{r['real_true']} of {r['n_real']} |")
    else:
        print("=" * 92)
        print(f"BOOLEAN SCHEMA TOGGLES — {len(rows)} of 93 RunnerConfig fields; "
              f"{n_real} real config file(s) scanned")
        print("=" * 92)
        print(f"  {'toggle':42s} {'default':>8s} {'simulation':>22s} {'real ON':>10s}")
        for r in rows:
            simv = "not set" if not r["sim_sets"] else str(r["sim"])
            print(f"  {r['name']:42s} {str(r['default']):>8s} {simv:>22s} "
                  f"{r['real_true']:>4d}/{r['n_real']:<5d}")
        print()
        print(f"ON BY DEFAULT: {len(always_on)} — "
              f"{', '.join(r['name'] for r in always_on)}")
        print()
        print(f"ENABLED NOWHERE ({len(never)}): armed in 0 real configs and not "
              f"turned on in simulation.")
        for r in never:
            print(f"    {r['name']}")
        print()
        print("An addition nothing reaches is not additive. These rows are either "
              "awaiting a study,")
        print("or they are dead weight; the brief says which, per row.")
        print()
        print(f"COMPUTED IN SIMULATION ({len(computed)}) — the launcher derives these "
              f"from a command-line flag,")
        print("so their simulated value cannot be read off the source and is NOT "
              "classified above:")
        for r in computed:
            print(f"    {r['name']}  (real configs enabling it: "
                  f"{r['real_true']} of {r['n_real']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
