# CDSFL master task list

**Opened 2026-09-09 13:45 BST (Europe/London). This is the standing work list. Update it as each task closes; do not rewrite it from scratch.**

**Desktop mirror: `~/Desktop/CDSFL_MASTER_TASK_LIST.md`.** The repository copy is canonical, because an unversioned file on one machine is a single point of failure.

**Why this file exists.** The founder ruled on 2026-09-09 that the programme is large enough that important elements will not survive the next compaction, and asked for one place that survives it. The full evidence behind every entry is in `experimental_notes/Research_FULL_RECORD_2026-09-09.md`, 1221 lines, which is the unfiltered output of 6 read-only research agents.

**Ordering is the founder's, verbatim:** the reliability mechanism first, then falsifier supply and the disabled machinery, "then the full itinerary of the rest. Full and complete and without exception and without stopping until complete." The remote-connection work goes last, by his instruction.

**Standing condition on every fix, founder ruling 2026-09-09, verbatim:** *"In all cases and with all fixes always check them with Fable and CC2 in full CDSFL panel review format (so not just some simple open ended prompt), they must use whatever aspects of the harness are currently working, including our mathematical model and all relevant mechanics in the formation of their answers/fixes, as should you. this format should then be saved as the standard for all future 6 full paid model reviews also."*

Status vocabulary is the note standard's: PROPOSED / BUILT / TESTED / COMMITTED / ENABLED. A defect is OBSERVED or HYPOTHESISED.

---

## 0. URGENT — expires 2026-09-11, 2 days from opening

**0.1 Renew the Wolfram Engine licence.** Status PROPOSED, needs the founder.
The Engine is documented to reactivate itself as expiry approaches, and **on this machine it has not**: `~/Library/WolframEngine/Licensing/mathpass` still carries its original mtime of 2026-08-02T21:09:38+0100 with 2 days left, while the Engine has demonstrably run and reached the cloud since (paclet files rewritten 2026-09-09T11:26:04+0100). No Wolfram-owned page promises an email reminder; the founder's assumption that one would arrive is **not supported by any published Wolfram source**. At expiry the kernel prompts for reactivation — a stop, not a degradation. Route: `wolframscript -activate`, or a fresh licence at `https://www.wolfram.com/engine/free-license/`. The Wolfram ID is reused; no re-download. **Not run here because it writes to the licence file and needs his credentials.**

**Open and material to this project:** how that reactivation prompt surfaces to a non-interactive `wolframscript -code` call driven from a bench runner is unconfirmed. This project has a recorded history of error strings being ingested as answers, so a licence prompt arriving as stdout is a live risk to any run after 2026-09-11.

**0.2 The WolframCloud MCP route is dead and should be retired, not repaired.** Status PROPOSED.
39 connection failures, first at 2026-09-04 23:12:11 and most recent 2026-09-09 09:02:48, against 2 successes in the whole log. The founder states the service was retired or changed such that it became impractical, and that the local Engine replaced it. The record agrees. The remaining work is to stop the app retrying a dead endpoint every few minutes and to make the local Engine the named route in the tool constraint box.

---

## 1. The reliability mechanism — founder ruling: top of the list

**1.1 Add a pre-commit hook that refuses a commit when the cheap guards are red.** Status PROPOSED.

**The finding, and it is unambiguous.** A commit-time guard was discussed on 5 separate occasions between 2026-08-25 and 2026-09-07 and **was never built**. All 4 installed hooks are `UserPromptSubmit` context injectors: they make 0 subprocess calls, emit 0 blocking decisions, and always exit 0. There is no git hook (14 files in `.git/hooks`, all `.sample`), no continuous integration, and `core.hooksPath` is unset. Nothing anywhere inspects repository state before a commit. **Commit `57d5a0e` reached HEAD on 2026-09-09 at 08:16:17 with the suite red**, which is the proof rather than the theory.

