# The 0.7 severity proxy has never been tested where severity varies

**Prepared 2026-10-28. Branch `sim/shakedown-2026-09-29`.** This answers the registered question `qs:c2e25a1e79c1`, which the founder promoted ahead of the convergence condition an earlier ruling had made it conditional on. His instruction, verbatim: *"Then do the measurement first."*

## The answer

The measurement was run, and the result is not what the project's own record says it is. The agreement figure cited for 8 weeks — a Cohen kappa of **-0.022688** with a Fisher exact **p = 0.778818** — reproduces exactly. But it was computed on a corpus whose severities all lie in **[0.65, 0.74]**, a window **0.09** wide. Power against a strong relationship is **0.144250**: the design would miss a real and strong association about 85 times in 100. The figure is **uninformative** about the proxy, not negative about it. Those are different claims, and the project has been making the stronger one.

## What the two instruments are

The harness treats a finding as critical when its severity reaches **0.7**. That threshold, applied to a number each model asserts about its own finding, is the proxy. The alternative is a 5-clause consequence rubric frozen in advance at `bench/exp40_baseline/CRITICAL_DEFINITION_PREREG_2026-05-18.md`, which asks what would happen if the defect were left in place. Whether the two agree is a real question about whether the convergence gate measures consequence or collects opinions.

## The stored result, reproduced exactly

The rubric was scored blind against 286 archived findings on 2026-09-02; the record is `experimental_notes/adversarial_records/rubric_adherence_audit_0C8_2026-09-02.json`. 259 were judgeable; 27 were marked unjudgeable because the stored text broke off before the defect claim appeared.

|  | rubric CRITICAL | rubric NON_CRITICAL |
|---|---|---|
| severity >= 0.7 | 114 | 67 |
| severity < 0.7 | 51 | 27 |

Observed agreement **0.544402** against an expected **0.554509**, which is where the negative kappa comes from. Odds ratio **0.900790**, 95% CI **[0.516836, 1.569980]**. Two independent computations of kappa agree to **1.63e-16**; the Fisher p was confirmed to 9 decimal places by an exact arbitrary-precision calculation.

## The obvious explanation was ruled out first

Cutting a 10-valued variable at one point discards information, so the cut itself was the first candidate. It is not the cause. Treating severity as continuous inside the band predicts the rubric verdict no better: logistic slope **-4.199407**, **p = 0.387828**; Mann-Whitney **p = 0.308546**. The mean severity of NON_CRITICAL findings, **0.695426**, is marginally *higher* than for CRITICAL, **0.692424**. The null survives removal of the dichotomy.

## The corpus is a boundary band, and that is the explanation

| quantity | audited corpus | whole archive |
|---|---|---|
| severity range | [0.65, 0.74] | [0.0, 1.0] |
| standard deviation | 0.026915 | 0.224319 |
| entries | 259 judgeable | 3,237 across 62 runs |

The band holds **0.132839** of all archive severities. A fitted slope's standard error scales inversely with the predictor's spread, so the restriction inflates it **8.3344**-fold. This is not asserted from theory: the analytic standard error **4.801159** matches the real fit's own **4.862883** to within **1.3%**, validating the power model on the actual data.

## What the design could and could not detect

- Minimum detectable slope at 80% power: **13.450855**, confirmed by simulation at **0.798250** against a 0.80 target.
- A strong relationship — P(CRITICAL) running 0.10 at severity 0 to 0.90 at severity 1 — is a slope of **2 ln 9 = 4.394449**, over 3 times smaller.
- **Power against that strong relationship: 0.144250.**

## The decisive test

Inside the band the 0.7 cut separates groups whose mean severities are **0.709171** and **0.657179**, a difference of **0.051992**. Under the strong relationship that implies an exact expected marginal odds ratio of **1.256464**. The first-order `exp(beta . delta-mean)` step gives **1.256682**, a relative error of **0.0174%**, so nothing here rests on the approximation; the exact figure is the one quoted. The measured interval **[0.516836, 1.569980]** contains it, and also contains **1.0** — so this corpus cannot tell the two hypotheses apart.

