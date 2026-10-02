# Free panel, star round: the 6 disputes settled, and the $HOME hole

Record written 2026-10-02T17:58:14+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.



## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel brief, ROUND 2 (STAR): reconcile the blind round's disputes

## REQUIRED SECTION 1 — The question

**Round 1 was blind. You each answered alone, in separate sandboxes, and you disagree with each other and with me on 6 specific points. Which of the 6 resolutions is correct, and does the design survive them?**

This is the SHARED round of the project's standard blind-then-star topology, the same shape the real experiments use. Both round-1 replies are reproduced in full at the end of this brief. **This round is NARROW: do not re-do the whole analysis. Work only the 6 disputes below.** Round 1 cost both of you a 1800 s timeout and a retry; staying inside the 6 is what keeps this round inside the budget.

Artefacts unchanged from round 1: `bench/falsifier_verify.py`, `bench/key_access_forensics.py`, `bench/reference_runner_v3.py`, and the 2 runs `bench/logs/prose_convergence_run1b_2026-10-02_20261002T044234Z` and `bench/logs/exp48_chemistry_exam_live_20260729T044134Z`.

### WHAT I DID AFTER ROUND 1

I re-executed your corrections on the REAL repository rather than adopting them. 2 of your findings held against me, 1 I could not reproduce, and 1 resolved into a different and larger defect than either of you named.

- **CONFIRMED against me.** The census producer's silent zero. `git ls-files` outside a work tree exits **128** with 0 bytes of stdout, and `scripts/guard_false_positive_blind_spot_2026-10-02.py:206` takes `.stdout.split()` with no returncode check. Both of you caught it independently. It is my defect and your fix is right.
- **CONFIRMED against me.** D2's silent false convergence. `open_crit_high_count`'s non-terminal set is `("OPEN","CONTESTED","REOPENED","CORROBORATED","WITHHELD")` — `UNCONFIRMED` is absent — so with both counters released nothing observes the critical. cc2's framing is the one I accept: the ruling specifies release AND report; D2 specified release and omitted report.
- **COULD NOT REPRODUCE.** You both report Exp 48 totalling **12** CONFIRMED with a second finding **C0017**. On this machine `scan_run` returns exactly **10 CONFIRMED, all C0012**, 0 for C0017.
- **RESOLVED INTO SOMETHING LARGER.** You report run 1b at **114** CONFIRMED / 108 out-of-scope; I measure **89 / 83** here and reproduce it exactly. `key_access_forensics.scan_run` defaults `repo_root` to `Path(__file__).resolve().parents[1]` — the **scanning** checkout, not the run's. Neither of you stated this as the root cause, though cc2 came closest.

## REQUIRED SECTION 2 — Use the harness

Answer by RUNNING, not by describing. Re-execute every figure you quote and say which machine and which checkout you ran it on — that attribution is the subject of dispute 2, so a figure without it is not an answer this round.

**The instrument that bears on this round is `S_k` together with the two-sided gate.** cc2 executed `GATE INPUT INVARIANCE: queue=0 → converged=True, queue=3 → converged=True`, concluding the queue reaches only the halt. **Expected: whichever D2 variant survives must leave both gate conditions and every `S_k` tristate byte-identical. Verify it on the surviving variant, do not carry round 1's verification across.**

## REQUIRED SECTION 3 — Produce a fix, and test it

A finding without a fix is incomplete; a fix without an EXECUTED falsifier is a hypothesis. Report the command and its output.

**Deliver every fix as a FILE written INTO your sandbox tree at its real path.** Prose is not delivery and scratch space is destroyed at teardown.

You are in a sandbox COPY. Do not reach the real repository, do not start an experiment or runner, do not run the full `pytest bench/tests/` suite, and make no paid dispatch.

## REQUIRED SECTION 4 — What would refute you

For each of the 6, state what evidence would overturn your resolution. Where you now agree with the other seat, say what would make you both wrong — agreement between 2 seats is not evidence, and this project does not confirm findings by model vote.

## REQUIRED SECTION 5 — Output shape

For each dispute D1–D6: **RESOLUTION** (one line), **WHO WAS RIGHT** (you / the other seat / CC1 / nobody), **EVIDENCE** (command and output, with the machine named), **FIX** (sandbox file path, or NONE and why), **WHAT WOULD REFUTE THIS**, **CONFIDENCE**.

### THE 6 DISPUTES

**D-1. The Exp 48 total: 10 or 12?** You both say 12 with a C0017. I measure 10, all C0012, on the real checkout. Is C0017 an artefact of scanning from a sandbox whose `repo_root` is not the run's repo? Settle it by running `scan_run` with `repo_root` pinned explicitly to BOTH values and reporting both.

**D-2. Machine dependence.** `repo_root` defaults to the scanning checkout. A forensic scanner whose verdict depends on who runs it cannot source an end-of-run advisory, because "if no key was accessed, say nothing" stops being well defined. Should `scan_run` take the run's own repo from a runner-authored record, and refuse rather than guess when that record is absent? Note fable's Q4 finding that undeclared targets drive most flagged runs — these may be one defect, not two.

**D-3. The D2 mechanism: `integrity_unobserved` (fable) or `integrity_refused` + mandatory record (cc2)?** Read each other's implementation. fable carves out the observer-did-not-install case so a sitecustomize failure cannot drain every critical; cc2 stamps a distinct flag, shares one predicate across both counters, and adds a per-round `KEY-ACCESS ADVISORY` line. Are these the same fix, complementary, or in conflict? Converge only if the evidence converges.

**D-4. Where does the advisory have to land?** cc2 states a residual: its record reaches the round log and `score_exam.py`'s result but NOT `completion_signal.json`, so a reader consuming only the signal sees `status: COMPLETE` with no advisory. fable wired `result["key_access_advisory"]` at finalize. The founder's ruling is "report it at the end of a run". Which surface satisfies that, and is `completion_signal.json` mandatory?

