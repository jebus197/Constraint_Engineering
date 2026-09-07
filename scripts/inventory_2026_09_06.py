#!/usr/bin/env python3
"""Where the 2026-09-06 programme actually stands. One artefact, checkable.

WHY. The founder asked "where are we and what exactly remains" after CC1 answered a
question and then failed to discharge it. An assurance is what he already had. This
enumerates every item from all 3 of his annotated answer files of 2026-09-06 plus
the panel-found work, with its state and its evidence.

STATES
  DONE      executed and committed, evidence named
  REFUTED   investigated and NOT done because the premise did not survive
  HELD      deliberately not started; the founder held that class of work
  BLOCKED   cannot proceed without the founder or without held material
  OPEN      CC1's to do, not started or not finished
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

ITEMS = [
 # (source, item, state, evidence-or-reason)
 ("51-list", "1 Exp 53 restart-vs-resume", "HELD", "launch; held with the simulated run"),
 ("51-list", "2 rubric authority", "DONE", "panel run; result recorded in the appendix"),
 ("51-list", "3 exp52 planted set", "HELD", "answer-key class, held by founder"),
 ("51-list", "4 reviewer write access + disclosure", "DONE", "scripts/measure_reviewer_write_disclosure.py"),
 ("51-list", "5,6,8,9,12,21,33,45 the 8 questions", "DONE", "answered; 21 also BUILT (text_protocol_tools.py)"),
 ("51-list", "7 canary must not block convergence", "DONE", "recorded in canary_seeding.py"),
 ("51-list", "13 temporary worktree", "DONE", "removed"),
 ("51-list", "15 description truncation", "BLOCKED", "code already fixed; archive backfill needs founder word"),
 ("51-list", "16 fixes + equipment + containments", "OPEN", "RE-MEASURED: 28 need a fix, 16 fix-ineffective, 43 blocked on the keys"),
 ("51-list", "18 C0015 / C0017", "DONE", "C0015 already fixed; C0017 repaired (non-finite fail-safe)"),
 ("51-list", "22 6th panel seat", "DONE", "dropped from 3 canonical definitions"),
 ("51-list", "23 severity is a model vote", "DONE", "removed from A4; panel found+fixed a hole in it"),
 ("51-list", "25 archive decryption path", "DONE", "recorded in RECOVERY.md without naming the location"),
 ("51-list", "26 relabel 37 finding IDs", "REFUTED", "does not reproduce; would have corrupted provenance"),
 ("51-list", "27 5 prose targets", "HELD", "exam content with planted defects = answer-key class"),
 ("51-list", "30 routing character class", "DONE", "unified to ONE imported definition + reproducing script"),
 ("51-list", "32 materiality review", "BLOCKED", "population does not reproduce; needs the held keys"),
 ("51-list", "35 confine panel agents from the repo", "DONE", "both halves; proved by execution, commit 132af1b"),
 ("51-list", "39 18-May PoC plan", "DONE", "closed in the tracker"),
 ("51-list", "40,41 the 2 nested batches", "DONE", "opened; 14 decisions, 6 live, 1 duplicate"),
 ("51-list", "44 Open Brain spot-check", "DONE", "casing already harmless (90 rows all casings); 4 ORPHANED rows found and fixed"),
 ("51-list", "49 record the rubric conflict", "DONE", "appendix section added"),
 ("51-list", "50 discharge rule", "DONE", "adopted with the scope-declared refinement"),
 ("51-list", "51 exp52 re-authoring confer", "HELD", "answer-key class"),
 ("51-list", "10,11 key sealing / Zenodo", "BLOCKED", "needs the founder's passphrase and hands"),
 ("51-list", "the 4 genuine falsifiers", "DONE", "all 4 commissioned; 2 refuted, 2 pinned"),
 ("51-list", "14,17,19,20,24,28,29,31,34,36,37,38,42,43,46", "DONE", "15 items scheduled on the runway at named horizons"),

 ("closing", "queue alarm halt-vs-veto", "DONE", "NOT softened; root cause found (round-0 escalation)"),
 ("closing", "Open Brain label split", "DONE", "read-side sentinel fix; ledger not rewritten (hash covers the label)"),
 ("closing", "other half of decision 35", "DONE", "seats run in a copy; both reported pwd + no .git"),
 ("closing", "panel review of ALL unreviewed 24h work", "OPEN", "2 of N panels run; more remain"),
 ("closing", "test all fixes in the simulated run", "HELD", "marked on the runway; run held for founder"),
 ("closing", "fold-and-seal the keys, per-key extraction", "BLOCKED", "needs passphrase; extraction question answered"),

 ("severity", "require worked proofs for severity", "DONE", "built + enforced one-directionally; the grader itself was misreading models"),

 ("panel", "overlay: undeletable clone", "DONE", "chflags at creation; 264 orphans had accumulated"),
 ("panel", "overlay: absolute-symlink write-through", "DONE", "escaping links removed at build"),
 ("panel", "overlay: partial clone raises", "DONE", "stderr now checked as well as returncode"),
 ("panel", "vault: false VAULTED on a path with a space", "DONE", "here-doc instead of pipe; cc2's falsifier passes"),
 ("panel", "routing: docstring overclaimed", "DONE", "script supplies the figure; definition unified"),
 ("keys", "10 seal the answer keys: the commands themselves", "BLOCKED",
  "PREPARED; 3 data-loss defects fixed first; needs the founder's passphrase"),
 ("security", "credential leak in every repo copy", "DONE",
  "6 sites; .env with 10 live keys; scrub plus fail-closed verification"),
 ("panel", "overlay built 3x per finding (~8.3s)", "OPEN", "MEASURED, not acted on"),
 ("panel", "clone materialises .env outside the repo", "DONE", "scrubbed + verified at all 6 repo-copy sites"),
]


def main() -> int:
    argparse.ArgumentParser(description=__doc__.split("\n")[0]).parse_args()
    from collections import Counter
    from statsmodels.stats.proportion import proportion_confint

    counts = Counter(state for _, _, state, _ in ITEMS)
    n = len(ITEMS)
    print("CDSFL programme inventory — 2026-09-06")
    print("=" * 74)
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--short"], cwd=REPO,
                           capture_output=True, text=True).stdout.strip()
    print(f"  HEAD {head}, tree {'CLEAN' if not dirty else 'DIRTY'}\n")
    for state in ("OPEN", "BLOCKED", "HELD", "REFUTED", "DONE"):
        k = counts.get(state, 0)
        lo, hi = proportion_confint(k, n, alpha=0.05, method="wilson")
        print(f"  {state:8s} {k:3d} of {n}  {100*k/n:5.1f}%  Wilson [{100*lo:.1f}%, {100*hi:.1f}%]")
    print()
    for state in ("OPEN", "BLOCKED", "HELD"):
        print(f"  --- {state} ---")
        for src, item, st, why in ITEMS:
            if st == state:
                print(f"    [{src:8s}] {item}")
                print(f"               {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
