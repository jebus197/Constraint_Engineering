# Is severity ordinal, and must its scale be domain-supplied? JOINT round

Record written 2026-11-12T08:39:45+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

This note preserves, in full and unedited, the joint half of the panel round on
whether severity is an ORDINAL quantity and whether its scale must be supplied
by the domain rather than fixed in the harness.

WHAT WAS REVIEWED, AND WHY IT WAS ASKED AT ALL. The founder raised the question
on 2026-11-11: whether pinning an exact number on severity is an arbitrary and
vacuous exercise once severity is accepted as a quantity each domain already
measures on its own scale, and whether the harness and the models must therefore
be told which scale and which cut to use per domain. The measurement answered
yes on both counts and is recorded as entry B144, the critical cut of 0.7 not
being a severity measurement: z3 returns sat for a strictly increasing
re-scaling that preserves every pairwise order while changing which items fall
above the cut, and unsat for the same attack on a cut named by a distinguished
element of the ordering. A transported cut is invariant; a frozen number is not.

WHY A JOINT ROUND AND NOT A SECOND BLIND ONE. The blind half,
severity_is_ordinal_2026-11-11, collected both seats' answers without either
seeing the other. A blind round alone is half a star topology, and this project
records 15 of 99 archived rounds having had their joint half run. The dispatcher
now refuses a new blind round while an earlier one still owes its joint half,
which is what made this round owed rather than optional.

WHAT THE SEATS WERE ASKED TO DO, AND WHAT THEY WERE FORBIDDEN TO DO. They were
not asked whether they agree, nor whether the other seat is right. A canonical
rule of this project is that there are no votes in CDSFL, and a reply amounting
to concurrence is recorded as a non-answer. They were asked to resolve
disagreement by measurement or to name the measurement that would, to say
whether agreement survives seeing the other's reasoning, and to report any
difference between the brief's quoted file state and the tree they found, rather
than assuming the difference was their own error.

THE SEATS AND THE ROUTE. 2 seats, cc2 and fable, both over the local command
line interface on the Max subscription. 0 paid seats were dispatched, so this
round cost no API credit. cc2 returned 26,768 characters after 35 tool calls in
737.6 s; fable returned 13,629 characters after 26 tool calls in 821.5 s. Both
replies landed complete.

WHAT CC1 DID WITH THE FINDINGS. The substantive outcome is a pairing rather than
a single number: severity for a domain is carried as the consequence measured on
that domain's own named scale together with a harness-computed credence, with
the class weight relocated onto the consequence side and the verification factor
retained rather than deleted. fable's reply reconciles cc2's refutation with its
own count as the necessity and sufficiency halves of 1 statement rather than as
a disagreement, and records that a prior joint round had already warned that
deleting the verification factor without relocating the point at which it vanishes was the trap. Those
findings bear directly on 2 open entries: B144, the critical cut not being a
severity measurement, and B146, the maths model stating the cut as a constant
where it must be a per-domain parameter.

WHAT IS NOT CLAIMED HERE. The seats' replies are evidence of what 2 models said
after reading the tree, and nothing in this note converts them into a finding.
Under this project's rule a finding is confirmed programmatically or by the human
in the loop, never by a model's word, so the design consequence of this round
remains the founder's decision and is held open under his discuss marker.

WHY THIS NOTE EXISTS AT ALL, STATED PLAINLY BECAUSE IT IS A FAULT OF MINE. The
round ran on 2026-11-11 and its output sat only in an ignored directory. The
work-list item covering it was marked DONE on the strength of the round having
been dispatched, and the full record it owed was never written. A commit board
of 2248.44 s refused on 2026-11-12 and named this round in 4 of its 5 failures.
Dispatching a round is not preserving it, in the same way that building the work
is not marking the entry.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# BRIEF — JOINT ROUND on whether severity is ordinal and its scale domain-supplied

**Round:** `severity_is_ordinal_2026-11-11_joint`. Free seats only (`cc2`, `fable`).
**Parent:** `severity_is_ordinal_2026-11-11`, the BLIND half, in which you each
answered this question without seeing the other. Both of your replies landed.
This is the JOINT half: you are now shown the other seat's actual words.

**Tree state:** repository at the commit this brief is dispatched from. Every file
quoted below is quoted AT THAT COMMIT with its line numbers, because a previous
joint round (entry B125) asked 2 seats about a file that had changed since they
answered, so their correct reading read as an error. Report any difference you
find rather than assuming it is your mistake.

---

## 0. WHAT IS BEING ASKED

**NOT being asked:** whether you agree, or whether the other seat is right. A
canonical rule of this project is that **there are no votes in CDSFL**. "I
concur" carries no information and will be recorded as a non-answer.

**BEING asked:** 3 things. (1) Where you and the other seat DISAGREE, resolve it
by measurement or state precisely what measurement would. (2) Where you AGREE,
say whether the agreement survives seeing the other's reasoning, because 2 seats
reaching one answer by one flawed route is not corroboration. (3) The founder has
since made 3 rulings and 1 correction that neither of you had: say what they
change in your answer.

---

## 1. THE OTHER SEAT'S ACTUAL WORDS, VERBATIM

### What `cc2` said — its refutation of P4

```
**P4** | Does not break the model, which asserts existence + order only | **REFUTE AS STATED** — incomplete for exactly the reason above. Existence + order is not enough to support a gate. The model must assert existence + order + a distinguished level. |
| **P5** | Consequence is a property of the application, not the error's form | **AGREE** |
| **P6** | §7.7 is a credence formula wearing a consequence name | **AGREE** (see `q7` for where it fails as credence too) |
| **P7** | `ΔV = Σ V(f)` is inadmissible and must become an order statistic | **AGREE on the mathematics, REFUTE the urgency.** `Σ` fails 4 of 6 relabellings. But the live analogue — `kappa_set` at `_convergence.py:267`/`:303` — is t
```

### What `fable` said — its measurement of where the cut transfers

```
`q4` — The 0.7 cut transfers to exactly one scale

With `x → lo + 0.7·(hi−lo)` (executed): CVSS → **7.0, exactly the High boundary** — expressible as the rank "High or above". FMEA → **7.3**, CTCAE → **3.8**, INES → **4.9** — all **between levels** (brief's own 0.7×5 = 3.5 convention lands between CTCAE grades too). So the frozen cut cannot be carried arithmetically into P3's scales; each θ_d must be a **per-scale frozen level**. Concrete defect in P3 as drafted; repaired in the delivered amendment.

## `q5` — Yes, and here is where

The capability fingerprint dimension **A = mean severity** (`bench/dm/_manager.py:722`, `obs_a`), persisted per model and updated by windowed mean or EMA (~:735-740
```

---

## 2. WHERE YOU DISAGREED, AND IT IS THE CENTRE OF THE QUESTION

