# Morning Report

12 November 2026, 06:20 GMT

This report answers the 2 questions you asked overnight, and lists the things that need your attention. It is not the decisions file. The 8 decisions awaiting your ruling are rendered separately, generated from the project's own records, and nothing here duplicates them.


### The 4 issues you asked about. Found, and they are your words not mine

You said you had no recollection of 4 guards being mentioned, by either of us, and you were right to doubt it. The phrase 4 guards was mine. The phrase 4 issues was yours.

Your message of the 11th of November reads, verbatim, fix everything, including the 4 issues you say are yours. It is at line 475359 of this session's transcript. The 4 are named in my own reply earlier that evening, at line 470429. The 4 that were mine are B22, on what a fix means outside code; B56, the demotion rule's operating point; B104, the spoken identifier convention; and B140, the 2 unbuilt routing rulings. A further 7 await you. Those 4 are, in order, what a fix means outside code, the demotion rule's operating point, the spoken reports carrying no ticket identifier, and the 2 routing rulings from the 10th.

So the 4 exist, they are identifiable, and your instinct that it was a snapshot rather than a standing item was correct. Measured this morning: B22, on what a fix means outside code, is closed on both the task list and the register. B56, the demotion rule's operating point, B104, the spoken reports carrying no ticket identifier, and B140, the 2 routing rulings from the 10th, are all still live and tracked by their own entry codes. All 3 carry no question for you, which confirms they are mine to do rather than yours to rule.

The enumeration item that described them has been retired as a stale snapshot, with the measurement that justifies retiring it: every 1 of the 4 is reachable by its own code, so a snapshot item adds no coverage and cannot be checked. Nothing is lost.

And a correction to my own record. My enumeration described this item as the other 3 of my own 4 issues, all 4 guard files exist and pass. That silently swapped your 4 for a different 4, namely 4 errors of mine recorded in a commit message that night. Neither description named a file, so neither could be falsified as written. That is why the item measured as unverifiable rather than done.


### Why I kept stopping. Measured, and now fixed

You asked twice why the session stops with work outstanding when the task list hook is supposed to prompt it onward. The answer is that it was not random. It was a designed cap being reached.

The stop gate refuses a stop while work is open, but it holds a budget of 8 refusals per turn. Once that budget is spent it prints a line saying it is allowing the stop so a finished session cannot be trapped, and it yields. Measured from this session's own transcript, that announcement appears 219 times, and the gate's state file recorded 15 refusals against a budget of 8 for a single turn, so the yield is routine rather than rare.

You then made the point that settles it. The limit of 8 is sensible for work that cannot proceed without you, and it is not sensible when it stops the session on work it can do. The gate's own documentation supports you: the stated reason for the budget is that a hook which can never yield would trap a session that has genuinely finished, and a session with work it can do has not finished.

The gate already knew the difference and was not using it. It has a function that skips entries awaiting your ruling when choosing which entry to name, added on the 10th of November, with 4 tests on it. Its own documentation records the mirror image of this fault: through the 9th of November it named an entry awaiting your ruling on every turn and refused the stop 8 times a turn against work nobody in the session could advance, which it describes as a whole day of pushing at an entry that could not move. I repaired which entry it names and left the budget flat, so the inverse case survived untouched.

The budget is now conditional. It stays at 8 when no open item can be moved without you, which preserves your original intent exactly. It rises by 1 base budget for every movable item otherwise, with a ceiling of 40. At the time of writing 11 of 19 open items were movable, so the budget was 40 rather than 8. That figure was wrong twice over, and where it finally landed is worth stating plainly. 7 entries have since been closed, which leaves 12 open, and every one of those 12 is yours: 8 await your ruling by the classifier, and the other 4 say in their own text that what remains is your decision. 0 are mine. So the budget sits at its floor of 8, which is where you set it, and it sits there because nothing is left in the queue that I can advance without you. The ceiling is a judgement and is labelled as one in the code: no measurement in this project relates a number of refusals to any outcome, so it must not be cited as derived.

102 tests pass on the stop gate after the change. And the repair exposed something worth more than itself. Raising the budget turned a test red, correctly: that test demanded the gate give up whenever a stop had already been interrupted once, which is behaviour this project deliberately retired on the 3rd of November. The gate's own code says so in as many words, and a sibling test in the same file asserts the opposite. 2 tests in 1 file demanded opposite outcomes from the same input, and the one that passed depended on leftover counter state. It is replaced by 3 tests of the invariant that actually prevents a trap, which is that the budget is finite.


### A design finding that needs your awareness, not your ruling

The steering simulation you asked for has been run, with a small model answering as a harness seat and me acting as the human in the loop. The proposer named the correct domain in 5 of 5 cases and the correct subdomain in 4 of 5, and 2 cases escalated to a dialogue, so the escalation path was exercised rather than described.

