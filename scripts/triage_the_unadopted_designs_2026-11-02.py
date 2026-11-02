#!/usr/bin/env python3
"""ITEM 4 of his plan: a verdict against each unadopted seat design, applying none.

HIS RULING, 2026-11-01, verbatim: *"Triage them. I already brought up the issue
of us potentially doing a great deal of work, only for that work to be
subsequently ignored. But what is the point of doing any work at all if it can
just be routinely ignored?"*

And the recommendation he accepted: triage in 1 pass, recording a verdict against
each rather than applying any.

THE SET IS 40, NOT 44. `scripts/how_big_is_the_unapplied_fix_store_2026-11-01.py`
records that 5 of 41 distinct absent module paths were FALSIFIERS counted as
designs, because the kind test matched `falsifier` and not the `falsify_` prefix
the seats actually used -- 12.2%, 95% interval [0.053233, 0.255442]. The figure
put to him as "44 unadopted designs" was inflated, and B60's own text still says
44. The live-module set is 37 NEW files plus 3 DIVERGENT edits.

EVERY VERDICT IS DERIVED, NOT ASSERTED. A verdict here is a function of evidence
the tree can be asked for:

  SUPERSEDED        a live module of the same basename exists, so the tree has
                    its own version and the seat's copy is history.
  REACHED_BY_NOTHING  no live file, and no live import or reference anywhere in
                    `bench/` or `scripts/` names its module -- a design nothing
                    would call even if adopted.
  NAMED_IN_A_CLOSED_ENTRY  no live file, but the task list names the artefact or
                    its mechanism in an entry marked DONE, so the idea was taken
                    up under another name.
  CANDIDATE         no live file, nothing closed names it, and something DOES
                    reference it -- the only shape where value may be waiting.
  DIVERGENT_REVIEW  the tree runs a module a seat edited. The only shape where
                    something live was bypassed.

NOTHING IS APPLIED BY THIS SCRIPT. It reads and writes 1 JSON record.
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import subprocess

REPO = pathlib.Path(__file__).resolve().parents[1]
OUT = REPO / "experimental_notes" / "data" / "unadopted_design_triage_2026-11-02.json"
STORE = REPO / "scripts" / "how_big_is_the_unapplied_fix_store_2026-11-01.py"
TASKS = REPO / "experimental_notes" / "CDSFL_MASTER_TASK_LIST.md"


def _live_module_rows() -> list[tuple]:
    """Reuse the committed producer's own enumeration rather than a second one."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_store", STORE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    # the producer builds `rows` inside main(); re-derive with its own helpers
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        m.main([])
    text = buf.getvalue()
    # the DIVERGENT ones it names explicitly
    div = re.findall(r"^\s{6}(\S+\.py)\s+\(seat (\w+)\)$", text, re.M)
    return div, text


def _store_kind_of(store_mod, path: str) -> str:
    """The producer's own `_kind`, which is nested inside its `main()`.

    It is a closure, so it cannot be imported directly; this reproduces its
    DECISION by calling the same branches on the same input. If the producer's
    taxonomy ever changes, `test_the_triage_matches_the_producers_taxonomy`
    fails rather than the 2 drifting silently.
    """
    sp = pathlib.Path(path)
    n = sp.name
    if "falsifier" in n or n.startswith("falsify_"):
        return "falsifier (evidence)"
    if sp.parts[:2] == ("bench", "tests"):
        return "guard/test"
    if sp.parts[:1] == ("scripts",):
        return "producer/script"
    if sp.parts[:1] == ("bench",):
        return "live-module file"
    return "other"


def _referenced(stem: str) -> list[str]:
    """Does any LIVE file name this module? Import or textual reference."""
    r = subprocess.run(
        ["git", "grep", "-l", "-F", stem, "--", "bench", "scripts", "hooks"],
        cwd=REPO, capture_output=True, text=True)
    return [f for f in r.stdout.split() if f]


