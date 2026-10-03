# Merge adjudication: neither seat's fix dominated, so the disagreement was decided per assertion

Record written 2026-10-03T09:13:01+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed, and why a third round existed at all

The 2026-10-02 star round left 3 disputed items with 2 incompatible fixes: cc2 and fable had each repaired the same defects in their own sandbox copies, and neither set dominated. Measured before this round ran: applying cc2's fix left 8 of fable's falsifiers red, applying fable's left 6 of cc2's red, and a 1-line composition of the 2 moved cc2's failures from 6 to 5 without converging. A merge could not be chosen by reading the 2 diffs, because each was internally consistent.

So this round asked the 2 free seats, cc2 and fable on the Claude CLI under the Max subscription, to adjudicate the merge per assertion rather than per fix, under the 3 formal standards the panel dispatcher now carries by construction: ADDITIVE, SIMPLEST SUFFICIENT, and COMPOSABILITY (compose only on a demonstrated advantage over each arm alone). No paid dispatch occurred.

## What the 2 seats returned, and where they agreed

Both seats decomposed the disagreement to the same per-assertion decisions, independently:

- **D-B, who names a sub-critical drain**: to cc2. One widened scope expression on the already-wired reader makes "whatever the counter drops, this names" hold by construction; the alternative keeps 2 scope expressions in sync by hand plus a new method and a second log line. Both seats tested composing the 2 and both refused it: with the reader widened, every id the sibling returns is already named, so composing prints the same id under 2 headings and has no advantage over either arm alone.
- **D-C, where an unobserved refusal is repaired**: to BOTH, composed, and this is the only genuine composition in the merge. It is earned by an executed 2 by 2 rather than by judgement. cc2's stamp fix alone leaves the A4 blocker at 0 over 2 replayed entries, because a checkpoint written before the fix carries the stale stamp and no stamp site runs again for it. fable's consumer guard alone leaves the record asserting that a machine tried and failed on an entry no routing ladder ever reached. Only the composition passes both properties.
- **D3, stale integrity stamps**: to fable. A pure addition at 2 call sites that already fire only after a replacement falsifier verified CONFIRMED.
- **The forensics run-root pin**: to cc2 wholesale, including the dual-root counterpart lookup that fable's version lacks.
- **The spawn-blob per-token path check**: to fable, the only fix for a confirmed defect.

One of fable's own assertions was retired rather than carried: it required the criticals reader to stay narrow, which after decision D-B pins the report to a scope narrower than the counter it exists to mirror, which is the shape of defect D-B itself. The superseded assertion text is preserved verbatim in the delivered test's docstring, and the intent behind it is re-asserted against the single reader.

## What was done with the findings

The merge was applied to the live tree by hand rather than wholesale, because 2 of the files each seat delivered had been edited after the sandboxes were taken and copying them in would have silently reverted the figure-amendments register. Verified on the live tree afterwards: all 3 seat falsifiers exit clean, 94 tests pass on the cc2-side set including the register and the refused-body work, and 43 of fable's test variants pass against the same single file set.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# ADJUDICATE A MERGE: 2 fixes, neither dominates, decide per assertion

Both of you fixed the same 3 confirmed defects in the star round of 2026-10-03.
Your fixes are INCOMPATIBLE. This round has one deliverable: **a single merged
file set that passes BOTH seats' falsifiers.** Not an opinion on which is nicer.

## The artefacts under review

- `bench/reference_runner_v3.py`, `bench/key_access_forensics.py`,
  `bench/falsifier_verify.py` — currently at the PRE-MERGE state, with neither
  seat's star-round fix applied.
- Both seats' delivered fixes and tests are in the tree, preserved at
  `experimental_notes/seat_evidence/falsifier_supply_and_integrity_star_2026-10-03/`
  and `bench/logs/falsifier_supply_and_integrity_star_2026-10-03/sandbox_harvest/`.

## THE MEASUREMENT THAT MAKES THIS A COMPOSABILITY QUESTION

Each fix was APPLIED and then run against BOTH seats' falsifiers. Executed, not
read:

- cc2's fix applied alone: **8 of fable's tests RED** —
  `test_a4_scope_guards_2026-10-03.py` (D-C carve-out reaching the A4 consumer,
  D-B sub-critical naming, D3 stale-stamp retraction) and
  `test_spawn_blob_tokens_2026-10-03.py`.
- fable's fix applied alone: **6 of cc2's tests RED** —
  `test_one_predicate_excludes_and_reports_2026-10-02.py` (excluded-implies-
  reported, randomised registries, the A4-drop invariant),
  `test_key_access_advisory_2026-10-02.py::test_the_excused_critical_is_reported_rather_than_lost`,
  `test_an_unobserved_refusal_keeps_a4_blocking_2026-10-03.py`,
  `test_forensics_verdict_is_a_fact_about_the_run_2026-10-03.py`.

So NEITHER is sufficient alone, and the founder's composability standard is
satisfied for composing: the demonstration exists.

**A FIRST COMPOSITION FAILED AND YOU SHOULD NOT REPEAT IT.** Dropping the
severity gate from `integrity_refused_criticals` so its scope matches
`unverified_critical_count` took cc2's failures from 6 to 5. The 2 fixes
disagree PER ASSERTION, not on one scope line.

## The shape of the disagreement, as far as it is understood

fable widened the SCOPE correctly — `unverified_critical_count` has carried no
severity gate since 2026-09-06, so it drops sub-critical refusals too — but
reported them through a SECOND reader, `integrity_refused_subcriticals`. cc2
argued the simplest sufficient form is to widen the 1 wired reader so that
"whatever the counter drops, this names" holds BY CONSTRUCTION. BOTH readers are
wired, so the additive standard does not decide it.

## Use the harness

RUN things. Apply a candidate merge in your sandbox and EXECUTE both test sets.
Report the command and its output. A claim that a merge works, without the 2 test
runs behind it, is not an answer. Use gamma and the two-sided gate for anything
touching convergence and S_k for anything touching admission; report any
proportion with a Wilson interval.

## HOW TO DECIDE — the 3 formal standards, which are in your SYSTEM prompt

For EVERY assertion where the 2 fixes disagree, name which standard decides it:
ADDITIVE (nothing removed without a committed measurement; nothing added that
no caller reaches), SIMPLEST SUFFICIENT (the simpler form wins where both
discharge the requirement), COMPOSABILITY (compose only on a DEMONSTRATED
advantage over each alone; prefer the single fix where it performs as well).

## Produce a fix and test it

Deliver the merged files INTO the sandbox repository tree at their real paths.
Then run BOTH test sets and paste the 2 summary lines. If an assertion in either
set is WRONG rather than merely inconvenient, say so and justify retiring it
under the standards — do not silently delete a test to go green.

## What would refute you

State what evidence would overturn your merge, and what you looked for that
would have changed your mind and did not appear.

## Output

Return, field by field: verdict; reasoning; the falsifier and its executed
result; the per-assertion adjudication table naming the deciding standard; the
2 test-suite summary lines after your merge; the files you delivered and where;
what would refute you; and the strongest disagreement with this brief's framing
and with the other seat's fix, naming where you think they are wrong.

## Termination

Stop when a further pass produces no new above-threshold findings.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 63 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel merge_adjudication_2026-10-03) -->

## VERDICT

**MERGE DELIVERED AND GREEN.** Both seats' full test sets pass against one file set. The disagreement is not one scope line — it decomposes into **7 assertions**, and the three standards decide them **differently**: 3 go to cc2, 3 go to fable, 1 (the D-B reporting shape) required retiring a fable assertion that is in *direct logical contradiction* with a committed oracle. Only **one** pair is a genuine composition, and I have the 2×2 measurement that earns it.

---

## THE FALSIFIER AND ITS EXECUTED RESULT

The composability claim — that D-C needs **both** halves — is the only one in this merge that cannot be settled by "both can coexist". I mutated each half out of the merged source and measured the two required properties:

