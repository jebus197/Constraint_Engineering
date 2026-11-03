# An 11 MB PNG Was Being Read As 780 Of His Rulings

3 November 2026, 15:45 GMT

## What this is

This answers the questions raised at 15:06, 15:34 and 15:45 on the 3rd of November, at the end of a session that ran for close to 24 hours with little supervision. It also reports a defect found while answering them that was larger than any of the questions: the reader that recovers the founder's written responses was treating an image file as 780 rulings he never wrote.

## The defect, and why it mattered more than it looks

The founder's responses folder holds a file named `Google Search Discussion on severity- 2026-09-28_10-28.md`. It is 11,076,291 bytes and it is not markdown. Its first 8 bytes are `89504e470d0a1a0a`, which is the PNG image signature, followed by the `IHDR` and `IDAT` chunk markers. It is a screenshot.

The reader accepted it on its extension. An allow list of 3 extensions, `.txt`, `.rtf` and `.md`, was added on the 20th of October for exactly this class of problem, after a zip archive returned 65 lines of compressed binary as annotations. The reader's own comment at that point reads "AN EXCLUSION LIST CANNOT HOLD" and "The ALLOW list is decidable." Both statements are true, and the allow list was still defeated, because an extension is a claim a file makes about itself rather than a fact about its contents.

The decoder then made the problem invisible. The codec in use is Mac OS Roman, chosen deliberately because it maps every one of 256 byte values and so never drops a character of the founder's writing. Applied to a PNG it produces 249,610 lines of noise without raising a single error, and 780 of those lines happen to begin with a hash character, which is the founder's annotation marker. So the reader returned 780 annotations attributed to him. That is 0.481779 of the entire 1,619-annotation corpus the reader reported.

3 guards went red on it, demanding verdict records for rulings that do not exist. And the same file made the reader 100 times slower, which is how the defect stayed hidden.

## Why no commit could land

The reader fetches the report lines each annotation attaches to, so the founder's comment can be read beside the report line it comments on. That function re-read and re-split the whole file once per annotation. With 780 annotations in an 11 MB file, the 11 MB file was decoded 780 times and split into lines 780 times.

Measured on 2 independent routes that agree to within 0.5 percent: the library call alone costs 3.576 seconds, while the command-line path costs 684.25 seconds, and a strided sample of 63 of the 1,619 annotations costs 420.63 milliseconds each, which projects the loop at 680.995 seconds. The sample has to be strided rather than taken from the head of the list, because the first 40 annotations sit in small files and cost 18.68 milliseconds each, which projects 30.241 seconds and is 22.5 times too low.

2 guards shell out to that command. The test timeout is 300 seconds. Both died, the pre-commit gate refused, and nothing could be committed. The timeout was also masking the 780 phantom annotations: at the previous commit the tests could not run far enough to reach the assertion that would have reported them. Confirmed by running those tests against the previous commit in a separate checkout, where they time out rather than fail.

## The repair, in 3 parts

The decode is now performed once per file per version, keyed on the file's path, its modification time in nanoseconds and its size, so a file edited while a process runs is decoded again rather than served from a stale copy. The lines are cached on the same key and returned as an immutable tuple, because a cache that hands out a mutable list hands every later caller the first caller's edits. Caching the decode alone was not enough: splitting the 11 MB file into lines costs 56.48 milliseconds and ran 780 times, which is 44.05 seconds, or 94 percent of what remained after the decode was cached.

The third part decides what a file is by reading its bytes. A file is treated as binary if it contains a null byte in its first 4,096 bytes, or if it opens with a known image or archive signature. Both tests are needed and that is measured rather than asserted: across the 348 files in the founder's folder, a null byte catches 39 and a signature catches 28, with 26 caught by both, and 2 caught by the signature alone. Those 2 are PDF files, which carry no early null byte. A PDF saved with a markdown extension is the same accident that produced the PNG, so neither test is redundant, which is the condition the project's composability standard sets.

The exclusion is reported by name, size and signature rather than applied silently, because a silent skip is the defect this reader exists to prevent.

## What the repair does not do

It cannot drop a ruling of the founder's. Every discriminator on the shape of prose tried on this folder was measured and refuted on the 17th of October, and those attempts lost real verdicts including the words "Verdict: y". Those tests all guessed whether a passage of prose was his. This one asks whether the file is text at all, which has a hard answer: 0 of his legitimate text and markdown files carry a null byte. The only 3 files that do are this PNG and 2 Word lock files that a prefix rule already excluded.

Proven by an A and B comparison inside a single process. With the binary test disabled the reader returns 1,619 annotations; with it enabled, 839. Exactly 780 are removed, all 780 from the PNG, 0 from any other file, 0 annotations are added, and all 131 of his markers survive unchanged.

The reader now completes in 6.80 seconds where it took 684.25, a factor of 100, with byte-identical output on the annotations that remain.

## A pinned figure was counting a heading written by this session

1 guard pins the annotation count over a closed window ending the 13th of October at 528. With the PNG excluded it returns 527.

