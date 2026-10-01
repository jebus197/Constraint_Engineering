# Green table, and the claim channel is now on

Constraint Engineering project. Work of 1 October 2026, on the simulation branch. Written 1 October 2026, afternoon, British Summer Time.

Plain-English companion. The technical record is filed as `Green_Table_And_The_Claim_Channel_2026-10-01.md`, and the text-to-speech version as `Green_Table_And_The_Claim_Channel_2026-10-01.txt`.


## The short version

The test table is green again, and the most useful thing found while making it green is that most of the red was not a regression at all. It was one fault wearing 6 different costumes: a dated measurement checked against an archive that has since grown. The archive grows every time an experiment runs, so a guard that compares a figure recorded in September against the whole archive today will go red without anything being broken.

That matters beyond tidiness, because a guard that goes red for a file nobody touched is on its way to being ignored. 6 separate guards had that shape and all 6 are now scoped to the population their claim actually names.

Alongside that, the 4 items marked for fixing in the morning report are all built, applied and tested, the claim level channel the review panel designed is built and switched on, and 1 question cannot be answered without spending seat dispatches, which is a decision for the founder.


## The table, before and after

The clean overnight run finished at 20 failed and 9200 passed. Every one of those 20 files is now green: 698 tests pass across the set, and the operational scripts family alone, which was carrying 9 of the 20 failures, passes 524 of 524.

The table is green. The final run on a genuinely frozen tree finished at 9375 passed, 8 skipped and 0 failed, in 3217.53 seconds, which is 53 minutes and 37 seconds. 49 attempts to reach the network were made across 21 tests and every one was denied.

It took 4 runs to get there, and 2 of those were spent on 1 test. The second gave 2 failures, both found and fixed. The third was voided by the assistant editing the tree while it was running: the single failure was a guard that photographs the repository's state before and after, which then blamed the measurement it was watching for a change the assistant had made in between. 4 of 480 test files take that photograph, which is 0.8333 per cent, and a single search would have found all 4 before the edit. The number of skipped tests rose from 7 to 8, which is the search guard standing aside in a shell where the tool it depends on cannot be reached, exactly as designed.

Landing the day's own work tripped 7 further guards, and every one of them was the assistant's own. The Desktop copy of the master task list drifted when the A7 entry changed. The memory ledger said 158 files where 163 exist, which is the 10th consecutive manual correction to a figure a remedy from August said should be derived rather than typed. The memory index broke both its length rule and its headroom rule, and its 5 new entries are now 1 grouped line. 2 synthetic strings in a test looked like references to files that do not exist, and were renamed to names the checker already treats as illustrative rather than widening a project wide exemption. A census of tests that assert on source text rather than running anything reached 81 against a limit of 80, exactly 2 of them the assistant's, and both are now structural checks that parse the file instead, which is what the census exists to encourage. And the strict form of one guard was inferring a precondition from the very inequality it was testing. Finding the cause took 2 attempts, and the first was wrong: the guess was that the suite's own creation and deletion of ignored files had removed whatever the search wrapper was hiding. That gate measured 910 ignored files and so never fired, and the test failed again, with its own message refuting the guess.

The real cause is that the wrapper is not self-contained. It hands the work to the Claude Code binary, and if that binary cannot be reached it silently becomes an ordinary search instead, at which point the 2 counts it compares are identical by construction. The variable that decides this is which shell started the test run: the path to that binary is set in the assistant's own environment and is not set in the founder's login shell, where the fallback location does not exist either. Measured in both: 911 against 1159 in one, 1159 against 1159 in the other. Every targeted re-run was launched by the assistant and passed, and both full runs were launched from the terminal and failed. It was never about the suite at all. The guard now checks whether that binary is reachable and stands aside where the difference it looks for cannot exist, verified in both directions, while its unconditional companion check still runs either way. When the wrapper does work it hides 248 of 1159 files, which is 21.3978 per cent, confidence interval 19.1332 to 23.8513 per cent.


## The one fault, named

A dated claim needs a dated denominator. 6 guards compared a figure measured at a point in time against the archive as it stands now.