**The design, and why it is small.** Run only these 4 already-mutation-verified files and refuse on non-zero exit: `test_documentation_drift_guards_2026-08-25.py`, `test_recovery_memory_doc_repairs.py`, `test_memory_index_limits_match_the_loader_2026-09-01.py`, `test_line_citations_resolve_2026-09-01.py`. Measured cost **28 tests in 1.26 s**, against 669.92 s for the full suite. That is what makes it survivable per commit; a full-suite gate would be bypassed within a day. These 4 files are exactly the ones that caught the 2026-09-09 breakage after the fact.

**Three wiring conditions**, without which the hook is itself an addition nothing reaches: it must live under a versioned `hooks/` directory, `core.hooksPath` must be set by the onboarding script rather than by hand, and a test must execute the hook and prove it refuses a deliberately broken tree.

**1.2 The gap a pre-commit hook does NOT close, measured.** Status PROPOSED.
Of 19 self-inflicted defects caught over 2026-09-08 and 2026-09-09: the test suite caught 7 (36.8%, Wilson [19.1%, 59.0%]), a later self-check caught 7, the founder caught 4 (21.1%, Wilson [8.5%, 43.3%]), a linter caught 1. Mechanisms took 8 of the 12 that fell to mechanism-or-founder, which is **not distinguishable from chance** (exact binomial p = 0.194, Fisher p = 0.110). Script: `scripts/who_catches_the_defects_2026-09-09.py`. It is a caught-only sample and the classification is the assistant's own, so it is an order-of-magnitude instrument for siting a guard, not a defect rate for CC1.

**The part that survives falsification.** Reclassifying every arguable entry in all 16 combinations moves the counts a long way — worst case p rises to 0.598 — but leaves one thing untouched: **all 4 founder-caught defects are CLAIMS, not code**, and all 8 mechanism-caught defects are artefacts a checker can read. A wrong statistical instrument, a misread clock, a stale "the push is blocked" carried across a compaction, and a conclusion drawn from measuring the wrong object. **A test suite evaluates code; nothing in this project evaluates a claim.** That split holds whichever way the 19 entries are classified, which is why it is the part worth acting on.

**1.3 The ancestor of this idea already existed and was the one command that did not survive.** Status PROPOSED, needs a founder ruling.
`qwerty` was a 5-point per-turn self-verification protocol in the February 2026 shorthand table, and `QWERTY_CHECKPOINT.md` was the file it wrote. Of that table's 5 entries, 4 survive verbatim in the current metacognitive command list; `qwerty` is the single one that does not. The self-check command is the one that was dropped. Whether to revive it, and in what form, is his call.

---

## 2. Falsifier supply — the halt cause

**2.1 Widen the falsifier intake parser.** Status PROPOSED. Founder ruling: *"build the fix and test it, then as ever, ask Fable and CC2 to check your fix."*
The 2026-09-08 Exp 45 run halted on `HALTED_IRREDUCIBLE_QUEUE_ALARM`. The attributed cause, 5 of 14 criticals arriving with no runnable falsifier (35.71%, Wilson [16.34%, 61.24%]), is real but downstream. The dominant loss is upstream in the intake parser: it recovered **26 of 69** `FALSIFIER:` blocks across the run (37.68%, Wilson [27.18%, 49.48%]) and **1 of 9 in the round that halted** (11.11%, Wilson [1.99%, 43.50%]). The seats were supplying falsifiers; the parser was dropping them. Fix at `bench/runner_core.py:1165-1175` and the guard at `:1236`.
**OPEN:** recovering a block is necessary but not sufficient — it must still bind to the right finding, so this is not shown to have prevented the halt.

**2.2 Implement and test every missing falsifier.** Status PROPOSED. Founder ruling: *"fix and test all remaining missing falsifiers."*
Includes C0050, confirmed as the single residual human-queue item at severity 0.9 with no falsifier of its own claim, none ever executed, and 0 verdicts recorded. It does not meet any reasonable reading of computationally irreducible.

**2.3 Fix falsifiers that are being misread rather than missing.** Status PROPOSED. Founder ruling, standing from 2026-09-08.

---

## 3. Enable the machinery that is switched off

