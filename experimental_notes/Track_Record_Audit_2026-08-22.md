# Is the track record sound? An audit of what the archive can prove about itself

**22 August 2026, 01:20–02:00 BST. HEAD `30a5c1c` plus working tree.**
**Every figure below is offline, reproducible, and cost nothing.**
**Reproduce with `python3 scripts/track_record_audit.py`.**

---

## The question

CDSFL is an LLM-reliability research framework for STEM. Biological component
names are analogy only. Its founding principle is TOOLS DECIDE, NOT VOTES: a
finding is confirmed when the runner independently re-executes a model-supplied
falsifier and observes the designed failure, never by model agreement.

Over five days an assistant (CC1) audited the harness and found a series of
defects. Eleven of CC1's own claims were withdrawn in the same window. The
founder asked whether that record means the work to date is unreliable, and
required that if the answer is yes it be said plainly.

Two hypotheses were put to a five-model panel with equal weight and no compelled
convergence.

**H-BUILD.** The defects are the ordinary residue of a system still being built.
A component cannot be faulted for running imperfectly before it is finished.

**H-VOID.** Conclusions were drawn from components broken at the time and
presented with confidence disproportionate to their state.

---

## The claim that started this, and its refutation

On 21 August CC1 told the founder, and repeated on 22 August, that **"the
founding principle is currently unauditable on its own record."** The claim came
from a reviewer and was never checked against the archive.

It is **false for every run from exp42 onward**, and the check took forty minutes.
It is **true for exp34 to exp41**, for a reason that is a dated commit rather than
a failure. This is the twelfth withdrawn CC1 claim of the week, and the first
withdrawn in the favourable direction.

---

## M1 — the correction rate over the project's life

611 commits, 12 March to 22 August 2026. Commits whose message matches a
correction, withdrawal or retraction pattern:

| month | commits | corrections | rate |
|---|---|---|---|
| 2026-03 | 238 | 2 | 0.8% |
| 2026-04 | 207 | 11 | 5.3% |
| 2026-05 | 51 | 2 | 3.9% |
| 2026-06 | 40 | 5 | 12.5% |
| 2026-07 | 34 | 4 | 11.8% |
| 2026-08 | 41 | 10 | 24.4% |
| **total** | **611** | **34** | **5.6%** |

The rate is **rising**, which is the opposite of what a maturing build predicts.
It is confounded twice over: the work shifted from building to auditing, and
commit volume fell roughly six-fold. M1 on its own decides nothing. All five
panellists said so independently and three proposed the same discriminating
measurement, recorded under "What is still not known" below.

## M2 — does the archive reproduce itself?

`scripts/replay_accounting.py --verify` replays each archived run's
location-keyed critical series from the stored registry and compares it against
the series recorded at run time.

**8 of 8 runs reproduce exactly** (exp42 through exp49). The replay is a valid
instrument and the archive is internally consistent.

## M3 — how much of the archive can show what decided it?

**2,030** registry entries across **27 distinct runs** (45 report files, of which
`exp36_evidence_latest` is a byte-equivalent duplicate of
`exp36_evidence_20260407T004931Z`, 217 entries each). **1,442** are in a terminal
status. Of those, **454 (31.5%)** carry a recorded `falsifier_verdict` — the
runner's own re-execution result — and 988 (68.5%) do not.

**CORRECTION.** An earlier draft of this note, and the brief the panel was given,
reported 2,247 entries / 1,652 terminal / 27.5% backed. Those figures counted the
duplicate directory. CC2 caught it by reproducing the measurement. The error ran
against the project's own interest, which is the right direction for an error to
run, but the two figures disagreed inside one measurement and that is a defect.

**That aggregate is a mixture of two eras and reporting it as one number is
misleading.**

| era | runs | entries | with falsifier code | terminal | backed by a tool verdict |
|---|---|---|---|---|---|
| exp42 onward, from 2026-06 | 13 | 586 | 477 (81.4%) | 536 | **458 (85.4%)** |
| exp34–41, to 2026-05 | 16 | 1464 | 0 (0.0%) | 910 | **0 (0.0%)** |

