# PRESERVED SEAT EVIDENCE. Written by seat 'cc2' during panel round 'check_my_work_2026-09-28', at the path shown above.
# Rescued from that round's sandbox harvest, which `.gitignore` keeps out of version control; the harvest path is NOT cited here because a citation a reader cannot follow is not evidence.
# sha256 of the seat's original, before this header: 805a148107a179adedd0ab969bd953dcf2327ec2e5e05fb2838ae8545a3373fc
# Copied by bench/panel_sandbox.py:preserve_seat_evidence. NOT edited.
#!/usr/bin/env python3
"""Is the harvest's run-log exclusion TOO WIDE? It was, and the brief proves it.

`bench/panel_sandbox.py:646 harvest()` excludes the run's own log directory so the
dispatcher's writes into the sandbox copy stop reading as seat changes. That fix is
right and the derivation of `_run_log_dir` is right: I traced all 4 call sites and
every one resolves to `REPO/bench/logs/<run>`, so the 3 destination shapes CC1
enumerated are complete --

  run_simulated_experiment.py:263 + :640   <run>/panel_worktree_harvest
  build_experiment_run.py:58 + :181        <run>/worktree_harvest/<tag>
  confer_convergence_panel:27 + :78        <run>/worktree_harvest/<tag>
  confer_maths_panel:263 + :98             <run>/sandbox_harvest/<seat>/attempt-N

-- and `parents[2]` really would have collapsed 2 of them onto `bench` and
`bench/logs`. I found no 4th destination shape. I found a 4th CONTENT shape, which
is worse, because it loses work rather than keeping noise:

  THE RUN'S OWN DIRECTORY IS NOT EMPTY. The brief lives in it. On this round:
  bench/logs/check_my_work_2026-09-28/BRIEF.md, beside dispatch.log. So
  "write your measurement next to the brief" -- an ordinary instruction, and the
  brief's own Section 3 tells seats to deliver files at real paths -- lands a
  genuine deliverable on a path the exclusion drops, and drops it under the
  message "this run's OWN log output, WHICH THE DISPATCHER WROTE". Discarded AND
  misattributed. The comment at :606-609 anticipates exactly this risk for
  `bench/logs/` wholesale and then does not apply the same reasoning one level in.

THE FIX USES THE MECHANISM THAT CAUSED THE ORIGINAL BUG. The dispatcher's writes
are DRIFT between two copies of one file (:598 -- `elapsed_s` differing by 0.9), so
they exist in BOTH trees. A seat's new file exists only in the sandbox. So a path
under the run directory is dispatcher output iff the canonical tree also has it.

Run:  python3 scripts/harvest_keeps_seat_work_in_the_run_dir_2026-09-28.py
Exit: 0 if the real harvest() keeps seat work and still drops dispatcher drift.
      1 if either half fails. Imports the REAL module; retypes nothing.
"""
from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "bench"))
import panel_sandbox as ps  # noqa: E402  the REAL target, not a copy

FAILURES: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"  [{'PASS' if ok else 'FAIL'}] {label}")
    if not ok:
        FAILURES.append(label)


def build(root: Path, run: str):
    """A canonical repo and a sandbox copy of it, with the shapes that matter."""
    repo, sandbox = root / "repo", root / "sandbox"
    for tree in (repo, sandbox):
        (tree / "bench" / "logs" / run).mkdir(parents=True)
        (tree / "bench" / "logs" / "some_other_round").mkdir(parents=True)
        (tree / "scripts").mkdir(parents=True)
        # The dispatcher's own log, in BOTH trees, drifting -- the original defect.
        (tree / "bench" / "logs" / run / "dispatch.log").write_text(
            "elapsed_s=12.3\n" if tree is repo else "elapsed_s=13.2\n")
        # The brief, in both trees, unchanged.
        (tree / "bench" / "logs" / run / "BRIEF.md").write_text("the brief\n")
        (tree / "scripts" / "pre_existing.py").write_text("x = 1\n")
    # --- now the SEAT writes, sandbox only ---
    # (a) the ordinary case: a fix at a real path outside bench/logs
    (sandbox / "scripts" / "seat_fix.py").write_text("print('fix')\n")
    # (b) a measurement under bench/logs/ but NOT in this run -- must survive
    (sandbox / "bench" / "logs" / "some_other_round" / "seat_measurement.json").write_text("{}\n")
    # (c) THE REGRESSION: a deliverable written beside the brief, in THIS run's dir
    (sandbox / "bench" / "logs" / run / "seat_findings.json").write_text(
        '{"finding": "written next to the brief, as instructed"}\n')
    # (d) and an edit to a pre-existing tracked file, for good measure
    (sandbox / "scripts" / "pre_existing.py").write_text("x = 2\n")
    # (e) THE REGRESSION MY OWN FIRST FIX CAUSED: an earlier attempt's harvest
    #     artefact, present in the SANDBOX ONLY. exists-in-both read it as seat
    #     work and harvested the harvest. Caught by running the committed suite.
    own = sandbox / "bench" / "logs" / run / "sandbox_harvest" / "fable" / "attempt-1"
    own.mkdir(parents=True)
    (own / "changes.diff").write_text("### noise\n")
    return repo, sandbox


