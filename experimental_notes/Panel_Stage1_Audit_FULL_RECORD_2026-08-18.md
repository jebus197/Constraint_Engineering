# Panel Review — Stage 1 Audit and the Path to Bench Run 2

**18 August 2026, dispatched 14:37 BST.** Five models, no compelled convergence.
Brief: 46,459 characters carrying two primary-source packs (raw code with line
numbers, raw measurement tables) plus a quarantined ledger of CC1's claims.

**This file is the COMPLETE, VERBATIM record.** Every response appears exactly as
returned, unedited and untrimmed. Analysis and synthesis live in the companion
note; nothing here is summarised.

---

## Gemini 3.1 Pro Preview (`ge`) — OpenRouter

- returned: **yes**
- elapsed: 51.4s
- length: 8,274 characters

### Verbatim response

Here is the independent adjudication of the source pack, CC1’s claims, and the path to BR2. I have applied the "TOOLS DECIDE" standard: every conclusion below is traced directly to the provided code and measurements.

### Q1. ADJUDICATE THE DISPUTED PAIR
**Verdict: CLAIM-B is correct. CLAIM-A is false.**

**The Evidence:**
1. The convergence gate (`_check_gamma_alt_convergence`, Source A, line 4385) calls `_settled_novelty_series(registry, round_idx)`.
2. `_settled_novelty_series` (Source B, lines 4347-4348) explicitly skips any entry where `status` is in `_NON_NOVEL_TERMINAL_STATUSES`.
3. `_NON_NOVEL_TERMINAL_STATUSES` (Source C, line 4180) includes `"MERGED"` and `"DUPLICATE"`.
4. Measurement M1 proves this mathematically: the runner's own `_settled_novelty_series` reproduces the archived `gamma_critical_history` exactly in 9 of 11 runs. If the gate had been reading pre-deduplication data, this match would be impossible.

**Does item 1.1 remain worth having?**
Yes. Item 1.1 repairs `novelty_counts`. While the gate does not read `novelty_counts`, `_compute_rho` *does* (Source H, line 1666). Because `novelty_counts` previously only corrected the final round (Source D), `rho` was being calculated using inflated historical rounds. Measurement M2 shows `rho_avg` drops significantly when corrected (e.g., exp46 drops from 0.3009 to 0.2176). 

**Consequence if I am wrong:** If CLAIM-A is somehow right, it means Python's `in` operator is failing on line 4347, which is absurd. If I am wrong, I accept that all historical gamma convergence verdicts are invalid and must be thrown out.

### Q2. THE FOUNDER HAS RULED ON MERGED SEMANTICS. FALSIFY THE RULING.
The founder's ruling imports the Bugzilla paradigm wholesale. It breaks under scrutiny.

**(a) Where the Bugzilla analogy breaks:**
A software bug is an objective defect in a controlled artefact (e.g., a null pointer). A STEM claim is an epistemic argument about the world. 
*   **"Duplicate" means something different:** In software, 100 users reporting a crash means 100 people hit the exact same stack trace. In STEM, 100 models reporting the same flaw often means they share the same training-data bias or are echoing a common misconception. Corroboration in LLMs is frequently just mode collapse.
*   **"Simplest sufficient fix" fails translation:** In code, the simplest fix (e.g., `if x is None: return`) is usually correct because it minimizes regression risk. In STEM, the "simplest" fix to a complex biological or physical theory is often reductionist and scientifically invalid. Nature does not optimize for patch parsimony.

**(b) Accounting vs. Behavioural split:**
CC1 is wrong. Surfacing a dupe count is **behavioural**. If a model sees "This finding has 3 duplicates" in its prompt, its context window has changed. It will likely anchor on that finding, assuming it is highly probable because others found it. This changes the model's subsequent search behavior. It is not zero-dispatch accounting.

**(c) Is a dupe count worth building against a thin signal?**
No. M9 shows a maximum corroboration of 3 across all experiments. Building aggregation machinery for a signal this thin is a waste of time. The signal is thin because the immune pipeline suppresses it (see Q6).

**(d) Should "simplest sufficient fix" be formalised?**
If it is a "core guiding principle," it **must** be formalised mathematically (e.g., a parsimony penalty term in the objective function). Leaving it only in the text directives guarantees it will be ignored whenever the LLM's attention drifts. However, formalising it requires a computable metric for "simplicity" in STEM, which you do not currently have.

### Q3. THE TWO NEW FINDINGS
**1. The churn detector cannot fire (M2, G):** 
*Severity: CRITICAL BLOCKER.* `rho_earliest_round` is hardcoded to 12 (Source G, line 557). 5 of 6 recent experiments converged or stalled before round 12. A core convergence mechanism is structurally disabled for the current length of your runs. This must be lowered before BR2.

**2. exp47 report truncation (M3):**
*Severity: MODERATE.* The report says 9 rounds, the disk has 14. This indicates a desync between the runner's state and the checkpoint/reporting mechanism, likely caused by a crash/resume loop. It breaks analysis but doesn't invalidate the underlying math.

### Q4. THE MINIMUM REPAIR SET BEFORE BR2
The current plan has the wrong order. You cannot measure deduplication mechanics while the pipeline is actively destroying the duplicates.

**The Minimum Set (in order):**
1.  **CUT:** Do not build the Bugzilla dupe count or target aggregation. The signal doesn't exist yet.
2.  **CUT:** Defer exp52 (factorial cells). Do not run complex factorials on a broken harness.
3.  **ADD (Stage 1):** Fix `rho_earliest_round` (Item 1.8). Lower it to a sensible window (e.g., 5) so churn can actually be measured.
4.  **KEEP (Stage 1):** Merge all zero-cost accounting repairs (1.1 through 1.5) and run the offline replay to validate the math.
5.  **MOVE UP (Stage 2.1):** Fix the immune pipeline suppression (see Q6). This is the single biggest blocker to BR2.
6.  **LIVE RUN (Stage 3):** Run exp50 (physics) to prove the pipeline fix allows corroboration to form naturally.

**Consequence if I am wrong:** If we run BR2 without fixing the pipeline and churn detector, you will pay for a full-scale evaluation where models are silenced by the harness and convergence is triggered by artificial starvation rather than actual discovery exhaustion.

### Q5. THE PROCESS QUESTION
CC1's diagnosis is correct but its proposed remedy (just being more careful) is insufficient. Panel review is structurally unable to catch this because a panel reading a prose summary of code will inherit the summary's errors. 

**The Mechanical Process Change:**
Institute a **"Falsification Command" rule**. No universal claim ("the gate reads X", "nothing else modifies Y") may be committed to the tracker without the exact terminal command (e.g., `grep`, `rg`, or an AST script) used to verify it across the codebase. The panel's job is not to read the claim, but to execute the command against the source pack. If the command is missing, the claim is automatically rejected.

### Q6. THE IMMUNE PIPELINE IS REMOVING 97% OF EVERYTHING
**(a) Is the mechanism right?**
Yes. CC1's refutation (M7) proves the pipeline doesn't delete from the registry. Instead, it feeds `_build_feedback_for_next_round` (line 9150), which explicitly tells models in the next round: `triaged.is_duplicate`. 
**What CC1 missed:** This is a suppression loop. By telling models "you found a duplicate," the harness trains them to stop reporting it. Corroboration never forms because the harness actively discourages it at round $N+1$.

**(b) What should the discriminator do?**
Since similarity scores fail on hard cases (AUC ~0.608), auto-rejecting is fatal. You are throwing away valid findings based on a coin toss. 
**Recommendation:** Stop auto-rejecting. Let corroboration accumulate in the registry.

**(c) The SMALLEST change:**
Apply Occam's razor. Do not invent new LLM-as-a-judge routing. 
Go to `bench/dm/_feedback.py` (referenced in M7, lines 5757-5765) and **comment out the block that appends to `duplicate_pairs`**. 
If the models are never told a finding is a duplicate, they will not be suppressed. They will continue to report it, the registry will naturally accumulate `MERGED` pointers via `registry.resolve()`, and you will finally see if genuine corroboration exists. Cost: 1 line of code deleted.

### Q7. ANYTHING NOT COVERED
**The exp47 Anomaly (M1 vs M3):**
In M1, exp47's recomputed gamma differs from the archive (0.3601 vs 0.3668). CC1 attributes this to a `max_round` bound difference. But M3 shows exp47 has 14 rounds on disk and only 9 in the report. 
**The Risk:** The runner's checkpointing or state-resume logic is leaking or truncating data upon restart. If a run crashes at round 9 and resumes to 14, but the report generator only sees 9, your final convergence metrics are being calculated on truncated arrays. 
**Action:** Before BR2, you must audit the checkpoint resume logic (`bench/reference_runner_v2.py:8337`) to ensure `novelty_counts` and `raw_counts` are fully restored and not overwritten by a stale state.

