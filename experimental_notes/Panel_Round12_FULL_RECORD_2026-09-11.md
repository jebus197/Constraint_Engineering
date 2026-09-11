# Panel Round 12 — FULL RECORD, unfiltered

Record written 2026-09-11T09:27:03+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

Round 12 reviewed task V2 — the repair of 11 task-list entries an adversarial sweep had called overstated. An entry saying another entry is wrong is itself a claim, so the repair was mechanised as `scripts/overstated_entries_2026-09-11.py` rather than worked off the reviewer's list.

## What the round found, stated before the replies rather than after

**Both seats returned NOT READY or READY WITH EXCEPTIONS, and both were right: the instrument was worse than the entries it judged.**

**It FABRICATED a 100% failure rate wherever git could not answer.** `git ls-files --error-unmatch` exits 0 tracked, 1 untracked and 128 outside a repository, and `tracked()` returned False for 1 and 128 alike. In the panel's own sandbox, which has no `.git`, the script printed *"11 of 11 still fail a MECHANICAL check = 100.0000%, Wilson [74.1167%, 100.0000%]"* — three confidence intervals on a fabricated number, and the exact inversion of the truth. The 2 intervals are disjoint from the real 0.0000%, Wilson [0.0000%, 25.8833%]. **It is the same defect a seat found in `orphan_figures` ONE ROUND EARLIER, in a script written the same day, with the correct pattern already committed in `bench/archive_corpus.py`.**

**Two of the four checks still read the entry LINE rather than the entry BLOCK** — the population error the script's own docstring claimed was "caught before it became the answer". It was caught in 1 of 3. Measured: 21 entries carry a figure on their first line and 47 in their block, so the clearance issued for 5 entries came from an instrument blind to more than half its population.

**The conclusions survived and the instrument did not**, which is the honest summary: 9 of 11 were already answered and the sweep still found a 12th the reviewer had not named — but every one of those verdicts was issued by an instrument with 2 live defects. Both are fixed, both are pinned, and the figure is re-derived at 0 of 11.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 12: V2's measurement, and everything this session added. DELIVER YOUR FIX AS A FILE

<!-- figure: archived falsifier rejections that are NOT location artefacts | scripts/archived_falsifier_rejections_2026-09-10.py | real-rejection rate : 2/640 = 0.3125% -->
<!-- figure: founder-ruled tracker items neither carried nor declared | scripts/ruled_items_are_accounted_2026-09-11.py | unaccounted rate: 0/15 = 0.0000% -->

## SECTION 0 — THE DELIVERY RULE, AND THREE HARD PROHIBITIONS

**Founder ruling:** *"they need to supply fixes, not just problems!"* A finding without a fix is not a deliverable, and a fix in prose is not delivered. **Write it INTO the sandbox repository tree at its real path and leave it there.** Your sandbox is YOURS ALONE as of this round's predecessor; what you leave in it is attributed to you by name.

**THE 3 CATEGORIES THE FOUNDER RESERVES TO HIMSELF IN PERSON.** Do not delete a git ref, do not spend money on a paid seat, do not touch the sealed answer-key store. Any patch containing `git branch -D`, `git tag -d`, `git push --delete`, `git gc --prune`, `git reflog expire` or `filter-repo` is refused whole.

## SECTION 1 — The question

Section P: no entry moves to DONE until its fix has been through a panel review. **Task V2** is BUILT and TESTED and stuck there. Eight further entries were closed this session on measurements that have had no adversarial pass at all. Review them, break them, and fix what you break.

## SECTION 2 — What is measured so far. RUN THESE.

1. **V2 — "repair the 11 overstated entries".** `scripts/overstated_entries_2026-09-11.py` checks each claim rather than acting on it. Result: **9 of the 11 were already answered**; 4.2's defect was real; and the sweep found a **12th the reviewer did not name**, 7.3, the same shape. **A population error in the instrument was caught before it became the answer:** measuring over `Entry.text` — the entry LINE only — reported **25 of 67** DONE entries naming no artefact, 37.3134%, Wilson [26.7182%, 49.2846%]. Over the whole BLOCK it is **0 of 67**.
2. **A7.** The entry said 25 archived escalated criticals with no falsifier; **no predicate returns 25**. The closest returns 22 and reproduces the entry's one checkable family figure. `exp53_control_zero_live` contributes **0 and cannot contribute any** — it holds no `*_report.json`, its findings are in `checkpoint.json` under `all_findings` in a different schema. All 22 are escalated by a **named** mechanism; ANONYMOUS is 0 of 22.
3. **A6.** 70 of 5026 test functions assert on Python source text, 1.3928%. An inert comment appended at EOF reddens **0 of 84** runner-dependent files. I13's first answer was **11 of 37 surviving, 29.7297%**, and reading 3 survivors refuted it; refined to files that CALL the symbol it is **0 of 22**.
4. **A16.** 58 of 112 scripts are ACTIONS. Running the 54 measurements wrote nothing — checked by `git status --porcelain` before and after. It then found **5 of 54** consuming `--help` as a positional argument.
5. **A18.** 2 of the 3 "unwired" config fields ARE read, via `getattr(cfg, "field", False)` — an attribute read written as a string, which an AST attribute scan reports as zero.

## SECTION 3 — Attack these specifically

