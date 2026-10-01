# Green table, and the claim channel is on

1 October 2026, afternoon, British Summer Time (UTC+1). Branch `sim/shakedown-2026-09-29`.

Technical record. A plain-English companion is filed as `Green_Table_And_The_Claim_Channel_Plain_English_2026-10-01.md`, and the text-to-speech version as `Green_Table_And_The_Claim_Channel_2026-10-01.txt`.

## What this closes

The clean full-suite run of 2026-10-01 02:15 BST finished at **20 failed, 9200 passed, 7 skipped** at `450bb1d`. All 20 are now closed. Every previously-red file passes: **698 tests** across the set, with `test_operational_scripts.py` alone at **524 of 524** (it carried 9 of the 20).

**THE TABLE IS GREEN. The final full-suite run on a genuinely frozen tree gave `9375 passed, 8 skipped, 0 failed in 3217.53 s (53:37)`**, with 49 outbound attempts across 21 tests all denied under strict netguard.

It took 4 runs to get there and 2 of those were spent on 1 test. The second run gave 2 failed / 9373 passed; both causes were found and fixed. The third was **voided by CC1 editing the tree while it ran** — the single failure was the guard that snapshots `git status`, blaming the measurement survey for a change CC1 had made between its 2 snapshots. 4 of 480 test files read `git status --porcelain`, 0.8333%, Wilson [0.3245%, 2.1229%]; one grep would have found all 4 before the edit. The skip count rose from 7 to 8, which is the grep blind-spot guard standing aside in a shell where the search wrapper's backend is unreachable, exactly as designed.

Landing the day's own work tripped **7 further guards, every one of them a documentation-parity or instrument-fragility guard, and every one mine**:

- The Desktop mirror of `CDSFL_MASTER_TASK_LIST.md` drifted when the A7 entry changed (2 guards). Re-synced with `scripts/sync_desktop_mirrors.py`.
- `resources/MEMORY_EXCLUSIONS.md` stated 158 memory files against 163 on disk. Corrected to 163, mirrored 101 to 106 — **the 10th consecutive manual correction to a figure the 2026-08-17 remedy said should be derived inside `sv` rather than typed.**
- `MEMORY.md` breached both the 150-character pointer rule (3 entries at 171, 162 and 160) and the 190-line headroom (192 lines). The 5 new entries are now 1 date-grouped line; the index is 188 lines.
- Two synthetic probe strings in the Wolfram test parsed as `file:line` citations naming files that do not exist. Renamed to basenames the citation guard's own `PLACEHOLDER` pattern already recognises, rather than widening a project-wide allowlist.
- The source-text-assertion census hit **81 against a ratchet of 80. Exactly 2 were mine**, and both are now structural `ast` checks — which is what the census exists to push toward, its own docstring recording that 4 guards of that class broke on correct changes in a single day. Census now **79**, none mine.
- `test_shell_grep_blind_spot`'s strict divergence test asserted `seen < real` while **inferring its precondition from the inequality under test**, and the cause took two attempts to find. **The first hypothesis was wrong and is recorded so it is not retried:** that the suite's own creation and deletion of git-ignored files removed what the wrapper had to hide. That gate measured **910** ignored matches, never fired, and the test failed again — the failure message refuting the hypothesis outright, since `1159 against 1159 with 910 ignored matches present` is a wrapper doing nothing, not a population with nothing to hide.

  **The real cause: the wrapper is not self-contained.** Its body execs the Claude Code binary as `ugrep`, and `if [[ ! -x $_cc_bin ]]; then command grep "$@"; return; fi` — so when that backend is unreachable it *silently* becomes plain grep. `CLAUDE_CODE_EXECPATH` is exported into the agent's environment and is **UNSET in the operator's login shell**, where the fallback `$HOME/.local/bin/claude` does not exist either. **Measured in both shells: agent 911 against 1159; login shell 1159 against 1159.** Every targeted re-run was launched by the agent and passed; both full-suite runs were launched from the terminal and failed. **The variable is which shell started pytest** — never suite context. Reproduced directly by pointing `CLAUDE_CODE_EXECPATH` at a missing path, which turns 911/1159 into 1159/1159. The gate now probes backend reachability and **skips** where the divergence cannot exist; verified in both directions, and the unconditional `seen <= real` invariant still runs either way. When the wrapper does work it hides **248 of 1159 files, 21.3978%**, Wilson **[19.1332%, 23.8513%]** on statsmodels and mpmath agreeing to 2.8e-17.

