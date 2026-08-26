# CDSFL Agent Operational Plan

**Audience.** AI agent self-consumption. Terse, actionable, and dynamically updated. Not a human-facing narrative. If a reader is looking for prose explanation, see the detail plan under "Canonical anchors" below.

**Function.** Authoritative operational tracker for the Exp 40–54 arc and the subsequent Bench Run 2 (27 frontier STEM problem sets). First resource to read after any compaction or long break.

**★ TEST-SUITE FIGURES IN THIS FILE ARE CORRECTED (2026-07-31). READ BEFORE QUOTING ANY PASS COUNT.** Every "non-network" label recorded below is false. `-m "not network"` was never an offline selection: the `network` marker was not registered until 2026-06-09 (`c865bd9`) and tags 3 tests out of ~2089, none of them a model-dispatch path. The 1121 and 907 figures came from hand-curated file-exclusion lists chosen on wall-clock, and those lists omit three files that reach live claude-CLI dispatch — `test_immune_agents.py`, `test_specialist_live_promotion.py`, `test_specialist_shadow_cells.py`. Those runs made billed live model calls. Corrections are appended in-place at the four sites below (Phase E item E1, and the 22 April 02:08 / 02:10 entries, and the 15 May waking-review context) rather than overwriting them, because this file is a record. **Current measured figure:** `python3 -m pytest bench/tests/ -q --netguard-strict` → **2086 passed, 3 skipped, 0 failed in 99.6 s**, 30 outbound attempts all denied, measured 2026-07-31 19:15 BST at HEAD `d4d4d7f` plus working tree. The suite is now offline by default via three mechanisms in `bench/tests/conftest.py`. Full account: `resources/RECOVERY.md`.

**★ DETACHED-LAUNCH RULE (founder directive 2026-07-29, standing).** ALL experiment runners + panel dispatches launch via `bench/detached_launch.sh` (nohup+disown, PPID 1) so they survive Claude-Code host restarts — harness-tracked background tasks die with the host (proven: the 01:37 restart killed the tracked Exp 47 runner; the detached physics review survived and completed). Monitors are attention-window tools: re-arm on wake by tailing the run log named in this tracker. PID files sit beside logs (`/tmp/exp47_launch_20260728.pid` etc.). Exp 47 RESUMED detached 01:47 (PID in pidfile; checkpoint-resume guard validated round 5 coverage). The run itself is CDSFL LLM-reliability work exclusively; all component names are analogy only.

**★ RESUME POINTER (2026-08-26 02:40 BST). SUPERSEDES EVERY POINTER BELOW.**

**SIX DECISIONS SIT WITH THE FOUNDER.** Full statement with options and one recommendation each: `experimental_notes/Decisions_Awaiting_The_Founder_2026-08-26.md` (+ Desktop TTS `CDSFL_tts/Decisions_Awaiting_The_Founder_2026-08-26.txt`). Summarised: (1) permission to rewrite branch history to purge the exp55 key blob — **18 of 59 commits are cited by hash in markdown and would need remapping**; this environment refuses `git filter-branch` without an explicit instruction; (2) merge to `main` or push the branch — **public main is 59 commits behind and the branch has NEVER been pushed**; (3) who authors exp55's replacement target AND exp52's planted set; (4) the two approved panel dispatches, unrun because they spend money and produce output needing a rested reader; (5) merge semantics / Bugzilla; (6) archive decryption instructions, held for a message of their own, LAST.

**★ exp55's TARGET IS SPENT — see rule 2 below.** Its answers were on public `main` from `bd9c569`, 2026-08-20 01:21 BST, three days before both runs. Keys now live OUTSIDE any git tree in `../CDSFL_experiment_keys/`. A re-run needs a NEW target.

**★ THE RENUMBER WAS NOT DONE, AND SHOULD NOT BE.** Measured: experiment number is already **perfectly monotonic in start time across all 44 non-empty run directories, 0 violations**. The three apparent exceptions are EMPTY directories from aborted 2026-08-07 re-invocations. Renumbering would rename 56 directories and sever every doc reference, since the directory name AND the report filename both embed the number. What IS wrong: four numbers never ran (50/51/52 have configs, 54 has none), and status is recorded twice and disagrees (**20 of 31 completion signals carry an EMPTY reason; 7 of those have a report that names the outcome the signal lost**). Derived, never typed: `python3 scripts/experiment_run_ledger.py --check`.

**★ SCALING HAS A NUMBER NOW.** Measured inter-architecture correlation **rho = 0.564 across 289 observations in 31 run directories**. At that rho the 5th architecture contributes **3.6%** of the 1st, and going 5 -> 50 architectures gains **+0.002 to +0.005** coverage across every plausible p. n* lands in **3-6**, which DERIVES the saturation figure the parking lot carried as an observation. Spec: `experimental_notes/Scaling_Spec_GlobalMind_2026-08-26.md`. Panel size is not the scaling axis; rho and artefact-count are.

**★ CORRECTED IN MEMORY:** "five straight convergences 42-46" is **FOUR**. exp43 did NOT formally converge — `resources/RECOVERY.md` said so all along, and exp43's report holds no `converged_at` at all.

**★ EXISTENCE IS NOT READABILITY.** This process lost read access to the private memory directory mid-session on 2026-08-26. Under that state `exists()`/`is_dir()` return True, `iterdir()`/`read_text()` raise, and **`glob()` returns an EMPTY LIST without raising**. sv crashed (exit 1) an hour after exiting 0 on the same tree. Guarded now in `scripts/cdsfl_sv.py` (`MemoryUnreadable`) and `bench/tests/_private_memory.py`. A failed count must never refresh the ledger's "counted" stamp.

**★ ONE COMMAND FOR THE FOUNDER:** this file's Desktop mirror is stale and this process cannot overwrite it (denied 6/6). `cp ~/Developer_Projects/Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md ~/Desktop/CDSFL_Agent_Operational_Plan.md`

**★ RESUME POINTER (2026-08-24 02:20 BST). Superseded by the block above; retained as trail.**

**★ START HERE — FRESH INSTANCE, COLD START. FOLLOW IN THIS ORDER.**

**Step 1 — run these two commands.** Together they take about six seconds and report LIVE state that no document can (current commit, dirty files, whether a runner is still executing).
```
cd /Users/georgejackson/Developer_Projects/Constraint_Engineering
git log --oneline -5 && git status --short
python3 scripts/cdsfl_recover.py --full
```
`cdsfl_recover.py --full` is the authority on git state and running processes; where any document disagrees with its `## GIT STATE` or `## RUNNING NOW` blocks, **the script wins**. Two more exist and are not needed at cold start: `python3 scripts/cdsfl_qc.py` (documentation consistency; currently 18 checks, 0 stale, 0 missing, 10 broken refs all of one known false-positive class) and `python3 scripts/cdsfl_sv.py` (state save — do NOT run at start).

**Step 2 — read these four, in this order. About 280 lines in total; everything else in all of them is dated trail.**

| # | file | read | what it gives you |
|---|---|---|---|
| 1 | *this file* — `experimental_notes/CDSFL_Agent_Operational_Plan.md` | this pointer block only, to the `---` below | the resume point and the five things not to get wrong |
| 2 | `~/Desktop/CDSFL_HANDOVER_2026-08-24.txt` | all 98 lines | **nine numbered decisions waiting for the founder**, four needing their key or judgement. This is the live work queue |
| 3 | `resources/RECOVERY.md` | lines 1-190: the two standing corrections at the top (the test-suite offline figure, and the simulated-panel mislabelling), then the **SESSION STATE — 2026-08-24 02:15 BST** block that begins at line 129 | pending work, blockers, and two corrections that are permanently in force |
| 4 | `resources/ONBOARDING.md` | the **Current State** block under `<!-- SV:LATEST_EXP_START -->` only | what the last two days established and why it mattered |

Both `RECOVERY.md` and `ONBOARDING.md` were updated by the state save at commit `4d4f58f` on 2026-08-24 and **do reflect current state**; each is a long append-only record, so read only the newest block at the top of each and treat everything beneath as history.

**Step 3 — do not act before reading the five prohibitions immediately below.** Each is a mistake this project has already made once.

**WHERE THE PROJECT IS.** Stage 1 of the runway is complete bar one ruling. Its exit test passes 8 of 8 (`python3 scripts/replay_accounting.py --verify`) and no archived run changes its convergence round under the repaired accounting. Stage 3 — exp50/51/52 — is **blocked on a scientific ruling, not on code and not on missing files.**

**FIVE THINGS THAT MUST NOT BE GOT WRONG BY A FRESH INSTANCE.**

1. **NEVER delete `exp39-experimental` before the encrypted bundle is verified.** Commits `ddd74bde` and `eecdb0f` are reachable from that branch **and nothing else**. They hold all three unrun exam articles and all five answer keys. Deleting the branch and running `gc` destroys the only local copies. The bundle (`~/Desktop/CDSFL_archive/exp39-experimental-2026-08-17.bundle.enc`) is date-complete but only the founder's passphrase proves it opens.

2. **★ exp55's target is SPENT — its answers went public on 20 August, three days before it ran.** This item previously read "NEVER push this branch", on the grounds that `control_two_distinct_defects_KEY.md` was tracked at HEAD. That was true and it was not the whole picture. The key's sibling `control_two_distinct_defects_GROUND_TRUTH.json` states the **same two defects in the same terms** (CT-01 Nyquist misquoted as `f_s > f_max`; CT-02 `df = 1.5625 Hz` right, "resolves 1 Hz" does not follow) and has been on **public main since `bd9c569`, 2026-08-20 01:21 BST**. The target itself is public too. Both exp55 runs started 2026-08-23. The 23 August key split was correct — it removed the answers from the file the runner stages into the panel prompt, the exposure that cost exp48 and exp49 — but it was not sufficient and nothing said so. **Both files now live outside any git tree** in `../CDSFL_experiment_keys/`, with `.gitignore` refusing `*_KEY.md`, `*_GROUND_TRUTH.json` and `*_ANSWER_KEY*`. **History was NOT rewritten** (18 of the branch's 57 commits are cited by hash in markdown, and the same content is public on main regardless), so the blobs stay reachable — stated, not glossed. **A re-run needs a NEW target.** Neither existing run reached round 1; both stopped at `r00`.

3. **exp53 must NOT be dropped.** It is the **zero-plant** control and measures stopping-decision contamination. exp55 is a **two-plant** harness control. Two plants is not zero plants.

4. **The three unrun articles are NOT lost.** They recover from `ddd74bde^` as `exp50_physics.md` / `exp51_biology.md` / `exp52_factorial.md`, matching the target MANIFEST's published hashes. The configs point at *staging* names (`PX-12-REF-05.md` and siblings) that were never committed. Searching the staging names and concluding data loss is a mistake already made once.

5. **Models are given ABSOLUTE target paths, never relative** (founder ruling, `dcbcf68`). The falsifier gate runs falsifiers in an empty working directory, so a relative-path reader ERRORs while a detached falsifier CONFIRMs — the gate then selects FOR falsifiers that never read the document. `_absolute_target` in the runner handles this at all five model-facing prompt sites; `bench/tests/test_absolute_target_paths_2026-08-23.py` pins it.

**MEASURED STATE.** Suite **3840 passed, 34 skipped, 0 failed**. qc **18 checks, 0 stale, 0 missing**, 10 broken refs all of one known false-positive class (non-path tokens read as paths). Branch `build-experiment-2026-08-22`, 34 commits ahead of `origin/main`, **not pushed and must not be**.

**LAST RUN.** exp55, twice on 2026-08-23, both `HALTED_IRREDUCIBLE_QUEUE_ALARM` at round 0. Cause found and fixed. **exp50/51/52 never started; exp53 started twice with no report; exp54 has no config.** exp55 sits *outside* the planned 40–54 arc as a harness control — do not read the numbering as sequential.

---

**★ RESUME POINTER (2026-08-17 01:45 BST). Superseded by the block above; retained as trail.**
**★ exp39-experimental ARCHIVE: `~/Desktop/CDSFL_archive/exp39-experimental-2026-08-17.bundle`**
**(676 commits, 107 not in main, restore-tested). Holds the per-run TARGET STATES that
counterfactual-repair adjudication needs. The REMOTE branch exposes 17 answer-key blobs
including exp50/51/52 which are UNRUN — remote deletion pending founder confirmation that
the encrypted archive verifies. MAIN IS NOT IN DEFICIT; that earlier claim was wrong.**

**READ `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` — it is the live queue. (Standing line:
every future pointer inherits it.)**

**THE TRUNCATION ALARM IS REFUTED. THREE FIXES LANDED. NO EXPERIMENT IS INVALIDATED.**
Suite **3540 passed, 14 skipped, 0 failed**.

CC1's 2026-08-16 claim that exp46 and exp49 converged EARLY because of truncation is
**WRONG**. Truncation was cutting PREMISE lists off the end of findings, so location
extraction gave the right answer for the wrong reason; repairing truncation alone made it
worse. **Two defects were masking each other.** With both fixed: exp44 10→8, exp45 3→3,
exp46 5→5, exp47 11→7, exp48 never, exp49 6→6. **No run converged early**; two were
DELAYED by truncation, the safe direction. The adversarial sweep was right and CC1 was not.

**[FIXED] A parser** (`runner_core.py`): the `|$` branch was unreachable after
`block.strip()`; separator class missed `.`/dashes; heading style has no separator.
5592 archived blocks: **4748→5060 matched, 312 recovered, ZERO regressions**. Two wider
candidates rejected — they shortened 870 and 834 correct descriptions. The first was nearly
shipped because the regression metric was blind to text loss.
**[FIXED] B backfill** (`scripts/backfill_descriptions.py`): **531 content-verified
repairs**, 471 unverifiable left alone, **archives NOT modified** (opt-in sidecars).
**[FIXED] C premise exclusion** (`finding_locations`): scope set by measurement — only
`Premises:` (35 findings), NOT `EVIDENCE:` (78), which substantiates the same defect.

**RE-DERIVED:** pairs 438→460, tier-3 coverage 94→110, truncated criticals 49%→14%,
AUC 0.986→0.976. **Survives:** P(merge|different)=14.9% at the live 0.20 threshold, ZERO
false splits, 84% fewer false merges than location keying alone, tier 3 wrong on all 3 of
the decisions it changes. **Dies:** truncation-harm association p=2.07e-05 → **p=0.272**.

**NEEDS A FOUNDER RULING:** the 133 unadjudicated similarity pairs (was 120).

Full record: `experimental_notes/Description_Truncation_Three_Fixes_2026-08-17.md`.

---

**★ RESUME POINTER (2026-08-16 23:42 BST). Superseded by the block above; retained as trail.**
**READ `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` — it is the live queue. (Standing line:
every future pointer inherits it.)**

**THE SIMILARITY FUNCTION'S EVIDENCE WAS NEVER STORED, AND MEASURING IT PROPERLY FOUND TWO
DEFECTS.** The founder-approved evaluation fix is BUILT. `scripts/similarity_operating_characteristic.py`
rebuilds the 438-pair dataset from the six archived reports; every recorded figure reproduces
exactly (165 / 161 / 94 / 438 / 28 / 290), pinned by `bench/tests/test_operating_characteristic.py`.
Suite **3517 passed, 14 skipped, 0 failed**; qc **8 checks, 0 broken refs, 0 missing, 0 stale**.

**[FIXED] `quantities_agree` treated a MISSING anchor as a wildcard** — a bare number matched any
number of equal value. This was tier 3's ENTIRE operative error: routed through
`identity_decision` it changed **3 of 318 labelled pairs and all 3 were wrong**. Fix costs nothing
(same-defect answers identical 19/0/9; false SAME 14 → 10; Fisher **1.4e-07 → 3.3e-09**,
cross-verified three ways; operative errors **3 → 0**). TESTED at 13 in
`bench/tests/test_anchorless_outcome_guard.py`. exp47's series moves at round 11 (0 → 1, C0063 now
counted); five of six runs byte-identical; **no convergence conclusion moves**.

**THE METHOD LESSON, and it generalises: an answer distribution is not an operating
characteristic.** Tier 3's justification described what it SAYS (Fisher p = 1.4e-07, never called a
same-defect pair DIFFERENT — both true). What it DOES was never measured and was 0 for 3. Whenever a
component is justified by a statistic, measure separately how often it changes a decision and how
often those changes are right.

**TWO ITEMS NEED A FOUNDER RULING BEFORE THE NEXT RUN.**
1. **Descriptions are truncated archive-wide.** 2187 descriptions: 714 exactly 200 chars
   (`runner_core.py:814` parser fallback `block[:200]`), 661 exactly 500
   (`reference_runner_v2.py:1059`), 1284 end mid-word — ~63%. Fixing `block[:200]` changes parsing
   for every future run mid-arc and breaks Exp 50+ comparability with Exp 40–49 on any
   signature-derived measure. **Do NOT overclaim the harm**: pooled OR 10.5 (p = 2.07e-05) REVERSES
   on exp48/exp49 — Simpson's paradox, causal claim NOT established. What survives: signatures
   shrink (median 4 vs 5, p = 0.0104) and **15 of 318 pairs sit EXACTLY on the 0.20 threshold**.
2. **The 120 dropped pairs.** The recorded measurement silently discards pairs between embedding
   0.70 and 0.90 — 27.4% of the data and the hard 27%. Extracted unanswered to
   `experimental_notes/data/similarity_adjudication_pack.json`. Deliberately NOT pre-answered. Every operating
   point is provisional until they return.

Full record: `experimental_notes/Similarity_Function_Operating_Characteristic_2026-08-16.md`
(+ `_Plain_English_` + Desktop TTS).

---

**★ RESUME POINTER (2026-08-05 20:30 BST). Superseded by the block above; retained as trail.**
**READ `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` — it is the live queue. (Standing line:
every future pointer inherits it.)**
**THE RECOVERY INSTRUMENTS WERE AUDITED AND MOST OF THEM WERE LYING.** A 15-agent read-only audit
returned **71 findings, 60 CONFIRMED on independent adversarial reproduction, 0 refuted**, plus 25
the verifiers found that the auditors missed. Full record: `experimental_notes/Recovery_Resource_Audit_2026-08-05.md`.
Uniform pattern, and it is this project's own signature failure: **every failure rendered as a
confident success.** Worst case — `cdsfl_seal_logs.py` tested a `(bool, str)` return for truth, so
**the tamper detector could never report tampering**; falsified directly (one appended byte → now
TAMPERED exit 1, at HEAD it was OK exit 0). Four root causes behind most of the rest: CURRENT_STATE
generated pre-commit; `latest_experiment()` bound to the top experiment number so halted exp53
blanked all ~60 archives; `git_state()` comparing to origin/main and rendering a FAILED rev-list as
"up to date"; and `cdsfl_recover.py` hunting markers deleted in April, so pending-work printed
nothing for **113 days**. `qc` had crashed for **105 days**; `onboard --full` was a no-op for **118**
with its own self-test reporting OK.
**OPEN BRAIN WAS UNFED, NOT BROKEN** — `sv` had no capture code; it now captures on every successful
commit (proven live, `project=CDSFL`). Its MCP entry was pinned to a March fork, so tamper evidence
was absent since 2026-06-08; unpinned, and `verify` now **exits 1** rather than certifying a
93%-unverifiable store as OK. **That red light is correct — do not "fix" it.**
**THE COMPACTION DRILL went 1-of-5 → 4.5-of-5.** Suite **2549 → 2776 passed / 7 skipped / 0 failed**
offline; OpenBrain 440 → 475.
**STATE:** do NOT read a hash from this line — it ages the moment the next commit lands, and a
stale-but-confident state claim is the exact defect this whole audit was about. Run
`python3 scripts/cdsfl_recover.py --full`; its `## GIT STATE` and `## RUNNING NOW` blocks are
computed live and label themselves authoritative. Standing facts that do NOT age: both repos
commit LOCALLY and are **not pushed** without the founder saying so, and OpenBrain
(`/Users/georgejackson/Developer_Projects/OpenBrain`) is a SECOND dirty tree that is easy to
forget at commit time.
**★ 13 FOUNDER RULINGS RAISED (2026-08-05)** — `~/Desktop/CDSFL_tts/Rulings_Needed_2026-08-05.txt` and
`experimental_notes/Rulings_Needed_2026-08-05.md`. **ALL THIRTEEN WERE RULED ON 2026-08-06.** The
authoritative status is the `## Disposition` table at the HEAD of that file — ten implemented, one
reversed (the bridge is fixed, not retired), one answered and folded into the estate audit, one in
progress (the Open Brain backfill). **Only two things still need the founder:** a spot-check of the
record classification, and the launchd reload command below.
The three that carried weight, and how they went: the 106 unlabelled Open Brain rows — RULED classify
them ALL, and normalise the `CDSFL`/`cdsfl` case split the equality filter treats as two projects;
which document owns the canonical recovery ordering — NOT a straight ruling, the founder asked instead
for an audit of the whole estate and a proposal against INDUSTRY STANDARDS rather than invented ones;
and whether this tracker stays the Desktop canonical — RULED it does not, the repo copy is canonical
and the Desktop copy is the mirror (see "Canonical anchors" below).
**★ SEPARATELY, AND UNCHANGED — these predate the recovery audit and are the ARC's decisions, not the
tooling's:** the DECISIVE form of the false-CONFIRMED discrimination control; the disposition of the
prose-similarity question the 5-model panel answered on 2026-08-04; and the zero-plant control restart.
These are what actually gate progress toward Bench Run 2. The recovery-resource work was a necessary
side track, not the arc.
**The Open Brain launchd bridge is SAFE to reload — the earlier warning here was FALSE.** It said
reloading would `sys.exit(1)` and restart-loop; that was written before the registry outbox path was
corrected and was never re-measured. Measured 2026-08-06, read-only, without starting anything:
`verify_canonical_install` OK, `load_config` OK, `validate_outboxes` OK — it would START. Founder
ruling 12 REVERSED the earlier retire recommendation (CW may return during UX design), so the code
was fixed rather than retired. PID 1406 has held the old code in memory since 2026-06-10; the reload
is the founder's to run:
`launchctl bootout gui/$UID/com.openbrain.bridge && launchctl bootstrap gui/$UID ~/Library/LaunchAgents/com.openbrain.bridge.plist`

**★ RESUME POINTER (2026-08-05 14:20 BST, post-`rs`). Superseded by the block above; retained as trail.**
**READ `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` FIRST — it is the live queue.** (Standing instruction,
inherited: it was first stated in the 2026-08-01 and 2026-08-02 pointers and was NOT carried forward when the
pointer advanced on 2026-08-04 and 2026-08-05, so it survived only inside superseded blocks. Every future
pointer must copy this line forward.)
State verified clean after the model point-update and relaunch: HEAD `624b39a`, tree clean, in sync with
`origin/exp39-experimental` (0/0), nothing running, no stray Wolfram kernels, `WolframCloud` live and
answering (`$Version` 15.0.0; ζ(3) and eigenvalues {4,2,1} match the recorded landmarks — Wolfram Language).
The `WolframBridgeLegacy` entry is GONE from `claude_desktop_config.json` (survives only in the two dated
`.bak` files); the config now holds `WolframCloud` alone, which is the intended end state. The local Engine
is correctly NOT an MCP server — on-demand via `wolframscript` only. Licence expires **2026-09-11**.
**PROVENANCE CORRECTION LANDED** (`624b39a`): the 2026-08-04 simulated bench's five reviewers were Claude
subagents, not the named frontier models, and had been reported under vendor names. Relabelled `SIM-A`…`SIM-E`
in the evidence JSON, the note, the founder TTS and the harness source, correction at the head of each.
Every measured result is UNCHANGED — 12/12 stages, five independent demonstrations, zero false positives.
Standing rule now in project `.claude/CLAUDE.md` and persistent memory: a simulated agent NEVER carries a
vendor name. The genuine five-model panel review (`bench/logs/pr_semantic_distinctness_2026-08-04/`, ~GBP 3)
is unaffected and its answers stand.
**FOUNDER DECISIONS STILL OPEN, unchanged:** (1) the DECISIVE form of the false-CONFIRMED discrimination
control (the detective form is already covered by ruling 3 and needs nothing); (2) ruling 1 disposition;
(3) the control restart — the evidence now supports it well.

