# Panel review — is the track record sound, or is the work to date unreliable?

**22 August 2026, dispatched 01:26 BST. Five models, no compelled convergence.**
Brief: 9,715 characters (`BRIEF.md` in this directory), carrying eleven raw
measurements taken from the archive the same night and both hypotheses stated
with equal weight.

**This file is the COMPLETE, VERBATIM record.** Every response appears exactly as
returned, unedited and untrimmed, including the parts that refute CC1. Analysis
and synthesis live in `Track_Record_Audit_2026-08-22.md`; nothing here is
summarised.

---

## Claude Opus 4.7 (`cc2`) — Claude CLI, Max subscription — the only panellist with file tools

- returned: **yes**
- elapsed: 422.5s
- length: 11,726 characters

### Verbatim response

## First: I broke read-only. Disclose before anything else.

I ran `scripts/null_perturbation_control.py --limit 12` to check the instrument works. It writes its output file unconditionally. It overwrote `experimental_notes/data/null_perturbation_control.json`, replacing the committed 397-row result from run `30a5c1c` with a 12-row one. Nothing else was touched.

Restore with:

```
git checkout -- experimental_notes/data/null_perturbation_control.json
```

I did not run that myself — you should see the damage and decide. The lesson generalises: that script is not safe to invoke read-only, and it should take `--dry-run` or write to a timestamped path.

---

## What I reproduced

M2: `replay_accounting.py --verify` → 8/8 MATCH, exactly as stated.
M3: 2,247 entries, 1,652 terminal, 474 carrying `falsifier_verdict` (454 terminal). Era split confirmed: modern 566 entries / 465 falsifier code / 454 tool-backed; pre-June 0.0%.
M5: contingency table reproduces **cell for cell**.
M7: four cases, exactly as listed.
M1: my regex is broader than yours (1.7 → 22.0%, 44/611) but the shape is identical and robust.

So the archive is honest about itself. That matters and it is not nothing.

## 1. Verdict: neither hypothesis. A **three-way split, and the fault line is the claim, not only the date**

**Tier 1 — before 3 June 2026 (16 runs, 1,464 entries, 0% tool-backed).** Not void. Not evidence for the founding principle either. These are multi-model panel results and should be labelled as such. That is a relabelling, not a retraction. H-BUILD is right about them as engineering; H-VOID is right about them *as citations for "tools decide"*.

**Tier 2 — code targets, exp42–47 (9 runs).** Tool-backed at high rate, replay-exact, and the falsifiers overwhelmingly import the real module. These stand as *a tool fired against the real artefact and the runner, not the panel, read the result*. They do **not** stand as *the tool discriminated the claim* — see §2.

**Tier 3 — exp48/exp49.** Exclude from headline claims. Three independent reasons: the documented answer-key contamination (your own errata: CC2 held the seeded set from round 1, "the retraction stands"); both target documents are **deleted** (`/Users/georgejackson/CDSFL_review_targets/exp48_chemistry.md` and `exp49_engineering.md` do not exist), so 68 falsifiers cannot be re-executed at all; and 14 of the 15 archive-wide self-certifying falsifiers live here. M3's 85.3% currently includes them.

The over-claim in the record is not "we found defects" — that is well supported. It is "our findings are tool-decided", which is supported for *the falsifier firing* and unsupported for *the falsifier firing because of the claim*, everywhere, including the modern arc.

**What changes my mind:** run the discrimination control against the 437 archived CONFIRMED falsifiers. ≥95% go quiet on a corrected copy → I move to H-BUILD for the modern arc without reservation. ≥10% still fire → I move materially toward H-VOID for the modern arc too.

## 2. Attack on M6

**(a) The p-value is not a test of anything.** `apply_falsifier_verdicts` (`reference_runner_v2.py:2936`) is called *after* `_update_finding_statuses` and unconditionally overwrites status from the tool verdict; the docstring says so in as many words. Given the gate on, "the tool prevails" is **deterministic**. A sign test against a vote-decided null tests a hypothesis the source code already assigns probability zero. 25/25, p = 2.98e-08 is arithmetic on a foregone conclusion. What M6 legitimately establishes is narrower and still worth having: *the gate was enabled and no bug bypassed it across 8 runs*. Given you found six model-vote paths to MERGED this week, that regression check is genuinely valuable. Report it as a regression check. Delete the p-value.

