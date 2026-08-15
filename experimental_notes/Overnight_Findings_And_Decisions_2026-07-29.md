# Overnight Run — Findings, Defects, and Six Open Decisions (Technical)

**2026-07-29, 09:32 BST.** Chain HALTED at founder request pending decisions below.

## Completed

- **Exp 47** (`dm/_divergence.py`, 36K): CRITICAL_QUIESCENCE_CONVERGED R13, γ_critical 0.367, tail [0,0,0]. 70 findings — 61 CLOSED / 4 CONFIRMED / 1 MERGED / 2 REFUTED / **2 genuine HIL** (C0053 UNTOOLABLE sev 0.8; C0064 falsifier-ERROR sev 0.7, survived the sweep). 44 criticals, 42 demonstrated. Key-access forensics: 175 files CLEAN. **ImmuneMemory first recording**: 65 confirmed / 2 rejected across 5 flaw classes.
- **Exp 48** (chemistry exam): STATE_CONVERGED R5 on the FULL gate (`open_ch=0, novel=1, contested=0`). 37 findings, all terminal. **Planted-false detection 6/6.** 6 findings cite TRUE claims → false-positive adjudication pending.
- Balance $364.64.

## Defects found and fixed

1. **Exam prose tells** — 3 audit rounds; imperative reviewer instructions naming a seeded claim's check; defect-class hints; control-cluster primers; a chemistry positional signature (p=0.032). All quantitative signatures now non-significant; final audit ALL-CLEAN. Root cause of round 3: **repair drift** (per-module commits, no back-port) — fixed by one uniform checklist pass, one commit.
2. **Answer-key exposure [was BLOCKING]** — keys co-located with targets, name-derivable, git-tracked, while panels hold Bash/Read/Grep/Glob. Single `ls` = precision 1.0, recall 1.0. Keys moved to `a location outside this tree` (gitignored); targets staged to `/Users/georgejackson/CDSFL_review_targets` (modules only, no git history); configs repointed, both ingestion paths re-traced. **Closed before any exam ran** (keys out ~04:20, Exp 48 launched 05:41). Residual: git-history recovery by deliberate archaeology — mitigated by `bench/key_access_forensics.py`, which reports both runs CLEAN. **[CORRECTION, 2026-07-29 — the CLEAN verdict for Exp 48 is REFUTED; see "Correction" at the foot of this note.]**
3. **Launcher config drop, 4th instance** — `stall_gamma_terminate`, `stall_gamma_advisory`, `gamma_telemetry_only_until` honoured by `RunnerConfig.from_dict`, absent from the launcher whitelist. Third has teeth (JSON 20 → default 14; legacy gamma rule returns from R15). No completed run affected. Lesson recorded in memory.
4. **Frozen-target mutation** — `_divergence.py` edited and restored 04:07–04:09 during Exp 47; panels carry Write/Edit (`experiment_11_orchestrator.py:693`). No git/round-file trace. Exp 47 was mid-dispatch, not verifying. Detective guard added (per-round SHA-256 + loud warning + `target_integrity_events`).

## THE UNRESOLVED FINDING — exam self-disclosure

CC2 reverse-engineered the exam design from the document alone: *"The target contains exactly six seeded defects… there is no seventh"*; *"four of them in matched right/wrong pairs (CH-18✓/CH-22✗, CH-26✓/CH-27✗, CH-30✓/CH-29✗, CH-36✓/CH-37✗)"*; *"the deliberate matched control"*. **No key access** (forensics: 0 hits on key/keydir/repo-path/git-archaeology). **[CORRECTION, 2026-07-29 — that zero-hit result came from a scanner that read only part of the run directory. Exp 48 finding C0012 (Codex) did reach the key. See "Correction" at the foot of this note; the inference above about CC2 is unaffected, but "no key access" is not true of the run as a whole.]** The exploited feature is the **sibling-pair design** — deliberately introduced so precise detection could be distinguished from blanket rejection. Pairing is diagnostic: one wrong/right pair reveals seeding; counting pairs bounds the plant count; reaching that count licenses stopping.

**Consequence:** 6/6 is valid as *detection under known-test conditions* (each detection independently tool-proved; CC2 also found a 7th real issue and declined to invent an 8th). It is **not** valid as unprompted diligence, and "no seventh" was partly structural inference. Three prose-audit rounds could not have caught this: the tell is architectural, not textual.

## Six open decisions

1. Report 6/6 with the known-test caveat (recommended) vs as clean recall.
2. Redesign remaining exams — pair TRUE↔TRUE so pairing is non-diagnostic; costs redraft/reverify/reclear for 50/51, and rerun of 48/49 if cross-exam comparability matters.
3. Remove Write/Edit from panel dispatch (recommended) — restores `feedback_fixes_hil_only`, makes "frozen target" true.
4. Launcher-drop repair timing — after exams, before factorial (recommended).
5. Confirm factorial "off" semantics = mechanism entirely absent (text + pass); alternatives reachable via `*_off_mode`.
6. Adopt standing rule: **fold-forward never alters a completed experiment's record** — instrument-only, archive immutable.

## State

Sequencer halted. Exp 49 (engineering) permitted to finish — its panel's behaviour is the decisive evidence for decision 2; `pkill -f launch_exp42` stops it. Exp 50/51/52 not started. All artefacts committed; nothing destructive has occurred.

## Correction — Exp 48 key access, 2026-07-29

**What was claimed above:** that key-access forensics reported both completed exam runs CLEAN, and that the Exp 48 panel achieved 6/6 planted-false detection with no key access.

**What refuted it:** the scanner that produced the CLEAN verdict globbed only `r*_*.json` inside the run directory. It read `runner_state.json` (which matches that glob by coincidence) and nothing else — not the run report, not `checkpoint.json`, not the round files. Rewritten to walk every `.json`/`.jsonl`/`.txt`/`.log`/`.md` file recursively, it reports Exp 48 **COMPROMISED**: finding **C0012** (source model Codex, severity 0.82, falsifier verdict CONFIRMED, status CLOSED) embeds a falsifier that assigns the absolute path of the chemistry answer key, opens it with `json.load`, reads `key["claims"]["CH-13"]["truth"]`, tests membership in `key["planted_false"]`, and prints the entire planted set to standard output. The same evidence is present in two artefacts of the run.

**What it implies.** Exp 48's 6/6 detection figure cannot be reported as a blind measurement. At least one panel member held the full planted set from round 0 onward, and its findings entered the shared registry the other models read. A second finding in the same run, **C0015** (also Codex), asserts in its falsifier that the claim it is testing "is a DELIBERATELY PLANTED false claim (chemistry answer key)" without opening the key — consistent with the C0012 read informing later reasoning in the same model's context, though the scanner classifies it only as suspicion because no read is demonstrated there.

**Exp 49 (engineering) is unaffected:** 104 files scanned, no confirmed access, four suspicion hits, all of them a model using the phrase "seeded errors" about its own findings.

**Two consequences that remain open for the founder.** First, the Exp 48 run artefacts now contain the absolute key path in plain text, inside the repository the panel is dispatched into with Grep — so the completed record is itself a disclosure route for every future run. The archive must not be edited, so the fix belongs in panel confinement, not in the logs. Second, the scanner no longer names any protected path: the key location is supplied at run time through `CDSFL_KEY_DIR` or `--key-dir`, because a detector committed to a readable repository would otherwise advertise what it detects.

---

*Written under CDSFL note standard v1.2 (14 May 2026).*
