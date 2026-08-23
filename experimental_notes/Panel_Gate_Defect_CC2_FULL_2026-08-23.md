# CC2 ADVERSARIAL REVIEW — Exp 55 discrimination control

Reviewer: CC2 (Claude Opus 5, 1M context), read-only disposable worktree
`/private/tmp/.../scratchpad/cc2_review_wt` at HEAD `66de417`.
Date: 2026-08-23T17:02:35+01:00.
Convergence compelled per founder override. Every claim below is backed by a
tool run reproduced inline. Nothing in the live tree was touched.

---

## HEADLINE

**The eighth defect exists, it is in the falsifier gate itself, and it inverts
the gate.** In Exp 55 round 0 the gate CONFIRMED the two falsifiers that never
open the target and returned ERROR on all six that do. The cause is that
`apply_falsifier_verdicts` runs every falsifier with the sandbox's throwaway
working directory, so a falsifier that reads its target by a relative path —
the form every model used, and the form the prompt's own location strings
invite — dies on `FileNotFoundError` before it can demonstrate anything.

CC1's relative-path fix was applied to the discrimination control **only**. The
main gate (`bench/reference_runner_v2.py:3819`), the routing ladder
(`bench/routing.py:128`) and the sweep re-attachment
(`bench/reference_runner_v2.py:4547`) all still call `reverify_falsifier`
without `cwd`. The fix landed one layer below the layer that was broken.

Consequence for the review CC1 asked for: **CLAIM 3's "2 of 2, 100%" is a
selection artefact of this defect, and CLAIM 4 is false.** Measured below, with
`cwd` supplied, five of the six ERRORed falsifiers CONFIRM and the
discrimination control returns **DISCRIMINATES** on them — the verdict the
control has waited its whole life to produce. It was not blind. It was starved.

---

## Q1 — Are CLAIMS 1–4 correct?

### CLAIMS 1 and 2: CORRECT.

C0001's falsifier is detached. It hardcodes `f_s_test = 200` where the document
says 400 and never opens the file
(`registry.entries.C0001.falsifier_code`, and the same shape at C0002). C0009
genuinely reads the target, regex-extracts `f_max` from the file's own bytes and
builds its counterexample from them (`registry.entries.C0009.falsifier_code`).
Both as described in the brief.

### CLAIM 3: THE COUNT IS RIGHT AND THE INFERENCE IS WRONG.

The report does contain exactly two discrimination records and both are on
detached falsifiers. But the reason the other six were "left alone" is not that
the control declined them. It is that the gate never gave the control anything
to work with — the control is only invoked on a `CONFIRMED` verdict
(`bench/reference_runner_v2.py:3826-3838`), and all six file-reading falsifiers
came back `ERROR`:

```
C0001 status=CONFIRMED    fv=CONFIRMED    reads target: NO   (detached)
C0002 status=CONFIRMED    fv=CONFIRMED    reads target: NO   (detached)
C0003 status=UNCONFIRMED  fv=ERROR        reads target: YES
C0004 status=UNCONFIRMED  fv=ERROR        reads target: YES
C0005 status=UNCONFIRMED  fv=UNTOOLABLE   (no falsifier)
C0006 status=UNCONFIRMED  fv=UNTOOLABLE   (no falsifier)
C0007 status=UNCONFIRMED  fv=ERROR        reads target: YES
C0008 status=UNCONFIRMED  fv=ERROR        reads target: YES
C0009 status=UNCONFIRMED  fv=ERROR        reads target: YES
C0010 status=UNCONFIRMED  fv=ERROR        reads target: YES
```
(read from `registry.entries.*` in `exp55_v3_control_report.json`)

Re-running the archived sources through the real
`bench.falsifier_verify.reverify_falsifier`, first exactly as the gate calls it
and then with `cwd` set to the repo root:

```
              archived   gate's call (no cwd)   with cwd=repo_root
C0001         CONFIRMED  CONFIRMED              — (detached, unaffected)
C0002         CONFIRMED  CONFIRMED              — (detached, unaffected)
C0003         ERROR      ERROR                  CONFIRMED
C0004         ERROR      ERROR                  CONFIRMED
C0007         ERROR      ERROR                  CONFIRMED
C0008         ERROR      ERROR                  REFUTED
C0009         ERROR      ERROR                  CONFIRMED
C0010         ERROR      ERROR                  CONFIRMED
```

The raw failure, captured from the sandbox:

```
[exit 1]
Traceback (most recent call last):
  File "/var/folders/.../cdsfl_falsifier_xibxh_lc/tmpaa7a_beq.py", line 3, in <module>
    text = Path("bench/cdsfl_registry/targets/control_two_distinct_defects.md").read_text()
  ...
FileNotFoundError
```

So the sample the control saw was size 2, and it was selected by the very bug
that produced it. "2 of 2, 100%" is not a measurement of the control's
discrimination power. **In Exp 55 the control's discrimination power against a
genuine reader was never measured at all.**

### CLAIM 4: FALSE. `retarget_substitutions == 0` is NOT a sound test for detachment.

`_retarget_falsifier` (`bench/reference_runner_v2.py:2837-2853`) counts literal
occurrences of the **absolute repo-root string** in the falsifier source and
returns that count. It is 0 for every falsifier that does not hardcode an
absolute path — which is nearly all of them, detached or not.

The counterexample the brief asks for is **already in the run's own data**. I
ran the real `run_discrimination_control` against the real target with each
falsifier as input:

```
C0001_detached(real)             nsub=0  INDETERMINATE_NOT_INTERCEPTED  intercepted=False
C0009_reader(real)               nsub=0  DISCRIMINATES                  intercepted=True  base=CONFIRMED corr=REFUTED
C0007_reader(real)               nsub=0  DISCRIMINATES                  intercepted=True  base=CONFIRMED corr=REFUTED
```

C0007 and C0009 read the target, discriminate perfectly, and score
`retarget_substitutions = 0`. CLAIM 4 is refuted by two findings inside the very
report it is a claim about.

Four further classes from the brief's list, all verified to read the target,
all scoring 0:

```
linecache (no open/read_text)        nsub=0  DISCRIMINATES  intercepted=True  base=CONFIRMED corr=REFUTED
runtime-built path (os.sep.join)     nsub=0  DISCRIMINATES  intercepted=True  base=CONFIRMED corr=REFUTED
glob-discovered path                 nsub=0  DISCRIMINATES  intercepted=True  base=CONFIRMED corr=REFUTED
env-var-built path                   nsub=0  DISCRIMINATES  intercepted=True  base=CONFIRMED corr=REFUTED
```

Code for the strongest of them — no `open`, no `read_text`, no `Path`, nothing a
call-site scan is likely to enumerate:

```python
import linecache
t = "".join(linecache.getlines("bench/cdsfl_registry/targets/control_two_distinct_defects.md"))
import re
if re.search(r"exceeds `f_max", t):
    print("FALSIFIED")
```
→ `retarget_substitutions = 0`, `intercepted = True`, outcome `DISCRIMINATES`.

`falsifier_verify.py:391-393` already states the principle CLAIM 4 violates: *"a
path is a string a program computes, so no amount of reading the source can
decide where the program will actually read."* CLAIM 4 proposes to decide
exactly that by reading the source.

### AND A SECOND, INDEPENDENT UNSOUNDNESS — in the probe CLAIM 4 should have cited.

The mechanism that actually produced `INDETERMINATE_NOT_INTERCEPTED` is not
`retarget_substitutions`; it is the tripwire probe at
`bench/reference_runner_v2.py:3537-3560`, which compares output against the real
target with output against `DISC_TRIPWIRE_BODY`
(`bench/reference_runner_v2.py:2756-2760`). That probe has its own
false-negative class, and it is a natural one, not an exotic one.

A prose falsifier can be written two ways: assert the *wrong* condition is
present, or assert the *right* condition is absent. The second form fires
identically on the tripwire body, because the tripwire body also lacks the right
condition. Verified:

```python
from pathlib import Path
t = Path("bench/cdsfl_registry/targets/control_two_distinct_defects.md").read_text()
if "2 * f_max" not in t:
    print("FALSIFIED")
