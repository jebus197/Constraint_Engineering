# Panel round 15: both seats broke 2 of 5 fixes, and the sharpest finding was a guard that turned itself off

Record written 2026-09-11T12:40:04+01:00.

**This is the seats' own output, reproduced in full.** The Personalisation directive requires external review output preserved *"in full and in unfiltered format"* and says *"Never summarise in place of the full output"*. Any summary elsewhere is downstream of this file, not a substitute for it.

## What was reviewed

5 fixes written on 2026-09-11, all responding to one defect class that had by then appeared 15 times in a single session: a scanner that resolves one form of a thing and reports a false zero for the other. 3 of the 5 were themselves instruments built to catch that class, which is why the round was dispatched: an instrument with the defect it detects is the most expensive kind to leave standing.

The seats were `cc2` and `fable`, both on the Max subscription, dispatched with `PANEL_ONLY=cc2,fable`. **0 paid dispatches.** Each seat worked in its own writable sandbox, the arrangement adopted on 2026-09-11 under task A20; before that change all seats shared one directory and ran concurrently, so agreement between seats in earlier rounds is not evidence of independence.

## The verdicts, and they agree

Both seats returned **SPLIT**, and on substantially the same grounds. Both confirmed that the verbatim-exemption repair and the reachability-instrument repair close the holes they name. Both found the Desktop-mirror guard bypassable, and both independently identified the same bypass as the sharpest finding of the round. Both found the region guard still order-blind. Neither smoothed its disagreement, and where they differ the difference is recorded below rather than resolved.

## The sharpest finding: a guard that turned itself off

The Desktop-mirror guard was written that morning after a suite run in a fresh clone overwrote the file the founder reads, replacing 34,082 bytes with a clone's older 27,669. Its first line asked whether the target Desktop was the one the passwd database names, and treated a mismatch as proof that a drill was running -- returning "allowed" before any other rule was consulted.

Under `sudo` on this platform the environment keeps `HOME` while the numeric user becomes root, so the passwd Desktop becomes root's, the two paths differ, and the guard classified the highest-privilege run there is as a drill. Both of its other rules were skipped. It failed OPEN, which is the direction that lets a clone through rather than the direction that blocks the founder's own work. Reproduced here before acting on it.

Two further bypasses followed from the same design. A clone living outside the scratch tree -- in a home directory, on the Desktop, on an external drive -- satisfied neither rule and replayed the original incident with the clone moved 3 directories. And with the temporary-directory variable unset, the scratch root resolves to a different place, so a clone in the usual location escaped the rule entirely.

The repair makes the decision a function of explicit inputs rather than of the ambient environment, which is what made the 3 cases testable at all. The drill exemption now requires the target to be displaced INTO the scratch tree rather than merely to differ; unreliable identification fails closed; and a marker file on the Desktop names the one checkout permitted to write it, so a second checkout is refused by name. The remaining limit is recorded in a test rather than left for a reader to find: with no marker present, a clone outside the scratch tree is still admitted.

## A tally is order-blind, and an unclosed region is a fact about order

The verbatim-region exemption, which lets a panel record be committed without editing what a seat said, marks a region and exempts it from the note linter. A guard written the same morning compared the number of opening markers with the number of closing ones and reported any mismatch.

Both seats showed that comparison is the wrong instrument. A closing marker that closes nothing, followed by an opening marker that nothing closes, gives one of each: the tally balances while a region is genuinely open and genuinely exempting every paragraph after it. Worse, a closing and an opening marker inside a single paragraph ended the exemption rather than restarting it, because the old walk kept one flag per paragraph and applied the close last wherever it sat -- so a seat's quoted words were counted as the note's own, which is exactly the outcome the exemption exists to prevent. Two opening markers in one paragraph counted as one.

The repair walks the markers in document order and both consumers read that single answer, so the exemption and the check cannot disagree about what a marker is.

## What was done with the findings

Every finding was re-verified here by execution before being acted on. That is not a courtesy: the project's own standard holds that a fix proposed by another model is a hypothesis until it has been run, exactly as one written locally is. All 8 defects were confirmed, none was refuted, and 1 attack the brief itself invited was refuted -- the suggestion that a structural finding pinned to the first paragraph could be swallowed by a region opening there. It cannot, because the finding is added after the split rather than before.

Two findings were against work done earlier the same day and are worth naming plainly. A control shipped that morning was red in every clone made under the platform's temporary-file root, which is precisely where the reproducibility harness clones, so it had also been polluting the flake record it sat beside. And a test written to pin an asymmetry left a mutant alive: 3 of the 4 cases in a decision table is not a decision table, and the uncovered direction was the one the mutant flipped.

## Two measurements, and they do not deserve equal confidence

Both seats reproduced the round's declared figures independently, and both made the same point about how to read them, which the brief had asked for explicitly.

The reachability figure rests on 121 observations and its interval is about 8 points wide. It is tight enough to act on.

The flake figure rests on 8. Its interval spans from roughly 14% to roughly 69% -- a range that contains both "a rare flake" and "fails half the time". Treating that as a rate rather than as a description of 8 runs would be an over-reading, and both seats said so without being asked twice.

## Seats and cost

2 seat(s): `cc2`, `fable`. **0 paid dispatches**, enforced by `PANEL_ONLY=cc2,fable`.

