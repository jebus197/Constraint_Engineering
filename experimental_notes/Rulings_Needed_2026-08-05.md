# Thirteen decisions that need you, with enough of the reasoning to decide on

2026-08-05 15:24 BST, revised 19:40 BST after the repairs landed


## Disposition — all thirteen ruled, 2026-08-06

The founder ruled on every item on 2026-08-06. This section is the authoritative status;
the reasoning for each question is preserved below, unchanged, as the record of what was
asked and why.

| # | Question | Founder's ruling | Status |
|---|---|---|---|
| 1 | Open Brain backfill | Classify ALL 106 with agents — *"There is no later"*. Normalise the `CDSFL`/`cdsfl` case split | **IN PROGRESS** |
| 2 | Who owns the canonical recovery ordering | NOT a straight ruling. Audit the whole estate and propose keep / retire / reorganise, against **industry standards, not invented ones** | **PROPOSAL PENDING** |
| 3 | Tracker canonicality | *"Invert it"* — the repo copy is canonical, the Desktop copy is the mirror | **DONE** |
| 4 | Should `sv` block or warn | *"Refuse and print an alert if the task is not fully completed"* — and the alert must show why, so the cause can be fixed | **DONE** |
| 5 | The retired IM service | *"Delete"* (overriding the recommended delete-seven-banner-one) | **DONE** |
| 6 | Desktop-only documents | Question answered: 227 total, of which 189 predate the note standard and are not defects, and 38 postdate it. Keep/dispense folded into the ruling-2 audit | **ANSWERED, folded into 2** |
| 7 | Memory index headroom | *"I will run with your recommendation"* — trim the six longest AND add the size check | **DONE** |
| 8 | Which section owns ONBOARDING's state block | *"Take the search route"* | **DONE** |
| 9 | `f` — three-step or five-step | *"IT IS FFAFP. That should have been clear for some time… Update the config to match"* | **DONE** |
| 10 | `sq` — standing or invoked | Invoked, as needed. The overload it guarded against is upstream capacity and largely not ours to control | **DONE** |
| 11 | Test coverage for the operational scripts | *"Do it. Don't delay. Delay for what end? To ship with broken code, that we might then never get around to fixing?"* | **DONE** — 162 tests |
| 12 | The file-drop bridge | **REVERSED the retire recommendation**: *"CW may come back into the picture during UX design… you should probably fix it"* | **CODE FIXED; RELOAD is the founder's action** |
| 13 | Seven unverifiable records | Leave them, label honestly as predating hashing with any later gap a mechanical confound. Also: find out why hashing was not automatic | **DONE** — and hashing IS automatic again, proven by a same-day before/after |

**Two things still need the founder, and only these two.** A spot-check of the record
classification once it lands, and the launchd reload command for the bridge, which is a
running service on their machine.

**One correction of record.** An earlier statement that the Exp 43 "FIX 1–5 design" is live
unimplemented work was WRONG. That tranche was designed 2026-07-19, coded 2026-07-27 in commit
`1cec60d`, and shaken out by Exp 44, which converged at round 12 with zero residue.

---

## How to use this document

Everything that could be repaired without asking is being repaired separately. What follows is only the residue: places where the right answer depends on what you want, not on what is true.

Each item gives the situation, why there is a choice at all, what each option costs, and a recommendation. The recommendation is a real opinion, not a formality. Where the recommendation is weak, that is said.

Three of these matter. Nine are small and can be answered in a word each. The three are numbered first.


## The Three That Matter


### Ruling one. The Open Brain backfill.

**The situation.** The memory store holds one hundred and fourteen records. Each is supposed to carry a label saying which project it belongs to, so that a query can ask for only this project's material. One hundred and six of them have no label, because for the past two months every write went through an older copy of the code that does not write one. That copy is now out of the path, so new records will be labelled correctly from here on. The existing hundred and six will not.

