# Overnight progress, 29 October 2026

Covering roughly 01:30 to 03:10. Written for a reader who was not present: every file path, figure and interval is kept, and each term is glossed where it first appears.

## The list now provably terminates — the one thing you asked to be told about

On 2026-10-28 `bench/tests/test_task_list_burndown_2026-09-11.py` failed with **R = 0.835714** and a 95% interval of **[0.6602, 1.0694]**, and its own message said *"The upper bound has reached 1: the list can no longer be said to terminate, and the founder asked to be told if that happened."*

**It has flipped.** With tonight's 12 closures committed — the branching ratio is computed from git history, so it could not move until the commit landed:

| | 2026-10-28 | after this commit |
|---|---|---|
| R, new entries per entry closed | 0.835714 | **0.782051** |
| 95% interval on R | [0.6602, **1.0694**] | [0.617445, **0.990540**] |
| Subcritical, i.e. terminates | **False** | **True** |

The underlying proportion is **122 additions against 156 closures, 122 of 278 = 0.438849**, Wilson **[0.381741, 0.497624]** with statsmodels and an independent NumPy closed form agreeing to all printed digits. R < 1 is equivalent to p < 0.5, and the Wilson **upper** bound is 0.497624, below 0.5. One-sided exact binomial against 0.5: **p = 2.379866e-02**.

`bench/tests/test_task_list_burndown_2026-09-11.py` returns **15 passed**, green for the first time.

**The honest limits, which the producer states itself.** R is partly a policy variable, because what becomes an entry is my decision and a lower bar would raise it. The remaining entries may not be like the closed ones. And the figure describes this body of work: opening a genuinely new area could restart discovery fast enough to push R back above 1, and this window says nothing about that.

## Read this first — and a correction to an earlier version of this note

An earlier version of this note, sent roughly 30 minutes before this one, described the `wr` ("work remaining") ticket kind as a **parked and invisible backlog** that the Stop gate does not hold the session open for. **That was wrong on 2 of its 3 claims.**

### Withdrawn (1): "the Stop gate does not hold the session open for these"

**False, and executing the predicate rather than reading it is what showed so.** `hooks/ticket_queue_gate.py:183` reads:

```python
prodding = [t for t in workable if t.kind != "wr"] or workable
```

A `wr` ticket **is** in `workable`, so it keeps the gate refusing at exit 2. Executed on synthetic sets:

| workable | prodding |
|---|---|
| `['pf','wr','wr']` | `['pf']` |
| `['wr','wr']` | **`['wr','wr']`** |
| `['qs','wr']` | `['qs']` |

So these items are counted, listed, and keep the session open, and when nothing else is workable the `or workable` fallback makes them prod. Only their being **named** as NEXT OPEN is suppressed, and the file says why: *"surfacing it as the next thing needing resolution is exactly how R1 was put back to him for 66 days. It is still COUNTED and still listed, so it cannot be lost — it simply does not prod."*

### Withdrawn (2): "it was built without his confirmation"

**Too strong.** The figure of 1 annotation was right; the conclusion was not. `hooks/ticket_queue_gate.py:144-148` attributes an instruction to him dated 2026-10-20: *"wr is a valid section in the Bugzilla registry, and you should use it to track all remaining outstanding work, and refer back to this before risking constantly referring back to me and requesting my verdict."*

That sentence is **not** in his annotation record — a corrected token-boundary search, `(?<![A-Za-z])wr(?![A-Za-z])`, still returns 1 — so it most likely came from **chat**, which `scripts/read_founder_responses_2026-10-11.py` does not cover, exactly as the `qs` directive records of the bounded-orchestrator question. **So I cannot establish that he did not confirm it**, and asserting that he had not was the error. "Not found in the annotations" is a different claim from "he did not say it".

**My first search was also defective** — it required `" wr "` with spaces on both sides, so it could never have matched *"wr is a valid section"*. The instrument was the weak point before the data was, which is this project's most-repeated lesson.

### What survives: a backlog, not a defect

**26 of the 36 live `wr` records are instructions or questions of his rather than deferred work** — 0.722222, Wilson [0.560075, 0.841517], binomial p = 1.133098e-02. If his quoted instruction is genuine then that is *precisely* what he asked for, and the classification is correct.

