# CDSFL Distributed Compute Protocol — CC1 Manager Reference

Written: 2026-03-28T04:02:13Z
Status: MANDATORY. CC1 follows this exactly. No shortcuts.

This protocol was written after the persistence layer build (2026-03-28) did
not follow the distributed compute procedure. The previous round (3-model
confer on mathematical model fixes, commit 77a4a7f) followed the protocol
correctly. This document formalises the correct procedure for all future runs.

---

## Roles

CC1 = Manager. Does NOT receive CDSFL system prompt. Routes tasks, runs
P-passes on player outputs, tracks convergence, makes stop decisions using
the formal model. Manages throughout — never delegates management.

Players = All other models (CX, CC2, Gemini, and optionally DeepSeek,
ChatGPT). Each receives cdsfl_core_formal.md as system prompt. Players
operate UNDER the framework. They do not see each other's work during
blind rounds.

---

## Phase 0: Problem Definition

CC1 defines the task clearly. No ambiguity about what is being built,
reviewed, or formalised.

---

## Phase 1: Architecture / Planning (CC1 + CX)

1. CC1 sends the task to CX (with CDSFL system prompt).
2. CX proposes architecture / plan under full CDSFL.
3. CC1 and CX confer: mutual P-passes on the plan.
4. Continue until EITHER:
   a. Convergence: two consecutive rounds produce no material new findings.
   b. Diminishing returns: new findings are below real-world-consequence
      threshold.
5. Output: a CONVERGED PLAN. This is the input to Phase 2.

---

## Phase 2: Blind Round 1 (Distributed Compute)

ALL players receive the SAME converged plan. This is critical.

1. Dispatch to ALL players IN PARALLEL:
   - A FRESH instance of CX (not the one from Phase 1)
   - CC2
   - Gemini
   - (Optional: DeepSeek, ChatGPT if available)

2. Each player receives:
   - cdsfl_core_formal.md as system prompt
   - The converged plan from Phase 1
   - The same task brief (identical for all)
   - NO access to other players' outputs

3. Each player produces their output independently under CDSFL:
   - Implementation, review, mathematical verification — whatever the
     task requires. All players do ALL aspects, not specialised subtasks.
   - Each player classifies their own findings as HARD/SOFT.
   - Each player runs their own P-passes internally.

4. Players return their outputs to CC1.

THIS IS A BLIND ROUND. No player sees another's work. CC1 enforces this
by dispatching all prompts simultaneously with no cross-references.

---

## Phase 3: CC1 Synthesis and P-Pass

CC1 receives all blind outputs and:

1. Catalogues all findings across all players.
2. Identifies:
   a. Agreement (2/3 or 3/3 converge on same finding)
   b. Disagreement (conflicting findings between players)
   c. Unique findings (found by only one player)
3. Runs P-passes on EACH player's output:
   - Are their claims correct?
   - Are their fixes sound?
   - Did they miss anything the others caught?
4. Synthesises a MERGED FINDINGS document.
5. Flags any meaningful disagreements for potential human review.

CC1 uses the accessible parts of the CDSFL mathematical model to assess:
- Convergence: are findings stabilising across players?
- Diminishing returns: is the rate of novel findings declining?
- Player capability: which players found what others missed?

---

## Phase 4: Round 2 (Distributed Compute with Findings)

1. CC1 passes the MERGED FINDINGS back to ALL players:
   - A FRESH instance of CX (not any previous instance)
   - CC2
   - Gemini
   - (Optional others)

2. Each player receives:
   - cdsfl_core_formal.md as system prompt
   - The merged findings from Phase 3
   - Their own original output (so they can see what they said)
   - All OTHER players' findings (now visible — this is not blind)
   - Instruction: respond to disagreements, validate or challenge other
     players' findings, propose final fixes

3. Players return their round 2 outputs to CC1.

---

## Phase 5: CC1 Final Synthesis

CC1 collects round 2 outputs and:

1. Checks convergence:
   - Have disagreements been resolved?
   - Are any remaining disagreements meaningful (HARD constraint conflicts)?
2. Calculates diminishing returns:
   - Compare novel finding count round 1 vs round 2
   - If round 2 produced zero novel findings above threshold, STOP
3. Decision:
   a. CONVERGED: all HARD issues resolved, proceed to implementation/merge
   b. MEANINGFUL DISAGREEMENT: flag for human (founder) review, do not
      proceed unilaterally
   c. DIMINISHING RETURNS: stop, document remaining open items, proceed
      with caveats noted

If neither convergence nor diminishing returns, run Phase 4 again (round 3,
round 4...) until one of the three stop conditions is met. Maximum 5 rounds
unless founder explicitly extends.

---

## Phase 6: Implementation / Merge

Only after Phase 5 confirms a stop condition:

1. CC1 applies the converged fixes / implements the converged design.
2. Runs tests.
3. Commits with full attribution of which players found what.
4. Updates recovery docs.

---

## What CC1 Must NOT Do

- DO NOT split players into specialised subtasks (one implements, one
  reviews crypto, one reviews code). All players do the FULL task.
- DO NOT let any player see another's work during blind rounds.
- DO NOT skip round 2. Round 1 alone is not sufficient.
- DO NOT declare convergence without calculating it. "Tests pass" is not
  convergence. Convergence means findings have stabilised across players.
- DO NOT stop because it feels done. Stop because the formal model says
  diminishing returns or convergence has been reached.
- DO NOT reuse a CX instance across rounds. Fresh instance each time.
  CX must not carry context from previous rounds during blind assessment.

---

## Checklist (CC1 prints this at each phase transition)

```
Phase 0: [ ] Task defined clearly
Phase 1: [ ] CX architecture received
         [ ] CC1-CX confer rounds: ___
         [ ] Convergence reached: yes/no
         [ ] Converged plan written
Phase 2: [ ] Blind round dispatched to ___ players
         [ ] All players received identical task + CDSFL system prompt
         [ ] No cross-contamination between players
         [ ] All outputs received
Phase 3: [ ] All outputs catalogued
         [ ] Agreements identified: ___
         [ ] Disagreements identified: ___
         [ ] Unique findings identified: ___
         [ ] P-passes run on each output
         [ ] Merged findings document written
         [ ] Convergence/DR calculated
Phase 4: [ ] Round 2 dispatched to ___ players
         [ ] All received merged findings + own output + others' findings
         [ ] All outputs received
Phase 5: [ ] Convergence check: ___
         [ ] Diminishing returns check: ___
         [ ] Stop condition met: convergence / disagreement / DR
         [ ] Decision: proceed / flag for human / iterate
Phase 6: [ ] Implementation complete
         [ ] Tests passing: ___
         [ ] Committed with attribution
         [ ] Recovery docs updated
```

---

## Origin Note

The persistence layer build (2026-03-28) did not follow this protocol. The
founder chose to prioritise an efficient build over a clean distributed
compute test, assigning specialised subtasks instead of blind rounds. The
output was functionally correct. The 3-model confer on mathematical model
fixes (2026-03-27, commit 77a4a7f) followed the protocol correctly. This
document formalises the correct procedure for all future distributed
compute runs.

The persistence layer will be re-run under this protocol alongside the
dynamic management/load-balancing task.