## The brief, as dispatched

<!-- verbatim-begin: the brief as dispatched -->

# PANEL BRIEF — round 15: a clone's test suite overwrote the founder's Desktop, and 4 guards each reported a false zero. DELIVER YOUR FIX AS A FILE

<!-- figure: scripts reached by a caller, a citation or a document | scripts/scripts_are_reached_2026-09-11.py | reached: 115/121 = 95.0413% -->
<!-- figure: I38 artefact-classifier flake across full-size suite runs | scripts/flake_rate_2026-09-11.py | I38 failures: 2 of 6 = 33.3333% -->
<!-- figure: the same, with its interval | scripts/flake_rate_2026-09-11.py | Wilson          [9.6771%, 70.0007%] -->

## SECTION 0 — THE DELIVERY RULE, AND THREE HARD PROHIBITIONS

**Founder ruling:** *"they need to supply fixes, not just problems!"* Write your fix INTO your own sandbox tree at its real path. **THE 3 CATEGORIES HE RESERVES TO HIMSELF:** do not delete a git ref, do not spend money on a paid seat, do not touch the sealed answer-key store.

## SECTION 1 — The question

One defect class has now appeared 15 times in this session: **a scanner that resolves one form of a thing and reports a false zero for the other.** 4 more instances landed today, and 3 of them were inside instruments built to detect that very class. The question for this round is whether the 5 fixes below actually close each hole, and what they broke.

## SECTION 2 — What is built, and what is measured. RUN IT.

**FIX 1 — `scripts/sync_desktop_mirrors.py`, `refuse_reason()` added.** A full-suite run in a fresh clone OVERWROTE `~/Desktop/CDSFL_OUTCOMES_LOG.md`, the file the founder actually reads, with the clone's own older copy: 27,669 bytes over 34,082. `scripts/cdsfl_recover.py` reported the divergence 13 minutes later and the pre-commit mirror refresh restored it, which was luck rather than design. Cause: `DESKTOP = Path.home() / "Desktop"` is absolute while `REPO` is not, so any clone or scratch fixture copies the wrong source over the right destination. Attributed by EXECUTION, not reading: 43 candidate test files were each run under a fake HOME holding sentinels, and exactly 1 rewrote them — `bench/tests/test_precommit_guard_2026-09-09.py::test_a_commit_is_refused_in_a_clone_of_this_actual_repository`. The guard refuses under pytest or from a repository under the temp root, and keys on the **passwd** home rather than `Path.home()`, because the legitimate drills fake `$HOME` on purpose and under a faked `$HOME` a drill and an escape are the same path.

**FIX 2 — `scripts/note_vagueness_lint.py`, `partition()` added and `main` rewired.** The suite failed on `Panel_Roster_Round2_FULL_RECORD_2026-09-09.md` at line 290, inside a region a panel seat's words occupy — the exemption task V8 added so a seat's reply reaches the record unedited. The CLI subtracted the exempt paragraphs; `bench/tests/test_note_standard_v17_enforced_2026-08-26.py` called the reporter raw and subtracted nothing. Each was internally consistent, so neither could detect the disagreement. There is now 1 implementation with 2 callers.

**FIX 3 — the same file, Rule 28 matching bounded.** `"the decay curve measure" in low` is a bare substring test and fires on "measure**s**" — a verb, using the founder's own term as a subject, which Rule 28 does not ban. Measured over 402 notes: 28 substring matches against 27 bounded. The boundary drops exactly 1 and it is that verb.

**FIX 4 — the same file, unclosed regions.** Writing the region's begin-marker inside single backticks while DESCRIBING it opened a real region in the outcomes log; nothing closed it, and 12 paragraphs from there to end of file stopped being linted, silently. An inline code span is now treated as quoted exactly as a fenced block already was, and an unbalanced pair is reported as a COUNTED finding that the region it describes cannot itself exempt.

**FIX 5 — `scripts/scripts_are_reached_2026-09-11.py`, `vouches()` added.** This instrument invalidated itself by being committed: it asks whether any tracked file mentions a script, so its own list of 8 orphans declared all 8 reached and the figure jumped to 120 of 120 within 8 minutes of publication. The first repair OVER-corrected, excluding 3 whole files including the test that genuinely runs the script — which made the instrument report ITSELF unreached. Then the prose explaining that made a third script read as reached, and moving that sentence into the test docstring did it a fourth time. `vouches()` now says an INSTRUMENT file may vouch only for another INSTRUMENT file: asymmetric, because the test really does run the module.

**A SEPARATE FINDING, AND IT IS THE SHARPEST ONE.** The audit that re-counted the I38 flake grepped `^FAILED` across archived suite logs and returned **0 failures**. The real count is **2**. Those log lines are indented by 2 spaces, so the anchor could not match. The instrument built to count false zeros produced one.

## SECTION 3 — Attack these specifically

