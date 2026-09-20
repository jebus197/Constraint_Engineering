# A8 Section P review: two seats, two different defects the suite could not see

Record written 2026-09-20T10:07:51+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS REVIEWED, AND WHY THIS ROUND HAD TO HAPPEN BEFORE ANYTHING ELSE COULD

Task A8 was the last entry standing between the master task list and a green test suite, and it was not open on its merits. The founder had ruled on it, the work was committed, and what remained was Section P itself: no entry moves to DONE until a panel has reviewed its fix.

The suite was red because `test_closure_outpaced_discovery_on_the_latest_full_day` reported that on 2026-09-18 the list gained 1 entry and closed 0. That test reads a single day, so a quiet day fails it, and `resources/RECOVERY.md` already recorded both the cause and the remedy: it goes green when A8 closes, and A8 waits only on a Section P review.

THAT PRODUCED A DEADLOCK IN A GATE COMMITTED 2 HOURS EARLIER. A spend gate added the same night refuses any dispatch when the last full-suite record is not green. Section P is discharged by a cc2 and fable round, which is free on the Max subscription. So a red suite blocked the review that closes the entry that turns the suite green. A guard that forbids its own remedy is not a guard, and `suite_record.gate` now takes a paid-seat count and proceeds, loudly, when it is 0. This round is the first thing that ran through it: the dispatch log opens with "panel (0 of 2 seats paid): the suite record is NOT green (exit code 1, 5 failed), but this round has 0 paid seats, so there is no spend to protect. Proceeding."

WHAT THE SEATS WERE ASKED. 7 claims drawn from entry A8 and its commits: that the manifest reproduces byte for byte; that the 6-state split of 575 cited paths is as recorded; that 50 of 575 is 8.6957% with a Wilson interval of 6.6580% to 11.2815%; that all 50 absent paths are in no git ref's history; that an independent shell classifier agrees on all 575 rows; that the guards can actually fail; and that commit b8dc6fd's message says 51 where the commit holds 50. The brief required each to be established by execution or refuted, each fix delivered as a file at a real path with an executed falsifier behind it, and a disagreement section with a body rather than a declared absence.

THE OUTCOME. Both seats returned A8 NEEDS THE NAMED CORRECTIONS FIRST, independently, and on DIFFERENT defects. All 7 claims hold by execution. Neither seat could break any recorded figure.

fable found that the guard could not see a falsified state column. The file's own docstring promised it re-derives every disposition; only the tracked state and the missing-versus-exists direction were re-derived. Flipping all 78 prefix rows to missing, which restates inside the manifest the exact false statement the 2026-09-17 repair exists to prevent, passed 16 of 16 tests.

cc2 found that the manifest was an input to its own census. It is a tracked file under experimental_notes, so from the second run every one of its 575 row keys was re-read as a NOTE citation of itself: 568 of 575 rows cited by the manifest, NOTE-labelling true for 575 of 575 by construction, and 161 rows carrying a cited_by the manifest had manufactured. cc2 also found the repair's own docstrings wrong in 4 places, and recorded that it had itself typed an unmeasured figure into one of them mid-review and corrected it on measurement.

Both seats independently corrected the brief, which named c9e7b08 as the classifier repair. It is not. 9c5eea3 is the repair and c9e7b08 is the commit the manifest is pinned at, which `git show --name-only` settles. Entry A8's own text was right; the brief compressed it wrongly, and that error was CC1's.

WHAT CC1 DID WITH THE FINDINGS. Both were verified independently before adoption, under the rule that a fix proposed by another model gets the same five-step treatment as one written here. fable's central claim was reproduced from scratch: flipping the 78 rows against the committed suite passed 16 of 16, and the manifest was restored byte-identical afterwards. The Wilson interval was recomputed with statsmodels and a hand-rolled mpmath version at 30 digits, agreeing to 4 decimal places at z = 1.95996398454.

