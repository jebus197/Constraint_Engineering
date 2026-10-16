#!/usr/bin/env python3
"""How many recorded identifiers carry a bare vendor name, and does the forward path still produce them?

HIS RULING, 2026-10-16: *"We normalise going forward, since recording vendor
names is purely a recording statistic and has no impact on capability, or how
our experiments work."*

WHAT THIS MEASURES. A seat is dispatched under a label carrying the mandatory
simulation suffix, and the runner prefixes that label to whatever identifier the
model chose for itself. A model that calls its own finding `GEMINI_F004`
therefore produces `Gemini-SIM_GEMINI_F004`, in which a reader meets a BARE
vendor name. The seat label was always correct; the bare name arrives inside the
model's own text.

A LATTICE OF PREDICATES, BECAUSE THE PROJECT RECORD CARRIED THREE DIFFERENT
FIGURES FOR THIS ONE DEFECT. The master task list records 64. An earlier scan
recorded 38. A first draft of this script printed 81. None of the three said
which predicate it was counting, which is the `compare lint counts like with
like` failure in its purest form: all of them scan the same archive and differ
only in the separator set, the file set, and whether a quote delimiter is
required. So every predicate is counted here and named, and the measured values
as of 2026-10-16 are recorded beside them:

  P1  quoted, `_` separator, JSON files ....... 64 in 7 files, 1 run
  P2  quoted, `_` separator, EVERY file ....... 64 in 7 files, 1 run
  P3  any separator, unquoted, JSON files ..... 81 in 10 files, 2 runs
  P4  any separator, unquoted, EVERY file ..... 98 in 14 files, 3 runs
  P5  distinct finding objects in reports .......4 in 1 run
  P6  distinct identifiers ..................... 2

P1 IS THE TASK LIST'S 64, reproduced exactly. P3 is wider because `-` and `:`
are also legal separators and the panel worktree harvest carries a copy. P4 adds
console logs. P5 counts findings rather than strings, and is the number that
matters for provenance: 4 recorded findings, carrying 2 distinct identifiers,
in 1 run.

THE 38 CANNOT BE REPRODUCED BY ANY PREDICATE IN THIS LATTICE. It was quoted in
an earlier brief without a producer, which is precisely what
`measured-rate-travels-with-its-script` forbids, and it is WITHDRAWN here rather
than carried forward. The figures above are the ones this script reproduces on
demand.

WHY NOTHING IS REWRITTEN. The archive is experimental evidence. Rewriting run
2's recorded findings to clear a cosmetic defect would be falsifying that
evidence, which was refused explicitly. Predicate A is therefore FROZEN: it can
only be cleared by time, as newer runs accumulate. What the repair changes is
what the NEXT run writes, and the second half of this script measures exactly
that by calling the composition path rather than reading its description.

`execute-do-not-grep`: the forward check CALLS `_strip_redundant_vendor_prefix`
and reproduces the call site's own composition. It does not assert on the text
of `runner_core.py`.

Free on `--help`: dispatches nothing, spends nothing, reads only local files.

Usage:
    python3 scripts/how_many_identifiers_carry_a_bare_vendor_name_2026-10-16.py
    python3 scripts/how_many_identifiers_carry_a_bare_vendor_name_2026-10-16.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: The vendor tokens are DERIVED from the runner's own roster, never declared a
#: second time here. A vendor name is legitimately the subject of this script --
#: it exists to count and strip them -- so this is not a capability decision
#: keyed on a model name and does not conflict with his ruling of 2026-10-07.
def _vendors() -> list[str]:
    sys.path.insert(0, str(REPO / "bench"))
    import runner_core  # noqa: PLC0415

    return sorted({str(v) for v in runner_core.MODEL_SPECS})


def _defect_pattern(vendors: list[str], *, quoted: bool, seps: str) -> re.Pattern[str]:
    alt = "|".join(re.escape(v) for v in sorted(vendors, key=len, reverse=True))
    q = '"' if quoted else ""
    # A composed identifier: <seat label>_<BARE VENDOR><separator>...
    return re.compile(rf'{q}([A-Za-z0-9]+-SIM)_({alt})([{seps}])', re.I)


#: The predicate lattice. Each row is (name, quoted, separators, globs).
PREDICATES = [
    ("P1  quoted, `_` only, JSON files", True, "_", ("*.json", "*.jsonl")),
    ("P2  quoted, `_` only, EVERY file", True, "_", ("*",)),
    ("P3  any separator, unquoted, JSON files", False, r"_\-:", ("*.json", "*.jsonl")),
    ("P4  any separator, unquoted, EVERY file", False, r"_\-:", ("*",)),
]


def _scan(pat: re.Pattern[str], globs: tuple[str, ...]) -> dict:
    raw = 0
    files: dict[str, int] = {}
    runs: set[str] = set()
    seen: set[Path] = set()
    for g in globs:
        for path in sorted(LOGS.rglob(g)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            try:
                text = path.read_text(errors="replace")
            except OSError:
                continue
            hits = pat.findall(text)
            if not hits:
                continue
            raw += len(hits)
            files[str(path.relative_to(REPO))] = len(hits)
            runs.add(path.relative_to(LOGS).parts[0])
    return {"occurrences": raw, "files": files, "runs": sorted(runs)}


def _finding_objects(vendors: list[str]) -> dict:
    """P5 and P6: count FINDINGS, not strings. This is the provenance figure."""
    alt = "|".join(re.escape(v) for v in sorted(vendors, key=len, reverse=True))
    pat = re.compile(rf'^([A-Za-z0-9]+-SIM)_({alt})[_\-:]', re.I)
    total = 0
    ids: set[str] = set()
    runs: set[str] = set()

    def walk(obj, run: str) -> None:
        nonlocal total
        if isinstance(obj, dict):
            fid = obj.get("finding_id") or obj.get("id")
            if isinstance(fid, str) and pat.match(fid):
                total += 1
                ids.add(fid)
                runs.add(run)
            for v in obj.values():
                walk(v, run)
        elif isinstance(obj, list):
            for v in obj:
                walk(v, run)

    for path in sorted(LOGS.rglob("*_report.json")):
        try:
            doc = json.loads(path.read_text(errors="replace"))
        except (OSError, ValueError):
            continue
        walk(doc, path.relative_to(LOGS).parts[0])
    return {"objects": total, "identifiers": sorted(ids), "runs": sorted(runs)}


def measure_archive(vendors: list[str]) -> dict:
    rows = []
    for name, quoted, seps, globs in PREDICATES:
        pat = _defect_pattern(vendors, quoted=quoted, seps=seps)
        row = _scan(pat, globs)
        row["predicate"] = name
        rows.append(row)
    return {"predicates": rows, "findings": _finding_objects(vendors)}


def measure_forward(vendors: list[str]) -> dict:
    """CALL the composition path on the exact identifiers the archive recorded."""
    sys.path.insert(0, str(REPO / "bench"))
    import runner_core  # noqa: PLC0415

    strip = getattr(runner_core, "_strip_redundant_vendor_prefix", None)
    if strip is None:
        return {"present": False, "cases": [], "still_defective": None}

    def compose(model_supplied: str, seat: str) -> str:
        fid = strip(model_supplied, seat)
        return fid if fid.startswith(f"{seat}_") else f"{seat}_{fid}"

    pat = _defect_pattern(vendors, quoted=False, seps=r"_\-:")
    cases = []
    # Every vendor, under its simulated and its paid seat label, with the exact
    # shape the models actually emitted.
    for v in vendors:
        for seat in (f"{v}-SIM", v):
            for supplied in (f"{v.upper()}_F004", f"{v}_F004", f"{v.lower()}-F004"):
                out = compose(supplied, seat)
                cases.append(
                    {
                        "model_supplied": supplied,
                        "seat": seat,
                        "composed": out,
                        "defective": bool(pat.search(out)),
                    }
                )
    # Idempotence: recomposing a composed identifier must not move it.
    for c in list(cases):
        again = compose(c["composed"], c["seat"])
        c["idempotent"] = again == c["composed"]
    return {
        "present": True,
        "cases": cases,
        "still_defective": sum(1 for c in cases if c["defective"]),
        "not_idempotent": sum(1 for c in cases if not c["idempotent"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="emit machine-readable output")
    args = ap.parse_args()

    vendors = _vendors()
    arch = measure_archive(vendors)
    fwd = measure_forward(vendors)

    if args.json:
        print(json.dumps({"archive": arch, "forward": fwd, "vendors": vendors}, indent=2))
        return 0

    print("IDENTIFIERS CARRYING A BARE VENDOR NAME")
    print(f"  vendor roster, derived from MODEL_SPECS: {', '.join(vendors)}")
    print()
    print("THE ARCHIVE, WHICH IS FROZEN BY DESIGN")
    for row in arch["predicates"]:
        print(
            f"  {row['predicate']:<42} {row['occurrences']:>4} occurrences"
            f"  {len(row['files']):>3} files  {len(row['runs'])} runs"
        )
    fnd = arch["findings"]
    print(f"  {'P5  distinct finding objects in reports':<42} {fnd['objects']:>4} findings"
          f"  {'':>3}        {len(fnd['runs'])} runs")
    print(f"  {'P6  distinct identifiers':<42} {len(fnd['identifiers']):>4}")
    for i in fnd["identifiers"]:
        print(f"       {i}")
    print()
    print("  files, under the widest JSON predicate (P3):")
    for f, n in sorted(arch["predicates"][2]["files"].items(), key=lambda kv: -kv[1]):
        print(f"       {n:>3}  {f}")
    print()
    print("THE FORWARD PATH, CALLED RATHER THAN READ")
    if not fwd["present"]:
        print("  VERDICT: the normalisation is ABSENT. The defect is live.")
        return 1
    n = len(fwd["cases"])
    print(f"  composed {n} identifiers across {len(vendors)} vendors, simulated and paid seats")
    print(f"  still carrying a bare vendor name .... {fwd['still_defective']} of {n}")
    print(f"  not idempotent under re-composition .. {fwd['not_idempotent']} of {n}")
    print()
    if fwd["still_defective"] == 0 and fwd["not_idempotent"] == 0:
        print("  VERDICT: the forward path is REPAIRED. The archive figure above is")
        print("  historical and will not grow. Nothing recorded was rewritten.")
        return 0
    print("  VERDICT: the forward path is STILL DEFECTIVE.")
    for c in fwd["cases"]:
        if c["defective"] or not c["idempotent"]:
            print(f"       {c['model_supplied']} @ {c['seat']} -> {c['composed']}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
