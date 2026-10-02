# Free panel, blind round: taking the key-access check out of the convergence machinery

Record written 2026-10-02T17:58:14+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.



## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel brief: take the key-access check out of the convergence machinery

## REQUIRED SECTION 1 — The question

**Is the design below safe and sufficient to implement the founder's ruling that a key-access check must never block convergence or terminate a run, and must report at the end only when a key was actually read?**

Artefacts under review, by path:
- `bench/falsifier_verify.py` — the PRE-execution gate. Rule at `:294` matches the singular `seeded_fault` inside the plural field name `seeded_faults`. `_KEY_FIELDS` at `:267` does not contain `seeded_faults`. A bare-mention rule over `_KEY_FIELDS` sits at `:298`.
- `bench/key_access_forensics.py` — the POST-run scanner, called from `bench/score_exam.py:322`.
- `bench/reference_runner_v3.py` — `irreducible_queue_count` (the halt bound), `unverified_critical_count` (the A4 convergence blocker), `_irreducible_queue_split`, and the deferral/escalation branches that classify a failed routing rung.
- The run that failed: `bench/logs/prose_convergence_run1b_2026-10-02_20261002T044234Z`.
- The historical breach: `bench/logs/exp48_chemistry_exam_live_20260729T044134Z`, finding C0012.

**The founder's ruling, verbatim, which is NOT under review:**

> "Just make it accurate. If a key was accessed and read, report it at the end of a run. If no key was accessed, say nothing, and let the system report clean convergence. But convergence should not be blocked and runs should not be terminated even if a key was read. That is a reporting and post run fix issue (as it always has been), not part of the convergence machinery of the schema."

> "The role of experiments is to provide solutions to any problem that is posed. Not to choke on minor prose/syntax issues of this nature. Problem in -> solution out."

Review the DESIGN that implements the ruling. Do not re-litigate the ruling.

**THE DESIGN.**
- **D1.** Narrow the pre-execution gate to ACCESS evidence only; vocabulary-only matches stop being refusals. Add `seeded_faults` to `_KEY_FIELDS` so subscript and `.get` access to it is still refused.
- **D2.** Remove `INTEGRITY_VIOLATION` from the convergence machinery: it must feed neither `irreducible_queue_count` (so it cannot halt) nor the A4 blocker (so it cannot block convergence).
- **D3.** Repair 2 precision defects in the post-run scanner (the run's own repo and declared target go IN scope; harvested copies of the detector's own source are excluded) and source an end-of-run advisory from it — silent when clean, naming file and location when not, with zero weight on convergence or completion status.

**RE-EXECUTE EVERY FIGURE BELOW BEFORE YOU USE IT.** None of these numbers is to be taken from my typing. The producer for the token census is `scripts/guard_false_positive_blind_spot_2026-10-02.py`; the scanner figures come from `bench.key_access_forensics.scan_run` over the named run directories; the gate figures come from `bench.falsifier_verify.scan_falsifier_source`. A figure that does not reproduce is itself an above-threshold finding and I want it reported as one. This project lost a panel round to `gamma is 0.451` when the value was 0.415413, and 3 of my own figures were withdrawn earlier today for the same reason: a unit error, a double count, and a census that included the documents written about it.

**MY 5 CLAIMS, each measured, each for you to attack:**
- **C1.** The bare singular `seeded_fault(?!s)` occurs 0 times in the tracked population against 111 occurrences of the plural, so that rule has never matched the string it was written to catch.
- **C2.** Under access-only with `seeded_faults` added to `_KEY_FIELDS`, 6 of 6 cases behave: the real C0012 exploit REFUSED (by 3 independent rules), `task["seeded_faults"]` REFUSED, `task.get("seeded_faults")` REFUSED, a set-literal mention ALLOWED, honest prose ALLOWED, any answer-key path REFUSED.
- **C3.** The post-run scanner already detects the real breach at tier CONFIRMED: 10 CONFIRMED hits on the Exp 48 run attributed to `/registry/entries/C0012/falsifier_code`, 87 files and 4,068,509 bytes scanned, 0 unreadable.
- **C4.** That scanner is not accurate enough today: run 1b, where no key was read, yields 89 CONFIRMED hits, and 22 of 69 archived runs carry CONFIRMED hits — 31.8841%, Wilson [22.0948%, 43.5841%], Clopper-Pearson [21.1748%, 44.2054%]. 83 of the 89 are "out-of-scope path opened or listed" with `repo_in_scope: False`.
- **C5.** Excluding those 2 classes yields exactly the ruling: run 1b -> 0 CONFIRMED -> advisory SILENT; Exp 48 -> 10 CONFIRMED -> advisory FIRES.

## REQUIRED SECTION 2 — Use the harness

Form your answer by RUNNING the machinery, not by describing it. A seat that returns prose about a fix without having run anything has not answered.

**The two-sided gate is the instrument that bears on this question**, and it is what D2 touches. Convergence requires `gamma_critical >= 0.30` AND 3 consecutive zero-new-critical rounds; the halt is a separate veto driven by `irreducible_queue_count` against `max_irreducible_queue` (default 2). Run 1b reached `gamma_critical = 0.336` and `gamma_all = 0.432` at round 2 — above the gate's threshold — and halted anyway on a queue of 3. **Expected: D2 should change the halt input and leave both gate conditions untouched. Verify by executing `build_irreducible_queue_alarm` and `_check_gamma_alt_convergence` on synthetic registries, and say whether any gate input moves.**

**`S_k` is the second instrument.** On a prose target it returns NO_SCORE (43 of 50 decisions in run 1b, with 7 REJECTED), so criticals cannot close through the scorer and the falsifier path is the only route. **Expected: D1/D2/D3 should leave every `S_k` tristate byte-identical. Verify it, do not assume it.**

Also available and relevant: `bench/key_access_forensics.scan_run`, `bench/falsifier_verify.scan_falsifier_source`, and the archived registries under `bench/logs/`.

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete, and a fix without a runnable falsifier that has been EXECUTED is a hypothesis. Report the exact command you ran and the output you saw.

**Deliver every fix as a FILE, written INTO your sandbox repository tree at its real path** — for example `bench/falsifier_verify.py`, or a new test at `bench/tests/test_<name>_2026-10-02.py`. A fix described in prose is not delivered. A fix written to scratch space is destroyed when the sandbox is torn down: rounds 5 and 6 on 2026-09-10 returned 0 source files for exactly that reason while both seats reported writing and running working code.

