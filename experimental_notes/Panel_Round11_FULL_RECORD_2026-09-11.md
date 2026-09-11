# Panel Round 11 — FULL RECORD, unfiltered

Record written 2026-09-11T09:27:03+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

Round 11 reviewed task V8 — the verbatim exemption that lets a panel record be committed without editing what the seats said. Two standing rules had collided: the Personalisation directive requires panel output preserved *"in full and in unfiltered format"*, and task V3 made the note linter BLOCKING at commit time, so a new note whose finding count rises above 0 refuses the commit. A verbatim transcript routinely contains findings in the seats' own prose, and the only way to commit one was to edit what the models actually said.

## Why this round matters beyond its findings

**Round 11 is the first panel round with real seat independence.** Until task A20 landed that day, every seat shared ONE writable sandbox and they ran concurrently, and seats are instructed to write their fixes into that tree at real paths — so a seat could read another's edits, and in round 10 one did. Agreement between seats sharing a writable directory is not evidence of anything. Each seat now gets its own sandbox.

**It paid immediately.** Both seats broke V8's scoping claim separately, which makes that agreement evidence where round 10's would not have been.

## What the round found, stated before the replies rather than after

**Both got amnesty for a note's own prose, by different routes.** (1) One space on a blank line: `sentences()` split paragraphs on a literal 2-newline string and `verbatim_paragraphs()` on a whitespace-tolerant regular expression, so the 2 paragraph numberings drifted and the exempt set was applied to findings numbered by the other splitter. A violation in the note's own voice counted 0 and was tagged `[verbatim]` — and the count is what the blocking ratchet reads. 20 of 730 markdown files in the tree already break it, 2.7397%, Wilson [1.7804%, 4.1938%]. (2) A marker inside a code fence: a note documenting the syntax in a fenced block opened a real region, because `sentences()` already skipped fenced paragraphs and the marker scan did not.

**Both are the same shape** — 2 hand-written expressions of one rule with no comparator, inside the exemption whose whole claim is that it is scoped. One `paragraphs()` now, fence stripping unconditional, and the repair moves nothing else: 1770 findings across 730 files before and 1770 after, 0 files changing count.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 11: 3 built-and-tested repairs awaiting Section P, and DELIVER YOUR FIX AS A FILE

<!-- figure: entry A19's NO_SCORE claim, re-derived over the tracked archive | scripts/orphan_figures_2026-09-10.py | NO_SCORE: 0 of 1035 = 0.0000% -->
<!-- figure: archived falsifier rejections that are NOT location artefacts | scripts/archived_falsifier_rejections_2026-09-10.py | real-rejection rate : 2/640 = 0.3125% -->

## SECTION 0 — THE DELIVERY RULE, AND THREE HARD PROHIBITIONS

**Founder ruling:** *"they need to supply fixes, not just problems!"* A finding without a fix is not a deliverable, and a fix in prose is not delivered. **Write it INTO the sandbox repository tree at its real path and leave it there.**

**YOU NOW HAVE YOUR OWN SANDBOX.** Until tonight every seat shared one writable copy and ran in it concurrently, so a seat read the other's edits and agreement between seats was not evidence of anything. That is fixed; your copy is yours alone, and what you leave in it is attributed to you by name.

**THE 3 CATEGORIES THE FOUNDER RESERVES TO HIMSELF IN PERSON.** Do not delete a git ref, do not spend money on a paid seat, do not touch the sealed answer-key store. You may recommend; you may not enact. Any patch containing `git branch -D`, `git tag -d`, `git push --delete`, `git gc --prune`, `git reflog expire` or `filter-repo` is refused whole.

## SECTION 1 — The question

Section P of the master task list: **no entry moves to DONE until its fix has been through a panel review.** Three entries are BUILT and TESTED and stuck there. Review them, break them, and fix what you break.

## SECTION 2 — What is measured so far

Read each entry in `experimental_notes/CDSFL_MASTER_TASK_LIST.md` and RUN its named evidence.

1. **V6** — a number typed into a panel brief had no guard on it, and one was wrong: the round-4 brief said *"gamma is 0.451"* and it is **0.415413**. Fix: `scripts/panel_brief_validate.py` re-EXECUTES every declared figure and refuses the brief if the script does not print it. Evidence: `bench/tests/test_panel_brief_format_2026-09-09.py`.
2. **V7** — a DONE marker naming a FAILING test passed the DONE-evidence guard, within the hour that guard shipped. Task V3 was marked DONE naming a file that was **10 of 10 RED** at that moment. Evidence: `bench/tests/test_done_markers_carry_evidence_2026-09-10.py`.
3. **V8** — the blocking note-lint made it impossible to commit a verbatim panel record without falsifying it. Two standing rules collided: panel output must be preserved *"in full and in unfiltered format"*, and the lint refuses spelled numbers. Fix: `<!-- verbatim-begin: <who> -->` regions are REPORTED but not COUNTED. Evidence: `bench/tests/test_verbatim_regions_are_not_linted_2026-09-10.py`.

