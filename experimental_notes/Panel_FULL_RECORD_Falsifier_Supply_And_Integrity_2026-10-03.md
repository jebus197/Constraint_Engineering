# Panel FULL RECORD — falsifier supply and the integrity merge

2026-10-03 06:11 BST

**3 rounds, 2 seats, 0 paid dispatches.** `cc2` and `fable`, both on `claude_cli`
against the founder's Max subscription. The committed paid-dispatch ledger
carries no entry for any of these rounds, which is what makes a paid seat
unreachable rather than merely unused.

**WHY 3 ROUNDS AND NOT 2.** Round 1 ran before the founder's 3 formal standards
were mechanical in the dispatcher. Measured when he asked: "additive" appeared 7
times in `bench/confer_maths_panel_2026-09-05.py`, "simplest sufficient" 0 times
and "composab" 0 times, so 2 of the 3 reached no seat on any round ever run. All
3 are now in the dispatcher prompt string that every seat receives, and round 2 re-ran the same
brief on that basis.

**A CONFOUND THAT MUST BE STATED RATHER THAN SMOOTHED.** Round 2 was NOT blind
with respect to round 1: every round-2 sandbox contained
`experimental_notes/seat_evidence/falsifier_supply_and_integrity_2026-10-02/`
and round 1's seat replies. No recorded tool call names those paths, but tool
previews are truncated, so absence of a record is not absence of a read. Two
variables therefore changed at once, and round 2's richer output cannot be
attributed to the standards alone.

**WHAT THE ROUNDS SETTLED.** All 3 disputes CONFIRMED by execution, in both
seats' own sandboxes. The material one refuted the assistant's own safety
headline: before the fix, a machine-wide observer failure CONVERGED a run with 0
verified criticals. The invariant had been asserted over the predicate while the
defect lived in a consumer's scope.

**WHAT REMAINS OPEN, AND IT IS THE ADJUDICATION.** Applying cc2's fix leaves 8 of
fable's falsifiers red; applying fable's leaves 6 of cc2's red. Neither is
sufficient alone. A composition is therefore justified by MEASUREMENT, which is
what the founder's composability standard requires, and a first one-line
composition did not converge. The merge is deliberately NOT applied.

---


# BLIND ROUND 1 — the 3 standards were NOT yet in the dispatcher

## Round directory: `falsifier_supply_and_integrity_2026-10-02`

### SEAT CC2

`route=claude_cli` `chars=22669` `tool_calls=88` `elapsed_s=1341.4` `ok=True`

<!-- verbatim-begin: cc2 -->
# VERDICT

**Part 2 (the fixes): the integrity predicate is SOUND. Two of the figures declared for it are NOT.** Three CONFIRMED findings, all fixed in the tree.

