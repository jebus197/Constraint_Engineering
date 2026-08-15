# The four rulings, explained properly, and an honest assessment of the literature cell

2026-08-03 22:15 BST


## Why this document exists

The four outstanding decisions were previously summarised in a line each, which is not enough to rule on. Each is expanded here to the point where a decision can actually be made. The fifth is already settled. The sixth, the literature cell, is assessed separately at the end because the question asked was whether it demonstrably works, and that deserves evidence rather than reassurance.


## Ruling one. The stopping rule, and what happened to the previous ruling on it

What the system does now. When the panel finds a problem, that finding is filed against a location in the document, meaning a particular named section, function or claim. The run stops when three consecutive rounds pass with no new serious problem found. But new is judged by location. If the panel finds a second, genuinely different serious problem in a place it has already flagged, the system does not count it as new.

So the honest description of what stopping currently means is: three rounds with no new serious problem in a place not already mentioned. That is narrower than what a reader would assume, which is three rounds with no new serious problem at all.

Why this arrangement exists at all. Before it, findings were counted by the label the model chose, and models relabel the same defect every round. That produced an experiment that found the same four real defects over and over and could never recognise it had finished. Location keying fixed that and unblocked the whole arc. It is not a mistake; it is a trade.

What was ruled on 31 July, and what happened. Three options were put forward. Leave it and state the limitation plainly. Revert to the older label based counting. Or build the missing piece that would separate two different problems in the same place. The ruling was to reject the first two and build the missing piece.

That build was measured before it was written, and it failed. Two approaches were tried. The first compares findings by meaning using a language model's own sense of similarity: it scored the two test cases at zero point six eight and zero point seven eight, both above the threshold, which means it declared two genuinely different problems to be the same problem. The second compares the actual words used: it correctly separated the test cases, but when run against six completed experiments it destroyed convergence in all six, because ordinary rewording between rounds then reads as a brand new problem. So the cheap version does not work, and a working version is real research rather than an afternoon's engineering.

That is why the ruling is being brought back. It could not be carried out as given, and I do not think that was ever reported back clearly.

The three options as they now stand.

Option A. Leave the rule as it is and state the limitation plainly in the results and in any paper. This costs nothing and delays nothing. It is also already partly covered: a separate check written for this purpose examines the final rounds of every completed run and reports any serious finding that arrived late and was not resolved, so the thing the rule could miss is looked for afterwards rather than hidden.

Option B. Revert to the older label based counting. This would have refused two of the three experiments that have stopped under the current rule, meaning those runs continue and cost more money, and it reintroduces the exact defect that stalled the arc in June.

Option C. Commission the real version. Genuine research, unknown duration, and it delays everything remaining.

Recommendation: Option A. The limitation is real but it is narrow, it is checked after the fact, and stating it plainly is more defensible than a mechanism that has not been shown to work. Option C can be revisited after Bench Run 2 if a reviewer presses on it.


## Ruling two. Restart the control run, and now restart it first

The control is the experiment with nothing wrong planted in it. Its purpose is to measure what a panel produces when there is genuinely nothing to find, which is the only way to know how much of a normal run's output is real. It was started on 1 August, spent four rounds, and halted.

Why restart rather than resume. Those four rounds were produced while the routing ladder was blind, so thirteen findings were locked into an unresolvable state by a fault rather than by anything real. Resuming carries that artefact into the one experiment whose entire purpose is to measure what a panel leaves behind. The four rounds already spent are a sunk cost of roughly twenty dollars.

Why it should now go first rather than last. A measurement taken tonight changes the ordering. The property that broke the control was printed code listings inside an English document. Counting those across all six exam documents: chemistry and engineering have none, and both converged. Physics has none. Biology has six, but they are one to four lines each with no function or class definitions, so they are short expressions rather than the kind of printed listing a finding refers to. The capstone has six genuine executable listings of nine to twenty lines. The control has seven.

So the control is the hardest case for the repair, and the capstone is the second hardest. Running the control first tests the repair where it is most likely to fail, for about twenty dollars, before the capstone is committed to. If the control converges, the capstone's risk drops sharply. If it does not, that is discovered cheaply.

Recommendation: restart, and run it first.


## Ruling three. The serious finding ceiling

Every finding carries a number for how serious it is, assigned once, at the moment it is raised, by the model that raised it. It is never recomputed.

At the end of a successful run there is a tidying pass that clears findings raised in error. Every clearance that pass has ever made was examined: there are eight in the entire archive, and the most serious it has ever touched scores zero point six six. The line above which a finding counts as serious is zero point seven.

The pass has therefore never cleared a serious finding, and it cannot. One route discards the request unread above that line. The other refuses even to record a correct negative verdict above it.

So a finding scored zero point six nine is cleared by the machinery. A finding scored zero point seven one becomes permanent human work. The instrument tolerates two such items before it refuses to declare a run finished at all.

There is a good reason behind the underlying rule. It comes from an earlier experiment where two of three negative verdicts on serious findings turned out to be wrong, so only a positive demonstration is allowed to settle a serious finding. That rule is sound and is not what is being questioned.

