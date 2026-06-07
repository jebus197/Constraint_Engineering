# Letting the Strong Models Take Up the Slack (Plain English)

**2026-06-07 15:31 BST**

## The idea

When a model finds a real bug but writes a broken test to demonstrate it, two bad responses are tempting: keep nagging that same weak model to fix its test, or give up and hand it to a human. A better response is to give the weak model a fair shot, and when it plainly can't, let a stronger model take over the test-writing. Strong models adjudicate; weak models just find. That is the whole idea, and the encouraging part is that the machinery for it was already built into the system — it had just been switched off.

## The machinery was already there, dormant

The system has long carried a per-model "capability fingerprint" that ranks the models — and it already places the strongest model top and the weakest bottom, matching exactly what the run data shows. It also has a load-balancer and a manager component meant to assign work by capability. But somewhere along the way these were bypassed: every round simply fired all five models in parallel and treated them identically. Restoring capability-aware routing for the test-writing task is not a new bolt-on; it is reconnecting something that was already designed and built.

## Who the weak link is

The data is blunt. One model, DeepSeek, accounts for ten of the fifteen stuck findings and five of the seven hardest, with a test-confirmation rate of 28%. The two strongest writers left zero stuck findings between them. So the weak link is clear and singular, and the strong writers are demonstrably reliable.

## What was tested before building

Three things, deliberately, before writing any production code.

First, the founder's own suggestion — teach the weak model by showing it worked corrections of its own mistakes, then demand it check its work. Tested honestly: it lifted the weak model from zero to one-in-three on fresh findings. So teaching helps a little, but it does not cure — the model stays unreliable, and the lesson evaporates on the next call because these models don't learn between invocations. The salvageable part of the idea is different and worth keeping: having the original finder confirm that the strong model's test really tests what it meant is a good cross-check against quietly testing the wrong thing.

Second, the actual mechanism — hand each of the seven hardest stuck findings to a strong model that can read the code and run and fix its own test as it goes. The weak models had scored zero on these. The strong model scored six out of seven.

Third, the one it missed. That finding is about code that mangles formatted code blocks, so the test has to embed a code block as text — and the strong model kept tangling its own quotation marks, breaking its test the same way twice. The very strongest writer handles it. So a two-rung ladder — strong model, then strongest model — clears all seven.

## What was built

A small, self-contained, fully unit-tested module. For each stuck critical finding it: checks whether the same defect is already confirmed elsewhere (if so, it was never a real escalation); otherwise routes the test-writing up a ladder of progressively stronger models, skipping the weak model that already failed, until one of them produces a test the runner's own checker confirms; and only escalates to a human if even the strongest can't. The runner's checker always decides the verdict — never the model's say-so. Ten unit tests pass.

## Where it stands

The mechanism is validated and the module is built and tested. Wiring it into the live round loop is the next step, and it was deliberately left for a fresh start rather than rushed at the end of a long session, because that part touches the core of the runner and a careless change there is exactly the kind of avoidable bug worth not introducing. After that comes the real test: re-run the experiment with this turned on and see whether it converges with no findings left for a human to rule on. The broader move it points to — keep the weak model as a finder, never as a falsifier — is the capability-aware load-balancing the project was built around in the first place.

---
*Written under CDSFL note standard v1.2 (14 May 2026). Technical: `Capability_Aware_Falsifier_Routing_2026-06-07.md`. TTS: `~/Desktop/CDSFL_tts/Capability_Aware_Falsifier_Routing_2026-06-07.txt`.*
