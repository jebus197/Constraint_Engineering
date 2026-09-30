# Morning report, 30 September 2026

**08:15 BST (Europe/London). Audience: the project's designer, for decisions. Plain English.**

## The headline answer: convergence is reachable, and the run came within 1 condition of it

The overnight simulated cycle got closer to convergence than any previous simulated run, and the record shows exactly what stopped it.

The convergence gate has 2 sides and needs both. At round 6 of the 5 seat arm, **both were satisfied**:

- gamma for critical findings stood at **0.436** against its threshold of **0.30**;
- and the count side had **3 consecutive rounds with no new critical findings**, which is the strict endpoint the gate asks for.

It still did not converge, and the runner named the reason itself:

> `A4 BLOCK: 2 unverified critical-severity candidate(s) (status UNCONFIRMED, no resolved falsifier) pending at round 6 — zero-critical streak does NOT accrue`

So a single safety rule held it open. That rule, A4, refuses to count a quiet round while any critical finding is still unverified. It is behaving correctly. The problem is upstream: those findings were unverified because **no runnable test was ever attached to them**. The run log is explicit: *"1 unresolved critical, 1 never assessed, no runnable falsifier"*.

**That is one mechanism, not a pile of them, and it is the same mechanism that stalls the prose arm**, where round 0 sent 12 of 12 findings to the human queue with no test verdict at all, a rate of 100.0000%, confidence interval 75.7506% to 100.0000%.

**So the honest answer to whether convergence is out of reach under the current set-up: no.** It is blocked by one identified, already-prioritised problem, which is the supply of runnable tests for findings. Nothing in the mathematics, in gamma, or in the gate needs changing. The model was not the obstacle at any point last night.

## What was repaired overnight, and what it bought

Rho was stuck at exactly 1.000 in every round of every simulated run, which made convergence by saturation impossible: a run could only ever run out of rounds. That is now fixed, and the improvement is large.

| | rounds stuck at exactly 1.000 | lowest value reached |
|---|---|---|
| before the repair | 3 of 4 | 0.9565 |
| after the repair | **0 of 8** | **0.3333** |

The difference is statistically clear, Mann-Whitney p = 0.0040.

4 further defects were found and repaired along the way. 2 of them could have corrupted a result:

1. **A finding could be erased from the novelty total entirely.** Where 2 models each corroborated the other, both were discounted, so 1 real defect counted 0 times. A guard against this already existed and named only the simpler case, so the door left open was the one that mattered.
2. **The repair was being undone 1 round later.** A pre-existing routine rewrote the whole history every round using the older rule, wiping the correction the moment the next round began.
3. **An interrupted simulated run could make the archive look 37.0 days newer than it is**, which silently switched off a safety quarantine on 13 control settings.
4. **The reason the previous run died was not the runner.** A standing instruction since 29 July requires every experiment to survive the session that starts it, and the script implementing that only ever covered one launcher, not the simulated one. Last night's cycle then ran unattended for 9 hours without trouble, which is the repair proving itself.

## A claim that has to be withdrawn

An earlier report stated that the discovery measure's churn flag blocks the convergence gate. **That is false, and has been since the 29 August ruling that made churn contributory rather than a veto.** Both review seats disproved it by running the gate twice with the flag on and off and getting the same answer, and the same check was then repeated independently. The direction matters more than the error: the repair was presented as making convergence harder to reach, and every route it actually opens makes convergence **easier**. 4 places in the code that repeated the false claim have been corrected.

## Where the simulated work has been kept, and a correction owed

The rule is that simulated runs are simulations: their output belongs on a local simulation branch, and the canonical repository is touched only by agreement or after a successful real run.

**The canonical branch has not been touched.** The published branch sits exactly where the last save left it, at commit a94a7bb, and nothing has been pushed.

What did happen is that 9 commits were made to the local copy of the main branch. 8 of those 9 are purely the lessons: code repairs, tests, measuring scripts and notes. 1 of them also carried 2 output files from a simulated run, and 6 more such files are staged but not committed. That mixing is contrary to the rule and is the correction owed. Nothing is lost and nothing is published; the tidy-up is a decision to be taken rather than an action already taken.

## The decisions this morning

1. **Separate the branches.** Put the whole overnight session on a local simulation branch, return the local main branch to where the last save left it, and then choose which lessons to carry across deliberately. Recommended, because it restores the rule exactly and loses nothing.
2. **Attack the supply of runnable tests.** This is the one mechanism blocking convergence. The review panel recommended letting a test that fires on both findings of a pair serve as the verdict that authorises treating them as one, with the condition strengthened so that firing on the same location is not mistaken for proving the same defect.
3. **Raise the round limit.** The arms stop at 8 rounds. The project's own formula for the best number of rounds gives 9.38 on its historical fit and 19.96 on the measured decay of last night's run. 8 is below both.

## What this session's own defect record showed

13 substantive defects were found overnight. The automatic guards, the test suite and the committed tests found **7 of them, 53.8462%**, confidence interval 29.1438% to 76.7939%. The free review panel found 3. The assistant found 2 unaided, and of the 3 defects capable of corrupting a result, the assistant found **none** alone. 4 of the 9 commits were refused by a guard before being accepted, and each refusal was correct.

The practical lesson is that the mechanised layer earns its keep and should be extended, and that the review panel should look at a design before it is built rather than after.

Written under CDSFL note standard v1.7 (26 August 2026).