Modern era by status: CLOSED **419/430 = 97.4%**; REFUTED 14/18 = 77.8%;
CONFIRMED 23/75 = 30.7%; MERGED 2/13 = 15.4%.

Refreshed from `scripts/track_record_audit.py` on 2026-09-01. The table had read
11 runs / 566 entries / 465 since 22 August while the script named in this
document's own reproduce line reported 13 / 586 / 477 — two further runs had
landed and nothing compared the document to the script. A parametrised test now
does: `bench/tests/test_derived_docs_match_their_generators_2026-09-01.py`.

## M4 — why the legacy era is empty

`git log -S'falsifier_verdict'` first hits **2026-06-03**, commit **`4fba6cc`**,
message: *"Falsifier gate: runner-decided verdicts replace the CONFIRM/CHALLENGE
vote (gated, default-off)."*

Every 0.0%-backed run predates that commit. `falsifier_gate_enabled` was then
checked in the configuration files themselves rather than read from the code
default — a distinction that produced a wrong claim earlier this week. It is
`<unset>` in all eight exp40/exp41 configs and **`True` in all seventeen configs
from exp42 onward**, including the unrun exp50, exp51, exp52 and exp53.

**The era boundary is the arrival of the mechanism, not a change in behaviour.**
That is the founder's engine analogy, and it is a dated commit rather than a
rationalisation.

## M5 — does the recorded status track the recorded tool verdict?

474 modern entries carry a tool verdict.

| tool verdict | CLOSED | CONFIRMED | MERGED | REFUTED | UNCONFIRMED | total |
|---|---|---|---|---|---|---|
| CONFIRMED | 417 | 19 | 1 | 0 | 0 | 437 |
| ERROR | 2 | 0 | 0 | 2 | 11 | 15 |
| REFUTED | 0 | 0 | 1 | 12 | 0 | 13 |
| UNTOOLABLE | 0 | 0 | 0 | 0 | 9 | 9 |

Tool said CONFIRMED, status became CLOSED or CONFIRMED: **436/437 = 99.8%**.
Tool said REFUTED, status became REFUTED: **12/13 = 92.3%**.
Tool said UNTOOLABLE, status became UNCONFIRMED: **9/9 = 100%**.

## M6 — when the tool verdict and the model majority disagree, which prevails?

227 modern entries carry both. 201 agree. 26 disagree.

- **the tool verdict prevails: 25**
- **the model majority prevails: 0**
- neither: 1

### There is no p-value here, and there must not be

An earlier draft reported a sign test: 25 of 25, p = 2.98e-08, later corrected to
25 of 26, p = 4.02e-07 after DeepSeek objected that excluding the ambiguous case
flatters the result. **Both are withdrawn.** CC2's objection supersedes DeepSeek's
and destroys the statistic outright:

> `apply_falsifier_verdicts` is called after `_update_finding_statuses` and
> unconditionally overwrites status from the tool verdict; the docstring says so
> in as many words. Given the gate on, "the tool prevails" is **deterministic**. A
> sign test against a vote-decided null tests a hypothesis the source code already
> assigns probability zero.

This is correct and it is worth dwelling on, because the same fact appears twice
in this note pulling in opposite directions. The votes-then-tool ordering was cited
below as the refutation of the panel's tautology objection — and it is. It is also
the reason the p-value is meaningless. **The evidence used to defend M6 is the
evidence that guts it, and CC1 reported the first without noticing the second.**

What the table legitimately establishes is narrower and still worth having: **a
regression check.** The gate was enabled and nothing bypassed it across every
modern run. Given that six model-vote paths to MERGED were found in this codebase
on 19 August, a check that the equivalent path is clean for CONFIRMED and REFUTED
is genuinely valuable. It is a bug check, not a significance test.

### The 26 disagreements are not 26 equivalent contests

CC2 decomposed them and the decomposition reproduces exactly. As a strict
partition:

| n | what it is | what it supports |
|---|---|---|
| 18 | the tool ERRORED or was UNTOOLABLE and the runner withheld | model agreement is **not sufficient**. Sound. |
| 6 | MERGE / REOPEN / EXTEND majorities against a CONFIRMED tool | **nothing.** MERGE means "duplicate of C00xx" — a housekeeping vote, not a truth vote. Counting it as "the model wanted a different truth" is CC1's construction and is not defensible. |
| 2 | a model majority making a truth claim against a tool truth verdict | this alone. |

The two survivors are `exp42_composer_locationkey_live` C0028 (tool REFUTED,
majority CONFIRM, ended REFUTED) and `exp44_evidence_locationkey_live` C0025 (tool
CONFIRMED, majority CHALLENGE, ended CLOSED).

**So "the tool overrules the panel on truth" rests on n = 2.** "Model agreement is
not sufficient" rests on 18 and holds. The seven-champions table below is the
housekeeping bucket and should be read as bookkeeping, not adjudication.

**Assumption-free restatement, requiring no mapping of intent:** of 16 findings
where the model majority voted CONFIRM and the falsifier ERRORED or was
UNTOOLABLE, the number that reached CONFIRMED or CLOSED is **zero**
(binomial p = 3.05e-05 against a vote-decided null).

### The panel's objections to M6, and what measurement says about each

**"It only shows the tool as a veto, never as a champion. Show a case where the
models wanted to kill a finding and the tool saved it."** (Gemini)

Measured: **7 such cases.** In four the model majority voted MERGE, in one
CHALLENGE, in two REOPEN; the tool said CONFIRMED; all seven ended CLOSED.

**But read them with CC2's decomposition above.** Six of the seven are the
housekeeping bucket: MERGE means "duplicate of C00xx" and REOPEN means "look
again", neither of which is a claim that the defect is not real. Only the CHALLENGE
case (`exp44_evidence` C0025) is a truth claim. So the honest answer to Gemini is
that the tool acts as a champion **once** on truth, and six further times on
bookkeeping. Gemini's objection is narrowed rather than refuted, and it was right
to make it.

| run | id | model majority | tool | final status |
|---|---|---|---|---|
| exp42_composer | C0003 | MERGE | CONFIRMED | CLOSED |
| exp42_composer | C0065 | MERGE | CONFIRMED | CLOSED |
| exp44_evidence | C0025 | CHALLENGE | CONFIRMED | CLOSED |
| exp45_memory | C0002 | MERGE | CONFIRMED | CLOSED |
| exp45_memory | C0006 | MERGE | CONFIRMED | CLOSED |
| exp47_divergence | C0038 | REOPEN | CONFIRMED | CLOSED |
| exp47_divergence | C0043 | REOPEN | CONFIRMED | CLOSED |

Counting only truth contests, the tool acts in both directions **twice**: once
declining a confirmation the panel wanted, once sustaining a finding the panel
challenged. Counting tool failures where the runner withheld, it declines a
panel-wanted confirmation **18** times.

**"Selection bias — M6 covers 227 of 566 modern entries. What happened to the
rest?"** (Gemini, ChatGPT, Codex, DeepSeek)

Measured: 247 entries carry a tool verdict and **no model votes at all**; 72 carry
votes and no tool verdict; 20 carry neither. The 247 cannot host a tool-versus-vote
contest, so they are not a withheld sample — they are an empty contest, and they
are 43.6% of the modern arc decided by the tool with no vote in play. The 72 are
a genuine residual and M6 says nothing about them.

**"Tautology — if the same code writes the tool verdict and the status, M6
measures the mapping, not a contest."** (Codex, ChatGPT)
**"Causal order is unrecorded — if votes were cast after seeing the tool output,
'tool prevails' is observationally equivalent to 'tool formalises the
majority'."** (DeepSeek)

This is the strongest objection and it is settled by reading the runner rather
than the data. In `reference_runner_v2.py` the order is explicit:

```
:9122   _update_finding_statuses(registry, round_idx, cfg=cfg)      # votes write the status
:9127   _ingest_corrected_copies(...)
:9131   apply_falsifier_verdicts(registry, round_idx, ...)          # the tool overrides it
```

