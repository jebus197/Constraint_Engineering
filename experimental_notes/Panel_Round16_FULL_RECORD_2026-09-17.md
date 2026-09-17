# Panel round 16 — the full record

**2026-09-17, 02:13 BST (Europe/London).** Dispatched 01:14, both seats returned by 01:37.

**Seats: cc2 and fable only. 0 paid dispatches** — verified before launch by importing the dispatcher under `PANEL_ONLY=cc2,fable` and reading its resolved roster. Each seat ran in its own sandbox copy (task A20); the live tree was untouched by either, confirmed by the attributor.

| seat | ok | chars | tool calls | elapsed |
|------|----|-------|-----------|---------|
| cc2 | True | 10,896 | 150 | 1114.0s |
| fable | True | 35,162 | 388 | 1417.3s |

**The brief** is `experimental_notes/panel_briefs/Overclaiming_Entries_Brief_2026-09-17.md`. The dispatched copy at `bench/logs/panel_round16_2026-09-17/BRIEF.md` is preserved exactly as sent, including the figures both seats went on to refute, because a brief records what the seats were actually asked.

## What was adopted, and what was verified before adopting it

Under `no-model-voting`, nothing here was accepted because a seat asserted it. Each item below was re-executed independently before any change was made.

1. **The census numerator was short by 1** (cc2). Its round-2 half was a hand-typed tuple of 6 where the adjudication marks 7, dropping `7.3`. Confirmed by re-reading the committed evidence. Fixed: the census now derives that half.
2. **The census denominator was the wrong population** (fable). It counted today's DONE markers while the numerator came from the audited set, so never-audited `A11` was silently counted as audited-and-clean. Confirmed. Fixed: the denominator is the audited population, and the excluded remainder is printed.
3. Both compose. The figure moved from **30 of 85** as dispatched to **31 of 84 = 36.9048%**, Wilson [27.3701%, 47.5848%], statsmodels and scipy agreeing to 0.0e+00.
4. **`--help` still destroyed content under `-m`** (fable). Confirmed by reproduction in a clean worktree with a fresh copy per invocation form. Measured across all 40 scripts carrying that guard: **2 of 40 = 5.0000%**, Wilson [1.3821%, 16.5039%], changed real content. A third script, `compose_all_2026-08-23`, leaked the same guard and ran over 240 seconds under `--help`. All 4 are fixed and verified inert under both forms.

## What is NOT yet adopted

fable proposes closures for all 31 entries; cc2 closed 2. **Those entry-level closures are not applied.** Each is a claim about an entry's evidence that must be re-executed independently before it changes the record, and that work has not been done.

## Errors of mine that the panel exposed or that surfaced while checking it

- The census defect was in an instrument I wrote and committed the same night, and it is the class the entries are being audited for.
- A first blast-radius probe used `git status`, which cannot see writes into gitignored paths, and reported 1 of 40. **Withdrawn.**
- A second counted `__pycache__` bytecode as content and reported 40 of 40. **Withdrawn.**
- A first reproduction of the `-m` defect reused one copy of the record across both invocation forms, so the second form had nothing left to destroy. **Withdrawn.**
- A commit message written with backticks inside a double-quoted shell string executed them: `import` resolved to ImageMagick and spliced its usage text into the body. Amended.
- An edit to entry A26 put its supersession on a line of its own, orphaning the entry from its marker and reddening 2 guards. Repaired.

---

## cc2 — complete and unedited

<!-- verbatim-begin: panel round 16 cc2 reply -->

All green. Two entries closed, two brief-level defects found, one candidate withdrawn. Three passes run; the fourth produced nothing new.

---

# Verdict

I closed **2 of the 30 entries** with executed fixes, and found **2 defects in the brief's own instruments** — one of which means a 31st entry exists that the closing programme would never have reached.

---

## entry: `census` — the brief's headline instrument (NEW FINDING)

- **claim**: "30 of 85 = 35.2941%, Wilson [25.9725%, 45.8875%]" are the DONE entries that claim more than their evidence shows.
- **verdict**: **UPHELD — the count is short by one.** The figure reproduces exactly from its committed script, so it passes `measured-rate-travels-with-its-script`. But the script derives its round-1 half from the committed verdicts and carries its round-2 half as a **hand-typed tuple** `ROUND2_UPHELD = ("3.3","9.2","9.3","9.4","L2","P7")`. The committed evidence marks **seven** round-2 entries non-`SUPPORTED`. **`7.3` (verdict PARTIAL) is missing**, and nothing ever compared the tuple to the file it was transcribed from. `7.3` is a real DONE entry. The round-1 half is intersected with real ids; the round-2 half was not — an asymmetry that would also let a phantom id inflate the numerator.
- **fix**: replaced the tuple with `round2_upheld()`, which reads the adjudication and takes every verdict `!= SUPPORTED`; and made the intersection symmetric: `return (r1 | round2_upheld()) & real, real`.
- **falsifier**: `scripts/falsifier_round2_upheld_is_complete_2026-09-17.py`
- **falsifier_result**:

```
BEFORE  round-2 NOT 'SUPPORTED' : 7  ['3.3','7.3','9.2','9.3','9.4','L2','P7']
        census hand-typed       : 6  ['3.3','9.2','9.3','9.4','L2','P7']
        OMITTED BY THE CENSUS   : ['7.3']
        FALSIFIED
        AssertionError: the census omits 1 entry/entries its own committed evidence
        marks as claiming more than it shows: ['7.3']. The reported count of 30 is short by 1.
AFTER   census round-2 set (DERIVED) : 7  [...'7.3'...]
        OMITTED BY THE CENSUS        : []
        OK: census set matches its evidence                              EXIT=0
```
Corrected figure: **31 of 85 = 36.4706%, Wilson [27.0293%, 47.0819%]**, two tools agreeing to 0.0e+00.
- **control**: reverted the census to the original in place → falsifier RED again with the identical assertion; restored → GREEN.
- **simplest_sufficient**: deriving is *cheaper* than guarding — it removes the failure mode by construction. I then **deleted my own phantom-id detector**, because the symmetric intersection makes that condition structurally impossible and an addition nothing reaches is not additive.
- **refutation**: show that round-2 `PARTIAL` does not mean "claims more than its evidence shows". It does — 7.3's own record says the evidence "does not establish the thing the task was set to do".

