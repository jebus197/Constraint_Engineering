# Master Finding Registry: C1 + C3 + C4 Collated

**Date:** 4 April 2026
**Code artifact:** `immune_agents.py` pre-v2, commit 927bfbc
**Model:** Gemini 3.1 Pro (all conditions)
**Verification:** All findings independently verified (SymPy, code inspection, or both)

## Status Key

- **V2 FIXED** — addressed by v2 shadow component (not yet activated)
- **V2 PARTIAL** — v2 shadow exists but doesn't fully address the issue
- **UNFIXED** — no fix in current codebase
- **MITIGATED** — partially addressed by existing safeguard (e.g. timeout)

## Fix Priority

- **P0** — silent data corruption or security vulnerability
- **P1** — incorrect results under normal operation
- **P2** — incorrect results under edge conditions
- **P3** — performance, dead code, or defence-in-depth

---

## DENDRITIC CELL (6 findings)

### MF-01: MATH_PATTERN Overbroad Regex (Math Hijack)
- **Sources:** C1-F14, C3, C4-DC4
- **Status:** V2 FIXED (`_MATH_PATTERN_V2`, lines 1791–1800)
- **Priority:** P0
- **Description:** `_MATH_PATTERN` matches bare `=`, `-`, `!`, `/`, `+`. Any description containing a hyphen (e.g. "use-after-free"), exclamation mark, or slash is misrouted to MATHEMATICAL instead of CODE_BEHAVIORAL. 30% of standard bug descriptions hijacked in testing. Downstream: misrouted claims fail CT Cell verification, inflating rejection rate, potentially triggering autoimmune flag.
- **Verification:** SymPy + regex testing. Confirmed worse than originally described — bare punctuation matches.
- **Fix:** Activate `_MATH_PATTERN_V2` which requires equation context (backtick-wrapped, numeric comparisons, named variables).

### MF-02: Extraction Asymmetry (T ⊄ E)
- **Sources:** C4-DC1
- **Status:** UNFIXED (related to MF-01 but distinct)
- **Priority:** P1
- **Description:** The trigger set T (patterns that activate MATHEMATICAL classification) is a strict superset of the extraction set E (patterns the backtick regex can extract). Unary operations (`-1`), functional math (`sqrt(x)`), and SymPy syntax (`Eq(x,y)`) trigger classification but fail extraction. Extraction regex requires binary operator with |L|≥1, |R|≥1.
- **Verification:** Regex testing. `Eq(x,y)` and `sqrt(x)` provably fail extraction despite triggering.
- **Fix:** Align trigger and extraction sets. Either narrow the trigger or broaden the extraction. V2 MATH_PATTERN partially addresses by narrowing trigger, but extraction regex also needs updating.

### MF-03: Context Erasure
- **Sources:** C4-DC2
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** Backtick extraction uses `re.search` to grab the first backtick-enclosed equation. Conditional context is permanently severed. "Ensure `x < 5` only when `y == True`" extracts only `x < 5`. Downstream verifiers attempt to prove a bounded claim globally, producing false rejections.
- **Verification:** Regex testing confirmed. First-match extracts `x < 5`, precondition lost.
- **Fix:** Extract all backtick expressions and preserve surrounding conditional text. Or pass full description alongside extracted claim.

### MF-04: First-Match Fallacy
- **Sources:** C1-F15
- **Status:** UNFIXED (related to MF-03)
- **Priority:** P2
- **Description:** `re.search()` returns only the first backtick match. If multiple backticked strings exist, the extraction grabs the wrong one.
- **Verification:** Code inspection confirmed. Line 227: `re.search` not `re.findall`.
- **Fix:** Use `re.findall` and select the most mathematically relevant match, or pass all matches.