and `apply_falsifier_verdicts` documents itself as *"Called AFTER
`_update_finding_statuses` so the falsifier verdict wins."* The vote-derived status
is written first and is then overridden. It is not a mapping and the order is not
inferred — it is the sequence of two calls nine lines apart.

The residual weakness is real and should be stated: this is **code-level
provenance, not per-entry provenance.** It shows the path every entry took; it
does not stamp each entry with the event that decided it. That is the gap the
typed transition log would close.

## M7 — a defect found while taking these measurements

24 modern entries have a falsifier verdict of ERROR or UNTOOLABLE. Four carry a
terminal status anyway:

| run | id | tool | status | severity | `verified` |
|---|---|---|---|---|---|
| exp42_composer | C0046 | ERROR | CLOSED | 0.85 | True |
| exp47_divergence | C0055 | ERROR | CLOSED | 0.62 | True |
| exp46_stage6 | C0014 | ERROR | REFUTED | 0.35 | False |
| exp48_chemistry | C0037 | ERROR | REFUTED | 0.45 | False |

The two CLOSED cases carry `verified=True` and have an independent
fix-verification behind them; they are defensible. The two REFUTED cases carry
`verified=False`: a falsifier that did not run wrote REFUTED.

**CORRECTION (CC2).** All four carry `escalated=True` — verified. A human saw each
of them at the moment it was mislabelled. The status is still wrong and the fix is
still cheap, but "killing a finding on no evidence" overstates it and is
withdrawn.

## M8 — a measurement attempted tonight and withdrawn

A gamma-stability check was attempted: recompute each run's final gamma from the
replayed series and compare against the archived `gamma_critical_history`. It
reported all 8 runs "MOVED" and the result is **withdrawn**. The two quantities
are not the same series — `gamma_critical_history` is built round by round from
the settled novelty counts, and `location_crit_shadow_history` is a shadow
location-keyed series. Comparing the gamma of one against the gamma of the other
compares different things.

This is the thirteenth withdrawal of the week and it occurred inside the analysis
of withdrawals, under the same failure shape as the other twelve: **a universal
asserted after one comparison, without checking that the two things compared were
the same thing.** It is recorded here rather than deleted because the rate of this
error is part of what the founder asked about.

The valid form of that check exists in the runway record (item 1.1: the runner's
own settled series reproduces the archived `gamma_critical_history` exactly in 9
of 11 archived runs) and was not re-derived tonight.

---

## M10 — the finding that outranks all of the above

**CC2 ran the gate directly rather than reasoning about it. Reproduced here:**

```
reverify_falsifier("assert False, 'FALSIFIED: trivially'")               -> CONFIRMED
reverify_falsifier("assert 3*6+8*2 == 3*4+8*2, 'FALSIFIED: unbalanced'") -> CONFIRMED
reverify_falsifier("print('FALSIFIED')")                                 -> CONFIRMED
reverify_falsifier("print('nothing happened')")                          -> REFUTED
```

**The gate measures that a falsifier fired. It does not, and cannot, measure that
it fired because of the claim.** A falsifier that asserts `False` unconditionally
is recorded as an independent tool confirmation, indistinguishable in the archive
from one that genuinely demonstrates a defect.

And **0 of 2,030 archived entries carry a `discrimination` record.** The
discrimination control has never run, once, in the project's life.
`discrimination_control_ask = False` at `reference_runner_v2.py:593`.

This does not mean the archived confirmations are false. It means **nothing in the
archive distinguishes a true confirmation from an empty one**, and that is a
different and more serious statement than anything in M3 through M7. It applies
to the modern arc as much as to the legacy era.

## M11 — exp48 and exp49 must come out of the headline

Three independent reasons, all verified tonight:

1. **Answer-key contamination**, already recorded in the project's own errata: CC2
   held the seeded set from round 1 and the retraction stands.
2. **Both target documents are deleted.** `/Users/georgejackson/CDSFL_review_targets/exp48_chemistry.md`
   and `exp49_engineering.md` are absent. **68 falsifiers cannot be re-executed at
   all**, so neither the discrimination control nor any replay can reach them.
