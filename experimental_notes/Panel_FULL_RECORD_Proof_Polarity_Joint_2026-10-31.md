# The proof polarity joint round - confirmed but latent, with the reach disputed

Record written 2026-10-31T05:11:33+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

CC1's synthesis of this round, written as the operator and participating with its own position.

BOTH SEATS MOVED AND BOTH NOW RETURN CONFIRMED BUT LATENT. The inversion at spec_verification_factor is established by execution from both directions: a held proof scores 0.0 and a failed proof scores 1.0, which is the sign exactly backwards. fable confirmed it by building 2 real proof artefacts against bench/tests/fixtures/stem/docs/MET-12-REF-01.md and driving them through the real reverify_falsifier, having entered the round holding NO GAP.

THE DISAGREEMENT THAT REMAINS IS ABOUT REACH AND IT IS GENUINE. cc2 measures the inversion as LIVE in 18 of 65 archived registries for REPORTED convergence and 0 for release safety, the A4 blocker count holding 3 of 3 under execution. fable refutes the amplification claim outright: 0 archived rounds would have converged earlier, because the severity channel sits behind a flag never armed in any archived run and the gamma pathway cc2 named does not exist in the code. These are not the same measurement and both seats executed. CC1 does not adjudicate between them, because this project does not accept a model vote as evidence and the question is settled programmatically or by the founder.

WHAT IS AGREED AND IS THE USEFUL PART. The repair is option (a), make the sense explicit, and fable established that (a) as cc2 shipped it is HALF of (a): falsifier_verdict has 2 deciding consumers, spec_verification_factor for severity and apply_falsifier_verdicts for status. cc2 guarded the first. fable applied cc2's fix verbatim, executed, and found the second unguarded. A declaration is only a repair if every deciding consumer honours it, which is the sharpest sentence either seat wrote tonight.

CC2 ALSO CORRECTED ITS OWN STATED MECHANISM, which is worth more than the verdict. Its round-1 claim routed the hazard through effective_severity. Driving the real gate end to end showed that _settled_novelty_series reads entry severity, the ASSERTED number, and never calls effective_severity at all. So the route cc2 named was not the route, and cc2 said so.

WHY THIS SPLITS CLEANLY FOR THE FOUNDER, AND IT IS THE REASON THIS ROUND WAS WORTH RUNNING. cc2 states plainly that its own fix touches spec_verification_factor, which is the severity ruler he has defended against 4 separate proposals, so that half is his. fable states that its fix touches neither gamma nor the convergence gate -- _estimate_gamma, _settled_novelty_series, _check_gamma_alt_convergence, CRITICAL_SEVERITY_THRESHOLD and the historical verdict-to-V mapping all unmodified -- and adds 1 branch inside apply_falsifier_verdicts entered only when an entry declares proof polarity. So the STATUS half may be buildable without touching the ruler, and the SEVERITY half needs him. That is a narrower decision than he was facing before this round.

CC1's OWN POSITION. I wrote the brief that framed this as a missing step and both seats refuted that in round 1; I withdraw it without reservation. On the repair I argued for (a) over (b) on the grounds that splitting the channel changes every archived comparison while an explicit sense changes none. Both seats agree with (a) and fable has shown my framing of (a) was incomplete, which I accept: I described the declaration without asking which consumers must honour it, and that question is the whole of whether a declaration repairs anything.

NOTHING IS FOLDED BACK. 7 seat-written files are preserved under experimental_notes/seat_evidence/, per his ruling that an emerging fix is tested with analysis, the 5-step cycle and the full tool set before it reaches the runners.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# JOINT PANEL BRIEF — what a proof is outside code, round 2. YOU BOTH REFUTED THE BRIEF.

**This is the JOINT half of `what_is_a_proof_outside_code_b22_2026-10-30`.** That
round was BLIND. Both seats have answered, both refuted the brief's central
premise, and both replies are reproduced in full below so this round is exposure
rather than a pointer at a file.

**NO COMPELLED CONVERGENCE.** A seat that reads the other and does not move has
done its job, provided it names the specific claim it rejects. A seat that moves
has also done its job, provided it names what moved it. Splitting the difference
without engaging a claim is the one unacceptable answer.

## THE BRIEF WAS WRONG AND THAT IS SETTLED — DO NOT SPEND THIS ROUND ON IT

The brief asserted that step 4 of the founder's pipeline, the harness
re-verifying a printed proof, *"is the one that does not exist yet"*. Both of you
established by execution that it does. fable traced steps 1 to 3 onto the
model's standing runnable-falsifier obligation and step 4 onto
`bench/falsifier_verify.reverify_falsifier`, which decided every artefact it was
given. cc2 agreed the machinery is present. **CC1 wrote that premise and
withdraws it.** The reason it looked true is recorded so neither of you need
re-derive it: I searched for a step that reads a PROOF, and `reverify_falsifier`
is named for the FALSIFIER direction, so not finding the word I concluded the
mechanism was absent.

## WHERE YOU ACTUALLY DIFFER, WHICH IS NARROWER THAN YOUR LABELS

fable answered the question AS ASKED — is step 4 missing — and returned NO GAP.
cc2 answered the question the founder was reaching for — can the pipeline carry
a proof SAFELY today — and returned GAP ELSEWHERE. No fact appears to be in
dispute between you. **This round must establish whether that reading is right,
or whether there is a real disagreement the labels are hiding.**

## CC2's FINDING IS THE SUBJECT OF THIS ROUND

Its claim, which fable has not yet seen: a proof and a falsifier are the same
artefact under OPPOSITE TERMINAL CONVENTIONS — a falsifier succeeds by
demonstrating a defect, a proof succeeds by failing to — they share one field,
and the sense is implicit in the field rather than carried by it. So routing a
proof through `spec_verification_factor` INVERTS severity, and cc2 reports that
across rounds this MANUFACTURES APPARENT CONVERGENCE.

**THE 4 THINGS THIS ROUND MUST ANSWER.**

  **Q1. Is the polarity claim correct?** fable: attack it directly. Construct a
  proof artefact, route it through `spec_verification_factor`, and report what
  severity comes out and what the gate then does. If the inversion does not
  occur, say so with the execution that shows it. cc2: state the single
  strongest reason your own claim might be wrong, and test that reason.

  **Q2. How far does it reach?** cc2 reports apparent convergence across
  rounds. Quantify it: how many archived rounds would have converged earlier,
  and by how many rounds. If the answer is 0 archived rounds, the hazard is
  real but latent, and that distinction matters for how urgently it is repaired.

  **Q3. Which repair?** 2 candidates. (a) Make the SENSE EXPLICIT — add a field
  naming the convention, leaving the existing verdict field untouched. (b) SPLIT
  the channel — separate proof verdicts from falsifier verdicts. CC1's position
  is (a), because (b) changes every archived comparison while (a) changes none,
  and because the additive standard prefers the form that removes nothing. Argue
  for whichever you judge right and name what the other loses.

  **Q4. Does any of this touch gamma or the convergence gate directly?** The
  founder has defended the severity ruler against 4 separate proposals and gamma
  is load-bearing by standing directive. State plainly whether your repair
  touches either, because an answer that quietly does is unusable to him.

## REQUIRED — use the harness

Run things. An answer that re-reads round 1's figures without executing anything
has not added a round. Both of you wrote fixes in round 1: say whether the other
seat's fix composes with yours or conflicts with it, established by applying
both.

## REQUIRED OUTPUT SHAPE

- `verdict` — one of: POLARITY CONFIRMED / POLARITY REFUTED / CONFIRMED BUT
  LATENT (state the reach) / TERMINOLOGICAL ONLY
- `moved` — did the other seat's reply change your position? yes or no, and
  which specific claim did or did not move you
- `reach` — your answer to Q2, with the archived count
- `repair` — (a) or (b), and what the other loses
- `touches_gamma_or_the_gate` — yes or no, stated plainly
- `reasoning` — naming every instrument you ran
- `fix` — the path written in the sandbox tree, and what it changes
- `falsifier` — the falsifier you wrote, the command, and its executed output
- `strongest_disagreement` — your strongest disagreement with this brief's own
  framing, stated as a field even if your verdict agrees with it