### MF-05: Logic/Structural Pattern Missing re.DOTALL
- **Sources:** C4-DC3 (ReDoS context), C1-F18 (NK multiline — related)
- **Status:** UNFIXED
- **Priority:** P2
- **Description:** `_LOGIC_PATTERN` and `_STRUCT_PATTERN` use `.*` without `re.DOTALL`. Multi-line descriptions where keywords span lines fail to match. Also creates O(N) backtracking on large inputs without the second keyword.
- **Verification:** Timing test confirmed O(N) scaling. Code inspection confirmed no `re.DOTALL`.
- **Fix:** Add `re.DOTALL` flag. Consider lazy quantifiers (`.*?`) to limit backtracking.

### MF-06: Natural Language Hijack
- **Sources:** C4-DC2 (R2 finding, survived falsification as part of DC-4)
- **Status:** UNFIXED
- **Priority:** P2
- **Description:** `_LOGIC_PATTERN` matches `\balways\b.*\bnever\b`. Conversational text ("I always thought this bug would never happen") triggers LOGICAL classification. Similarly `_STRUCT_PATTERN` matches `\bno\b.*\bclass\b`, routing CSS descriptions to structural verification.
- **Verification:** Regex testing confirmed both patterns match conversational English.
- **Fix:** Require patterns to appear within code-context markers (backticks, indentation) or add negative lookahead for conversational phrasing.

---

## HELPER T CELL — Voting Logic (7 findings)

### MF-07: Net Positive Contradiction (Asymmetric Thresholds)
- **Sources:** C1-F3, C1-F12, C3 (1.5× veto barrier), C4-HT1
- **Status:** V2 FIXED (helper_t_cell_v2_shadow, lines ~2044–2150)
- **Priority:** P0
- **Description:** Thresholds 0.6 (reject) and 0.4 (confirm) sum to 1.0, perfectly partitioning the probability space. Any finding not explicitly rejected is automatically confirmed. A 50/50 split → CONFIRMED. Net negative (C=0.41, R=0.59) → CONFIRMED. Docstring says "net positive confidence to survive" but code implements proportional voting that contradicts this.
- **Verification:** SymPy proof. R/T + C/T simplifies to 1. Concrete examples: net=-0.18 still CONFIRMED.
- **Fix:** V2 implements log-odds within-domain + max-signal across-domain. Explicit 0.7 scaling for rejection evidence. Activate v2.

### MF-08: Dead Else Block
- **Sources:** C1-F10, C1-F20 (algebraic proof), C3, C4 (retracted with nuanced loophole)
- **Status:** V2 FIXED (dead code eliminated in v2)
- **Priority:** P3 (dead code — no runtime impact)
- **Description:** The else block producing UNCERTAIN is mathematically unreachable when T ≥ 0.001 (proof: T < T contradiction). Technically reachable when T ∈ (0, 0.001) via floored denominator, but minimum agent confidence = 0.2 makes this impossible in practice.
- **Verification:** Algebraic proof (C1), SymPy confirmation, C4 found micro-total loophole and correctly assessed it as practically irrelevant.
- **Fix:** Remove dead else block or replace with explicit assertion. V2 eliminates the structure entirely.

### MF-09: Certainty Inversion Paradox
- **Sources:** C1-F11
- **Status:** V2 FIXED (new confidence formula in v2)
- **Priority:** P1
- **Description:** Final confidence = weight/total. A single weak CONFIRMED at 0.1 produces 100% confidence (0.1/0.1=1.0). A strong contested finding (CT CONFIRMED at 1.0 + B REJECTED at 0.9) produces only 52% confidence. System is blind to absolute evidence amount.
- **Verification:** Arithmetic confirmed. Single low-confidence verdict → 100% final confidence.
- **Fix:** V2 uses absolute evidence thresholds alongside ratios. Activate v2.

### MF-10: Micro-Total Discontinuity
- **Sources:** C4-HT2
- **Status:** V2 FIXED (floored denominator eliminated in v2)
- **Priority:** P1
- **Description:** Floored denominator `max(total, 0.001)` used for threshold routing but raw total used for confidence assignment. With C=0, R=0.0006: floored denom=0.001, reject_ratio=0.6 (meets threshold), confidence=0.0006/0.0006=1.0. Near-zero evidence → 100% certainty.
- **Verification:** SymPy confirmed. 0.0006 evidence → 1.0 confidence.
- **Fix:** V2 eliminates the floored denominator pattern. Activate v2.

