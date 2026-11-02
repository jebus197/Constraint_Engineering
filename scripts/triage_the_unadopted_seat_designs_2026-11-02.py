#!/usr/bin/env python3
"""Triage the unadopted seat-written designs. ONE VERDICT EACH, NONE APPLIED.

HIS RULING, 2026-11-01, annotation 7 of `Closing_Report_2026-11-01.txt`,
verbatim: *"Triage them. I already brought up the issue of us potentially doing a
great deal of work, only for that work to be subsequently ignored. But what is
the point of doing any work at all if it can just be routinely ignored?"*

And his question 26 of the same reply: *"Again what seat designs? I have no idea
what you are asking me here? What does '44' relate to?"* -- answered by B60's own
inventory: of 313 preserved seat-written Python artefacts, 45 are live-module
files that were never applied, and 44 of those are NEW modules a seat created
that the tree never adopted. Those 44 are the subject.

WHAT THIS DECIDES AND WHAT IT REFUSES TO DECIDE. Whether a design is worth
adopting is a JUDGEMENT. A rubric scoring 44 designs and sorting them would
launder that judgement as a measurement, which is the move the founder caught on
severity and the thing `bench/fix_comparator.py` was written this same day to
refuse. So this classifies only what is mechanically decidable:

  SUPERSEDED   EVERY top-level name the seat module defines is already defined
               somewhere in the live tree. The job is done, under whatever
               filename. Reported at full overlap only, so no threshold is
               chosen -- a cut picked without measuring its alternatives is this
               project's most recorded error class.
  UNTESTED     the seat shipped NO COMPANION TEST FILE for it anywhere in the
               same seat's directory. Adopting it would breach
               `additive-standard` from the addition side.

               ★ A 3RD PREDICATE WAS DISCARDED HERE. The first version asked
               whether the MODULE file itself contained a `def test_`, and
               returned 25 of 25, 1.000000 -- which this script's own unanimity
               guard REFUSED. It was right to: modules never contain their own
               tests by convention, so the predicate measured a convention and
               not a property. A seat writes the module and its falsifier as 2
               files, which is exactly what the 4 `bench/test_*.py` entries
               excluded a moment earlier were.
  NEEDS A READ  none of the above decides it. The symbol-overlap fraction and
               the docstring's first line are printed, so 37 one-line claims can
               be read instead of 37 files.

★ 2 PREDICATES WERE DISCARDED FROM THIS SCRIPT AFTER BEING RUN, BOTH MINE.

  UNREACHABLE WAS VACUOUS. It asked whether anything in the live tree imports the
  module's name, and returned 35 of 37, 0.945946, Wilson 95% [0.822953,
  0.985049]. A candidate is SELECTED because its path does not exist in the tree,
  and a module that does not exist cannot be imported by the tree -- so the
  verdict was true for 37 of 37 before anything was measured. It restated the
  selection criterion and carried 0 bits. Verified by execution, not reasoned.

  SUPERSESSION BY BASENAME MISSED THE REAL CASE. It returned 0 of 37, and the
  clearest instance proves it wrong: a seat wrote `bench/capability_identity.py`;
  no live file of that name exists, but `bench/routing.py` does and
  `composer.py` imports it AS `_cap_identity`. The job is done live under a
  different filename, which a basename test cannot see. Supersession is now
  tested by SYMBOL OVERLAP.

★ THE SELF-MATCH TRAP, WHICH ALREADY RUINED ONE ATTEMPT AT THIS. An earlier
triage returned SUPERSEDED for 27 of 27 artefacts and looked complete. The
preserved copies live under `bench/logs/**/files/bench/...` and a `bench/**`
glob matched each artefact against ITSELF -- recorded in
`feedback_a_false_positive_can_be_why_a_rule_is_unenforced_2026-11-02`, where a
uniform verdict is named as the cheapest available signal that a predicate is
wrong. Every path test here excludes the evidence store and the log harvests,
and the script REFUSES to report a verdict that is unanimous across all 44,
because at this sample size unanimity is far likelier to be a bug than a finding.
"""
from __future__ import annotations
import ast, collections, math, pathlib, re, sys

