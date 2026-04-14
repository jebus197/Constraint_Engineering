# Mathematical Tool Usage Analysis — Exp 39-0

## Overall Verdict

**R_k mathematical model adoption: 5/5 (100%).** All models compute R_k self-assessment scores with explicit arithmetic chains. This matches Exp 37 baseline (88-100%).

**SymPy/z3/numpy actual tool execution: 0/5.** No model invoked any mathematical library. Root cause: API dispatch mode provides no code execution sandbox. Models perform manual arithmetic — mostly correct, with errors in DeepSeek and abbreviated computation in Gemini.

## Per-Model Assessment

**CC2 (Claude Opus 4.6):** R_k computed with full step-by-step inline arithmetic. Python semantics claims verified by language spec reasoning. Falsification quality strong with genuine falsifier construction. Second-highest reasoning quality in panel.

**Codex (GPT-5.4):** Most detailed derivation chains. R_k and break-even (S*) computations hand-computed with full intermediate values. Falsification thorough with counterexample construction. Highest reasoning quality in panel.

**ChatGPT (GPT-5.4):** R_k computations inline with full chains. Break-the-fix attempts genuine. Format variation (JSON vs prose) but quality consistent.

**Gemini (3.1 Pro):** R_k present but abbreviated — intermediate steps truncated, fixed nu_eff values (0.05 or 0.02) rather than computed. Reduces auditability. Falsification shorter, sometimes formulaic.

**DeepSeek (R1-0528):** Most findings per round but shallowest per-finding reasoning. Contains at least two incorrect claims that tool verification would have caught (mutable default fix that does nothing, int() parsing claim that's wrong). Falsification sections thin.

## Summary Table

| Model | R_k Computed | SymPy | z3 | NumPy/SciPy | Falsification Quality | Tool Directive Followed |
|-------|-------------|-------|----|-------------|----------------------|------------------------|
| CC2 | Yes, detailed | No | No | No | Strong | R_k yes, tools no |
| Codex | Yes, detailed | No | No | No | Very strong | R_k yes, tools no |
| ChatGPT | Yes, detailed | No | No | No | Strong | R_k yes, tools no |
| Gemini | Yes, abbreviated | No | No | No | Good | R_k partial, tools no |
| DeepSeek | Yes, with errors | No | No | No | Weak-moderate | R_k yes, tools no |

## Root Cause

Models are dispatched via API calls in plain text completion mode. They do not have access to a Python runtime during response generation. The CDSFL directive instructs R_k computation (which they do) but actual tool execution would require tool-use API mode or a pre/post-processing validation step.

## Recommendations

1. Add post-parse R_k validation that recomputes from stated parameters and flags discrepancies (~10 LOC).
2. For actual tool execution, implement tool-use API mode in specialist dispatch (Phase 6).
3. Distinguish "compute R_k" (working) from "execute SymPy" (requires infrastructure) in the directive.
