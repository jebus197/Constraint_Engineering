# The Remaining Experiments — Where They Came From, and a Concrete Road Map

**2026-07-22, 01:03 BST.**

## The question, and the verdict

The founder asked a pointed question: was the second half of the experimental programme (experiments 44 through 54 in the original numbering) ever actually agreed, or have the models been waving the founder past it, implying the details would be settled later? A forensic audit of the planning documents, the panel-review records, the decision register, and the full git history gives a clear answer: **the founder's recollection is correct.** The tail of the programme was drafted in concrete detail, but it was never ratified by the founder. And the audit surfaced something more consequential: a whole layer of machinery that the tail was designed to validate turns out not to be connected to the live system at all.

## How the programme actually came to be

The fifteen-experiment structure was not designed from first principles. Experiment 39, an earlier effort, had been organised as fourteen sub-experiments in a configuration file. In mid-April 2026 that list was promoted, one entry per experiment, into the arc numbered 40 through 53, with experiment 54 added as a final integration study. The 17 April plan that did this left most of the later targets marked "to determine."

Four days later, a consolidated plan filled in the blanks — but the filling-in was done by a five-model AI panel, closed under a discussion discipline called compelled convergence, in which each model had to yield to an existing position or refute one, with no new alternatives admitted. The founder later identified compelled convergence as a methodological mistake, "a hack to force agreement," and retired it. So the apparent solidity of the tail ("five out of five models converged") rests on a mechanism the project itself has since repudiated.

Crucially, the plan's own design never claimed founder approval of the tail. It scheduled a founder sign-off gate after each experiment, and it kept a register of five decisions explicitly reserved for the founder, each due "at a concrete later trigger" — the entry to each future experiment. In other words, the hand-waving the founder remembers was structural: the plan literally said, cross each bridge when you come to it. The git record confirms no founder ratification of the tail exists anywhere. The founder's genuine rulings were about the framing and the count (April), a demand in June to review "what experiments 40 through 54 actually entail" before further runs, and the July restructuring that dropped two redundant experiments and renumbered the rest.

## The new finding: the specialist layer is not connected

The tail experiments were organised around domain specialists — a statistics specialist, a biology specialist, a physics specialist, and so on — each meant to route claims in its field to the appropriate verification tools. The audit checked whether that specialist machinery is actually in the live experiment runner. It is not. The configuration files for the specialists exist, but the live runner never reads them, and no live code activates specialist dispatch. The specialist layer was built in April in shadow form against an older orchestrator and was never carried into the runner that has executed every experiment since.

This means the tail's stated success criteria, such as "statistics specialist verdict count greater than zero," cannot be met as written, because there is no specialist to produce a verdict. What the experiments genuinely test — and have tested, successfully, through experiment 43 — is the five-model review panel, the runnable-falsifier gate ("tools decide, not votes"), and the convergence machinery, applied to one real module at a time. That machinery is real and proven. The specialist storyline was aspiration layered on top, and it quietly stopped being true when the project moved to the new runner.

One consequence deserves emphasis. The plan called for four purpose-written test modules — one each for biology, physics, chemistry, and engineering — kept separate so that each domain's specialist could be validated in isolation. With no specialists in the loop, the reason for four separate modules disappears. What survives is the modules' other, genuinely valuable property: they were to be written with deliberately planted false claims, so the system's ability to catch known errors could be measured directly. That is the only place in the whole programme where detection can be scored against a known answer key, and it works through the ordinary panel-and-falsifier path, no specialists required.

## Are the remaining experiments getting dramatically smaller?

No — not in target size. The remaining real modules run 10.7 thousand, 23 thousand, 29 thousand, and 39 thousand characters; experiment 43's target was 22 thousand. The four synthetic modules were specified at 15 to 25 thousand characters each, and none has ever been drafted. What genuinely shrinks is the effort per experiment: the machinery is proven, the configurations are templated, and the faults surfacing per experiment have been falling. Cost per run is roughly flat, about 12 to 40 dollars depending mostly on how many rounds convergence takes.

## The remaining experiments, plainly

Using the founder's July renumbering:

1. Experiment 44, then 45: two dormant but meaningful modules — the statistical cross-experiment memory (10.7 thousand characters), and the evidence layer (23 thousand characters), which is the query-and-provenance interface over the project's cryptographic accountability chain. The recommendation is to run the evidence layer first: it matches the size class where the old convergence fault actually appeared, so a clean convergence there is strong proof the newly designed fixes work, whereas the small memory module might converge easily and prove little.

2. Experiment 46: the literature-calibration module (29 thousand characters), which genuinely runs in shadow inside every experiment, observing each round and logging calibration data. Its original success criterion is one of the few in the tail that remains executable as written.

3. Experiment 47: the divergence module (39 thousand characters), fully live machinery used every round. The largest remaining target, best run after the fixes have been proven on the smaller ones. Defects found here pay immediate dividends, because this code runs in every subsequent experiment.

4. One consolidated synthetic STEM module (recommended, replacing the planned four): purpose-written scientific content of about 20 to 25 thousand characters carrying the strongest claim clusters from all four domains — sequence claims, unit and dimension claims, statistical claims, kinematics, stoichiometry, load factors — including every class of deliberately planted false claim. This preserves the answer-key measurement and the bridge toward real scientific content, at a quarter of the cost.

5. The final factorial experiment: the one piece of genuine experimental design in the tail. It runs the system four times on the same target — with the feedback directive on or off, crossed with the divergence directive on or off — and attributes the improvement causally to each directive. This is what turns the programme from a series of demonstrations into an experiment. The April plan never settled its target; the recommendation is a second fresh synthetic module, which also cleanly resolves an old unresolved dispute about how to run the baseline condition.

## The recommended road map, and what it buys

Implement the five convergence fixes (session work, no API cost). Then six runs: evidence layer, statistical memory, calibrator, divergence module, one synthetic STEM module, and the four-cell factorial. Estimated remaining cost: roughly 150 to 240 dollars, against the earlier projection of 300 to 450. The specialist layer and its planned activations are retired from this arc openly, not dropped silently; whether to wire them becomes a decision for Bench Run 2 preparation, if and when that proceeds.

Completing the arc delivers: the convergence machinery demonstrated across five further independent real modules; a measured detection score against planted errors in genuine scientific content; causal evidence for whether the two governing directives actually produce the improvement; and the system's own live machinery reviewed by the system itself. That is a complete, defensible proof-of-concept dossier — the foundation for Bench Run 2, the paper, and any outreach. What it does not deliver: large-scale third-party scientific content (that is Bench Run 2's job), and validated domain specialists.

Nothing here has been implemented. The renumbering, the compression of the synthetic tier, and the factorial target proposal are decisions reserved for the founder.

---

*Written under CDSFL note standard v1.2 (14 May 2026).*
