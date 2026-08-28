# Convergence gate panel, 2026-08-28

Three reviewers: CC1 (curator, does not vote), CC2, Fable 5. Both dispatched
reviewers ran on the Max plan at no metered cost, each sandboxed in a throwaway
git worktree. The brief is at `experimental_notes/panel_briefs/`.

**Disagreement is preserved, not smoothed.** Where the two reviewers differ,
both positions stand.

## cc2

`ok=True`, 18,775 chars, 489.5s

# Fable — panel review, rho veto and merge path
Tree `674040e`, disposable copy, 2026-08-28T03:43:06+01:00.

---

## Q1. Is `rho` structurally hostile to convergence?

**VERDICT: CONFIRMED on the mechanism. REFUTED on the empirical claim.**

### EVIDENCE

**The table reproduces exactly.** `python3 /tmp/rho_repro.py` against `RunnerConfig()` defaults (`rho_threshold=0.25`, `rho_rolling_window=3`, `rho_earliest_round=12`), 12 identical rounds:

```
honest total silence              nov=0 raw=0   rho_avg=0.000  churn=True
exhausted, 2 duplicates a round   nov=0 raw=2   rho_avg=0.000  churn=True
exhausted, 5 duplicates a round   nov=0 raw=5   rho_avg=0.000  churn=True
winding down, 1 novel of 8        nov=1 raw=8   rho_avg=0.125  churn=True
winding down, 2 novel of 8        nov=2 raw=8   rho_avg=0.250  churn=False
recycling at volume               nov=0 raw=40  rho_avg=0.000  churn=True
```

Six for six. The founder's zero-output objection does not rescue the finding: rows 2, 3 and 6 have raw of 2, 5 and 40 respectively — the panel is talking, it is just not saying anything new.

**The veto is wider than the brief says.** Churn blocks *both* live convergence paths, not only gamma-alt:

```
R._evaluate_gate_conditions(15, reg, 0, 0.9, cfg, open_ch_history=[0]*10,
                            rho_rolling_avg=0.10, rho_churn=<flag>)
  rho_churn=False -> converged=True  :: All conditions met: open_ch=0 (stable), novel=0, contested=0, gamma=0.900 (soft)
  rho_churn=True  -> converged=False :: Gate failed: rho_avg=0.100 < 0.25 (churn)
```

And it is entirely absent from the other gate. AST extraction of `_check_hardened_convergence` (lines 5371–5451): `'rho' occurrences: 0 | 'churn': 0`. So the two gate designs disagree about whether rho may block, and the blocking one is the one in use — `hardened_gate_enabled` is `false` in every config from exp42 to exp55 (`grep -rn '"hardened_gate_enabled"' bench/exp*_configs/*.json`, 22 of 26 false; the four `true` are exp40 slices and exp41).

**The algebra, sharpened.** CC1's "novelty ≥ raw/4 every round, indefinitely" is right for the steady state but wrong about the temporal demand, and the correct version is worse. Because the window is 3, what matters is the escape condition at the moment convergence would otherwise fire. SymPy on `(0 + 0 + x/r)/3 = 1/4`:

```
after 2 zero-novelty rounds, novelty needed in round 3 = 3*r/4
  raw= 5 -> need 4 novel  (ratio 0.80)
  raw= 8 -> need 6 novel  (ratio 0.75)
  raw=40 -> need 30 novel (ratio 0.75)
```

A panel that has been quiet for two rounds must produce a **75%-novel round** — a discovery burst on the scale of round one — to clear the flag. That is not "anti-correlated with convergence"; it is the reverse of it.

### Where I break CC1

**"No archived run has ever tripped churn" is false.** Grepping `[CHURN]` in run logs:

```
1  bench/logs/exp37_live.log
9  bench/logs/exp38_live_output.log
3  bench/logs/exp36_resume_live.log
```

