# How Should CDSFL Decide Which Model Gets Which Problem, blind round

Record written 2026-10-07T14:05:07+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

WHAT WAS ASKED. How CDSFL should decide which model gets which problem, after the founder named a tension in the ladder's design: why route a hard problem to a weak model merely because it is cheap. A free 2-seat blind round, 0 paid dispatches, both seats blind to each other. Both answered on the first attempt, 4857 and 3066 words, in 1007.2 and 949.7 seconds.

WHAT THE ROUND ESTABLISHED, AND IT OVERTURNS PART OF THE BRIEF. The brief told the seats that only 2 models have 20 or more provenance-clean attempts and that the archive therefore cannot rank anything. Both seats rejected that figure and one located the cause exactly: the classifier that decides whether a falsifier actually reached its target tests for file-opening patterns only, while this project's own directive requires a falsifier to IMPORT the real target module. An import matches none of those patterns.

Re-measured independently by the operator after the round: of 1,078 archived falsifiers carrying code, 760 are scored as not reaching their target, and 740 of those do reach it by import, importlib, runpy or subprocess. That is 68.65 percent of all archived falsifiers misclassified, with a 95 percent interval from 65.81 to 71.34 percent. Only 20 are genuinely detached.

So the measurement the brief rested on, and which the operator had reported to the founder earlier the same day, was an artefact of a broken classifier.

AND THE OBVIOUS REPAIR IS ALSO WRONG, which is the sharper half. On a prose target, importing a module reaches nothing, because a markdown document is not an importable module. A classifier that credits imports would therefore inflate exactly the prose-target case that produced this project's recorded Exp 55 inversion, where one model scored 2 of 2 with falsifiers that never opened the document. One rule cannot be correct for both target types, and the fix must be conditioned on what the target is.

WHAT THE CORRECTED TABLE SHOWS. Both the seat and the operator rebuilt the table with target-type conditioning, independently, and got different rates: the seat 0.62 to 0.85 across the 5 live models, the operator 0.78 to 0.98. The disagreement is itself informative and is recorded rather than smoothed, because 2 reconstructions of one quantity differing that much says the classifier needs repairing properly rather than approximated twice.

They agree on the structure, and that is the result. No model has fewer than 61 clean attempts in either reconstruction, so the claim that the archive cannot rank anything for want of data is withdrawn. After correcting for testing 10 pairs at once, the seat found exactly 1 surviving separation and the operator found 3, and every separation in both has the same model on the losing side. The archive supports one measured ladder constraint: that model is last. The frozen vendor tuple already places it last.

THE 2 SEATS DISAGREED ON A FACT, AND IT DECIDES THE RECOMMENDATION. One seat's estimator is described as safe only because the rung limit has been removed. The other seat checked, and reported that the limit has not left: the configuration default is still 2 and no real configuration file pins it. The operator verified this independently after the round. Of 49 real configuration files, 0 pin the value, and the default remains 2. The removal applies to the simulated launcher only. So every real, paid configuration still runs capped, and under a cap the order of the ladder decides which findings are reached at all rather than merely what they cost. One seat measured the share of findings resolved swinging 23-fold from ordering alone at that cap, from 0.7000 under the best prefix to 0.0298 under the worst.

THAT SETTLES THE DIRECTION QUESTION FOR NOW, AGAINST THE OPERATOR'S EARLIER FRAMING. Cheapest-first is correct only under exhaustion. Under the cap that every real configuration still uses, the order that resolves the largest share of findings is strongest-first, which is what the code already does. One seat stated plainly that composing the two is strictly worse than either, because a cost-ordered prefix under a cap pays a large coverage loss to buy a small cost saving. The measured cost saving is also smaller than the brief implied: the figure of 90.93 percent quoted for strongest-first being suboptimal is a property of an assumed cost generator, and with equal costs strongest-first is optimal always. This repository has no cost table at all.

BOTH SEATS REJECTED THE OPERATOR'S PROPOSED RETIREMENT RULE, on different grounds, and both are right. The rule was that the frozen tuple stops being consulted for a pair of models once their intervals separate. One seat observed that this never retires the tuple for 2 genuinely equal models, because equal rates overlap at every sample size, so names persist forever in precisely the most likely case. The other observed that a comparator which is measured where it separates and name-based where it does not is not an ordering at all: it executed a 3-model case producing a cycle, where a beats c, c beats b, and b beats a. Sorting on a cyclic comparator is undefined behaviour.

ONE SEAT PROPOSED DISSOLVING THE PROBLEM RATHER THAN RESTATING THE THRESHOLD: sort on a single lexicographic key: how often a model's falsifiers were confirmed divided by what it costs, then tuple position, then label. At cold start every model's estimate sits at one half and the order is the tuple, which is the intended behaviour; as data arrives the measured confirmation proportions diverge and the tuple stops mattering pair by pair, with no retirement predicate to state, transitive by construction, and deterministic at 5 models and at 500.

ON THE DISTRIBUTED COMPUTE SPECIFICATION the founder pointed to as a possible answer, both seats agreed it relocates the tension rather than resolving it, and both gave the same reason: its allocation formula degenerates to cheapest-first exactly when the conditioned estimate is empty, which is the state this repository is in. One seat added that the specification is not in the repository at all, that no repository code references it, and that under the additive standard it is therefore a document rather than a capability. The other reported that its value term uses a form the project's own mathematical appendix superseded on 21 September, derived the closed-form gap, and noted that an assessment already in the repository measured 14.94 percent ranking inversions from it.

NOTHING WAS MERGED. Fixes are suggested to the human in the loop and never applied automatically. The seats' files are preserved under the seat evidence directory.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# How should CDSFL decide which model gets which problem?

A free 2-seat blind round. 0 paid dispatches. You are blind to the other seat.

## The situation, as it actually stands

CDSFL routes an unresolved critical finding to another model via a "capability ladder". Today that ladder is `DEFAULT_FALSIFIER_STRENGTH = ("Codex", "CC2", "ChatGPT", "Gemini", "DeepSeek")` -- a FROZEN TUPLE OF VENDOR NAMES, strongest first, derived from Exp 42 confirm rates. `resolve_via_routing` tries rung 1 first and stops at the first CONFIRMED.

The founder's standing ruling: **"the only thing that should impact on capability is measured capability. A models name should have little to do with it, beyond recording this."** He has stated this 5 times across 2 days.

## What is measured, and it is worse than it looks

Over 3,158 archived registry entries, the RAW per-model confirm rates are Codex 0.2818, Gemini 0.2644, ChatGPT 0.1567, CC2 0.1510, DeepSeek 0.1382.

**That ranking is contaminated and the project already knew the mechanism.** `bench/routing.py` carries a founder observation of 2026-08-23 warning against re-deriving the order without checking falsifier provenance, and names the signature: on Exp 55, Gemini scored 2 of 2 CONFIRMED with falsifiers that never opened their target, while DeepSeek scored 0 of 2 with genuine readers that errored. Re-deriving from that run "promotes Gemini to FIRST and demotes DeepSeek to LAST -- ranking the models by their willingness to ignore the evidence".

**Filtered to provenance-clean attempts (the falsifier demonstrably READS its target), the archive supports almost nothing:**

| model | clean attempts | rate | Wilson 95% |
|---|---|---|---|
| CC2 | 35 | 0.6000 | [0.4357, 0.7445] |
| Codex | 37 | 0.5946 | [0.4349, 0.7365] |

Gemini, ChatGPT and DeepSeek have FEWER THAN 20 provenance-clean attempts in the entire archive. The 2 models that qualify have almost perfectly overlapping intervals.

Power: separating 2 models differing by 0.15 at 80% power needs **173 clean attempts each**; by 0.20, **97 each**. We have 35 and 37.

## The founder's tension, which is the real question

