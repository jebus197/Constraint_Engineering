# DECISIONS AWAITING YOU, 1 November 2026

2026-11-01 16:55 GMT. Written under note standard v1.9, which you ruled into existence today. Every item below says what it is, what it affects, what you decide, and what is recommended and why against the 3 formal standards. No item is named by its code alone.


## PART 1. WHAT YOU HAVE ALREADY SETTLED TODAY, SO YOU ARE NOT ASKED TWICE

There are 14. None of these needs another word from you.

The role assignment shape. You accepted the panel's recommendation of 2 dimensions and 1 layer. The structural half is built and folded back.

The revised severity design. You approved it. What the panel found is in part 3.

The secondary falsifier pass. On by default, a secondary may never change a verdict, and the 3 configurations that have no secondary stay as they are. All 3 are now pinned by a test, because all 3 were already true and a ruling that merely confirms the current state leaves nothing behind.

The proof checking module written by a panel model. Fixed and folded back.

The type checker. Enabled as its own task, kept out of the commit check, with a baseline now measured: 704 files checked, 1,050 findings about this project's own code across 276 files, and a further 1,205 errors that are missing stubs for other people's libraries and are reported separately rather than counted against us. The ratchet is per file, so a fix in one file cannot pay for a new error in another. Clearing 1,050 is a batch programme, which is what you asked for. A correction you should have: my stated reason for this task was wrong. I said the checker silently treated project symbols as untyped; it does not. What it actually did was stop running after the second file, which is why it had been reporting almost nothing.

The brief template wording on composability. Replaced with your own definition, and the weak form is now refused outright.

The fourth convergence condition on residual risk. The difficulty estimator comes first.

The 9 explanations owed. Retired. Nothing remains owed.

The bare entry code check. Built, scoped to the documents you read and binding only on files first seen from today.

The proof and falsifier definition. Written, and the useful result is in part 4.

A new ticket category for a statement that needs acting on. Built as the 6th kind, and both of your uses of it have been reclassified from discussions.

The note standard at version 1.9. Locked, with 2 enforced rules and 1 stated honestly as unenforced.

Closed issues being re-presented to you. Fixed, in 4 places, 1 of which was data rather than code.

The blocked run. Fix the routing and re-run on the current gate, not on the revised severity design. Scoped in part 5.


## PART 2. WHERE YOU WERE RIGHT AND MY FILES WERE WRONG, MEASURED

There are 4 corrections, all mine.

The decision count. You said 10 decisions sounded suspiciously high. It was. There were 4 different counts of a single quantity in front of you at the same moment, 3 of them inside the same file: the morning report's prose said 4, the numbered list under that section's own heading promising they were yours held 10 items, the generated half said 5, and the message left for you at 04:51 named 5 entries. The measured answer was 3. The membership was wronger than the count: the list of 10 omitted one of the 3 entirely, included 1 you had ruled on 30 October, and carried 6 items that were mine.

The unapplied model designs. I told you there were 44. The inventory looked for files named falsifier while the panel models had named theirs falsify, so 5 of 41 distinct paths were counted as unadopted designs when they are evidence by design. Corrected: 39 absent new modules plus 1 changed version of a real file. Another 5 paths were written twice, once by each of 2 models, so the number of distinct ideas is lower again.

The configurations without a secondary falsifier. I wrote 2. Measured over the live manifest there are 3.

The claim that a panel brief was truncated. That was my error and I had already withdrawn it on 31 October, but you were still asking, which means the withdrawal did not reach you. The brief the models answered carried your question complete, through to its closing question mark, along with your worked contrast and your point that severity depends on the complexity of the topic. The truncation was 4 characters missing from my own quotation in a later brief, after which I asserted that your record was cut off. Verified against the artefacts rather than against my own earlier report.


## PART 3. WHAT THE MODELS SAID ABOUT YOUR SEVERITY DESIGN

They vindicated it, and then found a trap in it that matters more than the vindication.

Your definition does not describe what the current cut measures. Your words, the chance a flaw survives a number of passes under scrutiny, are a verbatim statement of the residual risk quantity already in the mathematical model. What the code calls severity is materiality: how bad it would be if the flaw shipped. There are 2 load-bearing quantities sharing 1 word, and on paired archived entries they anti correlate, at the same sign and significance across 3 independent scans of different sizes. So the answer to your charge is not to defend the cut at 0.7. It is that 0.7 was never a bound on residual risk, and residual risk has never gated anything.

