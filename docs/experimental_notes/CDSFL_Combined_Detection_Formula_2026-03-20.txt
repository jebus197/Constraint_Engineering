# CDSFL Combined Detection Formula: Plain English Explanation

**2026-03-20**

---

## The Problem

The existing formula in the white paper answers one question: if you throw more machine passes at a problem, how much more likely are you to catch errors? Each pass has some probability of finding a flaw. More passes, more chances. But with diminishing returns — correlated machines share blind spots, so the tenth pass from the same architecture catches far less than the first.

What the formula never addressed is what happens when the human enters the picture. Currently, the human in the loop sits outside the maths entirely. They are described qualitatively as "the domain expert reviews," but never quantified. Your observation exposed why that is a problem: if the framework's entire premise is that unverified output should not be trusted, then treating the human's contribution as a black box outside the formula is exactly the blind acceptance the framework was designed to prevent.

---

## The Solution

The new formula brings the human inside.

It splits detection into two independent streams. The machine stream is everything already in the white paper — multiple passes, diversity discounts, flaw classes. The human stream is new: the human in the loop running their own passes, with their own detection probability, using their own methodology. The combined system catches everything either stream catches independently.

---

## Priming Correlation

The critical variable is the **priming correlation**. This measures how much the human's independence is compromised by having already seen the machine's output. If the expert reads the machine's analysis before doing their own thinking, they are cognitively primed. They start reasoning within the machine's framing. They are more likely to catch what the machine flagged as uncertain, less likely to notice what the machine confidently got wrong. Their blind spots begin to correlate with the machine's blind spots — which is precisely the failure mode the whole framework exists to prevent.

The numbers are stark:
- A good domain expert using **formal methodology, working independently** of the machine output pushes combined detection from roughly 50% to **96%**.
- The same expert, but **passively reviewing after reading the machine's work**, drops to about **65%**.

Passive review does not just reduce the human's contribution. It nearly eliminates it. The human becomes a rubber stamp with domain credentials.

That is the quantitative backing for the instinct that accepting blind CDSFL machine output contradicts the principle that you do not need to blindly accept machine output.

---

## Methodology Formality

The second component is **methodology formality**. The remark that informal methods should be discouraged turns out to be a **2.5 times difference** in detection probability. Same expert, same domain knowledge. The only variable is whether they apply a structured falsification process or rely on informal judgment.

Expertise is necessary but not sufficient — it is the floor. Methodology is the multiplier. An expert without method catches about a third of what the same expert with formal method catches. The parenthetical advice about methodology is the single largest lever in the formula after independence itself.

---

## Pluggable Domain Variables

The extensible part — the pluggable domain variables — is simpler than it sounds. The base detection probability for any human expert depends on two things: how much they know (expertise) and how rigorously they apply what they know (methodology). But in any specific domain, other factors matter:

- A structural engineer with access to material test data detects more than one without.
- A clinician under time pressure detects less.
- A regulatory specialist familiar with the specific jurisdiction catches things a generalist misses.

The formula provides slots for these variables. The domain operator decides which ones matter in their context and estimates their magnitude. The maths then shows the consequences — what the combined system's detection probability actually is, given these inputs. When no domain variables are specified, the formula collapses to the base case: expertise times methodology, nothing more. No unnecessary complexity when it is not needed.

---

## Nesting

Every simpler model already in the white paper nests inside this one. Remove the human passes, you get the existing machine-only formula. Set everything to uniform and independent, you get the original cumulative detection formula. The new formula does not replace anything — it generalises what was already there to include the component the framework always described qualitatively but never formalised: the human expert as an active, independent falsifier with quantifiable detection characteristics.

---

## The Key Takeaway

| Scenario | Combined Detection |
|---|---|
| Primed expert, informal methods | Barely better than machine alone |
| Independent expert, formal methodology | Approaches 98% |

The gap between those two scenarios is enormous, and it is entirely determined by **protocol decisions** — ordering and methodology — not by the expert's raw ability.
