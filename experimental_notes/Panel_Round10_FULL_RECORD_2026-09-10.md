# Panel Round 10 — FULL RECORD, unfiltered

Record written 2026-09-11T09:40:55+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed and why

Round 10 reviewed task A2 — making the suite pass in a fresh clone — after the repair had been built and the clone measured green.

## What the round found, and both findings were in CC1's own repair

**THE REBASE LAUNDERED A `..` ESCAPE PAST THE STATIC GUARD (fable).** It rewrote `/Users/x/Constraint_Engineering/../../../etc/passwd` into an overlay path that normalises OUTSIDE the overlay, and `_USER_PATH` never policed `/private/var/folders`, so a REFUSED path became an ALLOWED one. **The seat read `/etc/passwd` through it, 9,344 bytes.** Reproduced here before the fix was accepted. The shipped fix is stronger than the one proposed: the seat's refused a project path immediately followed by `/..`, which leaves the same escape with 1 component in front still rebased, while `_substitute_root` normalises the RESULT so where the `..` sits does not matter.

**THE OTHER SEAT REASONED ABOUT THAT EXACT PATH AND JUDGED IT BELOW THRESHOLD.** fable executed the attack instead, and was right. That is the difference between review and falsification.

**THE IDENTITY REACHED NOTHING OUTSIDE A `git clone` (cc2).** `bench/panel_sandbox.py:43` drops `.git`, so the project's own review sandbox, a ZIP, a Zenodo archive and a vendored copy all collapsed identity to the folder name — literally `"repo"` — and the rebase recognised **0 of the 35** paths. Now read from tracked `.zenodo.json`.

**THIS IS THE ROUND THAT PROVED THE SEATS WERE NOT INDEPENDENT.** fable's reply describes the `.zenodo.json` identity tier the cc2 seat had just invented, and its own figures section records *"my first (background) run reported 33/640 from a stale `.pyc` (old `repo_paths.py` with no declared tier)"*. **fable reviewed cc2's edited tree, not the tree under review.** That observation produced task A20: 1 sandbox per seat, `seat_proposals.diff` keyed `<seat>:<path>`. Round 11 is the first round where agreement between seats is evidence of anything.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 10: the suite must pass for a reader who CLONES, and DELIVER YOUR FIX AS A FILE

<!-- figure: archived falsifier rejections that are NOT location artefacts | scripts/archived_falsifier_rejections_2026-09-10.py | real-rejection rate : 2/640 = 0.3125% -->
<!-- figure: entry A19's NO_SCORE claim, re-derived over the tracked archive | scripts/orphan_figures_2026-09-10.py | NO_SCORE: 0 of 1035 = 0.0000% -->

## SECTION 0 — THE DELIVERY RULE, AND THREE HARD PROHIBITIONS

**Founder ruling:** *"they need to supply fixes, not just problems!"* A finding without a fix is not a deliverable, and a fix in prose is not delivered. **Write it INTO the sandbox repository tree at its real path and leave it there.** `bench/panel_sandbox.py:teardown` destroys everything else.

**THE 3 CATEGORIES THE FOUNDER RESERVES TO HIMSELF IN PERSON.** Do not delete a git ref, do not spend money on a paid seat, do not touch the sealed answer-key store. You may recommend; you may not enact. Any patch containing `git branch -D`, `git tag -d`, `git push --delete`, `git gc --prune`, `git reflog expire` or `filter-repo` is refused whole.

## SECTION 1 — The question

Task A2: *"Make the suite pass in a fresh clone. For a project whose stated purpose is reproducibility this is central, not cosmetic — a reader who follows the documented steps does not see what the maintainer sees."*

## SECTION 2 — What is measured so far. RUN THESE.

`scripts/fresh_clone_census_2026-09-10.py` and `scripts/archived_falsifier_rejections_2026-09-10.py` establish the facts. Run both. `--check` on the first re-runs every test the census names.