### MF-11: Verdict Spam
- **Sources:** C1-F13
- **Status:** UNFIXED (v2 does not cap per-cell contribution)
- **Priority:** P2
- **Description:** Additive weighting with no per-cell cap. If a cell outputs multiple verdicts for the same finding, it gets disproportionate voting power. Three NK REJECTED at 0.4 = 1.2 rejection weight, overpowering a single CT CONFIRMED at 1.0.
- **Verification:** Code inspection confirmed. `confirm_weight += v.confidence` sums all verdicts, no deduplication.
- **Fix:** Cap maximum contribution per cell, or deduplicate verdicts by cell before synthesis.

### MF-12: DUPLICATE Semantic Handling
- **Sources:** C4 (retracted — docstring says auto-reject), C1 (implicit in voting)
- **Status:** V2 FIXED (v2 separates duplicate handling from voting)
- **Priority:** P3
- **Description:** DUPLICATE verdicts contribute to `reject_weight`. This is documented behaviour ("DUPLICATE verdicts are auto-rejected") but creates a coupling between deduplication and voting that may not always be desirable.
- **Verification:** Code inspection confirmed. C4 correctly retracted this as "working as documented."
- **Fix:** V2 separates duplicate handling. No code change needed — note for architectural review only.

### MF-13: Rejection Rate Discrepancy
- **Sources:** C1-F8
- **Status:** UNFIXED
- **Priority:** P2
- **Description:** `regulatory_t_cell_check` counts REJECTED and DUPLICATE separately. Pipeline `run_immune_pipeline` counts both together. Inconsistent accounting means autoimmune threshold can be triggered at different points depending on which count is used.
- **Verification:** Code inspection confirmed. Lines 1113 vs 1289 use different counting.
- **Fix:** Unify counting method. Either both include duplicates or neither does.

---

## NK CELL (8 findings)

### MF-14: Continue Bypass (FP Check Skipped)
- **Sources:** C1-F16, C3
- **Status:** V2 FIXED (lines 1975–1978, `is_fp = True; break` then `if is_fp: continue`)
- **Priority:** P1
- **Description:** After marking a finding as DUPLICATE, `continue` skips the false-positive database check. A known hallucination pattern that also matches a prior finding gets tagged DUPLICATE instead of KNOWN_FP. This breaks Regulatory T Cell tracking of systematic model failures.
- **Verification:** Code inspection confirmed. Line 984: `continue` after duplicate verdict.
- **Note:** C4 retracted this arguing multi-signal emission is a feature. C1 correctly identified the downstream consequence (breaks Reg T tracking). The bug is valid — a duplicate should still be checked against the FP database.
- **Fix:** V2 restructures the flow. Activate v2.

### MF-15: Falsy Fallback Bug
- **Sources:** C4-NK-A
- **Status:** UNFIXED
- **Priority:** P2
- **Description:** `fp_db = false_positive_db or _KNOWN_FALSE_POSITIVES`. Empty list `[]` is falsy in Python. Caller passing `[]` to disable FP checks gets the default database loaded instead. Violates None/empty-list contract.
- **Verification:** Python semantics confirmed. `[] or default` evaluates to `default`.
- **Fix:** `fp_db = _KNOWN_FALSE_POSITIVES if false_positive_db is None else false_positive_db`

### MF-16: Vacuous Truth (Phantom Duplicates)
- **Sources:** C4-NK-B
- **Status:** UNFIXED
- **Priority:** P2
- **Description:** If `tau_sim=0.0` and `prior_findings=[]`, `best_sim` initialises to 0.0, `best_match` stays None. Condition `0.0 >= 0.0` is True. Finding flagged as "duplicate of None."
- **Verification:** Logic confirmed. Vacuous truth creates phantom duplicates.
- **Fix:** Guard: `if best_match is not None and best_sim >= tau_sim:`

