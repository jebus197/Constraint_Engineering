# Six things written vaguely, answered plainly

The founder marked six places in the 2026-08-28 reports where the writing forced guesswork. Each is
answered here in full. Where the honest answer is "that sentence was bad", it says so.

---

## 1. "What is a severity cutoff? What is its purpose?"

Every finding a model raises carries a **severity score between 0 and 1**. **0.7 is the line.** At or above
it, the finding counts as *critical*. Below it, it does not.

That single number decides three things:

- whether the finding counts toward the **zero-new-critical** condition, which is one of the two halves of
  the convergence gate;
- whether it is included in **gamma_critical**, the decay curve the gate actually reads;
- whether it can hold a run open.

**The complaint the May panel raised, restated plainly:** 0.7 is a bare number. Nothing derives it and
nothing anchors it to the world. A model that scores a defect 0.69 rather than 0.71 changes whether that
defect can hold up convergence, and there is no principle deciding which side it lands on.

**What "a consequence-based definition" would mean instead:** replace *"severity ≥ 0.7"* with a test about
what happens if the defect is left alone — for example, *"if unrepaired, this produces a wrong published
result"*. Defined by the consequence, not by a number somebody picked.

**Status:** still a bare threshold in the code. `CRITICAL_SEVERITY_THRESHOLD`, used at
`reference_runner_v2.py:1584`, `:1606`, `:2356` and elsewhere.

---

## 2. "What 'frozen scope' document? What is it for? What would it contain?"

The plain word for it is **a pre-registration**.

It would be written and **frozen before Bench Run 2 executes**, and it would say: what CDSFL claims to do,
what it does not claim to do, which domains are in scope, and what counts as success — decided in advance.

**Its purpose is to stop the claim being fitted to the result after the fact.** Without it, BR2 produces
numbers and the claim can be quietly adjusted to match whatever those numbers turn out to be. That is the
single easiest way for a project like this one to fool itself, and it is exactly what this project exists to
refuse elsewhere.

**Status:** does not exist. This is one of the two surviving items from the May plan.

---

## 3. "Well if you tell me what they are, perhaps I can decide if they are still worth doing?"

The two surviving items from the May plan are **items 1 and 2 above** — the severity cutoff and the frozen
scope document. Nothing else from that plan is outstanding; the other five were already done, including the
panel's headline recommendation, which shipped on 2026-06-10 as the two-sided gate.

That is the whole of it. Not a month of work: one document, and one definition.

---

## 4. "More tts vagueness… I again find myself trying to guess what you might be talking about"

The sentence marked was:

> *"An asymmetry is itself a finding: it says one defect contains the other. Recorded as containment, it is
> an answer, not a deadlock."*

That is unreadable, and the founder is right to say so. What it means:

For **4 of the 133 pairs**, the tool found a one-way relationship. **Applying finding A's fix also cures
finding B. Applying B's fix does not cure A.**

So A and B are not two separate defects, and they are not the same defect either. **B is part of A.** A is
the larger problem and B is a piece of it showing through somewhere else.

That is a result, not a stalemate. Nobody needs to adjudicate "same or different", because the honest answer
is neither — and "B sits inside A" is more useful than either label would have been. What the record needs
to say is which is which, so that fixing A is known to close B as well.

---

## 5. "So that sound good? 'Nothing to see here? Time to move along.', or not?"

Marked against the canary module after the sentence *"All nine are fixed and the module now carries 42
tests."*

**Not "nothing to see here."** Nine defects were found in a module CC1 had already attacked itself and judged
sound. That is the finding, and it is about CC1's self-review rather than about the module: **attacking your
own work is not a substitute for an independent panel, and this is the measurement that says so.**

The module is in better shape than it was. Whether it should exist at all is Question 1 of the panel
dispatched at 00:18 on 2026-08-30, on the founder's own reframing — a canary should be pointed at churn,
which occurs, not at silence, which does not.

---

## 6. "If they are looking at different aspects of the whole problem, is that not then by definition the whole problem?"

Marked against the recorded disagreement between the two reviewers over the vacuous-curve guard: one called
it a defect, the other called it deliberate and locked by a test, and CC1 recorded the disagreement without
resolving it.

**The founder is right, and it has now been demonstrated rather than argued.**

The guard was unreachable **only when the churn flag fired**, because churn was an early return that
short-circuited before the guard was ever evaluated. When rho was changed from a veto to a contributory
signal on the founder's own ruling — a change made for entirely separate reasons — **that early return went
away, and the guard became reachable again.**

Verified directly: a vacuous curve with churn firing now reaches the VACUOUS branch and returns a verdict,
with churn still named on it. Pinned by two tests in `test_vacuous_gamma_curve.py` so it cannot be lost
silently.

**One fix, both findings closed.** Which is the founder's point exactly: the two reviewers were describing
one problem from two sides, and the repair that addressed the whole of it settled both.