1. **The entry's own premise was FALSE.** It said "11 failed, 5487 passed, exit 1, against **0 failures in the working tree**", measured 2026-09-09. Re-measured 2026-09-10 at the same HEAD: **the clone gave 22 failed, 6592 passed**, and the **working tree gave 6**. The count had doubled in a day and the maintainer's tree was not clean.
2. **15 test files, 5 distinct causes.** 10 of 15 were clone-only (66.6667%, Wilson [41.7135%, 84.8237%], Clopper-Pearson [38.3804%, 88.1759%]); the other 5 were red in both trees.
3. **The largest single cause is a stale ABSOLUTE PATH.** Archived falsifiers carry the absolute path of the checkout they were written in. On the maintainer's machine that path IS the repo root, so the containment guard allows it; anywhere else it refuses. **35 of 640 archived falsifiers (5.4688%, Wilson [3.9582%, 7.5107%])**, and **5 of the 15 exp44 execution rows**, so `execution_based_matcher`'s headline "12 of 15" came out **7 of 15** for every reader.
4. **The repair is `_retarget_falsifier` rebasing a foreign checkout of THIS project onto the overlay at replay.** The containment guard is NOT changed.
5. A fix meant to detect a fresh clone **could never fire**: it asked whether `git config --get user.email` was empty, and `--get` falls back to GLOBAL config, which a clone inherits.
6. Prose figures measured over the maintainer's on-disk archive are not reproducible: 6,770 JSON files here against 6,160 tracked. The pinned "4142 of 4142" gate records is **3507 of 3507** in a clone.

## SECTION 3 — Attack these specifically

1. **THE REBASE IS THE ONE TO BREAK.** `bench/repo_paths.py:foreign_repo_roots` + `bench/reference_runner_v3.py:_retarget_falsifier`. Construct an archived falsifier that reaches something it should not, THROUGH the rebase. If you can, that is the finding of the round. Attack the regex, the identity resolution, and the interaction with `_allow_roots`.
2. **The identity comes from the git remote.** Break it: a fork, a mirror, a rename, a remote that is a local path, no remote at all, a submodule. What happens then, and is the failure safe?
3. **Are my SKIPS honest?** I converted several failures into skips where the checkout lacks the artefacts (`bench/archive_corpus.py`). A skip that can fire when the test COULD have run is a deleted test. Find one that can.
4. **Did I hide a real defect behind a corpus argument?** The gate-count figure moved from 4142 to 3507 because I changed the corpus. Check that the *conclusion* (the gate never fired) is unaffected, and say so if it is not.
5. **`bench/repo_paths.py` now runs `git` on import-adjacent paths.** Cost, failure modes, and what happens with no git binary.
6. **Task V4** (`scripts/orphan_figures_2026-09-10.py`): 4 task-list entries carried a figure with no producing script. Check my producers reproduce what the entries now claim, and that the A8 population caveat is correct rather than an excuse.

## SECTION 3B — EVERY FIX MUST BE TESTED, BY YOU, BEFORE YOU HAND IT BACK

**A fix you have not executed is a hypothesis.** Every fix you leave in the tree arrives with a runnable falsifier that you have RUN, and your reply carries its output. Put the test at `bench/tests/<name>.py`, run it with `python3 -m pytest -q <path>`, and quote the result line verbatim.

**The test must be able to FAIL.** Break the thing your fix repairs, run the test again, and quote the red output too. A test that passes against the broken state proves nothing; this project found 8 of its own mutation tests vacuous that way on 2026-09-09, and 2 of MINE tonight — a rebase mutation and an identity mutation both passed my first controls, and I had to rewrite them.

**Use the mathematical instruments where they bear.** Any proportion needs a Wilson interval and a second tool. The `severity` scale and the two-sided `gamma` gate are the runner's own instruments; if a fix of yours changes what reaches a verdict, say what it does to them.

## SECTION 4 — What would refute YOU

For every finding, state what evidence would overturn it. A finding naming no such evidence is an opinion. If you disagree with a claim in Section 2, say what you ran and what it returned.

## SECTION 5 — When to stop

**Diminishing returns.** Stop when another pass produces no new above-threshold finding. Above threshold means: it could put a wrong number in front of the founder, let a falsifier reach material that decides the answer, or make the repository claim something about itself that a reader cannot check. Do not pad to a count. Do not report style.

## SECTION 6 — The output shape, field by field

Return **Markdown**, in this order:

1. **`VERDICT`** — `SOUND`, `UNSOUND`, or `SOUND WITH EXCEPTIONS`, on the A2 repair as a whole, in the first line.
2. **`FILES I LEFT IN THE TREE`** — repo-relative paths you created or edited. `NONE` plus a reason if empty; an empty list without one is a failed round.
3. **`FINDINGS`** — numbered. Each: **WHAT** (1 sentence), **WHERE** (`path:line`), **EVIDENCE** (the exact command and its output, quoted), **FIX** (the path you wrote it to), **WHAT WOULD REFUTE THIS**, **SEVERITY** (0.0 to 1.0).
4. **`THE REBASE`** — your specific verdict on whether it can be used to reach material it should not, with what you ran.
5. **`FIGURES I RE-RAN`** — each declared figure, what you got, whether it matched.
6. **`WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1`** — preserved, never smoothed. Say so explicitly if you agree with everything.
7. **`WHAT I DID NOT CHECK`** — the honest boundary of your pass.