The clearest case was the population recount for the fix efficacy probe. A script written on 22 September checks that another script's docstring states the distinct number of probe records rather than a doubled one. The docstring says, in its own words, that across the 4 commissioning arms of 21 and 22 September there were 124 records of which 23 did not cure their own falsifier. The recount, however, counted every commissioning run on disk. Once the arms of 29 and 30 September were archived it measured 265 and 50 instead, and demanded the docstring be changed to those.

Obeying it would have overwritten a correct, dated record with a later one. The arithmetic settles it cleanly: the 4 named arms give 69 plus 9 plus 30 plus 16, which is 124, and 16 plus 3 plus 2 plus 2, which is 23. The later arms add 141 and 27. So 23 of 124 is 18.5484 per cent with a Wilson interval of 12.6898 to 26.2972 per cent, reproducing the docstring to 4 decimal places. The claim was never wrong. The denominator had drifted.

The same shape appeared in the predicate family recorded against task A7, in the archive exposure pin for the latent tagger, in both of the panel audit producers from 22 September, and in the disagreement guard for section P. All are now scoped, and in the A7 case a scope check confirmed the diagnosis: restricting the producer to runs archived before 17 September reproduces exactly the family the entry recorded on that date.


## What was genuinely broken

3 of the failures were real defects, and 2 of those were in work from the previous day.

A measurement script could not be parsed by Python 3.11, because it put a backslash inside an expression in a formatted string. That is legal from version 3.12 and a syntax error before it, and the project deliberately holds a floor at 3.11 because a module that cannot be parsed stops the whole suite from being collected, not just itself. The label is now built outside the string.

A morning report delivered to the founder carried 7 percentages and a p-value and named no artefact at all. The guard that caught it is the project's own rule that a live note must say where its figures come from. All 7 are now reproduced by a committed script which reads the archived runs, and rebuilding them surfaced 2 under-statements in the original wording. The p-value of 0.0040 is the one sided result and the two sided figure is 0.0079, which the report did not say; and the sentence reporting that 12 of 12 findings reached the human queue with no test verdict was true but read as though the round produced 12 findings, when it catalogued 15 and 3 of them closed with a confirmed verdict. Neither correction changes a conclusion. Both are now stated.

The third real defect was in the classifier that decides whether a finding is latent, meaning unreachable in practice. It matched the phrase "with no caller override", in a sentence that says callers cannot override a setting, and read it as evidence that no caller exists. The entry was tagged latent on prose meaning the opposite. That matters because the latent flag feeds eligibility for demotion, so a live defect could in principle be dropped from the convergence gate. Nothing was demoted on it, which was checked. The marker now requires the noun to be an absence rather than a modifier, and over every registry entry in the archive the tightening loses exactly that 1 false positive and no true positives, which means the existing pin of 16 entries is correct as it stands rather than needing to be loosened around a wrong tag.


## 2 guards were wrong about working code

The pre commit guard asserted that the git hooks setting held the literal text "hooks". On this machine it holds the absolute path to the same directory, the hook is present and executable, and it has been refusing commits all day. The test was reading a configuration string and reporting on a behaviour. It now resolves the configured path and asks the question that matters, which is whether it points at the versioned hooks directory and whether there is an executable hook in it. A clone pointing somewhere else, or missing the hook, is still red.

While fixing it, a claim was written into the comment that a relative setting is unsafe because git resolves it against the current directory. That claim was then measured rather than trusted, by making a throwaway repository and committing from a subdirectory under each spelling. On git 2.50.1 the hook ran both times. The claim was false and was removed before it shipped.

The second was the guard protecting the founder's Wolfram ruling, which scans the repository for anything pinning the policy to deny. It had gone red on 3 transient agent worktrees, which are throwaway copies of the repository that the agent tooling makes: they carry copies of the 2 files the scan exempts, and the exemptions are absolute paths, so a copy 1 directory deeper matched neither. Nothing was pinned to deny. The scan had walked out of its subject.

Fixing the scope exposed something worse in the same guard. Its pattern required the separator to follow the variable name directly, so it recognised the shell form and missed both spellings anyone would actually commit, in Python and in a configuration file. A guard that catches only the shell form, over a file set that includes Python and JSON precisely because that is where the setting would live, could have let the ruling be inverted in silence. The pattern is widened, deliberately not so far that it matches a mere mention of the word, and the predicate is now a named function with its own tests rather than a line inside a test.


## The disagreement condition, and a shortfall recorded

