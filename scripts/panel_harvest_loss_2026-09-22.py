#!/usr/bin/env python3
"""How much of the panel's delivered work never reached the repository.

THE DEFECT. Panel seats work inside isolated copies of this repository and
deliver fixes as FILES into those copies. The dispatcher harvests those files to
`bench/logs/<run>/sandbox_harvest/<seat>/attempt-N/files/<real path>`, which
persists. Nothing then copied them onward into `scripts/`, so the work was
present in the archive and absent from the tree -- invisible to every later
session, which re-asked questions that had already been answered.

WHY THIS SCRIPT EXISTS AT ALL. The rate below was quoted to the founder in
`experimental_notes/Panel_Audit_Closing_Report_2026-09-22.md` with NO producing
script, which is precisely the defect `measured-rate-travels-with-its-script`
names: a number that exists only as prose is a claim about evidence, not
evidence. It was caught by `scripts/panel_brief_validate.py` refusing to let the
same figure into a panel brief undeclared. The rule had to be enforced by a
machine before it was obeyed, which is the same shape as the note lint.

THE REFERENCE POINT IS PINNED, DELIBERATELY. The loss is measured against the
tree as it stood BEFORE recovery (default `ae0c837`). Measuring against a moving
HEAD would silently report 0 the moment the recovered files are committed, and a
measurement that erases itself on being acted upon is not a measurement. Pass
--ref to check any other commit; --ref HEAD answers the different and also
useful question "is anything UNHARVESTED right now".

Run:  python3 scripts/panel_harvest_loss_2026-09-22.py
      python3 scripts/panel_harvest_loss_2026-09-22.py --ref HEAD
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LOGS = REPO / "bench" / "logs"

#: The tree as it stood before the 2026-09-22 recovery. See the docstring.
PRE_RECOVERY_REF = "ae0c837"


def tracked_scripts(ref: str) -> set[str]:
    """Basenames under scripts/ present at `ref`."""
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, "scripts/"],
                         cwd=REPO, capture_output=True, text=True)
    if out.returncode != 0:
        print(f"git ls-tree failed for ref {ref!r}: {out.stderr.strip()}",
              file=sys.stderr)
        raise SystemExit(2)
    return {Path(p).name for p in out.stdout.split() if p.endswith(".py")}


def harvested_scripts() -> dict[str, str]:
    """Distinct seat-written scripts/*.py in the harvest -> first archive path."""
    found: dict[str, str] = {}
    for p in sorted(LOGS.glob("*/sandbox_harvest/*/attempt-*/files/scripts/*.py")):
        found.setdefault(p.name, str(p.relative_to(REPO)))
    return found


def interval(k: int, n: int):
    from statsmodels.stats.proportion import proportion_confint
    return (proportion_confint(k, n, alpha=0.05, method="wilson"),
            proportion_confint(k, n, alpha=0.05, method="beta"))


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--ref", default=PRE_RECOVERY_REF)
    args, _ = ap.parse_known_args()

    harvest = harvested_scripts()
    tracked = tracked_scripts(args.ref)
    if not harvest:
        print("no harvested scripts found -- has any panel run yet?",
              file=sys.stderr)
        return 2

    lost = {n: p for n, p in harvest.items() if n not in tracked}
    n, k = len(harvest), len(lost)

    print("PANEL HARVEST LOSS")
    print(f"  reference commit : {args.ref}"
          f"{'  (pinned: the tree before recovery)' if args.ref == PRE_RECOVERY_REF else ''}")
    print(f"  distinct scripts delivered by seats into sandboxes : {n}")
    print(f"  of those, absent from scripts/ at that commit      : {k}")
    print()
    (wlo, whi), (clo, chi) = interval(k, n)
    print(f"  LOSS RATE {k}/{n} = {100*k/n:.4f}%")
    print(f"      Wilson 95%          [{100*wlo:.4f}%, {100*whi:.4f}%]")
    print(f"      Clopper-Pearson 95% [{100*clo:.4f}%, {100*chi:.4f}%]")

    # second route, per multi_tool_crossverify: Wilson recomputed at 50 digits
    try:
        import mpmath as mp
        mp.mp.dps = 50
        z = mp.mpf("1.959963984540054235524594430520551527955550999086")
        ph, nn = mp.mpf(k) / n, mp.mpf(n)
        d = 1 + z**2 / nn
        c = (ph + z**2 / (2 * nn)) / d
        h = z * mp.sqrt(ph * (1 - ph) / nn + z**2 / (4 * nn**2)) / d
        print(f"      mpmath@50dps Wilson [{float(100*(c-h)):.4f}%, "
              f"{float(100*(c+h)):.4f}%]  |agreement| "
              f"{abs(float(c-h)-wlo):.2e} / {abs(float(c+h)-whi):.2e}")
    except ImportError:
        print("      (mpmath absent; single-route interval only)")

    print()
    print("  LOST FILES")
    for name, path in sorted(lost.items()):
        print(f"    {name}")
        print(f"        archived at {path}")
    if not lost:
        print("    none -- every delivered script is present at this commit")
    return 0


if __name__ == "__main__":
    from _cli_help import answer_help
    answer_help(__doc__, __file__)
    sys.exit(main())
