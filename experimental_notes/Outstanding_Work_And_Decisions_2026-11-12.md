# Outstanding work and decisions

12 November 2026, 20:50 GMT

This document enumerates what remains open on the CDSFL project at the close of the 12th of November, separated by who can act on it. The work that requires no founder input is listed first. Every item carries its own identifier and a descriptor long enough to identify the subject without a lookup, because the founder has no access to the project ticket store.

Every figure below comes from the project's own registry rather than from prose. Of 25 open entries, 9 can be advanced without the founder, 12 need a ruling or a permission from him, and 4 carry a ruling already and may need nothing at all.

Section 6 corrects a claim the morning report of the same day made in good faith and which the evening measurement refuted. That correction is recorded here rather than suppressed.


THE WORK THAT NEEDS NO FOUNDER INPUT

9 items, all of them raised during the 12th of November and all of them mine to carry out.

1. B158, the 11 guard assertions that read source text rather than running the code. A guard dated the 11th of September counts every test that checks for a literal string inside a Python source file instead of executing it and comparing behaviour. 11 such assertions, across 9 test files written between the 8th and the 11th of November, are not in the pinned list that guard compares against, so the guard is red. The whole class is 122 assertions out of 11,240 test functions, which is 1.0854 per cent with a 95 per cent interval from 0.9099 to 1.2944 per cent. The guard's own advice is the harder of the 2 routes and it is the right one: convert an assertion into one that executes, rather than widening the list.

2. B159, the 33 memory files that nothing points at. sv reports 198 working pointers in the memory index, none broken, and 33 memory files whose names appear nowhere in it. A memory the index does not name is never loaded, so its content is inert however good it is. All 33 were written between the 30th of September and the 30th of October. The index stands at 24,108 characters against a 25,000 character loading limit, so 33 new pointers do not fit and the remedy is to move older pointers into the archive file.

3. B161, the steering chat's missing recovery path. The 4 simulated steering chats exercised choosing a domain and escalating to a dialogue, but never the case where the researcher says the classifier picked the wrong category. The founder's own design for this is quoted in the entry. 3 separable pieces hide inside it: a repair turn with a small set of phrasings, a profile that survives a restart, and a test deciding when a new query falls outside the loaded profile.

4. B162, the steering surface conflating a task's subject with its consequence scale. A small model answering as a harness seat disagreed with the orchestrator's proposer about a pooled hazard ratio drawn from 3 unlike trial sites, and the seat was right. Both answers were correct about different questions: the subject is statistics, which decides which expert encoding a seat receives, while the consequence scale is biology's, inherited, which decides what counts as a critical finding. For the 4 domains citing an external published standard the 2 coincide. For the 5 declaring no scale and the 1 declaring a composed scale they can differ, which is 6 of the 10 declared domains.

5. B163, a user preferences section in each expert encoding. The founder's proposal is that the harness should hold how a researcher prefers to work rather than re-learning it every session. The recommendation is to build the explicit user-led form first, then the character budget of item 6, and only then consider having the orchestrator propose additions for the researcher to accept or reject. That ordering is not a preference: nothing currently bounds an encoding's length, so a learned route shipped first would grow with no instrument able to see it growing.

6. B164, nothing bounds an expert encoding's length. The composer prunes optional content when constraint density exceeds a budget, and density is constraints per token, so adding characters lowers it. Proved on 2 tools: the derivative of density with respect to character count is strictly negative, and the point where density equals the budget is a floor on length rather than a ceiling. Worked case: the densest of the 10 domains, at 5,803 characters, plus 1,000,000 characters of prose, gives a density of 0.000016 against a budget of 0.01. The budget would admit a megabyte of preferences without a murmur.

7. B165, the last full suite measurement is 5 days and more than 65 commits old. The cited run is 15,904 passed and 4 failed, 37 skipped, in 8,036.30 seconds, on the 7th of November. The gap is not those 4 known failures, which were triaged at the time. The commit gate runs a named guard list plus every test file dated the 29th of October or later, which is a sixth of the suite, so a guard outside that board drifts in silence. That is exactly how 2 guards came to fail undetected since the 8th of November. 1 clean full run closes it, at a cost of about 2 hours and 17 minutes of the founder's machine.