import sys as _sys, pathlib as _pl  # noqa: E402
for _cand in (_pl.Path(__file__).resolve().parent, *_pl.Path(__file__).resolve().parents):
    if (_cand / "_cli_help.py").is_file():
        if str(_cand) not in _sys.path:
            _sys.path.insert(0, str(_cand))
        break
from _cli_help import answer_help  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[1]
STORE = REPO / "experimental_notes" / "seat_evidence"
#: Paths that are NOT the live tree. The evidence store and the log harvests hold
#: preserved copies, so a search that includes them matches an artefact against
#: itself. This is the exclusion the earlier attempt lacked.
NOT_LIVE = ("experimental_notes/seat_evidence/", "bench/logs/", "/sandbox_harvest/",
            "/panel_worktree_harvest/", "/files/bench/")


def wilson(k: int, n: int):
    if n == 0:
        return (float("nan"),) * 3
    p = k / n; z = 1.959963984540054
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return p, max(0.0, c - h), min(1.0, c + h)


def _is_live(p: pathlib.Path) -> bool:
    s = str(p.relative_to(REPO)).replace("\\", "/")
    return not any(x.strip("/") in s for x in NOT_LIVE)


def _live_files() -> dict[str, list[str]]:
    """Live .py files by basename, with the store and harvests excluded."""
    out: dict[str, list[str]] = collections.defaultdict(list)
    for p in REPO.rglob("*.py"):
        if _is_live(p):
            out[p.name].append(str(p.relative_to(REPO)))
    return out


def _top_level_names(src: str) -> set[str]:
    """Public top-level function and class names. The module's offered surface."""
    try:
        tree = ast.parse(src)
    except Exception:                                        # noqa: BLE001
        return set()
    out = set()
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not n.name.startswith("_"):
                out.add(n.name)
    return out


def _live_symbol_index() -> set[str]:
    """Every public top-level name defined anywhere in the LIVE tree.

    Built once. The store and the harvests are excluded by `_is_live`, so a
    seat's own preserved copy cannot make its own symbols look adopted -- which
    is the self-match that returned 27 of 27 on an earlier attempt.
    """
    names: set[str] = set()
    for p in REPO.rglob("*.py"):
        if not _is_live(p):
            continue
        try:
            names |= _top_level_names(p.read_text(errors="replace"))
        except Exception:                                    # noqa: BLE001
            pass
    return names


def _first_doc_line(p: pathlib.Path) -> str:
    try:
        m = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        d = ast.get_docstring(m) or ""
        return (d.strip().splitlines() or [""])[0][:96]
    except Exception:                                        # noqa: BLE001
        return "(unparseable)"