---

## ChatGPT GPT-5.5 (`cgpt`) — OpenRouter

- returned: **yes**
- elapsed: 85.8s
- length: 13,171 characters

### Verbatim response

I did not have live file tools here, so this verdict is from the appended raw source pack only.

## 1. Disputed pair: CLAIM-B is supported; CLAIM-A is misattributed

The gate path in the source pack is clear:

- `_check_gamma_alt_convergence` calls:

```python
all_s, crit_s = _settled_novelty_series(registry, round_idx)
g_all = _estimate_gamma(all_s)
g_crit = _estimate_gamma(crit_s)
```

- `_settled_novelty_series` rebuilds from `registry.entries` on each call.
- It excludes:

```python
MERGED, DUPLICATE, UNCONFIRMED, REFUTED
```

before incrementing the series.

So the convergence gate does **not** read `novelty_counts`. It reads a live registry-derived settled series.

M1 supports that operationally: the runner’s own `_settled_novelty_series` reproduces archived `gamma_critical_history` in 9 of 11 rows, including exp44, exp45, exp46, exp48, exp49. The two mismatches are exp42 12-round and exp47, both already contaminated by archive/report-bound issues. They do not show that `novelty_counts` fed the gate.

Therefore:

- **CLAIM-B is right.**
- **CLAIM-A’s “gate-population mismatch” framing is wrong.**
- The “7 of 8 shift upward” result was not a gate result if it was computed on the all-findings / `novelty_counts` path.

Item 1.1 remains worth having, but it should be labelled as:

> retroactive correction of `novelty_counts` for rho and endocrine inputs, not gamma gate input.

Stage 1 material built on the same misattribution:

- Any claim that exp46’s convergence verdict was at risk because gamma moved under item 1.1.
- Any claim that archived convergence verdicts changed under item 1.1.
- Any claim that the gate previously counted later-merged duplicates through `novelty_counts`.

The exp46 narrow-margin claim itself stands: M1 gives exp46 `gamma_critical = 0.3357`, threshold stated as 0.30, margin ≈ 0.036, narrowest among exp44–49.

**If I am wrong:** the consequence is serious: BR2 should not run until a replay proves the exact historical gate input path for each archived run, because the convergence condition would have been instrumented differently from the spec.

---

## 2. MERGED / Bugzilla ruling: partly sound, but the analogy breaks at “repair”

### 2(a). Where the Bugzilla analogy breaks

The analogy is sound for one narrow idea:

> multiple reports can point to the same underlying issue, and the system should preserve those reports rather than erase them.

CDSFL already does that partly: M8 says the duplicate entry survives with `status` and `merged_into`.

But the analogy breaks in three places.

First, a software bug is usually a defect in an artefact the maintainer controls. A STEM claim may be wrong about the world. There may be no “fix” in the software sense; there may be correction, retraction, narrowed scope, new experiment, or unresolved anomaly.

Second, “duplicate” is less crisp. In Bugzilla, duplicate means two reports of the same software defect. In CDSFL it could mean:

- same textual criticism,
- same falsifier,
- same mathematical inconsistency,
- same location in artefact,
- same proposed repair,
- same empirical contradiction.

Those are not identical relations.

Third, “simplest sufficient fix” does not fully translate. It is useful as an engineering directive for editing artefacts, but dangerous as an epistemic rule. The simplest patch to a paper may hide that two distinct scientific failures were present.

So: preserve duplicate records and count corroboration, yes. Treat “resolved by simplest sufficient fix” as proof of identity or truth, no.

### 2(b). Accounting vs behavioural split

CC1’s split is mostly real.

A retroactive dupe count computed from stored `merged_into` pointers is accounting if it is only:

- in reports,
- in offline replay,
- in audit tables,
- not fed into prompts,
- not fed into severity,
- not fed into convergence.

But merely adding a count to a registry field could become behavioural if prompt construction serialises that field. The safe version is:

> compute dupe counts in a reporting/replay layer first, not in model-visible prompt state.

If later used in severity, model prompts, prioritisation, or convergence, it becomes behavioural and needs a live run.

### 2(c). Is the signal too thin?

For exp42–49, yes: M9 shows only 13 merge pointers across six experiments, max corroboration 3. That is too thin to drive severity or convergence.

But it is still worth building as cheap accounting, because across all archived registries there are 287 merge pointers. It may reveal whether the current pipeline suppressed corroboration.

It becomes informative if, after duplicate suppression is removed:

- independent models repeatedly land on the same canonical issue,
- dupe counts correlate with tool-confirmed defects,
- counts grow before convergence,
- counts distinguish high-salience defects from one-off noise.

Until then: report it, do not act on it.

### 2(d). Formalise “simplest sufficient fix”?

Not before BR2.

Keep it in directives for now. A formal parsimony term would need a measurable cost function. Otherwise it risks rewarding shallow patches over true diagnosis.

A later formal version could be a tie-breaker:

> among equally tool-valid repairs, prefer the smaller artefact change.

But not as a truth criterion.

**If I am wrong:** if dupe count is already model-visible through an untraced registry/report path, then adding it is behavioural and must be tested live before BR2.

---

## 3. Two new findings

### Churn detector

Real.

Source:

- `rho_earliest_round = 12`
- `_compute_rho` only sets churn when `round_number >= cfg.rho_earliest_round`
- M2 shows among exp44–49 only exp44 reaches round 12.

So for exp45, exp46, exp47, exp48, exp49 the churn detector structurally cannot fire.

Severity: **medium**.

It does not falsify archived convergence verdicts, because other gates can still converge. But it means rho/churn is mostly non-operative on the current arc.

Not a BR2 blocker if BR2 runs are expected to reach ≥12 rounds or if rho is explicitly treated as diagnostic-only. It is a blocker only if churn is supposed to protect against premature convergence in short runs.

### exp47 report truncation

Real.

M3 says:

- `converged_at = 13`
- `total_rounds = 14`
- `len(rounds) = 9`
- round indices start at 5
- raw response files r0–r13 exist.

Severity: **high for replay/accounting**, lower for live BR2.

It blocks using exp47’s archived report as a clean replay oracle. It does not prove exp47’s raw run is lost; raw per-round files exist.

Repair priority: above dupe-count niceties, below immune suppression.

**If I am wrong:** replay may waste effort fixing a report artefact that does not affect current runner behaviour. Cheapest check: reconstruct exp47 report from raw per-round files and compare registry round indices.

---

## 4. Minimum repair set before BR2

My recommended minimum path:

### Must land before paid BR2-scale runs

1. **Fix immune duplicate suppression.**  
   This is the main blocker. A system suppressing 97% of handled findings cannot measure discovery or corroboration.

2. **One live validation run after that fix.**  
   Replay cannot validate a prompt-behaviour change. Do not go straight to the full factorial.

3. **Fix/report exp47 archive truncation or exclude exp47 from replay metrics.**  
   The replay harness must not compare 9-round reports against 14-round raw/registry data.

4. **Complete replay for exp44–49 under old and repaired accounting.**  
   The exit test should be: reproduce old archived series first, then report deltas.

5. **Keep item 1.1, but relabel it rho/endocrine only.**

6. **Add dupe-count reporting as accounting only.**  
   Compute from `merged_into` pointers. Do not feed severity, prompts, or convergence before live validation.

7. **If Stage 2.2 is real, verify and fix it before BR2.**  
   The tracker claim that tool verdicts disappear through synthesis is serious, but in this brief it is tracker prose, not raw source. It needs one cheap source-level check. If confirmed, it is a blocker: the harness cannot record what tools showed.

### Cut or defer

- Cut any claim that gamma verdicts changed under item 1.1.
- Defer formal parsimony modelling.
- Defer dupe-count effects on severity/gate.
- Defer full exp44–49 live rerun.
- Defer exp49_dedup.
- Do not run exp51/52/54 until one post-suppression live run shows sane throughput.

I would reorder the current plan:

1. Finish cheap replay integrity fixes needed to trust measurements.
2. Immediately fix immune suppression.
3. Run one live shakedown.
4. Only then proceed to BR2 arc.