```
```
run_discrimination_control  -> INDETERMINATE_NOT_INTERCEPTED   intercepted=False   nsub=0
reverify against REAL target      -> CONFIRMED
reverify against CORRECTED copy   -> REFUTED
```

This falsifier reads the target, depends on the target, and **discriminates
perfectly** — and the interception probe calls it not-intercepted. Any verdict
that treats `NOT_INTERCEPTED` as determinate evidence of detachment will demote
it.

**Q1 verdict: CLAIMS 1, 2 correct. CLAIM 3's count correct, its inference
invalid. CLAIM 4 false — the control's stated detection is unsound, and the
detection it actually uses is unsound in a different way.**

---

## Q2 — Is the CLAIM 5 split the right fix, and is it sufficient?

**It is the right idea, it is not sufficient, and as specified it is unsafe.**

### Why it is unsafe as specified

CLAIM 5 derives `DETACHED_FALSIFIER` from `retarget_substitutions == 0` plus
"zero file-access call sites". Q1 shows the first conjunct carries no
information (0 for essentially every falsifier), so the test reduces to a static
AST scan for file-access call sites. That scan has no closed enumeration —
`linecache.getlines`, `fileinput.input`, `pkgutil.get_data`, `codecs.open`,
`mmap`, `pandas.read_csv`, `subprocess.run(["cat", ...])`, `getattr(builtins,
"open")` — and the module's own design note says source inspection cannot decide
where a program reads. A determinate verdict built on an indeterminate test that
then **demotes a CONFIRMED** is a new way to render a sound instrument as a
model failure. That is the class the project is trying to leave.

### The sound test already exists in the codebase and is switched off

`falsifier_verify.py:403-404` states the observer's second job verbatim:
*"Record whether the falsifier ever opened its target, which is what tells a
demonstration apart from an instrument that broke before it started."*

**It does not do this.** The audit hook only emits on refusal —
`_emit("D open\t" + path)` inside the `_denied` branch
(`bench/falsifier_verify.py:497`) — and `_read_trace`
(`bench/falsifier_verify.py:650-669`) parses only the ready marker and lines
beginning `D `. There is no record of an **allowed** open anywhere. The
documented capability is unimplemented.

That is the missing measurement, and it is four lines of work. Emit `A open\t
<resolved path>` for allowed opens, have `_read_trace` collect them into
`obs["opened"]`, and detachment becomes a **dynamic, ground-truth** fact: did
the resolved path of any open equal the overlay's target leaf? That answer is
correct for relative paths, runtime-built paths, globs, env vars, `linecache`,
`pkgutil`, and subprocess arguments alike, because it decides at the call on the
resolved path — exactly the design the module already argues for.

Recommended verdict set, with the interception probe kept as corroboration, not
as the decider:

| observer says target opened | tripwire probe | verdict |
|---|---|---|
| no  | not intercepted | `DETACHED_FALSIFIER` — determinate |
| yes | not intercepted | `INDETERMINATE_NOT_INTERCEPTED` — narrowed, genuinely ours (the negative-membership case above) |
| yes | intercepted | proceed to step 4 as today |

### What `DETACHED_FALSIFIER` must DO — exact sites

The two sets must stay separate, and this verdict belongs in **neither** of them
as currently written.

* Demotion is decided in `FindingRegistry.resolve`, the equipment-failure guard
  at **`bench/reference_runner_v2.py:1516-1529`**, gated on
  `EQUIPMENT_FAILURE_VERDICTS` (**line 1086**: `{"ERROR", "UNTOOLABLE"}`).
* Routing is decided at **`bench/reference_runner_v2.py:4223`**, gated on
  `ROUTABLE_INSTRUMENT_FAULTS` (**line 1099**), which is the demotion set plus
  `NON_DISCRIMINATING`.
* The stamp is applied in `_apply_discrimination_control`, the `DISC_FAILED`
  branch at **`bench/reference_runner_v2.py:3692-3706`** and the
  `DISC_INDETERMINATE` branch at **3709-3722**.

`DETACHED_FALSIFIER` is the same *kind* of fact as `NON_DISCRIMINATING`: the
instrument produced a reading, and the reading does not depend on the target. A
detached falsifier is in fact the limiting case of non-discrimination — it
cannot possibly go quiet on a corrected copy, because it never reads one.

So the answer to "demote CONFIRMED to what": **do not demote it at the gate.**
Add `DETACHED_FALSIFIER` to `ROUTABLE_INSTRUMENT_FAULTS` **only**
(line 1099), leave `EQUIPMENT_FAILURE_VERDICTS` untouched at line 1086, and
stamp it in `_apply_discrimination_control` exactly as `NON_DISCRIMINATING` is
stamped at line 3695 — including `mechanical_fault = True`, `hil_escalated =
True`, and the existing blocking branch at line 3835 gated on
`cfg.discrimination_control_blocks` (declared at
`bench/reference_runner_v2.py:641`, default `False`).

Putting it in the demotion set would turn discrimination blocking on by the back
door for a *new* verdict — the identical regression the comment at lines
1093-1098 records and three tests caught. The founder's default-off ruling on
blocking covers this verdict too; the point of the split is to make the record
say a true thing, not to change what the gate does without a ruling.

Escalation destination: the human, via the same `hil_escalated` / `hil_reason`
channel, and via the routing ladder for one attempt at a stronger writer
(`error_routed` guard, line 4224). That ladder is the right destination:
a detached falsifier is precisely the case where re-asking for a falsifier that
reads the document is the fix.

### Is the split sufficient? No — three things must ship with it

1. **The main gate must supply `cwd`.** Without it the control never sees a
   genuine reader, so no refinement of the control's vocabulary changes any
   outcome. See Q4 finding #1 — this is the load-bearing repair, and the verdict
   split is cosmetic until it lands.
2. **Do not pass `cwd=repo_root` at the main gate.** `falsifier_verify.py:18-23`
   states the throwaway cwd exists so a relative-path *write* cannot touch the
   tree. The correct move is to reuse the apparatus that already exists:
   run the gate inside `_build_discrimination_overlay(root, target_rel,
   real_text)` (`bench/reference_runner_v2.py:2833`), so relative reads resolve
   and relative writes land in a throwaway. CC1's own comment at
   `falsifier_verify.py:877-884` already flags the residual — the overlay's
   directory entries are symlinks, so a relative write follows into the real
   tree. That residual becomes load-bearing the moment the overlay is used on
   every falsifier rather than on two. The clean close is to deny write-mode
   `open` outside the scratch dir in the audit hook; the hook already receives
   the mode argument, and no honest falsifier writes anything.
3. **Publish the counted denominator.** The discrimination tally is already
   logged (`bench/reference_runner_v2.py:3894-3901`); once detachment is
   dynamic, the number that matters — *how many CONFIRMED findings rest on a
   falsifier that never opened the document* — becomes computable across the
   2,030-finding archive. That number is the answer to the founding claim, and
   nothing weaker substitutes for it.

**Q2 verdict: split yes, `retarget_substitutions` no, static call-site scan no,
observer-recorded opens yes, `ROUTABLE_INSTRUMENT_FAULTS` only, and it does
nothing until Q4 #1 is fixed.**

---

## Q3 — Is the remaining gap finite and burnable, or is it open-ended?

**The gap is finite. CC1's count of it is wrong by roughly a factor of four, in
the reassuring direction. The work is not bunk.**

Taking the three parts separately, because the founder is owed the distinction.

### (a) The "7 of 34" figure is a misreading of CC1's own file

`experimental_notes/data/instrument_inventory.json` reports `n = 34`,
`commissioning_candidates = 27`. Aggregating all 34 rows:

```
commissioning_candidate:  True 27, False 7
measured:                 True  5, False 29
panel_verdict:            '' × 34   (nothing adjudicated)
```

And the source note says it in words —
`experimental_notes/Instrument_Inventory_2026-08-22.md:65`: *"27 of 34
instruments have a commissioning candidate. 7 do not."*

The 7 is the count of instruments for which **no test even names them with both
a positive and a negative assertion**. It is the worst-off tail, not the
remaining work. The remaining work by the file's own accounting is **29
unmeasured instruments**, of which 27 carry an unverified heuristic guess.

### (b) The heuristic that produces the 27 is wrong 3 times out of 5, always in the confident direction

`python3 scripts/instrument_inventory.py` prints its own calibration:

```
  27 of 34 have a commissioning candidate; 7 do not.

  CALIBRATION OF THE HEURISTIC AGAINST DIRECT MEASUREMENT:
    5 rows have been measured directly; the heuristic
    disagreed with the measurement on 3 of them (I14, I26, I33).
    3 disagreement(s) in the CONFIDENT direction (I14, I26, I33): the heuristic said commissioned
    where measurement says it is not.
