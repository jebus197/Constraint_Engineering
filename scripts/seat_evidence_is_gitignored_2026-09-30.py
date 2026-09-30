#!/usr/bin/env python3
"""MEASUREMENT: how much seat-written evidence lives ONLY inside the gitignored
sandbox harvest, and is therefore unversioned and unrecoverable after a reboot.

FOUND 2026-09-30 while committing the falsifier-root-cause panel round. `git add
-A` staged 20 files from that round's harvest and left 88 out. The 20 it took are
BYTE-IDENTICAL to files already tracked at their canonical paths (cmp, 20 of 20,
0 differ). The 88 it left included the 3 seat-written falsifiers that produced
every figure the round published -- `0 of 5` vs `5 of 5`, Fisher p = 7.936508e-03,
the constant 52/55 e2 gate. The selection is exactly inverted: the redundant
copies are versioned and the unique evidence is not.

THE CAUSE is one line, `.gitignore:48 bench/logs/**`, which cannot distinguish a
harvest copy of an already-tracked artefact from a script that exists nowhere
else. `git check-ignore` confirms it for every one of the 88.

WHY IT IS ABOVE THRESHOLD. The project's own directive
`measured-rate-travels-with-its-script` requires a quoted rate to be committed
alongside the script that produced it, and records that the project already
learned this once: `scripts/similarity_operating_characteristic.py` was written
on 2026-09-01 because a justifying measurement "lived only as PROSE COMMENTS".
A script sitting in a gitignored directory is the same defect wearing a filename.
`scripts/panel_figure_provenance_2026-09-20.py` makes it concrete -- it names
harvest paths as the "producer" of published figures, so on a fresh clone those
producers are simply absent.

WHAT THIS SCRIPT DECIDES, by execution and not by reading:
  * every .py under any */sandbox_harvest/**/files/ in bench/logs;
  * for each, whether git ignores it (`git check-ignore`, the real decider);
  * whether the same basename exists at its canonical in-tree path, and whether
    git TRACKS that path (`git ls-files --error-unmatch`);
  * whether the harvest copy is byte-identical to the tracked file (hashlib), so
    a duplicate is not counted as preserved evidence when it is merely a copy,
    and a DIVERGED copy is reported separately because that is seat work too;
  * PRESERVED means: a tracked in-tree file exists for it. UNPRESERVED means the
    script exists only inside ignored space.
Wilson score interval on the unpreserved proportion, plus a per-round table.

Exit 0 always: this is a measurement, not a gate. The gate is the companion test.
"""
from __future__ import annotations

import hashlib
import subprocess
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "bench" / "logs"
HARVEST_DIRS = ("sandbox_harvest", "worktree_harvest", "panel_worktree_harvest")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _ignored(paths: list[Path]) -> set[Path]:
    """The real decider. `git check-ignore` prints only the ignored inputs."""
    if not paths:
        return set()
    out: set[Path] = set()
    CHUNK = 400
    for i in range(0, len(paths), CHUNK):
        batch = [str(p.relative_to(ROOT)) for p in paths[i:i + CHUNK]]
        r = subprocess.run(["git", "check-ignore", "--stdin"], cwd=ROOT,
                           input="\n".join(batch), capture_output=True, text=True)
        for line in r.stdout.splitlines():
            if line.strip():
                out.add(ROOT / line.strip())
    return out


def _tracked(paths: list[Path]) -> set[Path]:
    if not paths:
        return set()
    r = subprocess.run(["git", "ls-files", "-z", "--"] + [str(p.relative_to(ROOT)) for p in paths],
                       cwd=ROOT, capture_output=True, text=True)
    return {ROOT / s for s in r.stdout.split("\0") if s}


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> None:
    finds: list[tuple[str, Path, Path]] = []   # (round, harvest path, canonical rel path)
    for hd in HARVEST_DIRS:
        for f in sorted(LOGS.glob(f"*/{hd}/*/attempt-*/files/**/*.py")):
            parts = f.parts
            i = parts.index("files")
            canon = Path(*parts[i + 1:])
            rnd = parts[parts.index("logs") + 1]
            finds.append((rnd, f, canon))

    ignored = _ignored([f for _, f, _ in finds])
    canon_abs = [ROOT / c for _, _, c in finds]
    tracked = _tracked([p for p in canon_abs if p.exists()])

    rows = []
    for rnd, f, canon in finds:
        c = ROOT / canon
        in_tree = c.exists()
        is_tracked = c in tracked
        identical = in_tree and _sha(f) == _sha(c)
        rows.append({"round": rnd, "harvest": f, "canon": canon, "ignored": f in ignored,
                     "in_tree": in_tree, "tracked": is_tracked, "identical": identical})

    n = len(rows)
    ign = sum(r["ignored"] for r in rows)
    unpres = [r for r in rows if not r["tracked"]]
    diverged = [r for r in rows if r["tracked"] and not r["identical"]]

    print(f"seat .py files found in harvest space: {n}")
    print(f"  ignored by git          : {ign} of {n}" + (f" = {100*ign/n:.4f}%" if n else ""))
    lo, hi = wilson(len(unpres), n)
    print(f"  UNPRESERVED (no tracked in-tree file): {len(unpres)} of {n}"
          + (f" = {100*len(unpres)/n:.4f}%, Wilson [{100*lo:.4f}%, {100*hi:.4f}%]" if n else ""))
    print(f"  tracked but DIVERGED from harvest copy: {len(diverged)} of {n}"
          "   (seat edits to tracked files; provenance of the edit is in the harvest only)")

    per = defaultdict(lambda: [0, 0])
    for r in rows:
        per[r["round"]][0] += 1
        if not r["tracked"]:
            per[r["round"]][1] += 1
    print("\nper round   total  unpreserved")
    for rnd in sorted(per):
        t, u = per[rnd]
        mark = "  <== evidence stranded" if u else ""
        print(f"  {rnd:58s} {t:4d} {u:5d}{mark}")

    if unpres:
        print("\nUNPRESERVED, by canonical path (the scripts that exist nowhere a clone can reach):")
        seen = set()
        for r in sorted(unpres, key=lambda r: (str(r["canon"]), r["round"])):
            key = (str(r["canon"]), r["round"])
            if key in seen:
                continue
            seen.add(key)
            print(f"  {r['canon']}\n      round {r['round']}  ignored={r['ignored']}")


if __name__ == "__main__":
    main()