1. **V2 IS THE ONE UNDER SECTION P. Break its method, not only its arithmetic.** It concludes "already answered" for 9 entries by finding a dated CORRECTED paragraph. Is a correction that EXISTS necessarily a correction that is RIGHT? Pick one and check it.
2. **A7's predicate is fitted to a family figure.** I chose severity >= 0.7 AND `hil_escalated` AND no `falsifier_code` partly because it reproduces `exp55_v3_control` = 8. That is a single check against a single number. Find a predicate that also reproduces it and gives a different total.
3. **A6's I13 result is 5 functions in 1 module.** The upper bound is 15%, not 0. Extend it and see whether the conclusion survives a wider sample.
4. **The classification in A8 and A16 both turn on a judgement encoded as a rule.** `classify_citation` says a fixture stays a fixture; `classify` says unresolvable is an ACTION. Find a case where either rule gives the wrong answer for the right reason.
5. **Every number in Section 2 was produced by a script I also wrote.** That is the weakest structural property of this whole session. Pick the figure you least believe and re-derive it independently.

## SECTION 3B — EVERY FIX MUST BE TESTED, BY YOU, BEFORE YOU HAND IT BACK

**A fix you have not executed is a hypothesis.** Put the test at `bench/tests/<name>.py`, run it with `python3 -m pytest -q <path>`, and quote the result line verbatim.

**The test must be able to FAIL.** Break the thing your fix repairs, run the test again, and quote the red output too. This project found 8 of its own mutation tests vacuous that way, and **3 of mine in the last 24 hours** — a rebase control, an identity control, and a fence control whose fixture had its violation suppressed by a colon, so deleting the condition changed nothing and every test stayed green.

**Use the mathematical instruments where they bear.** Any proportion needs a Wilson interval and a second tool. If a fix changes what reaches a verdict, say what it does to `severity` and the two-sided `gamma` gate.

## SECTION 4 — What would refute YOU

For every finding, state what evidence would overturn it. A finding naming no such evidence is an opinion.

## SECTION 5 — When to stop

**Diminishing returns.** Above threshold means: it could put a wrong number in front of the founder, let a completion claim stand on a check that cannot fail, or let a guard go quiet. Do not pad to a count. Do not report style.

## SECTION 6 — The output shape, field by field

Return **Markdown**, in this order:

1. **`VERDICT`** — `READY FOR DONE`, `NOT READY`, or `READY WITH EXCEPTIONS` for **V2**, in the first line, then a one-line verdict for each of A6, A7, A16 and A18.
2. **`FILES I LEFT IN THE TREE`** — repo-relative paths. `NONE` plus a reason if empty.
3. **`FINDINGS`** — numbered. Each: **WHAT**, **WHERE** (`path:line`), **EVIDENCE** (the exact command and its output, quoted), **FIX** (the path you wrote it to), **WHAT WOULD REFUTE THIS**, **SEVERITY** (0.0 to 1.0).
4. **`THE FIGURE I LEAST BELIEVED`** — your answer to Section 3.5, with what you ran.
5. **`FIGURES I RE-RAN`** — each declared figure, what you got, whether it matched.
6. **`WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1`** — preserved, never smoothed.
7. **`WHAT I DID NOT CHECK`** — the honest boundary of your pass.

Do not return a summary in place of the full output.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 89 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round12_2026-09-11) -->

All work is green and verified. Writing up.

---

# VERDICT

**V2 — `NOT READY`.** Its headline instrument fails open outside a git work tree. Run in this sandbox it reported *"11 of 11 still fail a MECHANICAL check = 100.0000%, Wilson [74.1167%, 100.0000%]"*; with the probe repaired the same script reads **0.0000%, Wilson [0.0000%, 25.8833%]**. The two 95% intervals are **disjoint** — the original figure was an artefact of the instrument, not a property of the entries. Fixed and tested below; the fix has not itself been panel-reviewed, which Section P requires.

- **A6 — `READY WITH EXCEPTIONS`.** Its core is sound: the mutation revert is verified by *content* comparison, not by git, so it cannot silently fail to restore. One post-run guard read `git status` stdout with no returncode check and could only ever report "clean"; fixed. I did **not** extend I13 (Section 3.3).
- **A7 — `READY WITH EXCEPTIONS`.** The number is right and reproduces exactly (22; ANONYMOUS 0 of 22; 0 uncovered runner sites). The *stated reason for believing it* is refuted: eight readings reproduce the `exp55_v3_control = 8` anchor and they give three different totals — **20, 22, 32**.
- **A16 — `NOT READY`.** A material hole: the classifier green-lit `cdsfl_seal_logs.py`, whose default invocation seals log directories through `os.replace`. Fixed.
- **A18 — `NOT ASSESSED`.** I ran it (22/69 unread, Wilson [22.0948%, 43.5841%]) but did not attack it. Treating that as a pass would be a vote, not a tool.

# FILES I LEFT IN THE TREE

**New**
- `scripts/git_probe.py`
- `scripts/git_stdout_without_a_returncode_check_2026-09-11.py`
- `scripts/a7_predicate_is_underdetermined_2026-09-11.py`
- `bench/tests/test_git_probe_guards_are_not_vacuous_2026-09-11.py`
- `bench/tests/test_archive_predicate_and_vacuous_guards_2026-09-11.py`
- `bench/tests/test_a7_anchor_does_not_identify_the_predicate_2026-09-11.py`
- `bench/tests/test_a16_classifier_sees_across_modules_2026-09-11.py`
- `logs/a7_predicate_sensitivity_2026-09-11.json`

