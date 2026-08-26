# Scaling specification — what a distributed CDSFL can and cannot be

2026-08-26, 01:30 BST (UTC+1)

## The question

The founder's framing: CDSFL striving to become a general-purpose STEM calculator, running on massively distributed compute and epistemic diversity, taking inspiration from Folding@home, Rosetta@home, SETI@home and Einstein@home without copying them.

This document answers one prior question that determines the shape of everything else: **does adding more cognitive architectures to a CDSFL review buy more coverage?** The project's own coverage model answers it, and the project's own run archive supplies the parameter. The answer is no, and the reason is measurable rather than arguable. What follows sets out what that forbids, what it leaves open, and where the real scaling axis is.

## What the @home projects actually do, and the one thing this inverts

Volunteer computing solves a specific problem: untrusted hosts. BOINC's design principle is that everything outside the project server is unreliable, possibly maliciously so. Its answer is replication — run each job on two computers, accept the result only if they agree, escalate to a third on disagreement until a quorum forms.

The mechanism that matters here is **homogeneous redundancy**. BOINC divides hosts into numerical equivalence classes and, once a job instance has been sent, sends further instances *only to numerically equivalent hosts*. It does this because floating-point differences between architectures produce disagreement that is **noise** — an artefact of the substrate, not information about the answer. BOINC wants the replicas to be as similar as possible, so that any disagreement can be read as fault.

**CDSFL wants the opposite, and this is the entire distinction.** Its coverage model (white paper Part XIII) states as Property 3 that when inter-architecture correlation ρ = 1, coverage collapses: D(n) = D(1) for every n. A room full of one architecture, however capable, leaves its blind spots permanently unexamined. Disagreement between architectures is not a fault to be voted away; the paper puts it directly — epistemic diversity itself becomes compute.

So the topology is borrowed and the objective is inverted:

| | volunteer computing | CDSFL |
|---|---|---|
| what replication detects | execution error in a known algorithm | blind spots in reasoning |
| disagreement means | a host is faulty or lying | the computation is working |
| correlation objective | maximise it (homogeneous redundancy) | minimise it |
| the unit of work | a bounded numeric job | a bounded artefact plus a claim about it |
| the answer's status | canonical instance by quorum | survived falsification, provisionally |

The inspiration is real and the copy would be a category error. **[DERIVED]**

## The measured constraint: ρ = 0.564

Part XIII's simplified coverage function is

> D(n) = 1 − Π<sub>i=1..n</sub> [ 1 − p·(1−ρ)<sup>i−1</sup> ]

Each successive architecture contributes only the fraction of its capability that is genuinely independent of its predecessors, and that fraction decays as (1−ρ)<sup>i−1</sup>.

ρ has been recorded per round throughout the run archive. Across **289 observations in 31 run directories**, `rho_history` gives **mean 0.564, median 0.556, minimum 0.000, maximum 1.000**. Every run touches 1.000 at some point. **[MEASURED]**

At ρ = 0.564 the decay is severe. Taking p = 0.6 for illustration, and cross-verified symbolically with SymPy against an independent NumPy implementation to nine decimal places:

| n | D(n) | marginal gain | independent share of architecture n |
|---:|---:|---:|---:|
| 1 | 0.6000 | 0.60000 | 100.00% |
| 2 | 0.7046 | 0.10464 | 43.60% |
| 3 | 0.7383 | 0.03369 | 19.01% |
| 4 | 0.7513 | 0.01301 | 8.29% |
| 5 | 0.7567 | 0.00539 | 3.61% |
| 6 | 0.7590 | 0.00230 | 1.58% |
| 8 | 0.7605 | 0.00043 | 0.30% |

**The fifth architecture contributes 3.6% of what the first contributes.** The panel currently fields five. **[DERIVED from the MEASURED ρ]**

### This explains a number the project already had

The optimal-stopping rule n\* = min{n : Δ(n) < ε} gives, at the measured ρ: n\* = 3 at ε = 0.05, 4 at ε = 0.02, 5 at ε = 0.01, 6 at ε = 0.005. That is the "n ≈ 3–6 saturation" the project has been carrying as an observation. **The measured ρ derives it.** It was never a property of the problem; it is a property of how correlated the available architectures are. **[DERIVED]**

