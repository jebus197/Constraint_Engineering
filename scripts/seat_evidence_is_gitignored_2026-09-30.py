#!/usr/bin/env python3
"""MEASUREMENT: how much seat-written evidence lives ONLY inside the gitignored
sandbox harvest, and is therefore unversioned and unrecoverable after a reboot.

FOUND 2026-09-30 while committing the falsifier-root-cause panel round. `git add
-A` staged 20 files from that round's harvest and left 88 out. The 20 it took are
BYTE-IDENTICAL to files already tracked at their canonical paths (cmp, 20 of 20,
0 differ). The 88 it left included the 3 seat-written falsifiers that produced
every figure the round published -- `0 of 5` vs `5 of 5`, Fisher p = 7.936508e-03,
the constant 52/55 e2 gate. The selection is exactly inverted: the redundant
copies are versioned and the unique evidence is not.

THE CAUSE is one line, `.gitignore:48 bench/logs/**`, which cannot distinguish a
harvest copy of an already-tracked artefact from a script that exists nowhere
else. `git check-ignore` confirms it for every one of the 88.

WHY IT IS ABOVE THRESHOLD. The project's own directive
`measured-rate-travels-with-its-script` requires a quoted rate to be committed
alongside the script that produced it, and records that the project already
learned this once: `scripts/similarity_operating_characteristic.py` was written
on 2026-09-01 because a justifying measurement "lived only as PROSE COMMENTS".
A script sitting in a gitignored directory is the same defect wearing a filename.
`scripts/panel_figure_provenance_2026-09-20.py` makes it concrete -- it names
harvest paths as the "producer" of published figures, so on a fresh clone those
producers are simply absent.

WHAT THIS SCRIPT DECIDES, by execution and not by reading:
  * every .py under any */sandbox_harvest/**/files/ in bench/logs;
  * for each, whether git ignores it (`git check-ignore`, the real decider);
  * whether the same basename exists at its canonical in-tree path, and whether
    git TRACKS that path (`git ls-files --error-unmatch`);
  * whether the harvest copy is byte-identical to the tracked file (hashlib), so
    a duplicate is not counted as preserved evidence when it is merely a copy,
    and a DIVERGED copy is reported separately because that is seat work too;
  * PRESERVED means: a tracked in-tree file exists for it. UNPRESERVED means the
    script exists only inside ignored space.
Wilson score interval on the unpreserved proportion, plus a per-round table.

Exit 0 always: this is a measurement, not a gate. The gate is the companion test.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# A REAL PARSER, AND THE CHOICE IS THE PROJECT'S RATHER THAN MINE.
# `test_operational_scripts::test_an_unknown_flag_is_rejected_loudly` asserts
# argparse's OWN wording, "unrecognized arguments". The shared helper in
# `scripts/_cli_help.py` emits British "unrecognised argument(s)" instead, so a
# script taking that route cannot satisfy the guard however correctly it
# behaves. Widening the assertion was the wrong fix: the guard is DELIBERATE,
# and two scripts (`panel_brief_validate.py`, `quarantine_to_candidate.py`)
# carry `nargs="?"` added expressly so argparse REACHES its unknown-flag check.
# So the script changes, not the test.
#
# Parsing nothing is correct here -- this file takes no arguments. argparse
# supplies the usage line for `--help` (exit 0) and exits 2 with its own
# message on anything else, before any work is done. Added 2026-10-01 after
# the first clean full-suite run went red and 9 of its 20 failures were this
# family; the founder's rule is `feedback_help_must_never_cost_money`, where
# 15 of 17 runners once billed a live dispatch on an unrecognised argument.
#
# The `__main__` guard is load-bearing too: `test_operational_scripts` imports
# every parser-less script in a subprocess with `sys.argv == ['-c', <path>]`,
# so an UNGUARDED parse would read that path as an unrecognised argument and
# exit 2 -- the fix for one guard breaking another.
if __name__ == "__main__":
    import argparse as _argparse

    _argparse.ArgumentParser(
        description=(__doc__ or "").strip().split("\n")[0] or None,
    ).parse_args()


ROOT = Path(__file__).resolve().parent.parent
LOGS = ROOT / "bench" / "logs"
HARVEST_DIRS = ("sandbox_harvest", "worktree_harvest", "panel_worktree_harvest")


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


class GitUnavailable(RuntimeError):
    """git cannot decide ignore/tracked state here, so this survey has no answer.

    BOTH FREE SEATS FOUND THE SAME DEFECT INDEPENDENTLY on 2026-10-01 and fixed
    it differently; this is the composition rather than a choice between them.
    cc2 supplied the per-call check and the detail that decides it -- `git
    check-ignore` exits 1 for "nothing matched", a SUCCESS, so a naive
    `returncode != 0` would raise on every ordinary clean batch. fable supplied
    the consumer half: the ratchet test and the brief figure must SKIP where the
    measurement is undefined, not fail.

    NAMING THE EXCEPTION IS WHAT LETS BOTH HALVES COEXIST. cc2 raised a bare
    `RuntimeError`, which fable's consumer guards -- keyed on a named class --
    would have re-raised, turning an honest skip into an error in exactly the
    git-less environments the fix is for. `GitUnavailable` IS-A `RuntimeError`,
    so cc2's own tests still pass unchanged.
    """


def _require_git(r: "subprocess.CompletedProcess", what: str,
                 ok: tuple = (0,)) -> None:
    """Refuse to answer from an empty result after git failed.

    FREE PANEL, 2026-10-01. `_tracked` and `_ignored` both read `r.stdout` and
    never `r.returncode`. Where git cannot answer -- a panel sandbox copy, a
    `git archive` export, a Docker `COPY` without `.git`, no git binary --
    stdout is empty and the survey reported `251 of 251 unpreserved` against a
    declared `46 of 251`, with `ignored by git` simultaneously reading a
    reassuring `0 of 251`. One unchecked return code, a false alarm in one
    figure and a false clearance in the other, from the same run.

    A MEASUREMENT THAT CANNOT BE TAKEN MUST SAY SO. Raising here makes a
    git-less environment loud, which is the only honest reading: this survey's
    whole question is what git tracks, and without git it has no answer. The
    `ok` tuple exists because `git check-ignore` uses exit 1 for
    "nothing matched" -- a success.
    """
    if r.returncode in ok:
        return
    raise GitUnavailable(
        f"`git {what}` exited {r.returncode} in {ROOT}: "
        f"{(r.stderr or '').strip()[:200] or 'no stderr'}. This survey reports "
        f"what git tracks, so it has NO ANSWER here rather than an answer of "
        f"0 tracked -- which would read as 100% of seat evidence stranded. Run "
        f"it in a git checkout.")


def _ignored(paths: list[Path]) -> set[Path]:
    """The real decider. `git check-ignore` prints only the ignored inputs."""
    if not paths:
        return set()
    out: set[Path] = set()
    CHUNK = 400
    for i in range(0, len(paths), CHUNK):
        batch = [str(p.relative_to(ROOT)) for p in paths[i:i + CHUNK]]
        r = subprocess.run(["git", "check-ignore", "--stdin"], cwd=ROOT,
                           input="\n".join(batch), capture_output=True, text=True)
        # `check-ignore` EXITS 1 WHEN NOTHING IS IGNORED, which is success with
        # an empty answer; 128 is the fatal error. Reading the code without
        # that distinction would make every ordinary clean batch raise.
        _require_git(r, "check-ignore", ok=(0, 1))
        for line in r.stdout.splitlines():
            if line.strip():
                out.add(ROOT / line.strip())
    return out


def _tracked(paths: list[Path]) -> set[Path]:
    if not paths:
        return set()
    r = subprocess.run(["git", "ls-files", "-z", "--"] + [str(p.relative_to(ROOT)) for p in paths],
                       cwd=ROOT, capture_output=True, text=True)
    _require_git(r, "ls-files")
    return {ROOT / s for s in r.stdout.split("\0") if s}


def wilson(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


#: Where `panel_sandbox.preserve_seat_evidence` puts rescued seat files.
SEAT_EVIDENCE = "experimental_notes/seat_evidence"


def _preserved_copies() -> set:
    """{(round, canonical rel)} already rescued into the tracked tree.

    THE REPAIR'S OWN GUARD COULD NOT SEE THE REPAIR, found 2026-10-01 by running
    the first panel round after the repair landed. `preserve_seat_evidence`
    rescues a seat file to `experimental_notes/seat_evidence/<round>/<seat>/<rel>`
    -- a TRACKED path, reachable from any clone, which is the whole point. But
    this survey asked only whether `ROOT/<rel>` is tracked, so a file the repair
    had just rescued still counted as stranded. The round that proved the repair
    works therefore pushed the measured stranding UP, from 46 of 251 to 60 of
    268, and the shrink-only ratchet would have reported a breach caused by the
    fix succeeding.

    A preserved copy is NOT byte-identical to the harvest original -- provenance
    is prepended at rescue time, with the original's sha256 recorded inside it --
    so identity is not the test. Reachability is.
    """
    base = ROOT / SEAT_EVIDENCE
    out = set()
    if not base.is_dir():
        return out
    for rnd_dir in base.iterdir():
        if not rnd_dir.is_dir():
            continue
        for seat_dir in rnd_dir.iterdir():
            if not seat_dir.is_dir():
                continue
            for f in seat_dir.rglob("*"):
                if f.is_file() and f.name != "PROVENANCE.json":
                    out.add((rnd_dir.name, f.relative_to(seat_dir).as_posix()))
    return out


def survey() -> list:
    """Every seat `.py` in harvest space, with its preservation state.

    EXTRACTED 2026-10-01 so a GUARD CAN CALL IT. The logic lived inside
    `main()` and printed, so the only way to ask what it found was to read its
    output -- and the ratchet in
    `bench/tests/test_seat_evidence_stranding_does_not_grow_2026-10-01.py`
    needs the rows, not the text. `execute-do-not-grep`: where 2 forms exist,
    the test calls one rather than parsing the other.
    """
    finds: list[tuple[str, Path, Path]] = []   # (round, harvest path, canonical rel path)
    for hd in HARVEST_DIRS:
        for f in sorted(LOGS.glob(f"*/{hd}/*/attempt-*/files/**/*.py")):
            parts = f.parts
            i = parts.index("files")
            canon = Path(*parts[i + 1:])
            rnd = parts[parts.index("logs") + 1]
            finds.append((rnd, f, canon))

    preserved = _preserved_copies()
    ignored = _ignored([f for _, f, _ in finds])
    canon_abs = [ROOT / c for _, _, c in finds]
    tracked = _tracked([p for p in canon_abs if p.exists()])

    rows = []
    for rnd, f, canon in finds:
        c = ROOT / canon
        in_tree = c.exists()
        is_tracked = c in tracked
        identical = in_tree and _sha(f) == _sha(c)
        rows.append({"round": rnd, "harvest": f, "canon": canon, "ignored": f in ignored,
                     "in_tree": in_tree, "tracked": is_tracked, "identical": identical,
                     # RESCUED COUNTS AS REACHABLE. See `_preserved_copies`.
                     "preserved": (rnd, canon.as_posix()) in preserved})
    return rows


def unpreserved_by_round(rows: list | None = None) -> dict:
    """{round: count of seat files existing nowhere a clone can reach}."""
    out: dict = defaultdict(int)
    # STRANDED MEANS REACHABLE FROM NOWHERE, refined 2026-10-01 and the
    # refinement moves 0 historical counts.
    #
    # `not tracked` alone counts a file WRITTEN TODAY AND NOT YET COMMITTED as
    # stranded, because `git ls-files` cannot list it. The first round run after
    # the repair landed therefore pushed the figure from 46 to 49 purely because
    # 3 of the day's own new files were uncommitted, and the shrink-only ratchet
    # would have reported a breach caused by ordinary work in progress.
    #
    # Measured over all 12 rounds before changing anything: under this
    # definition every one of the 11 baseline rounds returns its EXACT baseline
    # count and the total returns to exactly 46, while the new round's 3 resolve
    # to pending rather than stranded. So the refinement is additive to accuracy
    # and not a loosening: a file present in the working tree becomes reachable
    # on commit, and one present NOWHERE never does. Pending files are reported
    # separately by `main()` rather than hidden.
    for r in (survey() if rows is None else rows):
        if not r["tracked"] and not r.get("preserved") and not r["in_tree"]:
            out[r["round"]] += 1
    return dict(out)


def main() -> None:
    # REPORT THE REFUSAL, DO NOT TRACEBACK. Added 2026-10-01 by FFAFP on the
    # seats' fixes: both made `survey()` refuse and neither taught `main()` to
    # say so, so running this script in a tarball or an export would have
    # printed a stack trace instead of the one sentence a reader needs. The
    # project's own idiom is to name the absent precondition and exit non-zero.
    try:
        rows = survey()
    except GitUnavailable as exc:
        print(f"CANNOT MEASURE HERE: {exc}", file=sys.stderr)
        raise SystemExit(2)
    n = len(rows)
    ign = sum(r["ignored"] for r in rows)
    unpres = [r for r in rows if not r["tracked"] and not r.get("preserved")
              and not r["in_tree"]]
    rescued = [r for r in rows if not r["tracked"] and r.get("preserved")]
    pending = [r for r in rows if not r["tracked"] and not r.get("preserved")
               and r["in_tree"]]
    diverged = [r for r in rows if r["tracked"] and not r["identical"]]

    print(f"seat .py files found in harvest space: {n}")
    print(f"  ignored by git          : {ign} of {n}" + (f" = {100*ign/n:.4f}%" if n else ""))
    lo, hi = wilson(len(unpres), n)
    print(f"  UNPRESERVED (no tracked in-tree file): {len(unpres)} of {n}"
          + (f" = {100*len(unpres)/n:.4f}%, Wilson [{100*lo:.4f}%, {100*hi:.4f}%]" if n else ""))
    print(f"  PENDING COMMIT (present in the tree, not yet committed): "
          f"{len(pending)} of {n}   (reachable from a clone once committed)")
    print(f"  RESCUED into experimental_notes/seat_evidence: {len(rescued)} of {n}"
          "   (untracked at their canonical path, but reachable from a clone)")
    print(f"  tracked but DIVERGED from harvest copy: {len(diverged)} of {n}"
          "   (seat edits to tracked files; provenance of the edit is in the harvest only)")

    per = defaultdict(lambda: [0, 0])
    for r in rows:
        per[r["round"]][0] += 1
        if not r["tracked"]:
            per[r["round"]][1] += 1
    print("\nper round   total  unpreserved")
    for rnd in sorted(per):
        t, u = per[rnd]
        mark = "  <== evidence stranded" if u else ""
        print(f"  {rnd:58s} {t:4d} {u:5d}{mark}")

    if unpres:
        print("\nUNPRESERVED, by canonical path (the scripts that exist nowhere a clone can reach):")
        seen = set()
        for r in sorted(unpres, key=lambda r: (str(r["canon"]), r["round"])):
            key = (str(r["canon"]), r["round"])
            if key in seen:
                continue
            seen.add(key)
            print(f"  {r['canon']}\n      round {r['round']}  ignored={r['ignored']}")


if __name__ == "__main__":
    main()
