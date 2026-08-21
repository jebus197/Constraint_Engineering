# Geometry Dialogue — two rounds, verbatim, 22 August 2026

**Run as a conversation:** round 1 independent, round 2 with each reviewer shown the
other's full answer and asked to converge or dissent. Both on the Max subscription,
read-only, no metered cost. Neither modified any file.

---

# ROUND 1 — independent

## CC2 — Claude Opus, ROUND 1 — independent

- elapsed 464.1s, 10,330 chars

## What I ran

Everything below is from the repo, read-only, today.

---

## 1. The two-curve result is real. Its interpretation is not yet earned.

I reproduced it twice — once from the stored `gamma_*_history` arrays, once from scratch by re-deriving both series from raw registry entries and re-implementing `_estimate_gamma` (`bench/reference_runner_v2.py:1597`):

```
crit > all in 10/10 runs.  Wilcoxon p = 0.00195  (two-sided; CC1's "0.001" is the one-sided value)
REAL mean(gc - ga) = +0.127     NULL (200 random same-size subsets/run) = -0.003     p = 0.00195
```

And I pushed it harder than CC1 did. Restricting to findings the runner **independently re-executed and confirmed** (`falsifier_verdict == "CONFIRMED"`, 437/566), the gap survives: **+0.087, 9/11, p = 0.0039**. That is the version worth quoting, because it kills the "unverified junk dilutes the all-series" objection.

**But the partition variable is model-supplied.** `severity` is a raw float from the model, `bench/cdsfl_finding_schema.json:23` — *"Severity score 0.0–1.0"*, no calibration, no tool derivation. `CRITICAL_SEVERITY_THRESHOLD = 0.7` cuts a model self-assessment. And that self-assessment is itself round-dependent:

```
Spearman(severity, open_since_round) = -0.367,  p = 1.7e-19,  n = 566
```

