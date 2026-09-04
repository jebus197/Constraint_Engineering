# Morning Round-Up — 2026-09-04 05:02 BST

## THE HEADLINE

The gate that decides whether a proposed fix is accepted has never once rejected anything. Not a low rate. Zero, across 3,816 checks.

This was measured 2 independent ways that agree exactly. The first reads the structured records: a genuine threshold rejection is the only path that writes a field called passes_threshold, because a fix rejected for any other reason arrives at that branch already marked rejected and never reaches the check. That field reads false 0 times and true 3,816 times. The second reads the run logs for the single line that only the threshold branch can emit, and finds it 0 times, against 400 occurrences of the error-path line. Fire rate 0 of 3,816, with a confidence interval from 0.0000 to 0.0010.

So the defect found on 3 September is not theoretical and not partial. The threshold formula was derived with one variable frozen at the value 1, and that variable is the very quantity the gate tests. At the only operating point the pipeline can reach it evaluates to minus one nineteenth, clamps to zero, and admits everything. Confirmed by symbolic algebra, by high precision arithmetic at 50 digits, by a local Wolfram kernel in exact fractions, and by solving the underlying equation directly without using the disputed formula at all.

## A SECOND DEFECT, FOUND BY THE PANEL, IN SOMETHING I HAD TOLD YOU WAS BUILT

I reported that half of the May pre-registration, the part reporting how sensitive a verdict is to the rubric disagreement, had been built. It had not. It was a constant.

The threshold profile wrote its keys using a format that rounds to 1 decimal place. That maps 0.65 onto 0.7 and 0.75 onto 0.8, so both edges of the disputed band were silently overwritten by their neighbours: 6 thresholds collapsed into 4 keys. The consumer then looked up the literal 0.65 and 0.75, found neither, and reported both edges as absent and the verdict as not robust. Unconditionally, for every run that could ever exist. One reviewer ran the real function over all 41 archived reports and found 41 of 41 vacuous.

It shipped because the test guarding it asserted on the text of the source file and never called the function. A test that reads source text can only confirm that the code describes itself consistently. It cannot catch a producer and a consumer that disagree about what a key looks like, because each description is individually correct.

The fix is a single token in 2 places. It is applied, and the replacement test executes the function against 2 constructed registries and asserts that the verdict can take both values. Reverting the fix fails 4 of the 5 new assertions while the old source-text file still passes all 8 of its own. That contrast is the entire argument of this week's work, demonstrated on the project's own instrument.

## WHAT WAS BUILT

The overlap record, which you approved as decision 7 and which everything else waits on. When 2 models find one defect the runner used to mint 2 unlinked entries and merge the second away, destroying the co-discovery signal at the moment it was created. Only 2 of 2,050 archived findings were recorded as raised by more than one model, which is why a saturation curve built from that field came out linear by construction and had to be withdrawn.

Two additive changes now record it. Registration seeds a list of occasions naming the model, the round and the report identifier. Merging carries the duplicate's occasions onto the surviving entry, deduplicated so that re-merging the same report cannot inflate the count. That deduplication is not tidiness: inflating a singleton is the classic failure of mark and recapture estimation and biases every coverage figure upward.

Nothing reads the new field yet, which is what makes this a recording change rather than a behavioural one. It cannot move a verdict. The field it sits beside has 12 live consumers and none of them changed.

Both halves were tested by reverting them separately. Removing everything fails 8 of the 9 new assertions. Removing only the merge half fails exactly the 4 that concern co-discovery. Restoring passes all 9.

## TWO RULES WRITTEN WHERE THEY WILL BE READ

Your ban on word-form numbers is now in both instruction files. The uncomfortable part is that the rule already existed as rule 27 of the note standard, and the linter already caught it. Running that linter over 5 notes written on 2 and 3 September returns 23 findings. The failure was never a missing rule or a missing checker. It was never running the checker, so the rule now says to run it and to treat a spelled number as blocking.

Your approved rule that a measured rate must travel with the script that produced it is also written in. Alongside it, a rule that a test must execute rather than grep, because 4 defects in this project have now been found by running two forms against each other and none was found by reading.

## A SWEEP, PARTLY DONE

Of 218 test files, 18 contain assertions on the source text of a Python module, 8.26 percent, with a confidence interval from 5.29 to 12.67 percent, and 26 such assertions in total. An honest caveat: not all 26 are defects. Checking that a line citation resolves is legitimately a text check. Separating the genuine cases needs judgement on each one rather than a pattern match, and that triage is the next item rather than something done overnight.

## WHERE I STOPPED, AND WHY

Phases 0 through 2 are complete and committed, along with the measurement half of phase 3. I stopped before phase 4, which is wiring the fix-complexity module and then repairing the threshold.

The reason is not tiredness, though it is now half past 6. Phase 4 is the one change in the queue that alters which fixes are accepted, which alters the prompts models see in the next round, which by that module's own documentation invalidates the ability to replay archived runs. It is the least forgiving change on the list. It also now has a much stronger case than it had last night, because the gate has been measured at exactly zero rejections, so repairing it will change behaviour rather than merely tidying it. That is a change worth making in daylight, with the panel reviewing it, rather than at the end of a long night.

Three items also remain that need you rather than me: whether the additional panel should be briefed on new mathematics as well as the execution gate, who signs a rubric adjudication, and how the past data should be recorded. Both reviewers converged independently on models drafting and you ratifying, which fits the existing principle without amending anything frozen.

The 4 errors visible in the test suite are unrelated to any of this and were proven so by stashing the changes and reproducing them exactly. They are tests of the outbound-call guard that deliberately attempt a call and lack the marker that permits it.


---

## References restored for the markdown copy

| Claim | Where |
|---|---|
| Valley gate fire rate 0 of 3,816, CI [0.0000, 0.0010] | commit `33ef614`; `passes_threshold` in archived reports |
| S\* = −1/19 at the live operating point | `bench/reference_runner_v3.py` `check_sk_threshold` |
| true break-even 0.504931170970423 | SymPy, mpmath 50 dp, wolframscript exact, direct solve |
| key collision, 6 thresholds into 4 keys | `gamma_threshold_profile`, fixed in `8d0a7ee` |
| 41 of 41 archived reports vacuous | fable, panel `panel_placement_20260904T030259Z` |
| occasions record, both halves P-passed | `bench/tests/test_occasions_record_co_discovery_2026-09-04.py` |
| 18 of 218 test files, 8.26%, CI [5.29%, 12.67%] | commit `bc30e02` |
| 23 lint findings across 5 notes | `scripts/note_vagueness_lint.py` |
| suite 4,868 passed, 4 pre-existing errors | `--netguard-strict`, 533.51 s |

Commits: `8d0a7ee`, `8bc32a9`, `33ef614`, `bc30e02`.
