# Panel Round 14 — FULL RECORD, unfiltered

2026-09-11, dispatched 06:55:35 BST, both seats returned by 07:14 BST. Record written 2026-09-11T09:23:36+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. The summary CC1 gave in conversation is downstream of this file, not a substitute for it.

## What was reviewed and why

Section P of the master task list makes a panel review a precondition on closing any entry. Round 14 reviewed 3 fixes made that morning under task A2, all of them repairs to defects found by cloning HEAD and running the suite in the clone — which gave **3 failed, 6952 passed, 38 skipped, 1 xfailed** against **6988 passed, 0 failed** in the working tree.

1. `hooks/stage0_restage.sh`, new — the pre-commit repairs wrote the working tree and never staged what they wrote, so every commit shipped the unrepaired content and the repair lagged 1 commit behind.
2. `scripts/citation_content_guard_2026-09-10.py`'s `repair()`, rewritten — an unbounded `str.replace` with no digit boundary had destroyed 3 correct citations while repairing 1.
3. `scripts/_cli_help.py`, new and wired into 30 scripts — **30 of 53** measurement scripts had no argument parser, so `--help` ran the whole measurement and exited 0, which the survey read as a clean answer. 56.6038%, Wilson [43.2654%, 69.0496%].

## Seats and cost

2 seats, `cc2` (Claude Opus 4.7 via CLI piped mode) and `fable`, both on the Max subscription. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`. Each seat ran in its OWN sandbox — round 11 was the first with that property, and it is what makes agreement between the seats evidence rather than contamination.

## What CC1 did with the findings, stated before the replies rather than after

**5 distinct defects, 3 of them found by both seats independently** — 60.0000%, Wilson [23.0724%, 88.2379%], Clopper-Pearson [14.6633%, 94.7255%]. cc2 found nothing fable missed; fable found 2 more.

**The seats proposed DIFFERENT delta-staging mechanisms for the worst finding — cc2 a 3-way `git merge-file`, fable a zero-context `git apply --cached` — and the disagreement was settled by measurement rather than by argument.** Measured on an 8-line file against a real index, with the repair at a varying distance from the author's unstaged hunk:

| gap | 3-way `git merge-file` | zero-context `git apply --cached` |
|---|---|---|
| 0 | CONFLICT | FAILED |
| 1 | CONFLICT | OK, withheld hunk excluded |
| 2 | OK | OK |
| 3 | OK | OK |

Zero-context apply succeeds everywhere merge-file does and also at gap 1 — a citation repair 1 line from an edit in progress, which is the common geometry. fable's mechanism shipped. At gap 0 both refuse, correctly: the repair and the withheld hunk touch the same line and there is no right answer without asking.

**Every other finding was reproduced here before it was accepted**, including the `index.lock` one, which was measured from a live hook across 4 commit forms.

## Seat: cc2

<!-- verbatim-begin: cc2 (Claude Opus 4.7, Max subscription, panel round 14) -->

VERDICT: **NOT READY**

The three fixes are directionally right and FIX 2 (the positional splice) is sound. FIX 1 closes the "repair misses the commit" defect but opens a symmetric one: it commits content the author deliberately withheld. FIX 3 is sound as far as it goes. Two further defects found. All three of my repairs are in the tree, executed, and shown red under mutation.

---

## FILES I LEFT IN THE TREE

| Path | Status |
|---|---|
| `hooks/stage0_restage.sh` | modified — partial-staging delta splice (F1), `index.lock` escape (F2) |
| `hooks/pre-commit` | modified — 1 call wiring `cdsfl_snapshot_partially_staged` before the repairs |
| `scripts/citation_content_guard_2026-09-10.py` | modified — byte-round-trip guard in `repair()` (F3) |
| `bench/tests/test_restage_preserves_partial_staging_2026-09-11.py` | new — 12 tests, all executed |

---

## FINDINGS

### 1. The re-staging commits hunks the author withheld — HIGH

**WHAT.** `cdsfl_restage_paths` runs `git add -- <path>` on a whole file. The stated mitigation — *"ONLY the exact paths a repair REPORTS changing are staged, so an unrelated work-in-progress edit is never swept into a commit"* — bounds which **files** are touched. It does not bound which **hunks**. A file staged with `git add -p` loses its withheld hunks to the next commit the moment a stage-0 repair touches it.

**WHERE.** `hooks/stage0_restage.sh`, `cdsfl_restage_paths`.

**EVIDENCE.** Scratch repo, real index, unmodified library:

```
--- git status (M in both columns = partially staged) ---
MM note.md
--- what is STAGED right now ---
L1 AUTHOR-STAGED / L2 original / L3 original / L4 original / L5 original
=== a stage-0 repair now edits note.md (line 3) and reports it ===
pre-commit: re-staged note.md (stage-0 repair)
--- what is STAGED after cdsfl_restage_paths ---
L1 AUTHOR-STAGED
L2 original
L3 REPAIRED
L4 original
L5 AUTHOR-WIP-NOT-STAGED      <-- committed, unasked
--- verdict ---
SWEEP-IN CONFIRMED: the unstaged hunk is now in the index and will commit.
```

This is the same class as the defect FIX 1 exists to cure, pointing the other way: HEAD gets content nobody reviewed, and `git status` afterwards looks innocent.

**FIX (delivered).** No stash — a 3-way merge into the index. `cdsfl_snapshot_partially_staged` (called from `hooks/pre-commit:151`, before any repair writes) copies the working-tree content of every path modified in *both* index and worktree; normally an empty set, 2 git calls. `cdsfl_stage_repair_delta` then computes `git merge-file -p <staged> <pre-repair worktree> <post-repair worktree>` and writes the result with `git hash-object -w` + `git update-index --cacheinfo` — **index only**, working tree untouched, nothing to lose if the hook dies. Every file that is *not* partially staged returns non-zero and falls through to the original `git add`, unchanged. Nothing removed; a narrower path added beside it.

On merge conflict (repair and WIP touch the same lines) it **refuses and says so loudly** rather than staging conflict markers. That narrow case reverts to the old 1-commit lag — but visibly, with instructions, instead of silently committing the author's WIP. I state this as a deliberate trade: an irreversible wrong commit is worse than a red guard the author is told about. Observed in the end-to-end integration run on a 3-line file where repair and WIP were adjacent lines:

```
pre-commit: note.md is partially staged AND the stage-0 repair
            collides with an unstaged hunk. NOT staged: staging
            it would commit conflict markers or your WIP.
