# PANEL BRIEF — round 9: adjudicate `exp39-experimental`, and DELIVER YOUR FIX AS A FILE

<!-- figure: exam answer keys reachable only from the branch | scripts/exp39_branch_inventory_2026-09-10.py | ANSWER KEYS: 5 -->
<!-- figure: paths in the branch history and nowhere in main's | scripts/exp39_branch_inventory_2026-09-10.py | no main-history tree: 12 -->

## SECTION 0 — THE DELIVERY RULE, AND ONE HARD PROHIBITION

**Founder ruling:** *"they need to supply fixes, not just problems!"* A finding without a fix is not a deliverable, and a fix in prose is not delivered. **Write it INTO the sandbox repository tree at its real path and leave it there.** `bench/panel_sandbox.py:teardown` destroys everything outside it.

**THE PROHIBITION. DO NOT DELETE A GIT REF, and do not propose a command that does.** Deleting a ref is one of 3 categories the founder reserves to himself in person. You may recommend a disposition; you may not enact one, and any patch containing `git branch -D`, `git tag -d`, `git push --delete`, `git gc --prune`, `git reflog expire` or `filter-repo` will be refused whole.

## SECTION 1 — The question, in his words

*"Get Fable and CC2 to look at this with you, decide which elements on this branch remain useful and should be adopted in light of everything else we have done and which should be considered superseded."*

## SECTION 2 — What is measured so far

`scripts/exp39_branch_inventory_2026-09-10.py` establishes the facts. Run it.

1. **The branch is LOCAL.** `git ls-remote --heads origin` returns `refs/heads/main` alone. Nothing on this branch was ever published.
2. **107 commits** are unreachable from `origin/main`.
3. **The tip tree differs from main by exactly 1 path:** `bench/reference_runner_v2.py`. The founder said, separately and recently, *"Look at the v2 runner too."*
4. **12 paths exist in the branch's unreachable history and in no main-history tree, and 5 of them are EXAM ANSWER KEYS** — chemistry, engineering, physics, biology, factorial — with the 6 exam targets they belong to and 1 note.
5. Each key is reachable from `origin/main` in **0 commits**.
6. The branch's own commit `eecdb0f` is titled *"CLOSE THE ANSWER-KEY EXPOSURE"* and names the residual: *"git-history recovery by deliberate archaeology"*.
7. I have created the tag `exp39-experimental-pinned-2026-09-10`. It creates a ref and removes nothing, and the entry itself recommends pinning before any disposition.

## SECTION 3 — Attack these specifically

1. **Is `bench/reference_runner_v2.py` superseded or not?** v3 is the active runner. Does v2 hold anything v3 lost? Compare them by EXECUTION where you can, not by reading. This is the founder's own question.
2. **My reachability claim.** I assert the keys are reachable from the branch and from no remote ref. Break that. Is there a reflog entry, a stash, a note, another local ref, or a packed object that reaches them by another route? If so the exposure surface is wider than I said.
3. **My tag.** It pins 107 commits AND the 5 keys. I judged that correct because the branch ref already reached them and the alternative is losing 107 commits. Argue the other side if you think it is wrong — and if you do, say what you would do instead WITHOUT deleting a ref.
4. **The 12-path figure.** I compare against the last 400 commits of main's history for tractability. That is a cut-off, and a cut-off can manufacture a difference. Check whether any of the 12 appears earlier in main than 400 commits back, and if so, fix `exp39_branch_inventory_2026-09-10.py`.
5. **What is worth adopting.** Beyond the runner: 107 commits of work. Name anything that should come to main, with the evidence that it is not already there.

## SECTION 3B — EVERY FIX MUST BE TESTED, BY YOU, BEFORE YOU HAND IT BACK

**A fix you have not executed is a hypothesis.** Every fix you leave in the tree must arrive with a runnable falsifier that you have RUN, and the brief must carry its output. Put the test at `bench/tests/<name>.py`, run it with `python3 -m pytest -q <path>`, and quote the result line verbatim in your findings.

**The test must be able to FAIL.** Show that: break the thing your fix repairs, run the test again, and quote the red output too. A test that passes against the broken state proves nothing, and this project found 8 of its own mutation tests vacuous that way on 2026-09-09. If your fix is to a measuring script, the control is a case whose answer you already know.

## SECTION 4 — What would refute YOU

For every finding, state what evidence would overturn it. A finding naming no such evidence is an opinion, and this project does not act on opinions. If you disagree with a claim in Section 2, say what you ran and what it returned.

## SECTION 5 — When to stop

**Diminishing returns.** Stop when another pass produces no new above-threshold finding. Above threshold means: it could put a wrong number in front of the founder, cause a ref to be mishandled, or lose work that exists nowhere else. Do not pad to a count; 2 findings with working fixes beat 9 with none. Do not report style or comment density.

## SECTION 6 — The output shape, field by field

Return **Markdown**, in this order:

1. **`VERDICT`** — `ADOPT`, `SUPERSEDED`, or `SPLIT`, for the branch as a whole, in the first line.
2. **`FILES I LEFT IN THE TREE`** — repo-relative paths you created or edited. `NONE` plus a reason if empty; an empty list without one is a failed round.
3. **`FINDINGS`** — numbered. Each: **WHAT** (1 sentence), **WHERE** (`path:line` or a git object), **EVIDENCE** (the exact command and its output, quoted), **FIX** (the path you wrote it to), **WHAT WOULD REFUTE THIS**, **SEVERITY** (0.0 to 1.0).
4. **`ADOPT / SUPERSEDE`** — a per-element table over what the branch uniquely holds, with the evidence for each call.
5. **`FIGURES I RE-RAN`** — each declared figure, what you got, and whether it matched.
6. **`WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1`** — preserved, never smoothed. Say so explicitly if you agree with everything.
7. **`WHAT I DID NOT CHECK`** — the honest boundary of your pass.

Do not return a summary in place of the full output.
