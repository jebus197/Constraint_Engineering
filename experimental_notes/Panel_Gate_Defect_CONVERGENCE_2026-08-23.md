# The falsifier gate rewards falsifiers that never read the document

**23 August 2026, 17:13 BST.** Panel: CC1, CC2, Fable. Convergence COMPELLED by founder override. Both external reviewers worked read-only in separate disposable worktrees at HEAD `66de417`, with no contact with each other.

Full unfiltered reviews, file/line references intact: `Panel_Gate_Defect_CC2_FULL_2026-08-23.md` (643 lines), `Panel_Gate_Defect_Fable_FULL_2026-08-23.md` (405 lines).

---

## 1. The finding, converged

The falsifier gate executes every falsifier in a throwaway scratch directory in which the target document does not exist. A falsifier that opens its target by a repo-relative path therefore dies on `FileNotFoundError` and is recorded as `ERROR`. A falsifier that invents its own numbers and opens nothing runs cleanly and is recorded as `CONFIRMED`.

**The gate structurally selects FOR the pathology the discrimination control exists to catch.**

Three call sites, all missing `cwd`:

| site | what it is |
|---|---|
| `bench/reference_runner_v2.py:3819` | the main gate, `apply_falsifier_verdicts` |
| `bench/reference_runner_v2.py:4547` | sweep re-attachment |
| `bench/routing.py:128` | the routing ladder's re-ask — called with neither `repo_root` nor `cwd` |

Default resolved at `bench/falsifier_verify.py:1127` (`tmp_cwd = cwd or _scratch`). The comment at `falsifier_verify.py:865-867` states the intent outright: *"ONLY the discrimination control passes it."*

**Aggravating factor (Fable).** The round prompt at `reference_runner_v2.py:4366-4377` names the target by relative path and instructs *"OPENS THE TARGET DOCUMENT BY PATH (the path named above)."* The harness orders the behaviour it then punishes. And the model-facing `execute_python` tool loop shares the same scratch cwd (`falsifier_verify.py:885`), so a model iterating a CORRECT falsifier sees `FileNotFoundError` and is trained away from reading the document.

## 2. The measurement both reviewers reproduced independently

Re-running Exp 55's own archived falsifiers through the real `bench.falsifier_verify.reverify_falsifier` — first exactly as the gate calls it, then with `cwd` supplied. Both reviewers produced this table separately; it agrees row for row.

| finding | reads target | archived | gate's call (no cwd) | with cwd |
|---|---|---|---|---|
| C0001 | no (detached) | CONFIRMED | CONFIRMED | CONFIRMED |
| C0002 | no (detached) | CONFIRMED | CONFIRMED | CONFIRMED |
| C0003 | yes | ERROR | ERROR | **CONFIRMED** |
| C0004 | yes | ERROR | ERROR | **CONFIRMED** |
| C0007 | yes | ERROR | ERROR | **CONFIRMED** |
| C0008 | yes | ERROR | ERROR | REFUTED |
| C0009 | yes | ERROR | ERROR | **CONFIRMED** |
| C0010 | yes | ERROR | ERROR | **CONFIRMED** |

With `cwd` supplied the discrimination control returns **DISCRIMINATES** — the verdict it was built for and has never once produced on a live run. CC2 produced it six times; Fable produced it on C0009 and recorded it as *"the first DISCRIMINATES in project history, produced in a reviewer's scratch worktree."*

CC2: *"It was not blind. It was starved."*

## 3. The causal chain of the halt, measured

Six relative-path falsifiers → `ERROR` → `UNCONFIRMED` → routed → **both rungs re-ran the same falsifier through the same broken cwd** → *"routing ladder exhausted after 2 rung(s)"* → six criticals locked irreducible against a bound of two → `IRREDUCIBLE_QUEUE` alarm → **halt at round 0**.

Four of the six queue items that halted the run (severities 0.82, 0.88, 0.75, 0.85) are harness-manufactured errors.

**Fable predicted, before the result existed, that the re-run would halt at round 0 again. It did:** `HALTED_IRREDUCIBLE_QUEUE_ALARM`, `halted_at_round: 0`, 1178 s.

## 4. CC1's claims, adjudicated

