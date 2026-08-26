# Decisions awaiting the founder, and what was done overnight

2026-08-26, 01:26 BST (UTC+1)


## Why this file exists

The founder asked that anything still needing their input be gathered into one place once the work that could proceed without them was complete. This is that list. Section one is the six decisions. Section two is the single command the founder can run in ten seconds. Section three is what was done while they slept, in case any of it changes how they want to decide.

Nothing in section one is urgent enough to have been guessed at. Each item states the options concretely and carries one recommendation rather than a menu.


## Section one — the decisions


### Decision 1 — permission to rewrite the working branch's history

What is being asked. Permission to remove the file control two distinct defects KEY dot md from the fifty nine commits on the working branch, using git's history rewriting tool.

Why it needs asking. The environment running this session refuses history rewriting as a destructive operation, so it cannot be done without an explicit instruction. It is also not free. Eighteen of the branch's fifty nine commits are referenced by their commit hash inside the project's own markdown documents, most of them in the current state document. Rewriting changes every one of those hashes, so all eighteen references would have to be remapped from the rewrite's own record of old hash to new hash, and each one verified afterwards.

What is at stake. The file is an answer key. Its contents are already public by another route, described in section three, so removing it publishes nothing new either way. What changes is whether a file named scorer key appears in the public repository's default branch history. That is a statement about how this project operates, separate from what the file reveals.

Recommendation. Grant it, and pair it with decision 2. The remapping is mechanical and verifiable, and this project has lost five experiments to key exposure. The cost is an hour of careful work.


### Decision 2 — where the work lands: `main`, or a branch

What is being asked. Whether to merge the working branch into main and push, or to push the branch by itself.

The measured position. Public main is fifty nine commits behind the working branch. The branch has never been pushed at all, so nothing of the last several weeks is visible to anyone reading the repository.

The difference. Pushing the branch creates a copy on the hosting service that nobody reading the project would think to look at, and main stays fifty nine commits stale. Merging into main makes the public repository current, and also makes every commit on the branch reachable from the default branch, including the one holding the answer key if decision 1 is declined.

Recommendation. Merge into main and push, after decision 1 is executed. The founder's own standing rule is that main is the only branch that gets updated unless there is a stated reason for an experimental branch, and the mechanism that broke that rule left main sixteen days stale in August.


### Decision 3 — who authors the replacement target for exp55

What is being asked. Experiment 55's target document is spent, for the reasons in section three. A re-run needs a new one. The question is who writes it and its planted defects.

Why it matters. The same question was already open for experiment 52's planted set, and the two should be answered together. If this assistant authors both, then this assistant knows the answers to two controls it will later help interpret, which is a provenance problem even if no key is ever read. If an external model authors them, the design has to be specified precisely enough to be reproducible without revealing itself.

Recommendation. An external model authors both, from a written specification the founder approves, and the resulting keys go straight into the outside key store without passing through the repository at any point. That is the arrangement the volunteer computing literature calls an indistinguishable spot check, and it is the only one that survives the failure mode described in section three.


### Decision 4 — the panel dispatches, which cost money

What is being asked. Two panel reviews were approved in the founder's last written instructions and have not been run. The first is the falsifier gate repair recommendation, to be reviewed with the second Claude instance and with Fable 5. The second is panel confirmation of the twenty seven instruments whose commissioning status is recorded as not verified, together with clean run readiness.

Why they were not run overnight. They spend real money and produce findings the founder has to read. Starting them while the founder slept would have meant a queue of unread panel output waiting in the morning, competing with the six decisions above. Neither is blocked by anything technical.

Recommendation. Run the falsifier gate review first and alone. It is the one whose outcome changes what the instrument confirmation should even ask.


### Decision 5 — merge semantics, the Bugzilla question

What is being asked. Whether the machinery is capable of genuine merging of findings in the sense the Bugzilla paradigm uses the word, whether it can be made capable, or whether it would have to be built from nothing. This was raised in the founder's last written instructions and is unchanged.

Status. No work was done on this overnight, because it is a design question rather than a defect, and the founder asked for it to go to a panel rather than to be settled here.


### Decision 6 — the archive decryption instructions