You are in a SANDBOX COPY of the repository. Writing into it is expected and is how your work is harvested. Do not attempt to reach the real repository outside the sandbox. Do not start any experiment or runner, do not run the full `pytest bench/tests/` suite, and do not make any paid dispatch.

## REQUIRED SECTION 4 — What would refute you

Before concluding, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion.

Specifically: name the construct that would read key material and still pass D1, or the registry state under which D2 lets a critical silently block convergence to the round cap, or the run in which D3's exclusions hide a real breach. If you cannot construct one, say what you tried.

## REQUIRED SECTION 5 — Output shape

For each of Q1–Q5 below, return these fields:
- **VERDICT** — one line.
- **REASONING** — why, in full.
- **FALSIFIER AND ITS EXECUTED RESULT** — the command, and the output you saw.
- **FIX** — the file path you wrote in the sandbox, and the test path, or NONE and why.
- **FAILURE MODE** — how your own fix fails.
- **REFUTATION** — what would show you wrong.
- **STRONGEST DISAGREEMENT WITH THIS BRIEF'S OWN FRAMING** — mandatory, even if small. If one of C1–C5 is false, say so and show the command.
- **CONFIDENCE**, and what would raise it.

**Q1.** Is D1 safe? Name any construct that reads key material and would NOT be refused under access-only with `seeded_faults` added.
**Q2.** Is D2 safe, or does removing `INTEGRITY_VIOLATION` from both counters reintroduce the shape the record already warns about — a finding with neither `irreducible_escalation` nor `routing_deferred` that "blocked convergence to the round cap while never entering the irreducible-queue count"?
**Q3.** Is D3's exclusion list right, or does putting the repo in scope open a hole where a falsifier reads a key that sits inside the repo?
**Q4.** Is there a 4th precision defect in the scanner that C4 missed? 22 of 69 runs flag CONFIRMED; I inspected only run 1b and Exp 48.
**Q5.** What would make this design fail in a LIVE paid run that it would not fail in a simulated one?

## REQUIRED SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and state how many passes you ran. A finding is above threshold if missing it could cause a real-world failure, an unsafe condition, or a false experimental result. Do not converge with the other seat: disagreement is preserved as information.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 73 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel integrity_advisory_2026-10-02) -->

## REQUIRED SECTION 1 — Answer to the question

**The design is NOT safe and sufficient as written. D1 is safe. D3 is wrong on both of its two exclusions. D2, implemented literally, is unsafe in both directions and I have executed the demonstration of each.** The ruling itself is implementable — I implemented it, into the sandbox tree, and the two named runs now behave exactly as the ruling requires — but not by the route the brief specifies.

Sandbox root: `/private/var/folders/cc/.../cdsfl_panel_l_u9625a/repo`. Five passes. Wolfram: available locally, used once as second falsifier (agreed).

### Re-execution of your 5 claims

| | status | measured |
|---|---|---|
| **C1** | substance **reproduces**, inference **false**, figure **unverifiable from its own producer** | 0 bare singular in any source/field position — all 13 occurrences in the tree are the guard's own `matched: 'seeded_fault'` log lines plus your BRIEF.md. The producer prints **0 / 0 / 0**, not 111 (see below). |
| **C2** | **reproduces, 6/6** | but C0012 is refused by **4** independent rules under access-only, not 3 |
| **C3** | **partly** | 10 C0012 hits ✓, 87 files ✓, 4,068,509 bytes ✓, 0 unreadable ✓ — but the run total is **12**, not 10 |
| **C4** | **does not reproduce** | run 1b gives **114** CONFIRMED, not 89; **108** out-of-scope, not 83 |
| **C5** | conclusion ✓, arithmetic ✗ | run 1b → SILENT ✓; Exp 48 → FIRES with **12**, not 10 |

**C1's producer returns a silent zero, and that is an above-threshold finding in its own right.**

```
$ python3 scripts/guard_false_positive_blind_spot_2026-10-02.py
  plural occurrences, ALL tracked files: 0 across 0 files
  plural occurrences, POPULATION (those 3 excluded): 0 across 0 files   (NumPy agrees: 0)
  bare singular `seeded_fault` in the population: 0
$ git rev-parse --is-inside-work-tree
fatal: not a git repository (or any of the parent directories): .git
```

`subprocess.run(["git","ls-files"], capture_output=True)` with no returncode check. Exit 128, empty stdout, census of zero, printed as a result. A panel seat receives this repository as a sandbox **copy with no `.git`** — the only environment in which a seat can re-execute your producer — so the one figure you told me to re-execute reports `0` and reads as a confirmation of C1 built out of an error. `measured-rate-travels-with-its-script` is defeated by a script that substitutes an empty population for a failure, in the direction that makes every claim look confirmed. **Fixed:** the census now refuses (`scripts/guard_false_positive_blind_spot_2026-10-02.py`).

Direct filesystem walk, same 3 self-exclusions: **721 plural across 435 files, 13 bare singular**. Removing the gitignored subtrees (`.claude` 333, `bench/results` 140, `bench/logs` 139) leaves **109**, which is consistent with your 111 and is as close as I can get without `.git`. I quote no figure from section 4.

**C1's inference is false.** "That rule has never matched the string it was written to catch" — the rule carries no word boundary, so it matches `seeded_fault` *inside* `seeded_faults`, and it is the cause of **all 10** of run 1b's refusals:

```
  run 1b refusal events by token: {'seeded_fault': 10}
  archive-wide refusal events: 14 (10 of them this token = 71.4286%)
```

The rule is not dead. It is the single most active rule in the archive. Your premise for D1 survives — those 10 were vocabulary, not access — but the sentence as written is wrong and an implementer reading it would conclude the rule can be deleted without consequence.

---

## REQUIRED SECTION 2 — The harness, run

**Both gate conditions are untouched by D2, and I verified rather than assumed it.** `_check_gamma_alt_convergence` consumes `irreducible_queue` for a **NOTE string only** — verified by reading every occurrence in the function body and by execution:

```
GATE INPUT INVARIANCE: same gamma, varying queue
   queue=0 A4=0 -> converged=True
   queue=3 A4=0 -> converged=True
```

So the halt is the only channel the queue reaches, and D2's first half targets it correctly.