**Why this is a choice and not just a repair.** Adding the labels means writing to records that already exist, and it means deciding what each one is. Most are obvious from their content, but not all, and a wrong label is worse than no label, because a wrong label makes a record show up in a query where it does not belong and vanish from the one where it does. I can pattern match on content and on which agent wrote it, but I cannot be certain, and I would rather not guess a hundred and six times unsupervised.

**One extra wrinkle, found during the repairs.** Of the eight records that do carry a label, seven say CDSFL in capitals and one says cdsfl in lower case. The filter is a plain equality test, so those are currently two different projects. Asking for CDSFL misses the lower case one; asking for cdsfl misses the other seven. Whether to normalise case is part of this same ruling, and the answer is almost certainly yes.

**The options.** First, I classify all one hundred and six by content and you spot check a sample. Second, I classify only the clearly unambiguous ones and leave the rest labelled as unclassified, which is honest and leaves a smaller pile for later. Third, leave them all unlabelled and never use the project filter, relying on reading the whole store.

**The cost of doing nothing.** The project filter is currently a trap rather than a feature. Run it today and it returns a session summary from the third of June presented as the current state, because everything newer is invisible to it. Unfiltered, the store gives a cluttered but honest answer. So doing nothing is survivable, as long as nobody ever uses the filter, which is exactly the kind of standing exception that gets forgotten.

**Recommendation.** The second option. Classify the unambiguous ones, leave the rest explicitly marked unclassified, and let the pile shrink naturally as you or I recognise entries. It is reversible, it needs no guessing, and it makes the filter safe immediately because an unclassified record is visibly unclassified rather than silently missing.


### Ruling two. Which document owns the recovery procedure.

**The situation.** There are currently four places that tell an agent how to recover after its memory is wiped, and they give four different procedures. They are not versions of each other and they are not supersets of each other. Which recovery you get depends entirely on which file you happen to open first. One of them never mentions the recovery script at all. The recovery script never mentions the file that global policy says must be read first.

**Why this is a choice.** Each document was written at a different time for a different reason and each is reasonable on its own terms. Deciding which one is canonical is a judgement about how you want to work, not a factual question with a right answer. The alternative, keeping all four in sync by hand, is what has been happening, and it is what produced the divergence.

**The options.** Nominate one document as canonical and have the other three point at it rather than restate it. Or accept the divergence and add a check that shouts when they disagree.

**Recommendation.** Nominate the operational tracker on the Desktop as canonical, because it is already the one that is actually current and already the one three separate directives name as the first read, and have the other three say only "the recovery procedure lives in the tracker" rather than repeating it. Restating a procedure in four places guarantees it will diverge in four places. This one has a real cost either way, because it means the project level configuration file stops being self contained.


### Ruling three. Where the tracker should live.

**The situation.** The operational tracker is the single file that is currently keeping the whole recovery path honest. Everything else was stale, silent, or wrong. Its canonical copy lives on the Desktop, outside the repository, with a mirror inside the repository that is refreshed by hand.

**Why this matters more than it sounds.** An unversioned file on one machine's Desktop is now the single point of failure for recovering this project. If it is lost or corrupted, there is no history to restore it from, and the mirror is only as current as the last time somebody remembered to copy it.

**The options.** Invert it, so the repository copy is canonical and the Desktop copy is the convenience mirror. Or keep the Desktop copy canonical and add an automatic check at save time that refuses to proceed while the two differ.

**Recommendation.** Invert it. The reason the Desktop copy became canonical is that it is easier to open, and that reason has been outweighed. A version controlled tracker gives you the full history of every resume pointer, which is genuinely useful when reconstructing what was believed when. A check has been added at save time regardless, so you get the warning either way. This is a weak preference, not a strong one, and if you find the Desktop copy materially easier to work with, keeping it canonical plus the new check is defensible.


## The Nine Small Ones


### Ruling four. Should saving state refuse to proceed when memory files have not been updated.

The save command now writes a session summary to Open Brain automatically, so that half of the problem is closed. The other half is the memory files, which are updated by me remembering to update them, with no check. Twice this week that was missed.

