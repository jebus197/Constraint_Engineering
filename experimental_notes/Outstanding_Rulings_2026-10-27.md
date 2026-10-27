# Outstanding rulings — 2026-10-27

**21:50 GMT. Branch `sim/shakedown-2026-09-29`, HEAD `2534c614`, pushed, tree clean.**

Every decision currently waiting on the founder, with its evidence and a recommendation. Each carries its register identifier so none can be lost. Two of his instructions of today are already carried out and are reported first, because the rest reads against them.

## Already carried out today, on his instruction

> "Revert to 3 and fix the gamma arm."

**The required quiet run is 3.** FOLLOW was run before the edit: 36 configuration files pin the value and **all 36 belong to experiments with an archived run**, so no live configuration changed and his standing no-rewrite ruling is untouched.

**The gamma arm is repaired, and the defect was precisely locatable.** The minimum gamma across all 8 premature closes is **0.3173**; the threshold sat at **0.30**, just below that entire distribution. It therefore blocked **0 of 8** premature closes while still blocking **2 of 22** sound ones. Fisher exact that it blocked premature more often than sound: **p = 1.000000**. Its only effect was to block correct closes.

| threshold | premature blocked | 95% Wilson | sound blocked | 95% Wilson |
|---|---|---|---|---|
| 0.30 (old) | 0 of 8 | [0.0000, 0.3694] | 2 of 22 | [0.0253, 0.2781] |
| **0.41 (applied)** | **4 of 8** | [0.2152, 0.7848] | **2 of 22** | [0.0253, 0.2781] |
| 0.4585 (Youden) | 6 of 8 | [0.4093, 0.9285] | 7 of 22 | [0.1636, 0.5268] |

0.41 was chosen because it **dominates** rather than trades, which is what `additive-standard` requires. One-sided exact test **p = 0.0293545535**, cross-verified between scipy and Wolfram to 10 decimal places.

**And a correction to something previously reported.** The producer behind "the gamma arm blocked 0 of 23 premature windows" passed an all-zero critical history into the gate, so every call took the gate's **vacuous-curve branch** — the branch that lets a panel reviewing a genuinely clean document converge, and which returns a verdict without consulting gamma at all. That headline was never a measurement of the gamma arm. Only 2 of the 23 windows are genuinely of that kind. Producer fixed; the original claim survives its own correction.

---

## 1. The gamma threshold — keep 0.41, or move to 0.4585 — **[qs:92f807974742]**

0.4585 catches 6 of 8 rather than 4, but costs 7 false blocks rather than 2 — it buys safety by spending extra rounds on roughly 1 in 3 runs that were closing correctly. That is the time-and-money trade he has been adjudicating, so it is his call.

**Recommendation: keep 0.41.** It is the only value that improves on the old setting at no cost, and 8 positive cases is too thin to justify paying for more.

## 2. Does the 0.7 severity cut match its own rule book — **[qs:c2e25a1e79c1]**

His assumption about 0.7's origin is **refuted by the record**. `CRITICAL_DEFINITION_PREREG_2026-05-18.md`:

> "The mathematical appendix documents severity thresholds 0.0 / 0.3 / 0.5; 0.7 was an undocumented code convention (F6)... the single largest cooking vector identified by the 2026-05-17 γ-hardening confer and the 2026-05-18 definitional confer (both unanimous on this point)."

It was made defensible by freezing a consequence rubric with 0.7 as its proxy. **Whether the proxy encodes the rubric is separately measurable, and the one time it was measured the answer was chance**: kappa = **−0.0227**, Fisher p = **0.78**, recorded in his own `additive-standard` directive. Never resolved in the other direction.

**Recommendation: yes it can be made accurate; the method is an agreement measurement against the frozen rubric. Not while convergence is still open.**

## 3. Can an adaptive quiet-round measure exist — **[qs:db9fb60889f5]**, **[qs:507deab063d2]**

A measurement built today asks what neither the withdrawn rule nor the external brief tested: can anything recorded at the moment of closing separate a premature close from a sound one?

| signal | role in the external brief | AUC | 95% CI | |
|---|---|---|---|---|
| `novel_this_round` | S1 finding silence | 0.3097 | [0.1067, 0.5126] | **blind** |
| `rho` | S2 residual stability | 0.2576 | [0.0000, 0.5193] | **blind** |
| `cross_model_diversity` | S4 panel split | — | — | **not recorded at fire points** |
| `findings_count` | *not proposed* | **0.9345** | [0.7978, 1.0000] | p = 0.002163 |
| `registry_total` | *not proposed* | **0.8542** | [0.6679, 1.0000] | p = 0.009477 |