Where it should go. Both models said residual risk should gate, as an added 4th condition beside the decay curve, the consecutive quiet rounds and the contested check. Never a substitute. The decay curve is untouched in every reply and the 2nd model says so explicitly.

Your worked contrast is computable from the shipped model. The attractor equals the base flaw rate of 0.05 divided by the detection power on the question, derived rather than chosen, confirmed in symbolic algebra and independently by the local Wolfram Engine. At the shipped base rate of 0.05, a detection power of 0.95 gives 0.0526, which is your easy arithmetic case; a power of 0.05 gives 1.0, saturated, which is your hard mathematics case. I reproduced every value exactly.

And the trap, which is the most valuable thing the round produced. The joint model refused both blind models' boundary formulas. The boundary written in the mathematical appendix is unbounded below and reaches 3 times 10 to the minus 10, while the shipped code returns 5.26 times 10 to the minus 2 on identical inputs. That is a gap of 8.2 orders of magnitude, structural rather than numerical. A constraint solver returns unsatisfiable for a gate asked to fire on a bound taken from the appendix. A boundary stated in appendix coordinates would mean the gate silently never fires.

Why it cannot be switched on today. The difficulty term never varies per question, because the field it would come from has no writers in the live tree. Over 1484 archived entries, a threshold at 4 times the floor blocks every entry, at 8 times it blocks 12.6 per cent, and at 10 times and above it blocks none. No multiplier discriminates, because residual risk carries no difficulty signal to discriminate on. That is the same finding as your fourth convergence condition needing the difficulty estimator first.


## PART 4. WHAT A PROOF IS, AND WHY IT NEEDED ITS OWN STEP

You ruled this follows from the code, is mine to write and yours to ratify. It is written into the glossary, and the useful result is a single word: polarity.

A falsifier succeeds by failing. A proof succeeds by holding. A falsifier that raises has demonstrated the defect; a proof that raises has demonstrated nothing. So the existing convention, under which a run that does not fail means the defect is absent, reads a correct proof as a refutation. That inversion is the whole reason a printed proof needs its own step rather than reuse of the falsifier path.

There are 2 things measured rather than assumed. The re-verification already works on prose: run against all 5 prose fixtures it returns a confirmation on 5 of 5 pristine documents across structural engineering, statistics, metrology, algorithms and numerical analysis. What is missing is the input, because the specialist dispatch reads a fragment scraped from a finding's description and never reads the model's derivation.

And the fold-back found its own hole. Under proof polarity a clean exit grants admissibility, so a proof with no assertion at all exited cleanly and was reported admissible. A model could have printed 1 harmless line and had its repair admitted. The sentence the code wrote in that case, that its own assertions held, is vacuously true of a proof with no assertions. It is closed by requiring an assertion, and deliberately not by reusing the existing predicate elsewhere in the tree, which accepts a bare import: right for deciding whether a block is code, wrong for deciding whether a clean exit means anything.


## PART 5. THE DECISIONS THAT WERE STILL YOURS, AND YOU RULED ALL 5 THE SAME NIGHT

There are 5. One of them is a permission rather than a design, and 1 more depends on that same permission.

### **RULED 1. WHETHER A CLASSIFIER NAMES A SEAT POSITION OR A FUNCTION

What it is. The project has 2 separate vocabularies that both get called a role. The 1st describes what a model does on a task. The 2nd describes where a seat sits in the dispatch topology. You have settled that these are 2 dimensions expressed in 1 policy layer, and that is built. What is not settled is which of those 2 dimensions a classifier belongs to.

What it affects. The functional layer cannot be built until this is decided, because its membership is the answer. Both panel models said independently that the code cannot settle it: it is a definition, not a measurement.

What you decide. Function, or seat position, or defer the definition and take only the structural half.

Recommendation, and why. Function. The other member of that axis, worker, is plainly a function, and reading classifier the same way leaves the topology axis free to say where a seat sits without competing for the same word. This is additive, because both vocabularies survive and no value is lost from either. It is the simplest sufficient answer, because it is a definition plus the alias normalisation already written and tested, not a new mechanism. No composability claim is made, because no second change was measured against it.