What is being questioned is narrower. When the computation runs and returns the answer this claim is actually fine, that answer is currently discarded rather than shown to anyone. A human adjudicating a permanent item never sees the computation the instrument already performed.

The options.

Option A. Accept the ceiling explicitly, and state in the results that a false alarm scored above the line is permanent human work.

Option B. Record the computed answer even where the tidying pass declines to act on it, so the human sees the evidence. Nothing is cleared automatically; only the record improves. Small change, no weakening of the underlying rule.

Option C. Allow a narrow demotion: a serious finding whose test passes cleanly against both the document and a corrected copy may drop one band, with the evidence attached. This is a real change to the rule and would need care.

Recommendation: Option B at minimum. It costs little and removes the specific absurdity of discarding an answer the machine already has.


## Ruling four. Should the queue alarm halt the run

There is an alarm that fires when too many findings pile up in an unresolvable state. Its purpose is to detect a mechanical failure, because a large pile of genuinely unresolvable findings almost always means something is broken rather than that the document is unusually hard. It was proved right on 1 August: the pile was caused by the routing ladder being blind, and raising the threshold twice to get past it was wrong both times.

Yesterday its behaviour was strengthened without a ruling. It previously refused to let the run declare success while continuing to run. It now stops the run outright.

The difference. Halting stops the spend immediately and preserves the state for inspection, but ends a run that might have recovered in later rounds. Refusing to declare success lets the run continue to its round limit, which costs more but gathers more evidence.

Recommendation: keep the halt. The alarm fires on a condition that indicates broken machinery, and continuing to spend money on broken machinery gathers evidence about the fault rather than about the science. But it was changed without asking, so it should be confirmed rather than assumed.


## Ruling five. Already settled

A single small paid dispatch to confirm a model reads the new document markers before any full run. Approved. It will be run before the control restarts.


## The literature cell. An honest assessment

The question asked was whether the work done means the cell now demonstrably feeds real material back to the panel and influences outcomes, and whether that can be confirmed irrefutably.

The honest answer is: the machinery exists, the path was demonstrated end to end, and it has never once run live. Three separate things, and they should not be run together.

What is genuinely proven. The retrieval half is real and was demonstrated against live sources: papers are found, downloaded, parsed and distilled into a brief, with the citation, the retrieval path, the number of characters actually parsed and a content hash recorded. One hundred and twenty nine tests covering the cell pass. Two switches exist in the runner: one renders the brief into the next round's prompt, and one feeds the corroboration and novelty measures into the mathematics.

What the proof actually proved, and what it stubbed. A dedicated harness exists that prints the artefacts rather than asserting success: the actual prompt string with the brief inside it, and the corroboration measure taking a non zero value. That is real evidence that the plumbing carries a brief to the point where a model would receive it. But the harness discloses its own stubs, and they matter. No paid model was called. The panel dispatch was replaced by a recorder that captures the prompt and returns a canned reply. The immune pipeline was replaced by an offline stand in. And the reader that judges whether a paper is relevant was set to none, falling back to a mechanical text method which is known to over rate relevance, which is why the shipped default refuses to inject briefs judged that way at all.

So: proven that a brief reaches the dispatch boundary. Not proven that a real panel receives one, reads it, and changes its findings because of it.

What the configurations actually say. All eight remaining experiment configurations do switch the cell on, so it will run and produce briefs. But neither of the two switches that let those briefs reach the panel is set, so they default to off. Checked against every archived run: the number that have ever had brief injection enabled is zero.

So the cell is on in the sense of running and observing. It is not on in the sense of influencing anything.

Is more work needed. Not much building. Turning it on is a configuration change, not a construction project. Two things would need attention. The reader that judges relevance defaults to a cheap model rather than the mechanical fallback, and that has been wired but never exercised in a live run. And roughly six percent of findings contain nothing but code or internal labels, so the search falls back to a fixed phrase which is itself meaningless; that wastes a retrieval and deserves a small fix.

The reason to be careful about timing. The capstone is a controlled comparison between four conditions. Chemistry and engineering already ran with the cell observing only. If the remaining legs run with it influencing the panel, the comparison is no longer between the things it was designed to compare. Switching this on mid arc would confound the capstone.

Recommendation. Leave the switches off for the remaining arc so the comparison stays clean, and treat the first live use as a declared change either within Bench Run 2 or as a dedicated run of its own. The work to enable it is small and can be scheduled deliberately rather than slipped in.


## One thing found tonight that needs no ruling

The control document's recorded fingerprint is stale. The manifest exists so that a result can be tied to the exact document that produced it, and it still records the version from before the seven claim repairs made on 1 August. It must be corrected before any run. Minutes of work.


## Two corrections to the record

The five remaining exam documents were previously described as not yet written. That was wrong. All six exist, were authored on 29 July, and are tool verified and panel reviewed. The recommendation to author them without printed code listings is withdrawn: rewriting them would discard validated work.

The claim that a bench run could have recorded a Wolfram authentication error as a mathematical result was also wrong. The tool is not in the pipeline and never has been, so a bench run would never call it. The hazard was real but confined to analysis work, not experiments.

Written under CDSFL note standard v1.2 (14 May 2026).