**P4 — does the model asserting existence and order suffice?** `cc2` REFUTED it:
existence plus order "is not enough to support a gate", and the model must assert
"existence + order + a distinguished level". `fable` AGREED with P4 and backed it
with a measurement: archived gate decisions "do not depend on the numbering
(301/301 preserved under 3 order statistics)".

**These are not obviously incompatible and that is the work.** `fable` measured
that the ORDERING is preserved; `cc2` argued that an ordering alone cannot site a
CUT. Both can hold. Say whether they do, and if they do, say what P4 should read.

**P6 — is section 7.7's product a good credence formula?** `cc2` AGREED; `fable`
REFUTED, holding that it "fails as credence too". Resolve or sharpen.

---

## 3. WHAT THE FOUNDER HAS RULED SINCE YOU ANSWERED

**(a) The scale and the critical level are DOMAIN-SUPPLIED and now declared.**
`bench/cdsfl_registry/domain_manifest.toml` declares, per domain, a severity scale
and a critical LEVEL — or `none` with a reason where no recognised scale exists.
4 of 10 domains carry a recognised scale; 6 declare none and inherit the
application's. Does that implement your position, overshoot it, or miss it?

**(b) The frozen constant is named as the artefact under refutation and nowhere
as a level.** His correction, verbatim: *"you again appear to be pinning 0.7 as a
meaningful cut point. Haven't we just established that it isn't?"*

**(c) Composition across domains.** His rule, verbatim: *"where two (or more)
quantities across domains don't compose, the solution is straightforward enough,
which is to instruct the models to quote both quantiles in their own specific
context... (The only exception being where a valid conversion between any two
quantities may already formally exist.)"* Tested with pint: 1 inch + 1 cm
composes to 3.540000 cm; 1 m + 1 s is refused. BUT a clinical grade and a
software score are both DIMENSIONLESS, so `CTCAE 3 + CVSS 7.0` evaluates to 10.0
and dimensional analysis cannot refuse it. **Is carrying the scale NAME with the
number sufficient, and what breaks it?**

---

## 4. WHAT HAS BEEN MEASURED SINCE, WHICH YOU SHOULD TRY TO BREAK

**The cut is not ordinal-admissible.** z3 returns `sat` for a strictly increasing
re-scaling that preserves every pairwise order and still changes
`count(severity >= 0.7)`; `unsat` for the same attack on a cut named by a
distinguished element. On the archive's 3,170 severities an affine re-scaling with
Spearman rho exactly 1.0000000000 destroys **1,416 of 1,416** critical calls —
1.000000, Wilson [0.997294, 1.000000].

**174 of those 1,416 turn on a representation tie.** The binary64 nearest 0.7 is
0.6999999999999999555910790149937383830547332763671875, strictly BELOW the real
7/10 — 0.122881 of the critical calls, Wilson [0.106795, 0.141009].

**`fable`'s scale-transfer result, extended.** CVSS v4.0 was confirmed from
first.org's own Table 22: High begins at exactly 7.0. So `fable`'s finding stands
on a primary source. FMEA has **2** landmarks, not 1: 7-8 is *high* and 9-10 is
*safety or regulatory*. 7 was declared as the conservative cut. **Is that the
right landmark, and does a 2-landmark scale change the argument?**

---

## 5. THE FALSIFIABLE QUESTIONS FOR THIS ROUND

**J1.** Reconcile `cc2`'s P4 refutation with `fable`'s 301/301 measurement, or
show they cannot be reconciled.
**J2.** Does declaring a per-domain scale and critical level in a config
discharge P2 and P3, or merely relocate the problem?
**J3.** Carrying the scale name with the number is the proposed enforcement for
the composition rule. Break it.
**J4.** 6 of 10 domains declare `severity_scale = "none"` and inherit the
application's. Is that honest or is it an evasion, and what would distinguish the
two?
**J5.** Does the 174-of-1,416 representation tie change any conclusion either of
you reached, or is it orthogonal?
**J6.** What is the strongest argument that this whole position is wrong and the
project should keep a single project-wide cut?

---

## 6. WHAT WOULD REFUTE THE POSITION

Name a STEM domain with a recognised consequence scale that the manifest declares
`none` for, or one where the declared critical level is not the field's own
threshold. Either refutes the per-domain design as implemented.

## 7. TERMINATION

Answer every question or say which you could not and what you would need. Where
you cannot refute, say which question you tried hardest on.


## What the blind half actually said, lifted byte-exact
These are MECHANICAL extracts, not chosen quotations: each is exactly 240 characters taken at a fixed fraction of the seat's landed reply, which is the span the topology gate itself samples. They therefore begin and end mid-sentence. That is deliberate -- a joint round that reads a summary of its parents is not a cross-check but a second opinion on my paraphrase, so the gate requires the parent's own bytes and these are them. Seats are referred to by POSITION, not by vendor, per the standing instruction to describe measured capability rather than model names.

### Seat 1, reply 38458 characters

At 0.25 of the reply:

```
efore Bench Run 2, not after.

---

## `q6` — the founder's own question

### `q6_notation`

**Short answer: conventional notation already covers it, and the model does not currently use that notation. Nothing exotic is needed; what is need
```

At 0.50 of the reply:

```
exp(t)','log(1+t)']
     phi(median)=25/4   median(phi)=13/2
   LOWER median: non-commuting []
   count >= cut, cut TRANSPORTED : non-commuting []
   count >= cut, cut HELD FIXED  : non-commuting ['t**2','sqrt(t)','exp(t)','log(1+t)','2t']

```

At 0.75 of the reply:

```
brief's own §3.6 table already exhibits four distinct attainable values at *fixed* confidence — `{0.0, 0.225, 0.45, 0.9}` — so the claim is contradicted inside the brief.

The SymPy half fails too. `d(Sev)/dW = C·V` is **≥ 0**, not `> 0`; i
```

### Seat 2, reply 18683 characters

At 0.25 of the reply:

```
ass_weight * ec.aggregated_severity`, a distinct line from the cited :267 (same function).

The census's claim that `reference_runner_v3.py` does no magnitude arithmetic **survives**: I inspected every AST candidate there (10334–21412); all
```

At 0.50 of the reply:

```
ne; the right pair is (sev_d(f), S_v(f)), and §7.7's only correctly-behaving factor, V_ver, is already inside S_v's determinate handling. The key property survives: W·S_v·V_ver(False) = 0 (appendix caution 1, already derived there).

## `q8
```

At 0.75 of the reply:

```
ion — it is the committed producer the project's own evidence rule requires for the amendment's figures.

## `commands_run` (principal, verbatim)

```
python3 scripts/severity_was_never_computed_from_the_model_2026-10-12.py
python3 scripts/
```

## What this joint round is asked to settle

The 2 seats AGREE that section 7.7's product is a credence wearing a consequence
name. They DISAGREE about the repair, and that disagreement is the question.
1 seat argues the universal scale distinguishes at most 2 consequences, so a
single constant is an auditable WRONG answer and per-domain levels are right.
The other argues the project already owns the correct credence in section 7.8's
log-odds fusion, so renaming 7.7 is the wrong repair.

