# Where the project stands, and the one decision outstanding

2026-05-29 22:30 BST. Constraint Engineering / CDSFL.

## The story in one paragraph

The convergence redesign the six-model sign-off panel approved has been built.
**315 tests pass.** Nothing has been committed to the repository and no new
experiment has launched, because while the build was being verified, one
question surfaced that only the founder can answer. The question is about how
strict a single safety check should be. The rest is ready to ship as soon as
that one call is made.

## How the bench decides a review is done, in plain terms

The bench runs a panel of frontier models on a piece of code, round after round.
Each round, the models report what they think is wrong with the code. A separate
mechanical step called the **verifier** then tries to confirm whether each
finding is a genuinely serious problem or not. Only findings that pass that
verification count as real serious findings.

The bench treats the review as **finished** when three things have all gone
quiet at the same time:

1. **Three rounds in a row turn up no new verified serious findings.** This is
   the main signal — the modern, accurate way of saying the decay curve (the
   project's founding idea) has flattened at the serious-findings frontier.
2. **The broader review state is calm.** No disputes between models, no collapse
   in the rate of useful work.
3. **All serious findings the verifier has produced are accounted for** —
   confirmed and reported, denied as not-critical, fixed and closed, or
   recognised as duplicates.

The decay curve itself — the slope number called gamma that has caused so much
past confusion — is now **computed and reported but does not decide anything**.
It is shown as evidence that the curve really did flatten (it reads close to 1.0
at a genuine finish). It is no longer a gate. That is the change the panel
approved, and the build implements it.

## The one open question

When the verifier looks at a serious-looking finding, it can return one of three
answers:

- **Yes — genuinely serious.**
- **No — not really serious.**
- **I don't know.**

The question is what to do when it says "I don't know" — or simply has not
finished looking yet.

The build's narrow answer (the build agent's choice): as long as the verifier
has not actively returned "I don't know," treat the round as quiet, including
rounds where serious-looking findings are still being processed. This keeps
things moving and reproduces the result the recent exp41c run was celebrated
for.

The recommended stricter answer: **any** serious-looking finding the verifier
has **not** confirmed or denied prevents the round from counting as quiet. Those
findings are escalated to the founder for a human verdict — what the project
calls human-in-the-loop (HIL) review.

## What each choice does in practice

**Loose version.** Exp 42 is more likely to auto-converge by itself. The cost is
that the bench can finish a run while a few serious-looking findings are sitting
in unresolved limbo, never verified one way or the other. That is the gap the
sign-off panel specifically named as a blocking concern.

**Strict version.** Exp 42 may not auto-converge at all. Instead, when the bench
has done its useful work but cannot resolve every serious-looking finding, it
**stops and asks the founder** to adjudicate them. This writes the standing rule
— "the human decides materiality" — directly into the gate.

## The honest consequence for exp41c

The exp41c run that converged cleanly at round 6 did so with **three**
serious-looking findings still in the unresolved pile — C0007, C0015, C0017 —
opened in rounds 1, 2 and 3. The verifier never confirmed or denied them. Under
the looser version those three were treated as quiet and the bench
auto-converged. Under the stricter version, exp41c would **not** have
auto-converged at round 6. It would have stopped and asked the founder whether
those three are genuine criticals or footnotes.

This is not a regression of the methodology. It is the verification doing its
job and revealing that the celebrated clean convergence leaned on the looser
interpretation.

## The deeper problem this points at

The verifier is being too cautious. It parks findings in the "I don't know" pile
instead of reaching a yes or no. A better verifier would resolve more findings
either way, and clean auto-convergence would happen naturally. **Improving the
verifier is the project's most important next-iteration item.** The sign-off
panel called the verifier the load-bearing core of the platform.

## What else is waiting

- **Two follow-up notices in the UI**, both small, both genuine, neither
  blocking. One asks for a cleanup of a second hidden place where gamma was
  still influencing termination (neutralised for Exp 42 already; full cleanup
  scheduled). The other is an unrelated pre-existing test failure in a different
  part of the code. Both can be dismissed for now and addressed later.
- **Codex CLI (CX2)**, signed in via the founder's normal account, is tested and
  ready to be added as a sixth panel model in the experiments once the strict-
  or-loose call is made.
- **Nothing committed, nothing running.** The state hasn't moved in the six days
  since the founder stepped away.

## The recommendation and the question

The recommendation is **strict**. It honours the standing rule against false
convergence, it puts materiality decisions where the founder said they belong
(with the human), and it operationalises the sign-off panel's blocking condition
without needing further documentation acrobatics. The honest cost is that Exp 42
might escalate a few findings to the founder for adjudication rather than
auto-converge — which is the right kind of cost for a robust working platform.

**One word answer:**

- **"strict"** — the build finishes, the new code is committed, CX2 is wired in
  as the sixth model, and Exp 42 launches under live monitoring.
- **"loose"** — same launch path, but the limitation is openly documented in the
  platform notes for the community to see.

Written under CDSFL note standard v1.2 (14 May 2026).
