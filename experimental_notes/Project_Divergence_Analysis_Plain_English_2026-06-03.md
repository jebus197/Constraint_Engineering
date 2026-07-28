# Where the project drifted from its founding idea — plain English

2026-06-03 02:50 BST. Constraint Engineering / CDSFL. A first solo analysis, to be put to the model panel afterwards to try to break it.

## The short version

There are two separate problems, and they are not the same kind of thing. One was there from the very beginning, written into the founding paper itself: the dream of "thousands of models working together, faster and better" describes a *different machine* than the one the paper actually describes and the one that got built. The other is a genuine wrong turn in the building: the system quietly started deciding what is true by having the models *vote*, which is the exact thing the founding documents say it must never do. The good news underneath the hard news: the founder's gut feeling that "design by committee" is wrong is not a new idea at all. It is the project's own founding rule, and the founding maths even warns that committee-style agreement destroys the whole benefit. The vision was never lost in the theory. It got buried in the building.

## What the project was originally meant to be

Three statements from the founding documents anchor everything.

First, the paper's own model of "what happens as you add more models" says plainly that the best number of models is *small* — three to six — and that adding more brings rapidly shrinking returns. It also warns that if the way you coordinate the models pushes them toward agreeing with each other, you lose the benefit entirely, and a crowd of models collapses back to being no better than one.

Second, the README states the rule for how the system decides what is true, in a single sentence: it does *not* rely on the models agreeing. It relies on tools, and when the tools cannot decide, on the human.

Third, the value was always supposed to come from *disagreement* between *different* kinds of model — disagreement treated as useful information, not as noise to be smoothed away.

So the original idea was: a small panel of genuinely different models, whose worth is catching things a single model would miss, where *tools* settle what is true and the human steps in only when the tools genuinely cannot. Shrinking returns from extra models were *expected*. Forcing the models to agree was named as the thing that ruins it.

## The first problem: two different dreams got mixed together

The current frustration — "five should beat one, a thousand should beat five, more compute should mean faster, or something is broken" — is describing a *different machine* than the one that exists.

There are two separate ideas hiding inside one phrase. The first is many different models *reviewing the same problem* to catch more mistakes. That is what the paper describes and what got built, and its own maths says it tops out at a handful of models and then barely improves — and gets slower, not faster. By that model, a thousand models all reviewing the same thing being no better than five is not a fault. It is exactly what the maths predicts.

The second idea is *splitting a hard problem into many pieces*, having many models each solve a piece, and combining the answers. *That* genuinely gets faster and better as you add compute. *That* is the real "Global Mind." But the paper never described it and the system never built it. It was the dream sitting behind the project, never actually designed.

So the computer-science instinct that "more compute should help" is correct — but only for problems you can *split up*, not for many models redundantly checking the same thing. The built system is the second kind. The dream is the first kind. They were never the same machine, and that mismatch has been there since the founding paper. That is why no single experiment ever "broke" it: there was nothing to break. It was a mix-up, not a malfunction. This is also the part I most want the panel to attack, because the paper's "small is best" result is about *reviewing*, and may simply be silent about the *splitting* case rather than ruling it out.

## The second problem: the building betrayed the rule

Within the machine that was built, the construction drifted away from its own rules — which is exactly the bug we hit this week.

The founding rule says tools decide, not agreement. But in practice the system was caught deciding findings by the models *voting* on each other — a committee — because the tool that was supposed to check the claims kept failing to reach a verdict. The committee was never chosen on purpose. It is what the system *falls back to* when its checking tools cannot ground a claim. And that is a direct breach of the one sentence that defines how the system is supposed to decide truth.

On top of that, the founding maths warns that pushing models to agree collapses the crowd back toward a single voice. Over time the system accumulated machinery that *forces* agreement — voting, reconciliation, compelled convergence. Forcing agreement is the precise thing the maths says destroys the benefit of having many models. So the observed feeling that five models are barely better than one is not a mystery. It is the predicted collapse, caused by coordinating the models toward agreement instead of preserving their disagreement.

And the way it happened matches the founder's own description exactly: a slow accumulation through constant local problem-solving, each new piece sensible on its own, while the whole drifted away from the founding idea, with no step ever stopping to check the whole against the original goal. The minutiae trap, made concrete.

## The Global Mind is still possible — but it is a different machine

The "split a problem across many models" dream is achievable and worth building. It rests on the two things this analysis points to. First, claims settled by tools, not by discussion — so an extra model adds checking power rather than another voice everyone has to listen to. Second, splitting the problem into different pieces, not repeating the same review — so an extra model does new work rather than the same work again. Build those two, and "more models, faster and better" finally becomes true, because the system is then doing distributed *computing*, not distributed *arguing*.

## What to do

First, make the built system obey its own rule again: tools decide. Critical findings should arrive with a runnable check attached, the system runs that check, and the voting committee is removed. This is immediate and it is exactly what the founding documents already say.

Second, stop forcing the models to agree. Re-examine compelled convergence and the voting machinery against the founding warning. Anything that pushes the models toward agreement is throwing away the very thing that makes a panel worth more than one model.

Third, only then design the "split the problem" machine deliberately — the real Global Mind — built on top of a core that settles claims with tools, rather than bolted onto the review system.

## Where this stands

This is a first solo reading, grounded in the founding documents. The next steps are to trace exactly *when* the voting machinery crept in, and to hand this whole argument to the model panel and ask them to *break* it, not to agree with it. Nothing has been changed in the code on the basis of this analysis yet.

Written under CDSFL note standard v1.2 (14 May 2026).
