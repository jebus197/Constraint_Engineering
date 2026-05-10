# Exp 40 Pre-Launch Focused Round 2 Panel Outcome

2026-05-10 19:30 BST

## Summary

The five-model focused confer round dispatched on the afternoon of 10 May 2026 closed cleanly. All five panel members returned within 185 seconds wall-clock under the parallel star-topology dispatch (each model receives the same prompt independently from the central agent and must converge on a single position rather than offer a menu). The round addressed five questions left open by the 22 April 2026 founder oversight Q&A: the G2 code-correctness fix at the K/L/M shadow-audit binding (G2 = the field-rename from `claim_id`/`severity` to `finding_id`/`confidence` so that the dict-comprehension keys map to real `CellVerdict` dataclass fields); the section 2a target-article scope briefs for Experiments 47, 51, 52, 53 (the four synthesised native modules in biology, physics, chemistry, engineering); the section 6b trigger specifications for the three remaining gap items G6 (specialist-to-specialist verdict conflict), G7 (MERGE deadlock auto-arbitration), G8 (burst-mode phase-zero convergence override); the trigger-versus-implement policy on those three; and the closure-now disposition of the four residuals identified in the 22 April debrief.

The four residuals had been closed earlier in the same session under an explicit founder directive that rejected deferral. Round 2's role on Q5 was to ratify or refute the closures on the merits rather than relitigate the close-now-versus-defer question, which had already been adjudicated.

## Panel composition (rotated to current frontier 2026-05-10)

| Slot | Model | Route | Identifier |
|---|---|---|---|
| CC2 | Claude Opus 4.7 | Claude CLI piped mode (Max subscription) | `opus` |
| Codex (cx) | GPT-5.5 | OpenRouter | `openai/gpt-5.5` |
| Gemini (ge) | 3.1 Pro Preview | OpenRouter | `google/gemini-3.1-pro-preview` |
| ChatGPT (cgpt) | GPT-5.5 | OpenRouter | `openai/gpt-5.5` |
| DeepSeek (ds) | V4 Pro | DeepSeek direct API | `deepseek-v4-pro` |

Smoke-tested on the same date against an anchor prompt before dispatch: 4/4 upgraded routes returned `verdict=CONFIRMED` on a known-true claim ("17 is prime"), JSON-conforming, with the falsification field populated. The Gemini, GPT, and DeepSeek slots all rotated to current frontier; the Opus slot is what the Max subscription serves. The DeepSeek upgrade was mandatory rather than optional — the older Reasoner R1-0528 endpoint is no longer listed by DeepSeek's catalogue API.

## Round-2 wall-clock and yield

| Model | Response chars | Wall-clock |
|---|---|---|
| Gemini 3.1 Pro | 7587 | 44.9 s |
| Codex GPT-5.5 | 10068 | 63.5 s |
| ChatGPT GPT-5.5 | 11919 | 79.2 s |
| CC2 Opus 4.7 | 12113 | 116.9 s |
| DeepSeek V4 Pro | 6433 (+17473 reasoning) | 185.4 s |

Total prompt size dispatched per model: 78947 characters (system 11821 + user 67126; the user prompt embedded the full Exp 40-54 consolidated plan as background plus the focused-round framing, the G2 code excerpt, the residuals-context block, and the five questions). Prompt size was within all five models' context windows.

## Per-question convergence

### Q1 — G2 code-correctness fix

All five models converged: the fix is correct on the merits, and the regression pins (AST schema check, dataclass field-binding test, behavioural replica, log-format pin, plus negative-regression pins explicitly banning the stale `claim_id` / `severity` keys) are sufficient to prevent recurrence. No latent issue at the fix site requires action.

Two models (Codex, ChatGPT) flagged a forward-going consideration that is not a fix to the G2 site itself but matters for downstream non-distortion calculation: severity is carried on the `Finding` dataclass, not on `CellVerdict`. Any audit calculation that needs severity to evaluate the `40_gate.json` `pass_condition` must explicitly join `CellVerdict` records back to their source `Finding` via `finding_id` rather than expecting severity to appear on the verdict record itself. This is captured here for the design of the K/L/M non-distortion measurement that runs across Experiments 40 to 50; it does not block Experiment 40 launch.

### Q2 — Section 2a target-article scope briefs

Convergence is partial, with one clear fold-in plus several panel-suggested refinements that vary in support level.

Four of five models (Codex, ChatGPT, CC2, DeepSeek) flagged that the original Experiment 47 biology brief did not exercise the biology specialist's `z3` logical-claim routing path declared in `domains/immune/biology.toml`. Adding a logical-claim cluster is the consensus fix. Three of five (Codex, ChatGPT, plus both DeepSeek and CC2 implicitly) also flagged that the original false-claim example — a "protein sequence with invalid codons" — was a category error: protein sequences are amino-acid strings and do not contain codons; codon-error claims attach to nucleotide-level (DNA / RNA) claims.

Both of those have been folded into the consolidated plan and its Desktop mirror in this session (see "High-confidence fold-ins applied" below).

The remaining Q2 suggestions had less convergence and are flagged for founder review:

- **CC2 / ChatGPT**: Add a `z3`-routable conservation-violation cluster to the Exp 51 physics brief (alongside the existing kinematics, conservation, dimensional, and special-function clusters).
- **CC2**: Correct the Exp 52 chemistry brief to name the routed tool as `stoichiometric_balance` (the actual `tool_manifest.toml` entry) rather than `collections.Counter` (which is the underlying stdlib used inside the routed tool).
- **CC2**: Drop `astropy.units` from the Exp 53 engineering brief (it is not in the engineering domain config) and add a `linear_programming`-routable optimisation claim (for example, a load-distribution problem with explicit constraints).

The 15-25K character budget per module was reaffirmed by all five.

### Q3 — Section 6b trigger specifications for G6, G7, G8

Four of five converged that the trigger structure is correct: G6 and G7 trigger from Exp 44 post-mortem with automatic migration to Exp 49 if Exp 44 produces no qualifying evidence; G8 remains out-of-arc pending external authorisation of a future burst-mode experiment. The multi-tool pairings for activation (pytest + AST inspection + `inspect` for callable signatures + trace-log parsing) and the minimum evidence thresholds were endorsed.

DeepSeek dissented substantively, with reasoning corroborated by inspection of the per-experiment matrix: Experiment 44 is a synthetic composition test that combines outputs from the mathematics specialist (Exp 41), the encodings composer (Exp 42), and the macrophage admissibility cell (Exp 43). It does not exercise multiple B-Cell specialists co-ruling on the same `Finding`, and is therefore structurally unlikely to produce specialist-to-specialist verdict conflicts (G6) or MERGE deadlocks between specialists (G7). The first experiment in the arc that forces multi-specialist co-rule by design is Exp 49 (cross-domain synthesis: math + stats + CS specialists on shared claims).

DeepSeek noted that the migration clause in the existing G6 and G7 entries already catches this — the trigger migrates to Exp 49 if Exp 44 produces no qualifying evidence — but argued that the wording cleanly scoped to Exp 49 directly would be tidier. A clarifying note has been folded into section 6b in this session: read the Exp 44 entries as early-observation checkpoints rather than as the realistic primary trigger; Exp 49 is the realistic primary. No code change is required because the trigger logic, evidence threshold, and migration are already correct.

Two models (Codex, CC2) suggested minor strengthenings: "first material observed conflict" wording on activation, and adoption of G7's "minimum three observed patterns" clause for G6 (to avoid arbitration-rule overfitting to a single conflict case). These are flagged for founder review.

### Q4 — Trigger-versus-implement policy

All five models converged: trigger-and-wait is the correct policy for all three gaps. G6 and G7 should not receive arbitration algorithms until post-mortem evidence shows the actual conflict and deadlock patterns; pre-registering a rule before the data exists violates the Popperian discipline the project runs under. G8 is correctly external-authorisation-only because burst mode is deliberately out-of-arc for Experiments 40 to 54.

ChatGPT added a useful refinement: implement instrumentation now (the trace-log fields and replay scaffolding that will be needed when the trigger fires), but not the arbitration rule itself. This is captured here as a panel suggestion for founder consideration during the Exp 44 pre-launch checkpoint.

### Q5 — Closure-now disposition of the four residuals

All five models converged that the four residuals as closed are correct on the merits. The panel was specifically asked not to recommend deferral on the basis that the residuals "could have waited" — the founder had adjudicated that question — and the panel respected the constraint. Comments on the closures are summarised below.

- **(a) Exp 39-0 gate state cross-check.** Five of five endorse: the original `max_open_crit_high=0` threshold was the **subject** of the Exp 39-0 calibration experiment, not its prerequisite; raising the default to 5 was the correct corrective action; the work-stream is complete even though the experiment's own `completion_signal.json` records `status: INCOMPLETE` because it never converged (it could not, by design — the threshold was unreachable). ChatGPT and Codex suggested the `ce_state.md` wording could distinguish more sharply between "experiment incomplete under old gate" and "calibration finding closed". The current ce_state.md update already makes this distinction; the suggestion is a wording-polish candidate rather than a substantive correction.

- **(b) Per-finding R_k time-series tracking.** Five of five endorse: not a blocker for any experiment in the Exp 40 to Exp 54 arc as currently planned. The runner's per-finding latest-R_k logging is sufficient; the gamma gate uses aggregated counts, the Stage 6 calibrator (Exp 50) uses whole-round triples, and the consolidated plan and `MATHEMATICAL_APPENDIX.md` carry no time-series-R_k requirement. Forward-going enhancement candidate; no current dependency.

- **(c) Scientific-notation amendment to the locked note standard.** Five of five endorse the v1.1 amendment as additive. Rule 11a (the `1×10^N (number-words)` format with verified exponent-to-word correspondence) and Rule 11b (the `<digit>E.<digit>` item-reference recognition rule, which prevents the "1E.10 → ten billion" misreading) close the scientific-notation gap without introducing new ambiguity. Codex suggested a wording polish to clarify behaviour for signed exponents (negative powers of ten) and `E.` item references with multi-digit indices (for example, `1E.10` versus `1.E.10`). This is a v1.2 candidate — not a v1.1 correction — for the next note-standard revision.

