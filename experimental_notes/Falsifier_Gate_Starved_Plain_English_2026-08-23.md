# The falsifier gate was rewarding the falsifiers that never read the document

**23 August 2026, 17:20 BST.** Plain-English companion to *The falsifier gate rewards falsifiers that never read the document* (the technical convergence record). Panel: CC1, CC2, Fable, convergence compelled.

## The finding in one paragraph

The discrimination control was not blind. It was starved. The gate sitting upstream of it had been destroying every falsifier that actually opened the target document, and passing every falsifier that ignored it. Remove the obstruction in a scratch copy and the control immediately returns `DISCRIMINATES` — the verdict it was designed for and has never once produced on a live run. One reviewer produced it six times in an afternoon; the other produced it once and called it the first in the project's history.

## Why it happens

Every falsifier runs inside a sandbox, and the sandbox hands it an empty throwaway working directory so that nothing it does can touch the real project. The target document does not exist in that empty folder.

So a falsifier written the sensible way — opening the document by its short project-relative name — fails on a missing file. The gate records that as an error and routes the finding away as unusable.

A falsifier written the lazy way — one that opens nothing and restates the document's numbers from memory — does not care where it runs. It executes cleanly and is recorded as confirmed.

**The gate discarded the falsifiers that examined the evidence and kept the ones that did not.** It was rewarding precisely the failure the discrimination control exists to catch.

## The measurement

Both reviewers took the control experiment's ten findings, extracted the falsifiers the models wrote, and re-ran each twice: once exactly as the gate runs it, once with the working directory pointed at the project. They worked separately, in isolated copies, without contact. Their results agree row for row.

| falsifier | opens the document | gate's verdict | with the directory fixed |
|---|---|---|---|
| two of them | no | confirmed | confirmed (no change — it opens nothing) |
| five of them | **yes** | error | **confirmed** |
| one of them | **yes** | error | **refuted** |

Five sound instruments were being thrown away, and one of them carried a genuine refutation the project never saw.

## Why the run halted, twice

Six falsifiers failed on the missing file. Each failure demoted its finding to unconfirmed. Each unconfirmed critical went to the routing ladder, which asks a stronger model for a better falsifier. Both rungs re-ran their replacements through the same broken directory, failed identically, and the ladder reported itself exhausted. Six criticals then sat irreducible against a bound of two, the queue alarm fired, and the run halted at round zero.

Four of those six were harness artefacts, not model failures, and all four carried high severities (0.75 to 0.88), which is why they counted as criticals.

One reviewer predicted from the code alone, before the second run's result existed, that a re-run would halt at round zero for the same reason. **It did.**

## The part that makes it circular

Three details turn a bug into a self-reinforcing loop:

1. **The round instruction tells models to open the target by its relative path** — in
capitals. The harness orders the behaviour it then punishes.
2. **The drafting tool shares the same empty directory.** A model iterating towards a
correct falsifier watches it fail on a missing file and reasonably concludes that reading the document does not work. The harness was training the panel away from reading the evidence.
3. **No test anywhere pins this behaviour.** The repair that shipped the day before
added tests for three other things and none for this.

## What CC1 got wrong

- **"The two flagged falsifiers never open the document."** Survived. Verified by
direct reading.
- **"The control caught two of two, 100%."** Arithmetically true, inferentially
worthless. The sample was size two and was selected by the very defect under investigation. The control's ability to judge a genuine falsifier was never measured.
- **"An internal counter mechanically detects detachment."** False. That counter only
counts substitutions of the project's full address, so it reads zero for every falsifier using a short relative name, whether or not it reads the document. Refuted by six executed counterexamples, including one that reads the document through the standard library's line cache and so contains none of the usual file-opening words. The sandbox's own design notes already state the principle violated: a path is a string a program computes, so reading the source cannot decide where the program will read.
- **"Seven of thirty-four instruments remain."** Wrong by roughly four times, in the
reassuring direction. Five instruments are verified by measurement; the true open count is **twenty-nine of thirty-four**. The heuristic behind the other twenty-seven is wrong three times in five by its own printed calibration, always over-claiming — it scored the falsifier gate as commissioned one day before this defect was found inside it.

## The right fix was already written, and switched off

CC1 proposed detecting detachment by inspecting a falsifier's source for file-opening operations. Both reviewers rejected it: there is no closed list of ways a program can read a file, and building a determinate verdict on an indeterminate test — then using it to demote a confirmed finding — would create a fresh instance of the project's signature failure.

The sound test already exists in the sandbox's design, in writing, unbuilt. The sandbox's audit layer watches every file operation a falsifier attempts, and its stated second purpose is to record whether the falsifier ever opened its target. **It records refusals only. It has never recorded a permitted open.** One reviewer sizes the repair at four lines.