3. **Every detached falsifier in the archive lives here.** Counting CONFIRMED
   falsifiers whose code never imports, opens or reads anything: 9 by the
   heuristic used here, 15 by CC2's broader one — and **100% of them are in exp48
   or exp49** on both counts. These are pure model-authored arithmetic, for
   example `assert left_H == right_H` with the coefficients transcribed by hand.
   If the transcription is wrong the confirmation is empty and nothing in the loop
   can see it. All are status CLOSED.

M3's 85.3% currently includes them.

---

## The verdict

**Neither hypothesis. All five panellists reached a split independently. None
chose pure H-BUILD; none chose pure H-VOID.** Four returned a dated two-way split.
CC2, which reproduced the measurements with tools rather than accepting them,
returned a three-way split and argued that the fault line is the claim being made,
not only the date. Its version is the one adopted below, because it survives the
evidence the other four did not have.

**Before 3 June 2026 — exp34 to exp41, 910 terminal entries.** The archive cannot
show these were tool-decided, because the mechanism did not exist. They are not
thereby false. They are **unaudited for the founding principle** and must not be
cited as tool-decided results. Codex's phrasing is the one to adopt: *unaudited
legacy results.*

**From 3 June 2026 on code targets — exp42 to exp47, 9 runs.** The record is
substantially self-auditing: 85.3% backed, 97.4% of closures backed, status
tracking the tool verdict at 99.8%, every archived series reproducing exactly, and
the gate demonstrably enabled and unbypassed. These stand as *a tool fired against
the real artefact, and the runner rather than the panel read the result.* They do
**not** stand as *the tool discriminated the claim* — M10 says nothing in the
archive can distinguish those.

**exp48 and exp49 — exclude from headline claims**, for the three reasons in M11.

The over-claim in the record is therefore not "we found defects", which is well
supported. It is **"our findings are tool-decided"**, which is supported for *the
falsifier firing* and unsupported for *the falsifier firing because of the claim*
— everywhere, including the modern arc.

**The founder's engine analogy holds, and the data locates exactly where it
holds.** It is not a rationalisation, because the boundary is a commit hash with a
date on it and a configuration flag that is unset before it and set after it. What
the analogy does not license is citing pre-June results as demonstrations of the
principle. They were produced before the part that demonstrates it existed.

---

## What is still not known, and it is the important part

Every panellist, in different words, made the same point: **none of the above
tests whether the falsifiers are any good.**

M5, M6 and M9 all measure whether the harness obeyed the tool. They are silent on
whether the tool was right. DeepSeek put the failure mode most sharply: *"A
falsifier that always fires would produce the observed CONFIRMED/CLOSED pattern
and pass M9."* Gemini reached the same place from the other direction: *"If your
falsifiers cannot recognise a repair, your 85.3% tool-backed modern archive is
backed by noise."*

The null-perturbation control run on 21 August closed one half of that: change
something the finding does not accuse, and 0 of 360 falsifiers moved. The other
half has never been run: **repair the accused claim, and the falsifier must go
quiet.**

---

## The next step

**Run the complementary discrimination control on the archive, offline.**

**Four of the five panellists named it, from four different arguments.** Codex
alone preferred the typed transition log, and its reasoning is recorded in the
panel file rather than smoothed away. CC2's ranking argument is the sharpest:
a log records *which mechanism decided*; if the mechanism does not discriminate,
the log faithfully records a worthless decision. The log is logically posterior.

It was thought to need a live run, because the in-runner control
(`_apply_discrimination_control`) is presence-gated on a corrected copy that no
panel has ever been asked for. **It does not.** Measured tonight:

- 437 modern findings have a falsifier that fired
- 437 of those carry the falsifier code
- **369 also carry a proposed fix, and 367 of those are in machine-applyable
  SEARCH/REPLACE form**