**3.1 Turn routing and the sweep back on in the exp56 configurations.** Status PROPOSED. Founder ruling, verbatim: *"these are the class of misconfigurations I observed as significant previously and they should be fixed."*
All 3 files carry `routing_enabled: false` and `post_convergence_sweep_rounds: 0`. All 4 capabilities the founder suspected of being broken — fingerprinting, routing, the sweep, decomposed dispatch — are still reached by live callers. Nothing is unwired; it is configuration.

**3.2 Restore tool use to the DeepSeek route.** Status PROPOSED. Founder ruling, verbatim: *"Why does DeepSeek get a free pass on tool use? ... No tool use is an unacceptable condition in the CDSFL schema, when an item exists that is genuinely computable. Verdict, fix DeepSeek and test it."*
`bench/experiment_11_orchestrator.py:1442` sets tools to none unconditionally for that route.

**3.3 Sweep for any other capability disabled by configuration rather than code.** Status PROPOSED. The exp56 case was found by accident; nothing has looked for siblings.

---

## 4. The doctrine corrections

**4.1 Amend the escalation rule to name misconfiguration.** Status PROPOSED. Founder ruling, verbatim: *"Verdict, do it, test it, then same answer as above, then test the fixes under f, and sy and then apply them to the simulation experimental runner if they check out."*
The rule appears in 5 live places and the word appears in 0 of them: `docs/GLOSSARY.md:168`, `bench/reference_runner_v3.py:6096-6098`, `scripts/hil_escalation_by_run.py:8`, `resources/RECOVERY.md:66`, `experimental_notes/CDSFL_Agent_Operational_Plan.md:132`. It must also point at where the fault might lie. No test asserts on the wording; a new one must CALL `build_irreducible_queue_alarm` and assert on the returned string, not read the source.

**4.2 Correct the simplicity note that propagated a wrong definition.** Status PROPOSED.
`memory/feedback_simplest_sufficient.md` carries the sentence *"Prefer extending machinery that exists and is already trusted over inventing a new component."* That single line is the source of the formulation the founder rejected on 2026-09-09, and it reappeared on 2026-09-07 and 2026-09-09. **His objection is correct and the record backs him:** simplicity is a property of the solution, not of its ancestry, and framing it as a preference for reuse tells models never to innovate and to keep building on worse foundations.

**The 3 axes are distinct, and 2 of the 3 are already in the mathematics.**
- **Sufficiency** is formalised: sigma and S_k at `docs/MATHEMATICAL_APPENDIX.md:214`, the section-10 predicate at `bench/directives/universal/cdsfl_core_formal.md:287-357`, live gate at `bench/reference_runner_v3.py:10934`. It is the HARD constraint.
- **Simplicity** is defined in the maths as the re-injection term nu at `docs/MATHEMATICAL_APPENDIX.md:215` — but **its implementation is a constant blind to complexity, and the module that would measure it has no caller.** It is the tie-breaker among candidates that already clear sufficiency.
- **Additivity** appears **0 times** in either mathematics file. It is a governance rule, not a model term, and should stop being described as though it were one.

**Correction to the founder's framing, on the record:** he recalls one considerable chat covering all 3. The chat about simplicity versus sufficiency is real and documented, 2026-08-18 to 2026-09-04, with 4 of his messages on 2026-09-02 alone and 2 committed notes. But additivity was a neighbouring strand of the Bugzilla arc, first raised 2026-08-20 23:04 and made standing 2026-09-07 12:13 — the word appears 0 times in either 2026-09-02 note. There was a 2-way conversation, not a 3-way one.

**4.3 Make nu actually measure complexity.** Status PROPOSED, needs a founder ruling.
Following from 4.2: the term that encodes simplicity in the model is a constant, and its measuring module is unreached. This is the additive standard's own failure mode sitting inside the mathematics.

---

## 5. The panel review format — a standing condition on everything above

