# Panel Round 7 — FULL RECORD, unfiltered

Record written 2026-09-11T09:40:22+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

Round 7 is the first round dispatched under an explicit DELIVERY RULE, written into the brief after rounds 5 and 6 returned excellent prose and 0 source files: a finding without a fix is not a deliverable, and a fix described in prose is not delivered either. Each seat was told to write its repair at its real path inside the sandbox repository tree.

## What the round found

**It worked, and the seats' patch found 2 holes in CC1's.** Round 7 returned 2 new test files and a patch to `scripts/panel_brief_validate.py`. The worst hole: a declared figure whose script path began `../` executed a script OUTSIDE the repository and accepted its output as evidence. The delivered code was P-passed against 12 cases the seats did not write before it was applied.

**A CAUTION THAT APPLIES TO THIS ROUND.** Until task A20 landed on 2026-09-11, all seats shared ONE writable sandbox and ran concurrently. Agreement between seats here is not evidence of independence.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 7: check this work, and DELIVER YOUR FIX AS A FILE

<!-- figure: gamma at 13 passes | scripts/ffafp_cycle_gamma_2026-09-10.py | 0.294998 -->

## SECTION 0 — READ THIS BEFORE ANYTHING ELSE. THE DELIVERY RULE HAS CHANGED.

**Founder ruling, verbatim, 2026-09-10:** *"its fine to find problems, but you must also provide (tool verified) fixes in all cases"* and *"they need to supply fixes, not just problems!"*

**A finding without a fix is not a deliverable this round. A fix described in prose is not delivered either.** Measured across panel rounds 5 and 6, in which the assistant made no concurrent edits: the seats handed back **0 source files**. Both rounds returned excellent prose and executed probes, and the code evaporated. The cause is mechanical, not yours — `bench/panel_sandbox.py:teardown` destroys the sandbox, and `changes()` only preserves files that are still **inside the sandbox repository tree** when you finish.

**So: write your fix INTO the sandbox repository tree, at the path it would live at, and leave it there.** Not `/tmp`. Not a scratch directory. If you modify an existing file, edit it in place in the sandbox. If you add a test, put it at `bench/tests/<name>.py`. Everything you leave in the tree is returned to the assistant as a patch, tested, and either applied or refused with a reason. Anything outside it is destroyed.

You may write freely inside the sandbox. It is a copy. The canonical tree is fingerprinted before and after and you cannot reach it.

## SECTION 1 — What to check

Three changes landed in the last 40 minutes, all responses to findings you made in round 6.

1. **`scripts/panel_brief_validate.py` — `check_declared_figures` hardened.** You both found it matched by substring, so a declared `0.29` reproduced against a printed `0.294998`. It now requires a whole token, delimited by anything that is not a digit, letter, dot or minus. fable's residual — that a bare `1` or `9` is a genuine token in almost any output — is closed by requiring at least 3 significant characters. Over 8 cases it now scores **8 of 8**, Wilson [67.5592%, 100.0000%], where the substring form scored **4 of 7**, Wilson [25.0458%, 84.1780%]. **And this very sentence was caught by `scripts/wilson_interval_consistency.py` before dispatch** — its first draft put the two counts side by side with only the LATTER count's interval after them, so the interval belonging to the 8-case score sat against the 7-case score. A correct interval under the wrong count, in a brief about a guard that refuses wrong numbers. Attack that too. **The check order was wrong on the first attempt and took 2 existing tests red**: the distinctiveness rule ran before the script-exists rule, so a declared figure against a missing script reported the wrong reason. Infrastructure failures now report first.

2. **`bench/tests/test_precommit_gate_cost_2026-09-10.py` — the pinned count moved 169 to 174**, because task V7 added 5 tests to one of the 6 guard files. The test went red exactly as its own docstring says it should, and the entry was corrected in the same change.

3. **`experimental_notes/CDSFL_MASTER_TASK_LIST.md` entry 1.1** — a duplicated sentence and a stale "These 4 files" were removed, both left by an earlier correction of mine.

**Attack all three.** The first is the one that matters: it is a guard whose whole job is refusing wrong numbers, and it has now been wrong twice.

## SECTION 2 — Use the harness

**Form your answer by RUNNING things.**