**★ RESUME POINTER (2026-08-04 03:55 BST, sv). Superseded by the block above; retained as trail.**
**THE PIPELINE NOW RUNS END TO END** — `bench/tools/simulated_bench.py`, REAL functions in real
order, target ALG-02-REF-01.md (7 claims, 1 planted defect, 2 executable listings = the shape that
halted the control), panel = 5 blind agents barred from the fixture module and any answer key, each
required to WRITE AND RUN a falsifier. No paid dispatch. **12/12 stages; planted defect DETECTED with
5 independent demonstrations; ZERO false positives confirmed; novelty collapsed 5 findings to [1,0].**
Found a REAL integration defect on its first run (fixture falsifiers carry a `<<DOC_PATH>>` token;
fed raw, both falsifier-bearing findings returned ERROR) — every component correct, the SEAM wrong,
which no unit test catches.
**HONESTY CHECK justified immediately:** 8 findings claimed their falsifier RAN, the runner confirmed
7. C0003 = ERROR, an asserted demonstration that is not one. Never accept "the model says it verified".
**FALSE-CONFIRMED HOLE MAY BE CHEAP:** unprompted, an agent ran its falsifier against a CORRECTED copy
(`seen = set()`) and recorded "not falsified", exit 0. So ASK THE PANEL for the discrimination control
rather than synthesising a corrected copy. Detective form already covered by ruling 3; **DECISIVE form
still needs a founder ruling** (touches CONFIRM-only).
STILL STANDS: routing proven 6/8 vs null 0/25 (p=2.5e-5); the two-sided gate is NOT what stops most
runs (STATE_CONVERGED 6, quiescence 6, budget 5; BOTH prose exams closed on STATE_CONVERGED); panel
answered ruling 1 5/5; the founder's STEM-token idea beat all five and BOTH-hierarchically beats
either; built SHADOW-ONLY, defaults False, no config sets it. Plan: shadow all four remaining legs
free, decide before BR2, do NOT promote mid-arc.
FOUNDER DECISIONS: (1) false-CONFIRMED decisive control; (2) ruling 1 disposition; (3) control restart
— evidence now strongly supports it.

**★ RESUME POINTER (2026-08-04 02:53 BST, sv). SUPERSEDES EVERY POINTER BELOW.**
ROUTING REPAIR **PROVEN**: paired replay through the real `_apply_routing`, **6 of 8 resolved** vs a
measured null of **0 of 25** (Fisher p=2.5e-5; binomial + mpmath agree). 11 dispatches, ~GBP 2.
**THE FINDING THAT REFRAMES RULING 1:** the two-sided gate is NOT what stops most runs. Across all
completed runs `STATE_CONVERGED` closed 6, critical-quiescence closed 6, budget/stall closed 5 — and
BOTH prose exams (48 r5, 49 r6) closed on STATE_CONVERGED, their critical series `[9,0,1,0,1,0]`
having no three-zero streak. The similarity question feeds a gate that fires on neither prose run.
**RULING 1 — panel answered 5/5, no compelled convergence.** All five: prose similarity is a dead end.
3 say no reliable method exists (causal, not textual); 2 say use the falsifier (mutation-response
equivalence / identity-under-intervention). **The founder's own proposal beat all of them:** hard STEM
tokens (numbers, claim IDs, identifiers) — duplicates median 0.542, distinct 0.000, p=7.5e-9, 97.5%
coverage. **And keeping BOTH beats either, but NOT by voting** — AND and OR both fail; HIERARCHICAL
works (location decides the coarse call; signature splits only WITHIN a flagged location, at 0.20).
Ground truth proven by execution: repairing D1 leaves D2 standing.
**BUILT SHADOW-ONLY** (`hierarchical_novelty_convergence` defaults False; no config sets it). Report
records the series, whether it gated, AND `novelty_rule_divergence` naming the SPECIFIC findings the
rules disagree on. **PLAN: shadow on all four remaining legs at zero cost, decide before BR2. Do NOT
promote live during the arc — it would confound the capstone's four-way comparison.**
LIMITS: two constructed cases, archive merged-pair sample n=14, the 0.20 within-location cut is NOT
swept against same-location pairs (archive lacks them; needs constructing).
Suite **2549 passed / 0 failed** offline. Night's spend under GBP 5.

**★ RESUME POINTER (2026-08-02 22:05 BST, sv). SUPERSEDES EVERY POINTER BELOW.**
**READ `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` FIRST — it is the live queue.**
MUST list A1–A10 **CLOSED**. But the ACTUAL convergence blocker was on no list: the ROUTING LADDER's
prompt was code-only and never received the target path or text, so on a prose target with fenced
listings no rung could resolve anything and the recorded reason was factually false. MEASURED
**41-for-41** routing resolutions on prose WITHOUT listings (Exp 48 chem 16/37, Exp 49 eng 25/38;
1 HIL in 75) vs **0-for-25** on the control WITH them (halt R3/16). Fixed `1bd7605`, 15 tests.
Found by offline 11-agent adversarial falsification, NOT review — the MUST list was necessary, not
sufficient. Convergence itself was never at risk: close-the-loop verified 0/37 and 0/38 in the two
runs that converged; gamma implicated nowhere.
ALSO CLOSED: `run_verification` 4th repair (veto semantics — the 3rd shipped `parse → PASS` and closed
a shell-injection fix); sweep runs on a halt; panel briefing corrected; B3 (ruff's success line counted
as a violation, live all arc); A9 preflight-that-refuses; A10 rejection reasons to the panel.
OPEN, NEEDS A RULING: the sweep CANNOT clear a critical (max severity ever touched 0.66 vs 0.70) so a
false-positive critical is permanent human work; and a valid-but-logically-wrong falsifier can CLOSE a
finding against a TRUE claim (new hole, not built). 38 sub-criticals stuck with no route to terminal.
WOLFRAM: paid keys died 2026-07-31. Now local free Engine (`Wolfram`, no ceiling, stateful, curated data
OK, but SINGLE-KERNEL and licence expires **2026-09-11**) + credential-free hosted (`WolframCloud`,
identical computation, stateless, hard ~30 s ceiling). Stays OUT of the pipeline.
WOLFRAM WIRING CORRECTED 22:15 after the restart failed: Claude Desktop rejects a bare `url` (use
`npx -y mcp-remote <url>`), and the local Engine must NOT be an always-on MCP server — Desktop spawned
TWO kernels against a SINGLE-KERNEL licence and every kernel request failed, `wolframscript` included.
Engine is now on-demand via Bash only. If wolframscript claims a licence fault, check `ps` for
`MacOS/wolfram -run` first. Licence expires 2026-09-11.
FOUNDER DECISIONS: (1) restart the control, after (2); (2) **free + highest value** — author the five
unwritten prose targets WITHOUT fenced code listings; (3) critical-severity ceiling; (4) alarm HALT vs
veto-only; (5) one paid sentinel-check dispatch; (6) push/merge + experimental-branch deletion.
Suite **2521 passed / 7 skipped / 0 failed**, offline under `--netguard-strict`.

**★ RESUME POINTER (2026-08-01 21:45 BST, HEAD `703041a`, tree clean). THIS SUPERSEDES EVERY POINTER BELOW.**
**READ `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` FIRST — it is the live queue; this file is now history behind it.**
Arc position: 47 divergence DONE, 48 chem DONE (converged r5, 31/32 falsifier-CONFIRMED), 49 eng DONE (converged r6, 31/31)
→ **53 zero-plant control PAUSED at round 4** (restart recommended, not resume: 13 findings were locked irreducible by the
broken S_k hard gate, not by anything real) → 50 physics → 51 biology → 52 factorial (frozen instrument) → HARD STOP → BR2.
BLOCKING the control: queue items A4/A5/A6/A9/A10 (unpaid, ~1 day) + B2/B3 + a docs sweep. A1/A2/A3/A7/A8 closed at `0a15138`.
Suite 2461 pass / 0 fail, OFFLINE under `--netguard-strict` (49 attempts, all denied, 3 KNOWN_OUTBOUND keys with written reasons).
**THE DAY'S GOVERNING LESSON:** `run_verification` was repaired FOUR times; the third shipped `ast.parse → PASS`, which closed a
finding whose fix injected `subprocess.call(..., shell=True)`. A syntax check speaks about the LISTING, never the FIX, so it may
only VETO. Outcomes are now FAIL / NO_APPLICABLE_CHECKS / PASS, and `vetoes_run` is kept separate from `checks_run` so a veto that
passes can never read as a check that ran. Generalise this to extraction-scoped bandit before wiring it. `max_irreducible_queue`
reverted to the default 2 — raising it to 8 then 30 suppressed a correctly-firing alarm both times.
FOUNDER DECISIONS OPEN: (1) restart-vs-resume the control; (2) is the queue alarm's new HALT (vs veto-only) intended;
(3) spend one dispatch confirming a model reads the new sentinel markers before a paid run; (4) push the local commits.
Notes: `Prose_Acceptance_Stage_2026-08-01` (technical + plain-English + TTS), `State_And_Remaining_Path_Plain_English_2026-08-01`
(+ Desktop TTS `Where_We_Are_And_What_Is_Left_2026-08-01.txt`).

**★ ONE-SHOT ARC IN FLIGHT (founder go 28 Jul 2026, ~23:55 BST). RESUME POINTER (post-compaction: read RECOVERY.md 28-Jul blocks + this line).** Sequence: 47 divergence (LAUNCHED 00:00 29 Jul, run dir exp47_divergence_locationkey_live_20260728T230026Z, deltas: sweep + FIRST ImmuneMemory recording) → 48 chem exam → 49 eng → 50 physics → 51 biology → 52 factorial (frozen instrument, fixes held out) → HARD STOP before BR2 for founder review. Guardrails: pause+call founder on non-convergence / surviving critical / new fault class / >$80/run / safety. HIL review post-hoc (founder ruling). Exam modules: drafted ahead + tool-verified answer keys (separate files under bench/cdsfl_registry/targets/) + panel draft-review + claim_patterns regex check; pass mark = ratified conjunctive gate (attributed recall 100%, non-distortion, noise-conditioned decision-change, γ-trajectory control; per-verdict logging). Chem draft workflow running. Markdown location-key landed (claim-ID symbols). BR2 rules banked: absolute tools-decide acceptance bar; ≤25%% novel items (tool-verifiable, own axis, promotable); ouroboros sources beyond-training-data material. Balance ~$452.

**★ CORRECTION 2026-08-06 — THE BLOCK BELOW IS HISTORY AND TWO OF ITS INSTRUCTIONS ARE NOW FALSE.**
It is retained because this file is a record, and its measurements were true when written. But it
contains live-sounding instructions that a recovering agent could act on, and this is now the
CANONICAL copy of the tracker, so they are corrected here rather than left to mislead:
(a) **"FIX designed … NOT yet coded" and "NEXT ON RESTART: implement FIX 1–5" are DONE.** The
    tranche was coded 2026-07-27 in commit `1cec60d` and shaken out by Exp 44, which converged at
    round 12 with zero residue — the first formal-endpoint zero-residue convergence in the project.
    Nothing about FIX 1–5 is outstanding.
(b) **"FIRST READ the 20-July CURRENT STATE block in `resources/RECOVERY.md`" is SUPERSEDED.** That
    block is now labelled superseded in RECOVERY.md itself. The live resume pointer is the ★ block
    at the TOP of this file; the FIRST READ order is this file, then
    `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md`. Exactly one document may say "read this
    first", and it is this one.
Everything else below stands as the record of what was known on 2026-08-02.

**Last updated.** 2026-08-02 22:05 BST (sv) (see the resume pointer at the top; the 20-July text below is retained as history). In brief: Exp 43 DONE (clean re-run, macrophage_cell.py) — the location-keyed two-sided gate GENERALISED (over-production solved: crit series [0,0,0] R6–11, gamma ~0.57, gate passed R4+R11), but formal 3-consecutive convergence was blocked by ONE mechanical artifact: sub-critical UNCONFIRMED findings (falsifier-error/absent, NOT model disagreement) mis-counted as "contested." FIX designed + sy/z3-verified (FIX 1 → converges R6), NOT yet coded. Arc reorder + renumber CONFIRMED & LOCKED (composition tests old-44/49 DROPPED — every run already tests the whole integrated system): NEW Exp 44 = `dm/_memory.py` (the shake-out / blue-water test), then evidence.py, _shadow_stage6.py, _divergence.py, then 4 synth STEM modules (to draft), then the 2×2 factorial. NEXT ON RESTART: implement FIX 1–5 (FFAFP + regression tests) → build NEW-Exp-44 memory.py config → run under cy. Full sequence in the 20-July RECOVERY block. Founder: finish efficiently, take the financial hit. Full detail: Desktop TTS `Exp43_Overnight_and_Contested_Analysis_2026-07-19` + `Exp44_Fix_Design_and_Forward_Plan_2026-07-19`. Prior gate context: **GAMMA TWO-SIDED GATE LIVE + overnight build banked (10–11 June); ~3-week founder hiatus (external model turbulence); full `rs` on 2 July confirms state intact (HEAD `6ed0adf`, tree clean, 62-test gate suite green).** Two-sided gate `71b190b` (founder ruling 2026-06-10; standing directive "GAMMA IS LOAD-BEARING — DO NOT DEMOTE IT" in project CLAUDE.md): convergence = `gamma_critical >= 0.30` AND 3 consecutive zero-new-critical rounds, BOTH required; tool-verified on both landmarks (exp41c gamma_critical=**1.000**, exp42=**0.687**; the "0.240" in older entries = the ALL-FINDINGS gamma, NOT the gate input). The gate commit left 3 tests red → fixed `633b4c6` (test class renamed from the demotion-asserting `TestGammaIsReportedNeverTriggers`; 434-test sweep green). **Severity calibration BUILT** `050f17c` (gated default-off, 17 tests; INERT until a latent-tagger sets `entry["latent"]` — fail-safe; never demotes safety/core/security/data_loss). **Exp 43 config** `1b5d148` (`bench/exp43_configs/43_macrophage_locationkey_live.json`) pre-flight VERIFIED (all gate flags survive launcher→RunnerConfig; 15 AST symbols extract from raw source — the Exp-42 silent-0-symbol failure mode pre-empted). Records `053e873`; sv `6ed0adf`. **Directive-measurement CORRECTION:** the dispatched system directive is ≈50K chars, of which 43,667 (`cdsfl_operational.md`, 18 sections) is appended UNPRUNED outside the composer prune path (`reference_runner_v2.py:2932`); today's pruner reaches only ≈6% (the domain packet); the "~60K directive" figure was a CONFLATION with the 60,416-char composer.py TARGET ARTICLE (user prompt, not directive). Trim-to-≈27K draft exists; awaits the `pr` panel. **Macrophage:** lives ONLY in `bench/macrophage_cell.py` (immune_agents.py has 0 macrophage code — matrix row corrected 2026-06-10); wired into the runner (instantiated `reference_runner_v2.py:3438`, observed `:3544`) but reaches NO live decision (shadow→shadow via ouroboros); ONBOARDING closure index re-tiered live_operational→shadow_integrated. **Load-balancer** (`dm/_load_balancer.py`): dormant-in-practice (DynamicManager.process_round never called by runner v2); DISTINCT from take_up_slack (planning-time task→model allocator vs reactive falsifier re-router) — KEEP, wire only when BR2 needs differential allocation. **dm consolidation:** Step 0/1 (green test baseline + landmark pin) done via `633b4c6` + `test_two_sided_gate.py`; Steps 2–6 (extract γ-estimator/novelty-series to `convergence_core.py`, collapse dm duplication, guard-test the refuted `ConvergenceDetector` out of the decision path) behind founder `go` — the landmark is fragile, direction is dm→runner, never a blind swap.

