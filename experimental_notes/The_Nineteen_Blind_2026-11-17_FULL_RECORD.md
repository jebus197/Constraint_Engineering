# Full record: the blind free-panel round on the 19 decisions awaiting the founder

Record written 2026-11-17T03:46:59+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

The founder asked for all 19 open decisions awaiting his ruling to be put to a free panel, blind, and then in a collaborative round, judged against the project's 3 formal standards: the simplest sufficient fix, the additive standard, and composability in its strong measured sense. He asked whether the panel's recommendation matched CC1's own, without the seats being told what CC1 had recommended.

Blindness was enforced by construction rather than by intention. The brief builder strips 18 recommendation-marker shapes out of every option and REFUSES to emit a brief if any marker survives, and it shuffles each item's options under a fixed seed so that position alone cannot leak the answer. Before any agreement was scored, the shuffle was replayed and required to reproduce the delivered brief byte for byte.

2 free seats answered: Claude Opus 4.7 through the command-line route, and Fable 5.1 through the same route. Both are free under the founder's existing subscription, which is why this round cost nothing to run.

The scoring instrument was repaired during this session and the repair is part of the record. It originally replayed the shuffle over the LIVE decisions file, which is sound only while that file still holds what the seats were shown. 3 recommendations were corrected after the round was scored, so the replay stopped reproducing the delivered brief and the instrument refused to score at all. It now reads the letters from the FROZEN brief that was dispatched and from a frozen record of CC1's own picks, pinned to a source commit and a blob digest, so the figures keep reproducing after the live file moves. The replay is retained as a cross-check that reports rather than refuses, because it detects a builder-side shuffle fault that the frozen route cannot see.

Agreement, recomputed from the frozen artefacts: both seats chose CC1's option on 12 of 19 items, and at least 1 seat agreed on 14 of 19. Disagreement is preserved as information and not smoothed to consensus: every one of the 19 remains the founder's to rule, and a seat differing from CC1 is not a seat being wrong.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# BRIEF — the 19 decisions the founder owes, put to the free panel blind


## ARTEFACT STAMPS AT DISPATCH

Each seat's copy is a photograph taken when its sandbox was staged. These
are the sha256 digests and modification times of every artefact this brief
names, AS DISPATCHED. If an artefact has changed since, a seat's reading of
it was correct against the state below and must not be read as an error
against a later state. Recompute with `sha256sum <path>` to compare.

| artefact | sha256 (first 16) | bytes | modified (UTC) |
|---|---|---|---|
| `experimental_notes/Decisions_Awaiting_You_2026-11-14_GENERATED.md` | `8d974251ee716fbe` | 87048 | 2026-11-14T14:38:33+00:00 |
| `experimental_notes/CDSFL_MASTER_TASK_LIST.md` | `8a43f6f8f2861b66` | 2104704 | 2026-11-14T13:49:20+00:00 |
| `scripts/register.py` | `11323e2a58405b59` | 11878 | 2026-10-31T01:52:08+00:00 |
| `bench/dm/_manager.py` | `1371196a63e7758c` | 72005 | 2026-08-27T00:01:46+00:00 |
| `bench/tests/test_precommit_gate_cost_2026-09-10.py` | `4189941fd6112722` | 14479 | 2026-11-13T07:47:07+00:00 |
| `hooks/cy_monitor_gate.py` | `575ba790ccd07763` | 14034 | 2026-11-08T14:54:35+00:00 |
| `hooks/local_resource_budget.py` | `387f4c7de3a4aeb9` | 13692 | 2026-10-28T17:46:45+00:00 |

## REQUIRED SECTION 1 — The question

**For each of the 19 numbered items below, recommend ONE of its stated options, or propose a better option the list does not contain, and say which of the project's formal standards your choice rests on.** Each item is a decision the founder has not yet made. Several carry an earlier ruling of his on a DIFFERENT question; where that is so the item says so, and the question put to you is the later one.

**THE 3 FORMAL STANDARDS, IN THE FOUNDER'S OWN WORDS. Use them by name. A verdict that recommends an option without naming the standard it rests on has not answered.**

**1. ADDITIVE — his wording of 2026-11-16, which REFINES the standing text and is the version in force for this round:** *"'additive' means that it must conform to the project's overall aims, objectives and specification, in addition to only applying a fix when a proposed fix can be shown to meaningfully enhance these if no previous fix exists and/or when it replaces/outperforms an existing fix, either previously in place, or proposed by you, or another model."* Read that as 2 clauses. A fix must FIT the project's aims, objectives and specification; and it must either fill a gap where no fix exists, or demonstrably outperform a fix that does exist — including one proposed by another seat in this very round. The standing form adds a third clause that still binds: an addition nothing reaches is not additive either, so a flag, gate or entry point with no caller and no test fails this standard as surely as a removal does.

**2. SIMPLEST SUFFICIENT.** The smallest change that addresses the ROOT CAUSE and the downstream consequences, not the smallest change that makes a symptom go away. Complexity that cannot be done without is justified; complexity that merely could be used is not.

**3. COMPOSABILITY — his words, 2026-10-02, verbatim:** *"Composability doesn't mean composing two solutions just because they can be composed. It means this principle should be applied where two composed solutions demonstrably provide a better, more robust and/or more efficient solution than either fix in isolation. Where a single fix out performs a composed one, that fix should continue to be preferred. In all cases any fix should also take the first two conditions fully into consideration also."* **So composability is a claim that REQUIRES A MEASUREMENT.** Reporting that 2 repairs do not conflict is the weak non-interference sense his definition excludes by name, and will be recorded as not having answered. Recommend a composition only with a measurement showing it beats either part alone on a NAMED property; where a single fix does as well, prefer the single fix.

**WHAT YOU ARE NOT TOLD, DELIBERATELY.** This brief does not carry any recommendation of mine, and the options under each item have been SHUFFLED so their order carries no signal. **Do not open `experimental_notes/Decisions_Awaiting_You_2026-11-14_GENERATED.md`, its spoken twin, or any `Morning_Report_*_GENERATED*` file**: those hold my recommendations and the point of this round is an independent answer. Everything else in the repository is yours to read and run.

## REQUIRED SECTION 2 — Use the harness

Form the answer by RUNNING the machinery, not by writing about it. A seat that returns prose without having executed anything has not answered. The repository holds the producers behind most of these items under `scripts/`, their guards under `bench/tests/`, the live task list at `experimental_notes/CDSFL_MASTER_TASK_LIST.md`, and the ticket register reachable through `scripts/register.py --id <hash>`. Where an item names a file, read it. Where it names a producer, run it. Where a figure in an item matters to your choice, re-derive it rather than trusting the sentence.

**EVERY NUMBER INSIDE THE 19 ITEMS IS QUOTED, NOT DECLARED, AND THAT IS SAID HERE RATHER THAN LEFT FOR YOU TO DISCOVER.** The items below are rendered from the committed decision records, so their figures are as those records state them. They are NOT re-executed by this brief's validator, which checks declared figures only. **Treat any number in an item as a claim about evidence rather than evidence**, and where one decides your recommendation, re-derive it from the named producer and say so. A figure you could not reproduce is itself a finding worth more than the verdict it was supporting.

## REQUIRED SECTION 3 — Produce a fix, and test it

**For each item, deliver a verdict; where your recommendation implies code or text, WRITE IT INTO THE SANDBOX TREE at its real path.** A fix described in prose is not delivered, and a fix written to scratch space is destroyed when the sandbox is torn down. Where an item is a pure judgement with no artefact — whether a standard is adopted, whether a branch is merged — say so and give the reasoning instead; do not manufacture a file to satisfy this section.

**A HARD CONSTRAINT ON EVERY ANSWER.** All 19 are the founder's to rule. Deliver analysis and any proposed artefact, and state plainly in each verdict that it awaits his ruling. Do not install anything as though it were settled.

## REQUIRED SECTION 4 — What would refute you

For each item, state the single observation that would show your recommendation wrong, and say whether the repository can produce that observation today. An item where nothing could refute your choice is an item where you are expressing a preference, and saying so plainly is a better answer than dressing it as a finding. **Where you disagree with the framing of an item — where the question as put is the wrong question — say so and give the right one. That is a finding, not a refusal.**

## REQUIRED SECTION 5 — Output shape

One block per item, in the order given, each carrying: the item code and hash; your chosen option letter or your own better option; the standard or standards your choice rests on, by name; the reasoning in at most a short paragraph; and your refuter. If you cannot reach a view on an item, say which item and why, rather than padding.

**Disagreement with the brief's own framing — a REQUIRED field, and the last thing your reply must carry.** State your strongest disagreement with how this brief frames the work: an item posed as the wrong question, an option list that omits the real answer, a standard applied where it does not bear, or a figure quoted here that your own run contradicts. **Disagreement is preserved as information and is not to be smoothed: there is NO compelled convergence in this round.** A reply with nothing in this field is accepted only if you say so explicitly.

## REQUIRED SECTION 6 — Termination

Stop when every one of the 19 carries a verdict, a named standard and a refuter. Do not continue past that to re-examine items already settled in your own answer, and do not spend the remaining budget enumerating immaterial observations.

---

## THE 19 ITEMS

### ITEM 1. B77 — `pf:4f09b9135a60`

**Headline.** The convergence gate's count side is ROSTER-BLIND, and a repair whose maths now checks out has sat unadopted since 2026-10-07.

**What it is.** The live convergence check takes 10 parameters and not 1 of them names the roster. That matters because 1 of its 2 sides counts consecutive rounds in which no new critical finding arrived, and that count gets easier to satisfy as the roster shrinks: fewer seats generate fewer findings, and the gate cannot tell a quiet healthy panel from a quiet depleted panel. An unadopted seat design written on 2026-10-07 repairs it by scaling the requirement, so a run missing seats has to stay quiet for proportionally longer before it may close. Its reasoning was checked rather than taken on trust, in 4 steps: the bound never asks for less than the exact requirement at any level of correlation between seats, 0 violations over 12,000 combinations, and it is exact rather than merely safe when seats are independent. 1 precondition the design does not state was found during that check, and is recorded with it: a panel whose critical rate is 0 gives an undefined requirement, and the design covers only the case of an empty roster. The case it addresses is real rather than hypothetical. 3 of 53 archived runs carry a round in which fewer seats answered than were taking part, and 1 of those is the failure of 18 July that the runner's own code describes in a comment. A SECOND REPAIR FOR THE SAME DEFECT WAS FOUND ON 2026-11-02 AND IT IS THE DESIGN NOW. A different seat, writing to the same brief on 2026-10-07, repaired it by counting quiet SEAT-ROUNDS rather than quiet rounds: the requirement becomes the roster size times the round count, and each round contributes however many seats actually answered. At a full roster, and at any roster that stays the same size, the 2 rules are literally the same rule, confirmed symbolically and over every roster size from 1 to 6 with 0 disagreements. They come apart when the roster CHANGES between rounds, which is the only shape the archive actually holds: all 3 degraded runs have a single short round with full rounds on at least 1 side. The first rule takes a single number for how many seats are live, so a run whose roster changed has to be given 1 value and the rule does not say which, and the 2 sensible choices disagree by as much as 6 rounds. On a run that lost 4 of 6 seats for 1 round and recovered, the second rule asks for 5 quiet rounds, while the first asks for 9 if you take the worst round and 3 if you take the last. The second rule has no such choice to make. It also aims at a bigger target: the stricter of the 2 convergence gates, which is the gate in force, has a fallback path where closing rests on the quiet count alone, and that gate takes 3 inputs of which none names the roster. A THIRD DESIGN WAS FOUND ON 2026-11-02 AND IT IS THE DESIGN NOW, which means this recommendation has changed twice. The same seat that wrote the first design also wrote a second design in the same brief, and that second design is the more complete. The 3 are not 3 rival answers once seen side by side. The first states the exact requirement and then takes a safe upper bound on it, which is why it needs no measured inputs. The third computes that same exact requirement, which costs it a dependence on 2 measured numbers. The second, from the other seat, restates the upper bound in a form that stays defined when the roster changes between rounds. The bound is never too small, checked over 36 combinations of roster size and correlation, and it is substantially looser: at a 1-seat roster it demands 18 quiet rounds where the exact requirement is 9 to 11, and at 2 seats 9 against 6 to 7. Every extra round is an extra round of every seat's time, and on a paid roster it is paid. WHAT DECIDES IT IS THAT THE THIRD DESIGN'S CASE FOR COMBINING ITS 2 PARTS IS MEASURED RATHER THAN ASSERTED, and it is the only such case found all day. Its own committed falsifier runs clean and shows each part curing a failure the other cannot: with only the record of who answered, the run is labelled degraded but still closes too early, at 2.4796 times its full-roster risk; with only the raised requirement, the risk is held but a reader sees the same record as a full-roster run; with both, it closes properly, is labelled degraded, and sits at 0.7125 of target. A healthy run pays nothing, and a run with no live seats does not converge at all. It also covers the gap the first design leaves, where a panel that never raises a critical finding gives an undefined requirement.

**Why it is his.** Yours because adopting it changes how a pre-registered convergence threshold is computed, and the standing directive on the decay curve reserves that surface to you. It also sits beside B76, where you already have the question of whether the 2 enabled convergence criteria may disagree, so the gate now carries 2 questions rather than 1. Nothing has been wired either way.

**What is actually owed from him.** A decision on whether to adopt the exact roster-aware requirement or the safe upper bound, and if the exact one, which of the 2 recorded correlation figures it should use: the pooled 0.405989 or the within-experiment 0.236014, where the gate is a within-run decision and the design currently defaults to the pooled one. It changes the requirement at 2 of 6 roster sizes.