The four items the founder marked for fixing, the round-cap ruling's unbuilt half, the claim-level channel, and the external-model input are all addressed below.

## The dominant cause was not a regression

**Six of the twenty failures were one fault: a dated measurement compared against an archive that has since grown.** Nothing was broken in any of the six.

| Guard | Symptom | Fix |
|---|---|---|
| `e1_population_recount_falsifier_2026-09-22.py` | demanded 265/50 where the docstring says 124/23 | `CLAIM_SCOPE = ("20260921", "20260922")`; whole-archive figure printed, asserted on nothing |
| `test_a7_predicate_family_is_quoted_2026-09-17.py` | entry quoted `{20, 22, 34}`, producer computed `{20, 22, 35}` | entry updated; scope-checked |
| `test_latent_tagger_evaluation.py::TestArchiveExposure` | 17 tagged against 16 pinned | marker misfire fixed, pin unchanged (see below) |
| `test_panel_audit_producers_2026-09-22.py` (×2) | pinned figures over 7 arms instead of 4 | both producers scoped; 2 anti-drift tests added |
| `test_panel_conditions_are_met_2026-09-10.py::TestP5…` (×2) | 114 of 117 replies | pattern widened (see below) |

**The arithmetic that settles the class.** `e1_mechanism_consequences_2026-09-22.py`'s docstring names its own population: *"Across the 4 commissioning arms of 2026-09-21/22, 124 proposed fixes carry a fix-efficacy probe result. 23 of them are `FIX_DOES_NOT_CURE_ITS_OWN_FALSIFIER`."* Per-run, cross-verified on SymPy and mpmath:

- claim scope: 69 + 9 + 30 + 16 = **124**; 16 + 3 + 2 + 2 = **23**
- later arms: 42 + 58 + 10 + 17 + 14 = **141**; 12 + 8 + 3 + 4 + 0 = **27**
- whole archive: **265** and **50**

23/124 = **18.5484%**, Wilson **[12.6898%, 26.2972%]** — the docstring's own interval to 4 decimal places. The claim was never wrong; the denominator drifted. `scripts/morning_report_figures_2026-10-01.py` and the scoped producers reproduce every figure.

**A7's scope check confirms the diagnosis independently.** Restricting `escalation_paths_2026-09-11.py` to runs archived before 2026-09-17 reproduces `{20, 22, 32}` exactly — the family recorded in that date's withdrawal. The two severity-filtered members, 20 and 22, have never moved; only the unfiltered member tracks archive size.

## Three real defects

1. **`scripts/fence_extractor_dominance_2026-09-30.py:76`** put a backslash inside an f-string expression — legal from Python 3.12, a `SyntaxError` on 3.11. `test_python_floor_2026-09-07.py` holds the floor at 3.11 because a module that will not *parse* stops the suite *collecting*. Label hoisted into a `CRLF` constant; verified parsing on 3.11 and still measuring on 3.13 (dominance intact, B-only = 0).

