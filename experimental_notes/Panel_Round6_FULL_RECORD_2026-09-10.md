# Panel Round 6 — FULL RECORD, unfiltered

Record written 2026-09-11T09:40:22+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

Round 6 asked how to fix what round 5 had found. It is the second half of a pair and should be read after `Panel_Round5_FULL_RECORD_2026-09-10.md`.

## What the round found

**The disagreement between the seats was real and not decorative:** fable called cc2's half *"the smaller half"* to its face. Both positions were preserved and reported to the founder unsmoothed, which is what the no-compelled-convergence condition is for.

**THE SAME HARNESS DEFECT AS ROUND 5.** Both seats wrote working fixes into scratch space and `bench/panel_sandbox.py:teardown` destroyed them, so this round also returned 0 source files. That is a defect in the harness and not in the seats, and it is why round 7's brief opens with an explicit delivery rule.

**A CAUTION THAT APPLIES TO THIS ROUND.** Until task A20 landed on 2026-09-11, all seats shared ONE writable sandbox and ran concurrently. Agreement between seats here is not evidence of independence.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 6: how to fix it. You diagnosed it; now produce the repair and test it.

<!-- figure: gamma at 13 passes | scripts/ffafp_cycle_gamma_2026-09-10.py | 0.294998 -->

**Founder instruction, verbatim:** *"Ask them too how you should fix these problems when they are done."*

**Read this first.** Several figures below have NO committed producing script. They are marked UNBACKED where that is true, because in round 5 fable caught the assistant quoting `rho = 0.4001` in a brief arguing about evidence discipline while having no script for it. That is the defect, admitted rather than repeated. Do not treat an UNBACKED figure as established; re-derive or reject it.

## SECTION 1 — What you found, and where you disagree

You reviewed `experimental_notes/CDSFL_MASTER_TASK_LIST.md` (84 entries, 508 lines) and its companion `experimental_notes/CDSFL_OUTCOMES_LOG.md`. You disagreed, and the disagreement is the subject of this round. It is preserved, not smoothed.

**cc2 said CONFIRMED, and sharpened it.** The list is 2 documents in 1 file, and 1 of them is an inbox for the process meant to empty it. Splitting the 84 entries by provenance: the founder's numbered itinerary (sections 0 to 10, plus L and M) is 40 entries with 19 DONE, 47.50%, Wilson [32.94%, 62.50%]; the review-generated backlog (P, R, Z, A, V) is 44 entries with 3 DONE, 6.82%, Wilson [2.35%, 18.23%]. Fisher exact p = 3.555346e-05, odds ratio 12.3651; chi-square with Yates p = 6.694047e-05; an mpmath exact hypergeometric upper tail gives 2.001149e-05. **REPRODUCED by the assistant against `scripts/task_list_markers.py`, but with NO COMMITTED SCRIPT — UNBACKED.**

**fable said PARTIAL, and called that the smaller half.** Its classification of the documented failed claims found **never-true-at-write-time failures outnumbering staleness failures roughly 2 to 1**. Its conclusion: a queue/archive/ledger split fixes accretion and staleness carry-forward and does nothing about a figure that was wrong the moment it was typed. It named the dominant defect generator as **unbacked figures**, and the remedy as the figure-declaration mechanism in `scripts/panel_brief_validate.py` (`check_declared_figures`), not document architecture.

**fable also refuted a claim in the round-5 brief.** It ran the 22 evidence files inside the panel sandbox and got **8 failed, 639 passed, 1 skipped**, because the sandbox has no `.git`. So "22 of 22 pass" is an environment-relative claim reported as an absolute one; **20 of 22**, Wilson [72.19%, 97.47%], with 2 asserting properties of a configured repository rather than of the artefact. That is the fresh-clone class already on the list as entry A2.

