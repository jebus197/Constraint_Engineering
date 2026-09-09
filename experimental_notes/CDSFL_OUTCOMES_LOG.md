# CDSFL outcomes log — the companion to the master task list

**Opened 2026-09-09 18:30 BST (Europe/London). Standing file. Append as each outcome lands; never rewrite.**

**Companion to `experimental_notes/CDSFL_MASTER_TASK_LIST.md`.** That file says what is to be done. This one says what was done, what it cost, and whether it can be undone. Desktop mirror: `~/Desktop/CDSFL_OUTCOMES_LOG.md`. The repository copy is canonical.

**Why it exists.** Founder instruction 2026-09-09, verbatim: *"You should of course be marking every outcome from all of your work in a companion file to the task list itself, so that it also does not get lost to compaction. A copy of this should also be placed on my desktop."*

---

## REVERSIBILITY, THE ANSWER TO THE FOUNDER'S QUESTION

He asked, verbatim: *"Would continuing risk anything I can't look at or you can't fix once the full task list is complete?"*

**No.** Census taken 2026-09-09 18:25 rather than asserted:

| Check | Result |
|---|---|
| Files deleted today | **0** |
| `exp39-experimental` branch | still present |
| `backup-pre-rewrite` ref | still present |
| Paid panel dispatch performed | **none** |
| Answer-key store touched | **no** |
| Commits today | 17, all in git |

Every change is a `git revert` away. The 3 categories that would NOT be recoverable are **deleting a git ref, spending money on a paid seat, and touching the sealed key store**. None has been done, and all 3 are on the task list as requiring the founder in person. **They will not be done without him.**

**Is item 3.1 a stopper? No.** The assistant stopped itself before changing anything, recorded why, and the work continues on the corrected item 3.1a. Nothing is broken and nothing is waiting.

---

## OUTCOMES, newest first

### 3.1 — SUPERSEDED. The "misconfiguration" was a deliberate mitigation. Commit `560c93a`
**Nothing changed in the configs.** The founder ruled that `routing_enabled: false` and `post_convergence_sweep_rounds: 0` in the 3 exp56 arms should be fixed, on an assistant report that said it was OPEN whether they were deliberate. **The record says deliberate.** They mitigate 2 live runner defects, each proven by an executing test: `_apply_routing` builds its ladder from the full orchestrator roster rather than `cfg.models`, so the 1-seat arm would dispatch to the vendors it exists to exclude, 3 of the 5 seats being paid; and the post-convergence sweep reaches undeclared seats. Both tests **passed rather than skipped** on 2026-09-09, so both defects are live. Flipping the flags would have destroyed the experiment and spent money. Superseded by **3.1a**, repair the runner to respect `cfg.models`, after which the guard lifts itself.

### 6.1 — DONE. All stop reasons now recorded. Commits `39b1042`, `e78fed4`
**23 of 41 archived runs never recorded why they stopped** — 56.1%, Wilson [41.0%, 70.1%]. All 23 INCOMPLETE; all 16 CONVERGED carry a reason. The round loop has **8 `break` statements and only 2 set `stop_reason`**. Root cause: the irreducible-queue halt set `result["convergence_reason"]` and never `brain.state`, so `_save_checkpoint()` on the next line wrote nothing — **the identical fault the gamma-alt comment records being repaired on 2026-05-18 for a different branch**. Fixed at the halt site before the checkpoint (ordering pinned by a test) and by a fallback before `signal_complete()` covering every exit including future ones, writing `UNRECORDED_STOP` rather than an empty string. 6 tests, 3 mutations, all caught.

### 2.1 — DONE. Falsifier intake. Commit `03ea98a`
**The recommended fix was refuted by measurement before it was applied:** widening the regex recovers **4,867 against 5,295 — a net loss of 428**. The diagnosis was right though: of 6,363 labels with a fenced block within 3 lines, **1,081 are missed, 16.99%**, Wilson [16.09%, 17.93%], and 1,066 of those carry a description between label and fence. Built as a **union**, which cannot lose an existing capture. The gap is constrained because a looser version captured `assert "FALSIFIER:" not in minimal` — **a false falsifier is worse than a missing one, the harness executes it**. Net **+492 recovered, 0 lost**. 13 tests, 3 mutations.

### 5.1 / section P — DONE. The panel brief format. Commit `7e26901`
The format did not exist. **Across 49 archived briefs: 0 required a seat to use the mathematical model as an instrument, 8 required a fix, 2 required the fix to be tested.** Template at `bench/directives/universal/panel_brief_template.md`, validator at `scripts/panel_brief_validate.py`, and the dispatcher **refuses** a failing brief before any of the 3 paid seats is reached. All 49 archived briefs would be refused, failing 1 to 7 checks, mean 2.4 — the spread is what shows it discriminates. Its own test tightened it twice; the second time because a document-wide search let a brief satisfy the output check by mentioning "verdict" anywhere.

### M1 + M2 — DONE. Task markers and the pulse hook. Commit `127fd36`
Composed rather than chosen, on the founder's correction. **Three regexes counted the same list as 23, 29 and 48; the true figure is 59.** Every entry now carries a machine marker; a 5th `UserPromptSubmit` hook injects the state each turn so it survives compaction. **The cross-check found a real fault on its first run** — entry 1.3 marked DONE with status PROPOSED. It was right: an item closed by founder ruling has no work product, and neither vocabulary could express "closed because it will not be done". A 5th state, `WITHDRAWN`, was added.

### 1.1 — DONE. The commit guard. Commits `33ce5d6`, `3c6f143`
Discussed 5 times since 2026-08-25, never built; `57d5a0e` reached HEAD that morning with the suite red. `hooks/pre-commit` runs 4 guards in 1.26 s against 670 s for the full suite, fails closed, `--no-verify` as the documented escape, wired by onboarding rather than by hand. **Proven live**: staging the previous day's exact breakage gives exit 1 and REFUSED. FOLLOW also found **3 of the 4 live hooks were in no repository at all**.

### Pass 5 — the evidence I said I preserved was never tracked. Commit `3c6f143`
Commit `3c4987d` stated the log and 22 snapshots "are now in the repo". They went into `bench/logs/`, which `.gitignore:41` excludes. **22 on disk, 0 tracked**, and the commit message asserting otherwise was false. Moved to `experimental_notes/evidence/`, stored as `.py.txt` so seat-written code stays out of the source scanners. Repository-wide: **177 of 3,803 cited `bench/logs/` paths are untracked**, 4.65%, Wilson [4.03%, 5.37%].

---

## STANDING NUMBERS

| Measure | Value |
|---|---|
| Full suite | 5555 passed, 4 skipped, 0 failed |
| Task list | 60 entries, 6 done, 1 withdrawn, 1 blocked |
| Commits today | 17 |
| Files deleted today | 0 |
| Mutations run today | 20, all caught once verified applied |

---

## WHAT IS NOT ESTABLISHED

Stated so it is not mistaken for a finding. Whether the falsifier gate ran in the 2026-09-08 run and recorded nothing, or never ran at all, is **OPEN** — the first search term used to test it was wrong and the stronger claim is not asserted without evidence. Whether the intake-parser repair would have prevented the halt is **OPEN**: recovering a block is necessary but not sufficient, since it must still bind to the right finding.

Written under CDSFL note standard v1.7 (26 August 2026).
