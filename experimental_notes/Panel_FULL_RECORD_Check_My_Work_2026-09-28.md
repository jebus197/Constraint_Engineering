# Check CC1 work — 4 defects found in the assistant own fixes

Record written 2026-09-28T23:57:28+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

Dispatched 16:52 on 2026-09-28 after the founder's CLI login was restored, replacing the round that had failed at authentication that morning. His scope, verbatim: "The panel review completion should mostly be just to check your work." The brief told both seats to assume a 4th defect existed, because 3 had already been caught that day in CC1's own fixes.

They found it, and more. 4 faults in CC1's work of the preceding 18 hours, each confirmed afterwards by CC1 executing the code rather than accepting the report.

FAULT 1, the paid-dispatch gate did not work. `PAID_LEDGER` pointed at a file that does not exist, and the real committed ledger is a mapping where the parser demanded a flat list. 11 tests passed only because every one monkeypatched a synthetic file of the right shape; the green never touched the real record.

FAULT 2, the path classifier was still evadable. `classify_write('/tmp/../repo/hooks/evil.py', '')` returned `transient` — a write landing inside the repository read as harmless scratch.

FAULT 3, the naming advisory reported a clean 0.0000% when it could see nothing at all. `repo_hits` shells `git grep`; a panel sandbox has `.git` severed, so every phrase returned -1 and `check()` silently dropped them all.

FAULT 4, 3 written claims were unsafe, including one in the note written that same day: the assertion that `--mcp-config` appears nowhere in the repository, when it is at `bench/wolfram_standard.py:194`.

The seats also DISAGREED about the public explorer and the disagreement was preserved rather than voted on, per `feedback_no_model_voting`. The founder then dissolved it by ruling that the choice was not binary, which produced the 2-mode explorer of the same evening.

All 4 faults were fixed on 2026-09-28 under FFAFP with mutation evidence, in a 4-agent workflow whose reports are held with this round.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel brief — check CC1's work of 2026-09-28

## SECTION 1 — The question

The founder's instruction, verbatim: *"The panel review completion should mostly be just
to check your work."* So this is not a design round. **The single question is whether the
7 pieces of work CC1 landed in the last 18 hours are CORRECT, and whether any of them is
a fix that does not fix, a measurement that measures nothing, or a claim wider than its
evidence.**

He also set the standard for how your answers are treated, verbatim: *"Your role is not
simply to dispatch seats and take them blindly at their word. You need to check they
actually make sense, when ran against the existing code."* CC1 will adjudicate what you
return against the code. Return things that survive that.

**The prior is that some of this IS wrong.** In the same 18 hours CC1 shipped 3 defects
into its own fixes and caught them only by executing: a naming check whose first design
returned 24 findings that were nearly all sentence fragments while MISSING the faults it
was built for; a harvest fix whose first version would have excluded the ENTIRE `bench/`
tree from every simulated run; and a blind-spot measurement that compared a tool with
itself and reported a reassuring 0%. Assume there is a 4th.

## SECTION 2 — Use the harness

Form every answer by RUNNING the machinery, not by describing it.

`S_k` bears on items 6 and 7, both of which concern what may be admitted or rejected on a
target that is not a program. **`nu_star` and the break-even bear on item 1**, which is a
question about a PUBLISHED tool's stopping rule. `gamma` and the two-sided gate bear on
none of this; say so if you find otherwise rather than reaching for them.

## SECTION 3 — Produce a fix, and test it

A finding without a fix is half an answer. A fix without a falsifier you have EXECUTED is
a hypothesis. Deliver every fix by WRITING IT INTO THE SANDBOX REPOSITORY TREE AT ITS REAL
PATH; a fix in prose is not delivered and a fix in scratch space dies at teardown.

<!-- figure: harvest loss | scripts/panel_harvest_loss_2026-09-22.py | 73.3333 -->

73.3333% of scripts delivered by seats have historically never reached `scripts/`, 33 of
45, Wilson 95% [58.9612%, 84.0351%]. Do not let yours join them.

A STORED falsifier may not call Wolfram; anyone reproducing this project must not need it
installed. You SHOULD use Wolfram while reasoning, with the open-source tools primary.

## SECTION 4 — The 7 things to check, and 4 questions left open

**1. THE PUBLISHED EXPLORER'S STOPPING RULE — highest stakes, because it is public.**
`explorer/index.html` is served at `jebus197.github.io/Constraint_Engineering/explorer/`.
Line 83 labels its slider `theta  stopping threshold on ΔR`; line 294 colours a pass green
on `s.dR >= o.theta` alone. CC1 claims this is the quantity
`docs/MATHEMATICAL_APPENDIX.md:217` RETIRED on 2026-09-21, that the correct quantity is
`:225`'s `R*q*sigma*(1-nu) - nu*(1-R)`, and that the error is STRICTLY one-directional —
1309 of 14440 grid points where the explorer stops and the appendix continues, 0 the
reverse, with z3 returning unsat on the general form ever falling below the explorer's dR.
**Attack all 3 claims.** Is the explorer's recursion actually wrong for its own stated
model, or is CC1 reading a trajectory display as a decision rule? Does the proposed
revision preserve what `dR` is legitimately for? And CC1 asserts Astra's proposed `R*q` is
ALSO wrong, being the sigma=1, nu=0 corner — check that against `:223`.

**2. THE HARVEST PROVENANCE FIX.** On a round where BOTH seats failed at authentication
with 0 tool calls and wrote nothing, the dispatcher printed "seats proposed edits to 8
file(s)" and "harvested 3394 byte(s) of seat-written files". CC1's diagnosis: the sandbox
is a copy of the repo, the dispatcher writes its log INTO the copy, and those writes read
as seat changes. Its fix excludes the run's own log directory, identified as the ancestor
of the harvest destination sitting directly inside a directory named `logs`.
**Check the exclusion is not too wide** — a seat asked to write a measurement under
`bench/logs/` must still be harvested — **and not too narrow.** The first version used
`dest.parents[2]` and would have excluded all of `bench/`; confirm the replacement is
right for all 3 destination shapes, and look for a 4th shape CC1 did not enumerate.

**3. THE PAID-DISPATCH LEDGER.** The founder's ruling: no paid dispatch without his
express authorisation. CC1 made the free seats the default and gated paid seats on a
committed ledger quoting his authorisation. **Find the bypass.** CC1 states in the code
that the enforcement is auditability rather than impossibility — test whether even that
holds, and whether the 4 launch sites that skip the policy layer can reach a paid route.

