# What Those Items Actually Were, In Plain English

3 November 2026, 16:17 GMT

## Why this exists

On the 30th of October the founder wrote, against a consolidated verdicts report, that items were being put to him by their reference code with no account of what they were. His words, verbatim: *"Simply stating a problem by it's designated ID (in this case B41) clearly tells me nothing about what that problem is? You need to stop doing this and issue clear explanations of each issue, what they affect and what your recommendations are?"* And immediately after: *"Again, I have no idea what you are talking about? What is 'C1'? Where have all your plain English explanations (which is a big part of the reason these tts files exst) about what these issues are gone?"*

Those complaints were recorded as questions in the register and were never answered. This answers the ones that name an identifiable item. The register's own figure: 14 of the 63 unanswered questions are this same complaint, a share of 0.222222 with a Wilson 95 percent interval from 0.137250 to 0.339123, concentrated 9 in the consolidated verdicts report of the 30th of October, 4 in the morning report of the 1st of November and 1 in the generated morning report of the 31st of October.

Finding which item each complaint attached to was only cheap after the reader repair committed earlier today. Before that repair the reader took 684.25 seconds and died on a test timeout; it now takes 6.80 seconds, so the report lines each annotation sits against can be fetched directly.

## B41, the work queue of the 19th of October, and it is finished

B41 was a work queue the founder issued on the 19th of October, written onto the master task list as 8 numbered lines so that the session stop gate would hold the work to it rather than relying on an author remembering it. It was not a defect. It was a list.

All 8 lines are discharged. 6 were discharged with recorded evidence on the 30th of October. Line 7 reduced to a single exception and that exception closed when the entry it depended on closed. The entry is marked done and committed, and the founder's ruling on it is dated the 1st of November.

1 correction belongs with it, because the entry itself carries the correction and a reader should not have to find it. The entry had quoted a figure — 10 of 11 panel-requested tickets having every referenced entry closed, 0.909091 with a Wilson interval from 0.622642 to 0.983768 — and that figure has no committed producer. It was traced by hand and the trace was written to an unversioned log on the Desktop. Under this project's own rule that any measured figure travels with the script that produced it, the number may not be cited as evidence. It is flagged inside the entry rather than quietly left in place.

**What it affects:** nothing outstanding. **What is recommended:** no action; it is closed.

## C1, the claim channel's weight, and what the single number was for

C1 was an instruction of the founder's dated the 2nd of October that nothing on the task list tracked. His words were *"Also implement this and test it on the upcoming simulated runs."*

The subject is the claim channel. The claim channel is the part of the harness that records what a model claims about its own work, separately from what the tools can verify. It was built to run in an informative-only mode, meaning it observes and reports but its output does not enter the scoring equations. Promotion out of that mode was supposed to wait on a commissioning run measuring how often the channel is wrong against known ground truth.

The test half was done and the implement half was not, and no entry recorded the gap. The channel did run in both free runs of the 15th of October — the record shows 22 claims, 19 decidable and 3 routed — so it was exercised, but no commissioning measurement of its error was taken.

The single number the item needed was the channel's weight. It reads 0.0, which means the multiplier it contributes is exactly 1 and the channel changes no score at all. That is the whole of what was being asked: whether to leave the weight at 0.0 or set it, and the answer could not be given without a measurement of the channel's error.

The entry is now marked done and committed, with the founder's ruling dated the 29th of October.

**What it affects:** whether a model's own claims influence scoring. At weight 0.0 they do not. **What is recommended:** no action on the entry; if the channel is ever promoted, the commissioning measurement comes first.

## B50, the 6 immune-memory assertions that were accusing an ordered reset

B50 concerned 6 assertions about immune memory that had begun to fail permanently. The important part is why they were failing: they were accusing a reset that the founder had himself ordered. The assertions were stale rather than correct, so the failure was in the test and not in the code under test.

The entry is marked done and committed.

**What it affects:** the board's ability to run clean, since permanently failing assertions block every commit. **What is recommended:** no action; it is closed.

## The 2 complaints that name no item

2 of the 14 attached to things that are not single entries, and both deserve a straight answer rather than a reference.

The first attached to a question about whether both baseline arms of an experiment should run after the third convergence rather than before it. The founder's objection was exact: *"I cannot gauge what the consequences of either of these would be, since you do not list them? What would they be?"* He was right that the consequences were not listed, and that is the fault. Listing them requires stating what changes in the measurement if the arms move, which was not done at the time and is not something a reference code can carry.

The second attached to a dense block about panel dispatches that could not be located, alongside the figure that 104 of his annotations since the 1st of October had no verdict record. His objection was *"This is an impossibly dense block of prose for me to understand?"* The underlying question he asked inside it was sharp and answerable: whether this was the same situation as before, where he had asked for a panel and the panel had simply never been run. That question is still owed an answer and is not answered here, because answering it needs a check of which panel requests were dispatched and which were not, and that check has not been run.

## The honest scale of what remains

The register holds 336 instructions and questions of the founder's in a state that means recorded but never resolved. Of those, 180 — a share of 0.535714 with a Wilson interval from 0.482285 to 0.588336 — resolve by this session writing something rather than building anything: 63 questions awaiting an answer, 108 discussions and 9 statements. The other 155 need a fix, or evidence that a fix already landed.

Of the 63 questions, 14 are the complaint this note answers and **49 are genuinely distinct questions** each needing its own answer. That is the real backlog, it is spread over 40 source files between the 1st and the 30th of October, and it is work that needs no input from the founder.

## The standing format, so this does not recur

The format the founder endorsed on the 30th of October is 4 parts for every item put to him: what it is, what it affects, what it decides, and what is recommended. Every section above follows it. A reference code alone is not an item description, and an item presented by code without those 4 parts should be treated as not yet presented.

Written under CDSFL note standard v1.9 (1 November 2026).