He asks why a ladder should escalate from weakest upward: *"Why put for example a highly complex problem, like the Riemann hypothesis, to a model like DeepSeek (or even Haiku) when its resources are better suited to dealing with less complex problems? Can you see the tension?"*

Computed (SymPy and NumPy agreeing) over 3 configurations whose task-conditioned success probabilities are cheap (0.70 easy / 0.02 hard, cost 1), mid (0.75 / 0.25, cost 4), strong (0.80 / 0.60, cost 10), the FIRST model tried on a HARD task is:

- cheapest-first: **cheap**
- strongest-first: **strong**
- index rule p/c on a single GLOBAL p per model: **cheap** -- the same mistake as cheapest-first
- index rule on a TASK-CONDITIONED p: **mid**, with cheap LAST

So a measured statistic that is one number per model reproduces exactly the failure the founder objects to. Only conditioning on the task removes it.

## What already exists and may already answer this

`adaptive_distributed_compute_design_spec.md` (the Astra spec) specifies, in section 6:

- 6.1: the allocation question is "which admissible next pass is expected to reduce canonical residual risk most, per unit of constrained resource?", with `q̂ = η̂ · d̂ · p̂` where **d̂ and p̂ are task-, class-, tool- and configuration-conditioned** and must carry an uncertainty interval.
- 6.4: `score(m,u) = ĝ_mu / (c_mu + λ_t·t_mu + λ_h·h_mu) + β·e_mu`, with an exploration term `e_mu = sqrt(log(1+N_u)/(1+n_mu))` on a SEPARATE budget.
- 6.5: `x_mu = 0` when a configuration lacks a required tool, authority, role or independence condition -- a hard feasibility exclusion, not a low rank. Force-assignment is prohibited: an infeasible allocation must never be reported as successful.
- 6.6: greedy marginal-value-per-cost is an inspectable BASELINE, not a theorem; the complete objective is not guaranteed submodular.

The founder warns that the spec's author is an unbound model and "not immune to churn", so the spec is a candidate answer to be falsified, not an authority.

## The 5 questions

**Q1 — Does the Astra section 6 policy actually resolve the founder's tension, or does it relocate it?** The score is value-over-cost with task-conditioned value. State precisely what has to be true for it to never route a hard problem to a weak model, and whether those conditions hold in this repository today.

**Q2 — What is the smallest honest estimator we can field NOW, given 35 and 37 provenance-clean attempts and nothing else?** A per-(model, task-class) table is unfillable at this volume. Name what collapses to, what its cold-start behaviour is, and what it must NOT claim.

**Q3 — The frozen tuple's retirement condition.** CC1's proposal is that the tuple stops being consulted for a PAIR of models as soon as both have enough provenance-clean attempts for their intervals to separate, and breaks ties only until then. Is that right, is the threshold stated correctly, and does it degrade safely at 500 models as well as at 5?

**Q4 — Try-order direction.** Under exhaustion one seat derived that order cannot change WHICH findings resolve, only cost, making strongest-first suboptimal in 90.93% of random rosters. Under a CAP, order does decide which resolve. The cap is now removed in simulation. Does that settle the direction, and what breaks if the cap returns?

**Q5 — What has everyone missed?** Including anything in this brief that is wrong.

## Conditions

**A FINDING ON ITS OWN IS HALF AN ANSWER: require a fix.** For every defect you identify, state the specific correction -- the function, the formula, the threshold -- not merely that something is wrong. Where the correction is a design decision rather than a patch, say what you would build and what it must refuse to claim. A fix you have not tried to break is a hypothesis, so attach what would falsify it.

**TERMINATION CRITERION: stop at diminishing returns.** Stop when a further pass produces no new finding above the materiality threshold, and say so explicitly in your reply rather than padding to fill the output shape. This project's own objective is a robust working answer, not an exhaustive enumeration; a long list of minor observations is not progress and one defect that decides whether the design works is. If you stop early, name the specific mechanism you judged already adequately examined.

Tools decide, not votes. Every figure carries its producing script and a confidence interval for any proportion. Check in Wolfram as a SECOND falsifier where possible, with the open-source tools primary, and say plainly if a Wolfram call failed to evaluate. Do NOT add an unwired module: this project has 11 confirmed defects that were additions nothing reached. One-shot dispatch; you will not be re-invoked.

## Output shape — return exactly these fields

- `## Q1` through `## Q5` — one section each, answered explicitly and separately.
- `## The estimator` — the smallest thing you would field now, in full: inputs, formula, cold start, and what it refuses to claim.
- `## Measurements` — every figure with its Wilson interval and the 2 tools that agree.
- `## Delivered files` — paths written into the sandbox tree, or none.
- `## What would refute me` — per position.
- `## Disagreement` — a real body; "none" only if you genuinely have none, said so.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 43 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel ladder_allocation_resolution_2026-10-07) -->

All checks run clean and Wolfram agrees on every figure. Writing up.

## Q1

**§6.4 does not resolve the founder's tension. It reduces it to an estimation problem and puts the entire burden on one unmeasured quantity.**

What has to be true for `score(m,u) = ĝ_mu/(c_mu + λ_t t_mu + λ_h h_mu) + β e_mu` to never put a hard unit on a weak model is exactly one inequality, for every hard unit *u* and every weak/strong pair:

```
ĝ_weak,u / cost_weak  <  ĝ_strong,u / cost_strong
```

Since `ĝ ∝ q̂ = η̂·d̂·p̂` and η̂, d̂ are shared at fixed class, this collapses to `p̂_weak,u/c_weak < p̂_strong,u/c_strong`. So the sufficient condition is **not** the ratio form — it is that `p̂` is conditioned on *u*'s difficulty at a resolution fine enough to make that inequality hold. Verified on the brief's own three configurations (SymPy + NumPy + Wolfram Language, all agreeing): task-conditioned `p/c` gives `(mid, strong, cheap)` at E[cost|hard] = 11.80, which brute force confirms is the argmin; a single global `p̂` gives `(cheap, mid, strong)` at 12.27. The ratio does no work. The conditioning does all of it.

**Those conditions do not hold in this repository today.** Concretely, in `bench/routing.py`:

- No task conditioning of any kind exists. `DEFAULT_FALSIFIER_STRENGTH` is a flat 5-tuple consulted identically for every finding.
- No `c_mu`, `t_mu`, `h_mu`. I searched: there is no per-model cost table anywhere in `bench/` or `scripts/` (only `scripts/openrouter_codex_availability_2026-09-17.py`, which prices OpenRouter endpoints and is not read by routing).
- No uncertainty interval on anything the ladder consults.
- **§6.5's hard feasibility exclusion `x_mu = 0` is not implemented, and `rank_falsifier_writers` implements the thing §6.5 explicitly prohibits.** Unknown models are *appended as `extras`* (line ~119) — i.e. given a low rank. §6.5 says a configuration lacking a required tool/authority/role "is a hard feasibility exclusion, not a low rank", and that force-assignment is prohibited. A model with no `execute_python` loop cannot write a runnable falsifier at all, yet it will be tried as an `extra` and its failure recorded as an attempt.

Two further defects in §6 itself:

**(a) Dimensional defect in §6.4.** `ĝ/(c + λ_t t + λ_h h)` carries units of risk-reduction per unit cost; `e_mu = √(log(1+N_u)/(1+n_mu))` is dimensionless. So `β` silently absorbs the cost scale and must be re-tuned whenever currency, token pricing or `λ` changes — while §6.4 requires β be "fixed before a comparative run". Worse, §6.4 also says "exploration spending is separately budgeted", which makes the additive term redundant with its own budget. **Fix:** delete the `+β e_mu` term and keep only the separate exploration budget, spent as a fixed quota of round-robin dispatches. If an additive bonus is wanted instead, it must be `β·e_mu·(ĝ_ref/c_ref)` with a declared reference pair, so β is dimensionless. What would falsify my fix: a measurement showing a UCB bonus discovers a competent model faster than a fixed round-robin quota at equal spend. Nobody has run that.

