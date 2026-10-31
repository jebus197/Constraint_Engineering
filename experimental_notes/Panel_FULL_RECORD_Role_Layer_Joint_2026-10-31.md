# The role layer joint round — both seats converged on TWO DIMENSIONS ONE LAYER

Record written 2026-10-31T03:00:00+00:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.



## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# JOINT PANEL BRIEF — the role layer, round 2. THE 2 SEATS DISAGREED.

**This is the JOINT half of `the_role_layer_b21_2026-10-30`.** That round was
BLIND: neither seat saw the other. Both have now answered, they reached
DIFFERENT verdicts, and both replies are reproduced in full below so that this
round is exposure rather than a pointer at a file.

**THERE IS NO COMPELLED CONVERGENCE AND THERE IS NO PRESSURE TO MOVE.** A seat
that reads the other's reply and does not change its verdict has done its job,
PROVIDED it says which specific claim it rejects and why. A seat that changes
its verdict has also done its job, provided it names what changed it. What is
NOT acceptable is a reply that splits the difference without engaging a
specific claim.

## WHERE YOU AGREED, MEASURED INDEPENDENTLY BY BOTH OF YOU

Both replies establish the same 3 facts by different instruments, so these are
treated as settled for this round and you should not re-derive them:

1. `bench/routing.py` — the mechanism that actually promotes and demotes —
   contains **0** occurrences of `role`, `mc.role` or `ModelConfig`. Promotion
   and demotion are not on the role axis at all.
2. `collator` is read by roughly 35 live predicates and **written by zero**
   construction sites. Every `!= "collator"` filter is therefore a tautology
   and every `== "collator"` branch unreachable.
3. `get_by_role` has **0** callers anywhere.

## WHERE YOU DIVIDED, WHICH IS WHAT THIS ROUND IS FOR

- **cc2 returned UNIFIED**: one dimension, carrying exactly 1 discriminating
  bit — arbitrator-that-dispatches-last or not — with 4 spellings. On that
  reading the founder's `worker` / `classifier` / `orchestrator` sits on the
  SAME axis at finer granularity, so the 2 vocabularies reconcile and no second
  layer is needed.
- **fable returned NEITHER**: 2 genuinely distinct dimensions, because the
  mapping is bundle-to-atoms rather than word-to-word —
  `is_arbitrator = (is_last and mc.role == "player_manager")` bundles
  *participates* and *decides* into one structural role, and `classifier` names
  no seat POSITION at all — but at most **1** new policy layer is ever
  warranted, because the structural dimension already exists as code and
  duplicating it into TOML would be an addition nothing reaches.

**THE QUESTION THIS ROUND MUST ANSWER, and it is narrower than round 1's.**

Given facts 1 to 3 above, is the disagreement SUBSTANTIVE or TERMINOLOGICAL?

  * If SUBSTANTIVE: name the concrete case the 2 positions decide differently.
    A case means a seat configuration, a dispatch, and the outcome each
    position predicts. If you cannot construct such a case, say so plainly —
    that answer is worth more than a defended label.
  * If TERMINOLOGICAL: say which of the 2 descriptions should be used in the
    code and why, and state what is LOST by adopting the other.