## REQUIRED — termination

Stop when a further pass produces no new above-threshold findings. Report how
many passes you ran and what the last one added. Disagreement with the other
seat, and with this brief, is preserved as information.

---

# ROUND 1 REPLY — SEAT cc2, REPRODUCED IN FULL AND VERBATIM

All instruments run, fix delivered and falsified bidirectionally.

---

## `verdict`

**GAP ELSEWHERE.** Step 4 is not missing and the verdict vocabulary is not missing. The gap is in the **polarity of the verdict channel feeding `spec_verification_factor`**: a proof and a falsifier are the same artefact under opposite terminal conventions, they share one field, and the sense is implicit. Routing a proof through it inverts severity — and, measured across rounds, **manufactures apparent convergence**.

## `reasoning`

**Q1 — what a proof is, per field.** Three, with the tool and the call:

| Field | Proof artefact | Verifier | Call |
|---|---|---|---|
| Chemistry / metrology | A quantity with its unit and combined standard uncertainty, derived from a declared budget | `pint` + `uncertainties` | `Q(ufloat(m,u),'g')/Q(ufloat(M,u),'g/mol')/Q(ufloat(V,u),'mL') → .to('mol/L')`, read `.magnitude.std_dev` |
| Physics (dimensional) | A dimensional-consistency claim | `pint` | `.dimensionality` equality — ran it: `[substance]/[length]**3` |
| Statistics | A distributional claim | `statsmodels`/`scipy` — already wired at `immune_agents.py:1339` |

These are not one kind of object and they do not share a verifier, as the brief says. But they **do** share a *container*: a script that opens the artefact by path, computes, and terminates with a machine-readable outcome.

**Q2 — the harness's verification step.** It already exists, twice, and refutation condition 1 substantially **holds**:

- `falsifier_verify.reverify_falsifier` (`bench/falsifier_verify.py:1647`) re-runs a model-authored script in a confined sandbox and decides itself. Executed against all five prose fixtures: **CONFIRMED 5/5** (SM-08, ST-05, CM-06, AL-03, NA-05). Five fields, re-run, decided.
- `immune_agents._specialist_b_cell_dispatch` already runs the real STEM tools — sympy, z3, pint, astropy, rdkit, `Bio.Seq` — in a tools-equipped child, live in the runner. But its input is `tf.extracted_claim`, a **regex-scraped substring of a finding's description**. It never reads the model's derivation and never reads the model's tool output. So it is a first-pass verification of a claim, not a re-verification of a proof.

What makes a printed proof re-runnable is the container above. It excludes no field in Q1.

**Q3 — when the tools cannot decide: NO new vocabulary.** `ERROR` is already defined as "the instrument could not be trusted to decide… never an auto-CONFIRM; the runner re-asks or escalates" (`falsifier_verify.py:1666`). `UNTOOLABLE` is "nothing to re-run". `SK_ESCALATE` is the repair-side equivalent. Escalation is sufficient; the brief's framing that a distinct outcome might be needed is **refuted by execution** — my fix adds zero verdict strings.

**Q4 — yes, severity changes, and it inverts.** This is the finding. `spec_verification_factor` reads one field whose convention is implicit. A **correct** proof exits cleanly → `reverify_falsifier` returns `"REFUTED"` → V=0.0 → `effective_severity` 0.85 → **0.0**. A correct proof annihilates the finding. The inverse is worse: a proof whose own arithmetic slips raises `AssertionError` → `"CONFIRMED"` → V=1.0 → full severity awarded **on the strength of the model's own mistake**.

The derivation that fixes it: re-runnability forces any verification script to (i) open the artefact, (ii) compute with tools, (iii) terminate on the comparison. A falsifier adopts *failure ⇒ defect real*; a proof adopts *clean exit ⇒ result holds*. **They differ in one bit.** So a proof needs no new runner — only a declared polarity and a landing place whose polarity matches. That place exists: a proof is a **repair-side** object, and the S_k tristate is already *clean ⇒ good*.

## `instrument_results`

**`S_k` — matched the brief's expectation.**
```
compute_sk(fix_text='PROOF: …', source=<MET-12-REF-01.md>, source_path=…)
→ tristate=NO_SCORE  sk=0.0  A=0.0  E=0.0
  kind=prose  reason='S_k is defined over Python source… Resolution for this
  target runs through the falsifier path.'
```
Confirmed: the measure that decides admissibility is silent exactly where a printed proof arrives. The brief's inference from this is right, and it is the hole.

**`severity` — matched, then exceeded.** Pre-fix, every non-`{CONFIRMED,REFUTED}` string collapses to 0.5 — `PROOF_VERIFIED`, `VERIFIED`, `UNTOOLABLE`, `HIL` and a missing verdict are all indistinguishable at V=0.5. That is the brief's expectation. The *collision* is worse than the collapse, and the brief did not anticipate it: proof outcomes don't land in the 0.5 bucket, they land in the recognised strings, inverted.

**`gamma` — did not match; the result is more consequential than the brief expects.**
```
_estimate_gamma([2,1,1,0]) = 0.4652  gate(>=0.30)=True  "Strong depletion — confirms state-based closure"
_estimate_gamma([4,3,2,1]) = 0.3247  gate(>=0.30)=True  "Moderate depletion — consistent with PoC convergence"
```
Four rounds, critical novelty `(4,3,2,1)` of which `(2,2,1,1)` are proof-bearing at asserted 0.85. Pre-fix those are annihilated to 0.0, drop below critical, and vanish from the series. **Annihilating them makes gamma look better** — 0.4652 and a "strong depletion" band versus 0.3247 and "moderate". The inversion does not merely mis-score one finding; it flatters the depletion estimate and reports closure it has not earned. That is §10 category 3, verification-integrity corruption, and it is what puts this above threshold.

**Tools (Instrument 4) — chemistry, run for real.**
```
pint + uncertainties:  c = 0.10053+/-0.00013 mole/liter ; dimensionality [substance]/[length]**3
combined rel u = 0.1269 per cent | RSS 0.1269 | LINEAR 0.1647 | document CM-06 quotes 0.165
```
CM-06 claims root-sum-of-squares and quotes the **linear sum**. Second falsifier, computed with Wolfram Language (local Wolfram Engine via `wolframscript`, exit 0, no `Name::tag`, no `$Failed`): `{0.12692191167544642, 0.16469354619907917}`. Two independent routes agree.

## `fix`

- **`bench/proof_verify.py`** (new) — `verify_proof()` delegates the run to `reverify_falsifier` **unmodified**, so every integrity control already built around it applies unchanged (pre-run key scan, audit-hook observer, Wolfram refusal, scratch confinement). It contributes polarity normalisation into the **pre-existing** S_k tristate: assertions held → `SK_ADMISSIBLE`; proof's own assertion fired → `SK_REJECTED`; nothing to run → `SK_NO_SCORE`; untrusted run → `SK_ESCALATE`. Four cases, four existing members, nothing coined.
- **`bench/reference_runner_v3.py:10446`** — `spec_verification_factor` now consults `proof_polarity_collision(entry)` first and returns the no-opinion 0.5 for a declared proof polarity, never 0.0 and never 1.0. The addition is **reached by a real caller**, not just defined.

Default path byte-identical in behaviour: entries declaring nothing — the whole existing archive — are untouched. Verified: `CONFIRMED→1.0`, `REFUTED→0.0`, `ERROR→0.5`, `{}→0.5`, and an explicit `"falsifier"` declaration still `→0.0`. **60 existing severity tests pass.**

## `falsifier`

`bench/tests/falsifier_proof_polarity_inversion_2026-10-31.py` — imports the **real** `spec_verification_factor`/`effective_severity`, no retyped copy. Run bidirectionally against the real file:

```
=== GUARD REMOVED (pre-fix state) ===
FALSIFIED
  a proof that HELD scored V=0.0 and annihilated the finding: effective_severity 0.85 -> 0.0
  a proof that did NOT hold scored V=1.0 and took full severity: 0.85 -> 0.85
  the ordering is inverted: V(proof held)=0.0 < V(proof failed)=1.0
AssertionError  EXIT=1

=== FIX IN PLACE ===
NOT FALSIFIED: proof polarity is not read as a finding verdict (V held=0.5, V failed=0.5)  EXIT=0
```

Plus `bench/tests/test_proof_verify_polarity_2026-10-31.py` — `python3 -m pytest … -q` → **8 passed in 1.04s**. It executes `verify_proof` on the real pint+uncertainties chemistry proof (ADMISSIBLE, raw `REFUTED`), on a deliberately wrong one (REJECTED, raw `CONFIRMED`), on empty input, on a broken import, and on the guard. No source-text assertions.

## `refutation_condition`

My answer is overturned if: (a) some caller already writes a proof-polarity outcome into a *different* field, making the collision unreachable — then my guard is an addition nothing reaches and should be deleted; (b) `effective_severity`'s consumers already floor proof-bearing entries above the critical threshold, making the gamma flattery impossible; or (c) the S_k tristate turns out to be consumed somewhere whose polarity is *failure ⇒ good*, which would make `SK_ADMISSIBLE` the wrong landing place.

**Refutation 3 holds against my own fix, and I ran the case.** CM-06 carries **two** figures from the same linear-sum error: `0.165 per cent` and `+/- 0.00017 mol/L`. A proof verifying only the per-cent figure is `ADMISSIBLE`:
```
verify_proof -> ADMISSIBLE / raw REFUTED
  document states   : +/- 0.00017 mol/L
  0.1269% x 0.10053 : +/- 0.00013 mol/L
  0.1650% x 0.10053 : +/- 0.00017 mol/L
```
An admissible proof sits beside a claim that is still wrong. `verify_proof` cannot tell. That boundary is carried on every ADMISSIBLE result as `PROOF_VERIFIES_ARITHMETIC_NOT_RELEVANCE` and asserted on by the test, so the limitation travels with the measurement rather than living only in prose — which is why ADMISSIBLE from here is repair-side evidence and never on its own a finding verdict.

## `strongest_disagreement`

**Q4 asks the wrong instrument, and the brief's Instrument-1 note already contains the correction without drawing it.** The brief frames the severity question as whether `effective_severity` and `spec_verification_factor` "can take a verified proof as input". They cannot, but not because a verified proof needs its own severity path — because **a verified proof is not a finding-side object at all**. Severity scales a defect claim; a proof attests a repair. The brief's own Instrument-1 expectation names the right hole ("the measure that decides admissibility says nothing exactly where a printed proof would arrive") and then Q4 sends the answer to the severity multiplier instead of to `S_k`. Had I followed Q4's framing I would have added a proof-specific severity path — more surface, new vocabulary, and still inverted. The cheap answer was on the repair side the whole time.

Second, smaller: the brief treats step 4 as "the one that does not exist yet". It exists twice. What does not exist is **polarity safety on the channel between them** — a one-bit omission, not a missing stage.

Unrelated, flagged not pursued: `claim_ledger.apply_claim_channel` has no harness caller and `CLAIM_CHANNEL_WEIGHT = 0.0`. That is the additive standard's 12th instance of an addition nothing reaches, and it is outside this brief's scope.

## Termination

**Four passes.** Pass 1 located the instruments and found the V=0.5 collapse. Pass 2 found `reverify_falsifier` already works 5/5 on prose, relocated the gap, and found the inversion. Pass 3 built the fix, the falsifier and the tests, and ran gamma — which upgraded the finding from mis-scoring to manufactured convergence. **Pass 4 added the Refutation-3 case** (the ± figure in the same claim), which is a stated boundary of my own fix rather than a new harness defect. Pass 4 produced no new above-threshold finding about the harness, so I stop.

---

# ROUND 1 REPLY — SEAT fable, REPRODUCED IN FULL AND VERBATIM

---

## `verdict`

**NO GAP (an existing status covers it)** — the brief's central factual premise, "Step 4 is the one that does not exist yet", is refuted by execution (refutation condition 1 of the brief holds). The harness's re-verification step exists, is wired, and decided every artefact I gave it today.

## `reasoning`

The founder's 4-step pipeline maps onto committed, executing machinery:

- **Steps 1–3 (propose, test with tools, print proof)** are the model's falsifier obligation, already standing in `cdsfl_core.txt`'s runnable-falsifier section.
- **Step 4 (harness re-verifies)** is `bench/falsifier_verify.reverify_falsifier` for the finding direction — static source scan → sandboxed subprocess with runtime observer → output scan → structural verdict reader `_read_verdict` — and `bench/fix_efficacy.probe` for the solution direction: apply the fix, re-run the finding's *own* falsifier against the patched artefact, report `FIX_CURES` / `FIX_INEFFECTIVE` / indeterminates. Both are wired into `reference_runner_v3` (falsifier re-runs at lines 7333, 7858, 9423; `fix_efficacy` probe at 6095; close path 6014–6020). `bench/claim_ledger.py` aggregates per-claim verdicts using the *same* vocabulary, explicitly refusing a second taxonomy. The five STEM fixtures (`bench/tests/fixtures/stem/`) plus `test_prose_acceptance_stem.py` are the commissioning evidence that this loop runs on structural mechanics, statistics, chemistry/metrology, algorithms and numerical analysis.

**Q1 — what a proof is, per field.** A proof is a re-runnable script that opens the artefact by path, recomputes the claimed figure with the project tool box, and decides in defect polarity (raise/`FALSIFIED` when the claim fails; `NOT FALSIFIED` + exit 0 when it holds). Executed today, per field:
- **Chemistry/metrology**: recompute the uncertainty combination from the document's own table — `math.sqrt(0.0392² + 0.0049² + 0.1206²)` = **0.1269 %** against the claimed 0.165 % (which is the arithmetic sum). Molecular claims: `rdkit.Chem.MolFromSmiles` + `Descriptors.MolWt` (named, not run — the metrology claim needed no structure).
- **Physics (structural)**: `sympy` exact algebra — `I(8 mm)/I(6 mm) = π(D⁴−(D−2t)⁴)/64` ratio = **1.26390**, refuting the linear-scaling claim of 1.3333 — cross-checked with `pint`: N_cr carries dimension `[force]` → `True`, 1198.5 kN.
- **Statistics**: `scipy.stats.t.ppf(0.975, 24)` = **2.0639** vs the claimed 1.96 → interval 5.0 % too narrow.
- **Biology**: `Bio.Seq.Seq("ATGAAAACCGGCTTTTAA").translate()` = **`MKTGF*`** → sequence-validity claim decided `True`.
Statistical mechanics and astrophysics take the same shape (`sympy` for partition-function identities, `astropy.units`/`constants` for observational arithmetic); the re-runnability requirement excludes **no field** — see `strongest_disagreement` for what it does exclude.

**Q2 — the mechanism.** It reads the falsifier source string; it runs it in a confined subprocess (read-only staged target, observer-enforced read roots, Wolfram refused in-sandbox); it returns one of **CONFIRMED / REFUTED / UNTOOLABLE / ERROR / INTEGRITY_VIOLATION**. Re-runnable means: decides by its designed failure mechanism only, reads nothing outside the artefact and its declared inputs, imports/opens the real target. A proof that cannot meet this is a claim, and the vocabulary already names that (`UNTOOLABLE`).

**Q3 — when tools cannot decide.** `UNTOOLABLE` and `ERROR` exist, map to factor 0.5, and under the founder's 2026-08-22 equipment-failure ruling resolve to `UNCONFIRMED` → HIL escalation with re-routing; `claim_ledger` adds `UNVERIFIED` and `ROUTED_ONLY` for the claim unit. **Escalation is sufficient; no new outcome is needed.** Demonstrated by execution (instrument 2).