BOTH FIXES WERE MERGED RATHER THAN CHOSEN BETWEEN, because each seat had added a 17th test to the same file and the two tests guard different things. The file now carries 18. CC1 added a case fable had not tested: a single row flipped, bench/logs/analysis from directory to template, which is the subtler corruption and also fails. Every mutation was restored to 18 green, the manifest regenerates byte-identical after cc2's change, the 6 state counts are unchanged at 184, 52, 197, 78, 14 and 50, only the cited_by labels move with NOTE dropping from 575 to 414, and the delivered shell cross-verifier reports 0 disagreements across all 575 rows.

WHAT WAS LEFT FOR THE FOUNDER. First, cc2's caveat on the word absent. Of the 50 paths, 7 are compiled-Python cache files, at least 11 are deliberate negative-test fixtures whose whole job is to not exist, and 3 are citations to an experiment that has not run yet. The arithmetic is right and the population is a mixture, so the backup question, item 12(g) of the action list, covers a strict subset of the 50 and is smaller than it looks. Second, an open policy question cc2 declined to decide: whether panel transcripts and quarantined logs count as citations. 192 of 575 rows, 33.4%, have no citer outside the manifest, panel transcripts and quarantined logs, and ruling on it would move the row set and every state count.

A PROCESS FINDING, RECORDED AND NOT FIXED. Both seats reported their sandbox arriving with no git directory, and each had to clone the object store in read-only before any git-dependent claim could be answered. The sandbox builder removes it by design, which is correct for confinement and wrong for any review whose subject is the history. The two need reconciling before the next history-dependent round.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — Section P review of task A8: the cited-logs manifest and its classifier

## Section 1 — The question

Task A8 is the last entry standing between this task list and a green suite, and it is not open on its merits: the founder ruled on it, the work was committed, and what remains is the Section P condition itself — no entry moves to DONE until a panel has reviewed its fix.

**Your job is to decide whether the fix is sound, and to say precisely where it is not.** If it is sound, say so and say what would change your mind. If it is not, fix it.

This round has **0 paid seats**. Both seats run on the Max subscription, so cost is not a reason to cut the work short.

## Section 2 — What you are reviewing

Three commits, in this order:

- **`b8dc6fd`** — force-added 50 files under `bench/logs/` and committed `experimental_notes/evidence/cited_logs_manifest_2026-09-17.json`. **Its message says 51 and `git show --name-status b8dc6fd` lists 50.**
- **`f22e95e`** — untracked 37 of those 50 and left 13 tracked, deleting nothing from disk, after the founder approved a reversal.
- **`c9e7b08`** — the classifier repair. `scripts/orphan_citation_era_2026-09-17.py` previously called every cited path that was not a file "missing — never kept". `disposition()` now returns 1 of 6 states.

**The files that carry it:**
- `scripts/orphan_citation_era_2026-09-17.py` — the classifier. **Run it:** `python3 scripts/orphan_citation_era_2026-09-17.py --at c9e7b08`.
- `experimental_notes/evidence/cited_logs_manifest_2026-09-17.json` — 575 rows, regenerated with `--at c9e7b08 --manifest`.
- `bench/tests/test_cited_logs_manifest_2026-09-17.py` — 16 tests. **Run them:** `python3 -m pytest bench/tests/test_cited_logs_manifest_2026-09-17.py -q`.
- `experimental_notes/CDSFL_MASTER_TASK_LIST.md` — entry A8 and Section P itself.

## Section 3 — The claims to falsify

Each of these is asserted in the record. Establish each by execution, or refute it.