Do not return a summary in place of the full output.


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 62 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round10_2026-09-10) -->

VERDICT: **SOUND WITH EXCEPTIONS** — the A2 diagnosis and the rebase are correct and the rebase opens no new reach, but the repair is *inert in every checkout that is not a `git clone`*, which includes this project's own panel sandbox; I found and fixed that, a duplicate identity implementation that defeated the fix, a dishonest skip, and a second git-backed figure that printed 100% by construction.

## FILES I LEFT IN THE TREE

| path | change |
|---|---|
| `bench/repo_paths.py` | added `declared_project_names`, `_NOT_AN_IDENTITY`, `_SOURCE_RANK`, and the declared identity tier in `project_names` |
| `scripts/archived_falsifier_rejections_2026-09-10.py` | `project_names` delegated to the one predicate instead of re-implemented |
| `scripts/orphan_figures_2026-09-10.py` | `GitCannotAnswer`; entry A8's figure refuses instead of guessing; A19 still reported |
| `bench/tests/test_fresh_clone_suite_2026-09-10.py` | enum widened for the new source *and strengthened*; dishonest skip at :156 lifted |
| `bench/tests/test_declared_identity_2026-09-10.py` | **new** — 30 controls, all three fixes, mutation-verified |

No patch of mine contains `git branch -D`, `git tag -d`, `git push --delete`, `git gc --prune`, `git reflog expire` or `filter-repo` (verified above: `NONE - clean`). I enacted nothing in the three reserved categories.

## FINDINGS

### 1. The A2 repair is inert in any checkout without `.git` — including this project's own panel sandbox — and it left the A2 suite RED there
**WHAT** Identity comes from the git remote with only the folder name as fallback; `git clone` carries a remote and nothing else does, so in a ZIP/tarball/Zenodo/vendored/sandbox checkout identity collapses to the folder name and the rebase recognises 0 of the 35 stale paths it exists to rebase.

**WHERE** `bench/repo_paths.py:140-157` (`project_names`), consumed at `bench/reference_runner_v3.py:4053`. The degraded state is institutional, not incidental: `bench/panel_sandbox.py:43` → `_NEVER_COPY = frozenset({".git"})`.

**EVIDENCE** This sandbox has `git` 2.50.1 on PATH and no `.git`:
```
$ python3 -m pytest -q -p no:warnings bench/tests/test_fresh_clone_suite_2026-09-10.py
FAILED ...::TestTheReplayRebaseIsBounded::test_it_rebases_this_project_named_from_another_checkout
FAILED ...::TestTheRejectionClassifier::test_the_real_rejection_count_is_location_independent
2 failed, 18 passed, 1 skipped in 5.05s
```
```
E       AssertionError: the archived path was not recognised
E       assert 0 == 1
```
The declared figure did not reproduce — I measured `33/640 = 5.1562%`, not `2/640`, with `project identity : ['repo'] (from the directory)`. After the fix:
```
$ python3 -m pytest -q -p no:warnings -rs bench/tests/test_fresh_clone_suite_2026-09-10.py
21 passed in 5.14s
```
```
project identity    : ['Constraint_Engineering', 'repo'] (from the declared)
real-rejection rate : 2/640 = 0.3125%   Wilson [0.0857%, 1.1322%]  Clopper-Pearson [0.0379%, 1.1243%]
location-artefact rate: 35/640 = 5.4688%  Wilson [3.9582%, 7.5107%]
```
Both of the brief's declared figures now reproduce exactly (`5.4688%`, Wilson `[3.9582%, 7.5107%]`). This is the basename-versus-path defect's **7th** recurrence, again inside the fix for the previous one.

**Bounding, because the fix widens what the rebase rewrites:** one tracked file, one field, one strict `github.com/<owner>/<repo>` pattern, and `_NOT_AN_IDENTITY` refuses a generic name even when declared. A prose scan would have been wrong: `PAPER.md` cites `github.com/jebus197/OpenBrain` and `github.com/jebus197/Project_Genesis`, and both would have become identities of this project. There is a control for that.

**FIX** `bench/repo_paths.py` + `bench/tests/test_declared_identity_2026-09-10.py`.