The cause is established and it is not the repair above. A rule added on the 2nd of November, that 2 or more hash characters is always a heading and never the founder's marker, removed exactly 1 line from that window. The line is `FINAL_REPORT_FOR_OPUS_2026-08-27.md` line 55, and it reads "## Note 6 - Scope, diversity, and an optional validation front". 2 hashes, and a section heading of a report this session wrote. It was never his writing, so 528 was 1 too high from the moment that rule landed.

Proven by an A and B comparison on that rule alone: with the shortcut disabled the window returns 528, with it enabled 527, and the single differing annotation is that heading. The pin is now 527, with the evidence recorded beside it, and it is reversible in 1 line if the founder judges otherwise. The guard's purpose, which is to catch one of his annotations being joined to or split from its neighbour, is untouched, and the direction of the correction removes a line from his record rather than admitting one.

## 41 rulings of his are being discarded, and his own marker is the cause

This is the most consequential finding in this note and it is separate from the PNG.

A line beginning with a single hash is the founder's annotation unless it looks like a heading. Where a generated original survives on the Desktop, his lines are known by set difference and need no guess. Everywhere else the only mechanism is a shape test: a line of 120 characters or fewer that does not end in a full stop, question mark or exclamation mark is called a heading and discarded.

Scored against the 583 annotations where ground truth exists, that shape test discards 41 of them. The proportion is 0.070326, Wilson 95 percent interval 0.052261 to 0.094016, Clopper-Pearson 0.050936 to 0.094198. And 299 of the 348 files, a share of 0.859195, have no surviving original at all, so on those the same test runs with nothing able to check it.

36 of the 41 end in one of the founder's own markers. A trailing marker displaces the sentence punctuation the shape test requires, so the marker he introduced in order to make his instructions traceable is precisely what makes them invisible. A markdown heading never ends in a ticket marker, so the marker is a structural signal the shape test is throwing away.

The discarded lines include these, verbatim:

- "# Permission is granted. stm"
- "# I accept your recommendation. Please implement it. fr"
- "# Agreed. You should rerun it under full cy protocol. stm"
- "# Build and implement option 1. fr"
- "# Retire them. stm"
- "# I chose option 1. fr"
- "# Verdict. Do it and study it in the upcoming simulated run. fr"
- "# Then do the measurement first. pf"
- "# I remember this. Yes do it as instructed. stm"
- "# This are runway items and I will authorise dispatch once all the work here has been completed. disc"
- "# This is a topic we have already fully addressed, together with an agreed fix. Did you ever implement it? qs"
- "# I did just give you (what I thought was) the answer to this? In the last morning report I said: #"

The phrase "I accept your recommendation" appears 7 times among the 41. The full list of 41, with file and marker, is reproduced in the spoken counterpart of this note.

## His asterisk proposal, tested

The founder asked whether wrapping each paragraph written by this session in asterisks, with his own comments opening with a hash and needing no closing mark, would make his comments machine-readable, and asked what it would buy.

Measured against the same ground truth, it buys all 41. Under that format a line is identifiable as written by this session because the asterisks travel inside the file, so the shape test is not needed at all. His comments read correctly go from 542 of 583 to 583 of 583, with 0 discarded, Wilson interval 0 to 0.006546.

A second and cheaper repair also exists: trust his marker. A line whose body ends in one of the 8 markers is his, with no shape test applied. That recovers 36 of the 41, a proportion of 0.878049, Wilson 0.744558 to 0.946767. Its false-positive rate cannot be read from his folder, because in the files with ground truth every hash line is his, 583 of 583, so that count has no denominator, and a 0 computed from an empty denominator is not a 0. The control comes from the other direction: across 1,151 single-hash headings written by this session in the repository's own notes, 0 end in one of his markers, Wilson 0 to 0.003326.

The 2 fixes compose, in the strong sense the project's standard requires, because neither dominates on both properties. The format change cannot reach a file already written, so it recovers 0 of the 41 already on disk. The marker rule cannot reach the 5 comments he left unmarked, which include "Verdict option 1" and "Same answer as before". Together they recover 36 already on disk and read 583 of 583 in future files. Neither is redundant.

2 limits are stated rather than discovered later. The format change governs only files written after it is adopted and repairs no existing file. And whether the Firefox Read Aloud extension speaks a lone asterisk aloud cannot be tested here, because it needs the extension and the founder's own ears; if it does read them, the proposal costs him the comfort the format exists to protect. A single sample file in the proposed format has been placed in his spoken-output folder so he can test that directly.

## The ticket store, after 24 hours

The store holds 3,384 tickets. By kind: 2,752 proposed fixes, 136 feature requests, 127 questions, 111 discussions under the live spelling, 93 under each of the 2 legacy spellings, 63 written records and 9 statements. By status, 2,214 are closed and 456 merged, against 85 still open, a share of 0.025118 with a Wilson interval of 0.020360 to 0.030953. 2,662 of 3,384 carry an anchor naming the file and position of the annotation they come from, a share of 0.786643.