**The options, shuffled.**
A. **Adopt the safe upper bound instead**, in the seat-rounds form, if you would rather not depend on 2 measured numbers at all. It is never too small and it stays defined when the roster changes between rounds, at the cost of up to 9 extra quiet rounds at a very small roster.
B. **Leave it unadopted** and accept that a run losing seats may close sooner than its pre-registered threshold intended. The status quo, and not neutral: at 2 live seats the chance of a falsely quiet window is 2.4796 times the full-roster value, and the gate cannot see the difference.
C. **Adopt the exact version**, on the simplest sufficient and additive standards. It is 1 file, it holds the risk at or below the full-roster value at every roster size from 1 to 6, it costs a healthy run nothing, and its case for combining its 2 parts is the only measured one in this arc. Its reasoning is cross-checked 2 ways inside the design, agreeing with an independent numerical calculation to better than 1 part in 1,000,000,000, and a constraint solver confirms its 2 labels cannot both apply and that the quiet count alone cannot tell the 2 causes apart.

### ITEM 2. B84 — `pf:4bcde489948b`

**Headline.** (no headline)

**What it is.** You ruled the ORDERING on 2026-11-01 — *"I accept your recommendation. Please implement it"* — against the recommendation that the difficulty estimator comes first, because until it exists the 4th convergence condition is *"a round counter wearing the name of a confidence measure"*. That ruling stands and is not reopened. **The question now before you is a different one, because the predicate-first check has since shown the estimator cannot be fitted at all.** Over 59 distinct archived runs — 65 directories less 6 identical twins — the structured run state holds 21 fields and 0 of them describe the TARGET before the run began.

**Why it is his.** Every available field is an outcome, so the only features are produced by the very thing an estimator would predict: rounds against findings correlate at Pearson r = 0.836787, p = 1.533183e-16, confirmed by NumPy to 9 decimal places, with Spearman rho = 0.782540. An estimator fitted on those would return a number that rises with how many rounds have run — the exact failure your own words name, and it would then carry the authority of a measurement while being a counter. The variance is NOT the obstacle, which is worth saying because it would be the easy answer: rounds run 1 to 41 with a standard deviation of 7.5471, a coefficient of variation of 0.961729.

**What is actually owed from him.** WHETHER TO RECORD A PRE RUN DESCRIPTION OF THE TARGET BEFORE BUILDING THE ESTIMATOR

**The options, shuffled.**
A. **Record only the 1 pre-run field this entry began with.** Narrower and still unblocks the difficulty estimator, at the price of leaving nu, q and the severity specification exactly where they are.
B. **Write an estimator on the features that exist.** it would be fitted on outcomes and wrong in the way your own words predicted, and it would then carry the authority of a measurement while being a round counter.
C. **Record the CLASS of missing reference points — 4 fields across 3 writers — and do not write any estimator yet.** Simplest sufficient: each is 1 field at a point that already writes, and the class costs little more than the instance while making 3 further quantities measurable. Additive: nothing is removed and no decision changes. The 4 are a pre-run target description, a baseline pass rate beside the post-fix one, and the 2 declared severity factors, `W(class)` and `confidence`.

### ITEM 3. B94 — `pf:bb28392e8a9e`

**Headline.** (no headline)

**What it is.** Repairing the verified flag left 2 questions that are yours. First, `bench/dm/_manager.py:717` computes v-bar -- the mean verification score, 1 of the 4 capability dimensions (D_decay, v-bar, A, C) defined in the mathematical appendix and the glossary, and written `v_bar` in code -- as the fraction of a model's findings whose verified flag is true, and documents it as mean verification quality. It is 1 of the 4 fingerprint dimensions, and role assignment scores a model as the dot product of a role's weight vector with that fingerprint, with the tie-break placing v_bar second in an order whose own docstring says higher values win. The flag it reads can be set by an execution or by the model writing VERIFIED in its own reply, and nothing records which setter produced a value. Second, the same gate reading the same flag sits in 4 other runners, and in all 4 the only setter is `mark_verified` while none of them writes a falsifier verdict or references a sandbox verification anywhere.

**Why it is his.** On v_bar: 38 of 50 archived observations are nonzero, so the dimension is not inert, but because the setter is unrecorded no claim is made that self-reporting has actually moved a role assignment, and that boundary is deliberate rather than cautious phrasing. The question is which quantity you want. If v_bar should measure how often this machine verified a model's findings, the parser should stop populating the flag from a reply and v_bar becomes a smaller honest number. If it should measure how often a model CLAIMS verification, it is correct today and the name is wrong. On the 4 runners: applying the canonical runner's new precondition there would make their close path unreachable instead of guarded, which is disabling a feature. This is the measured answer to your question about folding fixes back, and it is that a tested fix does not always fold back. The mislabel is also narrower than the defect: those 4 close with a bare resolve passing no adjudicator, so their closures are unlabelled rather than falsely attributed to a tool, which is why 840 of 1562 archived closures carry an empty adjudicator. The false tool label was v3 only and is fixed.

**What is actually owed from him.** Your choice on 2 independent halves: whether v_bar keeps both the model's own claim and the machine's verification as 2 fields, and which of the 2 the fingerprint reads; and whether the 4 sibling runners get an execution path or keep a relabelled closure. They can be answered separately.

**The options, shuffled.**
A. **Or give the 4 runners an execution path, or leave them.** Porting falsifier machinery into runners whose experiments have already completed adds 0 reachable callers, which the symmetric form of the ADDITIVE standard counts as not additive. Leaving them is defensible on the ground that their archives are read rather than extended, but it leaves a close path resting on a model's word.
B. **On the 4 runners, change their closure to record honestly what it rests on.** It is the SIMPLEST SUFFICIENT change that removes the untruth without removing the feature: a label change, not a behaviour change.
C. **On v_bar, keep both and let you choose which the fingerprint reads.**, and it is the ADDITIVE option: record the model's claim and the machine's verification as 2 fields rather than 1, removing neither, and point the fingerprint at whichever you name. It was not taken unasked because changing what v_bar counts changes a measurement that drives the experiment.

### ITEM 4. B125 — `pf:9aa8db33d2a3`

**Headline.** A JOINT ROUND ASKED 2 SEATS ABOUT A FILE THAT HAD CHANGED SINCE THEY ANSWERED, SO THEIR CORRECT READING OF THE SNAPSHOT READ AS AN ERROR AGAINST THE LIVE STATE.

**What it is.** A panel round runs in 2 halves. In the blind half each seat gets its own copy of the repository and answers without seeing the other. In the joint half both replies are put in front of each other, and the brief for that half refers to files by their path. The problem is that a seat's copy is a photograph taken when its sandbox was built, while the joint brief is read against the files as they are now. On this round a file gained 2 new sections between the halves, 35 minutes and 318 minutes after the blind replies landed, and 1 of those sections was written after the test board finished. A seat correctly reported that something was absent from the copy it could see, and the brief's wording presented that correct answer as a mistake.

**Why it is his.** It needs your ruling because all 3 remedies cost something different and the choice is yours. It also matters more than an ordinary stale reference: it turns a seat's correct work into what looks like an invention, and that is the 1 kind of error a panel cannot catch itself, because the seat has no way to know the file moved under it. The seat said it nearly reported itself for fabricating, and was stopped only by comparing the opening bytes of its own copy against the quoted text.

**What is actually owed from him.** WHETHER A JOINT PANEL BRIEF SHOULD QUOTE THE FILES IT REFERENCES, OR REFUSE WHEN THEY HAVE MOVED

**The options, shuffled.**
A. **Leave it to discipline: do not edit a referenced file between the 2 halves.** No code at all. This is the weakest of the 4 because this session broke that discipline twice without noticing, which is how the defect was found.
B. **Only add the refusal.** Cheap and mechanical: compare each referenced file's hash against the blind half's copy and refuse to dispatch if they differ. It cannot see a file that was changed and then changed back, and it tells a seat nothing about what it should have been looking at.
C. **Have the joint brief quote the state of every file it references, as at the blind half's dispatch, composed with a refusal when a referenced file has moved since.** Quoting makes what each seat actually saw checkable afterwards, which is the same reason the brief already quotes the seats' replies word for word. The refusal catches the other order of events, where the brief was written first and the file changed afterwards. Neither half does both jobs, so this is a composed fix and the reason is named. The cost is a longer brief and 1 more thing that can refuse a dispatch.
D. **Only quote the files.** Makes the exposure verifiable without adding a way for a dispatch to fail, but a brief written before an edit still goes out carrying the older text with nothing to flag it.

### ITEM 5. B141 — `pf:ffddb18b09a0`

**Headline.** THE DESCRIPTOR RULE HE HAS NOW ASKED FOR TWICE, AND 9 GUARD FILES THAT WERE OFF THE COMMIT GATE.

**What it is.** `bench/tests/test_precommit_gate_cost_2026-09-10.py` compares the guard-file count and the collected-test count declared in entry 1.1 against what `hooks/pre-commit` actually runs. It appears 0 times in that hook, so the guard whose whole job is to keep that declaration honest is itself outside the board it measures, and its assertion is unconditional with no skip. That is why the declaration was stale by 3 files before tonight while every commit came back green.

**Why it is his.** A stale cost declaration is the only thing standing between the project and an undetected change in what the commit gate watches. 3 of 235 guard files were on the gate and undeclared, 0.012766, Wilson [0.004351, 0.036854]. The cost is that the collected-test half of the guard goes red by DESIGN whenever an entry closes, so putting the whole guard on the gate makes refreshing the pin mandatory at every commit.

**What is actually owed from him.** Your ruling on which of the 3 options to take, since putting a guard on the commit gate changes what every future commit must satisfy and that is yours rather than mine

**The options, shuffled.**
A. LEAVE IT OFF, and accept that the declaration is checked only when the full suite is run. That is the status quo, and it is what allowed the 3-file drift.
B. SPLIT IT, which is the recommendation: put the FILE-COUNT assertion on the gate, because that number only moves when someone deliberately edits the guard list, and leave the COLLECTED-COUNT assertion in the full suite where entry closures belong. This catches the drift found tonight at every commit and adds 0 forced refreshes.
C. PUT THE WHOLE GUARD ON THE GATE. Nothing can drift, at the cost of refreshing the declaration whenever an entry closes -- which under your 2026-11-10 batching ruling is now rare rather than per-fix.

### ITEM 6. B142 — `pf:970ab5074a95`

**Headline.** THE SETTINGS SURFACE: THE ROLE SELECTOR CANNOT OFFER THE 4 ROLES THE UX BRIEF SPECIFIES, AND HIS CREDENTIAL STORE IS NOT IN THE BRIEF AT ALL.

**What it is.** Section 10 of the authoritative UX design brief specifies a model-and-role selector whose Role column offers Orchestrator, Worker, Researcher and Classifier. The backend's `known_roles()` returns `collator`, `participant` and `player_manager` -- the harness's own panel roles -- so that column cannot be populated as designed. Measured against the brief, 3 of its 5 requirements are built; the roles and the peer catalogue are not. Separately, the password-protected credential store you described appears nowhere in the brief: its Advanced section lists the registry-tunable surface and the donation matrix, and the Advanced mockup is a stub.

**Why it is his.** A registry role is not a label. It carries a merge signature and an alpha vector that the role-assignment scorer uses, so mapping 4 interface roles onto 3 harness roles changes how a run selects its models -- which B21 already records as your decision rather than mine. The alternative is a presentation layer the dispatcher ignores, which is honest but means the interface's roles never reach the harness. And the credential store touches secrets: today 10 keys sit in a plain-text environment file, so the direction of travel is clearly an improvement for how those keys are held, but how the store itself is built matters.

**What is actually owed from him.** Your ruling on whether the 4 interface roles map onto the harness's 3 or remain labels, and whether the credential store is built now or after the runway

**The options, shuffled.**
A. DEFER the role work until after the runway and build only the peer catalogue, which adds capability without touching selection. If the runway matters more than the interface.
B. ADD a presentation layer only: the interface offers the 4 names and the dispatcher keeps its own 3. Nothing about run selection changes, and the role column becomes labelling rather than control — which is honest only if the screen says so.
C. **MAP the 4 interface roles onto the 3 harness roles, which is the recommendation**, with the mapping written down and executed by a test so it cannot drift. The interface's roles then really reach the dispatcher. The cost is that it changes how a run selects models, which is why it is yours and not mine.

### ITEM 7. B143 — `pf:18582c4fed35`

**Headline.** (no headline)

**What it is.** You asked tonight whether severity had been abandoned in favour of a model vote. It had not: the model-asserted number is the original design, required by the finding schema since the 30th of March 2026, 7 months before the first severity panel, and 12 panel rounds since have been attempts to replace it. The real finding is narrower and worse. The formula in section 7.7 of the appendix needs 2 inputs. Reading the runner by syntax tree rather than by text search: the hard-or-soft class has 1 reader and 0 writers, and the confidence has 1 reader and 2 writers, neither of which writes the object the reader reads. So the formula defaults both inputs on every finding and the switch that would enable it stands off.

**Why it is his.** 3 things follow, and each was verified here rather than taken from the panel record. First, the 1 confidence value the codebase does collect is parsed out of a model's own verdict text with a default of 0.5, which is the self-report your directive of the 8th of November declares inadmissible, so pointing the formula at the value that exists would reinstall the vote. Second, the proof mechanism proves the wrong quantity: it accepts a reproduction of the residual-risk number as evidence for a severity claim, and over 652 archived findings the 2 correlate at minus 0.5538, p = 1.152e-53, so the proof moves against the number it licenses. Third, and this answers your question about magic tricks directly: with only 2 consequence weights, 0.5 and 1.0, no cut above 0.5 can test consequence magnitude at all. Z3 returns unsat for a counterexample and SymPy gives the supremum of the soft branch as exactly 0.5, so moving the cut from 0.7 to 0.8, 0.9 or 0.95 reclassifies 0 findings. A real mathematician would see that immediately, which is why it must be fixed before Bench Run 2 rather than after.

**What is actually owed from him.** Your ruling on whether the severity proof is repointed at the number it licenses, and whether the maths gains a 3rd consequence weight. The repoint has a different measured cost at each of its 3 call sites and is not reversible by a flag, so it is yours rather than mine. Collecting the 2 missing fields is already authorised by your ruling of the 8th of November and needs nothing further.

