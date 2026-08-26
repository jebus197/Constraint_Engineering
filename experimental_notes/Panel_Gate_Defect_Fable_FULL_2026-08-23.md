# FABLE ADVERSARIAL REVIEW — Exp 55 discrimination control
Reviewer: Fable (independent adversarial pass, isolated worktree at HEAD f9d4f5b).
Status: IN PROGRESS — Q1 and Q4 complete, Q2/Q3 being appended.

## Q1. Claims 1-4 — VERDICT: Claims 1 and 2 TRUE. Claim 3 TRUE-BUT-VACUOUS. Claim 4 FALSE.

### What the evidence shows (all verified by direct execution in the worktree)

Claim 1 (C0001/C0002 detached): TRUE. Both falsifier bodies
(report `registry.entries.C0001/C0002.falsifier_code`) contain no file access of
any kind. C0001 invents `f_s_test = 200` against the document's 400. Verified by
reading the code and by re-execution: both return CONFIRMED with or without a
repo cwd.

Claim 2 (C0009 reads the document): TRUE. Its code opens
`bench/cdsfl_registry/targets/control_two_distinct_defects.md` and regex-extracts
`f_max` from the text.

Claim 3 (6 readers / 2 detached / 2 absent; control fired on exactly the 2
detached): ARITHMETICALLY TRUE, but the inference CC1 hangs on it — "the control
is working as designed, the 6 genuine readers were left alone" — is FALSE. The 6
genuine readers were not "left alone" by the control; they were DESTROYED by the
main falsifier gate before the control could ever see them. All six carry
`falsifier_verdict: ERROR` in the report. I reproduced every archived verdict
exactly (see the table below). The control has still never adjudicated a single
target-reading falsifier on a live run. The "2 of 2, 100%" is selection bias
manufactured by a harness defect (Q4), not a control success.

### The reproduction table (run in this worktree, 2026-08-23)

| id    | archived verdict | reverify (as the gate runs it, no cwd) | reverify with cwd=repo root |
|-------|------------------|----------------------------------------|------------------------------|
| C0001 | CONFIRMED        | CONFIRMED                              | CONFIRMED                    |
| C0002 | CONFIRMED        | CONFIRMED                              | CONFIRMED                    |
| C0003 | ERROR            | ERROR                                  | CONFIRMED                    |
| C0004 | ERROR            | ERROR                                  | CONFIRMED                    |
| C0007 | ERROR            | ERROR                                  | CONFIRMED                    |
| C0008 | ERROR            | ERROR                                  | REFUTED (its own needle spans a line break) |
| C0009 | ERROR            | ERROR                                  | CONFIRMED                    |
| C0010 | ERROR            | ERROR                                  | CONFIRMED                    |

Every archived ERROR is a FileNotFoundError in the sandbox scratch cwd, not a
model failure. Five of the six "broken" falsifiers are correct instruments.

### Claim 4 (`retarget_substitutions == 0` is a sound mechanical test for
### detachment): FALSE, twice over, by execution.

`_retarget_falsifier` (bench/reference_runner_v2.py:2837-2852) counts and
rewrites ONLY the literal absolute repo-root string. A relative-path reader —
including C0009, CC1's own exemplar of a GENUINE reader — always yields
`retarget_substitutions == 0`. The field carries zero information about
detachment.

COUNTEREXAMPLE A (run, not hypothesised). C0009's own falsifier, given a
corrected copy, through `run_discrimination_control` at HEAD:

    outcome: DISCRIMINATES | retarget_substitutions: 0 | intercepted: True
    baseline: CONFIRMED | corrected: REFUTED

A falsifier that reads the target, extracts its numbers, discriminates
perfectly — and reads 0 on CC1's "mechanical detachment test". (Incidentally
this is the first DISCRIMINATES outcome ever produced by this control, and it
happened in a reviewer's scratch worktree.)

