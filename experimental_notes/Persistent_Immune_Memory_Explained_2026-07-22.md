# The Persistent Immune Memory Module — What It Is Intended To Do

**2026-07-22, 00:22 BST.**

## Summary

The persistent immune memory (`bench/dm/_memory.py`, class `ImmuneMemory`) is a component of the CDSFL system intended to let the review pipeline **learn, across many experiments, how often each class of flaw turns out to be a genuine defect**, and to use that accumulated history to set better *starting expectations* for future reviews. It is a documented part of the mathematical model — it feeds the starting prior of the recursive self-assessment equation R_k(0). It is currently **wired into no live code** (grep confirms zero live importers; only its own test file exercises it), so at present it does nothing. Its potential benefits are real but **scale-dependent**: over the remaining eight-experiment arc it would have almost nothing to learn from and would change little. It is a feature for a mature, high-volume system, not a short arc.

## Where it sits in the mathematical model

The recollection that this component has meaningful bearing, and was derived from the maths model, is **accurate**. The core idea — a *memory-blended prior* — is a documented section of the mathematical appendix (**§1.5, "Persistent Memory and Blended Prior"**). It is the software implementation of a formal piece of the model, not a stray bolt-on.

Two things are true at once, and the boundary matters:
1. The concept genuinely belongs to the maths model and touches the starting value of the self-assessment equation R_k.
2. Being *documented in the model* is not the same as being *active in the live convergence gate*. The gate that decides convergence today runs on the decay-curve measure (γ_critical), the count of consecutive zero-new-critical rounds, and the falsifier test. The blended prior is **not connected to that live machinery**.

Honest position: **real lineage in the model, currently inert in practice.**

## What it is intended to do

Every review begins with a **prior** — an initial estimate, made before looking at the specific code, of how likely a kind of flaw is to be a real defect rather than a false alarm. Without memory, that prior is a fixed default (e.g. an even chance).

The memory replaces that blind default with an **experience-informed** estimate: *"across the experiments run so far, this class of flaw turned out real roughly this often, so start from there."* Concretely, per flaw class it keeps a running tally of confirmed-vs-rejected counts across all past experiments:
- **Exponential decay** — recent experiments weigh more (`exp(-0.1)` per experiment), so it tracks the present, not the distant past.
- **Beta-Binomial smoothing** (Jeffreys 0.5/0.5) — the estimate is never exactly 0% or 100%, keeping it honest at small sample size.
- **Blended prior** — `π = (1 − ρ)·π_base + ρ·π_mem`, default `ρ = 0.2`. Most of the starting value is still the base default; only a fifth comes from memory.

Over many experiments the system's starting expectations become better calibrated — in adaptive-systems language, it develops a stronger internal sense of *what it tends to be looking for* (Holland's CAS principle).

**Essential protective property: advisory-only.** It adjusts *starting expectations*; it can **never change a final verdict**. In CDSFL, whether a flaw is real is decided by *running a test that tries to prove the flaw*, not by a prior. So it can influence where reviewers look first and the initial weight of a concern, but it can never confirm or dismiss a defect. Fail-safe by design: the worst it can do is a slightly wrong starting estimate, which the tool-decided verdict then corrects.

## The drift alarm

It also carries a **CUSUM staleness alarm**: if incoming flaw rates diverge from memory's predictions and the divergence accumulates past a threshold (default 2.0), it raises a caution that the remembered rates may be stale. It also stores a SHA-256 fingerprint of the source it learned from, so it self-invalidates if that source changes substantially.

## The advantages, if any

1. **Better-calibrated starting expectations over time** — less effort re-learning each experiment that a class of concern is usually real, or usually noise.
2. **Potentially faster convergence at scale** — fewer rounds spent on flaw classes history already shows are near-certain or near-noise.
3. **Early warning of drift** — flags when memory's guidance should be trusted less.
4. **Expresses a real adaptive-systems principle** — a legitimate design idea, not an invention.

Counterweight: every advantage is **advisory, bounded, and scale-dependent**. None can override a tool-decided verdict; all require a substantial history to be worth anything.

## What it would do if it ran live over the remaining arc

Over the remaining arc *specifically*, it would do **very little**, for four reasons:
1. **It starts empty.** On experiment one it has no history, falls back to the neutral default, leaves the prior unchanged — it does nothing.
2. **Its history would stay thin.** Even if wired to record each run (it is not), by experiments two–four it would hold only a handful of points, each from a *different* target file. A one-fifth nudge toward a 2–3-observation estimate is weak, possibly noisy.
3. **The drift alarm would have little to track.** CUSUM wants a repeated stream of similar material; each arc experiment is a different file reviewed once.
4. **It is orthogonal to convergence.** It only shifts starting expectations — it never decides whether an experiment converges. It could not have fixed Exp 43, and it will not decide any future convergence. That belongs to the γ gate, the zero-new-critical count, the falsifier, and the five mechanical fixes now designed.

**Net effect over the remaining eight experiments: close to nothing.** The component earns value only after dozens of experiments accumulate over a comparable flaw taxonomy — the scale of a full bench run or a production deployment.

## Bottom line for the decision

Sound, standard, low-risk, correctly built code implementing a real and documented piece of the maths model (the memory-blended prior for R_k) — so the sense that it has meaningful bearing is well founded. Its usefulness is **deferred and scale-dependent**; in the current arc it would be near-silent; its natural home is a mature, high-volume setting.

Two facts keep the decision clean:
- **Reviewing it as an Exp-44 target ≠ using it.** A review subjects its code to falsification like any other target; it commits to nothing.
- **Whether to ever wire it into the live pipeline is a separate, later, low-priority choice**, best revisited at bench-run scale.

---

*Written under CDSFL note standard v1.2 (14 May 2026).*