**Richness predicts remainder.** A close is likelier premature when the run has already found a lot; local quiet predicts nothing, which is also why the gamma arm was weak.

The obstacle is **8 positive cases**. The independent audit under ruling 5 used 2,416 labels and still found its model uncalibrated as delivered. Fitting on 8 is how 3 and 7 happened.

**Recommendation: stop proposing rules, start labelling closes.** Pre-register the signal, threshold rule and decision metric now; fit when at least 30 labelled closes exist, against the 8 available now. Every future run yields one labelled close. That turns an unsettleable argument into a countdown.

## 4. The stagger value before any panel or experiment — **[qs:6b0997d1f6b9]**

**Recommendation: accept 20 seconds** — the value used in the 2026-10-25 panel, which completed cleanly with both seats returning.

## 5. Runway placement for decision-model research — **[qs:01e5959468cf]**

TypeSafe AI, Jev, System One, RLCD and the Noul are **all real**; the external brief reported them accurately, which is useful calibration on it. The valuable source is the independent audit, [arXiv:2609.24052](https://arxiv.org/pdf/2609.24052) (Rafe & Das), which audited against 2,416 blinded labels *because* "the developer has published no calibration metrics":

- "the typed model and one frontier arm are **not calibrated as delivered**"
- "**Calibration varies by model rather than by paradigm, so each model must be audited**" — this project's own position, arriving independently from outside
- Recalibration on domain labels cut calibration error **3.3×** — fixable, but only with your own labelled data
- A **resolution floor** bounds calibration error for rare events on a 2-decimal grid, and premature convergence is rare

**We do not need it, and cheaply so:** `findings_count` discriminates at 0.9345, deterministically, free, from a column already in the logs.

**Recommendation: accept the post-BR2 placement, and take the audit's *method* as the useful part rather than the product.**

## 6. Does proof-backed severity remove the model-voting risk — **[qs:0c69884fa97f]**

His argument of 2026-10-25 is plausible and consistent with the evidence — the longest quiet run observed is 6 and 7 never occurs — but **unmeasured**. Recording it as established would be the flattering-measure failure the record names 3 times.

**Recommendation: measure it.** The question is whether a finding's recorded severity proof actually *determines* its classification, or whether the classification arrives another way and the proof is written after.

## 7. Run the blinded-depth test — **[qs:3cef02fdd3bb]**

The depth/breadth directive carries a 2-sided claim of which 1 side is measured (10 of 12 errors on 2026-10-11 were catchable by reasoning first). The tunnel-vision half is his hypothesis, with a named test and an explicit decision rule.

**Recommendation: run it, after the convergence work** — it needs past defects classified by which context first surfaced them, which is a sizeable manual pass.

## 8. Wire the discipline checker's own test files into the commit check — **[qs:a66794e63539]**

**[qs:a66794e63539]** None of the 3 files guarding the FFAFP checker is collected by the commit hook, which is why 4 sat broken or flaky unseen while it reported 1,439 passing on 3 occasions. Adding them was **deliberately reverted**: entry **B37** records that a test running the hook's whole 70-file list inside the suite *deadlocks* on 8 GiB, and B37 needs his ruling on exactly that.

**Recommendation: rule on B37 first.** Until then they stay out and the gap is recorded rather than silently accepted.

## 9. Resume the master task list — **[qs:49c2c0ed167e]**

Paused on his instruction; the pause file carries his own words and the Stop gate honours it. **69 workable tickets** behind it. Four master-list entries are OPEN and unruled: **B35, B36, B37, B41**.

**Recommendation: resume once rulings 1, 3 and 8 are given** — all three change what the list should contain.

## 10. The unresolved measurement disagreement — **[pf:798cb50b9126]**

One seat computes 32 and 16 of 53 where this analysis computes 34 and 21. Direction agrees, stronger on the seat's numbers, cause unestablished. Its wider point is conceded: those 3 figures were typed prose, not declared figures.

**Recommendation: park it.** It bears on no decision above and is recorded so it cannot vanish.

---

## On working hours

He observed he has regularly been kept up past 5am supplying verdicts. Taken — and this document exists partly so decisions can be answered at a time of his choosing rather than live.

Written under CDSFL note standard v1.8.
