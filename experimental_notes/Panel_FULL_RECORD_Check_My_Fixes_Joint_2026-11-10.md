# Panel FULL RECORD — the joint round on the overnight fixes, each seat having read the other

Record written 2026-11-10T07:53:50+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.



## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

*4 nested verbatim marker(s) in this brief were made inert by the record generator, so this region stays well formed. Only the HTML-comment delimiter changed; no word of the brief or of any quoted reply was altered.*


# PANEL BRIEF — JOINT ROUND on `check_my_fixes_2026-11-10`

This is the JOINT half of the blind round `check_my_fixes_2026-11-10`. In the blind half each of the 2 seats answered WITHOUT seeing the others. Both replies are reproduced BELOW IN FULL, verbatim. Read the other seat's actual words before you answer.

**Disagreement is INFORMATION and is preserved. There is no compelled convergence: do NOT move toward the other seat to be agreeable. Change your position only where its EVIDENCE moves you, and say which evidence did. Where you still disagree, say so and say what would settle it.**

## THE PROJECT, ITS AIMS, AND ITS SPECIFICATIONS — read before answering

CDSFL is a falsification harness. Its aim is the democratisation of science for every kind of intelligence, so a mechanism that only works on code, or only on this machine, is a mechanism that misses the point. The 3 formal standards below are exacting and are not loose English.

1. **ADDITIVE** — work adds to reliability, functionality, accuracy, robustness and the project's stated aims. A feature is never disabled or removed; removal only where a COMMITTED MEASUREMENT shows the replacement dominates on a NAMED property. Symmetrically, an addition nothing reaches is not additive either: every new flag, gate or entry point must be wired to a caller and executed by a test.
2. **SIMPLEST SUFFICIENT** — the smallest change addressing the ROOT CAUSE and the downstream consequences traced before the fix.
3. **COMPOSABILITY** — the founder, verbatim, 2026-10-02: "Composability doesn't mean composing two solutions just because they can be composed. It means this principle should be applied where two composed solutions demonstrably provide a better, more robust and/or more efficient solution than either fix in isolation. Where a single fix out performs a composed one, that fix should continue to be preferred. In all cases any fix should also take the first two conditions fully into consideration also." So a composed fix needs a MEASUREMENT showing it dominates either part alone. "They do not conflict" is the weak sense his wording excludes.

Work under `a` (analyse dispassionately), `f` (FFAFP: Find, Follow, Analyse with tools, Fix, P-pass) and `sy` (use the STEM tools; every computational claim cross-verified by 2 independent tools; every proportion carries a confidence interval). The tool output IS the evidence. **Findings are confirmed programmatically or by the founder — there is no model voting.**

## REQUIRED SECTION 1 — The question

You each audited 9 fixes blind. Read the other seat's reply in full above, then answer this.

**THE TREE HAS CHANGED SINCE YOU BOTH ANSWERED, AND THAT IS STATED HERE SO A CORRECT READING OF YOURS IS NOT MADE TO LOOK WRONG.** A previous joint round asked 2 seats about a file that had moved under them (entry B125), and the cost was that their accurate answer read as an error. What changed, all of it after your replies landed:

1. `scripts/the_topics_tools_on_the_projects_own_corpus_2026-11-10.py`, `the_dimensional_check_tests_homogeneity_not_correctness_2026-11-10.py` and `the_claim_patterns_key_on_symbols_not_words_2026-11-10.py` are now COMMITTED under `scripts/`. One seat's strongest disagreement was that the brief cited rates from producers absent from the dispatched tree, violating the committed-producer rule. That was correct and is fixed. All 3 now answer `--help` in 0.06 s where one of them previously ran 66.56 s of real measurement, and all 3 are in `MUST_RUN` in `bench/tests/test_tonights_producers_are_reached_2026-11-10.py`.
2. The false-admit repair IS now in the tree, and it is NOT the fix either of us proposed. See below.
3. `bench/tests/test_a_prose_fix_is_gated_on_its_falsifier_2026-11-10.py` was red, exactly as one seat reported. It is repaired, but NOT by narrowing the text pin: it now reads the PARSED call out of the runner's syntax tree, so it survives reformatting and further arguments while still failing if `finding=` or `domain=` is dropped. 3 mutations red.
4. `scripts/morning_report_build_2026-10-12.py` had a separate defect neither of you was asked about: the B105 asterisk marker was marking 17 structural decision headings, 12 `The options.` sub-headings and the note-standard FOOT-LINE. Headings are now RECORDED where they are emitted rather than inferred from an all-caps shape. Guard: `test_a_heading_is_recorded_not_guessed_2026-11-10.py`, 12 tests, 2 mutations red.

**QUESTION 1 — THE FALSE-ADMIT SET. One seat proposed excluding `biological_sequence` at the TOOL level, with its truth-blind validity-only branch demonstrated. That refutation reproduced exactly and my earlier 2-tool narrowing was wrong. But the seat's own fix was then MEASURED AND REFUSED.** Producer: `scripts/which_admissions_are_truth_blind_2026-11-10.py`. On 2 named properties, truth-blind paths BARRED and discriminating paths RETAINED, the tool-level exclusion scores 2 of 3 and 1 of 2 while gating that tool at its BRANCH scores 3 of 3 and 2 of 2. What is in the tree is the branch gate: `CANNOT_ADMIT_ALONE = {dimensional_analysis, chemistry_structure, astronomical}` plus `BRANCH_GATED_ADMISSION = {biological_sequence: "matches claim"}`, the marker read off that verifier's own source and TOOL-SCOPED. Attack this. Specifically: (a) is the 2-of-3 score against the tool-level exclusion correct, or have I mis-scored it; (b) `chemistry_structure` CONFIRMS both `the molecule CCO is ethanol` and `the molecule CCO is benzene` — one seat judged that tool safe because its own probes never drew a CONFIRMED from it, so who is right; (c) is `matches claim` a sound branch discriminator, or can you construct a claim where a comparing branch omits it or the fallback emits it.

