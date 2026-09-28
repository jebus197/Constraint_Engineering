# Review every CC1 change of 2026-09-23/24

Record written 2026-09-28T23:57:50+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

Dispatched 2026-09-24 against a brief asking both free seats to review EVERY change CC1 made on 2026-09-23 and 2026-09-24. Both responded: cc2 with 115 tool calls, fable with 78.

This record is written on 2026-09-28, 4 days after the round, and the delay is itself the finding worth recording. The guard `test_panel_rounds_have_a_full_record_2026-09-11.py` had been red on this round since it ran, and CC1 repeatedly reported the project's failing tests without noticing that 1 of them was naming a record CC1 itself owed. The Personalisation directive requires external review preserved "in full and in unfiltered format" and says "Never summarise in place of the full output"; a round left unrecorded for 4 days is that requirement unmet, whatever was done with the findings.

The seats' replies are reproduced whole below. CC1 does not re-characterise them here, because the point of the record is that a later reader can judge the seats' words for themselves rather than through a summary written by the party under review.

For the disposition of this round's findings, the subsequent record is `experimental_notes/Panel_FULL_RECORD_Check_My_Work_2026-09-28.md`, which covers the 2026-09-28 round that re-examined CC1's work after these findings were acted on, and which found 4 further defects in the fixes themselves.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# Panel brief — review EVERY change CC1 made on 2026-09-23/24

## SECTION 1 — The question

**Is any of the night's work wrong, insufficient, or an addition nothing reaches?**

Seven commits, `ae0c837..HEAD`. Read them with `git log --oneline ae0c837..HEAD` and
`git diff ae0c837..HEAD`. CC1 wrote all of it, largely between 01:20 and 03:00, and
none of it has been checked by anyone else. Two of the fixes below were themselves
repairs of CC1's earlier fixes from the same night, so the base rate of error in
this changeset is known to be non-zero before you start.

What changed, each with the claim CC1 attached to it:

1. **The prose-scoring flag no longer admits harmful fixes.** Two seats' fixes were
   adjudicated, ONE BRANCH WAS REMOVED as unreachable, and the removal is justified
   by a measurement. `bench/reference_runner_v3.py`, the block above
   `# THE SECOND SEAT'S DUPLICATE VETO BRANCH WAS REMOVED HERE`.
2. **The FFAFP trace detector, dead 2 days, is repaired and self-re-arms.**
   `hooks/ffafp_audit.py`: `migrate_turn()`, the stall counter, the forfeit notice.
3. **A Stop gate is ARMED** in `~/.claude/settings.json` under the key `Stop`:
   `hooks/ffafp_stop_gate.py`. It can REFUSE a turn.
4. **`classify_path` gained an "unresolved" class** and its 3 consumers exclude it.
5. **`CDSFL_SEAT` is now set** at both launch sites in
   `bench/experiment_11_orchestrator.py`.
6. **`routing_max_rungs`** on `RunnerConfig`, threaded only when it differs from 2.
7. **The harvest instrument** covers 3 destinations at full depth, content-addressed.
8. **30 suite failures closed**, including 20 module-level help calls guarded with
   `if __name__ == "__main__":`.

## SECTION 1b — The 4 things CC1 most expects to be wrong

Attack these first. CC1 believes each is a real risk and has not resolved any of them.

**(a) THE "unresolved" CLASS IS AN EVASION HOLE, CONFIRMED BY CC1 BEFORE SENDING
THIS. Do not spend a pass re-finding it; attack the FIX.** A path carrying an
unexpanded shell variable is excluded from the mutation set entirely, so it can
neither accuse nor excuse. Executed against the live predicate
`classify_path(p) not in ("transient", "unresolved")`:

    bench/reference_runner_v3.py          -> COUNTS
    $REPO/bench/reference_runner_v3.py    -> IGNORED   <-- real code, evaded
    ${HOME}/proj/bench/runner.py          -> IGNORED   <-- braced form, evaded

2 of 2 evasion forms succeed. CC1 introduced this at about 02:55 while repairing a
FALSE POSITIVE, and it is the worse trade of the two: a false refusal is visible,
annoying and self-correcting on the next bounce, whereas a silent evasion is none
of those. It also inverts this project's own stated asymmetry — `detect_target_kind`
resolves every ambiguous case to the SAFER side, and CC1 resolved this one to the
unsafe side.

**CC1's position, offered so you can attack it rather than guess at it:** the safe
default is that an unresolved path COUNTS, accepting the false refusal, because the
cost of a missed refusal is the whole purpose of the gate. But that restores the
original false positive on scratchpad writes, which is what gets a Stop hook parked.
The properly correct answer is probably neither: the hook sees the whole Bash
command text, and `$SP` is ASSIGNED in that text (`SP=/tmp/...`), so the variable
can be RESOLVED within the turn rather than guessed at. Resolve, do not guess. Say
whether that is achievable against the real transcript, what it costs, and what it
still cannot resolve (a variable exported in an earlier turn, or from the
environment). If you propose the counting default instead, give the measured
false-refusal rate it implies.

