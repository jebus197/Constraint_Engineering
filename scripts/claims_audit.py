#!/usr/bin/env python3
"""Check what the canonical documents ASSERT against what the data SAYS.

FOUNDER INSTRUCTION 2026-08-27: "Make deliberate and real efforts to ensure such
issues do not occur again! We have significant and previously effective
resources designed to guard against such errors and conflation, such as
MEMORY.md, RECOVERY.md, ONBOARDING.md, the repo and Git itself, our docs and our
experimental notes. Use them as appropriate in all cases."

THE CLASS THIS EXISTS FOR. Three times in 48 hours a canonical document asserted
a fact about data, the data said otherwise, and CC1 acted on the document
without opening the data. Every one reached the founder as a decision to make:

  2026-08-26  ".claude/CLAUDE.md and the runner dataclass say merge arbitration
              defaults False" -> TRUE in every config exp40..exp52. CC1 read the
              default and never opened a config file -- the SECOND time that
              exact error was made, the first being recorded in the runner's own
              comment five days earlier.
  2026-08-27  "RECOVERY.md: the 133 unadjudicated pairs -- PENDING FOUNDER
              RULING" -> adjudicated by tool on 2026-08-18, results sitting in
              experimental_notes/data/. CC1 recommended routing all 133 to the
              founder: the problem-generator failure.
  2026-08-28  "replay_accounting.py: no archived report carries a rho series in
              any form -- measured" -> 22 of 31 carry it per round. The word
              "measured" was doing work no code did.

The shape is identical each time: a PROSE CLAIM ABOUT DATA, aging silently while
the data moved. Documents cannot check themselves, and a reader who trusts them
inherits the staleness. So each such claim gets a checker, and the checker runs.

DELIBERATELY NARROW. This does not attempt to verify prose in general, which is
not decidable. It verifies a REGISTRY of specific claims whose data source is
named. Adding a claim is cheap; the point is that a claim which cannot be
checked does not belong in a canonical document as a fact.

Exit 0 when every registered claim still holds, 1 when one has gone stale.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


def _read(rel):
    p = REPO / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


# ── the checkers ─────────────────────────────────────────────────────────────

def merge_arbitration_default():
    """CLAIM: merge arbitration is off unless a config enables it."""
    on = off = 0
    for c in sorted(REPO.glob("bench/exp*_configs/*.json")):
        try:
            v = json.loads(c.read_text()).get("merge_arbitration_enabled")
        except (OSError, ValueError):
            continue
        if v is True:
            on += 1
        elif v is False:
            off += 1
    if on and not off:
        return False, (f"merge_arbitration_enabled is True in {on} configs and False in "
                       f"none. The dataclass default is not what any run uses.")
    return True, f"{on} configs enable it, {off} disable it"


def rho_series_absent():
    """CLAIM: no archived report carries a rho series."""
    have = tot = 0
    for d in sorted((REPO / "bench" / "logs").iterdir()) if (REPO / "bench/logs").is_dir() else []:
        if not (d.is_dir() and re.match(r"^exp\d+", d.name)):
            continue
        for f in sorted(d.glob("*_report.json")):
            try:
                r = json.loads(f.read_text())
            except (OSError, ValueError):
                continue
            tot += 1
            rounds = r.get("rounds")
            if isinstance(rounds, list) and any(
                    isinstance(x, dict) and x.get("rho") is not None for x in rounds):
                have += 1
            break
    if have:
        return False, (f"{have} of {tot} archived reports DO carry a per-round rho "
                       f"series. The claim that none does is false.")
    return True, f"0 of {tot} reports carry rho"


def pairs_pending_founder():
    """CLAIM: the similarity pairs await a founder ruling."""
    f = REPO / "experimental_notes" / "data" / "adjudication_by_repair.json"
    if not f.is_file():
        return True, "no adjudication output exists; the pairs are genuinely undecided"
    try:
        c = json.loads(f.read_text())["counts"]
    except (OSError, ValueError, KeyError):
        return True, "adjudication output unreadable"
    decided = sum(v for k, v in c.items() if k not in
                  ("UNDECIDABLE", "DISAGREE", "NO_BASELINE"))
    return False, (f"{decided} of {sum(c.values())} pairs were decided BY TOOL "
                   f"({f.relative_to(REPO)}). They are not pending a human.")


# ── the registry ─────────────────────────────────────────────────────────────
# Each entry: the document, a pattern whose PRESENCE asserts the claim, and the
# checker that says whether the claim still holds.
CLAIMS = [
    ("merge arbitration defaults OFF",
     [("bench/reference_runner_v2.py", r"defaults False and is unset in every")],
     merge_arbitration_default),
    ("no archived report carries a rho series",
     [("scripts/replay_accounting.py", r"count of rho-shaped keys is zero"),
      ("resources/RECOVERY.md", r"no archived report carries a rho series in any form\. Decide")],
     rho_series_absent),
    ("the similarity pairs await a founder ruling",
     [("resources/RECOVERY.md", r"133 unadjudicated pairs \(was 120\) — \*\*PENDING FOUNDER RULING")],
     pairs_pending_founder),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--list", action="store_true", help="show the registry and exit")
    args = ap.parse_args()

    if args.list:
        for name, sites, _ in CLAIMS:
            print(f"  {name}")
            for rel, pat in sites:
                print(f"      {rel}   /{pat[:56]}/")
        return 0

    stale = []
    print(f"  auditing {len(CLAIMS)} registered claims against their data\n")
    for name, sites, check in CLAIMS:
        asserted = [rel for rel, pat in sites if re.search(pat, _read(rel))]
        holds, detail = check()
        if asserted and not holds:
            stale.append((name, asserted, detail))
            print(f"  ** STALE ** {name}")
            print(f"      asserted in : {', '.join(asserted)}")
            print(f"      but the data: {detail}\n")
        elif asserted:
            print(f"  ok         {name}  ({detail})")
        else:
            print(f"  withdrawn  {name}  — no document still asserts it")
    if stale:
        print(f"  {len(stale)} claim(s) are asserted in a document and refuted by the data.")
        return 1
    print(f"\n  no registered claim is contradicted by its own data.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