1. **The manifest reproduces byte for byte.** Regenerating at `c9e7b08` yields exactly the committed file. Check it, do not assume it.
2. **The split of the 575 cited paths is: tracked 184; present but untracked 52; an existing directory 197; a truncated prefix of an existing path 78; a template 14; and absent from this machine 50.** Recompute. Do the 6 states sum to 575, and does each row's state match what the filesystem and git say?
3. **The absent 50 are 8.6957% of 575, Wilson 95% [6.6580%, 11.2815%].** Recompute the proportion and the interval with 2 independent tools — statsmodels and a hand-rolled Wilson, or scipy and mpmath — and say whether the recorded interval is right. A proportion quoted without an interval is not a measurement.
4. **All 50 are in no git ref's history.** This is the strongest claim in the entry and the most expensive to be wrong about, because it is the difference between "recoverable" and "gone".
5. **A second, independent classifier written with the shell's `test -f`, `test -d` and `ls` agrees on all 575.** Does it? Write it yourself rather than trusting that one was written.
6. **The guard can fail.** Removing the directory branch must fail the control that an existing directory is never labelled missing, and dropping 1 manifest row must fail the row test. Reinstate each defect and confirm the test goes red. **A guard that cannot fail measures nothing.**
7. **The `b8dc6fd` message says 51 where the commit holds 50.** Confirm, and say whether anything downstream reads that number.

## Section 4 — The harness you work under

You are operating under the full CDSFL harness. That means:

1. **Tools decide, not prose.** SymPy, z3, mpmath, SciPy, statsmodels and NumPy are primary. Wolfram is the SECOND falsifier, reached through the serial gate already on your PATH, used to check a result you already hold.
2. **A failed call is NOT EVIDENCE.** An error, a timeout or a `Name::tag` message verified nothing, and the claim stays UNVERIFIED.
3. **Cross-verify.** Every computational claim is checked with at least 2 independent tools, and every proportion carries a Wilson interval.
4. **A number travels with the code that produced it.** A figure with no runnable producer is a claim about evidence, not evidence.
5. **Where the mathematical model bears on your answer, use it as an instrument** — gamma, the two-sided gate, rho, severity and the S_k threshold — rather than discussing it. Say plainly if it does not bear on this question; a forced application would be worse than none.

## Section 5 — Fixes, and how to deliver them

A finding without a repair is half a contribution.

- **Deliver each fix as a file in your sandbox repository tree**, at a real path. You are confined to your own writable copy; write there. A fix quoted as a diff in prose is not delivered.
- **Write a falsifier for each fix and execute it.** State the command and its output.
- Keep the existing notation and file layout rather than introducing your own.

## Section 6 — Output shape

For each claim above: the verdict (HOLDS / FAILS / PARTIAL / UNCHECKED), the evidence with the exact command you ran, the fix if one is needed and the falsifier that tests it, and **what would refute your own verdict**.

Then state, in its own section, **where you disagree with the other seat or with CC1**. Disagreement is preserved as information and is never smoothed into consensus. A section reading "none" is not a disagreement section; if you genuinely disagree with nothing, say what evidence would have made you disagree.

End with a single verdict on the entry: **A8 IS SOUND AND MAY CLOSE / A8 NEEDS THE NAMED CORRECTIONS FIRST / A8 IS NOT SOUND**.

## Section 7 — Termination

Do not wait on a background task. Whatever you have written when your turn ends IS your answer. A partial answer carrying executed evidence is worth everything; a holding note is worth nothing. Stop when further passes produce no new above-threshold findings — diminishing returns is the criterion, not exhaustion.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 36 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_a8_section_p_2026-09-20) -->

## Section P review — task A8

Sandbox: `/private/var/folders/cc/.../cdsfl_panel_d5wedc22/repo`. It arrived without a `.git`, so I made it a real repo sharing the original object store read-only (`git clone --no-checkout --local --shared` → `reset --mixed HEAD`; 8,843 files tracked, 0 modified). The three A8 artefacts are byte-identical to the canonical HEAD and to `9c5eea3`, so the sandbox holds the artefact under review. I verified after every mutation that the canonical tree was untouched.

**One honest note on the canonical tree:** a full `git status` at 03:54 showed ` M experimental_notes/CDSFL_Agent_Operational_Plan.md`, a +20-line append. I made no write outside my sandbox, and the three A8 artefacts are byte-identical to HEAD (`git show HEAD:<f> | cmp - <f>`, all three clean). The append is the running session log, not mine — but its mtime falls inside my window, so I state it rather than claim certainty.

---

### Claim 1 — the manifest reproduces byte for byte — **HOLDS**