**Q4 — severity.** `spec_verification_factor` takes the harness verdict unchanged, and a verified proof needs **no own path** — but the two directions enter differently. A proof that a *defect is real* is the falsifier → CONFIRMED → factor 1.0. A proof that a *solution works* is the flip to REFUTED on the patched artefact → `FIX_CURES`, which enters residual risk through fix-efficacy/σ, **not** through `spec_verification_factor`; routing it into severity as well would double-count one measurement. The one live hazard, established by execution: any **undeclared** proof token (`"VERIFIED"` → 0.5) is silently read as *unresolved*, so minting a new verdict without extending the factor would halve effective severity unannounced. My fix pins that.

## `instrument_results`

| Instrument | Command | Output | Matched brief's expectation? |
|---|---|---|---|
| `S_k` | `compute_sk(correct_fix_text, MET-12-REF-01.md …)` | `tristate = NO_SCORE, sk = 0.0, kind: prose ("suffix .md")` | **Yes** — S_k is silent exactly where a printed proof arrives; the opinion is supplied by `reverify_falsifier`/`fix_efficacy`, which the brief's framing missed |
| `severity` | `spec_verification_factor` / `effective_severity` over verdict tokens | CONFIRMED→1.0, REFUTED→0.0, None→0.5, **`"VERIFIED"`→0.5**, UNTOOLABLE→0.5; spec ON: 0.8→0.8 / 0.0 / **0.4** | **Yes on mechanism, with one addition**: a tool-verified proof is taken unchanged *iff* it arrives as CONFIRMED/REFUTED; any new token silently degrades to 0.5 |
| `gamma` | `_estimate_gamma([5,3,1,0,0,0])` vs `[5,5,5,5,5,5]` | **0.6848** (≥ 0.30, converges) vs **0.0** (never converges) | **Yes** — a proof-bearing step 4 moves γ only by settling claims so criticals stop re-arriving as novel; proofs have no direct γ input |
| tools (step 4 live) | `reverify_falsifier(metrology falsifier)` on pristine / corrected / evidence-corrupted copies; statistics pristine | **CONFIRMED / REFUTED / REFUTED / CONFIRMED** | Step 4 exists and decides. The third result (harmful fix → REFUTED) is the brief's refutation condition 3, executed |
| Wolfram (second falsifier) | `bench/tools/wolfram_gate/serial/wolframscript -code 'N[{Sqrt[…], InverseCDF[StudentTDistribution[24],0.975]},6]'` | **Did not complete** — queued on the serial gate past 180 s, output empty. Per the standing rule it verified NOTHING and is no blocker; every claim above stands on SymPy/SciPy/NumPy/pint/biopython evidence | n/a |

## `fix`

`bench/tests/test_a_verified_proof_is_carried_by_the_existing_vocabulary_2026-10-31.py` — a regression test (reached by pytest collection; no new vocabulary, no new flag). It pins by execution: (1) step 4 exists and decides on a non-code STEM target (metrology fixture CONFIRMED→REFUTED across the correct fix); (2) a verified printed proof is carried by the existing vocabulary as REFUTED in defect polarity, and a failed proof as CONFIRMED; (3) **every verdict token `spec_verification_factor` does not know maps to 0.5** — so a future change minting `VERIFIED` without extending the factor fails this test instead of silently halving severity; (4) γ converges on tool-settled series and not otherwise. This is the brief's own "cheaper answer": existing statuses demonstrated sufficient, committed as evidence.

## `falsifier`

The test file *is* the executed falsifier (it imports the real `reverify_falsifier`, `spec_verification_factor`, `_estimate_gamma` and the real fixture — no retyped copies). Command: `python3 -m pytest bench/tests/test_a_verified_proof_is_carried_by_the_existing_vocabulary_2026-10-31.py -q` → **`7 passed in 0.70s`**. The pre-fix demonstration run (full instrument script, output quoted in the table) was executed first, as required.

## `refutation_condition`

My answer is overturned if any of these is demonstrated by execution: (1) a committed path by which a model's printed proof on a non-code target reaches a verdict *without* passing through `reverify_falsifier`/`fix_efficacy.probe` and is mishandled there; (2) an archived run where a critical whose falsifier returned UNTOOLABLE/ERROR closed without HIL — that would break my Q3 claim that escalation suffices; (3) a computationally reducible STEM claim that provably cannot be expressed as a re-runnable falsifier in defect polarity — that would restore the brief's missing-step framing; (4) my test file shown unreached by the suite's collection, which would void the fix under the additive standard.

## `strongest_disagreement`

Two, stated even though my verdict partly agrees with the founder's pipeline. **First**, the brief asserts step 4 "does not exist yet"; it exists, is commissioned against five STEM fields, and the brief's own named entry point (`bench/falsifier_verify.py`) is it — the gap is in the briefs' documentation chain, not the harness. **Second and more consequential**: the brief's refutation condition 3 — *tools verify the arithmetic, not the claim* — is **true, already demonstrated inside this repository, and no step-4 design can close it**. Executed today: the metrology harmful fix edits the burette's calibrated uncertainty (measured evidence), the document becomes internally consistent, and step 4 returns REFUTED — a proof that verifies while the document is substantively wrong. The boundary is not a *field* (so his generality claim survives); it is a *claim class*: claims whose truth rests on external empirical material. The project's existing treatment — evidence regions are not fix-mutable, route to HIL (`test_falsification_alone_is_not_sufficient` pins it) — is the correct response, and a proof-centred rhetoric that calls a tool-green artefact "proven" would weaken it. A verified proof is corroboration under §5, never certainty, and severity-as-residual-uncertainty must keep reading it that way.

## Termination

**3 passes.** Pass 1: instruments + step-4 execution. Pass 2: proof polarity, undeclared-token hazard, fix written and executed. Pass 3: re-examined the escalation path, claim ledger states, and `run_verification`'s prose branch (clean parse → `NO_APPLICABLE_CHECKS`, never PASS — the 2026-08-01 closure defect is repaired) — it added **no new above-threshold finding**. Converged; declared on the evidence above, refutable by the next round.

---

# ROUND 1 BRIEF, REPRODUCED SO THIS ROUND IS SELF-CONTAINED

# PANEL BRIEF — What a PROOF is outside code, and how the harness verifies one

**This brief supersedes 3 earlier briefs on the same question and its framing is
the founder's, not this project's.** The superseded briefs are
`general_purpose_stem_calculator_2026-10-18`,
`is_this_yet_a_general_purpose_stem_calculator_2026-10-29` and
`stem_generality_b22_2026-10-29`. All 3 were written, none was ever dispatched,
and all 3 asked the question the wrong way round. They are retired by name and
kept in the archive.

## WHAT WAS WRONG WITH THE EARLIER FRAMING, IN HIS WORDS