### **RULED 2. WHETHER THE UNADOPTED MODEL DESIGNS ARE WORTH HARVESTING

What it is. Panel models write fixes and new modules inside their own sandboxes during reviews. Those that were never applied now number 39 absent new modules plus 1 changed version of a real file, after the counting error in part 2 was corrected. You asked whether the fixes are good and whether we should implement them.

What it affects. Nothing is blocked on this. The question is whether value is accumulating unused.

What you decide. Triage the remainder for value, or keep the inventory running and decide named cases on their merits.

Recommendation, and why, and this reverses what I told you this morning. Keep the inventory running, but do not treat the store as archaeology either, because the 2 cases decided today were both worth folding and both found defects nobody was looking for. Folding the role repair back exposed a test constructing a model seat with no role at all, which would have matched no role keyed predicate. Folding the proof checker back exposed the clean exit hole. So the rule I now recommend is narrower and better founded than either option as originally put: fold back the designs attached to decisions you have actually made, and leave the rest inventoried. That is additive, since nothing is discarded, and simplest sufficient, since it spends effort only where a decision has already created a use for it.

### **RULED 3. THE SHARED SCOPE QUESTION BEHIND THE 4 DIRECTIVE COMPOSITION DEFECTS

What it is. There are 4 confirmed defects in how the project's own directives are assembled for a model: every model receives a reduced rendering that is a dump of configuration flags rather than prose; the de-duplicator treats a short line as a duplicate of a longer 1 and keeps the earlier of the 2, so a formula was deleted and its special case kept; the conflict detector recognises 4 topics and returns nothing for everything else, so both sides of a contradiction survive; and the coherence pruner deletes text to bring a density figure under budget while its numerator comes from a structure that pruning cannot touch, so density rises with every prune.

What it affects. 4 entries wait on this 1 answer and nothing else. Answering it releases all 4.

What you decide. Repair all of them, repair only the ones that mislead a model, or record them and stop.

Recommendation, and why. Repair 2 and record 2. The de-duplicator and the conflict detector both silently change what models are told, which is the fault class this project exists to catch. The coherence pruner is proved unreachable on 2 tools and is already switched off on both code paths, so repairing it changes no behaviour today. The configuration dump is a presentation question the coming interface work will revisit anyway. That split is simplest sufficient, because it spends repair effort only where a model's input is actually corrupted, and additive, because the 2 recorded defects keep their measurements and their entries rather than being closed.

### **RULED 4. PERMISSION TO MODIFY MY OWN STOP HOOK

What it is. You ruled that the automatic form of the save should refresh local resources without pushing, while the manual form commits and pushes. I built the design and could not install it. The automatic half lives in a Stop hook under your Claude configuration directory, and the harness refused the edit as self modification. The repository copy is not a second file: both paths are hard links to a single inode, which a test asserts deliberately, so writing the repository path would be the same write by another name. I did not do that.

What it affects. The automatic local save does not exist yet. Everything else about saving works: the manual command commits and pushes, and the gate that notices a long gap is live and correctly quiet.

What you decide. Grant permission for that one file, or apply the change yourself from the description, or leave the gate as it is and accept that the local reference resources refresh only when a manual save runs.

Recommendation, and why. Grant permission for that one file. The change is small and it only adds: it regenerates the generated state file, the memory ledger and a session summary, and it commits nothing, so nothing half finished can reach the permanent record, which was your reason for splitting the 2 forms. Simplest sufficient, because the alternative is that the detailed project memory you described is refreshed only when I remember to ask for a full save, and the record of today shows that is exactly what was missed last night.

And a last note on your phrase. Saving work locally admits 2 readings: a local commit, or a refresh with no commit at all. The mechanics choose the second: a local commit would run the commit check, which is 120 guard files and about 8 minutes, at every turn end. If you meant a local commit, say so and I will find another way.


### **RULED 5. WHETHER TO LOOSEN THE GATE THAT HOLDS ME TO MY OWN 5-STEP CYCLE

**What it is.** A gate checks, at the end of every turn, that the consequences of a change were traced before anything was touched. It searches a window of the transcript anchored at the first edit of the turn. On a short turn that is correct. On a long unattended turn, every cycle after the first can never satisfy it, because the evidence for the second cycle necessarily sits after the first cycle's edit.

