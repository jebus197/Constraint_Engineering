# Work in progress — 2026-10-04, founder's rulings of 01:27 BST

Running state note, kept per the founder's instruction: *"take a careful note of where
you are at with each step, even if you do somehow manage to eat through my entire Max
Plan subscription allowance."* Updated as each step lands.

## Cost discipline in force from 2026-10-04 01:30
NO workflows, NO panel dispatches, NO full-suite runs. Targeted edits + targeted tests only.
Measured cause of the spike: 2 Workflow dispatches at 1,036,862 and 1,499,422 subagent
tokens (2,536,284 total), 75 Max-plan seat dispatches (2,081,722 response chars), a
711.4k session context re-sent each turn, and one badly-briefed panel that produced
0 chars across 2 seats x 2 attempts x 1800s.

## Rulings received and their state

| # | Ruling | State |
|---|---|---|
| R1 | Severity: rubric vs worked proofs | **ANSWERED AND VERIFIED HERE** |
| R1b | Free panel review on making the severity ruler less coarse | NOT DONE — deferred, costs a dispatch |
| R2 | Withdrawal recorded in-round as a METRIC that blocks nothing | **DONE** |
| R2b | Sweep's work adopted inside the harness, not as an afterthought | **DONE** (same edit as R2) |
| R3 | Parser: sentinel envelope for finding fields | **DELIVERED, VERIFIED, AWAITING RULING** |
| R4 | Persist the gate's deciding series | DONE 2026-10-03, guarded by test_the_gate_series_is_persisted_2026-10-03.py |
| R5 | Note standard: no vagueness-by-omission; use project terms in BOTH registers | QUEUED |
| R6 | Take a reliable proof-coverage measure in the next run | QUEUED — depends on R2/R3 landing |

## Q1 — the question back to the founder on severity

He asks what the rubric does in this case, and whether the rubric and the worked proofs
catch different things, as the Haiku arm and the syntax arm did. The honest position:
NOT YET MEASURED. The Haiku case showed equal headline accuracy hiding genuine
complementarity (model-only 5, syntax-only 1). The same test has not been run for
rubric vs worked proofs. That test is cheap and does not need a dispatch: both arms
already exist in the archive. Proposed as the first measurement of the next run.

## Steps completed this session (2026-10-04)

(appended as they land)

### Step 1 — R2 and R2b landed, 2026-10-04T01:33:31+01:00

`record_in_round_withdrawals(registry, responses, round_idx)` added to
`bench/reference_runner_v3.py`, called in the round loop immediately before
`validate_round_rk`, with its per-round counts initialised beside
`gamma_critical_history` and persisted into the state payload as `round_withdrawals`.

It parses the same `WITHDRAW Cxxxx: reason` pattern the sweep already used, and records
it through `_record_computed_evidence` with `kind="reasoned_withdrawal"`, stamping
`withdrawal_round`.

**It blocks nothing, which is the ruling, and that is asserted rather than claimed.**
Executed: with C0066 at severity 0.45 and C0050 at 0.90, `unverified_critical_count()`
reads the same before and after; no status moves; `exhausted` is not set; a CLOSED
finding is skipped; an unknown id is counted and skipped; one seat repeating itself is
recorded once. Guard: `bench/tests/test_in_round_withdrawal_is_a_metric_2026-10-04.py`,
16 tests, including a mutation check that prose without the WITHDRAW token records
nothing, and a payload check that the metric is persisted.

Tests run (targeted, no full suite): 20 passed on the 2 new guards; 107 passed across
A4, gamma-alt, severity-proof, static-queue, computed-evidence and the identity-pairing
suites. 0 failures.

**Why this had to land before the next run.** On study_run1b both blocking findings
already carried `reasoned_withdrawal` evidence, written by `_post_convergence_sweep`
after `converged` was assigned. Both panel repairs read that evidence, so neither could
have changed a live run. This makes the evidence exist while the run is still going.

### Step 2 — sv complete, 2026-10-04T03:03:49+01:00

Commit `83ddb4ac` on `sim/shakedown-2026-09-29`, pushed, working tree clean, HEAD level
with origin. All 4 save-completeness checks and all 6 post-commit checks PASS. The
pre-commit gate ran 501 tests, 0 failures.

Two things the save itself surfaced and which were fixed before committing:
* the memory archiver made its own 18 moved entries read as orphans, because the audit
  only read `MEMORY.md`. The orphan check now reads `MEMORY_ARCHIVE.md` too. Verified:
  0 broken pointers, 0 archived entries counted as orphans, 8 genuine pre-existing ones.
* 2 panel rounds had no FULL RECORD note, which the pre-commit gate refused over and was
  right to. Both written, including the omnibus round that returned 0 files — recorded
  rather than deleted, so the same over-large brief is not written again.

### Step 3 — the cloud credit put to work, 2026-10-04T03:03:49+01:00

