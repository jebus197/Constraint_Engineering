# 2 Library Names Can Be 1 Route

**3 November 2026, 03:40 GMT**

## Summary

An audit of this session's own producers against the `sy` standing constraint scored each by counting STEM imports. That predicate is a proxy, and it ranked the set nearly backwards: 4 of a discovered population of 7 scripts passed it while resting a reported interval on a single route, and the 1 script it flagged owed no interval at all. The repair is built, measured and guarded; entries **B97** and **B98** of the master task list record both findings as DONE, and neither needs a ruling.

## 1. Why counting imports is the wrong predicate

The project's primary/secondary falsifier rule, settled 2026-10-31 and carried in `bench/falsifier_pairing.py`, turns on **independence**, not count. Its own measurement records that `scipy` and `statsmodels` resolve to the identical verifier `_verify_statistical`, so the canonical 2-tool statistical pair was 1 function called twice.

The consequence is exact. A helper computing Wilson from `statsmodels.stats.proportion.proportion_confint` and Clopper-Pearson from `scipy.stats.beta.ppf` imports 2 libraries and cross-checks neither interval. Those are **2 quantities on 1 route each**: it scores 2 by import count and 0 by the rule the count stood in for.

| producer | STEM imports | by import count | routes per quantity | by independence |
|---|---|---|---|---|
| `a_models_own_verified_flag_closes_it_2026-11-03` | 3 | PASS | Wilson 2, CP 2 | PASS |
| `a_bare_clock_was_dated_from_the_mtime_2026-11-03` | 2 | PASS | Wilson 1, CP 1 | **FAIL** |
| `b96_the_report_against_the_note_standard_2026-11-03` | 2 | PASS | Wilson 2, CP 1 | **FAIL** |
| `which_ticket_store_lessons_the_registry_lacks_2026-11-02` | 3 | PASS | Wilson 1, CP 2 | **FAIL** |
| `does_the_register_need_a_forum_2026-11-02` | 3 | PASS | Wilson 1, CP 2 | **FAIL** |
| `what_a_self_reported_v_bar_is_worth_2026-11-03` | 2 | PASS | a summation, 2 | PASS, strongest |
| `c0001_provenance_does_not_reconcile_2026-11-03` | 0 | **FAIL** | reports no quantity | N/A |

`what_a_self_reported_v_bar_is_worth_2026-11-03.py:77-78` computes each weight sum twice, once by `np.asarray(a, dtype=float).sum()` and once by `sum(sp.Rational(str(float(x))) for x in a)`, and derives its gain symbolically at line 93 with `assert sp.simplify(gain - a1) == 0`. By import count it scores the same 2 as a helper with no cross-check.

## 2. The C0001 producer, and the fix that was refused

`scripts/c0001_provenance_does_not_reconcile_2026-11-03.py` reports `1 of 4` and `9 of 23`, and a Wilson plus Clopper-Pearson pair was drafted for both. Checking the predicate killed that fix: the 4 `exp42_composer*` runs are a **complete enumeration**, 4 of 4 present against 78 runs under `bench/logs/`, and the figure serves an identification — which run the C0001 provenance clause names. An interval on it would state what fraction of composer runs carry severity 0.90.

The float-equality hazard was also guessed at and was already handled: line 104 compares with `abs(float(r[3]) - sev) < 1e-9`, not `==`.

**What was genuinely missing was a second route.** The primary counts registry entries at or above a threshold constant of `1.0` and asks whether that count is 0. The secondary, added as `_max_severity`, takes the run's actual maximum and compares. Both are reported with their agreement.

The secondary carries more than the primary can: the 2 routes agree in 4 of 4 candidate runs, and the maximum route establishes that C0001 is not the highest severity in **any** of the 4, where the primary could only ever speak for the 1 matching run.

## 3. Proving the second route is the same quantity

A second route is a cross-check only if it computes the same quantity; otherwise the pair is the error it exists to catch.

- **SymPy**: `simplify(lower_written_out - lower_canonical) == 0` and the same on the upper bound, both `True`.
- **statsmodels against mpmath at 40 dps**: worst disagreement `1.156e-16` over `(1,4)`, `(9,23)`, `(0,19)`, `(37,38)`, `(3,6)`.

## 4. The repair, and a refactor refused on evidence

All 5 `_iv` copies were first called on identical inputs: they agree to 10 decimal places across 4 cases. A shared helper would therefore have fixed **no measured numerical defect**, and was refused under `simplicity-default` and `composability-requires-a-measurement`, which requires a committed measurement that the composed form dominates either part alone.