2. **`experimental_notes/Morning_Report_2026-09-30.md`** carried 7 percentages and a p-value with no artefact. `scripts/morning_report_figures_2026-10-01.py` now reproduces all of them from `bench/logs/commissioning_arm1_panel_20260929T{194414,214647}Z/runner_state.json` and the arm-4 prose catalogue, each rate with Wilson and Clopper-Pearson intervals and the Wilson recomputed in mpmath at 50 dps (agreement 2.2e-16). Rebuilding surfaced two under-specifications, both corrected in place:
   - `p = 0.0040` is the **one-sided** Mann-Whitney; two-sided is **0.0079**. The one-sided form is quoted because the repair was predicted in advance to lower rho.
   - "12 of 12 findings … no test verdict" is true but the round catalogued **15**; 3 closed with a `CONFIRMED` verdict. The 100.0000% is the rate among findings that *reached the queue*, not among all findings in the round.
   - The "7 of 13 defects, 53.8462%" attribution is a **hand enumeration** with no artefact. Its interval arithmetic reproduces; the inputs cannot be rebuilt, and the note now says so.

3. **`bench/latent_tagger.py`'s `no_caller` marker** tagged `commissioning_arm4_prose_20260930T064044Z/C0014` latent on the phrase *"with no caller override"*, where "caller" qualifies "override" and the sentence states the defect. `latent` feeds demotion eligibility; checked, nothing was demoted on it. Tightened with a negative lookahead refusing a following modifier noun. **Measured over every registry entry in `bench/logs`: 1 lost (that false positive), 0 true positives lost** — so `PINNED_PROSE_TAGGED` returns to the 16 already pinned rather than being loosened around a wrong tag. 12 tests added (43 → 55). This is explicitly **not** the class fix: `TestFalseLatentExposure` records 9 further mention-not-assertion cases and reserves retiring the prose source to the founder.

## Two guards were wrong about working code

**`test_precommit_guard_2026-09-09.py`** asserted `core.hooksPath == "hooks"`. It holds the absolute path to the same directory; `hooks/pre-commit` is present and executable and the gate has been refusing commits all day. Now judged by **resolution** plus an executable-hook check; `cdsfl_onboard.py:1041` carried the same spelling comparison and would have rewritten a correct absolute path on every run. A comment claiming a relative path is unsafe was **measured and found false** — on git 2.50.1, committing from a subdirectory of a throwaway repo ran the hook under both spellings — and removed before shipping.

**`test_wolfram_is_enabled_not_denied_2026-09-29.py`** flagged 3 transient agent worktrees under `.claude/worktrees/wf_*`, which carry copies of the two exempt files while the exemptions are absolute prefixes. Nothing was pinned to deny. Exclusion follows the project's existing `_SKIP_DIRS` / `_NOT_THE_PROJECT` convention. Fixing the scope exposed a real hole: the pattern required the separator to follow the name directly, so it missed both spellings anyone would commit — `env["CDSFL_WOLFRAM_POLICY"] = "deny"` and a JSON pair. Widened (not so far as to match a prose mention), predicate extracted to `_deny_pins` with 3 tests.

## Section P: disagreement was stated, not sectioned

The pattern's section alternative is line-anchored, so a disagreement stated mid-sentence was invisible. Two replies complied in full:

- fable, `intelligence_first_2026-09-30`: *"Disagreements with CC1 (verdict vocabulary; stage reading) and the earlier seat (Wolfram parallel) are preserved in the note with the evidence that decides each."*
- fable, `a19_calculator_design_2026-09-30`: *"## Q4 — … And CC1's invariance claim is correct but incomplete — my named disagreement."*

Both briefs asked for the field twice (lines 14 and 78). **Widened: 4 gained, 0 lost over all 306 archived seat replies**, and 2 of the 4 are July/August under-counts, so the guard had been under-reporting for months. It deliberately stops short of a bare `disagreement with`, which also matched *"a model's disagreement with a CONFIRMED finding would vanish"* — a mention, not an assertion.

