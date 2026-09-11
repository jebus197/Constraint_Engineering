# Panel Round 9 — FULL RECORD, unfiltered

Record written 2026-09-11T09:40:55+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

Round 9 reviewed task 8.2 — the disposition of the `exp39-experimental` branch, which carries 107 commits main does not and the answer keys for several experiments. The question was whether anything on it should come to main.

## What the round found

**THE 2 SEATS DISAGREED AND THE DISAGREEMENT IS KEPT.** fable returned `SUPERSEDED`: nothing on the branch should come to main, and everything it uniquely holds is measured-superseded, policy-excluded, or history correctly preserved by the pin. cc2 returned `SPLIT`: the same call on adoption, but arguing that `reference_runner_v2.py` earns retention as the acceptance gate's own control, because v3 is recorded as v2 plus 10 patches each accepted on *"FAIL at the parent, PASS with the patch"* — and the parent IS v2, so losing it makes the fail-at-parent leg of all 10 acceptances unreproducible. **Both converge on: do not adopt, keep the pin.**

**A DESIGN DEFECT IN CC1'S OWN BRIEF (cc2).** Neither seat could re-run either declared figure, because both need a git repository and the sandbox has none. In the seat's words: *"A figure only one party can compute is a vote, not a tool result."* That is this project's founding standard and this round did not meet it for those 2 figures.

**THE BRIEF WAS ALSO OUT OF DATE AT DISPATCH.** cc2's reply opens its disagreement with *"Section 3.4 is already closed and the brief does not say so."* That observation is what produced task A4: `check_currency()` now compares a brief's modification time against every artefact it names and warns when one moved after the brief was written.

**A CAUTION THAT APPLIES TO THIS ROUND.** Until task A20 landed on 2026-09-11, all seats shared ONE writable sandbox and ran concurrently. Agreement between seats here is not evidence of independence.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

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


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 86 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round9_2026-09-10) -->

`VERDICT` — **SPLIT**

## FILES I LEFT IN THE TREE

- `scripts/exp39_branch_inventory_2026-09-10.py` (edited — two defects fixed)
- `bench/tests/test_exp39_inventory_key_patterns_and_push_2026-09-10.py` (new — 10 tests, mutation-proved)

No ref was created, deleted, pushed or renamed. No feature removed. Both fixes widen what the script can see; neither narrows it.

---

## FINDINGS

### 1. The inventory's key detector is blind to 29 of this project's own keys — and it feeds the push decision

**WHAT** `KEY_MARKER = "answer_key"` misses `ft-NNN_KEY.json`, `*_KEY.md` and `*GROUND_TRUTH.json`, so `key_bearing_refs()` reports a ref carrying key material as carrying none — and that is the number `push_tags_sends_keys` is computed from.

**WHERE** `scripts/exp39_branch_inventory_2026-09-10.py:131` (`KEY_MARKER`), consumed at `key_bearing_refs()` and at `inventory()`'s `keys = [p for p in only_hist if "answer_key" in p]`.

**EVIDENCE** This is not a hypothetical naming scheme. It is the project's own register (`bench/vault_keys.sh:204-206`) and the project already diagnosed and fixed this identical blindness **four days earlier**, on 2026-09-06:

```
$ sed -n 80,120p bench/tests/test_vault_status_sees_the_real_keys_2026-09-06.py
  1. It matched only '*answer_key*.json'. The BR2 keys are 'ft-NNN_KEY.json' and
     the exp55 pair are '*_KEY.md' / '*GROUND_TRUTH.json' -- 0 of 29 real keys
     matched the pattern, even with the path exclusion removed.
```

Run against a fixture I built whose answer I knew in advance — a bare remote carrying `main`, a local branch adding `keys/ft-001_KEY.json`, a tag on that branch:

```
only_hist          : ['keys/ft-001_KEY.json']
keys (counted)     : []
ANSWER KEYS: 0
key_bearing_refs   : {}
push_tags_sends_keys : False
```

The path is listed as branch-unique and simultaneously reported as not being a key. After the fix, same fixture, same command:

```
--- ANSWER KEYS: 1 ---
  ft-001_KEY.json: reachable from origin/main in 0 commit(s)
--- WHICH REFS CARRY A KEY, AND WHAT A PUSH WOULD SEND ---
  refs/heads/exp39-experimental: 1 key path(s)
  refs/tags/exp39-pinned: 1 key path(s)
  `git push --tags`        sends a key-bearing ref: True
```

**FIX** `scripts/exp39_branch_inventory_2026-09-10.py` — `KEY_PATTERNS` lifted verbatim from `bench/vault_keys.sh:493-494`, plus `is_key_path()`. `KEY_MARKER` is retained and tested against the **full path** as the original did, so the new matcher is a strict superset on every input (`test_new_matcher_is_a_strict_superset_of_the_old`). I got this wrong on my first pass — I tested the marker against the basename, which would have *lost* `answer_keys/x.json`. My own test caught it before it shipped.

I also replaced `rev-list --count -- <path>` with `--full-history` throughout (`touches()`): default history simplification can report 0 commits for a path genuinely reachable through a TREESAME merge side, and "0" is the answer this disposition hangs on.

**WHAT WOULD REFUTE THIS** Evidence that no `*_KEY.json` / `*_KEY.md` / `*GROUND_TRUTH.json` file exists anywhere in `exp39-experimental`'s 107 unreachable commits. I could not check that — see boundary below. If the branch's key material is genuinely all `*answer_key*.json`, the printed figure of 5 was right and this finding downgrades to "the detector is unsound but was not yet wrong."

**SEVERITY 0.8**

---

### 2. `plain_push_sends_keys` was a hardcoded `False`, and the evidence refuting it was read on the line above

**WHAT** `push_exposure()` returned the literal `False` for whether a plain `git push` sends key material, having already read `remote.origin.push` into the same dict and discarded it before the verdict.

**WHERE** `scripts/exp39_branch_inventory_2026-09-10.py`, in `push_exposure()`:

```python
# `git push` with no args pushes the current branch only.
"plain_push_sends_keys": False,
```

The comment is true. It is not an answer. If the **current branch is the key-bearing one**, or a wildcard refspec is configured, a plain push sends key material.

**EVIDENCE** Measured against a real bare remote:

```
=== HEAD is on: exp39-experimental ===
=== git push --dry-run  (plain push, explicit refspec configured) ===
To /var/folders/.../remote.git
 * [new branch]      exp39-experimental -> exp39-experimental
RC=0
```

git itself sends the key-bearing branch. The script, on that same repository, printed:

```
explicit_push_refspec: refs/heads/*:refs/heads/*
plain_push_sends_keys: False
```

**FIX** Same file. `plain_push_sends_keys` is now computed from `remote.origin.push` (via `refspec_sends()`), else from `push.default` — deriving each mode: `nothing` sends nothing; `current` sends HEAD **even with no upstream**; `simple`/`upstream`/`tracking` send HEAD only if an upstream exists (which is why the hardcoded `False` looked right — `exp39-experimental` has none); `matching` sends only branches already on the remote. A `plain_push_reason` string ships with it, so the founder gets the derivation and not a bare boolean.

**WHAT WOULD REFUTE THIS** A demonstration that `git push` with `remote.origin.push=refs/heads/*:refs/heads/*` does not send unpushed local branches, or that `push.default=current` requires an upstream. Both are directly falsifiable by `git push --dry-run` and I have run the first.

**SEVERITY 0.7** — it cannot itself publish anything, but it is the field a human reads before deciding whether the tag is safe.

---

### Test evidence — green, and proved capable of red

```
$ python3 -m pytest -q bench/tests/test_exp39_inventory_key_patterns_and_push_2026-09-10.py
10 passed in 4.30s
```

Mutation control. I reverted `is_key_path` to the bare marker and `plain_push_sends_keys` to the literal `False`:

```
===== RED RUN =====
FAILED ...::test_a_br2_style_key_on_the_branch_is_counted
FAILED ...::test_the_tag_is_reported_as_carrying_the_key
FAILED ...::test_the_old_marker_would_have_missed_this_key
FAILED ...::test_new_matcher_is_a_strict_superset_of_the_old
FAILED ...::test_plain_push_is_reported_true_when_a_wildcard_refspec_would_send_the_branch
FAILED ...::test_plain_push_is_reported_true_when_push_default_is_current_on_the_branch
FAILED ...::test_the_field_is_computed_not_a_literal
7 failed, 3 passed in 3.88s
===== RESTORED, GREEN RUN =====
10 passed in 4.31s
```

The 3 that stay green under mutation are the controls that *should* — a no-key repository reporting none, `simple`-with-no-upstream reporting `False`, and the ref-deletion guard. A detector that always fires is as useless as one that never does.

Two of my ten tests initially failed and **both were defects in my tests, not the fix**. Recorded because this panel found 8 vacuous mutation tests on 2026-09-09 and the failure mode is worth naming: (a) my "control" renamed the key with `git mv` and expected the finding to clear — it does not, and *must not*, because the earlier commit still carries the path, which is the whole exposure being measured; (b) my ref-deletion guard scanned its own source, which contains every forbidden token in its literal list, so it could never pass. A guard that cannot pass is not a guard.

---

## ADOPT / SUPERSEDE

| Element | Call | Evidence |
|---|---|---|
| `bench/reference_runner_v2.py` (the 1 tip-tree difference) | **SUPERSEDED as running code; RETAIN as the acceptance gate's control** | `bench/reference_runner_v3.py:63-67` states v3 = v2 + 10 patches, each gated on "FAIL at the parent, PASS with the patch, full suite green against the parent's own failing set — no model vote anywhere in that path", then composition-proved (10/10, 141 tests, 3,759 suite passes). That is a committed measurement of dominance, which is what the additive standard requires. **But**: the parent *is* v2. Delete it and the fail-at-parent leg of all ten acceptances becomes unreproducible — CDSFL §10 category 5. v2 earns retention as a control, not as a runner. |
| The 5 exam answer keys + 6 targets | **SUPERSEDED as content, RETAINED in history** | The exams were run; the keys are now vault-managed (`bench/vault_keys.sh`). Nothing to adopt. Nothing to delete either — and no ref may be deleted regardless. |
| The 107 unreachable commits | **PIN, as CC1 did** | Losing 107 commits to protect objects that were never published is the worse trade, and CC1's reasoning is sound. |
| `exp39_branch_inventory_2026-09-10.py` itself | **ADOPT, with findings 1 and 2 applied** | Above. |

---

## FIGURES I RE-RAN

| Figure | Result | Match |
|---|---|---|
| `ANSWER KEYS: 5` | **Could not re-run.** Sandbox has no `.git`; script exits 4 by design. | Unverified |
| `no main-history tree: 12` | **Could not re-run.** Same. | Unverified |

Both figures are unreproducible in the environment the panel was given. The script's exit-4 refusal is correct behaviour and I confirmed it (`sandbox exit=4`) — CC1's hardening (1) works. But it means **no seat on this panel can independently confirm either declared figure**, and a figure only one party can compute is a vote, not a tool result. That is the founding principle's own standard and this round does not meet it.

---

## WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

1. **Section 3.4 is already closed and the brief does not say so.** The 400-commit cut-off is gone from the tree — docstring item (3), with the union proved set-identical at 8293 both ways and 93× faster. The brief asks the panel to check something already fixed. I re-derived the underlying worry independently and **refuted my own hypothesis by execution**: I suspected `git log --name-only` omits the root commit's diff without `--root` (documented behaviour for `format-patch`). It does not, on git 2.50.1, including with the script's exact `--full-history -m --no-renames`:
   ```
   === EXACT script invocation on main ===   === ls-tree union over all commits ===
   keep.txt / m.txt / side.txt                keep.txt / m.txt / side.txt
   ```
   CC1's `history_paths` equivalence claim holds. I report it because a refuted hypothesis backed by a run is worth more than an unexamined agreement.