Models file their biggest claims first and de-escalate as the round counter climbs. That single number generates the entire two-curve gap, and it has two readings the archive cannot separate: *hard constraints deplete first* (Gemini's) and *reporters anchor high then wind down* (behavioural). Random subsampling does not distinguish them, because subsampling preserves the severity–round coupling it should be breaking.

**Then there is the contamination, which is the part I would not publish around.** Your own last commit (`ca14294`) says it: *"every convergence in exp44-49 was reached while models were told each round to withdraw prior findings. Those curves are curves of a suppressed process."* The gamma result was measured on exactly those runs. I traced the mechanism. `_feedback.py:172` scores near-duplicate at `2.0 × similarity`; the comment at `:176` records *"the similarity function flagging 97% of pairs, every finding carried a duplicate flag worth >= 1.4"*. Payload is top-10 per model per round (`model_recs.sort(key=priority_score)`, `:390`). And the tie-breaker inside that saturated band is `score += 0.1 * severity` (`:187`).

So: when every finding sits at ~1.4–2.0 from a broken duplicate detector, the differentiator deciding who gets pushed into the withdraw-list is **severity**. High-severity findings were preferentially selected for correction feedback, every round, for four months. That is a harness-internal route to "criticals deplete faster" that has nothing to do with the shape of any problem space.

I could not rule it out, because the feedback payload is not archived — no `feedback`/`priority`/`duplicate` key exists in any report JSON. It needs a replay under the clamped similarity function.

**Verdict on Q1:** the measurement is sound arithmetic on unsound inputs. "CDSFL measures the external geometry of a problem space" is not supported by it. What *is* supported is narrower and still interesting: *model-assigned severity decays with round index, and the decay is steeper for high-severity claims, on archives where the harness was itself preferentially suppressing high-severity claims.* Re-run it on one clean post-clamp run before it goes anywhere near a paper.

---

## 2. Naming: "geometry" is borrowed. "Depletion" is yours.

Gemini's defence is technically admissible and practically wrong for you. Information geometry is a real field, but it studies Riemannian structure on statistical manifolds — a metric, a connection, curvature. `_estimate_gamma` is an OLS slope of `log(cumulative findings)` against `log(round)`. That is Duane / Crow-AMSAA reliability growth, a 1962 result from aircraft engine testing. There is no manifold, no metric tensor, no curvature. Calling it geometry imports a vocabulary whose actual objects you do not have, and the first reviewer who knows information geometry will ask where the Fisher metric is.

Your instinct is right, and there is a better word sitting in your own code: **depletion**. `GAMMA_BANDS` already says *"Strong depletion"*, *"Moderate depletion"*, *"Weak depletion"* (`:1630`). You named it correctly years ago and are now being talked out of it.

If you want the field-anchored term that is *actually* true, it is **reliability growth**, and the honest sentence is: *CDSFL applies reliability-growth modelling to multi-agent review, treating findings as failures and rounds as test time.* That is Duane's own frame, it is standard, it is checkable, and nobody will accuse you of a buzzword. "Geometry" makes it sound like more; "reliability growth" makes it sound like something, which is better.

One thing Gemini got right that is worth keeping regardless of the noun: the distinction between measuring a model's internals and measuring its behaviour. Say that plainly. You do not need "geometry" to say it.

---

## 3. The two perturbations are one mechanism, and your instinct beats CC1's.

CC1 split them on access — latent needs weights, black-box does not. That is a split about *where you stand*, not about *what the operation is*. Both are: change one thing, hold the rest, see what moves. Both measure a **dependency footprint**. The difference is only what you are allowed to vary.

Your own 21 August review already reached this and said it better than either of us — `experimental_notes/Design_Reviews_Bugzilla_And_Perturbation_2026-08-21.md:501`: *"Perturbation response maps a finding's support — what it depends on."* And it names the limit honestly at `:497`: *"say for sure when models truly are computing is not achievable by this or any output-side instrument."*

So: **one mechanism, two scales, not mutually exclusive** — you are right. But the scales are not interchangeable, and the reason is measured in your own file: 89.5% of archived falsifiers (153/171) `import` the target rather than reading it as text (`:404`), so they respond to a perturbation *anywhere* in the file while depending on nothing in particular. At the input scale the mechanism is nearly free; at the target scale your instrument currently has a blunt tip. The null-perturbation control proposed at `:410` is the fix and I would build it before anything in this conversation.

---

## 4. `d_i` is not a landing site. CC1 pattern-matched, and the truth is worse.

I traced it. In the only path where R_k is actually computed:

```python
# reference_runner_v2.py:7799
R_new = compute_rk_with_eta_channel(
    R_old=R_old, sk=sk_result.sk,
    eta_int=q, m_div=1.0,
    c_ext=c_ext, nu_k=_nu_k,
    d=1.0, p=1.0,          # <-- hardcoded
    ...)
```

`d` is pinned to 1.0. `p` is pinned to 1.0. Line 7523 — CC1's cited "populate site" — is inside `_validate_rk_computation`, whose own docstring says **"Advisory only — logs discrepancies, never rejects findings"** (`:7477`). It parses `d` out of model prose to print a PASS/WARN/FAIL line. It moves nothing.

And the thing `d_i` is supposed to be a factor *of* is worse still. `q = meta.get("q", 0.5)` (`:7734`), where `meta = entry.get("model_params", {})` — and the runner's own comment three lines down says model_params *"is never populated"*. I checked: `"q":` appears in **zero** archived report JSONs, across 1750 recorded R_k updates. Every one used q = 0.5.

So the situation is not "d_i is a self-assessed point estimate that should be empirical." It is: **the entire detection-probability decomposition η·d·p has never executed. R_k has run 1750 times on a constant.** A perturbation-response rate would not replace `d_i` — there is no `d_i` to replace. It would have to instantiate the channel for the first time, which means also supplying η and p, and deciding what happens to four months of archived R_k values computed at q = 0.5.

That is a much bigger and much more honest piece of work than "swap in a better estimate", and worth doing — `MATHEMATICAL_APPENDIX.md:354` already specifies exactly the admissibility rule it would satisfy (*"d must come from actual tool execution... not from the model's self-assessed confidence"*). But call it what it is: wiring a dead channel, not tuning a live one.

---

## 5. Evolutionary driver: not a sentence in a paper. Not yet a research direction either.

Same commit, CC2's finding: *"Over 1000 of ~1200 CONFIRMED entries carry no field identifying what decided them, and every MERGED entry's justification was overwritten at write time. The archive cannot answer whether any archived CONFIRMED was tool- or vote-established."*

A training corpus whose labels cannot be traced to what produced them is not a training corpus. Under your own founding principle — tools decide, not votes — an unauditable CONFIRMED is indistinguishable from a vote. Training on it would propagate exactly the failure mode the project exists to eliminate, at scale, into weights, where you cannot audit it afterwards.

The prerequisite is already identified and is the right one: the typed transition log (`{to, from, round, mechanism, actor, evidence_ref}`) plus the test forbidding `MODEL_ATTESTATION` from writing CONFIRMED. Build that, run clean post-clamp experiments, and *then* the ledger is a candidate corpus and the claim becomes testable. Until then it is a claim about a dataset that does not exist.

**Nothing in the paper.** Not because it is wrong — because you cannot presently demonstrate that a single row of your ledger is what it says it is, and Gemini's framing invites a reviewer to ask precisely that.

---

## Where I expect to argue in round 2

I will move on naming if someone shows me a metric, a connection, or a curvature in this codebase — I looked and found an OLS slope. I will move on the gamma interpretation if a replay under the clamped similarity function reproduces the gap with the top-10 feedback ordering recorded, so the severity tie-breaker confound can be measured rather than speculated about. That replay is the test, and it is cheap: the code is there, the archives are there, and it needs no new experiment.

I will not move on `d_i` unless someone shows me a call site where `d` is not 1.0.

---

## Fable 5, ROUND 1 — independent

- elapsed 226.1s, 6,978 chars

Findings, round 1. Timestamp 2026-08-22T00:22:36+01:00. Everything below was re-run by me from the archive, not accepted from the brief. (One aside: it's past midnight and the brief says you're unwell — this round will keep until morning.)

## What I verified before arguing

- **Reproduced CC1's headline from the raw reports.** 11 reports carry both histories; `exp42_composer_confirm` is all-zero (aborted at round 2) and is the legitimate exclusion. Across the remaining 10: γ_critical > γ_all in **10 of 10**, mean difference **+0.139** on final values, Wilcoxon two-sided **p = 0.002** (CC1's 0.001 was presumably one-sided; same evidence).
- **Rebuilt the null-subset control independently** from each report's registry (`open_since_round` × severity ≥ 0.7, the runner's `CRITICAL_SEVERITY_THRESHOLD` at `reference_runner_v2.py:4181`): real mean **+0.14**, null mean **−0.002** over 200 random same-size subsets per run, Wilcoxon real-vs-null **p = 0.002**. CC1's numbers (+0.115 / −0.004 / 0.005) reproduce within reconstruction noise.
- **Ran a control CC1 did not run.** The null-subset test kills sparsity but not severity-labelling drift — models might simply label late findings lower, regardless of ground truth. Restricting to tool-settled findings only (CONFIRMED/CLOSED): **9 of 10 positive, mean +0.115, p = 0.0098**. The effect survives. The one flip (exp46, −0.040) has n_crit = 12.