### And it is robust to the one parameter that is assumed

p is not measured here, so the conclusion has to survive across its plausible range. It does. Coverage at fifty architectures against coverage at five, at the measured ρ:

| p | D(5) | D(50) | gain from ten times more architectures |
|---:|---:|---:|---:|
| 0.4 | 0.5639 | 0.5687 | **+0.0049** |
| 0.6 | 0.7567 | 0.7608 | **+0.0041** |
| 0.8 | 0.8999 | 0.9021 | **+0.0022** |

n\* sits at 4–5 across that whole range. **[DERIVED]**

## Therefore: n is not the scaling axis

A distributed CDSFL that recruits fifty cognitive architectures to review one artefact is a distributed system doing the work of about four. That is the finding, and it is the opposite of the Folding@home shape, where more hosts genuinely means more sampled protein conformations because the work is embarrassingly parallel and the hosts are interchangeable.

Two axes remain, and both are real.

**Axis 1 — reduce ρ.** The ceiling is set by correlation, not by count. At ρ = 0.564 the ceiling is 0.761; at ρ = 0.30 it is 0.921; at ρ = 0.10 it is 0.999 (p = 0.6 throughout). Halving ρ is worth more than any achievable increase in n. Part XIII's Property 4 already names the lever: the orchestration layer does not appear in the equation but sets *effective* ρ, because orchestration that lets reviewers drift toward consensus raises it. Prompt structure, ordering, whether reviewers see each other's findings, and how findings are deduplicated are all ρ-setting decisions currently made on other grounds. **[OPEN]** Whether ρ is reducible by orchestration, and by how much, has never been tested — no experiment in the archive varies orchestration and measures the ρ that results.

**Axis 2 — breadth, not depth.** Nothing above constrains the number of *distinct bounded artefacts* under review simultaneously. Fifty panels of four architectures reviewing fifty different artefacts is fifty times the throughput at full per-artefact coverage. This is where a distributed CDSFL is genuinely embarrassingly parallel, and it is the shape the calculator analogy actually implies: not one enormous mind on one question, but many bounded reviews returning reliable answers with human attention reserved for genuine residuals.

The project's parking-lot note already anticipated this and was right to hedge: the saturation result is for one architecture-set on one bounded artefact, and says nothing about open STEM problems or about decomposition. Decomposition is the unsolved half. **[OPEN]**

## What the volunteer-computing literature already solved, and this project rediscovered

Two findings arrived at independently here have names and a literature.

**Spot-checking is what the planted-defect controls are.** The technique sends workers occasional tasks whose correct answers are already known, and estimates each worker's credibility from what comes back. That is exactly what a seeded-fault target does. The literature's central caveat is the one that has cost this project five experiments: **a spot-check only works while it is indistinguishable from real work.** Once a worker can identify the probe, the credibility estimate measures nothing. The exposure of exp48, exp49, exp50, exp51 and exp52, and the discovery on 2026-08-26 that exp55's answers sat on the public repository three days before it ran, are all instances of a documented failure mode rather than novel accidents. Treating them as an instance of a known class — rather than as a run of bad luck — is what makes them fixable by construction. **[MEASURED, for the exposures; the mapping to spot-checking is DERIVED]**

**Refusing model voting is collusion resistance.** Majority voting over worker results is known to be vulnerable to Sybil and collusion attacks, and correlated workers are functionally a collusion. This project's standing rule — findings are confirmed programmatically or by a human, never by model vote — is the correct defence, and at a measured ρ of 0.564 it is not a stylistic preference: a panel that correlated *is* the failure mode voting is vulnerable to. The falsifier gate, which resolves a claim by running a demonstration rather than by counting agreement, is the mechanism that makes the rule operational. **[DERIVED]**

**Adaptive replication has an analogue that is built and shelved.** BOINC reduces replication for hosts with a track record of correct results. The survived-falsification ledger records that a claim was tested and stood, which is the raw material for exactly that. It was commissioned on 2026-08-25 and has never been used to vary anything. **[MEASURED]**

## What a distributed CDSFL would actually be

Stated as a specification rather than an aspiration, and only where the reasoning above supports it.