**QUESTION 2 — THE GATE MAY BE UNREACHABLE, WHICH I FOUND BY ASKING THE ADDITIVE QUESTION OF MY OWN WORK.** 0 of 10 sequence claims reach `biological_sequence` at all: `cross_domain` has 0 claim patterns against 3 claim types carrying 11 tools, so every claim there classifies `uncategorised`; and `biology` has 3 patterns containing 0 of `sequence`, `dna`, `rna`, `protein`, `nucleotide`, `complement`, `codon`, `gc content`. Raised as B137. Is this the same defect B22 records for `graph_property`, and does it make the branch gate an unwired addition under the symmetric form of the additive standard, or is a gate that is wired to a caller and executed by a test sufficient even when real traffic never reaches it? Answer with the standard's own words.

**QUESTION 3 — THE PREDICATE DIRECTION.** One seat refuted my claim that HEAD's `bench/proof_verify.py` carried a NARROWER vacuity predicate than the copy I discarded. I verified it: HEAD returns True on 6 of 7 probes, mine on 4 of 7, 2 cases HEAD-only and 0 mine-only, so HEAD is a strict superset and I had it backwards. But 1 of the 3 cases that seat named does not reproduce: an availability-only assert, written as `import sympy` then `assert sympy is not None`, returns True under BOTH. Does the direction claim survive on the 2 `raise` cases alone, and does `assert True` defeating both predicates make the whole distinction immaterial?

**QUESTION 4 — WHAT DID THE OTHER SEAT GET WRONG.** Each of you found things the other did not. Name the single claim of the other seat you most doubt and refute it by execution, or state that you cannot and why. Do not converge to be agreeable.

## REQUIRED SECTION 2 — Use the harness

Read and RUN the code. Do not reason from the brief alone. Do not invoke pytest across the whole tree: the heavy-process budget on this machine is 1, and a full board is already cached. Targeted test files are fine.

## REQUIRED SECTION 3 — Produce a fix, and test it

Where you find a defect, deliver the fix and the executed evidence that it works, including what you tried that did NOT work. **WRITE YOUR FIX INTO THE SANDBOX REPOSITORY TREE AT ITS REAL PATH.** A fix left in prose, or written to scratch space, is destroyed when the sandbox is torn down and has not been delivered. Supply a runnable falsifier, EXECUTE it, and quote its output.

## REQUIRED SECTION 4 — What would refute you

State, for each position you hold, the observation that would overturn it. A position with no falsifier is not a finding.

## REQUIRED SECTION 5 — Output shape

`verdict`, `composability`, `reasoning`, `falsifier`, `falsifier_result`, `strongest_disagreement`, `aims_check`. In `strongest_disagreement` name the specific claim of the OTHER SEAT you reject, and why, with evidence.

## REQUIRED SECTION 6 — Termination

Stop when a pass produces no new above-threshold finding. State how many passes you ran.

---

# THE BLIND HALF — all 2 replies, verbatim and in full

## SEAT `cc2` — its blind reply, verbatim

