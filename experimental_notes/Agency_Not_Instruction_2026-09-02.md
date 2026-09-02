# Agency, not instruction — and a review format that lies about itself

**2 September 2026, afternoon.** Two reviewers returned complete work for the
first time under a brief that permitted them to say a thing was sound. Between
them they corrected a claim that had already been reported upward, established
the instrument the scaling question depends on, and produced a patch that cannot
be applied by the tool its filename names.

---

## The correction that matters most

The finding reported earlier was that two panel seats running identical model
weights produced materially different results under two *instruction
conditions*, and that this justified building diversity out of prompts when only
one model is available.

The attribution was wrong. The runner states the cause plainly at reference_runner_v3.py:286: the shell-bearing routes, claude_cli and codex_exec, inherit the runner's working directory. One
seat had a shell in the real working tree. The other had a bare API call with,
at most, a sandboxed Python executor.

Restated with the correct label:

| route | findings carrying a falsifier | 95% interval |
|---|---|---|
| shell-bearing | 76/293 = 25.9% | [21.3%, 31.2%] |
| bare API | 57/330 = 17.3% | [13.6%, 21.7%] |

Fisher exact p = 0.0107, odds ratio 1.68. One reviewer raised the same objection
independently, calling it a different execution harness rather than a different
instruction.

Tool access explains the gap directly, and obviously, once it is named. A model with a shell can run the artefact
and hand back a falsifier it has watched fail. A model without one must write a
falsifier blind. An eight-point difference in falsifier production is what tool
access buys, not what prompt wording buys.

This matters beyond bookkeeping. The design conclusion that followed from the
wrong attribution — that a single-model deployment can manufacture diversity
from prompt roles — is now unsupported by this evidence. It may still be true.
It is no longer evidenced.

The distinction that replaces it is between one model used directly and one
model equipped with agents and tools. That is a testable difference and the
right next experiment.

## A patch that is not a patch

A reviewer reported that applying the delivered patch produced a tree missing
eight files, while the apply command reported success.

Verified across every review artefact on record: of 18 unique patches, 8 carry
content that the apply tool ignores — 44.4%, with an interval from 24.6 to 66.3
percent — totalling 9,914 lines. The apply command returns success on every one
of them, so there is no signal at all.

**One correction, made before this reaches anyone as fact.** The content is not
lost. The extraction step writes new files into the artefact deliberately, under
a header, with a comment explaining exactly why it is loud rather than silent: a
dropped file that says nothing reads identically to a review that produced
nothing. The lines are all present.

What is wrong is narrower and still real. The artefact is named as a patch, the
apply tool succeeds on it, and anyone who treats it as a patch receives an
incomplete tree with no warning. In the tree that results, the metering
component sits inside an exception handler that swallows everything, so a
default-on ruling becomes a permanent silent no-op — defeated not by a bug but
by a file extension.

## The instrument the scaling question depends on

The co-discovery audit now exists and is calibrated: 278 labelled cross-model
pairs, 42 genuine matches, 35 links proposed, 30 correct. Precision 85.7 percent
with an interval from 70.6 to 93.7, recall 71.4 percent. A reviewer re-derived it
by an independent route and obtained 83.3 percent, consistent.

That number is the precondition for everything the external literature offers:
without a measured matcher, the overlap statistic every estimator consumes is
uninterpretable.

But the operating point is measured on edges and the artefact asserts groups.
428 scored edges become 100 groups asserting 610 pairs. The difference, 182
pairs or 29.8 percent with an interval from 26.3 to 33.6, is present by
transitive closure alone and was never scored. The adjudicated sample contains no
pairs of that kind, so precision on nearly a third of the output is unmeasured
rather than 85.7 percent.

The inflation is quadratic and it is worth seeing plainly. A group of 5 asserts
10 pairs from as few as 4 links. A group of 12 asserts 66 from as few as 11. A
group of 20 asserts 190 from as few as 19. The worst case observed was a
12-finding group where 28 of its 66 asserted pairs had a scored link, leaving 38
that did not.

## What the reviewers rejected

An escalation ladder built on instruction conditions was rejected as shipped, on
three measured grounds. It has no caller on the production path, so no run would
ever record which condition was tried. If it were wired, it would be shorter than
the ladder it replaces — three rungs against six with one model — and because the
ladder is truncated to two rungs, the rung its own comment calls the refutation
posture would never be reached. And its supporting evidence is the misattributed
result described above.

The idea survives that rejection. The implementation does not.

## What went right, and it is worth recording

Both reviewers independently found the same defect in one reviewer's own work: a
script that accepted any unknown flag and exited successfully, violating a rule
this project wrote against exactly that failure. Both fixed it. Both supplied a
before-and-after measurement showing the fix worked and the correct behaviour
unchanged.

One reviewer reported a bug in its own review harness, unprompted, on the
grounds that a review reporting only its successful checks is not a review.

This was the first round in which recommendations arrived with evidence attached
to the remedy rather than only to the fault. The brief was rewritten to permit a
verdict of sound, to require a measurement that each proposed fix works, and to
carry the project's specification so that a recommendation could be justified
against its aims. That change appears to be what produced the difference.

## Postscript: the fixes, and two more found by making them

The patch-format fault is closed. Staging intent-to-add before diffing makes new
files into proper diff hunks, so a reviewer-created file now survives the apply
step where it previously vanished without a word. The loud fallback survives for
anything that cannot be turned into a hunk.

Making that fix surfaced two more, both in the provenance guard that enforces
the mandatory simulated-member suffix.

The first is the same false positive one artefact type later. The guard selected
a real panel review's patch as a simulated artefact, because the code the
reviewer had written mentions the convention, and then flagged the reviewer's own
filename as a bare vendor name. The guard already carried a repair for exactly
this class, written after a real tool log was flagged for grepping a simulated
label, but that repair blanks quoted values in structured records and a patch is
not a structured record, so it could not fire. The file's own principle now
extends to diff bodies: a token on a content line is prose, not a
self-declaration. Header lines are untouched, so a patch that genuinely creates a
simulated artefact still selects on its path.

The second was found by trying to break the first, and it is older and larger.
The guard's name rule required the token to be followed by punctuation or the end
of the string. This project names its simulated runs with a token followed
immediately by a digit. So none of the 20 simulated run directories on disk were
matched by the name rule, and selection rested entirely on the content rule -- a
simulated artefact carrying no content marker would not have been selected at
all, in a guard that exists because a simulated result must never be mistakable
for a real one. Widening the rule to accept a following digit matches 233 further
paths across the 15,453 examined, and every one of them is genuinely simulated.