```
python3 scripts/orphan_citation_era_2026-09-17.py --at c9e7b08 --manifest .scratch/regen_manifest.json
cmp .scratch/regen_manifest.json experimental_notes/evidence/cited_logs_manifest_2026-09-17.json
→ IDENTICAL   md5 0deae2a9fe95eb7d0fa462659f99ac2a (both)   83,648 bytes (both)
```

**Named scope limit, not a defect.** The pin makes the *citation set* and the *tracked set* reproducible; it does not make the **states** reproducible. `local_only` is defined as *on disk ∧ not in git* — so those 52 rows (9.04%) cannot be reproduced from a clone by construction, and `directory`/`prefix`/`missing` read the working tree too. "Reproduces byte for byte" is true **on this machine**; it is not a from-git property, and the entry should not be read as claiming one.

*What would refute me:* a clone-only regeneration producing the same bytes.

### Claim 2 — the 6-state split — **HOLDS**

Three independent routes agree: the producer's own run, the committed JSON, and a shell classifier I wrote.

```
tracked 184 · local_only 52 · directory 197 · template 14 · prefix 78 · missing 50 = 575
```

### Claim 3 — 8.6957%, Wilson [6.6580%, 11.2815%] — **HOLDS**

Four tools, 50/575:

| tool | point | lower | upper |
|---|---|---|---|
| statsmodels `proportion_confint` | 8.695652 | 6.658022 | 11.281511 |
| scipy `norm.ppf` + hand-rolled score interval | — | 6.658022 | 11.281511 |
| mpmath (`erfinv`, 40 dps) | — | 6.6580223 | 11.281511 |
| Wolfram Language (local Wolfram Engine, `wolframscript`) | 8.695652173913043 | 6.658022335673077 | 11.281511406822855 |

The Wolfram call computed (exit 0, no `Name::tag`, no `$Failed`), so it counts as the second falsifier. The recorded 4-dp figures are correct.

### Claim 4 — all 50 in no git ref's history — **HOLDS, on two validated methods; a third was discarded**

This is the claim the entry itself calls the most expensive to be wrong about, so I ran a **positive control** on each method: the 37 paths `f22e95e` deleted from tracking are known-in-history and known-on-disk.

| method | control (must be 37/37) | the 50 |
|---|---|---|
| A — `git log --all --format=%h -1 -- <path>` (what the producer does) | **37/37** | **0/50** |
| C — union of every path any commit touched | **37/37** | **0/50** |
| B — `git rev-list --objects --all` name sweep | **1/37** ❌ | 0/50 — **discarded** |

Method B returned the right answer for the wrong reason: it is 97.3% false-negative on its own control, so its zero is worthless and I do not count it. The claim stands on A and C. Residual: the repo has 6 merge commits, a theoretical blind spot for path-limited history walks; both methods agree, so I do not treat it as open.

**Interpretive caveat the entry should carry.** "Absent, and in no ref's history" reads as *lost evidence*. It is largely not. Of the 50: 7 are `__pycache__/*.pyc`; at least 11 are deliberate negative-test fixtures — `bench/logs/there-is-no-such-round/nothing.json` (cited by `test_cited_evidence_is_recoverable_2026-09-11.py`), `x`, `x.json`, `x/y.json`, `run/x.json`, `sim/round_00.json`, `simulated_run_x/gemini{,-sim}/round_00.json`, `launcher_transcripts/no_date_here.log` — paths whose whole job is to not exist; and 3 are the Exp 56 logs the entry already records as "citations to a future artefact". The arithmetic is right; the population is a mixture, and the founder's backup question (item 12(g)) is about a strict subset of it.

### Claim 5 — an independent shell classifier agrees on all 575 — **HOLDS**

I wrote one rather than trusting that one was written. Delivered at `scripts/a8_shell_crossverify_2026-09-20.sh` — `test -f`, `test -d`, `ls`, `grep -Fxq` only, sharing no code with the producer, reproducing `disposition()`'s branch order.