Section P of the panel protocol requires that disagreement between seats is preserved as information rather than smoothed to consensus. The guard reported that 2 rounds of 30 September had lost it.

3 of the 4 replies in those rounds had no disagreement section. 2 of the 3 had stated a disagreement in full, naming whom they disagreed with and carrying the substance, but inside a sentence rather than at the start of a line, and the pattern was anchored to line starts. One wrote that its disagreements with the assistant on verdict vocabulary and on stage reading were preserved in the note with the evidence that decides each. The other named a disagreement with the assistant inside a question heading. Both complied; the guard could not see it. Widening the pattern recovers 4 replies across all 306 archived seat replies and loses none, and 2 of those 4 are from July and August, so the guard had been under reporting compliance for months rather than only yesterday.

The widening deliberately stops short of matching the word used as a technical noun. A bare pattern also matched a sentence about how a model's disagreement with a confirmed finding would vanish, which is a remark about a mechanism and not a position held by the seat. Matching a mention rather than an assertion weakens a guard in the reassuring direction.

That leaves 1 genuine shortfall, and it is recorded rather than excused. The remaining reply never used the word at all. It did contradict the brief, and substantially: it recorded that the brief's own declared figure of 73 of 73 was a hardcoded literal rather than a live count, and that the live deduplicated count is 201. The project accepted that refutation and withdrew the figure. So the seat dissented and filed the dissent under the heading "Two corrections I owe". The shortfall is of form, not of substance, and the record says exactly that.

It also records something the round's design cannot supply. Both seats answer the same brief in parallel in separate sandboxes with no sight of each other's reply, so no seat can disagree with the other seat's content. The brief asked for that twice. The only objects available are the assistant and the brief.


## The 4 named fixes

First, the catalogue record now says whether the proposed fix worked. Every field it carried was about whether the defect was shown; none was about whether the fix was. The data was already on the entry: across 1 commissioning arm, 69 of 69 entries carry a fix efficacy result and 16 of them record that the fix did not cure its own falsifier. None of those 16 was visible to anyone reading the exported record. 3 fields are added rather than 1, and the one that matters is 3 valued, because a single true or false would merge a fix that failed with an instrument that could not look. What it immediately surfaces is that 16 of 69 findings in that arm are closed, with the defect demonstrated, while the fix that closed them was measured as not working. The disposition of those is a ruling, not a computation.

Second, confinement is no longer asymmetric across tools. Writing and editing were withheld from every seat, and the shell was not, because every mathematical tool the seats are required to use runs through it. The project's own notes said so and answered with position and detection: a sandbox copy so relative paths are harmless, and a before and after fingerprint so an absolute path write is caught afterwards. Detection is not prevention. A kernel sandbox profile now denies writes to the canonical tree for the seat process and everything it starts, which is exactly what no tool list can reach. 6 properties were measured against the real repository path: a write inside the copy succeeds, a new file and an append in the canonical tree are both refused, git cannot even lock its own configuration there, reading still works because a seat must read source, and the mathematical tools are unaffected. The deny is targeted at the canonical path rather than global, because a global deny also broke the command line tool's own state and would have traded a confinement gap for a dead seat. On a machine without the kernel sandbox the confinement call reports its own absence rather than pretending, and the per attempt record carries which control was in force.

Third, the orphaned extraction pattern is gone rather than reported again. It had no callers, which the project's own standard treats as a defect in its own right, and removing it required a committed measurement showing the survivor dominates on a named property. The property is recognition over 560 realistic document shapes. The orphan recognised 14, the survivor 224, and the number recognised only by the orphan is 0, with a Wilson interval of 0 to 0.6813 per cent on 2 independent tools agreeing to 2.6 times 10 to the minus 18. The survivor reaches 210 shapes the orphan could not, so the dominance is strict rather than equal. The pattern itself survives as a literal inside the test that proves it redundant, so the comparison is re-derived on every suite run rather than remembered.