--- COMMITTED AT HEAD ---   A / b / c        (WIP not committed)
--- WORKTREE ---            A / B-REPAIRED / C   (nothing lost)
```

**RED PROOF** (fix removed, same scenario):
```
FAILED ...::TestTheRepairLandsWithoutTheWip::test_the_withheld_hunk_is_not_swept_in
1 failed, 3 passed
```
Precisely one test flips — correct, because `git add` *does* deliver the repair and *does* leave the worktree alone; only the sweep-in assertion discriminates.

**WHAT WOULD REFUTE THIS.** A demonstration that `git add -- <path>` stages only hunks already in the index (it does not — shown above); or evidence that no stage-0 repair ever touches a file a maintainer partially stages. The citation repair edits `experimental_notes/**/*.md` including the founder's master task list, which is exactly the kind of file edited incrementally.

---

### 2. The pathspec notice fires on `git commit -a` and tells the author two false things — MEDIUM

**WHAT.** `cdsfl_warn_if_partial_commit`'s escape list is `"$_dir/index"|*/index|index`. Measured, git 2.50.1, by printing `$GIT_INDEX_FILE` from a live hook:

```
git commit            .git/index                        real index    (silent, correct)
git commit --amend    .git/index                        real index    (silent, correct)
git commit -a         <gitdir>/index.lock               real index    (WARNED — wrong)
git commit -- <path>  <gitdir>/next-index-<pid>.lock    TEMPORARY     (warned, correct)
```

`index.lock` matches none of the three escapes, so **every `git commit -am` in this repository** is told *"this is a pathspec commit (git commit -- <path>)"* and that the repairs *"WILL land in this commit even though they are outside the pathspec"*. Under `-a` there is no pathspec and committing every modified file is what was asked for. Both sentences are false, on the commonest commit command there is. The hole is the next instance of the shape the function's own comment warns about — and it is the opposite failure: the first version could never fire, this one fires when it must not.

**WHERE.** `hooks/stage0_restage.sh`, `cdsfl_warn_if_partial_commit`.

**EVIDENCE.** Live hook output, quoted verbatim above under `=== 3. commit -a ===` in the probe; reproduced end-to-end through a real `git commit -am` in the delivered test.

**FIX (delivered).** Added `"$_dir/index.lock"|*/index.lock|index.lock) return 0 ;;` beside the existing escapes. The discriminator is the basename: git names the final index `index`, its lock `index.lock`, and a genuinely temporary index `next-index-<pid>`. The pathspec case still warns.

**RED PROOF** (escape removed):
```
FAILED ...::test_a_real_index_is_silent[{gitdir}/index.lock-git commit -a]
FAILED ...::test_a_real_commit_dash_a_is_silent
2 failed, 3 passed
```

**WHAT WOULD REFUTE THIS.** A git version where `commit -a` uses a temp index not named `index.lock`, or where a pathspec commit *does* use `index.lock`. My measurement is one version on one machine — `test_the_notice_is_reachable_from_a_real_git_commit` re-derives both ends through real `git commit` invocations rather than set variables, so a version change fails the test rather than silently passing.

**I checked the other holes in attack 2 and did not find them.** Worktrees, `GIT_DIR`, and the `/tmp` vs `/private/tmp` symlink divergence all *widen* the mismatch (`GIT_INDEX_FILE` comes back `/tmp/…`, `--absolute-git-dir` `/private/tmp/…`), so they cause the notice to fire, never to be missed. The `*/index` escape catches the relative `.git/index` form git actually emits.

---

### 3. The citation splice and its own `check()` do not read the same file — MEDIUM (latent)

**WHAT.** Attack 3, answered: the `txt[start:end] != str(line)` guard does **not** catch every case. `check()` reads `errors="replace"`; `repair()` read `errors="strict"`. Two disagreements, both reproduced:

- **Invalid UTF-8** — `check()` decodes and reports a finding; `repair()` raised before any guard could run. The hook's `|| true` swallows it, so `--fix` dies mid-pass, every remaining citation ships stale, and HEAD is broken in a clone. That is *the round-14 failure re-entered through the repair that exists to close it*.
  ```
  check-mode read OK, len= 54 offset of 10934: 43
  repair-mode RAISED: UnicodeDecodeError 'utf-8' codec can't decode byte 0xff in position 0
  ```
- **CRLF** — `read_text` translates `\r\n`→`\n` in, `write_text` writes `\n` out. Repairing one line number silently rewrites **every line ending in the file**. The offset guard passes here (offsets agree); the damage is in the write. Under FIX 1 that whole-file rewrite is now auto-staged and committed.
  ```
  read back repr: 'alpha\nsee x.py:1234 here\nomega\n'
  CRLF survived : False
  ```

**Reachability today is zero** — 862 citing files scanned, `invalid UTF-8: 0`, `contains CRLF: 0`. That is exactly why it needs a guard and not a note.

**FIX (delivered).** One byte round-trip in `repair()`: `raw = path.read_bytes()`, `txt = raw.decode("utf-8", errors="replace")`, and if `txt.encode("utf-8") != raw` the file is REFUSED with a message and the rest of the pass continues. That single predicate catches both modes and *proves* the offsets `check()` computed index the text being spliced. Write is `write_bytes`, so newlines are not retranslated on the way out.

**RED PROOF** (strict read + `write_text` restored):
```
E       assert b'\r\n' in b'`sym` is at t.py:1\nand more\n'
E   UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
FAILED ...::test_a_crlf_file_is_not_rewritten_end_to_end
FAILED ...::test_an_invalid_utf8_file_does_not_abort_the_pass
```

**WHAT WOULD REFUTE THIS.** A demonstration that no citing file can ever acquire CRLF or non-UTF-8 bytes — `.gitattributes` enforcing LF and a pre-commit encoding check would do it, and neither exists. Or a demonstration that `read_text`/`write_text` preserve CRLF (they do not, shown above).

---

### 4. Attack 5 — the `usage:` criterion: I could not find a member of the class — SOUND

Executed all 54 measurement scripts with `--help` and timed each:

```
n = 54
   secs  rc   bytes  name
   0.99   0     565  drift_scan_scope_2026-09-08.py
   ...
   0.20   0     815  verify_five_stage_chain.py