**Part 1 (the founder's question): the intelligence-first contract IS honoured — 91.8% of model-reasoned criticals were later toolled, 1 of 537 accepted without a tool.** The founder's over-specificity intuition reproduces (OR 4.3063). But the brief's adjudication of Cause 2 is wrong: **Cause 2 reproduces exactly, 19 of 46**, and it is the largest inflation in the starvation figure — the brief dismissed the cause that matters most.

| # | Finding | Verdict |
|---|---|---|
| F1 | The key-access advisory's verdict on an archived run is a function of the **scanner's cwd**, not the run. 107 / 0 / 114 advisory hits from one run directory under three roots. | CONFIRMED |
| F2 | Cause 2 **does** reproduce (19/46). `repro_supply_causes`'s own `verdict()` counts `UNTOOLABLE` as a tool verdict, which is what refuted it. | CONFIRMED |
| F3 | "Run 1b halted with BOTH halves of the two-sided gate satisfied" is false. `novel_critical_history == [6,4,5]`, `gate_history == [False,False,False]`. | CONFIRMED |

---

# F1 — the advisory is pinned to the caller, not to the run (CRITICAL)

## Falsifier and executed result

```
$ python3 scripts/advisory_channel_selection_2026-10-02.py
  prose_convergence_run1b_2026-10-02
    CONFIRMED total                 : 114
    THIS MERGE   advisory / audit   : 107 / 7   fires=True   dropped=0
AssertionError: REGRESSION: run 1b read no key and the advisory fired
```

The committed producer for Part 2's declared figure **aborts on its own regression assertion**, so `THE MERGE DOMINATES BOTH ON THESE INPUTS` and the "a plant in the same file fires 2" figure were never computed in the delivered tree. Three roots, one run directory:

```
A staged tree (as delivered)                     conf= 114 adv= 107 aud=  7 fires=True
B canonical literal (what the test hardcodes)    conf=   7 adv=   0 aud=  7 fires=False
C canonical literal, NOT present (CI/other user) conf= 114 adv= 114 aud=  0 fires=True
```

Row C is worse than row A: with the canonical tree absent, `_committed_counterpart` finds nothing, every `carried_verbatim` flag is lost, and **the audit channel empties to 0** — the merge's "nothing is dropped" property fails in the same move as its silence property. So `run 1b 0 advisory / 7 audit` held at exactly one filesystem location on one machine, and row B is green only because `/Users/georgejackson/Developer_Projects/Constraint_Engineering` physically exists here.

`bench/tests/test_key_access_advisory_2026-10-02.py` had already met this and patched the **test**, hardcoding `CANONICAL_REPO = /Users/georgejackson/...` with a comment explaining why. The producer did not get the same workaround. **Test and committed producer disagreed about the same figure, and the test was green.** That is the Q5 failure class occurring today, by location drift rather than rule change.

## Fix delivered — `bench/key_access_forensics.py`

The pin was already in the archive and nothing read it: the runner has written `panel_confinement.run_root` into every report since 2026-09-01 ("WHERE THE PANEL COULD REACH", `reference_runner_v3.py:14928`). A recorded field no reader consumes is the additive standard's own failure mode. Added:

- `trusted_record_names()` — the existing anti-widening rule, factored out so both readers use one predicate.
- `discover_run_root()` — reads `panel_confinement.run_root` from **runner-authored records only**, refuses `/`, refuses two disagreeing values, returns `None` for pre-2026-09-01 runs.
- `scan_run` adds the recorded root **alongside** the live one (never substituted), in the `confined` test, the allowlist, and `_committed_counterpart`.
- `Report.run_root_recorded`, so a reader can tell a pinned verdict from a cwd-pinned one.

```
=== run 1b, three roots, AFTER the pin
  staged copy                  conf=7 adv=0 aud=7 fires=False pinned=True
  canonical                    conf=7 adv=0 aud=7 fires=False pinned=True
  a root that does not exist   conf=7 adv=0 aud=7 fires=False pinned=True
=== the exam case must NOT move
  exp48  staged     in_scope=False conf=12 adv=12 pinned=None
  exp48  canonical  in_scope=False conf=12 adv=12 pinned=None
```

Producer now exits 0 with `THE MERGE DOMINATES BOTH ON THESE INPUTS: True`, run 1b `0 / 7`, the plant firing `2 / 7`. The 2026-07-29 exam hole stays shut (exp48 unchanged, 12 hits, `repo_in_scope=False`). I checked the silence direction: an in-repo key read is still CONFIRMED by `answer[_-]key.*\.json` and the key-field patterns, which are not allowlist-gated — so the pin cannot create a false negative.

**120 tests green across the 8 affected files; the 8 pre-existing failures I measured before touching anything are unchanged** (6 are `git ls-files` refusing to census a non-git staged copy — the fail-loud design working, not a defect).

---

# F2 — Cause 2 reproduces; the reproducing script refuted it

```
control entries with NO falsifier body: 19
  verdict string repro_supply_causes reads: {'UNTOOLABLE': 19}
  which field it came from: {'falsifier_verdict': 19}
```

`repro_supply_causes`'s `verdict()` returns any non-empty string. `UNTOOLABLE` is non-empty — written by `reference_runner_v3.py:5808` when a critical arrives with no falsifier, returned by `reverify_falsifier("")`, and a member of `EQUIPMENT_FAILURE_VERDICTS` **precisely because it is not an adjudication of the claim**. So `nobody` was False for all 19 and the stratum measured 0 of 46.

Excluding the decline, on the same 624 rows, in the committed producer:

```
CAUSE 2  zero-plant controls: no falsifier at all
  as first written: a DECLINE counts as a verdict
    control  no-body  0  other 46   OR = 0.0000  p = 6.144102e-01  -> NOT REPRODUCED
  corrected: only a TOOL verdict counts as a verdict
    control  no-body 19  other 27   OR = 11.2593  p = 1.364814e-10  -> REPRODUCED
```

19/46 = 41.3043%, Wilson [28.2886%, 55.6605%]. scipy, mpmath hypergeometric sum, and **Wolfram Language (local Wolfram Engine)** agree: `sampleOR -> 11.2592592592592592592`, `twoSidedP -> 1.3648143901661857055e-10` — 12 digits.

**Both the brief's conclusion and its explanation are wrong.** The claim is not an artefact of the pre-fix body-only definition: 19/46 holds under *both* definitions once the decline is excluded. The claimed OR 14.9614 / p 6.39737e-12 sits beside my 15.5659 / 2.43e-12 under the tighter whitelist — same population, same order.

**Substantively: the control stratum is a real inflation.** Zero-plant runs have nothing to falsify, so 19 of 46 criticals correctly declined as UNTOOLABLE is the mechanism *working*. Counting them as starvation is the single largest inflation, and the brief ranked it out.

Fixed in `scripts/repro_supply_causes_2026-10-02.py`: both definitions printed, nothing removed, the non-reproduction kept on the record.

---

# F3 — the halt-bound change's cited evidence does not support it

```
$ python3 bench/tests/falsifier_run1b_gate_claim_2026-10-02.py
novel_critical_history (new genuine criticals per round): [6, 4, 5]
gate_history (the runner's own record of the gate):       [False, False, False]

FALSIFIED
AssertionError: BOTH HALVES SATISFIED is false. The COUNT side needs consecutive
rounds with ZERO new criticals; run 1b recorded [6, 4, 5] -- never zero in any
round -- and the runner's own gate_history is [False, False, False] ...
```

The two halves of `_check_gamma_alt_convergence` are the GAMMA side (`gamma_critical >= gamma_alt_threshold`) and the COUNT side (K consecutive rounds with zero new genuine criticals). **`gamma_all` is a third number, not the second half.** Run 1b never had a zero-critical round. So it would not have converged at round 2 whatever the queue contained, and the queue-of-3-against-2 is not a blocked convergence.

The founder's ruling is independent and stands; what fails is the citation. Also noted: `_irreducible_queue_split` returns `(0, 0)` on run 1b's *saved* registry with the predicate shipped **and** neutralised — so the predicate's effect is not demonstrable from the archived end-of-run state either. I did not assert a direction there; I could not compute one.

Fixed in `scripts/integrity_exclusion_figures_2026-10-02.py` (header corrected, the two refuting series now printed with the gamma figures) and the `reference_runner_v3.py:2239` comment (wrong citation quoted and corrected, not dropped).

---

# Q1 — the contract IS honoured

`scripts/intelligence_first_contract_2026-10-02.py` (delivered). Population: 624 deduplicated criticals, severity ≥ 0.7, post-exp42. Predicate: `status_adjudicator != "tool"` for "model-reasoned"; a tool verdict is any member of `{CONFIRMED, REFUTED, ERROR, TIMEOUT, INTEGRITY_VIOLATION, REFUSED}` on `falsifier_verdict`, `routing_verdict_unreconciled`, **or `routing_history[-1]`** — reading the ladder residual, because not reading it would reproduce Cause 3 inside the measurement.

```
model-reasoned criticals                        440/624 = 70.5128%
  ... of which a TOOL later returned a verdict  404/440 = 91.8182%  Wilson [88.8808%, 94.0317%]
accepted terminal status                        537/624 = 86.0577%
  ... accepted with NO tool verdict               1/537 =  0.1862%  Wilson [0.0329%, 1.0472%]
    sim45_memory_20260830T161215Z C0006 CORROBORATED runner model_confirm_quorum (3/2 independent)
```

The single offender was confirmed by model quorum — but `CORROBORATED` is the runner's own quarantine status (`ATTESTED_STATUSES`: "a model said so, not a tool measured it… readers MUST NOT count these"). **So: zero un-quarantined reasoning-only confirmations. The founder's design intent is met, and the 86.3727% hand-rolled rate is not a defect — hand-rolling in logic is scratchpad reasoning that gets toolled 91.8% of the time.**

One caveat I will not hide: `status_adjudicator` is recorded on only 184 of 624 (29.4872%), so for 70% the field cannot answer Q1 directly and the 91.8% rests on tool-verdict presence. A field absent on 70% of its population is a weak instrument.

# Q2 — the loop IS reachable on prose, and this refutes the brief's framing

```
prose-run criticals 43   code-run criticals 581
  prose: a TOOL returned a verdict     43/ 43 = 100.0000%  Wilson [91.7990%, 100.0000%]
  prose: accepted with NO tool verdict  0/ 43 =   0.0000%  Wilson [0.0000%, 8.2010%]
  code : a TOOL returned a verdict    537/581 =  92.4269%
  prose vs code, NO tool verdict: OR = 0.0000  p = 6.316256e-02
```

The briefing's "ruff, mypy, bandit and pytest have no purchase on prose" is true and irrelevant to Q2. Those are the **lint suite**. The adjudicating tool is `reverify_falsifier`, which re-executes a falsifier, and a prose falsifier is Python over text — `re` and `pathlib` are as general over prose as `ast` is over code. Prose criticals are toolled at 43/43, Wilson lower bound 91.8%, **higher** than code's 92.4%. Q2's premise does not hold.

# Q3 — I argue AGAINST a new template, and the measurement is the argument

The general cannot-fail guard already exists: `run_discrimination_control` runs the falsifier against a **corrected** copy and stamps `NON_DISCRIMINATING` when it fires on both. Demonstrated separating both shapes the brief names:

```
$ python3 bench/tests/falsifier_discrimination_guard_2026-10-02.py
  hardwired `return True`                    real=CONFIRMED corrected=CONFIRMED -> NON_DISCRIMINATING
  vacuous: 0 HIGH over an empty metric set   real=CONFIRMED corrected=CONFIRMED -> NON_DISCRIMINATING
  reads the real target                      real=CONFIRMED corrected=REFUTED   -> DISCRIMINATES
CLEAN EXIT
```

(My first draft of this falsifier printed `FALSIFIED` unconditionally and scored the real falsifier as non-discriminating; its own guard caught me. Recorded because it is the hazard under discussion.)

Then the reach, over 567 post-exp42 criticals that have a falsifier body:

```
DISCRIMINATION CONTROL RAN AT ALL : 44/567 =  7.7601%  Wilson [5.8313%, 10.2575%]
  NO_DISCRIMINATION among those run: 14/44 = 31.8182%  Wilson [19.9993%, 46.5569%]
  positively shown to discriminate : 21/567 = 3.7037%  Wilson [2.4350%, 5.5955%]
  prose: ran 4/33 = 12.1212%   code: ran 40/534 = 7.4906%
```

**Adding a template while the existing general guard reaches 7.76% of the population is an addition nothing reaches — the project's own 11-of-11 failure mode.** And 31.8% of the falsifiers it *did* check cannot fail: the hazard is not hypothetical, it is roughly one in three of those measured. The control's reach is bounded by needing a corrected copy. So the additive move is: **when no corrected copy exists, synthesise one by inverting the asserted property**, raising reach toward 567 rather than 44. That extends the guard that works; it does not add a second one beside it.

# Q4 — the repointing experiment, specified

- **Population.** The 157 of 499 distinct falsifier bodies that name ≥1 concrete file (31.4629%, Wilson [27.5433%, 35.6658%]), restricted to the 18 ERROR + 158 CONFIRMED rows Cause 1 is computed over, so the result is commensurable with OR 4.3063.
- **Substitution rule.** Mechanical, by AST, never by rewrite: for each path literal *p* resolving under the run's `run_root` (now readable — F1), substitute *p* → the same repository-relative path under a freshly staged copy of the target tree. Exactly one substitution class per body; bodies needing ≥2 incompatible classes are logged as NOT REPOINTABLE and counted, never dropped.
- **Decider.** `reverify_falsifier` on the repointed body, in the staged copy. Tools decide. Prose verdict is not an input.
- **Pre-registered rates.** H0: repointing does not change the verdict — `P(ERROR | repointed) = 18/176 = 10.2273%`, Wilson [6.5841%, 15.5257%]. H1 (over-specificity is causal): ERROR falls to the unnamed stratum's `10/388 = 2.5773%`, Wilson [1.4057%, 4.6833%]. Fisher on the resulting 2×2 at α = 0.05, scipy against an mpmath hypergeometric sum, Wolfram as second falsifier.
- **Stopping condition.** All 176 repointable bodies processed, or the Wilson interval on the repointed ERROR rate excludes **both** 10.2273% and 2.5773%, whichever first. A body whose repointed run ERRORs for an unrelated reason (import failure, syntax) is INDETERMINATE and reported, not scored — otherwise the experiment measures my substitution instead of the coupling.
- **Why it is the only thing that settles it.** Cause 1 is observational: a body naming a file may ERROR because authors who name files write more fragile falsifiers. Repointing holds the author fixed and moves only the path.

# Q5 — the rule-amendments register, delivered and demonstrated failing

`--as-of` pins the **denominator**. The access-only ruling changed the **numerator** at every date, so no as-of value reproduces 2/640.

I reject pinning the rule set. Keeping superseded rules alive forks the predicate at each ruling, and the forks are load-bearing **forever** because historical re-execution reaches them — each a second place the same bug lives, and each a second place every later fix must land. That is this project's own named shape ("fixed in one place, not its twin"). It also makes "we changed our mind about what counts" invisible: the brief re-executes and no reader learns the rule moved.

Delivered: `bench/directives/universal/rule_amendments.jsonl` + `_rule_amendment_reproduction` in `scripts/panel_brief_validate.py`. **A register entry is a committed measurement, not a note.** Five admissibility conditions; condition 5 is what makes it evidence:

1. an entry for exactly this brief and this declared value;
2. `superseded` is **present in the archived brief's own text** — no amending a figure the brief never declared;
3. `superseded != current` — an amendment must amend;
4. `producer` is the script the brief declared — no redirecting to a friendlier one;
5. **the named producer, re-executed now with the entry's own `--as-of`, prints `current`.**

```
$ python3 scripts/panel_brief_validate.py bench/logs/panel_round11_2026-09-11/BRIEF.md
panel-brief: RULE AMENDMENT — ... the brief declares 'real-rejection rate : 2/640 = 0.3125%',
which no longer re-executes at ANY date because the RULE changed on 2026-10-02: The integrity
gate narrowed to ACCESS-ONLY ... The register's successor value 'real-rejection rate : 1/640
= 0.1562%' WAS re-executed just now ... do NOT reuse this figure.
EXIT=0
```

The brief is **not edited**. The guard is demonstrated failing on all five conditions:

```
$ python3 -m pytest -q bench/tests/test_rule_amendment_register_2026-10-02.py
13 passed in 8.13s
```

— empty register leaves the validator exactly as strict; another brief's entry does not transfer; an unknown `superseded` is refused; `superseded == current` (the wildcard) is refused; a redirected producer is refused; a `current` that does not re-execute is refused; a malformed entry contributes nothing. One test proves a matching fixture register *does* accept, so the six refusals are refused for their stated reason and not because the harness cannot accept anything.

`test_declared_figure_as_of_2026-09-29.py` amended, not deleted: the superseded value is still named, and the property now asserted is the reconciliation. Both files green, 20 passed.

---

# WHAT WOULD REFUTE ME

- **F1.** If `panel_confinement.run_root` were model-writable. I checked: it is read only through `trusted_record_names`, the rule that already guards `target_file`. If the canonical tree's `scan_run` already did this and the staged copy is stale — I could not check (no `.git` in the staged tree), and that is my largest residual.
- **F2.** If `UNTOOLABLE` were ever a tool adjudication. Grepped both producers; it is written for empty input and sits in `EQUIPMENT_FAILURE_VERDICTS`. If the 4 control runs are not genuinely zero-plant, the inflation argument dies — I identified them by name (`control`/`zero`), inherited from the brief's own producer, and did not verify their configs.
- **F3.** If the two-sided gate's COUNT side were satisfiable with non-zero `novel_critical_history`. I read the body; I could not fully instantiate `RunnerConfig` to call it, so I rest on `gate_history == [False,False,False]`, the runner's own record.
- **Q1/Q2.** 43 prose criticals from essentially one run family. A second prose run with a lower toolled rate would weaken Q2 sharply; the Wilson lower bound 91.80% is what I have.

**What I looked for and did not find:** a path by which the pin creates a false negative (none — the key-path patterns are not allowlist-gated); a reasoning-only CONFIRMED outside quarantine (1 of 537, and it is quarantined); any regression from my six edits (120 targeted tests green, 8 pre-existing failures unchanged, ruff clean on every file I authored).

# STRONGEST DISAGREEMENT WITH THE BRIEF

1. **"CAUSE 2, zero-plant controls, NOT REPRODUCED" is wrong, and the brief's explanation for the non-reproduction is also wrong.** It reproduces at 19/46 under both definitions. The brief then asked me to adjudicate whether the stratum is "a real inflation or an artefact of that conflation" — the dichotomy is false. It is a real inflation *and* the non-reproduction was an artefact, of a different conflation than the one named.

2. **Part 2's "Measured: run 1b 0 advisory / 7 audit" was not measured in the delivered tree.** The producer aborted. The brief declared five figures for validator re-execution and left this one in prose; it is the one that was false.

3. **The three causes are not competing.** Cause 1 is a minority effect on ERROR among criticals that *have* a falsifier. Cause 2 is about criticals that correctly have none. Cause 3 is about the feedback rendering. They are disjoint strata of one figure, and "adjudicate, do not average" is right for a reason the brief does not give: averaging them would double-count the same 624 rows under three incompatible denominators.

4. **The population dispute resolves against the date cut.** `0 of 558` post-2026-06-06, Wilson [0%, 0.6837%], versus `14 of 624` post-exp42, Wilson [1.3411%, 3.7305%] — the intervals do not overlap, so this is not a rounding disagreement. The date cut drops 89 rows that the feature cut keeps, including undated `panel_*` and `prose_*` directories where the newest runs live, and keeps 51 the feature cut excludes. **For a question about a feature, the feature cut is the population; a date cut answers a question about a calendar and loses the newest runs to do it.** 14/624 is the right figure.

5. **The brief says the access-only ruling "left 3 tests red". It left 8.** Six are `test_guard_false_positive_figures_2026-10-02.py` refusing to census a non-git staged copy — correct fail-loud behaviour, not a defect, but it was not traced either.

# DELIVERED FILES

| Path | Change |
|---|---|
| `bench/key_access_forensics.py` | `trusted_record_names`, `discover_run_root`, run-root pin in `scan_run` + `_committed_counterpart`, `Report.run_root_recorded` |
| `scripts/panel_brief_validate.py` | `RULE_AMENDMENTS`, `_load_rule_amendments`, `_rule_amendment_reproduction`, loud acceptance |
| `bench/directives/universal/rule_amendments.jsonl` | **new** — the register, with the round-11 entry |
| `bench/tests/test_rule_amendment_register_2026-10-02.py` | **new** — 13 tests, all 5 guards demonstrated failing |
| `bench/tests/falsifier_run1b_gate_claim_2026-10-02.py` | **new** — F3's falsifier |
| `bench/tests/falsifier_discrimination_guard_2026-10-02.py` | **new** — Q3's guard demonstration |
| `scripts/intelligence_first_contract_2026-10-02.py` | **new** — Q1/Q2/Cause-2 producer |
| `scripts/repro_supply_causes_2026-10-02.py` | Cause 2 under both definitions; `UNTOOLABLE` excluded from "verdict" |
| `scripts/integrity_exclusion_figures_2026-10-02.py` | F3 corrected; refuting series printed |
| `bench/reference_runner_v3.py` | `:2239` citation corrected, quoted not dropped |
| `bench/tests/test_declared_figure_as_of_2026-09-29.py` | amended to assert the reconciliation; superseded value retained |

All five producers exit 0 (one did not before). Wolfram Language (local Wolfram Engine) served as second falsifier on F2's 2×2 only; my first Wolfram call used `FisherRatioTest`, the wrong instrument, and verified nothing — it is not quoted.

**Terminating.** A further pass over the integrity predicate, the A4 blocker, and the 48-combination/400-registry invariant produced no above-threshold finding: the predicate's carve-out ordering is correct, `integrity_unobserved` blocks as documented, and the one-predicate-four-readers invariant holds under execution.
<!-- verbatim-end -->
### SEAT FABLE

`route=claude_cli` `chars=12036` `tool_calls=58` `elapsed_s=931.2` `ok=True`

<!-- verbatim-begin: fable -->
All green. Further passes produced no new above-threshold findings — terminating per §6/§10. Final report, field by field.

---

# VERDICT

**The 2026-10-02 merge is architecturally sound and I confirm its design choices — but it shipped with a CRITICAL relocation defect I demonstrated, fixed, and regression-held.** The founder's starvation fear is **not realised in the absolute sense**: post-gate, zero criticals have neither falsifier nor verdict. The real brittleness is **path-binding, not logic** — and I executed the repointing experiment that proves the archived logic survives decoupling. The intelligence-first contract is **honoured at 536/537** post-gate.

# FINDINGS AND FIXES (delivered as files, all executed)

**F1 — CRITICAL, CONFIRMED, FIXED: the forensic verdict over an archive was a function of where the scan ran.**
`scan_run` judged archived path literals against the *scanning machine's* repo root, ignoring the runner-authored `panel_confinement.run_root`. From this relocated checkout, run 1b's 107 legitimate repo reads became CONFIRMED advisory hits; the brief's own "Measured: 0 advisory / 7 audit" figure was false here, and the committed measurement `advisory_channel_selection_2026-10-02.py` died on its own assert (`AssertionError: REGRESSION: run 1b read no key and the advisory fired` — executed, shown above). A committed measurement that re-executes on exactly one machine is a claim about evidence, not evidence — the same defect class as the `r*_*.json` glob reading Exp 48 as CLEAN.
- **Falsifier**: `bench/tests/test_forensics_survives_relocation_2026-10-02.py` — ran pre-fix: `1 failed` (FALSIFIED), guards green.
- **Fix**: `bench/key_access_forensics.py` — new `discover_run_roots()` reads `panel_confinement.run_root` from runner-authored records through the **same** single-trusted-report boundary (`_trusted_record_paths`, factored, not duplicated); historical roots join the confinement test and, for unconfined runs only, the allowlist.
- **Verified**: falsifier now 3/3 green; `advisory_channel_selection` EXIT=0 printing 0 advisory / 7 audit; 90 targeted tests pass; exp48 exam semantics untouched (C0012 answer-key hits and C0017 both still caught; pre-`run_root` archives bit-identical behaviour). Forged-second-report widening attempt refused by test.

**F2 — SAME CLASS IN THE PRE-EXECUTION GATE, reported not patched (HIL).** Re-verifying run 1b's archived falsifiers from this checkout: all 9 path-coupled bodies return INTEGRITY_VIOLATION ("path outside the declared target") though run 1b's own record shows they executed and confirmed canonically. I did **not** widen the gate's refusal set — that is a security boundary and the founder's call; the repoint substitution (below) is the safe remedy for archival re-verification.

**F3 — Part 1b DELIVERED: rule-change amendments register.** The brief said 3 red tests; **I measured 2** (`test_as_of_the_briefs_date_reproduces_the_declared_figure`, `test_the_archived_brief_is_not_refused`). Delivered: `bench/amendments_register.json` (append-only; one entry: 2/640 → 1/640, access-only ruling) wired into `scripts/panel_brief_validate.py`'s historical path. The register is held to evidence: it reconciles **only if its superseding value re-executes in the same `--as-of` output**, and the acceptance prints a loud `AMENDED FIGURE` line. Demonstrated failing when it should: `bench/tests/test_amendments_register_2026-10-02.py` — unregistered stale figure refused; **tampered register entry refused**; fresh-brief dodge still shut; brief verified unedited on disk. The two red oracles amended loudly (amendment documented in-test, superseded value preserved machine-checked). 12/12 green. Against rule-set pinning: keeping superseded rules executable forever is unbounded maintenance and a standing bypass surface (the wide gate stays importable); the register is one committed record per ruling, checked in both directions.

**F4 — the standing measurement IS partly tautological, adjudicated.** `falsify_prose_falsifier_supply_2026-09-30.py` part 3's "routing cannot substitute for supply" compares two **author-written stubs**: `untaught` returns `""`, `taught` returns the very falsifier part 1 already proved works. `resolved` equals supplied-by-stub by construction — it measures the stubs, not routing. Parts 1–2 are genuine (5/5 bidirectional discrimination executed; reachability grep real, though `"stem_fixtures"` substring is a weak reachability predicate). Keep the script; discount part 3 as evidence.

# THE FOUNDER'S QUESTION, ADJUDICATED ON THE THREE CAUSES

**CAUSE 1 (over-specificity): REPRODUCED and strengthened.** OR 4.3063, p = 2.430001e-04 — scipy, independent mpmath sum, **and Wolfram Language (local engine): OR 4.3063291, p = 0.00024300011** (attribution per Wolfram's terms). But the coupling is in **PATH, not logic**.

**CAUSE 2 (zero-plant controls): ARTEFACT of the `classify()` conflation — demonstrated.** Under the OLD body-only predicate I reproduce exactly **19/46** in controls; **all 19 carry verdict UNTOOLABLE**. They were assessed and declined — the mechanism *working* on findings with nothing to falsify. Under the corrected predicate: 0/46, Fisher p = 0.614. The claimed OR 14.96 measured the conflation, not starvation.

**CAUSE 3: BLOCKED by D-2, confirmed by execution** — `target_file` on 52/624 post-feature criticals, all `.py`. D-2 is now blocking a measurement; recording `target_file` in every registry entry is the unblock.

**The population dispute: the adversarial pass is right in substance.** My 14/624 reproduces — but all 14 sit in `exp42_composer_20260602T230020Z`, dated **2026-06-02, four days before the falsifier gate landed**. The exp-number cut smuggles a pre-feature window into a post-feature claim. The correct population is *runs after 2026-06-06*, and on it absolute starvation ("nothing written and nothing recorded") is **0**. The 57.4% all-time figure in the supply decomposition is dominated by pre-gate archaeology.

**Q1 — the contract is honoured post-gate: 536/537.** Population: deduplicated criticals (sev ≥ 0.7) across all archived registries, post-exp42 cut, status ∈ {CLOSED, CONFIRMED, CORROBORATED} (n = 537). Predicate: a recorded tool verdict (`falsifier_verdict`, unreconciled ladder field, or last routing-history verdict). Violations, named: `sim45_memory…/C0006` — CORROBORATED on UNTOOLABLE, a reasoning-only confirmation, **a defect not a style** (1/537, Wilson [0.03%, 1.05%]); and `exp42_composer_20260606…/C0046` — CLOSED on ERROR, a close without demonstration. Pre-gate, 432/1417 confirmations were reasoning-only — exactly the class the gate eliminated.

**Q2 — the loop IS reachable on prose, by execution.** Static instruments have no purchase, but the *decider* does: `reverify_falsifier` executes document-reading falsifiers, and the corpus discriminates 5/5 bidirectionally on prose. Stronger: my repoint pilot shows real seats on run 1b (a prose target) *already wrote* prose falsifiers the tool CONFIRMS once path-decoupled. The founder's "scratchpad reasoning until tool-confirmed" contract is exactly what the archive shows — hand-rolled logic (86.4%) adjudicated by the tool (536/537). The gap is supply wiring, which the 09-30 script's standing red assert correctly demands.

**Q3 — the template, with its guard demonstrated failing.** The general template is the **bidirectional control pair** the project already owns: falsifier(artefact) must CONFIRM *and* falsifier(control-with-defect-absent) must REFUTE. The cannot-fail guard is the flip requirement, and I executed it: genuine template ADMITTED (CONFIRMED/REFUTED); the `check_sk_threshold` shape (always-asserts) REJECTED (CONFIRMED/CONFIRMED); the A19 `e4_bandit` shape (never-fires) REJECTED (REFUTED/REFUTED). I deliberately did **not** commit an unwired guard module — an addition nothing reaches is the project's own top defect class (11/11 since 08-01); the guard belongs inside `reverify_falsifier`'s protocol when the corpus is wired live, which is one decision, the founder's.

**Q4 — the repointing experiment, specified and piloted.** *Pilot executed*: run 1b's 9 distinct bodies hardcoding the recorded `run_root`; substitution = prefix replacement with the live root, nothing else edited; decider = `reverify_falsifier`. Result: **8/9 recovered to a tool decision (8 CONFIRMED, 1 ERROR)**, Wilson [57.1%, 99.5%]. *Full spec*: population — the 157/499 file-naming bodies from the committed decomposition, stratified ERROR vs CONFIRMED; substitution rule — rewrite each body's path literals to the staged copy of the same artefact (prefix map from each run's `panel_confinement.run_root`, now machine-readable via `discover_run_roots`); decider — `reverify_falsifier`, never prose; pre-registered rates — H1: ≥50% of named-file ERRORs recover to a decided verdict under repointing (coupling is in path); H0: recovery ≤10% (coupling is in logic, repointing is futile); report both strata with Wilson intervals and Fisher on recovered×named; stopping — fixed population, one pass, no sampling (157 bodies is affordable); any body the gate refuses goes to HIL, never silently dropped.

# WHAT WOULD REFUTE ME

- F1: an archived run whose `panel_confinement.run_root` is *not* the repo root (e.g. a staged dir), which would poison my allowlist derivation — I searched the runner and found exactly one write site, `str(REPO_ROOT)` unconditionally; a second write site elsewhere would overturn it. A model shown writing the single trusted report *and* displacing the runner's artefact would break the trust boundary I reused.
- The contract figure: a registry field other than the three I read in which tool verdicts live (my `verdict()` predicate would undercount); finding CONFIRMED-status entries whose `falsifier_verdict` was model-written rather than runner-written.
- CAUSE 2: controls where seats *wanted* to write falsifiers and the record shows attempts erased — I looked (bodies with routing history in control runs) and found none; their presence would restore the inflation claim.
- The repoint pilot: bodies whose CONFIRMED-after-repoint is vacuous (asserting trivialities). I spot-read them — they grep the real spec document for claimed text — but a full admissibility pass over all 8 could overturn individual verdicts.

# STRONGEST DISAGREEMENT WITH THE BRIEF

1. The brief presents "run 1b 0 advisory / 7 audit" as **Measured**. It measured on one machine. Until today's fix the same committed script *refuted* that figure anywhere else — the brief's Part 2 evidence standard did not meet its own Part 1 standard ("a number that exists only as prose…" applies equally to a number that re-executes only on the founder's laptop).
2. "Left 3 tests red" — I measure **2**. Name the third or correct the count.
3. The adversarial block labelled "not reproduced by any committed script" is framed as the weakest claim on the table; executed, it is the **strongest** — the 0/558 cut is the right population and my own 14/624 confirms the residue is a pre-feature artefact. The brief's cut-at-exp42 framing, not the adversarial pass, is what's wrong there.
4. The decomposition's headline "57.4% NOTHING WRITTEN AND NOTHING RECORDED" is dominated by pre-gate runs and invites exactly the starvation misreading the founder voiced. The honest headline is: *post-gate absolute starvation is zero; the live defects are path coupling (fixed mechanically by repointing), one CORROBORATED-without-tool entry, one CLOSED-on-ERROR, and D-2 blocking the prose stratum.*

**Convergence declared**: hard assumptions tested (trust boundary, exam confinement, both refusal directions of the register, gate semantics); every residual finding (F2, the REFUTED-stale-ladder edge in `_integrity_violation_excluded` — non-material because REFUTED is terminal at every call site; the weak reachability predicate in the 09-30 script) sits below the real-world-consequence threshold or is routed to HIL above. A further pass yielded no new material findings.

# BLIND ROUND 2 — all 3 standards in the dispatcher; NOT blind w.r.t. round 1

## Round directory: `falsifier_supply_and_integrity_r2_2026-10-02`
<!-- verbatim-end -->
### SEAT CC2

`route=claude_cli` `chars=6245` `tool_calls=265` `elapsed_s=3469.9` `ok=True`

<!-- verbatim-begin: cc2 -->
**18 passed** on their new tests; **76 passed** across my surface plus the amended oracle, so their `falsifier_verify.py` edit does not disturb my fixes. `_path_tokens`/`_TOKEN_RE` is present in the source.

My own probe refuses all three read routes with nothing leaked — but it does **not** independently confirm their layer-4 mechanism, because my probes name the key directory literally and so trip layer 3 first (`src_violations=3` on every arm). Their probe used an env-rooted *relative* path, which is what made layer 3 blind. That distinction is theirs, not mine.

---

# AMENDMENT — verdict revised

**My earlier "PART 2 is SOUND in design" does not survive.** I had written that the merge was *unrefuted-by-me, not verified*. It is now refuted. Four defects, each with a differential-execution falsifier, each fixed and green:

| # | defect | consequence |
|---|---|---|
| **D1** | `unverified_critical_count` has had **no severity gate since 2026-09-06**; `integrity_refused_criticals` gates `severity >= 0.7` | sub-critical refusals drained from the A4 blocker **and named in no report** — 970 silent drains over 225,280 entries, 41/4000 randomised |
| **D2** | the `integrity_unobserved` carve-out returns `False`, which routes entries into `_apply_routing`'s `else` → `irreducible_escalation`, which the counter skips **before** consulting the predicate | a machine-wide observer failure **drains every critical out of A4 and the advisory names none** — `halt_queue 2` against a bound of 2, so the run **can CONVERGE with zero verified criticals**, the exact outcome the carve-out's docstring claims to prevent |
| **D3** | `clear_stale_resolution_stamps` retracts three stamps and left `integrity_refused` standing | a critical whose falsifier was **replaced and verified CONFIRMED** is still excused, and the advisory overstates |
| **D4** | the spawn hook resolved each whole argument blob; under `shell=True` the blob *is* the command line, so `cat /x/key.json` normalised to a path under an allowed root and `/bin/sh` inherited no hook | **a falsifier read a protected file** past the access-only gate, the runtime observer and the output scan. The identical path through `open()` was refused |

**D2 is the most serious thing in this review**, and it falsifies the brief's own headline claim directly: *"An `integrity_unobserved` carve-out keeps blocking, so a machine-wide observer failure cannot drain every critical out of A4."* It does drain them — not by failing the predicate, but by routing around the consumer that reads it. The invariant was asserted over the predicate; the defect was in a consumer's **scope**, which is precisely what 48 handpicked combinations (all pinning `severity=0.9`) and a randomised arm that compares the report against *the report's own scope* cannot see.

**Why the shipped invariant missed all four:** no consumer reimplements the predicate — all four call sites genuinely call `_integrity_violation_excluded`, and the halt bound and the irreducible collector gate severity themselves, so the predicate governs them identically over 225,280 entries. The brief's "one predicate decides all three" is **true and insufficient**. One predicate with three different *scopes* is three predicates.

**Fixes** (additive; no gate removed, no test weakened): `integrity_refused_subcriticals()` keyed on the counter's own condition; an `integrity_unobserved and not exhausted` guard placed *before* the irreducible skip, with a releasable valve (`test_the_block_is_releasable`) so a transient fault cannot block forever; two flags added to the retraction list; `_path_tokens()` testing every path the command line carries, with 0 false positives on 6 honest spawn shapes. 18 new tests, 746 on the changed-surface regression set.

**Task 4 is sound and I accept it.** The `{C0012, C0015} → {C0012}` narrowing was measured over all 872 archive sources, not the two named members: exactly **1** source stopped being refused, and C0015's only key-ish content is printed prose. No real detection was dropped.

### What this does to my own conclusions

- **F6 hardens.** I reported that the intelligence-first contract has no backstop re-adjudicating vote-confirmed findings. D1–D3 are three independent routes by which a critical leaves the convergence machinery **without any adjudication at all** — so the missing backstop is not a latent gap, it is load-bearing today.
- **A pattern across F1, D1, D2 and D4 that is worth naming more than any one of them.** Every one is a *scope* defect in a correct mechanism: the allowlist carried the wrong root, the counter carried the wrong severity floor, the carve-out's return value carried the wrong routing consequence, the path check carried the wrong granularity. None was a wrong algorithm. The project's grid-and-randomise idiom tests predicates thoroughly and **scopes not at all** — all four were found by differential execution or by relocation, never by a combination sweep.
- **The brief's "48 field combinations and 400 randomised registries" should be read as a measurement of the predicate, not of the invariant it claims.** The honest figure is: 4 consumers, 1 predicate, **2 distinct scopes**, 0 tests comparing a consumer against its counter.

### What would refute this amendment

The four defects are another seat's measurements. I verified that the code exists, that 18 tests pass, that 76 tests across my surface are undisturbed, and that all three read routes are refused end-to-end with nothing leaked — but **I did not independently reproduce the layer-4 isolation, the 970 silent drains, or the zero-verified-criticals convergence**. A re-run of `.scratch/adv/falsify_carveout_drains_a4.py` against a reverted `reference_runner_v3.py` is the single check that would settle D2, and I did not run it. Treat D1–D3 as **PLAUSIBLE pending independent re-execution**, D4 as **CONFIRMED end-to-end but not confirmed at the layer it claims**.

### Termination

Still **not converged**, and now for a stronger reason than before. A further pass produced four above-threshold findings in the artefact the brief invited me to break — so the brief's own stopping condition is not met, and F6's structural defect remains without a delivered fix.
<!-- verbatim-end -->
### SEAT FABLE

`route=claude_cli` `chars=16650` `tool_calls=74` `elapsed_s=981.8` `ok=True`

<!-- verbatim-begin: fable -->
All pending checks are done; the 7 producer-invisible runs carry zero criticals, so no figure moves. Final report.

---

# VERDICT

**The 2026-10-02 merge is SOUND in design and broken in one place the brief itself declared as measured.** The merged integrity predicate, the advisory/audit split, the access-only gate, the amended oracle, and the `classify()` ordering fix all survive execution and targeted attack (201 tests green across every touched surface). One material defect: **the forensics scanner's scope verdict is machine-dependent, so the brief's "run 1b 0 advisory / 7 audit" was a measurement pinned to one machine** — the committed measurement crashed in this checkout with 107 false advisory hits. Fixed, demonstrated, delivered. On the founder's question: his over-specificity intuition is **real but minority** (reproduced, OR 4.3063); the dominant truth is that starvation is a **legacy artefact of population mis-cutting** — on the correctly cut post-gate population, **0 of 610** criticals lack both falsifier and verdict — and the intelligence-first contract is honoured at **535/537 = 99.63%**, Wilson [98.65%, 99.90%].

# MATERIAL FINDINGS (most severe first)

**F1 — CONFIRMED, FIXED. The scope allowlist is not relocation-invariant; the committed advisory measurement does not re-execute off the founder's machine.**
Falsifier: ran `scripts/advisory_channel_selection_2026-10-02.py` → `AssertionError: REGRESSION: run 1b read no key and the advisory fired`, 107 advisory / 7 audit against the declared 0 / 7. Cause, verified by inspection of the hits: all 107 are `out-of-scope path opened` on falsifier bodies in `checkpoint.json` opening `/Users/georgejackson/...` — the *original* machine's repo root, compared against the *current* repo root. The 2026-10-02 `resolve_target_dirs` fix repaired relative paths but left absolute recorded literals machine-pinned. A verification instrument whose verdict depends on which machine re-runs it is the Exp-48-scanner shape again: a confident wrong answer, this time in the false-positive direction.
Fix delivered: `_relocated_counterpart_exists` + `suffix_roots` remap in `bench/key_access_forensics.py` — a literal whose longest existing path-suffix resolves under the current repo root is in scope **only when the repo is already in scope** (code review); OFF for confined exams; protected key paths still lose first; no-counterpart literals stay CONFIRMED (fails toward reporting); content-based signals (answer-key names, key fields, planted sets) never consult scope.
Executed: new test `bench/tests/test_scanner_scope_is_relocation_invariant_2026-10-02.py` — **red before the fix (2 failed / 3 guard-cases passed), green after**; `advisory_channel_selection` now prints `0 advisory / 7 audit`, the plant still fires (2 advisory), `MERGE DOMINATES BOTH: True`, exit 0; ancestors-refusal and advisory tests still green (27 passed).

**F2 — CONFIRMED, FIXED (Q5). A rule change invalidates an archived declared figure in a way `--as-of` cannot absorb, and 2 tests were red.**
`archived_falsifier_rejections --as-of 2026-09-11` now prints **1/640 = 0.1562%** against the archived **2/640 = 0.3125%**; `test_as_of_the_briefs_date_reproduces_the_declared_figure` and `test_the_archived_brief_is_not_refused` were red (I found 2 red, not the brief's 3; no third was red in this checkout — if it existed it was repaired before dispatch).
Ruling delivered, as files: **a committed amendments register, not rule-set pinning.** Pinning the rule set keeps every superseded gate implementation alive forever — unbounded surface, and this project's record (11 additions nothing reached) argues against machinery that only history exercises. Instead: `scripts/figure_amendments_register.json` records (producer, declared, amended, rule-change id, prose); `scripts/panel_brief_validate.py` consults it **only after** the strict check and plain `--as-of` both fail, and accepts **only** the producer printing the registered amended value exactly, as-of the brief's own date, **loudly, naming the rule change**. A third value refuses; a wrong registered value refuses; a missing register fails closed; the mtime dodge stays shut. The archived brief is untouched and still carries `2/640`.
Executed: `bench/tests/test_figure_amendments_register_2026-10-02.py` — 6/6, including the guard **failing when it should** (wrong amended value → refused; unregistered third value → refused). The genuinely-wrong test was amended to pin the figure *through* the register (with a dated justification in the test body — reported here, not silently repaired): `test_declared_figure_as_of_2026-09-29.py` now 7/7.

**F3 — CONFIRMED, FIXED (D-2). `target_file` absent from the checkpoint blocked Cause 3 outright.**
Reproduced: Cause 3 stratification computable on 52 of 624 (all `.py`, zero prose) — the REPORT records `target_file`, the CHECKPOINT (`runner_state.json`, which the instruments walk) never did. Fix: the checkpoint dict in `bench/reference_runner_v3.py` now stamps `target_file` and `run_root` (the latter is F1's provenance done properly — an artefact that names its own root needs no suffix guessing). Executed: `bench/tests/test_checkpoint_carries_target_file_2026-10-02.py` — AST-level assertion that the keys are in the *checkpoint* dumps call, plus the supply instrument executed against a synthetic corpus and resolving the new field. 2/2 green. D-2 closes prospectively; the 572 archived criticals stay unstratifiable — no backfill can honestly manufacture that record.

**F4 — CONFIRMED (partial), no code change. The standing measurement `falsify_prose_falsifier_supply_2026-09-30.py` is tautological in exactly one of its three conjuncts.**
Derivation, not vote: `bench/routing.py:161–165` — falsifier code enters `resolve_via_routing` *only* through `resolve_fn`; `code == "" ⇒ last_verdict = "ERROR"` on every rung. So "no supply ⇒ 0 resolved" is a **theorem of the code**, and the `taught` arm feeds back the fixture falsifier part 1 already proved CONFIRMED, so "corpus supply ⇒ 5/5" is forced given part 1. Part 3 cannot fail while parts 1 and routing import succeed. **But the allegation overreaches as stated**: parts 1 (bidirectional discrimination, 5/5 executed) and 2 (live-path reachability, 0 importers, flips the day wiring lands) are genuinely falsifiable, and the script's verdict is their conjunction. Ruling: keep the script; read part 3 as derivation, not measurement. Removing it would fail the additive standard with no committed measurement showing a replacement dominates.

Below threshold, noted under §8 epistemic marking: 7 archive runs are visible only via `checkpoint.json`, which the supply producers do not glob — executed check: those runs carry **0** criticals ≥ 0.7, so no published figure moves; worth a one-line glob widening someday, not a finding.

# THE ADJUDICATION OF THE THREE CAUSES

**Cause 1 (over-specificity): STANDS, as a minority effect.** Reproduced: 18/28 named among ERROR vs 158/536 among CONFIRMED, OR = 4.3063, scipy p = 2.430001e-04, mpmath agreeing to 1e-9, and **Wolfram Language (local Wolfram Engine): OR = 4.3063291, p = 2.4300011e-04** — three independent instruments agree. But it governs the ERROR bucket (32/1309 = 2.44% of criticals), not the headline.

**Cause 2 (zero-plant controls): DEAD AS STATED, and its mechanism survives relocated.** Executed: control no-body-no-verdict is **0/46** (claimed 19/46), Fisher p = 0.614. The 19 exist — and **all 19 carry verdict UNTOOLABLE**: the pre-fix `classify()` read the body before the verdict and reported assessed-and-declined as never-written, exactly the conflation the same-day fix corrected. The control stratum is **not** a starvation inflation. The surviving signal moved buckets: UNTOOLABLE is **19/46 = 41.30%** Wilson [28.29%, 55.66%] on controls vs **20/578 = 3.46%** [2.25%, 5.28%] live — Fisher OR = 19.63, p = 1.49e-13. On zero-plant targets the instrument *declines*, overwhelmingly. The absence of a falsifier there is the mechanism working, recorded honestly as a declination.

**Cause 3 (prose vs code): WAS unmeasurable; now measurable going forward.** See F3.

**The population dispute (0/558 vs 14/624): BOTH single-axis cuts are wrong; the intersection is right.** Executed: all 14 bare criticals in the exp-number cut come from **one run, `exp42_composer_20260602T230020Z` — four days before the gate landed on 2026-06-06**; the bare date cut conversely sweeps in undated pre-feature `exp36_evidence_latest` (37 bare). Feature presence requires both axes: expno ≥ 42 (or non-exp) ∩ dated ≥ 2026-06-06 → **0 bare of 610**. The adversarial pass's conclusion is correct; its denominator and the brief's are both artefacts. Since the gate landed, no critical has ended a run with neither a falsifier nor a verdict.

# THE QUESTIONS

**Q1 — the contract is honoured, with one dated breach.** Population: 624 post-feature criticals (dedup on run×cid, body-preferring); predicate: status ∈ {CONFIRMED, CLOSED, CORROBORATED} without effective tool verdict CONFIRMED (falsifier_verdict ∥ routing residual ∥ last routing-history verdict). Result: **535/537 = 99.63%**, Wilson [98.65%, 99.90%] tool-adjudicated. The 2: `exp42_composer_20260606T202037Z/C0046` — CLOSED over verdict ERROR, no status mechanism, on the gate's first day — a genuine reasoning-only closure, 1/537; and `sim45_memory/C0006` — `model_confirm_quorum (3/2)` over UNTOOLABLE, but labelled **CORROBORATED**, which `ATTESTED_STATUSES` exists to mark as attested-not-demonstrated, in a simulated run the archive instruments already exclude: by design. The founder's scratchpad framing is the correct description of what the archive shows: 86.4% hand-rolled reasoning, almost invariably terminated by a tool.

**Q2 — what adjudicates prose: the decider executing document-parsing falsifiers, and the loop is reachable — it was reached.** Run 1b, a prose target: **21/21 criticals carry falsifier_verdict CONFIRMED** (35/40 all entries). The stem corpus: 5/5 bidirectional under `reverify_falsifier` itself. "Ruff/mypy/bandit have no purchase on prose" is true and beside the point — the general instrument on prose is regex + sympy/mpmath re-derivation *inside* the falsifier, with the verdict still the executed comparison. What is missing is not reachability but **supply**: 0 live-path modules import the one proven prose pattern, so reaching the loop is per-seat skill, not machinery. The wiring change cc2's script names remains the fix, and it is a founder decision, not mine to land in a review.

**Q3 — the template exists, delivered, and its cannot-fail guard was demonstrated failing.** `bench/falsifier_template.py`: `run_general_falsifier(target, defect_predicate, control_transform)` — target is a *parameter* (repointable, the property the 31.46% file-naming stratum lacks), the predicate delegates to a general instrument, and the **control transform is mandatory**: when `predicate(pristine) == predicate(control)` the template **raises `FalsifierCannotFail`** instead of returning any verdict — vacuity surfaces as ERROR in the ladder, where ERROR already has a remedy, never as a silent verdict. Executed: `bench/tests/test_general_falsifier_template_2026-10-02.py`, 7/7, including the `check_sk_threshold` shape (`lambda s: True`) and the `e4_bandit` shape (measures nothing, answers alike) both **refused by the guard**, plus a sympy-delegating pendulum claim CONFIRMED pristine / REFUTED corrected / repointed without edits.

**Q4 — the repointing experiment, pre-registered.** *Population:* the 158 named-and-CONFIRMED post-feature bodies (Cause-1's named/CONFIRMED cell), precondition: the named file exists in-tree. *Substitution rule:* stage a byte-identical copy of each named file at a fresh path; rewrite in the body only the `FILE_RE`-matched spans resolving to that file; assert the body diff touches nothing else. *Decider:* `falsifier_verify.reverify_falsifier`, two arms — (A) replay unedited (controls for archive rot), (B) repointed. *Pre-registered rates:* H_general — arm-B CONFIRMED rate inside arm-A's Wilson 95% interval; H_specificity — arm-B ERROR excess consistent with OR ≈ 4.3 over the unnamed baseline. *Decision:* Fisher exact on arm × {CONFIRMED, ¬}, two-sided, α = 0.01, OR with CI. *Stopping:* fixed-N, the whole population (the decider is local and cheap); degraded stop — if >20% fail the precondition, publish that rate and no comparison, because the archive is then the finding.

**Q5 — answered under F2:** amendments register, delivered, demonstrated failing when it should; `--as-of` keeps the corpus, the register carries the rule, the record is edited never.

# FIXES DELIVERED (all in the tree, all executed)

1. `bench/key_access_forensics.py` — relocation remap (F1).
2. `bench/tests/test_scanner_scope_is_relocation_invariant_2026-10-02.py` — 5 tests, red→green shown.
3. `scripts/figure_amendments_register.json` — the Q5 register.
4. `scripts/panel_brief_validate.py` — register-consulting historical path, loud, fail-closed.
5. `bench/tests/test_figure_amendments_register_2026-10-02.py` — 6 tests incl. refusal cases.
6. `bench/tests/test_declared_figure_as_of_2026-09-29.py` — the rule-broken assertion repinned through the register (reported, dated, not silent).
7. `bench/reference_runner_v3.py` — checkpoint stamps `target_file` + `run_root` (D-2).
8. `bench/tests/test_checkpoint_carries_target_file_2026-10-02.py` — writer+reader executed.
9. `bench/falsifier_template.py` + `bench/tests/test_general_falsifier_template_2026-10-02.py` — Q3.

Regression: 201 tests passed across every touched surface; the three mandated producers re-executed and match the brief's five declared figures exactly (13.6273 / 86.3727 / 31.4629 / 67.4419 / 4.3063).

# WHAT WOULD REFUTE ME

- **F1:** a pre-fix scan of run 1b on the canonical machine also showing 107 advisory hits — then they were real hits, not relocation artefacts. The module's own committed measurement (114→7 against the canonical root) and the hit contents (literals under the recorded original root) say otherwise. Also: a demonstrated exam-run bypass through the suffix remap would refute my fix's safety claim — I attacked it with a confined-exam case and an answer-key literal, and both stayed CONFIRMED.
- **0/610:** one bare critical ≥ 0.7 in a post-2026-06-06, ≥exp42 registry outside my glob. I looked — the only producer-invisible registries (7 checkpoint-only runs) carry zero criticals.
- **Q1:** a status field or artefact recording model-attested closure that my predicate misses; I searched `verdicts`/`status_adjudicator`/`status_mechanism` and found the attested channel correctly segregated as CORROBORATED.
- **Cause 2:** any control-run critical with no body *and no verdict anywhere* — there are none; all 19 carry UNTOOLABLE.

# STRONGEST DISAGREEMENT WITH THE BRIEF

1. **The brief presented "run 1b 0 advisory / 7 audit" as a measurement, and its own committed producer refutes it everywhere except one machine.** The brief's validator re-executed five figures before dispatch but not this one — the exact gap between a figure that is *declared* and one that is *committed* which the project's own figure-validation machinery exists to close. The advisory figures should have been declared as `<!-- figure -->` comments and validated like the rest.
2. **"Adjudicate: is the control stratum a real inflation" presumes a live question.** It was closed by the same-day `classify()` fix the brief itself describes; the brief should have re-run the claim before listing Cause 2 as open.
3. **"Decide which population is the right one" offers a false binary.** Neither cut is right; the intersection is, and it vindicates the adversarial pass's conclusion with a corrected denominator (0/610).
4. **The brief calls the 2026-09-30 script "tautological" without qualification.** One conjunct of three is; the other two are the falsifiable content, and one of them (reachability) is the actionable finding. The right disposition is reinterpretation, not the removal the word invites.

Wolfram attribution: the OR/p cross-check above was computed with Wolfram Language (local Wolfram Engine via `wolframscript`).

**Termination:** a further pass over the merged predicate (48-state + 400-registry invariants re-run), the oracle amendment, the gate, and the producers surfaced no new above-threshold findings. Converged: the hard assumptions tested are enumerated above; every residual observation (checkpoint-only runs, the sim45 attested entry, the third red test I could not find) is below the real-world-consequence threshold and marked as such.

# STAR ROUND — both blind rounds embedded verbatim

## Round directory: `falsifier_supply_and_integrity_star_2026-10-03`
<!-- verbatim-end -->
### SEAT CC2

`route=claude_cli` `chars=28026` `tool_calls=100` `elapsed_s=1335.3` `ok=True`

<!-- verbatim-begin: cc2 -->
# VERDICT

**All three disputes CONFIRMED by execution in this sandbox. All three fixed, in the tree, with falsifiers that were red before and clean after.** Where I differ from the blind seats is not on *whether* the defects are real — I reproduced every one independently — but on **which fix should stand**, and in two of three cases the fix a seat delivered is the wrong shape under the standards.

| | finding | verdict | standard that decides the fix |
|---|---|---|---|
| **D-A** | the forensic scope verdict is a function of the scanner's cwd, in **both** directions | CONFIRMED | **ADDITIVE** — the pin already exists and nothing read it |
| **D-B** | sub-critical key-access refusals drain from A4 and are reported nowhere | CONFIRMED | **SIMPLEST SUFFICIENT** — widen the wired reader, don't add a second one |
| **D-C** | the `integrity_unobserved` carve-out never executes for the A4 blocker | CONFIRMED | **SIMPLEST SUFFICIENT + ADDITIVE** — fix the stamp, not one of four consumers |

One honest bound that neither blind round states and that changes how D-B/D-C should be read: **the archive prevalence of both is zero.** Over 3,246 archived registry entries, `integrity_refused` appears on 0 and `integrity_unobserved` on 0 — the whole mechanism landed on 2026-10-02 and has never run. D-B/D-C are prospective defects: 0/204 UNCONFIRMED entries in the D-B class, Wilson [0%, 1.85%]. They are material because the gate is new and the first run that trips it is the one that counts, not because anything has already been lost.

---

# D-A — settled by execution; the correct machine-independent measurement

Reproduced immediately: the committed producer dies on its own regression assert in this checkout.

```
$ python3 scripts/advisory_channel_selection_2026-10-02.py
    CONFIRMED total : 114 ;  THIS MERGE advisory/audit : 107 / 7   fires=True
AssertionError: REGRESSION: run 1b read no key and the advisory fired
```

105 of the 107 are path literals under the producing machine's own repo root, which run 1b records in `panel_confinement.run_root`. **But the brief and both seats state the defect one-directionally.** It is two defects, and the second is worse:

```
RED-BEFORE (three roots, one archive)      conf / adv / audit
  this sandbox                                114 / 107 /  7
  the producing machine's root                  7 /   0 /  7
  a root that is not on disk (CI)             114 / 114 /  0   <-- audit channel EMPTIES
```

At a root that does not exist, `_committed_counterpart` resolves nothing, every `carried_verbatim` flag is lost and the *merge's own "nothing is dropped" property fails in the same move as its silence property*. Fable's round-2 fix addresses only the allowlist. **The correct machine-independent measurement is `7 CONFIRMED, 0 advisory, 7 audit`, and it is only machine-independent once the counterpart lookup is pinned too.**

### Which fix stands, and why

**ADDITIVE decides it.** The runner has written `panel_confinement.run_root` into every report since 2026-09-01 and no reader consumed it — an addition nothing reaches, this project's 11-of-11 failure class. Wiring the existing field is strictly additive and the recorded root is a *fact about the run*.

I **reject fable's `_relocated_counterpart_exists` / `suffix_roots` remap**: it declares a literal in scope when its longest existing path-suffix resolves under the live root. That is a heuristic with a free parameter — any literal whose tail happens to match a repo-relative path becomes in-scope, from any tree, including one chosen for that property. The recorded root has no such degree of freedom. Simplest sufficient also favours the pin: one trusted-record read versus a suffix search.

### Delivered — `bench/key_access_forensics.py`

`trusted_record_names()` (the anti-widening rule factored out of `discover_target_dirs`, not copied), `discover_run_root()`, the recorded root **added alongside** the live one in both the allowlist and `_committed_counterpart`, and `Report.run_root_recorded` so a reader can tell a pinned verdict from a cwd-pinned one. Gated on `not confined`, which is the entire safety argument: for an exam the repository holds the exam design, so the root the run executed under is exactly what must stay out of scope.

```
GREEN-AFTER:
   conf/adv/audit = (7, 0, 7)   root=<this sandbox>
   conf/adv/audit = (7, 0, 7)   root=<the producing machine>
   conf/adv/audit = (7, 0, 7)   root=/nonexistent/checkout/of/this/repo
   invariant? True
$ python3 scripts/advisory_channel_selection_2026-10-02.py   # EXIT=0
    run 1b  advisory/audit 0 / 7  fires=False ;  planted copy 2 / 7 fires=True
    THE MERGE DOMINATES BOTH ON THESE INPUTS: True
```

exp48 is bit-identical: 12 CONFIRMED, `repo_in_scope=False`. A key read from *inside* the recorded root is still CONFIRMED — only the out-of-scope path signal consults the allowlist; `CONFIRMED_PATTERNS` and `protected` do not.

**The existing suite caught my first draft.** `test_key_access_forensics.py::test_scanner_source_names_no_protected_path` refuses an absolute home literal anywhere in the scanner source, and my docstring quoted the founder's path. That guard is right and I removed the literal. Worth naming: the hazard it blocks is precisely how `test_key_access_advisory_2026-10-02.py` was green while the producer was red.

---

# D-B — CONFIRMED. The counter and the report do not quantify over the same entries.

```
$ PYTHONPATH=. python3 bench/tests/falsifier_subcritical_refusal_is_silent_2026-10-03.py
  sev=0.9 integrity_refused=False  A4_count=1  reported=[]
  sev=0.9 integrity_refused=True   A4_count=0  reported=['C0001']
  sev=0.5 integrity_refused=False  A4_count=1  reported=[]
  sev=0.5 integrity_refused=True   A4_count=0  reported=[]      <-- silent
FALSIFIED
AssertionError: D-B CONFIRMED: ... Excluded-implies-reported FAILS.
```

`unverified_critical_count` is scoped to `status == "UNCONFIRMED"` at **any** severity (the gate was removed 2026-09-06, deliberately, on the founder's ruling that a model-assigned float must not decide convergence). `integrity_refused_criticals` still gated at 0.7. **One predicate with two scopes is two predicates** — CC2 round 2's phrasing, and it is exactly right.

Why the shipped invariant missed it: the 48-combination grid pins `severity=0.9` on every entry, and the randomised arm recomputes the expectation using *the reporter's own 0.7 gate* — it compares the reporter against itself. **Zero tests compared a consumer against its counter.**

### Fix — **SIMPLEST SUFFICIENT decides it.**

I **reject CC2's `integrity_refused_subcriticals()`**: a second method needs its own caller, its own report key and its own round-loop log line to be reachable, and an addition nothing reaches is the named top defect class. Widening the reader that is **already wired** (`_integrity_refused = registry.integrity_refused_criticals()` in the round loop) reaches every consumer for free and returns a **strict superset** — nothing that was reported stops being reported, so it also passes ADDITIVE. One disjunct:

```python
and ((e.get("severity") or 0.0) >= CRITICAL_SEVERITY_THRESHOLD
     or e.get("status") == "UNCONFIRMED")
```

The method name is kept deliberately: it is quoted verbatim in the `integrity_refused_reason` string written onto entries and into every archived registry.

**Three committed oracles pinned the defect green and I amended all three loudly, dated, with the superseded assertion preserved verbatim** — `test_a_terminal_or_subcritical_entry_is_neither` (whose own docstring claimed the reporter is scoped "like the counters", which is the false premise), `test_randomised_registries_agree`, and `test_the_excused_critical_is_reported_rather_than_lost`. I report that as a finding in its own right rather than a silent repair; the falsifier above is its evidence. I added the invariant that was missing: **`test_whatever_the_A4_counter_drops_is_named_in_the_report`**, which measures A4 with the predicate live and again neutralised and requires every dropped id to be named — a severity floor re-entering either side fails there, with an anti-vacuity assertion that a drop was actually witnessed.

---

# D-C — CONFIRMED, and it is the safety property of the whole merge.

Driven against the **real `_apply_routing`**, with an anti-vacuity control arm:

```
$ PYTHONPATH=. python3 bench/tests/falsifier_carveout_drains_a4_2026-10-03.py
INTEGRITY_VIOLATION in EQUIPMENT_FAILURE_VERDICTS : False
INTEGRITY_VIOLATION in ROUTABLE_INSTRUMENT_FAULTS : False
  observer never installed   irreducible_escalation=True   integrity_refused=None
  key-access refusal         irreducible_escalation=None   integrity_refused=True   <-- control took the other branch
MACHINE-WIDE OBSERVER FAILURE — 2 criticals, alarm bound 2
  unverified_critical_count (A4 blocker) : 0
  irreducible_queue_count                : 2  alarm fires=False
  integrity_refused_criticals (report)   : []
  criticals verified by a tool           : 0
FALSIFIED
```

A run can **CONVERGE with zero verified criticals and name none of them** — the exact outcome `_integrity_violation_excluded`'s docstring claims its carve-out prevents. The carve-out returns `False` correctly; it is simply never reached, because `unverified_critical_count` skips `irreducible_escalation` *before* calling it.

### Fix — **SIMPLEST SUFFICIENT + ADDITIVE decide it, and I reject CC2's.**

CC2 round 2 put an `integrity_unobserved and not exhausted` guard inside `unverified_critical_count` plus a releasable valve. That fixes **one of four readers** and leaves `irreducible_escalation`, `hil_escalated` and `hil_reason` standing on an entry no ladder ever reached — a false assertion in the record, which is the thing the 2026-09-07 "NEVER ASSESSED IS NOT IRREDUCIBLE" repair exists to forbid. It also adds a valve the design already supplies.

**Fix it at the stamp.** `irreducible_escalation` asserts "a machine tried and failed"; when the observer never installed, no machine tried. One condition in `_apply_routing` admits an unobserved refusal to the equipment-failure branch it already belongs in:

```python
elif ((e.get("falsifier_verdict") or "").strip().upper() in EQUIPMENT_FAILURE_VERDICTS
      or ((e.get("falsifier_verdict") or "").strip().upper() == INTEGRITY_REFUSED_VERDICT
          and e.get("integrity_unobserved"))):
```

All four readers become correct at once; no counter is touched; no new state; the entry still reaches the irreducible-queue alarm via `routing_deferred`, exactly as every other equipment failure does; and the `_defer_is_equipment` flag is extended so the record names the fault it observed.

```
CLEAN EXIT: the carve-out keeps A4 blocking
  unverified_critical_count (A4 blocker) : 2      # blocks
  irreducible_queue_count                : 2      # still visible to the alarm
```

**COMPOSABILITY, applied properly:** composing the stamp fix with a counter guard is the obvious "both can coexist" move and I decline it. There is no measurement showing the pair beats the stamp fix alone — the stamp fix already makes A4 block at the bound where it failed — so the single fix is preferred, per the founder's 2026-10-02 wording.

Test: `test_an_unobserved_refusal_keeps_a4_blocking_2026-10-03.py`, 5/5, including **`test_a_genuinely_exhausted_ladder_is_still_irreducible`** — the capability that must not be removed.

---

# Q1 — the contract is honoured, but the 537 is a numerator, not a denominator

Population: 3,029 deduplicated registry entries from the 62 of 310 run directories carrying a registry (`<run>/runner_state.json → ["registry"]["entries"]`, report taking precedence; symlinks resolved — `exp36_evidence_latest` and `experiment_18` otherwise double-count 39 accepted criticals). Criticals at severity ≥ 0.7: 1,366. Accepted = status ∈ {CONFIRMED, CLOSED, CORROBORATED}: **930**. Tool verdict = any of {CONFIRMED, REFUTED, ERROR, TIMEOUT, INTEGRITY_VIOLATION, REFUSED, UNTOOLABLE, NON_DISCRIMINATING} on `falsifier_verdict` ∥ `routing_verdict_unreconciled` ∥ `routing_history[-1]["verdict"]`.

- **All accepted criticals, no tool verdict: 393/930 = 42.2581%, Wilson [39.1216%, 45.4583%].**
- **Restricted to the 40 run dirs with any falsifier machinery: 0/537, Wilson [0%, 0.7103%].**

**The 537 reproduces exactly — and both quoted figures are decompositions of it, not of the population.** Of the 537, `falsifier_verdict` is CONFIRMED ×535, ERROR ×1, UNTOOLABLE ×1. So fable's **535/537 = 99.6276%** is the *CONFIRMED share*, Wilson [98.6523%, 99.8978%], and CC2's 536/537 is 537 minus the UNTOOLABLE. Neither is the proportion of model-reasoned findings later toolled; both are compositions of the already-toolled set. **The answer to the question as asked is 0/537 accepted with no tool verdict, Wilson [0%, 0.71%].**

Every one of the 393 comes from 17 run directories ending at `exp41c` — all pre-exp42, all before the falsifier gate. Nothing after exp41c contributes a single one. 42.26% is an **era artefact**, not a tooling gap. Zero entries rely on a routing field alone; the two routing fields add no coverage at all, and `TIMEOUT`/`REFUSED` never appear anywhere in the corpus.

# Q2 — what adjudicates prose, and a confound both seats missed

Classifier: report `target_file` extension (46 `.py`, 7 `.md`); 10 registry dirs unclassifiable, 6 of them carrying 80 accepted criticals, excluded from the 2×2 and named rather than dropped.

| stratum | n | tool verdict | Wilson 95% |
|---|---|---|---|
| PROSE | 93 | 93 | [96.0333%, 100%] |
| CODE | 757 | 391 (51.6513%) | [48.0920%, 55.1938%] |

Fisher exact, two-sided, on `[[93,0],[391,366]]`: **OR = ∞ (Haldane–Anscombe 175.059), p = 2.819486e-25** — scipy, an independent mpmath hypergeometric sum, and **Wolfram Language (local Wolfram Engine, via `wolframscript`)** agreeing: `twoSidedP = 2.819485987e-25`; Wolfram also reproduced the Wilson lower bound 0.9603324974 against statsmodels' 96.033250%.

**The answer: the lint suite is the wrong instrument and its absence is irrelevant.** The adjudicator is `reverify_falsifier`, which re-executes a falsifier; a prose falsifier is Python over text, and `re` + sympy/mpmath re-derivation are as general over prose as `ast` is over code. 93/93 prose criticals carry a tool verdict.

**But I will not let that Fisher stand as a prose-vs-code result, and both blind seats quoted one without this caveat.** All 7 prose run directories are post-gate; all 393 no-tool entries are pre-exp42. The 2×2 is largely a test of *old runs vs new runs* wearing a prose/code label. Restricted to tool-era runs both strata are 100% and the test is vacuous. The defensible claim is the univariate one: prose criticals are toolled at 93/93, Wilson lower bound 96.03%.

# Q3 — No. Do not build one. The general guard exists and reaches 7.76% of the population.

Independently reproduced CC2's reach figures from the archive:

```
criticals WITH a falsifier body                 : 567
  discrimination control left a record          :  44/567 =  7.7601%  Wilson [5.8313%, 10.2575%]
    of those, NO_DISCRIMINATION                 :  14/44  = 31.8182%  Wilson [19.9993%, 46.5569%]
    positively shown to DISCRIMINATE            :  21/567 =  3.7037%  Wilson [2.4350%,  5.5955%]
    INDETERMINATE (3 kinds)                     :   9/44
```

`run_discrimination_control` already *is* the general cannot-fail guard: it reruns the falsifier against a corrected copy and stamps `NON_DISCRIMINATING` when it fires on both. **Adding a template beside a guard that reaches 7.76% is an addition nothing reaches** — ADDITIVE refuses it. And the hazard is not hypothetical: roughly one in three of the falsifiers the guard *did* check cannot fail.

The additive move is to raise the existing guard's reach — when no corrected copy is supplied, synthesise one by inverting the asserted property — not to put a second guard next to it. I also decline to commit an unwired template module, which is fable's own stated reason for declining, and fable then committed `bench/falsifier_template.py` anyway. That is the contradiction in fable's Q3: the reasoning is right and the delivery contradicts it.

My own falsifiers in this round each carry the guard inline: `falsifier_carveout_drains_a4` **asserts the control arm took the other branch** before it reports, so a dead routing loop makes it error rather than confirm. That is the cheap general form, and it is where the guard belongs.

# Q4 — the repointing experiment, specified to run

- **Population.** The 158 named-and-CONFIRMED post-feature bodies in Cause 1's named/CONFIRMED cell, plus the 18 named ERRORs, n = 176. Precondition: the named file exists in-tree. **Now mechanically reachable** — `discover_run_root` makes each run's original root machine-readable, which it was not when either seat specified this.
- **Substitution rule.** By AST, never by rewrite. For each path literal resolving under the run's recorded `run_root`, substitute the same repository-relative path under a freshly staged byte-identical copy. Assert the body diff touches nothing but `FILE_RE`-matched spans. One substitution class per body; bodies needing ≥2 incompatible classes are logged NOT REPOINTABLE and **counted, never dropped**.
- **Two arms, because one measures nothing.** (A) replay unedited — controls for archive rot; (B) repointed. Without arm A a recovery is indistinguishable from the archive having gone stale.
- **Decider.** `falsifier_verify.reverify_falsifier` in the staged copy. Prose verdict is not an input.
- **Pre-registered rates.** H0: repointing does not change the verdict, `P(ERROR | repointed) = 18/176 = 10.2273%`, Wilson [6.5841%, 15.5257%]. H1: ERROR falls to the unnamed stratum's `10/388 = 2.5773%`, Wilson [1.4057%, 4.6833%]. Fisher two-sided at α = 0.01 on arm × {CONFIRMED, ¬}, OR with CI, scipy against an mpmath hypergeometric sum, Wolfram as second falsifier.
- **Stopping.** Fixed-N, one pass over all 176. Degraded stop: if >20% fail the precondition, publish that rate and **no comparison** — the archive is then the finding. A body ERRORing for an unrelated reason (import, syntax) is INDETERMINATE and reported, not scored, or the experiment measures my substitution instead of the coupling.
- **Why only this settles it.** Cause 1 is observational: a body naming a file may ERROR because authors who name files write more fragile falsifiers. Repointing holds the author fixed and moves only the path.

# Q5 — an amendments register, and I endorse CC2's form over fable's

`--as-of` pins the **denominator**; a rule change moves the **numerator at every date**, so no as-of value reproduces `2/640`. I reject pinning the rule set: keeping superseded gate implementations executable forever forks the predicate at each ruling, and every fork is load-bearing because historical re-execution reaches it — a second place the same bug lives and a second place every later fix must land. It also makes "we changed our mind about what counts" invisible.

Both seats delivered a register; I did not write a third, and **declining to is the standard applying to me.** Adjudicating between two written fixes rather than adding a synthesis is what SIMPLEST SUFFICIENT requires. I endorse **CC2's** form (`bench/directives/universal/rule_amendments.jsonl` + `_rule_amendment_reproduction`) over fable's for one reason that decides it: CC2's condition 2 — *`superseded` must be present in the archived brief's own text* — closes the dodge of amending a figure the brief never declared, and fable's three conditions have no equivalent. Both share the condition that makes a register evidence rather than a note: **the named producer, re-executed now with the entry's own `--as-of`, must print `current`.** The archived record is never edited; the register carries the rule; the validator says so loudly and names the ruling.

This is a design verdict from reading two delivered fixes, not a measurement I made. I mark it as such.

---

# WHAT WOULD REFUTE ME

- **D-A.** If `panel_confinement.run_root` were model-writable. It is read only through `trusted_record_names`, the rule that already guards `target_file`, and the runner writes it at exactly one site as `str(REPO_ROOT)` unconditionally. A second write site, or a model shown displacing the runner's own report, overturns the pin. **What I looked for and did not find:** a path by which the pin creates a false negative — the key-path and key-field patterns are not allowlist-gated and `protected` is tested first, so I could not construct one.
- **D-B / D-C.** If the archive prevalence were non-zero, the materiality argument would be stronger, not weaker; **it is zero, and I report that against my own case.** If `integrity_unobserved` were ever written on an entry that genuinely exhausted a ladder, moving it to `routing_deferred` would understate — the only write site reads `"observer did not install"` out of the rejection records, so it cannot be.
- **D-C specifically.** If `_irreducible_queue_split` had counted unobserved entries *and* the alarm bound were 0, the pre-fix behaviour would have blocked anyway. It is 2, and the fixture sits at exactly 2, which is why the alarm stays silent.
- **Q1.** A registry field other than the three I read in which tool verdicts live. I searched; `routing_verdict_unreconciled` exists on 4 entries corpus-wide and adds zero coverage. **What would have changed my mind and did not appear:** an accepted critical with a tool verdict in a field my predicate misses — all 537 are sourced from `falsifier_verdict` alone.
- **Q2.** A post-gate *code* run with a low toolled rate, which would separate the prose effect from the era effect. There is none in this archive, which is exactly why I refuse to report the OR as a prose finding.
- **Q3.** If the discrimination control's 7.76% reach were an artefact of my field probe rather than real absence. I checked the field shapes directly: `discrimination` on 44, `discrimination_indeterminate` on 9, outcomes `DISCRIMINATES` 21 / `NO_DISCRIMINATION` 14 / three INDETERMINATE kinds 9.

---

# STRONGEST DISAGREEMENTS

**With this brief's framing.**

1. **D-A is posed as one defect and is two.** "107 advisory / 7 audit in another checkout" is the false-positive direction. At a root that is not on disk the same archive reads **114 advisory / 0 audit** — the audit channel empties and the merge's "nothing is dropped" property fails. A fix that repairs only the allowlist leaves the second half open; fable's does.
2. **"One round reports 535/537 = 99.63%. Verify or refute it."** Both. The arithmetic is exact and the *question it answers* is not Q1: 535/537 is the CONFIRMED share of the already-toolled set. The answer to Q1 as written is 0/537, Wilson [0%, 0.71%]. A ratio whose denominator is the set you are trying to measure the complement of cannot answer the question.
3. **Q2's premise is sound and its framing invites a confounded answer.** The brief asks what adjudicates prose; the available 2×2 answers it with an era difference wearing a prose label. Both blind seats published that Fisher without the caveat.
4. **"Stop when a further pass produces no new above-threshold findings"** collided with the standards: amending three committed oracles is above threshold and had to be reported, not absorbed into a fix.

**With the blind replies.**

5. **CC2 round 2's D1 and D2 fixes are the wrong shape, though the findings are right.** `integrity_refused_subcriticals()` is a second method requiring its own wiring to be reached — CC2's own 11-of-11 argument refuses it. The D2 counter-guard plus releasable valve fixes one of four readers and leaves `irreducible_escalation`/`hil_escalated`/`hil_reason` falsely asserted on an entry no ladder reached. One condition at the stamp does both jobs with no new state.
6. **CC2's "970 silent drains over 225,280 entries" is not an archive figure and should not read as one.** Measured over the real archive: 3,246 registry entries, **0** carrying `integrity_refused`, **0** carrying `integrity_unobserved`, **0/204** UNCONFIRMED entries in the D-B class, Wilson [0%, 1.85%]. The defect is real; the quoted scale is synthetic and the reply does not say so.
7. **Fable's Q3 reasoning refutes fable's Q3 delivery.** Round 1 declines to commit an unwired guard module, naming the 11-of-11 class; round 2 commits `bench/falsifier_template.py`. The round-1 position is correct.
8. **The Cause-2 "dispute" between CC2 and fable is not a dispute.** CC2: 19/46 under both definitions once the decline is excluded. Fable: 0/46 corrected, 19/46 under the old predicate, all 19 carrying UNTOOLABLE. Same data, same mechanism, one semantic question — does a decline count as a verdict. The brief preserved it as disagreement; it is a definition, and both seats state the same underlying 19.
9. **"Left 3 tests red" — both seats say 2, and the number in this tree is different again.** My targeted run of 737 tests across every affected surface leaves exactly **one** failure, `test_cited_logs_manifest_2026-09-17::test_every_row_state_rederives_from_the_classifier`, and it is pre-existing and not a defect: 184 rows re-derive as `local_only` because this staged copy has no `.git`, so `git ls-files` censuses nothing. That is the fail-loud design working, and it is the same class CC2 traced to 6 of its 8. The red-test count is a property of the checkout, which is the very thing D-A is about.

---

# DELIVERED

| path | change |
|---|---|
| `bench/key_access_forensics.py` | **D-A fix** — `trusted_record_names()` (factored), `discover_run_root()`, recorded root added to the allowlist and to `_committed_counterpart`, `Report.run_root_recorded` |
| `bench/reference_runner_v3.py` | **D-C fix** (`_apply_routing`: an unobserved refusal joins the equipment-failure branch; `_defer_is_equipment` extended) and **D-B fix** (`integrity_refused_criticals` covers the A4 blocker's scope) |
| `bench/tests/test_forensics_verdict_is_a_fact_about_the_run_2026-10-03.py` | **new**, 14 tests — invariance across 3 roots, audit-channel survival, confined-exam gate **and its non-vacuous twin**, model-cannot-pin, disagreement refused, `/` refused, no-recorded-root unchanged, exp48 bit-identical |
| `bench/tests/test_an_unobserved_refusal_keeps_a4_blocking_2026-10-03.py` | **new**, 5 tests — incl. an anti-vacuity control and the genuinely-exhausted-ladder capability |
| `bench/tests/falsifier_carveout_drains_a4_2026-10-03.py` | **new** — D-C's runnable falsifier, drives the real `_apply_routing` |
| `bench/tests/falsifier_subcritical_refusal_is_silent_2026-10-03.py` | **new** — D-B's runnable falsifier |
| `bench/tests/test_one_predicate_excludes_and_reports_2026-10-02.py` | 2 assertions amended loudly (superseded text preserved) + **`test_whatever_the_A4_counter_drops_is_named_in_the_report`**, the consumer-vs-counter invariant that was missing |
| `bench/tests/test_key_access_advisory_2026-10-02.py` | the third oracle pinning D-B green, amended loudly |

**Regression: 732 passed, 4 skipped across every affected surface** (`-k integrity|routing|irreducible|key_access|forensic|scanner|advisory|panel_five|equipment|hil_queue|convergence|a4|predicate|supply|classifier`), 1 pre-existing non-git failure. Ruff clean on every file I authored or edited; the runner's 54 ruff errors are pre-existing and none fall in my edited ranges. Wolfram Language (local Wolfram Engine, via `wolframscript`) served as second falsifier on the Fisher 2×2 and the Wilson bound only; every other figure is open-source-tool-derived.

**Terminating.** A further pass over the merged predicate, the four readers, the advisory split and the exam confinement produced no new above-threshold finding: the one remaining residual I can name — that the irreducible-queue bound of 2 still lets a 2-critical run close around a HIL queue — is the design the alarm's own docstring states and argues for, and is below the real-world-consequence threshold now that A4 blocks on a dead observer.
<!-- verbatim-end -->
### SEAT FABLE

`route=claude_cli` `chars=18810` `tool_calls=76` `elapsed_s=1643.2` `ok=True`

<!-- verbatim-begin: fable -->
All green: 301 tests across every touched surface, both falsifiers clean, the committed producer exits 0. A further pass over the gate, the counters, and the producers yields nothing new above threshold — terminating per §6/§10. Final report, field by field.

---

# VERDICT

**The 2026-10-02 merge's design is sound; its safety headline was false.** All three disputes resolve the same way — CONFIRMED, each by a falsifier I executed against the real code in this sandbox, not by adopting either seat's prose. D-C is the material one: **before today's fix, a machine-wide observer failure converged a run with zero verified criticals in this tree — `CRITICAL_QUIESCENCE_CONVERGED` returned over 2 unobserved criticals.** The brief's own round-1 framing ("the carve-out keeps blocking") and both seats' round-1 convergence declarations asserted the invariant over the *predicate*; the defect lived in a *consumer's scope*, and only round-2 execution found it. All four defects (D-A, D-B, D-C, plus CC2-R2's D4, which I reproduced independently) are **scope defects in correct mechanisms** — CC2-R2's pattern diagnosis is the most valuable sentence either round produced. I additionally confirmed D3 (stale `integrity_refused` survives a verified replacement) and corrected the refuted `:2239` citation (F3, CC2-R1). Fixes for all of it are in the tree, red-before/green-after, 301 tests green.

# THE FALSIFIER AND ITS EXECUTED RESULT

`bench/tests/falsifier_star_db_dc_2026-10-03.py` — imports the real `reference_runner_v3` and `routing`, drives the **real `_apply_routing`** (route stubbed to an unresolved `INTEGRITY_VIOLATION`; dispatch stubbed so the transport-dead guard isn't tripped — a naive stub measures the wrong branch), then reads the real counters and the real convergence gate.

Pre-fix (`python3 bench/tests/falsifier_star_db_dc_2026-10-03.py`):
```
D-B  sub-critical (0.5) UNCONFIRMED: A4 before refusal = 1  (severity gate absent: yes)
D-B  same entry + integrity_refused : A4 after = 0, integrity_refused_criticals() = []
D-B  FALSIFIED: drained from the A4 blocker, named in NO report
D-C  unobserved entry after REAL _apply_routing: irreducible_escalation=True
D-C  carve-out predicate: _integrity_violation_excluded = False  (must keep blocking)
D-C  A4 blocker over 2 unobserved criticals = 0 ... queue = 2, bound = 2, halt alarm = None
D-C  _check_gamma_alt_convergence -> converged=True   (CRITICAL_QUIESCENCE_CONVERGED, VACUOUS CURVE)
AssertionError: defects demonstrated: ['D-B', 'D-C']     EXIT=1
```
Post-fix: `CLEAN EXIT`, EXIT=0. D4 differential (real decider, pre-fix): env-rooted path in a `shell=True` blob → **CONFIRMED (spawn allowed)**; identical path as a list element → `INTEGRITY_VIOLATION`. Post-fix: both refused; 6 honest spawn shapes carry zero false refusals.

# D-A / D-B / D-C — THE STANDARD THAT DECIDES, AND THE FIX ENDORSED

**D-A — CONFIRMED.** The committed producer aborts in my sandbox at **107 advisory / 7 audit**, so "run 1b 0/7" was a fact about one machine. The correct machine-independent measurement: **run 1b = 0 advisory / 7 audit, `fires=False`, with scope judged against the run's own recorded `panel_confinement.run_root`** — demonstrated identical from this checkout and from a second, physically distinct root (`test_run1b_is_silent_from_a_second_real_root`). **Deciding standard: ADDITIVE, and it picks CC2's fix.** The pin consumes a runner-recorded fact that had sat unread since 2026-09-01 — a recorded field no reader consumes is the additive standard's own named failure mode — while FABLE-R2's suffix-remap *infers* scope from what happens to exist under the scanner's current tree, a heuristic where a fact is available. Simplest-sufficient concurs (one trusted-record predicate, factored, both readers share it), and composability **rejects** composing the two: no committed measurement shows pin+remap dominating the pin alone on any named property — run 1b carries the field; pre-2026-09-01 archives fall back to current behaviour bit-identically, and exp48's verdict never consulted scope (re-verified: `repo_in_scope=False`, key-read hits intact). Delivered: `trusted_record_names()` factored, `discover_run_root()` (refuses `/`, refuses disagreeing records — forged-second-report attack refused by test), pin added **alongside** the live root, `Report.run_root_recorded`. Producer now exits 0 with the plant still firing 2/7 and `MERGE DOMINATES BOTH: True`.

**D-B — CONFIRMED** (first falsifier block above; 93 forensics tests + 48 merge tests unaffected). **Deciding standard: SIMPLEST SUFFICIENT, with the additive standard setting the boundary condition.** Three candidate fixes: (a) re-gate the A4 exclusion at severity ≥ 0.7 — **refused**: a sub-critical refusal would then block convergence, violating the 2026-10-02 founder ruling; (b) widen `integrity_refused_criticals` — **refused**: it requires amending two committed-oracle assertions whose scope statements are currently true of that reader, and makes the "critical(s) excused" advisory text lie; (c) **endorsed, CC2-R2's shape**: `integrity_refused_subcriticals()`, keyed on the A4 counter's own scope (UNCONFIRMED, < 0.7, same predicate), wired to the round-loop advisory and executed by `test_a4_scope_guards_2026-10-03.py`. (c) is sufficient — the drain is now named — and is the smallest change that leaves every committed oracle intact.

**D-C — CONFIRMED, and it falsifies the merge's headline claim.** The carve-out predicate is correct and was consumed correctly by the halt bound; `unverified_critical_count` skipped `irreducible_escalation` *before* consulting it, and `_apply_routing`'s refusal branch (`and not e.get("integrity_unobserved")`) guarantees unobserved entries arrive carrying exactly that flag. With queue ≤ bound (alarm fires only at `>`), the run converges verified-nothing — executed, not argued. **Deciding standard: SIMPLEST SUFFICIENT.** The fix is one condition — `if e.get("irreducible_escalation") and not e.get("integrity_unobserved")` — using the *existing* `exhausted` valve as the release (guarded by `test_the_block_is_releasable`), against the alternative of a new routing branch for unobserved entries (new state, new stamps, same effect). A permanent observer failure now burns to `max_rounds`: the fail-safe direction for a dead instrument. The founder's ruling is untouched: plain refusals still leave A4 and are still reported (guarded).

**Also fixed, same session:** D3 — `integrity_refused`/`integrity_unobserved` join `clear_stale_resolution_stamps`'s retraction list (demonstrated pre-fix: a REOPENED critical with the stale flag was excused); D4 — per-token spawn check inside the observer source (independently reproduced end-to-end before fixing); F3 — the `:2239` comment's "BOTH halves satisfied" corrected against run 1b's own record (`gamma_critical_history=[0.0, 0.0, 0.336]`, novelty tails never zero, stop=`HALTED_IRREDUCIBLE_QUEUE_ALARM`): CC2-R1's refutation of the citation verifies; the ruling stands on its own grounds.

# THE FOUNDER'S QUESTIONS

**Q1 — honoured, and I can be sharper than either seat.** My population: all 57 runner-authored `runner_state.json` registries, severity ≥ 0.7, dedup on run×cid (1306 criticals; producer `scripts/star_q1_contract_2026-10-03.py`, delivered). Predicate: accepted = status ∈ {CONFIRMED, CLOSED, CORROBORATED}; tool record = any of `falsifier_verdict` / `routing_verdict_unreconciled` / `routing_history[-1]`; adjudication = CONFIRMED/REFUTED in any of those (ERROR/UNTOOLABLE are, by the runner's own `EQUIPMENT_FAILURE_VERDICTS` definition, execution records with no reading). Feature cut (expno ≥ 42 or non-exp): **accepted with ANY tool record 496/496 = 100.00% [99.23%, 100%]; accepted with a surviving ADJUDICATION 493/496 = 99.40%, Wilson [98.24%, 99.79%]** — statsmodels, with Wolfram Language (local Wolfram Engine, via wolframscript) agreeing to all printed digits. The 535/537 figure verifies in substance on a different denominator (seats read report/checkpoint sources too; I read runner_state only). The three exceptions: the two both rounds named (`exp42_composer/C0046` CLOSED-on-ERROR, gate's first day; `sim45/C0006` CORROBORATED-on-UNTOOLABLE, quarantined by `ATTESTED_STATUSES` by design) **plus one neither seat surfaced: `shakedown_2026-09-29/arm1_harvest/C0041` — status CONFIRMED, `verified=true`, severity 0.8, standing on `NON_DISCRIMINATING` after the discrimination control voided its falsifier, with its own source model having withdrawn the claim.** That is the record-only default of the discrimination control (`discrimination_control_blocks=False`) leaving a terminal CONFIRMED on a voided instrument — the founder's recorded open decision, now with a live instance to decide it on. I changed nothing there; it is his call, and it now has a named cost.

**Q2 — the premise doesn't hold, both rounds agree, and I concur from the decider's own structure.** Ruff/mypy/bandit/pytest are the lint suite; the adjudicator is `reverify_falsifier`, which executes falsifiers, and a prose falsifier is Python over text (`re`, `pathlib`, sympy/mpmath re-derivation) with the verdict still the executed comparison. Run 1b — a prose run — carries tool verdicts throughout its registry (I read it directly for F3). The genuine gap is supply wiring (zero live-path importers of the proven prose pattern), which is a founder decision, not a review deliverable.

**Q3 — no new standalone template.** Deciding standards: ADDITIVE (an unwired second mechanism is the project's 11-of-11 class) and COMPOSABILITY's refusal arm (no committed measurement shows a template dominating an extension of `run_discrimination_control`, the cannot-fail guard that already exists and already demonstrated both failure shapes in CC2-R1's executed matrix). The additive move remains CC2's: synthesise a corrected copy when none is supplied, raising the control's reach from 7.76% [5.83%, 10.26%] toward the full falsifier-bearing population. **And my C0041 finding is the missing half of this answer: the guard that exists caught the non-discriminating falsifier and the CONFIRMED status survived anyway.** Reach *and* consequence both need the founder's decision; a new template addresses neither.

**Q4 — the repointing experiment.** Endorse FABLE-R2's registration as the base — its two-arm design (arm A: unedited replay, controlling for archive rot; arm B: repointed) is the one element that makes the result interpretable, and CC2's spec lacks it — with CC2's INDETERMINATE channel kept (a repointed body erroring for an unrelated reason is reported, never scored). Population: the 157/499 file-naming bodies (re-executed in this sandbox: 31.4629% [27.5433%, 35.6658%]), stratified ERROR vs CONFIRMED; substitution: rewrite only path spans resolving to the named file against a byte-identical staged copy, prefix map from `panel_confinement.run_root` — **now machine-readable via the very `discover_run_root` delivered today, which is what makes the experiment runnable at all**; decider: `reverify_falsifier`; pre-registered: H_general = arm-B CONFIRMED rate inside arm-A's Wilson interval; H_specificity = arm-B ERROR excess consistent with OR ≈ 4.31; Fisher two-sided, α=0.01; fixed-N, whole population; degraded stop if >20% fail the file-exists precondition. This composition is justified under the standard: without arm A, rot and coupling are confounded — a design necessity, not a preference.

**Q5 — the amendments register, ONE of them.** Both seats independently delivered the same design (committed per-ruling record; accepted only when the named producer re-executes the successor value as-of the brief's date; loud; fail-closed; archived brief untouched) and both independently rejected rule-set pinning for the same reason — superseded gates alive forever are unbounded surface. I endorse the design and rule the implementations must be **merged to one file at one path**: two registers consulted by one validator is the "fixed in one place, not its twin" shape this project has already paid for. CC2-R1's five admissibility conditions are the stricter spec (condition 2 — `superseded` must appear in the archived brief's own text — and condition 5 — re-execution of `current` — subsume FABLE's checks), so: CC2's condition set, one path, FABLE's loud `AMENDED FIGURE` naming the rule change. Deciding standard: SIMPLEST SUFFICIENT over the union.

# FIXES DELIVERED (all in this tree, all executed)

| Path | Change |
|---|---|
| `bench/reference_runner_v3.py` | D-C guard in `unverified_critical_count`; `integrity_refused_subcriticals()` + round-loop advisory wiring (D-B); D3 retraction-list additions; `:2239` citation corrected (quoted, not dropped) |
| `bench/key_access_forensics.py` | `trusted_record_names()` factored; `discover_run_root()`; recorded-root pin alongside live root; `Report.run_root_recorded` (D-A) |
| `bench/falsifier_verify.py` | `_spawn_path_tokens` + per-token spawn check in the observer source (D4) |
| `bench/tests/falsifier_star_db_dc_2026-10-03.py` | **new** — the executed falsifier, red pre-fix / clean post-fix |
| `bench/tests/test_a4_scope_guards_2026-10-03.py` | **new** — 11 guards: D-C both directions + valve, D-B scope, D3 |
| `bench/tests/test_forensics_run_root_pin_2026-10-03.py` | **new** — 7 guards: invariance across 2 real roots, forged-record refusal, `/` refusal, confined exam, exp48 unchanged |
| `bench/tests/test_spawn_blob_tokens_2026-10-03.py` | **new** — 6 guards: D4 both directions, zero false refusals |
| `scripts/star_q1_contract_2026-10-03.py` | **new** — Q1 producer, both strictness levels, three cuts |

Regression: **301 passed** across every touched surface; `advisory_channel_selection` EXIT=0 with the declared figures; `falsifier_supply_decomposition` and `claim_classifier_labelled_set` both EXIT=0; ruff clean on every file I touched. Wolfram attribution: the Q1 Wilson cross-check was computed with Wolfram Language (local Wolfram Engine, via wolframscript).

# WHAT WOULD REFUTE ME

- **D-C:** a third consumer of the carve-out I haven't traced that still drains unobserved entries. I checked all four named readers plus the `:16472` log decomposition; the halt bound and report consume the predicate correctly. A code path writing `exhausted=True` *during* an observer failure would hollow the valve guard — I did not exhaustively audit `_update_finding_statuses`'s exhaustion conditions; that is my largest residual.
- **D-A:** a runner write-site for `panel_confinement.run_root` other than `str(REPO_ROOT)`, or any archived run whose recorded root is a staging dir rather than the repo — either would poison the pin. FABLE-R1 searched and found one write site; I did not independently re-search, and say so.
- **D-B fix scope:** evidence that any status other than UNCONFIRMED is drained from any counter by the predicate at sub-critical severity — my reader would under-report it. I checked `open_crit_high_count` and the halt bound; neither consults the predicate below 0.7.
- **Q1:** a tool-verdict field outside the three I read, or acceptance statuses beyond my three. The C0041 claim fails if some artefact shows a later, surviving CONFIRMED re-verification — I searched the entry's routing history (ERROR, ERROR) and found none.
- **What I looked for that would have changed my mind and did not appear:** a false-negative path through the run-root pin (key-path/key-field patterns are not allowlist-gated — tested); a false refusal from the per-token spawn check (6 honest shapes, zero); any committed test red after my edits (none; I did not measure a pre-existing-failure baseline for the *full* suite, per the dispatch's own prohibition, but every file I touched runs green).

# STRONGEST DISAGREEMENTS

**With the brief:** (1) D-C is posed as "settle it" in neutral voice, but the artefact under review *shipped* with the claim "a machine-wide observer failure cannot drain every critical out of A4" asserted on the strength of 48 combinations and 400 randomised registries — all of which test the predicate and none of which compare a consumer against its counter. The honest statement of that invariant was always "one predicate, four readers, **two scopes**, zero scope tests." (2) The brief asks which fix to endorse for D-B before asking whether the shipped *test* should also be strengthened — it should: I note the invariant test's randomised arm still compares the report to the report's own scope; my new guards cover the gap, but the brief's framing treats the oracle as sound when the oracle's blind spot is what let D-B ship.

**With the seats:** (1) **Both round-1 convergence declarations were false when made.** CC2-R1 terminated on "the predicate's carve-out ordering is correct, `integrity_unobserved` blocks as documented"; FABLE-R1 declared the merge's design choices confirmed. Both declarations were predicate-level evidence stretched to a consumer-level claim — under §10 that is a declaration without the evidence it cites, and it is the exact failure the no-compelled-convergence rule exists to keep honest. (2) **CC2-R2's quantities remain unreproduced**: I confirmed D1/D2's mechanisms end-to-end but not "970 silent drains / 225,280" or "41/4000" — those populations are their synthetic harness, and per CC2-R2's *own* caveat they stay PLAUSIBLE as figures while the defects are CONFIRMED. My D4 reproduction, however, upgrades their weakest-labelled finding ("confirmed end-to-end but not at the layer it claims") to confirmed at exactly the layer it claims: the differential (shell blob allowed, list refused) isolates the spawn hook, because layer 3 sees neither probe. (3) **FABLE-R2's "SOUND in design and broken in one place"** undercounts by three: D-B, D-C and D3 were all live in the artefact FABLE-R2 declared converged on, and its own §10 justification ("48-state + 400-registry invariants re-run") is the predicate-scope mistake again — re-running a test that cannot see a defect class is not evidence against that class. (4) FABLE-R2's relocation fix (suffix remap) loses to the recorded fact on the additive standard's own terms, per D-A above — my seat's blind-round work, and I am overruling it with a measurement, which is how this is supposed to go.

**Terminating.** A further pass over the patched counters, the gate (both refusal directions, honest shapes), the retraction helper, and the three mandated producers surfaced no new above-threshold finding. Residuals below threshold, marked: the exhaustion-condition audit named above; the invariant test's randomised arm still scoped to ≥ 0.7 (my guards cover it; folding the scope into that file means amending a committed oracle and is the founder's call); C0041's record-only discrimination default — reported, not changed, his decision.


<!-- verbatim-end -->

Written under CDSFL note standard v1.7 (26 August 2026).