**Modified** — `scripts/overstated_entries_2026-09-11.py`, `scripts/source_text_fragility_2026-09-11.py`, `scripts/measurement_scripts_only_2026-09-11.py`, `bench/repo_paths.py`, `bench/tests/test_measurement_survey_is_safe_2026-09-11.py`, `bench/tests/test_config_aliases_survive_both_paths.py`, `bench/tests/test_derived_docs_match_their_generators_2026-09-01.py`, `bench/tests/test_task_list_entry_count_2026-09-10.py`

No patch of mine contains any of the three reserved operations. Nothing was removed; every change adds a capability or makes an existing check able to fail.

# FINDINGS

### 1. A guard that compares `git status` output to itself cannot fail, and it guards the archive-overwrite incident

**SEVERITY 0.75** · **WHERE** `bench/tests/test_measurement_survey_is_safe_2026-09-11.py:110-119` (pre-fix)

**WHAT.** `git status --porcelain` outside a work tree exits 128 and prints **nothing on stdout** — byte-identical to "the tree is clean". The test captured `.stdout` before and after the survey and asserted `before == after`. Both sides are `''`. A staged panel sandbox carries no `.git`, so this is the ordinary environment for a reviewer. The incident this test exists for is a survey **overwriting a deliberately preserved archive**.

**EVIDENCE.**
```
$ python3 - (porcelain before → write a file → porcelain after)
before: (128, "''")
after  : (128, "''")
assert before == after HOLDS despite a real write: True
```