**The choice is whether the save command should print a loud warning and continue, or refuse to save until either the memory files have been touched or an override flag is passed.**

**Recommendation.** Refuse, with an override flag. A warning that scrolls past in a long output is not a check, and the whole theme of today's findings is mechanisms that report a problem in a way nobody reads. The override keeps you unblocked when the omission is deliberate.


### Ruling five. The retired message service.

It is named as a recovery step in eight places. It does not fail when run. It succeeds, returning fifty three well formed entries about an unrelated project whose newest is dated the fourth of April, with nothing marking them as retired or stale.

**The choice is to delete the eight instructions, or to keep them behind an explicit retired banner.**

**Recommendation.** Delete seven, banner one. Delete the instructions, because an instruction to consult a retired service is pure cost. Keep a single line somewhere in the recovery documents saying that the service existed, was retired when it became clear the models could be reached directly through the command line, and should not be consulted, so that a future reader who finds references to it in old notes knows what they are looking at.


### Ruling six. Fourteen documents that exist only on the Desktop.

Fourteen substantive documents exist as plain text on the Desktop with no version in the repository. Four of them are cited by name in a document that opens by promising the reader can rebuild everything from the repository alone. Two of the four carry the design of a fix that has not yet been implemented.

**The choice is to convert all fourteen into repository markdown, or only the four that are cited, or to stop citing them.**

**Recommendation.** Convert the four cited ones now, the rest at leisure, and add a check that a cited note name resolves to a file inside the repository. Stopping the citations is the wrong direction, because the material is genuinely worth citing.


### Ruling seven. The memory index size.

The index is at ninety seven percent of a twenty five thousand character loading limit. A note from the second of July claimed it truncates every session. That claim was measured and is wrong: nothing is being lost today. But the headroom is roughly eight more sessions at the current rate of writing.

The overrun comes from ten session entries carrying full paragraph summaries in a file whose own specification says one line per entry. The content is duplicated inside the files they point at, so trimming them loses nothing.

**The choice is to trim the six longest entries now, reclaiming about four thousand characters, or to wait until it actually starts truncating.**

**Recommendation.** Trim now, and add a size check to the save command. Waiting means discovering the problem by losing something, and what would be lost first is the newest entries, which are the ones most likely to matter.


### Ruling eight. Which section of the onboarding document owns the state block.

The onboarding script has a mode that has done nothing since the day it was written, one hundred and eighteen days ago, and its own self test reports success. The cause is that the reader looks for markers in one section of the document while the writer puts them in a different section. Fixing it requires deciding which section is right, and I do not know which you intended.

**The choice is to make the reader search the whole document for the markers wherever they are, or to move the writer's output into the section the reader expects.**

**Recommendation.** Make the reader search the whole document. It is more robust, it survives future reorganisation of the onboarding document, and it does not move content that people may have got used to finding in a particular place.


### Ruling nine. Two definitions of the letter f.

Your configuration file defines f as Find, Follow, Fix, a three step cycle. Persistent memory records a correction saying it is Find, Follow, Analyse, Fix, P-pass, a five step cycle, and that memory has carried a note flagging the contradiction since the eleventh of April without it being resolved.

The two are not equivalent. The five step version includes gathering evidence with tools before fixing, and falsifying the fix afterwards. A session following the configuration file skips both.

**Recommendation.** The five step version, and update the configuration file to match. That is what the correction says you wanted, and the two skipped steps are exactly the ones the rest of the project's method insists on.


### Ruling ten. Two definitions of strictly sequential working.

The tracker lists strictly sequential tool use as non negotiable on every turn. Your configuration file describes it as a mode you invoke and release. Since the tracker is the mandated first read after a memory wipe, a fresh agent currently adopts one tool call at a time permanently, and applies it to every agent it dispatches, which materially slows everything.

**Recommendation.** Your configuration file's reading, that it is invoked rather than standing, and correct the tracker. If you did intend it as standing for this project, say so and I will make the configuration file agree instead.