**What it affects.** It refused 4 times in a row last night, always naming the same files, on turns that had each done the tracing it was asking for. A gate that cannot be satisfied stops carrying information, because the only way past it is to ignore it, and once it is ignored a real refusal is ignored with it.

**What you decide.** Anchor the window to each cycle rather than to the whole turn, or leave it exactly as it is.

**Recommendation, and why.** Anchor it per cycle. This one is proved rather than observed: z3 returns unsatisfiable for the condition after the first edit and satisfiable for the passing condition, and SymPy gives the witness. The fix moves 1 window boundary and nothing else, and the gate keeps every step it checks today, so it only adds. A caveat: that gate is the same kind of file as the one in decision 4, a hook in your configuration directory hard linked into the repository, so granting decision 4 grants this as well, and declining it makes this one yours to apply. Entry B63, the first-anchored FOLLOW window; the proof is `scripts/a_first_anchored_window_is_unsatisfiable_2026-11-01.py` and the measurement of the live gate is `scripts/follow_is_credited_only_before_the_first_edit_2026-11-01.py`.

## PART 6. THE 2 ITEMS YOU ASKED ME TO EXPLAIN, IN PLAIN ENGLISH

You said you do not know what these are or why they are deferred. Both are deferred by your own earlier decisions, and both carry a question raised after you deferred them, which is why they surfaced again.

### ADMITTING A MODEL TO THE HARNESS IS NOT TRIVIAL, AND THE COST IS SILENT DEFAULTING

Your question, from 16 October: adding, removing or changing models should be entirely trivial by design and should not require major code changes, and is it. The answer has 2 halves. The number of edits is modest: 12 per model tables across 6 live harness files, plus 1 registry file. The failure mode is not. A model that does not exist was put through the real resolution chain, and of 7 steps, 5 default silently and only 2 fail loudly. A researcher who misses 1 table gets a seat that runs while being quietly wrong.

The prerequisite is built: a missing registration is now named rather than defaulted. What is still yours is whether to consolidate to a single registration point, and specifically whether a missing registration should raise, refuse to dispatch that 1 seat, or fail at a run level pre-flight check. That changes how every seat is configured, which is why it was not done unattended. You deferred it on 17 October.

An aside that is now relevant: the defect class this entry is about is exactly what folding the role repair back exposed today, in a test that built a seat with no role at all.

### THE ORCHESTRATOR MODEL BOUND INSIDE THE HARNESS

Your specification, from 17 October, quoted because it is the design: "the role of the orchestrator model within the harness should be more or less identical to your current role outside of the harness, when you monitor experiments under our full cy protocol, so that it could run largely autonomously throughout an experiment (using the full machinery of the harness to compute its work), until an experiment completes. It would also serve as the primary interface for experiments, where researchers could enter instructions, discuss changes, monitor experiments as they run and to discuss any findings when they complete." You added that the classifier aspect becomes doubly useful once fixes fold back at the close, because something must then decide which fixes are better, which compose, and which meet the 3 formal standards, and that this is not model voting but, in your words, "more akin to the simple classifier work already done by Haiku".

You also set its priority yourself, on the same day: "I do not wish you to become too sidetracked on this specific issue. It should be built and tested at the appropriate time. But there are clearly many other issues that have yet to be addressed in your outstanding task list before we get to this." That is why it is recorded rather than built, and the recording was the fix for a real omission, because my discussion of 16 October had not touched it at all.

What is still yours is 1 placement question only: the shadow arm immediately after the 1st stage replay exit test, which is free and the nearest actionable point, and the live bound arm after the merge to the canonical branch and before the 3rd stage capstone.


## PART 7. WHAT IS BUILT BUT NOT YET SCOPED, AND WHAT IT NEEDS

There are 2 pieces of your work still unbuilt, and both are substantial builds on live experimental machinery rather than tidying. I am naming what each needs rather than starting them at the end of a long session.

The difficulty estimator. The fourth convergence condition cannot discriminate until the difficulty term varies per question, and the field it would come from has no writers in the live tree. Building it means deciding how difficulty is estimated per question and wiring it into the residual risk recursion, which changes what every run computes. The measurement that justifies it is already committed.

