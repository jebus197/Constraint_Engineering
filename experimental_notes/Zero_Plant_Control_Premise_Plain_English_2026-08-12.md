# The control document was not clean, and the review panel was right

2026-08-12, overnight session. All measurement done offline, with no paid model calls.

## The short version

A warning was raised that the system had a serious accuracy problem: that when a
five-model review panel was shown a document containing no errors, it invented a
large number of serious findings anyway. If true, that would undermine the whole
approach, because a reviewer that cries wolf against correct material is worse than
no reviewer at all.

It was not true. The warning was checked and it collapsed. The findings the panel
produced against that document were examined against the document's own source code,
and they are **correct**. The panel found real bugs. The machinery that re-runs each
finding's proof confirmed them properly. Nothing malfunctioned.

What went wrong was the reasoning behind the warning, and that turns out to be the
more interesting story.

## The mistake

The document is called a "zero-plant control". That name means one specific thing:
nobody deliberately hid an error in it. It was then treated as meaning something much
stronger, namely that the document contains no errors at all.

Those are different statements, and the space between them is where the whole false
alarm lived. A document nobody deliberately broke can still be broken. This one is.

The document contains working code, and two pieces of that code are genuinely wrong.

The first is a rate limiter, the component that stops a system being overwhelmed by
too many requests. It is supposed to hand out a fixed budget of permission tokens and
refuse anything beyond that. But it never checks that a request asks for a positive
number of tokens. Ask it for minus ten, and the arithmetic runs backwards: instead of
spending tokens, the request *creates* ten of them, and the limiter now holds more
budget than it is ever supposed to have. Every later request sails through a limiter
that is no longer limiting anything.

The second is a routing table that decides which server handles which piece of data.
It uses a standard library function to find the right server, but the particular
version it calls returns the position *after* a match rather than the match itself.
So a key that lands exactly on a server boundary is sent to the wrong server. Most of
the time nothing lands exactly on a boundary, which is exactly why a bug like this
survives review.

Both were found by the panel. Both are real. Both are still in the document.

## Why this is not a failure of the audit

It would be easy, and wrong, to conclude that whoever checked the document was
careless. The checking was thorough. Every one of the document's forty-four claims
was not merely read but actually executed, using symbolic algebra, a constraint
solver, dimensional analysis and random sampling, according to what each claim
needed. That is a serious standard.

The problem is subtler and it is a problem of scope.

Consider the routing table. The document's claim about it says that the *index stays
within bounds*, that the lookup can never run off the end of the list of servers.
That claim is completely true, and it was verified correctly.

The panel's finding is that the lookup *goes to the wrong server*. That is also
completely true.

These two statements are not in conflict. They are about different properties of the
same three lines of code. One is about not crashing. The other is about being right.
The audit checked the claims. The panel reviewed the document. A defect in code that
no claim happens to describe is a genuine finding that the checking record simply has
nothing to say about.

That is the real fault, and it is a design fault in the control rather than a mistake
by anyone: the record of what is true covers the claims, while the review covers the
whole artefact. Any finding outside a claim can be neither confirmed nor denied. It is
unscoreable by construction.

## The loop this created, which is visible in the project's own history

There were two runs against this document, three days apart. Comparing them shows the
consequence playing out.

The first run produced seven serious findings. Almost every one lines up with a claim
that was rewritten shortly afterwards. The panel pointed at the rate limiter accepting
negative requests, and at the same limiter being unsafe when several things use it at
once. It pointed at the routing table. It pointed at a retry-delay claim.

The response was to rewrite the claims. The limiter claim gained two new qualifying
phrases: it now describes behaviour only "under single-threaded use" and only for
"unit-cost requests". Those two phrases are precisely the two problems the panel had
identified.

The code was not changed.

So the second run found the same defects again, because the code still had them, and
because the panel reviews code rather than sentences. Narrowing a claim closes the
finding on paper and changes nothing in the artefact. The document cannot escape this
loop by being reworded. Every future run will re-find the same three defects for as
long as they remain, and none of those findings can be scored.

The checking record itself names the cost of this. Findings of this ambiguous kind
"accumulate in the queue that decides whether a review may finish", and they are what
halted the first attempt at the run.

## A separate and quite different defect, found in the same place

While examining why some findings had produced no usable verdict, a second problem
appeared that has nothing to do with the first.

When a model writes a proof, it hands back a small program wrapped in the standard
formatting marks that separate code from prose in a written document. The system pulls
the program out by finding the opening mark and reading until the closing mark.

The trouble is that some proofs need to read the document itself and pull the code
listings out of it, which means those proofs must *mention* the very same formatting
marks in their own text. The extractor sees the mention, mistakes it for the end, and
cuts the program off in mid-sentence. What survives is a fragment that looks like a
program, is not valid, and fails the moment it runs.

Five findings in the later run died exactly this way, each cut off at the same point,
one hundred and thirty-four characters in, halfway through a piece of text the program
never finished writing.

The direction of this fault is the worst part. A proof that does the lazy thing, and
pastes its own private copy of the code rather than reading the real document,
survives untouched. A proof that does the careful thing, opening the actual document
and working from what is really there, destroys itself. The extractor was quietly
penalising rigour.

Across the whole archive the effect is small, about two in a hundred proofs. Inside
this one run it is nearly half, and the reason is exactly what the mechanism predicts:
this is the only target that is a written document with code inside it. Every other
target is plain source code, which a proof can load directly without ever mentioning a
formatting mark. The remaining planned experiments all use written documents, so this
would have grown worse as the work continued.

## The useful consequence

The proofs were never actually lost. They were preserved in the raw record of what
each model said; only the extracted copies were damaged. Re-reading that raw record
with the corrected extractor recovers forty-two working proofs where the damaged
version had twenty-six, twelve of which could not run at all.

That matters practically. This experiment does not need to be paid for again. It can
be re-scored from material already on disk, and the re-scored version rests on a
better body of evidence than the original run produced.

## What now needs a decision

The two defects are still in the document. There are three honest ways forward.

The document could be repaired, which restores the property it was believed to have.
It could be left as it is and the two defects written down as known, true findings.
Or the control could be retired and replaced with something whose record of truth
covers the whole artefact rather than only its claims.

The second is recommended. It costs the least, and it produces a better instrument
than a clean document ever could. A document with nothing wrong in it can only ever
measure false alarms. A document with two known faults in it measures false alarms and
missed detections both, and a review system that quietly stops noticing things is a
far more dangerous failure than one that occasionally over-reports.

## A note on how this was found

None of this came from a planned investigation. It came from checking a single number
before putting it into a question that was about to be sent to five models at a cost.
The number was wrong, the reasoning behind it was wrong, and following that thread
produced the two most useful findings of the night.

Checking it cost nothing.

Written under CDSFL note standard v1.2 (14 May 2026).
