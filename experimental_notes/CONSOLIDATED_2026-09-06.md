# CDSFL consolidated report, Sunday 2026-09-06, evening. All unsupervised work from your answer file.

READ PARTS 1 AND 7 FIRST. Part 1 is what changed in the runner and its gates. Part 7 is what still needs you. Everything else is evidence and can wait.



## PART 1. THE 3 CHANGES THAT MATTER

THE MODEL VOTE IS OUT OF THE CONVERGENCE GATE. Decision 23, your words: there are no votes in CDSFL. The fail safe that decides whether a run may converge was reading a severity number, and that number is assigned by the model that filed the finding. It was a vote wearing a number's clothes. It now reads whether a tool actually returned a verdict, which is a fact rather than an opinion. Both panel seats reached that same replacement independently.

I checked it cannot cause a false convergence rather than arguing that it cannot. Replayed across 87 archived reports, the new rule blocks more often in 36.8 percent of them, identically in 63.2 percent, and less often in 0 of 87, with an interval from 0 to 4.2 percent. Convergence can only become harder, never easier.

That change then exposed a second vote one level down, which I would not have found by looking. Three existing tests failed and they were right to fail: one asserted that demoting a severity number cleared the block. Severity calibration is a model adjusting a model's number in order to open a gate. That is the same vote. It still runs, still records what it changed, still orders the queue. It no longer decides convergence. Worth knowing because you commissioned that feature only 2 days ago, and this narrows what it does.

THE SANDBOX WAS NOT A SANDBOX. Decision 35, which you called a containment fix rather than a preference. The throwaway copy used for falsifier checks mirrored every neighbouring file as a link back into the real repository, and links are transparent to writing. A falsifier that wrote to a neighbouring path modified the real working tree. I reproduced it: one write, and the real file changed. The old note said deletion could not escape the sandbox, which was true, and about deletion only, which is what made it look safe for so long. Panel agents were separately caught editing the repository during runs twice, so this was not a theoretical route.

Fixed by making the sandbox a real copy rather than a set of links, using a filesystem clone that costs 2.77 seconds on this 683 megabyte repository. Where a clone is impossible it now refuses to build rather than quietly building an unsafe one. My own first attempt broke 5 existing tests and the falsification pass caught it.

A CORRUPT NUMBER SCORED AS A PERFECT RESULT. Decision 18. The risk calculation defended itself by clamping inputs into range, but a not-a-number value passes that clamp as though it were the maximum, because every comparison with not-a-number is false. So a corrupt fix-efficacy scored as a perfect fix. Executed before the change: a not-a-number input and an infinite input both returned exactly 0.3666666666666667. Non-finite values now resolve to the cautious end of every range instead: unknown risk is maximum risk, unknown detection detects nothing, unknown efficacy fixes nothing. Strictly stricter, so it cannot manufacture a convergence.



## PART 2. THE RUBRIC RESULT, WHICH DISSOLVED THE PROBLEM RATHER THAN SOLVING IT

Decision 2 sent the rubric question to the free seats. Both refuted the premise of my own brief and agreed with each other.

The 45.56 percent disagreement between the rubric and the 0.7 number is real and is not a disagreement. All 259 judgeable cases sit inside the band from 0.65 to 0.74, so the audit is a boundary sample by construction and says nothing about the number's behaviour anywhere else. Inside that band the 2 are not diverging, they are unrelated: kappa is minus 0.0227 and the Fisher exact p is 0.78, where pure independence would predict 44.55 percent disagreement against the 45.56 measured.

The cause is measurement noise in the severity number itself. Using 273 pairs where 2 different models scored the same defect, the noise in that number has a standard deviation of 0.1419. The band is 0.09 wide. The gate is asking for finer resolution than the instrument possesses. Same defect, 2 models, opposite sides of the line: 82 of 273, or 30.04 percent. A simulation using only that noise figure, with nothing fitted to the audit, predicts 45.58 against the measured 45.56.

Two alternative explanations were killed rather than assumed away, which is why I believe it.

The consequence is good news: the 0.7 cut is not the fault and does not move, so no new dated pre-registration is engaged and there is no book-cooking exposure. And the 91 findings with no executable falsifier are actually 4: 85 predate the field existing, 2 were settled by a merge, 4 are genuine. Our own committed reproducer confirms that split exactly. All of this is now recorded in the mathematical appendix.



## PART 3. YOUR QUESTION 52, ON GROK AND THE DOCUMENT SWEEP

You asked how the recent work changes Grok's observations, and whether it changes any claims in our documents.

Grok's account was that CDSFL deliberately refuses to manufacture competence the user does not have, because tool-backed admissibility and mechanical falsification sit in the critical path, so an incompetent user is subjected to the same discipline as any other node. That description remains accurate about the design, and I think it is the sharpest external statement of the project's intent that we have.

What the recent work changes is not the claim but its warrant. Three findings in 48 hours all have the same shape: something that looked like a tool decision was actually an opinion in disguise. The severity float gating convergence was a model vote. The fix acceptance threshold was a formula that was not the break even of the model it claimed to implement. And the universal directive was telling every model a false thing about our own mathematics. So the honest position is that Grok described the architecture correctly and the implementation had not yet caught up with it in at least 3 places. It has now caught up in those 3.

