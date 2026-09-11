# Closing the repair loop — and adapting canaries to what is actually detectable

**READ THIS FIRST — this brief asks for FIXES, not just findings.**

The three dispatches before this one asked you to find problems, refute claims and return verdicts. None
asked for a repair. The founder identified that on 2026-08-29 and was right: *"The purpose of these multi
model reviews is not just to find problems (although that is clearly 50% of it), but also to suggest fixes.
But you have a bad habit of simply telling our models during these reviews 'find problems with this code'
and not telling them to come up with fixes."*

So for **every** finding below, return: the finding, **a concrete fix** (file, function, the actual change),
and **your confidence in that fix** with what would falsify it. A finding without a proposed repair is half
an answer here.

Two independent questions. Answer both.

---

## QUESTION 1 — Canaries must detect churn, not silence

The founder has corrected the premise the previous canary brief was built on, and the correction is
load-bearing:

> *"you cannot look for a signal of 'silence' from an LLM. That is impossible. If things are done this way,
> then the risk is you will end up looking for a signal you can never detect... The only condition (ever) in
> the entire history of this project where a model, a round, or an experiment has produced no output has been
> the result of broken machinery, a misconfigured experiment, or one of the parsing issues we have
> encountered. The purpose of rho and our other machinery is to detect when models have stopped producing
> new useful and/or novel output and may have entered the territory of 'churn', which in itself should be a
> contributing measure when deciding if a problem space has been usefully exhausted."*

The previous brief framed canary seeding as distinguishing *"the panel went quiet because the document is
clean"* from *"the panel went quiet because the panel stopped looking"*. **Both halves of that are the wrong
signal.** An LLM does not go quiet. It keeps producing. The real failure mode is **churn** — continued
volume with no new content.

`bench/canary_seeding.py` (built 2026-08-28, 42 tests, read it in full) is therefore currently pointed at a
condition that does not occur.

**1a.** Can the mechanism be re-pointed at churn? Concretely: a panel that is genuinely exhausted should
still **kill a freshly seeded canary**, because detection capacity is intact even when there is nothing left
to find. A panel that is churning should **miss it**, because it is recycling rather than reading. Is that
distinction real, and is it measurable with what this module already does?

**1b.** If yes — what exactly changes in `canary_seeding.py`? Give the code. Note that `rho` was changed
TODAY (commit `aff3ab7`) from a convergence **veto** to a **contributory** signal, per founder ruling. How
should a canary result combine with rho and with the two-sided gate? It must **contribute**, never veto —
that is a standing ruling, not a preference.

**1c.** If the answer is that canary seeding cannot be adapted and should be retired as an idea, say so
plainly and say why. The founder asked directly: *"Is it useful or not? Can it be fixed? Should it be? Or
should it be retired as an idea?"* A clean "retire it" is a perfectly acceptable answer and costs nothing to
give.

---

## QUESTION 2 — The repair loop closes for broken falsifiers but not for ineffective fixes

Read `experimental_notes/Why_The_Machinery_Was_Not_Clearing_The_Pile_2026-08-30.md` first — it is short and
carries the evidence for everything below.

Established, and not in dispute:

* The feedback channel is **built and enabled by default**. It already tells a model *"FALSIFIER ERROR: your
  test did not run to a verdict... Re-write it so it runs."*
* A fix is **never applied and its own falsifier re-run in flight**, because the test article is frozen by
  founder-directed methodology (`bench/launch_exp41.py:6`, `apply_fixes_back_enabled=false`).
* Consequently `FIX_INEFFECTIVE` — a fix that does not cure the defect it claims to cure — is invisible
  live. **16 of the 48 undecided similarity pairs are exactly this.**

**2a.** CC1's proposal: run the counterfactual on a **scratch copy** — apply the fix, re-run that finding's
own falsifier, discard the copy — leaving the frozen article byte-identical, and emit one more feedback line.
`scripts/adjudicate_by_repair.py` already does exactly this post-hoc with a `try/finally` restore. **Attack
this proposal.** Does it violate the static-article methodology in some way CC1 has not seen? What does it
cost per round? What happens when a fix touches a file that is not the target? When two findings propose
conflicting fixes in the same round?

**2b.** If the proposal survives, **write it** — the function, where it hooks in, what the feedback line
says, and the test that would commission it. If it does not survive, give the alternative that does.

**2c.** A second gap: `_inround_reask` fires on **one** condition, unparseable output, and its prompt says
*"Do not add new analysis; reformat what you already produced."* Everything else waits for the next round —
so a finding whose falsifier errors in the **final** round never gets a repair opportunity. Is that worth
closing, and if so how, without letting a run extend itself indefinitely to chase repairs?

---

## Rules

- Run things. Every verdict must be something you executed, not something you read.
- You are in a throwaway git worktree. Nothing you write escapes. Do not push.
- **Disagreement is information.** Do not converge toward the other reviewer or toward CC1. Where you think
  CC1 is wrong, say so and show the run that proves it — that has been the most valuable output of every
  dispatch so far.
- Report what you could not check, and why. That section is not optional.
- The founder is not a developer and reads these. Name files and functions precisely; do not assume context.
