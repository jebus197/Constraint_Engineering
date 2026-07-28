# Experiment 40 Pre-Launch State at 9 May 2026

2026-05-09 20:55 BST

## Summary

The Constraint Engineering Experiment 40 pre-launch state is unchanged across a sixteen-day hiatus running from 23 April to 9 May 2026. The repository sits on branch `exp39-experimental` at HEAD `7cdf846`, working tree clean, pushed to origin, no new commits during the hiatus. Pre-launch runtime code is closed. Four open items remain. None has moved during the gap, and all four are founder-judgement decisions rather than code work.

## Repository state

| Field | Value |
|---|---|
| Branch | `exp39-experimental` |
| HEAD | `7cdf846` |
| Working tree | clean |
| Origin | up to date |
| Test count | 1311 collected |
| Fast non-network sweep | 907/907 pass in 342.12 s |
| Overnight new tests | 56/56 pass in 2.33 s |

Most recent commit `7cdf846` is an operational-plan date-correction landed during the post-compaction resume on 23 April 2026 at 05:01 BST. The substantive prior commit is `7c9df2b`, the documentary save-state landing the founder oversight question-and-answer debrief from 22 April. Earlier in the same window, `991cde0` closed five of nine residual gap-closure items (G1 through G5) and added trigger specifications for G6, G7, and G8. Earlier still, `2fbedcd` landed the three pre-launch fix items F1, F2, and F3, and enriched the K, L, M shadow-audit logging.

The single test file with a hang is `test_exp29_integration.py::test_three_round_flow`, which sits on the Claude command-line Haiku large-language-model classifier path at roughly 14.4 s per call. The hang is pre-existing and unrelated to the overnight edits, confirmed against the `bench/logs/immune_pipeline.log` entry at 02:05:51 BST on 22 April showing the corrected field set emitting under live load.

## What was settled before the hiatus

Pre-launch runtime code is closed. Three fix items landed on 21 April 2026.

**F1 — SymPy sandbox allow-list correction** at `bench/immune_agents.py:977`. SymPy is the symbolic-mathematics library used by the immune-agent verdict path. The previous configuration left the sandbox so restricted that every SymPy verdict silently returned uncertain. The fix expanded the allow-list to include `Integer`, `Float`, `Rational`, `Symbol`, `Add`, `Mul`, `Pow`, `pi`, `E`, `oo`, `sqrt`, `Eq`, `Gt`, `Lt`, `Ge`, `Le`, `log`, and `exp`, while keeping `__builtins__` empty so the remote-code-execution blocklist still holds. Four regression tests pass in 7.70 s.

**F2 — `compute_rk_with_eta_channel` wrapper activation in identity mode** at `bench/reference_runner_v2.py:3510`. The bare `compute_rk(R_old, q, sk, nu_b, nu_f)` call was swapped for `compute_rk_with_eta_channel(R_old, sk, eta_int=q, m_div=1.0, c_ext=0.0, nu_k=0.0, d=1.0, p=1.0, nu_b, nu_f)`. At those parameters the wrapper reduces mathematically to the bare form within numerical tolerance below 1e-9. A 1620-case pre-verification and a 567-case grid sweep confirm the identity numerically. Config flag `eta_int_modulator_wired_into_compute_rk` in `bench/exp40_configs/40_gate.json` is `true`.

**F3 — `DEBUG_CHANNEL_CHECK` assertion** at the same code site. Gated by an environment variable, it compares the wrapped output against an independently computed bare output to within 1e-9. Production default is no-op. Purpose is to catch any future refactor that shifts identity-mode parameters.

**K, L, M shadow-audit logging enriched** at `bench/immune_agents.py:5400-5428`. K, L, M are the physics, chemistry, engineering shadow specialists, where shadow specialist means a verdict-emitting cell whose output is logged but not used for live promotion until non-distortion evidence accumulates. The log records per-verdict structured detail of `finding_id`, `verdict`, `confidence`, `tool_used`, and a 256-character `evidence` excerpt.

**Round 2 plan review closed** via five-model compelled-convergence star topology, where compelled-convergence star topology means each of the five models receives the same prompt independently in a hub-and-spoke arrangement and must converge on a single position rather than offering a menu of options.

**Overnight gap-closure shift on 22 April** closed five of nine items in the Experiment 39 to Experiment 40 gap-closure list. Each G-item is a residual code or documentation gap carried forward from earlier work.

| # | Gap | Status | Pre-launch blocker? |
|---|---|---|---|
| G1 | Gate C admissibility-parser preflight wired into launcher | CLOSED with 6 tests | yes (resolved) |
| G2 | K/L/M shadow-audit regression test plus bug fix at `bench/immune_agents.py:5411-5421` (renamed `claim_id`/`severity` → `finding_id`/`confidence`, the real `CellVerdict` dataclass fields) | CLOSED with 11 tests | no |
| G3 | Stage 6 calibrator test harness, SymPy-verified delta and noisy-OR identities | CLOSED with 18 tests | no (Exp 50 unblock) |
| G4 | `open_crit_high_count()` REOPENED regression | CLOSED with 11 tests, no fix needed | no |
| G5 | `contested_count()` grace-period regression | CLOSED with 10 tests, no fix needed | no |
| G6 | Specialist-to-specialist verdict-conflict resolution | SPEC ONLY (§6b trigger) | no (Exp 49) |
| G7 | MERGE deadlock auto-arbitration | SPEC ONLY (§6b trigger) | no (Exp 44) |
| G8 | Burst-mode phase-zero convergence override | SPEC ONLY (§6b trigger) | no |
| G9 | F4 closure-state lexicon applied | PARTIAL (lexicon added, ~40 retroactive labels not swept) | no |

