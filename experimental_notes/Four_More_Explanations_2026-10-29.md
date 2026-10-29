# 5 more explanations he asked for

**2026-10-29 19:00 GMT (Thursday).** Branch `sim/shakedown-2026-09-29`.

Entry **B51** of the master task list enumerates 16 register items whose text asks for an explanation. 1 is a finding of CC1's that the enumerating predicate caught on the word *explain*; 2 were answered in `Answers_And_New_Decisions_2026-10-29.md`; 2 carry his own instruction to hold them; 5 were closed earlier today. These are the remaining 5.

**Every figure here was recomputed today.** 1 of them had more than doubled since the file he annotated, and that is reported rather than quietly updated.

## 1. What ruling is expected on the 16 closed findings

**His words**, annotating `Closing_Report_2026-10-01.txt`: *"What ruling do you expect from me? You need to explain this issue."*

**What he was annotating:** *"16 findings in 1 arm are closed, with the defect demonstrated, while the fix that closed them was measured as not curing its own falsifier."*

**The issue.** In `commissioning_arm1_panel_20260921T215405Z`, all 69 entries carry fix-efficacy data and split 3 ways: **25** where the fix cured its own falsifier, **16** where it did not, **28** where the instrument could not look. The split sums to 69 exactly (asserted, not assumed). So in 16 cases a fault was real, a repair was applied, the item was recorded CLOSED, and re-running the test that proved the fault still fired.

| figure | value | 95% interval |
|---|---|---|
| closed with a non-curing fix | 16 of 69 = **0.231884** | Wilson [0.148079, 0.343968]; exact [0.138735, 0.349069] |
| cured | 25 of 69 = 0.362319 | Wilson [0.258957, 0.480202] |
| instrument could not look | 28 of 69 = 0.405797 | Wilson [0.297889, 0.523641] |

Cross-verified across statsmodels, a NumPy closed form, the exact beta interval and an mpmath division to 25 decimal places. The field is deliberately **tri-state** (`True` / `False` / `None`) because a boolean merges *the fix failed* with *the instrument could not look* — different states, only 1 of which is a defect in the work. Built as fix 1 of 4 on 2026-10-01: `bench/fix_efficacy.py` gained `OUTCOME_MEANINGS`, `CONCLUSIVE_OUTCOMES`, `ALL_OUTCOMES`, and the catalogue record gained `fix_cured_its_falsifier`.

**The single decision:** should those 16 be reopened?

- **For:** a closed finding whose repair demonstrably did not work is a finding still live, and leaving it closed is the *silent evidence loss* that clause 4 of the 2026-05-18 pre-registration names as critical in its own right.
- **Against:** the defect is demonstrated and the disposition is now visible in the exported record, so nothing is hidden; and reopening items in an archived run rewrites a historical record without changing any live behaviour.

**Recommendation: reopen none, and record the 16 as a known population** so the next commissioning arm's rate can be compared rather than rediscovered. This is the same reasoning he applied to the duplicate pairs this morning — *"not a particularly productive use of resources attempting to rewrite history now"* — and it costs one line rather than a migration.

## 2. The false-alarm proportion for demotion, and why 0.05

**His words**, annotating `Consolidated_For_Your_Evening_2026-10-11.txt`: *"You need to explain this one to me further in plain English. What is the recommendation and why?"*

**What he was annotating:** item 3, *"ONE FALSE-ALARM PROPORTION FOR DEMOTION, AND 0.05 IS THE SUGGESTED VALUE. ... THIS WAS NEVER ANSWERED AND WAS DROPPED FROM THE EARLIER FILE. It is the item that needs a number rather than a yes."*

**What it is.** When the harness judges that a model has become less reliable, it can err twice over: missing a real decline, or demoting a model that is in fact stable. The false-alarm proportion is the accepted probability of the **second** error.

**Why it needs a number.** Every other threshold in the demotion rule follows arithmetically once this one is fixed. Set it and the boundaries are *derived*; leave it unset and the boundaries must be chosen directly — which is exactly the undocumented numeric gate the 2026-05-18 pre-registration exists to forbid.

**Recommendation: 0.05**, for 2 reasons. It is the conventional level, so a reader outside the project need not take the choice on trust; and it makes the thresholds recomputable from 1 number instead of each needing its own justification. A stricter 0.01 demotes fewer stable models and reacts more slowly; a looser 0.10 reacts faster and demotes more models undeservedly. At the evidence volumes this harness reaches, the difference is a small change in the number of supported divisions rather than a change of kind — on the 2026-10-11 figures, 11 divisions instead of 13 at the stricter two-sided setting he approved in the same message.

## 3. Would the fix make the number of failures go up?

**His words**, annotating `READ_THIS_ONE_Decisions_2026-10-16.txt`: *"In plain English please. Are you saying that by implementing your fix, the number of failures would go up? How would this impact experiments? How would it impact on the HIL review queue, or are you talking about something else?"*

**3 answers, in his order.** The number of **reported** failures rises. The number of **actual** faults does not change — they occur now and nothing says so. The impact on the HIL review queue is **0**, established by execution.

**The subject.** Adding a model means editing **12 sites across 6 live-harness files** (`composer.py`, `dm/_types.py`, `experiment_11_orchestrator.py`, `reference_runner_v3.py` ×4, `routing.py`, `runner_core.py` ×4). Of the 10 steps a new seat passes, **5 fail silently, 4 announce, 1 fails loudly** — down from 9 silent of 10 before entry C18 routed 3 lookups through a recording resolver. A silent failure means the seat runs and loses whatever that table gated: the class `base_model_label`'s own docstring calls it *"a capability lost with no error"*, recorded 8 times in this project. Producer: `scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py`, whose lambdas now call the live resolver rather than re-implementing each lookup — `execute-do-not-grep` applied to the measuring script.

