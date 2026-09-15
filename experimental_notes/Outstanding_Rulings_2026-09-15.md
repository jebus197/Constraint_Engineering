# The remaining rulings, listed in full

2026-09-15, 02:24 BST, Europe/London.

## Summary

The founder's replies to the 59-entry decision file were read in full on 2026-09-15. 3 replies were missed on a first pass because they carried no hash marker: a question asking what the 5 A11 rulings were, acceptance of the A8 recommendation, and a design ruling on A19. The earlier file named the 5 A11 rulings without ever listing them, which is why he had to ask. They are listed below, and each was checked against the repository on 2026-09-15 before being put to him. 1 of the 5 turned out to be settled already. 6 further questions follow that the earlier file never put to him. Items are numbered so he can reply by number, as before.

## What Has Been Recorded From His Replies

1. L1 and L2, the note linter: fix as necessary, through the panel.

2. R1, restarting experiment 53: deferred until after the next simulated run, and until the lessons from that run are applied.

3. R3, the discrimination control block: to be armed and tested live in the next experimental run.

4. Z1, the Zenodo token rotation: done after the work on this list is complete.

5. A19: build per-fragment classification if it is not already built, review it with Fable and CC2 against the simplest sufficient fix standard and the additive standard, and test it live in the next experimental run. A target that is only prose has nothing to compute, and a target mixing formulas with prose must not be rejected for containing prose.

6. The 59 entries stay on the list, and the panel plan for them is approved in full.

7. W1 is left for the founder to look at in the morning. The licence repaired on 2026-09-15 was the Wolfram Engine licence, task 0.1, which is separate from the Wolfram MCP server licence that W1 covers.

8. The next simulated run is HELD. Entry 60 of the reply file asked for it to start overnight, but the founder's chat message at 02:06, written after that file was saved at 01:41, holds it until his new work on the mathematical model has been reviewed. R1 and R3 wait with it.

## Answers To The Founder'S Questions

A7. What was the fix, are falsifiers part of the intended machinery, and do they need building?

Falsifiers are part of the intended machinery, and have been since 2026-06-03. The formal schema requires every seat to attach a runnable falsifier, a labelled block of Python, to each critical finding. The runner re-runs that block independently, and that re-run decides the verdict, not a vote. A critical finding with no falsifier receives the verdict UNTOOLABLE.

The 28 falsifiers written under task 2.2 were different. The assistant wrote them after the fact, as test files for specific archived findings, and they are not part of the runtime machinery. They showed that at least 2 findings marked UNTOOLABLE were testable after all, and both were real defects: 1 already fixed, and 1 still live and then fixed.

A7's own fix was an instrument rather than a falsifier. Its figures did not reproduce: the count is 22, not 25, and experiment 53 contributes none, because its 10 critical findings were never escalated. All 22 were escalated to a human by a named mechanism that records its reason: 11 because the routing ladder ran out, 8 on merge deadlock, and 3 on a stale contested challenge. There was no hole. The audit had counted only the first kind, so 11 of the 22 looked unexplained. Every escalation point in the runner is now checked by a test, and that check found a 7th escalation path on its first execution.

Nothing more needs building for archived runs, which cannot be retro-fitted. For future runs, task 2.1 repaired the intake parser, which had been missing 16.99 percent of labelled falsifiers. Whether seats now supply enough falsifiers can only be measured in a run, and that run is held.

A8. The problem in more detail.

The experiment log directory is excluded from git by design. It holds 446 megabytes in 7,345 files, and it exists on this machine only. Notes, code and tests cite 225 paths inside it, and 86 of those paths are not tracked: 38.2222 percent, with a Wilson interval of 32.1210 to 44.7189 percent and a Clopper-Pearson interval of 31.8438 to 44.9154 percent, both produced by the committed orphan-figures script on 2026-09-15. Of the 86, 37 are cited only by code, 15 only by tests as fixtures, and 8 are shorthand in prose rather than real paths. 26 are cited by a note: 11.5556 percent, Wilson 8.0089 to 16.3929 percent.

