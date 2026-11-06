#!/usr/bin/env python3
"""Archive a whole dormant section out of MEMORY.md.

THE WIRED CALLER for `cdsfl_sv.archive_stale_memory_entries`'s
`dormant_sections` axis. Without it that parameter would be a capability
nothing reaches, which the project's additive standard names in its second
half as not additive at all.

WHEN TO REACH FOR THIS. `sv` refuses a save when the index crosses its
refuse line. Dated session entries age out on their own. A section that is
UNDATED and no longer live -- a finished project, a historical handoff log --
cannot age out at any window, so it is named here instead. Nothing is
deleted: rows are appended to MEMORY_ARCHIVE.md under a dated heading that
records which route moved them, and a timestamped backup of the index is
written first.

ALWAYS RUN --dry-run FIRST. It reports exactly which rows would move and the
headroom that would result, and writes nothing.

    python3 scripts/archive_a_dormant_memory_section_2026-11-06.py --list
    python3 scripts/archive_a_dormant_memory_section_2026-11-06.py \
        --section "Metis (Agent Harness Project)" --dry-run
"""
from __future__ import annotations
import argparse, pathlib, re, sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cdsfl_sv as sv  # noqa: E402

MEM = pathlib.Path.home() / ".claude/projects/-Users-georgejackson-Developer-Projects/memory"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--section", action="append", default=[],
                    help="exact section title, without the leading '## '. Repeatable.")
    ap.add_argument("--list", action="store_true",
                    help="show every section with its size and bullet count, then exit")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would move and write nothing")
    ap.add_argument("--mem-dir", default=str(MEM))
    args = ap.parse_args()

    mem = pathlib.Path(args.mem_dir)
    idx = mem / sv._MEMORY_INDEX_NAME
    if not idx.is_file():
        print(f"no index at {idx}", file=sys.stderr)
        return 2
    text = idx.read_text(encoding="utf-8")
    thr = int(sv._MEMORY_INDEX_LIMIT_CHARS * sv._MEMORY_INDEX_REFUSE_FRACTION)

    if args.list or not args.section:
        parts = re.split(r"(?m)^(##+ .*)$", text)
        print(f"{idx}: {len(text)} chars, refuse line {thr}, "
              f"headroom {thr - len(text)}")
        print(f"{'section':62s} {'chars':>7s} {'bullets':>8s}")
        for i in range(1, len(parts), 2):
            title = parts[i][3:].strip()
            body = parts[i + 1] if i + 1 < len(parts) else ""
            bullets = sum(1 for l in body.splitlines()
                          if sv._MEMORY_BULLET_RE.match(l))
            print(f"{title[:62]:62s} {len(parts[i]) + len(body):7d} {bullets:8d}")
        if not args.section:
            print("\nname a section with --section to archive it; "
                  "always with --dry-run first")
        return 0

    rep = sv.archive_stale_memory_entries(
        mem, window_days=sv._MEMORY_WINDOW_DAYS, dry_run=args.dry_run,
        dormant_sections=tuple(args.section))
    for k in ("ok", "moved", "freed_chars", "kept_undated", "reason",
              "backup", "archive"):
        print(f"  {k}: {rep[k]}")
    for when, title in rep["moved_titles"]:
        print(f"    {when:>10s}  {title}")
    projected = len(text) - rep["freed_chars"]
    print(f"\n  index {len(text)} -> {projected}, headroom {thr - projected}"
          f"{'  (DRY RUN — nothing written)' if args.dry_run else ''}")
    return 0 if rep["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