**A correction the assistant owes both of you.** It told the founder the list "provably does not converge" at p = 0.000910, from 22 closures of 71 movements. That counted the initial population build-out — 35 to 59 entries on the day the list was written — as discovered work. Excluding it: 25 appended after the list was populated against 22 closed, arrival over closure 1.1364, binomial test p = 0.3854, **not significant**. The divergence claim is WITHDRAWN. cc2's 1.09 was the better denominator.

## SECTION 2 — Use the harness

**Produce your answer by RUNNING things. A remedy you have not executed is a suggestion.**

- **`scripts/task_list_markers.py`** — drive `parse_entries`, `check` and `unsupported_done_entries`. Any remedy that changes the document's shape must keep these working, or say what replaces them.
- **`scripts/panel_brief_validate.py`** — `check_declared_figures` is the mechanism fable proposes generalising. Execute it. Establish what it can and cannot catch. It re-executes a declared figure's script and compares an exact string; ask what happens to a figure that is a rate rather than a literal, to one whose script takes 45 seconds, and to the 379 archived notes that declare nothing.
- **`scripts/ffafp_cycle_gamma_2026-09-10.py`** — the two-sided gate, gamma at or above 0.30 AND 3 consecutive zero-discovery passes. Both sides currently FAIL. If your remedy changes what counts as a finding, say what it does to this gate.
- **Wilson intervals, Fisher exact, and a second independent implementation** for every proportion you report. Two tools, minimum.

## SECTION 3 — Produce a fix, and test it

**This round's deliverable IS the fix.** Round 5 was the diagnosis. Give a repair for each problem below that someone could apply tomorrow, and execute enough of it to show it works.

1. **The register collision.** One entry carries an immutable original statement, a mutable current status, and an append-only correction log, with no rule for which wins. 15 of 84 entries carry 2 or more in-place corrections; entry 1.1 carries 8 and cites 5 distinct dates in one paragraph. UNBACKED. What is the concrete new shape, and what migrates where?
2. **Unbacked figures.** fable's dominant generator. What is the rule, what enforces it, and what does it cost on a document with hundreds of existing figures? Does it apply retrospectively or only to new claims?
3. **The review exhaust.** 44 entries generated by the assistant's own review process, closing at one twelfth the rate of the founder's itinerary. Should they be in this list at all? If not, where, and what stops them being lost?
4. **35 uncommitted files, over 7 hours.** Claimed to cause 12 of 19 overstatement verdicts because entries say COMMITTED while naming untracked files. UNBACKED. What is the rule that prevents it recurring?
5. **DONE means 2 different things.** The evidence executes for every entry, while 116 of 266 of the surrounding claims do not hold. Should DONE bind the code, the prose, or both, and what checks whichever you choose?

**Where you propose a checker, WRITE IT and RUN IT.** Report the exact command and output. Where you claim an existing test is weak, mutate the source, assert the mutation applied AND that it lands on a line the fixture executes, run the test, report whether it went red.

**Work in the sandbox copy. Do not modify the canonical tree.** Note that the sandbox has no `.git` — fable established that in round 5 — so plan around it and say which of your figures that limits.

## SECTION 4 — What would refute you

State, before concluding, what evidence would overturn your own remedy.

Specifically: name the failure mode your fix does NOT address. If you are cc2, say what document architecture cannot fix. If you are fable, say what figure discipline cannot fix. And say what it would take to change your mind about the other seat's position, because on the evidence so far both of you are partly right and the founder needs to know which half to build first.

## SECTION 5 — Output shape

- `verdict` — your position on which remedy should be built FIRST, and why
- `fix` — the repair, concretely, per numbered problem above
- `falsifier` and `falsifier_result` — what you executed and what it returned
- `migration` — what happens to the 84 existing entries under your remedy, and who does it
- `cost` — what your fix costs in time and in what it makes harder
- `refutation_condition` — Section 4's answer
- `strongest_disagreement` — with THIS brief and with the other seat. Do not converge.
- `passes_run` — how many

## SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. A finding is above threshold if missing it could let a false completion claim stand, break a live run, or feed the founder a stale fact as a current one. Diminishing returns is this project's own criterion and it applies to you.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 29 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round6_2026-09-10) -->

