# Experiment 40 Architectural Review — What the Panel Decided, in Plain English

2026-05-15 23:25 BST

## What this note is

A reader-friendly account of a five-model review that signed off the
architecture before the next phase of Experiment 40. The technical
companion carries the dispatch record, prompt sizes, and verbatim
quotes. This note explains what was reviewed, how the review was run,
and what the panel concluded.

## The setting

After the second leg of Experiment 40 and the block of fixes that
followed it, three architectural questions stood between the project
and two next steps: restarting Experiment 40 for more rounds, and
switching on the new merge-deadlock resolution rule. The project's
discipline is that architectural decisions of this weight get a
compelled-convergence review — five independent models, each forced to
commit to a single answer per question rather than offer a menu, run
under the project's full reasoning protocol.

That review had first been run locally, by the working model alone,
because the command-line tool for one of the panel members had been
quarantined mid-session by an over-cautious operating-system malware
scan (a false positive, since cleared and the tool reinstalled). The
local pass had found and fixed two real issues. This live five-model
round was the independent check: would the full panel reach the same
conclusions?

## How it was run

All five models — Claude, Gemini, two GPT-5.5 routes, and DeepSeek —
received the same package: the merge-deadlock rule's design note in
full, the complete source of the module that implements it, and the
full post-mortem of the fix block, plus the three questions. They
answered independently and in parallel under the latest version of the
project's reasoning protocol. All five returned cleanly within about
two minutes.

## What the panel decided

On every question, and on the overall verdict, the panel was
unanimous — a clean five-out-of-five. The acceptance bar for this kind
of review is exactly that: anything short of unanimity re-opens the
question. Nothing re-opened.

On the first question — is the merge-deadlock resolution rule sound to
switch on as designed — all five said yes, with no change required
before it is enabled. The rule asks the panel to vote when the system
cannot decide where a finding belongs, takes a clear majority, is cost
capped, and ships switched off until a deliberately small, low-risk
experiment. The panel independently confirmed the earlier finding that
the voting rule holds up under deliberately awkward vote splits.

On the second question — should the identifier-hardening be the simple
bounded rule that was applied, or the deeper architectural change a
second-opinion model had proposed — all five endorsed the bounded fix
now, with the deeper change held in reserve and triggered only if the
problem recurs in the next rounds. None thought the bigger change
should be forced through before restarting.

On the third question — are the three "languages" the system and the
panel share (how findings are named, how fixes are formatted, how
votes are cast) coherent, and was it right to strengthen the
reformat request now while deferring the more invasive
ask-again-mid-round mechanism — all five agreed the languages are
coherent and the staging is correct.

The overall verdict was unanimous: yes, the architecture is sound to
restart Experiment 40 for more rounds with the new rule still switched
off, and yes, it is sound to switch the new rule on at the planned
small experiment afterwards. No blocking items.

The one thing the panel flagged is not an objection but a discipline:
during the restarted rounds, keep an eye on the two documented warning
signs. If mangled identifiers reappear despite the bounded fix, that
triggers the deeper identifier change. If well-formed fixes keep
failing to parse for reasons other than staleness, that triggers the
mid-round re-ask. Neither is expected; both have a defined path if
they happen.

## What this resolves and what remains

This review was one of two things that had been left as a human
decision. It is now closed with a unanimous panel sign-off: the
architecture is validated. The only remaining decision is a different
kind — whether and when to actually launch the multi-hour restart,
which is a cost-and-supervision call for the founder, not an
architectural one. The review confirms the runner is sound to restart
whenever that call is made; it does not itself start anything.

Written under CDSFL note standard v1.2 (14 May 2026).