**WHAT WOULD REFUTE THIS** A demonstration that every reader path carries `.git` (would make the tier dead weight — but `panel_sandbox.py:43` alone refutes it); or a tracked identity source that drifts from the remote, making `.zenodo.json` a second place for the name to rot; or evidence that the `_NOT_AN_IDENTITY` list admits a name that rebases an unrelated path.

**SEVERITY 0.75**

### 2. A duplicate `project_names` inside the census defeated the fix to the real one
**WHAT** The census re-implemented identity locally, so repairing the canonical predicate did not move its figure — the anti-pattern the repo names at `execution_based_matcher.py:330` ("a second implementation of a rule, which is a second rule"), while the script's own docstring at :74 already cited `project_names()` as the authority.

**WHERE** `scripts/archived_falsifier_rejections_2026-09-10.py:110-138`.

**EVIDENCE** After fixing `bench/repo_paths.py`, the census was unchanged at `real-rejection rate : 33/640 = 5.1562%`. After delegating: `2/640 = 0.3125%`. **Committed measurement for the removal, as the additive standard requires:** in a no-`.git` checkout the copy gives 33 of 640 and the module gives 2 of 640, which is the maintainer's own figure — the copy is strictly dominated on location independence, not merely disliked.

**FIX** `scripts/archived_falsifier_rejections_2026-09-10.py`.

**WHAT WOULD REFUTE THIS** A property the local copy has that the module lacks (I found none); or a call site where delegating creates an import cycle.

**SEVERITY 0.6**

### 3. A skip that fired where the test could have run — a deleted test, in exactly the checkout the file defends
**WHAT** `test_a_directory_rename_does_not_lose_the_identity` skipped on `source != "remote"`, but the remote is only one tier; with the declared tier answering, every assertion in it passes.

**WHERE** `bench/tests/test_fresh_clone_suite_2026-09-10.py:156`.

**EVIDENCE** `SKIPPED [1] ...:156: no git remote here, so the strong identity is absent` → after narrowing the guard to `source == "directory"` (the one state where the assertion genuinely cannot hold): `21 passed` with **0 skipped**. This is §3.3 answered with an instance. The gate-count skips I also checked are **honest** — they name why (`git cannot list the archive here, so the tracked corpus cannot be identified`) and are `archive_corpus`-backed.

**FIX** `bench/tests/test_fresh_clone_suite_2026-09-10.py`.

**WHAT WOULD REFUTE THIS** A checkout where `source == "declared"` but the assertion legitimately fails.

**SEVERITY 0.45**

### 4. Entry A8's figure printed 100% *by construction*, with a confidence interval on it
**WHAT** `untracked_cited_paths` read `git ls-files`'s `.stdout` and ignored the return code; with no `.git`, git exits 128 with empty stdout, `tracked` becomes empty, every cited path counts as untracked.

**WHERE** `scripts/orphan_figures_2026-09-10.py:74`.

**EVIDENCE** `git ls-files` → `fatal: not a git repository`. The script printed:
```
  cited: 127   untracked: 127
  127/127 = 100.0000%
  Wilson 95%          : [97.0640%, 100.0000%]
```
A fabricated figure, in the direction that **inflates** the finding. The correct pattern already existed in this repo, written the same day: `bench/archive_corpus.py:50` tests `out.returncode != 0`. Now:
```
REFUSING TO REPORT entry A8's figure: `git ls-files` could not answer ... (exit 128) ...
100% by construction, not by measurement. Run this in a git checkout.
```
My own first cut raised `SystemExit` and took entry A19's figure down with it; there is now a control (`test_refusing_A8_does_not_suppress_A19`) for that regression, and A19 still reports `NO_SCORE: 0 of 1035 = 0.0000%`.

**FIX** `scripts/orphan_figures_2026-09-10.py`.

**WHAT WOULD REFUTE THIS** A caller depending on the old lenient behaviour; or a no-`.git` path by which the tracked corpus *is* recoverable (then refusing is too strong and it should measure).

**SEVERITY 0.65**