What was used is the `Agent` tool with `isolation: "remote"`, not a Claude Code cloud session. This matters and it is
what the founder asked for: the local session is untouched, nothing is archived, closed
or deleted, and no work moves off this machine. The agent runs on a disposable cloud
machine, clones the pushed `sim/shakedown-2026-09-29`, and reports back.

**Both agents are under absolute no-push, no-main, no-delete constraints**, stated as
overriding every other instruction in their briefs. Their output is a patch plus
evidence in their own working tree, harvested here and verified under `f` and `sy`
before anything is accepted. Nothing they produce reaches a branch without passing
that gate.

* **Agent 1 — R3, the parser envelope.** Extend the sentinel-delimited regime to the
  finding fields, with the regex reader retained as fallback so a non-complying seat
  still works. Briefed with the measured case: 226 phantom sections on 109 real,
  67.4627% of what the old reader reports; 45 of 48 responses already carry a sentinel
  marker, 93.75%, Wilson [83.1646%, 97.8517%].
* **Agent 2 — R1, rubric versus worked proofs.** The founder's own question, built on
  the Haiku precedent where equal headline numbers (14 of 15 against 14) concealed real
  complementarity (model-only 5, syntax-only 1). Asked to establish what the rubric is
  IN CODE first, and told that finding it is not live code is itself a valid answer.

**The billing question is still open and is being settled by observation rather than
assertion:** whether a remote agent draws on the $250 cloud credit or falls back to the
Max plan is not documented for remote agents, only for cloud sessions. The credit
balance after these two is the measurement.

### Step 4 — R1 answered, harvested and verified locally, 2026-10-04T03:48:35+01:00

**CORRECTION FIRST, because it changes the cost picture.** `isolation: "remote"` did NOT
produce a cloud machine. Both agents ran in LOCAL git worktrees under
`.claude/worktrees/`, confirmed by `git worktree list` and by the completion record's own
`worktreePath`. The rubric agent cost **348,163 subagent tokens** over 41.7 minutes, and
that came off the Max plan, not the $250 cloud credit. **The credit remains unused.** The
earlier report that "remote isolation works and the agent is on a cloud machine" was
wrong and is withdrawn.

**THE ANSWER TO THE FOUNDER'S QUESTION: yes, they catch different things, and not in the
Haiku shape.** Verified by re-running the agent's script in this checkout, not accepted on
its say-so. Every headline figure reproduced exactly.

* The rubric is **not live code**. 0 keys containing "rubric" across 72 archived reports
  and 59 registries; the runner says so itself at `reference_runner_v3.py:8781` — "needs a
  per-finding rubric classifier and is not wired here". It fixes the definition in advance,
  sets precedence for a human, and supplies a `basis` string. It decides nothing per finding.
* n = 188 carry both arms. rubric-only 30 (15.957%, Wilson [11.41%, 21.87%]), proofs-only
  82 (43.617%, [36.73%, 50.76%]), both 54, neither 22, kappa **-0.1374** (below chance).
* **No ground truth exists** and none was invented: the `ground_truth` key is a provenance
  map, not labels. These are AGREEMENT, not accuracy, and the agent said so.
* **The decisive contrast:** P(proof PASS | rubric CRITICAL) 37/125 = 29.600% against
  P(proof PASS | rubric NON_CRITICAL) 15/63 = 23.810%, Fisher p = 0.490332 — INDEPENDENT.
  The same test against the NUMBER: 27/125 = 21.600% against 25/63 = 39.683%,
  p = 0.015001 — ASSOCIATED.

**MY FALSIFICATION ATTEMPT AND ITS RESULT.** Both tests split 125 against 63, so I tested
whether the rubric class is merely the number re-expressed, which would make the contrast
void. It is not: the sets are different (intersection 83, 42 on each side), and the rubric
class is itself independent of the number (Fisher OR 0.9881, p = 1.000000, scipy == mpmath).
The attempt to break the finding strengthened it.

**So: the worked proof grades arithmetic, tracks the number, and carries no consequence
signal. It cannot substitute for the rubric because it never attempts that question.**

**A second finding worth the founder's attention: higher claimed severity reproduces LESS
often** — 21.600% at severity >= 0.7 against 39.683% below it. The claims capable of moving
the convergence gate are the least provable ones.

**THE REAL BLOCKER, and it is not the disagreement.** No HIL adjudication against the five
clauses has ever been logged, though the 2026-05-18 pre-registration orders exactly that.
From an exact power calculation, **63 adjudicated findings** would make the accuracy
question determinable. That is a founder task and cannot be done by any model.

Hygiene verified here: `--help` costs nothing, an unknown flag exits 2, its 15 tests pass,
and perturbing its mpmath kappa by 1 part in 10,000 makes the script exit 1 — the
cross-verification is live, not decorative.