def main() -> int:
    answer_help(__doc__, __file__)
    if not STORE.is_dir():
        print(f"the seat evidence store is absent at {STORE}")
        return 1

    live = _live_files()
    LIVE_NAMES = _live_symbol_index()
    print(f"  live public top-level names indexed: {len(LIVE_NAMES)}")

    # The 44: ABSENT live-module files, i.e. not tests, not falsifiers, not
    # scripts. Classified by the seat's own path inside the store.
    cands = []
    for f in sorted(STORE.rglob("*.py")):
        # ★ THE LAYOUT IS `<round>/<seat>/<the path the seat wrote to>`, taken
        # from the existing producer rather than guessed. A first version here
        # searched for a `files/` segment -- the layout used by the LOG
        # harvests, not by this store -- and matched 0 of 313, which the script
        # correctly refused to report as a clean sheet.
        parts = f.relative_to(STORE).parts
        if len(parts) < 3:
            continue
        sp = "/".join(parts[2:])
        # ★ A TEST IS A TEST WHEREVER IT SITS, corrected 2026-11-02. A first
        # version excluded `bench/tests/` by DIRECTORY and let 4 files named
        # `bench/test_*.py` through, which were then reported as designs needing
        # a judgement. They are falsifiers a seat put beside the module they
        # test. The criterion is the BASENAME, not the folder.
        if (sp.startswith(("bench/tests/", "scripts/"))
                or pathlib.Path(sp).name.startswith("test_")
                or "falsif" in sp):
            continue
        if not sp.startswith("bench/"):
            continue
        if (REPO / sp).is_file():
            continue                     # applied or diverged, not our subject
        cands.append((f, sp))

    print("=" * 78)
    print("TRIAGE OF THE UNADOPTED SEAT DESIGNS")
    print("=" * 78)
    print(f"  candidates found: {len(cands)}")
    if not cands:
        print("  NONE. Either the store moved or the path rule is wrong; a 0 here")
        print("  is a reason to check this script, not to report a clean sheet.")
        return 1

    rows = []
    for f, sp in cands:
        stem = pathlib.Path(sp).stem
        base = pathlib.Path(sp).name
        src = f.read_text(encoding="utf-8", errors="replace")
        # A COMPANION TEST: any test file in the SAME seat directory naming this
        # module's stem. That is how a seat actually ships a tested design.
        seat_dir = f.parents[len(pathlib.Path(sp).parts) - 1]
        stem_l = stem.lower()
        companions = [c for c in seat_dir.rglob("*.py")
                      if c != f and c.name.lower().startswith(("test_", "falsify_"))
                      and stem_l in c.read_text(errors="replace").lower()]
        has_tests = bool(companions)
        offered = _top_level_names(src)
        covered = offered & LIVE_NAMES
        frac = (len(covered) / len(offered)) if offered else 0.0
        if offered and frac >= 1.0:
            v = "SUPERSEDED"
            why = (f"all {len(offered)} public name(s) it defines already exist "
                   f"live: {sorted(covered)[:4]}")
        elif not has_tests:
            v = "UNTESTED"
            why = (f"no companion test file in this seat's directory; "
                   f"{len(covered)} of {len(offered)} name(s) already live "
                   f"({frac:.4f})")
        else:
            v = "NEEDS A READ"
            why = (f"{len(covered)} of {len(offered)} name(s) already live "
                   f"({frac:.4f}). {_first_doc_line(f)}")
        rows.append({"path": sp, "verdict": v, "why": why,
                     "lines": src.count("\n") + 1, "tests": has_tests,
                     "overlap": frac})

    c = collections.Counter(r["verdict"] for r in rows)
    print(f"\n  {'verdict':14s} {'n':>4s}  share")
    for v, n in c.most_common():
        p, lo, hi = wilson(n, len(rows))
        print(f"  {v:14s} {n:4d}  {p:.6f}  Wilson 95% [{lo:.6f}, {hi:.6f}]")

    if len(c) == 1:
        only = next(iter(c))
        print(f"\n  *** REFUSED: all {len(rows)} came back {only}. At this sample")
        print(f"  size a unanimous verdict is far likelier to be a predicate bug")
        print(f"  than a finding -- an earlier attempt at this returned SUPERSEDED")
        print(f"  for 27 of 27 because its glob matched each artefact against")
        print(f"  ITSELF. Nothing is concluded. Check the path rule first.")
        return 2

    print(f"\n  EVERY CANDIDATE, ONE LINE EACH")
    for v in ("NEEDS A READ", "UNTESTED", "SUPERSEDED"):
        sel = [r for r in rows if r["verdict"] == v]
        if not sel:
            continue
        print(f"\n  --- {v} ({len(sel)}) ---")
        for r in sorted(sel, key=lambda x: -x["lines"]):
            print(f"    {r['lines']:5d} lines  {r['path']}")
            print(f"                  {r['why']}")

    print(f"\n  NOTHING WAS APPLIED. This records a verdict against each, which is")
    print(f"  what his ruling asked for. The {c.get('NEEDS A READ', 0)} marked NEEDS A")
    print(f"  READ are the only ones a judgement is owed on, and each is 1 line.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