**One genuine shortfall, recorded in `bench/directives/universal/section_p_shortfalls.json`.** cc2 on `a19_calculator_design_2026-09-30`: 4235 chars, ok, 157 tool calls, complete, **0 occurrences** of disagree/disagreement/dissent/diverge. It did refute the brief — *"the brief's '73 of 73' is a hardcoded literal … the live deduplicated count is 201"*, a refutation the project accepted and acted on — filed under "Two corrections I owe". A shortfall of **form**, stated as such. The entry also records that the round's blind parallel design makes "disagreement with the other seat" unanswerable; three options are left to the founder.

## The four named fixes

**1. The catalogue record says whether the fix worked.** `export_finding_catalogue` carried `demonstrated` and `falsifier_verdict`, both about the defect. `bench/fix_efficacy.py` gains `OUTCOME_MEANINGS`, `CONCLUSIVE_OUTCOMES`, `ALL_OUTCOMES`; the record gains `fix_efficacy_outcome`, `fix_efficacy_meaning`, `fix_efficacy_measured` and `fix_cured_its_falsifier`. The last is **tri-state** — `True` / `False` / `None` — because a boolean merges "the fix failed" with "the instrument could not look". On `commissioning_arm1_panel_20260921T215405Z`: 69 of 69 entries carry efficacy data, split 25 / 16 / 28, and **16 of 69 are `CLOSED` with `demonstrated=True` while the fix was measured as not curing its own falsifier**. 12 tests.

**2. Confinement is no longer tool-asymmetric.** `panel_sandbox.confine()` wraps the seat in a `sandbox-exec` profile denying writes to the canonical subpath; wired at `experiment_11_orchestrator.call_claude_cli` and recorded per attempt as `write_confinement`. Six properties measured by execution: write inside the copy **allowed**; new file and append in the canonical tree **denied**; `git config --local` there **denied**; reading **allowed**; SymPy/NumPy and HOME writes **allowed**. Targeted rather than global because a global deny broke the CLI's own state. Degrades to a reported absence on hosts without `sandbox-exec`. 11 tests, each attempting a real escape.

**3. `_MD_PY_FENCE` removed, under the removal clause.** Zero callers. `scripts/md_fence_orphan_dominance_2026-10-01.py` measures recognition over 560 shapes: orphan 14, live 224, **orphan-only 0**, Wilson **[0.0000%, 0.6813%]** (statsmodels and mpmath agreeing to 2.6e-18), and the live pattern reaches **210** shapes the orphan could not — dominance is proper. The pattern survives as a literal in the test that proves it redundant, re-derived each run.

**4. Harvest stranding repaired at source.** 251 seat `.py` files across 22 rounds, **251 of 251 git-ignored**, **46 of 251 = 18.3267%** (Wilson [14.0302%, 23.5781%]) reachable from no clone, over 11 rounds. `panel_sandbox.preserve_seat_evidence`, called from `harvest()`, copies every seat-written file with no tracked counterpart to `experimental_notes/seat_evidence/<round>/<seat>/` with provenance and the pre-header sha256. Edits to tracked files are **not** duplicated (144 of 251; that path staged 47 MB of byte-identical copies when tried), and `.scratch/` is excluded. Ratchet: `seat_evidence_stranding_baseline.json` is shrink-only and any round not listed must have zero. 21 tests across two files.

## The round cap

The ruling's second half was unbuilt: the recommendation named no number and there was no way to set a cap. `suggested_cap()` derives a **floor** from the gate — `max_rounds + gamma_alt_consecutive_zero_crit` — giving **11** for the 8-round arm, and says plainly it is not a prediction, because round count is not estimable on this archive. `--rounds N` (always wins, never blocked) plus an attended prompt; `_is_attended()` refuses to prompt on a detached or print-only run, since a prompt in a detached run is a dead run. Default 10. 14 tests.

## The claim channel

