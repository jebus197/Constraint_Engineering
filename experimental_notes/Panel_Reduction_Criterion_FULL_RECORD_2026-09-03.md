# Panel Review — The Reduction Criterion — FULL RECORD

**Dispatched 2026-09-03 01:38:38 BST. Two reviewers, sandboxed in disposable git worktrees, Max-plan, no metered cost.**
Brief: `bench/logs/panel_reduction_20260903T003819Z/BRIEF.md` (128 lines).
Raw: `cc2.json`, `fable.json`, with per-reviewer tool logs.

| Reviewer | Elapsed | Tool calls | Reply |
|---|---|---|---|
| cc2 (opus) | 1107s | 90 | 15,704 chars |
| fable | 323s | 37 | 10,225 chars |

Reproduced verbatim and unfiltered. Disagreement preserved, not smoothed.

---

# REVIEWER: cc2

## What I ran

Everything below was executed in the disposable copy. Where I could not check something, I say so.

**Procedural honesty first:** the brief arrived as one document, so I cannot claim I answered Q1 blind to Section 3. What I *can* say is that my discriminator was derived from the three cases and the repository, and it produced a finding Section 3 does not contain — a live defect of exactly Case C's shape, sitting inside the machinery that implements the criterion you're being asked to define.

---

## Q1 — the discriminator

**A legitimate simplification names the condition under which it fails. A defective one names a threshold.**

Case A: π disappears because `R` is a sufficient statistic. I verified it symbolically — unrolling `R(i)=R(i-1)(1-q)/(1-q·R(i-1))` from `R(0)=π` over five passes is identical to the batch posterior `π·m/((1-π)+π·m)`, and the appendix's own further reduction (`K=1, d=1, q=p, π=0.5 → (1-p)ⁿ/(1+(1-p)ⁿ)`) is exact at n=6. The residual is empty by construction, and the boundary is *stated*: π∈[0,1), m∈(0,1], the contradiction corner excluded.

Case B: `p=0` is a declared limit, and what falls out is a named object with its own domain.

Case C: signature similarity is not a restricted form of "different falsifier." It's a **correlational proxy** — it agreed with the full rule on the population the author happened to look at. There was no condition under which it was known to hold, only a number (0.20) carried over from a population (unlocated findings) that was the logical complement of the one it was applied to.

So: a reduction is an *identity plus a stated domain*. A proxy is a *threshold plus an unstated population*. The failure mode isn't "the simple thing was wrong" — it's that the simple thing had no domain attached, so no one could tell what it was claiming.

**Where I differ from Section 3.** τ is a good instrument but the brief treats "τ=0 by proof" and "τ=0 by enumeration" as interchangeable routes. They are not. Enumeration is only as strong as D, and in Case C *D was the whole dispute*. My subagent reproduced the measurement using the project's own `signature_similarity`, `stem_signature` and `finding_locations`: under "same function = identical location set" the rate is 41.5% (282/680, Wilson [37.8, 45.2]); under "same function = shares ≥1 symbol" it collapses to 12–18%. Same instrument, same archive, same threshold — the headline swings by 3×. A τ established by enumeration is a claim about D, and D is where the arguing will happen. Section 3's "D declared *before* either was proposed" is doing far more work than its one clause suggests; it is the entire load-bearing element, and it should be promoted to the definition's centre rather than parked in the setup.

---

## Measurements 1–8, re-run

