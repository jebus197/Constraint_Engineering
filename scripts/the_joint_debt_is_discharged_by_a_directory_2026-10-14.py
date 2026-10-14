#!/usr/bin/env python3
"""The joint-round debt is discharged by a DIRECTORY, not by a joint round.

WHAT THIS MEASURES, and it measures the live code rather than describing it.

`bench/confer_maths_panel_2026-09-05.py::_rounds_owing_a_joint_round` decides
which blind rounds still owe their joint half. The founder asked on 2026-10-06
for the star topology to be unskippable. This script establishes, by EXECUTION,
that the debt is discharged by 2 routes that require no joint round to have run:

  ROUTE 1 -- THE NAME. A sibling directory whose name contains any of
  ("joint", "star", "_r2", "round2") and contains the owing round's 18-character
  stem discharges the debt. Nothing requires that sibling to hold a single reply.

  ROUTE 2 -- THE DECLARATION. `topology.json` is written AT DISPATCH, before any
  seat answers, and its `joint_of` list is unioned into `declared_joint_of`. A
  round killed 30 seconds after launch therefore discharges its parent for ever.

Both were found on 2026-10-14 when CC1's own joint round for
`his_rulings_2026-10-13` was killed with 0 replies and the parent's debt
disappeared regardless.

AND THE 2 FORMS DISAGREE IN COMMITTED CODE. `bench/star_topology_2026-10-06.py`
fixed exactly this inference for the round KIND: its docstring reads *"THE ROUND
KIND MUST NOT BE INFERRED FROM THE DECLARATION IT REQUIRES"*, and `round_kind`
detects jointness by finding 240 contiguous characters of another round's reply
inside the brief. The debt gate never adopted that rule, so `topology.json` can
record `kind: joint` on a round `round_kind` calls blind.

RUN IT: python3 scripts/the_joint_debt_is_discharged_by_a_directory_2026-10-14.py
`--help` is free and dispatches nothing.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
SEATS = ("cc2", "fable", "cx", "ge", "cgpt", "ds", "kimi")
MARKERS = ("joint", "star", "_r2", "round2")
RULING_DATE = "2026-10-06"


def _load(path: pathlib.Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def landed(d: pathlib.Path) -> list:
    """Seats with a reply that actually succeeded and carried characters."""
    out = []
    for n in SEATS:
        f = d / f"{n}.json"
        if not f.is_file():
            continue
        try:
            j = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(j, dict) and j.get("ok") and (j.get("chars") or 0) > 0:
            out.append(n)
    return out


def dated_on_or_after(name: str) -> bool:
    m = re.search(r"(20\d\d-\d\d-\d\d)", name)
    if not m:
        m2 = re.search(r"(20\d\d)(\d\d)(\d\d)T", name)
        if not m2:
            return False
        return f"{m2.group(1)}-{m2.group(2)}-{m2.group(3)}" >= RULING_DATE
    return m.group(1) >= RULING_DATE


def owed(require_partner_replies: bool) -> list:
    """The derivation, with the partner-must-have-answered rule switchable.

    `require_partner_replies=False` reproduces the live predicate exactly.
    `True` is the proposed repair: a discharge requires a partner that ANSWERED.
    """
    rounds, declared_joint_of = {}, set()
    for d in sorted(LOGS.iterdir()):
        if not d.is_dir() or not (d / "BRIEF.md").is_file():
            continue
        lands = landed(d)
        kind = None
        t = d / "topology.json"
        if t.is_file():
            try:
                rec = json.loads(t.read_text(encoding="utf-8"))
                kind = rec.get("kind")
                # THE REPAIR: a declaration only discharges if the declaring
                # round actually collected 2 or more replies.
                if (not require_partner_replies) or len(lands) >= 2:
                    declared_joint_of.update(rec.get("joint_of") or [])
            except Exception as exc:
                # NAMED, not swallowed: an unreadable topology.json changes the
                # owed set, so a reader must see that one could not be read.
                print(f"  ** unreadable topology.json in {d.name}: {exc!r}")
        rounds[d.name] = (lands, kind)

    out, names = [], list(rounds)
    for name, (lands, kind) in rounds.items():
        if len(lands) < 2:
            continue
        if kind == "joint" or any(m in name for m in MARKERS):
            continue
        if name in declared_joint_of:
            continue
        stem = name.replace("_blind", "").replace("blind_", "").split("_2026")[0][:18]
        partners = [o for o in names
                    if o != name and any(m in o for m in MARKERS) and stem in o]
        if require_partner_replies:
            partners = [o for o in partners if len(rounds[o][0]) >= 2]
        if partners:
            continue
        if not dated_on_or_after(name):
            continue
        out.append(name)
    return sorted(out)


def wilson(k: int, n: int):
    """Wilson 95% interval, computed twice with independent tools."""
    # ★ A SWALLOWED IMPORT MEANS A FIGURE LOSES ITS INTERVAL IN SILENCE.
    # `except Exception: pass` here would let a missing statsmodels or mpmath
    # remove a confidence interval from a reported proportion with no trace,
    # and this project's standing rule is that every proportion carries one.
    # The failure is now NAMED and returned, so the caller can print it.
    a = b = None
    _why = []
    try:
        from statsmodels.stats.proportion import proportion_confint
        a = tuple(float(x) for x in proportion_confint(k, n, 0.05, method="wilson"))
    except Exception as exc:
        _why.append(f"statsmodels unavailable: {exc!r}")
    try:
        import mpmath as mp
        mp.mp.dps = 40
        z = mp.mpf("1.959963984540054235524594430520551527955")
        p, nn = mp.mpf(k) / n, mp.mpf(n)
        c = p + z ** 2 / (2 * nn)
        d = z * mp.sqrt(p * (1 - p) / nn + z ** 2 / (4 * nn ** 2))
        den = 1 + z ** 2 / nn
        b = (float((c - d) / den), float((c + d) / den))
    except Exception as exc:
        _why.append(f"mpmath unavailable: {exc!r}")
    if _why:
        print("  ** INTERVAL TOOL MISSING, so a figure below carries no "
              "interval: " + "; ".join(_why))
    return a, b


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()

    if not LOGS.is_dir():
        print(f"no logs directory at {LOGS}")
        return 2

    os.environ["PANEL_BRIEF_UNCHECKED"] = "1"
    star = _load(REPO / "bench" / "star_topology_2026-10-06.py", "_star")

    live_fn = None
    try:
        panel = _load(REPO / "bench" / "confer_maths_panel_2026-09-05.py", "_panel")
        live_fn = panel._rounds_owing_a_joint_round
    except Exception as exc:                                    # pragma: no cover
        print(f"  NOTE: could not import the dispatcher ({exc}); "
              f"comparing the reimplementation only")

    before = owed(require_partner_replies=False)   # the pre-2026-10-14 behaviour
    after = owed(require_partner_replies=True)     # the repair

    # EXECUTE BOTH FORMS. The live function carries the repair as of 2026-10-14,
    # so it must agree with `after`. If it agrees with `before` instead, the
    # repair has been reverted and this script says so rather than assuming.
    agree = None
    if live_fn is not None:
        real = sorted(live_fn())
        agree = (real == after)
        print(f"  live predicate       : {len(real)} owed -> {real}")
        print(f"  repaired form        : {len(after)} owed -> {after}")
        print(f"  live carries the fix : {agree}")
        if real == before and before != after:
            print("  ★ THE REPAIR IS NOT IN THE LIVE CODE — live matches the "
                  "pre-fix behaviour")
        elif not agree:
            print("  ★ LIVE MATCHES NEITHER FORM — the predicate has changed again")

    newly = [r for r in after if r not in before]
    print(f"\n  pre-fix behaviour    : {len(before)} owed")
    print(f"  FALSELY DISCHARGED BY A DIRECTORY ALONE: {len(newly)} -> {newly}")
    mine_live, mine_fixed = before, after

    # The disagreement between the declared kind and the detected kind.
    dis, checked = [], 0
    for d in sorted(LOGS.iterdir()):
        t = d / "topology.json"
        if not d.is_dir() or not t.is_file() or not (d / "BRIEF.md").is_file():
            continue
        try:
            declared = json.loads(t.read_text(encoding="utf-8")).get("kind")
        except Exception:
            continue
        if declared is None:
            continue
        checked += 1
        detected = star.round_kind(LOGS, d.name)
        if declared != detected:
            dis.append((d.name, declared, detected, len(landed(d))))

    print(f"\n  rounds with a recorded kind: {checked}")
    print(f"  declared kind != detected kind: {len(dis)}")
    if checked:
        a, b = wilson(len(dis), checked)
        print(f"    rate {len(dis)}/{checked} = {len(dis)/checked:.6f}")
        if a:
            print(f"    Wilson (statsmodels): [{a[0]:.6f}, {a[1]:.6f}]")
        if b:
            print(f"    Wilson (mpmath)     : [{b[0]:.6f}, {b[1]:.6f}]")
        if a and b:
            print(f"    tools agree to      : {max(abs(a[0]-b[0]), abs(a[1]-b[1])):.2e}")
    for name, declared, detected, n in dis:
        print(f"    {name}: declared={declared} detected={detected} landed={n}")

    # Partners that discharge a debt while holding no replies at all.
    empty = []
    for d in sorted(LOGS.iterdir()):
        if not d.is_dir() or not (d / "BRIEF.md").is_file():
            continue
        if not any(m in d.name for m in MARKERS):
            continue
        if len(landed(d)) == 0:
            empty.append(d.name)
    print(f"\n  marker-named rounds holding 0 replies: {len(empty)} -> {empty}")

    # ─────────── WAS A DECLARED JOINT ROUND ACTUALLY JOINT? ───────────
    #
    # A joint round's purpose is that each seat sees the OTHER seat's blind reply.
    # There are exactly 2 ways that can happen: the brief CARRIES the reply, or the
    # seat goes and READS it from the tree (nothing purges a sibling round unless
    # `blind_of` names it, and for a joint round `blind_of` is empty).
    #
    # BOUND HONESTLY: `input_preview` in the tool transcript is a PREVIEW and may be
    # truncated, so a read can be missed. This is therefore a LOWER bound on
    # exposure-by-reading and an UPPER bound on the "neither" count.
    print("\n  === was each declared joint round actually joint? ===")
    rows, neither = [], []
    for d in sorted(LOGS.iterdir()):
        tj = d / "topology.json"
        if not d.is_dir() or not tj.is_file():
            continue
        try:
            rec = json.loads(tj.read_text(encoding="utf-8"))
        except Exception:
            continue
        parents = [x for x in (rec.get("joint_of") or []) if str(x).strip()]
        if not parents:
            continue
        quoted = set(star.quotes_other_rounds(LOGS, d.name))
        for parent in parents:
            by_brief = parent in quoted
            readers, nonreaders = [], []
            for seat in landed(d) or SEATS:
                tf = next((q for q in sorted(d.glob(f"{seat}.tools*"))), None)
                if tf is None:
                    continue
                try:
                    calls = json.loads(tf.read_text(encoding="utf-8")).get("calls", [])
                except Exception:
                    continue
                # ★ A BARE SUBSTRING MATCH IS WRONG HERE, and the first version
                # of this script made exactly that mistake. `joint_X` CONTAINS
                # `X`, so a seat reading its OWN round directory scored as having
                # read the parent -- which inverted the finding for
                # `joint_clear_the_outstanding_2026-10-12`. The parent name must
                # start at a token boundary. Same shape as the `A13/A14`
                # compound-identifier error of 2026-10-13.
                pat = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(parent))
                hit = any(pat.search(str(c.get("input_preview", "")))
                          for c in calls)
                (readers if hit else nonreaders).append(seat)
            exposure = ("BRIEF" if by_brief
                        else "READ" if readers and not nonreaders
                        else "PARTIAL" if readers
                        else "NEITHER")
            rows.append((d.name, parent, exposure, readers, nonreaders))
            if exposure == "NEITHER":
                neither.append((d.name, parent))
    for name, parent, exposure, readers, nonreaders in rows:
        print(f"    {name}")
        print(f"      joint_of={parent}  exposure={exposure}")
        print(f"      seats that touched the parent: {readers or 'none'}; "
              f"did not: {nonreaders or 'none'}")
    if rows:
        k, n = len(neither), len(rows)
        a, b = wilson(k, n)
        print(f"\n  declared joint, NEITHER quoted nor read: {k}/{n} = {k/n:.6f}")
        if a:
            print(f"    Wilson (statsmodels): [{a[0]:.6f}, {a[1]:.6f}]")
        if b:
            print(f"    Wilson (mpmath)     : [{b[0]:.6f}, {b[1]:.6f}]")
        for name, parent in neither:
            print(f"    ★ {name} was recorded as the joint half of {parent} and "
                  f"exposed NEITHER seat to it")

    if args.json:
        print(json.dumps({
            "live_owed": mine_live, "repaired_owed": mine_fixed,
            "falsely_discharged": newly, "kind_disagreements": dis,
            "forms_agree": agree, "empty_marker_rounds": empty,
        }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