## SECTION 3 — Attack these specifically

1. **V8 is the dangerous one. Can a note buy amnesty for its OWN writing by quoting someone?** The claim is that the exemption is SCOPED, so prose outside the markers is linted normally. Break that. Try nesting, an unclosed region, a marker inside a code fence, a marker inside a quoted block, CRLF, and a region that opens in one file and closes in another.
2. **V7 checks that a DONE entry's evidence file exists, asserts, is collected AND passes.** Find a DONE entry whose evidence passes for a reason unrelated to the claim — a test that would pass with the fix reverted. Name the entry.
3. **V6 re-executes declared figures.** What does it do with a figure whose script is slow, absent, non-deterministic, or exits non-zero with the right string on stderr? Does it refuse where it should and only where it should?
4. **The 3 fixes together.** V6 refuses a brief, V7 refuses a DONE marker, V8 exempts a region. Each is a gate. **Which of them can be satisfied without doing the thing it is meant to enforce?**
5. **`bench/repo_paths.py` gained `project_names`, `declared_project_names`, `foreign_repo_roots` and `is_onboarded_checkout` in the last 24 hours.** They are consumed by the falsifier replay path. Attack the identity resolution: a fork, a mirror, a rename, a submodule, no remote, no `.git`, a non-GitHub remote, a `.zenodo.json` that disagrees with the remote.

## SECTION 3B — EVERY FIX MUST BE TESTED, BY YOU, BEFORE YOU HAND IT BACK

**A fix you have not executed is a hypothesis.** Every fix you leave in the tree arrives with a runnable falsifier that you have RUN, and your reply carries its output. Put the test at `bench/tests/<name>.py`, run it with `python3 -m pytest -q <path>`, and quote the result line verbatim.

**The test must be able to FAIL.** Break the thing your fix repairs, run the test again, and quote the red output too. This project found 8 of its own mutation tests vacuous that way on 2026-09-09, and 2 of CC1's last night — a rebase mutation and an identity mutation both passed the first controls, and both had to be rewritten because the checkout's FOLDER happened to carry the project's name.

**Use the mathematical instruments where they bear.** Any proportion needs a Wilson interval and a second tool. The `severity` scale and the two-sided `gamma` gate are the runner's own instruments; if a fix of yours changes what reaches a verdict, say what it does to them.

## SECTION 4 — What would refute YOU

For every finding, state what evidence would overturn it. A finding naming no such evidence is an opinion. If you disagree with a claim in Section 2, say what you ran and what it returned.

## SECTION 5 — When to stop

**Diminishing returns.** Stop when another pass produces no new above-threshold finding. Above threshold means: it could put a wrong number in front of the founder, let a completion claim stand on a failing check, or let a note exempt itself from a rule it is subject to. Do not pad to a count. Do not report style.

## SECTION 6 — The output shape, field by field

Return **Markdown**, in this order:

1. **`VERDICT`** — for EACH of V6, V7 and V8: `READY FOR DONE`, `NOT READY`, or `READY WITH EXCEPTIONS`, in the first lines.
2. **`FILES I LEFT IN THE TREE`** — repo-relative paths you created or edited. `NONE` plus a reason if empty; an empty list without one is a failed round.
3. **`FINDINGS`** — numbered. Each: **WHAT** (1 sentence), **WHERE** (`path:line`), **EVIDENCE** (the exact command and its output, quoted), **FIX** (the path you wrote it to), **WHAT WOULD REFUTE THIS**, **SEVERITY** (0.0 to 1.0).
4. **`WHICH GATE CAN BE SATISFIED WITHOUT DOING THE THING`** — your answer to Section 3.4, with what you ran.
5. **`FIGURES I RE-RAN`** — each declared figure, what you got, whether it matched.
6. **`WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1`** — preserved, never smoothed. Say so explicitly if you agree with everything.
7. **`WHAT I DID NOT CHECK`** — the honest boundary of your pass.

Do not return a summary in place of the full output.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 48 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round11_2026-09-11) -->

# VERDICT

- **V6 — READY WITH EXCEPTIONS.** The re-execution machinery is sound and refuses in all four directions Section 3.3 names. But the gate is satisfiable without doing the thing: it never reads the brief's prose. Demonstrated, fixed, tested.
- **V7 — READY WITH EXCEPTIONS.** The mechanism does exactly what it claims. But at the moment a DONE marker is written it can see **3 of 52** DONE-evidence files — 5.77%, Wilson [1.98%, 15.65%] — so the V3 window it was built to close is still open for 49 of them. Measured, instrumented, tested. The remaining hole is architectural, not a bug in V7.
- **V8 — NOT READY (now repaired).** Section 3.1's attack succeeds. A note **can** buy amnesty for its own writing, and it does not need to be adversarial to do it. Fixed and mutation-checked; on the repaired code I would call it READY.

---

# FILES I LEFT IN THE TREE