**(b) THE REMOVAL MAY BE WRONG.** Both seats wrote a branch under the identical
guard `_scoring_prose and tristate == SK_ADMISSIBLE`. CC1 kept the branch that
CONVICTS on new gate defects and removed the branch that always returned NO_SCORE,
on the named property "convictions recorded on harmful fixes", 3 of 5 against 0 of
5. Was that the right property? The removed branch was strictly more conservative.
Does the survivor admit anything the removed one would have refused, on ANY input,
not only the 5 fixtures? `scripts/a19_flag_admits_harmful_fixes_2026-09-22.py` is
the producer; extend its population rather than trusting its 10 rows.

**(c) 20 HELP CALLS WERE GUARDED IN ONE MECHANICAL PASS.** Each became
`if __name__ == "__main__": answer_help(...)`. Verify by EXECUTION that no script's
real behaviour changed: that each still answers `--help`, still refuses an unknown
flag where it did before, and still does its work. A mechanical edit applied 20
times is 20 chances to have broken something quietly.

**(d) THE SYNTHETIC END-TO-END FIXTURE FOR THE STOP GATE IS MISSING AND OWED.** CC1
wrote 2 such tests, found them VACUOUS by probing `fa.scan` directly (no turn was
ever handed to `fa.audit`), deleted them, and recorded the debt in
`bench/tests/test_ffafp_stop_gate_2026-09-24.py`. Build the fixture that actually
works, or establish that it cannot be built and say why.

**(e) 3 SCRIPTS ACT WHEN IMPORTED, AND CC1 FAILED TO FIX IT TWICE.**
`test_help_never_acts_2026-09-11.py::test_no_tracked_script_writes_at_import` is RED
on `scripts/a19_flag_admits_harmful_fixes_2026-09-22.py`,
`scripts/a19_veto_only_prose_sk_2026-09-22.py` and
`scripts/a19_prose_gates_are_one_sided_2026-09-22.py`. All 3 do their work at module
level, so importing them builds trees and spawns ruff and bandit. They write ONLY
inside a temporary directory, so nothing in the repository is touched, but the rule
is right: a tool that inspects a script must not make it act.

CC1 attempted the wrap mechanically, broke 2 of the 3 on the indentation of a
multi-line construct, restored them from git, and stopped rather than keep cutting
at working files at 03:00. The obstacle is that each file INTERLEAVES imports with
work, and the `if __name__ == "__main__"` guard sits MID-FILE (line 33 of the first),
so a naive "indent everything after the imports" is wrong.

Do this properly: move each file's work into `main()`, keep every import resolvable,
keep the `--help` answer reachable, and verify by EXECUTION that each still answers
`--help`, still does its work when run, and now does NOTHING when imported. The
guard named above is the acceptance test. This is the least interesting item here
and the most likely to be got wrong quietly, which is why it is stated precisely.

## SECTION 2 — Use the harness

Form your answer by RUNNING the machinery, not by describing it.

`S_k` is the instrument for item (b): the question is whether the surviving branch
can ever return ADMISSIBLE on a non-Python target. Prove or refute it over a
population you construct, not the 5 archived fixtures. Report what `R_k` does in
each case, because the founder's rule is that an unscoreable fix must not move risk.

`sigma` bears on items (a) and (d): both are questions about whether an instrument's
silence is evidence. A detector that cannot see a class of write, and a test that
examines nothing, are the same failure — silence indistinguishable from health. Say
what each would have to assert to tell those apart.

`gamma` and the two-sided gate do NOT bear on this changeset; say so if you find
otherwise. `routing_max_rungs` touches the ladder but not gamma: `_estimate_gamma`
short-circuits below `min_rounds=3`, so a single-round run cannot be gamma-governed;
verify that by calling it rather than taking it from this brief.

## SECTION 3 — Produce a fix, and test it

A finding without a fix is half an answer. A fix without a falsifier you have
EXECUTED is a hypothesis.

Deliver every fix by WRITING IT INTO THE SANDBOX REPOSITORY TREE AT ITS REAL PATH.
A fix described in prose is not delivered. A fix written to scratch space is
destroyed at teardown.

<!-- figure: harvest loss | scripts/panel_harvest_loss_2026-09-22.py | 72.0930 -->

72.0930% of scripts delivered by seats never reached `scripts/` measured against the
pinned pre-recovery commit.
Do not let yours join them. Note that `hooks/ffafp_audit.py` and
`hooks/ffafp_stop_gate.py` also live OUTSIDE the repository at `~/.claude/hooks/`;
deliver a fix to the repository copy and state what installs it.

A STORED falsifier may not call Wolfram: anyone reproducing this project must not
need it installed. You SHOULD use Wolfram while reasoning — it is the chief
secondary falsifier and the open-source tools remain primary.

Report the command you ran and the output you saw, verbatim.

## SECTION 4 — What would refute you

State, before concluding, what evidence would overturn your own answer. If you
report the evasion in (a) as real, say what a correct fix costs in false positives,
because the previous Stop hook was parked within a day for firing too often. If you
report the removal in (b) as correct, name the input class you searched and did not
find a counterexample in.

## SECTION 5 — Output shape