13 firings across three runs. I reconstructed exp38's churn rounds from its report's `rho_avg` series and predicted 9 firings at rho_avg `[0.1296, 0.2157, 0.086, 0.1737, 0.1711, 0.1711, 0.2141, 0.0927, 0.1907]`. The log shows exactly 9, at `0.130, 0.216, 0.086, 0.174, 0.171, 0.171, 0.214, 0.093, 0.191`. Exact match — the reconstruction is sound, and exp38 is the demonstration that when a run goes deep, rho collapses. It ran 23 rounds and churned in 9 of the 12 rounds after round 12.

**"The lowest rolling average in the archive is exp43 at 0.287" is false twice over.** Scanning `rho_avg` across all 24 reports: minimum overall is exp38 at **0.0345**; exp43's own minimum is **0.1587** (round 7). 0.2870 is exp43's *final-round* value, so the comparison was made against last-round rho rather than the minimum. Separately, `0.287` is the adjudicator's cost figure — **0.287 s/pair** — which appears in six notes (`RUNWAY_to_BR2_2026-08-18.md:689`, `Track_Record_Audit_2026-08-22.md:422`, and others). Two different quantities, same digits. Under the current runner, `exp42_composer_takeupslack` also crosses (rho_avg 0.1921 at round-number 12), though its critical streak was not clean that round so churn was not the operative blocker.

**The protective mismatch is real, and I can name the third protection CC1 missed.** `novelty_counts.append(novel_this_round)` / `raw_counts.append(len(findings))` at :10009/:10011 — all-severity, against a critical-only streak, as CC1 says. But also: `max_rounds` is **16** in every exp50–53 config and rho cannot fire before round 12, so the veto window is **rounds 12–16 — five rounds of sixteen**. In exp55 (`max_rounds: 6`) the window is structurally empty. And `burst_mode` is `"off"` in every config, so the `novelty_counts.clear()` reset at :10997/:11032 never runs. The exposure is narrow but live, and it is exactly the tail of a long run — the only place convergence is decided late.

### RECOMMENDATION

Converting veto → contributor is right, and the reason is not the anti-correlation — it is that **rho measures a different population from the thing the gate decides.** A ratio over all-severity findings has no standing to veto a critical-quiescence verdict.

Concretely, in `bench/reference_runner_v2.py`:

1. **Delete the early return at :4979.** Replace with a contributory term appended to the reason string of whichever branch fires:
   ```python
   _rho_note = ("" if not rho_churn else
       f" [rho_avg below {cfg.rho_threshold} at this round — discovery efficiency "
       f"was low on the ALL-SEVERITY population; the critical series is what "
       f"converged. Review.]")
   ```
   Carry `_rho_note` into both `return True` strings alongside `_queue_note`, which is already the established pattern for exactly this ("a reader of a reason string is told the queue size rather than left to infer it", :4966-4970).

2. **Same change at :4673-4674** in `_evaluate_gate_conditions` — move the churn entry out of `failures` into a note field. Otherwise the state gate keeps the veto and step 1 achieves nothing.

3. **If a blocking rho is wanted, measure the right population.** Add `novel_critical_counts` / `raw_critical_counts` beside the existing appends at :10009-10011 and compute `rho_critical`. That is building, not wiring — no critical-raw counter exists today. Only *that* series has standing to block a critical-quiescence gate.

4. **`rho_earliest_round=12` has no derivation on record** — the code says so itself at :2088. The shadow floor at :2103 (`2 * rho_rolling_window = 6`) is the honest structural value and is already computed and logged. Once rho stops vetoing, promoting the floor to 6 costs nothing, and the two stop drifting.

**Where I disagree with CC1's framing:** the exposure is not primarily "a clean document". A clean document with churn is blocked, yes — but so is *every* long run that converges after round 12, clean document or not. exp38 is the proof and it was not a clean document.

---

## Q2. Is the vacuous-curve guard unreachable when churn fires?

**VERDICT: CONFIRMED as control flow. PARTIAL as a defect — the ordering is deliberate and test-locked.**

### EVIDENCE

Direct execution of the gate, round 12, all-zero critical history, `gamma_critical=0.0`, `total_findings=10`:

```
clean doc, churn=False -> converged=True
  CRITICAL_QUIESCENCE_CONVERGED (two-sided gate, VACUOUS CURVE): zero critical findings...
clean doc, churn=True  -> converged=False
  critical-quiescence blocked: churn (rho_avg below 0.25) at round 12
```

Unreachable, as claimed. The `return False` at :4979 precedes the `cumulative_critical == 0` test at :5002 with nothing between them.

**But this is not an oversight.** `bench/tests/test_vacuous_gamma_curve.py:126-137` asserts it, by name:

```python
@pytest.mark.parametrize("kwargs,marker", [
    ({"unresolved_critical": 1}, "A4 BLOCK"),
    ({"contested": 2}, "contested"),
    ({"rho_churn": True}, "churn"),
])
def test_the_other_gates_still_bind_on_a_vacuous_series(self, kwargs, marker):
    """Vacuity satisfies the gamma side only. Every other gate still applies."""
```

That test passes (48 passed across the four gate/merge test files, 0.47 s). So the design intent is explicit: vacuity buys the gamma side and nothing else. CC1's finding is therefore not "an ordering bug slipped in" — it is "one of the three gates that still bind should not be binding". That is Q1, not a separate defect.

Two further facts sharpen it. The test pins `round_idx=5` with `rho_churn=True` — a combination the live runner cannot produce, since churn requires round-number ≥ 12. And **`VACUOUS` appears nowhere in `bench/logs/`**: the guard has never fired in any archived run, against any condition. Both exp53 checkpoints record `completed_round` 2 and 3, `converged=False`, `failed=False`, 3 and 4 findings — so the zero-plant control did not converge via the vacuous path either. The guard is entirely untested against live data.

### RECOMMENDATION

Do not reorder. Reordering fixes the clean-document case and leaves the exp38 case — a long run with a real curve, blocked at round 13 by a ratio over the wrong population — untouched, while silently contradicting a named test.

Take the Q1 repair instead: remove the churn early return at :4979 and the churn failure at :4673, and Q2 dissolves with no ordering change at all. Then amend `test_the_other_gates_still_bind_on_a_vacuous_series` to drop the `rho_churn` row and add a positive test that a churning vacuous run **converges with the rho note attached** — which is the behaviour the founder's "contributing measure" actually describes.

If Q1 is rejected and churn stays a veto, then the minimal Q2 repair is to hoist the `cumulative_critical == 0 and total_findings > 0` test above :4979 — and the same test file must be amended either way, so "reorder" is not the cheaper option.

---

## Q3. Merge: wiring or building?

**VERDICT: PARTIAL — wiring at the registry, building at the adjudicator.**

### EVIDENCE

**CC1 is right that the receiving end is finished.** I probed `FindingRegistry.resolve` directly with a live registry and two registered findings:

```
adjudicator=model    -> status=WITHHELD  merged_into=None    blocked=adjudicate_by_repair SAME both directions
adjudicator=tool     -> status=MERGED    merged_into=C0002
adjudicator=human    -> status=MERGED    merged_into=C0002
adjudicator=runner   -> status=MERGED    merged_into=C0002
```

A tool-adjudicated MERGED writes cleanly today. Nothing needs building there. The claim in `RUNWAY_to_BR2_2026-08-18.md:689` that "**NO** code path writes MERGED at all" is true of the current *call sites* — all four pass `adjudicator="model"` — but false of the *capability*.

**CC1 is right that the in-code reason for the gap is stale.** The comment at :2508-2511 says the tool "cannot be called from HERE: this function receives `(registry, round_idx, cfg)` and no target path, and RunnerConfig carries none." Both halves are false on this tree. `RunnerConfig` has a `test_article` field (:494), and `_update_finding_statuses` — the very function containing that comment — already reads it 76 lines below, at :2596:

```python
target_file = (entry.get("target_file") or (cfg.test_article if cfg else None))
...
from bugzilla_loop import attempt_close
attempt = attempt_close({...}, target_path, test_cmd=..., timeout=120)
```