**D-5. The C0015 oracle edit.** You BOTH independently removed C0015 from the expected-rejection set in `bench/tests/test_falsifier_cannot_read_the_key.py`. I verified it: C0015 fires 0 access rules and exactly 1 vocabulary rule, on the literal text `PLANTED false` in its own commentary. I accept the edit. **But state plainly whether this is an amendment to a committed acceptance oracle**, because fable's round-1 summary said no oracle was weakened while the diff removes a member of an expected set. Which is it, and what protects C0012's half from the same reasoning later?

**D-6. The residual neither of you closed.** fable names a ladder-side path where an integrity refusal leaves the entry labelled UNTOOLABLE/ERROR and still counts as deferred — run 1b's C0029 did exactly this. Does cc2's shared-predicate fix cover it? If not, what does?

## REQUIRED SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings on these 6, and say how many passes you ran. A finding is above threshold if missing it could cause a false experimental result, an unsafe condition, or a real-world failure. **Preserve disagreement.** If after reading the other seat you still disagree, say so and show why — a convergence produced by deference is worth less than a stated split.

---

# ROUND 1, SEAT cc2 (opus), VERBATIM

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

---

# ROUND 1, SEAT fable, VERBATIM

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

## Seat: cc2

Route `claude_cli`, 68 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel integrity_advisory_r2_2026-10-02) -->

---

# Panel round 2 — the 6 disputes, settled by execution

**Machine:** `Mac-mini.local` (Darwin arm64, Python 3.13.3). **Checkout:** sandbox copy at `/private/var/folders/cc/scptwd_s4cgclnjn5937fyjw0000gn/T/cdsfl_panel_7tfq53x8/repo`, no `.git`. Every figure below was re-executed here. Wolfram: available, used once as second falsifier, it computed (exit 0, `Out` value, no `Name::tag`).

**The headline inverts the brief.** Both of your hypotheses about the cause are refuted, and your own 10 is the artefact.

`repo_root` is not the variable. Pinned to both checkouts, `scan_run` returns **byte-identical hit sets** on both runs. The variable is `_in_scope`'s prefix clause: `a.startswith(target)` was written for display truncation, but an **ancestor directory is also a prefix**. On the machine that ran the experiment, the run directory sits inside the repository, inside `$HOME` — so the repository root, `/Users/georgejackson` and `/Users` were all reported IN SCOPE. C0017's literal *is* the bare repository root. That is 10-vs-12 and 89-vs-114, one clause, both disputes.

It is also a hole, not only a precision defect: **`os.listdir("/Users/georgejackson")` — the listing that discovers the vault name `vault_keys.sh` deliberately hides under `$HOME` — was in scope on your machine**, and `print_report` exited 0.

---

## D-1. The Exp 48 total: 10 or 12?

**RESOLUTION:** **12.** Ten was a reading available only where the run directory sits inside the repository; post-fix the scan returns 12 at every `repo_root`, including yours.

**WHO WAS RIGHT:** Both seats on the number; **nobody** on the mechanism — your `repo_root` hypothesis is refuted, and neither seat named the ancestry clause.

**EVIDENCE** (sandbox named above):

```
exp48  target_dirs = ['/Users/georgejackson/CDSFL_review_targets']
  repo_root=SANDBOX  repo_in_scope=False CONFIRMED=12  {'C0012': 10, 'C0017': 2}
  repo_root=REAL     repo_in_scope=False CONFIRMED=12  {'C0012': 10, 'C0017': 2}
     files=87 bytes=4068509 unreadable=0   (identical hit lists, not just counts)
```

`repo_root` cannot move a hit: both runs are `confined=True`, and a confined scan never puts `repo_root` on the allowlist. Simulating **your run directory's location** instead reproduces your number exactly:

```
exp48 out-of-scope literals, allowlist = [run_dir, staged target]
  run_dir = sandbox path : 2   {'/Users/georgejackson/Developer_Projects/Constraint_Engineering': 2}
  run_dir = YOUR path    : 0   {}        <- 12 becomes 10
C0017 hit: out-of-scope path opened or listed | exp48_chemistry_exam_live_report.json
  /registry/entries/C0017/falsifier_code
  snippet: REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")
```

Post-fix, pinned at three values: `{'C0012': 10, 'C0017': 2}` each time.

This is a **class this repository already named**. `scan_falsifier_source(C0017)` returns exactly one rule, `'a path outside the declared target'` — the same location-artefact class documented at `test_falsifier_cannot_read_the_key.py` (A2, 2026-09-10: *"On the maintainer's machine that path IS the repository root, so it never fires; in any other checkout it does"*). The gate got a classifier for it. The forensic scanner never did.

**FIX:** `bench/key_access_forensics.py` (`_is_ancestor_dir`, `_in_scope`); `bench/tests/test_scanner_machine_independence_2026-10-02.py`.

**WHAT WOULD REFUTE THIS:** a third reading of Exp 48 on either machine post-fix; or a `scan_run` call where pinning `repo_root` *does* move an Exp 48 hit — which would mean the brief's account was right after all and mine is wrong. Both are one command. **What would make both seats wrong together:** if C0017's falsifier legitimately named that path as a *declared* target, in which case the right fix is the target record, not the scope clause. It does not — `discover_target_dirs` returns the confined `CDSFL_review_targets`.

**CONFIDENCE:** High. Hit lists compared, not counts; anti-vacuity control reproduces the 10.

---

## D-2. Machine dependence

**RESOLUTION:** Confirmed, larger than stated, and **not** caused by `repo_root`. `scan_run` **should** take the run's own repo — and **the record already exists and was simply never read**. Refusing when it is absent is wrong, and I have the measurement.

**WHO WAS RIGHT:** You on the symptom. **Nobody** on the cause or the remedy. Both seats' fixes *preserve* the dependence — I executed both.

**EVIDENCE.** Your 89/83 reproduced from this sandbox by relocating the run directory alone:

```
run1b target_dirs = ['bench']   (repo-RELATIVE)
  out-of-scope, run_dir = sandbox : 108        total CONFIRMED 114
  out-of-scope, run_dir = YOUR path:  83        total CONFIRMED  89   delta = 25
  the 25 that flip: 25x '/Users/georgejackson/Developer_Projects/Constraint_Engineering'
```