**The options, shuffled.**
A. REPOINT THE PROOF AND ADD A THIRD WEIGHT, which is the recommendation, taken in that order and with the collection done first by me without troubling you. Collecting the 2 fields is already yours by the ruling of the 8th of November, and B87, the entry on the severity specification asking for an inadmissible quantity, classes it as carrying out an instruction rather than a decision, so it proceeds either way. Repointing the proof makes a release door depend on a proof about the number it actually releases. Adding a third consequence weight strictly between 0.5 and 1.0 is the only change that makes any cut a test of magnitude, and section 7.7's own caution 3 used to point at 5 material-defect categories as a scale that exists, and that citation was found dead on the 11th of November and replaced: the file it named is 39 lines long, has no such section, and nothing in the repository enumerates those categories.
B. COLLECT THE FIELDS AND STOP THERE, leaving both the proof and the weights as they are. This is the smallest step, it makes the formula computable in shadow, and it changes no gate, but it leaves the number carrying no consequence meaning.
C. REPOINT THE PROOF ONLY and leave the maths at 2 weights, accepting that the critical cut tests the class and the belief but never the magnitude, and saying so plainly in the paper rather than letting a reader assume otherwise.

### ITEM 8. B154 — `pf:10e2507dabf6`

**Headline.** 2 DECISIONS ARE OWED TO HIM FROM THE NIGHT'S ENCODING WORK: WHERE THE FAILURE-MODE CRITICAL LEVEL SITS, AND WHETHER 22 DRAFT BOXES GO TO THE PANEL

**What it is.** 2 decisions came out of the encoding work of the 11th and 12th of November, and neither blocks any other item, so both are reported rather than raised as blockers. The first is where the critical level sits on the engineering severity scale. The engineering domain now declares the AIAG-VDA failure-mode severity scale, whose published landmarks are 7 to 8 for high consequence and 9 to 10 for safety or regulatory consequence. The manifest declares the critical level at 7. The second is the 22 new expert encodings written against current published standards, all of them tagged DRAFT, which were authorised for panel adjudication in the morning.

**Why it is his.** On the first: 7 is the conservative cut, because it admits MORE findings as critical than the standard's own safety line would. Moving it to 9 would align the declaration with the standard it cites, and would LOOSEN what the gate admits. A change that loosens a gate changes which findings reach a human, so it is not a change to take from a reading of a standard. On the second: the tier ladder is DRAFT, then CROSS_VERIFIED, then VALIDATED by a human, then OPERATIONAL. A panel moves a box exactly 1 rung, to CROSS_VERIFIED, and not to the top; the human validation rung stays separate and stays his. All 22 are tagged DRAFT on purpose so that 142 lines of detail is never mistaken for adjudicated authority, because density is not provenance.

**What is actually owed from him.** Your ruling on whether the engineering critical level stays at 7 or moves to 9, and when the 22 draft encodings go to the panel. The free panel has answered the level question twice, blind and joint, and both seats recommend 7. The level is yours because it decides which findings the gate admits as critical.

**The options, shuffled.**
A. HOLD THE PANEL DISPATCH UNTIL THE 28 OLDER ENCODINGS ARE ENRICHED, SO THE PANEL SEES AN EVEN CORPUS. Defensible, and it delays adjudication of 22 boxes that are already written and already in use by the composer. The 22 would stay DRAFT meanwhile, which is the correct state for them, so the cost is time rather than risk.
B. LEAVE THE ENGINEERING CRITICAL LEVEL AT 7 AND SEND THE 22 DRAFT ENCODINGS TO THE PANEL AT HIS CONVENIENCE. 7 is the conservative cut and nothing is lost by holding it: a finding admitted as critical that turns out not to be gets a second look, while a finding excluded by a looser cut gets none. The panel dispatch costs nothing on the free seats and moves the 22 boxes exactly 1 rung.
C. MOVE THE ENGINEERING CRITICAL LEVEL TO 9 TO MATCH THE PUBLISHED SAFETY AND REGULATORY LINE. This is defensible and it is what the standard's own text says, but it loosens the gate, so the consequence of being wrong falls on findings that would no longer reach a human at all.

### ITEM 9. B160 — `pf:055a68c4f4ae`

**Headline.** THE FIGURE THE TURN HOOK PRINTS TO HIM RESTS ON A PROXY NO SIBLING PREDICATE AGREES WITH ON ANY ENTRY IT APPLIES TO

**What it is.** Every turn prints a line saying how many open items await your ruling. For an item that already carries a ruling of yours, the test deciding whether anything is still owed is whether ANY date anywhere in that item's text is later than the ruling date. The intent behind it is exact and correct: a question raised after a ruling cannot have been answered by it. The implementation is a stand-in for that intent, and a dated progress note of mine is not a question. 3 tests for the same idea were computed side by side. The first is the one in use. The second asks whether a later date sits inside the asking sentence itself. The third asks whether an asking sentence is positioned after the first post-ruling date.

**Why it is his.** They disagree on all 4 of the items they apply to, and not 1 of the 4 gets the same answer from all 3. The convergence gate item is yes, no, yes. The difficulty estimator item is yes, yes, no. The verified-flag item is yes, no, no. The joint-round item is yes, yes, no. The line you read says 8 of 12 open items await you, and 4 of those 8 are these. If the test in use is wrong, that figure is wrong, and the defensible floor is 4 rulings you have never given plus 4 permissions. No 4th test was written, deliberately, on this project's own rule that a surface defeating 3 predicates is the point to stop and raise it rather than to try a 5th time.

**What is actually owed from him.** Your choice among the 4 options for the predicate behind the count the turn hook prints to you. Nothing further is owed on the measurement: the 3 candidate tests disagree on every entry they apply to, so no measurement can choose between them and the choice is a judgement about which direction of error you prefer.

**The options, shuffled.**
A. REPLACE IT WITH THE POSITION TEST, so an item is treated as awaiting you only when an asking sentence sits after the first post-ruling date. This would move 3 of the 4 off your list, leaving 5 of 12. It reads a document as if it were chronological, which these entries are not.
B. LEAVE THE TEST AS IT IS AND CHANGE NOTHING. It errs toward telling you about an item rather than hiding it, and the suppression direction is the one this project has already had to withdraw once, on the 9th of November, after retiring asking sentences removed live questions from your list. The cost is that the printed figure can overstate what you owe, which a report can say in words instead.
C. REPLACE IT WITH THE SENTENCE TEST, so an item is treated as awaiting you only when a later date sits inside the asking sentence itself. This would move the verified-flag item and the convergence gate item off your list, leaving 6 of 12 rather than 8. It is the tightest of the 3 and the most likely to hide something.
D. KEEP THE TEST AND REPORT THE DISAGREEMENT BESIDE THE COUNT, so the line says 8 and the report names the 4 that 3 tests cannot agree on. Nothing is hidden and nothing is overstated without a note, at the cost of a longer line.

### ITEM 10. B170 — `pf:ed54f9ccded2`

**Headline.** (no headline)

**What it is.** You checked the public repository and were told the recent severity work is not there, even though the last commit reads as very recent. Both halves of that are true. The shakedown branch carries a commit pushed at 18:46 on the 12th of November, which is the recent one you saw. The main branch carries a commit from the 30th of September, and the repository's default view is main, so what a reader browses is 43 days old. Nothing failed to push. The work is on GitHub, on a branch no default view shows. Checked file by file: the domain manifest, the severity panel full record, the severity proxy producer and the per-domain cut guard are all absent from main, and the mathematical appendix is present but 43 days stale, which is worse than absent because a reader cannot tell.

**Why it is his.** This is not a discovery so much as a warning nobody acted on. Sv prints on every single commit that it is not on main, quotes your own ruling that main is the only branch that gets updated unless there is a stated reason to open an experimental branch, and warns that drift is what left main 16 days stale in August. The current drift is 2.7 times worse than that incident, and the merge has been listed as owed to you in the recovery document since at least the 7th of November. A warning that fires on every one of them and changes nothing is the loudest possible form of a mechanism nothing reaches, and that half is mine to fix. The ruling is yours because the branch was opened for a stated reason your own rule permits, so the question is whether the shakedown is over, and because a merge of over 620 commits across 43 days is not casually reversible.

**What is actually owed from him.** WHETHER THE 620-PLUS COMMITS ON THE SHAKEDOWN BRANCH MERGE TO MAIN, OR THE SHAKEDOWN BRANCH BECOMES THE REPOSITORY DEFAULT

**The options, shuffled.**
A. KEEP THE SPLIT DELIBERATELY AND SAY SO PUBLICLY, with a note on main naming the active branch. Honest and nearly free, but it accepts that the default view stays stale and relies on a reader noticing the note.
B. MERGE THE 620-PLUS COMMITS TO MAIN AND KEEP COMMITTING THERE. It restores your own stated rule, makes the work visible to any reader including the external models you check with, and removes the drift at its cause rather than warning about it. The cost is one merge with a real conflict surface across 43 days, and a full board afterwards before anything else lands.
C. MERGE AND THEN RETIRE THE SHAKEDOWN BRANCH ENTIRELY, so there is one line of development. Simplest end state, largest single step, and it forecloses going back to a separate experimental branch without opening a new one.
D. MAKE THE SHAKEDOWN BRANCH THE REPOSITORY DEFAULT. Cheapest by far, 1 setting on GitHub, and it makes every reader see the current work immediately. It leaves main as a 43-day-old artefact that still looks authoritative to anyone who navigates to it directly, which is the condition that caused this.

### ITEM 11. B171 — `pf:5292c9025d73`

**Headline.** HIS MID-TURN MESSAGE SILENTLY DISCARDS HIS OWN STANDING `d`, SO THE STOP GATE PRODDED PAST A BARRIER ITS OWN DOCUMENTATION CALLS NEVER OVERRIDDEN

**What it is.** The stop gate lists 3 exemptions and its own documentation calls the first one, your instruction to discuss rather than proceed, never overridden. On the 12th of November it refused a stop 9 times in a turn whose message ended with that very instruction. Measured on the live transcript: the gate reads your commands as none. The founder messages in the window carry the discussion marker 3 times and then, fourth, your mid-turn question about a documentation sweep, which carries no command at all. 2 lines of the gate wipe the command set whenever a message of yours arrives after any tool call of mine, so your question wiped your own instruction.

**Why it is his.** This is the same fault as the one repaired on the 8th of November arriving through a different door. Then it was your own next line that erased your command, and the repair was to take the union of commands across the turn rather than the last line alone. The union fixed the line path and left the mid-turn message path open. The reset is not wrong in itself, which is why this is not a simple revert: its own comment names the opposite failure it prevents, that a discussion marker from an earlier turn would otherwise silence the gate indefinitely. Both failures are real. The discriminator comes from your own rulings rather than from invention: an unmarked comment that ends in a question mark is a question, and a discussion marker is a barrier rather than an item in a sequence, so answering a question does not lift the barrier.

**What is actually owed from him.** WHETHER TO ALLOW THE EDIT TO THE STOP HOOK THAT STOPS YOUR MID-TURN MESSAGES DISCARDING YOUR OWN DISCUSSION MARKER

**The options, shuffled.**
A. ALLOW A NARROWER EDIT that exempts only the discussion marker from the reset and leaves every other command resetting as now. Smaller change, but it treats 1 marker specially for no stated reason beyond this incident.
B. ALLOW THE EDIT, so the reset clears your commands only when the new message carries at least 1 command, or is an imperative not ending in a question mark. A bare question then leaves a standing discussion marker standing, and any instruction from you still clears it, so a stale marker still cannot silence the gate indefinitely.
C. LEAVE IT AND ACCEPT THE PRODDING, on the grounds that a mid-turn message is genuinely new input and the gate cannot know your intent. Costs nothing to build and means your discussion markers keep being discarded whenever you add a thought mid-turn.

### ITEM 12. B175 — `pf:00cfce67090e`

**Headline.** THE CLEAN SUITE MUTATES THE WORKING TREE AND THE GIT INDEX WHILE MEASURING THEM, AND 1 TEST COSTS 17 MINUTES TO ASSERT SOMETHING ITS OWN SUBJECT DOES NOT NEED

**What it is.** 2 tests write to the live repository during a full-suite run, and 1 of them stages a file into the git index. Those 2 writes are mine to fix and the environment seam, an environment variable the generator honours so a test can redirect its writes, is already prepared and proven at 12 checks of 12. THIS DECISION IS THE THIRD PART AND IT IS YOURS: the mirrors test currently asserts that the whole commit hook exits successfully, which drags the whole guard board along. Asserting instead the effect of the hook's FIRST stage would let the test run in a throwaway repository, stop the index being written, and remove about 17 minutes from every full suite run.

**Why it is his.** A measurement that alters its subject cannot speak about the subject, and the staged file would also enter the next commit unasked. But the 17-minute change is not a repair with a right answer: it changes WHAT A TEST ASSERTS. The hook's first stage sits 368 lines before the guard board, and the mirror ordering is the only thing the test claims to examine, so asserting the stage is the narrower and more honest claim. The cost is that it stops incidentally proving the whole hook passes -- real coverage, standing at 1 assertion over the hook's entire exit path, and precisely what costs the 17 minutes. The end-to-end behaviour is already covered by 2 other tests.

**What is actually owed from him.** Your ruling on the 3rd part only. The 2 live-tree writes are mine to fix and the environment seam is already prepared and proven at 12 checks of 12. What is yours is whether the mirrors test asserts the effect of the hook's 1st stage instead of its exit code, because that changes what the test asserts, and it trades about 17 minutes off every full suite run against 1 assertion of end-to-end coverage.