Fourth, the stranding of seat written evidence is repaired at source. A panel harvest lands inside the logs directory, which version control ignores, so every file a seat writes is invisible to git by construction: 251 seat scripts across 22 rounds, all 251 ignored, and 46 of them, 18.3267 per cent with a Wilson interval of 14.0302 to 23.5781 per cent, existing nowhere a fresh copy of the project could reach. 12 scripts and 2 design notes were rescued by hand the previous day, which is the manual step now replaced. The harvest copies every seat written file that has no counterpart in the tracked tree into a tracked directory, with its origin written into the file and the seat's own checksum recorded before the header is added. Files the seats merely edited are not copied, because the canonical file already reaches a clone and copying it again is how an earlier attempt staged 47 megabytes of byte identical duplicates. Scratch space is not preserved, because scratch space is working residue rather than evidence. A ratchet now holds the backlog: counts may only fall, and any round not already listed must have none, because a round run after the repair should preserve its own.


## The round cap now suggests a number, and it can be set

The ruling on the cap had 2 halves and only 1 had been built. The recommendation fired correctly on the run that prompted it, and named no number, so a reviewer was told to raise a cap with no indication of how far. There was also no way to set a cap at all; it was a default inside the code.

The number is now derived from the gate rather than fitted. Predicting how many rounds a target actually needs is not estimable on the current archive, which both free seats found independently and an external model restated more strongly. So the question answered instead is the smallest cap that could satisfy the gate from where the run stopped: the gate's second half requires 3 consecutive rounds with no new critical finding, and a run that ended while still producing criticals has accrued none of that streak, so it needs at least 3 more rounds whatever the target is. On the run in question that gives 11, which is its 8 plus 3, and the text says plainly that it is a floor and not a prediction.

The cap can now be set 2 ways: a flag, which always wins and is never blocked, and a question asked on an attended run. An unattended or detached run is never asked, because a prompt in a detached run is a dead run, and detached running is the whole point of that launcher.


## The claim channel is built and switched on

This is the substantive piece the review produced. Both seats found, independently, that nothing in the harness judged a claim as its unit: the fix scorer classifies a proposed fix, which is 1 level above what task A19 says. The design is theirs, and 1 seat falsified 3 of its own 4 candidate architectures before recommending the survivor. Its 4 pieces are a ledger of claims per target, decidable claims carrying falsifiers into the existing verification path, undecidable claims routed to a human rather than discarded, and file level admissibility as an aggregate over the ledger. The fix scorer is untouched and its abstention keeps the meaning the glossary gives it.

It is populated from what already exists, because every registered finding is a claim about the target: one carrying a runnable falsifier is a claim computation can settle, one without is routed. The aggregate is 3 valued and the third value matters: a target with no claims at all is the only state that corresponds to genuinely non computable, and it attaches to the absence of claims rather than the absence of fenced code.

Run against the archived prose arm, where the current machinery holds no opinion about anything in the target, the channel reports 15 claims, 8 of them decidable, 3 decided, 7 routed to a human and 0 discarded. That is the case that justifies the channel, on real archived data rather than in argument.

It is informative only for now, which is the seat's own recommendation and not a deferral: the channel is on and populated, and wiring its verdicts into the scoring equations waits on a commissioning run measuring how often it is wrong against the corpus's known ground truth.

What it does not do is stated in the artefact itself rather than only in a comment. It records claims the seats stated. It does not manufacture claims for a target no finding names, so it does not test whether a reasoning stage surfaces material unstated claims. That was the recommending seat's own strongest self refutation, and closing it needs a corpus extension where the planted defect is an unstated consequence of 2 individually true stated values.


## What the external model added

The founder asked whether Grok's input on the round cap brought anything new, or was churn, and whether it was worth another panel round. It brought 2 things and neither needs a panel.

The first is an argument rather than a figure, and it is stronger than the panel's. The panel concluded that the number of rounds a target needs cannot be predicted from its complexity on this archive, which is a fact about the archive and could be overturned by more data. Grok's objection is structural: complexity is not stationary. After the first round what determines how many rounds remain is no longer the original document but the document plus the fixes applied, the challenges still open and the examination history. A cap fitted to complexity measured before the run predicts a quantity from a state that no longer exists by the time it matters. That survives a larger archive. It is recorded beside the cap reasoning.

The second was checkable and was checked, and it was a real gap. Grok's recommendation ends with the instruction to always record which stop reason fired. The runner does set a stop reason on every exit path, and carries a fallback that names an unrecorded stop rather than leaving it blank, because not knowing why is worse than any named halt. The report carried no stop field at all. The reason was computed in flight and discarded at the edge, which is the difference between a run that converged and a run that ran out of budget, and that is precisely the distinction the cap recommendation exists to surface. It is now in the report, with a separate field recording whether the reason is a real one or the fallback.


