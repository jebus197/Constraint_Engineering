# CONFIRM-only Falsifier Gate: the Clean No-Faking Design

**2026-06-07 12:19 BST.** Supersedes the "refutation scrutiny" recommendation in `Falsifier_Retry_Test_2026-06-07.md` §5.3 — that proposed fix FAILED its own test. Documents the design that replaced it, its validation on the 15 Exp-42 residuals, and the honest convergence verdict. Committed `0a4d8ce`.

## 1. Why "refutation scrutiny" was dropped

The earlier note recommended verifying a suspect REFUTED by having an *independent strong model* write a fresh falsifier. **Tested and it failed:** gpt-5.5, given C0019/C0028/C0040 with explicit anti-pattern hints, **also REFUTED the two real defects** (C0028, C0040) single-shot. A lone falsifier — even from a strong model — falls into the same traps (mutate-in-place comparison, inert stand-in). The audit caught them only via skeptical, *iterative*, code-reading investigation, which a single falsifier does not replicate. So scrutiny-by-another-falsifier is not reliable.

## 2. The design: CONFIRM-only for criticals

The Exp-42 verdict-correctness audit established a one-sided error profile: **CONFIRMED 7/7 correct, REFUTED 1/3** (C0028/C0040 false). Mechanistic cause: a CONFIRMED requires an active `AssertionError`/`FALSIFIED` demonstration (essentially unfakeable); a REFUTED is a passive clean exit, which a logically-broken falsifier also produces. So:

> **A critical (sev ≥ 0.7) is resolved ONLY by a CONFIRMED demonstration.** A REFUTED on a critical is NOT trusted to drop it — it is escalated to HIL. A REFUTED on a non-critical is still trusted (no masking risk).

`bench/reference_runner_v2.py::apply_falsifier_verdicts`, gated. `test_falsifier_gate.py`: critical clean-run now asserts HIL/escalated; non-critical clean-run asserts REFUTED (asymmetry locked in). 141 falsifier/gate tests pass.

**This eliminates the one place a real critical can be faked away** — a false REFUTED masking a real defect is now structurally impossible.

## 3. The retry: CONFIRM-only, max-3, honest framing

Un-CONFIRMED critical (REFUTED / ERROR / no falsifier) → re-dispatch the source model up to 3×, each attempt fed the prior re-run result, **honest framing** (raise IFF the defect is genuinely present; clean-exit if genuinely absent — *not* biased toward confirming, so a CONFIRMED stays reliable). Still un-CONFIRMED after 3 → HIL. Harness hardening (`falsifier_verify._sandbox_env`, both repo root + `bench/` on PYTHONPATH) is committed and removes the relative-`sys.path` failure class.

## 4. Validation on the 15 Exp-42 residuals

