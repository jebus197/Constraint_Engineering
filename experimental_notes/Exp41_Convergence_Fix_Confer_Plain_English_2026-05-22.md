# Experiment 41 — Convergence Fixes and Five-Model Confer (plain English)

2026-05-22 (BST). Constraint Engineering / CDSFL.

## What happened

Two real defects in the maths model's convergence detector were found, fixed, and independently checked by all five panel models. The original, simpler convergence design was endorsed for a controlled re-run of Experiment 41. An earlier mistake in how the findings were classified is also corrected here.

## The two defects

**The rate measure (kappa_rate)** had been counting *every* finding in a round, including ones already seen — so a round that just repeated old findings looked like fresh discovery and blocked convergence, and a genuinely quiet (finished) review read as unfinished. The fix makes it count only genuinely *new* discoveries and their decline from the early peak, so a quiet, exhausted state correctly converges.

**The novelty/similarity check** was the serious one. The similarity function runs in embedding mode, where even unrelated findings score ~0.48; the merge threshold was 0.33, below that floor — so almost everything was treated as a duplicate. Genuinely new findings, including critical ones, were judged old, never counted, and the safety veto never fired. The detector could declare a review finished with a critical problem unaddressed — **false convergence**, the worst failure. The config already had the correct higher threshold (0.55) for embedding mode; it had simply never been connected. The fix connects it, matched to the similarity function actually in use. Live experiments were never affected — the runner's immune pipeline had already worked around it; the defect was confined to the detector module.

## The independent check

All five models reviewed under a "find what's wrong" framing. Verdicts: fixes **sound** (one) or **sound-with-conditions** (four); scope **reasonable** (one) or **reasonable-with-conditions** (four); every model cleared the book-cooking self-check. Two conditions were addressed immediately (bind the threshold to the actual similarity function; fix the same bug in the load-balancing module rather than defer it — flagged as a hard blocker). The rest concern the runner-level gate and the re-run, scheduled next.

## The correction to the record

An earlier classification pass made three errors, all caught by re-testing and the panel: a verification script false-flagged a finding via a crude text match; a hardcoded verdict and a misread filed the novelty defect as a footnote when it was the material false-convergence bug. The panel that raised it was right; the single reviewer who dismissed it was wrong — the project's multi-model falsification method working as intended, including on the AI running it.

## What comes next

The detector is now correct and panel-verified. Next: rebuild the runner's convergence gate in the original simple spirit — gamma back to a reported diagnostic, convergence on no genuinely-new verifier-surviving discoveries for several consecutive rounds, a known critical still blocks, the verifier promoted carefully (filter noise, never silently discard real findings). Then re-run Experiment 41 on the same frozen target, thresholds fixed in advance, no tuning after — to see if it converges cleanly and honestly, replicating Experiment 37, the last naturally converged run before the later complications.

Written under CDSFL note standard v1.2 (14 May 2026).
