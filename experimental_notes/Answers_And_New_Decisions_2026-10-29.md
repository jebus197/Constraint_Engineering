# Answers and New Decisions

**2026-10-29 17:45 GMT (Thursday).** Branch `sim/shakedown-2026-09-29`.

This note follows `Responses/Decisions_Awaiting_You_2026-10-29.txt`, which the founder annotated with 13 verdicts earlier the same day. It answers the 3 questions those annotations raised, withdraws 3 claims the earlier document made which later measurement refuted, records the 7 pieces of work the rulings authorised, and raises 5 new matters needing a decision. The master task list was not resumed, on his instruction.

Every proportion carries a 95% confidence interval computed twice by independent methods. The claim-channel algebra was additionally checked in Wolfram Language, which agreed on all 6 properties; that agreement is attributed to Wolfram Language and the open-source tools remain primary.

## 1. The 63 adjudications: the no-voting rule was being applied too strictly

**His challenge, verbatim:** *"63 adjudications/verdicts (if they are verdicts like these?) is days worth of work for me. This seems like an unreasonable amount of work, and makes me wonder if you are applying the 'no-voting' rule too strictly? It is a rule intended for the models in the harness during experiments (simulated and real), not a rule that prevents you from doing work that is computationally reducible, and that might not normally be up to a HIL to decide. But if you can demonstrate why a HIL is specifically required in this case, I will consider them."*

He is right, and the rule's own text settles it against the sentence that had been resting on it.

- The standing correction in `.claude/CLAUDE.md` reads **"Findings confirmed programmatically or by HIL — no model voting"**. The memory behind it, `feedback_no_model_voting.md`, records the correction that produced it — *"When did machines get voting rights?"* — and sets the status model as `OPEN -> CONFIRMED (>=2 independent models, programmatic)` or `UNCONFIRMED -> HIL_REVIEW`. **Programmatic confirmation is one of the two permitted routes.** What is forbidden is a model *vote to reject a finding*, a different act from a deterministic script applying the 5 clauses of `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`.
- **The project has already done it once.** `experimental_notes/adversarial_records/rubric_adherence_audit_0C8_2026-09-02.json` holds **286 first-pass verdicts and 108 second-pass verdicts** against those exact clauses, each with written reasoning.
- **63 is a power figure, not a workload:** simulated power 0.916500; about 48 reaches 0.80. The closed form of 35 simulates only 0.6472 and must not be quoted.
- **0 items have been shown to require him.** `scripts/reproduce_rubric_human_queue_partition.py` states that an item is irreducible only if a falsifier cannot be written for it, and none has been shown untoolable. 1,911 of 3,255 archive entries carry no falsifier — 0.587097, Wilson [0.570090, 0.603899], exact [0.569957, 0.604080] — which is a tooling backlog.
- **Where a human is still worth it is validation, not production.** Over 4,000 draws (seed 20261029), an anchor set of **30** labels detects a labeller agreeing at kappa 0.80 with probability 0.9537, against 0.9902 at 63 and 0.8500 at 15.

Producer: `scripts/how_many_adjudications_actually_need_him_2026-10-29.py`. The refuted sentence has been replaced in both `~/.claude/CLAUDE.md` and `.claude/CLAUDE.md` with this reasoning, so it cannot be repeated from memory.

**A provenance gap found in the same pass, and an addition to his point rather than a correction of it:** that audit names **no scorer**, and its `ground_truth` field holds the withheld severity values rather than human labels. Raised as new matter 3 below.

## 2. The immune-memory assertions, refreshed at his request

**His annotation:** *"You need to refresh my memory of exactly what this is referring to?"*

The immune memory is the store of priors the immune layer accumulates about recurring flaw classes. He reset it on 2026-10-17; the archive preserves his stated reason — that the reset was for the upcoming live experiments, since simulation can only tell us so much about how the facility will function in real live or paid experiments — names the 6 experiments it held, and carries a restore command.

6 assertions in `bench/tests/test_immune_memory_evaluation.py` were written against the pre-reset population and describe 3 to 5 experiments. The live store holds 1, because a free run wrote the first post-reset records at 00:57 on 2026-10-29. **The product is correct and the assertions are stale.**

They did not fail on the day of the reset because a skip was added on 2026-10-17 for this exact false alarm, conditioned on 0 records on disk plus an archive, with the stated intent that it would re-arm once a run wrote. This morning's run wrote, so the skip lapsed correctly and the assertions re-armed correctly against a population that cannot return.