8. B166, the session state guard cannot see a 4 digit test count written without a thousands separator. The effect today is nil, because the paragraph concerned carries 5 other figures and names its producers. The latent effect is that a paragraph whose only figure is a plain 4 digit count would pass the producer rule without ever being examined, so the rule would be silent rather than satisfied.

9. B167, the narrated morning report goes stale within hours. Checked against the live record the same evening, 7 of 9 claims in the 12th of November report are superseded or were wrong when written. The decisions half is already generated from the registry and cannot go stale, so the staleness is confined to the narration. The proposal is to keep the narrated report as a dated account of a window and make the standing spoken deliverable the generated decisions file plus 2 generated lists.


THE 3 FEATURE REQUESTS, WITH THEIR OWN TICKET IDENTIFIERS

These were raised on the founder's instruction of the 12th of November and carry the feature request kind, which matters because the project rule is that a feature request stays open until implemented, merged or rejected, and that only the founder may reject such a request.

1. B161, ticket 6dc871eb0d25. The steering chat's recovery path when the researcher disagrees with the classifier, and a profile that persists across a restart. This is the founder's own design and his words are quoted verbatim in the entry.

2. B162, ticket 52d3a212c327. The steering surface must resolve and record both the task's subject domain and its consequence domain.

3. B163, ticket 1d3989c889b7. A user preferences section in each expert encoding, explicit and user led.


THE REFINEMENTS PROPOSED TO THOSE REQUESTS

On the steering recovery path, the refinement is that the 3 pieces inside it must not be bundled into 1 commit. The phrasing set is a user experience choice with no falsifiable criterion, so it gets a fitness review rather than a falsification pass. The persisted profile needs a stored state file with an owner and a lifetime, which is a new durable artefact. The mismatch test is the only piece with a measurable criterion available today, because the 4 simulated chats left a labelled set of 5 domain calls and 5 subdomain calls, and it must reuse the classifier's existing predicate rather than becoming a second copy of it.

On the steering surface, the refinement is that the recovery path and the dual domain resolution are 2 different repairs for 2 different faults. The recovery path handles a human disagreeing with the classifier. The dual domain resolution handles the classifier being right about 1 question and wrong about the other, which no amount of asking the founder can resolve. They are deliberately not recommended as a composed fix, because no measurement yet shows the pair beating either part alone, and the project standard permits a composed recommendation only with such a measurement.

On user preferences, the refinement is the ordering argued in item 5 above, and a terminology note. The founder wrote the word distillation in single quotes, which his own convention marks as a framing concept rather than an exact term, so this is not a correction of him. What he describes is nearer to preference induction from interaction traces than to distillation, which in training research means fitting a smaller model to a larger one's outputs. The distinction decides what would be built: induction can be made auditable and reversible per item, where a distilled artefact cannot be queried about why it believes something.


THE DECISIONS THAT ARE THE FOUNDER'S

6 need a ruling he has never given.

1. B141, whether the guard on the gate's own declared cost, written for the descriptor rule, goes on the commit gate, split so the file count half gates every commit and the collected count half stays in the full suite.

2. B142, the settings surface, whether the 4 interface roles map onto the harness roles, and whether the credential store is built now or after the runway.

3. B143, whether the severity proof is repointed at the severity figure the gate actually uses, since it currently licenses a release door on a proof of a different number, and whether the mathematical appendix gains a third consequence weight.

4. B154, whether the engineering critical level moves from 7 to 9 to match the published safety line, which loosens a gate and is therefore not a change to take from a reading of a standard, and when the 22 draft encodings go to the panel.

5. B160, which test replaces the proxy deciding whether a question was asked after the founder already ruled, since no sibling predicate agrees with it. 3 candidates disagree on all 4 of the entries they apply to. 4 options are recorded, and the recommendation is to change nothing, because 2 of the 3 candidates would remove items from his decision list and that direction has already had to be withdrawn once.

6. B170, whether the 621 commits on the shakedown branch merge to the main branch, or the shakedown branch becomes the repository default. This is the subject of section 6 below.

4 need only a word of permission rather than a decision.

1. B56, the demotion rule's operating point is recorded at 1 in 50, and wiring it changes which seats the harness dispatches, against the standing rule never to bench a model.

2. B104, whether the spoken reports need the 12 character ticket identifier as well as the entry code and its subject.