```

Every disagreement is the heuristic over-claiming. I14 is **the falsifier gate
itself** — scored commissioned by the heuristic, measured NOT commissioned. If
that 3-of-5 rate holds, most of the 27 "yes" rows are not commissioned either.
The tool says this about itself, in its own output, unprompted. That is a point
in the project's favour, not against it — but it is not compatible with quoting
7 as the residual.

### (c) The enumeration unit is too coarse, and a MEASURED row still carried a live defect

I16 (`run_discrimination_control`) is one of the five rows marked
`measured: true`, on the strength of a 372-falsifier archive run. Q1 above found
a false-negative class inside it — the negative-membership falsifier that is
stamped `NOT_INTERCEPTED` while discriminating perfectly. One inventory row
covers at least five independently falsifiable sub-instruments: the baseline
check, the determinism probe, the tripwire probe, `_retarget_falsifier`, and
`_derive_corrected_copy_from_fix`. None of the five appears in the 34.

So the burndown's denominator is an undercount at the granularity at which
defects actually occur, and "measured" is per-row, not per-mechanism.

### The definitive answer to the founder's question

**Yes, demonstrably closer to iron-clad, and no, not iron-clad — and the gap is
burnable rather than open-ended.** The reasoning, stated so it can be attacked:

The instruments are a *closed hand-written list* in source
(`scripts/instrument_inventory.py:42-79`), not a discovered set that grows when
you look at it. Each fix so far has closed the defect it named and has not
spawned new instruments — it has revealed *sub-instruments that already existed
and were never enumerated*. That is a resolution problem, not a divergence
problem: refining the unit of enumeration terminates, because the code is
finite. Nothing I found today required a new component to be built; everything
was a component that already shipped and had never been fed a known-bad input.

The falsification I ran against "it is open-ended": if each fix opened two more,
the 2026-08-15→22 week would show the instrument count rising. It does not —
the count is 34 in a list written by hand, and this session's finding (Q4 #1)
lives inside I14 and I15, both already enumerated, and Q4 #2–#4 live inside
`build_acceptance.py`, which is **not enumerated at all** and should be. That
is one row to add, not a branching tree.

What must change to make the burndown honest:

1. Quote **29 unmeasured of 34**, not 7. The 7 is the no-candidate tail.
2. Add `bench/build_acceptance.py` (three instruments: the parent-fail check,
   the patch-pass check, the suite-green check) and `bench/cost_ledger.py` to
   the list. It is currently absent and it is the gate the build experiment's
   whole claim rests on.
3. Decompose I16 into its five probes, and I14/I15 into gate-and-reader, since
   both have now been falsified at sub-row granularity.
4. Treat `commissioning_candidate` as it is labelled — a heuristic with a
   measured 60% false-positive rate — and never quote the 27 as progress.

That yields a list nearer 40 rows with 5 measured. It is a long burn, it is
countable, and every row has a defined completion test ("feed it a known-bad
input and assert it answers differently"). **That is a backlog, not a
regress.** The founder is not spending borrowed money on something unbounded.
He is spending it on a bounded list whose size has been under-reported to him by
about 4×.

---

## Q4 — The eighth defect

Four findings. The first is the eighth defect and it is the one that matters.

### FINDING 1 (CRITICAL) — the falsifier gate ERRORs every falsifier that reads its target by a relative path

**`bench/reference_runner_v2.py:3819`**
```python
verdict = reverify_falsifier(fcode, repo_root=repo_root)
```
No `cwd`. `reverify_falsifier` therefore falls to
`tmp_cwd = cwd or _scratch` (`bench/falsifier_verify.py:1127`), a
`TemporaryDirectory`. Every relative path in the falsifier resolves against an
empty directory.

Same omission at:
* **`bench/reference_runner_v2.py:4547`** — sweep re-attachment.
* **`bench/routing.py:128`** — `verdict = reverify_fn(code)`, the routing
  ladder's re-ask, called with neither `repo_root` nor `cwd`.

**Failure scenario, measured, not hypothesised.** Exp 55 round 0. Six of ten
findings carried a falsifier that opens
`bench/cdsfl_registry/targets/control_two_distinct_defects.md` relatively. All
six returned `ERROR` → `UNCONFIRMED` → routed → both rungs re-ran the same
falsifier through the same broken cwd → `"routing ladder exhausted after 2
rung(s) reached a model; no rung returned a falsifier the runner could confirm"`
(`registry.entries.C0003.hil_reason`, identically at C0004, C0007–C0010) →
6 criticals locked irreducible → `IRREDUCIBLE_QUEUE` alarm, count 6 against a
bound of 2 → **run halted at round 0**.