| outcome | count | findings |
|---|---|---|
| **CONFIRMED** (real defect, auto-resolved) | **8/15** | C0023, C0029, C0031, C0032, C0033, C0037, C0046 (orig 7, audit-correct) + **C0019** (retry) |
| **HIL** (genuine exception, never dropped) | **7/15** | C0028, C0040 (sy-verified real, models can't auto-demonstrate); C0015, C0034, C0036, C0054, C0063 (un-adjudicated after max-3) |

**No false REFUTED (no masking). No false CONFIRMED.** Both checked:
- **C0019 — the false-CONFIRMED stress test.** The retry flipped it CONFIRMED; the audit had called it a non-defect. sy-verified: `_block_is_hard(".. code-block:: python\\n   # This is a HARD problem")` → **True**, control (no HARD keyword) → **False**. This is the SAME over-classification class as audit-CONFIRMED C0029 (`"You should ALWAYS check for null."` → True) and C0031. So the CONFIRMED is a **real** defect. The audit's REFUTED was correct only for the *original* falsifier, which tested the one sub-case the space-padding handles (`"SHARED"`). **The old `REFUTED→drop` gate would have masked this real defect; CONFIRM-only + retry caught it.** Net validation that the design is strictly better.

## 5. Honest convergence verdict

Convergence has two gates; resolving the residuals touches only one.

1. **No unverified critical pending** — the 8 CONFIRMED clear; the **7 HIL'd ones still block it** (escalated, not resolved). The human adjudicating those 7 (confirm real / drop false-positive) clears this gate.
2. **Panel quiescence** (3 consecutive zero-new-critical rounds) — SEPARATE. Exp-42 `novel_this_round` was 15→1 (approaching) but never zero.

**So the system cannot fully auto-converge — and that is the no-faking floor, not a bug.** The 7 are real un-auto-confirmable criticals; trusting a clean exit to clear them is the exact masking just eliminated. They are the "exceptions where minimal HIL isn't possible." Path to genuine convergence: **HIL adjudicates the 7 exceptions → gate 1 clears; the panel quiets over a few rounds (helped by severity calibration, still pending) → gate 2 clears → Exp 42 converges, genuinely.**

**Answer to "does resolving the residuals take Exp 42 over the line?":** see §6 — the "7 → HIL" figure below was CORRECTED: the HIL floor on this target is **zero**.

## 6. CORRECTION (12:50 BST) — the 7 "HIL exceptions" are ALL resolvable; HIL floor is ZERO

The §4/§5 framing called 7 residuals "genuine exceptions" needing the HIL. **That was wrong, and was tested to destruction.** A 14-agent workflow (`wf_f046bc18`) had a capable writer investigate each of the 7 — read the real `composer.py`, write a correct falsifier, RUN it through `reverify_falsifier`, adversarially re-check — and **all 7 → CONFIRMED real defects, 0 genuinely un-resolvable** (re-run independently here: 7/7 CONFIRMED).

| residual | real defect | why the source model failed | category |
|---|---|---|---|
| C0028 | phenotype transform corrupts HARD situation packet (composer.py:1362) | DeepSeek compared a value `compose` mutates **in place** → false REFUTED | **duplicate** of CONFIRMED **C0003** (Codex) |
| C0015 | `_prune_for_coherence` density math prunes all SOFT packets | DeepSeek imported a **hallucinated module** (`...policy`) | **duplicate** of CONFIRMED **C0001** |
| C0040 | `_load_universal_directive` swaps full→minimal even for non-minimal models | ChatGPT wrote **no falsifier** (empty) | none_resolvable (capability) |
| C0034 | fallback density calibration returns const ~0.057 | DeepSeek **hallucinated the API signature** → ERROR | none_resolvable |
| C0036 | `resolve_layer_conflicts` knows only 4 hard-coded topics | **no falsifier** (self-asserted "VERIFIED") | none_resolvable |
| C0054 | `_directive_topic_and_stance` returns only the first topic | **no falsifier** (empty) | none_resolvable |
| C0063 | `_apply_phenotype_transform` destroys markdown code blocks | Gemini falsifier **truncated** at 97 chars | none_resolvable |

**None falls into a legitimate HIL category** (0 genuinely_hard_to_falsify, 0 safety, 0 core_functionality, 0 uncertain, 0 contested). 2 are duplicates of already-CONFIRMED findings; 5 are model-capability gaps. Every one is deterministic synchronous data-flow — nothing resists falsification.

**Why the earlier max-3 retry got 1/8 but this got 7/7:** the retry re-asked the **same weak source models** that already failed. The fix is **routing** — an un-confirmed critical must go to a **capable** falsifier-writer (strongest model / iterative agent), NOT the source model — plus **deduplication** so a residual whose defect is already CONFIRMED elsewhere is never escalated.

**Corrected convergence answer:** gate 1 (no unverified critical pending) clears with **zero HIL** on this target once the retry routes to a capable writer + dedup runs. Gate 2 (quiescence) still needs severity calibration. The genuine-HIL categories are real but live in *other* targets (concurrency/timing, safety, authority), not these 7.

## 7. Remaining work

- **Retry routing fix:** re-dispatch un-confirmed criticals to a CAPABLE falsifier-writer (not the source model) + iterate. Validated out-of-band (7/7); wire into the runner round loop.
- **Deduplication:** detect when a residual's defect is already CONFIRMED under another id (C0028↔C0003, C0015↔C0001) and never escalate it.
- **Severity calibration** (9/15 over-rated) → help gate 2.

## 8. Commits

`0a4d8ce` CONFIRM-only gate + test; `9381980` harness hardening + retry/correctness notes; resolvability finding this section (workflow `wf_f046bc18`).

---
*Written under CDSFL note standard v1.2 (14 May 2026). Plain-English: `Falsifier_CONFIRM_Only_Design_Plain_English_2026-06-07.md`; TTS: `~/Desktop/CDSFL_tts/Falsifier_CONFIRM_Only_Design_2026-06-07.txt`.*