That is apply-a-fix-and-re-run, in scope, already running. So the plumbing objection is answered by the file itself.

**Where CC1 is wrong: `adjudicate_by_repair.py` cannot be called as-is.** `_direction` (:209-226) writes the patched source to the **live target file** and restores it in a `finally`:

```python
target.write_text(patched, encoding="utf-8")
v_self  = _verdict(fixer.get("falsifier_code") or "", state)
v_other = _verdict(other.get("falsifier_code") or "", state)
finally:
    target.write_text(orig, encoding="utf-8")
```

Acceptable for an offline batch on a checkout. Not acceptable mid-run: the runner hashes the target every round and raises `*** TARGET INTEGRITY WARNING ***` on change (:10181-10190), which this would trip on every adjudication; and a kill between write and restore corrupts the target under review. The Bugzilla loop next door uses a **sandbox copy** — that is the pattern. Rewriting `_direction` to take a scratch path is a real change with a correctness stake, not wiring.

**The cost of a wrong merge, quantified.** From `experimental_notes/data/adjudication_by_repair.json`, 133 pairs:

```
SAME 23 | DIFFERENT 10 | SAME_ONE_WAY 17 | DIFFERENT_ONE_WAY 35
UNDECIDABLE 33 | DISAGREE 8 | NO_BASELINE 7
```

Both-directions-agree decides **33 of 133 — 25%**. The other **75% the tool cannot decide.** That number is the whole of Q3.

**A separate defect I found while probing.** `resolve`'s tool-only enforcement (:1465-1472) fires only on `adjudicator == "model"`, and `adjudicator` **defaults to `"tool"`**:

```
reg.resolve(a, 'MERGED', 1, merged_into=b)   # no adjudicator argument
  -> status MERGED, status_adjudicator recorded as 'tool'
```

A call site that forgets the argument writes MERGED *and stamps it as tool-verified*, with no execution behind it. The comment at :1467-1469 states this is intentional ("the default, so every existing call site keeps its authority"), but the effect is that the tool-only guard is enforced by caller honesty. Meanwhile `evidence_required` — declared for all ten statuses, including MERGED's `"adjudicate_by_repair verdict SAME in BOTH directions"` — is **read zero times** in the runner and zero times in the tests. It is documentation wearing a schema's clothes.

### RECOMMENDATION

1. **`scripts/adjudicate_by_repair.py:209`** — change `_direction(fixer, other, target, orig, orig_key)` to write to a scratch copy and run the falsifier with `cwd` pointed at it, rather than mutating `target`. Extract `adjudicate_pair(A, B, target_path) -> verdict` as an importable function; keep `main()` as a thin caller. This is the only genuine build.
2. **`bench/reference_runner_v2.py:2520`** — replace the `resolve(..., adjudicator="model")` withhold with a call to that function, and pass `adjudicator="tool"` with `evidence=` carrying both falsifier hashes, both verdicts, both directions and the target hash. Delete the stale comment at :2508-2511; it is now false and will mislead the next reader as it misled this review.
3. **`bench/reference_runner_v2.py:2183`** — `_try_merge_arbitration` does not receive `cfg`. Add it as a parameter (both call sites, :2459 and :10694, have `cfg` in scope) and route it through the same adjudicator. Keep the WITHHELD fallback verbatim for every non-`SAME` verdict.
4. **`bench/reference_runner_v2.py:1430`** — change `adjudicator: str = "tool"` to `adjudicator: str` (required) and update call sites. A claim of tool authority should have to be typed.
5. **`bench/reference_runner_v2.py:1465`** — enforce `evidence_required` for the tool-only statuses: refuse MERGED whose `evidence` does not carry two falsifier hashes and two verdicts. The schema already says what to check.

### On the founder's question — where judgement sits

I disagree with the framing that judgement must be *added* to the merge path. Judgement is already there, and putting more in is the wrong move.