def main() -> int:
    run = "check_my_work_2026-09-28"
    live_brief = REPO / "bench" / "logs" / run / "BRIEF.md"
    print("\n0. THE PREMISE, CHECKED ON DISK RATHER THAN ASSUMED")
    check(live_brief.exists(),
          f"the brief really does live inside the run's own log directory "
          f"({live_brief.relative_to(REPO)})")

    print("\n1. THE REAL harvest(), ON THE 4 CONTENT SHAPES")
    root = Path(tempfile.mkdtemp(prefix="cdsfl_harvest_probe_"))
    try:
        repo, sandbox = build(root, run)
        dest = repo / "bench" / "logs" / run / "sandbox_harvest" / "cc2" / "attempt-1"
        rl = ps._run_log_dir(dest, repo)
        print(f"    _run_log_dir -> {rl!r}")
        check(rl == f"bench/logs/{run}",
              "the run directory is derived correctly for the deepest shape")
        # the 2 shallower shapes, which parents[2] got wrong
        check(ps._run_log_dir(repo / "bench/logs" / run / "worktree_harvest" / "ge",
                             repo) == f"bench/logs/{run}",
              "and for <run>/worktree_harvest/<tag>  (parents[2] gave 'bench/logs')")
        check(ps._run_log_dir(repo / "bench/logs" / run / "panel_worktree_harvest",
                             repo) == f"bench/logs/{run}",
              "and for <run>/panel_worktree_harvest  (parents[2] gave 'bench')")

        m = ps.harvest(sandbox, repo, dest)
        taken = set(p.replace("\\", "/") for p in m["files_taken"])
        print(f"    files_taken ({m['changed']}): {sorted(taken)}")
        print(f"    skipped as this run's own output: {m['skipped_own_log_output']}")

        check("scripts/seat_fix.py" in taken,
              "KEEPS a seat fix at a real path (the ordinary case)")
        check("scripts/pre_existing.py" in taken,
              "KEEPS a seat edit to a pre-existing file")
        check("bench/logs/some_other_round/seat_measurement.json" in taken,
              "KEEPS a seat measurement under bench/logs/ but outside this run "
              "-- the exclusion is NOT too wide in that direction")
        check(f"bench/logs/{run}/seat_findings.json" in taken,
              "KEEPS a seat deliverable written BESIDE THE BRIEF, inside this run's "
              "own directory  <-- THE FIX. Path-only exclusion dropped this.")
        check(f"bench/logs/{run}/dispatch.log" not in taken,
              "and STILL DROPS the dispatcher's own drifting log -- the original "
              "defect stays fixed")
        check(not any("sandbox_harvest" in r for r in taken),
              "and STILL DROPS the harvest's OWN output even though it is in the "
              "sandbox only -- the harvest does not harvest itself")
        check(ps._harvest_container_rel(dest, repo, rl)
              == f"bench/logs/{run}/sandbox_harvest",
              "the harvest container is derived, not hardcoded")
        check(m["skipped_own_log_output"] >= 2,
              "both drops are counted and reported rather than silent")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    print("\n2. THE OLD BEHAVIOUR IS STILL REACHABLE FOR CALLERS WITH NO REPO")
    check(ps._is_dispatcher_own_output("bench/logs/r/x.json", "bench/logs/r") is True,
          "repo=None keeps the path-only verdict, so no existing caller or test "
          "changes meaning (additive, not a replacement)")
    check(ps._is_dispatcher_own_output("bench/logs/r10/x.json", "bench/logs/r") is False,
          "and a sibling run whose name is a prefix is not caught")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    rc = main()
    print()
    if FAILURES:
        print(f"FALSIFIED -- {len(FAILURES)} check(s) failed:")
        for f in FAILURES:
            print(f"  - {f}")
    else:
        print("The exclusion is now neither too wide nor too narrow.")
    sys.exit(rc)