So it holds and it settles. Whether it prevented anything is the question actually asked, and the answer is that no surface records it. Work avoided because a ticket already existed is not logged anywhere, so the saving is not measured. 5 tickets of 3,384 are marked as duplicates, 0.001478, and the store records the link without recording the order, so even those do not show whether the duplicate was caught before the work was redone or after. The 2 re-derivations found earlier in this session were caught by reading the register by hand, not by the store refusing them. That is a gap in the instrument rather than a result about it.

Its value to outside researchers and autonomous agents is not measured and is not measurable yet, because none has read it. Stating otherwise would be the flattering-measure failure this project has already recorded 3 times.

## The identifiers were not reaching him, and he is right that they were not

Of 11 spoken files delivered to the founder on the 3rd of November, 2 carry any ticket identity at all, a proportion of 0.181818 with a Wilson interval of 0.051368 to 0.476981, and each of those 2 carries exactly 1. The markdown counterparts in the repository do better at 11 of 31, or 0.354839.

The cause is the spoken-output rule itself. A 12-character hexadecimal identity read aloud is a string of unrelated letters and digits, so it was being stripped from the files he actually reads. The store therefore holds 3,384 identified tickets while the surface he reads carries almost none of them. His observation that he saw the identifiers only briefly after they were agreed is accurate.

The recommended resolution keeps both properties rather than sacrificing either. The markdown counterpart carries the full identity, because that is the surface a researcher or an agent reads and the surface where duplicate detection matters. The spoken file carries the short task code, of the form B94 or C30, which reads aloud as 2 characters and a number and which he already uses when writing back. This needs his ruling, because it changes what the files he reads contain.

## The statement marker exists and is reached

The founder asked how the statement marker is working out and whether it was recorded in the project's instruction files and guards. It was. It was built on the 1st of November as the 5th member of the kind vocabulary, it is read out of his annotations by the harvester's marker patterns, 9 tickets are filed under it, and 7 guards name it.

A correction to that figure of 7 belongs here. A first version of the measuring script tested for the 3 letters as a substring and reported 36 guards, because words such as "postmortem" and "adjustment" contain them. The word-boundary figure is 7. The same shape of predicate error has now been recorded 9 times in this project, 5 of those reading a match as presence.

## Where his responses actually live

Of the 839 annotations the reader now returns, 583 are in plain-text files, a share of 0.694875, and 256 are in rich-text files, a share of 0.305125 with a Wilson interval of 0.274914 to 0.337112.

So his remark that the plain-text files are the ones to look in is read as guidance for searching rather than as an instruction to narrow the reader, because narrowing the allow list to plain text alone would drop 256 of his annotations, close to a third of the record. That reading is flagged for his confirmation rather than acted on.

His second signal was tested and holds with the hedge he himself supplied. Of the 48 plain-text files the reader accepts, 36 carry a note-standard line within their last 6 non-blank lines, a proportion of 0.750000 with a Wilson interval of 0.612156 to 0.850794. His words were "usually, although not always exclusively", and 0.750000 is exactly that: a strong signal and not a sufficient one.

## Producers

Every figure above is produced by a committed script, because a number that exists only as prose is a claim about evidence rather than evidence.

- `scripts/would_asterisks_make_his_comments_machine_readable_2026-11-03.py` for the 41 discarded comments, the asterisk comparison, the marker rule, the false-positive control and the composability measurement.
- `scripts/has_the_ticket_store_earned_its_place_2026-11-03.py` for the store's composition, its settlement rates, the identifier reach and the statement-marker checks.
- `scripts/why_the_responses_reader_crossed_its_budget_2026-11-03.py` for the timing diagnosis.
- `bench/tests/test_a_png_named_md_is_not_his_writing_2026-11-03.py` for the repair, with 15 tests. 5 of 5 reverting mutations were confirmed red, including 3 successive attempts at a wall-clock guard, meaning a guard that fails if the code gets slower, that were blind: the first went vacuous once the PNG was excluded, the second compared 2 helpers rather than the code path that chooses between them, and the third used a bound of 10 milliseconds that sat above both routes. The bound is now calibrated by measurement at 0.80 milliseconds, between a cached cost of 0.0310 and an uncached cost of 4.8563 on the same file.

## One error of this session's own, recorded

While comparing lint output against the previous commit, a command chain of the form "echo and ruff and git stash" broke at the ruff step, because ruff exits with a failure code when it reports findings. The trailing "git stash pop" then ran unguarded and restored a stash that already existed on the stack and had nothing to do with this session, leaving `hooks/ffafp_audit.py` in a conflicted state with conflict markers in it.

It was detected immediately, because the output contained a stash message the chain could not have produced. The file was restored to the committed version, the pre-existing stash is intact and untouched on the stack, and no other file was affected. The lesson is narrow and mechanical: comparing a working file against a committed one is done with a direct read of the committed version, never by moving the working tree out of the way.

Written under CDSFL note standard v1.9 (1 November 2026).
