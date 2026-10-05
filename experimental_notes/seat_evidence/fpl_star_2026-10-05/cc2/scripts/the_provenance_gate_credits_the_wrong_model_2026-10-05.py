# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'fpl_star_2026-10-05', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: ed3e0dd47875507e99bf4683c9e6c8147c5234709d20db494fda64b0a3353aaf
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""The provenance check credits a routed confirmation to the model that FAILED.

WHY THIS EXISTS (panel review, 2026-10-05, claude seat). The proposal
`experimental_notes/Proposal_Fingerprint_Falsification_Dimension_2026-10-05.md`
would promote `scripts/competence_provenance.py` from an advisory record to a GATE
on pool entry for a measured falsification rate that reorders `bench/routing.py`'s
ladder. Before it can gate anything it has to attribute each falsifier to the model
that wrote it. It does not.

THE DEFECT, in two lines of the runner. In `bench/reference_runner_v3.py`, the
`elif result.resolved:` branch of the routing block does:

    e["falsifier_code"] = result.falsifier_code
    e["falsifier_verdict"] = "CONFIRMED"
    ...
    e["resolved_by_routing"] = result.model_used

So on every routed resolution the entry's `falsifier_code` is REPLACED by the
resolving rung's falsifier, while `source_model` still names the weak model whose
own falsifier failed. `competence_provenance.analyse` keys on
`e.get("source_model")`. Every routed CONFIRMED is therefore credited to the model
that failed and withheld from the model that succeeded, and the falsifier whose
provenance is classified was not written by the model it is filed under.

DIRECTION OF THE ERROR. It is not noise. It moves confirmations from resolvers to
sources, i.e. it DEPRESSES the rate of exactly the models the ladder puts at the top
and INFLATES the rate of the models it puts at the bottom. That is the same
direction as the selection effect the proposal names as its strongest objection, so
the two compound rather than cancel.

This script measures the size of the error over the archive. Read-only.
"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent


def _help_requested() -> bool:
    return any(a in ("-h", "--help") for a in sys.argv[1:])


def _print_usage_and_exit() -> None:
    print((__doc__ or "").strip())
    print()
    print(f"usage: {sys.argv[0].split('/')[-1]} [report.json ...]")
    raise SystemExit(0)


def measure(reports) -> dict:
    """Count entries whose falsifier author is not the entry's source_model."""
    tot = routed = routed_confirmed = misattributed = 0
    moves: collections.Counter = collections.Counter()
    examples: list = []
    for p in reports:
        try:
            d = json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
        except Exception:
            continue
        ents = ((d.get("registry") or {}).get("entries") or {})
        for cid, e in ents.items():
            if not isinstance(e, dict):
                continue
            tot += 1
            author = e.get("resolved_by_routing")
            if not author:
                continue
            routed += 1
            if e.get("falsifier_verdict") == "CONFIRMED":
                routed_confirmed += 1
                src = e.get("source_model")
                if src and str(src) != str(author):
                    misattributed += 1
                    moves[(str(src), str(author))] += 1
                    if len(examples) < 6:
                        examples.append(
                            (pathlib.Path(p).parent.name, cid, src, author))
    return {"entries": tot, "routed": routed, "routed_confirmed": routed_confirmed,
            "misattributed": misattributed, "moves": moves, "examples": examples}


def main() -> int:
    if _help_requested():
        _print_usage_and_exit()
    reports = [pathlib.Path(a) for a in sys.argv[1:]] or sorted(
        REPO.glob("bench/logs/*/*_report.json"))
    reports = [p for p in reports if p.is_file()]
    if not reports:
        print("  no report found"); return 1
    r = measure(reports)
    print("=" * 78)
    print("WHO WROTE THE FALSIFIER THE CONFIRM RATE IS BUILT FROM")
    print("=" * 78)
    print(f"  reports scanned                                  : {len(reports)}")
    print(f"  registry entries                                 : {r['entries']}")
    print(f"  entries resolved by the routing ladder           : {r['routed']}")
    print(f"    ...of which CONFIRMED                          : "
          f"{r['routed_confirmed']}")
    print("  CONFIRMED entries whose falsifier was written by")
    print("  a model OTHER than the one competence_provenance")
    print(f"  files them under (`source_model`)                : "
          f"{r['misattributed']}")
    if r["entries"]:
        print(f"  share of all entries misattributed               : "
              f"{100.0 * r['misattributed'] / r['entries']:.3f}%")
    if r["routed_confirmed"]:
        print(f"  share of ROUTED confirmations misattributed      : "
              f"{100.0 * r['misattributed'] / r['routed_confirmed']:.3f}%")
    print()
    print("  credit moved FROM (source_model) -> TO (resolved_by_routing):")
    for (src, dst), n in r["moves"].most_common(12):
        print(f"    {src:<14} -> {dst:<14} {n:>4}")
    print()
    for x in r["examples"]:
        print(f"    e.g. {x[0]} {x[1]}: filed under {x[2]}, written by {x[3]}")
    print()
    print("  READING IT. Every misattributed entry is a CONFIRMATION, so the whole")
    print("  error sits in the NUMERATOR of the rate the proposal would rank on, and")
    print("  it always moves credit from a resolver to a source. A gate built on this")
    print("  attribution does not merely admit the wrong models -- it computes the")
    print("  ladder's own ordering backwards on the routed population.")
    print()
    print("  FIX, as shipped alongside this script: competence_provenance.analyse now")
    print("  keys on `resolved_by_routing or source_model`, pinned by")
    print("  bench/tests/test_provenance_credits_the_falsifier_author_2026-10-05.py")
    return 0 if r["misattributed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