### MF-17: Toothless Anomaly Detection
- **Sources:** C1-F17
- **Status:** UNFIXED
- **Priority:** P2
- **Description:** Anomaly detection appends UNCERTAIN verdict with 0.4 confidence. UNCERTAIN contributes zero weight in `helper_t_cell_synthesize`. Detection does nothing to the final outcome.
- **Verification:** Code inspection confirmed. UNCERTAIN weight = 0 at line 1069.
- **Fix:** Either make anomaly detection produce a weighted verdict (e.g. LOW_CONFIDENCE with 0.3 reject weight) or remove dead detection code.

### MF-18: Multiline Regex in FP Database
- **Sources:** C1-F18
- **Status:** UNFIXED
- **Priority:** P3
- **Description:** `_KNOWN_FALSE_POSITIVES` patterns lack `re.DOTALL`. Patterns with `.*` don't match across newlines. LLM outputs frequently contain line breaks.
- **Verification:** Code inspection confirmed. Lines 928, 933: no `re.DOTALL`.
- **Fix:** Add `re.DOTALL` to all FP patterns.

### MF-19: O(N×M) Scaling Bottleneck
- **Sources:** C1-F19
- **Status:** UNFIXED
- **Priority:** P3
- **Description:** Deduplication compares every new finding against every prior finding. At 10,000 prior findings and 50 new findings = 500,000 synchronous similarity comparisons.
- **Verification:** Code inspection confirmed. Nested loop with no early termination or indexing.
- **Fix:** Add similarity index (e.g. locality-sensitive hashing) or cap comparison set to most recent N priors.

### MF-20: Race Condition on Shared State
- **Sources:** C1-F1
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** NK cell and B cell run in parallel via `ThreadPoolExecutor`. Both receive the same `triaged` list. NK cell mutates `tf.is_duplicate = True`. B cell reads `tf.is_duplicate` to skip duplicates. Non-deterministic behaviour depending on thread scheduling.
- **Verification:** Code inspection confirmed. Lines 1208–1223: same `triaged` reference shared between threads. No locks, no copies.
- **Fix:** Deep-copy triaged list for each cell, or use thread-safe flags, or serialize NK before B cell.

### MF-21: Intra-Round Duplicate Blindness
- **Sources:** C3 (state mutation leak context), NK v2 shadow data
- **Status:** V2 FIXED (NK v2 caught 9 intra-round duplicates in Run 11)
- **Priority:** P1
- **Description:** NK v1 only compares against `prior_findings` (previous rounds). Duplicates within the same round are invisible.
- **Verification:** Run 11 shadow data: NK v2 caught 9 intra-round dups that v1 missed, inflating R0 count from ~35 to 44.
- **Fix:** NK v2 includes intra-round comparison. Activate v2.

---

## B CELL — Verification Engine (12 findings)

### MF-22: Silent Error Swallowing
- **Sources:** C4-BC1
- **Status:** V2 PARTIAL (stderr captured but not checked)
- **Priority:** P0
- **Description:** `_run_tool_subprocess` uses `subprocess.run` with `capture_output=True` but omits `check=True`. Returns only `stdout`. If generated Python crashes, traceback goes to stderr, function returns empty string, pipeline defaults to UNCERTAIN. Completely blind to internal crashes.
- **Verification:** Code inspection confirmed. Line 636–639: no `check=True`, stderr ignored.
- **Fix:** Add `check=True` or inspect return code. Log stderr. Return explicit error verdict instead of empty string.

### MF-23: Proof by n=100 Fallacy
- **Sources:** C4-BC2
- **Status:** UNFIXED
- **Priority:** P0
- **Description:** If symbolic simplification fails, `_verify_sympy` substitutes n=100 for "numerical truth." Tests a universal quantifier (∀n) with a single scalar. sin(100)≈−0.506 → system confirms "sin(n) is always negative." n²>5000 at n=100 → True, ignoring failure at n∈[0,70].
- **Verification:** SymPy confirmed. sin(100)<0 but sin(π/4)>0. Single-point cannot prove universal.
- **Fix:** Test multiple values (e.g. n=0, 1, 10, 100, 1000) and require all to agree. Or flag as UNCERTAIN when symbolic proof fails instead of falling back to numerical spot-check.