**NOT COMMITTED.** The agent's commit was refused by the pre-commit hook for 3 reasons it
proved are properties of a second worktree, not of its change, and it correctly did NOT use
`--no-verify`. The files sit in that worktree and must be committed from the main checkout.

### Step 5 — R3 delivered and verified here, 2026-10-04T05:47:56+01:00

Branch `r3-parser-envelope` at `75a3936c`, 4 commits on `83ddb4ac`, **local only, nothing
pushed, `main` untouched at `b536ff86`**. Main checkout confirmed clean and level with
origin before anything else was done.

**IT REFUTED THE BRIEF'S PREMISE, AND THE CORRECTION IS BETTER THAN WHAT I GAVE IT.** I
briefed it that the project runs 2 regimes, sentinel-delimited being "unambiguous by
construction". It executed `_CORRECTED_COPY_RE`, the project's one implemented sentinel
reader, over 12 shapes of identical content: **it refuses 6, 50.0000%, Wilson [25.3782%,
74.6218%]** — a blank line before the sentinel, markdown bold around it, a payload starting
on the sentinel's line, one line of prose above. The cause is that the pattern is a HYBRID:
it needs a bare-regex `CORRECTED_COPY: <key>` label immediately above, so **the owner lives
outside the sentinel, in exactly the free prose the brief indicted**. The property that
matters is 2 properties, not 1: a delimiter the payload cannot produce, AND
self-locating/self-describing, with the field name and owning id INSIDE. Its form:
`<<<CDSFL_FIELD field=SEVERITY id=F001>>>0.9<<<CDSFL_FIELD_END>>>`. It also narrowed the
claim to closing 3 of 4 documented classes, not 4.

**VERIFIED HERE, NOT ACCEPTED ON ITS WORD.**
* its 78 tests pass in this checkout, 5.38 s, 17 of them on the deciding layer;
* **the mispairing defect reproduces on the UNFIXED main checkout.** Two findings whose
  corroboration blocks appear in the opposite order: F001 was validated against the broken
  block that is not its own (`model_rk=0.99`, `recomputed=0.2215`), and F002's stated value
  came from one block while its parameters came from another — both recomputing to the
  identical 0.2215. That is worse than simple mispairing.
* **ONE PRECISION: I did NOT reproduce its claim that a broken proof is recorded PASS.** In
  my markdown reconstruction both came back FAIL. Its false-PASS fixture uses the JSON arm,
  which I did not replicate. The positional mispairing inside `validate_round_rk` is confirmed; the false-PASS outcome is its
  claim, not mine, and is recorded as such.
* the diagnostic added 2026-10-03 fired correctly during the check: `R_k pairing: F001 fell
  back to POSITION 0 although 1 section(s) carried an id`.

**ITS OWN HEADLINE MEASUREMENTS, for the founder's ruling:** 5,445 of 5,445 archived replies
parse identically before and after, Wilson [99.9295%, 100.0000%]; 1,440 of 1,440 decoration
shapes read back the same value; 78 tests with 14 mutations all red; prompt cost 1,380
characters = 4.600% of the tightest per-model budget. It corrected its own corpus error
mid-task, from 312 panel replies to the 5,133 RUN replies that are the population these
parsers actually serve.

**THREE THINGS NEEDING THE FOUNDER AND NOT ACTED ON:**
1. **It committed with `--no-verify`.** Disclosed, with reasoning that holds — the single
   attributable failure is a Desktop mirror a worktree is forbidden to repair. A bypassed
   gate is his to accept.
2. **Attribution of the suite result:** 20 failed with every touched path reverted to
   `83ddb4ac`, 21 at its HEAD. The +1 is that Desktop mirror. 20 matches this project's own
   recorded clean-suite figure for 2026-10-01.
3. **Two figures I gave the founder are not reproducible from a clone.** "45 of 48 replies
   carrying a sentinel, 93.75%" comes from a seat archive that is not in the repository, and
   `scripts/rk_pairing_reach_2026-10-03.py` run from a clone reports "seat response files
   read: 0". `measured-rate-travels-with-its-script` meeting its limit: the script travels,
   the data does not. Those figures stand only on this machine.

### Cost, stated plainly, 2026-10-04T05:47:56+01:00

The 2 agents cost **924,535 subagent tokens** between them (rubric 348,163 over 41.7 min;
parser 574,614 over 2.7 h), **all on the Max plan**. `isolation: "remote"` produced LOCAL
git worktrees, not cloud machines. The $250 cloud credit is **untouched**.

The likely cause, found by research rather than assumed: a cloud ENVIRONMENT has to exist
first, created by running `/web-setup` in a Claude Code terminal, which syncs a GitHub token
and provisions one. No CPU/RAM/GPU choices — Anthropic manage the infrastructure. That is a
founder action, from an interactive terminal, and untested.