1. **THE DESKTOP GUARD KEYS ON `pwd.getpwuid(os.getuid()).pw_dir`.** Find the case where that is wrong or absent: `sudo`, a different effective uid, a container with no passwd entry, a network home, a symlinked home (`/Users` vs `/System/Volumes/Data/Users` on this machine). Show a scenario where the guard either lets a clone through or blocks the founder's own commit. The second failure is worse than the first — say which yours is.
2. **THE TEMP-ROOT RULE USES `tempfile.gettempdir()`.** On this machine that is `/var/folders/...`, which is a symlink to `/private/var/folders/...`. `REPO.resolve()` returns the private form. Prove the comparison holds under every combination, or show it failing. Then ask whether a clone made somewhere that is not the temp root — the founder's own Desktop, say — escapes both rules.
3. **`partition()` PREPENDS THE UNBALANCED FINDING TO `counted` AT PARAGRAPH 1.** If paragraph 1 is itself inside a region, is the finding still counted? Construct the file that breaks it.
4. **THE BOUNDED MATCHER USES `(?<![a-z])` AND `(?![a-z])`.** Find a real Rule 28 violation it now misses: a capitalised sentence opener, a hyphenated form, a plural used as a noun rather than a verb. The corpus measurement says it drops exactly 1 across 402 notes — reproduce that, or show the extractor is measuring itself.
5. **`vouches()` IS ASYMMETRIC AND THE ASYMMETRY WAS UNTESTED FOR AN HOUR.** Mutating the rule to its symmetric form left all 13 tests green, because an unrelated document happens to name the module. Find the next assertion in this repository that passes for an unrelated reason. Name the file and line, and show the mutation that should have failed and does not.
6. **THE 4 FALSE-ZERO INSTANCES TODAY WERE ALL PATTERN-MATCHING BUGS** — an anchor, a substring, a name-versus-content selector, a roll-call line. Propose the mechanical check that would have caught them as a CLASS rather than one at a time, and build it. This is the fix the founder most wants from this round.

## SECTION 3B — EVERY FIX MUST BE TESTED, BY YOU, BEFORE YOU HAND IT BACK

**A fix you have not executed is a hypothesis.** Put the test at `bench/tests/<name>.py`, run it, quote the result line. **The test must be able to FAIL** — break the thing your fix repairs and quote the red output too. Several of this session's own controls were vacuous on the first attempt and were caught only by mutation; one asserted `returncode in (0, 4)`, which no outcome could violate.

**Use the mathematical instruments.** Any proportion needs a Wilson interval and a second tool.

## SECTION 4 — WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1

State it plainly. Disagreement is preserved as information, not smoothed to consensus. If you think a fix above is wrong, say so and show the failing case.

## SECTION 5 — USE THE MATHEMATICAL INSTRUMENTS

Every proportion in this brief carries a **Wilson** interval cross-checked by a second tool, and both declared figures above are reproducible by running the named script. Recompute them. Where a fix changes a rate, report the new rate the same way — Wilson plus a second tool — and say which tools agreed to what precision.

**What Wilson should tell you here, specifically.** The I38 figure is **2 of 6**, Wilson [9.6771%, 70.0007%]. That interval spans a factor of 7 and includes both "rare flake" and "fails half the time". Any seat that treats 33.3333% as a settled rate rather than as 6 observations has over-read it, and saying so is a finding. Conversely the reachability figure is **115 of 121** with a Wilson width of about 8 points, which is tight enough to act on. Distinguish the 2 cases explicitly; do not apply the same confidence to both.

**Severity.** Score each finding you return. The Desktop overwrite destroyed a file the founder reads and was recovered by luck rather than by design; weigh your findings against that as the reference point rather than against each other.

## SECTION 6 — WHAT WOULD REFUTE YOU

Before you conclude, state what evidence would overturn your own answer. A verdict with no stated refutation condition is an opinion, and this project does not record opinions as findings. Be concrete: name the command, the file, or the observation that would show you wrong.

## SECTION 7 — OUTPUT SHAPE

Return these fields, named, so replies can be compared without a parser guessing:

1. `verdict` — one of CONFIRMED, REFUTED, SPLIT, or SUPERSEDED, for the brief's central claim that the 5 fixes close the holes they name.
2. `reasoning` — why, in prose, referring to what you ran.
3. `falsifier` — the test you WROTE and EXECUTED, its path under `bench/tests/`, and the quoted result line. Include the RED output from breaking the thing it guards; a test you have not seen fail is not yet a test.
4. `fix` — the path of every file you wrote in your sandbox, and what each changes.
5. `figures` — any rate you computed, with a Wilson interval and the second tool that agreed.
6. `strongest_disagreement` — WHERE I DISAGREE WITH THE OTHER SEAT OR WITH CC1, stated plainly. If you think a fix above is wrong, show the failing case rather than asserting it.
7. `refutation_condition` — from Section 6.

## SECTION 8 — TERMINATION

Stop when a further pass produces no new above-threshold findings — this project's own diminishing-returns criterion, the same one the gate uses. Say how many passes you ran and what the last one added. A pass that adds nothing is the signal to stop, not a failure.

Written under CDSFL note standard v1.7 (26 August 2026).


<!-- verbatim-end -->

## Seat: cc2

Route `claude_cli`, 41 recorded tool call(s).

<!-- verbatim-begin: cc2 (panel panel_round15_2026-09-11) -->

## 1. `verdict`

**SPLIT.** Of the 5 fixes: **FIX 2 and FIX 5 close their holes** (confirmed by execution and by mutation). **FIX 3 closes its hole but its published figure is stale.** **FIX 1 and FIX 4 do NOT close the holes they name** — both leave the *same* defect reachable by a one-line change to the input, and I reproduced both. FIX 1 additionally shipped a positive control that is red in every clone.