**(b) The real disagreement count is 1, not 26.** I decomposed your 26 (and reproduced it exactly — 16 + 7 + 1 + 1 + 1):

- **16** are tool `ERROR`/`UNTOOLABLE` — the tool *failed*, and the runner withheld. That is the assumption-free restatement and it is sound. It supports "model agreement is not **sufficient**."
- **7** are `MERGE`/`REOPEN`/`EXTEND` majorities against a CONFIRMED tool. MERGE means "duplicate of C00xx". That is a housekeeping vote, not a truth vote. Counting it as "the model wanted a different status" is your construction and it is not defensible. Drop these.
- **1** is a TIE.
- **1** — exactly one — is a model majority voting CONFIRM against a tool verdict of REFUTED: `exp42_composer_locationkey_live` C0028, severity 0.3, four votes.

So "the tool overrules the panel" rests on **n = 1**. "Votes are not sufficient" rests on 16 and holds.

**(c) The signals are near-constant, so agreement is uninformative.** Across the modern arc: 575 of 662 model votes are CONFIRM (87%); 437 of 474 tool verdicts are CONFIRMED (92%). Two signals that both say YES ~90% of the time will agree ~80% of the time by construction. Your low disagreement rate is not evidence of a well-behaved instrument.

**(d) The falsifier is not independent of the model.** It is authored by the same model that raised the finding. Independence lives in the *execution*, not the *design*. A model that misunderstands the target the same way twice gets CONFIRMED.

**(e) I probed the reader directly.** Good news first: the historical `NOT FALSIFIED` substring bug is genuinely fixed — `_read_verdict("NOT FALSIFIED: claim does not hold", "", 0)` → `REFUTED`. But:

```
reverify_falsifier("assert False, 'FALSIFIED: trivially'")            -> CONFIRMED
reverify_falsifier("assert 3*6+8*2 == 3*4+8*2, 'FALSIFIED: unbalanced'") -> CONFIRMED
reverify_falsifier("print('FALSIFIED')")                              -> CONFIRMED
```

The gate measures *fired*, not *fired because*. And **0 of 2,247 archived entries carry a `discrimination` record** — the control has never run, once, in the project's life. `discrimination_control_ask = False` at line 593, with the 2026-08-12 refutation recorded beside it.

**(f) 15 archived CONFIRMED falsifiers never touch the repo or target at all** — pure model-authored arithmetic, all 15 status CLOSED, 14 of them in exp48/49. `assert left_H == right_H` with the coefficients transcribed by hand. If the transcription is wrong, the confirmation is empty and nothing in the loop can see it.

**(g) Two small corrections to the brief.** M7's four cases all carry `escalated=True` — the two REFUTED-on-ERROR entries went to a human at the moment they were mislabelled, so "killing a finding on no evidence" overstates it (the status is still wrong). And M3's headline is internally inconsistent: 2,247 entries span **28** report files, not 27 runs — `exp36_evidence_latest` duplicates `exp36_evidence_20260407T004931Z`, 217 entries, identical. De-duplicated the total is 2,030 and the aggregate is 454/1,442 = **31.5%**, not 27.5%. The error runs against your own interest, which is the right direction for it to run, but the two figures in one measurement disagree.

## 3. M1: mostly artefact, and the proposed fix is not a better regex

Both confounds you name are real, and there is a third: the *subject* of the corrections changed, not just the volume. But the measurement that settles it is a re-indexing, not a re-count.

**Bucket corrections by the month the claim was ASSERTED, not the month it was withdrawn.** Rate-by-withdrawal-month rises mechanically whenever you audit — it is a property of the auditing, not the work. Rate-by-assertion-month asks the question you actually care about: *of the claims made in March, how many turned out wrong?* If March's cohort has a high eventual-correction rate and August's is low, the build was sloppy and the audit is working. If it inverts, recent work is genuinely worse.

Right-censoring is the catch — August's claims have had days to be caught, March's have had months. So pair it with survival: report each cohort's correction rate at 30 / 60 / 90 days, and compare August's 30-day figure against March's 30-day figure, not against March's lifetime figure.

