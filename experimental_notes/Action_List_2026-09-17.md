# Action list: finishing the work agreed on 2026-09-16 and 2026-09-17

2026-09-17, 16:21 BST, Europe/London. Worked in order, and ticked only when the done-test beside each item has been run and passed.

## Why this list exists

The founder asked, at 15:18, whether all the work agreed in the previous 24 hours was complete. It was not. A read-only audit by 11 agents, run between 15:35 and 16:18, established what remains, and the founder then asked for a sequential list that can be checked off, with the founder's own outstanding verdicts and the Zenodo key rotation placed last if that is safe. It is safe: every item that waits on a verdict has a conservative default in force until the founder rules, and no earlier item depends on a verdict.

The source of every item is 1 of: the founder's answers after the hash marks in `~/Developer_Projects/Responses/Outstanding_Rulings_2026-09-15.rtf`; the founder's chat rulings of 01:00 on 2026-09-17 on I16, I18, A8, Question 10 and Question 7; the instruction "Implement all outstanding actions as agreed"; and the suggested-task card from the Question 9 agent, which the founder asked to be added.

## The list

1. [x] **Secrets out of every seat's environment.** Source: the card. Importing the panel dispatcher loads 10 secrets into its own environment, 8 API keys plus `GITHUB_TOKEN` and `ZENODO_TOKEN`, and every seat inherits them, so a seat's shell could make a paid call, push to GitHub or publish to Zenodo. Done when a seat's child environment carries none of them, shown by a test that captures the environment a seat is started with, and a free probe shows the seat's shell cannot see a marker variable the dispatcher holds. Must precede item 2.

    DONE 2026-09-17 16:33 BST, status COMMITTED and ENABLED, because every live seat launcher calls it by default. `seat_environment()` in `bench/experiment_11_orchestrator.py` removes every variable whose name looks like a credential, and 7 launchers now pass it: `call_claude_cli`, `call_codex`, the simulated-run shim, the simulated panel agents, and 3 in `bench/decomposed_dispatch.py`, which the experiment runner imports and which the card did not name. Codex keeps `OPENAI_API_KEY` and nothing else. Evidence: `bench/tests/test_seat_environment_carries_no_secrets_2026-09-17.py`, 14 passed, driving each launcher and capturing the environment it passes; removing the fix at each of the 5 sites checked this way failed its own test, and a ratchet fails if any new subprocess call in those 5 modules omits `env=`. `scripts/seat_environment_probe_2026-09-17.py --live`, 2 free Max-plan calls: BEFORE `KEY_PRESENT PLAIN_PRESENT`, AFTER `KEY_ABSENT PLAIN_PRESENT`. The 14 test files that exercise these launchers: 126 passed under `--netguard-strict`. The repository's `.env` holds 10 names and none is `ANTHROPIC_API_KEY`, so no earlier Claude seat was switched to paid billing by this route.

2. [ ] **Question 9: dispatch the engineering entries to the panel.** Source: "This is fully approved". Scope 34 entries: the 59 supplementary entries, less the 7 held entry ids, less the 16 that panel round 16 has just reviewed, less R10 and R11, which bear directly on the mathematical model and are held with A19 pending the founder's verdict in item 12. Free seats only. Done when the brief passes its validator, 0 paid seats is confirmed before launch, and both seats have returned.

3. [ ] **A8: correct the marker and repair the evidence classifier.** Source: the founder's acceptance of the A8 recommendation. The marker still reads OPEN/PROPOSED because the closing commit never edited the task list, and 286 of the manifest's 335 "missing" paths are directories, truncated prefixes or templates rather than lost files. Done when the marker reads OPEN/COMMITTED with its evidence named and a dated paragraph records both commits, the classifier distinguishes a missing file from an existing directory under a test with a directory control, and the manifest is regenerated at a named commit.