The ancestry hole, at its worst case:

```
ANCESTOR-ADMISSION PROBE (allowlist = your run dir + staged target)
  in_scope=True   /Users
  in_scope=True   /Users/georgejackson          <- the vault's parent
  in_scope=True   .../Constraint_Engineering
  in_scope=False  /Users/georgejackson/CDSFL_exam_keys   (only when --key-dir is set)
```

**Both round-1 fixes are machine-dependent.** Executed against the harvested modules in `bench/logs/integrity_advisory_2026-10-02/sandbox_harvest/`:

```
fable  run1b  repo_root=sandbox CONFIRMED=107 advisory=FIRES
       run1b  repo_root=REAL    CONFIRMED=  0 advisory=SILENT
cc2    run1b  repo_root=sandbox CONFIRMED=114 advisory=FIRES
       run1b  repo_root=REAL    CONFIRMED=  7 advisory=SILENT
```

Normalising the relative target does not remove the dependence — it *moves it onto `repo_root`*, where it becomes the whole verdict. Each seat's reported figure holds only on your machine.

**The record you asked for already exists.** `reference_runner_v3` has written `panel_confinement.run_root` since 2026-09-01. Census: **19 of 86** archived run dirs carry it (22.1%) — **including run 1b**, naming your checkout. `scan_run` ignored it for `Path(__file__).parents[1]`.

```
POST-FIX, this sandbox:
  run1b  run_repo_root(record) = /Users/georgejackson/Developer_Projects/Constraint_Engineering
    default (record)  assumed=False in_scope=True  CONFIRMED=  7
    pinned REAL       assumed=False in_scope=True  CONFIRMED=  7
  exp48  record = None
    default / SANDBOX / REAL        CONFIRMED= 12 every time
```

**Refuse when absent? No — measured.** 67 of 86 runs carry no record; a hard refusal disables the scanner on **77.9%** of the archive to gain a property, with nothing dominating it on a named measure. Instead the guess is made visible: `repo_root_assumed` on the `Report`, printed by `print_report`, and the advisory states the scan is not portable. Archive-wide, 86 run dirs:

```
PRE-FIX  (ancestry on, __file__)  runs firing=31/86  total CONFIRMED=1060
POST-FIX (ancestry off, record)   runs firing=29/86  total CONFIRMED= 926
runs with MORE hits after: 0      NEWLY FIRING (0 -> >0): 0
NEWLY SILENT: 2  (sim45_memory x2) — inspected: 27 hits, all `REPO = Path(...)`
                 honest reads of the repo under review; no key-material label
PRE  36.0465% Wilson95 [26.6970%, 46.5893%]
POST 33.7209% Wilson95 [24.6165%, 44.2174%]   exact McNemar b=0 c=2, p=0.5
```

Wolfram second falsifier agrees to 13 significant figures: `{33.7209302325581395, 24.61654857757776, 44.2174392410278}` — *computed with Wolfram Language (local Wolfram Engine via `wolframscript`)*. **I will not claim a precision win from 31→29: p=0.5.** The gain is 134 fewer hits and portability, not the run-level rate.

**One defect or two?** fable's Q4 is a **sibling, not the same**: 33 of 86 runs declare no target at all, so `bool(rep.target_dirs)` is False, `confined` is False, and the repo is *always* in scope. Different branch, opposite direction. Not fixed here; named.

**FIX:** `bench/key_access_forensics.py` (`RUN_ROOT_RECORD`, `_runner_authored_records`, `run_repo_root`, `Report.repo_root_used/_assumed`, `scan_run` root + relative-target resolution, `print_report` provenance); `bench/tests/test_scanner_machine_independence_2026-10-02.py`.

**WHAT WOULD REFUTE THIS:** a run whose recorded `run_root` is wrong — written by a runner in a worktree whose root is not the repo the paths resolve against. `is_sandbox_worktree` sits beside it and I did **not** consult it; that is the weakest line in my fix. Also: my own test `test_a_wrong_explicit_repo_root_still_changes_the_answer` pins that an explicit wrong root restores 114. The record removes the guess, not the dependence.

**CONFIDENCE:** High on the cause and the measurement. Medium on the record's trustworthiness across worktrees.

---

## D-3. `integrity_unobserved` or `integrity_refused` + record?

**RESOLUTION:** **Complementary. Each alone is unsafe, in opposite directions, and I executed both failures.** Not the same fix, not in conflict.

**WHO WAS RIGHT:** Both, half each. Neither alone.

**EVIDENCE** (harvested sources, same sandbox):

```
cc2  "observer did not install" / integrity_unobserved occurrences: 0
```

cc2's exclusion fires on the verdict string alone. `reverify_falsifier` also returns `INTEGRITY_VIOLATION` when the observer never installed — machine-wide when it happens. Every critical releases from both counters and the run converges with nothing tested. fable's carve-out is load-bearing.

```
fable  integrity_refused_criticals: absent.  Reporting channel = end_of_run_advisory
fable  run1b  repo_root=REAL  CONFIRMED=0  advisory=SILENT
```

fable's channel is **not coupled to the exclusion it authorises**. Run 1b's 10 gate refusals were all *vocabulary* matches on `seeded_fault`; the artefact scan finds no access, the advisory returns `None`, and the excused critical is reported nowhere. cc2's paired record is load-bearing.

**And a third defect neither seat has.** cc2's record gates `severity >= 0.7` while the counter it shadows stopped gating on severity on 2026-09-06 (AUC 0.464). Executed:

```
severity=0.5, UNCONFIRMED, refused:
  control unverified_critical_count() == 1     (A4 does count it)
  with refusal                       == 0     (released)
  cc2-shape record (severity >= 0.7) == []    (silent)
```

That is the silent false convergence, reachable with no severity editing at all. My record has **no severity gate**.

**FIX:** `bench/reference_runner_v3.py` — `_integrity_refused` (cause carve-out + both verdict fields), `INTEGRITY_REFUSED_VERDICT`, `LADDER_VERDICT_FIELD`, skips in `_irreducible_queue_split` and `unverified_critical_count`, `FindingRegistry.integrity_refused_criticals()`, cause stamp at the reverify site. Tests: `bench/tests/test_integrity_refusal_composition_2026-10-02.py` — **9 passed**, each with an anti-vacuity control.