scripts taking >1.0s to answer --help: 0
```

Every one returns inside a second — interpreter start plus imports, no measurement. The three shortest outputs, which I read individually, are ordinary `argparse` help. The five hand-rolled helpers (`competence_provenance`, `materiality_population`, `note_vagueness_lint`, `quote_exemption_effect`, `target_mutation_arrival`) all print then exit. **The class is empty at this HEAD.** The criterion remains necessary-not-sufficient in principle — a script whose output merely *contains* a line starting `usage:` would score as answering — but no such script exists here. *Refuted by:* a script whose measurement output contains a `usage:`-initial line, or one that prints usage and continues.

### 5. Attack 4 — nothing invokes the wired scripts with an argument — SOUND

Ripgrepped the whole repository (shell, Makefile, yml/toml/cfg, md, json, py) and `~/Desktop` for each of the 31 wired basenames followed by a non-comment token. Zero invocations with arguments. The only hits are prose mentions and `test_operational_scripts.py`'s own `--bogus` refusal assertion. `shell=True` call sites name none of them. *Refuted by:* an operator habit or an external script outside the repo and Desktop — which I cannot see.

*(Bookkeeping, not a finding: 31 files carry `from _cli_help import answer_help`, not 30. The 31st is `help_is_answered_2026-09-11.py`, the producing script itself.)*

---

## CAN A REPAIR STILL MISS THE COMMIT

**Partial staging: it could not miss, it could over-reach — and now it does neither.** Confirmed by execution (Finding 1). Fixed by index-only 3-way merge. One residual case remains where the repair *does* lag: when the repair and an unstaged hunk collide within merge context. I chose that deliberately over staging conflict markers or the author's WIP, and it is loud rather than silent. Verified end-to-end: `HEAD` keeps the clean staged content, the worktree keeps the WIP, the message names the remedy.

**Temporary index: the repair reaches the commit.** Re-measured. `git commit -- <path>` sets `GIT_INDEX_FILE` to `<gitdir>/next-index-<pid>.lock`, the hook's `git add`/`update-index` write *that* index, and the commit carries them. The brief's claim is correct. What I changed is the notice's trigger, not the mechanism.

**The `git add` failure path still lags silently-ish.** `cdsfl_restage_paths`'s `else` branch prints "it will lag a commit behind" to stderr and the commit proceeds. That is the original design (stage 0 never refuses) and I did not change it — but it means a git failure produces exactly the round-14 defect with one stderr line as the only warning. Not fixed; flagged.

---

## FIGURES I RE-RAN

| Figure | Source | Result |
|---|---|---|
| not answering `--help`: **0/54 = 0.0000%** | `scripts/help_is_answered_2026-09-11.py` | reproduced exactly |
| Wilson 95% **[0.0000%, 6.6414%]** | same | reproduced exactly |
| Clopper–Pearson 95% [0.0000%, 6.6032%] | same (statsmodels/beta; scipy agrees to 1.4e-17) | reproduced; second tool present as required |
| citation guard, 0/6 outside symbol, Wilson [0.0000%, 39.0334%] | `citation_content_guard_2026-09-10.py` | green after my patch |
| citing-file population: 862 files, 0 invalid UTF-8, 0 CRLF | my probe | new |

**The pre-fix 30/53 = 56.6038% figure I could NOT reproduce.** It requires `git checkout d92564e^`, and this panel sandbox is not a git repository (`git status` exits 128). I take it on the brief's word and on the committed-alongside script; I did not verify it.

---

## WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

No other seat's output was available to me, so nothing here is agreement or disagreement with a seat. I disagree with **the brief's own Section 2 claim** that FIX 1's mitigation suffices: *"The helper stages ONLY the exact paths a repair reports changing"* is offered as the answer to sweep-in, and Finding 1 shows by execution that it is not. I also disagree with the brief's framing of the pathspec notice as *"a notice, which never refuses"* being adequate — a notice that fires on the wrong command is worse than none, because it trains the reader past the real one.

I **agree** with FIX 2's diagnosis and repair. The positional splice with a right-to-left order and a digits-at-offset guard is correct, and I found no way to defeat it that was not a read/write inconsistency (Finding 3) rather than a splice fault.

---

## WHAT I DID NOT CHECK

- **Attack 6 is not fully answered.** I proved by execution that all 54 answer `--help` without doing work, and the helper is a no-op on empty argv. I did **not** execute all 31 wired scripts with *no* arguments and compare against a pre-fix baseline — there is no git here to produce the baseline, and several scripts take minutes. A diff is not proof and I do not have an execution. This is the largest gap in my verdict.
- **The full suite.** Not run (>8 min). Targeted regression: **109 passed, 1 failed** across the 8 neighbouring test files. The one failure is `test_measurement_survey_is_safe_2026-09-11.py::test_running_the_measurement_set_leaves_the_tree_untouched`, and it is a sandbox artefact, not my edits: it asserts `git status` returns 0 before comparing, and this tree has no `.git` (exit 128, confirmed). That assertion is cc2's round-12 anti-vacuity guard doing exactly its job. My edits touch three files none of which that test imports.
- **The clone-at-HEAD claim itself.** I could not clone and could not confirm the 3-failure → 0-failure transition.
- **`git merge-file` behaviour under exotic modes** — symlinks, submodule gitlinks, files with the executable bit changed but content unchanged. `cdsfl_stage_repair_delta` reads the existing mode from `git ls-files --stage` and preserves it, but I tested only regular 100644 files.
- **Concurrency.** Two commits racing the same `CDSFL_SNAPDIR` — each hook run gets its own `mktemp -d`, but I did not test it, and the snapshot directory is never removed (it is in `$TMPDIR`, so the leak is bounded by reboot rather than by me).

<!-- verbatim-end -->

## Seat: fable

<!-- verbatim-begin: fable (Max subscription, panel round 14) -->

**VERDICT: READY WITH EXCEPTIONS** — the 3 fixes close what they claim; I found and repaired 4 above-threshold defects in them (attack 1 and attack 2 of the brief are real, plus 2 the brief did not name), all fixed and tested in my tree.

## FILES I LEFT IN THE TREE

1. `hooks/stage0_restage.sh` — modified: pre-repair snapshot + zero-context delta staging (`cdsfl_snapshot_unstaged`, `cdsfl_stage_repair_delta`); `index.lock` added to the notice's silent patterns.
2. `hooks/pre-commit` — modified: calls `cdsfl_snapshot_unstaged` before any repair (line 151, ahead of the ledger block at ~line 178); both repair display greps widened to `REFUSED|Traceback|Error`.
3. `scripts/citation_content_guard_2026-09-10.py` — modified: `repair()` refuses an undecodable file per-file instead of crashing the whole pass.
4. `bench/tests/test_round14_restage_and_repair_2026-09-11.py` — new, 4 tests, all runnable falsifiers; run RED against the pre-fix tree first (`3 failed, 1 passed`), GREEN after (`4 passed`).

## FINDINGS

**F1 — The re-staging sweeps the author's unstaged hunks into the commit (brief attack 1: CONFIRMED).**
**WHERE:** `hooks/stage0_restage.sh`, `cdsfl_restage_paths` (`git add -- "$_p"`).
**EVIDENCE:** constructed in a scratch repo — author stages hunk A, leaves "UNSTAGED SECRET" unstaged, repair edits the same file, hook restages:
```
--- WHAT LANDED IN THE COMMIT:
line1 STAGED-EDIT
cite runner.py:50
UNSTAGED SECRET
SWEEP-IN CONFIRMED: unstaged hunk committed
```
The "only paths a repair reports" mitigation is **insufficient**: it narrows across files, not within one, and the repaired files (notes, task list) are exactly files an author partially stages.
**FIX (delivered):** snapshot pre-repair working-tree blobs (`git hash-object -w`) before repairs run; for a path with pre-existing unstaged edits, stage only the repair's delta via a zero-context patch and `git apply -p2 --cached --unidiff-zero`; on any failure, loud skip (reported lag, not silent sweep). I tried `git merge-file` first per the brief's "stash-style isolation" hint and it **conflicts on the common geometry** (repair edit adjacent to the unstaged hunk — `merge-file rc=1`, quoted above), which is why the fix is zero-context apply anchored on the replaced line's own content.
**TEST:** `test_partial_staging_is_not_swept_in` — RED pre-fix (`AssertionError: the hook's re-staging swept the author's unstaged hunk`), GREEN post-fix; also asserts the repair still reaches the commit and the secret stays unstaged (` M note.md`).
**WHAT WOULD REFUTE THIS:** a demonstration that `git add -p` followed by a same-file repair cannot occur in this workflow, or a git version whose `git add` stages hunks selectively.
**SEVERITY: HIGH** — puts content at HEAD the author deliberately excluded.

**F2 — The pathspec notice fires falsely on every `git commit -a` and `--include` (brief attack 2: hole found).**
**WHERE:** `cdsfl_warn_if_partial_commit`, the `case` patterns.
**EVIDENCE:** measured in a scratch repo: `git commit -a` → `GIT_INDEX_FILE=$GIT_DIR/index.lock` → `NOTICE FIRED`, telling the author "this is a pathspec commit … git status will read MM after" — all false there: the locked index *becomes* the real index, so the repair lands in both and no MM results. `--include` measured identically (`index.lock`). A notice wrong on the ordinary case stops being read — the same decay path as a guard that cannot fail, in mirror image.
**FIX (delivered):** `index.lock` suffix patterns added to the silent set; the pathspec temp index is `next-index-<pid>.lock` (measured: `next-index-36860.lock`) and still fires.
**TEST:** `test_notice_is_silent_on_commit_a` (RED pre-fix, quoted assertion above) + `test_notice_fires_on_pathspec_commit` (kept firing; mutation-checked — silencing `*/next-index-*.lock` turned it red: `1 failed`).
**WHAT WOULD REFUTE THIS:** a git version or commit mode where `index.lock` in hooks does *not* become the real index — e.g. evidence that `git commit -p` uses `index.lock` for a genuinely partial commit (I did not test `-p`; it is interactive).
**SEVERITY: MEDIUM** — wrong statement printed to the founder on a routine command.

**F3 — One undecodable citing file silently aborts every citation repair (brief attack 3: resolved as crash, not mis-splice).**
**WHERE:** `citation_content_guard_2026-09-10.py::repair`, strict `read_text` vs `check()`'s `errors="replace"`.
**EVIDENCE:** `STRICT READ RAISES: 'utf-8' codec can't decode byte 0xff in position 7` where the replace-read succeeds. The splice can never land in the wrong place — if strict read succeeds the two decodes are identical, and the `txt[start:end] != str(line)` guard covers the rest — but the crash propagates out of `repair()`, the hook's `|| true` swallows it, and **no repair lands for any file**: the one-commit-behind defect this round exists to close, reintroduced by one bad byte in one note. (Reading with `errors="replace"` in repair instead would be worse: write-back swaps real bytes for U+FFFD.)
**FIX (delivered):** per-file try/except; undecodable file is `REFUSED … nothing written` to stderr (now surfaced by the widened hook grep), remaining files repaired.
**TEST:** `test_repair_survives_an_undecodable_citing_file` — RED pre-fix (`UnicodeDecodeError`), GREEN post-fix; asserts the good file is repaired, the bad file's bytes untouched.
**WHAT WOULD REFUTE THIS:** proof every current and future file matched by `SEARCH` is valid UTF-8 — untenable, since `check()` uses `errors="replace"` precisely because it isn't guaranteed.
**SEVERITY: HIGH** — restores the round's headline defect via a single file.

