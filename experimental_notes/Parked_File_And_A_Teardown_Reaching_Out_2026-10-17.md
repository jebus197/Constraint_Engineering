# Task B3 is built, and finding it uncovered a test teardown that was changing file permissions outside its sandbox

2026-10-17 13:51 BST.

## What B3 was

The file `experimental_notes/PARKED_FOR_THE_FOUNDER.md` holds items classified as not blocking, queued for the founder to settle at the end of the task list rather than interrupting him. Nothing removed an item from it when the underlying task entry closed. So settled business accumulated in front of the live items. Measured on 2026-10-13 by `scripts/has_he_already_ruled_on_the_parked_2026-10-13.py`: 14 of 21 items were already settled, 66.6667%, with a 95% Wilson interval from 45.3735% to 82.8052%. The founder's ruling on reading that was, build it and implement it.

## What was built

A new producer, `scripts/regenerate_the_parked_file_2026-10-17.py`, derives the live portion from the master task list's own markers at generation time and moves every settled item to a section at the foot of the file carrying the reason it was settled. Nothing is deleted, because staleness is visible and deletion is not. Applied: 7 items still need him, 14 are settled, all 21 preserved with their text intact.

## Four defects in the generator, found before it ever touched the file

First, it carried its own copy of the rule for what counts as settled, and that copy disagreed with the measurement on 5 of 21 items, in both directions. It read identifiers from an item's body as well as its heading, it did not split a compound identifier such as `A13/A14` into its 2 halves, it required every entry an item named to be settled rather than any one of them, and it had no route for an item refuted by execution. Two of those 5 disagreements would have moved a LIVE item into the settled section, which is the burial the task exists to fix, performed by the cure. The repair was to expose the measurement's own classification as a function and call it, so 2 spellings of the rule cannot drift apart.

Second, it paraphrased the founder inside double quotation marks. It wrote, rather than bother me with them now, where he wrote, unless there is something that clearly warrants my immediate attention. Under his quotation convention, double quotes mean verbatim. The quotation is now a constant lifted from the file rather than retyped prose.

Third, its check that nothing had been lost compared only the NUMBER of headings before and after. A second producer, `scripts/would_the_count_only_postcondition_have_caught_it_2026-10-17.py`, reverts that check and applies a mutation that truncates each item's text. The old check returns exit code 0 and prints the words, all preserved, while losing the text of 7 of 21 items, 10,929 of 32,817 characters, 33.3029%. The 7 are exactly the live items, the ones still needing him. The replacement refuses with exit code 2 and names all 7.

Fourth, and the one that would have shipped silently: the generator was not idempotent. The parser gives the last live item a body that absorbs everything up to the next heading, which includes the separator and the settled section's own title. So the second run re-emitted both, producing 28 reason lines for 14 items and 2 copies of the settled heading, and every further run would have added another. The first run looked perfect. Committing after a single run would have shipped a file that grew on every regeneration.

## One consequence traced rather than discovered by failure

The script `scripts/blocker_triage.py` appends newly parked items to the end of the file. Since the end of the file is now the archive, a plain append would have buried each new item on arrival. It now inserts ahead of the settled section.

## The wider finding, which has nothing to do with the parked file

The new guard suite builds a sandbox by symlinking the repository's scripts directory into pytest's temporary directory. Running it stripped the execute bit from 22 tracked scripts in the real repository. The cause is a teardown in `bench/tests/conftest.py`, written on 2026-09-08 for a sound reason: tests that reduce directory permissions on purpose left pytest unable to delete its own temporary trees, and 11 megabytes of undeletable directories had accumulated behind a wall of warnings. It walked the temporary directory setting every file to 600 and every directory to 700. The Python call it used follows a symbolic link, so for any test that symlinked a real path into the sandbox, the permission change landed on the real target.

The reach is not limited to the repository. The test file `test_desktop_mirrors_stay_current_2026-09-10.py` symlinks every entry of the home directory into the sandbox, and `test_canary_seeding_2026-08-28.py` symlinks the repository root. Both have been running for weeks. The evidence is the pair of literal values: the umask on this machine is 022, so any file a tool creates here is 644 and any directory 755, yet the files .zshrc, .gitconfig and AGENTS.md in the home directory all stand at exactly 600, 389 tracked files stood at exactly 600, and the repository root stands at exactly 700. The binary `/usr/bin/git` is still 755 only because macOS System Integrity Protection refused the change and the resulting error was swallowed.

The fix is to skip symbolic links, and it loses nothing: the deletion routine unlinks a symbolic link without reading its target, so the target's permissions were never needed to delete the tree, and deleting the tree is the teardown's entire purpose. The repository has been restored to the permissions the git index implies: 389 files from 600 to 644, and 22 executables to 755. A producer, `scripts/how_far_did_the_cleanup_fixture_reach_2026-10-17.py`, now reports 0 of 8,138 tracked files disagreeing with the index, Wilson interval 0.0000% to 0.0472%, cross verified between statsmodels and scipy with mpmath.

Files in the founder's home directory were deliberately NOT changed. A permission of 600 is more restrictive than the default rather than less, so nothing is exposed, and altering permissions in his home directory is his decision rather than an assistant's. The same applies to the repository root at 700.

## What holds it

Two new guard files carry 14 tests and are both in the commit time set, which now stands at 1,001 tests across 35 files. Every assertion executes the code rather than reading its text. Three separate mutations were applied to confirm the tests can fail: truncating each body makes the preservation check refuse, bypassing the strip makes the idempotence check refuse, and removing the symbolic link skip makes 3 of the 4 permission tests refuse. The new suite also carries a ratchet comparing every tracked file's on disk execute bit against the git index, so the same drift cannot return unnoticed.

## What remains

The task list stands at 151 entries with 22 open, and 17 of those wait on the founder. The next unblocked item is A19.

Written under CDSFL note standard v1.8.