The routing repair is ALREADY BUILT, and only the re-run is left. You told me to fix the routing and re-run. I checked before building anything, and the fix landed on 12 October, 9 days after the run that blocks. The run blocks on 2 entries whose falsifiers are empty, so the proof half of the release can never be satisfied, and the fault in those 2 is that nothing ever served them rather than that they were rated wrongly. Calling the live predicate on both of them today returns admit, so the ladder would serve them now. It is wired rather than merely present: 4 call sites, 1 of them the dispatch admission itself, with its own test green at 4 passed. So there is no code left to write here, and what remains is the re-run, which costs your machine real time. It should start when you are at the keyboard, and it will run on the current gate rather than the revised severity design, for the reason in part 1.


## PART 8. DECISIONS STILL YOURS, AFTER ALL 5 RULINGS, AND WHY NEITHER IS A REPEAT

Added 2026-11-01 23:56 GMT. You answered all 5 of the decisions above that evening. 2 of those entries turn out to carry a SECOND question that your ruling did not reach, and they are set out here rather than folded into the 5, because asking you again for something you have settled is the failure this file exists to prevent.

How these 2 surfaced is worth a line. I marked both entries settled on your rulings, and a guard refused it. The guard exists because a ruling date must never silence a question raised after it, and it was right both times: 2 of the 7 items I released were released wrongly. Neither was caught by me.

### DECISION 1. WHETHER MODEL REGISTRATION CONSOLIDATES TO A SINGLE POINT

What it is. Adding a model to the harness touches 12 per-model tables across 6 files. The measured behaviour is much better than the entry's own headline says: of 10 steps in the live resolution chain, 0 now default silently, 8 announce their default and 1 fails loudly on a missing file. What no step does is REFUSE the run, which is what you ruled on 1 November it should do.

What it affects. How every seat is configured. Consolidating to a single registration point is the second half of that entry, and a single point that still defaulted silently would hide 12 misses behind 1.

What you decide. Whether registration consolidates to 1 point now, or whether the refusing pre-flight you ruled for is enough on its own for the time being.

Recommendation, and why. The refusing pre-flight first and consolidation afterwards. The pre-flight is additive and cannot change what a passing run does, so it is the simplest sufficient step; consolidation changes every seat's configuration and should follow a run that proves the pre-flight catches what it should.

### DECISION 2. WHETHER THE AUTOMATIC SAVE SHOULD COMMIT LOCALLY OR ONLY REFRESH

What it is. You granted permission for the save hook on 1 November and it has been used. The entry records a second thing as owed: confirmation of how the automatic save should behave. My design refreshes local reference files and commits nothing, on the reading that your ruling separated an automatic local refresh from the manual form that commits and pushes.

What it affects. Whether anything half finished can reach the permanent record automatically.

What you decide. Confirm the refresh-without-committing reading, or tell me you meant a local commit, in which case the design changes.

Recommendation, and why. Refresh without committing, which is what is built. It was your own stated reason for splitting the 2 forms, and it means an automatic save can never put an incomplete state into history.

## PART 9. WHAT THIS FILE DELIBERATELY DOES NOT REPEAT

The zero plant control is not put to you again. It is scheduled on the runway with its gate stated as something checkable, and the only outstanding part is the money, recorded once.

The severity gate, the integrity carve out and the proven floor are not put to you as questions. You ruled all 3 and the answer to each was whether the work was done. It was.

The 9 explanations are not listed. They are retired on your ruling, each recorded with its own date so the record still shows it was asked.

Every figure above has a producing script committed beside it, named at the point the figure is used. The decision count comes from a script that classifies every live entry from the entry's own text, proves the dependency graph acyclic in a constraint solver, and cross checks every interval in 2 independent implementations.


---

## TECHNICAL APPENDIX — the paths and the producers the spoken version leaves out

Added for the markdown companion only. The spoken file names no paths by design.

### What was built today, with its guard