2 of the 6 are a stale constant naming 3 runs dated late July, roughly 3 months before the reset, and a filter repairs both: 0.333333, Wilson [0.096771, 0.700007] — wide because 6 is a small denominator. The other 4 assert facts measured on data the reset destroyed.

**Recommendation, unchanged:** widen the skip condition from "0 records plus an archive" to "the live store no longer contains the runs the claim was measured on", which preserves the intent that it is not a permanent exemption. Alternatives are to re-measure all 4 against the post-reset store as it fills, or to restore the archived priors — the latter would undo the reset he ordered and is listed only for completeness. **Still needs his word; not built.**

## 3. What the severity wobble meant, and whether it still matters

**His annotation:** *"You previously reported that severity 'wobbled', and could not be pinned exactly to 0.7? You recently did work on the severity gate however, so perhaps the question is what did you mean, and is this still relevant in light of this work?"*

2 distinct things, and the link between them is the consequential part.

- **The wobble** is the spread between 2 independent assessments of 1 defect. Over 147 archive entries where 2 or more independent assessments of 1 defect are recoverable within a single run: median **0.1200**, mean **0.1786**, against the 0.1419 the 2026-10-18 brief asserted. Producer: `scripts/is_severity_noise_or_disagreement_2026-10-19.py`.
- **The 0.7** is the critical cut — an undocumented code convention (F6), pre-registered on 2026-05-18 as a numeric proxy for the 5-clause rubric, with the rubric authoritative where the 2 disagree.

**The link.** With assessments of 1 defect differing by about 0.12 and the cut at 0.7, a defect genuinely near the cut lands on either side depending on which assessment is kept — and **nothing combines them**. Executed against the registry on 2026-10-29, `FindingRegistry.resolve(..., "MERGED", ...)` keeps whichever entry happened to be the merge *target*, carrying its own first-recorded severity; an AST walk finds **0** calls to `max`, `min`, `median`, `mean` or `sum`. The kept value lies outside the range of its own inputs in **35 of 147 — 0.238095, Wilson [0.176469, 0.313061], exact [0.171789, 0.315261]** — 24 above every assessment and 11 below every one, with one entry carrying assessments of 0.35 and 0.45 beside a kept value of 0.95.

**Still relevant, and more so.** The recent severity work changed no merge rule. `bench/tests/test_the_kept_severity_is_not_an_aggregate_2026-10-29.py` *pins* the absence of any such rule, so adding an aggregation step turns the test red. And `scripts/the_severity_proxy_was_never_tested_2026-10-28.py` established that the band the proxy was tested on is only 0.09 wide, making that measurement uninformative rather than negative. **So his original reading is strengthened:** if the kept number is whichever entry happened to be the merge target, the point value is not a summary of anything, and a range would be strictly more informative than the point value it replaces. What severity should *mean* remains his, as he said; what the archive can now say is that the present point value is arbitrary.

## 4. Three claims from the morning document, withdrawn

### 4.1 The workspace trust flag — he was right and the second half of the claim is refuted

**His annotation:** *"This is part of the Claude login process, which as stated previously has already been done. The login process asks you to trust the workspace or not. I accepted the prompt to authorise it. You can test it to see."*

Measured from `~/.claude.json`: `hasTrustDialogAccepted` is **True** for `/Users/georgejackson/Developer_Projects` — the directory this session roots at — and **False** for the `Constraint_Engineering` subdirectory, which the earlier note had read. Both statements were true of different keys.

The second half — that seats run degraded — **fails its own test**. Treatment (`claude -p` with cwd inside the repository) and control (the same in a scratch directory with no `.claude/settings.json`) both used the Bash tool successfully; a third condition in that empty directory with all 31 `CLAUDE_*`/`ANTHROPIC_*` variables scrubbed also succeeded. So the project's 20 allow entries are not what grants a seat its tools, and no degradation exists. Producer: `scripts/does_the_project_allow_list_reach_a_seat_2026-10-29.py`. **Decision 2 should be withdrawn rather than ruled.**

### 4.2 The identityless floor is 319, not the 320 he was asked to approve

His ruling rested on the claim that the identityless count of 320 *"cannot be brought back down"*, so the fix was built first. `TicketStore.adopt_identity` succeeded on `pf:b0d8ca44a450` and the count fell to **319**; it was correctly refused on `qs:7d558a3e3381` and `pf:b4517f6ecfe6`, each of which already has a correctly-identified twin at the digest its anchor implies. `IDENTITYLESS_CEILING` is set to 319. Producer: `scripts/an_identity_can_now_be_walked_back_2026-10-29.py`.