## entry: `L2`

- **claim**: moving the quote mask before the sentence split removed 8 false positives and added 0, across 379 notes / 1138 findings, 0.70%, Wilson [0.4%, 1.4%].
- **verdict**: **UPHELD — but the audit's diagnosis was wrong on the decisive point.** The audit read the script's "19 ADDED" as contradicting the entry's `0 added`. It does not. `count()` keyed findings on **paragraph number**, and the two splitters number paragraphs differently (`"\n\n"` vs `re.compile(r"\n[ \t]*\n")`). I printed the pairs: all 19 are byte-identical in rule and subject, shifted only in index — `(111,'UNNAMED SUBJECT','the system')` → `(117,...)`, `121→127`, `156→167`, `183→194`; rule multiset identical, index multiset not. **The script was contradicting itself.** What genuinely overclaimed was all five stale figures.
- **fix**: keyed `count()` on `(rule, subject)` as a `Counter` (multiset, so dropped-index collisions keep multiplicity); re-derived the entry's figures to **412 notes, 11 removed, 0 added, 1.0648% of 1033, Wilson [0.5966%, 1.8890%]**.
- **falsifier**: `scripts/falsifier_L2_figures_reexecute_2026-09-17.py` — runs the named script and compares every figure the entry states.
- **falsifier_result**:

```
BEFORE  notes scanned: L2 states 379, script prints 412
        false positives removed: L2 states 8, script prints 11
        findings denominator: L2 states 1138, script prints 1033        FALSIFIED
AFTER   notes scanned 412=412 | removed 11=11 | denominator 1033=1033 | added 0=0
        OK: every figure L2 states re-executes from the script it names   EXIT=0
```
`0 added` is now **demonstrated**, and the script exits 0 instead of 1 — a standing false alarm against a fix that introduced nothing.
- **control**: two independent reverts. Revert the *entry text* only → RED on all three figures. Revert the *script key-fix* only → RED with `exit code: 1`, `removed 11 vs 29`. Both restored → GREEN. Named evidence still `17 passed`.
- **simplest_sufficient**: I tested the cheaper option and it **provably cannot work**. The existing 8th commit guard passes L2, because `proportion_confint(8, 1138, 'wilson')` *is* exactly `[0.4%, 1.4%]` — arithmetically perfect, describing a corpus that had grown. That is the wrong-but-coherent class `wilson_interval_consistency.py` disclaims in its own docstring. Re-execution was required; re-checking could not reach it.
- **refutation**: show a finding in the `+19` whose rule or subject differs. The multiset equality says there is none.

## entry: `P7`

- **claim**: the assistant is bound by the same conditions as the seats *mechanically* — figure re-execution, Wilson checking, a DONE-evidence guard, `unsupported_done_entries`.
- **verdict**: **UPHELD.** The mechanisms exist and work; the named evidence does not establish them. Proven by **mutation, not classification**: destroy `check_declared_figures` and `unsupported_done_entries` outright and P7's named evidence stays green at 12/12. Its named file contains `assistant` 0 times, `check_declared_figures` 0, `unsupported_done` 0, `GAMMA_BANDS` 0.
- **fix**: re-pointed the marker to four files (adding `test_panel_brief_format_2026-09-09.py`, `test_done_markers_carry_evidence_2026-09-10.py`, `test_stated_gate_count_matches_measurement_2026-09-07.py`); and corrected the prose's `scans 1,522 files` — it reads **1,767** today — by recording that the count tracks the corpus and is deliberately not pinned, since pinning a drifting figure manufactures a standing false alarm.
- **falsifier_result**:

```
BEFORE  check_declared_figures   -> exit=0  12 passed    NOT DETECTED
        unsupported_done_entries -> exit=0  12 passed    NOT DETECTED
        FALSIFIER RED -- P7's evidence does not establish P7's claim
AFTER   BASELINE: exit=0  395 passed, 2 skipped
        check_declared_figures   -> exit=1  14 failed, 381 passed   DETECTED
        unsupported_done_entries -> exit=1   1 failed, 394 passed   DETECTED
        FALSIFIER GREEN                                              EXIT=0
```
- **control**: reverted the marker with the mutations held identical → RED, both `NOT DETECTED`. Restored → GREEN. Verified no mutation residue: `grep -c "_dead_"` → 0, 0.
- **simplest_sufficient**: no new test. The mechanisms were already held — the marker pointed at the wrong file. I also **rejected the audit's other P7 objection**: `hooks/pre-commit:60` says verbatim `# THE 8th GUARD`, so the entry quotes the hook's own numbering. Sourced, not invented. Left alone.

## entry: `brief §2` — "25 of the 30 name evidence that asserts on source text"

- **verdict**: **REFUTED as stated — not derivable.** A precise count cited with no producing script, which this project's own rule forbids. I wrote the missing script (`scripts/execute_not_grep_census_2026-09-17.py`) and it will not pin the figure: the mechanical bracket is **[3, 28] of 30** — 25 wide on a population of 30.
- The instructive part is **my own classifier being wrong twice**. Strict count moved **22 → 11 → 3** as I found each further way a test reaches code: direct import, `spec_from_file_location` (L2's file, which calls `LINT.lint` 17 times), and `sys.path.insert` + bare `import reference_runner_v3 as rr` (9.1's file, which calls `rr.study_programme_report`). **The naive draft lands at 22 — near the brief's 25 — precisely by missing the load forms that make the evidence behavioural.**
- **falsifier**: `scripts/falsifier_import_forms_are_detected_2026-09-17.py`. **control**: restored the draft-1 regex → RED on forms B and C with the live calls named; restored → GREEN.
- **The defensible floor**: **3 of 30** name evidence that loads no repository module at all. That number is real; 25 is not measured.

## Withdrawn candidate — reported because a near-miss is information

