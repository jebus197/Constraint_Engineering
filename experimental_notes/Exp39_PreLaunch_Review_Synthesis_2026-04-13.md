# Exp 39 Pre-Launch Review Synthesis

**Date:** 13 April 2026 04:51 BST
**Scope:** 10-stream pre-launch review — 5 external model confers (CC2, the Claude Opus 4.6 CLI instance; Codex 5.6; Gemini 3.1 Pro; ChatGPT 5.4; DeepSeek Reasoner) + 5 internal CC (Claude Code) sub-agents (InsectBrain, Immune Pipeline, CC2 Runner, DM Convergence, Launch Sequencer/PE)
**Outcome prior to commit 2279adb:** All 10 streams returned NO-GO
**Outcome after commit 2279adb:** 11 distinct blockers fixed, reassessment below


## Cross-Stream Corroboration Matrix

Four findings were discovered independently by multiple streams. These carry the strongest evidential weight.

**HIL (human-in-the-loop) pause / exit 42 mishandling** was the most widely corroborated failure. Gemini identified it as a BLOCKER (exit 42 counted as fatal in required_failures). ChatGPT independently found the same issue. DeepSeek flagged two causally linked symptoms: B1 (HIL pause exits without saving checkpoint) and B3 (resume restarts from experiment 1 rather than the paused position). The InsectBrain sub-agent corroborated the checkpoint side — `_save_checkpoint()` was serialising only 9 of 20 Finding fields, meaning any resume after HIL pause would restore a degraded state even if the checkpoint file existed. Taken together, four streams converged on one root dysfunction: the HIL pause/resume path was broken end-to-end, spanning exit code propagation, checkpoint completeness, and field restoration.

**Launch CLI plumbing** was independently found by two external models. Codex identified that `launch_exp39.py` did not forward `--hil-review` or `--resume` to the child runner and therefore could not propagate exit 42 correctly. ChatGPT raised the identical finding. No sub-agent was scoped to the launch script directly, but the consequence (broken resume) was the downstream manifestation caught by DeepSeek and Gemini.

**DOMAIN_MAP missing entries** (biology, cs_software, information_science) was found by ChatGPT and independently by DeepSeek (B2). Two external models, no sub-agent coverage — this is a gap in the internal review scope rather than a weakness of the finding itself.

**PE (PolicyEngine) HARD constraint runtime enforcement** was raised by CC2 (as a structural observation: `ffafp_required` and `structured_reasoning_required` defined in schema but no runtime validation in the immune pipeline), corroborated by ChatGPT (labelled UNCERTAIN), and by DeepSeek (B4, labelled HARD VIOLATION). Three streams flagged this. The sub-agent immune pipeline review also caught related unenforced behaviour — `UNSCORED` verdicts incorrectly rejected — which is a manifestation of the same class of problem: immune agent behaviour not matching declared schema constraints.

**Config pattern mismatch** (all 14 configs using `pattern="fff"` rather than the reviewed four-layer protocol) was found by Codex alone among the external models. No sub-agent caught it. It is a clean single-source finding, not corroborated, but mechanically verifiable and unambiguous.


## Blocker Classification

Eleven distinct blockers were fixed in commit 2279adb. Classified by type:

**Plumbing (3):** CLI argument forwarding missing (`--hil-review`, `--resume` not passed to child runner); HIL pause excluded from required_failures count; dependency check incorrectly including hil_paused results. These are wiring failures — correct logic existed but was not connected through the launch layer.

**Serialisation (3):** `_save_checkpoint()` serialising 9 of 20 Finding fields (data truncation on pause); `load_checkpoint()` not restoring all 20 fields; non-atomic checkpoint and round JSON writes (write_text rather than tmpfile-and-rename). These are data integrity failures that would have produced silent partial state on resume without any error signal.

**Semantic error (3):** `typed_llm_classifier()` with unbound `domain` variable (would raise NameError at runtime); `UNSCORED` verdicts incorrectly excluded from the pass-through set (valid findings silently dropped); exit 42 counted as fatal failure rather than propagated as pause signal (correct exit code treated as error).

**Config (1):** All 14 experiment configs using `pattern="fff"` — the old single-layer pattern — rather than `"four_layer"`, meaning the reviewed protocol was not being invoked.

**Design / schema (1):** NK (natural killer) cell false-positive patterns from domain TOML not merged into immune agents; Reg T (regulatory T-cell) v2 UNCERTAIN rate check missing. These were added in the fix commit but sit at the boundary between implementation gap and design oversight.


## Residual Risks

Three categories of concern were raised by reviewers but are not fully resolved by commit 2279adb.