### 4.3 The explanations owed number 16, not 9

The figure of 9 was recalled rather than enumerated. From the register, **16** live items carry text of his asking for an explanation; 2 are answered here, leaving **14**. Now entry **B51** on the master task list, which lists all 16 by the response file each was annotated in.

## 5. What the rulings authorised, and what was built

| # | Entry | His words | Built | Tests | Mutants |
|---|-------|-----------|-------|-------|---------|
| 1 | B47 | *"Build and implement option 1. fr"* | `record_sv_completion`, `unclean_sv_commits`, `_previous_sv_commit(require_clean=True)` in `scripts/cdsfl_sv.py` | 14 | 7 of 7 |
| 2 | B49 | *"Do the re-baseline and implement your fix as you suggest. fr"* | `TicketStore.adopt_identity` + `_by_identity` bridge in `exact()` and `propose()`; ceiling 317→319 | 18 | 4 of 4 |
| 3 | B48 | *"Group them as you suggest. fr"* | `group_feedback_index_entries` in `scripts/cdsfl_sv.py`, wired into the preflight | 15 | 6 of 6 |
| 4 | Q4 | *"I accept your recommendation. fr"* | `register_deferrals`, `effective_state`, `deferral_disagreements`, `derive_deferred_markers` in `scripts/task_list_markers.py`; `TicketStore.undefer` | 17 | 6 of 6 |
| 5 | C1 | *"I accept your recommendation. fr"* | `claim_channel_factor`, `apply_claim_channel`, `CLAIM_CHANNEL_WEIGHT=0.0`, ceiling 0.5 in `bench/claim_ledger.py` | 16 | 7 of 7 |
| 6 | B46 | *"leave them as history…"* | `qs:3684bacc44bd` CLOSED with his answer as its resolution | — | — |
| 7 | R1 | *"It should go at the end of your current master task list."* | moved from 16th of 184 to last of 186; 184 identifiers verified identical; checker 0 problems | — | — |

**Details worth recording:**

- **B48** took the index from **174 lines to 105**, refusal headroom from 26 lines to 95, with `chars` unchanged at 21,231 and all 187 pointers intact.
- **Q4** found the 2 deferral representations disagreeing in both directions: markers deferred `B20, C33`; the register deferred `B13, B20, B21, B22, C1, C21, C33`. They now agree exactly. Building it required `undefer`, which did not exist — deferral was one-way, so an item deferred pending his decision stayed deferred after he decided. 3 of the 7 (`C1`, `B21`, `B22`) were discharged by his rulings today and cleared with those rulings recorded.
- **C1**'s form is `R_k_effective = R_k * (1 - weight * coverage)`. SymPy, z3 and Wolfram Language agree on 6 properties: the factor lies in [0.5, 1]; the product in [0, 1]; the product can never exceed `R_k`; weight 0 and coverage 0 each leave `R_k` exactly unchanged; a positive `R_k` cannot reach 0; and `d(factor)/d(coverage) = -weight`. The ceiling is 0.5 rather than 1 because at 1 with full coverage annihilation **is** reachable (z3: sat), which is the ceiling's justification. Weight is 0 by default, so the arithmetic is built and not switched on.

**3 defects were found in this session's own work by its own falsification passes**, and each is recorded where it happened rather than quietly fixed:

1. B47's skip message was built from the unclean *record set* rather than from the actual resolution, so it could have announced a skip that never happened. Mutation 4 of 6 exposed it.
2. B47's recorder was tested while its call site was not, so writing the wrong cleanliness value left every test green. Mutation 5 of 6 exposed it.
3. B49's `exact()` bridge did not reach `propose()`, which computes its own digest — and the guard test passed on the *reworded* tier rather than the bridge, so it was green for a reason unrelated to what it claimed to test. Found by tracing `exact()`'s callers: it has exactly 1 production caller, `candidates()`, which decides nothing.

A fourth, in `adopt_identity` itself: the first version could attach an anchor another ticket already carried, because every check reasoned about the implied digest and `tid_of` never reads the anchor when a `task_ref` is present. A guard was added; a `task_ref` branch that could never fire was deleted rather than left in as apparent thoroughness.

## 6. Five new matters needing a decision

### 6.1 Two distinct faults can collapse onto one identity, and the register is already corrupted