This is computable from the archive today. Each of the 34–44 correction commits names what it corrected; `git log -S` on the retracted claim finds the assertion. Secondary normalisation: denominate by *claims made* (registry entries, note assertions), not commits — commit count is a measure of typing.

## 4. Single next step: **run the discrimination control on the 437 archived CONFIRMED falsifiers**

Why it dominates every alternative:

- **vs. wiring counterfactual repair to the merge site** — same mechanism, wrong target. MERGED is 13 entries in the modern arc. CONFIRMED/CLOSED is 436. That wiring protects the small case while the large case stays untested; and it falls out of the same code once the control exists.
- **vs. the typed transition log** — a log records *which mechanism decided*. If the mechanism does not discriminate, the log faithfully records a worthless decision. Logically posterior. Your `null_perturbation_control.py` docstring already makes this argument and it is correct. (The log is still worth building: no archived report records `falsifier_gate_enabled` — it is inferable from the presence of `falsifier_verdict`, but inferred, not recorded.)
- **vs. fixing M7** — 4 entries, all already escalated to a human. Real, small, not urgent.
- **vs. more live experiments** — adding runs on an uncalibrated instrument multiplies exposure. Do not.

**And the blocker is smaller than the record says.** "Nothing supplies a corrected copy" is true prospectively, false retrospectively. Two routes, both offline, both needing zero panel dispatch:

1. **313 of the 372 code-target CONFIRMED entries (84%) carry a non-empty `proposed_fix`.** Apply it to an overlay, re-run the falsifier, require silence.
2. Cheaper and assumption-free: **most of these defects were subsequently repaired in the repo.** Re-run each archived falsifier against the commit that fixed the defect it accuses. Still fires → it was never testing that claim. This uses only git history and the archive.

That is one measurement, running tonight, on the load-bearing claim. Everything else on your list is downstream of its answer.

## 5. Strongest falsification of my own answer

**M9 already argues against me, and I expect the control to come back mostly clean.** 397 falsifiers, 360 fired on the unmodified target, 0 flipped when an unaccused module-level function was renamed under them (304 eligible). That rules out a large family — falsifiers responding to *the file changing* rather than to the claim. My 15 detached falsifiers are 3.4% of 437 and concentrated in the two runs I am already excluding. If the discrimination control comes back ≥95% quiet, my position collapses to *"the label ran two months ahead of the evidence"* — which is much closer to H-BUILD than where I have landed. I am making a claim about what is currently **demonstrated**, not predicting that the instrument is broken.

**Second, against my own §2(a).** If the falsifier gate had bugs — and you found six model-vote paths to MERGED this week — then "the tool prevails" was *not* deterministic in practice, and 25/25 is a genuine measurement of bug-freedom on that path. That defence is fair. It just is not the defence the sign test implies, and it does not need one.

**Third, against the Tier-1 relabelling.** I have not shown that any pre-June conclusion is *wrong* — only that its own record cannot show what decided it. Unauditable is not false. If the pre-June findings were later independently re-derived (some of the code-target defects plainly were), the relabelling is bookkeeping, not a retraction. I would want that checked before anyone treats "Tier 1" as a warning label.

---

## DeepSeek V4 Pro (`ds`) — DeepSeek direct

- returned: **yes**
- elapsed: 163.8s
- length: 4,896 characters

### Verbatim response

**Assumption stated plainly:** I have not inspected the raw `*_report.json` files. My verdict assumes the M1–M9 summaries are accurate. To finalise I would need the raw records for exp46_stage6 C0014, exp48_chemistry C0037, the 78 modern terminal entries lacking a tool verdict, and a pre-June replay run.

## 1. Verdict

Neither H-BUILD nor H-VOID alone. The evidence supports a **dated split**, with named exceptions after the split.

- **Before 2026-06-03:** the record cannot show tool-decided outcomes, because the falsifier mechanism did not exist. These results are not automatically void, but they are **unaudited for the founding principle** and should not be cited as tool-decided. M2’s replay covers only exp42–49, so the pre-June runs also lack the archive-reproduction check.
- **From 2026-06-03 onward:** the record is largely self-consistent. M2 reproduces exactly; 85.3% of terminal entries are backed by a tool verdict; M5 shows status tracks tool verdict almost perfectly; M6 shows votes do not override tool verdicts when they conflict; M9’s null-perturbation control supports specificity.