### MF-24: Substring Injection (VERIFIED_TRUE)
- **Sources:** C4-BC3
- **Status:** UNFIXED
- **Priority:** P0
- **Description:** Wrapper checks `if "VERIFIED_TRUE" in output`. If a claim contains the literal text "VERIFIED_TRUE", SymPy treats it as a symbolic variable, subprocess prints "SIMPLIFIED: VERIFIED_TRUE", wrapper falsely returns CONFIRMED.
- **Verification:** String matching confirmed. Substring check has no context guard.
- **Fix:** Use exact line matching (`output.strip() == "VERIFIED_TRUE"`) or structured output format (JSON) instead of substring search.

### MF-25: Tautological If-Then Z3 Logic
- **Sources:** C4-BC4
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** Z3 verifier extracts "if-then" conditions via regex but creates unconstrained boolean variables X, Y. Checks satisfiability of `X ∧ ¬Y`. This is always satisfiable (X=True, Y=False). Every if-then claim is unconditionally REJECTED.
- **Verification:** Logic confirmed. Unconstrained booleans → always satisfiable → always rejected.
- **Fix:** Parse the actual condition and consequent from the claim and encode them as Z3 constraints, not independent variables.

### MF-26: Scientific Notation Blindness
- **Sources:** C4-BC5
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** Numeric fallback regex `r'[-+]?\d*\.?\d+'` splits scientific notation. "p=1e-5≥0" extracts [1, -5, 0]. Checks 1.0≥−5.0 (True), destroying exponential meaning.
- **Verification:** Regex testing confirmed. `1e-5` split into `1` and `-5`.
- **Fix:** Add scientific notation pattern: `r'[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?'`

### MF-27: Z3 Requires 2+ Numbers
- **Sources:** C1-F4
- **Status:** V2 PARTIAL (v2 shadow uses AST-grounded SMT-LIB)
- **Priority:** P2
- **Description:** Z3 fallback requires `len(nums) >= 2`. Claims with one number ("x≥5") fall through to Z3_UNSTRUCTURED → UNCERTAIN.
- **Verification:** Code inspection confirmed. Lines 730–752: `if len(nums) >= 2` guard.
- **Fix:** V2 shadow uses structural encoding. Activate v2. Additionally, handle single-number claims in v1 fallback.

### MF-28: Regex Empty String Match (Z3)
- **Sources:** C1-F2
- **Status:** V2 PARTIAL (v2 avoids the regex entirely)
- **Priority:** P2
- **Description:** Z3 number extraction regex can match empty strings (both `\d*` and `\.?` are optional). Causes ValueError on float conversion.
- **Verification:** Code inspection confirmed. Pattern `r'[-+]?\d*\.?\d+'` can match empty-ish strings.
- **Fix:** Use `r'[-+]?(?:\d+\.?\d*|\.\d+)'` to require at least one digit. Or activate v2.

### MF-29: Dropped Correlations
- **Sources:** C4-BC6
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** Three independent failures: (a) subprocess prints "STRONG_CORRELATION" but wrapper checks for "SIGNIFICANT" — all correlations silently dropped; (b) r-value regex can't match r=1.0 (requires decimal after optional zero); (c) alpha boundary uses strict `<` so p=0.05 exactly is rejected.
- **Verification:** String matching, regex testing, and arithmetic all confirmed.
- **Fix:** (a) Check for "STRONG_CORRELATION" as well as "SIGNIFICANT". (b) Update regex to match integers: `r'r\s*=\s*([-+]?\d+\.?\d*)'`. (c) Use `<=` not `<` for alpha comparison.

### MF-30: SymPy Substitution Wrong Variable
- **Sources:** C1-F7
- **Status:** UNFIXED
- **Priority:** P2
- **Description:** `local_dict` only defines `n` as a symbol. Claims using `x`, `k`, `m` etc. fail with undefined variable error, caught silently → UNCERTAIN.
- **Verification:** Code inspection confirmed. Line 655: only `'n': symbols('n')` in local_dict.
- **Fix:** Add common mathematical variables to local_dict: `x, y, z, k, m, t, a, b, c`.