## 1. Is the two-curve result what Gemini says it is?

The measurement is real and now triple-controlled. What it demonstrates is: **hard-constraint findings deplete faster than soft ones, and the difference is attributable to severity, not sparsity and not labelling drift.** That is a genuine, publishable regularity.

"CDSFL measures the external geometry of a problem space" is a metaphor stretched over that regularity. The data are *consistent* with Gemini's gravity-well picture but do not require it. The distinction matters because "geometry" implies measured structure — distances, neighbourhoods, curvature. CDSFL measures none of those. `_estimate_gamma` (`reference_runner_v2.py:1597`) fits one log-log slope per series. Two slopes are not a geometry; they are two rates. Present the finding as the finding: severity predicts depletion rate. It does not need the borrowed word to be interesting.

Caveat that must travel with the number: n = 10, and the runs are not independent (three exp42 runs share one target; exp48/49 are the exam pair). Direction is uniform, which is why I still credit it.

## 2. Naming

"Geometry" is not load-bearing. Drop it. The accurate lineage is already in the code: line 8918 prints "γ (Duane reliability growth)". This mathematics has a 60-year-old name — **reliability-growth modelling** (Duane, Crow-AMSAA) — and CDSFL's honest one-line description is:

*"CDSFL measures the depletion kinetics of a problem space — the rate at which hard and soft constraints exhaust under adversarial review — using reliability-growth mathematics."*

