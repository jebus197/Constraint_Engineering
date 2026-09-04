# Panel Review — Verification of Four Changes, and Three Open Questions — FULL RECORD

**2026-09-04 22:15 BST.** Dispatched 2026-09-04 21:31 BST at `5a0f20c`. Two reviewers, sandboxed
in disposable linked worktrees, Max-plan, no metered cost.

| Reviewer | Elapsed | Tool calls | Reply |
|---|---|---|---|
| cc2 (opus) | 1940s | 85 | 24,064 chars |
| fable | 1180s | 96 | 13,108 chars |

Brief: `bench/logs/panel_verify_20260904T203042Z/BRIEF.md`.

## Outcome, and what was done about it

Both reviewers CONFIRMED C3 and C4. cc2 returned REFUTED-WITH-FIX on C1 and C2;
both reviewers REFUTED the suite claim independently. Every refutation was
reproduced here before acting, and all are fixed in `1928de4`.

**The two reviewers DISAGREE on the disposal of the S_k gate, and the
disagreement is preserved rather than smoothed.** Fable: repair it, since the
repair is replay-neutral. cc2: remove it, because the hard-gate conjunction `A`
rejects 9.7% while `S*` rejects 0.0% of what `A` passes, so `A` is the real
Valley-of-Bad-Fixes gate. That needs a founder ruling.

Reproduced verbatim and unfiltered below.

---

# REVIEWER: cc2

# CDSFL PANEL REPORT — verification by execution

Working copy: `cdsfl_panel_x_e8jab6/repo` @ `5a0f20c`. All mutations reverted; tree clean at exit.

---

## PART 1

### C1 — key collision (`:.1f` → `:g`) — **CONFIRMED, with a residual hazard**

Reverted the fix at both sites and re-ran:

| | new executing test | old source-text test |
|---|---|---|
| fixed | 5 passed | 8 passed |
| reverted to `:.1f` | **4 failed, 1 passed** | **8 passed** |

Claim reproduced exactly. The one new test that survives the revert is `test_it_returns_false_for_a_band_sensitive_registry` — it passes *vacuously*, because the bug pins the verdict to `False`. Alone it is no better than the grep it replaced; `test_both_outcomes_are_reachable` is what actually carries the discrimination. Worth knowing which of the five is load-bearing.

**Is `:g` right? Not quite — it trades a certain collision for a rarer one.** `:g` is 6-significant-figure formatting, and it drops trailing zeros. Executed against the live function with an extended threshold tuple:

```
in : (0.5, 0.65, 0.75, 1.0, 0.6150000001, 0.615)   → 6 thresholds
out: ['0.5', '0.615', '0.65', '0.75', '1']          → 5 keys
```

Two failures this project could plausibly hit:
- **`1.0 → "1"`.** The prereg tuple already runs to 0.8; extending it to 1.0 (the natural "criticals only at the ceiling" probe) produces key `"1"`. Any consumer written as `.get("1.0")` gets `None` — *the identical failure mode just fixed*, from the same producer/consumer string coupling.
- **6-sigfig truncation collides** `0.615` with `0.6150000001`, which is what an `arange`/linspace-generated sweep produces.

**REFUTED-WITH-FIX:** use `repr(float(thr))` instead of `f"{thr:g}"`. `repr` is round-trip-unique for every float — collision-free by construction, and `repr(0.65) == "0.65"`, so the two hardcoded consumer lookups keep working unchanged. The deeper fix is to stop keying by string at all, but `repr` costs one character and closes the class.

### C2 — the occasions record — **REFUTED-WITH-FIX**

The narrow claim survives: I grepped all 16 `source_model` sites in `reference_runner_v3.py` and every site elsewhere; nothing reads `occasions`, no decision path touches it, and no verdict can move today. **But the record is being written wrong, in a way that violates this project's founding principle.**

**The carry runs before the tool-only enforcement.** Executed:

```
reg.resolve(dupe, "MERGED", merged_into=keep, adjudicator="model")
  → dupe status      : WITHHELD        (MERGED is TOOL_ONLY; the merge was REFUSED)
  → dupe merged_into : None
  → merge_candidate  : C0001
  → TARGET occasions : 2 entries, the second tagged
                       {'via':'merge', 'merged_from':'C0002', 'merged_round':1}
```

The runner refused the merge, and the target *still* permanently gained the duplicate's occasion, labelled as a merge that never happened, pointing at a `merged_from` that was never merged. The block sits at line ~1795, above the `adjudicator == "model"` check at ~1815. A model's unverified assertion of duplication writes into the overlap record — votes deciding, not tools. Since the whole point of `occasions` is to feed mark-recapture coverage estimators, this inflates exactly the recapture count those estimators are most sensitive to.