### MF-31: Statistical Regex Missing Leading Zero
- **Sources:** C1-F6
- **Status:** UNFIXED
- **Priority:** P3
- **Description:** Stat regex requires leading zero: `p\s*[<=]\s*0\.\d`. Standard notation "p<.05" (without leading zero) fails to match.
- **Verification:** Code inspection confirmed. Lines 188–195: requires `0.` prefix.
- **Fix:** Make leading zero optional: `p\s*[<=]\s*0?\.\d`

### MF-32: Hardcoded Stubs / Dead Code (_verify_uncertainty)
- **Sources:** C4-BC7
- **Status:** UNFIXED
- **Priority:** P3
- **Description:** `_verify_uncertainty` unconditionally returns UNCERTAIN regardless of calculation. Never called from `b_cell_verify` (no UNCERTAINTY branch). Function signature requires `metric_value: float` and `metric_std: float` but pipeline only provides strings.
- **Verification:** Code inspection confirmed. Dead function with type mismatch.
- **Fix:** Remove dead function or implement properly and add UNCERTAINTY routing in b_cell_verify.

### MF-33: Class-Switching Contradiction
- **Sources:** C4-BC8
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** When SymPy returns UNCERTAIN, pipeline "class-switches" to Z3. SymPy is a symbolic algebra engine; Z3 (as implemented) is a blind 2-number regex extractor. Falling back from failed symbolic proof to regex number comparison guarantees false positives from coincidental number extraction.
- **Verification:** Architectural analysis confirmed. The fallback degrades verification integrity.
- **Fix:** Z3 fallback should use proper constraint encoding (as in v2 shadow) not regex number extraction. Or flag Z3-fallback confirmations as LOW_CONFIDENCE.

---

## PIPELINE / ORCHESTRATOR (7 findings)

### MF-34: Autoimmune Amnesia
- **Sources:** C1-F21
- **Status:** UNFIXED
- **Priority:** P0
- **Description:** When autoimmune flag triggers, override passes ALL findings through — including DUPLICATE and KNOWN_FP caught by NK cell. The override should only rescue findings rejected by CT/B cells, not findings flagged by innate immunity.
- **Verification:** Code inspection confirmed. Lines 1283–1286: blanket `filtered = [tf.finding for tf in triaged]`.
- **Fix:** Filter override to only rescue non-duplicate, non-known-FP findings: `filtered = [tf.finding for tf in triaged if not tf.is_duplicate and not tf.is_known_fp]`

### MF-35: Autoimmune Inconsistent State
- **Sources:** C1-F5
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** Autoimmune override modifies `filtered_findings` and `rejected_findings` lists but does not update `final_verdicts` or `final_confidences` dictionaries. Returned `ImmuneResponse` has findings in filtered list but verdicts still say REJECTED.
- **Verification:** Code inspection confirmed. Override at lines 1283–1286 doesn't touch verdict dicts computed at line 1257.
- **Fix:** Update `final_verdicts` to UNCERTAIN or AUTOIMMUNE_OVERRIDE for rescued findings.

### MF-36: Fail-Open Illusion
- **Sources:** C1-F22
- **Status:** UNFIXED
- **Priority:** P0
- **Description:** If all verification tools fail (API key expired, SymPy crashes, subprocesses fail), all cells return UNCERTAIN. Helper T passes 100% through. Regulatory T reports "healthy: 0% removal rate." Broken pipeline silently degrades to no-op filter.
- **Verification:** Code inspection confirmed. UNCERTAIN → pass through. Reg T only checks rejection rate, not UNCERTAIN rate.
- **Fix:** Regulatory T must monitor UNCERTAIN rate. If >50% UNCERTAIN, flag "Systemic Tool Failure" instead of reporting healthy.