- **`scripts/panel_brief_validate.py`** — drive `check_declared_figures` directly. Construct declarations that SHOULD pass and that should be refused. Find one it still gets wrong. Candidates worth trying: a figure that appears only inside a longer word, a figure with a thousands separator, a negative number, a percentage sign, a figure printed only on stderr, a script that prints the figure but exits non-zero, a declaration whose script path escapes the repository with `..`.
- **`python3 -m pytest bench/tests/test_panel_brief_format_2026-09-09.py -q -p no:cacheprovider --netguard-strict`** — 29 tests. Mutate the source and prove they catch it. A mutation must be asserted APPLIED and must land on a line the fixture executes.
- **`scripts/ffafp_cycle_gamma_2026-09-10.py`** — the two-sided gate, gamma at or above 0.30 AND 3 consecutive zero-discovery passes. Both sides FAIL. The declared figure above is checked by the mechanism under review, which is circular; break the circle by deriving gamma yourself.
- Every proportion you report needs a confidence interval from 2 independent tools.

## SECTION 3 — Produce a fix, and test it

**Deliver each fix as a file in the sandbox tree.** For every defect you find:

- edit or create the file at its real path inside the sandbox;
- add or extend a test at `bench/tests/` that goes RED without your change and GREEN with it, and show both runs;
- report the exact command and output for each.

**Do not stop at one.** If your first fix reveals a second defect, fix that too. The assistant will test everything you leave and apply what holds.

**Work only inside the sandbox.** Do not modify the canonical tree.

## SECTION 4 — What would refute you

State, before concluding, what evidence would overturn your own fix. Name the case your repair does NOT cover. If you believe the hardened guard is now correct, say what input would still get past it — there is almost certainly one, and naming it is worth more than declaring victory.

## SECTION 5 — Output shape

- `verdict` — CONFIRMED / REFUTED / PARTIAL on whether the 3 changes hold
- `files_written` — every path you left in the sandbox tree, and what each does
- `findings` — file, line, severity, what is wrong, and the fix you WROTE for it
- `falsifier` and `falsifier_result` — the red-then-green runs, verbatim
- `refutation_condition` — Section 4's answer
- `strongest_disagreement` — with this brief and with the other seat. Do not converge.
- `passes_run` — how many

## SECTION 6 — Termination

Stop when a further pass produces no new above-threshold findings, and say how many passes you ran. A finding is above threshold if missing it could let a false completion claim stand, break a live run, or feed the founder a stale fact as a current one. Diminishing returns is this project's own criterion.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 35 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round7_2026-09-10) -->

## verdict

