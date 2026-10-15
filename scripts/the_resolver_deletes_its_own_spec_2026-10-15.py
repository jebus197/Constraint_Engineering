#!/usr/bin/env python3
"""WITHDRAWN FIGURES, RECORDED RATHER THAN DELETED. See the superseding producer.

WHAT THIS SCRIPT CLAIMED, AND WHY BOTH FIGURES ARE WITHDRAWN. Its first version
reported, over the 5 models and 10 domains of the real compose grid:

    HARD deleted: 45
    SOFT deleted: 475

NEITHER NUMBER MEASURED DELETION. The classification asked whether each
pre-resolution block appeared in the list produced by RE-SPLITTING the
post-resolution packet text. `resolve_layer_conflicts` rebuilt each packet by
joining its kept blocks with a SINGLE newline, while
`_split_packet_directives` splits on BLANK lines and strips every line -- so a
round trip through the resolver merged blocks that a blank line had separated
and removed their indentation. The 520 "deletions" were that round-trip
asymmetry. Measured directly on the structural domain packet: 4,515 characters
and 18 blocks in, 4,403 characters and 5 blocks out, with **0 blocks lost**
under verbatim containment.

THE ASYMMETRY WAS A REAL DEFECT AND IS NOW FIXED -- a packet that loses nothing
passes through byte-identical -- but it was never the defect this script's
numbers described, and a figure that measures the wrong thing is worse than no
figure, because it is believed.

THE HONEST FIGURES, and the producer that holds them, is
`scripts/the_spec_is_not_work_2026-10-15.py`:

  * 40 of 42 conflicts were the specification resolved AGAINST ITSELF --
    95.2381%, Wilson [84.2101%, 98.6842%] -- against 2 cross-layer and 0
    same-layer.
  * 41 of the 42 deletions had a HARD loser by the resolver's own HARD
    predicate -- `constraint_class == "HARD" or _block_is_hard(text)` -- since
    the universal packet is classed HARD. 40 were blocks of the project's own
    specification; the 41st was the biomedical pre-specified-sample-size
    formula. **A SECOND WITHDRAWAL, RECORDED HERE WITH THE FIRST**: an earlier
    reading of this said 11, having applied `_block_is_hard` to
    `ConflictRecord.loser_text`, which is truncated to 100 characters and
    carries no packet class.
  * After the repair: 2 conflicts recorded, 0 HARD deletions, 0 blocks lost.

WHY THIS FILE IS KEPT. `measured-rate-travels-with-its-script` means a number
must have a producer. The inverse obligation is that a WITHDRAWN number must
have a record of its withdrawal, or the same mistake is available to be made
again. Running this file prints the withdrawal and then runs the correct
producer, so the 2 can never be read apart.
"""
from __future__ import annotations

import pathlib
import runpy
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]
SUPERSEDED_BY = REPO / "scripts" / "the_spec_is_not_work_2026-10-15.py"


def main() -> int:
    print("=" * 78)
    print("WITHDRAWN 2026-10-15: 'HARD deleted: 45' and 'SOFT deleted: 475'")
    print("=" * 78)
    print(__doc__.strip())
    print()
    print("=" * 78)
    print(f"RUNNING THE SUPERSEDING PRODUCER: {SUPERSEDED_BY.name}")
    print("=" * 78)
    if not SUPERSEDED_BY.is_file():
        print(f"  MISSING: {SUPERSEDED_BY}", file=sys.stderr)
        return 1
    runpy.run_path(str(SUPERSEDED_BY), run_name="__main__")
    return 0


def _answer_help_without_measuring(doc: str) -> None:
    """A `--help` MUST NEVER COST ANYTHING, and that is a founder-standing rule:
    15 of 17 runners once billed a live dispatch on any unrecognised argument.
    This script's measurement is free, but the rule is about the SHAPE: a flag
    that silently runs the whole measurement is indistinguishable from a flag
    that silently spends. Guarded by
    `bench/tests/test_help_is_answered_2026-09-11.py`.
    """
    import argparse
    ap = argparse.ArgumentParser(
        prog=pathlib.Path(__file__).name,
        description=(doc or "").strip().splitlines()[0] if doc else None,
        epilog="Takes no arguments: run it with none to produce the measurement.",
    )
    ap.parse_args()


if __name__ == "__main__":
    _answer_help_without_measuring(__doc__)
    raise SystemExit(main())
