# Experiment 41 — Convergence Investigation (plain English)

2026-05-22 (BST). Constraint Engineering / CDSFL.

## What happened

Experiment 41 reviewed a fixed, 438-line piece of mathematics (the convergence detector) for twelve rounds and did not reach convergence. This note explains, plainly, why convergence has become hard since Experiment 40, what the "hardened" gate is, when it arrived, whether it was authorised, and how to restore honest convergence without lowering the standard.

## The short answer

Convergence used to be routine and is now elusive for three reasons. The test for "finished" was changed from a **state-based** test to a **rate-based** one. The rate-based test only passes when the panel's discovery of new problems visibly **slows down**. And the panel doesn't slow down, because it **over-produces** findings, most of which aren't real. So convergence is blocked by noise feeding a test whose pass-mark was never validated. It is **not** mathematically impossible.

## Two kinds of "finished" test

**State-based:** declares done when the set of open problems stops changing — same findings, nothing new, two passes running. This is how Experiments 36 and 37 (early April 2026) converged naturally, and it matches the convergence module's own design, where a stability measure decides and the rate measure (gamma) is only a thermometer.

**Rate-based (gamma):** measures whether the *rate* of new critical findings is decaying — like a Geiger counter clicking less as a source decays. Near 1.0 means discovery has stopped; near 0.0 means findings keep coming steadily. The gate demands gamma of at least 0.30 (clearly slowing) before declaring convergence.

## When it changed

The gamma gate entered on **17 April 2026**, in the second-generation runner built for Experiment 40. Experiment 39 and earlier used the older runner with no gamma gate. Searching every record, there is **no convergence on file for Experiment 38 or 39**; the last confirmed natural convergences are **Experiments 36 and 37**, both state-based. So the dividing line is the gamma gate arriving at Experiment 40 — not a failure at 39 specifically.

## What "hardened" means

On **18 May 2026** the gamma gate was made much stricter. The old gate was an **OR** (pass if gamma cleared its mark *or* a few quiet rounds). The hardened gate is an **AND**: gamma (critical findings only, after duplicates removed) must reach 0.30, *and* hold steady and survive dropping any one round, *and* there must be three straight rounds with no new critical findings. A fallback waives the gamma rule only when there are fewer than eight criticals in total. The hardening was deliberate, to stop premature or cooked convergence.

## Why it can't pass for a substantial target

Gamma is "one minus how fast the running total of criticals grows." Steady growth means gamma zero; a flattening total means gamma climbs toward one. In Experiment 41 the panel found about **two new criticals every round, for all twelve rounds** — a near-straight line — so gamma stayed pinned at zero. It briefly touched 0.2488 at round two, just shy of 0.30, then decayed.

Using the runner's own formula: had the panel front-loaded its real findings and gone quiet, gamma would have sailed past 0.30 (front-loaded-then-stopped scores 0.71; graceful decay 0.64; with the same 24 findings, about half found in the first three rounds clears it). **The threshold is reachable. The panel just never slows down.**

## Why the panel never slows: over-production

Of **79 findings, not one produced a fix that passed mechanical verification**, and **27 couldn't even be confirmed to exist in the code**. The internal checker (running silently) kept judging findings uncertain or false — proving numerical claims false, flagging fixes that target code not in the file. A bounded 438-line module has a finite number of real critical bugs; a panel finding real ones would find them early and then go quiet. Instead it manufactured ~2 new "criticals" a round. That steady manufacture of noise is the direct cause of the flat gamma.

## A safeguard was skipped

The five-model conference that recommended the hardening (17 May 2026) set four conditions to keep it honest. One was: **recalibrate the gamma threshold on held-out data, and let it be able to fail.** That recalibration was **never done**. The 0.30 mark was frozen before the run (the honest, anti-cooking part) but never checked for whether a genuinely-finished review could actually reach it. Completing this is **not** lowering the bar — it is finishing a safeguard that was specified and omitted.

## Was it authorised?

The conference said plainly it **required founder approval before implementation**. The next day's commit was labelled **founder-directed**. The founder has since said approval was likely a high-level wave-through, without two consequences being made clear: that gamma stays a strict pass/fail needing discovery to slow, and that the recalibration safeguard would be skipped. Fair record: **recommended and waved through — not slipped in, but not approved with eyes fully open.**

## Two side issues

**Empty responses:** three in the whole run, all from one model (Gemini, via the OpenRouter service), which returned empty bodies after 4–6 minute stalls. The recovery protocol absorbed all three; no model missed a round and the backup route was never needed. Still worth fixing at source rather than leaning on recovery.

**The silent checker:** the internal verifier that checks findings against the code is in observation-only mode. It already spots most findings as weak or false, but its verdicts are ignored. Switching it on to filter findings would cut the over-production directly.

## How to restore honest convergence

- **Finish the skipped recalibration**, so the pass-mark reflects what a real, completed review scores.
- **Switch on the silent checker** to filter unconfirmed and false findings before they count.
- **Capture the panel's own "I'm finished" declarations** — in Experiment 41 one model explicitly declared it was done, and the runner ignored it and kept counting.
- **Reconsider the gate's shape:** combine the resolution discipline of the state test (which worked in 36/37, but could "finish" with bugs left open if their count merely plateaued) with the conservatism the gamma gate was reaching for, keeping gamma as the diagnostic it was meant to be.

## Bottom line

Convergence is not impossible. It is blocked by a panel over-producing noise into a rate-based gate whose pass-mark was never validated. The fix is to make the measurement track reality — filter the noise, validate the threshold — not to lower the standard. A review should end when the genuine defects are exhausted, and read as ended when it is.

Written under CDSFL note standard v1.2 (14 May 2026).