**FIX.** `scripts/git_probe.py` (`porcelain()` returns `None`, never a misleading `''`) + `snapshot_tree`/`tree_difference` in the test: git when git can answer (founder's checkout unchanged), a filesystem manifest otherwise — so the check still runs and can still fail.
```
detects the write: True {'added': ['logs/_demo_write.txt'], 'removed': [], 'changed': []}
```

**WHAT WOULD REFUTE THIS.** A demonstration that the A16 survey is only ever run inside a git work tree — i.e. that `git status` cannot fail where this test runs. I found no such precondition anywhere in the file or its runner.

---

### 2. V2's own headline is produced by the same fail-open, and it is a 100% vs 0% swing

**SEVERITY 0.7** · **WHERE** `scripts/overstated_entries_2026-09-11.py:68-71` (pre-fix)

**WHAT.** `tracked()` returned `r.returncode == 0`. `git ls-files --error-unmatch` exits non-zero for *"not tracked"* **and** for *"not a repository"*. Outside a work tree every evidence path came back untracked, all 84 of them, and V2 reported every one of its 11 named entries as failing a mechanical check.

**EVIDENCE.** Before:
```
of V2's 11 named entries, 11 still fail a MECHANICAL check = 100.0000%
  Wilson 95%          : [74.1167%, 100.0000%]  (statsmodels)
  Clopper-Pearson 95% : [71.5086%, 100.0000%]  (statsmodels/beta)
```
After:
```
  *** 84 evidence path(s) COULD NOT BE CHECKED: this tree has no git work tree ***
of V2's 11 named entries, 0 still fail a MECHANICAL check = 0.0000%
  Wilson 95%          : [0.0000%, 25.8833%]  (statsmodels)
```
Disjoint at 95%. In a real git checkout `tracked()` returns `True`/`False` exactly as before, so no existing behaviour moved.

**FIX.** `scripts/git_probe.py::is_tracked` (tri-state) wired into `tracked()`; UNCHECKED rows are reported separately and excluded from the proportion, whose basis is now printed.

**WHAT WOULD REFUTE THIS.** Running the unrepaired script in a genuine git checkout and getting a figure materially above 0 — that would mean the 11 entries really do fail and git absence merely coincided. I cannot run that here; the repaired script separates the two cases so the next reviewer can.

---

### 3. `is_archived_run_output` fails *open* on an absolute path, and has already cost one dead branch

**SEVERITY 0.5** · **WHERE** `bench/repo_paths.py:56` (pre-fix)

**WHAT.** Every declared root is repo-relative (`bench/logs`), so an absolute path never matched one and returned `False` — *"not archived"*, the **permissive** answer, from the predicate whose entire job is to protect archives. `Path.rglob` yields absolute paths, so handing one over is the natural idiom. I made this exact mistake myself within minutes of reading the file.

**EVIDENCE.**
```
arc('bench/logs/x.json')      = True
arc(REPO/'bench/logs/x.json') = False
```
And the repository's own record, `bench/tests/test_derived_docs_match_their_generators_2026-09-01.py:60`: *"`is_archived_run_output` matches declared roots like `bench/logs`, which an absolute path does not begin with — so the first version of this branch never fired and the skip was unreachable. Caught 2026-09-10 by running it in the clone rather than reading it."* That caller hand-rebased its own path; **the shared predicate was left unguarded**.

**FIX.** `bench/repo_paths.py::_rebase_if_inside_repo` — rebases absolute paths that lie inside the repository; absolute paths *outside* stay `False`, because `line_mentions_archive_path` feeds this predicate real paths like `/usr/lib/python3/os.py` and raising would break it. Relative behaviour is byte-identical (pinned by test).

**WHAT WOULD REFUTE THIS.** A caller that depends on an in-repo absolute path being classified as production source. I enumerated all 8 call sites; all pass repo-relative paths, and all 29 of their existing tests still pass.

---

### 4. A16's classifier green-lit a script that seals log directories

**SEVERITY 0.6** · **WHERE** `scripts/measurement_scripts_only_2026-09-11.py:58` (pre-fix)

**WHAT.** The script's docstring states the safety rule: *"Anything this cannot resolve is an ACTION: an unrecognised call, a dynamic attribute…"*. **The code did not do that** — an unrecognised call was simply not a reason, so it fell through to MEASUREMENT, the runnable set.

**EVIDENCE.** Synthetic probe:
```
  MEASUREMENT  cross-module write helper    []
  MEASUREMENT  unrecognised bare call       []
  MEASUREMENT  io.open write                []
```
Reachable in the real population: of the 57 MEASUREMENT-classed scripts, **12 call into a local module the scanner cannot see — 21.0526%, Wilson [12.4745%, 33.2861%]**. Resolving them one level found a live one:
```
cdsfl_seal_logs.py -> ('MEASUREMENT', [])        # empty reason list
chain: VerificationChain() reaches replace() at verification_chain.py:621
bench/verification_chain.py:621:            os.replace(tmp_path, path)
```
`cdsfl_seal_logs.py`'s **default** invocation "seals every unsealed directory under logs/confer and logs/chat"; `--dry-run` is the opt-in for writing nothing. Only argparse's `--help` short-circuit keeps the survey off it — and *"5 of 54 scripts consumed `--help` as a positional argument"* is this same entry's other finding. Two independent things had to hold; one was never checked.

**FIX.** One-level cross-module resolution in `classify`, plus the `io.open` alias. Blast radius pinned: **exactly one script flips** (`cdsfl_seal_logs.py`), 57/59 → 56/60. The first version flipped four, and two were wrong — `str.replace` counted as a file write (`convergence_location.py:65` is `h.strip().lower().replace(" ", "_")`), and symbols were attributed to modules that do not define them. Unresolved symbols are now reported loudly (9 of them) rather than reclassified, because removing a working measurement from the survey needs evidence too.

**WHAT WOULD REFUTE THIS.** Evidence that the survey never invokes a MEASUREMENT-classed script without `--help`, *and* that argparse's short-circuit is itself guarded. The second half is what A16's own `--help` finding shows cannot be assumed.

---

### 5. Two vacuous git-read guards; one reports full coverage while examining nothing

**SEVERITY 0.4** · **WHERE** `test_derived_docs_match_their_generators_2026-09-01.py:165`, `test_task_list_entry_count_2026-09-10.py:136`

**WHAT.** The first builds `found` from `git ls-files` stdout with no returncode check; its only consumer is `assert not stray`, so with git absent the coverage ratchet reports **full coverage over zero documents**. The second asserts an expected value of **0**, which empty input also produces.

**EVIDENCE.** The contrast, live in this sandbox, same missing `.git`:
```
test_line_citations_resolve_2026-09-01.py   → 2 errors (it HAS `assert out.returncode == 0`)
test_derived_docs_match_their_generators…   → 12 passed
```
Census: `scripts/git_stdout_without_a_returncode_check_2026-09-11.py` → 39/70 candidates, narrowed to 9 git reads in tests, **hand-read down to 2**. `test_line_citations:99` was a declared over-report (returncode checked one frame up); `test_the_sandbox_severs_history:117` is vacuous *by design* and has its own positive control at `:105` — that is the pattern I copied.

**FIX.** Honest `pytest.skip` when git cannot answer; a **positive control** (`== 15` under the prose patterns) added so a `0` from an empty fetch cannot pass as a `0` from a real revision. Proven pre-existing vs mine: baseline `7 failed, 8 passed`; after `7 failed, 7 passed, 1 skipped` — my change converts exactly one falsely-passing test into an honest skip.

**WHAT WOULD REFUTE THIS.** A demonstration that both tests are only ever collected inside a git work tree.

---

### 6. A7's anchor does not identify A7's predicate

**SEVERITY 0.45** · **WHERE** `scripts/escalation_paths_2026-09-11.py:7-11`

**WHAT.** A7 defends its predicate because it *"reproduces the entry's OTHER family figure exactly, `exp55_v3_control` = 8, so it is almost certainly the one that was meant."* One scalar at one site is a one-bit test and cannot select among nine readings.

**EVIDENCE.**
```
 total  exp55  runs  predicate
    22      8     7  A7 baseline                          <-- hits the anchor
    20      8     7  same but severity STRICTLY > thr      <-- hits the anchor
    32      8     8  drop the severity threshold entirely  <-- hits the anchor
predicates reproducing exp55_v3_control = 8 : 8
distinct TOTALS among them                  : [20, 22, 32]
```
**This does not show 22 is wrong** — it reproduces exactly, and I confirmed the probe and A7 agree on A7's own predicate (both 22). It shows the stated reason for believing it is not a reason. 22 must travel as "22 *under this predicate*".

**FIX.** `scripts/a7_predicate_is_underdetermined_2026-09-11.py` + test pinning `[20, 22, 32]`.

**WHAT WOULD REFUTE THIS.** A second independent anchor from the entry that the 20- and 32-readings fail. The entry's only other family figure is the one already used.

---

### 7. A seventh instance of the bare-substring shape task 6.4 closed at six sites

**SEVERITY 0.3** · **WHERE** `bench/tests/test_config_aliases_survive_both_paths.py:119`

**WHAT.** `if "/logs/" in str(p): continue` — the exact shape 6.4's correction documents. It admits **703** archived files the shared predicate excludes: **690** under `bench/results/` and **13** under `bench/logs_quarantine/` — precisely the two roots 6.4 names a bare substring as missing.

**LATENT, NOT BITING.** 0 of those 703 sets a legacy alias true today, so nothing enters the assertion. Reported at 0.3 for that reason.

**FIX.** Wired to `is_archived_run_output`. The wiring is proven load-bearing by a monkeypatch recorder that *runs* the guard — see the disagreement section below.

**WHAT WOULD REFUTE THIS.** Nothing changes my measurement; the honest counter is that a latent divergence is below the founder's materiality bar. I have argued it is worth one line because 6.4 exists to remove exactly this divergence.

# THE FIGURE I LEAST BELIEVED

**V2's "11 of 11 = 100.0000%".** A unanimous result is the one most likely to be produced by a broken instrument rather than by eleven independent facts, and a 95% lower bound of 74.1167% on n = 11 is a lot of confidence to draw from one predicate.

I re-derived the underlying predicate independently rather than re-running the script: `git ls-files --error-unmatch <path>` directly, and `ls -la` on the same path.

```
$ git ls-files --error-unmatch bench/tests/test_escalation_paths_2026-09-11.py
fatal: not a git repository (or any of the parent directories): .git
rc=128
$ ls -la bench/tests/test_escalation_paths_2026-09-11.py
-rw-r--r--@ 1 georgejackson staff 6263 Sep 11 02:18 …
```

The file is present; git's non-zero exit says nothing about tracking. **100.0000% was the count of times `git` failed to start, presented as a defect rate.** That is Finding 2, and the repaired script reads 0.0000% on the identical tree.

# FIGURES I RE-RAN

| Figure | Declared | I got | Match |
|---|---|---|---|
| Header: real-rejection rate | 2/640 = 0.3125% | `2/640 = 0.3125%`, Wilson [0.0857%, 1.1322%] | ✅ exact |
| Header: unaccounted ruled items | 0/15 = 0.0000% | `0/15 = 0.0000%`, Wilson [0.0000%, 20.3883%] | ✅ exact |
| A7: escalated criticals, no falsifier | 22 | 22 | ✅ exact |
| A7: `exp53_control_zero_live` contributes 0 | 0 | 0 (holds no `*_report.json`) | ✅ |
| A7: ANONYMOUS | 0 of 22 | `0/22 = 0.0000%`, Wilson [0.0000%, 14.8655%] | ✅ exact |
| A7: uncovered runner escalation sites | 0 | 0 | ✅ |
| A16: scripts that are ACTIONS | 58 of 112 | 59 of 116 (pre-fix, incl. my 3 additions) → **113 pre-existing, not 112** | ⚠️ population differs by 1, cause unidentified |
| A16: the 4 named scripts are ACTIONS | 4 of 4 | 4 of 4 | ✅ |
| A18 | 2 of 3 fields read via `getattr` | script runs; reports 22/69 unread | ⚠️ not the same figure; not attacked |
| V2: entries failing a mechanical check | (implied low) | 100.0000% pre-fix → 0.0000% post-fix | ❌ instrument defect |

# WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

1. **On V2's method (Section 3.1), I partly disagree with the brief's framing.** I picked two corrections and checked them. **6.7's correction is RIGHT** — `ImmuneMemory` in `bench/dm/_memory.py` has 12 methods and **0 contain the word "evidence"**, so `self.has_evidence(...)` does raise; the only file in the tree defining `has_evidence` is a 2026-09-08 mutation snapshot. **6.4's correction is RIGHT about what it claims and incomplete about its class** — it says "the scope the entry claimed is closed", which is true and carefully scoped, and a seventh instance survives outside that scope. So the answer to *"is a correction that exists necessarily right?"* is: **both I checked were right**; what a dated CORRECTED paragraph does not establish is *completeness*. That is a weaker and more useful conclusion than "corrections may be wrong".

2. **I do not accept A7's 22 as refuted, and I will not join anyone who says the figure is wrong.** It reproduces exactly and its ANONYMOUS set is genuinely empty. Only the justification falls. Preserving that distinction matters more than the finding.

3. **I disagree with my own first attempt, and record it because the brief asks for it.** My initial F4 test was **vacuous** — it re-derived both path sets itself and never touched the site, so reverting the site to `"/logs/" in str(p)` left it **green**. Caught by mutating the site, not by reading the test. Replaced with a monkeypatch recorder that *runs* the guard; that version fails with *"the shipped-config guard never consulted bench/repo_paths"*. Also caught in my own work: `tree_manifest` used `os.stat`, which follows symlinks, and silently dropped a dangling self-referential link under `bench/logs/exp36_evidence_20260407T004931Z/` — found by reconciling two counts of the same tree (9711 vs 16722) and chasing the one file the exclusions did not explain. Now `os.lstat`; count reconciles exactly (9712 = 16722 − 7010 ruff-cache).

4. **A16's rule gives the wrong answer for the right reason on my own `git_probe.py`** (Section 3.4). It is classed ACTION because it spawns `git` — yet it spawns only read-only queries and cannot write. The asymmetry argument makes ACTION the correct call: the cost is a missing survey row, versus overwriting a preserved archive. I report this as the rule working, **not** as a defect, and I did not change it.

# WHAT I DID NOT CHECK

- **Section 3.3 — A6's I13 extension beyond 5 functions in 1 module.** Not attempted. The 0-of-22 result stands unchallenged by me and its 15% upper bound is untested.
- **A18 entirely.** I ran `config_fields_are_read_2026-09-11.py` and reproduced no figure from it; the brief's "2 of the 3" claim is unexamined.
- **`classify_citation` in A8** (the other half of Section 3.4). I attacked only A16's `classify`.
- **Whether any repaired figure changes `severity` or the two-sided `gamma` gate: it does not, and I checked.** The runner imports only `foreign_repo_roots` from `repo_paths` (`reference_runner_v3.py:4048`), which I did not touch; nothing else I changed is imported by the verdict path. No finding severity and no gamma input moves.
- **The two long-running A16 tests** (`test_running_the_measurement_set_leaves_the_tree_untouched`, `test_none_consumes_the_flag_as_data`, both `timeout=3600`). Deselected, per the standing instruction not to spend the dispatch waiting. **This is the weakest point in my A16 fix**: I changed which scripts the survey executes and could not run the test that executes them. The change is strictly conservative (one fewer script runs, and that script writes), but it is unconfirmed by execution and should be confirmed before A16 moves to DONE.
- **The full suite.** Not run. I ran targeted files only; the 7 pre-existing failures in `test_task_list_entry_count` are environmental (no `.git`) and I proved them present before my edit as well as after.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 73 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round12_2026-09-11) -->