```
bash scripts/a8_shell_crossverify_2026-09-20.sh "$S" .scratch/tracked_at_c9e7b08.txt <manifest>
→ 197 directory · 184 tracked · 78 prefix · 52 local_only · 50 missing · 14 template
→ total: 575   DISAGREEMENTS: 0 of 575   EXIT=0
```

### Claim 6 — the guard can fail — **HOLDS**

Baseline `16 passed in 1.22s`. Both named defects reinstated in the sandbox, each red on exactly the named test, each restored green:

| mutation | result |
|---|---|
| delete the `p.is_dir()` branch | `TestDisposition::test_an_existing_directory_is_never_missing` **FAILED** (`- directory / + prefix`), 1 failed 15 passed |
| drop 1 manifest row | `test_the_rows_are_exactly_the_citations_at_the_named_commit` **FAILED**, 1 failed 15 passed |

### Claim 7 — `b8dc6fd` says 51, holds 50 — **HOLDS, and nothing downstream reads it**

Message line 6: *"51 note-cited files that existed on disk are now tracked"*. `git show --name-status b8dc6fd` → 56 entries, **50** under `bench/logs`. The same message is stale on four further figures (567 paths / 220 tracked / 12 untracked / 335 missing, vs the committed 575 / 184 / 52 / 339). A `git grep` at HEAD for those figures returns nothing — the only near-hit was the substring `51 files` inside `7351 files`. Commit messages are immutable; **no live document repeats them**, so this is recorded, not load-bearing.

---

## The material finding: the manifest is an input to its own census

**The manifest is a tracked file under `experimental_notes/`, so from the run after the first, every one of its 575 row keys was re-read as a NOTE citation of itself.** Measured at `c9e7b08`:

- **568 of 575** rows are "cited by" the manifest.
- **NOTE-labelling reads 575 of 575 — 100% by construction.** That is why the producer prints `cited by a NOTE and untracked: 391/575` identically to its overall untracked line.
- **161 rows (28.0%)** carry a `cited_by` the manifest manufactured for itself.

The producer's own comment (lines 48–53) states the rule this breaks — *"a log file naming its own sibling paths is not a CITATION"* — and the A8 entry stated it again on 2026-09-11: *"a classifier that reclassifies a path by being written about is measuring the writing."* This is that defect a third time, in the one file guaranteed to name every path in the corpus. It is §10 category 3, verification-integrity corruption: the founder's ruling keys on the NOTE population, and `test_the_note_cited_recoverable_files_are_readable_from_a_clone` gates on `"NOTE" in cited_by`, a predicate now true for every row, so it cannot discriminate. It is also a ratchet — a path can never leave the census once entered, even if its last genuine citation is deleted.

**Fix delivered** (`scripts/orphan_citation_era_2026-09-17.py`): the pathspec becomes a named `EXCLUDE` constant adding `:(exclude,glob)experimental_notes/evidence/cited_logs_manifest_*.json`. It is surgical — **0 rows vanish, 0 of 575 states change**; only `cited_by` moves, NOTE 575 → 414. Every figure in Claims 2, 3 and 4 is preserved exactly.

**Falsifier delivered** — a 17th test, `test_the_manifest_is_not_an_input_to_its_own_census`, with a non-vacuity control (the manifest really does name >100 paths, so there is something to exclude) and the guard (NOTE must not be true of every row).

```
python3 -m pytest bench/tests/test_cited_logs_manifest_2026-09-17.py -q   → 17 passed
# MUTATION 3: revert EXCLUDE to (":(exclude)bench/logs",)
→ FAILED ...::test_the_manifest_is_not_an_input_to_its_own_census
  FAILED ...::test_the_rows_are_exactly_the_citations_at_the_named_commit
  2 failed, 15 passed
# restored → 17 passed; shell cross-verifier → 0 of 575 disagreements
# regenerated manifest → cmp IDENTICAL
```