- **(d) Component closure-state index.** The panel split on the F3 `DEBUG_CHANNEL_CHECK` label. Three models (Gemini, ChatGPT-conditional, CC2) argued for `shadow_integrated`: F3 runs in the dev/CI path, executes on real inputs, and emits assertion side-effects. Two models (Codex weakly, DeepSeek explicitly) argued for `library_complete`: F3's production default is no-op (gated by environment variable); when active, it can abort the run on assertion failure, which is a behavioural side-effect that does not fit the observation-only definition of `shadow_integrated`. The labelling edge case is real — F3 does not fit any of the three lexicon labels cleanly, because the lexicon was designed for components that are either off, observing, or driving live decisions, not for components that are off-by-default but become assertive when toggled.

  Pending founder adjudication, the F3 label remains `library_complete` in the index. The Component Closure-State Index is otherwise endorsed as a sufficient closure of the retroactive labelling sweep. Stage 6 calibrator and K/L/M shadow-audit labels (`shadow_integrated`) are correct per all five models.

## High-confidence fold-ins applied in this session

The following changes were folded into the consolidated plan (`experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md`) and mirrored byte-identical to the Desktop canonical (`~/Desktop/CDSFL_Consolidated_Plan_2026-04-21.md`), per the four-of-five-or-better convergence threshold:

1. **Exp 47 biology brief.** New cluster 5: logical claims for `z3` routing (boolean relationships among gene-expression, regulatory, or pathway states). Origin: 4/5 models flagged that the original 4-cluster brief did not exercise the biology specialist's `z3` path. Cluster moved from 5 to 6: corrected false-claim example. The original "protein sequence with invalid codons" was a category error (protein sequences are amino-acid strings and do not contain codons). Replaced with a nucleotide-level construct: a DNA sequence labelled as a complete open reading frame for a named protein, where translation reveals a premature stop codon contradicting the labelled protein length.

2. **Section 6b clarifying note.** A new paragraph appended to section 6b records the Round 2 observation that Experiment 44 is structurally unlikely to surface multi-specialist conflicts (it composes outputs from one specialist plus the composer plus the macrophage), and that Experiment 49 is the realistic primary trigger for G6 and G7. The migration clauses in the existing G6 and G7 entries already handle this case correctly; the note exists to align reader expectations with the experiment design rather than to change trigger logic.

## Items flagged for founder review (medium convergence)

These panel suggestions had less than 4/5 support but are surfaced rather than silently discarded so the founder can decide whether to fold them in before Exp 51, 52, 53, or 49 enter their respective drafting windows:

- Add a `z3`-routable conservation-violation cluster to the Exp 51 physics brief.
- Correct the Exp 52 chemistry brief tool name from `collections.Counter` to `stoichiometric_balance`.
- Drop `astropy.units` from the Exp 53 engineering brief; add a `linear_programming`-routable optimisation claim.
- Adopt "first material observed conflict" and "minimum three observed patterns" wording in section 6b's G6 entry.
- Implement G6 / G7 instrumentation now (trace-log fields, replay scaffolding) without the arbitration rule itself, in advance of the Exp 44 / Exp 49 trigger firing.
- Polish ce_state.md wording to distinguish "Exp 39-0 incomplete under old gate" from "Exp 39-0 calibration finding closed".
- Clarify Rule 11 in a future v1.2 note-standard revision for signed exponents and multi-digit item-reference indices.
- F3 `DEBUG_CHANNEL_CHECK` label: 3/5 panel split favours `shadow_integrated`; 2/5 endorse the current `library_complete`. Awaiting founder adjudication.

## Path forward

The Round 2 outcome does not surface any pre-launch blocker for Experiment 40. The runtime code is closed (F1, F2, F3 from 21 April; G1 through G5 closed overnight on 22 April; G6, G7, G8 specification-only by Popperian design; G9 lexicon plus Component Closure-State Index closed in this session). The four residuals are closed. Panel review of the items not previously panel-reviewed is now complete with 4/5 or better convergence on every load-bearing question.

The next operational steps, as agreed before the round dispatched, are: a comprehensive documentation sweep across `README.md`, `resources/ONBOARDING.md`, `resources/RECOVERY.md`, `docs/MATHEMATICAL_APPENDIX.md`, `PAPER.md`, `docs/GLOSSARY.md`, `docs/ARCHITECTURE.md`, `docs/REPRODUCING.md`, and `docs/CURRENT_STATE.md`, sequential per file, README first; then Experiment 40 dispatch and post-mortem; then the rest of the Exp 40 to 54 arc within the seven-day funding-and-outreach window the founder named for this session.

## Next review trigger

The next decision point for the founder is the disposition of the items flagged in the medium-convergence list above, particularly the F3 label adjudication and the medium-priority Exp 51 / 52 / 53 brief refinements (these are not on the immediate critical path because Exp 51 / 52 / 53 are later in the arc, but folding them in early avoids a re-edit at module-drafting time). After founder disposition, the autonomous queue continues into the documentation sweep and Experiment 40 dispatch.

Written under CDSFL note standard v1.1 (10 May 2026).
