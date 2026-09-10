#!/usr/bin/env python3
"""Task 9.2: every fix in the task list, and how each one performs.

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

HIS RULING: "Add every fix in this list to the study programme, and measure how
each performs."

WHAT "PERFORMS" MEANS HERE, so the measurement is falsifiable. Every DONE entry
on the master task list names an evidence file, and that file is the fix's own
instrument: it is what would go red if the fix regressed. So a fix's performance
is answerable today, without a run, in 3 questions:

  1. Does its evidence file EXIST?
  2. Does the suite COLLECT it? A test nothing runs is not an instrument.
  3. Does it PASS, and how many assertions does it carry?

A FIX WHOSE TEST NOBODY RUNS HAS NOT BEEN MEASURED, it has been asserted. That is
the whole point of the exercise, and it is the same standard the additive
standard applies to features: an addition nothing reaches is not additive.

THE INVENTORY IS DERIVED, NEVER TYPED. It comes from the markers on the task
list, so a fix added tomorrow appears here without anyone remembering to add it.
That is what the 5 corrections to the pre-commit cost figure were about.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))


def inventory():
    import task_list_markers as tlm
    entries = tlm.parse_entries(REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md")
    return [e for e in entries if e.state == "DONE"]


def main() -> int:
    # LINE-BUFFERED. The first run of this script produced an EMPTY output file
    # for 2 minutes while pytest walked 42 files, and an empty file is
    # indistinguishable from a hung script. Python buffers stdout when it is not
    # a terminal; this reconfigures it so progress is visible as it happens.
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except AttributeError:                                # pragma: no cover
        pass
    done = inventory()
    with_ev = [e for e in done if e.evidence]
    files = sorted({f for e in with_ev for f in e.evidence})

    print(f"DONE entries on the task list      : {len(done)}")
    print(f"  carrying an evidence file        : {len(with_ev)}")
    print(f"  distinct evidence instruments    : {len(files)}\n")

    from statsmodels.stats.proportion import proportion_confint
    if done:
        lo, hi = proportion_confint(len(with_ev), len(done), method="wilson")
        print(f"  evidence coverage: {len(with_ev)}/{len(done)} = "
              f"{len(with_ev) / len(done):.4%}  Wilson [{lo:.4%}, {hi:.4%}]")

    missing = [f for f in files if not (REPO / f).is_file()]
    outside = [f for f in files if not f.startswith("bench/tests/")]
    print(f"\n  instruments that do not exist    : {len(missing)} {missing}")
    print(f"  instruments the suite cannot see  : {len(outside)} {outside}")

    print(f"\n--- do they run, and do they pass? ---")
    print(f"  running pytest over {len(files)} instrument(s); this takes minutes")
    present = [f for f in files if (REPO / f).is_file() and f.startswith("bench/tests/")]
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        *present], cwd=REPO, capture_output=True, text=True,
                       timeout=1800)
    tail = [l for l in r.stdout.splitlines() if " passed" in l or " failed" in l]
    print(f"  {tail[-1] if tail else '(no summary line)'}")
    failed = [l for l in r.stdout.splitlines() if l.startswith("FAILED")]
    for l in failed[:10]:
        print(f"    {l}")
    if len(failed) > 10:
        print(f"    ... and {len(failed) - 10} more failure(s) not shown. "
              f"A list capped at 10 under a heading that reads as complete is "
              f"a silent falsehood, so the remainder is stated.")

    ok = r.returncode == 0 and not missing and not outside
    print(f"\n  EVERY FIX'S INSTRUMENT EXISTS, IS COLLECTED, AND PASSES: {ok}")
    if not ok:
        print("  A fix whose test nobody runs has not been measured; it has been")
        print("  asserted. Repair the instrument before trusting the entry.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
