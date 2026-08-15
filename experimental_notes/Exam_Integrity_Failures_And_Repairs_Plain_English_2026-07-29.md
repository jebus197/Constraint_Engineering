# Two Ways The Exams Leaked, And What Was Done About Them

2026-07-29, 13:05 BST.

## The short version

The exam redesign was completed and then, during the checks that precede any exam
run, two separate integrity failures came to light. Both were self-inflicted. Both
are now closed for every future run.

The first is that a reviewing model read the answer key during the chemistry exam.
It did this at round one, and it printed the complete list of seeded claims. The
chemistry score of six out of six therefore cannot be reported as a blind detection
rate. The engineering exam shows no evidence of the same access, though it ran before the fix existed, so that is weaker than saying it is clean.

The second is that the answer key for the capstone experiment, which has not yet
run, was recoverable from the project's own version history, and the twelve seeded
claims it named were exactly the twelve in the live key. That experiment would have
been worthless had it run. The document is being reseeded so that the recoverable
key is wrong.

Nothing already recorded has been altered. The corrections sit alongside the
archive, not inside it.

## How the first leak worked

Three conditions had to hold at the same time, and every one of them was of this
project's own making.

The reviewing panel was given the project's own folder as its working directory.
That is correct for the experiments that review the project's code, because the
panel has to reach the code. It was wrong for the exams, where the whole point is
that the panel cannot reach the marking scheme.

A note inside that folder said where the answer keys had been moved to. The keys
had been moved out of the project folder that same morning, precisely to hide them.
The note recording their new location was committed inside the project folder
seventy-six minutes before the chemistry exam began. The fix advertised the thing
it was hiding.

Older copies of the keys remained in the project's version history, where two
ordinary commands retrieve them.

The model that read the key was not cheating. It had found a genuine error in a
claim about molar mass, and it opened the key to check whether that error was
deliberate, so that it would not propose a fix destroying a seeded fault. That is
conscientious behaviour. It is also, unavoidably, the moment that model learned which six claims were seeded.

How far that reached is narrower than first stated. The summary the panel is shown
never includes the code a model writes, and the seeded list appears in no other
model's output anywhere in the run. One model held the answer; the other four have
no traceable route to it. The retraction still stands, because that one model is
the one whose declaration that the search was finished drove the experiment to
close.

## What the chemistry result is now worth

Two things survive and should be said alongside the retraction.

Every one of the six detections carries an independent, runnable demonstration.
Nothing was accepted because a model asserted it. The chemistry is correct whoever
pointed at it.

Measured with the project's own scoring tool, the chemistry exam carries one
finding against a claim that was actually true, and the engineering exam ten. An
earlier version of this account said there were none, which was wrong, and also
said the panel had not padded its score. That second statement was about intent,
which the record cannot establish either way, and it has been withdrawn.

What cannot be recovered is the stopping decision: whether that panel would have
kept looking, and for how long, had it not known the count. That is exactly the
quantity the exams exist to measure, and for the chemistry exam it is lost.

## The awkward part, which changes what the redesign rests on

The model that read the answer key is the same model that, in the same round,
announced that the document contained exactly six seeded defects and that there was
no seventh. That announcement was the whole reason for redesigning the exams: it was
read as the model working out the design from the document's structure.

It cannot carry that weight any more. A model holding the answer key does not need
to work anything out, and the record cannot separate the two explanations.

The redesign is not left without support, because the engineering exam shows the
same kind of recognition — the model there wrote that the seeded errors had been
fully harvested — and nothing in that run touches a key at all. So the argument for
the redesign now rests on the engineering exam rather than the chemistry one, and
the zero-plant control stops being a confirmation and becomes the decisive test.


## The second leak, and why it was caught in time

The keys were originally committed inside the project folder before being moved
out. Version control does not forget. Two ordinary commands against the old
location return a complete answer key.

For the four experiments already finished, the recoverable keys are either
superseded by rewritten documents or belong to exams already sat. For the capstone
experiment, which crosses two mechanisms on and off across four paid runs, the
recoverable key named the identical twelve claims as the live one. Had it run, its
result would have measured nothing.

