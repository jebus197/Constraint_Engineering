#!/usr/bin/env python3
"""How many archived falsifiers never read their target at all?

THE QUESTION
------------
`reverify_falsifier` records CONFIRMED when a falsifier raises AssertionError or
prints FALSIFIED. It has never required the falsifier to DEPEND on the file it
accuses. Measured 2026-08-22: `print('FALSIFIED')` returns CONFIRMED. Reconfirmed
by both reviewers on the 2026-08-28 instrument confirmation panel, which added a
scale figure -- of 372 archived falsifiers replayed against every historical
version of their target, 346 fired on every single version and were never quiet.

346 of 372 is suggestive, not decisive: a defect genuinely present in every
version would produce the same pattern. This probe supplies the decisive test.

THE DISCRIMINATOR
-----------------
Replace the target with content that shares nothing with it, and re-run.

    still CONFIRMED  -> the falsifier cannot be touching its target. Definitive.
    ERROR            -> it reached for the target and could not use it. Coupled.
    REFUTED          -> it used the target and found no defect there. Coupled.

The asymmetry is the point. ERROR and REFUTED are both evidence of coupling; only
a surviving CONFIRMED proves its absence. So this probe UNDERCOUNTS
target-independence and never overcounts it, which is the safe direction for a
measurement that will be used to discount evidence.

WHAT "COUPLED" DOES AND DOES NOT MEAN -- read this before quoting the number
---------------------------------------------------------------------------
Coupling here is established by IMPORT, not by test content. A falsifier that
imports its target and then asserts something entirely unrelated to the accused
defect ERRORs on substitution exactly like a rigorous one, and this probe scores
both as coupled. So a high coupled count is NOT a clean bill of health; it rules
out only the crudest failure, the falsifier that never touches the file at all.

The first eight rows probed were all CONFIRMED on the real target and all ERROR on
the substitute -- coupled by import, every one. That is worth stating plainly
because it is the OPPOSITE of what the 346-of-372 figure suggests, and the two are
not in conflict: 346 fired on every historical version, which this probe cannot
address. Whether a falsifier tests the defect it ACCUSES is a third question that
neither measurement answers.

MEASUREMENT ONLY
----------------
Nothing here changes a verdict, a gate or a stored finding. It writes one JSON
file of results. Whether target-independent falsifiers should be excluded from
the corpus is a founder ruling, and a large one, because it bears on how much of
the archived evidence means anything.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from bench.falsifier_verify import reverify_falsifier  # noqa: E402

#: Deliberately valid Python that imports nothing and defines nothing the
#: original target had. A syntactically broken file would make every falsifier
#: ERROR and the probe would measure the breakage rather than the coupling.
UNRELATED = (
    '"""Unrelated placeholder. Shares no symbol with any project target."""\n'
    "\n"
    "ZZ_PLACEHOLDER_CONSTANT = 20260828\n"
    "\n"
    "\n"
    "def zz_placeholder_function(zz_argument):\n"
    '    """Return the argument unchanged."""\n'
    "    return zz_argument\n"
)


def probe_one(falsifier_code: str, target: pathlib.Path, timeout: int = 20) -> dict:
    """Run one falsifier against its real target and against an unrelated one."""
    if not (falsifier_code or "").strip():
        return {"verdict_real": "UNTOOLABLE", "verdict_destroyed": None, "coupled_to_target": None}
    original = target.read_text(encoding="utf-8") if target.is_file() else None
    real = reverify_falsifier(falsifier_code, repo_root=str(REPO), timeout=timeout)
    if original is None:
        return {"verdict_real": real, "verdict_destroyed": None, "coupled_to_target": None,
                "note": "target file absent, so the substitution cannot be made"}
    try:
        target.write_text(UNRELATED, encoding="utf-8")
        destroyed = reverify_falsifier(falsifier_code, repo_root=str(REPO), timeout=timeout)
    finally:
        target.write_text(original, encoding="utf-8")
        assert target.read_text(encoding="utf-8") == original, "target not restored"
    reads = None
    if real == "CONFIRMED":
        # Only meaningful when the falsifier fires on the real target at all.
        reads = destroyed != "CONFIRMED"
    return {"verdict_real": real, "verdict_destroyed": destroyed, "coupled_to_target": reads}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0, help="probe at most N findings (0 = all)")
    ap.add_argument("--out", default="experimental_notes/data/target_independence_2026-08-28.json")
    ap.add_argument("--timeout", type=int, default=20)
    args = ap.parse_args()

    arch = REPO / "experimental_notes" / "data" / "discrimination_control_archive.json"
    if not arch.is_file():
        print(f"archive not found: {arch}", file=sys.stderr)
        return 2
    raw = json.loads(arch.read_text(encoding="utf-8"))
    rows = raw if isinstance(raw, list) else (raw.get("rows") or next(iter(raw.values())))

    # The archive rows carry cid/run/target but NOT the falsifier source, so it is
    # resolved from each run's own report. Checked rather than assumed: an earlier
    # draft read `r["falsifier_code"]`, which does not exist, and would have
    # reported every row undecidable while looking like a completed measurement.
    def _codes_for(run: str, _cache={}) -> dict:
        if run in _cache:
            return _cache[run]
        out = {}
        for d in (REPO / "bench" / "logs").glob(f"*{run}*"):
            if not d.is_dir():
                continue
            reps = [x for x in d.glob("*_report.json") if ".errata" not in str(x)]
            if not reps:
                continue
            try:
                ents = json.loads(reps[0].read_text(encoding="utf-8"))["registry"]["entries"]
            except Exception:                                   # noqa: BLE001
                continue
            for cid, e in ents.items():
                if (e.get("falsifier_code") or "").strip():
                    out.setdefault(cid, e["falsifier_code"])
            break
        _cache[run] = out
        return out

    results, tally = [], {"reads": 0, "independent": 0, "undecidable": 0}
    todo = rows[:args.limit] if args.limit else rows
    for i, r in enumerate(todo, 1):
        code = _codes_for(r.get("run") or "").get(r.get("cid") or "", "")
        tgt = r.get("target")
        if not code or not tgt:
            tally["undecidable"] += 1
            continue
        target = REPO / tgt
        out = probe_one(code, target, timeout=args.timeout)
        out.update({"cid": r.get("cid"), "run": r.get("run"), "target": tgt})
        results.append(out)
        key = {True: "reads", False: "independent", None: "undecidable"}[out["coupled_to_target"]]
        tally[key] += 1
        if i % 25 == 0:
            print(f"  {i}/{len(todo)}  {tally}", flush=True)

    dest = REPO / args.out
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"tally": tally, "rows": results}, indent=2), encoding="utf-8")
    print(f"\n  probed {len(results)} falsifiers")
    print(f"    coupled (by import)   {tally['reads']}")
    print(f"    TARGET-INDEPENDENT    {tally['independent']}   <- confirmed against an unrelated file")
    print(f"    undecidable           {tally['undecidable']}")
    print(f"  written: {dest}")
    print("\n  UNDERCOUNTS by construction: only a surviving CONFIRMED is proof of")
    print("  independence, so the real figure is at least this and never less.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
