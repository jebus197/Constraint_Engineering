# CDSFL Cognitive Curves Analysis

**24 March 2026**

---

## Full Bench Test Progress

The full bench test is running. 11 of 104 runs completed after approximately 6 hours. At the current rate of roughly 35 minutes per run, the estimated completion time is approximately 2.5 days from when it started, so around Wednesday evening.

Early results from the first 3 tasks show the expected gradient emerging.

- **Task ft-001** (mathematics): Control found 10 hard findings. HIL found 1. CDSFL found 8. CDSFL+HIL found 15 and was the only condition marked as resolved.
- **Task ft-002** (broader task): Control found 27. HIL found 4. CDSFL found 43. CDSFL+HIL found 23. This is an anomaly where CDSFL alone outproduced CDSFL+HIL — discussed below.
- **Task ft-003**: Control found 19. HIL found 2. CDSFL found 31. CDSFL+HIL is still running.

HIL is consistently the weakest condition, finding 1, 4, and 2 across the three tasks. The 500 character expert hint with generic self iteration is not enough to match structured methodology. This is marked as a condition to revisit in a future bench run with more realistic expert conversation patterns.

---

## The ft-002 Anomaly

On task ft-002, CDSFL alone found 43 hard findings while CDSFL+HIL found only 23. This is counterintuitive because the full methodology should outperform structure alone.

Looking at the per-model curves reveals the likely explanation. Under CDSFL alone, CC produced a non-monotone curve of 3, 2, 3, 4 — that spike at the end is suspicious. DeepSeek was near flat at 3, 2, 1, 1, 1. Under CDSFL+HIL, the curves were cleaner: CC showed gentle decay at 2, 2, 2, 1; DeepSeek was near flat but at a lower starting point.

The likely explanation is that CDSFL without expert guidance lets all 5 models scatter across a wide error surface without direction. More findings, but potentially more noise. CDSFL+HIL focuses the search, producing fewer but more targeted findings. The quantity versus quality distinction applies here. Without the verification scores on individual findings we cannot confirm this definitively, but the curve shapes support it. CDSFL alone has more non-monotone spikes suggesting noise. CDSFL+HIL has more clean decay suggesting signal.

---

## Cognitive Curves for Human Models

During analysis of the bench test results, a significant extension of the decay curve framework emerged. The D, v-bar, A, C capability fingerprint — originally designed to measure AI analytical capability — could potentially be applied to measure human cognitive patterns during expert AI interaction.

If you record a human expert reviewing a proof or debugging code alongside an AI system, round by round, finding by finding, their per-turn discovery rate produces the same kind of curve as an AI model. That curve is a cognitive fingerprint.

- An expert who scans comprehensively and exhausts surface issues quickly produces **steep decay**.
- A methodical expert who works sequentially through constraint domains produces **gradual decay**.
- An expert who pattern matches without deepening produces a **flat line**.
- An expert who has genuine insights after apparent stagnation produces **non-monotone spikes** — the eureka pattern.

These are different cognitive strategies, and they are measurable from the same data the bench test already collects.

---

## Where Human Cognitive Curves Could Be Significant

**Cognitive science.** Measuring how experts process complex information under different tool conditions. Does AI assistance make experts faster (steeper decay)? More thorough (higher total findings)? Or lazier (flatter curves and deference to AI)? This connects directly to the automation complacency literature.

**Education.** Students who show decay curves on problem sets are genuinely learning — they exhaust what they understand and reach their limit. Students who show flat curves are performing rote operations without deepening. The curve shape becomes a diagnostic for genuine understanding versus surface performance.

**Professional certification.** Does this expert's cognitive curve during a case review match the expected profile for their claimed expertise level? The curve replaces credential checking with performance measurement. This is exactly the CDSFL calibration thesis.

**AI user experience design.** Which interaction patterns produce the best human cognitive curves? If brief expert hint then self-iteration produces flat human curves, while interactive bidirectional discussion produces steep decay curves, the interaction design directly affects cognitive performance. You could optimise the AI interface for human cognitive outcome, not just for user satisfaction or engagement metrics.

---

## The Bidirectional Feedback Loop

The founder identified a potentially significant feedback mechanism. If optimal human cognitive curves can be mapped with reasonable accuracy, these could be used not only to produce better prompt engineers, but could potentially map back onto AI cognition patterns themselves.

The loop works as follows:
1. Measure human expert curves on analytical tasks.
2. Use those patterns to design better AI interaction protocols.
3. The improved AI produces better results.
4. Humans review those results.
5. Human curves improve from better AI interaction.
6. The cycle repeats.

This is co-evolution — the same mechanism that drives CDSFL self-improvement. The methodology improves the tools, the improved tools improve the methodology. Adding the human cognitive dimension makes it **three-way co-evolution**: methodology, AI capability, and human cognitive performance all improving together.