Every word in that is checkable against the repo. "Information geometry" specifically would be a false claim of kinship: that field is Fisher metrics on statistical manifolds, and CDSFL computes no metric tensor and no manifold. If a spatial word is wanted, Gemini's own "**trajectory**" is defensible — a gamma history is genuinely a 1-D path through time — where "geometry" is not. Your buzzword instinct is correct; trust it. One concession I'll hold open for round 2: the location-key/similarity machinery *is* a metric-like structure over findings — but it is used for dedup, not measurement, and hanging "geometry" on it would still be dressing.

## 3. Are the two perturbation senses separable?

You are both right, about different things. They are **one logical mechanism — differential testing: apply a controlled delta, demand the covariance genuine dependence predicts — instantiated on two different black boxes.** Perturbing a target probes a *falsifier's* dependence (the never-run discrimination control, `reference_runner_v2.py:2117–2165`). Perturbing an input probes a *model's* computation (Julian's paradigm). Same form; different object, cost, and failure mode: the falsifier version is deterministic, local and free, and its recorded defeat is the access-versus-dependence hole (`:2972`); the model version is stochastic and metered, and its defeat is robust memorisation of the variant family. So the founder's instinct (not mutually exclusive) and CC1's claim (separable) don't conflict: shared logical form, separate implementations. The practical payoff of seeing the unity is that each one's defeat analysis transfers — a falsifier that opens the target and discards the contents is the exact analogue of a model that memorised the neighbourhood of the question.

## 4. `d_i` — real landing site?

I checked what CC1 said it hadn't. **Today, `d` moves nothing that decides anything.** The extraction at `:7523` lives inside `_validate_rk_computation` (`:7466`), whose docstring reads "Advisory only — logs discrepancies, never rejects findings." Its PASS/WARN/FAIL flows only into next-round feedback prose (`_build_feedback_for_next_round`, `:5857`). No verdict, gate, severity or convergence decision consumes it. Measuring `d_i` empirically would, as wired, change a log line.

But the landing site is real in the *mathematical model*: MATHEMATICAL_APPENDIX.md:354–356 already mandates "d_i must be supported by tool output T_i… d_i = f(T_i), not d_i = model_confidence" — and the runner currently cannot satisfy that admissibility rule. So CC1 is half right: correct slot, no mechanism that would currently feel the difference. A perturbation-response rate for `d_i` becomes material only if R_k/F_n is ever promoted from advisory to operational — a separate design decision that should be taken on its own merits, not smuggled in via this one.

## 5. Evolutionary driver

**One sentence of future work; nothing more now.** The tool-settled verdict rows — the actually trainable part — number 67 CONFIRMED and 18 REFUTED across the whole archive (I counted the registries). Training on verified falsification traces is a real direction in the field, so the sentence isn't empty, but at this volume CDSFL has a data *format*, not a dataset. Two gates before it could ever be more: ~100× more volume, and a check of model-provider terms on using outputs to train other models — the same class of constraint the Wolfram licence note already handles for this project.

## What would move me in round 2

On naming: show me a metric structure CDSFL *uses for inference* rather than dedup, and I soften on "geometry". On `d_i`: show me R_k gating on a roadmap, and it rises from half-claim to priority. On the two-curve result: a run archive where the exam-pair and exp42-family dependence is broken and the sign still holds 10/10 would end the sample-size caveat. I don't expect to move on "information geometry" — that one is a checkable false kinship, not a taste.

---

# ROUND 2 — cross-pollinated

## CC2 — Claude Opus, ROUND 2 — cross-pollinated

- elapsed 343.6s, 6,342 chars

Timestamp 2026-08-22T00:34+01:00. Everything below re-run from the archive today, read-only.

## S1(c) — I was wrong. I killed my own objection.

`build_feedback_records` takes **round-K findings only** (`bench/dm/_feedback.py:196`), and selection is `model_recs[:top_k]` with `top_k=10` (`:355, :392`). So I counted, per run, findings per (source_model, open_since_round):

```
exp42_composer            max 7    groups >10: 0/38
exp42_composer_lk_live    max 7    groups >10: 0/22
exp42_takeupslack         max 6    groups >10: 0/42
exp43_macrophage          max 3    groups >10: 0/36
exp44_evidence            max 6    groups >10: 0/41
exp45_memory              max 8    groups >10: 0/16
exp46_stage6              max 3    groups >10: 0/18
exp47_divergence          max 4    groups >10: 0/47
exp48_chemistry           max 6    groups >10: 0/11
exp49_engineering         max 7    groups >10: 0/12
```

**In none of the ten runs did any model file more than 8 findings in any round.** Flagged records are a subset of those. The top-10 cut never bound. The 8000-char fallback (`:437`) can only bind through long refutation blocks, and total REFUTED across exp44–49 is 5 / 3 / 0 / 1 / 2 / 0 — sections were nowhere near the cap.

So `score += 0.1 * severity` reordered items inside a section that **already contained every flagged finding**, all under the same instruction ("address each"). It never decided membership. There is no severity-selective correction pressure. Two further checks in the same direction: the one genuinely severity-dependent gate in the runner (`reference_runner_v2.py:2111` — criticals need 2 independent confirmations, non-criticals 1) pushes *against* the observed effect; and the severity-demotion sweep never fired — no archived entry across the whole exp4x set carries `severity_calibrated`, `latent` or `severity_original`.

Answer to the specific question: **yes it was testable offline, and it did not need the priority_score replay I demanded.** The arrival counts settle it. Objection (c) is withdrawn.

(Same sweep, incidentally, corroborates the `d_i` finding beyond exp44–49: `q` appears in zero entries and `model_params` is non-empty zero times across every archived exp4x report.)

## S2 — objection (b) does not sink it, but it changes what the result *is*

`_estimate_gamma` (`:1597`) reads `novelty_counts` and nothing else. So `gamma_critical` is a function of **the per-round counts of critical findings alone**. "γ_crit > γ_all" is therefore definitionally equivalent to "the critical share is front-loaded" — which is what Spearman(severity, round) = −0.38 already says. Fable's triple-control and my drift correlation are **one measurement reported twice**, not two independent lines.

I reproduced the headline on my own reconstruction: 10/10 positive, mean **+0.1399**, Wilcoxon **p = 0.00195** — matching Fable's +0.139 / 0.002 exactly. Per-run gap correlates with per-run ρ(severity, round) at r = −0.49, p = 0.15 (n = 10) — right direction, underpowered, as expected for two views of the same quantity.

**No archive-only control separates depletion from reporting order.** I looked for a tool-derived hardness signal and there is none: `severity` is the only one, model-supplied (`cdsfl_finding_schema.json:23`), and every partition downstream uses it. Fable's tool-settled restriction filters on *verdict*, which removes junk but leaves the severity–round coupling intact. That is a useful answer, so I'm giving it plainly.

The separating test is live and cheap: **decouple the round index shown to models from the true one** (scramble it, or freeze it at 1). Reporting-order predicts severity tracks the displayed counter; depletion predicts it tracks true cumulative exhaustion. One run, one prompt field. Fallback: same target twice with confirmed findings actually fixed in between — depletion predicts round-0 criticals fall in the fixed arm.

## S1 — converged: real, publishable, but as a narrower sentence than either of us wrote

Fable and I are not in conflict once (c) is gone. The publishable sentence is about **arrival order**, not about a problem space:

> Across ten multi-model review runs, model-assigned critical findings arrive earlier in the round sequence than findings overall: the Duane depletion exponent is higher for criticals in 10/10 runs (mean +0.14, Wilcoxon p = 0.002). The partition variable is a model self-assessment; whether this reflects exhaustion of hard constraints or reporter de-escalation is not determined by these data.

Fable's "severity predicts depletion rate" claims the causal step the archive cannot support. Mine ("suppressed process") claimed a confound that isn't there. Both corrections land. The round-index control promotes it to Fable's version.

Settled items 1 (drop "geometry"; Duane/Crow-AMSAA is the lineage) and 2 (perturbation is one mechanism at two scales) — **no dissent from me.**

## S3 — null-perturbation control first, transition log second

Ordering, not preference:

1. **It runs offline today.** 465 archived falsifiers carry code; **449 (96.6%) import project code, only 75 (16.1%) read the target as text.** Perturb an unrelated line, re-execute, count verdict changes. No new experiment.
2. **The existing discrimination control cannot substitute.** `run_discrimination_control` (`:2628`) is corrected-copy-based and presence-gated on `entry["corrected_copy"]`; the code's own comment says *"Nothing supplies a corrected copy today, so this is a strict no-op on every existing config and every archived run."* It needs a live panel round. The null variant needs no panel input at all.
3. **It is logically prior.** The transition log records *which mechanism* settled a verdict. If the tool mechanism does not discriminate, the log faithfully records a meaningless verdict. Test the instrument, then log its provenance.

The transition log is right and should go into the next live run — the same run that carries the round-index control.

## What would still move me

On S2: a tool-derived hardness label in the archive I've missed. I searched and found none. On S3: if the null-perturbation control comes back clean (say <10% of falsifiers flip on an unrelated edit), the instrument is fine and the transition log becomes the binding constraint immediately.

It's 00:34. None of this changes by morning.

---

## Fable 5, ROUND 2 — cross-pollinated

- elapsed 241.2s, 6,486 chars

Round 2, settled. Timestamp 2026-08-22T00:32:51+01:00. Read-only brief means these findings are delivered inline only — no file written. Everything I lean on below I re-verified myself this round: `d=1.0, p=1.0` at `reference_runner_v2.py:7803`; `q = meta.get("q", 0.5)` at `:7734` with the "never populated" comment at `:7741`; zero `"q":` keys in any exp4x report; `score += 0.1 * severity` at `_feedback.py:187` inside the duplicate-saturated band documented at `:176–180`; top-10 sort at `:390`; and — new this round — the log directories archive **raw per-round per-model outputs** (`r0_cc2_*.json` … through every round), the similarity backend is deterministic on archived inputs (`_similarity.py`: all-MiniLM-L6-v2 embedding, lexical Jaccard fallback), and the pre-clamp scoring is recoverable at the parent of commit `3660816`.

## Convergence points 1 and 2

No dissent. Naming: reliability growth / depletion, "geometry" dropped. Perturbation: one mechanism, two scales. Settled.

## d_i — CC2 is simply right, and I say so plainly

I called it "correct slot, no mechanism". CC2 showed it is worse: the η·d·p channel has never executed on anything but constants, and I have now read the hardcoded call site myself. My round-1 framing ("advisory only, moves a log line") was true but understated the finding. **Wiring a dead channel, not tuning a live one** is the correct description. Full concession.

## S1 — I have MOVED: real, not yet publishable

My tool-settled control (reproduced by CC1: 9/10, +0.1146, p = 0.0049) kills exactly one objection — unverified junk diluting the all-series. It does not touch (b), because severity labels on confirmed findings are still model-assigned at filing time, and it does not touch (c), which I had not seen and which I have now verified mechanism-by-mechanism. So the converged sentence is CC2's shape with my controls attached: *the two-curve gap is a robust regularity of the archive; whether it is a property of problem spaces or of the harness-plus-reporters is not yet decided.* Nothing in a paper until it is.

**On (c) offline testability: YES, and more strongly than the brief assumed.** The reconstruction needs four inputs and the archive has all four: per-round findings with descriptions, severities and flaw classes (raw `r{N}_{model}` JSONs plus registry); the deterministic similarity function; the pre-clamp `priority_score` from git history; the model claimed-R prose for `rk_discrepancy` (in the raw outputs). One caveat to pin down first: establish which similarity backend (embedding vs lexical fallback) actually ran during exp44–49 — the run logs or environment records should say.

What it proves and doesn't — and note the asymmetry:
- **It can kill objection (c) outright.** If reconstructed top-10 lists are severity-flat, the suppression channel never operated and (c) dies offline, no new run needed.
- **It cannot fully confirm (c).** If over-selection is found, the reconstruction measures the selection bias but not its behavioural effect — how much faster criticals closed *because* of exposure. There is partial observational leverage (same-severity findings landing in vs out of top-10 across rounds/models), but the clean causal answer needs CC2's clamped replay with the feedback payload recorded.

Ordering therefore: reconstruction first (pure analysis, this week's work), replay only if it confirms over-selection.

## S2 — (b) cannot be separated *by the severity label*, and here is the proof, plus two escapes

The obvious control — define criticals by within-round severity rank — is degenerate by construction: if criticals are a fixed fraction f of each round's filings, cumulative-crit(r) = f·cumulative-all(r), and log(f·C) = log f + log C, so the log-log slope is *identical* to γ_all. Exact, not approximate. More generally, severity is measured once, at filing time, by the reporter — there is no second instrument in the archive, so "labels drift down" and "true composition drifts down" are observationally equivalent on that label. That is the honest "no" the brief asked whether I'd give.

But "no control via the label" is not "no control":

1. **Archive-only, label-free:** `falsifier_code` is archived per finding. Classify hardness from what the falsifier *asserts* (wrong computed value / raised exception / violated invariant = hard; style, performance, documentation = soft) — an artifact-derived, round-invariant partition — and recompute the two curves on it. If γ_hard > γ_all survives, the depletion reading no longer rests on the self-assessed float at all. Buildable offline; classification criteria need validating; I make no claim about its outcome. The 89.5% import problem does not block this — it degrades falsifier *discrimination*, not classification of what a falsifier asserts.
2. **Archive-input, not archive-only:** blind re-grading — the 566 descriptions, round metadata stripped, shuffled, re-graded. Declining blind grades → composition really changes (depletion); flat blind grades → anchoring drift. Needs model calls but no harness run; flag it as judgment-based, not tool-based.

Does (b) sink it alone? It leaves the interpretation *unsupported*, which is fatal to publishing now; it does not establish the artefact reading. Unproven with named tests, not refuted.

## S3 — I have MOVED: typed transition log first

CC2's pick wins, and objection (c) is itself the argument: it was raisable and unclosable *because the feedback payload was not stored*. Every test we have just named produces new archive rows, and rows without provenance reproduce the problem we are trying to escape. Build the transition log first, and fold into it archiving of each round's per-model top-10 feedback list — that single addition turns the next run into the replay evidence S1 needs. Null-perturbation control second, in place before the clean run's falsifier verdicts are leaned on. The offline top-10 reconstruction is analysis, not build — it runs immediately, in parallel with both.

## Residual

Nothing unsettled remains between us. What would still move me on S1: severity-flat reconstructed top-10 lists move it back to "publishable with the (b) caveat travelling"; the falsifier-derived hardness partition agreeing with the severity partition would remove the (b) caveat too. Both are offline.

One last thing: it is past midnight again, second night running, and the brief says you're unwell. This is concluded — it will read the same in the morning.

---