**If I am wrong:** if suppression is not actually caused by prompt feedback, then moving Stage 2 ahead wastes one live run. Cheapest pre-live check: inspect one post-April next-round prompt and verify whether NK duplicate verdicts are rendered as instructions that discourage re-reporting.

---

## 5. Process question

CC1’s diagnosis is necessary but not sufficient.

The pattern is not just “checked one member of a set.” The deeper failure is:

> universal claims were written before the cheapest falsifier was run.

Mechanical process change:

1. Every technical claim over a set must have a claim card:
   - exact claim,
   - quantified set,
   - source files/functions,
   - cheap falsifier command,
   - result,
   - counterexample search status.

2. No “gate reads X” claim without:
   - `rg X`,
   - call graph / AST reference check,
   - one archived replay comparison.

3. No “lossless” or “preserved” claim without:
   - source write-path audit,
   - read-path audit,
   - one measured cardinality check.

4. Label claims as:
   - HYPOTHESIS,
   - SOURCE-OBSERVED,
   - MEASURED,
   - REPLAY-VALIDATED.

5. Require each note to include:
   - “strongest falsifier I ran,”
   - “strongest falsifier I did not run.”

Panel review helps only if panellists inspect primary source or rerun commands. A panel briefed only with prose inherits the prose’s errors. For this failure mode, panel agreement is weak evidence.

**If I am wrong:** this adds process overhead. But the overhead is cheap compared with three days of correction commits and a possible wasted BR2 run.

---

## 6. Immune pipeline removing 97%

### 6(a). Is suppression the right mechanism?

M7 supports suppression, not deletion:

- registry write occurs at line 8899,
- immune pipeline runs later at line 9092,
- immune pipeline never writes registry,
- live consumer is next-round feedback,
- duplicate verdicts are rendered into the next prompt.

So CC1 correctly refuted “duplicates are destroyed before registry.”

What is still not fully proven from M7:

- that the prompt wording actually tells models to stop reporting,
- that models obey it,
- that the 97% internal removal rate maps directly to suppressed external corroboration.

But the mechanism is plausible and fits M9: only 13 merge pointers across exp42–49.

Cheapest check: print the actual next-round feedback block for a post-April run and compare re-reporting rates for findings labelled duplicate vs not labelled duplicate.

### 6(b). What should the duplicate discriminator do?

Do not retune thresholds. The AUCs are too weak:

- embedding 0.608,
- Jaccard 0.586,
- stem-signature 0.433.

The discriminator should stop being an auto-rejector.

Recommended behaviour:

- similarity may propose “candidate duplicate,”
- it must not suppress re-reporting,
- it must not assign final duplicate identity,
- identity should be decided by a stronger mechanism: tool verdict, counterfactual repair equivalence, explicit registry merge, or human/audit rule.

For live model prompts, use wording like:

> “Possible overlap with Cxxxx. If you believe your finding is independently supported, restate it with evidence. Do not omit it solely because of this flag.”

### 6(c). Smallest change

Smallest useful change:

> disable rendering NK-cell duplicate verdicts into the next-round prompt, or render them as non-suppressive advisory text.

Do not build a new discriminator first.

Keep:

- registration,
- pipeline logging,
- shadow analysis.

Remove only the behavioural suppression path.

This is Occam’s repair: stop the harmful action before inventing replacement machinery.

**If I am wrong:** if duplicate feedback is not suppressive, this will not restore throughput. Cheapest measurement before/after live run: count repeated canonical/location reports in the next two rounds with duplicate feedback off.

---

## 7. Additional risks / missed issues

Two risks not fully covered:

1. **M1 has archive identity ambiguity.**  
   exp42 appears multiple times, and 2 of 11 rows differ. Before final replay conclusions, each row needs a unique run ID and round-bound explanation.

2. **“No convergence verdict changed” is only about repairs already replayed.**  
   It does not imply verdicts will survive behavioural repairs. Once duplicate suppression changes prompts, archived convergence margins are not predictive.

Final recommendation:

> Do not spend BR2 money yet. Finish replay integrity, fix immune duplicate suppression, run one cheap live validation, then proceed only if throughput and reporting are sane.

---

## Codex GPT-5.5 (`cx`) — OpenRouter

- returned: **yes**
- elapsed: 91.7s
- length: 14,550 characters

### Verbatim response

## 1. Disputed pair: CLAIM-B is better supported.

The source pack supports **CLAIM-B**.

The convergence gate does **not** read `novelty_counts`. It reads:

```python
all_s, crit_s = _settled_novelty_series(registry, round_idx)
g_all = _estimate_gamma(all_s)
g_crit = _estimate_gamma(crit_s)
```

Source: A, lines 4385-4387.

`_settled_novelty_series()` rebuilds from the registry and excludes:

```python
MERGED, DUPLICATE, UNCONFIRMED, REFUTED
```

Source: B/C, lines 4347-4348 and 4179-4181.

So the gate path was already using a post-terminal-status series, not the stored `novelty_counts` list.

M1 mostly confirms this empirically: the runner’s own settled series reproduces the archived `gamma_critical_history` in 9 of 11 rows. The two exceptions, exp42 12-round and exp47, are anomalies, not evidence that the gate read `novelty_counts`.

### Does item 1.1 remain worth having?

Yes, but **not as a gamma-gate repair**.

It repairs `novelty_counts`, which is used by:

- `_compute_rho()` at F/H.
- endocrine module input at F line 9060.
- persisted checkpoint/report accounting.

But there is one important caveat CC1 underplays: source order shows `_compute_rho()` is called at line 8935, before the retroactive recompute at 9038-9043. If that order is still true in the full file, the repair may not affect the current round’s rho until later persistence/replay. That should be checked directly before claiming “rho is repaired” without qualification.

### What in Stage 1 was built on the same misattribution?

The following should be retracted or relabelled:

- “Gate-population mismatch” as a gamma-gate defect.
- “All 8 archived runs shift under the repair and 7 of 8 shift gamma upward.”
- The exp46 concern that gamma moved because of item 1.1.

Those were apparently computed from the all-findings or stored novelty series, not the gate’s settled critical series.

### Consequence if I am wrong

If the full source contains another gamma path that reads `novelty_counts`, then item 1.1 becomes a real gate repair and all archived convergence margins need replay under old/new accounting before any paid BR2 run.

---

## 2. Founder’s MERGED/Bugzilla ruling: where it breaks and where it holds

### 2(a). The Bugzilla analogy is useful, but not exact.

It holds for **record preservation**:

- A duplicate report should not vanish.
- It may contain independent evidence.
- It may affect priority/corroboration.

CDSFL already preserves the duplicate record: M8 says `registry.resolve()` writes status and `merged_into` to the duplicate, and 287/287 MERGED entries carry pointers.

Where the analogy breaks:

1. **Software bugs are defects in an artefact under maintainer control.**  
   STEM claims are claims about the world. There may be no “fix” in the software sense.

2. **“Duplicate” does not mean exactly the same thing.**  
   In Bugzilla, two reports may refer to the same implementation fault. In STEM, two findings may:
   - attack the same premise,
   - attack different premises with the same symptom,
   - share a repair but not an identity,
   - be independent corroborations of a real defect.

3. **“Resolved by simplest sufficient fix” imports a repair-centric frame.**  
   Some STEM defects are not fixed by editing a document. They may require:
   - rejecting a claim,
   - narrowing a domain,
   - adding uncertainty,
   - distinguishing hypotheses,
   - collecting evidence.

So: preserve Bugzilla’s duplicate accounting idea, but do not let the analogy imply that every STEM defect has a software-style patch resolution.

### 2(b). Accounting vs behavioural split is real, but fragile.

CC1’s split is mostly right:

- **Retroactively computing dupe counts from stored `merged_into` pointers** is accounting.
- Letting dupe count affect severity, prompts, dispatch, convergence, or prioritisation is behavioural.

But “surfacing” is ambiguous.

If the count is surfaced only in offline reports, replay tables, or archive summaries, it is accounting.

If the count appears in live prompts, dashboards used by humans during a run, triage queues, or model context, it can change behaviour. Then it is not zero-dispatch.

So the safe rule is:

> Dupe count may be computed and reported offline before BR2. It must not affect live prompts, severity, convergence, ordering, or model instructions until validated in a live run.

### 2(c). Is dupe count worth building with only 13 pointers across exp42-49?

Not as a BR2 blocker.

M9 says:

- 13 merge pointers across exp42-49.
- 11 canonical targets.
- maximum corroboration count 3.