**Effect on experiments: more trustworthy, because of when it fires.** The panel rejected 2 of the 3 options. A plain error at each lookup needs 15 edit sites and fails at first use — mid-run, after money is spent. Refusing to dispatch the seat is benching it, which this codebase forbids.

**Effect on the HIL queue: none, and this is measured rather than argued.** Running `scripts/preflight_health_check_2026-10-06.py` today: it wrote to no registry, no ticket store and no data file, and left the working tree unchanged. A registration miss surfaces on the pre-run POST screen and never becomes a finding, so it cannot reach the queue.

**And the live figure worth his attention.** That run reported **8 of 8 checks passed**, and *inside* the passing check listed all 6 simulated seats as absent from 4 tables each — `runner_core.MODEL_SPECS`, `runner_core.INITIAL_FINGERPRINTS`, `composer.PHENOTYPE_TRANSFORMS`, `composer.MODEL_COHERENCE_BUDGETS`. That is **24 absences reported inside a PASS**. Whether each is a genuine miss or a legitimate property of a simulated label is precisely what a loud failure would force someone to decide, and nobody has.

## 4. The paired comparison, which is not about caution

**His words**, annotating `Status_Decisions_And_Next_Steps_2026-10-15.txt`: *"Is this caution on what we should test in simulated runs warranted? We have already discussed this recently. Or is this about something else other than caution? You will need to explain in plan Englis what you are asking me to rule on here."* (*plan Englis* is *plain English*.)

**He is right on both counts: it is not about caution, and the caution question was already settled.** The file failed to say so.

**The actual problem.** The measurement compares 2 arms. Its core assumption holds — the target document is byte-identical at the old commit and today, 3,498 bytes with the same checksum. But its design names a run from **2026-10-03** as the fixed side of the pair, because that run was the head of the branch on the day the design was verified.

**Re-measured 2026-10-29, and the drift has more than doubled.** Against the head at 2026-10-03/04 (`75a3936c`): **341 commits** since, **51** touching `reference_runner_v3.py` or `runner_core.py`, **10** touching `composer.py`. The annotated file said 141, 24 and 3. Those were correct on 2026-10-15 and are now stale, which **strengthens** the argument rather than weakening it.

**So the measurement would be taken against the old runner** — a version of `reference_runner_v3.py` and `composer.py` that will not be kept, telling him about software that no longer exists.

**The decision, in one sentence: run both arms AFTER the 3rd convergence rather than before it**, so what is evaluated is the runner and composer he will actually keep. It is a question of timing, not of care.

## 5. The significance of the hazard figure resting on 2 wrong parameters

**His words**, annotating `Dynamic_Roster_Panel_Synthesis_2026-10-08.txt`: *"What is the significance of this? Please explain in plain English."*

**What he was annotating:** *"The headline hazard figure in the brief rested on two parameters and both were wrong. It assumed a per seat per round critical finding rate of 0.3; one seat measured 0.2337 and rejected the assumption at a probability of 5.6 times 10 to the minus 11, and the other measured 0.1994 over a wider population."*

**The significance, in one sentence: a safety number put to the panel was built on a per-seat-per-round rate of 0.3 that nobody had measured, and when the seats measured it the brief's own hazard figure turned out to overstate the risk.**

| what the brief assumed | what a seat measured | the brief's overstatement |
|---|---|---|
| 0.3 critical findings per seat per round | **0.2337** (same population) | **22.1000%** high; assumed/measured = 1.283697 |
| 0.3 | **0.1994** (wider population) | **33.5333%** high; assumed/measured = 1.504514 |

Cross-checked in mpmath to 25 decimal places. The seat's rejection of the 0.3 assumption at *p* = 5.6×10⁻¹¹ is quoted as the seat gave it and is **not** recomputed here, because the population size behind it is not recorded in the brief — which is itself an instance of the same defect.

**A third error in the same brief, found by the same round.** The brief claimed the hazard magnitude moves by a factor of **7.7915** across a plausible range. That factor spans a correlation of 0 to 0.8, while the brief priced exact values only over 0.1 to 0.5, where the correct collapse is **6.053** — so the brief overstated the collapse by **28.7213%** (mpmath agreeing).

**Why it matters in 3 ways, in increasing order of importance.**

1. **The direction is reassuring.** Every error ran the same way: the brief made the hazard look worse than it is. A decision taken on it would have been over-cautious rather than unsafe.
2. **The cause is the rule this project already has.** An assumed rate of 0.3 was presented inside a brief as though it bore on the question, with no producing script. That is `measured-rate-travels-with-its-script` applied to a brief rather than to a note, and it is why briefs now declare their figures as `<!-- figure: label | script | value -->` comments that the validator **re-executes** before dispatch. The B22 brief written today declares 4 and all 4 re-execute.
3. **The panel earned its cost.** 3 errors in one brief's arithmetic, all 3 found by seats, 2 of them by independent measurement rather than by reading. That is the strongest available evidence that a panel round does work rather than agree — and it is evidence about the method, not about any model.

**No ruling is owed on this one.** It is an explanation of why a figure he was shown was wrong, and the declared-figure re-execution in `scripts/panel_brief_validate.py` that prevents the recurrence is already built and running.

## What remains on B51

2 explanations stay outstanding and both carry his own deferral:

- **The 94 unsavable blockers** — *"If the answer is nothing that would prevent you from completing your work, then save your explanation of this until the end of your work on the master task list too."*
- **The ladder and boot check question** — *"Ask me again when this work is complete if not."*

Neither is forgotten; neither is due.

Written under CDSFL note standard v1.8 (17 October 2026).
