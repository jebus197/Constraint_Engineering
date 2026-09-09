# Target-mutation watch evidence, 2026-09-08

**Moved here 2026-09-09 because the original location was untracked and the evidence was therefore not preserved at all.**

Commit `3c4987d` on 2026-09-08 claimed to have preserved this evidence out of the session temporary directory. It did not. It copied the files into `bench/logs/`, which `.gitignore:41` excludes with `bench/logs/**`, so **0 of the 22 snapshots were ever tracked** and they existed on exactly 1 machine — the single point of failure the commit set out to remove. Found on the 5th FFAFP pass of 2026-09-09, by cloning the repository and watching the citation guard fail in the clone while passing locally.

**Why the snapshots carry a `.py.txt` extension.** They are Python source a panel seat wrote during a run. Stored as `.py` under a tracked directory they would be parsed by the repository's source scanners — the same scanners repaired on 2026-09-08 after archived model output was read as production code. The `.txt` suffix keeps them readable and diffable while keeping model output out of every Python scan.

## What this evidence is

`target_state_transitions.log` records 12 distinct blob hashes for `bench/dm/_memory.py` between 07:15:03 and 09:31:15 on 2026-09-08, written by a 15-second poll loop. The snapshots are the file's contents at each of those states.

The measurement built on it is `scripts/target_mutation_arrival_2026-09-08.py`, with guards in `bench/tests/test_target_mutation_arrival_2026-09-08.py`. The rewrites were not spread across the run: 7 of the 12 states fall inside the first 600 s of an 8172 s window, KS D=0.5465 p=0.002496, gap coefficient of variation 1.8643 against a uniform-null mean of 0.9307 with Monte Carlo p=0.00141.

`snapshots/SEAT_064003_03845310.py.txt` is the substantive one: at line 360 a seat added a guard to `update_drift` carrying its own reason, and converted the detector to a two-sided CUSUM. It is a review finding applied in place rather than proposed, which is the defect; whether the fix is correct is OPEN.

Written under CDSFL note standard v1.7 (26 August 2026).