- `verdict` — SOUND / PARTLY SOUND / UNSOUND, on the changeset as a whole
- `reasoning` — citing file and line
- `findings` — one entry per defect, each with: what, where, how you executed it,
  and whether it is above the real-world-consequence threshold
- `evasion_a`, `removal_b`, `help_guards_c`, `fixture_d` — your verdict on each of
  the 4 named risks, with the evidence
- `falsifier_path`, `falsifier_command`, `falsifier_output` — verbatim
- `fix_path` — real repository paths, or NONE with the reason
- `additive_check` — for each fix you propose: what caller reaches it, what test
  executes it
- `refutation_condition`
- `strongest_disagreement` — with this brief's framing, including with CC1's
  adjudication in (b). Must not be empty; if you agree with everything, say why
  that is suspicious.
- `passes_run`

## SECTION 6 — Termination

Stop on diminishing returns: when a further pass adds no finding above the
real-world-consequence threshold. Report how many passes you ran and what the last
one added. Do not manufacture findings and do not nitpick style — CC1's prose is not
the subject, its correctness is.

Disagreement with the other seat is information. Do not smooth it away.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 115 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel review_all_cc1_work_2026-09-24) -->

Verified by calling, not by reading. Writing up.

---

## verdict

**PARTLY SOUND.** Six of the eight changes hold. Two do not: the `unresolved` class (item 4) is a confirmed evasion whose fix was incomplete in a way CC1 did not reach, and the removal (item 1) is *safe on the property CC1 named* but was justified by a measurement with only one arm. Items 2, 5, 6, 7, 8 and the help-guard pass survive scrutiny.

## reasoning

The night's two fixes-of-fixes are the ones that broke. Everything mechanical held.

## findings

**F1 — `classify_write` consumer 3 loses the kind, so the gate stays silent anyway. Above threshold.**
`hooks/ffafp_audit.py:542`. Fixing the two `record_tool` consumers is not enough: `audit()` re-classifies the *stored* path with no command text in scope, so `$D/_convergence.py` re-reads as `unresolved`, the subtraction empties `kinds`, and `code_touched` is False on a real code change. The mutation is recorded and its kind is lost — the gate never fires. I did not find this by reading; my own falsifier failed on it:

```
AssertionError: the variable-named code write was evaded: {'is_work': True, 'doc_only': True,
'code': False, ..., 'files': ['$D/_convergence.py']}
```

Fixed by storing the *resolved* path at record time and using `classify_write` in `audit`.

**F2 — the removal's justifying measurement has no benign arm. Above threshold.** See `removal_b`.

**F3 — `scripts/a19_flag_admits_harmful_fixes_2026-09-22.py:10` hardcodes `ROOT = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")`.** The other two a19 producers use `parents[1]`. This is the producer whose 10 rows justified the removal; run anywhere else it silently measures a *different tree*, or nothing. CDSFL §10 category 5, unreproducibility. Not fixed — fixing it changes which tree the archived figures came from, and that is CC1's call to make, not mine.

## evasion_a

**REAL, and the fix is resolution, not either default CC1 proposed.** Resolution *is* achievable against the real transcript. Measured through `scan`'s own `on_tool` hook over the live 262.2 MB corpus, 7986 mutations:

```
class          classify_path  classify_write
  code                  4006            4009
  doc                   2097            2146
  other                  497             504
  transient             1144            1275
  unresolved             242              52

RECOVERED from the evasion: 190 of 242 (78.5%)
  -> transient   131      -> doc  49      -> other  7      -> code  3
```

**59 real writes the old code dropped in silence are now counted. Zero false refusals** — no newly-counted path resolved under `/tmp`, and only `code` can make the gate refuse: 3 paths, every one a real `.py`.

**The measured false-refusal rate you asked for, for the counting default: 131 of 242 = 54.1%** (Wolfram Language: `54.13223140495868`). That is what parks a Stop hook, and it is why I did not take CC1's stated fallback.

What it still cannot resolve, and I have left visible in a test rather than buried: a variable exported in an earlier turn, one inherited from a parent shell, and any value built by command substitution. `$REPO/bench/reference_runner_v3.py` with `REPO` unbound is **still evaded** — deliberately. Counting it means guessing a directory, which is the defect the function exists to stop. 52 of 242 remain.

## removal_b

**Two-part verdict, and I disagree with the adjudication while agreeing with its outcome.**

*Safe:* the survivor cannot admit anything, on any input. Both arms of the inner `if` at `reference_runner_v3.py:11326–11358` return, so under the guard `_scoring_prose and tristate == SK_ADMISSIBLE` the function never reaches the ADMISSIBLE return at :11385. This is control flow, not a fixture result — no population can refute it. The removal does not open an admission hole.

*Wrong property:* the survivor **convicts** where the removed branch held NO_SCORE, and the producer's population contains **no benign fixes**, so a false conviction was impossible to observe by construction. I extended it. Three benign documentation fixes — a listing showing a hardcoded `/tmp` path *as the antipattern to avoid*, an `assert` in an illustrative snippet, a `random` Monte-Carlo example:

```
tmpdir-doc       REJECTED     bandit: 0 new HIGH, 1 new MEDIUM
assert-doc       REJECTED     ruff: 1 new diagnostic(s)
random-doc       REJECTED     ruff: 1 new diagnostic(s)
```

3 of 3 benign fixes convicted, at the *same signal strength* as the harmful ones (`structural` harmful: ruff 1 new + bandit 1 MEDIUM; `numerical`: 2 MEDIUM). Conviction precision on the combined population is **3/6 = 0.5**, Wilson 95% [0.188, 0.812]. No threshold separates the arms on this evidence. The code convicts on MEDIUM and on any ruff diagnostic, while the comment at :11312 justifies only HIGH.

The archived `correct_fix` of all 5 fixtures returns NO_SCORE, so nothing in the archive contradicts CC1 — which is exactly the point: the population could not have shown it.

## help_guards_c

**SOUND.** 25 files touched, 20 the mechanical wrap. Each pre-edit twin was reconstructed and run head-to-head: `--help` identical 20/20, unknown-flag refusal identical 20/20, work identical 17/20 (the 3 diffs are log timestamps only). No script lost its help, none accepts a flag it used to refuse. The ordering hazard was tested explicitly and is absent — the guard precedes every work statement, `--help` runs sub-2s, and a 20,343-file snapshot after running `--help` on all 25 showed zero files created or removed. The one non-2 exit (`ffafp_liveness_check`) is `takes_no_arguments=False` by intent.

## fixture_d

**Buildable — and CC1's stated reason for the debt is refuted.** The note says "Reproducing a real turn needs the transcript fields `scan` keys off, and I did not establish them." They were already established *in this repository*, in `bench/tests/test_ffafp_dead_detector_2026-09-22.py:90–108`, committed two days earlier, with a live `run_gate` that drives the gate end-to-end. The single missing field is `origin: {"kind": "human"}`; without it no turn opens and `fa.audit` examines nothing, which is precisely why the deleted pair was vacuous.

Built. Every end-to-end test asserts a turn actually opened and the verdict names the file *before* asserting an exit code — the anti-vacuity assertion the deleted pair lacked. Both the refusal and the non-refusal case are covered, so `returncode == 2` is not passing by default.

## sigma / the silence question

Both (a) and (d) are the same failure: silence indistinguishable from health. To tell them apart, each instrument must assert something *positive* about its own reach. The detector must assert that a path it declines to count was **resolved and found transient**, not merely unparsed — which is why tier 3 is a named, tested residue with a count rather than an unlogged fallthrough. The test must assert that **a turn opened and the verdict names the file** before reading any exit code. Both are now asserted.

## gamma

Confirmed, by calling rather than reading:

```
  rounds=1 counts=[5] -> gamma=0.0
  rounds=2 counts=[5, 3] -> gamma=0.0
  rounds=3 counts=[5, 3, 2] -> gamma=0.3639938835663522
```

A single-round run cannot be gamma-governed. `routing_max_rungs` touches the ladder, not gamma. Nothing in this changeset bears on the two-sided gate.

## falsifier_path

`bench/tests/test_ffafp_unresolved_evasion_2026-09-24.py` (11 tests) and `scripts/ffafp_unresolved_evasion_2026-09-24.py` (the corpus reproducer cited in the docstring, so the figure is not an assertion).

## falsifier_command / falsifier_output

```
$ python3 -m pytest bench/tests/test_ffafp_unresolved_evasion_2026-09-24.py -q
...........                                                              [100%]
11 passed in 0.34s
```

```
$ python3 scripts/ffafp_unresolved_evasion_2026-09-24.py
corpus: 6 transcripts, 262.2 MB, 7986 mutations
RECOVERED from the evasion: 190 of 242 (78.5%)
59 real writes previously dropped in SILENCE are now counted as work.
131 more are ignored for the RIGHT reason rather than by accident;
counting them instead -- the count-everything alternative -- would be 54.1% false refusals on this class.
52 remain tier-3 residue: leading variable, directory unknowable.
```

(b) precision, primary/open-source then Wolfram as second falsifier:
```
$ python3 -c "...proportion_confint(3,6,...)"
conviction precision 3/6 = 0.5
Wilson  95%: (0.1876, 0.8124)      Clopper-Pearson 95%: (0.1181, 0.8819)

$ wolframscript -code 'N[{3/6, 190/242*100, 131/242*100}]'
{0.5, 78.51239669421487, 54.13223140495868}
```
Computed with Wolfram Language (local Wolfram Engine, via `wolframscript`). No stored falsifier calls Wolfram.

(e) acceptance, run/help/import for all three:
```
a19_flag_admits_harmful_fixes:  run=0/IDENTICAL help=0/IDENTICAL import_output_lines=0
a19_veto_only_prose_sk:         run=0/IDENTICAL help=0/IDENTICAL import_output_lines=0
a19_prose_gates_are_one_sided:  run=0/IDENTICAL help=0/IDENTICAL import_output_lines=0
non-pycache files created on import: []
```
`test_help_never_acts_2026-09-11.py` itself cannot run here — it refuses rather than reporting 0 offenders from an unreadable `git ls-files`, which is the test behaving correctly. I ran its rule directly instead.