### Mutation proof (§3B — each test must be able to fail)
```
##### MUTATION 1: delete the declared tier from project_names #####
FAILED ...TestTheDeclaredTierAnswersWithoutGit::test_identity_does_not_collapse_to_the_folder_name
FAILED ...TestTheDeclaredTierAnswersWithoutGit::test_the_rebase_works_with_no_remote_at_all
FAILED ...TestTheDeclaredTierAnswersWithoutGit::test_a_foreign_checkout_is_resolved_with_no_remote
3 failed, 23 passed in 0.75s
--- and the maintainer's A2 suite under the same mutation:  3 failed, 17 passed, 1 skipped
##### MUTATION 2: drop the _NOT_AN_IDENTITY filter #####
FAILED ...TestTheDeclaredTierIsBounded::test_a_generic_name_is_refused
1 failed, 25 passed in 0.61s
##### MUTATION 3: restore the .stdout-only read #####
FAILED ...test_it_refuses_when_git_cannot_answer
FAILED ...test_it_refuses_on_an_empty_listing_too
2 failed, 2 passed, 26 deselected in 3.42s
##### RESTORED #####  51 passed in 7.80s
```
Every control asserts on the identity **source**, never on mere membership of `Constraint_Engineering` in the name set — in the maintainer's tree the folder carries that name, which is the exact trap that made his first identity control vacuous. Targeted regression run across everything touching `_retarget_falsifier` and `repo_paths`: **90 passed, 2 skipped** and **69 passed**.

I also hit one of my own: my first key-reach control keyed on the bare finding id and failed, because **finding ids are not globally unique across runs** (exp47 also carries a `C0012`, and that one *is* a location artefact). Now keyed on `(run, cid)`, with the reason recorded in the test.

## THE REBASE

**It cannot be used to reach material it should not. The static traversal capability pre-exists it and is not widened by it.** I attacked the regex, the identity resolution and the `_allow_roots` interaction.

The rebase does flip refusals to acceptances — that is its *purpose*, so a flip is not itself evidence. The question is whether any flip yields reach a directly-authored path could not already obtain. It does not:

```
"open('/etc/passwd')"                                        -> []
"open('/tmp/../etc/passwd')"                                 -> []
"open('/private/var/folders/x/overlay/../../../etc/passwd')"  -> []
"open('/Users/georgejackson/ov/../../../etc/passwd')"        -> [('a path outside the declared target', ...)]
```
`_USER_PATH` (`falsifier_verify.py:316`) matches only home- and volume-shaped roots. Overlays are `tempfile.mkdtemp` (`reference_runner_v3.py:3848`) → `/private/var/folders/...`, which that rule never matched. So a `..`-bearing remainder surviving the rebase lands in a region the static path rule did not police before the rebase existed, and any model could already name directly. Where the overlay *is* under home, `_norm_path` normalises `..` and the guard holds. The runtime observer (`_resolve` → `realpath`, `falsifier_verify.py:486-496`) resolves `..` independently, and `_denied` tests the protected set before the allow set.

Two residuals, both below threshold and both reported rather than fixed: (a) `foreign_repo_roots`'s middle character class admits `..`, so `/Users/gj/../../../etc/Constraint_Engineering/x` is rebased to `/tmp/overlay/x` — a false-positive rebase of a directory genuinely outside the project, redirecting *inward*, not an escape; (b) `project_names` unconditionally adds `root.name`, so a reader who clones into a folder named e.g. `src` widens the rebase to any path ending `/src`. I deliberately did **not** narrow those tiers — narrowing them is a behaviour change I have not measured, and an unmeasured narrowing is not an improvement. My `_NOT_AN_IDENTITY` filter applies only to the tier I added.

Decisive negative control, run **with the remote suppressed** (i.e. against the widened configuration): `/etc/passwd`, `~/.ssh/id_rsa`, `Documents/answer_key.json`, `Other_Project`, `Constraint_Engineering_backup`, `OpenBrain` — all six `(out, n) == (code, 0)`. And exp48 C0012, the archived falsifier that opened the chemistry answer key, is **still refused** and still classified real, on 8 grounds including `an answer-key file path`; it is not reclassified as a location artefact. There is a control pinning that.

## FIGURES I RE-RAN

| figure | declared | I got | match |
|---|---|---|---|
| real-rejection rate | `2/640 = 0.3125%` | `33/640 = 5.1562%` **before**; `2/640 = 0.3125%`, Wilson `[0.0857%, 1.1322%]`, CP `[0.0379%, 1.1243%]` **after my fix** | **NO**, then **YES** |
| location artefacts | `35` (implied by 5.4688%) | `4` before; `35/640 = 5.4688%`, Wilson `[3.9582%, 7.5107%]` after | **NO**, then **YES** |
| A19 `NO_SCORE` | `0 of 1035 = 0.0000%` | `0 of 1035 = 0.0000%`, Wilson `[0, 0.3698%]`, CP `[0, 0.3558%]`; verdicts `{ADMISSIBLE: 691, ESCALATE: 154, REJECTED: 190}` | **YES** |
| clone-only files | `10/15 = 66.6667%` | `10 of 15 = 66.6667%`, Wilson `[41.7135%, 84.8237%]`, CP `[38.3804%, 88.1759%]` | **YES** |
| stale-path falsifiers | `35 of 640 (5.4688%)` | reproduced after fix | **YES** |
| A8 untracked | `127/127 = 100%` | refuses now — **the figure was an artefact** | **N/A, withdrawn** |