With `cwd` supplied, five of those six CONFIRM and one REFUTES (table in Q1).
The run would not have halted.

**Why this is the eighth defect and not a duplicate of the seventh.** The commit
message at HEAD says the relative-path fix "is in". It is in
`run_discrimination_control` (five sites: `reference_runner_v2.py:3512, 3524,
3525, 3552, 3575`) and nowhere else. `falsifier_verify.py:864-876` states the
intent explicitly — *"`cwd` overrides it, and ONLY the discrimination control
passes it"*. The diagnosis was right about the mechanism and wrong about the
layer. The alarm's own text named the layer correctly: *"a gate that cannot
speak to this target"* (`irreducible_queue_alarm.notify`). The gate, not the
control.

**Severity.** This is the project's named house failure mode, executed by the
gate the founding claim rests on, and it is *inverted*: the falsifiers that
ignore the document CONFIRM, and the falsifiers that read it ERROR. Every prose
target in the archive is affected. Any archived `ERROR` verdict on a prose
finding is suspect until re-measured with `cwd`.

**Suggested fix (not applied).** Run the gate inside an overlay rather than the
bare repo — see Q2 point 2 for why `cwd=repo_root` is the wrong shortcut. Then
re-run the archive and publish the delta: *N archived ERROR verdicts that are
actually CONFIRMED or REFUTED*. That number belongs in the paper.