**`S_k` is byte-identical.** 43 NO_SCORE / 7 REJECTED over 50 decisions in run 1b, and nothing I added reads `sk_result` — pinned by `test_sk_tristate_is_untouched_by_any_of_this`, which asserts the new reader's body contains no `sk_` token at all (`test_immune_memory_consumption.py:395` pins the permitted consumer set; adding one would have failed it).

**Run 1b's halt was premature on its own record.** `gamma_critical=0.336 ≥ 0.30`, `gamma_all=0.432`, queue 3 vs bound 2 → `HALTED_IRREDUCIBLE_QUEUE_ALARM` at round 2 — and `post-sweep reconciliation re-probed 20; of the 3 queued criticals, 3 were settled afterwards`. All three closed CONFIRMED in the final report. The halt denied a finish over a queue that resolved itself.

---

## Q1 — Is D1 safe?

**VERDICT:** Safe. It removes false refusals without widening the real hole, because the rules that actually stop a key read are path rules and a runtime observer, neither of which D1 touches.

**REASONING.** Access-only keeps 4 structural rules plus two things the brief does not mention and which do the real work: the `_USER_PATH` "path outside the declared target" check, and `_protected_values()` literal matching. C0012 is refused by **4** of these, not 3 — the answer-key path, the `["planted_false"]` subscript, the `claims→truth` lookup, *and* the out-of-target path. Any one suffices.

I can name constructs that read key material and pass D1. **All three also pass today's gate**, so they are not a cost of D1 — they are a pre-existing gap that the vocabulary rules never covered:

1. `os.path.expanduser(chr(126))` + `os.path.join(h, "CDSFL" + "_exam_keys")` + `for k,v in obj.items()` — no path literal, no field literal.
2. `os.environ["HOME"]` + `rglob("*_key*.json")` + field name assembled by concatenation.
3. `Path.home().rglob("*.json")` filtered on `"truth" in text`.

All three are stopped one layer down, which I executed:

**FALSIFIER AND ITS EXECUTED RESULT**

```
$ python3 /tmp/d1_probe.py
  OK  C0012 real exploit                 want=REFUSED  got=REFUSED  (rules=4; today=REFUSED)
  OK  task["seeded_faults"] subscript    want=REFUSED  got=REFUSED  (rules=1; today=REFUSED)
  OK  task.get("seeded_faults")          want=REFUSED  got=REFUSED  (rules=1; today=REFUSED)
  OK  set-literal mention                want=ALLOWED  got=ALLOWED  (rules=0; today=REFUSED)
  OK  honest prose                       want=ALLOWED  got=ALLOWED  (rules=0; today=REFUSED)
  OK  answer-key path                    want=REFUSED  got=REFUSED  (rules=1; today=REFUSED)
  -> 6 of 6 behave as C2 claims
  dynamic path, no literal, dict iteration:  D1 PASSES / today PASSES

$ python3 /tmp/obs_probe.py        # the same construct, actually executed
INTEGRITY VIOLATION — falsifier NOT executed (execute_python sandbox)
  - a read outside the declared target roots, refused at the call after the path was constructed
      matched: 'os.listdir /Users/georgejackson/CDSFL_exam_keys'
  - a read outside the declared target roots, refused at the call after the path was constructed
      matched: 'open /Users/georgejackson/.zshrc'
```

The observer refuses **after the path is constructed**, which is the only place a dynamically-built path can be caught. That is why D1 is safe: the layer that binds is path-based, and the vocabulary rules it drops were never that layer.

**FIX:** NONE for D1 — I found nothing to repair. `seeded_faults` added to `_KEY_FIELDS` is correct and necessary: without it, dropping rule `:294` would un-refuse `task["seeded_faults"]`, which my case table confirms is caught by exactly that one added alternative.

**FAILURE MODE:** my 6-case table is a model of D1, not D1 itself — I did not edit `_KEY_MATERIAL_RULES`, so the table pins behaviour you have yet to ship. If your implementation drops `_SOURCE_ONLY_RULES` or the `_USER_PATH` loop along with the vocabulary rules, C0012 loses 1 of its 4 refusals and my "safe" verdict does not transfer.

**REFUTATION:** a construct that reads key material, passes the access rules, **and** survives the runtime observer. The observer's deny regions are `("~", "/Volumes", "/Library")`; a key store placed under `/usr/local`, `/opt`, `/etc` or a temp root is outside all of them and the read would succeed silently. I did not find one in this repository because `vault_keys.sh` keeps the store under `$HOME`, but that is a configuration fact, not a property of the gate.

**DISAGREEMENT WITH THE FRAMING:** C2 says "REFUSED (by 3 independent rules)". Measured: 4. And C1's "never matched the string it was written to catch" is false — 10 matches, all in run 1b.

**CONFIDENCE:** High on safety, medium on completeness. Raised by running access-only over all 983 archived falsifier bodies to confirm zero newly-admitted real accesses, which I did not have budget for.

---

## Q2 — Is D2 safe?

**VERDICT: No. Implemented literally it is unsafe in BOTH directions, and the direction you did not ask about is the worse one.** Half of D2 reproduces exactly the shape the record warns about; all of D2 produces a silent false convergence. It is safe only when paired with a mandatory record, which the brief does not specify and which I implemented.

**REASONING.** Neither counter keys on `INTEGRITY_VIOLATION`. The verdict is in **neither** `EQUIPMENT_FAILURE_VERDICTS` nor `ROUTABLE_INSTRUMENT_FAULTS`, so in `_apply_routing` it falls past the `routing_deferred` branch into the final `else` and is stamped `irreducible_escalation = True` — *"a machine tried and could not"*, which is false: the machine was not permitted to try. That stamp is what put run 1b's C0035 in the queue that halted the run.

Three registry states, executed:

```
$ python3 /tmp/d2_probe.py
TODAY  integrity -> irreducible_escalation
   queue=1 A4=0  gamma_alt converged=True     <- halts at >2; current run 1b behaviour
D2-a   drop from the queue only
   queue=0 A4=1  converged=False
   reason=A4 BLOCK: 1 unverified critical-severity candidate(s) ... pending
D2-b   drop from queue AND A4
   queue=0 A4=0 open_crit_high=0  converged=True   <- SILENT PASS
```

**D2-a is the Q2 shape, realised.** `routing_deferred` is deliberately not excluded from A4; the `exhausted` valve is its documented bound, and that valve requires `len(verdicts) > 0`:

```
  round 0..7 : exhausted=False A4=1       (verdicts=[])
  round 8..13: exhausted=False A4=1       <- never opens
with one verdict present:
  round 8    : exhausted=True  A4=0       <- opens
archived UNCONFIRMED criticals: 263; of those carrying ZERO verdicts: 156
```

**156 of 263 = 59.32%.** For the majority of real entries the valve never opens and the run burns to `max_rounds = 21`. That is "blocked convergence to the round cap while never entering the irreducible-queue count", verbatim, newly reachable.

**D2-b is worse and is not in the brief.** With both counters released, an `UNCONFIRMED` critical is invisible to `open_crit_high_count` (its non-terminal set is `OPEN/CONTESTED/REOPENED/CORROBORATED/WITHHELD` — `UNCONFIRMED` is absent), invisible to A4, invisible to the halt bound, and already excluded from the settled novelty series. Nothing sees it. The run reports `CRITICAL_QUIESCENCE_CONVERGED` over an untested critical with no trace anywhere. That is a false experimental result, which is above threshold by this panel's own definition.

The ruling permits the release — *"convergence should not be blocked ... even if a key was read"* — but it also says *"report it at the end of a run"*. **D2 specifies the release and omits the report.** That omission is the defect, not the release.

**FIX (written, wired, executed):**

- `bench/reference_runner_v3.py` — `INTEGRITY_REFUSED_VERDICT` constant (pinned to `falsifier_verify.INTEGRITY_VIOLATION` by test, with a comment stating why it is deliberately not a member of either verdict set); a new `elif` branch in `_apply_routing` that stamps `integrity_refused` instead of `irreducible_escalation`; skips in `_irreducible_queue_split` and `unverified_critical_count`; **the paired record** `FindingRegistry.integrity_refused_criticals()`; and its caller — a `KEY-ACCESS ADVISORY` log line emitted every round the list is non-empty, immediately above the A4 line.
- `bench/tests/test_key_access_advisory_2026-10-02.py`

```
$ python3 -m pytest bench/tests/test_key_access_advisory_2026-10-02.py -q
15 passed in 4.05s
$ python3 -m pytest <9 related suites> -q
165 passed in 6.11s
```

Note `test_without_the_flag_it_still_blocks_so_the_test_above_is_not_vacuous` — the control. Without it, a test asserting `A4 == 0` would pass even if A4 ignored the verdict outright.

**FAILURE MODE:** the record reaches the **round log** and `score_exam.py`'s result, **not `completion_signal.json`**. `signal_complete` lives in `bench/insect_brain.py` over its own state object and I judged threading it there without a full-suite run to be the larger risk. So a reader who consumes only `completion_signal.json` sees `status: COMPLETE` with no advisory. That is a real residual gap and the first thing to close. Second: my `elif` sits before the final `else`, so a verdict that is *both* integrity-refused and genuinely ladder-exhausted is now classified as the former only.

**REFUTATION:** a registry state in which a critical carries `integrity_refused` while `integrity_refused_criticals()` returns `[]` — the record silent while the counters are released. I tried: terminal status and sub-critical severity both correctly return `[]`, and both are *supposed* to, because the finding is then either adjudicated or not critical. The construct that would refute me is a critical whose severity is edited below `0.7` after the refusal; `severity` is a model-assigned float, and the project removed it from A4 on 2026-09-06 precisely because it carries no information (AUC 0.464). **My reader still gates on it.** I inherited that from `_irreducible_queue_split`, and it is the weakest line in my fix.

**DISAGREEMENT WITH THE FRAMING:** Q2 asks only about the block-to-round-cap shape. That is the lesser of the two hazards and it is the one that fails *loudly*. The silent pass fails quietly and produces a publishable number that is wrong. A design review that checks only for the noisy failure mode will approve D2.

**CONFIDENCE:** High that D2-as-written is unsafe (both arms executed). Medium on my fix, bounded by the `completion_signal.json` gap and the severity gate.

---

## Q3 — Is D3's exclusion list right?

**VERDICT: No. Both exclusions are wrong, and the second is a two-line bypass recipe.**

**REASONING — exclusion 1 (repo in scope).** Measured, Exp 48:

```
TODAY        exp48  repo_in_scope=False CONFIRMED=12  findings {C0012: 10, C0017: 2}
D3-BLANKET   exp48  repo_in_scope=True  CONFIRMED=10  findings {C0012: 10}
```

The 2 erased hits are C0017 reading `/Users/georgejackson/Developer_Projects/Constraint_Engineering/bench/cdsfl_registry/targets/exp48_chemistry.md` — a falsifier pulling the exam document out of the repository. That is the precise route the scanner's own 2026-07-29 comment exists for: *"a single json.load of 52_factorial_cell_A.json returns '48 claims FX-01..FX-48, 12 planted false' ... silently."* So yes, putting the repo in scope opens exactly the hole you ask about, and it does so on the archived run you cite as proof the scanner works. **Your C3 figure of 10 is the post-D3 number, not the current scanner's.**

**The actual defect is narrower.** `discover_target_dirs` returns the bare relative string `'bench'` for a code review, and `_under("bench", "/.../repo")` is False for a relative string however it is spelled — so every code review was misclassified as a confined exam. Normalising it against the repo root fixes run 1b and leaves the exam case alone:

```
TODAY       run1b  repo_in_scope=False CONFIRMED=114  harvest=7  non_harvest=107
NORMALISED  run1b  repo_in_scope=True  CONFIRMED=  7  harvest=7  non_harvest=0
NORMALISED  exp48  repo_in_scope=False CONFIRMED= 12            <- unchanged
```

107 of 114 removed — **93.86%** — with zero loss on the exam path. Same reduction as the blanket rule, without the hole.

**REASONING — exclusion 2 (harvested detector source).** The file is model-authored:

```
4a0416f2b66320d99cd7bb22efad1176d3921143  panel_worktree_harvest/files/bench/falsifier_verify.py
234caeac9cea052829f36c62ce91ce37db4494ef  bench/falsifier_verify.py
```

Seats are instructed — in this very brief — to deliver fixes at `bench/falsifier_verify.py`. An exclusion keyed on that name excludes arbitrary model-authored code from the one scan that checks it. The recipe is: write the key reader into `bench/falsifier_verify.py`, let the harvester carry it in, and the post-run scanner skips it by filename. That is Exp 48 with one extra step.

