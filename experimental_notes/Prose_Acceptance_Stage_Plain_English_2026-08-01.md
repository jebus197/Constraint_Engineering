# The check that could only ever say no

2026-08-01 21:35 BST

## Summary

One small piece of the CDSFL review system was rebuilt four times on 1 August
2026. Only the fourth attempt survives, and it contradicts the third. What
settles the matter is a distinction that sounds obvious once stated and was not
obvious at all while the work was in progress: a check that asks "is this code
still grammatical?" is talking about the code. It is not talking about whether
the change someone just made to that code was a good idea. So it can refuse a
change. It can never approve one.

The cost of missing that distinction was measured rather than imagined. A
proposed repair that quietly inserted a command-injection call into the document
under review was marked verified, and the finding it claimed to fix was closed.

The problem was caught by five small test documents built for the purpose. No
paid model was involved. The whole test suite runs offline in under a second.

## The setting

The system reviews technical documents. When a reviewer proposes a repair, a
verification routine decides whether that repair is sound enough to close the
issue. If it says yes, the issue closes. Nothing else closes an issue, so that
one decision carries the whole weight.

The routine was built when every target was a Python source file. For a source
file it has real instruments to hand: a linter that flags sloppiness, a type
checker that catches mismatched values, a security scanner that flags dangerous
patterns. Point those instruments at an English design document and they produce
gibberish, because they are reading prose as if it were code.

The document under review on 1 August was exactly that: a design reference,
written mostly in English, with a handful of Python listings printed inside it as
examples. So the routine needed to learn what to do when the thing in front of it
is not a program.

## Three wrong answers

The first attempt was to skip the instruments entirely on a non-code file and
report success. That is worse than the original fault. It turns "I could not
check this" into "I checked this and it was fine", and every issue in the run
closes with nothing examined.

The second attempt was to pull the Python listings out of the document and
require the instruments to approve them. But those listings lean on things the
document introduces in its surrounding English prose, so a listing lifted out on
its own always looks broken. Nothing ever passes, and the review jams.

The third attempt looked right. Pull the listings out, and simply ask whether
they are still grammatical Python. If they are, approve. That shipped.

## Why the third was wrong

Every harmful change is grammatical. Grammar is not the property that
distinguishes a good repair from a bad one.

Tested against the real document, a repair that inserted a command-injection call
inside one of the printed listings was perfectly grammatical, was approved, and
closed its issue. The record it left behind read, in effect: verified, because
seven code listings parsed correctly. A sensible wording correction and a
security hole took the same route through the system and came out with the same
verdict.

## The fix

The verification routine now has three possible answers instead of two.

It can report a genuine fault, when a listing that used to be grammatical no
longer is. That is a real signal about the repair, and the issue stays open.

It can report that nothing applicable was run. This is the new middle answer, and
it covers the ordinary case: the grammar check found nothing wrong, but the
grammar check was never capable of judging the repair in the first place. The
issue stays open and goes to a human.

It can report success, but only for an actual code file where the real
instruments ran and agreed.

Alongside that, the system now keeps two separate lists: things that were
checked, and things that can only ever object. The grammar check moved to the
second list. Keeping them apart matters more than it sounds, because a check that
sits in the "things we examined" column is how a later reader, whether a person
or a model, comes to believe the repair was scrutinised when it was not.

The same reasoning is already earmarked for the security scanner when it is
wired in, because the injection measured today sat inside a code listing, where
that scanner would have looked at it and shrugged.

## What caught it

Five short technical reference documents, written to the same shape as the real
target but sharing none of its content, each with a known flaw planted in it:

A graph algorithm that reports a valid processing order for a structure that
contains a loop, where no valid order exists.

A variance calculation that loses nearly all its precision when the numbers
involved are large and close together.

A confidence interval built on the wrong measure of spread.

A beam calculation that uses the strength of a cross-section about one axis when
the load is applied about the other.

A measurement uncertainty that adds two independent errors together instead of
combining them in the way independent errors actually combine.

Each document mixes argument in English, mathematics in English, and worked code
examples — which is precisely the arrangement the founder asked about: what
happens when logic and mathematics have to live side by side in the same target.
The answer is that the system now handles it by refusing to pretend, rather than
by refusing to engage.

Fifty-one tests exercise these documents. Among them is a deliberate tripwire: a
test that asserts the broken behaviour and is configured to fail loudly if it
ever starts passing. That tripwire is what refused to let the third repair's
defect settle in quietly.

## An honest note about three tests that changed

Three tests written earlier the same morning said that an edit touching only
prose should be reported as passing. They now say it should be reported as "no
applicable checks were run".

That distinction deserves stating plainly, because "I changed the tests to agree
with my change" is how a genuine regression gets normalised. What those tests
were protecting is unchanged and was right: a harmless wording edit must not be
reported as a fault in the repair. What moved is only the label, because nothing
capable of judging the repair had actually run. The test that would have mattered
— that a broken listing is still reported as a fault — was never touched and
still passes.

## Also settled today

An alarm that had been refusing to let the run finish was raised twice, to eight
and then to thirty, to get past it. Both changes are reverted. The alarm was
right. It had detected that the fix-scoring machinery was rejecting every
proposed repair — thirty-eight rejections, twenty-nine of them from the same
broken check — and raising the threshold was suppressing a working instrument
rather than fixing anything.

A summary line in the test suite claimed the wrong thing about itself: it advised
running with a strict flag even when the strict flag was already active. That is
a verification claim that misreports its own conditions, and it briefly misled a
reader today. Fixed.

Thirteen genuine records that had been written into the run archive by
out-of-band analysis were moved out to a separate analysis log. The archive is
meant to record runs and nothing else.

## Where this leaves the work

Half the agreed must-do list is closed. The remaining half divides into the work
that faces the review panel — how documents are presented to it, how its proposed
tests are read, which specialists get involved for a prose target — and two
guards: one that refuses to start a run whose settings contradict its target, and
one that tells the panel *why* its repairs were rejected. That second one matters
more than its size suggests: fifty repairs were rejected across four rounds and
not one model was ever told.

The state at the end of the day: 2461 tests passing, none failing, all offline.

Written under CDSFL note standard v1.2 (14 May 2026).