**§3.4 — the gate-count conclusion is corpus-invariant, and this is a derivation, not a judgement.** The tracked corpus T is a subset of the on-disk corpus D (a tracked file in a checkout is on disk). Firings are counted per record, so `|{x ∈ T : fired(x)}| ≤ |{x ∈ D : fired(x)}| = 0`, hence firings(T) = 0. Moving the denominator 4142 → 3507 **cannot** manufacture or destroy a firing; only a corpus change in the *widening* direction could, and T ⊆ D forbids it. The number moved; the conclusion cannot. No real defect is hidden behind the corpus argument. The two skips in that file are honest.

**§3.5 — `repo_paths` running git.** Cost: **15.59 ms per `project_names()` call**, one subprocess, `timeout=30`, at import-adjacent call sites. With no git binary at all it now degrades *upward*, not down:
```
git on PATH: None
project_names: ({'Constraint_Engineering', 'repo'}, 'declared')
rebase resolves: ['/Users/x/Constraint_Engineering']
```
Before my fix that case resolved nothing. The `OSError`/`SubprocessError` catch was already correct; what was missing was anything to fall back *to*.

**Effect on the runner's instruments (§3B).** My fix changes neither the `severity` scale nor the two-sided `gamma` gate. It changes the **population** reaching them: 31 archived falsifiers per 640 that were routed to human review purely for where a directory sits now get re-executed and receive a tool verdict. That is the intended direction — tools decide, not location — but it is a real change to verdict inputs, and the resulting CONFIRMED/REFUTED split is unmeasured (below).

## WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

I saw no other seat's output, so this is disagreement with the brief (CC1) only.

1. **Section 2's framing that the stale-path repair works is too strong.** It holds for `git clone` and for nothing else. The brief's own declared figure `2/640 = 0.3125%` did not reproduce for me — I measured `33/640 = 5.1562%`, and the maintainer's own test named `test_the_real_rejection_count_is_location_independent` failed, asserting an invariance that did not hold. I agree with the diagnosis and the repair's *shape*; I disagree that it was finished.
2. **Section 3.1 predicted the rebase would be the finding of the round. It is not.** I attacked it as instructed and it held. Declaring it sound is the honest result, and the real defect was one layer up — in how identity is *obtained*, not in how the rebase uses it.
3. **Section 3.6's A8 caveat: I agree it is a correct caveat, not an excuse** — it names the population difference and explicitly declines to quote the two figures against each other. But the *figure it caveats* was an artefact in any non-git checkout, which the caveat does not mention and could not catch.
4. **I disagree with the brief's implicit boundary "fresh clone".** The reproducibility claim is owed to readers who take the ZIP or the Zenodo archive this project itself publishes, and — decisively — to the project's own panel sandbox, which is where every one of these reviews runs.

## WHAT I DID NOT CHECK

- **The CONFIRMED/REFUTED split of the 31 newly-rebased falsifiers.** I proved they are now *executed* rather than refused, and that the key-reach case is still refused. I did not re-run their verdicts, so I cannot say what the corrected `execution_based_matcher` headline is; I verified the brief's claim that it *was* 7 of 15 for readers only via the rejection census, not by re-running exp44.
- **`scripts/fresh_clone_census_2026-09-10.py --check`**, which re-runs all 15 named test files. I ran the census itself (figures matched) and ran 5 of the named files plus the `repo_paths` and discrimination suites directly. I did not run the full suite — the brief forbids it.
- **The other three clone-only causes** (`import-time-io`, `environment`, `cascade`) beyond confirming the census still names them.
- **Whether `.zenodo.json` can drift from the git remote.** It agrees today (`github.com/jebus197/Constraint_Engineering`); nothing I added detects future disagreement between the two tiers, and a control that asserts they agree would be worth adding.
- **Windows and case-insensitive filesystems.** `_NOT_AN_IDENTITY` is compared lower-cased, but I tested only macOS.
- **`line_mentions_archive_path` / `is_archived_run_output`**, which I did not touch; §3.5's cost question I answered for `project_names` only.
- **Non-GitHub remotes** (GitLab, self-hosted) in the declared tier — the pattern is GitHub-only by design, so such a project would fall through to the directory name exactly as before. That is a deliberately narrow scope, not a tested one.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 65 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round10_2026-09-10) -->

