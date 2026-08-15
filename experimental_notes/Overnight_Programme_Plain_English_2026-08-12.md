# The overnight programme, what it found, and the six things that need a ruling

2026-08-12, from about one in the morning to just before four. One paid model dispatch, roughly three pounds. Everything else offline.


## What was run

The agreed programme had four parts. Three approved repairs. Three build and measurement tasks. Two pieces of external research. And a set of reporting duties.

All of it ran. The work was carried out by fourteen separate agents working on separate files at the same time, followed by an independent checking pass over the whole result, and a final gate that refused to approve the work until a blocker was cleared.

The gate was right to refuse, the blocker is now fixed, and the full test suite stands at three thousand four hundred and eighty one passing with none failing.


## The headline, which is a correction rather than a discovery

The warning that started this was that the system produces large numbers of false accusations against documents containing no errors. That warning was mine, and it was wrong.

The document in question does contain errors. Real ones, in working code, that nobody planted. The accusations the panel made against it are correct. They were checked line by line against the document's own source.

There was no epidemic of false accusations. There was a false premise, and it was mine.

The phrase zero plant control means only that nobody deliberately hid an error. It was treated as meaning the document contains no errors at all. Those are different things, and a document nobody deliberately broke can still be broken.

Two separate lines of evidence arrived at this independently on the same night, which is worth stating because neither knew about the other.

The first was direct measurement. Two pieces of code in the document are genuinely wrong. A rate limiter that can be tricked into creating budget instead of spending it, by asking for a negative amount. And a routing table that sends data to the wrong server whenever a key lands exactly on a boundary. Both were found by the panel. Both are real. Both are still there.

The second was the external research, which reached the same place from mathematics rather than inspection. On a document containing no errors, the standard measures of a detector's quality collapse. Precision becomes exactly zero for any detector with any false alarm rate at all, however good it is, because there are no true findings to divide by. Recall becomes undefined, zero divided by zero. So neither number carries any information about how good the detector is. There is an established result, from work on intrusion detection published in 2000, showing that when the thing being looked for is very rare the alarm rate dominates entirely, and that no amount of consensus between reviewers repairs it.

The project's own scoring script already refuses to report either measure for this control. That refusal turns out to be exactly right and to match the literature.


## Why the same faults keep reappearing

Comparing the two runs against this document, three days apart, shows a loop.

The first run found the faults. The response was to rewrite the claims so they no longer covered the faulty behaviour. The rate limiter claim gained the words under single threaded use and unit cost requests, which are precisely the two problems the panel had reported. The code itself was never changed.

So the second run found the same faults again, because the code still had them and because the panel reviews code rather than sentences.

This is a scope mismatch rather than anybody's carelessness. The record of what is true covers the claims. The review covers the whole document. A fault in code that no claim describes can be neither confirmed nor denied against that record. It is unscoreable by construction, and rewording will never end it.

The checking of the claims themselves was thorough. Every claim was executed rather than read, using symbolic algebra, a constraint solver, dimensional analysis and random sampling. The claims are true. The code is faulty. Both statements hold at once.


## A second fault, which was quietly destroying the best evidence

When a model writes a proof, it hands back a small program wrapped in the formatting marks that separate code from prose. The system extracted the program by reading from the opening mark to the first closing mark it found.

Some proofs need to read the document and pull the code listings out of it, which means those proofs have to mention those same formatting marks in their own text. The extractor saw the mention, took it for the end, and cut the program off mid sentence. What remained looked like a program, was not valid, and failed the moment it ran.

The direction of this is the serious part. A proof that pastes its own private copy of the code survives untouched. A proof that opens the real document and works from what is actually there destroys itself. The extractor was penalising the more rigorous approach and sparing the lazier one.

Across the whole archive this affected about two proofs in every hundred. Within the control run it affected nearly half, and the reason is exactly what the mechanism predicts. That is the only target which is a written document with code inside it. All the other targets are plain source files, which a proof can load directly without ever mentioning a formatting mark. Every remaining planned experiment uses written documents, so this would have grown worse.

It is fixed. The closing mark must now stand alone on its own line, which distinguishes a real ending from one quoted inside a piece of text.


## Something valuable that follows from that fix

The proofs were never lost. They survive in the raw record of what each model said, and only the extracted copies were damaged.

Re-reading that raw record with the corrected extractor recovers forty two working proofs, all of which run, where the stored version had twenty six of which twelve could not run at all.

This means the control experiment does not need to be paid for again. It can be re-scored from material already held, and the re-scored result rests on better evidence than the original run produced.


## What the five model panel said

One paid dispatch, five models, run without any requirement that they agree.

