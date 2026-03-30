# CDSFL Role-Based Model Architecture

**27 March 2026**

---

## The Football Team Analogy

In a real football team, players are assigned positions based on their demonstrated abilities. A striker plays forward. A defender defends. The goalkeeper stays in goal. The team manager decides strategy. The team captain executes tactics on the field. No player does everything. Every player contributes according to their strengths. The team wins or loses as a collective, not as individuals.

The same principle applies to distributed AI compute under CDSFL. Instead of giving all five models the same task with the same prompt — which is what we have been doing — each model should be assigned a role-specific position based on what the bench data shows they are actually good at.

---

## The Role Map

Based on the bench test data and observed performance across smoke tests and the current full bench run, the five models show distinct capability profiles.

**Claude Opus 4.6 — Team Manager:** Orchestrates the overall process, assigns roles, monitors performance via the decay curve diagnostic, makes strategic decisions about when to continue or stop, generates solutions, and provides expert guidance. Strength: sustained multi-step reasoning across complex problems. Also participates as a strategic reviewer, contributing findings alongside managing the team.

**Codex 5.3 — Team Captain:** The on-field leader who executes the manager's strategy, runs P-passes with line-level precision, performs code analysis, verifies findings, and makes tactical decisions in real time. Strength: precise analytical work, especially on code and structured problems. In the extended P-pass protocol, Codex is the primary adversarial partner who tests the manager's work.

**Gemini 3.1 Pro — Mathematical Specialist:** Despite being a generalist chatbot that performed poorly on most review tasks, Gemini produced the core mathematical framework for the Popper formalisation, including the Duane NHPP model, Mayo's severity function, and KL divergence for HIL analysis. Strength: theoretical and mathematical work rather than practical code review.

**ChatGPT 5.4 — Generalist Forward:** In the single-round smoke test under CDSFL + HIL, it produced 11 findings, more than any other model. Under Control it produced almost nothing. The methodology activates its capability dramatically. Strength: broad structured output when given clear direction.

**DeepSeek V3.2 — Budget Workhorse:** API costs are fractions of a penny per call. It produces adequate baseline analysis and sometimes generates genuine findings under CDSFL, but its decay curves tend toward flat, indicating limited analytical depth. Strength: volume screening at very low cost.

---

## How Role Assignment Works

**The first bench run is the tryout.** All models play all positions on all tasks. The Duane analysis tool measures each model's gamma (convergence parameter), D score (inverse half-life), and verification rate per domain. This data becomes the basis for role assignment.

**Subsequent runs use the Registry's model-level configuration (Layer 4)** to encode role assignments. For example:
- A mathematics task might assign Gemini as primary mathematical reviewer, Codex as verification lead, and DeepSeek as initial screening.
- A code task might assign Codex as primary reviewer, Claude as architectural analyst, and ChatGPT as structured output generator.

The manager (Claude) reads each model's performance profile from the Registry, considers the current task's domain and difficulty, and assigns positions. The captain (Codex) executes the assignments and makes tactical adjustments based on what emerges during the review rounds.

**Role assignment is not permanent.** The Registry continuously updates model profiles based on new performance data. A model that improves on code tasks gets promoted to code reviewer. A model that degrades on mathematical tasks gets reassigned.

A small percentage of assignments (10–20%) are deliberately out-of-position to test for emergent capability that the current data might miss.

---

## The Efficiency Argument

Currently, all five models review every task identically. This means every model spends tokens on tasks it may not be equipped to handle. DeepSeek reviewing a complex mathematical proof produces flat-curve output that adds noise without signal. Those API calls are wasted.

Assigning DeepSeek to volume screening (quick first-pass identification of obvious issues) and Gemini to mathematical verification (deep analysis of specific claims) uses each model's tokens where they produce the most value.

**Cost savings are potentially significant.** If DeepSeek handles 50% of the initial screening at one tenth the cost per token of Claude, and Claude only engages on tasks that survive the initial screen, the total API cost drops while analytical quality improves. The team manager optimises for total team output, not individual model utilisation.

---

## Why This Is More Than an Analogy

The decay curve provides the **objective performance measurement** that real human organisations lack. In a human organisation, role assignment is based on reputation, seniority, and subjective assessment — all of which can be gamed. In this system, role assignment is based on gamma, D, and the verification score — all empirically measured, computationally verified, and continuously updated. The model cannot fake its decay curve.

This makes the role-based architecture **self-correcting**:
- Poor performers are detected automatically
- Strong performers are promoted automatically
- The system learns which models are trustworthy for which tasks and adjusts accordingly

This is the same principle as Genesis trust scores applied to AI model management.

---

## What Remains

The role-based architecture requires the bench data to implement. The current run produces that data. Once it completes, the Duane analysis tool characterises each model's capability profile per domain. The Registry's model-level configs encode the resulting role assignments. The next run tests whether role-based assignment produces better results than uniform assignment.

**The prediction:** a well-managed team outperforms a group of individuals doing the same thing. The measurement framework exists to prove or disprove this prediction empirically.