`bench/tests/test_task_list_figures_have_producers_2026-09-10.py` (V4's evidence) **fails 2 of 6**, which would refute the brief's "No test fails. Every named evidence file exists and passes." I reverted my edits and reproduced it identically on a pristine tree, then found the cause: this panel copy has no `.git`, `git ls-files` exits 128, and the producer **correctly raises** `GitCannotAnswer` rather than fabricating "127/127 = 100.0000%". **The guard working as designed, not a defect.** This is the failure mode this repository already documents — a seat's red is evidence about the copy, not the repository. I nearly filed it.

---

**refutation (of my whole answer)**: run `scripts/falsifier_round2_upheld_is_complete_2026-09-17.py` on a tree where `round2_never_audited_13.json` marks 7.3 `SUPPORTED`; my central finding dies. For L2, produce a corpus where the paragraph-keyed and rule-keyed counts agree — then the index was never the artefact.

**disagreement**: the brief's framing — *"No test fails. Every named evidence file exists and passes. The gap is between what the tests establish and what the entries CLAIM"* — is too clean, and it is the reason a 31st entry was invisible. The audit is **not** the privileged instrument the brief treats it as: its round-2 half reached the census as a typed constant, not as a measurement, which is the same class of defect the 30 entries are being closed for. The brief also says "**84** DONE entries" where its own script says 85 (I confirmed 85; an 86th loose match is prose, not a marker) — three different counts of the same list inside one document. And "25 of the 30" is a two-figure count with no producer in a brief whose first instrument is `measured-rate-travels-with-its-script`. **The instruments measuring the overclaiming overclaim in exactly the same way.**

**termination**: **3 passes.** Pass 1 gave the census and L2; pass 2 gave the `execute-do-not-grep` census and P7; pass 3 was guard re-verification, which surfaced the V4 candidate (refuted) and P7's drifting count (fixed). The final sweep — all four falsifiers `EXIT=0`, the marker guard `350 passed`, the Wilson guard `Every stated interval agrees` — produced no new above-threshold finding, so I stopped.

<!-- verbatim-end -->

---

## fable — complete and unedited

<!-- verbatim-begin: panel round 16 fable reply -->

All 30 entries are closed with executed evidence. I independently re-ran the decisive producers before compiling (sweep `_TERMINAL` at `bench/reference_runner_v3.py:6219` excludes CONFIRMED while the report block at `:859-866` includes it; `done_evidence_commit_coverage` prints **2/81** not 2/52; `capabilities_disabled_by_config` prints **15/6/40.0000%** not 18/9/50%). The workers' findings survive my own execution. Final seat answer follows.

---

# Seat answer — closing the 30 flagged DONE entries

**Method.** Every entry's named evidence was executed (`pytest -q`, never the full suite); every proposed fix was demonstrated by a falsifier run RED against the current state and GREEN against a patched temp copy, with a control showing the falsifier can fail. No repo file was modified; falsifier artifacts live in `/tmp/panel_gP/`, `/tmp/panel_g236/`, `/tmp/panel_gRV/`, `/tmp/panel_gMISC/`, `/tmp/panel_seat_main/` and the session scratchpad (`panel_g9/`, `panel_gA/`, `panel_g18/`). All intervals cross-verified statsmodels `proportion_confint` vs closed form (agreement ≤1e-9 or better). `CRITICAL_SEVERITY_THRESHOLD` read from `bench/reference_runner_v3.py:6902` = 0.7.

**Tally: 0 REFUTED outright, 13 UPHELD, 17 PARTIAL.** No entry was fully clean; equally, several audit limbs were themselves refuted by execution (noted per entry). The dominant defect class is confirmed and is worse than the brief states: **typed figures drift** — every numeric claim typed rather than read from an instrument has drifted, including the audit's own figures within six days, and including the brief's (see Disagreement).

---

## P-group (evidence `test_panel_conditions_are_met_2026-09-10.py`, `12 passed in 4.32s`)

**P1** — *claim:* every post-ruling round used the schema dispatcher; 0 paid replies; "0 of the 24 directories dated after it" Wilson [0, 11.6970%]. — *verdict:* **UPHELD.** Named file tests only the cost half (its `_is_paid` has zero call sites; inline predicate at :163 is what runs). Executed: archive holds **26** post-2026-09-05 dirs, not 24, and the stated interval is Wilson for 0/**29** — count and interval disagree with each other AND the archive (0/24→[0,13.7976%], 0/26→[0,12.8729%], 0/29→[0,11.6970%]). — *fix:* marker gains `test_panel_runs_under_the_schema_2026-09-07.py, test_panel_brief_format_2026-09-09.py` (both run: `31 passed`); prose narrowed to the validator-gate mechanism (dispatcher identity is unrecorded in seat files); figure → "0 of the 26 … Wilson [0.0000%, 12.8729%], re-measured 2026-09-17". — *falsifier:* `/tmp/panel_gP/falsifier_p1_p3_p7.py`; RED `AssertionError: P1 evidence […] names no file that tests the format/schema half` + `P1 states 0 of 24; archive holds 26` exit=1; GREEN on patched copy exit=0, and patched copy passes `scripts/wilson_interval_consistency.py`. — *control:* the two RED runs. — *simplest_sufficient:* both added files already exist and pass. — *refutation:* a sidecar recording dispatcher identity per round, or a shipped predicate yielding 24 dirs with Wilson upper 11.6970%.

**P3** — *claim:* seats use the harness; 28/28 vs "8 of 134", Fisher 1.495e-24. — *verdict:* **PARTIAL.** The P3 tests genuinely execute the reply corpus (30/30 under-ruling replies carry tool calls; floor 23 calls — the round-1 audit's "a single pwd satisfies it" limb is wrong). But no shipped instrument produces 8/134 (walker: 8/**189** = 4.2328%, Wilson [2.1602%, 8.1288%]; 28/28 is now 30/30; 36/162 is now 38/219). — *fix:* marker gains `test_panel_brief_format_2026-09-09.py`; requote all figures to the named walker's population; Fisher → 6.366e-30 (`fisher_exact([[30,0],[8,181]])`). — *falsifier:* same file, check_p3; RED `P3 states 8 of 134 pre-ruling; the cited test's own walker measures 8 of 189` exit=1; GREEN patched exit=0. — *control:* RED runs. — *simplest_sufficient:* marker append + requote, no code. — *refutation:* a committed producer yielding 8/134 today.

**P4** — *claim:* seats must produce and test a fix (delivery rule standing). — *verdict:* **UPHELD.** Prose is true; evidence only pins the past (hardcoded round-7 dir + source-text assert on a frozen BRIEF.md). Executed proof: a mutant archive with an all-prose round 99 passes the named evidence `3 passed, 9 deselected`. Live false zero confirmed: round 15's 5 delivered files sit in the mirror layout; `source_files()` reads only `seat_proposals.diff` → 0. — *fix:* new standing test `/tmp/panel_gP/test_p4_delivery_is_a_standing_condition_2026-09-17.py` (both layouts, rounds 5/6 pinned as the recorded contrast, anti-vacuity `shortfall(n,10)`). — *falsifier_result:* new test vs mutant `1 failed`; vs real repo `1 passed in 0.11s`. — *control:* the mutant failure. — *simplest_sufficient:* one additive test; avoids locking in the round-15 false zero. — *verifier plan:* improved — its item 1 as written would be born RED on rounds 5/6. — *refutation:* an existing delivery-threshold test (grep found none).

**P5** — *claim:* no compelled convergence; disagreement preserved; CC1 synthesises. — *verdict:* **UPHELD.** Vacuity proven by execution: with `_replies()` forced empty **both P5 tests pass** (`0 >= -2`, `set() <= {...}`), and `bench/logs/**` is gitignored, so a fresh clone reports the founder's condition satisfied over 0 replies. CC1 clause has no test anywhere (grep: comments only). Entry's "2 misses" is stale (0 today). — *fix:* new never-vacuous test (mirror corpus + shipped `DISAGREEMENT_RE`, skip-paired-with-assert) + claim-narrowing scoping the CC1 clause as unguarded. — *falsifier_result:* RED `P5 guard reports GREEN over 0 replies` exit=1; GREEN new test skips/fails on empty corpus, `1 passed` on real. — *control:* doctored consensus-only 10-round corpus → `1 failed`. — *refutation:* any suite test that reddens on an empty P5 corpus.

**P7** — *claim:* the assistant is bound by the same conditions mechanically; "scans 1,522 files"; "all 4 defects caught were the assistant's". — *verdict:* **UPHELD.** Named file exercises seat conditions (1 grep hit for any P7 mechanism — a comment). Mechanisms exist and pass elsewhere (`354 passed, 2 skipped`), but the marker names none of them. Executed: the script prints **1,762** files today; `hooks/pre-commit:60-63` records a seat's rounded lower bound among the catches, contradicting "all 4". — *fix:* marker repointed to the four mechanism-exercising files; figures corrected to the script's printed count; attribution sentence deferred to the hook's own record. — *falsifier_result:* RED `P7 says the script scans 1522 files; it scans 1762 today` exit=1; GREEN patched exit=0. — *refutation:* a run printing 1,522 today.

## 9-group

**9.1** — *claim:* the sweep "cannot clear a critical — CONFIRMED is terminal to it, it was never able to". — *verdict:* **PARTIAL, and the entry's sentence is FALSE by execution** (independently re-confirmed by this seat). Sweep `_TERMINAL` at :6219 = `{MERGED, CLOSED, REFUTED, DUPLICATE}` — no CONFIRMED; executed sweep on a stubbed registry: OPEN critical sev 0.75 with CONFIRMED falsifier → `cleared=1 final_status=CONFIRMED`; a CONFIRMED entry is re-offered and re-cleared. The report block at :859-866 states the opposite mechanism. — *fix:* narrow the entry to the true mechanism (severity-gated withdrawal paths; ungated CONFIRMED-demonstration path) **plus a separate above-threshold code finding**: `study_programme_report`'s `why_the_sweep_cannot_clear_a_critical` block emits a false answer and a terminal set contradicted by the sweep — founder item 28 would be ruled on a false blocker. Its own falsifier (`report_vs_sweep.py`) ran RED vs live module, GREEN vs corrected temp copy. — *falsifier_result:* `checker_9_1` RED exit=1 on real list; GREEN exit=0 on patched. — *control:* mutated sweep (CONFIRMED terminal, gated branch) flips the computed ground truth — verdict is computed from executed code, not strings. — *refutation:* CASE1/CASE2 not reproducing (they reproduce).

**9.2** — *claim:* every DONE entry carries evidence (56/56, Wilson [93.5806%, 100%]). — *verdict:* **PARTIAL** (provenance): the claim is true and guarded today (re-derived: 85/85, Wilson [95.6761%, 100%] three ways) — but by `test_done_markers_carry_evidence_2026-09-10.py` (`350 passed`), which the marker does not name; the named study-programme file has 0 inventory-related hits. — *fix:* marker repoint (add the real guard, keep the old file; patched copy parses via `scripts/task_list_markers.py`, 95 entries both copies). — *falsifier_result:* RED `none of them reads the task-list markers` exit=1; GREEN exit=0. — *refutation:* the named file containing any assertion that reads the task list.

**9.3** — *claim:* intake parser: 132/411 raw, 132/138 fenced, 271 unfenced, 6 via tolerant companion. — *verdict:* **PARTIAL.** Mechanism true by execution (10 tests call the telemetry; wiring verified 5 call sites). Figures irreproducible and **internally inconsistent: 411−271=140≠138**; evidence docstring says 132/140; three independent scans give three answers (411/357/439 raw at 119 replies) ⇒ no committed selection rule. All quoted intervals are correct *for their stated counts* — the counts are the defect. — *fix:* withdraw point figures to the band the shipped test actually asserts (fenced Wilson lower >85%), until the scan script is committed. — *falsifier:* arithmetic-coherence checker; RED `411-271=140 != 138` exit=1; GREEN patched exit=0. — *control:* an alternative fix (138→140) also passes — the checker enforces arithmetic, not wording. — *refutation:* one committed scan reproducing the full set (foreclosed by the arithmetic).

**9.4** — *claim:* "a future run cannot report a cross-architecture correlation it did not have the architectures to measure." — *verdict:* **UPHELD (whole-claim), falsified by execution.** A six-seat one-model panel labelled `*-SIM` yields `run_is_simulated=True` yet `answerable=True, why_not=None`; `cfg` is accepted by `study_programme_report` and never read; detection keys on label strings only. A strengthening test would fail against current code, so per protocol the fix is narrowing. — *fix:* entry states detection is label-level only; gating on `run_is_simulated(cfg)`/`registry.model_identity` remains open. — *falsifier_result:* RED exit=1 (computed from two live-code calls); GREEN patched exit=0; the checker auto-flips if the code is fixed. — *note:* the brief's S_k/`compute_sk` framing for 9.4 matches nothing in the audit record (0 grep hits); `compute_sk` was still called — prose target → `NO_SCORE`, as documented — but it is unrelated to 9.4. — *refutation:* `answerable: false` on the -SIM panel (executed: it is not).

## 5.2 / A13 / A20 / A26

**5.2** — *claim:* the dispatcher "every paid review would use" validates first; 49/49 refused, 0/7 under it. — *verdict:* **PARTIAL.** Refusal mechanism real and executed (validator in-process + dispatcher subprocess exit 2). The universal is false: 3 production brief-reading paid dispatchers never import the validator (`confer_track_record_pr_2026-08-22.py`, `confer_stage1_audit_pr_2026-08-18.py`, `confer_enforcement_prose_pr_2026-08-19.py` — computed, matching the verifier's independent list). "0 of 7" has drifted twice (7→15→**16**); headline still reads "Status PROPOSED." above a DONE marker. Re-measured: 49/49 (Wilson [92.7302%, 100%]), 0/16 ([0%, 20.3883%]). — *fix:* narrowing naming the 3 unguarded routes + producer-script requirement for the split. — *falsifier_result:* RED `6 overclaim(s)` exit=1; GREEN after `apply_fix.py` (`4 edits, each hit exactly once`) exit=0. — *refutation:* a committed path making the 3 old dispatchers inert.

**A13** — *claim:* DONE by running the named falsifier; 168/168/168 census. — *verdict:* **UPHELD.** The named file (`5 passed`) establishes the *other* candidate (sandbox distinctness); zero census content. The census IS committed elsewhere and passes (`test_sandbox_survives_the_suite_2026-09-11.py`, `5 passed, 1 deselected`). — *fix:* one marker edit adding that test (comma-lists are the established convention, 6 precedents). — *falsifier_result:* RED `census result (168/168/168) is covered by none of the named evidence files` exit=1; GREEN patched exit=0. — *refutation:* the named file asserting the census (read and run: it does not).

**A20** — *claim:* 1 sandbox per seat; "5 tests, 3 mutations verified red". — *verdict:* **UPHELD on the evidence gap** (every factual sentence true — 29 and 14+16 re-derived in one command each). Decisive execution: deleting `_SEAT_SANDBOXES[_n] = str(sandboxes[_n])` (single live line; the fallback then hands every seat the first seat's tree) leaves the named evidence **`5 passed`** — the guard cannot see the exact round-10 defect. — *fix:* new test compiling and executing `main()`'s real sandbox-population statements + `confine_this_thread`, asserting every seat resolves to its own directory. — *falsifier_result:* new test vs mutant `1 failed` (two seats resolved to the same writable directory); vs real `1 passed`. — *control:* the one-line mutation, verified applied (541→540 lines). — *refutation:* any committed named test that reddens under that mutant (the full named file stayed green).

**A26** — *claim:* `--help` inertness repaired; "all 9 … leave the tree clean"; 7/122 = 5.7377%. — *verdict:* **PARTIAL.** Repair real and executed (both assemblers: exit 0, usage, record byte-identical). Two overclaims: **`python3 -m scripts.assemble_panel_record_0819 --help` still destroys the record** (reproduced: 56,368→1,888 bytes, rc 0 — the `except ImportError: pass` around `_cli_help` swallows the flag under `-m`); and the rate's numerator excludes the 2 assemblers from its own property (corrected 9/122 = 7.3770%, Wilson [3.9294%, 13.4269%]). — *fix:* new executing inertness test (direct-invocation only, since the `-m` leg is genuinely false today) + narrowing recording the `-m` bypass as open. — *falsifier_result:* mutant (call deleted, comment/import kept — the shape the committed substring control at :110 cannot see) → `1 failed`, verbatim: the flag ran the ordinary work; real → `1 passed`. Wording checker RED exit=1 → GREEN exit=0. — *refutation:* `-m --help` leaving the record intact (it did not).

## 1.2 / 8.1 / 8.3 / 10.1

**1.2** — *claim:* the claims-vs-code split "survives reclassifying every arguable entry in all 16 combinations", worst-case p 0.598. — *verdict:* **PARTIAL — and the figure is TRUE and now reproducible.** Catcher stats reproduce exactly from the committed script; the sweep existed in prose only (tree-wide grep: no enumeration, no 0.598). The worker **re-derived the sweep from the entry's own method**: 4 claim-typed SELF rows → 2^4=16; `binomtest` monotone 0.1938→…→**0.5982 = the entry's 0.598 to the digit** (closed form Σ C(16,k)/2¹⁶, k=8..16 = 0.5981903); invariant holds in all 16. — *fix:* commit the producer + test, repoint the marker — keep the entry's strongest sentence rather than strike it. — *falsifier_result:* RED (producer absent) `2 failed, 1 passed`; GREEN (`SWEEP_PRODUCER=…`) `3 passed`; producer prints `WORST CASE p = 0.5982 / INVARIANT HELD IN ALL 16 COMBINATIONS: True`. — *control:* one FOUNDER row retyped → invariant test reddens. — *disagreement with verifier:* its delete-if-irreproducible branch is moot — it reproduces.

**8.1** — *claim:* global `rs` shortcut made project-conditional. — *verdict:* **UPHELD** (work real; named evidence about something else entirely — `test_operational_scripts.py` has 0 references to shortcuts/queue/recovery; green with the fix fully reverted, by construction). — *fix:* new test on `resources/SHORTCUTS.md`/`RECOVERY.md` committed bytes; marker repoint. Deliberately does not assert absence of the old queue names (they legitimately appear in the amendment clause — the verifier's named trap). — *falsifier_result:* GREEN on real `3 passed`; RED on reverted-row copy `2 failed, 1 passed`, while the currently named evidence cannot see the mutation at all. — *refutation:* any committed test reddening on revert (grep: none).

**8.3** — *claim:* "5 of 117" justifies the branch; "attribution was measured, not assumed". — *verdict:* **UPHELD (PARTIAL).** In this gitless staging the evidence still passes `3 passed, 2 skipped` — and `test_it_reports_both_halves` passes because the script prints the measured-sounding attribution caveat **verbatim from constants after measuring nothing** and exits 0. Line 99's `assert branch < off or off == branch` is tautological. Intervals verify for the dated counts; nothing pins the counts. — *fix:* refusal patch (branch-absent path → explicit refusal, exit 4 — mirroring the accepted 8.2 repair) + date-pin narrowing. — *falsifier_result:* RED `exit=0 measured=False caveat_printed=True → CHECK_EXIT=1`; GREEN patched `exit=4 … CHECK_EXIT=0`. — *control:* unpatched copy at the identical temp location → CHECK_EXIT=1. — *verifier plan:* adopt 1–3,5; improve 4 (a no-git environment must still terminate in refusal — this staging has no git at all).

**10.1** — *claim:* "**every failure path says NOTHING WAS CHANGED**"; "13 tests". — *verdict:* **PARTIAL — audit correct when filed; tree since substantially repaired** (bad-flag path now echoes the sentinel before exit 2, execution-tested; 16 tests now, not 13). Residual: the universal is still false at the post-restart partial-failure path (line 110), by the test class's own documented design; and the dry-run test passed here while the DRY branch never executed (rc 1 via unreachable-host — vacuity confirmed by execution). — *fix:* narrow to "every failure path **that exits before the restart step**…", "13"→"16". — *falsifier_result:* RED `qualified=False → CHECK_EXIT=1`; GREEN patched (`edit applied, 1 occurrence`) `CHECK_EXIT=0`. — *refutation:* the universal being literally true of the current script (it is not).

## 2.2 / 3.3 / 6.1 / 6.6

**2.2** — *claim:* every missing falsifier written, 28/28; population correction 817→28. — *verdict:* **PARTIAL — the audit's two CONFIRMED defects are already closed in the current file** (headline self-corrected; marker names all 9 files; all 9 execute: `68 passed, 1 warning in 3.82s`; 28/440 Wilson verified to 1.4e-17). Surviving residue: 3 of 8 exp53 tests silently skip off the founder's machine (unversioned `~/CDSFL_review_targets/…`), demonstrated `5 passed, 3 skipped`. — *fix:* additive test reconstructing SW-21-REF-04.md **byte-exactly from the committed run record** (sha256 matches `bench/cdsfl_registry/targets/MANIFEST.md`), re-running the 3 doc adjudications machine-independently. — *falsifier_result:* RED (old evidence, other-machine TARGET) `5 passed, 3 skipped`; GREEN new test `3 passed in 0.10s`. — *control:* tampered record → `3 errors` at the hash assertion. — *note:* the worker upgrades the verifier's "optional" to worth-doing: this project already lost 68 falsifiers to exactly this out-of-tree pattern.

**3.3** — *claim:* "18 off-switches; 9 READ = 50.0000%"; "NOTHING WAS CHANGED, deliberately"; `_sk_note` quoted as "S_k off in all three arms". — *verdict:* **UPHELD** (re-confirmed by this seat: the named producer prints **"of 15 off-switches found, 6 are READ by the runner = 40.0000%"**, Wilson [19.8245%, 64.2532%] today). Cause: `sk_enabled` flipped to True in all 3 arms at 17:58 BST 2026-09-10 — 18 minutes after the entry's own correction stamp — on the founder's explicit instruction, recorded in `_sk_note` ("TURNED ON … SUPERSEDED, NOT DELETED") and already pinned by the evidence test. The entry prose alone is stale. — *fix:* dated supersession appended to the entry carrying the producer's current figures + additive residue-pinning test (6 unexplained switches). — *falsifier_result:* RED `entry 3.3 quotes figures its named producer no longer prints` exit=1; GREEN on supersession-patched copy exit=0. — *control:* planted `_hardened_gate_note` in a mutated config dir → `1 failed, 1 passed`; real → `2 passed`. — *note:* the flip turned S_k **on** — nothing here demotes gamma or the two-sided gate.

**6.1** — *claim:* stop-reason fallback "catches every remaining exit, including ones added later"; "3 mutations, all caught". — *verdict:* **PARTIAL.** The fallback exists and executes correctly (5 new executing tests pass against it). But: the runner-half evidence is source-text arithmetic — **both semantic kills (guard disabled; sentinel emptied) leave the committed 6 tests green** (`6 passed` twice, demonstrated); the distinguishability test ends in a literal-vs-literal assert that can never fail; and "every remaining exit" is false — `sys.exit(42)` at :14783/:14833 sits inside `run_experiment` with no wrapping try/finally, terminating before the fallback. — *fix:* AST-compile-and-execute test of the actual fallback If-statement (structural selection, so a mutant can't hide) + narrowing scoping the claim to `break`s and scoping out the two resumable HIL pauses. — *falsifier_result:* GREEN real `5 passed in 0.73s`; RED MUT1 `4 failed, 1 passed`; RED MUT2 `3 failed, 2 passed`; committed evidence on both mutants: `6 passed` — blind. — *refutation:* MUT1/MUT2 reddening the committed evidence, or a try/finally routing exit(42) through the fallback (AST scan: none).

**6.6** — *claim:* rewrite attribution "wired, not merely added… both call sites asserted by AST"; "a stale registration is visible as stale". — *verdict:* **PARTIAL.** The attachment is correct (proven by executing the real `if _prev_h:` branch — claim true, evidence wrong: the committed check is a substring assert inside a class whose docstring says "AST, not grep"). The staleness claim is **false by measurement**: `seat_done` has no production caller; after a 5-seat then 2-seat round, `seats_in_flight()` reports 5 (actual live: 0), dead entries oldest and unmarked. — *fix:* executing attribution test + narrowing ("the candidate set is a superset, not a narrowing to live seats"). — *falsifier_result:* GREEN real `2 passed`; MUT3 (`_attrib = target_attribution(_tgt_p) and {}` — keeps the call and the literal, discards the record): new test `2 failed`, committed 9 tests `9 passed` — blind. Staleness demo verbatim: "seats reported in flight: 5 … any field marking staleness: False". — *refutation:* a production `seat_done` caller (grep: none) or the demo reporting 2.

## R2 / R3 / R5 / V1

**R2** — *claim:* "Measured: 14 of 68 settings out of step, 20.5882%". — *verdict:* **PARTIAL.** The named script prints **30 of 140** today (glob consumes its own redesigned outputs), and even baseline-only re-derivation gives **16 of 70** because the exp56 convention gained `exhausted_round_threshold` after the measurement — 14/68 reproduces from nothing at HEAD. — *fix:* pin as a dated snapshot preserved in each config's `measured_gap` field, with re-measure instructions. — *falsifier_result:* RED `neither re-derives from its script nor is pinned as a snapshot` exit=1; GREEN patched exit=0. — *control:* weakening "SNAPSHOT" to "measurement" in the patched copy → exit=1. — *key rejection:* the verifier's plan item 1 ("re-running must print 14 of 68 again") is **falsified by execution** — its proposed test would be born RED.

**R3** — *claim:* silent arming impossible; "a config that arms the flag must explain why or the test refuses it". — *verdict:* **PARTIAL.** Default-False and no-config-arms verified by execution; but **0 of 47 configs carry the key at all**, so the guard's failing branch has never executed and has no positive control; coverage is 3 of 17 dirs. Mitigant: the 2026-08-30 AST predecessor test genuinely guards the named defect (`6 passed`). — *fix:* new test with positive controls (armed-no-note REFUSED; armed-with-note ACCEPTED) over ALL `bench/exp*_configs/*.json`, population floor ≥40. — *falsifier_result:* old evidence vs mutant tree with silently-armed exp53 config: `8 passed, 3 deselected` — blind; new test: `1 failed` on mutant, `5 passed` on real. — *control:* neutered rule (`if True:`) → the positive-control test reddens.

**R5** — *claim:* C0015/C0017 materiality ruling written back; RECOVERY.md no longer pending. — *verdict:* **PARTIAL — and the audit's lead limb is REFUTED by execution**: full revert (PENDING back, "RULED 2026-09-06" removed) turns the guard red, so it is not vacuous; the auditor's mutation was the state the annotate-don't-delete convention deliberately permits. The coverage limb stands: of the named places, `Operational_Plan.md:684/:752` are deliberate trail-blocks, but `Research_FULL_RECORD_2026-09-09.md:987/:1161` still read NEEDS FOUNDER post-ruling with no trail defence — the DONE prose narrows silently. — *fix:* disposition every named place explicitly in the entry (written-back / deliberately-left / remains-to-annotate). — *falsifier_result:* RED (both limbs, checked live against the repo) exit=1; GREEN patched exit=0. — *control:* dropping the residual sentence from the patch → exit=1.

**V1** — *claim:* DONE-evidence guard "fails if … green against a reverted fix. That last clause is the load-bearing one." — *verdict:* **PARTIAL.** The guard genuinely executes (350 parametrized passes over the live list) — but the self-declared load-bearing clause is implemented nowhere (grep: only the guard's own docstring conceding it and the test pinning the concession), and unlike V7's pass-check hole no successor tracks it. S_k side-check executed as instructed: `compute_sk` on a prose target → `tristate='NO_SCORE'`, `target_kind: 'prose'` (called, not grepped); 0/1035 Wilson [0.0000%, 0.3698%] verified both ways. — *fix:* Route B — carve the clause out of the headline as NOT delivered + add successor entry **V9** (per-item revert controls, with mandatory positive control so it cannot land as another guard-that-cannot-fail). — *falsifier_result:* RED `DONE while its self-declared load-bearing clause is neither implemented nor carved out` exit=1; GREEN patched exit=0. — *control:* patched copy with V9 removed → exit=1.

## A4 / A6 / L2 / V4 / V7

**A4** — *claim:* currency fail-safe warns and does not refuse; "a test asserts currency is not in the refusing CHECKS list". — *verdict:* **PARTIAL.** Behaviour correct; the non-refusal half of the evidence is a **tautology** (`… or True` at :95) plus a source slice; nothing asserts an exit code. Decisive control: a mutant validator that REFUSES on currency (rc 1) passes the entire declared evidence file `7 passed`. — *fix:* executing test asserting `"CURRENCY WARNING" in stderr` AND `returncode == 0`, plus executing `CHECKS` membership; delete the `or True`. — *falsifier_result:* RED vs refusing mutant `1 failed … returncode=1, stderr='… REFUSED …'`; GREEN default `2 passed in 0.19s`. — *note:* nothing here touches gamma or the two-sided gate; the standing gamma directive attaches to the instruments check, not to A4.

**A6** — *claim:* I11 (0/84) and I13 ("0 of 22 survived") measured; "both instruments refuse to run on a dirty tree". — *verdict:* **PARTIAL.** Census + I11 fine (bare run reproduces; worked-example and anti-vacuity controls). I13's invocation was never recorded — the script has no defaults, so the 22-caller denominator cannot be rebuilt: operator's report, not a measurement. The safety sentence is source-text-held: mutants with refusal disabled but all grepped strings kept pass every committed refusal assertion. — *fix:* executing refusal test (real temp git repo, dirty tree, rc 2 + byte-identical target) + I13 narrowing. — *falsifier_result:* RED vs disabled mutants `2 failed`; GREEN real `2 passed`; narrowing checker RED→GREEN. — *refutation:* a committed record fixing the `--module`/5-symbol set that reproduces 37/22.

**L2** — *claim:* quote-exemption: "8 false positives removed, 0 added" across 379 notes. — *verdict:* **PARTIAL — and the audit's "contradicted by its own committed script" limb is itself an instrument artifact**, proven by execution: the script's `(para, kind, text)` key reports paragraph *renumberings* as removed+added pairs (19/19 on the compendium); re-keyed on `(kind, text)`, today's corpus (412 notes, 987 findings) reproduces **8 removed, 0 added exactly**. The script exits 1 today against the entry's claim — the comparator, not the claim, is the defect. — *fix:* executing index-insensitive effect test + narrowing recording the re-keying and refreshed figures (0.81%, Wilson [0.41%, 1.59%]). — *falsifier_result:* RED mutant-1 (fix undone) `the fix removes no quotation false positive at all`; RED mutant-3 `4 findings ADDED`; GREEN real `1 passed in 1.55s`. — *control:* both mutants (each assertion arm shown able to fail).

**V4** — *claim:* figure-producer sweep over "18 entries", 0 orphans after repair. — *verdict:* **UPHELD (PARTIAL).** `Entry.text` is the heading line only — the guard sees 18 first-lines, blind to over half its stated population (block-level population **48**; both give 0 orphans at HEAD, so the conclusion survives, the instrument doesn't). Demonstrated: an unproduced 7-significant-figure p-value injected into an entry BLOCK passes the committed guard (`orphans=[] rc=0`). Also: 2 of the 6 evidence tests fail in any gitless checkout — the declared evidence cannot run green in the panel's own environment. — *fix:* block-level sweep + anti-truncation floor + population re-wording. — *falsifier_result:* RED new sweep on injected copy `figure with no live script in the BLOCK of: ['R1']`; GREEN real `2 passed`. — *control:* the old-guard green run on the same injected copy.

**V7** — *claim:* "2 of 52 DONE-evidence files run at commit time, 3.8462%". — *verdict:* **UPHELD** (re-confirmed by this seat: the named instrument prints **2/81 = 2.4691%**, Wilson [0.6797%, 8.5628%], "open for 79 of 81" today). The guard asserts only `>=40`/non-empty/strict-subset — structurally unable to notice the drift; and its "two tools agree" check compares the same formula with itself (both Clopper-Pearson; independent `math.comb` bisection confirms the value but proves non-independence). — *fix:* instrument-anchored narrowing ("the current figure is whatever the committed script prints, never this sentence"; the 2/52 pair retained as history — verifier traced it to mismatched revisions) + executing test of the entry's "It merges now" claim. — *falsifier_result:* RED `entry quotes 2 of 52; the committed instrument prints 2 of 81, and the figure carries no as-of date` → GREEN on narrowed copy; merge test RED on reverted mutant (`failing evidence was DELETED by the other`), GREEN real. — *control:* the declared evidence ran `6 passed` at the same moment its own docstring carried the false figure.

---

## Seat-level finding: the brief's own headline has the M1 defect

`measured-rate-travels-with-its-script` holds — `scripts/done_audit_overclaim_rate_2026-09-17.py` reproduces the brief's 30/85 exactly. But the **denominator mixes populations**: `n` counts *current* DONE markers (85) while `k` comes from the *audited* population. Executed: current DONE = 85; round-1 ∪ round-2 audited ∩ DONE = **84**; set difference = `{A11}` (evidence dated 2026-09-17 — DONE after the audit, never audited). "30 of 85 DONE entries claim more than their evidence shows" silently counts A11 as audited-and-clean. The defensible figure is **30 of 84 = 35.7143%, Wilson [26.2994%, 46.3787%]** (matching the audit README), or 30/85 with A11 disclosed as unaudited. This is the exact defect class M1 documents — a population counted against the wrong count — recurring inside the instrument built to prevent it.

*Falsifier (executed):* `/tmp/panel_seat_main/falsifier_denominator.py` — RED against the committed script: `AssertionError: FALSIFIED: denominator 85 exceeds audited population 84 and unaudited ids ['A11'] are not disclosed in the output`, exit=1. *Fix:* patched copy computes `audited_ids()` from both audit files, uses `n = len(audited)`, discloses the remainder; it prints `30 of 84 = 35.7143% / Wilson [26.2994%, 46.3787%] / … never audited (excluded): A11` and the falsifier returns `OK … exit=0`. *Control:* the RED run against the committed script. *Simplest sufficient:* one function + two line edits in the script; disclosure alone would also pass the falsifier by design (either cure is honest).

## What would refute this seat's answer

Per-entry conditions are stated above. Globally: any committed instrument that reproduces a figure this answer declares irreproducible (8/134, 14/68, 132/138, 2/52, 1,522, 18/9/50%, 0/24); any committed test that reddens under the mutations this answer declares the evidence blind to (P4 all-prose round, A20 single-line map deletion, 6.1 MUT1/MUT2, 6.6 MUT3, A4 refusing validator, A6 disabled refusal, R3 silent arming); or a record that A11 was in fact audited.

## Strongest disagreement with the brief

1. **The brief's own headline figure carries the defect class under review.** 30/85 conflates the audited population (84) with today's DONE count (85, including never-audited A11) — demonstrated RED→GREEN above. The brief that prosecutes typed-figure drift shipped one.
2. **"No test fails" is too kind.** Three named evidence files fail or skip in this panel's own staging (A26: 3 failed, gitless; V4: 2 failed, gitless; 2.2: 3 skipped, out-of-tree target), and several committed tests were proven *unable* to fail for their stated reason (P5 on an empty corpus, A4's `or True`, 6.1's literal-vs-literal, 8.3's tautological compare). A test that cannot fail is a defect in the evidence, not merely in the pointer.
3. **The audit is not privileged — confirmed in both directions.** Beyond the 5 phantom ids it already admits: R5's lead limb refuted by execution; L2's "contradicted by its own script" was an instrument artifact; 2.2's confirmed defects were already closed in the file this panel received; P3's round-1 reasoning was wrong on its own terms; the brief's 9.4 tasking described a different defect than the audit record holds. Conversely, verifier closing plans were stale twice over: R2's plan item 1 and P4's item 1 would each have been **born RED** if implemented as written. Plans, like figures, drift — only execution at HEAD decides.
4. **One above-threshold code finding travels with this close:** the `why_the_sweep_cannot_clear_a_critical` report block (`bench/reference_runner_v3.py:859-866`) states a mechanism the executed sweep contradicts (`_TERMINAL` at :6219 excludes CONFIRMED; an OPEN critical with a CONFIRMED falsifier IS cleared) — a founder ruling on item 28 would rest on a false blocker. Falsifier executed RED vs live module, GREEN vs corrected copy.

## Termination

Each worker ran 2 passes over its entries (pass 2 added confirmations only, nothing above threshold); this seat ran 2 passes over the compiled set — pass 2 independently re-executed the three highest-stakes producer claims (9.1 terminal set, V7 2/81, 3.3 15/6/40%) and all three reproduced; no continuation mechanism per the objective-and-diminishing-returns guard remains unexamined. **Converged.** All corrections are additive or narrowing; no feature is removed anywhere in this answer, gamma and the two-sided gate are untouched, and every proposed new test was executed and shown able to fail.

<!-- verbatim-end -->

Written under CDSFL note standard v1.7 (26 August 2026).