Once it exists, detachment becomes observed fact rather than inference, and the answer is correct no matter how the program computed the path.

## The one disagreement, and how it resolves

CC2 proposed naming the new verdict `DETACHED_FALSIFIER`. Fable demonstrated by execution that the name claims more than the measurement supports: a falsifier that genuinely reads the document, but falls back on a memorised value if the read fails, lands in the identical record. The existing probe measures whether output changes when the document changes — insensitivity to content, which is strictly weaker than never reading it.

**They compose rather than compete.**

| verdict | available | what it means |
|---|---|---|
| `TARGET_INSENSITIVE` | now, from the existing probe | output does not depend on the document's content |
| `DETACHED_FALSIFIER` | after the four-line audit fix | the falsifier never opened the document at all |

Fable's name is adopted for what is measurable today. CC2's becomes correct only once the audit layer records permitted opens.

## A decision that is yours, not an implementation

Both reviewers reached the same wiring independently: the new verdict feeds the routing ladder, and must **not** join the set that drives automatic demotion — that set demotes terminal statuses unconditionally, and adding to it switches on blocking behaviour that is deliberately off by founder ruling. That mistake was made once and three tests caught it.

Fable raised an objection needing a ruling rather than code. If the new insensitive verdict blocks a finding while the older non-discriminating verdict stays advisory, the gap between them is one cosmetic line: a model could add a read it then ignores and escape the sanction while changing nothing. This is the mid-August panel's access-versus-dependence objection verbatim. Fable's position: **both outcomes block or neither, as one ruling rather than two wirings.**

## Two further blocking defects, both in the acceptance gate

**Reading the suite result.** The gate collects failing tests by scanning for lines beginning `FAILED`, captures the suite's exit code, and never examines it. When a suite fails to *load* — a syntax error, a removed import — it aborts before any test runs and produces no `FAILED` lines at all. The gate sees an empty failure list, concludes nothing went red, and **accepts the patch**. A change that broke every test in the repository would be certified green by the gate built to prevent exactly that. Its own notes say a failure and a crash must never look the same; here the crash looks like a pass.

**The baseline.** Before judging a patch the gate measures which tests already fail without it. If that measurement fails — a workspace that could not be created, a timeout — it records the baseline as **empty** and caches that for every later candidate. Every pre-existing failure then counts as newly caused, every patch is rejected, and the acceptance rate collapses toward zero. The project's own written interpretation of near-zero acceptance is *the models cannot do the task*. Both reviewers found this independently; its own documentation records that it already falsely rejected one valid patch the previous day.

## Is the work bunk?

**No.** Both reviewers, definitively.

CC2's reasoning: the instruments are a closed, hand-written list in source, not a set that grows when examined. Every defect closed the thing it named. What recent work revealed is not new components but sub-components that always existed and were never enumerated — a resolution problem, not a divergence problem, and refining the unit of enumeration terminates because the code is finite. *"A backlog, not a regress."*

Fable dissents on strength, and the dissent stands rather than being smoothed: the phrase *demonstrably closer* needs a convergence curve — defects per run over time — that nothing tracks. Until it exists and bends down, the supportable claim is narrower: **the instrument now fails loudly instead of silently, and one dominant defect class remains active.**

Fable also names a bias outranking both positions. All eight defects found in two days had the same direction of error: every one debited the models' measured competence, the precise quantity this project exists to measure. **No model-competence figure should leave this bench until a run completes with no new harness defects.**

## What must happen next

**No further paid run until the working-directory repair lands.** Both reviewers, unprompted, independently. At the current state, every prose-target run is guaranteed to spend a full five-model round — roughly nineteen minutes — and halt at round zero. Two runs have now demonstrated it.

The repair must not simply point the working directory at the project. The empty folder exists so a falsifier cannot write into the real tree, and that protection is worth keeping. Both reviewers converged on the alternative: build a scratch folder containing a copy of the target at its expected relative position and point the working directory there. Reads resolve; writes stay harmless. CC2 adds that the audit layer already receives the mode of every file operation, so refusing write access outside the scratch folder closes the remaining risk entirely — and no honest falsifier writes anything.

Ship it with the regression test that exists nowhere today: **a falsifier that opens its target by a short relative name must reach a confirmed verdict through the main gate.**

## Provenance

Both reviews were read-only, in separate disposable copies, with no contact between reviewers. Every load-bearing claim in both was produced by executing the project's own code rather than by inspection alone. Full unfiltered text of both, with all source references intact, is preserved alongside the technical record. Nothing has been applied.

Written under CDSFL note standard v1.2 (14 May 2026).