COUNTEREXAMPLE B (run, not hypothesised). A falsifier that OPENS the target and
extracts `f_max` FROM it, but falls back to the memorised value when the read
fails:

    import re, pathlib
    try:
        T = pathlib.Path("bench/cdsfl_registry/targets/control_two_distinct_defects.md").read_text()
        fmax = int(re.search(r"f_max = (\d+) Hz", T).group(1))
    except Exception:
        fmax = 180
    fs_ce = 2*fmax - 1
    if fs_ce > fmax and not (fs_ce > 2*fmax):
        print("FALSIFIED: bare f_s > f_max is insufficient for Nyquist")
        raise AssertionError("CT-01")

Result through `run_discrimination_control` at HEAD:

    outcome: INDETERMINATE_NOT_INTERCEPTED | retarget_substitutions: 0 | intercepted: False

This falsifier demonstrably opens and reads the target on the live path, yet
lands in exactly the record CC1 proposes to relabel `DETACHED_FALSIFIER`
("never opens the target"). The label would be factually false. What the
tripwire actually measures is OUTPUT INSENSITIVITY TO TARGET CONTENT — a
strictly weaker property than detachment.

DEFINITIVE ANSWER Q1: `retarget_substitutions == 0` is NOT a sound test for
detachment — it reads 0 for every relative-path reader (counterexample A) and
the tripwire's `intercepted == False` reads false for target-reading falsifiers
with content-insensitive output (counterexample B). Claim 4 is false. The
detachment detection in this run was not mechanical; it was a side effect of the
gate defect below.

## Q4. THE EIGHTH DEFECT — FOUND, REPRODUCED, AND IT CAUSED THE HALT.

**The main falsifier gate executes every falsifier in a throwaway scratch
directory in which the target document does not exist, while the harness's own
prompt orders models to open the target by repo-relative path.**

The sites:

* bench/reference_runner_v2.py:3819 — `verdict = reverify_falsifier(fcode,
  repo_root=repo_root)` — NO `cwd`. Default cwd is a throwaway temp dir
  (bench/falsifier_verify.py:1127, `tmp_cwd = cwd or _scratch`; comment at
  falsifier_verify.py:865-867: "Default: a throwaway scratch dir … `cwd`
  overrides it, and ONLY the discrimination control passes it").
* bench/reference_runner_v2.py:4547 — sweep falsifier re-attachment, same bare
  call. Any corrected falsifier resubmitted through the sweep that reads by
  relative path will ERROR and never clear.
* bench/routing.py:128 — `verdict = reverify_fn(code)`; the gate passes the bare
  `reverify_falsifier` reference, so the routing ladder — the ONLY absorber
  between the gate and HIL — destroys stronger writers' relative-path
  falsifiers the same way.
* The model-facing `execute_python` tool loop shares the same scratch cwd
  (falsifier_verify.py:885), so a model that iterates a CORRECT relative-path
  falsifier through the tool sees FileNotFoundError and is trained away from
  reading the document.

The contradiction is self-inflicted: the prompt at
bench/reference_runner_v2.py:4366-4377 names the target by its RELATIVE path and
instructs "runnable test that OPENS THE TARGET DOCUMENT BY PATH (the path named
above)". Six of eight falsifier-bearing findings obeyed; all six ERRORed. The
two that disobeyed (Gemini's detached pair) were the only CONFIRMED. **The gate
structurally selects FOR detached falsifiers and against instruction-following
ones — it rewards exactly the pathology the discrimination control exists to
catch.**

Measured consequences in the archived run (bench/logs/exp55_v3_control_20260823T144624Z/):

* 4 of the 6 irreducible-queue items that halted the run are these
  harness-manufactured ERRORs (severities 0.82, 0.88, 0.75, 0.85; the other 2
  are the genuinely UNTOOLABLE C0005/C0006). The halt was caused by the
  harness, not by model irreducibility.
* The commit message of f9d4f5b ("the alarm diagnosed itself correctly, and the
  relative-path fix it demanded is in") is wrong on the second clause: the fix
  commit threaded `cwd` into the discrimination control's five sites ONLY
  (verified against `git show f9d4f5b -- bench/reference_runner_v2.py`; the
  gate line 3819 is untouched). The discrimination control only runs on
  falsifiers that already reached CONFIRMED — which relative-path readers can
  never do. **A re-run at HEAD will halt at round 0 again, identically.** The
  fix repaired the back room and left the front door bricked up.
* This is defect eight in the established shape: a HARNESS failure (sandbox cwd)
  rendered as a MODEL failure (ERROR verdicts attributed to Codex, ChatGPT,
  DeepSeek and CC2 falsifiers, escalated as "un-demonstrated criticals").


## Q2. Is the DETACHED_FALSIFIER / narrowed INDETERMINATE split the right fix,
## and is it sufficient? — VERDICT: RIGHT IN SPIRIT, WRONG AS SPECIFIED, AND
## NOT SUFFICIENT.

### Why the split as specified is wrong

1. Its mechanical predicate does not exist. CC1's discriminator is
   "`retarget_substitutions == 0` plus zero file-access call sites". The first
   conjunct carries no information (Q1, counterexample A: C0009 reads the
   target and scores 0). The second conjunct is measured NOWHERE: the sandbox
   trace records only the ready marker and DENIALS
   (bench/falsifier_verify.py:659-669, `_read_trace` — lines beginning "D ").
   Allowed opens are never logged. There is no field, no counter, no record of
   file-access call sites anywhere in the harness. The proposed verdict would
   be minted from a measurement that has never been taken.

2. The label overstates what the tripwire measures. `intercepted == False`
   means "output insensitive to target content", NOT "never opens the target"
   (Q1, counterexample B: a falsifier that opens the target and extracts f_max
   from it lands NOT_INTERCEPTED). `DETACHED_FALSIFIER` as a name would assert
   a stronger fact than the instrument can know. If the split lands, the
   honest name is `TARGET_INSENSITIVE` (or the detail text must say "output
   does not depend on the target", never "never reads it").

3. "CONFIRMED must not stand" IS discrimination blocking, and blocking is
   default-off by founder ruling (`discrimination_control_blocks: bool = False`,
   bench/reference_runner_v2.py:641; note the comment at 1094 cites
   "RunnerConfig:594", a stale line reference). Auto-demoting on the new
   verdict while NO_DISCRIMINATION stays record-only creates a perverse
   gradient: a garbage falsifier that never touches the target is demoted,
   while the SAME garbage plus one cosmetic
   `open("...target.md").read()` line survives as CONFIRMED — because
   access-washing moves it from the detached bucket into the fires-on-both
   bucket (DISC_FAILED), which records and does not block. The 2026-08-12
   panel's access-vs-dependence objection (recorded at
   reference_runner_v2.py:3841-3850) applies verbatim. The split without
   blocking parity REWARDS strictly worse falsifiers. Either both outcomes
   block or neither does — that is one founder decision, not two wirings.

### Where a detached-class verdict must act, exactly

* Minting: `run_discrimination_control`, bench/reference_runner_v2.py:3419;
  the interception branch at 3553-3562 is where NOT_INTERCEPTED is currently
  minted and where any split must happen. To make it determinate, the observer
  must first be extended to log allowed opens of the overlay target during the
  baseline run (new plumbing in `_install_observer` / `_read_trace`,
  bench/falsifier_verify.py:637-669) — "the falsifier never opened the target"
  then becomes a measured fact instead of an inference from output identity.
* Applying: `_apply_discrimination_control`, bench/reference_runner_v2.py:3601;
  a new branch must sit BETWEEN the `DISC_FAILED` branch (3692-3707) and the
  `elif outcome in DISC_INDETERMINATE:` branch (3709), doing what DISC_FAILED
  does: `falsifier_verdict` -> a routable fault label, `verified = False`,
  `escalated = True`, `hil_escalated = True`, `mechanical_fault = True`, and
  status CONFIRMED -> UNCONFIRMED via `registry.resolve(cid, "UNCONFIRMED",
  round_idx)` — but the status demotion gated on
  `cfg.discrimination_control_blocks` exactly as DISC_FAILED is gated at the
  call site (`apply_falsifier_verdicts`, 3835-3846).
* Set membership: the new label (or NON_DISCRIMINATING reused) goes into
  `ROUTABLE_INSTRUMENT_FAULTS` ONLY (reference_runner_v2.py:1099) so the
  routing ladder at 4223 sends a stronger writer. It must NEVER enter
  `EQUIPMENT_FAILURE_VERDICTS` (1086): `resolve()`'s T04 guard at 1517-1533
  demotes every terminal status for that set unconditionally, which would turn
  blocking on by the back door — the exact prior merge failure the three tests
  pinned.

### Why it is not sufficient even done right

The split relabels 2 records. It does nothing about the defect that produced
the run's actual failure: the main gate destroyed all six genuine readers
before the control saw them (Q4). Fix the split and re-run at HEAD, and the
run halts at round 0 again with the same queue. Sufficiency requires the gate
cwd fix first; the split is second-order.

### A contradiction found in passing (existing code, not the proposal)

In non-blocking mode (the default), `_apply_discrimination_control`'s
DISC_FAILED branch stamps `falsifier_verdict = "NON_DISCRIMINATING"`,
`verified = False` and resolves CONFIRMED -> UNCONFIRMED (3694-3702), and the
gate then immediately re-resolves CONFIRMED and sets `verified = True`
(3846-3847). Net state at HEAD: `status: CONFIRMED, verified: True,
falsifier_verdict: NON_DISCRIMINATING, mechanical_fault: True` — a finding
simultaneously verified and mechanically faulted, plus an
UNCONFIRMED->CONFIRMED status flap written to the status log every round the
cache re-applies. The helper's docstring ("returns to the same state as any
un-demonstrated critical") describes blocking behaviour that the default
configuration contradicts. Suggested: in non-blocking mode the helper must not
touch status or verified at all (record + escalate only); the demotion belongs
exclusively behind `discrimination_control_blocks`.

## Q3. "The remaining gap is FINITE AND COUNTED — 7 uncommissioned of 34."
## — VERDICT: FALSIFIED, on the repository's own data. The remainder is
## NEITHER counted at 7 NOR demonstrably finite. The work is NOT bunk — but
## the instrument's defects all bias the same direction, and that must be
## said plainly.

### The count is wrong by the inventory's own file

`experimental_notes/data/instrument_inventory.json`: n=34,
`commissioning_candidates: 27`, and `measured: true` on exactly FIVE rows
(I14, I16, I26, I33, I34). The "7" counts instruments lacking even a
CANDIDATE test (I02, I04, I07, I08, I14, I26, I33 —
`Instrument_Inventory_2026-08-22.md:65`). "Has a candidate" means a filename a
heuristic matched (`heuristic_said: true`), not a commissioning: 22 of the 27
candidates have `measured: false`. By the project's OWN definition of
commissioned (known-good AND known-bad input, verified answers differ —
`Panel_Diversity_And_Inactive_Instruments_2026-08-23.md:186`), the
uncommissioned count is 29 of 34, not 7 of 34. CC1's number undercounts its
own records four-fold. And of the 5 marked measured: I26 is shelved, I33 is
not wired, I14 is "measured NOT commissioned" per the panel note — leaving
TWO instruments (I16, I34) with commissioning-grade evidence.

### The enumeration does not bound the defect surface

All eight defects of 21-23 August live in the SEAMS between enumerated
instruments, not inside any row: gate<->sandbox cwd (defect 8), control<->
overlay retargeting (defect 7), parser<->fence grammar (defect 4, the
`parse_test` truncation), baseline<->worktree assumption (the SUITE_WENT_RED
false rejection recorded in build_acceptance.py:131-146). An inventory of 34
nodes has ~n^2 seams and enumerates none of them. The inventory also has no
row for the irreducible-queue alarm, the acceptance gate, the cost ledger,
`_retarget_falsifier`, the tripwire, or the corrected-copy supplies (verified
by keyword sweep over rows). The list is a useful map of emitters; it is not a
census of failure sites, and counting it as one is how "finite and counted"
was minted.

### Commissioning is not monotone — measured instruments un-measure

I14 (the falsifier gate) was marked `measured` on 22 August. Defect 8 sits
inside it on 23 August (reference_runner_v2.py:3819). The f9d4f5b fix shipped
with `bench/tests/test_three_gaps_2026-08-23.py`, which pins co-discovery, the
cost ledger, and temp-dir teardown — NOT the cwd behaviour it was named for;
no test anywhere pins "a relative-path falsifier reaches CONFIRMED through the
gate" (verified: no cwd assertion in bench/tests/). Fixing defect 7 created
the visibility of defect 8 and the fix for defect 8 (Q2) requires a NEW
instrument (observer open-logging) that is on no list. That is the
each-fix-opens-more dynamic, demonstrated inside this review, not asserted.

### What the founder should actually be told

1. NOT BUNK, with evidence: the truth channel fails conservative. In this run
   the alarm halted loudly and correctly; the control refused to conclude
   rather than minting a verdict; null-perturbation (I34) measured 360
   firings, 0 moved by irrelevant edits; the acceptance gate is genuinely
   two-sided. And my E2/E3 runs show the pipeline is ONE SMALL FIX from
   working: with a correct gate cwd, this exact archived round yields 7
   CONFIRMED (5 of them genuine readers), 1 REFUTED, and the control's first
   genuine DISCRIMINATES.
2. THE SYSTEMATIC BIAS, plainly: all eight harness defects debited the
   models' measured competence — the quantity this project exists to measure.
   An instrument whose defects all bias one direction produces a
   systematically wrong primary reading even when each defect is individually
   found later. Until a run completes with zero new harness defects, no
   model-competence number from this bench should be quoted outside the
   project.
3. THE MONEY, plainly: at HEAD, every prose-target run is guaranteed to halt
   at round 0 after burning a full five-model round (~19 min, 1152 s
   measured), because the gate cannot confirm any falsifier that follows the
   harness's own prompt instruction to open the document by path. Do not
   launch another paid run before the gate cwd fix lands.
4. The honest convergence metric does not exist yet: nothing tracks
   defects-found-per-run over time. Until that curve exists and bends down,
   "demonstrably closer to iron-clad" is not a claim the record can support;
   "failing loudly instead of silently, with one dominant defect class
   (harness-fault-rendered-as-model-fault) still active" is.

## Q4 ADDENDUM — the ninth defect, and minor findings

### Ninth defect (found in the secondary audit targets, same house shape)

`suite_baseline` (bench/build_acceptance.py:128-166): if the baseline
worktree add fails (line 155) or the baseline suite run raises — including
`subprocess.TimeoutExpired` from `_run` — (lines 159-160), the parent
baseline is cached as `frozenset()`: "nothing fails at the parent". Step 3
(build_acceptance.py:279-290) then counts every PRE-EXISTING failure as a new
failure and returns REJECTED_SUITE_WENT_RED. A harness timeout becomes a
verdict that the MODEL's patch broke the suite — the exact failure class the
function's own docstring narrates having fixed on 2026-08-22 — and the
poisoned baseline is CACHED, so every subsequent candidate at that parent
inherits the false rejection. Failure scenario: one slow CI moment during the
baseline run of a 40-task build experiment -> every accepted-able patch at
that parent rejected SUITE_WENT_RED -> acceptance rate collapses toward the
pre-registered "models cannot do the task" tell. Suggested fix: a failed
baseline measurement must return/raise ERR_HARNESS (indeterminate) and must
not be cached; `frozenset()` may only be stored when a suite run actually
completed.

### Minor findings (each one line, file:line)

* bench/build_acceptance.py:255-263 asymmetry: pytest exit 3/4/5 at the
  parent -> ERR_HARNESS, but the same exits WITH the patch fall into
  `rc_after != 0` -> REJECTED_TEST_STILL_FAILS_WITH_PATCH — a pytest internal
  error rendered as a model failure.
* bench/build_acceptance.py:180 default `parent="HEAD"` + `_BASELINE` cache
  keyed on the string "HEAD" (149-153): any caller that does not resolve HEAD
  to a SHA (the current driver does, build_experiment_run.py:194) gets stale
  baselines the moment HEAD moves.
* bench/cost_ledger.py:104 `wall_clock_s` sums per-dispatch elapsed times;
  under parallel dispatch this is cumulative dispatch-seconds, not wall
  clock — mislabelled field.
* bench/reference_runner_v2.py:1094 comment cites "RunnerConfig:594"; the
  flag is at 641 — stale cross-reference.
* Exp 55 report `context_files: []` — with the suggested materialise-the-
  target gate fix, falsifiers reading declared context files by relative path
  would still ERROR; the fix must materialise target + declared context
  files, and that boundary should be stated in the gate.

## SUGGESTED FIXES (suggested to the human; nothing applied)

FIX 1 [BLOCKING, before any paid run] — the gate cwd. Do NOT pass the real
repo root as cwd (a falsifier's relative WRITE would land in the live tree —
the residual risk already flagged at falsifier_verify.py:869-880). Simplest
sufficient: in `reverify_falsifier`/`execute_python` callers at
reference_runner_v2.py:3819 and 4547 and in the reverify closure handed to
`route()` (routing.py:128), materialise a scratch cwd containing a COPY of the
target (and declared context files) at its repo-relative path, and run with
`cwd=<that scratch>`. Reads by relative path work; writes land in the
throwaway; no overlay symlink risk. Add the missing regression test: "a
falsifier that opens the target by relative path reaches CONFIRMED through
`apply_falsifier_verdicts`" — the test defect 7's fix should have shipped
with.

FIX 2 — the verdict split (Q2), done as specified there: observer open-logging
first, honest name (TARGET_INSENSITIVE), ROUTABLE_INSTRUMENT_FAULTS only,
status demotion behind `discrimination_control_blocks`, and one founder ruling
covering DISC_FAILED and the new outcome together (blocking parity).

FIX 3 — `suite_baseline` indeterminate-on-error, uncached (Q4 addendum).

FIX 4 — non-blocking DISC_FAILED must not touch status/verified in the helper
(the contradiction in Q2); the helper's mutations belong behind the same flag
as the gate's.

FIX 5 — inventory hygiene: add a `commissioned` field distinct from
`heuristic_said`; the founder-facing number is 29/34 open, not 7/34.

## ONE-LINE VERDICTS

* Q1: Claim 4 FALSE — `retarget_substitutions == 0` reads 0 for genuine
  readers (executed counterexample) and the tripwire cannot distinguish
  "never reads" from "reads but ignores" (executed counterexample).
* Q2: split right in spirit, wrong as specified (unmeasured predicate,
  overclaiming name, back-door blocking asymmetry), and insufficient without
  the gate fix.
* Q3: "7 of 34" FALSIFIED — 29/34 unmeasured by the repo's own file; the
  enumeration misses the seams where all 8 defects lived; commissioning is
  non-monotone. Not bunk — but all 8 defects bias against the models, and no
  paid run should launch before Fix 1.
* Q4: eighth defect FOUND at reference_runner_v2.py:3819 (+4547,
  routing.py:128): the gate runs falsifiers where the target does not exist
  while the prompt orders them to open it by path; it caused the halt, it
  selects FOR detached falsifiers, and the f9d4f5b fix did not touch it. A
  ninth found in build_acceptance.py:155/160.

Review completed 2026-08-23T17:0x+01:00 in the isolated worktree; every
executed claim above was produced by running the repository's own code at HEAD
f9d4f5b.
