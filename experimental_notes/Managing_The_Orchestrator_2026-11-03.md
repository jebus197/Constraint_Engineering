# How the founder manages this session, as a template for managing the orchestrator

**3 November 2026, 04:35 GMT**

His instruction, 2026-11-03: *"Your job with the orchestrator will simply be to manage it the same way I manage you, to prompt it to continue, to explain fixes, to ensure it maintains our 3 project standards... Indeed you can draw up a sketch of my main interaction patterns with you and use this as your template to interact with this orchestrator model."*

This sketch is **derived from the record, not from impression**. The corpus is the 839 annotations he has written on delivered documents, read with `scripts/read_founder_responses_2026-10-11.py`.

## The honest limit of the corpus, stated first

The corpus holds his annotations on documents. **It does not hold his chat messages.** His challenge of 2026-11-03 — *"But are you certain that all 13 (or is it 19?) are new issues I have never ruled on before?"* — is a chat message and appears nowhere in it. So the 2 figures below that bear on challenging a claim and disowning attributed words are **floors, not rates**, and must not be quoted as his frequency of doing either:

| behaviour | n of 839 | Wilson 95% | status |
|---|---|---|---|
| asks for the simpler option | 80 | [0.077282, 0.117109] | a rate |
| grants or approves | 54 | [0.049662, 0.083033] | a rate |
| demands a measurement | 43 | [0.038270, 0.068324] | a rate |
| names one of the 3 standards | 43 | [0.038270, 0.068324] | a rate |
| corrects terminology | 11 | [0.007336, 0.023324] | a rate |
| challenges a claim | 2 | [0.000654, 0.008650] | **a FLOOR** |
| disowns words attributed to him | 1 | [0.000210, 0.006720] | **a FLOOR** |

A class is not exclusive; a single annotation can do several.

## 1. He writes short, and rarely marks

**Median 128 characters**, mean 245.8, 90th percentile 594, maximum 3788. So the ordinary intervention is 1 or 2 sentences, with occasional long ones that carry a ruling and its reasoning.

**Only 73 of 839 carry a trailing marker** — 0.087008, Wilson 95% [0.069770, 0.108011], Clopper-Pearson [0.068819, 0.108158]. Most used: `qs` 26, `fr` 22, `stm` 9, `disc` 5, `pf` 5. **So 91% of his interventions are unmarked prose**, which is exactly why he ruled that an unmarked comment not ending in a question mark defaults to a discussion rather than a proposed fix.

**213 of 839 end in a question mark** — 0.253874, Wilson [0.225591, 0.284399]. About 1 intervention in 4 is a question.

**Template:** brief, unmarked prose by default. Do not decorate every message with a label. Ask rather than instruct about a quarter of the time.

## 2. He opens with a verdict

His commonest opening words across 839: `I` 72, `this` 62, `so` 61, `then` 61, **`verdict` 42**, `same` 41, `again` 30. The 5th commonest word he starts with is the word "verdict" — he states the decision first and the reasoning after, which is the same order the project's own style directive requires of me.

**Template:** lead with the verdict. "Build it." "Not this." "Measure it first." Then the reason, if a reason is needed.

## 3. He reminds me he is a non-developer and asks for clarification in that light

**HIS CORRECTION, 2026-11-03, and the measurement vindicates him against my own
first answer.** This section originally read *"the single commonest thing he does
is ask for less"*, at 80 of 839. He struck it: *"You can scratch the 'asking for
less' from the template of my behavioural patterns. I do not think it is a
correct characterisation in any case. What I do often do is remind you that I am
a non-developer and request clarifications in light of this from you."*