---

## Mapping to Domain Expert Tradeable Configurations

Under the complete CDSFL schema, domain expert configurations are tradeable assets. A verified expert encodes their knowledge into a constraint box that other practitioners can use. Adding the cognitive curve means the configuration is not just *what* the expert knows, but *how* they apply it.

A structural engineering configuration might include instructions like: "prioritise load path analysis in rounds one and two, check material fatigue in rounds three and four, verify safety factors in round five." That is a cognitive strategy, not just a knowledge set.

This makes the configuration more valuable and more verifiable. You can check whether following the strategy produces a decay curve that matches the expert's own curve. If it does, the strategy transfers. If it does not, the strategy is expert-specific and less generally useful.

---

## Feeding Curves into Genesis Trust Scores

Currently trust scores in Genesis reflect outcomes — did the expert find real issues? Adding cognitive curves means trust scores also reflect process: did the expert demonstrate genuine analytical depth?

An expert who finds 8 real issues with a clean decay curve (indicating genuine analysis converging on truth) earns more trust than one who finds 8 real issues with a flat curve (which might indicate luck, pattern matching, or churning with occasional hits). The process dimension adds information that outcomes alone do not capture.

---

## Ethical Considerations

**Privacy.** Cognitive curves are deeply personal data. They reveal how you think — your scanning patterns, your depth of analysis, your cognitive fatigue profile, your tendency toward breadth versus depth. This is more invasive than performance metrics. Performance says *what you did*. Cognitive curves say *how your mind works*.

**Neurodiversity.** If the system defines optimal cognitive curves, it systematically advantages people whose natural cognitive style matches that optimum. People with ADHD might show non-monotone curves with distracted scanning punctuated by sudden deep insights. People with autism might show extremely steep initial decay from exhaustive systematic scanning. Both can be highly effective analysts, but their curves look different from each other and from any assumed average optimal. A system that rewards one curve shape penalises valid cognitive diversity. The specific curve shapes for neurodivergent populations are not established and this observation is speculative.

**Goodhart's Law.** If people know their curve is being measured, they may game it — producing artificial decay patterns rather than following their natural cognitive process. This is the same gaming risk identified for AI models, but harder to detect in humans because we cannot inspect their reasoning the way we can inspect model output.

**Consent and power.** Who is measured? Who defines optimal? In a workplace, if your employer measures your cognitive curve and uses it in performance assessment, that is a significant power asymmetry. In Genesis's voluntary marketplace, the expert chooses to have their curve measured as part of earning trust. The consent model matters enormously.

**Proposed ethical framework:**
- Cognitive curves are offered by the expert as evidence of capability, never extracted without consent.
- The expert controls whether their curve is visible.
- The system rewards verified outcomes first, cognitive curves second.
- No one is penalised for an unusual curve shape that produces good outcomes.
- Diversity of cognitive styles is explicitly protected.

---

## Novelty Assessment

The individual components exist in the literature. Cognitive curve measurement exists in learning analytics. Process mining exists in workflow analysis. Trust mechanisms exist in reputation systems. But the specific combination — using empirically measured cognitive decay curves as design inputs for AI interaction patterns, as trust signals in a decentralised labour market, and as tradeable components of domain expert configurations — does not appear to have been articulated previously. This should be verified against current literature.

---

## Falsifiable Questions

1. Do human cognitive curves on analytical tasks show consistent patterns within domains? If structural engineers consistently show similar curve shapes that differ from software engineers, domain-specific cognitive profiles exist and are measurable.

2. Does following a human-derived cognitive strategy improve AI review performance compared to unconstrained AI review? Directly testable on bench test tasks.

3. Does cognitive curve measurement change human behaviour through the Goodhart effect? Testable by comparing expert performance when they know versus when they do not know their curve is being measured.

4. Does cognitive curve diversity correlate with review quality in multi-expert teams? If teams with diverse cognitive curves outperform teams with homogeneous curves, diversity protection is not just ethical — it is functional.

5. Can AI interaction design be optimised for human cognitive curve shape? If different AI prompting strategies produce measurably different human decay curves on the same tasks, the interaction design is a controllable variable that affects cognitive performance.

6. Does the bidirectional feedback loop converge? If iterating the measure-design-measure cycle produces measurably better outcomes each iteration, the co-evolutionary mechanism works. If it plateaus or diverges, the feedback loop has limits that need to be understood.

These are research questions for a programme of work extending well beyond the current bench test. But the bench test produces the first dataset where some of these could be explored by analogy — specifically whether the 5 AI models' cognitive curves under different conditions show the patterns that would make human curve measurement meaningful.