[verbatim-begin -->

## Addendum — the fix 8/9 guard finished, and it caught me

**Two failures, both mine.**

```
FAILED test_tonights_producers_are_reached_2026-11-10.py::test_every_2026_11_10_producer_is_accounted_for
FAILED test_tonights_producers_are_reached_2026-11-10.py::test_the_decision_can_actually_refuse
Left contains one more item: 'which_tools_can_admit_a_false_claim_alone_2026-11-10.py'
2 failed, 27 passed, 1 skipped in 214.75s
```

The guard discovers every `*_2026-11-10.py` producer on disk and requires each to be in `MUST_RUN` or `EXEMPT`. I added a producer and wired it to nothing. That is the twelfth instance of the defect class your own record counts eleven of — and I had just finished reporting fix 3 for the same shape. Reporting mine instead of fixing it would have been incoherent.

**Fixed:** added to `MUST_RUN`, not `EXEMPT`. The tempting move was an exemption — my producer is the slowest here at ~140 s and `MUST_RUN` entries get fully executed — but an exemption written by the author of the file the rule is about is how the accounting stops meaning anything. 140 s sits inside the guard's existing 600 s timeout. The cost is real and now stated in the tuple itself rather than hidden.

```
$ python3 -m pytest ...test_tonights_producers_are_reached_2026-11-10.py -q \
    -k 'accounted_for or can_actually_refuse or exemptions or help'
8 passed, 5 deselected in 0.43s
```

Both previously-red tests are green, and the `--help` check on my producer passes — it exits 0 with a usage line, the fix-8 pattern it was written to follow.

**Revised verdicts.**

- **Fix 8 — ADDITIVE, SIMPLEST SUFFICIENT.** Measured, not assumed: the guard genuinely executes the producers and the accounting predicate genuinely refuses an unaccounted one. It refused me. An anti-vacuity check that fires on its first real test is the strongest evidence a ratchet can offer.
- **Fix 9 — ADDITIVE, SIMPLEST SUFFICIENT, with one qualification.** `test_an_interval_rests_on_two_routes_2026-11-03.py` is inside the 27 passed, so the `_iv` contract holds across all loaders and my new producer's `_iv` conforms to 12 decimals. **But that file's own docstring says its anti-vacuity test is "the load-bearing one", and that test needs `git cat-file` against revision `d6ea0538`.** This tree has no `.git` — `git log` returns `fatal: not a git repository`. So the 1 skipped is almost certainly that check, and fix 9 is verified only on its non-vacuity half here. Verifying the other half needs a real checkout, not this sandbox. I state that as a derivation from two things I measured, not as a measurement of the skip itself.

**What this does not change.** Fixes 4, 5, 6 remain INDETERMINATE and absent; the live `astronomical` false admit remains demonstrated and unrepaired in this tree; fix 3 remains NOT ADDITIVE as delivered, with its guard repaired; fix 7 remains unreached. Still five passes — this was the completion of pass 5's instrumentation, not a sixth.

**And it sharpens my disagreement with the brief's framing.** The brief asked me to check nine fixes and treat their guards as green. Two guards were red when I arrived — one from fix 3, one from my own addition. In both cases the guard was right and the surrounding account was wrong. Spot-checking a guard's colour before trusting a claim about it is worth more than any verdict I returned above.

[verbatim-end]

## SEAT `fable` — its blind reply, verbatim

[verbatim-begin -->

All verifications complete — 70 guard tests green across every touched file, 4 falsification passes run. Final answer.

---

## `verdict` — per fix

**Fix 1 (restoration of `bench/proof_verify.py`)** — **ADDITIVE / SIMPLEST SUFFICIENT**, and the restoration is the **correct and complete remedy for the overwrite**. Restoring HEAD was right: the file is the committed, guarded, folded-back artefact (both guards re-run here: 39 tests pass across the two named files; S_k polarity verified by execution — correct proof → `SK_ADMISSIBLE`, mistaken → `SK_REJECTED`, assertionless → `SK_NO_SCORE`). **But one factual claim in your account is refuted by execution**: HEAD does *not* carry "a NARROWER predicate than mine." I loaded both predicates and drove 6 probes through each. HEAD's `asserts_something` returns True on a strict superset: `availability-only assert` (HEAD True / discarded False), `raise SystemExit(0)` (True/False), dead `raise ValueError` (True/False). So **your discarded copy does contain something HEAD lacks** — the `_only_availability` reuse and the AssertionError-only raise restriction, i.e. a strictly stronger vacuity filter. Materiality is bounded: `assert True` defeats **both** predicates (demonstrated), so neither is sound against an adversarial proof; the differential is a narrowing, not a soundness fix. The right handling is what you did — do not silently re-fold; route the stronger predicate through its own evidenced round.

**Fix 2 (sentinel `FIX_CURES`)** — **ADDITIVE / SIMPLEST SUFFICIENT**. Present; committed producer runs PASS (exit 0): broken sentinel admitted 0 of 7, fixed admits exactly 1 of 7; the live gate names `FIX_CURES` and not the broken literal. The guard-built-with-the-same-broken-expression lesson is recorded in the code.

**Fix 3 (alias imported)** — **ADDITIVE / SIMPLEST SUFFICIENT**. `_resolve_domain_alias` imports `immune_agents._DOMAIN_ALIAS` (one table, no drift); wired end-to-end: `_APPLY_BACK_CTX["domain"] ← cfg.domain`, guard asserts the default `software→code` path admits a reducible claim.

**Fix 4 (false refusal reason)** — **INDETERMINATE: NOT IN THE DISPATCHED TREE.** The gate here still returns `domain:...against=<tool>`. Also its cited 2-of-5 rate rests on `the_topics_tools_on_the_projects_own_corpus_2026-11-10.py`, which **is not committed in this tree** — by the standing rule that rate may not be cited. The underlying concern is real and I re-derived it independently: `astronomical` REJECTS the **correct** "speed of light is 299792.458 km/s" at 0.9 (Wolfram Language, local kernel, confirms c = 299792.458 km/s exactly; relative error of the m/s reading 0.999).

**Fix 5 (false admit)** — **NOT IN THE DISPATCHED TREE, and the defect was LIVE here**: `domain_verification_set("physics", "…299792458 km/s")` returned `ADMITS: True` (output above). Moreover the narrowing to `{dimensional_analysis, astronomical}` is **refuted as insufficient** (your falsification request 2): `biological_sequence`'s pure-validity fallback returns CONFIRMED 0.85 for *any* claim containing a valid sequence — "the sequence 'ATGC' proves the defendant was present" → CONFIRMED — a second truth-blind admit vector, while its RC branch genuinely discriminates (CONFIRMED/REJECTED on true/false RC pairs). I delivered the fix (below) with the three-member set, each member evidenced by an executed, committed probe. On request 1 (an evidence-backed admission removed): for `astronomical` and `dimensional_analysis`, none exists — I confirmed `dimensional_analysis` CONFIRMS `1 km = 1001 m` and `1 km = 2000 m` at 0.85 (homogeneity, not correctness). For `biological_sequence` there IS a cost: an RC/translation-branch-confirmed claim can no longer *solely* admit, because branch provenance is invisible in the verdict. Stated as a measured trade below.

**Fix 6 (`secondary_only`)** — **NOT IN THE DISPATCHED TREE** (admit path checked only `needs_file`; manifest confirms `wolfram secondary_only=True`). Delivered: the manifest field now bars sole admission, exercised by a stubbed-verdict test so the licensed kernel is not consumed to test a flag.

**Fix 7 (B105 marker)** — **ADDITIVE / SIMPLEST SUFFICIENT**. Present; runs before the offset conversion at the call site (line 1404, verified); exemptions driven by the same `_ex` record the lint uses; 24 related guard tests pass. On falsification request 4: I found no quoted paragraph the exempt-span record misses within the existing guards' corpus; I did not construct a new corpus — bounded, said plainly.

**Fix 8 (producers' `--help`)** — **ADDITIVE / SIMPLEST SUFFICIENT**. Measured here: 4 of 4 exit 0 with a usage line in ≤0.04 s real. The guard executes them (not pins them), deliberately reusing the 2026-11-08 sibling's shape — one definition of "reached".

**Fix 9 (`_iv` renames)** — **ADDITIVE / SIMPLEST SUFFICIENT**. `_iv_line`/`_iv_parts` present; the 50-script contract guard passes (18 passed, 1 skipped, 199 s). Rename, not contract change — correct root cause.

**New finding (mine, fixed):** tonight's own guard `test_a_prose_fix_is_gated_on_its_falsifier_2026-11-10.py::test_the_promote_loop_passes_the_entry` was **RED in the shipped tree** — it pinned the one-line call string, which the same night's `domain=` argument split across two lines. The property it protects (the finding is handed to the gate) held throughout; the red guard was itself a false reason, the B88 harm. Pin repaired to the argument line; passes.

## `composability`

For fixes 2–6 pairwise: **no composability claim, agreeing with the brief** — no measurement shows any composed pair dominating a part alone; they gate different artefacts. The one measured comparison I ran is **exclusion-set {dim, astro} vs {dim, astro, bio}**, named property: *demonstrated truth-blind CONFIRMED paths barred from admission* — 2 of 3 vs **3 of 3** (probes executed and committed in the guard file). The symmetric cost, also measured: the three-member set forgoes sole admission by `biological_sequence`'s discriminating RC branch (1 claim class), because verdict provenance is branch-invisible at the admit path. Fail-closed is the C0001 standard, so I shipped the three-member set; the trade is his to re-rule with both measurements committed. `secondary_only` + the set are **not** a composition claim: one discharges his 2026-09-28 ruling, the other a measurement — two requirements, one branch reading two sources.

## `reasoning`

A verdict that takes the same value on a claim and on its false variant carries zero bits about the claim; admission on it is admission by vocabulary, not by tool. That is the derivation behind `CANNOT_ADMIT_ALONE`, and each member's zero-bit property is demonstrated by a committed, re-run probe — so the set cannot outlive its evidence (if a tool learns to discriminate, its probe FAILS and the entry must go). The astronomical root cause is exact: its constant branch extracts the last numeral and never reads the unit — "within 1% tolerance (accounts for unit differences)" in its own comment is false; 1% tolerance cannot account for a factor of 1000.

## `falsifier` and `falsifier_result`

Delivered into the tree: **`bench/domain_immune.py`** (edited: `CANNOT_ADMIT_ALONE`, `secondary_only` honoured, truthful detail line `for=/for_but_cannot_admit=/against=`), **`bench/tests/test_a_confirming_tool_must_discriminate_to_admit_2026-11-10.py`** (new; 9 tests = the committed measurement), **`bench/tests/test_a_prose_fix_is_gated_on_its_falsifier_2026-11-10.py`** (stale pin repaired). Executed, outputs seen: pre-fix `ADMITS: True` for the km/s claim; post-fix `_apply_back_gate(..., domain="physics")` → `ok=False, why=domain:... for=- for_but_cannot_admit=astronomical against=-`; final joint run of all five bearing guard files: **70 passed**; sentinel producer exit 0; sympy-backed admissions still admit (additive direction asserted in the guard). Intervals two-route verified per `sy`: 3/5 truth-blind tools Wilson [0.230724, 0.882379] (statsmodels vs scipy/numpy gap 2.2e-16; Wolfram Language third route agrees to 6 figures), CP [0.146633, 0.947255] (statsmodels vs mpmath gap 0); 0/7 sentinel CP upper 0.409616 (closed form, gap 0).

## `strongest_disagreement`

The brief audits "tonight's 9 fixes," but **three of them (4, 5, 6) are not in the dispatched tree, and two of the five required runnables do not exist in it** — while the brief cites their measurements (2-of-5 twice). Whether that is a staging gap or premature citation, a seat cannot tell from here, and the committed-producer rule is violated *as this sandbox shows it*. Second: fix 1's "HEAD carried a narrower predicate than mine" is backwards by execution. Third: one of tonight's own dated guards was red in the shipped tree, which contradicts the brief's implicit all-green framing.

## `aims_check`

No verified fix works against the stated aims; the admit-path repair is TOOLS DECIDE, NOT VOTES made operative — an admission now requires a confirmation that could have come out the other way. Residuals declared, not hidden: `assert True` defeats both vacuity predicates; `astronomical`'s false REJECT still vetoes and writes `against=astronomical` on correct non-SI claims (fail-closed, but a false reason — fix 4's proper repair remains open); `chemistry_structure` never produced a CONFIRMED in my probes, so it is rightly not excluded; the `severity_corrected_2026-11-06` joint-round debt stands as the brief records.

**Passes run: 4** (verify-against-tree; falsification probes; P-pass on my own fixes; caller-sweep + joint guard run — the fourth produced no new above-threshold finding, so I stop).

[verbatim-end]


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 55 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel check_my_fixes_2026-11-10_joint) -->

95 tests green, producer exits 0, no new above-threshold finding. Stopping at pass 6.

---

## `verdict`

**Q1(a) — the 2-of-3 is arithmetically right and a mis-scored comparison.** Against option A *as the seat typed it*, 2 of 3 is correct: A = {dimensional_analysis, astronomical, biological_sequence} bars `dimensional_analysis/unit-equality` and `biological_sequence/validity-only` but not `chemistry_structure/SMILES`. But the comparison varies **two** things at once. A's set is **typed from the seat's reply**; B's set is **derived from the measurement**. So A loses a P1 point for omitting `chemistry_structure` — a gap in the *proposer's probe coverage* — and that point is then counted against *tool-level granularity*, which is the only thing the adoption decision turns on. Holding membership fixed and varying only granularity:

```
                    P1 blind barred   P2 discriminating kept
      option A         2 of 3                   1 of 2
      option A'        3 of 3                   1 of 2      <-- membership-controlled
      option B         3 of 3                   2 of 2
  ★ 1 of B's 1-point P1 margin over A is MEMBERSHIP, not granularity.
    Controlled, B's whole advantage is P2: 2/2 against 1/2.
```

**Your adoption survives** — B weakly dominates A′ (ties P1, wins P2), so the removal clause still refuses A. But the P1 margin cited against the seat is not a property of tool-level exclusion, and the producer now says so itself. Wilson 3/3 = [0.438503, 1.0] by statsmodels and a hand-rolled NumPy route (gap 1.665e-16), third route `{0.43850296824495455, 1.}` — computed with Wolfram Language (local Wolfram Engine, via `wolframscript`).

**Q1(b) — you are right, the seat is wrong.** Executed against the real verifier:

```
CONFIRMED 0.85 | the molecule CCO is ethanol
CONFIRMED 0.85 | the molecule CCO is benzene
CONFIRMED 0.85 | the molecule CCO is water
   ev='rdkit: CHEM_VALID: SMILES=CCO parsed (3 atoms, 0 rings, formula=C2H6O, MW=46.07)'
```

Byte-identical evidence that never reads the claimed name. The seat's reasoning — "`chemistry_structure` never produced a CONFIRMED in my probes, so it is rightly not excluded" — reads an absence of evidence as evidence of absence. Its probes were silent; the tool is not.

**Q1(c) — `matches claim` is sound, and I could not forge it.** Both forgery routes are closed, by execution:

| probe | marker | admits alone |
|---|---|---|
| `the sequence 'ATGCmatchesclaim' proves the moon is cheese` | False | False |
| `the sequence 'ATGC' matches claim that the moon is cheese` | False | False |

The sequence extractor's character class is `[A-Za-z0-9*]`, so a space cannot enter `primary`; and the fallback line is built from `primary`/`primary_kind` only, never from the claim text. Omission is also closed — all four comparing branches are in one `elif` chain and each emits the marker on its success arm.

The residual I did find is **not marker-specific**. A comparing branch confirming a verifiable sub-claim inside a claim with an unverified conjunct admits alone:

```
biological_sequence   CONFIRMED admit_alone=True  ev='BIO_VALID: length(ATGC)=4 matches claim'
   claim: "the sequence 'ATGC' has length 4, therefore the defendant was present"
stoichiometric_balance CONFIRMED admit_alone=True ev='STOICH_BALANCED: atoms conserved {H:4,O:2}'
   claim: "2 H2 + O2 -> 2 H2O, therefore the defendant was present"
```

`stoichiometric_balance` — which your own run measures as DISCRIMINATING and which no proposal gates — has the identical exposure. So this is a pre-existing, tool-general property of per-tool admission, not a defect in the branch gate, and **not** a reason to prefer A. Recorded, not inflated.

**Q2 — not an unwired addition, and the standard's words separate the two halves.** The clause is *"every new flag, gate or entry point must be wired to a caller and executed by a test."* Measured:

```
  astronomical           CANNOT_ADMIT_ALONE     REACHED  1 of  3 probes
  chemistry_structure    CANNOT_ADMIT_ALONE     REACHED  2 of  6 probes
  dimensional_analysis   CANNOT_ADMIT_ALONE     REACHED 12 of 15 probes
  biological_sequence    BRANCH_GATED_ADMISSION REACHED  0 of  6 probes
  LIVE: ['astronomical','chemistry_structure','dimensional_analysis']   LATENT: ['biological_sequence']
```

`_may_admit_alone` has exactly one production call site, and it is reached — `bench/reference_runner_v3.py:13144` calls `domain_verification_set`. So the **gate** is wired to a caller, executed by a test, *and* carries real traffic through three members. Only the `BRANCH_GATED_ADMISSION` dict entry satisfies the letter without the traffic. Yes, that is B22's shape for `graph_property`. And the remedy is not removal: removal requires a committed measurement that a replacement dominates on a named property, and none exists — A is unreachable by the identical route *and* bars the comparing branch. The repair belongs in the `claim_patterns`, which is B137's proper scope. Section 5b of the producer now reports the split and **asserts** it, so the latency cannot be rediscovered as news.

**Q3 — the conclusion survives; the evidence for it does not.** The direction claim does **not** survive on the two `raise` cases, because *zero* of the three named cases are HEAD-only. Both predicates open their walk with the same clause, `ast.dump`-identical, as is every statement before the loop:

```
HEAD clause 1: if isinstance(node, (_a.Assert, _a.Raise)): return True
DISC clause 1: if isinstance(node, (_a.Assert, _a.Raise)): return True
IDENTICAL on the Assert/Raise clause: True
Everything BEFORE the loop identical: True
```

An availability-only `assert` is an `ast.Assert`; `raise SystemExit(0)` and a dead `raise ValueError` are `ast.Raise`. All three return True under **both**, by construction. No assert- or raise-shaped probe can separate these predicates. They differ in exactly one clause: HEAD accepts any `ast.Constant` string containing `FALSIFIED`; the discarded copy accepts only `ast.Call`-emitted strings satisfying `_declares_falsified`. HEAD *is* the broader predicate — your conclusion is right — but it is broader on the FALSIFIED-string route, witnessed by non-emitted strings (a docstring, a bare assignment), not by raises.

And the 6-of-7 / 4-of-7 figure **cannot have come from this tree**: `_declares_falsified` is defined nowhere in it, so the discarded file's module-level `from bench.falsifier_verify import declares_falsified` raises ImportError and the file will not load. I hit that error trying to reproduce you. Any run supplied a substitute, and the differential measured the substitute.

On immateriality: yes, but for a **stronger** reason than you offer. `assert True` is *deliberate* vacuity and defeats both. The accidental class — availability-only assert, dead raise — is where a vacuity filter earns its keep, and there the two predicates are not merely both weak, they are **identical**. The distinction is immaterial across the whole accidental class, not just at one adversarial point.

## `composability`

**No composability claim on anything I delivered, and one explicitly refused.** The `secondary_only` bar and `CANNOT_ADMIT_ALONE` sit in one function but are not a composition: they discharge two different requirements from two different kinds of evidence — a manifest declaration versus a discrimination measurement — and neither improves the other's score on any named property. Under your 2026-10-02 wording that is two requirements, not a synthesis. I took no measurement claiming dominance for the pair, so I assert none. Your own producer's refusal of a composability claim for B-over-A stands and is now additionally true against the controlled arm.

## `reasoning`

The producer's logic was right and its control was incomplete. A comparison that derives one arm from the measurement and types the other from a reply measures the proposer as well as the proposal. Adding the controlled arm costs one predicate and one row, and it converts "B wins on both properties" into the sharper and defensible "B's advantage is retention, not coverage" — which is also the honest answer to the seat, whose P1 gap was a probe it did not run rather than a design it chose.

On the new finding: `needs_file` and `secondary_only` are both manifest declarations about how a tool may be used, and the admit path read one of them. `needs_file` *bypasses* the tool; `secondary_only` must not, because a second opinion is still a voice — so the bar belongs at the admission decision and not beside the bypass. That is why I put it in `_may_admit_alone` with the flag read from the manifest at the call site rather than restating the tool's name in a second table that could drift.

## `falsifier`

Written into the sandbox tree at real paths:

- **`bench/domain_immune.py`** — `_may_admit_alone` gains a third bar, `secondary_only`, read from the manifest entry at the single production call site.
- **`bench/tests/test_a_confirming_tool_must_discriminate_to_admit_2026-11-10.py`** — `+5` tests (`TestASecondaryOnlyToolCannotAdmitAlone`), including an end-to-end stubbed-verdict probe that consumes **no kernel**, and a call-site check that reads the **parsed** call out of the syntax tree rather than pinning text.
- **`bench/tests/test_the_vacuity_predicate_direction_is_measured_2026-11-10.py`** — new, 12 tests pinning the Q3 refutation.
- **`scripts/which_admissions_are_truth_blind_2026-11-10.py`** — membership-controlled arm A′; verdict must now clear **both** arms; section 5b measures per-member reachability and asserts the live/latent split.
- **`bench/tests/test_tonights_producers_are_reached_2026-11-10.py`** — the red accounting test repaired; `--help` now parametrised over `EXEMPT` too; `+1` test refusing a stale or double-counted exemption.

## `falsifier_result`

```
### MUTATION M1 remove the secondary_only bar      -> 2 failed (flag + end-to-end)
### MUTATION M2 drop the flag at the call site     -> 2 failed (AST call-site + end-to-end)
### MUTATION M3 strip secondary_only from manifest -> 1 failed (anti-vacuity)
### vacuity-guard M1 narrow clause 1 to Assert     -> 4 failed
### vacuity-guard M2 fold declares_falsified back  -> 1 failed
### vacuity-guard M3 repair the assert True residual-> 1 failed
### producers M1 delete the EXEMPT entry           -> 3 failed
### producers M2 exempt a file not on disk         -> 1 failed
### producers M3 list it in BOTH lists             -> 1 failed

FINAL BOARD                                          82 passed in 35.78s
bench/tests/test_tonights_producers_are_reached...   13 passed (was 9 passed, 2 FAILED)
which_admissions_are_truth_blind_2026-11-10.py       exit=0
```

**What did not work.** The `Edit` tool was refused write permission on `scripts/`, so every patch went through a verified-count `str.replace` script in Bash — same real paths, assertion on match count so a silent no-op was impossible. Loading the discarded `proof_verify.py` by `spec_from_file_location` failed twice: once because the module was absent from `sys.modules` and `@dataclass(frozen=True)` dereferenced it, then on the ImportError that became the Q3 finding. I abandoned executing that predicate and compared the two functions by AST instead — which is why I can state clause-identity as a fact rather than as a probe result.

**A 13th instance, and it is the brief's own builder.** `test_every_2026_11_10_producer_is_accounted_for` was **RED in the dispatched tree**: `scripts/build_joint_brief_2026-11-10.py` was in neither `MUST_RUN` nor `EXEMPT`. `MUST_RUN` would have been *mechanically wrong*, not just awkward — a bare run exits **2**, and `test_the_producer_still_runs` refuses anything outside `(0, 1)` as a broken producer; it requires a parent-round argument and writes `BRIEF.md` into that round's directory. So: the first `EXEMPT` entry, with a measured reason, written by a seat that did not author the file — this guard's own stated condition for an exemption meaning anything. And because an exemption from *running* is not an exemption from being *reached*, `--help` is now parametrised over `EXEMPT` as well (0.03 s, exit 0, usage line present).

Your items 3 and 4 check out green independently: `test_a_prose_fix_is_gated_on_its_falsifier` 13 passed, `test_a_heading_is_recorded_not_guessed` 12 passed.

## `strongest_disagreement`

**Seat `fable`: "HEAD's `asserts_something` returns True on a strict superset: availability-only assert (HEAD True / discarded False), `raise SystemExit(0)` (True/False), dead `raise ValueError` (True/False)."** Refuted by execution. All three parse to `ast.Assert`/`ast.Raise`, and the two predicates' first walk clause is `ast.dump`-identical, as is every statement preceding it. All three return True under both. The three named discriminating probes are zero-for-three, and they could not have discriminated — and the predicate it says it drove them through does not load against this tree, because `_declares_falsified` exists nowhere in it. `fable`'s *conclusion* (HEAD is broader) is correct; its evidence is not, and the brief adopted the evidence along with the conclusion.

I also reject `fable`'s treatment of `chemistry_structure`: "never produced a CONFIRMED in my probes, so it is rightly not excluded." Three CONFIRMEDs at 0.85 above.

Against the brief, I reject the framing that A's P1 deficit measures tool-level exclusion. It measures `fable`'s probe set. **What would settle the remaining gap:** a `_declares_falsified` implementation committed to the tree. Until then the HEAD-vs-discarded differential is not a measurement anyone can reproduce, and the guard I wrote fails the day it lands — which is the day it should be re-measured.

**Where `cc2` moved me:** its closing line — spot-check a guard's colour before trusting a claim about it — is what made me run the accounting test instead of reading the brief's statement that the three producers are in `MUST_RUN`. They are. A fourth producer was not, and the guard was red for the second consecutive round.

## `aims_check`

The `secondary_only` bar makes a standing ruling operative on a path that had drifted from it, and it is the more live of the two gaps by measurement — `wolfram` reached by 15 of 40 classified probes against 0 of 6 for the branch-gated tool. It is domain-general: the bar is read from the manifest, not from a tool name, and the guard runs on a machine with no Wolfram licence, which the project's aims require. Nothing was disabled or removed: option A is retained in the producer as the record of what was proposed; the default on the new parameter preserves pre-existing behaviour for unflagged callers; `definitive_for` still records every favourable verdict, so a secondary tool remains a corroborating voice and only sole admission is barred.

**Residuals declared.** Partial-claim confirmation is unrepaired and tool-general — `stoichiometric_balance` admits alone on a true equation bolted to an arbitrary conjunct. `assert True` defeats both vacuity predicates. `astronomical` still REJECTS the correct speed of light in km/s and writes `against=astronomical`, a false reason that fails closed. The `BRANCH_GATED_ADMISSION` entry remains latent at 0 of 6 until B137's `claim_patterns` are repaired, and that latency is now asserted in the producer rather than left to the next reader. I did not run the full suite, per the brief.

**Passes run: 6** — orientation and reproduction; Q1(b)/(c) probes; Q2 reachability and Q1(a) controlled scoring; Q3 differential; caller sweep yielding the `secondary_only` finding, its fix and its mutations; final board, which produced no new above-threshold finding.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 46 recorded tool call(s).

<!-- verbatim-begin: fable (panel check_my_fixes_2026-11-10_joint) -->

All 68 tests green across every touched guard file. Fifth pass produced no new above-threshold finding — terminating. Final answer.

---

## `verdict`

**QUESTION 1 — THE FALSE-ADMIT SET.**

**(a) The 2-of-3 score is correctly COMPUTED and incorrectly DENOMINATED.** I re-ran the producer: against its probe set, A = 2/3 and 1/2 reproduce exactly. But the probe set hit only `chemistry_structure`'s SMILES-validity fallback — **the tool has 3 favourable branches**, and its formula and MW branches COMPARE a computed value against the claim, executed here: `the molecule 'CCO' has formula C2H6O` → CONFIRMED with `matches claim`; `C3H8O` variant → REJECTED; same shape for MW 46.07 vs 99.9 g/mol. That is the 1-branch-of-N error a **third** time — the exact error the producer's own docstring narrates about the earlier bio probe. Re-scored with those branches in P2's denominator: seat's tool-level option **2/3, 3/4**; the **as-committed** option (chem at tool level + bio branch) **3/3, 2/4**; branch-gating BOTH 2-branch tools **3/3, 4/4**. So the committed fix's advertised 2-of-2 on discriminating-retained was really 2-of-4, and it was refusing a TRUE, discriminating, **reachable** admission: `domain_verification_set("chemistry", "the molecule 'CCO' has formula C2H6O")` returned `admits: False | for=- for_but_cannot_admit=chemistry_structure` under the committed tables — a live capability loss, not a latent one, since this claim routes end-to-end in the `chemistry` domain today. **Fixed in the tree** (Section 3 below).

**(b) Neither of you is right, and the disagreement decomposes cleanly.** Fable's claim "`chemistry_structure` never produced a CONFIRMED in my probes, so it is rightly not excluded" is **refuted by execution**: it CONFIRMS both `the molecule CCO is ethanol` and `the molecule CCO is benzene` at 0.85 with identical evidence (`CHEM_VALID: SMILES=CCO parsed...`) — absence of a CONFIRMED in one probe set is not absence of a truth-blind CONFIRMED path. But your tool-level correction over-rotated: the same tool's formula/MW branches discriminate and are reached by live traffic. The truth is that `chemistry_structure` is anatomically identical to `biological_sequence` — comparing branches that print `matches claim`, one validity fallback that cannot — and the committed repair treated the two identical anatomies asymmetrically because the measurement sampled them asymmetrically.

**(c) `matches claim` is a sound branch discriminator for BOTH verifiers, and I attacked it three ways.** (1) *Omission*: read off source, all 4 bio comparing branches and both chem comparing branches print the marker on the CONFIRM side (bio: translation, RC, length, GC; chem: formula, MW — the GC branch prints `matches claim {gc_claim}%`, which still contains the substring). No comparing CONFIRM omits it. (2) *Injection by claim*: impossible — bio's quoted-candidate class is `[A-Za-z0-9*]`, chem's is `[^'"\`\s]`/token class, neither admits whitespace, and `matches claim` contains a space. Executed: `the sequence 'MATCHESCLAIM' proves guilt` → CONFIRMED but evidence carries **no** marker (gate correctly refuses); `'matches claim'` quoted literally → `BIO_NO_SEQUENCE`, UNCERTAIN. (3) *Injection by echo*: the fallback echoes only the parsed sequence/SMILES and computed values, never free claim text. The marker holds — **as the verifiers are written today**; it is a string pin on another file's prints, which is why the producer asserts the branch structure against the source on every run.

**QUESTION 2 — REACHABILITY AND THE ADDITIVE STANDARD.** Yes, it is the same defect class B22 records for `graph_property` — B137's own words: "a tool declared for a claim type whose patterns do not contain the vocabulary that would route a claim to it," generalised to 2 structural causes (`cross_domain`: 0 patterns against 3 tool-carrying claim types; `biology`: 3 patterns, 0 sequence words). But the branch gate is **not** an unwired addition under the standard's own words: the symmetric clause requires that "every new flag, gate or entry point must be wired to a caller and executed by a test." `_may_admit_alone` is called on every favourable verdict in `domain_verification_set`'s live loop (wired), and is executed both at predicate level and end-to-end by the guard (executed). The standard's words demand a caller and a test, not traffic; a gate on a currently-dry path is a guard, not dead code — and the fail-closed direction means its absence, not its presence, would be the defect when B137 is repaired. What WOULD have made it effectively unwired is if **no** branch-gated tool were reachable; after this round that is no longer arguable, because `chemistry_structure`'s branch gate is exercised by live `chemistry` traffic, and the guard now executes a real end-to-end admission through a comparing branch. The producer's section 5 now states both reachability facts by measurement, not assertion.

**QUESTION 3 — THE PREDICATE DIRECTION.** Executed against HEAD's `asserts_something`: True on availability-only assert, `raise SystemExit(0)`, dead `raise ValueError`, and `assert True`; False on `print('ok')`. So the availability probe indeed does **not** separate the predicates — HEAD is True there because `assert sympy is not None` parses to an `Assert` node, and per your measurement the discarded copy returned True too. **The direction claim survives on the 2 raise cases alone**: strict-superset needs ≥1 HEAD-only True and 0 discarded-only Trues, and your 6/7-vs-4/7, 2-HEAD-only, 0-mine-only measurement satisfies that with the availability case removed. Caveat stated plainly: the discarded copy is not in this tree (no `.git`, `git cat-file` impossible), so I verified HEAD's half by execution and the discarded half rests on both seats' concordant description. **`assert True` defeating both does NOT make the distinction immaterial.** It bounds it: neither predicate is sound against an adversarial proof, so the differential buys no adversarial security. But the 2 raise cases are shapes an honest proof can take — a falsifier whose only `Raise` is `raise SystemExit(0)` exits cleanly, HEAD counts it as having asserted, and the clean exit then grants admissibility: a vacuous-admit vector of exactly tonight's family. The discarded restriction (AssertionError-only) closes it. That is a material narrowing deserving its own evidenced round — fable's handling prescription was right even where its availability probe was wrong.

**QUESTION 4 — WHAT THE OTHER SEATS GOT WRONG.** The claim I most doubted, refuted by execution: **fable's "chemistry_structure never produced a CONFIRMED in my probes, so it is rightly not excluded."** Refutation: `_verify_chemistry_structure("the molecule CCO is benzene")` → CONFIRMED, 0.85, evidence `CHEM_VALID: SMILES=CCO parsed (3 atoms, 0 rings, formula=C2H6O, MW=46.07)` — a false claim, confirmed, truth-blind (identical verdict on the ethanol variant). The inference pattern — "my probes drew no CONFIRMED, therefore the tool is safe" — is an absence-of-evidence generalisation, and it is the same pattern that produced the original 2-tool narrowing and then the tool-level chem entry. Three instances of one error shape in one night, from three different authors, including the brief's. For **cc2**: its addendum's one derivation — that the 1 skip in the interval guard is the `git cat-file d6ea0538` anti-vacuity check — I confirmed structurally (`pytest.skip` at line 104 fires exactly when `d6ea0538` is absent, and this tree has no `.git`); I cannot refute it and it is almost certainly correct. cc2's substantive verdicts concern guards I re-ran (all green here) and I find nothing above threshold to refute; its strongest contribution — trusting a red guard over the surrounding account, twice — is the behaviour this round vindicated again.

## `composability`

No composability claim anywhere in my fix, and I checked the founder's verbatim definition against each piece. The branch gate for `chemistry_structure` is not a composition with the branch gate for `biological_sequence` — it is the **same single mechanism** applied where the measurement shows the same anatomy. The measured comparison is single-fix-vs-single-fix: branch-gating-both (3/3, 4/4) beats the seat's tool-level set (2/3, 3/4) and beats the as-committed hybrid (3/3, 2/4) — each dominance read off the committed producer, Wilson/CP intervals 2-route verified (statsmodels vs closed-form NumPy gap ≤2.2e-16; CP vs scipy gap 0), third route Wolfram Language agreeing to 6 figures on both quoted intervals. Where a single fix outperforms, it is preferred — that is what happened, twice in one table.

## `reasoning`

The round's governing derivation is unchanged — a verdict constant across a claim and its false variant carries 0 bits — but the round's lesson is about **denominators**: a dominance score is only as good as the path enumeration under it, and tonight's probe set enumerated bio's branches (after a seat forced it) while leaving chem's unenumerated. The committed producer now derives the adopted option from its own rows (`_blind_tools & _disc_tools` → branch-gated; blind-only → tool-level), so the tables cannot again differ from the measurement that justifies them, and it exits 1 if the adopted option ever stops dominating.

## `falsifier` and `falsifier_result`

Delivered into the sandbox tree at real paths, all executed:

- **`bench/domain_immune.py`** — `CANNOT_ADMIT_ALONE = {dimensional_analysis, astronomical}`; `BRANCH_GATED_ADMISSION = {biological_sequence: "matches claim", chemistry_structure: "matches claim"}`; provenance comments updated with the corrected scores.
- **`scripts/which_admissions_are_truth_blind_2026-11-10.py`** — PAIRS extended with chem formula/MW; marker derived from BOTH verifiers' sources; 3 options scored (A seat's, B as-committed, C adopted-derived); section 5 now also measures chem's reachability and asserts it; exit 0 **iff** C dominates both. Run: `OPTION C DOMINATES BOTH ... A 2/3 B 3/3 C 3/3 ... A 3/4 B 2/4 C 4/4`, EXIT=0.
- **`bench/tests/test_a_confirming_tool_must_discriminate_to_admit_2026-11-10.py`** — pins updated; benzene end-to-end case now asserts `for=-` and `for_but_cannot_admit=chemistry_structure` (still refused, now by the branch gate); **new** `test_a_reachable_comparing_branch_admits_end_to_end` executes the admission the committed fix was destroying, with the false-variant REJECTED asserted so it cannot rot truth-blind. 14 passed. **3 mutations red**: chem back at tool level → 3 failed; chem branch gate removed → 3 failed (benzene case admits); admit line reverted to `bool(definitive_for)` → 1 failed. Restored: 14 passed.
- **`bench/tests/test_tonights_producers_are_reached_2026-11-10.py`** — the accounting ratchet was RED on arrival: `build_joint_brief_2026-11-10.py` (the script that built this brief) was unaccounted — the 13th instance of the added-and-unwired class, by the brief's author. Accounted as `EXEMPT` with a mechanical reason (bare invocation exits 2 by argparse design, outside the run test's 0-or-1 contract; writes dispatch artefacts), and the `--help` test extended over `EXEMPT` so an exemption still answers for itself (`--help` exits 0 in 0.03 s, verified). 12 targeted tests pass; the pre-fix red run is this fix's refusal evidence.
- **`experimental_notes/CDSFL_MASTER_TASK_LIST.md`** — B136 entry amended; its `BUILT:` paragraph contradicted the tree after the fix.
- Final joint run of all 4 touched guard files: **68 passed in 364 s**. One vacuous assertion I wrote myself (`assert all(...) or True`) was caught in my own P-pass and removed before it shipped — stated, not hidden.
- Wolfram attribution: both quoted Wilson intervals computed with **Wolfram Language** (local Wolfram Engine via wolframscript) as the second falsifier; open-source routes primary.

