# Test-count and "non-network" claims: full correction list

2026-07-31, 19:35 BST.

## Verdict

**THE FIGURE DOES NOT HOLD, AND IT WAS NEVER TRUE.

"1255 tests (1121 non-network pass)" fails on both halves. The count is stale (2089 collected at 2026-07-31 19:09 BST, HEAD d4d4d7f + parallel-workflow working tree) and unstable (bench/tests/test_immune_memory_consumption.py parametrises over timestamped run directories under bench/logs/ — it collected 45 tests at 19:09 BST against 146 log directories, up from 18 at 18:20 BST; the total grows whenever anything archives). The "non-network" half is not stale — it is false, and was false on the day it was written.

HARD REFUTATION, not inference. The 907/907 "fast non-network sweep" (22 April 2026, commit 991cde0) is the one run whose exclusion list is on the record: test_openrouter_tools.py, test_deepseek_specialist.py, test_dynamic_management.py, test_ouroboros_query_quality.py, test_exp29_integration.py. Three test files that reach a live claude-CLI dispatch entry point existed on that date and are NOT in that list — bench/tests/test_immune_agents.py (created 2026-04-02, eeb7f40), test_specialist_live_promotion.py and test_specialist_shadow_cells.py (both created 2026-04-17, bdfc93a). None carried pytest.mark.network then or now. The 907/907 run therefore included live model dispatch by construction. The 1121/1121 run (21 April, 2fbedcd) has the same defect with a worse aggravation: its "six network-dependent test files excluded" are never named anywhere in the record, so the figure is not reproducible even in principle. Its 19m02s wall-clock for 1121 tests, against 276 s for 2058 tests with outbound calls denied, is the live-dispatch signature.

THE PROJECT WROTE THE CONTRADICTION DOWN AND DID NOT ACT ON IT. experimental_notes/CDSFL_Agent_Operational_Plan.md:278 (and its Desktop mirror), 22 April 2026 02:08 BST, states verbatim that test_exp29_integration.py "sits on the non-network code path despite doing real CLI dispatch". resources/ONBOARDING.md:359 states that the file "was authored ... for regression coverage of the real-dispatch path" and that "Its exclusion from the overnight fast-sweep is a pytest wall-clock decision ... not a statement that the file belongs to the Exp 40 arc." The correct response to both observations was to add pytest.mark.network. It was never added. The exclusion criterion in use was wall-clock, not network — and the record says so in its own words.

THE ROOT DOCUMENT DEFECT is pytest.ini:11-14. The marker's own registration text claims it denotes "model dispatch" and that such tests are "excluded from offline runs with -m 'not network'". Neither clause was ever implemented: 3 tests out of 2089 carry the marker, and none of the 62 tests measured making outbound calls is among them. Every "non-network" claim in the project leans on that line, and the line asserts a property the marker has never had.