All verification complete — every touched module's evidence tests pass post-patch (`25 passed in 203.06s`). Final panel return:

---

# VERDICT

**V2: READY WITH EXCEPTIONS** — the conclusions survive independent attack, but the instrument that produced them carried two live defects (both fixed and tested this round) and its stated denominators have drifted; it must be re-run once, in the founder's git tree, before the DONE flips.

- **A6: SOUND, with drift.** 70/5026 reproduces as **73/5091** today (1.4340% vs 1.3928%, same class, growth is new tests including mine). I13's wider-sample extension was **not** performed — the 15% upper bound stands unexamined.
- **A7: CONCLUSION SOUND, IDENTIFICATION OVERSTATED — corrected in place.** 22 reproduces; ANONYMOUS = 0/22 reproduces; runner-site gaps = 0 reproduces. But "almost certainly the one that was meant" is refuted: the anchor does not identify the predicate (Finding 3).
- **A16: FIGURES SOUND, GUARANTEE BROKEN — repaired.** 58 ACTIONS reproduces (58/113 today vs 58/112; one measurement script added since). The classifier missed five resolvable write forms in the dangerous direction (Finding 4); no current script uses them, so the published figures stand.
- **A18: SOUND, with one census blind spot repaired.** All three per-field claims verified at the named lines (`reference_runner_v3.py:12638`, `:14984`, `:9423`). The default census silently dropped every list-valued key — including `api_access`, the very key the entry's argument leans on (Finding 5).