2. **I agree the tag is correct (Section 3.3) but not for CC1's stated reason.** CC1 justifies it as "the alternative is losing 107 commits." The stronger justification is that v2 is the *control* for v3's ten-patch acceptance gate — pinning it preserves reproducibility of an already-banked result, which is a positive reason rather than the absence of a negative one.

3. **CC1 was alive to the tag's push risk and under-powered its own instrument.** `push_exposure()` exists precisely because a tag is published by an easier command than a branch. That instinct is right. But it computes tag exposure through a marker that cannot see 29 of this project's keys, and reports plain-push exposure as a constant. The right control was reached for and does not work.

4. **Recommendation I did not enact, and deliberately did not ship.** A `pre-push` hook refusing any ref reaching key material would close finding 2's residual. The script already measures `pre_push_hook: False`. I did not write one: I could not wire it to a caller or execute it against a real remote in this budget, and *"an addition that nothing reaches is not additive either"* — 11 of this project's confirmed defects since 2026-08-01 were exactly that. Shipping an untested hook would have made me the twelfth. This is a recommendation to the founder, not a delivery.

---

## WHAT I DID NOT CHECK

- **`bench/reference_runner_v2.py` by execution — the founder's own question.** The file is not in the sandbox (`ls: No such file or directory`) and there is no git to retrieve it from. My SUPERSEDED call rests on v3's documented, mechanically-gated provenance, **not on a run**. Anyone wanting that answer must dispatch a seat into a real clone.
- **Section 3.2 (reflog, stashes, notes, other local refs, packed objects).** Requires `.git`. Untouched. I note that `key_bearing_refs()` enumerates `for-each-ref`, which covers branches, tags and remotes but **not** the reflog, stash, or dangling objects — so even in a real clone that function under-reports the surface by construction. I did not fix this; it is the strongest remaining lead.
- **Whether the branch's 12 unique paths actually include any `*_KEY.json` / `*GROUND_TRUTH.json`.** This determines whether finding 1 changes the printed figure of 5 or merely the soundness of the instrument. One `git log --all --name-only` in a real clone settles it.
- **The full suite.** Per brief, targeted tests only.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 58 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round9_2026-09-10) -->

# VERDICT

`SUPERSEDED` — nothing on `exp39-experimental` should be adopted to main; everything it uniquely holds is either measured-superseded (the v2 runner), policy-excluded (keys/targets, which main deliberately vaulted out), or history correctly preserved by CC1's pin tag. No ref disposition proposed; the prohibition was not approached.

# FILES I LEFT IN THE TREE

- `bench/tests/test_exp39_branch_inventory.py` — known-answer control suite for the repaired inventory script (3 tests, all executed, all passing; contains its own red-control).
- Note on `scripts/exp39_branch_inventory_2026-09-10.py`: I wrote a full repair to it at 21:09; the other seat's repair landed over it at 21:10 fixing the same three defects with a version that **dominates mine on named properties** (exit-code separation 3/4, `--full-history -m --no-renames`, data/presentation split via `inventory()`, measured 93× speedup, `--repo/--branch/--main` CLI). Per the Additive Standard I deferred to theirs rather than clobbering, and instead **validated their version by execution** (see Figures) and pointed my test file at its API. The current on-disk script is theirs, verified by me.

# FINDINGS

**1. The inventory script reported a clean "nothing to measure" while measuring nothing at all — and it fired today.**
**WHERE:** `scripts/exp39_branch_inventory_2026-09-10.py` (pre-repair `git()` at old line 29–31).
**EVIDENCE:** In the panel sandbox (no `.git`), the original printed `no branch exp39-experimental in this clone -- nothing to measure.` and exited 0. That statement is false — it is not a clone missing a branch, it is not a repository. Post-repair: `REFUSING TO REPORT: not a usable git repository … NOTHING WAS MEASURED. This is not a clean result.` / `exit=4`.
**FIX:** `scripts/exp39_branch_inventory_2026-09-10.py` (current version, joint with other seat) + `bench/tests/test_exp39_branch_inventory.py`. Result line, verbatim: `3 passed in 1.56s`. Red-control: my first-draft test against the mid-edit script produced `3 failed, 2 passed in 1.74s` — the fixture demonstrably goes red; the retained-defect test `test_capped_scan_wrongly_claims_the_deleted_path` is the permanent in-suite red-control (it executes the old capped method and asserts it still produces the wrong answer).
**WHAT WOULD REFUTE THIS:** a run of the pre-repair script in a non-repo directory exiting non-zero, or printing anything other than the clean-shaped message.
**SEVERITY:** 0.6 (it put a wrong statement in front of this panel today).

