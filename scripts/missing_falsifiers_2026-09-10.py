#!/usr/bin/env python3
"""Task 2.2: how many falsifiers are actually missing, and which?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

HIS RULING: "fix and test all remaining missing falsifiers." Before any of them
can be fixed, "all" has to mean something countable, and the obvious count is
wrong by a factor of 29.

THE NAIVE COUNT IS 817 AND IT IS A CATEGORY ERROR. Sweeping every archived
registry for a critical finding with an empty `falsifier_code` returns 817. But
the falsifier mechanism was BUILT on 2026-06-03 -- components at `ed12c7f`, the
voting replacement at `4fba6cc`. A run from April could not carry a falsifier,
and calling that a missing falsifier is like calling a 1990 car's missing airbag
a manufacturing defect. Split at the build date: 789 pre-mechanism, 28 after.

28 IS THE TASK. Each one is a critical finding, raised after the machinery
existed to test it, that was never tested.

WHY THE CONTROLS ARE COUNTED SEPARATELY. exp53 and exp55 are ZERO-PLANT CONTROLS
-- targets with no defects deliberately planted. A finding raised against a
control is a candidate false positive, so an absent falsifier there is a
different question from one against a live target: writing it does not confirm a
defect, it tests whether the finding was real at all. Both are reported.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]

#: The date the falsifier mechanism landed. Before it, absence is not omission.
MECHANISM_BUILT = "20260603"

#: Severity at or above which a finding is "critical" in this project.
CRITICAL = 0.7


def _stamp(dirname: str) -> str:
    for tok in dirname.split("_"):
        if tok.startswith("20") and len(tok) >= 8 and tok[:8].isdigit():
            return tok[:8]
    return "00000000"


def entries(state: dict) -> list[dict]:
    reg = state["registry"]
    ent = reg.get("entries", reg) if isinstance(reg, dict) else reg
    vals = list(ent.values()) if isinstance(ent, dict) else list(ent)
    return [v for v in vals if isinstance(v, dict)]


def survey() -> dict:
    pre, post = [], []
    for r in sorted((REPO / "bench" / "logs").glob("exp*/runner_state.json")):
        name = r.parent.name
        try:
            rows = entries(json.loads(r.read_text()))
        except (ValueError, OSError, KeyError):
            continue
        crit = [v for v in rows
                if isinstance(v.get("severity"), (int, float))
                and v["severity"] >= CRITICAL]
        miss = [v for v in crit if not (v.get("falsifier_code") or "").strip()]
        bucket = pre if _stamp(name) < MECHANISM_BUILT else post
        for v in miss:
            bucket.append({"run": name, "id": v.get("canonical_id"),
                           "status": v.get("status"),
                           "severity": v.get("severity"),
                           "verdict": v.get("falsifier_verdict"),
                           "control": "control" in name,
                           "description": (v.get("description") or "")[:110]})
    return {"pre": pre, "post": post}


#: Where a written falsifier declares what it covers.
TESTS = REPO / "bench" / "tests"


def declared_covers(tests_dir: pathlib.Path = TESTS) -> dict[tuple[str, str], list[str]]:
    """Every (run directory, canonical id) pair a test file declares, and who declares it.

    ADDED 2026-09-17 (task 2.2, panel round 16). This used to be a typed set
    holding 1 pair, so the script went on printing "ALREADY WRITTEN: 1 /
    REMAINING: 27" after all 28 falsifiers had been written. The count now comes
    from the test files themselves: each one that writes a falsifier for a
    finding in `survey()["post"]` carries a module-level

        COVERS = {("<run directory>", "<canonical id>"), ...}

    The run is part of the key because a canonical id is unique only within a
    run: exp53 carries C0001 in 2 runs, exp55 carries C0005 and C0006 in 2.

    The declaration is read with `ast.literal_eval`, so no test module is
    imported. A `COVERS` that is not a literal set of 2 strings raises rather
    than being skipped, because a declaration this function cannot read would
    otherwise show up only as a falsifier that was never written.
    """
    import ast

    out: dict[tuple[str, str], list[str]] = {}
    for f in sorted(pathlib.Path(tests_dir).glob("test_*.py")):
        src = f.read_text(encoding="utf-8")
        if "COVERS" not in src:
            continue
        for node in ast.parse(src, filename=str(f)).body:
            if not (isinstance(node, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "COVERS"
                            for t in node.targets)):
                continue
            try:
                value = ast.literal_eval(node.value)
            except ValueError as exc:
                raise ValueError(f"{f.name}:{node.lineno}: COVERS is not a "
                                 f"literal: {exc}") from exc
            if not isinstance(value, set) or not all(
                    isinstance(p, tuple) and len(p) == 2
                    and all(isinstance(x, str) for x in p) for p in value):
                raise ValueError(f"{f.name}:{node.lineno}: COVERS must be a set "
                                 f"of (run directory, canonical id) string pairs")
            try:
                shown = str(f.relative_to(REPO))
            except ValueError:
                shown = str(f)
            for pair in value:
                out.setdefault(pair, []).append(shown)
    return out


def coverage(post: list[dict], covers) -> tuple[set, set, set]:
    """(written, remaining, stale): the population split by the declarations.

    `stale` is a declared pair that is not in the population, which means a
    run directory or id was mistyped or the population moved.
    """
    population = {(r["run"], r["id"]) for r in post}
    declared = set(covers)
    return population & declared, population - declared, declared - population


def main() -> int:
    s = survey()
    pre, post = s["pre"], s["post"]
    print(f"critical findings with an EMPTY falsifier: {len(pre) + len(post)} in total")
    print(f"  {len(pre)} raised BEFORE the mechanism existed ({MECHANISM_BUILT}) "
          f"-- not omissions")
    print(f"  {len(post)} raised after it -- THIS is the population of task 2.2\n")

    live = [r for r in post if not r["control"]]
    ctrl = [r for r in post if r["control"]]
    print(f"  against LIVE targets  : {len(live)}")
    print(f"  against ZERO-PLANT CONTROLS: {len(ctrl)}  (a finding here is a "
          f"candidate false positive;\n      writing its falsifier tests whether "
          f"the finding was real, not whether a defect is)\n")

    by_run = collections.Counter(r["run"] for r in post)
    for run, n in sorted(by_run.items()):
        ids = sorted(r["id"] for r in post if r["run"] == run)
        print(f"  {run}: {n}  {ids}")

    print("\n  by recorded verdict:",
          dict(collections.Counter(str(r["verdict"]) for r in post)))
    print("  by status           :",
          dict(collections.Counter(str(r["status"]) for r in post)))

    from statsmodels.stats.proportion import proportion_confint
    tot_post_crit = 0
    for r in sorted((REPO / "bench" / "logs").glob("exp*/runner_state.json")):
        if _stamp(r.parent.name) < MECHANISM_BUILT:
            continue
        try:
            rows = entries(json.loads(r.read_text()))
        except (ValueError, OSError, KeyError):
            continue
        tot_post_crit += sum(
            1 for v in rows if isinstance(v.get("severity"), (int, float))
            and v["severity"] >= CRITICAL)
    if tot_post_crit:
        lo, hi = proportion_confint(len(post), tot_post_crit, method="wilson")
        lo_c, hi_c = proportion_confint(len(post), tot_post_crit, method="beta")
        print(f"\n  untested share of post-mechanism criticals: {len(post)} of "
              f"{tot_post_crit} = {100 * len(post) / tot_post_crit:.2f}%")
        print(f"  Wilson 95%          : [{lo * 100:.2f}%, {hi * 100:.2f}%]  (statsmodels)")
        print(f"  Clopper-Pearson 95% : [{lo_c * 100:.2f}%, {hi_c * 100:.2f}%]  (statsmodels/beta)")
        from scipy.stats import beta as sbeta
        slo = sbeta.ppf(0.025, len(post), tot_post_crit - len(post) + 1)
        shi = sbeta.ppf(0.975, len(post) + 1, tot_post_crit - len(post))
        print(f"  Clopper-Pearson 95% : [{slo * 100:.2f}%, {shi * 100:.2f}%]  "
              f"(scipy, cross-check; agrees to {abs(slo - lo_c):.1e})")

    covers = declared_covers()
    done, left, stale = coverage(post, covers)
    files = sorted({f for pair in done for f in covers[pair]})
    print(f"\n  ALREADY WRITTEN: {len(done)} "
          f"(declared as COVERS in {len(files)} test files under bench/tests)")
    for f in files:
        print(f"      {f}")
    print(f"  REMAINING       : {len(left)}")
    for run, fid in sorted(left):
        print(f"      {run} {fid}")
    if stale:
        print(f"  DECLARED BUT NOT IN THE POPULATION: {len(stale)}")
        for run, fid in sorted(stale):
            print(f"      {run} {fid}  <- {covers[(run, fid)]}")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help   # scripts/ is sys.path[0] when run directly
    answer_help(__doc__, __file__)
    sys.exit(main())
