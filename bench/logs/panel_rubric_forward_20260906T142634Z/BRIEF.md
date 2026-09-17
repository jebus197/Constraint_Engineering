# The rubric and its numeric proxy disagree on 45.56% of cases. Propose the forward fix.

## You are asked for a SOLUTION, not a verdict

The founder's standing instruction: propose the fix, do not merely find the fault. A verdict that
only diagnoses is a failed answer. Use your shell — sympy, z3, numpy, scipy, statsmodels,
wolframscript, and the repo itself. The named `sympy_verify` tools are NOT on your route; say so
and use the shell. **Answer as yourself.** No assigned roles; both seats get the same questions.
Disagreement is preserved as information, never smoothed toward consensus.

## The measured situation

CDSFL gates findings on severity. There are 2 authorities and they conflict.

* **The rubric** — a consequence-based classification, pre-registered and FROZEN in May 2026. The
  live work queue records a standing ruling that it is **authoritative wherever it and the number
  disagree**, and that moving the number requires a new dated pre-registration.
* **The number** — a bare numeric severity cut at **0.7**, described in that same ruling as the
  rubric's *operational proxy*.

**They disagree on 118 of 259 judgeable cases: 45.56%, Wilson [39.6%, 51.7%].** That is exactly the
band where the gate is decided. Worse: **91 of the 118 disagreements (77.1%, Wilson [68.8%, 83.8%])
have NO executable falsifier at all.** Where nothing executable exists, a lookup settles nothing and
the conflict decides the outcome by itself. **Nothing anywhere reports that gap.**

Related and probably the same defect one level down: a **model-assigned severity float currently
gates convergence**. This project forbids model voting — findings are confirmed programmatically or
by a human, never by vote — so a float a model chose is a vote wearing a number's clothes.

## What is already settled — do not re-open

* Who adjudicates the 4 escalated cases: **nobody**. It is a 4-way schema lookup, measured and
  reproduced by `scripts/reproduce_rubric_human_queue_partition.py`.
* An earlier claim that 82% of the disputed band was already tool-settled was **wrong**: it was
  computed on 33 of the 118 cases, not all 118.
* The conflict in ARCHIVED data will be recorded in the appendix and the reproducing guide. That is
  ruled and is not your question.

## The questions

**Q1. Which authority should govern, going forward?** The rubric, the number, or a third thing that
subsumes both? Derive it from what each can actually decide, not from preference. Note the asymmetry:
a consequence rubric encodes judgement a number cannot carry, but a number is mechanically checkable
and a rubric clause may not be.

**Q2. What replaces the model-assigned severity float that gates convergence?** It must be
computable without a model's opinion, or the no-voting rule is violated at the gate. If you believe
no such replacement exists, say so plainly — that is a legitimate and important answer.

**Q3. The 91 cases with no executable falsifier.** Options include commissioning falsifiers for them,
changing what the metric measures, changing how it is measured, or accepting the gap and REPORTING
it. Which, and why? The founder asked exactly this: "To build and commission the missing falsifiers?
To change the measurement metric itself and, or how it is measured? All of these or one of these?"

**Q4. What is the cheapest change that stops the gap being SILENT?** This project's repeated failure
is not the defect but that nothing reports it. Name a concrete artefact.

**Q5. What executable check would refute your own proposal?**

## Constraints

* **TOOLS DECIDE, NOT VOTES.** Derive, execute, quote real output. Any proportion needs a confidence
  interval.
* Any proposal that requires a model to assign a number that then gates anything is self-refuting
  here. Check your own answer against that before submitting it.
* Moving the 0.7 cut requires a NEW DATED PRE-REGISTRATION. A proposal that silently moves it is
  book-cooking, which 4 of 5 seats flagged unprompted in May.
* Do not pad. The founder has ADHD and reads every word.

## Context so your focus does not narrow

CDSFL uses structured Popperian falsification and a multi-model panel to find defects in STEM
artefacts. Biological names in the codebase are analogy only. The mathematical model has survived
every attack in the project's life; the failures have always been mechanical or in the prose ABOUT
the mathematics — 2 examples from the last 48 hours: a universal directive told every model that
C(n) is the recursive equation at prior 0, when at prior 0 that recursion is identically 0 forever;
and the fix-acceptance gate's threshold turned out to sit below the true break-even at 297 of 297
reachable settings. Assume the same shape here: look for the mechanical fault before concluding the
severity model itself is wrong. A simulated full-harness run is planned next, so a proposal
exercisable in shadow during that run is worth more than one that cannot be.