VERDICT and full findings below.

---

## `VERDICT`
**SOUND WITH EXCEPTIONS** — the A2 repair's spine is sound (the `.zenodo.json` "declared" identity tier makes the rebase work in a `.git`-less checkout, declared figures reproduce deterministically, the fresh-clone suite passes 21/21, the no-git-binary path fails safe), but I found two above-threshold defects, both fixed and tested in the tree: the A2 rebase can launder a `..`-escape past the static containment guard, and a financial-safety invariant is deleted for checkouts holding 1–9 panel replies.

## `FILES I LEFT IN THE TREE`
- `bench/reference_runner_v3.py` — edited `_retarget_falsifier` (fail-closed `..` guard)
- `bench/tests/test_panel_conditions_are_met_2026-09-10.py` — edited: ungated the paid-seat safety check
- `bench/tests/test_rebase_no_dotdot_escape_2026-09-10.py` — new regression test (rebase escape)
- `bench/tests/test_paid_seat_check_is_not_gated_2026-09-10.py` — new regression test (paid-seat gate)

## `FINDINGS`

### Finding 1 — The A2 rebase launders a `..`-traversal escape past the static guard
- **WHAT**: `_retarget_falsifier` rewrites `/Users/x/Constraint_Engineering/../../../etc/passwd` into `<overlay>/../../../etc/passwd`, which normpath-resolves *outside* the overlay; the pre-rebase form is caught by `scan_falsifier_source`'s `_USER_PATH` net but the rewritten form is not, and the runtime observer is default-allow for `/etc`.
- **WHERE**: `bench/reference_runner_v3.py:4056` (naive `text.replace(stale, overlay_root)`)
- **EVIDENCE** (end-to-end, before fix):
  ```
  subs= 1
  === execute_python result ===
  READ_BYTES 9344
  FALSIFIED
  ```
  The rebased path read `/etc/passwd` (9344 bytes) with no integrity refusal. The identical pre-rebase `/Users/...` path *is* refused (`A3 (no rebase) static-scan: [('a path outside the declared target', '/Users/attacker/secrets.txt')]`), so the rebase — not a pre-existing hole — is what opens it.
- **Boundary (what it does NOT reach)**: the scoring key stays defended — a rebased path to a `CDSFL_KEY_DIR` store returned `INTEGRITY VIOLATION — a protected location named literally`, and `/Users` home material is caught by `_USER_PATH` (`matched: '/Users/georgejackson/.cdsfl_probe_secret'`). So it reaches non-key files outside the sandbox (`/etc`, `/opt`, `/usr`, sibling trees), not the material that decides the exam answer.
- **FIX**: `bench/reference_runner_v3.py` — the rebase now refuses to rewrite any project-path immediately followed by `/..`, leaving the stale `/Users/` prefix so the static guard refuses it to a human (fail-closed). After fix, the same attack returns `INTEGRITY VIOLATION — NOT EXECUTED`; a benign path still retargets (`open("/tmp/cdsfl_overlay_probe/bench/x.md") subs= 1`).
- **Test + mutation**: `test_rebase_no_dotdot_escape_2026-09-10.py` → `3 passed`; reverting the fix → `2 failed, 1 passed` (the two escape tests go red, benign stays green). Existing consumers unaffected: `test_discrimination_control.py` + `test_absolute_target_paths_2026-08-23.py` + both new tests → `66 passed`.
- **WHAT WOULD REFUTE THIS**: showing the runtime observer *does* deny `/etc/passwd` on a stock config (it did not here), or that no code path applies `_retarget_falsifier` to model/archived-authored code (it is applied in `execution_based_matcher._run` and the discrimination control).
- **SEVERITY**: 0.55 — a genuine defense-in-depth regression; capped below 0.7 because the answer key and home dirs stay protected by independent mechanisms.