Those 26 are what a ruling is about. Anyone reading one of those notes in a fresh clone of the repository cannot open the evidence it cites. The earlier file overstated the cost of tracking them by describing it as 446 megabytes. Only the note-cited files would need tracking. A commit on 2026-09-11 measured that set at 20 files and 1.63 megabytes, but that figure has not been re-measured since and does not match the 26 counted on 2026-09-15.

## The 5 A11 Rulings, Each Checked On 2026-09-15

RULING 1. I16, finding C0050, severity 0.9. It claims that the memory module in the decision-making package took 6 different contents within about 4 minutes during a review round. Its subject is a series of file hashes that the run recorded, not the code under review, and the harness only runs falsifiers against the code under review. So C0050 cannot be tested as things stand, and it is still unresolved. The choice: build a second kind of falsifier target that can test a recorded series of file hashes, or withdraw C0050 as a claim about how the review round edited a file rather than about the code. Recommendation: withdraw it and record why, because task 6.6 now records candidate writers for every future rewrite, which covers what C0050 was reaching for going forward.

RULING 2. I18, 2 leftover git stashes. The older one, from 2026-09-02, holds a mutation-test change marked MUTANT M9. It deletes the guard that stops the post-convergence sweep re-clearing a finding another model has already cleared. That guard is intact in the runner today. The newer one, from 2026-09-11, was recorded nowhere until now. It holds early drafts of the 2 source-text audit scripts, both of which are committed in later, longer versions, so nothing in it would be lost. The hazard is that applying the older stash would silently disable a live guard. Dropping a stash deletes a git ref, which is one of the 3 actions the founder reserves to himself in person. The choice: drop both, by running the 2 commands given in the markdown copy of this file, or keep them and add a guard that refuses to apply any stash carrying a MUTANT marker. Recommendation: drop both.

RULING 3. I23, the exhausted-round valve in experiment 56. The runner's default threshold is 8 stalled rounds, and all 3 experiment 56 configurations set a maximum of 8 rounds without overriding that threshold. A finding can never stall for 8 rounds inside an 8-round run, so the valve never opens. cc2 proposed a threshold of 6. The configurations are frozen pre-registration files, so any change is a pre-registration change. The choice: set 6 in the 3 configurations, or accept a valve that never opens. Recommendation: defer this with the held run and settle it when the run is re-planned under the revised mathematical model.

RULING 4. I28, attributing file rewrites. ALREADY SETTLED, NO RULING NEEDED. Task 6.6, completed on 2026-09-10, built exactly the option this ruling offered. Each rewrite now records the seats in flight, the file's own status record and the thread that noticed it, labelled as candidates and never as attribution. Naming the writing process outright would need root access through the file system usage tool or dtrace, which means the founder's password. Nothing is proposed unless he wants that.

RULING 5. I31, the drift detector. The update drift detector is a two-sided cumulative-sum check in the memory module of the decision-making package, and it has 0 production callers, so it has never run. Task 6.7 assessed its guard and closed, but the choice this ruling asks was never made. Replayed over 3 recording runs, its largest excursion was 0.5595 against a threshold of 2.0. Under the additive standard, an addition nothing reaches is not additive. The choice: wire it into production, which makes its threshold live and testable, or retire it with an explicit retired entry. Recommendation: decide this together with the revised mathematical model, because the detector compares observed confirmation rates against the memory model's prediction, and the revision may change that prediction.

## Further Questions The Earlier File Never Put To The Founder

QUESTION 6. The 4 composer defects parked from task 2.2. They were parked because fixing them changes the text sent to models and breaks replay of earlier runs. The largest, C0040 at severity 0.88, is confirmed: the full universal directive of 27,803 characters is always replaced by a minimal rendering of roughly 2,500 characters. The others are C0037; C0036 with C0054, where the conflict detector misses 95.6120 percent of directives; and C0001, where the coherence pruner makes its own metric worse. The founder expects the CDSFL system prompt to be refactored for the revised mathematical model. The choice: fix these 4 now, or fold them into that refactor. Recommendation: fold them into the refactor, because both change the text sent to models, and doing it twice would pay the replay cost twice.