### Ruling eleven. Test coverage for the operational scripts.

None of the five operational scripts has any test coverage. That is why one script crashed on every run for one hundred and five days and another did nothing for one hundred and eighteen without anyone noticing. Individual tests have been added alongside today's repairs, but there is no systematic coverage.

Every defect found today is detectable by a test of under ten lines. The work is about half a day.

**Recommendation.** Do it, but scheduled against a concrete trigger rather than someday. The natural trigger is before the control experiment restarts, because that is the next time the recovery path carries real weight. This is your call because it is half a day that is not experimental progress.


### Ruling twelve. A background service that has done nothing for five months.

A service starts every sixty seconds, logs a healthy line, is faithfully restarted by the operating system, and reads a file path that is the placeholder inside a shipped example template. It has ingested nothing since March. Its purpose was to let a design agent drop files into a folder and have them absorbed into the memory store, from an environment that could not reach the database directly.

The code side has been repaired so it points at the real registry and refuses to start silently on a bad path. Whether to actually restart the service is yours, because it runs on your machine and because the agent it existed to serve may no longer be in use.

**Two things found while repairing it that change the shape of this decision.** First, the registry the service reads names an outbox folder that does not exist. The path it holds ends in ob outbox directly under the project folder; the real one is inside the cw handoff folder. So even after the code repair, restarting the service as things stand would make it fail loudly and immediately, and the operating system would restart it every ten seconds forever. That is honest rather than silent, which is an improvement, but it is not a state to leave running while you sleep.

Second, and more seriously, the service writes through whichever copy of the memory code it finds next to the project it is serving. The project it serves happens to contain the old copy. So the moment it actually ingested anything, it would re-open the exact hole that was closed today by unpinning the search path, because it would route the write through the fork that writes no project label, no content hash and no signature. It has been left with a loud startup error naming this, and the behaviour deliberately unchanged, because changing it is a design decision about how that service resolves its code.

**Recommendation.** Retire it, which resolves all three problems at once. If the design agent is no longer working this way, a service that runs forever to serve nobody is the definition of what you said you did not want. If you do want it back, the order matters: correct the registry path first, then fix how it resolves its code, then reload. Reloading first gives you a restart loop.


### Ruling thirteen. Seven records that cannot be verified.

The memory store's verification command now correctly refuses to pass. It reports eight valid records, ninety nine that predate the introduction of hashing and are legitimately unverifiable, and seven that were written AFTER hashing was introduced and still have no hash. Those seven span the eighth of June to today, and they are the ones that matter, because they were written by a path that should have hashed them and did not. Until this morning all one hundred and six were being reported together as legacy, and the command exited successfully.

**The choice is what to do about the seven.** They can be re-hashed now, which makes the verification pass again but is a slightly odd thing to do: hashing a record after the fact records that it has not changed since you hashed it, not that it has not changed since it was written. Or they can be left, accepted as a known gap with the command staying red until the store is next rebuilt.

**Why this needs you rather than me.** Anything that touches the tamper evidence layer touches the property this project publishes as central to its method, and quietly making a red light green is precisely the move the whole exercise was about not making.

**Recommendation.** Leave them, and record the gap explicitly. A verification command that says "seven records from this window cannot be verified, here they are" is more honest and more useful than one that says OK because someone back filled the hashes. Accept the red light as accurate. Anything written from now on hashes correctly, so the gap is bounded and will not grow.

**Be aware of one consequence either way: the verification command now exits with a failure code, so any habit or script that treated a successful exit as a green light will now report failure.** That is intended.


## A closing note

None of this touches the experiment results, the convergence machinery, the mathematics, or anything published. All of it is about the ability to pick the work back up cleanly. That distinction is worth holding onto: the instruments that measure the project were faulty, the project was not.


---

Companion to the Desktop TTS file of the same name and date.

Written under CDSFL note standard v1.2 (14 May 2026).