| Path | What |
|---|---|
| `scripts/note_vagueness_lint.py` | **edited** — one shared paragraph splitter; single read; unbalanced-marker warning |
| `bench/tests/test_verbatim_paragraph_numbering_2026-09-11.py` | **new** — 7 tests, mutation-checked |
| `scripts/panel_brief_validate.py` | **edited** — `undeclared_figures()` + wired coverage report in `main` |
| `bench/tests/test_declared_figure_coverage_2026-09-11.py` | **new** — 8 tests, mutation-checked |
| `scripts/done_evidence_commit_coverage_2026-09-11.py` | **new** — the 3/52 instrument, figure read not typed |
| `bench/tests/test_done_evidence_commit_coverage_2026-09-11.py` | **new** — 7 tests, mutation-checked |

Combined regression, my 3 new files plus the 6 guards they touch:

```
398 passed in 18.59s
```

---

# FINDINGS

### 1. V8: the verbatim exemption leaks OUTSIDE the region, and a single space triggers it

**WHAT** `sentences()` and `verbatim_paragraphs()` used two different paragraph splitters, so a blank line carrying whitespace shifts the exempt set past `verbatim-end` and exempts the note's own prose.

**WHERE** `scripts/note_vagueness_lint.py:206` (`sentences`, split on the literal `"\n\n"`) against `scripts/note_vagueness_lint.py:269` (`verbatim_paragraphs`, split on `re.split(r"\n\s*\n")`). The second function's docstring asserted the two numberings *"agree by construction rather than by coincidence."* They do not.

**EVIDENCE** — fixture: clean intro, a blank line carrying **one space**, a properly opened *and closed* verbatim region, then a Rule 27 violation in the note's own voice after `verbatim-end`.

```
$ python3 scripts/note_vagueness_lint.py /tmp/amnesty.md     # pre-fix
  amnesty.md: 0 finding(s)
    ---- 1 finding(s) inside a verbatim region, reported and NOT counted ----
    para 5  SPELLED NUMBER (Rule 27: use digits)  ('twenty-nine')   [verbatim]
      The panel returned twenty-nine findings in total.

  0 finding(s). Reported, not enforced — read before delivering.
```

Counted **0** → the blocking per-file ratchet passes. The linter labelled the note's own sentence `[verbatim]`.

The mechanism is already live in the tree, not hypothetical:

```
files where the 2 splitters DISAGREE: 20      (of 730 .md files)
```

Post-fix, same fixture:

```
  amnesty.md: 1 finding(s)
    para 6  SPELLED NUMBER (Rule 27: use digits)  ('twenty-nine')
```

**FIX** `scripts/note_vagueness_lint.py:198-203` — one `PARAGRAPH_BREAK` / `paragraphs()`, called by both. Blast radius measured **before** adopting the regex form (the more correct of the two, since a whitespace-only line *is* a paragraph break): across all 730 `.md` files the sentence stream moves on **3 files, 69443 → 69453 sentences**, all three archived logs that nothing gates.

Test `bench/tests/test_verbatim_paragraph_numbering_2026-09-11.py`:

```
7 passed in 0.37s
```

Mutation — restore `text.split("\n\n")` inside `sentences()`:

```
FAILED ...::test_the_exemption_does_not_leak_past_verbatim_end
FAILED ...::test_the_two_numberings_agree_on_a_whitespace_blank_line
FAILED ...::test_a_single_splitter_is_the_only_one
3 failed, 4 passed in 0.35s
```

The four that stay green are the additive half — the exemption still working, the unbalanced-marker warning, its discrimination case, the single read — green *because* the mutation does not touch them. My first draft of that docstring said 2 would go red; the measurement said 3 and I corrected the docstring to the measurement.

**WHAT WOULD REFUTE THIS** A demonstration that `sentences()` and `verbatim_paragraphs()` cannot disagree — i.e. that no reachable `.md` file contains `\n[ \t]+\n`. Refuted already by the 20-file count. Or: a caller of the linter that normalises whitespace-only lines before invoking it, which would make the divergence unreachable in practice. I checked `hooks/pre-commit` and `main()`; neither normalises.

**SEVERITY 0.75** — it lets a note exempt itself from a rule it is subject to, which is Section 5's own threshold verbatim, and the exempting file class is the one carrying panel records.

---

### 2. V8, second-order: a marker imbalance exempts to end-of-file and nothing said so

**WHAT** An unclosed `verbatim-begin` exempts every paragraph after it to EOF. That is pinned as known behaviour, but the only thing watching it was `test_the_record_still_carries_its_markers_in_pairs`, scoped to one named file.

**WHERE** `scripts/note_vagueness_lint.py:269` (`verbatim_paragraphs`: `inside` never resets).

**EVIDENCE**

```
$ python3 -m pytest -q bench/tests/test_verbatim_paragraph_numbering_2026-09-11.py
7 passed in 0.37s
```
including `test_an_unbalanced_marker_is_announced`, which requires the literal `UNBALANCED VERBATIM MARKERS: 1 begin, 0 end` on a file with an unclosed region, and `test_a_balanced_file_is_not_warned_about`, which requires silence on a balanced one.