The test file's own fourth class is titled *"A merge the guards refuse must not carry occasions either"* and covers self-merge and phantom-target — both of which return early, above the carry. It does not cover the refusal that happens *below* it. **Fix: move the carry block to after the enforcement, keyed on the post-substitution `merged_into`.**

**Dedup key: `(model, round, alias)` can collide.** Executed — one model, one round, the same `finding_id` reused for two genuinely different defects:

```
C0001 (target) ← merge C0002 "null deref in parser"  (Fable, r1, alias 'dup')
              ← merge C0003 "race in scheduler"      (Fable, r1, alias 'dup')
occasions on target: 2, not 3.
```

Three distinct canonicals, two occasions. The registry itself mints separate canonicals for these (it does not treat ID reuse as absorption — there is a test file named for that), so the dedup key is *stricter* than the registry's own identity notion. The key should be `canonical_id` (or `(model, round, canonical_id)`), which is unique by construction. Direction of error is undercount, so it biases coverage *down* — the opposite of the refused-merge bug, which biases up. Both should be fixed; they do not cancel.

### C3 — netguard markers — **CONFIRMED**

The marker is read in exactly two places in `conftest.py`. Neither touches `install_netguard`, `uninstall_netguard`, or `set_free_window`. One un-skips `network`-marked tests at collection (these four carry no `network` marker, so no effect); the other returns early in the teardown fixture, waiving only the auto-fail. Enforcement is structurally untouched.

Executed, in-process, with the window open:

```
popen paid  -> FileNotFoundError | CDSFL netguard denied subprocess -> curl
popen free  -> FileNotFoundError | CDSFL netguard denied subprocess -> curl
connect ip  -> ConnectionError   | CDSFL netguard denied tcp -> 172.66.0.243
dns paid    -> gaierror          | CDSFL netguard denied dns -> api.openai.com
```

All four denied, by the guard, with the guard's own message. Under `--netguard-strict` the file is 18 passed and the terminal summary lists all four attempts as denied. The money guard holds.

**One note, not a refutation.** `test_curl_to_a_FREE_host_is_also_denied_inside_the_window` uses a bare `pytest.raises(Exception)` with no message assertion, and the Popen guard raises `FileNotFoundError` — the same exception an absent `curl` produces. That one test would pass green on a box without curl even with the guard removed. Its three siblings assert on the message; give it the same assertion.

### C4 — grep converted to execution — **CONFIRMED**

Removed `Bash` from the argv, left the word in the file, kept syntax valid:

```
SYNTAX VALID: YES
GREP TEST ("--allowedTools" in src and "Bash" in src): True   ← old test PASSES
EXECUTING TEST: E  assert 'Bash' in ['Read', 'Grep', 'Glob']  ← new test FAILS
```

Exactly the claimed discrimination. (Minor: `granted = argv[i+1:]` takes everything after the flag, so a later unrelated argv element containing `Bash` would false-pass. `argv[i+1:i+5]` or a set-intersection would tighten it.)

### Suite claim — **REFUTED**

`python3 -m pytest bench/tests/ --netguard-strict -q`:

```
2 failed, 4864 passed, 4 skipped, 18 warnings in 847.69s
```

Not `4870 passed, 0 failed, 0 errors`. Collection total matches (4870), but the claim omits 4 skips and 2 failures. **Both failures are artefacts of the disposable copy, not code defects — I verified each:**

1. `test_the_sandbox_flag_distinguishes_the_two_cases` — asserts `(REPO/".git").is_dir()`. Here `.git` is a 92-byte *file*: this copy is a linked worktree. `git worktree list` confirms it. The test assumes the canonical repo is never itself a worktree; that assumption is false in the very environment the panel is run in, which is worth fixing given this test file exists to reason about worktrees.
2. `test_the_committed_ledger_matches_bench_logs` — drift is one line, the "12 aborted invocations wrote an empty directory" sentence. Those 12 directories are empty; git cannot track empty directories, so they do not exist in a worktree checkout and the regenerator finds zero. Environment, not drift.

So the *substantive* claim ("nothing is broken") stands; the *stated* claim does not reproduce. Report it as `4864 passed, 4 skipped, 2 environment-conditional failures` and it becomes reproducible.

---

## PART 2

### Q1 — the S_k gate: **redundant, and repairing it is provably inert. Third reading.**

I reproduced both routes and then went past them, and the extra measurement changes the answer.