**AND THE 1 CLAIM EACH OF YOU SHOULD ATTACK FIRST.**

  * To cc2: fable's bundle-to-atoms argument. Does `is_arbitrator = (is_last
    and role == "player_manager")` bundle 2 of the founder's functions into 1
    structural role, and if it does, does your 1-bit reading survive it?
  * To fable: cc2's measurement that 4 role values are CONSTRUCTED against 3
    declared, with 2 undeclared synonyms behaving identically to
    `participant`. If the incumbent vocabulary is 1 bit with 4 spellings, in
    what sense is it a second DIMENSION rather than a second NAME?

## THE FOUNDER'S CAVEAT, UNCHANGED FROM ROUND 1

His words, verbatim:

    Put it to the free panel. But with the cavate that the player/manager and
    football/soccer framing was only ever meant to be an analogy anyway, to
    help us decide how things should be organised, and when models should be
    demoted/promoted. It was helpful to that extent, but the roles I have
    suggested are more descriptive and more accurate overall I feel, and I
    suspect they would be a better fit for the project as a whole? qs,pf

Facts 1 to 3 appear to settle the first half of this: the analogy's terms never
carried the promotion and demotion semantics, because those live on a disjoint
axis. Say whether you agree that this disposes of the "what does the
scaffolding hold up" question, or whether something remains.

## REQUIRED OUTPUT SHAPE

- `verdict` — one of: UNIFIED / TWO DIMENSIONS ONE LAYER / TWO DIMENSIONS TWO
  LAYERS / TERMINOLOGICAL ONLY
- `moved` — did the other seat's reply change your position? yes or no, and
  which specific claim did or did not move you
- `deciding_case` — the concrete case the 2 positions decide differently, or an
  explicit statement that you could not construct one
- `reasoning` — naming every instrument you ran
- `fix` — the path written in the sandbox tree, and what it changes
- `falsifier` — the falsifier you wrote, the command, and its executed output
- `strongest_disagreement` — your strongest disagreement with this brief's
  own framing, stated as a field even if your verdict agrees with it

## REQUIRED — use the harness

Run things. An answer that re-reads round 1's figures without executing
anything has not added a round. Both of you wrote fixes in round 1; say whether
the other seat's fix composes with yours or conflicts with it, established by
applying both.

---

# ROUND 1 REPLY — SEAT cc2, REPRODUCED IN FULL AND VERBATIM

## `verdict`

**UNIFIED** — one dimension. There is no second dimension for a role layer to be orthogonal to, because the incumbent "structural" vocabulary does not exist as a vocabulary when you measure it rather than read it.

## `reasoning`

**Instrument 1 — `scripts/how_many_role_values_does_the_code_construct_2026-10-31.py` (written this round, AST, not grep).** The brief and the existing producer both take the incumbent vocabulary to be the 3 members of `Role`. Parsing every `ModelConfig(role=<literal>)` call site in live code (excluding `bench/logs/`, which holds `sandbox_harvest` copies of older revisions of the same files) gives **4 constructed values against 3 declared**, and the distribution is the finding:

| value | declared | construction sites | what it decides |
|---|---|---|---|
| `participant` | yes | 16 | nothing — it means "not the manager" |
| `player` | **no** | 9 | nothing; behaves as `participant` |
| `reviewer` | **no** | 4 | nothing; behaves as `participant` |
| `player_manager` | yes | 2 | dispatch last + `is_arbitrator` (`run_exp20_confer.py:253`, `:533`) |
| `collator` | yes | **0** | nothing — nothing ever sets it |

`collator` is read by ~35 live predicates (`mc.role != "collator"` at `reference_runner_v3.py:13189`/`:13269` and 16 sibling runners; `mc.role == "collator"` at `runner_core.py:382`, `experiment_11_orchestrator.py:2511` and 6 others) and written by zero. The reason is in the module's own docstring, line 6: *"(caller) is collator only — no synthesis, no P-passes, no stop decisions."* **`collator` names the harness, not a seat.** It is a category error in a per-seat enum, so every `!= "collator"` filter is a tautology and every `== "collator"` branch is unreachable.

**So the live role dimension carries exactly one discriminating bit: arbitrator-that-dispatches-last, or not.** Three declared values of which one is the harness and one is a no-op, plus two undeclared synonyms of the no-op. That is not a second axis; it is one bit with four spellings.

His `worker` / `classifier` / `orchestrator` is three values on *that same axis* — what a seat is dispatched to do — at finer granularity, and it contains the one live distinction (`orchestrator` ⊇ the arbitrator bit; `worker` ⊇ everything `participant`/`player`/`reviewer` collapse to). Two vocabularies on one axis reconcile; they do not need two layers.

**The caveat's three questions, answered from the ranking code rather than the words.**

1. **Does his vocabulary drop the promotion/demotion semantics? No — and neither does the incumbent one, because the role enum never held them.** `bench/routing.py` is 988 lines and contains **0** occurrences of `.role`, `mc.role` or `ModelConfig` (`grep -c` → 0). `season_strength_order(registry, labels, frozen=None, alpha=0.05)` ranks on `labels` and measured falsification outcomes. Promotion and demotion are **label-keyed and strength-keyed, on an axis disjoint from role**. Renaming the enum drops nothing, because the enum was never load-bearing for it.
2. **Is anything dropped needed?** One thing, and it is nameable: `player_manager` encodes a *conjunction* — `run_exp20_confer.py:253-254` splits `active` into manager + participants and then dispatches **all** of them, with the manager also reviewing (`is_last and mc.role == "player_manager"`). If `orchestrator` is later read as "dispatches others, does not itself review", that dual membership is lost. That is a definition to write down, not a vocabulary to preserve.
3. **One change or two? TWO.** Measured, not judged: the enum and `routing.py` are on different axes, in different files, and `routing.py` does not read `mc.role`. Renaming `player_manager` cannot touch `season_strength_order`; retiring "season" / "players/teams should get demoted promoted" from `routing.py:543-560` cannot touch the enum. Treating them as one change is how the enum rename would silently acquire a ranking-semantics argument it has no mechanism to affect.

**Instrument 2 — `scripts/what_does_layer_order_actually_decide_2026-10-30.py` (the brief's producer).** Reproduced verbatim: 60 pairs, 17 HARD dotpaths, **0 of 60** differ on reversal, Wilson 95% [0.000000, 0.060172], one-sided exact upper 0.048703; absence `RAISE / SILENT / WARN`; `roles_dir_exists False`. Matched the brief exactly.

**Instrument 3 — `_check_monotonicity` signature and empty-dict call.** `(merged: dict[str, Any], layer_name: str) -> None` — no previous-policy parameter, so it compares against module constants. `_check_monotonicity({}, 'empty')` raises `PolicyViolationError` with **17** violations, one per protected dotpath. Order-independent by construction, confirmed by execution.

**Instrument 4 — `scripts/may_two_policy_layers_collide_2026-10-31.py` (written this round).** Four results, one of which refutes my own hypothesis:

- Sibling collisions: **0 of 60**, reproduced independently.
- **I predicted overlap with layer 1 would be pervasive, and I was wrong.** Of 98 leaf writes across 16 lower-layer files, exactly **1** overrides a `universal.toml` leaf: `convergence.advisory_d_after_round`, 3 → 2, SOFT, in `cross_domain.toml`. Override rate 1/98 = 0.010204, Clopper-Pearson 95% [0.000258312, 0.055544972] — scipy, statsmodels, mpmath (bisection, 40 dps) and Wolfram Language (local Wolfram Engine, `InverseBetaRegularized`) agree to 1e-9. **The registry is used as a disjoint namespace union, not an override stack: 97 of 98 writes add a new key.** The whole `_deep_merge` + monotonicity apparatus guards one live override.
- A collision, executed: two layers setting `verification.demo_soft` to 5 and 1 give `1` merged A→B and `5` merged B→A, with **0 warnings and no record of the discarded value anywhere in the merged policy**. Last writer wins, silently.
- Hostile role layer lowering `verification.peer_support_min_families` 2 → 1: caught at layer `'role'` in **3/3** insertion positions.

## `precedence`

**Layer 5, after model.** The role selects the seat actually doing the work, so it is the most specific selector; and the position is, by the measurement above, nearly arbitrary — it decides 0 keys today and the registry's own usage pattern (97/98 adds) says it will keep deciding ~0.

**My answer does not depend on layers being permitted to overlap.** It depends on a collision being *reported*. Overlap must stay permitted — forbidding it would disable the one override in `cross_domain.toml` and disable overriding itself, which is the engine's documented purpose and a removal with no replacement. Refusal is also wrong for a different reason: it converts a configuration-authoring mistake into a run-time abort in a project whose motivation here is substrate agnosticism. **Permit, and report.** Silent last-writer-wins on the policy that configures the measurement machinery is CDSFL core §10 category 3/4: a run is configured differently from how either file reads, and the artefact cannot distinguish the two.

## `absence_behaviour`

**WARN** — `warnings.warn` and continue, the unknown-domain precedent at `registry.py`, and the choice is evidenced rather than preferred.

- **RAISE is wrong on the founder's own stated motivation.** The reason for role management is *"We clearly cannot make such claims, and then say 'Oh, btw, that isn't really true.'"* A layer that raises on a missing file is a layer every new substrate must satisfy before it can run at all. The model layer already does this and it is the harshest behaviour in the engine.
- **SILENT is refuted by measurement, not by taste.** `tasks/` **does not exist** (`tasks_dir_exists False`). So layer 3 is not "silent when a file is missing" — layer 3 has **never applied, for any `task_id`, since the directory it reads from is absent**, and nothing announced it. The documented "four-layer configuration hierarchy" is a three-layer merge in practice. SILENT is the precedent that produced that, which is the whole argument against it.
- **WARN is the only one of the three with evidence of working as intended**: it continues (so agnosticism holds) and it announces (so a run log distinguishes "no role policy applied" from "role policy applied"). `roles_dir_exists False` today, so WARN is also what the layer will do on day one — and will say so.

## `instrument_results`

| command | key output | matched brief? |
|---|---|---|
| `python3 scripts/which_role_vocabulary_does_the_code_speak_2026-10-30.py` | `63/67 = 0.940299  Wilson [0.856305, 0.976541]`, 24 files | **yes**, and the figure is not load-bearing — see disagreement |
| `python3 scripts/what_does_layer_order_actually_decide_2026-10-30.py` | `0 of 60 pair(s)`; `[0.000000, 0.060172]`; `0.048703`; `17` HARD dotpaths; `RAISE/SILENT/WARN`; `roles_dir_exists False` | **yes, every figure** |
| `python3 -c "inspect.signature(_check_monotonicity)"` → `(merged, layer_name)`; `_check_monotonicity({}, 'empty')` | raised `PolicyViolationError`, 17 violations | **yes** |
| `python3 scripts/how_many_role_values_does_the_code_construct_2026-10-31.py --probe-reads` | declared 3, constructed 4; undeclared `['player','reviewer']`; **declared-but-never-constructed `['collator']`** | **no — refutes the brief's premise** |
| `python3 scripts/may_two_policy_layers_collide_2026-10-31.py` | siblings 0/60; ancestor overrides **1/98**; collision silent, 0 warnings; hostile caught 3/3; `tasks_dir_exists False` | partly — collision/absence as stated; **1/98 refutes my own hypothesis** |
| `wolframscript -code '…InverseBetaRegularized…'` | `{0.0102040816…, 0.00025831161124090354, 0.05554497166331361, 0.04870291331009746}`, exit 0, `Out` present, no `Name::tag` | computed; agrees with scipy/statsmodels/mpmath to 1e-9 |

Wolfram-derived values above are attributed to **Wolfram Language (local Wolfram Engine, via `wolframscript`)**. It is the second falsifier only; the open-source stack computed every value first. `wolframscript` was not on `PATH` and `timeout` is absent on this host — both worked around, neither a blocker.

## `fix`

Written into the sandbox tree at its real path: **`bench/experiment_11_orchestrator.py`** (+ two instrument scripts, one falsifier, one test file).

Enforcement at the one chokepoint every `ModelConfig` passes through:

- `ROLE_ALIASES = {"player": "participant", "reviewer": "participant"}` — only the two spellings the AST scan **found in the tree**. The founder's `worker`/`classifier`/`orchestrator` are deliberately **not** entered: which member each maps to, and whether `classifier` has a member at all, is policy.
- `canonical_role(value)` — resolves via `get_args(Role)`, so the `Literal` is the single source of truth and no second member list can drift. This is the defect it closes, so it must not reintroduce it.
- `ModelConfig.__post_init__` → `self.role = canonical_role(self.role)`. Raises `ValueError` on a genuinely unknown spelling.
- `collator` **retained**, with its 0-writer/~35-reader asymmetry documented at the declaration. Nothing replaces it and I have no committed measurement that a replacement dominates, so removing it is not available to me. It is reported for the founder, not deleted.

**This is the no-flag-day answer to the 63-values-across-24-files cost.** Normalising at construction means every reader compares against a canonical member and never against a spelling. Adopting a different role vocabulary is then **rows in `ROLE_ALIASES` plus a changed `Role`, with zero changes to the ~35 reader predicates**. Delivered and tested, not described.

**Behaviour preservation, executed:** both aliases satisfy `(alias != "collator") == (target != "collator")` and `(alias == "player_manager") == (target == "player_manager")`, so every live read is bit-identical. Exactly one behaviour changes, in one direction: `get_by_role("participant")` now finds a seat constructed as `player`, which it previously missed — and `get_by_role` has **0 callers today**, which is itself an instance of the project's named failure mode and the reason the drift was latent.

I did **not** build the role layer, and I did not compose a second fix onto this one. The silent-collision reporter is a real above-threshold defect (below) but it is a *different* defect, and I have no measurement that composing it with this fix beats either alone.

## `falsifier`

`scripts/falsifier_role_literal_unenforced_2026-10-31.py` — imports the real `bench.experiment_11_orchestrator`, constructs real `ModelConfig` objects, retypes nothing.

```
$ python3 scripts/falsifier_role_literal_unenforced_2026-10-31.py     # WITH FIX
declared Role members : ['collator', 'player_manager', 'participant']
  'player'     normalised to 'participant'
  'reviewer'   normalised to 'participant'
  get_by_role('participant') finds the 'player' seat : True
CLEAN: no undeclared spelling survives construction; the defect is not demonstrated.
EXIT=0
```

Negative control — my own patch's 7-line `__post_init__` reverted programmatically (asserted single anchor match), file restored after:

```
$ python3 scripts/falsifier_role_literal_unenforced_2026-10-31.py     # DEFECT PRESENT
  'player'     SURVIVED as 'player' -- outside ['collator', 'player_manager', 'participant']
  'reviewer'   SURVIVED as 'reviewer' -- outside [...]
  get_by_role('participant') finds the 'player' seat : False
  dispatch filter (role != 'collator') passes it     : True