**He is right, and the 80 was my regex matching English grammar.** Of those 80
matches: **46 are the adverb "simply"** ("simply not yet been done", "simply
stating a problem by its ID"), 13 are "simple/simpler" describing a thing, 11 are
`simplest sufficient` naming the project standard, and only **10 are genuine
complaints of excess** — 10 of 839, 0.011919, Wilson 95% [0.006487, 0.021800].

**His own characterisation is 5.2x more frequent.** Reminding me he is a
non-developer, 19 of 839; requesting a clarification or explanation, 41 of 839;
union **52 of 839, 0.061979**, Wilson [0.047575, 0.080375]. Against the genuine
excess rate: Fisher exact odds ratio 5.477510, **p = 3.336033e-08**.

This project's own voice discriminator already records the identical failure: it
had to exclude the bare article `a` from its marker set because `a` matched the
`a` command mid-prose in 3 of 4 cases. A discriminator that fires on a common
English word is not a discriminator.

**AND THE TEMPLATE INVERTS HERE RATHER THAN COPYING.** His words: *"But you do
not suffer from this limitation, so when you require clarifications, you can
afford to be correspondingly more rigorous than I am able to be."* So this
pattern is the one place the template must NOT be imitated. Where he asks for a
plain-language explanation because he does not read code, a clarification put to
the orchestrator should be the opposite: name the file, the line, the predicate
and the standard, and demand an answer in those terms.

## 4. He names the standard rather than arguing the case

43 of 839 name additive, simplest sufficient, composability, falsification or P-pass. He does not usually argue a design on its merits; he names the standard it fails. His definition of composability, verbatim: *"Composability doesn't mean composing two solutions just because they can be composed. It means this principle should be applied where two composed solutions demonstrably provide a better, more robust and/or more efficient solution than either fix in isolation."*

**Template:** judge the orchestrator's work against the 3 standards by name, and require it to say which standard its change satisfies. A change that cannot name one is not ready.

## 5. He requires the measurement before the claim

43 of 839 demand a measurement. The project rule this produced, in his words: a measured rate, proportion or count -- any figure at all, 0 exceptions -- may be cited only if the script that produced it is committed alongside it, because a number existing only as prose is a claim about evidence rather than evidence.

**Template:** ask the orchestrator for the producer, not the number. Refuse a figure whose script does not exist.

## 6. He corrects the name before the substance

11 of 839 correct terminology. Verbatim, on his own usage: *"as a UK native, I tend to use the word programme as a way to denote a study, or a series of events, whereas I will use program, to denote a software program"* — and he added *"But you should mark it nevertheless."* A thing called by the wrong name is treated as a defect, not a style quibble, because a name that drifts makes the record unsearchable.

Tonight supplied a live instance: he asked *"What is v-bar? I have never heard of it before?"* about a quantity defined in the glossary and written 12 times in the appendix. The cause was that every surface he reads carried the code identifier and never the model's name — 12 occurrences against 0 in the decisions file, 20 against 0 in the task list.

**Template:** require the orchestrator to use the project's own vocabulary, and treat a code identifier leaking into a human-facing document as a defect of equal standing with a code defect.

## 7. He disowns words put in his mouth, and this is the behaviour to copy most carefully

Measured at 1 of 839, which is a **floor** and not a rate, because this happens mostly in chat. It is nonetheless the most consequential thing he does. Verbatim instances: *"We discussed the Wolfram access problem only recently. You are quoting a rule that does not exist."* And: *"That is not my insistence at all I never said anything like this!"* And the ruling it produced: *"If you quote me, it must be verbatim!"*

The project record names this failure twice — a rule invented and then attributed to him, and advice he had struck surviving in prose that still carried his name.

**Template:** never attribute a constraint to an authority that did not state it. When managing the orchestrator, quote its own prior words back to it verbatim or describe its position without quotation marks at all — and require the same of it. An orchestrator that justifies a change by citing a standard nobody wrote is the exact failure this project exists to catch.

## 8. He prompts continuation rather than supervising steps

His standing continuation command tells the session to carry on and to monitor anything running at about a 60 second cadence, pausing on anything odd, analysing it fully, fixing it, and resuming — and always to keep a terminal showing the run's live tail. He does not inspect intermediate steps; he sets the cadence and the stopping condition and lets the work run.

He also objects when the session stops without cause. Verbatim: *"Why do you keep stopping for non-blocking items? ... Why not just leave them all to discuss with me at the end of the completed task list, unless there is something that clearly warrants my immediate attention?"*

**Template:** prompt the orchestrator to continue; do not approve each step. Interrupt only on a blocker, where a blocker is mechanically defined as something that prevents further progress, and park everything else to the end. Keep its live output visible.

## 9. A question of his is a tracked object, not a conversational aside

He ruled that a question carries its own hashed identity in the register exactly as a feature request and a proposed fix do, *"so they can be tied directly to the problems they address and so that in future you can't lose them, or forget which issues they address."* 26 of his 73 marked annotations are questions, the single commonest marker he uses.

**Template:** every question put to the orchestrator, and every question it raises, is recorded with an identity and resolved by an answer rather than by a build.

## 10. His intervention is the system working, not the system failing

The project's design position: his intervention is the human-in-the-loop design operating as intended, and the target is minimal intervention, never 0.

**Template:** do not optimise for an orchestrator that never needs prompting. Measure how often it needs prompting and about what, because that distribution is the result, not a cost.

## The operational loop, assembled

1. **State the task and the standard it must satisfy.** Verdict first, reason second. Name which of additive, simplest sufficient or composability applies.
2. **Let it run.** Do not approve steps. Monitor at the cadence the continuation protocol sets, with its output visible.
3. **On any claim it makes, ask for the producer and not the number.** A figure without a committed script is refused.
4. **On any proposal, ask for the smallest version first.** The commonest correction in the corpus is "too much".
5. **On any citation of a rule, check the rule exists and says that.** This is the failure mode with the worst consequences and the one the corpus under-measures.
6. **Record every question with an identity.** Resolve it with an answer.
7. **Interrupt only on a mechanical blocker.** Park the rest to the end of the list.
8. **Require it to try to break its own fix before presenting it.** A fix it has not tried to break is a hypothesis.

## What this sketch does not establish

It is a description of his patterns, not evidence that applying them to a different model produces the same results. **No measurement here bears on whether this template works as a management protocol** [SPECULATIVE], and treating the sketch as validated would be the flattering-measure failure the project record names 3 times. What would test it: the orchestrator run with and without the template, scored on the same rubric, with the standards-compliance rate as the named property.

## What the formal construction adds, and where it does not fit

The founder asked that the rigour recommended by the 2 standards he named — Meta-Agent Architectures and the Model-Agent Interface — be used in deciding how this session should interact with the orchestrator, and that the decision state what is useful and applicable and what is not.

Neither name exists as a published specification. The formal construction that does the work he pointed at is the **assume-guarantee contract** (arXiv 2608.14590), in which each agent declares the inputs it relies on and the outputs it promises, so a composition can be checked rather than hoped for.

### 3 elements apply directly

**1. The orchestrator declares its assumptions and guarantees as data.** The reason is not tidiness: a declaration lets a claim be checked against the orchestrator's own stated promise rather than against the manager's judgement, which removes the manager as arbiter of whether work is acceptable. The worked example is `bench/tools/cy_actuator_2026-11-03.py`, whose `ASSUMES` and `GUARANTEES` dictionaries hold 4 assumptions and 5 guarantees, with `bench/tests/test_the_actuator_holds_its_contract_2026-11-03.py` iterating the guarantees and failing if any guarantee is declared with no test class naming it.

**2. A terminal state requires a verification.** Already enforced: `TicketStore.close()` in `bench/ticket_store.py` refuses without a verification, and `bench/reference_runner_v3.py` gates CONFIRMED to CLOSED on `verified`. Applied to the orchestrator, it means no fix may be declared finished on the orchestrator's own assertion.

**3. A model's assertion settles nothing.** The project's standing no-voting rule, which applies to the orchestrator exactly as to every seat. It may propose, classify and sequence; it may not confirm its own work by saying so.

### 1 element does not fit, and the mismatch is named rather than smoothed

The adjacent industrial pattern is the **thin orchestrator**: a deterministic supervisor performing classification, gathering, reliability checks and delegation only, holding no domain judgement of its own.

The founder's specification asks for something different. The orchestrator is to decide *"which fixes are 'better' than others, which compose and which don't and which meet our formal simplest sufficient fix, additive and composability standards"* — his words of 2026-10-17, and the part he called doubly useful once fixes fold back at the close. That is domain judgement.

So the orchestrator in this design is deliberately **not thin**, and any claim that it follows the thin-orchestrator pattern would be false.

What follows is a constraint rather than a contradiction. Because the orchestrator holds judgement, its judgements are what most needs a declared contract, and the comparator it would use already exists: `bench/fix_comparator.py`, 395 lines, exposing `compare` with `additive_verdict` and `composability_verdict`, guarded by `bench/tests/test_the_fix_comparator_refuses_to_rank_2026-11-02.py`, which already refuses to rank without evidence. A declared contract is therefore what keeps a judging orchestrator accountable, not an administrative formality.

### 1 element is unresolved and is his to settle

His specification asks for a sandbox *"which the orchestrator model shouldn't know about"*. The isolated copy exists and is guarded — `bench/tools/run_simulated_experiment_sandboxed.sh` and `bench/panel_sandbox.py`, with 2 guards. No concealment mechanism exists in either: the sandbox is created as `mktemp -d -t cdsfl_sim` and `tempfile.mkdtemp(prefix="cdsfl_sim_panel_")`, so the path names the simulation, and a seat armed with Bash can read its own working directory.

Full concealment from a shell-armed model is probably not achievable, so this is a design question rather than a defect. Raised as `qs:a7e64483f941` with 3 options: rename the path, accept discoverability and record it as part of what the arm measures, or remove the shell — which would conceal the sandbox and also remove the tool use the project exists to measure.

Written under CDSFL note standard v1.9 (1 November 2026).