That is a very thin live-arc signal. It is not enough to justify behavioural weighting.

It becomes informative if, after immune suppression is removed:

- duplicates/corroborations actually accumulate,
- counts correlate with tool-confirmed defects,
- high-dupe findings are more likely to survive reconciliation,
- indirect duplicate chains are common enough to matter.

Given that the code can compute it retroactively from stored pointers, I would build the offline count if cheap, but not delay BR2 for it.

### 2(d). Should “simplest sufficient fix” be formalised?

Not before BR2.

It belongs in directives for now.

Reason: a formal parsimony term can easily reward underspecified fixes. In STEM work, the simplest fix is not always the truest fix. Parsimony is useful as a tie-breaker, not as primary evidence.

I would formalise it later only if CDSFL is explicitly evaluating proposed repairs, and then only as something like:

> among tool-valid repairs that preserve empirical adequacy, prefer the least invasive change.

Not as a convergence term.

---

## 3. New findings: churn detector and exp47 truncation

### Churn detector claim: real.

Source G/H:

```python
rho_earliest_round = 12
churn = rho_avg < cfg.rho_threshold and round_number >= cfg.rho_earliest_round
```

M2 shows for exp44-49:

- exp44 reaches 13 rounds.
- exp45, exp46, exp47, exp48, exp49 do not reach round 12.

So the churn detector is structurally unable to fire in most of the current arc.

Severity: **medium**.

It is a monitoring/stopping-signal defect, not evidence that convergence verdicts changed.

### exp47 report truncation: real.

M3 shows:

- `converged_at = 13`
- `total_rounds = 14`
- `len(rounds) = 9`
- round indices only `[5..13]`
- gamma history length 9
- raw response files for r0-r13 exist.

That is a real archive/report integrity defect.

Severity: **medium-high for replay**, low-to-medium for live BR2.

It blocks using exp47 as clean replay evidence until reconstructed or excluded. It does not by itself block BR2 if the live runner now writes complete reports.

### BR2 blocker?

Neither is the main BR2 blocker.

The immune suppression problem is more serious.

But before BR2, I would require:

- exp47 either reconstructed from raw files or excluded from replay claims;
- churn detector described honestly as mostly inactive on short runs.

---

## 4. Minimum repair set before BR2

My recommended order:

### Must do before any expensive BR2-scale run

1. **Fix immune duplicate suppression.**  
   This is the largest live behavioural distortion. M6/M7 indicate the system has been suppressing about 97% of handled items for months.

2. **Validate the suppression fix with one live shakedown run, not the full factorial.**  
   Replay cannot validate prompt-behaviour changes.

3. **Run Stage 1 replay only far enough to prove the accounting harness can reproduce old archived outputs.**  
   Specifically:
   - reproduce old gamma/rho/novelty series where archive is complete;
   - exclude or reconstruct exp47;
   - label item 1.1 as rho/endocrine/accounting, not gamma-gate.

4. **Check the rho repair ordering.**  
   Source order suggests `_compute_rho()` may happen before the repaired recompute. If true, move the recompute before rho calculation or stop claiming live rho is repaired.

5. **Preserve tool verdicts through synthesis.**  
   If confirmed/rejected tool verdicts are being collapsed into DUPLICATE/UNCERTAIN, the harness still cannot record what the experiment showed.

### Should do if cheap, but not BR2 blockers

- Offline Bugzilla-style dupe count.
- MERGED target aggregation in reports.
- Churn-detector analysis/tuning.
- exp47 archive reconstruction.

### Cut or defer

I would cut/defer:

- Any behavioural use of dupe count.
- Any parsimony formalisation.
- Full exp44-49 live rerun.
- `exp49_dedup`.
- Stage 4 control-target work.
- Four-cell factorial until after one live shakedown proves throughput is restored.

### Revised plan

1. Minimal Stage 1 replay sanity.
2. Fix immune suppression.
3. Fix tool-verdict preservation.
4. One live shakedown run, probably exp50.
5. Only then proceed to exp51/52/54.

### Consequence if I am wrong

If immune suppression is not actually changing model behaviour, then reordering Stage 2 ahead of Stage 1 wastes one live run. The cheapest falsifier is to inspect the exact next-round prompt text and compare subsequent model behaviour after NK duplicate feedback appears.

---

## 5. Process question

CC1’s diagnosis is plausible but incomplete.

The pattern is not just “checked one member of a set.” It is:

> made a path claim without proving the call graph and consumers.

Examples:

- “the gate reads X” requires grep/call graph proof.
- “MERGED deletes information” requires checking both duplicate and target writes.
- “pipeline removes before registry” requires checking execution order.

### Mechanical process change

For every claim quantified over a set or path, require a small evidence block:

1. **Claim.**
2. **Exact command run.**
3. **Files/lines inspected.**
4. **Cardinality.**
5. **Negative grep/call graph result.**
6. **Cheapest falsifier.**

Example:

> Claim: gamma gate does not read `novelty_counts`.  
> Evidence: grep all references to `novelty_counts`; inspect `_check_gamma_alt_convergence`; inspect `_settled_novelty_series`; archived gamma reproduction table.  
> Falsifier: find any convergence path where `_estimate_gamma()` receives `novelty_counts`.

Panel review helps only if the panel gets primary sources or executable commands. A panel briefed only with prose inherits the prose’s errors.

So I would impose:

- no “path claim” without grep/call graph;
- no “all archived runs” claim without table + script;
- no “lossless/delete/fold” claim without inspecting writes to both source and target;
- every correction commit must include the failed command that would have caught the original error.

---

## 6. Immune pipeline removing 97%: how to fix it

### 6(a). Is the suppression mechanism right?

Mostly yes.

M7 says:

- Registry write happens first at line 8899.
- Immune pipeline runs later at line 9092.
- Immune result has two consumers:
  - next-round feedback, live;
  - shadow cells, zero verdict effect.
- It never writes to registry.
- It does not set MERGED, gate registration, or feed convergence.

So the mechanism is not deletion before registry. It is likely **prompt-mediated suppression**: models are told a finding duplicates another one and therefore stop re-reporting or stop developing it.

What CC1 has still missed: M7 does not prove the exact wording or strength of the prompt instruction. The next cheap check is to inspect `_build_feedback_for_next_round()` and the rendered prompt text. “Duplicate verdicts are rendered” may range from harmless advisory to effective rejection.

### 6(b). What should the duplicate discriminator do?

Given the measured AUCs:

- embedding AUC 0.608,
- Jaccard 0.586,
- stem-signature 0.433,

threshold tuning is not defensible.

The duplicate discriminator should not make final suppressive decisions from similarity.

Recommended behaviour:

1. Similarity may flag **possible overlap**.
2. It must not auto-reject.
3. It must not suppress re-reporting.
4. Final duplicate identity should be decided by a tool/counterfactual repair test where available, or by later reconciliation.
5. Corroboration should be allowed to accumulate.

### 6(c). Smallest useful change

The smallest change is:

> Stop rendering NK-cell duplicate verdicts into the next-round prompt as suppressive feedback.

Even smaller implementation options:

- disable that feedback block;
- or change it to non-suppressive wording:  
  “Possible overlap with X. Do not treat this as resolved. Re-report if independently supported.”

I prefer disabling the live prompt effect entirely for the shakedown. Keep logging the immune result for offline analysis.

This restores throughput without inventing new machinery.

### Consequence if I am wrong

If the prompt feedback is not suppressive, disabling it will not restore throughput. The cheapest falsifier is one controlled live or semi-live A/B: same target/config, duplicate feedback on vs off, compare number of re-reported/corroborated findings reaching registry over the first few rounds.

---

## 7. Anything not covered

Two additional risks:

### 7.1 Rho repair ordering may be wrong.

Source F shows:

- `_compute_rho()` at line 8935.
- novelty correction/recompute at lines 8985-9043.

If true in the full file, then rho is computed before the repaired series exists. That is a direct implementation-order risk.

Cheap check: move the recompute before `_compute_rho()` or add a test where a late MERGED entry changes rho in the same round.

### 7.2 M1 does not fully prove “every round” for all archived runs.

M1 proves strong agreement for most final archived histories. But exp42 12-round and exp47 differ. exp47 is already known incomplete. Those anomalies should be fenced off before broad archive claims.

---

## Final recommendation

Do not spend BR2-scale money yet.

Do this, in order:

1. Verify/fix rho repair ordering.
2. Reproduce old archive accounting by replay; exclude or reconstruct exp47.
3. Disable suppressive NK duplicate feedback.
4. Preserve tool verdicts through synthesis.
5. Run one live shakedown only.
6. If throughput and reporting are sane, proceed to the remaining BR2 arc.

The main blocker is not the gamma gate. It is the immune pipeline’s behavioural suppression and the harness’s ability to preserve what the run actually found.

## Strongest falsification of my answer

I did not read the full repository directly; I adjudicated from the appended source pack. My answer is falsified if the full source shows another active convergence path where `_estimate_gamma()` receives `novelty_counts`, or if the rendered NK duplicate feedback is demonstrably non-suppressive and models continue re-reporting despite it.

---

## DeepSeek V4 Pro (`ds`) — DeepSeek direct

- returned: **yes**
- elapsed: 348.6s
- length: 9,972 characters

### Verbatim response

Independent verdict: **CLAIM-B is correct on the gate path.** The strongest falsification of my own answer is the two M1 mismatches, exp42 12-round and exp47. They are attributed to max_round bound, not accounting, but I did not run the forced max_round rerun. If those mismatches persist after matching the bound, then part of CLAIM-A’s blast radius could still be live for those archived histories. The cheap test would be an AST/grep of every caller of `_estimate_gamma` and a rerun of `_settled_novelty_series` with `max_round` pinned to the archived `round_idx`.

---

### Q1. Adjudicate the disputed pair

**CLAIM-B is right.** The gate calls `_settled_novelty_series` directly at A:4385–4387. That function reads `registry.entries.values()`, filters `_NON_NOVEL_TERMINAL_STATUSES` on every call, and never touches `novelty_counts`. Source B/C show the exclusion is intrinsic. Source F shows no gate consumer of `novelty_counts`.

`novelty_counts` is the repaired variable at D/E. It feeds `_compute_rho` and the endocrine module, not the gate.

Item 1.1 remains worth keeping, but **relabelled as a rho/endocrine repair**. Its “82% of merges land in a later round” measurement is real, but it is not evidence about the gate.

Something still on the same misattribution? Yes, one thing: the replay exit test and runway should not claim gamma changes under item 1.1. If they do, they are still carrying the old framing. Also, I flag in Q7 that the repaired `novelty_counts` recompute at E filters only by status, not by location-key dedup.

If I am wrong, and the gate does read `novelty_counts` through some path not shown, then item 1.1 is a gate repair and all archived runs need retabulation. The cheapest measurement is the forced max_round rerun above.

---

### Q2. Falsify the founder’s MERGED ruling

**(a) The analogy breaks in three places.**

First, a software bug is a defect in an artefact under the maintainer’s control. A STEM claim is a proposition about the world. “Duplicate” in Bugzilla usually means same code location/same failure mode. In STEM, two textually similar claims can be different defects because their assumptions, scope, evidence, or target differ. Text similarity is already measured as near-chance on hard cases, so duplicate identity cannot be inherited from Bugzilla.

Second, Bugzilla duplicates carry independent user reports. CDSFL model reports may be correlated echoes from the same model or same prompt. A high dupe count would not necessarily mean independent corroboration.

Third, “resolved by simplest sufficient fix” assumes a maintainer who can patch the artefact. A wrong STEM claim is not repaired by a simple patch; false claims require new evidence. Importing “simplest sufficient fix” into the mathematical model would smuggle a repair-centric assumption into a falsification framework.

**(b) CC1’s accounting/behavioural split is real only if “surfacing” is precise.**

Retroactively computing a dupe count from stored pointers is accounting. Storing it in a report is accounting. Putting it into the next-round model prompt is behavioural. The current prompt already renders duplicate verdicts, so adding dupe counts there would be behavioural. CC1’s phrase “recording and surfacing” is too loose. The correction is: **record retroactively, but do not surface to models until a live run validates the effect.**

**(c) No, not worth building now.**

M9 shows 13 merge pointers across six experiments and max corroboration 3. That is too thin to inform priority or convergence. A dupe count becomes informative only after the immune pipeline stops suppressing re-reporting, after merge decisions use tool/evidence rather than near-chance similarity, and after experiments run long enough to produce multiple rounds.

**(d) “Simplest sufficient fix” should stay in directives, not the formal model.**

It is an engineering heuristic for repair. Formalising it as a parsimony term would change convergence verdicts based on an unvalidated prior. That is behavioural and needs live validation. Keep it as a directive for human/engineer repair; do not put it in gamma.

---

### Q3. The two new findings

Both are real.

**Churn detector claim is real.** G shows `rho_earliest_round = 12`. M2 shows only exp44 reaches R12 among exp44–49. For the others, rho churn cannot fire regardless of rho. Severity: moderate. It is not a BR2 blocker by itself because other convergence gates exist, but it means one intended signal is dead for short runs. The fix is config, not new machinery: lower or make `rho_earliest_round` adaptive.

**exp47 report truncation is real.** M3 shows a 14-round raw record, but the report’s per-round list and gamma history start at round 5. Raw files for all 14 rounds are present. Severity: high for archive integrity, low for runtime. This is a blocker for any per-round exp47 comparison and for replay validation if the report is used as source rather than raw files. It should be fixed before BR2 replay.

Rank: exp47 truncation is more severe because it corrupts direct interpretation; churn is a dead indicator but does not corrupt existing data.

---

### Q4. Minimum repair set before BR2

Land before spending on Stage 3:

1. **Purge the unrun answer-key blobs reachable from the remote branch** — see Q7.
2. **Fix exp47 report generation or rebuild the report from raw response files.** This is zero dispatch.
3. **Fix or explicitly disable `rho_earliest_round = 12` for short runs.** Otherwise churn is dead for planned runs.
4. **Do Stage 2.1 now: remove the immune pipeline’s live duplicate auto-reject/suppression.** This is the one behavioural repair most likely to restore useful throughput.
5. **Run one validation live run after Stage 2.1.** Do not run the full Stage 3 factorial or capstone until that validation run shows normal throughput.
6. **Defer MERGED semantics item 1.6.** The dupe count can be added later as a retrospective report field, not as a prompt/severity/gate behaviour.

Cut from the current plan:

- Cut Stage 3 until after the validation run.
- Cut Stage 2.2/2.3 as separate live runs; fold tool-verdict preservation into the validation run only if cheap.
- Cut Stage 4.3 load-balancer shakedown; it is expensive and not needed before BR2.
- Cut any plan that treats item 1.1 as fixing gamma.

---

### Q5. Process question

CC1’s diagnosis is necessary but not sufficient. The failure mode is asserting a universal claim after checking one member of the set. Panel review is structurally unable to catch this if the brief is prose, because the panel inherits the description’s scope error.

Concrete mechanical change:

- Any quantified claim of the form “X does/does not read Y” or “all Z” must include the exact command or script that enumerates the set, and the count of set members checked.
- For `all`/`none` claims, the commit message must include the negative search output, e.g. `rg -n "novelty_counts" bench/reference_runner_v2.py` and the caller list.
- Any claim without that artefact must be labelled `UNVERIFIED`, not `CLAIM`.
- Panel briefs should be generated from raw source/measurement packs, not narrative summaries. This brief already approaches that: source pack first, CC1 prose second.
- The cheapest refuting command should be run before the claim is made, not after. That is the actual discipline missing.

---

### Q6. Immune pipeline removing 97%

**(a) The suppression mechanism is broadly right, but CC1 still misses one thing.**

M7 shows registration happens before the pipeline, and the pipeline never writes to the registry. Therefore “removal” is not deletion. Its only live effect is next-round prompt injection. That is suppression of re-reporting.

What CC1 misses: because the pipeline does not write MERGED status, the first report of a “duplicate” may remain live in the registry. The 97% removal rate is not clearing the registry; it is censoring future prompts. This is still harmful to corroboration, but it is also possible that known duplicate findings remain counted in registry-based series unless another process marks them terminal. The mechanism needs to be verified by tracing every caller of `registry.resolve`, not just consumers of `immune_result`.

**(b) Given near-chance similarity, the duplicate discriminator should not be a similarity final decider.**

Best option: **stop auto-rejecting and let corroboration accumulate.** Routing to a tool is acceptable only where a cheap reliable tool exists; otherwise it adds new machinery. Flag-without-suppressing is second best, but even a soft duplicate flag may bias models.

**(c) Smallest change:**

Remove the NK-cell duplicate verdict injection from `_build_feedback_for_next_round`, or make it explicitly non-authoritative, e.g. “similarity noted” rather than “duplicate of”. That is a small code change, no new machinery, and directly restores throughput.