FALSIFIED
AssertionError: `Role` is unenforced: ['player', 'reviewer'] survived construction outside
['collator', 'player_manager', 'participant']. Every live read is `!= "collator"`, so such a
seat is dispatched as a reviewer while a role-keyed lookup misses it.
```

Fails iff the defect is present, in both directions.

```
$ python3 -m pytest bench/tests/test_the_role_literal_is_enforced_2026-10-31.py -q
6 passed in 0.19s
$ python3 -m pytest <10 regression files that construct ModelConfig> -q
58 passed in 8.15s   /   44 passed in 3.81s
$ python3 -m bench.cdsfl_registry.registry
17 × PASS, All configs valid.
```

108 existing tests, 6 new, registry validation clean. The full suite was not run — it exceeds the dispatch budget.

## `refutation_condition`

My answer is overturned by any of:

1. **A role value other than `player_manager` changing an outcome.** If a `mc.role == "collator"` branch is reached by any live path — a construction site I missed, a dict/TOML/JSON config route, or a dynamic `.role =` assignment — then `collator` is live, the incumbent vocabulary has ≥2 discriminating values, and "one bit with four spellings" is wrong. My scan covers literal `role=` kwargs to `ModelConfig(...)` only; a non-literal or non-`ModelConfig` route would escape it. **This is the weakest link in my derivation and I name it as such.**
2. **`classifier` turning out not to be on the dispatch axis.** If a classifier is a *function applied to content* rather than a thing a seat is dispatched to be — e.g. a per-finding adjudication step that any seat performs — then it is genuinely a second dimension and ORTHOGONAL is right. I could not settle this from the code because no seat classifies today; it rests on how the founder defines it, and I say so rather than assuming.
3. **Promotion/demotion turning out to be role-keyed somewhere.** `bench/routing.py` has 0 role references, but if another ranking path reads `mc.role`, then the enum *is* load-bearing for the analogy's semantics and caveat answers 1 and 3 both flip.
4. A sibling-collision-free merge being shown to be *enforced* rather than conventional — which would make the collision reporter unnecessary.

## `strongest_disagreement`

**The brief's load-bearing premise is a tautology, and it is the sentence the fix-is-cheap argument rests on:** *"The runner reads it live at `bench/reference_runner_v3.py:13189` and `:13269` as `mc.role != "collator"` … So a caller for a role layer already exists, which the additive standard requires and which would otherwise have to be invented."*

Both cited reads test for a value **no construction site in the repository ever sets**. They are `True` for every seat that has ever existed. The brief verified that the reads exist and that the line numbers had drifted 18 lines — careful work — but did not verify that anything reaches the branch, which is the only thing the additive standard actually asks. A read nothing writes is the mirror image of the failure the standard names, and this instance has ~35 readers.

Two further disagreements, one of them with myself:

- **The brief's own refutation condition 3 is right for a reason stronger than it gives.** It says 63-to-4 should not decide it because incumbency is not an argument. The measurement says worse: **37 of those 63 occurrences are `collator`**, a value with zero writers. The tally is largely counting readers of dead code, and its denominator — a grep for 3 declared words plus 3 proposed ones — cannot see `player` (9 sites) or `reviewer` (4) by construction, so it could not have detected that the literal is unenforced. The figure is sound as a *renaming cost* and misleading as evidence about what a role *is*.
- **Against myself: I predicted ancestor overlap would be pervasive and that this would show overlap is already permitted-and-pervasive. The measurement refuted me — 1 of 98 leaf writes.** Reported because it is information. It makes the brief's framing *more* right than I expected (the layers really are near-disjoint), and it sharpens the live question rather than dissolving it: a 5-layer merge whose layers overlap on 1 leaf in 98 has no exercised override behaviour at all, so the first real sibling collision will be the first time anyone finds out it is silent.

**One above-threshold defect I report without fixing, so it is not mistaken for settled.** A leaf collision between any two layers resolves last-writer-wins with no warning, no log entry and no trace of the discarded value in the merged policy (executed: 5 vs 1 → `1` one way, `5` the other, 0 warnings). Today the exposure is 0 sibling pairs, so it is latent; adding any fifth layer is the point at which it becomes live, because a role policy plausibly wants `verification.*` or `convergence.*` — the namespaces domains already write. The fix is to record discarded values on the merged policy and `warnings.warn` once per collision — permit and report, never refuse. I did not build it: it is a second defect, not a composition with the role fix, and composing them on no measurement is the thing the composability directive forbids.

**One below-threshold observation, stated so it is not mistaken for a finding.** `HARD_CONSTRAINTS` does a strict `isinstance(actual, bool)` check with an explicit comment that `1` is not `true`; the symmetric check is absent from `HARD_THRESHOLDS`, where `isinstance(True, int)` is `True`. Executed: `convergence.hard_coverage_threshold = true` is **accepted** (`False` correctly raises). But `int(True) == 1 == ` the floor, so the accepted value is numerically identical to the required one. Type-hygiene asymmetry, no behavioural consequence, below the §6 threshold. Reported, not fixed.

## `termination`

**Four passes.**

1. Ran both named producers; verified `_check_monotonicity`'s signature and empty-dict raise; found `get_by_role` has 0 callers.
2. AST scan of construction sites → 4 constructed vs 3 declared; `collator` 0 writers / ~35 readers. **The pass that decided the verdict.**
3. Collision, ancestor-overlap, position-independence and absence instrument → refuted my own ancestor-overlap hypothesis (1/98); confirmed silent last-writer-wins; 3/3 hostile-layer catches; found `tasks/` has never existed.
4. Fix, falsifier with negative control, 108 regression tests, registry validation, and the `bool`-in-`HARD_THRESHOLDS` check.

**Pass 4 added nothing above threshold** — its one new observation (`hard_coverage_threshold = true` accepted) is numerically inert and is reported as below threshold. §6's criteria are met for the question asked: the hard assumptions were tested by execution, the one residual above-threshold finding (silent collision) is named with its mechanism and exposure rather than left implicit, and no further pass is indicated by a specific mechanism I can name. I am **not** declaring the artefacts defect-free — I am declaring this question answered and naming the weakest link in my own derivation (refutation condition 1) rather than claiming it closed.

---

# ROUND 1 REPLY — SEAT fable, REPRODUCED IN FULL AND VERBATIM

All instruments run, fix delivered red→green, neighbours green, Wolfram concurs. Final answer.

---

## `verdict`

**NEITHER.** The structural and functional roles are **2 distinct dimensions** — reconciliation is lossy in both directions — but they do **not** need 2 policy layers. The structural dimension is topology, already implemented as code and never consulted by the policy engine (`load_effective_policy` returns 9 keys, 0 mentioning role; its only live effects are dispatch exclusion and ordering). The functional dimension is the only candidate for a registry layer, so at most **1 new layer** is ever warranted. UNIFIED fails because the mapping is bundle→atoms, not word→word: `run_exp20_confer.py:533` sets `is_arbitrator=(is_last and mc.role == "player_manager")` — one structural role bundling two of his functions (participates *and* decides) — and `classifier` names no seat position. ORTHOGONAL-as-glossed ("2 separate layers") fails because the structural dimension's layer already exists as code (`experiment_11_orchestrator.Role`, `dm/_types.Role` + `RoleAssignment`), and duplicating it into TOML would be an addition nothing reaches.

## `reasoning`

Instruments run, in order:

1. **`scripts/what_does_layer_order_actually_decide_2026-10-30.py`** — reproduced every brief figure: 0 of 60 pairs order-sensitive, Wilson [0.000000, 0.060172] (closed form and statsmodels agree), one-sided exact 0.048703 (scipy = mpmath to 1e-9), 17 HARD dotpaths, absence = RAISE/SILENT/WARN, `roles_dir_exists False`, `tasks_dir_exists False`.
2. **`scripts/which_role_vocabulary_does_the_code_speak_2026-10-30.py`** — 63/67 = 0.940299 before my fix; **74/78 = 0.948718 after** (see `strongest_disagreement` on why that movement matters).
3. **Live registry execution** (`_load_toml`/`_deep_merge`/`_check_monotonicity`, no re-implementation): synthetic SOFT collision → **last writer wins** (`temperature` 0.9 vs 0.2 under reversal; monotonicity passes both orders); HARD boolean weakened from **middle and last** position → `PolicyViolationError` both times; HARD threshold **raised** above floor → permitted; `_check_monotonicity({}, …)` → raises; `inspect.signature` → `(merged, layer_name)`, no prior policy, so order-independence is by construction, confirmed by execution.
4. **Role-consumer trace**: the runner's only live role reads are `mc.role != "collator"` at `reference_runner_v3.py:13189`/`:13269` (drift from `:13171`/`:13251` confirmed). `get_by_role` has **0 callers** anywhere. `bench/routing.py` — the ranking mechanism — uses the word "role" **0 times**; `strength_order_from_evidence` ranks seats by measured refutation outcomes (Fisher exact + Holm) and refuses to rank when no pair separates. The promotion/demotion semantics live in `bench/dm/_role_assignment.py::RoleAssignment.reassign`: **PM static for run duration (HARD constraint C3), COL/PAR reassigned between rounds** on capability fingerprints with failure penalty and hysteresis.
5. **Wolfram second falsifier** (local Wolfram Engine via wolframscript): `N[1 - 0.05^(1/60)]` = 0.04870291331009746, agreeing with scipy/mpmath. *Computed with Wolfram Language.*

**On the caveat's 3 questions:**

1. **What his vocabulary drops:** (a) `collator` — the only role value live dispatch code reads; (b) the static/dynamic reassignment split, which is attached to the dm `Role` enum, not to the football words; (c) the bundle structure — `player_manager` is participate+decide, two of his atoms in one seat. What it does **not** drop: capability promotion/demotion, because that never lived in any role vocabulary — `routing.py` ranks seat labels by evidence, role-blind.
2. **Is the dropped material needed?** Collator exclusion: yes — without it the collating seat is dispatched as a finder. PM-static (HARD C3): yes — a designed invariant with an Exp14 fix history, but expressible in his vocabulary (orchestrator static, others dynamic). The *football words* themselves carry nothing; the semantics are in code keyed on role identity, so they survive a rename **iff both declarations move together** — which nothing enforced until tonight's guard.
3. **1 change or 2?** The premise is false by measurement: the ranking code (`routing.py`, `reference_runner_v3.py`, `runner_core.py`) carries **0 football terms already** — pinned by `test_the_ranking_mechanism_carries_no_football_2026-10-17.py` (AST; ran green). It names things `strength_order`, `capability_identity`, `season_strength_order`. There is nothing left to retire *from the ranking code*. What remains is **1 change confined to the role declarations** — and it is 2 declarations (`experiment_11_orchestrator.py:59` and `dm/_types.py:311`), which my guard now forces to move as 1 visible change.

## `precedence`

If and when a functional role layer is added: **universal → domain → task → role → model** (role as layer 4 of 5, before model). Derivation: on current content the position is immaterial — 0 of 60 pairs share any leaf, measured — so the choice only binds under overlap, where "most specific merges last" is the engine's documented logic and a named model's tuning is more specific than a generic role bundle. **Yes, my answer depends on overlap being permitted**, and it should be: override is the engine's stated purpose (registry.py docstring: "additions/overrides"), and the executed evidence shows the dangerous half is already position-proof — a HARD key weakened from *any* layer position raises, because `_check_monotonicity` compares against module constants after every merge. SOFT overlap is permitted-by-design; the namespace disjointness is an accident of current content, not an invariant worth a refusing gate (a gate would remove the documented override feature with no committed measurement showing disjointness dominates — the additive standard forbids that removal).

## `absence_behaviour`

**WARN — the domain precedent.** (1) Like domain and unlike model, a role would be resolved from internal configuration (the seat table), not from an explicit per-run user request; the model layer raises because the user *named* that model and silence would mean their choice silently unapplied. (2) Absence degrades safely: all 17 HARD dotpaths are enforced from constants regardless, by execution. (3) Decisive and empirical: the live role vocabulary **already contained undeclared values** — `role="player"` and `role="reviewer"` at 4 live sites — so RAISE would have retroactively broken every simulated run over a naming fork nothing read, and SILENT is exactly how that fork went unnoticed. WARN surfaces it and continues.

## `instrument_results`

| Instrument | Command | Output | Matches brief |
|---|---|---|---|
| Layer order producer | `python3 scripts/what_does_layer_order_actually_decide_2026-10-30.py` | 0/60, Wilson [0, 0.060172], one-sided 0.048703, 17 HARD dotpaths, RAISE/WARN/SILENT, roles_dir False | **Yes, all 7 figures** |
| Vocabulary producer | `python3 scripts/which_role_vocabulary_does_the_code_speak_2026-10-30.py` | 63/67 = 0.940299 pre-fix; 74/78 post-fix | Yes pre-fix |
| Live collision experiment | inline python3 via live `R._deep_merge`/`R._check_monotonicity` | last-writer-wins on SOFT; `PolicyViolationError` on HARD weaken from middle **and** last; tighten permitted; `{}` raises; signature `(merged, layer_name)` | Yes — establishes what the brief asked for |
| Absence behaviours | `load_effective_policy` calls inside producer | model RAISE, task SILENT, unknown domain WARN | Yes, 3 precedents |
| Football ratchet | `pytest test_the_ranking_mechanism_carries_no_football…` | green — ranking code carries 0 terms | Not in brief; refutes caveat Q3's premise |
| Wolfram | `wolframscript -code 'N[1 - 0.05^(1/60), 10]'` | 0.04870291331009746 (Out line present, exit 0) | Yes, agrees with scipy/mpmath |

## `fix`

Written into the sandbox tree:

- **`bench/tests/test_the_structural_role_vocabulary_cannot_fork_silently_2026-10-31.py`** (new, 4 tests): pins the explicit bijection {collator↔COL, player_manager↔PM, participant↔PAR} between the two unlinked structural declarations, and AST-scans every quoted `role=` passed to `ModelConfig` in live bench code against `typing.get_args(Role)`, with an anti-vacuity planted-stray test and a scan-liveness test. This is the mechanism that makes the caveat's feared failure — renaming one declaration and silently detaching the HARD-C3 reassignment semantics on the other — loud, whichever vocabulary he rules for.
- **`bench/tools/run_simulated_experiment.py:638`**, **`bench/tools/gemini_tool_switch_test.py:72`**, **`bench/tools/prove_ouroboros_loop_close.py:258,:260`**: `role="player"`/`role="reviewer"` → `role="participant"`. Behaviour-preserving, verified before editing: no live code compares either value (the only live role comparisons in the tree are `!= "collator"` ×2 and `player_manager` in exp20).

Deliberately **not** built: the role layer, its TOML content, or any overlap gate — per the brief's own warning and the simplest-sufficient standard.

## `falsifier`

The guard **is** the falsifier and it ran red before the fix: first execution reported `bench/tools/prove_ouroboros_loop_close.py:258/:260 role='reviewer'` as live strays (and the pre-edit run would equally have named `role='player'`), i.e. it demonstrated the defect against the real modules by import and AST, no retyped code. Commands and outputs:

- `python3 -m pytest bench/tests/test_the_structural_role_vocabulary_cannot_fork_silently_2026-10-31.py -q` → **2 failed** (strays caught) → after fix → **4 passed in 2.71s**.
- Neighbour guards: `pytest test_which_role_vocabulary… test_what_layer_order_decides… test_the_study_arms_are_expressible… test_the_ranking_mechanism…` → **39 passed**; `pytest bench/tests/test_ouroboros_loop_close.py` → **42 passed**.

## `refutation_condition`

My verdict is overturned if any of: (1) a live code path is shown that selects *policy* (not dispatch/ordering) on the structural role — then the structural dimension does belong in the registry and NEITHER collapses toward ORTHOGONAL-with-2-layers; (2) a caller is produced that passes a functional role into `compose()`/`load_effective_policy` keyed by `mc.role` — I claim the brief's "caller already exists" names the wrong caller (structural reads cannot key a functional layer; the real caller is `composer.py:1878`, which passes domain+model only); (3) somebody demonstrates `classifier` expressible as a seat position or exp20's arbitrator bundle expressible as a single functional atom — then UNIFIED is lossless and I am wrong. My WARN answer falls if a run is shown where a silently-degraded role policy caused a wrong result that a raise would have prevented — that committed measurement would justify RAISE.

## `strongest_disagreement`

The brief says "a role dimension already exists and it is not his" — singular. **Execution shows two**, unlinked: the orchestrator `Literal` and `bench/dm/_types.py:311 Role` (PM/COL/PAR), and the brief's artefact list omits `bench/dm/` entirely, which is where the promotion/demotion semantics its own caveat asks about actually live (`RoleAssignment.reassign`, PM static HARD C3). Worse, the "existing vocabulary" was already forked in live code — 4 construction sites carried values outside the declared `Literal`, unenforced and unread — so the 63-to-4 incumbency the brief prices is the incumbency of a vocabulary that could not even police its own membership. Related: the vocabulary tally is **unstable as an instrument** — it moved 63/67→74/78 partly because my conformance fix and my guard (which must quote the words it guards) feed the count. A figure that grows when you write the test for it prices nothing; the brief was right to rule it out as a decider, but for an additional, measured reason.

## Termination

**5 passes.** (1) producers reproduced; (2) registry collision/monotonicity semantics established by execution; (3) role-consumer trace — found the second declaration, the role-blind ranking code, 0-caller `get_by_role`, 4 stray sites; (4) fix + falsifier, red→green; (5) neighbour guards, Wolfram cross-check, tally re-measurement — the last pass added the tally-instability observation and **no new above-threshold finding**. Converged. One immaterial note under §8 marking, not blocking: `get_by_role` (`experiment_11_orchestrator.py:96`) has 0 callers — a selector nothing reaches, pre-existing; flagged, not fixed, since removing it is his call under the additive standard.

---

# ROUND 1 BRIEF, REPRODUCED SO THIS ROUND IS SELF-CONTAINED

# PANEL BRIEF — Is a model's ROLE 1 dimension or 2, and may policy layers overlap at all?

Round: `the_role_layer_b21_2026-10-30`. Entry B21 of `experimental_notes/CDSFL_MASTER_TASK_LIST.md`, ruled 2026-10-17. Free seats only.

## REQUIRED SECTION 1 — The question

**Are the harness's STRUCTURAL roles and the founder's FUNCTIONAL roles 1 dimension to be reconciled, or 2 orthogonal dimensions needing 2 layers — and where, if anywhere, can a role layer change an outcome?**

The founder's design intent, verbatim: *"role management, such as 'worker'... 'classifier'... and 'orchestrator'"*, individually selectable, alongside model selection. His argument for it: the project claims substrate, model and vendor agnosticism, and *"We clearly cannot make such claims, and then say 'Oh, btw, that isn't really true. Here is a list of the only models you can use.'"*

**A ROLE DIMENSION ALREADY EXISTS AND IT IS NOT HIS.** `bench/experiment_11_orchestrator.py:59` declares `Role = Literal["collator", "player_manager", "participant"]`; `:77` makes `role: Role` a required field with no default; `:96` provides `get_by_role`. The runner reads it live at `bench/reference_runner_v3.py:13189` and `:13269` as `mc.role != "collator"` — verified 2026-10-30; entry B21 cites `:13171` and `:13251`, which have drifted 18 lines each, the same drift as its `ImmuneMemory.load` citation. So a caller for a role layer already exists, which the additive standard requires and which would otherwise have to be invented.

**BUT THE 2 VOCABULARIES ARE DIFFERENT CONCEPTS.** The existing 3 are STRUCTURAL — who collates, who manages the roster, who participates — and describe a seat's place in the topology. His 3 are FUNCTIONAL, describing what a model DOES. They overlap partially rather than cleanly: `player_manager` is close to his *orchestrator* and `participant` to his *worker*, while **`classifier` has no counterpart in the enum and `collator` has none in his list**.

Artefacts under review, by path:

- `bench/cdsfl_registry/registry.py` — `load_effective_policy`, `_deep_merge`, `_check_monotonicity`, and the constants `HARD_CONSTRAINTS`, `HARD_THRESHOLDS`, `HARD_STRINGS`
- `bench/experiment_11_orchestrator.py` — `Role`, `ModelConfig.role`, `get_by_role`
- `bench/reference_runner_v3.py:13189` and `:13269` — the 2 live reads of `mc.role`
- `bench/cdsfl_registry/domains/` and `models/` — layers 2 and 4, the only 2 that exist as directories


<!-- figure: role vocabulary | scripts/which_role_vocabulary_does_the_code_speak_2026-10-30.py | 63/67 = 0.940299 -->
<!-- figure: layer order | scripts/what_does_layer_order_actually_decide_2026-10-30.py | 0 of 60 pair(s) -->
<!-- figure: order interval | scripts/what_does_layer_order_actually_decide_2026-10-30.py | [0.000000, 0.060172] -->
<!-- figure: one-sided bound | scripts/what_does_layer_order_actually_decide_2026-10-30.py | one-sided exact 95% upper bound : 0.048703 -->
<!-- figure: protected set | scripts/what_does_layer_order_actually_decide_2026-10-30.py | HARD dotpaths protected by the live check: 17 -->
<!-- figure: absence behaviour | scripts/what_does_layer_order_actually_decide_2026-10-30.py | RAISE, WARN, SILENT -->
<!-- figure: missing directories | scripts/what_does_layer_order_actually_decide_2026-10-30.py | roles_dir_exists       False -->

## HIS CAVEAT, ADDED 2026-10-30 ON HIS INSTRUCTION — READ IT BEFORE ANSWERING

The founder ruled this question to the panel and attached a caveat. It is his
position, stated so the panel is not deciding in ignorance of it. It is NOT a
verdict and the panel is not being told how to answer; a brief that argued
against it on evidence would be doing its job.

His words, verbatim:

    "Put it to the free panel. But with the cavate that the player/manager and
    football/soccer framing was only ever meant to be an analogy anyway, to
    help us decide how things should be organised, and when models should be
    demoted/promoted. It was helpful to that extent, but the roles I have
    suggested are more descriptive and more accurate overall I feel, and I
    suspect they would be a better fit for the project as a whole? qs,pf"

("cavate" is "caveat".)

WHAT THAT CHANGES IN THE QUESTION. The brief below treats the existing
vocabulary — collator, player manager, participant — and his proposed
vocabulary — worker, classifier, orchestrator — as 2 candidate systems of
equal standing, and asks whether they are 1 vocabulary to reconcile or 2
dimensions needing 2 layers. His caveat says the first was never intended as a
vocabulary at all: it was an ANALOGY adopted to reason about how seats should
be organised and when a model should be promoted or demoted, and it served
that purpose. So the panel should not weigh an analogy's terms as though they
were a designed role model.

THE QUESTION THAT REMAINS IS THEREFORE NARROWER AND SHARPER. If the football
terms were scaffolding, what did the scaffolding hold up that the descriptive
roles must still carry? Promotion and demotion are the named function. A
"player manager" is a seat that both participates and decides; "worker",
"classifier" and "orchestrator" describe what a model DOES in a run. Those are
not the same axis, and an answer that simply renames the first set as the
second may silently drop the promotion and demotion semantics the analogy was
adopted to express.

SO THE PANEL IS ASKED, IN ADDITION TO SECTION 1:

  1. Does his descriptive vocabulary carry everything the analogy carried, in
     particular the promotion and demotion semantics? Name anything it drops.
  2. If something is dropped, is it needed, or was it an artefact of the
     analogy? Answer with reference to what the ranking and routing code
     actually does, not to what the words suggest.
  3. Retiring the last football term from the ranking code is the same change.
     Say whether that is 1 change or 2.

WHAT MUST NOT BE ASSUMED. That his caveat settles the layer question. Whether
roles are 1 dimension or 2 is a question about the policy engine's structure,
and his caveat is about where 1 of the 2 candidate vocabularies came from. A
reply that answers the provenance question and calls the structural question
answered has not answered it.

## REQUIRED SECTION 2 — Use the harness

Form your answer by RUNNING the producers and the registry functions named below, not by describing them. A seat that returns prose without having run anything has not answered.

**QUESTION 2 AS THE ENTRY POSED IT IS VACUOUS ON THE CURRENT CONFIGURATION, AND THAT IS THIS BRIEF'S MOST FALSIFIABLE CLAIM.** The entry asked where a role layer should sit in the precedence, introducing it with the words *"monotonicity protects the HARD keys either way but the SOFT keys go to whichever layer merges last"*. Measured 2026-10-30: the first half holds and **the second half asserts something that does not exist**. Merging all 60 (domain, model) pairs canonically and reversed moves **0 of 60 pairs**, Wilson 95% [0.000000, 0.060172], one-sided exact upper bound 0.048703 with scipy and mpmath agreeing — because the domain files write `constraints.*`, `convergence.*` and `verification.*` while the model files write `model.*` and `protocol.*`, and **0 of 60 pairs share even one leaf key**.

Run `scripts/what_does_layer_order_actually_decide_2026-10-30.py` and try to refute that. If you can construct a pair of EXISTING layer files whose merge is order-sensitive, this brief's framing of question 2 fails and the precedence question is live after all.

**SO THE LIVE QUESTION IS THE ONE UNDERNEATH: may layers write into each other's namespace at all?** Nothing in `_deep_merge` forbids it. The disjointness is a convention that no mechanism enforces. Establish by execution what happens when 2 layers DO set the same leaf, and say whether that should be permitted, refused or merely reported.

**QUESTION 3 HAS 3 PRECEDENTS, NOT 2.** Established by calling `load_effective_policy`: a missing MODEL file raises `FileNotFoundError`; a missing TASK file is skipped in silence; an UNKNOWN domain emits `warnings.warn` and continues. A known domain whose file is missing is also silent, so the domain layer alone holds 2 of the 3 behaviours. Run it and confirm, then say which precedent a role layer should follow and why.

**MONOTONICITY IS ORDER-INDEPENDENT BY CONSTRUCTION, NOT BY LUCK.** `_check_monotonicity` receives the merged policy and a layer NAME — never the previous policy — so it compares against module constants and cannot be sensitive to order. Verify that by reading its signature and then by calling it with an empty dict, which must raise. If a role layer could weaken a HARD constraint from any position, question 2 becomes a safety question rather than a preference, and that is worth establishing either way.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete. A fix without a runnable falsifier that has been EXECUTED is a hypothesis.

Write your fix INTO the sandbox repository tree at its real path, as a file. A fix described in prose is not delivered, and a fix written to scratch space is destroyed when the sandbox is torn down. Report the exact command you ran and the output you saw.

**WHAT IS DELIBERATELY NOT BUILT, AND WHY YOU SHOULD NOT BUILD IT EITHER WITHOUT ANSWERING QUESTION 1 FIRST.** The role layer's CONTENT. Deciding what a `classifier` role constrains is policy, not plumbing, and inventing it would be the flattering-design failure this project's record names. The layer itself is a handful of lines once questions 1, 2 and 3 are answered, since it is a TOML load, a `_deep_merge` and a `_check_monotonicity` exactly like the 4 beside it.

If your fix reconciles the 2 vocabularies into 1 dimension, note that this touches **63 quoted values across 24 files** and say how you would do it without a flag day. If your fix adds a second orthogonal layer, it touches none of them — state what that costs in comprehensibility instead, because a 5-layer merge carrying 2 role dimensions is harder to reason about than the present 4-layer merge.

## REQUIRED SECTION 4 — What would refute you

State, before you conclude, what evidence would overturn your own answer.

This brief's framing is refuted if any of these holds, and you should test all 3:

1. **The vocabularies are reconcilable without loss.** If `classifier` can be expressed as a structural position, or `collator` as a function, then they are 1 dimension and the 63-to-4 asymmetry is irrelevant.
2. **Order already decides something.** If 2 existing layer files can be shown to collide on a leaf, question 2 is live and this brief has mis-stated it.
3. **THE 63-TO-4 TALLY SHOULD DECIDE IT.** This brief asserts the opposite: 63 against 4 is what any months-old vocabulary shows against 1 proposed 11 days earlier, so choosing the incumbent BECAUSE it is the incumbent is the reasoning this project exists to refuse. If you think the incumbency is nonetheless decisive, say why on grounds other than those 2 figures.

## REQUIRED SECTION 5 — Output shape

Return exactly these fields, so replies can be compared without a parser guessing:

- `verdict` — exactly 1 of: UNIFIED (reconcile into a single dimension) / ORTHOGONAL (2 separate layers) / NEITHER (state what instead)
- `reasoning` — the derivation, naming each instrument you ran
- `precedence` — where a role layer sits, and whether your answer depends on layers being permitted to overlap
- `absence_behaviour` — which of RAISE, WARN or SILENT an unregistered role should take, and why that precedent and not the other 2
- `instrument_results` — for each producer named above: the command, the output, and whether it matched this brief's stated expectation
- `fix` — the path written in the sandbox tree, and what it changes
- `falsifier` — the falsifier you wrote, the command you ran, and its executed output
- `refutation_condition` — what would overturn your answer
- `strongest_disagreement` — your strongest disagreement with this brief's own framing, stated even if your verdict agrees with it

## REQUIRED SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings; a finding is above threshold if missing it could cause a real-world failure, a violation or an unsafe condition. Report how many passes you ran and what the last pass added.

There is no compelled convergence in this round. Disagreement with the other seat, and with this brief, is preserved as information rather than smoothed to consensus. Do not attempt to reconcile your answer with anyone else's.

Written under CDSFL note standard v1.8 (17 October 2026).


Written under CDSFL note standard v1.8 (17 October 2026).


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 47 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel joint_the_role_layer_b21_2026-10-31) -->

## `verdict`

**TWO DIMENSIONS ONE LAYER.**

Unchanged from round 1 in substance (my `NEITHER` was "2 distinct dimensions, at most 1 new policy layer"), now stated in this round's vocabulary and backed by execution rather than by the bundle-to-atoms argument alone.

---

## `moved`

**No on the verdict. Yes on one sub-claim, and I name it.**

**What did not move me: cc2's "4 constructed against 3 declared, 2 undeclared synonyms behaving identically to `participant`, therefore 1 bit with 4 spellings."** I reject the inference, not the measurement. The measurement is right and I reproduced it. The inference fails at two places, both executed:

1. **The live predicates induce 3 cells, not 2.** `python3 scripts/does_the_role_space_factorise_2026-10-31.py` §A, running the real `get_dispatch_order` and the real arbitrator predicate over every spelling:

   | role value | dispatched | arbitrates |
   |---|---|---|
   | `collator` | False | False |
   | `player_manager` | True | **True** |
   | `participant` / `player` / `reviewer` | True | False |

   `distinct (dispatched, arbitrates) cells : 3`, `log2(3) = 1.584963`. cc2's "exactly 1 bit" is **REFUTED by execution**. cc2 discounts the `collator` cell because nothing writes it on the `ModelConfig` axis — which is point 2.

2. **cc2's own refutation condition 1 is met, on the declaration its scan could not see.** §E: `RoleAssignment.assign` on 3 real `ModelSpec`s returns `role_map = {'m1': 'PM', 'm2': 'COL', 'm3': 'PAR'}` — `dm_constructs_collator: True`. cc2's AST scan covered literal `role=` kwargs to `ModelConfig(...)` and cc2 flagged that as "the weakest link in my derivation". It is the link that breaks. A collator-class seat is constructed every run that goes through `bench/dm/_manager.py:106`.

**What did move me, and it is cc2's doing.** In round 1 I edited the 3 stray `role="player"`/`role="reviewer"` production sites and treated an alias table as unnecessary surface. Measured this round: empty `ROLE_ALIASES` with cc2's enforcement in place and **21 existing tests fail** across 7 files (plus `scripts/how_many_places_must_change_to_add_a_model_2026-10-16.py:276`). cc2's alias table is reached by 9 construction sites. I was wrong that it was shim-only, and I retract that part.

---

## `deciding_case`

**Constructed, and it exists in the repository today rather than only on paper.**

**Case, hypothetical form — an independent adjudicator.** 4 seats. Seat D must render the round verdict having seen every other seat's findings, and must be *excluded* from the finding-production dispatch so it is not adjudicating its own findings. The founder's `orchestrator` names exactly this and says nothing about participating.

- **cc2's position predicts:** `role="orchestrator"` is one alias row onto one incumbent cell. Aliased to `player_manager` → **4 dispatches, D produces findings and arbitrates** (the exclusion is unobtainable). Aliased to `collator` → **3 dispatches, `is_arbitrator` never evaluated, no verdict**. Those are the only two options: aliasing can only land on a declared member, and §A enumerates all three.
- **My position predicts:** `(position=excluded, function=orchestrator)` → **3 dispatches, verdict from D.**

Executed: `(excluded, arbitrates)` is empty across all 8 candidate spellings, while the 2-field encoding reaches it. Falsifier output below.

**Case, live form — and this is the stronger one, because it is running now.** The two subsystems already occupy **different cells of the product with the same three words**:

- `bench/dm/_load_balancer.py::_admissibility_mask` — PM is **excluded** from standard task allocation when K>1 (`mask[0][0] == 0`; COL and PAR get 1), while PM is static for the run (HARD C3) and the one role the failure handler never demotes.
- `bench/run_exp20_confer.py` — `player_manager` is **included** in the dispatch *and* decides.

Same concept, opposite cell on the participation axis, two live subsystems. A single axis cannot hold both assignments; a position × function product holds them trivially. That is not a configuration I invented — it is what the code does.

**Why this is substantive and not a label.** cc2's verdict carries an operational promise: adopting the founder's vocabulary is "rows in `ROLE_ALIASES` plus a changed `Role`, with zero changes to the ~35 reader predicates." §F shows that promise is void. Over all 27 maps from {worker, classifier, orchestrator} to the 3 measured cells, exactly **1** satisfies distinguishability plus the dispatch requirements — and it forces `classifier ↦ collator`, the value whose own docstring reads "no synthesis, no P-passes, no stop decisions". Add the measured fact that a classifier is dispatched (§C) and the count is **0**: z3 `unsat`, independently confirmed by exhaustive Wolfram enumeration. There is no alias table that reconciles the vocabularies. cc2's cheap-rename path does not exist.

**And the reason it does not exist is measurable, not definitional.** §C ran the real `_build_confer_prompt` across the 2×2 of (structural `is_arbitrator`) × (the policy composer's classification directive, read live from `composer._PRESET_THREE_LAYER_SCHEMA`): **4/4 cells reachable, all 4 prompts textually distinct, `structural input determines functional : False`.** Two inputs that vary independently. Collapsing them into one field would make some currently-reachable configuration unreachable — a removal, with no committed measurement that the collapse dominates.

---

## `reasoning`

Instruments run, all in this sandbox, all by execution:

1. **`scripts/does_the_role_space_factorise_2026-10-31.py`** (new, 215 lines) — §A cell count via real `get_dispatch_order` + real arbitrator predicate; §B 4th-cell reachability; §C the 2×2 prompt factorial; §D role-blindness; §E the dm declaration; §F z3.
2. **z3 4.16.0** — single-field encoding `sat` on distinguishability alone (forcing `classifier ↦ collator`), **`unsat`** once "a classifier is dispatched" is added; two-field encoding `sat`.
3. **Wolfram Language** (local WolframScript, exit 0, value printed, no `Name::tag`, no `$Failed`) — exhaustive enumeration as second falsifier: `{27, 1, {{1,0,2}}, 0, 1.5849625007211562}`. 27 maps, 1 survives the first constraint set, **0** survive with the measured dispatch fact, and `Log2[3]` agrees with Python to 1e-15. *Computed with Wolfram Language.* Open-source stack (z3, Python) computed every value first; Wolfram is corroboration only.
4. **`FailureHandler.get_recovery` executed, rounds 1–5** — see `strongest_disagreement`.
5. **`RoleAssignment.assign` / `.reassign` executed** on 3 real `ModelSpec`s.
6. **`LoadBalancer._admissibility_mask` executed** — PM excluded from standard tasks when K>1.
7. **`inspect.signature`** on `load_effective_policy` → `['domain', 'task_id', 'model']`; `composer.compose` → 0 params matching `role`; word `role` in `registry.py` and `composer.py` → **0 / 0**.
8. **Both round-1 fixes applied and cross-tested** — see `fix`.
9. **Targeted regression** — 304 + 111 = 415 tests. Full suite not run (exceeds dispatch budget, per brief).

**On the caveat's "what did the scaffolding hold up".** I do **not** agree that facts 1–3 dispose of it. Fact 1 is true as stated and I accept it: `bench/routing.py` has 0 `role` occurrences, and its functions (`strength_order_from_evidence`, `season_strength_order`, `labels_the_order_ranks`, `route`) produce an *order* — they mutate no seat's standing. The brief's **gloss** on fact 1 — "the mechanism that actually promotes and demotes", "promotion and demotion are not on the role axis at all" — is wrong twice over, and the second error is material. See `strongest_disagreement`.

---

## `fix`

Written into the sandbox tree at real paths.

**New this round:**

- **`bench/tests/test_the_role_axis_carries_demotion_2026-10-31.py`** (108 lines, 4 tests, green) — pins by execution that the structural role axis carries demotion: `DOWNGRADE_ROLE` mutating `role_map` COL→PAR, PAR→EXCLUDE escalation, PM static across `reassign`, and role-gated task admissibility. It pins *behaviour*, not spelling, so it survives whichever vocabulary the founder rules for and fails only if demotion stops being role-keyed. This is the guard the caveat's own question asks for and that fact 1's gloss would have told a reader was unnecessary.
- **`bench/run_exp20_confer.py`** — `is_arbitrator_seat(mc, is_last)`: one definition, **2 wired callers**. The predicate `is_last and mc.role == "player_manager"` was written out twice, at `:533` (behavioural) and `:579` (the dispatch log's metadata). Two copies of one rule means a vocabulary change applied to one and not the other makes the **run log name a different arbitrator than the one that actually arbitrated** — CDSFL core §10 category 4, silent evidence loss, not a visible failure. Measured after: `remaining inline copies : 0`, `callers : 2`. It also gives the falsifier a real callable target instead of a retyped predicate.
- **`scripts/does_the_role_space_factorise_2026-10-31.py`** — the instrument above.
- **`scripts/falsifier_one_role_field_cannot_express_an_excluded_decider_2026-10-31.py`** — below.

**Both round-1 fixes re-applied, because this tree arrived pristine** (no git, neither fix present; cc2's orchestrator edit was not in `experimental_notes/seat_evidence/`, so I reconstructed it from its reply and its harvested test's import list, which pins `ROLE_ALIASES` / `canonical_role` exactly). cc2's `ROLE_ALIASES` + `canonical_role` + `__post_init__` in `bench/experiment_11_orchestrator.py`; my guard test plus the 3 stray-site edits in `bench/tools/`.

### Do the two round-1 fixes compose? Measured, and the answer is *conflict first, then yes.*

**They conflict as delivered.** cc2's fix applied **alone**, my guard run against it:

```
FAILED test_every_live_modelconfig_role_is_in_the_declared_vocabulary
  bench/tools/gemini_tool_switch_test.py:72        role='player'
  bench/tools/prove_ouroboros_loop_close.py:258    role='reviewer'
  bench/tools/prove_ouroboros_loop_close.py:260    role='reviewer'