**5.1 Write the missing half of the format.** Status PROPOSED. This gates every "check it with Fable and CC2" instruction in this list.
**Half of it exists and is test-guarded:** the `SYSTEM` string in `bench/confer_maths_panel_2026-09-05.py` carries the 28,183-character formal schema plus 4 panel rules, has sandbox confinement, control-plane fingerprinting, real tool-call recording, and a test that executes rather than greps. It is the only 1 of 39 dispatchers that does. Both seats are genuinely tool-enabled: 237 and 41 recorded tool calls on 2026-09-07.
**The other half does not exist as a format at all.** The USER prompt is a hand-written `BRIEF.md` read straight off disk, with no template, no schema, no validation and no test. Measured across all 49 archived briefs: **0 require a seat to use the mathematical model as an instrument, 8 require a fix, 2 require the fix to be tested.**

**Correction to the founder's framing:** he asked that "this format should then be saved as the standard". The presupposition is contradicted — there is no format to save. It must be written first, then saved.

**5.2 Adopt the written format as the standard for all future 6-model paid reviews.** Status PROPOSED. Follows 5.1 and is his explicit instruction.

---

## 6. The remaining engineering, in the founder's "full itinerary"

**6.1** Record all run stop reasons, not only on convergence. 2 of the 8 loop-exit paths set a reason; a 2026-09-08 run wrote an empty reason while its report named the alarm. 3-line fallback before `signal_complete()`. Founder ruling: *"Verdict. Do it, Then same answer."*
**6.2** Derive the seat watchdog budget from the retry budget. `max_retries` is wired and read at 5 sites in `dispatch()`, but is named 0 times in `bench/reference_runner_v3.py`, and the watchdog's `timeout * 3` truncates the configured budget for 4 of 5 seats. Founder ruling: *"Same answer."*
**6.3** Read the caller-supplied logs directory instead of minting a second one. `ExperimentConfig.logs_dir` is written by the launcher and read **0 times** by the runner, which mints its own timestamp and path — a written-but-never-read field, which is the unwired-addition half of the additive standard. Founder ruling: *"Then build the fix and test it, then as ever, ask Fable and CC2 to check your fix."*
**6.4** Close the 6 remaining bounded-traversal instances with one shared path-delimited predicate, 1 of them wired to a suite ratchet. Founder ruling: *"So the sweep (and its original context, which I shouldn't need to repeat), should be run again if you do this? If so, do it."* — **so the sweep must be re-run after the fix, not before.**
**6.5** Tie a monitor's lifetime to its run. 0 launchers clean up monitors and 0 monitors read a process-identifier file; the 1 file written by `bench/detached_launch.sh:11` is consumed only by a read-only printer. macOS `tail` rejects the flag that would make it follow a run and exit with it, so the tie must be a shell wrapper. Founder ruling: *"So again what's the fix? Did you consult the other models yet? If not same as the last answer."*
**6.6** Instrument target rewrites with an author, not only a blob hash. Attribution of the 12 rewrites of `bench/dm/_memory.py` is OPEN because the watch recorded hashes and not actors.
**6.7** Assess whether the seat's `update_drift` guard is correct. It is a candidate finding against a detector the committed source still describes as unreached.

---

## 7. The notes remediation

**7.1** Repair the experimental notes. Status PROPOSED. Founder ruling, verbatim: *"Fix them all, or at least those that a technical reader would be likely to find insufficient in the interests of reproducibility."*
**1158 findings across 217 of the 373 notes** (58.18%, Wilson [53.11%, 63.07%]), of which **535 are the unnamed-subject class** (46.20%, Wilson [43.35%, 49.08%]) — the exact class complained of. 1 offending phrase accounts for 235 findings, 20.29% of the corpus.
**7.2** Wire the vagueness linter to something. Whether any hook, test or continuous-integration step invokes it is OPEN; the evidence suggests it is only ever run by hand, which is the 2026-09-04 lesson repeating.
**7.3** Record the two-document distinction, founder ruling 2026-09-09, verbatim: *"The experimental notes (all of them) are intended for the technical reader to allow them to follow along with everything we have done exactly, and exist in the interests of scientific reproducibility. My TTS notes are a more generally comprehensible version of these accessible to the skill level of a technical, but non-coding engineer ... They are separate, but related resources. This should be clearly marked and remembered in all your output."*

---

## 8. Housekeeping