### FINDING 2 (CRITICAL) — `build_acceptance.py` step (3) passes vacuously when the suite fails to collect

**`bench/build_acceptance.py:278-280`**
```python
rc_suite, out_suite = _run(suite_cmd, wt, suite_timeout)
new_failures = failing_nodeids(out_suite) - baseline
if new_failures:
```
`rc_suite` is assigned and **never read** — verified by grep: line 278 is its
only occurrence in the file. And `failing_nodeids`
(**`bench/build_acceptance.py:120-122`**) matches only `^FAILED\s+(\S+)`.

A pytest **collection error** produces no `FAILED` lines at all; it aborts the
session:

```
=========================== short test summary info ============================
ERROR t/test_err.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.19s
```

Fed through the real function:
```
pytest returncode: 2
failing_nodeids  : set()
new_failures - baseline(empty): set()
=> step (3) verdict would be:  SUITE GREEN -> ACCEPTED
```

**Failure scenario.** A model patches `bench/reference_runner_v2.py` and
introduces a `SyntaxError`, an `ImportError`, or removes a symbol a test module
imports at top level. The whole suite fails to collect. Zero `FAILED` lines.
`new_failures` is empty. The gate returns `ACCEPTED` with the detail *"adds no
suite failure the parent does not already have"* — a patch that broke every test
in the repository, certified green by the gate whose entire claim is that it is
two-sided and mechanical.