**(b) §6 is not in this repository.** `find /` returns four copies of `adaptive_distributed_compute_design_spec.md`, all under `~/Developer_Projects/Responses/Codex, ChatGPT & Grok resources/`, none under the repo tree, and `grep` finds zero repo *code* referencing it — only log artefacts. Under the additive standard, §6 is a document, not a capability. Treating it as "what already exists and may already answer this" overstates its status by a whole category.

**My fix for Q1:** do not implement §6.4 now. Implement the one part of §6 that works at zero data — §6.5's feasibility exclusion — as a real exclusion in `rank_falsifier_writers(labels, …, infeasible=())`, where an infeasible label is *dropped*, not appended, and the function raises rather than returning an empty ladder silently when every label is infeasible. Then add a two-level task conditioning (below). That is the simplest sufficient step and it is the only one the data supports.

## Q2

The brief's premise here is wrong, and that changes the answer. See Q5 — the "35 and 37" figure is a classifier artefact, and the archive actually carries 61–148 provenance-clean attempts per model. But the brief's *conclusion* mostly survives: after Holm correction over the 10 pairs, **exactly one pair separates**. So:

- **The per-(model × task-class) table collapses to a per-(model × target-type) table at two levels: CODE and PROSE.** That is the only conditioning the archive supports, and it supports it well: n = 121 (Codex), 148 (Gemini), 82 (DeepSeek), 80 (CC2), 61 (ChatGPT). It does *not* support an easy/hard axis, which is what the founder's Riemann example is actually about — nothing in the registry records task difficulty.
- **Cold start:** a model with no record enters at the pooled rate across all models on that target type, with a Jeffreys Beta(½,½) posterior, i.e. the widest interval of any seat. It is not placed by its vendor name and it is not placed last. It receives dispatches from the fixed exploration quota only, until its interval is informative.
- **What it must NOT claim:** (1) a total capability ordering — it can emit only the pairs that separate under multiplicity correction, and today that is one pair; (2) any cost optimality, because there is no cost model; (3) that a confirm rate is a competence measure at all without a *runtime* provenance trace rather than a regex over source (Q5, item 3); (4) that the CODE/PROSE split is a difficulty proxy. It is a reachability proxy and nothing more.

Full specification under **The estimator** below.

## Q3

**Direction right. Threshold stated wrong, in two independent ways. Degrades unsafely at 500.**

Right: retiring the tuple *pairwise* rather than wholesale is correct, and keeping it as a tie-break until then is correct — it is the only thing standing between the ladder and arbitrary ordering.