**4. THE 3 UNREVIEWED CLASSIFIER CHANGES** in `hooks/ffafp_audit.py`: a `classify_write`
adapter, a `shell_bindings` alias, and classification on the LITERAL LEADING PREFIX plus
LITERAL EXTENSION so a variable in a filename no longer hides a write. No seat has seen
these. **Find the evasion that still gets through.**

**5. THE NAMING CHECK, whose own hypothesis CC1 reports as REFUTED.**
`scripts/note_naming_check_2026-09-28.py`. Requiring a term to be used WITHOUT
introduction removes only 8.9744% of findings over 40 of 427 notes, so it cannot block;
density 1.7750 per note makes it an advisory only. CC1 documents 2 structural blind spots:
it cannot see a COLLISION, and it goes blind retrospectively. **Check the measurement
reproduces, and check the blind spots are the only ones.**

**6. THE SESSION'S OWN `grep` HIDES MOST FILES.** `scripts/shell_grep_blind_spot_2026-09-28.py`
reports 3743 of 5245 matching files never shown = 71.3632%, Wilson [70.1245%, 72.5706%],
because the shell function wraps ugrep with `--ignore-files` and `.gitignore` excludes
`bench/logs/**`. **Reproduce it.** Then answer the question CC1 did not: WHICH PAST CLAIMS
IN THIS REPOSITORY ARE UNSAFE because they rest on a search that returned 0? Name specific
files and lines. This is the item most likely to have consequences beyond its own fix.

**7. THE WOLFRAM ROUTE WAS NEVER DEAD, and a standing document says it was.**
`.claude/CLAUDE.md` records the hosted route DISABLED 2026-09-10 "BECAUSE IT IS DEAD",
citing 42 of 43 connection failures from 2026-09-04, Fisher exact p = 2.199086e-14. CC1
now claims that figure measures the `npx mcp-remote` STDIO SHIM's attach success — the
health script's patterns key on the literal string `WolframCloud`, the removed entry's
NAME — and not the endpoint's reachability; and that the official Wolfram connector to the
SAME host answers correctly today. **Check whether the figure supports the inference that
was drawn from it**, and whether re-scoping it is the right correction or an
over-correction in the opposite direction.

**LEFT OPEN, and secondary to the 7 above.** (8) HOW to widen the extractor beyond a
fenced code block to any computable STEM element, and what must NEVER be claimed
computable. (9) Whether a prose-target rejection should require a HIGH severity finding —
the founder's worry is a HIL queue growing unmanageably, so answer with counts. (10) A
guard against editing the tree during a measurement; CC1 invalidated a full suite run 5
times in one day this way, and the obvious guard could deadlock a session. (11) The owed
Stop-gate fixture, whose 2 predecessors examined nothing because `fa.scan` handed
`fa.audit` no turn.

## SECTION 5 — What would refute you

For each item, state before concluding what evidence would overturn your answer. On item 1
name what would show the explorer correct as it stands. On item 2 name the seat file your
exclusion would wrongly drop. On item 6 name a claim you checked that turned out SAFE.

## SECTION 6 — Output shape

Per item: `id`, `verdict`, `reasoning` with file and line, `fix_path` or NONE with the
reason, `falsifier_path`, `falsifier_command`, `falsifier_output` verbatim,
`additive_check` naming the caller that reaches your change and the test that executes it,
and `refutation_condition`. Then overall: `strongest_disagreement` with this brief's
framing, which must not be empty, and `passes_run`.

## SECTION 7 — Termination

Stop on diminishing returns: when a further pass adds no finding above the
real-world-consequence threshold. Say how many passes you ran and what the last one added.
Do not manufacture findings and do not nitpick style. **If you cannot finish all 11, do
fewer properly and say which you did not reach.**

Disagreement with the other seat is information. Do not smooth it away.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 169 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel check_my_work_2026-09-28) -->

All fixes delivered and executed. Writing up.

---

# Panel seat — check of CC1's work, 2026-09-28

**Passes run: 4.** (1) orient + derive item 1 on SymPy/z3; (2) fan out on items 2/3/4/7, reproduce item 6; (3) write + execute the four fixes; (4) regression sweep and discrimination checks. Pass 4 added one finding above threshold (the hook-mirror drift my own item-4 fix creates) and nothing else, so I stopped.

**Reached: 1, 2, 3, 4, 6, 7. Not reached: 5, 8, 9, 10, 11.** I did fewer properly rather than all badly, as instructed.

---

## `id: 1` — the published explorer's stopping rule

**`verdict`: DEFECT CONFIRMED, but not the one CC1 diagnosed. Claim A confirmed, claim C confirmed, CLAIM B REFUTED. CC1's proposed fix would have broken the page.**

**`reasoning`.** Three separate results, all derived:

- **Claim A — confirmed.** `explorer/index.html:176` sets `dR: R_old - R_new`. SymPy reduces that, at σ=1, ν=0, to `R*q*(R-1)/(R*q-1)` — *bit-identical* to `MATHEMATICAL_APPENDIX.md:217`'s retired `q·R(1−R)/(1−qR)`. At ν=0 generally it is `σ ×` that same expression. The page ships the retired quantity scaled by σ.
- **Claim C — confirmed.** z3 returns **unsat** on `E_225 < dR` over the open box. The appendix form never falls below the explorer's.
- **Claim B — REFUTED, and this is the load-bearing disagreement.** `:225`'s `R·q·σ·(1−ν) − ν·(1−R)` is the improvement of the *two-branch mixture* `R(1−qσ)(1−ν)+ν`. SymPy: `R − mix − E225 == 0` ✓. But `Rbase − R(1−qσ) == 0` is **False** — the explorer's `σ·R_det + (1−σ)·R` is a *different recursion*. At R=.85, q=.45, σ=.9 they give 0.766 vs 0.506.

  Decisively: **`bench/reference_runner_v3.py:11947–11961` — the repo's own canonical `compute_rk` — implements the EXPLORER's recursion verbatim** (`R_det`, then `sk*R_det + (1-sk)*R_old`, then `*(1-nu_eff)+nu_eff`). The explorer is faithful to the shipped model. Pasting `:225` over `dR` would have made the ΔR bars stop equalling the drop in the trajectory drawn directly above them — a fix that introduces a defect.

  CC1 is right that Astra's `R·q` is the σ=1,ν=0 corner (SymPy: `E225.subs({s:1,nu:0}) == R*q`), but `:225` already says exactly that in prose. That claim is correct and adds nothing.

