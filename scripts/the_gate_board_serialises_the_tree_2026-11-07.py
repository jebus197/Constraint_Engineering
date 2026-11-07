#!/usr/bin/env python3
"""The commit gate's real cost is not its duration: it is an exclusion window.

ENTRIES B81 AND B103 price the commit gate in SECONDS -- B81 records 4 of 4
commits over the 660 s its own header declares, at 800, 769, 738 and 745. That
is the cost to the committer. THIS MEASURES A SECOND COST NOBODY HAS PRICED: for
as long as the board runs, a write anywhere it reads can change a guard's answer
mid-run, so the whole tree is effectively locked.

WHY IT IS NOT HYPOTHETICAL. On 2026-11-07 a triage tool was run 6 minutes into a
2h17m board and wrote `experimental_notes/PARKED_FOR_THE_FOUNDER.md`, which 5
guards read and 3 of those are on the board. The committed bytes were restored
38 seconds later, but the window had already opened. 3 further writes that
session were held back only because the intersection was checked by hand first:
the parked file (3 of 128 on the board), the ticket store (16 of 128) and
`resources/RECOVERY.md` (3 of 128, including the staleness guard the save itself
depends on).

WHAT IS COUNTED. For each of the gate's 128 guard files, the repository
directories it names in its own source. A guard that names a directory can be
perturbed by a write into it. This is a STATIC over-approximation of what each
guard actually opens and it is reported as such: a file may name a path in a
comment and never read it. It is an UPPER bound on exposure and a LOWER bound on
nothing, which is the honest direction for a lock claim.

Exit 0 iff every share was computed and both interval routes agreed.
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

import mpmath as mp
from scipy.stats import beta as _beta
from statsmodels.stats.proportion import proportion_confint

mp.mp.dps = 40
REPO = pathlib.Path(__file__).resolve().parent.parent
WATCHED = ("experimental_notes", "resources", "scripts", "bench/tests",
           "bench/tickets", "bench/logs", "hooks", "docs")

#: ★ THE WINDOW REACHES OUTSIDE THE REPOSITORY, AND THE FIRST VERSION OF THIS
#: SCRIPT MISSED IT -- which is how it bit, 20 minutes after this file was
#: written. 2 memory files were written to the PRIVATE MEMORY DIRECTORY while a
#: commit board was running, on the judgement that a path outside the repository
#: could not perturb a guard inside it. It can:
#: `bench/tests/test_recovery_memory_doc_repairs.py` is ON the gate board and
#: compares that directory's file count against a ledger committed in
#: `resources/`. The board refused with `326 individual memory files on disk,
#: ledger states 324` after 664.29 s, a whole board spent on a write that looked
#: safe because it was out of tree.
#: So an EXTERNAL path is counted too, named by its own token rather than by a
#: repository-relative prefix.
EXTERNAL = (
    "~/.claude/projects/-Users-georgejackson-Developer-Projects/memory",
    ".claude/projects",
    ".claude/hooks",
)


def _iv(k: int, n: int):
    if n == 0:
        return (0.0, 1.0), (0.0, 1.0), 0.0
    lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
    z = mp.mpf("1.959963984540054235524594430520551527955")
    ph = mp.mpf(k) / n
    den = 1 + z**2 / n
    cen = (ph + z**2 / (2 * n)) / den
    half = (z / den) * mp.sqrt(ph * (1 - ph) / n + z**2 / (4 * n * n))
    cl = 0.0 if k == 0 else float(_beta.ppf(0.025, k, n - k + 1))
    ch = 1.0 if k == n else float(_beta.ppf(0.975, k + 1, n - k))
    dis = max(abs(lo - float(cen - half)), abs(hi - float(cen + half)))
    return (max(0.0, lo), hi), (cl, ch), dis


def _show(label: str, k: int, n: int) -> None:
    (wl, wh), (cl, ch), dis = _iv(k, n)
    print(f"  {label}: {k} of {n} = {k / n:.6f}" if n else f"  {label}: 0 of 0")
    print(f"      Wilson 95% [{wl:.6f}, {wh:.6f}]   "
          f"Clopper-Pearson 95% [{cl:.6f}, {ch:.6f}]")
    print(f"      2-route disagreement {dis:.3e}")
    assert dis < 1e-6, f"the 2 interval routes disagree by {dis}"


def main(argv) -> int:
    import importlib.util as iu
    spec = iu.spec_from_file_location(
        "gc", REPO / "scripts" / "precommit_gate_cost_2026-09-10.py")
    gc = iu.module_from_spec(spec)
    spec.loader.exec_module(gc)
    board = [pathlib.Path(str(x)) for x in gc.gate_files()]

    print("=" * 78)
    print("THE GATE BOARD AS AN EXCLUSION WINDOW, NOT A DURATION")
    print("=" * 78)
    print(f"the gate's board: {len(board)} guard files\n")

    hits = collections.Counter()
    per_file = {}
    for p in board:
        f = p if p.is_absolute() else REPO / p
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        named = {d for d in WATCHED if re.search(rf"\b{re.escape(d)}/", src)}
        #: an external path counts as its own directory, so the window's reach
        #: beyond the repository is visible rather than silently excluded
        for e in EXTERNAL:
            tail = e.rstrip("/").split("/")[-1]
            if e in src or re.search(rf"\.claude[/\\]{re.escape(tail)}", src) \
                    or (tail == "memory" and "memory" in src and ".claude" in src):
                named.add("OUTSIDE THE REPO: " + e)
        per_file[p.name] = named
        for d in named:
            hits[d] += 1

    n = len(per_file)
    print("DIRECTORIES THE BOARD'S GUARDS NAME, and how many name each:")
    for d, k in hits.most_common():
        print(f"    {k:>4}  {d}/")
    print()
    exposed = sum(1 for v in per_file.values() if v)
    _show("board guards naming ANY watched directory", exposed, n)
    print()
    for d in ("experimental_notes", "resources", "scripts", "bench/tests"):
        _show(f"naming {d}/", hits.get(d, 0), n)

    print("\n" + "=" * 78)
    print("WHAT THIS DOES AND DOES NOT SUPPORT")
    print("  SUPPORTS: while the board runs, a write into any directory above")
    print("    can change a guard's answer, so the safe action is to wait. The")
    print("    exclusion is wide, not narrow.")
    print("  DOES NOT SUPPORT: a claim that every named directory is actually")
    print("    opened. This is a STATIC over-approximation and an UPPER bound")
    print("    on exposure. A guard naming a path in a comment is counted.")
    print("  THE DECISION IT BEARS ON is B81 and B103, which price the gate in")
    print("    seconds only. Whether a tier split should also be justified by")
    print("    the exclusion window is his call, not this script's.")
    print("=" * 78)
    return 0


if __name__ == "__main__":
    import pathlib as _pl
    sys.path.insert(0, str(_pl.Path(__file__).resolve().parent))
    from _cli_help import answer_help as _answer_help
    _answer_help(__doc__, __file__, takes_no_arguments=True)
    raise SystemExit(main(sys.argv[1:]))