**The 75% is the answer.** The tool decides 33 of 133 pairs. The other 100 do not become votes — they become **WITHHELD**, and a withheld finding stays live, stays countable, stays in gamma and in `open_crit_high_count`. It keeps costing rounds until something resolves it. That is not a dumb calculator refusing to answer; it is the system holding an open question open at a measured price. The intelligence is in *building the falsifier and the repair in the first place* — a model proposing a fix that cures another finding's test is doing far harder work than a model ticking a merge box. The repair is the judgement. The re-run is the check.

Where I would put a human, and only there: `DISAGREE` — 8 pairs where forward says SAME and reverse says DIFFERENT. That is not "the tool has no opinion"; it is "the tool has two contradictory opinions", and the contradiction is itself evidence that the two findings sit in an asymmetric relation the merge model does not represent (A's fix subsumes B, but B's does not subsume A — arguably neither MERGED nor KEEP_DISTINCT is the right answer). Route those to ESCALATED, which the vocabulary already reserves as "the SOLE arbiter state — do not widen it" (:1226). The remaining 92 undecided pairs need no judgement at all. They need a better falsifier, which is a discovery problem, not an adjudication one.

The failure mode I would guard against is subtler than voting: **letting a model's confidence in its own merge proposal count as partial evidence** when the tool returns `SAME_ONE_WAY` (17 pairs). It will be tempting, because one-way SAME looks like most of the way there. It is not. Require both directions or withhold — the asymmetry is the finding.

---

## WHAT I COULD NOT CHECK

- **I did not run a live experiment.** Every gate result above comes from calling `_compute_rho`, `_evaluate_gate_conditions` and `_check_gamma_alt_convergence` directly with constructed inputs. No panel dispatch occurred in this session at all. The claim "churn would fire in exp38 at these 9 rounds" is a reconstruction from the archived report validated against the archived log, not a re-execution.
- **I did not run the adjudicator for real.** `--dry-run` reports 133 unadjudicated pairs, 90 code targets in scope, 43 exam. I did not run `--run exp44`, so I have not personally verified the 23 SAME verdicts — I read them from the stored JSON.
- **The archived `rho_avg` values are known-contaminated.** `Stage1_Accounting_Repairs_2026-08-18.md:101-102` shows exp46 corrects 0.3009 → 0.2176 and exp48 0.3056 → 0.1944 once `novelty_counts` is repaired. My archive scan uses the *uncorrected* stored values, so my minima are, if anything, optimistic. Under corrected accounting exp46 and exp48 would both sit below threshold. I did not recompute the corrections.
- **exp53's checkpoints carry no rho series and no convergence reason string** (both fields empty), so I could not determine *why* those runs stopped — only that `converged=False` and `failed=False`. My statement that the vacuous path never fired rests on `VACUOUS` being absent from every file under `bench/logs/`, which is weaker than reading the reason.
- **I did not run the full 3878-test suite** — only the 4 gate/merge files (48 passed) and 3 rho files (40 passed). I cannot say the tree is green overall.
- **Whether removing the churn veto changes any archived run's verdict** is untested. It would require re-running exp38 and exp42_takeupslack under the patched gate, which needs a live panel.

---

## fable

`ok=True`, 9,283 chars, 453.6s

All checks done. Report follows.

---

# Fable — Panel review: rho veto and the merge path

Timestamp: 2026-08-28 03:36–03:55 BST. All commands run in the disposable copy at commit 674040e. Gate tests pass on this tree (`pytest bench/tests/test_two_sided_gate.py test_per_model_rho_itc.py test_rho_persisted_2026-08-27.py` → 16 passed).

## Q1 — VERDICT: PARTIAL. Structural claim CONFIRMED; archive claim REFUTED in one material respect.

**What I ran.**