But the modern arc is **not fully sound**. M7 shows two no-evidence REFUTEDs; 14.7% of modern terminal entries lack a recorded tool verdict; several repaired defects affected recorded components, and the truncation repair moved the convergence round in 2 of 6 runs, even if conservatively.

**What would change my mind:** a timestamped transition log showing statuses were assigned before or independently of tool verdicts; a material failure of the complementary discrimination control; or evidence that the 78 unbacked modern terminal entries were closed by model agreement.

## 2. Attack on M6

M6 is supportive but not load-bearing alone.

- **Selection bias.** It covers 227 of 474 tool-verdict entries. The other 247 are absent, and the 78 modern terminal entries with no tool verdict are excluded. The founding principle must hold across all terminal statuses, not only entries where a tool verdict happens to exist.
- **Causal order is unrecorded.** There are no timestamps showing votes preceded tool verdicts or statuses followed tool verdicts. If votes were cast after seeing the tool verdict, or if the falsifier author knew the votes, then “tool prevails” is observationally equivalent to “tool formalises the majority.” The low disagreement rate is exactly what contamination would produce.
- **Clustering.** 16 of 26 disagreements come from one run. The entry-level p-value treats those as independent. The run-level sign test is better but still n=8, and run exchangeability is assumed, not shown.
- **The p-value excludes the one “neither” case.** As reported it is 25/25. Including the ambiguous case as “not tool-prevails” gives 25/26, still significant but no longer the reported figure. The exp46 C0014 case is not benign: M7 says an ERROR falsifier wrote REFUTED with `verified=False`, killing a finding on no evidence. M6’s mapping calls that “more conservative”; M7 calls it a defect.
- **M6 tests status given a tool verdict.** It cannot detect the failure mode where no tool verdict exists and votes decide.

Bottom line: M6 shows statuses usually follow tool verdicts when a tool verdict exists. It does not, by itself, prove tools **caused** the statuses.

## 3. Rising correction rate

The rising rate is most plausibly an artefact of the shift from building to auditing, but M1 cannot distinguish that from worsening reliability.

Distinguishing measurement: for every correction commit, use `git blame` to find the birth commit of the corrected code, then compute **corrections per line of code by code age**. If the rise is from auditing old components, mean age-at-correction will be high and recent-code defect density will be flat or falling. If reliability is genuinely worsening, newly authored code will show rising defect density.

## 4. Single next step

**Run the complementary discrimination control: repair the accused claim and verify the falsifier goes quiet.**

This dominates the other candidates because it tests whether the modern falsifier verdicts are valid at all. M9 shows falsifiers do not flip on irrelevant perturbations, but it does not show they track the accused defect. A falsifier that always fires would produce the observed CONFIRMED/CLOSED pattern and pass M9. If the complementary control fails on a material fraction, M5/M6/M9 become hollow. The transition log is the close second: necessary for future audit, but it does not test existing verdicts.

## 5. Strongest falsification of my answer

A timestamped transition log showing that modern statuses were written before the recorded tool verdict, or that tool verdicts were retrofitted to match model votes, would collapse the dated split into H-VOID for the modern arc too. That would turn M5/M6 into a record-keeping pattern rather than evidence that tools decided.

---

## Gemini 3.1 Pro Preview (`ge`) — OpenRouter

- returned: **yes**
- elapsed: 25.1s
- length: 3,603 characters

### Verbatim response

**1. Verdict**
A specific split. 
*   **Pre-June 3, 2026 (exp34-41): H-VOID.** The archive contains 0% tool-backed verdicts. The founding principle ("tools decide") is entirely unauditable on the record. These results must be treated as unreliable.
*   **Post-June 3, 2026 (exp42+): Leans H-BUILD.** The mechanism exists, 85.3% of terminal entries are tool-backed, and M2 proves exact reproducibility. The defects found (M8) are severe but were caught by the audit, and re-derivation showed they did not alter the core convergence conclusions. 

**What would change my mind:** The un-run complementary control (repair the claim -> falsifier goes quiet). If that control fails, it means the falsifiers are hardcoded or structurally biased to fail regardless of the target's state. If the tools are invalid, the post-June 3 "tool-decided" archive collapses into H-VOID.