1 failed, 3 passed
```

cc2's fix makes those spellings *harmless at runtime* and leaves them in the source; my guard declares them *inadmissible in source* regardless of runtime behaviour. Opposite policies on whether an alias spelling is legitimate. They co-exist only once my 3 stray-site edits are also applied — at which point `10 passed`.

**Then they compose, and the composition dominates — by measurement, not judgement, which is what the composability directive requires.** Two disjoint failure modes:

| failure mode | cc2 alone | fable alone | composed |
|---|---|---|---|
| non-literal role spelling (`"".join(["goal","keeper"])` — no quoted `role=` in source) | **CAUGHT** → `ValueError: unknown ModelConfig role 'goalkeeper'` | blind by construction (AST scans literals) | CAUGHT |
| one-sided declaration rename (dm `Role.COL` → `CLS`, simulating the caveat's rename applied to one of the two declarations) | **MISSED** (`6 passed`) | **CAUGHT** (`test_the_two_declarations_are_in_bijection` failed) | CAUGHT |

1/2 each, 2/2 composed. And the **smaller** variant loses: strip `ROLE_ALIASES` to `{}` and keep enforcement — `21 failed, 48 passed`. So the composition also beats the simpler fix, which is the test simplest-sufficient actually demands and which I would otherwise have failed.

Final state: `304 passed` (role guards + `test_dynamic_management.py` + `test_which_role_vocabulary_2026-10-30.py`), `111 passed` (every test file constructing `ModelConfig`, plus `test_ouroboros_loop_close.py`). Control artefacts removed and verified absent (`grep -c independent_arbiter` → 0, 0).

---

## `falsifier`

`scripts/falsifier_one_role_field_cannot_express_an_excluded_decider_2026-10-31.py`. Imports the real `bench.run_exp20_confer` and real `ModelConfig`, calls the target's own `is_arbitrator_seat`, retypes nothing.

```
$ python3 scripts/falsifier_one_role_field_cannot_express_an_excluded_decider_2026-10-31.py
single-field encoding -- every value, real dispatch:
  role value        excluded  arbitrates   reaches required cell
  collator              True       False                   False
  player_manager       False        True                   False
  participant          False       False                   False
  player               False       False                   False
  reviewer             False       False                   False
  worker               False       False                   False
  classifier           False       False                   False
  orchestrator         False       False                   False

