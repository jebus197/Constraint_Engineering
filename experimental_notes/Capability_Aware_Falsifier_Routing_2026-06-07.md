# Capability-Aware Falsifier Routing (Take-Up-Slack) — Design + Validation

**2026-06-07 15:31 BST.** When a weak model leaves a critical finding un-confirmed, route falsification to progressively stronger writers rather than re-asking the weak model or escalating to a human. Restores the capability-aware routing that the live runner had collapsed into flat parallel dispatch. Module committed `d383a6e` (validated, unit-tested; not yet wired).

**[Correction 2026-08-05.]** The module path used throughout this note — `bench/take_up_slack.py`, §4 heading and §5 — is dead at the current HEAD. The file was **renamed, not deleted**: `bench/take_up_slack.py` → `bench/routing.py` on 2026-07-12 in commit `349951f` ("A3: rename take_up_slack -> routing (code-only; behaviour byte-identical)"). Verified by `git log --diff-filter=D --name-only -- bench/take_up_slack.py` (one deletion, in `349951f`) and `git log --diff-filter=A --name-only -- bench/routing.py` (added in the same commit). The code is intact at the new path; the `take_up_slack` function and log-prefix names moved with it. The *config key* `take_up_slack_enabled` is **not** dead — it is still accepted as a back-compatible alias for `routing_enabled` on both config-ingestion paths (`bench/launcher_core.py:216`, `bench/reference_runner_v2.py:760`), and the Exp 42–49 configs still carry it. This entry is left intact as historical record; it described the tree correctly on 2026-06-07.

## 1. The architecture already exists — it was dormant

The capability-aware routing the founder remembered is built but disconnected from the live runner:

- **Capability fingerprints** — `bench/dm/_types.py` (4-D: detection-decay, verification-quality, accuracy, coverage); hardcoded baselines `runner_core.py:66–72` already rank **CC2 strongest (decay 0.10) → DeepSeek weakest (0.25)**.
- **LoadBalancer** (`bench/dm/_load_balancer.py`, multi-objective task allocation) and **RoleAssignment** (`bench/dm/_role_assignment.py`, PM/COL/PAR by capability) are instantiated via `DynamicManager` (`reference_runner_v2.py:4810`) but **never called for routing**. Models are dispatched in a flat parallel fan-out — identical treatment every round.
- **CC2 player-manager** (`bench/cc2_manager.py`, bounded-authority router + 5 claude_cli sub-agents) is also **dormant** — not called from the live loop.

So "take up the slack" is not a new hack; it is **wiring the dormant capability routing for the one task blocking convergence**: falsification.

## 2. Primary offender (data, Exp-42 run)

| model | findings | confirmed | residuals (of 15) | confirm rate |
|---|---|---|---|---|
| **DeepSeek** | 18 | 5 | **10** | **28%** |
| Gemini | 25 | 20 | 4 | 80% |
| ChatGPT | 6 | 4 | 1 | 67% |
| **CC2 (opus)** | 8 | 6 | **0** | 75% |
| **Codex (gpt-5.5)** | 10 | 9 | **0** | 90% |

DeepSeek is the weak link by a wide margin (10/15 residuals, 5/7 hardest). CC2 and Codex leave **zero** residuals. The two zero-residual writers should adjudicate; DeepSeek should never be asked to take up slack.

## 3. Three tests (run before building anything)

- **Teaching the weak model** (founder's "demand it checks its work"): DeepSeek taught with two worked corrections of its own mistakes + principles, tested on three *fresh* findings → **1/3** CONFIRMED (vs 0/5 untaught). Verdict: a marginal booster, **not a cure** — LLMs do not learn across calls; the lift must be re-supplied every time, which is a costlier way to do what routing does for free. Salvageable value: the loop is a useful **confidence cross-check** (does the original finder agree the falsifier tests its claim?), guarding against the C0019 re-scope failure mode — keep it for *that*, not as a fix.
- **Take-up-slack** (strong writer + execute_python tool loop, the in-runner dispatch path): on the 7 hardest residuals (weak source models **0/7**), gpt-5.5 + tool loop = **6/7 CONFIRMED**.
- **C0063** (the 7th): gpt-5.5 trips **consistently** (2/2) on a string-embedding trap — the finding is about `_apply_phenotype_transform` destroying markdown code blocks, so the falsifier must embed a fenced code block as a literal, and gpt-5.5 produces nested triple-quotes that break its own test (`unterminated triple-quoted string`). The strongest rung (opus-class agent) handles it — workflow `wf_f046bc18`'s C0063 falsifier CONFIRMED (re-verified). So the **2-rung ladder reaches 7/7**.

## 4. The design (module `bench/take_up_slack.py`)

For each un-confirmed critical (escalated by `apply_falsifier_verdicts`):
1. **Dedup** — if the defect is already CONFIRMED under another id (C0028↔C0003, C0015↔C0001), resolve as a duplicate; never escalate a confirmed defect.
2. **Ladder** — route to progressively stronger writers (by capability fingerprint), **excluding the finding's own failed source model**, with the execute_python tool loop. The runner's `reverify_falsifier` is the decider, never the model. CONFIRMED wins.
3. **HIL** — only if even the strongest writer can't confirm (a genuinely-hard, e.g. nondeterministic, defect).

CONFIRM-only still holds throughout: a REFUTED at any rung is not trusted to drop the critical; it just advances to the next rung. Runner-agnostic + side-effect-free (`resolve_fn` / `reverify_fn` / `similarity_fn` injected). **10 unit tests pass.**

## 5. Status + next step

- **DONE:** module built, unit-tested, committed `d383a6e`; mechanism validated end-to-end (6/7 single rung, 7/7 ladder).
- **NEXT (deliberately not done at session end):** wire `take_up_slack` into the round loop at the single call site after `apply_falsifier_verdicts` (`reference_runner_v2.py:5396`), gated; provide `resolve_fn` = the runner's `dispatch(strong_cfg, prompt, enable_tools=True)` + falsifier extraction, `similarity_fn` = `_finding_similarity`. Then the convergence test: resume Exp 42 with take-up-slack ON → does it converge with zero residual-HIL? (Behind the founder's gate to review the Exp 40–54 contents first.)
- **Role-specialisation** (broader): keep DeepSeek as a *finder* (its findings are mostly real) but stop trusting it to *falsify*. This is the substrate-agnostic load-balancing the project was built for; the full DynamicManager/LoadBalancer revival is a larger separate piece.

---
*Written under CDSFL note standard v1.2 (14 May 2026). Plain-English: `Capability_Aware_Falsifier_Routing_Plain_English_2026-06-07.md`; TTS: `~/Desktop/CDSFL_tts/Capability_Aware_Falsifier_Routing_2026-06-07.txt`.*