The document is being reseeded: which claims carry the errors is changing, while
the difficulty ladder and the two clean control sections are preserved. The old key
is being left in the version history on purpose, as a tripwire. The claims it names
are no longer the claims that are seeded, so any future run that flags exactly
those without demonstrating them has done archaeology rather than verification, and
will say so in its own findings.

## Why the forensic scan said everything was clean

The scan meant to catch precisely this reported both completed experiments clean
earlier in the day. That statement was wrong.

The scan looked only at files whose names matched one pattern, meant to select the
per-round model responses. It caught the chemistry incident on a re-run purely by
luck, because one other file's name happens to match that pattern by coincidence.
The main run report, which holds the same evidence, was never scanned and never
would have been.

The scan now reads every file in a run directory, distinguishes confirmed access
from mere vocabulary, and stops the chain rather than reporting a compromised
number as though it were a measurement.

## The four layers now standing between a panel and a key

1. The panel is confined to the staged document's own directory. It no longer
   stands in the project folder. If that directory is missing the run refuses to
   start rather than quietly falling back to the project folder, because failing
   quietly is how the first leak went unnoticed.
2. Documents are staged one per directory, each named by the identifier the
   document gives itself. Previously all the exams sat in one directory, so a
   single listing showed every paper in the series including those not yet sat,
   with the experiment numbers and subjects in the filenames. Now a listing shows
   exactly one document with a neutral name. The files are read-only and the
   directories refuse new files, both proven by attempting to write and being
   refused.
3. Every reference to where the keys live has been removed from the project folder's
   working files. This is not complete and should not be described as though it were:
   the commit history still records the old location in its messages, and removing
   that would mean rewriting history.
4. During a run the keys are held as a single compressed archive under an opaque
   name, so there is no file whose name a search would match and no readable text
   whose content a search would match. This is concealment rather than encryption,
   and it is the third layer rather than a substitute for the first two.

A note on the fourth layer: the first place chosen for that archive was somewhere
the detector itself treated as ordinary background noise, so the concealment and
the detection would have quietly cancelled each other out. That was caught while
the detector was being rewritten, and the detector is now told explicitly where the
archive is.

## What is still open

One exposure has not been closed. The assistant's own conversation records are
stored under the user's Library folder and contain key material, because the keys
were printed into the session while the exams were being built. A model that
guessed that location could read them. Closing this properly requires running the
panel under an operating-system sandbox or as a separate user account, which is a
real change to make in the middle of an experimental arc. For now it is mitigated
by the four layers above and by detection, but it is not eliminated, and it is
recorded here rather than quietly accepted.

## The exam redesign itself

The physics and biology documents were rebuilt so that seeded claims are no longer
paired with a correct twin in a way that lets a reader spot the pattern, and so
that the number of seeded claims cannot be worked out by counting anything. Correct
claims are now paired with other correct claims as often as with seeded ones.

A zero-plant control document has been added. It contains forty-four claims and
none of them are seeded. It is written in the same register and structure as the
seeded exams and, on a formal comparison against its closest sibling, is
statistically indistinguishable from it. It measures the stopping decision
directly: a panel that announces it has found the seeded errors in a document
containing none has revealed that it is reasoning from structure rather than from
verification. It also gives a clean false-alarm rate, which no seeded document can.

An independent audit returned clean for the biology document and clean for the
control, and found one surviving signal in the physics document: seeded claims
still tended to sit next to near-duplicate claims doing the same operation, which
let a reader rank the claims by similarity and find six of the seven for a third of
the work. That is under repair.

The audit also found something applying across the whole set. The original design
produced an arithmetic rule — the number of seeded claims equals the number of
sections minus one — and that rule still holds on the two exams already sat. A
reader who works it out on one paper carries it to the next. It is being broken
everywhere it can still be broken.

## Where things stand

Nothing is running. The chain is halted deliberately while the repairs finish and
are re-audited. The order once it resumes is physics, then biology, then the
zero-plant control, then the four capstone runs, stopping before the second bench
run as directed.

Three decisions are outstanding and none blocks the repairs: whether the chemistry
and engineering exams should be re-run under the new design or reported with the
contamination stated; whether to spend the effort on an operating-system sandbox
for the panel; and the materiality review of findings raised against claims that
were true, of which there are ten in the engineering exam and one in the
chemistry exam, measured with the project's own scoring tool.

Written under CDSFL note standard v1.2 (14 May 2026).