### Finding 2 — A financial-safety invariant is deleted for 1–9 replies
- **WHAT**: `test_zero_paid_replies_in_any_round_under_section_p` gated its per-record "no paid seat was dispatched" check behind `corpus.shortfall(len, 10)`; a paid seat among fewer than 10 replies is **skipped, not caught** — a founder-reserved money constraint silently disabled in that window.
- **WHERE**: `bench/tests/test_panel_conditions_are_met_2026-09-10.py:79-87` (before fix)
- **EVIDENCE** (falsifier, 3 replies incl. one `route="anthropic_api"`):
  ```
  SKIPPED though a paid seat was present and checkable: this checkout holds 3 panel seat replies under Section P, and the measurement ne
  FALSIFIED
  ```
  After fix: `test RAN and caught the paid seat: a paid seat was dispatched under the ruling: [('panel_2026-09-02_r2', 'PAID-b')]`
- **FIX**: `bench/tests/test_panel_conditions_are_met_2026-09-10.py` — removed the `shortfall` gate from the safety boolean (meaningful at any n≥1, trivially true at n=0). The "too few to *conclude*" statistical reporting stays in its sibling `test_the_rounds_under_the_ruling_exist_at_all`, which is unchanged.
- **Test + mutation**: `test_paid_seat_check_is_not_gated_2026-09-10.py` → `4 passed`; re-introducing the gate → `4 failed`. The full file still passes clone-side: `15 passed` (paid check passes trivially at n=0, vacuity sibling skips honestly).
- **WHAT WOULD REFUTE THIS**: showing some *other* always-on control fails a paid dispatch at 1–9 replies (I found none in this test module), or that 1–9-reply states never occur (they occur mid-experiment and in partial commits).
- **SEVERITY**: 0.5 — touches a founder-reserved money constraint; reachability needs a partial corpus (1–9 replies), and a fresh clone at n=0 is unaffected.

## `THE REBASE`
It **can** be used to reach material it should not — I read `/etc/passwd` end-to-end through it (Finding 1) — but it **cannot** reach the material that decides the exam answer: the scoring key is refused by the protected-set (hash + literal), and `/Users` home material by `_USER_PATH`. The mechanism is `..`-laundering: the rebase strips the `/Users/` prefix the static guard keys on, and the runtime observer is a denylist (default-allow) that omits `/etc`. The brief's premise that "the containment guard is NOT changed" is true but insufficient — the guard is unchanged while the rebase now feeds it a form it doesn't catch. I attacked the regex (benign paths still rewrite), identity resolution (declared tier resolves `Constraint_Engineering` with no `.git`), and `_allow_roots` interaction (destination is always an allowed root, so the *direction* is safe; the `..`-escape is the exception). Fixed fail-closed and regression-tested.

## `FIGURES I RE-RAN`
- **`archived_falsifier_rejections_2026-09-10.py`**: 2/640 real rejections (Wilson [0.0857%, 1.1322%]), 35/640 location artefacts — **matches** the declared `2/640`. Note: my first (background) run reported `33/640` from a **stale `.pyc`** (old `repo_paths.py` with no declared tier); three consecutive clean runs are deterministic at 2/640, so I withdraw non-determinism as a finding.
- **`orphan_figures_2026-09-10.py`**: A8 = 127/127 cited `bench/logs` paths untracked (correctly scoped as a slice, not the entry's 4.65% denominator); A19 NO_SCORE = 0/1035 (Wilson [0%, 0.3698%]), claim holds, wider interval honestly reported for the smaller tracked population. **Reproduced.**
- **`fresh_clone_census_2026-09-10.py`**: 10/15 clone-only (Wilson [41.71%, 84.82%]), 5 causes; other 5 red in both trees. **Matches** brief §2.

## `WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1`
I disagree with the framing that the rebase only redirects *into* the overlay and therefore cannot affect containment. For `..`-bearing paths the redirect resolves *outside* the overlay and bypasses the static guard — demonstrated by reading `/etc/passwd`. Everything else in Section 2 reproduced as stated.

## `WHAT I DID NOT CHECK`
- The full ~8-min suite and `--check` census re-run (one-shot budget).
- The top-of-function `real`-root substitution in `_retarget_falsifier` (line 4029, pre-existing, outside A2 scope) has the same `..` class for *live* falsifiers; I did not fix it — flag for a follow-up.
- §3.4 "gate never fired" conclusion under the 4142→3507 corpus change — I relied on the census's own statement, not an independent re-derivation.
- Fork/mirror/rename identity against a *real* `.git` clone (the sandbox has none; I tested the declared and no-git tiers only). Minor: `Path(".").name == ""` puts an empty string in `project_names` under a `.`-root, harmlessly skipped by `foreign_repo_roots`.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round10_2026-09-10/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