The file's own docstring (lines 56-58) says *"'it failed' and 'it crashed' must
never render identically"*. Here they render identically, and the crash renders
as a pass.

**Suggested fix.** Parse `^ERROR\s+(\S+)` alongside `^FAILED`, and refuse
outright on `rc_suite in (2, 3, 4, 5)` with `INDETERMINATE_HARNESS_ERROR` —
symmetric with the treatment `rc_before` already gets at line 211. `rc_suite ==
1` with an empty `new_failures` set should also be refused, since it means the
run failed on tests the regex did not capture.

### FINDING 3 (HIGH) — `suite_baseline` caches an empty baseline on harness failure, re-arming the exact defect it was written to fix

**`bench/build_acceptance.py:151-165`**
```python
rc, _ = _run(["git", "worktree", "add", "--detach", str(wt), parent], REPO)
if rc != 0:
    _BASELINE[key] = frozenset()
    return _BASELINE[key]
...
except Exception:
    _BASELINE[key] = frozenset()
```

An empty baseline means `new_failures = failing_nodeids(out_suite) - ∅` = every
failure in the suite, including the pre-existing ones. The docstring at lines
131-142 records that this is precisely what falsely rejected a valid Codex patch
on 2026-08-22, and that *"near-0% is this harness's own pre-registered tell for
'the models cannot do the task'"*.

**Failure scenario.** `git worktree add` fails once (disk pressure, a stale
worktree lock, a concurrent run — and there is a live experiment writing to this
repo right now), or the baseline suite exceeds `suite_timeout` and
`TimeoutExpired` is caught by the bare `except Exception` at line 159. The
empty set is **cached in `_BASELINE`** for the rest of the process. Every
subsequent candidate is measured against a baseline of zero known failures.
`test_falsifier_cannot_read_the_key.py` is documented (line 134) as failing in
any fresh worktree, so *every* candidate then hits `REJECTED_SUITE_WENT_RED`.
The run reports near-0% acceptance, which the pre-registered tell reads as *the
models cannot do the task*.

A harness fault becomes a published verdict about six models' competence, via a
path the same file already identifies as this project's house failure mode.

**Suggested fix.** Return a sentinel (`None`) on failure, not `frozenset()`, do
not cache it, and have `evaluate` return `INDETERMINATE_HARNESS_ERROR` when the
baseline is unavailable. An unmeasured baseline is not a green baseline.

### FINDING 4 (HIGH) — model-supplied paths in `build_acceptance.py` can write outside the worktree

**`bench/build_acceptance.py:198-200`**
```python
tp = wt / test_path
tp.parent.mkdir(parents=True, exist_ok=True)
tp.write_text(test_src, encoding="utf-8")
```
and **`bench/build_acceptance.py:232-252`**
```python
f = wt / rel
...
f.write_text(src.replace(search, replace, 1), encoding="utf-8")
```

`test_path` comes from the model's `TEST_FILE:` line
(`bench/build_acceptance.py:107-111`) and `rel` from the model's SEARCH block
header (line 53). Neither is validated. `pathlib` discards the left operand on
an absolute right operand:

```
Path('/tmp/cdsfl_build/wt_abc') / '/Users/georgejackson/.zshrc'
  -> PosixPath('/Users/georgejackson/.zshrc')
Path('/tmp/cdsfl_build/wt_abc') / '../../../etc/hosts'
  -> PosixPath('/tmp/cdsfl_build/wt_abc/../../../etc/hosts')
```

**Failure scenario.** A model emits `TEST_FILE: /Users/georgejackson/
Developer_Projects/Constraint_Engineering/bench/reference_runner_v2.py` — by
confusion, not malice, and confusion is enough. `mkdir(parents=True,
exist_ok=True)` succeeds, `write_text` overwrites the live runner in the real
tree with the model's test source. The module docstring's isolation guarantee
(lines 36-38: *"A rejected patch cannot leave a trace"*) is void. The patch path
is narrower — `f.is_file()` at line 233 means it can only overwrite files that
already exist — which is precisely the dangerous set.

`_build_discrimination_overlay` in the runner already carries the right guard
(`bench/reference_runner_v2.py:2810-2820`: rejects absolute paths and any `..`
component). `build_acceptance.py` was written later and does not.

**Suggested fix.** Port that guard: reject absolute `test_path`/`rel`, reject
any `..` component, and assert `wt.resolve() in resolved.parents` before every
write.

### Two smaller notes, below the founder's threshold but cheap to close

* **`bench/cost_ledger.py:118-122`** — `_flush` writes the sole cost record with
  a non-atomic `write_text`, and `__init__` (lines 57-61) silently resets a
  corrupt ledger to `[]`, after which the next flush overwrites the file. A
  crash mid-write therefore destroys the run's spend record silently. Write to a
  temp file and `os.replace`; on a parse failure, refuse to overwrite.
* **`bench/cost_ledger.py:95-108`** — `totals()` sums `est_input_tokens` over
  metered rows only, but the module docstring (lines 23-25) says unmetered
  routes *"are still counted, because 'how much did we use' and 'how much were
  we charged' are different questions."* They are not counted. Add
  `est_*_tokens_unmetered`.
* **`bench/reference_runner_v2.py:1094`** cites
  `discrimination_control_blocks` at `RunnerConfig:594`; it is at line **641**.
  Stale reference in a comment that exists to stop a specific regression.

---

## WHAT I COULD NOT VERIFY

* Whether Findings 2 and 3 actually fired during the 2026-08-22 build
  experiment. `bench/logs/` is gitignored (`bench/build_acceptance.py:135`) and
  this worktree carries only
  `bench/logs/build_experiment_2026-08-22/composition_report.json`. The check
  the founder can run in the live tree: for each of the eight accepted patches,
  confirm the recorded `suite_after` summary shows a nonzero passed count rather
  than an error line, and confirm the baseline for that run was non-empty.
  A `suite_after` that reads `1 error` rather than `N passed` is Finding 2
  having fired.
* Whether the archived 2,030 findings' `ERROR` verdicts change under a
  `cwd`-corrected gate. Measured for the 6 in Exp 55; the archive re-run is the
  measurement that sizes Finding 1 and I did not run it, being read-only and
  outside the brief's scope.

---

## SUMMARY FOR THE FOUNDER

The control is not broken and it is not vindicated — it was never given a
genuine falsifier to judge, because the gate upstream of it kills every
falsifier that reads the document. Fix the gate's working directory and the
control immediately starts producing `DISCRIMINATES` verdicts; I made it do so
six times this afternoon against Exp 55's own findings.

The verdict-split CC1 proposes is worth doing, but not on the evidence it names.
The sound test is already half-written in `falsifier_verify.py` and switched
off.

The instrument backlog is real, bounded, and roughly four times larger than the
figure quoted. That is a reporting failure, not a scientific one. The work is
not bunk; the burndown is honest arithmetic away from being trustworthy.

Written by CC2, read-only, 2026-08-23T17:02:35+01:00.