## verdict

**Build the figure rule first — but not the mechanism fable named, because I executed it and it does not catch the class fable diagnosed.**

fable is right about the generator and wrong about the remedy. cc2 is right about the diagnosis and its remedy is 2/3 obtainable for ten lines. Both of those are executed results below, not judgements.

The deciding argument is cheapness and precedence: cc2's headline figures were marked UNBACKED in this brief. I wrote the missing script in about fifteen minutes and **every one of them reproduced exactly, under two independent implementations agreeing to 1e-12**. That is the case for figure discipline going first — not that cc2 is wrong, but that the cost of making cc2's argument trustworthy is a quarter-hour, and until it is paid nobody can safely act on it. A document migration cannot be evaluated on figures that might be wrong.

## fix

**2. Unbacked figures (build first).** `check_declared_figures` has two holes, both executed:

*Hole A — it is opt-in.* Its own docstring: "A brief that declares NOTHING passes."

```
$ python3 scripts/panel_brief_validate.py /tmp/seat_cc1_r6/BRIEF_round6.md
panel-brief: BRIEF_round6.md carries all 7 required sections
EXIT=0
```

**This brief — whose subject is unbacked figures, which marks seven of its own figures UNBACKED in prose — passes the mechanism proposed to fix unbacked figures.** That is the whole defect in one command.

*Hole B — it compares by substring* (`if want not in (r.stdout + r.stderr)`):

| declared value | old (substring) | new (token) |
|---|---|---|
| `0.294998` (truth) | PASSES | PASSES |
| `0.2` | **PASSES** | REFUSED |
| `0.29` | **PASSES** | REFUSED |
| `1` (rides on `pass 1:`) | **PASSES** | **PASSES — still open** |
| `0.451` (genuinely wrong) | REFUSED | REFUSED |

Declaring gamma as `0.2` currently reproduces against `0.294998`.

**The rule I propose is deliberately not "every figure needs a script"** — unaffordable against hundreds of task-list figures and 379 archived notes, and unaffordable rules get switched off. It is:

> **Every figure is either backed or marked.** A backed figure declares a script and must reproduce *by token*. An unbacked figure must say so in the paragraph carrying it. A **silent** figure is refused.

The cost of an unbacked figure becomes one word, not one script. **Not retrospective** — `scan()` takes one document and the caller passes the brief, not the archive. That is the same argument the opt-in design used, applied where it is actually true.

**3. The review exhaust.** Keep the 44 in one file, but stop calling them the same kind of object. Add a `provenance: founder|review` field to the existing marker and make `--summary` print the two closure rates separately. That is a field, not a file move, so nothing can be lost in a migration — and it makes starvation visible on the pulse line every day instead of requiring a panel round to notice.

**1. The register collision — the machine-readable half is free.** `parse_entries` reads the marker on the line *after* a heading and nowhere else. Any marker elsewhere is invisible to every tool, **including `check()`'s own duplicate-identifier test, which cannot fire on an identifier `parse_entries` never emitted.**

```
$ python3 /tmp/seat_cc1_r6/orphan_markers.py scripts
CDSFL_MASTER_TASK_LIST.md:191: ORPHAN marker ... <!-- task: 2.1 | state: DONE | status: ENABLED -->
CDSFL_MASTER_TASK_LIST.md:282: ORPHAN marker ... <!-- task: 5.1 | state: DONE | status: ENABLED -->
orphan-markers: 2 problem(s)   EXIT=1
```

86 marker lines, 84 attached, **2 orphans, both claiming DONE**, both differing from the attached marker for the same identifier (no `evidence:` field). `task_list_markers.py --check` reports "84 entries, 0 problems". Two records of one entry's state, no rule for which wins, and the tool silently picks one — the register collision, in ten lines of fix, with no migration.

