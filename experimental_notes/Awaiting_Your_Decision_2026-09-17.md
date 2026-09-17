# What is left, and all of it waits on the founder

2026-09-17, 21:17 BST, Europe/London.

## Summary

Items 1 to 10 of `experimental_notes/Action_List_2026-09-17.md` are done, each with its evidence recorded in the list. The full suite is green under `--netguard-strict` at `def8eae`: 7,936 passed, 5 skipped, 1 xfailed, 0 failed, exit code 0, 2526.06 s. Nothing on the assistant's side is waiting on work.

What remains is 4 actions only the founder can take, 8 verdicts owed, and 6 decisions that surfaced during today's work. The 5th, the Wolfram licence renewal, was automated after this note was first written and is recorded as done below. Every one has a conservative default already in force, so none of them blocks progress; they are listed so that a default is chosen rather than inherited by silence.

## 1. Actions only the founder can take

**A1. Drop the 2 stashes (task I18).** Deleting a git ref is 1 of the 3 actions reserved to the founder in person. `git stash list` shows `stash@{0}` on `6c6d053` and `stash@{1}` on `164d2b3`. The guard the stashed mutant would have removed is verified intact either way.

```
git stash drop 'stash@{1}' && git stash drop 'stash@{0}'
```

**A2. Push, or run `sv`.** 17 commits sit unpushed, `0812897` through `3f391f4`.

**A3. DONE 2026-09-17 21:34 BST, and it needed no decision after all.** The founder's instruction that it needs no credentials was correct and the project's record was wrong: `wolframscript -activate` with stdin closed returns exit 0 and "Wolfram Engine activated", prompting for nothing. `scripts/wolfram_licence_renew_2026-09-17.py` runs under the LaunchAgent `com.cdsfl.wolfram-licence-renew` at login and twice a day, so a lapse repairs itself. Nothing is owed on 2026-10-08.

**A4. Decide how to stop Wolfram connector permission prompts.** The project rule `mcp__Wolfram__*` does not match the connector's tool names. Either choose "always allow" at the next prompt, or reply `y` and the assistant adds the connector's identifier to `permissions.allow` in `.claude/settings.json`.

**A5. The Wolfram licence email (task W1).** W1 stays BLOCKED until Wolfram answers in writing whether the connector's use and the local agent-tools server are permitted. A draft follow-up is in the instructions note. Only the founder can send it, or record a reply that has already arrived.

**A6. Task 10.2, Tailscale's own SSH service.** Still the founder's call, unchanged.

**A7. Z1, the Zenodo token rotation.** Last, as ruled. Credentials are the founder's to handle and the assistant never enters them.

## 2. The 8 verdicts owed, each with its default and 1 recommendation

**(a) R10 and R11: hold with A19, or send to the panel.** Both bear on the mathematical model: R11 answers ruling 4.3 with `gamma_input`, and R10 is the reading behind the references selection. Default in force: held. **Recommendation: keep them held until the revised model is reviewed**, with A19.

**(b) I31: keep the report-only call, or revert it.** The wiring commit's stated premise is false, recorded on task A11 and beside the call site: `π_mem` is defined in appendix section 1.5 with the CUSUM statistics and the 2.0 threshold, so the detector does depend on the current model and the founder's condition for deferring was met. It also cannot fire where it sits: production makes 1 update per run, `save` keeps no CUSUM state, and z3, confirmed by `Reduce` on the local Wolfram Engine, finds fewer than 3 same-direction updates cannot cross 2.0. **Recommendation: leave the call in place, because it decides nothing and cannot fire, and fold the detector's design into the review of the revised model.**

**(c) Arm C of the next simulated run, marked launch-blocked.** `bench/exp56_configs/d11_seat_contrast_diversity_arm.json` carries `_arm.launch_blocked: true`, and the stated reason is the Codex seat's paid route. In a simulated run both its seats are the same stand-in, so the run is the weak form by construction. **Recommendation: rule that the simulated run includes this arm, and record the ruling in that config's note.**