Both cannot be adopted as written. State which pairing the maths model should
carry, name the property your answer dominates on, and say what measurement
would refute you. Disagreement is preserved as information; do not converge for
the sake of converging.


## Produce a fix, and test it

A finding without a fix is INCOMPLETE. A fix without a runnable falsifier that
you have EXECUTED is a hypothesis, not a fix. So for whichever pairing you argue
for, produce the repair and then try to break it.

Write your fix INTO the sandbox repository tree at its real path, as a file. A
fix described in prose, or left in scratch space, is destroyed at teardown and
has not been delivered. Name the path you wrote and the falsifier you ran, and
paste the falsifier's actual output rather than describing it.

Use the harness. The mathematical instruments are available to you and the tool
output IS the evidence: a constraint solver and a symbolic algebra system are
both installed, and a claim about admissibility under re-scaling is decidable by
them rather than arguable. Where a result can be checked a second way, check it.

COMPOSABILITY, as the founder defines it and not as the word is loosely used:
compose 2 repairs ONLY on a DEMONSTRATED advantage over each repair alone, where
the demonstration is a MEASUREMENT and not a judgement, and prefer the single
repair wherever it performs as well. Both candidate pairings below could be
composed; saying so is not an argument for doing it.

## What would refute you

State, before you argue, what result would make your answer wrong. An answer
with no refuting condition is a preference. If a measurement you name would
settle it and you can run it in the sandbox, run it.

## Output shape

Return these fields, each named, in this order.

1. PAIRING — which pairing the maths model should carry, in 1 sentence.
2. PROPERTY — the named property your pairing dominates the alternative on.
3. FIX_PATH — the repository path you wrote your fix to.
4. FALSIFIER_PATH — the path of the runnable falsifier you executed.
5. FALSIFIER_OUTPUT — its actual output, pasted, not summarised.
6. REFUTED_BY — the result that would make your answer wrong.
7. DISAGREEMENT — where you disagree with the other seat's blind reply, quoted.
8. COMPOSABILITY — whether you claim a composed repair, and the MEASUREMENT for
   it if you do, or an explicit statement that you do not claim one.

## Termination

Stop when you have delivered all 8 fields with a falsifier you have executed, or
when you can state precisely which field you cannot complete and why. Do not
converge toward the other seat for the sake of agreement: disagreement is
preserved here as information, and a seat that changes position without new
evidence has added noise rather than signal.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 35 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel severity_is_ordinal_2026-11-11_joint) -->

All instruments have run. Writing up.

---

## 1. PAIRING

**`severity_d(f) = ( c_d(f) , credence(f) )` with `credence(f) = S_v(f) · Ver(verification)`** — the consequence half supplied by the domain on its own named scale, the credence half harness-computed from §7.8's log-odds posterior **times the retained `Ver` factor**, and `W(class)` **relocated out of the credence half** onto the consequence side as the declared 2-level fallback where `σ_d = none`.

This adopts **neither** seat as written. Seat 1's per-domain levels are right about the left half and wrong to leave §7.7's product as the right half. Seat 2 is right that §7.8 already owns the correct credence and wrong that `Ver` is "already inside `S_v`" — it is not, and cannot be.

**The defect neither blind reply caught, which is the finding of this round.** §7.7.1 as committed says *"with `credence(f)` being today's §7.7 product under its own name."* That product is `W(class) · confidence · Ver`, and §7.7 caution 3 states in its own words that *"Consequence magnitude enters `Sev` through `W` alone."* **So the pair put a consequence factor in both components and performed no separation.** z3, over factor values parsed from the live appendix table rather than retyped:

- **B1 `unsat`** — there is *no* evidence with `Ver > 0` on which `credence(HARD) == credence(SOFT)`. The "credence" half is not a function of the evidence; it varies with the consequence class over its whole domain.
- **B2 `unsat`** — for every `c ∈ (W(SOFT), W(HARD)]`, `W·B ≥ c ⇔ class = HARD ∧ B ≥ c`. **Caution 3's collapse travels with the product into the new slot.** Relocating a collapsed product into the second component of a pair does not uncollapse it.

Wolfram Language second-sources the `W(SOFT)` branch: `Resolve[ForAll[{B,c}, Implies[0≤B≤1 ∧ 1/2<c≤1, Equivalent[B/2≥c, False]]], Reals]` → `True`; the matching `Exists` → `False`. (Local Wolfram Engine via `wolframscript`, exit 0, no `Name::tag`, no `$Failed`.) *Computed with Wolfram Language.*

**Why `Ver` is retained rather than folded into `S_v`** — this is where I disagree with seat 2 on a decidable point. SymPy: `solveset(1/(1+exp(−Λ)) = 0, Λ, Reals)` → `EmptySet`; `limit(S_v, Λ→−∞) = 0`, unattained. So `credence = S_v` alone makes the key property **unrepresentable, not merely unstated**. §7.8's own tabulated disproved case scores `S_v = 0.27289178365887057`, not 0. With `Ver` retained, `S_v · Ver(False) = 0` exactly.

**Why `W` is relocated and not deleted** — the additive standard. 6 of 10 declared domains carry `severity_scale = "none"`; where the application supplies no scale either, `W`'s `{SOFT ≺ HARD}` is the only ordering the framework owns. It is retained, demoted, and the fallback reports its scale name as `"constraint-class proxy (2 levels)"` so a reader sees the resolution instead of inferring absent precision.

## 2. PROPERTY

**Separability under the admissibility rule: each component is a function of its own inputs alone, and neither component's gate collapses onto the other's variable.** Measured against the two alternatives on exactly this property:

| candidate right half | class-independent (z3 B1) | key property representable (SymPy) | harness-computed |
|---|:--:|:--:|:--:|
| `W · confidence · Ver` (seat 1 / §7.7.1 as committed) | **no** (`unsat`) | yes | **no** (0 of 3,170 entries carry `confidence`) |
| `S_v` (seat 2) | yes | **no** (`EmptySet`) | yes |
| `S_v · Ver` (mine) | yes | yes | yes |

Mine is the only one of the three that is 3-for-3. That is a dominance, not a preference.

## 3. FIX_PATH

`docs/MATHEMATICAL_APPENDIX.md` — §7.7.1, the "WHAT §7.7's PRODUCT BECOMES" block, amended in place with the corrected pair, the two z3 derivations, the SymPy reason `Ver` survives, the `W` relocation under the additive standard, and an explicit "what this does not fix" paragraph.

Supporting file written: `bench/tests/test_the_credence_half_carries_no_consequence_2026-11-12.py` (4 tests, all passing) — so the fix is executed by a test rather than being an addition nothing reaches.

## 4. FALSIFIER_PATH