So the control can be run against these findings with no dispatch and no metered
cost: apply the finding's own fix to a scratch copy of the target, re-run the
finding's own falsifier, and require it to go quiet. The machinery to apply a
SEARCH/REPLACE fix and re-run a falsifier already exists in
`scripts/adjudicate_by_repair.py`, measured at 0.287 s per pair. CC2 counts 313 of
372 code-target CONFIRMED entries (84%) carrying a non-empty `proposed_fix`; the
count here is 367 of 437 across all modern runs, and the difference is exp48/49,
which M11 excludes and whose targets are in any case deleted.

**CC2 offers a second route, cheaper and free of the assumption that a proposed
fix is a correct fix:** most of these defects were subsequently repaired in the
repository. Re-run each archived falsifier against the commit that fixed the
defect it accuses. If it still fires, it was never testing that claim. This uses
only git history and the archive and needs no fix application at all. **Run both:
they fail in different ways and agreement between them is itself evidence.**

**Pre-registered decision rule, taken from CC2 before the measurement is made, so
it cannot be chosen after seeing the answer:** 95% or more go quiet on a corrected
copy, and the modern arc moves to H-BUILD without reservation. 10% or more still
fire, and it moves materially toward H-VOID.

A falsifier that still fires after its own accused defect is repaired is not
testing that defect. If a material fraction behave that way, M5 and M6 show only
that the harness obeyed bad tools, and the modern arc drops toward H-VOID. If they
go quiet, the modern archive is evidenced from both sides and the remaining work is
provenance and the live runs.

**Ranked below it, and not started:**

1. Wire counterfactual repair to the merge site. Verified tonight: **no code path
   in `reference_runner_v2.py`, `immune_agents.py` or `bench/dm/` writes MERGED at
   all** — the only MERGED writers left are the frozen exp33–37 runners. Five sites
   now record `merge_candidate_of` and `merge_blocked_reason` instead. Any live run
   started today would produce zero merges. `target_path` is a local in
   `run_experiment` (assigned `:8225`–`:8231`) and the `_update_finding_statuses`
   call is at `:9122` in the same function, so this is one argument.
2. The typed transition log, recording the deciding mechanism per status change,
   with a test forbidding a model attestation from writing CONFIRMED, CLOSED or
   MERGED. This converts M6's code-level provenance into per-entry provenance.
3. Fix M7: a falsifier verdict of ERROR or UNTOOLABLE must not be able to write a
   terminal status.
4. The M1 confound. Three panellists proposed measuring corrections against the
   **age of the code being corrected** via `git blame`. CC2's version is better and
   is the one to build: **bucket each correction by the month the claim was
   ASSERTED, not the month it was withdrawn.** Rate-by-withdrawal-month rises
   mechanically whenever anyone audits — it is a property of the auditing, not of
   the work. Rate-by-assertion-month asks the question that matters: of the claims
   made in March, how many turned out wrong? Pair it with survival to handle
   right-censoring — report each cohort at 30, 60 and 90 days and compare August's
   30-day figure against March's 30-day figure, never against March's lifetime
   figure. Denominate by claims made, not by commits; commit count measures typing.

5. Make `scripts/null_perturbation_control.py` safe to invoke read-only. It writes
   its output file unconditionally, and on 22 August a read-only reviewer running
   it with `--limit 12` overwrote the committed 397-row result with a 12-row one.
   The reviewer disclosed it immediately and the file was restored from git. It
   should take `--dry-run` or write to a timestamped path.

---

## Sources consulted for this note

`bench/logs/*/*_report.json` (27 archived registries); `git log` over 611 commits;
`bench/reference_runner_v2.py` at `:2936`, `:9122`, `:9131`, `:8225`;
`bench/exp4*_configs/`, `bench/exp5*_configs/`; `scripts/replay_accounting.py`;
`experimental_notes/RUNWAY_to_BR2_2026-08-18.md`;
`experimental_notes/CDSFL_Agent_Operational_Plan.md`;
`bench/falsifier_verify.reverify_falsifier` (executed directly);
`/Users/georgejackson/CDSFL_review_targets/`;
`bench/logs/track_record_pr_2026-08-22/` (the panel, 5 of 5 returned).

Full verbatim panel record: `Panel_Track_Record_FULL_RECORD_2026-08-22.md`.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).