---

### Q7. Anything not covered

Three things.

1. **Remote answer-key leak risk.** The tracker says the remote branch was not deleted and that 17 answer-key blobs are reachable from it, including unrun exp50/51/52. That is a validity/security blocker. Delete or purge those blobs before any live run.

2. **The repaired `novelty_counts` recompute is still not location-deduplicated.** Source E lines 9038–9043 filter only by `open_since_round` and terminal status. `_settled_novelty_series` at B uses location keys to deduplicate. So the rho/endocrine repair may still overcount echoes that are not marked MERGED. The cheap check is to compare the repaired per-round `novelty_counts` against `_settled_all` in the archive.

3. **M1’s two mismatches are unexplained in the source pack.** They are attributed to max_round bound, but I would not accept that without the forced-bound rerun. If they are not bound artefacts, exp42 12-round and exp47 archived gamma histories may not be fully post-dedup, which would partially rehabilitate the old item 1.1 framing for those two runs.

---

## Claude Opus 4.7 (`cc2`) — Claude CLI, Max subscription

- returned: **yes**
- elapsed: 428.0s
- length: 26,033 characters
- note: retry at timeout=900s after three 300s timeouts

### Verbatim response

# INDEPENDENT PANEL VERDICT — 2026-08-18 14:58 BST, HEAD d922f68

**Headline: the source pack you were given is mislabelled in its two most load-bearing sections, and both CLAIM-A and CLAIM-B are wrong as stated. I also found the cause of the 97% removal rate. It is one line of arithmetic, and I reproduced it: 97.4% measured against your logged 97.1%.**

---

## Q1. ADJUDICATE THE DISPUTED PAIR

**Neither claim is correct. CLAIM-B is closer, and CC1's position 1 is right about gamma and wrong about the gate.**

### The pack's sections A and B are not what they say they are

Pack section A is captioned `_check_gamma_alt_convergence — the two-sided gate`, lines 4381–4396. That is **`_check_hardened_convergence`**. The real `_check_gamma_alt_convergence` starts at line **3856**.

Pack section B is captioned `_settled_novelty_series`, lines 4336–4361. That is the tail of **`_location_keyed_critical_series`**. The real `_settled_novelty_series` starts at line **4184**.

This matters because the function the pack shows you is **not running in this arc**:

```
bench/reference_runner_v2.py:506   hardened_gate_enabled: bool = False
exp44…exp49 configs:               "hardened_gate_enabled": false   (all six)
```

`_check_hardened_convergence` is the one that calls `_settled_novelty_series` directly (:4385). It is switched off. Every convergence in M4 came from `_check_gamma_alt_convergence`, dispatched at :9452.

### What the live gate actually reads

```python
9452:  _check_gamma_alt_convergence(
9453:      round_idx, gamma, novel_critical_history, cfg, ...
                          ^^^^^^^^^^^^^^^^^^^^^^ a STORED list
9459:      gamma_critical=gamma_critical,   # freshly computed at :9401
```

The two-sided gate has two sides and they have **different provenance**:

| Side | Source | Post-dedup in every round? |
|---|---|---|
| γ side: `gamma_critical >= 0.30` | `_estimate_gamma(_settled_crit)` at :9401, rebuilt from the registry each round | **Yes** |
| Count side: K zero-critical rounds | `novel_critical_history`, appended at :8916, only `[-1]` overwritten (:9345, :9372) | **No** |

So CLAIM-B is right about γ and **wrong** in its central sentence — "the gate never reads the repaired variable, it calls `_settled_novelty_series` directly." The gate reads a stored list with exactly the frozen-history defect CLAIM-A describes. CLAIM-B refuted CLAIM-A by pointing at the wrong function.

### The falsifier I ran

I recomputed the gate's count input against the settled registry and compared it to what was recorded:

```
exp44  recorded  [4,2,2,1,0,2,0,1,0,0,0,0,0]
       resettled [4,2,3,1,0,2,1,1,0,0,0,0,0]   DIFFERS at rounds 2, 6
exp45  SAME       exp46  SAME
exp47  recorded  [5,3,1,0,1,1,0,0,1,0,0,0,0,0]
       resettled [6,3,1,1,1,1,0,1,2,0,1,0,0,0]  DIFFERS at rounds 0,3,7,8,10
```

Staleness is real and present in 2 of the 4 runs I could recompute (exp48/49 have no extractable target symbols).

**CLAIM-A got the direction wrong.** It says removing duplicates shifts γ upward. The corrections here go **up, not down** — exp47 round 10 recorded 0, resettles to 1. Reason: `_location_keyed_critical_series` keys on code location and accumulates `seen`. Removing an earlier merged entry *frees its location*, so a later finding at that location becomes novel. Deduplication is not monotone on this series. Nobody has stated that.

**No archived verdict changes.** exp47's last-3 window is `[0,0,0]` recorded and resettled; it converged at 13 either way. exp44 converged via the state gate. So M4 stands — but for a reason neither claim gives.

### Is item 1.1 worth keeping?

Yes, and CC1's re-labelling to "ρ/endocrine repair" is correct as far as it goes. But **the repair is incomplete in a way the re-label conceals**: the retroactive loop at :9038 recomputes `novelty_counts` and does not touch `novel_critical_history`, which is the one input to the live gate carrying the same defect. Item 1.1 fixed the copy that does not gate and left the copy that does.

**One more thing built on the same misattribution.** The retroactive loop assumes list index == `open_since_round`:

```python
9038:  for _r in range(len(novelty_counts)):
9039:      novelty_counts[_r] = sum(1 for e in ... if e["open_since_round"] == _r ...)
```

`novelty_counts.clear()` is called on phase transition (:9803, :9838). After a clear, index 0 is global round N, not round 0, and the repair writes wrong values into every position. Harmless now — `burst_mode: "off"` in all of exp44–52 — but it is a live landmine if any BR2 config ever enables phases. Guard it or assert `burst_mode == "off"`.

**Consequence I accept if wrong:** if someone shows me `hardened_gate_enabled` was true in a run that converged, my Q1 collapses and CLAIM-B is simply right. I checked all six configs and the runner default; I did not check exp42/43.

---

## Q2. FALSIFY THE BUGZILLA RULING

I can falsify parts. The core survives.

**(a) Where the analogy breaks.** Two places, and one of them is serious.

*It survives* the "record persists" half. That is a records-management claim, indifferent to whether the artefact is code or a paper.

*It breaks* on "resolved." In Bugzilla, resolution is an act on an artefact the maintainer controls: the fix lands and the bug is closed by construction. A STEM claim can be wrong about the world, and "resolved" then means one of two very different things — the *text* was repaired, or the *claim* was shown false. Bugzilla has no state for "the reported behaviour is correct and the specification is wrong." CDSFL needs one. Your own runway names this exact hazard under "counterfactual repair is not ground truth": one repair curing two distinct defects. Bugzilla never had that problem because a patch that fixes two bugs *is* two fixed bugs.

*It breaks harder on "duplicate."* Two Bugzilla reports are duplicates iff they have the same root cause in one codebase — a fact about a shared, inspectable substrate. Two STEM findings can name the same passage and be **different errors in it**, which is precisely the KNOWN LIMITATION documented at :4331: "location-only keying cannot see a SECOND distinct defect in an already-flagged function." Bugzilla's dupe relation is an equivalence relation on causes. CDSFL's is a similarity judgement on prose. They are not the same relation, and importing Bugzilla's confidence in dupe-marking imports confidence CDSFL has not earned.

*"Simplest sufficient fix" does not survive intact.* In Bugzilla it is a *maintenance* virtue — minimise regression risk in code you own. In science, parsimony is an *epistemic* claim about explanations (Occam), and the two coincide only sometimes. A minimal textual patch to a paper can leave the underlying error in place. The directive is right; the Bugzilla provenance for it is not.

**What I would keep:** persistence of the duplicate record, the state machine, dupe counting. **What I would drop:** the assumption that a dupe mark is as reliable in CDSFL as in Bugzilla. It demonstrably is not — see Q6.

**(b) Is CC1's accounting/behavioural split real?** Real, and CC1 has under-claimed one leak and missed another.

*Computing* a dupe count from stored pointers is inert. *Surfacing* it is not, and there are two paths CC1 has not traced:

1. **The round prompt.** `_build_feedback_for_next_round` already renders `NEAR-DUPLICATE: cosine 0.xx to <id>` plus "(+ N other similar prior findings)" into the next round's prompt (`bench/dm/_feedback.py:468-476`). A corroboration count surfaced anywhere near that channel becomes model-visible, and the instruction attached to it is "either prove it is distinct **or withdraw**." That is behavioural, not accounting.
2. **The HIL channel.** A count shown to a human reviewer changes which findings get looked at, which changes escalation and `unverified_critical_count()`, which is a hard **blocker** in the gate (A4, :3925). Human-in-the-loop is part of the system.

The split holds only under a stated invariant: **the count is written to the report and nowhere the prompt builder or the HIL queue can reach.** Say that explicitly, and add a test that asserts the dupe count does not appear in any string returned by `_build_feedback_for_next_round`. Then it is genuinely zero-cost.

**(c) Is 13 pointers worth building against?** No — and it is the wrong question. Thirteen is not a measurement of corroboration; it is a measurement of the pipeline's suppression, for the reason Q6 establishes. Building a counter now would calibrate it against an artefact. **Build the counter, do not interpret it.** It costs an hour and it is the instrument you will need to read the fixed run. Interpreting it before Q6 lands would be reading a thermometer in a fire.

It becomes informative when a post-fix run yields corroboration counts with a spread — several entries at 2+, a tail at 1. If a post-fix run still returns max-count 1 across the board, the finding is that models do not independently rediscover, which is itself a publishable result about panel diversity.

**(d) Should parsimony be formalised?** **No. Keep it in the directives.**

Three reasons, and I hold this against my own instinct to formalise:

1. A parsimony term needs a complexity measure over proposed fixes. You do not have one, and any proxy you would reach for — diff size, token count, symbol count — is gameable by a model that has been *told* it is scored on it. You would be adding an objective the panel can hill-climb without improving anything.
2. It duplicates what γ already does. γ measures diminishing returns on discovery. A parsimony term measures economy of repair. Coupling them lets a run converge because fixes got shorter, which is not the property you want the gate to certify.
3. It is a *selection* rule between candidate fixes, not a *convergence* rule. It belongs where it is — in the directives, at the point of choosing.

**Consequence I accept if wrong:** if a post-fix run shows panels systematically preferring elaborate fixes over sufficient ones, and a HIL reviewer confirms it, formalisation earns its place. Measure it before building it.

---

## Q3. THE TWO NEW FINDINGS

**Churn detector: real, correctly diagnosed, and CC1 has under-rated it.**

Confirmed: `rho_earliest_round: int = 12` (:557), unset in all six configs, `round_number = len(raw_counts)` (:1676). exp44 alone (13 rounds) reaches it.

CC1 treats this as an accounting gap. It is not. `rho_churn` is passed into `_check_gamma_alt_convergence` as **blocking condition (d)**. A blocker that cannot fire is a **safety interlock that is disconnected in 5 of 6 runs**, and its failure direction is *permissive* — it makes convergence easier, never harder. That is the dangerous direction. **Severity: above every accounting item in Stage 1.**

**exp47 truncation: real, correctly observed, wrongly diagnosed, and lower severity than it looks — but its root cause is a BR2 blocker.**

I found the mechanism. exp47 has three response sets for round 5 (`round5_cc2` at 002732, 004717, 005214) — **the run was resumed at round 5**. The restore block at :8329–8371 restores `novelty_counts`, `raw_counts`, `novel_critical_history`, `gamma_history`, `gate_history`, `open_ch_history`, `stall_history`, per-model histories, ITC state and burst state. It does **not** restore `result["rounds"]`, `gamma_all_history`, or `gamma_critical_history`. Those three restart empty — hence 9 not 14. `location_crit_shadow_history` shows 14 because it is assigned the whole recomputed series at :9963, not accumulated.

No data is lost: `round_00.json`…`round_13.json` and the checkpoint's 14 `round_records` are all on disk. **The exp47 report is reconstructible offline at zero cost.**

But the underlying defect is: **any resumed run produces a report that silently under-states its own round count and γ history.** BR2 is your longest arc. It will resume. Fix the restore block, not the exp47 file. **This is a BR2 blocker; the exp47 artefact is not.**

**Ranking against the repairs already made:** resume-state loss > churn interlock > `novel_critical_history` staleness > items 1.2–1.5 > exp47 artefact.

---

## Q4. MINIMUM REPAIR SET BEFORE BR2

**Add these three. All zero-dispatch.**

- **A. The similarity map fix (Q6).** Highest value item on the page. One line, replay-validatable.
- **B. Restore-block completion.** Add `rounds`, `gamma_all_history`, `gamma_critical_history` to the checkpoint write and the restore read. One test: checkpoint at round 3, resume, assert `len(report["rounds"]) == total_rounds`.
- **C. Apply item 1.1's retroactive recompute to `novel_critical_history`**, and guard both loops against the `clear()` index shift. This is the gate's actual input.

**Cut these.**

- **1.7 replay of exp44–49, in its current form.** Its exit test — "reproduce the archived series exactly under the OLD accounting" — is unsatisfiable for exp47, whose report is structurally truncated by defect B. Land B first, rebuild exp47's report from `round_XX.json`, then replay. Otherwise you will spend a day debugging a replay harness that is correct.
- **1.6 as a build item.** Ship the dupe count as report-only accounting with the no-leak test from Q2(b). Do not decide MERGED semantics until a post-fix run gives you a real distribution.
- **Stage 3's four-cell factorial (3.3–3.6), for now.** Four cells at live cost to measure interaction effects on an instrument whose duplicate discriminator you are about to change. Run exp50 alone first.

**Ordering, and I disagree with CC1 here.** CC1 puts Stage 2 ahead of Stage 1. I would not reorder the stages — I would **move one item out of Stage 2 into Stage 1**, because the similarity fix is not behavioural in the sense the runway means. Changing the map changes which findings are *flagged*, and you can validate that against the 85 tool-decided labels and the archived findings entirely offline. Only the *live consequence* — do models stop withdrawing — needs a run. So:

1. **A + B + C** — zero dispatch, one to two days.
2. **Offline replay** of the similarity fix against the 85 labels and archived registries. Zero dispatch. This is your Stage-1 exit test and it is a real one.
3. **exp50 physics, one live run**, with A/B/C in place. This validates the behavioural half of Q6 *and* is a Stage 3 experiment. You get two things for one payment.
4. Read the dupe-count distribution from that run. **Then** decide MERGED semantics.
5. BR2.

The saving versus the current plan is one live dedup run (already deferred), the four factorial cells until later, and a day of replay-harness debugging.

---

## Q5. THE PROCESS QUESTION

**CC1's diagnosis is right about the shape and wrong about the sufficiency.** "Quantified over a set, checked one member" describes the errors. It does not describe *why* the one member got checked. In every case I traced, the checked member was the one **named in the prose CC1 was working from** — the runway tracker, the prior note, the commit message. The failure is not sampling. It is that **prose citations were treated as an index into the code.**

The proof is in this very brief. Its source pack contains two functions under two other functions' names. Nobody caught it in three days, because everyone downstream — including a five-model panel — read the caption.

**The mechanical change I would impose.** One rule, cheap, and it would have caught five of the six:

> **Any claim of the form "X reads Y" or "X calls Y" must be accompanied by the output of a grep for every call site of Y, pasted in full, in the same commit.** Not a line range. Not a quoted excerpt. The unfiltered call-site list.

Pack section F does this for `novelty_counts` and it is the only section of the pack that is fully correct. It is also the section that would have shown, had the same been done for `novel_critical_history`, that :8916 appends and only :9345/:9372 overwrite `[-1]` — the whole of Q1 in six lines of grep output.

Second rule, narrower: **a source pack must be generated by a script that extracts by symbol name, not by line range.** Line ranges rot on every edit. `inspect.getsource(fn)` cannot mislabel.

**Can panel review help here?** Mostly no, and the brief already says why — "a panel briefed with a description inherits the description's errors." I would put it more sharply: **on this failure mode a panel is worse than useless, because five models agreeing on an inherited error produces confidence, not correction.** That is vote-based confirmation, which is the thing CDSFL exists to reject.

It is rescuable, and cheaply. Panel review works here **only if the brief withholds the conclusion and supplies the tool.** Do not send "the gate reads the settled series — verify." Send "here is the repo, here is the run archive; determine what the gate reads." The first invites confirmation. The second forces execution. Your own founding principle — tools decide, not votes — applies to how you brief the panel, not just to what it reports.