The 1 complete implementation was propagated into the 4 incomplete ones, keeping the 3-tuple contract that 4 of 5 files already used. The single call site in `a_bare_clock_was_dated_from_the_mtime_2026-11-03.py` moved from a 2-tuple unpack to a 3-tuple and now prints the cross-check magnitude.

2 docstrings were false and are now true: `b96_the_report_against_the_note_standard` claimed *each on 2 implementations* with CP on scipy alone, and `does_the_register_need_a_forum` claimed *each on 2 independent tools* with Wilson on statsmodels alone.

## 5. A figure must outlive its own repair

`scripts/counting_imports_ranks_producers_backwards_2026-11-03.py` reported `0 of 7` the instant the repair landed, which would have left the finding alive only as prose — the defect `measured-rate-travels-with-its-script` names.

It now takes `--rev`, reading subjects via `git show <rev>:<path>`:

```bash
python3 scripts/counting_imports_ranks_producers_backwards_2026-11-03.py --rev d6ea0538
```

| source | population | single route | cross-checked |
|---|---|---|---|
| `git d6ea0538` | 7 | **4** | 5 |
| working tree | 7 | **0** | 6 |

Cross-verified on a structurally different route: an AST pass keying on call structure rather than text names the **same 4 files** — 4 of the 5 `_iv`-defining scripts. The denominators differ because the producer's population also holds 2 session producers defining no `_iv`, and each figure is reported with its own denominator.

## 6. Guards and falsification

- `bench/tests/test_an_interval_rests_on_two_routes_2026-11-03.py` — 19 tests. 12 **execute** every `_iv` helper and cross-compare, which is what reaches the 2 files dated 2026-11-02 that `test_tonights_producers_are_reached_2026-11-03.py` cannot see, its glob matching only `*2026-11-03*`. Its load-bearing case runs the detector against `d6ea0538` and requires it to come back dirty.
- `bench/tests/test_the_superlative_has_two_routes_2026-11-03.py` — 7 tests. Its decisive case is **planted**: a registry whose maximum sits at `0.95`, below the threshold, where the counting route concludes the finding IS the highest and the maximum route catches that it is not. A guard built only from live runs would pass with the second route deleted.
- `scripts/the_second_route_mutations_2026-11-03.py` — **4 of 4 mutations red**, subject restored byte-for-byte by sha256.

## 7. 4 defects in the instruments, each found by running them

1. **A test of a maximum cannot detect a floor beneath it.** Asserting `_max_severity({"A": None, "B": 0.4}) == 0.4` is satisfied by coercing `None` to `0.0`, since `0.0` is never the maximum of a set holding a positive number. The discriminating case is a registry whose only entry is the `None`: skipping returns `None`, coercing returns `0.0`.
2. **The detector detected itself**, because it necessarily holds the literal it searches for and the regexes it matches with, and was then classified single-route on its own pattern text. Third occurrence of that shape.
3. **Its first population was a hand-picked list of 6 reported as coverage**, and it missed `does_the_register_need_a_forum_2026-11-02` — a file this session repaired while the list justifying the repair never examined it. The population is now discovered by definition site.
4. **The first patch replaced a block without checking what followed it** at a deeper indent, orphaning a `print` and breaking the file.

## 8. A process error, recorded

A memory file was added and `resources/MEMORY_EXCLUSIONS.md` rewritten while a commit board was running. The board tests the working tree and `bench/tests/test_recovery_memory_doc_repairs.py` is among its 120 guard files and counts those files, so that test's verdict became dependent on when the board reached it. The standing rule against editing the tree mid-board exists for that reason. The ledger was refreshed by invoking `cdsfl_sv._update_memory_exclusions_ledger` rather than by hand, after a dry run: 292 to 293 files, mirrored 234 to 235, total 291 to 292.

## 9. Status

Entry B97, the import-count audit that ranked producer rigour backwards, and entry B98, the superlative tested against a hardcoded severity threshold, are both DONE and COMMITTED; neither needs a ruling. Decisions awaiting the founder remain **14**, counted from the morning report's own numbered sections: B21, B71, B76, B77, B79, B81, B82, B83, B84, B87, B88, B93, B94, B96. 16 entries are OPEN, reconciling as 13 presented plus 3 not — B20 deferred on his instruction, B22 a question he raised, B56 settled at 1 in 50 — with B71 BLOCKED on him and correctly presented.

Written under CDSFL note standard v1.9 (1 November 2026).
