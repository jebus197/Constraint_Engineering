# Experiment 40 Post-Continuation Fix Tranche — Post-Mortem

2026-05-15 22:30 BST

## Summary

Following the Experiment 40 continuation run (post-mortem
`experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md`) and the
founder's review plus an unconstrained-Gemini second opinion, a twelve-item
work block was executed under the full metacognitive discipline (panel
confer intent, strictly sequential tool use, Find-Follow-Analyse-Fix-P-pass,
multi-tool cross-verification, P-pass falsification, TTS output). Nine
substantive engineering items completed; one item (architectural confer)
completed via the mandated local-P-pass fallback because the Codex CLI was
unstable in the execution environment; one item (Experiment 40 R17–R21
resume) is surfaced as a founder decision rather than executed
autonomously, for the reasons in §"Deferred to founder decision"; this
note is the twelfth item.

229 regression tests pass across the full tranche plus the eight
pre-continuation fixes plus adjacent suites. Every behavioural change is
either backward-compatible by construction (opt-in state, default-off
config) or covered by a new dedicated regression file. Two issues the
local architectural P-pass surfaced were fixed in-line (a parser
length bound, a cross-surface ID-grammar inconsistency).

## Work Items and Outcomes

### Plain-English continuation post-mortem — ITC naming correction

The founder corrected a conflation: ITC is the project's "IT Crowd fix"
discipline (on degradation, restart the model fresh with
fingerprint-informed scope; never bench or skip), and the deeper
rationale is burst reasoning — a fresh instance surfaces what a
long-running instance has stopped seeing. The continuation post-mortem's
plain-English and TTS companions, and the technical post-mortem's
Anomaly 5, were rewritten to name ITC correctly rather than inventing an
"Intelligent Task Controller" expansion from context.

### Fix 1a — finding-ID parser hardening

`bench/runner_core.py`. The Exp 39 leakage guards caught Python
variable-name leaks but not the continuation's class: arbitrary code
fragments written into the FINDING_ID field (`f for f in findings}`,
single backticks, multi-token text). Added `_structurally_valid_fid`
(module-level helper + `_VALID_FID_STRUCTURE` regex) enforcing
`^[A-Za-z0-9_]{1,128}$`, called at all four parser paths (JSON-array,
JSON-object, marker; the tuple path is pre-validated by its own regex).
Whitespace normalised before validation for parity across paths. The
128-char length bound was added under P-pass after adversarial fuzzing
showed a pathological all-alphanumeric id (5000 chars) would otherwise
pass. 20 dedicated regression tests
(`bench/tests/test_finding_id_structural_validation.py`).

### Fix 1b — LLM classifier log-message honesty

`bench/immune_agents.py`. Root cause established: NOT a fence-post or
rounding error. In software-domain runs `llm_primary` is True and the
override fires for any valid disagreeing classification regardless of
confidence (regex agreement is ~15% in software — intentional). The
OVERRIDE log unconditionally printed `threshold=%.2f`, making a correct
llm-primary override at conf=0.68 read as a sub-threshold bug; the skip
log printed "below threshold" for the UNCATEGORISED-skip case
(conf=0.88, above threshold — self-contradictory). This is a
logging-honesty defect, not a logic defect. Each of the four decision
branches now states its actual gating reason. A `TestLogicUnchanged`
class proves the override decision is byte-identical. 6 regression tests
(`bench/tests/test_llm_classifier_log_honesty.py`).

### Fix 1c — Regulatory-T v2 per-model-bias windowing

`bench/immune_agents.py`, `bench/insect_brain.py`. The per-model-bias
AUTOIMMUNE check fired every round a model hit ≥85% removal; in a
converged run one model reasonably produces mostly already-canonicalised
findings and trips it every round, generating recurring HIL noise and
resurrection churn. Added an optional `bias_window_state` dict
(caller-owned, persists across rounds) threaded through
`run_immune_pipeline`; only the per-model-bias check is windowed
(combined-removal-rate and uncertain-rate stay immediate — they are
round-level health signals). Default `None` ⇒ byte-identical legacy
behaviour, so every pre-existing caller and test is unaffected. The
brain owns the persistent state across rounds. 4 regression tests
(`bench/tests/test_rt_v2_bias_windowing.py`).

### Fix 1d — ITC γ-regime gate

