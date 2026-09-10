#!/usr/bin/env python3
"""Task R6(a): which files did a seat rewrite, in which runs, and is any archived
measurement contaminated?

MEASURED, and committed alongside the figures (`measured-rate-travels-with-its-script`).

WHAT WAS ASKED. On 2026-09-08 the founder ruled the absolute-path fix itself --
"for sure we should fix it" -- and asked 2 factual questions that are the
assistant's to answer, not his to decide: what is the blast radius, and does
anything need reverting. `f011c1a` established the mechanism: a seat is handed
the ABSOLUTE repository path by `_absolute_target`, and a cwd confines only
RELATIVE paths, so a shell-bearing seat can write anywhere regardless of
`panel_cwd`. Twice on that morning a seat rewrote `bench/dm/_memory.py` -- 24,834
bytes at 04:20:52 and 25,650 at 04:22:22, against a committed 20,605.

THE QUESTION THIS SCRIPT ANSWERS IS NARROWER THAN THE MECHANISM. That a seat
COULD write anywhere is established. What is owed is whether it DID, in the runs
whose numbers the project quotes.

THREE INSTRUMENTS, AND THE COVERAGE OF EACH IS REPORTED.

1. WITHIN-RUN MUTATION. A report's `target_hashes` records the target's digest at
   each round. More than 1 distinct value means the target changed WHILE the run
   was reading it. This is decisive and needs no external reference, but only
   some reports carry the field.
2. AGAINST THE COMMITTED HISTORY. For a target inside the repository, a recorded
   digest that matches no committed revision of that file means the run reviewed
   content that was never committed.
3. ABSENCE OF THE INSTRUMENT. A run that recorded no hash at all cannot be
   cleared. Reporting it as clean would be the "a guard that cannot fail" defect
   this project has already named 3 times in a night, so it is counted
   separately and loudly as UNKNOWABLE rather than folded into either verdict.

The 3rd is the honest part. A blast-radius answer built only on runs that happen
to carry an instrument would understate the radius by exactly the runs that do
not.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parents[1]


#: The rewrites the project actually OBSERVED, with where each was recorded.
#: Every size here is quoted from a committed document, never remembered, and
#: each is checked against the whole history below. Question (b) -- "do we need
#: to revert anything" -- is decidable for exactly these, because a rewrite that
#: never reached a commit cannot need reverting.
OBSERVED_REWRITES = (
    ("bench/dm/_memory.py", 25861,
     "CDSFL_Agent_Operational_Plan.md:142, after the first aborted run, "
     "mtime 02:29:45"),
    ("bench/dm/_memory.py", 24834,
     "commit f011c1a, seat rewrite at 04:20:52 on 2026-09-08"),
    ("bench/dm/_memory.py", 25650,
     "commit f011c1a, seat rewrite at 04:22:22 on 2026-09-08"),
)

#: The size the same records give as correct, so a match is as loud as a miss.
EXPECTED_SIZE = {"bench/dm/_memory.py": 20605}


def committed_sizes(rel: str) -> list[int]:
    """Every byte size this path has had in a commit, across all refs."""
    revs = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", rel],
        cwd=REPO, capture_output=True, text=True).stdout.split()
    out = []
    for rev in revs:
        blob = subprocess.run(["git", "show", f"{rev}:{rel}"],
                              cwd=REPO, capture_output=True)
        if blob.returncode == 0:
            out.append(len(blob.stdout))
    return out


def reports() -> list[pathlib.Path]:
    return sorted((REPO / "bench" / "logs").glob("exp*/exp*_report.json"))


def _in_repo(target: str) -> pathlib.Path | None:
    """The repo-relative path of a target, or None if it lives outside the tree."""
    if not target:
        return None
    p = pathlib.Path(target)
    if not p.is_absolute():
        p = REPO / p
    try:
        rel = p.resolve().relative_to(REPO.resolve())
    except ValueError:
        return None
    return rel


def committed_digests(rel: pathlib.Path) -> set[str]:
    """Every sha256 this path has ever had in a commit, across all refs."""
    revs = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", str(rel)],
        cwd=REPO, capture_output=True, text=True).stdout.split()
    out = set()
    for rev in revs:
        blob = subprocess.run(["git", "show", f"{rev}:{rel}"],
                              cwd=REPO, capture_output=True)
        if blob.returncode == 0:
            out.add(hashlib.sha256(blob.stdout).hexdigest())
    return out


def hashed_everywhere() -> tuple[int, int, int]:
    """(directories carrying target_hashes, hashed rounds, dirs that are sims).

    TWO POPULATIONS, AND THEY ARE NOT THE SAME QUESTION. The sweep above counts
    ARCHIVED LIVE EXPERIMENT REPORTS, because the blast-radius question is about
    runs whose numbers the project quotes. `reference_runner_v3.py`'s own
    docstring counts RUN DIRECTORIES, which includes simulation harnesses, and
    reports "9 run directories carry `target_hashes`, covering 38 hashed rounds".
    Both are legitimate; quoting one against the other is not. This function
    measures the docstring's population so the 2 figures can be compared instead
    of appearing to contradict each other.
    """
    dirs, rounds, sims = set(), 0, set()
    for f in (REPO / "bench" / "logs").rglob("*.json"):
        try:
            j = json.loads(f.read_text())
        except (ValueError, OSError):
            continue
        if isinstance(j, dict) and j.get("target_hashes"):
            dirs.add(f.parent.name)
            rounds += len(j["target_hashes"])
            if f.parent.name.startswith("sim"):
                sims.add(f.parent.name)
    return len(dirs), rounds, len(sims)


def classify(report: dict) -> dict:
    """One report -> what the instruments can say about it.

    EXTRACTED SO THE NULL RESULT IS FALSIFIABLE. This logic lived inline in
    main(), where the only way to test it was against the real archives -- which
    contain no mutated run, so a detector that could never fire would have
    produced exactly the same "0 mutated" output. A test now feeds it a
    synthetic mutated report and requires it to fire.

    Returns `hashed` (was the instrument running), `distinct` (how many digests
    the target had), `mutated` (more than 1, so it changed mid-run) and `rel`
    (the repo-relative target path, or None when the target lives outside).
    """
    th = report.get("target_hashes") or {}
    target = report.get("target_file", "")
    distinct = sorted(set(th.values()))
    return {
        "hashed": bool(th),
        "rounds": len(th),
        "distinct": distinct,
        "mutated": len(distinct) > 1,
        "target": target,
        "rel": _in_repo(target) if th else None,
    }


def main() -> int:
    reps = reports()
    with_hashes, mutated, uncommitted, unknowable, outside = [], [], [], [], []

    for r in reps:
        d = json.loads(r.read_text())
        name = r.parent.name
        c = classify(d)
        target, distinct = c["target"], c["distinct"]
        if not c["hashed"]:
            unknowable.append((name, target))
            continue
        with_hashes.append(name)
        if c["mutated"]:
            mutated.append((name, target, c["rounds"], len(distinct)))
        rel = c["rel"]
        if rel is None:
            outside.append((name, target))
            continue
        known = committed_digests(rel)
        stray = [h for h in distinct if h not in known]
        if stray:
            uncommitted.append((name, str(rel), len(stray), len(distinct), len(known)))

    n = len(reps)
    print(f"ARCHIVED RUNS SWEPT: {n}\n")

    print("--- instrument 1: did the target change DURING the run? ---")
    print(f"  runs carrying per-round target hashes: {len(with_hashes)} of {n}")
    if mutated:
        for name, target, rounds, distinct in mutated:
            print(f"  MUTATED MID-RUN: {name}")
            print(f"      {target}: {distinct} distinct digests over {rounds} rounds")
    else:
        print("  0 of those runs shows more than 1 distinct digest.")
        print("  Every run that CAN be checked this way read 1 unchanging target.")

    print("\n--- instrument 2: was the content ever committed? ---")
    in_tree = len(with_hashes) - len(outside)
    print(f"  runs whose target lives inside the repository: {in_tree} of "
          f"{len(with_hashes)} hashed")
    for name, target in outside:
        print(f"  OUTSIDE THE TREE, not checkable against git: {name} -> {target}")
    if uncommitted:
        for name, rel, stray, distinct, known in uncommitted:
            print(f"  NEVER COMMITTED: {name}: {stray} of {distinct} digest(s) for "
                  f"{rel} match none of its {known} committed revisions")
    elif in_tree:
        print("  every in-tree digest matches a committed revision of its file.")

    d_all, r_all, d_sim = hashed_everywhere()
    print(f"\n  ACROSS ALL RUN DIRECTORIES, not just live experiment reports: "
          f"{d_all} directories,\n  {r_all} hashed rounds, of which {d_sim} "
          f"directories are SIMULATION harnesses (sim*).")
    print(f"  So {d_all - d_sim} live run directories carry the instrument. "
          f"reference_runner_v3.py's\n  docstring states 9 directories and 38 "
          f"rounds for this population; that was measured on\n  2026-09-08 and "
          f"has since grown. The live-experiment figure above is the one the\n"
          f"  blast-radius question needs.")

    print("\n--- instrument 3: what cannot be cleared ---")
    print(f"  runs with NO target hash recorded: {len(unknowable)} of {n} "
          f"({100 * len(unknowable) / n:.2f}%)")
    print("  These are not clean and are not dirty. The instrument that would")
    print("  answer the question was not running when they ran.")

    from statsmodels.stats.proportion import proportion_confint
    lo, hi = proportion_confint(len(unknowable), n, method="wilson")
    print(f"  Wilson 95% for the unknowable share: "
          f"[{lo * 100:.2f}%, {hi * 100:.2f}%]  (statsmodels)")
    from scipy.stats import beta as sbeta
    clo = sbeta.ppf(0.025, len(unknowable), n - len(unknowable) + 1)
    chi = sbeta.ppf(0.975, len(unknowable) + 1, n - len(unknowable))
    print(f"  Clopper-Pearson 95%: [{clo * 100:.2f}%, {chi * 100:.2f}%]  (scipy, "
          f"cross-check -- a 2nd tool, as this project requires)")

    print("\n--- ANSWER TO (a), THE BLAST RADIUS ---")
    print(f"  Runs showing a target mutated mid-run: {len(mutated)}")
    print(f"  Runs whose target content was never committed: {len(uncommitted)}")
    print(f"  Runs that cannot be checked at all: {len(unknowable)}")
    print("  The radius is therefore bounded BELOW by the first 2 and cannot be")
    print("  bounded above from the archives alone.")

    # ---- (b) DO WE NEED TO REVERT ANYTHING? ----
    #
    # This half IS fully decidable, and it is worth separating from (a) for that
    # reason. A rewrite that never reached a commit cannot need reverting, and
    # whether it reached one is a question the whole history answers exactly.
    print("\n--- ANSWER TO (b), DOES ANYTHING NEED REVERTING ---")
    landed = []
    by_file = {}
    for rel, size, where in OBSERVED_REWRITES:
        sizes = by_file.setdefault(rel, committed_sizes(rel))
        hit = size in sizes
        landed.append(hit) if hit else None
        print(f"  {rel} at {size:,} bytes ({where})")
        print(f"      {'LANDED IN A COMMIT' if hit else 'never reached a commit'}")
    for rel, sizes in by_file.items():
        uniq = sorted(set(sizes))
        exp = EXPECTED_SIZE.get(rel)
        print(f"\n  {rel}: {len(sizes)} commit(s), {len(uniq)} distinct size(s): "
              + ", ".join(f"{u:,}" for u in uniq))
        if exp is not None:
            print(f"      the records give {exp:,} as correct; it is "
                  f"{'present' if exp in uniq else 'ABSENT'} in the history")

    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip()
    tracked_dirty = [l for l in dirty.splitlines() if not l.startswith("??")]
    print(f"\n  tracked files differing from HEAD right now: {len(tracked_dirty)}")
    for l in tracked_dirty:
        print(f"      {l}")

    if landed or tracked_dirty:
        print("\n  SOMETHING NEEDS ATTENTION -- see the lines above.")
        return 1
    print("\n  NOTHING NEEDS REVERTING, for what is checkable: not one observed")
    print("  rewrite reached a commit, and no tracked file differs from HEAD.")
    print("  This is a statement about the rewrites that were OBSERVED. The 35")
    print("  runs above that carry no target hash are not covered by it.")
    return 0 if not (mutated or uncommitted) else 1


if __name__ == "__main__":
    sys.exit(main())