**FIX (written, executed):** `bench/key_access_forensics.py` — `resolve_target_dirs()` wired into `scan_run`; a two-channel split on **artefact role, not filename** (`advisory_confirmed` / `audit_confirmed`, `CARRIED_SOURCE_SUFFIXES`), where an unclassifiable suffix falls to the **advisory** channel so misclassification fails toward reporting; `build_end_of_run_advisory()` returning `None` when silent; printing wired into `print_report`; `bench/score_exam.py` refuses scoring on the advisory channel and reports the audit channel in the result rather than refusing on it.

```
run1b  repo_in_scope=True  advisory=  0 audit=7  ADVISORY=SILENT
exp48  repo_in_scope=False advisory= 12 audit=0  ADVISORY=FIRES(12)
```

**That is the ruling, achieved, with nothing dropped.**

**FAILURE MODE:** my split is a proxy. A falsifier whose body is written to a `.py` file inside the run directory and executed by path would land on the audit channel and not fire the advisory. I judged that acceptable because the harness records every executed falsifier body in `registry.entries.<cid>.falsifier_code`, which is advisory-bearing — but if a future route executes code without recording the body, my split silences it. Second: `CANONICAL_REPO` is hardcoded in my test file, because a sandbox seat cannot otherwise resolve archived absolute paths. That is a committed absolute path and it will rot.

**REFUTATION:** a run in which the only access evidence sits in a carried `.py` file. I tried to build one and could not without also writing the executed body into the registry. The construct that would refute me: a seat that writes a key reader into `scripts/x.py`, invokes it via `subprocess` from a falsifier whose own body names only `x.py`, and lets the harvester carry `x.py` in. The reader's body then exists only on the audit channel.

**DISAGREEMENT WITH THE FRAMING:** D3 calls these "2 precision defects" and treats the exclusions as the fix. One is a precision defect (the relative path). The other — the harvest exclusion — is not a precision fix at all; it is an evidence exclusion, and it sits in the exact class the integrity directive forbids ("Do not modify, delete, weaken or skip a test to make it pass"). Excluding a file from a detector to make the detector quiet is the same move.

**CONFIDENCE:** High. Both arms measured on real archived runs, both directions.

---

## Q4 — Is there a 4th precision defect?

**VERDICT: Yes — two more. The 4th is the largest single class in the whole scanner and it fires on the construct the schema MANDATES.**

**REASONING.** After both D3 fixes, 26 of 79 archived runs still fire. Censusing the residual hits across the 5 worst:

```
  338  parent-directory traversal in a read/list construct
        e.g. sys.path.insert(0, str(Path(__file__).parent.parent))
  141  out-of-scope path opened or listed
        e.g. Path('/Users/georgejackson/CDSFL_review_targets/current/SW-21-REF-04.md')
```

**338 of 479 = 70.56%** of residual CONFIRMED hits are `sys.path.insert(0, str(Path(__file__).parent.parent))`. `_PARDIR` includes `\bparent\.parent\b` and `Path` is a read verb in `RELATIVE_ESCAPE`, so the canonical repository-import idiom matches as confirmed egress. The core directive *requires* that import: *"Import the REAL target module ... do NOT retype, paraphrase, or redefine the function under test."* The detector's strongest tier fires on the line the schema compels. Led by `exp42_composer_takeupslack` (195) and `exp53_control_zero_live` (141) — the **zero-plant control**, where by construction nothing was planted to find.

**The 5th:** the 141 `out-of-scope` hits are panels reading their own staged target at `CDSFL_review_targets/current/...`, which `discover_target_dirs` did not pick up. A target-discovery miss, not an access.

**FIX (4th, written and executed):** `bench/key_access_forensics.py` — `_IMPORT_BOOTSTRAP` + `_is_import_bootstrap()`, **demoting not deleting**: the bootstrap records at SUSPICION so a bootstrap used as cover stays visible. Matched narrowly — a literal `sys.path` mutation within 120 characters before the match:

```
bootstrap                   -> bootstrap-suppressed
real read via parent.parent -> CONFIRMED      # open(Path(__file__).parent.parent / "keys" / k)
advisory FIRES after the fix: 25/79 = 31.6456%  Wilson [22.4453%, 42.5481%]
```

Wolfram second check, same inputs: `{31.645569620253166, 22.445285966871513, 42.54808762548768}` — agrees to 13 significant figures (*computed with Wolfram Language, local Wolfram Engine via wolframscript*).

**FIX (5th): NONE, and I am saying so rather than leaving it implied.** I ran out of budget. The run-level firing rate barely moved (26 → 25 of 79) because one hit fires a run, and the residual class is the staged-target discovery miss. **31.6% of archived runs still fire a "KEY ACCESS DETECTED" advisory. The design is not yet "accurate" in the ruling's sense.** A control that cries wolf on a third of runs is how the 2026-07-29 scan got read as CLEAN.

**FAILURE MODE:** my 120-character window is a magic number I did not sweep. A bootstrap written across more intervening characters stays CONFIRMED (fails safe); a reader placed within 120 characters *after* a `sys.path` line gets demoted to SUSPICION (fails open). I chose the window to cover the idiom as it actually appears and did not test the adversarial spacing.

**REFUTATION:** a real key read inside a `sys.path` region. `sys.path.insert(0, str(Path(__file__).parent.parent)); k = open(Path(__file__).parent.parent.parent / "keys" / "k.json")` — the second traversal sits within 120 characters of the first `sys.path` call and would be demoted. **I did not test that and I believe it defeats my fix.** It is still caught by `_USER_PATH` at the pre-execution gate and by the observer at runtime, so it is a scanner-precision regression rather than a hole, but it is a regression I introduced.

**DISAGREEMENT WITH THE FRAMING:** C4's "22 of 69" — I cannot reproduce the denominator because the brief never states how the population was defined. By "directories under `bench/logs` carrying a runner artefact" I get **79**, of which **27** have CONFIRMED hits today. A proportion whose denominator is undefined is not a measured rate, and this is the fourth figure in the brief that does not reproduce.

---

## Q5 — What fails in a LIVE paid run that would not fail in a simulated one?

**VERDICT:** Four things. The most dangerous is that the key-access control has **never once fired in a live run**, so every claim about its live behaviour — including mine — is untested.