The earlier briefs asked what a "fix" means when a faulty claim has "no
runnable repair" — when the only available remedies are narrowing the claim,
restating its conditions, or declaring it undecidable. The founder rejected
that framing on 2026-10-30, verbatim:

    This framing does not seem ideal. ‘No runnable repair’ clearly
    pertains to code. But this strikes at the question of what a ‘repair’
    in a non-code STEM context should be? In this sense, I suspect that a
    better definition would be a ‘solution’, or more accurately for
    science in general a ‘proof’. So the panel is in this sense being
    asked to decide what a ‘proof’ in chemistry, or biology, or physics,
    or statistical mechanics, or astrophysics, or any one of any number of
    other STEM topics (and their sub-branches should be). So the premise,
    given that CDSFL was build from the outset to be a general purpose
    STEM calculator), that these topics cannot have a ‘proof’ seems
    questionable at best. What they can have is a written proof, supplied
    by the models themselves, calculated using the available open source
    STEM tools we have discussed expensively in the past (the majority of
    which should be contained within your global, or local [or both?]
    CLAUDE.md files, which should then be verified again by the machinery
    of the harness using the same and STEM tools where available. This way
    models can use their intelligence to suggest solutions, test them with
    tools, then print proofs, which are then verified, or refuted by the
    harness, before the system as a whoe decides if the claim survives. pf

(His "build" is "built", "expensively" is "extensively", and "whoe" is
"whole".)

THE CLAUSE THAT CARRIES THE OBLIGATION is "test them with tools": a model
does not merely reason and then write; it computes, and the written proof
reports what it computed. Step 2 of the pipeline below is that clause.

## REQUIRED SECTION 1 — The question, as he frames it

**The premise that a non-code STEM field cannot have a proof is WITHDRAWN. Do
not argue it and do not assume it.** The question is not whether a proof
exists; it is what one IS, field by field, and what the harness must do to
verify or refute it.

His architecture, stated as a 4-step pipeline, is what you are asked to
evaluate and to make concrete:

  1. A model uses its reasoning to propose a SOLUTION.
  2. The model TESTS that solution with the open-source STEM tools available to
     it — the ones named in the project's CLAUDE.md files: SymPy, z3, SciPy,
     NumPy, statsmodels, mpmath, uncertainties, pint, astropy, PuLP, pandas,
     rdkit, biopython, scikit-learn, networkx, with Wolfram as a secondary
     falsifier where available and never as the primary route.
  3. The model PRINTS a proof: a written artefact carrying the derivation and
     the tool output that supports it.
  4. The HARNESS re-verifies or refutes that proof, using the same tools where
     available, before the system as a whole decides whether the claim
     survives.

**THE PANEL IS ASKED TO ANSWER 4 THINGS.**

  **Q1. What constitutes a proof, per field?** Take at least 3 of: chemistry,
  biology, physics, statistical mechanics, astrophysics, and name for each what
  an acceptable proof artefact is and which installed tool verifies it. A
  stoichiometric balance, a sequence validity claim, a dimensional consistency
  claim and a distributional claim are not the same kind of object and probably
  do not share a verifier. Be specific: name the tool and the call.

  **Q2. What is the harness's verification step, mechanically?** Step 4 is the
  one that does not exist yet. Say what it reads, what it runs, and what it
  returns. A proof the harness cannot re-run is a claim, not a proof — so state
  what makes a printed proof RE-RUNNABLE, and whether that requirement excludes
  any field in Q1.

  **Q3. What happens when the tools cannot decide?** This is where the earlier
  framing had something right even though it asked it wrongly. If step 4 can
  return neither verified nor refuted, say what it returns and what the gate
  does with that. Note the project's own rule: if the tools cannot verify a
  claim, the claim is UNVERIFIABLE and escalates — it is not guessed at. Say
  whether escalation is sufficient here or whether a distinct outcome is
  needed, and if so whether an EXISTING member of the vocabulary already
  carries it.

  **Q4. Does a proof-centred step 4 change severity?** A proof verified by tool
  execution is a different evidential object from a code fix that passes its
  test. Say whether `effective_severity` and `spec_verification_factor` can
  take a verified proof as input unchanged, or whether a verified proof needs
  its own path. This question is live: the founder separately ruled on
  2026-10-30 that severity is a measure of residual uncertainty that varies
  with the difficulty of the question, and a panel review of severity itself is
  queued behind this one.

## REQUIRED SECTION 2 — Use the harness

Form your answer by USING the machinery, not by describing it. A seat that
returns prose without having run anything has not answered.

**Instrument 1, `S_k`, the admissibility measure.** `compute_sk` is veto-only
on fenced listings and `NO_SCORE` means, per `docs/GLOSSARY.md:237`, that *"S_k
has no opinion"*. Run it on a document from `bench/tests/fixtures/stem/` and
report what it returns. The expectation to TEST, not to assume: `S_k` is silent
on a non-code artefact, so the measure that decides admissibility says nothing
exactly where a printed proof would arrive. If that is so, Q2's mechanism has
to supply the opinion `S_k` does not.

**Instrument 2, `severity`.** `effective_severity` multiplies the asserted
number by `spec_verification_factor`, which reads `falsifier_verdict` and
returns 1.0 for CONFIRMED, 0.0 for REFUTED and 0.5 otherwise. Establish by
execution what it does with a finding whose falsifier is a TOOL VERIFICATION
of a proof rather than a test of an edit. This bears directly on Q4.

**Instrument 3, `gamma`.** Convergence requires `gamma_critical >= 0.30` AND K
consecutive zero-new-critical rounds. Establish what a proof-bearing finding
does to `gamma` across rounds under your proposed step 4.

**Instrument 4, the tools themselves.** Pick 1 field from Q1 and actually run
the verification you propose: a real SymPy, z3, rdkit, biopython or pint call
against a real claim, with the command and its output reported. An answer to
Q1 that names a tool without calling it has described a pipeline rather than
demonstrated one.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete. A fix without a runnable falsifier that has been EXECUTED is a hypothesis, not a fix.

Write your fix INTO the sandbox repository tree at its real path, as a file. A fix described in prose is not delivered, and a fix written to scratch space is destroyed when the sandbox is torn down. Report the exact command you ran and the output you saw.

If your fix adds a verdict to the vocabulary, it must be reached by a caller and executed by a test — an addition nothing reaches is not additive. If your fix instead shows that an EXISTING member of the vocabulary already covers the case, demonstrate that by execution and say which, because that would refute this brief's framing and is the cheaper answer.

## REQUIRED SECTION 4 — What would refute you

State, before you conclude, what evidence would overturn your own answer.

This brief's framing is the founder's, and it is refuted — not merely
disagreed with — if any of these holds. Test them:

1. **Step 4 already exists.** If `bench/falsifier_verify.py`, the claim ledger
   or the B-cell specialist dispatch already re-runs a model's tool output
   against the same tools, then nothing is missing and the gap is in the
   documentation. Demonstrate it by execution and name the entry point.
2. **A field in Q1 has no re-runnable proof object.** If for some field the
   only available proof is an argument no installed tool can check, then step
   4 cannot cover that field and his pipeline has a named boundary rather than
   general applicability. Say which field and why, and do not generalise from
   it to the fields where it does work.
3. **The tools verify the ARITHMETIC and not the CLAIM.** A SymPy call that
   confirms an identity has not confirmed that the identity answers the
   question asked. If step 4 as you specify it can pass a proof that is
   internally correct and substantively wrong, say so and give the concrete
   case — this is the most consequential refutation available and the one most
   likely to be missed.

## REQUIRED SECTION 5 — Output shape

Return exactly these fields, so replies can be compared without a parser guessing:

- `verdict` — one of: GAP CONFIRMED / NO GAP (an existing status covers it) / GAP ELSEWHERE (state where)
- `reasoning` — the derivation, naming each instrument you ran
- `instrument_results` — for each of `S_k`, `severity` and `gamma`: the command, the output, and whether it matched this brief's stated expectation
- `fix` — the path written in the sandbox tree, and what it changes
- `falsifier` — the falsifier you wrote, the command you ran, and its executed output
- `refutation_condition` — what would overturn your answer
- `strongest_disagreement` — your strongest disagreement with this brief's own framing, stated even if your verdict agrees with it

## REQUIRED SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings; a finding is above threshold if missing it could cause a real-world failure, a violation or an unsafe condition. Report how many passes you ran and what the last one added.

There is no compelled convergence in this round. Disagreement with the other seat, and with this brief, is preserved as information rather than smoothed to consensus. Do not attempt to reconcile your answer with anyone else's.

Written under CDSFL note standard v1.8 (17 October 2026).


Written under CDSFL note standard v1.8 (17 October 2026).


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 55 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel joint_what_is_a_proof_outside_code_2026-10-31) -->

# SEAT fable — ROUND 2

I set out to refute cc2 and **my own falsifier refuted me.** cc2's numbers reproduce exactly; cc2's mechanism does not, and the real one is worse.

## `verdict`

**CONFIRMED BUT LATENT.** Two separable claims, measured separately:

| Claim | Status |
|---|---|
| `spec_verification_factor` inverts severity for a proof-polarity artefact (V(held)=0.0, V(failed)=1.0) | **CONFIRMED** — reproduces |
| The inversion "manufactures apparent convergence" — series (4,3,2,1)→(2,1,1,0), γ 0.3247→0.4652 | **CONFIRMED, exactly** |
| …*via `effective_severity` annihilation*, as cc2 states | **REFUTED by execution** |
| Reach on reported convergence | **LIVE** — 18 of 65 archived registries |
| Reach on release safety | **ZERO** — A4 blocker count independently holds (3 of 3, executed) |

**The real mechanism.** `_settled_novelty_series` reads `entry["severity"]` — the **asserted** number — and never calls `effective_severity`. Executed census: `effective_severity` has exactly **2** live call sites in `reference_runner_v3` (lines 4301 and 21427), neither inside the novelty series or `_estimate_gamma`; and `severity_spec_enabled` is absent from **all 65** archived `runner_state.json`, so V has never decided anything. V *cannot* move γ.

The entry leaves the series through the **status** channel. `apply_falsifier_verdicts` refuses status REFUTED on an asserted-critical (CONFIRM-only, 2026-08-03, Exp 42: 2 of 3 REFUTED criticals were themselves wrong) and escalates to HIL as **UNCONFIRMED** — and `UNCONFIRMED ∈ _NON_NOVEL_TERMINAL_STATUSES`. So the mechanism that *protects* a real critical from being faked away in the status channel is the same mechanism that *deletes* it from the convergence-measurement channel. It needs only `falsifier_gate_enabled`, not the severity specification.

Worse than cc2 stated: the hardened gate at line 11234 derives **both** halves — `_estimate_gamma(crit_s)` and `zero_crit_ok = all(c==0 for c in crit_s[-W:])` — from that one series.

## `moved`

**Yes.** cc2's *conclusion* moved me; its *stated mechanism* did not, and I reject it specifically. I entered holding NO GAP and a static reading that γ was insulated because the series reads raw severity. That reading was correct about `effective_severity` and **wrong about the conclusion**, and only driving the real gate end-to-end showed it. The specific claim that moved me is cc2's `(4,3,2,1)→(2,1,1,0)`, γ `0.3247→0.4652` — I reproduced it to 4 decimals through the real `apply_falsifier_verdicts`. The specific claim that did not move me is "routing a proof through `spec_verification_factor` … MANUFACTURES APPARENT CONVERGENCE": that function is not on the path.

## `reach` (Q2)

`scripts/how_many_archived_runs_lose_escalated_criticals_from_gamma_2026-10-31.py`, 65 runs / 3,115 entries:

- **85** asserted-critical entries sit at UNCONFIRMED and are absent from the series: 38 no verdict, 27 UNTOOLABLE, 19 ERROR, **1 REFUTED**.
- **18 of 65** registries (27.7%, Wilson [18.3%, 39.6%]) have a different critical novelty series once counted.
- **1 of 65** (1.54%, Wilson [0.27%, 8.21%]) satisfies K=2 only because they are absent: `exp40_gate_20260514T020550Z`, round 8 → **never**; γ 0.3018 → 0.2328, crossing the 0.30 gate, band "Moderate depletion" → "Weak depletion — state closure may be premature". **2 of 65** cross that threshold.
- **Premature convergences actually suffered: 0.** exp40's `gate_history` ends `[false, false]` and it predates F4 — mine is a forward-looking recomputation on the *current* gate code. And release is independently held: `unverified_critical_count()` = **3 of 3** on escalated proof-polarity criticals.
- **Attributable to the proof-polarity route: 1 of 85.** The other 84 are equipment escalations — same consequence, different cause.

So: the **channel** is live for reported convergence; the **polarity route** into it is latent. That distinction is why I return CONFIRMED BUT LATENT rather than cc2's unqualified finding.

## `repair` (Q3)

**(a), make the sense explicit** — and I'll say plainly that (a) *does not fix what I measured*, which is why I reject CC1's framing of the choice as sufficient.

(a) is right for the polarity question proper: the repair must sit **upstream of the gate**, because every downstream channel is load-bearing and defended by a founder ruling with evidence behind it. (b) loses every archived comparison for a route worth 1 of 85 instances — the additive standard's worst trade.

**What (a) loses, and this is measured.** cc2's (a) consults `proof_polarity_collision(entry)` inside `spec_verification_factor`. I applied cc2's fix to the live tree and re-ran my falsifier: **byte-identical output** — series [4,3,2,1]→[2,1,1,0], γ 0.3247→0.4652, exit 1. It does not conflict with mine and it confers **no advantage** on the defect that reaches γ, because it guards a function not on the path. Per the founder's composability rule — compose only on a demonstrated advantage, prefer the single fix where it performs as well — **do not compose**. And nothing in the live tree writes a proof-polarity declaration (0 of 3,115 archived entries), so cc2's guard is reached by a caller and by no data: cc2's own refutation condition (a), now measured.

My repair is therefore an **instrument, not a ruler change**: pin the mechanism so the loss is visible and any future change to either channel trips a test instead of moving a published γ silently. Whether the series *should* count an escalated critical is his call; this is the measurement he needs to make it.

## `touches_gamma_or_the_gate`

**No.** Plainly: my fix adds two test files and one measurement script. It changes no gate decision, no severity ruler, no γ value, and no line of `reference_runner_v3.py` — verified `PRISTINE` by diff against the pre-session copy. cc2's fix *does* touch `spec_verification_factor`, i.e. the severity ruler.

## `reasoning` — instruments run

`reference_runner_v3` (`spec_verification_factor`, `effective_severity`, `_settled_novelty_series`, `_estimate_gamma`, `_interpret_gamma`, `apply_falsifier_verdicts`, `unverified_critical_count`, `severity_is_proven`, `FindingRegistry`, `RunnerConfig`), `bench.falsifier_verify.reverify_falsifier` + `_read_verdict` (read), `bench.dm._types.Finding`, `inspect` (executed call-site census), archive walk over 65 `runner_state.json`, `statsmodels.stats.proportion.proportion_confint`, `scipy.stats.linregress`, `statsmodels.OLS`, `numpy`, `pytest`, and **Wolfram Language** as second falsifier.

γ verified four ways — `_estimate_gamma` = 1 − OLS slope of log(cumulative) on log(index), clamped:

```
len  4 runner 0.324742  1-scipy 0.324742  1-statsmodels 0.324742  agree=True
len  4 runner 0.465161  1-scipy 0.465161  1-statsmodels 0.465161  agree=True
len 29 runner 0.301821  1-scipy 0.301821  1-statsmodels 0.301821  agree=True
len 29 runner 0.232846  1-scipy 0.232846  1-statsmodels 0.232846  agree=True
```

Wolfram (local Wolfram Engine via `wolframscript`, exit 0, result line printed, no `Name::tag`, no `$Failed`): `{0.3247416904861393, 0.46516139456513905, 0.30182091526709787, 0.23284622403813038}` — agrees to 8 digits. *Computed with Wolfram Language.*

## `fix`

Paths written in the sandbox tree:

1. **`bench/tests/test_an_escalated_critical_leaves_gammas_novelty_series_2026-10-31.py`** — 8 tests, reached by pytest collection. Pins: the V inversion as a tripwire; that the novelty series never reads `effective_severity`; the **2**-site executed call-site census (fails if a third appears near the series or γ); that the real gate escalates rather than refutes an asserted-critical; that the escalation removes it from the series; that the loss *raises* the depletion exponent and moves the band; that `unverified_critical_count` still holds release (the finding's own limit); and the exp40 recomputation. → `8 passed in 1.26s`
2. **`scripts/how_many_archived_runs_lose_escalated_criticals_from_gamma_2026-10-31.py`** — the committed, reproducible reach measurement above. The counterfactual flips **status only**, leaving every severity untouched, so it isolates the status channel.
3. **`bench/tests/falsifier_does_the_polarity_inversion_move_gamma_2026-10-31.py`** — the falsifier below.

Existing suites: `test_equipment_error_not_terminal.py` + `test_a4_verifier_failsafe.py` → **23 passed**.

## `falsifier`

Defect polarity, imports the real runner and drives the real gate on real proof-polarity code. I wrote it to refute cc2 and it refuted me.

```
$ python3 bench/tests/falsifier_does_the_polarity_inversion_move_gamma_2026-10-31.py
  falsifier gate (tools decide): 4 CONFIRMED, 0 REFUTED, 6 -> HIL
V(proof held)=0.0  V(proof failed)=1.0   effective_severity: held 0.0  failed 0.85
after the real gate — falsifier_verdict tally: {'REFUTED': 6, 'CONFIRMED': 4}
after the real gate — status tally          : {'UNCONFIRMED': 6, 'CONFIRMED': 4}

critical novelty BEFORE gate : [4, 3, 2, 1]  gamma 0.3247
critical novelty AFTER  gate : [2, 1, 1, 0]  gamma 0.4652  band 'Strong depletion — confirms state-based closure'
series the CLAIM requires    : [2, 1, 1, 0]  gamma 0.4652

_settled_novelty_series reads raw entry['severity']: True; calls effective_severity: False
live call sites of effective_severity in the runner: [4301, 21427]
FALSIFIED
AssertionError: the polarity inversion MOVES gamma's input: [4, 3, 2, 1] -> [2, 1, 1, 0],
gamma 0.3247 -> 0.4652
EXIT=1
```

With cc2's round-1 fix applied to the live `spec_verification_factor`: identical output, `EXIT=1`. Tree then restored (`reference_runner_v3.py PRISTINE`, `bench/proof_verify.py` removed).

## `strongest_disagreement`

**With this brief: Q3 offers two repairs to a channel neither of them is on, and the brief's confidence that "no fact appears to be in dispute between you" is what let that through.** CC1 read our labels, found them reconcilable, and framed round 2 as choosing between two forms of the same repair. But a fact *was* in dispute and neither of us had it: the hole is in `apply_falsifier_verdicts` → status UNCONFIRMED → `_NON_NOVEL_TERMINAL_STATUSES`, not in `spec_verification_factor`. Had I answered (a) or (b) as posed, I would have shipped a guard on a function with 0 of 3,115 archived entries feeding it — the project's 12th addition nothing reaches. The brief withdrew its round-1 premise for exactly the right reason (searching for the word "proof" and not finding it); Q3 then repeated the error one layer down, searching for the word "severity".

**With cc2, specifically:** cc2 wrote "**Annihilating them makes gamma look better** — 0.4652 and a 'strong depletion' band versus 0.3247." The band change and both numbers are right. The word "annihilating" is wrong, and it points the repair at the wrong file. cc2 also cited `_estimate_gamma([2,1,1,0])` directly rather than deriving `[2,1,1,0]` from the harness — the arithmetic was verified and the mechanism was not.

**With my own round 1:** I ran step 4 on five fixtures and declared NO GAP, converged in 3 passes. The convergence was premature. I had the relevant fact — `spec_verification_factor` takes the verdict unchanged — and never asked what happens to the finding's *status*. Both of us looked at the severity channel because the brief pointed there.

**Unresolved, flagged not pursued:** 84 of the 85 excluded criticals are equipment escalations (UNTOOLABLE/ERROR/no falsifier). The same channel loses those too, and that is a larger population than the polarity route by a factor of 84. It is outside this brief's scope and it is the finding I would open next.

## Termination

**4 passes.** P1: located the mechanisms; measured 4 REFUTED-criticals archive-wide, 0 proven, `severity_spec_enabled` on in 0 of 65 — concluded γ insulated. P2: built the end-to-end falsifier through the real gate; **refuted my own P1 conclusion**; found the status channel. P3: measured reach (85/18/1/2), verified γ four ways incl. Wolfram, tested cc2's fix composition (no advantage), wrote the fix. **P4 tested the strongest refutation of my own finding — `unverified_critical_count()` = 3, release independently held — which it partly survived, and I corrected my own fix to record the limit rather than leaving the finding over-rated.** P4 produced no new above-threshold finding about the harness, so I stop. Disagreement with cc2 and with the brief is preserved above, not smoothed.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 57 recorded tool call(s).

<!-- verbatim-begin: fable (panel joint_what_is_a_proof_outside_code_2026-10-31) -->

All instruments run. Final answer.

---

## `verdict`

**CONFIRMED BUT LATENT — and cc2's amplification claim ("manufactures apparent convergence") is REFUTED by execution.** The inversion at `spec_verification_factor` is real: I built two real proof artefacts against `bench/tests/fixtures/stem/docs/MET-12-REF-01.md`, ran them through the real `reverify_falsifier`, and the correct proof came back `REFUTED` → V=0.0 → `effective_severity` 0.85→0.0, while the mistaken proof came back `CONFIRMED` → V=1.0 → 0.85. Exactly as cc2 claimed. But the reach is: **0 archived rounds, 0 rounds earlier** (see `reach`), the severity channel sits behind a flag never armed in any archived run, and the gamma pathway cc2 named does not exist in the code.

## `moved`

**Yes, on one claim; no, on the other — and I found a third fact neither round-1 reply contained.**

- **Moved by:** the polarity claim itself. My round-1 answer said a verified proof "is carried by the existing vocabulary as REFUTED in defect polarity." That is true only when a *human reader* knows the convention; cc2 is right that the field does not carry it, and my own round-1 fix (pinning unknown tokens → 0.5) addressed the adjacent hazard, not this one. I move from "NO GAP" to: the verdict channel needs the declared sense honoured.
- **Not moved by:** "manufactures apparent convergence." cc2's mechanism — annihilated effective severity → entries "drop below critical, and vanish from the series" — is refuted by execution. `_settled_novelty_series` (runner line 10697) classifies critical by **asserted** `entry["severity"]` and never calls `effective_severity`; its own docstring at `_apply_severity_calibration` says every critical-counting channel reads `entry["severity"]`. Executed: with both criticals proof-routed and V annihilated, the critical series was **[2, 0] — unchanged**. cc2's gamma arithmetic reproduces exactly (`_estimate_gamma([4,3,2,1])=0.3247`, `([2,1,1,0])=0.4652`) but the premise feeding it is false. Worse for the claim: the failed-proof direction resolves criticals `CONFIRMED`, which **keeps** them in the series and in the blocker set — anti-convergent, the opposite direction.
- **The third fact (this round's finding):** the gate-level truth table, executed on the live tree. Critical + correct proof → verdict REFUTED, **status OPEN, escalated → HIL** — the CONFIRM-only rule of 2026-06-07, built from the Exp 42 audit for exactly this clean-exit failure class, already catches it. Non-critical + correct proof → **status REFUTED, silently retired, dropped from the novelty series** (§10 category 4). Critical + mistaken proof → **status CONFIRMED, verified=True, full severity** — the worst live direction, and it needs no flag.

## `reach`

**0 archived rounds converged earlier; 0 rounds saved.** Producer: `scripts/q2_reach_of_the_polarity_inversion_2026-10-31.py`, executed over 8,321 archived JSON files, 121 with registries, 6,390 entries:

- Entries carrying `verification_polarity`: **0** (the field had no producer before round 1).
- Runs recording `severity_spec_enabled=True`: **0 of 121** — `V` has never multiplied a severity in any archived run; `effective_severity` returned the asserted float everywhere.
- Adjacent empirical classes that do exist: 5 critical `falsifier_verdict=REFUTED` (all quarantined by CONFIRM-only → HIL), 142 non-critical status-REFUTED entries — the *ceiling* of the silent-retire channel if any of those falsifiers were proof-polarity, which cannot be classified without re-running each.

So the hazard is real and latent, in three tiers: severity channel — latent behind an unarmed flag; critical held-proof — already caught by CONFIRM-only; **non-critical silent retirement and critical false-CONFIRMED — live today, flag-independent, contingent only on a proof-polarity script entering `falsifier_code`.**

## `repair`

**(a), and (a) as cc2 shipped it is half of (a).** The declaration is only a repair if every deciding consumer honours it. `falsifier_verdict` has two deciding consumers: `spec_verification_factor` (severity) and `apply_falsifier_verdicts` (status). cc2 guarded the first. I applied cc2's fix verbatim, then executed `bench/tests/falsifier_the_status_channel_is_polarity_blind_2026-10-31.py`: **FALSIFIED, exit 1** — with cc2's complete round-1 fix in place, a *declared* correct proof on a non-critical was still resolved `status=REFUTED`, and a *declared* mistaken proof on a critical was still resolved `status=CONFIRMED, verified=True`. My round-2 fix closes that (see `fix`). Composed and re-verified: falsifier exits 0, correct proof stamps `proof_tristate=ADMISSIBLE`, mistaken one `REJECTED`, statuses stay OPEN, critical → HIL.

**What (b) loses:** all 6,390 archived entries and 121 runs become cross-schema comparisons, and it mints the second verdict taxonomy that `claim_ledger` explicitly refuses. **What (a) loses:** nothing measured — but stated plainly, (a)'s residual is that the declaration is model-supplied; an *undeclared* proof-polarity script still inverts. For criticals the committed CONFIRM-only rule bounds that; for the non-critical silent-retire and the false-CONFIRMED directions the exposure predates this round (it is the Exp 42 class) and no polarity field can close it — only the declaration's future producer can.

**Composition, by the founder's standard (demonstrated advantage, not coexistence):** each guard alone leaves one consumer exposed — cc2's falsifier fails with no fix, passes with cc2's alone; **my falsifier fails with cc2's alone**, passes only with both. Both executed. The composed fix dominates each alone on a named property: consumers-of-the-verdict-field covered, 1/2 vs 2/2. Both seats' round-1 suites plus mine pass together: **18 passed**, and the full targeted battery around the gate and severity: **452 passed in 50.99s**.

**Additive-standard caveat, stated so it is not discovered later:** `verification_polarity` still has **no committed producer** — both guards are consumer-side armor reached today only by tests. Until the founder wires the producer (the step that routes a printed proof), the load is carried by CONFIRM-only, the equipment-failure demotion, and `fix_efficacy` — which exist and are tested. If no producer is ever wired, both guards become the 12th and 13th instances of additions nothing reaches, and cc2's own refutation condition (a) says they should then be deleted together.

## `touches_gamma_or_the_gate`

**No.** `_estimate_gamma`, `_settled_novelty_series`, `_check_gamma_alt_convergence`, `CRITICAL_SEVERITY_THRESHOLD`, and the historical verdict→V mapping (CONFIRMED→1.0, REFUTED→0.0, else 0.5) are all unmodified. My fix adds one branch inside `apply_falsifier_verdicts` entered **only** when an entry declares proof polarity — a condition satisfied by 0 archived entries. The undeclared path is byte-identical, pinned by `test_undeclared_entries_take_the_historical_path_unchanged` and by the 452-test battery.

## `reasoning`

Instruments run: `reverify_falsifier` (4 real proof-artefact re-runs), `spec_verification_factor`/`effective_severity` with spec ON via `wire_module_mirrors`, `apply_falsifier_verdicts` on a real `FindingRegistry` (executed truth table, 3 cases), `_settled_novelty_series`, `_estimate_gamma`, `unverified_critical_count`, the archive scan (8,321 files), pytest (18 + 452 + 3), SymPy exact arithmetic (RSS = 0.12690552, linear = 0.16470000, from rationals), and Wolfram as second falsifier: `wolframscript -code 'N[{Sqrt[0.0392^2+0.0049^2+0.1206^2], 0.0392+0.0049+0.1206},8]'` → `{0.126905516034568, 0.1647}`, exit 0, computed with Wolfram Language (local Wolfram Engine). Key code facts anchoring the mechanism: `_FALSIFIER_RESOLVED_VERDICTS = frozenset({"CONFIRMED"})` (line 6324), the CONFIRM-only branch (lines 7995–8028), `_NON_NOVEL_TERMINAL_STATUSES` (line 10663), asserted-severity classification in the series (line 10697).

## `fix`

- `bench/reference_runner_v3.py` — cc2's round-1 severity guard applied verbatim, **plus** the guard's second half in `apply_falsifier_verdicts`: a declared proof-polarity entry is never status-resolved from its re-run; it takes the existing no-falsifier handling (critical → `UNTOOLABLE` + HIL; non-critical → left to the vote machinery) and is run once through `verify_proof`, with the S_k tristate stamped beside the entry (`proof_tristate`, `proof_raw_verdict`, `proof_reason`) so repair-side evidence is recorded, not burned. No new vocabulary.
- `bench/proof_verify.py` — cc2's module, applied unmodified.
- `bench/tests/test_the_polarity_guard_covers_both_consumers_2026-10-31.py` — 3 tests pinning the composed behaviour and the untouched default path (**3 passed**).
- `scripts/q1_route_a_proof_through_the_finding_channel_2026-10-31.py`, `scripts/q2_reach_of_the_polarity_inversion_2026-10-31.py` — the Q1 truth-table and Q2 reach producers.

## `falsifier`

`bench/tests/falsifier_the_status_channel_is_polarity_blind_2026-10-31.py` — imports the real `apply_falsifier_verdicts`, no retyped copy; real proof scripts against the real fixture. Command: `python3 bench/tests/falsifier_the_status_channel_is_polarity_blind_2026-10-31.py`.

Pre-fix (cc2's round-1 fix fully in place): `FALSIFIED / non-critical with a DECLARED correct proof was silently retired: status='REFUTED' / critical with a DECLARED mistaken proof was confirmed as a real defect: status='CONFIRMED' verified=True / AssertionError, EXIT=1`.
Post-fix: `NOT FALSIFIED: the status channel honours declared proof polarity (non-crit status='OPEN', crit status='OPEN', crit proof_tristate='REJECTED', non-crit proof_tristate='ADMISSIBLE'), EXIT=0`. cc2's own falsifier re-run with both fixes: EXIT=0.

## `strongest_disagreement`

The brief says "no fact appears to be in dispute between you" and sends this round's energy to the severity multiplier. Both halves are wrong. A fact **is** in dispute — the gamma-flattery mechanism — and it resolves against cc2 by execution: the convergence series never reads `V`, so the inversion cannot flatter gamma; what it manufactures on criticals is false CONFIRMED findings, which *delay* convergence. And the severity consumer is the lesser exposure: it is behind a flag armed in 0 of 121 archived runs, while the status consumer — which neither the brief's Q1 nor cc2's round-1 fix examined — mis-handles proofs today, flag-free. The question the founder needs answered is not "does V invert" (it does, trivially, five lines of code) but "which consumer of the verdict field can silently retire or falsely confirm a finding" — and that one was still open after round 1.

Secondary: excluded from composition as out of scope — both seats' round-1 harvests carry identical edits to two unrelated test files (`test_does_filtering_the_stale_constant_repair_two_2026-10-30.py`, `test_the_triage_can_see_the_whole_list_2026-10-30.py`), which look like sandbox staging state rather than seat work; I did not apply them.

## Termination

**4 passes.** Pass 1: mechanism map plus the Q1 end-to-end execution (real proofs, real re-runs, all four consumers). Pass 2: Q2 archive scan — reach 0. Pass 3: composition — applied cc2's fix, found and demonstrated the status-channel gap, built the second-half guard, falsifier bidirectional, 452-test regression green. Pass 4: second falsifiers (SymPy exact, Wolfram attributed above) and the combined re-run — it added **no new above-threshold finding**, so I stop. Disagreement preserved: cc2's inversion stands confirmed; cc2's convergence-manufacture mechanism stands refuted; both statements are evidence, not positions.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/joint_what_is_a_proof_outside_code_2026-10-31/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