**RESUME POINTER (12 July 2026 02:15 BST, Phase 1 executed overnight) — PAUSED FOR FOUNDER REVIEW BEFORE EXP 43.** Phase 1 (A1–A4) DONE; commits on `exp39-experimental` (pushed at this sv): A1 pruning `pr` panel 4/5 (cc2 blocked by CLI OAuth; unanimous SOUND-WITH-CAVEATS; §18 = top prune; RECOMMENDATION-only, NOT implemented) `ef1fe7b`; A2 ouroboros SHADOW real-work (resolve OA→download→pypdf/pdfplumber parse→cheap-reader brief; proven live on arXiv 1706.03762 = 24k chars parsed/hashed/briefed; strictly shadow — briefs never reach a prompt/c_ext/γ) `df18201`; A3 routing rename `take_up_slack`→`routing` (code-only; ALL configs unchanged; alias in BOTH launcher_core AND RunnerConfig.from_dict) `349951f`; adversarial-pass fixes `b656549`. **A4 §10 = already INERT** (flag never passed to RunnerConfig; no compelled-conv text in dispatch) ⇒ Exp 43 is now FULLY directive-identical to Exp 42 on BOTH launch paths (supersedes the "run without §10 = deviation" framing). **ADVERSARIAL PASS (14 agents, 5 confirmed/5 refuted) caught + FIXED a real A3 regression:** the routing alias was ONLY in launcher_core, NOT RunnerConfig.from_dict → the runner's own `--config` CLI ran routing SILENTLY OFF for Exp 43 (my earlier "verified" tested only the launcher path). Fixed in both paths + regression test; 4 LOW shadow-ouroboros findings also fixed. **BLOCKER (founder morning action):** claude CLI (CC2) OAuth session EXPIRED (macOS Keychain; the generic 401 was masked by inherited `ANTHROPIC_BASE_URL`). Force re-login: run `claude` → `/login` (or `claude logout`/`claude login`); VERIFY `claude -p --model opus "PONG"` in a PLAIN terminal (must print PONG, no OAuth-expired). Needed so Exp 43's 5-model panel is byte-identical to Exp 42 (call_claude_cli uses `--system-prompt`=full CDSFL directive, which subagents can't replace). Once fresh, dispatch launches with `env -u ANTHROPIC_BASE_URL` (no code change). **Full suite 1595 pass / 3 fail:** 2 = CLI-OAuth timeout; 1 = PRE-EXISTING stale test `test_both_phase1_paths_use_the_constant` (decomposed_dispatch.py refactored off `_PHASE1_MAX_TOKENS` in `fbafff8`, unrelated — flag/fix separately). Report: `experimental_notes/CDSFL_Overnight_Phase1_2026-07-12.md` (+ `_Plain_English_` + Desktop TTS). **NEXT (Phase 2, on founder review + CLI re-login):** launch Exp 43 `python3 bench/launch_exp42.py --config "$(pwd)/bench/exp43_configs/43_macrophage_locationkey_live.json"` under full cy; ouroboros studies in shadow (NB: frozen Exp 43 config has NO `_ouroboros` block → the cell will NOT run in 43; enabling it = a pre-registration amendment needing founder sign-off). **OPEN founder decisions:** (a) set `hasTrustDialogAccepted` flag in `~/.claude.json`? (b) optional post-43 Exp-43-config-key rename to `routing_enabled`; (c) fix the pre-existing stale phase1 test; (d) A1 pruning cuts (implement + ablation, post-43); (e) complete A1 panel to 5/5 via cc2 once the CLI is up.

**Superseded resume pointer (8 July 2026, post pre-Exp-43 verification + founder decision-register close) — AGREED ACTION LIST:** Discussion phase CLOSED. Keys present + live-valid; `.env` now `chflags uchg` immutable (unlock: `chflags nouchg .env`). All flagged mechanisms tool-verified GREEN (250 tests): falsifier gate (CONFIRM-only, voting removed), routing (take_up_slack, wired `:5787`), §17/§18, merge-arb, immune. **PHASE 1 (before Exp 43, A1+A2 in parallel on founder `y`):** A1 — directive-pruning `pr` panel (5-model), design-guarded so it CANNOT touch the falsification core (gamma/R_k/gates = HARD constraint off the pruning surface; hypothesis-not-authority; ablation decides); output = RECOMMENDATION only, NOT implemented pre-43 (keeps 43 directive-identical to 42). A2 — ouroboros SHADOW-real-work build (cheap reader = Haiku/DeepSeek + full-text fetch+parse + brief generation + shadow-logging), integration-test-gated; runs in shadow during Exp 43 = the study the founder wants, zero convergence confound. A3 — routing rename `take_up_slack`→`routing` (module/flag/logs/tests + launcher back-compat + Exp 43 config flag; founder ruled 8 July it is trivial, NOT postponed — Phase 1). A4 — **RETIRE compelled convergence (§10)** (founder ruling 8 July: it was a star-topology HACK to force agreement when gamma wouldn't add up; an external reviewer would flag it as curve-fitting against the honesty claim; now redundant given the falsifier gate resolves criticals by runnable demonstration, not panel agreement). Method: (1) investigate what `section_10_compelled_convergence` actually does in dispatch; (2) verify mechanistically it is INERT under the falsifier gate; (3) retire + test (no new issues). **DECISION: run Exp 43 WITHOUT §10** — a convergence achieved without the hack is the stronger, more defensible result; isolation fallback = re-run with §10 on if it surprises. (NB: this is now the ONE deliberate deviation from directive-identical-to-42; justified because it removes a confound from the honesty claim rather than adding one.) **PHASE 2:** B1 — launch Exp 43 (`43_macrophage_locationkey_live.json`, config carries EVERY Exp-42-landmark flag identically; only target differs) under full cy; ouroboros studying in shadow. **PHASE 3 (during/after 43):** D3 findings staleness sweep (69 composer.py defects → fold-back, SEPARATE from 43); latent-tagger (D4); macrophage minimal-promote w/ STRICT HIL-high-severity threshold = safety/critical-functionality/ethical/legal ONLY (D6, post-43, informed by 43's review of the file); directive-prune IMPLEMENT+ablation (from A1); dm consolidation Steps 2-6 + rename (D8/D9); doc divergences (MATHEMATICAL_APPENDIX §8.7 stale; ouroboros scope; consensus-voting drift). **PARKING LOT (open, not near-term):** CDSFL at scale (open question, "it depends"; Part XIII n≈3-6 saturation is for architecture-A-on-one-bounded-artefact ONLY, says nothing about open STEM / decomposition); open-topology anti-dispute safeguard (star has the anti-voting guard, open topology has NO analogue — real gap); topology-switch UX; architecture (B). Founder correction: goal = the CALCULATOR ANALOGY (reliable viable answers, HIL for genuine residuals only), NOT removing the human; self-improvement = emergent bonus, NOT core. Detail: `CDSFL_Ouroboros_and_Self_Improvement_Assessment_2026-07-08.md` (§9 correction) + `CDSFL_Founder_Decision_Register_2026-07-06.md`. **No Bench Run 2.**

**Superseded resume pointer (8 July 00:20).** (1) **KEYS CORRECTION: the "missing keys" claim was FALSE** — all keys present in `.env` all along (`export KEY=value` format; the checkers ignored the `export ` prefix — parser bug fixed in `scripts/check_model_keys.py`; live pings HTTP 200 OpenRouter + DeepSeek). NO founder key action needed → on founder `y`, **LAUNCH EXP 43** (the generalisation test: does the location-keyed two-sided gate converge a SECOND module?): `python3 bench/launch_exp42.py --config "$(pwd)/bench/exp43_configs/43_macrophage_locationkey_live.json"` under full cy monitoring. (2) `sy`+`f` the Exp 42 findings fold-forward (moving target — staleness-check each). (3) Builds, each integration-test-gated: latent-tagger (activates severity calibration), ouroboros loop-close (papers→models), Stage-6 (ν_k,c_ext)→live equation, dm consolidation Steps 2–6 (behind `go`), routing rename `take_up_slack`→`routing`. (4) Directive-pruning `pr` panel (cc2+cx routes available; ge/cgpt/ds ride the same missing keys). (5) **FOUNDER DECISIONS:** macrophage minimal-promote (HIL-flag on ≥0.9 anomaly) vs retire-as-cosmetic; load-balancer keep-dormant confirm; dm consolidation `go`; routing rename approve. Master detail: `experimental_notes/CDSFL_Remediation_Program_2026-06-09.md` (POST-COMPACTION block) + `Overnight_Run_Report_2026-06-10.md` + `CDSFL_Full_State_Assessment_2026-07-02.md`. **No Bench Run 2.**

**Prior update.** 7 June 2026 23:14 BST. **DEFINITIVE ROOT CAUSE of Exp-42 non-convergence FOUND (tool-verified) + panel review (pr) complete: the convergence MEASURE is correct; its NOVELTY INPUT is corrupted by a CROSS-ROUND DEDUP FAILURE.** Investigation (`wf_10157160`) + the founder's gamma question: REFUTED my interim "demoting gamma was the mistake" hypothesis — demoting gamma was CORRECT (old gamma>=0.30 trigger would have FALSELY converged Exp 42 at round 3 while 15 criticals/round poured in; gamma is a Duane cumulative-slope artifact, laggy/unsafe; the 2026-05-23 panel was right; NO measure-goal mismatch — both old-gamma and the zero-new-critical count are diminishing-returns on the critical pop, both PoC-aligned, both ignore non-critical noise). **THE REAL BLOCKER (verified from the run registry):** the criticals-by-`open_since_round` = {0:15,1:10,2:6,3:3,4:1,6:1,8:2,9:1,10:1,12:4,13:4,14:4}; the late "4,4,4 resurgence" (R12-14) is **~4 DISTINCT real defects RE-FOUND every round** (C0065=C0070=C0075 phenotype-transform; C0064=C0068=C0073 count_constraints; C0066=C0071=C0076=**prior C0037** compose-ignores; C0067=C0069=C0074 prune-coherence), **all CONFIRMED (real) but NOT NEW** — cross-round dedup fails to match a defect to its earlier self, so they re-count as novel criticals, perpetually resetting the 3-zero streak. **The system SUBSTANTIVELY converged by round 5 (genuinely-new criticals→0); it cannot RECOGNISE convergence because dedup re-counts known defects.** Founder's "same churn or real?" = BOTH: real defects, churned by a dedup bug (not hallucination, not endless discovery). **PANEL (pr: CC2/CX/GE/DS, independent, no compelled convergence):** split on static-target — GE+DS RIGHT ("finite pool; non-convergence = a system reliability bug, dedup/inflation"), CC2+CX's "static can't converge, need fix-loop" true for the FULL reliability claim but the WRONG read for THIS run; UNANIMOUS tell "4,4,4 too uniform = same defects, dedup the late findings" → led straight to the root cause; UNANIMOUS consolidation method = Strangler-Fig (characterisation-test the WORKING inline code, extract to ONE module, delete ~14 dormant copies, feature-flag + replay-diff, one component at a time, revertible). GE: noise-tolerant MOVING-AVG (<1.0) would converge at round 8; null-test (run on a known-clean module) to prove inflation; DS: seeded-defect benchmark for the PoC acceptance gate. Panel responses `/tmp/panel_results.json`. **DEJA-VU = SAME DISEASE:** the failing dedup IS one of the re-derived inline mechanisms (the audit found 'similarity' re-grown); consolidation fixes both the convergence bug AND the wheel-reinvention.

**READ FIRST (morning review):** `experimental_notes/Session_Audit_2026-06-07.md` (+ TTS `~/Desktop/CDSFL_tts/Session_Audit_2026-06-07.txt`) — complete ~17h session ledger: DONE (11 commits) / ESTABLISHED FACTS / active-vs-dormant audit (`wf_a559aaad`: reframe + feedback GENUINELY ACTIVE; severity-calibration + directive-pruning NEVER BUILT; dedup root cause pinned to `reference_runner_v2.py:5446-5453`) / DISCUSSED / OUTSTANDING (11 items) / CORRECTIONS (4 of my own claims refuted by falsification).

**RESUME POINTER (7 June 23:14 BST) — DEFINITIVE FIX PATH, in order:** (1) **FIX THE CROSS-ROUND DEDUP** (the immediate convergence fix — a re-found CONFIRMED defect must read as KNOWN, not novel; likely a weak inline similarity copy) → re-run/replay Exp 42 → expect convergence (substantively converged by R5 already). (2) **CONSOLIDATE** the duplication via the panel's unanimous Strangler-Fig (this likely SUBSUMES #1 — the canonical similarity replaces the weak inline copy) = the founder's audit + deja-vu fix. (3) **GROUND-TRUTH AUDIT** (claimed-active vs genuinely-active: directive reframe, severity calibration, churn machinery, directive pruning — 60K still 60K; the 4.6 false-load-balancer report proves the record is untrustworthy). (4) Harden the stop criterion (GE moving-avg + null-test, DS seeded benchmark) + the find-FIX-reverify loop for the full PoC reliability claim. (5) RENAME take_up_slack→routing (routing facet of load-balancing/fingerprinting). Founder invoked `x` (rest override) — session ~13h, 23:14, deep night. No Bench Run 2.

**Prior update.** 7 June 2026 21:16 BST. **EXP 42 CLEAN RERUN COMPLETE — routing (take-up-slack) WIRED + LIVE-PROVEN (0 HIL); did NOT converge (over-production isolated as the sole remaining blocker).** Config `42_composer_takeupslack.json` (gate + take_up_slack_enabled ON, apply_fixes off, 16 rounds), ~4.4h, exited at round-15 budget. **FINAL: 80 canonical, 69 CONFIRMED (verified real defects), 11 resolved by routing, status 69 CLOSED / 10 CONFIRMED / 1 MERGED-dedup, escalated→HIL = 0 (ZERO, every round).** `gamma_critical_history` climbed to 0.658 (R11) then PLATEAUED + slid to 0.637 — never approached ~1.0; the flat line IS the over-production. **De-confounded result cleanly separates the two questions: (1) does routing work? YES, completely — the original 15-residual HIL pile-up is ELIMINATED (0 HIL, 11/11 escalations resolved by Codex→CC2 ladder live). (2) does it converge? NO — single isolated reason: unbounded over-production (panel keeps confirming real-but-LATENT criticals; gate-2 quiescence/3-zero-critical never reached). Contests (R6-7) self-resolved 0 HIL; churn (R12) + novelty flickered near threshold.** Colossus framing: 69 definitive findings, no definitive STOP (we never bounded "done"). Wiring commits `d134e8f`+`041faaa` (gated, 23 tests, live smoke C0034→CONFIRMED via Codex; Codex-first ladder ordering). **FOUNDER PAUSE-AND-RECONSIDER scheduled here (~11h session, approaching rest window).**

**RESUME POINTER (7 June 21:16 BST) — POST-PAUSE PLAN (founder-directed, audit-FIRST):** The 4.6-false-report-of-active-load-balancing proves the project's "what's active" record is UNTRUSTWORTHY (an un-falsified "X is active" claim — exactly what CDSFL exists to distrust). **(A) GROUND-TRUTH AUDIT (tool-grounded: git/grep/call-site-trace, NOT docs):** a ledger — proposed / genuinely-active / falsely-reported-active / useful-now — across churn detection-prevention-mitigation, the directive reframe (diminishing-returns / build-to-PoC), model behavioural feedback ("tell models what they're doing"), directive PRUNING (the operational directive is STILL ~60,416 chars in this run's dispatch logs → if pruning was reported done, that's another false-active), and the load-balancing/fingerprinting family. Cross-check ONBOARDING/RECOVERY/this-tracker vs code. **(B) RESOLVE THE CHURN DIAGNOSIS:** the 1-2/round are REAL (gate-CONFIRMED) but real-but-LATENT, over-rated ≥0.7; locate WHY nothing bounds them — is the diminishing-returns directive LIVE, is severity calibration LIVE or dormant? **(C) THEN:** apply the reframe (build-to-PoC, not endless bugs) + severity calibration + the separate-runner / load-balancing EVIDENCE test (founder: test everything, let evidence decide) — now on a trusted record. **(D) RENAME (first fresh-session task, deliberately NOT done at hour-11):** `take_up_slack`→`routing` (the ROUTING facet of the load-balancing/fingerprinting mechanism — "different sides of one coin", cross-ref `dm/_load_balancer.py` + `runner_core.py:66-72`): module `routing.py`, `route()`, `RoutingResult`, `routing_enabled`, `_apply_routing`, log `routing:`, tests `test_routing*`, launcher backward-compat for the old flag. No Bench Run 2.

**Prior update.** 7 June 2026 15:31 BST. **CAPABILITY-AWARE FALSIFIER ROUTING ("take-up-slack") BUILT + VALIDATED + UNIT-TESTED (`d383a6e`).** Founder directive: give weak models a fair chance, but when they demonstrably can't falsify, the STRONGER models "take up the slack" rather than endless re-asking; this is the capability-fingerprint / load-balancing work (which exists but was COLLAPSED to flat parallel dispatch — `DynamicManager`/`LoadBalancer`/`RoleAssignment`/`cc2_manager.py` all instantiated but DORMANT; fingerprints in `runner_core.py:66–72` already rank CC2 strongest→DeepSeek weakest). **Primary offender = DeepSeek** (data: 28% confirm rate, 10/15 residuals, 5/7 hardest; CC2+Codex = 0 residuals each). **Three tests run first:** (1) teaching the weak model (founder's "demand it checks its work") = 1/3 on fresh findings vs 0/5 untaught — marginal booster NOT a cure (no cross-call learning); keep the finder-agreement loop only as a confidence cross-check vs C0019-style re-scope. (2) take-up-slack = strong model (gpt-5.5) + execute_python tool loop on the 7 hardest residuals (weak source 0/7) → **6/7 CONFIRMED**. (3) C0063 (7th) = gpt-5.5 trips 2/2 on a markdown-code-block string-embedding trap; strongest rung handles it → **2-rung ladder = 7/7**. **Module `bench/take_up_slack.py`** (committed): dedup (defect already CONFIRMED elsewhere → never escalate) → ladder of progressively stronger writers (exclude failed source) with tool loop, reverify decides → HIL only if strongest can't. Runner-agnostic, side-effect-free, **10 unit tests pass**. CONFIRM-only still holds (REFUTED at any rung never drops the critical). Notes: `Capability_Aware_Falsifier_Routing_2026-06-07.md` + `_Plain_English_` + TTS. **RESUME POINTER (7 June 15:31 BST):** WIRE `take_up_slack` into the round loop at the single call site after `apply_falsifier_verdicts` (`reference_runner_v2.py:5396`), gated — provide `resolve_fn = dispatch(strong_cfg, prompt, enable_tools=True)` + falsifier extraction, `similarity_fn = _finding_similarity`; (deliberately NOT done at session end — touches the core round loop). THEN the convergence test: resume Exp 42 with take-up-slack ON → converge with zero residual-HIL? Behind founder gate (review Exp 40–54 contents first). Broader: role-specialise the panel (DeepSeek = finder not falsifier); full DynamicManager/LoadBalancer revival is a larger separate piece. No Bench Run 2.

**[Correction 2026-08-05.]** The module path `bench/take_up_slack.py` in the 7-June entry above is dead at the current HEAD. It was **renamed, not deleted**: `bench/take_up_slack.py` → `bench/routing.py` on 2026-07-12 in commit `349951f` ("A3: rename take_up_slack -> routing (code-only; behaviour byte-identical)"). Verified by `git log --diff-filter=D --name-only -- bench/take_up_slack.py` (returns `349951f` alone) and `git log --diff-filter=A --name-only -- bench/routing.py` (added in the same commit). The 12-July resume pointer above already records this rename; the 7-June entry is left intact as the record of that date. The *config key* `take_up_slack_enabled` is NOT dead — it is still accepted as a back-compatible alias for `routing_enabled` on both ingestion paths (`bench/launcher_core.py:216`, `bench/reference_runner_v2.py:760`), and the Exp 42–49 configs still carry it, so `42_composer_takeupslack.json` still loads.

**Prior update.** 7 June 2026 12:19 BST. **CLEAN NO-FAKING RUNNER BUILT — CONFIRM-only falsifier gate.** Verdict-correctness audit of the 15 Exp-42 residuals showed a one-sided error profile: **CONFIRMED 7/7 correct, REFUTED 1/3** (C0028/C0040 = real defects falsely REFUTED by clean-exiting broken falsifiers — false-REFUTED masking). **The first proposed fix (independent-falsifier scrutiny) FAILED its own test** — gpt-5.5 also refuted the real defects single-shot; a lone falsifier falls into the same traps. **Shipped fix = CONFIRM-only** (`0a4d8ce`, `apply_falsifier_verdicts`, gated): a critical is resolved ONLY by a CONFIRMED demonstration (active AssertionError/FALSIFIED, unfakeable); REFUTED on a critical → HIL, NEVER dropped; REFUTED on a non-critical still trusted. Eliminates false-REFUTED masking **structurally**. 141 falsifier/gate tests pass. **Validation (CONFIRM-only + max-3 honest retry on the 15 residuals): 8 CONFIRMED (real defects, incl. C0019 which the OLD `REFUTED→drop` gate would have MASKED — sy-verified real over-classification defect, same class as audit-CONFIRMED C0029/C0031), 7 → HIL (genuine exceptions; C0028/C0040 sy-verified real). NO false REFUTED, NO false CONFIRMED (both checked).** **Honest convergence verdict — 2 gates:** (1) no unverified critical pending — 8 CONFIRMED clear it, the 7 HIL'd BLOCK it until the human adjudicates; (2) panel quiescence (3 zero-new-critical rounds) — SEPARATE, Exp-42 `novel_this_round` 15→1 (approaching, never zero). **CORRECTION (12:50 BST) — the "7 → HIL" floor was WRONG; the HIL floor on this target is ZERO.** Founder challenged it; a 14-agent workflow (`wf_f046bc18`) had a CAPABLE writer investigate each of the 7 (read real `composer.py`, write + RUN a correct falsifier via `reverify_falsifier`, adversarially re-check): **ALL 7 → CONFIRMED real defects, 0 genuinely un-resolvable** (re-run independently: 7/7 CONFIRMED). HIL categories: **2 DUPLICATE** (C0028↔CONFIRMED C0003 in-place-mutation comparison; C0015↔CONFIRMED C0001 hallucinated import) + **5 none_resolvable** (model-capability gaps: C0040/C0036/C0054 wrote NO falsifier, C0063 truncated at 97 chars, C0034 hallucinated API). **0 genuinely_hard_to_falsify, 0 safety, 0 core_functionality, 0 uncertain, 0 contested.** Why the max-3 retry got 1/8 but this got 7/7: the retry RE-ASKED THE SAME WEAK SOURCE MODELS; fix = **route un-confirmed criticals to a CAPABLE falsifier-writer (not the source model) + iterate**, plus **deduplication** (a residual whose defect is already CONFIRMED elsewhere is never escalated). With those, gate 1 clears with **zero HIL** on this target; gate 2 (quiescence) still needs severity calibration. Genuine-HIL categories are real but live in OTHER targets (concurrency/timing, safety, authority), not these 7. Notes: `Falsifier_CONFIRM_Only_Design_2026-06-07.md` §6 (corrected) + `_Plain_English_` + TTS. Commits `0a4d8ce` gate, `3545da8` notes, `9381980` harness. **RESUME POINTER (7 June 12:50 BST):** (a) **retry-ROUTING fix** — re-dispatch un-confirmed criticals to a capable writer (strongest model / iterative agent), NOT the source model (validated out-of-band 7/7; wire into runner round loop); (b) **deduplication** of residuals against already-CONFIRMED findings; (c) severity calibration (help gate 2); (d) optional Exp 42 resume to watch gates close live. Founder still gates reviewing what Exp 40–54 entail before further full runs. No Bench Run 2.