**The two stated routes, checked.** Parsing all 7,544 JSON artefacts: `passes_threshold` is `true` 3,601 times, `false` **0** times. (The brief says 3,816; I get 3,601 across `.json`, and 0 in `.jsonl`. The count does not reproduce; the material claim does.) The single `false` string in the tree is the brief's own text. The log-line route needs care: a naive grep for `REJECTED sk=` returns **39**, not 0. All 39 are inside `model_responses` / `turns[].content` — panellists quoting the runner's own f-string source with `{cid}` unexpanded. Zero are emitted lines. Claim stands; the method as written would have failed a less careful reader.

**The Wilson CI is the wrong instrument, and it is the same error C1 just fixed.** This is not a rare event with sampling uncertainty. At every reachable configuration, the gate is a tautology:

```
sk values in [0,1] at 1e-5 resolution that FAIL the gate: 0 / 100,001
  sk=-1e9  -> (True, 0.0)      sk=inf -> (True, 0.0)
```

`S* = -1/19` exactly (confirmed via `Fraction`), clamps to 0; `sk` is itself clamped to `[0,1]`; `s_floor` is `0.0` in every config file in the repo; `model_params` has no production writer (one test fixture only); and `R_old` is `0.5` in **all 3,601** archived decisions with `rk0_source` absent. So `passes = sk >= max(0,0)` is `True` for every possible input, including infinity. Reporting `[0.0000, 0.0010]` says "could fire about 1 in 1000". The truth is "cannot fire". A constant wearing the costume of a measurement — in the brief's own statistics, four days after the panel fixed that exact species.