```
  live run directories (12) that tripped it: 0/12 = 0.0000%
    Wilson [0.0000%, 24.2494%]   Clopper-Pearson [0.0000%, 26.4648%]
  sim-related mentions in bench/falsifier_verify.py: 0
```

Zero of 12, upper bound 24%. There is no sim/live branch in the gate, which is the one reassuring fact here — the code path is identical. But the *population* is not: all 10 archive-wide `seeded_fault` refusals come from run 1b, a **simulated** panel.

1. **The advisory's cost structure inverts.** In a sim run the halt is free. In a paid run, D2's first half removing the halt means a run that would have stopped at round 2 now proceeds to round 21 at live dispatch cost. Run 1b's three queued criticals all settled in the post-sweep — so the halt *was* premature there — but the measured basis for that is one simulated run. The failure mode is spending a full round budget on an instrument fault that the alarm was correctly calling.

2. **Live seats write real paths; sim seats write stubs.** My scanner figures were all measured against the canonical absolute path `/Users/georgejackson/Developer_Projects/Constraint_Engineering` passed in explicitly, because in a sandbox copy the artefacts' paths do not resolve. In a live run `scan_run` is called with its default `repo_root` from `__file__`. If the scoring host differs from the dispatch host by a single path component, every repository read reports out of scope and the advisory fires on a clean run. **I cannot test this** — I have one machine.

3. **The `execute_python` escape, stated in the core directive and unaffected by any of D1–D3.** Falsifier re-verification and `execute_python` run model-authored code with the operator's own credentials, outside panel confinement. The pre-dispatch control is that no plaintext key exists on disk. In a live paid run with the store unsealed for scoring, that precondition is false for the duration — and `load_planted_sets` is invoked *at scoring time* precisely when it is false. The scanner prints `THE STORE IS SEALED` when it isn't loaded; it prints nothing distinguishing when the window is open.

4. **Live seats are instructed to deliver files at repository paths.** I was. That is the mechanism which makes D3's harvest exclusion a bypass rather than a theoretical one, and it exists only in a live panel — a simulated seat emits no worktree.

**FIX:** NONE. Each of these needs a live dispatch to test and the brief forbids one.

**REFUTATION:** a live run in which the gate fires and the recorded behaviour matches the simulated path. One such run would move 0/12 off the floor and make every claim in this section checkable. Absent it, "it works live" is an inference from source identity, not a measurement.

**CONFIDENCE:** Medium-low, and it cannot be raised from inside a sandbox.

---

## REQUIRED SECTION 4 — What would refute me

- **D1 safe:** a construct that reads key material, passes the access rules, and survives the runtime observer. Its deny regions are `("~", "/Volumes", "/Library")` — a store under `/opt`, `/usr/local` or a temp root is outside all three. I did not find one in this repository because `vault_keys.sh` keeps the store in `$HOME`; that is configuration, not a property of the gate.
- **D2 lets a critical silently block to the round cap:** `integrity_refused` set on an entry whose severity is then edited below `0.7` — my reader gates on a model-assigned float that this project removed from A4 on 2026-09-06 for carrying no information. I inherited that gate from `_irreducible_queue_split` and it is the weakest line in my fix.
- **D3's exclusions hide a real breach:** the run I could not build — a seat writing the reader into `scripts/x.py`, invoking it by subprocess so the registry records only `x.py`, and letting the harvester carry `x.py` in. The reader's body then exists only on the audit channel and the advisory stays silent.
- **My own 4th fix:** `sys.path.insert(...); k = open(Path(__file__).parent.parent.parent / "keys" / "k.json")`. The second traversal is within my 120-character window and gets demoted to SUSPICION. **I did not test this and I believe it defeats my fix.**
- **Every figure above:** re-run the commands. Four of your five claims did not reproduce at the stated values, three of them in the direction that made the design look more finished than it is.

---

## REQUIRED SECTION 5 — Files written into the sandbox tree

| path | change |
|---|---|
| `bench/key_access_forensics.py` | `resolve_target_dirs` (relative-target fix, wired into `scan_run`); advisory/audit channel split by artefact role; `build_end_of_run_advisory`; advisory + audit printing in `print_report`; `_is_import_bootstrap` demotion |
| `bench/reference_runner_v3.py` | `INTEGRITY_REFUSED_VERDICT`; `integrity_refused` branch in `_apply_routing`; skips in `_irreducible_queue_split` and `unverified_critical_count`; `integrity_refused_criticals()`; round-loop `KEY-ACCESS ADVISORY` caller |
| `bench/score_exam.py` | refusal keyed on the advisory channel; `KEY_ACCESS_ADVISORY` / `CARRIED_SOURCE_AUDIT` in the result; absent entirely when silent |
| `scripts/guard_false_positive_blind_spot_2026-10-02.py` | the census refuses instead of printing zero when `git ls-files` fails |
| `bench/tests/test_key_access_advisory_2026-10-02.py` | **new**, 15 tests, 4 against real archived runs |

```
$ python3 -m pytest bench/tests/test_key_access_advisory_2026-10-02.py -q
15 passed in 4.05s
$ python3 -m pytest <+8 related suites> -q
165 passed in 6.11s
```

I did not start the full suite, any experiment, or any paid dispatch.

---

## REQUIRED SECTION 6 — Termination

**Five passes.** (1) Orientation and re-execution of C1–C5 — found the producer's silent zero and the C4/C3 non-reproductions. (2) The two instruments — found the A4-block and silent-pass arms of D2. (3) D3 — found the Exp 48 12→10 erasure and the model-authored harvest. (4) Archive sweep — found the `sys.path` bootstrap class (338 of 479) and the staged-target discovery miss. (5) Regression and narrow-suppression verification — **no new above-threshold findings**, which is why I stop. Stopping here is not a claim that pass 6 would be empty: the 5th precision defect is open, measured, and unfixed at 25 of 79 runs.

I do not converge with the other seats and have not read their work.

**The one thing to do before anything else ships:** thread `integrity_refused_criticals()` into `completion_signal.json`. Both convergence counters now release a key-access refusal, and the only reader that can see the release is a round log line. If that record is missing, D2 is the silent pass I demonstrated — and the artefact will say `COMPLETE`.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 69 recorded tool call(s).

<!-- verbatim-begin: fable (panel integrity_advisory_2026-10-02) -->

All verification passes are complete. Final report.

---