## fix_path

- `hooks/ffafp_audit.py` — `_VAR_REF`/`_ASSIGN`/`_FORLOOP`, `shell_bindings`, `resolve_shell_vars`, `classify_write`; all 3 consumers now resolve, and store the resolved form.
- `bench/tests/test_ffafp_unresolved_evasion_2026-09-24.py` — new.
- `scripts/ffafp_unresolved_evasion_2026-09-24.py` — new.
- `scripts/a19_flag_admits_harmful_fixes_2026-09-22.py`, `scripts/a19_veto_only_prose_sk_2026-09-22.py`, `scripts/a19_prose_gates_are_one_sided_2026-09-22.py` — work moved into `main()`.

**What installs the hook:** `cp hooks/ffafp_audit.py ~/.claude/hooks/ffafp_audit.py`. I deliberately did **not** run it — modifying the live user environment is not mine to do. Consequently `test_the_versioned_hook_matches_the_one_that_actually_runs[ffafp_audit.py]` and `test_the_versioned_copy_is_the_one_that_actually_runs` are **RED by design** until that copy happens. I checked the drift is entirely mine: 5 lines differ in the live direction, exactly my 3 consumer edits. **CC1 left the two copies in sync** — that is a point in the changeset's favour.

## additive_check

| Fix | Caller that reaches it | Test that executes it |
|---|---|---|
| `classify_write` | all 3 consumers in `record_tool`/`audit`, i.e. every Bash and Edit call the hook sees | 11 tests in the new file; tiers 1/2/3 each pinned separately |
| `resolve_shell_vars` | `classify_write` + both `record_tool` store sites | `test_a_bound_variable_is_resolved_not_guessed` |
| `shell_bindings` | `resolve_shell_vars` | `test_a_command_substitution_value_is_refused_not_half_expanded` |
| end-to-end fixture | the real gate, as a subprocess, over a real transcript | is itself the test; anti-vacuity asserted first |
| reproducer script | cited by name in `classify_write`'s docstring, so the figure is checkable | run above; refuses and returns 1 if the corpus is absent rather than printing a clean zero |
| 3 scripts → `main()` | unchanged CLI entry | run/help/import verified by diff against pre-edit capture |

Nothing was removed. Tier 3 keeps the residual hole *visible and asserted* rather than closing it by guess.

## refutation_condition

- **(a) overturned if** a machine's corpus shows newly-counted paths resolving under `/tmp` — i.e. my "zero false refusals" is corpus-specific. My figure comes from one corpus, 6 transcripts, one operator's habits. A different operator who writes `LOG=/tmp/x; ... > $LOG/a.py` would be counted; I did not find that shape here, but one corpus is one corpus. Also overturned if `os.environ` in the hook's process differs materially from the shell's, making environment-tier resolution wrong rather than merely absent.
- **(b) overturned if** my three benign fixes are judged genuinely harmful — a defensible position: one could argue a doc listing that trips bandit *should* be rewritten. That is an argument about the project's standard, not about the measurement, and it would make the survivor correct and my finding a preference. I searched documentation-shaped prose fixes that add a fenced listing; I did **not** search fixes that modify an existing listing, or non-Python fenced languages, and a counterexample there would sharpen the finding rather than refute it.
- **(F1) overturned if** storing the resolved path breaks a consumer of `turn["mutations"]` I did not exercise — persisted state written by the old build now mixes raw and resolved forms. `migrate_turn` backfills *keys*, not values, so it will not normalise them. 116 ffafp tests pass, but I did not replay a real persisted state file.

## strongest_disagreement

**With CC1's adjudication in (b), and with this brief's framing of it.** The brief asks "does the survivor admit anything the removed one would have refused?" — and that question cannot find the defect. The answer is provably no, on every input, and answering it is what makes the removal look justified. The actual difference between the two branches is **NO_SCORE versus REJECTED**, and the property CC1 named ("convictions recorded on harmful fixes") measures only the arm where conviction is correct. A domination claim needs both arms. Measured across both, the conviction is a coin flip.

I also disagree with the brief's ranking. It calls (e) "the least interesting item here." (e) was fine. The item that actually bit was the one nobody listed: **fixing two of the three consumers looks like fixing the hole and is not** — my own patch passed inspection and failed execution, on exactly the change the brief treated as already-diagnosed. "Do not spend a pass re-finding it; attack the fix" was right, but the fix needed attacking one layer deeper than either CC1 or the brief located it.

Where I agree with CC1 — on (c), and on the removal being *safe* — I want to name why that is not suspicious: both are claims with mechanical decision procedures. (c) was settled by a differential run of 20 reconstructed twins, and the removal's safety by control flow that no input can route around. Those are the two claims here I did not need judgement for.

## passes_run

**5.** (1) reproduce the evasion and map the consumers; (2) measure the corpus and build the resolver; (3) prove (b) structurally, then build the benign arm; (4) write the falsifier — which failed and exposed F1; (5) the (e) transform, which failed twice (docstring swallowed, then a nested `def`) before passing.