**8.1** Amend the `rs` definition in the global configuration. `ACTION_QUEUE.md` and `QWERTY_CHECKPOINT.md` are **Project_Genesis artefacts from February and March 2026**, later copied into Metis, and were never present in Constraint_Engineering across 1,161 revisions. Make the 2 names project-conditional rather than unconditional; a flat delete is also safe, since every consumer already has a project-local pointer. Also sweep the residual mention at `resources/SHORTCUTS.md:36`.
**8.2** Adjudicate the exp39-experimental branch with Fable and CC2. Founder ruling, verbatim: *"Get Fable and CC2 to look at this with you, decide which elements on this branch remain useful and should be adopted in light of everything else we have done and which should be considered superseded."* It holds 107 commits unreachable from `origin/main`, 865 orphan-candidate objects and 12 file paths existing nowhere else, but its tip tree is byte-identical to main commit `043a0a8`. One tag command pins everything before any deletion.
**8.3** Rebuild the figure that justifies keeping that branch. "20 of 21 falsifiers reproduce against an earlier stored version" exists only as prose and as a code comment at `scripts/adjudicate_by_repair.py:270`, with no committed output. The rule covering this explicitly names code comments.

---

## 9. The next simulated run — everything above feeds it

Founder ruling, verbatim: *"We will begin another simulated run once all these remaining issues have been addressed and you have checked your fixes with Fable and CC2 as previously."*

And, raised by him for the third time: *"Conduct your outstanding full programme of study in the next experimental run, since you say you skipped it in the last run, and add the above fixes to this study programme too, and note how well (or otherwise) all our fixes perform."*

**9.1** The 6 study-programme items already scheduled by his 2026-09-06 rulings: the critical-severity ceiling; why the sweep cannot clear a critical; classifying falsifier ERROR causes; the rho = 0.564 cross-architecture correlation; corrected S\* values; and both reach conditions. **Reported on: 0 of 6 in the last run.**
**9.2** Add every fix in this list to the study programme, and measure how each performs.
**9.3** Study the intake-parser behaviour specifically. Founder ruling: *"Study the parser behaviour in the next simulated run and report."*
**9.4** Note that study item 46, the cross-architecture correlation, was **unanswerable in the last run** because all 6 seats were one model wearing 6 labels. Fixing that is a precondition, not a measurement.

---

## 10. Last, by founder instruction — the remote connection

**10.1** Build a script the founder can run from his hotel machine that restarts the desktop application and re-establishes this session's remote control. Founder ruling, verbatim: *"We will build a script I can place on my remote desktop here in my hotel, which when I run it will restart you/the Claude desktop app and if necessary/technically possible restart this specific session, so I can begin working with it immediately."*
**The mechanism is now known rather than guessed:** remote control was re-enabled at 2026-09-08 18:10:21 with `[rcAutoEnable] verdict: enable=true source=explicit_pref trigger=warm_send`. The trigger is a message sent locally at the machine. The preference is already set; only the trigger was missing.
**A correction the assistant owes here:** it reported that the session recovers unaided and that returning home was very unlikely to be what restored it. That was wrong. It measured `sessions-bridge` reconnecting a persisted cloud session and reported it as this conversation's remote control, which is a different object and was not restored. The founder's account was correct throughout.
**10.2** Decide whether to enable the private network's own shell service, currently off, which would remove key handling.

---

## Sources

`experimental_notes/Research_FULL_RECORD_2026-09-09.md` (1221 lines, the unfiltered agent output behind every entry above); `experimental_notes/CDSFL_Agent_Operational_Plan.md`; `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md`; `experimental_notes/RUNWAY_to_BR2_2026-08-18.md`; `resources/RECOVERY.md`; `experimental_notes/Morning_Report_2026-09-09.md`.

The inventory behind this list counted **121 distinct open items** across those sources, of which 19 already carry a founder ruling and need only execution, 17 need a founder decision, and 26 are blocked on a named prior item. This file is the ordered executable subset; the 121-item inventory is in the full record.

Written under CDSFL note standard v1.7 (26 August 2026).