**2. Attack on M6 (The load-bearing measurement)**
Beyond CC1's objections, M6 has three critical flaws:
*   **Missing Denominator (Selection Bias):** M6 analyzes 227 entries that carry *both* a tool verdict and model votes. But M3 states there are 566 modern entries. What happened to the other 339? If tools only run when models agree, or if tool execution failures aren't logged in the denominator, the sample is heavily biased.
*   **Asymmetry of Override:** M6 proves the tool acts as a *veto* (model says CONFIRM, tool ERRORED -> status REFUTED). It does not prove the tool acts as a *champion*. To prove "tools decide, not votes," you must show cases where the model majority voted REFUTE, the tool voted CONFIRM, and the status became CONFIRMED. The brief provides no evidence this has ever happened.
*   **Tool Validity Assumption:** M6 assumes the tool's verdict is mathematically sound. If a falsifier is poorly written and simply asserts `True` or crashes, it will "prevail" over a dissenting model, but not because it successfully tested the artefact. 

**3. M1: Rising correction rate**
It is ambiguous. 10 corrections out of 41 commits in August is a high rate, but expected if the sole focus shifted to auditing. 
**Proposed measurement:** Measure the *age* of the code being corrected. I would need the `git blame` data for the lines changed in those 34 correction commits (a file I do not have). 
*   If August commits are fixing code written in March/April, it is an artefact of the audit phase cleaning up build residue. 
*   If August commits are fixing code written in July/August, the current engineering process is unstable, and the rising rate is a warning sign.

**4. Single next step**
**Run the complementary discrimination control** (repair the claim, the falsifier must go quiet).
*   **Why it dominates:** It tests the integrity of the decider. M9 proved falsifiers don't break when unrelated code changes. But if a falsifier fires on broken code, and *still fires* on repaired code, it is not a test; it is a broken script. If your falsifiers cannot recognize a repair, your 85.3% tool-backed modern archive is backed by noise. You cannot wire counterfactual repairs to the merge site or build transition logs until you prove the tools actually measure what they claim to measure.

**5. Strongest falsification of my own answer**
My "Leans H-BUILD" verdict for the post-June era relies on the 85.3% tool-backed rate being representative of the whole. If the missing 14.7% of unbacked modern entries contain the *critical, load-bearing findings* of those experiments, then the 85.3% is a vanity metric. If the most important conclusions bypassed the tool gate, my defense of the modern era is falsified.

---

## Codex GPT-5.5 (`cx`) — OpenRouter

- returned: **yes**
- elapsed: 28.5s
- length: 4,974 characters

### Verbatim response

## 1. Verdict

**Specific split.**

- **Before 2026-06-03:** the archive cannot show that results were tool-decided, because `falsifier_verdict` did not exist. Those results may be useful historically, but they are **not self-auditing under CDSFL’s founding rule**. I would not cite them as confirmed findings unless re-run or otherwise backed by external evidence.

- **From 2026-06-03 onward:** the record is much stronger. M2, M5, and especially M6 support that the modern harness usually follows “tools decide, not votes.” But it is not clean: **85.3% backed is not 100%**, CONFIRMED/MERGED are weakly backed compared with CLOSED, and M7 shows two modern terminal REFUTED outcomes from tool ERROR with `verified=False`.

So I would not say “the work to date is void.” I would say:

> **Pre-3-June results are unaudited legacy results. Modern results are mostly tool-backed but still need transition-level provenance before being treated as fully reliable.**

What would change my mind:

- Toward **H-BUILD/sound**: a typed transition log, or equivalent replay, showing every modern terminal status was caused by a valid tool/verification mechanism, plus repair-side controls passing.
- Toward **H-VOID**: evidence that many modern `falsifier_verdict` records are stale, misattached, non-independent, or not actually responsible for status transitions.

## 2. Attack on M6

M6 is useful, but it is not decisive.

Additional weaknesses:

1. **It proves correlation more than causation.**  
   Status tracks tool verdict, but without a transition log we do not know that the tool verdict caused the status.

2. **Possible shared-code circularity.**  
   If the same code writes `falsifier_verdict` and final status, agreement may only show that one mechanism copied from the other.

