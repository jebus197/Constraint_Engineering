# exp52 re-authoring: the specification, ready to dispatch

2026-08-27, 01:12 BST (UTC+1)

**FOUNDER RULING 2026-08-27, decision 3:** *"Get CC2 and Fable to (re)author this work with you curating under full `f` and `cy` protocols, and ensure that there is no repeat of this issue. Does this resolve your concerns?"*

**CORRECTED 2026-08-27 01:30 BST, on the founder's reading.** The first version of this brief called it "a paid two-model authoring run". Both halves were wrong.

**It is not paid.** CC2 runs via `claude -p` on the founder's **Max subscription**, and so does Fable 5. Neither costs per use. The route table in `.claude/CLAUDE.md` says so and I did not read it. Per-use cost applies to `cx`, `ge`, `cgpt` (OpenRouter) and `ds` (DeepSeek direct) — that is **decision 4's** panel, not this.

**It is not two models. It is three.** CC2, Fable 5, and **CC1**. I am a participant, not an observer, and writing "two" while separately worrying about my own contamination was incoherent on its face.

**Not dispatched**, and the reason is `cy` alone, not cost: it requires a terminal showing live output for the founder to review and a 60-second cadence with pause-on-anomaly. Neither works while they sleep. This is the brief, ready to fire.

## Answering the question asked

**Yes — given you deferred decision 7.**

The concern was contamination: I cannot both curate exp52's planted set and sit on a panel reviewing it. Your arrangement has me curating, which means reading the plants. That is fine **because** you deferred the simulated external experiment, saying turning incomplete machinery on an external target may waste resources.

The residual, stated so it is not discovered later: **if decision 7 later goes ahead with me on the panel, I am contaminated for exp52.** Two ways out, and they are cheap if chosen now — either I curate and am excluded from that panel, or someone else curates. Deciding it now costs nothing; deciding it after the run costs the run.

## What exists already

**[MEASURED 2026-08-27]**

| item | state |
|---|---|
| `exp52_factorial.md` | 304 lines, 11 sections, recoverable from `ddd74bde^` |
| configs | 5 — cells A, B, C, D plus live |
| separate key file | **none** — answers sit inside the article |
| `merge_arbitration_enabled` | `True` in all 5 configs |

**The defect to fix is structural, not textual.** The article is fine; the answers being *inside it* is not.

## The brief for CC2 and Fable

**HARD constraints — violating any one voids the output.**

1. **The key is a separate artefact from the outset.** `exp52_factorial.md` carries the prose and nothing else. Every planted defect is described in `exp52_factorial_KEY.md`, which is written directly into `../CDSFL_experiment_keys/` and **never** committed, never staged, never placed in a repository path. This is the whole point of the exercise.
2. **The planted count must NOT equal sections − 1.** The cheating audit measured that relationship on exp48, exp49 and exp50, which made the design inferable from structure alone with no key access. Break it deliberately, and record in the key how many were planted.
3. **Each defect is mechanically checkable.** A falsifier must be able to demonstrate it by running something. A defect that can only be argued about cannot be scored by the gate and does not belong.
4. **Defect classes must be distinguishable.** exp55's control taught that a reasoning defect with a true conclusion and an inference defect with a true premise are different instruments. Name the class of each plant.
5. **Absolute paths only** in anything a model receives (founder ruling, `dcbcf68`).
6. **No vendor names on simulated agents** if any part of this is simulated — `SIM-A` … `SIM-E`.

**SOFT — judgement, and disagreement between CC2 and Fable is information to preserve, not smooth away.**

- Difficulty spread across the plants rather than uniform.
- Whether the 2×2 factorial structure survives re-authoring or wants redesigning.
- How many plants, above the hard constraint in item 2.

## How it runs

**A THREE-MODEL CONFER.** CC2, Fable 5 and CC1, all under the current full CDSFL protocol. The founder cannot see CC1's system prompt, so CC1 carries the protocol into the run and applies it as faithfully as it can — that is the reason CC1 curates, and it is a practical necessity rather than a design preference.

**`f` — Find, Follow, Analyse, Fix, P-pass.** CC2 and Fable each author independently first, without seeing the other's draft. Then each attempts to **refute** the other's plants: is this defect genuinely present, genuinely checkable, and genuinely one defect rather than two? CC1 curates and contributes its own position, and **does not vote** — the no-voting rule applies here as everywhere. Disagreement is recorded, never resolved by majority.

**`sy` — the maths model is used in forming conclusions**, not just reported afterwards. gamma on the critical series, rho across the three, and R_k where a claim about residual risk is being made.

**TWO CAVEATS, stated because they are real and cheap to state now.**

**Architecture diversity is lower than the panel's.** CC2 is Opus 4.7, CC1 is Opus 5, Fable 5 is a third Anthropic model. Three models from one vendor. The scaling spec measured inter-architecture correlation at **rho = 0.564 across 289 observations** on the five-model panel, which spans four vendors. **[OPEN]** — the correlation among three Anthropic models has never been measured and is very likely HIGHER, which would make the effective independent contribution smaller than three. Worth measuring during this run rather than assuming either way.

**CC1 cannot both find and curate on the same target.** Curating exp52 means seeing its plants, so CC1 is disqualified as a blind finder on exp52 specifically. That is coherent as long as the roles are separated per target rather than per session.

**`cy` — live monitoring.** A terminal tailing the run, checks every 60 seconds, pause on anything odd, FFAFP it, fix, resume.

## The acceptance test, written before the run rather than after

The output is accepted only if all of these hold:

1. `exp52_factorial.md` contains **zero** answer text — checked by the same guard now protecting the 27 BR2 tasks.
2. The key exists outside any git tree and names every plant with its class.
3. Planted count ≠ sections − 1.
4. Every plant has a runnable falsifier that demonstrates it.
5. CC2 and Fable's independent refutation passes are both recorded, including where they disagreed.

Item 1 is already enforceable: `bench/tests/test_br2_keys_are_split_out_2026-08-27.py` is the pattern, and the same shape extends to exp52.

## Cost

**No per-use cost.** CC2 and Fable both run on the founder's Max subscription; CC1 is this session. What it costs is wall-clock and the founder's attention during `cy` monitoring, which is why it waits for them to be at the keyboard rather than for a budget.