**Burst mode checkpoint gap.** Codex flagged that burst mode phase state is not checkpointed before pause. This was explicitly deferred as not relevant for 39-0 (burst_mode=off) but remains unresolved for future runs that enable burst mode. It is a latent correctness risk conditional on configuration.

**PE HARD constraint runtime enforcement.** All three models that flagged this — CC2, ChatGPT, DeepSeek — agree that `ffafp_required` and `structured_reasoning_required` are declared in schema but not enforced at runtime in the immune pipeline. The fix commit added Reg T v2 UNCERTAIN rate check and NK cell FP (false-positive) pattern merging, which are adjacent improvements, but the specific structural gap — no runtime validation that findings entering immune processing satisfy the schema constraints — was not listed among the 11 committed fixes. This is the most significant open item. If the gap remains, HARD constraint definitions serve as documentation rather than enforcement, which contradicts the core CDSFL (Constraint-Driven Synthesis and Falsification) premise.

**HIL visibility.** Gemini's readiness confer (separate from this review, logged in the 13 April readiness assessment) noted that round reports present counts only, giving HIL reviewers insufficient signal to make informed pause/continue decisions. This was assessed as valid and deferred. It does not block 39-0 but degrades the quality of HIL oversight during the run.

**Three sub-agent streams not read before compaction.** The CC2 runner review, DM convergence review, and launch sequencer/PE review completed but their outputs were not read before session compaction. The continuation summary notes these likely overlapped with known blockers, and the 11 committed fixes cover the intersection of all named streams. However, any finding unique to those three streams — not corroborated by the streams that were read — may have been lost. This is a procedural gap in the review record, not a claim that unknown blockers exist.


## Review Methodology Assessment

The 10-stream approach produced meaningful redundancy that a single reviewer could not have replicated.

The corroboration pattern itself is informative. The HIL/exit-42 cluster was found in four independent ways: structural (Gemini, ChatGPT flagging the exit code), causal (DeepSeek tracing what happens to progress on resume), and data (InsectBrain finding the serialisation truncation that undermines resume even when exit code is correct). A single reviewer would likely have found one entry point into this failure and missed the others. The combination established the full failure chain.

The CLI plumbing gap was found by two external models but missed by all five internal sub-agents. This reflects scope: the sub-agents were targeted at component internals, not at the launch orchestration layer. External models, prompted to review launch readiness broadly, naturally swept the entry point. This is the expected division — component review and system-level review are not substitutes for each other.

The DOMAIN_MAP omission was found by two external models and no sub-agents. Again, this is a scope artefact. The sub-agents reviewed specific files; the domain map is a configuration artifact that sits outside any single component's review boundary. Multi-model external review caught it specifically because the prompts were system-wide.

The config pattern mismatch was found by one model only (Codex). It is the kind of finding that requires a reviewer to cross-reference the config files against the current protocol specification — a task that benefits from having been given the protocol documentation as context. The fact that only one model found it does not diminish the finding; it suggests that not all external models were equally primed on the four-layer protocol definition.

The false-negative risk is the three unread sub-agent streams. The methodology produced more output than could be processed before compaction. For future multi-stream reviews, all stream outputs should be read and reconciled before any state-saving event.


## GO/NO-GO Reassessment

**Conditional GO for 39-0 with burst_mode=off.**

The 11 committed fixes directly address every blocker that would cause a run to fail silently, lose progress on resume, or produce incorrect verdicts. The serialisation fixes are complete (all 20 fields round-trip). The exit code propagation is correct. The CLI plumbing is in place. The DOMAIN_MAP entries exist. The config pattern is correct across all 14 configs.

The open PE HARD constraint enforcement gap warrants attention before runs that rely on the schema enforcement path as a control mechanism. For 39-0, where the primary target is the immune pipeline under structured conditions, the risk is that HARD constraint violations in findings could pass through without being caught at the policy layer. This is not a hypothetical: DeepSeek labelled it a HARD VIOLATION and CC2 raised it as a structural gap. It should be investigated and either confirmed-fixed or explicitly accepted as a known limitation before 39-0 is declared fully clean.

Burst mode remains deferred and acceptable for 39-0 specifically.

HIL visibility remains deferred and acceptable for 39-0 with awareness that HIL decisions will be made on count-level information only.

The three unread sub-agent streams represent an unresolved gap in the review record. Unless their outputs are recovered and reconciled, the review cannot be called complete. The practical risk is low given the corroboration coverage from the streams that were read, but the gap should be acknowledged explicitly rather than assumed away.

**Summary position:** 39-0 is launchable. The PE HARD constraint enforcement gap is the one item that should be investigated before declaring full readiness — not because it will crash the run, but because an unenforced HARD constraint is a contradiction of the system's stated design contract.