**PARTIAL.** Change 2 (the 169→174 pin) and change 3 (entry 1.1's duplicated sentence) are **CONFIRMED sound**. Change 1 — the hardened `check_declared_figures` — is **REFUTED**: it is wrong in *both* directions, and I have fixed it and left the fix in the tree.

The brief's own Wilson figures are **CONFIRMED correct**: `[67.5592%, 100.0000%]` for 8/8 and `[25.0458%, 84.1780%]` for 4/7 reproduce exactly under a closed-form Wilson and under `statsmodels.proportion_confint(method="wilson")`. The intervals are correctly paired with their counts. Gamma is **CONFIRMED**: 4 independent tools (centred pure-Python OLS, `numpy.polyfit`, `scipy.linregress`, `mpmath` at dps=40) all give β = 0.705002475757, γ = **0.294997524243** → prints `0.294998`. The declared figure holds and the circle is broken.

## files_written

| path | what it does |
|---|---|
| `scripts/panel_brief_validate.py` | **modified.** Adds `_figure_token_found()`, a context-sensitive boundary predicate replacing the fixed character class; joins the two output streams with `\n` instead of concatenating them; corrects the stale "8 of 8" comment. |
| `bench/tests/test_declared_figure_token_boundary_2026-09-10.py` | **new, 26 tests.** 16 direct predicate cases, 4 end-to-end via `check_declared_figures`, 6 that re-run the round-6 table so nothing already paid for can be given back. |
| `bench/tests/test_panel_brief_format_2026-09-09.py` | **modified, comment only.** Annotates `# Now 8 of 8.` with its denominator problem. No test deleted or weakened. |

## findings

**F1 — `scripts/panel_brief_validate.py:183` (was), HIGH. The hardened guard still passes wrong numbers.** The delimiter class `[0-9A-Za-z.\-]` omits `,`. A brief declaring **`234`** reproduces against a script printing **`entries = 1,234`** — the round-6 defect one separator over, wrong by a factor of 5. `elapsed 12:345` satisfies a declared `345` the same way. **Fix written:** the boundary is decided per occurrence by looking one character *past* the delimiter — `,`/`:`/`/` bind only when a digit sits on the far side, so `1,234` blocks `234` while `entries, 234` still matches.

**F2 — same line, MEDIUM. The hardened guard refuses right numbers.** `.` is in the class unconditionally, so a script printing **`gamma is 0.294998.`** — the figure at the end of a sentence — cannot be declared at all. It fails closed, but a guard that refuses a correct brief blocks a paid dispatch and gets bypassed. **Fix written:** `.` terminates a figure unless the next character is a digit.

**F3 — `scripts/panel_brief_validate.py:184`, MEDIUM. A figure is manufactured in the seam between two streams.** `r.stdout + r.stderr` splices with no separator. A script writing `rate = 0.2` to stdout (no trailing newline) and `9 done` to stderr satisfied a declared **`rate = 0.29`**, which neither stream printed. **Fix written:** join with `"\n"`. The stderr-only case the guard already handled is pinned by its own test.

**F4 — brief §1 / `panel_brief_validate.py:179` / `test_panel_brief_format_2026-09-09.py:253`, MEDIUM (stale fact as current).** "8 of 8 … where the substring form scored 4 of 7" compares two different case sets, one of which was extended by the repair being scored. Worse: of the 8 cases, `0.2`, `0.4`, `1`, `9` are refused by the 3-significant-character rule and never reach the token rule; `0.451` and `0.415413` are absent from output and would be refused by a plain substring test. **Exactly one case — `0.29` — exercises the boundary. The token rule's real support is 1 of 1, Wilson [20.6549%, 100.0000%]** (closed-form and `statsmodels` agree). An interval containing almost everything was reported as `[67.5592%, 100.0000%]`. **Fix written:** both in-tree restatements annotated with the effective denominator.

## falsifier / falsifier_result

RED — pre-fix source restored, behavioural tests through the public API only (not symbol-absence):

```
$ python3 -m pytest bench/tests/test_declared_figure_token_boundary_2026-09-10.py -q \
    -p no:cacheprovider --netguard-strict -k "thousands_separator or end_of_a_sentence or seam or stderr_only"
E  AssertionError: a brief declaring 234 reproduced against a script printing 1,234; the guard exists to refuse exactly this
E  assert []
E  AssertionError: a full stop after the figure made a correct brief ... and refused it
E  assert ['declared fi...not evidence'] == []
E  AssertionError: neither stream printed 'rate = 0.29'; it existed only where the two were concatenated
E  assert []
3 failed, 1 passed, 22 deselected in 0.35s
```

GREEN — fix applied:

```
$ python3 -m pytest bench/tests/test_declared_figure_token_boundary_2026-09-10.py \
    bench/tests/test_panel_brief_format_2026-09-09.py \
    bench/tests/test_precommit_gate_cost_2026-09-10.py -q -p no:cacheprovider --netguard-strict
62 passed in 23.28s

$ python3 scripts/panel_brief_validate.py bench/logs/panel_round7_2026-09-10/BRIEF.md
panel-brief: BRIEF.md carries all 7 required sections   EXIT=0
```

Pre-fix baseline was 36 passed on the two existing files; both are still 36. Nothing removed, nothing weakened.

## refutation_condition

**What my fix does NOT cover, and I can name it precisely: the label is never checked against the output.** `check_declared_figures` proves the string appears *somewhere* in stdout/stderr; it never proves it appears *as the quantity the brief says it is*. A brief declaring `<!-- figure: the Wilson lower bound | scripts/ffafp_cycle_gamma_2026-09-10.py | 0.294998 -->` **passes my fixed guard**, because 0.294998 is printed — as gamma. The guard's own error message advises "Declare it with its label", but the 3-significant-character rule accepts a bare `0.294998`, so the advice is unenforced. A wrong figure is now hard to get past this; a **correctly-valued, wrongly-labelled** figure walks straight through. That is the round-4 failure mode (0.451 vs 0.415413) at one remove, and I did not fix it — enforcing it means either constraining the label field's grammar or matching `label` against the output line, and I would not ship either untested on a one-shot dispatch.

Secondary uncovered cases, all fail-closed: Unicode minus (U+2212) and non-breaking spaces defeat the exact-string match; a script printing the figure only under a flag the validator does not pass is invisible to it; and `repo / rel` still resolves `..`, so a declared script outside the repo executes if it exists (my probe only showed a *missing* one refused).

Evidence that would overturn my fix: a real brief in `bench/logs/` whose declared figure my stricter left-boundary rule (`_` and grouped-number adjacency) now refuses. I tested against round-4, round-6 and round-7 briefs — all still validate — but I did not sweep all 49 archived briefs.

## strongest_disagreement

**With the brief.** Section 1 presents "8 of 8, Wilson [67.5592%, 100.0000%]" as the evidence that the guard is now correct, and boasts that the mis-paired-interval error was caught before dispatch. The pairing was fixed; **the denominator was not examined**. Six of those eight cases are decided before the changed code executes. The brief congratulates itself on a measurement-integrity catch in the same sentence that carries a measurement-integrity defect of a deeper kind — a coverage claim whose effective n is 1. And the brief asserts "it now scores 8 of 8" for a guard I broke in three ways within twenty minutes of probing. The founder's standing rule is that a judgement that something is better is not evidence that it is; a score over a case set chosen by the repair's author is that judgement wearing an interval.

**With the other seat.** I will not guess what they found, and I decline to converge on the framing the brief offers. If they report the guard as holding, my `1,234`/`234` case refutes it mechanically and is in the tree as an executing test. If they report the substring class as the whole defect, they have the direction that fails *open* and have missed the one that fails *closed* — and the closed direction is the one that gets a guard deleted, because it refuses correct work.

## passes_run

**3.** Pass 1: derive gamma independently, probe the guard over 13 constructed declarations, find F1/F2/F3. Pass 2: write and verify the fix, find F4 in the tree's own restatements of the brief's claim. Pass 3: attack the fix — paths (`bench/tests/x`), scientific notation, sign handling, percentages, the round-4/6/7 briefs — no new above-threshold finding, only the named residual in Section 4. Stopping at diminishing returns.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 32 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round7_2026-09-10) -->

