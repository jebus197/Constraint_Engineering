# Experiment 44 Launch, the Fix Tranche, and the Specialist Promotion

**Preserved into the repository 2026-08-06 02:15 .** Exp 44 launch and the fix tranche going live. Provenance for the first zero-residue convergence.

**Provenance.** This is the plain-text text-to-speech document from `~/Desktop/CDSFL_tts/Exp44_Launch_and_Fix_Tranche_2026-07-27.txt`,
preserved VERBATIM below rather than rewritten. It is a record, and rewriting a record is a fault in
this project. It was cited by name in `RECOVERY.md`
while existing on one machine's Desktop only — and `resources/RECOVERY.md` opens by promising a reader
can rebuild everything from the repository alone. That promise now holds for this document.

---

Experiment 44 Launch, the Fix Tranche, and the Specialist Promotion

2026-07-27, 01:27 BST.


Summary

Experiment 44 launched at 01:27 BST on 27 July 2026, targeting the evidence layer module, the query and provenance interface over the project's cryptographic accountability chain. It is the first run under the five convergence fixes designed after Experiment 43, and the discriminating test of whether those fixes produce clean convergence. Before launch, the fixes were implemented in the runner, attacked by an adversarial verification pass that found and repaired four real defects in the first implementation, and pinned by a fresh regression suite. Separately, on the founder's standing instruction, all specialist B cell types are now live from this experiment onwards.


The Five Fixes, Now In The Runner

Fix one. The convergence gate no longer counts an un-demonstrated sub-critical finding as contested. In Experiment 43, two low-severity items, one with a broken test and one with no test at all, held veto power over convergence for eight rounds. Such items now go to an explicit, logged residual queue for human review instead of blocking the gate. Genuine model disagreement still blocks, at any severity.

Fix two. A finding whose test errored is now routed once to a stronger model for a corrected test, whatever its severity, instead of sitting in limbo.

Fix three. The finding parser no longer accepts a round review summary as if it were a new finding, which is exactly how one of the two blockers entered the registry.

Fix four. The patience threshold for ageing out contested items is lowered from five rounds to three in the experiment configuration, since five rounds of paid computation to clear a trivial item was waste.

Fix five. The panel directive now makes clearing residual findings an explicit duty. A model must either supply a working test for its own unconfirmed finding or explicitly withdraw it.


The Adversarial Pass Caught Four Real Defects

In keeping with the project's method, the new fixes were themselves attacked by four independent adversarial reviewers before being trusted. They found four genuine faults in the first implementation, each then repaired and pinned by a test.

First, the launcher path silently dropped the new patience setting, the same class of silent divergence between the two launch paths that was caught before Experiment 43. Second, the new exclusion rule could silence a finding that models were genuinely still disputing. It now never excludes an item carrying an unresolved challenge, and the exclusion only operates at all when the falsifier gate is on, so historical baselines replay unchanged. Third, an outage that prevented any model from being reached would have permanently burned a finding's single routing attempt. The attempt is now only consumed when a model actually responded. Fourth, the parser hardening would have discarded a genuine, historically confirmed high-severity finding that quoted registry identifiers inside code. The check now ignores quoted code and comments.

The tally: one launch-path gap, one silencing risk, one wasted-attempt path, one lost-finding path, all found before a single dollar was spent on the run. This is the falsification discipline applied to the project's own repairs.


All Specialists Now Live

On the founder's repeated instruction, the physics, chemistry, and engineering specialists were promoted from shadow to live, joining mathematics, statistics, biology, information science, and software. All eight specialist domains now run live from Experiment 44 onwards. A live test confirmed the physics specialist engages its symbolic mathematics, logic, and astronomy tools when given a physics claim. The promotion has no effect on Experiment 44 itself, which runs the software domain for instrument comparability, and becomes meaningful for the synthetic science modules and Bench Run 2. An audit of all remaining shadow code is the committed next step after this run.


What Experiment 44 Tests

The run reviews the evidence layer, about 23 thousand characters, under exactly the instrument that produced the Experiment 42 landmark and the Experiment 43 generalisation, with the five fixes as the only declared changes. The prediction, registered before launch: clean convergence within the round budget, expected around rounds six to eight, with no sub-critical item blocking the gate and the residual queue explicitly logged. If it does not converge, the cause is assumed mechanical and will be diagnosed under live monitoring. Estimated cost is fifteen to twenty five dollars. A clean result is the founder's decision point on funding the remainder of the arc.

The run is under continuous monitoring, with a live terminal window open showing the full output.


Written under CDSFL note standard v1.2 (14 May 2026).
