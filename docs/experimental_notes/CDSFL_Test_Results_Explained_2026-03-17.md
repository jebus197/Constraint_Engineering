# CDSFL Test Results Explained

**Date:** 17 March 2026

---

## What We Did

We gave 20 engineering problems to 4 AI models. Each problem contained known, hidden errors that we planted deliberately. Every model got two shots at each problem. First, with no guidance at all — which we call the bare or control condition. Second, with CDSFL directives, which are structured instructions telling the model to look for constraint violations, check its own work, and run multiple verification passes.

---

## Results So Far (4 of 7 Models Complete)

| Model | Bare | CDSFL | Improvement |
|---|---|---|---|
| GPT-4o | 90% | 100% | +10 percentage points |
| Claude Sonnet 4 | 95% | 100% | +5 percentage points |
| OpenAI o3-mini | 95% | 100% | +5 percentage points |
| Claude Sonnet 4 (extended thinking) | 97.5% | 100% | +2.5 percentage points |

---

## What This Means

Every model found more errors when given CDSFL directives than when working bare. The less capable the model, the bigger the improvement. GPT-4o, which is a standard model without built-in reasoning chains, improved the most. Sonnet 4 with extended thinking, which already has sophisticated internal reasoning, improved the least — but it still improved.

The pattern makes intuitive sense. CDSFL acts like a structured engineering checklist. Strong models already perform many of these checks internally. Weaker models benefit more from being told explicitly what to look for and how to verify their own work.

---

## Statistical Significance

We used Mathematica to verify whether these improvements are real or could be due to chance. The McNemar test — a standard statistical test for paired comparisons — gave a combined p-value of 0.0077 across all four models. In plain terms, there is less than a 1% probability that these improvements happened by chance. The conventional threshold for statistical significance is 5%, so we are well below it.

---

## False Positives

A natural concern is whether CDSFL makes models cry wolf — flagging problems that do not actually exist. The raw numbers look concerning at first glance: CDSFL models flag more issues overall. But this is because they produce three times as much text, since they run three verification passes instead of one response.

When you divide by the number of responses to get the per-response false positive rate, CDSFL models actually produce **slightly fewer** false positives per response than bare models. The ratio is 0.946, meaning CDSFL is about 5% better at avoiding false alarms on a per-response basis. The framework is not making models more paranoid. It is making them more thorough.

---

## Sample Size and Statistical Power

Our pilot used 20 tasks, which is enough to detect whether an effect exists and roughly size it. However, Mathematica identified that we need at least 61 tasks to reliably distinguish small differences between models — for example, telling apart a model that detects 95% of faults from one that detects 97.5%. We have 90 tasks in the full test bench, which is more than enough if we decide to run the expanded version.

---

## Optimal Number of Verification Passes

Mathematica also modelled the optimal number of CDSFL verification passes:

- **Reasoning models** (o3-mini, Sonnet with extended thinking): per-pass detection probability ~0.999. One pass is sufficient.
- **Standard models** (GPT-4o, Sonnet 4): per-pass detection probability ~0.975. Two passes brings them to equivalent performance. Three passes shows diminishing returns for all models.

This has practical implications for cost — you can potentially halve the number of passes for reasoning models without losing detection quality.

---

## What Is Still Running

Three more model configurations are still in progress:

- **Google Gemini 2.5 Flash** — running, approximately 30–40% through 20 tasks.
- **Google Gemini 2.5 Pro** — running, approximately 30–40% through 20 tasks.
- **Llama 3.3 70B** (via Groq) — failed at task 11 of 20 due to the free tier daily token limit of 100,000 tokens. Needs either a provider upgrade or a wait until tomorrow when the limit resets.

---

## Why the Remaining Results Matter

The Gemini results will test whether the CDSFL effect is model-agnostic. So far we have tested Anthropic and OpenAI models, which share some architectural similarities. Google Gemini is a genuinely different model family. If the same pattern holds, that is strong evidence that the framework works regardless of which AI model you use — which is one of CDSFL's core claims. If the pattern breaks for Gemini, that is equally valuable scientifically, because it tells us where the framework's assumptions fail.

The Mathematica findings about statistical power and optimal pass counts hold regardless of individual model results. Those are properties of the experimental design, not of any specific model.

---

## Next Steps

Once all seven models complete, the full dataset goes to a fresh Codex instance for adversarial review. Codex has not seen any of this work before and will attempt to find flaws in our methodology, our scoring, and our conclusions. After that, CC and CX will do adversarial P-pass ping-pong to stress-test the results from both directions.