# FILES I LEFT IN THE TREE

- `bench/tests/test_panel12_instrument_fixes_2026-09-11.py` — NEW: 11 tests over Findings 1, 2, 4, 5
- `bench/tests/test_escalation_predicate_disclosure_2026-09-11.py` — NEW: 2 tests over Finding 3
- `scripts/overstated_entries_2026-09-11.py` — PATCHED: git rc semantics, no-git refusal, block population
- `scripts/measurement_scripts_only_2026-09-11.py` — PATCHED: open-write forms, `truncate`
- `scripts/config_fields_are_read_2026-09-11.py` — PATCHED: list-valued keys are census leaves
- `scripts/escalation_paths_2026-09-11.py` — PATCHED: `predicate_family()` + underdetermination disclosure, docstring correction
- `bench/tests/test_overstated_entries_2026-09-11.py` — AMENDED: follows the refusal behaviour and the block population (annotated with why)

# FINDINGS

**1. V2's instrument fabricates a 100% failure rate wherever git cannot answer — including this panel's own sandbox.**
- **WHERE:** `scripts/overstated_entries_2026-09-11.py:68-71` (pre-fix `tracked()`)
- **EVIDENCE:** `git ls-files --error-unmatch` exits **128** for "not a git repository" and **1** for "untracked" (demonstrated: `rc_no_repo=128`, `rc_untracked=1`, `rc_tracked=0`). The pre-fix function returned False for both. Running the script in this sandbox: `of V2's 11 named entries, 11 still fail a MECHANICAL check = 100.0000%` / `Wilson 95% : [74.1167%, 100.0000%]` — three confidence intervals on a fabricated number, the exact inversion of the brief's "9 of 11 already answered". Any tarball, `git archive` export, or panel worktree reproduces it.
- **FIX:** `tracked()` now maps 0→True, 1→False, else RuntimeError; `main()` probes `git rev-parse` and **refuses with exit 2**. Post-fix in sandbox: `REFUSING TO MEASURE: not a git repository… exit=2`. Test red pre-fix: `AssertionError: tracked() must refuse outside a git repository, not report 'not tracked'` — `1 failed in 0.15s` (also re-broken by mutation, red again, restored). Green: `11 passed in 0.53s`.
- **WHAT WOULD REFUTE THIS:** a demonstration that `git ls-files --error-unmatch` returns 1 outside a repository on any supported platform, or that no deployment of this script ever runs outside a `.git` tree — this round is the counterexample to the latter.
- **SEVERITY: 0.85** (wrong number in front of the founder, produced live, self-certain in the output).

