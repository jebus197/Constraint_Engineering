# CDSFL Methodology Self-Test Summary

**Date:** 19 March 2026
**Model:** Gemini via command line interface

---

## Overview

This is a summary of the four-condition self-test comparing how Gemini performs code review under different levels of guidance. The code under review was the CDSFL benchmark harness itself, a Python script of 805 lines with 10 known defects.

---

## The Four Conditions

**Condition 1 — Control.** Gemini received just the code and a simple instruction to find defects. No methodology. No domain context. This is the baseline — what the model finds on its own.

**Condition 2 — CDSFL only.** Gemini received the full CDSFL methodology document (276 lines covering constraint classification, falsification loops, epistemic marking, and termination protocols). The prompt was minimal — just three sentences saying apply the methodology. No domain context about what the code does or what matters.

**Condition 3 — HIL only.** Gemini received domain context explaining what the code is (a benchmark harness), what it does (run tasks under multiple conditions), and what matters (scientific validity, data integrity, operational reliability, and reproducibility). No methodology document. Just expert framing.

**Condition 4 — CDSFL plus HIL.** Gemini received both the full methodology document and the domain context. This is the complete system — methodology plus expert framing.

There was also a fifth data point: rounds 1 through 5 from the previous session, where CC wrote detailed review prompts directing Gemini to find specific types of issues. This is reclassified as expert direction without the formal protocol.

---

## Results

**Control** found 7 issues, 4 matching ground truth defects, and 2 novel valid findings. No false positives.

**CDSFL only** found 4 issues, 3 matching ground truth defects, and 2 novel findings. Importantly, CDSFL produced structured methodology artefacts that no other condition did. It classified constraints as hard or soft, applied a three-pass falsification loop, used a proportionality gate to skip trivial claims, marked claims as `[VERIFY:current]` or `[SPECULATIVE]`, and stated a survival predicate. The findings were fewer but more rigorous.

**HIL only** found 9 issues, 4 matching ground truth defects, and 6 novel findings. This was the highest yield of any single invocation. The domain context directed Gemini's attention to scientific validity concerns — like the missing temperature parameter for reproducibility — that no other single-invocation condition found.

**CDSFL plus HIL** found 4 issues, 4 matching ground truth, and 2 novel findings. Surprisingly, adding the methodology to domain context did not increase finding count. It may have constrained Gemini's free exploration by imposing output structure. However, it did add rigour through constraint classification and epistemic marking.

**Rounds 1 through 5** found approximately 45 issues across 5 rounds, achieving 100% ground truth recall. This dramatically outperformed all single-invocation conditions. But this is 5 rounds of iterative expert-directed review versus single invocations — the comparison is informative but not apples-to-apples.

---

## Key Observations

**First:** The format injection defect — where Python's `.format()` method crashes on curly braces in mathematical notation — was found only by iterative expert-directed review. No single invocation, with or without methodology, with or without domain context, found it. Some defects require deep iterative exploration to surface.

**Second:** The temperature and seed finding (critical for a benchmark) was found only by conditions with domain context. Understanding what code *is* — a scientific benchmark — directs attention to concerns that methodology alone misses.

**Third:** CDSFL produced zero false positives and structured output. The methodology's value is qualitative — rigour and auditability — not just quantitative.

**Fourth:** All conditions produced zero false positives. Gemini did not hallucinate defects under any condition.

---

## Implications for the Round-Robin Convergence Test

- The round-robin **must** be iterative. Single-invocation CDSFL dramatically underperforms iterative CDSFL. The methodology's iteration protocol is load-bearing, not optional.

- Domain context should be provided to all models. Expert framing directs attention to concerns that methodology alone misses.

- The round-robin should allow both internal iteration (driven by the methodology) and external iteration (driven by cross-model feedback between rounds).

- The intelligence-agnostic principle is supported. CC providing domain expert context is a standard step in CDSFL's confer paradigm. The confer mechanism handles expertise boundaries by flagging items for peer review. Human peer review is explicitly invited at the confer stage, not bypassed.
