#!/usr/bin/env python3
"""Reset the immune memory for the upcoming live experiments. ARCHIVES, never deletes.

HIS RULING, 2026-10-16, verbatim: *"No. We reset immune memory for the upcoming
live experiments, since simulation can probably only tell us so much about how
this facility will function in real live/paid experiments. There should be a
facility for researchers to select a switch in the upcoming UX build if they
want immune memory to persist between different experiments, or if they want it
to be reset between experiments. For us in our upcoming use case, since our
models won't change ... probably the best strategy is to leave the default in
this case set to on, so that it can persist between experiments?"* And, pressed
the same day: *"isn't the best time to do this now, immediately before the
transition back to main is made?"*

THREE HALVES, AND ONLY 2 WERE BUILT. The researcher switch exists as
`RunnerConfig.immune_memory_scope`, defaulting to `persist` exactly as he
directed, with its consumer in the runner. The ONE-OFF RESET was named in the
runner's own comment as this file and this file did not exist, so a code comment
promised a mechanism nobody could run. That is what this closes.

WHY A RESET AND NOT AN EDIT. The live store holds priors from 6 experiments and
names only 3 of them -- `free_run1_directive_whole`, `free_run2_severity_spec`
and `leg3_final_shakedown`, which are exactly the 3 SIMULATED shakedown runs.
The memory's own `provenance_complete` property reports this on every load, and
it carries a second consequence the founder was not told about: the
duplicate-ingestion guard refuses an `exp_id` it has SEEN, so it cannot refuse a
re-run of an unnamed one, and re-ingesting any of the 3 live experiments would
silently double its counts. A fresh store has complete provenance by
construction and carries no simulated priors, so the reset answers both.

IT ARCHIVES FIRST AND PROVES THE WRITE BEFORE TOUCHING THE LIVE FILE. Point,
never prune: the priors learned from 6 experiments are evidence and are kept,
with a sidecar recording what they were and why they were set aside. The live
file is replaced only after the archive has been written AND read back
byte-identical. `--restore` puts any archived copy back.

DRY RUN BY DEFAULT.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import shutil
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
LIVE = REPO / "bench" / "state" / "immune_memory.json"
ARCHIVE = REPO / "bench" / "state" / "immune_memory_archive"

#: The simulated runs, by the suffix their ids carry. A stand-in seat's label
#: carries the mandatory `-SIM` suffix by his ruling of 2026-08-08, and a
#: simulated RUN is named by its launcher, so both forms are listed rather than
#: guessed at from the shape of the string.
SIMULATED_MARKERS = ("sim", "free_run", "leg1", "leg2", "leg3", "shakedown")


#: THE REQUIRED SHAPE OF AN IMMUNE MEMORY. A restore that accepts any JSON can
#: destroy the very thing it exists to protect, and this script's own test did
#: exactly that on 2026-10-17: the sidecar `*.why.json` matched the archive glob,
#: sorted AFTER the real copy, and `--restore` wrote it over the live store. The
#: live memory then held `{archived_utc, reason, state_when_archived,
#: restore_with}` and the runner would have loaded 0 priors believing that to be
#: the truth. Recovered byte-exactly from the real archive, which is the whole
#: reason the archive is written and verified first.
REQUIRED_KEYS = frozenset({"version", "experiment_count", "experiment_ids",
                           "records"})


def _is_memory(path: pathlib.Path) -> bool:
    """True only for a file that really is an immune memory."""
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    return isinstance(d, dict) and REQUIRED_KEYS.issubset(d.keys())


def _archived_memories() -> list:
    """Archived MEMORIES, never sidecars. ONE definition, used by list and restore."""
    return sorted(p for p in ARCHIVE.glob("immune_memory_*.json")
                  if not p.name.endswith(".why.json") and _is_memory(p))


def _rel(p: pathlib.Path) -> str:
    """A path for display, which never raises.

    `Path.relative_to` throws when the path is not under the repository, and
    this script's own guard suite drove exactly that by pointing LIVE at a
    temporary directory. A reporting helper that can abort the operation it is
    reporting on is a fault in itself, so it degrades to the absolute path.
    """
    try:
        return str(p.relative_to(REPO))
    except ValueError:
        return str(p)


def _sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _describe(path: pathlib.Path) -> dict:
    if not path.is_file():
        return {"exists": False}
    d = json.loads(path.read_text(encoding="utf-8"))
    ids = list(d.get("experiment_ids") or [])
    sim = [e for e in ids if any(m in e.lower() for m in SIMULATED_MARKERS)]
    recs = d.get("records") or {}
    return {
        "exists": True,
        "sha256": _sha(path),
        "experiment_count": d.get("experiment_count"),
        "experiment_ids": ids,
        "named": len(ids),
        "unnamed": (d.get("experiment_count") or 0) - len(ids),
        "provenance_complete": len(ids) == (d.get("experiment_count") or 0),
        "simulated_named": sim,
        "flaw_classes": sorted(recs.keys()),
        "total_confirmed": round(sum(float(r.get("confirmed") or 0)
                                     for r in recs.values()), 6),
        "total_rejected": round(sum(float(r.get("rejected") or 0)
                                    for r in recs.values()), 6),
    }


def _fresh(old: dict) -> dict:
    """An empty store that keeps the SHAPE and the tuning of the old one."""
    return {
        "version": old.get("version", 1),
        "experiment_count": 0,
        "decay_rate": old.get("decay_rate"),
        "drift_threshold": old.get("drift_threshold"),
        "source_hash": None,
        "experiment_ids": [],
        "records": {},
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true",
                    help="write the reset (default is a dry run)")
    ap.add_argument("--restore", metavar="ARCHIVED_FILE",
                    help="put an archived copy back as the live store")
    ap.add_argument("--list", action="store_true",
                    help="list archived copies and exit")
    a = ap.parse_args()

    ARCHIVE.mkdir(parents=True, exist_ok=True)

    if a.list:
        copies = _archived_memories()
        print(f"archived copies: {len(copies)}")
        for c in copies:
            print(f"  {c.name}  {c.stat().st_size} bytes  sha {_sha(c)[:12]}")
        skipped = [p.name for p in ARCHIVE.glob("immune_memory_*.json")
                   if p not in copies]
        if skipped:
            print(f"  (not restorable, and named rather than hidden: {skipped})")
        return 0

    if a.restore:
        src = pathlib.Path(a.restore)
        if not src.is_absolute():
            src = ARCHIVE / src.name
        if not src.is_file():
            print(f"FATAL: no such archived copy: {src}")
            return 2
        if not _is_memory(src):
            print(f"FATAL: {src.name} is not an immune memory. It lacks "
                  f"{sorted(REQUIRED_KEYS)}, so restoring it would replace the "
                  f"priors with something the runner would read as 0 "
                  f"experiments. REFUSING.")
            print(f"  restorable copies: "
                  f"{[p.name for p in _archived_memories()]}")
            return 2
        before = _describe(LIVE)
        shutil.copy2(src, LIVE)
        print(f"restored {src.name} -> {_rel(LIVE)}")
        print(f"  was: {json.dumps(before)}")
        print(f"  now: {json.dumps(_describe(LIVE))}")
        return 0

    before = _describe(LIVE)
    if not before["exists"]:
        print(f"FATAL: no live immune memory at {_rel(LIVE)}. "
              f"Nothing to reset, and inventing one is not a reset.")
        return 2

    print("=" * 74)
    print("IMMUNE MEMORY RESET, on his ruling of 2026-10-16")
    print("=" * 74)
    print(f"\nlive store: {_rel(LIVE)}")
    for k in ("sha256", "experiment_count", "named", "unnamed",
              "provenance_complete", "flaw_classes",
              "total_confirmed", "total_rejected"):
        print(f"  {k:<22} {before[k]}")
    print(f"\n  every experiment it NAMES, so none is set aside unseen:")
    for e in before["experiment_ids"]:
        tag = "SIMULATED" if e in before["simulated_named"] else "live"
        print(f"    {e}   [{tag}]")
    if before["unnamed"]:
        print(f"\n  AND {before['unnamed']} COUNTED EXPERIMENT(S) IT CANNOT NAME.")
        print(f"  The duplicate-ingestion guard refuses an id it has SEEN, so it")
        print(f"  cannot refuse a re-run of an unnamed one: re-ingesting any of")
        print(f"  those would silently DOUBLE its counts. A fresh store has")
        print(f"  complete provenance by construction, which is a second reason")
        print(f"  for the reset he ordered for the first.")

    if not a.apply:
        print("\n--dry-run (default). Nothing written. Re-run with --apply.")
        return 0

    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    dest = ARCHIVE / f"immune_memory_{stamp}.json"

    # PROVE THE WRITE BEFORE TOUCHING THE LIVE FILE. The recorded rule is never
    # to act before the write is proven; here the act is irreversible in effect
    # if the archive turns out not to be there.
    shutil.copy2(LIVE, dest)
    if not dest.is_file() or _sha(dest) != before["sha256"]:
        print(f"FATAL: the archive copy at {dest} does not match the live file. "
              f"REFUSING to reset: the priors from "
              f"{before['experiment_count']} experiments would be lost.")
        return 2
    sidecar = dest.with_suffix(".why.json")
    sidecar.write_text(json.dumps({
        "archived_utc": stamp,
        "reason": ("his ruling of 2026-10-16: reset immune memory for the "
                   "upcoming live experiments, since simulation can only tell "
                   "us so much about how this facility will function in real "
                   "live/paid experiments"),
        "state_when_archived": before,
        "restore_with": f"python3 {pathlib.Path(__file__).name} --restore {dest.name}",
    }, indent=2), encoding="utf-8")

    old = json.loads(LIVE.read_text(encoding="utf-8"))
    LIVE.write_text(json.dumps(_fresh(old), indent=2) + "\n", encoding="utf-8")
    after = _describe(LIVE)

    print(f"\narchived to {_rel(dest)}")
    print(f"  sidecar   {sidecar.name}")
    print(f"  verified  sha256 matches the live file it copied")
    print(f"\nlive store is now fresh:")
    for k in ("experiment_count", "named", "unnamed", "provenance_complete",
              "flaw_classes", "total_confirmed", "total_rejected"):
        print(f"  {k:<22} {after[k]}")
    print(f"\nRESTORE:  python3 scripts/{pathlib.Path(__file__).name} "
          f"--restore {dest.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
