# Exp 52 roles — the question answered, and CC1's objection withdrawn

**Owed since 2026-08-27.** The founder asked *"So what do you propose? Who should be the finder? CC2 and
Fable between them? Fable alone?"* and added the correction that mattered more than the question:

> *"in your traditional role as 'curator'… why is this even an issue? You would remain the curator and would
> remain fully within this role, which has never proved a problem before? **You are clearly conflating the
> process of 'panel review' with that of a full blown panel member.** In both cases however this has never
> been your role."*

## The founder is right, and the record settles it in one query

CC1's stated concern was: *"I cannot both find and curate on the same target. Curating experiment 52 means
seeing its planted defects, which disqualifies me as a blind finder on that target specifically."*

**That disqualification is from a role CC1 has never held.**

Across every archived experiment, findings carry a `source_model`. The counts:

| source_model | findings |
|---|---|
| Gemini | 392 |
| DeepSeek | 271 |
| ChatGPT | 174 |
| CC2 | 163 |
| Codex | 154 |
| **CC1** | **0** |

**Zero of 1,154.** The dispatched panel for a live run is `['CC2', 'ChatGPT', 'Codex', 'DeepSeek',
'Gemini']`. CC1 runs the harness; it has never been in the panel.

**The objection is withdrawn.** It was a conflict invented rather than observed, and one query refutes it.

## The distinction the founder drew, restated

The two things CC1 conflated are genuinely different and both should continue:

**A panel member** is one of the five models dispatched into an experiment. It reads the target blind and
produces findings that enter the registry with its name on them. CC1 is not one and never has been.

**A panel review** is the `cc2`/`fable` confer dispatch — a review OF work, not participation IN an
experiment. Under `pr` CC1 holds its own position there, as it did on the canary build, where its position
was written and committed *before* either reviewer returned. That is not the same as being a finder, and it
creates no contamination of any experiment.

## The proposal

**Nothing changes.** Exp 52 runs with the standard five-model panel as finders. CC1 curates, exactly as in
exp 40 through 51, which is the arrangement the founder describes as never having been a problem.

The re-authoring spec at `experimental_notes/Exp52_Reauthoring_Spec_2026-08-27.md` still carries the
withdrawn objection and has been corrected in place, since a spec asserting a rule the founder has overruled
is the documentation-staleness defect this project treats as equal in standing to a code defect.
