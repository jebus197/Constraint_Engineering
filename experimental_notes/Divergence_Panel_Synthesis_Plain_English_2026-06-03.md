# What the panel said, and the way forward — plain English

2026-06-03 05:20 BST. Constraint Engineering / CDSFL. A six-model panel reviewed the completed analysis of where the project drifted, and was deliberately asked to *break* it, not agree with it. This is the plain-English summary.

## The headline

All six models reached the same verdict: the diagnosis is **sound, with caveats.** And — without being forced or even encouraged to agree — they independently arrived at the *same* picture of how to fix it. That fact is itself quietly reassuring: when the question is well-posed and checkable, genuinely different models converge on their own. They do not need to be herded into a consensus. Which is the whole point.

## Three ways the panel sharpened the diagnosis

**First, a more precise name for the disease.** The earlier analysis said the system "decided truth by discussion instead of by tools." The panel sharpened this: the system never really *chose* to vote. It allowed the models to make claims in plain English that no tool could check — and once a claim cannot be checked, the only thing left is for the models to argue about it. So the real fix is stronger and simpler than "stop voting." It is: **no claim is allowed to exist unless it arrives with the check that would prove it wrong.** A finding must carry its own test. Then there is nothing left to vote about — the test decides. This is the missing piece of the calculator.

**Second, an honest limit.** Not everything can be checked by a tool. The simple risk number the system already verifies is easy to recompute. But a real finding like "this approach is fragile" or "this won't generalise" may have no mechanical test at all. So the rule is: tools decide everything they can, and the genuinely undecidable handful go to the human — which is exactly what the founding documents always said. The honest goal is to make that handful *small*, not to pretend it is empty.

**Third, the cleanest reconciliation of the whole tension.** One model put it perfectly: disagreement between models is valuable for *deciding what to look at*, but not for *deciding what is true*. The models' differing views are a search party fanning out to cover more ground — that is worth keeping. But once they have each found something, a tool, not a show of hands, decides whether it is real. So the system keeps the creative disagreement and removes only the voting on truth. Those were always two different things that got tangled together.

## How to build the big version — the part you actually asked about

On the question of scale — how to throw five, or five hundred, models at a hard problem like the Riemann Hypothesis and get one coherent answer — the panel and I converged on a single shape, and it mirrors how the volunteer-computing projects you mentioned already work.

You do not hand "solve the Riemann Hypothesis" to five hundred models. You break the problem into a web of small, *checkable* pieces — each piece a specific claim with a clear way to test it, and clear links to the pieces it depends on. Each piece gets a small panel of a few different models that reason about it and try to break it, and then a tool checks it. The pieces combine along their dependencies into the whole, with the risk of each piece adding up the chain; the overall problem is "solved" when the top claim's remaining risk is low enough and every critical piece has been settled by a tool. This is exactly how the project that checked a trillion Riemann zeros worked — independent ranges, each verified by recomputation, with the property that a single bad zero would have disproved the whole conjecture. The new ingredient is that the workers here *reason*, so the pieces can have dependencies and can spawn smaller pieces — which is the genuinely new and non-trivial engineering.

And when several models produce several different *valid* answers? You do not vote. You rank them by hard criteria in order: which passes the most checks, then which carries the least residual risk, then which covers more, then which is simplest. Only a true tie on all of those goes to you. That directly answers the thing that has been bothering you — five models, five answers — without a popularity contest.

## What carries over, and what does not

The core ideas all survive and transfer to any field: falsification, the risk model, "finished means the search is genuinely exhausted," the sealed permanent record, and the human as final authority. What is specific to code review and should *not* be carried over blindly is the particular set of code tools and, above all, the habit of pointing the whole panel at one artifact. The future is decompose, distribute, recombine.

## What to do next

1. Make the rule real: a serious finding must arrive with its own test, or be sent to you. The tool runs the test; the test decides. (This is the concrete restart of the verifier work, now with a clear specification.)
2. Separate the search from the verdict: keep the models disagreeing about *what* to check; let tools decide *whether* it holds. Retire forced agreement.
3. Tell the models they are building and solving a thing, not hunting bugs forever.
4. Build the "web of checkable pieces" engine on a small problem first, prove it finishes by tools and not votes, then grow the number of pieces.

## Honest about what is still open

The engine that breaks a problem into pieces and reassembles them does not exist yet — the panel agrees on its shape, but building it is the real next job. Some findings will always need your judgement; the claim is that there are few of them. And whether the whole thing genuinely works across science, not just code, is still unproven until the frontier-problem run tests it.

The short version: you were right on the substance, the panel confirmed it, the contradiction was never real, and the missing piece of the calculator now has a name — every claim must carry its own test.

Written under CDSFL note standard v1.2 (14 May 2026).
