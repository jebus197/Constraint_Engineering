# The Timing Re-Review — What the Panel Decided When Asked Fairly

2026-05-16 03:30 BST

## What this note is

A plain-English account of a second five-model review that re-decided
three "when should we implement this" questions, after the first review
was found to have been asked in a leading way. The technical companion
carries the dispatch record and verbatim reasoning.

## Why it was re-run

The earlier review reached a clean five-out-of-five on all three
questions — but its questions had quietly assumed the answer ("is the
plan to defer this correct?"). Large models tend to agree with a
stated position, so a unanimous yes to a question that contains its
own answer is weak evidence. The founder caught this and asked for a
re-run where deferral was not the default: state the facts and both
sides of the argument, tag the working model's own reasoning so the
panel could attack it, and require any "defer" to come with a specific
technical reason and a named experiment where it would instead happen.

## What changed when the bias was removed

The false unanimity disappeared. Where the biased round had said
"defer all three, five-nil," the neutral round split every question:
roughly three-to-two one way on the first, two-to-three the other way
on the second, four-to-one on the third. That split is the point — it
shows the earlier consensus was an artefact of how the question was
posed, exactly as suspected. Because no question reached full
agreement, each was decided on the strongest argument that survived
adversarial testing, not by counting votes.

## The three decisions

**The merge-deadlock resolver — hold it off for this restart.** This
reversed the working model's own prior position. The argument that
won: the part of this feature that has been thoroughly tested is the
vote-counting logic; the part that builds the list of candidates to
vote on, from live system state, has never run for real. A bug there
would not fail safely — it would silently merge the wrong things and
quietly corrupt the very convergence signal this restart exists to
measure. That is precisely the "are we faking the result" risk the
founder named. Re-hitting the known deadlocks for a few rounds is
wasteful but harmless and logged; a silent wrong-merge in the headline
run is neither. So the resolver stays switched off for the restart and
is switched on at the next, deliberately small, low-risk experiment —
where if it misbehaves, it does so cheaply and visibly.

**The identifier-collision fix — defer the big rewrite, but install a
detector now.** Everyone agreed the substance: the simple fix already
in place and the proposed deeper change fix genuinely different bugs,
and the deeper one — two findings with the same name silently
overwriting each other — is real and still open. But it has never
actually been observed in any run, the naming convention makes it
rare, and rebuilding the identifier system right before a restart
would destabilise a clean 229-test baseline for a problem nobody has
seen. The project's own evidence-before-action discipline says don't.
The resolution: don't do the rewrite, but add a small, safe,
watch-only detector that records if the collision ever actually
happens during the restart. If it fires, the rewrite happens before
the next experiment, with evidence. If it never fires, deferring it
was the right call, proven rather than assumed. That detector is the
one thing built in this session.

**The mid-round re-ask — defer.** Four to one. The fix already in
place catches malformed output and re-requests it the next round; it
delays a finding by one round, it does not lose it. The decisive
point: the convergence metric tracks a rate across rounds, and a
finding delayed by one round is still counted the next round, so the
delay shifts timing without removing anything. Adding a live re-ask
inside the most stateful part of the run, to save one round, is a bad
trade. Implement it later only if the restart's evidence shows the
delay is actually material.

## Why this is the honest outcome

The net result is that the restart runs on the work already done plus
one tiny watch-only detector, with the riskier, never-tested code held
back for a cheap, isolated first run. That is the integrity-preserving
choice: nothing unproven is allowed to move state during the run whose
convergence is the headline number, and every deferral is now
evidence-gated and written into the canonical plan at the exact point
it must be acted on, so it cannot be quietly forgotten. The working
model's own earlier recommendation was overturned by this process;
that reversal is recorded, not hidden — which is the whole point of
running the review without a thumb on the scale.

A standing rule was adopted from this: timing questions are never
again to be posed with deferral as the default. Ask whether the fix is
sound, ask when, and make any "later" earn its place with a technical
reason and a named home in the plan.

Written under CDSFL note standard v1.2 (14 May 2026).