`scripts/the_credence_half_still_carries_the_consequence_2026-11-12.py`

It parses the live §7.7 factor table at run time (never retypes it), decides B1/B2/A1/A2 on z3 over the parsed values, decides the `S_v` zero on SymPy, and carries a **mutation test** so a check that has gone blind fails loudly instead of passing vacuously. Reads only the artefact and its repository modules; writes nothing.

## 5. FALSIFIER_OUTPUT

```
==========================================================================
THE CREDENCE HALF STILL CARRIES THE CONSEQUENCE -- producer, 2026-11-12
==========================================================================

1. FACTORS PARSED FROM THE LIVE SECTION 7.7 TABLE: {'W(HARD)': 1.0, 'W(SOFT)': 0.5, 'Ver(True)': 1.0, 'Ver(None)': 0.5, 'Ver(False)': 0.0}
  [ok ] section 7.7 table still declares W(HARD)
  [ok ] section 7.7 table still declares W(SOFT)
  [ok ] section 7.7 table still declares Ver(True)
  [ok ] section 7.7 table still declares Ver(None)
  [ok ] section 7.7 table still declares Ver(False)

2. z3 ON THE PARSED VALUES (the collapse is a property of the SHAPE)
  [ok ] B1  no evidence with Ver>0 makes credence(HARD)==credence(SOFT)  -- z3 -> unsat; unsat means the 'credence' half varies with the CONSEQUENCE class
  [ok ] B2  W*B >= cut  <=>  class=HARD and B >= cut, for every cut in (W_SOFT, W_HARD]  -- z3 -> unsat; unsat means caution 3's collapse PERSISTS inside the pair
  [ok ] A1  a FIXED-VALUE cut is breakable by an order-preserving relabel  -- z3 -> sat
  [ok ] A2  a TRANSPORTED level is not  -- z3 -> unsat

3. SymPy -- WHY `Ver` CANNOT BE FOLDED INTO `S_v`
  [ok ] S_v = 1/(1+exp(-L)) has NO zero over the reals  -- solveset -> EmptySet; so credence=S_v alone cannot represent Ver(False)=0
  [ok ] its infimum is 0 and unattained  -- limit L->-oo = 0
  [ok ] credence = S_v * Ver(False) = 0 EXACTLY -- the key property survives

4. MUTATION TEST -- a check that cannot detect the defect is worthless
  [ok ] the predicate DOES fire on the superseded sentence  -- mutant detected
  [ok ] the predicate does NOT fire on the live section 7.7.1  -- live text repaired

5. REPORTED MEASUREMENT (a separate, UNFIXED defect -- not asserted here)
   call sites of domain_vocabulary.severity() outside the module: 0 []
   _convergence.py still gates on a FIXED VALUE: True
   eta_veto = 0.9  ->  on CVSS v4.0 that is 9.0, the CRITICAL band, while the manifest declares critical_level = 'High' (7.0)

CLEAN -- the credence half carries no consequence factor in the live appendix.
EXIT=0
```

Regression test, same tree:

```
....                                                                     [100%]
4 passed in 28.49s
```

Pre-existing test unbroken: `bench/tests/test_the_cut_is_a_domain_property_2026-11-11.py` → `12 passed in 4.35s`.

**One honest note on the falsifier's own history.** My first version of the pytest check was a bare negative match on the superseded sentence, and it **failed on the repaired file** — because the amendment *quotes* the sentence it supersedes, which is this project's recording convention. I did not loosen the assertion; I replaced the duplicated predicate with an import of the producer's single conjunctive one, so there is one copy rather than two that drift.

## 6. REFUTED_BY

My answer is wrong if any of these lands:

1. **`W` is shown not to be a consequence factor.** If `W(HARD)/W(SOFT)` is re-derived as an evidence weight — e.g. "hard constraints are easier to verify, so the class is informative about truth" — with a measured likelihood ratio, then `W` belongs in the credence half and my relocation is the error. The measurement: `P(claim true | class = HARD) / P(claim true | class = SOFT)` on a population carrying both the class and an adjudicated outcome. If that ratio is `2.0 ± `, §7.7's product was calibrated and I broke it. It is currently unmeasurable — 0 of 3,170 entries carry the class, though a writer now exists.
2. **`S_v` is shown to attain 0 in the implemented verifier set.** If some verifier's `TNR = 0` or `FNR = 1`, the log-odds term diverges and `Λ_total = −∞` is reachable in floating point, giving `S_v = 0.0` exactly — then `Ver` *is* redundant and seat 2's `(c_d, S_v)` is correct and simpler. The §7.8 table shows no such verifier (all four rates in `(0,1)`), but a future verifier with an absolute veto would refute me.
3. **A two-level consequence ordering is shown sufficient.** If a run landing entries with the class populated shows that moving the cut within `(W(SOFT), W(HARD)]` reclassifies entries in a way that tracks real-world impact, then `W` is an adequate `c_d` and the per-domain left half is over-engineering against the simplest-sufficient standard.

## 7. DISAGREEMENT

**Against seat 2**, quoted from its blind reply: *"the right pair is (sev_d(f), S_v(f)), and §7.7's only correctly-behaving factor, V_ver, is already inside S_v's determinate handling. The key property survives: W·S_v·V_ver(False) = 0."*

Its own sentence refutes its own pairing. The equation it writes to show survival, `W·S_v·V_ver(False) = 0`, **contains `V_ver` as a separate factor** — so the key property survives *because `Ver` is written outside `S_v`*, not because it is inside it. `S_v`'s "determinate handling" excludes indeterminate verifiers from `D_det`; it does not produce a zero, and `solveset` returns `EmptySet` for one. If the pair is literally `(sev_d(f), S_v(f))`, the `V_ver` factor in that equation has nowhere to live and the key property is unrepresentable. The repair is one character of structure: the right half is `S_v · Ver`, not `S_v`.

It also writes `W·S_v·V_ver` — retaining `W` in the belief product, which is the very contamination z3 B1/B2 refute. So seat 2 is right about the provenance and wrong about the algebra.

**Against seat 1**, quoted: *"Existence + order is not enough to support a gate. The model must assert existence + order + a distinguished level."* I agree with this and it is the stronger half of its reply — see J1. Where I part from it is on urgency triage: its blind reply calls `Σ` inadmissible but **refutes the urgency** on the grounds that the live analogue is elsewhere. The `kappa_set` sum at `_convergence.py:267`/`:303` is live, is a sum of ordinal severities, and `Σ` is inadmissible under every strictly increasing re-parameterisation I tested (SymPy: `φ(x)+φ(y) − φ(x+y) = −2xy`, zero only when `xy = 0`). Urgency is not reduced by the defect being in code rather than in prose.

## 8. COMPOSABILITY

**I do not claim a composed repair in the founder's sense, and I want to be precise about why, because the shape invites the mistake.**