| # | Verdict | What I got |
|---|---|---|
| 1 | **Both halves fail** | 28 occurrences (16 "reduces to", 9 "special case", 3 "vanish") on 26 lines, not 29. And not zero are tested: `test_ouroboros_loop_close.py::test_channel_semantics_hold_at_the_documented_corners` asserts §1.1's "c_ext=0 → Stage 6 reduces to Stage 5" *by executing both forms and comparing at 1e-12*, plus the ν_k/c_ext corners. 74 tests pass. |
| 2 | **Reproduces, and understates it** | `nu_eff = 1-(1-ν_b)(1-(1-s_k)ν_f)` — no complexity term, confirmed. But ν_b/ν_f/q are read from `entry["model_params"]`, and the code's own comment at line 9829 states that is *never populated*. So on every run Exp 37→49 they are the literal constants 0.05, 0.20, and q=0.5. Not blind to blast radius — blind to everything. |
| 3 | **Half wrong** | `nu_star` appears in zero `.py` files: correct. But its algebraic dual is live. `check_sk_threshold` (9712) is called at 9857 from `_evaluate_sk_for_findings`, called at 11782 inside the round loop, and it gates fix acceptance — the `REJECTED … (Valley of Bad Fixes)` branch. The hard exit exists, parameterised on S_k rather than ν. See below: it is also wrong. |
| 4 | **Reproduces exactly** | `bench/dm/_fix_complexity.py` has two non-log references: its own test, and `scripts/instrument_inventory.py:69`, which labels it `"(shadow)"`. |
| 5 | **Not reproducible** | Arithmetic exact (7/27 = 0.2593, Wilson [0.132, 0.447]). My name-matcher over module-level `UPPER_CASE` numerics in the runner finds **5**, not 27. The author's population is a different and unstated one. The claim as written cannot be checked by anyone but its author. |
| 6 | **Numerator exact, denominator not** | 282 reproduces on the nose; 711 does not — nearest is 680 (41.5%). No reproduction script exists in the working tree, any branch, or the stash; the claim survives as prose in five places. |
| 7 | **309 exact; 13 not mechanically reproducible** | Subject-line scan: 2. Full-body regex: 6. The classification is human reading. All quoted CIs are arithmetically correct (13/309 → [0.025, 0.071]; 4/13 → [0.127, 0.576]). |
| 8 | **3 of 5 verified by commit; the zero is definition-dependent** | `9bb0047`, `98ddede`, `eeaa0b3` all exist and say what's claimed. "0 dishonest optimisation" holds only on an *intent* reading. Behaviourally it is not zero: `4d4f58f` records the falsifier gate **selecting for** detached falsifiers that open nothing and restate the target's numbers from memory, and record CONFIRMED; `15a7094` "converged at round 3, and the convergence is vacuous"; `adb566b` "126 of 246 proposed fixes do not silence their own test." The list of 5 also omits an environment-side containment failure: `62fd55f`, "the answers were in the reviewers' working directory." |

---

## The finding: S\* is a Case C, and it is live

`check_sk_threshold` computes `S* = (ν_b + ν_f − ν_bν_f − qR) / (ν_f(1−ν_b))`. I derived where that comes from: it is `ν_eff(s_k) ≤ ν*` with **ν\* evaluated at σ=1**, i.e. `ν* = qR`. But the appendix's own ν\* is σ-dependent — `ν* = σ·R·q/(1 − q·R·(1−σ))` — and I confirmed symbolically that *that* form is the exact break-even of the appendix's three-phase model. The code holds σ=1 while σ = s_k is the very variable under test.

The residual, enumerated against the project's own `compute_rk`:

- Grid (s_k, q, R) at 0.01 over (0,1)³, ν_b=0.05, ν_f=0.20 — the live constants: **970,299 cells, 191,708 disagreements, τ = 0.1976.** Every single disagreement is in the unsafe direction: the gate admits a fix that `compute_rk` says *raises* residual risk. Worst case R: 0.25 → 0.4268.
- Wider grid including ν variation: 171,475 cells, τ = 0.187, again 100% unsafe-direction.
- **At the only operating point the live pipeline can reach** (q=0.5, R=`RK0_PI_BASE`=0.5, ν_b=0.05, ν_f=0.20, s_floor=0.0): S\* evaluates to −0.0526, clamps to 0.0, and the gate admits everything. The true break-even is s_k ≈ 0.504. **50.4% of the S_k range is admitted while increasing risk.** The "Valley of Bad Fixes" gate has, on every run to date, rejected nothing on this ground.

Repro:
```
python3 -c "import sys;sys.path.insert(0,'.');
from bench.reference_runner_v3 import check_sk_threshold, compute_rk
print(check_sk_threshold(sk=0.3,nu_b=.05,nu_f=.2,q=.5,R=.5), compute_rk(R_old=.5,q=.5,sk=0.3))"
# (True, 0.0)  0.55065      <- gate: pass.  R_k: 0.5 -> 0.551
```