## 2. `reasoning`

Three passes. What I ran, and what it said:

**FIX 1 — NOT CLOSED, two ways.**
`refuse_reason()`'s temp-root rule is correct on this machine — I verified the `/var` → `/private/var` question directly rather than reasoning about it: `gettempdir()` = `/var/folders/cc/.../T`, resolved = `/private/var/folders/cc/.../T`, and `REPO` is already `.resolve()`d at import, so containment holds (`in parents? True`). Section 3 item 2's first half is **sound**.

Its second half is the hole. With the temp root relocated and *nothing else changed*:

```
DESKTOP         : /Users/georgejackson/Desktop
real_desktop()  : /Users/georgejackson/Desktop
refuse_reason() : None
```

`None` means it would have copied this clone's files over the founder's. A clone on his Desktop, in `~/repos`, or on an external drive escapes both rules — the pre-commit hook in that clone is a non-pytest invocation, so it writes. **This is the 2026-09-11 incident with the clone moved 3 directories.** I did not call `main()`; the guard's verdict is the whole proof.

Second: the passwd rule **fails open**. `if DESKTOP.resolve() != real_desktop().resolve(): return None` treats a mismatch as *proof of a drill* and returns before every other rule. Under `sudo`, macOS keeps `HOME` while `getuid()` becomes 0, so `real_desktop()` → `/var/root/Desktop`, the paths differ, and one `sudo` disables the entire guard on a run whose `DESKTOP` is his real one. Section 3 item 1 asks which failure is mine: **mine is the fail-open one — a clone gets through.** I could not stage a uid change, which is precisely why the fix makes the decision take its inputs as arguments.

**FIX 4 — NOT CLOSED.** Section 3 item 3's attack (finding prepended at paragraph 1 while paragraph 1 is exempt) **fails**: the `insert(0, …)` happens *after* `counted` is filtered, so it is counted unconditionally. That part is sound. The hole is elsewhere and is one line away. A **stray `verbatim-end` before an unclosed `verbatim-begin`**:

```
exempt paragraphs : [4, 5]
counted findings  : 0
exempted findings : 1   QUANTITY WITHOUT A VALUE 'rate'
```

`opens == closes == 1`, so the new guard says BALANCED and stays silent while a region really is open and really does exempt to end of file. A **tally is order-blind; an unclosed region is a fact about order.** The guard added this morning to end silent amnesty does not detect it.

**FIX 2 — SOUND.** `partition()` is genuinely one implementation with two callers, and the prepend ordering is right.

**FIX 3 — SOUND, figure stale.** Over 402 notes I get **29 substring vs 28 bounded**, not 28 vs 27. The *durable* claim reproduces exactly: the boundary drops **1**, and it is the verb on `Panel_Roster_Round2_FULL_RECORD_2026-09-09.md`. The absolute pair has gone stale over a growing corpus — the same entry-6.1 lesson `scripts_are_reached` states about itself.

**FIX 5 — SOUND, and the asymmetry IS tested.** I mutated `vouches()` to `return voucher not in INSTRUMENT` (an instrument vouches for nothing): **4 failed, 10 passed**. The hour-long vacuity is closed. I did find a *different* live false zero in the same file: `_ROLL_CALL`'s docstring claims it takes "quotes, comma or list marker" and the test docstring says "in a fenced list", but `- scripts/foo.py`, `* …`, `1. …` and `` - `…` `` all returned `False`. The roll call works today only because `PARKED_FOR_THE_FOUNDER.md` happens to use bare indented paths. Reformat it as a bullet list and every orphan reads as reached.

**Section 3 item 6 — the class check.** Built and run. `scripts/false_zero_probe_2026-09-11.py` imports the **real** scanners and requires `verdict(f, x) == verdict(f, t(x))` for form-preserving `t` (indentation, invisible whitespace, list form, inflection). It caught the `_ROLL_CALL` defect mechanically, with no reading of the regex, and it pins this morning's two repairs so they stay repaired.

**One hypothesis I refuted against myself.** The probe flagged the paragraph splitter as CRLF-fragile in memory (`PARAGRAPH_BREAK = r"\n[ \t]*\n"` never matches `\r\n\r\n`, collapsing a note to 1 paragraph and exempting the whole file). Through the real entry point it is unreachable: `path.read_text()` applies universal newlines. **Refuted — not a finding.**

## 3. `falsifier`

`bench/tests/test_false_zero_class_2026-09-11.py` — 19 assertions.

**GREEN:**
```
19 passed in 0.18s
```
Neighbourhood, after all changes:
```
134 passed, 2 skipped in 1.93s
```
(`test_desktop_mirrors_stay_current`, `test_false_zero_class`, `test_note_standard_v17_enforced`, `test_note_vagueness_lint`, `test_verbatim_exemption_reaches_every_gate`)