**5. DONE should bind the code — and it already does, completely.** Measured: **22 of 22 DONE entries carry an `evidence:` field, 22 of 22 named files exist**, and `unsupported_done_entries` correctly maps synthetic failures back to entries 1.1 and 2.1. **0 of 22 bind any prose claim.** So DONE does not mean two things ambiguously; it means one thing tightly and one thing not at all. Don't widen DONE — the tight half is this list's only working guard. Bind the prose separately with the figure ledger (fix 2), which is the *only* checker that reads the surrounding claims.

**4. 35 uncommitted files.** The rule that prevents it: `hooks/pre-commit` already exists and is enabled (entry 1.1). Add a seventh guard refusing a commit whose diff touches the task list while an entry says COMMITTED naming an untracked path — one `git ls-files --error-unmatch` per named path. **I cannot execute this: the sandbox has no `.git`.** Untested, and I decline to claim otherwise.

## falsifier / falsifier_result

Above, plus two more executed results:

**cc2's figures, now backed** (`/tmp/seat_cc1_r6/task_list_provenance.py`, proposed as `scripts/task_list_provenance.py`):
```
founder  DONE 19/40 = 47.50%  Wilson [32.94%, 62.50%]
review   DONE  3/44 =  6.82%  Wilson [ 2.35%, 18.23%]
odds ratio 12.3651
Fisher one-sided (log-gamma, mine) : 2.001149e-05
Fisher one-sided (scipy)           : 2.001149e-05   agree to 1e-12: True
Fisher two-sided (scipy)           : 3.555346e-05
```
Every cc2 figure reproduces. **cc2 is CONFIRMED on the arithmetic.**

**The fix, run on this brief:**
```
$ python3 /tmp/seat_cc1_r6/figure_ledger.py --repo <repo> BRIEF_round6.md
  - line 19: figure '0.000910' is neither declared-and-reproduced nor marked UNBACKED
  - line 19: figure '1.1364'   ...
  - line 19: figure '0.3854'   ...
  - line 27: figure '0.30'     ...
figure-ledger: 4 problem(s)   EXIT=1
```
Zero false positives after one tuning pass (paragraph-scoped marks, identifier exemption; v1 flagged 14 including "entry 1.1"). Three of the four are the *withdrawn-divergence* paragraph — the brief marks the **claim** WITHDRAWN and leaves its **replacement figures** unbacked and unmarked. The fourth, `0.30`, is the gate threshold: a specification constant, borderline.

**Targeted suite:** `7 failed, 126 passed`. All 7 are in `test_task_list_entry_count_2026-09-10.py`, all one cause: `EVERY REVISION OF THE FILE — 0 of them` — no `.git`. **fable's A2 class, independently reproduced.**

## migration

Nothing moves. All three fixes are additive fields and additive checkers over the file as it stands: two orphan markers hand-deleted (one commit, one person, five minutes), one `provenance:` token added per entry by `--apply` with hand correction, and the figure ledger applied to **new briefs only**. The 84 entries stay where they are. That is deliberate — a migration is the one operation that can lose an entry, and this list exists because things were being lost.

## cost

The figure ledger is ~150 lines and one subprocess run per declared figure. It makes writing slower by exactly one word per unbacked figure. It **makes convergence harder to declare**: its output is findings, so switching it on extends the discovery series and pushes the two-sided gate further from side (b) — the last three passes are `[4, 2, 1]` and this adds to the next one. That is the correct direction and I will not pretend it is free.

The declared-figure re-execution has a real ceiling: a 45-second script × N declarations serialises into the dispatch path. Cache by `(script, mtime)`; a rate-shaped figure that no script prints as a literal must be declared as the token the script actually emits, which is a discipline on the *script*, not the checker.

## refutation_condition