`bench/reference_runner_v2.py`. The pre-existing A4 rho-gate already
suppressed the DEGRADATION *restart* when rho was healthy, but the
DEGRADATION was still recorded as a classification before the
suppression check, so it still fed `_itc_consecutive_failures` and
still fired the per-round HIL underperformer flag — the precise
continuation bug (all five models HIL-flagged every round despite no
restart). Two corrections: (i) a γ-regime gate also suppresses
DEGRADATION when γ is in the converged regime (γ < 0.10), independent
of rho — low yield there is convergence, not collapse, and an ITC
restart would defeat the burst-reasoning rationale; (ii) a suppressed
DEGRADATION is recorded with `classification=None` plus a `suppressed`
marker, so it feeds neither the consecutive-failure streak nor the HIL
flag. Backward-compatible (default `gamma_current=1.0`); the existing
A4 test passes unchanged. 6 regression tests
(`bench/tests/test_itc_gamma_gate.py`).

### Fix 1e — strengthened reformat request; in-round dispatch deferred

`bench/dm/_sk_format.py`. The existing 1D.5 mechanism already does
reject-and-reformat (next-round). The high-value, low-risk improvement
is the STRUCTURE_VIOLATION header plus a strict mandatory template
stating that an unparseable fix is treated as no fix at all. The full
in-round re-dispatch loop was deliberately deferred: it is the
highest-risk item (new dispatch path, per-round cost, loop risk) for a
one-round timing gain, and the continuation's persistent extract
failures were mostly stale findings (proposed_fix targeting
already-modified source) that an in-round retry cannot fix anyway.
Documented escalation trigger: implement the in-round variant if
R17–R21 still shows a material rate of *non-stale* extract failures
after the strengthened request. 18 tests
(`bench/tests/test_sk_format_precheck.py`, two updated for the
strengthened contract).

### G7 — merge-deadlock arbitration

New module `bench/merge_arbitration.py` implementing the
compelled-convergence rule from
`experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md`:
`build_arbitration_query`, `parse_arbitration_vote`, `aggregate_votes`,
`dispatch_merge_arbitration`, with `MergeArbitrationVote` /
`MergeArbitrationResult` dataclasses. Aggregation: ≥3 of 5 same target
→ merge; ≥3 KEEP_DISTINCT → register distinct; otherwise stay deferred.
Dispatch is injectable (runner passes the real model dispatch; tests
pass a stub — no network in the module). Runner integration in
`bench/reference_runner_v2.py`: four config fields (default disabled),
a module-level `_merge_arb_ctx` following the established `_itc_*`
pattern so `_update_finding_statuses` keeps a stable signature, a
`_try_merge_arbitration` seam in the MERGE-deferred branch, per-round
budget reset, and the Gemini-suggested round-level tie-breaker (when
γ < tiebreaker_gamma AND γ-alt unmet, sweep unresolved deadlocks).
Config keys added to `40_gate.json` (disabled) and threaded through
both launchers. **Default `merge_arbitration_enabled=False`** — the
design stages enablement for Experiment 41 (single specialist, low
MERGE, low blast radius) after review. All G7 paths inert by default
⇒ zero regression. 18 module tests
(`bench/tests/test_merge_arbitration.py`).

### DeepSeek V4 Pro investigation

`bench/decomposed_dispatch.py`. Root cause established from the
deterministic code path plus the in-code comment already acknowledging
4096-token truncation: Phase-1 per-chunk calls capped `max_tokens` at
4096; DeepSeek V4 Pro and Gemini 3.1 Pro are reasoning models that emit
a `reasoning_content` trace before final `content`. A large chunk plus
the full 4-Layer protocol prompt exhausts 4096 on the trace, so
`content` is empty and the actual review — in `reasoning_content` —
was silently discarded (the dispatchers only read `.content`). Fix:
raise the Phase-1 cap to 8192 and add `_extract_message_text`, which
falls back to `reasoning_content` then `reasoning` when `content` is
empty. Applied symmetrically to the DeepSeek and OpenRouter Phase-1
paths. This subsumes Gemini's "recursive synthesis" suggestion more
directly — the analysis already exists in the trace; recovering it
beats a costly re-dispatch. 10 regression tests
(`bench/tests/test_decomposed_reasoning_fallback.py`).

### Multi-tool cross-verification of the eight pre-continuation fixes