**And the stronger statement.** "Inside the interval" says only that the observation is not ruled out. Simulating 20,000 draws under the strong hypothesis, **0.792050** of them produce a point estimate inside the *same* measured interval, median **1.260417**. The observation is the **modal outcome** under the hypothesis the project's directive treats as excluded. That is the formal sense in which the measurement decided nothing.

## The falsification the finding survived

If range restriction were a blanket excuse it would make the rubric's own readers look unreliable in the band too, collapsing the finding into "the labels are noise". It does not. On the 93 items both judged, the 2 blind readers agree with each other at kappa **0.836883**, raw agreement **0.924731**, Fisher **p = 6.230872e-17**, while agreeing with the proxy at kappa **+0.016913** and **+0.157562**, neither significant. Restriction bites the continuous predictor, not the binary judgement both readers make. The labels are sound; only the comparison with the number is crippled.

## Sample size is not the problem

Replacing the band severities with **the same 259** drawn from the full archive raises power against the strong relationship from **0.144250 to 1.0000**, and drops the minimum detectable slope from **13.450855 to 1.7380** — well below the strong relationship's 4.394449. The entire deficit is the window's narrowness.

## A second limit analysis cannot repair

The audit's method line records that severity was *"withheld and redacted from 80 of 286 texts"*. **No per-item redaction flag is stored**, so those 80 cannot be located. Up to **206 of 259** verdicts may have been formed with the number in view. No reanalysis fixes this; only a fresh adjudication recording its own blinding item by item would.

## "Only the band matters" is false, measurably

The strongest objection to all of the above is that the convergence gate only ever acts *at* the cut, so in-band agreement is the only agreement with any operational bearing. It does not survive contact with the archive. Of 3,237 registry entries, **2,807** — **0.867161**, Clopper-Pearson **[0.854982, 0.878672]** — were classified at a severity the audit never examined: **1,119** above 0.74 and **1,688** below 0.65.

Worse for the objection: **1,119 of the 1,408 critical calls** the gate has ever made, a share of **0.794744**, sit *above* the band. Those are the gate's **confident** classifications. A disagreement there is more consequential than one at the cut, not less, because nothing about a severity of 0.9 invites a second look.

## What this changes in the project's own directive

`.claude/CLAUDE.md` cites this kappa as the reason a proposal to replace the model-derived severity with the rubric was wrong, describing the rubric as one measured as *"agreeing no better than chance"*. **The founder's catch of that proposal stands** — the replacement acts precisely at the cut, and at the cut the band did measure chance. What is **not** supported is the general claim, because outside the band the measurement is silent. The directive needs the band qualifier it lacks. This corrects a justification the assistant supplied, not the decision it was used to support.

## The costed ask

| full-range sample | simulated power vs the strong relationship |
|---|---|
| 35 (the closed form's answer) | 0.6472 |
| 50 | 0.8397 |
| 63 (already costed) | 0.916500 |

About **48** items reach 80%. The **63**-item adjudication already costed from an exact power calculation on the measured discordance is sufficient and conservative. **The closed form must not be quoted**: it says 35, where simulation gives 0.6472. Supplying the labels is a founder task — peer-model CONFIRM votes are forbidden as evidence in this project, and no other ground truth exists.

## Reproducing every figure

Producer: `scripts/the_severity_proxy_was_never_tested_2026-10-28.py`, which recomputes all of the above from the stored audit and the archive with nothing carried over as prose. Guard: `bench/tests/test_the_severity_proxy_was_never_tested_2026-10-28.py`, which **executes** the producer rather than reading its source text, and holds 31 assertions. 4 deliberate reversions turn it red across 10 distinct assertions: moving the cut off 0.7; widening the corpus to full range; counting the 27 unjudgeable items as non-critical instead of excluding them; replacing the second reader's verdicts with noise. The second reversion is the condition under which this finding is **retired**, which is why it is tested rather than described.

Written under CDSFL note standard v1.8