---

## Q6. THE 97% REMOVAL RATE

### (a) The suppression mechanism is right. The cause is one line, and I found it.

M7 checks out: `registry.register` at :8899, `run_immune_pipeline` at :9092, two consumers, no registry write. Suppression, not deletion. Confirmed.

But CC1 stopped at the mechanism and never asked *why the discriminator says duplicate*. Here it is:

```python
bench/dm/_similarity.py:183     cos01 = (cos_sim + 1.0) / 2.0
bench/dm/_similarity.py:186     return (1 - BETA) * cos01 + BETA * b_class
bench/dm/_similarity.py:37-38   CLASS_BONUS = 0.3   BETA = 0.2
bench/immune_agents.py:3075     tau_sim: float = 0.50
```

`tau_sim = 0.50` was calibrated for the **Jaccard** backend, whose floor is 0. The embedding backend maps cosine from `[-1, 1]` to `[0, 1]`. Sentence-transformer cosines between arbitrary English **are never negative** — so half the output range is dead, and the *live* range starts at 0.4.

**The falsifier, executed on exp46's 27 archived findings, 351 pairs:**

```
raw cosine:            min=0.150  median=0.484  max=0.867     (never negative)

CURRENT (cos+1)/2, no class match   min 0.460  med 0.593   flagged duplicate:  97.4%
CURRENT,              class match   min 0.520  med 0.653   flagged duplicate: 100.0%
```

**97.4%.** Your logged four-month rate is **97.1%**. That is the mechanism, reproduced.

The floor at 0.460 sits 0.04 below the threshold. With a class match — `+0.06` — the *floor* is 0.520, **above** `tau_sim`. **Any two findings sharing a flaw class are duplicates by construction, regardless of what they say.** That is your regression of 12 April 2026: a backend substituted under a threshold calibrated for a different scale.

The `+0.418` figure in the `immune_agents.py` comment is this same floor on a different run. It was recorded and never traced to the affine map.

### (b) What the discriminator should do

First — **your AUC argument is being misapplied.** AUC is invariant under monotone transforms, so `(x+1)/2` does not change it: embedding AUC really is 0.608, and the map fix does not improve the *ranking*. But "retune the threshold is not available" does not follow. AUC 0.608 says the ranker is weak. The **operating point** is a separate quantity, and yours is pinned at ~100% positive rate — the single worst point on any ROC curve. Even a weak ranker at a sane operating point passes most findings. The brief conflates a bad ranker with an unusable one. Only the first is established.

Second — of your options, **stop auto-rejecting and let corroboration accumulate** is right, and it is right for a reason independent of the threshold: `_finding_similarity` is a *prose* judgement, and CDSFL's own principle says a finding is confirmed when a tool re-executes a falsifier. **A similarity score is a vote dressed as a measurement.** It should never be the final identity decider — which is exactly what your 85-label adjudication already concluded.

Target architecture, for later: similarity **proposes**, a tool **disposes**. Flag as candidate-duplicate, let both survive to the registry, and let the falsifier re-execution decide. That is your founding principle applied to dedup.

### (c) The smallest change

**Clamp the negative half.**

```python
cos01 = max(0.0, cos_sim)      # was: (cos_sim + 1.0) / 2.0
```

That is the whole fix. It restores a `[0, 1]` scale whose floor is 0 — the Jaccard scale `tau_sim = 0.50` was calibrated against — so the threshold means what it was set to mean. Measured on the same 351 pairs:

```
CLAMPED, no class match   min 0.120  med 0.387   flagged duplicate: 18.5%
CLAMPED,    class match   min 0.180  med 0.447   flagged duplicate: 35.3%
```

From 97.4% to 18.5%. No new machinery, no new constant, no retuning. It is a **bug fix**, not a recalibration — the old map was wasting half its range on a region the data never visits.

Validate offline before spending anything: recompute the duplicate decisions on the archived findings under both maps and score against your 85 tool-decided labels. Zero dispatch. If precision at the clamped operating point is no better than base rate, escalate to the flag-don't-suppress design — but measure first.

One free extra: the loop at :3100–3107 `break`s on the **first** match above threshold, not the best. So `duplicate_of` is an arbitrary above-threshold neighbour, not the nearest. Harmless at 97% flagging; visible once flagging drops to 18%. Remove the early exit when you land the clamp.

---

## Q7. NOT COVERED ELSEWHERE

Three things.

**1. Every convergence in exp44–49 was reached with the duplicate discriminator saturated.** This is the confound that dwarfs the rest. For four months, every model was told at the start of every round that essentially all its prior findings were near-duplicates and must be proven distinct **or withdrawn**. Your convergence data measures a panel under a standing instruction to stop reporting. The γ decay curves are real curves — of a suppressed process.

I am **not** saying γ is wrong. Your directive on that is sound and I have no evidence against the model. I am saying the *runs* are contaminated, and the contamination has a known start date and a one-line cause. **exp50 post-fix is not just the next experiment — it is your first uncontaminated measurement of the thing the project is about.** Treat it as such and instrument it accordingly.

**2. The gate's failure-swallow at :9382 is not equivalent in the two modes.** When `location_keyed_convergence` is on and the location computation throws, the handler logs loudly but the round's gate input **silently keeps the ID-proxy value** set three lines earlier. The log says "REVIEW THIS ROUND." Nothing enforces that anyone does. For BR2, that should raise a HIL flag in the report, not only a log line — a warning nobody is contractually required to read is the same failure shape as the Wolfram `[HTTP Error 401]` case already in your project directives.

**3. Two similarity backends, one threshold, silent selection.** `finding_similarity` picks the embedding backend if the model loads and Jaccard if it does not (`_similarity.py:163-166`) — no log line either way. The two have different score distributions and share one `tau_sim`. A BR2 run on a machine where sentence-transformers fails to load will produce quietly different dedup behaviour from one where it succeeds, and nothing in the report records which ran. Log the backend into the report. One line.

---

## RECOMMENDATION, IN ORDER

1. **Clamp the cosine map.** One line, `bench/dm/_similarity.py:183`. Then remove the early-exit `break` at `immune_agents.py:3106`. **Zero cost.**
2. **Replay the archive under the clamp** against the 85 tool-decided labels. This is the real Stage-1 exit test. **Zero cost.**
3. **Complete the checkpoint restore block** — `rounds`, `gamma_all_history`, `gamma_critical_history` — with a resume round-trip test. Rebuild exp47's report from `round_00…13.json`. **Zero cost.**
4. **Extend item 1.1's retroactive recompute to `novel_critical_history`**; guard both loops against the `clear()` index shift. **Zero cost.**
5. **Set `rho_earliest_round` per run**, e.g. `min(12, max_rounds // 2)`, so the churn interlock can fire. Re-derive the exp44–49 churn flags offline. **Zero cost.**
6. **Log the similarity backend** into the report; add the dupe count as report-only with a no-leak test. **Zero cost.**
7. **Run exp50 physics, once.** Read the corroboration distribution. **One live run.**
8. **Then** decide MERGED semantics, then the factorial, then BR2.

Everything before step 7 is free. If step 2 shows the clamp does not separate, you have spent nothing and you escalate to flag-don't-suppress with a real measurement behind it.

---

## STRONGEST FALSIFICATION OF MY OWN ANSWER

My Q6 result rests on 351 pairs from **one** run (exp46, 27 findings), all drawn from a **single target document**. Findings about one document share vocabulary, so my cosine distribution is biased *high* — which makes 97.4% an over-estimate of the true flagging rate, and my clamped 18.5% correspondingly optimistic. The coincidence with your logged 97.1% could be partly luck.

**The cheapest thing that would settle it:** rerun the same 20-line script across exp44, exp47, exp48 and exp49 registries and report the four flagging rates. If they cluster near 97%, the mechanism is confirmed on independent targets. If exp48/49 come in at 70%, the affine map is a contributor rather than the cause, and something else is also firing. Ten minutes, no dispatch. **Do this before step 1.**

Second, weaker: I claim no archived verdict changes under the `novel_critical_history` correction, but I could only recompute 4 of 6 runs — exp48 and exp49 have no extractable symbols for their targets. Both converged via the state gate per M4, so the count side was not decisive, but I have not verified that directly.

**What I did not check:** M6's monthly parse, M9's 13 pointers, the 85-label AUC figures, and exp42/43's gate configuration. I took all four as given.

---


*5 of 5 panellists returned a usable response (counted by ok=true AND non-empty text, not by file presence).*

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).