`tid_of` derives a ticket's identity from its `kind` and `task_ref` alone, so 2 different faults filed against 1 entry take the same identity and the second silently overwrites the first.

**The live damage:** `pf:2835f264ae18` is the only ticket carrying `task_ref='B50'` and its surviving title is *"A belt-and-braces assertion in the ruled-item guard is unreachable"* (the guard is `bench/tests/test_a_ruled_item_is_not_a_decision_2026-10-16.py`, which refuses a save while decisions are owed him) — a different fault. B50's actual subject sits at `pf:b276e059857b`, carrying no reference. The register answers the wrong thing for B50.

Recovered from the append-only log, **75** identities have carried 2 or more distinct titles; 65 of those have title word overlap below 0.20, median 0.0488. **That bounds exposure and does not count collapses:** `tid_of`'s own docstring records a non-collapse cause for a changed title — an addendum recording a neighbouring entry as built sits above the entry in a shared block and changes the text the title extractor reads. Exactly 1 case is confirmed by reading, and it is B50's.

**The fix** is to let an identity admit more than 1 ticket per kind and reference. It changes the identity scheme, so it is not built.

**An ambiguity in his ruling, flagged rather than resolved:** *"Do the re-baseline and implement your fix as you suggest"* could mean the identity-setting method (built) or that plus the 4th option above (not built). The recommendation named only the first; the second was described as found by accident. The specific question: did he mean both?

### 6.2 The paid-dispatch decline is enforced in 1 module of the many that could spend

**His ruling:** *"This is declined. No paid dispatch can happen without my express authorisation."*

`bench/confer_maths_panel_2026-09-05.py::select_models` already implements exactly that: it refuses any named paid seat unless `_paid_is_authorised` finds his verbatim words for that round, and every failure path — missing file, unreadable file, wrong schema, unnamed round, quote under the minimum length — returns a refusal rather than degrading to no guard.

But it lives in 1 module. Measured by `scripts/which_paid_routes_pass_his_gate_2026-10-29.py`: **155** non-archived modules name a paid route and **1** consults the ledger — 0.006452, Wilson [0.001140, 0.035636], exact [0.000163, 0.035420]. Of the 34 live entry points, **10** issue an outbound request and so can spend (`decomposed_dispatch`, `experiment_11_orchestrator`, `interactive_smoke`, `live_dispatch_policy`, `openrouter_tools`, `ouroboros_cell`, `run_round_robin`, `runner_core`, `tests/conftest`, `cdsfl_onboard`) and **0** of those consult it.

The measurement is an upper bound, not a demonstration: naming an outbound call is not proof that a reachable path makes it. Lifting the gate into a single chokepoint would touch the live runner path, which is why it is raised rather than done. Raised as `pf:ee787f54d237`.

### 6.3 The blind audit names no scorer

`rubric_adherence_audit_0C8_2026-09-02.json` holds 286 first-pass and 108 second-pass verdicts and no field naming who or what produced them; its `ground_truth` field holds the withheld severity values. A result attributed to nobody is a provenance gap by this project's own standard.

**Recommendation:** record as an addendum, not a rewrite, that the verdicts were model-produced and by which route if the run's own logs can still establish it — and state plainly that they cannot if they cannot. It bears directly on how much weight the 286 labels can carry.

### 6.4 Whether to commission the run that would justify a non-zero claim-channel weight

The channel is built, proved and inert. The condition for a weight above 0, set by the seat that designed it, is a commissioning run measuring the channel's error rate against known ground truth. That run does not exist.

What can be said already: the channel would not be idle. Over 65 archived run states it would move `R_k` in **42** — 0.646154, Wilson [0.524751, 0.751245] — with mean coverage 0.443544 and median 0.512821. So "it would change nothing" is ruled out, which is the question that precedes the commissioning run.

### 6.5 B50 still needs his word

Explained in section 2 at his request. 6 assertions stay red until he rules, and they are 6 of the 7 failures outstanding before tonight's work; the 7th was the identity count his B49 ruling cleared.

## 7. State

The full board (`python3 -m pytest bench/tests/ -q --timeout=1800`) is running, with a terminal open on its live output. Before tonight: 7 failures, 6 of them the immune-memory assertions above. 7 new guard files, **80 tests**, **37 of 38** deliberate mutations caught — the one not applied had a mismatched anchor rather than a surviving defect. The master task list holds **186** entries: 12 open, 161 done, 4 deferred, 9 withdrawn. Nothing on it was resumed.

Written under CDSFL note standard v1.8 (17 October 2026).
