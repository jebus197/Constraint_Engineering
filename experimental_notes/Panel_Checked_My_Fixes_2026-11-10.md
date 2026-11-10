# A free panel checked tonight's fixes and found 3 things wrong in them

10 November 2026, 05:40 GMT

## Summary

A 2-seat free panel (`cc2` = Claude Opus via CLI, `fable` = Fable 5.1 via CLI, both on the existing Max subscription, 0.00 GBP of API spend) audited 9 repairs made during the night of 2026-11-09 to 2026-11-10. Round directory: `bench/logs/check_my_fixes_2026-11-10/`.

It confirmed 6 fixes, found 1 committed guard red in the shipped tree, found 3 fixes absent from the dispatched tree, and refuted 2 claims in the account of the work. Both refutations reproduced on independent verification. Acting on the second produced a repair that dominates both the original and the panel's proposal on 2 pre-named properties.

## Refutation 1 — the vacuity predicate direction

`bench/proof_verify.py` decides whether a proof asserts anything. It was destructively overwritten earlier in the night and restored with `git checkout HEAD --`. The account of that restoration claimed HEAD carried a **narrower** predicate than the discarded copy.

Verified by loading both and driving 7 probes through each:

| probe | HEAD `asserts_something` | discarded `_asserts_something` |
|---|---|---|
| `assert True` | True | True |
| real assert | True | True |
| availability-only assert | True | True |
| `raise SystemExit(0)` | True | **False** |
| dead `raise ValueError` | True | **False** |
| `raise AssertionError` | True | True |
| no assert, no raise | False | False |

HEAD returns True on 6 of 7, the discarded copy on 4 of 7; 2 cases HEAD-only, **0** cases discarded-only. HEAD accepts a strict superset, so the discarded copy rejected more empty proofs than HEAD does, and the recorded claim was backwards. Recorded on entry B69 [`386e72aea57f`] under `failure-later-refutation-protocol`.

**1 of the 3 cases the seat named does not reproduce**: an availability-only assert, written as `import sympy` then `assert sympy is not None`, returns True under both. The direction rests on the 2 `raise` cases. The seat bounded materiality correctly: `assert True` defeats both, so neither is sound against an adversarial proof and the difference is a narrowing, not a soundness fix.

## Refutation 2 — the false-admit set, and why neither proposal was adopted

Producer: `scripts/which_admissions_are_truth_blind_2026-11-10.py`.

The control: a verdict taking the same value on a claim and on a false variant sharing its vocabulary carries 0 bits about the claim.

My earlier narrowing barred 2 tools, having measured `biological_sequence` as discriminating. The seat refuted that and the refutation reproduces: the verifier has 5 favourable branches, 4 comparing and 1 validity-only. Executed — `the sequence 'ATGC' proves the defendant was present` and `the sequence 'ATGC' proves the moon is made of cheese` both return `CONFIRMED` at 0.85 with identical evidence `BIO_VALID: DNA sequence 'ATGC' (len=4, GC=50.0%)`.

The seat proposed excluding the tool outright. That was measured and **refused** — and then a second seat refuted the fix that replaced it, which is why the table below carries 3 options and not 2.

The second seat found that `chemistry_structure` also has comparing branches: molecular formula and molecular weight each check a computed value against the claim. The configuration I had committed barred that tool at the **tool** level, so it destroyed a live, reachable, discriminating admission — `the molecule 'CCO' has formula C2H6O` routes to chemistry/mathematical, the tool is dispatched, and the gate refused anyway. That is the same 1-branch-of-N error I had just refused the first seat for.

Re-scored over **12** fully enumerated admitting paths rather than the 5 the first pass saw:

| option | P1 truth-blind barred | P2 discriminating retained |
|---|---|---|
| A — tool-level exclusion (the first seat's) | 4 of 5 | 3 of 7 |
| B — what I first committed | 5 of 5 | 5 of 7 |
| C — gating at the branch wherever the anatomy calls for it (adopted) | **5 of 5** | **7 of 7** |

Intervals for C: P1, 5 of 5, Wilson 95% [0.565518, 1.000000] and Clopper-Pearson [0.478176, 1.000000]; P2, 7 of 7, Wilson [0.645670, 1.000000] and Clopper-Pearson [0.590384, 1.000000]. Every interval cross-checked by 2 independent routes — `statsmodels` against a written-out NumPy Wilson form, and `scipy.stats.beta.ppf` against an mpmath incomplete-beta inversion — maximum gap 1.110e-16.

Option C dominates both A and B, so under `additive-standard`'s removal clause both are refused. **No composability claim**: C alone beats each of the others alone, and C is not a third mechanism — it is the same branch rule applied wherever the measurement shows the same anatomy, which is why it is derived by a **rule** and not by a list of names.

Built in `bench/domain_immune.py`:
- `CANNOT_ADMIT_ALONE = {dimensional_analysis, astronomical}`
- `BRANCH_GATED_ADMISSION = {biological_sequence: "matches claim", chemistry_structure: "matches claim"}`, the marker read off those verifiers' own sources and **tool-scoped**
- `definitive_for` unchanged, so no favourable verdict is discarded; only admission narrows
- the refusal detail now carries `for_but_cannot_admit=` so the record distinguishes *nothing agreed* from *only blind tools agreed*

### A third truth-blind tool both sides missed

`chemistry_structure` returns `CONFIRMED` for both `the molecule CCO is ethanol` (true) and `the molecule CCO is benzene` (false). The seat had recorded that its own probes never drew a CONFIRMED from it and that it was therefore rightly not excluded.

### 2 defects in the producer itself

1. The marker `matches claim` is `biological_sequence`-specific and was applied globally, wrongly barring `stoichiometric_balance`, which the same run measures as discriminating.
2. The closing verdict named the wrong property as decisive, contradicting figures printed above it.

Both corrected; option B's tool set is now **derived** from the measurement rather than typed, so the producer cannot disagree with itself.

## Half of what was adopted is not reached by real traffic — raised as B137 [`c90b0066dad0`]

Asking `additive-standard`'s symmetric question of my own work: **0 of 10 sequence claims reach `biological_sequence`**, Wilson 95% [0.000000, 0.277533], Clopper-Pearson [0.000000, 0.308497].

2 causes:
- `cross_domain` declares 3 claim types carrying 11 distinct tools and has **0** compiled claim patterns, so every claim classifies `uncategorised` and no tool there can be dispatched. 1 of 10 loaded domains, Wilson [0.017876, 0.404150].
- `biology` is **not** pattern-free (an early wrong inference): it has 3 patterns for 3 claim types, but 0 of them contain `sequence`, `dna`, `rna`, `protein`, `nucleotide`, `complement`, `codon` or `gc content`.

This is B22 [`1ff32fa3455f`]'s `graph_property` finding generalised: a tool declared for a claim type whose patterns lack the vocabulary that would route a claim to it. It costs nothing in correctness today — an unreached tool returns no verdict and the gate fails closed — but it bounds the claim that both gated tools are exercised, and it matters for Bench Run 2.

## The guard passed for the wrong reason

The guard's first version had 12 tests, all green when the original defect was restored (`bool(computing_for)` reverted to `bool(definitive_for)`). Every end-to-end probe it used was refused because another tool **rejected** the claim, so `not definitive_against` was False and the verdict never depended on the gate.

The discriminating case is `the molecule CCO is benzene` in `chemistry`: false, confirmed only by a truth-blind tool, nothing against. The guard now asserts that premise explicitly. `bench/tests/test_a_confirming_tool_must_discriminate_to_admit_2026-11-10.py`, 13 tests, 4 of 4 mutations red.

## The spoken-report generator was marking its own headings

`scripts/morning_report_build_2026-10-12.py`'s B105 [`8341a3b8b7af`] asterisk marker decided "heading" by testing whether every letter was uppercase. `DECISION 1. B13 [`ca9300af3535`], admitting a model is not trivial` has a prose headline, so all 17 were marked, along with 12 `The options.` sub-headings and the note-standard foot-line, which must appear exactly as the final content.

B105's own finding was that a shape heuristic misreading headings was 1 of 3 measured causes of lost founder annotations, so inferring a heading here repeated the error that entry diagnosed. `render_tts` now **records** heading indices as it emits them (3 sites), the way `_ex` already records quoted spans. Marked lines fall 87 → 57; 17 + 12 + 1 = 30 accounts exactly. Guard: `bench/tests/test_a_heading_is_recorded_not_guessed_2026-11-10.py`, 12 tests, 2 of 2 mutations red, with a corrected probe — the first version put the heading at index 0 where the document-title exemption spared it, so the probe's position manufactured the result.

## 3 pinned figures moved, caused by this session's own work

Established by running the real producer against the task list at HEAD and in the working tree, with the file restored and verified byte-identical by sha256:

| pin | was | now | cause |
|---|---|---|---|
| decision queue size | 10 | 7 | B79 [`b66f04976372`], B104 [`0811e96298f9`], B131 [`97de1e6ae57a`] left; asks retired on his 2026-11-08 ruling |
| producer backlog | 10 of 10 | 7 of 7 | same |
| `REPEAT` partition | 5 | 8 | rulings carried in; `REAL` fell 11 → 1 |

The denominator held at 17 throughout, which is the pin earning its keep in the opposite direction to 2026-11-09: the live set did not move, only the classification.

## Also repaired

- `bench/tests/test_a_prose_fix_is_gated_on_its_falsifier_2026-11-10.py` was red, as the seat reported. Converted from a source-text pin to a **parsed-call** check over the runner's AST, so it survives reformatting and further arguments but still fails if `finding=` or `domain=` is dropped. 3 mutations red.
- 3 producers cited by B22 and B136 [`9b448553810d`] lived only in a scratchpad, so those entries cited evidence a clone could not reach. Moved into `scripts/`, `--help` gated (worst case 66.56 s → 0.06 s), and added to `MUST_RUN` (4 → 8).

## What is running

2 joint rounds, sequential (4 concurrent CLI seats would exceed the 8 GiB memory budget): `check_my_fixes_2026-11-10_joint` and `severity_corrected_2026-11-06_joint`. Briefs built by a new parameterised `scripts/build_joint_brief_2026-11-10.py`, each embedding both blind replies in full and verbatim, verified to carry a 240-character contiguous span of each before writing.

The builder's first printed dispatch line was wrong — it named the round as `PANEL_ROUND` where the dispatcher reads `sys.argv[1]` — and both rounds exited 2 in under a second. Corrected in the builder, not only in the command.

Written under CDSFL note standard v1.9 (1 November 2026).