QUESTION 7. The audit of done entries. 30 of 84 done entries claim more than their evidence shows: 35.7143 percent, with a Wilson interval of 26.2994 to 46.3787 percent, recorded with its evidence on 2026-09-11. That evening a reply choosing to fix only the misleading ones was typed but never sent. Does the approved panel plan cover closing these 30, or only the 51 lettered entries? The options: close all 30 through the panel, close only the misleading ones, or record them and stop.

QUESTION 8. Task 10.2, SSH over the private network. This is the 1 entry on the founder's own list that is blocked on him. With Tailscale switched off, SSH over Tailscale, the workaround for the desktop app restarting while he is away, is no longer available. The choice: enable Tailscale's own SSH service, go back to the earlier SSH route, or leave remote access until it is needed.

QUESTION 9. Panel review under the current mathematical model. The approved brief requires seats to use the mathematical model as an instrument, and the founder regards the current model as superseded by his revision. For most of the 51 entries, which are harness engineering, the model has no bearing. A19 is different, because the admissibility gate is part of the model. Proposal: dispatch the engineering entries now, and hold A19 until the new material has been reviewed.

QUESTION 10. A8, confirming the ruling. At Decision 1 the founder accepted the recommendation to accept and label; at item 32 he asked for more detail before ruling. That detail is above. The one fact it changes is the cost: tracking would not mean 446 megabytes, only the files that notes cite. Does accept and label stand, or should the note-cited files be tracked?

QUESTION 11. Onboarding. His direction has been received. Proposed: check every third-party tool in the Tool Constraint Box, adding the ones not checked today, which are biopython, astropy, crosshair, matplotlib, networkx, pandas, pint, PuLP, rdkit and scikit-learn; install the Wolfram Engine through Homebrew, launch its activation, set its kernel path and prove the kernel computes, rather than only checking that the command exists; correct the stale text that still describes the Wolfram hosted route as live and still lists the retired Wolfram Alpha API client; and on systems without Homebrew, print copy-and-paste instructions with download links. The choice: approve, amend or reject.

## Commands and file references

**Ruling 2, dropping both stashes** (the founder runs these himself; dropping the older one first keeps the newer at index 0):

```bash
git stash drop 'stash@{1}' && git stash drop 'stash@{0}'
```

- The mutant stash patch removes `cid in _handled` from the sweep guard; the guard is intact at `bench/reference_runner_v3.py:6296`.
- The newer stash's drafts: `scripts/source_text_assertions_2026-09-11.py` and `scripts/source_text_fragility_2026-09-11.py`, both committed, and used by `bench/tests/test_source_text_and_neighbour_audit_2026-09-11.py`.
- Ruling 3: `exhausted_round_threshold: int = 8` at `bench/reference_runner_v3.py:1335`; `"max_rounds": 8` in each of `bench/exp56_configs/d9_multi_model_panel.json`, `d9_single_model_with_agents.json` and `d11_seat_contrast_diversity_arm.json`.
- Ruling 5: `update_drift` is defined at `bench/dm/_memory.py:314`; an AST scan of `bench/` outside the tests finds 0 call sites.
- A8 figures: `python3 scripts/orphan_figures_2026-09-10.py`. A7 figures: `scripts/escalation_paths_2026-09-11.py`, guarded by `bench/tests/test_escalation_paths_2026-09-11.py`.
- Ruling 1 and Ruling 4 source: `experimental_notes/ISSUES_LOG_2026-09-09.md`; task 6.6 evidence: `bench/tests/test_target_rewrites_carry_an_author_2026-09-10.py`.

Written under CDSFL note standard v1.7 (26 August 2026).
