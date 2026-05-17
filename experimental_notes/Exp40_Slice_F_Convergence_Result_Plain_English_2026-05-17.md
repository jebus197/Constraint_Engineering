# It Converged — What That Means, in Plain English

2026-05-17 01:30 BST

## The headline

The final run settled. On the small extracted piece of the file, with
the repair loop and the other fixes switched on, the panel stopped
finding new serious problems for three rounds running and the run ended
itself early — seven rounds into a twenty-round budget. This is the
first time the experiment has settled in this whole arc of work. It is
a real, defined result and a clean confirmation that the diagnosed
cause was the right one. It is also a single run on the smallest
target, and the limits of the claim are stated here rather than
glossed.

## Why this is real and not another false alarm

The earlier run produced two false "it settled" alarms from the
watchdog, so this claim was checked hard against the authoritative
record before being written down. It passes every check the false
alarms failed. The run stopped itself early — the false alarms never
did. The settle is recorded as a top-level fact in the run's own
report, not inferred from a log line. The progress measure rose steadily
(roughly 0.16 to 0.27) instead of sitting flat near 0.05 as it did for
twenty-five rounds in the earlier run. And the repair loop was visibly
working: four checked fixes were written into the working copy of the
file — each one only after the whole test suite still passed — and the
panel then reviewed the improved file and ran out of new serious
problems. That is exactly the chain of events the diagnosis predicted.

## The honest limits

Four things must be said plainly. First, the run settled by the
"no new serious problems for three rounds" route, not by the progress
measure reaching its target line; the measure ended at 0.27, below the
0.30 line, and the runner itself attached the note "weak depletion,
state closure may be premature". It is a genuine settle by the rule
written for this experiment, but a modest one, not a saturated one.
Second, this is one run on the smallest possible piece, and several
things were changed at once (smaller target, repair loop, the immediate
re-ask, the cleaned starting file). It shows the cause was real and the
cure works; it does not, on its own, prove the whole problem is solved
for bigger targets, nor say which single change did the most work — that
needs the planned controlled comparison. Third, settling does not mean
every issue was resolved: of forty tracked items, sixteen were closed,
twenty-one were left unconfirmed, none contested. "Settled" means the
panel stopped raising new serious issues, not that it finished
everything. Fourth, the run printed a stock end-of-run line claiming it
ended without settling; that line is a known wrong default — the
authoritative record says it settled at round six.

## Why it matters

The earlier run, on the whole unrepaired file, sat flat for twenty-five
rounds and never settled. This run, on a right-sized piece with fixes
actually written back, settled at round six with the progress measure
climbing. The contrast is large and points exactly where the diagnosis
said it would: the thing blocking settlement was that fixes were never
written back, so the work never ran out. Remove that, on a sensibly
sized target, and it settles. This supports the long-held position that
settlement is real and was being blocked by a mechanical fault — now
with the fault identified, fixed, and the fix shown to work.

It does not finish the wider programme. It establishes, on a controlled
small target, that the diagnosis was right and the cure works. The
sensible next steps are to repeat on progressively larger pieces and to
run the controlled comparison that says how far this scales and which
change carries it — not to declare the whole problem solved on one
small piece.

Written under CDSFL note standard v1.2 (14 May 2026).