That sharpens the principle rather than weakening it. The garbage in, garbage out stance requires a second clause: it is not enough for a tool to be in the critical path, whatever sits in that path has to actually be a tool. A number produced by a model and then treated as measurement is the most dangerous object in a system like this, precisely because it looks like the safeguard rather than the risk. That belongs in the founder's notes, and it is the strongest argument for the discipline you have been enforcing.

On the documents: no outward claim needed retracting. What changed is that the appendix now records the severity account honestly, and the 5 stage lineage no longer claims to be a chain of strict generalisations when 1 of its links is a change of coordinates. Both are corrections toward precision, not away from the project's claims.



## PART 4. EVERYTHING COMPLETED

Decision 7, a missed canary does not block convergence. Recorded in the module where the open question was stated, and closed rather than deferred.
Decision 13, the temporary worktree, removed after checking. It held an empty cache directory, which my first scan missed.
Decision 18, the 2 footnotes. One was already fixed. The other was not, and is described in Part 1.
Decision 22, the 6th panel seat, dropped from the 3 canonical definitions. Historical records keep their wording because they describe runs that happened.
Decision 23, the severity vote, described in Part 1.
Decision 30, the routing pattern. This was more than a character class: 2 live copies existed and differed by 7 alternatives, so whether a finding was routed for mathematical checking depended on which module asked. Measured across 8709 descriptions, they disagreed on 40, which is 0.46 percent, and in every one of those the stricter module routed for checking and the other did not. Unified on the broader form, because a false positive costs a wasted check and a false negative costs an unchecked mathematical claim.
Decision 35, the containment fix, described in Part 1.
Decision 39, the old proof of concept plan, closed as irrelevant archaeology.
Decision 44, the Open Brain spot check. It immediately found something: the project label is split by case, 89 memories under one spelling and 1 under the other, plus 4 unclassified, and the filter is an exact match, so a query for one silently misses the other.
Decision 49, the rubric conflict recorded in the appendix, described in Part 2.
Decision 50, the discharge rule adopted with the scope declared before the claim, scoped to identity claims so empirical fits keep their existing vocabulary.
Decisions 14, 17, 19, 20, 24, 28, 29, 31, 34, 36, 37, 38, 42, 43 and 46, all marked on the runway or in the study programme at the points you named, across 4 horizons.
Your 8 questions, all answered in the earlier round up.
And the answer key checker, which was not on your list at all, described in Part 5.



## PART 5. THE ANSWER KEY CHECKER, WHICH WAS NOT ON YOUR LIST

While verifying decision 10 before writing you commands, the checker that guards the answer keys reported all clear while 29 plaintext key files sat on disk, 27 of them answer keys for exams that have never run. It was blind twice: it matched a filename pattern that matches none of the real files, and it excluded the folder they are in. The arc sequencer halts unless that check reports clear, so a false all clear does not merely misinform, it lets an experiment arc start with the answers readable. And the command I had given you would have sealed nothing while printing success.

Fixed, with 7 tests built on a throwaway home directory so they test the script rather than this machine. A second, latent fault surfaced while testing: with an empty legacy list the script exited silently with no output at all.



## PART 6. WHAT I DID NOT DO, AND WHY

Decisions 3 and 51 both concern experiment 52's planted set and the re-authoring of its target. That is answer key material, and you held the answer key work for your return, so I held these with it rather than deciding the boundary myself.

Decision 4, keeping reviewer write access and measuring disclosure instead, needs the measurement built and I did not start it.
Decision 16, supplying 17 fixes, repairing 11 equipment cases and recording 4 containments. Not started. This is the largest remaining piece.
Decision 25, recording the archive decryption instructions. Not started, and it touches key handling, so it sits naturally with the sealing work.
Decision 27, authoring the 5 prose targets. Not started.
Decision 32, the materiality review against true claims. Not started.
Decision 15, the description truncation. The code is already fixed. What remains is archived damage, 13.19 percent of stored descriptions truncated at 200 characters, and a repair tool exists. That needs your word because it rewrites archived records.



## PART 7. WHAT NEEDS YOU

One. Which way to seal the answer keys: fold the 29 files into the vault's own store as a single archive with a single passphrase, or seal that directory separately. I recommend folding, because 2 archives means 2 passphrases and a second thing to forget. Say which and I will give you commands tested against the real directory.

Two. Whether to run the description backfill across the archive. It repairs real damage but rewrites archived records, so I want your word rather than my assumption.

Three. Severity calibration is now inert for convergence, as a consequence of decision 23. You commissioned it 2 days ago. Nothing is broken and it still does useful work, but you should know its scope narrowed, and that the reason is that it was itself a vote.

Four. The Open Brain label split, which is a 1 line correction I did not make because it edits a records database rather than code.

Five. The simulated run is held for your return, as you instructed, along with the answer key work that precedes it.

Written under CDSFL note standard v1.7 (26 August 2026).