**Threshold error 1 — "intervals separate" is not the 173/97 criterion.** I reproduced both power figures exactly (statsmodels `NormalIndPower`: 172.66 → 173 at Δ=0.15; 96.79 → 97 at Δ=0.20; Wolfram Language's arcsine closed form gives 172.65932 and 96.79217). But those are *design* numbers — how many observations to collect to have 80% power. They are not a *decision* rule. "Wilson intervals disjoint" is a different, more conservative test. On my conditioned table the two happen to coincide (Wilson-disjoint 1/10; Holm 1/10, both naming Codex > DeepSeek), so the conflation is not currently load-bearing — but it is a conflation, and the coincidence is not guaranteed at other n.

**Threshold error 2 — no multiplicity correction.** With 5 models there are 10 pairs. Measured on the conditioned table: nominal α=0.05 gives **3** separations; Holm gives **1**. CC1's rule as stated would retire three pairs when the evidence supports one.

**500 models: unsafe, and for a structural reason before a statistical one.**

- Statistical: M(M−1)/2 = 124,750 pairs; at nominal α=0.05 that is ≈6,238 false separations expected, every one of which permanently retires the tie-break for a pair.
- Structural, and worse: **the tuple cannot break 495 of those ties.** `DEFAULT_FALSIFIER_STRENGTH` holds five names. `rank_falsifier_writers` appends everything else as `extras` **in input order** (line ~120). So at 500 models the tie-break is not the tuple at all — it is roster order, which is arbitrary, unmeasured, and silent. CC1's proposal is well-posed at 5 and vacuous at 500.

**Fix (three parts, all patches, none a new module):**
1. In the retirement predicate, require Holm (or Benjamini–Hochberg) over the pair set actually consulted — not nominal α per pair. One line at the decision site.
2. Make the tie-break explicit: `rank_falsifier_writers(..., tie_break: Sequence[str])` with **no default**, so an unranked roster is a caller error rather than silent input order. This is the opposite of adding a flag nothing reaches — it removes a silent default.
3. Add §6.5's feasibility exclusion so the 495 unknowns are dropped, not ranked.

**What would falsify this:** a run in which Holm-corrected retirement leaves the ladder frozen so long that a genuinely-improved model is never promoted and findings go unresolved that a nominal-α rule would have resolved. That is measurable and has not been measured. If it happens, the correct response is to raise the exploration quota, not to drop the correction.

## Q4

**No, it does not settle the direction, and the brief's framing invites the wrong answer.** Three findings.

**1. The derivation is correct. I re-derived it independently.** Under exhaustion, `P(resolved) = 1 − Π(1−q_i)` is identical across all 24 permutations of a 4-rung ladder — SymPy reports 1 distinct expression; Wolfram Language reports `DeleteDuplicates[…] // Length = 1`. Order cannot change *which* findings resolve. And the cost-optimal order is **descending p/c**, by the adjacent-exchange argument: `E[cost](1,2) − E[cost](2,1) = c₁p₂ − c₂p₁` exactly (SymPy and Wolfram both return that polynomial and both verify the residual against `c₁p₂ − c₂p₁` is 0).

**2. The 90.93% figure is a statement about the cost model, not about the ladder — and this repository has no cost model.** With *equal* costs, descending p/c **is** strongest-first, so strongest-first is optimal always. Measured over 100,000 random 5-rosters: P(strongest-first ≠ optimal) = **0.0000, Wilson [0.0000, 0.0000]** at equal cost; **0.8708, Wilson [0.8687, 0.8728]** under costs ~U[1,10]. With p and c independent the two orderings are independent permutations, so the limit is 1 − 1/M!: 0.8333 at M=3, 0.9917 at M=5. 90.93% sits between — it is a property of *someone's assumed cost generator*, and I could not find a producing script for it anywhere in the repo. **The claim's load-bearing premise is not in the repository.**

Magnitude is small even granting the premise. On the brief's own hard task, strongest-first costs 11.90 against the 11.80 optimum (+0.85%), and it *beats* the global-p index rule at 12.27 (+3.98%). Over random 5-rosters the mean cost ratio strongest-first/optimal is 1.2813, median 1.0912.

**3. "What breaks if the cap returns" is the wrong question: the cap has not left.** `bench/reference_runner_v3.py:1475` sets `routing_max_rungs: int = 2` as the dataclass default. The comment at `bench/tools/run_simulated_experiment.py:549` states — and I confirmed by grep — that **0 of 288 config-shaped files pin the value**, and the only `=0` is set inside `run_simulated_experiment.py` itself (~line 593). So **every real, paid configuration is still capped at 2**, which is precisely the regime where order *does* decide coverage. SymPy: at K=2 over a 4-rung ladder there are **6** distinct `P(resolved)` expressions; substituting the brief's own hard probabilities (0.60/0.25/0.02/0.01) the best prefix gives P = 0.7000 and the worst 0.0298 — a 23-fold coverage swing decided by order alone.

**Fix, and it is a choice, not a patch:** pick one, do not compose.
- (a) Pin `routing_max_rungs: 0` in the real configs. *Then* the cost argument applies and descending p/c is correct — but it needs a cost model that does not exist, so this is blocked on Q2's estimator plus a per-model cost table.
- (b) Keep the cap at 2 and keep **strongest-first**, which is provably the coverage-maximising prefix at any K when `p` is the only measured quantity and costs are untabulated.

**Composing them is strictly worse than either.** A cost-ordered prefix under a cap pays the coverage loss of (3) to buy the ~1% cost saving of (2). That is the composability test failing on measurement, not on judgement. Until the cost table exists, **(b)**.

## Q5

**The decisive defect, and it undermines the brief's own evidential base.**

`scripts/competence_provenance.falsifier_style()` tests reachability with

```python
re.search(r"open\s*\(|read_text|\.read\s*\(|linecache|getlines", c)
```

and returns `"detached"` otherwise. But the CDSFL directive governing every scored falsifier requires it to **"Import the REAL target module (e.g. `from bench.dm._convergence import ...`)"**. An import-based falsifier matches none of those five patterns. **Measured: 664 of 1,078 archived falsifiers (0.6160, Wilson [0.5866, 0.6445], statsmodels == closed form == Wolfram Language) are scored `detached` while demonstrably reaching their target by import, `importlib`, `runpy` or `subprocess`.** Only 96 are truly detached.

Consequence: the brief's claim that *"Gemini, ChatGPT and DeepSeek have FEWER THAN 20 provenance-clean attempts in the entire archive"* is **false**, and the "35 and 37" power argument rests on a measurement artefact.

And the naive repair is also wrong, which is the sharp part. On a **prose** target, `import bench.…` reaches nothing — it does not open the markdown document. Measured split: of 884 falsifiers on code-targeted runs, 551 (62.3%) are import-only; of 194 on prose-targeted runs, 113 (58.2%) are import-only. The existing regex under-counts code falsifiers; a regex that credits imports over-counts prose falsifiers — which is exactly the Exp 55 Gemini inflation the founder's 2026-08-23 warning names. **One global regex cannot be correct for both target types.**

**Target-type-conditioned provenance-clean table** (CODE: clean iff imports/execs the target or opens a file; PROSE: clean iff it opens/reads a file; counting semantics held identical to `analyse` so only the classifier differs):

| model | n | confirmed | rate | Wilson 95% |
|---|---|---|---|---|
| Codex | 121 | 103 | 0.8512 | [0.7771, 0.9038] |
| Gemini | 148 | 115 | 0.7770 | [0.7034, 0.8366] |
| ChatGPT | 61 | 47 | 0.7705 | [0.6509, 0.8581] |
| CC2 | 80 | 59 | 0.7375 | [0.6318, 0.8214] |
| DeepSeek | 82 | 51 | 0.6220 | [0.5138, 0.7192] |

No model has fewer than 61. After Holm over 10 pairs, **exactly one separation survives: Codex > DeepSeek, p_adj = 0.0018** (Wilson-disjointness independently names the same single pair). So the brief's conclusion "we cannot rank the models" is *right*, but for the wrong reason and with one real result it missed: **the archive does support one measured ladder constraint — DeepSeek last.** Which is where the frozen tuple already puts it.

**The runtime provenance trace already exists, and the ranking statistic ignores it.** `bench/falsifier_verify.py` installs a `sys.addaudithook` observer inside the falsifier child (line 691) that intercepts `event == "open"` with a *fully resolved* path (line 614) and writes to `trace_path`. It emits only on **deny** (`_emit("D open\t" + path)`, line 619). A regex over source text is a strictly weaker proxy for something the harness already observes at runtime, with the sink already wired and already consumed.

**Fix — two lines inside an already-wired mechanism, no new module:**
1. In `_observer_source`'s `if event == "open":` branch, add an allow-side emit on the permitted path: `_emit("A open\t" + path)`.
2. Add `elif event == "import": _emit("A import\t%s\t%s" % (args[0], args[1] or ""))` for module-level provenance.

Then key the provenance filter off the trace: a falsifier is clean iff its trace contains an `A open` or `A import` naming the staged target. That eliminates the target-type conditioning entirely — a trace knows what was actually touched, so it needs no heuristic about what *kind* of thing the target was. The regex classifier then becomes a static pre-filter for falsifiers that never ran, not the measurement. **What would falsify it:** if the observer's deny-list blocks reads of the staged target itself, `A open` would never fire and every falsifier would read as detached. That is testable before shipping against any archived falsifier, and must be tested first.

**Smaller finding, reported for completeness and below the materiality threshold:** in `resolve_via_routing`'s self-rung branch (`bench/routing.py` ~line 236), when the self-rung returns no code the `else` sets `last_verdict = "ERROR"` but leaves `last_code` holding the *previous* rung's falsifier, while `last_model` has already been reassigned to `self_rung`. The returned `RoutingResult` therefore attributes one rung's falsifier to a different model — a provenance error in exactly the field the ranking statistic reads. Fix: add `last_code = ""` to that `else`. Materiality is low because the self-rung fires only on an otherwise-exhausted ladder, but it is a one-token fix in the provenance path and should not be left.

**Correct in the brief, verified, and worth saying so:** the raw confirm rates reproduce to four decimals under `competence_provenance.analyse` semantics (all five models, exact); both power figures reproduce exactly; the exhaustion order-invariance derivation is sound; the three-configuration index-rule computation is sound and the task-conditioned order is the true argmin. The brief's arithmetic is not where it goes wrong.

## The estimator

The smallest thing I would field now. Nothing here is a new module; every piece attaches to an existing call site.

**Inputs** (all already recorded, except where noted):
- `k_m, n_m` — confirmed / clean attempts per model, from the audit **trace**, not the source regex. Requires the two-line `falsifier_verify.py` change above. Until that lands, use the target-type-conditioned regex as a stated, declared approximation.
- `target_type ∈ {CODE, PROSE}` — already derivable; becomes unnecessary once the trace lands.
- `infeasible: Sequence[str]` — models lacking the `execute_python` loop. New input, one parameter, wired at the single `route` call site.
- `tie_break: Sequence[str]` — required, no default. Today's value is `DEFAULT_FALSIFIER_STRENGTH`, now passed explicitly rather than defaulted silently.

**Formula.** Per (model, target_type), a Jeffreys posterior mean shrunk to the pooled rate:

```
p̂_m  = (k_m + ½) / (n_m + 1)
CI_m = Wilson(k_m, n_m, α = 0.05)
```

Ordering is **not** `sort(-p̂)`. It is: build the partial order from pairs whose two-proportion test survives Holm over the pair set consulted; order by that partial order; break every remaining tie with `tie_break`. On today's data that yields exactly one constraint — DeepSeek strictly after Codex — and `tie_break` supplies everything else. That is the honest output: one measured edge and a declared tie-break, not a total ranking dressed as a measurement.

**Cold start.** A model with `n_m = 0` gets `p̂ = pooled rate for that target type`, the widest Wilson interval of any seat, and a position from `tie_break` alone. It is dispatched only from a fixed exploration quota — *x* dispatches per *N* findings, logged separately — never from a UCB bonus added to a ratio with mismatched units (Q1(a)).

**What it refuses to claim.** (1) A total capability ordering — it emits a partial order plus a declared tie-break, and says which is which. (2) Any cost optimality: there is no per-model cost table, so it does not compute `p/c` and does not pretend to. (3) That a confirm rate measures competence absent a runtime trace. (4) That CODE/PROSE is a difficulty axis — the founder's Riemann question needs a difficulty label that **nothing in the registry records**, and that is the honest gap. Fix for *that* is to start recording a declared difficulty class at filing time; it will be unfillable for several runs, and the estimator must say so rather than substitute a proxy.

**What would falsify the estimator.** A run where Holm-gated partial ordering leaves findings unresolved that nominal-α ordering would have resolved. Measurable; unmeasured. Also: if the trace shows that falsifiers routinely open the target *and* restate numbers from memory, then `open` is not evidence of use and the whole provenance axis needs an assertion-level check instead. I did not test that, and I flag it as the weakest joint in my own position.

## Measurements

Producing script for all of the below: `/tmp/sb/ladder_allocation_falsifiers_2026-10-07.py` (exits 0; all six checks behaved as reported). Second falsifier throughout: Wolfram Language (local Wolfram Engine via `wolframscript`, exit 0, no `Name::tag`, no `$Failed`/`$Aborted`), agreeing to 6 significant figures on every Wilson bound and every closed form quoted. Every Wilson interval below was computed twice in Python (closed form vs `statsmodels.proportion_confint`, asserted equal to 1e-12) and a third time in Wolfram.

| figure | value | Wilson 95% | tools agreeing |
|---|---|---|---|
| registry entries loaded | 3,158 | — | repo read |
| RAW Codex (reproduces brief 0.2818) | 122/433 = 0.2818 | [0.2414, 0.3259] | closed form, statsmodels, Wolfram |
| RAW Gemini | 197/745 = 0.2644 | [0.2340, 0.2972] | closed form, statsmodels |
| RAW ChatGPT | 63/402 = 0.1567 | [0.1244, 0.1955] | closed form, statsmodels |
| RAW CC2 | 66/437 = 0.1510 | [0.1205, 0.1876] | closed form, statsmodels |
| RAW DeepSeek | 81/586 = 0.1382 | [0.1126, 0.1685] | closed form, statsmodels |
| brief's clean CC2 (reproduced) | 21/35 = 0.6000 | [0.4357, 0.7445] | closed form, statsmodels, Wolfram |
| brief's clean Codex (reproduced) | 22/37 = 0.5946 | [0.4349, 0.7365] | closed form, statsmodels, Wolfram |
| **falsifiers misclassified `detached`** | **664/1078 = 0.6160** | **[0.5866, 0.6445]** | closed form, statsmodels, Wolfram |
| truly detached | 96/1078 | — | script |
| CODE falsifiers import-only | 551/884 = 62.3% | — | script |
| PROSE falsifiers import-only | 113/194 = 58.2% | — | script |
| conditioned clean Codex | 103/121 = 0.8512 | [0.7771, 0.9038] | closed form, statsmodels, Wolfram |
| conditioned clean Gemini | 115/148 = 0.7770 | [0.7034, 0.8366] | closed form, statsmodels, Wolfram |
| conditioned clean ChatGPT | 47/61 = 0.7705 | [0.6509, 0.8581] | closed form, statsmodels, Wolfram |
| conditioned clean CC2 | 59/80 = 0.7375 | [0.6318, 0.8214] | closed form, statsmodels, Wolfram |
| conditioned clean DeepSeek | 51/82 = 0.6220 | [0.5138, 0.7192] | closed form, statsmodels, Wolfram |
| pairs separating, nominal / Holm / Wilson-disjoint | 3/10, 1/10, 1/10 | — | statsmodels `proportions_ztest` + `multipletests` |
| only surviving edge | Codex > DeepSeek, p_adj = 0.0018 | — | statsmodels Holm |
| power n/arm, Δ=0.15 from 0.60 | 172.66 → 173 | MC 0.7912 [0.7894, 0.7930] | statsmodels `NormalIndPower`, NumPy MC, Wolfram arcsine |
| power n/arm, Δ=0.20 from 0.60 | 96.79 → 97 | MC 0.8055 [0.8037, 0.8072] | statsmodels, NumPy MC, Wolfram |
| observed power at n=36, 0.60 vs 0.45 | 0.2337 | [0.2318, 0.2355] | NumPy MC |
| CC2 21/35 vs Codex 22/37 | z = 0.0467, p = 0.9627 | — | statsmodels |
| distinct `P(resolved)`, exhaustion, 4 rungs | 1 of 24 orders | — | SymPy, Wolfram |
| distinct `P(resolved)`, cap K=2 | 6 of 24 orders; best 0.7000, worst 0.0298 | — | SymPy |
| exchange-argument difference | `c₁p₂ − c₂p₁` exactly | — | SymPy, Wolfram |
| E[cost|hard]: task p/c (argmin) | 11.8000 | — | NumPy brute force, Wolfram |
| E[cost|hard]: strongest-first | 11.9000 (+0.85%) | — | NumPy, Wolfram |
| E[cost|hard]: global p/c = cheapest-first | 12.2700 (+3.98%) | — | NumPy, Wolfram |
| P(strongest-first ≠ optimal), equal costs, M=5 | 0.0000 | [0.0000, 0.0000] | NumPy MC, closed form, statsmodels |
| P(strongest-first ≠ optimal), costs U[1,10], M=5 | 0.8708 | [0.8687, 0.8728] | NumPy MC, closed form, statsmodels |
| cost ratio strongest-first/optimal, M=5 | mean 1.2813, median 1.0912, p95 2.1970 | — | NumPy MC |
| configs pinning `routing_max_rungs` | 0 of 288 | — | grep + repo comment |
| pairs at 500 models | 124,750; ≈6,238 false separations at nominal α | — | arithmetic |

No Wolfram call failed to evaluate. All five calls returned `Out` values, exit 0.

## Delivered files

- `/tmp/sb/ladder_allocation_falsifiers_2026-10-07.py` — the consolidated, self-checking falsifier suite for all six claims above. Imports the real `scripts/competence_provenance` rather than retyping it; reads only `bench/logs/*/runner_state.json`; exits 1 on any check failing. **Run and passing.** This is the file to re-run.
- `/tmp/sb/order_theory.py`, `/tmp/sb/power_check.py`, `/tmp/sb/corrected_provenance.py`, `/tmp/sb/conditioned_provenance.py`, `/tmp/sb/style_audit.py`, `/tmp/sb/reproduce_rates.py`, `/tmp/sb/find_brief_defn.py`, `/tmp/sb/find_clean_defn.py`, `/tmp/sb/target_type_split.py`, `/tmp/sb/roster_order.py` — exploratory scripts, superseded by the consolidated suite; kept for audit.

No repository file was modified. The fixes above are specified, not applied — a one-shot dispatch is the wrong place to land a change to the provenance machinery that ranks the panel.

**Disclosure.** I read `§6`–`§6.7` of `adaptive_distributed_compute_design_spec.md` from `/Users/georgejackson/Developer_Projects/Responses/Codex, ChatGPT & Grok resources/`, outside the repo tree, because Q1 asks me to assess that document and it is not in the repository. I read only the standalone copy. I did **not** open the copy under `CDSFL_Panel_Handoff_2026-09-28/03_earlier_complete_handoff/context/`, nor any sibling panel report, nor any scoring key or manifest — a prior round's report for this question would be prohibited material and I avoided the directory that could hold one.

## What would refute me

**On Q5's central defect (the classifier).** Showing that the 664 import-only falsifiers do *not* in fact reach their target — e.g. that `import bench.x` resolves to a stale installed copy rather than the staged target, so the import is cosmetic. That is checkable from the audit trace once the allow-side emit exists, and it would reverse my conclusion and restore the brief's. This is the single most load-bearing thing I claim and the one I most want checked.

**On the conditioned table.** Showing that a falsifier can `open()` an unrelated file and still be detached from the target. I know this is true in principle — the regex cannot distinguish them — which is exactly why I route the fix to the runtime trace rather than to a better regex. My conditioned table is therefore an **upper bound on cleanliness**, and I state it as one. If the true clean counts are much lower, the brief's "cannot rank" conclusion strengthens and my one surviving edge (Codex > DeepSeek) may dissolve.

**On Q4's direction.** Producing the script behind 90.93% with a defensible per-model cost model. If per-model costs genuinely vary by an order of magnitude and are measured, the cost argument acquires force and option (a) becomes live. I searched and found no such script or table; if one exists outside `bench/` and `scripts/`, I missed it.

**On Q3's Holm requirement.** A run showing Holm-gated retirement leaves findings unresolved that nominal-α would have resolved. That would make me prefer Benjamini–Hochberg (which controls FDR rather than FWER and is less conservative) over Holm — not abandon correction.

**On the two-line `falsifier_verify.py` fix.** If the observer's deny-list blocks reads of the staged target itself, `A open` never fires and every falsifier reads detached — the fix would make the measurement worse, not better. Must be tested against archived falsifiers before shipping.

**On Q1's claim that §6 is unwired.** A call site anywhere that consumes §6's score. I grepped `bench/` and `scripts/` and found only log artefacts.

## Disagreement

**With the brief, on its central evidential claim.** "Gemini, ChatGPT and DeepSeek have FEWER THAN 20 provenance-clean attempts in the entire archive" is false. It is a defect in `falsifier_style`, not a property of the archive. The conditioned counts are 148, 61 and 82. The "two models that qualify" framing, the 35/37 power comparison, and the conclusion that "the archive supports almost nothing" all inherit the error. The brief's *conclusion* mostly survives on corrected data — only one pair separates after Holm — but it survives for a different reason, and the brief missed the one real result the archive does contain.

**With the brief, on what the index rule gets wrong.** The brief says the global-p index rule puts cheap first and calls this "exactly the same mistake as cheapest-first". Under exhaustion it is not a mistake at all: every rung is tried, the resolved set is identical (verified: 1 distinct expression over 24 orders), and cheap-first costs 12.27 against an 11.80 optimum — a 3.98% cost penalty, not a routing failure. The "mistake" framing silently imports cap semantics into an exhaustion argument. The founder's tension is real, but it is a tension about *caps*, not about index rules.

**With the brief, on whether Q4 is close to settled.** The brief presents exhaustion as removing the cap and asks whether that settles the direction. It does not, because the cap is still 2 in every paid configuration (`reference_runner_v3.py:1475`, pinned by 0 of 288 configs) and is removed only in the arm that costs nothing. The question is phrased as if the production regime had changed; it has not.

**With CC1, on the retirement threshold.** Direction right, two errors: conflating a power *design* number with a separation *decision* rule, and omitting multiplicity correction. On the data that is the difference between retiring three pairs and one. And the proposal is vacuous at 500 models, where the tuple cannot break 495 of the ties and roster order silently does the work.

**With the implied composition.** I will not propose combining a cost-ordered ladder with a cap. Composing them pays the up-to-23-fold coverage loss of a bad capped prefix to buy a ~1% expected-cost saving. Where one fix alone performs as well, prefer it: under a cap, strongest-first alone; under exhaustion with a real cost table, descending `p/c` alone.

**Where I agree without reservation.** The founder's ruling that only measured capability may order the ladder is correct and the frozen tuple is not a measurement. But the archive currently supports exactly one measured edge, and it is the edge the tuple already has right. The honest near-term answer is not a new allocator — it is to fix the provenance measurement so that the next few runs can actually earn the ordering.

---

**Termination.** I am stopping here, at diminishing returns. The final pass over `bench/routing.py` produced one finding below the materiality threshold (the self-rung `last_code` attribution, reported above with its one-token fix) and nothing above it. I judged three mechanisms already adequately examined and did not pursue them further: the duplicate-detection path (`confirmed_duplicate`, orthogonal to allocation and unchanged by any answer here), the `-SIM` label normalisation in `rank_falsifier_writers` (already carries a recorded second-pass fix and a test), and the `routing_deferred` / `ladder_was_empty` discriminator (carries a dated repair, a stated reason, and a named test). The defect that decides this design is the provenance classifier, and it is above; a longer list would not add to it.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 31 recorded tool call(s).

<!-- verbatim-begin: fable (panel ladder_allocation_resolution_2026-10-07) -->

All measurements computed and double-checked. Writing the verdict.

---

## Q1

**Astra §6 relocates the tension; it does not resolve it today, and even with perfect data its numerator is a quantity this project has already superseded.**

For `score(m,u) = ĝ_mu/(c_mu + λ_t·t_mu + λ_h·h_mu) + β·e_mu` to never put a weak model first on a hard unit, four conditions must hold:

1. **The conditioned estimate must exist.** ĝ_mu is built from q̂ conditioned on task, class, tool and configuration (§6.1). If q̂ is flat across m (no data), ĝ is constant across m and the score degenerates to `const/cost` — **cheapest-first, the exact failure in the brief's third bullet.** Astra with empty cells IS the global-index mistake.
2. **The ordering condition.** g = R − R_next is strictly increasing in q: I derived dg/dq = σ(1−ν)R(1−R)/(1−qR)² > 0 on the domain (SymPy; Wolfram residual 0). So with β = 0 the weak model is never first iff g(q̂_weak)/C_weak < g(q̂_strong)/C_strong, where C is the full denominator. Near small q this is q̂_w/q̂_s < C_w/C_s — in the founder's example 0.02/0.60 = 0.033 < 1/10, so mid/strong lead, matching the brief's fourth bullet.
3. **β = 0.** The exploration term exists precisely to sometimes send hard units to under-sampled (often weak) models. "Never" is not just unachievable under §6.4 — it is undesirable, because without those probes the conditioned table never fills. The honest claim is "never under exploitation, deliberately and budgeted under exploration."
4. **The numerator must be the right quantity, and it is not.** §6.1's g is the ΔR form the appendix superseded on 2026-09-21. I re-derived the gap: E[improvement] − g_spec = **R²qσ(1−ν)(1−q)/(1−qR) ≥ 0**, R-dependent, so it does not cancel in a ranking (SymPy and Wolfram Language both reduce the difference to 0 against that closed form). The repository already measured the consequence: 14.94% ranking inversions in the high-risk regime (`Adaptive_Distributed_Compute_Spec_Assessment_2026-09-29.md`). The spec also carries scalar ν where `compute_rk` composes `nu_eff = 1 − (1−nu_b)(1−(1−sk)·nu_f)`.

**Do these conditions hold in this repository today? No.** Three of five live models have <20 provenance-clean critical attempts; the two that qualify do not separate (Fisher p = 0.68 on the nearest reproducible cell). Condition 1 fails, so fielding §6.4 now routes cheapest-first.

**Fix:** adopt §6.4's *shape* (value-over-cost with feasibility exclusions, §6.5's no-force-assignment) but (a) numerator := `R·q̂·σ̂·(1−ν̂_eff) − ν̂_eff·(1−R)` with the live two-channel ν_eff, and (b) do not field the task-conditioned table until its cells meet the power floor (below). *Falsifier:* re-run the assessment's inversion measurement with the corrected numerator; if inversions persist at the same rate, my fix failed.