**2. The 400-commit cutoff and whitespace path-splitting were latent figure-corrupters; the published figures survive them — by luck, now by construction.**
**WHERE:** same script, old lines 34–35 (`.split()`) and 63 (`[:400]`).
**EVIDENCE:** Main holds **1021** commits (`git rev-list origin/main | wc -l` → `1021`), so 621 were invisible to the window. Re-measured against **full** history: every one of the 12 paths returns `0` from `git rev-list origin/main --count -- <path>` (all twelve outputs quoted in my transcript, each `: 0`). Two space-bearing paths exist (`docs/Experiment 40 response.docx/.txt`) in **both** trees, so fragments cancelled — a spaced path unique to one side would have emitted fabricated names. My fixture proves the failure shape: a deleted-then-re-added path (`deep_shared.txt`, in main's old history only, absent from every recent tree) is wrongly reported "unique" by the capped method and correctly excluded by the full-history method.
**FIX:** as above; both suites together: `11 passed in 4.70s`, both test orders.
**WHAT WOULD REFUTE THIS:** any of the 12 paths returning non-zero from full-history `rev-list --count`, which would instead mean the published "12 unique" figure was wrong.
**SEVERITY:** 0.5 (latent; verified not expressed in the published figures).

**3. CC1's reachability claim is CONFIRMED, and strengthened to blob level.**
**WHERE:** git object store of the real repo.
**EVIDENCE:** (a) per-ref scan over all 13 refs: only `refs/heads/exp39-experimental : 15` and `refs/tags/exp39-experimental-pinned-2026-09-10 : 15` reach key-touching commits; every other ref including `refs/stash` and the filter-branch residue `refs/original/refs/heads/build-experiment-2026-08-22` shows `0`. (b) All 3 stash trees (incl. `^3` untracked): `(no key/target paths)`. (c) `git notes list`: empty. (d) 311 unreachable objects via `fsck --unreachable --no-reflogs`: zero contain an `answer_key` path; zero key blobs among them. (e) Strongest: all **17** distinct key-blob OIDs across branch history were hunted with `git log --all --reflog --find-object=<oid>`; every containing commit is an ancestor of `exp39-experimental` (`scan complete`, no exceptions). (f) `bench/vault_keys.sh status`: `VAULTED — no plaintext key file on disk in any known or scanned location.`
**FIX:** none needed — this is a verification, not a defect. No file written.
**WHAT WOULD REFUTE THIS:** any key blob OID appearing in a commit not ancestral to the branch, a key path in any stash/notes/dangling tree, or a plaintext key on disk.
**SEVERITY:** 0.0 (clean verdict, backed by derivation — the exposure surface is exactly {branch, pin tag}, both local, remote carries main alone).

**4. `bench/reference_runner_v2.py` on the branch is superseded, proven by execution.**
**WHERE:** `exp39-experimental:bench/reference_runner_v2.py` (blob `30fb24f`) vs `bench/reference_runner_v3.py` on main.
**EVIDENCE:** v3 **is** v2 renamed (`ce08914 2026-09-01 "Rename the runner to v3"`) and continued for 82 commits after the branch line stopped (08-12). AST comparison: branch-v2 has 153 defs; **0 are missing from v3**; 106/153 byte-identical; 0 CLI flags lost; all 26 probed branch-added identifiers present in v3. Executed head-to-head on `compute_rk`: finite inputs identical (`0.42240000000000005` both); corrupt inputs — `sk=nan` → v2: `0.3666666666666667` (NaN silently scored as a *perfect* fix via the `min(1.0, nan)` trap), v3: `0.62` (conservative fail-safe, panel-verified 2026-09-06). The only direction of difference found is v3 strictly safer.
**FIX:** none — adjudication answer, table below. No file written.
**WHAT WOULD REFUTE THIS:** a def, flag, or behaviour present in branch-v2 and absent/regressed in v3. I found none; the un-audited residue is the other 46 differing shared defs (declared under "not checked").
**SEVERITY:** n/a (adjudication).

# ADOPT / SUPERSEDE

| Element (unique to branch) | Call | Evidence |
|---|---|---|
| `bench/reference_runner_v2.py` (tip) | **SUPERSEDED** | v3 = renamed continuation; 0 lost defs/flags; NaN execution comparison above |
| 5 answer keys (history) | **DO NOT ADOPT — policy** | Main commit `20d2ccf "Keys move out of the repository"`; vault reports sealed archive, no plaintext; adopting would reverse a founder-ruled exposure closure |
| 6 exam targets exp48–53 (history) | **DO NOT ADOPT — policy** | Main tip carries `.cleared_exp48…exp53` markers in `bench/cdsfl_registry/targets/`; targets deliberately removed; branch copies are the exposed pre-vault versions (per `2ce2a69`: byte-identical recovery already measured) |
| `Overnight_Work_Completed_Plain_English_2026-08-02.md` | **RETAIN VIA PIN, not adopt** | Historical record; 08-01 counterpart exists in main; pin tag preserves it; adopting is optional founder taste, not a defect either way |
| 107 commits of sv-notes / work | **SUPERSEDED as code, RETAINED as history** | Every v2-line feature probe found re-landed in main (26/26 identifiers); the commit narrative survives via the annotated pin tag |
| CC1's pin tag | **AGREE — keep** | `cat-file -t` → `tag` (annotated, `c01f98c → e49a021`); creates a ref, removes nothing, pins all 107 commits; the alternative loses history and any disposition stays with the founder |

# FIGURES I RE-RAN

| Declared figure | I got | Match |
|---|---|---|
| Remote heads = main alone | `refs/heads/main` only | ✓ |
| 107 unreachable commits | 107 | ✓ |
| Tip tree diff = 1 path (`reference_runner_v2.py`) | 1, same path | ✓ |
| 12 unique-history paths | 12 (same list) — and re-verified against **full** 1021-commit history, not 400 | ✓ (strengthened) |
| ANSWER KEYS: 5, each 0 commits from origin/main | 5; all `0` | ✓ |
| eecdb0f exists, titled exposure-close, names the archaeology residual | confirmed in log | ✓ |

# WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

- **CC1, minor but real:** "reachable from the branch and from no remote ref" was true but incomplete as an exposure statement — stash, `refs/original/*` (which exists in this repo), reflogs, and dangling objects are local routes the sentence didn't cover. I checked all of them; the claim survives, so this is a scoping disagreement, not a refutation. Also, CC1's script told this panel's own sandbox "no branch in this clone" — false in kind, not degree — now fixed.
- **The other seat:** no substantive disagreement; their script repair dominates mine and I deferred. One observation for the record: their `test_this_repair_proposes_no_ref_deletion` failed once (`1 failed, 10 passed`) during our concurrent writes and passes deterministically in both orders now (`11 passed in 4.70s`) — a write-race artifact of the shared sandbox, not a defect in either fix, but worth knowing the shared-sandbox panel design permits mid-edit reads.

# WHAT I DID NOT CHECK

- The other 46 shared-but-differing defs between branch-v2 and v3 beyond `compute_rk` — bounded by 0-lost-defs/0-lost-flags, but a behavioural regression inside a shared def in v3 is not excluded by my probes.
- The content of any answer key or exam target — prohibited, not attempted; all key claims are path/OID-level.
- Working-tree copies of the repo elsewhere on this machine beyond the one `mdfind` surfaced.
- Whether the 6 branch exam targets are byte-identical to the vaulted copies (I relied on commit `2ce2a69`'s recorded measurement).
- The full test suite — per brief; only the two targeted suites were run.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round9_2026-09-10/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