3. **Selection bias.**  
   M6 only covers entries with both tool verdicts and model votes. It says less about entries lacking one side, especially the poorly backed CONFIRMED/MERGED statuses.

4. **It does not validate the falsifiers themselves.**  
   Even if the harness obeyed tool verdicts, the falsifier could be brittle, target the wrong thing, or produce false positives. M9 helps on null perturbations, but the missing complementary repair control matters.

5. **Entry-level independence is weak.**  
   Findings in one run may share prompts, code paths, templates, parser bugs, or adjudication rules. The run-level sign test helps, but 8 runs is still small.

6. **“Tool prevails” depends on interpretation.**  
   Mapping votes and verdicts to intended outcomes is partly constructed. The assumption-free restatement helps, but only for one slice: model CONFIRM versus ERROR/UNTOOLABLE.

7. **It does not cover the legacy era.**  
   M6 supports the modern arc only. It cannot rehabilitate exp34–41.

8. **ERROR/UNTOOLABLE handling is partly broken.**  
   M7 shows terminal outcomes after non-running falsifiers. That is direct evidence that the gate is not airtight.

So M6 is **positive evidence for the modern principle operating**, but not enough to say the modern archive is fully reliable.

## 3. Rising correction rate: warning sign or audit artefact?

Both are plausible. The rate rising during an audit-heavy period is not automatically bad. If you look harder, you find more corrections.

A useful distinguishing measurement:

> For each month, classify commits by work type: feature/build, experiment/result, audit, repair, documentation. Then compute correction rate per prior-result-bearing commit, not per total commit.

Even better:

- count **corrections per audited artefact**;
- record **severity**: cosmetic, metadata, harness-affecting, result-changing;
- record whether each correction affects **already cited conclusions**.

If August has more corrections only because more audits occurred, that supports H-BUILD/audit artefact. If August has more **result-changing corrections per audited item**, that supports H-VOID.

## 4. Single next step

**Build a typed transition log recording the deciding mechanism for every status change.**

Why it dominates:

- It directly tests the core rule: tools decide, not votes.
- It would expose M7-style invalid terminal transitions.
- It would make M6 causal instead of merely correlational.
- It would separate valid closures, verified fixes, refutations, merges, withholds, and errors.
- It becomes the backbone for future audits and live experiments.

I would pause new live experiments until this exists. Otherwise new results may add volume without resolving the reliability question.

## 5. Strongest falsification of my answer

My verdict is wrong if a transition-level replay of the modern archive shows that many post-3-June terminal statuses were not caused by valid falsifier execution or independent verification, but by manual judgement, model agreement, stale verdicts, or broken ERROR handling.

That would move me from “modern mostly reliable but incomplete” toward **H-VOID for the modern arc too**.

---

## ChatGPT GPT-5.5 (`cgpt`) — OpenRouter

- returned: **yes**
- elapsed: 40.0s
- length: 5,692 characters

### Verbatim response

## 1. Verdict

**Specific split.**

- **Before 3 June 2026:** treat results as **not self-auditing as CDSFL results**. The archive cannot show that terminal decisions were tool-decided, because `falsifier_verdict` did not exist. They may still be true findings, but their own record does not prove the founding principle was followed.

- **From 3 June 2026 onward:** treat the record as **substantially more reliable, but not clean**. M3, M5, and especially M6 are positive evidence that the modern system usually followed “tools decide, not votes.” But M7 shows the gate was not perfect: two findings were REFUTED after tool ERROR with `verified=False`.

So I do **not** choose pure H-BUILD or pure H-VOID.

My verdict is:

> **The work to date is mixed. Pre-3-June results are not void as claims, but they are not proven tool-decided on their own record. Post-3-June results are mostly auditable and mostly tool-governed, with known exceptions that should be quarantined.**

What would change my mind:

- Toward **H-VOID**: if replay shows modern `falsifier_verdict` values were not produced by independent runner execution, or if counterfactual repair controls show many falsifiers still fire after the accused defect is repaired.
- Toward **H-BUILD**: if pre-3-June findings can be re-run now and independently acquire tool verdicts matching their archived conclusions, and if M7-type bad transitions are exhaustively found and rare.