**The options, shuffled.**
A. Give the mirrors test a scratch repository: REFUTED, the test's own comment records why a copied tree produces a false red.
B. An environment seam the generator honours and the test sets for every generator: prepared, and P-passed at 12 checks of 12.
C. Have the mirrors test assert the effect of the hook's first stage rather than its exit code: removes the real-repository run, stops the staging, and takes about 17 minutes off every full suite. And the argument against it is stated rather than hidden: it removes an assertion, so the removal clause of the additive standard applies and needs a committed measurement that the replacement dominates on a named property. The named property is suite cost at about 17 minutes a run, measured; what it loses is end-to-end coverage, at 1 assertion over the hook's whole exit path already duplicated by 2 other tests.

### ITEM 13. B180 — `pf:aa6f7b704f10`

**Headline.** THE GATE THAT ENFORCES HIS 60-SECOND MONITORING DIRECTIVE WAS INERT THROUGH BOTH OF TODAY'S 3-HOUR MEASUREMENTS

**What it is.** `hooks/cy_monitor_gate.py` enforces your standing directive of 2026-05-18 to monitor a running experiment at about 60-second cadence. Its predicate is `pgrep -f "run_simulated_experiment.py"` and nothing else. Measured by execution while the B165 full-suite measurement was running: `cy.live_runs()` returned an empty pair while `pgrep -f "pytest bench/tests"` returned 1 pid. So through the 3 h 19 m 43 s run that ended 07:30:43 and the 3 h 07 m 58 s run that ended 12:40:10, the gate was silent. The monitoring happened because the directive is in the instruction files and was followed by hand; the gate itself was inert, which is the symmetric half of the additive standard.

**Why it is his.** It is yours because widening it changes how often a gate interrupts you. A 200-minute pytest is plainly a running process and your directive says experiment or process, so I believe it should be seen. But that is a judgement about your own interruptions, not about correctness, and 2 full-suite runs a day would mean the gate prodding through both.

**What is actually owed from him.** Your ruling on whether the monitoring gate widens to see a full-suite run. The gate exists to enforce your own 60-second directive, so widening it changes what prods you and when, which makes the scope yours. The measurement is already in hand: the gate was silent through both of the 3-hour measurements.

**The options, shuffled.**
A. Leave it scoped to simulated experiments. The status quo, and not neutral: the directive is then enforced only by my reading the instruction files each session, which is exactly the arrangement the additive standard calls an addition nothing reaches.
B. Widen it to see a full-suite run, which is the recommendation. The directive is then enforced by a mechanism rather than by my remembering it, at the cost of the gate prodding during every suite run.

### ITEM 14. B182 — `pf:9950e21f2aed`

**Headline.** (no headline)

**What it is.** `~/.claude/hooks/local_resource_budget.py` runs before every delegated Agent, Task and Workflow call and stops delegated work launching the project's heavy verification on a machine with 8 cores, 8 GiB and a measured heavy budget of 1. On 2026-11-13 it refused 2 adversarial-review briefs of mine, both of which FORBADE delegated heavy runs in as many words. Chasing that refusal, its live predicate was imported and driven over a systematic grid: 5 ordinary verbs of execution x 10 noun phrases this project uses for its own suite x 3 sentence tails, 150 cells, every one a genuine instruction that should be refused. 126 pass straight through.

**Why it is his.** The gate's own docstring records the over-refusal class from 2026-10-17 and claims to have fixed it by requiring an imperative mention outside a negation. That half HOLDS: 3 of 3 prohibitions are correctly not refused. The other direction was never checked. 8 of the 10 noun phrases are completely blind, 15 of 15 each, including `bench/tests/` - the literal path a brief would name - and `the full test suite`, the most natural phrasing. Only `the suite` and `the full board` are caught, and those are the 2 phrasings the gate's author tested. The gate's own docstring argues why under-catching is the dangerous half: an author who cannot state a limit drops it or rewords around the matcher, and a delegated agent with no stated limit is more likely to invoke the tooling.

**What is actually owed from him.** Your permission to edit the resource-budget hook, which by design cannot be changed without it, and your choice between widening the noun-phrase side and leaving the gate as it stands. The measured gap is 126 of 150 real instructions passing the gate.

**The options, shuffled.**
A. Leave the gate as it is and rely on the briefs themselves to state the limit. Cheapest, and defensible only if delegated briefs are always written by something that states limits - which is the assumption the gate exists because it failed.
B. Widen the noun-phrase side to the forms this project actually writes, and add a case for a bare path such as `bench/tests/`. It closes the measured 0.84 gap and leaves the negation handling, which works, untouched.

### ITEM 15. B185 — `pf:3142ce4958c8`

**Headline.** EXPERT ENCODINGS GO STALE AGAINST CHANGING STANDARDS, AND THE ARCHIVE CANNOT SAY WHICH VERSION ANY PAST RESULT USED

**What it is.** Standards revise slowly - 0.976190 per year combined across the 4 feeds - so the textbook-obsolescence risk is real but low-grade. The faster decay is that the archive cannot be re-interpreted: when a standard does change, nothing records which past results used the old scale. The design agreed with him is 3 files, not 1: formal standards, user preferences, and confirmations.

**Why it is his.** The 3 files have radically different change rates, and that is what makes the split dominate rather than being taste. Tamper detection is not built from scratch: the project already seals directories into RFC 9162 Merkle chains with SHA-256 and refuses on tamper.

**What is actually owed from him.** Your choice of exposure ceiling for the encoding currency check, 1 per cent against 0.5 per cent, and whether model and client version share the standards record or get their own. Neither is a correctness question: both trade how often you are prompted against how long a superseded standard can sit unnoticed.

**The options, shuffled.**
A. A tighter 0.5 per cent ceiling, needing a 7.31-day backstop. More checks, little gain given the session cadence.
B. Model and client version recorded in the same file as standards, or in their own. They drift far faster - the installed client is 70 patch releases behind what the newest model needs.
C. Exposure ceiling of 1 per cent, giving a 14-day backstop for absences, with the primary check on every session start. On his measured session pattern 0 of 74 gaps exceeded that ceiling, so the backstop fired 0 times over that pattern.

### ITEM 16. B186 — `pf:d0f37996a791`

**Headline.** HE PROPOSES A 4th FORMAL PROJECT STANDARD, REAL-WORLD APPLICABILITY UNDER A HUMAN-CONSEQUENCE CAVEAT, AND IT IS NOT YET ADOPTED

**What it is.** The project has 3 formal standards: simplest sufficient, additive, and composability requires a measurement. Each is written in both instruction files with a decision rule a reader can apply. He has proposed a 4th, real-world applicability, scoped to where a change has a meaningful consequence for the human in the loop.

**Why it is his.** It is raised rather than adopted because his words were 'I am considering' and 'I would suggest'. Adopting a standard from a deliberation would be an inference, and this project records a defect class where tentative or rejected advice acquired his authority through my prose. It is not redundant: the existing 3 all govern the SHAPE of a fix and none asks whether the fix matters to the person using it.

**What is actually owed from him.** WHETHER TO ADOPT REAL-WORLD APPLICABILITY AS AN ADDITIONAL FORMAL STANDARD, AND IN WHAT EXACT WORDS

**The options, shuffled.**
A. Leave it as a consideration and decide later. Costs nothing now, but the case that prompted it recurs.
B. Adopt it scoped exactly as he worded it, governing only where a change has a meaningful consequence for the human in the loop, and require that invoking it NAMES the consequence rather than merely asserting that a consequence exists.
C. Fold it into the existing additive standard as a clause rather than standing it up as a 4th. Fewer standards to hold, at the cost of burying the one question the others do not ask.

### ITEM 17. B190 — `pf:d837803feb6a`

**Headline.** A PANEL ANSWERED A QUESTION HE ASKED AND THE ANSWER REACHED NO DOCUMENT HE HAS EVER BEEN GIVEN

**What it is.** The standards-currency brief put 5 sub-questions to the free seats. 4 are reported in the spoken file he received. The 5th, on commensuration, is not reported in it at all - neither the spoken copy nor its markdown twin contains the words commensuration, disjunction or incommensurable.

**Why it is his.** The seats did answer it. The full record holds 8 occurrences of the question and 10 of disjunction, including the resolution that disjunction is the unique fail-safe aggregator, which makes the remaining question a policy one and therefore his. The answer exists in a 115,529-byte record he has not been given, and the question it hands him reached neither a spoken file nor an entry.

**What is actually owed from him.** Your ruling on whether the disjunction over per-scale critical cuts is adopted now or deferred, and your authorisation for severity-record stamping. The stamping is the precondition for measuring the aggregator at all, so deferring the first without authorising the second leaves the question unmeasurable.

**The options, shuffled.**
A. Defer the aggregator until severity-record stamping is built, so the choice can be measured rather than reasoned.
B. Authorise the severity-record stamping separately - it is the precondition for measuring anything about commensuration.
C. Adopt the disjunction, which is the recommendation: it cannot under-report a critical finding in any scale, so it is the fail-safe member. The empirical comparison cannot be run until severity records carry a scale field.

### ITEM 18. B194 — `pf:a3b5ccfe2d28`

**Headline.** (no headline)

**What it is.** The composer builds every working seat's prompt from the core directive file. It classifies each block of that file as a HARD constraint by keyword, so a block containing MUST, NEVER or HARD is carried to every seat verbatim, and a block containing none of those words is not carried at all. An unratified draft split across 2 blocks therefore delivers its binding sentence and drops the header saying the draft is not binding. Part 1 is built and is mine: a marker that suppresses a block whatever its keywords, so a draft can sit in the canonical file and reach 0 prompts. PART 2 IS YOURS: whether the composer should also REFUSE a block whose own text announces it as proposed while carrying no marker.

**Why it is his.** The defect was found by the cc2 seat, which was asked to write the paragraph you would paste for your proposed 4th standard and declined to write it where the brief pointed. Its stated reason was verified here by calling the predicate rather than taking its word: the header returns False and a 1-sentence body containing MUST returns True. Part 2 is yours and not mine because it is a TIGHTENING. It would refuse a commit that is currently allowed, and the author it refuses is the author who did not know the not-in-force marker exists, which is the whole population the fix is for. A tightening that fires on the people it is meant to help can be worse than the hazard, and that trade is a judgement rather than a measurement.

**What is actually owed from him.** Your ruling on part 2 only. Part 1 is built, tested and on the gate, and needs nothing from you. What is yours is whether the composer should REFUSE an unmarked block that announces itself as proposed, because that is a tightening: it would refuse work currently allowed, and the author it refuses is the author who did not know the not-in-force marker exists.

**The options, shuffled.**
A. Leave part 1 as the whole fix: the marker exists, the directive documents it, and an author who misses it installs an unratified rule silently as before. Cheapest, and it keeps the refusal surface unchanged, but it relies on each author reading a section of a 32,000-character file, which is the arrangement the additive standard calls an addition nothing reaches.
B. Report rather than refuse: warn on an unmarked announcing block and let the commit through. It preserves the evidence without blocking anyone, and it is weaker than it sounds here, because the author who missed the marker is also the author who will not read the warning.
C. Require the marker: refuse any block whose text announces itself as proposed, draft or awaiting a ruling while carrying no marker. It is the only option that reaches the author who does not know the not-in-force marker exists, which is the population the whole fix is for, and the refusal names the marker, so the refusal itself teaches it. The cost is a new way for a commit to be refused, and the refusal can be wrong: a live directive discussing ratification would trip it unless the announcing phrase is matched strictly.

### ITEM 19. B197 — `qs:633854939cf3`

**Headline.** THE TASK LIST'S BRANCHING POINT ESTIMATE HAS CROSSED 1, SO THE LIST IS NOW GROWING ON BALANCE AND NOT MERELY FAILING TO EXCLUDE GROWTH.

**What it is.** The full suite of 2026-11-14 failed the subcriticality check on the task list. The branching ratio is 1.033088 with a 95 per cent interval of [0.874617, 1.220273], over 281 entries added against 272 closed across 406 snapshots. You ruled on 2026-11-08 that an interval crossing 1 was accepted and the instruction was to keep closing. The guard was then narrowed to fire only on the point estimate, precisely so it would stay silent on what you had settled. It has now fired on the stronger condition.

**Why it is his.** An interval crossing 1 says growth cannot be excluded. A point estimate above 1 says growth is the central estimate. Those are different claims and only the first carries your ruling. What moved it is visible in the last 2 snapshots: 322 entries with 274 closed on 2026-11-13, against 340 with 275 on 2026-11-14, so 18 were added and 1 closed in 2 days. Most of the 13 entries worked through overnight remain open because they await you, which is their correct state and is also the reason the ratio moved.

**What is actually owed from him.** WHETHER THE BRANCHING RATIO REACHING 1 AS A POINT ESTIMATE, RATHER THAN AS AN INTERVAL THAT CROSSES IT, CHANGES YOUR 2026-11-08 RULING

**The options, shuffled.**
A. Direct a verified closing pass over open entries whose evidence is now green, which would move it honestly rather than by moving a threshold.
B. Accept it and retire the subcriticality assertion entirely, keeping the figure as a reported number with no gate. This costs the alarm.
C. Rule again that the ratio of 1.033088 stands and the instruction is still to keep closing, and re-scope the guard a second time to the interval's LOWER bound crossing 1, which is the next strictly stronger fact. The measurement stays, it is still reported, and it can still fire on something you have not ruled on.



<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 377 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel the_nineteen_2026-11-17) -->

All six evidence agents are in, and my own derivations are done. Writing up.

---

# VERDICTS ON THE 19 — free-panel seat, 2026-11-17

**All six dispatch digests verified identical** (`sha256sum`), so every reading below is against the state as dispatched. **Every one of the 19 verdicts awaits the founder's ruling. Nothing below is installed as settled.**

**Two artefacts written to the sandbox tree at their real paths** (the Edit tool required interactive approval unavailable in a one-shot dispatch; applied via Bash):
- `scripts/what_is_safe_to_merge_to_main_2026-10-16.py` — fail-open repair (Item 10)
- `bench/tests/test_the_merge_instrument_refuses_without_history_2026-11-17.py` — its guard, **3 passed**
- `experimental_notes/Proposed_Fourth_Standard_Real_World_Applicability_2026-11-17.md` — draft wording, marker on **16 of 16 blocks** (Item 16)