| what | where | guard |
|---|---|---|
| Note standard v1.9, Rules 32 to 34 | `scripts/note_vagueness_lint.py` | `bench/tests/test_the_note_standard_v19_is_enforced_2026-11-01.py`, 17 tests |
| `stm` as the 6th ticket kind | `bench/ticket_store.py`, `scripts/harvest_tickets_2026-10-17.py`, `scripts/read_founder_responses_2026-10-11.py` | `bench/tests/test_every_kind_is_reachable_by_a_reader_2026-11-01.py`, 6 tests |
| The decision list's 4 faults | `scripts/morning_report_build_2026-10-12.py` | `bench/tests/test_a_settled_item_is_not_a_decision_2026-11-01.py`, 8 tests |
| His 3 secondary-falsifier rulings, pinned | `bench/falsifier_pairing.py`, `bench/immune_agents.py` | `bench/tests/test_his_secondary_falsifier_settings_are_pinned_2026-11-01.py`, 6 tests |
| The brief template's composability wording | `scripts/panel_brief_validate.py` | `bench/tests/test_the_brief_template_states_composability_his_way_2026-11-01.py`, 7 tests |
| The 9 explanations retired | `experimental_notes/data/explanations_superseded.json` | the generator reports 0 owed |
| `bench/proof_verify.py` folded back | `bench/proof_verify.py` | `bench/tests/test_the_proof_verifier_is_folded_back_2026-11-01.py`, 18 tests |
| The role resolver folded back | `bench/experiment_11_orchestrator.py` and 3 files under `bench/tools/` | `bench/tests/test_the_role_literal_is_enforced_2026-10-31.py` and `bench/tests/test_the_structural_role_vocabulary_cannot_fork_silently_2026-11-01.py`, 22 tests across 3 files |
| The phantom-entry checker | — | `bench/tests/test_a_bold_span_cannot_mint_a_task_entry_2026-11-01.py`, 4 tests |
| The proof and falsifier definitions | `docs/GLOSSARY.md` | — |
| A save postcondition naming a file that does not exist | `scripts/sv_postconditions.py` | `bench/tests/test_sv_postconditions_gate_2026-09-20.py`, 27 tests |

### Mutation results

Every repair above was attacked: 4 of 4 caught on `how_many_decisions_actually_need_him_2026-11-01.py`, 4 of 4 on the v1.9 rules, 4 of 4 on the kind vocabulary, 4 of 4 on the decision list, 4 of 4 on the brief template and the retirement, 3 of 3 on `bench/proof_verify.py`, 4 of 4 on the role resolver, 3 of 3 on the save postcondition. Each harness replays the bytes it found and asserts the subject byte-identical afterwards, never restoring from git, because a mutation harness is always pointed at work written minutes earlier.

### Figures with their producers

- The decision count, the dependency graph and the suppression finding: `scripts/how_many_decisions_actually_need_him_2026-11-01.py`
- The unapplied-fix inventory, corrected: `scripts/how_big_is_the_unapplied_fix_store_2026-11-01.py`
- The secondary-falsifier coverage, 27 of 30 with an independent secondary: `scripts/the_secondary_falsifier_rule_2026-10-31.py`
- The commit gate's reach, 120 files of 747, so 636 reached only by a full board: `scripts/precommit_gate_cost_2026-09-10.py`
- Whether any panel brief is still outstanding, 7 of 7 dispositioned: `scripts/is_any_panel_brief_still_outstanding_2026-11-01.py`

### The severity figures, cross-verified

The attractor `R* = nu_b / q` holds in SymPy and in the local Wolfram Engine independently. At `nu_b = 0.05`: `q=0.95` gives `1/19 = 0.052632`; `q=0.50` gives `0.100`; `q=0.30` gives `1/6 = 0.166667`; `q=0.05` gives `1.0`, saturated. The appendix-versus-shipped gap is `log10(5.263158e-02 / 3.188776e-10) = 8.217622`, agreeing in mpmath and SymPy to 1e-9. z3 returns `unsat` for a gate firing on an appendix-derived bound.

### `canonical_role`, formally verified

Idempotent over all 5 resolvable spellings; z3 `unsat` on any alias pointing outside the declared set; total on the domain and refusing all 6 off-domain spellings including `worker`, `classifier` and `orchestrator`, which is correct because mapping them is policy; and 0 of 13 undeclared role literals remain in live code by AST scan, Wilson 95% [0.000000, 0.228095].

### Commits

`df76ebe0`, `8fd4b688`, `0a0f4ced`, `b26462fc`, `e90f1dbf` and the batches still in the gate at the time of writing. Branch `sim/shakedown-2026-09-29`. **Public `main` remains 478 commits behind this branch**, so none of this is visible in the public repository until it is merged, which is the founder's to authorise.

Written under CDSFL note standard v1.9 (1 November 2026).
