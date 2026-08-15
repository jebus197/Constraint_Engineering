# The recovery instruments were checked, and most of them have been quietly lying

**2026-08-05 15:24 BST**

## What was asked and what was done

The question was simple. Open Brain, the persistent memory store, had clearly stopped
recording anything. So: fix it, and while we are here, are the other recovery resources
actually working, or are they decoration?

Recovery resources are the files and scripts that let an assisting agent rebuild its
understanding of the project after its working memory is wiped. They are not documentation
in the ordinary sense. They are instruments. When they are right, work continues. When
they are wrong, work restarts from a false picture.

Fifteen agents audited them: seven auditors, each given one family of resources and told
to test by running things rather than by reading them; seven adversarial checkers, each
told to refute the first agent's findings rather than agree with them, and to reject
anything they could not reproduce themselves; and one to consolidate. Seventy-one findings
came back. **Sixty were confirmed on independent reproduction, eight were judged less
serious than first claimed, three were judged worse, and none were refuted.** The checkers
also found twenty-five further faults the auditors had missed.

Nothing was changed. This was read-only.

## The short version

The recovery path works today, but not for the reason it appears to. It works because one
file happens to be current: the operational tracker on the Desktop. Every automated part
of the path is stale, silent, or actively wrong, and each one fails in the specific way
this project has learned to fear most — by producing a confident, well-formed, plausible
answer that is false.

That single working file is also the only one not under version control.

## Open Brain: not broken, and not what anyone thought

The database is healthy. PostgreSQL has been running since 10 June, semantic search works,
the embeddings are real, and a test write went in and came back out correctly. The store
itself is fine.

Three things are wrong above it.

**Nothing feeds it.** The save-state command is defined in two places. The global
definition says a save includes an Open Brain session summary and names it first. The
project-level definition, which takes precedence, does not mention Open Brain at all, and
the script that actually runs contains no Open Brain code of any kind. Every entry that
exists was written because an operator remembered to type the command by hand. The last
one is dated 2 August because that is the last time anyone remembered.

**There are two installations and the wrong one is in use.** The suspicion this morning was
that the copy at `Developer_Projects/OpenBrain/` might be a decoy pointing at a dead end.
The truth is the reverse. That copy is the real project: newer code, project scoping,
cryptographic signing, hash chaining, 440 tests. The copy inside `Project_Genesis/` is a
fork frozen in early March. A configuration file pins the Python search path to the fork,
so every write for two months has gone through the older code. The consequence: tamper
evidence — the property this project publishes as central to its method — is present on 8
rows out of 114 and has been silently absent since 8 June. Every memory written since then
is unverifiable, and nothing anywhere says so.

**The tool meant to detect that reports success.** It prints `Chain integrity: OK` and
exits 0. It labels rows written minutes ago as predating the migration, because that label
is hardcoded and was written when the assumption behind it was still true. A store that is
93% unverifiable reports itself clean.

A fourth item is almost comic. A background service has polled a file path every sixty
seconds for five months. The path is the placeholder inside a shipped example template,
whose own comment tells you to copy it elsewhere before use. The service starts, logs a
healthy line, is faithfully restarted by the operating system, and has ingested nothing
since March.

And there is a trap in the fix. The documented cure for the store mixing several projects
together is a filter that selects only this project's records. Running it now returns a
session summary from 3 June presented as current state, because the project label has been
stripped from every write since the fork took over. Unfiltered, the store gives a cluttered
but honest answer. Filtered, it gives a clean, confident, entirely wrong one. **The filter
must not be recommended to anyone until the existing records are relabelled.**

## The four faults that produce most of the damage

Several findings turned out to be one underlying fault seen from different angles. Four
root causes account for most of what a recovering agent is told.

1. **The save script writes its state snapshot before it makes the commit.** So the snapshot
   can never describe the commit that contains it: it names the previous commit and lists
   as uncommitted precisely the files the commit is about to include. Eight consecutive
   commits were checked; all eight do this. The recovery script then prints that snapshot
   as its first section, above a live check that contradicts it, in the same run.

2. **The function that finds the most recent experiment looks only at the highest-numbered
   experiment and never falls back.** The zero-plant control was deliberately halted before
   writing a report, and it carries the highest number. So the recovery script announces
   that no experiment logs exist, in a repository holding ~60 experiment directories and 37
   reports. This has also been silently disabling part of the save process since 2 August.

3. **The remote comparison is hardcoded against `main`** while all work happens on another
   branch. It announces a diverged remote — 98 ahead, 1 behind — for a branch exactly in
   step with its real upstream. False alarm in one direction; in the other, if the check
   fails entirely it reports "up to date", a false all-clear.