```
variant                        | A4 over 2 REPLAYED entries | fresh route: irreducible_escalation
----------------------------------------------------------------------------------------------------
BOTH (the shipped merge)       |              2 [  OK] |                  False [  OK]
cc2 stamp fix ALONE            |              0 [FAIL] |                  False [  OK]
fable consumer guard ALONE     |              2 [  OK] |                   True [FAIL]
NEITHER (pre-merge)            |              0 [FAIL] |                   True [FAIL]
```

The replay arm is not hypothetical. `--resume` restores a registry through `FindingRegistry.from_dict(ckpt_data["registry"])`, whose **entire body** is `reg.entries = data.get("entries", {})` — read with `inspect.getsource`, then exercised end to end:

```
rehydrated entries: 2
A4 after a REAL from_dict restore of a pre-fix checkpoint: 2
OK: a resumed pre-fix registry keeps blocking A4
```

So a checkpoint written **before today** carries `irreducible_escalation=True` beside `integrity_unobserved=True` and no stamp site ever runs again for it. cc2's stamp fix cannot reach those entries; fable's consumer guard can. Conversely fable's guard alone leaves `irreducible_escalation`/`hil_escalated`/`hil_reason` asserting "a machine tried and failed" on an entry no ladder reached. **Neither dominates; the composition strictly dominates both on two named properties.** That is the founder's standard met by measurement, not by judgement.

All three seat falsifier scripts now exit clean:

```
falsifier_carveout_drains_a4        -> exit=0 :: CLEAN EXIT: the carve-out keeps A4 blocking
falsifier_subcritical_refusal_is_silent -> exit=0 :: CLEAN EXIT: no silent drain
falsifier_star_db_dc                -> exit=0 :: CLEAN EXIT: neither claim demonstrated
```

---

## PER-ASSERTION ADJUDICATION

| # | Assertion in dispute | cc2 | fable | **Decided for** | **Standard, and why** |
|---|---|---|---|---|---|
| 1 | **D-B: who names a sub-critical drain** | widen the one wired reader (`or status=="UNCONFIRMED"`) | add `integrity_refused_subcriticals()` + 2nd log line | **cc2** | **SIMPLEST SUFFICIENT.** Both discharge "excluded ⇒ reported". cc2 costs one disjunct, returns a strict superset (nothing reported stops being reported), and makes the invariant hold *by construction*. fable costs a second method, report key, log line, and holds the invariant only as the union of two scopes a later edit can drift apart. **COMPOSABILITY was tested and refused:** with the reader widened, every id the sibling returns is already named — composing prints the same id under two headings. No advantage over either alone ⇒ prefer the single fix. ADDITIVE is neutral (both wired). |
| 2 | **D-C: where the unobserved refusal is repaired** | at the **stamp** in `_apply_routing` | at the **consumer** in `unverified_critical_count` | **BOTH** | **COMPOSABILITY, demonstrated.** The 2×2 above. Stamp-alone fails the replay shape (A4→0); consumer-alone fails the record shape (`irreducible_escalation` True). The composition is the only cell passing both. |
| 3 | **D3: stale integrity stamps retracted** | absent | adds `integrity_refused`/`integrity_unobserved` to `clear_stale_resolution_stamps` | **fable** | **ADDITIVE.** Pure addition at two call sites that already fire only after a replacement falsifier verified CONFIRMED — which proves the gate passed *and* the observer installed. Removing it would need a measurement that something dominates; there is none. |
| 4 | **Forensics: `trusted_record_names` + `discover_run_root` + `run_root_recorded`** | identical | identical | **kept once** | Not a disagreement. Both seats converged on the same mechanism and the same four refusals (`/`, disagreement, non-runner-authored, pre-2026-09-01). |
| 5 | **Confinement test: live root only, or both roots** | live root only | both roots | **fable** | **ADDITIVE.** cc2's narrower form does not dominate: `resolve_target_dirs` already rescues a *relative* target record, but an **absolute** target recorded under the producing machine's repo root is under neither the live root nor any staged dir after relocation — so that code review is classified a confined exam, repo comes off the allowlist, and the 107-hit storm reproduces one archive shape further along. Removal would be removal-without-measurement. |
| 6 | **Counterpart lookup over both roots** | adds recorded-root fallback | absent | **cc2** | **ADDITIVE**, and it is the *opposite* failure direction from #5. Measured on run 1b from `/nonexistent/checkout/of/this/repo` pre-fix: audit **7 → 0**, every `carried_verbatim` flag lost, the whole audit channel emptied into the advisory. Neither pin fixes the other. |
| 7 | **`shell=True` per-token spawn check** | reported the hole | wrote `_spawn_path_tokens` | **fable** | **ADDITIVE.** Closes a real asymmetry (`subprocess.run('cat '+p, shell=True)` allowed, `['cat', p]` refused) with 0 false refusals over the committed honest-spawn corpus. |