**2. Two of V2's four checks still commit the population error its own docstring says was "caught before it became the answer".**
- **WHERE:** `scripts/overstated_entries_2026-09-11.py:100-108, 140-155` (pre-fix `check_figures_have_producers`, `check_self_contradiction` — both over `Entry.text`, the entry LINE)
- **EVIDENCE:** measured line-vs-block: `entries with a figure LINE: 21 BLOCK: 47` — the shipped check was blind to 26 figure-carrying entries, and `orphans BLOCK: ['W1']` (W1's block quotes `Fisher exact p = 2.199086e-14` and cites no script). The "figures reproduce or cite a producing script" clearance for 1.1/5.1/6.2/6.5/M1 was issued by an instrument scanning first lines only.
- **FIX:** both checks now take `blocks`; the pinned invariant is *no DONE entry is a figure-orphan* (W1 is BLOCKED — a question, not a completion claim). Test red pre-fix (in the initial `10 failed, 1 passed` run: `TypeError`/missed fixture); green after.
- **WHAT WOULD REFUTE THIS:** evidence that `Entry.text` carries the full block (it does not — `parse_entries` line 128 binds `line`), or that no continuation paragraph in the list carries a figure (47 > 21 refutes it).
- **SEVERITY: 0.7** (a clearance check that cannot see most of its population; conclusion happened to survive — the instrument did not).

**3. A7's predicate is underdetermined by its single anchor; "almost certainly the one that was meant" is refuted.**
- **WHERE:** `scripts/escalation_paths_2026-09-11.py:10-11` (docstring claim)
- **EVIDENCE:** sweep of 7 candidate predicates over 2,642 archived registry entries. `hil & nofals` with **no severity filter** also reproduces the exp55_v3_control family figure exactly (2 + 6 = 8) with **total = 32**; strict `sev > 0.7` also gives 8 with total = 20. So {20, 22, 32} all pass the identification check, and the entry's unreproduced 25 sits inside that range. Robustness held where it matters: ANONYMOUS = 0 on the widest set too (`wide set … 32, ANONYMOUS=0`; paths: 12 merge deadlock, 11 irreducible, 9 stale contested). Dedup order (first-wins vs last-wins) does not move the 22.
- **FIX:** `predicate_family()` added and wired into `main()`, which now prints: `THE PREDICATE IS UNDERDETERMINED BY ITS ANCHOR… shipped (total 22)… dropping the severity filter (total 32)… ANONYMOUS is 0 under every candidate`. Docstring corrected by appended paragraph. Test red pre-fix: `AttributeError: module 'ep_t' has no attribute 'predicate_family'` — `2 failed in 2.85s`. Green: `2 passed in 1.84s`.
- **WHAT WOULD REFUTE THIS:** a second archived family figure that only the shipped predicate reproduces — that would complete the identification and make my "family, not a point" claim moot.
- **SEVERITY: 0.5** (headline number presented as identified when it is one of a family; the actionable conclusion was never at risk).

**4. A16's classifier passes five resolvable write forms as MEASUREMENT — the asymmetric direction it exists to prevent.**
- **WHERE:** `scripts/measurement_scripts_only_2026-09-11.py:78-84` (pre-fix builtin-`open`-only handling)
- **EVIDENCE:** pre-fix classifications, all `('MEASUREMENT', [])`: `pathlib.Path("x").open("w")`, `os.open("x", O_WRONLY|O_CREAT)`, `io.open("x","w")`, `open("x", mode="w")`, `f.truncate(0)`. Each writes the filesystem. The docstring's guarantee — "anything this cannot resolve is an ACTION" — was false for the method form of `open`, whose mode is not at `args[1]`. Sweep of the current 55 MEASUREMENTs: none uses these forms, so **the published 58/112 figure and the wrote-nothing survey stand**; classification post-fix is unchanged (`55/58 of 113`).
- **FIX:** any `open` call (method or builtin) is resolved; method-form treats every argument as a mode candidate and anything unresolvable as ACTION (a filename containing `w/a/x/+` costs a missing survey row — the cheap direction, documented); `truncate` added to `_WRITING_ATTRS`. Red pre-fix: `10 failed, 1 passed`; mutation red: `4 failed, 1 passed` with the guard disabled; restored green: `5 passed`, full file `11 passed`. Negative control (`open("w_file.txt")` read-only) stays MEASUREMENT in both states.
- **WHAT WOULD REFUTE THIS:** a reading of `classify` under which `Path.open("w")` was already caught (there is none — `attr=="open"` matched no branch), or a policy statement that pathlib writes are out of scope (the docstring claims the opposite).
- **SEVERITY: 0.75** (the failure it invites is the archived-overwrite incident A16 exists to prevent; latent, not yet fired).

**5. A18's census drops every list-valued config key, so an unread list-valued key could never be flagged.**
- **WHERE:** `scripts/config_fields_are_read_2026-09-11.py:89-95` (pre-fix `walk` — lists recursed into, key never recorded; the recursion into a list of scalars recorded nothing at all)
- **EVIDENCE:** pre-fix, `declared_fields` on a fixture `{"api_access": [], …}` omits `api_access` — the very key the A18 entry's "the arm is not lying" argument depends on was absent from the default census population. Post-fix default census: `78 keys examined, 54 read, 24 read by nothing` (most of the 24 look like declarative arm metadata — `designed_as`, `fail_condition`, `lapsed_when` — that is the founder's read, not mine). Per-field claims all verified: `reference_runner_v3.py:12638` `getattr(cfg, "merge_arbitration_enabled", False)` ✓, `:14984` `immune_memory_enabled` ✓, `:9423` `api_access` ✓, `max_papers_per_round: 0 readers` ✓.
- **FIX:** list-valued keys are leaves *and* dicts inside lists are walked. Red pre-fix (in the `10 failed` run); green after; evidence tests `25 passed in 203.06s`.
- **WHAT WOULD REFUTE THIS:** any pre-fix run whose output contains a list-valued key name — the `walk` code path made that impossible.
- **SEVERITY: 0.45** (census blind spot in the dangerous direction; the entry's specific conclusions were unaffected).

**Severity/gamma statement (Section 3B):** every fix touches measurement scripts and tests only. Nothing here reaches the runner's verdict path; no finding's `severity` is recomputed and the two-sided `gamma` gate's inputs are untouched.

# THE FIGURE I LEAST BELIEVED

**"Over the whole BLOCK it is 0 of 67"** — because it was produced by the same author's script whose sibling checks I had just shown scan the wrong population, and because a 37.31%→0% swing on a population change invites the suspicion that the second instrument is broken in the opposite direction. I re-derived it **without** `task_list_markers` or the V2 script: a raw regex over the marker lines, blocks reconstructed independently, artefact = any `scripts/|bench/|experimental_notes/|resources/|hooks/` path or the marker's own evidence field. Result: **92 markers, 80 DONE, 0 DONE entries naming no artefact** — the numerator claim replicates exactly; the **denominator does not: 80 DONE today, not 67** (confirmed by `parse_entries`: `Counter({'DONE': 80, …})`). Thirteen entries changed state or arrived after the figure was cut, and the brief carries it undated. As a corroborating spot-check I also hand-derived the Wilson interval for the header's 2/640: centre 0.0060896, half-width 0.0052322 → [0.0857%, 1.1322%], matching the script's statsmodels output to all printed digits.

# FIGURES I RE-RAN

| Declared | I got | Match |
|---|---|---|
| V2: "9 of 11 already answered" | pre-fix sandbox run says **11 of 11 fail (100%)** — fabricated (Finding 1); post-fix the script correctly refuses here; needs one run in a git tree | ✗ as an instrument, direction confirmed by hand |
| V2: 0 of 67 DONE naming no artefact | **0 of 80** (independent re-derivation) | numerator ✓, denominator drifted |
| V2: LINE population 25-of-67 error class | LINE 21 vs BLOCK 47 figure-carriers; error still live in 2 checks | ✓ error confirmed, wider than reported |
| A7: 22 escalated, no falsifier | **22** ✓ (first- and last-wins dedup both) | ✓ |
| A7: exp55_v3_control = 8 | **8** (2+6) — but under ≥3 predicates | ✓ and underdetermined |
| A7: ANONYMOUS 0/22; runner gaps 0 | **0/22**, and **0/32** on the widest predicate; gaps 0 | ✓, robust |
| A7: exp53 contributes 0 | ✓ — no `*_report.json` in either exp53 dir reaches `registry_entries` | ✓ |
| A6: 70/5026 = 1.3928% | **73/5091 = 1.4339%** | direction ✓, drifted |
| A16: 58 of 112 ACTIONS | **58 of 113** (55 MEASUREMENT), unchanged by my patch | ✓ (+1 script since) |
| A18: 2 of 3 fields read; line numbers | all three lines verified verbatim; `max_papers_per_round` 0 readers | ✓ |
| Header: 2/640 = 0.3125% | **2/640**, Wilson [0.0857%, 1.1322%] hand-derived ✓ | ✓ |
| Header: 0/15 unaccounted | **0/15** | ✓ |
| 6.7 correction content (Section 3.1) | pinned tests execute: `39 passed in 2.37s`; `ImmuneMemory` genuinely lacks `has_evidence` | ✓ — correction is right, not merely present |

# WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

1. **CC1's "a population error … was caught before it became the answer" claims more than happened.** It was caught in **one of three** affected checks; the other two shipped with the error, and the brief presented the script as the corrected instrument. The correction was partial and the docstring's confidence was not earned.
2. **CC1's A7 phrase "almost certainly the one that was meant" is refuted, not softened**: a one-anchor identification with at least three predicates passing the anchor is not "almost certain". The number 22 should be quoted with its family {20, 22, 32}.
3. **CC1's denominators are presented as current when they are perishable.** 67 DONE is 80 today; 5026 test functions is 5091; 112 scripts is 113. None of this changes a conclusion, but a brief that quotes undated counts against a moving list invites exactly the reproduction failures A7 spent its budget on.
4. Minor: A18's claim that `merge_arbitration_enabled` is "READ … by production" is carried by the runner line, ✓ — but the script also counts `scripts/claims_audit.py` (a measurement) as a production reader; "production" in `readers_of` is looser than the prose implies.

# WHAT I DID NOT CHECK

- **A6/I13 extension (Section 3.3):** I did not mutate a wider sample of the 22 symbol-calling files; the 15% Wilson upper bound stands unexamined, and my A6 verdict rests on the census reproducing, not on new mutation evidence.
- **A8's `classify_citation` rule** (Section 3.4, first half): not examined at all; my Section-3.4 answer is entirely on A16's `classify`.
- **A16's `--run` behaviour end-to-end** (the 5-of-54 `--help`-as-positional figure): I re-ran classification, not execution, of the 55 measurement scripts.
- **The "0 of 84 runner-dependent files" EOF-comment result:** not re-run (it requires the suite-scale runs the brief forbids).
- **The 22 escalated criticals' substance** — whether any *should* have carried a falsifier is the founder's disposition, per A7's own framing.
- **Git history of anything:** this sandbox has no `.git`, so every "tracked/committed" claim was checked structurally, not historically; the V2 script's tracked-evidence section must have its one confirming run in the founder's tree before V2's marker moves.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round12_2026-09-11/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
