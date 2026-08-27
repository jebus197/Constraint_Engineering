# exp52 re-authoring: the specification, ready to dispatch

2026-08-27, 01:12 BST (UTC+1)

**FOUNDER RULING 2026-08-27, decision 3:** *"Get CC2 and Fable to (re)author this work with you curating under full `f` and `cy` protocols, and ensure that there is no repeat of this issue. Does this resolve your concerns?"*

**Not dispatched.** `cy` requires a terminal showing live output for the founder to review and a 60-second monitoring cadence. Neither is possible while they sleep, and a paid multi-model authoring run whose output nobody reads for six hours is the opposite of what `cy` is for. This is the brief, ready to fire.

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
2. **The planted count must NOT equal sections − 1.** The cheating audit measured that relationship on exp48, exp49 and exp50, which made the design inferable from structure alone with no key access. Break it deliberately and record the chosen count in the key.
3. **Each defect is mechanically checkable.** A falsifier must be able to demonstrate it by running something. A defect that can only be argued about cannot be scored by the gate and does not belong.
4. **Defect classes must be distinguishable.** exp55's control taught that a reasoning defect with a true conclusion and an inference defect with a true premise are different instruments. Name the class of each plant.
5. **Absolute paths only** in anything a model receives (founder ruling, `dcbcf68`).
6. **No vendor names on simulated agents** if any part of this is simulated — `SIM-A` … `SIM-E`.

**SOFT — judgement, and disagreement between CC2 and Fable is information to preserve, not smooth away.**

- Difficulty spread across the plants rather than uniform.
- Whether the 2×2 factorial structure survives re-authoring or wants redesigning.
- How many plants, above the hard constraint in item 2.

## How it runs

**`f` — Find, Follow, Analyse, Fix, P-pass.** CC2 and Fable each author independently first, without seeing the other's draft. Then each attempts to **refute** the other's plants: is this defect genuinely present, genuinely checkable, and genuinely one defect rather than two? I curate: I do not author, and I do not vote. Disagreements are recorded, not resolved by majority — the no-voting rule applies here as everywhere.

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

Two model dispatches plus refutation rounds. Real money, and the reason this waits for a rested reader rather than firing at 01:12.