**The decisive new measurement: repairing the threshold changes nothing.** I extracted every archived `S_k` score and re-ran the gate at the correct σ-dependent break-even (I independently reproduced `0.5049311709704233` by root-finding at 40 dp — the brief's constant is right):

```
archived S_k with a threshold decision: 3601
  min 0.7400   p10 0.9333   median 1.0000   max 1.0000
  at S* = 0.504931 (true break-even): REJECT 0 / 3601 = 0.00%
  at S* = 0        (as shipped)     : REJECT 0 / 3601 = 0.00%
```

**Minimum observed S_k is 0.74.** The correctly-parameterised gate rejects nothing either. Two consequences:

- The founder's concern that repair is behavioural — "changes which fixes are accepted, which invalidates replay of archived runs" — is **empirically unfounded across all 29 archived runs**. The repair is a no-op on the entire corpus. Replay is safe. That concern should be retired.
- "It needs tightening to become accurate" is **refuted by execution**. Accuracy is achievable; consequence is not. You would be repairing an instrument that would still never move.

**Why it can never fire — the structural reason, which is the answer to the founder's question.** `sk = A * E`, and the threshold branch is reached only when `tristate == SK_ADMISSIBLE`, i.e. `sk > 0`, i.e. `A == 1`. The population arriving at the threshold is *pre-filtered by the hard-gate conjunction*. Across the archive:

```
tristate: ADMISSIBLE 3601 | REJECTED 515 | ESCALATE 1172
A: 1 → 3601   0.0 → 1687
REJECTED by the hard-gate conjunction A : 515 / 5288 = 9.7%
REJECTED by the S* threshold            : 0 / 3601 = 0.0%
```

And `E` is a *renormalised weighted arithmetic mean over gates that already passed*, so it is bounded below by the weakest surviving gate score — empirically 0.74, and exactly 1.0 in 2,472 of 3,601 cases.

**My answer: redundant, remove it — and this is the founder's reading, but reached for a different and sharper reason than the one offered.** The zero fire rate is *not* evidence that upstream discrimination is working; a tautology corroborates nothing, and would read zero against garbage input. What *is* evidence is the pair above: `A` rejects 9.7% and `S*` rejects 0.0% of what `A` passes. The hard-gate conjunction is the real Valley-of-Bad-Fixes gate. `S*` is a second gate over a population the first has already cleared, and its input has no mass below its own break-even.

The honest disposal is not silent deletion. Delete `check_sk_threshold` from the decision path, and record in the appendix that the Valley criterion is *enforced by `A`, not by `S*`*, with these numbers attached — otherwise the appendix keeps claiming a σ-dependent break-even that no code implements and no data would ever reach. Keep the σ-dependent formula as documented theory; do not pretend it is running.

**A caveat I cannot resolve by tool:** `E`'s distribution is suspicious in its own right — 69% of scores are exactly 1.0. That may mean the effect gates are themselves saturated and uninformative, in which case `A`'s 9.7% is the *only* discrimination in this whole pipeline. That is a separate investigation and I did not run it.

**What would change my mind:** a single archived or constructed run in which an `A == 1` fix scores `S_k < 0.5049`. One such case makes the gate non-redundant and repair worth doing. I found zero in 3,601. Also: evidence that `model_params` or `sk_s_floor` is written by any live launcher — I found none, but I searched this repo, not every operator config that has ever existed.

### Q2 — simplicity/sufficiency: **new mathematics, no; new machinery, yes — one gate, and it is not the one proposed**

**I verified the foundation, and it is stronger than the brief states.** The brief reports "residual exactly 0 for n=1..8, and the induction step is exactly 0". That is a numerical spot-check plus a recursion argument for something that needs neither. Under K=1 (so w=1), d_i=1, p_ik=p, π=1/2:

```
sympy:  (π·m)/((1−π) + π·m) − (1−p)^n/(1+(1−p)^n)  ≡  0
        for symbolic n and symbolic p.  is identically zero: True
```

`m_k = (1−p)^n` substitutes directly into the appendix's line-71 posterior and the ½s cancel. It is a one-line algebraic identity, closed for all n and all p simultaneously — no induction, no n=1..8, no mpmath at 30 dp. The reduction property is true; the *verification* that was performed is weaker and more elaborate than the theorem deserves. That is itself a datum about the criterion under discussion: the panel treated a compressive simplification as if it needed sampling, when proof was one `simplify()` away. **Sampling can refute a simplification but can never admit one — and it also cannot tell you when it wasn't needed.**

**New mathematics: no, and I agree with the 2026-09-04 panel, for their reason.** A reduction property is a theorem *about* the equation. Folding it in makes the equation piecewise and destroys the collapse that the property is asserting. There is no term to add. The criterion as stated — "S and F agree across a scope D declared before either was proposed; residual empty, or named, bounded and filed as its own claim" — is already a proof obligation, and proof obligations do not live inside state equations.

**But "a named definition plus one policy sentence" is decoration**, and I part company with the prior panel there — the founder is right to push. A definition in an appendix changes nothing about model output. The distinction earns its place only if it changes what the *runner* does with a model's claim. And there is a precise thing it should change, which the prior panel's "execution gate" proposal misses:

> **Reductions must be discharged, not sampled.** When a finding or fix asserts that form S and form F agree across scope D, the runner must attempt symbolic/exhaustive discharge *first*. Only on failure does it fall back to sampling — and a sampled result may then only be recorded as REFUTED or as UNDISCHARGED. Never as CONFIRMED.

That is not a policy sentence; it is an asymmetry in the verdict vocabulary, and it is exactly the project's existing `TOOL_ONLY_STATUSES` shape applied one level up. It is also directly falsifiable against this repo's own history: the reduction property *was* admitted on sampled evidence (n=1..8 at 30 dp), and the right answer was a `simplify()` call. Under this rule that admission would have been refused, the discharge attempted, and the theorem obtained. The rule would have improved the output of this very project, this week. That is why it is not decoration.

**On the composition question: the two axes do compose, and the gate is the one that carries the mathematics.** The gate is what forces the criterion to be *applied*; the criterion is what tells the gate which verdicts are reachable from which evidence. Neither alone does the job — a gate without the asymmetry admits sampled agreement, and the asymmetry without a gate is a paragraph.

**Where I'd apply the concrete cost/compressive distinction inside CDSFL right now:** Q1's finding is a *cost* simplification masquerading as a compressive one. Deleting `check_sk_threshold` makes the artefact smaller. It captures no structure. The compressive version of the same move is the record I asked for above: "the Valley criterion is enforced by A; S* is subsumed, here is the distribution that shows it." Same deletion, but it now states something with reach — it predicts what any future gate over an `A==1` population will do. The criterion is what distinguishes those two, and this is a live case, not a hypothetical.

**What would change my mind:** show me a proposed simplification in this project's history where symbolic/exhaustive discharge was infeasible *and* sampled agreement turned out to be correct and load-bearing. That would mean the asymmetry costs more than it buys. I did not find one; I checked one case (the reduction property) and it fell the other way.

### Q3 — the human queue: **~82% of the disputed band is already tool-decided**

I reproduced the headline exactly. Using `rubric_adherence_audit_0C8_2026-09-02.json` and the live `CRITICAL_SEVERITY_THRESHOLD = 0.7`:

```
judgeable 259 (286 − 27 UNJUDGEABLE), agree 141 = 54.44%, Wilson [48.4%, 60.4%]
  (sensitivity: at 0.65 → 63.7%; at 0.75 → 36.3%)
```

Then I resolved all 286 audit items back to their live registry entries — 286/286 matched — and applied a **correction the brief does not make.** The audit spans 29 runs; only 12 of them predate nothing, but **186 of 286 entries come from runs whose schema has no `falsifier_verdict` field at all**. Counting those as "no falsifier" would be a schema artefact, not a measurement. Restricting to the 100 falsifier-era entries:

```
FALSIFIER-ERA judgeable: 81   agree 48   DISAGREE 33 (40.7%)

DISAGREEMENTS (n=33) — the population the pre-registration routes to rubric-or-human:
  A  already tool-settled (runner re-executed a falsifier)  27  81.8%  Wilson [65.6%, 91.4%]
  B  settled by merge (duplicate; the parent's verdict governs) 2   6.1%
  C  instrument fault (ERROR/UNTOOLABLE)                     0   0.0%
  D  no falsifier produced at all                            4  12.1%  Wilson [4.8%, 27.3%]
```

**Answer: roughly 88% of the disputed band is programmatically decidable and needs no human — 82% is already decided.** The genuine remainder is 4 of 33.

**The separating test, stated so it can be run.** Not a judgement, a lookup already in the schema:

1. `falsifier_verdict ∈ {CONFIRMED, REFUTED}` → **decided.** The runner re-executed it. Rubric/numeric disagreement about *severity labelling* is downstream of a settled existence question; it cannot reach the queue.
2. `status == MERGED` → **decided.** The parent's verdict governs; adjudicating a duplicate twice is double-counting.
3. `falsifier_verdict ∈ {ERROR, UNTOOLABLE}` → **not human — equipment.** The existing equipment-failure guard already routes these to re-instrumentation. Sending a broken instrument to a person is queue inflation of the exact kind the founder forbids.
4. No falsifier and none commissionable → **queue.** 4 of 33 here.

Two of the pre-registration's five clauses are additionally machine-decidable outright and should be pulled out before any queueing: **clause 5, Unreproducibility** ("an accepted result that cannot be reproduced from the logged inputs and fixes") is a replay, which this runner can already do; **clause 3, Verification-integrity corruption** ("a bug that changes the *measurement* of convergence") is precisely the class a falsifier targeting the accounting settles — C1 and C2 in this very brief are clause-3 findings, and both were settled by execution, by me, in this session. Neither should ever have reached a human as a *judgement*; they reach a human as a *decision*, which is different.

**The 54.4% is being read as a defect. It is not.** The two blind readers agreed with each other at κ=0.837 while each agreed with the number ~55%. That is not reader noise and it is not rubric failure — it is the correct finding that **a scalar severity in [0.65, 0.75] does not encode a five-clause consequence taxonomy**, and no threshold on it ever will. Tightening the threshold cannot help; the sensitivity sweep above shows agreement moving from 64% to 36% as the threshold moves, with no maximum inside the band. The right conclusion is that the numeric proxy should not be adjudicating consequence at all in this band — the falsifier verdict already does the work for 82% of it.

**The founder's selection rule — "prefer the solution matching the simplicity/sufficiency formalisation most exactly" — is operable, but only as a tie-break, and it is not needed here.** As stated it has a gap: it presumes both candidate solutions are *admissible*, and admissibility is the prior question. Applied properly to this case:

- *Candidate 1: send the disputed band to a human.* Scope D = the 33 disagreements. Residual = 33. Nothing is captured; the artefact is not smaller and reaches nothing.
- *Candidate 2: apply the four-way lookup above.* Scope D = the same 33, declared before the partition was computed. Residual = 4, **named and bounded** — the four entries with no falsifier. That is a compressive simplification: a short rule with wide reach, whose residual is filed as its own claim ("commission falsifiers for these four").

Candidate 2 wins on the criterion. But it also wins outright on correctness, so the tie-break never binds. **That is the honest test of the rule: it agreed with the answer I already had, which means I learned nothing from it here.** I would not yet claim it is load-bearing. It becomes load-bearing the first time two *equally correct* solutions differ in residual, and I have not seen that case.

**What would change my mind:** find me 5 items among the 27 tool-settled disagreements where the falsifier verdict is right about existence but a human's clause judgement would still have changed the run's outcome. That would mean the falsifier verdict does not subsume the severity dispute, and the 82% collapses. Also: my falsifier-era restriction cuts n from 118 to 33 — the wide Wilson bound [65.6%, 91.4%] is real, and re-running this on the next 100 falsifier-era findings is the cheap way to tighten or break it.

---

## Summary

| | verdict |
|---|---|
| C1 `:g` fix | CONFIRMED; **REFUTED-WITH-FIX** on the format choice — use `repr(float(thr))` (`1.0 → "1"`, and 6-sigfig collisions) |
| C2 occasions | narrow claim CONFIRMED (no verdict moves); **REFUTED-WITH-FIX** — carry runs *above* the tool-only refusal, so a model's unverified merge writes the overlap record; dedup key collides on reused `finding_id` |
| C3 netguard markers | **CONFIRMED** — all four denied by the guard, enforcement structurally untouched |
| C4 grep → execution | **CONFIRMED** — reproduced exactly |
| suite `4870 / 0 / 0` | **REFUTED** — `4864 passed, 4 skipped, 2 failed`; both failures are worktree-copy artefacts, verified |
| Q1 | gate is a **tautology, not a rare event** (Wilson CI inapplicable); repair rejects **0/3601** at the true break-even (min S_k = 0.74); redundant because `A` rejects 9.7% upstream — **remove, and record why** |
| Q2 | reduction is a symbolic identity for all n, p (stronger than claimed); **no new term**; machinery = *reductions must be discharged, not sampled* — sampled agreement may record REFUTED or UNDISCHARGED, never CONFIRMED |
| Q3 | **27/33 (81.8%) of falsifier-era disputed-band disagreements are already tool-settled**; genuine queue = 4/33; separating test is a 4-way schema lookup, not a judgement |

---

# REVIEWER: fable

All verification complete. Report follows.

---

# PANEL REPORT — jebus.2504, 2026-09-04

## PART 1 — VERDICTS

### C1 — key collision: **CONFIRMED**
Ran, not read. As shipped: 5/5 new + 8/8 old pass. Reverted `:g`→`:.1f` at both sites (sed, verified 2 substitutions): **4 of 5 new assertions fail, old source-text file still passes 8/8** — exactly as claimed. The test discriminates; the old one provably cannot.

Is `:g` right? Yes for anything this project would plausibly adopt: I formatted all six `PREREG_GAMMA_PROFILE_THRESHOLDS` plus 0.55/0.625/0.675/0.725 and the noisy `0.6500000000000001` — all exact ("0.65", not "0.7"); `:g` even *heals* float noise. The residual hazard is not `:g` itself but the **consumer's hardcoded literals** `"0.65"`/`"0.75"` at runner:6335-6336: adopt a band edge whose `:g` form differs from its written literal (e.g. `2/3` → `"0.666667"`) and the identical producer/consumer-disagree defect returns. Derive the lookup keys through the same formatter. Minor; not a refutation.

### C2 — occasions record: **CONFIRMED**
Repo-wide grep for every read of `occasions` (`.get`, `[...]`, both quote styles): written at `register` (:1687), carried inside `resolve` (:1795-1805), read **only by its own test**. The carry runs after the merge guards and cannot change the merge decision; `git diff 8bc32a9..HEAD` shows the only `source_model` lines touched are comments. Its 9 tests pass. The "purely additive, cannot move a verdict" claim holds.

Two nits. (1) The comment says "12 live consumers"; I count **11** read sites in the runner. (2) Dedup key `(model, round, alias)`: two genuinely distinct reports collide only if one model reuses one finding_id in one round and both are merged into the same target — but the merge itself already declared them one defect, so no distinct occasion is lost; what *is* silently dropped is the second merge path's `merged_from` provenance, count unaffected. Watch `getattr(finding, "round_idx", 0)`: if `round_idx` is ever absent, cross-round same-ID reports collapse to round 0 and would dedup wrongly. Key is right today; that default is the fragile edge.

### C3 — netguard markers: **CONFIRMED**
The marker is consulted at exactly two places: the `_netguard` teardown fixture (:563, early return before the fail) and the collection skip opt-out (:502). It appears **nowhere** in `_guard_getaddrinfo` / `_guard_connect` / `_guard_popen_init` — enforcement never reads markers; the only enforcement bypass is `CDSFL_ALLOW_LIVE_DISPATCH=1`, orthogonal to this change. Executed both directions: with markers, the 4 tests pass under `--netguard-strict` and the summary reports all 4 attempts **DENIED** (subprocess:curl ×2, tcp ×1, dns ×1); with one marker stripped, the attempt is *still denied*, the test still passes, and the teardown ERROR returns. Denial is intact; only the auto-fail is waived. This one is sound where it protects money.

### C4 — grep converted to execution: **CONFIRMED**
Reproduced the P-pass verbatim: removed `"Bash"` from the shim's argv list, `ast.parse` clean, `"Bash"` remains ×2 in source so the grep-style check passes — and the executing test fails at `assert "Bash" in granted`. Restored: 14/14 pass. The interception is at `SHIM.subprocess.run`, so an argv path bypassing `subprocess.run` would evade it; none exists in the shim.

### Suite claim: **REFUTED AS STATED — confirmed in substance**
Measured under `--netguard-strict`: **4864 passed, 2 failed, 4 skipped, 0 errors, 619.5 s** (4870 collected — the claimed number is the *collected* count). Both failures are provisioning artifacts of this disposable copy, mechanisms verified:
1. `test_the_sandbox_flag_distinguishes_the_two_cases` asserts `REPO/.git` is a **directory**; this copy is a linked worktree with a 92-byte `.git` *file* — the test failing is its own subject matter working.
2. Ledger drift: regenerating the ledger here omits the "12 aborted invocations" footer because those runs left **empty directories, which git does not materialise** in a worktree; the committed ledger keeps the footer → mismatch.

Both plausibly pass in the canonical checkout. Zero non-environmental failures found. But "4870 passed" was not observed and, with 4 skips in this environment, cannot be — report the author's line as unreproduced-exactly.

---

## PART 2

### Q1 — the S_k gate: **third reading, with numbers**

The stated cause reproduces on every checkable digit. Algebraically (exact, by hand + sympy): the code's S* is *identically* the condition `nu_eff(s_k) ≤ q·R`, i.e. the appendix ν\* at **σ=1**. At the literal defaults, S\* = **−1/19** exactly (Fraction arithmetic), clamps to 0; the σ-dependent break-even solves to **√23161/38 − 7/2 = 0.5049311709704234** — matching the brief. `model_params` writer: none outside one test fixture. Fire rate: 0 rejections confirmed by both routes — the "REJECTED sk= … Valley" line appears **0 times in runner-emitted logs** against 1538 ADMISSIBLE lines (every one printing `S*=0.000`) and exactly **400** `REJECTED A=` error-path lines. The 39 archive hits of that string are all model-authored text inside round JSONs, not runner output. One discrepancy per calibration: the denominator **3,816 does not reproduce — I count 3,523** `"passes_threshold": true` in this copy (the single `false` is the panel brief quoting itself). Direction unchanged.

**The founder's reframe, tested rather than argued:** I ran the counterfactual. The *corrected* threshold (0.50493) would have rejected **0 of the 1538** archived admissions — minimum sk ever admitted is **0.740**. Three consequences:

1. On the archive, the gate is redundant *whether broken or repaired* — so the "repair invalidates replay" objection is **empirically void**: zero decision flips.
2. But "redundant, remove it" does not follow, because the ≥0.74 floor is a property of the fixes seen, **not of the machinery**: `tristate = ADMISSIBLE if sk > 0`, and low sk is reachable by construction. Concretely: with no `test_cmd` configured, a fix that introduces new bandit HIGH findings scores **sk = 1/3 — admitted today, rejected by the corrected gate**. Nothing upstream blocks it. The zero fire rate is evidence the upstream machinery has *so far* only passed high-sk fixes, not that it must.
3. The reframe's optimistic reading is also incomplete for a second reason: even *repaired*, the gate compares sk against a constant, because q, R, ν_b, ν_f are all literals with no writer. And note a repaired gate has a rejects-everything regime at low R (ν_b alone exceeds break-even) — theoretically sensible ("don't touch low-risk artefacts"), operationally drastic, unreachable while R is the 0.5 literal.

**Recommendation:** neither remove nor silently bind. Repair the formula, ship it as **diagnostic-only alongside the live check for one arc** (the project's own `gamma_threshold_profile` pattern: "DIAGNOSTIC ONLY: it changes no verdict"), then bind. Separately flagged: a regression-*failing* fix (e2=0, others clean) scores sk=0.6 and passes even the corrected gate — the E-weights admit a fix that breaks the test suite; the threshold repair does not fix that and someone should look at it.

### Q2 — simplicity/sufficiency: small new mathematics, real machinery, composition warranted

I re-verified the foundation independently and more strongly than the brief: the induction step of `R_n = (1−p)^n/(1+(1−p)^n)` is **symbolically exactly 0** (sympy, not sampled), base case = π = 0.5.

**Maths axis:** agree with the prior panel that nothing belongs *in* the state equations — a reduction property is a theorem about the equation, and folding it in makes the equation piecewise, the opposite of collapse. The new mathematics warranted is modest but not nothing: the **residual as a first-class object** — for each reduction pair, file (S, F, D, res) where res is the disagreement set/bound over the pre-declared D, with the trichotomy *proved-zero / bounded-and-filed / unfiled ⇒ inadmissible*. That this is machinery and not decoration is demonstrable **on this repo's own history**: Q1's gate is precisely an unfiled non-zero residual. `check_sk_threshold`'s S\* is the σ=1 slice of the appendix's ν\*; the implicit scope was all σ; the residual was the entire Valley; it shipped silently and admitted everything for months. The criterion, mechanically applied at review time ("over what D does this formula agree with the appendix form? — only σ=1; residual unfiled"), refutes that simplification before it ships. One retrodicted live catch is the evidence "recording is sufficient" lacks.

**Machinery axis:** an execution gate over a **reduction registry**: the appendix's 28 statements as executable tuples, re-verified in the suite by proof/enumeration (sympy induction, exhaustive scan) — turning "5 spot-checked" into "28 regression-guarded", the same conversion C4 just performed on a grep test. Two provisos: the gate's scope must include **code claiming to implement an appendix formula**, because the residual that actually fired was appendix↔runner, not appendix↔appendix; and sampled checks (mpmath) are retained as smoke only — the criterion's own consequence, sampling refutes but never admits, must bind the gate too.

**Composition:** warranted. Definition without gate is today's state — 28 statements, 5 checked, and an inadmissible reduction shipped in code regardless. Gate without definition has no admissibility criterion. Joined, they extend TOOLS-DECIDE to simplification claims: a model proposing a simplification ships D plus proof/enumeration, the runner re-executes, or the simplification is filed as a claim and not applied. That is the mechanism by which this improves model-output reliability, and it is the project's founding rule pointed at a new claim class, not decoration.

### Q3 — the disputed band: the separating test exists and is the founding rule

**The test:** a disputed-band finding is tool-decidable iff it admits a falsifier whose *executed* outcome decides the governing clause. Route: (1) carries or admits a runnable falsifier → run it, verdict mechanical; (2) names a machine-checkable constraint or a reproduction recipe → run it; (3) neither → human queue, **tagged with which of the founder's four irreducibility categories it claims** — a queue entry without a category is a triage failure, not an irreducible item.

**The fraction:** by clause type (0C.8 counts), wrong-result 68 + unreproducibility 6 + hard-constraint 8 = **82/259 = 31.7% decidable per se**; verification-integrity (67) and evidence-loss (16) split — the *fact* is often executable (C1 was itself a verification-integrity defect confirmed by execution), the consequence-weighting sometimes not. Measured floor in this copy: **127 of 359** band entries in archived runner states already carry falsifier/computed-evidence fields (~35%). So plausibly 30–60% tool-decidable — but that number must come from running the test over the 259, not from me. Pilot on the 109 findings sitting exactly at 0.70, where the census says a third are non-critical by the rubric.

**The selection rule:** inoperable verbatim — "matches most exactly" names no metric. Operable refinement: *prefer the solution whose equivalence to the goal is establishable with empty residual by proof or enumeration; failing that, the smaller named-and-filed residual.* So refined, it does real work here: partition-by-executable-test (residual = the named, bounded human queue) beats route-everything-to-human (residual unnamed — decidable items buried in the queue, the founder's stated inflation failure) and beats trust-the-numeric (residual = the 118 disagreements, unfiled).

---

## What would prove me wrong

- **C1:** adoption of a threshold whose `:g` form differs from its written literal. **C2:** a dynamic-key read of `occasions` my literal-string grep missed. **C3:** any `_guard_*` path consulting a marker before denying. **C4:** an argv path in the shim not routed through `subprocess.run`.
- **Suite:** the same 2 failures in a canonical (non-worktree) checkout — that converts my environment attribution into an author error.
- **Q1:** an archived admitted fix with sk < 0.505 later confirmed harmful (bind now, skip the diagnostic arc); or proof sk ≥ 0.74 for all reachable gate inputs (true redundancy — remove).
- **Q2:** a showing that a reduction registry, as it would actually have been populated, contains no tuple covering `check_sk_threshold` — then the retrodicted catch evaporates and the machinery is decoration.
- **Q3:** running the separating test over the 259 and finding <10% decidable — the inflation worry would then be moot and the triage machinery unjustified overhead.

**Calibration outcome, for the record:** of the brief's numbers I could execute, these reproduced exactly: −1/19, 0.504931170970423, 400 error-path lines, 4/5 revert failures, 8/8 old-test passes, the C4 P-pass, 4870 collected. Three did not: 3,816 → **3,523** measured; "12 consumers" → **11**; "4870 passed, 0 failed" → **4864/2/4**, both failures environment-attributed. The brief's predicted error rate held.