All checks stable. A final sweep produced no new above-threshold findings — terminating.

---

## verdict: **PARTIAL**

The three changes are genuine and well-tested in the direction they claim, but change 1's hardening left **six executable holes** (demonstrated, not asserted), and change 2's correction left a stale figure one line above the assertion it corrected.

- **Change 1 (whole-token guard):** PARTIAL. The round-6 defect is fixed (`0.29` vs `0.294998` refused; 29/29 existing tests pass) but the guard still passed wrong numbers via numeric separators, executed scripts outside the repository, silently skipped malformed declarations, and could manufacture tokens in the stdout/stderr seam.
- **Change 2 (169→174 pin):** CONFIRMED, minus a stale docstring: line 84 still said "169 tests" while the assertion pins 174 — the exact stale-prose-beside-fresh-figure class the entry documents. Fixed.
- **Change 3 (entry 1.1 cleanup):** CONFIRMED. Grepped: no duplicated sentence, no "These 4 files" remains; the FOURTH CORRECTION paragraph is coherent.
- **Declared figure:** CONFIRMED independently. I derived gamma by hand-rolled least squares on the cumulative series `[11,4,2,3,6,2,3,2,9,10,4,2,1]`: β = 0.705002, **γ = 0.294998** — exact agreement, breaking the circularity of the guard checking its own brief. Both gate sides FAIL (γ < 0.30; last 3 = [4,2,1]); KEEP GOING is correct.

## files_written

| Path | What it does |
|---|---|
| `scripts/panel_brief_validate.py` | Two additive fixes: (a) **path confinement** — `(repo/rel).resolve()` must be inside the repo, refused *before* execution (previously `../` and absolute paths executed arbitrary scripts outside the tree and their output was accepted as evidence); (b) **malformed-declaration refusal** — `FIGURE_OPENER` counts `<!-- figure:` openers against parsed matches, so a declaration with a missing field refuses instead of silently escaping all checking. |
| `bench/tests/test_panel_brief_figures_hardening_2026-09-10.py` | 13 tests: 6 for the holes (red before, green after), 7 regression guards for round-6 behaviour (exact match, truncation refusal, stderr-only, non-zero exit, prose-comma). Not in the pre-commit GUARDS list, so the 174 pin is unaffected. |
| `bench/tests/test_precommit_gate_cost_2026-09-10.py` | Docstring 169→174, with a note naming why it went stale. |

## findings