4. [ ] **Question 11: wire the Wolfram standard where it can be wired without a verdict.** Source: "Ensure this is wired in all cases appropriately". The standard exists only as prose. Done when 1 shared helper classifies a failed call as not evidence and attributes a successful 1; the test suite and the falsifier sandbox refuse to start the licensed kernel; automated and simulated runs deny it, as the licence constraint already requires; panel seats receive the standard in their system prompt with Wolfram denied by default until item 12; onboarding retries, checks for a stale kernel and warns before the 2026-10-08 licence expiry; and each change is held by an executing test. Added 2026-09-17 while closing item 1: the 2 falsifier sandboxes, `_apply_back_gate` and `_run_effect_regression` in `bench/reference_runner_v3.py`, run model-proposed source with the full environment, secrets included. Stripping them there changes the environment the gate's tests run in, so it is measured first, by running the same test command with and without the secrets and comparing the passed and failed counts, and applied only if those counts agree.

5. [ ] **W1: the Wolfram setup instructions.** Source: the founder's request to "print a set of instructions for me to follow to set this up fully for you", with the steps the assistant can take separated out. Done when the instructions are on the founder's Desktop as spoken text and in the repository as a note, lint-clean, with every claim either checked or marked unverified.

6. [ ] **Question 7: apply panel round 16's closures to the 31 entries.** Source: "Question 7, the 30: approved. Do the work." Each closure was re-executed independently: 8 hold, 21 hold in part, 1 is refuted and 1 overclaim is not real. Done when every entry carries a dated correction resting on execution, every figure it keeps has a committed producer, and each test the corrections name exists and passes.

7. [ ] **I31: record that the drift-detector wiring rested on a false premise.** Source: the founder's conditional ruling, "if it depends on some element of how our current mathematical model functions, defer it". The commit that wired it said the detector's input appears nowhere in the mathematical appendix; it does, written with the Greek letter. Done when the finding is verified by execution and recorded on the entry. Whether to keep the report-only call or revert it is the founder's to decide, in item 12; the call decides nothing meanwhile.

8. [ ] **The programme of study: the addendum the founder's rulings require.** Source: I23, I31, Question 6, A7, R3, A19 and Question 11. Done when a dated addendum records what the current programme misses, including that the simulated launcher cannot run the 3 pre-registered arms and that the seat list names real vendors for stand-in seats; every figure in it has a committed producer; and the Desktop copy carries the same addendum.

9. [ ] **Question 9 results: take them in without voting.** Done when the round's records are mirrored and its full record note is written, and each seat proposal is re-executed before anything is adopted.

10. [ ] **Close out.** Done when the full suite passes under `--netguard-strict` with the exit code captured, the recovery documents and tracker are current, everything is committed, and this list is reprinted as done or not done.

## Placed last: the founder's own items

11. [ ] **I18: drop both stashes, in person**, because deleting a git ref is the founder's to do: `git stash drop 'stash@{1}' && git stash drop 'stash@{0}'`

12. [ ] **Verdicts still owed.** (a) Hold R10 and R11 with A19, or send them to the panel. (b) I31: keep the report-only call or revert it. (c) Arm C of the next simulated run is marked launch-blocked pending the founder's ruling. (d) Wolfram in panel reviews: denied, which is the default now in force, or allowed through a single-kernel queue. (e) Whether a workflow-spawned agent calling Wolfram is the assistant's own interactive use or automated use. (f) Whether the Wolfram connector is named in the project instructions as a working route, which also means editing wording in a file that is the founder's. (g) A8: whether any backup, such as Time Machine or another machine, holds the evidence files that no git ref contains. (h) The experiment 56 arm-declaration exposure, held as an expected failure, whose fix edits a frozen pre-registration.

13. [ ] **Task 10.2: Tailscale's own SSH service**, still the founder's call.

14. [ ] **Push** the commits this list produces, or run `sv`.

15. [ ] **Z1: rotate the Zenodo token**, last, as the founder asked. Credentials are the founder's to handle, and the assistant never enters them.

Written under CDSFL note standard v1.7 (26 August 2026).
