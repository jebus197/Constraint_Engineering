"""sv reports room for entries it will refuse to save.

THE DEFECT. `cdsfl_sv.py` refuses a save when the memory index reaches
`int(25000 * 0.95) = 23750` characters, and reports its remaining runway from
`_MemoryIndexAudit.headroom`, which is `25000 - chars`. The 2 limits are 1,250
characters apart, so every runway figure sv prints is measured against the
point at which the LOADER truncates rather than the point at which SV ITSELF
REFUSES. `entries_left` inherits the error, because its character branch is
`max(0, self.headroom) // (self.median_entry + 1)`.

WHY IT MATTERS RATHER THAN BEING A ROUNDING QUIBBLE. The index is the thing sv
exists to protect, and the figure sv prints is the only warning anyone gets.
Measured 2026-11-08, with the index at 23,674 characters: sv reports room for
11 more entries while 0 fit before its own refusal. A tool whose job is to
report a runway overstating it by 11 entries is how the index arrives at 76
characters from refusal with nothing having raised an alarm.

WHAT IS NOT CLAIMED HERE. Entry B129 records "3 entries from refusing a save",
and that figure is NOT produced by this arithmetic: sv gives 11. The 3 came
from elsewhere, most likely `the_index_has_run_out_of_movable_parts` at a
smaller index size. An earlier version of this script's own header asserted
that derivation and it is withdrawn, which is why the assertion below checks
only what it measures.

WHY THIS IS NOT REPAIRED HERE. Changing `headroom` or `entries_left` changes
when a gate passes, and `bench/tests/test_sv_rulings.py` PINS the current
meaning deliberately -- `assert audit.headroom == sv._MEMORY_INDEX_LIMIT_CHARS
- audit.chars`. That is the same reason B29 was raised for the founder's ruling
instead of being fixed: a change to when a gate passes is his. This script
measures the gap and stops.
"""
from __future__ import annotations

import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

MEM = (pathlib.Path.home() / ".claude" / "projects"
       / "-Users-georgejackson-Developer-Projects" / "memory")


def measure(mem_dir: pathlib.Path = MEM) -> dict:
    import cdsfl_sv as sv
    a = sv._audit_memory_index(mem_dir)
    limit = sv._MEMORY_INDEX_LIMIT_CHARS
    frac = sv._MEMORY_INDEX_REFUSE_FRACTION
    threshold = int(limit * frac)
    by_loader = max(0, a.headroom) // (a.median_entry + 1)
    by_refuse = max(0, threshold - a.chars) // (a.median_entry + 1)
    return {"chars": a.chars, "lines": a.lines, "median_entry": a.median_entry,
            "loader_limit": limit, "refuse_fraction": frac,
            "threshold": threshold, "headroom_to_loader": a.headroom,
            "room_to_threshold": threshold - a.chars,
            "sv_entries_left": a.entries_left,
            "entries_by_loader": by_loader, "entries_by_refuse": by_refuse}


def main() -> int:
    m = measure()
    print("THE MEMORY INDEX, AND THE 2 LIMITS")
    print(f"  index                        : {m['chars']:,} characters,"
          f" {m['lines']} lines")
    print(f"  loader truncates at          : {m['loader_limit']:,}")
    print(f"  sv REFUSES at                : {m['threshold']:,}"
          f"  ({m['refuse_fraction']:.0%} of the loader limit)")
    print(f"  the 2 are apart by           :"
          f" {m['loader_limit'] - m['threshold']:,} characters")
    print()
    print("WHAT sv REPORTS AGAINST WHAT BINDS")
    print(f"  headroom sv prints           : {m['headroom_to_loader']:,}"
          f"  (to the LOADER limit)")
    print(f"  room before sv REFUSES       : {m['room_to_threshold']:,}")
    print(f"  median entry                 : {m['median_entry']} characters")
    print(f"  entries sv says still fit    : {m['sv_entries_left']}")
    print(f"  entries that fit before the refusal : {m['entries_by_refuse']}")
    gap = m["sv_entries_left"] - m["entries_by_refuse"]
    print(f"  OVERSTATEMENT                : {gap} entries")
    assert m["entries_by_loader"] == m["sv_entries_left"], (
        "sv's entries_left no longer matches the loader-limit arithmetic, so "
        "this script's account of the cause is stale -- re-read it before "
        "quoting the gap")
    assert m["room_to_threshold"] <= m["headroom_to_loader"], \
        "the refuse threshold must not exceed the loader limit"
    print()
    print("  the 2 assertions above check that the CAUSE still holds, not just")
    print("  that the numbers differ: sv's own figure must equal the")
    print("  loader-limit arithmetic for this to be the explanation.")
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    import sys as _sys
    _sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main())
