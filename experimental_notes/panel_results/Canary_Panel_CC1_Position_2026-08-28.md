# CC1's own position on the canary build

**Written 2026-08-28 04:14 BST, BEFORE either reviewer returned.** Under `pr` the founder's rule is
that CC1 participates with its own position and does not merely synthesise the range. A position
written after reading the other two is a summary wearing a position's clothes, so this is timestamped
and committed first.

## Q1 — Is the in-repo guard real? YES, and it is now attacked rather than assumed.

Four attacks, all refused, all pinned as tests:

| attack | result |
|---|---|
| plain in-repo absolute path | refused |
| symlink outside the repo pointing at a file inside it | refused |
| symlinked *directory* pointing at the repo root | refused |
| `..` traversal from a home-directory temp dir back into the repo | refused |
| genuine outside path (the known-good control) | **allowed**, as it must be |

`pathlib.resolve()` follows symlinks before the containment comparison, which is what defeats
attacks 2 and 3.

**One methodological trap worth recording.** The traversal test built from a `/var` temp directory
lands in `/private/Users/...` because `/var` is a symlink on macOS. The file does not exist there, so
the call fails with `FileNotFoundError` — and that reads exactly like the guard working. It is not.
The test now builds from a home-directory temp dir and asserts the traversal actually reaches the
file before expecting the refusal. **A guard that is never reached cannot be said to have held.**

## Q2 — Are the Goodhart guards load-bearing? Two yes, one only partly.

**(a) Held-out only: load-bearing.** `detection_rate` refuses to report when the held-out pool is
empty, rather than silently falling back to the full catalogue.

**(b) Multi-generator: load-bearing but crude.** A single-generator held-out set is refused. Two
generators where one contributes exactly one canary is barely better and is currently accepted.
There is no minimum contribution per generator. **This is a real gap and I have not closed it,**
because the right minimum is an empirical question and inventing a number would be the same
un-derived-threshold problem the project already has with `rho_threshold=0.25`.

**(c) Blinding: necessary, not sufficient, and I want to be explicit about the limit.** The check
covers the CONTENT of the seeded document — no canary id, no generator name, no ground-truth
summary, none of the words canary/seeded/mutant. It cannot survive a reviewer that can read the
target's version history, where the seeded edit is one `git diff` away. **The panel reviewers are
given Bash.** So blinding is a property of how the target is PRESENTED, not of this module, and
seeding must happen on a copy with no history. Recorded in the docstring as a known limit.

## Q3 — Is the measurement sound? It was not. I found a defect in my own module.

`detection_rate` derived its output from the catch list alone, so **a model that caught nothing was
absent from the result rather than scoring 0.0.** The totally blind reviewer — the exact failure this
whole instrument exists to surface — was the one result that could go missing. Silent omission in the
reassuring direction, inside the module written to catch silent omission in the reassuring direction.

Fixed: the roster of dispatched models is now required, and an empty roster is refused.

**Still open, and I do not have an answer:** p_hat = catches/k treats all canaries as equally hard.
Two models finding the same canary and two models finding different canaries give the same panel-level
number. An unkillable canary — one whose defect the target cannot actually express — silently lowers
every model's score with no way to tell it apart from a genuine miss. That is a denominator problem I
can see but cannot fix without run data.

## Q4 — What is missing before it could be wired to the gate?

1. A real verifier. `catches()` takes one injected and scores NOTHING without it. The intended one is
   counterfactual: the finding's falsifier fires on the seeded text and not on the clean text. That
   machinery exists (`bench/falsifier_verify.py`) but **is itself under a live finding as of tonight**
   — a falsifier that never touches its target still returns CONFIRMED, and 346 of 372 archived
   falsifiers fired on every historical version of their target. **Wiring canary scoring to that
   verifier today would build a new instrument on a broken one.** This is the blocking item.
2. A catalogue, which does not exist yet, in the key store, encrypted. The 31 files already there are
   still plaintext pending the founder's passphrase.
3. A ruling on whether a missed canary BLOCKS convergence. That is a new way for a run to fail.

## Q5 — Should it be built at all? The strongest case against.

The honest case against is that **canary seeding measures detection of defects we already know how to
construct, and the panel's value is finding defects we do not.** A high p_hat on hand-built canaries
is consistent with total blindness to the defect classes nobody thought to seed. It certifies the
instrument against the part of the space we can already see.

Fable's own scoping note concedes this and turns it into a rule: a domain is in scope only if
ground-truthed seeded defects can be built for it. I think that is the right response — it converts
the limitation into an explicit boundary rather than papering over it — but it should be stated
plainly rather than left implicit, because it materially narrows what any p_hat can be claimed to
certify.

The cheaper instrument that answers a nearby question already exists and is already broken: the
discrimination control. **Fixing it may be worth more than building this.** I would not let canary
seeding become the reason that fix waits.

## What I could not check

- No live run. Every verdict here is unit-level against a module written hours ago.
- p_hat has never been computed on real reviewer output, so nothing is known about its variance,
  and no threshold on it would have any derivation — the same gap `rho_threshold` has.
- I have not tested whether a panel can learn seeded-defect *texture*. That needs at least two runs
  against the same reviewers and is the question Q5 turns on.
