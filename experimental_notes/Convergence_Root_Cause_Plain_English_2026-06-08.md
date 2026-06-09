# Why Convergence Stayed Out of Reach, and the Code Location Fix

2026-06-08 BST

*Plain-English companion. The technical record, with file and line references and per-claim
verification provenance, is `Convergence_Consolidation_Plan_2026-06-08.md`.*

## What this is about

The CDSFL system reviews one piece of software using several large language models working
together under a falsification discipline. Each round, the models hunt for defects. The system
is meant to recognise when the panel has essentially run out of genuinely new serious defects,
and then stop. That recognition is called **convergence**. For a long time it has been
unreliable: the system would run round after round, apparently still finding new serious
problems, and never settle. This note explains the genuine root cause, found and verified on
8 June 2026, and the fix that follows from it.

## The recurring problem, in plain terms

Picture a panel of inspectors examining one engine. By the fifth pass they have found every
real fault. But the inspection log keeps recording faults as brand new, because each inspector
writes the same fault up in slightly different words, and the clerk filing the reports cannot
tell that two differently worded reports describe the same fault. The log never shows a quiet
stretch, so the inspection never officially finishes. That is what was happening. The system
substantively finished finding distinct serious defects very early — around round 3 to 5 of a
16-round run — but could not recognise that it had finished.

## The true root cause

The system decided whether a finding was new by comparing the **words** of its description
against findings already seen. Every method it ever used was a variation on free-text
similarity: an identifier the model picked fresh each time (so a re-found defect always looked
new); word overlap; sentence-embedding meaning comparison. The decay-curve measure, **gamma**,
was computed from the count of supposedly-new findings, so it inherited the same flaw.

The deep problem: free-text similarity cannot work here. Every finding is about the same one
source file, so all findings read as broadly similar — whether or not they describe the same
defect. Two genuinely different defects in one file look similar; a re-worded report of one
defect looks different. There is no clean cut-off separating "same defect" from "different
defect" using description text alone. That is why convergence stayed out of reach: the search
was always for a better text-similarity number, and no such number exists for this task.

## The decisive test, including an overturned assumption

The project already contained a more sophisticated convergence detector, built in earlier
experiments and then left unused while the main system rebuilt a simpler version inline. The
natural assumption was that the answer had been built before and just needed connecting. That
was tested directly, by feeding Experiment 42's real round-by-round findings into the dormant
detector as it stands.

It failed too, instructively. At its default similarity threshold it merged nearly every
finding in a round into a single group (all findings are about one ~400-line file, so they
score as similar), and declared the run finished at **round 2** — before a genuinely serious
defect had even been found at round 3. The sophisticated detector had the same disease as the
simple one. The problem was never a missing component; it is that every component keyed novelty
on free text, and free text is the wrong key.

## The fix

Code-review findings are not arbitrary text — they are about specific named places in the
code: functions and methods. The fix: stop keying novelty on description words; key it on the
**code location**, i.e. which function the finding is about. The system reads the target file,
extracts its function names automatically, and keys each serious finding by the functions it
names. A serious finding counts as new only if it names a code location no earlier serious
finding has flagged.

On Experiment 42 this converges at about **round 6**, with a stable quiet stretch from round 5
onward — exactly where the old identifier method never converges at all. The late burst of four
serious findings per round at rounds 12–14, which had defeated the old system, is correctly
recognised as re-finds of defects already located by round 4: they add nothing new, and the run
is seen to have settled.

## How this was checked, and what the checking caught

The result was computed four independent ways, all agreeing on convergence in the round 6–7
range with a stable quiet tail. Then a panel of independent adversarial reviewers ran, each
told to **refute** the conclusion using their own scripts and the raw data.

The panel confirmed two things and corrected two — and the corrections are the point of the
method:

- **Confirmed:** the dormant detector really does over-merge and falsely converge at round 2.
- **Confirmed:** the late burst really is re-finds, with no genuine new serious discovery.
- **Corrected:** one late defect first appears at round 4, not round 3 as first stated (off by
  one round).
- **Corrected, and more important:** an exact sequence of numbers quoted in the claim came from
  an earlier draft and did not match the final method, and the precise convergence round depends
  on the fine detail of how the location key is defined. The qualitative result is robust; the
  exact round is not a fixed constant and must not be presented as one.

There is also a **known limitation**, stated rather than hidden: keying purely on code location
cannot tell apart two genuinely different defects in the same function. A second distinct defect
in an already-flagged function would be missed. Removing that blind spot needs a carefully
calibrated secondary check on meaning — future work.

## What was actually built

- A self-contained component that extracts a file's function names and keys findings by
  location, usable on any target file.
- Tests that lock in the behaviour, including the Experiment 42 result and a deliberate test
  that documents the known limitation so it stays visible.
- Calibration tests checking the harder properties directly: re-worded re-finds collapse to
  nothing (the bug being fixed), and the system does not falsely declare completion while
  genuinely new locations are still appearing (the dangerous failure to guard against).
- The location method **wired into the main system as a shadow reading only** — computed every
  round and written into the run report beside the old count, but not yet making the convergence
  decision. Deliberate: it puts the verified method where it will be exercised and observed on
  the next real run, without trusting it to decide before that trust is earned. The change is
  reversible and, switched off, leaves behaviour exactly as before.

## The deeper lesson

The real subject is reliability in machine-assisted work. Useful things get built, the working
context is lost, a later worker assumes they are active because an earlier worker implied so,
the old problem resurfaces in new clothes, and effort is spent re-solving what was already
solved. That pattern is precisely what this project exists to study and constrain. The
countermeasure used here is a durable written record in which every claim names the tool that
verified it, so no future worker takes an earlier one's word for what is true versus assumed.
The convergence problem was, in the end, a single mis-chosen key — hiding in plain sight,
repeatedly rediscovered and repeatedly forgotten.

## What is next

The location reading is observable on the next run. Before it is trusted to decide convergence,
two things are required: a secondary meaning check for two defects in one function, and one live
confirmation run showing it settles where it should. After that, the standing plan follows in
order: promoting the stronger-model routing to the default path; building the missing ability to
down-rate an over-rated but real finding; pruning the very large standing instruction set; and
only then advancing to the next experiment.

---
Written under CDSFL note standard v1.2 (14 May 2026).