- **Claims 1 and 2 (C0001/C0002 detached; C0009 genuinely reads): CORRECT.** Both reviewers.
- **Claim 3 (2 of 2, 100%): count correct, inference INVALID.** The sample was size
two and was selected by the very defect that produced it. The control has never adjudicated a single target-reading falsifier on a live run.
- **Claim 4 (`retarget_substitutions == 0` detects detachment): FALSE.**
`_retarget_falsifier` (`reference_runner_v2.py:2837-2852`) counts only the literal absolute repo-root string, so it reads 0 for every relative-path reader. Counterexamples run by CC2: `linecache.getlines`, a runtime-built `os.sep.join` path, a glob-discovered path, an env-var-built path — all read the target, all score 0, all outcome `DISCRIMINATES`. `falsifier_verify.py:391-393` already states the principle: *"a path is a string a program computes, so no amount of reading the source can decide where the program will actually read."*
- **CC1's "7 of 34 instruments remain": WRONG BY ~4x, in the reassuring direction.**
The 7 counts instruments lacking even a candidate test. `measured: true` is set on exactly **5** of 34 rows. The open count is **29 of 34**. The heuristic producing the other 27 is wrong 3 times in 5 by its own printed calibration, always over-claiming — including scoring the falsifier gate itself (I14) as commissioned when measurement says it is not.

## 5. The proposed fix was unsafe; the sound test is already half-written and switched off

CC1 proposed deriving a determinate `DETACHED_FALSIFIER` verdict from `retarget_substitutions == 0` plus a static scan for file-access call sites. Both reviewers rejected it, on two independent grounds:

- The first conjunct carries no information (§4).
- A static call-site scan has no closed enumeration — `linecache.getlines`,
`fileinput.input`, `pkgutil.get_data`, `codecs.open`, `mmap`, `pandas.read_csv`, `subprocess.run(["cat", ...])`, `getattr(builtins, "open")`.

**The sound test is documented in the codebase and was never implemented.**
`falsifier_verify.py:403-404` states the observer's second job verbatim: *"Record whether the falsifier ever opened its target, which is what tells a demonstration apart from an instrument that broke before it started."* The audit hook emits only on refusal (`_emit("D open\t" + path)`, `falsifier_verify.py:497`) and `_read_trace` (`falsifier_verify.py:650-669`) parses only the ready marker and `D ` lines. **No allowed open is recorded anywhere.** CC2 sizes the repair at four lines.

## 6. The one substantive divergence, and its resolution

CC2 proposed the verdict be named `DETACHED_FALSIFIER`. Fable proved by execution that the name overclaims: a falsifier that DOES open and read the target, but carries a memorised fallback on read failure, lands in the identical record —

```python
try:
    T = pathlib.Path("bench/cdsfl_registry/targets/control_two_distinct_defects.md").read_text()
    fmax = int(re.search(r"f_max = (\d+) Hz", T).group(1))
except Exception:
    fmax = 180
```
→ `INDETERMINATE_NOT_INTERCEPTED`, `retarget_substitutions: 0`, `intercepted: False`.

What the tripwire measures is **output insensitivity to target content**, which is strictly weaker than detachment. Fable's honest name: `TARGET_INSENSITIVE`.

**Resolution: the two are not alternatives, they are two different measurements, and they compose.**

| available | source | verdict | meaning |
|---|---|---|---|
| today | tripwire probe | `TARGET_INSENSITIVE` | output does not depend on target content |
| after the 4-line observer fix | observer trace | `DETACHED_FALSIFIER` | the falsifier never opened the target at all |

Fable's naming is adopted for the verdict available today. CC2's verdict becomes available, and correct, only once the observer records allowed opens.

## 7. Wiring, converged exactly

Both reviewers independently reached the identical wiring, and the identical prohibition:

- Membership in **`ROUTABLE_INSTRUMENT_FAULTS` only** (`reference_runner_v2.py:1099`).
- **Never** `EQUIPMENT_FAILURE_VERDICTS` (`reference_runner_v2.py:1086`) — the T04
guard in `FindingRegistry.resolve` (`reference_runner_v2.py:1516-1533`) demotes terminal statuses unconditionally for that set. Adding it there is the back-door-blocking merge that three tests were written to catch.
- Stamp in `_apply_discrimination_control` (def at 3601) as a new branch between the
`DISC_FAILED` branch (3692-3707) and `elif outcome in DISC_INDETERMINATE` (3709).
- Demotion of `CONFIRMED` gated on `discrimination_control_blocks`
(`reference_runner_v2.py:641`, default `False`).

**Fable's access-washing objection decides the blocking question.** Blocking the insensitive bucket while `DISC_FAILED` stays record-only rewards adding one cosmetic `read_text()` line to an otherwise worthless falsifier — the 2026-08-12 panel's access-versus-dependence objection verbatim, recorded at `3841-3850`. **Both outcomes block or neither. One founder ruling, not two wirings.**

## 8. Further defects found, beyond the eighth