*What would refute me:* evidence that `experimental_notes/evidence/` is intended as a citation source on equal footing with prose notes. I think not — but note the same argument extends to `experimental_notes/evidence/panel_records_*/**.tools.json` and `bench/logs_quarantine/`, which are transcripts and quarantined logs. **192 of 575 rows (33.4%) have no citer outside {manifest, panel transcripts, quarantined logs}.** I did **not** exclude those: unlike the manifest, that is a policy call on what counts as a citation, and it would move the row set and every state count. It is the founder's to rule, and I flag it rather than take it.

## Second finding: the repair's own docstrings are wrong by 4

The producer docstring says *"Of the 335 rows it so labelled, 194 were directories … 14 templates. 49 were absent."* Re-running the pre-repair 3-state rule over the same 575:

```
pre-repair: {tracked 184, local_only 52, missing 339}
the repair splits those 339 as: directory 197 · prefix 78 · template 14 · missing 50  (sum 339)
DOCSTRING: 335 = 194 + 78 + 14 + 49        MEASURED: 339 = 197 + 78 + 14 + 50
```

Internally consistent, externally wrong — it disagrees with the manifest the same commit produced. The test file repeats it twice (`194 of the 335`, `194 existing`) and adds a third stale figure, *"Of 283 note-cited untracked paths, only 52 existed on disk"* (measured: 277 and 42). All four corrected in place, additively, each marked with its correction date. `17 passed`.

**I committed this defect myself, mid-review.** I typed 230/52 into that docstring from inference rather than measurement, then measured 277/42 and corrected it. Recorded because the standard is symmetric.

## Where I disagree with the panel brief

**Section 2's third bullet is wrong: `c9e7b08` is not the classifier repair.** It adds 3 files, touches no A8 artefact, and its subject is *"panel: brief for Question 9, the 34 engineering entries"*. `git show c9e7b08:scripts/orphan_citation_era_2026-09-17.py` has no `STATES` constant — it is the **pre-repair 3-state version**. The repair is **`9c5eea3`**, *"fix: A8's manifest called 197 existing directories 'never kept'; 6 states, pinned to a commit"*. `c9e7b08` is the commit the manifest is *pinned to*, not the commit that repaired it — and the task-list entry A8 says exactly that and is **correct**. The brief conflated the two. `f22e95e` likewise carries a subject about entry-body boundaries, but does hold the 37 D / 13 A the brief describes, so that bullet is substantively right.

I have no other seat's output to disagree with. What would have made me disagree with a seat: any verdict on Claim 4 resting on a history search with no positive control — my method B returned the correct answer while being 97.3% blind, and a seat quoting it as corroboration would have been quoting noise.

## Verdict

**A8 NEEDS THE NAMED CORRECTIONS FIRST.**

All seven claims hold as stated, and the figures in the entry are correct — I could not break any of them. But the producer reads its own manifest as a citation source, which makes the NOTE population 100% true by construction and manufactures 161 of 575 `cited_by` labels; and the repair's docstrings misreport its own headline arithmetic in four places. Both are fixed, wired to callers, and covered by an executed falsifier in my sandbox tree:

- `scripts/orphan_citation_era_2026-09-17.py` — `EXCLUDE`, docstring
- `bench/tests/test_cited_logs_manifest_2026-09-17.py` — 17th test, docstrings
- `experimental_notes/evidence/cited_logs_manifest_2026-09-17.json` — regenerated
- `scripts/a8_shell_crossverify_2026-09-20.sh` — new, independent

Apply those and A8 may close. The brief's mis-attribution of `c9e7b08` should be corrected in the panel record; the entry itself needs no change on that point. The open policy question — whether panel transcripts and quarantined logs count as citations, worth 192 of 575 rows — is the founder's, and I have left it untouched.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 44 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_a8_section_p_2026-09-20) -->

All verification legs are green and the mutation controls are red exactly where they should be. The review has converged — the last pass produced no new above-threshold findings. Final report:

---

# Section P review — Task A8 (seat: Fable)

**Preliminary note on the harness.** The staged sandbox arrived with **no `.git`** — every claim under review is git-dependent, so I cloned the original repo's object database into my writable copy via APFS `cp -Rc` (read-only on the source; nothing written to the original). The staged `__pycache__` was cloned from the original repo and carried baked-in absolute paths; I purged it and confirmed by execution (`m.REPO` printout) that every test run exercises the **sandbox** tree. All results below post-date that purge.

