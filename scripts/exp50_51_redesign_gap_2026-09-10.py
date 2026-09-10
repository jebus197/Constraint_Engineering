#!/usr/bin/env python3
"""Task R2: which fixes since the exp50/51 configs were written are NOT in them?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

HIS RULING, 2026-08-22, verbatim: *"5: Redesign with all uncovered fixes in place
after the upcoming build experiment and any fixed it uncovers in place also."*
The precondition -- the build experiment -- has been met, so this is execution
work rather than a decision. But "all uncovered fixes" is not a list anyone has
written down, so the first job is to produce one from the record rather than from
memory.

THE METHOD, and it deliberately does not ask what a fix "should" be. The exp56
arm configs are the NEWEST pre-registration files in the repository and were
written after every fix in question. So a setting present in an exp56 arm and
absent from an exp50/51 config is a candidate gap, and a setting whose VALUE
differs is a candidate divergence. That turns a vague instruction into a diff.

WHAT THIS SCRIPT DOES NOT DO. It does not edit the exp50/51 files. They are
pre-registration artefacts, and task 3.1 established what a literal reading of a
ruling costs when applied to one: flipping flags there would have destroyed the
experiment the arm exists to run and spent money doing it. This produces the diff
and names which side each difference should probably follow; a human decides.

IT ALSO DOES NOT RUN ANYTHING. Both configs declare 5 models including 3 paid
seats. Running them is money, which is one of the founder's 3 standing categories
requiring him in person.
"""
from __future__ import annotations

import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
OLD = sorted(REPO.glob("bench/exp5[01]_configs/*.json"))
NEW = sorted(REPO.glob("bench/exp56_configs/*.json"))

#: Keys that SHOULD differ between experiments -- they name the experiment, its
#: target, or its declared variable. A difference here is the design, not a gap.
BY_DESIGN = {
    "_comment", "_arm", "_plan_ref", "experiment_name", "domain", "test_article",
    "context_files", "immune_memory_path", "panel_cwd", "models", "pattern",
    "topology", "_pre_registration", "_specialist_cells", "_macrophage",
}


def settings(p: pathlib.Path) -> dict:
    d = json.loads(p.read_text(encoding="utf-8"))
    return {k: v for k, v in d.items() if not k.startswith("_") or k in BY_DESIGN}


def main() -> int:
    if not OLD or not NEW:
        print("  exp50/51 or exp56 configs are absent on this machine")
        return 0
    new_common: dict = {}
    for p in NEW:
        for k, v in settings(p).items():
            if k in BY_DESIGN:
                continue
            new_common.setdefault(k, set()).add(json.dumps(v, sort_keys=True))
    # A setting the 3 newest arms AGREE on is a convention; one they differ on is
    # arm-specific and cannot be carried across.
    convention = {k: json.loads(next(iter(v))) for k, v in new_common.items()
                  if len(v) == 1}
    print(f"newest pre-registration files: {len(NEW)}")
    print(f"settings all {len(NEW)} agree on (the convention): {len(convention)}\n")

    missing_all, differs_all = [], []
    for p in OLD:
        cur = settings(p)
        missing = sorted(k for k in convention if k not in cur)
        differs = sorted(k for k in convention
                         if k in cur and cur[k] != convention[k])
        missing_all += [(p.name, k) for k in missing]
        differs_all += [(p.name, k, cur[k], convention[k]) for k in differs]
        print(f"  {p.name}")
        print(f"      settings present : {len(cur)}")
        print(f"      MISSING vs convention ({len(missing)}): {missing}")
        print(f"      DIFFERENT value  ({len(differs)}):")
        for k in differs:
            print(f"          {k}: exp50/51 has {cur[k]!r}, exp56 convention is "
                  f"{convention[k]!r}")

    n = len(convention) * len(OLD)
    k = len(missing_all) + len(differs_all)
    if n:
        from statsmodels.stats.proportion import proportion_confint
        from scipy import stats as sps
        import mpmath as mp
        w = proportion_confint(k, n, method="wilson")
        c = proportion_confint(k, n, method="beta")
        mp.mp.dps = 30
        z = mp.mpf(str(sps.norm.ppf(0.975)))
        pp, N = mp.mpf(k) / n, mp.mpf(n)
        cc = (pp + z**2 / (2 * N)) / (1 + z**2 / N)
        h = (z / (1 + z**2 / N)) * mp.sqrt(pp * (1 - pp) / N + z**2 / (4 * N**2))
        print(f"\n  settings out of step with the newest convention: {k} of {n} "
              f"= {k / n:.4%}")
        print(f"      Wilson [{w[0]:.4%}, {w[1]:.4%}] statsmodels | "
              f"[{float(cc - h):.4%}, {float(cc + h):.4%}] mpmath | "
              f"agree to 1e-9: {abs(w[0] - float(cc - h)) < 1e-9}")
        print(f"      Clopper-Pearson [{c[0]:.4%}, {c[1]:.4%}]")
    print("\n  Nothing was edited. Both exp50/51 configs declare 5 models "
          "including 3 paid\n  seats, so running them is money and is the "
          "founder's to authorise.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