---

## 2. Attack on M6

M6 is useful, but it proves less than it first appears.

Main weaknesses:

1. **It may prove governance, not truth.**  
   M6 shows status usually followed the tool over the vote. It does not prove the tool verdict was scientifically valid.

2. **Possible tautology.**  
   If the status-writing code simply maps `falsifier_verdict=CONFIRMED` to `CLOSED`, then M6 partly measures that mapping. That is still useful, but it is not independent evidence unless the transition path is audited.

3. **No typed transition log.**  
   We see final status and final tool verdict, but not necessarily the exact deciding event. Without a transition log, later edits, repairs, or overrides may be hidden.

4. **Selection bias.**  
   M6 only covers the 227 entries with both model votes and tool verdicts. It does not cover entries missing either side.

5. **Entry-level independence is weak.**  
   Findings can share code, run, prompt, model panel, artefact, or falsifier templates. The sign-test p-value is therefore overconfident.

6. **Temporal order matters.**  
   If model votes happened after seeing tool output, or if tool generation was influenced by model reasoning, “tool vs vote” is not a clean contest.

7. **Disagreement cases are few.**  
   26 disagreements is informative, but it is a small stress test of the principle.

8. **ERROR / UNTOOLABLE handling is different from CONFIRMED / REFUTED.**  
   “Model CONFIRM but tool ERROR, and status does not close” supports conservatism. But it is not the same as proving a falsifier decided the scientific claim.

9. **One bad case matters conceptually.**  
   M7 shows REFUTED could be written after ERROR. That directly violates the clean form of the rule.

My bottom line on M6:

> M6 is strong evidence that the modern pipeline usually did not let model votes overrule tools. It is not, by itself, proof that the tools were valid or that every terminal status was properly decided.

---

## 3. M1: warning sign or audit artefact?

The rising correction rate is a **warning sign**, but not decisive.

It is confounded by the work changing from building to auditing. A rising correction rate during an audit can mean the audit is working, not that the system is getting worse.

Measurement to distinguish:

> Do a cohort audit by creation date: randomly sample terminal findings from each month, apply the same current verification protocol to each sample, and measure the invalid/withdrawn fraction per audited finding.

Important controls:

- same audit depth per month,
- same definition of correction,
- count corrections per audited claim, not per commit,
- separate code defects from scientific-result defects,
- record whether each defect would have changed a terminal conclusion.

If old and new cohorts fail at similar rates, M1 was mostly audit exposure.  
If modern cohorts fail less, the build improved.  
If modern cohorts fail more, the rising correction rate is a real reliability warning.

---

## 4. Single next step

**Wire counterfactual repair to the merge site: no code path writes MERGED until the accused defect is repaired and the falsifier goes quiet.**

Why this dominates:

- M6 shows tools usually beat votes.
- M9 shows falsifiers are stable under irrelevant perturbations.
- But the missing test is the most important one: **does the falsifier stop firing when the accused defect is fixed?**

Without that, a falsifier may merely detect some correlated feature, not the actual claimed defect.

This step directly tests scientific discrimination, not just process compliance.

---

## 5. Strongest falsification of my answer

My answer would be falsified if a sampled modern audit shows:

- typed execution records exist or can be reconstructed,
- every terminal modern status traces to an independently re-executed falsifier or verified repair,
- counterfactual repairs make falsifiers go quiet at high rate,
- and the M7-type cases are the only bad transitions.

Then I would upgrade the post-3-June archive from “mostly reliable with exceptions” to “sound, with minor repaired defects.”

Conversely, if counterfactual repairs fail often, I would downgrade the modern archive sharply: M6 would then show only that the system obeyed bad tools.

---


*5 of 5 panellists returned a usable response, counted by ok=true
AND non-empty text, not by file presence.*

**Disclosure.** CC2 ran `scripts/null_perturbation_control.py --limit 12` during its
review, which writes its output unconditionally and overwrote the committed 397-row
result with a 12-row one. It disclosed this before anything else in its report and did
not restore the file itself, so the damage would be seen. The file was restored from
git the same night; the script needs a `--dry-run` and is listed as item 5 of the
next-step list.

Written under CDSFL note standard v1.4 (13 August 2026, Rule 24 added 16 August).