NEGATIVE CONTROL -- same requirement, 2-field encoding
  dispatch order            : ['A', 'B', 'C']
  D excluded from dispatch  : True
  2-field encoding reaches the cell : True

FALSIFIED
AssertionError: No value of a SINGLE `role` field reaches (excluded from dispatch)
AND (arbitrates): the cell is empty across all 8 candidate spellings, while the
2-field encoding (position x function) reaches it. ... cc2's UNIFIED reading
cannot express an independent adjudicator.
```

**Two-directional, executed in both directions.** Control: add `independent_arbiter` as a 4th `Role` member, exclude it from `active`, let `is_arbitrator_seat` accept it off-position — 3 edits to the target, restored after:

```
CLEAN: single-field values ['independent_arbiter'] reach (excluded, arbitrates).
cc2's 1-bit reading carries the case; the defect is not demonstrated.
EXIT=0
```

Target restored → red again. Fails iff the defect is present, exits clean iff the claim is false.

**The control is itself informative and I will not bury it.** A single field *can* encode the case — by enumerating a product cell, which is exactly what `player_manager` already is. So "1 dimension or 2" is not a question about field count; it is whether the value set **factorises**. The claim that survives is narrower and sharper than mine in round 1: cc2's specific reading — that the founder's 3 are "the same axis at finer granularity" — fails, because a refinement of a 1-D axis refines the *same* partition, and `classifier` cuts across all three cells (§C, 4/4) rather than refining one.

---

## `strongest_disagreement`

**The brief's own "settled fact 1" is settled as a sentence about `routing.py` and false as the claim the brief builds on it. Executed, `bench/dm/_failure_handler.py`:**

```
before:  {'m1': 'PM', 'm2': 'COL', 'm3': 'PAR'}
round 1: action=RETRY            role_map={'m1':'PM','m2':'COL','m3':'PAR'}
round 2: action=DOWNGRADE_ROLE   role_map={'m1':'PM','m2':'PAR','m3':'PAR'}
round 3: action=EXCLUDE          role_map={'m1':'PM','m2':'PAR','m3':'PAR'} active=['m1','m3']
```

That is a demotion, keyed on role identity, mutating the role map. Alongside it: `RoleAssignment.reassign` re-chooses COL between rounds on capability fingerprints with hysteresis while holding PM static (HARD C3), and `_admissibility_mask` gates task allocation on the same values. **Promotion and demotion are on the role axis — they are simply not in `routing.py`.** `routing.py` ranks; `bench/dm/` moves seats.

This matters beyond bookkeeping, and it is the one place this round could have gone wrong by agreeing. The brief writes: "Facts 1 to 3 appear to settle the first half of this: the analogy's terms never carried the promotion and demotion semantics, because those live on a disjoint axis." Had both seats accepted that, the panel would have told the founder his rename is free of demotion consequences — when a rename applied to `experiment_11_orchestrator.Role` and not to `dm/_types.Role` detaches `DOWNGRADE_ROLE`, `reassign` and `_admissibility_mask` from the dispatch vocabulary, silently. **The scaffolding holds up three live mechanisms.** My new guard makes that loud; it is the direct answer to the caveat's question and it did not exist before this round.

Two further disagreements:

- **The brief's framing of the round-1 agreement is itself the error, not just the gloss.** Fact 2 ("`collator` written by zero construction sites") is true of `ModelConfig(role=<literal>)` and false of the project: `role_map['m2'] = 'COL'` every run. The brief instructs seats not to re-derive facts 1–3. Facts stated at one scope and relied on at another are how both seats came to agree on something neither measured. I accepted the facts as literally written and tested the *scope*, which is not the same as re-deriving them — and the scope is where both of them break.
- **Against myself, and it is the round's most uncomfortable result.** My round-1 edits to the 3 stray sites, plus my implicit view that an alias table was surplus, were wrong: emptying `ROLE_ALIASES` breaks 21 tests. The seat I disagree with measured something I had not, and the composed fix beats my fix alone on a named property. I would have shipped the weaker one.

**One below-threshold note, marked so it is not mistaken for a finding.** `get_by_role` still has 0 callers (settled fact 3). cc2's enforcement gives it one more case it would now resolve correctly, and it still has no caller. Pre-existing, the founder's to remove under the additive standard, not mine.

**Termination: 4 passes.** (1) Located the second declaration's live COL construction and the dm demotion path. (2) Built and ran the factorisation instrument — §A refuted the 1-bit reading, §C established independence, §F the UNSAT. (3) Wrote the falsifier, ran it in both directions, cross-checked §F in Wolfram. (4) Applied both round-1 fixes, measured conflict then disjoint coverage then the 21-test alias dependency, added the demotion guard and the duplicated-predicate fix, 415 tests green. Pass 4 produced the duplicated-predicate finding (§10 category 4) and no further above-threshold finding; I am not declaring the artefacts defect-free, only this question answered, and the weakest link in my own derivation is named above — the independent-adjudicator configuration is a requirement I asserted, which is why I reached for the live PM-excluded-while-deciding case in `bench/dm` instead.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 31 recorded tool call(s).

<!-- verbatim-begin: fable (panel joint_the_role_layer_b21_2026-10-31) -->

All composed and green: 45 + 23 + 5 tests pass, `All configs valid.`, negative control exits clean. Everything needed is executed. Final answer.

---

## `verdict`

**TWO DIMENSIONS ONE LAYER** — retained from round 1, and the disagreement with cc2 is **SUBSTANTIVE**, not terminological. I constructed and executed the deciding case this round.

One scoping concession and one hardening: at `ModelConfig` scope, cc2's "one bit with four spellings" is correct and I concede it — `player`/`reviewer` were never a second dimension, they were a fork. But the system's structural role axis is **declared twice**, and the half cc2's instrument could not see — `bench/dm/_types.py:311 Role` (PM/COL/PAR) — is live, three-valued, and carries role-keyed demotion semantics, demonstrated by execution below. The structural dimension is therefore no longer `[SPECULATIVE]`; the functional dimension (whether `classifier` names a seat position or a function) still is, pending the founder's definition — which both seats independently flagged as undecidable from code.

## `moved`

**No on verdict; yes on one component.** The specific claim I reject: *"the live role dimension carries exactly one discriminating bit: arbitrator-that-dispatches-last, or not."* It is falsified by cc2's **own refutation condition 1** ("a role value other than `player_manager` changing an outcome… a non-literal or non-`ModelConfig` route would escape it — this is the weakest link in my derivation"), through exactly the route cc2 named: the dm enum. Credit where due — cc2's 4-vs-3 measurement moved me off one thing: my round-1 gloss that the bundle argument alone established two dimensions. It did not; at `ModelConfig` scope cc2's reduction is right, and it was cc2's challenge that forced the system-scope measurement which decided the round.

## `deciding_case`

Constructed and **executed**, not hypothesised (`scripts/falsifier_the_role_axis_is_one_bit_2026-10-31.py`, real imports, nothing retyped):

**Configuration:** an exp20/exp35 run — `run_exp20_confer.py:641` / `run_exp35_policy_engine.py:2170` build `DynamicManager`, whose constructor calls `RoleAssignment.assign` (`dm/_manager.py:106`) and whose round-completion calls `.reassign` (`:600`) and hands `role_map` to `FailureHandler` (`:605`). **Dispatch:** a seat assigned `Role.COL` returns repeated UNDERPERFORM across the persistence window; an otherwise-identical seat assigned `Role.PAR` does the same.

**Executed outcome:** COL seat → `RETRY` then `DOWNGRADE_ROLE`, demoted to PAR, **still active**. PAR seat → `RETRY` then `EXCLUDE`, **ejected from the run** (`_failure_handler.py:321-331`, IM_F008). Same seat, same failures; only a non-`player_manager` role value decides survival. Additionally: `RoleAssignment.assign` on a 3-seat pool constructs `Role.COL` live (`_role_assignment.py:150`), and `get_alpha/get_baseline` return different vectors for COL vs PAR (`alpha_col=[0.2,0.3,0.25,0.25]` vs `alpha_par=[0.25,0.25,0.25,0.25]`).

**What each position predicts differently:** under cc2's UNIFIED, migrating to the founder's vocabulary is "rows in `ROLE_ALIASES` plus a changed `Role`, with zero changes to the ~35 reader predicates" — complete, because the axis carries one bit. Under mine, that migration leaves the dm enum speaking PM/COL/PAR while the orchestrator speaks the new words: the two declarations of one dimension fork silently, and the within-run demotion semantics (PM-static HARD C3, COL→PAR downgrade, PAR→EXCLUDE escalation) end up keyed on a vocabulary the project no longer uses. My round-1 bijection guard exists precisely to make that fork loud; cc2's migration recipe has no mechanism that touches it.

## `reasoning`

Instruments run this round, in order: (1) tree-state scan — the sandbox was **reset**; neither round-1 fix was present, so both were re-applied from scratch; (2) grep/AST sweep re-confirming stray spellings (`player` ×8, `reviewer` ×3 as quoted `role=` kwargs; the `role="user"/"model"/"tool"` hits are genai `Content` messages, not `ModelConfig` — a grep-vs-AST trap cc2 rightly avoided); (3) caller trace of `RoleAssignment`: exp12/17/20 string mentions are **review-target vocabulary**, the real call pair is `dm/_manager.py:106/:600`, reached live from exp20:641 and exp35:2170; (4) `role_map` consumer trace: `_failure_handler.py:102/:244/:321-331`, `_load_balancer.py:177`; (5) the falsifier, executed → FALSIFIED on parts A, A2, B, C; (6) negative control → clean exit; (7) both fixes applied and the composed battery run: 45 + 23 + 5 passed, registry `All configs valid.` Wolfram was not invoked this round: no new mathematical result was derived (the evidence is execution traces and a config-vector inequality, not a statistic); round 1's figures stand unchanged and were Wolfram-cross-checked by both seats then.

Also established: exp20's dispatch (`mc.role` strings) and the dm `role_map` are **unlinked** — `role_assignment` never appears in `run_exp20_confer.py`. A dm COL demotion does not update any `ModelConfig.role`. Flagged under §8 as `[SPECULATIVE]`-adjacent design observation, not fixed: whether they *should* be linked is policy.

## `fix`

Both round-1 fixes applied; **they compose, no conflict** — established by applying both:

- Mine: `bench/tests/test_the_structural_role_vocabulary_cannot_fork_silently_2026-10-31.py` (bijection {collator↔COL, player_manager↔PM, participant↔PAR} + AST stray scan + anti-vacuity + liveness); stray normalisation in `bench/tools/gemini_tool_switch_test.py`, `prove_ouroboros_loop_close.py` (×2), `run_simulated_experiment.py`. Ran **red** (strays caught) → **green** after normalisation.
- cc2's, applied verbatim to `bench/experiment_11_orchestrator.py`: `ROLE_ALIASES`, `canonical_role` resolving via `get_args(Role)`, `ModelConfig.__post_init__`. Behaved exactly as cc2 reported: aliases normalise, unknown spelling raises `ValueError`, `get_by_role("participant")` finds alias-constructed seats, both live-read invariants preserved.

**Measured composition advantage over each fix alone** (the composability directive's required demonstration): M2 PRE — with my fix alone, runtime `ModelConfig(role="player")` **survives undeclared** (executed: `'player'`, declared? `False`); M2 POST — composed, it normalises to `'participant'`. Mirror: with cc2's fix alone, an in-tree stray literal is silently normalised with **no signal** (M2 POST shows no warning), while my guard catches it statically (planted-stray test, executed). Each fix alone misses one of the two stray-entry routes; composed, both are covered. Composed battery: **73 tests passed** (45 + 23 + 5), registry valid. Not built, deliberately: the role layer, any dm change, any `collator` removal.

## `falsifier`

`scripts/falsifier_the_role_axis_is_one_bit_2026-10-31.py` — imports the real `bench.dm._role_assignment`, `_failure_handler`, `_types`. Command: `python3 scripts/falsifier_the_role_axis_is_one_bit_2026-10-31.py`. Executed output: **FALSIFIED**, `AssertionError` with four violations (COL constructed live; 3 simultaneous live values; COL/PAR vectors differ; COL→`DOWNGRADE_ROLE`-still-active vs PAR→`EXCLUDE`-ejected on identical failures), EXIT=1. Negative control (identical-role world): **clean exit, no violations**. Fails iff the one-bit claim is false; it is.

## `strongest_disagreement`

**With this brief's settled fact 1 — specifically its second sentence.** The measurement ("`bench/routing.py` contains 0 occurrences of role") is true and I re-confirmed it. The inference printed beside it — *"Promotion and demotion are not on the role axis at all"* — is **false by execution**: the brief generalised a single-file measurement into a system property. There are two promotion/demotion mechanisms: between-run season ranking (`routing.py`, role-free — fact 1's actual scope) and **within-run role reassignment and demotion** (`RoleAssignment.reassign` with hysteresis and failure penalty; `FailureHandler` DOWNGRADE_ROLE), which is role-keyed and live. Consequently the founder's caveat is **not fully disposed of** by facts 1–3: the scaffolding does hold something up — the within-run demotion machinery in `bench/dm`, PM-static HARD C3 included. His rename can proceed, but it must move **both** declarations together (the guard now forces this), and the migration bill is not "alias rows plus a changed Literal." Secondary disagreement, same root: fact 2's "written by zero construction sites" is true at `ModelConfig` scope but presented unscoped, while `Role.COL` is constructed live at `_role_assignment.py:150`.

**Termination:** three passes this round. Pass 1 re-established tree state and ran the dm trace (decided the round); pass 2 wrote and executed the falsifier plus negative control; pass 3 applied both fixes and ran the composed battery. Pass 3 added no new above-threshold finding. Converged per §10: the residual open items — the classifier definition and the unlinked dispatch/dm role systems — are named with mechanisms and owners (the founder's policy call), not left implicit.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/joint_the_role_layer_b21_2026-10-31/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
