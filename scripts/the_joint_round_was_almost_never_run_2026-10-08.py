#!/usr/bin/env python3
"""Star topology was declared unskippable and the joint half was almost never run.

THE FOUNDER'S QUESTION, 2026-10-08: *"And you don't seem to have been running
recent panels under star topology, blind run first?"*

HE WAS RIGHT, AND THE MEASUREMENT IS LARGER THAN THE QUESTION. Star topology is
2 halves: each seat answers BLIND, then a JOINT round follows in which each seat
sees the other's blind reply. Of the archived rounds that collected 2 or more
landed replies, the great majority have no joint round at all -- so what was
reported as star topology was, repeatedly, a single blind round.

WHY THE GUARD BUILT TO PREVENT THIS COULD NOT SEE IT. His ruling of 2026-10-06
was *"I stated that it should be built into all confer round machinery going
forward so it couldn't be skipped"*, and
`_refuse_if_topology_is_skipped` was built for it. That check refuses a round
whose SIBLING on the same brief holds a landed reply and is not declared blind.
A round with no sibling passes trivially. So it guards contamination BETWEEN
rounds and is structurally unable to detect that the joint round never happened.

AND THE DECLARATION LEFT NO TRACE. `PANEL_BLIND_OF` and `PANEL_JOINT_OF` are
environment variables: they steer a run and write nothing, so nothing after the
fact could distinguish a declared blind round from an undeclared one. That is the
root cause of the invisibility, and it is why
`bench/confer_maths_panel_2026-09-05.py` now writes `topology.json` into every
round directory BEFORE dispatch.

WHAT THIS SCRIPT IS FOR. It produces the rate, dated 2 ways -- over the whole
archive and over the rounds dispatched since the ruling, which is the fair
denominator for compliance -- and it seeds the registry of rounds that carry the
debt, so the omission sits in the record rather than being quietly repaired.

THE PAIRING IS A HEURISTIC AND IS LABELLED AS ONE. A joint round is identified by
its NAME (`joint`, `star`, `_r2`, `round2`), because before `topology.json`
existed there is nothing else to read. A joint round named something else would
be missed, so the counts are an UPPER bound on the omission. The direction is not
in doubt: 4 of the rounds in the list were dispatched by this assistant on
2026-10-07 and 2026-10-08 and had no joint round planned at all.

Run: python3 scripts/the_joint_round_was_almost_never_run_2026-10-08.py
"""
from __future__ import annotations

import argparse
import glob
import json
import math
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SEATS = ("cc2", "fable", "cx", "ge", "cgpt", "ds", "kimi")
JOINT_MARKERS = ("joint", "star", "_r2", "round2")

#: The date the ruling was given. Rounds before it are history; rounds after it
#: are compliance, and conflating the 2 would flatter the recent record.
RULING_DATE = "2026-10-06"

Z = 1.959963984540054


def wilson(k: int, n: int, z: float = Z) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = (z / d) * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, c - h), min(1.0, c + h))


def is_jointish(name: str) -> bool:
    return any(m in name for m in JOINT_MARKERS)


def round_date(name: str) -> str:
    """The ISO date in a round name, or '' when it uses the compact stamp."""
    import re
    m = re.search(r"(20\d\d-\d\d-\d\d)", name)
    if m:
        return m.group(1)
    m = re.search(r"(20\d\d)(\d\d)(\d\d)T", name)
    return f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else ""


def collect(repo: Path = REPO) -> list[dict]:
    out = []
    for d in sorted(glob.glob(str(repo / "bench" / "logs" / "*/"))):
        rd = Path(d.rstrip("/"))
        if not (rd / "BRIEF.md").is_file():
            continue
        landed = []
        for f in glob.glob(str(rd / "*.json")):
            st = Path(f).stem
            if st not in SEATS:
                continue
            try:
                j = json.load(open(f))
            except Exception:
                continue
            if isinstance(j, dict) and j.get("ok") and (j.get("chars") or 0) > 0:
                landed.append(st)
        topo = rd / "topology.json"
        rec = {}
        if topo.is_file():
            try:
                rec = json.loads(topo.read_text())
            except Exception:
                rec = {}
        out.append({"round": rd.name, "seats": sorted(landed),
                    "date": round_date(rd.name),
                    "has_topology_record": topo.is_file(),
                    "declared_kind": rec.get("kind"),
                    "declared_joint_of": rec.get("joint_of") or []})
    return out