**So what *is* wrong?** The page contradicts *itself*, and that needs no appeal to the appendix. `:295` latched `stopAt` on the **first** pass under θ and never revised it. `dR` is unimodal in R with peak `R* = (1−√(1−q))/q` — SymPy confirms this critical point is **independent of σ**, so the appendix's premature-stop band is inherited whole. The default preset opens at π=0.85, above R*=0.574 at q=0.45; its first four `dR` values *rise* 0.0719 → 0.1060.

**`fix_path`: `explorer/index.html` (lines 289–348).** Stop is now the **last** crossing (exhaustion), scanned backwards; the first crossing is *shown*, not hidden, annotated with R* when it sits above the peak. `dR` itself is untouched — it is correct as the trajectory drop, and the θ slider still colours each bar.

**`falsifier_path`: `scripts/explorer_stopping_rule_2026-09-28.py`** — extracts `simulate()` and the stop block **verbatim from the real page** and runs them under node; no Wolfram.

**`falsifier_command`:** `python3 scripts/explorer_stopping_rule_2026-09-28.py`

**`falsifier_output`** (fixed page, then the same falsifier against a reverted copy):
```
slider-reachable grid points swept      : 129960
points where the page announces a stop  : 128797
points where a LATER bar clears theta   : 0 = 0.0000%
peak of dR at q=0.45 (default preset)   : R* = (1-sqrt(1-q))/q = 0.574178  -- independent of sigma, SymPy-derived

CONSISTENT: wherever the page announces a stop, no later bar on the same chart stands above theta.
EXIT=0
```
```
FALSIFIED
  worst case: {'pi': 0.05, 'p': 0.95, 'eta': 1, 'sigma': 1, 'nu': 0, 'theta': 0.001, 'pert': 0.3}
    announced stop = pass 3, yet a later pass reaches dR = 0.279021 >= theta = 0.001
AssertionError: explorer/index.html contradicts its own chart at 28981 of 129960
slider-reachable points
```
**22.30% of the page's own slider space was self-contradictory.** 337 of those need no perturbation at all.

**`additive_check`.** Caller: `draw()` in `explorer/index.html`, the sole renderer, on every slider `input` event. Test: the falsifier above, demonstrated to fail on the pre-fix page and pass on the fixed one.

**`refutation_condition`.** The explorer is correct as it stands if `stopAt` were never read as a decision — but `:302–304` prints `stop ≈ pass N` in θ-gold beside the θ rule. Show me that `dR` is monotone in R for some slider-reachable (q,σ,ν) and the peak argument dies. Show me that `reference_runner_v3.py:11959` does *not* define the operational recursion and claim B revives.

---

## `id: 2` — the harvest provenance fix

**`verdict`: THE EXCLUSION IS CORRECT. THE FIX IS HALF-APPLIED — it repairs one of the two numbers its own docstring names.**

**`reasoning`.** `panel_sandbox._run_log_dir` (`:560–582`) and `_is_dispatcher_own_output` (`:585–615`) are right. No `parents[N]` survives. All three documented shapes — plus **a fourth CC1 did not enumerate, the run directory itself** — resolve to `bench/logs/myround` (executed, output below). Prefix collisions are handled (`startswith(rel + "/")`).

But `panel_sandbox.py:594–600` cites **two** symptoms from the 0-work `founder_verdicts_2026-09-28` round: *"harvested 3394 byte(s)"* **and** *"seats proposed edits to 8 file(s)"*. Only the first passes through `harvest()`. The second is built at `bench/confer_maths_panel_2026-09-05.py:893` by calling `panel_sandbox.changes()` **directly, unfiltered**, and written to `seat_proposals.diff` — the file a reader opens to see what seats proposed. On a round where nobody wrote anything it would still say 8.

**`fix_path`: `bench/confer_maths_panel_2026-09-05.py`** (proposals block) — filters through the *same* `_run_log_dir` / `_is_dispatcher_own_output` pair. One rule, one implementation, two call sites; the exclusion count is printed, not swallowed.

**`falsifier_path`: `bench/tests/test_proposals_exclude_dispatcher_own_output_2026-09-28.py`**

**`falsifier_command`:** `python3 -m pytest bench/tests/test_proposals_exclude_dispatcher_own_output_2026-09-28.py bench/tests/test_harvest_excludes_its_own_output_2026-09-28.py bench/tests/test_paid_dispatch_needs_authorisation_2026-09-28.py -q`

**`falsifier_output`:** `41 passed in 1.00s`, plus the shape check and the discrimination proof:
```
bench/logs/myround/sandbox_harvest/cc2/attempt-1 -> bench/logs/myround
bench/logs/myround/worktree_harvest/x            -> bench/logs/myround
bench/logs/myround/panel_worktree_harvest        -> bench/logs/myround
bench/logs/myround                               -> bench/logs/myround   <- the 4th
PRE-FIX  block contains _is_dispatcher_own_output: False <- test would FAIL
POST-FIX block contains _is_dispatcher_own_output: True  <- test PASSES
```

**`additive_check`.** Caller: `main()` in `confer_maths_panel_2026-09-05.py` at the post-round proposals block, reached on every panel round. Tests: the five classes above, including `TestTheCallSiteIsActuallyWired`, which fails on the pre-fix source.

**`refutation_condition` — the seat file my exclusion would wrongly drop.** It would be `bench/logs/otherrun/seat_measurement.json`: a seat's measurement under `bench/logs/` but outside this run. `test_a_seat_measurement_in_another_run_directory_is_kept` asserts it survives, and it does. `bench/dm/_convergence.py` (the `parents[2]` casualty) also survives. If either were dropped, my fix is too wide.

---

## `id: 3` — the paid-dispatch ledger

**`verdict`: THE GATE IS INERT. It reads a path that has never existed, and the shipped ledger has an incompatible schema. Every existing test monkeypatches the defect away. This is the 4th defect the brief predicted.**

**`reasoning`.** `PAID_LEDGER` resolved to `bench/paid_dispatch_authorisations.json` — **`is_file() → False`**. The committed ledger is at `bench/directives/universal/paid_dispatch_authorisations.json`, is a **dict** with `authorisations`/`rounds`/`founder_verbatim`, not the **list** of `{round, founder_authorisation}` the parser requires. Executed:

```
gate on real round: (False, 'no authorisation ledger at .../bench/paid_dispatch_authorisations.json')
```
for `maths_panel_2026-09-20`, a round the founder authorised in his own words (*"OK launch the panel…"*, £12 ceiling).

It fails **closed**, so nothing overspent — but the module's own claim at `:397–398`, *"paid dispatch remains available by exactly the same route it always had"*, was **false**. There was no input yielding a paid seat. The first person needing one must move the path or delete the guard — the exact failure `paid_dispatch_authorisations.py:10–14` exists to prevent.