`bench/claim_ledger.py`, wired into the run report, informative-only. Four pieces, all the seats' design: a ledger per target; decidable claims into the existing verify path; undecidable claims **routed**, never discarded (routing is set in `__post_init__`); file-level admissibility as a **three-valued aggregate** — `claim-addressable` / `routed-only` / `no-decidable-claims`, the last being the only state that corresponds to "genuinely non-computable" and attaching to the absence of *claims*, not of fences. `compute_sk` untouched; `Claim.__post_init__` **raises** on an invented verdict, which directly guards against repeating `INADMISSIBLE`.

Populated from registry entries, so it fills on the next simulated run with no brief change. On `commissioning_arm4_prose_20260930T064044Z`, where `_gateable_source` returns `None` and `compute_sk` returns `NO_SCORE`: **15 claims, 8 decidable, 3 decided, 7 routed, 0 discarded.** The report carries a `not_covered` field stating that v1 records claims the seats *stated* and does not test whether a REASON stage surfaces *unstated* claims — the recommending seat's own strongest self-refutation.

**Near-miss.** The wiring first read `cfg.target_file`; `RunnerConfig` has no such field, so it would have raised, been swallowed by the section's exception guard, and silently disabled the channel on every run behind a plausible `{"written": false}`. Now reads `result["target_file"]`; the test **parses** the runner for a live `cfg.target_file` access rather than grepping (the first version matched the explanatory comment).

## External input, and the classifier question

**Grok brought two things, neither needing a panel round.** The non-stationarity argument is structural and stronger than the panel's data argument: after round 0 the state determining remaining rounds is the document *plus* applied fixes, open challenges and examination history, so a cap fitted to pre-run complexity predicts from a state that no longer exists. Recorded beside the cap reasoning. Its second item — *"always record which reason fired"* — was checked and **was a real gap**: `brain.state.stop_reason` is set on every exit path with a fallback naming an unrecorded stop, and the report carried no stop field. `stop_reason_fields()` now supplies `stop_reason` and `stop_reason_recorded`; 10 tests.

**The labelled set exists.** `scripts/claim_classifier_labelled_set_2026-10-01.py`: 15 documents, 10 positive (5 corpus fixtures, intact and fence-stripped), 5 opinion-prose negatives. Status quo (`_gateable_source`): accuracy **10/15 = 66.6667%**, sensitivity **5/10 = 50.0000%** Wilson **[23.6593%, 76.3407%]**, specificity 5/5. It misses every prose variant.

**The composability answer, and its limit.** Composing with an anchor-based claim check recovers all 5. But the anchors come from the corpus's own claim lists — the answer key — and the arm returns `False` on an unseen document, verified by giving it one. So 15/15 is a lookup's score, not a classifier's, and the composition cannot answer whether a cheap model finds claims in documents it has not been given answers to. That needs a model arm on withheld labels, which costs seat dispatches; `--emit-model-set` prepares it with labels in a separate file. 11 tests.

**A gap in the record:** the recalled Haiku reliability measurement is not in the repository. Haiku is named as the v2 classifier at `docs/ARCHITECTURE.md:93`; no committed script measures its agreement and no figure for it appears in the docs, resources, notes or project memory.

## Open for a ruling

1. Section P semantics where a seat genuinely agrees, and the object of "disagreement" in a blind parallel round.
2. Whether to spend free-seat dispatches on the classifier model arm; whether the Haiku measurement exists outside the repository.
3. Which of the 46 backlogged stranded files to rescue (the `.scratch/` ones should stay unpreserved).
4. Confirmation that the claim channel stays informative-only until a commissioning run measures how often it is wrong against the corpus's known ground truth.
5. Disposition of the 16 findings closed with a measured non-curing fix, now visible in the export.
6. `bench/logs/exp36_evidence_latest` is a symlink traversed by `registry_entries()`, yielding 217 ids twice. It affects none of today's figures and was left alone because fixing it could move archived numbers.
7. A7's hand-maintained family figure will drift again; the alternative is a dated scope, as the other five guards now have.

Written under CDSFL note standard v1.7 (26 August 2026).