4. **The recovery script looks for two text markers that were deleted from the file in
   April.** For 113 days the section a recovering agent most needs — what to do next — has
   printed "no pending work section found" while ~1,600 lines of live pending work sat in
   the very file the script had just opened. The function returns the same empty string
   whether the file is missing or the marker is missing, so the two failures are
   indistinguishable.

## The instruments that were supposed to catch this

**The quality-control command has crashed on every invocation since 22 April** — 105 days
without an automated staleness sweep. It fails loudly, which is the merciful part, but the
repository has had no automatic checking during the entire period in which these faults
accumulated. It would have caught several of them.

**The onboarding script's `--full` mode has been a no-op since the day it was written**, 118
days ago, and its own built-in self-test reports success. It reads one section of a
document looking for markers the writer puts in a different section.

**The log-sealing verifier can never report tampering.** It calls a function returning a pair
— a yes/no and an explanatory message — then tests the pair for truth. In Python a non-empty
pair is always true, so the answer is discarded before it is read. A modified sealed log
reports as intact. In a project whose central claim is tamper-evident provenance, the
tamper detector's detection branch is dead code. Structurally the same fault as the verdict
reader that once matched "NOT FALSIFIED" as though it said "FALSIFIED".

**The credential checker fails to strip a prefix from the environment file**, so the
onboarding script reports all six interface keys as missing — three of them marked
required — while all are present. This is the same parser fault that cost real time on
8 July, occurring a second time in a different script.

None of these five scripts has any test coverage. That is why a crash lasted 105 days and a
no-op lasted 118.

## One small thing worth doing immediately

The save script has a model name written into it as a fixed string, and the string is out
of date. It has been stamping the wrong model's name onto commits — including onto this
morning's commit, whose entire subject was that attributing a result to a model that did
not produce it is indistinguishable from fabricating it. It is one line. Correct it first,
whatever else is decided.

## The documents

The main onboarding document carries today's date at the top and content that stops on
2 August. The save script updates the date unconditionally and skips the body whenever the
body contains hand-written prose — which it always does. The timestamp advances; the
content does not.

The document whose entire purpose is to be honest about what is withheld from the public
record states that the private memory index holds 65 files. It holds 101. Between 25 and 39
entries are neither published nor declared as withheld, which the document's own definition
calls an omission fault.

Fourteen substantive documents exist only as plain text on the Desktop with no version in
the repository. Four are cited by name in a document that opens by promising the reader can
rebuild everything from the repository alone.

Eight places still instruct a recovering agent to consult the retired message service. It
does not fail. It succeeds, returning 53 confidently formatted entries whose newest is
dated 4 April, about an unrelated project, with nothing marking them as retired.

The tracker contains a section headed **authoritative** that is 74 days stale and tells a
reader that experiment 42 is next. Its own recovery instructions send a reader to two
sections: one completed 105 days ago, one whose newest entry is 82 days old. And its
instruction to read the live work queue was carried in an older block and not carried
forward when the pointer was advanced, so an agent following the current pointer correctly
never learns the live queue exists.

## One standing belief was corrected

A note from 2 July recorded that the memory index is too large and that its tail truncates
on every session load. A checker measured it: the index is at 97% of the limit but is **not**
truncating and has not been. The belief was wrong. Headroom is genuinely thin — roughly
eight more sessions at the current rate — but nothing is being lost today. Recorded because
a correction is as much a result as a fault.

## A caveat on the method

No finding was refuted. That is unusual and should not simply be taken as a compliment to
the auditors. Most of these faults are of a kind where reproduction is easy and refutation
correspondingly rare: run the command, and either the false output appears or it does not.
The checkers did adjust eleven severities in both directions and did add twenty-five faults
the auditors missed, so they were not merely nodding along. But a zero-refutation rate on a
first pass is worth noting rather than celebrating.

## What this means

The honest answer to the question asked is that the recovery resources are **not** working as
intended. One file is. The rest range from silently unhelpful to actively misleading, and
the pattern across them is consistent: every failure renders as a confident success. That
is the same pattern this project has repeatedly caught inside its own experimental
machinery, and it has now been found in the instruments that report on the project itself.

There is a reading of that which is not bleak. The method works. It was applied to its own
operator's tooling and it found what was wrong. The faults are almost all small and
mechanical, most under twenty lines, and none touches the experimental results, the
convergence machinery, or anything published. What they touch is the ability to pick the
work back up cleanly — which matters enormously when the sessions are long and the funding
is finite.

Full technical record with every command and every output:
`experimental_notes/Recovery_Resource_Audit_2026-08-05.md`. Raw agent returns:
`experimental_notes/adversarial_records/recovery_resource_audit_raw_2026-08-05.json`.

Written under CDSFL note standard v1.2 (14 May 2026).