**WHAT WOULD REFUTE THIS:** a registry state where an entry is released by both counters and absent from `integrity_refused_criticals()`. I removed the severity gate and the terminal-status filter is the only remaining narrowing — and it is correct (an adjudicated finding is not outstanding). The construct that would break me: a refusal on an entry whose status is driven terminal *by the refusal itself*. I did not find one. **What would make both seats wrong together:** if `INTEGRITY_VIOLATION` has a fourth return site neither of us enumerated — fable says four, cc2 does not count them, and I did not verify the count.

**CONFIDENCE:** High on complementarity (both failures executed). Medium on completeness of the cause enumeration.

---

## D-4. Where does the advisory have to land?

**RESOLUTION:** Two different things are being conflated. The **forensics advisory** (evidence about artefacts) belongs on the report — fable's `result["key_access_advisory"]` satisfies the ruling. The **`integrity_refused` record** (the thing that changed the convergence decision) must sit on the same artefact that asserts the decision. `completion_signal.json` is where "clean convergence" is reported, so the qualification belongs there. **Mandatory for the record, not for the advisory.**

**WHO WAS RIGHT:** cc2, on identifying the residual. Neither closed it, and neither did I.

**EVIDENCE.** `signal_complete` (`bench/insect_brain.py:1387`) writes the only artefact whose top-level field is `status`, over its own state object — it cannot see `FindingRegistry`. It is in the scanner's own `RUNNER_AUTHORED` tuple and `seal_experiment_logs.py` treats it as the experiment checkpoint. And the release removes the *last* trace from the gate's own output:

```
GATE INPUT INVARIANCE, converging case (round 3, history [0,0,0,0], gamma 0.336):
  queue= 0 -> (True, 'CRITICAL_QUIESCENCE_CONVERGED (two-sided gate) ...')
  queue= 3 -> (True, '... [NOTE: irreducible queue 3 > bound 2 ...]')
  converged identical across queue: True
  FULL RETURN byte-identical across queue: FALSE
  gamma swept 0.05/0.10/0.29/0.30/0.336/0.50 — decision moved at 0 of 6
```

**I correct cc2 here.** cc2 reported the queue reaches "a NOTE string only" and verified `converged=True` at two queue values. There is a real branch, `if irreducible_queue > cfg.max_irreducible_queue`. **Both gate *conditions* are byte-identical** — the boolean and both named sub-conditions, at every gamma swept. The **reason string is not**: the NOTE appears when the queue exceeds the bound. My patch lowers the queue, so it can only *remove* that NOTE, never add one — which is precisely why the record must exist elsewhere.