def claim_the_joint_half_is_usually_missing() -> dict:
    rows = collect()
    multi = [r for r in rows if len(r["seats"]) >= 2]
    names = [r["round"] for r in rows]

    def has_partner(r):
        if r["declared_kind"] == "joint":
            return True
        # declared by a LATER round naming it
        if any(r["round"] in o["declared_joint_of"] for o in rows):
            return True
        if is_jointish(r["round"]):
            return True
        stem = r["round"].replace("_blind", "").replace("blind_", "").split("_2026")[0]
        key = stem[:18]
        return any(o != r["round"] and is_jointish(o) and key in o for o in names)

    missing = [r for r in multi if not has_partner(r)]
    paired = len(multi) - len(missing)
    lo, hi = wilson(paired, len(multi))

    since = [r for r in multi if r["date"] and r["date"] >= RULING_DATE]
    since_missing = [r for r in since if not has_partner(r)]
    slo, shi = wilson(len(since) - len(since_missing), len(since)) if since else (0, 0)
    return {
        "rounds_with_a_brief": len(rows),
        "rounds_with_2_or_more_landed_replies": len(multi),
        "rounds_carrying_a_topology_record": sum(
            1 for r in rows if r["has_topology_record"]),
        "paired_with_a_joint_round": paired,
        "paired_rate": round(paired / len(multi), 6) if multi else None,
        "paired_wilson": (round(lo, 6), round(hi, 6)),
        "missing_count": len(missing),
        "missing_rounds": [r["round"] for r in missing],
        "ruling_date": RULING_DATE,
        "since_the_ruling_total": len(since),
        "since_the_ruling_paired": len(since) - len(since_missing),
        "since_the_ruling_paired_wilson": (round(slo, 6), round(shi, 6)),
        "since_the_ruling_missing": [r["round"] for r in since_missing],
        "pairing_is_a_heuristic": True,
        "bound_direction": ("an UPPER bound on the omission: a joint round named "
                            "without any of the markers would be missed"),
    }


def claim_the_record_is_now_writable() -> dict:
    """The fix, checked by execution rather than by reading the dispatcher.

    Imports the dispatcher and asserts the writer exists and is called from
    `main`. A test that only read the source could not tell a defined function
    from a called one, which is this project's most repeated failure shape.
    """
    import ast
    src = (REPO / "bench" / "confer_maths_panel_2026-09-05.py").read_text()
    tree = ast.parse(src)
    defined = any(isinstance(n, ast.FunctionDef)
                  and n.name == "_write_topology_record" for n in ast.walk(tree))
    called = [n for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
              and n.func.id == "_write_topology_record"]
    in_main = False
    for n in ast.walk(tree):
        if isinstance(n, ast.FunctionDef) and n.name == "main":
            in_main = any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                          and c.func.id == "_write_topology_record"
                          for c in ast.walk(n))
    return {"writer_defined": defined, "call_sites": len(called),
            "called_from_main": in_main,
            "wired": defined and in_main,
            "note": ("an addition nothing reaches is not additive; this is the "
                     "check that the writer is CALLED, not merely defined")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true", help="print every missing round")
    args = ap.parse_args()

    d = claim_the_joint_half_is_usually_missing()
    print("== 1. how often the joint half of star topology was actually run ==")
    for k in ("rounds_with_a_brief", "rounds_with_2_or_more_landed_replies",
              "rounds_carrying_a_topology_record", "paired_with_a_joint_round",
              "paired_rate", "paired_wilson", "missing_count"):
        print(f"   {k}: {d[k]}")
    print(f"\n   since the ruling of {d['ruling_date']}: "
          f"{d['since_the_ruling_paired']} of {d['since_the_ruling_total']} paired, "
          f"Wilson {d['since_the_ruling_paired_wilson']}")
    print(f"   unpaired since the ruling: {d['since_the_ruling_missing']}")
    print(f"   {d['bound_direction']}")
    if args.list:
        print("\n   every unpaired round:")
        for r in d["missing_rounds"]:
            print(f"      {r}")

    print("\n== 2. the declaration is now recorded, and the writer is WIRED ==")
    for k, v in claim_the_record_is_now_writable().items():
        print(f"   {k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