3. B140, the 2 routing rulings given on the 10th of November are recorded but unbuilt, and building them changes routing.

4. B144, the critical cut of 0.7. The measurement needs no ruling. The design consequence is the founder's and the entry holds it under his discussion marker.

A further 4 entries carry a ruling already and may need nothing at all: B77 on the convergence gate's roster blindness, B84 on the difficulty estimator that cannot be fitted, B94 on the 2 decisions left from the verified flag repair, and B125 on the joint round that asked 2 seats about a file which had changed. Whether anything remains on these 4 is precisely what B160, on the proxy no sibling predicate agrees with, settles.

2 further entries read as needing permission and do not: B168, on a ticket's kind being decided by 2 title keywords, and B169, on the permission predicate misreading a sentence, both described in section 7.


WHY THE RECENT WORK IS NOT VISIBLE ON THE PUBLIC REPOSITORY

The founder checked the public repository with an external model on the 12th of November and was told the recent severity work is not present, even though the last commit reads as very recent. Both halves of that are true and they are not in conflict.

Nothing failed to push. The work is on the public repository, on a branch that no default view shows. The shakedown branch carries a commit pushed at 18:46 UTC on the 12th of November, which is the recent commit observed. The main branch carries a commit from the 30th of September, and the repository's default pointer is main, so what a reader browses is 43.3929 days old.

Checked file by file against both branches: the domain manifest, the severity panel full record, the severity proxy producer and the per domain cut guard are all absent from main. The mathematical appendix is present on main and 43 days stale, which is worse than absent, because a reader cannot tell.

Measured on 2 agreeing routes: 621 commits exist on the branch and not on main, spanning 43.9643 days, a mean of 14.1251 commits per day, with a Poisson exact 95 per cent interval of 13.0358 to 15.2811 per day. Over the 39 active days the mean is 15.9231 with a bootstrap interval of 11.1282 to 21.5897. Main is 1 commit ahead and 621 behind, so this is a merge and not a fast forward.

The founder's suggestion that the cause might be a missing documentation sweep is refuted by the file existence check. A sweep updates the content of files that exist. It cannot make a file appear on a branch it was never committed to. A separate sweep is nonetheless owed and is being run.

The blast radius of a merge was traced before anything was proposed. 0 lines of code in the scripts or hooks directories hard code the branch name, and the repository has no continuous integration workflows, so neither a merge nor a change of default branch breaks any code. 4 documents name the branch and would need sweeping afterwards: the machine generated state snapshot, the new session handover, the recovery document and the onboarding document.

The instrument warned on every single commit. sv prints that it is not on main, quotes the founder's own ruling that main is the only branch that gets updated unless there is a stated reason to open an experimental branch, and warns that drift is what left main 16 days stale in August 2026. The current drift is a factor of 2.7121 worse than the incident that warning was written about, and the merge has been listed as owed to the founder in the recovery document since at least the 7th of November. A warning that fires 621 times and changes nothing is the loudest possible form of a mechanism nothing reaches, and that half is the orchestrator's to fix rather than the founder's.


2 ENTRIES READ AS THE FOUNDER'S AND ARE NOT

B168 records that a ticket's kind is decided by 2 title keywords in the harvester, so an entry declaring itself a feature request is filed as a proposed fix. 6 of 311 rows receive the feature request kind, which is 0.019293 with a 95 per cent Wilson interval from 0.008871 to 0.041444, and they are selected by the words orchestrator and selection appearing in a title rather than by what the entry is.

B169 records that the permission predicate for an entry's residue, installed on the founder's approval the same afternoon misreads a sentence describing his authority as a sentence claiming it. It classified B168, the entry on a ticket's kind being decided by 2 title keywords, as needing his permission. What it matched was that same entry's own record of the rule that only the founder may reject a feature request, a sentence about feature requests in general. The direction of that error is the harmful one, because a false positive moves an item off the set the session can advance, so the gate goes quiet about work it could be doing.

Both the ticket kind entry B168 and the permission predicate entry B169 currently read as needing permission, and both are the orchestrator's to build. The true figures are therefore 4 permissions and 11 items of work, not 6 and 9. Rewording the entries so they stop tripping the predicate was considered and refused on the record, because that is gaming the instrument rather than repairing it.


Written under CDSFL note standard v1.9 (1 November 2026).