**Why it survived:** all 11 cases in `test_paid_dispatch_needs_authorisation_2026-09-28.py` — *including the anti-vacuity case* — bind `PAID_LEDGER` to a `tmp_path` file they write themselves. The suite proved the parser works on a synthetic ledger and never asked whether the shipped one is reachable.

**On the brief's "4 launch sites":** the count is a substantial undercount. 65 files carry both a `__main__` and a reachable paid transport; **1** calls the gate. `reference_runner_v3.py:16408` defaults to 4-of-5 paid seats and consults only the suite record. And inside the gated file, `:456` binds `MODELS` from `PANEL_ONLY` **at import time**, ungated. I did not fix these — that is a design round, not a check.

**`fix_path`: `bench/confer_maths_panel_2026-09-05.py`** — path corrected; new `_paid_ledger_entries` normalises **both** shapes so all 11 existing tests keep passing unmodified (I did not rewrite a test to fit a fix).

**`falsifier_path`: `bench/tests/test_paid_dispatch_needs_authorisation_2026-09-28.py` → `TestTheShippedLedgerIsActuallyReachable`** (5 cases, **no monkeypatch**).

**`falsifier_command`:** `python3 -m pytest bench/tests/test_paid_dispatch_needs_authorisation_2026-09-28.py -q`

**`falsifier_output`:** `16 passed in 0.19s` (11 original + 5 new). And:
```
LEDGER exists: True
authorised round : (True, "authorised for round 'maths_panel_2026-09-20': OK launch the panel...")
unauthorised round: (False, "no ledger entry for round 'check_my_work_2026-09-28'")
```

**`additive_check`.** Caller: `main()` → `select_models(_ONLY, LOGS.name)` at `:832`. Tests: the 5 new cases, one of which (`test_the_committed_shape_is_not_read_as_a_prefix_or_range`) guards against the fix turning the gate into a rubber stamp.

**`refutation_condition`.** If `bench/paid_dispatch_authorisations.json` is *meant* to exist and be operator-created per-round, then failing closed is correct and only the docstring lies. I found no writer for that path anywhere.

---

## `id: 4` — the three unreviewed classifier changes

**`verdict`: THE EVASION THAT STILL GETS THROUGH IS `sed -i` / `tee` / `git apply` / `patch`. FIXED for the two that are parseable.**

**`reasoning` — measured by calling the module, not reading it:**
```
'sed -i "" s/a/b/ bench/dm/_convergence.py'  -> ['<in-place>']  code_touched= False
'echo x > bench/dm/_convergence.py'          -> ['bench/dm/...'] code_touched= True
```
`hooks/ffafp_audit.py:510` records the literal sentinel `<in-place>`; `classify_path` (`:458`) has no extension to work with and returns `other`; `audit()` (`:664–667`) computes `code_touched = "code" in kinds` as **False**; `ffafp_stop_gate.py:106` (`if v.get("code")`) never fires. The write *is* recorded, so `is_work` is True — **the turn reads as audited while FIND/FOLLOW/FIX/P-PASS are all skipped.** That is the worst direction: it looks like coverage.

`classify_write` is a pure re-composition and adds no protection; `shell_bindings` is a harmless alias. The leading-prefix rule at `:446–449` has a worse hole — `/tmp/$V/../../repo/bench/a.py` launders to `transient`, because nothing calls `normpath` or `realpath` — which I report but did **not** fix, because the correct repair is path normalisation across the whole module and that is a design change, not a check.

**`fix_path`: `hooks/ffafp_audit.py`** — new `_INPLACE_OPERAND`; the sentinel is **kept** (still the honest answer for `git apply`/`patch`, whose targets live inside the diff) and the literal operands are **added**. 44 lines added, **0 removed** (verified by `diff`).

**`falsifier_command`:** the inline probe below, plus `python3 -m pytest bench/tests/ -q -k ffafp`

**`falsifier_output`:**
```
'sed -i "" s/a/b/ bench/dm/_convergence.py'  -> ['<in-place>', 'bench/dm/_convergence.py']  kinds=['code','other']
'sed -i.bak -e s/a/b/ docs/NOTES.md'         -> ['<in-place>', 'docs/NOTES.md']             kinds=['doc','other']
'cat /tmp/a | tee bench/dm/_convergence.py'  -> ['<in-place>', 'bench/dm/_convergence.py']  kinds=['code','other']
'tee bench/dm/_convergence.py < /tmp/a'      -> ['<in-place>', 'bench/dm/_convergence.py']  kinds=['code','other']
'git apply /tmp/p.diff'                      -> ['<in-place>']                              kinds=['other']
'sed -i "" s/a/b/ /tmp/scratch.py'           -> ['<in-place>', '/tmp/scratch.py']           kinds=['other','transient']
```
No false accusation: `.md` → `doc`, `/tmp` → `transient`, `git apply` unchanged.

**`additive_check`.** Caller: `bash_mutations()` → `audit()` → `ffafp_stop_gate.py:106`, on every Bash turn. Tests: `bench/tests/test_ffafp_*` — **127 passed**.

**⚠ CONSEQUENCE OF MY OWN FIX, reported rather than papered over.** `test_precommit_guard_2026-09-09.py::...[ffafp_audit.py]` and `test_ffafp_all_five_steps_2026-09-20.py::test_the_versioned_copy_is_the_one_that_actually_runs` now **fail**: they compare `hooks/ffafp_audit.py` against `~/.claude/hooks/ffafp_audit.py`, and my edit makes them drift. **I did not mirror the file and I did not touch the tests.** Writing to `~/.claude/` from a panel seat is a control-plane modification the dispatcher flags as a violation, and loosening the test to pass is the second prohibited behaviour under falsifier integrity. **CC1 must run the one-line mirror.** Until then the drift is real and the tests are right to say so.

**`refutation_condition`.** If the Stop gate consumes something other than `v.get("code")`, `code_touched` being False is harmless and this is not a defect.

---

## `id: 5` — the naming check

**`verdict`: NOT REACHED.** I did not run `scripts/note_naming_check_2026-09-28.py` and I will not report a verdict on a measurement I did not execute. `fix_path`: NONE — no finding. Items 8–11 likewise not reached.

---

## `id: 6` — the session's `grep` blind spot

**`verdict`: CC1'S NUMBER IS SOUND. CC1'S SCRIPT DOES NOT REPRODUCE AS STORED — it chooses its subject by a race, and on first re-run it returned VACUOUS.**