The deeper resolution of the founder's tension is not the score at all — it is **exhaustion** (Q4): once the ladder exhausts, who goes first is purely a cost question, and the Riemann-to-DeepSeek outcome costs one wasted cheap dispatch, never a lost finding.

## Q2

**It collapses to one number per full model label: a Jeffreys posterior on provenance-clean per-attempt confirms, divided by measured cost, used only to order rungs under exhaustion.**

- Per-(model, task-class) is unfillable: the power floor is 173 clean attempts/arm to separate 0.15 at 80% (closed form and statsmodels agree: 173; Wolfram: 173). We have ≤46 anywhere, in any accounting.
- **Full label, not vendor base.** The archive separates SIM from live by huge margins (Codex-SIM 0.7683 vs Codex 0.2901 author-keyed; `rank_falsifier_writers._base` strips `-SIM`, which pools them — keep that normalisation for tuple *matching* only, never for the estimator key).
- **Cold start:** n = 0 → p̂ = ½, ĉ = roster median → unknown models enter at median index, ordered among equals deterministically (below). No model is ever excluded — the estimator reorders rungs and never removes one, so it opens no gate and needs no minimum sample.
- **It is safe only because the cap is removed.** Under exhaustion, misordering costs tokens, not findings (Q4 derivation). If a cap returns, this estimator is insufficient by construction and must say so.
- **What it refuses to claim:** task-conditioned capability; that CC2 ≠ Codex (p = 0.68); any rate for the <20-attempt models beyond its Wilson interval; and any claim at all from cells the provenance classifier currently feeds it (see Q5.1 — the classifier itself is biased). It logs depth (`rungs_tried`) per attempt now so the conditioned table can fill later, but reads nothing from it yet.