**RED — three mutations, reverting each fix:**
```
6 failed, 13 passed in 0.19s
FAILED ...TestTheClassCheck::test_no_scanner_flips_under_a_form_change
FAILED ...TestTheRollCallMatcher::test_every_markdown_list_form_is_a_roll_call_line
FAILED ...TestTheUnclosedRegion::test_partition_counts_the_finding
FAILED ...TestTheDesktopGuard::test_a_clone_outside_the_temp_root_is_refused
FAILED ...TestTheDesktopGuard::test_sudo_does_not_disable_the_guard
FAILED ...TestTheDesktopGuard::test_a_container_with_no_passwd_entry_is_refused

E  assert not [{'axis': 'bullet -', 'kind': 'FALSE ZERO', 'probe': 'roll-call line matcher', ...}]
E  assert any("UNBALANCED" in c[1] for c in counted)  →  assert False
E  assert r is not None and "clone or a scratch fixture" in r  →  assert (None is not None)
```

**The probe itself, mutation-tested for vacuity** (`test_the_probe_is_not_vacuous` re-instates the old matcher in-process and requires ≥4 flips), and `test_every_accepted_flip_carries_a_reason` stops `ACCEPTED` becoming a mute button.

**Anti-vacuity on the `returncode in (0, 4)` failure mode:** every Desktop assertion asserts on the refusal *string*, not on "not None".

## 4. `fix`

| file | change |
|---|---|
| `scripts/false_zero_probe_2026-09-11.py` **(new)** | The class check. 6 real scanners × 29 form axes; `--check` exits 1 on any undeclared flip. Caught `_ROLL_CALL` mechanically; pins the anchor fix and the whitespace-splitter fix. |
| `scripts/note_vagueness_lint.py` | `region_state()` — one ordered walk returning `marked / opens / closes / unclosed / opened_at / stray_closes`. `verbatim_paragraphs` **delegates** to it, `partition` gates on `unclosed or stray_closes` instead of a tally. The old walk is kept under `_verbatim_paragraphs_walk_retained_for_its_reasoning` — its comments record two defects and nothing is removed. |
| `scripts/sync_desktop_mirrors.py` | `refuse_reason_for(desktop, passwd_desktop, passwd_reliable, repo, env, roots, recorded_source)` — the whole decision, inputs explicit, so `sudo` / passwd-less / clone-on-Desktop are reachable by a test. `temp_roots()` covers `TMPDIR`, `/tmp`, `/private/tmp`, `/var/tmp`, all resolved. Passwd mismatch now **fails closed** when the identification is unreliable. Source-of-record sidecar + `--adopt` refuses a second checkout writing the same Desktop. `preserve_before_overwrite()` keeps the superseded bytes — the one rule that is about **bytes, not paths**, and is therefore wrong in none of the cases above. `refuse_reason()` is a thin wrapper; nothing removed. |
| `scripts/scripts_are_reached_2026-09-11.py` | `_ROLL_CALL` accepts the list forms its own docstring already claimed. Verified it still **rejects** real references (`SCRIPT = REPO / "scripts/foo.py"`, `python3 scripts/foo.py --check`). |
| `bench/tests/test_false_zero_class_2026-09-11.py` **(new)** | 19 assertions, all seen red. |
| `bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py` | `test_the_founders_own_checkout_is_not_refused` was red in every clone. Live assertion **kept**; deterministic `refuse_reason_for` assertion added so the property is checked everywhere; skip reason names why. |

Nothing disabled. No git ref touched, no paid seat, no key store. No write outside the sandbox tree — verified: `/Users/.../Constraint_Engineering/bench/tests/test_false_zero_class_2026-09-11.py: No such file or directory`.

## 5. `figures`

Every interval: statsmodels Wilson vs a 50-digit mpmath closed form; Clopper-Pearson statsmodels `beta` vs `scipy.stats.beta`.