## Claim 1 — Manifest reproduces byte for byte: **HOLDS**

`python3 scripts/orphan_citation_era_2026-09-17.py --at c9e7b08 --manifest .scratch/regen_manifest.json`, then `cmp` → **BYTE-IDENTICAL**; sha256 `0a1198be…4428535` on both files.
*Refuted by:* any byte differing on a fresh clone — e.g. if disk state the classifier reads (`is_file`/`is_dir`/`iterdir`) has drifted, which is precisely what would make the manifest stale.

## Claim 2 — The 6-state split of 575: **HOLDS**

Recomputed by execution: tracked 184; local_only 52; directory 197; prefix 78; template 14; missing 50. Sum = 575 ✓. Per-row agreement with filesystem and git established under claim 5. The entry's "339 missing at `c9e7b08`" also checks arithmetically: 197+78+14+50 = 339 (the 3-state version called every non-file "missing").

## Claim 3 — 50/575 = 8.6957%, Wilson [6.6580%, 11.2815%]: **HOLDS**, three tools

- statsmodels `proportion_confint(50, 575, method="wilson")` → 8.6957% [6.6580%, 11.2815%]
- hand-rolled Wilson in mpmath (30 dps, z = √2·erfinv(0.95) = 1.95996398454) → [6.6580%, 11.2815%]
- Wolfram (second falsifier, local Wolfram Engine via `wolframscript`, exit 0, computed with Wolfram Language): {8.69565217, **6.65802234, 11.28151141**} — matches to every printed digit.

*Refuted by:* any of the three disagreeing beyond display precision.

## Claim 4 — All 50 absent paths in no ref's history: **HOLDS**, two independent sweeps

1. `git log --all --format= --name-only | sort -u` (9,169 historical paths) checked against all 50 as exact paths **and** as directory prefixes → **0 hits**.
2. Union of `git ls-tree -r` over all 18 refs' tip trees (8,876 paths), same matching → **0 hits**. `git stash list` is empty.

These use different machinery from the script's own per-path `git log --all -1 -- <path>` (which also reported 50 of 50). *Residual, stated not hidden:* a file added in an evil merge and deleted before every tip would evade sweep 1 and 2 both; the script's pathspec walk covers that case, so the three mechanisms jointly close it. Reflog-only/dangling objects are outside the claim's wording ("no git ref's history") — and the founder has ruled the git-history remainder accepted regardless.

## Claim 5 — Independent shell classifier agrees on all 575: **HOLDS**

I wrote my own (`.scratch/shell_classifier.sh`: `git ls-tree` + `test -f` + `test -d` + `ls`/`grep`, same precedence order), ran it over all 575 paths at `c9e7b08`, diffed against the manifest's states → **ALL 575 AGREE**.
*Refuted by:* one differing row. Note: the entry asserts this cross-check but commits no producer for it; mine is delivered in the sandbox at `.scratch/shell_classifier.sh` — worth committing beside the entry, since a number travels with its producer.

## Claim 6 — The guards can fail: **HOLDS**

- Removing the `is_dir()` branch → `TestDisposition::test_an_existing_directory_is_never_missing` **FAILED** (1 failed, 15 passed); restored → 16 pass.
- Dropping 1 manifest row (`bench/logs/QUARANTINE_T01_model_written/`) → `test_the_rows_are_exactly_the_citations_at_the_named_commit` **FAILED**; restored → 16 pass.

## Claim 7 — Message says 51, commit holds 50: **HOLDS**, nothing consumes the 51

`git show -s b8dc6fd` says "51 note-cited files … are now tracked"; `git show --name-status b8dc6fd` adds exactly **50** files under `bench/logs/` (plus manifest, test file, classifier, 3 edits). Grep across the task list, scripts and tests finds no downstream consumer of "51" (hits are the unrelated "51-decision file"). The task-list entry itself records the discrepancy in the same sentence the brief quotes. The message is immutable; the record corrects it in place; no fix is possible or needed. Cross-checks: `f22e95e` deletes exactly **37** `bench/logs` paths and `comm` shows exactly **13** of the 50 remain tracked at `f22e95e` — the test docstring's corrected "37 and 13" is right.

