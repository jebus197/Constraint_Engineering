#!/usr/bin/env python3
"""Recover finding descriptions that the parser mangled, WITHOUT touching the archive.

WHAT THIS REPAIRS
-----------------
Until 2026-08-17 `runner_core.parse_findings` fell through to `block[:200]` on
15.1% of finding blocks, and that fallback does not truncate a description — it
SUBSTITUTES the raw schema header for it. The stored "description" for those
findings reads `FINDING_ID: F006\\nSEVERITY: 0.80\\nFIND: <first ~130 chars>`.
A second cap, `finding.description[:500]` in `FindingRegistry.register`, clipped
a further 29%.

Both reach live machinery — the location-keyed convergence count reads the
registry description (`reference_runner_v3.py:4288`), as does the CC2
verification prompt (`:6271`). So the archived registries under-describe what the
models actually said, and any measurement derived from them inherits that.

The parser is now fixed. This script re-parses each run's archived raw model
responses with the CURRENT parser and writes what the description SHOULD have
been, so analysis can be re-derived without a paid re-run.

WHY IT WRITES A SIDECAR AND NEVER EDITS THE REPORT
--------------------------------------------------
The archived reports are evidence. Rewriting them in place would destroy the
"before" state, make every prior measurement unreproducible, and leave no way to
tell a repaired figure from an original one — which is the same provenance
failure this project keeps finding in its own instruments. So each run gets

    bench/logs/<run>/descriptions_backfill.json

and every consumer opts in explicitly. Nothing reads it by default.

THE JOIN IS VERIFIED, NOT ASSUMED
---------------------------------
A registry entry is matched to a re-parsed finding on `(source_model,
source_alias)`, and the match is then CHECKED against the stored text before it
is trusted:

  * `prefix`     - stored is exactly the first N chars of the recovered text.
                   This is the 500-cap case and the check is exact.
  * `fallback`   - stored is exactly `block[:200]` of the block the finding came
                   from, i.e. the parser's old failure signature, and the
                   recovered text comes from re-parsing that same block.
  * `unverified` - the join produced text that satisfies neither check. NOT
                   written as a repair; counted and reported so the coverage
                   figure is honest.

Anything that cannot be verified is left alone. A silent bad join here would
corrupt exactly the measurements this exists to correct.

Usage
-----
    python3 scripts/backfill_descriptions.py --report        # coverage only
    python3 scripts/backfill_descriptions.py --write         # write sidecars
    python3 scripts/backfill_descriptions.py --write --run exp47_divergence
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from bench.runner_core import parse_findings  # noqa: E402

SIDECAR = "descriptions_backfill.json"

# The parser's own block splitter and reject guards, mirrored so a block can be
# matched to the `block[:200]` a failed parse would have produced.
_FID_PAT = (r'\*{0,2}[Ff][Ii][Nn][Dd][Ii][Nn][Gg][\s_-]*'
            r'[Ii][Dd]\*{0,2}\s*[:=\-]\s*')
_LEAK = {"full_id", "finding_id", "description", "target_file", "proposed_fix",
         "model_id", "round_idx", "severity", "flaw_class", "abstraction",
         "verified", "fid", "raw_fid"}


def _raw_response_files(run_dir: pathlib.Path):
    for p in sorted(run_dir.glob("*.json")):
        m = re.match(r"r(?:ound)?(\d+)_([A-Za-z0-9]+)_", p.name)
        if not m:
            continue
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(j, dict) and isinstance(j.get("response"), str):
            yield int(m.group(1)), (j.get("model_label") or m.group(2)), j["response"]


def recovered_index(run_dir: pathlib.Path) -> dict:
    """(model, finding_id) -> LIST of (round, recovered_description, block).

    A LIST, not a single value, and that is the whole point. Models re-file the
    same `F001` in round after round, so keying one entry per (model, id) — which
    an earlier draft of this script did with `setdefault` — silently joins a
    round-0 block to a round-3 registry entry. It looked like it worked: the join
    succeeded, the text was plausible, and 23 of exp47's repairs were quietly
    wrong. The content check below is what caught it, which is the argument for
    having the check at all rather than trusting the key.
    """
    idx: dict = {}
    for rnd, label, resp in _raw_response_files(run_dir):
        parsed = {f.finding_id: (f.description or "")
                  for f in parse_findings(label, rnd, resp)}
        for b in re.split(rf'(?={_FID_PAT})', resp):
            b = b.strip()
            m = re.match(_FID_PAT + r'(\S+)', b)
            if not m:
                continue
            # CC2 writes `**FINDING_ID:** F001`, putting the separator INSIDE the
            # bold markers, so the raw capture is `**` and the real id follows.
            # Strip the markers and re-take the token; without this every CC2
            # finding indexes under the key `**` and joins to nothing.
            fid = m.group(1).strip().rstrip(",;)]} ").strip("*")
            if not fid:
                nxt = b[m.end(1):].strip().split()
                fid = nxt[0].rstrip(",;)]} ").strip("*") if nxt else ""
            if not fid or fid.lower() in _LEAK:
                continue
            desc = parsed.get(fid) or parsed.get(f"{label}_{fid}") or ""
            for key in ((label, fid), (label, f"{label}_{fid}")):
                idx.setdefault(key, []).append((rnd, desc, b))
    return idx


def backfill_run(run_dir: pathlib.Path) -> dict | None:
    reports = [p for p in run_dir.glob("*_report.json") if ".errata" not in str(p)]
    if not reports:
        return None
    try:
        entries = (json.loads(reports[0].read_text(encoding="utf-8"))
                   .get("registry") or {}).get("entries") or {}
    except Exception:
        return None
    if not entries:
        return None

    idx = recovered_index(run_dir)
    out: dict = {}
    stats = {"entries": len(entries), "prefix": 0, "fallback": 0,
             "unverified": 0, "no_join": 0, "unchanged": 0, "ambiguous": 0}

    for cid, e in entries.items():
        stored = e.get("description") or ""
        model = e.get("source_model") or ""
        aliases = e.get("source_aliases") or []
        if isinstance(aliases, str):          # some archives store it as a repr
            aliases = re.findall(r"'([^']+)'", aliases) or [aliases]

        cands = []
        for a in aliases:
            for key in ((model, a), (model, f"{model}_{a}")):
                cands.extend(idx.get(key, []))
        if not cands:
            stats["no_join"] += 1
            continue

        # Every candidate is tested against the stored text; only a candidate
        # that reproduces the stored value exactly — as a prefix, or as the
        # `block[:200]` the old fallback would have cut — is eligible.
        hits = []
        for _rnd, rec, blk in cands:
            rec = (rec or "").strip()
            if not rec:
                continue
            if rec == stored.strip():
                hits.append(("unchanged", rec))
            elif stored and rec.startswith(stored):
                hits.append(("prefix", rec))
            elif stored and blk.strip()[:len(stored)] == stored:
                hits.append(("fallback", rec))

        if not hits:
            stats["unverified"] += 1
            continue
        if any(m == "unchanged" for m, _ in hits):
            stats["unchanged"] += 1
            continue

        distinct = {r for _m, r in hits}
        if len(distinct) > 1:
            # Two different rounds both reproduce the stored text. Which one the
            # registry entry came from is not decidable from the archive, so the
            # entry is left alone rather than repaired on a coin toss.
            stats["ambiguous"] += 1
            continue

        method, rec = hits[0]
        stats[method] += 1
        out[cid] = {"method": method, "stored_len": len(stored),
                    "recovered_len": len(rec), "description": rec}

    return {"run": run_dir.name, "stats": stats, "descriptions": out}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="write the sidecar files")
    ap.add_argument("--report", action="store_true", help="coverage only (default)")
    ap.add_argument("--run", help="substring filter on the run directory name")
    args = ap.parse_args()

    dirs = [d for d in sorted((REPO / "bench" / "logs").iterdir())
            if d.is_dir() and (not args.run or args.run in d.name)]
    tot = {"entries": 0, "prefix": 0, "fallback": 0, "unverified": 0,
           "no_join": 0, "unchanged": 0, "ambiguous": 0}
    rows = []
    for d in dirs:
        r = backfill_run(d)
        if not r:
            continue
        for k in tot:
            tot[k] += r["stats"][k]
        rows.append(r)
        if args.write and r["descriptions"]:
            (d / SIDECAR).write_text(json.dumps(r, indent=1), encoding="utf-8")

    print(f"{'run':44s}{'entries':>8s}{'prefix':>8s}{'fallbk':>8s}{'unver':>7s}{'ambig':>7s}{'nojoin':>8s}")
    for r in rows:
        s = r["stats"]
        print(f"{r['run'][:44]:44s}{s['entries']:8d}{s['prefix']:8d}"
              f"{s['fallback']:8d}{s['unverified']:7d}{s['ambiguous']:7d}{s['no_join']:8d}")
    rep = tot["prefix"] + tot["fallback"]
    print(f"\n{'TOTAL':44s}{tot['entries']:8d}{tot['prefix']:8d}"
          f"{tot['fallback']:8d}{tot['unverified']:7d}{tot['ambiguous']:7d}{tot['no_join']:8d}")
    print(f"\n  repaired (verified join)   {rep}")
    print(f"  already correct            {tot['unchanged']}")
    print(f"  join found but UNVERIFIED  {tot['unverified']}  (left alone by design)")
    print(f"  ambiguous across rounds    {tot['ambiguous']}  (left alone by design)")
    print(f"  no raw response on disk    {tot['no_join']}")
    if args.write:
        print(f"\n  sidecars written as bench/logs/<run>/{SIDECAR}")
        print("  the archived reports were NOT modified.")
    else:
        print("\n  dry run — pass --write to create the sidecars.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
