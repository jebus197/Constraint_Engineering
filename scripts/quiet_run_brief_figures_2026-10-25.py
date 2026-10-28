#!/usr/bin/env python3
"""The declared figures for the 2026-10-25 quiet-run panel brief.

WHY A SEPARATE SCRIPT. A panel brief's declared-figure check re-executes a BARE
SCRIPT PATH, with no room for an argument, so `producer.py --figures` cannot be
declared. This wrapper exists for the same reason
`scripts/night_run_brief_figures_2026-10-02.py` does.

WHY DECLARING THEM MATTERS. A number typed into a brief's prose is never checked.
A declared figure is RE-EXECUTED before the brief is allowed out. The project
learned this when `gamma is 0.451` reached 2 seats and the true value was
0.415413.

Every figure here is produced by `bench/what_should_the_quiet_run_be_2026-10-25.py`
over the live archive. Nothing is typed.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
PRODUCER = REPO / "bench" / "what_should_the_quiet_run_be_2026-10-25.py"


def main() -> int:
    # `--help` MUST NOT COST MONEY, AND MUST NOT COST A MEASUREMENT EITHER.
    # The first version of this wrapper overwrote sys.argv unconditionally, so
    # `--help` silently ran the whole archive sweep and printed figures instead of
    # a usage line. The commit gate caught it: "exit 0 but no usage line -- the
    # flag was ignored". This is the project's own rule, measured once at 15 of 17
    # runners billing for a help flag.
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        print("usage: quiet_run_brief_figures_2026-10-25.py")
        print()
        print("Prints the declared figures for the 2026-10-25 quiet-run panel brief,")
        print("so a brief's declared-figure check can RE-EXECUTE them. Takes no")
        print("arguments. The figures come from")
        print("bench/what_should_the_quiet_run_be_2026-10-25.py over the live archive;")
        print("nothing here is typed.")
        return 0
    # AND AN UNRECOGNISED ARGUMENT EXITS 2 RATHER THAN BEING IGNORED -- added
    # 2026-10-28. The help branch above was correct and incomplete: anything
    # that is NOT -h or --help fell straight through and ran the whole sweep
    # with exit 0, so `--this-flag-does-not-exist` read as success. The project
    # already holds this rule in test_operational_scripts, in these words: "a
    # script that accepts `--fix-timestamps` and does nothing with it is the
    # 118-day no-op again".
    if sys.argv[1:]:
        print(f"usage: {pathlib.Path(__file__).name}", file=sys.stderr)
        print(f"unrecognised argument(s): {' '.join(sys.argv[1:])}",
              file=sys.stderr)
        print("This script takes no arguments. Refusing rather than ignoring "
              "them.", file=sys.stderr)
        return 2
    spec = importlib.util.spec_from_file_location("_qr", PRODUCER)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_qr"] = m
    spec.loader.exec_module(m)
    sys.argv = [str(PRODUCER), "--figures"]
    return m.main()


if __name__ == "__main__":
    sys.exit(main())