- **What figure discipline cannot fix:** a figure correctly produced by a script that measures the wrong object. Entry 2.1's `6,363` denominator is exactly this — the entry admits it is "not reproduced exactly under any of 15 readings". A script makes it reproducible and leaves it wrong. My checker verifies reproduction, not validity, and I claim nothing more.
- **What document architecture cannot fix:** a claim false at write time. fable is right about that and cc2's remedy does not touch it.
- **What would refute my priority:** run `figure_ledger.scan` over the 49 archived briefs. If it flags more than roughly one figure in ten as a false positive, authors will blanket-mark UNBACKED and the rule degrades into a no-op — worse than nothing, because it will read as discipline. I have measured precision on **one** brief. That is a sample of one and I am aware of it.
- **What would change my mind about cc2:** evidence that the 44 review entries are where the material defects live. Then the closure asymmetry is correct triage, not starvation, and the architecture split loses its urgency — but so does my ordering argument, because both remedies would then be aimed at the wrong queue.

## strongest_disagreement

**With fable:** naming `check_declared_figures` as the remedy. Executed, it passes this brief unchanged. The remedy is not that mechanism generalised, it is that mechanism *closed* — non-opt-in and token-exact. Recommending it as it stands would have shipped a guard that cannot fail in the direction it exists to check, which is this project's own named failure shape.

**With cc2:** the register collision is presented as needing a document rewrite. Two-thirds of its measurable damage is two orphan HTML comments and a ten-line function. Take the free part before proposing the migration.

**With this brief:**
1. "15 of 84 entries carry 2 or more in-place corrections" — my operationalisation gives **10 of 84, Wilson [6.60%, 20.54%]**. Marked UNBACKED and, on my measurement, overstated.
2. "entry 1.1 ... cites 5 distinct dates in one paragraph" — 5 distinct dates across the **whole entry**; the densest single paragraph carries **3**. Overstated in the direction that makes the problem look worse. Entry 1.1's **8 corrections: reproduced exactly.**
3. The brief presents `3.555346e-05` and then "an mpmath exact hypergeometric upper tail gives `2.001149e-05`" as though a third tool disagreed. They are the **two-sided and one-sided Fisher on the same table** and they agree exactly. Framing a one-sided tail as a discrepant cross-check is the stale-fact-as-current-fact class the brief's own threshold names.

## passes_run

**Four.** Each produced new above-threshold findings: (1) the three named scripts; (2) the figure mechanism — substring and opt-in holes; (3) task-list structure — orphan markers, correction counts; (4) provenance script, DONE-evidence coverage, targeted suite.

**I did not observe a zero-discovery pass.** I stopped on budget, not on convergence. Under §3 that is budget exhaustion carrying residual falsification debt, and the two-sided gate's side (b) is not satisfied by my run any more than by the series `[4, 2, 1]`. Reporting this as convergence would be the category-3 integrity violation, so I do not.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 25 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round6_2026-09-10) -->

All executed. Four passes run; pass 4 surfaced nothing new above threshold. Final report.

---

## verdict — build fable's half first, but hardened, then cc2's split second

The figure gate before the architecture split — with one non-negotiable amendment: **`check_declared_figures` as shipped fails its own motivating case and must not be generalised until repaired.** I demonstrated by execution that its substring match PASSES a declared figure of `0.29` against a true printed `0.294998` — the same class as V6's 0.451-vs-0.415413 band upgrade (`0.4` is a substring of `0.415413`; it would pass too). Generalising the mechanism before hardening it puts a guard that cannot fail in the load-bearing position.

Why this half first, from this round's own evidence: the one figure in this brief that was declared with a script (gamma 0.294998) reproduced exactly on my first run; the compound figure that wasn't ("15 of 84 entries carry 2+ corrections, 1.1 carries 8, 5 dates") reproduced only partially — **8 and 5 reproduce; 15 reproduces under no counting rule I could construct (3, 5, or 13 depending on rule)**. The dominant defect generator was live in the very brief instructing the panel about it, and only the declaration mechanism caught the difference. cc2's split is real, cheap, and I executed it — but it separates the inbox from the itinerary; it does not make a DONE claim true, and the 11-of-19 overstatement epidemic was inside the founder-itinerary entries.