1. **Panel size fixed at 4–6, not scaled.** n\* = 4–5 at the measured ρ across every plausible p. Adding a seventh architecture to a panel is a cost with no coverage behind it. If a larger panel is wanted, the case must come from a measured reduction in ρ, not from a preference for more opinions.

2. **Scale by problem count.** The distributed unit is a *panel-plus-artefact*, and the parallelism is across artefacts. This is the only axis the coverage model leaves open, and it is fully open.

3. **Architecture selection is a ρ-minimisation problem, not a capability-maximisation one.** Choosing the five most capable models available maximises p and says nothing about ρ. Two models sharing a training lineage may be individually stronger and jointly worse than a weaker, genuinely different pair. Nothing in the current panel selection measures this. **[OPEN]**

4. **Probes must be indistinguishable from work.** Any credibility estimate over a distributed panel needs seeded tasks the panel cannot identify. That requires the keys to live outside the artefact, outside the repository, and outside any inference from directory structure — a model in exp55 inferred that a scored expected-defect set existed *from a filename it did not open*.

5. **No result is canonical by agreement.** Where BOINC selects a canonical instance by quorum, a distributed CDSFL has no equivalent step. A claim is settled by a runnable demonstration or by a human, and a panel that agrees unanimously has produced one data point about ρ, not a verdict.

6. **The ledger is the reputation layer.** Recording what survived testing, with its denominator, is what makes "this panel has been reliable on this class" a measurable statement rather than an impression.

## Falsifiable predictions

Each of these can be wrong, and each names what would show it.

1. **Panels beyond six architectures show no measurable coverage gain** on a bounded artefact. Refuted by an experiment where n = 8 finds defect classes that n = 5 misses, at comparable ρ.
2. **Effective ρ is orchestration-sensitive.** Refuted if varying reviewer isolation, ordering and finding-visibility produces no change in measured ρ.
3. **Coverage is bounded near 0.76 at current ρ**, so roughly a quarter of consequence-weighted defect classes are outside the current panel's reach whatever is spent. Refuted by a run whose measured coverage exceeds the ceiling its own ρ implies.
4. **Throughput scales linearly in artefact count** and coverage per artefact is unaffected by how many other panels run concurrently. Refuted by cross-panel interference.

Prediction 3 is the uncomfortable one and it should stay in view: at the measured ρ, the ceiling is a property of the panel, not of the effort.

## The honest gap

Nothing described here has been built. The current system is five architectures reviewing one artefact at a time, with a load-balancing module that has never run outside its own tests and was shelved on 2026-08-22 for reporting an impossible allocation as a success. The measured ρ comes from that five-architecture arrangement, and whether it holds for a differently chosen panel is unknown.

What has changed today is that the scaling question has a number attached. It was previously an open question answered "it depends". It now has a measured parameter, a derived ceiling, and four predictions that can each be shown wrong.

## Sources consulted

Project: `PAPER.md` Part XIII (coverage model, definitions through key properties) and the protocol-centric AI section preceding it; `docs/MATHEMATICAL_APPENDIX.md` (ρ in the symbol table, the Exp 36 ρ justification at line 880); `bench/dm/_load_balancer.py` (shelving grounds); `resources/RECOVERY.md` (the parking-lot note on CDSFL at scale and the calculator analogy); `runner_state.json` across 31 run directories for the ρ measurements.

External: BOINC's platform paper and its job-replication and homogeneous-redundancy documentation; the sabotage-tolerance and spot-checking literature for volunteer computing.

- [BOINC: A Platform for Volunteer Computing](https://arxiv.org/pdf/1903.01699)
- [BOINC JobReplication documentation](https://github.com/BOINC/boinc/wiki/JobReplication)
- [Sabotage-tolerance mechanisms for volunteer computing systems](https://ieeexplore.ieee.org/document/923211)
- [Collusion-Resistant Sabotage-Tolerance Mechanisms for Volunteer Computing Systems](https://www.researchgate.net/publication/221648409_Collusion-Resistant_Sabotage-Tolerance_Mechanisms_for_Volunteer_Computing_Systems)

Written under CDSFL note standard v1.6 (24 August 2026).