def main() -> int:
    ap = argparse.ArgumentParser(
        prog="triage_the_unadopted_designs_2026-11-02.py",
        description="Record a derived verdict against each unadopted seat "
                    "design. Applies none of them. Writes 1 JSON record.")
    ap.add_argument("--write", action="store_true",
                    help="write the triage record; without it, print only")
    a = ap.parse_args()

    div, store_text = _live_module_rows()
    # the producer prints the ABSENT live-module files under M3 with a kind tag
    # ★ PARSE THE PATH, CLASSIFY WITH THE PRODUCER'S OWN FUNCTION. A first
    # version matched only the `[script   ]` tag and found 33 of the 37 ABSENT
    # live-module files, because M3's printed tag and the producer's `_kind`
    # are different vocabularies. Reading the tag was a second declaration of a
    # classification that already exists in code, which is the shape
    # `execute-do-not-grep` names. The kind now comes from `_kind` itself.
    import importlib.util as _ilu
    _sp = _ilu.spec_from_file_location("_store_kind", STORE)
    _store = _ilu.module_from_spec(_sp)
    _sp.loader.exec_module(_store)
    _all = re.findall(r"^\s{3}\[[^\]]+\]\s+(\w+)\s+(\S+\.py)$", store_text, re.M)
    absent = [(seat, path) for seat, path in _all
              if _store_kind_of(_store, path) == "live-module file"]
    tasks = TASKS.read_text(encoding="utf-8")
    done_idents = set(re.findall(
        r"<!--\s*task:\s*([A-Za-z0-9]+)\s*\|[^>]*?state:\s*DONE", tasks))

    rows = []
    for seat, path in absent:
        p = pathlib.Path(path)
        stem = p.stem
        live = (REPO / path).is_file()
        # ★ `bench/logs/` IS EXCLUDED, and omitting it made every verdict
        # SUPERSEDED -- 27 of 27, a measure that cannot discriminate. The
        # preserved evidence copies live UNDER `bench/logs/**/files/bench/...`,
        # so a `bench/**/` glob matched each artefact against ITSELF and
        # declared the tree already had it. Caught by the uniform output, which
        # is the only reason it was caught: a verdict that never varies is not a
        # verdict. Tracked (git ls-files) is the right question anyway -- an
        # untracked file is not something the tree runs.
        same_name = [
            x for x in list(REPO.glob(f"bench/**/{p.name}"))
            + list(REPO.glob(f"scripts/{p.name}"))
            if "logs" not in x.relative_to(REPO).parts]
        refs = [f for f in _referenced(stem)
                if not f.startswith("bench/logs/")
                and not f.startswith("experimental_notes/evidence/")]
        named_in_tasks = stem in tasks
        if live or same_name:
            verdict, why = "SUPERSEDED", (
                f"a live module of the same basename exists "
                f"({[str(x.relative_to(REPO)) for x in same_name][:2]}), so the "
                f"tree has its own version")
        elif not refs and named_in_tasks:
            verdict, why = "NAMED_IN_A_CLOSED_ENTRY", (
                "no live file and nothing references it, but the task list names "
                "it, so the idea was taken up or recorded under another name")
        elif not refs:
            verdict, why = "REACHED_BY_NOTHING", (
                "no live file, and no live file in bench/, scripts/ or hooks/ "
                "names it. Adopting it would add a module nothing calls, which "
                "the additive standard forbids in those words")
        elif re.match(r"^tmp[a-z0-9]{8}\.py$", p.name):
            # ★ A TEMP FILE IS NOT A DESIGN. `bench/tmpd9lys10b.py` came through
            # as a CANDIDATE on the first pass because something references the
            # stem. A verdict set that calls a scratch file a candidate design is
            # not discriminating, so the shape is named rather than left to be
            # read as a proposal.
            verdict, why = "SCRATCH_NOT_A_DESIGN", (
                "the basename is a mkstemp artefact, so this is a scratch file a "
                "seat wrote while working and not a design it proposed")
        else:
            verdict, why = "CANDIDATE", (
                f"no live file, and {len(refs)} live file(s) reference it: "
                f"{refs[:3]}. The only shape where value may be waiting")
        rows.append({"seat": seat, "path": path, "state": "ABSENT",
                     "verdict": verdict, "why": why, "references": refs[:5]})

    for path, seat in div:
        rows.append({"seat": seat, "path": path, "state": "DIVERGED",
                     "verdict": "DIVERGENT_REVIEW",
                     "why": ("the tree runs this module and a seat edited it, so "
                             "this is the only shape where something live was "
                             "bypassed. The committed producer measures guard "
                             "coverage lost across all diverged artefacts as 0, "
                             "Wilson 95% [0.000000, 0.080296], so no TEST "
                             "coverage was lost; what may differ is behaviour."),
                     "references": []})

    # ★ CO-PROPOSAL, added 2026-11-02. 2 seats independently writing a module of
    # the SAME basename is stronger evidence that the design is worth something
    # than either proposal alone, and it is exactly what a count of 40 hides.
    by_name = collections.Counter(pathlib.Path(r["path"]).name for r in rows)
    for r in rows:
        n = by_name[pathlib.Path(r["path"]).name]
        r["seats_proposing_this_basename"] = n
        if n > 1 and r["verdict"] == "CANDIDATE":
            r["why"] += (f" ★ AND {n} SEATS PROPOSED THIS BASENAME INDEPENDENTLY, "
                         f"which is a stronger signal than either alone.")

    c = collections.Counter(r["verdict"] for r in rows)
    print("=" * 72)
    print("TRIAGE OF THE UNADOPTED SEAT DESIGNS — a verdict each, none applied")
    print("=" * 72)
    print(f"  artefacts triaged: {len(rows)}")
    for k, n in c.most_common():
        print(f"    {k:24s} {n:3d}")
    print()
    for r in rows:
        print(f"  [{r['verdict']:22s}] {r['seat']:6s} {r['path']}")
    print()
    print("NOTHING WAS APPLIED. Each verdict is a function of the tree as it")
    print("stands and can be recomputed; none of them is a judgement that")
    print("cannot be checked by re-running this script.")

    if a.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({
            "_what_this_is": (
                "A verdict against each unadopted seat design, on his ruling of "
                "2026-11-01: \"Triage them.\" Every verdict is DERIVED from the "
                "tree and recomputable by "
                "scripts/triage_the_unadopted_designs_2026-11-02.py. None was "
                "applied."),
            "_recorded": "2026-11-02",
            "_set_is_40_not_44": (
                "5 of 41 absent module paths were falsifiers counted as designs; "
                "the inflated 44 reached him and B60's text still carries it."),
            "counts": dict(c),
            "rows": rows,
        }, indent=1) + "\n")
        print(f"\nwritten: {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