THE REAL FIGURE. Two measurements exist and they are not the same measurement. Task 1 Run B (2026-07-31 18:35 BST, HEAD d4d4d7f + dirty tree, outbound calls denied with catchable errors so the application's own offline fallbacks engage): 2055 passed / 2058 selected / 3 failed / 3 deselected in 276 s. The uncommitted correction header now sitting at resources/RECOVERY.md:8-41 quotes a different figure — "2080 passed, 3 skipped, 0 failed in 109 s; 30 outbound attempts, all denied" at 18:57 BST — because that is a post-fix run with bench/tests/conftest.py, bench/live_dispatch_policy.py and HF_HUB_OFFLINE in place, not the pre-fix simulation. Both are real; they must not be conflated, and the header should say which is which. Collection has since drifted again to 2089.

WHAT FAILS ONCE THE NETWORK IS BLOCKED: nothing that matters. Zero of the 62 offenders asserts on live model behaviour. Every one passes offline. The three Run B failures are _target_to_query regressions in a parallel workflow's uncommitted edits to bench/ouroboros_cell.py (mtime 2026-07-31 18:32:52) — out of scope under the hard constraint, flagged for them.

SCOPE OF CONTAMINATION: 31 sites across 13 files, in three tiers. Tier 1 (false "non-network" label, or a count presented as current state): pytest.ini, resources/RECOVERY.md, resources/ONBOARDING.md, docs/CURRENT_STATE.md, docs/REPRODUCING.md, README.md, PAPER.md, the memory index and ce_state.md, plus five experimental-notes files and the Desktop tracker. Tier 2 (accurate dated history needing an annotation, not a rewrite): the per-experiment merge records in docs/EXPERIMENTAL_RESULTS.md and docs/FOUNDERS_NOTES.md. Tier 3 (the generator): scripts/cdsfl_sv.py:388 emits the undated, unqualified collection count into docs/CURRENT_STATE.md on every sv — every future stale number comes from that one line, so fixing the documents without fixing the generator buys nothing.

TWO SITES THE FOUNDER SHOULD RULE ON BEFORE ANYTHING ELSE. (1) docs/REPRODUCING.md:56-62 tells third parties to run `python3 -m pytest bench/tests/ -v` and says "All tests should pass" — a reader with a claude CLI and a Max subscription burns roughly 23 minutes of serialised model time and does not know it; a reader without one gets a silently different code path, because _active_llm_classify fails open at bench/immune_agents.py:5021-5022. That is the public reproducibility instruction and it is the worst single line in the set. (2) resources/ONBOARDING.md is the "read this first" document and has NO correction header, while RECOVERY.md now has one. Anyone onboarding reads the false figures first and the correction never.

NO FILES WERE EDITED. Report only.**

## How long the claim was wrong

IT WAS NEVER TRUE. There is no drift point, because there was no true period to drift from.

Git-verified timeline:

2026-04-02, `eeb7f40` — `run_immune_pipeline` created in bench/immune_agents.py; bench/tests/test_immune_agents.py created the same day. Live-dispatch reachability begins here.

2026-04-04, `440567d` — bench/tests/test_exp29_integration.py created. It already imports `run_immune_pipeline` at line 39 and calls `brain.run_immune_pipeline(...)` inside `test_three_round_flow`. `_get_claude_cli` is introduced in the SAME commit. The test file has carried the live-dispatch path since the hour it was written, and has never carried a marker.

2026-04-11, `1703ed1` — `_active_llm_classify` added: the fail-open Haiku classifier, `subprocess.run([claude, "-p", prompt, ...], timeout=15)` serialised under `_CLAUDE_CLI_LOCK`, returning `(None, 0.0)` when the CLI is absent (bench/immune_agents.py:5021-5022).

2026-04-17, `bdfc93a` — FIRST use of `pytest.mark.network` anywhere in the repo, 13 days AFTER the live-dispatch test path already existed. It was applied to ouroboros and OpenRouter tests. It was not applied to any of the five live-dispatch files. The same commit CREATES two more unmarked live-dispatch files, test_specialist_live_promotion.py and test_specialist_shadow_cells.py.

2026-04-21, `2fbedcd` — FIRST "non-network" pass-count in the record, in the commit subject line itself ("1121/1121 non-network tests pass") and in resources/RECOVERY.md:558 + resources/ONBOARDING.md:399. False on the day it was written. Same day, `be6d13a` writes "1255 tests (1121 non-network pass)" into MEMORY.md and ce_state.md.

2026-04-22, `991cde0` — the 907/907 "fast non-network sweep", whose exclusion list IS recorded and provably omits three live-dispatch files. The tracker entry written at 02:08 BST the same night states verbatim that test_exp29_integration.py "sits on the non-network code path despite doing real CLI dispatch". The contradiction is identified, written down, and not acted on.

2026-04-23, `7c9df2b` — resources/ONBOARDING.md:359 restates it: the file was "retained for regression coverage of the real-dispatch path" and its exclusion is "a pytest wall-clock decision ... not a statement that the file belongs to the Exp 40 arc." Second admission. Still no marker.

2026-06-09, `c865bd9` — pytest.ini created, registering the marker with text claiming it denotes "model dispatch" and that such tests are "excluded from offline runs with -m 'not network'". This CODIFIES the false property into the repo's configuration, 49 days after it was first known to be false. No marker is added to any dispatching test in this commit or since.

2026-07-12 — experimental_notes/CDSFL_Overnight_Phase1_2026-07-12.md:126 still writes "Full non-network suite: 1,595 passed".

2026-07-31 — measured. 62 distinct tests, 82 attempts, 5 external targets under hard block; 3 of 2061 deselected by the marker.

DURATIONS.
The written claim "non-network" has been wrong for 101 days, from 2026-04-21 to 2026-07-31, continuously, across at least 13 files.
The underlying condition — unmarked live model dispatch inside the default test suite — has existed for 118 days, since 2026-04-04.
The repo configuration asserting the false property (pytest.ini) has been wrong for 52 days, since 2026-06-09.

NO CHARITABLE READING SURVIVES. The strongest available defence would be that the six unnamed files excluded from the 21 April run happened to cover every live-dispatch path. It fails on three counts. (1) The very next day's sweep names its exclusions, and three live-dispatch files — test_immune_agents.py, test_specialist_live_promotion.py, test_specialist_shadow_cells.py, all present in the tree at commit 991cde0 — are not among them; nothing in the record characterises those three as network-dependent at any point. (2) The huggingface.co reachability via bench/dm/_similarity.py touches 35 tests spread across many files and could not be excised by a six-file list. (3) 19m02s for 1121 tests, against 276 s for 2058 tests with outbound calls denied, is not a wall-clock a hermetic run produces.

The claim did not decay. It was born false, was contradicted in writing twice within 48 hours of birth by the project's own notes, and was then hardened into pytest.ini seven weeks later.

## Sites — 24 require correction, of 32 audited

NO FILE BELOW HAS BEEN EDITED except `resources/RECOVERY.md`, which carries the
new offline-suite block and its own corrections. `README.md`, `PAPER.md` and the
`docs/` set are public-facing; amending a headline claim in them is the founder's
decision, not the orchestrator's. This file is the record to act from.

### `pytest.ini:14`

**Current**

> network: test makes real external network calls (arxiv, semantic_scholar, model dispatch); excluded from offline runs with -m "not network".

**Corrected**

> network: LEGACY MARKER — DOES NOT DEFINE THE OFFLINE SELECTION. Registered 2026-06-09 (c865bd9), first used 2026-04-17 (bdfc93a). It was applied to 3 tests out of 2089 and never to any of the 62 tests measured making outbound calls on 2026-07-31, despite this text naming "model dispatch". `-m "not network"` has never been an offline run. The suite is made offline by bench/tests/conftest.py (HF_HUB_OFFLINE, bench/live_dispatch_policy.py gating immune_agents._get_claude_cli(), and a socket/subprocess guard), not by this marker. Retained only to keep honestly-marked tests deselectable.

### `pytest.ini:5`

**Current**

> 300s is generous — the full non-network suite's slowest legitimate test is well under it — so this only ever trips on a genuine hang, converting it into a fast, reported failure instead of an indefinite block.

**Corrected**

> 300s is a backstop. It has in practice tripped on test_exp29_integration.py::test_three_round_flow, and not on a hang: on ~44 serialised 15 s live claude-CLI dispatches under _CLAUDE_CLI_LOCK — designed behaviour of an undeclared network dependency, not a deadlock. With outbound calls denied the whole suite completes in 109-276 s, so this timeout is now genuinely a hang detector rather than a live-dispatch budget.

### `resources/RECOVERY.md:558`

**Current**

> Branch: `exp39-experimental`. Non-network pytest subset 1121/1121 passing (19m02s); focused regression subset 249/249 passing (9m17s). Six network-dependent test files excluded because they depend on live API state and do not exercise the code paths touched this session.

**Corrected**

> Branch: `exp39-experimental`. Pytest subset 1121/1121 passing (19m02s); focused regression subset 249/249 passing (9m17s). [CORRECTION 2026-07-31: this was NOT a non-network run. Six files were excluded by hand; they are not named anywhere in the record, so the figure is unreproducible. pytest.mark.network was not the selector and covered 3 tests. Test files reaching live claude-CLI dispatch — test_immune_agents.py, test_specialist_live_promotion.py, test_specialist_shadow_cells.py — all existed on this date, carried no marker, and were on no documented exclusion list. The 19m02s wall-clock against 276 s for 2058 tests with outbound calls denied is the live-dispatch signature. This entry is historical record; do not quote it as reproducibility evidence.]

### `resources/ONBOARDING.md:399`

**Current**

> Branch: `exp39-experimental`. Non-network pytest subset 1121/1121 passing (19m02s); focused regression subset 249/249 passing (9m17s). Six network-dependent test files excluded because they depend on live API state; they do not exercise the code paths touched this session.

**Corrected**

> Identical correction to resources/RECOVERY.md:558. Drop the words 'Non-network' and 'network-dependent'; the exclusion was hand-curated and its file list was never recorded.

### `resources/RECOVERY.md:534`

**Current**

> Test count grew from 1255 to 1311 (56 new tests across five new test files). **All 56 new tests pass in 2.33 s.** Fast non-network sweep excluding five long-running or CLI-blocking files (`test_openrouter_tools.py` 36, `test_deepseek_specialist.py` 29, `test_dynamic_management.py` 283, `test_ouroboros_query_quality.py` 11, `test_exp29_integration.py` 44): **907/907 pass in 342.12 s**, zero failures.

**Corrected**

> Test count grew from 1255 to 1311. All 56 new tests pass in 2.33 s. Fast sweep excluding five long-running or CLI-blocking files [named list retained]: 907/907 pass in 342.12 s. [CORRECTION 2026-07-31: the label 'non-network' is false and the exclusion criterion was wall-clock, not network. Three live-dispatch test files existed on this date and are absent from the five-file list — test_immune_agents.py (eeb7f40, 2026-04-02), test_specialist_live_promotion.py and test_specialist_shadow_cells.py (both bdfc93a, 2026-04-17). This sweep made live claude-CLI Haiku calls.]

### `resources/ONBOARDING.md:378`

**Current**

> Fast non-network sweep excluding five long-running or CLI-blocking files (`test_openrouter_tools.py`, `test_deepseek_specialist.py`, `test_dynamic_management.py`, `test_ouroboros_query_quality.py`, `test_exp29_integration.py`) returns **907/907 pass in 342.12 s** with zero failures.

**Corrected**

> Same correction as resources/RECOVERY.md:534. Strike 'non-network'; the criterion was wall-clock. Three unlisted live-dispatch files were included in the run.

### `docs/CURRENT_STATE.md:26`

**Current**

> **1638 tests collected** (`python3 -m pytest bench/tests/ --co -q`)

**Corrected**

> **2089 tests collected** at 2026-07-31 19:09 BST, HEAD `d4d4d7f` + uncommitted working tree (`python3 -m pytest bench/tests/ --co -q`). NOTE: the collected total is not stable — `bench/tests/test_immune_memory_consumption.py` parametrises over timestamped run directories under `bench/logs/` (45 tests against 146 directories at this reading) and grows whenever an experiment archives. Collection count is not a pass count and says nothing about whether the run is offline.

> **[This proposed wording was itself REFUTED, 2026-07-31.]** `test_immune_memory_consumption.py` does NOT parametrise over timestamped run directories — its `_RUNS` is a hardcoded list of six named directories. The collected total does drift, but because tests are being added (2089 to 2102 within ninety minutes that evening), not because collection is data-dependent. The wording actually applied to `docs/CURRENT_STATE.md` reflects the corrected reason.

### `scripts/cdsfl_sv.py:388`

**Current**

> lines.append(f"**{tests} tests collected** (`python3 -m pytest bench/tests/ --co -q`)")

**Corrected**

> Emit the count bound to a commit and a timestamp, and state the instability, e.g. f"**{tests} tests collected** at {ts}, HEAD `{sha}` (`python3 -m pytest bench/tests/ --co -q`). Collection is parametrised over `bench/logs/` run directories and is not a fixed number; this is a collection count, not a pass count."

### `docs/REPRODUCING.md:59`

**Current**

> Run the test suite to verify the codebase:
> 
> ```bash
> python3 -m pytest bench/tests/ -v
> ```
> 
> All tests should pass. If any fail, check the error messages for missing dependencies or environment issues.

**Corrected**

> Run the test suite to verify the codebase:
> 
> ```bash
> python3 -m pytest bench/tests/ -q
> ```
> 
> The suite is offline by default (bench/tests/conftest.py sets HF_HUB_OFFLINE, gates immune_agents._get_claude_cli() via bench/live_dispatch_policy.py, and guards sockets/subprocesses). Add `--netguard-strict` to fail any test that merely ATTEMPTS an outbound call. To exercise the live model path deliberately, and only then: `CDSFL_ALLOW_LIVE_DISPATCH=1 python3 -m pytest bench/tests/`. WARNING for reproducers on any build predating 2026-07-31: this command dispatched ~93 live claude-CLI calls serialised under a 15 s timeout — up to ~23 minutes of billed model time — and on a machine without the CLI took a silently different code path, because _active_llm_classify fails open at bench/immune_agents.py:5021-5022.

### `README.md:534`

**Current**

> *CDSFL. 20 April 2026. Fundamentalist open source under the MIT License. Forty experiments on the record; 1250 bench tests passing; a mathematical appendix under iterative extension at 1991 lines.*

**Corrected**

> *CDSFL. Fundamentalist open source under the MIT License. Forty-nine experiments on the record; 2089 bench tests collected and 2055+ passing offline as of 2026-07-31 at HEAD `d4d4d7f`; a mathematical appendix under iterative extension.* — and drop bare pass-counts from the strapline entirely, or bind every one to a date, a commit, and the command that produced it. The 1250 figure came from a full-suite run that made live model calls and is not a hermetic reproducibility figure.

### `PAPER.md:11`

**Current**

> Experiment 40 Stage 3 closed the integration test at 1250/1250 tests passing.

**Corrected**

> Experiment 40 Stage 3 closed the integration test at 1250/1250 tests passing at commit `6580737` (18 April 2026). [Qualification required: that run was the full suite with no offline selection and included live model dispatch — the 20 min 23 s wall-clock is the signature. It is a record of the suite's state, not a hermetic reproducibility figure. The suite was made offline on 2026-07-31; the current figure is 2055 passing of 2058 selected with outbound calls denied.]

### `docs/EXTENDED_RATIONALE.md:181`

**Current**

> The test suite stands at 1250 tests passing.

**Corrected**

> At commit `6580737` (18 April 2026) the test suite stood at 1250 tests passing, in a full-suite run that included live model dispatch. As of 2026-07-31 at HEAD `d4d4d7f` the suite collects 2089 and passes 2055 of 2058 selected with outbound calls denied.

### `docs/FOUNDERS_NOTES.md:727`

**Current**

> The full suite stands at 1,250 passing tests in twenty minutes of wall-clock.

**Corrected**

> At the Experiment 40 launch gate the full suite stood at 1,250 passing tests in twenty minutes of wall-clock. [2026-07-31: those twenty minutes were largely live claude-CLI Haiku dispatch, serialised at 15 s per call under _CLAUDE_CLI_LOCK, not test execution. With outbound calls denied a larger suite completes in 109-276 s.]

### `/Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md:18`

**Current**

> - [Current State](ce_state.md) — 1255 tests (1121 non-network pass). Exp 40 pre-launch CLOSED 21 April: F1/F2/F3 landed + K/L/M shadow-audit enriched. Round 2 plan review closed via compelled convergence. HEAD 2fbedcd.

**Corrected**

> - [Current State](ce_state.md) — 2089 tests collected, 2055/2058 passing offline (2026-07-31, HEAD d4d4d7f + dirty tree). The earlier '1255 tests (1121 non-network pass)' figure is RETRACTED: '-m "not network"' was never an offline selection and that run made live model calls. Collected totals drift (test_immune_memory_consumption.py parametrises over bench/logs/ run directories).

### `/Users/georgejackson/.claude/projects/-Users-georgejackson-Developer-Projects/memory/ce_state.md:23`

**Current**

> - **1311 tests collected** on branch `exp39-experimental` (pre-sv, working tree dirty). Pre-shift baseline was 1255 collected / 1121 non-network pass; ... Fast non-network regression sweep (excluding five long-running or CLI-blocking files ...) returned **907/907 pass in 342.12 s**, zero failures.

**Corrected**

> Strike both instances of 'non-network'. The 1121 run's exclusion list was never recorded; the 907 run's list is recorded and provably omits three live-dispatch files (test_immune_agents.py, test_specialist_live_promotion.py, test_specialist_shadow_cells.py). Replace the headline with the current measured figure and bind it to date + commit + command.

### `experimental_notes/CDSFL_Agent_Operational_Plan.md:278`

**Current**

> ...907 collected, **907/907 pass in 342.12 s** (5m 42s), exit code 0, zero failures. The test_exp29_integration.py::test_three_round_flow hang reproduced under a dedicated 120 s run — confirmed hanging on `Claude CLI Haiku` LLM classifier invocations (14.4 s per call, 3 rounds × N findings per round) plus the fact that it sits on the non-network code path despite doing real CLI dispatch.

**Corrected**

> Keep the sentence verbatim — it is the project's own contemporaneous statement of the defect — and append: [2026-07-31: this observation, recorded 22 April 2026 02:08 BST, identified the exact contradiction. No pytest.mark.network was added in response, and 'non-network' continued to be applied to sweeps for a further 99 days. The 907/907 sweep itself included three unmarked live-dispatch files.]

### `experimental_notes/CDSFL_Agent_Operational_Plan.md:235`

**Current**

> - [x] **E1.** Full pytest regression run post-changes. **Result:** ... fast non-network sweep excluding five long-running or CLI-blocking files ... returns 907/907 pass in 342.12 s. Zero regressions.

**Corrected**

> Strike 'non-network' — the criterion was wall-clock. Same correction as resources/RECOVERY.md:534.

### `experimental_notes/CDSFL_Agent_Operational_Plan.md:279`

**Current**

> E2 (ce_state update) — `memory/ce_state.md` line 16 updated with the final pass counts (56/56 new, 907/907 fast non-network) and the pre-existing-hang provenance note replacing the "TBD at sv" placeholder.

**Corrected**

> Strike 'non-network' from the parenthetical.

### `experimental_notes/CDSFL_Agent_Operational_Plan.md:765`

**Current**

> Pre-continuation test count was 1255 (1121 non-network pass); the continuation did not run additional tests.

**Corrected**

> Pre-continuation test count was 1255 collected, 1121 passing in a hand-curated subset that was NOT offline; the continuation did not run additional tests.

### `/Users/georgejackson/Desktop/CDSFL_Agent_Operational_Plan.md:278`

**Current**

> Byte-mirror of experimental_notes/CDSFL_Agent_Operational_Plan.md — same wording at lines 235, 278, 279, 765.

**Corrected**

> Apply the identical corrections at all four lines. This is the CANONICAL copy per operational-tracker-cdsfl and the first document read after compaction, so it must not be left behind the repo mirror.

### `experimental_notes/Exp40_PreLaunch_State_Post_Hiatus_2026-05-09.md:18`

**Current**

> | Fast non-network sweep | 907/907 pass in 342.12 s |

**Corrected**

> | Fast wall-clock-limited sweep (NOT offline — included live claude-CLI dispatch) | 907/907 pass in 342.12 s |

### `experimental_notes/Exp40_PreLaunch_Gap_Closure_Overnight_2026-04-22.md:99`

**Current**

> Total collected post-shift: 1311 (pre-shift 1255 plus 56 new). The full non-network regression run is in progress at note-write time; the expected pass count is at least 1171 (pre-shift 1121 plus 56 new)...

**Corrected**

> Strike 'non-network'; the run in progress was not offline. Note also that the projected 1171 was never confirmed by a recorded result — the note asserts an expectation that no later entry closes.

### `experimental_notes/CDSFL_Overnight_Phase1_2026-07-12.md:126`

**Current**

> Full non-network suite: 1,595 passed, 3 failed.

**Corrected**

> Full suite: 1,595 passed, 3 failed. NOT a non-network run — `-m "not network"` deselected 3 tests of ~1,600 and excluded no live-dispatch path.

### `experimental_notes/Convergence_Consolidation_Plan_2026-06-08.md:212`

**Current**

> **199 runner/convergence/config tests pass; full non-network suite running.**

**Corrected**

> **199 runner/convergence/config tests pass; full suite running (not offline — see the 2026-07-31 test-suite offline correction).**

## Audited and found correct — 8

- `resources/ONBOARDING.md`
- `resources/RECOVERY.md`
- `PAPER.md`
- `PAPER.md`
- `docs/FOUNDERS_NOTES.md`
- `docs/FOUNDERS_NOTES.md`
- `docs/EXPERIMENTAL_RESULTS.md`
- `bench/tests/test_ouroboros_realwork.py`

---

Written under CDSFL note standard v1.2 (14 May 2026).