## fix — per numbered problem

**1. Register collision.** Three registers, one precedence rule: the **marker** is the machine register and wins for state/status (`task_list_markers.py` unchanged); the **original statement** is immutable; **corrections become dated one-line entries in a `Corrections:` sub-block, each naming its producing script** — never inline rewrites of prior corrections, which is mechanically what produced 1.1's sentence-quoting-itself. On closure, narrative moves to `CDSFL_OUTCOMES_LOG.md`, leaving heading + marker + evidence. Measured migration workload: 11 entries carry correction tokens (13 under the broadest rule).

**2. Unbacked figures.** Extend `<!-- figure: label | script | value -->` to task-list entries; replace substring match with **whole-numeric-token match** and **per-script caching**. Executed v2: refuses `0.29`, refuses a stale `CONVERGED` verdict-word, still passes the exact figure; caching cut 5-figures-on-1-script from 0.7 s to 0.1 s (factor N for N figures). Scope: **new and touched entries in the two live registers only** (task list, operational plan). Retrospective application to the archive is rejected: 372 notes at top level, 2 files in the tree carry any declaration — retrofitting refuses everything for reasons unrelated to why it's validated, the validator's own documented rationale. Honest residual: a short indistinct token (`9`) passes even v2 because it is a genuine token somewhere in output; the rule must require ≥3 significant characters or a labelled `label = value` output line.

**3. Review exhaust.** Yes, out of this list — and I executed the migration: 40 itinerary + 44 backlog, **0 identifiers lost, 0 duplicated, both halves coherent (exit 0) under the shipped engine with zero code change** — `--path` already parameterises `check`, `summarise`, and the pulse. What stops loss: the pulse hook reads both files; the backlog keeps markers, so the V1 evidence guard and `unsupported_done_entries` still bind it. Demo limitation stated honestly: my splitter cuts at entry bounds, so section headings land in the wrong half; production migration must cut at `##` bounds — mechanical, and the coherence checks already prove the invariants to assert.

**4. 35 uncommitted files.** Rule: `status: COMMITTED|ENABLED` requires every evidence file to appear in `git ls-files` at HEAD. Checker written and executed in all three branches: gitless → **exit 3 "CANNOT VERIFY", never "clean"** (the round-5 environment-relative lesson, designed in); synthetic git repo with untracked evidence → REFUSE naming the entry; tracked/open → clean. Wire as a 7th pre-commit guard; its cost is ~0.1 s against the gate's measured 2.96 s median.

**5. DONE binds both, asymmetrically.** Code: the existing V1 evidence guard plus fix 4. Prose: a DONE entry's figures must be declared and reproduce (fix 2); undeclared narrative moves to the outcomes log at closure, so the queue never accumulates prose nothing checks. Plus one rule from my own pass 3: **evidence tests asserting configured-repository properties must declare it** — 2 of 22 currently don't, which is exactly why "22 of 22" was environment-relative.

## falsifier / falsifier_result