F4 is the documentation rule for tagging schema elements as `library_complete`, `shadow_integrated`, or `live_operational`. The lexicon section was added to `resources/ONBOARDING.md` and the most stale description was corrected, but a full retroactive sweep of the remaining mentions was deliberately not performed.

**Founder oversight question-and-answer on 22 April between 02:15 and 02:30 BST** surfaced four residuals beyond the G-list:

1. The Experiment 39 phase-zero gate contradiction. Project memory documents the gate as complete, while the recovery criterion of zero open critical-high findings was not personally cross-checked against live runner state.
2. Per-finding R_k time-series tracking, which has not been assessed for blocking impact on any specific experiment in the Experiment 40 to Experiment 54 arc.
3. The scientific-notation sub-rule. The convention requires large numbers to be written as `1×10^N (number-words)` with verified exponent-to-word correspondence. The rule lives in the operational tracker and the relevant feedback memory file but has not been amended into the locked `cdsfl_note_standard_v1.md`. Amendment requires v1.1 or v2 with a dated lock line per the standard's own amendment clause.
4. Full retroactive F4 closure-state labelling, deferred to forward-going discipline rather than a sweep.

A new feedback memory file landed during the post-compaction debrief on 23 April: `feedback_fix_all_scope_split.md`, capturing the lesson that autonomous fix-all windows must decompose the target list into bounded-fix, specification-only, or full-sweep at write time rather than at debrief.

## Open items

Four items remain open at the close of the hiatus. None has been touched.

1. **Focused confer round scope.** Proposed scope:
   - Q1: G2 code correctness at `bench/immune_agents.py:5411-5421`
   - Q2: §2a target-article scope briefs for Experiments 47, 51, 52, 53
   - Q3: §6b trigger specifications for G6, G7, G8
   - Q4 (optional): G6/G7/G8 trigger-versus-implement policy
2. **Path for G6, G7, G8.** Three options: (a) add as a dedicated question in the focused confer round, (b) implement now in a rested pass, (c) accept deferral with explicit flagging in the pre-launch checklist. G6 is specialist-to-specialist verdict-conflict resolution, G7 is the merge-deadlock automatic arbitration, G8 is the burst-mode phase-zero convergence override.
3. **Residuals disposition.** Whether the four residuals listed above block Experiment 40 launch or defer to post-launch housekeeping.
4. **Experiment 40 launch approval itself.** Pre-launch runtime work is closed. The question is whether items 1–3 gate launch, or whether launch can proceed while a focused confer round runs in parallel.

## Integrity caveats

Two points from the oversight question-and-answer worth re-stating cold so they are not lost between sessions.

The Popperian framing applied to G6, G7, and G8, namely that arbitration rules must emerge from post-mortem evidence rather than being pre-registered, is genuine design discipline. It is also in part cover for overnight-risk judgement calls that would have benefited from founder input or a second-model review. Both characterisations are true.

Panel-review status across the pre-launch surface is uneven. Already reviewed: F1/F2/F3 strategy, the Gate C admissibility-parser preflight step, the Stage 6 calibrator design, the Experiment 40 to Experiment 54 scope and ordering, the §6b native-synthesis commitment, the K/L/M non-distortion principle, and the shadow-promotion-now policy. The shadow-promotion-now policy is the rule that verified shadow elements move to live use under non-distortion evidence rather than waiting for a separate promotion experiment. Not yet reviewed: the G2 code-correctness fix, the §2a scope briefs, the §6b trigger specifications, the test-coverage adequacy of G3/G4/G5, and the lexicon wording of G9. The focused confer round in item 1 is intended to close that review gap.

## Recommended next move

If the goal is the shortest path to Experiment 40 launch with integrity intact, the natural sequence is:

1. Settle item 1 by approving, amending, or substituting the focused confer round scope. A three-or-four-question focused round dispatched via star topology is one bounded confer cycle. Cost is roughly the dispatch wall-clock plus a read of the consolidated outcome.
2. As the focused round returns, settle items 2 and 3. Both become easier once the panel-review gap on G2, §2a, and §6b is closed.
3. Settle item 4 — Experiment 40 launch approval — on a clean documentary state.

Alternative path: launch now and run the focused confer round in parallel. Pre-launch runtime code is closed and tested. Nothing in the focused round is expected to require runtime patches before first dispatch. Choice between the two is founder judgement, not a code question.

## Anchoring documents

| Title | Purpose |
|---|---|
| Agent Operational Tracker | Self-consumption resume pointer for Experiment 40 to Experiment 54 arc plus Bench Run 2. Desktop canonical with byte-identical repo mirror in `experimental_notes/`. |
| Recovery Document | `resources/RECOVERY.md`. Carries the 22 April debrief block in its current pending work section. |
| Consolidated Plan | Repo mirror at `experimental_notes/Exp40_to_54_Consolidated_Plan_2026-04-21.md`. Gap-closure table at §6a, trigger specifications at §6b, target-article scope briefs at §2a. |
| Fix-All Scope Split Lesson | `feedback_fix_all_scope_split.md` in the project memory folder. |

## Next review trigger

The next decision point is the founder's response on the focused confer round scope. Once approved, amended, or substituted, the autonomous queue advances either to dispatching the focused round or to direct work on items 2 through 4. Until that response, no further autonomous task is outstanding.

Written under CDSFL note standard v1 (21 April 2026).