Status. Held, as the founder directed, for a message of their own, and to be done as the last step. Named here only so the list is complete.


## Section two — the one command


The operational tracker's Desktop copy is one hundred and seventy eight thousand nine hundred and seventy one bytes against the repository copy's one hundred and eighty thousand and forty three. It drifted because the tracker was edited during this session and this process cannot overwrite existing files on the Desktop. That restriction was measured six times out of six on the twenty fifth of August. The repository copy is canonical by the founder's ruling of the sixth of August, so the repository copy is right and the Desktop copy is stale.

Refreshing it is one command:

```bash
cp ~/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md ~/Desktop/CDSFL_Agent_Operational_Plan.md
```

Separately, and requiring no action unless the founder wants it: this session lost read access to the persistent memory folder part way through the window, after edits to files in that folder had already succeeded. The exact minute was not captured, which is itself a lapse against this project's rule that a time is read from the clock and never typed. Nothing was lost. The save routine and the drift guards were both hardened to report that condition rather than crash or misreport it, which is described in section three. If the founder wants the memory folder readable again in future sessions, that is an environment setting rather than a project change.


## Section three — what was done overnight


### Finding 1 — exp55's answers were public three days before it ran

The rule that has been stopping this project from publishing its work named the wrong file. It guarded the scorer key, which was split out of the target document on the twenty third of August. That split was correct and necessary. But the key's sibling, the ground truth file for the same target, states the same two defects in the same terms and has been on the public main branch since the twentieth of August at twenty one minutes past one in the morning. The target document itself is public too. Both experiment 55 runs started on the twenty third. The ground truth file also names which single edit would appear to cure both defects, and names the disagreement between two panel models that the control was built to settle, which is the experiment's design rather than merely its answers.

Both files now live outside any repository, in a folder called CDSFL experiment keys, with a README recording why the target is spent. The repository's ignore rules refuse the whole class by filename pattern.

A correction to what was reported at half past midnight. It was stated then that neither experiment 55 run produced a final report. They both did. The wrong filename was probed. What the reports actually say is that both runs halted at round one on an irreducible queue alarm, which is a more useful fact and does not change the conclusion that neither run produced a usable result.

### Finding 2 — the renumbering premise does not hold, and two other things do

The founder asked for the experiments to be renumbered by actual run order. Measuring first showed there is nothing to fix. Sorted by start time, the experiment number is already perfectly monotonic across all forty four non-empty run directories, with zero violations. The three apparent exceptions are empty directories written on the seventh of August by aborted re-invocations of experiments 35 and 36, which are not runs. Renumbering would also be expensive, because both the run directory name and the report filename embed the experiment number, so it would mean renaming fifty six directories and severing every document reference that points into them.

Two real problems sit underneath the request. First, four numbers in the span never ran at all: 50, 51 and 52 have configurations and no run directory, and 54 has neither. A reader counting the span infers twenty seven experiments; twenty three numbers produced a directory and twenty two produced a report. Second, each run's outcome is recorded in two places that disagree. Twenty of thirty one completion signals carry an empty reason field, and in seven of those the run report does name an outcome the signal lost. Tooling reading only the signal sees a converged run as incomplete. The runner's own source code names this defect and dates a partial fix to the eighteenth of May; runs after that date still show it.

A ledger now derives all of this from the artefacts rather than from anyone's memory, and fails if the committed copy stops matching what is on disk.

### Finding 3 — a convergence count in persistent memory was wrong

The persistent memory index recorded five straight convergences across experiments 42 to 46. The correct figure is four. Experiment 43 did not formally converge, and the repository's own recovery document said so all along, recording that its formal three consecutive convergence was blocked by one mechanical artifact. Its report holds no convergence record of any kind and its completion signal reads incomplete. The repository was right and the memory was wrong. Both memory entries corrected against the artefacts.

### Finding 4 — the scaling question now has a number

The founder asked for a specification framing this project as striving toward a general purpose STEM calculator on massively distributed compute and epistemic diversity, inspired by the at home projects without copying them.

The prior question is whether adding cognitive architectures buys coverage. The project's own coverage model says that depends on the correlation between architectures, and that correlation has been recorded every round all along without anyone summing it. Across two hundred and eighty nine observations in thirty one run directories the mean is 0.564.