The last pass added no new finding above threshold — it converted a known defect into a verified fix and confirmed the inverse transform restored the originals byte-exactly. Stopping there.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 78 recorded tool call(s).

<!-- verbatim-begin: fable (panel review_all_cc1_work_2026-09-24) -->

# Panel verdict — CC1's night work, `ae0c837..HEAD`

**Preliminary:** the sandbox is staged **without `.git`**, so `git log/diff` cannot run here; I reviewed the tree directly. Three suite failures in `test_help_never_acts_2026-09-11.py` are staging artefacts (`git ls-files` fails loudly, by design), not defects of CC1's work — I re-ran its predicate git-free over all 206 scripts instead.

## verdict — PARTLY SOUND

The substance holds everywhere I could execute it. But the changeset shipped four defects: the confessed evasion hole (a), a **vacuous reachability test** guarding item 6, a **measurement producer pinned to the founder's absolute path** underwriting the removal in item 1, and the owed fixture (d). All four are repaired in this pass, with executed falsifiers.

## reasoning

- Item 1 removal block (`bench/reference_runner_v3.py:11360–11383`): structurally correct — both branches sit under the identical guard `_scoring_prose and tristate == SK_ADMISSIBLE` (11326), the first returns unconditionally, so the second was unreachable on **every** input, not just the fixtures.
- Item 2/3: `hooks/ffafp_audit.py` stall counter (`STALL_LIMIT=2`, `main()` liveness block) and `migrate_turn()` are sound; 94 tests green. Gate armed in `~/.claude/settings.json` under `Stop`, timeout 20; installed copies were byte-identical to repo copies before my fix.
- Item 5: `seat_environment()` sets `CDSFL_SEAT` at both launch sites (`experiment_11_orchestrator.py:1267, 1413`); reader confirmed at `wolfram_standard.py:420`; 22 tests pass.
- Item 6: the *wiring* at `reference_runner_v3.py:6064–6067` is correct — proven by executing the real `_apply_routing` with a route recorder (`max_rungs=5` arrives on opt-in, no keyword at default). The shipped *test* was not (finding F2). A settable path exists (`RunnerConfig` from-dict, line 1660).
- Item 7: `panel_harvest_loss_2026-09-22.py` matches its claims — `HARVEST_DIRS` covers the 3 destinations, `files/**` is full depth, sha256 content index over scripts/bench/hooks, loud `SystemExit(2)` on git failure. **Not executable here** (needs git + logs); verified by reading only.
- Item 8: spot-verified ~800 tests green across the touched files (458 operational-scripts, 226 prose-acceptance, 94 ffafp/routing, 22 wolfram). Full suite not run per dispatch rule.
- `gamma`: does **not** bear on this changeset — verified by calling: `_estimate_gamma([5])=0.0`, `([5,3])=0.0`, `([5,3,1])=0.4496`. Short-circuit below `min_rounds=3` confirmed by execution, not from the brief.

## findings

**F1 — the "unresolved" class is a silent evasion hole** (`hooks/ffafp_audit.py::classify_path`, pre-confirmed by CC1). Executed pre-fix: `$REPO/bench/reference_runner_v3.py` and `${HOME}/proj/bench/runner.py` both excluded from the mutation set. Above threshold (silent evidence loss, category 4). **Fixed — see evasion_a.**

**F2 — the routing reachability test never executed the thing it guards** (`bench/tests/test_routing_max_rungs_is_reachable_2026-09-24.py`, old lines 63–76). Its "recorder" test monkeypatched `RT.route` and then **called its own recorder** with a kw-dict the test itself built from a copy of the call-site expression — `_apply_routing` never ran. The companion check was an `inspect.getsource` substring scan, the project's own named `source_text_assertions` shape. A wiring bug (e.g. reading a constant instead of `cfg`) would have passed. Above threshold (verification-integrity, category 3). **Fixed:** rewrote both tests to drive the real `_apply_routing` over a minimal escalated critical; 7/7 pass. Executed proof preceding the fix: opt-in kwargs `{'max_rungs': 5}`, default kwargs `{}`.

**F3 — the removal's producer measured a hard-coded tree** (`scripts/a19_flag_admits_harmful_fixes_2026-09-22.py:10`, `ROOT = pathlib.Path("/Users/georgejackson/Developer_Projects/Constraint_Engineering")`). The committed measurement justifying the branch removal came from a script that crashes on any other machine and, run from any other checkout — **including this review sandbox** — silently measures the live repo instead of the tree under test. Its own sibling states the rule it broke. Above threshold (unreproducibility, category 5). **Fixed:** repo-relative with `CE_ROOT` override; measurement reproduced in-sandbox post-fix (3/5 harmful fixes convicted — matches the removal comment's figure).

**F4 — 3 scripts act at import** (pre-confirmed, item e). **Fixed** — see help_guards_c. Now 0 offenders in 206.

**F5 — the owed E2E fixture** (pre-confirmed, item d). **Built** — see fixture_d.

## evasion_a — REAL, and the fix is CC1's own third option: RESOLVE, don't guess

