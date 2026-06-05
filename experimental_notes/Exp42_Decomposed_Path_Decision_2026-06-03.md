# Experiment 42, the chunking problem, and a decision to make

**2026-06-03 17:45 BST**

## What the system is trying to do

The system reviews a piece of code using a panel of five AI models. Each model hunts for bugs. The founding principle is that whether a reported bug is real should be decided by **running a tool, not by the models voting** among themselves. The forensic study earlier this session confirmed that truth-by-voting was exactly where the project had drifted from its own principle, so the whole point of this work was to put tools back in charge of deciding what is true.

## The fix that was built and confirmed

The mechanism now works like this. When a model reports a serious bug, it must attach a small runnable test, called a **falsifier**. The test imports the real code under review and is written so that it fails only if the bug is genuinely present. The **runner** (the controlling program) then runs that test itself, and the result of that run decides the verdict. The model's opinion no longer decides anything. If a model attaches no runnable test, or the test is broken, the finding goes to a human rather than being waved through. That is the safety property that matters most: the system never confirms a bug it cannot mechanically demonstrate.

That entire mechanism was built, tested, and committed during this run, across **seven commits** (`32a006a` → `5ae340b`); **300+ automated tests pass**. Three real bugs were caught and fixed along the way:

1. **Auto-confirm bug** — broken test code was being read as a confirmed bug, the exact rubber-stamp the whole fix exists to prevent.
2. **Launcher drop** — the launcher silently dropped the switch that turns the new mechanism on, so the experiment would have quietly run the old voting system with no error.
3. **Crap-out bug** — a model that kept requesting the tool every iteration could return nothing at all, losing its whole contribution for the round.

All three are fixed and pinned with their own tests.

## How far the run got

Experiment 42 was launched twice. The first launch was paused within the first round, because live monitoring caught that large files were being sent down a path that did not carry the tool — fixed and committed. The second launch ran the first full round on all five models with the tool active everywhere. Then the first verdict arrived: **0 confirmed, 0 refuted, 14 findings sent to human review.** The run was paused there for analysis.

## What "14 to human review" actually means

This is the important part, because it is **not** a failure of the safety mechanism — the mechanism did exactly the right thing. It refused to confirm fourteen serious findings because none arrived with a runnable test it could re-run. The problem sits upstream, in how those findings were produced. Two separate causes:

**Cause 1 — a format clash (4 of 5 models).** The composer file under review is large (~60,000 characters). For large files the system breaks the file into chunks, feeds them in pieces, then asks for a final summary. This chunking was added by an earlier experiment to stop output quality collapsing on very large inputs. But the chunking summary instruction was written for the *old* way of describing a falsification — as prose. It literally tells the models to write a section called "FALSIFICATION (FALSIFIER / ATTEMPT / RESULT)", in words. So four of the five models did exactly that: they wrote their tests as sentences ("the finding would be false if…") instead of as runnable code. Several actually ran code with the tool to check their reasoning, then reported the result in prose anyway. With no runnable code block, the runner had nothing to re-run, and every serious finding correctly fell through to human review.

**Cause 2 — a lost-text bug (the 5th model).** The fifth model, driven through a command-line tool rather than a web-style interface, produced a full set of findings (>13,000 characters). But a separate bug in the chunking path for that model threw the text away and returned an empty result, so its findings never reached the runner. That bug was exposed by giving the path tool access.

The pattern worth noticing: the chunking path was built for the old prose style and for very large inputs, and it is now fighting the new runnable-test mechanism. Each fix on that path has uncovered another problem on it.

## The decision to make

**Option 1 — keep the chunking and fix its problems.** Rewrite the chunking summary instruction so it demands a runnable test in code rather than prose, and fix the bug that throws away the command-line model's text. Faithful to the earlier experiment's quality protection — but given the pattern, more problems on that path are likely.

**Option 2 (recommended) — route around the chunking for files of this size.** The composer file is 60,000 characters, *below* the 80,000-character threshold where the quality collapse that chunking guards against actually begins. Below that threshold, the decision to chunk is just caution inherited from older, smaller models. Meanwhile the simple path — sending the whole file in one go with the tool attached — is already **proven clean** in the controlled tests (it produced a proper runnable test importing the real code, and the runner decided correctly). Routing files below the threshold to that proven path fixes **both** problems at once, the command-line model included, because its simple path works too.

The recommendation is Option 2: the faster route to a clean first result, using the path already shown to work. The one honest risk is that 60,000 characters in a single prompt could still degrade a model whose real comfortable limit is lower — which is part of why the chunking exists. The tool reduces that risk (a model can inspect the code actively rather than holding all of it in mind), but it is unproven at this size; the first round of a re-run would show immediately whether the risk is real.

**Nothing has been changed in the code since the pause. The experiment is stopped and waiting on this decision: keep the chunking and fix it, or route sub-threshold files to the simple proven path.**

---

Written under CDSFL note standard v1.2 (14 May 2026).
