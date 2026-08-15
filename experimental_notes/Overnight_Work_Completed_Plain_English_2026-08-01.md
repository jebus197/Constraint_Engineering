# What was done overnight, and what is still waiting on a ruling

2026-08-01 23:39 BST

## Read this one first

This is the only document needed in the morning: it carries both what changed and
every decision outstanding. The earlier note *Today in full, and the decisions
needed* remains accurate but is superseded on the decisions list, because two of
its eleven work items are now a founder call rather than pending work.

Nothing done overnight requires a decision to be revisited. All five rulings stand
exactly as stated earlier, and none of the overnight work depended on any of them.

One correction to this document itself: it was first written with times just past
midnight on 2 August, while the system clock read 23:39 on 1 August. The times were
estimated rather than read — the one thing the timestamp rule forbids — so this
file and its TTS companion are renamed to the date they were actually written. A
file dated 2 August does not exist.


## The short version

Seven items closed, all offline, no money spent. The agreed must do list is now complete, and so is the item that was on no list at all and turned out to be the actual blocker. The test suite stands at 2521 passing, none failing, with no network access.

The five decisions from the earlier note are all still open and none of them held any of this up.


## The blocking item, done first

The routing ladder now knows what it is looking at. On an English document it receives the document's location, the document's text, and an instruction to open it by name and extract the listing a claim refers to. Previously it received the finding's identifier, its description, which model raised it, and its severity, and was told to import a program module that does not exist.

The measurement that justified this was forty one successful resolutions out of forty one attempts on documents without printed code listings, against zero out of twenty five on the document that has them.

Two smaller repairs travelled with it. The failure message no longer claims something it cannot know: instead of no model produced a runnable test, it now records how many rungs actually reached a model and that none returned a test the system could confirm. And both versions of the instruction now warn against putting a code fence inside the answer, which is the transport fault that truncated two of five test cases into errors.

Fifteen new checks guard this. There were none before, for either instruction.


## The note that would have wasted the next run

A note written into the control experiment's configuration blamed the halt on the fix scoring machinery. That was wrong, and it was written earlier the same day by this session. A restart on the strength of it would have hit the same wall at the same round. It now carries the traced evidence and names the real cause.


## The cleaner now runs when a run fails

The end of run sweep was switched on only when a run converged, which meant it was off in exactly the runs with the most left over. The control run had it configured for two rounds and ran none of them, because it halted. It now runs on a halt as well, states plainly in the log that the run did not converge, and records which trigger fired so that a tidying pass can never later be mistaken for a success. It still cannot rescue a failed run: it adds no findings, it runs after the verdict, and serious findings remain demonstration only inside it.


## The panel is no longer told something untrue

Every model, every round, was told that a proposed fix gets applied to a copy, checked by three tools and a test suite, and closes the finding if all pass. On an English document none of that happens, and yesterday afternoon's repair is what made the sentence false. A panel reading it would reasonably conclude that writing a good fix is the way to settle a finding. It is not. The instruction now says so, and names the runnable test as the route that does work, while still asking for fixes because they are useful to a human reader.


## A quiet fault that had been running the whole arc

The code quality checker was counting the linter's own success message as a violation. A clean file produced the report all checks passed and the system read that as evidence of a defect, and confirmed the finding. Reproduced against the real tool before and after the repair.

This one is worth understanding because of where it leads. A confirmation of this kind raises a finding's severity, and severity is the single number that decides whether the end of run sweep is allowed to clear a finding later. So it was inflating precisely the population that becomes permanent human work.


## The launch now refuses rather than warns

Three checks, deliberately not ten. Everything the system can correct by itself it already corrects, and a check that re-argued those would be noise that gets switched off. What is left is what cannot be fixed once a run is under way: the document must exist and not be empty, the routing ladder must be switched on for an English document because it is the only absorber before the human queue, and the demonstration gate must be switched on because with fix scoring off it is the only route to a settled finding.

It stops the run. A warning is a thing a tired person scrolls past.

A correction comes with it. The earlier claim that all eight queued configurations fail three of three launch checks was repeated twice and is false. All eight have both switches on, seven of them under an older key name. Their only failure is the missing document, five of six of which have not been written yet. That figure predated three of the repairs.


## The panel is now told why its repairs were declined

Fifty repairs were rejected across four rounds of the control run and no model was ever told, so every round the panel proposed into a gate it could not see. Each active finding now carries the reason where the panel will actually read it: which gate refused it and that the repair did not settle the finding, or that repair scoring does not apply here and a runnable test is what settles it instead, or that its test failed to run, or the real reason it was passed to a human. A healthy finding adds nothing, because this is rendered for every finding on every round.


## Two things caught by guards written earlier

Both are worth recording because they are the pattern that worked.

The linter repair flipped an earlier characterisation check from one verdict to the opposite one. That check carried its own instruction for exactly this case: if this stops holding, the parsing was fixed, so re-measure rather than delete. Re-measured. The finding is that the fault changed sign rather than shrinking. Before, a tool that never opened the document voted to confirm a finding and inflate it. Now it votes to dismiss it. What prevents both is a separate guard which is on in every real run.

The panel feedback work tripped a structural guard that limits which parts of the system may read the repair scoring record at all. It went red, correctly. Widening it was the documented remedy, but being made to look again revealed that the first version was putting a numeric score into the panel's prompt, which opens a channel from the repair pipeline into the discovery stream for no benefit. A panel can act on the syntax gate refused this. There is nothing to do with zero point zero. Removed.

The tests that survived contact overnight were the ones asserting a property and carrying a note about what to do when they fire. The ones that broke were asserting a symptom.


## Still waiting on a ruling

One. The serious finding ceiling. The end of run sweep cannot clear a serious finding and structurally never has, so a serious finding raised in error is permanent human work decided by a single number assigned once by a model and never recomputed. The instrument tolerates two before refusing to converge. Either accept that explicitly, or authorise recording the computed answer even where the sweep declines to act on it. Recommendation: record it at minimum.

Two. Whether the five unwritten documents should carry their claims in prose, tables and equations rather than printed code listings. This is free and decouples the remaining work from the fault fixed tonight. Probably the highest value decision available.

Three. Whether the queue alarm should halt a run outright, as it now does, or merely refuse to declare success.

Four. Whether to spend a few pence confirming a model reads the new document markers before any paid run.

Five. Whether the night's commits should be pushed. They remain local.

And the control run itself, which should now be restarted rather than resumed, but only after decision two is taken, because the answer changes what the remaining documents look like.


## What is left that needs no ruling

The thirty eight findings stuck with no route to a settled state. The hole where a valid but logically wrong test can settle a finding against a true claim. The transport truncation and the four checks currently skipped because of it. Clearing the flag that makes the system re dispatch findings up a ladder already recorded as exhausted, which is pure cost. The log that writes into the run archive when it should not. And a documentation sweep.

Written under CDSFL note standard v1.2, 14 May 2026.