1. Reproduced CC1's table by calling `_compute_rho` directly (defaults confirmed: threshold 0.25, earliest 12, window 3). **All six rows reproduce exactly**: 0.000/True, 0.000/True, 0.000/True, 0.125/True, 0.250/False, 0.000/True.
2. Called `_check_gamma_alt_convergence(12, ..., rho_churn=True/False)` with a perfect zero-critical history and `total_findings=9`. churn=True → `False, "critical-quiescence blocked: churn"`. churn=False → `True, VACUOUS CURVE converged`. The veto is real and it fires before everything at line 4979.
3. Read `_evaluate_gate_conditions` (4673–4674, 4718–4719): churn is appended to `failures`, and any failure returns False. **So churn vetoes BOTH convergence paths, not just the alt path.** The anti-correlation argument is sound and worse than stated: there is no route around it. The run does not hang — it burns the round budget and reports non-convergence, exactly the failure the vacuous guard was written to prevent.
4. Extracted per-round `rho_avg` from every archived report (`bench/logs/*/*report*.json`).

**Where CC1's empirics break.** "The lowest rolling average in the archive is exp43 at 0.287, margin 0.037" is wrong on this tree:

- **exp42_composer_takeupslack, round 12: rho_avg = 0.1921** — below threshold at a churn-eligible round. Under today's code that trips churn. The margin was not +0.037; it was breached by 0.058. The likely reason it never fired live is the Bug 4 off-by-one (`len-1` vs 1-based round, comment at 2081) active in June, which delayed churn one round; by round 13 rho recovered to 0.3032. So "no archived run ever tripped churn" may be true of what the runs *logged*, but the archive **does** contain a breach under current code — and notably it was a healthy mid-run lull that recovered, meaning the churn region is visited by live panels, not only by the hypothetical clean document.
- exp43's 0.287 is its final-round value (its true minimum is 0.1587 at round 7, churn-ineligible). CC1's number is only correct restricted to churn-eligible rounds — the claim as worded is false.
- The runner's own shadow-floor comment (2093–2095) records *corrected* rho_avg 0.2176 (exp46) and 0.1944 (exp48), both under 0.25 — CC1's "protective mismatch" story coexists with three sub-threshold excursions in the modern archive alone.

**The founder's objection does not weaken the finding.** Confirmed: the blocked rows have raw = 2, 5, 8 — models responding, output all-duplicate. That is the convergence signature, not broken machinery. (One refinement the objection *does* motivate: zero-raw rounds folded into rho as 0.0 conflate dead dispatch with exhaustion; `models_responded` is already in round records and is the right discriminator for the alarm use.)

**RECOMMENDATION.** Veto → contributor is the right repair, and it is small:

1. `bench/reference_runner_v2.py:4979–4984` — delete the early return. When `rho_churn` is true at a convergence that otherwise passes, append to the reason string: `[rho_avg {x} below {threshold} at close — low all-severity novelty is consistent with exhaustion; review dedup health]`, in the style of the vacuous-curve "REVIEW THIS RUN" tail. Low rho is evidence *for* exhaustion; the one failure mode it can genuinely indicate (dedup over-merging suppressing novelty) is a review flag, not a gate condition.
2. `reference_runner_v2.py:4673–4674` — same change in the state gate: log, don't append to `failures`.
3. Keep churn exactly where it does honest work: per-model ITC restart (10347–10354) and the shadow-floor telemetry (2086–2109). No change there.
4. Do **not** add rho as a third gate condition. The two-sided gate (gamma_critical + zero-critical streak) is the settled design and already encodes diminishing returns twice; rho joins the reason string as corroborating context, which is precisely "a contributing measure".

## Q2 — VERDICT: CONFIRMED.

**Evidence.** Step 2 above is the direct demonstration: identical inputs, only `rho_churn` flipped, and the vacuous-curve guard at 5030 is unreachable behind the return at 4979. Verified the exp53 note: two run directories (`exp53_control_zero_live_2026072*`, `...0801*`), 3 and 4 macrophage shadow-round files, no final report — neither run reached round 12, so the guard has never met live churn.

**RECOMMENDATION.** Neither reorder nor a conditional churn return — both are half-fixes. Reordering repairs only the vacuous case and still vetoes the ordinary clean tail (criticals exhausted, minors trickling below 25% novelty), which is the *common* exposure. The Q1 repair (delete the veto) subsumes Q2 entirely; land that and this finding closes for free. If for some reason the veto is retained, the minimal correct form is: evaluate the streak and vacuous check first, and let churn block only a *non*-clean tail — but I would not build that.