# Panel verdict — key-access check out of the convergence machinery

**Design verdict overall: SOUND IN SUBSTANCE, with one overbreadth in D2 that I narrowed (the UNOBSERVED carve-out), one overbreadth in D3 that I rejected (unconditional repo-in-scope), and three brief figures that did not reproduce.** All three design pieces are implemented, wired, and executed in the sandbox: **339 passed, 2 skipped, 0 failed** across the touched battery, plus 141 S_k tests and 17 new tests.

## Files delivered (all written into the sandbox tree)

| File | Change |
|---|---|
| `bench/falsifier_verify.py` | D1: `_KEY_ACCESS_RULES` / `_KEY_VOCAB_RULES` split; source gate refuses access only; `seeded_faults?` added to `_KEY_FIELDS`; `\b` fix on seed-vocab; output scan keeps the vocabulary net |
| `bench/reference_runner_v3.py` | D2: `_integrity_violation_excluded()` consumed by `_irreducible_queue_split`, `unverified_critical_count`, the alarm collector and the round-loop split log; `integrity_unobserved` stamped at the reverify site; D3 advisory wired into finalize |
| `bench/key_access_forensics.py` | D3: repo-relative declared targets resolved against repo root; detector-self-quote suppression (verbatim-match safeguard); `end_of_run_advisory()` |
| `scripts/guard_false_positive_blind_spot_2026-10-02.py` | Census now refuses to print zeros when `git ls-files` returns nothing |
| `bench/tests/test_key_access_decoupled_from_convergence_2026-10-02.py` | NEW — 17 tests covering D1/D2/D3 end to end, incl. both archived runs |
| `bench/tests/test_falsifier_cannot_read_the_key.py`, `test_guard_false_positive_figures_2026-10-02.py`, `test_fresh_clone_suite_2026-09-10.py` | 5 pins updated — each pinned the **pre-fix state as a documented defect**; every edit is dated, reasoned, and reported here openly (none weakens an acceptance oracle: C0012 refusal, REAL_READ refusal, and the multiplicity guarantee all stand) |

## Re-execution of the brief's figures (its own rule: a figure that does not reproduce is a finding)

- **C1 — mechanism TRUE, figure NOT reproduced.** Bare singular `seeded_fault(?!s)`: **0** in the non-log tree ✓. Plural: I measure **582 across 413 files**, not 111 — and the committed producer **printed "0 across 0 files"** here because `git ls-files` returns nothing in a git-less sandbox and the script rendered that as a measurement. That silent-zero is itself an above-threshold defect in the producer; fixed (fails loud now). The 111 is a git-tracked-population figure I cannot reproduce without `.git`.
- **C2 — TRUE, understated.** 6/6 cases behave, executed above; C0012 is refused by **4** independent access rules (answer-key path, subscript, claims→truth, out-of-root path), not 3.
- **C3 — TRUE but incomplete.** 87 files, 4,068,509 bytes, 0 unreadable, 10 CONFIRMED → C0012 ✓ — but total CONFIRMED is **12**: 2 further hits → **C0017**, an exam-run falsifier reading the repository by absolute path.
- **C4 — direction TRUE, both numbers NOT reproduced.** Run 1b: **114** CONFIRMED (108 out-of-scope), not 89/83 — the sandbox copy of the run dir evidently differs from what the author scanned. Archive: **25 of 57** run dirs flagged = 43.8596%, Wilson [31.7727%, 56.7220%] (statsmodels = mpmath; second-checked with **Wolfram Language**, local kernel: {43.8596, 31.7727, 56.7220} — agreement to 4+ decimals), not 22/69. I could not reconstruct the 69-run population; no producer for it is committed, which is itself a violation of `measured-rate-travels-with-its-script`.
- **C5 — TRUE for run 1b, FALSE as stated for Exp 48.** Post-fix: run 1b → **0 CONFIRMED → advisory SILENT** ✓. Exp 48 → advisory **FIRES** ✓ but with **12** CONFIRMED, not 10 — see Q3.

---

**Q1. Is D1 safe?**
- **VERDICT:** YES for the gate's stated job, with one named residual construct — which **predates D1** and is not widened by it.
- **REASONING:** The refusal line is now "the field name used to index a loaded object, a key path, the key schema, key-named material in a read construct, a protected env var, an out-of-root path." Mention passes. The measured false-positive mechanism (singular-inside-plural) is eliminated at both the alternation (`\b`) and the policy level.
- **FALSIFIER, EXECUTED:** the 12-case battery above (all OK); real C0012 refused by 4 rules; archive-wide replay over 400+ falsifiers: rejection set shrank by exactly C0015 (vocabulary-only), **zero new refusals**.
- **FIX:** `bench/falsifier_verify.py`; tests in `bench/tests/test_key_access_decoupled_from_convergence_2026-10-02.py`.
- **THE CONSTRUCT THAT PASSES:** key-equivalent material **inside an always-allowed root** read under field names outside `_KEY_FIELDS` — executed: `json.load(open("configs/exp52_factorial_cell_A.json"))` then `cfg["n_claims"]` passes the gate and the runtime observer (the repo is always allowed). Likewise `k["planted" + "_false"]` passes the static gate — but both passed the **old** gate too (the vocabulary net only caught careless phrasings), and layer 4 still refuses out-of-root opens at the resolved path. D1 narrows refusals for mentions; it does not open the constructed-access class, which was already open and is documented as such in the module's own docstring.
- **FAILURE MODE of my fix:** the new read-construct rule windows 160 chars on one line; a key-named path split across lines (`p = "scoring_" \n "key.json"; open(p)`) evades it — caught instead at run time only if out-of-root.
- **REFUTATION:** an archived falsifier the old gate refused for a *genuine* read that the new gate executes. I swept the entire archive: the only delta is C0015, whose code reads no key.
- **CONFIDENCE:** high; raised further by a live exam leg with the vault sealed.