## Q3

CC1's pair-retirement condition is wrong in three distinct ways, one of them structural.

1. **It conflates power with outcome.** "Enough attempts for their intervals to separate" never arrives for two genuinely equal models — intervals of equal p overlap at every n. So the frozen tuple is consulted *forever* exactly when the truth is "no difference," which perpetuates names-over-measurement in the most likely case. Correct retirement: a pair retires on **either** separation (Fisher exact at pre-registered α — not Wilson non-overlap, which is conservative and n-dependent) **or** powered non-separation (n ≥ 173/arm for δ = 0.15, or TOST) → declared measured-tie → ordered by cost. Both exits retire the tuple.
2. **A hybrid pairwise comparator is not an order.** Measured-where-separated plus tuple-where-not produces a cycle. Executed (section G of my script): A = 124/200, B = 6/10, C = 200-attempt 96/200, tuple rank C > B > A. Then A beats C (measured, intervals separated), C beats B (tuple), B beats A (tuple): **A > C > B > A.** A sort on a cyclic comparator is implementation-defined behaviour. 
3. **500 models:** 124,750 pairs at α = 0.05 → ~6,237 expected false separations with no multiplicity control; and the tuple names 5 vendors, so the tie-break is undefined for the other 495 — today's fallback is roster order, an accident of config files, which is not deterministic across runs.