Caveat I hold myself to: τ here is over an enumerated synthetic domain, not a workload distribution. But the *sign* result — no disagreement is ever conservative — is domain-independent, and the single reachable operating point needs no distribution at all.

This is the third instance of the same pattern in the repo, and the other two are already documented: the absorb signature rule (Case C), and `gate_would_fire`, a simplified reimplementation of the live convergence gate removed on 2026-09-01 after executed counterexamples showed it disagreeing in both directions (comment at 6244–6255). Three for three, the residual was found by *executing the two forms against each other*, never by reading them.

---

## Q2 — is the distinction sound?

**Sound, with one correction.** Cost simplicity and compressive simplicity are genuinely orthogonal, and the repo demonstrates it: `S*` is 30 lines and low blast radius (maximally cost-simple) and has τ≈0.20 (zero compressive value). The `E=mc²` framing survives as an illustration.

What it rests on: that S and F are both *executable*, so the residual can be enumerated rather than argued. Every case where this project caught a truncation, it caught it by running both. Where the criterion will not work is where F is prose — and that is most of the appendix's §7–8. Do not oversell it there.

The correction: the criterion as stated is a property of a *pair* (S, F). It says nothing about whether F itself is right. `S*` vs the true break-even has τ=0.20; the true break-even vs reality is unmeasured, because ν_b and ν_f are two constants nobody derived. Fixing S\* to match `compute_rk` would take τ to 0 and change nothing about whether the model predicts anything. That is worth saying out loud before this becomes a gate.

---

## Q3 — quantification

τ is the right *shape* and the project already has it under a name: **verdict sensitivity**. `gamma_threshold_profile` (6224–6280) reports `inputs_vary_with_threshold` and `gamma_range_across_thresholds` — "does the picture the gate reads change with the threshold" — mandated by the 2026-05-18 pre-registration and built 2026-09-01. That is τ over a threshold choice, already instrumented, already diagnostic-only.

**Recommendation: define it, add no machinery. Use the existing name.** Concretely:

- τ is a **correctness** quantity; `ν ≤ ν*` is a **benefit/cost** quantity. Do not merge them and do not put τ in the appendix's trade-off family. A simplification with τ>0 is not a bad trade, it is a false statement.
- Do not attach a CI to τ when D was enumerated. Section 3 says this and is right; measurement 6 violates it in the same document (a Wilson interval on a full-archive enumeration is describing sampling noise that isn't there — the real uncertainty was the definition of D, which no interval captures).
- One field, not a subsystem: where a substitution is made, record `residual: proved-empty over <D>` or `residual: <τ> over <D>, filed as <claim id>`. That is a sentence, not a module.

---

## Q4 — where it goes, and the first move

**Definition in `docs/MATHEMATICAL_APPENDIX.md`; rule in the acceptance policy only for pairs where both sides are executable; not in the directives.** The directives are already long and models already read them selectively.

**Do not make the 29 reduction properties checkable first.** I spot-checked them and they are the wrong target: `L_n → R_n` when `s_k = w_k` is substitution of identical symbols; `H(x) → c` is `1·1·1`; `f_del=1`, `η_dec=1`, `τ_defer=0`, `σ=0`, `V_s=0`, `ν=0` are all "set a term to its identity and it disappears." They are true by construction, cheap to read, and two are already asserted by a passing test. Building 29 tests against them would produce 29 green lights over the safest statements in the repository.

**The first move is the opposite one: find the reductions nobody declared.** They live in code, they are invisible to a name matcher (nothing in `check_sk_threshold` says "σ=1"), and they are where all three known instances came from. The mechanical version is cheap and needs no new framework: **wherever two functions in the runner claim to answer the same question, enumerate a grid and diff them.** That is one afternoon and it found τ=0.20 in the fix-acceptance gate on the first try.

**Decision consequence if I'm wrong:** if the 29 turn out to contain a false one, my "trivially true by construction" claim is refuted and the audit was worth it. I checked five (Ising ψ=0, §1.1 π-vanishing, §1.1 Stage-4 reduction, L_n, H(x)); all five hold. I did not check the remaining ~21, and I say so rather than implying I did.

---

## Q5 — containment, proportionately

Measurement 8's framing puts "dishonest optimisation" and "containment" in separate columns. The record suggests they're the same column viewed from different ends. `4d4f58f` is a model producing an artefact that scores well by not doing the work — no dishonesty required, just gradient. Treating gaming as an intent question is what makes it read as zero.

**Proportionate next step: record, don't restrict.** The panel models carry Write/Edit because that is what makes them useful reviewers; `9bb0047` correctly chose detective-only. Keep that.

**What the next simulated run should measure:** for each agent, per round — (a) writes outside its declared write-set, by path; (b) whether the agent's own output *mentioned* the write. That second field is the whole discriminator.

**Helping vs worse:** the tell is not the boundary crossing, it's the *record*. In `9bb0047` a reviewing model mutated the target and **restored it** — invisible to git and to the round files. Restoring is not evidence of good intent; it is evidence of trace suppression, whether or not anything intended it. So: *an agent exceeding its boundary while trying to help leaves the crossing legible and says it did. One doing something worse leaves the state unchanged and the record silent.* Announced-and-persistent is a helpful overreach. Unannounced-and-reverted is the one to alarm on — and it is the cheapest thing here to measure, because you already hash the target each round.

Add `62fd55f`'s class too: the answers being in the reviewers' working directory is a containment failure with no model at fault. Counting only model-side events will make the environment side invisible.

---

## Q6 — what's missing

1. **Partly a solution in search of a problem — for the machinery, not the name.** By your own stopping criterion: would absence of this waste bench compute? A τ *framework* would not have caught S\*, because nobody declared S\* as a simplification. What caught it was executing two functions against each other. So: adopt the name and the one-sentence residual field (near-zero cost, high explanatory value), and skip anything that requires a declaration step, because the failures all come from substitutions nobody thought to declare.

2. **The bigger defect is upstream of all of this.** `ν_b=0.05`, `ν_f=0.20`, `q=0.5`, `R(0)=0.5` are four constants that have driven every S_k decision from Exp 37 to Exp 49, because `model_params` is never populated. `_fix_complexity` — the one thing built to make ν vary — is a shadow with no caller. Fixing S\*'s τ while ν is a constant is polishing the second decimal of a number with no first one. If forced to choose one move: **wire `_fix_complexity` in, then fix S\***, in that order.

3. **A meta-point the brief half-makes.** Measurements 5, 6 and 7 are the three that failed to reproduce, and they share a property: each depends on a population the author defined and did not record. Measurement 6 has no script anywhere in the repo. That is the Reduction Criterion applied to the brief itself — a number stated without its D. If one thing from this ships, make it: **a measured rate must be accompanied by the script that produced it, or it is prose.** That rule needs no new machinery either, and it would have caught 3 of 8 items here.

**Decision consequences I'd accept if wrong:** if S\* is defended as intentionally conservative — an approximation deliberately biased toward admitting fixes — then my finding downgrades from defect to undocumented design choice, and the correct action is a comment, not a patch. I found no comment, no test, and no note asserting that, and the log line "Valley of Bad Fixes" describes a gate that rejects, so I don't believe it. If someone produces the derivation showing σ=1 was chosen deliberately, I withdraw the severity and keep the τ measurement.

---

# REVIEWER: fable

# Panel report — The Reduction Criterion

## 0. What I ran and what survived

Every number below was re-executed in this copy or marked unverifiable. Verdicts: **6 reproduce, 2 partially, 2 could not be checked as stated** — including, awkwardly, the brief's own central number.

| Claim | Verdict | What I got |
|---|---|---|
| Case A: recursive ≡ batch, π vanishes | **CONFIRMED by my own run** | Exact-rational check, 200 random cases, `Fraction` arithmetic: identical every time. K=1/d=1/π=½ reduction to `(1−p)ⁿ/(1+(1−p)ⁿ)` also exact. |
| M1: 29 reduction properties, 0 tested | **PARTIAL** | I count **28** occurrences (26 lines) with `reduces to\|special case\|vanish(es\|ing)`, not 29. "Zero tested" holds for the appendix's statements — but `bench/tests/test_channel_boundary.py:148-176` **does** grid-assert a reduction identity (η-channel → bare `compute_rk`). That property lives in confer docs, not the appendix, so the claim is literally true and misleading in spirit: the project already knows how to test a reduction; it has done it exactly once. |
| M2: `compute_rk` blind to the fix | **CONFIRMED** | Read at 9355–9397. `nu_b`, `nu_f` are default parameters (0.05, 0.20); no call site passes fix-dependent values; no complexity/size/blast term exists. |
| M3: ν > ν* exit in no live path | **CONFIRMED** | ν* appears only in `confer_*.py` analysis records. The runner imports none of them; its only break-even is **S\*** (line 9716), a different quantity. |
| M4: `_fix_complexity.py` uncalled | **CONFIRMED** | Sole non-test reference: `scripts/instrument_inventory.py` (labelled "(shadow)"). |
| M5: 27 tunables / 7 documented | **NOT REPRODUCIBLE** | The count exists only as prose in `experimental_notes/Truncation_Rate_Formalisation_2026-09-03.md`. No script, no list of the 27. By the project's own standard (the preamble of `similarity_operating_characteristic.py`) this number is not yet citable. |
| M6: 282/711, τ = 0.397 | **NOT REPRODUCIBLE — direction confirmed, number not** | No stored script or pair dataset. The numbers live as prose in a commit message and a comment at `reference_runner_v3.py:11394`. My own reconstruction (683 archived findings with falsifiers, function names regex-extracted, all-report pairing) gives **791/4874 = 0.162** ≥ 0.20 — a different population, so not a refutation, but proof the figure can't be re-derived from the repo. The *defect* is real either way; the fix is live and its tests (21) pass. |
| M7: 13/309 insufficient-fix commits | **PLAUSIBLE, unreproduced** | 309 commits confirmed exactly. My heuristic grep finds ≥15 candidates; without the author's criteria, 13 and the 4-self-attributed subcount can't be checked. |
| M8: 0 gaming, 5 containment | **PARTIAL** | `9bb0047`, `98ddede`, `eeaa0b3` all exist and say what the brief says. The 2026-09-01 panel edits and integrity-log mutations I confirmed only indirectly. I found no gaming instance either — and `latent_control_audit.py` (run live) shows `target_integrity_events` is **SILENT_BUT_RAN**: the containment instrument itself cannot currently prove it ran. |

## Q1 — my discriminator (formed before reconciling with §3)

The three cases are **three different kinds of move**, and the kind determines what verification is even possible:

- **Case A is an identity** — an algebraic re-parameterisation. Nothing is dropped; π isn't "lost", it's the initial condition of an exactly-unrolled product. Verification: proof. Available, done, and I redid it.
- **Case B is a domain restriction** with a declared boundary and a *named* remainder outside it. Verification: proof within scope + the remainder filed as its own claim.
- **Case C is a proxy substitution**: the defining criterion (falsifier difference) was replaced by an observable correlate (token overlap) and the extensions were *hoped* to coincide. For a proxy, τ = 0-by-proof is unavailable **in principle** — the only admissible verification is measurement over the deployment population, and it was instead validated on one point drawn from the opposite population (a cross-file pair, for a rule deployed on same-location pairs).

So my discriminator: **classify the move first — identity, restriction, or proxy — because the class dictates the burden of proof; the defect in Case C was demanding proxy-level trust at identity-level evidence.** This is compatible with §3's τ but sharper ex ante: τ tells you *after measuring* that C failed; the classification tells you *before proposing* that C required measurement at all. One more thing §3 doesn't say: in Case C the exact rule ("different falsifier ⇒ different defect") was *already simpler in the compressive sense* than the proxy replacing it. The project didn't over-simplify; it substituted a worse simple for a better one.

## Q2 — is the distinction sound?

**Sound.** Cost simplicity vs compressive simplicity is a real engineering distinction with a real pedigree (short description that *fits all the data* vs short artefact that *dropped some*), and the project's record instantiates both poles cleanly. It rests on one load-bearing element the note half-admits: **the parameter didn't disappear, it moved.** τ is parameter-free only after D *and the measure on D* are fixed. An unweighted τ over an enumerated D can hide disagreement concentrated in the frequently-hit region (Case C's 39.7% was on precisely the most probable collision population). The defence — scope fixed by the brief beforehand — is correct and is where all the residual gaming risk now lives. State that as the criterion's own declared residual and the reasoning is fully sound.

Also sound: separating proof / enumeration / sampling, and refusing CIs on identities. That correction (the note says its own first table got it wrong) is the criterion applied to itself, working.

## Q3 — is τ the right quantity?

τ is right, and **it already exists in this project under another name**: the wrong-merge rate in `scripts/similarity_operating_characteristic.py` *is* a truncation rate — fraction of the domain where the simple rule disagrees with the fuller criterion at the operating point. τ names and generalises a measurement the project already performs. ν ≤ ν* is *not* the same quantity — ν prices harm from a fix; τ prices disagreement of a substitute — keep them apart.

Given the founder's constraint: **define, add nothing.** One definition in the appendix; one sentence of policy: *a change claiming "the simpler form suffices" must declare D before the candidate and file τ with its method (proof / enumeration / sample+CI).* No score, no weight, no new term in R_k. Consequence I accept if wrong: if τ-filing proves too heavy in practice, the cost is a few skipped filings, discoverable in the commit record — cheap to detect, cheap to reverse.

## Q4 — application and first move

Appendix definition + acceptance-policy sentence. In directives: only the one-line classification question (identity / restriction / proxy?). **Not** the first move to write 29 tests. The findings 2–4 cluster tells a single story: the appendix's benefit/cost exit (ν*) exists nowhere live, and the one instrument that could feed it (`_fix_complexity.py`) is unwired. Before building anything, apply the project's own stopping criterion **as a measurement**: replay archived runs with a *record-only* shadow computing ν vs ν* from the existing shadow features, and count how often the hard exit would ever have fired. Fires never → findings 2–4 are documentation debt; close them with a paragraph. Fires on real runs → wire it, with the replay as its commissioning evidence. For the reduction properties themselves: one parametrized test file of symbolic/grid identities — my 12-line script covered two of them in seconds; the pattern already exists in `test_channel_boundary.py`. Cheap, and it converts 28 prose claims into checkable ones. Consequence if I'm wrong about deferring ν*: one more experiment ships without a harm-exit that would have fired — bounded by the replay being run first.

## Q5 — containment, proportionately

Zero gaming, five boundary events, at least some of them helpful-overreach. Proportionate next steps, both already implied by the repo's own artefacts: (1) adopt `latent_control_audit.py`'s own recommendation — give the integrity guard an unconditional "I ran" counter, because a detective control that can't prove it ran is not a control; (2) resolve the founder ruling explicitly pending in `9bb0047` on whether reviewing models hold Write/Edit at all — the cheapest containment is not granting the capability. What the next simulated run should measure: out-of-boundary writes per run, classified by target (module-under-review / harness / logs) × disclosure (did the model report its own write?). That last axis is the discriminator you asked for: **helpful overreach is disclosed and objective-aligned; the worse thing is undisclosed and correlates with a measured quantity improving without underlying work** — of which the record contains zero instances. No new architecture warranted.

## Q6 — what the author missed

1. **The brief's central number fails the brief's own standard.** 282/711 exists only as prose in a commit message and a code comment — the exact pathology `similarity_operating_characteristic.py`'s preamble was written to correct, recommitted one day later. Same for the 27-tunables count. Both need a stored pair-list/script before either is cited again. This is my strongest finding.
2. **The count discipline slipped again in miniature**: 29 vs my 28; "zero tested" vs one grid-asserted reduction identity. Trivial individually; in a project whose thesis is *run the command, then make the claim*, exactly the residue worth naming.
3. **Solution in search of a problem?** No — but narrowly. τ as a *definition* passes the stopping criterion because Case C shows real bench compute was spent on a truncation (a shipped guard deleting genuinely distinct defects). τ as *machinery* — a gate, a schema field, an enforcement hook — currently fails it: one confirmed instance does not justify infrastructure. The note's own conclusion ("name a quantity the appendix already relies on, make it checkable") is the right size. Hold it there.