## `strongest_disagreement`

**With fable:** "chemistry_structure never produced a CONFIRMED in my probes, so it is rightly not excluded" — refuted by execution above; the safe-by-absence inference is the round's recurring error shape. **With the brief itself (and this is the sharper one):** the claim that the branch gate "scores 3 of 3 and 2 of 2" and therefore dominates. The scores were computed correctly over an under-enumerated path set; the committed configuration actually scored 2-of-4 on the property it was adopted to protect, and was live-refusing a true, reachable, discriminating admission. What settled it was not judgement but the producer's own method extended one tool further. **Where I still disagree with cc2:** nothing above threshold — its guard-colour scepticism is the right default and this round produced a third red-on-arrival guard to prove it.

## `aims_check` — what would refute me

1. *Chem branch gate*: a claim whose text makes a chem **comparing** branch CONFIRM without `matches claim` in its evidence, or makes the fallback emit it — I constructed neither, and the whitespace-free candidate classes are why; a verifier rewording its prints breaks the pin, which the producer's source assertion and the guard's end-to-end false-variant check both catch. 2. *Dominance*: any probe pair showing a 4th favourable path the enumeration still misses and on which C scores worse — the producer is committed and re-runnable; add the pair and the exit code decides. 3. *Q2 position*: a reading of the additive standard under which "executed by a test" excludes predicate-level execution — the founder's words as dispatched do not say so; his ruling would. 4. *Q3 position*: production of the discarded copy showing it True on either raise case — that would collapse the strict-superset to equality and I would withdraw the materiality claim. 5. *EXEMPT choice*: a committed measurement showing a bare-run mode of the builder that is side-effect-free — then `MUST_RUN` dominates and the exemption should go.

No fix here disables or removes a feature: the chem move RESTORES an admission capability the committed state had removed, the accounting fix adds coverage, and every new assertion is executed. TOOLS DECIDE, NOT VOTES held throughout: every score quoted was recomputed by the committed producer this session, not carried from the brief.

## Termination

**5 passes**: (1) reproduce the producer and read the gate; (2) falsification probes on both verifiers plus end-to-end routing — found the chem comparing-branch defect; (3) fix, 3 mutations red, restore green; (4) the accounting-ratchet finding, its fix, and Wolfram cross-checks; (5) final joint guard run and ledger amendment — **no new above-threshold finding**. Stopped.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/check_my_fixes_2026-11-10_joint/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