On 1 of those 2 escalations the seat disagreed with my proposer, and the seat was right. The task was a pooled hazard ratio from 3 unlike trial sites. My proposer named statistics. The seat named biology, reasoning from the manifest's own rule rather than against it: statistics declares no severity scale of its own, with the stated reason that a statistical error's consequence belongs to the application it serves, and the application here is a vaccine dosing claim, so the consequence is patient harm.

Both answers are correct about different questions. The task's subject is statistics, which decides which expert encoding a seat should receive. The task's consequence scale is biology's, inherited, which decides what counts as a critical finding.

So a steering surface that returns 1 domain conflates 2 separable things. For the 4 domains that cite an external published standard the 2 coincide. For the 5 that declare no scale and the 1 that declares a composed scale they can differ, which is 6 of the 10 declared domains. The surface should resolve and record both.

This was not visible from the design. It was surfaced by an independent seat contradicting a construction I had written myself, which is the reason the dialogue was run with a separate model rather than adjudicated alone.


### 3 things that are wrong and are not mine to decide

First, a red test that is not mine. A case in the blocker triage guard expects a blocking verdict for an item about an exhausted round threshold. The only entry mentioning that subject is A11, the entry on 5 rulings settled in September, which is done, so no open entry declares a dependency on it and the triage is correct. The test is stale. It also sits off the commit gate, so it has been failing undetected since that September rulings entry closed. Fixing it is small but it is outside the agreed batch.

Second, the stop gate's own suggested remedy writes to the repository. When it refuses a stop it suggests running the blocker triage classifier, and that classifier appends to the parked items file. Obeying it 27 minutes into a commit board changed a section heading count that 3 of that board's tests assert on, taking it from 72 to 73, which fails those tests on a repository that is otherwise correct. It has now happened 3 times in 1 night. The damage was reversed and verified each time, and the fix owed is that the classifier should refuse to write while a board is running and print its verdict instead.

Third, the commit duration ledger recorded a refusal reason that contradicted the board's own output. It said the desktop mirror had drifted. All 4 mirrors were in sync, verified file by file, and the board's log says so. The real refusal was 2 red tests about a 1-character fault of mine: an evidence field holding 2 paths separated by a space where the convention, used by 87 existing markers, is a comma. A recorded cause that contradicts the board is worse than no cause, because it is acted upon.


### A regulatory figure was wrong in an expert encoding, and it is now fixed

While bringing the 28 older expert encodings up to depth, a worker found a defect in content that was already there, not in anything added. The pharmaceutical chemistry encoding stated the elemental impurity limits of the ICH Q3D guideline, labelled as oral limits, as palladium 10, platinum 10, nickel 20 and copper 300 micrograms per day.

Those are the parenteral figures, not the oral ones. The oral permitted daily exposures are palladium 100, platinum 100, nickel 200 and copper 3000 micrograms per day. All 4 were uniformly a factor of 10 low, which is the signature of reading across the wrong column rather than 4 independent mistakes. A model following that file would have over-controlled every oral product by a factor of 10, rejecting batches that comply.

I did not take the worker's word for it. The values were confirmed independently by external search against published reference tables before the file was changed, because a model's claim is not evidence under this project's own rule. The corrected line names the superseded figures rather than erasing them, states that they are correct for the parenteral route the line does not cover, and gives the inhalation figures as well, which are lower again by a factor of 10.

It is worth saying why this came out of enrichment work rather than review. The worker was told to write an exception catalogue, which means asking where the file's own hard constraints stop holding. Asking that question of a figure is what exposed the figure. A review pass that read the file for sense would have found it consistent, because it is internally consistent and simply wrong.


### The 1 question I will not answer for you

The spoken reports you read carry the entry code and its subject, for example the line that reads decision 1, B77, whether the convergence gate should know how many seats are answering. What they do not carry is the 12 character ticket hash that the repository copy carries beside it.

Measured across 648 spoken files on your Desktop: 220 carry an entry code, which is 0.339506 with a 95 per cent Wilson interval from 0.304087 to 0.376817; 16 carry a ticket hash, 0.024691; and 425 carry neither. So the complaint recorded in B104, that the reports lacked the identifier facility you asked for, holds for the historical corpus.

For the reports generated now it is a different question, and it is yours. A 12 character hexadecimal digest read aloud is noise, and your own rule says a hash carries no meaning at all and must never be written without saying what it is about. The entry code plus its subject is both traceable and speakable. So: does your spoken copy need the hash as well, or does the code with its descriptor satisfy what you asked for? If you want the hash I will add it. If the code suffices, the current generator already meets it and the 425 older files are a backlog rather than a defect.


### 3 things found after this report was first written

First, the enrichment did not cost the seats anything, which had to be checked rather than assumed. The 29 enriched encodings roughly doubled in length, and the composer discards optional text when a directive set exceeds a seat's coherence budget. At the tightest seat's budget of 0.01 every 1 of the 10 domains sits between 0.002137 and 0.002700, a factor of about 4 below the limit, and nothing is discarded anywhere. So the added guidance reaches every seat as written. Had that not held, the work would have been written and then thrown away before any model saw it.