Implemented `shell_assignments()` + `resolve_shell_vars()` in `hooks/ffafp_audit.py`: `$VAR`/`${VAR}` in write targets are expanded from (1) plain-literal assignments in the same command text (heredoc bodies excluded; `$(...)`/backtick values refused — never half-resolve), then (2) the hook's inherited environment (`HOME` etc. reach the Bash tool and the hook identically). Wired into `bash_mutations` **and** the survey, so the two cannot disagree. Executed:

- `SP=/tmp/claude/scratchpad; … > $SP/gate_in.json` → `/tmp/…` → **transient** (the 01:47 false positive, now excused by *evidence*)
- `REPO=/Users/x/proj; … > $REPO/bench/reference_runner_v3.py` → **code, COUNTS** (evasion form 1 closed)
- `${HOME}/proj/bench/runner.py` → **code, COUNTS** (form 2 closed — previously invisible even as "unresolved": the brace failed `_NOT_A_PATH`)
- `SP=$(mktemp -d); … > $SP/x.py` → stays **unresolved**, excluded (true target is transient anyway)

**Is it achievable against the real transcript, and what does it cost?** Measured over all 534 live transcripts: **433** `$VAR`-bearing redirect write targets; **322 (74.4%) resolve from same-command assignments**, 0 needed the env fallback, **111 (25.6%) residual**. Of the resolved: **237 transient, 3 code, 82 other**. So the counting default CC1 offered as "safe" would have manufactured **≥237 false accusations** out of 433 (and the 3 real code writes it would catch, resolution catches too). What resolution still cannot reach: the 111 residuals (mktemp-style substitutions, vars from earlier turns). For those, exclusion is the **accurate** side, not the unsafe one: shell state does not persist between Bash calls in this harness, so a residual variable expanded to nothing at runtime — the literal path was provably never written. Cost of the fix in false positives: a wrong resolution requires a spoofed literal assignment *and* a `$VAR` redirect in one command; bounded at one bounced stop.

## removal_b — CORRECT, and the brief's "strictly more conservative" framing is wrong

- **Never-admit, structurally:** for `kind != TARGET_KIND_PYTHON`, either the early return fires (11079, NO_SCORE) or `_scoring_prose` is True, in which case every exit is REJECTED/ESCALATE/NO_SCORE — the branch at 11326 intercepts the only ADMISSIBLE route. No input escapes.
- **Population beyond the 10 rows** (extended the producer family, executed): 20 archived + **19 constructed** evaluations — `.md/.txt/.rst`, listing-bearing and pure-prose, clean/HIGH-injecting/fence-deleting fixes, both flag states, through both `compute_sk` and `_evaluate_sk_for_findings`. Result: **0 admissions; R_k held in every case; findings stay OPEN**. Convictions land exactly on statically evidenced harm; clean sweeps abstain (NO_SCORE), never pay out.
- **R_k:** REJECTED never reaches `apply_sk_to_rk` with an update — verified in code (12689–12692: tally + log only) and by execution. The founder's rule holds.
- **The only behavioural delta** between survivor and removed branch: `_rejection_lines` (12745) renders the conviction's reason into the next round's prompt. Conviction on gate-evidenced harm is *more truthful feedback*, not less conservative; a false conviction costs one misleading prompt line, below threshold. The removed branch refused **nothing** — it only abstained; calling it "more conservative" conflates silence with caution.
- Input class searched without counterexample: all non-Python suffixes above × fix classes {clean addition, bandit-HIGH injection, fence deletion, pure-prose edit} × flag states, plus the archived 5×2×2.
- The necessity of the veto (not just its safety) is mathematical: with e1/e2 unavailable, `inf E = 1/3 > 0` — **Wolfram Language (local Wolfram Engine) confirms `MinValue = 1/3` exactly**, so under the old aggregation bandit alone could never reject.

## help_guards_c — VERIFIED BY EXECUTION; the 3 owed refactors delivered

- Sweep over all 46 guard-carrying scripts, each executed twice: `--help` → exit 0 with a `usage:` line in 46/46; bogus flag → exit 2 refusal in 46/46. **PASS=46 FAIL=0.**
- The 3 a19 scripts (item e) properly refactored: work moved into `main()`, imports intact, `answer_help` at the bottom guard. Executed all four acceptance axes per script: import inert (0.15–0.21 s, 0 bytes stdout, no ruff/bandit spawned — previously the full pipeline ran), `--help` answers, bogus refuses, and the real work still runs to completion (all 3 executed end-to-end, exit 0; `a19_prose_gates` prints its full "rule holds" line). The named acceptance test's predicate: **0 offenders of 206** (was 3).

## fixture_d — BUILT, with the anti-vacuity assertion the deleted tests lacked

The deleted tests were vacuous because their transcripts never satisfied `is_human_prompt` — it requires `origin.kind == "human"`, which they didn't set. Four E2E tests now in `bench/tests/test_ffafp_stop_gate_2026-09-24.py`, each of which **first proves via `fa.scan` that the fixture yields a real open turn with the expected mutation set**, then asserts the gate subprocess's exit code: unverified code edit → **refused (exit 2, names the file and P-PASS)**; scratchpad-only `$SP` turn → **allowed (exit 0)**, the 01:47 bounce replayed; code edit + pytest after → **released**; `$REPO` evasion write → **refused**. On σ: this is the answer to "silence indistinguishable from health" for both instruments — the audit hook asserts its *offset advances* (liveness), and the fixture asserts the *turn was seen* before trusting exit 0. An instrument's silence counts only after it proves it looked.