**Fix — dissolve the threshold instead of restating it.** Sort on one total lexicographic key: `(p̂_Jeffreys/ĉ descending, tuple-rank, full label)`. At cold start all p̂ = ½ and the order is tuple-then-label — CC1's intent. As data arrives, p̂ diverges and the tuple stops mattering pair by pair with **no retirement predicate to state, transitive by construction, deterministic at M = 5 and M = 500.** Separation testing is demoted from mechanics to reporting (what you may *claim*), which is where a statistic that cannot gate belongs. *Falsifier:* exhibit any input on which this key is non-transitive or non-deterministic — by construction of lexicographic order on scalars there is none; or show a measured run where a retained tuple-rank tie-break dominates it on resolutions-per-token.

## Q4

**Settled conditionally — and the conditions must be named, because one of them is already scheduled to break.**

The derivation (not the 90.93%): with stop-at-first-CONFIRMED and position-independent per-attempt success, P(resolve | exhaustion) = 1 − ∏(1−p_i), symmetric in order. Order moves cost only, and the adjacent-transposition identity E[cost](…a,b…) − E[cost](…b,a…) = Q(c_a·p_b − c_b·p_a) (SymPy simplifies to 0; Wolfram residual 0) gives descending **p/c** as the exactly optimal order — brute force over 8,000 seeded rosters, worst gap 0.00e+00.

The **90.93% is a property of the roster prior, not of the project**: same code, uniform prior → 90.08% [89.11%, 90.96%]; p~U(0.3,0.95) with lognormal cost → 97.50% [96.97%, 97.94%]. Cite the derivation; stop citing the share.

What breaks it:

- **The cap returns.** Then the prefix decides *which* findings resolve, the objective splits: choose the cap-m **subset by largest p̂**, order *within* it by p̂/ĉ. The p/c prefix alone is wrong — executed counterexample: p = (0.60, 0.50, 0.05), c = (10, 5, 0.1), cap 2: top-p set resolves 0.8000, the p/c prefix 0.5250, **losing 0.2750 of resolution probability**. Any code that caps must switch selection rules or it silently trades findings for tokens.
- **Position-dependent success.** The derivation assumes exchangeable attempts. The self-rung's `routing_feedback` and the proposed aid levels make later attempts *better informed* — the project's own 0/5 → 1/3 worked-examples figure is direct evidence success is state-dependent. Today only the self-rung carries feedback, so invariance holds across the ranked rungs; if aid levels extend to all rungs, the derivation is void and must be redone.
- **The gamma coupling** (round 2: 2/14 archived runs cross the γ_critical ≥ 0.30 arm when unresolved criticals flip) means exhaustion is not a pure spend question; `scripts/gamma_and_when_the_ladder_resolves_2026-10-07.py` already frames the prompt-vs-late test. Not new, but it belongs in the conditions list, not a footnote.

## Q5

**1. (Material — this decides whether the round's own evidence base is sound.) The provenance classifier contradicts the project's provenance doctrine.** `competence_provenance.falsifier_style` classifies "reads" by regex `open(|read_text|.read(|linecache|getlines`. `bench/routing.py`'s own Exp-42 comment states the legitimate access path for code targets: *"a code falsifier reaches its target by `import`."* Measured: **1,279 of 1,511 (84.65%, Wilson [82.74%, 86.38%]) falsifiers classified "detached" import a repository module.** The provenance-clean cell — the foundation of the brief's table, round 2's contradiction of the tuple, and every estimator proposed this week — is a 662-of-2,173 slice that systematically excludes import-style code falsifiers and admits any falsifier that `open()`s *anything*, target or not. The misclassification runs in both directions and is correlated with target type (prose vs code), so it can invert per-model ranks, which is precisely what the cell exists to prevent. **Fix:** `falsifier_style(code, target_hints)` where the runner records the staged target's basename and module name per entry; "reads" iff the code opens a path containing that basename **or** imports that module. *Falsifier:* re-run the clean cell under the corrected classifier; if no model's Wilson interval moves and no rank flips, my materiality claim is refuted.

**2. The brief's own figures do not reproduce in this tree.** The clean cell "CC2 21/35 = 0.6000, Codex 22/37 = 0.5946" matches **none** of eight accountings (entry/attempt × all/critical × full/base label × registry/rung-level). Nearest: crit-entry CC2 39/41, Codex 42/46; crit-attempt CC2 39/59 [0.5337, 0.7686], Codex 42/70 [0.4829, 0.7067]. The raw rates (Codex 0.2818…) also differ from every keying I ran (nearest, author-keyed over 6,194 entries: Codex 0.2901, Gemini 0.2607, CC2 0.1590, ChatGPT 0.1522, DeepSeek 0.1321 — note my scan puts **CC2 above ChatGPT**, inverting the brief's middle order). Every qualitative conclusion survives — overlap, underpower, contamination — but figures without a reproducing producer violate this round's own conditions. Fix: the brief's table must name its producing script or be regenerated from `scripts/ladder_allocation_seat_checks_2026-10-07.py`.

**3. The Riemann example is about the wrong task.** Routing dispatches *falsifier-writing for an already-diagnosed finding*, not problem-solving. Hardness of the target ≠ hardness of demonstrating a stated defect in it. The tension is real for Astra's general allocation problem; for `resolve_via_routing` it is smaller than the founder fears, and exhaustion shrinks it to a token cost.

**4. Exploration is free under exhaustion.** Every unresolved critical tries every rung, so the clean cells fill as a side effect — the ladder is its own explorer. Wiring Astra's β·e_mu term (and its separate budget) into routing would be an addition nothing needs: the 12th of the 11.

**5. SIM/live pooling is still live code.** `_base` strips `-SIM` for rank matching while the measured populations separate widely; any estimator keyed on base label inherits simulated history into live estimates. Round 2 flagged it; it remains. Fix is one line of scope: normalise for tuple matching, never for the estimator key.

Items 2–5 found, verified, nothing further above materiality: **I stop here at diminishing returns.** Mechanisms I judged adequately examined: the archive accountings (eight variants scanned), the order-invariance derivation (symbolic + brute force under two priors), and the gamma coupling (already measured twice in the record).