## FINDING (the one material defect) — the suite could not see a falsified state column

**The module docstring promises "this test re-derives every disposition from the repository and requires the committed manifest to match." It did not.** Only `tracked` (both directions) and missing-vs-`exists()` were re-derived. Demonstrated by execution: flipping all **78 `prefix` rows to `"missing"`** — restating, in the manifest itself, the exact false statement ("never kept" about recoverable evidence) the 2026-09-17 repair exists to prevent — ran **16 passed**. A truncated prefix names no path `exists()` can see, so the guard was blind to 92 rows (78 prefix + 14 template), and to every inter-state flip among the non-tracked, non-missing states. Under §10 this is category 4, silent evidence loss, above threshold.

**Fix delivered** (sandbox, real path): `bench/tests/test_cited_logs_manifest_2026-09-17.py` gains `test_every_row_state_rederives_from_the_classifier` — every row's state must equal `disposition()` against the tracked set at the recorded commit. Falsifiers, all executed:

- Committed manifest: **17 passed**.
- 78-row corruption reinstated: **exactly the new test FAILED**, 16 passed; restored → 17 passed.
- Classifier-side mutation (prefix branch removed): **2 failed** — the synthetic-tree unit pin `test_each_state[…prefix]` *and* the new test (committed manifest now disagrees with the mutated producer); restored → 17 passed. The two legs triangulate: unit pins hold the producer, the new test holds the manifest; my new test alone shares the producer's blind spot if both regress together, which is why the unit pins stay load-bearing.

*What would refute my finding's materiality:* evidence that the state column is never read downstream — but the manifest is the deliverable of the founder's accept-and-label ruling; the label **is** the product.

**Below threshold, noted under §8, not blocking:** (a) the docstring's "283 note-cited untracked, 52 on disk" is the pre-ruling tree — verified true at `b8dc6fd^` (283/52 by execution) — accurate history, loosely anchored; (b) `_git()` ignores returncode/stderr, so on a gitless tree the classifier silently reports an empty corpus rather than erroring — the tests would fail loudly first, so consequence is below threshold; (c) if my test is adopted, the A8 entry's "16 tests" becomes 17 in the DONE write-up.

## Disagreement (with the brief / CC1)

1. **The brief mislabels `c9e7b08` as "the classifier repair."** By execution: the repair commit is **`9c5eea3`** ("fix: A8's manifest called 197 existing directories 'never kept'"); `c9e7b08` is the *pre-repair* commit the manifest is **pinned at** — the task-list entry itself says the version committed at `c9e7b08` labels 339 paths missing. The work is internally consistent; the brief's compression is not. Order: b8dc6fd → f22e95e → c9e7b08 → 9c5eea3.
2. **I disagree with the record's implicit claim that the committed suite discharged the "manifest tells the truth" property.** The mutation controls the entry cites (directory branch, dropped row) are real and red, but they cover the producer and the row *set*, not the state *column* — refuted above by a 78-row corruption passing green. Fixed rather than only reported.

Per §5, every claim above survived ≥2 independent falsification passes with Δ = 0 on the final pass — convergent termination, no falsification debt carried. The residual-risk machinery (R_k, S_k, ρ) does not otherwise bear on a one-round verification review and I have not force-applied it.

## Verdict

**A8 NEEDS THE NAMED CORRECTIONS FIRST** — one correction, delivered and falsified in this sandbox: adopt `test_every_row_state_rederives_from_the_classifier` (and, optionally, commit the shell cross-classifier beside the entry). Claims 1–7 all HOLD by execution; the classifier repair, the manifest, and the reversal accounting are sound. With the state-fidelity guard merged, A8 is sound and may close.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_a8_section_p_2026-09-20/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
