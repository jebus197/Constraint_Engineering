# The rulings of 17 September, executed

2026-09-17, 23:16 BST, Europe/London.

## Summary

5 of the founder's rulings were carried out in 5 commits: Wolfram enabled for every seat and every agent as the second falsifier; the project instructions corrected; a fresh working tree for every panel attempt with nothing deleted afterwards; the missing instrument for CC1's own position built and implemented; and the 3 tests that failed outside a git checkout repaired rather than skipped. 1 further ruling asked for a measurement before a verdict, and that measurement is now in hand: Codex is separately available on OpenRouter, and a distinct Codex seat would cost 0.440 of what that seat costs today.

3 defects were found on the way, none of them in the work being done: an onboarding check that called a working Wolfram kernel absent, a simulated experiment runner that destroyed the panel's working tree on the way out, and 7 timestamps this assistant typed rather than read.

## Wolfram, enabled and queued

The founder's ruling, verbatim: *"So fully enable it. But we don't depend just on Wolfram ... Wolfram, although it should always be used wherever possible, should remain the secondary/verification source (a second falsifier), where our other relevant tools should also aways be used and should remain primary in all cases."* And, on agents: *"Agents are not exempt from using tools ... Every model and every agent should use tools wherever possible, including Wolfram."*

The default in force 6 hours earlier was the opposite: a gate that refused the kernel outright to every automated seat. Removing that gate was not sufficient, because the constraint that justified it is real. The free Wolfram Engine runs 1 kernel, and 3 concurrent calls measured on 2026-08-02 returned 1 result and 2 disconnections. Seats run at the same time by design, so an unqueued route hands 2 of every 3 seats a failure that reads like a mathematical answer.

What replaced the refusal is a queue. `bench/tools/wolfram_gate/serial/wolframscript` sits first on every seat's and every agent's PATH. It takes a machine-wide exclusive lock, runs the real binary 1 call at a time, passes the child's exit code through untouched, and appends either the attribution Wolfram's terms require or `[NOT EVIDENCE]` with the reason the call verified nothing. Every call is recorded to a log, so the route can be measured later rather than assumed.

Serialisation was measured through the real gate against the real Engine by `scripts/wolfram_serial_gate_probe_2026-09-17.py`: 2 calls started at the same moment, the second waited 5.1 seconds in the queue while the first held the kernel for 5.1 seconds, the 2 kernel windows were disjoint, both results classified as evidence, both carried the attribution, and both answers were correct. In the test suite the same property is held against a fake kernel, and removing the lock makes that test fail on overlapping intervals.

Wolfram is never a dependency. An absent kernel, a busy queue and a failed call each return a message naming SymPy, z3 and mpmath and saying plainly that this is not a blocker. The onboarding script says the same and keeps its 1-command install offer.

1 exception stands, and it is the founder's own condition rather than a preference of the assistant's: a stored falsifier may not call Wolfram. A falsifier is re-run by whoever reproduces the experiment, and *"anyone running the project, should not be required to install Wolfram to do so"* — a falsifier that calls the kernel writes exactly that requirement into the archive. The model that writes the falsifier may use Wolfram freely while reasoning.

### The defect found on the way

The onboarding script asks the kernel to evaluate `Print[1+1]` and required "2" to be the last line of the answer. The binary prints 2 and then the `Null` that `Print` returns, so a kernel that had just computed correctly was classified as having no kernel at all, and the script then offered to reconfigure a kernel path that was already right. The test fixtures replied `"2"`, a shape the binary never emits, so a producer and a consumer disagreed while each described itself consistently. The fixtures now carry the measured output and reverting the fix fails 4 tests.

## The project instructions, corrected

The founder approved both edits and asked that the file and the test asserting its wording change together, which they did. `.claude/CLAUDE.md` carried a tool prefix, `mcp__Wolfram__*`, that matches nothing: the connector's tools carry a per-installation identifier, which is why every connector call still raises a permission prompt. It also called the local Engine "the only WORKING Wolfram route today", which the connector's own successful result contradicts. The file now carries the enabling ruling verbatim, the serial gate and the policy that selects it, the 1 exception, and the licence reasoning that produced the earlier default — retained, because the ruling overrides the conclusion and not the facts, and because the letter to Wolfram is still unanswered.

## A fresh tree for every attempt, and nothing deleted

The ruling: *"Do it. And make sure this is how all future panel reviews and experiments (both paid and simulated) work in the future too. Take care when a panel review or an experiment completes however that the sandbox does not simply get automatically deleted and that the results do not end up simply being discarded, as has happened in the recent past."*

In round 17 a seat hit the 1,800-second cap and its retry reran in the same working copy the timed-out attempt had been editing for half an hour. 14 of the 19 files that seat left behind had no reply behind them, and its verdict on 1 entry was measured against its own unreported edits. A retry that inherits a half-finished tree is not a second attempt at the same task.

Every attempt now asks for its own working directory before it starts. The first attempt keeps the copy built before dispatch, so a round with no retry pays nothing extra; every later attempt gets a new copy of the canonical tree. The attempt number travels with the reply, on both the success and the failure path, and each attempt's tool log records the directory it ran in. The proposals file is keyed by seat and attempt, so every tree is read rather than only the one the seat ended in.