## The classifier question, and why it is not free

The panel recommended that the boundary of non computability become an outcome rather than a gate: a document is judged to carry no decidable claims only after something has looked for them. Neither seat would guess whether a small cheap classifier can draw that boundary, and 1 specified a labelled test set with executable ground truth instead of guessing.

That set now exists: 15 documents, 10 of them carrying claims with planted ground truth, in both intact and prose only form, and 5 controls of opinion prose carrying nothing computable. The first real number for the status quo comes out of it. The current triage, which is fence syntax, scores 10 of 15 for accuracy and 5 of 10 for sensitivity, with a Wilson interval of 23.6593 to 76.3407 per cent. It misses every prose variant, and it raises no false alarm on the opinion prose.

The composability question the founder asked has a clean answer on this set and an awkward one in general. Composing the syntax test with a claim locating test recovers all 5 missed documents. But the claim locating test finds claims by their anchors, and the anchors come from the corpus's own claim lists, which is the answer key. On a document the corpus does not describe it has no anchors to find and returns nothing, which was verified by giving it one. So its score of 15 of 15 is a lookup's and not a classifier's, and composing a syntax gate with a lookup cannot answer whether a cheap model can find claims in a document it has not been given the answers to.

That needs a model arm, run against documents whose labels it has not seen, and that costs seat dispatches. The set is prepared for it, with the labels written to a separate file so a model can be scored without ever being shown them. Whether to spend the dispatches is the founder's call.

There is also a gap in the record worth naming. The founder recalls measuring the classifier agent, Haiku, and finding it generally reliable. That measurement is not in the project record: Haiku is named as the classifier in the architecture document, and searching the committed scripts, the documentation, the resources, the experimental notes and the project memory returns no script that measured its agreement and no figure for it. It may exist outside the repository. If it does it should be committed beside its number, and if it does not, this labelled set is what would produce one.


## Errors caught in the assistant's own work

5 are worth recording, because 4 of them were caught by the project's own machinery rather than by reading.

A test predicate searched source text for an attribute name and matched the explanatory comment that exists to say why the attribute is not used. That is the third time in 2 days that a predicate matched a word rather than a behaviour. It now parses the module and looks for a real expression.

The wiring for the claim ledger first read a configuration field that does not exist. It would have raised, been swallowed by the report section's own exception guard, and left every report carrying a plausible statement that the ledger was not written, while the channel did nothing at all. That is the addition nothing reaches, and it was caught by checking the attribute against the real class before running anything.

A newly written measurement script printed a list cut to 10 items with no statement of what it withheld, which is the project's own rule and one the assistant had fixed in a different file earlier the same day. The project's guard caught it.

A claim written into a comment, that a relative hooks setting is unsafe, was false on this version of git. Measuring it before shipping is what caught it.

A test probe was built in a shape the real reply did not have, which made a correct pattern look broken. The probe was wrong, not the pattern.


## What needs a ruling

7 things, all recorded and none blocking.

The disagreement condition's semantics, where a seat genuinely agrees and so has no disagreement to preserve, and whether a blind parallel round should ask for disagreement with the assistant and the brief rather than with a reply the seat cannot read.

Whether to spend free seat dispatches on the model arm of the classifier question, and whether the Haiku measurement exists outside the repository.

The 46 stranded files already on the backlog, and which of them are worth rescuing, noting that the scratch ones should not be.

Confirmation that the claim channel stays informative only until a commissioning run measures how often it is wrong against known ground truth.

The disposition of the 16 findings that are closed with a measured non curing fix, now visible in the exported record.

A duplicated archive directory: one run's logs are reachable under 2 names because one is a symbolic link to the other, so a counter walking directories reads 217 registry identifiers twice. It affects none of the figures checked today, and it was deliberately left alone because fixing it could move archived numbers.

And the predicate family recorded against task A7, which is maintained by hand and will drift again the next time an experiment runs. The alternative is to scope it to a date, as the other 5 guards now are.


Every figure above was computed in this session, each proportion carries an interval, and the scripts that produce them are committed alongside them.


Written under CDSFL note standard v1.7 (26 August 2026).
