# The pipeline now runs end to end, and it was tested by a panel it did not write

2026-08-04 04:08 BST


## Read this after the earlier overnight file

An earlier document was written at one sixteen this morning and covers the routing repair and the panel review. This one covers everything after that. The two together are the full night. Nothing in either needs a decision before you read them.


## The short version

Until tonight, almost everything repaired this week had only been tested in isolation. Each part worked when checked on its own. Nothing had been run through the whole machine from one end to the other. That gap matters more here than it sounds, because the project's recurring failure has never been a broken part. It has been two working parts that disagree at the join, and no test of a single part can see that.

The whole machine has now been run, on a document with a known planted error, reviewed by five independent agents who were not told what the error was and were forbidden from looking it up. Twelve stages, all twelve correct. The planted error was found and demonstrated five separate times. Nothing false was confirmed.


## What the run actually did

The document is a short technical reference, about one hundred and fifty lines, with seven claims and exactly one deliberately false claim, plus two runnable code listings. That last detail matters: printed code inside an English document is the exact shape that halted the control experiment last week.

Five agents were each given the document and the review rules and told to find false claims and prove them. Proving means writing a small program that fails only if the error is genuinely there, and running it before reporting. They were barred from opening the file that holds the answers.

Their findings were then put through the real machinery, not a copy of it: the document-type check, the launch guard, the repair scorer, the verification step, the panel briefing, the demonstration gate, the feedback that tells the panel why something was refused, both measures of what counts as a new problem, and the stopping rule.

All five found the planted error. Each wrote its own proof, and the machine re-ran every one rather than taking the agent's word. Five independent demonstrations of one real defect. The one claim raised against a true statement was correctly not settled, and went to the human queue instead of being accepted.


## The thing it found that nothing else would have

On its very first run, before any of the above, it failed. Both findings that carried a proof came back as errors and were escalated to a human as unresolvable.

The cause was a placeholder. The stored proofs contain a marker where the document's location should go, and that marker has to be filled in before the code will run. Fed through unchanged, the code was broken on arrival.

Every individual part was correct. The join between two of them was not. That is precisely the failure this project keeps meeting, and precisely what a test of any single part cannot see. Finding it on the first pass is the strongest argument for having built the thing at all.


## A check that earned its place immediately

Before running the panel, a check was added that compares what an agent claims against what the machine can confirm. Every agent is asked whether it actually ran its proof.

All eight findings claimed yes. The machine could confirm seven. One came back as an error: a claimed demonstration that is not one.

That single discrepancy is the entire argument for the rule that only a re-run demonstration settles a serious finding. Not a principle argued in the abstract, but a case that appeared the first time anyone looked. It is why the answer to "the model says it verified this" must always be to check.


## One decision waiting for you just got smaller and cheaper

The open problem was this: a proof can be valid code and still be wrong, firing when the claim it tests is actually sound. That would close a finding against a true statement. The fix I had in mind was to run each proof a second time against a corrected copy of the document, and treat a proof that fires on both as not discriminating. Building that looked like real machinery, and it touches the most load-bearing rule in the system, which is why it was left for you.

One of the agents did it without being asked. It ran its own proof against a corrected version of the document, recorded that the proof stayed quiet and exited cleanly, and reported that alongside its finding.

So the control does not need to be built. It can simply be asked for: write the proof, and also show it does not fire when the claim is sound. That is a change to what the panel is told, not a change to the verification rule.

This splits the decision cleanly. Recording the result and passing it to you, changing no verdict, is already covered by the ruling you gave on the third question and needs nothing further. Only the stronger version, where the machine automatically downgrades a proof that fails this test, still needs your ruling.


## An agent corrected me

One agent's second finding concerns a subtlety in how the language decides whether two values are the same: it checks whether they are literally the same object before checking whether they are equal. That is exactly the point I got wrong earlier in the night, when a demonstration I ran contradicted the label I had put on it.

It rated the issue as minor, which is correct. But it is worth recording that the method caught its own operator, again.


## Also built since the earlier file

The combined measure you proposed is now built, switched off by default, and recorded alongside the existing one on every future run at no cost. It compares findings by their hard content, meaning numbers, claim labels and code names, rather than by their wording, and it does so only within a location the system has already flagged. The report will now also name the specific findings where the two measures disagree, so what you get back is a list of cases to look at rather than two rows of numbers.

Nothing has been promoted. The plan remains to gather four runs of paired evidence for free and decide before the large benchmark.


## What is waiting for you

One. The stronger form of the proof-discrimination control described above. The weaker form needs no ruling and is covered already.

Two. The first question, on telling two defects apart, now with five panel answers and a working candidate that came from your own suggestion.

Three. Restarting the control experiment. The evidence supports it considerably better than it did last night.

Nothing is running. Everything is committed and saved. The test suite stands at two thousand five hundred and forty nine passing, none failing, with no network access.

Written under CDSFL note standard v1.2, 14 May 2026.
