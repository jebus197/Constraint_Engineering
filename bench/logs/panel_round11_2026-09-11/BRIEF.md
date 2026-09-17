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