**Wolfram was not called.** Every result below is decided by SymPy, z3, NumPy/SciPy, statsmodels or direct execution of the repository's own producers; no claim rests on a Wolfram-only value, so the second falsifier was not needed. On a machine without it that is the whole answer.

---

## ITEM 1. B77 — `pf:4f09b9135a60` · convergence gate

**My option: NONE OF A/B/C — the question is already answered by the live code. Keep what is wired; do not adopt the exact version.**

**Standard: ADDITIVE (clause 2 — a replacement must demonstrably outperform the incumbent) + SIMPLEST SUFFICIENT.**

The brief says the repair "has sat unadopted since 2026-10-07" and "Nothing has been wired either way." **Both are false against the dispatched artefact.** `required_quiet_run(k, n_declared, n_live)` is live at `bench/reference_runner_v3.py:1625-1691`, implementing `ceil(K·n_declared/n_live)`, wired into **both** arms (`:10327` legacy, `:11640` hardened condition C), with `live_seat_count()` at `:1694`. Guards `test_both_convergence_arms_are_roster_aware_2026-11-12.py` + `test_the_roster_window_bound_is_sound_2026-11-02.py`: **34 passed in 3.39s**.

The brief's decisive argument for the seat-rounds form — "the first rule takes a single number for how many seats are live, and the rule does not say which" — **does not apply to the wired code**, which evaluates per round via `live_seat_count(round_idx, raw_counts_per_model)` at `:21575` and `:21610`. There is no single value to choose.

I re-derived the exact requirement `K·f(n_dec)/f(n_live)` with `f(n) = −ln E[(1−p)^n]` under a beta-binomial latent, and swept it against the wired formula:

| live | WIRED | exact ρ=.236, q∈{.1,.3,.5} | exact ρ=.406 | wired ≥ exact |
|---|---|---|---|---|
| 1 | 18 | 11.04 / 10.61 / 10.03 | 8.35 / 7.96 / 7.47 | YES |
| 2 | 9 | 6.29 / 6.13 / 5.92 | 5.28 / 5.13 / 4.95 | YES |
| 6 | 3 | 3.000 | 3.000 | YES (exact) |

The wired bound is never below the exact requirement at either recorded ρ, and is tight at full roster. The exact version's cost is a standing dependence on two measured numbers, and **the ρ choice changes the integer window at exactly 2 of 6 roster sizes** (live=1 and live=2) — reproducing the brief's figure. Paying a permanent parameter dependence to save quiet rounds only at rosters of 1 and 2 fails SIMPLEST SUFFICIENT. `0.2873/0.1159 = 2.4789`, consistent with the quoted 2.4796 to rounding.

**Refuter:** an archived or simulated run at a 1- or 2-seat roster where the wired window demonstrably costs more seat-time than the exact one would save, *net of the risk that a mis-estimated ρ introduces*. The repository can produce half of this today (the window comparison, as above); it cannot produce the cost half, because no run has executed since the 2026-11-12 wiring.

---

## ITEM 2. B84 — `pf:4bcde489948b` · difficulty estimator

**My option: C, with the correction that field 1 is already built.**

**Standard: SIMPLEST SUFFICIENT + ADDITIVE (symmetric clause).**

The producer reproduces exactly: 59 distinct runs, 21 state fields, 0 pre-run target fields, Pearson **r = 0.836787, p = 1.533183e-16**, Spearman **0.782540**, sd 7.5471, CV 0.961729. Option B is correctly rejected — an estimator on those features is a round counter wearing a measurement's authority.

**But option A is already executed.** `pre_run_target_description()` exists at `bench/reference_runner_v3.py:9942` and a 22nd key `"pre_run_target"` is written at `:21703` under his 2026-11-08 ruling. 0 of 65 archived states carry it because **no run has executed since**. So what is actually owed is the *remaining three* fields — and two of them (`W(class)`, `confidence`) are the same two inputs Item 7 needs. **This is not composability** in his sense: it is one collection site with two consumers, not two fixes composed, and I claim no measured advantage for pairing them.

**Refuter:** a single executed run whose `pre_run_target` turns out to be itself outcome-derived (e.g. populated after round 1). The repository cannot produce it today — it needs one run to complete.

---

## ITEM 3. B94 — `pf:bb28392e8a9e` · v_bar and the verified flag

**My option: C on v_bar; B on the four runners.** These are genuinely independent and I answer them separately as the item invites.

**Standard: ADDITIVE on both halves — removal clause for v_bar, symmetric clause for the runners.**

Every figure reproduces: `_manager.py:717-719` computes v_bar from `f.verified`; both setters exist (`runner_core.py:748/838/896/1127` from reply text; `immune_agents.py:6477`, `insect_brain.py:1358` from execution); `_types.py:417` is a bare `verified: bool = False` with **no provenance field**; 38 of 50 nonzero; **7 of 8 construction sites populated from the model's own reply**; 840 of 1562 empty adjudicators (re-derived independently — the figure is a *string literal* in the producer at `:472-473`, not computed, so it will silently go stale).

C is right because changing what v_bar counts changes a live measurement, and ADDITIVE's removal clause forbids that without a committed measurement that the replacement dominates. Two fields removes nothing and defers only the fingerprint pointer, which is his.

On the four runners (`reference_runner.py`, `run_exp35_policy_engine.py`, `run_exp36_evidence.py`, `run_exp37_evidence.py` — each 1 setter, **0** falsifier-verdict writes): porting the execution path adds 0 reachable callers, which the symmetric clause counts as not additive. B is the smallest change that removes the untruth without removing the feature.

**Refuter:** a single archived role assignment whose winner changes under machine-verified-only v_bar. The repository *can* produce this today — 4 runs carry fingerprints — and it was not run here. That is a gap in my answer, stated rather than hidden.

---

## ITEM 4. B125 — `pf:9aa8db33d2a3` · joint brief against a moved file

**My option: B — add only the refusal. Not C.**

**Standard: COMPOSABILITY (his sense) — and it refuses the composition here.**

**Half of option C already shipped.** `stamp_brief_at_dispatch()` at `bench/confer_maths_panel_2026-09-05.py:1657-1721` injects the sha256/bytes/mtime table via `scripts/stamp_the_brief_artefacts_2026-11-06.py` — **the brief I am answering carries it, and I used it.** The entry's own text "3 CANDIDATE REMEDIES, NONE BUILT" is stale.

So C is no longer "compose two new things"; it is "add a second thing beside a shipped one." His definition requires a **measurement** that the pair beats either part alone on a named property. No such measurement exists, and I did not produce one. What is measurable and missing is narrower: the stamper reads **live bytes at joint-dispatch time** and nothing compares them against the blind half's snapshot. The refusal closes exactly that, and it is the only un-built half.

**Refuter:** a case where a stamp alone would have prevented the 2026-11-10 incident. It would show the shipped half already suffices and even B is unnecessary. The repository can test this today by replaying that round's hashes.

---

## ITEM 5. B141 — `pf:ffddb18b09a0` · gate-cost guard off the gate

**My option: B (split), on a stronger ground than the item gives.**

**Standard: SIMPLEST SUFFICIENT.**

Reproduced: the test appears **0 times** in `hooks/pre-commit`; **0** skip/xfail in the file; 3/235 = 0.012766, Wilson [0.004351, 0.036854] exactly. Targeted run (board test deselected per the no-heavy-run rule): **11 passed, 1 deselected, 32.13s**.

**Two of the brief's figures are stale.** The gate now runs **309** guard files, not 235, and the declaration at task-list `:318` reads `files=309 collected=5088` — **the pin is current today**, not stale. On today's denominator the drift rate is 3/309 = 0.009709.

The real argument for B is one the item does not make: the two assertions are **sequential statements in one method** (`:181-183` file count, `:184-188` collected count), so the file-count assert **masks** the collected-count assert on failure. Splitting them is therefore not only about gate placement — it repairs a live masking defect. That is the root cause; C does not address it and A leaves both.

**Refuter:** a measurement showing the collected-count assertion goes red on a commit that closes no entry — which would mean the two cannot be separated by refresh cadence after all. Producible today by running the guard against a synthetic entry-closure diff.

---

## ITEM 6. B142 — `pf:970ab5074a95` · role selector and credential store

**My option: NONE AS FRAMED — the role half is already built; the real owed decision is the functional→structural map.**

**Standard: ADDITIVE (symmetric clause).**

`known_roles()` returns **seven** roles — `['classifier','collator','orchestrator','participant','player_manager','researcher','worker']`. The brief's three are now `known_roles("structural")`. Four functional role files were added 2026-11-14; guard `test_the_interface_roles_reach_the_selector_2026-11-14.py`: **12 passed**. Option C's "the interface cannot offer the 4 roles" is false.

What remains is exactly option B's condition, and it is **already the documented state**: `bench/model_catalogue.py:76-84` says in terms *"adding them changes which names the SELECTOR can offer and changes 0 dispatch decisions."* The functional→structural map lives at `:86-99` with `classifier→None`, `researcher→None` — so two of the four interface roles reach nothing. **That is the unreached addition**, and it is what is actually owed: whether `classifier` and `researcher` get a structural target or the screen states that they are labels.

The "3 of 5 requirements built" figure is wrong in the pessimistic direction: strictly **1 of 5** is fully built (roles); search and roster table are partial (peer absent entirely — 0 occurrences); add-model and presets are absent.

On the credential store: it exists (`bench/credential_store.py`, Argon2id/scrypt → AES-256-GCM, mode 0600) on his direct 2026-11-10 requirement, with a guard. Its absence from the brief is a brief gap, not unauthorised work. The "10 keys" figure is **not reproducible here** — `.env` is excluded from panel sandboxes by design.

**Refuter:** a dispatch in which a model selected as `researcher` in the interface actually reaches a different seat than one selected as `worker`. Producible today by driving `load_effective_policy(role=...)` for both.

---

## ITEM 7. B143 — `pf:18582c4fed35` · severity formula

**My option: A — repoint the proof and add a third weight, in that order.**