Second, I nearly reported a defect in the composer that does not exist. My first check called it with the wrong argument, treating a subdomain label as a file variant, and it warned correctly about files it could not find. Called the documented way, all 10 domains compose between 5803 and 11281 characters with no warnings at all, and all 40 declared encoding paths exist. The warnings were right and my usage was wrong. In the same pass I compared a figure of 2813 estimated tokens against a coherence budget of 0.01 and reported a breach; those budgets are densities rather than quantities of tokens, so I had compared a quantity to a ratio. Both are errors in my checking rather than in the subject, which is the pattern this report closes on.

Third, and this one is a real gap in my own record keeping. The 6 entries I raised last night to track the outstanding work all describe work that is now finished, and all 6 still read as open. The open count stands at 19 where it should be 13. That is a defect this project has recorded before, under the heading that building the work is not marking the entry, where the earlier instance was 5 built and 5 reading open. The consequence is that the automated prompt has been naming a queue 6 entries longer than it is. Closing them touches 3 surfaces at once and it is now done. All 6 are struck through on the list, marked done with their evidence, their tickets closed, and the open count is 13.

I called that the first item of the next batch and that was wrong, which is worth saying plainly because it is the more interesting half of this. Your instruction last night carried 3 clauses: add the remaining 10 tasks, make sure the automation runs, and mark anything already done as done and record it in the registry as well. My enumeration measured the first 2 and never asked about the third. So it printed that the list was complete while 6 entries it had itself just measured as finished still read as open, and the precedent was sitting in the same file, because 3 sibling entries raised on the same night had already been struck through. A predicate that measures the building cannot see the marking, since each is individually correct.

The enumeration now checks the marking too, and the check reaches the exit code rather than only a printed line, so the loop cannot end while the clause is outstanding. 6 of 6 deliberately reverted versions of that check fail as they should, and the subject file is restored byte for byte afterwards.

A further point came out of that pass, and it is yours to know rather than to decide. The counter that decides which open items I can advance cannot tell an item that asks you nothing from an item whose residue is your permission. 4 of the 12 open entries are the second kind and say so in their own words: the demotion rule's operating point, the spoken identifier convention, the 2 routing rulings, and the critical cut of 0.7, whose entry says the measurement needs no ruling but the design consequence is yours and is held under your d. That is the same fault the counter's own documentation records from the 10th of November, in mirror image. My first version of the fix caught 3 of the 4 and missed the critical cut, which is why it was falsified against every entry before being applied rather than after, and a mutation then showed that the repair for that miss was itself tested by nothing. It is now 10 tests with 7 of 7 reverted versions failing as they should. It is NOT installed. Installing it edits the stop hook itself, and this session is not permitted to modify the hook governing its own stopping without your say-so. It is the single thing in this batch I could not finish, and it needs 1 word from you.


### Where the agreed work list stands

Of the 21 items agreed over the window, 17 are now settled, 1 is retired as the stale snapshot described above, and 3 remain open. The commit is held deliberately until last, on your ruling that it is the logical place for it once the work list is confirmed complete.

Of the 3 remaining, the severity round's joint half is dispatched and running on the free seats as this is written. The 2 halves of B125, the joint round that asked 2 seats about a file which had changed since they answered, are measured and reported below. The 28 older expert encodings are being brought to the same depth as the 22 written yesterday, with 6 parallel workers, 1 per domain family.

On B125, that same joint round quoting a file which had moved, the measurement refuses the recommendation rather than supporting it, and you should know that before the entry is closed. Its accepted recommendation is a composed fix. Your composability standard permits recommending a composed fix only where a measurement shows it beats either part alone. That measurement cannot be taken: of 17 archived joint briefs, 17 name an artefact and 0 carry the digest table that records each named file's state at dispatch, so no round has ever had either half in force and there is no data on either half alone. What is unambiguous, and needs no composition claim, is that the stamping function works and reaches 0 of 17 briefs, which the additive standard forbids on its own.


### 10 errors of my own, because they bear on how much to trust the rest

10 of the measurement predicates I wrote to check this work were wrong on their first run. 2 reported the work as better than it is, including 1 that could never have failed at all, and 8 reported it as worse. The figure of 10 wrong predicates matters more than the direction, which at 2 against 8 is not statistically distinguishable: it is the reason every figure in this report names the instrument that produced it, and the reason a guard that passes first time now gets a mutation test before it is believed.

1 of those mutation tests caught a vacuous test of mine this morning. Removing the length normalisation from the domain proposer left the guard green, because the case I had constructed made an alphabetical tiebreak decide rather than the property under test. The case was repaired and all 3 mutations now fail the guard as they should.


Written under CDSFL note standard v1.9, 1 November 2026.
