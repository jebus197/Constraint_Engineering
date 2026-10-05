#!/usr/bin/env python3
"""Models already attach id-addressed falsifiers in-round, and the runner discards them.

THE CLAIM UNDER TEST. The closing sweep's one capability that the round loop lacks is
the id-addressed re-attachment parse — the literal form

    FALSIFIER: C0066
    ```python
    ...runnable code...
    ```

which lets a model attach a runnable falsifier to ANY named finding, several in one
reply. `scripts/sweep_channels_are_post_verdict_2026-10-05.py` shows that form has
exactly ONE parse site repo-wide, at `bench/reference_runner_v3.py:7454`, inside
`_post_convergence_sweep`. In-round, `_extract_routing_falsifier` takes a falsifier
only for the single finding the routing ladder is currently handing out, and
`_apply_routing` refuses anything below severity 0.7
(`scripts/the_counter_and_the_router_disagree_2026-10-05.py`).

THE HYPOTHESIS. The round directive itself asks for this form — `reference_runner_v3.py`
~:4973 records that "a model already answers a labelled `FALSIFIER: <id>` + payload
form in the round directive". If models comply in-round, then id-addressed falsifiers
are ALREADY ARRIVING in round replies and are being thrown away for want of a parser.
That would make the in-round sweep a zero-dispatch change: parse what is already there.

If instead models emit this form only when the sweep prompt asks for it, then an
in-round sweep genuinely needs its own dispatch, and the cost is real.

WHAT THIS MEASURES, over archived round-reply files: how many carry the id-addressed
form, split by phase, and how many of those ids name a finding that was a residual at
the stop point. The parse used here is the SWEEP'S OWN regex, so a hit is by
construction something the sweep would have accepted.

Run:  python3 scripts/in_round_falsifiers_are_discarded_2026-10-05.py
"""
from __future__ import annotations

import argparse
import ast
import glob
import json
import math
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"
RUNNER = REPO / "bench" / "reference_runner_v3.py"

TERMINAL = frozenset({"MERGED", "CLOSED", "REFUTED", "DUPLICATE"})

#: THE SWEEP'S OWN PATTERN, lifted verbatim from reference_runner_v3.py:7454 so that
#: a hit here is by construction a block the sweep would have accepted. Verified
#: against the source at runtime by `_pattern_still_matches_the_runner`.
SWEEP_RE = re.compile(r"FALSIFIER:\s*(C\d{4})\s*```(?:python)?\s*\n(.*?)```", re.S)
#: A bare label with no fenced payload. Counted separately: it is a model trying to
#: comply and failing to produce something runnable, which is a different fact.
BARE_RE = re.compile(r"FALSIFIER:\s*(C\d{4})")


def wilson(k: int, n: int):
    if n == 0:
        return (0.0, 0.0)
    z = 1.959963984540054
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (max(0.0, (c - m) / d) * 100.0, min(1.0, (c + m) / d) * 100.0)


def _pattern_still_matches_the_runner() -> bool:
    """The sweep's regex is copied here; confirm the copy is still faithful."""
    src = RUNNER.read_text(encoding="utf-8")
    return r'FALSIFIER:\s*(C\d{4})\s*```(?:python)?\s*\n(.*?)```' in src


