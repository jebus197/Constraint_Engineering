# THE STANDING GOAL — the founder's autonomy handover, 2026-11-21

This file exists because the instruction it carries was given in chat, and chat
does not survive a compaction. His own words on that point: *"This is probably
the most important instruction I will give you in this project so far, so you
should treat it accordingly and implement it in a way that will survive every
compaction event from now on."*

The block between the INJECT markers below is read by
`hooks/task_list_pulse.py` and placed in context on EVERY turn, beside the
`[tasks]` summary and the `[entries]` roster. Edit the block to change what a
future session is told; edit nothing else and the delivery keeps working.

## HIS WORDS, VERBATIM

From his annotation of 2026-11-21:

> *"Then do that. If you recall the role of the HIL (in this case me) is to deal
> with issues that are computationally irreducible, or that fall into the
> category of safety, legal/ethical, or a fundamental change in the way the
> system works (or is intended to work at a whole). You know the project's goals
> and specifications, you have the work in front of you. You know what the
> project aims to achieve. You also have free access to the other models in the
> free panel review. You should use them always through any significant batch of
> work to check your work, suggest fixes and then test these fixes before
> implementing them. The end goal you should have in sight at the very least is
> to take us to the final item on your master task list, which is the
> orchestrator run that was build some time ago, and after this, then on to the
> remaining items on our runway. That does not mean that you need to cut
> corners, but it does mean you should strive to not allow the work to become
> infinite. We should be talking in terms of weeks (or shorter) rather than
> months. That is your goal."*

And from the same exchange in chat:

> *"I am officially handing the remainder of the work up until the orchestrator
> experiment over to you. ... In essence you have complete autonomy on what
> happens from this point on until the orchestrator experiment is ready to run.
> And equally important instruction is that after every meaningful batch of work,
> you should always run your fixes by a free panel to check them, the check any
> fixes they suggest before implementing them. It was never intended to be the
> HIL's role that they should be troubled with things you are capable of
> deciding on your own."*

The phrase *"the check any fixes"* is a typo for *"then check any fixes"*, and
the correction is unambiguous: the panel's proposals are TESTED before adoption,
not adopted because a panel proposed them. His standing rule that a model vote
is not evidence applies to the panel's output exactly as it applies to any seat.

And his correction of 2026-11-21, when work stopped to write a status report:

> *"What was the primary instruction I gave you? Have you stopped? How is that
> possible in light of this instruction? It's good that you found issues and
> fixed them. You should continue to do this until your primary objective is
> attained."*

## THE 4 RESERVED CATEGORIES, AND WHAT THEY ARE NOT

An item goes to him only if it is one of these:

1. **Computationally irreducible** — no falsifier can be written for it. By the
   project's own standard (`scripts/reproduce_rubric_human_queue_partition.py`)
   an item is irreducible ONLY if a falsifier cannot be written, and 0 items
   have ever been shown untoolable. The 1,911 of 3,255 entries with no falsifier
   are a TOOLING backlog, not a queue for him.
2. **Safety.**
3. **Legal or ethical.**
4. **A fundamental change in how CDSFL works, or is intended to work as a
   whole.**

Everything else is mine to decide. A judgement that is merely difficult,
contested, or expensive is NOT one of the 4. Asking him about it is the failure
this handover exists to end — his words: it was never intended to be the HIL's
role that they should be troubled with things the orchestrator can decide alone.

## WHAT THIS DOES NOT SUSPEND

Nothing. The additive standard, simplest sufficient, composability, FFAFP, P-pass and its
5-pass budget, `measured-rate-travels-with-its-script`, `execute-do-not-grep`
and the note standard all bind exactly as before. Autonomy is about WHO DECIDES,
not about how carefully the work is done. His own qualification: not cutting
corners, while not letting the work become infinite.

<!-- INJECT-BEGIN -->
HIS STANDING GOAL, handed over 2026-11-21 and in force until the bounded
orchestrator run is ready: carry the master task list through to its final
entry, the orchestrator run, then on to the remaining runway. Weeks, not months.
Do not stop while work remains; do not cut corners to go faster.
AUTONOMY: decide it yourself. He is the HIL for 4 categories ONLY —
computationally irreducible, safety, legal/ethical, or a fundamental change in
how CDSFL works as a whole. Everything else is yours. A hard or contested
judgement is NOT one of the 4.
EVERY BATCH: put the work to a free panel, then TEST what the panel proposes
before adopting any of it. A panel's proposal is a hypothesis, not a fix.
COMMIT ONCE PER AGREED BATCH, never per fix.
Full text and his verbatim words: experimental_notes/THE_STANDING_GOAL.md
<!-- INJECT-END -->

Written under CDSFL note standard v1.9 (1 November 2026).