| executed | result |
|---|---|
| `scripts/task_list_markers.py --check` / `--summary` | 84 entries coherent; 57 open, 22 done, 2 blocked, 3 withdrawn |
| `scripts/ffafp_cycle_gamma_2026-09-10.py` | gamma **0.294998** (brief's declared figure reproduces exactly); (a) FAIL, (b) FAIL, KEEP GOING |
| `provenance_split_2026-09-10.py` (2 implementations each) | founder 40/19 DONE = 47.50% Wilson [32.94%, 62.50%]; review 44/3 = 6.82% [2.35%, 18.23%]; Fisher p = 3.555346e-05, OR 12.3651 — scipy == hand-rolled to 1e-12. **cc2's split CONFIRMED and now backed** |
| corrections census, 3 counting rules | 1.1 carries 8 (case-insensitive) ✓, 5 distinct dates ✓; "15 of 84" irreproducible (3/5/13) ✗ |
| `figure_gate_weakness_demo.py` | v1 PASSES wrong-substring `0.29`; v2 refuses; cache 0.7 s→0.1 s; bare `9` passes both (stated limit) |
| `split_migration_demo.py` | 40+44=84, 0 lost/duplicated, both halves exit 0, pulse works per file |
| `committed_means_tracked.py`, 3 branches | gitless exit 3 CANNOT VERIFY; untracked COMMITTED → REFUSE X2; clean otherwise |
| pytest over the 22 DONE-evidence files, in-sandbox | **8 FAILED, confined to 2 files** (`test_precommit_guard`, `test_task_list_entry_count`) — both assert git-configured state. **fable's 20-of-22 refutation REPRODUCED**, Wilson [72.19%, 97.47%] verified |
| targeted baseline `test_task_list_markers` + `test_panel_brief_format` | 37 passed |

## migration

40 entries → ITINERARY, 44 → REVIEW_BACKLOG (executed above, re-cut at section bounds for production); 22 DONE entries keep heading+marker+evidence, narrative appended to the outcomes log; 11 correction-bearing entries restructured into dated `Corrections:` sub-blocks; markers and engine untouched. The assistant does it, panel-checks it, roughly half a day. Gate impact (Section 2's question): none — my remedies move entries between files and add validation; they do not change what counts as an above-threshold finding, and the series JSON is untouched. The gate stays KEEP GOING.

## cost

Figure gate: one execution per distinct script per validation — a 45 s script costs 45 s, so it runs at commit time on touched entries, never in the per-turn pulse; it makes quoting a quick number harder, which is the point; verbatim-token matching refuses `47.5%` where the script prints `47.50%`, a deliberate false-refusal bias. Split: two files plus mirrors to keep in sync, and the engine's duplicate-ident check is per-file — a cross-file check is a required addition (~20 lines). Tracked-checker: reads exit 3 in every gitless sandbox — panels must treat that as loud-skip, not failure.

## refutation_condition

My build-first verdict is overturned if a committed-script census of the 116 failed surrounding claims shows a majority are **non-numeric prose claims** ("the guard is wired", "awaiting his passphrase") — the figure gate cannot see those, and priority flips to cc2's architecture plus V5-style freshness machinery. The failure mode my fix does not address: **a wrong instrument** — when claim and producing script share the same defect (6.2's hardcoded-operator class), re-execution corroborates the error; no figure gate catches that, only adversarial review does. Nor does either seat's remedy touch settled-rulings-never-written-back (R4–R9's class). What would move me to cc2's half first: git-history evidence (unavailable in this sandbox) that correction-on-correction accretion generates wrong figures at a higher rate than fresh claims do.

## strongest_disagreement

**With this brief:** it argues figure discipline while typing an irreproducible compound figure — "15 of 84" reproduces under no rule (3, 5, or 13); marking it UNBACKED does not discharge round 5's own standard, which was re-derive or reject. And "379 archived notes" is uncited; I count 372 top-level notes. **With fable:** right target, but generalising the shipped `check_declared_figures` without the token-match repair installs a guard demonstrably blind to its own motivating defect class. **With cc2:** "2 documents in 1 file" under-describes the disease — after my executed split, the overstatement epidemic (11 of 19 DONE) sits entirely in the founder-itinerary half. Architecture empties the inbox; it does not make DONE true. Both seats are half right; the founder should build the hardened figure gate this week and take the split as the cheap second step it demonstrably is.

## passes_run

**4.** Pass 1: baseline + reproduction of cc2's split and the corrections census. Pass 2: the three fix demos built and executed. Pass 3: self-falsification — evidence-suite rerun reproducing fable's 8 failures, synthetic-repo exercise of the git branch, limits of my own demos recorded. Pass 4: interval verification and archive-coverage count — no new above-threshold finding. Converged under §10: the residuals (bare-token limit, section-bound splitting, cross-file ident check) are named, below threshold, and carried in the fix text rather than left silent.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round6_2026-09-10/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