The left half (per-domain `c_d`) and the right half (`S_v · Ver`) are *not two solutions to one problem* that I am electing to compose on a demonstrated advantage. They are **two components of one object**, and the defect has two independent parts: consequence contamination of the right half, and two-level resolution of the left. The measurement that establishes neither part alone discharges the defect:

- Left half alone (`c_d` on a declared scale, credence kept as §7.7's product): z3 B1 still returns `unsat` → the credence half still varies with the consequence class → consequence is counted twice. **Not discharged.**
- Right half alone (`S_v · Ver`, consequence left as `W`): z3 B2's generalisation at `W ∈ {1/2, 1}` still holds → any cut above `W(SOFT)` tests class and belief and bounds impact not at all, caution 3 verbatim. **Not discharged.**

So both are required by the structure of the object, not elected on a comparative advantage. Calling that "composability" would import the word loosely, which is precisely what the founder's 2026-10-02 ruling forbids. **No composition claimed.**

---

# The round's falsifiable questions

## J1 — `cc2`'s P4 refutation vs `fable`'s 301/301

**They reconcile, and the reconciliation is a quantifier, not a compromise.** They are statements about different objects:

- `fable` measured a property of an **archived decision set**: on those 301, the gate's output is *invariant* under the three order statistics tried. That is an existential over `φ` — "for the φ I applied, nothing moved."
- `cc2` asserted a property of the **model's expressive adequacy**: existence + order does not *determine* a cut. That is a universal — "there is no φ-invariant way to site a cut from order alone."

A universal non-existence claim is not touched by one φ on which nothing moved. And z3 settles the universal directly: **A1 `sat`** — a strictly increasing relabel preserving every pairwise order *does* change `count(severity ≥ cut)` when the cut is a fixed value; **A2 `unsat`** — it cannot when the cut is a transported distinguished element. The archive agrees at scale: an affine re-scaling with Spearman ρ exactly 1.0000000000 destroys 1,416 of 1,416 critical calls while reordering nothing. `fable`'s 301/301 was measured on *order statistics*, which A2 covers; it was never a test of a fixed-value cut, so it never contradicted `cc2`.

**What P4 should read.** Not "does not break the model" and not "the model is incomplete", but:

> **P4.** The model's assertion that `(≽_d, θ_d)` exists is *necessary and not sufficient*. The ordering alone is invariant and determines every order statistic (z3 A2 `unsat`); it does **not** determine a cut (z3 A1 `sat`). A gate therefore requires the distinguished element `θ_d` as a *declared primitive of the domain*, which is additional data the ordering does not supply. `fable`'s 301/301 and `cc2`'s refutation are both correct, at different quantifiers.

**Does my agreement with `fable` survive seeing `cc2`?** On the measurement, yes — I reproduced its scale transfer independently and it is exact (CVSS → 7.000 lands on the `High` floor; FMEA 7.300, CTCAE 3.800, INES 4.900 all between levels). On the *conclusion* it drew from it, **no**: 301/301 is weaker evidence than it reads as, because it tested the invariant family. `cc2`'s route is the one that bears on a gate.

## J2 — does declaring the level in a config discharge P2 and P3?

**It discharges the declaration and relocates the execution, and the relocation is measurable.** `bench/cdsfl_registry/domain_vocabulary.py` validates hard — a scale with no `critical_level`, or a `none` with no `severity_scale_reason`, is a `VocabularyError` rather than a silent pass. That is real and it is more than P2/P3 asked for.

But an AST sweep of `bench/**/*.py` and `scripts/**/*.py` finds **0 call sites** of `domain_vocabulary.severity()`. The module's one importer, `composer.py:911`, uses `resolve_pair`, `is_known`, `default_subdomain`, `subdomains` and `encoding_path` — never `severity`. **No seat prompt carries its domain's scale.** Meanwhile the live gate is `_convergence.py:381`:

```python
return any(ec.aggregated_severity >= self.config.eta_veto for ec in novel)
```

with `eta_veto = 0.9` (`_types.py:91`) — a **fixed value**, exactly the form z3 A1 returns `sat` against. And on the one scale that can receive a number as a rank, `0.9 → 9.0` is CVSS's **Critical** band while the manifest declares `software.critical_level = "High"` (floor 7.0). **The declared level and the executed cut disagree by one band.**

So: P2/P3 are discharged *as specification* and not *as behaviour*. This is this project's own measured failure class — 11 confirmed defects since 2026-08-01 were additions nothing reached. The simplest sufficient wiring is one call site: `_veto` taking the level from `severity(domain)` and comparing a transported level rather than a float. **I did not make that change** — it alters live convergence behaviour on every run and is not what this round asked for — and I have recorded it in §7.7.1 under "what this does not fix" so it is not mistaken for fixed.

## J3 — break the scale-name enforcement

**Broken, two ways, both executed.**

**(a) The name carries no DIRECTION, and the only admissible statistic needs one.** `severity()` returns keys `{domain, scale, levels, critical_level, note, reason, inherits_from_application, composes_from_selected}` — **no direction field**. GHS runs inverted (Category 1 most severe); CVSS, CTCAE and FMEA run ascending. Executed:

```
chemistry levels as returned: ['Category 5', 'Category 4', 'Category 3', 'Category 2', 'Category 1']
max() over them:              'Category 5'          <- the LEAST severe
```

The rule says never sum, **select** — take the maximum. Applied to chemistry from the data `severity()` actually returns, `max` selects the least severe finding in the set. The inversion is stated in `critical_level_note` **prose only**, so a correct consumer must parse an English paragraph to know which end of the list is worse. **A scale name without a declared direction does not make an order statistic computable.** Repair: `severity()` returns `direction ∈ {"ascending","descending"}`, and `levels` is returned in increasing-severity order by contract with a test.

**(b) One name is a FAMILY of scales.** `may_compose("chemistry","chemistry")` returns `True` — *"both report on 'GHS health hazard category (Rev. 11, 2025)', so they are the same scale."* But GHS category numbering is **per hazard class**: acute toxicity, skin corrosion and carcinogenicity are distinct ladders sharing the word "Category". Two findings both labelled `GHS health hazard category` can sit on different ladders, and name equality composes them. The arbiter is string equality, and string equality is coarser than scale identity. Repair: the declared scale string must name the hazard class, or carry a sub-scale field. [VERIFY:current] — the per-hazard-class structure of GHS Rev. 11 is stated from the standard's architecture and was not retrieved from a primary source in this round.

What **survives** J3: the name is *necessary*. pint cannot refuse `CTCAE 3 + CVSS 7.0` (both dimensionless, evaluates to 10.0), so the refusal must be on the name. The name is just not *sufficient*: it needs direction and sub-scale identity before an order statistic is computable from it.

## J4 — 6 of 10 declaring `none`: honest or evasion?

**Honest, and the distinguishing test is mechanical rather than a matter of tone.** An honest `none` is *falsifiable by naming a scale*; an evasion is not. Three properties make it falsifiable here, and all three hold: (i) `severity_scale_reason` is **required** — `VocabularyError` on absence, so the absence must be argued; (ii) `inherits_from_application = true` **names the successor**, so the quantity is not simply dropped; (iii) each reason states a *mechanism* — mathematics: "the consequence is a property of the application, not of the error's form"; physics: "a nuclear result inherits INES; an optics result may inherit nothing."

The distinguishing measurement: **count recognised consequence scales the field owns that the manifest declares `none` for.** An evasion has a non-empty count. I tried to make that count non-empty — see §6 below, where I partly succeeded.

The one place `none` *is* currently doing evasive work: `inherits_from_application = true` names no mechanism for *obtaining* the application's scale. There is no `application` parameter on `severity()` and no caller to pass one. So on those 6 domains the inheritance is declared and unroutable — which is why my pairing keeps `W` as the named fallback with its resolution stated, rather than leaving `c_d` undefined.

## J5 — the 174-of-1,416 representation tie

**Orthogonal to the position, and it strengthens the argument for it.** Confirmed independently with exact rationals:

```
binary64 0.7  = 3152519739159347/4503599627370496
real     7/10 = 7/10
0.7 < 7/10    : True          (difference 4.4408920985006264e-17)
```

It changes no conclusion either seat reached, because both conclusions are about **ordinal admissibility**, and admissibility fails at the level of the *form* `value ≥ constant` regardless of how that constant is represented. The tie is a second, independent reason the same form is unsafe: `0.7` is not the number the author wrote, so 174 of the 1,416 critical calls turn on a rounding artefact rather than on a judgement about consequence. z3 A1's `sat` holds over the exact rationals with `RealVal("7/10")` — no float involved — so the ordinal result does not depend on the tie, and the tie does not depend on the ordinal result.

The practical consequence worth recording: it makes the defect **undetectable by inspection**. A reader auditing `>= 0.7` sees the author's intent, not the executed comparison. A transported level has no representation at all, so it cannot have a representation tie — which is a secondary advantage of the repair that nobody has claimed yet.

## J6 — the strongest case that this whole position is wrong

**The simplest-sufficient standard, aimed straight at it.** Stated as strongly as I can make it:

> The frozen cut's *entire job* is to decide, within a research harness, whether a review round may stop. That decision is **epistemic**, not consequential — nothing ships, no patient is dosed, no blade is machined. The project already measured, on its own archive, that moving the cut from 0.7 to 0.8, 0.9 or 0.95 reclassifies **0** of 3,170 entries on the computed severity, because that severity is three-valued. A constant that reclassifies nothing is not a defect worth ten declarations, four primary-source citations, a new validated vocabulary module and a subdomain taxonomy. The ordinal argument is *mathematically correct and operationally inert*: it replaces one unreachable number with ten reachable ones and a composition rule, in a harness where no gate reads any of them. Measured: `severity()` has **0 callers**. The per-domain design is 0-for-0 on influencing a decision; the single constant is 0-for-3,170. Both bind nothing, and the single constant is one line.

**Why I still hold the position, and the one measurement that would flip me.** The argument above is sound about *today* and wrong about *direction*. The reason the constant reclassifies 0 entries is that `constraint_class` and `confidence` are populated on 0 of 3,170 — the inputs are missing, not the cut. A writer for `constraint_class` now exists. Once a run lands entries carrying it, the cut becomes live, and a live fixed-value cut is the form z3 returns `sat` against on the archive at 1,416 of 1,416.

**The measurement that would flip me:** a run landing entries with `constraint_class` and a harness-computed credence, where moving the cut within `(W(SOFT), W(HARD)]` reclassifies entries **and** the reclassifications track adjudicated real-world impact. That would show a two-level consequence ordering is sufficient, and ten declarations would be surface to go wrong for nothing.

I will also concede the weaker half of J6 outright: the *scale of the apparatus* is defensible criticism even if the position is right. Ten domain declarations with four primary-source citations are the simplest sufficient fix only if they are reached. They are not reached. Until `severity()` has a caller, J6's charge lands.

---

## §6 — what would refute the per-domain design

I tried hardest here, and I have a **partial refutation** rather than a clean one.

**Nuclear and radiological work.** `physics` declares `severity_scale = "none"` and its own reason **names the scale it is declining to declare**: *"A nuclear result inherits INES; an optics result may inherit nothing."* The IAEA International Nuclear and Radiological Event Scale is a recognised consequence scale with levels 0–7 and published landmarks. Yet:

- `physics` subdomains are `general`, `classical`, `thermodynamics`, `quantum` — **no nuclear subdomain**.
- `find bench/directives -iname "*nuclear*" -o -iname "*radiolog*"` returns **nothing**. No nuclear encoding exists, declared `owed` or otherwise.

So the inheritance the manifest describes **has no route**: there is no `(domain, subdomain)` pair that resolves to nuclear work, hence nothing from which INES could be inherited. This is not "a domain with a recognised scale declared `none` by oversight" — the manifest names the scale knowingly — it is **a recognised scale the manifest names and cannot reach.** Under §6's second clause it is a real defect in the design *as implemented*: the honest form is `physics.subdomains.nuclear` with `severity_scale = "IAEA INES"`, a declared `critical_level`, and `owed = true` on the encoding. The repair is a manifest entry, not a redesign, so the per-domain design survives — but it survives with a named gap rather than untouched.

**Second candidate, weaker, flagged rather than asserted.** `chemistry.critical_level = "Category 2"`. GHS's own recognised landmark for acute toxicity is the **signal word**, and the `Danger`/`Warning` boundary does not fall between Categories 2 and 3. If that is right, the declared critical level is not the field's own threshold and §6's second clause is satisfied a second time. I could not settle it: the manifest's own note records that *"the numeric LD50/LC50 cutoffs were not retrieved"*, I had no primary GHS source in this sandbox, and I will not assert a standard's content from recall in a round whose subject is citing scales accurately. **[VERIFY:current]** — the measurement needed is one read of GHS Rev. 11 Annex 1's signal-word assignment per acute-toxicity category.

---

## Termination

All 8 fields delivered with an executed falsifier; J1–J6 answered; §6 answered with a partial refutation.

**Hardest attempt, which failed:** I tried to break the `(c_d, S_v · Ver)` pairing by finding a verifier configuration where `Λ_total = −∞` is reachable, which would make `Ver` redundant and seat 2's simpler pair correct. All four rates in §7.8's table lie in `(0,1)`, so every log-likelihood ratio is finite and `S_v > 0` strictly. I could not construct the refutation from the implemented verifier set, and I have recorded it as REFUTED_BY condition 2 so a future verifier with an absolute veto refutes me rather than being argued with.

**What I could not complete:** the chemistry `critical_level` check above, needing one primary-source read; and the `severity()` wiring, which I deliberately did not change — it alters live convergence on every run, it was not this round's question, and under the additive standard a behavioural change to a gate needs its own measurement rather than being folded into a maths-model correction.

**The declaration I will not make:** this is not convergence. §7.7.1's left half is correct, its right half is now correct, and **neither reaches a gate.** The material defect of the per-domain severity design is unresolved and I have written that into the appendix rather than around it.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 26 recorded tool call(s).

<!-- verbatim-begin: fable (panel severity_is_ordinal_2026-11-11_joint) -->

All evidence is in. The regression producer still exits 0, and its own output records a prior joint round's warning that deleting `Ver` without relocating its zero was the trap — my amendment writes the relocation in explicitly rather than falling into it.

---

## J1 — cc2's P4 refutation vs my 301/301: reconciled as a lemma pair

They are both true and they are necessity and sufficiency halves of one statement. cc2's claim is about **definability**: a total preorder has no distinguished element, so `critical_d` is undefined from order alone — the gate cannot be *sited*. My 301/301 is about **invariance**: *given* a distinguished level transported with the scale, decisions are preserved under every order-preserving relabelling. My measurement never defended order-only; it proved the repaired gate's invariance. So my blind AGREE on P4-as-stated does **not** survive cc2's reasoning — P4 was incomplete as written — and P4 should read what appendix §7.7.1 now asserts: *the model asserts existence of the triple `(≽_d, θ_d, σ_d)` and nothing about any numbering of it*. cc2's refutation accepted; the 301/301 becomes its sufficiency proof.

## J2 — the manifest discharges the specification half and relocates enforcement

Measured: `bench/cdsfl_registry/domain_vocabulary.py` reads and **validates** the declarations (raises on a scale with no `critical_level`, on `none` with no reason — :96–:107) and renders `severity()` with the scale name beside the level. So the declarations have readers. But the gating path is unchanged: `reference_runner_v3.py:1253/:3049` and `audit_closing_window.py:198` still compare a model-asserted float against `CRITICAL_SEVERITY_THRESHOLD = 0.7`. No gate consumer compares `c_d(f)` against a declared level. Until one does, P2/P3 are **declared, not discharged** — and a validated-but-ungated config field sits adjacent to this project's measured defect class of additions nothing reaches. The remainder is B143 (the formula whose inputs are read from nowhere).

## J3 — breaking name-carriage

Four breaks, in increasing depth: **(1)** Enforcement is string comparison, so free-text spellings (`"CVSS"` vs `"CVSS v4.0 base score"`) defeat it — names must resolve by identity against the manifest's declared `σ_d`, or the 3-of-17 vocabulary drift recurs at the scale layer. **(2)** Homonymous versions with different landmark semantics: AIAG 4th-edition severity (RPN era) vs AIAG-VDA 2019 (Action Priority) share the 1–10 range; the edition must be in the name, as the manifest's own v3.1→v4.0 correction demonstrates. **(3)** The exception clause ("a formally defined conversion exists") is too weak as worded: CVSS numeric → qualitative band is formal and citable yet **many-to-one**, so composing through it loses order information; the exception must require an order-embedding, not merely a published mapping. **(4)** Deepest: a name *beside* a number is documentation, not enforcement. `may_compose()` refuses correctly — but only for callers that call it; a bare float pulled out of the `severity()` dict bypasses the refusal, and pint cannot catch two dimensionless grades (the manifest's `arbiter` line admits this). Sufficient only when comparison and composition sites are forced through the vocabulary module or a carrier type whose comparison consults the name.

## J4 — honest, with one measured near-evasion, and the distinguisher is executable

Distinguishers: `none` is honest iff (a) no recognised field-owned scale exists and the stated reason survives a source check, and (b) inheritance is **operational** — a run records *which* application scale was inherited. On (a), all 5 nones survive my refutation attempts (maths: none exists; statistics: none field-wide; physics: INES is event-scoped nuclear/radiological, exactly as the reason states; information science: CVSS inheritance stated; logistics: excursion classes don't generalise). **I could not produce the §6 refutation** — no domain declared `none` has a recognised scale I can name. But the **mirror defect exists on a declared domain**: biology declares CTCAE v5.0 *domain-wide*, and CTCAE is a clinical adverse-event scale — correct for the `biomedical` subdomain, a category error for `natural_world`, `zoology`, `genetics` (3 of 4 subdomains; an ecology finding has no CTCAE grade). The repair is placement, not design: declare scales at the granularity the founder's own correction placed encodings — the subdomain. On (b), `inherits_from_application = true` currently has no run-time mechanism: nothing records the inherited scale, so today it is a promise. That is the line between honest and evasive, and it is checkable: grep a run artefact for an inherited `(value, scale)` pair — today, zero exist.

## J5 — corroborating for the shared half, orthogonal to the disagreement

The 174/1,416 ties (binary64's nearest 0.7 = 0.69999999999999995559…, strictly below real 7/10) show the frozen cut was not even a stable *value* — a class of decisions turned on a representation artefact. Under level-named gates the class vanishes: ranks have no float. It adds one requirement the manifest already satisfies — declared levels must be representation-exact, and all four are strings/integers ("High", "Category 2", "Grade 3", "7"). It bears not at all on the credence-slot question: both candidates are three-valued on the archive, nowhere near a 0.7 tie.

## J6 — strongest case for a single project-wide cut, and its defeater

The manager's selection (§7.11) works a multi-domain finding pool and needs cross-domain ranking; per-domain levels make inter-domain comparison undefined beyond binary critical/not, and the composition rule then mandates quoting both — the manager loses its total order. Add simplicity: one constant audited at 5 sites versus 10 declarations + inheritance + composition rules, against a project record of 11 additions nothing reached. **Defeater, measured:** the total order was fictitious — an order-preserving rescale with Spearman ρ = 1.0 destroys 1,416/1,416 critical calls, and on the computed quantity the archive is three-valued, so the cut's position anywhere in (0.5, 1.0] carried zero information (0.7→0.95 reclassifies 0 entries). Comparability that does not survive relabelling is dependence on a labelling, not a property.

---

## The eight fields

**1. PAIRING** — The maths model should carry `severity_d(f) = (c_d(f), S_v(f))`: domain-supplied consequence on `(≽_d, θ_d, σ_d)` paired with §7.8 Approach B's harness-computed posterior — not the renamed §7.7 product in the credence slot.

**2. PROPERTY** — **Provenance** (the appendix's own term for it: who computed the belief factor), measured as computability on the archive: `S_v` is computable on **3,170/3,170** distinct entries from the recorded `falsifier_verdict`, while the renamed product's model-asserted factor `confidence` is present on **0/3,170** — at a cost of **0** §7.11 decision flips. Secondary dominations, each tool-derived: class-invariance (the renamed product differs by exactly 2× at equal evidence; z3 sat / Wolfram `Reduce → False`), and the correct neutral update (`Λ += 0` vs an unmotivated multiplicative halving).

**3. FIX_PATH** — `docs/MATHEMATICAL_APPENDIX.md` §7.7.1, "WHAT §7.7's PRODUCT BECOMES" (pair corrected; superseded form kept visible; §7.7 retained as the legacy selection heuristic — nothing removed; the key property explicitly **relocated** to §7.11 rather than silently lost). Plus the committed producer `scripts/the_credence_half_is_sv_not_the_renamed_product_2026-11-12.py`, cited from the amendment so the doc and its falsifier reach each other.

**4. FALSIFIER_PATH** — `scripts/the_credence_half_is_sv_not_the_renamed_product_2026-11-12.py` (raises `AssertionError`/prints `FALSIFIED` iff any amendment claim is false; exits 0 otherwise). Executed; plus one Wolfram Language call as second falsifier.

**5. FALSIFIER_OUTPUT** — actual output, in full:

```
[PASS] G1a sympy: P(HARD)/P(SOFT) == 2 at equal (confidence, Ver), all c,v>0  ratio=2
[PASS] G1b z3: class-dependence of P at equal evidence is sat
[PASS] G1c a fully verified SOFT finding gets P-credence <= 0.5  P = 0.5
[PASS] G3a S: D_det empty => S_v == 0.5 == prior, belief unmoved
[PASS] G3b sympy: 0.5*belief == belief has NO positive solution -- the multiplicative 0.5 is never the identity update
[PASS] G4a sympy: sigmoid(Lambda) = 0 has no real solution
[PASS] G4b sympy: the Lambda -> -oo limit is 0 and unattained
[PASS] G4c sympy: FNR < TNR so a lone falsification gives S_v < 0.5  S_v = 0.009911
[PASS] G4c dimensional: FNR < TNR so a lone falsification gives S_v < 0.5  S_v = 0.181818
[PASS] G4c numerical: FNR < TNR so a lone falsification gives S_v < 0.5  S_v = 0.260870
[PASS] G4d veto: SymPy falsified + others verified => S_v < 0.5 (appendix verified line: 0.272)  S_v = 0.272043
[PASS] G4e veto inequality: |log(FNR/TNR)|_sympy > sum of other positive weights  4.6042 > 3.6199

[frame] distinct registries: 67; entries with numeric severity: 3170
[PASS] G2a archive: `confidence` present on 0 entries (candidate P's model-asserted factor has no writer)  present on 0/3170
[info] constraint_class present on 0/3170 (writer exists since B84; population pending)
[PASS] M1 archive: 7.11 selection at >= 0.5 decides IDENTICALLY under both candidates on every entry -- 0 decision flips  flips = 0/3170
[PASS] M2 archive frame is non-empty (else the measurement is void)
[PASS] W1 appendix pair now reads ( c_d(f) , S_v(f) )
[PASS] W2 appendix keeps the superseded form visible and cites this producer
[PASS] W3 section 7.7 is NOT removed (additive standard)

ALL CHECKS PASS (3170 archived entries; 0 decision flips; 4 grounds verified with sympy+z3)
```

Wolfram second falsifier (local Wolfram Engine via wolframscript; values attributed to Wolfram Language): `{{}, 0, True, False}` — σ(Λ)=0 has no real solution; the Λ→−∞ limit is 0; the veto inequality holds in exact rationals; `Reduce[ForAll[{c,v}, …, c·v == c·v/2]] = False` (the renamed product is not class-invariant). Regression: `scripts/no_severity_bound_above_one_half_is_a_magnitude_test_2026-11-06.py` still exits 0 against the amended appendix.

**6. REFUTED_BY** — (a) A committed calibration showing `W·confidence·Ver`, scored as a probability against HIL-adjudicated finding truth, achieves lower log-loss or Brier than `S_v` on the same findings — that restores the renamed product on the only property a credence is for. (b) A measurement that HARD/SOFT class predicts `P(true | same verifier outcomes)` — that would readmit class into the credence (though as `Λ_prior(class)`, still amending my text). (c) Any archived entry where the two candidates' §7.11 decisions differ (`M1 flips > 0`) — voiding my changes-nothing claim. None of the three exists today; (c) was tested against all 3,170.

**7. DISAGREEMENT** — Three, against cc2's blind reply. **(i)** *"the right pair is (sev_d(f), S_v(f))"* — right occupant, wrong name: `Sev(f)` already denotes §7.7's product in the same document, and letter-collision is the pathology the founder paid to fix on 2026-11-11 (the V→Ver rename). The consequence half is `c_d(f)`. **(ii)** *"§7.7's only correctly-behaving factor, V_ver, is already inside S_v's determinate handling"* — false for the property that matters: `S_v` carries Ver's *order* but not its *zero* (SymPy: no real solution to σ(Λ)=0; Wolfram: `{}`; a falsified finding scores 0.0099–0.272, never 0). The zero is a selection property and must be relocated explicitly to §7.11 — the appendix's caution 1 warns that otherwise the key property becomes "unrepresentable rather than merely unstated", and the 2026-11-06 producer's output records a prior joint round where exactly this silent deletion was proposed. My amendment writes the relocation in. **(iii)** cc2's P7 *"REFUTE the urgency"* of Σ→max: `kappa_set` sums `aggregated_severity` at `_convergence.py:267/:276/:303` and feeds the convergence gate at `:364` — an inadmissible sum in a live gating path is material, not deferrable; it needs its own round with a flips-under-max measurement. Conversely I **concede P4**: my blind agreement with it as stated does not survive cc2's argument (J1). Position-change disclosure: I moved on the credence slot from my blind delivery — with the new evidence of G2a, M1, and G4a–e above, not for convergence's sake.

**8. COMPOSABILITY** — I claim a composed repair, under the founder's definition, with measurements: the adopted pairing combines my blind half (per-domain `(≽_d, θ_d, σ_d)` consequence, pair structure) with cc2's credence occupant (`S_v`), repaired on the zero-relocation. Against my blind pairing alone it dominates on **provenance/computability**: 3,170/3,170 vs 0/3,170, at 0 decision flips (G2a, M1 — executed). Against cc2's as written it dominates on **key-property preservation**: G4a proves the zero is unrepresentable in `S_v`, so cc2's form silently loses a property the appendix declares load-bearing; mine relocates it explicitly and G4c–e prove the operational effect (disproved ⇒ rejected) survives in every case. Neither blind half alone carries both measurements; the composition is therefore demonstrated, not assumed.

**Residual finding worth its own entry:** biology's domain-wide CTCAE declaration is a category error for 3 of its 4 subdomains (J4) — scale declarations belong at subdomain granularity, exactly where the founder's 4-subdomain correction placed encodings. I tried hardest on §6's direct refutation (a `none` domain owning a recognised scale) and could not produce one; the biology placement defect is the closest surviving relative.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/severity_is_ordinal_2026-11-11_joint/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