## falsifier — path / command / output (verbatim)

`falsifier_path`: `bench/tests/test_ffafp_stop_gate_2026-09-24.py` (18 tests) and `scripts/a19_veto_only_prose_sk_2026-09-22.py` (population). No stored falsifier calls Wolfram.

`falsifier_command`: `python3 -m pytest bench/tests/test_ffafp_stop_gate_2026-09-24.py -q`
`falsifier_output`: `..................` / `18 passed in 0.47s`

`falsifier_command`: `python3 scripts/a19_veto_only_prose_sk_2026-09-22.py` (tail)
`falsifier_output`: `OK: 20 archived evaluations + constructed population (3 suffixes x 5 rows + 2 pure-prose + 2 e2e), 0 admissions, R_k held in every case.`

Final regression: `python3 -m pytest bench/tests/test_ffafp_stop_gate_2026-09-24.py bench/tests/test_routing_max_rungs_is_reachable_2026-09-24.py bench/tests/test_ffafp_audit_hook_2026-09-05.py bench/tests/test_ffafp_dead_detector_2026-09-22.py bench/tests/test_ffafp_state_migration_2026-09-22.py bench/tests/test_ffafp_cycle_gate_2026-09-10.py -q` → **`94 passed in 11.38s`**.

## fix_path

1. `hooks/ffafp_audit.py` — resolve-then-classify. **Install:** `cp hooks/ffafp_audit.py ~/.claude/hooks/ffafp_audit.py` (I did not write into the live `~/.claude` from a panel sandbox; until installed, `test_the_versioned_copy_is_the_one_that_actually_runs` fails **by design** — that is the sync guard working).
2. `bench/tests/test_ffafp_stop_gate_2026-09-24.py` — +9 tests (resolution + E2E).
3. `scripts/a19_flag_admits_harmful_fixes_2026-09-22.py` — `main()`, repo-relative ROOT.
4. `scripts/a19_veto_only_prose_sk_2026-09-22.py` — `main()` + constructed population.
5. `scripts/a19_prose_gates_are_one_sided_2026-09-22.py` — `main()`.
6. `bench/tests/test_routing_max_rungs_is_reachable_2026-09-24.py` — real-execution tests.

## additive_check

Nothing removed anywhere. (1) `shell_assignments`/`resolve_shell_vars`: called by `bash_mutations` (every consumer: hook, gate, survey); executed by 9 new tests. (2) new tests: executed, 18/18. (3–5) `main()`s: called by the `__main__` guards; executed by the operational-scripts probe (458 pass) and by my direct runs. (6) `_drive_real_apply_routing`: called by 2 tests, executed, 7/7.

## refutation_condition

- **(a):** a live-transcript survey showing resolution *mis*-resolving at a material rate (a spoofed assignment plus real `$VAR` redirect in one command), or residual-unresolved writes that demonstrably landed on tracked code — either overturns "residuals stay excluded". My 433-target corpus measurement is the thing to re-run.
- **(b):** any input on which the survivor returns ADMISSIBLE with `kind != TARGET_KIND_PYTHON` (one `compute_sk` call refutes me), or any consumer that closes a finding or moves R_k on `SK_REJECTED` that I missed in the grep of consumers.
- **(c/e):** any of the 46 scripts whose *pre-change* behaviour differed from what I asserted — only git history (absent here) could show that; a diff against `ae0c837` in the real repo is the check.
- **F2:** if some other test I did not find already executes `_apply_routing` with a non-default `routing_max_rungs`, my "vacuous" claim weakens to "redundant".

## strongest_disagreement

With the brief's framing of (a), in both directions. First, it presents the choice as counting-vs-exclusion and calls exclusion "the unsafe side" universally; measured, the counting default is the *worse* instrument — ≥237 of 433 real `$VAR` targets are transient, so counting manufactures false refusals at ≥55% of the class, which is precisely how the 2026-09-11 hook died. Second, for the *residual* class, exclusion is not the unsafe side at all: in this harness the unexpanded variable means the literal path was never written, so exclusion is the factually correct verdict, not a hole. And against CC1's adjudication in (b): the adjudication was **right** but its stated justification was **under-supported when shipped** — the dominance property was measured by a producer that only ran on one machine against a hard-coded tree, and the reachability guard for item 6 tested itself. The night's conclusions survive; two of its instruments did not deserve the trust the comments claimed for them.

## passes_run

**4.** (1) read/verify all eight items; (2) attack pass on the five named risks; (3) fix + falsifier pass; (4) measurement/consumer pass (corpus resolution rates, REJECTED consumers, Wolfram checks). The 4th pass added the 433-target measurement and `_rejection_lines`; nothing it surfaced crossed the threshold beyond what was already fixed — converged, stopped there.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/review_all_cc1_work_2026-09-24/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