At that correlation the fifth architecture contributes three point six percent of what the first contributes, and the panel fields five. Going from five architectures to fifty gains between two and five thousandths of coverage across every plausible detection rate. Optimal stopping lands between three and six, which derives the saturation figure the project has carried as an observation for months. It was never a property of the problem. It is a property of how correlated the available architectures are. The arithmetic was done twice, symbolically and numerically, agreeing to twelve decimal places.

The inversion from the volunteer computing projects is the substantive distinction. Those systems deliberately send duplicate work only to numerically equivalent machines, because disagreement between different architectures there is noise rather than information. This project's model says the opposite: when correlation reaches one, coverage collapses to what a single architecture achieves. Same shape, opposite objective.

Two things this project worked out independently turn out to have names in that literature. The planted defect controls are what is called spot checking, and its documented central caveat is precisely the failure this project has suffered five times: a spot check works only while it is indistinguishable from real work. And the standing refusal to let models vote on findings is collusion resistance, which at a measured correlation of 0.564 is not a stylistic preference but a necessity.

So the scaling axis is not the number of architectures. It is reducing correlation, where halving it is worth more than ten times the panel, and increasing the number of distinct bounded artefacts under review, where the work is genuinely parallel. Four falsifiable predictions are stated, including the uncomfortable one: at the current correlation roughly a quarter of consequence weighted defect classes are beyond the panel's reach whatever is spent.

### Finding 5 — a claim withdrawn, and the tool that refutes it

It was claimed on the twenty fifth of August that supersession across documents cannot be detected mechanically. The founder asked whether that was certain. It was too strong. A checker now detects the specific pattern that bit this project, a hold assertion that names the file holding the decisions where that file already carries a rulings heading, and it fires on the real historical file. Its first version also fired on a genuine hold recorded inside a dated entry from April with four months of later entries beneath it, which taught it the right rule: a hold counts as live only inside the newest dated entry, or inside none.

### Finding 6 — sv crashed, an hour after being declared working

At fifty three minutes past midnight the save command exited cleanly. At fifty two minutes past one the same command on the same tree exited with a traceback. Nothing in the repository had changed. This process had lost read access to the persistent memory folder.

Under that condition the folder still reports that it exists and that it is a directory, while every attempt to list or read it fails, and the pattern matching call used to find files returns an empty list without raising an error at all. Every memory access in the save routine and in the drift guards was gated on existence rather than on readability, so no guard fired. The save routine crashed outright. One drift guard reported that no note standard files were found, asserting absence where there was only denial, inside the guard written the previous day to catch exactly that class of mistake. Another died with a type error, a permission denial wearing the costume of a different defect entirely.

The distinction now enforced throughout is that absent and unreadable are not the same thing. Absent means there is nothing to count. Unreadable means the count did not happen, and must never crash the save, never write a zero, never pass silently, and above all never refresh the counted date on the ledger, because that date is a claim about when the number was last verified. The save routine now says so out loud and exits cleanly, and the stamp was verified to have stayed at the last successful count.

While falsifying the tests for that fix, one of the three deliberate breaks turned out to be a no operation, because of a mis-escaped pattern. The tests passed and proved nothing. It was redone correctly and fails as it should. A falsification that does not falsify is worth less than none at all, because it manufactures confidence.

### Finding 7 — sv's completion report was answering a different question

The founder asked why a push does not leave local and remote fully in sync, since that is the point of the exercise. The answer is that nothing was failing in the push. The save routine reported the state of the remote before the save and a yes or no for whether a push happened, and stopped. Neither is the state after the save. It also printed the words state save complete before committing and pushing, and then did more work.

It now measures again afterwards and reports one block last, which re-reads the commit, the branch, the working tree and the remote. On a side branch it reports both facts together: that the branch itself is fully in sync, and that public main is however many commits behind and does not show the work. That second sentence is the one that was missing, and it is the whole answer to the founder's question.


## Test state

Sixty seven new tests were added across six files during this window, every one of them falsified by deliberately breaking the thing it tests. The full suite result at the close of the window is recorded in the chat summary and in the final commit of this window.


Written under CDSFL note standard v1.6 (24 August 2026).