**FIX** `scripts/note_vagueness_lint.py` `main()` — a per-file warning. **The counting behaviour is unchanged and deliberately so**: escalating to a refusal changes the commit ratchet's exit status, which I cannot verify here without git. I recommend that escalation; I did not enact it.

**WHAT WOULD REFUTE THIS** Showing the commit ratchet already refuses unbalanced markers by another route. I did not find one in `hooks/pre-commit`.

**SEVERITY 0.35**

---

### 3. V6: the gate is satisfied by declaring a true figure while the prose states a false one

**WHAT** `check_declared_figures` proves a *declared* value re-executes. It never reads the prose, so the round-4 defect survives V6 intact, now with a green light on it.

**WHERE** `scripts/panel_brief_validate.py:198` — `check_declared_figures` operates only on `FIGURE.finditer(text)`.

**EVIDENCE** A brief declaring the **true** gamma against a real script, whose prose two lines below states the **wrong** one:

```
$ python3 scripts/panel_brief_validate.py /tmp/v6/LIAR.md
panel-brief: LIAR.md carries all 7 required sections
exit=0
```

Measured on **this round's own brief**: 2 declared figures, 19 distinct numeric literals in the prose.

**FIX** `scripts/panel_brief_validate.py:331-...` — `undeclared_figures()`, wired into `main()` at line 478 as a **report, not a refusal** (the precedent is `check_currency` in the same module; refusing would refuse every brief in the archive, and this module's own words are that a guard which refuses a correct brief gets bypassed). Calibrated on the 6 most recent archived briefs: 1, 2, 4, 7, 8 and 56 claims. On round 11's brief:

```
panel-brief: FIGURE COVERAGE — 5 numeric claim(s) in the prose are backed by no declared figure:
  0.451, 0.415413, 0.0, 1.0, 3.4
```

It names `0.451` and `0.415413` — the two numbers from the incident that created V6.

```
$ python3 -m pytest -q bench/tests/test_declared_figure_coverage_2026-09-11.py
8 passed in 0.40s
```

Mutations: `undeclared_figures` returning `[]` → **3 failed, 5 passed**; deleting the `main` call → **1 failed, 7 passed**.

**My fix shipped a bug and my own test caught it before I handed it over.** The first `_NUMERIC_CLAIM` used `(?![\w.-])`, which refused `0.415413.` at the end of a sentence — *the exact round-7 defect documented forty lines above it in the same file*, reproduced in a new regex. Red output:

```
>       assert "0.415413" in out, out
E       AssertionError: ['0.451']
1 failed, 7 passed in 1.07s
```
Boundary is now context-sensitive (`.` continues a number only when a digit follows), matching `_figure_token_found`.

**WHAT WOULD REFUTE THIS** Showing the dispatcher already cross-checks brief prose against declared figures somewhere I did not look. I grepped `panel_brief_validate.py` end to end; `validate()` is keyword checks only.

**SEVERITY 0.6** — it is the "wrong number in front of the founder" case, by name.

---

### 4. V7: at commit time the reporter can see 3 of 52 DONE-evidence files

**WHAT** `unsupported_done_entries` reads outcomes a run already produced and runs nothing. At the moment a DONE marker is written — a commit — the only things that run are `hooks/pre-commit`'s 8 GUARDS.

**WHERE** `scripts/task_list_markers.py:132` (reads `failed_nodeids`, runs nothing) with `bench/tests/conftest.py:618` (terminal summary only, does not change exit status).

**EVIDENCE**

```
$ python3 scripts/done_evidence_commit_coverage_2026-09-11.py
  DONE evidence files          : 52
  hook GUARDS files            : 8
  run at COMMIT time           : 3
  commit-time coverage         : 3/52 = 5.77% Wilson [1.98%, 15.65%]
  NOT run at commit time       : 49
```

Wilson cross-checked against an independent bisection on the score inequality `|k/n − p|/√(p(1−p)/n) ≤ z`, sharing no algebra with the closed form — `test_wilson_agrees_with_an_independent_derivation`, green. Bounds print **outward** (floor the low, ceil the high) so the interval is never narrower than computed.

The V3 incident is therefore reproducible for 49 of 52 entries: mark DONE, commit, hook runs 8 files that are green, full suite is 13 minutes away.

**FIX** `scripts/done_evidence_commit_coverage_2026-09-11.py` + `bench/tests/test_done_evidence_commit_coverage_2026-09-11.py`.

```
7 passed in 0.35s
```
Mutations: typing the guard list instead of reading it → `test_the_guard_list_is_read_from_the_hook` red; rounding the interval inward → `test_the_interval_rounds_outward` red. Both **1 failed, 6 passed**.

**I did not enact the hook change.** The right fix is a gate that runs the evidence of any entry whose marker is newly DONE in the staged diff. That needs `git diff --cached`, and **there is no `.git` in this sandbox** (`fatal: not a git repository`), so I could not execute it. An untested hook edit is precisely the addition-nothing-reaches class this standard forbids, so I delivered the measurement instead and am naming the gate as a recommendation. `test_the_coverage_is_a_subset_and_the_gap_is_real` fails the day coverage reaches 100%, with a message saying to retire it rather than delete it silently.

**WHAT WOULD REFUTE THIS** A pre-commit path I missed that runs more than the GUARDS list — the script reads the hook, so point it at the real hook and it will report whatever is there. Or evidence that DONE markers are never written in a commit that does not also run the full suite; I have no way to check that from a `.git`-less tree and say so.

**SEVERITY 0.55**

---

# WHICH GATE CAN BE SATISFIED WITHOUT DOING THE THING

**All three. They fail in three different places, which is the useful part.**

| Gate | Satisfied without doing the thing? | What I ran |
|---|---|---|
| **V6** | **Yes — at the boundary of what it reads.** Declare a figure that genuinely re-executes; write a different number in the prose beside it. Gate green, exit 0. | `/tmp/v6/LIAR.md` → `carries all 7 required sections`, `exit=0` |
| **V7** | **Yes — at the boundary of what it runs.** It attributes failures it *sees*; at commit time it sees 3/52. Marking DONE on a red file commits cleanly for 49 of 52 entries. | `done_evidence_commit_coverage_2026-09-11.py` → `3/52 = 5.77%, Wilson [1.98%, 15.65%]` |
| **V8** | **Yes — and this one is the worst, because it inverts.** The gate does not merely fail to fire; it actively grants amnesty to prose it was told to lint. One space on a blank line. | `/tmp/amnesty.md` → `0 finding(s)` with the note's own sentence tagged `[verbatim]` |

The common shape: **each gate checks a representation of the thing rather than the thing.** V6 checks the declaration, not the prose. V7 checks the outcome record, not the test. V8 checks paragraph *numbers* produced by a splitter that was not the splitter producing the findings. V8's is the one worth generalising, because the failure was a second hand-written expression of one rule with no comparator — `execute-do-not-grep`, inside the exemption whose entire claim is that it is scoped.

Ranked by what I would fix first: **V8 (repaired here) → V6 (repaired here) → V7 (measured here, needs a hook change only the founder's environment can verify).**

---

# FIGURES I RE-RAN

| Declared | Script | What I got | Match |
|---|---|---|---|
| `NO_SCORE: 0 of 1035 = 0.0000%` | `scripts/orphan_figures_2026-09-10.py` | `NO_SCORE: 0 of 1035 = 0.0000%` | **exact** |
| `real-rejection rate : 2/640 = 0.3125%` | `scripts/archived_falsifier_rejections_2026-09-10.py` | `real-rejection rate : 2/640 = 0.3125%` | **exact** |

Both reproduce. `2/640 = 0.3125%` is arithmetically right (`2/640 = 0.003125`). Note that with k=2, n=640 the Wilson 95% interval is roughly [0.09%, 1.13%] — the point estimate is quoted bare in the brief, which is the class of thing my V6 fix now reports; both are in the FIGURE COVERAGE output above only because they *are* declared, so they were correctly excluded.

The brief's **other** numbers — `0.451`, `0.415413`, `10 of 10 RED`, `4 findings`, `9 figures` — are declared nowhere and re-executed by nothing. That is finding 3, and it fires on this brief.

---

# WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

I have not read the other seats' returns — one-shot dispatch, own sandbox, no shared registry — so I have nothing to smooth and nothing to agree with. Where I disagree with the **tree**:

1. **`verbatim_paragraphs`' docstring was false.** *"the 2 agree by construction rather than by coincidence"* — they agreed by coincidence, on clean files, and 20 files in this tree already break the coincidence. I rewrote the sentence rather than deleting it, so the claim's history stays visible.

2. **I disagree with V8's own test file's framing of the unclosed region.** `test_an_unclosed_region_does_not_silently_swallow_the_rest` is named for a property it does not assert — it asserts the region *does* swallow the rest, and calls that safe. It is safe for a record and unsafe for a note; the file pinned the behaviour without making it visible on any file but one. I added the visibility and left the behaviour.

3. **I do not accept "READY FOR DONE" for V7 as written**, but I do not think that is V7's fault. V7 does what its docstring says and its docstring already concedes the limit. The 5.77% is the size of the concession, and nobody had measured it.

---

# WHAT I DID NOT CHECK

- **Section 3.5 entirely — `bench/repo_paths.py`.** I did not touch `project_names`, `declared_project_names`, `foreign_repo_roots` or `is_onboarded_checkout`, and I ran no fork/mirror/rename/submodule/no-remote/no-`.git`/non-GitHub/`.zenodo.json` case. This is the largest hole in my pass. It is also the one I could least honestly test: **this sandbox has no `.git` at all**, so every identity-resolution path would exercise the no-`.git` branch and nothing else, and a green result would be a folder-name coincidence — the exact trap the brief says caught two of CC1's mutations last night.
- **Section 3.2 — naming a specific DONE entry whose evidence passes with the fix reverted.** I did not do per-entry mutation testing across 67 DONE entries; I measured the structural gap instead. The entry the brief is fishing for may exist and I have not named it.
- **V8 attack surfaces I did not exercise:** a marker inside a code fence, a marker inside a quoted block, nesting, and a region opening in one file and closing in another. I stopped because the whitespace case already breaks the scoping claim and the shared-splitter fix is the right repair regardless of which of those also lands. **Two I can reason about but did not run:** CRLF is a non-issue because `Path.read_text()` applies universal-newline translation, and cross-file regions cannot exist because `verbatim_paragraphs` is called per file — but I did not execute either, so treat both as unverified.
- **The full suite.** Per the brief I ran targeted files only: 398 tests across my 3 new files and the 6 guards they touch. I have not proven my `sentences()` change is inert against the other ~50 test files, only against the 3 that lint or gate notes.
- **Whether my `PARAGRAPH_BREAK` change moves any file's ratchet baseline.** I measured the sentence stream (3 of 730 files, +10 sentences, all archived logs) rather than the finding counts. A file being edited in the same commit as its count moves would be affected; I could not test the ratchet without git.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 45 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round11_2026-09-11) -->

All confirmed: the 9 failures are `GitCannotAnswer` — the sandbox has no `.git` (the exact defect P8/P1 documented: `_NEVER_COPY={".git"}`), pre-existing environment, not my edits. Note also: **V7's fix fired live during my own run** — the summary correctly named `task M1 is marked DONE and names: test_task_list_entry_count…` when that git-dependent evidence failed here. The mechanism works.

---

# VERDICT

- **V6 — READY WITH EXCEPTIONS.** The re-execution mechanism is fail-closed at every edge I probed by execution (absent, slow, non-zero-exit-with-correct-stderr, non-deterministic — all refused). Exception: the recorded opt-in design means the round-4 defect shape — a wrong instrument value typed in prose, nothing declared — still passes clean. Warning channel added, tested, mutation-verified.
- **V7 — READY WITH EXCEPTIONS.** The reporter works (it fired correctly during this very review). Exceptions, both repaired this round: duplicate identifiers in the live list made `unsupported_done_entries` silently overwrite one DONE entry's failing evidence with another's; and the list itself was incoherent (`--check` exit 1, 4 duplicates) at dispatch time. Inherent limit stands as stated: it only maps failures the session produced.
- **V8 — NOT READY as dispatched.** The load-bearing claim — "prose outside the markers is linted normally, so a note cannot buy amnesty for its own writing" — was false in two executed ways. Both repaired, tested, and mutation-verified in this round; with the repair accepted it is ready.

# FILES I LEFT IN THE TREE

- `scripts/note_vagueness_lint.py` — edited (shared `paragraphs()` split; fence-aware, line-accurate verbatim scan)
- `scripts/task_list_markers.py` — edited (`unsupported_done_entries` merges duplicate-ident hits instead of overwriting)
- `scripts/panel_brief_validate.py` — edited (`check_undeclared_instrument_values`, wired into `main()`, advisory)
- `experimental_notes/CDSFL_MASTER_TASK_LIST.md` — edited (2026-09-11 entries renumbered P1–P4 → P8–P11, dated renumbering note added, content untouched)
- `bench/tests/test_verbatim_scoping_cannot_be_bought_2026-09-11.py` — new, 6 tests
- `bench/tests/test_duplicate_idents_do_not_eat_failures_2026-09-11.py` — new, 3 tests
- `bench/tests/test_undeclared_instrument_values_warn_2026-09-11.py` — new, 6 tests
- `bench/tests/test_declared_identity_names_only_itself_2026-09-11.py` — new, 2 tests

# FINDINGS

**1. A whitespace-bearing blank line bought amnesty for a note's OWN prose (V8).**
**WHAT:** `sentences()` split paragraphs on literal `"\n\n"` while `verbatim_paragraphs` split on `r"\n\s*\n"`; a blank line carrying a space desynchronised the two numberings and mapped own-prose findings into the exempt set. The docstring's "agree by construction" was false — they agreed by byte-coincidence.
**WHERE:** `scripts/note_vagueness_lint.py:246` (pre-fix).
**EVIDENCE:** file with `<!-- verbatim-end -->\n \n` + a Rule 27 violation: `a1.md: 0 finding(s) — para 4 … [verbatim]` (quoted in full above); control file without the space counted 1. Post-fix the same bytes count ≥1.
**FIX:** `scripts/note_vagueness_lint.py` (`paragraphs()` shared by both consumers; whitespace-only lines normalised first). Test green: `14 passed` with the existing V8 suite; full-revert control: `2 failed, 4 passed`; restored: `6 passed`.
**WHAT WOULD REFUTE THIS:** the pre-fix linter counting ≥1 on `a1.md` on any machine, or a demonstration that the pre-commit ratchet reads something other than the counted total.
**SEVERITY:** 0.7 — it defeats a blocking commit gate for the note's own writing, the exact thing the entry says cannot happen.

**2. A marker inside a code fence opened a real region (V8).**
**WHAT:** a note *documenting the verbatim syntax* in a ``` block opened an exemption covering everything after it; `sentences()` skips fenced paragraphs but the marker scan did not.
**WHERE:** `scripts/note_vagueness_lint.py:234-255` (pre-fix).
**EVIDENCE:** `a3.md: 0 finding(s) — … [verbatim]` (quoted above). Post-fix: counted, no `[verbatim]`. Fence-blind mutation: `1 failed, 5 passed`.
**FIX:** same file — fence state tracked line-by-line outside regions; fences inside a region are quoted text and cannot poison the scan (also tested).
**WHAT WOULD REFUTE THIS:** the pre-fix linter counting the a3 violation, or evidence no real note will ever document the syntax (this brief itself quotes the markers).
**SEVERITY:** 0.6.

**3. Duplicate live-list identifiers + dict overwrite = silent evidence loss inside the V7 guard.**
**WHAT:** the 2026-09-11 additions reused P1–P4, already owned by the panel-condition section P1–P7; `--check` exited 1 naming all 4; and `unsupported_done_entries` did `out[e.ident] = sorted(hit)`, so with both duplicates' evidence failing, the first entry's failing file vanished from the `DONE ENTRIES WHOSE EVIDENCE FAILED` report — §10 category 4, inside the guard built to prevent it.
**WHERE:** `experimental_notes/CDSFL_MASTER_TASK_LIST.md:529-539`; `scripts/task_list_markers.py:160` (pre-fix).
**EVIDENCE:** `python3 scripts/task_list_markers.py --check` → 4 × "identifier P_n already used", `exit=1`. Post-fix merge demo: `{'P1': ['bench/tests/test_alpha.py', 'bench/tests/test_beta.py']}`; overwrite mutation: `1 failed, 2 passed`. After renumbering: `task list coherent: 92 entries, 0 problems`, and the guard suites: `301 passed`.
**FIX:** merge in `scripts/task_list_markers.py`; renumber to P8–P11 with a dated note; pin test `test_the_live_list_has_no_duplicate_identifiers`.
**WHAT WOULD REFUTE THIS:** a demonstration that pre-fix code reported both files for one ident, or a committed record that P1–P4 reuse was deliberate aliasing.
**SEVERITY:** 0.65.

**4. V6's gate is satisfied by not opting in — the original defect still passes (recorded design, now visible).**
**WHAT:** nothing connects instrument values typed in prose to the declaration mechanism; the exact round-4 text passes clean.
**WHERE:** `scripts/panel_brief_validate.py:198-312` (pre-fix).
**EVIDENCE:** `check_declared_figures("Section 2: \`gamma\` is 0.451, Strong depletion.")` → `[]` (executed, quoted above).
**FIX:** advisory `check_undeclared_instrument_values` wired into `main()` — refusing would break the panel-reviewed opt-in design, so it names the value instead. `61 passed` with the whole brief-format suite; unwired mutation: `1 failed, 5 passed`.
**WHAT WOULD REFUTE THIS:** an existing caller that already cross-checks prose instrument values against declarations (I found none).
**SEVERITY:** 0.5.

**5. Task 4.2 is a DONE entry whose evidence passes for reasons unrelated to its claim (Section 3.2 answer).**
**WHAT:** 4.2 claims a sentence removed from `memory/feedback_simplest_sufficient.md`, status COMMITTED; its evidence `test_recovery_memory_doc_repairs.py` (24 tests) contains **zero** references to that file or sentence, and the file lives **outside the repository** (`~/.claude/projects/...`, exists on one machine only). The evidence is green with the fix fully reverted, by construction.
**WHERE:** `experimental_notes/CDSFL_MASTER_TASK_LIST.md:272-273`.
**EVIDENCE:** `grep -c "feedback_simplest_sufficient\|Prefer extending machinery" bench/tests/test_recovery_memory_doc_repairs.py` → `0`; `ls memory/feedback_simplest_sufficient.md` → `No such file or directory` (repo); file present under the home directory.
**FIX:** none written — no repo-resident test can honestly assert on an out-of-tree, never-committed file, and a vacuous test would be the 11-confirmed-defects class. The repair belongs to V2 (OPEN, which already lists 4.2): either commit the memory file or move 4.2 off DONE. Recommendation only; V2 is not mine to close.
**WHAT WOULD REFUTE THIS:** any assertion in that test file (or another named evidence) that reads the corrected sentence.
**SEVERITY:** 0.55.

**6. `declared_project_names` trusts an unguarded invariant of `.zenodo.json` (Section 3.5).**
**WHAT:** every GitHub-shaped `related_identifiers` entry becomes a project identity consumed by `foreign_repo_roots`; the docstring asserts the file "names its own repository and nothing else", but nothing enforced it — one added citation would make a foreign project's absolute paths rebase as this project's tree.
**WHERE:** `bench/repo_paths.py:124-162`.
**EVIDENCE:** synthetic 2-identifier file → `{'Constraint_Engineering', 'OtherProject'}` and `foreign_repo_roots("/home/x/OtherProject/bench/a.py")` → `['/home/x/OtherProject']`. Live-file mutation control (citation appended, then restored): `1 failed, 1 passed` → restored `2 passed`. Other probed cases behaved correctly: no-`.git` sandbox → `({'Constraint_Engineering'}, 'declared')`; `is_onboarded_checkout()` → `False`; folder name `repo` filtered.
**FIX:** `bench/tests/test_declared_identity_names_only_itself_2026-09-11.py` — pins the identity and documents the widening mechanism; editing `.zenodo.json` now forces a same-commit identity decision.
**WHAT WOULD REFUTE THIS:** a filter on `relation` (e.g. only `isSupplementTo`) already excluding citations — there is none; the code reads all entries.
**SEVERITY:** 0.4.

**Instruments statement (3B):** none of these fixes touches what reaches a runner verdict — the `severity` scale, `GAMMA_BANDS` and the two-sided gate are unmodified. Every change moves in the fail-closed direction: V8 can only count *more* own-prose findings, V7 can only report *more* failing evidence, V6 adds an advisory channel. I report my probe results as counts, not rates — 2 of 6 attack shapes produced amnesty is too small an n for an interval to add information rather than decoration; the brief's two declared proportions carry their own intervals and reproduced (below).

# WHICH GATE CAN BE SATISFIED WITHOUT DOING THE THING

All three, in different ways — ranked by how cheaply, with what I ran:

1. **V8 (was worst, now repaired):** satisfiable *mechanically*, twice, without even claiming to quote anyone — the whitespace-line and code-fence bypasses above, both demonstrated by execution and now closed. The *inherent* remainder: the markers assert quotation and nothing can verify authorship, so a note can still wrap its own prose in `verbatim-begin` deliberately — mitigated only by the exempted findings being printed in full (a reader-visible lie, not an invisible one).
2. **V6:** satisfiable by *omission* — type the number, declare nothing. Executed: `check_declared_figures` returned `[]` for an undeclared wrong gamma. Recorded opt-in design; now at least named at dispatch by the warning.
3. **V7:** satisfiable by *not producing the failure* — it maps only failures the session produced, so a targeted green run says nothing about the named evidence (stated honestly in its own docstring), and the DONE-evidence guard beneath it accepts any existing, asserting, collected, *unrelated* test — 4.2 is the live specimen. Per-item mutation testing remains the only closure, and the entry says so.

# FIGURES I RE-RAN

- `scripts/orphan_figures_2026-09-10.py` → `NO_SCORE: 0 of 1035 = 0.0000%`, Wilson [0.0000%, 0.3698%] — **matched the brief exactly.** (Its A8 section correctly *refused* in this no-git sandbox rather than fabricating 100% — the round-10 repair working.)
- `scripts/archived_falsifier_rejections_2026-09-10.py` → `real-rejection rate : 2/640 = 0.3125%`, Wilson [0.0857%, 1.1322%], location artefacts 35/640 — **matched the brief exactly.**

# WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

- **V8's entry text and its test docstring claim the numbering agreed "by construction."** It agreed by coincidence, on byte-exact blank lines only. The 8 shipped tests all used pristine `\n\n` separators, so the load-bearing "scoped, not whole-file" property was tested only on inputs where the two splits happen to coincide.
- **CC1 broke the coherence substrate the same day it shipped it:** the P1–P4 reuse landed within hours of `unsupported_done_entries` — the guard keyed on identifiers while its author was duplicating identifiers. Same-day self-collision, the V1/V3 class again.
- **P8's (née P1) sandbox-independence claim I checked rather than accepted:** my sandbox files are real copies, not symlinks, and my mutations never reached the canonical tree. Agreement, but by verification.
- Otherwise I agree with Section 2's three claims as stated; each reproduced when run.

# WHAT I DID NOT CHECK

- **Inline double-quoted markers**: `"...<!-- verbatim-begin: x -->..."` in prose still toggles a region (`mask_quoted` is not applied to the marker scan). Residual, lower-risk than the fence case; I kept the fix's blast radius small and disclose it rather than half-fix it.
- **Gamma itself**: I did not re-derive 0.415413 — no falsification of V6's motivating number was attempted; round 4's two independent re-derivations stand as the record.
- **The other ~60 DONE entries' evidence** for 4.2-style vacuousness — only 4.2 confirmed; the shared-evidence clusters (R4–R9 on `test_rulings_written_back`, 9.1/9.2/9.4) are unaudited candidates.
- **The full suite** (forbidden by brief). The 9 observed failures are diagnosed environment failures (`GitCannotAnswer`, no `.git` in the panel sandbox — the P8 finding's own subject); I did not verify they are green in a git checkout.
- **The dispatcher's live wiring** of `check_declared_figures` (`bench/confer_maths_panel_2026-09-05.py`) — it validates argv at module import (P10) and spends money when run; I relied on its existing test rather than executing it.
- **repo_paths fork/mirror/rename/submodule** cases were reasoned through, not executed; only no-`.git`, declared-tier, folder-name filtering and `foreign_repo_roots` were probed by execution.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round11_2026-09-11/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