All five independently proposed the same primary mechanism, and it is the one the founder has been asking for since the beginning of August. Rather than trying to infer what a proof meant from the words around it, require it to state its numbers. What value was claimed. What value was actually computed. Then compare the numbers rather than interpret the prose. Five frontier models given the problem cold reached for the founder's own answer.

Four of the five rejected the false premise in the question without being prompted. The one that accepted it produced the weakest answer of the five, and discarded a useful mechanism as a direct result. That is a clean demonstration of why models should not be pushed toward agreement.

One model destroyed a recommendation that had already been made. The recommendation was that if a proof never opens the document it accuses, the accusation should be blocked. The objection is that a rule which checks whether a file was opened, rather than whether the conclusion depends on its contents, is one line of code away from being defeated. A model that learns its accusations are rejected simply opens the file and throws the contents away. The measurement then reports perfect compliance, discriminates nothing, and moves in the direction that looks like success.

That recommendation is withdrawn. The replacement proposed in its place does not need the correct version of a document, only a disturbed one, which requires knowing nothing at all. The machinery perturbs the accused passage, separately perturbs an unrelated passage, runs the proof against each, and reads the result off a short table. That distinguishes a proof that genuinely depends on what it accuses from one that does not, and it also identifies equipment failures for free, because an equipment failure is unaffected by the document's contents.


## What was repaired tonight

The verdict reader no longer decides whether a failure is equipment breakage by checking whether the author used one of three particular words in an error message.

The extraction fault described above.

Three routes by which a proof could still reach the material that states the answers.

A naming check that failed to notice one of five simulated agents.

The quality control sweep, which reported one hundred and thirty seven broken document references and now reports none, with the arithmetic published so the reduction can be checked rather than trusted.

A gap in the safety net around configuration. A previous fix made the two paths that read configuration agree by construction, and a test enforces it by walking every field. But a renamed setting is not a field, so it was invisible to that test. One such rename exists, covering a component enabled by seventeen configurations. Breaking it would have silently switched that component off with every test still passing. The new test discovers renames by inspection, so future ones are covered without anybody remembering.

And a switch that should have existed. One of tonight's agents connected a mechanism and armed it at the same time. The next live run would have started refusing accusations on grounds the founder has not yet ruled on. It now records what it observes and changes nothing, and arming it requires a deliberate decision.


## Five times the evidence contradicted the person reporting it

This is recorded because the pattern is the point, not because anybody needs reassuring.

The claim that the panel produces false accusations against clean documents was refuted by reading the document.

A claim that resumed runs had been silently losing their proofs was refuted by finding a second, separate record that had been preserving them all along.

A claim that a fourth configuration fault had been found was refuted by discovering the fix already present and already tested.

A claim that a component was switched off everywhere was refuted by finding it enabled under an older name.

And the date on ten files was wrong by two days, because it was typed from memory rather than read from the clock, which is a mistake with its own standing instruction.

In each case the correction came from a measurement that took under a minute.


## The six things that need a ruling

One. The two real faults in the control document. They can be repaired, or kept and written down as known true faults, or the document can be retired. Keeping them and writing them down is recommended, because a document with two known faults measures both false alarms and missed detections, whereas a clean document can only ever measure false alarms, and a review system that quietly stops noticing things is the more dangerous failure.

Two. Whether to arm the mechanism described above. It is currently connected and recording. Arming it changes the most load bearing rule in the system, and the panel refuted the design as originally proposed. The recommendation is to leave it recording, gather the evidence, and build the perturbation test instead.

Three. A direction of travel that needs watching. The verdict reader fix moves some past results from confirmed to equipment error. On the archive nothing moves, because every affected entry is already in a final state. Going forward the direction is not automatically safe, because a finding that stops counting can bring a review to an end sooner rather than later. This deserves an explicit decision rather than being discovered later.

Four. The load balancer. The research confirms the founder's reasoning about large scale work and calls it stronger than the founder stated it. It also finds that this particular component does not serve that purpose, has never run outside its own tests, and contains a fault where an impossible allocation is reported as a successful one. It also contains a description of itself that has been false for four and a half months and was already reported once. Recommend retiring it and treating the scaling question as a separate design problem.

Five. One component described in project records as running in shadow leaves no trace in any run. It is not running at all. It should either be connected so it produces evidence, or described accurately.

Six. A record of claims that survived challenge was built four days ago without an explicit decision and is not connected to anything. It should be connected or the claim that it exists should be withdrawn. It is currently the clearest example of the ambiguous state that everything else here is being cleared out of.


## The state of things

Nothing has been committed and nothing pushed. The main read me file is untouched, verified by comparing its contents rather than trusting a status listing. No experiment is running. The test suite passes in full, and the network guard confirms that all forty one attempts to reach outside during the tests were blocked, so nothing in the test run cost money.

Written under CDSFL note standard v1.2 (14 May 2026).