def _can_reach_a_verdict(code: str) -> bool:
    """The runner's own runnability test, in brief: parses as Python AND can produce
    a verdict signal (`assert`/`raise`, the FALSIFIED token in a string, or an
    import). Mirrors `_extract_routing_falsifier`'s accepting signals."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assert, ast.Raise, ast.Import, ast.ImportFrom)):
            return True
        if isinstance(n, ast.Constant) and isinstance(n.value, str) \
                and "FALSIFIED" in n.value:
            return True
    return False


def _parse_args(argv=None):
    p = argparse.ArgumentParser(
        prog="in_round_falsifiers_are_discarded_2026-10-05.py",
        description=__doc__.split("\n\n")[0])
    p.add_argument("--run", default=None, help="one run directory under bench/logs")
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = _parse_args(argv)

    print("=" * 78)
    print("ARE ID-ADDRESSED FALSIFIERS ALREADY ARRIVING IN ROUND REPLIES?")
    print("=" * 78)
    faithful = _pattern_still_matches_the_runner()
    print(f"the sweep's regex is still present verbatim in the runner: {faithful}")
    if not faithful:
        print("  *** the copy here may no longer match what the sweep accepts ***")
    print()

    runs = ([pathlib.Path(args.run)] if args.run
            else sorted({pathlib.Path(p).parent for p in
                         glob.glob(str(LOGS / "*" / "r*_*.json"))}))

    tot_files = tot_with_fenced = tot_with_bare_only = 0
    tot_blocks = tot_runnable = 0
    by_phase = {}
    ids_seen = set()
    per_run = []

    for run in runs:
        files = sorted(glob.glob(str(run / "r*_*.json")))
        files = [f for f in files if re.search(r"/r\d+_[^/]*\.json$", f)]
        if not files:
            continue
        n_f = n_fen = n_bare = n_blk = n_run_ok = 0
        for fp in files:
            try:
                j = json.loads(pathlib.Path(fp).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            if not isinstance(j, dict):
                continue
            resp = j.get("response") or ""
            if not isinstance(resp, str):
                continue
            n_f += 1
            phase = str(j.get("phase") or "?")
            fenced = SWEEP_RE.findall(resp)
            bare = set(BARE_RE.findall(resp))
            d = by_phase.setdefault(phase, {"files": 0, "fenced": 0, "blocks": 0})
            d["files"] += 1
            if fenced:
                n_fen += 1
                d["fenced"] += 1
                d["blocks"] += len(fenced)
                n_blk += len(fenced)
                for cid, code in fenced:
                    ids_seen.add(cid)
                    if _can_reach_a_verdict(code.strip()):
                        n_run_ok += 1
            elif bare:
                n_bare += 1
        tot_files += n_f
        tot_with_fenced += n_fen
        tot_with_bare_only += n_bare
        tot_blocks += n_blk
        tot_runnable += n_run_ok
        if n_f:
            per_run.append((run.name, n_f, n_fen, n_bare, n_blk, n_run_ok))

    print("-" * 78)
    print(f"{'run':<42} {'files':>5} {'fenced':>6} {'bare':>5} {'blks':>5} {'runnable':>8}")
    print("-" * 78)
    for name, n_f, n_fen, n_bare, n_blk, n_ok in per_run:
        if n_fen or n_bare:
            print(f"{name[:42]:<42} {n_f:>5} {n_fen:>6} {n_bare:>5} "
                  f"{n_blk:>5} {n_ok:>8}")
    shown = sum(1 for r in per_run if r[2] or r[3])
    print(f"({shown} of {len(per_run)} runs had any FALSIFIER label; "
          f"runs with none are omitted)")

    print()
    print("-" * 78)
    print("BY PHASE — where in the run the form appears")
    print("-" * 78)
    for ph in sorted(by_phase, key=lambda k: -by_phase[k]["files"]):
        d = by_phase[ph]
        rate = 100.0 * d["fenced"] / d["files"] if d["files"] else 0.0
        print(f"  {ph[:40]:<40} files={d['files']:>5}  with fenced form="
              f"{d['fenced']:>4} ({rate:.2f}%)  blocks={d['blocks']}")

    print()
    print("=" * 78)
    print("POOLED")
    print("=" * 78)
    print(f"round-reply files scanned                : {tot_files}")
    if tot_files:
        lo, hi = wilson(tot_with_fenced, tot_files)
        print(f"carrying the id-addressed FENCED form    : {tot_with_fenced} "
              f"= {100.0 * tot_with_fenced / tot_files:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")
        lo, hi = wilson(tot_with_bare_only, tot_files)
        print(f"carrying a BARE label and no payload     : {tot_with_bare_only} "
              f"= {100.0 * tot_with_bare_only / tot_files:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")
    print(f"total id-addressed blocks                : {tot_blocks}")
    print(f"distinct finding ids addressed           : {len(ids_seen)}")
    if tot_blocks:
        lo, hi = wilson(tot_runnable, tot_blocks)
        print(f"of those blocks, able to reach a verdict : {tot_runnable} "
              f"= {100.0 * tot_runnable / tot_blocks:.4f}%, "
              f"Wilson [{lo:.4f}%, {hi:.4f}%]")

    print()
    print("READING IT.")
    if tot_blocks == 0:
        print("  NOT ONE id-addressed falsifier appears in any archived round reply.")
        print("  So the form is produced only when the sweep prompt asks for it, and")
        print("  an in-round sweep cannot be had by parsing replies the runner")
        print("  already receives — it needs its own offer, and that offer costs a")
        print("  dispatch per round. Design accordingly; do not assume free gain.")
    else:
        print("  Id-addressed falsifiers DO arrive in round replies, and the runner")
        print("  has no in-round parser for them, so they are discarded. Parsing")
        print("  them in-round is a zero-dispatch gain.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