What is true either way is that **26 instructions of his are outstanding and unworked**, among them *"Then do the work please, and check your work with the free panel"*, *"Fix the convergence gate so it becomes the 2-part test, as envisaged"* and *"Update officially to CDSFL note standard v1.8"*. That is **work owed**, not a mechanism to repair.

**The one ruling still worth his word:** whether he is content for those 26 to be worked from the `wr` list in his stated order — after the master task list — or wants any promoted now.

## Summary

6 task entries closed — **C12, B29, B31, B33, C15, B39** — taking the master task list from 21 open entries to **17**. 1 entry (**B47**) and 2 register questions were deliberately added, which is why the fall is 4 rather than 6: an owed decision that is not recorded is an owed decision that gets lost.

4 things need the founder's decision, listed in the final section.

## C12 — the quiet run, and the panel answering the entry's own doubt

His ruling of 2026-10-08 was *"Verdict. Fix it and check your fix with the free panel."* The fix half was already complete (`REQUIRED_QUIET_RUN = 3` at `bench/reference_runner_v3.py:1560`). The panel half ran on 2026-10-28 in both a blind and a joint round, and it answered the entry's doubt rather than endorsing its premise.

The doubt was whether a longer run of quiet rounds is the right lever at all. **It is not.**

| Finding | Figure |
|---|---|
| Local quiet (`novel_this_round`) at the firing point | AUC **0.3097**, CI **[0.1067, 0.5126]** — spans 0.5, so blind |
| Raw `findings_count` at the firing point | AUC **0.9058**, CI **[0.7494, 1.0000]** — discriminates |
| Occurrences of 7 consecutive quiet rounds | **0** across 409 rounds and 63 reports |
| False-quiet rate at a required run of 3 | **8 of 30 = 0.266667**, Wilson [0.1418, 0.4445] |
| Residual once the 0.41 gamma arm is applied | **4 of 30 = 0.1333**, Wilson [0.0531, 0.2968] (the seat reported [0.0533, 0.2966]; recomputed 2026-10-29 and all 3 of statsmodels, NumPy and mpmath give [0.053097, 0.296813], so the seat's interval was slightly off and mine repeated it) |

The first seat's words: *"I tried to show 3 re-opens false quiet. It does not, because quiet is not the signal."* The other's: *"7 is a gate nothing reaches, which the project's own additive standard names as not additive."*

**The joint round then undercut the curve the entry rests on.** The `premature` label is a disjunction over the rounds *after* a firing point, and `any([])` is `False` — so a firing point with nothing recorded after it was labelled sound with no evidence. It is *unobserved*, not sound. Of 30 firing points, **10 have an empty tail** and 10 more a tail of 1; not one of the 8 premature labels comes from a tail shorter than 2. **Tail length alone predicts the label at AUC 0.971591**, CI [0.888203, 1.0]. A `--min-tail` option now lets a caller drop such labels, defaulting to 0 so every published figure reproduces byte for byte.

## A 7-hour silent hang

A background process started around 19:20 on 2026-10-28 was found still alive at 02:30 on 2026-10-29: **7 h 20 m elapsed against 0.01 s of CPU**. It was writing a session-state block into `resources/RECOVERY.md`. The command used an *unquoted* shell heredoc, so the shell evaluated the backticked branch name inside the prose as a command substitution; that failed, the heredoc was left malformed, and `python3 -` blocked on stdin indefinitely.

`resources/RECOVERY.md` is current — the block was written later by another route, 2 commits behind HEAD against a ceiling of 60 — so no state was damaged. The entire cost was the silence.

This was the 4th instance of a known fault with the same cause but the **1st with this consequence**, and it is the worst of the 3, because it is the only kind that never reports itself: a background task that never exits never notifies, and "still running" is indistinguishable from "making progress" in every status display. The rule recorded: confirm a background heredoc **exited** rather than that it started (`ps -o etime=,time=` separates a blocked read from real work, because real work accumulates CPU and a blocked read does not), and prefer `python3 scriptfile` over `python3 -`, because a file cannot be truncated by the shell mid-stream.

## A guard accusing correct code

2 consistency checks on the ticket register were failing, both naming 1 record: a question owed to the founder, filed against task C1. **The record was correct.** The guard was written on 2026-10-17; the `qs` (question) kind entered the register on 2026-10-19, 2 days later. Because `tid_of` makes a task reference the whole identity *alongside the kind*, and the task-list harvester emits only `fr` and `pf`, the guard was structurally incapable of accepting any question carrying a task reference. It was accusing the newer kind of failing to be the older kind.

The fix widens the acceptable identity set to every kind, and keys it **per reference** rather than as one flat pool. The second half is a genuine strengthening: a flat pool would admit a record claiming reference C1 while sitting at the identity belonging to C2. 2 mutations were run and both turned red.

That fix is already load-bearing: the question raised against B39 later the same night sits at a canonical identity only because of it, and the register now reports **0 live records at a non-canonical identity**.

## B29 — the save mechanism, and a question that had been parked behind nothing

His ruling of 2026-10-19: *"Verdict: Option 3. Dut do Options 3 and 1 compose, if an event occurs where a save operation does not complete cleanly?"* (*Dut* is *But*.)

**Option 3 is built.** `_check_recovery_currency` is now the 5th check in the pre-flight of `sv`, the save command, so the currency of `resources/RECOVERY.md` is tested *before* the commit rather than only after it.

**The margin is what makes this more than moving the old check earlier.** Pre-commit, HEAD is 1 commit behind where it will be when the post-condition runs, so a block sitting at exactly the ceiling of 60 would pass before and fail after — the original defect displaced by 1 commit rather than repaired. The predicate is therefore `behind + 1 <= 60`. It borrows the existing guard's own parser and ceiling by path rather than keeping a second copy of either, because a producer and a consumer that each describe themselves correctly and disagree with each other is the failure mode `execute-do-not-grep` names.

Measured cost **0.1690 s cold, 0.0793 s warm**, against the 0.3333 s he budgeted.

**His composition question is answered: yes, and neither option is redundant.**

| | Count | Share |
|---|---|---|
| Follow-up saves within 15 min, after the check existed | 14 of 89 pairs | 15.7303%, Wilson [9.6078%, 24.6888%] |
| Of those 14, naming the condition Option 3 pre-checks | **7** | 0.500000, Wilson [0.267992, 0.732008] |
| Of those 14, which Option 3 cannot see | **7** | 0.500000, Clopper-Pearson [0.230361, 0.769639] |

The falsifier was stated before the count: redundancy requires **0** in the not-prevented column, and that column's 95% lower bound is **0.2680**, so redundancy is excluded. The clearest residual case is commit `eb4bd2ca`, *"sv: the ONBOARDING milestone entry the script does not write"* — a second save forced by a different post-condition, which no staleness pre-check can see.

Producer: `scripts/do_options_three_and_one_compose_2026-10-29.py`. It imports the parent producer's pair logic so the denominators agree exactly, and prints all 14 classifications so they can be checked rather than trusted. **Its limit, stated:** a commit subject is what a save *says* about itself, not an observation of which gate fired, because git does not record the gate. The figures bound exposure and classify intent; they do not count realised refusals.

### Two false citations withdrawn

B29 claimed his composition question was *"answered in the session note of 2026-10-20"*. **No such note exists.** Of 21 tracked files carrying that date, exactly 1 is a session note, concerning an unrelated capability comparison, and **0 of the 21 mention B29**.

The identical sentence appears in **B39**, deflecting a different composition question of his. So this was a pattern, not a slip: 2 of his questions had been parked behind 1 citation to a document that does not exist. Both are now removed.

2 stale figures in B29 were also corrected: the follow-up rate is **14 of 89 (15.7303%)**, not 14 of 83 — the denominator grew as saves landed — and the claim that 8 of 14 subjects name the session-state and producer-citation condition was wrong; a classifier and an independent hand count both give **7**.

## B31 — the credential redactor withholding an ordinary setting

Approved twice, on 2026-10-18 and again on 2026-10-19 with an objection to being asked a second time.

Scope measured before changing anything: of `RunnerConfig`'s **100** fields, exactly **1** collides with the credential pattern and it is not a secret — `location_keyed_convergence`, caught because the substring `key` appears in `keyed`. So the redactor's precision on this configuration was **0 true positives against 1 false positive** (0.010000, Wilson [0.001767, 0.054486]). The archived count had grown from 4 of 4 reports to **5 of 5**, so the fault was accruing.

The rule was first **extracted** out of a 582-line function into `redacted_declared_config`, because while it sat inline the only possible check was a scan of source text. An exemption set then matches field names **exactly, never as substrings**, so a future field named `location_keyed_convergence_api_key` stays withheld. The pattern list is untouched, so nothing protected before is unprotected now.

## B33 — a declared mode with no effect path

His ruling of 2026-10-19 was *"Verdict option 1"*, choosing to wire the mode over retiring it or renaming its report field.

The mode had **4 artefacts and 0 effect path**: a config field, a slot in `mode_effects`, a published series, and a report field whose name asserts that it gates. Nothing in the runner ever wrote to its slot, so it could not operate however it was set. It now substitutes its series into the critical-novelty series the convergence gate reads, and records the rounds in which it substituted at the point of substitution.

2 design points were settled by reading the surrounding contract rather than assuming:

- **The report field that restates the flag is deliberately unchanged.** The design keeps the *declared* value and the *observed* effect apart so the 2 can be reconciled; collapsing them would destroy the comparison. The defect was that the observed side was permanently empty, not that the declared side restated the flag.
- **When both this mode and its sibling are declared, the sibling stands down** rather than being overwritten, because this mode *refines* the sibling's rule. Overwriting would have left the sibling recording a substitution that did not survive the round — a false record of effect inside `mode_effects`, the record built to hold effects truthfully.

Replacing the circular detector with a detector that reads the effect immediately surfaced a **true historical disagreement** the old detector could not express: 1 archived run declared the mode while it had no effect path (1 of 5, Wilson [0.036224, 0.624465]). That run is not edited — history is not rewritten here — but recorded as a named exemption keyed on its own directory, which makes the exemption self-bounding so any recurrence in a future run fails.

## C15 — the ranking number

His ruling of 2026-10-09 was that models should be distinguished only by a ranking number derived from demonstrable capability, measured at the start of an experiment (1 round constituting a season) and then held fixed.

**This is built.** `season_strength_order` is defined at `bench/routing.py:543` and genuinely called from the live dispatch path at `bench/reference_runner_v3.py:8657-8661`, where it freezes and logs whether the order in force was MEASURED or DEFAULTED.

The vendor-ordered fallback remains, and the measured reason matters: **the ladder order is not estimable from the archive.** Heterogeneity between seats is established (chi-square 14.5802, 4 dof, p = 0.005656) but **0 of 10** pairwise comparisons survive correction for multiple testing. A ranking *is* a set of pairwise orderings, so the archive supports "they differ" and supports no statement about which is stronger. That is why his season design is the only sound founding rather than a preference.

## B39 — the kept severity is not an aggregate

His ruling of 2026-10-19: *"Verdict: option 1, but do options 1 and 2 compose? Is this a useful thing to do? Or is 1 preferable over the other?"* Option 1 was to identify the rule producing the kept value before building either panel fix.

**The rule is the absence of a rule.** `FindingRegistry.resolve(..., "MERGED", merged_into=...)` is the single chokepoint every merge passes through. Executed on a registry holding 2 assessments of 1 defect at 0.35 and 0.45:

- target severity **0.35 before the merge, 0.35 after**
- the merged entry keeps its own **0.45**
- the target gains **no severity-related key at all**
- an AST walk of `resolve` finds **0** calls to `max`, `min`, `median`, `mean` or `sum`

So the kept value is whichever entry happened to be the merge *target*, and every other assessment is discarded from it — though not deleted, since it survives on its own entry, which is why the inputs were recoverable for the original measurement.

**That explains the 23.8095% rather than smoothing it.** 35 of 147, interval 17.6469% to 31.3061%, with 24 above every assessment and 11 below. With no aggregation step the kept value is only *coincidentally* inside the range of the other assessments, so the 21.0884% equalling the median is the coincidence rather than the rule, and a value outside the range is not "intended" in any designed sense.

**His composition question therefore has a stronger answer than an ordering preference: options 1 and 2 do not compose concurrently, and 1 is logically prior.** Option 2 was to build the smoothing fix, and smoothing presupposes an aggregate to smooth. There is none, so option 2 is the wrong *shape* of fix rather than a lower-priority fix. Option 1's own text had already sequenced this: *"Neither panel fix should be built until that is answered."*

No code behaviour was changed. `bench/tests/test_the_kept_severity_is_not_an_aggregate_2026-10-29.py` pins the rule that exists today — 6 tests, 5 executing the real chokepoint — so that if an aggregation step is ever added, the test which assumed its absence fails and says so.

## What needs the founder's decision

1. **B47** (new) — Option 1 of B29: have `sv` record whether its post-conditions passed, and have the `memory-updated` check measure against the last save that *finished cleanly*. The measurement above is the case for it: it covers the 7 of 14 occasions Option 3 cannot see. Not built, because it changes when a save gate **passes**, and that has consistently been his call.
2. **`qs:fd5e6e379930`** (new, against B39) — should 2 or more independent assessments of 1 defect be **combined** at all, and if so is the kept value a central tendency, a bound, or an interval rather than a point? He has already observed that no archive can settle this, because, in his reasoning's own words, it is *"a question about what the quantity means"*.
3. **C21** — the one narrow point remaining on the routing ladder: whether *membership* of the falsifier list should be separated from its *order*. His ruling of 2026-10-07 is currently implemented as membership and guarded by a check on the list's length, so separating the 2 changes recorded behaviour. C21 remains open with a larger scope, including the cold-start draw, the removal of sporting vocabulary from the code, and 3 further questions of his from 2026-10-09.
4. **R1** — restarting the zero-plant control experiment, which costs money and needs express authorisation.

## Operational notes

- The **Desktop copy of the master task list**, which is the copy he reads, had diverged from the repository copy by **3,173 bytes**. It has been refreshed and the 2 are byte-identical.
- A full suite run is in progress, logging to `~/Desktop/CDSFL_suite_2026-10-29.log` with a terminal tab tailing it. The previous complete run took 1 h 25 m (36 failed, 12,954 passed, 24 skipped). **B35 and B36 both close on this run's result**, which is their own recorded FOR DONE condition.
- All individually affected checks were run and pass. **6 separate mutations** were used to confirm the new checks fail when the code they guard is broken: 2 on the identity widening, 2 on the B33 wiring, 1 on the Option 3 margin, and 1 verifying the restored state is green.

---


## After 06:24 — the save was refused by the very defect the night had been about

The subcriticality record would not commit. `sv` ran at 06:27 and stopped at exit 1 on its `memory-updated` check, reporting that the newest memory file was 2.7 hours OLDER than the previous sv commit. That is entry B29 exactly: the check measures against the last save, so a follow-up save in the same session is refused for lacking memory that already exists. Option 3, built earlier the same night, pre-checks a different condition and does not cover it; Option 1, which would, is raised as B47 and awaits a ruling.

The honest route was taken rather than the override the script itself warns against: a memory entry was owed for the subcriticality result, so it was written, and the save then landed at `96aec301` with all 6 postconditions passing.

## The memory index had 2 limits and only 1 was being reported

Writing that entry exposed a defect in `sv`'s own reporting. The loader truncates `MEMORY.md` on EITHER characters (25,000) or lines (200), both read out of the installed binary rather than assumed. The figure `sv` prints for remaining runway divided the CHARACTER headroom by the median entry size and ignored lines entirely. On the live index that meant **34 entries of runway reported where the binding line budget allowed 11**, and against the refuse line, **22 by characters against 1 by lines**. The next memory entry — and every save writes a memory entry — would have refused the save.

The diagnosis is a single character, and the code's own docstring already contained it: the `+ 1` in `headroom // (median_entry + 1)` charges each entry's newline against the character budget and against nothing else, while the line above it reads that an entry costs its own line plus the newline. The prose knew; the arithmetic did not.

Neither bound can be dropped, because which of them binds is not fixed. The 2 cross at a median entry of 322.5455 characters; the live median is 103. Across the 5 index snapshots on disk the character budget bound in 3 and the line budget in 2, the switch arriving during October as entries were compressed to single-line pointers. So the character-only formula was right when written and wrong by the time it mattered.

The existing trim could not clear it. Run dry, it reported nothing older than 30 days in Project State — 0 entries, 0 characters — because the month had been productive and every ageable entry was recent. And the pressure is not self-correcting: **116 of 149 entry-lines, 77.8523%, are permanently beyond that trim**, the largest block being the Feedback section at 78 lines, which is standing guidance and ages by design never.

Two things were built. The reported figure now takes whichever budget binds, with z3 proving the bound cannot overrun either. And same-date Project State entries are merged onto 1 line — the key the index already groups on — which took it from 189 lines to 174, kept all 185 pointers, created no over-long entry or preamble, and took the refuse headroom from 1 line to 16. It also stops the growth at source, because a session's entries carry today's date and merge into today's line at no further cost in lines.

The Feedback section is deliberately NOT merged. It has no semantic key — 0 of its 78 lines carry a date — so compacting it would mean merging by position, which is the mechanical-transformation failure the record already names. How that section should be relieved when it binds next is a decision, not a build, and it is recorded as such.

## The register's limit on tickets without an identity cannot be walked back, and it was walked through

A second guard is correctly red. The ticket register ratchets the number of tickets carrying neither a task reference nor an anchor at 317; it stands at **320 of 2,887**, 0.110842 with a 95% Wilson interval of [0.099903, 0.122814] agreed to 6 decimal places by 2 independent methods. The 3 additions were all raised by hand between 04:05 and 06:06 that morning, using the plain proposal call instead of the call that derives an anchor — the same mistake the register's own documentation records from 2026-10-27, where it notes that the escape hatch was designed, documented and simply not used.

What makes this worth recording is that the 320 cannot be brought back down. Measured against a scratch copy: raising 1 identityless ticket takes 320 to 321; migrating it onto a properly derived identity takes it to 322, because history is preserved by keeping the old record as a tombstone and that tombstone is itself identityless; and raising the same item correctly leaves it at 322. **287 of the 320 are exactly such tombstones.** No method sets an identity on an existing ticket.

The obvious repair is refuted by its own blast radius. Making the register refuse an identityless ticket would close the hole, and would also break **60 call sites across 11 test files** whose purpose is to exercise the fallback tiers that exist FOR items without identities. Narrowing the ratchet to ignore tombstones is refuted too: tombstone statuses are terminal, and the register treats a terminal ticket sharing a subject as grounds not to raise a new ticket, so a bare tombstone can still refuse genuinely new work.

So the ceiling is a decision, not a build. Re-baselining a ratchet to admit a breach of its author's own making is not a change to make unilaterally.

## Every failure in the full suite was root-caused before the suite reported them

The run was given a durations table, which also settles the last open part of entry B36. Because no test-order randomisation is installed and the working tree was deliberately left untouched for the run's duration, the failure positions in the progress stream could be mapped to test identities directly, roughly 40 minutes before the summary would have named them.

All 10 failures have causes:

**6 in the immune-memory evaluation are stale pins accusing behaviour that was ordered.** The live memory holds 1 experiment where they expect 3 to 5. It was reset on 2026-10-17 and the archive records why, verbatim: a ruling of 2026-10-16 to reset the immune memory for the upcoming live experiments, since simulation can only tell us so much about how this facility will function in real live or paid experiments. The archive preserves the prior state, names its 6 experiments, and carries a restore command. The write path loads before recording, so the count of 1 is correct accumulation onto a deliberately emptied memory. The product is right and the guards contradict a ruling.

**1 is the limit described above**, correct and awaiting a decision.

**1 was a file mirrored into the repository the same night.** The external assessment of 10 April carried its standard stamp as a sentence beginning with a label, which the strict foot-line reader cannot cross while the older anywhere-search reader could, so the note silently lost enforcement — the precise shape that guard's own documentation predicted. Fixed by wrapping the external body in a verbatim region, which is what it is, and making the stamp the canonical foot-line. Both readers now agree, and blocking findings fell from 15 to 0.

**1 was the generated morning report**, failing Rules 27 and 28 on 4 findings that all sat in quoted material: a word inside a commit subject, a phrase inside a task-list headline, a word inside a quotation of the founder, and a word lifted from the parked file. Those rules govern what this project writes, not what it quotes, and the verbatim-region markers for that already existed and were simply never used by the generator. The 5 quoting sections now open verbatim regions; the authored section deliberately does not.

**1 is a declared figure gone stale** — the set of tests run before every commit now collects 1,508 against a declared 1,500, because tests were added. That guard is the model the others should follow: it names its own refresh command in its failure message, so the fix is 1 command rather than a judgement.

*Written under CDSFL note standard v1.8. Spoken-word version: `~/Desktop/CDSFL_tts/Overnight_Progress_2026-10-29.txt`.*
