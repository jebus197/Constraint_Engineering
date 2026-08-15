# Today in full, and the decisions needed

2026-08-01 23:05 BST


## The short version

The founder's read is correct. This is a routing fault, and the other specialist types exist precisely to handle it. Nothing found today contradicts that, and the measurements support it directly.

The project is closer to the goal than it feels tonight, and the numbers say so rather than the narrative. The six clean convergences were real and they still stand. Two of them, the chemistry exam and the engineering exam, were English documents carrying their arguments in prose, tables and equations. Both converged. Between them they produced seventy five findings and exactly one went to a human, and that one was cleared automatically afterwards. The instrument already works on prose STEM.

What broke was narrower than it looked all day. One document shape, English prose containing printed code listings, meets one stage of the system that was never told such documents exist. That is it. It is a prompt, not an architecture.


## The finding that matters

There is a ladder. When a model fails to produce a working test for a defect, the finding goes to a stronger model, then a stronger one again. That ladder is the only thing between a finding and the human queue.

The instruction sent up that ladder is written for program code only. It tells the model to import the module under review. The packet handed alongside carries the finding's identifier, its description, which model raised it, and its severity. It does not carry the document's location, and it does not carry the document's text.

So a model asked to test a defect in a printed listing inside an English document is told to import a module that does not exist, and is never told where the document is. Both rungs fail. The system then records the reason as, no model produced a runnable test. That sentence is false. No model was ever given the target.

The numbers. On the two exams with no printed listings, the ladder resolved forty one findings out of forty one attempts. On the two attempts at the control document, which does carry printed listings, it resolved zero out of twenty five, and the run halted at round three of sixteen.

A fourteen line test that simply opens the control document by name and exercises the listing returns a confirmed result from the system's own verifier, for the very finding the instrument had called impossible. The findings were always computable. The instrument withheld the input and then recorded the failure as irreducibility.

Notably, the end of run sweep instruction was already made document aware today. The ladder was not. That asymmetry is the whole defect.


## Three things stated earlier today that were wrong

One. A note written into the control experiment's configuration blames the halt on the fix scoring machinery. That is mechanically false, and it was written by this session. Every route to the human queue was traced and none of them sits in that pipeline. If the control is restarted on the strength of that note it will halt again in the same place. The note is being corrected tonight.

Two. Today's repair was framed as a possible risk to prose convergence. It is not. Both exams converged under the worst version of that code the project has shipped, and in both runs the fix verification stage verified nothing at all. Every closure came from the demonstration stage instead.

Three. The fifty one tests written today measured neither convergence nor human queue load. No test in the set touches a convergence gate or a queue counter, and none asserts that any finding ever reaches a closed state. They prove the machinery declines to close things wrongly, which is worth having, but that is not what was claimed for them.


## One thing that needs a ruling, and cannot be engineered around quietly

The end of run sweep is the mechanism relied upon to clear findings that were raised in error. Every clearance it has ever made was examined. There are eight in the whole archive, and the most serious it has ever touched scores point six six. The line above which a finding counts as serious is point seven.

So the sweep has never cleared a serious finding and structurally cannot. One path discards the request unread above that line. The other refuses even to record a correct negative verdict.

The number that decides this is assigned once, at intake, by a model, and is never recomputed. A finding scored point six nine is cleared by the machinery. A finding scored point seven one becomes permanent human work. The instrument tolerates two such residents before it refuses to converge at all.

There is a good reason behind the underlying rule, and it is backed by evidence from an earlier experiment where two of three negative verdicts on serious findings turned out to be wrong. The rule is not the problem. The problem is that when the computation runs and returns the answer this claim is actually fine, that answer is discarded rather than shown to anyone.


## What proceeds tonight without any decision

1. Make the ladder instruction document aware. This is the blocking item and it goes first.
2. Correct the false note in the control experiment's configuration.
3. Run the end of run sweep on a halt and on a round limit exit, not only on a convergence. It was configured for the control run and never executed because the run halted.
4. Correct the panel instruction, which still tells every model every round that fixes are linted, tested and closed on a clean pass. On an English document none of that now happens.
5. Fix the test transport that truncates any test carrying its own code fence, then reinstate the four tests that were skipped because of it.
6. Require a confirming test to also pass cleanly against a corrected copy of the document. This closes a newly found hole where a valid but logically wrong test closed a finding against a claim that was true.
7. Give a route out to the thirty eight findings across ten archives that are stuck with no way forward and remain exposed to a late objection that blocks convergence.
8. Stop re dispatching findings up a ladder that has already been recorded as exhausted. Pure cost saving.
9. The linter success message that is being counted as a violation, which has been quietly confirming code quality findings that do not exist across the whole arc.
10. The launch check that refuses to start a run whose settings contradict its target, and the feed that tells the panel why its repairs were rejected. Fifty rejections across four rounds and no model was ever told.
11. Documentation sweep across the glossary, the architecture document and the queue.


## Decisions required from the founder

1. The control run. Recommendation: neither restart nor resume until the ladder fix lands and its configuration note is corrected. Then restart rather than resume, because four of its rounds were produced by broken machinery.

2. The five remaining prose targets do not exist yet. They are named in the physics, biology and capstone configurations but have not been written. Recommendation: author them with their claims in prose, tables and equations rather than in printed code listings. The two exams that converged had no printed listings and produced one human escalation in seventy five findings. This decouples the whole remaining arc from the ladder defect and costs nothing. This is probably the single highest value decision available tonight.

3. The serious finding ceiling described above. Either accept it explicitly, or authorise recording the computed answer even where the sweep declines to act on it, so that a human adjudicating a permanent resident at least sees the computation the instrument already performed and discarded. Recommendation: record the answer at minimum.

4. The queue alarm now halts the run outright rather than merely refusing to declare convergence. That change was made today and is stronger than what was originally specified. Confirm whether halting is intended.

5. Whether to spend a few pence on a single dispatch confirming that a model actually reads the new document markers before any paid run.

6. Whether tonight's commits should be pushed. They are local only. Nothing in them is sensitive.

Two older decisions remain open and unchanged. Whether to delete the experimental branch once the merge to the main branch is confirmed by hand, and whether to regenerate the three exams whose answer keys sit in public history. On the second the founder already judged the exposure overstated and elected to move on.


## One honest boundary

No run has completed under the current code. Every archive on disk predates today's repairs, and both the ladder and the end of run sweep dispatch live models and cannot be exercised offline. Everything above is anchored in code read at the current commit, in offline harnesses driving the real functions, and in archives from the earlier instrument. One completed control run after the ladder fix is what would settle the true figure.

Written under CDSFL note standard v1.2, 14 May 2026.