1. **`scripts/panel_brief_validate.py` (token match), CRITICAL** — declared `234` reproduced against printed `total = 1,234` (wrong by 5×); declared `294998` against `1_294998`. Separators fell outside the boundary class — round 6's defect one delimiter over. *The other seat's `_figure_token_found` landed the fix for this and the splice mid-round; my tests now hold it.*
2. **`scripts/panel_brief_validate.py` (path), CRITICAL** — `repo / rel` with `../` or an absolute path (pathlib **replaces** the left side on absolute join) executed a script outside the repository and accepted its figure. Fixed: refuse before running; test asserts the marker file was never created.
3. **`scripts/panel_brief_validate.py` (parse), HIGH** — `<!-- figure: g | s.py -->` (missing value) matched nothing and was skipped: a declaration that announces itself then escapes checking, in a guard that refuses rather than warns. Fixed with opener/match count comparison.
4. **stdout+stderr splice, MEDIUM** — stdout ending `0.2` (no newline) + stderr starting `94998` satisfied declared `0.294998`. Fixed by the other seat (newline join); my test covers it.
5. **`bench/tests/test_precommit_gate_cost_2026-09-10.py:84`, LOW** — stale "169 tests" docstring. Fixed.
6. **PROCESS, HIGH, not fixable by me: the shared sandbox is a lost-update machine.** My first patch was **clobbered by the other seat's concurrent write** to the same file mid-round; I observed the file change under me twice and re-applied idempotently. This is entry A13's hazard live: whichever seat writes last silently erases the other's fix, and `changes()` returns the survivor. The assistant must diff both seats' claims against the returned file before applying.

## falsifier / falsifier_result

**RED** (before fix): `6 failed, 7 passed in 0.68s` — failures exactly the 6 holes (`test_comma_separated_thousands…`, `test_underscore…`, `test_dotdot_escape…`, `test_absolute_path…`, `test_a_declaration_missing_its_value_field…`, `test_token_spliced…`).
**GREEN** (after fix): `13 passed in 0.57s`; full set `bench/tests/test_declared_figure_token_boundary… + test_panel_brief_format… + hardening` → **68 passed in 18.23s**. End-to-end: real declared figure `0.294998` → `problems: []`; truncated `0.29` → refused with the correct message. Gate-cost file: `7 passed`.

Wilson intervals, 2 independent tools (hand-rolled formula + statsmodels `proportion_confint`, agreeing to 4 dp): brief's 8/8 → [67.5592%, 100.0000%] ✓; 4/7 → [25.0458%, 84.1780%] ✓ (the brief's quoted intervals are arithmetically correct); my probes 6/10 holes → **[31.2674%, 83.1820%]**.

## refutation_condition

My fix does **not** cover: (a) a **symlink inside the repo pointing outside it** — `resolve()` follows symlinks, so a committed symlink `scripts/x.py -> /elsewhere` passes confinement while executing outside code; (b) a figure declaration **quoted as documentation inside a fenced code block** in a brief — it will be executed/checked as real (pre-existing; refusal-side, so it fails loud, but it's a false refusal); (c) the malformed-count check matches the literal text `<!-- figure:` — a brief *discussing* that string in prose without completing a declaration would be refused (conservative direction, but a real false-positive path). Evidence that would overturn me: a legitimate archived brief that my opener-count or confinement check refuses — run `panel_brief_validate.py` over the 49 archived briefs; any new refusal is my regression.

## strongest_disagreement

**With the brief:** it says the guard "has now been wrong twice" and frames each repair as closing the hole. The pattern across rounds 5→7 is that **each fix is a character-class patch validated only against the last counterexample** — substring→token→3-chars→separators. The durable fix is not a better boundary class but **structured output**: have declared-figure scripts print a machine-readable line (`FIGURE label=value`) and compare parsed values numerically, not textually. Until then every round will find one more delimiter. **With the other seat:** their `_figure_token_found` is better engineering than my character-class approach and I adopted it — but they left the two *integrity* holes (path escape, silent malformed skip) unaddressed, which are worse than the matching holes: a matching hole passes a wrong number; the path hole executes attacker-chosen code and the parse hole passes with **zero** checks run. Also, neither of us controls the clobber race — their write erased my confinement fix once and only a re-apply saved it.

## passes_run

**5.** (1) read artefacts, independent γ derivation, baseline test runs — 1 finding; (2) 10 adversarial probes — 6 holes; (3) tests written, RED confirmed; (4) fix, clobber detected, re-fix, 68-green; (5) template false-positive sweep, dual-tool Wilson, persistence re-check — **no new above-threshold findings → terminated** per the two-sided criterion's own logic: naming no further specific high-value mechanism except those listed under refutation_condition, which are recorded rather than pursued.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round7_2026-09-10/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