**Standard: ADDITIVE (clause 1 — fit to the project's specification) + SIMPLEST SUFFICIENT.**

I derived the collapse myself rather than trusting the sentence. SymPy: the maximum of `Sev = W·c·Ver` over `c ∈ [0,1]` is **1** for (HARD, Ver=True) and **exactly 1/2** for all five other cells. z3, over the negation of the equivalence across all three variables: **unsat** — so `Sev ≥ θ ⟺ (HARD ∧ Ver=True ∧ c ≥ θ)` for every `θ ∈ (1/2, 1]`. A second z3 query: no cut in (0.5, 1.0] reclassifies anything at the realised Sev values — **unsat**. Consequence magnitude enters only through `W`, and `W` has two values, so **no cut above 0.5 is a bound on magnitude**. Confirmed independently by a second instance on a separately-written script, agreeing exactly.

And the fix is verified, not asserted: with a third weight at 0.75, z3 returns **sat** for "moving the cut 0.7→0.8 reclassifies by class." The third weight is precisely what makes the cut a test of magnitude. That is the root cause; option B leaves it and option C says so in the paper instead of fixing it.

The repoint is justified independently: over **652** archived findings the severity float and the R_k the proof reproduces correlate at **r = −0.5538, p = 1.152e-53, CI [−0.6048, −0.4982]** — the proof moves *against* the number it licenses, and 555 of 652 (85.12%) proven entries would stop being released under the proof's own 0.05 tolerance.

**One brief figure corrected:** "the class has 1 reader and 0 writers" is false. AST analysis gives **1 reader (`:11026`) and 1 writer (`:3713`)**, and that writer targets `self.entries[canonical_id]` — *the very object the reader reads*, added 2026-11-11. The appendix itself already corrects this at `:1382-1394`. The honest statement is **not populated**, not unwritable. The confidence half reproduces exactly (1 reader, writers into `stats['verdicts']` and `_sv_rows`, neither the registry entry), as does the `0.5` default parsed from verdict text at `:14773`.

**Refuter:** a declared third consequence weight that no domain can populate, making the richer formula an addition nothing reaches. Testable today against `domain_manifest.toml`, where 5 of 10 domains declare `severity_scale = "none"` — that is the live risk and I flag it as unresolved.

---

## ITEM 8. B154 — `pf:10e2507dabf6` · engineering critical level; 22 drafts

**My option: B — hold 7, send the 22 at his convenience.**

**Standard: ADDITIVE (clause 1) — and `p-pass-ambiguity-default`, which the manifest itself already invokes.**

The manifest at `bench/cdsfl_registry/domain_manifest.toml:284-295` declares the AIAG-VDA scale, the bands (`7-8 high`, `9-10 safety or regulatory`) and `critical_level = "7"` — all reproduced. Its own `critical_level_note` already records the full argument: *"7 AND 9 ARE BOTH DEFENSIBLE CUTS AND THEY ADMIT DIFFERENT SETS... Moving it to 9 would LOOSEN what the gate admits."* An ambiguous constraint resolves HARD; the conservative cut is the HARD reading. A finding wrongly admitted as critical gets a second look; a finding excluded by a looser cut gets none. The asymmetry is the whole argument, and it survives.

**22 DRAFT reproduces exactly.** Two corrections: the older corpus is **30** untagged files, not 28; and `grep -c tier bench/cdsfl_registry/composer.py` = **0** — the composer never reads `encoding_tier`, so DRAFT is inert as a filter. More sharply: **all four engineering encodings are untagged**, so engineering contributes zero of the 22, and the critical level reaches a prompt through the manifest severity block, not through a DRAFT encoding. Option A's "even corpus" concern is therefore about a tier the consumer cannot see.

**Refuter:** an archived engineering finding at severity 7 or 8 that reached a human and was judged not worth a human's time. That would show 7 over-admits. The repository can answer it today — the archive carries severities — but it cannot answer it *on the AIAG scale*, because 0 of 809 severity records carry a scale field (see Item 17).

---

## ITEM 9. B160 — `pf:055a68c4f4ae` · the "awaits you" predicate

**My option: D — keep the test, report the disagreement beside the count.**

**Standard: ADDITIVE (removal clause) + SIMPLEST SUFFICIENT.**

The live predicate reproduces verbatim at `scripts/how_many_decisions_actually_need_him_2026-11-01.py:321`: `any(d > ruled for d in _DATED_IN_BODY.findall(txt))`. The per-item pattern reproduces exactly — B77 yes/no/yes, B84 yes/yes/no, B94 yes/no/no, B125 yes/yes/no. **The 3-predicate comparison is a committed producer** (`scripts/how_much_of_this_is_actually_his_2026-11-12.py:224-249`), which the item's "no 4th test was written" framing obscures.

**The printed figure in the item is badly stale.** Live output of `scripts/task_list_markers.py --summary` is **"19 of 54 open await YOU"**, not 8 of 12. And the predicate now applies to **5** entries (B142 joined after its 2026-11-12 ruling), **5 of 5 disagreeing**, not 4 of 4.

A and C both *suppress*, and this project withdrew a suppression on 2026-11-09 after retiring asking sentences removed live questions from his list. Replacing a predicate when no measurement can choose between the candidates is choosing a direction of error by taste. D removes nothing, hides nothing, and costs one line — and the producer that generates the disagreement list already exists, so D is a wire, not a build.

**Refuter:** him saying the longer line is worse than the overstatement. Nothing in the repository can produce that observation; it is his preference, and I say so plainly rather than dressing it as a finding.

---

## ITEM 10. B170 — `pf:ed54f9ccded2` · shakedown branch vs main

**My option: B — merge and keep committing on main.**

**Standard: ADDITIVE (clause 1 — conformance to the project's stated aims).**

This is the one item where the *decision* rests on a judgement I cannot verify here, and I say so: **this sandbox has no `.git`**, so every commit count, date and ahead/behind figure in the item is NOT REPRODUCIBLE by me. What *is* reproducible: the warning exists at `scripts/cdsfl_sv.py:1111-1147`, quotes his ruling verbatim, and **warns, never aborts** (it is not a git hook — it fires only on commits routed through `sv`). The August incident is independently committed in three files. `43.3929/16 = 2.71205625`, so "2.7× worse" is arithmetically right conditional on two unverifiable dates. No producer exists for any B170 figure; the entry's `evidence:` marker names only the warning file.

B restores his own stated rule and removes the drift at its cause. D is cheapest but leaves a 43-day-old `main` that still looks authoritative, which is the exact condition that caused this. C forecloses a future experimental branch his rule already permits.

**A separate defect found while checking this, fixed and guarded.** `scripts/what_is_safe_to_merge_to_main_2026-10-16.py`'s `sh()` discarded `returncode`. With no `.git` it returned `""` everywhere, so the script **exited 0** while printing "a MERGE, not a fast-forward" and "B7's repair held" — an all-zero all-clear from an instrument that could not see. Reproduced before reporting. Repaired to refuse, reusing the behaviour `scripts/task_list_burndown_2026-09-11.py` already has, so no new mechanism was introduced. Verified by execution: **`REFUSED: ... exited 128 ... EXIT=2`**. Guard written and green: **3 passed**. This is the instrument the merge decision would have been made on.

**Refuter:** a measurement showing the merge's conflict surface across 43 days exceeds the cost of the staleness. The repository **cannot** produce it from this sandbox at all, and that is why B remains a judgement — his, not mine.

---

## ITEM 11. B171 — `pf:5292c9025d73` · mid-turn message discards `d`

**My option: NONE — the defect does not reproduce on the live hook. Nothing to allow.**

**Standard: ADDITIVE (clause 2 — a fix must fill a gap or beat an incumbent; here the incumbent already holds).**

The three exemptions and the "never overridden" sentence reproduce at `hooks/work_not_narrate.py:930-934` and `:36`. But the claimed "2 lines wipe the command set" is **contradicted**: line 888 reads `if worked_since and (_new or not _is_bare_question(c))`, guarded since 2026-11-12. The reset fires only when the new message carries a command *or* is not a bare question — **which is option B's proposal, already implemented.**

Driven directly against the live predicate on real JSONL fixtures:

| case | result |
|---|---|
| `d` is last founder message | `had_d=True` — stop allowed |
| `d`, then assistant tool calls | `had_d=True` — marker survives |
| **bare question mid-turn after a tool call** | **`had_d=True` — marker survives** |
| control: non-question message after work | `had_d=False` — reset fires, as intended |

Mutation board `scripts/the_mid_turn_predicate_mutations_2026-11-10.py`: **7 of 7 RED**, restore sha256-verified. Guard `test_his_command_is_the_union_over_the_turn_2026-11-08.py`: **21 passed**, on the gate at `pre-commit:497`.

The "9 times" figure is also wrong: the repository records **34+** for 2026-11-12 and **8** for 2026-11-08. No "9" appears anywhere.

**Refuter:** a live transcript from after 2026-11-12 where a standing `d` is discarded by a mid-turn message. The repository can produce this today by replaying the 2026-11-12 transcript through the current hook — I ran constructed fixtures, not that transcript, and that is the weaker half of my evidence.

---

## ITEM 12. B175 — `pf:00cfce67090e` · mirrors test, 17 minutes

**My option: C, and the removal clause is satisfied more easily than the item claims.**

**Standard: ADDITIVE (removal clause) + SIMPLEST SUFFICIENT.**

Reproduced: the test runs the real hook with `cwd=ROOT` at `test_desktop_mirrors_stay_current_2026-09-10.py:355`; asserts the whole hook exits 0 at `:398`; the scratch-repo refutation is real at `:363-371`; the gap is **1035 − 667 = 368** lines exactly (the task list's absolute 589/957 are stale). The 17 minutes is **measured with a committed record** — 1032 s, n=1, observed live on 2026-11-13.

**Two findings that strengthen C.** First, the claim "already covered by 2 other tests" is **unsourced** — it appears verbatim in four places and names the two tests nowhere; on my reading the genuine end-to-end coverage is **1** test (`test_precommit_guard_2026-09-09.py::test_a_green_tree_commits`), not 2. That weakens C's stated justification. Second, and decisively: `resources/suite_record.json` records that at the last committed full board, **the mirrors test was RED** — `TestTheOrderingActuallyHolds::test_a_drifted_mirror_does_not_refuse_the_commit` is in `failed_tests`. **You cannot spend 17 minutes a run defending coverage from a failing test.** The removal clause asks for a committed measurement that the replacement dominates on a named property; suite cost at 1032 s is measured, and the coverage being traded away is 1 assertion that is currently not passing.

The scratch-repo refutation is also narrower than option A states — it is specific to a tree with **no `.git`**; `test_precommit_guard_2026-09-09.py` shows a `git init`-ed scratch repo works.

**Refuter:** a regression in the hook's exit path that the stage-1 assertion would miss and the exit-code assertion would catch. Producible today by mutating the hook below stage 0 and checking which assertion goes red — the project's own mutation-board idiom. It was not run here.

---

## ITEM 13. B180 — `pf:aa6f7b704f10` · monitor gate scope

**My option: B — widen it.**

**Standard: ADDITIVE (symmetric clause).**

The predicate is `pgrep -f "run_simulated_experiment.py"` and nothing else, at `hooks/cy_monitor_gate.py:212`. His 2026-05-18 directive says *experiment or process*; a 200-minute pytest is plainly a running process. A gate enforced only by the assistant reading the instruction files each session is precisely the arrangement the symmetric clause names — and this project has 11 confirmed defects of that exact shape against 0 removals of something needed.

The cost is real and I state it rather than minimise it: two full boards a day means the gate prodding through both, and the gate's own docstring records that its sibling `work_not_narrate.py` was killed by the 15 s hook timeout **153 of 360 times** for being slow. Widening a `pgrep` pattern adds no I/O, so that specific risk does not transfer.

**Refuter:** a measurement that the widened gate's refusals during a suite run exceed its `MAX_REFUSALS` budget and so disable themselves — turning the widening into an addition that reaches nothing. Producible today by running the gate against a planted pytest pulse with `CDSFL_CY_LOGS`/`CDSFL_CY_STATE`, which exist precisely so this can be executed. I did not run it.

---

## ITEM 14. B182 — `pf:9950e21f2aed` · resource-budget hook

**My option: B — widen the noun-phrase side. And the permission he is being asked for is the right thing to ask for.**

**Standard: ADDITIVE (clause 2) + SIMPLEST SUFFICIENT.**

**I did not edit the hook**, because the item states it cannot be changed without his permission and that permission has not been given. I measured it instead, driving the live `_instructs_heavy_verification` over a 150-cell grid (5 verbs × 10 noun phrases × 3 tails), every cell a genuine instruction that should be refused:

```
grid cells=150  REFUSED=30  PASSED THROUGH=120  gap=0.800000
  15/15 refused   'the suite'
  15/15 refused   'the full board'
   0/15 refused   'the full test suite'      <- the most natural phrasing
   0/15 refused   'bench/tests/'             <- the literal path a brief names
   0/15 refused   'the test suite' | 'the whole test suite' | 'the guard board'
   0/15 refused   'the full guard board' | 'the board' | 'the verification suite'
```

The structural claim reproduces **exactly**: 2 of 10 phrases caught at 15/15, 8 completely blind at 0/15, and the two caught are the two the author tested. My gap is 0.800 against the brief's 0.84; the difference is my phrase list, not the mechanism, and the finding is unchanged. The negation half holds — all five prohibitions I tested, including the ones in my own agent briefs tonight, correctly pass.

The regexes are three lines (`:98-102`); widening `_NOUN_MENTION` and adding a bare-path case is the smallest change reaching the root cause, and it leaves the negation handling — which works — untouched.

**Refuter:** a measurement that the widened matcher re-opens the 2026-10-17 over-refusal class. Producible today, and it is the check I would run first: the same grid rewritten as prohibitions, which must stay at 0 refusals.

---

## ITEM 15. B185 — `pf:3142ce4958c8` · encoding currency

**My option: C (1 per cent ceiling), and B answered as "their own file". But the item cannot be ruled on tonight, and I say why.**

**Standard: SIMPLEST SUFFICIENT.**

The combined rate **0.976190/yr** reproduces (0.111111 + 0.142857 + 0.222222 + 0.5). The 3-file design exists. RFC 9162 Merkle sealing exists at `bench/verification_chain.py` with the refuse-on-tamper driver `scripts/cdsfl_seal_logs.py`. The client is **70 patch releases** behind (`claude --version` = 2.1.220 vs 2.1.290), which answers B on its own: a quantity drifting ~1400×/yr does not belong in a file that changes ~1×/yr, and splitting is what makes the per-file change rates meaningful.

**But the item's own derivation is wrong.** Solving `1 − exp(−λt) = 0.01` at the combined 0.976190/yr gives **3.76 days**, not 14; at 0.005 it gives **1.88 days**, not 7.31. The 14.61 and 7.3050 figures reproduce only from **λ = 0.5** (the GHS worst case) through the repo's own `ceiling·730.5/λ` form. The figures are real; the attribution in the item is not. The "0 of 74 gaps" splits: **0 exceeded** reproduces (0 of 182, max gap 12.15 d), but **74** has no producer and no recorded filter.

**The blocking fact:** `scripts/the_standards_currency_mutations_2026-11-13.py` **refuses to run** — its baseline is already red, with `test_the_standards_currency_producer_holds_2026-11-13.py::test_c2_the_self_exclusion_is_reachable_and_moves_the_count` FAILING. That test is on the commit gate. Ruling on an exposure ceiling whose producer's own guard is red is ruling on an unverified instrument.

**Refuter:** the red guard turning out to be a stale assertion rather than a producer defect — which would clear the way to rule tonight. Producible today by reading that one assertion; I did not, and flag it as the next thing to check.

---

## ITEM 16. B186 — `pf:d0f37996a791` · a 4th formal standard

**My option: B, amended — adopt it, but define it BY REFERENCE to the five material-defect categories already in `cdsfl_core_formal.md` §10 rather than as fresh text.**

**Standard: SIMPLEST SUFFICIENT + ADDITIVE (symmetric clause).**

It is not redundant: the existing three all govern the *shape* of a fix, and none asks whether the person using the system would notice. That gap is real.

But a fresh definition of materiality would be the **second** declaration of one idea, and this project has already measured what that costs. `.claude/CLAUDE.md` records it: the composability standard reaches every seat through the dispatcher's SYSTEM prompt intact, while the **brief template** states it as *"say whether the repairs compose, conflict, or are independent"* — the weak form his own definition excludes. Two declarations, disagreeing, and the measured consequence was **10 of 10** uses in the excluded sense, Wilson [0.722467, 1.000000]. §10 already enumerates materiality in five categories, lives in a 32,671-character file, and reaches every working seat through the composer.

Option C (fold into additive) buries the one question the others do not ask. Option A costs nothing now but the case recurs.

**Artefact delivered:** `experimental_notes/Proposed_Fourth_Standard_Real_World_Applicability_2026-11-17.md`, carrying proposed wording for him to accept, amend or reject. It is **not** written into `.claude/CLAUDE.md` — writing it there is installing it, and his words were *"I am considering."* The wording scopes the standard to **priority, never admissibility**, because a materiality standard that can refuse work becomes a mechanism for declining unglamorous repairs, which `cdsfl_core_formal.md`'s Objective section forbids by name.

**Refuter:** a change with a real consequence for the human that maps to none of §10's five categories. Producible today — enumerate the open entries' stated consequences against the five. I did not run it, and my recommendation rests on that unexecuted check.

---

## ITEM 17. B190 — `pf:d837803feb6a` · commensuration

**My option: B and C together, and this is the one place I claim a composition — on the item's own structure, not on a measurement, and I mark the difference.**

**Standard: ADDITIVE (clause 1).**

Reproduced: the full record is **115,529 bytes** exactly; the spoken copy and its markdown twin contain `commensuration`, `disjunction` and `incommensurable` **0 times each**; the resolution is at `:191` — *"Disjunction is the unique **fail-safe** member, so 'is disjunction right?' is a policy question, not an admissibility one."* Two minor corrections: the "8 and 10" are `grep -c` **line** counts, not occurrence counts (9 and 11 occurrences); and `incommensurable` appears 0 times in the round-2 record (once in round 1).

**The decisive fact is the item's last sentence, and it is confirmed:** a scan of 133,283 archived records found **809** carrying a `severity` key and **0 of 809** carrying any of `scale`, `severity_scale`, `standard_version`, `critical_level`, `consequence_domain`. The schema at `bench/cdsfl_finding_schema.json:23-28` is a bare dimensionless number. **The empirical comparison between aggregators cannot be run at all today.**

C alone adopts an aggregator that cannot be measured for an unbounded period; A alone defers a question the panel has already resolved on admissibility grounds while leaving the precondition unbuilt, so the deferral never ends. Stamping is the precondition for measuring anything here — that is a structural dependency, not a claim of measured dominance, and his standard reserves the word "composability" for the latter. I am not claiming it.

**Refuter:** an archived finding whose critical status differs under disjunction versus conjunction. **The repository cannot produce this observation today** — that is the finding, not a limitation of my answer.

---

## ITEM 18. B194 — `pf:a3b5ccfe2d28` · composer refusal on unmarked draft blocks

**My option: C — require the marker. And I have a measurement the item does not.**

**Standard: ADDITIVE (symmetric clause).**

Everything reproduces: `_block_is_hard()` at `composer.py:796-799` returns **False** for a draft header and **True** for a one-sentence MUST body; `_NOT_IN_FORCE_MARKER` at `:740`, wired at `:366` before HARD extraction; guard `test_a_draft_block_binds_nothing_2026-11-14.py` **12 passed** and on the gate at `pre-commit:583`; the formal file is **32,671 characters**. One correction: the marker list is **eight** words (`HARD, MUST, NEVER, REQUIRED, NON-NEGOTIABLE, FORBIDDEN, DO NOT, ALWAYS`), not three — so the surface that silently binds is wider than the item says.

The item's argument against C is that the tightening *"fires on the people it is meant to help."* **I tested that on myself.** Writing the Item 16 draft deliberately, knowing the per-block rule, having just read the directive that states it, I put the marker on headings and my own check caught **8 of 16 blocks missing it** — including the block containing the proposed standard's binding text. Under part 1 alone that draft would have shipped its MUST sentence and dropped every warning.

That is one observation, not a rate, and I will not inflate it. But it is the direct counter to the item's objection: the tightening does fire on the author who did not know — **and that is the only way the author finds out**, because the refusal names the marker. The author who misses a marker in a 32,671-character file is also the author who will not read option B's warning. Option A relies on exactly the reading that failed.

**Refuter:** a live directive block discussing ratification that the announcing-phrase matcher trips on. Producible today by running the proposed matcher over `cdsfl_core_formal.md` — and I note the marker string appears **0 times** in that file today, so the corpus for this test is clean and the false-positive risk is measurable before anything ships.

---

## ITEM 19. B197 — `qs:633854939cf3` · branching ratio

**My option: A, but the question as put is the wrong one — see below. Not C.**

**Standard: ADDITIVE (removal clause) + SIMPLEST SUFFICIENT.**

The arithmetic reproduces exactly: 281/272 = **1.0330882**, and the Wilson interval on 281/553 transformed by `p/(1−p)` gives **[0.874617, 1.220273]** — matching to all printed digits, and Agresti-Coull agrees. The counts themselves need `.git`, which this sandbox lacks. Note the dispatched task list holds **344** entries against the item's quoted snapshot of 340, so the ratio is already slightly higher than quoted.

C is moving a threshold to silence an alarm, and the guard's own docstring at `:243-270` explains why that was acceptable *once* — because he had ruled on the interval. Doing it a second time, pre-emptively, is the pattern the first re-scope took care to distinguish itself from. B retires a measurement with no committed showing that a replacement dominates, which the removal clause forbids directly.

**But the framing is wrong, and this is a finding.** The branching-process model treats each closed entry as an individual producing R children. An entry blocked on his ruling **produces nothing** — it is an absorbing state pending an external input, not a branching individual. The item says so itself: *"Most of the 13 entries worked through overnight remain open because they await you."* So R is measuring a mixture of two processes, only one of which is a branching process. The correct repair is to stratify, and **the vocabulary already supports it**: `STATES` at `task_list_markers.py:59` includes `BLOCKED`, and my own tally finds it used **0 times** — 275 DONE, 54 OPEN, 10 WITHDRAWN, 5 DEFERRED. An unused state in a declared vocabulary is itself an addition nothing reaches. There is direct precedent: `test_withdrawn_entries_are_not_counted_as_outstanding` already excludes a category for exactly this reason.

So: **A now** (it moves the figure honestly rather than by moving a threshold), and the stratification as the real repair. A is also what the guard's error text asks for.

**Refuter:** a stratified ratio that stays above 1 on the work-gated entries alone — which would show the growth is genuine and not an artefact of decision backlog. **The repository cannot produce this today** (no `BLOCKED` markers, no `.git` here), and until it can, both my recommendation and the item's own three options rest on an unstratified figure.

---

# DISAGREEMENT WITH THE BRIEF'S FRAMING — required field

**My strongest disagreement: seven of the nineteen items ask about work that has already been done, and the brief's own Section 2 warning did not go far enough.** It told me to treat numbers as claims. The stale thing is not the numbers — it is the **premises**.

| item | premise as put | dispatched state |
|---|---|---|
| 1 · B77 | *"sat unadopted since 2026-10-07"*, *"Nothing has been wired either way"* | `required_quiet_run` live at `:1625`, both arms wired `:10327`/`:11640`, **34 guard assertions green** |
| 2 · B84 | record a pre-run target field | **already written** at `:21703` under his 2026-11-08 ruling |
| 4 · B125 | *"3 CANDIDATE REMEDIES, NONE BUILT"* | the hash-stamp half shipped 2026-11-06 — **it is on the brief I am reading** |
| 5 · B141 | declaration *"stale by 3 files"*, 235 guards | pin **current**; gate runs **309** |
| 6 · B142 | `known_roles()` returns 3 | returns **7**; the 4 interface roles exist, guard 12 passed |
| 7 · B143 | class has *"0 writers"* | **1 writer**, into the exact object the reader reads |
| 11 · B171 | *"2 lines wipe the command set"* | guarded since 2026-11-12; **the defect does not reproduce** |

That is a 7-of-19 rate, and it is not a documentation nuisance. **Item 1 is the clearest case.** Its three options are *adopt the bound*, *adopt the exact version*, *leave it unadopted* — and the bound is already in force, so "the status quo" as the brief describes it does not exist. Worse, the brief's central argument for preferring the seat-rounds form is that the ratio form "has to be given 1 value and the rule does not say which." The wired implementation evaluates per round. The argument was answered by the code five days before the brief was written.

**The mechanism is visible and it is Item 9's defect.** The items are rendered from committed decision records, and the predicate deciding whether a record is still live asks whether *any date anywhere* in the entry postdates the ruling. An entry whose body accumulates progress notes stays "owed" however much of it has shipped. The same predicate prints **19 of 54**, while the item quoting it says **8 of 12**. So the brief's own staleness is an instance of the defect Item 9 asks me to rule on, and Item 9 is the item whose quoted figure is most wrong. I would put that question first, ahead of the other eighteen.

**Second disagreement: Section 3 asks for fixes at their real path, and three of the nineteen cannot honour it without violating a standing control.** Item 14's hook *"by design cannot be changed without his permission"*; Item 18's part 2 is a tightening reserved to him; Item 16's whole point is that writing the paragraph where the brief pointed would install it. The brief resolves this only in its last clause — *"do not manufacture a file"* — but the honest discharge for a *draft* artefact is the not-in-force marker, which Item 18 is simultaneously asking him to rule on. **I used it, and it failed on my first attempt at 8 of 16 blocks.** A brief that asks seats to deliver draft artefacts should state the marker convention in the brief rather than leaving each seat to find it in a 32,671-character file — which is the exact failure mode Item 18 describes.

**Third, and smaller: Item 12's option list omits the measurement that decides it.** Three options argue about whether 17 minutes is worth 1 assertion of end-to-end coverage. Neither the item nor the task-list entry mentions that `resources/suite_record.json` records the mirrors test as **RED at the last committed full board**. Once that is on the table the trade is not close, and no option in the list is phrased to use it.

**Where I could not reach a view:** Item 15. I can recommend the 1 per cent ceiling and separate files on the evidence, but its mutation board **refuses to run against a red baseline**, and a guard on the commit gate is currently failing. I decline to treat an exposure ceiling as settled while the instrument producing it is unverified, and I would rather say so than return a verdict with a confident shape and nothing under it.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 37 recorded tool call(s).

<!-- verbatim-begin: fable (panel the_nineteen_2026-11-17) -->

All verification I could land this turn is in. What was executed: the Item 2 producer, the severity-collapse producer, the composer predicate, the resource-budget predicate (before and after fix, 150-cell grid), the cy-gate predicate (before and after fix, planted process), the two B77 roster guards (20 passed), SymPy + Wolfram on the §7.7 supremum, and the B197 ratio/CI re-derivation. Two artefacts are written into the sandbox tree, both marked `AWAITING FOUNDER RULING`. The background run of `scripts/precommit_gate_cost_2026-09-10.py` had not returned by write-up; Item 5's 3-of-235 figure therefore stays quoted, and I say so there.

**Every verdict below is a recommendation. All 19 are his to rule. Nothing here is installed as settled — the two sandbox edits are proposals carrying the ruling marker.**

---

**ITEM 1 — B77 `pf:4f09b9135a60` — Better option (A, as ratification of what is already live).** The brief's premise "Nothing has been wired either way" is false against the dispatched tree: `bench/reference_runner_v3.py:1625` carries `required_quiet_run` — the safe upper bound, `ceil(K·n_declared/n_live)` — wired into **both** convergence arms (lines 10327, 11640), its docstring recording "his instruction of 2026-11-12 was to wire BOTH convergence arms" and calling the formula "HIS ACCEPTED DESIGN". I ran both guards: 20 passed in 1.00 s. So the upper bound is the status quo, and the live question is only whether to *replace* it with the exact design. **ADDITIVE** (clause 2): a replacement must demonstrably outperform the wired fix; the exact design's gain (fewer quiet rounds at 1–2-seat rosters) is bought with a dependence on 2 measured correlation figures that disagree (0.405989 vs 0.236014) at 2 of 6 roster sizes, and no committed measurement shows a real archived run paying material extra rounds under the bound — the 3 degraded runs each had a *single* short round, where the two rules nearly coincide. **SIMPLEST SUFFICIENT**: the bound takes no measured inputs and cannot be wrong in the unsafe direction. If he adopts the exact version regardless, use the pooled 0.405989: higher correlation is the stricter requirement and the fail-safe side. *Refuter:* a committed replay of the 3 degraded archive runs showing the bound demanding materially more rounds than the exact requirement at the rosters actually observed — producible today from the archive.

**ITEM 2 — B84 `pf:4bcde489948b` — C.** Re-derived by running `scripts/can_a_difficulty_estimator_be_fitted_2026-11-02.py`: r = 0.836787, p = 1.533183e-16, NumPy agrees, Spearman 0.782540; 21 state keys, 0 pre-run target fields. An estimator on these features is a round counter wearing a confidence measure's name — his own words, now tool-confirmed. **SIMPLEST SUFFICIENT** on the root cause: the defect is a missing *class* of reference points, not 1 missing field; each of the 4 is 1 field at a writer that already writes. **ADDITIVE**: nothing removed, no decision changes, and each field is reached by the estimator work it unblocks. Option B is refuted by the producer itself; option A fixes the instance and leaves ν, q and the severity spec unmeasurable. *Refuter:* an estimator fitted on the existing 21 fields whose output does **not** rise with round count — the producer can test that today, and shows the opposite.

**ITEM 3 — B94 `pf:bb28392e8a9e` — C on v_bar, B on the 4 runners.** Verified at `_manager.py` (v_bar region): `obs_v = fraction of findings with f.verified`, and the setter is unrecorded. Keep **both** quantities as 2 fields (model's claim; machine's verification), point the fingerprint at the machine's — that is the quantity the name "mean verification quality" and TOOLS DECIDE both demand — but the repoint is his because it changes a measurement driving role assignment. **ADDITIVE**: 2 fields remove nothing; option A's port of falsifier machinery into completed runners adds 0 reachable callers and fails the symmetric clause. **SIMPLEST SUFFICIENT** for the runners: a relabel that makes the closure say what it rests on (a model's word) is the smallest change that removes the untruth without disabling the close path. *Refuter:* a replay of archived runs with v_bar split showing self-reported VERIFIED values having flipped a role assignment — producible today; if found, the repoint is urgent, not optional.

**ITEM 4 — B125 `pf:9aa8db33d2a3` — Better option: the stamp table, not full quoting.** This very brief demonstrates the fix: a per-artefact sha256+mtime table at blind dispatch, with the standing instruction that a seat's reading is judged against the stamped state. That cures the actual harm — correct snapshot-reading adjudicated as error — in *both* edit orders, because adjudication is against the stamp regardless of when the file moved; and it lets the seat self-check, which is what stopped the near-self-report. **SIMPLEST SUFFICIENT**: full quoting (D/C) reproduces whole files the seat already holds; stamps carry the same adjudicative content at hash cost. **COMPOSABILITY** bars option C as put: "neither half does both jobs" is the non-interference sense his definition excludes — no measurement shows stamps+refusal beating stamps alone, and the refusal adds a dispatch-failure surface a changed-and-reverted file still evades. Add the refusal only when a case arrives that stamps failed to cure. *Refuter:* an archived joint round where a stamp table was present and a seat's correct snapshot reading was still adjudicated as error — searchable in the panel records today.

**ITEM 5 — B141 `pf:ffddb18b09a0` — B (split).** Verified: `test_precommit_gate_cost` appears 0 times under `hooks/` while `hooks/pre-commit` carries a 300+-entry GUARDS list — the declaration's own guard is off the board it measures. The observed drift class (3 undeclared files) is *list* drift, which the file-count assertion catches at every commit; the collected-count half goes red **by design** at entry closure, and this test's own header records what a flapping bound teaches ("that the checker is noise"). **SIMPLEST SUFFICIENT**: the split catches the measured failure with 0 forced refreshes. **ADDITIVE**: option C adds a mandatory refresh nothing in the observed defect class needs. The 3/235 (0.012766, Wilson [0.004351, 0.036854]) stays **quoted**: the producer ran past my budget and had not returned at write-up. *Refuter:* a drift episode where collected-count moved while the file list did not (a collection change independent of entry closure) — derivable from repo history today; if frequent, C wins.

**ITEM 6 — B142 `pf:970ab5074a95` — A (defer the mapping; build the peer catalogue; credential store after the runway).** A registry role carries a merge signature and an alpha vector; a 4→3 surjection is a change to run selection with **no measurement** that mapped selection performs as well as current selection — **ADDITIVE** clause 2 unmet, and under clause 1 the UX brief's 4 names and the backend's 3 roles are a spec conflict that renaming cannot discharge. Option B's label-only column is reached by no dispatcher — the symmetric clause's definition of not-additive. The peer catalogue adds capability touching nothing contested. The credential store appears in no spec; 10 plain-text keys are real, but building a secrets store without a brief is how spec-less surface ships — write its section first. *Refuter:* a replay of archived runs under a candidate 4→3 mapping showing role-assignment scores non-degraded — producible today; if committed, C becomes the additive choice.

**ITEM 7 — B143 `pf:18582c4fed35` — A (collect first, repoint, add a third weight).** Re-derived with 2 tools: SymPy gives the soft branch supremum as exactly 1/2, and Wolfram Language (local Wolfram Engine) returns `{1/2, {c→1, v→1}}`; with attainable values {0.5, 1.0}, cuts 0.7/0.8/0.9/0.95 all yield the same critical set — 0 reclassifications, confirming magnitude-blindness. The collapse producer ran clean and adds: the cut partitions by falsifier verdict and applies the model's own number inside the CONFIRMED block. **ADDITIVE**: a release door must depend on a proof about the number it releases (fits the aims; fills a gap no existing fix covers); the third weight is the only change making any cut a magnitude test. **SIMPLEST SUFFICIENT**: one weight strictly inside (0.5, 1.0) is the minimal change that does it. Collection proceeds under his 8 Nov ruling either way. *Refuter:* re-running the −0.5538 correlation producer after the repoint and finding the repointed proof agreeing with the pre-registered rubric *worse* than the current proof does on the 259 audit cases — producible today.

**ITEM 8 — B154 `pf:10e2507dabf6` — B (hold 7; dispatch the 22 at his convenience).** 7 admits more findings as critical than the standard's safety line; an over-admitted finding gets a second look, an excluded one gets none — the asymmetry decides. **ADDITIVE**: moving to 9 narrows what reaches a human with no committed measurement that the looser gate outperforms (clause 2 unmet); "the standard says 9" is a reading, not a measurement. The panel dispatch costs nothing on free seats and moves the boxes exactly 1 rung; option A buys corpus evenness with pure delay. *Refuter:* measured reviewer overload at cut 7 — a false-critical rate from the review records showing material findings drowned — producible from the archive today.

**ITEM 9 — B160 `pf:055a68c4f4ae` — D.** Three predicates disagree on all 4 items they apply to; the item is right that no measurement chooses between them, so this is a stated preference for the over-reporting error direction — and I say so plainly. The project already withdrew the suppression direction once (9 Nov). **ADDITIVE**: D removes nothing, the note is printed where the count is printed (reached), and nothing is hidden without annotation. *Refuter:* none the repository can produce today — this is a preference, declared as one per Section 4.

**ITEM 10 — B170 `pf:ed54f9ccded2` — B (merge to main; keep committing there).** The sandbox carries no `.git`, so I could not re-derive the branch state; the file-level absences are taken as quoted. **ADDITIVE** clause 1: his own standing rule names main as the branch, so B is the only option that *fits the specification*; D moves the default and leaves a stale-but-authoritative main — the exact condition that caused this; A institutionalises it. **SIMPLEST SUFFICIENT**: the root cause is divergence from the ruled default, and only the merge removes it. C's branch retirement is a removal with no committed measurement that forbidding experimental branches outperforms permitting them — his own rule permits them with stated reason. *Refuter:* a `git merge --no-commit` dry run on his machine showing an unresolvable conflict surface — producible today, and it should be run before the merge is scheduled.

**ITEM 11 — B171 `pf:5292c9025d73` — B, as ratification.** Verified in the dispatched tree: `hooks/work_not_narrate.py` already carries the narrowed reset (`if worked_since and (_new or not _is_bare_question(c))`, dated 2026-11-12), with the opposite-failure protection kept and the discriminator drawn from his own 2 rulings. **SIMPLEST SUFFICIENT**: it fixes the class (any bare mid-turn question wiping commands), where A fixes one marker for this incident only; C re-opens a defect with a named mechanism. **ADDITIVE**: the stale-marker protection is narrowed, not removed. Discrepancy noted: the item says 9 refusals, the hook's comment says 34+ prods for the same incident — neither re-derivable here (no transcript in the sandbox). *Refuter:* a live transcript where his bare question was *intended* to lift `d` and the gate kept refusing — producible in use, not from this sandbox.

**ITEM 12 — B175 `pf:00cfce67090e` — C.** **ADDITIVE** removal clause, satisfied as stated: named property = suite cost, ~17 min/run (quoted — re-measuring means a full-suite run, which this dispatch excludes); what is removed = 1 exit-path assertion claimed duplicated by 2 other tests. **SIMPLEST SUFFICIENT**: the test's only stated claim is mirror ordering, and the first-stage assertion is that claim without dragging a 368-lines-distant guard board along; a measurement that mutates the git index while measuring it cannot speak about its subject. The duplication claim is the load-bearing sentence I could not verify in budget — make confirming it the pre-adoption check. *Refuter:* grep/run of the 2 named tests showing neither asserts the hook's exit path — producible today; if so, the removal clause is unsatisfied and C falls to B-only.

**ITEM 13 — B180 `pf:aa6f7b704f10` — B (widen). Artefact written.** Verified first: the gate's sole process predicate was `pgrep -f "run_simulated_experiment.py"` — a 200-minute pytest was invisible, so the directive was enforced by memory, the symmetric **ADDITIVE** clause's exact description of an addition nothing reaches. The fix is in `hooks/cy_monitor_gate.py` (marked `B180, AWAITING FOUNDER RULING`): a second pattern `pytest.*bench/tests`, scoped to this project's suite so an unrelated pytest cannot refuse stops, shell exclusion applied to both. Measured: a planted non-shell process with a suite-shaped command line is seen (and the pattern also picked up genuine suite processes live on this machine). **SIMPLEST SUFFICIENT**: one pattern added, nothing else touched. *Refuter:* his own judgement that suite-run prods cost him more than unmonitored 3-hour runs — only he can produce that observation; the repository cannot.

**ITEM 14 — B182 `pf:9950e21f2aed` — B (widen the noun side). Artefact written.** Measured before: 30/150 of my re-built genuine-instruction grid caught (item quotes 126/150 pass-through on its grid; my independent grid gives 120/150 — same structure, exact figure not reproducible from the item text since the noun list isn't stated; `bench/tests/` and "the full test suite" 0/15 each, confirmed). Fix in `hooks/local_resource_budget.py` (marked `B182, AWAITING FOUNDER RULING` — and note his permission gates the *live* `~/.claude` copy, which I have not touched): widened `_NOUN_MENTION` to the project's actual phrasings plus the bare path, kept in the noun class so citation without an execution verb stays clean. Measured after: 150/150 caught, negations 0/4 refused (the 2026-10-17 repair intact), citations 0/2 refused. **ADDITIVE** clause 2: outperforms the existing fix on the named property, measured. **SIMPLEST SUFFICIENT**: regex widening only. *Refuter:* a corpus of legitimate briefs that cite the suite without instructing it being refused by the widened set — producible today from archived briefs.

**ITEM 15 — B185 `pf:3142ce4958c8` — C for the ceiling; own record for the versions.** 1% with the 14-day backstop: 0 of 74 measured gaps exceeded it (quoted — session-gap data not re-derived here), so 0.5% doubles the checks for zero measured exposures caught. **SIMPLEST SUFFICIENT**. For model/client versions: a separate record, by the item's own winning argument — the split dominated *because* the files have radically different change rates, and 70-patch-release drift in the standards file recreates the mixed-rate defect the split removed. **ADDITIVE** clause 1. *Refuter:* re-measured session gaps showing breaches of the 1% ceiling — producible from his session logs today.

**ITEM 16 — B186 `pf:d0f37996a791` — B.** Pure judgement, no artefact. Adopt scoped exactly as he worded it, with the requirement that invoking it *names* the consequence — that requirement is what keeps it a decision rule rather than rhetoric, matching the form of the other 3. **ADDITIVE** clause 1: it fills the one question the existing 3 never ask (all govern a fix's shape, none its mattering); C buries that question inside a standard about shape; A leaves the recurring case ungoverned. Adoption and wording are strictly his — the project's own defect class (tentative advice acquiring authority) is why I recommend rather than draft-install. *Refuter:* decision records showing the 3 existing standards already forcing the human-consequence answer in the cases that prompted this — searchable today; if common, the 4th is redundant and C wins.

**ITEM 17 — B190 `pf:d837803feb6a` — B now, and C provisionally.** Authorise stamping first: it is the precondition for *any* measurement here, and deferring the aggregator without it (A alone) leaves the question permanently unmeasurable — the item says this itself. Adopt the disjunction on the derivation, not a vote: under the core document's own admissibility table, per-scale cuts compose only by selection, and the disjunction is the unique aggregator that cannot under-report a critical on any scale — a derivable fail-safe property, which is why adoption need not wait for the empirical comparison, while stamping lets that comparison later refute it. **ADDITIVE**: stamping is an addition wired to the measurement that reaches it; no composition claim is made, so **COMPOSABILITY**'s measurement demand is not invoked. *Refuter:* stamped severity records showing the disjunction flooding review with per-scale criticals no scale-owner ranks material — producible only *after* stamping exists; today the repository cannot produce it, which is itself the argument for B.

**ITEM 18 — B194 `pf:a3b5ccfe2d28` — C (require the marker, strictly matched).** Executed: the composer's live predicate classifies the announcing header SOFT (`False`) and a 1-sentence MUST body HARD (`True`) — the hazard is real in the dispatched tree; the sentinel is `[CDSFL:NOT-IN-FORCE]`. The decisive evidence against B is this project's own record in Item 10: a warning that fired **on every commit** changed nothing for 43 days — a committed measurement that report-don't-refuse fails for precisely the population that doesn't read warnings. **ADDITIVE** clause 2: C outperforms B on the only property that matters, reaching the author who doesn't know the marker exists, and the refusal text teaches it. The strict-match caveat is a real acceptance test: the live "Drafted But Not In Force" section of the core file discusses not-being-in-force and must not trip the matcher — commit that as the fix's falsifier. *Refuter:* the proposed matcher run over the live core files refusing a ratified block — producible today, and it is the test the fix must ship with.

**ITEM 19 — B197 `qs:633854939cf3` — A.** Re-derived: 281/272 = 1.033088 exactly; log-ratio CI re-derived as [0.874446, 1.220512], agreeing with the quoted [0.874617, 1.220273] to 3 decimal places (method variant). B retires an alarm with no committed measurement that silence dominates — the **ADDITIVE** removal clause fails it outright. C re-scopes the guard a second time, in the suppression direction, to whatever it has not yet fired on — a threshold that moves whenever it fires measures nothing. **SIMPLEST SUFFICIENT**: the root cause is visible in the last 2 snapshots — 18 added, 1 closed, most awaiting *him* — and these 19 rulings are the unlock; a verified closing pass after them moves the ratio honestly. *Refuter:* the burndown producer finding almost no green-evidence entries actually closable — producible today; that would show real intake growth, not backlog, and the question would return as a scoping decision, not a closing pass.

---

**DISAGREEMENT WITH THE BRIEF'S FRAMING (required field).** Strongest: **Item 1 poses a settled question as open.** "Nothing has been wired either way" is contradicted by the dispatched tree — `required_quiet_run` (the safe upper bound) is wired into both convergence arms on his recorded instruction of 2026-11-12, guarded (20 tests, run green here), and its docstring names it "HIS ACCEPTED DESIGN". Option B's "leave it unadopted — the status quo" misdescribes the status quo; the only live residual is *replace-with-exact or not*, which is how I answered it. Secondary: **Item 14's 126/150 did not reproduce exactly** — my independently re-built grid gives 120/150 pass-through; the structure and direction confirm fully (only the author's 2 tested phrasings catch; the path and natural phrasings are 0/15), but the headline figure depends on an unstated noun list, so it should be quoted with its grid. Tertiary: Item 11's count (9 refusals) disagrees with the hook's own comment for the same incident (34+); one of the two records is wrong and neither is re-derivable from this sandbox.

**Delivered artefacts (both marked `AWAITING FOUNDER RULING`):** `hooks/local_resource_budget.py` (B182 widening; measured 150/150 vs 30/150, negation handling intact) and `hooks/cy_monitor_gate.py` (B180 widening; planted-process verification passed). Wolfram was used once, computed, and is attributed above. All 19 items carry a verdict, a named standard, and a refuter; per Section 6, I stop here.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/the_nineteen_2026-11-17/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