## Q3 — VERDICT: PARTIAL. Wiring not building is right; the "23 SAME" evidence base is overstated by roughly half.

**Evidence.**

- Read all three sites. Vocabulary 1188–1197: MERGED is tool-only, evidence `adjudicate_by_repair verdict SAME in BOTH directions`, terminal, `out_to: ()`. Merge seam 2183–2209: vote path correctly closed. `scripts/adjudicate_by_repair.py`: real, complete, and the runner already owns both halves it needs (`_apply_fix_to_source`, `reverify_falsifier`). In-run wiring is *simpler* than the offline script — the live target is the baseline, so the git version-walk disappears. CC1's structural conclusion stands.
- **But I audited the 23 SAME rows' `detail` fields:** only **11 of 23** are clean (`REFUTED` on all four legs). 12 carry at least one `ERROR` leg; one is `ERROR` on all four. `_direction` (adjudicate_by_repair.py:222–226) reaches SAME as the *fall-through for any non-CONFIRMED verdict*, and the `FIX_INEFFECTIVE` check only catches `v_self == CONFIRMED`. I confirmed by synthetic run that a patch which breaks the module outright yields `ERROR` (pristine → CONFIRMED, cured → REFUTED, syntax-broken → ERROR). Consequence: **two mutually module-breaking patches adjudicate SAME in both directions.** Wired as-is, that writes MERGED — a terminal, unrecoverable deletion from the convergence evidence — on a pair of bad patches. (One honest aside: my first synthetic showed "cured → CONFIRMED"; that was my own stale-`__pycache__` artifact, same file size in the same mtime second, resolved before concluding anything.)

**RECOMMENDATION.**

1. Before wiring, tighten `_direction` (both copies, :222–226 and :358–362): SAME requires `v_self == "REFUTED" and v_other == "REFUTED"`; any ERROR/UNTOOLABLE leg → UNDECIDED for that direction. Today's merge-ready evidence is then **11 pairs, not 23**.
2. Give MERGED an exit: add `REOPENED` to its `out_to` (parity with REFUTED and CLOSED, which both have it), *and* union the falsifier — the surviving canonical entry inherits the merged finding's falsifier and evidence, so even a wrong merge deletes a count from gamma but never deletes a check. That converts "a wrong merge silently deletes convergence evidence" into "a wrong merge miscounts, recoverably".
3. Bound expectations: on the archived distribution only 33/133 pairs decided both directions (25%). Most live merge proposals will stay WITHHELD. That is correct behaviour, not a shortfall.

**Where judgement sits** (my position, preserved as disagreement if the others differ): in *what to compute*, never in *what the computation concluded*. Concretely three places — candidate selection (the pair space is quadratic; models nominating which pairs merit a repair test is judgement doing scheduling), authorship (the fixes and falsifiers that constitute the evidence are model-written, tool-executed), and the exit path (DISAGREE/UNDECIDED → WITHHELD → ESCALATED, where the vocabulary already names the human as sole arbiter). That is an intelligent calculator: intelligence proposes and routes; the calculator's verdict register is never writable by opinion. Nothing about the founder's question requires a fourth place.

## WHAT I COULD NOT CHECK

- Whether churn stayed silent in every **live** run: per-round `rho_churn` was not persisted until 2026-08-27, and I found no exp42_takeupslack stdout log. My "would trip under current code" is recomputed from persisted `rho_avg`, not observed from a live log — and those archived values predate the similarity-function repair, so corrected values would differ (direction unknown).
- Whether exp42_takeupslack's stored `rho_avg` used today's zero-raw handling (Bug 1); if not, exact values shift.
- `adjudicate_by_repair.py` end-to-end re-execution (needs the off-repo exam store and cross-ref git history). I verified the code by reading and audited its stored output; I did not regenerate the 133 rows.
- The full test suite — I ran only the three rho/gate test files (16 passed), not the ~3878.

---