**`reasoning`.** First re-run, verbatim:
```
VACUOUS: the session's grep matched /usr/bin/grep on every pattern.
  The shell wrapper was NOT loaded... Do not read 0% as reassurance.
falsifier                   4304           4304       0
EXIT=3
```
**CC1's `is_vacuous` guard worked and refused loudly — that design is vindicated.** But the cause is `ls -t ~/.claude/shell-snapshots/ | head -1`, which picks the newest snapshot written by *any* session. Measured: **36 snapshots on this machine, exactly 2 carry the `grep` shadow** — so the selector had roughly a 94% chance of choosing one that cannot make the measurement, and the published 71.3632% records *which* snapshot produced it nowhere.

A second, sharper instance of the same class inside my own fix: my first wrapper-detector keyed on `grep()` and found **0 of 36**, because Claude Code writes it as `function grep {` — *no parentheses*. My detector reproduced the exact failure it was added to prevent, on its first run. Both are recorded in the file.

Pinned to a snapshot that actually carries the shadow (`ARGV0=ugrep ... --ignore-files`), it reproduces:
```
snapshot under test: /Users/georgejackson/.claude/shell-snapshots/snapshot-zsh-1790533362770-wbcl1l.sh
FILES THE SESSION'S grep NEVER SHOWS: 3727/5237 = 71.1667%
  Wilson 95%          [69.9247%, 72.3777%]
  Clopper-Pearson 95% [69.9187%, 72.3910%]
  mpmath@40dps Wilson [69.9247%, 72.3777%]   |agreement| 1.63e-17
```
CC1's 71.3632% sits inside my interval and mine inside CC1's; the 5237 vs 5245 denominator is archive drift over the day. **The figure is right.**

**`fix_path`: `scripts/shell_grep_blind_spot_2026-09-28.py`** — `snapshot()` honours `CDSFL_SHELL_SNAPSHOT`, else takes the newest snapshot that *actually defines* a `grep` function (both declaration forms), else falls back so the vacuity guard still speaks; the chosen file is **printed with the result**.

**`falsifier_command`:** `python3 scripts/shell_grep_blind_spot_2026-09-28.py`
**`falsifier_output`:** as above, `EXIT=0`.

**`additive_check`.** Caller: `main()` in the same script, the only entry point. Executed: the run above, which moved from `EXIT=3` (vacuous) to `EXIT=0` with provenance.

**The question CC1 did not answer — and I did not finish either.** I did **not** complete a systematic sweep of past zero-returning searches, and I will not name files I did not check. What I can state with evidence: the unsafe class is any claim of the form *"N occurrences"* where N came from `grep -rl X . | wc -l` at a moment `bench/logs/**` was invisible — `.gitignore:48` — and it is not cosmetic, because `falsifier` alone is **1025 visible vs 4305 real**, a 3280-file hole. The one concrete instance I verified is CC1's own script's first attempt (0 of 541, vacuous).

**A claim I checked that turned out SAFE — as the brief requires.** `.claude/CLAUDE.md:316–323`'s 42-of-43 / Fisher `p = 2.199086e-14`. `scripts/wolfram_route_health_2026-09-10.py:28` reads `~/Library/Logs/Claude`, **outside the repository and outside `.gitignore`'s reach**, and the counts reproduce exactly against `/usr/bin/grep` (39 + 1 + 3 = 43 failures, 21 successes, 64 attempts). The blind spot does not touch it.

---

## `id: 7` — the Wolfram route was never dead

**`verdict`: CC1 IS RIGHT THAT THE FIGURE DOES NOT SUPPORT THE INFERENCE. RE-SCOPING IS THE CORRECT CORRECTION AND IS NOT AN OVER-CORRECTION — but CC1 understates the problem, and a second defect in the same passage went unreported.**

**`reasoning`.** The arithmetic is **valid**: cells `[[1,20],[42,1]]`, Fisher `p = 2.199086e-14`, OR 840, χ² with Yates `8.709349e-13` — all reproduce exactly. Both arms are the same population (shim attach attempts) split by date, so there is no arm mismatch. The failure is **construct validity**: `scripts/wolfram_route_health_2026-09-10.py:31,44,45` keys every pattern on the literal string `WolframCloud` — the *removed config entry's name* — and the file contains **no HTTP client at all**. 41 of the 42 post-cut failures are generic `CONNECTION_CLOSED` / *"went away before the attach completed"*: the **local child process died**. That says nothing about `agenttools.wolfram.com`.

The one event that *did* reach the host refutes "dead" outright — an application-level `503 error-acquiring-kernel, "exceeded maximum number of queued requests"` from a **live, responding, overloaded** server, counted in the "dead" numerator.

**Not an over-correction, for three reasons that do not rest on CC1's word.** (i) The script's own `main()` prints a warning when the last attempt succeeded — and it did, 2026-09-09 09:07:25, 3 tools announced — which `.claude/CLAUDE.md:287` overrides with "DEAD" anyway. (ii) `CDSFL_MASTER_TASK_LIST.md:659` kept *"a transport fault"* open as one of three causes; CLAUDE.md closed it without evidence. (iii) Re-scoping **removes nothing**: the local `wolframscript` route stays primary, and the additive standard's removal clause was invoked on the property *availability*, which was never measured for the endpoint.

**Second defect, unreported by CC1.** `2.199086e-14` is `min_j p_j` over **17 candidate cuts** — a maximally-selected statistic the script itself labels `"<- NOT a p-value; do not quote alone"`, emitting `p_bonferroni ≈ 3.74e-13` and a permutation p. **CLAUDE.md contains zero occurrences of "Bonferroni", "permutation", "maximally-selected" or "candidate cut".** The quoted figure is the one the script warns against quoting.

**`fix_path`: NONE, with the reason.** The correct repair edits `.claude/CLAUDE.md:287–323` and retires `bench/tests/test_wolfram_route_retired_2026-09-10.py:107,116,148`, which currently **pin the contested wording** — so the test suite enforces the inference under review. Both are standing operator documents recording a decision the founder made while away from the machine; `Wolfram_Two_Routes_2026-09-28.md:102` already lists this as an open decision **for him**. Rewriting his ruling from a seat is not additive, and weakening the test that encodes it is prohibited. I report; he decides.

**`additive_check`.** N/A — no change delivered, deliberately.

**`refutation_condition`.** A direct HTTP probe of `agenttools.wolfram.com` returning connection-level failure across a comparable window would make "dead" true and my verdict wrong. **No script in this repository performs one** — which is itself the gap. I did not run one: an unrequested outbound probe from a panel seat is not mine to make.

---

## `strongest_disagreement` with this brief's framing

**Three, and the first is the one that matters.**