`S_k` tristate, run 1b, from the archived report: **30 NO_SCORE / 6 REJECTED over 36 `sk_result` records**. (I do not reproduce cc2's 43/7 over 50 from the report alone — a scope difference, below threshold, flagged.) Invariance verified on *my* variant, not carried across: **0 `sk_` tokens in every inserted region**, and 95 S_k tests pass.

**FIX: NONE, and I am saying so rather than implying it.** Threading `integrity_refused_criticals()` into `signal_complete` crosses from `FindingRegistry` into `insect_brain`'s state object, and I will not ship that without the full suite I am forbidden to run. **This is the first thing to close.** Shipping the release without it means an artefact that says `status: CONVERGED` over an untested critical with the gate's own NOTE now suppressed.

**WHAT WOULD REFUTE THIS:** a committed reader that consumes `completion_signal.json` and nothing else. I did not enumerate the consumers, so "a reader sees COMPLETE with no advisory" is a property of the artefact, not a demonstrated harm. If every consumer reads the report too, this drops below threshold.

**CONFIDENCE:** High that the surface is missing. Medium that it matters, bounded by the unenumerated readers.

---

## D-5. The C0015 oracle edit

**RESOLUTION:** **It is an amendment to a committed acceptance oracle — plainly, and there are TWO of them, not one.** Neither is a *weakening*. fable's summary is literally true and materially misleading.

**WHO WAS RIGHT:** You, to insist on the distinction. fable's phrasing conceals a second edit.

**EVIDENCE.** The rule census, this sandbox:

```
C0012  4 rules: answer-key path | ["planted_false"] subscript | claims->truth | outside declared target
       + 2 vocabulary
C0015  1 rule : plant vocabulary — matched text 'PLANTED false'
```

Your verification reproduces. But the oracle's docstring is not a defect pin — it is a measured false-positive census that names C0015 as legitimate (*"a falsifier from the same contaminated run whose own text asserts which claim was planted"*) and says *"If a future rule change makes this fail, the rule is blocking honest work."* Removing a member is an amendment to that.

The diff shows a **second** edit fable's summary does not mention:

```
-    assert any("plant" in r or "seed" in r for r in reasons)
+    assert any("subscripted" in r for r in reasons)
```

That removes the requirement that a plant-vocabulary rule fire on the real exploit. Classification: **both are amendments; neither is a weakening.** The `expected` assertion is set *equality*, so dropping a member tightens one direction (C0015 must now **not** be refused) and loosens none. The second substitutes an access-class requirement for a vocabulary-class one, with `>= 3` unchanged — and the substitute is the stronger kind, since access is what stops a read.

**What protects C0012's half:** `expected == {C0012}` is still equality, so un-refusing C0012 makes `rejected` empty and fails. The weak point is the *named classes* in `test_the_real_exp48_c0012_exploit_is_refused` — three separate assertions, each individually amendable by exactly the reasoning fable used. That is the gap, and it is the real answer to your question.

**FIX:** I did **not** edit the oracle. D1's access-only split is not applied in my tree, so C0015 is still refused here and removing it would make the test fail — the edit is only correct *paired with* D1. The structural protection is deliverable now and is what I shipped: the anti-vacuity controls in `bench/tests/test_scanner_machine_independence_2026-10-02.py` and `bench/tests/test_integrity_refusal_composition_2026-10-02.py`, both of which restore the pre-fix state and assert the defect returns. The missing piece — a pin that C0012's refusal must come from **access-class** rules regardless of which regex names them — I name and did not ship.

**WHAT WOULD REFUTE THIS:** a documented prior decision classifying C0015's refusal as a known defect rather than correct behaviour. I searched the file and found the opposite. **What would make all three of us wrong:** if C0015's `PLANTED false` commentary is itself inherited leaked knowledge — then refusing it is correct and the amendment is a weakening after all. The founder's own note says C0015 came "from the same contaminated run". I did not read C0015's body to settle it, and **that is the single most likely place this answer is wrong.**

**CONFIDENCE:** High on the classification. **Medium-low** on whether the amendment is right, for the reason just stated.

---

## D-6. The residual neither of you closed

**RESOLUTION:** **No, cc2's shared predicate does not cover it — and neither does fable's.** The field is `routing_verdict_unreconciled`, and both predicates read `falsifier_verdict` only.

**WHO WAS RIGHT:** fable, for naming the residual. Neither seat's code closes it.

**EVIDENCE.** Run 1b's C0029, verbatim from its report:

```
C0029 {'status':'CLOSED', 'severity':0.8, 'falsifier_verdict':'CONFIRMED',
       'routing_deferred':True, 'verdicts':[],
       'routing_verdict_unreconciled':'INTEGRITY_VIOLATION'}
```

Set at `reference_runner_v3.py:6196` by the `UNTOOLABLE->ERROR` reconciler: a rung whose verdict is neither resolved nor `ERROR` is recorded **only** there. The entry keeps its own label, stays `routing_deferred=True`, passes `_irreducible_queue_split`'s severity test, and feeds the halt bound. `grep -c routing_verdict_unreconciled` is 1 in each seat's harvested runner — the setter, never a reader.

Post-fix, executed:

```
test_a_ladder_side_refusal_is_covered_too        _integrity_refused(C0029) is True
                                                 _irreducible_queue_split -> (0, 0)
                                                 record -> ['C0029']
test_reading_only_the_entry_verdict_misses_it    entry-verdict-only predicate -> False
```

**FIX:** `LADDER_VERDICT_FIELD` + the two-field loop in `_integrity_refused`, `bench/reference_runner_v3.py`; both tests above.

**WHAT WOULD REFUTE THIS:** a third landing site. `routing_verdict_reconciled` exists beside it and I did **not** check whether a refusal can reach it. Also: treating a ladder-side refusal exactly like an entry-side one releases an entry that may *also* be genuinely ladder-exhausted — there the instrument really did fail, which per `EQUIPMENT_FAILURE_VERDICTS` should keep blocking. **My patch cannot distinguish those two, and that is a release I widened beyond what either seat authorised.** Evidence that a ladder-side refusal coexists with a genuine exhaustion would refute me and argue for report-only treatment on that path.

**CONFIDENCE:** High that neither seat covers it. **Medium-low on my fix** — I may have widened the release too far, and I would not ship this half without the founder's ruling.

---

## Files delivered (sandbox tree, real paths)

| path | change |
|---|---|
| `bench/key_access_forensics.py` | `_is_ancestor_dir` + `_in_scope` ancestry fix; `RUN_ROOT_RECORD`, `_runner_authored_records`, `run_repo_root`; `Report.repo_root_used` / `.repo_root_assumed`; `scan_run` prefers the run's own record and resolves repo-relative targets against it; `print_report` prints the provenance and warns when assumed |
| `bench/reference_runner_v3.py` | `INTEGRITY_REFUSED_VERDICT`, `LADDER_VERDICT_FIELD`, `_integrity_refused` (fable's carve-out + cc2's flag + the ladder field); skips in `_irreducible_queue_split` and `unverified_critical_count`; `FindingRegistry.integrity_refused_criticals()` **without** the severity gate; cause stamp at the reverify site |
| `bench/tests/test_scanner_machine_independence_2026-10-02.py` | **new**, 10 tests, 2 anti-vacuity controls, both archived runs |
| `bench/tests/test_integrity_refusal_composition_2026-10-02.py` | **new**, 9 tests, every release paired with a control |

```
$ python3 -m pytest <the 2 new files + 9 related suites> -q
223 passed in 27.34s
$ python3 bench/key_access_forensics.py bench/logs/prose_convergence_run1b_...
  repo root : /Users/georgejackson/Developer_Projects/Constraint_Engineering  (from the run's own record)
```

No full suite, no experiment, no runner, no paid dispatch. I read the harvested round-1 implementations at `bench/logs/integrity_advisory_2026-10-02/sandbox_harvest/` — that is the brief's own instruction for D3; I did not read `cc2.json`/`fable.json`, `seat_proposals.diff`, or any scoring material.

---

## Termination — 4 passes

(1) Pinned `repo_root` both ways, found it irrelevant, found the ancestry clause. (2) Confirmed the hole at `/Users/georgejackson`, read the archive for the `run_root` record, measured the before/after. (3) Executed both seats' harvested code: both machine-dependent, cc2 missing the carve-out, fable's channel decoupled, cc2's record narrower than its release. (4) Composed and tested; gate and `S_k` re-verified on **my** variant; found the reason-string non-identity and the C0015 second edit. Pass 4 produced no new above-threshold finding on these 6, which is why I stop. It is not a claim that pass 5 would be empty: D4's `completion_signal.json` and fable's undeclared-target class are open, measured, and unfixed.

**Disagreements preserved.**

- **With you, twice.** `repo_root` is not the cause; and your 10 is the artefact, not our 12.
- **With cc2.** The queue reaches a real branch, not "a NOTE string only"; the gate's *conditions* are invariant, its *return value* is not. cc2's record gates on severity while the counter it shadows does not — a silent release at severity 0.5, executed. cc2's 43/7 S_k census does not reproduce from the report (I get 30/6 over 36).
- **With fable.** "None weakens an acceptance oracle" is true and conceals a second amendment to the same file. fable's reporting channel is silent in exactly run 1b's case, which is the case the ruling was written for. fable's 0-CONFIRMED/SILENT figure holds only on your machine.
- **Against myself.** My own test caught me asserting post-fix `repo_root` invariance that my own fix had just destroyed; I rewrote the claim as the pre-fix fact it actually is. And my D6 release is wider than either seat authorised — I would hold that half pending your ruling.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 59 recorded tool call(s).

<!-- verbatim-begin: fable (panel integrity_advisory_r2_2026-10-02) -->

All verification complete. Final report.

---

# ROUND 2 VERDICT — seat fable

**Machine attribution for every figure below:** host `Mac-mini.local` (home `/Users/georgejackson`), sandbox checkout `/private/var/folders/cc/.../cdsfl_panel_efceg5bo/repo` (no `.git`), Python 3 via `python3`. Where a pin to the canonical checkout matters I passed `repo_root=/Users/georgejackson/Developer_Projects/Constraint_Engineering` **as a string parameter only** — nothing under that path was read. This sandbox arrived **fresh**: none of my round-1 edits were present, so every fix below was re-established and re-executed here.

**Headline: 5 of the 6 resolutions land, and one of CC1's — D-1's mechanism — is wrong in a way that matters: C0017 is not a sandbox artefact; the canonical checkout's 10 is the false negative.** The design survives all 6 with the fixes delivered below. 283 tests pass across the targeted battery (207 + 69 + 7 new forensics tests included in those counts).

---

## D-1. Exp 48: 10 or 12?

**RESOLUTION:** **12.** C0017 is real and must stay flagged. The canonical checkout's 10 is a **false negative produced by `_in_scope`'s truncation shortcut**, not a sandbox artefact — and `repo_root` was never the mechanism.

**WHO WAS RIGHT:** Both seats on the figure; **nobody** on the mechanism, CC1 closest to naming machine dependence but wrong about its channel.

**EVIDENCE** (this sandbox): I ran `scan_run` with `repo_root` pinned to the sandbox, to the canonical path, and defaulted — **all three return 12 CONFIRMED {C0012: 10, C0017: 2}**, `repo_in_scope=False`. So pinning `repo_root` cannot produce CC1's 10. The actual channel is the `run_dir` allowlist entry: `_in_scope` accepted `a.startswith(target)` ("truncation of an allowed root"), and on the canonical checkout the run directory sits **inside** the repository, so the C0017 literal — exactly the repo root — is an *ancestor* of the run_dir allowlist entry. Executed:

```
C0017 literal in scope on REAL checkout?  True      ← reproduces CC1's 10
C0017 literal in scope in SANDBOX?        False     ← our 12
HOME itself in scope given a target dir?  True      ← the generalisation: `ls $HOME` passed everywhere
```

C0017's falsifier does `REPO = Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")` then reads `bench/cdsfl_registry/targets/exp48_chemistry.md` — a confined exam panel pulling the target out of the repository, the precise route the 2026-07-29 confinement comment exists for. The suppression is worse than C0017: `$HOME` and every ancestor of any allowlist entry scored in scope **on every machine**.

**FIX:** `bench/key_access_forensics.py` — the shortcut now requires the continuation to begin mid-component (`not a[len(target):].startswith(("/", "\\"))`): a path cut by a display limit keeps its carve-out; a complete ancestor directory does not. Post-fix, executed: exp48 = **12 under both pins**; the real-checkout suppression gone; genuine truncation and elision still in scope. Pinned by `bench/tests/test_forensics_machine_independence_2026-10-02.py` (`test_exp48_total_is_12_under_both_repo_root_pins`, `test_truncation_shortcut_no_longer_scores_ancestors_in_scope`) — 7 passed.

**WHAT WOULD REFUTE THIS:** an artefact diff showing the canonical run directory contains files this sandbox copy lacks (CC1 can check in one command: my claim predicts the canonical 10 flips to 12 after this one-line fix, with **no other change**). If it doesn't flip, my mechanism is wrong.

**CONFIDENCE:** High — the mechanism is executed in both directions, and it predicts both seats' 12 and CC1's 10 from one line.

## D-2. Machine dependence of `repo_root`

**RESOLUTION:** **Yes — record-or-refuse.** `scan_run` now resolves the run's own repo from a runner-authored record (`repo_root` in `completion_signal.json`, which the runner now writes at finalize), then from an explicit argument, and otherwise **raises `RepoRootUnresolved`** — never guesses from `__file__`.

**WHO WAS RIGHT:** CC1 on the root cause (neither seat stated it in round 1; cc2 came closest). On "one defect or two" with my Q4: **one class, two records.** Both are "scanner scope inputs not sourced from runner-authored records" — `repo_root` (fixed here) and `target_file` (requires runner-side recording at dispatch; still flagged for the founder, not silently absorbed).

**EVIDENCE** (this sandbox): archived exp48 with no record → `REFUSED: ... no 'repo_root' in any runner-authored record ... refusing to substitute the scanning checkout`, CLI exit 2. Run 1b with the run's own repo pinned: **7 CONFIRMED** (all in `panel_worktree_harvest/files/bench/falsifier_verify.py`, quoting its own fixtures — the round-1 D3 residual, carried not hidden); mis-pinned to the sandbox: **114**. The mispin inflation is 107/114 = **93.8596%**, Wilson [87.8657%, 96.9941%] (statsmodels; second-checked, agreeing to 4+ decimals, computed with Wolfram Language, local Wolfram Engine via wolframscript). This confirms CC1's 89-vs-114 class exactly: the verdict was a function of the scanning machine. Also run 1b's relative `'bench'` target now resolves against the run's repo → `repo_in_scope=True`, killing the confined-exam misclassification.

**FIX:** `bench/key_access_forensics.py` (`RepoRootUnresolved`, `resolve_run_repo_root`, resolution order, relative-target normalisation, CLI refusal); `bench/reference_runner_v3.py` + `bench/insect_brain.py` (runner writes `repo_root` into `completion_signal.json` via `signal_complete(extras=...)`). `bench/score_exam.py` needs **no edit**: its existing `except Exception` already converts the refusal to "UNVERIFIED, not as clean" — refusal to score, loudly. **Declared oracle-adjacent amendment:** `bench/tests/test_key_access_forensics.py`'s `_run_dir` fixture now writes the record a real run carries (dated comment in file; **no assertion changed**), plus one explicit `repo_root=` in the displaced-signal parametrization. Full suite: 26 passed.

**WHAT WOULD REFUTE THIS:** a legitimate consumer that must scan record-less archived runs unattended — the refusal would then convert silent wrongness into operational breakage with no escape hatch. (The hatch is `--repo-root`; if a caller exists that cannot supply it, this design fails.)

**CONFIDENCE:** High on mechanism and direction; medium on the fixture amendment being the founder's preferred shape.

## D-3. `integrity_unobserved` vs `integrity_refused` + mandatory record

**RESOLUTION:** **Complementary, with one genuine conflict — and the evidence decides it.** cc2's release-all-IV conflicts with my carve-out at exactly one class: observer-did-not-install. Releasing that class lets a machine-wide sitecustomize failure drain every critical out of A4 — a silent false convergence on a run with no sandbox boundary. The surviving variant is the synthesis: **cc2's shared predicate + distinct flag + mandatory record + per-round advisory, with my unobserved carve-out kept blocking**, and the classifier's fail-safe default is *block* (release requires evidence).

**WHO WAS RIGHT:** Both, on different halves. I concede CC1's framing against my round 1: I specified release and under-specified the report; cc2's "release AND report" is the ruling's shape. cc2 concedes nothing on the carve-out — reading `reverify_falsifier` here confirms the four IV sites, and site 2 ("observer trace absent") is equipment, not key access.

**EVIDENCE:** implemented and executed in this sandbox. `_integrity_released` is **one predicate, three readers** (`_irreducible_queue_split`, `unverified_critical_count`, the halt alarm's evidence collector — cc2's round-1 fix missed the third; a queue of released items would have halted and then *described nothing*). Executed: key-access refusal → A4 0, queue 0, record non-empty; unobserved → A4 1, queue 1, record empty; no flag → blocks (the non-vacuous control); classifier defaults to block on an empty/missing rejection record. Record is deliberately **not severity-gated** — closing cc2's own self-named weakest line (the AUC-0.464 float can no longer hide the record). 17 tests in `bench/tests/test_integrity_release_and_report_2026-10-02.py`, all passing, plus the committed S_k-consumer guard (62 passed together).

**FIX:** `bench/reference_runner_v3.py` — `INTEGRITY_REFUSED_VERDICT` (pinned to the gate by test, in neither fault set), `_classify_integrity_refusal`, `_stamp_integrity_refusal`, `_integrity_released`, stamps at the entry-verdict landing site and in `_apply_routing`, a new `elif` so a refusal can never be stamped `irreducible_escalation` ("a machine tried and could not" is false — it was not permitted to try; run 1b's C0035), `FindingRegistry.integrity_refused_criticals()`, per-round `KEY-ACCESS ADVISORY` log line.

**WHAT WOULD REFUTE THIS (both of us):** an IV rejection whose record text matches neither the unobserved markers nor any key-access rule — my classifier blocks it forever (fail-safe, but a *mislabelled genuine key-access refusal* would then re-create the block-to-round-cap shape the ruling forbids). The classifier keys on prose markers in `_announce_rejection` records, which is a string coupling; a reworded rejection message flips classification silently. A structured `kind` field written at the rejection site would be sturdier — named, not built, within this round's budget.

**CONFIDENCE:** High on the synthesis and on the carve-out; medium on marker-string robustness.

## D-4. Where must the advisory land?

**RESOLUTION:** **`completion_signal.json` is mandatory.** The advisory must land **where the status lands**: the signal is the one artefact whose `status` a downstream reader consumes alone, and it is in the scanner's own `RUNNER_AUTHORED` trust set. The round log (when) and the report (full detail) are complementary, not sufficient — cc2 named this residual itself, and CC1's question answers itself through the false-pair construction: `status: COMPLETE` readable without the advisory is exactly the silent pass D2-b.

**WHO WAS RIGHT:** cc2 on identifying the gap; neither seat had closed it.

**EVIDENCE/FIX:** `signal_complete(extras=None)` in `bench/insect_brain.py` (signal's own fields win — extras **cannot overwrite `status`**, executed: a forged `status` in extras is discarded); runner finalize passes `{"repo_root": ..., "key_access_advisory": [...] }`, the advisory also mirrored into `result`. Executed: `test_completion_signal_carries_advisory_and_repo_root` and the no-extras control both pass.

**WHAT WOULD REFUTE THIS:** a committed downstream consumer that validates `completion_signal.json` against a closed schema and rejects unknown keys — the extras would then fail a run at finalize. I found no such validator, but I did not sweep every consumer.

**CONFIDENCE:** High.

## D-5. The C0015 oracle edit

**RESOLUTION:** **It IS an amendment to a committed acceptance oracle**, and my round-1 summary's "none weakens an acceptance oracle" was wrong *as phrased*. Removing a member from an expected-rejection set weakens the oracle by definition; the defensible claim was narrower — the amendment is evidenced (C0015 fires 0 access rules, 1 vocabulary rule on its own commentary) and openly declared. Evidence and declaration make an amendment legitimate; they do not make it not-an-amendment. I state the concession plainly.

**WHO WAS RIGHT:** CC1 to force the classification; both seats right on the substance of the edit.

**FIX (what protects C0012's half):** the **criterion, committed, not the list** — `test_c0012_refusal_is_access_not_vocabulary` in `bench/tests/test_forensics_machine_independence_2026-10-02.py` runs the archived C0012 exploit through the live gate and asserts **≥3 distinct ACCESS-class refusals** (answer-key path, key-field subscript, claims→truth). Executed: passes. The C0015 amendment's entire justification was "0 access rules fired"; that reasoning now has a committed boundary it can never cross, because any future edit that leaves C0012 refused by fewer than 3 access rules fails this test before any expected-set edit is even proposed. (Note: in this fresh sandbox the round-1 vocab/access split is absent, so I did **not** re-apply the C0015 set-edit alone — without the split it would turn a passing oracle red. The guard test is split-independent and protects C0012 under either gate.)

**WHAT WOULD REFUTE THIS:** demonstration that C0012's access-rule hits are themselves fixture-dependent (e.g. the archived falsifier body drifting in the errata) — the test pins against the live archived report, so artefact drift would surface as a guard failure, which is the designed direction.

**CONFIDENCE:** High.

## D-6. The ladder-side residual (C0029)

**RESOLUTION:** **cc2's shared-predicate fix does NOT cover it, and neither did mine.** Both round-1 fixes key on the **entry's** verdict; a rung refusal leaves the entry labelled UNTOOLABLE/ERROR and `route()` persists `INTEGRITY_VIOLATION` only into `routing_history` — which I verified is exactly run 1b's archived state: `C0029 | verdict CONFIRMED (post-sweep) | routing_deferred=True | rung verdicts ['INTEGRITY_VIOLATION']` (and C0035 likewise carries the rung IV). What covers it: **stamp at the rung site**, where `result.verdict` and the rejection record are both live, feeding the same shared predicate.

**WHO WAS RIGHT:** Me on naming the residual; cc2's architecture is still the right carrier — the fix is an extension of cc2's predicate, not a replacement.

**EVIDENCE/FIX:** `_apply_routing` now stamps `_stamp_integrity_refusal(e, round_idx, "routing_rung")` when `result.verdict == INTEGRITY_VIOLATION and not result.resolved`, with the same unobserved carve-out. Executed replay from run 1b's own record (`test_d6_rung_refusal_shape_from_run1b_is_released_once_stamped`): the C0029 halt-round shape counts **1** in the queue pre-stamp, **0** post-stamp, and appears in the mandatory record. Passes.

**Named residual, carried not hidden:** `route()` keeps only the **last** rung's verdict. A rung IV followed by a later rung returning CONFIRMED or ERROR is not stamped and does not reach the advisory — the refusal survives only in `INTEGRITY_REJECTIONS` and stderr. Closing it needs `route()` to accumulate per-rung verdicts (it already accumulates `rungs_tried`); one field, flagged for the next round.

**WHAT WOULD REFUTE THIS:** a registry state where a rung-refused critical still blocks or still halts after the stamp — I tried to construct one; the shared predicate plus the collector skip makes it unconstructible through these counters. The construct that survives is the multi-rung shadowing above, which I name rather than claim away.

**CONFIDENCE:** High for single-rung (executed); medium overall because of the shadowing residual.

---

## REQUIRED SECTION 2 — the harness, on the surviving variant

Verified **on the surviving variant in this sandbox**, not carried from round 1: `_check_gamma_alt_convergence` with run 1b's own figures (γ_crit 0.336, γ 0.432) at `irreducible_queue=0` and `=3` returns **identical, both `converged=True`** (`test_gate_input_invariance_queue_reaches_only_the_halt`), and the A4 side still blocks with `unresolved_critical=1` (the non-vacuity control). **S_k:** every new function's source contains no `sk_` token (inspection test — which caught my own first docstring and the committed consumer-guard would have too), and run 1b's archived tristate census is pinned: **{NO_SCORE: 30, REJECTED: 6, (none): 4} over 40 entries** on this machine. Note a figure dispute preserved: cc2's round-1 "43 NO_SCORE / 7 REJECTED over 50 decisions" does not match the final `runner_state.json` registry here — likely a different denominator (per-decision vs per-entry); mine travels with its producer above.

## Files delivered (sandbox tree, real paths)

| path | change |
|---|---|
| `bench/key_access_forensics.py` | D-1 ancestor/truncation fix; D-2 `RepoRootUnresolved` + `resolve_run_repo_root` + record-or-refuse + relative-target normalisation + CLI refusal |
| `bench/reference_runner_v3.py` | D-3/D-6 synthesis: constant, classifier (fail-safe: block), stamps at entry + rung sites, `_integrity_released` (3 readers incl. the alarm collector), integrity `elif` in `_apply_routing`, `integrity_refused_criticals()`, per-round advisory line, finalize wiring of advisory + `repo_root` into signal and result |
| `bench/insect_brain.py` | `signal_complete(extras=None)`; signal fields win over extras |
| `bench/tests/test_integrity_release_and_report_2026-10-02.py` | **new**, 17 tests incl. run 1b C0029 replay, gate invariance, S_k guards, signal tests |
| `bench/tests/test_forensics_machine_independence_2026-10-02.py` | **new**, 7 tests: D-1 both pins, D-2 refusal/record, D-5 C0012 criterion guard |
| `bench/tests/test_key_access_forensics.py` | fixture amendment (dated, declared): synthetic runs carry the runner-authored `repo_root` record; one explicit pin in the displaced-signal case; **no assertion changed** |

```
283 passed across the targeted battery (incl. the committed S_k consumer guard,
A4/gamma/queue/escalation/launcher suites, and both archived-run suites); 0 failed.
Full suite, experiments, and paid dispatch: not run, per the brief.
```

## REQUIRED SECTION 6 — Termination

**Three passes.** (1) Mechanism discovery — executed all three `repo_root` pins, found the `_in_scope` ancestor hole and the record absence. (2) Implementation + executed falsifiers for all six. (3) Regression + edge re-examination — found and fixed my own docstring tripping the S_k token guard, the displaced-signal fixture case, and surfaced the multi-rung shadowing residual. A fourth quick sweep produced nothing new above threshold.

**Preserved disagreements:** (i) against both seats' round 1 — C0017 was never a sandbox artefact and 10 was never correct; (ii) against cc2 — releasing unobserved-IV is unsafe and the synthesis keeps my carve-out; (iii) against my own round 1 — "no oracle weakened" was wrong as phrased, conceded at D-5; (iv) cc2's S_k denominator does not reproduce here. **Open residuals, named:** multi-rung IV shadowing in `route()`; the harvested-detector self-quote hits (7 on run 1b) still fire the scanner pending round-1 D3's channel split; the undeclared-`target_file` half of the D-2 class still belongs in the runner.

The design survives the 6 resolutions as fixed above. Done.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/integrity_advisory_r2_2026-10-02/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