**F4 — A crashed repair was invisible at commit time.**
**WHERE:** `hooks/pre-commit`, both `_LEDGER_OUT`/`_CIT_OUT` display greps.
**EVIDENCE:** a traceback contains neither `refreshed`, `repaired`, `->` nor (pre-F3) `REFUSED`; `|| true` eats the exit code — executed demonstration above shows the old pattern printing nothing for `Traceback…ValueError: boom`, the new one surfacing both lines, and a clean run printing nothing (count 0).
**FIX (delivered):** greps widened to `…|REFUSED|Traceback|Error`.
**WHAT WOULD REFUTE THIS:** a Python failure mode that exits non-zero with no `Traceback`/`Error` token — exists (`sys.exit(3)`), so this is mitigation, not proof; the suite guards remain the backstop.
**SEVERITY: MEDIUM.**

**F5 — The absolute-path removal class is not empty (no fix applied — outside the entry's claim, inside its principle).**
`scripts/decision_label_staleness_2026-09-09.py:29` pins `~/.claude/projects/-Users-georgejackson-…/a07b3790….jsonl`, and `scripts/cdsfl_sv.py:1302` similarly — machine-specific inputs that make those scripts measure this machine wherever launched. The two *named* removals are done (only comments remain in `absorb_rule_disagreement`; `deepseek_falsifier_supply` clean). **REFUTED BY:** a ruling that transcript-reading instruments are maintainer-machine-only by design. **SEVERITY: LOW.**

## CAN A REPAIR STILL MISS THE COMMIT

Yes, in exactly two ways, both now **loud**: (1) the delta-apply fallback (zero-context patch fails to apply) prints `NOT auto-staged … will lag a commit behind` — executed in the merge-file debug run above; (2) an undecodable file's citations stay stale, `REFUSED` printed, report-mode guard stays red in the suite. The temporary-index attack: hook `git add`/`git apply --cached` reach the pathspec commit via `GIT_INDEX_FILE` (measured, `next-index-*.lock`), so repairs land there too; the notice for that case still fires. Ran: 3 scratch-repo probes, 4 new tests, mutation check.

## FIGURES I RE-RAN

- `help_is_answered_2026-09-11.py`: **0/54 = 0.0000%, Wilson [0.0000%, 6.6414%]** — matches the brief exactly; manual Wilson derivation agrees with statsmodels to <1e-12 for both 0/54 and 30/53; Clopper-Pearson 30/53 [42.2826%, 70.1608%] reproduced.
- The **pre-fix 30/53 is NOT re-executable here**: the panel sandbox is not a git repository (`git rev-parse` exits 128), so `d92564e^` cannot be checked out. Arithmetic verified; measurement not.
- All 31 wired scripts (brief says 30 — I count **31** excluding `_cli_help.py`; the "+ wired into 30 scripts" figure is off by one or counts differently — worth one line of correction): `--help` answers with usage, bogus flag exits 2, max `--help` wall time 2.08s (`who_catches_the_defects` — scipy/statsmodels import cost above the `__main__` guard, no work done). "usage:-but-still-works" class: empty over the surveyed set — every manual-usage printer (`competence_provenance`, `materiality_population`, `quote_exemption_effect`, `ffafp_cycle_gamma`, `note_vagueness_lint`) raises `SystemExit`/returns immediately after printing.
- Tests: pre-fix `3 failed, 1 passed`; post-fix `4 passed`; mutation `1 failed`; neighbours + mine `62 passed, 2 skipped in 15.63s`; `test_operational_scripts -k unknown_flag`: `114 passed` — the taught scan genuinely routes wired scripts into the executed branch (it is not the vacuous double-assert it resembles at line 1381; that branch only re-states its own guard, the wired scripts fall through to a real subprocess execution).

## WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

With CC1's own text in `stage0_restage.sh`: "an unrelated work-in-progress edit is never swept into a commit" was **false as written** (F1) — true across files, false within one; and the pathspec notice, built explicitly to avoid "a check that compared a variable with itself", shipped with the inverse defect: a check that fires when nothing is wrong (F2). Both claims were measured-sounding prose sitting on an untested case.

## WHAT I DID NOT CHECK

`git commit -p`/`--interactive` index naming; paths containing spaces through `git apply -p2` (quoted-path handling untested); the full pre-commit hook end-to-end with all 8 guards (needs a full clone with git history); the Desktop mirrors (outside the sandbox); the full suite (prohibited by budget); whether `who_catches_the_defects`' 2s import cost matters anywhere; the 2 skipped tests' skip reasons; reproducing 30/53 at `d92564e^` (no git here — the one part of `measured-rate-travels-with-its-script` this dispatch could not exercise).

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round14_2026-09-11/` holds the brief, both seat replies, both tool logs, the canonical-touch attribution and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed at `experimental_notes/evidence/panel_records_2026-09-11/panel_round14_2026-09-11/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.

Written under CDSFL note standard v1.7 (26 August 2026).