**Prior update.** 7 June 2026 01:35 BST. **EXP 42 COMPLETE — falsifier mechanism PROVEN on a full 12-round run; did NOT converge (over-production of un-falsifiable criticals).** 12 rounds / 3h28m, gate ON, static composer (`apply_fixes_back=false`). **42 CONFIRMED + 1 REFUTED** by the runner re-running real tools (spot-checked genuine: import the real `cdsfl_registry.composer` module, re-verify CONFIRMED deterministically — NOT gamed), 41 CLOSED, 67 canonical. **0 empties, 0 false-confirms, 0 crashes, 0 fallback-route use** — mechanism works end-to-end, tools decide not votes. Non-convergence cause: **15 un-falsifiable criticals** (sev≥0.7, no working falsifier) blocked A4 (correctly — A4 refuses convergence while unverified criticals pend). **15-agent skeptical audit (`wf_d6371c68`) vs the REAL source:** **13/15 are REAL defects** (1 false-positive C0037, 1 uncertain C0034); failure_reason = **8 buggy falsifier CODE** (relative `sys.path.insert(0,'bench')` breaking from runner CWD, non-existent module imports, truncated `import sy`, `print FALSIFIED`+uncaught AssertionError = wrong exit semantics) + 7 no falsifier; **9/15 over-rated severity** (real-but-LATENT — needs a trigger absent from all 13 real directive files). **HIL-legitimacy (founder's Q; `rg`'d the categories — fix-sign-off for safety/core-functionality, irreconcilable-disagreement, UNCERTAIN, contested, reopen; minimal-HIL principle `feedback_hil_fatigue`):** the 15 are **AVOIDABLE, NOT legitimate HIL** — none is a safety / core-functionality / genuine-uncertainty escalation; they are real bugs the PANEL should have resolved (working falsifier + severity calibration). Minimal-HIL IS achievable on this target; the `genuinely_hard_to_falsify` exception (concurrency/timing) did NOT occur here (0/15) but could on other code. Notes: `experimental_notes/Exp42_Results_2026-06-07.md` + `_Plain_English_` + TTS `~/Desktop/CDSFL_tts/Exp42_Results_and_HIL_Question_2026-06-07.txt`. **RESUME POINTER (7 June 01:35 BST) — NO experiments auto-started; FOUNDER GATES:** (a) review what Exp 40–54 actually entail (founder wants this before further runs); (b) falsifier-QUALITY fixes — harness hardening (run falsifiers from repo root + inject import scaffolding → rescues the `sys.path`/import ERROR class for free), falsifier-debug retry (feed the runner's ERROR stderr back to fix the test, à la `_falsifier_format_repair` but for ERROR not just missing), severity calibration (latent/conditional defects < 0.7); (c) convergence-policy decision (should a real-but-latent un-falsifiable defect BLOCK convergence, or be triaged HIL-without-blocking?). **No Bench Run 2.**

**Prior update.** 6 June 2026 21:18 BST. **RUNNER HARDENED — FALSIFIER MECHANISM NOW WORKS FOR ALL 5 MODELS; CLEAN RUNNER.** The 3-June Exp 42 (run2) surfaced that models produced findings but ZERO tool-testable falsifiers (the live "14 findings → all HIL" failure). Root-caused + fixed every cause this session — all gated (gate-off byte-identical), 301+ tests pass, 3 commits pushed to `exp39-experimental`. **`fbafff8` falsifier mechanism (all 5 models):** gemini empty (whole+decomposed) = reasoning-budget starvation → gate-on Phase-1 + synthesis budget floor (`_gate_turn_budget` / `_PHASE1_GATE_TOKENS=32768`, `decomposed_dispatch.py`); the empty-content retry in `_run_openai_tool_loop` now fires for reasoning models too (the `not extra_body` guard had wrongly excluded gemini) + a tool-less large-budget forced-synthesis retry. deepseek = same Phase-1 budget fix; its OpenAI tool-translation is broken (DSML `｜`-markup) → routed TEXT-ONLY both paths + a gate-on falsifier FORMAT-REPAIR retry (`_falsifier_format_repair`) that converts its prose/ATTEMPT falsifiers to runnable blocks. Synthesis SAFETY-NET: raw chunk code passed to synthesis when Phase-1 is empty. Runner now forwards `mc.extra_body` into `decomposed_dispatch` (was hard-coded None → gemini's reasoning cfg never reached the runner's decomposed path). Gate-aware §2 directive promoted to CORE (`_gate_falsifier_directive`, `reference_runner_v2.py`; runnable falsifier gate-on, byte-identical gate-off). **`1169f2b` B-Cell v2:** `_build_smt2_from_claim` matched any word before an operator ("be" from "should be <= 0.5") → grounded 0; now matches KNOWN numeric source constants (case-insensitive) → real claims z3-verify (CONFIRMED/REJECTED), non-numeric claims defer honestly (no "Cannot ground" noise). **`5e81c94` S_k:** path-less SEARCH/REPLACE blocks (model omits the file path on a single-target review) were mis-parsed → false `no_blocks_for_target`; now `_looks_like_fix_path` validates the token and path-less blocks default to the single target. **EVIDENCE:** 50-cell matrix (5 models × {whole,decomposed} × 5 runs) = 0 empties; decomposed (the runner's path) strong for 4/5 (gemini fully recovered: 0→16 confirmed testable), deepseek the laggard (1/5 testable, rest → HIL safely). 2-round Exp 42 CONFIRMATION on the real runner (`42_composer_confirm.json`): falsifier gate 18 CONFIRMED / 0 REFUTED / 4 → HIL, A4 fail-safe blocked false-convergence, **`persistent_empty_flags: 0`, `secondary_route_usage: 0`** — no empty/worthless output, tools decide not votes. Note: `experimental_notes/Falsifier_Mechanism_Progress_2026-06-06.md`. **HONEST BOUNDARIES (non-blocking):** the whole path yields fewer testable falsifiers than decomposed (runner decomposes the composer → moot for Exp 42; flagged for small-payload work); deepseek weakest reviewer; some fixes report `search_not_found` = models' imperfect SEARCH reproduction (moot on a static target, `apply_fixes_back=false`). **RESUME POINTER (6 June 21:18 BST):** full 12-round pre-registered Exp 42 (`42_composer.json`, gate ON, static composer) LAUNCHING now under cy monitoring. **STOP after Exp 42 — report results, then review what Exp 40–54 actually entail (founder wants to examine the experiment contents before further runs). No auto-start of further experiments. No Bench Run 2.**

**Prior update.** 3 June 2026 10:30 BST. **ROOT-CAUSE FIX UNDER WAY — "tools decide, not votes."** A forensic divergence study (6-model panel, verdict SOUND-WITH-CAVEATS) located where the project first left its founding principle: truth-by-discussion (the CONFIRM/CHALLENGE model vote) had quietly replaced truth-by-tools, because the system permitted natural-language findings that no tool could parse — which *forced* a vote. Founder-approved fix = "(a)+(b) with strong caveats": (a) models actively use an `execute_python` tool to check/iterate findings; (b) every critical finding carries a runnable FALSIFIER that **imports the REAL target module**, and the RUNNER independently re-runs it — the runner's verdict decides, NEVER the model's prose claim. Un-toolable criticals → HIL, never voted. Built + committed, **gated default-off (byte-identical when the flag is off)**: falsifier components at HEAD `ed12c7f` (`bench/falsifier_verify.py` reverify truth-decider; tool-call loop in `experiment_11_orchestrator.py`; `FALSIFIER:` parse in `runner_core.py`; `Finding.falsifier_code/_verdict`); the **voting-replacement** at HEAD `4fba6cc` (`apply_falsifier_verdicts` gated override + `RunnerConfig.falsifier_gate_enabled` + register wiring; 10-case regression test `bench/tests/test_falsifier_gate.py`; **346 runner/convergence tests pass**). A real auto-confirm bug was caught in review and fixed: a BROKEN falsifier (bad import / typo / syntax error) must return ERROR, never auto-CONFIRM — CONFIRMED now requires the falsifier's *designed* demonstration (AssertionError / FALSIFIED token). DONE + INDEPENDENTLY VERIFIED (CC1 re-ran the smoke test, not a rubber-stamp): the `execute_python` tool is threaded into the **live** experiment dispatch (`dispatch`→`_dispatch_worker`→`dispatch_to_model`→`_dispatch_single_model`, gated by `enable_tools` sourced from `cfg.falsifier_gate_enabled` at the star/relay round dispatchers; **default-off byte-identical** — `if tools:` guard skips the loop; ruff delta 0; **362 tests pass**); the directive carries a new "Runnable Falsifiers for Critical Findings" section (real-module import + fail-iff-defect + run-via-`execute_python` + runner-decides + missing→HIL); `bench/exp42_configs/42_composer.json` now sets `falsifier_gate_enabled: true`. The integrated smoke test (`bench/smoketest_dispatch_integrated_2026-06-03.py`) PASSED on BOTH dispatch paths — **the `execute_python` subprocess runs from INSIDE the multiprocessing daemon worker** (the single key risk — confirmed viable), the model attaches a real-module falsifier (fallback unused), and the runner's independent re-run decides CONFIRMED, not a vote. **RESUME POINTER (3 June ~11:10 BST):** Exp 42 was launched ~10:57 BST; **cy monitoring caught at round 0 that the DECOMPOSED-dispatch path (large targets above the 80K-or-fingerprint decompose threshold; the composer target is 60K) never received the `execute_python` tool** — so on large targets models *reason* rather than *run* falsifiers (the (a)-half gap). The runner still re-runs every falsifier and decides on ALL paths, so the core (b) "tools decide" holds and stays SAFE (an un-self-tested buggy falsifier → ERROR → HIL, never a false-confirm); small targets use the tooled path and are unaffected. Founder chose **FIX-FIRST** (clean first-result validation, no (a)-gap confound). **DONE + COMMITTED `da8c1a6`:** `execute_python` added to the decomposed/multiturn **synthesis turn** per-API (`_decomposed_openrouter`/`_decomposed_deepseek` via the shared `_run_openai_tool_loop`; `_decomposed_claude_cli` via `--allowedTools Bash Read` on the final turn; threaded through `_multiturn_fallback`), **decomposition kept intact** (Exp 39 confound), gated default-off (301 tests pass; ruff delta 0). **Plus a crap-out fix** in `_run_openai_tool_loop`: a model requesting tools on every iteration returned EMPTY on max_iters exhaustion (a crapped-out round) — now forces one tool-less final call so it always returns its synthesis (2 regression tests; hardens BOTH dispatch paths). **Exp 42 RELAUNCHED ~12:06 BST** (`python3 bench/launch_exp42.py --config 42_composer.json`; launcher log `/tmp/exp42_composer_run2_2026-06-03.log`; runner logs `bench/logs/exp42_composer_20260603T110641Z`); round 0 confirmed **`[tools-on synthesis]` on all 5 models incl. CC2/claude_cli `[tools-on]`** — the fix is live in the run. **NOW: cy-monitoring** (persistent event monitor on round boundaries + per-round falsifier-gate verdicts + failures/fallbacks). Watch list: falsifier-adherence on the decomposed path (poor adherence → no-falsifier criticals → HIL → could stall convergence, since the pass condition requires no unverified criticals pending) + the CC2/claude_cli tool path (not openrouter-smoke-tested) + the crap-out path. `pr` on non-convergence. **STOP at the PoC — no Bench Run 2.** **STOP at the PoC — do NOT run Bench Run 2** (it needs its own design discussion; a pre-BR2 `pr` question is already noted: "how do we make the system more useful for STEM topics"). Paired divergence notes: `experimental_notes/Divergence_Study_Complete_2026-06-03.md`, `Project_Divergence_Analysis_2026-06-03.md`, `Divergence_Panel_Synthesis_2026-06-03.md` (each + `_Plain_English_` + TTS in `~/Desktop/CDSFL_tts/`). `pr` MC command registered (panel review; no compelled convergence; CC1 participates + synthesises).

**Prior update.** 23 May 2026 01:35 BST. **EXPERIMENT 41 CONVERGED CLEANLY (founder's core goal met).** `exp41c_first_principles` (target the now-fixed `bench/dm/_convergence.py`) reached `GAMMA_ALT_CONVERGED` at round 6 (zero-novel-critical count path; gamma 0.000→0.240 load-bearing; 22 canonical, 4 CLOSED, no empties, no secondary route). Path: convergence-detector fixes (`0901fd5`: `kappa_rate` novel-decline rewrite; embedding-floor `effective_tau_sim` wired into `_convergence.py`/`_similarity.py`/`_manager.py`; software verifier shadow→live) + first-principles runner gate (`86587f4`: genuine settled novelty feeds gamma + state gate + γ-alt) + gamma restored load-bearing (`4b97be0`: `gamma_alt_threshold` 1.1→0.30, trigger-not-blocker). Two 5-model confers: fix-verification 5/5 SOUND / SOUND-WITH-CONDITIONS; gamma-unification 5/5 SOUND-WITH-CONDITIONS, IMPOSSIBILITY-RISK LOW. **This sv pushes HEAD `4b97be0` (15 commits) to origin.** PENDING (founder go-ahead, maths-model-adjacent): gamma-unification implementation — headline gamma on the genuine-critical series, keep the count as the OR safety guard, do not raise 0.30, do not collapse to a gamma-only gate. PENDING (founder HIL): materiality of the C0015 / C0017 footnotes. **NEXT: Exp 42** (`bench/cdsfl_registry/composer.py`, S_k expert encodings), now unblocked.

**Prior update.** 15 May 2026 22:30 BST. Post-continuation 12-item fix tranche executed under full MC discipline (cc2 cx ge cgpt ds sq f sy p t). 9 engineering items complete; architectural confer completed via mandated local-P-pass fallback (Codex CLI unstable in env); Exp 40 R17–R21 resume + live confer surfaced as founder decisions (cost/supervision gates). 229 regression tests pass across the tranche + 8 pre-continuation fixes + adjacent suites. New module `bench/merge_arbitration.py` (G7, default-disabled). 6 new test files. Paired fix-tranche post-mortem written: technical `experimental_notes/Exp40_Fix_Tranche_Postmortem_2026-05-15.md`, plain-English `..._Plain_English_2026-05-15.md`, TTS `~/Desktop/CDSFL_tts/Exp40_Fix_Tranche_Postmortem_2026-05-15.txt`. **sv landed: HEAD `b13dd6d` pushed to `origin/exp39-experimental`** (3 sv commits this session: 7ecbf26 tranche, 553d41d tracker, b13dd6d confer) (137 files: tranche + 6 test files + 4 post-mortems + run logs + regenerated state; ONBOARDING/RECOVERY/ce_state updated). Codex CLI restored to 0.130.0 (notarized, authenticated). Working tree clean post-sv.

**Earlier update.** 15 May 2026 05:30 BST. Experiment 40 continuation run completed (ran 03:15:48 → 05:20:26 BST, 7,478 seconds, exit code 0). Wall-clock cap fired at Round 17 boundary. Seven rounds completed in this leg (R10–R16); 17 rounds total across both legs of Exp 40. γ-decay reached 0.034 (deep converged regime); γ-alt boolean not met. Seventeen BUGZILLA verified CLOSED transitions. Six D4 MERGE DEADLOCK escalations to HIL — G7 evidence cluster now in hand. Paired post-mortem written: technical at `experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md`, plain-English at `experimental_notes/Exp40_Continuation_Postmortem_Plain_English_2026-05-15.md`, TTS at `~/Desktop/CDSFL_tts/Exp40_Continuation_Postmortem_2026-05-15.txt`. HEAD prior to post-mortem write: `3bbf2c7`. Working tree carries the run's untracked log files + the three new post-mortem documents.

---

## Recovery-first card

After compaction or a long break, read in this order:
1. **This file, end to end.**
2. `git log --oneline -10 && git status` in `Constraint_Engineering/`.
3. `python3 -m open_brain.cli session-context --agent cc`.
4. **The ★ RESUME POINTER block at the top of this file — that is the resume point.** The FIRST one is current; every pointer below it is trail. Do not take the resume point from any section further down: the "Active work queue" section is a closed 22 April 2026 shift, and the "Completed in current window" log is ordered newest-near-top, so its tail is stale — the log's last entry is 15 May 2026, not the newest.
5. **READ `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` FIRST — it is the live queue.** This file carries state; the queue carries what is open. Neither substitutes for the other.

**Standing instructions are inherited, not left behind.** When the resume pointer is advanced, every standing instruction in the pointer it supersedes must be copied into the new one. An agent that correctly treats everything below the current pointer as trail will never see an instruction stranded in an older block. The live-queue line above was stranded exactly that way on 2026-08-04 and again on 2026-08-05.

Do **not** re-read the consolidated plan before this file; the consolidated plan is for detail, this file is for state.

---

## Open items carried forward from the 22 April work queue

Lifted from "Active work queue (22 April 2026 overnight shift)" further down this file, which is
otherwise fully checked off and therefore easy to skip. **Phase F is the only part of that 22 April 2026
shift still open.** It is not the current resume point — it is the Bench Run 2 consolidation work to do
whenever the Exp 40–54 arc and the founder review release it. This copy is the live one; the copy in the
closed shift below is trail. Founder has not ruled on the shift section itself, so nothing there is deleted.

- [ ] **F1.** Read `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` Section XI end-to-end.
- [ ] **F2.** Consolidate the 27 frontier STEM problem sets into this file.
- [ ] **F3.** Nail down per-task: domain, claim-cluster, expected tool routing, falsifiability criterion.

---

## Canonical anchors

> **Canonicality of this tracker flipped to the repo copy (founder ruling, 2026-08-06).** The repo copy wins because the tracker carries the recovery path, and an unversioned file on one machine's Desktop is a single point of failure. Both copies stay byte-identical; the Desktop copy is still the convenient one to open, but it is no longer the authority.

| Resource | Path |
|---|---|
| This file — **CANONICAL** (self-consumption tracker) | `Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md` |
| Desktop mirror of this file (byte-identical; convenient, not the authority) | `~/Desktop/CDSFL_Agent_Operational_Plan.md` |
| Detail plan (prose, for human + mixed audience) | `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md` and `Constraint_Engineering/experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` (byte-identical) |
| Note standard — CURRENT (v1.2, locked 14 May 2026) | `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_note_standard_v1.2.md` |
| Note standard — archival (v1 locked 21 April 2026, v1.1 locked 10 May 2026; superseded, do not write to these) | `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/cdsfl_note_standard_v1.md` and `cdsfl_note_standard_v1.1.md` |
| Global CLAUDE.md (user-level directives) | `~/.claude/CLAUDE.md` |
| Project CLAUDE.md | `Constraint_Engineering/.claude/CLAUDE.md` |
| MEMORY.md index | `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/MEMORY.md` |
| Project state file | `~/.claude/projects/-Users-georgejackson-Developer-Projects/memory/ce_state.md` |
| RECOVERY.md (repo-level recovery protocol) | `Constraint_Engineering/resources/RECOVERY.md` |
| ONBOARDING.md (repo-level project context) | `Constraint_Engineering/resources/ONBOARDING.md` |
| Mathematical appendix | `Constraint_Engineering/docs/MATHEMATICAL_APPENDIX.md` |
| Architecture doc | `Constraint_Engineering/docs/ARCHITECTURE.md` |
| Glossary | `Constraint_Engineering/docs/GLOSSARY.md` |
| Canonical 4-phase execution plan (Phase C = BR2) | `Constraint_Engineering/experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` Section XI |
| Runner v2 (active Exp 40–54) | `Constraint_Engineering/bench/reference_runner_v2.py` (4922 lines) |
| Runner v1 (frozen Exp 38/39 baseline) | `Constraint_Engineering/bench/reference_runner.py` |

---

## Superseded resume pointer (2026-05-23 state snapshot — retained for trail)

> **NOT CURRENT — do not act on this section.** It was the state snapshot on 2026-05-23 and it says Exp 42 is next; the arc has since been renumbered and run well past that. Live state is the ★ RESUME POINTER block at the top of this file: the FIRST one is current, everything below it is trail. Live work queue is `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md`.

- **Branch.** `exp39-experimental`
- **SUPERSEDED (2026-05-23, post-Exp-41 convergence — retained for trail; the HEAD / RESUME-POINTER bullets below are pre-launch history, superseded by this entry).** HEAD `4b97be0` (about to be pushed by this sv; 15 commits ahead of origin). **Exp 41 CONVERGED cleanly** — `exp41c_first_principles` reached `GAMMA_ALT_CONVERGED` at round 6 (zero-novel-critical count path; gamma 0.000→0.240 load-bearing; 22 canonical, 4 CLOSED, no empties, no secondary route). Detector fixed (`0901fd5`), first-principles runner gate (`86587f4`), gamma restored load-bearing (`4b97be0`). **RESUME POINTER:** (1) optional founder-gated gamma-unification implementation — headline gamma on the genuine-critical series, keep the count as the OR guard, threshold 0.30 unchanged, no gamma-only gate; (2) founder HIL on C0015 / C0017 materiality; (3) **Exp 42** next (`bench/cdsfl_registry/composer.py`, S_k expert encodings), now unblocked. Full detail: RECOVERY.md "Current Pending Work (22–23 May 2026)".
- **HEAD (2026-05-22, pre-launch — SUPERSEDED 23 May, see CURRENT above).** *About-to-commit*: 15 Exp 40 fixes harvested into `bench/dm/_feedback.py` (full-suite-gated, +854 chars); 3 Exp 40 hardened configs flipped to `apply_fixes_back_enabled: false` (static target); `cdsfl_core_formal.md` §10 added (compelled-convergence sufficiency assessment); `bench/exp41_configs/41_convergence.json` + `bench/launch_exp41.py` created. Predecessors: `86234b3` (Exp 40 campaign synthesis), `5fe9101` (B→C seam fixes), `86470a5` (reconstruction-bypass removal + DeepSeek direct), `e0272c6` (primary/secondary route fallback architecture). Not yet pushed to origin (sv not invoked this window).
- **RESUME POINTER (SUPERSEDED 23 May — Exp 41 has since CONVERGED; see CURRENT bullet above).** Original pre-launch pointer: **EXPERIMENT 41 IS READY TO LAUNCH.** Target: `bench/dm/_convergence.py` (437 lines, ConvergenceDetector — bounded-mathematics module). Launch command: `python3 bench/launch_exp41.py --config 41_convergence.json` (dry-run first if desired: append `--dry-run`). Methodology: STATIC TARGET (apply-fixes-back-during-review off, per founder direction 2026-05-22); COMPELLED CONVERGENCE (§10 of `cdsfl_core_formal.md`); PRIMARY/SECONDARY ROUTE FALLBACK on every model (no benching); RECONSTRUCTION BYPASSES REMOVED; HARDENED GATE with frozen pre-registered defaults identical to Exp 40. Exp 41 is the first experiment under the corrected methodology and serves as the cleanest methodology-validation test — bounded mathematics has a naturally exhaustible solution space, in contrast to Exp 40's open-ended parser slice.
- **RESUME POINTER.** Exp 40 plan-D hardened-gate campaign **COMPLETE** (all 3 faithful units run + synthesised + paired-noted). Faithful decomposition = 3 natural units (AST-verified, not 7 atomic fragments). Authoritative outcomes (`report.json` per unit): **Unit B `detect_finding_id_collisions` CONVERGED** (`HARDENED_CONVERGED at R3`, sparsity-fallback, cum_critical=4<8, γ_crit reported-not-gated; 4 apply-back). **Unit A `parse_admissibility_block` NOT converged** (hardened re-run; full mode cum_critical→18; loo_min flat 0.0 R3–R11; 7 apply-back; 12 rounds; supersedes prior un-hardened/falsified plan-F runs). **Unit C cluster NOT converged** (1st run outage-terminated R5 = infrastructure not verdict; clean re-run 12 rounds, full mode cum_critical 14–15, loo_min 0→0.20 never 0.25; conjunction empirically vindicated R8/R9→R10; 8 apply-back). **Central result: the hardened conjunction is empirically anti-cooking** — a legacy γ-alt OR gate would have converged all 3; the conjunction converged only the genuinely-exhaustible unit and refused A/C where γ_crit decay is not leave-one-round-out robust; Unit C's R8/R9→R10 sequence directly refutes the OR-gate convergence. Paired notes: `experimental_notes/Exp40_Hardened_Gate_Campaign_2026-05-18.md` (+ `_Plain_English_`) + TTS `~/Desktop/CDSFL_tts/Exp40_Hardened_Gate_Campaign_2026-05-18.txt`. **NEXT: Exp 41 recommendation = PROCEED** (hardened gate validated; non-blocking follow-ups carried forward, not blockers).
- **Two runner-class defects found live + fixed at the B->C seam (commit 5fe9101):** (1) `CircuitBreakerTripped` not pickle-safe → TypeError across `dispatch_to_model`'s mp.Queue → circuit breaker silently inoperative arc-wide (root-caused, P-passed, `__reduce__` added, regression test). (2)+(3) hardened/γ-alt convergence set only the result dict, not `brain.state.converged`/per-round flag → launcher printed "no convergence"+exit 1 and `completion_signal.json` wrote INCOMPLETE for a converged run (both fixed). All three are F6 clause-3 verification-integrity (reporting/serialization layer); none corrupts the measurement.
- **Test count.** Gate-hardening 8 tests; plan-D focused suites 56 + adjacent 58; seam-fix 18 (incl. real mp.Queue round-trip). All green; zero new ruff (delta=0 per modified file vs HEAD).

---

## Standing rules (non-negotiable, every turn)

1. **Multi-tool cross-verification.** Every computational claim verified with at least two relevant tools where available. Pairings:
   - Math: **SymPy + Wolfram** (Wolfram via MCP, local-only, not part of CDSFL infrastructure).
   - Stats: **scipy.stats + statsmodels**.
   - Symbolic / constraint logic: **SymPy + z3**.
   - Dimensional analysis: **pint + astropy.units**.
   - Chemistry structure: **rdkit + regex-based parser cross-check** (no second equivalent tool installed).
   - Biology sequence: **biopython + (regex for sequence-validity subset)** (no second equivalent tool installed).
   - Optimisation: **PuLP + scipy.optimize**.
   - Behavioural code: **crosshair + pytest**.
   - Numerical precision: **NumPy + mpmath** (for precision cross-check).
   - Code structure: **AST + inspect + dis** (stdlib).
2. **1E.10 catch (standing).** "1E.10" in the CDSFL plan is **Plan Item 1.E.10**, NOT scientific notation `1e10`. A 21 April 2026 misreading propagated "ten billion" language through multiple notes. Treat every "1E.n" token as an item reference unless proven otherwise.
3. **Scientific notation in plain-English notes.** When a genuine large number appears, use `1×10^N (number-words)` format, e.g. `1×10^10 (ten billion)`. Verify exponent–word correspondence before writing (10^7 = ten million, 10^10 = ten billion).
4. **Note standard v1.2 (current working version, locked 14 May 2026; v1/v1.1 archival).** Every TTS and experimental-notes markdown ends with the foot-line `Written under CDSFL note standard v1.2 (14 May 2026).` Rule 12: substantive technical notes carry a technical markdown PLUS a plain-English companion PLUS the TTS mirror. 12 rules summarised in project CLAUDE.md; full text in `cdsfl_note_standard_v1.2.md`. (Rule reference updated 2 July 2026; was stale at v1.)
5. **FFAFP for any untested claim.** Find → Follow → Analyse (with available tools) → Fix → P-pass. Applies to every proposed fold-in of an Exp 39 / confer-round outstanding item.
6. **Multi-tool is for computational claims specifically.** Rhetorical or stylistic choices do not get tool-verified; aesthetic fitness review, prose precision review, or design review applies (per user CLAUDE.md `rigour-universal`).
7. **`cy` monitoring contract (standing directive 2026-05-18).** `cy` is no longer bare "continue". It means: continue the work AND, whenever an experiment/process is running, monitor it at ~60-second cadence; on anything screwy or off, pause the process, FFAFP it (analyse fully with all available/relevant tools), apply the fix, then resume; and always keep a terminal window open pointing to the full current tail output of the running experiment for the founder to review. Recorded in global CLAUDE.md, project CLAUDE.md MC table, MEMORY.md shorthand.

---

## Founder-invocable modes (NOT standing — off unless the founder says otherwise)

- **`sq` — strictly sequential tool use.** One tool call per message, no parallel batches; sub-agents dispatched while it is in force inherit the same constraint. **It is manually invoked by the founder on an as-needed basis and is NOT in force by default.** It was listed as standing rule 1 here until 2026-08-06, which made every post-compaction agent adopt one-call-per-message permanently and impose it on its sub-agents. **Founder ruling 2026-08-06:** the aim was to prevent Anthropic server overloads, but experience has shown there is probably very little that can be done about these — it is a matter of Anthropic server capacity (and other issues) upstream, and is unlikely to be the result of anything done here. In those cases the only option is usually to wait for Anthropic to fix it. That finding is recorded rather than deleted so the rule is not re-derived from first principles in six months.

---

## Per-experiment target-article matrix (nailed down)

> **★★ THE 20-JULY MAP BELOW IS ITSELF WRONG — CORRECTED 13 August 2026 against the run record.**
> Founder-flagged. The renumbering notice below was written to stop exactly this confusion and
> has been propagating a different version of it since 20 July. **Ground truth is the set of run
> directories under `bench/logs/`, because those are what actually executed.** Measured today:
>
> | Exp | What actually ran | 20-July map said | Verdict |
> |---|---|---|---|
> | 44 | `exp44_evidence_locationkey_live` (`evidence.py`) | `dm/_memory.py` | **WRONG — 44/45 swapped** |
> | 45 | `exp45_memory_statistics_live` (`dm/_memory.py`) | `evidence.py` | **WRONG — 44/45 swapped** |
> | 46 | `exp46_stage6_locationkey_live` | `dm/_shadow_stage6.py` | correct |
> | 47 | `exp47_divergence_locationkey_live` | `dm/_divergence.py` | correct |
> | 48 | `exp48_chemistry_exam_live` | biology | **WRONG** |
> | 49 | `exp49_engineering_exam_live` | physics | **WRONG** |
> | 50 | not started — **physics** | chemistry | **WRONG** |
> | 51 | not started — **biology** | engineering | **WRONG** |
> | 52 | not started — 2×2 factorial capstone | 2×2 factorial | correct |
> | 53 | `exp53_control_zero_live` — **zero-plant control**, paused | absent from the map | **MISSING** |
>
> **The authoritative sequence is `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md` section C**,
> which matches the run record on every row it covers. The two notices below are retained as the
> trail, not as guidance. Consequence had this gone unnoticed: an agent following either the table
> or the 20-July map would re-run three completed experiments and would run an engineering
> configuration in the slot the control occupies.
>
> Also corrected: Stage 6 is NOT a future experiment 50. It ran as experiment 46. Any plan text
> describing a forthcoming Stage 6 calibrator study is stale by that fact.
>
> *(Desktop mirror re-syncs at next `sv`.)*
>
> **★ NUMBERING SUPERSEDED (20 July 2026) — this table uses the ORIGINAL Exp 40–54 scheme.** The arc was RENUMBERED + LOCKED on 20 July: the two composition/interface tests (old 44 + old 49) were DROPPED (redundant — every run already exercises the whole integrated system), and the numbering closed up. **Authoritative current sequence: the 20-July CURRENT STATE block in `resources/RECOVERY.md` and the header of this file.** Map (new# = [old matrix#]): NEW 44 = `dm/_memory.py` [old 45, the shake-out] · NEW 45 = `evidence.py` [old 48] · NEW 46 = `dm/_shadow_stage6.py` [old 50] · NEW 47 = `dm/_divergence.py` [old 46] · NEW 48–51 = biology/physics/chemistry/engineering synth modules, TO DRAFT [old 47/51/52/53] · NEW 52 = 2×2 factorial [old 54]. The rows below are retained for their file-location / size / routing detail only; read the numbers via this map. (Repo mirror re-syncs to this at next commit.)

Status legend: FIXED (specific, stable, ready) | PROVISIONAL (specified, scope TBC) | UNDECIDED (no target yet).

| Exp | Target article / module | File location | Status | Notes |
|---|---|---|---|---|
| 40 | §17 feedback directive (base for Gate A, first live exercise) | `bench/dm/_feedback.py` | FIXED | Pre-launch F1–F4 closed. Gate C preflight wiring pending. Founder launch approval pending. |
| 41 | Bounded mathematics module | `bench/dm/_convergence.py` (or `_suppression.py`; size confirmed post-Exp-40) | FIXED (conditional size) | Mathematics calibration target. |
| 42 | Expert encodings S_k | `bench/cdsfl_registry/composer.py` | FIXED | S_k admissibility across vendor encodings. |
| 43 | Macrophage admissibility (bounded ~20K char unit) | `bench/macrophage_cell.py` (whole file, 547 lines / ~22K, 15 AST symbols, self-contained stdlib-only) | FIXED | Verdict-wiring confirmation under live load. **CORRECTED 2026-06-10:** macrophage lives in `macrophage_cell.py`, NOT `immune_agents.py` (which has 0 macrophage code). Config: `bench/exp43_configs/43_macrophage_locationkey_live.json` (wiring pre-flight-verified; gated on model API keys). |
| 44 | Composition test (no new target) | Synthetic, combines Exp 41 + 42 + 43 outputs | FIXED | Mechanical interface check. |
| 45 | Statistics specialist | `bench/dm/_memory.py` (beta-binomial memory + CUSUM) | FIXED (conditional size) | `statsmodels + scipy + uncertainty_propagation` per `domains/immune/statistics.toml`. |
| 46 | §18 divergence directive | `bench/dm/_divergence.py` | FIXED | §18 live since Exp 39; module is also the test article (self-referential). |
| 47 | Synthesised native biology module | To be drafted; ~15–25K chars | FIXED target-strategy (panel 21 April) | **Scope brief below.** Biology specialist routes: `sympy + biological_sequence + dimensional_analysis`; `z3` for logical; `statsmodels + scipy + uncertainty_propagation` for statistical. Per `domains/immune/biology.toml`. |
| 48 | Information-science specialist | `bench/evidence.py` (641 LOC, ~23K chars) | FIXED | Information-science B-Cell specialist. |
| 49 | Cross-domain synthesis (no new target) | Synthetic, combines Exp 41 + 45 + 46 outputs | FIXED | Mathematics + statistics + CS integration. Post-mortem watch-item: three alternative orderings (Gemini §18-first, ChatGPT swap 46/48, DeepSeek stats adjacent 41) if tier inconsistencies surface. |
| 50 | Microglia / Stage 6 calibrator (self-referential) | `bench/dm/_shadow_stage6.py` | FIXED | Ouroboros query-quality fix prerequisite — cross-verified at entry gate. |
| 51 | Synthesised native physics module (K, shadow) | To be drafted; ~15–25K chars | FIXED target-strategy (panel 21 April) | **Scope brief below.** DeepSeek composer.py candidate withdrawn (lacks dimensional density). Physics B-Cell (K, shadow) routes: `sympy + dimensional_analysis + astronomical`. Per `domains/immune/physics.toml`. |
| 52 | Synthesised native chemistry module (L, shadow) | To be drafted; ~15–25K chars | FIXED target-strategy (panel 21 April) | **Scope brief below.** Chemistry B-Cell (L, shadow) routes: `chemistry_structure` (RDKit) + `dimensional_analysis`. Per `domains/immune/chemistry.toml`. |
| 53 | Synthesised native engineering module (M, shadow) | To be drafted; ~15–25K chars | FIXED target-strategy (panel 21 April) | **Scope brief below.** Engineering B-Cell (M, shadow) routes: `sympy + uncertainty_propagation + dimensional_analysis`. Per `domains/immune/engineering.toml`. |
| 54 | Integration run with 2×2 factorial | Candidate: `bench/reference_runner_v2.py` self-test (runner-tests-runner meta) | PROVISIONAL | 2×2 factorial design locked. Cells A/B/C/D defined: A = §17 off + §18 off (Exp 36–38 baseline archive); B = §17 on + §18 off; C = §17 off + §18 on; D = both on. Cell A entry-method decision open (RQ3, 3–2 split persists; founder decides at Exp 54 entry). |

**[Correction 2026-08-05.]** The Exp 41 row above offers `_suppression.py` as an alternative target to `bench/dm/_convergence.py`. **`bench/dm/_suppression.py` was never created** — this is a deletion-free dead reference: no file of that name exists at any commit in this repository's history (`git log --all --name-only --format="" | grep -i suppress` returns nothing), so there is no replacement path to redirect a reader to. Exp 41 in fact ran against `bench/dm/_convergence.py`, the option that was taken — the three Exp 41 configs (`bench/exp41_configs/41_convergence.json`, `41b_first_principles.json`, `41c_first_principles_run.json`) name `bench/dm/_convergence.py` and no suppression module. Suppression logic in this codebase lives inside existing modules (`bench/dm/_immune.py`, `bench/dm/_convergence.py`), not in a file of its own. The row is left intact as the record of a target choice that was still open at the time.

### Target-article scope briefs (Exp 47, 51, 52, 53)

> **★ STALE — superseded by the consolidated plan §2a.** These briefs predate the Round 2 (2026-05-10) and Round 3 (2026-05-13) corrections (biology z3 cluster, codon category-error fix, `stoichiometric_balance`, engineering LP cluster + astropy removal). **The authoritative briefs live in `Exp40_to_54_Consolidated_Plan_2026-04-21.md` §2a** — brief any panel from there, never from this section (the Round-3 stale-anchor failure mode).

Each of the four synthesised native modules must embed **falsifiable** claims that exercise the routed tools. The 15–25K character budget allows 4–6 distinct claim clusters per module.

**Exp 47 — Biology (~15–25K chars, native synthesis).** Claim clusters:
1. **Sequence-validity claims.** DNA/RNA/protein sequences with assertions about validity, GC content, open reading frames, stop-codon positions. Falsifiable via `biopython` `Seq` operations + regex cross-check.
2. **Dimensional claims.** Molar mass, concentration, reaction-rate kinetics with explicit units. Falsifiable via `pint` dimensional analysis.
3. **Statistical-distribution claims.** Allele frequency, Hardy-Weinberg equilibrium, χ² goodness-of-fit. Falsifiable via `scipy.stats` + `statsmodels` cross-check.
4. **Mathematical claims.** Logistic-growth ODE with specific parameters, population-dynamics fixed points. Falsifiable via `sympy` + optional `scipy.integrate` numerical cross-check.
5. **At least one intentionally false claim** so the specialist has something to reject (e.g. a sequence labelled "protein" that contains invalid codons).

**Exp 51 — Physics (~15–25K chars, native synthesis).** Claim clusters:
1. **Kinematics claims.** Projectile motion, orbital period, free-fall timing with specific numerical values. Falsifiable via `sympy` symbolic + `pint` dimensional + `astropy.constants` cross-check.
2. **Conservation laws.** Energy conservation in elastic collisions, momentum in two-body scattering, charge invariance. Falsifiable via `sympy` + numerical bounds via `scipy`.
3. **Dimensional consistency.** Force = mass × acceleration verification, power = work / time, specific relativistic-limit sanity checks. Falsifiable via `pint` + `astropy.units` cross-check.
4. **Special-function claims.** Specific integrals, series expansions of physical quantities. Falsifiable via `sympy` + `mpmath` (arbitrary precision cross-check).
5. **At least one intentionally false claim** (e.g. a kinetic-energy formula missing the ½ factor).

**Exp 52 — Chemistry (~15–25K chars, native synthesis).** Claim clusters:
1. **SMILES validity.** Valid and invalid SMILES strings with assertions about parse success and molecular identity. Falsifiable via `rdkit.Chem.MolFromSmiles` + regex structural cross-check.
2. **Stoichiometry.** Balanced-equation claims with coefficient-sum assertions. Falsifiable via `rdkit` + `collections.Counter` atom-balance cross-check.
3. **Molecular-weight claims.** Specific molecules with stated molecular weights in g/mol. Falsifiable via `rdkit` `Descriptors.MolWt` + `pint` dimensional check.
4. **Functional-group identification.** SMARTS-pattern claims for carbonyl, hydroxyl, amine presence. Falsifiable via `rdkit` substructure matching.
5. **At least one intentionally false claim** (e.g. an unbalanced equation claimed as balanced).

**Exp 53 — Engineering (~15–25K chars, native synthesis).** Claim clusters:
1. **Load-factor calculations.** Beam deflection, column buckling, stress-strain with specific numerical values. Falsifiable via `sympy` + `pint` + `uncertainties` propagation.
2. **Material-tolerance claims.** Stated tolerance ranges for yield strength, fatigue limit, with uncertainty propagation. Falsifiable via `uncertainties` package + `scipy` for confidence bounds.
3. **Safety-factor routing.** Nominal load vs. worst-case load with specific safety-factor values. Falsifiable via manual formula re-derivation (`sympy`) + dimensional check (`pint`).
4. **Dimensional consistency.** Units across mechanical, thermal, electrical domains. Falsifiable via `pint` + `astropy.units` cross-check.
5. **At least one intentionally false claim** (e.g. a safety factor stated as dimensionless but computed with non-cancelling units).

Each module: draft ahead of its experiment's entry, not at entry. Keep as separate Markdown files under `bench/cdsfl_registry/targets/` (directory to be created when first module drafts).

---

## Exp 39 → Exp 40 gap-closure list

Eight gap items carried forward from Exp 38/39 and subsequent confer rounds. Each gets FFAFP and multi-tool verification. Fold-in status and scheduled close marked below. **Closed** = fix applied, tests added, committed.

| # | Gap | Current state | Pre-Exp-40 blocker? | Scheduled close | FFAFP status |
|---|---|---|---|---|---|
| G1 | Gate C Codex preflight wiring into Exp 40 launcher | `gate_c_preflight()` wired into `--preflight` + full-run paths; 6 tests in `test_launch_exp40.py` all green | **Yes** (blocks Exp 40 launch) | Pre-launch (this session) | CLOSED |
| G2 | K/L/M shadow-audit regression test | 11-test file pins schema + field binding + behaviour + log format; bug fix applied (claim_id/severity → finding_id/confidence) | No | Pre-launch (this session) | CLOSED |
| G3 | Ouroboros query-quality calibrator test harness | 18-test harness on Stage 6 calibrator; SymPy-verified delta + noisy-OR identities; monotone frequency scaling; epistemic tagging + API surface pinned | No (Exp 50 blocker) | This session | CLOSED |
| G4 | `open_crit_high_count()` REOPENED status handling | 11-test regression pin on v2; behaviour + purity + signature + AST source-truth; no fix needed (existing body correct) | No (v2 correctness) | This session | CLOSED |
| G5 | `contested_count()` grace_period parameter wiring | 10-test regression pin on v2; behaviour + signature + AST default + call-site purity; parameter is respected, no fix needed | No (v2 correctness) | This session | CLOSED |
| G6 | Specialist-to-specialist verdict-conflict resolution | No mechanism in v2; Exp 49 assumes one | No (Exp 49 blocker) | Exp 44 post-mortem → Exp 49 prep | Scheduled |
| G7 | MERGE deadlock auto-arbitration | D2 escalation only; no auto-merge | No (Exp 44 boundary) | Exp 44 post-mortem | Scheduled |
| G8 | Burst-mode Phase 0 convergence override | Not folded; burst disabled for Exp 40 | No | Future burst experiment | Scheduled |
| G9 | F4 closure-state labels applied across all schema elements | Lexicon section added to ONBOARDING; stale K/L/M description corrected in situ with `shadow_integrated` label; remaining mentions left for forward-going discipline rather than retroactive sweep | No (documentation) | This session (ONBOARDING sweep) | CLOSED |

---

## Active work queue (22 April 2026 overnight shift) — COMPLETED HISTORICAL SHIFT, NOT THE RESUME POINT

> **This shift closed on 22 April 2026 and is retained for trail.** Its top item, A1, is "Create this file" —
> completed and checked off. **The resume point is the ★ RESUME POINTER block at the top of this file**
> (first one is current, everything below it is trail), and the live work queue is
> `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md`. Every item below is checked off except Phase F, which is
> lifted to "Open items carried forward from the 22 April work queue" near the top of this file.

### Phase A — Plan and memory infrastructure
- [x] **A1.** Create this file at `~/Desktop/CDSFL_Agent_Operational_Plan.md`.
- [x] **A2.** Mirror this file at `Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md`.
- [x] **A3.** Link from global CLAUDE.md under new `Project Operational Trackers` section (three new directives).
- [x] **A4.** Link from project CLAUDE.md as the first `Key Documentation` item.
- [x] **A5.** Link from MEMORY.md index as first item under `Project State`.
- [x] **A6.** Link from `Constraint_Engineering/resources/RECOVERY.md` as first-read block before the Minimum Recovery numbered list.
- [x] **A7.** Captured as `memory/feedback_1e10_catch.md` and indexed in MEMORY.md.
- [x] **A8.** Captured as `memory/multi_tool_crossverify.md` and indexed in MEMORY.md.

### Phase B — Factual corrections to four broken notes
- [x] **B1.** Rewrote F1–F4 paragraph in Round 2 Plain-English markdown. F1/F2/F3 descriptions now match runtime behaviour; F4 identified as closure-state lexicon, not exception-handling tightening.
- [x] **B2.** Reframed Cell A paragraph in the Round 2 markdown: Exp 36–38 baseline archive; ouroboros standing framing with version-confound retained as the panel's measurement-level label.
- [x] **B3.** Mirrored B1 and B2 in the Round 2 TTS file.
- [x] **B4.** Rewrote F1/F2/F3 bullets in the Section 8 Decision Register markdown. F4 noted as documentation-only, landed earlier in arc. 1E.10 clarified as Plan Item 1.E.10 reference, not numerical magnitude.
- [x] **B5.** (a) Rewrote Decision 2 Cell A paragraph in the register markdown with Exp 36–38 baseline spec + ouroboros reframe. (b) Corrected K/L/M graduation line (was wrongly scoped to decision 2; now correctly bound by Round 2 non-distortion check, K/L/M flip at Exp 51/52/53 respectively).
- [x] **B6.** Mirrored B4 and B5 in the Section 8 Register TTS file.

### Phase C — Consolidated plan augmentation
- [x] **C1.** Appended `2a. Target-article scope briefs (Exp 47, 51, 52, 53)` section to `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md`. Inserted between §2 (15-experiment arc table + factorial cells list) and §3 (fold-in consolidation). Each of the four domain subsections lists 4–5 claim clusters with explicit falsifiability route and a terminal intentionally-false-claim requirement; section closes with drafting-cadence + storage-path direction (`bench/cdsfl_registry/targets/exp{47,51,52,53}_{biology,physics,chemistry,engineering}.md`).
- [x] **C2.** Appended `## 6a. Exp 39 → Exp 40 gap-closure list` to the consolidated plan between §6 (Round 2 outcome) and §7 (Appendix A). Section carries G1–G9 table with cross-references to §6 RQ items, §4 shadow-element rows, and §2 per-experiment rows. Table columns: #, Gap, Current state, Pre-Exp-40 blocker?, Scheduled close trigger, FFAFP status, Cross-reference. Section closes with per-gap multi-tool cross-verification pairings, pre-launch path (G1/G2/G4/G5/G9), and post-launch path (G3/G6/G7/G8).
- [x] **C3.** Mirrored `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md` → `~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md`. `diff -q` confirms byte-identity (exit code 0, no differing-bytes output). Both copies now include §2a (target-article scope briefs) and §6a (Exp 39 → Exp 40 gap-closure). Phase C closed.

### Phase D — Gap-closure FFAFP pass
- [x] **D1 (G1).** Wired Gate C preflight into `bench/launch_exp40.py`. Added `gate_c_preflight()` function (live-path import + schema-drift guard on `ADMISSIBILITY_GATES` + 5-case canonical matrix drawn from existing offline tests) + `--skip-gate-c` escape hatch. `--preflight` path now runs Gate C before model-connectivity check; full-run path runs Gate C before runner dispatch; `--dry-run` deliberately skips Gate C (config-only surface). New test file `bench/tests/test_launch_exp40.py` with 6 tests: 3 unit (healthy parser; schema drift detected; drift message names got + expected); 2 CLI subprocess (`--preflight` exit 0 with PASS line; `--dry-run` does not fire Gate C); 1 coverage (canonical cases align with parser truth). All 6 new + 39 existing feedback-channel tests green. **G1 CLOSED.**
- [x] **D2 (G2).** Wrote `bench/tests/test_shadow_audit_klm.py` — 11 tests across 4 classes. FFAFP surfaced a bug: the 21 April enrichment used `claim_id` + `severity` as dict keys bound via `getattr(v, ..., None)`, but neither is a `CellVerdict` field; both always resolved to None, silently losing 2 of 5 audit slots. Fix applied at `bench/immune_agents.py:5411-5421` — renamed keys to the real CellVerdict fields `finding_id` + `confidence`. Regression pins: AST-level schema check enforces exact 5-field set `{finding_id, verdict, confidence, tool_used, evidence}`; two standalone pins explicitly ban `claim_id` and `severity` from reoccurring; field-binding test uses `dataclasses.fields(CellVerdict)` to verify every key maps to a real attribute; behavioural replica covers N→N emission, evidence truncation at 256 chars, empty-string preservation; log-format pin checks the `_shadow_log` format string. All 11 pass. **G2 CLOSED.**
- [x] **D3 (G4).** Wrote `bench/tests/test_open_crit_high_count_v2.py` — 11 tests across 4 classes. FFAFP outcome: **no fix needed** to `bench/reference_runner_v2.py:447` — the existing `_NON_TERMINAL = ("OPEN", "CONTESTED", "REOPENED")` literal already handles REOPENED correctly; the gap was coverage, not behaviour. New pins: (i) five behavioural tests — REOPENED at 0.9 severity counted, at 0.5 severity excluded, mixed OPEN+REOPENED counted together, exhausted REOPENED excluded, CLOSED-high excluded; (ii) two purity tests — no `exhausted` flag mutation, idempotent under repeated call; (iii) two signature pins using `inspect.signature` + `typing.get_type_hints` (the latter because runner v2 uses `from __future__ import annotations` and raw signature returns strings); (iv) two AST source-truth pins — `_NON_TERMINAL` tuple literal contains REOPENED, OPEN, and CONTESTED. Multi-tool: pytest + inspect + typing + ast. 61 pass (D1+D2+D3+existing). **G4 CLOSED.**
- [x] **D4 (G5).** Wrote `bench/tests/test_contested_count_v2.py` — 10 tests across 4 classes. FFAFP outcome: **no fix needed** to `bench/reference_runner_v2.py:464` — the parameter is not silently ignored, the three call-sites simply use the default. Pins landed: (i) four behavioural — grace_period=1 excludes at boundary, grace_period=3 includes, implicit default matches explicit 2, grace_period=0 disables UNCONFIRMED counting; (ii) three signature — default is 2, params `[self, current_round, grace_period]`, return `int` (resolved via `typing.get_type_hints` for deferred annotations); (iii) one AST — the literal default in the source is exactly 2; (iv) two call-site — no call-site passes `grace_period=` as a kwarg literal (source-level check; all three call-sites at lines 1019/1135/1214-1215 use default), call-site count ≥ 3 sanity. Multi-tool: pytest + inspect + typing + ast + source-read. 10 pass in 0.82 s. **G5 CLOSED.**
- [x] **D5 (G3).** Wrote `bench/tests/test_shadow_stage6_calibrator.py` — 18 tests across 6 classes. FFAFP outcome: **no fix needed** to `bench/dm/_shadow_stage6.py` — the 14 April design is intact, two-dimensional reporting preserved, identities hold. Pins: (i) four public-API surface — class instantiable, `observe_round` signature `[self, round_idx, findings, immune_response, ouroboros_data]`, returns `ShadowStage6RoundLog`, empty findings yields empty log; (ii) two triple invariants — `nu_k_proxy`/`c_ext`/`h_ratio` are distinct dataclass fields, each in [0, 1]; (iii) two SymPy-verified delta identities — `sp.simplify(delta_code - delta_closed) == 0` symbolic proof that `δ = η · c_ext · (1 − ν_k)`, plus concrete anchor test comparing `_assess_finding` output to the closed form within 1e-4; (iv) two noisy-OR combiner — SymPy-verified `c_ext_raw = 1 − (1−c_s1)(1−c_s2)` → 0.65 at (0.5, 0.3), unit-interval boundedness at c_s=0 and c_s=1; (v) two frequency-scaling monotonicity — c_freq non-decreasing in encounter count, bounded at C_MAX=0.95 even after 100 repeated encounters; (vi) two epistemic tagging — no-search finding with `nu_k_proxy=0.5 < 0.6` NOT tagged SPECULATIVE, searched-empty finding with `nu_k_proxy=0.8 + c_ext≈0.224` IS tagged SPECULATIVE; (vii) four source-truth pins — GAMMA_SRC=0.7, ALPHA_FREQ=0.1, C_MAX=0.95, module docstring retains HARD 6 two-dimensional framing. Wolfram cross-check skipped (local-only per plan standing rules; SymPy closed-form proof is the HARD identity). Multi-tool: pytest + SymPy + inspect + ast + dataclasses. 18 pass in 0.76 s. **G3 CLOSED.**
- [x] **D6 (G9).** ONBOARDING closure-state label sweep — glossary + targeted-label approach. Added `## Closure-State Lexicon (F4, locked 21 April 2026)` section to `resources/ONBOARDING.md` between Standing Rules and Current State, defining `library_complete` / `shadow_integrated` / `live_operational` with one-clause examples and the shadow-promotion-now non-distortion bounding condition. Corrected the most load-bearing stale description in situ: the K/L/M shadow-audit line on line 51 incorrectly described the pre-compaction bug (`claim_id, severity`) and has been rewritten to the real `CellVerdict` fields `finding_id, confidence` with a "22 April 2026 correction" note pointing to both the fix at `bench/immune_agents.py:5411-5421` and the regression test `bench/tests/test_shadow_audit_klm.py`; line now carries the `shadow_integrated` closure label inline. Remaining ~40 shadow mentions across ONBOARDING not individually labelled — a full text sweep is judged lower value and higher risk than defining the lexicon once + correcting the one stale factual description. Any future reader of ONBOARDING has the definitions in reach; the discipline migrates forward from this point rather than rewriting history. **G9 CLOSED (documentation-only).**
- [x] **D7.** G6, G7, G8 scheduled-close trigger specifications — added new section `## 6b. Scheduled trigger specifications (G6, G7, G8)` to the consolidated plan (repo + Desktop mirror, byte-identical post-edit) immediately after §6a's post-launch path paragraph. Each gap now carries (a) explicit entry trigger with migration path if the primary trigger produces no qualifying evidence, (b) multi-tool pairings to apply on activation, (c) minimum evidence threshold for the close verdict. Table status-column updates: G1/G2/G3/G4/G5/G9 flipped from `Pending` to `CLOSED` in the same pass; G6/G7/G8 remain `Scheduled`. Section closes with a Popperian note that the arbitration rules are deliberately left unspecified — they must emerge from post-mortem evidence rather than being pre-registered.

### Phase E — Commit and continuation
- [x] **E1.** Full pytest regression run post-changes. **Result:** 56 new tests pass in 2.33 s (standalone run of the five new files); fast wall-clock-limited sweep excluding five long-running or CLI-blocking files (`test_openrouter_tools.py`, `test_deepseek_specialist.py`, `test_dynamic_management.py`, `test_ouroboros_query_quality.py`, `test_exp29_integration.py`) returns 907/907 pass in 342.12 s. Zero regressions. `test_exp29_integration.py::test_three_round_flow` confirmed hanging on Claude CLI Haiku LLM classifier (14.4 s per call, pre-existing, unrelated to overnight edits — `bench/logs/immune_pipeline.log` at 02:05:51 BST shows the overnight `finding_id`/`confidence` rename emitting correctly). Longer non-ignore sweep deferred to daylight window. [Correction 2026-07-31: this item originally called the 907 sweep "fast non-network". It was not a non-network run. The exclusion criterion was wall-clock cost, not network use, and three unmarked live-dispatch files — `test_immune_agents.py`, `test_specialist_live_promotion.py`, `test_specialist_shadow_cells.py` — were inside the 907 and made live claude-CLI Haiku calls. The 907/907 pass count stands as a record of what passed; the offline label does not, and this figure must not be quoted as reproducibility evidence. See `resources/RECOVERY.md`.]
- [x] **E2.** Update `ce_state.md` with the overnight shift results. Line 16 updated with final pass counts + pre-existing-hang provenance note.
- [x] **E3.** Update `ONBOARDING.md` and `RECOVERY.md` with the 22 April session block. Both files updated with final pass counts replacing the "TBD at sv" placeholder.
- [x] **E4.** `sv` with descriptive commit message; push to origin. Committed 991cde0 on `exp39-experimental`; 17 files committed via `scripts/cdsfl_sv.py --commit --push`, atomic push to origin succeeded at 02:14 BST.
- [x] **E5.** Final pass on this file — mark all completed items, set next resume point for morning review.

### Phase F — Bench Run 2 (deferred until Exp 40–54 complete) — STILL OPEN; live copy is "Open items carried forward from the 22 April work queue" near the top of this file
- [ ] **F1.** Read `experimental_notes/Exp36_Ground_Truth_Reference_2026-04-08.md` Section XI end-to-end.
- [ ] **F2.** Consolidate the 27 frontier STEM problem sets into this file.
- [ ] **F3.** Nail down per-task: domain, claim-cluster, expected tool routing, falsifiability criterion.

---

## Completed in current window (append at each task close)

- **2026-08-05 14:18 BST.** Full `rs` after the model point-update and relaunch. Verified: HEAD `624b39a`, tree clean, in sync with origin (0/0), no runners and no stray Wolfram kernels, `WolframCloud` live and matching its recorded landmarks, `WolframBridgeLegacy` absent from the live config. Read end-to-end: this tracker, `OUTSTANDING_QUEUE_to_BR2.md`, the RECOVERY head block, project and global CLAUDE.md. IM and Open Brain are both Genesis-era and carry nothing for CDSFL — the last Open Brain capture is 2026-08-02, so the 08-04/08-05 sessions are recorded in git and the notes only. Resume pointer advanced to carry the provenance correction, which the 2026-08-04 pointer predated.
- **29 July 2026, 08:52 BST.** BI-39 routing fragility RESOLVED (`342d37a`) — the item recorded-not-repaired in the Exp 51 biology exam repair `8500037`. Founder ruling: repair approved; BI-39's closing clause hyphenated so the control-cluster claim carries a routing trigger independent of its own BI-nn tag. Re-verified 43/43 under biopython/sympy/scipy/statsmodels/pint/z3, zero key mismatches, six planted falses byte-identical by SHA-256, routing 43/43 at 0.85 in BOTH tagged and bare form (was 42/43 bare). Applied while the arc sequencer sat on the Exp 49 leg at round 3 — Exp 50 and 51 unstarted, so no run saw a mid-flight target change. Three measured corrections to the original caveat, all in the key notes + commit body: twelve OTHER claims are equally hyphen-dependent (so BI-39 was the extreme of a 13-claim family, not an outlier); the live classifier never sees claim text, only the reviewing model's prose; and models emit NON-ASCII hyphens in ~12% of tag citations (chiefly U+2011), which match no pattern — so the tag was never a dependable trigger. A stronger-looking alternative (`61 + 3 = 64`) was falsified and rejected on tell hygiene: it would have been the module's only inline arithmetic identity, resolving to one claim at precision 1.00, planted on a control record. **Residual for a separate ruling: the arc-wide `[+\-*/^]` class question — narrowing it invalidates four validated keys mid-arc, widening it routes em-dash punctuation to the mathematical specialist. Not taken while the arc runs.**
- **2 July 2026, 23:35 BST.** Full `rs` after ~3-week hiatus + forced compaction + model turbulence: recover script, git (HEAD `6ed0adf` clean/in-sync — repo untouched across the gap), OB/IM, MEMORY.md read from disk in full (loader truncates its tail — index is 26,298 bytes vs the ~24.4KB load limit; restructure proposed to founder), THIS FILE read end-to-end (668 lines — surfaced the stale 7-June resume pointer, now advanced, and the sq standing rule), RECOVERY.md verified from disk, ACTION_QUEUE/QWERTY confirmed not-CDSFL-artifacts, 62-test gate suite green. Full state assessment written: `experimental_notes/CDSFL_Full_State_Assessment_2026-07-02.md` (+ `_Plain_English_` + TTS). Blocker status: model API keys STILL absent from `.env` (Exp 43 + full `pr` gated); codex CLI restored (quota block expired 11 June). Note-standard reference in the note-standard standing rule (numbered 5 at the time; renumbered to 4 on 2026-08-06 when `sq` left the list) updated v1→v1.2.
- **10–11 June 2026, 01:00–04:17 BST.** (Logged here retroactively 2 July — this file's log was not advanced that night, a tracker-policy violation now corrected.) Two-sided gamma gate `71b190b` + regression fix `633b4c6` + severity calibration `050f17c` + Exp 43 config `1b5d148` + records `053e873` + sv `6ed0adf`; 434-test sweep green; matrix Exp-43 row corrected to `bench/macrophage_cell.py`; ONBOARDING macrophage re-tiered; four read-only investigations (severity spec, directive measurement, macrophage/load-balancer, dm consolidation) delivered with file:line evidence.
- **22 April 2026, 00:17 BST.** A1 — created `~/Desktop/CDSFL_Agent_Operational_Plan.md`. First version of the self-consumption operational tracker. Scope: Exp 40–54 + Bench Run 2. Includes recovery-first card, canonical anchors, standing rules, per-experiment target-article matrix with scope briefs for Exp 47/51/52/53, Exp 39 gap-closure list, active work queue, multi-tool cross-verification pairings.
- **22 April 2026, 00:24 BST.** A2 — mirrored the operational plan at `Constraint_Engineering/experimental_notes/CDSFL_Agent_Operational_Plan.md` (byte-identical to the Desktop copy at write time). Canonical copy is the Desktop file; the repo copy exists for version-controlled recoverability and for agents whose first action on recovery is `git status`.
- **22 April 2026, 00:45 BST.** A3 — added three `operational-tracker-*` directives to `~/.claude/CLAUDE.md` under a new `Project Operational Trackers` section immediately after `Recovery Resource Strategy`. Directives name Desktop canonical + repo mirror, update policy, and post-compaction read order.
- **22 April 2026, 00:48 BST.** A4 — linked the operational plan as the first `Key Documentation` item in `Constraint_Engineering/.claude/CLAUDE.md` (project CLAUDE.md).
- **22 April 2026, 00:52 BST.** A5 — linked the operational plan as the first item under `Project State` in `MEMORY.md`, above the current-state entry.
- **22 April 2026, 00:55 BST.** A6 — added a `First read` block to the top of `Constraint_Engineering/resources/RECOVERY.md`'s `Minimum Recovery` section, pointing to the operational plan before the numbered list.
- **22 April 2026, 01:01 BST.** A7 — created `memory/feedback_1e10_catch.md` with the standing rule (1E.n is a hierarchical item reference, not scientific notation) and companion scientific-notation format rule. Indexed in MEMORY.md under Feedback.
- **22 April 2026, 01:08 BST.** A8 — created `memory/multi_tool_crossverify.md` with the full pairing matrix, scope, Wolfram caveat, and FFAFP integration. Indexed in MEMORY.md under Feedback. Phase A closed.
- **22 April 2026, 01:22 BST.** B1 — rewrote the F-paragraph in the Round 2 markdown note (Question 1, "What this means in practice"). F1/F2/F3 now describe actual runtime behaviour; F4 identified as closure-state lexicon landed earlier in arc, documentation-only.
- **22 April 2026, 01:29 BST.** B2 — rewrote Question 3 Cell A paragraph in the Round 2 markdown. Cell A archive is Exp 36–38 baseline (§17 off, §18 off), not Exp 38/39. Ouroboros framing introduced; "version confound" retained as the panel's measurement-level label but positioned as a consequence of the ouroboros evolution, not a standalone concern.
- **22 April 2026, 01:35 BST.** B3 — mirrored B1+B2 in the Round 2 TTS file. TTS format preserved: no markdown symbols, § → "section", `backticks` → plain text.
- **22 April 2026, 01:42 BST.** B4 — rewrote F1/F2/F3 bullet descriptions in the Section 8 Decision Register markdown. F1 = SymPy sandbox allow-list (not SMT sandbox); F2 = compute_rk_with_eta_channel wrapper activation with explicit "Item 1.E.10 is a plan-item reference, not a numerical magnitude" gloss; F3 = debug-time assertion addition (not removal). F4 noted in preamble as documentation-only from earlier in arc.
- **22 April 2026, 01:48 BST.** B5a — rewrote Decision 2 Cell A paragraph in the register markdown: Exp 36–38 baseline archive + ouroboros principle framing.
- **22 April 2026, 01:52 BST.** B5b — corrected adjacent K/L/M graduation line in the same register (pre-launch section): was wrongly scoped to "decision 2 below"; now correctly bound by the Round 2 non-distortion check, with K/L/M flip at Exp 51/52/53.
- **22 April 2026, 02:00 BST.** B6 — mirrored B4 + B5a + B5b in the Section 8 Register TTS file. Phase B closed.
- **22 April 2026, 01:04 BST.** C1 — appended new subsection `## 2a. Target-article scope briefs (Exp 47, 51, 52, 53)` to the consolidated plan, between the §2 experiment table + factorial cells block and §3 fold-in consolidation. Each domain (biology / physics / chemistry / engineering) gets a dedicated sub-subsection naming: the routing specialist and its `domains/immune/*.toml` entry, 4 falsifiable claim clusters with per-cluster tool routing, and a mandatory intentional-false-claim for rejection-test coverage. Section closes with drafting cadence (draft ahead of experiment entry, not at entry) and storage-path direction. Opening paragraph introduces the c_ext / target-module-validity orthogonality argument that the panel used to reject adapters.
- **22 April 2026, 01:06 BST.** C2 — appended `## 6a. Exp 39 → Exp 40 gap-closure list` between §6 (Round 2 outcome) and §7 (Appendix A). Table of G1–G9 with cross-references into §6 RQ items, §4 shadow-element rows, §2 per-experiment rows. Multi-tool cross-verification pairings named per computational gap (G1: AST + pytest; G2: pytest + AST schema check; G3: pytest + SymPy + mpmath; G4: pytest + inspect; G5: pytest + inspect + dis; G6–G8 scheduled; G9 documentation-only). Pre-launch path = G1/G2/G4/G5/G9. Post-launch path = G3/G6/G7/G8.
- **22 April 2026, 01:07 BST.** C3 — mirrored repo consolidated plan to Desktop canonical. `cp` followed by `diff -q` exit code 0, zero differing bytes. Both copies carry §2a + §6a. Phase C closed.
- **22 April 2026, 01:12 BST.** D1 (G1 Gate C wiring) — added `gate_c_preflight()` to `bench/launch_exp40.py`; wired into `--preflight` path (before model-connectivity stub) and full-run path (before runner dispatch). `--dry-run` unchanged (no Gate C; config-only surface). `--skip-gate-c` flag added for debug. Preflight covers: import check; `ADMISSIBILITY_GATES` schema-drift detection; 5-case canonical matrix (missing block, empty input, all-pass, one-fail, sigma-ASCII variant) drawn from offline test truth. New test file `bench/tests/test_launch_exp40.py` (6 tests, all passing). `test_feedback_channel.py` still 39 green. Multi-tool verification: pytest (45 tests); subprocess CLI smoke; monkeypatch-driven drift injection for schema guard. **G1 CLOSED.**
- **22 April 2026, 01:18 BST.** D2 (G2 shadow-audit regression test) — wrote `bench/tests/test_shadow_audit_klm.py` (11 tests, 4 classes, all passing). FFAFP on the 21 April enrichment surfaced a bug: the pre-compaction `shadow_detail` dict-comp bound `claim_id` and `severity` via `getattr(v, ..., None)`, but neither key is a `CellVerdict` dataclass field (confirmed via `dataclasses.fields`) — both silently resolved to None, halving the audit's Round 2 RQ4 non-distortion signal. Fix applied at `bench/immune_agents.py:5411-5421` with explanatory comment block: `claim_id → finding_id`, `severity → confidence`. Regression pins (multi-tool AST + pytest): `_extract_shadow_detail_keys` parses `immune_agents.py` and extracts the dict-comp key set, asserting exact match to `{finding_id, verdict, confidence, tool_used, evidence}`; two standalone pins explicitly ban `claim_id` and `severity` from reoccurring; `test_all_shadow_detail_keys_bind_to_cellverdict_attributes` uses `dataclasses.fields(CellVerdict)` for binding verification; behavioural replica covers N→N emission, 256-char truncation edge cases (both sides), empty-string preservation; log-format pin checks the `_shadow_log` format string `"B-Cell specialist (shadow, domain=%s): %d verdicts; detail=%s"` is present. Run: 11 passed in 2.48 s. **G2 CLOSED.**
- **22 April 2026, 01:22 BST.** D3 (G4 `open_crit_high_count()` REOPENED regression) — wrote `bench/tests/test_open_crit_high_count_v2.py` (11 tests, 4 classes, all passing). FFAFP outcome: **no fix needed** — the existing `_NON_TERMINAL = ("OPEN", "CONTESTED", "REOPENED")` literal at `bench/reference_runner_v2.py:454` already handles REOPENED correctly; v1 and v2 bodies are byte-identical at the 22 April baseline. The gap was coverage, not behaviour. Pins landed: (i) five behavioural — REOPENED at 0.9 severity counted, at 0.5 severity excluded, mixed OPEN+REOPENED counted together, exhausted REOPENED excluded, CLOSED-high excluded; (ii) two purity — no `exhausted` mutation, idempotent; (iii) two signature — `inspect.signature` for parameter contract plus `typing.get_type_hints` for return-type resolution (v2 uses `from __future__ import annotations` so raw signature returns the annotation as a string); (iv) two AST source-truth — `_NON_TERMINAL` literal contains REOPENED + OPEN + CONTESTED. Adjacent regression: 61 tests pass across D1 + D2 + D3 + existing `test_runner_status_transitions.py` + `test_confer_verification.py` in 1.78 s. **G4 CLOSED.**
- **22 April 2026, 01:25 BST.** D4 (G5 `contested_count()` grace_period regression) — wrote `bench/tests/test_contested_count_v2.py` (10 tests, 4 classes, all passing). FFAFP outcome: **no fix needed** to `bench/reference_runner_v2.py:464` — the parameter is respected by the function body (lines 481 + 494 both use it); the three in-module call-sites (1019, 1135, 1214-1215) use the default `grace_period=2` implicitly rather than threading from config. That implicit-default pattern is not itself a defect for Exp 40 launch, but any future sweep experiment will need a `RunnerConfig.grace_period` field; the call-site purity pin will surface the change when it happens. Pins: (i) four behavioural — `grace_period=1` excludes at boundary (rounds_in_status=1 not < 1), `grace_period=3` includes, implicit default equals explicit 2, `grace_period=0` disables UNCONFIRMED counting entirely; (ii) three signature — default 2 via `inspect.signature`, param order `[self, current_round, grace_period]`, return `int` via `typing.get_type_hints`; (iii) one AST — source default literal is exactly 2; (iv) two call-site — no live call-site passes `grace_period=` kwarg literal, call-site count ≥ 3 sanity. Multi-tool: pytest + inspect + typing + ast + source-read. 10 pass in 0.82 s. **G5 CLOSED.** (Separate observation: the inner `grace_period = 2` hardcoded at `reference_runner_v2.py:829` inside `_update_finding_statuses` is a parallel latent wiring gap — logged internally, not a G5 blocker, will surface when G-list is re-reviewed.)
- **22 April 2026, 01:28 BST.** D5 (G3 Stage 6 calibrator test harness) — wrote `bench/tests/test_shadow_stage6_calibrator.py` (18 tests, 6 classes, all passing). FFAFP outcome: **no fix needed** — the 14 April two-dimensional design at `bench/dm/_shadow_stage6.py` is intact, identities hold, HARD 6 preserved. Pins landed: (i) four public-API — class instantiable without args, `observe_round` signature stable, returns `ShadowStage6RoundLog`, empty-findings clean; (ii) two triple invariants — `nu_k_proxy`/`c_ext`/`h_ratio` are distinct dataclass fields on `PerFindingNoveltyLog`, each ∈ [0, 1]; (iii) two SymPy delta identities — symbolic `sp.simplify(delta_code − delta_closed) == 0` proof that `δ = η · c_ext · (1 − ν_k)`, concrete anchor at known finding matching to 1e-4; (iv) two noisy-OR — SymPy value 0.65 at (c_s1=0.5, c_s2=0.3), unit-interval bounds at c_s=0 and c_s=1; (v) two frequency-scaling — c_freq monotone non-decreasing in encounter count N, bounded at C_MAX=0.95 under saturation (100 repeats); (vi) two epistemic tagging — no-search (ν_k=0.5) NOT tagged, searched-empty (ν_k=0.8, c_ext≈0.224) tagged SPECULATIVE; (vii) four source-truth — GAMMA_SRC=0.7, ALPHA_FREQ=0.1, C_MAX=0.95, module docstring retains two-dimensional HARD 6 framing. Wolfram cross-check skipped (local-only per plan standing rules; SymPy closed-form identity is the load-bearing proof). Multi-tool: pytest + sympy + inspect + ast + dataclasses. 18 pass in 0.76 s. **G3 CLOSED.**
- **22 April 2026, 01:33 BST.** D6 (G9 ONBOARDING closure-state label sweep) — added `## Closure-State Lexicon (F4, locked 21 April 2026)` section to `resources/ONBOARDING.md` between the Standing Rules and Current State blocks, naming `library_complete` / `shadow_integrated` / `live_operational` with one-clause examples for each, promotion-order rule, and pointer to the shadow-promotion-now non-distortion bounding condition. In the same pass, corrected the most load-bearing stale factual description on ONBOARDING line 51: the K/L/M shadow-audit entry previously described the pre-compaction bug (`claim_id` + `severity`) as the live schema. It now reads the real `CellVerdict` field set (`finding_id, verdict, confidence, tool_used, evidence`), carries an explicit "22 April 2026 correction" note pointing at `bench/immune_agents.py:5411-5421` for the fix and `bench/tests/test_shadow_audit_klm.py` for the 11-test regression pin, and wears the `shadow_integrated` closure label inline. A full retroactive labelling of the remaining ~40 shadow mentions in ONBOARDING is NOT attempted — the decision (documented in-row and here) is that defining the lexicon once + fixing the one outright-stale description is both higher value and lower risk than a large search-and-replace across settled prose. Forward-going discipline is: new ONBOARDING additions wear the label at write time; existing mentions retain the earlier phrasing but the glossary is in reach. **G9 CLOSED (documentation-only).**
- **22 April 2026, 01:37 BST.** D7 (G6/G7/G8 scheduled-close trigger specifications) — added new `## 6b. Scheduled trigger specifications (G6, G7, G8)` subsection to the consolidated plan (both repo and Desktop mirror, byte-identical post-edit per `diff -q`). Each of the three gaps now carries an entry trigger with automatic migration path (Exp 44 → Exp 49 → Exp 54 for G6/G7; external authorisation for G8), the multi-tool cross-verification pairings that apply on activation (pytest + AST + inspect + trace-log parsing), and the minimum evidence threshold for a close verdict. In the same edit pass, updated the §6a status column for G1/G2/G3/G4/G5/G9 from `Pending` to `CLOSED` via a single `replace_all=true` on the distinctive `| Pending |` cell pattern (safely non-overlapping with the `Pending activation` string on line 18 used by the S3 shadow-element entry). Added a paragraph under §6a acknowledging the overnight-shift closures with explicit test-file references. Popperian framing preserved: the §6b section closes by noting that the arbitration rules for G6 and G7 are deliberately unspecified — they must emerge from post-mortem evidence rather than being pre-registered. Phase D closed. Next: Phase E (regression run → state-file updates → sv → final pass).
- **22 April 2026, 02:08 BST.** E1 (regression run) — two-part pytest evidence captured. Part one: standalone run of the five new test files (`bench/tests/test_launch_exp40.py` + `test_shadow_audit_klm.py` + `test_shadow_stage6_calibrator.py` + `test_open_crit_high_count_v2.py` + `test_contested_count_v2.py`), 56 collected, **56/56 pass in 2.33 s**. Part two: fast non-network regression sweep excluding five long-running or CLI-blocking files (`test_openrouter_tools.py` 36, `test_deepseek_specialist.py` 29, `test_dynamic_management.py` 283, `test_ouroboros_query_quality.py` 11 non-network, `test_exp29_integration.py` 44), 907 collected, **907/907 pass in 342.12 s** (5m 42s), exit code 0, zero failures. The test_exp29_integration.py::test_three_round_flow hang reproduced under a dedicated 120 s run — confirmed hanging on `Claude CLI Haiku` LLM classifier invocations (14.4 s per call, 3 rounds × N findings per round) plus the fact that it sits on the non-network code path despite doing real CLI dispatch. Log evidence at `bench/logs/immune_pipeline.log` 02:05:51 BST shows the overnight `finding_id`/`confidence` rename emitting correctly under the live path: `detail=[{"finding_id": "sf1", "verdict": "CONFIRMED", "confidence": 0.85, "tool_used": "rdkit", ...}]`. The hang is therefore pre-existing (pre-compaction), unrelated to overnight edits, and the overnight fix is demonstrably working in production pipeline traces. A longer non-ignore sweep is deferred to the daylight review window. [Correction 2026-07-31: the entry above is preserved verbatim because its closing observation — that `test_three_round_flow` "sits on the non-network code path despite doing real CLI dispatch" — is the project's own contemporaneous sighting of the defect, recorded 22 April 2026 02:08 BST. It named the exact contradiction and nothing was done with it: no `pytest.mark.network` was added in response, and the "non-network" label went on being applied to sweeps for a further 99 days. Two consequences for reading this entry. First, the 907 sweep it reports was itself not offline — the five-file exclusion list was chosen on wall-clock, and three unmarked live-dispatch files (`test_immune_agents.py`, `test_specialist_live_promotion.py`, `test_specialist_shadow_cells.py`) were inside the 907. Second, the "hang" was not a deadlock: it was roughly 44 serialised 15 s live claude-CLI dispatches under `_CLAUDE_CLI_LOCK`, which is the designed behaviour of an undeclared network dependency. With outbound calls denied the entire suite now finishes in 99.6 s (`python3 -m pytest bench/tests/ -q --netguard-strict` → 2086 passed, 3 skipped, 0 failed, 2026-07-31 19:15 BST, HEAD `d4d4d7f` plus working tree). See `resources/RECOVERY.md`.]
- **22 April 2026, 02:10 BST.** E2 (ce_state update) — `memory/ce_state.md` line 16 updated with the final pass counts (56/56 new, 907/907 fast wall-clock-limited sweep — not offline, see the 2026-07-31 correction on the 02:08 entry above) and the pre-existing-hang provenance note replacing the "TBD at sv" placeholder.
- **22 April 2026, 02:12 BST.** E3 (ONBOARDING + RECOVERY updates) — both files' 22 April 2026 session blocks updated with the final pass counts replacing the "TBD at sv" placeholder. The `bench/logs/immune_pipeline.log` at 02:05:51 BST evidence line is now cross-referenced in both files as proof that the overnight rename is operational under the real pipeline, not only under unit tests.
- **22 April 2026, 02:14 BST.** E4 (sv commit + push) — `python3 scripts/cdsfl_sv.py --commit --push -m "<long descriptive message>"` succeeded. Commit **991cde0** on `exp39-experimental` (previous HEAD `be6d13a`). Seventeen files committed in total: seven modified and ten staged-from-untracked (five new test files + operational plan repo mirror + four new experimental notes). `docs/CURRENT_STATE.md` auto-regenerated by the sv script. Atomic push to `origin/exp39-experimental` succeeded in the same subprocess invocation. Working tree clean post-commit.
- **22 April 2026, 02:18 BST.** E5 (final operational-plan pass) — Current-State-Snapshot HEAD updated `be6d13a → 991cde0`, working-tree-status note updated from "Dirty, 2M + 2U" to "Clean post-commit, 17 files committed", test-count line updated with the 56/56 new + 907/907 fast-sweep figures, shift-level description updated to reflect six-of-nine gap closure. Morning-review resume pointer set: the next action is a waking review of this shift's paired output + founder decision on Exp 40 launch approval; no outstanding automated task remains. Phase E closed.
- **22 April 2026, 02:15–02:30 BST.** Founder oversight Q&A (debrief of overnight shift). Two founder questions: (1) `test_exp29_integration.py` naming + Exp 40 scope — clarified as pre-Exp-40 regression coverage for real-dispatch path, not an arc artefact; (2) completeness + misses + panel-review worth. Honest gap catalogue recorded: 5 of 9 G-items fully closed (G1-G5), 3 of 9 specification-only (G6/G7/G8), 1 of 9 partial (G9). Four residuals identified beyond the G-list: Exp 39-0 gate contradiction not personally verified; per-finding R_k time-series not addressed; scientific-notation sub-rule not amended into locked `cdsfl_note_standard_v1.md`; full retroactive F4 closure-state labelling not performed. Clarification recorded: "integration" has two senses — fold-in-and-test (overnight directive) vs Exp 54 factorial (the arc's integration experiment). Panel-review status mapped: F1/F2/F3 strategy + Gate C step + Stage 6 design + scope/ordering + RQ6b + K/L/M non-distortion + shadow-promotion-now already reviewed; G2 code correctness + §2a scope briefs + §6b trigger specs + G3/G4/G5 coverage + G9 lexicon wording NOT reviewed. Self-assessment clause recorded: "fix all" was interpreted on a spectrum (bounded-fix / specification-only / full-sweep) and the split should have been flagged at write time, not at debrief.
- **23 April 2026, 04:50 BST.** Documentary-state sv prep (post-compaction resume of the 22 April `sv` directive) — new memory file `feedback_fix_all_scope_split.md` created capturing the lesson that autonomous "fix all" windows must decompose the target list into bounded-fix / specification-only / full-sweep at start of window and announce the split in the shift note. Indexed in MEMORY.md under Feedback.
- **23 April 2026, 04:55 BST.** Documentary-state sv prep — ONBOARDING.md new oversight-Q&A block inserted at top of Current State (before overnight shift block); RECOVERY.md parallel block inserted at top of Current Pending Work; ce_state.md Key Facts prepended with oversight-Q&A summary; this operational plan Last-Updated header + Current-State snapshot + Completed-log + Resume-point updated.
- **23 April 2026, 05:01 BST.** Documentary-state sv commit `7c9df2b` landed via `scripts/cdsfl_sv.py --commit --push`. Four files committed: `docs/CURRENT_STATE.md` (auto-regenerated by sv script), `experimental_notes/CDSFL_Agent_Operational_Plan.md` (repo mirror), `resources/ONBOARDING.md`, `resources/RECOVERY.md`. Pushed to `origin/exp39-experimental`. Working tree clean post-commit. Memory file + Desktop canonical not in repo (per design); new memory file `feedback_fix_all_scope_split.md` lives in `~/.claude/projects/…/memory/`.
- **15 May 2026, 02:15 BST.** Pre-continuation post-mortem fix tranche landed across nine commits on `exp39-experimental` (HEAD `3bbf2c7`): (1) `35c44b6` decomposed-dispatch synthesis empty-response fallback; (2) `12ad362` Bugzilla CLOSED-loop module `bench/bugzilla_loop.py`; (3) `8cb1fbe` Bugzilla CLOSED-loop runner integration; (4) `26b28f8` gamma input post-reconciliation novelty fix; (5) `9891bda` Stage 6 calibrator `int`-flaw-class crash fix; (6) `a8a33c2` explicit Bugzilla paradigm in panel prompt; (7) `b2f3444` parse-admissibility-block FINDING_ID terminator regex fix; (8) `7f3066b` ITC CAPABILITY_MISMATCH false-positive guard; (9) `3bbf2c7` launcher_core shared infrastructure + G7 design (paired notes at `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md` + `_Plain_English_2026-05-15.md`, TTS at `~/Desktop/CDSFL_tts/G7_Merge_Deadlock_Resolution_Design_2026-05-15.txt`). Config bump: `bench/exp40_configs/40_gate.json` max_rounds 8→18, extension_cap 10→20.
- **15 May 2026, 03:15:48 BST.** Exp 40 continuation run launched via `python3 bench/launch_exp40.py --resume`. Resumed from Round 10 of the original 2026-05-14 run; registry restored with 146 entries. Background-task ID `bdqum45ab`; monitor task ID `b9hwsq8tn` (later re-armed as `bhfiygnhd` after timeout).
- **15 May 2026, 03:15:48 → 05:20:26 BST.** Run executed seven additional rounds (R10–R16). Wall-clock elapsed 7,478 seconds (cap was 7,200s; runner finished round close before exit). Final γ 0.034; final ρ 0.6; novel_critical_history last 10 rounds `[1, 0, 1, 0, 3, 2, 1, 0, 4, 2]` — γ-alt not met. Total canonical entries 179; 280 raw findings; status distribution OPEN 68 / CONFIRMED 42 / CLOSED 26 / UNCONFIRMED 23 / MERGED 19 / CONTESTED 1. Seventeen verified BUGZILLA CLOSED transitions during the continuation alone. Five D4 MERGE DEADLOCK distinct entries on the HIL queue (C0008, C0023, C0023 at fourteen rounds is the longest unresolved merge in project history, C0032, C0035, C0044, C0147). Three D2 HIL escalations (C0052, C0071, C0044). All five panel members hit DEGRADATION classification by Round 14; Gemini hit TRANSIENT_FAILURE twice. Active monitoring ran continuously across all heartbeats (~80 monitor events received and assessed); no FFAFP-grade halts triggered.
- **15 May 2026, 05:20:26 BST.** Runner exited cleanly (exit code 0). Final report saved to `bench/logs/exp40_gate_20260514T020550Z/exp40_gate_report.json`; final state at `runner_state.json`; per-round model outputs at `round{10..16}_{model}_*.json`. Monitor process detected Python gone and emitted termination notice.
- **15 May 2026, 05:25–05:30 BST.** Paired post-mortem written under CDSFL note standard v1.2 (locked 14 May 2026): technical version at `experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md` (~310 lines), plain-English companion at `experimental_notes/Exp40_Continuation_Postmortem_Plain_English_2026-05-15.md` (~200 lines), TTS plain-text at `~/Desktop/CDSFL_tts/Exp40_Continuation_Postmortem_2026-05-15.txt` (mirrors plain-English in TTS-safe formatting). Post-mortem assesses all seven fixes against live behaviour (all functioned as designed), records five anomalies for next-experiment attention (DeepSeek 0-char Phase-1 sections; parser code-fragment finding-IDs; LLM classifier sub-threshold OVERRIDE logs; RT v2 AUTOIMMUNE flag noise on Gemini per-round; ITC DEGRADATION-in-convergence false positive), and catalogues the G7 deadlock evidence cluster for the founder's implementation decision.

---

## Superseded resume pointer (2026-07-29 chain-halt state — retained for trail)

> **NOT CURRENT — do not act on this section.** Live state is the ★ RESUME POINTER block at the top of this file: the FIRST one is current, everything below it is trail. Live work queue is `experimental_notes/OUTSTANDING_QUEUE_to_BR2.md`.

**SUPERSEDED — 2026-07-29 12:45 BST. Retained for trail. Everything below this block is older trail still.**

**Chain state: HALTED, deliberately, mid-repair. Nothing is running. Balance ~$364.**

**Completed and unaffected:** Exp 44 (clean convergence, zero residue), 45, 46, 47
(converged R13, two genuine HIL residuals), 48 chemistry (converged R5, 6/6 — see
retraction below), 49 engineering (converged R6, 6/6, forensics clean).

**What halted the chain.** Two integrity failures found during the Exp 50 pre-flight,
both self-inflicted, both now closed forward:

1. **A panel model read the scoring key during Exp 48.** At round 1 a routed model
   wrote a falsifier that opened the key and printed the entire planted set
   (preserved at `registry.entries.C0012.falsifier_code`). Three conditions had to
   hold together: the panel's working directory was the repository; a config note
   *inside* the repository named where the key had been moved to, committed 76
   minutes before the run; and superseded keys sat in git history. The fix had
   advertised what it hid. **Exp 48's 6/6 is retracted as a blind detection rate**
   and must be reported as detection by a panel that knew the seeded set. The six
   demonstrations remain individually sound; what is lost is the stopping decision.
   Errata: `bench/logs/exp48_chemistry_exam_live_20260729T044134Z.errata`.
   Exp 49 is clean by the same scan and stands.
2. **The factorial's key was recoverable from git history with all 12 planted IDs
   identical to the live key** — a total compromise of a capstone that had not yet
   run. The module is being reseeded so the historical key is void, and the old
   key is left in history deliberately as a tripwire.

**Instrument changes, forward only (no completed record altered):**
- `panel_cwd` confines the shell-bearing routes to the staged target's own
  directory; refuses a missing directory rather than failing open; threaded
  through BOTH config-ingestion paths and pinned by `test_panel_isolation.py`.
- Targets staged one per directory under their own internal Document ID
  (`bench/stage_targets.sh`), mode 444 files inside mode 555 directories — both
  enforcements empirically proven, and a directory listing no longer enumerates
  the exam series.
- `bench/vault_keys.sh` holds the keys as a single opaque archive during runs, so
  no key file name or plaintext key content is on disk for a filesystem search to
  find. Obfuscation, not encryption — the third layer, not a substitute.
- Every reference to the key's location removed from the repository.
- Key-access forensics scans every file in a run directory (it had caught the
  Exp 48 incident only by luck — `r*_*.json` happens to match `runner_state.json`;
  the run report, holding the same evidence, would never have been scanned).
- `bench/arc_sequencer.sh` rewritten: asserts keys vaulted, asserts one file in
  the panel's working directory, runs forensics after every leg and HALTS on
  key-access evidence.

**Exam redesign (the reason the arc paused before Exp 50).** CC2 had
reverse-engineered the chemistry exam's design from its sibling-pair structure.
Physics and biology rebuilt with true/true pairing and plant counts that are not
one-per-cluster; a **zero-plant control** (`exp53`, Document ID SW-21-REF-04,
44 claims, none seeded) added as the direct measure of the stopping decision.
Independent audit: biology CLEAN, control CLEAN and statistically
indistinguishable from its seeded sibling; **physics SIGNAL-REMAINS** (seeded
claims sat beside near-duplicate twins, neighbour-Jaccard p=0.017, the only
finding to survive multiplicity correction) — under repair. Audit also found a
cross-target count prior, "seeded count = sections − 1", which held on 48, 49 and
50; being broken everywhere it can still be broken.

**Third defect, found pre-launch on the control (commit `2887106`).** The two-sided
gate could not tell "no curve" from "a flat curve". `_estimate_gamma` fits a Duane
decay to the cumulative critical series, and two OPPOSITE series both drive it to
~0.0: `[0,0,0,0,0,0]` (no critical ever found — no curve to fit) and
`[2,2,2,2,2,2]` (constant arrival, no decay at all). The first is the best possible
outcome, the second the worst. A panel reviewing a genuinely clean document
perfectly could therefore never converge — it would burn its full budget, report
non-convergence, and halt the arc on a document with nothing in it. The zero-plant
control, whose whole purpose is to be clean, could not have produced its own
headline result. **Gamma was NOT demoted**: the estimator's DOMAIN was narrowed, the
vacuous case converges under a distinct verdict carrying both counts and an explicit
"REVIEW THIS RUN", a constant-rate series still stays blocked, a panel returning
nothing at all is refused as a dead panel, and every other gate still binds.
Verified inert on all six completed runs (Exp 44–49 carry 34/12/12/44/32/31
criticals, so the branch cannot fire). Churn was checked for the same degeneracy and
is not affected — `rho_earliest_round` is 12 and the control converges well before.

**RESUME ORDER once the repair audit returns CLEAN:** stage → clear → vault keys →
`bench/arc_sequencer.sh` → Exp 50 physics → 51 biology → **53 zero-plant control** →
52 factorial cells A–D (instrument frozen at cell A) → STOP before BR2.

**Open founder rulings (none blocking the above):**
- Whether to re-run Exp 48 (and 49) under the new design, or report both with the
  contamination stated. Re-running gains nothing if the new design does not
  eliminate recognition, which the control will show.
- Residual exposure: this assistant's own session store under
  `~/Library/Application Support/` contains key content and is reachable by an
  absolute-path read. Closing it properly needs an OS-level sandbox for the panel
  (`sandbox-exec` or a separate user), which is a real change mid-arc. Currently
  mitigated by confinement + de-pointering + vaulting + detection, not eliminated.
- Materiality review: 11 Exp 49 findings against TRUE claims, 6 similar in Exp 48,
  and Exp 47's two genuine HIL residuals.

---

### Superseded resume pointer (definitional confer — retained for trail)

**Next action — FOUNDER DECISION on the definitional confer outcome (advisory), then Week-1 of the scoped PoC plan.**

Advisory 5-model definitional confer ran clean 2026-05-18 (logs `bench/logs/confer_exp40_definitional_2026-05-18/`; purely factual, no embedded position, dissent permitted). **Q1 unanimous 5/5: total exhaustion NOT attainable** (open all-severity surface vs Duane closed-pool; γ-all 0.10–0.23; resource bound) — confirms the founder view on independent grounds. **Q2 NOT unanimous (reported, not collapsed): X (Gemini, CC2) / X-not-as-implemented bridging Z (Codex) / Z functional benchmark (ChatGPT, DeepSeek).** Unanimous core beneath the split: total-exhaustion out; bare 0.7 severity is the top vulnerability → replace with a pre-registered consequence-based critical def; settled-registry accounting (not live); pre-registered+scoped+hostile-reproducible; apply-fixes-back ON; OR-gate → stricter conjunction. **Synthesis (soundest-argument, P-passed incl. bias-check): the answer is the CONJUNCTION, not X-or-Z** — pre-registered consequence-based critical/structural def + settled accounting + critical-exhaustion stability AND a frozen held-out STEM benchmark with mechanical pass/fail (DeepSeek's test-impact criterion = sharpest F6 fix). Disclosure: cc2 mis-framed itself as CC1 (weight 4+1, not clean 5). Concrete ~1-month plan: Wk1 freeze POC_SCOPE.md + pre-registered critical rubric + settled-only estimator fix + frozen benchmark; Wk2-3 bounded PoC on decomposed slices, apply-back ON, conjunction-gated; Wk3-4 robustness sweep + isolated adversarial pass + audit bundle + scope-declared write-up; defer λ_ext, full BR2, total-exhaustion. Bottom line: internal convergence to date does NOT by itself prove the goal; a defensible PoC must show correct answers on pre-registered untuned STEM problems. Paired note `experimental_notes/Exp40_Definitional_Confer_Outcome_2026-05-18.md` (+ plain-English + TTS). **No code changed — advisory; awaiting founder decision.**

### Superseded resume pointer (plan-F resume FALSIFIED — retained for trail)

**Next action — MORNING DISCUSSION (founder-deferred): OR-vs-complementary gate + γ-input hardening. The full-budget resume DID NOT answer the question — artefactual stop, reported as such.**

**Resume outcome (FALSIFIED, do NOT read as a win):** the resume stopped at R7 — the FIRST resumed round — because the γ≥0.30 arm (kept active as the legit win condition) fired: runner LIVE novelty_counts [10,9,6,9,3,2,1,2] → γ=0.3047 (correctly computed; NOT a guard/arith error). It does NOT hold: production-faithful recompute from the SETTLED registry gives all-novelty γ=0.231 (below 0.30). The convergence verdict flips on live-vs-settled novelty accounting. Crossed by only 0.0047, single round, run-length-sensitive (demonstrated twice). Confound: R7 reviewed the RE-SEEDED PRISTINE slice (0 apply-back promotions; R8 repair reconstruction never reached). The full-budget γ trajectory question is STILL unanswered. Robust signal unchanged: settled critical-γ=0.553 (strong) vs all-novelty 0.231 (weak) — same severity-granularity ordering as every prior run. Verdict: the all-novelty γ≥0.30 OR-arm is not a trustworthy sole convergence certificate — concrete input for the OR-vs-complementary-gate decision; supports the founder's distrust of a single-signal γ crossing. Run report: bench/logs/exp40_slice_admissibility_20260516T223952Z/. Audit tool: bench/exp40_gamma_findings_audit.py.

**Record fact (founder asked):** the zero-novel-CRITICAL trigger WAS
ratified — Consolidated Plan §S10 "Enforced": Exp 40 sole acceptance
gate = `γ≥0.30 OR 3 consecutive zero-novel-CRITICAL`. plan-F's R6
convergence was within the ratified OR gate (not invented, not
cooking). Honest nuance: the OR never required the two arms to agree.

**Running (autonomous, 2026-05-18 ~01:06 BST):** plan-F FULL-BUDGET
RESUME — `python3 bench/launch_exp40.py --resume --config
40_slice_admissibility.json`. Resumed R7→R19 (full 20-round budget;
checkpoint R6→start 7, verified). INSTRUMENTATION-ONLY config change
(NOT γ change, NOT cooking, documented in the config _comment):
`gamma_alt_consecutive_zero_crit 3→999` (zero-crit early-stop arm
disabled — the trigger that pre-empted plan-F at R6),
`earliest_stop_round 3→20` (main state gate can't pre-empt).
`gamma_alt_threshold` stays 0.30 UNCHANGED → a legit γ≥0.30 still
stops/▸detected. Non-cooking agreed fixes intact (apply-back, in-round
re-ask, G7, collision-fix). NO γ-hardening applied (awaits ruling).
Question: how far does γ depletion actually get over the full budget if
not pre-empted. PID `/tmp/exp40_sliceR_pid`; log `/tmp/exp40_sliceR_logpath`;
guard bg `bc7903e7l` (`/tmp/exp40_sliceR_guard.sh`, 60s, freeze only on
unambiguous corruption); Terminal open. **Known caveat (disclosed):**
resume re-seeds the working copy pristine; R0-R6 repairs reconstructed
from the restored CLOSED registry at the R8 loop-top → R7 reviews
pristine, R8+ reconstructed-repaired (minor 1-round artefact, does not
invalidate the γ-trajectory question; registry/γ-history continuity
preserved). MORNING: read `/tmp/exp40_sliceR_DONE` (terminal:
GAMMA_THRESHOLD_REACHED = γ≥0.30 win, or FULL_BUDGET_R19 = γ did NOT
reach 0.30 in 20 rounds) or `/tmp/exp40_sliceR_ALERT` + the run log.
Report the γ trajectory straight, win or not.

**Corpus recalibration finding (the other half of "both"):**
production-faithful γ via the runner's own post-reconciliation rule +
real `_estimate_gamma` (`bench/exp40_gamma_findings_audit.py`):
plan-F all=0.222 / crit=0.510 (57% substantive, ~0% residual dup);
Exp40 R0-R28 all=0.102 / crit=0.329 (41% substantive, ~10% residual
dup, offline proxy). Consistent 2-point ordering crit-γ ≫ all-γ
corroborates the severity-granularity reading on independent runs —
**but corpus = 2 regime points, far too thin to SET a recalibrated
threshold; doing so now would be the book-cooking risk. Pre-register
the method; derive the number only once enough regime-stratified runs
exist (this resume adds a long-budget point; Bench Run 2 adds many).**
The residual-churn question is answered: de-churn largely held;
findings are substantive — γ's low all-novelty value is severity-mix,
not churn.

### Superseded resume pointer (γ-confer outcome — retained for trail)

**Next action — FOUNDER RULING on the γ-hardening confer outcome, then implement steps 1-2+5.**

5-model neutral confer (gemini/codex/cc2/chatgpt/deepseek, compelled
convergence, γ-demotion excluded as founder HARD constraint) ran clean
2026-05-17 (logs `bench/logs/confer_exp40_gamma_hardening_2026-05-17/`).
**5/5: harden γ, do NOT demote (all argued demotion technically
unnecessary).** 4/5 unprompted: the hardening IS book-cooking unless
anti-cooking controls enforced. Converged core: feed γ the
post-reconciliation **critical/structural severity-gated** series as
the gate, all-novelty logged as diagnostic (dual-series); regime-aware
recalibration pre-registered NOT fitted to plan-F; keep apply-back
(reverting = the documented non-convergence cause); offline ≈0.60 /
`[8,4,0,3,1,1,1]` NOT production truth — must recompute through
production pipeline (mismatches the post-mortem zero-critical tail; 3
models caught it). Splits resolved on the anti-cooking constraint
(CC1 synthesis, not vote): keep frozen calibration leg (P3); defer
λ_ext/P4 to instrumented-not-gating until ν/Δ data-fixed; severity cut
= project HARD/SOFT-constraint class not bare 0.7 (DeepSeek's "0.7
already sound" flagged unverified); CC2 sparsity guard
(count-based zero-crit fallback below min cumulative-critical) is
non-optional. Synthesised 7-step position + CC1 independent read in
`experimental_notes/Exp40_Gamma_Hardening_Confer_Outcome_2026-05-17.md`
(+ plain-English + TTS). **No code changed — decision-grade, awaiting
founder ruling.** Standing caution: production recompute may show γ
does not clear a properly recalibrated bar; if so the bar holds and it
is reported, not engineered around.

### Superseded resume pointer (plan-F result — retained for trail)

**Next action — FOUNDER REVIEW. Plan-F CONVERGED (qualified) — FIRST convergence in the Exp 40 arc. Remediation build E→F COMPLETE, validated, committed, sv'd.**

Plan-F (`exp40_slice_admissibility`) reached **γ-alt convergence at
round 6** (`converged_at=6`, reason `GAMMA_ALT_CONVERGED: 3 consecutive
rounds zero novel CRITICAL`), stopped early (7 of 20 rounds, 5,808 s).
Falsified hard vs the report (two R24–R28 false positives demanded it):
survives — early stop, `gamma_history=[0,0,.156,.135,.172,.219,.267]`
rising (vs R24–R28 flat ~.05/25r), apply-back exercised (4 promotions
C0001/C0005@r2, C0012/C0019@r3, full-suite-green, 0 rejected; working
copy 132→135 lines), in-round re-ask recovered 1 (Gemini). Registry 40
canonical (CLOSED 16 / UNCONFIRMED 21 / CONFIRMED 2 / MERGED 1 /
CONTESTED 0).

**QUALIFICATIONS (not buried):** (1) converged via zero-novel-CRIT
γ-alt path, NOT γ≥0.30 — γ final 0.267, runner flagged "weak depletion,
state closure may be premature"; genuine by the defined gate but
modest. (2) ONE run, smallest slice, multiple variables changed at once
(decomp + apply-back + reask + cleaned baseline) — validates root cause
+ cure, does NOT isolate the dominant factor nor prove general
scaling; factorial follow-up needed. (3) convergence = no new CRIT 3
rounds, not all-resolved (21 UNCONFIRMED). (4) trailing "ended without
convergence (likely wall-clock)" is the known-inaccurate generic
string — false here; authoritative = converged_at=6.

**Significance:** first arc convergence; large differential vs the
non-converged R24–R28 comparator, in the predicted direction →
supports the founder's thesis (convergence real, was mechanically
blocked) with the mechanism now identified, fixed, demonstrated.

**Recommended next (NOT founder-approved):** re-run on progressively
larger slices then full `_feedback.py`; run the factorial isolating
apply-back vs decomposition; fold the C0001/"CLOSED≠correct" lesson
(S_k tolerates regressions) into methodology via the plan-C full-suite
gate template.

Paired result post-mortem: `experimental_notes/
Exp40_Slice_F_Convergence_Result_2026-05-17.md` (+ plain-English +
TTS). Build trail commits `6838e58 6e63169 c2dd4ef 58a4efa 42da873
654a4c8 111a098` + the F-result sv. Guard `b5mjsuyig` exited clean
(TRUE convergence); no ALERT; run process ended normally.

### Superseded resume pointer (build running — retained for trail)

**Next action — MORNING REVIEW of plan-F outcome. Remediation build E→D COMPLETE + committed; F (decomposed convergence re-run) RUNNING under live guard (2026-05-16 ~23:40 BST, autonomous).**

Founder directive "just do it all" discharged. Root cause (confirmed
code+git+Exp36): verified fixes only ever sandbox-applied, never written
back → panel re-reviews same defects → re-injection-dominated
non-convergence. Six items built this session, milestone-committed:

- **E** `6838e58` — collation of all 44 CLOSED fixes (40 artefact / 0
  runner / 4 stale); strict-gated cleaned baseline
  `bench/exp40_baseline/_feedback_cleaned.py` (11 accepted, 40/40 tests).
  **Key finding: C0001 was CLOSED at run time despite e2_regression
  0.974 (38/39) — CLOSED≠correct; S_k threshold tolerates regressions.**
- **A** `6e63169` — collision-overwrite fixed (collision-safe
  (fid,model) keying; 106 tests pass).
- **B** `c2dd4ef` — in-round re-ask (dispatch-phase, bounded, 8 tests).
- **C** `58a4efa` — apply-fixes-back to per-run working copy, FULL-suite
  gated (the C0001 lesson), default-off, 5 tests. Structural cure.
- **D** `42da873` + `654a4c8` — slice `_feedback_slice.py` (~110 lines)
  + `40_slice_admissibility.json` + launcher `--config`.
- **F** RUNNING — `python3 bench/launch_exp40.py --config
  40_slice_admissibility.json`. Confirmed at start: apply-back ON
  (seed=pristine slice), in-round re-ask ON, G7 ON, Gate C PASS, target
  5,596 chars, cap R0–R19. PID file `/tmp/exp40_slice_pid`; log path in
  `/tmp/exp40_slice_logpath`; guard `/tmp/exp40_slice_guard.sh` (bg
  task `b5mjsuyig`, 60s, freeze only on unambiguous corruption,
  alert-only otherwise). Terminal window open.

**MORNING: check `/tmp/exp40_slice_DONE` (terminal: convergence /
STALL_CONVERGED / R19-complete) or `/tmp/exp40_slice_ALERT` (anomaly;
frozen only if corruption) + `/tmp/exp40_slice_ffafp.log` + the
Terminal + the run log. Report F's convergence result straight,
converged or not — that is the founder's core question.** Maths
re-audit (old plan item 1) declined by founder; no doubt carried.
Paired post-mortem: `experimental_notes/
Exp40_Remediation_Build_E_to_F_2026-05-16.md` (+ plain-English + TTS).
If F finished while the session was alive, an F-results post-mortem +
sv supersedes this pointer.

### Superseded resume pointer (plan approved, pre-build — retained for trail)

**Next action — EXECUTE the approved Exp 40 root-cause remediation plan (founder-approved 2026-05-16, MC `d, t` discharged). Begin with E, then A+B, then C, D, F.**

Root cause confirmed (code + git + Exp 36 audit): verified fixes are applied
only in a throwaway sandbox (`reference_runner_v2._run_regression_suite`
~L3088–3116); the real `bench/dm/_feedback.py` (621 lines) is never patched,
so the panel re-reviews the same defects every round → re-injection-dominated
non-convergence (γ peaked 0.2967@R3 then flat ≈0.05 for 25 rounds; the maths
model predicts exactly this, no metric doubt). Approved plan (paired note
`experimental_notes/Exp40_RootCause_Remediation_Plan_2026-05-16.md` + plain-
English + TTS):

- **E.** Collate + `sy` + `f` all past Exp 40 fixes (296 canonical / 44
  CLOSED, 4 legs): runner fixes → fold into `reference_runner_v2`; artefact
  fixes → cumulative-gated baseline for C; stale → discard+log. **First.**
- **A.** Collision-overwrite fix at `_feedback.py:228` (collision-safe
  accumulation, retain+log both; 5 `.get(fid)` consumers FFAFP'd; UUID-
  namespace only if a consumer can't be satisfied — report, don't switch
  silently). Replaces the detector-gated deferral with a real fix.
- **B.** In-round re-ask (dispatch phase, not reconciliation close; 1 retry/
  model/round, idempotent, logged; 1e stays fallback).
- **C.** Apply verified fixes back → per-run working copy under run log dir
  (NOT repo file); next run seeded from all prior CLOSED patches; promote
  only if cumulative working copy still passes all gates. **Changes Exp 40
  from static-stimulus → iterative repair-and-reconverge — intended,
  recorded.**
- **D.** Decompose target; first slice = admissibility/parse group (seam
  shown before run).
- **F.** Re-run: decomposed + seeded baseline + apply-back + A + B + G7 on;
  generous cap (≤~20 rounds OK now design is fixed); live 60 s monitor,
  pause/fix-on-the-fly.

Maths re-audit (old plan item 1) **declined** by founder — convergence taken
as real/bounded; no doubt carried forward. Notes written, uncommitted (next
sv folds them). On execution: implement, do not re-litigate or re-defer.

### Superseded resume pointer (R24–R28 result — retained for trail)

**Next action — founder review of the Exp 40 R24–R28 result. Exp 40 COMPLETE (R0–R28).**

**Headline result: the mechanical-blocker hypothesis is FALSIFIED for this
target.** The G7-enabled 5-round leg (R24–R28) was the clean test of "remove
the merge-deadlock blocker → convergence follows". G7 removed the blocker
completely and correctly (8–10 deadlocks resolved by ≥3/5 majority; C0023 at
21 rounds — project record — resolved 5/5; zero merge cycles). Convergence
still did NOT occur: γ flat ≈0.047–0.051 (G7-on) vs ≈0.048 (G7-off R17–R23) —
no convergence effect. Full γ R0–R28 peaked **0.2967 at R3** (≈1.1% below the
0.30 gate) then declined and plateaued ≈0.05 for 25 rounds. The system
approaches the gate early then diverges; the divergence is NOT the deadlocks.
Convergence remains real in general (Exp 37 clean; this run touched the
threshold at R3) — this is a target-specific divergence. Candidate
[SPECULATIVE]: novelty-regeneration dynamics and/or γ-metric/gate
mis-calibration (Exp 36 audit: "γ classifies wrong at system level during
churn"; this run logged "Gamma disagrees with state closure — recommend HIL
audit"). Final: 417 findings, 296 canonical (UNCONFIRMED 108 / CONFIRMED 91 /
MERGED 53 / CLOSED 44), 33 HIL flags. Bounded exactly R24–R28 — the R17–R23
overrun corrective (`extension_cap == max_rounds`) is confirmed working.

Paired post-mortem written: technical `experimental_notes/
Exp40_R24_R28_Convergence_Test_Postmortem_2026-05-16.md`, plain-English
`..._Plain_English_2026-05-16.md`, TTS `~/Desktop/CDSFL_tts/
Exp40_R24_R28_Convergence_Test_Postmortem_2026-05-16.txt`.

**Next-work pointer (recommendation, not yet founder-approved):** the open
question has moved off the deadlocks. A targeted study instrumenting
raw-vs-novel divergence and re-examining the γ definition + gate threshold on
a rich target is the indicated next step before any further single-mechanism
fix. G7 stays enabled (validated, correct). Awaiting founder direction.

### Superseded resume pointer (R24–R28 launch — retained for trail)

**Exp 40 R24–R28 was launched 2026-05-16 ~17:56 BST** (founder-directed clean
convergence test, G7 ON, `merge_arbitration_enabled=true`, `max_rounds=
extension_cap=29`, target `_feedback.py` held stable, in-round re-ask not
bundled). Ran 5,533 s, exactly R24–R28, clean stop. Result above.

### Superseded resume pointer (R17–R23 morning review — retained for trail)

**Next action — founder morning review (2026-05-16). Exp 40 R17–R23 COMPLETE; full overnight delegation discharged.**

Exp 40 resume ran 03:32:53 → 05:45:27 BST, 7,954 s, exit 0, clean stop on
the round-cap boundary. **Executed R17–R23 (7 rounds)** — see Caveat 1.
Final γ 0.048 (deep converged-by-decay; γ-alt not met). Registry 260
canonical (CONFIRMED 95 / OPEN 64 / CLOSED 40 / MERGED 32 / UNCONFIRMED 29).

**All fixes validated in production:** 16 DeepSeek/Gemini reasoning-trace
recoveries; Fix-1b honest logs every round; Fix-1c windowing fired
AUTOIMMUNE correctly at 3/3 and tracked sustained bias to 6 rounds (both
halves proven); Fix-1e REFORMAT path active each round; Fix-1a — no
mangled IDs in 370 findings; 12 BUGZILLA verified CLOSED. **Collision
detector: ZERO collisions in 7 rounds → §6c Q2 UUID-namespace deferral is
now EVIDENCE-JUSTIFIED.** G7 stayed disabled (§6c); D4 deadlocks recurred
as predicted (C0023 = 21 rounds, longest in project history) — the Exp 41
enablement evidence.

**Caveat 1 (operator config error):** founder requested R17–R21 (5);
config (max_rounds=22/extension_cap=24) + the runner's active
budget-extension mechanism yielded R17–R23 (7). Not a runaway (investigated
before acting; loop_cap ceiling held; ran to clean completion). Standing
corrective in §6c: for a bounded N-round resume set extension_cap ==
max_rounds.

**Caveat 2 (confound):** target `_feedback.py` was modified this session
(collision detector); panel reviewed changed source → rising novel-CRIT
[2→15] is largely artefact, not pure convergence. Any R17–R23 vs R10–R16
comparison must carry this caveat.

Post-mortem: `experimental_notes/Exp40_R17_R23_Resume_Postmortem_2026-05-16.md`
(+ plain-English + TTS). No FFAFP pause was needed across ~135
monitor events.

**Exp 41 entry actions (now evidence-backed, §6c + Exp 41 matrix row):**
enable G7; UUID-namespace stays deferred (detector proved zero collisions);
in-round dispatch deferred (1e handled load). All pending founder review.

---

### Superseded resume pointer (R17–R21 launch — retained for trail)

**Next action — Exp 40 R17–R21 running (2026-05-16, founder asleep, autonomous).**

Neutral timing re-confer complete (the 2026-05-15 biased round is superseded).
5-model, no presupposed answer, panel falsified CC1 reasoning. Outcome
(binding, recorded in consolidated plan §6c + Exp 41 matrix row):
- **G7 enablement → DEFER to Exp 41.** Reverses CC1's prior enable-now
  position. Reason: candidate-set construction in `_try_merge_arbitration`
  never live-tested → silent-wrong-merge risk corrupts the R17–R21
  convergence signal. G7 stays config-disabled for R17–R21.
- **UUID-namespace → DEFER pre-Exp 41, collision-evidence-gated.**
  Observation-only collision detector implemented now
  (`_feedback.detect_finding_id_collisions`, 10 tests) as the evidence
  gate. Exp 41 reads the R17–R21 accumulator; any cross_model collision
  ⇒ implement before Exp 41.
- **In-round reformat dispatch → DEFER to Exp 41**, R17–R21-evidence-gated.
- Standing methodology adopted: fix-timing confers never present deferral
  as the baseline (§6c methodology note).

Outcome notes: `experimental_notes/Exp40_Timing_Reconfer_Outcome_2026-05-16.md`
(+ plain-English + TTS). 210 regression tests pass. R17–R21 restarting on
the fix tranche + collision detector, G7 disabled — founder-authorised this
turn ("implement all fixes present and then restart experiment 40").
Monitoring at 60 s with FFAFP discipline; paired post-mortem at close.

---

### Superseded resume pointer (fix-tranche post-mortem review — retained for trail)

**Next action — founder review of the fix-tranche post-mortem (15 May 2026, evening).**

The post-continuation 12-item fix tranche is complete (9 engineering items
+ local architectural P-pass; 229 tests pass; **sv landed HEAD `7ecbf26`
pushed to origin/exp39-experimental**, working tree clean; codex CLI
restored 0.130.0 notarized+authed). Read in this order:
   a. Plain-English `experimental_notes/Exp40_Fix_Tranche_Postmortem_Plain_English_2026-05-15.md`
      (or TTS `~/Desktop/CDSFL_tts/Exp40_Fix_Tranche_Postmortem_2026-05-15.txt`).
   b. Technical `experimental_notes/Exp40_Fix_Tranche_Postmortem_2026-05-15.md`
      — per-item outcomes, test ledger, files changed, deferral rationale.
   c. The 15 May 22:30 entries in the Completed log below.

**Live architectural confer — CLOSED 2026-05-15 23:25 BST.** Ran the
five-model compelled-convergence round (Gemini/Codex/CC2/ChatGPT/
DeepSeek, star, `cdsfl_core_formal.md`, single round). **5/5 on all
three questions + 5/5 OVERALL: YES to (a) resume R17–R21 with G7
disabled, YES to (b) enable G7 at Exp 41 as designed. No blocking
items.** Sole caveat = operational discipline: watch the two
documented escalation triggers during R17–R21 (mangled IDs → UUID;
non-stale extract failures → in-round dispatch). Outcome note:
`experimental_notes/Exp40_Architectural_Confer_Outcome_2026-05-15.md`
(+ plain-English + TTS). Logs:
`bench/logs/confer_exp40_architectural_2026-05-15/`.

**One open item remains a founder DECISION, not unfinished work:**
   - **Exp 40 R17–R21 resume** — multi-hour run, significant OpenRouter
     spend, founder's established practice is close monitoring. Full fix
     tranche folded in + regression-clean; the panel has now validated
     the architecture is sound to resume (G7 disabled) and to enable G7
     at Exp 41. Ready when the founder elects to start it, at the
     preferred monitoring cadence. This is a cost/supervision call, not
     an architectural one — the architecture is signed off.

**sv** is also pending founder direction — the whole tranche is one
coherent regression-clean changeset ready to commit (new module
`bench/merge_arbitration.py`, 6 new test files, 10 modified files,
3 post-mortem docs, tracker).

---

### Superseded resume pointer (continuation post-mortem review — retained for trail)

1. Read the Experiment 40 continuation paired post-mortem in this order:
   a. Plain-English companion at `experimental_notes/Exp40_Continuation_Postmortem_Plain_English_2026-05-15.md` (or TTS mirror at `~/Desktop/CDSFL_tts/Exp40_Continuation_Postmortem_2026-05-15.txt`) — entry point for the narrative.
   b. Technical version at `experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md` — file paths, registry counts, commit hashes, fix-effectiveness assessment per fix, five anomalies catalogue, G7 deadlock evidence cluster.
   c. G7 design (pre-run) at `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md` and its plain-English companion — the rule that the continuation produced evidence for.
   d. The 15 May entries in this file's "Completed in current window" log — chronological summary of the pre-continuation fix tranche, the run itself, and the post-mortem write.

2. Four founder decisions now actionable:
   a. **G7 implementation decision.** Continuation produced the deferral-evidence cluster the G7 design was waiting for: six distinct findings hit D4 MERGE DEADLOCK escalation, including a fourteen-round marathon (C0023) and a twenty-way ambiguity (C0008). Decide: (i) proceed with implementation against the design at the path above, (ii) adjust design first, (iii) defer pending more evidence.
   b. **Five anomalies disposition.** Five anomalies identified for next-experiment attention (DeepSeek 0-char Phase-1 sections; parser code-fragment finding-IDs; LLM classifier sub-threshold OVERRIDE logs; RT v2 AUTOIMMUNE flag noise on Gemini per-round; ITC DEGRADATION-in-convergence false positive). None blocks Exp 41 entry. Decide: fix all before Exp 41, fix some, or defer to inline-fix-as-needed.
   c. **Resume Exp 40 vs advance to Exp 41.** Continuation reached deep convergence by γ-decay (terminal 0.034) but γ-alt boolean was not met. Two more rounds (R17, R18) within `max_rounds=18` are possible via `--resume` with a `wall_clock_cap_s` bump. Alternatively advance to Exp 41 (bounded mathematics module) per the planned arc. The post-mortem flags Exp 41 as the natural place to introduce G7 if implementation is approved.
   d. **sv timing.** Three new post-mortem documents are untracked + run produces many untracked log files. Decide: sv now (atomic post-run state preservation), or defer until after G7 implementation decision.

3. After founder decisions land, the resume pointer advances accordingly — either to G7 implementation surface (`bench/merge_arbitration.py` + runner integration around line 870–900 per the design's §Implementation Surface), to anomaly fixes, to Exp 40 R17–R18 resume, or to Exp 41 launch prep.

**Blocker on autonomous advance.** Founder decisions a–d above. The post-mortem captures all data needed for those decisions; no further automated work is outstanding.

**Context for the waking review.** HEAD `3bbf2c7` on `exp39-experimental` (pushed to origin pre-continuation). Working tree dirty: three new post-mortem documents (two markdown + one TTS), one updated tracker (this file + repo mirror not yet synced), many untracked per-round model output JSON files under `bench/logs/exp40_gate_20260514T020550Z/`, run log at `bench/logs/exp40_continuation_20260515T021531Z.log`, runner state + final report. Pre-continuation test count was 1255 (1121 non-network pass); the continuation did not run additional tests. [Correction 2026-07-31: read that as 1255 collected and 1121 passing in a hand-curated subset that was NOT offline. `-m "not network"` was not the selector, the six excluded files were chosen by hand and never named anywhere in the record, and test files reaching live claude-CLI dispatch were inside the 1121. The figure is therefore unreproducible and is not offline evidence. See `resources/RECOVERY.md`.] The runner exited cleanly (exit code 0) at 05:20:26 BST after 7,478 seconds. No FFAFP-grade halts triggered across approximately eighty monitor events captured during the run.

**Phase E closed. Phase F remains gated on Exp 40–54 completion. Exp 40 is in a clean stopping state but neither γ-alt nor max-rounds convergence was reached; the founder's decision on resume-vs-advance determines whether Phase F advances to Exp 41 immediately or after a brief Exp 40 R17–R18 leg.**

---

## Notes on audience and format (non-content)

This file deliberately breaks some of the note-standard rules that apply to TTS and third-party-facing documentation:
- It uses process-adjacent headers ("Active work queue", "Phase A / B / C / …") because those headers are load-bearing for navigation by the agent.
- It uses short internal labels (G1–G9, A1–A8, etc.) without inline glossing on every reoccurrence, on the basis that the tracker is the label's own context.
- It uses first-person reference-frame ("resume point", "next action") because the intended reader is the agent continuing the work.

The foot-line is still applied per the standard's discoverability requirement.

---

Written under CDSFL note standard v1 (21 April 2026).
