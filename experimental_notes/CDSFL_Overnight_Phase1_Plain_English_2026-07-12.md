# CDSFL Phase 1 — Overnight Execution Report (plain English)

2026-07-12, 02:10 BST.

## What this covers

CDSFL is a system in which several frontier AI models review code and scientific claims under a
strict falsification discipline: a finding only counts if a runnable check can demonstrate it,
and where the tools cannot decide, a human does. Before running the pivotal generalisation
experiment (Experiment 43 — does the convergence result found on one code module repeat on a
second, different one?), a short list of preparatory tasks was agreed. This report describes
those tasks, carried out overnight, and an adversarial self-check that followed them.

## The four preparatory tasks

The first was a review, by a panel of five models, of the large standing instruction document
that is attached to every model on every turn. The question was narrow: how much of it is
history and motivational prose that a model does not act on, and could be trimmed without
weakening the falsification rigour. Four of the five models answered (the fifth was blocked by
the login problem described below). They agreed the trimming approach is sound with caveats, and
three of the four independently pointed at the same section — the one dealing with forcing models
to agree — as the best candidate to cut. That is the very section the project had already
decided to retire, so the panel rediscovered it from scratch. Their disagreements were kept
rather than averaged away: notably, one model wanted to compress a section about the project's
core mathematics while another insisted it be left alone. Because that section touches the
load-bearing mathematics, any change there needs direct human judgement. The panel's output is a
recommendation only; nothing was cut, and every proposed cut would be tested by a controlled
comparison before adoption.

The second task gave real substance to a component that had been hollow. This component is meant
to gather outside research, read it, and offer what it learns back to the review process. Until
now it fetched only short abstracts, threw them away, and emitted a placeholder. It now finds a
freely-available full-text copy of a paper, downloads and reads it, has a cheap fast model distil
what the paper says, and turns that into a real, sourced note. This was proven on a well-known
paper: the full text was fetched, tens of thousands of characters were parsed, and a genuine
summary was produced in place of the old placeholder. Crucially, all of this runs in a
shadow mode: the notes are written to a log for study but never reach the models doing the actual
review and never touch the convergence mathematics. So it cannot distort the coming experiment.

The third task was a straightforward rename, which the founder had judged trivial. A mechanism
previously called "take up the slack" is now called "routing", throughout the code. The important
constraint was that the experiment must behave identically to its predecessor, so all the
configuration files were left exactly as they were, and a compatibility bridge was added so the
old name in those files still works. The behaviour is unchanged; only the names moved.

The fourth item was to retire a crude mechanism for forcing agreement among models. Investigation
confirmed it was already switched off and reaching nothing — there is nothing operative left to
remove. A pleasant consequence is that the coming experiment is now fully identical to its
predecessor, which is a cleaner starting point than the earlier plan expected.

## The adversarial self-check, and what it caught

Rather than trust that the new work was correct, an independent adversarial pass was run over it:
fourteen separate agent reviews, each trying to break two specific promises — that the research
component stays strictly in shadow, and that the rename changed nothing about behaviour. Each
suspected flaw was then handed to a second reviewer told to refute it and to assume it was wrong
unless it could reproduce the failure from the actual code. This caught five real defects (and
correctly dismissed five others; one reviewer even caught a fabricated reference inside another
report and kept only the true part).

The most important find was a genuine mistake in the rename. The compatibility bridge for the old
configuration name had been added in one place but not a second, equally valid one — the
experiment runner's own direct launch path. Through that second path, the renamed setting silently
reverted to off, which would have quietly disabled the routing mechanism and made the experiment
diverge from its predecessor. The earlier check had only exercised the first path and missed this.
It is now fixed in both places, verified, and locked with a regression test. This is exactly the
kind of silent divergence the adversarial discipline exists to catch, and it justified the pass on
its own.

The other four findings were smaller and all in the shadow research component, which does not even
run in the coming experiment, so none could have affected the result. They were nonetheless real
flaws in freshly written code — a download routine that could crash instead of degrading
gracefully, a size cap that a misbehaving server could slip past, and tests that did not actually
exercise the new machinery offline — and all were fixed and covered with new tests.

## The login problem, and why it is not a dead end

One of the project's most effective reviewers is Claude reached through its command-line tool. That
route is currently returning an authentication error. The cause turned out to be twofold: the
surrounding environment was redirecting the login to the wrong place, which masked the real issue,
and underneath that the subscription login session had simply expired and could not refresh itself
automatically. This is a routine expiry, not a broken account. The founder can fix it in under a
minute by logging in once from a terminal; a single test command confirms whether it took. Until
then, Claude can still take part in review discussions through a different internal route, though
for the experiment itself the command-line route is preferred because it alone can replace the
model's entire instruction set with the project's own — which is why fixing it, rather than
working around it, is the right call.

## Where things stand

The experiment is ready and untouched, its configuration identical to its predecessor's in every
operative respect. Nothing has been launched. The work now waits on two things: the founder's
one-minute login refresh, and the founder's review of this report. After that, the experiment can
run, with the research component observing quietly in the background.

Written under CDSFL note standard v1.2 (14 May 2026).