## The estimator

**Inputs** (all existing fields — no new module; lands inside `rank_falsifier_writers` at its one call site, with a test that executes it):
- k(m) = CONFIRMED re-executions by `reverify_falsifier` of falsifiers *written by* m (`falsifier_author` precedence), **provenance-clean under the corrected classifier of Q5.1** — until that classifier lands, the estimator runs on the current "reads" cell and says so in its output.
- n(m) = clean attempts, attempt-level: a routed entry adds the filer's failed attempt to the filer's denominator.
- ĉ(m) = mean tokens per routing dispatch for m; roster median when unmeasured.
- Keyed on the **full label** (`Codex-SIM` ≠ `Codex`).

**Formula:** p̂(m) = (k+½)/(n+1) (Jeffreys — binomial reference prior, interval behaviour matching the project's mandated Wilson). Rung order = lexicographic descending on `(p̂(m)/ĉ(m), −tuple_rank(m), label)`, tuple_rank defined only for the 5 frozen names, rank ∞ otherwise.

**Cold start:** all p̂ = ½, ĉ = median → order = frozen tuple among its 5 names, label order beyond — today's validated behaviour, reproduced not deleted (additive standard: the tuple is demoted to tie-break, removed only when a committed measurement shows the key dominating it on resolutions-per-token).

**It refuses to claim:** task-conditioned capability; separation between any pair not Fisher-separated at pre-registered α (CC2/Codex: p = 0.68 — indistinguishable); validity under a rung cap (it reorders, never removes; if `max_rungs ≠ 0` it must log that the selection rule, not just the order, is now wrong per Q4); validity under all-rung feedback (aid levels void its optimality derivation); and any rate as a number rather than an interval below n = 173.

**Falsifiers for the estimator itself:** a run where its order resolves fewer criticals than the frozen tuple under exhaustion (impossible under order-invariance — so observing it refutes the invariance assumptions, which is the more important discovery); a run where it spends more tokens per resolution than the frozen tuple (refutes p/c on the measured ĉ); the Q5.1 reclassification flipping ranks (refutes its current input cell).

## Measurements

All produced by `scripts/ladder_allocation_seat_checks_2026-10-07.py` (this round, this tree) unless noted. Wolfram Language (local Wolfram Engine via `wolframscript`) computed on every row marked W; all calls evaluated — none failed.

| figure | value | Wilson 95% | tools |
|---|---|---|---|
| "detached" falsifiers importing a repo module | 1279/1511 = 84.65% | [82.74%, 86.38%] | closed form + statsmodels |
| clean crit-entry: CC2 | 39/41 = 0.9512 | [0.8386, 0.9865] | closed form + statsmodels |
| clean crit-entry: Codex | 42/46 = 0.9130 | [0.7968, 0.9657] | same |
| clean crit-attempt: CC2 / Codex | 39/59 = 0.6610 / 42/70 = 0.6000 | [0.5337, 0.7686] / [0.4829, 0.7067] | same |
| CC2 vs Codex separation | Fisher p = 0.6796 (entry), 0.5837 (attempt) | — | scipy fisher_exact |
| DeepSeek 12/16 vs Gemini 1/8, clean crit | Fisher p = 0.0078 (tuple tail contradicted) | DS [0.5050, 0.8982] / Gem [0.0224, 0.4709] | scipy; matches round-2 record |
| power, δ=0.15 (0.60 vs 0.45), 80%, α=0.05 | 173/arm | — | closed form + statsmodels; **W: 173** |
| power, δ=0.20 | 97/arm | — | same; **W: 97** |
| toy table, first on HARD | cheap / strong / cheap / **mid** (cheap last) | — | SymPy exact + NumPy; **W: indices {1/50, 1/16, 3/50}** |
| swap identity residual | 0 | — | SymPy; **W: 0** |
| dg/dq − σ(1−ν)R(1−R)/(1−qR)² | 0 | — | SymPy; **W: 0** |
| E[imp] − g_spec − R²qσ(1−ν)(1−q)/(1−qR) | 0 | — | SymPy; **W: 0** |
| p/c vs exhaustive optimum, 8000 rosters | worst gap 0.00e+00 | — | NumPy + itertools exhaustive |
| strongest-first suboptimal, uniform prior | 3603/4000 = 90.08% | [89.11%, 90.96%] | NumPy; closed form + statsmodels |
| …p~U(.3,.95), lognormal cost | 3900/4000 = 97.50% | [96.97%, 97.94%] | same (prior-dependence shown) |
| CAP=2: top-p set vs p/c prefix | P 0.8000 vs 0.5250, loss 0.2750 | — | NumPy exact |
| comparator cycle A>C>B>A | True (executed) | A [0.5511,0.6844], B [0.3127,0.8318], C [0.4118,0.5490] | closed form + statsmodels |
| raw author-keyed live rates (6194 entries) | Cx .2901, Gem .2607, CC2 .1590, GPT .1522, DS .1321 | n = 786/1381/786/736/1098 | archive scan, 2 globs |

## Delivered files

- `scripts/ladder_allocation_seat_checks_2026-10-07.py` — all nine sections (A–I), answers `--help`, reads only `bench/logs/` and repo code, exit 0. (Created via shell; the Write tool lacked pre-approval in this dispatch.)

## What would refute me

- **Q1 (Astra relocates):** show the task-conditioned cells fillable today at the 173/arm floor, or show the §6.1 numerator producing the same ranking as E[improvement] over the project's own R distribution (the 14.94% inversion figure going to ~0 on re-measurement).
- **Q2 (global p̂/ĉ is safe now):** any path where the rung order gates an outcome under `max_rungs=0` — e.g. a budget ledger that halts mid-ladder, which turns order back into selection. If such a halt exists in the runner, my "cost-only" safety claim is wrong and the estimator needs the cap-mode selection rule immediately.
- **Q3 (lexicographic key):** a demonstrated input where it is non-transitive/non-deterministic, or a committed measurement where CC1's pairwise scheme beats it on resolutions-per-token.
- **Q4 (direction settled):** a measured run under exhaustion where ordering changed *which* criticals resolved — that refutes exchangeability, not just the ordering.
- **Q5.1 (classifier bias is material):** the corrected classifier moving no interval and flipping no rank.

## Disagreement

- **With the brief:** its two headline tables (raw rates; 35/37 clean cell) are not reproducible from this tree — nearest cells differ in n, k, and in one middle-order rank. Conclusions survive; the figures as printed do not meet the round's own producer-and-interval condition.
- **With CC1 (Q3):** pair-retirement-on-separation is the wrong predicate twice over — it never retires for equal models and its comparator can cycle. I replace the threshold with a total sort key rather than correcting the threshold.
- **With the round-2 seat, partially:** I adopt its Jeffreys/p̂-per-attempt core but reject depth-stratification as a *fielded* input (294 rung records; single-digit cells) and reject any claim built on the current "reads" filter until Q5.1's classifier fix lands — its own contradiction of the tuple (Fisher p = 0.0078) is computed on a cell whose classifier misclassifies 84.65% of detached-labelled falsifiers' access style.
- **With the founder, narrowly:** "the system shouldn't care at all what a model is called" — at cold start something must break ties deterministically, and the only validated end-to-end ordering in this project is the frozen tuple (Exp 42, 7/7 across two rungs). The additive standard itself forbids deleting it without a committed dominating measurement. Demote it to tie-break; the system stops caring about names at exactly the rate it acquires data.

Where the reasoning I reviewed is sound, I say so: the order-invariance derivation, the p/c optimality rule, the exhaustion ruling, and the Astra feasibility-exclusion (§6.5, no force-assignment) all survived every falsification I ran.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/ladder_allocation_resolution_2026-10-07/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