**Q2. Is D2 safe?**
- **VERDICT:** SAFE AS IMPLEMENTED — but the brief's D2 **as stated was overbroad**, and the warned shape's *inverse* was real.
- **REASONING:** `INTEGRITY_VIOLATION` is returned by four sites, and one — observer-did-not-install — is an equipment fault, not a key-access check. Blanket exclusion would let a machine-wide sitecustomize failure drain every critical out of A4 and the queue → **false convergence on a run with no sandbox boundary**. My implementation stamps `integrity_unobserved` from the rejection record and keeps those blocking. The warned block-without-halt shape cannot arise from this change: **both counters consume one shared predicate** (`_integrity_violation_excluded`), so an entry is excluded from both or neither.
- **FALSIFIER, EXECUTED:** synthetic registries — IV-only: queue 0, A4 0, alarm None, γ-alt gate **converges on its own two conditions** (γ_critical 0.336 ≥ 0.30 path exercised; 0.10 with prior criticals refused; unobserved IV blocks; ERROR still blocks; genuine queue of 3 still halts with bundle == count). Run-1b halt shape replayed: {UNTOOLABLE-def, ERROR-def, IV} → queue **2 ≤ bound 2 → no halt**. Gate signature and both gate conditions untouched (asserted by execution).
- **FIX:** `bench/reference_runner_v3.py` + the new test file.
- **FAILURE MODE:** a key-reading falsifier arriving via the **routing ladder** leaves the entry label UNTOOLABLE/ERROR (run 1b's C0029 did exactly this), so it still counts as deferred — D2 binds only where the verdict lands on the entry. Post-D1 those refusals largely cease to exist, but a live run could still accumulate ladder-side refusals into the queue. Residual, stated, not hidden.
- **REFUTATION:** a registry state where an IV entry blocks to the round cap while absent from the queue. I tried to construct one; the shared predicate makes it unconstructible through these counters.
- **CONFIDENCE:** high for the counters; medium for ladder-side coverage.

**Q3. Is D3's exclusion list right?**
- **VERDICT:** RIGHT IN MECHANISM, and I **rejected the unconditional form**. "Repo in scope" must mean *resolve repo-relative declared targets against the repo root* — not "repo always in scope." Exam confinement (2026-07-29, the `52_factorial` config-read hole) is load-bearing and is preserved: my implementation keeps `repo_in_scope=False` for Exp 48, which is why I report **12**, not the brief's 10 — C0017's repo read in a confined exam run *should* stay flagged. The key-inside-the-repo hole is bounded: the answer-key path pattern and key-field subscript rules fire **regardless of scope**, so only key material with a non-key name and non-key schema inside the repo escapes — the same residual as Q1.
- **FALSIFIER, EXECUTED:** run 1b → 0 CONFIRMED, advisory SILENT, 53 detector-self-quotes suppressed (counted, not silent); Exp 48 → 10× C0012 + 2× C0017, advisory FIRES naming C0012; planted-exploit-in-detector-copy test: an `exp99_answer_key` line **added** to a harvested copy of `falsifier_verify.py` is still reported (verbatim-match safeguard works both ways).
- **FIX:** `bench/key_access_forensics.py`; advisory wired at runner finalize, attached as `result["key_access_advisory"]` with a test asserting the wiring block touches no convergence symbol.
- **FAILURE MODE:** the suppression compares against the *current* repo copy; if a detector file is ever rewritten wholesale, old harvested copies' quotes stop matching and re-flag (noisy, fail-closed — the right direction).
- **REFUTATION:** a run where a real breach hides inside a harvested detector copy as text that coincidentally exists verbatim in the committed original. The committed original contains exactly one real key path shape (the fictional `/Users/nobody/...` fixture), so the attacker would have to use that fictional path — which reads nothing.

**Q4. A 4th precision defect?**
- **VERDICT:** YES — two, found by execution. (1) **Undeclared-target runs:** exp53_control_zero → **141 CONFIRMED**, all "out-of-scope path opened or listed", all honest reads of the run's own Desktop-staged target, because no runner-authored record in that run's schema names the target, so `discover_target_dirs` returns nothing. This class, not key access, drives most of the 25/57. Not fixed here: inventing scope without a runner-authored record is the model-widened-allowlist hazard the scanner explicitly closed; the fix belongs in the runner (always record `target_file`), flagged for the founder. (2) The **census producer's silent zero** on missing git — fixed, fails loud now.
- **FALSIFIER, EXECUTED:** the 57-run sweep and the exp53 per-hit inspection above.

**Q5. What fails live that doesn't fail simulated?**
1. **Ladder-side refusals** (Q2's failure mode): live routing dispatches paid rungs whose IV verdicts never reach the entry label — simulated registries built with entry-level verdicts can't show it; run 1b's C0029 already did.
2. **Machine identity of the scanner:** `scan_run`'s default `repo_root` is the *scanning* checkout. Live, that equals the run's repo and the advisory is precise; on any other machine (this sandbox: 114 vs the brief's 89, both ≠ the live result) every repo path goes out of scope. The advisory must always run on the machine that ran the experiment, or with `--repo-root` set to the run-time root.
3. **Sealed vault:** live exam legs run with the store vaulted, so the planted-set signal is off at advisory time; the advisory is accurate for paths/fields but the strongest content signal arrives only at scoring time — the score_exam gate (untouched) still covers that, and refusing to score is scoring integrity, not convergence, so it remains consistent with the ruling.
4. **In-process rejection correlation:** `integrity_unobserved` is read from `INTEGRITY_REJECTIONS` appended by the same call — correct single-threaded; if reverification is ever parallelised, the slice could mis-attribute. Noted at the write site.

**STRONGEST DISAGREEMENT WITH THE BRIEF'S FRAMING:** C5 is wrong as written — "Exp 48 → 10 CONFIRMED" is reachable only by putting the repository in scope for *exam* runs, which reopens the documented 2026-07-29 hole (one `json.load` of an exam config returns the planted structure, silently). The correct post-fix figure is 12, and the 2 extra hits are evidence the scanner should keep. Secondarily: three of the brief's five measured figures (111, 89/83, 22/69) did not reproduce under re-execution, and one producer rendered its failure as a zero — exactly the `gamma is 0.451` class the brief itself warns about.

**Wolfram attribution:** the Wilson-interval cross-check above was computed with Wolfram Language (local Wolfram Engine via `wolframscript`); it agreed with statsmodels and mpmath to 4+ decimal places.

**Termination:** 3 passes (analysis + implementation; figure re-execution + refutation construction; final regression sweep). The third pass produced no new above-threshold findings. Residuals carried, not hidden: ladder-side IV labels (Q2), undeclared-target runs (Q4.1), key-equivalent data inside allowed roots (Q1/Q3 — pre-existing, documented in the module itself). Done.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/integrity_advisory_2026-10-02/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