**The one retirement, stated openly.** fable's `test_a_subcritical_refusal_is_named` asserts `integrity_refused_criticals() == []` for a sub-critical. The committed oracle `test_one_predicate_excludes_and_reports_2026-10-02.py::test_a_terminal_entry_is_neither_and_a_subcritical_one_IS_REPORTED` asserts `== ["C2","C3"]` with C2 at severity 0.1. **These cannot both hold** — it is a contradiction, not a preference, so one had to go on the merits. I retired the *implementation choice*, not the *requirement*: all four properties fable's class pinned are re-asserted against the single widened reader, each superseded line kept verbatim in a comment above its replacement, plus a new `test_no_second_reader_was_left_behind` so a future re-add trips the file rather than silently restoring two scopes. **No test was deleted to go green.**

**Two gate tests I had to add.** fable's widened confinement test (#5) was wired to a caller but **executed by no test** — this project's top defect class, 11 of 11. I added `test_an_absolute_target_under_the_recorded_root_is_a_code_review` (with a mutation control that neutralises `discover_run_root` and asserts the verdict flips to confined, so the guard cannot be the can't-fail shape mutation testing caught on 2026-10-02) and `test_an_exam_staged_outside_the_recorded_root_stays_confined` for the safety direction.

---

## THE TWO TEST-SUITE SUMMARY LINES

```
########## SEAT cc2 TEST SET (final) ##########
45 passed in 12.59s

########## SEAT fable TEST SET (final) ##########
27 passed in 3.81s
```

Pre-merge baseline for comparison: cc2 set **17 failed, 28 passed**; fable set did not even collect (`ImportError: cannot import name 'discover_run_root'`).

**Wider regression, committed neighbours: `131 passed`.** Full targeted sweep over all 36 test files naming any changed symbol: **492 passed, 9 failed** — and all 9 are **pre-existing**, verified by restoring the pre-merge sources and re-running (6 in `test_guard_false_positive_figures_2026-10-02.py`, byte-identical failures; 3 in `test_parked_measurements_still_run_2026-09-11.py`, which need `git status` and this sandbox is not a git repository). I did not touch them.

Proportions, three independent computations in agreement — statsmodels, mpmath to 30 dp, and Wolfram Language (local Wolfram Engine, via `wolframscript`):

| | | Wilson 95% |
|---|---|---|
| fable assertions needing retirement | 4/24 = 16.6667% | [6.6787%, 35.8531%] |
| cc2-set assertions red pre-merge | 17/45 = 37.7778% | [25.1081%, 52.3701%] |
| merged-set assertions red post-merge | 0/69 = 0.0000% | [0.0000%, **5.2737%**] |

That upper bound is the honest statement of what 69 green assertions buy: the true residual red rate could still be as high as ~5%.

---

## FILES DELIVERED, AT THEIR REAL PATHS

| File | Δ | sha256 (12) |
|---|---|---|
| `bench/reference_runner_v3.py` | +114 / −11 | `3b0b9ee810a8` |
| `bench/key_access_forensics.py` | +164 / −24 | `b046fea5bfdf` |
| `bench/falsifier_verify.py` | +30 / −1 | `d7979492f0f3` |

Eight test files installed at `bench/tests/*2026-10-03*` (both seats', from the sandbox harvest). Two edited, both transparently: `test_a4_scope_guards_2026-10-03.py` (TestDB class re-pointed at the single reader, superseded text preserved, +1 anti-drift test) and `test_forensics_run_root_pin_2026-10-03.py` (+2 gate tests with a mutation control). Pre-merge snapshot at `/tmp/premerge/`.

**One citation I corrected mid-merge and must declare.** My own first draft of the D-C comment cited `resume_from_state` as the restore path. **No such function exists** — I had written a plausible name instead of a measured one. I found it by grepping for it, got 0 hits outside my own comment, traced the real path (`--resume` → `FindingRegistry.from_dict`), read the body with `inspect.getsource`, and rewrote the comment. Had I not checked, the merge would have shipped a fabricated call-path citation inside the very fix whose argument depends on it.

---

## WHAT WOULD REFUTE ME

1. **A caller of `integrity_refused_subcriticals` outside the panel round.** I grepped and found only the one log line fable added. If an external consumer (dashboard, report schema, archive reader) keys on that method name, SIMPLEST SUFFICIENT flips to ADDITIVE and the second reader must be restored.
2. **A measured advantage for two advisory lines over one.** If an operator study showed the split headline materially changes triage, that is the demonstration COMPOSABILITY requires and I have none against it. I looked for one in both seats' evidence; neither offered a measurement, only a judgement.
3. **An exam archive whose staged targets sit *under* its recorded `run_root`.** fable's widened confinement test would then put the repository back in scope for an exam. I looked: exp48 records `run_root: None` so the pin is inert for it, and its targets are at `/Users/georgejackson/CDSFL_review_targets`, outside the tree. If such an archive exists, assertion #5 must be narrowed to cc2's form.
4. **A false refusal from `_spawn_path_tokens` in a real falsifier.** I ran the committed honest-spawn corpus (0 refusals) but that corpus is small. A production falsifier refused on an innocent token would overturn #7.

**What I looked for that would have changed my mind and did not appear:** I expected the two forensics fixes to conflict, since both rewrite `scan_run`'s confinement block. They do not — the seats converged on the same `trusted_record_names`/`discover_run_root` mechanism, and the two deltas (confinement scope, counterpart lookup) address **opposite failure directions** and are independent. I also expected cc2's `test_a_confined_exam_does_not_get_the_pin` to go red under fable's widened confinement test; I traced the fixture and it stages outside both roots, so it survives. The forensics "incompatibility" in the brief is, on execution, a union — not a conflict.

---

## STRONGEST DISAGREEMENT WITH THE BRIEF'S FRAMING

**"The 2 fixes disagree PER ASSERTION, not on one scope line" is right, but the brief's count is low and its diagnosis of the failed first composition is incomplete.** Dropping the severity gate from `integrity_refused_criticals` so its scope matches `unverified_critical_count` took cc2 from 6 reds to 5 — the brief reads that as evidence the disagreement is broad. It is better evidence that **the first composition dropped the wrong thing**. Dropping the gate outright makes the reader name *terminal* and *OPEN* sub-criticals the A4 counter never saw, which overstates. cc2's `or status == "UNCONFIRMED"` is a **disjunction, not a deletion**, and it is the difference between "matches the counter's scope" and "has no scope". The residual 5 were D-C and the forensics pin, which that edit never addressed.

**And the brief's premise that "BOTH readers are wired, so the additive standard does not decide it" is correct but under-read.** It does not follow that the standards are silent — SIMPLEST SUFFICIENT decides it cleanly, and COMPOSABILITY decides it *again*, in the same direction, because the composed form is strictly worse than either alone (duplicate reporting). Two of the three standards converge; this was never a toss-up.

## WHERE I THINK EACH SEAT IS WRONG

**fable.** (a) Its D-B reader is the wrong shape for the reason above, and its test actively pinned `integrity_refused_criticals() == []` — pinning the *narrowness* that was the defect, in a file whose stated purpose is to close a silent-exclusion gap. (b) Its citation correction to the run-1b comment is a **correct finding carried by wrong figures**: it quotes novelty tails `[.., 4, 8] / [9, 4, 5]`; the archive carries `novel_critical_history [6, 4, 5]` and `rho_novelty_counts [18, 6, 9]`. I adopted the finding and replaced the numbers with measured ones (`gamma_critical_history [0.0, 0.0, 0.336]`, `gamma_alt_consecutive_zero_crit` 3 against zero zero-critical rounds, `gamma_alt_earliest_round` 3 against `halted_at_round` 2). Replacing a false citation with an unverified one is not a repair. (c) It widened the confinement gate and wired **no test** to the widening — the exact defect class this project has shipped 11 times.

**cc2.** (a) Its D-C fix is at the right place but is **not sufficient alone**, and its own test cannot see that, because every fixture drives `_apply_routing` live — the replay shape is structurally invisible to it. (b) Its forensics confinement form leaves the absolute-target code review misclassified after relocation, which is the same defect it is fixing, one archive shape along. (c) Its claim that a sibling reader "would need its own caller, its own report key and its own round-loop log line to be reached at all" is true but is an argument from *cost*, not from *sufficiency* — fable **did** wire all three. The decisive argument is the one cc2 understates: with the reader widened, the sibling is redundant, so composing them duplicates output. cc2 won this assertion on a weaker argument than the one available to it.

---

## TERMINATION

A further pass produced no new above-threshold findings. The nine remaining red assertions in the wider sweep are pre-existing and confirmed pre-existing by restoring the pre-merge sources; they are out of scope for this merge and I did not touch them. The three categories I would still call open — an external consumer of the retired reader, an exam archive staged under its own recorded root, and the small honest-spawn corpus — are stated above as refutation conditions rather than as findings, because I looked for each and none appeared.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 51 recorded tool call(s).

<!-- verbatim-begin: fable (panel merge_adjudication_2026-10-03) -->

# MERGE ADJUDICATION — final report

## Verdict

**MERGED AND GREEN.** A single file set is delivered that passes both seats' falsifiers (all 3 exit clean) and both seats' test sets (45 + 24 passed), with 139 neighbouring committed tests unregressed. One of fable's assertions was **wrong, not inconvenient**, and is retired with its superseded text preserved verbatim; everything else composes or resolves per-assertion under the three standards.

## Reasoning

The two fixes disagree at four sites, and no single rule decides all four — which is why the first composition attempt (one scope line) only moved cc2's failures 6→5. Adjudicated per assertion:

| # | Assertion site | cc2's form | fable's form | Decision | Deciding standard |
|---|---|---|---|---|---|
| 1 | **D-B: who names the sub-critical drain** | Widen the one wired reader: `integrity_refused_criticals` gains `or status == "UNCONFIRMED"` | Second reader `integrity_refused_subcriticals()` + second advisory line; criticals reader asserted to stay narrow | **cc2** | SIMPLEST SUFFICIENT: both discharge "no silent exclusion"; one widened scope expression on the already-wired reader makes "whatever the counter drops, this names" hold *by construction*, vs. two scope expressions kept in sync by hand plus a new method and log line. COMPOSABILITY refuses keeping both: no committed measurement shows the two-reader form dominating on any named property, and under the widened reader fable's `integrity_refused_criticals() == []` becomes logically false, not just structural. |
| 2 | **D-C: where the unobserved carve-out is enforced** | At the stamp: `_apply_routing` routes an unobserved refusal into the equipment-failure branch (`routing_deferred`, never a false `irreducible_escalation`/`hil_*`) | At the consumer: `unverified_critical_count` skip gains `and not integrity_unobserved` | **BOTH (composed)** | COMPOSABILITY, with the demonstration executed: the stamp fix alone cannot reach entries *already* carrying the stale stamp (archived registries written by pre-fix code — fable's TestDC constructs exactly that state and went red under cc2 alone); the consumer guard alone leaves routing writing false `irreducible_escalation`/`hil_reason` assertions onto the record (cc2's stamp tests went red under fable alone). Mutations A and B below show each half is load-bearing on the merged tree — neither is an addition nothing reaches. |
| 3 | **D3: stale `integrity_refused`/`integrity_unobserved` stamps** | — (not addressed) | Join `clear_stale_resolution_stamps` | **fable** | ADDITIVE: wired (called at both rescue sites), executed by TestD3, conflicts with nothing. |
| 4 | **Gamma citation in `_irreducible_queue_split`** | — | Comment correction: run 1b's count-side never held | **fable, minus its figures** | I re-verified against run 1b's own report: `gamma_critical_history [0.0, 0.0, 0.336]` and `novel_critical_history [6, 4, 5]` — the claim is CONFIRMED, but fable's bracketed figures ("[.., 4, 8] / [9, 4, 5]") do **not** match the record and were dropped from the merged comment. |
| 5 | **Forensics run-root pin** | `trusted_record_names` + `discover_run_root` + allowlist pin gated on `not confined` + **dual-root `_committed_counterpart` lookup** | Same core, plus recorded root added to the `confined` test itself, **no** counterpart fix | **cc2 wholesale** | SIMPLEST SUFFICIENT + the executed measurement: cc2's file passes *both* seats' forensics tests (fable's lacks the counterpart fix, which is why `test_the_audit_channel_survives_relocation` and the 7/0/7 split went red under fable alone). Fable's confined-test widening is pinned by no test — under ADDITIVE it is an addition nothing reaches, so it is not carried. |
| 6 | **Spawn-blob token pass in `falsifier_verify.py`** | — (not delivered) | Per-token path check under `shell=True` | **fable wholesale** | ADDITIVE: only fix for a confirmed defect; `test_falsifier_cannot_read_the_key.py` (in the 139) shows 0 false refusals on honest shapes. |

**The retired assertion.** Fable's `test_a_subcritical_refusal_is_named` asserted `integrity_refused_criticals() == []` for an UNCONFIRMED sub-critical refusal. Once the structure is decided at site 1, that assertion pins the report to a scope *narrower than the counter it exists to mirror* — the exact shape of defect D-B itself. It is retired in the delivered `test_a4_scope_guards_2026-10-03.py` following the project's own amendment convention (superseded assertions preserved verbatim in the docstring, justification citing the standards); the *intent* of every retired assertion — drain named, no overstatement — is re-asserted against the single reader (OPEN sub-crit not named; unobserved not named; verdict-route named). Nothing was silently deleted. The evidence copies under `experimental_notes/seat_evidence/` are untouched.

## Falsifiers and executed results

All three seat falsifiers, re-executed on the merged tree (tools decide):

```
falsifier_subcritical_refusal_is_silent_2026-10-03.py : CLEAN EXIT (0)  — sev 0.5: A4 1→0 AND reported=['C0001']
falsifier_carveout_drains_a4_2026-10-03.py            : CLEAN EXIT (0)  — A4=2, converged refused, no false irreducible stamp
falsifier_star_db_dc_2026-10-03.py                    : CLEAN EXIT (0)  — "neither claim demonstrated"
```

Plus my own mutation falsifiers proving each composed half binds (executed, then reverted):
- **A** (strip consumer guard): `TestDC::test_the_carveout_reaches_the_a4_consumer` + `test_convergence_is_refused_under_observer_failure` **FAIL** → guard is load-bearing for archived state.
- **B** (strip stamp disjunct): `test_an_unobserved_refusal_is_not_called_ladder_exhausted` **FAIL** → stamp fix is load-bearing for the record's truthfulness.
- **C** (re-narrow reader): 5 tests **FAIL** across both suites → the widened scope is pinned from both sides.

## The two summary lines

```
cc2 set   (test_one_predicate…, test_key_access_advisory…, test_an_unobserved_refusal…, test_forensics_verdict…): 45 passed in 13.08s
fable set (test_a4_scope_guards…, test_spawn_blob_tokens…, test_forensics_run_root_pin…):                          24 passed in  3.84s
```

Regression: 139/139 neighbouring committed tests pass. Pass proportions 69/69 and 139/139, Wilson 95% [0.9473, 1.0000] and [0.9731, 1.0000] (statsmodels; the 69/69 interval independently confirmed as {0.947263, 1.} — computed with Wolfram Language, local Wolfram Engine).

## Files delivered (sandbox tree, real paths)

- `bench/reference_runner_v3.py` — D3 retraction (fable) + citation correction (fable, figures corrected against the record) + consumer guard (fable) + widened `integrity_refused_criticals` (cc2) + stamp-side equipment-branch disjunct and defer-reason classification (cc2). Composition rationale written at each site.
- `bench/key_access_forensics.py` — cc2's version wholesale.
- `bench/falsifier_verify.py` — fable's version wholesale.
- `bench/tests/`: `test_a4_scope_guards_2026-10-03.py` (TestDC/TestD3 verbatim fable; TestDB amended, superseded assertions preserved), plus verbatim copies of `test_an_unobserved_refusal_keeps_a4_blocking_2026-10-03.py`, `test_forensics_verdict_is_a_fact_about_the_run_2026-10-03.py`, `test_forensics_run_root_pin_2026-10-03.py`, `test_spawn_blob_tokens_2026-10-03.py`, and the three falsifier scripts.

## What would refute this merge

1. **An archived registry or a committed measurement** showing the two-reader report form dominating the widened single reader on a named property (e.g., a downstream consumer that must distinguish severity bands and cannot from the ids) — that would reopen site 1. I looked for any caller or archived artefact consuming a severity-banded advisory and found none.
2. **A real relocated-scan archive whose target dirs are absolute paths inside the producing repo** — cc2's forensics would call it confined where fable's would not. I looked: run 1b records *relative* target dirs (resolved against the scanner's root) and exp48 stages outside the repo, so no archived run exercises the difference. If one appears, fable's `_scope_roots`-in-confined-test semantics should be revisited *with a test*.
3. Any run of the two suites or three falsifiers on this tree producing a different result than quoted — the commands are above and reproducible.

## Strongest disagreements

**With the brief's framing:** "a single merged file set that passes BOTH seats' falsifiers" was achievable; "passes both seats' *test sets* verbatim" was **not**, and the brief half-acknowledges this without saying it: fable's `integrity_refused_criticals() == []` and cc2's amended committed oracle `== ["C2","C3"]` are logically contradictory on the same input. No merge satisfies both. The deliverable necessarily includes a retirement, and the brief would have been sharper stating that the contradiction, not the incompatibility, is the thing to adjudicate. Also, the brief's "BOTH readers are wired, so the additive standard does not decide it" is right but incomplete — additive is silent, *simplest-sufficient* decides, and composability's "prefer the single fix where it performs as well" independently refuses the both-readers escape hatch.

**With fable's fix:** the second reader was structure defending an archived oracle ("keeps the committed oracle intact") that cc2 had meanwhile *correctly amended* — the oracle's narrow scope was itself the pinned defect. Defending a wrong assertion's stability is not a property worth a second scope expression. Separately, fable's citation correction contained unverifiable figures ("novelty tails [.., 4, 8] / [9, 4, 5]") that do not match run 1b's record (`novel_critical_history [6, 4, 5]`) — a corrected citation carrying its own failed citation.

**With cc2's fix:** "THE FIX IS AT THE STAMP, NOT IN THE COUNTER" is overstated as an either/or. The stamp fix cannot reach state it didn't write — archived registries stamped by pre-fix code are exactly the input `unverified_critical_count` will be handed on resume, and cc2's own D3 gap (no retraction of integrity stamps) left that state live. Mutation A proves the consumer guard does real work on the merged tree. cc2 also left the spawn-blob defect it first reported for fable to fix, and shipped no D3 at all.

**Termination:** a further pass over the merged tree (mutations A–C, the 139-test regression sweep, the record-level verification of the citation) produced no new above-threshold findings. Converged.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/merge_adjudication_2026-10-03/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