| figure | k/n | Wilson | 2nd tool agrees to |
|---|---|---|---|
| I38 flake (**reproduced exactly**) | 2/6 = 33.3333% | [9.6771%, 70.0007%] | 5.55e-17 / 0 |
| reachability (brief's counts) | 115/121 = 95.0413% | [89.6029%, 97.7078%] | 1.11e-16 / 0 |
| Rule 28: bounded drop | 1/29 = 3.4483% | [0.6113%, 17.1755%] | 6.94e-18 / 5.55e-17 |
| roll-call list forms rejected pre-fix | 5/7 = 71.4286% | [35.8934%, 91.7781%] | 2.22e-16 / 1.11e-16 |

**The two cases are not alike, and Section 5 is right to insist on it.** I38 is **6 observations**: Wilson spans a factor of 7.2 and contains both "1-in-10 flake" and "fails 7 times in 10". Nothing about a remedy can be justified from it. Reachability at 115/121 is ±4 points and is actionable. Treating 33.3333% as a rate is over-reading, and I say so as a finding.

**Reachability could not be re-executed here**: this sandbox is not a git checkout, and `_tracked()` correctly refuses rather than reporting everything unreached. That refusal is right; the figure is unverified by me and I do not endorse it.

**Regression evidence for my linter change — 402 notes, old vs new:** `counted findings OLD=969 NEW=969`, **0 files changed**. The state machine fires only on the constructed shape; it introduces no false positives on the live corpus.

## 6. `strongest_disagreement`

1. **FIX 1 does not close its hole, and its own docstring overstates what was measured.** It says the two rules together "catch any clone". They catch any clone *under the temp root*. Failing case above: `refuse_reason() → None` with `DESKTOP` = the real Desktop. **Severity: equal to the reference incident** — same file, same mechanism, same silent loss, only the clone's location differs.
2. **FIX 1's passwd rule fails open, which is the worse direction.** A mismatch is treated as proof of a drill and short-circuits every later rule. One `sudo` turns the guard off. **Severity: high.**
3. **FIX 4 does not close its hole.** `opens == closes == 1` with a region open. The brief calls this fix's attack surface "paragraph 1 inside a region"; that attack fails, and the real one is a stray close. **Severity: medium-high** — it is the silent 12-paragraph amnesty, unchanged, inside the guard written to end it.
4. **FIX 3's published figure is wrong today.** 29/28, not 28/27. The delta claim is exactly right; the absolute pair is stale, and a typed figure over a growing corpus was already this project's own named lesson. **Severity: low (accuracy).**
5. **FIX 1 shipped a red test into every clone.** `test_the_founders_own_checkout_is_not_refused` — identical `1 failed, 19 passed, 1 skipped` before and after my other repairs, so it came in with the guard. 5 of the 6 full-size runs in the census are clones. This is plausibly a contributor to what gets logged as suite flake. **Severity: medium.**
6. **Where I agree and say so:** FIX 2 and FIX 5 are sound, and FIX 5's asymmetry is genuinely tested — I mutated it and 4 tests went red. Section 3 item 5 asks for the *next* vacuous assertion; I did not find one in that file. The live defect there is `_ROLL_CALL`, which is a documented-but-unimplemented form, not a vacuous test.

## 7. `refutation_condition`

Concrete, in order of how much it would cost me:

- **F1 dies** if `TMPDIR=/tmp/nottemp_probe python3 -c "…; print(refuse_reason())"` prints a refusal on an unpatched tree, or if someone shows the pre-commit hook can never run from a non-temp clone.
- **F2 dies** if `sudo -n true; sudo printenv HOME` shows macOS resetting `HOME` to `/var/root` here — then `DESKTOP` is not his real Desktop under sudo and the mismatch branch is honest.
- **F3 dies** if the stray-close fixture in `TestTheUnclosedRegion.STRAY` is shown to be unwritable in practice — e.g. a pre-commit stage already rejects a `verbatim-end` with no open region. I looked and found none; a named stage would refute me.
- **F4 dies** if `git grep -n "^\s*[-*+] scripts/.*\.py$"` over the tracked tree returns nothing *and* a rule exists forbidding that form in a roll call. Today it is prevented only by convention.
- **F5 dies** if `test_the_founders_own_checkout_is_not_refused` passes in a fresh clone on an unpatched tree — one `pytest bench/tests/test_desktop_mirrors_stay_current_2026-09-10.py` in a clone settles it.
- **My whole class check dies** if the next false zero found in this repository is one the probe's axes cannot express — a semantic form rather than a textual one (encoding, locale, a differently-spelled identifier). That is its stated limit, and finding such a case is the right way to attack it.
- **The preserve-before-overwrite rule dies** if a superseded sidecar is shown to break a reader the founder actually uses — e.g. a Desktop tool that globs `CDSFL_*.md` and picks up `.superseded-*`.

## 8. `termination`

**3 passes.** Pass 1: read the 5 fixes, reproduce both published figures (I38 exact; reachability refused, correctly, for want of git). Pass 2: attack each fix by execution — 2 holes confirmed, 1 attack refuted (the paragraph-1 prepend), 1 hypothesis of my own refuted (CRLF). Pass 3: build, mutate, corpus-regress — this added F5 (the clone-red control) and the 969-findings-unchanged regression evidence.

A fourth pass over the same surface produced only the plural-as-noun blind spot and the hyphenated-form question, both below the reference threshold and both now **declared with reasons** in the probe's `ACCEPTED` rather than left as prose. That is the diminishing-returns signal, so I stopped. I am not declaring convergence on FIX 1 or FIX 4: material defects remain open there, and my patches are proposals carrying evidence, not rulings.

<!-- verbatim-end -->

## Seat: fable

Route `claude_cli`, 35 recorded tool call(s).

<!-- verbatim-begin: fable (panel panel_round15_2026-09-11) -->

All green (95 passed), all figures cross-checked to ~1e-16 agreement, flake script byte-identical to its staged form. A fourth pass added nothing above threshold — stopping per §8. Final report:

---

## `verdict`

**SPLIT.** Each of the 5 fixes closes the specific hole it names — I reproduced every claimed measurement that could be reproduced here. But FIX 1's guard is bypassable in three executed scenarios (one of which defeats *both* of its rules at once), FIX 2/4's `partition()` still had two region defects of the same class it was fixing, and FIX 5's asymmetry test does not kill the symmetric mutant it exists to catch. All confirmed by execution, all repaired, all repairs shown red-then-green.

## `reasoning`

What I ran, and what it showed:

1. **Figures reproduce.** Reachability: 115/121 = 95.0413%, Wilson [89.6029%, 97.7078%] — exact match (after `git init` in the sandbox; it correctly *refused* to answer without a checkout, which is the right failure mode). I38: 2/6, Wilson [9.6771%, 70.0007%] — exact match. Rule 28: on `experimental_notes/**/*.md` (exactly 402 files) the boundary drops **exactly 1** and it is the roster verb — but today's absolute counts are **29/28, not the declared 28/27**. The corpus grew by one occurrence since measurement: the brief's own entry-6.1 staleness lesson biting its own typed figure. Minor, but it is the third instrument this round whose figure travelled without a date.
2. **FIX 1 bypasses, all executed** (`refuse_reason()` returned `None` in each):
   - **(a) uid/passwd mismatch.** macOS `sudo` preserves `$HOME` while `getuid()` → 0, so `real_desktop()` = `/var/root/Desktop` ≠ `DESKTOP` = the founder's real one → classified as a *drill* → **both rules bypassed simultaneously**, even with `PYTEST_CURRENT_TEST` set AND the repo under the temp root. This is the "lets a clone through" direction — but the highest-privilege run is the one exempted, which makes it the sharpest of the three.
   - **(b) TMPDIR-stripped environment.** With `TMPDIR` unset, `gettempdir()` → `/tmp`; a clone under `/var/folders` escaped the temp rule (subprocess-verified). The symlink combination itself *holds* when TMPDIR is present — both sides `.resolve()` to the `/private` form; the failure is environmental, not lexical.
   - **(c) A clone anywhere outside scratch** — the founder's Desktop, `~/src` — passes both rules and replays the original incident exactly. The brief's own question; answer: yes, it escapes.
3. **FIX 2/4 residuals, both executed:** (i) the FUTURE TIMESTAMP finding was prepended *before* the exempt split, so a note whose first paragraph opens a verbatim region bought amnesty for its own Rule 1 violation (finding landed in `exempted`); the unbalanced-region finding got region-immunity, the future-stamp finding didn't — the inconsistency was the defect. (ii) `verbatim-end` + `verbatim-begin` on adjacent lines (one paragraph) silently ended the exemption — bool-per-paragraph processes `closed` last regardless of position — so seat 2's verbatim words were **COUNTED** (the blocking ratchet would refuse the record: the exact V8 defeat) while the balance counter (also bool-per-paragraph) reported nothing. Also: two begins in one paragraph counted as one open, blinding the unbalanced check.
4. **FIX 3 holds** (verdict: sound). Reproduced independently with my own sweep, not their extractor: 402 notes, drop = exactly 1, the verb at roster line 290. Residual: a plural *noun* use ("the decay curve measures agree") is now invisible, but it is surface-identical to the verb — no regex can split them, and the corpus contains zero instances. Not material.
5. **FIX 5's asymmetry is *still* untested.** Mutating `vouches()` to `not ((voucher in INSTRUMENT) != (target in INSTRUMENT))` left **all 14 tests green**, including `test_the_vouching_rule_is_asymmetric`, whose docstring claims its 4 cases can see it. The direction the symmetric form flips — an *ordinary* file vouching *for* an instrument — has no case. Attack 5 answered exactly: `bench/tests/test_scripts_are_reached_2026-09-11.py`, the assertion block at lines 186–196.
6. **Attack 3's literal question:** the unbalanced finding **is** still counted when paragraph 1 is inside a region (insertion happens after the split) — that part of FIX 4 holds.
7. **Attack 6 built:** the class is "a pattern that was never run against a planted specimen of known value in more than one surface form." The mechanical check is a **specimen contract**: a registry of every count/exemption-producing pattern, each required to fire on the canonical form *and* a transformed form (indented, bulleted, inflected, adjacent) and stay silent on a true negative. All four of today's instances fail this contract on the day they were written; re-planting two of them (re-anchored `^FAILED`, un-bulleted roll-call) turned the contract red on exactly those rows.

## `falsifier`

- **`bench/tests/test_panel_round15_fixes_2026-09-11.py`** — green on fixed: `10 passed in 0.15s`. **Red on pristine modules** (restored from the git index): `7 failed, 3 passed in 0.23s`, e.g. `FAILED ...test_a_sudo_shaped_run_in_a_clone_is_refused` (the 3 passing either way are the anti-vacuity / default-off controls, which must).
- **`bench/tests/test_scanner_specimen_contract_2026-09-11.py`** — green: `6 passed in 0.16s`. **Red with two instances re-planted:** `2 failed, 4 passed in 0.17s` — `FAILED ...[flake._failed_the_test]`, `FAILED ...[roll-call line selector]`.
- **Strengthened `test_the_vouching_rule_is_asymmetric`** (5th case added): symmetric mutant now dies — `1 failed in 0.19s`; real module: `14 passed in 16.47s`.
- **Differential census:** `402 notes; count differs on 0` — the lint patch changes blocking counts on no existing note.

## `fix`

All in my sandbox tree at real paths:

- `scripts/sync_desktop_mirrors.py` — drill exemption now requires `DESKTOP` displaced **to scratch** (closes the sudo/uid bypass); temp rule checks a resolved *set* of scratch roots (`gettempdir()`, `/tmp`, `/var/tmp`, `/var/folders`, `/dev/shm` — closes the TMPDIR-stripped escape); opt-in `.cdsfl_canonical_checkout` marker on the real Desktop refuses any other checkout by name (closes the non-scratch-clone class; **default-off** — no marker, no behaviour change; refusals stay exit-0 so no commit is ever blocked); `--register-canonical` flag wired into `main` and executed by test, and a scratch clone cannot register itself.
- `scripts/note_vagueness_lint.py` — future-stamp finding inserted into `counted` *after* the exempt split (region-immune, matching the unbalanced finding); new `_marker_events()` walks markers in positional order and both consumers (exemption + balance counter) share it — one implementation, two callers, their own stated idiom.
- `scripts/scripts_are_reached_2026-09-11.py` — `_ROLL_CALL` accepts markdown-bullet roll-call lines (`- scripts/x.py`), the same one-form defect pointing the other way (false non-zero reach hiding an orphan).
- `bench/tests/test_scripts_are_reached_2026-09-11.py` — 5th `vouches` case, with the executed mutant history in the comment.
- `bench/tests/test_panel_round15_fixes_2026-09-11.py`, `bench/tests/test_scanner_specimen_contract_2026-09-11.py` — new, described above.

## `figures`

| figure | value | Wilson 95% | second tool, agreement |
|---|---|---|---|
| reachability | 115/121 = 95.0413% | [89.6029%, 97.7078%] | mpmath 50-dps closed form, ≤1.11e-16 |
| I38 flake | 2/6 = 33.3333% | [9.6771%, 70.0007%] | mpmath, ≤5.55e-17 (also CP [4.3272%, 77.7222%]) |
| Rule 28 bounded-drop (today) | 1/29 = 3.4483% | [0.6113%, 17.1755%] | mpmath, ≤5.55e-17 |
| lint-patch behaviour drift | 0/402 notes | — | differential census, exact |

**The two-cases distinction, explicitly:** the I38 interval spans 9.7%–70% — a factor of 7 covering both "rare flake" and "fails half the time"; **6 observations is a description of 6 runs, not a rate**, and the Fisher p=1.0000 clone split settles nothing. Act on it only by collecting more rows. The reachability interval (~8 points wide, floor 89.6%) is tight enough to act on. Treating these with equal confidence would itself be a defect.

**Severity** (reference: the Desktop overwrite — founder's file destroyed, recovered by luck): sudo-bypass **high** (defeats both rules at once, but requires an unusual invocation); TMPDIR escape **medium-high** (plausible in cron/launchd/sudo environments); non-scratch clone **medium-high** (replays the incident exactly; needs a second checkout, which the founder demonstrably makes); seat-swallowing paragraph **medium** (blocks a founder record — the *worse* direction — but loudly, at commit); exempt future-stamp **medium-low** (silent amnesty, narrow trigger); vouches mutant survival **medium** (a calibration instrument asserting an untested property); roll-call bullet **low** today (no bulleted line exists yet); stale Rule 28 figure **low**.

## `strongest_disagreement`

The brief says FIX 1's passwd keying separates "a drill from an escape" because "a drill cannot move it." **The keying is backwards under privilege change**: it doesn't identify the *founder's* Desktop, it identifies the *current uid's* Desktop, and the mismatch is treated as proof of a drill when it is equally proof of `sudo`. Failing case, executed: `refuse_reason()` → `None` with the pytest flag set AND the repo under the temp root — both rules dead. I also disagree with the brief's implicit framing that the 5 fixes constitute closure of the *class*: 15 instances of one defect class closed one-at-a-time is the pattern the founder is objecting to; the specimen contract is the class-level answer, and only it turned red on re-planted instances. Finally, against CC1's likely reading of `test_the_vouching_rule_is_asymmetric` as discharging the mutation debt: it did not — I ran the mutant and all 14 stayed green.

## `refutation_condition`

- Show a **legitimate existing drill** that displaces `DESKTOP` to a non-scratch path — my tightening would refuse it, flipping my sudo fix into the worse (founder-starving) failure. Command: `grep -rn "setattr(sync, \"DESKTOP\"" bench/tests/` and exhibit one not under `tmp_path` (I found none).
- Show `refuse_reason()` returning non-None in the founder's real checkout with no marker present — would refute my "no new blocking by default" claim. Command: `python3 -c 'import ...; print(refuse_reason())'` in his checkout.
- Show any of the 402 notes where pristine vs fixed `blocking()` counts differ — refutes my zero-regression claim (my census script is in the transcript; re-run it).
- Show pytest emitting a `FAILED` line-form my specimen registry doesn't cover (e.g. a wrapped/truncated id) that `_failed_the_test` misses — would show the contract is itself under-specified, the recursive instance of the class.
- A 7th full-size suite run moving I38 outside [9.6771%, 70.0007%] refutes nothing — that is the point of quoting the interval.

**Passes:** 3 substantive (reproduce + probe; fix + red/green; regression attribution + differential census). A 4th pass produced no new above-threshold finding — that is the stop signal, per §8. Residual falsification debt: FIX 1's behaviour under a genuinely absent passwd entry (containers) was derived (falls back to `Path.home()`, rules apply — safe direction) but not executed, and the two regression reds in `test_desktop_mirrors_stay_current` were attributed to sandbox artifacts (pristine-module red; unborn-HEAD ratchet baselines) rather than eliminated — both marked [VERIFY:current] for a run in a real checkout.

<!-- verbatim-end -->

## Where the raw record lives

`bench/logs/panel_round15_2026-09-11/` holds the brief, every seat reply, the tool logs and `seat_proposals.diff`. That directory is excluded by `.gitignore:41`, so a byte-identical copy is committed under `experimental_notes/evidence/`, verified by sha256 and checked on every suite run by `bench/tests/test_panel_records_are_preserved_2026-09-11.py`.


Written under CDSFL note standard v1.7 (26 August 2026).