### MF-37: Batch Timeout Timebomb
- **Sources:** C1-F23
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** Orchestrator timeout = CT timeout + 30s (usually 210s). B cell processes findings sequentially, each with 15s subprocess timeout. With 20 math findings → 300s possible. Orchestrator kills B cell thread at 210s, all verdicts lost.
- **Verification:** Code inspection confirmed. B cell is sequential with no internal parallelism or batch timeout.
- **Fix:** Either parallelize B cell internally, or calculate dynamic timeout: `max(ct_timeout + 30, len(math_findings) * 15 + 30)`.

### MF-38: Fuzzy Match Exploit
- **Sources:** C1-F24
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** CT cell mechanical verification accepts very short snippets. A 1-significant-token snippet matching with ratio 1/1=1.0≥0.6 passes verification at 0.5 confidence. Generic snippets like "value" or "return" match within ±2 lines of any cited location.
- **Verification:** Code inspection confirmed. Token filter (>3 chars) helps but 1-token matches still pass.
- **Fix:** Enforce minimum snippet length or minimum token count: `if len(snippet_tokens) < 3: return False, 0.0, "Snippet too short"`

### MF-39: Typo Bypass
- **Sources:** C1-F25
- **Status:** UNFIXED
- **Priority:** P1
- **Description:** CT cell outputs JSON with `finding_id`. Helper T groups by ID using `dict.get()`. LLM typo in ID → empty verdict list → UNCERTAIN → passes through. LLM can accidentally or systematically bypass rejection.
- **Verification:** Code inspection confirmed. Line 530: `fid = rv.get("finding_id", "")`.
- **Fix:** Pass findings as indexed list ([1], [2]) to CT cell. LLM outputs integer index, Python maps back to real finding_id. Eliminates ID formatting dependency.

### MF-40: Unsafe parse_expr (DoS)
- **Sources:** C1-F9
- **Status:** MITIGATED (15s subprocess timeout)
- **Priority:** P3
- **Description:** Claim text passed to SymPy `parse_expr`. While sandboxed with empty builtins, complex mathematical strings can cause denial of service. Mitigated by 15s subprocess timeout.
- **Verification:** Code inspection confirmed. Line 653: claim → parse_expr. Line 637: 15s timeout.
- **Fix:** Low priority given timeout mitigation. Consider input length/complexity cap for additional defence.

---

## SUMMARY

| Priority | Count | V2 Fixed | Unfixed | Partial/Mitigated |
|----------|-------|----------|---------|-------------------|
| P0       | 7     | 2        | 4       | 1                 |
| P1       | 15    | 4        | 11      | 0                 |
| P2       | 11    | 0        | 9       | 2                 |
| P3       | 7     | 2        | 4       | 1                 |
| **Total**| **40**| **8**    | **28**  | **4**             |

### V2 Activation Impact

Activating v2 shadows immediately addresses 8 findings:
- MF-01 (math hijack), MF-07 (voting asymmetry), MF-08 (dead else block), MF-09 (certainty inversion), MF-10 (micro-total), MF-12 (duplicate handling), MF-14 (continue bypass), MF-21 (intra-round blindness)

### Remaining After V2: 32 findings (28 unfixed + 4 partial/mitigated)

### P0 Unfixed (fix first)
1. **MF-22** Silent error swallowing — pipeline blind to crashes
2. **MF-23** Proof by n=100 — mathematically invalid verification
3. **MF-24** Substring injection — VERIFIED_TRUE bypass
4. **MF-34** Autoimmune amnesia — override releases known FPs
5. **MF-36** Fail-open illusion — broken pipeline reports healthy

### Cross-Reference Notes

- C3 findings (13 total, 5 SymPy-verified) overlap substantially with C1/C4. The 5 proven findings (dead else block, math hijack, NK continue bypass, voting asymmetry, state mutation) are all captured as MF-01, MF-07, MF-08, MF-14, MF-20. Any C3-unique findings not listed here should be cross-checked against C3 logs during fix implementation.
- C4 retracted 12 findings. All retractions reviewed. The NK continue bypass retraction (C4 argued "feature") was overruled by C1 evidence and code verification — the bug is real (MF-14). All other retractions were correct.
- Findings are deduplicated. Where multiple conditions found the same bug, the finding with the deepest analysis is cited as primary source and all sources listed.