Structural verification confirmed all eight intact (one false-alarm
needle corrected under P-pass — the runner uses `attempt_close`, not
`verify_and_close_fixes`; the latter is the standalone-CLI entry). 102
prior-fix regression tests pass. The one genuine computational claim —
the gamma-input fix (commit 26b28f8) — was cross-verified with three
tools: z3 proved the set-cardinality invariant (post-reconciliation
novelty ≤ raw opened: negation unsatisfiable); SymPy proved the Duane
γ closed-form slope is symbolically identical to the textbook OLS
slope, with NumPy agreeing to 1.11×10^-16 (about one part in ten
thousand million million); 2000 randomised trials confirmed γ ∈ [0,1]
universally and the targeted convergence scenario confirmed the fix's
rationale (pre-reconciliation input masked depletion the
post-reconciliation input correctly surfaces).

### Architectural P-pass (confer fallback)

The Codex CLI was unstable in the execution environment (`which`
resolved it; direct invocation reported "no such file" — inconsistent
between calls) and the OpenRouter/DeepSeek keys were not loaded in the
shell, so a live five-model confer could not be assembled reliably. Per
the standing fallback rule, a rigorous local P-pass was run on the
three architectural questions. G7 aggregation survived adversarial
testing across eight pathological vote distributions with no
falsification. Parser robustness fuzzing rejected every unsafe input
(injection, homoglyphs, path traversal, zero-width characters) and
surfaced the pathological-length gap, fixed in-line. The
common-language-schema design-fitness review surfaced a cross-surface
grammar inconsistency (G7 used `C\d{3,}`, the runner uses `C\d{4,}`),
aligned in-line. The fallback delivered the confer's substantive value:
two real issues found and fixed.

## Deferred to founder decision

Two items are surfaced rather than executed autonomously, for explicit
reasons (cost-awareness and supervision discipline, not scope-drop):

- **Live five-model architectural confer.** The local P-pass covered
  the substance. A live confer remains valuable as the founder's
  decision gate before G7 *enablement*. Trigger: Codex CLI stability
  restored and the founder available to supervise the API spend. G7 is
  implemented and inert; nothing is blocked by deferring the live
  confer.
- **Experiment 40 R17–R21 resume.** A multi-hour experiment with
  significant OpenRouter spend. The founder's established pattern for
  these runs is close monitoring (the continuation was monitored at
  60-second heartbeats). Launching it autonomously without that
  supervision contradicts that pattern and the project's
  cost-awareness discipline. Trigger: founder go-ahead, with the
  monitoring cadence the founder prefers. The full fix tranche is
  folded in and regression-clean, so the resume is ready whenever the
  founder elects to start it.

## Test Ledger

| Suite | Tests | Status |
|---|---|---|
| Fix 1a structural validation | 20 | pass |
| Fix 1b classifier log honesty | 6 | pass |
| Fix 1c RT v2 windowing | 4 | pass |
| Fix 1d ITC γ-gate | 6 | pass |
| Fix 1e reformat precheck | 18 | pass |
| G7 merge arbitration | 18 | pass |
| DeepSeek reasoning fallback | 10 | pass |
| Pre-continuation fixes + adjacent | 147 | pass |
| **Consolidated sweep** | **229** | **pass** |

## Files Changed

New: `bench/merge_arbitration.py`; six new test files. Modified:
`bench/runner_core.py`, `bench/immune_agents.py`,
`bench/insect_brain.py`, `bench/reference_runner_v2.py`,
`bench/decomposed_dispatch.py`, `bench/dm/_sk_format.py`,
`bench/exp40_configs/40_gate.json`, `bench/launch_exp40.py`,
`bench/launcher_core.py`, `bench/tests/test_sk_format_precheck.py`,
plus the continuation post-mortem companions and the operational
tracker. HEAD at write time: `3bbf2c7` (uncommitted working tree —
sv pending founder direction).

## Path Forward

1. Founder review of this note and the continuation post-mortem.
2. Founder decision on the live confer and the R17–R21 resume (above).
3. On resume, watch the documented escalation triggers: the in-round
   reformat dispatch (1e) and the in-round arbitration dispatch (G7
   enablement) become warranted only if R17–R21 shows the bounded
   fixes are insufficient.
4. sv when the founder directs — the working tree is regression-clean
   and ready to commit as one coherent tranche.

## Cross-references

- `experimental_notes/Exp40_Continuation_Postmortem_2026-05-15.md`
- `experimental_notes/G7_Merge_Deadlock_Resolution_Design_2026-05-15.md`
- Plain-English companion:
  `experimental_notes/Exp40_Fix_Tranche_Postmortem_Plain_English_2026-05-15.md`
- TTS companion:
  `~/Desktop/CDSFL_tts/Exp40_Fix_Tranche_Postmortem_2026-05-15.txt`

Written under CDSFL note standard v1.2 (14 May 2026).