Nothing is deleted on the way out. Whole changed files are copied into the run's own log directory, not only their diffs, because a seat that writes a new script leaves an artefact whose value is the file itself. The copies are then kept, listed in a manifest, with the exact command to remove them printed for the operator. Deletion is opt-in and is refused outright when a harvest did not complete.

The founder's instruction covers every runner, not only this one, so the question was measured rather than assumed. `scripts/sandbox_deletion_audit_2026-09-17.py` parses every tree-removing call in the bench directory and classifies what it removes: 26 calls, of which 6 remove a tree a model worked in. 3 of those were destroying a seat's work with no harvest, including the simulated experiment runner, which is the path the founder named. All 3 now harvest first and keep the tree when a harvest fails. The audit reports 0 remaining.

That audit's first version missed the worst of the 3, because it classified by variable name and the simulated runner calls its worktree `_wt_parent`, which reads as scratch. It now asks whether the same function hands the path to a model.

## The instrument for CC1's own position

The ruling: *"If this is a missing test/instrument, then build it and implement it, and add it to the program of study for the next simulated run."*

The panel protocol has always said that CC1 participates with a position of its own and synthesises the range across the seats. Every other clause of that protocol had an instrument; this half had none.

`scripts/p5_cc1_position_2026-09-17.py` derives the range from the seats' own verdict tokens — the entries where 2 seats gave different verdicts — so the set is computed rather than asserted, and then reports which of those entries CC1 answered with a position of its own. It never scores a seat, because a model judging a model is what this project forbids.

Run against round 17 before anything was written, it found 9 entries carrying a verdict from both seats, 2 of them in disagreement, and no CC1 position at all. The record now carries that position: on A23, where the seats split FAILS against HOLDS, execution reproduces both defects and CC1's position is FAILS, with the note that the dissenting seat's reading was taken in a tree carrying its own unreported edits; on A22, where they split HOLDS against PARTIAL, the entry's own dated paragraph refutes the premise of the PARTIAL, so CC1's position is HOLDS. The disagreement is preserved rather than settled by weight of seats.

The instrument can say no: 3 of its 8 tests are negative controls, and a round where the seats never differ is reported as vacuous rather than as a pass, because 0 of 0 covered is not evidence that anything was synthesised. It is item 8 of the programme of study for the next simulated run.

## The 3 tests that failed outside a checkout

The founder: *"Surely you can't repair these (and the other 3 entries) and skip? That doesn't make any sense. Why not just repair?"* Repaired, and neither file carries a skip.

One asked git which test files the project tracks, and git exits with an error in a copy that has no repository — which every panel sandbox is. It now falls back to walking the tree, which answers the question that still has an answer there: which test files exist outside the collected root. In a real checkout git remains the authority.

The other 2 asserted that a script exits cleanly and prints its sections. Outside a checkout that script deliberately refuses to measure, because without git every path would count as untracked and the figure would read 100% by construction. The refusal is the script working, so the tests now assert the measurement inside a checkout and the refusal, by its stated reason and exit code, outside one. Measured in a copy with the repository directory removed: 14 passed, 0 failed, and the same 14 pass in the checkout.

## The Codex seat: measured, 1 question owed

The founder asked for the catalogue to be read before he rules. It was read with a public listing that needs no key and dispatches nothing, so the measurement cannot spend money. 445 models are listed.

Codex is separately available, as 5 distinct models. The newest, `openai/gpt-5.3-codex`, costs 1.75 dollars per 1,000,000 prompt tokens and 14.00 per 1,000,000 completion tokens, with a 400,000-token context. The cheapest, `openai/gpt-5.1-codex-mini`, costs 0.25 and 2.00.

The confound is confirmed from the catalogue and not only from the configuration: the Codex seat and the ChatGPT seat both point at `openai/gpt-5.5`, a real model at 5.00 and 30.00 per 1,000,000 tokens. 1 model wearing 2 labels is why the panel has 4 architectures and reports 5.

At round 17's own volumes — a 31,298-character brief and a mean reply of 17,983 characters, at 4 characters per token — 1 seat-round costs 0.1740 dollars on the shared model and 0.0766 on `openai/gpt-5.3-codex`, cross-checked with NumPy and mpmath agreeing to 1 part in 1,000,000,000,000. A distinct Codex seat costs 0.440 of what that seat costs today, so the diversity the founder wants is cheaper than the confound.

The question owed is narrow: point the Codex seat at `openai/gpt-5.3-codex` and leave the ChatGPT seat where it is? Nothing has been changed, because pointing a paid seat at a different model is the founder's call.

## The timestamps

7 timestamps written into the action list tonight were typed rather than read from the clock, including 1 that placed work in the following day. Each now carries the commit time of the work it describes, or the producing script's own recorded time. The rule this broke is the project's own: never type a timestamp, capture it.

## What is still owed by the founder

The verdicts on the drift detector and on the proposed V9 entry, both explained in chat; the ruling on the 3 paid dispatchers that read a brief and pay for seats without validating it, which stay registered and unused meanwhile; the narrow Codex seat question above; dropping the 2 stashes, which is a git reference deletion and reserved to him; the push, now 25 commits; task 10.2 on Tailscale's own SSH service; and the Zenodo token rotation, last, as ruled.

Written under CDSFL note standard v1.7 (26 August 2026).
