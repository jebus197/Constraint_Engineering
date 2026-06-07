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

**Answer to "does resolving the residuals take Exp 42 over the line?":** it gets it *to* the line honestly (8 confirmed real defects, 7 escalated, zero faked); the HIL steps it over by adjudicating the 7. No single-step auto-convergence is possible without faking.

## 6. Remaining work

- **Wire the max-3 retry into the runner round loop** (validated out-of-band here; not yet in-runner).
- **Severity calibration** (9/15 over-rated, prior note) to lower the new-critical rate → help gate 2.
- **Optional:** a resume of Exp 42 with retry + calibration ON to observe gates 1+2 close live (will surface marginal new findings — diminishing returns per founder caution).

## 7. Commits

`0a4d8ce` CONFIRM-only gate + test; `9381980` harness hardening + retry/correctness notes.

---
*Written under CDSFL note standard v1.2 (14 May 2026). Plain-English: `Falsifier_CONFIRM_Only_Design_Plain_English_2026-06-07.md`; TTS: `~/Desktop/CDSFL_tts/Falsifier_CONFIRM_Only_Design_2026-06-07.txt`.*