**[BLOCKING] `bench/build_acceptance.py:278-280`** — `rc_suite` is assigned and never read, and `failing_nodeids` (120-122) matches only `^FAILED\s+(\S+)`. A pytest **collection error** produces no `FAILED` lines, so `new_failures` is empty and step (3) returns ACCEPTED. A patch introducing a `SyntaxError` or `ImportError` that breaks the entire suite is certified green by the gate whose whole claim is that it is two-sided. The file's own docstring (56-58) says *"'it failed' and 'it crashed' must never render identically."* Here the crash renders as a pass. Fix: parse `^ERROR\s+(\S+)` alongside `^FAILED`; refuse on `rc_suite in (2,3,4,5)` symmetrically with `rc_before` at line 211; refuse `rc_suite == 1` with an empty failure set.

**[BLOCKING] `bench/build_acceptance.py:151-165`** — `suite_baseline` caches `frozenset()` on worktree-add failure (155) or any exception including baseline timeout (159). Found independently by both reviewers. An empty baseline makes every pre-existing failure read as new; the docstring (131-142) records that this exact thing falsely rejected a valid Codex patch on 2026-08-22, and that near-0% acceptance is *"this harness's own pre-registered tell for 'the models cannot do the task'."* The poisoned baseline is cached for every subsequent candidate. Fix: return `None`, do not cache, return `INDETERMINATE_HARNESS_ERROR`. An unmeasured baseline is not a green baseline.

**[NEEDS A FOUNDER RULING] `bench/build_acceptance.py:198-200` and `232-252`** — `test_path` (from the model's `TEST_FILE:` line) and `rel` (from the SEARCH header) are unvalidated, and `Path(wt) / '/absolute/path'` discards the left operand. A confused model could overwrite the live runner in the real tree, voiding the module's stated isolation guarantee (36-38). `_build_discrimination_overlay` (`reference_runner_v2.py:2810-2820`) already carries the correct guard; port it.

**[NEEDS A FOUNDER RULING] a status contradiction (Fable)** — in default non-blocking mode the `DISC_FAILED` helper stamps `NON_DISCRIMINATING`, `verified=False` and demotes to `UNCONFIRMED` (3694-3702); the gate then re-resolves `CONFIRMED` and sets `verified=True` (3846-3847). The record left behind reads `status: CONFIRMED, verified: True, falsifier_verdict: NON_DISCRIMINATING, mechanical_fault: True`, and it flaps every cached round. The helper's mutations belong behind the same flag as the gate's.

**Minor, both reviewers:** `cost_ledger.py:118-122` non-atomic `write_text` on the sole spend record, and `__init__` (57-61) silently resetting a corrupt ledger to `[]` before the next flush overwrites it; `cost_ledger.py:95-108` does not count unmetered tokens despite the docstring (23-25) saying it does; `cost_ledger.py:104` `wall_clock_s` is cumulative dispatch-seconds, not wall clock; `reference_runner_v2.py:1094` cites `RunnerConfig:594` for `discrimination_control_blocks`, which is at **641** — a stale reference inside the comment that exists to prevent a specific regression.

## 9. The answer to the founder's question

**Not bunk.** Both reviewers, independently and definitively.

CC2: *"The instruments are a closed hand-written list in source, not a discovered set that grows when you look at it... That is a backlog, not a regress. The founder is not spending borrowed money on something unbounded."*

Fable dissents on how close, and the dissent is preserved rather than smoothed: *"'Demonstrably closer to iron-clad' needs a convergence curve (defects-per-run over time) that nothing currently tracks; until it exists and bends down, the supportable claim is 'failing loudly instead of silently, with one dominant defect class still active.'"*

Fable also names a systematic bias that outranks both positions: **all eight defects debited the models' measured competence — the very quantity this project measures.** No model-competence figure from this bench should be quoted externally until a run completes with zero new harness defects.

## 10. The operational consequence

**[BLOCKING] Do not launch another paid run before the gate `cwd` fix.** Both reviewers, unprompted and independently. At HEAD every prose-target run is guaranteed to burn a full five-model round (1152 s and 1178 s measured, two runs) and halt at round 0.

The fix must NOT be `cwd=repo_root`: `falsifier_verify.py:18-23` records that the throwaway cwd exists so a relative-path *write* cannot touch the tree. Both reviewers converged on the same alternative — materialise a scratch working directory containing the target (and declared context files) at its repo-relative path, and pass that. CC2 adds that the audit hook already receives the mode argument, so denying write-mode `open` outside the scratch dir closes the residual symlink risk CC1 flagged at `falsifier_verify.py:877-884`.

Ship it with the regression test neither the fix nor `bench/tests/test_three_gaps_2026-08-23.py` currently has: *a relative-path falsifier reaches CONFIRMED through `apply_falsifier_verdicts`*. Fable verified that **no test anywhere pins cwd behaviour.**

Written under CDSFL note standard v1.2 (14 May 2026).