**(d) Wolfram in panel reviews: denied, or a single-kernel queue.** Denial is the default now in force and is enforced in code. The seats run concurrently against 1 licensed kernel, and 3 concurrent calls measured on 2026-08-02 gave 1 result and 2 disconnections. **Recommendation: keep it denied until Wolfram answers A5.**

**(e) Whether a workflow-spawned agent calling Wolfram counts as the assistant's interactive use or as automated use.** Today's 5 agents made 0 Wolfram calls. **Recommendation: classify a dispatched or workflow-spawned agent as automated, so the licence constraint applies to it, and keep Wolfram for the main session only.**

**(f) Whether the Wolfram connector is named in the project instructions as a working route.** `.claude/CLAUDE.md` still names a tool prefix that no longer exists and calls the local Engine "the only WORKING Wolfram route today", which the connector's `Out[1]= 4` contradicts. That file is the founder's, and `bench/tests/test_wolfram_route_retired_2026-09-10.py` asserts the sentence, so both change in 1 commit. **Recommendation: approve the edit, and the assistant makes both changes together.**

**(g) A8: whether any backup holds the evidence files that no git ref contains.** 50 cited paths are absent from this machine and from every git ref's history, measured by `scripts/orphan_citation_era_2026-09-17.py`. **Recommendation: check Time Machine or another machine once; if nothing holds them, the manifest's label stands as the answer and A8 can close after its Section P review.**

**(h) The experiment 56 arm-declaration exposure, held as an expected failure.** Its fix edits a frozen pre-registration. **Recommendation: leave it as an expected failure until the revised model is reviewed, since the run it belongs to is deferred anyway.**

## 3. Decisions that surfaced in today's work

**(i) 3 paid dispatchers read a brief and pay without validating it.** `bench/confer_track_record_pr_2026-08-22.py`, `bench/confer_stage1_audit_pr_2026-08-18.py` and `bench/confer_enforcement_prose_pr_2026-08-19.py`. They are recorded in `bench/directives/universal/unvalidated_paid_dispatchers.json` as OPEN EXEMPTIONS, not decisions, and a test refuses any new paid dispatcher that is neither validating nor registered. **Recommendation: retire all 3, because each was written for a single past review and the maths panel dispatcher supersedes them; the alternative is to add the validator call to each.**

**(j) The dispatcher reuses a seat's sandbox after a timeout.** fable hit the 1,800 s cap in round 17 and its retry reused the sandbox built at 16:38:13, so 14 of the 19 files it left have no reply behind them, and its verdict on A23 was measured against its own unreported edits. **Recommendation: fix it before the next panel round, by building a fresh sandbox per attempt and recording the attempt in the reply.**

**(k) A proposed entry V9, not opened.** Task V1's third condition, that a DONE entry's evidence must go red against a reverted fix, is not implemented and no entry tracks it. Opening an entry is the founder's to approve. **Recommendation: open V9 and schedule it after the model review, because it is the guard that would have caught R3's evidence passing against a reverted fix.**

**(l) The CC1 clause of P5 has no instrument.** Whether CC1 states its own position and synthesises the range is checked by no test or script. **Recommendation: give it its own OPEN entry rather than leaving it inside a DONE one.**

**(m) The 5 agent worktrees, 2.3 GB.** They sit under `.claude/worktrees/`, their branches intact, and every change they produced is merged and committed. **Recommendation: the assistant removes the worktrees and leaves the branches, on the founder's `y`.**

**(n) 3 tests fail in a copy with no git repository**, in `bench/tests/test_every_test_file_is_collected_2026-09-01.py` and `bench/tests/test_overstated_entries_2026-09-11.py`. They fail openly rather than inventing an answer, which is the correct half; in a panel sandbox they still raise the "DONE entries whose evidence failed" banner. **Recommendation: repair them with the same reasoned skip already adopted for M1, A16 and A2.**

## 4. What happens if none of this is decided

Every default is already in force: R10, R11 and A19 stay held; the I31 call stays and cannot fire; arm C stays launch-blocked; Wolfram stays denied to automated runs; the 3 unvalidated dispatchers stay registered and unused; the worktrees stay on disk. No item now carries a date: the Wolfram licence renews itself under a LaunchAgent.

Written under CDSFL note standard v1.7 (26 August 2026).
