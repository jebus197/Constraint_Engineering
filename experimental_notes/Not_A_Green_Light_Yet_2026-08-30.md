# Not A Green Light Yet: The Review Broke The Guard I Had Just Built

2026-08-30, 22:09 BST (UTC+1)

A complete inventory of every action agreed on 30 August was rebuilt from the record rather than from memory: 37 items, drawn from 6 self-proposed repairs and 4 model reviews. Nine were still outstanding and were closed. The test suite then reported 4549 passed, 0 failed and 0 skipped, against 4434 passed with 34 skipped and 2 failed at the start of the day.

A third review was then run against that state, and it returned a verdict of "not a green light". It was right on 9 of its 10 counts. The most serious was that the network guard built earlier the same day could be walked around three different ways, and that a repair made earlier the same day was a net regression. Those are now closed. One item remains open and needs a decision that is not the assistant's to make.

The reason a fresh inventory was needed is worth stating plainly. The first review ended with a ranked list of 9 actions. Four of them, ranked 4th, 5th, 7th and 8th, were not carried out, and a later summary nonetheless described the work as substantially complete.


## The Network Guard Was Breached Three Ways

The instruction was that the internet is always available here, and that testing the literature-retrieval component costs nothing beyond an existing subscription. Three tests had been switched off for 49 days by a guard that could not tell a paid model dispatch from a free lookup of a scientific paper.

The first repair permitted a fixed list of free hosts. That was the wrong shape, and measuring it showed why: retrieval follows a document identifier to whichever publisher hosts the paper, and the very first run reached a publisher no such list would have contained. It was inverted to a list of paid endpoints that stay blocked.

Both reviewers then broke that too, independently. One of them wrote three adversarial tests and, run as written, all three succeeded. A command-line fetch tool reached a paid endpoint and got a normal HTTP 200 response from inside the permitted window, because it was not on the list of metered programs. A separate program was used to look up the paid endpoint's numeric address, and a direct connection to that address succeeded, because the block list holds names and a number matches none of them. And five commercial providers nobody had listed were all permitted, which is the deeper problem: a list of paid providers cannot be completed, because new ones appear without notice.

The guard is now bounded by capability rather than by enumeration. Inside the permitted window, only one network-capable program may be launched, and it is the one covered by the existing subscription. A numeric address is permitted only if this guard itself resolved it during this window, so an address obtained by other means is refused. And billable credentials are removed from the environment for the duration of the window and restored afterwards, so reaching an unlisted provider produces an authentication failure and bills nothing. That last measure closes the third breach without needing to know who the providers are, and it was verified against a credential for a vendor that appears on no list.

The sharpest criticism was about method rather than code. The 8 tests written to prove the guard was safe all called the same internal decision function and never exercised the enforcement path at all. They asserted the policy; both breaches were in the enforcement. Five tests that drive the actual enforcement have been added.


## A Repair That Made Things Worse

Earlier the same day a defect was fixed in the code that recovers a proof-program from a model's reply. The closing marker had been allowed to match anywhere, including inside quoted text, so a proof-program that quotes a code listing was cut off at its own first inner marker.

Requiring the closing marker to sit alone on its line fixed that case and broke every other case. With a malformed closing marker, the search ran past it, past the next block's opening marker, and paired with the wrong closer. One trailing word after one closing marker destroyed every block in the reply, well-formed ones included. Measured directly: the old pattern found 2 blocks, the new pattern found 0. It failed closed and silently into the routing ladder, whose failure mode is a false report of an exhausted ladder, which is the exact defect the function exists to prevent.

A second attempt, scanning block by block with a permissive fallback, recovered the malformed closers and broke the original case again. The two requirements only conflict within a block, not across a reply. So the strict reading of the whole reply is taken first, and the permissive reading is used only when the strict one yields nothing runnable at all. 11 tests now pin 7 reply shapes and both original fixtures.


## A Regression Introduced And Caught The Same Day

Enabling the three literature tests by default made the whole suite dependent on the internet. Two of the three fail outright with no connection, so on a plane, in a build environment with no outbound access, or during an outage at the paper archive, the suite would go red and read as a code defect. The test configuration's founding property, that it simulates a machine with no network and stays green, had been destroyed.

They now run when the connection is available and skip, with a stated reason, when it is not. That satisfies both the instruction and the property.


## Five Smaller Items, All Closed

The runner printed a warning saying a configuration flag was not connected, 23 lines before connecting it. Deleted.

That flag's effect rides on a separate switch, so setting it while the other switch is off produces no effect at all. That combination is now announced rather than silent.

Nothing tested the connection, so the line that makes it work could have been deleted with the suite staying green. That is precisely how the flag survived disconnected from 21 August. 7 tests now hold it.

The test guard and the simulated-run tripwire each held their own hand-maintained list of paid endpoints. They had already drifted apart, 8 entries against 5, and both omitted two endpoints this repository actually dispatches to. There is now one canonical list of 13. The first attempt to share it fell back silently to a 5-entry copy, so the running guard held 5 while the canonical list held 13; that silent fallback has been removed.


## The One Open Item

The third review measured the board as 2 failed rather than 0 failed, and concluded the green result had never been measured on a clean checkout. That was reproduced and diagnosed: there are 311 hardcoded absolute paths inside 51 archived result files. At the canonical location the exploit guard passes, verified at 35 passed. At any other location those archived proof-programs appear to read outside their declared target, producing 17 rejections against 2 expected, a rate of 3.62 percent with a 95 percent confidence interval of [2.28, 5.73].

So the board is green where the work is done, and it is not portable. Making it portable means rewriting 311 paths inside the archive, and this project's own standing rule forbids reaching backwards into the record. That decision is not the assistant's to make and it is the reason this is not yet being called a green light.

One further item is environmental rather than technical. The second reviewer's third-pass session terminated on a command-line trust error inside its disposable copy and never produced a report. Its adversarial tests survived only because reviewer files are now extracted before the copy is destroyed, which was itself a directive issued this morning. Clearing that error requires accepting a trust prompt once, interactively, which the assistant cannot do.


Written under CDSFL note standard v1.7 (26 August 2026).