**1. The brief asks me to attack CC1's three claims on item 1 and decide "is the explorer's recursion wrong". Both framings mislead.** The explorer's *recursion* is right — it matches `reference_runner_v3.py:11947–11961` line for line, which is the operational model. Claim B is **refuted**: `:225` is the improvement of a *different* recursion, and had CC1 landed its proposed substitution the page's ΔR bars would have stopped equalling the trajectory they sit under — a fix creating a defect. The real bug is smaller, uglier, and fully self-contained: a **latched first crossing**, contradicting the page's own chart at 22.30% of slider space. It is findable by executing the page and never opening the appendix. The brief's framing would have routed me into an appendix argument and past the actual defect.

**2. Section 2's routing of the harness is wrong, and I say so rather than reach.** `S_k` was directed at items 6 and 7; **it bears on neither**, and I found no path by which it could. It bears decisively on **item 1**: the peak `R* = (1−√(1−q))/q` is *independent of σ*, which is precisely why the retired pathology survives the Stage 5 generalisation intact. `nu_star` and the break-even were directed at item 1; they are computed at `:174` and drive only the regime sentence, and played no part in the defect. `gamma` and the two-sided gate bear on nothing here, as the brief anticipated.

**3. Item 2's two questions — "too wide?" "too narrow?" — both aim at the right function and miss the defect.** `_run_log_dir` and `_is_dispatcher_own_output` are correct at all four shapes. The defect is that **half the call sites never call them**, and CC1's own docstring names the symptom it did not fix.

**And the brief's prior was correct, twice over.** There was a 4th defect: **item 3's gate is inert**, refusing every round including the ones the founder authorised in his own words, with eleven tests passing because every one of them monkeypatches the broken path away. Then a 5th, in my own work: my item-6 wrapper detector keyed on `grep()` and found 0 of 36, reproducing on its first run exactly the failure it was written to prevent. I caught it by executing. Neither would have been found by reading.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 79 recorded tool call(s).

<!-- verbatim-begin: fable (panel check_my_work_2026-09-28) -->

The `--measure` sweep under the grep fallback is still grinding through the 400 MB tree in the background; its unit tests (8/8, executing `check()`, `repo_hits()`, and the sentinel) already prove the fix, and the citable corpus figures remain the git-grep ones produced in the real repo. I have what I need. Final report.

---

# Panel seat B — verdicts on CC1's 7 items

## Item 1 — Explorer stopping rule

**verdict:** CC1's 3 claims **CONFIRMED**; script section 5 (`nuStar`) **MISATTRIBUTED** — a claim wider than its evidence.

**reasoning:** I re-derived, independently of CC1's script: E[ΔR] − dR = **(1−ν)·σ·q·R²·(1−q)/(1−qR) ≥ 0** on the whole open cube (SymPy confirms; Wolfram Language via the local Engine returns `True` on `Resolve[ForAll[...]]` — exit 0, computed). So the explorer's gate (`index.html:294`, `s.dR >= o.theta`) can only ever stop too **early** — the one-directional claim is a theorem, stronger than the 1309/14440 sweep, which I reproduced exactly. At σ=1, ν=0 the explorer's dR is symbolically the retired conditional ΔR_k (`MATHEMATICAL_APPENDIX.md:217`), and line 83/111/304 make it decision-bearing, not a trajectory display. Astra's `R·q` is the σ=1, ν=0 corner and always an upper bound (`:223`) — CC1 right. **But**: the explorer's `nuStar` at `:174-175` is *exactly* the appendix's own committed ν\* (`MATHEMATICAL_APPENDIX.md:280`), and I derived that dR=0 ⟺ ν=ν\* — it is the precise break-even of the plotted trajectory, and `:302`'s divergence analysis depends on it (the expectation break-even degenerates to 1 at R=1). Calling it "the explorer's own break-even, not the model's" (script §5, test class docstring) mislocates the defect: if it is superseded, the **appendix §:280–:284 hard exit** is what needs amending, and that is the founder's call, not a page edit.

