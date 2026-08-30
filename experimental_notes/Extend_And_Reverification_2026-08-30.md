# Extend Is Now Read, And Your Two Corrections Were Both Right.

2026-08-30, 14:08 BST (UTC+1)

You asked me to wire the extend mechanism, re-check the remaining fixes properly, and report. All three are done. Along the way two of your corrections turned out to be sharper than I first understood, and my own checks caught two defects in my own work before they landed.


## First, The Two Questions You Asked In The Margins

You asked which it is with the old experimental branch, because I had told you one thing and then another. The answer is that I was talking about two different objects and slurring them together, which is my fault and not a change of position.

There is the encrypted archive on your desk, and there is the branch in the repository. They are not the same thing. The archive still needs your passphrase to prove it opens, and that was true in August and remains true. The branch is ordinary local history and needs nothing at all.

So when you asked whether you need to decrypt something for me to extract: no. You need do nothing. I checked directly, and both missing exam documents are sitting in the local repository right now as retrievable objects, one of 20,290 bytes and the other of 24,542. No passphrase is involved. The branch must still never be deleted, which has never changed and which I have never said otherwise.

Your second question was about my merge ruling and you were right that I had misrepresented it. Your ruling was that merge should work, but that superseded findings should be recorded rather than discarded. I kept describing merging as though deleting the other finding were unavoidable. It is not, and your own ruling from the 21st of August already contains the answer, in these words: extend is the answer to ledger versus instrument, and it is read by nothing.

I checked. Nine days later, it is still read by nothing.


## What That Actually Meant, Measured

Models are instructed to emit five kinds of cross reference: confirm, challenge, extend, merge and reopen. I counted how many places in the code act on each.

Confirm is acted on in nine places. Challenge in six. Merge in three. Reopen in one. Extend in zero. It is the only one of the five that nothing reads.

And there are 209 extend statements sitting in the archive across fifteen experiments. Every one of them is a reviewer saying "that finding also has this consequence", and not one has ever reached a human, reached another model, or influenced anything whatsoever. Just under three percent of all cross references we have ever collected, filed and then dropped on the floor.

That is what your ruling was pointing at, and it went nine days unfixed after you made it.


## What I Built

Extensions are now collected onto the finding they belong to. They are sent to the model that owns that finding, through the feedback channel that already runs every round, so the model is told what consequences its fix must also cover. And they are written into the report, so they reach you as well.

I paired that deliberately with the fix checker, because your own ruling specified the connection: a fix whose own test still fires afterwards is demonstrably insufficient, and the schema should name what it misses. The extensions are what it misses. So when a fix fails its own test and extensions have been filed against it, the model is told both things together.

It records and it never decides. It cannot change a status, and it is absent from both convergence gates, with a test that reads the gates and fails if either so much as mentions it.


## My Own Checks Caught Two Defects In My Own Work

The falsification step of the cycle is the one I have been skipping, and it earned its place twice today.

The change that writes extensions into the report used the wrong variable name. It would have raised an error the first time a report was generated. Caught before it landed.

And three of the seven tests I wrote failed against code that was perfectly correct, because the tool I used to inspect the code rewrites double quotes as single quotes, so my checks could never match. I nearly went looking for a fault in working code. Fixed, and then properly commissioned: putting the old unwired version back makes six of the seven fail.


## The Statistics, Done Properly This Time, With Two Tools Each

Your rule from the 21st of April says every computed claim gets checked with at least two tools. Last night I satisfied that rule zero times. Today, for every claim:

The verdict counts agree between two independent counting methods, 7047 cross references in total.

The headline about fixes not curing their own tests remains 126 out of 246, and both a confidence interval and a separate significance test agree that "more than half" is not supported. The range is 45 to 57 percent and the test gives three quarters, which is nowhere near significant. "About half" is what the data says.

The tests that never read their target remain eight out of 372, with a range of roughly one to four percent.

And one new result, which I had not looked at before. I compared the rate of ineffective fixes between experiments, worst against best: about 64 percent in one and about 32 percent in another. The test gives 0.15, which is not significant. So ineffective fixes run at somewhere near half in every experiment, rather than the figure being driven by one bad run. That makes the finding stronger, not weaker: it is a property of the whole corpus, not an artefact.


## The Simulated Run

You were right that this should be tested before the benchmark run rather than during it, and your framing is the part worth keeping: the benchmark is the entire machinery turned on a large number of real targets for the first time, and it is the wrong place to discover something does not work.

The simulated run already existed. It was built at the start of August, it drives the real pipeline in the real order with agents standing in for the paid models, and it still ran clean after last night's changes.

I have added five stages to it, one for each repair from the last two days: the churn measure being contributory rather than blocking, the patch applier refusing anything that would break the file, the disposable review copies no longer carrying the repository history, the fix checker being unable to gate anything, and now the extend mechanism being read. Sixteen stages, all passing.


## The Other Thing You Were Right About

You asked why I was throwing away the repairs the reviewers write in their sandboxes. There was no good answer. Between them the two reviewers had written seven changes and fifteen tests, and my cleanup destroyed all of it before I read a line, so both reviews had to be rebuilt from their written descriptions.

Fixed. The changes are extracted before the sandbox is torn down, and if the extraction fails the sandbox is kept rather than deleted. I proved it end to end.

And the tool logging you asked for immediately earned itself. The very first log showed a reviewer attempting to write a file directly, being refused because that permission is not granted, and falling back to a shell command instead. We have never been able to see that happen before.


## Where Things Stand

The full test suite is at 4401 passing, nothing failing, nothing uncommitted.

Still outstanding for you: the key files in plain text, and the push, which you ruled goes last and now stands at well over 150 commits spanning nine days.

Still outstanding for me: the discrimination control misattribution, which is the one I would want settled before the benchmark run because that run is its first real exposure, and it now has a simulated run to be tested in first.


Written under CDSFL note standard v1.7 (26 August 2026).