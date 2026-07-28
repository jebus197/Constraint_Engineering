# Falsifier Mechanism — Progress and Plan

**2026-06-06 16:56 BST**

## What the original problem was

The falsifier mechanism is the heart of the current work. When the panel of models reviews a piece of code, each critical finding is supposed to carry a small runnable test — a *falsifier* — that the runner can execute on its own. If the test fires, the defect is real and the finding is confirmed *by the tool*, not by any model's opinion. If a finding has no runnable test, it goes to a human rather than being confirmed on trust. In the live run that started this investigation, all fourteen findings went to the human queue because none carried a runnable test. The mechanism was producing prose, not testable code. That was the problem to solve.

## The central fix — found, verified, and now in the core

The operational directive every model receives contains §2, which defines what a falsifier is. The original definition described it in prose: state the condition that would disprove the claim, what was tested, the result. Models read that and produced prose. The fix redefines §2 to demand a runnable Python block that imports the **real** target module and either raises an error or prints a marker word *if and only if* the defect is genuinely present. With that single change the strongest models began producing real runnable tests that the runner re-ran and confirmed.

This change is now in the core runner, gated on the falsifier gate (off → directive byte-identical, so non-gate experiments are unchanged). Verified: directive rewritten gate-on, untouched gate-off, full suite passes (293 tests). Real progress on the original problem — the mechanism now produces testable falsifiers for the capable models.

## The measurement, and what it showed

A test matrix was run: five models × {whole, decomposed} × three runs = thirty cells. The result was uneven.

| Model | Whole (testable/critical) | Decomposed (testable/critical) |
|---|---|---|
| cc2 (opus) | 5/6 | **8/8** |
| chatgpt (gpt-5.5) | 2/10 | 7/11 |
| cx (gpt-5.5) | 5/9 | 3/7 |
| gemini-3.1-pro | 2/5 (+1 empty) | 0/1 (crap-out) |
| deepseek-v4-pro | 0/1 (crap-out) | 0/0 (crap-out) |

The strongest model produced a runnable test for almost every critical on both methods. Two produced them ~half to two-thirds of the time. Gemini and DeepSeek largely failed, and on decomposed produced almost nothing.

## Why the two weak models failed — the real cause

The cause is **not** model incapability. The raw outputs show fixable plumbing faults.

- **Single-chunk forced-decomposition.** The target is 113K chars — a single chunk for these models. An 80K threshold forces *any* payload above it into decomposed delivery, even a single chunk. Splitting one chunk gains nothing and adds failure points. The threshold fires when it shouldn't.
- **Synthesis blind to raw code.** Decomposed runs in two stages: Phase-1 analyses each chunk; Phase-2 (synthesis) is handed *only the Phase-1 analyses, never the original code*. When a Phase-1 analysis is empty, synthesis has nothing. Gemini said so in its own output: *"no code had been provided… nothing to assess."* It was correct — the code never reached it.
- **Gemini reasoning-budget exhaustion.** Phase-1 chunk analysis ran on an 8192-token budget with **no reasoning config**. Gemini's private reasoning consumed the whole budget → empty visible content. Same root cause behind an intermittent whole-path empty (one run: 507s → nothing).
- **DeepSeek markup.** DeepSeek emits tool calls as pipe-delimited (`｜`) markup inside the message text, not the normal field. Phase-1 doesn't parse it, so the analysis is unusable. Notably, even broken, DeepSeek had written a genuine runnable falsifier importing the real module — it was engaging; the plumbing lost the output.

## What is being kept, to be clear

**Decomposed delivery is being kept.** It is the fallback for when a single whole delivery is too large to succeed, and that design is sound. The faults above are reasons to *fix* it so it works for every model when needed — and to stop it being triggered when whole would have worked — not reasons to remove it.

## What remains, and the plan

Bar: **every** model, not only the strong ones, produces runnable testable falsifiers. Plan, decomposed delivery kept:

1. Give Phase-1 chunk analysis the same reasoning budget + config the whole path already uses → Gemini's Phase-1 stops emptying.
2. Parse DeepSeek's pipe-delimited markup in Phase-1 extraction → its analysis becomes usable.
3. Safety net: if any chunk analysis is still empty, include that chunk's raw code in synthesis → synthesis is never blind.
4. Time + iteration ceiling on the whole-path tool loop → Gemini can't burn 500s then return nothing; force findings before that point.
5. Restore intended order: try whole first for payloads that fit; fall back to decomposed only when whole is genuinely too large or fails. Correct the 80K threshold that pre-empts whole.
6. Once all five produce testable falsifiers on a clean matrix re-run, run a full-panel confirmation through the real runner — the true test.

## Honest status

The core fix is in and verified for the strong models. The reasons the weak models failed are now understood, and they are fixable plumbing faults rather than model limits. The work is **not** finished: the Phase-1 budget, the synthesis safety net, and the whole-path ceiling still need building and testing, and only a clean re-run will show whether the high bar is met. Nothing committed to core beyond the verified §2 change — testing before touching real code.

---
*Written under CDSFL note standard v1.2 (14 May 2026).*