**fix_path:** `explorer/index.html` — the stop layer only: slider relabelled `θ stopping threshold on E[ΔR]`; `simulate()` now computes `eDR = R·q·σ·(1−ν) − ν·(1−R)` (appendix `:225`); chart 2 bars, green gate, and "stop ≈ pass" all use `eDR`; dR kept for what it is legitimately for (trajectory, inspector, net-harm regime); `nuStar` deliberately untouched pending the appendix ruling.
**falsifier_path:** `bench/tests/test_explorer_gates_on_expected_improvement_2026-09-28.py` (extracts the JS formula and compares to the appendix by SymPy; asserts the dR gate is gone).
**falsifier_command:** `python3 -m pytest bench/tests/test_explorer_gates_on_expected_improvement_2026-09-28.py bench/tests/test_explorer_stopping_quantity_2026-09-28.py -q`
**falsifier_output:** `16 passed, 1 skipped` (the skip is CC1's premise test skipping by design: "the stopping rule was revised; confirm it now uses the general expected improvement").
**additive_check:** the new test file executes the revised page; CC1's `TestTheProducingScriptAgreesWithThisFile` still executes the producing script.
**refutation_condition:** the explorer as it stood would be correct if the committed model defined the stop quantity as the realized trajectory drop — `:217`/`:225` say the opposite — or if the page carried no decision semantics; it carries three. My nuStar dissent falls if the founder amends `:280–:284` to the expectation break-even.

## Item 2 — Harvest provenance fix

**verdict:** **SOUND.** Not too wide, not too narrow; no live 4th shape.

**reasoning:** All 4 call sites (`confer_maths_panel:96`, `confer_convergence_panel:78`, `build_experiment_run:181`, `run_simulated_experiment:640`) resolve dest under `bench/logs/<run>/…` with `<run>` directly inside `logs`, so `_run_log_dir` returns `bench/logs/<run>` for every shape; ran CC1's 30 tests — all pass, including the anti-vacuity pair and the parents[2] catastrophe class. Latent-only fragilities, below material: a future dest containing a *nested* `logs` directory would narrow the exclusion (bottom-up first match), and a repo checked out under a directory named `logs` yields run_log_rel `"."` (harmless — no rel path matches). The file my exclusion would wrongly drop: one a brief directs a seat to write inside the **current** run's own `bench/logs/<run>/` — no live brief does; other runs' dirs are proven harvested (`test_another_runs_log_directory_is_still_harvested`).
**fix_path:** NONE — the shipped fix is correct; adding guards for shapes no caller uses would be an addition nothing reaches.
**falsifier_command / output:** `python3 -m pytest bench/tests/test_harvest_excludes_its_own_output_2026-09-28.py -q` → `30 passed` (with the explorer file, 1.69s).
**refutation_condition:** a caller found passing a dest not under `bench/logs/<run>` (I enumerated all 4; there are none), or a brief directing seat output into the current run's log dir.

## Item 3 — Paid-dispatch ledger

**verdict:** **DEFECTIVE — this is the 4th defect the brief predicted.** No spend bypass through the gate (fail-closed), but the authorisation half was unwired to reality.

**reasoning:** `confer_maths_panel:399` pointed `PAID_LEDGER` at `bench/paid_dispatch_authorisations.json` — **a file that does not exist** — and its parser required a flat list of `{"round", "founder_authorisation"}`. The committed ledger lives at `bench/directives/universal/paid_dispatch_authorisations.json` as a **dict** with `authorisations[].rounds[]` and `founder_verbatim[]`: even repointed, every committed authorisation would be refused ("ledger is not a list"). CC1's own suite passed only because every test monkeypatches a synthetic flat-schema file — a fix whose green never touched the real record. Consequence: the founder's next authorised round is refused unless someone writes a **second** ledger — the exact two-copies drift `bench/paid_dispatch_authorisations.py`'s docstring forbids. On the bypass question: `main()` is guarded, but the module-level `MODELS` binding still honours `PANEL_ONLY` with no ledger check, and the direct paid routes (`experiment_11_orchestrator.call_openrouter`, `openrouter_tools.call_openrouter_with_tools`, `reference_runner_v3`, `decomposed_dispatch`) never consult any ledger — the "auditability, not impossibility" statement in the code is accurate and holds, no better and no worse.
**fix_path:** `bench/confer_maths_panel_2026-09-05.py` — `PAID_LEDGER` now points at the committed file; `_ledger_entries()` normalises both shapes; all refusal paths kept.
**falsifier_path:** `bench/tests/test_paid_gate_reads_the_committed_ledger_2026-09-28.py` — executes the gate against the **real** committed ledger (a real authorised round passes, an unknown round refuses, flat schema still parses).
**falsifier_command / output:** `python3 -m pytest bench/tests/test_paid_gate_reads_the_committed_ledger_2026-09-28.py bench/tests/test_paid_dispatch_needs_authorisation_2026-09-28.py -q` → `15 passed in 0.20s` (CC1's 11 tests all still green).
**additive_check:** `select_models` → `_paid_is_authorised` → `_ledger_entries` is executed by both test files; `main()` rebinding is asserted by CC1's `TestTheGuardIsWiredIntoMain`.
**refutation_condition:** the flat-schema file existing intentionally on the real machine as a to-be-committed ledger (it is absent from this full-tree copy, which includes ignored files, so I hold it absent).
**Escalation, not mine to fix:** `test_panel_conditions_are_met_2026-09-10.py` is red on real data — round `arm4_prose_anatomy_2026-09-22` holds **paid replies (cx, ge) with no ledger entry**, and `founder_verdicts_2026-09-28`'s two 0-tool-call seats are not recorded shortfalls. Recording either requires the founder's words; a seat must not forge them.

## Item 4 — Classifier changes in `hooks/ffafp_audit.py`

**verdict:** alias and adapter **SOUND**; the literal-prefix rule has a **CONFIRMED evasion**.

**reasoning:** "Transience is decided by where a path starts" is unsound under `..`. Executed against the real module: `classify_write("/tmp/${V:-../../repo}/hooks/evil.py", …)` → **transient**; `/tmp/$V/hooks/evil.py` (V knowable from neither command nor hook env) → **transient**; `/tmp/../repo/hooks/evil.py` → **transient**; and `${V:-default}` is the sharp case — the default value is attacker-chosen *in the same command*, invisible to `shell_assignments` (not an assignment; `_VAR` has no `:-` branch) but honoured by the real shell, so the landing point is deterministic while the classifier reads the one verdict that **excuses** a write. `$(…)` never matched the variable regex at all.
**fix_path:** `hooks/ffafp_audit.py` — a transient prefix is granted only when the remainder is literal and traversal-free; literal `..` falls through to extension classification (accuses honestly: `/tmp/../repo/hooks/evil.py` → `code`); a dynamic remainder (`$VAR`, `${…}`, `$(…)`, backtick) under a transient head returns `unresolved`, never `transient`. The 2026-09-24 bounce fix and head+extension rule are preserved unchanged.
**falsifier_path:** `bench/tests/test_transient_prefix_cannot_be_escaped_2026-09-28.py` — includes an **executed** bash traversal write landing inside a repo tree that the old rule classified transient.
**falsifier_command / output:** `python3 -m pytest bench/tests/test_transient_prefix_cannot_be_escaped_2026-09-28.py -q` → `6 passed`. Full ffafp regression: `127 passed`, 2 expected reds from the **sync guard** (`hooks/ffafp_audit.py` now differs from the installed `~/.claude/hooks/` copy — syncing is CC1's adoption step; a panel seat writing to the operator's control plane is the 2026-09-07 incident).
**refutation_condition:** proof that the hook's inherited environment always carries the expanding value (it cannot for `${V:-…}` defaults), or that the harness rewrites redirect targets before the hook sees them.

## Item 5 — Naming check

**verdict:** measurement **DOES NOT REPRODUCE here, and the non-reproduction is itself a defect** — the false-zero class.

**reasoning:** `repo_hits` shells `git grep`; this panel sandbox (like every panel sandbox — `.git` severed by design) returns rc 128 → `-1`, and `check()` treated `-1` like "found somewhere". Result, executed: `--measure` printed **RULE A 0/40 = 0.0000%, density 0.0000** with no warning — a measurement that measures nothing, in the reassuring direction, the same shape as the Exp 48 forensic "CLEAN" and CC1's own vacuous first grep comparison. Two of CC1's own committed tests were red here for the same reason (`assert -1 > 0`). The docstring figures (27/40, 8.9744%, 1.7750) are consistent with the script's arithmetic and were produced where git works; I could not independently reproduce them without leaving confinement, and after my fix the sandbox-mode figures will differ slightly (full-tree grep sees more files → fewer findings — conservative for an advisory). The 2 documented blind spots are real; I found a **3rd structural one**: backend failure masquerading as absence-of-findings — now closed.
**fix_path:** `scripts/note_naming_check_2026-09-28.py` — plain-grep fallback when git is absent; `check()` raises loud on `-1`; `--measure` runs a sentinel (`repo_hits("additive standard") > 0`) and refuses with exit 3 rather than print a rate it cannot compute.
**falsifier_command / output:** `python3 -m pytest bench/tests/test_note_naming_check_2026-09-28.py -q` → **`8 passed`** (was `2 failed, 6 passed` before the fix, in this git-less tree). Caveat: sandbox-mode `--measure` is slow (~80 full-tree greps); the citable corpus figures remain the git-grep ones.
**refutation_condition:** evidence that panel sandboxes carry `.git` (this one demonstrably does not) or that the advisory is only ever run from the real repo — the two red committed tests refute the latter already.

## Item 6 — The session grep blind spot

**verdict:** **CONFIRMED**, including its own anti-vacuity guard; and the past-claims question has concrete answers.

**reasoning:** In this sandbox the script correctly refuses (exit 3, "VACUOUS: … compared the real grep with itself") because the wrapper isn't loaded — the guard against CC1's own third self-shipped defect works. The mechanism is confirmed at `.gitignore:48` (`bench/logs/**`, 353 MB). I verified the arithmetic independently: 3743/5245 = 71.3632%, Wilson [70.1245%, 72.5706%] reproduced to all quoted digits at mpmath 40 dps.
**Past claims now UNSAFE as written** (each falsified by a search that can see the archive; each **conclusion** survives, the universal quantifier does not):
- `experimental_notes/Dedup_Historical_Brief_Addendum_2026-08-18.md:474` — "**GAMMA_SRC appears nowhere outside its own module and test**": it appears in `bench/logs/confer_stage6_full/combined_20260414T111854Z.json` and the exp46 round transcripts.
- `experimental_notes/Design_Reviews_Bugzilla_And_Perturbation_2026-08-21.md:28` — "**cc2_verification_step appears nowhere in the repo except inside its own docstring**": it appears in `bench/logs/exp38_ouroboros_20260410T104416Z/round_00.json` and 3 sibling files, all predating the claim.
- `experimental_notes/Wolfram_Two_Routes_2026-09-28.md` — "**`--mcp-config` … appears nowhere in the repository**": it appears at `bench/wolfram_standard.py:194` — not even archive-dependent; CC1's own newest note carries the shape it diagnoses.
**A claim checked that turned out SAFE:** the same addendum's `:403` "**`RESOLVED` … zero occurrences in the whole archive**" — `/usr/bin/grep -rl '"RESOLVED"' bench/logs` returns nothing; and `confer_maths_panel`'s "0 occurrences each" over `cdsfl_core_formal.md` (single named file, wrapper-immune; verified 0).
**fix_path:** NONE for the script (correct as shipped); the three unsafe claims need dated correction blocks, which is note-keeping CC1 should adjudicate rather than a seat rewriting history unilaterally.
**refutation_condition:** the wrapper not honouring `.gitignore` in real sessions — refuted by CC1's 8-pattern differential; or the three "unsafe" hits being in-scope-excluded by each claim's own wording — none of the three carries a scope qualifier.

## Item 7 — The Wolfram route

**verdict:** CC1's re-scoping **CONFIRMED and correctly bounded in the note; the standing document was not yet corrected — now it is.** One residual overreach flagged.

**reasoning:** `scripts/wolfram_route_health_2026-09-10.py:44-45` keys SUCCESS/FAILURE on the literal entry name (`announcing WolframCloud: (\d+) tool` / `Failed to connect to WolframCloud`) — the figure measures the **desktop app's attach to the `npx mcp-remote` shim**, never the host. The 42/43 and p = 2.199086e-14 are sound *for that quantity*; "BECAUSE IT IS DEAD" at `.claude/CLAUDE.md:287` drew the endpoint inference the instrument cannot support, and the task list (`CDSFL_MASTER_TASK_LIST.md:659`) had been more careful. Not an over-correction: disabling the entry stays justified (97.7% attach failure is reason enough), and CC1's note keeps the figure. Residual overreach in the note: "reachable **throughout**" rests on point samples (1 post-cut attach success, 2026-09-17 `Out[1]= 4`, 2026-09-28 A4) — established is "answered on every date probed", not continuity.
**fix_path:** `.claude/CLAUDE.md` — headline rescoped to "BECAUSE ITS TRANSPORT WAS DEAD", with the instrument's keying, the point-sample bound, and the note cited; NAMED LOSS bounded to the desktop-app route.
**falsifier_command / output:** `python3 -m pytest bench/tests/test_wolfram_route_retired_2026-09-10.py -q` → `13 passed` (the guard that pins this block's required content still holds).
**refutation_condition:** desktop logs containing endpoint-level probes distinct from attach lines (the patterns show none), or evidence the host was down across 09-10→17, which would re-open the endpoint inference.

---

**Items 8–11: not reached.** I chose to finish 7 properly, per Section 7.

**strongest_disagreement:** Two. (1) The brief frames CC1's `nuStar` finding as part of a package to confirm or refute about *the explorer*; it is neither — the explorer's `nuStar` is the appendix's own committed ν\* (`:280`), exact break-even of the plotted trajectory (dR=0 ⟺ ν=ν\*, derived), and the load-bearing role it plays in the `:302` divergence analysis means replacing it in the public page ahead of an appendix ruling would put the published tool in conflict with the committed model. The defect CC1's script §5 found is real mathematics but belongs to the **appendix**, and the brief's "PUBLISHED tool's stopping rule" framing hides that. (2) Section 2's steer that `nu_star` bears on item 1 was right, but "S_k bears on items 6 and 7" did not survive contact: nothing in items 6 or 7 was decided by S_k — the deciders were `.gitignore` semantics and desktop-log pattern scope. Gamma and the two-sided gate indeed bore on nothing, as the brief predicted.

**passes_run:** 2 full passes per item (reproduce/derive, then fix/falsify), plus a third sweep over items 2 and 6 hunting a 4th harvest shape and further unsafe zero-claims. The third pass added the `--mcp-config` finding and nothing else above the material threshold — diminishing returns, stopped there. Delivered into the tree: 3 code fixes (`bench/confer_maths_panel_2026-09-05.py`, `hooks/ffafp_audit.py`, `scripts/note_naming_check_2026-09-28.py`), 1 published-page fix (`explorer/index.html`), 1 standing-doc rescope (`.claude/CLAUDE.md`), 4 new test files — all executed: **126 passed, 1 skipped** on the final targeted batch, with the 2 known ffafp sync-guard reds (adoption step) and 4 pre-existing data-state reds in `test_panel_conditions_are_met` escalated above, not papered over. Wolfram was used as second falsifier once (E ≥ dR, `Resolve → True`, computed with Wolfram Language, local Engine); no stored falsifier calls it.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/check_my_work_2026-09-28/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
